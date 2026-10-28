/** Real EngineSupervisor control coverage with an in-memory stdio child. */
import { afterEach, describe, expect, it, vi } from 'vitest'
import { EventEmitter } from 'node:events'
import { PassThrough, Writable } from 'node:stream'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { mkdtemp, readFile, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import fixtures from '../../packages/contracts/v2/fixtures.json'

const processDouble = vi.hoisted(() => ({ spawn: vi.fn(), queue: [] as unknown[] }))
vi.mock('node:child_process', () => ({ spawn: processDouble.spawn }))

import {
  EngineSupervisor,
  EngineError,
  OrdinaryLibraryAuthority,
  QueryProjectReadTicket,
} from '../../apps/desktop/src/main/engine'
import { OrdinaryProjectSource } from '../../apps/desktop/src/main/ordinary-project-source'
import type { ProjectView } from '@ontolearn/contracts'

type Row = Record<string, unknown>
const id = (n: number) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
const registryPath = fileURLToPath(
  new URL('../../packages/contracts/v2/registry.json', import.meta.url),
)
const registryHash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const limits = {
  startupMs: 1000,
  handshakeMs: 1000,
  requestMs: 500,
  totalMs: 2000,
  heartbeatMs: 1000,
  cancelGraceMs: 1000,
  maxFrameBytes: 262144,
  maxQueuedJobs: 32,
  maxConcurrentJobs: 2,
  maxPageItems: 100,
  maxPageBytes: 131072,
  maxWorkerMemoryBytes: 536870912,
}
const jobCreated = structuredClone(
  (
    fixtures.cases.find((item) => item.name === 'response job.create')!.value as {
      result: Row
    }
  ).result,
)
const jobRunning = structuredClone(
  fixtures.cases.find((item) => item.name === 'job running')!.value as Row,
)
const business3Capabilities = [
  'health',
  'session.ping',
  'project.get',
  'project.catalog',
  'project.create',
  'project.open',
  'project.read',
  'query.definition.load',
]

/** In-memory stdio child: counts real writes and holds selected replies. */
class MemoryChild extends EventEmitter {
  stdout = new PassThrough()
  stderr = new PassThrough()
  stdin: Writable
  exitCode: number | null = null
  signalCode: NodeJS.Signals | null = null
  calls: Row[] = []
  holdPing = false
  pendingPing?: Row
  wrongId = false
  notifyAfterJobCreate = true
  // When set, kill() marks exit without emitting close: the real close event
  // is delivered later by the test (late old-child close coverage).
  deferKillClose = false
  constructor(
    readonly session: string,
    readonly profile: 'legacy2' | 'business3',
  ) {
    super()
    this.stdin = new Writable({
      write: (bytes, _encoding, done) => {
        const q = JSON.parse(bytes.toString()) as Row
        this.calls.push(q)
        if (q.method === 'session.ping' && this.holdPing) {
          this.pendingPing = q
          done()
          return
        }
        this.reply(q)
        done()
      },
    })
  }
  reply(q: Row): void {
    let result: unknown
    const params = (q.params ?? {}) as Row
    if (q.method === 'hello') {
      result = {
        selectedVersion: this.profile === 'business3' ? 3 : 2,
        engineVersion: '0.1.0',
        engineSessionId: this.session,
        capabilities:
          this.profile === 'business3'
            ? business3Capabilities
            : ['health', 'session.ping', 'job.create'],
        limits,
        registryHash,
      }
    } else if (q.method === 'session.ping') result = { nonce: params.nonce }
    else if (q.method === 'project.get' || q.method === 'project.open')
      result = {
        projectId: id(1),
        projectRevision: 1,
        inputSnapshotId: 'a'.repeat(64),
        dependencyVector: {},
        formatVersion: 3,
      }
    else if (q.method === 'project.create') {
      const canonical = Object.fromEntries(
        Object.keys(params)
          .sort()
          .map((key) => [key, params[key]]),
      )
      const requestHash = createHash('sha256')
        .update(JSON.stringify(canonical), 'utf8')
        .digest('hex')
      result = {
        createResultVersion: 1,
        projectId: id(1),
        operationId: params.operationId,
        requestHash,
        receipt: {
          projectCreateReceiptVersion: 1,
          libraryEvidenceRef: 'a'.repeat(64),
          projectId: id(1),
          operationId: params.operationId,
          requestHash,
          contextHash: 'a'.repeat(64),
          planHash: 'a'.repeat(64),
          operationSequence: 1,
          domainRevision: 0,
          metadataVersion: 1,
          inputSnapshotId: 'a'.repeat(64),
          beforeCheckpointRef: 'a'.repeat(64),
          afterCheckpointRef: 'b'.repeat(64),
        },
      }
    } else if (q.method === 'query.definition.load') result = { status: 'ok' }
    else if (q.method === 'job.create') result = jobCreated
    else result = { status: 'ok', engineVersion: '0.1.0' }
    const envelope = {
      kind: 'response',
      protocolVersion: q.method === 'hello' ? 2 : this.profile === 'business3' ? 3 : 2,
      engineSessionId: this.session,
      id: this.wrongId ? id(9) : q.id,
      method: q.method,
      ok: true,
      result,
    }
    queueMicrotask(() => this.stdout.write(`${JSON.stringify(envelope)}\n`))
    if (q.method === 'job.create' && this.notifyAfterJobCreate) {
      const notification = {
        kind: 'notification',
        protocolVersion: 2,
        engineSessionId: this.session,
        subscriptionId: id(8),
        projectId: jobRunning.projectId,
        jobId: jobRunning.jobId,
        seq: 1,
        event: 'job.state',
        data: jobRunning,
      }
      queueMicrotask(() => this.stdout.write(`${JSON.stringify(notification)}\n`))
    }
  }
  kill(): boolean {
    this.exitCode = 0
    if (this.deferKillClose) return true
    queueMicrotask(() => this.emit('close', 0))
    return true
  }
}

/** Ordinary-library child mirroring the t01 query-consumer reference. */
class QueryMemoryChild extends EventEmitter {
  stdout = new PassThrough()
  stderr = new PassThrough()
  stdin: Writable
  exitCode: number | null = null
  signalCode: NodeJS.Signals | null = null
  calls: Row[] = []
  ordinaryAcquire?: Row
  constructor(
    readonly session: string,
    readonly registryHashValue: string,
  ) {
    super()
    this.stdin = new Writable({
      write: (bytes, _encoding, done) => {
        const q = JSON.parse(bytes.toString()) as Row
        this.calls.push(q)
        const params = (q.params ?? {}) as Row
        let result: unknown
        if (q.method === 'hello')
          result = {
            selectedVersion: 2,
            engineVersion: '0.1.0',
            engineSessionId: this.session,
            capabilities: ['health', 'session.ping', 'ordinary.library', 'query.definition.load'],
            registryHash: this.registryHashValue,
            limits: structuredClone(
              (
                fixtures as {
                  queryConsumer: { samples: { prepared: { executionIdentity: { limits: Row } } } }
                }
              ).queryConsumer.samples.prepared.executionIdentity.limits,
            ),
          }
        else if (q.method === 'health') result = { status: 'ok', engineVersion: '0.1.0' }
        else if (q.method === 'ordinary.library' && params.op === 'choices')
          result = { ...params, choices: [{ choiceRef: id(13), projectId: id(1) }] }
        else if (q.method === 'ordinary.library' && params.op === 'acquire') {
          const rest = { ...params }
          delete rest.choiceRef
          this.ordinaryAcquire = { ...rest, leaseRef: id(14), project: queryProject() }
          result = this.ordinaryAcquire
        } else if (q.method === 'ordinary.library' && params.op === 'commit') {
          const acquired = this.ordinaryAcquire!
          result = {
            op: 'commit',
            ownerId: params.ownerId,
            actionId: params.actionId,
            actionSeq: params.actionSeq,
            leaseRef: params.leaseRef,
            project: structuredClone(acquired.project),
          }
        } else result = { ...params }
        queueMicrotask(() =>
          this.stdout.write(
            `${JSON.stringify({
              kind: 'response',
              protocolVersion: 2,
              id: q.id,
              method: q.method,
              engineSessionId: this.session,
              ok: true,
              result,
            })}\n`,
          ),
        )
        done()
      },
    })
  }
  kill(): boolean {
    this.exitCode = 0
    queueMicrotask(() => this.emit('close', 0))
    return true
  }
}

function queryProject(): ProjectView {
  return {
    projectId: id(1),
    projectRevision: 1,
    inputSnapshotId: 'a'.repeat(64),
    dependencyVector: { 'facts:asserted': 1, 'query:Q1': 1 },
    formatVersion: 2,
  }
}

class OpenAuthority extends OrdinaryLibraryAuthority {
  allows(): boolean {
    return true
  }
}

class ReadTicket extends QueryProjectReadTicket {
  attaches: unknown[] = []
  attachDispatch(value: unknown): void {
    this.attaches.push(value)
  }
  release(): void {
    /* the transport never reaches release in these fenced cases */
  }
}

async function realQueryContext(mountLedger: boolean) {
  const path = mountLedger ? await ledgerPath() : null
  const child = new QueryMemoryChild(id(2), registryHash)
  mount(child)
  const instance = new EngineSupervisor(
    { packaged: false, appPath: '/memory/desktop', resourcesPath: '/memory/resources' },
    {
      registryPath,
      command: { command: '/memory/engine', args: [] },
      ordinaryLibrary: { ownerId: id(11), authority: new OpenAuthority() },
      ...(path
        ? { transportLedger: { path, launchId: '9f9f9f9f-8e8e-4d4d-8c8c-2b2b2b2b2b2b' } }
        : {}),
    },
  )
  supervisors.push(instance)
  const source = new OrdinaryProjectSource(instance.ordinaryLibraryClient())
  const [choice] = await source.choices()
  expect((await source.open(choice)).ok).toBe(true)
  return { instance, source, child, path }
}

const supervisors: EngineSupervisor[] = []

async function ledgerPath(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'engine-ledger-supervisor-'))
  return `${root}/engine-transport-ledger.jsonl`
}

