import { createHash } from 'node:crypto'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { tmpdir } from 'node:os'
import { afterEach, describe, expect, it } from 'vitest'
import {
  EngineSupervisor,
  type EngineConnectionState,
  type SupervisorOptions,
} from '../../apps/desktop/src/main/engine'
import { validateV2, v2Registry } from '@ontolearn/contracts/v2'

const registryPath = resolve('packages/contracts/v2/registry.json')
const hash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const limits = {
  startupMs: 1000,
  handshakeMs: 1000,
  requestMs: 1000,
  heartbeatMs: 1000,
  totalMs: 2000,
  cancelGraceMs: 1000,
  maxFrameBytes: 262144,
  maxQueuedJobs: 32,
  maxConcurrentJobs: 2,
  maxPageItems: 100,
  maxPageBytes: 131072,
  maxWorkerMemoryBytes: 536870912,
}
const script = `
const fs=require('node:fs'),{createInterface}=require('node:readline'),{randomUUID}=require('node:crypto');
const [mode,hash,limitsRaw,capsRaw,marker]=process.argv.slice(1);
fs.appendFileSync(marker,process.pid+'\\n');
const session=randomUUID();
function output(q,result,extra={}) {process.stdout.write(JSON.stringify({kind:'response',protocolVersion:2,engineSessionId:session,id:q.id,method:q.method,ok:true,result,...extra})+'\\n')}
createInterface({input:process.stdin}).on('line',raw=>{
const q=JSON.parse(raw);
if(q.method==='hello') {
 if(mode==='nohello') return;
 output(q,{selectedVersion:2,engineVersion:'0.1.0',engineSessionId:session,capabilities:JSON.parse(capsRaw),registryHash:mode==='badhash'?'0'.repeat(64):hash,limits:JSON.parse(limitsRaw)});return;
}
if(q.method==='session.ping') return output(q,{nonce:q.params.nonce});
if(mode==='hang') return;
if(mode==='business') return output(q,undefined,{ok:false,error:{code:'STORAGE_BUSY',messageKey:'storage.busy',params:{retryAfterMs:10},retryable:true}});
output(q,{status:'ok',engineVersion:'0.1.0'});
if(mode==='exit') setTimeout(()=>process.exit(11),10);
if(mode==='invalid') setTimeout(()=>process.stdout.write('{"bad":1,"bad":2}\\n'),10);
});
`
const active: EngineSupervisor[] = []
const directories: string[] = []
function create(mode = 'normal', options: SupervisorOptions = {}) {
  const directory = mkdtempSync(join(tmpdir(), 'i04-connection-'))
  directories.push(directory)
  const marker = join(directory, 'starts')
  const engine = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: '' },
    {
      registryPath,
      startupMs: 1000,
      handshakeMs: 200,
      requestMs: 200,
      heartbeatMs: 1000,
      command: {
        command: process.execPath,
        args: [
          '-e',
          script,
          mode,
          hash,
          JSON.stringify(limits),
          JSON.stringify(v2Registry.v2Runtime),
          marker,
        ],
      },
      ...options,
    },
  )
  active.push(engine)
  return { engine, starts: () => readFileSync(marker, 'utf8').trim().split('\n') }
}
function deferred<T>() {
  let resolveValue!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolveValue = done
  })
  return { promise, resolve: resolveValue }
}
afterEach(() => {
  for (const engine of active.splice(0)) engine.stop()
  for (const directory of directories.splice(0)) rmSync(directory, { recursive: true, force: true })
})

