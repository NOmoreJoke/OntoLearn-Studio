import { createHash } from 'node:crypto'
import { performance } from 'node:perf_hooks'
import { setTimeout as delay } from 'node:timers/promises'
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
  type OwnershipDetailArgs,
  type OwnershipDetailPage,
  type ProjectCheckpointBridge,
  type ProjectManagementBridge,
  type LearningLedgerBridge,
  type ProjectLearningReadDTO,
  type ProjectLearningAttemptStartDTO,
  type ProjectLearningHintRecordDTO,
  type ProjectLearningObservationRecordDTO,
  type ProjectLearningTaskCheckDTO,
  type ProjectQualityCheckArgs,
  type ProjectQualityPrepareDTO,
  type ProjectQualityReadArgs,
  type ProjectQualityReadDTO,
  type QualityJobInputDTO,
  type QualityRunReceiptDTO,
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
import { ProjectManagementSession } from './project-management-session'
import { ProjectRestoreSession } from './project-restore-session'
import type { TaskService, TaskRecoveryContext, TaskRecoveryRequest } from './task-service'

type RecordValue = Record<string, unknown>
type QualityMethod = 'project.quality.read' | 'project.quality.prepare'
type QualityCapability = ProjectQualityPrepareDTO['chain'][number]
type QualityRequest = (method: string, params: RecordValue) => Promise<unknown>

