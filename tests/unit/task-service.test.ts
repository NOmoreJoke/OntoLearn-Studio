import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import {
  explainError,
  jobStatus,
  resultSummary,
} from '../../apps/desktop/src/renderer/src/task-presentation'
import { healthSchema, safeError, type JobView, type TaskUpdate } from '@ontolearn/contracts'

function fixture(name: string): Record<string, unknown> {
  return structuredClone(fixtures.cases.find((item) => item.name === name)!.value) as Record<
    string,
    unknown
  >
}
const projectId = '00000000-0000-4000-8000-000000000001'
const session = '00000000-0000-4000-8000-000000000002'
const subscriptionId = '00000000-0000-4000-8000-000000000008'
class Engine {
  engineSessionId = session
  job = fixture('job running') as JobView
  calls: Array<{ method: string; params: Record<string, unknown> }> = []
  listeners = new Set<(value: unknown) => void>()
  failure: unknown
  onNotification(listener: (value: unknown) => void) {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
  emit(value: unknown) {
    this.listeners.forEach((listener) => listener(value))
  }
  async request(method: string, params: Record<string, unknown>): Promise<unknown> {
    this.calls.push({ method, params })
    if (this.failure) throw this.failure
    if (method === 'project.get')
      return {
        projectId,
        projectRevision: 1,
        inputSnapshotId: this.job.inputSnapshotId,
        dependencyVector: { 'facts:asserted': 1 },
        formatVersion: 2,
      }
    if (method === 'job.get') return structuredClone(this.job)
    if (method === 'job.subscribe')
      return {
        subscriptionId,
        projectId,
        jobId: this.job.jobId,
        seq: 0,
        stateVersion: this.job.stateVersion,
      }
    if (method === 'job.unsubscribe')
      return { subscriptionId: params.subscriptionId, unsubscribed: true }
    if (method === 'job.cancel')
      return {
        jobId: this.job.jobId,
        disposition: 'accepted',
        state: 'cancelling',
        stateVersion: this.job.stateVersion + 1,
      }
    throw new Error('unimplemented fake')
  }
}
function service() {
  const engine = new Engine()
  const tasks = new TaskService(engine)
  tasks.selectProject(projectId, [engine.job.jobId])
  return { engine, tasks }
}
function stateEvent(engine: Engine, job: JobView, seq = 1) {
  return {
    kind: 'notification',
    protocolVersion: 2,
    engineSessionId: session,
    projectId,
    jobId: engine.job.jobId,
    subscriptionId,
    seq,
    event: 'job.state',
    data: job,
  }
}

describe('trusted task bridge', () => {
  it('does not accept renderer project authority or generic creation', async () => {
    const engine = new Engine()
    const tasks = new TaskService(engine)
    expect(await tasks.activeProject()).toEqual({ ok: true, data: null })
    expect((await tasks.getJob(engine.job.jobId)).ok).toBe(false)
    expect(engine.calls).toEqual([])
    tasks.selectProject(projectId)
    expect(
      (
        await tasks.listJobs({
          projectId: 'evil',
          filter: 'all',
          pageSize: 20,
          cursor: null,
          listSnapshotId: null,
        } as never)
      ).ok,
    ).toBe(false)
    expect(engine.calls).toEqual([])
    expect('createJob' in tasks).toBe(false)
    tasks.dispose()
  })
  it('rebuilds using authoritative queries and subscriptions, never writes or cancellation', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    const first = await tasks.restore()
    expect(first.ok).toBe(true)
    tasks.detachView()
    engine.job = fixture('job succeeded') as JobView
    tasks.attachView((value) => updates.push(value))
    const next = await tasks.restore()
    expect(next.ok && next.data.jobs[0]).toEqual(engine.job)
    expect(next.ok && first.ok && next.data.generation > first.data.generation).toBe(true)
    expect(engine.calls.map((call) => call.method)).toEqual([
      'project.get',
      'job.get',
      'job.subscribe',
      'job.unsubscribe',
      'project.get',
      'job.get',
      'job.subscribe',
    ])
    expect(updates).toEqual([])
    tasks.dispose()
  })
  it('rejects old project/session/subscription, duplicate, gap and regressive state notifications', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    await tasks.restore()
    const complete = fixture('job succeeded') as JobView
    complete.stateVersion = engine.job.stateVersion + 1
    const valid = stateEvent(engine, complete)
    for (const mutation of [
      { projectId: subscriptionId },
      { engineSessionId: subscriptionId },
      { subscriptionId: session },
      { seq: 2 },
      { data: { ...complete, stateVersion: engine.job.stateVersion } },
    ])
      engine.emit({ ...valid, ...mutation })
    expect(updates).toEqual([])
    engine.emit(valid)
    engine.emit(valid)
    expect(updates.map((value) => value.job.state)).toEqual(['succeeded'])
    engine.emit(stateEvent(engine, { ...engine.job, stateVersion: complete.stateVersion + 1 }, 2))
    expect(updates).toHaveLength(1)
    tasks.dispose()
  })
  it('keeps cancellation decision separate from live state and coalesces subscriptions', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    const [one, two] = await Promise.all([
      tasks.subscribeJob(engine.job.jobId),
      tasks.subscribeJob(engine.job.jobId),
    ])
    expect(one).toEqual(two)
    expect(engine.calls.filter((call) => call.method === 'job.subscribe')).toHaveLength(1)
    expect((await tasks.cancelJob(engine.job.jobId)).ok).toBe(true)
    expect(updates).toEqual([])
    await tasks.unsubscribeJob(engine.job.jobId)
    expect(engine.calls.filter((call) => call.method === 'job.cancel')).toHaveLength(1)
    tasks.dispose()
  })
  it('rejects an old page unsubscribe after the new view has subscribed', async () => {
    const { engine, tasks } = service()
    const first = await tasks.restore()
    tasks.attachView(() => {})
    const next = await tasks.restore()
    if (!first.ok || !next.ok) throw new Error('fixture restore failed')
    const count = engine.calls.filter((call) => call.method === 'job.unsubscribe').length
    expect(
      await tasks.unsubscribeView({ jobId: engine.job.jobId, generation: first.data.generation }),
    ).toEqual({
      ok: false,
      error: {
        code: 'PERMISSION_DENIED',
        messageKey: 'permission.denied',
        params: {},
        retryable: false,
      },
    })
    expect(engine.calls.filter((call) => call.method === 'job.unsubscribe')).toHaveLength(count)
    expect(
      (await tasks.unsubscribeView({ jobId: engine.job.jobId, generation: next.data.generation }))
        .ok,
    ).toBe(true)
    tasks.dispose()
  })
  it('retains a notification delivered immediately with the subscribe response', async () => {
    const { engine, tasks } = service()
    const original = engine.request.bind(engine)
    const complete = {
      ...fixture('job succeeded'),
      stateVersion: engine.job.stateVersion + 1,
    } as JobView
    engine.request = async (method, params) => {
      const result = await original(method, params)
      if (method === 'job.subscribe') engine.emit(stateEvent(engine, complete))
      return result
    }
    const response = await tasks.subscribeJob(engine.job.jobId)
    expect(response.ok && response.data.state).toBe('succeeded')
    tasks.dispose()
  })
  it('preserves catalog error fields but never exception text or malformed safe errors', async () => {
    const { engine, tasks } = service()
    const safe = {
      code: 'TIMEOUT',
      messageKey: 'job.timeout',
      params: { phase: 'request' },
      retryable: true,
    }
    engine.failure = { error: safe, message: '/private/path secret' }
    expect(await tasks.getJob(engine.job.jobId)).toEqual({ ok: false, error: safe })
    engine.failure = new Error('/private/path token')
    const failed = await tasks.getJob(engine.job.jobId)
    expect(failed).toEqual({ ok: false, error: safeError(undefined) })
    expect(JSON.stringify(failed)).not.toContain('/private')
    tasks.dispose()
  })
  it('cleans a subscription that resolves after view invalidation', async () => {
    const { engine, tasks } = service()
    let resolve!: (value: unknown) => void
    let started!: () => void
    const subscriptionStarted = new Promise<void>((done) => {
      started = done
    })
    const original = engine.request.bind(engine)
    engine.request = async (method, params) =>
      method === 'job.subscribe'
        ? new Promise((done) => {
            resolve = done
            started()
          })
        : original(method, params)
    const pending = tasks.subscribeJob(engine.job.jobId)
    await subscriptionStarted
    tasks.detachView()
    resolve({
      subscriptionId,
      projectId,
      jobId: engine.job.jobId,
      seq: 0,
      stateVersion: engine.job.stateVersion,
    })
    expect((await pending).ok).toBe(false)
    expect(engine.calls.at(-1)).toEqual({
      method: 'job.unsubscribe',
      params: { projectId, jobId: engine.job.jobId, subscriptionId },
    })
    tasks.dispose()
  })
})
describe('safe four-part presentation', () => {
  it('uses v2 health and fixed error templates', () => {
    expect(
      healthSchema.safeParse({
        protocolVersion: 2,
        engineVersion: '0.1.0',
        status: 'ok',
        capabilities: ['health'],
      }).success,
    ).toBe(true)
    const text = explainError(
      safeError({
        code: 'TIMEOUT',
        messageKey: 'job.timeout',
        params: { phase: 'cancel' },
        retryable: true,
      }),
      'task',
    )
    expect(Object.keys(text)).toEqual(['what', 'why', 'fix', 'detail'])
    expect(text.why).toContain('取消收尾')
    expect(text.fix).toContain('不要重新提交写任务')
    expect(
      explainError(
        {
          code: 'INTERNAL_ERROR',
          messageKey: 'evil',
          params: { path: '/private' },
          retryable: false,
        },
        'task',
      ).detail,
    ).not.toContain('/private')
  })
  it('distinguishes cancelled/failed and unavailable summary without claiming all work complete', () => {
    expect(jobStatus(fixture('cancelled zero rounds') as JobView)).toContain('已取消')
    const job = {
      ...fixture('cancelled with two rounds'),
      state: 'succeeded',
      resultRef: (fixture('job succeeded') as JobView).resultRef,
    } as JobView
    expect(resultSummary({ rows: [] }, job)).toContain('不可用')
    const progress = (
      job.commitProgress as {
        committedProgress: { runId: string; lastCommittedRound: number; snapshotRef: string }
      }
    ).committedProgress
    const cells = [
      'run.summary.v1',
      progress.runId,
      progress.lastCommittedRound,
      progress.snapshotRef,
      true,
      true,
      3,
      'consumption',
    ]
    const binding = {
      projectId: job.projectId,
      resultId: job.resultRef!.resultId,
      inputSnapshotId: job.inputSnapshotId,
      scope: job.scope,
      parametersHash: job.parametersHash,
    }
    expect(resultSummary({ binding, rows: [{ cells }] }, job)).toContain('存在未处理事件（3）')
    expect(
      resultSummary({ binding, rows: [{ cells: [...cells.slice(0, 6), 0, 'consumption'] }] }, job),
    ).toContain('不可用')
    expect(
      resultSummary({ binding: { ...binding, resultId: subscriptionId }, rows: [{ cells }] }, job),
    ).toContain('不可用')
  })
})
