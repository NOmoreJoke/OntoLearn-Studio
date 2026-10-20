import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import type { EngineConnectionState } from '../../apps/desktop/src/main/engine'
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
  engineSessionId: string | undefined = session
  processGeneration = 1
  restartFailures = 0
  states = new Set<(event: EngineConnectionState) => void>()
  subscriptionId = subscriptionId
  projectRevision = 1
  inputSnapshotId = 'a'.repeat(64)
  job = fixture('job running') as JobView
  calls: Array<{ method: string; params: Record<string, unknown> }> = []
  listeners = new Set<(value: unknown) => void>()
  failure: unknown
  onNotification(listener: (value: unknown) => void) {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
  onConnectionState(listener: (event: EngineConnectionState) => void) {
    this.states.add(listener)
    return () => {
      this.states.delete(listener)
    }
  }
  disconnect() {
    const previous = this.engineSessionId!
    this.engineSessionId = undefined
    this.states.forEach((listener) =>
      listener({
        state: 'disconnected',
        generation: this.processGeneration,
        engineSessionId: previous,
        error: { code: 'ENGINE_EXITED', messageKey: 'engine.exited', params: {}, retryable: true },
      }),
    )
  }
  emit(value: unknown) {
    this.listeners.forEach((listener) => listener(value))
  }
  async request(method: string, params: Record<string, unknown>): Promise<unknown> {
    this.calls.push({ method, params })
    if (!this.engineSessionId) {
      if (this.restartFailures-- > 0)
        throw {
          error: {
            code: 'ENGINE_EXITED',
            messageKey: 'engine.exited',
            params: {},
            retryable: true,
          },
        }
      this.processGeneration++
      this.engineSessionId = `00000000-0000-4000-8000-${String(100 + this.processGeneration).padStart(12, '0')}`
      const engineSessionId = this.engineSessionId
      this.states.forEach((listener) =>
        listener({ state: 'ready', generation: this.processGeneration, engineSessionId }),
      )
    }
    if (this.failure) throw this.failure
    if (method === 'project.get')
      return {
        projectId,
        projectRevision: this.projectRevision,
        inputSnapshotId: this.inputSnapshotId,
        dependencyVector: { 'facts:asserted': 1 },
        formatVersion: 2,
      }
    if (method === 'operation.get') return null
    if (method === 'job.get') return structuredClone(this.job)
    if (method === 'job.subscribe') {
      this.subscriptionId = `00000000-0000-4000-8000-${String(7 + this.calls.filter((call) => call.method === 'job.subscribe').length).padStart(12, '0')}`
      return {
        subscriptionId: this.subscriptionId,
        projectId,
        jobId: this.job.jobId,
        seq: 0,
        stateVersion: this.job.stateVersion,
      }
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
function jobOf(update: TaskUpdate): JobView {
  if (update.kind === 'job') return update.job
  if (update.kind === 'restored') return update.view.jobs[0]
  throw new Error('Expected an authoritative job/view update')
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
    engineSessionId: engine.engineSessionId,
    projectId,
    jobId: engine.job.jobId,
    subscriptionId: engine.subscriptionId,
    seq,
    event: 'job.state',
    data: job,
  }
}

describe('trusted task bridge', () => {
  it('fences a disconnected idle transport and rebuilds through authoritative job and operation reads', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    let restored!: (view: import('@ontolearn/contracts').TaskView) => void
    const recovery = new Promise<import('@ontolearn/contracts').TaskView>((done) => {
      restored = done
    })
    tasks.attachView((value) => {
      updates.push(value)
      if (value.kind === 'restored') restored(value.view)
    })
    const before = await tasks.restore()
    const count = engine.calls.length
    engine.job = { ...fixture('job failed'), stateVersion: engine.job.stateVersion + 2 } as JobView
    engine.disconnect()
    expect(updates[0]).toMatchObject({ kind: 'connection', state: 'reconnecting', attempt: 0 })
    const view = await recovery
    expect(view.jobs[0]).toEqual(engine.job)
    expect(before.ok && view.generation > before.data.generation).toBe(true)
    expect(engine.calls.slice(count).map((call) => call.method)).toEqual([
      'project.get',
      'job.get',
      'job.subscribe',
      'operation.get',
    ])
    expect(updates.some((value) => value.kind === 'job')).toBe(false)
    const after = engine.calls.length
    engine.states.forEach((listener) =>
      listener({
        state: 'disconnected',
        generation: 1,
        engineSessionId: session,
        error: { code: 'ENGINE_EXITED', messageKey: 'engine.exited', params: {}, retryable: true },
      }),
    )
    await new Promise((done) => setTimeout(done, 0))
    expect(engine.calls).toHaveLength(after)
    tasks.dispose()
  })
  it('stops after three failed read attempts, retains last-known jobs, and allows one explicit retry budget', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    let offline!: () => void
    const stopped = new Promise<void>((done) => {
      offline = done
    })
    tasks.attachView((value) => {
      updates.push(value)
      if (value.kind === 'connection' && value.state === 'offline') offline()
    })
    await tasks.restore()
    const count = engine.calls.length
    engine.restartFailures = 3
    engine.disconnect()
    await stopped
    expect(engine.calls.slice(count).map((call) => call.method)).toEqual([
      'project.get',
      'project.get',
      'project.get',
    ])
    expect(
      updates
        .filter((value) => value.kind === 'connection')
        .map((value) => (value.kind === 'connection' ? [value.state, value.attempt] : null)),
    ).toEqual([
      ['reconnecting', 0],
      ['reconnecting', 1],
      ['reconnecting', 2],
      ['reconnecting', 3],
      ['offline', 3],
    ])
    expect(updates.some((value) => value.kind === 'job' || value.kind === 'restored')).toBe(false)
    await new Promise((done) => setTimeout(done, 400))
    expect(engine.calls).toHaveLength(count + 3)
    engine.job = { ...fixture('job failed'), stateVersion: engine.job.stateVersion + 2 } as JobView
    const retry = await tasks.restore()
    expect(retry.ok && retry.data.jobs[0]).toEqual(engine.job)
    expect(engine.calls.slice(count + 3).map((call) => call.method)).toEqual([
      'project.get',
      'job.get',
      'job.subscribe',
      'operation.get',
    ])
    expect(updates.at(-1)?.kind).toBe('restored')
    tasks.dispose()
  })
  it('cancels old recovery backoff when the selected project changes', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    await tasks.restore()
    const count = engine.calls.length
    engine.restartFailures = 3
    engine.disconnect()
    await new Promise((done) => setTimeout(done, 0))
    tasks.selectProject('00000000-0000-4000-8000-000000000077')
    const oldCount = updates.length
    tasks.attachView((value) => updates.push(value))
    await new Promise((done) => setTimeout(done, 800))
    expect(engine.calls.slice(count).map((call) => call.method)).toEqual(['project.get'])
    expect(updates).toHaveLength(oldCount)
    tasks.dispose()
  })
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
  it('rejects old project/session/subscription, duplicate and post-terminal notifications', async () => {
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
    ])
      engine.emit({ ...valid, ...mutation })
    expect(updates).toEqual([])
    engine.emit(valid)
    engine.emit(valid)
    expect(updates.map((value) => jobOf(value).state)).toEqual(['succeeded'])
    engine.emit(stateEvent(engine, { ...engine.job, stateVersion: complete.stateVersion + 1 }, 2))
    expect(updates).toHaveLength(1)
    tasks.dispose()
  })
  it('advances the view generation on a newer project revision and retains historical job input', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    const before = await tasks.restore()
    if (!before.ok) throw new Error('fixture restore failed')
    const oldSubscription = engine.subscriptionId
    const calls = engine.calls.length
    engine.projectRevision = 2
    engine.inputSnapshotId = 'b'.repeat(64)
    const next = await tasks.restore()
    if (!next.ok) throw new Error('revision restore failed')
    expect(next.data.generation).toBe(before.data.generation + 1)
    expect(next.data.project?.inputSnapshotId).toBe('b'.repeat(64))
    expect(next.data.jobs[0].inputSnapshotId).toBe(before.data.jobs[0].inputSnapshotId)
    expect(next.data.jobs[0].input).toEqual(before.data.jobs[0].input)
    expect(engine.calls.slice(calls).map((call) => call.method)).toEqual([
      'project.get',
      'job.unsubscribe',
      'job.get',
      'job.subscribe',
    ])
    const final = {
      ...fixture('job succeeded'),
      stateVersion: engine.job.stateVersion + 1,
    } as JobView
    const count = engine.calls.length
    engine.emit({ ...stateEvent(engine, final, 2), subscriptionId: oldSubscription })
    await new Promise((done) => setTimeout(done, 0))
    expect(updates).toEqual([])
    expect(engine.calls).toHaveLength(count)
    engine.emit(stateEvent(engine, final))
    expect(
      updates.map((value) => ({
        generation: value.generation,
        input: jobOf(value).inputSnapshotId,
      })),
    ).toEqual([{ generation: next.data.generation, input: before.data.jobs[0].inputSnapshotId }])
    tasks.dispose()
  })
  it('fences old notifications on atomic completion and emits a re-read full revision view', async () => {
    const { engine, tasks } = service()
    engine.job = {
      ...fixture('atomic queued no commit'),
      state: 'running',
      stateVersion: 2,
    } as JobView
    const updates: TaskUpdate[] = []
    let restored!: (view: import('@ontolearn/contracts').TaskView) => void
    const restoration = new Promise<import('@ontolearn/contracts').TaskView>((done) => {
      restored = done
    })
    tasks.attachView((value) => {
      updates.push(value)
      if (value.kind === 'restored') restored(value.view)
    })
    const before = await tasks.restore()
    if (!before.ok) throw new Error('initial restore failed')
    const oldSubscription = engine.subscriptionId
    const original = engine.request.bind(engine)
    let started!: () => void
    const reading = new Promise<void>((done) => {
      started = done
    })
    let resolve!: (value: unknown) => void
    let projection: unknown
    engine.request = async (method, params) => {
      const response = await original(method, params)
      if (method === 'project.get') {
        projection = response
        started()
        return new Promise((done) => {
          resolve = done
        })
      }
      return response
    }
    const final = fixture('atomic succeeded committed') as JobView
    ;(final.commitProgress as { marker: { projectRevision: number } }).marker.projectRevision = 2
    engine.job = final
    engine.projectRevision = 2
    engine.inputSnapshotId = 'b'.repeat(64)
    const calls = engine.calls.length
    engine.emit(stateEvent(engine, final))
    // These are valid old-subscription notifications while project.get is pending.
    for (let seq = 2; seq <= 4; seq++)
      engine.emit({
        ...stateEvent(
          engine,
          {
            ...fixture('atomic queued no commit'),
            state: 'running',
            stateVersion: seq + 2,
          } as JobView,
          seq,
        ),
        subscriptionId: oldSubscription,
      })
    await reading
    expect(updates).toEqual([])
    resolve(projection)
    const view = await restoration
    expect(view.generation).toBe(before.data.generation + 1)
    expect(view.project?.projectRevision).toBe(2)
    expect(view.project?.inputSnapshotId).toBe('b'.repeat(64))
    expect(view.jobs[0]).toEqual(final)
    expect(view.jobs[0].inputSnapshotId).toBe(before.data.jobs[0].inputSnapshotId)
    expect(engine.calls.slice(calls).map((call) => call.method)).toEqual([
      'job.unsubscribe',
      'project.get',
      'job.get',
      'job.subscribe',
    ])
    expect(updates).toHaveLength(1)
    tasks.dispose()
  })
  it('hands the initial restore into a trusted atomic completion received with subscribe response', async () => {
    const { engine, tasks } = service()
    engine.job = {
      ...fixture('atomic queued no commit'),
      state: 'running',
      stateVersion: 2,
    } as JobView
    const final = fixture('atomic succeeded committed') as JobView
    ;(final.commitProgress as { marker: { projectRevision: number } }).marker.projectRevision = 2
    const original = engine.request.bind(engine)
    let first = true
    engine.request = async (method, params) => {
      const response = await original(method, params)
      if (method === 'job.subscribe' && first) {
        first = false
        engine.job = final
        engine.projectRevision = 2
        engine.inputSnapshotId = 'b'.repeat(64)
        engine.emit(stateEvent(engine, final))
      }
      return response
    }
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    const view = await tasks.restore()
    expect(view.ok).toBe(true)
    if (!view.ok) throw new Error('atomic restore handoff failed')
    expect(view.data.project?.projectRevision).toBe(2)
    expect(view.data.jobs[0]).toEqual(final)
    expect(view.data.jobs[0].inputSnapshotId).not.toBe(view.data.project?.inputSnapshotId)
    expect(updates).toHaveLength(1)
    expect(updates[0].kind === 'restored' && updates[0].view).toEqual(view.data)
    expect(engine.calls.map((call) => call.method)).toEqual([
      'project.get',
      'job.get',
      'job.subscribe',
      'job.unsubscribe',
      'project.get',
      'job.get',
      'job.subscribe',
    ])
    tasks.dispose()
  })
  it('does not hand an old initial restore through a later window generation', async () => {
    const { engine, tasks } = service()
    engine.job = {
      ...fixture('atomic queued no commit'),
      state: 'running',
      stateVersion: 2,
    } as JobView
    const final = fixture('atomic succeeded committed') as JobView
    ;(final.commitProgress as { marker: { projectRevision: number } }).marker.projectRevision = 2
    const original = engine.request.bind(engine)
    let first = true
    let release!: (value: unknown) => void
    let started!: () => void
    const refreshing = new Promise<void>((done) => {
      started = done
    })
    engine.request = async (method, params) => {
      const response = await original(method, params)
      if (method === 'job.subscribe' && first) {
        first = false
        engine.job = final
        engine.projectRevision = 2
        engine.emit(stateEvent(engine, final))
      } else if (method === 'project.get' && !first) {
        started()
        return new Promise((done) => {
          release = done
        })
      }
      return response
    }
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    const pending = tasks.restore()
    await refreshing
    tasks.attachView((value) => updates.push(value))
    release({
      projectId,
      projectRevision: 2,
      inputSnapshotId: 'b'.repeat(64),
      dependencyVector: { 'facts:asserted': 1 },
      formatVersion: 2,
    })
    const result = await pending
    expect(result.ok).toBe(false)
    expect(updates).toEqual([])
    tasks.dispose()
  })
  it('observes activeProject revision once, rebuilds read subscriptions, and rejects an older projection', async () => {
    const { engine, tasks } = service()
    await tasks.restore()
    const count = engine.calls.length
    expect((await tasks.activeProject()).ok).toBe(true)
    expect(engine.calls.slice(count).map((call) => call.method)).toEqual(['project.get'])
    const before = engine.calls.length
    engine.projectRevision = 3
    expect((await tasks.activeProject()).ok).toBe(true)
    expect(engine.calls.slice(before).map((call) => call.method)).toEqual([
      'project.get',
      'job.unsubscribe',
      'job.get',
      'job.subscribe',
    ])
    const stable = engine.calls.length
    engine.projectRevision = 2
    const stale = await tasks.activeProject()
    expect(stale.ok).toBe(false)
    expect(engine.calls.slice(stable).map((call) => call.method)).toEqual(['project.get'])
    tasks.dispose()
  })
  it('coalesces a missing notification into an authoritative read and fresh working subscription', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    let recovered!: (value: TaskUpdate) => void
    const recovery = new Promise<TaskUpdate>((done) => {
      recovered = done
    })
    tasks.attachView((value) => {
      updates.push(value)
      recovered(value)
    })
    await tasks.restore()
    const oldSubscription = engine.subscriptionId
    const before = engine.calls.length
    const wire = {
      ...fixture('job succeeded'),
      stateVersion: engine.job.stateVersion + 1,
    } as JobView
    engine.job = { ...engine.job, stateVersion: engine.job.stateVersion + 2 }
    const gap = stateEvent(engine, wire, 2)
    for (let i = 0; i < 5; i++) engine.emit(gap)
    expect(updates).toEqual([])
    expect(jobOf(await recovery)).toEqual(engine.job)
    expect(engine.subscriptionId).not.toBe(oldSubscription)
    expect(engine.calls.slice(before).map((call) => call.method)).toEqual([
      'job.unsubscribe',
      'job.get',
      'job.subscribe',
    ])
    // A late old subscription cannot settle the new watch; its seq is irrelevant.
    engine.emit({ ...stateEvent(engine, wire), subscriptionId: oldSubscription })
    expect(updates).toHaveLength(1)
    const final = {
      ...fixture('job succeeded'),
      stateVersion: engine.job.stateVersion + 1,
    } as JobView
    engine.emit(stateEvent(engine, final))
    expect(updates.map((value) => jobOf(value).state)).toEqual(['running', 'succeeded'])
    const calls = engine.calls.length
    engine.emit(stateEvent(engine, { ...engine.job, stateVersion: final.stateVersion + 1 }, 3))
    expect(engine.calls).toHaveLength(calls)
    tasks.dispose()
  })
  it('re-reads a further gap that arrives with the replacement subscription response', async () => {
    const { engine, tasks } = service()
    let recovered!: (value: TaskUpdate) => void
    const recovery = new Promise<TaskUpdate>((done) => {
      recovered = done
    })
    tasks.attachView(recovered)
    await tasks.restore()
    const original = engine.request.bind(engine)
    let introduced = false
    engine.request = async (method, params) => {
      const response = await original(method, params)
      if (method === 'job.subscribe' && !introduced) {
        introduced = true
        engine.job = { ...engine.job, stateVersion: engine.job.stateVersion + 1 }
        engine.emit(stateEvent(engine, engine.job, 2))
      }
      return response
    }
    engine.job = { ...engine.job, stateVersion: engine.job.stateVersion + 1 }
    const before = engine.calls.length
    engine.emit(stateEvent(engine, engine.job, 2))
    expect(jobOf(await recovery)).toEqual(engine.job)
    expect(engine.calls.slice(before).map((call) => call.method)).toEqual([
      'job.unsubscribe',
      'job.get',
      'job.subscribe',
      'job.unsubscribe',
      'job.get',
      'job.subscribe',
    ])
    tasks.dispose()
  })
  it('reconciles a contradictory next stateVersion without accepting its wire state', async () => {
    const { engine, tasks } = service()
    let recovered!: (value: TaskUpdate) => void
    const recovery = new Promise<TaskUpdate>((done) => {
      recovered = done
    })
    tasks.attachView(recovered)
    await tasks.restore()
    const wire = { ...engine.job, stateVersion: engine.job.stateVersion + 3 }
    engine.job = { ...fixture('job failed'), stateVersion: wire.stateVersion + 1 } as JobView
    engine.emit(stateEvent(engine, wire))
    expect(jobOf(await recovery)).toEqual(engine.job)
    tasks.dispose()
  })
  it('discards an in-flight gap recovery after the view generation changes', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    await tasks.restore()
    const original = engine.request.bind(engine)
    let started!: () => void
    const reading = new Promise<void>((done) => {
      started = done
    })
    let resolve!: (value: unknown) => void
    let held = false
    engine.request = async (method, params) => {
      if (method === 'job.get' && !held) {
        held = true
        started()
        return new Promise((done) => {
          resolve = done
        })
      }
      return original(method, params)
    }
    engine.emit(
      stateEvent(
        engine,
        { ...fixture('job succeeded'), stateVersion: engine.job.stateVersion + 1 } as JobView,
        2,
      ),
    )
    await reading
    tasks.attachView((value) => updates.push(value))
    const restored = await tasks.restore()
    expect(restored.ok).toBe(true)
    resolve({ ...fixture('job succeeded'), stateVersion: engine.job.stateVersion + 10 })
    // A macrotask lets the old bounded read finish and its recovery continuation settle.
    await new Promise((done) => setTimeout(done, 0))
    expect(updates).toEqual([])
    const final = {
      ...fixture('job succeeded'),
      stateVersion: engine.job.stateVersion + 1,
    } as JobView
    engine.emit(stateEvent(engine, final))
    expect(updates.map((value) => jobOf(value).state)).toEqual(['succeeded'])
    tasks.dispose()
  })
  it('does not recover an old engine binding until explicit restore reads the new session', async () => {
    const { engine, tasks } = service()
    const updates: TaskUpdate[] = []
    tasks.attachView((value) => updates.push(value))
    await tasks.restore()
    const before = engine.calls.length
    engine.engineSessionId = '00000000-0000-4000-8000-000000000099'
    const final = {
      ...fixture('job succeeded'),
      stateVersion: engine.job.stateVersion + 1,
    } as JobView
    engine.emit(stateEvent(engine, final, 2))
    await new Promise((done) => setTimeout(done, 0))
    expect(engine.calls).toHaveLength(before)
    await tasks.restore()
    engine.emit(stateEvent(engine, final))
    expect(updates.map((value) => jobOf(value).state)).toEqual(['succeeded'])
    tasks.dispose()
  })
  it('does not replay a read recovery after the current job was unsubscribed', async () => {
    const { engine, tasks } = service()
    await tasks.restore()
    const before = engine.calls.length
    engine.emit(
      stateEvent(
        engine,
        { ...fixture('job succeeded'), stateVersion: engine.job.stateVersion + 1 } as JobView,
        2,
      ),
    )
    await tasks.unsubscribeJob(engine.job.jobId)
    await new Promise((done) => setTimeout(done, 0))
    expect(engine.calls.slice(before).map((call) => call.method)).toEqual(['job.unsubscribe'])
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
