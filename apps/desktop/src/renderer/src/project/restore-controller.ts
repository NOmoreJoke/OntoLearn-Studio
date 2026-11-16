import {
  safeError,
  type BridgeResult,
  type ProjectCheckpointListDTO,
  type ProjectRestoreConfirmationDTO,
  type ProjectRestoreOperationDTO,
  type ProjectRestorePageDTO,
  type ProjectRestorePreviewDTO,
  type ProjectRestoreResultDTO,
  type ProjectCheckpointBridge,
  type ProjectManagementBridge,
  type RestoreImpactDocument,
  type SafeError,
} from '@ontolearn/contracts'

export type RestoreControllerState = {
  list?: ProjectCheckpointListDTO
  selectedProjectId?: string
  preview?: ProjectRestorePreviewDTO
  pages: ProjectRestorePageDTO[]
  readSegmentHashes: string[]
  document?: RestoreImpactDocument
  confirmation?: ProjectRestoreConfirmationDTO
  recoveryLoaded: boolean
  recovery: Array<{ operationId: string; projectId: string }>
  busy: boolean
  error?: SafeError
  notice: string
}

/** Presentation state only. The named host services own every permission; a
 * lost reply keeps the original operation for reconciliation, never a replay. */
export class ProjectRestoreController {
  #state: RestoreControllerState = {
    pages: [],
    readSegmentHashes: [],
    recovery: [],
    recoveryLoaded: false,
    busy: false,
    notice: '',
  }
  #listeners = new Set<() => void>()
  #selection = 0
  #request = 0
  #closed = false
  constructor(
    private readonly bridge: ProjectCheckpointBridge &
      Pick<ProjectManagementBridge, 'getProjectManagementState'>,
    applied: (result: ProjectRestoreResultDTO) => void = () => {},
    private readonly makeId: () => string = () => crypto.randomUUID(),
  ) {
    this.applied = applied
  }
  private applied: (result: ProjectRestoreResultDTO) => void
  setAppliedHandler(handler: (result: ProjectRestoreResultDTO) => void): void {
    this.applied = handler
  }
  getSnapshot = () => this.#state
  subscribe = (listener: () => void) => {
    this.#listeners.add(listener)
    return () => {
      this.#listeners.delete(listener)
    }
  }
  #set(patch: Partial<RestoreControllerState>): void {
    if (this.#closed) return
    this.#state = { ...this.#state, ...patch }
    for (const listener of this.#listeners) listener()
  }
  get unresolved(): boolean {
    return this.#state.busy || this.#state.recovery.length > 0 || !this.#state.recoveryLoaded
  }
  async initialize(): Promise<void> {
    if (this.#closed || this.#state.busy) return
    this.#set({ busy: true })
    let listSelection = false
    try {
      const pending = await this.bridge.getPendingProjectRestoreOperations()
      if (pending.ok) {
        this.#set({
          recovery: pending.data.map((item) => ({
            operationId: item.operationId,
            projectId: item.projectId,
          })),
          recoveryLoaded: true,
        })
        // 首启可能尚未选中任何项目；此时不发起检查点列表读取，避免无效的
        // listProjectCheckpoints 请求污染首启界面。App 在打开/创建项目完成
        // management 尾段后显式触发一次刷新。
        listSelection = !!this.#state.selectedProjectId
      } else
        this.#set({
          error: pending.error,
          notice: '未能核对原恢复操作，请关闭并重新打开应用后核对。',
        })
    } catch {
      this.#set({ error: safeError(undefined) })
    } finally {
      this.#set({ busy: false })
    }
    if (listSelection) await this.refresh()
  }
  select(projectId: string | undefined): void {
    if (this.#state.selectedProjectId === projectId) return
    this.#selection++
    this.#request++
    this.#set({
      selectedProjectId: projectId,
      list: undefined,
      preview: undefined,
      pages: [],
      readSegmentHashes: [],
      document: undefined,
      confirmation: undefined,
    })
  }
  async refresh(cursor: string | null = null): Promise<void> {
    if (this.#closed || this.#state.busy) return
    if (!this.#state.selectedProjectId) {
      // 无选中项目时不发起 listProjectCheckpoints；面板提示需先打开项目。
      this.#set({ list: undefined })
      return
    }
    const request = ++this.#request
    this.#set({ busy: true, error: undefined })
    try {
      const result = await this.bridge.listProjectCheckpoints({ pageSize: 20, cursor })
      if (request !== this.#request || this.#closed) return
      if (result.ok) this.#set({ list: result.data })
      else this.#set({ error: result.error })
    } catch {
      if (request === this.#request) this.#set({ error: safeError(undefined) })
    } finally {
      if (request === this.#request) this.#set({ busy: false })
    }
  }
  /** 等待进行中的操作结束后再刷新一次；供选中项目变化的自动同步使用。 */
  async refreshWhenIdle(): Promise<void> {
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
    if (this.#closed) return
    await this.refresh()
  }
  async createCheckpoint(label: string | null): Promise<void> {
    if (this.#closed || this.unresolved) return
    const request = ++this.#request
    this.#set({ busy: true, error: undefined, notice: '' })
    try {
      const result = await this.bridge.createProjectCheckpoint({
        operationId: this.makeId(),
        label: label && label.trim() ? label.trim() : null,
      })
      if (request !== this.#request || this.#closed) return
      if (!result.ok) this.#set({ error: result.error })
      else {
        this.#set({ notice: '已创建手动检查点。' })
        await this.refresh()
      }
    } catch {
      if (request === this.#request) this.#set({ error: safeError(undefined) })
    } finally {
      if (request === this.#request) this.#set({ busy: false })
    }
  }
  async previewRestore(targetCheckpointRef: string): Promise<void> {
    if (this.#closed || this.unresolved) return
    const selection = this.#selection
    const request = ++this.#request
    this.#set({
      busy: true,
      error: undefined,
      notice: '',
      preview: undefined,
      pages: [],
      readSegmentHashes: [],
      document: undefined,
      confirmation: undefined,
    })
    const current = () =>
      !this.#closed && selection === this.#selection && request === this.#request
    try {
      const management = await this.bridge.getProjectManagementState()
      if (!current()) return
      if (!management.ok) {
        this.#set({
          error: management.error,
          notice:
            management.error.code === 'REVISION_CONFLICT'
              ? '项目版本已变化，请刷新后重新预览。'
              : '',
        })
        return
      }
      const result = await this.bridge.previewProjectRestore({
        targetCheckpointRef,
        expectedCheckpointRef: management.data.checkpointRef,
        expectedLifecycleVersion: management.data.lifecycle.version,
      })
      if (!current()) return
      if (!result.ok) {
        this.#set({
          error: result.error,
          notice:
            result.error.code === 'REVISION_CONFLICT'
              ? '项目版本已变化，请刷新后重新预览。'
              : result.error.code === 'INVALID_REQUEST'
                ? '该检查点不可恢复（可能就是当前状态）。请选择其他检查点。'
                : '',
        })
        return
      }
      this.#set({ preview: result.data, notice: '请完整阅读恢复影响，再明确确认。' })
      await this.#readAllPages(result.data)
    } catch {
      if (current()) this.#set({ error: safeError(undefined) })
    } finally {
      if (request === this.#request) this.#set({ busy: false })
    }
  }
  async #readAllPages(preview: ProjectRestorePreviewDTO): Promise<void> {
    const pages: ProjectRestorePageDTO[] = []
    const hashes: string[] = []
    let cursor: string | null = null
    do {
      const page = await this.bridge.getProjectRestorePage({
        previewRef: preview.previewRef,
        cursor,
      })
      if (!page.ok) throw new Error(page.error.code)
      pages.push(page.data)
      for (const segment of page.data.segments) hashes.push(segment.sha256)
      cursor = page.data.nextCursor
    } while (cursor !== null)
    const raw = decodeSegmentText(pages.flatMap((page) => page.segments))
    this.#set({
      pages,
      readSegmentHashes: hashes,
      document: JSON.parse(raw) as RestoreImpactDocument,
    })
  }
  cancelPreview(): void {
    if (this.#state.busy) return
    this.#request++
    this.#set({
      preview: undefined,
      pages: [],
      readSegmentHashes: [],
      document: undefined,
      confirmation: undefined,
      notice: '已取消；未提交恢复。',
      error: undefined,
    })
  }
  async confirmRestore(): Promise<void> {
    const state = this.#state
    if (this.#closed || this.unresolved || !state.preview || !state.document) return
    const request = ++this.#request
    this.#set({ busy: true, error: undefined })
    try {
      const result = await this.bridge.confirmProjectRestore({
        previewRef: state.preview.previewRef,
        documentHash: state.preview.documentHash,
        readSegmentHashes: state.readSegmentHashes,
      })
      if (request !== this.#request || this.#closed) return
      if (!result.ok) {
        this.#set({
          error: result.error,
          notice: '确认未通过：需要先完整阅读全部影响分段，且项目状态未变化。',
        })
        return
      }
      this.#set({ confirmation: result.data, notice: '已确认。请再次确认执行整项目恢复。' })
    } catch {
      if (request === this.#request) this.#set({ error: safeError(undefined) })
    } finally {
      if (request === this.#request) this.#set({ busy: false })
    }
  }
  async applyRestore(): Promise<void> {
    const state = this.#state
    if (this.#closed || this.unresolved || !state.confirmation || !state.preview) return
    const request = ++this.#request
    this.#set({ busy: true, error: undefined })
    try {
      const result = await this.bridge.restoreProject({
        operationId: this.makeId(),
        confirmationRef: state.confirmation.confirmationRef,
        documentHash: state.preview.documentHash,
      })
      if (request !== this.#request || this.#closed) return
      if (!result.ok) {
        this.#set({
          error: result.error,
          notice:
            result.error.code === 'REVISION_CONFLICT'
              ? '项目状态已变化，恢复未执行。请重新预览后再试。'
              : '操作结果尚未确认；保留原操作，请勿重复提交，可核对原操作。',
        })
        return
      }
      this.#accept(result.data)
    } catch {
      this.#set({ error: safeError(undefined), notice: '结果未知；请核对原操作，勿重复提交。' })
    } finally {
      if (request === this.#request) this.#set({ busy: false })
    }
  }
  #accept(result: ProjectRestoreResultDTO): void {
    if (this.#closed) return
    this.#set({
      preview: undefined,
      pages: [],
      readSegmentHashes: [],
      document: undefined,
      confirmation: undefined,
      notice: '整项目恢复已完成；历史运行、审计与操作证物保持不变。',
    })
    this.applied(result)
  }
  async reconcile(): Promise<void> {
    const pending = this.#state.recovery[0]
    if (this.#closed || this.#state.busy || !pending) return
    this.#set({ busy: true, error: undefined })
    try {
      const record = await this.#operationState(pending.operationId)
      if (!record.ok) {
        this.#set({
          error: record.error,
          notice: '操作结果尚未确认；保留原操作，请关闭并重新打开应用后核对，勿重复提交。',
        })
        return
      }
      if (record.data.state === 'applied') this.#accept(record.data.result)
      else
        this.#set({
          recovery: this.#state.recovery.filter((item) => item.operationId !== pending.operationId),
          notice: '已核实原恢复操作未提交。如需继续，请重新预览并确认。',
        })
    } catch {
      this.#set({ error: safeError(undefined) })
    } finally {
      this.#set({ busy: false })
    }
  }
  async #operationState(operationId: string): Promise<BridgeResult<ProjectRestoreOperationDTO>> {
    // Main recomputes the durable request hash from its own journal; the
    // renderer only names the original operation identity.
    return this.bridge.getProjectRestoreOperation({ operationId })
  }
  close(): void {
    this.#closed = true
    this.#selection++
    for (const listener of this.#listeners) listener()
    this.#listeners.clear()
  }
}

/** Concatenate base64 segments into UTF-8 text without trusting any preview hint. */
export function decodeSegmentText(
  segments: Array<{ ordinal: number; dataBase64: string }>,
): string {
  const ordered = [...segments].sort((a, b) => a.ordinal - b.ordinal)
  const bytes = ordered.flatMap((segment) =>
    Array.from(atob(segment.dataBase64), (c) => c.charCodeAt(0)),
  )
  return new TextDecoder('utf-8', { fatal: true }).decode(new Uint8Array(bytes))
}
