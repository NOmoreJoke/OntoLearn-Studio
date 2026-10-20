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
} from '@ontolearn/contracts'
import {
  acceptsJobEvent,
  validateV2,
  type EventBinding,
} from '../../../../packages/contracts/src/v2'

interface TaskEngine {
  request(method: string, params: Record<string, unknown>): Promise<unknown>
  readonly engineSessionId: string | undefined
  onNotification(listener: (event: unknown) => void): () => void
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
interface Watch {
  binding: EventBinding
  job: JobView
}

// This disposable cache holds view context only. All state and commit evidence is re-read from SQLite.
export class TaskService {
  private projectId: string | null = null
  private generation = 0
  private watches = new Map<string, Watch>()
  private remembered = new Set<string>()
  private earlyBytes = 0
  private earlyEvents = new Map<string, unknown[]>()
  private cancelledSubscriptions = new Set<string>()
  private pendingSubscriptions = new Map<string, Promise<BridgeResult<JobView>>>()
  private release: () => void
  private sink: ((value: TaskUpdate) => void) | undefined
  constructor(private engine: TaskEngine) {
    this.release = engine.onNotification((value) => this.receive(value))
  }
  // Called only by trusted main-process project selection, never exposed as IPC.
  selectProject(projectId: string, jobs: string[] = []): void {
    id.parse(projectId)
    if (jobs.length > 16 || jobs.some((job) => !id.safeParse(job).success))
      throw new Error('INVALID_REQUEST')
    this.detachView()
    this.projectId = projectId
    this.remembered = new Set(jobs)
  }
  attachView(sink: (value: TaskUpdate) => void): void {
    this.detachView()
    this.sink = sink
  }
  detachView(): void {
    this.generation++
    this.sink = undefined
    for (const watch of this.watches.values())
      void this.engine
        .request('job.unsubscribe', {
          projectId: watch.binding.projectId,
          jobId: watch.binding.jobId,
          subscriptionId: watch.binding.subscriptionId,
        })
        .catch(() => {})
    this.watches.clear()
    this.earlyEvents.clear()
    this.earlyBytes = 0
  }
  dispose(): void {
    this.detachView()
    this.release()
  }
  private async call<T>(method: string, params: Record<string, unknown>): Promise<T> {
    if (!validateV2(`params_${method}`, params)) throw { error: invalid }
    const generation = this.generation
    const result = await this.engine.request(method, params)
    if (generation !== this.generation) {
      if (method === 'job.subscribe' && validateV2('result_job.subscribe', result)) {
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
  activeProject(): Promise<BridgeResult<ProjectView | null>> {
    return this.guard(async () =>
      this.projectId ? this.call<ProjectView>('project.get', { projectId: this.projectId }) : null,
    )
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
      if (previous)
        await this.call('job.unsubscribe', {
          projectId,
          jobId,
          subscriptionId: previous.binding.subscriptionId,
        })
      // Query first; subscribe's stateVersion must match before accepting notifications.
      for (let attempt = 0; attempt < 3; attempt++) {
        const job = await this.call<JobView>('job.get', { projectId, jobId })
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
          return this.watches.get(jobId)!.job
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
      if (watch)
        await this.call('job.unsubscribe', {
          projectId: watch.binding.projectId,
          jobId: watch.binding.jobId,
          subscriptionId: watch.binding.subscriptionId,
        })
      return null
    })
  }
  restore(): Promise<BridgeResult<TaskView>> {
    return this.guard(async () => {
      const generation = this.generation
      const project = this.projectId
        ? await this.call<ProjectView>('project.get', { projectId: this.projectId })
        : null
      const jobs: JobView[] = []
      for (const jobId of this.remembered) {
        const response = await this.subscribeJob(jobId)
        if (!response.ok) throw { error: response.error }
        jobs.push(response.data)
      }
      if (generation !== this.generation) throw { error: denied }
      return {
        generation,
        project,
        jobs: jobs.map((job) => this.watches.get(job.jobId)?.job ?? job),
      }
    })
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
  private receive(value: unknown): void {
    if (!validateV2('notification', value)) return
    const event = value as {
      event: string
      projectId: string
      engineSessionId: string
      jobId: string
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
      !acceptsJobEvent(value, watch.binding) ||
      this.engine.engineSessionId !== watch.binding.engineSessionId
    )
      return
    watch.binding.lastSeq = event.seq
    if (event.event === 'job.progress') {
      this.sink?.({
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
    this.sink?.({ generation: this.generation, job: structuredClone(event.data) })
  }
}
