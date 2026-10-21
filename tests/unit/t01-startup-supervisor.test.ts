import { afterEach, describe, expect, it, vi } from 'vitest'
import { EventEmitter } from 'node:events'
import { PassThrough } from 'node:stream'
import { createHash, randomUUID } from 'node:crypto'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import {
  EngineError,
  EngineSupervisor,
  getEngineCommand,
  type EngineConnectionState,
  type SupervisorOptions,
} from '../../apps/desktop/src/main/engine'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { explainError } from '../../apps/desktop/src/renderer/src/task-presentation'
import { isTaskUpdate, type TaskUpdate } from '@ontolearn/contracts'
import { v2Registry } from '@ontolearn/contracts/v2'

// This one controlled transport injection delivers stdout before 'spawn', so no hello pending exists.
// All other cases delegate to the actual OS spawn; this is not native/process evidence.
const controlled = vi.hoisted(() => ({ child: undefined as object | undefined }))
vi.mock('node:child_process', async (importOriginal) => {
  const actual = await importOriginal<typeof import('node:child_process')>()
  return {
    ...actual,
    spawn: (...args: unknown[]) => {
      if (controlled.child) {
        const child = controlled.child
        controlled.child = undefined
        return child
      }
      return Reflect.apply(actual.spawn, undefined, args)
    },
  }
})
const location = { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: '' }
const registryPath = resolve('packages/contracts/v2/registry.json')
const hash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const expected = {
  code: 'PROJECT_FORMAT_UNSUPPORTED',
  messageKey: 'project.formatUnsupported',
  params: { supportedFormats: [3] },
  retryable: false,
}
const limits = {
  startupMs: 1000,
  handshakeMs: 1000,
  requestMs: 1000,
  totalMs: 10000,
  heartbeatMs: 1000,
  cancelGraceMs: 1000,
  maxFrameBytes: 262144,
  maxQueuedJobs: 32,
  maxConcurrentJobs: 2,
  maxPageItems: 100,
  maxPageBytes: 131072,
  maxWorkerMemoryBytes: 536870912,
}
const childScript = String.raw`
const {createInterface}=require('node:readline'),{randomUUID}=require('node:crypto'),fs=require('node:fs');
let [mode,hash,limits,caps,marker]=process.argv.slice(1);limits=JSON.parse(limits);caps=JSON.parse(caps);
if(marker){let n=0;try{n=Number(fs.readFileSync(marker))}catch{}fs.writeFileSync(marker,String(n+1));if(n)mode='normal';}
const session=randomUUID(),error={code:'PROJECT_FORMAT_UNSUPPORTED',messageKey:'project.formatUnsupported',params:{supportedFormats:[3]},retryable:false};
const failure=JSON.stringify({kind:'startupFailure',diagnosticVersion:1,engineSessionId:null,registryHash:hash,error});
const wire=q=>JSON.stringify({kind:'response',protocolVersion:2,id:q.id,method:'hello',engineSessionId:session,ok:true,result:{selectedVersion:3,engineVersion:'0.1.0',engineSessionId:session,capabilities:caps,limits,registryHash:mode==='badhash'?'0'.repeat(64):hash}})+'\n';
createInterface({input:process.stdin}).on('line',line=>{const q=JSON.parse(line);
if(q.method==='hello'){
 if(mode==='failure'||mode==='once')return process.stdout.write(failure+'\n'+wire(q));
 if(mode==='spaces')return process.stdout.write(' '.repeat(2000)+failure+'\n'+wire(q));
 if(mode==='over')return process.stdout.write(' '.repeat(1025-Buffer.byteLength(failure))+failure+'\n'+wire(q));
 if(mode==='badprofile')return process.stdout.write(failure+'\n');
 if(mode==='incompatible')return process.stdout.write(JSON.stringify({kind:'response',protocolVersion:2,id:q.id,method:'hello',engineSessionId:null,ok:false,error:{code:'VERSION_INCOMPATIBLE',messageKey:'protocol.versionIncompatible',params:{supportedVersions:[3]},retryable:false}})+'\n');
 if(mode==='ready-failure')return process.stdout.write(wire(q)+failure+'\n'+wire(q));
 process.stdout.write(wire(q));return;
}
const result=q.method==='session.ping'?{nonce:q.params.nonce}:{status:'ok',engineVersion:'0.1.0'};
if(mode==='wrong-notification'){const n={kind:'notification',protocolVersion:3,engineSessionId:randomUUID(),subscriptionId:randomUUID(),projectId:randomUUID(),jobId:randomUUID(),seq:1,event:'job.progress',data:{stateVersion:1,progress:{stage:'computing',completed:0,total:1}}};return process.stdout.write(JSON.stringify(n)+'\n'+JSON.stringify({kind:'response',protocolVersion:3,id:q.id,method:q.method,engineSessionId:session,ok:true,result})+'\n');}
if(mode==='business-format')return process.stdout.write(JSON.stringify({kind:'response',protocolVersion:3,id:q.id,method:q.method,engineSessionId:session,ok:false,error})+'\n');
process.stdout.write(JSON.stringify({kind:'response',protocolVersion:3,id:q.id,method:q.method,engineSessionId:session,ok:true,result})+'\n');
});`
const active: EngineSupervisor[] = []
const directories: string[] = []
function directory() {
  const path = mkdtempSync(join(tmpdir(), 't01-startup-'))
  directories.push(path)
  return path
}
function fixture(mode = 'normal', options: SupervisorOptions = {}, marker = '') {
  const engine = new EngineSupervisor(location, {
    profile: 'business3',
    registryPath,
    startupMs: 1500,
    handshakeMs: 1000,
    requestMs: 1000,
    heartbeatMs: 1000,
    command: {
      command: process.execPath,
      args: [
        '-e',
        childScript,
        mode,
        hash,
        JSON.stringify(limits),
        JSON.stringify(v2Registry.foundationProfiles.business3.methods),
        marker,
      ],
    },
    ...options,
  })
  active.push(engine)
  return engine
}
async function caught(promise: Promise<unknown>) {
  try {
    await promise
    throw new Error('expected rejection')
  } catch (error) {
    return error
  }
}
function python(script: string, args: string[] = []) {
  const r = spawnSync(getEngineCommand(location).command, ['-I', '-c', script, ...args], {
    encoding: 'utf8',
    timeout: 10000,
  })
  expect(r.error).toBeUndefined()
  expect(r.status, r.stderr).toBe(0)
  return r.stdout.trim()
}
afterEach(() => {
  for (const engine of active.splice(0)) engine.stop()
  for (const path of directories.splice(0)) rmSync(path, { recursive: true, force: true })
})

