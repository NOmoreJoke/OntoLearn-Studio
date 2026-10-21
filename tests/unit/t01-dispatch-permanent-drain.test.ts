import { afterEach, describe, expect, it, vi } from 'vitest'
import { createHash, randomUUID } from 'node:crypto'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { EventEmitter } from 'node:events'
import { PassThrough } from 'node:stream'
import type { ChildProcess } from 'node:child_process'
import { EngineSupervisor, type SupervisorOptions } from '../../apps/desktop/src/main/engine'
import {
  ChildOwnership,
  DispatchAccounting,
  LifecycleFault,
  ownJson,
  type CompletionPort,
  type DispatchFacts,
  type DispatchSource,
  type ExecutionEvidenceProducer,
  type SessionFacts,
  type TerminalJobFact,
  type Ticket,
} from '../../apps/desktop/src/main/engine-lifecycle'
import { validateBusiness3, v2Registry } from '@ontolearn/contracts/v2'

// Three write-outcome injections are logic evidence only; all other spawn calls are real.
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
const fixtures = JSON.parse(readFileSync(resolve('packages/contracts/v2/fixtures.json'), 'utf8'))
  .cases as Array<{ valid: boolean; name: string; value: Record<string, unknown> }>
const jobTemplate = fixtures.find((c) => c.name === 'response job.create' && c.valid)!.value.result
const createTemplate = fixtures.find((c) => c.name === 'request job.create' && c.valid)!.value
  .params as Record<string, unknown>
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
// Real Node child and OS pipes; no Python Store, model, GUI or real issuer is involved.
const script = String.raw`
const {createInterface}=require('node:readline'),{randomUUID}=require('node:crypto'),fs=require('node:fs');
const [mode,hash,rawLimits,caps,marker,template]=process.argv.slice(1),limits=JSON.parse(rawLimits),session=randomUUID(),jobs=new Map();
const incarnation=fs.existsSync(marker)?fs.readFileSync(marker,'utf8').split('\"spawn\"').length:1;
fs.appendFileSync(marker,JSON.stringify({spawn:process.pid})+'\n');
if(mode==='ignore-term'||mode==='end-holder'||(mode.startsWith('cap-')&&incarnation===1))process.on('SIGTERM',()=>fs.appendFileSync(marker,JSON.stringify({signal:'TERM'})+'\n'));
const response=(q,result)=>{fs.appendFileSync(marker,JSON.stringify({reply:q.method,id:q.id})+'\n');process.stdout.write(JSON.stringify({kind:'response',protocolVersion:q.method==='hello'?2:3,engineSessionId:session,id:q.id,method:q.method,ok:true,result})+'\n')};
createInterface({input:process.stdin}).on('line',line=>{
 const q=JSON.parse(line);fs.appendFileSync(marker,JSON.stringify({request:q.method,id:q.id,params:q.params})+'\n');
 if(q.method==='hello'){if(mode==='cap-hello'&&incarnation===1)return;const run=()=>response(q,{selectedVersion:3,engineVersion:'0.1.0',engineSessionId:session,capabilities:JSON.parse(caps),limits,registryHash:hash});if(mode==='slow-hello'||(mode==='cap-reconnect'&&incarnation>1))setTimeout(run,120);else run();return;}
 if(q.method==='session.ping'){if(mode==='cap-reconnect'&&incarnation===1)return;response(q,{nonce:q.params.nonce});return;}
 if(q.method==='health'){
  if(mode==='hold')return;
  const run=()=>response(q,{status:'ok',engineVersion:'0.1.0'});
  if(mode==='late')setTimeout(run,120);else run();
  if(mode==='descendant'){require('node:child_process').spawn(process.execPath,['-e','setTimeout(()=>process.exit(0),450)'],{stdio:['ignore',process.stdout,process.stderr]});setTimeout(()=>process.exit(0),15);}
  if(mode==='end-holder')setTimeout(()=>process.stdout.end(),5);
  if(mode==='unmatched')setTimeout(()=>response({...q,id:randomUUID()},{status:'ok',engineVersion:'0.1.0'}),10);
  return;
 }
 if(q.method==='job.create'){
  const p=q.params,j={...JSON.parse(template),jobId:randomUUID(),projectId:p.projectId,operationId:p.operationId,capability:p.capability,input:p.input,inputSnapshotId:p.input.inputSnapshotId,scope:p.input.scope,parametersHash:p.input.parametersHash,confirmationRef:p.confirmationRef};jobs.set(j.jobId,j);if(mode==='late-create')setTimeout(()=>response(q,j),120);else response(q,j);return;
 }
 if(q.method==='job.subscribe'){if(mode==='subscriptions-full'){process.stdout.write(JSON.stringify({kind:'response',protocolVersion:3,engineSessionId:session,id:q.id,method:q.method,ok:false,error:{code:'QUEUE_FULL',messageKey:'job.queueFull',params:{retryAfterMs:100},retryable:true}})+'\n');return;}response(q,{subscriptionId:randomUUID(),projectId:q.params.projectId,jobId:q.params.jobId,stateVersion:1,seq:0});return;}
 if(q.method==='job.unsubscribe'){response(q,{subscriptionId:q.params.subscriptionId,unsubscribed:true});return;}
 if(q.method==='job.get'){if(mode==='cap-reconnect'&&incarnation===1)return;const run=()=>response(q,jobs.get(q.params.jobId));if(mode==='late-completion')setTimeout(run,120);else run();return;}
});`
const engines: EngineSupervisor[] = []
const directories: string[] = []
function fixture(mode = 'normal', options: SupervisorOptions = {}) {
  const directory = mkdtempSync(join(tmpdir(), 't01-dispatch-drain-'))
  directories.push(directory)
  const marker = join(directory, 'events.jsonl')
  const engine = new EngineSupervisor(location, {
    profile: 'business3',
    registryPath,
    requestMs: 1000,
    handshakeMs: 1000,
    startupMs: 1500,
    heartbeatMs: 1000,
    command: {
      command: process.execPath,
      args: [
        '-e',
        script,
        mode,
        hash,
        JSON.stringify(limits),
        JSON.stringify(v2Registry.foundationProfiles.business3.methods),
        marker,
        JSON.stringify(jobTemplate),
      ],
    },
    ...options,
  })
  engines.push(engine)
  const events = () => {
    try {
      return readFileSync(marker, 'utf8')
        .trim()
        .split('\n')
        .map((s) => JSON.parse(s) as Record<string, unknown>)
    } catch {
      return []
    }
  }
  return { engine, events }
}
const pause = (ms: number) => new Promise<void>((done) => setTimeout(done, ms))
async function pending(promise: Promise<unknown>, ms = 15) {
  return Promise.race([
    promise.then(
      () => 'settled',
      () => 'rejected',
    ),
    pause(ms).then(() => 'pending'),
  ])
}
function jobParams(): Record<string, unknown> & { operationId: string } {
  return { ...structuredClone(createTemplate), operationId: randomUUID() }
}

