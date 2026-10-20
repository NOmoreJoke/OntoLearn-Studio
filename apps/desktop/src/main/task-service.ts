import { z } from 'zod'
import {
  safeError,
  type BridgeResult,
  type JobListOptions,
  type JobView,
  type ProjectView,
  type ProgressView,
  type ResultPageOptions,
  type TaskUpdate,
  type TaskView,
  type SafeError,
} from '@ontolearn/contracts'
import {
  acceptsJobEvent,
  validateV2,
  type EventBinding,
} from '../../../../packages/contracts/src/v2'
import type { EngineConnectionState } from './engine'

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
interface Recovery {
  projectId: string
  generation: number
  attempt: number
  cancelled: boolean
  error: SafeError
  promise?: Promise<BridgeResult<TaskView>>
  wake?: () => void
}
interface Watch {
  binding: EventBinding
  job: JobView
}

// This disposable cache holds view context only. All state and commit evidence is re-read from SQLite.
export class TaskService {
  private projectId: string | null = null
  private generation = 0
  private projectRevision: number | undefined
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
  private cancelledSubscriptions = new Set<string>()
  private dirtyWatches = new WeakSet<Watch>()
  private reconciliations = new Map<string, Promise<void>>()
  private pendingSubscriptions = new Map<string, Promise<BridgeResult<JobView>>>()
  private release: () => void
  private releaseConnection: () => void
  private recovery: Recovery | undefined
  private connection: 'ready' | 'reconnecting' | 'offline' = 'ready'
  private engineGeneration = -1
  private lastReadySession: string | undefined
  private disconnectedSession: string | undefined
  private disposed = false
  private sink: ((value: TaskUpdate) => void) | undefined
  constructor(private engine: TaskEngine) {
    this.lastReadySession = engine.engineSessionId
    this.release = engine.onNotification((value) => this.receive(value))
    this.releaseConnection = engine.onConnectionState((value) => this.connectionChanged(value))
  }
  // Called only by trusted main-process project selection, never exposed as IPC.
  selectProject(projectId: string, jobs: string[] = []): void {
    id.parse(projectId)
    if (jobs.length > 16 || jobs.some((job) => !id.safeParse(job).success))
      throw new Error('INVALID_REQUEST')
    this.detachView()
    this.projectId = projectId
    this.projectRevision = undefined
    this.remembered = new Set(jobs)
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
  }
  private connectionChanged(event: EngineConnectionState): void {
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
      !validateV2('error', event.error)
    )
      return
    this.disconnectedSession = event.engineSessionId
    this.connection = 'reconnecting'
    this.fenceConnection()
    if (this.recovery) {
      this.recovery.error = safeError(event.error)
      return
    }
    if (this.projectId && this.sink) void this.beginRecovery(safeError(event.error))
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
        error: safeError(recovery.error),
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
      const result = await Promise.race([
        this.restoreOnce(true),
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
      if (!this.alive(recovery)) return { ok: false, error: safeError(denied) }
      if (result.ok) {
        this.connection = 'ready'
        this.sink?.({ kind: 'restored', generation: result.data.generation, view: result.data })
        return result
      }
      recovery.error = result.error
      this.fenceConnection(!!this.engine.engineSessionId)
      if (attempt === 3) {
        this.connection = 'offline'
        this.connectionUpdate(recovery, 'offline')
        return result
      }
    }
    return { ok: false, error: safeError(denied) }
  }
  private async call<T>(method: string, params: Record<string, unknown>): Promise<T> {
    if (!validateV2(`params_${method}`, params)) throw { error: invalid }
    const generation = this.generation
    const requestedSession = this.engine.engineSessionId
    const result = await this.engine.request(method, params)
    if (generation !== this.generation) {
      if (
        method === 'job.subscribe' &&
        this.engine.engineSessionId &&
        (!requestedSession || requestedSession === this.engine.engineSessionId) &&
        validateV2('result_job.subscribe', result)
      ) {
        const sub = result as { subscriptionId: string }
        void this.engine
          .request('job.unsubscribe', { ...params, subscriptionId: sub.subscriptionId })
          .catch(() => {})
      }
      throw { error: denied }
    }
    if (!validateV2(`result_${method}`, result)) throw new Error('INVALID_RESPONSE')
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
  private async guard<T>(action: () => Promise<T>): Promise<BridgeResult<T>> {
    try {
      return { ok: true, data: await action() }
    } catch (error) {
      return { ok: false, error: safeError((error as { error?: unknown } | null)?.error) }
    }
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
  private async restoreJobs(): Promise<JobView[]> {
    const jobs: JobView[] = []
    for (const jobId of this.remembered) {
      const response = await this.subscribeJob(jobId)
      if (!response.ok) throw { error: response.error }
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
    const request = this.doSubscribe(jobId, key).finally(() => {
      this.pendingSubscriptions.delete(key)
      this.cancelledSubscriptions.delete(key)
      this.dropEarly(key)
    })
    this.pendingSubscriptions.set(key, request)
    return request
  }
  private async doSubscribe(jobId: string, key: string): Promise<BridgeResult<JobView>> {
    return this.guard(async () => {
      const projectId = this.project()
      if (!id.safeParse(jobId).success) throw { error: invalid }
      if (!this.remembered.has(jobId) && this.remembered.size >= 16)
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
  private restoreOnce(reconcileMarkers = false): Promise<BridgeResult<TaskView>> {
    return this.guard(async () => {
      const project = this.projectId
        ? await this.call<ProjectView>('project.get', { projectId: this.projectId })
        : null
      if (project) this.observeProject(project)
      const generation = this.generation
      const session = this.engine.engineSessionId
      try {
        const jobs = await this.restoreJobs()
        if (reconcileMarkers) await this.reconcileMarkers(jobs)
        if (generation !== this.generation) throw { error: denied }
        return { generation, project, jobs }
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
  getResult(resultId: string): Promise<BridgeResult<Record<string, unknown>>> {
    return this.guard(() => this.call('result.get', { projectId: this.project(), resultId }))
  }
  getResultPage(options: ResultPageOptions): Promise<BridgeResult<Record<string, unknown>>> {
    return this.guard(async () => {
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
      const result = await this.call<Record<string, unknown>>('result.get', {
        projectId: this.project(),
        resultId: options.resultId,
      })
      return this.call('result.page', {
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
    const sink = this.sink
    this.detachView()
    this.sink = sink
    const generation = this.generation
    const refresh = Promise.resolve()
      .then(async () => {
        if (
          this.projectId !== projectId ||
          this.generation !== generation ||
          this.engine.engineSessionId !== engineSessionId
        )
          return
        const project = await this.call<ProjectView>('project.get', { projectId })
        this.observeProject(project, true)
        const jobs = await this.restoreJobs()
        if (
          this.projectId !== projectId ||
          this.generation !== generation ||
          this.engine.engineSessionId !== engineSessionId ||
          !jobs.length
        )
          return
        const restoredView: TaskView = { generation, project, jobs }
        this.sink?.({ kind: 'restored', generation, view: restoredView })
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
    if (!validateV2('notification', value)) return
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
    if (!acceptsJobEvent(value, watch.binding)) {
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