/** Mounted children are consumed strictly in spawn order. */
function mount(child: MemoryChild | QueryMemoryChild): void {
  processDouble.queue.push(child)
}
processDouble.spawn.mockImplementation(() => {
  const child = processDouble.queue.shift() as MemoryChild | undefined
  if (!child) throw new Error('engine-ledger-supervisor: no mounted child')
  queueMicrotask(() => child.emit('spawn'))
  return child as never
})

async function supervisor(
  profile: 'legacy2' | 'business3',
  options: ConstructorParameters<typeof EngineSupervisor>[1] = {},
) {
  const child = new MemoryChild(id(2), profile)
  mount(child)
  const instance = new EngineSupervisor(
    { packaged: false, appPath: '/memory/desktop', resourcesPath: '/memory/resources' },
    {
      profile,
      registryPath,
      startupMs: 1000,
      handshakeMs: 500,
      requestMs: 500,
      heartbeatMs: 1000,
      command: { command: '/memory/engine', args: [] },
      ...options,
    },
  )
  supervisors.push(instance)
  return { child, supervisor: instance }
}

async function withLedger(
  profile: 'legacy2' | 'business3',
  options: ConstructorParameters<typeof EngineSupervisor>[1] = {},
) {
  const path = await ledgerPath()
  const value = await supervisor(profile, {
    transportLedger: { path, launchId: '9f9f9f9f-8e8e-4d4d-8c8c-2b2b2b2b2b2b' },
    ...options,
  })
  return { ...value, path }
}

