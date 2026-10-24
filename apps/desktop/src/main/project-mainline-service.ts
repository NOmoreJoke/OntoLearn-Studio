import { createHash } from 'node:crypto'
import {
  safeError,
  safeDisplayError,
  type BridgeResult,
  type ProjectView,
  type JobView,
  type TaskView,
  type ChangeSetConfirmation,
  type ChangeSetPreview,
  type ChangeSetPage,
  type MainlineProjectBridge,
  type MainlineCatalogDTO,
  type MainlineCreateRequestDTO,
  type MainlineCreateResultDTO,
  type MainlineProjectReadDTO,
  type MainlinePreviewArgs,
  type MainlineExampleCreateRequestDTO,
  type MainlineExampleCreateResultDTO,
  type MainlineDraftSaveArgs,
  type MainlineDraftSaveResultDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '../../../../packages/contracts/src/v2'
import {
  EngineError,
  MainlineProjectTransport,
  EngineSupervisor,
  type MainlineMethod,
  type QueryMainReadBudget,
} from './engine'
import { OrdinaryProjectSource, type OrdinaryCurrent } from './ordinary-project-source'
import { QueryDefinitionService } from './query-definition-service'
import type { TaskService, TaskRecoveryContext, TaskRecoveryRequest } from './task-service'

type RecordValue = Record<string, unknown>
export type MainlineCatalog = MainlineCatalogDTO
export type MainlineCreate = MainlineCreateResultDTO
export type MainlineRead = MainlineProjectReadDTO
type CreateArgs = MainlineCreateRequestDTO
const denied = () =>
  new EngineError({
    code: 'PERMISSION_DENIED',
    messageKey: 'permission.denied',
    params: {},
    retryable: false,
  })
const invalid = () =>
  new EngineError({
    code: 'INVALID_STATE',
    messageKey: 'protocol.invalidState',
    params: {},
    retryable: false,
  })
function stable(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    const encoded = JSON.stringify(value)
    if (typeof encoded !== 'string') throw invalid()
    return encoded
  }
  if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']'
  const row = value as RecordValue
  return (
    '{' +
    Object.keys(row)
      .sort()
      .map((key) => JSON.stringify(key) + ':' + stable(row[key]))
      .join(',') +
    '}'
  )
}

