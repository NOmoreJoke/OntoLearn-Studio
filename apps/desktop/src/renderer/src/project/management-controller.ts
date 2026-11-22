import {
  safeError,
  type MainlineManagementAction,
  type MainlineManagementCatalogDTO,
  type MainlineManagementCatalogState,
  type MainlineManagementItemDTO,
  type MainlineManagementPreviewDTO,
  type MainlineManagementResultDTO,
  type ProjectManagementBridge,
  type PendingProjectManagementOperationDTO,
  type SafeError,
} from '@ontolearn/contracts'

type PendingManagement = {
  operationId: string
  confirmationRef?: string
  documentHash?: string
  projectId: string
  kind: MainlineManagementAction['kind']
}
export type ManagementState = {
  filter: MainlineManagementCatalogState
  catalog?: MainlineManagementCatalogDTO
  selected?: MainlineManagementItemDTO
  selectedProjectId?: string
  preview?: MainlineManagementPreviewDTO
  recoveryLoaded: boolean
  recovery: PendingProjectManagementOperationDTO[]
  pending?: PendingManagement
  receipt?: MainlineManagementResultDTO
  busy: boolean
  error?: SafeError
  notice: string
}

/** Presentation state only. The named host services own all permissions and writes.
 * Once apply is entered, only the original operation is queried; a failed or lost
 * reply never turns into a second copy or a replayed deletion.
 */
