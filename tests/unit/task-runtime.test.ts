import { describe, expect, it } from 'vitest'
import { spawnSync } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { EngineSupervisor, getEngineCommand } from '../../apps/desktop/src/main/engine'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { explainError } from '../../apps/desktop/src/renderer/src/task-presentation'
import { validateV2 } from '../../packages/contracts/src/v2'
import type { JobView, TaskUpdate, TaskView } from '@ontolearn/contracts'

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
      if (['succeeded', 'failed', 'cancelled'].includes(update.job.state)) resolveJob(update.job)
    },
    stop: () => clearTimeout(timer),
  }
}
async function runtime(
  capability: 'test.rounds' | 'test.read' | 'test.atomic',
  parameters: Record<string, unknown>,
  dropFirstState = false,
  coalesceAtomicCompletion = false,
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
    let dropped: Notification | undefined
    let jobId = ''
    let forward: ((value: unknown) => void) | undefined
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
      onNotification(listener: (event: unknown) => void) {
        forward = listener
        return supervisor.onNotification((value) => {
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
      if ('restoredView' in update)
        views.push((update as TaskUpdate & { restoredView: TaskView }).restoredView)
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
          waiting.observe({ generation: restored.data.generation, job: current })
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
        dropped,
        calls,
        views,
        operation,
        initial: restored,
        heldAtomic,
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

describe('actual Python → supervisor → task service runtime', () => {
  it('recovers one omitted real state notification through a durable read and fresh subscription', async () => {
    const result = await runtime('test.rounds', { workMs: 200, maxRounds: 3 }, true)
    expect(result.terminal.state).toBe('succeeded')
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
    const later = result.received.find(
      (event) =>
        event.subscriptionId === result.dropped!.subscriptionId && event.seq > result.dropped!.seq,
    )
    expect(later).toBeDefined()
    expect(
      new Set(result.received.map((event) => event.subscriptionId)).size,
    ).toBeGreaterThanOrEqual(2)
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
