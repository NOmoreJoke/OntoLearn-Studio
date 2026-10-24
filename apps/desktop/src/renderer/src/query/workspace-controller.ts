import { z } from 'zod'
import { validateV2 } from '../../../../../../packages/contracts/src/v2'
import type {
  BridgeResult,
  SafeError,
  QueryConsumerBridge,
  MainlineProjectBridge,
  MainlineProjectReadDTO,
  QueryDraftDTO,
  QueryDefinitionLoadDTO,
  QuerySelectionDTO,
  MainlineDraftSaveArgs,
  MainlineDraftSaveResultDTO,
  ChangeSetPreview,
  ChangeSetPage,
  ChangeSetManifest,
  ChangeSetConfirmation,
  JobView,
  TaskUpdate,
  TaskView,
  QueryExecuteArgs,
} from './api002-source-types'
import { draftSchema, definitionIdSchema } from './draft'
import {
  displayDescriptor,
  displayRows,
  displayText,
  type DisplayDescriptor,
} from './typed-results'
import type { QueryResultPanelProps } from './typed-result-panel-props'

// Named public methods only. T01 supplies the real bridge and canonical verifier.
export type QueryWorkspaceBridge = QueryConsumerBridge &
  Pick<
    MainlineProjectBridge,
    | 'readProject'
    | 'saveProjectDraft'
    | 'previewProjectChangeset'
    | 'getProjectDiffPage'
    | 'confirmProjectChangeset'
    | 'commitProjectChangeSet'
  > & {
    listJobs(options: {
      filter: 'all' | 'active' | 'terminal'
      pageSize: number
      listSnapshotId: string | null
      cursor: string | null
    }): Promise<BridgeResult<Record<string, unknown>>>
    getJob(jobId: string): Promise<BridgeResult<JobView>>
    getOperation(operationId: string): Promise<BridgeResult<Record<string, unknown> | null>>
    cancelJob(jobId: string): Promise<BridgeResult<Record<string, unknown>>>
    onTaskUpdate(listener: (update: TaskUpdate) => void): () => void
  }
export type VerifyFullDiff = (
  expected: { projectId: string; previewHash: string; manifest: ChangeSetManifest },
  pages: readonly ChangeSetPage[],
) => Promise<unknown[]>
export const QUERY_EDITOR = 'query-workspace-v1'
const initialDraft: QueryDraftDTO = {
  name: '',
  description: '',
  sparql: '',
  scope: 'asserted',
  capabilityQuestion: '',
  source: 'editor',
}
const freeze = <T>(value: T): T => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const child of Object.values(value)) freeze(child)
    Object.freeze(value)
  }
  return value
}
const rawText = z.string().refine((value) => !/[\uD800-\uDFFF]/u.test(value))
const scratchDraft = z
  .object({
    name: rawText.max(128),
    description: rawText.max(4096),
    sparql: rawText.max(65536),
    scope: z.enum(['asserted', 'asserted+derived']),
    capabilityQuestion: rawText.max(4096),
    source: z.enum(['template', 'visual', 'editor', 'model']),
  })
  .strict()
const sha256 = async (text: string) =>
  Array.from(
    new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))),
    (byte) => byte.toString(16).padStart(2, '0'),
  ).join('')
const unicodeCompare = (a: string, b: string) => {
  const ac = Array.from(a, (character) => character.codePointAt(0)!),
    bc = Array.from(b, (character) => character.codePointAt(0)!)
  for (let i = 0; i < Math.min(ac.length, bc.length); i++) if (ac[i] !== bc[i]) return ac[i] - bc[i]
  return ac.length - bc.length
}
const clone = <T>(value: T): T => structuredClone(value)
export const canonicalQueryJson = (value: unknown): string => {
  if (value === null || typeof value !== 'object') {
    if (typeof value === 'string' && /[\uD800-\uDFFF]/u.test(value))
      throw new Error('INVALID_STATE')
    if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('INVALID_STATE')
    const text = JSON.stringify(value)
    if (text === undefined) throw new Error('INVALID_STATE')
    return text
  }
  if (Array.isArray(value)) return '[' + value.map(canonicalQueryJson).join(',') + ']'
  return (
    '{' +
    Object.keys(value)
      .sort(unicodeCompare)
      .map(
        (key) =>
          JSON.stringify(key) + ':' + canonicalQueryJson((value as Record<string, unknown>)[key]),
      )
      .join(',') +
    '}'
  )
}
const equal = (a: unknown, b: unknown) => a === b || canonicalQueryJson(a) === canonicalQueryJson(b)
const terminal = (job: JobView) => ['succeeded', 'failed', 'cancelled'].includes(job.state)
class ReadFailure extends Error {
  constructor(readonly safe: SafeError) {
    super(safe.code)
  }
}
const take = <T>(result: BridgeResult<T>): T => {
  if (!result.ok) throw new ReadFailure(result.error)
  return result.data
}

type Preview = {
  ready: Extract<ChangeSetPreview, { status: 'ready' }>
  diff: unknown[]
  completionCursor: string
  edit: number
  draft: QueryDraftDTO
  definitionId: string
}
type PendingWrite =
  | { kind: 'draft'; args: MainlineDraftSaveArgs; edit: number }
  | { kind: 'commit'; operationId: string; preview: Preview; confirmation: ChangeSetConfirmation }
  | { kind: 'execute'; args: QueryExecuteArgs; definitionId: string; expectedSnapshotId: string }
type JobObservation = { job: JobView; conflict: boolean; counterexample?: JobView }
type ResultLane = 'result' | 'historyResult'
interface QueryHistory {
  listSnapshotId: string
  cursor: string | null
  seenCursors: string[]
  lastKey?: { createdAtMs: number; jobId: string }
  page: number
  jobs: JobView[]
}
export interface QueryWorkspaceState {
  projectId: string
  read?: MainlineProjectReadDTO
  draft: QueryDraftDTO
  definitionId: string
  selection: QuerySelectionDTO
  loaded?: QueryDefinitionLoadDTO
  edit: number
  document: number
  dirty: boolean
  draftBaseRevision?: number
  jobReconciled?: boolean
  jobObservationConflict?: boolean
  reconcileList?: { operationId: string; listSnapshotId: string; cursor: string | null }
  busy: boolean
  notice: string
  error?: SafeError
  preview?: Preview
  pending?: PendingWrite
  draftReceipt?: MainlineDraftSaveResultDTO
  job?: JobView
  jobKind?: 'commit' | 'execute'
  jobDefinitionId?: string
  jobDraft?: QueryDraftDTO
  jobExpectedInput?: Record<string, unknown>
  jobConfirmationRef?: unknown
  watchPending?: boolean
  cancelRequested?: boolean
  result?: QueryResultPanelProps
  history?: QueryHistory
  historySelection?: JobView
  historyResult?: QueryResultPanelProps
  resultView: 'current' | 'history'
  operationMarker?: Record<string, unknown> | null
}