// This fixture is deliberately NOT an issuer. WeakMaps only exercise the consumer's original-object binding.
function sourceFixture(producer?: ExecutionEvidenceProducer) {
  let invalidate: () => void = () => undefined
  let current: SessionFacts | undefined
  const permits = new WeakMap<object, string>()
  const checks: DispatchFacts[] = []
  let onCheck: (() => void) | undefined
  let spawnAllowed = true
  const source: DispatchSource = {
    execution: producer,
    installInvalidationSink(_supervisor, sink) {
      invalidate = sink
    },
    checkBeforeSpawnSync() {
      if (!spawnAllowed) throw new Error('missing actual location issuer')
    },
    recordValidatedSession(facts) {
      current = facts
    },
    checkAndConsumeDispatchSync(permit, facts) {
      if (
        !current ||
        current.actualSupervisor !== facts.actualSupervisor ||
        current.actualChildOwner !== facts.actualChildOwner ||
        current.engineSessionId !== facts.engineSessionId ||
        current.generation !== facts.generation ||
        current.hostClientId !== facts.hostClientId ||
        current.profile !== facts.profile ||
        current.registryHash !== facts.registryHash ||
        current.engineVersion !== facts.engineVersion ||
        JSON.stringify(current.limits) !== JSON.stringify(facts.limits) ||
        permits.get(permit) !== facts.actualRequest.method
      )
        throw new Error('wrong original')
      permits.delete(permit)
      checks.push(facts)
      onCheck?.()
    },
    recordSessionTerminal() {
      current = undefined
    },
  }
  return {
    source,
    checks,
    mint(method = 'health') {
      const p = {}
      permits.set(p, method)
      return p
    },
    revoke() {
      invalidate()
    },
    setCheck(fn: () => void) {
      onCheck = fn
    },
    denySpawn() {
      spawnAllowed = false
    },
    setExpected(facts: SessionFacts) {
      current = facts
    },
    get session() {
      return current
    },
  }
}
function producerFixture(cleanup = true) {
  type Reservation = {
    originalRequest: Readonly<Record<string, unknown>>
    privateTicket: object
    actualSupervisor: object
    originalDispatch: object
    completionPort: CompletionPort
    bound: boolean
    cancelled: boolean
    facts?: DispatchFacts
    job?: Record<string, unknown>
    callback?: (issued: object) => void
  }
  const reservations = new Map<object, Reservation>()
  const observations = new Map<object, Reservation>()
  const terminals = new WeakMap<object, { ticket: object; fact: TerminalJobFact }>()
  const cleanups = new WeakMap<object, object>()
  const producer: ExecutionEvidenceProducer = {
    incarnation: Object.freeze({}),
    reserveOperation(facts) {
      const reservation = {}
      reservations.set(reservation, { ...facts, bound: false, cancelled: false })
      return reservation
    },
    cancelReservation(key) {
      const r = reservations.get(key)
      if (!r || r.cancelled) throw new Error('wrong reservation')
      r.cancelled = true
    },
    bindOperation(key, facts) {
      const r = reservations.get(key)
      if (
        !r ||
        r.bound ||
        r.cancelled ||
        r.originalRequest !== facts.originalRequest ||
        r.privateTicket !== facts.privateTicket ||
        r.actualSupervisor !== facts.actualSupervisor
      )
        throw new Error('wrong bind')
      r.bound = true
      r.facts = facts
      const observation = {}
      observations.set(observation, r)
      return observation
    },
    bindAcceptedJob(observation, response) {
      const r = observations.get(observation)
      if (!r || r.job) throw new Error('wrong acceptance')
      r.job = (response as { result: Record<string, unknown> }).result
    },
    observe(observation, callback) {
      const r = observations.get(observation)
      if (!r || r.callback) throw new Error('wrong observe')
      r.callback = callback
      return {
        closeObservation() {
          if (!cleanup) return Promise.resolve({})
          const issued = {}
          cleanups.set(issued, observation)
          return Promise.resolve(issued)
        },
      }
    },
    projectTerminal(issued, ticket) {
      const entry = terminals.get(issued)
      if (!entry || entry.ticket !== ticket) throw new Error('wrong terminal')
      return entry.fact
    },
    projectObservationCleanup(issued, observation) {
      if (cleanups.get(issued) !== observation) throw new Error('unknown cleanup')
      cleanups.delete(issued)
    },
  }
  return {
    producer,
    reservations,
    observations,
    first() {
      return [...observations.values()][0]!
    },
    emit(r: Reservation, overrides: Partial<TerminalJobFact> = {}) {
      const issued = {}
      terminals.set(issued, {
        ticket: r.privateTicket,
        fact: {
          operationId: String(r.job!.operationId),
          projectId: String(r.job!.projectId),
          jobId: String(r.job!.jobId),
          state: 'succeeded',
          ...overrides,
        },
      })
      r.callback!(issued)
    },
    forge(r: Reservation) {
      r.callback!({})
    },
  }
}
function trackReservations() {
  const entries: Array<{ ticket: Ticket; book: DispatchAccounting }> = []
  const samples: Array<{
    label: string
    total: number
    business: number
    completion: number
    control: number
  }> = []
  const sample = (label: string) => {
    const active = entries.map((e) => e.ticket).filter((t) => t.bytes > 0)
    const value = {
      label,
      total: active.length,
      business: active.filter((t) => t.pool === 'business').length,
      completion: active.filter((t) => t.pool === 'completion').length,
      control: active.filter((t) => t.pool === 'hello' || t.pool === 'ping').length,
    }
    samples.push(value)
    return value
  }
  const original = DispatchAccounting.prototype.reserve
  const spy = vi.spyOn(DispatchAccounting.prototype, 'reserve').mockImplementation(function (
    this: DispatchAccounting,
    ...args: Parameters<DispatchAccounting['reserve']>
  ) {
    try {
      const ticket = Reflect.apply(original, this, args) as Ticket
      entries.push({ ticket, book: this })
      sample('reserved:' + ticket.pool)
      return ticket
    } catch (error) {
      sample('rejected:' + args[4])
      throw error
    }
  })
  return {
    entries,
    samples,
    sample,
    restore() {
      spy.mockRestore()
      sample('finally-after-drain')
      const path = join(
        mkdtempSync(join(tmpdir(), 't01-dispatch-budget-evidence-')),
        'reservations.json',
      )
      writeFileSync(
        path,
        JSON.stringify(
          {
            test: expect.getState().currentTestName,
            samples,
            reservations: entries.map(({ ticket, book }) => ({
              pool: ticket.pool,
              bytes: ticket.bytes,
              attempted: ticket.attempted,
              watch: ticket.watch,
              cancelRequested: ticket.cancelRequested,
              attemptedKnownCancellation: !!ticket.attemptedCancellation,
              remaining: book.snapshot(),
            })),
          },
          null,
          2,
        ) + '\n',
      )
      console.info('T01_DISPATCH_BUDGET_EVIDENCE ' + path)
    },
    assertBounded() {
      expect(
        samples.every(
          (s) => s.total <= 130 && s.business <= 128 && s.completion <= 1 && s.control <= 1,
        ),
      ).toBe(true)
    },
  }
}
afterEach(async () => {
  for (const engine of engines.splice(0)) {
    const drain = engine.stopAndDrain()
    expect((await drain.observe({ waitMs: 2500 })).state).toBe('ended')
  }
  for (const path of directories.splice(0)) rmSync(path, { recursive: true, force: true })
})