describe('engine connection lifecycle', () => {
  it('announces ready once for negotiated identity and preserves health process reuse', async () => {
    const { engine, starts } = create()
    const events: EngineConnectionState[] = []
    engine.onConnectionState((event) => events.push(event))
    await engine.health()
    await engine.health()
    expect(events).toEqual([
      { state: 'ready', generation: 1, engineSessionId: engine.engineSessionId },
    ])
    expect(starts()).toHaveLength(1)
  })
  it('announces a safe disconnection once and reconnects only upon explicit caller request', async () => {
    const { engine, starts } = create('exit')
    const events: EngineConnectionState[] = []
    const disconnected = deferred<EngineConnectionState>()
    engine.onConnectionState((event) => {
      events.push(event)
      if (event.state === 'disconnected') disconnected.resolve(event)
    })
    await engine.health()
    const first = events[0]
    const failed = await disconnected.promise
    expect(failed).toMatchObject({
      state: 'disconnected',
      generation: first.generation,
      engineSessionId: first.engineSessionId,
      error: { code: 'ENGINE_EXITED', messageKey: 'engine.exited', params: {}, retryable: true },
    })
    if (failed.state === 'disconnected') expect(validateV2('error', failed.error)).toBe(true)
    expect(engine.engineSessionId).toBeUndefined()
    await new Promise<void>((done) => setTimeout(done, 150))
    expect(events.map((event) => event.state)).toEqual(['ready', 'disconnected'])
    expect(starts()).toHaveLength(1)
    await engine.health()
    const next = events.find(
      (event) => event.state === 'ready' && event.generation > first.generation,
    )!
    expect(next).toBeDefined()
    expect(next.engineSessionId).not.toBe(first.engineSessionId)
    expect(starts()).toHaveLength(2)
    engine.stop()
  })
  it('reports protocol failure with original generation after successful negotiation', async () => {
    const { engine } = create('invalid')
    const disconnected = deferred<EngineConnectionState>()
    engine.onConnectionState((event) => {
      if (event.state === 'disconnected') disconnected.resolve(event)
    })
    await engine.health()
    const identity = engine.engineSessionId
    expect(await disconnected.promise).toEqual({
      state: 'disconnected',
      generation: 1,
      engineSessionId: identity,
      error: {
        code: 'INVALID_REQUEST',
        messageKey: 'protocol.invalidRequest',
        params: { field: 'envelope' },
        retryable: false,
      },
    })
  })
  it.each(['badhash', 'nohello'])(
    'does not fabricate a negotiated session on %s bootstrap failure',
    async (mode) => {
      const { engine } = create(mode, { handshakeMs: mode === 'nohello' ? 25 : 200 })
      const events: EngineConnectionState[] = []
      engine.onConnectionState((event) => events.push(event))
      await expect(engine.health()).rejects.toHaveProperty('error')
      expect(events).toEqual([])
      expect(engine.engineSessionId).toBeUndefined()
    },
  )
  it('does not report connection failure for one timed-out request or safe business error', async () => {
    for (const mode of ['hang', 'business']) {
      const { engine } = create(mode, { requestMs: 20 })
      const events: EngineConnectionState[] = []
      engine.onConnectionState((event) => events.push(event))
      await expect(engine.health()).rejects.toHaveProperty('error')
      expect(events.map((event) => event.state)).toEqual(['ready'])
      engine.stop()
    }
  })
  it('intentional stop is silent and prevents further process starts', async () => {
    const { engine, starts } = create()
    const events: EngineConnectionState[] = []
    engine.onConnectionState((event) => events.push(event))
    await engine.health()
    engine.stop()
    engine.stop()
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
    await new Promise<void>((done) => setTimeout(done, 30))
    expect(events.map((event) => event.state)).toEqual(['ready'])
    expect(starts()).toHaveLength(1)
  })
  it('supports unsubscribe, does not replay, and isolates listeners and their mutations', async () => {
    const diagnostics: string[] = []
    const { engine } = create('exit', { onDiagnostic: (event) => diagnostics.push(event) })
    const removed: EngineConnectionState[] = []
    engine.onConnectionState((event) => removed.push(event))()
    const events: EngineConnectionState[] = []
    engine.onConnectionState((event) => {
      event.engineSessionId = 'mutated'
      throw new Error('private listener text')
    })
    const disconnected = deferred<EngineConnectionState>()
    engine.onConnectionState((event) => {
      events.push(event)
      if (event.state === 'disconnected') disconnected.resolve(event)
    })
    await engine.health()
    const late: EngineConnectionState[] = []
    const unsubscribe = engine.onConnectionState((event) => late.push(event))
    expect(late).toEqual([])
    unsubscribe()
    await disconnected.promise
    expect(removed).toEqual([])
    expect(late).toEqual([])
    expect(events.every((event) => event.engineSessionId !== 'mutated')).toBe(true)
    expect(diagnostics).toEqual(['listenerFailed', 'listenerFailed'])
  })
})