/** Retain this instance while an entered write is unresolved; disconnect never erases it. */
export class QueryWorkspaceController {
  private state: QueryWorkspaceState
  private listeners = new Set<() => void>()
  private view = 0
  private release?: () => void
  private taskGeneration?: number
  private connection = 0
  private observation = 0
  private observationReady = false
  private leases = new Set<symbol>()
  private pendingJob?: { intent: PendingWrite } & JobObservation
  // A conflict blocks new writes. Only the prior Job and the one write already
  // awaiting ACK can acquire separate holds; unrelated jobs are never ingested.
  private jobConflicts = new Map<string, { original: JobView; counterexample: JobView }>()
  constructor(
    readonly projectId: string,
    readonly bridge: QueryWorkspaceBridge,
    readonly verifyDiff: VerifyFullDiff,
  ) {
    this.state = {
      projectId,
      draft: clone(initialDraft),
      definitionId: '',
      selection: { kind: 'current' },
      edit: 0,
      document: 0,
      dirty: false,
      busy: false,
      resultView: 'current',
      notice: '请读取当前项目。',
    }
    freeze(this.state)
  }
  getSnapshot = () => this.state
  subscribe = (listener: () => void) => {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }
  private set(patch: Partial<QueryWorkspaceState>) {
    if ('pending' in patch && patch.pending !== this.state.pending) this.pendingJob = undefined
    this.state = freeze({ ...this.state, ...patch })
    for (const fn of this.listeners) fn()
  }
  /** Each caller owns only its lease. App seeds the actual current restored view. */
  connect(view?: TaskView): () => void {
    if (
      view &&
      (view.project?.projectId !== this.projectId ||
        !Number.isSafeInteger(view.generation) ||
        view.generation < 0 ||
        (this.taskGeneration !== undefined && view.generation < this.taskGeneration))
    )
      return () => {}
    const lease = Symbol()
    this.leases.add(lease)
    if (!this.release) {
      const connection = ++this.connection
      this.observationReady = true
      let stop: (() => void) | undefined
      this.release = () => stop?.()
      try {
        stop = this.bridge.onTaskUpdate((update) => {
          if (connection === this.connection) this.observeTask(update)
        })
        if (connection !== this.connection) stop()
      } catch (error) {
        if (connection === this.connection) this.disconnect()
        throw error
      }
    }
    if (view && this.leases.has(lease))
      this.observeTask({ kind: 'restored', generation: view.generation, view })
    return () => {
      if (!this.leases.delete(lease)) return
      if (!this.leases.size) this.disconnect()
    }
  }
  private observeTask(update: TaskUpdate) {
    const project =
      update.kind === 'restored'
        ? update.view.project?.projectId
        : update.kind === 'job'
          ? update.job.projectId
          : update.projectId
    if (
      project !== this.projectId ||
      !Number.isSafeInteger(update.generation) ||
      update.generation < 0 ||
      (update.kind === 'restored' && update.view.generation !== update.generation) ||
      (this.taskGeneration !== undefined && update.generation < this.taskGeneration)
    )
      return
    if (
      (this.taskGeneration !== undefined && update.generation > this.taskGeneration) ||
      update.kind === 'connection' ||
      (update.kind === 'restored' &&
        this.state.read &&
        update.view.project &&
        (update.view.project.inputSnapshotId !== this.state.read.inputSnapshotId ||
          update.view.project.projectRevision !== this.state.read.domain.projectRevision))
    ) {
      this.view++
      this.observation++
      this.set({
        read: undefined,
        loaded: undefined,
        preview: undefined,
        result: undefined,
        history: undefined,
        historySelection: undefined,
        historyResult: undefined,
        notice: '任务视图已换代；保留原任务/操作和编辑，请重新核对项目。',
      })
    }
    this.taskGeneration = update.generation
    if (update.kind === 'connection') {
      this.observationReady = false
      return
    }
    if (update.kind === 'restored') {
      this.observationReady = true
      for (const job of update.view.jobs) this.observeJob(job)
    } else if (this.observationReady) this.observeJob(update.job)
  }
  private observeJob(job: JobView) {
    const current = this.state.job
    if (current) {
      const observed = this.compareObservation(job, current)
      if (observed) {
        this.retainConflict(current, observed.counterexample)
        this.set({
          job: clone(observed.job),
          jobObservationConflict: this.state.jobObservationConflict || observed.conflict,
          jobReconciled: observed.conflict ? false : this.state.jobReconciled,
          notice: terminal(observed.job)
            ? '收到真实终态，请刷新并核对持久结果。'
            : this.state.notice,
        })
      }
    }
    const intent = this.state.pending
    if (!intent || !this.matchesIntent(job, intent)) return
    const previous = this.pendingJob
    const candidate: JobObservation | undefined =
      previous?.intent === intent
        ? this.compareObservation(job, previous.job)
        : { job, conflict: false }
    if (candidate)
      this.pendingJob = {
        intent,
        job: clone(candidate.job),
        conflict: previous?.conflict || candidate.conflict,
        counterexample: this.preferMarker(previous?.counterexample, candidate.counterexample),
      }
  }
  private matchesIntent(job: JobView, pending: PendingWrite): boolean {
    if (pending.kind === 'draft' || !validateV2('job', job)) return false
    const commit = pending.kind === 'commit'
    const operationId = commit ? pending.operationId : pending.args.operationId
    const snapshotId = commit ? pending.confirmation.inputSnapshotId : pending.expectedSnapshotId
    const input = job.input as Record<string, unknown>
    if (
      !input ||
      job.projectId !== this.projectId ||
      job.operationId !== operationId ||
      job.capability !== (commit ? 'changeset.commit' : 'query.execute') ||
      job.inputSnapshotId !== snapshotId ||
      input.inputSnapshotId !== snapshotId ||
      input.scope !== 'asserted' ||
      input.parametersHash !== job.parametersHash ||
      !equal(input.derivedResultIds, [])
    )
      return false
    return commit
      ? equal(input, {
          inputSnapshotId: snapshotId,
          scope: 'asserted',
          definitionId: 'changeset',
          parametersHash: pending.confirmation.parametersHash,
          derivedResultIds: [],
          preparedPlanRef: pending.confirmation.preparedPlanRef,
        }) && job.confirmationRef === pending.confirmation.confirmationRef
      : input.definitionId === pending.definitionId &&
          input.preparedPlanRef === null &&
          job.confirmationRef === null
  }
  /** Exactly one read per validated receipt; never retries or performs a write. */
  private async observeAcceptedJob(original: JobView) {
    if (!this.release || !this.observationReady) return
    const connection = this.connection,
      observation = this.observation
    try {
      const reply = await this.bridge.getJob(original.jobId)
      if (
        !reply.ok ||
        !this.release ||
        !this.observationReady ||
        connection !== this.connection ||
        observation !== this.observation
      )
        return
      const current = this.state.job
      if (!current || !this.sameJob(current, original)) return
      const observed = this.compareObservation(reply.data, current)
      if (observed) {
        this.retainConflict(current, observed.counterexample)
        this.set({
          job: clone(observed.job),
          jobObservationConflict: this.state.jobObservationConflict || observed.conflict,
          jobReconciled: observed.conflict ? false : this.state.jobReconciled,
          notice: terminal(observed.job)
            ? '收到真实终态，请刷新并核对持久结果。'
            : this.state.notice,
        })
      }
    } catch {
      // A failed observation cannot erase an accepted Job or settle UNKNOWN.
    }
  }
  private sameJob(incoming: JobView, current: JobView): boolean {
    if (
      !validateV2('job', incoming) ||
      incoming.projectId !== this.projectId ||
      incoming.jobId !== current.jobId ||
      incoming.operationId !== current.operationId ||
      incoming.inputSnapshotId !== current.inputSnapshotId ||
      incoming.capability !== current.capability
    )
      return false
    if (
      [
        'input',
        'parametersHash',
        'implementation',
        'limits',
        'dependencyVector',
        'definitionSetDigests',
        'confirmationRef',
        'scope',
        'createdAtMs',
      ].some((key) => !equal(incoming[key], current[key]))
    )
      return false
    const before = current.commitProgress as { mode: string; operationId?: string }
    const after = incoming.commitProgress as { mode: string; operationId?: string }
    return before.mode === after.mode && before.operationId === after.operationId
  }
  private mergeJob(incoming: JobView, current: JobView): JobView | undefined {
    if (!this.sameJob(incoming, current)) return
    if (incoming.stateVersion < current.stateVersion) return
    if (incoming.stateVersion === current.stateVersion && !equal(incoming, current)) return
    if (terminal(current) && !equal(incoming, current)) return
    const before = current.commitProgress as { mode?: unknown; marker?: unknown }
    const after = incoming.commitProgress as { mode?: unknown; marker?: unknown }
    if (before.mode === 'atomic' && before.marker && !equal(before.marker, after.marker)) return
    return incoming
  }
  private compareObservation(incoming: JobView, current: JobView): JobObservation | undefined {
    if (!this.sameJob(incoming, current)) return
    const next = this.mergeJob(incoming, current)
    if (next) return { job: next, conflict: false }
    if (this.mergeJob(current, incoming)) return { job: current, conflict: false }
    // Two canonical, immutable-bound observations cannot be ordered without
    // contradicting a terminal/version/marker. Retain the original AND a
    // bounded counterexample; a later ordinary refresh cannot erase this hold.
    return { job: current, conflict: true, counterexample: incoming }
  }
  private preferMarker(previous?: JobView, incoming?: JobView) {
    if (!incoming) return previous
    if (
      previous &&
      ((previous.commitProgress as { marker?: unknown }).marker ||
        !(incoming.commitProgress as { marker?: unknown }).marker)
    )
      return previous
    return clone(incoming)
  }
  private retainConflict(original: JobView, incoming?: JobView) {
    if (!incoming) return
    const key = `${original.operationId}:${original.jobId}`
    const previous = this.jobConflicts.get(key)
    this.jobConflicts.set(key, {
      original: previous?.original ?? clone(original),
      counterexample: this.preferMarker(previous?.counterexample, incoming)!,
    })
  }
  private holdReconciliation() {
    if (!this.state.jobObservationConflict) return false
    this.set({
      jobReconciled: false,
      notice: '原任务状态记录互相矛盾；保留相关原任务与提交责任，暂不能完成核验。',
    })
    return true
  }
  private rememberOperationMarker(job: JobView, marker: Record<string, unknown> | null) {
    if (
      !marker ||
      !validateV2('commitMarker', marker) ||
      marker.projectId !== job.projectId ||
      marker.operationId !== job.operationId ||
      marker.jobId !== job.jobId
    )
      return
    const known = this.state.operationMarker
    if (known?.operationId === job.operationId && !equal(known, marker)) return
    this.set({ operationMarker: clone(marker) })
  }
  disconnect() {
    this.view++
    this.connection++
    this.observation++
    this.observationReady = false
    // Already authenticated original-Job facts survive detach, like state.job.
    // Old callbacks are fenced; only a validated ACK may adopt this candidate.
    this.leases.clear()
    const release = this.release
    this.release = undefined
    release?.()
  }
  get hasUnresolvedWrite() {
    return (
      !!this.state.pending ||
      (!!this.state.job &&
        (this.state.jobObservationConflict ||
          !terminal(this.state.job) ||
          (this.state.jobKind === 'commit' && !this.state.jobReconciled)))
    )
  }
  private async action(work: (view: number) => Promise<void>) {
    if (this.state.busy) return
    const view = this.view
    this.set({ busy: true, error: undefined })
    try {
      await work(view)
    } catch (error) {
      if (view === this.view)
        this.set({
          error: error instanceof ReadFailure ? clone(error.safe) : undefined,
          notice:
            error instanceof ReadFailure
              ? `操作未完成：${error.safe.code}；保留当前内容与原操作。`
              : '结果无法确认；保留原操作与当前内容，请对账或按原参数重试。',
        })
    } finally {
      this.set({ busy: false })
    }
  }
  private live(view: number) {
    if (view !== this.view) throw new Error('STALE_VIEW')
  }
  editDraft(patch: Partial<QueryDraftDTO>) {
    this.set({
      draft: { ...this.state.draft, ...patch },
      edit: this.state.edit + 1,
      dirty: true,
      preview: undefined,
      notice: '当前编辑未提交；不会改变已有结果。',
    })
  }
  setDefinitionId(id: string) {
    this.set({
      definitionId: id,
      loaded: undefined,
      edit: this.state.edit + 1,
      dirty: true,
      preview: undefined,
    })
  }
  setSelection(selection: QuerySelectionDTO) {
    this.set({
      selection: clone(selection),
      loaded: undefined,
      preview: undefined,
      edit: this.state.edit + 1,
      notice: '输入已改变，请按所选输入重新载入查询。',
    })
  }
  reviewCurrentBase() {
    if (this.hasUnresolvedWrite || !this.state.read) return
    this.set({
      draftBaseRevision: this.state.read.domain.projectRevision,
      loaded: undefined,
      preview: undefined,
      dirty: true,
      edit: this.state.edit + 1,
      notice: '已明确选择把当前草稿用于已读领域版本；仍须完整差异核验与确认。',
    })
  }
  replaceDraft(draft: QueryDraftDTO) {
    this.editDraft(draftSchema.parse(draft))
    this.set({ document: this.state.document + 1 })
  }
  newQuery() {
    if (this.hasUnresolvedWrite) return
    this.set({
      draft: clone(initialDraft),
      draftBaseRevision: this.state.read?.domain.projectRevision,
      document: this.state.document + 1,
      definitionId: '',
      loaded: undefined,
      preview: undefined,
      dirty: false,
      edit: this.state.edit + 1,
    })
  }
  private checkRead(read: MainlineProjectReadDTO) {
    if (
      read.projectId !== this.projectId ||
      read.workspace.projectId !== this.projectId ||
      read.workspace.draft.editor !== QUERY_EDITOR ||
      read.inputSnapshotId !== read.workspace.inputSnapshotId ||
      read.domain.projectRevision !== read.workspace.domainRevision
    )
      throw new Error('INVALID_STATE')
  }
  open = () =>
    this.action(async (view) => {
      if (this.hasUnresolvedWrite) throw new Error('UNRESOLVED_WRITE')
      const edit = this.state.edit,
        read = take(await this.bridge.readProject({ editor: QUERY_EDITOR }))
      this.checkRead(read)
      this.live(view)
      if (this.state.edit !== edit) throw new Error('EDIT_CHANGED')
      let draft = clone(initialDraft),
        definitionId = ''
      const durable = read.workspace.draft
      if (durable.state !== 'missing' && durable.present && durable.contentJson !== null) {
        const content = JSON.parse(durable.contentJson)
        if (content.version !== 1) throw new Error('INVALID_DRAFT')
        draft = scratchDraft.parse(content.draft)
        definitionId = rawText.max(128).parse(content.definitionId)
      }
      this.set({
        read: clone(read),
        draftBaseRevision:
          durable.state !== 'missing' && durable.present
            ? durable.boundDomainRevision
            : read.domain.projectRevision,
        edit: this.state.edit + 1,
        document: this.state.document + 1,
        draft,
        definitionId,
        loaded: undefined,
        preview: undefined,
        dirty: false,
        notice: '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
      })
    })
  load = () =>
    this.action(async (view) => {
      if (this.hasUnresolvedWrite) throw new Error('UNRESOLVED_WRITE')
      const id = definitionIdSchema.parse(this.state.definitionId),
        selection = clone(this.state.selection),
        edit = this.state.edit
      const base = take(await this.bridge.getQueryDefinitionBase())
      this.live(view)
      if (
        selection.kind === 'current' &&
        this.state.read &&
        (base.projectRevision !== this.state.read.domain.projectRevision ||
          base.inputSnapshotId !== this.state.read.inputSnapshotId)
      )
        throw new Error('BASE_CHANGED')
      const loaded = take(await this.bridge.loadQueryDefinition({ definitionId: id, selection }))
      this.live(view)
      if (
        this.state.edit !== edit ||
        loaded.projectId !== this.projectId ||
        loaded.definitionId !== id ||
        (selection.kind === 'historical' && loaded.inputSnapshotId !== selection.snapshotId) ||
        (selection.kind === 'current' &&
          (loaded.baseProjectRevision !== base.projectRevision ||
            loaded.inputSnapshotId !== base.inputSnapshotId))
      )
        throw new Error('INVALID_LOAD')
      this.set({
        loaded: clone(loaded),
        draftBaseRevision: loaded.baseProjectRevision,
        document: this.state.document + 1,
        edit: this.state.edit + 1,
        draft:
          loaded.kind === 'managed'
            ? clone(loaded.draft)
            : { ...clone(initialDraft), sparql: loaded.text },
        dirty: false,
        preview: undefined,
        notice:
          loaded.kind === 'legacy'
            ? '旧查询仅有执行文本；请补全信息，经完整差异确认保存为正式受管查询后再执行。'
            : '已载入真实受管定义；后续编辑需先正式提交。',
      })
    })
  saveDraft = () =>
    this.action(async (view) => {
      if (this.state.pending && this.state.pending.kind !== 'draft')
        throw new Error('UNRESOLVED_WRITE')
      let pending = this.state.pending
      if (!pending && this.hasUnresolvedWrite) throw new Error('ACTIVE_JOB')
      if (!pending) {
        const read = this.state.read
        if (!read) throw new Error('NO_BASE')
        if (this.state.draftBaseRevision !== read.domain.projectRevision)
          throw new Error('EXPLICIT_REBASE_REQUIRED')
        const draft = scratchDraft.parse(this.state.draft),
          definitionId = rawText.max(128).parse(this.state.definitionId)
        const contentJson = canonicalQueryJson({ version: 1, definitionId, draft })
        if (new TextEncoder().encode(contentJson).length > 65536) throw new Error('DRAFT_TOO_LARGE')
        pending = {
          kind: 'draft',
          edit: this.state.edit,
          args: {
            operationId: crypto.randomUUID(),
            editor: QUERY_EDITOR,
            expectedGeneration:
              read.workspace.draft.state === 'missing' ? 0 : read.workspace.draft.generation,
            boundDomainRevision: this.state.draftBaseRevision ?? read.domain.projectRevision,
            contentJson,
          },
        }
        this.set({ pending })
      }
      if (pending.kind !== 'draft') return
      const contentHash = await sha256(pending.args.contentJson)
      this.live(view) // A detached editor must not first dispatch into another selected project.
      const receipt = take(await this.bridge.saveProjectDraft(clone(pending.args)))
      // Keep the actual receipt even after detach; never apply it to a replacement document.
      if (
        receipt.projectId !== this.projectId ||
        receipt.operationId !== pending.args.operationId ||
        receipt.editor !== QUERY_EDITOR ||
        receipt.generation !== pending.args.expectedGeneration + 1 ||
        receipt.boundDomainRevision !== pending.args.boundDomainRevision ||
        receipt.draftSaveVersion !== 1 ||
        receipt.contentHash !== contentHash ||
        !/^[a-f0-9]{64}$/.test(receipt.afterCheckpointRef) ||
        !Number.isSafeInteger(receipt.operationSequence) ||
        Object.keys(receipt).length !== 9
      )
        throw new Error('INVALID_RECEIPT')
      this.set({ draftReceipt: clone(receipt), pending: undefined })
      const read = this.state.read ? clone(this.state.read) : undefined
      if (read) {
        const head = read.workspace.draft
        if ((head.state === 'missing' ? 0 : head.generation) <= receipt.generation)
          read.workspace.draft = {
            editor: QUERY_EDITOR,
            state: 'present',
            present: true,
            generation: receipt.generation,
            boundDomainRevision: receipt.boundDomainRevision,
            contentHash: receipt.contentHash,
            contentJson: pending.args.contentJson,
          }
        this.set({ read })
      }
      this.live(view)
      this.set({
        dirty: pending.edit !== this.state.edit,
        notice:
          pending.edit === this.state.edit
            ? '工作草稿已持久化；正式定义尚未提交。'
            : '原操作草稿已保存，当前新编辑仍未保存。',
      })
    })
  prepare = () =>
    this.action(async (view) => {
      if (this.hasUnresolvedWrite || this.state.selection.kind !== 'current')
        throw new Error('SAVE_CURRENT_ONLY')
      const read = this.state.read
      if (!read) throw new Error('NO_BASE')
      if (this.state.draftBaseRevision !== read.domain.projectRevision)
        throw new Error('EXPLICIT_REBASE_REQUIRED')
      const draft = draftSchema.parse(this.state.draft),
        id = definitionIdSchema.parse(this.state.definitionId),
        edit = this.state.edit
      if (draft.scope !== 'asserted') throw new Error('ASSERTED_DERIVED_UNAVAILABLE')
      const previous = read.domain.state.definitions.find(
        (value) => value.layer === 'query' && value.id === id,
      )
      const references = previous ? (JSON.parse(previous.payload).references ?? []) : []
      const { sparql, ...fields } = draft
      const preview = take(
        await this.bridge.previewProjectChangeset({
          baseRevision: read.domain.projectRevision,
          intent: 'change',
          plan: {
            definitions: [
              {
                layer: 'query',
                id,
                value: { text: sparql, references, descriptor: { version: 1, ...fields } },
              },
            ],
          },
        }),
      )
      this.live(view)
      if (this.state.edit !== edit) throw new Error('EDIT_CHANGED')
      if (
        preview.status !== 'ready' ||
        preview.projectId !== this.projectId ||
        preview.baseRevision !== read.domain.projectRevision ||
        preview.intent !== 'change' ||
        preview.manifest.documentKind !== 'diff'
      )
        throw new Error('PREVIEW_CONFLICT')
      const pages: ChangeSetPage[] = []
      let cursor: string | null = null
      for (let count = 0; count < 512; count++) {
        const page: ChangeSetPage = take(
          await this.bridge.getProjectDiffPage({
            previewHash: preview.previewHash,
            documentKind: 'diff',
            pageSize: 16,
            cursor,
          }),
        )
        this.live(view)
        if (this.state.edit !== edit) throw new Error('EDIT_CHANGED')
        if (!page.complete && pages.some((old) => old.nextCursor === page.nextCursor))
          throw new Error('CURSOR_REPEATED')
        pages.push(clone(page))
        if (page.complete) break
        cursor = page.nextCursor
      }
      if (!pages.at(-1)?.complete) throw new Error('DIFF_INCOMPLETE')
      const diff = await this.verifyDiff(
        { projectId: this.projectId, previewHash: preview.previewHash, manifest: preview.manifest },
        pages,
      )
      this.live(view)
      if (this.state.edit !== edit) throw new Error('EDIT_CHANGED')
      this.set({
        draft,
        preview: {
          ready: clone(preview),
          diff: clone(diff),
          completionCursor: pages.at(-1)!.nextCursor,
          edit,
          draft: clone(draft),
          definitionId: id,
        },
        notice: '全部差异已读取并经 canonical verifier 核验；请阅读后明确确认提交。',
      })
    })
  confirmAndCommit = () =>
    this.action(async (view) => {
      const preview = this.state.preview
      if (!preview || preview.edit !== this.state.edit || this.hasUnresolvedWrite)
        throw new Error('INVALID_PREVIEW')
      const confirmation = take(
        await this.bridge.confirmProjectChangeset({
          previewHash: preview.ready.previewHash,
          completionCursor: preview.completionCursor,
        }),
      )
      this.live(view)
      if (preview.edit !== this.state.edit) throw new Error('EDIT_CHANGED')
      if (
        confirmation.projectId !== this.projectId ||
        confirmation.previewHash !== preview.ready.previewHash ||
        confirmation.inputSnapshotId !== preview.ready.inputSnapshotId ||
        confirmation.parametersHash !== preview.ready.parametersHash ||
        confirmation.preparedPlanRef !== preview.ready.preparedPlanRef
      )
        throw new Error('INVALID_CONFIRMATION')
      const operationId = crypto.randomUUID()
      this.set({
        pending: { kind: 'commit', operationId, preview, confirmation: clone(confirmation) },
        reconcileList: undefined,
      })
      const job = take(await this.bridge.commitProjectChangeSet({ operationId, confirmation }))
      this.accept(job, operationId, 'commit', preview.definitionId, preview.draft)
      await this.observeAcceptedJob(job)
      this.live(view)
      this.set({ notice: '正式提交任务已受理；尚不能判定领域保存成功，请刷新任务核对终态。' })
    })
  private accept(
    job: JobView,
    operationId: string,
    kind: 'commit' | 'execute',
    definitionId: string,
    draft: QueryDraftDTO,
  ) {
    if (
      !validateV2('job', job) ||
      job.projectId !== this.projectId ||
      job.operationId !== operationId ||
      job.capability !== (kind === 'commit' ? 'changeset.commit' : 'query.execute')
    )
      throw new Error('INVALID_JOB')
    const pending = this.state.pending
    const expectedSnapshot =
      pending?.kind === 'commit'
        ? pending.confirmation.inputSnapshotId
        : pending?.kind === 'execute'
          ? pending.expectedSnapshotId
          : undefined
    if (!expectedSnapshot || job.inputSnapshotId !== expectedSnapshot)
      throw new Error('INVALID_JOB_INPUT')
    const input = job.input as Record<string, unknown> | undefined
    if (
      !input ||
      input.inputSnapshotId !== job.inputSnapshotId ||
      input.scope !== 'asserted' ||
      input.parametersHash !== job.parametersHash ||
      !equal(input.derivedResultIds, [])
    )
      throw new Error('INVALID_JOB_INPUT')
    if (pending?.kind === 'commit') {
      const expected = {
        inputSnapshotId: pending.confirmation.inputSnapshotId,
        scope: 'asserted',
        definitionId: 'changeset',
        parametersHash: pending.confirmation.parametersHash,
        derivedResultIds: [],
        preparedPlanRef: pending.confirmation.preparedPlanRef,
      }
      if (!equal(input, expected) || job.confirmationRef !== pending.confirmation.confirmationRef)
        throw new Error('INVALID_JOB_INPUT')
    } else if (
      pending?.kind === 'execute' &&
      (input.definitionId !== pending.definitionId ||
        input.preparedPlanRef !== null ||
        job.confirmationRef !== null)
    )
      throw new Error('INVALID_JOB_INPUT')
    const candidate = this.pendingJob
    const bound =
      candidate && candidate.intent === pending && this.sameJob(candidate.job, job)
        ? candidate
        : undefined
    const observed = bound ? this.compareObservation(job, bound.job) : undefined
    if (bound) {
      this.retainConflict(bound.job, bound.counterexample)
      this.retainConflict(bound.job, observed?.counterexample)
    }
    this.set({
      reconcileList: undefined,
      job: clone(observed?.job ?? job),
      jobReconciled: false,
      jobObservationConflict:
        this.state.jobObservationConflict || bound?.conflict || observed?.conflict || false,
      jobExpectedInput: clone(input),
      jobConfirmationRef: job.confirmationRef,
      jobKind: kind,
      jobDefinitionId: definitionId,
      jobDraft: clone(draft),
      pending: undefined,
      cancelRequested: false,
      result: undefined,
      resultView: 'current',
    })
  }
  execute = () =>
    this.action(async (view) => {
      if (
        this.state.job &&
        (this.state.jobObservationConflict ||
          !terminal(this.state.job) ||
          (this.state.jobKind === 'commit' && !this.state.jobReconciled))
      )
        throw new Error('ACTIVE_JOB')
      let pending = this.state.pending
      if (pending && pending.kind !== 'execute') throw new Error('UNRESOLVED_WRITE')
      if (!pending) {
        const loaded = this.state.loaded,
          draft = draftSchema.parse(this.state.draft)
        if (
          !loaded ||
          loaded.kind !== 'managed' ||
          !equal(draft, loaded.draft) ||
          draft.scope !== 'asserted'
        )
          throw new Error('SAVE_OR_LOAD_REQUIRED')
        pending = {
          kind: 'execute',
          expectedSnapshotId: loaded.inputSnapshotId,
          definitionId: loaded.definitionId,
          args: {
            operationId: crypto.randomUUID(),
            loadRef: loaded.loadRef,
            visibleDraft: draft,
            selection: clone(this.state.selection),
          },
        }
        this.set({ pending })
      }
      if (pending.kind !== 'execute') return
      const receipt = take(await this.bridge.executeSavedQuery(clone(pending.args)))
      if (receipt.operationId !== pending.args.operationId) throw new Error('INVALID_RECEIPT')
      this.accept(
        receipt.acceptedJob,
        receipt.operationId,
        'execute',
        pending.definitionId,
        pending.args.visibleDraft,
      )
      this.set({ watchPending: receipt.watch.state === 'pending' })
      await this.observeAcceptedJob(receipt.acceptedJob)
      this.live(view)
      this.set({
        notice:
          receipt.watch.state === 'pending'
            ? '真实任务已受理，观察订阅失败；刷新原 Job，不新建查询。'
            : '查询任务已受理；请以任务终态和固定结果为准。',
      })
    })
  refreshJob = () =>
    this.action(async (view) => {
      const original = this.state.job
      const edit = this.state.edit,
        selection = clone(this.state.selection),
        definitionId = this.state.definitionId
      if (!original) throw new Error('NO_JOB')
      let job = take(await this.bridge.getJob(original.jobId))
      this.live(view)
      if (
        job.jobId !== original.jobId ||
        job.projectId !== this.projectId ||
        job.operationId !== original.operationId ||
        job.inputSnapshotId !== original.inputSnapshotId
      )
        throw new Error('INVALID_JOB')
      const current = this.state.job
      if (!current || current.jobId !== original.jobId) throw new Error('STALE_JOB')
      const observed = this.compareObservation(job, current)
      this.retainConflict(current, observed?.counterexample)
      job = observed?.job ?? current
      this.set({
        job: clone(job),
        jobObservationConflict: this.state.jobObservationConflict || observed?.conflict,
        jobReconciled: observed?.conflict ? false : this.state.jobReconciled,
      })
      if (this.holdReconciliation()) return
      if (!terminal(job)) {
        this.set({ notice: '任务尚未结束。取消 ACK 不代表终态。' })
        return
      }
      if (job.state !== 'succeeded') {
        if (this.state.jobKind === 'execute') {
          this.set({ jobReconciled: true, notice: `查询终态：${job.state}；未产生成功结果。` })
          return
        }
        // T01 OT02/03/04: a full canonical immutable-bound terminal Job is
        // necessary. An operation error/null alone is never negative proof.
        const atomic = job.commitProgress as {
          mode: string
          operationId?: string
          marker?: unknown
        }
        const known = this.state.operationMarker
        const knownOriginal =
          known &&
          known.projectId === job.projectId &&
          known.operationId === job.operationId &&
          known.jobId === job.jobId
        if (
          atomic.mode !== 'atomic' ||
          atomic.operationId !== job.operationId ||
          atomic.marker !== null ||
          knownOriginal
        ) {
          this.set({
            jobReconciled: false,
            notice: '原失败或取消任务存在提交证据或不一致；保留原操作继续对账，未判定回滚。',
          })
          return
        }
        const reply = await this.bridge.getOperation(job.operationId)
        this.live(view)
        if (reply.ok) this.rememberOperationMarker(job, reply.data)
        if (this.holdReconciliation()) return
        if (!reply.ok) {
          this.set({
            jobReconciled: false,
            error: clone(reply.error),
            notice: `已核对原${job.state}终态及任务空marker；原操作交叉核对未完成，保留待决。读取错误不代表未提交。`,
          })
          return
        }
        if (reply.data !== null) {
          this.set({
            jobReconciled: false,
            notice: '原操作返回提交证据或不一致；保留失败或取消任务，未认定回滚。',
          })
          return
        }
        this.set({
          jobReconciled: true,
          notice: `原任务已${job.state}；完整终态与原操作均核对无领域提交。再次保存须由你重新核对差异并确认。`,
        })
        return
      }
      if (this.state.jobKind === 'commit') {
        const markerReply = await this.bridge.getOperation(job.operationId)
        this.live(view)
        if (markerReply.ok) this.rememberOperationMarker(job, markerReply.data)
        if (this.holdReconciliation()) return
        const marker = take(markerReply)
        if (
          !marker ||
          !validateV2('commitMarker', marker) ||
          marker.projectId !== this.projectId ||
          marker.operationId !== job.operationId ||
          marker.jobId !== job.jobId ||
          (this.state.operationMarker?.operationId === job.operationId &&
            !equal(this.state.operationMarker, marker)) ||
          marker.beforeSnapshotId !== job.inputSnapshotId ||
          !equal(job.input, this.state.jobExpectedInput) ||
          job.confirmationRef !== this.state.jobConfirmationRef
        )
          throw new Error('OPERATION_UNCONFIRMED')
        const atomic = job.commitProgress as
          | { mode?: unknown; operationId?: unknown; marker?: Record<string, unknown> | null }
          | undefined
        if (
          !validateV2('commitProgress', atomic) ||
          atomic?.mode !== 'atomic' ||
          atomic.operationId !== job.operationId ||
          !atomic.marker ||
          !['projectRevision', 'beforeSnapshotId', 'afterSnapshotId', 'planHash'].every(
            (field) => atomic.marker![field] === marker[field],
          )
        )
          throw new Error('JOB_MARKER_MISMATCH')
        // Actual terminal + original durable marker settle the original write.
        // Availability/currentness of a later definition is a separate read fact.
        this.set({ operationMarker: clone(marker), jobReconciled: true })
        const savedReply = await this.bridge.loadQueryDefinition({
          definitionId: this.state.jobDefinitionId!,
          selection: { kind: 'historical', snapshotId: marker.afterSnapshotId as string },
        })
        this.live(view)
        if (this.holdReconciliation()) return
        if (!savedReply.ok) {
          this.set({
            error: savedReply.error,
            notice: '原提交成功与operation已核对；历史定义重读无法确认，未建立可复用loadRef。',
          })
          return
        }
        const saved = savedReply.data
        if (
          saved.projectId !== this.projectId ||
          saved.kind !== 'managed' ||
          saved.definitionId !== this.state.jobDefinitionId ||
          saved.inputSnapshotId !== marker.afterSnapshotId ||
          saved.baseProjectRevision !== marker.projectRevision ||
          !equal(saved.draft, this.state.jobDraft)
        )
          throw new Error('ORIGINAL_DEFINITION_MISMATCH')
        if (
          edit !== this.state.edit ||
          definitionId !== this.state.definitionId ||
          !equal(selection, this.state.selection)
        ) {
          this.set({ notice: '原提交历史定义已核对；编辑或输入已改变，不应用迟到载入。' })
          return
        }
        const readReply = await this.bridge.readProject({ editor: QUERY_EDITOR })
        this.live(view)
        if (this.holdReconciliation()) return
        const read = take(readReply)
        this.checkRead(read)
        if (
          read.domain.projectRevision < (marker.projectRevision as number) ||
          (read.domain.projectRevision === marker.projectRevision &&
            read.inputSnapshotId !== marker.afterSnapshotId)
        )
          throw new Error('FRESH_READ_MARKER_MISMATCH')
        if (edit !== this.state.edit || !equal(selection, this.state.selection)) return
        const reply = await this.bridge.loadQueryDefinition({
          definitionId: saved.definitionId,
          selection: { kind: 'current' },
        })
        this.live(view)
        if (this.holdReconciliation()) return
        if (edit !== this.state.edit || !equal(selection, this.state.selection)) return
        const unchanged =
          reply.ok &&
          reply.data.projectId === this.projectId &&
          reply.data.kind === 'managed' &&
          reply.data.definitionId === saved.definitionId &&
          reply.data.inputSnapshotId === read.inputSnapshotId &&
          equal(reply.data.draft, this.state.jobDraft) &&
          equal(this.state.draft, this.state.jobDraft)
        this.set({
          read: clone(read),
          loaded: unchanged ? clone(reply.data) : undefined,
          preview: undefined,
          draftBaseRevision: unchanged ? read.domain.projectRevision : this.state.draftBaseRevision,
          dirty: !unchanged,
          error: reply.ok ? undefined : reply.error,
          notice: unchanged
            ? '真实提交终态、原operation、历史与当前定义均已核对；可执行受管查询。'
            : '原提交历史版本已核对；当前定义已变化或不可读，未把当前loadRef绑定旧编辑，请复核。',
        })
      } else {
        const result = await this.readJobResult(job, view)
        if (this.holdReconciliation()) return
        this.set({
          jobReconciled: true,
          result,
          notice: result.descriptor
            ? '已取得真实结果描述；按固定引用分别读取文本与结果页。'
            : '原任务与结果身份已保留；结果描述读取未完成，请核对读取状态。',
        })
      }
    })
  private async readJobResult(job: JobView, view: number): Promise<QueryResultPanelProps> {
    if (
      !validateV2('job', job) ||
      job.capability !== 'query.execute' ||
      job.state !== 'succeeded' ||
      job.projectId !== this.projectId ||
      !job.resultRef
    )
      throw new Error('NO_QUERY_RESULT')
    const response = await this.bridge.getQueryResultDescriptor({
      resultId: job.resultRef.resultId,
    })
    this.live(view)
    const binding = { projectId: this.projectId, resultId: job.resultRef.resultId }
    if (!response.ok)
      return {
        ...binding,
        descriptor: undefined,
        readFailure: {
          ...binding,
          descriptorRef: null,
          error: response.error,
        },
      }
    const descriptor = displayDescriptor(response.data, binding)
    const input = job.input as Record<string, unknown>
    if (
      descriptor.identity.jobId !== job.jobId ||
      descriptor.identity.inputSnapshotId !== job.inputSnapshotId ||
      descriptor.identity.definitionId !== input.definitionId ||
      descriptor.identity.parametersHash !== job.parametersHash ||
      !equal(descriptor.identity.implementation, job.implementation)
    )
      throw new Error('RESULT_JOB_MISMATCH')
    return { ...binding, descriptor }
  }
  readQueryHistory = (restart = false) =>
    this.action(async (view) => {
      const old = restart ? undefined : this.state.history
      if (old?.cursor === null) {
        this.set({ notice: '本轮历史任务列表已读完；刷新可开始新的固定列表。' })
        return
      }
      const raw = take(
        await this.bridge.listJobs({
          filter: 'terminal',
          pageSize: 100,
          listSnapshotId: old?.listSnapshotId ?? null,
          cursor: old?.cursor ?? null,
        }),
      )
      this.live(view)
      if (!validateV2('jobList', raw)) throw new Error('INVALID_HISTORY_PAGE')
      const page = raw as unknown as {
        binding: { projectId: string; listSnapshotId: string; filter: string; order: string }
        jobs: JobView[]
        nextCursor: string | null
      }
      if (
        page.binding.projectId !== this.projectId ||
        page.binding.filter !== 'terminal' ||
        page.binding.order !== 'createdAtMs+jobId:asc' ||
        page.jobs.length > 100 ||
        (old && page.binding.listSnapshotId !== old.listSnapshotId) ||
        (page.nextCursor !== null && old?.seenCursors.includes(page.nextCursor))
      )
        throw new Error('INVALID_HISTORY_PAGE')
      let lastKey = old?.lastKey
      for (const job of page.jobs) {
        const key = { createdAtMs: job.createdAtMs as number, jobId: job.jobId }
        if (
          job.projectId !== this.projectId ||
          !terminal(job) ||
          (lastKey &&
            (key.createdAtMs < lastKey.createdAtMs ||
              (key.createdAtMs === lastKey.createdAtMs && key.jobId <= lastKey.jobId)))
        )
          throw new Error('INVALID_HISTORY_ORDER')
        lastKey = key
      }
      this.set({
        history: {
          listSnapshotId: page.binding.listSnapshotId,
          cursor: page.nextCursor,
          seenCursors: [...(old?.seenCursors ?? []), ...(page.nextCursor ? [page.nextCursor] : [])],
          lastKey,
          page: (old?.page ?? 0) + 1,
          jobs: clone(page.jobs.filter((job) => job.capability === 'query.execute')),
        },
        notice: '已读取原持久查询任务；选择任务只恢复结果，不执行新查询。',
      })
    })
  restoreQueryResult = (jobId: string) =>
    this.action(async (view) => {
      const listed =
        this.state.history?.jobs.find((job) => job.jobId === jobId) ??
        (this.state.historySelection?.jobId === jobId ? this.state.historySelection : undefined)
      if (!listed || listed.capability !== 'query.execute') throw new Error('NO_HISTORY_JOB')
      this.set({ historySelection: clone(listed), historyResult: undefined, resultView: 'history' })
      const fresh = take(await this.bridge.getJob(jobId))
      this.live(view)
      const job = this.mergeJob(fresh, listed)
      if (!job) throw new Error('HISTORY_JOB_MISMATCH')
      this.set({ historySelection: clone(job) })
      if (job.state !== 'succeeded') {
        this.set({ notice: `原查询任务为${job.state}；没有成功结果，不重新执行。` })
        return
      }
      const result = await this.readJobResult(job, view)
      this.set({
        historyResult: result,
        notice: result.descriptor
          ? '已恢复原查询结果；输入快照与过期状态以该结果的真实描述为准，未重新执行。'
          : '已定位原查询结果；描述读取未完成，保留原任务与快照，未重新执行。',
      })
    })
  showCurrentResult() {
    if (!this.state.busy) this.set({ resultView: 'current' })
  }
  recoverOriginalCommit = () =>
    this.action(async (view) => {
      const pending = this.state.pending
      if (pending?.kind !== 'commit') throw new Error('NO_PENDING_COMMIT')
      const job = take(
        await this.bridge.commitProjectChangeSet({
          operationId: pending.operationId,
          confirmation: clone(pending.confirmation),
        }),
      )
      this.accept(
        job,
        pending.operationId,
        'commit',
        pending.preview.definitionId,
        pending.preview.draft,
      )
      await this.observeAcceptedJob(job)
      this.live(view)
      this.set({ notice: '按原确认与operation取回受理；未生成新操作，请刷新原Job。' })
    })
  restartCommitList() {
    if (this.state.pending?.kind !== 'commit' || this.state.busy) return
    this.set({
      reconcileList: undefined,
      notice: '新一轮固定列表对账将从第一页开始；原operation与UNKNOWN保持，不自动发请求。',
    })
  }
  findOriginalCommitJob = () =>
    this.action(async (view) => {
      const pending = this.state.pending
      if (pending?.kind !== 'commit') throw new Error('NO_PENDING_COMMIT')
      const cached = this.state.reconcileList
      const old = cached?.operationId === pending.operationId ? cached : undefined
      if (old && old.operationId === pending.operationId && old.cursor === null) {
        this.set({ notice: '本次固定列表已读完未找到原Job；不认定未发生，保留UNKNOWN。' })
        return
      }
      const page = take(
        await this.bridge.listJobs({
          filter: 'all',
          pageSize: 100,
          listSnapshotId: old?.listSnapshotId ?? null,
          cursor: old?.cursor ?? null,
        }),
      )
      this.live(view)
      if (!validateV2('jobList', page)) throw new Error('INVALID_JOB_LIST')
      const value = page as unknown as {
        binding: { projectId: string; listSnapshotId: string; filter: string; order: string }
        jobs: JobView[]
        nextCursor: string | null
      }
      if (
        value.binding.projectId !== this.projectId ||
        value.binding.filter !== 'all' ||
        value.binding.order !== 'createdAtMs+jobId:asc' ||
        (old && value.binding.listSnapshotId !== old.listSnapshotId) ||
        (value.nextCursor !== null && value.nextCursor === old?.cursor)
      )
        throw new Error('INVALID_JOB_LIST')
      const matches = value.jobs.filter((job) => job.operationId === pending.operationId)
      if (matches.length > 1) throw new Error('AMBIGUOUS_OPERATION')
      this.set({
        reconcileList: {
          operationId: pending.operationId,
          listSnapshotId: value.binding.listSnapshotId,
          cursor: value.nextCursor,
        },
      })
      if (matches.length) {
        this.accept(
          matches[0],
          pending.operationId,
          'commit',
          pending.preview.definitionId,
          pending.preview.draft,
        )
        this.set({ notice: '在真实固定Job列表找到原operation；未重提，请刷新核对终态。' })
      } else
        this.set({
          notice: value.nextCursor
            ? '本页未找到原Job；可继续同一固定列表。'
            : '完整列表未找到原Job；不能证明未发生，保留UNKNOWN。',
        })
    })
  reconcileCommit = () =>
    this.action(async (view) => {
      const pending = this.state.pending
      if (pending?.kind !== 'commit') throw new Error('NO_UNKNOWN_COMMIT')
      const marker = take(await this.bridge.getOperation(pending.operationId))
      this.live(view)
      if (!marker) {
        this.set({
          notice: '尚无原操作 marker；不能据此认定未提交，保留 UNKNOWN，禁止换 operation 重提。',
        })
        return
      }
      if (
        !validateV2('commitMarker', marker) ||
        marker.projectId !== this.projectId ||
        marker.operationId !== pending.operationId ||
        typeof marker.jobId !== 'string'
      )
        throw new Error('INVALID_MARKER')
      const known = this.state.operationMarker
      if (known?.operationId === pending.operationId && !equal(known, marker))
        throw new Error('CONTRADICTING_MARKER')
      // A later null read or failed Job lookup must not erase known commit evidence.
      this.set({ operationMarker: clone(marker) })
      const job = take(await this.bridge.getJob(marker.jobId))
      this.accept(
        job,
        pending.operationId,
        'commit',
        pending.preview.definitionId,
        pending.preview.draft,
      )
      this.live(view)
      this.set({ notice: '已按原 operation 找到真实 Job；请刷新核对终态。' })
    })
  cancel = () =>
    this.action(async (view) => {
      const job = this.state.job
      if (!job || this.state.jobKind !== 'execute' || terminal(job))
        throw new Error('NO_ACTIVE_QUERY')
      const receipt = take(await this.bridge.cancelJob(job.jobId))
      this.live(view)
      if (!validateV2('result_job.cancel', receipt) || receipt.jobId !== job.jobId)
        throw new Error('INVALID_CANCEL')
      this.set({
        cancelRequested: receipt.disposition !== 'alreadyTerminal',
        notice:
          receipt.disposition === 'alreadyTerminal'
            ? '取消回执：任务已是终态，请刷新原Job。'
            : receipt.disposition === 'alreadyRequested'
              ? '取消回执：此前已请求，仍等待真实终态。'
              : '取消请求已受理；等待原Job真实终态。',
      })
    })
  readRows = (cursor: string | null = null, startIndex = 0, lane: ResultLane = 'result') =>
    this.action(async (view) => {
      const result = this.state[lane]
      if (!result?.descriptor) throw new Error('NO_RESULT')
      const descriptor = result.descriptor as DisplayDescriptor
      const requested = {
        descriptorRef: descriptor.descriptorRef,
        cursor,
        startIndex,
        pageSize: 200,
      }
      const reply = await this.bridge.getQueryRowsPage({
        descriptorRef: requested.descriptorRef,
        cursor,
        pageSize: requested.pageSize,
      })
      this.live(view)
      if (this.state[lane] !== result) throw new Error('STALE_RESULT')
      if (!reply.ok) {
        this.set({
          [lane]: {
            ...result,
            readFailure: {
              projectId: this.projectId,
              resultId: result.resultId,
              descriptorRef: descriptor.descriptorRef,
              error: reply.error,
            },
          },
        })
        return
      }
      const value = displayRows(reply.data, descriptor, requested)
      this.set({ [lane]: { ...result, rows: { value, requested }, readFailure: undefined } })
    })
  readText = (cursor: string | null = null, startUtf8Byte = 0, lane: ResultLane = 'result') =>
    this.action(async (view) => {
      const result = this.state[lane]
      if (!result?.descriptor) throw new Error('NO_RESULT')
      const descriptor = result.descriptor as DisplayDescriptor
      const requested = {
        descriptorRef: descriptor.descriptorRef,
        cursor,
        startUtf8Byte,
        maxUtf8Bytes: 32768,
      }
      const reply = await this.bridge.getQueryExecutedTextPage({
        descriptorRef: requested.descriptorRef,
        cursor,
        maxUtf8Bytes: requested.maxUtf8Bytes,
      })
      this.live(view)
      if (this.state[lane] !== result) throw new Error('STALE_RESULT')
      if (!reply.ok) {
        this.set({
          [lane]: {
            ...result,
            readFailure: {
              projectId: this.projectId,
              resultId: result.resultId,
              descriptorRef: descriptor.descriptorRef,
              error: reply.error,
            },
          },
        })
        return
      }
      const value = displayText(reply.data, descriptor, requested)
      this.set({ [lane]: { ...result, text: { value, requested }, readFailure: undefined } })
    })
}