export class ProjectManagementController {
  #state: ManagementState = {
    filter: 'active',
    busy: false,
    notice: '',
    recovery: [],
    recoveryLoaded: false,
  }
  #listeners = new Set<() => void>()
  #selection = 0
  #catalogRequest = 0
  #readRequest = 0
  #operation = 0
  #closed = false
  constructor(
    readonly bridge: ProjectManagementBridge,
    private applied: (result: MainlineManagementResultDTO) => void = () => {},
    private readonly makeId: () => string = () => crypto.randomUUID(),
  ) {}
  setAppliedHandler(handler: (result: MainlineManagementResultDTO) => void): void {
    this.applied = handler
  }
  getSnapshot = () => this.#state
  subscribe = (listener: () => void) => {
    this.#listeners.add(listener)
    return () => {
      this.#listeners.delete(listener)
    }
  }
  #set(patch: Partial<ManagementState>): void {
    if (this.#closed) return
    this.#state = { ...this.#state, ...patch }
    for (const listener of this.#listeners) listener()
  }
  get unresolved(): boolean {
    return (
      this.#state.busy ||
      !!this.#state.pending ||
      this.#state.recovery.length > 0 ||
      !this.#state.recoveryLoaded
    )
  }
  async initialize(): Promise<void> {
    if (this.#closed || this.#state.busy) return
    this.#set({ busy: true })
    try {
      const result = await this.bridge.getPendingProjectManagementOperations()
      if (result.ok) this.#set({ recovery: result.data, recoveryLoaded: true })
      else
        this.#set({
          error: result.error,
          notice: '未能核对原管理操作，请关闭并重新打开应用后核对。',
        })
      await this.#refreshCatalog(this.#state.filter, null)
    } catch {
      this.#set({ error: safeError(undefined) })
    } finally {
      this.#set({ busy: false })
    }
  }
  select(projectId: string | undefined): void {
    if (this.#state.selectedProjectId === projectId) return
    this.#selection++
    this.#readRequest++
    this.#set({ selectedProjectId: projectId, selected: undefined, preview: undefined })
  }
  async readSelected(): Promise<void> {
    // A selection read waits for the complete current management action, including
    // its catalog/state tail. No ready interval may expose half-refreshed state.
    while (!this.#closed && this.#state.busy) {
      await new Promise<void>((resolve) => {
        const release = this.subscribe(() => {
          if (!this.#state.busy || this.#closed) {
            release()
            resolve()
          }
        })
      })
    }
    if (this.#closed || !this.#state.selectedProjectId) return
    this.#set({ busy: true })
    try {
      await this.#readSelected()
    } finally {
      this.#set({ busy: false })
    }
  }
  async #readSelected(): Promise<void> {
    const projectId = this.#state.selectedProjectId
    if (this.#closed || !projectId) return
    const selection = this.#selection,
      read = ++this.#readRequest
    try {
      const result = await this.bridge.getProjectManagementState()
      if (this.#closed || selection !== this.#selection || read !== this.#readRequest) return
      if (!result.ok) this.#set({ error: result.error })
      else if (result.data.projectId !== projectId) this.#set({ error: safeError(undefined) })
      else this.#set({ selected: result.data })
    } catch {
      if (selection === this.#selection && read === this.#readRequest)
        this.#set({ error: safeError(undefined) })
    }
  }
  async refresh(
    filter: MainlineManagementCatalogState = this.#state.filter,
    cursor: string | null = null,
  ): Promise<void> {
    if (this.#closed || this.#state.busy) return
    this.#set({ busy: true, error: undefined })
    try {
      await this.#refreshCatalog(filter, cursor)
    } finally {
      this.#set({ busy: false })
    }
  }
  async #refreshCatalog(
    filter: MainlineManagementCatalogState,
    cursor: string | null,
  ): Promise<void> {
    const request = ++this.#catalogRequest
    this.#set({ filter, error: undefined })
    try {
      const result = await this.bridge.getProjectManagementCatalog({
        state: filter,
        pageSize: 50,
        cursor,
      })
      if (request !== this.#catalogRequest || this.#closed) return
      if (result.ok) this.#set({ catalog: result.data })
      else this.#set({ error: result.error })
    } catch {
      if (request === this.#catalogRequest) this.#set({ error: safeError(undefined) })
    }
  }
  async preview(
    action: MainlineManagementAction,
    restore?: MainlineManagementItemDTO,
  ): Promise<void> {
    if (this.#closed || this.unresolved) return
    if ((action.kind === 'restore-trash') !== !!restore) return
    const selection = this.#selection,
      operation = ++this.#operation,
      projectId = restore?.projectId ?? this.#state.selectedProjectId
    if (!projectId) return
    this.#set({ busy: true, preview: undefined, receipt: undefined, error: undefined, notice: '' })
    const current = () =>
      !this.#closed && selection === this.#selection && operation === this.#operation
    try {
      // Read the actual current CP and lifecycle, rather than guessing a version
      // from a previous catalog page or silently substituting lifecycle version 0.
      const read = restore
        ? { ok: true as const, data: restore }
        : await this.bridge.getProjectManagementState()
      if (!current()) return
      if (!read.ok) {
        this.#set({ error: read.error })
        return
      }
      if (read.data.projectId !== projectId) throw new Error('IDENTITY_CONFLICT')
      if (!restore) this.#set({ selected: read.data })
      const result = await this.bridge.previewProjectManagement({
        action,
        expectedCheckpointRef: read.data.checkpointRef,
        expectedLifecycleVersion: read.data.lifecycle.version,
        ...(restore ? { restoreProjectId: projectId } : {}),
      })
      if (!current()) return
      if (!result.ok) this.#set({ error: result.error })
      else if (
        result.data.projectId !== projectId ||
        JSON.stringify(Object.entries(result.data.action).sort()) !==
          JSON.stringify(Object.entries(action).sort()) ||
        result.data.document.checkpointRef !== read.data.checkpointRef ||
        result.data.document.lifecycleVersion !== read.data.lifecycle.version
      )
        throw new Error('IDENTITY_CONFLICT')
      else this.#set({ preview: result.data, notice: '请核对完整影响，再明确确认。' })
    } catch {
      if (current()) this.#set({ error: safeError(undefined) })
    } finally {
      if (operation === this.#operation) this.#set({ busy: false })
    }
  }
  cancelPreview(): void {
    if (this.#state.busy || this.#state.pending) return
    this.#operation++
    this.#set({ preview: undefined, notice: '已取消；未提交项目更改。', error: undefined })
  }
  #accept(pending: PendingManagement, result: MainlineManagementResultDTO): void {
    if (this.#closed) return
    if (
      result.operationId !== pending.operationId ||
      result.projectId !== pending.projectId ||
      result.kind !== pending.kind ||
      (result.kind !== 'copy-current' && result.targetProjectId !== result.projectId) ||
      (result.kind === 'copy-current' && result.targetProjectId === result.projectId)
    )
      throw new Error('IDENTITY_CONFLICT')
    this.#set({
      pending: undefined,
      recovery: this.#state.recovery.filter((item) => item.operationId !== pending.operationId),
      preview: undefined,
      receipt: result,
      notice:
        result.kind === 'copy-current'
          ? '副本已创建。当前仍是源项目；可明确打开副本。'
          : result.kind === 'trash'
            ? '项目已移至回收站；数据和历史仍保留。'
            : result.kind === 'restore-trash'
              ? '项目已恢复；不会续跑旧任务。'
              : '项目设置已保存。',
    })
    // A receipt is retained even after a view change. The shell must also check
    // the original project before retiring or refreshing its current context.
    this.applied(result)
  }
  async apply(): Promise<void> {
    const preview = this.#state.preview
    if (this.#closed || this.unresolved || !preview) return
    if (Date.now() >= preview.expiresAtMs) {
      this.#set({ preview: undefined, notice: '预览已到期，请重新预览。' })
      return
    }
    const selection = this.#selection,
      operation = ++this.#operation
    this.#set({ busy: true, error: undefined })
    try {
      const confirmation = await this.bridge.confirmProjectManagement({
        previewRef: preview.previewRef,
        documentHash: preview.documentHash,
      })
      if (this.#closed || selection !== this.#selection || operation !== this.#operation) return
      if (!confirmation.ok) {
        this.#set({ error: confirmation.error })
        return
      }
      if (
        confirmation.data.previewRef !== preview.previewRef ||
        confirmation.data.documentHash !== preview.documentHash ||
        confirmation.data.projectId !== preview.projectId ||
        confirmation.data.kind !== preview.action.kind
      )
        throw new Error('IDENTITY_CONFLICT')
      const pending: PendingManagement = {
        operationId: this.makeId(),
        confirmationRef: confirmation.data.confirmationRef,
        documentHash: preview.documentHash,
        projectId: preview.projectId,
        kind: preview.action.kind,
      }
      this.#set({ pending })
      const result = await this.bridge.applyProjectManagement({
        operationId: pending.operationId,
        confirmationRef: confirmation.data.confirmationRef,
        documentHash: preview.documentHash,
      })
      if (result.ok) {
        this.#accept(pending, result.data)
        await this.#refreshCatalog(this.#state.filter, null)
        await this.#readSelected()
      } else
        this.#set({
          error: result.error,
          notice:
            '操作结果尚未确认；保留原操作。若无法查询，请关闭并重新打开应用后核对，勿重复提交。',
        })
    } catch {
      this.#set({
        error: safeError(undefined),
        notice:
          '操作结果尚未确认；保留原操作。若无法查询，请关闭并重新打开应用后核对，勿重复提交。',
      })
    } finally {
      this.#set({ busy: false })
    }
  }
  async reconcile(operationId?: string): Promise<void> {
    const pending = operationId
      ? this.#state.recovery.find((item) => item.operationId === operationId)
      : this.#state.pending
    if (this.#closed || this.#state.busy || !pending) return
    this.#set({ busy: true, error: undefined })
    try {
      const result = await this.bridge.getProjectManagementOperation({
        operationId: pending.operationId,
      })
      if (!result.ok)
        this.#set({
          error: result.error,
          notice: '操作结果尚未确认；保留原操作，请关闭并重新打开应用后核对，勿重复提交。',
        })
      else if (result.data.state === 'applied') this.#accept(pending, result.data.result)
      else
        this.#set({
          pending: undefined,
          recovery: this.#state.recovery.filter((item) => item.operationId !== pending.operationId),
          preview: undefined,
          notice: '已核实原操作未提交。如需继续，请重新预览并确认。',
        })
      if (result.ok) {
        await this.#refreshCatalog(this.#state.filter, null)
        await this.#readSelected()
      }
    } catch {
      this.#set({ error: safeError(undefined) })
    } finally {
      this.#set({ busy: false })
    }
  }
  close(): void {
    this.#closed = true
    this.#selection++
    for (const listener of this.#listeners) listener()
    this.#listeners.clear()
  }
}