describe('bounded owned input and synchronous entry admission', () => {
  it('rejects accessors without running them, cycles, nonfinite numbers and invalid surrogates', () => {
    let reads = 0
    const accessor = Object.defineProperty({}, 'x', {
      enumerable: true,
      get() {
        reads++
        return 'x'
      },
    })
    const cycle: Record<string, unknown> = {}
    cycle.x = cycle
    for (const input of [
      accessor,
      cycle,
      NaN,
      Infinity,
      '\ud800',
      { x: undefined },
      new Date(),
      Array(2),
    ])
      expect(() => ownJson(input)).toThrow(LifecycleFault)
    expect(reads).toBe(0)
  })
  it('budgets escaped and UTF8 bytes before stringify and copies the original once', () => {
    const original = { a: ['中文', '"\n'] }
    const owned = ownJson(original)
    expect(owned.bytes).toBe(Buffer.byteLength(JSON.stringify(original)))
    original.a[0] = 'changed'
    expect((owned.value as typeof original).a[0]).toBe('中文')
    expect(Object.isFrozen((owned.value as typeof original).a)).toBe(true)
    expect(() => ownJson('中'.repeat(90000))).toThrow(LifecycleFault)
    let nested: unknown = null
    for (let i = 0; i < 34; i++) nested = [nested]
    expect(() => ownJson(nested)).toThrow(LifecycleFault)
  })
  it('reserves all 128 first-start requests before any ensure microtask and rejects 129', async () => {
    const { engine, events } = fixture('slow-hello')
    const promises = Array.from({ length: 128 }, () => engine.health())
    const excess = engine.health()
    expect(events()).toEqual([])
    await expect(excess).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
    expect((await Promise.all(promises)).every((v) => v.status === 'ok')).toBe(true)
    expect(events().filter((e) => e.request === 'health')).toHaveLength(128)
    expect(events().filter((e) => e.spawn)).toHaveLength(1)
  })
  it('releases 260 sequential actual foreground handlers without accumulating 128 slots', async () => {
    const { engine, events } = fixture('normal', { maxPending: 1 })
    for (let i = 0; i < 260; i++) await engine.health()
    expect(events().filter((e) => e.request === 'health')).toHaveLength(260)
    expect(events().filter((e) => e.spawn)).toHaveLength(1)
  })
  it('rejects public hello and malformed/accessor requests before spawn', async () => {
    const { engine, events } = fixture()
    let reads = 0
    await expect(engine.request('hello', {})).rejects.toMatchObject({
      error: { code: 'INVALID_STATE' },
    })
    await expect(engine.request('health', { wrong: true })).rejects.toMatchObject({
      error: { code: 'INVALID_REQUEST' },
    })
    await expect(
      engine.request(
        'health',
        Object.defineProperty({}, 'x', {
          enumerable: true,
          get() {
            reads++
            return 1
          },
        }),
      ),
    ).rejects.toMatchObject({ error: { code: 'INVALID_REQUEST' } })
    expect(reads).toBe(0)
    expect(events()).toEqual([])
  })
  it('keeps written timed-out foreground capacity until its exact late response returns', async () => {
    const { engine, events } = fixture('late', { requestMs: 25, maxPending: 1 })
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
    await pause(150)
    const next = engine.health()
    await expect(next).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
    expect(events().filter((e) => e.request === 'health')).toHaveLength(2)
  })
})