describe('startup actual stdio, private provenance and complete error projection', () => {
  it('settles the explicit startup promise with no hello pending, retaining first cause through EOF/close', async () => {
    const fake = Object.assign(new EventEmitter(), {
      stdout: new PassThrough(),
      stderr: new PassThrough(),
      stdin: new PassThrough(),
      exitCode: null,
      signalCode: null,
      kill: () => {
        queueMicrotask(() => fake.emit('close', 1))
        return true
      },
    })
    let written = 0
    fake.stdin.on('data', (bytes: Buffer) => {
      written += bytes.length
    })
    controlled.child = fake
    const engine = fixture()
    const events: EngineConnectionState[] = []
    engine.onConnectionState((event) => events.push(event))
    const operation = engine.health()
    queueMicrotask(() => {
      fake.stdout.write(
        JSON.stringify({
          kind: 'startupFailure',
          diagnosticVersion: 1,
          engineSessionId: null,
          registryHash: hash,
          error: expected,
        }) + '\n',
      )
      fake.stdout.end()
      fake.emit('spawn')
    })
    const cause = await caught(operation)
    expect(engine.projectFailure(cause, operation)).toEqual(expected)
    expect(written).toBe(0)
    expect(events).toEqual([])
    await new Promise((done) => setImmediate(done))
    expect(engine.projectFailure(cause, operation)).toEqual(expected)
  })
  it('terminates a strict3 wrong-session notification before the following valid response in the same chunk', async () => {
    const engine = fixture('wrong-notification')
    const events: EngineConnectionState[] = []
    const notifications: unknown[] = []
    engine.onConnectionState((event) => events.push(event))
    engine.onNotification((event) => notifications.push(event))
    const operation = engine.health()
    expect(engine.projectFailure(await caught(operation), operation).code).toBe('INVALID_REQUEST')
    expect(events.map((event) => event.state)).toEqual(['ready', 'disconnected'])
    expect(notifications).toEqual([])
    expect(engine.engineSessionId).toBeUndefined()
  })

  it.each(['failure', 'once'])(
    'locks safe first cause and stops same-chunk hello: %s',
    async (mode) => {
      const engine = fixture(mode)
      const events: EngineConnectionState[] = []
      engine.onConnectionState((e) => events.push(e))
      const operation = engine.health()
      const cause = await caught(operation)
      expect(engine.projectFailure(cause, operation)).toEqual(expected)
      expect(events).toEqual([])
      expect(engine.engineSessionId).toBeUndefined()
      await new Promise((r) => setTimeout(r, 30))
      expect(engine.projectFailure(cause, operation)).toEqual(expected)
    },
  )
  it.each(['spaces', 'over', 'badhash', 'business-format'])(
    'rejects invalid raw/binding/business diagnostic: %s',
    async (mode) => {
      const engine = fixture(mode)
      const operation = engine.health()
      const cause = await caught(operation)
      expect(engine.projectFailure(cause, operation).code).toBe('INVALID_REQUEST')
      expect(engine.engineSessionId).toBeUndefined()
    },
  )
  it('does not authorize startup diagnosis in the default2 profile', async () => {
    const engine = fixture('badprofile', { profile: 'legacy2' })
    const p = engine.health()
    expect(engine.projectFailure(await caught(p), p).code).toBe('INVALID_REQUEST')
  })
  it('keeps actual ready history and authenticates each delivered disconnection clone', async () => {
    const engine = fixture('ready-failure')
    const events: EngineConnectionState[] = []
    engine.onConnectionState((e) => events.push(e))
    const p = engine.health()
    await caught(p)
    expect(events.map((e) => e.state)).toEqual(['ready', 'disconnected'])
    const event = events[1]
    const original = engine.projectConnectionFailure(event)
    expect(original).toMatchObject({
      generation: 1,
      state: 'disconnected',
      error: { code: 'INVALID_REQUEST' },
    })
    expect(engine.projectConnectionFailure(structuredClone(event))).toBeUndefined()
    expect(fixture().projectConnectionFailure(event)).toBeUndefined()
    event.engineSessionId = randomUUID()
    expect(engine.projectConnectionFailure(event)).toEqual(original)
  })
  it('requires the original promise/object and preserves old attempt cause after a new generation', async () => {
    const engine = fixture('failure', {}, join(directory(), 'starts'))
    const first = engine.health()
    const cause = await caught(first)
    expect((await engine.health()).protocolVersion).toBe(3)
    const current = engine.engineSessionId
    expect(engine.projectFailure(cause, first)).toEqual(expected)
    expect(engine.engineSessionId).toBe(current)
    expect(engine.projectFailure(cause, Promise.resolve()).code).toBe('INTERNAL_ERROR')
    expect(engine.projectFailure(new EngineError(expected), first).code).toBe('INTERNAL_ERROR')
    expect(engine.projectFailure(structuredClone(cause), first).code).toBe('INTERNAL_ERROR')
    expect(fixture().projectFailure(cause, first).code).toBe('INTERNAL_ERROR')
    Object.defineProperty(cause, 'error', {
      value: { ...expected, params: { supportedFormats: [99] } },
    })
    expect(engine.projectFailure(cause, first)).toEqual(expected)
    expect(
      Object.keys(engine).some((k) => /origins|operations|connections|session|sign/.test(k)),
    ).toBe(false)
  })
  it('carries the real startup rejection through TaskService and the final explanation', async () => {
    const engine = fixture('failure')
    const tasks = new TaskService(engine)
    tasks.selectProject(randomUUID())
    try {
      const result = await tasks.restore()
      expect(result).toEqual({ ok: false, error: expected })
      if (!result.ok) expect(explainError(result.error, 'task').what).toBe('项目格式暂不受支持。')
    } finally {
      tasks.dispose()
    }
  })
  it('fences an original TaskService rejection when its project changes before catch', async () => {
    const engine = fixture('failure', {}, join(directory(), 'attempts'))
    const tasks = new TaskService(engine)
    tasks.selectProject(randomUUID())
    const nextProject = randomUUID()
    const actualRequest = engine.request.bind(engine)
    const intercepted = vi.spyOn(engine, 'request').mockImplementation((method, params) => {
      const operation = actualRequest(method, params)
      void operation.catch(() => tasks.selectProject(nextProject))
      return operation // The authentic original promise is preserved; only view timing is injected.
    })
    try {
      expect(await tasks.restore()).toMatchObject({
        ok: false,
        error: { code: 'PERMISSION_DENIED' },
      })
      intercepted.mockRestore()
      expect((await engine.health()).protocolVersion).toBe(3)
    } finally {
      intercepted.mockRestore()
      tasks.dispose()
    }
  })
  it('preserves an authenticated3 job.get failure across nested subscription and restore guards', async () => {
    const database = join(directory(), 'nested.sqlite')
    const project = python(
      'from ontolearn_engine.job_store import JobStore;from ontolearn_engine.resources import CONTRACT;from uuid import uuid4;import sys;p=str(uuid4());s=JobStore(sys.argv[1],contract=CONTRACT,target_format=3);s.create_project(p);s.close();print(p)',
      [database],
    )
    const script = String.raw`
import runpy
from ontolearn_engine.coordinator import Coordinator,ServiceFault
original=Coordinator.dispatch
def dispatch(self,method,params):
 if method=='job.get': raise ServiceFault('VERSION_INCOMPATIBLE',{'supportedVersions':[3]})
 return original(self,method,params)
Coordinator.dispatch=dispatch
runpy.run_module('ontolearn_engine',run_name='__main__')
`
    const engine = new EngineSupervisor(location, {
      profile: 'business3',
      registryPath,
      dataPath: database,
      allowedProjects: [project],
      command: { command: getEngineCommand(location).command, args: ['-I', '-c', script] },
    })
    active.push(engine)
    const tasks = new TaskService(engine)
    const rememberedJob = randomUUID()
    tasks.selectProject(project, [rememberedJob])
    try {
      expect(await tasks.restore()).toEqual({
        ok: false,
        error: {
          code: 'VERSION_INCOMPATIBLE',
          messageKey: 'protocol.versionIncompatible',
          params: { supportedVersions: [3] },
          retryable: false,
        },
      })
      const subscription = tasks.subscribeJob(rememberedJob)
      const original = await subscription
      expect(original).toMatchObject({ ok: false, error: { code: 'VERSION_INCOMPATIBLE' } })
      const substitute = vi.spyOn(tasks, 'subscribeJob')
      try {
        substitute.mockImplementation(() => Promise.resolve(structuredClone(original)))
        expect(await tasks.restore()).toMatchObject({
          ok: false,
          error: { code: 'INTERNAL_ERROR' },
        })
        substitute.mockImplementation(() => Promise.resolve(original))
        expect(await tasks.restore()).toMatchObject({
          ok: false,
          error: { code: 'INTERNAL_ERROR' },
        })
      } finally {
        substitute.mockRestore()
      }
    } finally {
      tasks.dispose()
    }
  })
  it('legacy wrappers cannot give a new-format error startup authority', async () => {
    const engine = fixture('failure')
    const tasks = new TaskService({
      request: async (m, p) => engine.request(m, p),
      get engineSessionId() {
        return engine.engineSessionId
      },
      onNotification: (fn) => engine.onNotification(fn),
      onConnectionState: (fn) => engine.onConnectionState(fn),
    })
    tasks.selectProject(randomUUID())
    try {
      const result = await tasks.restore()
      expect(result).toMatchObject({ ok: false, error: { code: 'INTERNAL_ERROR' } })
    } finally {
      tasks.dispose()
    }
  })
  it('projects the exact terminating [3] bootstrap incompatibility to a legacy2 caller', async () => {
    const engine = fixture('incompatible', { profile: 'legacy2' })
    const p = engine.health()
    const cause = await caught(p)
    expect(engine.projectFailure(cause, p)).toEqual({
      code: 'VERSION_INCOMPATIBLE',
      messageKey: 'protocol.versionIncompatible',
      params: { supportedVersions: [3] },
      retryable: false,
    })
    expect(engine.engineSessionId).toBeUndefined()
  })
  it('real Python default2 and explicit3 negotiate; mismatched engines terminate without fallback', async () => {
    for (const profile of ['legacy2', 'business3'] as const) {
      const engine = new EngineSupervisor(location, {
        profile,
        dataPath: join(directory(), 'db.sqlite'),
        registryPath,
      })
      active.push(engine)
      expect((await engine.health()).protocolVersion).toBe(profile === 'business3' ? 3 : 2)
    }
    const command = getEngineCommand(location)
    // Explicit engine3 versus legacy2 app; a real, empty private DB is migrated by the actual constructor.
    const oldApp = new EngineSupervisor(location, {
      registryPath,
      dataPath: join(directory(), 'db.sqlite'),
      command: {
        command: command.command,
        args: [...command.args, '--t01-internal-profile=business3'],
      },
    })
    active.push(oldApp)
    const p = oldApp.health()
    expect(oldApp.projectFailure(await caught(p), p)).toMatchObject({
      code: 'VERSION_INCOMPATIBLE',
      params: { supportedVersions: [3] },
    })
    // A trusted harness intentionally chooses a legacy engine; ignore app's appended argv in this fixed script.
    const newApp = new EngineSupervisor(location, {
      profile: 'business3',
      registryPath,
      dataPath: join(directory(), 'db.sqlite'),
      command: {
        command: command.command,
        args: [
          '-I',
          '-c',
          'from ontolearn_engine.coordinator import serve;import asyncio;asyncio.run(serve())',
        ],
      },
    })
    active.push(newApp)
    const q = newApp.health()
    expect(newApp.projectFailure(await caught(q), q)).toMatchObject({
      code: 'VERSION_INCOMPATIBLE',
      params: { supportedVersions: [2] },
    })
  }, 20000)
  it('real future SQLite typed cause reaches a bridge-safe fixed message', async () => {
    const database = join(directory(), 'future.sqlite')
    python(
      'import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);c.execute("PRAGMA user_version=4");c.close()',
      [database],
    )
    const engine = new EngineSupervisor(location, {
      profile: 'business3',
      registryPath,
      dataPath: database,
    })
    active.push(engine)
    const tasks = new TaskService(engine)
    tasks.selectProject(randomUUID())
    try {
      const result = await tasks.restore()
      expect(result).toEqual({ ok: false, error: expected })
      expect(
        python(
          'import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute("PRAGMA user_version").fetchone()[0])',
          [database],
        ),
      ).toBe('4')
    } finally {
      tasks.dispose()
    }
  })
  it('runs a real3 atomic Job through TaskService events, immutable results and one receipt across restart', async () => {
    const database = join(directory(), 'job.sqlite')
    const fixtureData = JSON.parse(
      python(
        String.raw`
import json,sys
from uuid import uuid4
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
project=str(uuid4());store=JobStore(sys.argv[1],contract=CONTRACT,target_format=3)
try:
 store.create_project(project);snapshot=store.project_get(project);parameters=store.put_blob(project,{'workMs':500})
 prepared=store.prepare_plan(project,snapshot['projectRevision'],{'definitions':[{'layer':'rule','id':'node3-atomic','value':{'enabled':True}}]},actor=str(uuid4()),permission='write')
 print(json.dumps({'projectId':project,'operationId':str(uuid4()),'capability':'test.atomic','input':{'inputSnapshotId':snapshot['inputSnapshotId'],'scope':'asserted','definitionId':'probe','parametersHash':parameters,'derivedResultIds':[],'preparedPlanRef':prepared['preparedPlanRef']},'confirmationRef':prepared['confirmationRef']}))
finally: store.close()
`,
        [database],
      ),
    ) as Record<string, unknown> & { projectId: string; operationId: string }
    const pidMarker = join(directory(), 'owned-coordinator.pid')
    const options: SupervisorOptions = {
      profile: 'business3',
      registryPath,
      command: {
        command: getEngineCommand(location).command,
        args: [
          '-I',
          '-c',
          `import os,pathlib,runpy;pathlib.Path(${JSON.stringify(pidMarker)}).write_text(str(os.getpid()));runpy.run_module('ontolearn_engine',run_name='__main__')`,
        ],
      },
      dataPath: database,
      allowedProjects: [fixtureData.projectId],
      testMode: true,
    }
    const engine = new EngineSupervisor(location, options)
    active.push(engine)
    const tasks = new TaskService(engine)
    tasks.selectProject(fixtureData.projectId)
    const updates: TaskUpdate[] = []
    const recoverySession: { value?: string } = {}
    let finishRecovery: ((value: TaskUpdate) => void) | undefined
    tasks.attachView((value) => {
      expect(isTaskUpdate(value)).toBe(true)
      updates.push(value)
      if (
        value.kind === 'restored' &&
        recoverySession.value &&
        engine.engineSessionId !== recoverySession.value
      )
        finishRecovery?.(value)
    })
    const before = await tasks.restore()
    expect(before).toMatchObject({
      ok: true,
      data: { project: { formatVersion: 3, projectRevision: 0 } },
    })
    const job = (await engine.request('job.create', fixtureData)) as {
      jobId: string
      state: string
      resultRef: { resultId: string } | null
    }
    const subscribed = await tasks.subscribeJob(job.jobId)
    expect(subscribed).toMatchObject({ ok: true, data: { jobId: job.jobId } })
    if (subscribed.ok) expect(['queued', 'running']).toContain(subscribed.data.state)
    let current = job
    const deadline = Date.now() + 8000
    while (Date.now() < deadline) {
      current = (await engine.request('job.get', {
        projectId: fixtureData.projectId,
        jobId: job.jobId,
      })) as typeof job
      if (['succeeded', 'failed', 'cancelled'].includes(current.state)) break
      await new Promise((done) => setTimeout(done, 10))
    }
    expect(current.state).toBe('succeeded')
    expect(current.resultRef).not.toBeNull()
    expect(await engine.request('job.create', fixtureData)).toMatchObject({
      jobId: job.jobId,
      state: 'succeeded',
    })
    const restored = await tasks.restore()
    expect(restored).toMatchObject({
      ok: true,
      data: {
        project: { formatVersion: 3, projectRevision: 1 },
        jobs: [{ jobId: job.jobId, state: 'succeeded' }],
      },
    })
    expect(await tasks.getResult(current.resultRef!.resultId)).toMatchObject({
      ok: true,
      data: { resultId: current.resultRef!.resultId },
    })
    expect(await tasks.getOperation(fixtureData.operationId)).toMatchObject({
      ok: true,
      data: { jobId: job.jobId },
    })
    expect(updates.length).toBeGreaterThan(0)
    recoverySession.value = engine.engineSessionId
    const recovered = new Promise<TaskUpdate>((done, fail) => {
      const timer = setTimeout(
        () => fail(new Error('actual coordinator recovery did not complete')),
        8000,
      )
      finishRecovery = (value) => {
        clearTimeout(timer)
        done(value)
      }
    })
    const ownedPid = Number(readFileSync(pidMarker, 'utf8'))
    expect(Number.isSafeInteger(ownedPid) && ownedPid > 1).toBe(true)
    process.kill(ownedPid, 'SIGTERM') // Only this test's just-launched Python coordinator.
    expect(await recovered).toMatchObject({
      kind: 'restored',
      view: {
        project: { formatVersion: 3, projectRevision: 1 },
        jobs: [{ jobId: job.jobId, state: 'succeeded' }],
      },
    })
    expect(
      updates.some((value) => value.kind === 'connection' && value.state === 'reconnecting'),
    ).toBe(true)
    expect(engine.engineSessionId).not.toBe(recoverySession.value)
    expect(await tasks.getOperation(fixtureData.operationId)).toMatchObject({
      ok: true,
      data: { jobId: job.jobId },
    })
    tasks.dispose()
    engine.stop()
    // Observe the original process's actual OS lease release, without killing any other process.
    expect(
      python(
        String.raw`
import time,sys
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
for _ in range(300):
 try: s=JobStore(sys.argv[1],contract=CONTRACT,target_format=3);s.close();print('released');break
 except ValueError: time.sleep(.01)
else: raise RuntimeError('lease did not release')
`,
        [database],
      ),
    ).toBe('released')
    const second = new EngineSupervisor(location, options)
    active.push(second)
    expect(
      await second.request('operation.get', {
        projectId: fixtureData.projectId,
        operationId: fixtureData.operationId,
      }),
    ).toMatchObject({ jobId: job.jobId })
    expect(await second.request('job.create', fixtureData)).toMatchObject({
      jobId: job.jobId,
      state: 'succeeded',
    })
    expect(
      python(
        "import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);print(c.execute('SELECT count(*) FROM operation_claims WHERE operation=?',(sys.argv[2],)).fetchone()[0]);c.close()",
        [database, fixtureData.operationId],
      ),
    ).toBe('1')
  }, 20000)
  it('keeps TaskUpdate finite filtering independent from runtime authorization', () => {
    expect(
      isTaskUpdate({
        kind: 'connection',
        generation: 1,
        projectId: randomUUID(),
        state: 'offline',
        attempt: 3,
        error: expected,
      }),
    ).toBe(true)
  })
})
