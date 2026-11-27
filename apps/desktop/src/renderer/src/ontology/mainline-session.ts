import { safeBusiness3Error, type BridgeResult, type JobView } from '@ontolearn/contracts'
import type {
  CurrentProject,
  DraftSaveArgs,
  DomainRead,
  EditPlan,
  OntologyMainlineBridge,
  Preview,
} from './mainline-api'
import { readFullDiff } from './mainline-diff'
import { ontologyOperations, OntologyOperationBook } from './mainline-operations'
import { closedBookmark, pendingBookmark, recoveredPending } from './mainline-recovery'
import { readOwnershipConflictDetail } from './mainline-ownership'
import type { OwnershipConflictDetailViewModel } from './OwnershipConflictDetailView'

export const ONTOLOGY_EDITOR = 'ontology-transaction'
export type CommitMarker = {
  projectId: string
  operationId: string
  jobId: string
  planHash: string
  projectRevision: number
  beforeSnapshotId: string
  afterSnapshotId: string
}
export type PreparedEdit = {
  preview: Preview
  rows: unknown[]
  completionCursor: string
}
export type PendingEdit = {
  operationId: string
  /** Comparison only; recovered data is never used to replay a confirmation. */
  confirmationRef: string
  preview: Pick<
    Extract<Preview, { status: 'ready' }>,
    'projectId' | 'baseRevision' | 'inputSnapshotId' | 'preparedPlanRef' | 'parametersHash'
  >
  job?: JobView
  /** Local control-flow knowledge only. Never restored from a bookmark. */
  unsubmitted?: boolean
  bookmarkSave?: DraftSaveArgs
  draftBeforeAttempt?: string | null
  cleanupSave?: DraftSaveArgs
  /** A returned CAS/state rejection may require a fresh UI cleanup intent. */
  cleanupNeedsRefresh?: boolean
  observedMarker?: CommitMarker
}
export type SessionState = {
  phase: 'idle' | 'reading' | 'preparing' | 'ready' | 'submitting' | 'pending' | 'unknown' | 'saved'
  source?: DomainRead
  prepared?: PreparedEdit
  pending?: PendingEdit
  receipt?: CommitMarker
  error?: string
  ownershipDetail?:
    | { status: 'reading' | 'unavailable' }
    | { status: 'ready'; viewModel: OwnershipConflictDetailViewModel }
  stale: boolean
}
const unwrap = <T>(result: BridgeResult<T>): T => {
  if (!result.ok) throw new Error(result.error.code)
  return result.data
}
class DraftSaveRejected extends Error {}
export function sourceIdentity(source: DomainRead): string {
  return JSON.stringify([
    source.projectId,
    source.domain.projectRevision,
    source.inputSnapshotId,
    Object.entries(source.domain.dependencyVector).sort(([a], [b]) => a.localeCompare(b)),
  ])
}
function matches(source: DomainRead, current: CurrentProject | null): boolean {
  return (
    !!current &&
    current.projectId === source.projectId &&
    current.projectRevision === source.domain.projectRevision &&
    current.inputSnapshotId === source.inputSnapshotId &&
    JSON.stringify(Object.entries(current.dependencyVector).sort()) ===
      JSON.stringify(Object.entries(source.domain.dependencyVector).sort())
  )
}
const message = (cause: unknown) => {
  // Only fixed UI messages and canonical error codes; never print arbitrary exceptions.
  const allowed = new Set([
    'STALE_CONTEXT',
    'INVALID_CHANGESET_DOCUMENT',
    'INVALID_RECEIPT',
    'INVALID_PREVIEW',
    'PERMISSION_DENIED',
    'INVALID_STATE',
    'INVALID_REQUEST',
    'RESOURCE_LIMIT',
    'STORAGE_FAILURE',
    'STORAGE_BUSY',
    'IDENTITY_CONFLICT',
    'OWNERSHIP_CONFLICT',
    'REVISION_CONFLICT',
    'ENGINE_DISCONNECTED',
    'ENGINE_UNAVAILABLE',
    'INTERNAL_ERROR',
    'CANCELLED',
  ])
  return cause instanceof Error && allowed.has(cause.message) ? cause.message : 'INTERNAL_ERROR'
}

/** One UI context, using the real named bridge. It cannot authorize a write itself.
 * An entered commit retains its original operation ID until authoritative reconciliation.
 */
