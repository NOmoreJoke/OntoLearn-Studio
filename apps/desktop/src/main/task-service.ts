import { z } from 'zod'
import {
  safeError,
  safeDisplayError,
  type BridgeResult,
  type JobListOptions,
  type JobView,
  type ProjectView,
  type ProgressView,
  type ResultPageOptions,
  type ResultMetadataDTO,
  type ResultPageDTO,
  type TaskUpdate,
  type TaskView,
  type SafeError,
} from '@ontolearn/contracts'
import {
  acceptsJobEvent,
  acceptsBusiness3JobEvent,
  validateBusiness3,
  validateV2,
  type EventBinding,
} from '../../../../packages/contracts/src/v2'
import { EngineError, EngineSupervisor, type EngineConnectionState } from './engine'

interface TaskEngine {
  request(method: string, params: Record<string, unknown>): Promise<unknown>
  readonly engineSessionId: string | undefined
  onNotification(listener: (event: unknown) => void): () => void
  onConnectionState(listener: (event: EngineConnectionState) => void): () => void
}
const id = z.string().uuid()
const denied = {
  code: 'PERMISSION_DENIED',
  messageKey: 'permission.denied',
  params: {},
  retryable: false,
}
const invalid = {
  code: 'INVALID_REQUEST',
  messageKey: 'protocol.invalidRequest',
  params: { field: 'params' },
  retryable: false,
}
/** Main-only seam, installed synchronously by the production project owner.
 * A context is an actual attempt, never a renderer-supplied grant or project DTO.
 */
export interface TaskRecoveryContext {
  readonly projectId: string
  readonly generation: number
  isCurrent(): boolean
}
export type TaskRecoveryRequest = (
  method: string,
  params: Record<string, unknown>,
) => Promise<unknown>
export interface TaskMainlineRecovery {
  run(
    context: TaskRecoveryContext,
    restore: (request: TaskRecoveryRequest) => Promise<BridgeResult<TaskView>>,
  ): Promise<BridgeResult<TaskView>>
}
interface Recovery {
  projectId: string
  generation: number
  attempt: number
  cancelled: boolean
  error: SafeError
  promise?: Promise<BridgeResult<TaskView>>
  wake?: () => void
  attemptToken?: object
  scope?: { token: object; request: TaskRecoveryRequest; current: () => boolean }
}
interface Watch {
  binding: EventBinding
  job: JobView
}