function qualityOperationId(operationId: string, suffix: string): string {
  const hex = createHash('sha256').update(`${operationId}:${suffix}`).digest('hex')
  const variant = ((Number.parseInt(hex[16]!, 16) & 0x3) | 0x8).toString(16)
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-4${hex.slice(13, 16)}-${variant}${hex.slice(17, 20)}-${hex.slice(20, 32)}`
}

function qualityParams(
  args: ProjectQualityCheckArgs,
  defaultScope?: 'asserted+derived',
): RecordValue {
  const { constraintId, validationScope = defaultScope, ...params } = args
  return {
    ...params,
    ...(constraintId === undefined ? {} : { constraintId }),
    ...(validationScope === undefined ? {} : { validationScope }),
  }
}
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
  operationId: string
  request: string
  owner: object
  session: string
  budget: QueryMainReadBudget
  accepted?: JobView
  jobId?: string
  payloadEntry: object
  pendingReplies: Set<object>
  active: number
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
  #fullIntents = new Set<MainlineIntent>()
  #management: ProjectManagementSession
  #restore: ProjectRestoreSession
  constructor(
    readonly supervisor: EngineSupervisor,
    readonly tasks: TaskService,
    private readonly reattachView: () => void,
    options: { managementJournalPath?: string; restoreJournalPath?: string } = {},
  ) {
    if (supervisor.profile !== 'business3') throw denied()
    this.queries = new QueryDefinitionService(this.source, tasks)
    this.#management = new ProjectManagementSession({
      client: () => this.#client(),
      selection: () => {
        const current = this.source.current()
        return current
          ? {
              projectId: current.project.projectId,
              owner: current.owner,
              session: current.engineSessionId,
              epoch: this.#selectionEpoch,
            }
          : null
      },
      epoch: () => this.#selectionEpoch,
      call: (client, method, params) => this.#call(client, method, params),
      retireSelection: (projectId, epoch) => {
        if (
          this.#selectionEpoch === epoch &&
          this.source.current()?.project.projectId === projectId
        )
          void this.source.closeSelection().catch(() => {})
      },
      hasOtherUnresolvedResponsibility: () =>
        this.#otherResponsibilities() || this.supervisor.hasOtherMainlineResponsibility,
      journalPath: options.managementJournalPath,
    })
    this.#restore = new ProjectRestoreSession({
      client: () => this.#client(),
      selection: () => {
        const current = this.source.current()
        return current
          ? {
              projectId: current.project.projectId,
              owner: current.owner,
              session: current.engineSessionId,
              epoch: this.#selectionEpoch,
            }
          : null
      },
      epoch: () => this.#selectionEpoch,
      call: (client, method, params) => this.#call(client, method, params),
      hasOtherUnresolvedResponsibility: () =>
        this.#otherResponsibilities() ||
        this.#management.hasUnresolvedResponsibility ||
        this.supervisor.hasOtherMainlineResponsibility,
      journalPath: options.restoreJournalPath,
    })
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
  #otherResponsibilities(): boolean {
    return (
      this.#busy ||
      this.#retiredRecovery.size > 0 ||
      this.queries.hasOutstanding ||
      [...this.#fullIntents].some(
        (intent) => intent.active > 0 || intent.unknown || intent.pendingReplies.size > 0,
      )
    )
  }
  get hasUnresolvedResponsibility(): boolean {
    return (
      this.#otherResponsibilities() ||
      this.#management.hasUnresolvedResponsibility ||
      this.#restore.hasUnresolvedResponsibility
    )
  }
  get managementBlocked(): boolean {
    return this.#management.hasUnresolvedResponsibility
  }
  get restoreBlocked(): boolean {
    return this.#restore.hasUnresolvedResponsibility
  }
  getPendingProjectManagementOperations() {
    return this.#run(() => this.#management.pending())
  }
  getProjectManagementCatalog(
    args: Parameters<ProjectManagementBridge['getProjectManagementCatalog']>[0],
  ) {
    return this.#run(() => this.#management.catalog(args))
  }
  getProjectManagementState() {
    return this.#run(() => this.#management.state())
  }
  previewProjectManagement(
    args: Parameters<ProjectManagementBridge['previewProjectManagement']>[0],
  ) {
    return this.#run(() => this.#management.preview(args))
  }
  confirmProjectManagement(
    args: Parameters<ProjectManagementBridge['confirmProjectManagement']>[0],
  ) {
    return this.#run(() => this.#management.confirm(args))
  }
  applyProjectManagement(args: Parameters<ProjectManagementBridge['applyProjectManagement']>[0]) {
    return this.#run(() => this.#management.apply(args))
  }
  getProjectManagementOperation(
    args: Parameters<ProjectManagementBridge['getProjectManagementOperation']>[0],
  ) {
    return this.#run(() => this.#management.operation(args))
  }
  listProjectCheckpoints(args: Parameters<ProjectCheckpointBridge['listProjectCheckpoints']>[0]) {
    return this.#run(() => this.#restore.list(args))
  }
  createProjectCheckpoint(args: Parameters<ProjectCheckpointBridge['createProjectCheckpoint']>[0]) {
    return this.#run(() => this.#restore.create(args))
  }
  getPendingProjectRestoreOperations() {
    return this.#run(() => this.#restore.pending())
  }
  previewProjectRestore(args: Parameters<ProjectCheckpointBridge['previewProjectRestore']>[0]) {
    return this.#run(() => this.#restore.preview(args))
  }
  getProjectRestorePage(args: Parameters<ProjectCheckpointBridge['getProjectRestorePage']>[0]) {
    return this.#run(() => this.#restore.page(args))
  }
  confirmProjectRestore(args: Parameters<ProjectCheckpointBridge['confirmProjectRestore']>[0]) {
    return this.#run(() => this.#restore.confirm(args))
  }
  restoreProject(args: Parameters<ProjectCheckpointBridge['restoreProject']>[0]) {
    return this.#run(() => this.#restore.apply(args))
  }
  getProjectRestoreOperation(
    args: Parameters<ProjectCheckpointBridge['getProjectRestoreOperation']>[0],
  ) {
    return this.#run(() => this.#restore.operation(args))
  }
  getProjectLearningState(args: Parameters<LearningLedgerBridge['getProjectLearningState']>[0]) {
    return this.#run(() => this.#learning<ProjectLearningReadDTO>('project.learning.read', args))
  }
  startLearningAttempt(args: Parameters<LearningLedgerBridge['startLearningAttempt']>[0]) {
    return this.#run(() =>
      this.#learning<ProjectLearningAttemptStartDTO>('project.learning.attempt.start', args),
    )
  }
  recordLearningHint(args: Parameters<LearningLedgerBridge['recordLearningHint']>[0]) {
    return this.#run(() =>
      this.#learning<ProjectLearningHintRecordDTO>('project.learning.hint.record', args),
    )
  }
  recordLearningObservation(
    args: Parameters<LearningLedgerBridge['recordLearningObservation']>[0],
  ) {
    return this.#run(() =>
      this.#learning<ProjectLearningObservationRecordDTO>(
        'project.learning.observation.record',
        args,
      ),
    )
  }
  checkLearningTask(args: Parameters<LearningLedgerBridge['checkLearningTask']>[0]) {
    return this.#run(() => {
      const { selectedOrigins, ...params } = args
      return this.#learning<ProjectLearningTaskCheckDTO>('project.learning.task.check', {
        ...params,
        ...(selectedOrigins === undefined ? {} : { selectedOrigins }),
      })
    })
  }
  /** Learning ledger calls stay behind the selected-project/session guards;
   *  params and results are validated against the pinned business3 schemas. */
  async #learning<T>(method: MainlineMethod, args: RecordValue): Promise<T> {
    const current = this.#current()
    const client = this.#client()
    const params: RecordValue = { ...args, projectId: current.project.projectId }
    if (!validateBusiness3('params_' + method, params)) throw invalid()
    const value = (await this.#call<RecordValue>(client, method, params)) as RecordValue
    if (!validateBusiness3('result_' + method, value)) throw invalid()
    if (value.projectId !== params.projectId) throw invalid()
    if (
      method !== 'project.learning.read' &&
      (value.operationId !== params.operationId || value.taskId !== params.taskId)
    )
      throw invalid()
    return value as T
  }
  #qualitySelection(
    current: NonNullable<OrdinaryCurrent>,
    client: MainlineProjectTransport,
  ): () => boolean {
    const epoch = this.#selectionEpoch
    return () =>
      this.#selectionEpoch === epoch &&
      this.source.current() === current &&
      this.#current() === current &&
      client.owner === current.owner &&
      client.engineSessionId === current.engineSessionId
  }
  async #qualityRequest<T extends ProjectQualityReadDTO | ProjectQualityPrepareDTO>(
    method: QualityMethod,
    params: RecordValue,
    current: NonNullable<OrdinaryCurrent>,
    guard: () => boolean,
    request: QualityRequest,
  ): Promise<T> {
    if (!guard() || params.projectId !== current.project.projectId) throw denied()
    if (!validateBusiness3('params_' + method, params)) throw invalid()
    const value = (await request(method, params)) as T
    if (!guard()) throw denied()
    if (
      !validateBusiness3('result_' + method, value) ||
      value.projectId !== params.projectId ||
      (method === 'project.quality.prepare' &&
        (!('operationId' in value) ||
          value.operationId !== params.operationId ||
          value.chain[0] !== 'reasoning.execute' ||
          value.chain[1] !== 'validation.execute'))
    )
      throw invalid()
    return value
  }
  getProjectQualityState(
    args: ProjectQualityReadArgs,
  ): Promise<BridgeResult<ProjectQualityReadDTO>> {
    return this.#run(() => {
      const current = this.#current()
      const client = this.#client()
      return this.#qualityRequest<ProjectQualityReadDTO>(
        'project.quality.read',
        args,
        current,
        this.#qualitySelection(current, client),
        (method, params) => this.#call(client, method as QualityMethod, params),
      )
    })
  }
  prepareProjectQualityCheck(
    args: ProjectQualityCheckArgs,
  ): Promise<BridgeResult<ProjectQualityPrepareDTO>> {
    return this.#run(() => {
      const current = this.#current()
      const client = this.#client()
      return this.#qualityRequest<ProjectQualityPrepareDTO>(
        'project.quality.prepare',
        qualityParams(args),
        current,
        this.#qualitySelection(current, client),
        (method, params) => this.#call(client, method as QualityMethod, params),
      )
    })
  }
  async #qualityJob(
    request: QualityRequest,
    args: {
      projectId: string
      operationId: string
      capability: QualityCapability
      input: QualityJobInputDTO
    },
    totalMs: number,
  ): Promise<JobView> {
    const params = { ...args, confirmationRef: null }
    if (!validateBusiness3('params_job.create', params)) throw invalid()
    const matches = (value: unknown): value is JobView => {
      if (!validateBusiness3('job', value)) return false
      const job = value as JobView
      return (
        job.projectId === args.projectId &&
        job.operationId === args.operationId &&
        job.capability === args.capability &&
        job.confirmationRef === null &&
        stable(job.input) === stable(args.input)
      )
    }
    const accepted = await request('job.create', params)
    if (!matches(accepted)) throw invalid()
    const deadline = performance.now() + totalMs
    let interval = 100
    let latest = accepted
    while (true) {
      const job = await request('job.get', { projectId: args.projectId, jobId: accepted.jobId })
      if (
        !matches(job) ||
        job.jobId !== accepted.jobId ||
        job.stateVersion < latest.stateVersion ||
        (job.stateVersion === latest.stateVersion && job.state !== latest.state)
      )
        throw invalid()
      if (job.state === 'succeeded' || job.state === 'failed' || job.state === 'cancelled')
        return job
      latest = job
      const remaining = deadline - performance.now()
      if (remaining <= 0)
        throw new EngineError({
          code: 'TIMEOUT',
          messageKey: 'job.timeout',
          params: { phase: 'total' },
          retryable: true,
        })
      await delay(Math.min(interval, remaining))
      interval = Math.min(interval * 2, 1000)
    }
  }
  runProjectQualityCheck(
    args: ProjectQualityCheckArgs,
  ): Promise<BridgeResult<QualityRunReceiptDTO>> {
    return this.#run(async () => {
      const current = this.#current()
      const client = this.#client()
      const guard = this.#qualitySelection(current, client)
      if (!guard() || args.projectId !== current.project.projectId) throw denied()
      const budget = this.supervisor.queryReadBudget(current.owner)
      const finish = budget.beginConsumerRequest()
      try {
        const params = qualityParams(args, 'asserted+derived')
        budget.beforeArguments(params)
        const request: QualityRequest = async (method, input) => {
          if (!guard()) throw denied()
          const pin = this.supervisor.issueQueryPin(current.owner, current.engineSessionId, guard)
          const operation = this.supervisor.requestPinned(method, input, pin)
          try {
            const value = await operation
            if (!guard()) throw denied()
            return value
          } catch (cause) {
            if (!guard()) throw denied()
            throw this.#operationError(cause, operation)
          }
        }
        const prepared = await this.#qualityRequest<ProjectQualityPrepareDTO>(
          'project.quality.prepare',
          params,
          current,
          guard,
          request,
        )
        const { projectId, operationId } = prepared
        const totalMs = prepared.executionIdentity.limits.totalMs!
        const reasoningJob = await this.#qualityJob(
          request,
          {
            projectId,
            operationId: qualityOperationId(operationId, 'reasoning'),
            capability: 'reasoning.execute',
            input: prepared.reasoningInput,
          },
          totalMs,
        )
        const validationJobs: JobView[] = []
        if (reasoningJob.state === 'succeeded') {
          const resultId = reasoningJob.resultRef?.resultId
          for (const [index, input] of prepared.validationInputs.entries()) {
            validationJobs.push(
              await this.#qualityJob(
                request,
                {
                  projectId,
                  operationId: qualityOperationId(operationId, `validation:${index}`),
                  capability: 'validation.execute',
                  input: {
                    ...input,
                    derivedResultIds:
                      input.scope === 'asserted+derived' && resultId ? [resultId] : [],
                  },
                },
                totalMs,
              ),
            )
          }
        }
        const qualityState = await this.#qualityRequest<ProjectQualityReadDTO>(
          'project.quality.read',
          { projectId },
          current,
          guard,
          request,
        )
        const receipt: QualityRunReceiptDTO = {
          qualityRunVersion: 1,
          projectId,
          operationId,
          reasoningJob,
          validationJobs,
          qualityState,
        }
        budget.handoff(receipt)
        return receipt
      } finally {
        finish()
      }
    })
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
    if (
      !current ||
      this.#closed ||
      this.#management.hasUnresolvedResponsibility ||
      this.#restore.hasUnresolvedResponsibility ||
      current.engineSessionId !== this.supervisor.engineSessionId
    )
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
      const value = (await operation) as T
      if (String(method) === 'project.restore.confirm')
        console.log('confirm-transport-ok', JSON.stringify(value).slice(0, 120))
      return value
    } catch (cause) {
      if (String(method).startsWith('project.restore.'))
        console.log('restore-transport-threw', method, String(cause).slice(0, 240))
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
    if (
      this.#busy ||
      this.#closed ||
      this.#management.hasUnresolvedResponsibility ||
      this.#restore.hasUnresolvedResponsibility
    )
      throw invalid()
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
  getOwnershipConflictDetailPage(
    args: OwnershipDetailArgs,
  ): Promise<BridgeResult<OwnershipDetailPage>> {
    return this.#run(async () => {
      const current = this.#current(),
        client = this.#client(),
        epoch = this.#selectionEpoch
      if (client.owner !== current.owner) throw denied()
      const result = await this.#call<OwnershipDetailPage>(client, 'project.ownership.detail', {
        ...args,
        projectId: current.project.projectId,
      })
      if (
        this.#selectionEpoch !== epoch ||
        this.source.current()?.owner !== current.owner ||
        this.source.current()?.project.projectId !== current.project.projectId ||
        client.engineSessionId !== current.engineSessionId
      )
        throw denied()
      return result // Never publish a workspace, selection or snapshot projection.
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
    // The compact identity (including the Map key and original binding) is
    // prepaid separately and never FIFO-forgotten. Existing global hard budgets
    // still bound its lifetime storage, including after payload retirement.
    intent.budget.retainHolding(intent, {
      operationId: intent.operationId,
      request: intent.request,
      engineSessionId: intent.session,
      jobId: accepted?.jobId ?? intent.jobId ?? null,
    })
    if (accepted) {
      intent.budget.retainHolding(intent.payloadEntry, accepted)
      intent.accepted = accepted
      intent.jobId = accepted.jobId
    }
  }
  #offerIntent(intent: MainlineIntent): JobView {
    if (!intent.accepted || intent.unknown) throw denied()
    const pending = Object.freeze({})
    intent.budget.onReplyConsumed(intent.payloadEntry, () => {
      if (!intent.pendingReplies.has(pending)) throw invalid()
      if (intent.pendingReplies.size > 1) {
        intent.pendingReplies.delete(pending)
        return
      }
      if (intent.active !== 0 || intent.unknown || !intent.accepted) throw invalid()
      const accepted = intent.accepted
      intent.accepted = undefined
      try {
        intent.budget.releaseHolding(intent.payloadEntry)
      } catch (cause) {
        intent.accepted = accepted
        throw cause
      }
      intent.pendingReplies.delete(pending)
      this.#fullIntents.delete(intent)
    })
    intent.pendingReplies.add(pending)
    return intent.accepted
  }
  async #readAcceptedIntent(
    intent: MainlineIntent,
    current: NonNullable<OrdinaryCurrent>,
    request: RecordValue,
  ): Promise<JobView> {
    const budget = intent.budget,
      finish = budget.beginConsumerRequest()
    try {
      const params = { projectId: current.project.projectId, jobId: intent.jobId }
      budget.beforeArguments(params)
      const pin = this.supervisor.issueQueryPin(
        current.owner,
        current.engineSessionId,
        () => this.source.current() === current,
      )
      const operation = this.supervisor.requestPinned('job.get', params, pin)
      let job: JobView
      try {
        job = (await operation) as JobView
      } catch (cause) {
        throw this.#operationError(cause, operation)
      }
      if (
        !validateBusiness3('job', job) ||
        job.jobId !== intent.jobId ||
        job.projectId !== current.project.projectId ||
        job.operationId !== intent.operationId ||
        job.capability !== request.capability ||
        job.confirmationRef !== request.confirmationRef ||
        stable(job.input) !== stable(request.input)
      )
        throw invalid()
      if (this.source.current() !== current) throw denied()
      budget.handoff(job)
      return job
    } finally {
      finish()
    }
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
        if (this.#fullIntents.size >= 16) throw invalid()
        intent = {
          operationId: args.operationId,
          request: fingerprint,
          owner: current.owner,
          session: current.engineSessionId,
          budget: this.supervisor.queryReadBudget(current.owner),
          payloadEntry: Object.freeze({}),
          pendingReplies: new Set(),
          active: 0,
          unknown: false,
        }
        this.#keepIntent(intent)
        this.#intents.set(args.operationId, intent)
        this.#fullIntents.add(intent)
      }
      if (intent.unknown) throw denied() // No automatic replay of an entered write.
      intent.active++
      try {
        if (intent.accepted) return this.#offerIntent(intent)
        if (intent.jobId) return await this.#readAcceptedIntent(intent, current, request)
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
          return this.#offerIntent(intent)
        } finally {
          finish()
        }
      } finally {
        intent.active--
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
    this.#management.dispose()
    this.#restore.dispose()
    void this.source.dispose().catch(() => {
      // The original handles remain in #retiredRecovery. A failed cleanup does
      // not make disposal proof of release or erase a preceding operation error.
    })
    this.#retireRecoveryPending()
  }
}