describe('private dispatch source, original facts and final synchronous fence', () => {
  it('binds real hello facts, consumes once, and copies mutations before the ensure microtask', async () => {
    const { engine, events } = fixture()
    const source = sourceFixture()
    engine.attachDispatchSource(source.source)
    const permit = source.mint()
    const operation = engine.requestWithDispatch(permit, 'health', {})
    expect(operation.dispatchObservation).toBe('not-written')
    await expect(operation.logicalOutcome).resolves.toMatchObject({ status: 'ok' })
    expect(operation.dispatchObservation).toBe('write-attempted')
    await expect(operation.operationExecution).resolves.toEqual({ kind: 'foreground-returned' })
    expect(source.checks[0]).toMatchObject({
      actualSupervisor: engine,
      engineSessionId: engine.engineSessionId,
      profile: 'business3',
      registryHash: hash,
    })
    expect(source.checks[0].actualRequest.engineSessionId).toBe(engine.engineSessionId)
    expect(source.checks[0].originalRequest).toEqual({ method: 'health', params: {} })
    await expect(
      engine.requestWithDispatch(permit, 'health', {}).logicalOutcome,
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    expect(events().filter((e) => e.request === 'health')).toHaveLength(1)
  })
  it('rejects raw business and missing producer before spawn without minting a scope', async () => {
    const { engine, events } = fixture()
    const source = sourceFixture()
    engine.attachDispatchSource(source.source)
    await expect(engine.request('project.get', { projectId: randomUUID() })).rejects.toMatchObject({
      error: { code: 'INVALID_STATE' },
    })
    await expect(
      engine.requestWithDispatch(source.mint('job.create'), 'job.create', jobParams())
        .logicalOutcome,
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    expect(events()).toEqual([])
  })
  it('missing actual spawn authority yields spawn0 and write0', async () => {
    const { engine, events } = fixture()
    const source = sourceFixture()
    source.denySpawn()
    engine.attachDispatchSource(source.source)
    await expect(
      engine.requestWithDispatch(source.mint(), 'health', {}).logicalOutcome,
    ).rejects.toBeDefined()
    expect(events()).toEqual([])
  })
  it('a copied permit and a different Supervisor cannot acquire original authority', async () => {
    const a = fixture(),
      b = fixture(),
      sa = sourceFixture(),
      sb = sourceFixture()
    a.engine.attachDispatchSource(sa.source)
    b.engine.attachDispatchSource(sb.source)
    const permit = sa.mint()
    for (const [engine, p] of [
      [a.engine, { ...permit }],
      [b.engine, permit],
    ] as const)
      await expect(
        engine.requestWithDispatch(p, 'health', {}).logicalOutcome,
      ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    expect(a.events().filter((e) => e.request === 'health')).toEqual([])
    expect(b.events().filter((e) => e.request === 'health')).toEqual([])
  })
  it('rejects each original Supervisor/child/host/session/generation/profile/version/limit mismatch before write', async () => {
    const { engine, events } = fixture()
    const s = sourceFixture()
    engine.attachDispatchSource(s.source)
    await engine.health()
    const original = s.session!
    const mismatches: Partial<SessionFacts>[] = [
      { actualSupervisor: {} },
      { actualChildOwner: {} },
      { hostClientId: randomUUID() },
      { engineSessionId: randomUUID() },
      { generation: original.generation + 1 },
      { profile: 'legacy2' },
      { registryHash: '0'.repeat(64) },
      { engineVersion: 'other' },
      { limits: { requestMs: 1 } },
    ]
    for (const mismatch of mismatches) {
      s.setExpected({ ...original, ...mismatch })
      const op = engine.requestWithDispatch(s.mint(), 'health', {})
      await expect(op.logicalOutcome).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
      expect(op.dispatchObservation).toBe('not-written')
    }
    expect(events().filter((e) => e.request === 'health')).toHaveLength(1)
  })
  it('synchronous source-only revocation inside the final hook prevents every business byte', async () => {
    const { engine, events } = fixture()
    const source = sourceFixture()
    engine.attachDispatchSource(source.source)
    source.setCheck(() => source.revoke())
    const op = engine.requestWithDispatch(source.mint(), 'health', {})
    await expect(op.logicalOutcome).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
    expect(op.dispatchObservation).toBe('not-written')
    expect(events().filter((e) => e.request === 'health')).toEqual([])
  })
  it('reentrant stop inside final check prevents write, clears owned work and drains', async () => {
    const { engine, events } = fixture()
    const source = sourceFixture()
    engine.attachDispatchSource(source.source)
    source.setCheck(() => engine.stop())
    const op = engine.requestWithDispatch(source.mint(), 'health', {})
    await expect(op.logicalOutcome).rejects.toBeDefined()
    expect(op.dispatchObservation).toBe('not-written')
    expect(events().filter((e) => e.request === 'health')).toEqual([])
    await expect(engine.stopAndDrain().transportOwnershipLifetime).resolves.toEqual({
      kind: 'transport-ended',
    })
  })
  it('async-looking final checks fail closed, and reentrant public entry reserves nothing', async () => {
    const { engine, events } = fixture()
    const source = sourceFixture()
    engine.attachDispatchSource(source.source)
    let nested: Promise<unknown> | undefined
    source.setCheck(() => {
      nested = engine.health()
      void nested.catch(() => undefined)
    })
    await engine.requestWithDispatch(source.mint(), 'health', {}).logicalOutcome
    await expect(nested).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
    expect(events().filter((e) => e.request === 'health')).toHaveLength(1)
    const second = fixture()
    const bad = sourceFixture()
    bad.source.checkAndConsumeDispatchSync = (() =>
      Promise.resolve()) as unknown as DispatchSource['checkAndConsumeDispatchSync']
    second.engine.attachDispatchSource(bad.source)
    await expect(
      second.engine.requestWithDispatch(bad.mint(), 'health', {}).logicalOutcome,
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    expect(second.events().filter((e) => e.request === 'health')).toEqual([])
  })
  it('a failed attachment permanently closes business admission and cannot be replaced', async () => {
    const { engine, events } = fixture()
    expect(() => engine.attachDispatchSource({} as DispatchSource)).toThrow()
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    await expect(engine.request('project.get', { projectId: randomUUID() })).rejects.toMatchObject({
      error: { code: 'INVALID_STATE' },
    })
    expect(() => engine.attachDispatchSource(sourceFixture().source)).toThrow()
    expect(events()).toEqual([])
  })
  it('consumes the entrance copy even when original caller params mutate before hello', async () => {
    const { engine, events } = fixture('slow-hello')
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const params = jobParams(),
      expected = structuredClone(params)
    const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', params)
    params.operationId = randomUUID()
    ;(params.input as Record<string, unknown>).definitionId = 'changed'
    await op.logicalOutcome
    expect(events().find((e) => e.request === 'job.create')!.params).toEqual(expected)
    expect(p.first().originalRequest).toBe(p.first().facts!.originalRequest)
  })
  it('bounds public listener sets and permanently stops admission', async () => {
    const { engine } = fixture()
    const listeners = Array.from({ length: 64 }, () => engine.onNotification(() => undefined))
    expect(() => engine.onNotification(() => undefined)).toThrow()
    listeners[0]()
    expect(() => engine.onNotification(() => undefined)).not.toThrow()
    Array.from({ length: 64 }, () => engine.onConnectionState(() => undefined))
    expect(() => engine.onConnectionState(() => undefined)).toThrow()
    engine.stop()
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
  })
})

describe('logical outcome, Job execution and finite producer observation are different lifetimes', () => {
  it('queued acceptance and actual transport close cannot invent a terminal Job', async () => {
    const { engine } = fixture()
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await expect(op.logicalOutcome).resolves.toMatchObject({ state: 'queued' })
    expect(await pending(op.operationExecution)).toBe('pending')
    await engine.stopAndDrain().transportOwnershipLifetime
    expect(await pending(op.operationExecution)).toBe('pending')
  })
  it('requires the actual producer ticket/observation and exact Job binding before release', async () => {
    const { engine } = fixture()
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await op.logicalOutcome
    const r = p.first()
    p.forge(r)
    p.emit(r, { jobId: randomUUID() })
    expect(await pending(op.operationExecution)).toBe('pending')
    p.emit(r)
    await expect(op.operationExecution).resolves.toMatchObject({
      kind: 'terminal-job',
      job: { state: 'succeeded', jobId: r.job!.jobId },
    })
  })
  it('synchronously reserves 128 producer watches at first startup and uses the separate completion slot at full ordinary capacity', async () => {
    const { engine, events } = fixture('slow-hello')
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const ops = Array.from({ length: 128 }, () =>
      engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams()),
    )
    expect(p.reservations.size).toBe(128)
    const excess = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await expect(excess.logicalOutcome).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
    await Promise.all(ops.map((o) => o.logicalOutcome))
    expect(await pending(ops[0].operationExecution)).toBe('pending')
    const r = p.first()
    const result = await r.completionPort.request(
      r.privateTicket,
      'job.get',
      { projectId: r.job!.projectId, jobId: r.job!.jobId },
      s.mint('job.get'),
    )
    expect(result).toMatchObject({ state: 'queued' })
    expect(events().filter((e) => e.request === 'job.create')).toHaveLength(128)
    p.emit(r)
    await ops[0].operationExecution
    await pause(0)
    const accepted = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await accepted.logicalOutcome
    expect(events().filter((e) => e.request === 'job.create')).toHaveLength(129)
  })
  it('keeps a timed-out completion RPC counted and refuses arbitrary priority methods or foreign tickets', async () => {
    const { engine } = fixture('late-completion', { requestMs: 25 })
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    await engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams()).logicalOutcome
    const r = p.first()
    const params = { projectId: r.job!.projectId, jobId: r.job!.jobId }
    await expect(
      r.completionPort.request({}, 'job.get', params, s.mint('job.get')),
    ).rejects.toBeDefined()
    await expect(
      r.completionPort.request(
        r.privateTicket,
        'job.get',
        { ...params, jobId: randomUUID() },
        s.mint('job.get'),
      ),
    ).rejects.toBeDefined()
    await expect(
      r.completionPort.request(r.privateTicket, 'job.get', params, s.mint('job.get')),
    ).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
    await expect(
      r.completionPort.request(r.privateTicket, 'job.get', params, s.mint('job.get')),
    ).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
    await pause(150)
    await expect(
      r.completionPort.request(r.privateTicket, 'job.get', params, s.mint('job.get')),
    ).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
  })
  it('authenticates a late create reply without resolving the timed-out logical outcome again', async () => {
    const { engine, events } = fixture('late-create', { requestMs: 25 })
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await expect(op.logicalOutcome).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
    expect(await pending(op.operationExecution)).toBe('pending')
    await pause(140)
    const r = p.first()
    expect(r.job!.state).toBe('queued')
    p.emit(r)
    await expect(op.operationExecution).resolves.toMatchObject({ kind: 'terminal-job' })
    await expect(op.logicalOutcome).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
    expect(events().filter((e) => e.request === 'job.create')).toHaveLength(1)
  })
  it('a provider may supply original terminal evidence after transport ended, with no Store release inference', async () => {
    const { engine } = fixture()
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await op.logicalOutcome
    await engine.stopAndDrain().transportOwnershipLifetime
    expect(await pending(op.operationExecution)).toBe('pending')
    p.emit(p.first())
    await expect(op.operationExecution).resolves.toMatchObject({ kind: 'terminal-job' })
  })
  it("consumer rejects a producer that returns someone else's reservation before write", async () => {
    const { engine, events } = fixture()
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    const original = p.producer.reserveOperation.bind(p.producer)
    p.producer.reserveOperation = (facts) => {
      original(facts)
      return {}
    }
    engine.attachDispatchSource(s.source)
    const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
    await expect(op.logicalOutcome).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    expect(op.dispatchObservation).toBe('not-written')
    expect(events().filter((e) => e.request === 'job.create')).toEqual([])
  })
  it('uses actual server subscription refusal and falls back to the independent get route', async () => {
    const { engine, events } = fixture('subscriptions-full')
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    await engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams()).logicalOutcome
    const r = p.first(),
      params = { projectId: r.job!.projectId, jobId: r.job!.jobId }
    await expect(
      r.completionPort.request(r.privateTicket, 'job.subscribe', params, s.mint('job.subscribe')),
    ).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
    await expect(
      r.completionPort.request(r.privateTicket, 'job.get', params, s.mint('job.get')),
    ).resolves.toMatchObject({ state: 'queued' })
    expect(events().filter((e) => e.request === 'job.subscribe')).toHaveLength(1)
  })
  it('owns at most one subscription per original ticket and authenticates unsubscribe before reuse', async () => {
    const { engine, events } = fixture()
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    await engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams()).logicalOutcome
    const r = p.first(),
      params = { projectId: r.job!.projectId, jobId: r.job!.jobId }
    const subscription = (await r.completionPort.request(
      r.privateTicket,
      'job.subscribe',
      params,
      s.mint('job.subscribe'),
    )) as { subscriptionId: string }
    await expect(
      r.completionPort.request(r.privateTicket, 'job.subscribe', params, s.mint('job.subscribe')),
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    await expect(
      r.completionPort.request(
        r.privateTicket,
        'job.unsubscribe',
        { ...params, subscriptionId: randomUUID() },
        s.mint('job.unsubscribe'),
      ),
    ).rejects.toBeDefined()
    await expect(
      r.completionPort.request(
        r.privateTicket,
        'job.unsubscribe',
        { ...params, subscriptionId: subscription.subscriptionId },
        s.mint('job.unsubscribe'),
      ),
    ).resolves.toMatchObject({ unsubscribed: true })
    await r.completionPort.request(
      r.privateTicket,
      'job.subscribe',
      params,
      s.mint('job.subscribe'),
    )
    expect(events().filter((e) => e.request === 'job.subscribe')).toHaveLength(2)
  })
  it('retains terminal observation capacity when close returns unverified cleanup', async () => {
    const { engine } = fixture()
    const p = producerFixture(false),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    for (let i = 0; i < 128; i++) {
      const op = engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams())
      await op.logicalOutcome
      const r = [...p.observations.values()].at(-1)!
      p.emit(r)
      await op.operationExecution
    }
    await pause(0)
    await expect(
      engine.requestWithDispatch(s.mint('job.create'), 'job.create', jobParams()).logicalOutcome,
    ).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
  })
  it('does not double-create an operation or bind/cancel a different reservation', async () => {
    const { engine, events } = fixture()
    const p = producerFixture(),
      s = sourceFixture(p.producer)
    engine.attachDispatchSource(s.source)
    const params = jobParams()
    await engine.requestWithDispatch(s.mint('job.create'), 'job.create', params).logicalOutcome
    await expect(
      engine.requestWithDispatch(s.mint('job.create'), 'job.create', params).logicalOutcome,
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    const r = p.first(),
      key = [...p.reservations.keys()][0]
    expect(() => p.producer.bindOperation({}, r.facts!)).toThrow()
    expect(() => p.producer.bindOperation(key, r.facts!)).toThrow()
    expect(() => p.producer.cancelReservation({})).toThrow()
    p.producer.cancelReservation(key)
    expect(() => p.producer.cancelReservation(key)).toThrow()
    expect(events().filter((e) => e.request === 'job.create')).toHaveLength(1)
  })
})

describe('write observation remains attempted after uncertain local outcomes (logic only)', () => {
  for (const mode of ['false', 'throw', 'callback-error'] as const) {
    it(`does not replay or report not-written after write ${mode}`, async () => {
      const child = Object.assign(new EventEmitter(), {
        stdin: new PassThrough(),
        stdout: new PassThrough(),
        stderr: new PassThrough(),
        kill() {
          setImmediate(() => {
            child.emit('exit')
            child.stdin.destroy()
            child.stdout.destroy()
            child.stderr.destroy()
            setImmediate(() => child.emit('close'))
          })
          return true
        },
      })
      let writes = 0
      child.stdin.write = ((chunk: Uint8Array, callback?: (error?: Error) => void) => {
        const q = JSON.parse(Buffer.from(chunk).toString('utf8'))
        if (q.method === 'hello') {
          const session = randomUUID()
          setImmediate(() =>
            child.stdout.write(
              JSON.stringify({
                kind: 'response',
                protocolVersion: 2,
                id: q.id,
                method: 'hello',
                engineSessionId: session,
                ok: true,
                result: {
                  selectedVersion: 3,
                  engineVersion: '0.1.0',
                  engineSessionId: session,
                  capabilities: v2Registry.foundationProfiles.business3.methods,
                  limits,
                  registryHash: hash,
                },
              }) + '\n',
            ),
          )
          return true
        }
        writes++
        if (mode === 'throw') throw new Error('synthetic write throw')
        if (mode === 'callback-error')
          setImmediate(() => callback?.(new Error('synthetic write callback')))
        return false
      }) as typeof child.stdin.write
      controlled.child = child
      const { engine } = fixture('normal', { requestMs: 25 })
      const source = sourceFixture()
      engine.attachDispatchSource(source.source)
      const op = engine.requestWithDispatch(source.mint(), 'health', {})
      setImmediate(() => child.emit('spawn'))
      await expect(op.logicalOutcome).rejects.toBeDefined()
      expect(op.dispatchObservation).toBe('write-attempted')
      expect(writes).toBe(1)
      expect(await pending(op.operationExecution)).toBe('pending')
    })
  }
})

describe('cross-session control budget and reentrant producer reservation regressions', () => {
  for (const pool of ['hello', 'ping'] as const) {
    it(`shares one hello/ping control slot with ${pool} occupying the 130th reservation`, () => {
      const book = new DispatchAccounting(128),
        tickets: Ticket[] = []
      for (let i = 0; i < 128; i++) tickets.push(book.reserve({ method: 'health', params: {} }, 1))
      const completion = book.reserve(
        { method: 'job.get', params: {} },
        1,
        undefined,
        undefined,
        'completion',
      )
      tickets.push(completion)
      const control = book.reserve(
        { method: pool === 'hello' ? 'hello' : 'session.ping', params: {} },
        1,
        undefined,
        undefined,
        pool,
      )
      tickets.push(control)
      expect(tickets.filter((t) => t.bytes > 0)).toHaveLength(130)
      const other = pool === 'hello' ? 'ping' : 'hello'
      expect(() =>
        book.reserve({ method: other, params: {} }, 1, undefined, undefined, other),
      ).toThrow(LifecycleFault)
      expect(() => book.reserve({ method: 'health', params: {} }, 1)).toThrow(LifecycleFault)
      expect(() =>
        book.reserve({ method: 'job.get', params: {} }, 1, undefined, undefined, 'completion'),
      ).toThrow(LifecycleFault)
      control.attempted = true
      book.cancelUnwritten(control)
      expect(control.bytes).toBe(1)
      book.foreground(tickets[0])
      expect(tickets.filter((t) => t.bytes > 0)).toHaveLength(129)
      expect(() =>
        book.reserve({ method: other, params: {} }, 1, undefined, undefined, other),
      ).toThrow(LifecycleFault)
      book.foreground(control)
      const next = book.reserve({ method: other, params: {} }, 1, undefined, undefined, other)
      expect(completion.bytes).toBe(1)
      expect(next.bytes).toBe(1)
      expect(tickets.filter((t) => t.bytes > 0).length + 1).toBe(129)
    })
  }
  it('keeps old real ping/completion unknown, rejects new hello before spawn, then reconnects after actual old owner close', async () => {
    const { engine, events } = fixture('cap-reconnect', { requestMs: 300, heartbeatMs: 350 })
    const p = producerFixture(false),
      source = sourceFixture(p.producer)
    engine.attachDispatchSource(source.source)
    const trace = trackReservations()
    try {
      const op = engine.requestWithDispatch(source.mint('job.create'), 'job.create', jobParams())
      await op.logicalOutcome
      const r = p.first()
      await expect(
        r.completionPort.request(
          r.privateTicket,
          'job.get',
          { projectId: r.job!.projectId, jobId: r.job!.jobId },
          source.mint('job.get'),
        ),
      ).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
      p.emit(r)
      await op.operationExecution
      for (let i = 0; i < 100 && engine.engineSessionId; i++) {
        await pause(5)
        trace.sample('waiting-old-session')
      }
      expect(engine.engineSessionId).toBeUndefined()
      const oldPing = trace.entries.find((e) => e.ticket.pool === 'ping')!.ticket
      const completion = trace.entries.find((e) => e.ticket.pool === 'completion')!.ticket
      expect(oldPing.bytes).toBeGreaterThan(0)
      expect(completion.bytes).toBeGreaterThan(0)
      const requests = Array.from({ length: 128 }, () => engine.health())
      requests.forEach((p) => void p.catch(() => undefined))
      expect(trace.sample('128-waiting-before-ensure')).toMatchObject({
        total: 130,
        business: 128,
        completion: 1,
        control: 1,
      })
      await expect(engine.health()).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
      const results = await Promise.allSettled(requests)
      expect(
        results.every(
          (r) =>
            r.status === 'rejected' &&
            (r.reason as { error: { code: string } }).error.code === 'QUEUE_FULL',
        ),
      ).toBe(true)
      expect(events().filter((e) => e.spawn)).toHaveLength(1)
      expect(oldPing.bytes).toBeGreaterThan(0)
      expect(completion.bytes).toBeGreaterThan(0)
      for (let i = 0; i < 300 && oldPing.bytes > 0; i++) {
        await pause(5)
        trace.sample('waiting-real-owner-close')
      }
      expect(oldPing.bytes).toBe(0)
      expect(completion.bytes).toBeGreaterThan(0)
      const recovered = Array.from({ length: 128 }, () => engine.health())
      const recoveredOutcomes = await Promise.allSettled(recovered)
      expect(
        recoveredOutcomes.every((outcome) =>
          outcome.status === 'fulfilled'
            ? outcome.value.status === 'ok'
            : (outcome.reason as { error?: { code?: string } }).error?.code === 'TIMEOUT',
        ),
      ).toBe(true)
      // Capacity is the requirement; a 128-frame batch is not a latency benchmark.
      // Exact late responses must still close every original foreground ticket.
      for (let i = 0; i < 400 && trace.sample('waiting-recovered-foreground').business > 0; i++)
        await pause(5)
      expect(trace.sample('recovered-foreground-returned').business).toBe(0)
      await expect(engine.health()).resolves.toMatchObject({ status: 'ok' })
      expect(events().filter((e) => e.spawn)).toHaveLength(2)
      expect(trace.samples.some((s) => s.total === 130)).toBe(true)
      expect(completion.bytes).toBeGreaterThan(0)
      trace.assertBounded()
      await engine.stopAndDrain().transportOwnershipLifetime
      trace.sample('after-permanent-stop')
      trace.assertBounded()
    } finally {
      await engine.stopAndDrain().transportOwnershipLifetime
      trace.restore()
    }
  })
  it('reserves hello before the real spawn and retains an old unanswered hello until its owner ends', async () => {
    const { engine, events } = fixture('cap-hello', { handshakeMs: 40 })
    const trace = trackReservations()
    try {
      await expect(engine.health()).rejects.toMatchObject({ error: { code: 'TIMEOUT' } })
      const hello = trace.entries.find((e) => e.ticket.pool === 'hello')!.ticket
      expect(hello.bytes).toBeGreaterThan(0)
      await expect(engine.health()).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
      expect(events().filter((e) => e.spawn)).toHaveLength(1)
      expect(hello.bytes).toBeGreaterThan(0)
      for (let i = 0; i < 300 && hello.bytes > 0; i++) {
        await pause(5)
        trace.sample('old-hello-owned')
      }
      expect(hello.bytes).toBe(0)
      await expect(engine.health()).resolves.toMatchObject({ status: 'ok' })
      expect(events().filter((e) => e.spawn)).toHaveLength(2)
      trace.assertBounded()
    } finally {
      await engine.stopAndDrain().transportOwnershipLifetime
      trace.restore()
    }
  })
  it('permanent stop settles all 128 waiters while real old control still owns its slot', async () => {
    const { engine, events } = fixture('cap-reconnect', { heartbeatMs: 30 }),
      trace = trackReservations()
    try {
      await engine.health()
      for (let i = 0; i < 100 && engine.engineSessionId; i++) {
        await pause(5)
        trace.sample('wait-ping-timeout')
      }
      const ping = trace.entries.find((e) => e.ticket.pool === 'ping')!.ticket
      const requests = Array.from({ length: 128 }, () => engine.health())
      requests.forEach((p) => void p.catch(() => undefined))
      await pause(1)
      const drain = engine.stopAndDrain()
      const results = await Promise.allSettled(requests)
      expect(results.every((r) => r.status === 'rejected')).toBe(true)
      expect(ping.bytes).toBeGreaterThan(0)
      expect((await drain.observe({ waitMs: 5 })).state).toBe('pending')
      expect(events().filter((e) => e.spawn)).toHaveLength(1)
      await drain.transportOwnershipLifetime
      expect(ping.bytes).toBe(0)
      trace.sample('drained')
      trace.assertBounded()
    } finally {
      await engine.stopAndDrain().transportOwnershipLifetime
      trace.restore()
    }
  })
  for (const outcome of ['success', 'throw', 'async-looking'] as const) {
    it(`cancels a real reservation returned after reserve synchronously stops, at most once (${outcome})`, async () => {
      const { engine, events } = fixture(),
        p = producerFixture(false),
        source = sourceFixture(p.producer),
        trace = trackReservations()
      const reserve = p.producer.reserveOperation.bind(p.producer),
        cancel = p.producer.cancelReservation.bind(p.producer)
      let actual: object | undefined,
        calls = 0
      p.producer.reserveOperation = (facts) => {
        actual = reserve(facts)
        engine.stop()
        return actual
      }
      p.producer.cancelReservation = (reservation) => {
        calls++
        expect(reservation).toBe(actual)
        if (outcome === 'throw') throw new Error('unknown cancellation')
        if (outcome === 'async-looking') return Promise.resolve() as unknown as void
        cancel(reservation)
      }
      engine.attachDispatchSource(source.source)
      try {
        const op = engine.requestWithDispatch(source.mint('job.create'), 'job.create', jobParams())
        await expect(op.logicalOutcome).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
        const entry = trace.entries.find((e) => e.ticket.background)!
        expect(calls).toBe(1)
        expect(entry.ticket.request).toBeUndefined()
        expect(entry.ticket.frame).toBeUndefined()
        expect(entry.ticket.attempted).toBe(false)
        expect(entry.book.snapshot()).toMatchObject({
          tickets: 0,
          watches: outcome === 'success' ? 0 : 1,
        })
        await engine.stopAndDrain().transportOwnershipLifetime
        await expect(
          engine.requestWithDispatch(source.mint('job.create'), 'job.create', jobParams())
            .logicalOutcome,
        ).rejects.toBeDefined()
        expect(calls).toBe(1)
        expect(events()).toEqual([])
        trace.assertBounded()
      } finally {
        await engine.stopAndDrain().transportOwnershipLifetime
        trace.restore()
      }
    })
  }
})

describe('permanent transport ownership uses actual child and actual stdio close', () => {
  it('returns one drain operation, closes actual pipes, and bounds observers without cancelling cleanup', async () => {
    const { engine } = fixture('ignore-term')
    await engine.health()
    const drain = engine.stopAndDrain()
    expect(engine.stopAndDrain()).toBe(drain)
    const waits = Array.from({ length: 8 }, () => drain.observe({ waitMs: 15 }))
    await expect(drain.observe({ waitMs: 15 })).rejects.toThrow(LifecycleFault)
    expect(
      (await Promise.all(waits)).every((s) => s.state === 'pending' && s.ownedChildren === 1),
    ).toBe(true)
    await expect(drain.transportOwnershipLifetime).resolves.toEqual({ kind: 'transport-ended' })
    expect(await drain.observe({ waitMs: 1 })).toEqual({
      state: 'ended',
      ownedChildren: 0,
      starting: 0,
    })
    await expect(drain.observe({ waitMs: 60001 })).rejects.toThrow(LifecycleFault)
  })
  it('waits for inherited pipes after child exit and never treats exit as close', async () => {
    const { engine } = fixture('descendant')
    await engine.health()
    await pause(60)
    const drain = engine.stopAndDrain()
    expect((await drain.observe({ waitMs: 10 })).state).toBe('pending')
    await drain.transportOwnershipLifetime
    expect((await drain.observe({ waitMs: 1 })).state).toBe('ended')
  })
  it('stopping before ensure starts creates no child and still completes drain', async () => {
    const { engine, events } = fixture()
    const request = engine.health()
    engine.stop()
    await expect(request).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
    await engine.stopAndDrain().transportOwnershipLifetime
    expect(events()).toEqual([])
  })
  it('settles the real backoff deferred on stop and does not spawn its continuation', async () => {
    const { engine, events } = fixture('unmatched')
    await engine.health()
    await pause(30)
    const next = engine.health()
    void next.catch(() => undefined)
    await pause(1)
    const drain = engine.stopAndDrain()
    await expect(next).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
    await drain.transportOwnershipLifetime
    await pause(120)
    expect(events().filter((e) => e.spawn)).toHaveLength(1)
  })
  it('keeps old and current real child owners counted and refuses a third before spawn', async () => {
    const { engine, events } = fixture('end-holder')
    await engine.health()
    await pause(25)
    await engine.health()
    await pause(25)
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'QUEUE_FULL' } })
    expect(events().filter((e) => e.spawn)).toHaveLength(2)
    const drain = engine.stopAndDrain()
    expect((await drain.observe({ waitMs: 10 })).ownedChildren).toBe(2)
    await drain.transportOwnershipLifetime
  })
  it('failed real OS spawn retains ownership through its actual error and close events', async () => {
    const { engine, events } = fixture('normal', {
      command: { command: join(tmpdir(), `missing-engine-${randomUUID()}`), args: [] },
    })
    await expect(engine.health()).rejects.toMatchObject({ error: { code: 'ENGINE_EXITED' } })
    await engine.stopAndDrain().transportOwnershipLifetime
    expect(events()).toEqual([])
  })
  it('unmatched strict3 frames still terminate the current connection', async () => {
    const { engine } = fixture('unmatched')
    await engine.health()
    await pause(30)
    expect(engine.engineSessionId).toBeUndefined()
  })
  it('logic-only child close without closed streams cannot release an owner or allow a third child', async () => {
    const book = new ChildOwnership(() => undefined),
      a = book.reserve(),
      b = book.reserve()
    expect(() => book.reserve()).toThrow(LifecycleFault)
    const fake = Object.assign(new EventEmitter(), {
      stdin: new PassThrough(),
      stdout: new PassThrough(),
      stderr: new PassThrough(),
      kill() {
        return true
      },
    })
    a.spawnEntered = true
    a.bind(fake as unknown as ChildProcess)
    a.finishStarting()
    fake.emit('exit')
    a.retire()
    fake.emit('close')
    b.cancelNeverCreated()
    b.finishStarting()
    book.stopped()
    expect((await book.operation.observe({ waitMs: 1 })).state).toBe('pending')
    fake.stdin.destroy()
    fake.stdout.destroy()
    fake.stderr.destroy()
    await book.operation.transportOwnershipLifetime
    expect(book.snapshot().state).toBe('ended')
  })
  it('logic-only null-stream spawn still requires the actual child close event', async () => {
    const book = new ChildOwnership(() => undefined),
      owner = book.reserve()
    const fake = Object.assign(new EventEmitter(), {
      stdin: null,
      stdout: null,
      stderr: null,
      kill() {
        return false
      },
    })
    owner.spawnEntered = true
    owner.bind(fake as unknown as ChildProcess)
    owner.finishStarting()
    fake.emit('exit')
    owner.retire()
    book.stopped()
    expect((await book.operation.observe({ waitMs: 1 })).state).toBe('pending')
    fake.emit('close')
    await book.operation.transportOwnershipLifetime
  })
  it('logic-only accounting retains attempted unknown frames and limits total bytes independently of count', () => {
    const accounting = new DispatchAccounting(128),
      params = jobParams(),
      request = { method: 'job.create', params }
    const tickets = Array.from({ length: 32 }, (_, i) =>
      accounting.reserve(
        { ...request, params: { ...params, operationId: String(i) } },
        Buffer.alloc(262144),
      ),
    )
    expect(accounting.snapshot()).toEqual({
      tickets: 32,
      frameBytes: 8388608,
      watches: 32,
      completion: 0,
    })
    expect(() => accounting.reserve({ method: 'health', params: {} }, Buffer.alloc(1))).toThrow(
      LifecycleFault,
    )
    tickets[0].attempted = true
    accounting.cancelUnwritten(tickets[0])
    expect(accounting.snapshot().tickets).toBe(32)
    accounting.cancelUnwritten(tickets[1])
    expect(accounting.snapshot().tickets).toBe(31)
  })
  it('the test wire uses strict same-version envelopes and complete Job results', () => {
    expect(validateBusiness3('params_job.create', jobParams())).toBe(true)
    expect(
      validateBusiness3('response', {
        ...fixtures.find((c) => c.name === 'response job.create')!.value,
        protocolVersion: 3,
      }),
    ).toBe(true)
  })
})