async function readLedger(path: string): Promise<Row[]> {
  const text = await readFile(path, 'utf8')
  return text
    .split('\n')
    .filter((line) => line.length > 0)
    .map((line) => JSON.parse(line) as Row)
}

async function waitFor(predicate: () => Promise<boolean>, timeoutMs = 3000): Promise<void> {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    try {
      if (await predicate()) return
    } catch {
      // Ledger files flush asynchronously; a missing file now is not failure.
    }
    await new Promise((done) => setTimeout(done, 20))
  }
}

afterEach(() => {
  for (const instance of supervisors.splice(0)) instance.stop()
})

describe('enabled supervisor keeps original transport identity', () => {
  it('returns identical health and ping results with and without a ledger', async () => {
    const disabled = await supervisor('legacy2')
    const enabled = await withLedger('legacy2')
    const expected = await disabled.supervisor.health()
    expect(await enabled.supervisor.health()).toEqual(expected)
    const nonce = id(4)
    expect(await enabled.supervisor.request('session.ping', { nonce })).toEqual(
      await disabled.supervisor.request('session.ping', { nonce }),
    )
  })

  it('records prepared/write/response with pending-derived method and write settle', async () => {
    const { supervisor: instance, path } = await withLedger('legacy2')
    await instance.health()
    await waitFor(async () =>
      (await readLedger(path)).some((line) => line.kind === 'response' && line.method === 'health'),
    )
    const events = await readLedger(path)
    const prepared = events.filter((line) => line.kind === 'requestPrepared')
    expect(prepared.length).toBeGreaterThanOrEqual(2) // hello + health
    expect(prepared.every((line) => typeof line.requestId === 'string')).toBe(true)
    const settled = events.filter((line) => line.kind === 'writeSettled')
    expect(settled.length).toBe(prepared.length)
    expect(settled.every((line) => line.writeError === false)).toBe(true)
    for (const response of events.filter((line) => line.kind === 'response')) {
      const match = prepared.find((line) => line.requestId === response.requestId)
      expect(match).toBeDefined()
      expect(response.method).toBe(match!.method)
    }
    expect(events[0]).toMatchObject({ kind: 'header' })
  })

  it('links job.create responses and job.state notifications without inventing methods', async () => {
    const { supervisor: instance, path } = await withLedger('legacy2')
    const params = structuredClone(
      (
        fixtures.cases.find((item) => item.name === 'request job.create')!.value as {
          params: Row
        }
      ).params,
    )
    const result = (await instance.request('job.create', params)) as Row
    expect(result.state).toBe('queued')
    await waitFor(async () =>
      (await readLedger(path)).some(
        (line) => line.kind === 'notification' && line.state === 'running',
      ),
    )
    const events = await readLedger(path)
    const response = events.find((line) => line.kind === 'response' && line.method === 'job.create')
    expect(response).toMatchObject({
      operationId: jobCreated.operationId,
      jobId: jobCreated.jobId,
      projectId: jobCreated.projectId,
      state: 'queued',
    })
    const notification = events.find((line) => line.kind === 'notification')
    expect(notification).toMatchObject({
      jobId: jobRunning.jobId,
      projectId: jobRunning.projectId,
      state: 'running',
    })
  })

  it('sends a real business3 project.create and records it without any job linkage', async () => {
    const { supervisor: instance, path } = await withLedger('business3')
    const params = {
      requestVersion: 1,
      operationId: id(8),
      name: '设备𠮷',
      initialization: { kind: 'blank' },
    }
    const result = (await instance.request('project.create', params)) as Row
    expect(result.projectId).toBe(id(1))
    expect((result.receipt as Row).operationId).toBe(params.operationId)
    await waitFor(async () =>
      (await readLedger(path)).some(
        (line) => line.kind === 'response' && line.method === 'project.create',
      ),
    )
    const events = await readLedger(path)
    const prepared = events.find(
      (line) => line.kind === 'requestPrepared' && line.method === 'project.create',
    )
    expect(prepared).toMatchObject({ operationId: params.operationId })
    const response = events.find(
      (line) => line.kind === 'response' && line.method === 'project.create',
    )!
    expect(response).toMatchObject({ operationId: params.operationId, projectId: id(1) })
    expect(response.jobId).toBeUndefined()
    expect(response.state).toBeUndefined()
  })

  it('never records unmatched responses as validated evidence', async () => {
    const diagnostics: string[] = []
    const wrong = await withLedger('legacy2', {
      onDiagnostic: (event) => diagnostics.push(event),
    })
    wrong.child.wrongId = true
    const code = await wrong.supervisor.health().then(
      () => 'ok',
      (error: EngineError) => error.error.code,
    )
    expect(code).toBe('TIMEOUT')
    await waitFor(async () => (await readLedger(wrong.path)).length > 0)
    const events = await readLedger(wrong.path)
    expect(diagnostics).toContain('unmatchedResponse')
    expect(events.filter((line) => line.kind === 'response')).toHaveLength(0)
  })

  it('rejects an overflowing pending window with the original QUEUE_FULL identity', async () => {
    const attempt = (instance: EngineSupervisor, nonce: string) =>
      instance.request('session.ping', { nonce }).then(
        () => 'ok',
        (error: EngineError) => error.error.code,
      )
    const codesOf = async (value: { supervisor: EngineSupervisor; child: MemoryChild }) => {
      value.child.holdPing = true
      const both = await Promise.all([
        attempt(value.supervisor, id(21)),
        attempt(value.supervisor, id(22)),
      ])
      return { both, calls: value.child.calls.filter((q) => q.method === 'session.ping') }
    }
    const disabled = await supervisor('legacy2', { maxPending: 1 })
    const enabled = await withLedger('legacy2', { maxPending: 1 })
    const disabledOutcome = await codesOf(disabled)
    const enabledOutcome = await codesOf(enabled)
    expect([...enabledOutcome.both].sort()).toEqual(['QUEUE_FULL', 'TIMEOUT'])
    expect(enabledOutcome.both).toEqual(disabledOutcome.both)
    // Exactly one ping reached the wire on each instance; the rejected one
    // was never written.
    expect(enabledOutcome.calls).toHaveLength(1)
    expect(disabledOutcome.calls).toHaveLength(1)
    await waitFor(async () =>
      (await readLedger(enabled.path)).some((line) => line.kind === 'requestRejected'),
    )
    const events = await readLedger(enabled.path)
    const rejected = events.filter((line) => line.kind === 'requestRejected')
    expect(rejected).toHaveLength(1)
    expect(rejected[0]).toMatchObject({ reason: 'queueFull', method: 'session.ping' })
    expect(rejected[0].requestId).toBeUndefined()
    const prepared = events.filter((line) => line.kind === 'requestPrepared')
    expect(prepared).toHaveLength(2) // hello + the single written ping
    expect(events.filter((line) => line.kind === 'writeSettled')).toHaveLength(2)
  })

  it('keeps the original pre-write pin rejection, wire silence and records its reason', async () => {
    const loadParams = structuredClone(
      (fixtures as { queryConsumer: { samples: { params: Row } } }).queryConsumer.samples.params[
        'query.definition.load'
      ],
    )
    const binding = {
      projectId: id(1),
      engineSessionId: id(2),
      generation: 1,
      selectionSeq: 1,
      projectRevision: 1,
      inputSnapshotId: 'a'.repeat(64),
    }
    const run = async (mountLedger: boolean) => {
      const context = await realQueryContext(mountLedger)
      const current = context.source.current()!
      let live = true
      const pin = context.instance.issueQueryPin(
        current.owner,
        current.engineSessionId,
        () => live,
        { ...binding, selectionSeq: current.selectionSeq },
      )
      const read = new ReadTicket()
      const count = context.child.calls.length
      // The revocation mock replaces the method, so reachability is judged by
      // the spy call count, not by the (unused) attaches array.
      const attachSpy = vi.spyOn(read, 'attachDispatch').mockImplementation(() => {
        live = false
      })
      const rejection = await context.instance
        .requestQueryProjectGet({ projectId: id(1) }, pin, read, {
          ...binding,
          selectionSeq: current.selectionSeq,
        })
        .then(
          () => 'resolved',
          (error: unknown) => (error instanceof EngineError ? error.error.code : 'other'),
        )
      // The original contract: a revoked guard rejects through
      // #checkQueryPin with PERMISSION_DENIED.
      expect(rejection).toBe('PERMISSION_DENIED')
      expect(attachSpy).toHaveBeenCalledTimes(1)
      expect(context.instance.queryWriteEntered(pin)).toBe(false)
      expect(context.child.calls).toHaveLength(count)
      return { context, rejection }
    }
    const enabled = await run(true)
    const disabled = await run(false)
    expect(enabled.rejection).toBe(disabled.rejection)
    await waitFor(async () =>
      (await readLedger(enabled.context.path!)).some(
        (line) => line.kind === 'requestRejected' && line.reason === 'pinGuard',
      ),
    )
    const events = await readLedger(enabled.context.path!)
    const pinGuard = events.filter(
      (line) => line.kind === 'requestRejected' && line.reason === 'pinGuard',
    )
    expect(pinGuard).toHaveLength(1)
    expect(pinGuard[0]).toMatchObject({ method: 'project.get' })
    // The final pin fires after registration: this request WAS prepared...
    const prepared = events.filter(
      (line) => line.kind === 'requestPrepared' && line.method === 'project.get',
    )
    expect(prepared).toHaveLength(1)
    // ...never written: no write settle carries the rejected request id.
    const rejectedId = prepared[0]!.requestId
    expect(
      events.some((line) => line.kind === 'writeSettled' && line.requestId === rejectedId),
    ).toBe(false)
    void loadParams
  })

  it('never places an observer between the final recovery pin and stdin.write', () => {
    const source = readFileSync(
      fileURLToPath(new URL('../../apps/desktop/src/main/engine.ts', import.meta.url)),
      'utf8',
    )
    const pinToken = 'recoveryCurrent?.()'
    const writeToken = 'session.child.stdin.write(encoded'
    let windowStart = -1
    let windowEnd = -1
    let cursor = 0
    for (;;) {
      const pin = source.indexOf(pinToken, cursor)
      if (pin < 0) break
      const write = source.indexOf(writeToken, pin)
      if (write >= 0 && (windowEnd < 0 || write - pin < windowEnd - windowStart)) {
        windowStart = pin
        windowEnd = write
      }
      cursor = pin + 1
    }
    expect(windowStart).toBeGreaterThan(0)
    expect(windowEnd).toBeGreaterThan(windowStart)
    expect(windowEnd - windowStart).toBeLessThan(800)
    // The straight-line success path is pin -> write; the catch clause only
    // runs on the original rejection path, so ledger hooks may live there.
    const catchAt = source.indexOf('} catch', windowStart)
    expect(catchAt).toBeGreaterThan(windowStart)
    expect(catchAt).toBeLessThan(windowEnd)
    const straightLine = source.slice(windowStart, catchAt)
    expect(straightLine).not.toContain('ledger')
    expect(source.slice(windowStart, windowEnd)).toContain('writeEntered')
    // Prepared is recorded before the guarded region; settled only in the
    // write callback after it.
    const sendStart = source.lastIndexOf('#send(', windowStart)
    const preparedAt = source.indexOf('recordRequestPrepared', sendStart)
    expect(preparedAt).toBeGreaterThan(sendStart)
    expect(preparedAt).toBeLessThan(windowStart)
    expect(source.indexOf('recordWriteSettled', windowEnd)).toBeGreaterThan(windowEnd)
  })

  it('records a late old-child close after the new session is established', async () => {
    const { supervisor: instance, child, path } = await withLedger('legacy2')
    await instance.health()
    // Fence session 1 with an invalid frame while deferring the old child's
    // real close event.
    child.deferKillClose = true
    child.stdout.write('{"a":1,"a":2}\n')
    await waitFor(async () => (await readLedger(path)).some((line) => line.kind === 'fence'))
    const second = new MemoryChild(id(3), 'legacy2')
    mount(second)
    // The reconnect establishes session 2 BEFORE the old child's close.
    await instance.health()
    await waitFor(async () => {
      const events = await readLedger(path)
      return events.filter((line) => line.kind === 'sessionStart').length >= 2
    })
    // The old child's real close arrives only now, after the new session.
    // The old child's real close arrives late and keeps its own generation.
    child.exitCode = 0
    child.emit('close', 0)
    await waitFor(async () =>
      (await readLedger(path)).some((line) => line.kind === 'childClosed' && line.generation === 1),
    )
    const events = await readLedger(path)
    const starts = events.filter((line) => line.kind === 'sessionStart')
    const lateClose = events
      .filter((line) => line.kind === 'childClosed' && line.generation === 1)
      .at(-1)!
    expect(events.indexOf(lateClose)).toBeGreaterThan(events.indexOf(starts[1]!))
    expect(lateClose.generation).toBe(starts[0]!.generation)
    // The new session is unaffected by the late old close.
    expect(await instance.health()).toMatchObject({ status: 'ok' })
    instance.stop()
    await waitFor(async () => (await readLedger(path)).at(-1)?.kind === 'footer')
    const footer = (await readLedger(path)).at(-1) as Row
    expect(footer.childrenOpenCount).toBe(0)
    expect(footer.incomplete).toBe(false)
    void second
  })

  it('holds the seal open while a real child has not closed after stop', async () => {
    const { supervisor: instance, child, path } = await withLedger('legacy2')
    await instance.health()
    // Defer the child's real close: stop must not fabricate a complete footer
    // while an actual child remains open.
    child.deferKillClose = true
    instance.stop()
    await waitFor(async () => (await readLedger(path)).some((line) => line.kind === 'fence'))
    const duringHold = await readLedger(path)
    expect(duringHold.some((line) => line.kind === 'footer')).toBe(false)
    // Releasing the last real close is what completes the launch evidence.
    child.exitCode = 0
    child.emit('close', 0)
    await waitFor(async () => (await readLedger(path)).at(-1)?.kind === 'footer')
    const footer = (await readLedger(path)).at(-1) as Row
    expect(footer.stopRequested).toBe(true)
    expect(footer.childrenOpenCount).toBe(0)
    expect(footer.incomplete).toBe(false)
  })

  it('rejects a wire-pending request with the identical original invalid-frame error', async () => {
    const run = async (mountLedger: boolean) => {
      const context = mountLedger ? await withLedger('legacy2') : await supervisor('legacy2')
      await context.supervisor.health()
      // Hold ping replies so the real request stays pending on the wire.
      context.child.holdPing = true
      const nonce = '00000000-0000-4000-8000-0000000000dd'
      const settled = context.supervisor.request('session.ping', { nonce }).then(
        () => 'ok',
        (error: EngineError) => error,
      )
      await waitFor(async () => context.child.calls.some((q) => q.method === 'session.ping'))
      const writtenAtFrame = context.child.calls.length
      // The malformed frame hits the same live session while the ping pends.
      context.child.stdout.write('{"a":1,"a":2}\n')
      const rejection = await settled
      expect(typeof rejection).not.toBe('string')
      return { context, rejection: rejection as EngineError, writtenAtFrame }
    }
    const enabled = await run(true)
    const disabled = await run(false)
    // The original invalid-frame error identity is identical in full.
    expect(enabled.rejection.error).toEqual(disabled.rejection.error)
    expect(enabled.rejection.error.code).toBe('INVALID_REQUEST')
    expect(enabled.rejection.error.params).toEqual({ field: 'envelope' })
    // Wire order and count stay identical with and without the ledger.
    expect(enabled.context.child.calls.map((q) => q.method)).toEqual(
      disabled.context.child.calls.map((q) => q.method),
    )
    expect(enabled.context.child.calls.length).toBe(disabled.context.child.calls.length)
    expect(enabled.writtenAtFrame).toBe(disabled.writtenAtFrame)
    await waitFor(async () =>
      (await readLedger((enabled.context as unknown as { path: string }).path)).some(
        (line) => line.kind === 'fence',
      ),
    )
    const events = await readLedger((enabled.context as unknown as { path: string }).path)
    // The wire-pending request was prepared and written exactly once.
    const prepared = events.filter((line) => line.kind === 'requestPrepared')
    expect(prepared).toHaveLength(3) // hello + health + the held ping
    expect(events.filter((line) => line.kind === 'writeSettled')).toHaveLength(3)
    // The invalid frame never becomes validated evidence.
    const fenceAt = events.findIndex((line) => line.kind === 'fence')
    expect(fenceAt).toBeGreaterThan(-1)
    expect(
      events
        .slice(fenceAt)
        .filter((line) => line.kind === 'response' || line.kind === 'notification'),
    ).toHaveLength(0)
  })

  it('fences a died child, reconnects a new generation and seals a complete footer', async () => {
    const { supervisor: instance, child, path } = await withLedger('legacy2')
    await instance.health()
    const second = new MemoryChild(id(3), 'legacy2')
    mount(second)
    child.exitCode = 73
    child.emit('close', 73)
    await instance.health()
    await waitFor(async () => {
      const events = await readLedger(path)
      return events.filter((line) => line.kind === 'sessionStart').length >= 2
    })
    const events = await readLedger(path)
    const starts = events.filter((line) => line.kind === 'sessionStart')
    expect(starts.length).toBeGreaterThanOrEqual(2)
    const late = events.find((line) => line.kind === 'childClosed' && line.exitCode === 73)
    expect(late).toMatchObject({ generation: starts[0]!.generation })
    instance.stop()
    await waitFor(async () => {
      const all = await readLedger(path)
      return all.at(-1)?.kind === 'footer'
    })
    const footer = (await readLedger(path)).at(-1) as Row
    expect(footer.stopRequested).toBe(true)
    expect(footer.childrenOpenCount).toBe(0)
    expect(footer.incomplete).toBe(false)
  })

  it('writer failure keeps supervisor behavior identical and never overwrites the old file', async () => {
    const path = await ledgerPath()
    await writeFile(path, 'old-foreign-content\n', { encoding: 'utf8', flag: 'ax' })
    const broken = await supervisor('legacy2', {
      transportLedger: { path, launchId: '11111111-2222-4333-8444-555555555555' },
    })
    const plain = await supervisor('legacy2')
    expect(await broken.supervisor.health()).toEqual(await plain.supervisor.health())
    expect(await readFile(path, 'utf8')).toBe('old-foreign-content\n')
  })
})