export class OntologySession {
  #state: SessionState = { phase: 'idle', stale: true }
  #listeners = new Set<() => void>()
  #sequence = 0
  #disposed = false
  #retired = false
  #generation?: number
  #reconciling = false
  #cleaning = false
  #release?: () => void
  #releaseBook?: () => void
  #bookWriting = false
  #readFlight?: Promise<void>
  #queuedRead?: Promise<void>
  #initialReadDone = false
  #initialWaiters = new Set<() => void>()
  constructor(
    readonly bridge: OntologyMainlineBridge,
    readonly operations: OntologyOperationBook = ontologyOperations,
  ) {}
  #resolveInitialWaiters(): void {
    this.#initialReadDone = true
    for (const notify of this.#initialWaiters) notify()
    this.#initialWaiters.clear()
  }
  /** Wait until the auto-triggered initial read settles or the session retires/disposes. */
  whenInitialReadSettled(): Promise<void> {
    if (this.#retired || this.#disposed || this.#initialReadDone) {
      return this.#readFlight ?? Promise.resolve()
    }
    return new Promise<void>((resolve) => {
      this.#initialWaiters.add(resolve)
    })
  }
  /** Page attachment: subscribe synchronously; cleanup cancels its queued auto-read. */
  connectForPage(): () => void {
    this.connect()
    let active = true
    queueMicrotask(() => {
      if (active && !this.#retired) void this.read()
      else this.#resolveInitialWaiters()
    })
    return () => {
      if (!active) return
      active = false
      this.dispose()
    }
  }
  connect(): void {
    if (this.#retired) return
    if (this.#release) return
    this.#disposed = false
    this.#releaseBook = this.operations.subscribe(() => {
      if (this.#bookWriting || !this.#state.source) return
      const entry = this.operations.get(this.#state.source.projectId)
      if (
        JSON.stringify(entry?.pending) === JSON.stringify(this.#state.pending) &&
        JSON.stringify(entry?.receipt) === JSON.stringify(this.#state.receipt)
      )
        return
      this.#sequence++
      this.#set({
        pending: entry?.pending,
        receipt: entry?.receipt,
        phase: entry?.pending ? 'unknown' : entry?.receipt ? 'saved' : 'idle',
        prepared: undefined,
        ownershipDetail: undefined,
        stale: true,
      })
    })
    this.#release = this.bridge.onTaskUpdate((update) => {
      if (this.#generation !== undefined && update.generation < this.#generation) return
      if (this.#generation !== undefined && update.generation !== this.#generation)
        this.invalidate()
      this.#generation = update.generation
      if (update.kind === 'connection') this.invalidate()
      const jobs =
        update.kind === 'job' ? [update.job] : update.kind === 'restored' ? update.view.jobs : []
      for (const job of jobs) {
        const pending = this.operations.get(job.projectId)?.pending
        if (pending && this.#boundJob(pending, job) && this.#followsJob(pending.job, job)) {
          this.#book(() => this.operations.pending({ ...pending, job }))
          if (this.#state.source?.projectId === job.projectId)
            this.#set({ pending: { ...pending, job } })
        }
      }
      if (
        update.kind === 'restored' &&
        this.#state.source &&
        !matches(this.#state.source, update.view.project)
      )
        this.invalidate()
    })
  }
  getSnapshot = (): SessionState => this.#state
  subscribe = (listener: () => void): (() => void) => {
    this.#listeners.add(listener)
    return () => this.#listeners.delete(listener)
  }
  #set(patch: Partial<SessionState>): void {
    if (this.#disposed) return
    this.#state = { ...this.#state, ...patch }
    for (const listener of this.#listeners) listener()
  }
  #guard(sequence: number): void {
    if (this.#retired || this.#disposed || sequence !== this.#sequence)
      throw new Error('STALE_CONTEXT')
  }
  invalidate(): void {
    this.#sequence++
    this.#set({
      stale: true,
      prepared: undefined,
      ownershipDetail: undefined,
      error: 'STALE_CONTEXT',
      phase: this.#state.pending ? 'unknown' : 'idle',
    })
  }
  dispose(): void {
    this.#disposed = true
    this.#sequence++
    if (this.#state.ownershipDetail) this.#state = { ...this.#state, ownershipDetail: undefined }
    this.#release?.()
    this.#release = undefined
    this.#releaseBook?.()
    this.#releaseBook = undefined
    this.#resolveInitialWaiters()
  }
  /** Host calls synchronously BEFORE its first selection/session-changing call.
   * This context can never reconnect. A settled host selection needs a new instance.
   * Already-dispatched acknowledgements still belong to the original operation book.
   */
  retire(): void {
    if (this.#retired) return
    this.#retired = true
    this.invalidate()
    this.dispose()
  }
  #book(work: () => void): void {
    this.#bookWriting = true
    try {
      work()
    } finally {
      this.#bookWriting = false
    }
  }
  #boundJob(pending: PendingEdit, job: JobView): boolean {
    const input = job.input
    const stableFlat = (value: unknown) =>
      value && typeof value === 'object'
        ? JSON.stringify(Object.entries(value).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)))
        : ''
    return (
      job.projectId === pending.preview.projectId &&
      job.operationId === pending.operationId &&
      job.capability === 'changeset.commit' &&
      job.confirmationRef === pending.confirmationRef &&
      (!pending.job ||
        (job.jobId === pending.job.jobId &&
          stableFlat(job.implementation) === stableFlat(pending.job.implementation) &&
          stableFlat(job.limits) === stableFlat(pending.job.limits))) &&
      job.inputSnapshotId === pending.preview.inputSnapshotId &&
      !!input &&
      typeof input === 'object' &&
      'preparedPlanRef' in input &&
      input.preparedPlanRef === pending.preview.preparedPlanRef &&
      'inputSnapshotId' in input &&
      input.inputSnapshotId === pending.preview.inputSnapshotId &&
      'parametersHash' in input &&
      input.parametersHash === pending.preview.parametersHash &&
      'scope' in input &&
      input.scope === 'asserted' &&
      'definitionId' in input &&
      input.definitionId === 'changeset' &&
      'derivedResultIds' in input &&
      Array.isArray(input.derivedResultIds) &&
      input.derivedResultIds.length === 0
    )
  }
  #followsJob(previous: JobView | undefined, next: JobView): boolean {
    if (!previous) return true
    if (next.stateVersion < previous.stateVersion) return false
    if (next.stateVersion === previous.stateVersion && next.state !== previous.state) return false
    if (['succeeded', 'failed', 'cancelled'].includes(previous.state))
      return next.state === previous.state && next.stateVersion === previous.stateVersion
    return true
  }
  #hasJobMarker(job: JobView | undefined): boolean {
    const progress = job?.commitProgress as { mode?: unknown; marker?: unknown } | undefined
    return progress?.mode === 'atomic' && progress.marker !== null && progress.marker !== undefined
  }
  async #findOriginalJob(pending: PendingEdit, sequence: number): Promise<JobView | undefined> {
    const remembered = this.operations.get(pending.preview.projectId)?.pending?.job
    if (remembered && this.#boundJob(pending, remembered)) return remembered
    let cursor: string | null = null
    let snapshot: string | null = null
    const seen = new Set<string>()
    // A bounded lookup may remain unknown. It never manufactures a negative receipt.
    for (let index = 0; index < 32; index++) {
      this.#guard(sequence)
      const page: Record<string, unknown> = unwrap(
        await this.bridge.listJobs({
          filter: 'all',
          pageSize: 100,
          listSnapshotId: snapshot,
          cursor,
        }),
      )
      this.#guard(sequence)
      const binding = page.binding as Record<string, unknown> | undefined
      if (
        !binding ||
        binding.projectId !== pending.preview.projectId ||
        binding.filter !== 'all' ||
        binding.order !== 'createdAtMs+jobId:asc' ||
        typeof binding.listSnapshotId !== 'string' ||
        (snapshot !== null && snapshot !== binding.listSnapshotId) ||
        !Array.isArray(page.jobs)
      )
        throw new Error('INVALID_RECEIPT')
      snapshot = binding.listSnapshotId
      for (const job of page.jobs as JobView[]) {
        if (this.#boundJob(pending, job)) return job
      }
      if (page.nextCursor === null) return
      if (typeof page.nextCursor !== 'string' || seen.has(page.nextCursor))
        throw new Error('INVALID_RECEIPT')
      seen.add(page.nextCursor)
      cursor = page.nextCursor
    }
  }
  async read(): Promise<void> {
    if (this.#retired || this.#disposed) return
    if (this.#readFlight) {
      if (!this.#queuedRead) {
        this.#sequence++ // An older read cannot publish as this refresh's result.
        const again = () => {
          this.#queuedRead = undefined
          return this.read()
        }
        this.#queuedRead = this.#readFlight.then(again, again)
      }
      if (this.#state.ownershipDetail) this.#set({ ownershipDetail: undefined })
      return this.#queuedRead
    }
    const requestedSequence = ++this.#sequence
    // Reserve the slot before callbacks or state publication can request another
    // read. All entry points share one flight and at most one coalesced refresh.
    const flight = Promise.resolve().then(async () => {
      if (this.#retired || this.#disposed || requestedSequence !== this.#sequence) return
      await this.#readNow()
    })
    this.#readFlight = flight
    const release = () => {
      if (this.#readFlight === flight) this.#readFlight = undefined
      this.#resolveInitialWaiters()
    }
    void flight.then(release, release)
    if (this.#state.ownershipDetail) this.#set({ ownershipDetail: undefined })
    return flight
  }
  async #readNow(): Promise<void> {
    const sequence = ++this.#sequence
    this.#set({ phase: 'reading', prepared: undefined, error: undefined, stale: true })
    try {
      this.#guard(sequence)
      const source = unwrap(await this.bridge.readProject({ editor: ONTOLOGY_EDITOR }))
      this.#guard(sequence)
      let entry = this.operations.get(source.projectId)
      const recovered = recoveredPending(source)
      if (
        recovered &&
        entry?.closedOperationId !== recovered.operationId &&
        entry?.receipt?.operationId !== recovered.operationId
      ) {
        if (!entry?.pending) this.#book(() => this.operations.pending(recovered))
        else if (entry.pending.operationId !== recovered.operationId)
          throw new Error('INVALID_STATE')
        entry = this.operations.get(source.projectId)
      }
      this.#set({
        source: structuredClone(source),
        stale: false,
        pending: entry?.pending,
        receipt: entry?.receipt,
        phase: entry?.pending ? 'pending' : entry?.receipt ? 'saved' : 'idle',
      })
    } catch (cause) {
      if (!this.#disposed && sequence === this.#sequence)
        this.#set({ phase: this.#state.pending ? 'unknown' : 'idle', error: message(cause) })
    }
  }
  async #current(source: DomainRead, sequence: number): Promise<void> {
    this.#guard(sequence)
    const active = unwrap(await this.bridge.getActiveProject())
    this.#guard(sequence)
    if (!matches(source, active)) throw new Error('STALE_CONTEXT')
  }
  async prepare(plan: EditPlan): Promise<void> {
    return this.#prepare({ intent: 'change', plan: structuredClone(plan) })
  }
  async prepareUndo(): Promise<void> {
    if (this.#retired) return
    const receipt = this.#state.receipt
    if (!receipt || this.#state.pending) return
    // Undo is a new operation with a freshly read base, never an inverted local diff.
    await this.read()
    if (this.#state.source?.projectId !== receipt.projectId || this.#state.stale) return
    await this.#prepare({ intent: 'undo', targetOperationId: receipt.operationId })
  }
  async #prepare(
    intent: { intent: 'change'; plan: EditPlan } | { intent: 'undo'; targetOperationId: string },
  ): Promise<void> {
    const source = this.#state.source
    if (
      this.#retired ||
      !source ||
      this.#state.stale ||
      this.#state.pending ||
      ['reading', 'preparing', 'submitting'].includes(this.#state.phase)
    )
      return
    const sequence = ++this.#sequence
    this.#set({
      phase: 'preparing',
      prepared: undefined,
      error: undefined,
      ownershipDetail: undefined,
    })
    const identity = sourceIdentity(source)
    const requireCurrent = () => {
      this.#guard(sequence)
      if (
        this.#state.source !== source ||
        sourceIdentity(source) !== identity ||
        this.#state.stale ||
        this.#state.pending
      )
        throw new Error('STALE_CONTEXT')
    }
    try {
      await this.#current(source, sequence)
      requireCurrent()
      const result = await this.bridge.previewProjectChangeset({
        baseRevision: source.domain.projectRevision,
        ...intent,
      })
      requireCurrent()
      if (!result.ok && result.error.code === 'OWNERSHIP_CONFLICT') {
        this.#set({ error: 'OWNERSHIP_CONFLICT', ownershipDetail: { status: 'reading' } })
        try {
          const error = safeBusiness3Error(result.error)
          if (error.code !== 'OWNERSHIP_CONFLICT' || typeof error.params.detailRef !== 'string')
            throw new Error('INVALID_OWNERSHIP_DETAIL')
          await this.#current(source, sequence)
          requireCurrent()
          const viewModel = await readOwnershipConflictDetail(
            this.bridge,
            {
              projectId: source.projectId,
              detailRef: error.params.detailRef,
              sourceBaseRevision: source.domain.projectRevision,
            },
            requireCurrent,
          )
          requireCurrent()
          await this.#current(source, sequence)
          requireCurrent()
          this.#set({ phase: 'idle', ownershipDetail: { status: 'ready', viewModel } })
        } catch (cause) {
          requireCurrent()
          if (cause instanceof Error && cause.message === 'STALE_CONTEXT') {
            this.invalidate()
          } else {
            this.#set({ phase: 'idle', ownershipDetail: { status: 'unavailable' } })
          }
        }
        return
      }
      const preview = unwrap(result)
      if (
        preview.projectId !== source.projectId ||
        preview.baseRevision !== source.domain.projectRevision ||
        (preview.status === 'ready' &&
          (preview.inputSnapshotId !== source.inputSnapshotId ||
            preview.intent !== intent.intent ||
            preview.targetOperationId !==
              (intent.intent === 'undo' ? intent.targetOperationId : null))) ||
        (preview.status === 'conflict' &&
          (intent.intent !== 'undo' || preview.targetOperationId !== intent.targetOperationId))
      )
        throw new Error('INVALID_PREVIEW')
      const full = await readFullDiff(this.bridge, preview, () => this.#guard(sequence))
      this.#guard(sequence)
      this.#set({ phase: 'ready', prepared: { preview, ...full } })
    } catch (cause) {
      if (!this.#disposed && sequence === this.#sequence)
        this.#set({
          phase: 'idle',
          error: message(cause),
          prepared: undefined,
          ownershipDetail: undefined,
        })
    }
  }
  discardPreview(): void {
    if (this.#state.pending || this.#state.phase === 'submitting') return
    this.#sequence++
    this.#set({ prepared: undefined, phase: 'idle', ownershipDetail: undefined })
  }
  /** Called only by the explicit human confirmation button after displaying all rows. */
  async confirm(): Promise<void> {
    const { source, prepared, pending, stale } = this.#state
    if (
      this.#retired ||
      !source ||
      !prepared ||
      prepared.preview.status !== 'ready' ||
      pending ||
      stale ||
      this.#state.phase !== 'ready'
    )
      return
    const sequence = ++this.#sequence
    const preview = prepared.preview
    this.#set({ phase: 'submitting', error: undefined })
    let entered = false
    let reserved: PendingEdit | undefined
    try {
      await this.#current(source, sequence)
      this.#guard(sequence)
      const confirmation = unwrap(
        await this.bridge.confirmProjectChangeset({
          previewHash: preview.previewHash,
          completionCursor: prepared.completionCursor,
        }),
      )
      this.#guard(sequence)
      if (
        confirmation.projectId !== preview.projectId ||
        confirmation.previewHash !== preview.previewHash ||
        confirmation.preparedPlanRef !== preview.preparedPlanRef ||
        confirmation.inputSnapshotId !== preview.inputSnapshotId ||
        confirmation.parametersHash !== preview.parametersHash
      )
        throw new Error('INVALID_PREVIEW')
      await this.#current(source, sequence)
      this.#guard(sequence)
      const operation: PendingEdit = {
        operationId: crypto.randomUUID(),
        preview,
        unsubmitted: true,
        confirmationRef: confirmation.confirmationRef,
        draftBeforeAttempt:
          source.workspace.draft.state === 'present' ? source.workspace.draft.contentJson : null,
      }
      const contentJson = pendingBookmark(source, operation)
      operation.bookmarkSave = {
        operationId: crypto.randomUUID(),
        editor: ONTOLOGY_EDITOR,
        expectedGeneration:
          source.workspace.draft.state === 'missing' ? 0 : source.workspace.draft.generation,
        boundDomainRevision: source.domain.projectRevision,
        contentJson,
      }
      reserved = operation
      this.#book(() => this.operations.pending(operation))
      this.#set({ pending: operation })
      // Persist the original attempted operation in the owning project's UI draft
      // before entering the domain write. This bookmark grants no retry authority.
      await this.#saveDraft(operation.bookmarkSave, source.projectId, sequence)
      this.#guard(sequence)
      await this.#current(source, sequence)
      this.#guard(sequence)
      operation.unsubmitted = false
      this.#book(() => this.operations.pending(operation))
      this.#set({ pending: operation })
      this.#guard(sequence)
      entered = true
      const job = unwrap(
        await this.bridge.commitProjectChangeSet({
          operationId: operation.operationId,
          confirmation,
        }),
      )
      // Keep a real accepted operation even if its UI context was invalidated meanwhile.
      if (!this.#boundJob(operation, job)) throw new Error('INVALID_RECEIPT')
      if (
        this.operations.get(operation.preview.projectId)?.closedOperationId ===
        operation.operationId
      )
        return
      const remembered = this.operations.get(operation.preview.projectId)?.pending ?? operation
      const latest = remembered.job
      const accepted = {
        ...remembered,
        job: latest && latest.stateVersion > job.stateVersion ? latest : job,
      }
      this.#book(() => this.operations.pending(accepted))
      if (this.#disposed) return
      this.#set({ pending: accepted, phase: 'pending', prepared: undefined })
      if (sequence === this.#sequence) await this.reconcile()
    } catch (cause) {
      if (!entered && reserved) {
        const remembered = this.operations.get(reserved.preview.projectId)?.pending
        if (remembered?.operationId === reserved.operationId) {
          reserved = { ...remembered, unsubmitted: true }
          const unsubmitted = reserved
          this.#book(() => this.operations.pending(unsubmitted))
          if (this.#state.pending?.operationId === reserved.operationId)
            this.#set({ pending: reserved })
        }
      }
      if (!this.#disposed && (reserved || sequence === this.#sequence))
        this.#set({
          phase: reserved ? 'unknown' : 'idle',
          error: message(cause),
          prepared: undefined,
        })
      if (!entered && reserved && !this.#disposed) {
        await this.clearUnsubmitted()
        if (!this.#disposed && !this.#state.pending) this.#set({ error: message(cause) })
      }
    }
  }
  async #saveDraft(args: DraftSaveArgs, projectId: string, sequence: number): Promise<void> {
    this.#guard(sequence)
    const result = await this.bridge.saveProjectDraft(args)
    if (!result.ok) throw new DraftSaveRejected(result.error.code)
    const saved = result.data
    const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(args.contentJson))
    const contentHash = Array.from(new Uint8Array(bytes), (byte) =>
      byte.toString(16).padStart(2, '0'),
    ).join('')
    if (
      saved.draftSaveVersion !== 1 ||
      saved.projectId !== projectId ||
      saved.operationId !== args.operationId ||
      saved.editor !== args.editor ||
      saved.generation !== args.expectedGeneration + 1 ||
      saved.boundDomainRevision !== args.boundDomainRevision ||
      saved.contentHash !== contentHash
    )
      throw new Error('INVALID_RECEIPT')
  }
  async clearUnsubmitted(): Promise<void> {
    if (this.#retired) return
    const pending = this.#state.pending
    if (!pending?.unsubmitted || this.#cleaning) return
    this.#cleaning = true
    const sequence = ++this.#sequence
    this.#set({ phase: 'submitting', prepared: undefined })
    try {
      let cleanup = pending.cleanupSave
      if (!cleanup || pending.cleanupNeedsRefresh) {
        this.#guard(sequence)
        const fresh = unwrap(await this.bridge.readProject({ editor: ONTOLOGY_EDITOR }))
        this.#guard(sequence)
        if (fresh.projectId !== pending.preview.projectId) throw new Error('STALE_CONTEXT')
        const other = recoveredPending(fresh)
        const content =
          fresh.workspace.draft.state === 'present' ? fresh.workspace.draft.contentJson : null
        const value: unknown = content === null ? null : JSON.parse(content)
        const ownClosure =
          value &&
          typeof value === 'object' &&
          'reconciliationVersion' in value &&
          value.reconciliationVersion === 1 &&
          'pending' in value &&
          value.pending === null &&
          'closedOperationId' in value &&
          value.closedOperationId === pending.operationId
        if (
          (other && other.operationId !== pending.operationId) ||
          (!other && !ownClosure && content !== null && content !== pending.draftBeforeAttempt)
        )
          throw new Error('INVALID_STATE')
        const generation =
          fresh.workspace.draft.state === 'missing' ? 0 : fresh.workspace.draft.generation
        if (
          cleanup &&
          cleanup.boundDomainRevision === fresh.domain.projectRevision &&
          cleanup.expectedGeneration === generation
        ) {
          // The rejection has no observed CAS change: retain the original save.
          // A generic INVALID_STATE does not prove that a save was unaccepted.
        } else {
          // This is a new cancellation of an unsubmitted UI intent, not a retry of
          // an unknown domain commit. Fresh application generation CAS prevents
          // a late original bookmark write from overwriting this closure. A prior
          // cleanup might itself have committed; no negative claim is made about
          // it. Only the locally known unsubmitted domain intent is being closed.
          cleanup = {
            operationId: crypto.randomUUID(),
            editor: ONTOLOGY_EDITOR,
            expectedGeneration: generation,
            boundDomainRevision: fresh.domain.projectRevision,
            contentJson: closedBookmark(fresh, pending.operationId),
          }
        }
        const remembered = { ...pending, cleanupSave: cleanup, cleanupNeedsRefresh: false }
        this.#book(() => this.operations.pending(remembered))
        this.#set({ pending: remembered })
      }
      // A lost cleanup acknowledgement retries this exact original save ID/args.
      await this.#saveDraft(cleanup, pending.preview.projectId, sequence)
      this.#guard(sequence)
      this.#book(() => this.operations.terminal(pending))
      this.#set({ pending: undefined, phase: 'idle', stale: true })
      await this.read()
    } catch (cause) {
      if (
        cause instanceof DraftSaveRejected &&
        ['REVISION_CONFLICT', 'INVALID_STATE'].includes(cause.message)
      ) {
        const remembered = {
          ...(this.operations.get(pending.preview.projectId)?.pending ?? pending),
          cleanupNeedsRefresh: true,
        }
        this.#book(() => this.operations.pending(remembered))
        this.#set({ pending: remembered })
      }
      if (!this.#disposed && sequence === this.#sequence)
        this.#set({ phase: 'unknown', error: message(cause) })
    } finally {
      this.#cleaning = false
    }
  }
  async reconcile(): Promise<void> {
    if (this.#retired) return
    const initial = this.#state.pending
    if (!initial || this.#state.phase === 'submitting' || this.#reconciling) return
    if (initial.unsubmitted) return this.clearUnsubmitted()
    let pending: PendingEdit = initial
    this.#reconciling = true
    const sequence = ++this.#sequence
    this.#set({ error: undefined })
    try {
      this.#guard(sequence)
      const raw = unwrap(await this.bridge.getOperation(pending.operationId))
      this.#guard(sequence)
      if (raw) {
        const marker = raw as CommitMarker
        if (
          marker.projectId !== pending.preview.projectId ||
          marker.operationId !== pending.operationId ||
          typeof marker.planHash !== 'string' ||
          !/^[a-f0-9]{64}$/.test(marker.planHash) ||
          marker.beforeSnapshotId !== pending.preview.inputSnapshotId ||
          !Number.isSafeInteger(marker.projectRevision) ||
          marker.projectRevision <= pending.preview.baseRevision ||
          typeof marker.afterSnapshotId !== 'string' ||
          !marker.afterSnapshotId ||
          typeof marker.jobId !== 'string' ||
          (pending.job && marker.jobId !== pending.job.jobId)
        )
          throw new Error('INVALID_RECEIPT')
        if (
          pending.observedMarker &&
          ![
            'projectId',
            'operationId',
            'jobId',
            'planHash',
            'projectRevision',
            'beforeSnapshotId',
            'afterSnapshotId',
          ].every(
            (key) =>
              pending.observedMarker?.[key as keyof CommitMarker] ===
              marker[key as keyof CommitMarker],
          )
        )
          throw new Error('INVALID_RECEIPT')
        pending = { ...pending, observedMarker: marker }
        const observed = pending
        this.#book(() => this.operations.pending(observed))
        this.#set({ pending })
        this.#guard(sequence)
        const job = unwrap(await this.bridge.getJob(marker.jobId))
        this.#guard(sequence)
        const progress = job.commitProgress as
          { mode?: unknown; operationId?: unknown; marker?: Record<string, unknown> } | undefined
        if (
          job.state !== 'succeeded' ||
          !this.#boundJob(pending, job) ||
          !this.#followsJob(pending.job, job) ||
          job.jobId !== marker.jobId ||
          progress?.mode !== 'atomic' ||
          progress.operationId !== marker.operationId ||
          !progress.marker ||
          !['planHash', 'projectRevision', 'beforeSnapshotId', 'afterSnapshotId'].every(
            (key) => progress.marker?.[key] === marker[key as keyof CommitMarker],
          )
        )
          throw new Error('INVALID_RECEIPT')
        this.#book(() => this.operations.terminal(pending, marker))
        this.#set({ receipt: marker, pending: undefined, phase: 'saved', prepared: undefined })
        // A refresh failure must not erase this authenticated committed result.
        await this.read()
        const fresh = this.#state.source
        if (
          !this.#state.stale &&
          fresh &&
          (fresh.projectId !== marker.projectId ||
            fresh.domain.projectRevision < marker.projectRevision ||
            (fresh.domain.projectRevision === marker.projectRevision &&
              fresh.inputSnapshotId !== marker.afterSnapshotId))
        )
          this.#set({ stale: true, error: 'INVALID_RECEIPT' })
        return
      }
      if (pending.observedMarker || this.#hasJobMarker(pending.job))
        throw new Error('INVALID_RECEIPT')
      if (!pending.job) {
        const recovered = await this.#findOriginalJob(pending, sequence)
        this.#guard(sequence)
        if (!recovered) {
          this.#set({ phase: 'unknown' })
          return // Null is not proof that an entered write never happened.
        }
        pending = { ...pending, job: recovered }
        const remembered = pending
        this.#book(() => this.operations.pending(remembered))
        this.#set({ pending })
      }
      const jobId = pending.job?.jobId
      if (!jobId) throw new Error('INVALID_RECEIPT')
      this.#guard(sequence)
      const job = unwrap(await this.bridge.getJob(jobId))
      this.#guard(sequence)
      if (!this.#boundJob(pending, job) || job.jobId !== jobId) throw new Error('INVALID_RECEIPT')
      if (!this.#followsJob(pending.job, job)) throw new Error('INVALID_RECEIPT')
      pending = { ...pending, job }
      const observedJob = pending
      this.#book(() => this.operations.pending(observedJob))
      this.#set({ pending })
      if (job.state === 'failed' || job.state === 'cancelled') {
        const progress = job.commitProgress as
          { mode?: unknown; operationId?: unknown; marker?: unknown } | undefined
        if (
          progress?.mode !== 'atomic' ||
          progress.operationId !== pending.operationId ||
          progress.marker !== null
        )
          throw new Error('INVALID_RECEIPT')
        if (
          job.resultRef !== null ||
          (job.state === 'failed' ? job.error === null : job.error !== null) ||
          typeof job.finishedAtMs !== 'number' ||
          job.finishedAtMs !== job.updatedAtMs ||
          typeof job.createdAtMs !== 'number' ||
          job.finishedAtMs < job.createdAtMs
        )
          throw new Error('INVALID_RECEIPT')
        this.#book(() => this.operations.terminal(pending))
        this.#set({
          pending: undefined,
          prepared: undefined,
          phase: 'idle',
          stale: true,
          error: job.state === 'cancelled' ? 'CANCELLED' : (job.error?.code ?? 'INTERNAL_ERROR'),
        })
      } else
        this.#set({
          pending: { ...pending, job },
          phase: job.state === 'succeeded' ? 'unknown' : 'pending',
        })
    } catch (cause) {
      if (!this.#disposed && sequence === this.#sequence)
        this.#set({ phase: 'unknown', error: message(cause) })
    } finally {
      this.#reconciling = false
    }
  }
  async cancel(): Promise<void> {
    if (this.#retired) return
    const pending = this.#state.pending
    if (!pending?.job) return
    const sequence = this.#sequence
    try {
      this.#guard(sequence)
      unwrap(await this.bridge.cancelJob(pending.job.jobId))
      // Cancellation acknowledgement is not a terminal state or rollback proof.
      await this.reconcile()
    } catch (cause) {
      this.#set({ error: message(cause) })
    }
  }
}