/** Production source: only the supervisor's actual business3 transport may publish. */
export class MainlineProjectSource extends OrdinaryProjectSource {
  #value: OrdinaryCurrent = null
  #revision = 0
  #sequence = 0
  #listeners = new Map<object, (value: OrdinaryCurrent, revision: number) => void>()
  #client?: MainlineProjectTransport
  #disposedMainline = false
  #selectionHolding?: { entry: object; budget: QueryMainReadBudget }
  #selectionHoldingUnknown = false
  constructor(private readonly closeOwner?: (fence: () => void) => void) {
    super(null)
  }
  override get available(): boolean {
    return !this.#disposedMainline && !!this.#value
  }
  override current(): OrdinaryCurrent {
    return this.#value
  }
  override observe(listener: (value: OrdinaryCurrent, revision: number) => void): () => void {
    if (this.#disposedMainline || this.#listeners.size >= 8) throw invalid()
    const ref = Object.freeze({})
    this.#listeners.set(ref, listener)
    try {
      listener(this.#value, this.#revision)
    } catch (cause) {
      this.#listeners.delete(ref)
      throw cause
    }
    return () => {
      this.#listeners.delete(ref)
    }
  }
  #notify(): void {
    this.#revision++
    for (const fn of this.#listeners.values()) {
      try {
        fn(this.#value, this.#revision)
      } catch {
        /* isolate consumer */
      }
    }
  }
  fence(): void {
    if (this.#sequence >= Number.MAX_SAFE_INTEGER) throw invalid()
    this.#sequence++
    this.#value = null
    this.#client = undefined
    const holding = this.#selectionHolding
    if (holding && !this.#selectionHoldingUnknown) {
      try {
        holding.budget.releaseHolding(holding.entry)
        this.#selectionHolding = undefined
      } catch {
        // Keep this original obligation; a new selection cannot refund it.
        this.#selectionHoldingUnknown = true
      }
    }
    this.#notify()
  }
  #keepSelection(client: MainlineProjectTransport): void {
    if (this.#selectionHoldingUnknown || !client.selected) throw invalid()
    const budget = client.supervisor.queryReadBudget(client.owner)
    if (this.#selectionHolding && this.#selectionHolding.budget !== budget) throw invalid()
    const entry = this.#selectionHolding?.entry ?? Object.freeze({})
    try {
      budget.retainHolding(entry, {
        engineSessionId: client.engineSessionId,
        selectionSeq: this.#sequence,
        project: client.selected,
      })
    } catch (cause) {
      this.#selectionHoldingUnknown = true
      this.#value = null
      this.#client = undefined
      this.#notify()
      throw cause
    }
    this.#selectionHolding = { entry, budget }
  }
  preparePublication(client: MainlineProjectTransport, current: () => boolean): () => void {
    if (
      this.#disposedMainline ||
      !MainlineProjectTransport.owns(client) ||
      !EngineSupervisor.owns(client.supervisor) ||
      !client.supervisor.ownsMainlineClient(client) ||
      !client.engineSessionId ||
      !client.selected
    )
      throw denied()
    if (!validateBusiness3('result_project.get', client.selected)) throw invalid()
    if (!current()) throw denied()
    this.#keepSelection(client)
    // Reserve this independently while still inside the real receiver scope.
    // Committing the staged source after consume does not allocate a new holding.
    const sequence = this.#sequence,
      holding = this.#selectionHolding,
      selected = client.selected,
      value = Object.freeze({
        owner: client.owner,
        supervisor: client.supervisor,
        engineSessionId: client.engineSessionId,
        selectionSeq: sequence,
        project: selected,
      })
    let committed = false
    return () => {
      if (
        committed ||
        this.#disposedMainline ||
        !current() ||
        this.#sequence !== sequence ||
        this.#selectionHolding !== holding ||
        client.selected !== selected ||
        !client.supervisor.ownsMainlineClient(client)
      )
        throw denied()
      committed = true
      this.#client = client
      this.#value = value
      this.#notify()
      // An observer can synchronously close/select/dispose. It cannot make this
      // old publication a successful recovery or cause a subsequent restored.
      if (!current() || this.#value !== value || this.#sequence !== sequence) throw denied()
    }
  }
  publish(client: MainlineProjectTransport): void {
    this.preparePublication(client, () => true)()
  }
  override observeProject(
    project: ProjectView,
    supervisor: EngineSupervisor,
    session: string,
  ): void {
    const current = this.#value,
      client = this.#client
    if (
      !current ||
      !client ||
      current.supervisor !== supervisor ||
      current.engineSessionId !== session ||
      project.projectId !== current.project.projectId
    )
      return
    client.acceptProject(project) // Authenticated original response object, not a DTO clone.
    if (project.projectRevision === current.project.projectRevision) {
      if (stable(project) !== stable(current.project)) throw invalid()
      return
    }
    this.#keepSelection(client)
    this.#value = Object.freeze({ ...current, project: client.selected! })
    this.#notify()
  }
  override async closeSelection(): Promise<void> {
    if (this.closeOwner) this.closeOwner(() => this.fence())
    else this.fence()
  }
  override async dispose(): Promise<void> {
    if (!this.#disposedMainline) {
      this.#disposedMainline = true
      if (this.closeOwner) this.closeOwner(() => this.fence())
      else this.fence()
      this.#listeners.clear()
    }
  }
}

type MainlineIntent = {
  request: string
  owner: object
  session: string
  budget: QueryMainReadBudget
  accepted?: JobView
  unknown: boolean
}

type MainlineRecoveryHandle = {
  client: MainlineProjectTransport
  token: object
  projectId: string
  epoch: number
}

/** Named main-only application service. No generic renderer invoke or issuer DTO. */
export class ProjectMainlineService implements MainlineProjectBridge {
  readonly source = new MainlineProjectSource((fence) => {
    this.#invalidateRecovery()
    try {
      fence() // Revoke issuer before clearProject can notify any view/observer.
      if (!this.#closed) this.tasks.clearProject()
    } catch (cause) {
      this.#retireRecoveryPending()
      throw cause
    }
    const failure = this.#retireRecoveryPending()
    if (failure) throw failure
  })
  readonly queries: QueryDefinitionService
  #projectedErrors = new WeakSet<EngineError>()
  #closed = false
  #busy = false
  #connectionRelease: () => void
  #projectRelease: () => void
  #recoveryRelease: () => void
  #selectionEpoch = 0
  #recoveryPrincipal?: MainlineRecoveryHandle
  #retiredRecovery = new Set<MainlineRecoveryHandle>()
  #intents = new Map<string, MainlineIntent>()
  constructor(
    readonly supervisor: EngineSupervisor,
    readonly tasks: TaskService,
    private readonly reattachView: () => void,
  ) {
    if (supervisor.profile !== 'business3') throw denied()
    this.queries = new QueryDefinitionService(this.source, tasks)
    // Installed before any connection event or recovery microtask can occur.
    this.#recoveryRelease = tasks.installMainlineRecovery(supervisor, {
      run: (context, restore) => this.#recover(context, restore),
    })
    this.#connectionRelease = supervisor.onConnectionState((state) => {
      const current = this.source.current()
      if (
        current &&
        (state.state === 'disconnected' || state.engineSessionId !== current.engineSessionId)
      ) {
        // Revoke old source/issuer immediately, but retain TaskService's P/J
        // recovery responsibility. User clear/select is a different operation.
        this.source.fence()
      }
    })
    this.#projectRelease = tasks.observeActiveProject((project, session) => {
      if (project && session) this.source.observeProject(project, supervisor, session)
    })
  }
  #invalidateRecovery(): void {
    const principal = this.#recoveryPrincipal
    // Revoke first. Keep the original owner/token handle until Engine reports
    // actual completion; dropping a field or timing out cannot release it.
    this.#recoveryPrincipal = undefined
    if (principal) this.#retiredRecovery.add(principal)
    if (this.#selectionEpoch >= Number.MAX_SAFE_INTEGER) throw invalid()
    this.#selectionEpoch++
  }
  #retireRecoveryPending(): unknown {
    let firstFailure: unknown
    // At most16 handles: issuance refuses another principal at that bound.
    // Engine cleanup has no observer callbacks; deletion cannot hide a pending
    // or failed handle, and a repeated dispose can retry the exact same entry.
    for (const principal of this.#retiredRecovery) {
      try {
        if (this.supervisor.retireMainlineRecovery(principal.client, principal.token))
          this.#retiredRecovery.delete(principal)
      } catch (cause) {
        firstFailure ??= cause
      }
    }
    return firstFailure
  }
  #recover(
    context: TaskRecoveryContext,
    restore: (request: TaskRecoveryRequest) => Promise<BridgeResult<TaskView>>,
  ): Promise<BridgeResult<TaskView>> {
    const principal = this.#recoveryPrincipal
    const current = () =>
      !this.#closed &&
      !this.#busy &&
      this.#recoveryPrincipal === principal &&
      this.#selectionEpoch === principal?.epoch &&
      context.isCurrent()
    if (!principal || context.projectId !== principal.projectId || !current()) throw denied()
    let publish: (() => void) | undefined
    let restored: BridgeResult<TaskView> | undefined
    // Return the original Engine operation promise. TaskService can project an
    // authentic startup/business failure against its actual originating promise.
    const operation = this.supervisor.runMainlineRecovery(
      principal.token,
      current,
      async (client, request) => {
        if (!current()) throw denied()
        const result = await restore(request)
        if (!current()) throw denied()
        if (result.ok) {
          const project = result.data.project
          if (
            !project ||
            project.projectId !== principal.projectId ||
            result.data.generation !== context.generation ||
            !client.engineSessionId ||
            client.engineSessionId !== this.supervisor.engineSessionId
          )
            throw denied()
          // Actual project.get response brand, not a caller DTO or old snapshot.
          client.acceptProject(project)
          publish = this.source.preparePublication(client, current)
        }
        restored = result
        return result
      },
      (view) => {
        if (!current() || !publish || !restored?.ok || restored.data !== view) throw denied()
        // Engine has completed/consumed the real background reply. Its selected
        // alias and restored view, and this source's staged selection, remain held.
        publish()
        if (!current()) throw denied()
      },
    )
    // This observes the real operation's settlement without wrapping/replacing
    // its error-provenance identity or masking its first rejection.
    void operation.then(
      () => {
        this.#retireRecoveryPending()
      },
      () => {
        this.#retireRecoveryPending()
      },
    )
    return operation
  }
  #client(): MainlineProjectTransport {
    if (this.#closed) throw denied()
    const client = this.supervisor.mainlineProjectClient()
    if (!client) throw denied()
    return client
  }
  #current(): NonNullable<OrdinaryCurrent> {
    const current = this.source.current()
    if (!current || this.#closed || current.engineSessionId !== this.supervisor.engineSessionId)
      throw denied()
    return current
  }
  #operationError(cause: unknown, operation: Promise<unknown>): EngineError {
    const error = new EngineError(this.supervisor.projectFailure(cause, operation))
    this.#projectedErrors.add(error)
    return error
  }
  async #run<T>(work: () => Promise<T>): Promise<BridgeResult<T>> {
    try {
      return { ok: true, data: await work() }
    } catch (cause) {
      return {
        ok: false,
        error:
          cause instanceof EngineError && this.#projectedErrors.has(cause)
            ? safeDisplayError(cause.error)
            : safeError(cause instanceof EngineError ? cause.error : undefined),
      }
    }
  }
  async #call<T>(
    client: MainlineProjectTransport,
    method: MainlineMethod,
    params: RecordValue,
  ): Promise<T> {
    const operation = client.request(method, params)
    try {
      return (await operation) as T
    } catch (cause) {
      throw this.#operationError(cause, operation)
    }
  }
  getProjectCatalog(args: {
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<MainlineCatalog>> {
    return this.#run(() => this.#call<MainlineCatalog>(this.#client(), 'project.catalog', args))
  }
  async #selection<T>(
    work: (client: MainlineProjectTransport, current: () => boolean) => Promise<T>,
  ): Promise<T> {
    if (this.#busy || this.#closed) throw invalid()
    this.#busy = true
    try {
      this.#invalidateRecovery()
      const epoch = this.#selectionEpoch
      const current = () => !this.#closed && this.#selectionEpoch === epoch
      this.source.fence()
      this.tasks.clearProject()
      const failure = this.#retireRecoveryPending()
      if (failure) throw failure
      if (!current()) throw denied()
      return await work(this.#client(), current)
    } finally {
      this.#busy = false
    }
  }
  #publish(client: MainlineProjectTransport, current: () => boolean): void {
    if (
      !current() ||
      !client.selected ||
      client.engineSessionId !== this.supervisor.engineSessionId
    )
      throw denied()
    this.tasks.selectProject(client.selected.projectId)
    this.reattachView() // Real window attachment is supplied by main; no fake sink.
    if (!current()) throw denied()
    const failure = this.#retireRecoveryPending()
    if (failure) throw failure
    if (this.#retiredRecovery.size >= 16) throw invalid()
    const epoch = this.#selectionEpoch
    const token: object = this.supervisor.issueMainlineRecovery(
      client,
      () =>
        !this.#closed && this.#selectionEpoch === epoch && this.#recoveryPrincipal?.token === token,
    )
    this.#recoveryPrincipal = { client, token, projectId: client.selected.projectId, epoch }
    this.source.publish(client)
    if (!current()) throw denied()
  }
  createBlankProject(args: CreateArgs): Promise<BridgeResult<MainlineCreate>> {
    return this.#run(() =>
      this.#selection(async (client) => {
        const result = await this.#call<MainlineCreate>(client, 'project.create', args)
        if (
          result.operationId !== args.operationId ||
          result.receipt.operationId !== args.operationId ||
          result.projectId !== result.receipt.projectId ||
          result.requestHash !== createHash('sha256').update(stable(args), 'utf8').digest('hex')
        )
          throw invalid()
        return result
      }),
    )
  }
  createExampleProject(
    args: MainlineExampleCreateRequestDTO,
  ): Promise<BridgeResult<MainlineExampleCreateResultDTO>> {
    return this.#run(() =>
      this.#selection(async (client) => {
        const result = await this.#call<MainlineExampleCreateResultDTO>(
          client,
          'project.example.create',
          args,
        )
        if (
          result.operationId !== args.operationId ||
          result.receipt.operationId !== args.operationId ||
          result.projectId !== result.receipt.projectId ||
          result.receipt.exampleId !== args.exampleId ||
          result.receipt.inputDigest !== args.inputDigest ||
          result.requestHash !== createHash('sha256').update(stable(args), 'utf8').digest('hex')
        )
          throw invalid()
        return result
      }),
    )
  }
  openProject(args: { projectId: string }): Promise<BridgeResult<ProjectView>> {
    return this.#run(() =>
      this.#selection(async (client, current) => {
        const result = await this.#call<ProjectView>(client, 'project.open', args)
        this.#publish(client, current)
        return result
      }),
    )
  }
  saveProjectDraft(args: MainlineDraftSaveArgs): Promise<BridgeResult<MainlineDraftSaveResultDTO>> {
    return this.#run(async () => {
      const current = this.#current(),
        client = this.#client()
      if (client.owner !== current.owner) throw denied()
      const result = await this.#call<MainlineDraftSaveResultDTO>(client, 'project.draft.save', {
        ...args,
        projectId: current.project.projectId,
      })
      if (
        result.projectId !== current.project.projectId ||
        result.operationId !== args.operationId ||
        result.editor !== args.editor ||
        result.generation !== args.expectedGeneration + 1 ||
        result.boundDomainRevision !== args.boundDomainRevision ||
        result.contentHash !== createHash('sha256').update(args.contentJson, 'utf8').digest('hex')
      )
        throw invalid()
      // Preserve an actual durable receipt even if the user switched views while
      // awaiting it. No result is published into the replacement editor.
      return result
    })
  }
  readProject(args: { editor: string }): Promise<BridgeResult<MainlineRead>> {
    return this.#run(async () => {
      const current = this.#current(),
        client = this.#client()
      if (client.owner !== current.owner) throw denied()
      const result = await this.#call<MainlineRead>(client, 'project.read', {
        ...args,
        projectId: current.project.projectId,
      })
      if (
        this.source.current()?.owner !== current.owner ||
        client.engineSessionId !== current.engineSessionId
      )
        throw denied()
      // Same selected owner: refresh the projection without selectProject/resetting Jobs.
      this.source.publish(client)
      return result
    })
  }
  async #selectedCall<T>(method: string, params: RecordValue): Promise<T> {
    const current = this.#current(),
      budget = this.supervisor.queryReadBudget(current.owner)
    const finish = budget.beginConsumerRequest()
    try {
      budget.beforeArguments(params)
      const pin = this.supervisor.issueQueryPin(
        current.owner,
        current.engineSessionId,
        () => this.source.current() === current,
      )
      const operation = this.supervisor.requestPinned(
        method,
        { ...params, projectId: current.project.projectId },
        pin,
      )
      let value: T
      try {
        value = (await operation) as T
      } catch (cause) {
        throw this.#operationError(cause, operation)
      }
      if (this.source.current() !== current) throw denied()
      budget.handoff(value)
      return value
    } finally {
      finish()
    }
  }
  previewProjectChangeset(args: MainlinePreviewArgs): Promise<BridgeResult<ChangeSetPreview>> {
    return this.#run(() => this.#selectedCall('changeset.preview', args))
  }
  getProjectDiffPage(args: {
    previewHash: string
    documentKind: 'diff' | 'undo-impact'
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<ChangeSetPage>> {
    return this.#run(() => this.#selectedCall('changeset.diff.page', args))
  }
  confirmProjectChangeset(args: {
    previewHash: string
    completionCursor: string
  }): Promise<BridgeResult<ChangeSetConfirmation>> {
    return this.#run(() => this.#selectedCall('changeset.confirm', args))
  }
  #keepIntent(intent: MainlineIntent, accepted = intent.accepted): void {
    intent.budget.retainHolding(intent, {
      request: intent.request,
      engineSessionId: intent.session,
      ...(accepted ? { accepted } : {}),
    })
    intent.accepted = accepted
  }
  commitProjectChangeSet(args: {
    operationId: string
    confirmation: ChangeSetConfirmation
  }): Promise<BridgeResult<JobView>> {
    return this.#run(async () => {
      const current = this.#current(),
        confirmation = args.confirmation
      if (
        confirmation.projectId !== current.project.projectId ||
        !validateBusiness3('result_changeset.confirm', confirmation)
      )
        throw invalid()
      const request = {
        operationId: args.operationId,
        capability: 'changeset.commit',
        confirmationRef: confirmation.confirmationRef,
        input: {
          inputSnapshotId: confirmation.inputSnapshotId,
          scope: 'asserted',
          definitionId: 'changeset',
          parametersHash: confirmation.parametersHash,
          derivedResultIds: [],
          preparedPlanRef: confirmation.preparedPlanRef,
        },
      }
      const fingerprint = stable({ projectId: current.project.projectId, ...request })
      let intent = this.#intents.get(args.operationId)
      if (
        intent &&
        (intent.request !== fingerprint ||
          intent.owner !== current.owner ||
          intent.session !== current.engineSessionId)
      )
        throw invalid()
      if (!intent) {
        if (this.#intents.size >= 16) throw invalid()
        intent = {
          request: fingerprint,
          owner: current.owner,
          session: current.engineSessionId,
          budget: this.supervisor.queryReadBudget(current.owner),
          unknown: false,
        }
        this.#keepIntent(intent)
        this.#intents.set(args.operationId, intent)
      }
      if (intent.accepted) return intent.accepted
      if (intent.unknown) throw denied() // No automatic replay of an entered write.
      intent.unknown = true
      const budget = this.supervisor.queryReadBudget(current.owner),
        finish = budget.beginConsumerRequest()
      try {
        budget.beforeArguments(request)
        const pin = this.supervisor.issueQueryPin(
          current.owner,
          current.engineSessionId,
          () => this.source.current() === current,
        )
        const operation = this.supervisor.requestPinned(
          'job.create',
          { ...request, projectId: current.project.projectId },
          pin,
        )
        let accepted: JobView
        try {
          accepted = (await operation) as JobView
        } catch (cause) {
          intent.unknown = this.supervisor.queryWriteEntered(pin)
          throw this.#operationError(cause, operation)
        }
        if (
          !validateBusiness3('job', accepted) ||
          accepted.operationId !== args.operationId ||
          accepted.projectId !== current.project.projectId ||
          accepted.capability !== 'changeset.commit' ||
          stable(accepted.input) !== stable(request.input)
        )
          throw invalid()
        this.#keepIntent(intent, accepted)
        intent.unknown = false
        budget.handoff(accepted)
        if (this.source.current() !== current) throw denied()
        // The real accepted Job is returned even when later view subscription fails.
        void this.tasks.subscribeJob(accepted.jobId).catch(() => {})
        return accepted
      } finally {
        finish()
      }
    })
  }
  dispose(): void {
    if (this.#closed) {
      this.#retireRecoveryPending()
      return
    }
    this.#closed = true
    this.#invalidateRecovery()
    this.#recoveryRelease()
    this.#connectionRelease()
    this.#projectRelease()
    this.queries.dispose()
    void this.source.dispose().catch(() => {
      // The original handles remain in #retiredRecovery. A failed cleanup does
      // not make disposal proof of release or erase a preceding operation error.
    })
    this.#retireRecoveryPending()
  }
}
