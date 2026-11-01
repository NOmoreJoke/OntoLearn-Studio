import { describe, expect, it, vi } from 'vitest'
import { spawnSync, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { EngineSupervisor, getEngineCommand } from '../../apps/desktop/src/main/engine'
import { JsonlReader } from '../../apps/desktop/src/main/jsonl'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { explainError } from '../../apps/desktop/src/renderer/src/task-presentation'
import { matchesResponse, validateV2 } from '../../packages/contracts/src/v2'
import {
  reassembleChangeSetDocument,
  type BridgeResult,
  type ChangeSetPage,
  type JobView,
  type TaskUpdate,
  type TaskView,
} from '@ontolearn/contracts'

// Test-owned interception observes actual child stdio, without reflecting private engine state.
const spawnControl = vi.hoisted(() => ({
  observe: undefined as undefined | ((child: ChildProcessWithoutNullStreams) => void),
  fail: false,
}))
vi.mock('node:child_process', async (importOriginal) => {
  const actual = await importOriginal<typeof import('node:child_process')>()
  return {
    ...actual,
    spawn: (...args: unknown[]) => {
      const child = Reflect.apply(
        actual.spawn,
        undefined,
        spawnControl.observe && spawnControl.fail
          ? [args[0], ['-I', '-c', 'raise SystemExit(73)'], args[2]]
          : args,
      ) as ChildProcessWithoutNullStreams
      spawnControl.observe?.(child)
      return child
    },
  }
})
const workspace = resolve('.')
// Development-only read of another checkout's sources; dependencies, database,
// Python process and Node runtime always belong to this test's own worktree.
// If set, its engine package must be editable-installed in this worktree's .venv
// so the real isolated worker imports the same source as the coordinator.
const source = process.env.ROOT_SOURCE_PATH ? resolve(process.env.ROOT_SOURCE_PATH) : workspace
const location = { packaged: false, appPath: join(workspace, 'apps/desktop'), resourcesPath: '' }
const python = getEngineCommand(location).command

function pythonJson(script: string, args: string[]): unknown {
  const result = spawnSync(python, ['-I', '-c', script, ...args], {
    cwd: workspace,
    encoding: 'utf8',
    timeout: 10000,
    maxBuffer: 1048576,
  })
  expect(result.error).toBeUndefined()
  expect(result.status, result.stderr).toBe(0)
  return JSON.parse(result.stdout)
}
const prepareScript = String.raw`
import json,sys
from uuid import uuid4
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'packages/engine/src'))
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
store=JobStore(sys.argv[2],contract=CONTRACT)
try:
 store.create_project('transport-fixture')
 project=store.public_project('transport-fixture')
 snapshot=store.project_get(project)
 parameters=store.put_blob(project,json.loads(sys.argv[3]))
 input_={'inputSnapshotId':snapshot['inputSnapshotId'],'scope':'scenario' if sys.argv[4]=='test.rounds' else 'asserted','definitionId':'transport-probe','parametersHash':parameters,'derivedResultIds':[],'preparedPlanRef':None}
 confirmation=None
 if sys.argv[4]=='test.atomic':
  plan={'definitions':[{'layer':'rule','id':'bridge-atomic-probe','value':{'enabled':True}}]}
  prepared=store.prepare_plan(project,snapshot['projectRevision'],plan,actor=str(uuid4()),permission='write')
  input_['preparedPlanRef']=prepared['preparedPlanRef']
  confirmation=prepared['confirmationRef']
 print(json.dumps({'projectId':project,'input':input_,'confirmationRef':confirmation}))
finally:
 store.close()
`
const evidenceScript = String.raw`
import json,sqlite3,sys
from pathlib import Path
connection=sqlite3.connect(Path(sys.argv[1]).as_uri()+'?mode=ro',uri=True)
try:
 row=connection.execute('SELECT dto,run FROM jobs WHERE id=?',(sys.argv[2],)).fetchone()
 rounds=[r[0] for r in connection.execute('SELECT number FROM rounds WHERE run=? ORDER BY number',(row[1],))] if row[1] else []
 terminal=connection.execute('SELECT status FROM run_terminal WHERE run=?',(row[1],)).fetchone() if row[1] else None
 print(json.dumps({'job':json.loads(row[0]),'rounds':rounds,'terminal':terminal[0] if terminal else None,'jobs':connection.execute('SELECT count(*) FROM jobs').fetchone()[0],'claims':connection.execute('SELECT count(*) FROM operation_claims').fetchone()[0]}))
finally:
 connection.close()
`
interface Fixture {
  projectId: string
  input: Record<string, unknown>
  confirmationRef: string | null
}
interface Notification {
  event: string
  jobId: string
  projectId: string
  engineSessionId: string
  subscriptionId: string
  seq: number
  data: JobView
}
type WireNotification = Omit<Notification, 'data'> & { data: unknown }
function terminalWait() {
  let resolveJob!: (job: JobView) => void
  let rejectWait!: (error: Error) => void
  const finished = new Promise<JobView>((done, fail) => {
    resolveJob = done
    rejectWait = fail
  })
  void finished.catch(() => {})
  const timer = setTimeout(
    () => rejectWait(new Error('No durable terminal state received within the test deadline')),
    10000,
  )
  return {
    finished,
    observe: (update: TaskUpdate) => {
      const jobs =
        update.kind === 'job' ? [update.job] : update.kind === 'restored' ? update.view.jobs : []
      for (const job of jobs)
        if (['succeeded', 'failed', 'cancelled'].includes(job.state)) resolveJob(job)
    },
    stop: () => clearTimeout(timer),
  }
}
async function runtime(
  capability: 'test.rounds' | 'test.read' | 'test.atomic',
  parameters: Record<string, unknown>,
  dropFirstState = false,
  coalesceAtomicCompletion = false,
  commitBeforeFirstJobRead = false,
) {
  const directory = await mkdtemp(join(tmpdir(), 'ontolearn-task-runtime-'))
  try {
    const database = join(directory, 'engine.sqlite')
    const fixture = pythonJson(prepareScript, [
      source,
      database,
      JSON.stringify(parameters),
      capability,
    ]) as Fixture
    // This check prevents a source-only probe from accidentally running an old
    // installed worker while launching a newer coordinator through -c.
    const installedWorker = pythonJson(
      'import json,pathlib,ontolearn_engine.worker;print(json.dumps(str(pathlib.Path(ontolearn_engine.worker.__file__).resolve())))',
      [],
    )
    expect(installedWorker).toBe(join(source, 'packages/engine/src/ontolearn_engine/worker.py'))
    const supervisor = new EngineSupervisor(location, {
      dataPath: database,
      allowedProjects: [fixture.projectId],
      testMode: true,
      registryPath: join(source, 'packages/contracts/v2/registry.json'),
      ...(process.env.ROOT_SOURCE_PATH
        ? {
            command: {
              command: python,
              args: [
                '-I',
                '-c',
                `import sys,runpy;sys.path.insert(0,${JSON.stringify(join(source, 'packages/engine/src'))});runpy.run_module('ontolearn_engine',run_name='__main__')`,
              ],
            },
          }
        : {}),
    })
    const calls: Array<{ method: string; params: Record<string, unknown> }> = []
    const received: Notification[] = []
    const allReceived: WireNotification[] = []
    let dropped: Notification | undefined
    let jobId = ''
    let forward: ((value: unknown) => void) | undefined
    let heldProject: unknown
    let delayedSubscribe = false
    let heldAtomic: Notification | undefined
    let releaseAtomic!: (event: Notification) => void
    const atomicNotification = new Promise<Notification>((done) => {
      releaseAtomic = done
    })
    const transport = {
      get engineSessionId() {
        return supervisor.engineSessionId
      },
      async request(method: string, params: Record<string, unknown>) {
        calls.push({ method, params: structuredClone(params) })
        const response = await supervisor.request(method, params)
        if (commitBeforeFirstJobRead && method === 'project.get' && !heldProject) {
          heldProject = structuredClone(response)
          // Only delay a real response: the worker and every returned DTO stay real.
          // No subscription exists while the actual atomic write finishes.
          const deadline = Date.now() + 6000
          while (true) {
            const actual = (await supervisor.request('job.get', {
              projectId: fixture.projectId,
              jobId,
            })) as JobView
            if (actual.state === 'succeeded') break
            if (Date.now() >= deadline || ['failed', 'cancelled'].includes(actual.state))
              throw new Error('Atomic write did not finish before project response delivery')
            await new Promise((done) => setTimeout(done, 10))
          }
        }
        if (coalesceAtomicCompletion && method === 'job.subscribe' && !delayedSubscribe) {
          delayedSubscribe = true
          let timer: ReturnType<typeof setTimeout> | undefined
          try {
            const event = await Promise.race([
              atomicNotification,
              new Promise<never>((_done, reject) => {
                timer = setTimeout(
                  () =>
                    reject(new Error('No real atomic completion for subscribe scheduling probe')),
                  6000,
                )
              }),
            ])
            expect(event.subscriptionId).toBe(
              (response as { subscriptionId: string }).subscriptionId,
            )
            // Delay only response delivery, then forward the unmodified real
            // notification in its promise turn before exposing that response.
            forward?.(event)
          } finally {
            clearTimeout(timer)
          }
        }
        return response
      },
      onConnectionState: supervisor.onConnectionState.bind(supervisor),
      onNotification(listener: (event: unknown) => void) {
        forward = listener
        return supervisor.onNotification((value) => {
          allReceived.push(structuredClone(value as WireNotification))
          const event = value as Notification
          if (event.event === 'job.state' && event.jobId === jobId) {
            received.push(structuredClone(event))
            const commit = event.data.commitProgress as { mode: string; marker?: unknown }
            if (
              coalesceAtomicCompletion &&
              !heldAtomic &&
              commit.mode === 'atomic' &&
              commit.marker
            ) {
              heldAtomic = event
              releaseAtomic(event)
              return
            }
            // Transport fault injection only: omit one actual wire notification.
            // Neither worker output, Store state nor any delivered wire value changes.
            if (dropFirstState && !dropped) {
              dropped = structuredClone(event)
              return
            }
          }
          listener(value)
        })
      },
    }
    const tasks = new TaskService(transport)
    const waiting = terminalWait()
    const views: TaskView[] = []
    const observe = (update: TaskUpdate) => {
      if (update.kind === 'restored') views.push(update.view)
      waiting.observe(update)
    }
    tasks.attachView(observe)
    try {
      expect((await supervisor.health()).protocolVersion).toBe(2)
      const job = (await supervisor.request('job.create', {
        projectId: fixture.projectId,
        operationId: randomUUID(),
        capability,
        input: fixture.input,
        confirmationRef: fixture.confirmationRef,
      })) as JobView
      jobId = job.jobId
      tasks.selectProject(fixture.projectId, [job.jobId])
      tasks.attachView(observe)
      const restored = await tasks.restore()
      expect(restored.ok).toBe(true)
      if (restored.ok)
        for (const current of restored.data.jobs)
          waiting.observe({ kind: 'job', generation: restored.data.generation, job: current })
      const terminal = await waiting.finished
      const result = await tasks.getJob(job.jobId)
      expect(result.ok).toBe(true)
      if (!result.ok) throw new Error('Durable final read failed')
      const evidence = pythonJson(evidenceScript, [database, job.jobId]) as {
        job: JobView
        rounds: number[]
        terminal: string | null
        jobs: number
        claims: number
      }
      const operation = await tasks.getOperation(job.operationId)
      expect(operation.ok).toBe(true)
      return {
        terminal,
        job: result.data,
        evidence,
        received,
        allReceived,
        dropped,
        calls,
        views,
        operation,
        initial: restored,
        heldAtomic,
        heldProject,
      }
    } finally {
      waiting.stop()
      tasks.dispose()
      supervisor.stop()
    }
  } finally {
    await rm(directory, { recursive: true, force: true, maxRetries: 20, retryDelay: 50 })
  }
}

async function disconnectRuntime(capability: 'test.rounds' | 'test.atomic', failRestarts = false) {
  const directory = await mkdtemp(join(tmpdir(), 'ontolearn-disconnect-runtime-'))
  let supervisor: EngineSupervisor | undefined
  let tasks: TaskService | undefined
  let deadline: ReturnType<typeof setTimeout> | undefined
  try {
    const database = join(directory, 'engine.sqlite')
    const fixture = pythonJson(prepareScript, [
      source,
      database,
      JSON.stringify({ workMs: 800, maxRounds: 50 }),
      capability,
    ]) as Fixture
    const command = getEngineCommand(location)
    const observed: Array<{
      child: ChildProcessWithoutNullStreams
      pending: Map<string, Record<string, unknown>>
      framingFailed: boolean
      bufferedBytes: () => number
    }> = []
    spawnControl.fail = false
    spawnControl.observe = (child) => {
      const item: (typeof observed)[number] = {
        child,
        pending: new Map(),
        framingFailed: false,
        bufferedBytes: () => outgoing.bufferedBytes + incoming.bufferedBytes,
      }
      observed.push(item)
      const outgoing = new JsonlReader(
        (value) => {
          const request = value as Record<string, unknown>
          if (validateV2('request', request)) item.pending.set(String(request.id), request)
          else item.framingFailed = true
        },
        () => {
          item.framingFailed = true
        },
      )
      const incoming = new JsonlReader(
        (value) => {
          const response = value as Record<string, unknown>
          const request = item.pending.get(String(response.id))
          if (request && matchesResponse(request, response))
            item.pending.delete(String(response.id))
        },
        () => {
          item.framingFailed = true
        },
      )
      child.stdout.on('data', (bytes: Buffer) => incoming.push(bytes))
      const write = child.stdin.write
      child.stdin.write = new Proxy(write, {
        apply(target, receiver, args: unknown[]) {
          outgoing.push(typeof args[0] === 'string' ? Buffer.from(args[0]) : (args[0] as Buffer))
          return Reflect.apply(target, receiver, args)
        },
      })
    }
    supervisor = new EngineSupervisor(location, {
      dataPath: database,
      allowedProjects: [fixture.projectId],
      testMode: true,
      registryPath: join(source, 'packages/contracts/v2/registry.json'),
      command,
    })
    const engine = supervisor
    const calls: Array<{ method: string; params: Record<string, unknown> }> = []
    const updates: TaskUpdate[] = []
    const raw: unknown[] = []
    let observedDisconnect = false
    let checkpoint!: (job: JobView) => void
    const checkpointReady = new Promise<JobView>((done) => {
      checkpoint = done
    })
    let restoreView!: (view: TaskView) => void
    const restored = new Promise<TaskView>((done) => {
      restoreView = done
    })
    let markOffline!: () => void
    const offline = new Promise<void>((done) => {
      markOffline = done
    })
    const transport = {
      get engineSessionId() {
        return engine.engineSessionId
      },
      request(method: string, params: Record<string, unknown>) {
        calls.push({ method, params: structuredClone(params) })
        return engine.request(method, params)
      },
      onConnectionState: engine.onConnectionState.bind(engine),
      onNotification(listener: (value: unknown) => void) {
        return engine.onNotification((value) => {
          raw.push(value)
          listener(value)
        })
      },
    }
    tasks = new TaskService(transport)
    const service = tasks
    const timeout = new Promise<never>((_done, reject) => {
      deadline = setTimeout(() => reject(new Error('real disconnect recovery deadline')), 15000)
    })
    void timeout.catch(() => {})
    const bounded = <T>(value: Promise<T>) => Promise.race([value, timeout])
    await engine.health()
    const created = (await engine.request('job.create', {
      projectId: fixture.projectId,
      operationId: randomUUID(),
      capability,
      input: fixture.input,
      confirmationRef: fixture.confirmationRef,
    })) as JobView
    service.selectProject(fixture.projectId, [created.jobId])
    service.attachView((update) => {
      updates.push(update)
      if (update.kind === 'connection') {
        observedDisconnect = true
        if (update.state === 'offline') markOffline()
      }
      if (update.kind === 'restored' && observedDisconnect) restoreView(update.view)
      const jobs =
        update.kind === 'job' ? [update.job] : update.kind === 'restored' ? update.view.jobs : []
      for (const job of jobs) {
        const progress = job.commitProgress as {
          mode: string
          committedProgress?: { lastCommittedRound: number }
        }
        if (
          capability === 'test.atomic'
            ? job.state === 'succeeded'
            : progress.committedProgress?.lastCommittedRound === 1
        )
          checkpoint(job)
      }
    })
    const initial = await service.restore()
    expect(initial.ok).toBe(true)
    if (!initial.ok) throw new Error('initial real view missing')
    const checkpointed = await bounded(checkpointReady)
    await new Promise<void>((done) => setImmediate(done))
    const old = observed.at(-1)!
    expect(old.framingFailed).toBe(false)
    expect(old.pending.size).toBe(0)
    expect(old.bufferedBytes()).toBe(0)
    // Round-1 is only the arming signal. Under CI scheduling delay, later rounds
    // can commit before SIGKILL; baseline retained progress at the kill itself.
    const before = (await bounded(
      engine.request('job.get', {
        projectId: fixture.projectId,
        jobId: created.jobId,
      }),
    )) as JobView
    expect(before.jobId).toBe(checkpointed.jobId)
    if (capability === 'test.rounds') {
      expect(before.state).toBe('running')
      expect(
        (before.commitProgress as { committedProgress?: { lastCommittedRound: number } })
          .committedProgress?.lastCommittedRound,
      ).toBeGreaterThanOrEqual(1)
    } else {
      expect(before.state).toBe('succeeded')
    }
    const oldPid = old.child.pid
    const oldSession = engine.engineSessionId
    const callCount = calls.length
    if (failRestarts) spawnControl.fail = true
    const closed = new Promise<void>((done) => old.child.once('close', () => done()))
    expect(old.child.kill('SIGKILL')).toBe(true)
    await bounded(closed)
    let firstManual: Awaited<ReturnType<TaskService['restore']>> | undefined
    if (failRestarts) {
      await bounded(offline)
      expect(observed).toHaveLength(4) // one original and exactly three real failed child starts
      expect(engine.engineSessionId).toBeUndefined()
      expect(
        updates.filter(
          (update) =>
            update.kind === 'restored' && update.view.generation > initial.data.generation,
        ),
      ).toEqual([])
      await new Promise((done) => setTimeout(done, 800))
      expect(observed).toHaveLength(4)
      spawnControl.fail = false
      firstManual = await bounded(service.restore())
    } else {
      // A user's first read during automatic recovery shares its pending result.
      firstManual = await bounded(service.restore())
    }
    expect(firstManual.ok).toBe(true)
    const view = await bounded(restored)
    expect(firstManual.ok && firstManual.data).toEqual(view)
    expect(engine.engineSessionId).not.toBe(oldSession)
    expect(observed.at(-1)?.child.pid).not.toBe(oldPid)
    const evidence = pythonJson(evidenceScript, [database, created.jobId]) as {
      job: JobView
      rounds: number[]
      jobs: number
      claims: number
    }
    const marker = await service.getOperation(created.operationId)
    expect(marker.ok).toBe(true)
    expect(calls.slice(callCount).some((call) => call.method === 'job.unsubscribe')).toBe(false)
    expect(calls.some((call) => call.method === 'job.create' || call.method === 'job.cancel')).toBe(
      false,
    )
    expect(calls.slice(callCount).some((call) => call.method === 'operation.get')).toBe(true)
    expect(view.jobs[0]).toEqual(evidence.job)
    expect(evidence.jobs).toBe(1)
    expect(evidence.claims).toBe(1)
    return { before, view, evidence, marker, updates, starts: observed.length, raw }
  } finally {
    clearTimeout(deadline)
    tasks?.dispose()
    supervisor?.stop()
    spawnControl.observe = undefined
    spawnControl.fail = false
    await rm(directory, { recursive: true, force: true, maxRetries: 20, retryDelay: 50 })
  }
}

describe('actual Python → supervisor → task service runtime', () => {
  it('automatically reconciles a real coordinator exit with zero pending requests and retained rounds', async () => {
    const result = await disconnectRuntime('test.rounds')
    expect(result.starts).toBe(2)
    expect(result.before.state).toBe('running')
    expect(result.view.jobs[0].state).toBe('failed')
    expect(result.view.jobs[0].error).toEqual({
      code: 'ENGINE_EXITED',
      messageKey: 'engine.exited',
      params: {},
      retryable: true,
    })
    expect(result.view.jobs[0].commitProgress).toEqual(result.before.commitProgress)
    const retained = (
      result.before.commitProgress as { committedProgress: { lastCommittedRound: number } }
    ).committedProgress.lastCommittedRound
    expect(result.evidence.rounds).toEqual(
      Array.from({ length: retained }, (_, index) => index + 1),
    )
    expect(
      result.updates.some(
        (update) => update.kind === 'connection' && update.state === 'reconnecting',
      ),
    ).toBe(true)
    expect(
      result.updates.some((update) => update.kind === 'connection' && update.state === 'offline'),
    ).toBe(false)
  }, 20000)
  it('re-reads a real atomic marker after transport loss without changing its successful job', async () => {
    const result = await disconnectRuntime('test.atomic')
    expect(result.starts).toBe(2)
    expect(result.view.jobs[0]).toEqual(result.before)
    expect(result.view.jobs[0].state).toBe('succeeded')
    expect(result.marker.ok && result.marker.data?.projectRevision).toBe(1)
    expect(result.view.jobs[0].commitProgress).toEqual(result.before.commitProgress)
  }, 20000)
  it('enters explicit offline after three real failed restarts, then permits an explicit read recovery', async () => {
    const result = await disconnectRuntime('test.rounds', true)
    expect(result.starts).toBe(5)
    const states = result.updates.filter((update) => update.kind === 'connection')
    expect(
      states.filter((update) => update.state === 'offline').map((update) => update.attempt),
    ).toEqual([3])
    expect(result.view.jobs[0].state).toBe('failed')
    expect(result.view.jobs[0].commitProgress).toEqual(result.before.commitProgress)
    const retained = (
      result.before.commitProgress as { committedProgress: { lastCommittedRound: number } }
    ).committedProgress.lastCommittedRound
    expect(result.evidence.rounds).toEqual(
      Array.from({ length: retained }, (_, index) => index + 1),
    )
  }, 20000)
  it('recovers one omitted real state notification through a durable read and fresh subscription', async () => {
    const result = await runtime('test.rounds', { workMs: 200, maxRounds: 3 }, true)
    expect(
      result.terminal.state,
      JSON.stringify({
        terminalError: result.terminal.error,
        durableState: result.evidence.job.state,
        durableError: result.evidence.job.error,
        rounds: result.evidence.rounds,
      }),
    ).toBe('succeeded')
    expect(result.job.state).toBe('succeeded')
    expect(result.evidence.job).toEqual(result.job)
    expect(result.evidence).toMatchObject({
      rounds: [1, 2, 3],
      terminal: 'succeeded',
      jobs: 1,
      claims: 1,
    })
    expect(result.dropped).toBeDefined()
    expect(validateV2('notification', result.dropped)).toBe(true)
    // A genuine progress frame can expose the missing state sequence before
    // another state arrives. It must trigger the same durable reconciliation.
    const later = result.allReceived.find(
      (event) =>
        event.subscriptionId === result.dropped!.subscriptionId && event.seq > result.dropped!.seq,
    )
    expect(later).toBeDefined()
    expect(validateV2('notification', later)).toBe(true)
    // Fresh subscribe is the durable recovery proof. A job that reaches terminal
    // during reconcile may emit no further job.state on the replacement subscription,
    // so do not require a second subscriptionId inside job.state-only `received`.
    expect(
      result.calls.filter((call) => call.method === 'job.subscribe').length,
    ).toBeGreaterThanOrEqual(2)
    expect(result.calls.filter((call) => call.method === 'job.get').length).toBeGreaterThanOrEqual(
      3,
    )
    expect(
      result.calls.every((call) =>
        ['project.get', 'job.get', 'job.subscribe', 'job.unsubscribe', 'operation.get'].includes(
          call.method,
        ),
      ),
    ).toBe(true)
  }, 20000)
  it('observes real atomic commit revision and sends a rebuilt historical-input view', async () => {
    const result = await runtime('test.atomic', { workMs: 200 })
    expect(result.terminal.state).toBe('succeeded')
    expect(result.evidence.job).toEqual(result.job)
    expect(result.evidence).toMatchObject({ jobs: 1, claims: 1, rounds: [] })
    expect(result.initial.ok).toBe(true)
    if (!result.initial.ok) throw new Error('initial view missing')
    expect(result.views).toHaveLength(1)
    const view = result.views[0]
    expect(view.generation).toBeGreaterThan(result.initial.data.generation)
    expect(view.project!.projectRevision).toBe(1)
    expect(view.jobs[0].state).toBe('succeeded')
    expect(view.jobs[0].inputSnapshotId).toBe(result.initial.data.jobs[0].inputSnapshotId)
    expect(view.jobs[0].inputSnapshotId).not.toBe(view.project!.inputSnapshotId)
    expect(result.operation.ok && result.operation.data?.projectRevision).toBe(1)
    expect(result.calls.filter((call) => call.method === 'project.get')).toHaveLength(2)
    expect(
      result.calls.some((call) => call.method === 'job.create' || call.method === 'job.cancel'),
    ).toBe(false)
  }, 20000)
  it('hands initial restoration over when a real atomic completion precedes subscribe response delivery', async () => {
    const result = await runtime('test.atomic', { workMs: 200 }, false, true)
    expect(result.heldAtomic).toBeDefined()
    expect(validateV2('notification', result.heldAtomic)).toBe(true)
    expect(result.initial.ok).toBe(true)
    if (!result.initial.ok) throw new Error('fresh initial restoration missing')
    expect(result.initial.data.project?.projectRevision).toBe(1)
    expect(result.initial.data.jobs[0]).toEqual(result.evidence.job)
    expect(result.initial.data.jobs[0].state).toBe('succeeded')
    expect(result.views).toHaveLength(1)
    expect(result.views[0]).toEqual(result.initial.data)
    expect(result.evidence).toMatchObject({ jobs: 1, claims: 1, rounds: [] })
    expect(
      result.calls.some((call) => call.method === 'job.create' || call.method === 'job.cancel'),
    ).toBe(false)
  }, 20000)
  it('re-reads project authority when an actual atomic write finishes before the first job read', async () => {
    const result = await runtime('test.atomic', { workMs: 200 }, false, false, true)
    expect(result.heldProject).toMatchObject({ projectRevision: 0 })
    expect(result.initial.ok).toBe(true)
    if (!result.initial.ok) throw new Error('fresh initial restoration missing')
    expect(result.initial.data.project?.projectRevision).toBe(1)
    expect(result.initial.data.jobs[0]).toEqual(result.evidence.job)
    expect(result.initial.data.jobs[0].state).toBe('succeeded')
    expect(result.initial.data.jobs[0].inputSnapshotId).not.toBe(
      result.initial.data.project?.inputSnapshotId,
    )
    expect(result.operation.ok && result.operation.data?.projectRevision).toBe(1)
    expect(result.evidence).toMatchObject({ jobs: 1, claims: 1, rounds: [] })
    expect(result.calls.filter((call) => call.method === 'project.get')).toHaveLength(2)
    expect(result.calls.some((call) => ['job.create', 'job.cancel'].includes(call.method))).toBe(
      false,
    )
  }, 20000)
  it('preserves persisted worker-failure error fields through the safe presentation boundary', async () => {
    const result = await runtime('test.read', { workMs: 200, failRound: 1 })
    const error = {
      code: 'INTERNAL_ERROR',
      messageKey: 'engine.internal',
      params: {},
      retryable: false,
    }
    expect(result.terminal.state).toBe('failed')
    expect(result.job.error).toEqual(error)
    expect(result.terminal.error).toEqual(error)
    expect(result.evidence.job.error).toEqual(error)
    expect(result.evidence).toMatchObject({ rounds: [], terminal: null, jobs: 1, claims: 1 })
    const explanation = explainError(result.job.error!, 'task')
    expect(Object.keys(explanation)).toEqual(['what', 'why', 'fix', 'detail'])
    expect(Object.values(explanation).every((value) => value.length > 0)).toBe(true)
    expect(explanation.detail).toContain('INTERNAL_ERROR')
  }, 20000)
})

it('restores real business3 selection, original Jobs and atomic marker through a fresh coordinator without test grants', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'ontolearn-business3-recovery-'))
  const database = join(directory, 'owned.sqlite')
  const children: Array<{
    child: ChildProcessWithoutNullStreams
    calls: Array<Record<string, unknown>>
    closed: Promise<void>
  }> = []
  const updates: TaskUpdate[] = []
  let supervisor: EngineSupervisor | undefined
  let tasks: TaskService | undefined
  let projects: ProjectMainlineService | undefined
  const deadline = Date.now() + 25000
  const step = async <T>(operation: Promise<T>): Promise<T> => {
    let timer: ReturnType<typeof setTimeout> | undefined
    try {
      return await Promise.race([
        operation,
        new Promise<never>((_, reject) => {
          timer = setTimeout(
            () => reject(Error('business3 recovery source test deadline')),
            Math.max(1, deadline - Date.now()),
          )
        }),
      ])
    } finally {
      clearTimeout(timer)
    }
  }
  const take = <T>(reply: BridgeResult<T>): T => {
    if (!reply.ok) throw Error(`Real business3 refused ${JSON.stringify(reply.error)}`)
    return reply.data
  }
  try {
    spawnControl.fail = false
    spawnControl.observe = (child) => {
      const calls: Array<Record<string, unknown>> = []
      const reader = new JsonlReader(
        (frame) => calls.push(frame as Record<string, unknown>),
        () => {
          throw Error('invalid real outgoing frame')
        },
      )
      const write = child.stdin.write
      child.stdin.write = new Proxy(write, {
        apply(target, receiver, args: unknown[]) {
          reader.push(typeof args[0] === 'string' ? Buffer.from(args[0]) : (args[0] as Buffer))
          return Reflect.apply(target, receiver, args)
        },
      })
      children.push({
        child,
        calls,
        closed: new Promise<void>((done) => child.once('close', () => done())),
      })
    }
    // Real production authority, no testMode, allowedProjects, worker fixture or SQL.
    supervisor = new EngineSupervisor(location, { profile: 'business3', dataPath: database })
    const engine = supervisor
    tasks = new TaskService(engine)
    const taskService = tasks
    projects = new ProjectMainlineService(engine, taskService, () =>
      taskService.attachView((update) => updates.push(update)),
    )
    const service = projects
    const receiver = engine.mainlineReplyReceiver()
    const receive = async <T>(work: () => Promise<BridgeResult<T>>): Promise<T> => {
      const delivery = await step(receiver.receive(work))
      if (delivery.value.ok) receiver.consume(delivery.receipt)
      return take(delivery.value)
    }
    const created = await receive(() =>
      service.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: '真实生产恢复',
        initialization: { kind: 'blank' },
      }),
    )
    const selected = await receive(() => service.openProject({ projectId: created.projectId }))
    const preview = await receive(() =>
      service.previewProjectChangeset({
        baseRevision: selected.projectRevision,
        intent: 'change',
        plan: {
          definitions: [
            {
              layer: 'ontology',
              id: 'Recovery',
              value: { triples: [], references: [], singleValuedPredicates: [] },
            },
            {
              layer: 'query',
              id: 'Q1',
              value: {
                text: 'ASK {}',
                references: [{ layer: 'ontology', id: 'Recovery' }],
                descriptor: {
                  version: 1,
                  name: '恢复原查询',
                  description: '真实有限ASK',
                  scope: 'asserted',
                  capabilityQuestion: 'Can the original result survive?',
                  source: 'editor',
                },
              },
            },
          ],
        },
      }),
    )
    if (preview.status !== 'ready') throw Error('Expected actual baseline preview')
    const pages: ChangeSetPage[] = []
    let cursor: string | null = null
    for (let count = 0; count < 8; count++) {
      const page = await receive(() =>
        service.getProjectDiffPage({
          previewHash: preview.previewHash,
          documentKind: 'diff',
          pageSize: 2,
          cursor,
        }),
      )
      pages.push(page)
      cursor = page.nextCursor
      if (page.complete) break
    }
    expect(pages.at(-1)?.complete).toBe(true)
    expect(await step(reassembleChangeSetDocument(preview, pages))).toHaveLength(2)
    const confirmation = await receive(() =>
      service.confirmProjectChangeset({
        previewHash: preview.previewHash,
        completionCursor: cursor!,
      }),
    )
    const accepted = await receive(() =>
      service.commitProjectChangeSet({ operationId: randomUUID(), confirmation }),
    )
    const terminal = async (job: JobView): Promise<JobView> => {
      while (Date.now() < deadline) {
        const value = take(await step(taskService.getJob(job.jobId)))
        expect(value.jobId).toBe(job.jobId)
        expect(value.operationId).toBe(job.operationId)
        if (['succeeded', 'failed', 'cancelled'].includes(value.state)) return value
        await step(new Promise<void>((done) => setTimeout(done, 10)))
      }
      throw Error('real original Job did not terminate')
    }
    const baseline = await terminal(accepted)
    expect(baseline.state).toBe('succeeded')
    const marker = take(await step(taskService.getOperation(baseline.operationId)))
    expect(marker?.jobId).toBe(baseline.jobId)
    // Establish the committed baseline through the real public read before
    // testing coordinator recovery; this does not assert automatic refresh.
    const preparedDomain = await receive(() => service.readProject({ editor: 'query' }))
    const atomic = baseline.commitProgress as {
      mode: string
      operationId?: string
      marker?: {
        projectRevision: number
        beforeSnapshotId: string
        afterSnapshotId: string
        planHash: string
      } | null
    }
    if (atomic.mode !== 'atomic' || !atomic.marker) throw Error('Expected real atomic marker')
    expect(atomic.operationId).toBe(baseline.operationId)
    expect(marker).toEqual({
      projectId: created.projectId,
      operationId: baseline.operationId,
      jobId: baseline.jobId,
      ...atomic.marker,
    })
    expect(preparedDomain.domain.projectRevision).toBe(atomic.marker.projectRevision)
    expect(preparedDomain.workspace.domainRevision).toBe(atomic.marker.projectRevision)
    expect(preparedDomain.inputSnapshotId).toBe(atomic.marker.afterSnapshotId)
    const preparedSource = service.source.current()!
    expect(preparedSource.project.projectId).toBe(created.projectId)
    expect(preparedSource.project.projectRevision).toBe(atomic.marker.projectRevision)
    expect(preparedSource.project.inputSnapshotId).toBe(atomic.marker.afterSnapshotId)
    expect(preparedSource.project.dependencyVector['query:Q1']).toBeGreaterThan(0)
    const loaded = await receive(() =>
      service.queries.loadQueryDefinition({ definitionId: 'Q1', selection: { kind: 'current' } }),
    )
    if (loaded.kind !== 'managed') throw Error('Expected actual managed query')
    expect(loaded.projectId).toBe(created.projectId)
    expect(loaded.baseProjectRevision).toBe(preparedSource.project.projectRevision)
    expect(loaded.inputSnapshotId).toBe(preparedSource.project.inputSnapshotId)
    expect(loaded.definitionVersion).toBe(preparedSource.project.dependencyVector['query:Q1'])
    const executed = await receive(() =>
      service.queries.executeSavedQuery({
        operationId: randomUUID(),
        loadRef: loaded.loadRef,
        visibleDraft: loaded.draft,
        selection: { kind: 'current' },
      }),
    )
    const query = await terminal(executed.acceptedJob)
    expect(query.state).toBe('succeeded')
    const domainBefore = await receive(() => service.readProject({ editor: 'query' }))
    const oldSource = service.source.current()!
    const replyBookBeforeFault = receiver.diagnostic()
    const old = children[0]
    const watermark = updates.length
    const oldSession = engine.engineSessionId
    expect(children).toHaveLength(1)
    expect(old.child.kill('SIGKILL')).toBe(true)
    await step(old.closed)
    // Manual and automatic recovery share the authentic same-project reauthorization.
    const restored = take(await step(taskService.restore()))
    expect(engine.engineSessionId).not.toBe(oldSession)
    expect(children).toHaveLength(2)
    const successor = children[1]
    expect(successor.child.pid).not.toBe(old.child.pid)
    const openIndex = successor.calls.findIndex((call) => call.method === 'project.open')
    const firstProjectRead = successor.calls.findIndex((call) => call.method === 'project.get')
    expect(openIndex).toBeGreaterThanOrEqual(0)
    expect(firstProjectRead).toBeGreaterThan(openIndex)
    expect(successor.calls.filter((call) => call.method === 'project.open')).toHaveLength(1)
    expect(successor.calls[openIndex].params).toEqual({ projectId: created.projectId })
    expect(
      successor.calls.some((call) => ['job.create', 'job.cancel'].includes(String(call.method))),
    ).toBe(false)
    expect(restored.project?.projectId).toBe(created.projectId)
    expect(new Set(restored.jobs.map((job) => job.jobId))).toEqual(
      new Set([baseline.jobId, query.jobId]),
    )
    expect(restored.jobs.find((job) => job.jobId === baseline.jobId)).toEqual(baseline)
    expect(restored.jobs.find((job) => job.jobId === query.jobId)).toEqual(query)
    expect(take(await step(taskService.getOperation(baseline.operationId)))).toEqual(marker)
    expect(take(await step(taskService.getOperation(query.operationId)))).toBeNull()
    const domainAfter = await receive(() => service.readProject({ editor: 'query' }))
    expect(domainAfter.domain).toEqual(domainBefore.domain)
    expect(service.source.current()?.engineSessionId).toBe(engine.engineSessionId)
    expect(service.source.current()?.owner).not.toBe(oldSource.owner)
    const faultUpdates = updates.slice(watermark)
    const reconnect = faultUpdates.findIndex(
      (u) =>
        u.kind === 'connection' && u.projectId === created.projectId && u.state === 'reconnecting',
    )
    const ready = faultUpdates.findIndex(
      (u) => u.kind === 'restored' && u.view.project?.projectId === created.projectId,
    )
    expect(reconnect).toBeGreaterThanOrEqual(0)
    expect(ready).toBeGreaterThan(reconnect)
    const replyBookAfterRecovery = receiver.diagnostic()
    expect(replyBookAfterRecovery.orphans).toBe(replyBookBeforeFault.orphans)
    expect(replyBookAfterRecovery.offered).toBe(0)
    expect(replyBookAfterRecovery.computing).toBe(0)
    expect(replyBookAfterRecovery.unknown).toBeGreaterThanOrEqual(replyBookBeforeFault.unknown)
    expect(replyBookAfterRecovery.holdingCount).toBeGreaterThan(0)
    // This completed-Job/atomic-marker positive does not claim an active query fault,
    // rounds recovery or GUI evidence; those remain distinct actual acceptance gates.
  } finally {
    projects?.dispose()
    tasks?.dispose()
    supervisor?.stop()
    try {
      await Promise.all(
        children.map(async (entry) => {
          let timer: ReturnType<typeof setTimeout> | undefined
          try {
            await Promise.race([
              entry.closed,
              new Promise<never>((_, reject) => {
                timer = setTimeout(() => reject(Error('owned business3 child close missing')), 3500)
              }),
            ])
          } finally {
            clearTimeout(timer)
          }
        }),
      )
      await rm(directory, { recursive: true, force: true, maxRetries: 20, retryDelay: 50 })
    } finally {
      spawnControl.observe = undefined
      spawnControl.fail = false
    }
  }
}, 30000)