// This disposable cache holds view context only. All state and commit evidence is re-read from SQLite.
interface AuthenticatedFailure {
  value: SafeError
  generation: number
  projectId: string | null
  recoveryRefusal?: boolean
}
export class TaskService {
  #supervisor?: EngineSupervisor
  #caught = new WeakMap<object, AuthenticatedFailure>()
  #outcomes = new WeakMap<
    object,
    { context: AuthenticatedFailure; promises: WeakSet<Promise<unknown>> }
  >()
  private validate(name: string, value: unknown): boolean {
    return this.#supervisor?.profile === 'business3'
      ? validateBusiness3(name, value)
      : validateV2(name, value)
  }
  private projectId: string | null = null
  private generation = 0
  private projectRevision: number | undefined
  private lastProject: ProjectView | null = null
  private projectObservers = new Map<
    object,
    (project: ProjectView | null, session: string | undefined) => void
  >()
  private projectRefresh = new Map<number, Promise<TaskView | undefined>>()
  private projectTransition:
    | {
        from: number
        to: number
        projectId: string
        session: string
        view: Promise<TaskView | undefined>
      }
    | undefined
  private watches = new Map<string, Watch>()
  private remembered = new Set<string>()
  private earlyBytes = 0
  private earlyEvents = new Map<string, unknown[]>()
  #queryWatchReservations = new Map<
    object,
    { projectId: string; generation: number; supervisor: EngineSupervisor }
  >()
  queryViewGeneration(projectId: string, supervisor: EngineSupervisor): number {
    if (this.disposed || this.#supervisor !== supervisor || this.projectId !== projectId)
      throw new EngineError(denied)
    return this.generation
  }
  reserveQueryWatch(projectId: string, supervisor: EngineSupervisor): object {
    if (
      this.disposed ||
      this.#supervisor !== supervisor ||
      this.projectId !== projectId ||
      this.remembered.size + this.#queryWatchReservations.size >= 16
    )
      throw new EngineError({
        code: 'RESOURCE_LIMIT',
        messageKey: 'resource.limitExceeded',
        params: { resource: 'memory' },
        retryable: false,
      })
    const token = Object.freeze({})
    this.#queryWatchReservations.set(token, { projectId, generation: this.generation, supervisor })
    return token
  }
  releaseQueryWatch(token: object): void {
    this.#queryWatchReservations.delete(token)
  }
  queryWatchReserved(token: object): boolean {
    return this.#queryWatchReservations.has(token)
  }
  async watchAcceptedQuery(
    token: object,
    job: JobView,
    supervisor: EngineSupervisor,
  ): Promise<BridgeResult<JobView>> {
    const reservation = this.#queryWatchReservations.get(token)
    if (
      !reservation ||
      reservation.supervisor !== supervisor ||
      this.#supervisor !== supervisor ||
      reservation.projectId !== job.projectId ||
      this.projectId !== job.projectId ||
      reservation.generation !== this.generation ||
      !this.validate('job', job) ||
      job.capability !== 'query.execute'
    )
      return { ok: false, error: safeError(denied) }
    // Transfer this one reserved watch into the original remembered16, never mint another cap.
    this.#queryWatchReservations.delete(token)
    this.remembered.add(job.jobId)
    const result = await this.subscribeJob(job.jobId)
    if (
      this.disposed ||
      this.#supervisor !== supervisor ||
      this.projectId !== reservation.projectId ||
      this.generation !== reservation.generation
    )
      return { ok: false, error: safeError(denied) }
    return result
  }
  private cancelledSubscriptions = new Set<string>()
  private dirtyWatches = new WeakSet<Watch>()
  private reconciliations = new Map<string, Promise<void>>()
  private pendingSubscriptions = new Map<string, Promise<BridgeResult<JobView>>>()
  private release: () => void
  private releaseConnection: () => void
  private recovery: Recovery | undefined
  private mainlineRecovery: TaskMainlineRecovery | undefined
  private mainlineRecoveryRequired = false
  private connection: 'ready' | 'reconnecting' | 'offline' = 'ready'
  private engineGeneration = -1
  private lastReadySession: string | undefined
  private disconnectedSession: string | undefined
  private disposed = false
  private sink: ((value: TaskUpdate) => void) | undefined
  constructor(
    private engine: TaskEngine,
    private readonly onProjectChanged?: (projectId: string | null) => void,
  ) {
    this.#supervisor = EngineSupervisor.owns(engine) ? engine : undefined
    this.lastReadySession = engine.engineSessionId
    this.release = engine.onNotification((value) => this.receive(value))
    this.releaseConnection = engine.onConnectionState((value) => this.connectionChanged(value))
  }
  installMainlineRecovery(supervisor: EngineSupervisor, adapter: TaskMainlineRecovery): () => void {
    if (
      this.disposed ||
      this.#supervisor !== supervisor ||
      supervisor.profile !== 'business3' ||
      this.mainlineRecoveryRequired ||
      typeof adapter.run !== 'function'
    )
      throw new EngineError(denied)
    this.mainlineRecoveryRequired = true
    this.mainlineRecovery = adapter
    return () => {
      if (this.mainlineRecovery !== adapter) return
      this.mainlineRecovery = undefined
      this.cancelRecovery()
      if (this.projectId) this.connection = 'offline'
    }
  }
  // Called only by trusted main-process project selection, never exposed as IPC.
  selectProject(projectId: string, jobs: string[] = []): void {
    id.parse(projectId)
    if (jobs.length > 16 || jobs.some((job) => !id.safeParse(job).success))
      throw new Error('INVALID_REQUEST')
    this.detachView()
    this.projectId = projectId
    this.projectRevision = undefined
    this.lastProject = null
    this.remembered = new Set(jobs)
    this.connection = 'ready'
    this.onProjectChanged?.(projectId)
  }
  // Main owns project identity independently of renderer and task view generation.
  projectContext(): string | null {
    return this.disposed ? null : this.projectId
  }
  /** Main-only selection fence; never cancels a durable accepted Job. */
  clearProject(): void {
    const previousSink = this.sink
    this.detachView()
    this.projectId = null
    this.projectRevision = undefined
    this.lastProject = null
    this.remembered.clear()
    this.connection = 'ready'
    this.onProjectChanged?.(null)
    this.notifyProject()
    try {
      previousSink?.({
        kind: 'restored',
        generation: this.generation,
        view: { generation: this.generation, project: null, jobs: [] },
      })
    } catch {
      /* selection is already fenced; a destroyed view cannot undo it */
    }
  }
  observeActiveProject(
    listener: (project: ProjectView | null, session: string | undefined) => void,
  ): () => void {
    if (this.disposed || this.projectObservers.size >= 8) throw new Error('INVALID_STATE')
    const registration = Object.freeze({})
    this.projectObservers.set(registration, listener)
    try {
      listener(this.lastProject, this.engine.engineSessionId)
    } catch (cause) {
      this.projectObservers.delete(registration)
      throw cause
    }
    return () => {
      this.projectObservers.delete(registration)
    }
  }
  private notifyProject(): void {
    for (const listener of this.projectObservers.values()) {
      try {
        listener(this.lastProject, this.engine.engineSessionId)
      } catch {
        /* isolate observers */
      }
    }
  }
  attachView(sink: (value: TaskUpdate) => void): void {
    this.detachView()
    this.sink = sink
  }
  private cancelRecovery(): void {
    const recovery = this.recovery
    if (recovery) {
      recovery.cancelled = true
      recovery.wake?.()
    }
    this.recovery = undefined
  }
  private clearView(remoteUnsubscribe: boolean, cancelRecovery: boolean): void {
    if (cancelRecovery) this.cancelRecovery()
    this.projectTransition = undefined
    this.generation++
    this.sink = undefined
    for (const watch of this.watches.values()) {
      if (remoteUnsubscribe && this.engine.engineSessionId === watch.binding.engineSessionId)
        void this.engine
          .request('job.unsubscribe', {
            projectId: watch.binding.projectId,
            jobId: watch.binding.jobId,
            subscriptionId: watch.binding.subscriptionId,
          })
          .catch(() => {})
    }
    this.watches.clear()
    this.earlyEvents.clear()
    this.earlyBytes = 0
  }
  detachView(): void {
    this.clearView(true, true)
  }
  private fenceConnection(remoteUnsubscribe = false): void {
    const sink = this.sink
    this.clearView(remoteUnsubscribe, false)
    this.sink = sink
    if (this.recovery) this.recovery.generation = this.generation
  }
  dispose(): void {
    this.disposed = true
    this.detachView()
    this.release()
    this.releaseConnection()
    this.projectObservers.clear()
    this.onProjectChanged?.(null)
  }
  private connectionChanged(event: EngineConnectionState): void {
    if (this.#supervisor && event.state === 'disconnected') {
      const issued = this.#supervisor.projectConnectionFailure(event)
      if (!issued) return
      event = issued
    }
    if (
      this.disposed ||
      !Number.isSafeInteger(event.generation) ||
      event.generation < this.engineGeneration ||
      !id.safeParse(event.engineSessionId).success
    )
      return
    this.engineGeneration = event.generation
    if (event.state === 'ready') {
      const previous = this.lastReadySession
      this.lastReadySession = event.engineSessionId
      if (this.recovery || !previous || previous === event.engineSessionId) return
      if (this.projectId && this.sink) {
        this.connection = 'reconnecting'
        this.fenceConnection()
        void this.beginRecovery(
          safeError({
            code: 'ENGINE_EXITED',
            messageKey: 'engine.exited',
            params: {},
            retryable: true,
          }),
        )
      }
      return
    }
    if (
      event.engineSessionId !== this.lastReadySession ||
      this.disconnectedSession === event.engineSessionId ||
      !this.validate('error', event.error)
    )
      return
    this.disconnectedSession = event.engineSessionId
    this.connection = 'reconnecting'
    this.fenceConnection()
    if (this.recovery) {
      this.recovery.error = safeDisplayError(event.error)
      return
    }
    if (this.projectId && this.sink) void this.beginRecovery(safeDisplayError(event.error))
  }
  private alive(recovery: Recovery): boolean {
    return (
      !this.disposed &&
      !recovery.cancelled &&
      this.recovery === recovery &&
      this.projectId === recovery.projectId &&
      this.generation === recovery.generation
    )
  }
  private connectionUpdate(recovery: Recovery, state: 'reconnecting' | 'offline'): void {
    if (this.alive(recovery))
      this.sink?.({
        kind: 'connection',
        generation: this.generation,
        projectId: recovery.projectId,
        state,
        attempt: recovery.attempt,
        error: safeDisplayError(recovery.error),
      })
  }
  private beginRecovery(error: SafeError): Promise<BridgeResult<TaskView>> {
    if (this.connection !== 'offline' && this.recovery && this.alive(this.recovery))
      return this.recovery.promise!
    this.cancelRecovery()
    const recovery: Recovery = {
      projectId: this.project(),
      generation: this.generation,
      attempt: 0,
      cancelled: false,
      error,
    }
    this.recovery = recovery
    this.connection = 'reconnecting'
    recovery.promise = Promise.resolve()
      .then(() => this.recover(recovery))
      .finally(() => {
        if (this.recovery === recovery) this.recovery = undefined
      })
    this.connectionUpdate(recovery, 'reconnecting')
    return recovery.promise
  }
  private restoreRecovery(
    recovery: Recovery,
    attemptToken: object,
  ): Promise<BridgeResult<TaskView>> {
    const adapter = this.mainlineRecovery
    if (!this.mainlineRecoveryRequired) return this.restoreOnce(true)
    const current = () => this.alive(recovery) && recovery.attemptToken === attemptToken
    const context: TaskRecoveryContext = Object.freeze({
      projectId: recovery.projectId,
      get generation() {
        return recovery.generation
      },
      isCurrent: current,
    })
    return this.guard(async () => {
      if (!adapter || !current()) throw { error: denied }
      let restored: Promise<BridgeResult<TaskView>> | undefined
      const operation = adapter.run(context, async (request) => {
        if (!current()) throw { error: denied }
        const scope = { token: attemptToken, request, current }
        recovery.scope = scope
        try {
          restored = this.restoreOnce(true, false, current)
          const result = await restored
          if (!current()) throw { error: denied }
          return result
        } finally {
          if (recovery.scope === scope) recovery.scope = undefined
        }
      })
      let result: BridgeResult<TaskView>
      try {
        result = await operation
      } catch (cause) {
        if (!current()) throw { error: denied }
        if (this.#supervisor) {
          const token = Object.freeze({})
          this.#caught.set(token, {
            value: this.#supervisor.projectFailure(cause, operation),
            recoveryRefusal: this.#supervisor.isMainlineRecoveryRefusal(cause, operation),
            generation: this.generation,
            projectId: this.projectId,
          })
          throw token
        }
        throw cause
      }
      if (!current()) throw { error: denied }
      if (!result.ok) this.forwardFailure(result, restored ?? operation)
      if (
        result.data.generation !== this.generation ||
        result.data.project?.projectId !== recovery.projectId
      )
        throw { error: denied }
      return result.data
    })
  }
  private async recover(recovery: Recovery): Promise<BridgeResult<TaskView>> {
    for (let attempt = 1; attempt <= 3; attempt++) {
      if (!this.alive(recovery)) return { ok: false, error: safeError(denied) }
      if (attempt > 1) {
        await new Promise<void>((done) => {
          const timer = setTimeout(done, 250 * 2 ** (attempt - 2))
          recovery.wake = () => {
            clearTimeout(timer)
            done()
          }
        })
        recovery.wake = undefined
        if (!this.alive(recovery)) return { ok: false, error: safeError(denied) }
      }
      recovery.attempt = attempt
      this.connectionUpdate(recovery, 'reconnecting')
      let timer: ReturnType<typeof setTimeout> | undefined
      const attemptToken = Object.freeze({})
      recovery.attemptToken = attemptToken
      const restoration = this.restoreRecovery(recovery, attemptToken)
      const result = await Promise.race([
        restoration,
        new Promise<BridgeResult<TaskView>>((done) => {
          timer = setTimeout(
            () =>
              done({
                ok: false,
                error: safeError({
                  code: 'TIMEOUT',
                  messageKey: 'job.timeout',
                  params: { phase: 'request' },
                  retryable: true,
                }),
              }),
            15000,
          )
        }),
      ])
      clearTimeout(timer)
      // Expire the exact attempt even when the race timed out while a real
      // request is still pending. A late reply cannot authorize another attempt.
      if (recovery.attemptToken === attemptToken) recovery.attemptToken = undefined
      if (!this.alive(recovery)) return { ok: false, error: safeError(denied) }
      if (result.ok) {
        this.connection = 'ready'
        this.sink?.({ kind: 'restored', generation: result.data.generation, view: result.data })
        // A synchronous sink may select/close/dispose. Never return its old view
        // as a current recovery success after that owner has been invalidated.
        if (!this.alive(recovery)) return { ok: false, error: safeError(denied) }
        return result
      }
      // Only the original authenticated mainline outcome may stop retrying a
      // nonretryable refusal. A DTO or a timed-out race has no such context.
      const issued = this.#outcomes.get(result)
      const terminalRefusal =
        this.mainlineRecoveryRequired &&
        issued?.context.recoveryRefusal === true &&
        issued.promises.has(restoration) &&
        issued.context.projectId === recovery.projectId &&
        issued.context.generation === this.generation &&
        result.error.retryable === false
      recovery.error = result.error
      this.fenceConnection(!!this.engine.engineSessionId)
      if (terminalRefusal || attempt === 3) {
        this.connection = 'offline'
        this.connectionUpdate(recovery, 'offline')
        return result
      }
    }
    return { ok: false, error: safeError(denied) }
  }
  private async call<T>(method: string, params: Record<string, unknown>): Promise<T> {
    if (!this.validate(`params_${method}`, params)) throw { error: invalid }
    const generation = this.generation
    const requestedSession = this.engine.engineSessionId
    const scope = this.recovery?.scope
    if (this.mainlineRecoveryRequired && this.connection !== 'ready' && !scope?.current())
      throw { error: denied }
    const operation =
      this.mainlineRecoveryRequired && this.connection !== 'ready' && scope
        ? scope.request(method, params)
        : this.engine.request(method, params)
    let result: unknown
    try {
      result = await operation
    } catch (cause) {
      if (generation !== this.generation) throw { error: denied }
      if (this.#supervisor) {
        const token = Object.freeze({})
        this.#caught.set(token, {
          value: this.#supervisor.projectFailure(cause, operation),
          recoveryRefusal: this.#supervisor.isMainlineRecoveryRefusal(cause, operation),
          generation,
          projectId: this.projectId,
        })
        throw token
      }
      throw cause
    }
    if (generation !== this.generation) {
      if (
        method === 'job.subscribe' &&
        this.engine.engineSessionId &&
        (!requestedSession || requestedSession === this.engine.engineSessionId) &&
        this.validate('result_job.subscribe', result)
      ) {
        const sub = result as { subscriptionId: string }
        void this.engine
          .request('job.unsubscribe', { ...params, subscriptionId: sub.subscriptionId })
          .catch(() => {})
      }
      throw { error: denied }
    }
    if (!this.validate(`result_${method}`, result)) throw new Error('INVALID_RESPONSE')
    if (result && typeof result === 'object') {
      const record = result as Record<string, unknown>
      for (const key of ['projectId', 'jobId', 'resultId', 'operationId']) {
        if (key in params && key in record && params[key] !== record[key])
          throw new Error('INVALID_RESPONSE')
      }
    }
    return result as T
  }
  private project(): string {
    if (!this.projectId) throw { error: denied }
    return this.projectId
  }
  private guard<T>(action: () => Promise<T>): Promise<BridgeResult<T>> {
    let source: Promise<T>
    try {
      source = action()
    } catch (cause) {
      source = Promise.reject(cause)
    }
    const promise: Promise<BridgeResult<T>> = source.then(
      (data) => ({ ok: true, data }),
      (cause) => {
        const context = cause && typeof cause === 'object' ? this.#caught.get(cause) : undefined
        const current =
          context && context.generation === this.generation && context.projectId === this.projectId
        const result = {
          ok: false as const,
          error: current
            ? safeDisplayError(context.value)
            : context
              ? safeError(denied)
              : safeError((cause as { error?: unknown } | null)?.error),
        }
        if (current) this.#outcomes.set(result, { context, promises: new WeakSet([promise]) })
        return result
      },
    )
    return promise
  }
  private forwardFailure(
    result: Extract<BridgeResult<unknown>, { ok: false }>,
    originatingPromise: Promise<unknown>,
  ): never {
    const issued = this.#outcomes.get(result)
    if (issued && issued.promises.has(originatingPromise)) {
      if (
        issued.context.generation !== this.generation ||
        issued.context.projectId !== this.projectId
      )
        throw { error: denied }
      const token = Object.freeze({})
      this.#caught.set(token, issued.context)
      throw token
    }
    // A DTO/clone alone carries no startup/business3 authority.
    throw { error: safeError(result.error) }
  }
  private observeProject(project: ProjectView, alreadyFenced = false): boolean {
    if (this.projectRevision !== undefined && project.projectRevision < this.projectRevision)
      throw {
        error: {
          code: 'INVALID_STATE',
          messageKey: 'protocol.invalidState',
          params: {},
          retryable: false,
        },
      }
    const advanced =
      this.projectRevision !== undefined && project.projectRevision > this.projectRevision
    this.projectRevision = project.projectRevision
    this.lastProject = project
    this.notifyProject()
    if (advanced && !alreadyFenced) {
      // A revision is a new view generation. Preserve the view delivery target,
      // discard its subscriptions, and keep each job's immutable input grouping.
      if (this.recovery) this.fenceConnection(true)
      else {
        const sink = this.sink
        this.detachView()
        this.sink = sink
      }
    }
    return advanced
  }
  private async restoreJobs(current?: () => boolean): Promise<JobView[]> {
    const jobs: JobView[] = []
    for (const jobId of this.remembered) {
      if (current && !current()) throw { error: denied }
      const operation = this.subscribeJob(jobId)
      const response = await operation
      if (current && !current()) throw { error: denied }
      if (!response.ok) this.forwardFailure(response, operation)
      jobs.push(response.data)
    }
    return jobs.map((job) => this.watches.get(job.jobId)?.job ?? job)
  }
  activeProject(): Promise<BridgeResult<ProjectView | null>> {
    return this.guard(async () => {
      if (!this.projectId) return null
      const project = await this.call<ProjectView>('project.get', { projectId: this.projectId })
      if (this.observeProject(project)) {
        const generation = this.generation
        await this.restoreJobs()
        if (generation !== this.generation) throw { error: denied }
      }
      return project
    })
  }
  getJob(jobId: string): Promise<BridgeResult<JobView>> {
    return this.guard(() => this.call('job.get', { projectId: this.project(), jobId }))
  }
  listJobs(options: JobListOptions): Promise<BridgeResult<Record<string, unknown>>> {
    return this.guard(async () => {
      if (
        !z
          .object({
            filter: z.enum(['all', 'active', 'terminal']),
            pageSize: z.number().int().min(1).max(100),
            listSnapshotId: id.nullable(),
            cursor: id.nullable(),
          })
          .strict()
          .safeParse(options).success
      )
        throw { error: invalid }
      return this.call('job.list', { ...options, projectId: this.project() })
    })
  }
  cancelJob(jobId: string): Promise<BridgeResult<Record<string, unknown>>> {
    // A cancellation response is a decision-time snapshot, never an authoritative terminal update.
    return this.guard(() => this.call('job.cancel', { projectId: this.project(), jobId }))
  }
  subscribeJob(jobId: string): Promise<BridgeResult<JobView>> {
    if (!id.safeParse(jobId).success)
      return Promise.resolve({ ok: false, error: safeError(invalid) })
    const key = `${this.generation}:${jobId}`
    const pending = this.pendingSubscriptions.get(key)
    if (pending) return pending
    if (this.pendingSubscriptions.size >= 16)
      return Promise.resolve({
        ok: false,
        error: safeError({
          code: 'RESOURCE_LIMIT',
          messageKey: 'resource.limitExceeded',
          params: { resource: 'memory' },
          retryable: false,
        }),
      })
    const operation = this.doSubscribe(jobId, key)
    const request = operation.finally(() => {
      this.pendingSubscriptions.delete(key)
      this.cancelledSubscriptions.delete(key)
      this.dropEarly(key)
    })
    // Register only this internally linked wrapper promise, never a caller-supplied DTO.
    void request.then(
      (result) => {
        const issued = this.#outcomes.get(result)
        if (issued?.promises.has(operation)) issued.promises.add(request)
      },
      () => {},
    )
    this.pendingSubscriptions.set(key, request)
    return request
  }
  private doSubscribe(jobId: string, key: string): Promise<BridgeResult<JobView>> {
    return this.guard(async () => {
      const projectId = this.project()
      if (!id.safeParse(jobId).success) throw { error: invalid }
      if (
        !this.remembered.has(jobId) &&
        this.remembered.size + this.#queryWatchReservations.size >= 16
      )
        throw {
          error: {
            code: 'RESOURCE_LIMIT',
            messageKey: 'resource.limitExceeded',
            params: { resource: 'memory' },
            retryable: false,
          },
        }
      const previous = this.watches.get(jobId)
      this.watches.delete(jobId)
      if (previous && previous.binding.engineSessionId === this.engine.engineSessionId)
        await this.call('job.unsubscribe', {
          projectId,
          jobId,
          subscriptionId: previous.binding.subscriptionId,
        })
      // Query first; subscribe's stateVersion must match before accepting notifications.
      for (let attempt = 0; attempt < 3; attempt++) {
        const job = await this.call<JobView>('job.get', { projectId, jobId })
        if (
          previous &&
          (job.stateVersion < previous.binding.stateVersion ||
            (job.stateVersion === previous.binding.stateVersion &&
              job.state !== previous.binding.state))
        )
          throw {
            error: {
              code: 'INVALID_STATE',
              messageKey: 'protocol.invalidState',
              params: {},
              retryable: false,
            },
          }
        if (this.cancelledSubscriptions.has(key)) throw { error: denied }
        const subscription = await this.call<{
          subscriptionId: string
          seq: number
          stateVersion: number
        }>('job.subscribe', { projectId, jobId })
        if (this.cancelledSubscriptions.has(key)) {
          await this.call('job.unsubscribe', {
            projectId,
            jobId,
            subscriptionId: subscription.subscriptionId,
          })
          throw { error: denied }
        }
        const session = this.engine.engineSessionId
        if (session && subscription.stateVersion === job.stateVersion) {
          this.watches.set(jobId, {
            job,
            binding: {
              engineSessionId: session,
              projectId,
              jobId,
              subscriptionId: subscription.subscriptionId,
              lastSeq: subscription.seq,
              stateVersion: job.stateVersion,
              state: job.state,
            },
          })
          this.remembered.add(jobId)
          const events = this.earlyEvents.get(key) ?? []
          this.dropEarly(key)
          for (const event of events) this.receive(event)
          const active = this.watches.get(jobId)
          // Applying an early atomic commit can fence this exact subscription.
          // Its restoration owns the successor; never dereference a removed watch.
          if (!active) throw { error: denied }
          return active.job
        }
        await this.call('job.unsubscribe', {
          projectId,
          jobId,
          subscriptionId: subscription.subscriptionId,
        })
      }
      throw {
        error: {
          code: 'INVALID_STATE',
          messageKey: 'protocol.invalidState',
          params: {},
          retryable: false,
        },
      }
    })
  }
  unsubscribeView(request: unknown): Promise<BridgeResult<null>> {
    const parsed = z
      .object({ jobId: id, generation: z.number().int().min(0).max(Number.MAX_SAFE_INTEGER) })
      .strict()
      .safeParse(request)
    if (!parsed.success) return Promise.resolve({ ok: false, error: safeError(invalid) })
    if (parsed.data.generation !== this.generation)
      return Promise.resolve({ ok: false, error: safeError(denied) })
    return this.unsubscribeJob(parsed.data.jobId)
  }
  unsubscribeJob(jobId: string): Promise<BridgeResult<null>> {
    return this.guard(async () => {
      if (!id.safeParse(jobId).success) throw { error: invalid }
      const key = `${this.generation}:${jobId}`
      if (this.pendingSubscriptions.has(key)) this.cancelledSubscriptions.add(key)
      const watch = this.watches.get(jobId)
      this.watches.delete(jobId)
      if (watch && watch.binding.engineSessionId === this.engine.engineSessionId)
        await this.call('job.unsubscribe', {
          projectId: watch.binding.projectId,
          jobId: watch.binding.jobId,
          subscriptionId: watch.binding.subscriptionId,
        })
      return null
    })
  }
  restore(): Promise<BridgeResult<TaskView>> {
    if (this.projectId && this.connection !== 'ready') {
      if (!this.recovery || this.connection === 'offline')
        this.fenceConnection(!!this.engine.engineSessionId)
      return this.beginRecovery(
        safeError({
          code: 'ENGINE_EXITED',
          messageKey: 'engine.exited',
          params: {},
          retryable: true,
        }),
      )
    }
    return this.restoreOnce()
  }
  private restoreOnce(
    reconcileMarkers = false,
    alreadyFenced = false,
    current?: () => boolean,
  ): Promise<BridgeResult<TaskView>> {
    return this.guard(async () => {
      // A project read and its job reads are separate transactions. A committed
      // job can therefore prove that the earlier project projection is obsolete.
      // Publish only after the projection covers every observed atomic marker;
      // continuous commits get three reads, never an unbounded retry loop.
      let requiredRevision = 0
      let requiredSnapshot: string | undefined
      for (let attempt = 0; attempt < 3; attempt++) {
        if (current && !current()) throw { error: denied }
        const project = this.projectId
          ? await this.call<ProjectView>('project.get', { projectId: this.projectId })
          : null
        if (current && !current()) throw { error: denied }
        if (project) this.observeProject(project, alreadyFenced)
        if (current && !current()) throw { error: denied }
        const generation = this.generation
        const session = this.engine.engineSessionId
        try {
          let jobs = await this.restoreJobs(current)
          if (reconcileMarkers) await this.reconcileMarkers(jobs)
          if (current && !current()) throw { error: denied }
          if (generation !== this.generation) throw { error: denied }
          // Operation reads may yield while same-generation progress advances.
          // Return the current validated watch DTO, never overwrite it with an
          // older job snapshot captured before that await.
          jobs = jobs.map((job) => this.watches.get(job.jobId)?.job ?? job)
          let conflictingSnapshot = false
          for (const job of jobs) {
            const commit = job.commitProgress as {
              mode: string
              marker?: { projectRevision: number; afterSnapshotId: string } | null
            }
            if (commit.mode !== 'atomic' || !commit.marker) continue
            const marker = commit.marker
            if (marker.projectRevision > requiredRevision) {
              requiredRevision = marker.projectRevision
              requiredSnapshot = marker.afterSnapshotId
            } else if (marker.projectRevision === requiredRevision) {
              if (requiredSnapshot && requiredSnapshot !== marker.afterSnapshotId)
                conflictingSnapshot = true
              requiredSnapshot = marker.afterSnapshotId
            }
          }
          if (
            conflictingSnapshot ||
            (project?.projectRevision === requiredRevision &&
              requiredSnapshot &&
              project.inputSnapshotId !== requiredSnapshot)
          ) {
            this.fenceConnection(true)
            throw {
              error: {
                code: 'INVALID_STATE',
                messageKey: 'protocol.invalidState',
                params: {},
                retryable: false,
              },
            }
          }
          if (!project || project.projectRevision >= requiredRevision)
            return { generation, project, jobs }
          // Fence before awaiting the new projection, including on exhaustion.
          // Preserve only this exact trusted atomic-refresh successor reference;
          // external view/session/project changes still invalidate its handoff.
          const transition = this.projectTransition
          const continuesTransition =
            transition &&
            transition.to === generation &&
            transition.projectId === project.projectId &&
            transition.session === session
          this.fenceConnection(true)
          if (continuesTransition) {
            transition.to = this.generation
            this.projectTransition = transition
          }
          alreadyFenced = true
        } catch (error) {
          // Only a trusted atomic-refresh transition may hand this read into its
          // successor. A project switch, reload, or engine replacement clears or
          // invalidates this single bounded reference instead of reviving old reads.
          const transition = this.projectTransition
          if (
            transition &&
            transition.from === generation &&
            transition.to === this.generation &&
            transition.projectId === project?.projectId &&
            transition.projectId === this.projectId &&
            transition.session === session &&
            session === this.engine.engineSessionId
          ) {
            const view = await transition.view
            if (
              view &&
              this.projectTransition === transition &&
              view.generation === this.generation &&
              this.projectId === transition.projectId &&
              this.engine.engineSessionId === session
            )
              return view
          }
          throw error
        }
      }
      throw {
        error: {
          code: 'INVALID_STATE',
          messageKey: 'protocol.invalidState',
          params: {},
          retryable: false,
        },
      }
    })
  }
  private async reconcileMarkers(jobs: JobView[]): Promise<void> {
    for (const job of jobs) {
      const marker = await this.call<Record<string, unknown> | null>('operation.get', {
        projectId: job.projectId,
        operationId: job.operationId,
      })
      if (marker && marker.jobId !== job.jobId) throw { error: invalid }
      const commit = job.commitProgress as { mode: string; marker?: Record<string, unknown> | null }
      if (
        commit.mode === 'atomic' &&
        ((commit.marker === null) !== (marker === null) ||
          (commit.marker &&
            marker &&
            Object.keys(commit.marker).some((key) => commit.marker![key] !== marker[key])))
      )
        throw { error: invalid }
    }
  }
  getResult(resultId: string): Promise<BridgeResult<ResultMetadataDTO>> {
    return this.guard<ResultMetadataDTO>(() =>
      this.call<ResultMetadataDTO>('result.get', { projectId: this.project(), resultId }),
    )
  }
  getResultPage(options: ResultPageOptions): Promise<BridgeResult<ResultPageDTO>> {
    return this.guard<ResultPageDTO>(async () => {
      if (
        !z
          .object({
            resultId: id,
            pageSize: z.number().int().min(1).max(200),
            cursor: id.nullable(),
          })
          .strict()
          .safeParse(options).success
      )
        throw { error: invalid }
      const result = await this.call<ResultMetadataDTO>('result.get', {
        projectId: this.project(),
        resultId: options.resultId,
      })
      return this.call<ResultPageDTO>('result.page', {
        binding: {
          projectId: this.project(),
          resultId: options.resultId,
          inputSnapshotId: result.inputSnapshotId,
          scope: result.scope,
          parametersHash: result.parametersHash,
          order: 'ordinal+rowId:asc',
        },
        pageSize: options.pageSize,
        cursor: options.cursor,
      })
    })
  }
  getOperation(operationId: string): Promise<BridgeResult<Record<string, unknown> | null>> {
    return this.guard(() => this.call('operation.get', { projectId: this.project(), operationId }))
  }
  private dropEarly(key: string): void {
    for (const value of this.earlyEvents.get(key) ?? [])
      this.earlyBytes -= Buffer.byteLength(JSON.stringify(value))
    this.earlyEvents.delete(key)
  }
  private refreshProject(watch: Watch): void {
    if (this.projectRefresh.has(this.generation) || this.projectRefresh.size >= 16) return
    const { projectId, engineSessionId } = watch.binding
    const fromGeneration = this.generation
    // A verified current subscription can request an authority read, but its
    // marker is not itself the project projection. Fence old delivery now so
    // no late old-input state can reach this view while that read is pending.
    // This is the same observed recovery, not a view detach: retain its bounded
    // budget and require operation evidence in the trusted successor as well.
    const reconcileMarkers = !!this.recovery
    this.fenceConnection(true)
    const generation = this.generation
    const refresh = Promise.resolve()
      .then(async () => {
        if (
          this.projectId !== projectId ||
          this.generation !== generation ||
          this.engine.engineSessionId !== engineSessionId
        )
          return
        const restored = await this.restoreOnce(reconcileMarkers, true)
        if (
          !restored.ok ||
          this.projectId !== projectId ||
          this.generation !== restored.data.generation ||
          this.engine.engineSessionId !== engineSessionId ||
          !restored.data.jobs.length
        )
          return
        const restoredView = restored.data
        this.sink?.({ kind: 'restored', generation: restoredView.generation, view: restoredView })
        return restoredView
      })
      .catch(() => undefined)
      .finally(() => {
        this.projectRefresh.delete(generation)
      })
    this.projectRefresh.set(generation, refresh)
    this.projectTransition = {
      from: fromGeneration,
      to: generation,
      projectId,
      session: engineSessionId,
      view: refresh,
    }
  }
  private reconcile(watch: Watch): void {
    const generation = this.generation
    const { jobId, projectId, engineSessionId } = watch.binding
    const key = `${generation}:${jobId}`
    this.dirtyWatches.add(watch)
    if (this.reconciliations.has(key) || this.reconciliations.size >= 16) return
    // One recovery per job is in flight; each recovery makes at most three
    // bounded read/subscription attempts, including gaps arriving with a reply.
    const recovery = Promise.resolve()
      .then(async () => {
        const pending = this.pendingSubscriptions.get(key)
        if (pending) await pending
        let target = watch
        for (let attempt = 0; attempt < 3; attempt++) {
          if (
            this.generation !== generation ||
            this.projectId !== projectId ||
            this.engine.engineSessionId !== engineSessionId ||
            this.watches.get(jobId) !== target ||
            this.cancelledSubscriptions.has(key) ||
            ['succeeded', 'failed', 'cancelled'].includes(target.binding.state)
          )
            return
          this.dirtyWatches.delete(target)
          const result = await this.subscribeJob(jobId)
          const current = this.watches.get(jobId)
          if (
            !result.ok ||
            this.generation !== generation ||
            this.projectId !== projectId ||
            this.engine.engineSessionId !== engineSessionId ||
            !current
          )
            return
          if (this.dirtyWatches.has(current)) {
            target = current
            continue
          }
          this.sink?.({ kind: 'job', generation, job: structuredClone(result.data) })
          return
        }
      })
      .catch(() => {})
      .finally(() => this.reconciliations.delete(key))
    this.reconciliations.set(key, recovery)
  }
  private receive(value: unknown): void {
    if (!this.validate('notification', value)) return
    const event = value as {
      event: string
      projectId: string
      engineSessionId: string
      jobId: string
      subscriptionId: string
      seq: number
      data: JobView & { progress?: ProgressView }
    }
    if (event.projectId !== this.projectId || event.engineSessionId !== this.engine.engineSessionId)
      return
    const watch = this.watches.get(event.jobId)
    const key = `${this.generation}:${event.jobId}`
    if (!watch && this.pendingSubscriptions.has(key)) {
      const events = this.earlyEvents.get(key) ?? []
      const bytes = Buffer.byteLength(JSON.stringify(value))
      if (events.length < 8 && this.earlyBytes + bytes <= 1048576) {
        this.earlyBytes += bytes
        events.push(value)
        this.earlyEvents.set(key, events)
      }
      return
    }
    if (
      !watch ||
      this.engine.engineSessionId !== watch.binding.engineSessionId ||
      event.engineSessionId !== watch.binding.engineSessionId ||
      event.projectId !== watch.binding.projectId ||
      event.jobId !== watch.binding.jobId ||
      event.subscriptionId !== watch.binding.subscriptionId
    )
      return
    if (['succeeded', 'failed', 'cancelled'].includes(watch.binding.state)) return
    const commit =
      event.event === 'job.state'
        ? (event.data.commitProgress as {
            mode: string
            marker?: { projectRevision: number } | null
          })
        : undefined
    if (
      commit?.mode === 'atomic' &&
      commit.marker &&
      (this.projectRevision === undefined || commit.marker.projectRevision > this.projectRevision)
    ) {
      this.refreshProject(watch)
      return
    }
    if (
      !(this.#supervisor?.profile === 'business3'
        ? acceptsBusiness3JobEvent(value, watch.binding)
        : acceptsJobEvent(value, watch.binding))
    ) {
      // Old/repeated notifications have no authority. A forward sequence gap or
      // contradictory next state requires a fresh durable snapshot, not guesses.
      if (event.seq > watch.binding.lastSeq || event.data.stateVersion > watch.binding.stateVersion)
        this.reconcile(watch)
      return
    }
    watch.binding.lastSeq = event.seq
    if (event.event === 'job.progress') {
      this.sink?.({
        kind: 'job',
        generation: this.generation,
        job: structuredClone(watch.job),
        progress: structuredClone(event.data.progress),
      })
      return
    }
    if (event.event !== 'job.state') return
    watch.binding.stateVersion = event.data.stateVersion
    watch.binding.state = event.data.state
    watch.job = event.data
    this.sink?.({ kind: 'job', generation: this.generation, job: structuredClone(event.data) })
  }
}
