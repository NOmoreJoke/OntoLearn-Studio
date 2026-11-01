import { describe, expect, it } from 'vitest'
import {
  LEDGER_LIMITS,
  TransportLedger,
  resolveTransportLedger,
  type LedgerControls,
  type LedgerSink,
} from '../../apps/desktop/src/main/engine-ledger'

class ManualClock {
  t = 0
  now(): number {
    return this.t
  }
  advance(ms: number): void {
    this.t += ms
  }
}

class ManualScheduler {
  tasks: (() => void)[] = []
  schedule(fn: () => void): void {
    this.tasks.push(fn)
  }
  run(): void {
    const task = this.tasks.shift()
    if (task) task()
  }
  runAll(): void {
    while (this.tasks.length > 0) this.run()
  }
}

interface PendingWrite {
  chunk: Buffer
  callback: (error: Error | null | undefined, bytesWritten?: number) => void
}

/** Exercises the real production sink against a temp file. */
async function productionSinkHarness() {
  const { mkdtemp } = await import('node:fs/promises')
  const { tmpdir } = await import('node:os')
  const { join } = await import('node:path')
  const root = await mkdtemp(join(tmpdir(), 'engine-ledger-prod-'))
  const path = join(root, 'engine-transport-ledger.jsonl')
  const ledger = TransportLedger.open({
    path,
    launchId: null,
    appPid: process.pid,
    platform: 'test',
  })
  return { ledger, path, root }
}

/** Close is deferred until flushClose(): covers the async close-event window. */
class ManualSink implements LedgerSink {
  writes: Buffer[] = []
  pending: PendingWrite[] = []
  closeCount = 0
  #closeListeners: ((closeError: Error | null) => void)[] = []
  #errorListeners: ((error: Error) => void)[] = []
  #deferClose = false

  deferClose(): void {
    this.#deferClose = true
  }
  write(
    chunk: Buffer,
    callback: (error: Error | null | undefined, bytesWritten?: number) => void,
  ): void {
    this.writes.push(chunk)
    this.pending.push({ chunk, callback })
  }
  settle(error: Error | null = null): void {
    const entry = this.pending.shift()
    // Success reports the explicit byte completion of its own chunk.
    if (entry) entry.callback(error, error ? undefined : entry.chunk.byteLength)
  }
  settleShort(): void {
    // A sink-reported short write: fewer bytes than the chunk requested.
    const entry = this.pending.shift()
    if (entry) entry.callback(null, Math.max(0, entry.chunk.byteLength - 1))
  }
  close(): void {
    this.closeCount += 1
    if (this.#deferClose) return
    this.flushClose()
  }
  flushClose(closeError: Error | null = null): void {
    for (const listener of this.#closeListeners) listener(closeError)
  }
  onClose(listener: (closeError: Error | null) => void): void {
    this.#closeListeners.push(listener)
  }
  onError(listener: (error: Error) => void): void {
    this.#errorListeners.push(listener)
  }
  emitError(error: Error): void {
    for (const listener of this.#errorListeners) listener(error)
  }
  text(): string {
    return this.writes.map((chunk) => chunk.toString('utf8')).join('')
  }
}

function harness() {
  const clock = new ManualClock()
  const scheduler = new ManualScheduler()
  const sink = new ManualSink()
  const controls: LedgerControls = {
    now: () => clock.now(),
    schedule: (fn) => scheduler.schedule(fn),
  }
  const ledger = TransportLedger.open({
    path: '/unused',
    launchId: '0b1b2b3b-4b5b-6b7b-8b9b-acbd11223344',
    appPid: 4242,
    platform: 'test',
    controls,
    sinkFactory: () => sink,
  })
  return { ledger, clock, scheduler, sink }
}

function lines(text: string): Record<string, unknown>[] {
  return text
    .split('\n')
    .filter((line) => line.length > 0)
    .map((line) => JSON.parse(line) as Record<string, unknown>)
}

describe('transport ledger enablement resolution', () => {
  const launchId = '1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d'
  const profile = '/tmp/ontolearn-e2e-profile-ab12cd'
  const enable = (overrides: Partial<Parameters<typeof resolveTransportLedger>[0]> = {}) =>
    resolveTransportLedger({
      flag: '1',
      launchId,
      userDataPath: profile,
      packaged: false,
      platform: 'win32',
      userDataArg: profile,
      ...overrides,
    })

  it('enables only the explicit flag on a matching isolated Windows profile', () => {
    expect(enable()).toEqual({
      transportLedger: { path: `${profile}/engine-transport-ledger.jsonl`, launchId },
    })
  })

  it('rejects packaged, missing flag, other values and non-isolated profiles', () => {
    expect(enable({ packaged: true })).toBeUndefined()
    expect(enable({ flag: undefined })).toBeUndefined()
    expect(enable({ flag: '0' })).toBeUndefined()
    expect(enable({ userDataPath: '/tmp/some-other-profile' })).toBeUndefined()
    expect(enable({ userDataPath: '/tmp/ontolearn-e2e-profile-x' })).toBeUndefined()
  })

  it('rejects other platforms, invalid launch ids and argv/profile mismatches', () => {
    expect(enable({ platform: 'linux' })).toBeUndefined()
    expect(enable({ platform: 'darwin' })).toBeUndefined()
    expect(enable({ launchId: 'not-a-uuid' })).toBeUndefined()
    expect(enable({ launchId: undefined })).toBeUndefined()
    expect(enable({ userDataArg: undefined })).toBeUndefined()
    expect(enable({ userDataArg: '/tmp/different-profile' })).toBeUndefined()
    expect(enable({ userDataPath: '/tmp/link/ontolearn-e2e-profile-ab12cd' })).toBeUndefined()
  })
})

describe('transport ledger writer control', () => {
  it('writes the header first with launch identity captured at open time', () => {
    const { ledger, clock, scheduler, sink } = harness()
    clock.advance(11)
    ledger.recordFence(1, 'ENGINE_EXITED', 0)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    expect(all[0]).toMatchObject({
      kind: 'header',
      appPid: 4242,
      launchId: '0b1b2b3b-4b5b-6b7b-8b9b-acbd11223344',
      monotonicMs: 0,
    })
    expect(all[1]).toMatchObject({ kind: 'fence', monotonicMs: 11 })
    expect(ledger.state).toBe('active')
  })

  it('reads each whitelisted field once and never touches unknown keys', () => {
    const reads = { operationId: 0, evil: 0 }
    const clone = {
      id: 'r'.repeat(128),
      method: 'm'.repeat(128),
      params: {
        get operationId(): string {
          reads.operationId += 1
          return 'op-1'
        },
        get evil(): string {
          reads.evil += 1
          return 'never'
        },
        jobId: 'j'.repeat(129),
        projectId: 42 as unknown as string,
      },
    }
    const { ledger, scheduler, sink } = harness()
    ledger.recordRequestPrepared(3, clone, 'changeset.commit', 'request', 77)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const event = lines(sink.text()).find((line) => line.kind === 'requestPrepared')!
    expect(reads).toEqual({ operationId: 1, evil: 0 })
    expect(event.requestId).toBe('r'.repeat(128))
    expect(event.method).toBe('m'.repeat(128))
    expect(event.operationId).toBe('op-1')
    expect(event.jobId).toBeNull()
    expect(event.projectId).toBeNull()
    expect(event.paramsByteLength).toBe(77)
  })

  it('never reads payload fields for job/project linkage beyond the fixed whitelist', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordResponse(1, { id: 'r1', method: 'job.create' }, true, 12, {
      operationId: 'op-9',
      jobId: 'job-9',
      projectId: 'proj-9',
      state: 'queued',
      input: { secret: 'payload' },
    })
    ledger.recordResponse(1, { id: 'r2', method: 'project.create' }, true, 12, {
      operationId: 'op-8',
      projectId: 'proj-8',
      createResultVersion: 1,
    })
    ledger.recordResponse(1, { id: 'r3', method: 'health' }, true, 5, { status: 'ok' })
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const job = all.find((line) => line.requestId === 'r1')!
    expect(job).toMatchObject({ kind: 'response', jobId: 'job-9', state: 'queued' })
    expect(job.input).toBeUndefined()
    const project = all.find((line) => line.requestId === 'r2')!
    expect(project).toMatchObject({ operationId: 'op-8', projectId: 'proj-8' })
    expect(project.jobId).toBeUndefined()
    expect(project.state).toBeUndefined()
    const health = all.find((line) => line.requestId === 'r3')!
    expect(health.operationId).toBeUndefined()
  })

  it('reads job.state notification state from data.state', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordNotification(2, {
      kind: 'notification',
      event: 'job.state',
      projectId: 'proj-1',
      jobId: 'job-1',
      data: { projectId: 'proj-1', jobId: 'job-1', operationId: 'op-2', state: 'running' },
    })
    ledger.recordNotification(2, { kind: 'notification', event: 'other' })
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const state = all.find((line) => line.kind === 'notification' && line.state === 'running')!
    expect(state).toMatchObject({ projectId: 'proj-1', jobId: 'job-1', operationId: 'op-2' })
    const other = all.find((line) => line.kind === 'notification' && line.state === undefined)!
    expect(other.projectId).toBeUndefined()
  })

  it('records pre-clone rejections with fixed reasons and no invented request id', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordRequestRejected('queueFull', 'session.ping')
    ledger.recordRequestRejected('validation', 'project.create')
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const rejected = lines(sink.text()).filter((line) => line.kind === 'requestRejected')
    expect(rejected).toHaveLength(2)
    expect(rejected[0]).toMatchObject({ reason: 'queueFull', method: 'session.ping' })
    expect(rejected.every((line) => line.requestId === undefined)).toBe(true)
  })

  it('keeps sequence strictly increasing with the injected monotonic clock', () => {
    const { ledger, clock, scheduler, sink } = harness()
    clock.advance(5)
    ledger.recordFence(1, 'ENGINE_EXITED', 0)
    clock.advance(7)
    ledger.recordFence(1, 'TIMEOUT', 1)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    expect(all.map((line) => line.seq)).toEqual([1, 2, 3])
    expect(all.slice(1).map((line) => line.monotonicMs)).toEqual([5, 12])
  })

  it('bounds the queue at the fixed slot count and counts drop-newest loss', () => {
    const { ledger, scheduler, sink } = harness()
    // The header already occupies one queue slot after construction.
    for (let index = 0; index < LEDGER_LIMITS.queueSlots + 3; index += 1)
      ledger.recordFence(1, 'ENGINE_EXITED', index)
    expect(ledger.counters.queueLength).toBe(LEDGER_LIMITS.queueSlots)
    expect(ledger.counters.droppedQueue).toBe(4)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
  })

  it('replaces a genuinely reachable oversized record with an overflow note', () => {
    const { ledger, scheduler, sink } = harness()
    // Every field below is inside the production whitelist bounds; the
    // combined serialization alone exceeds the per-record byte cap.
    const id128 = 'x'.repeat(128)
    const clone = {
      id: id128,
      method: id128,
      params: {
        operationId: id128,
        jobId: id128,
        projectId: id128,
        capability: id128,
      },
    }
    const serialized = JSON.stringify({
      kind: 'requestPrepared',
      seq: 2,
      monotonicMs: 0,
      generation: 1,
      requestId: id128,
      method: id128,
      phase: id128,
      paramsByteLength: 262144,
      ...clone.params,
    })
    expect(Buffer.byteLength(serialized, 'utf8')).toBeGreaterThan(LEDGER_LIMITS.maxRecordBytes)
    ledger.recordRequestPrepared(1, clone, id128, id128, 262144)
    ledger.requestStop()
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    expect(all.some((line) => line.kind === 'requestPrepared')).toBe(false)
    const note = all.find((line) => line.kind === 'recordOverflowNote')
    expect(note).toMatchObject({ originalKind: 'requestPrepared' })
    const footer = all[all.length - 1]!
    expect(footer.overflow).toBe(1)
    expect(footer.incomplete).toBe(true)
  })

  it('honors total record caps including the reserved header and footer', () => {
    const { ledger, scheduler, sink } = harness()
    // Drain in small batches so the queue slot cap never drops anything.
    let settled = 0
    while (ledger.counters.acceptedRecords < LEDGER_LIMITS.totalRecords - 2) {
      ledger.recordWriteSettled(`id-${settled}`, false)
      settled += 1
      if (ledger.counters.queueLength >= 16) {
        scheduler.runAll()
        while (sink.pending.length > 0) sink.settle()
      }
    }
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    expect(ledger.counters.acceptedRecords).toBe(LEDGER_LIMITS.totalRecords - 2)
    ledger.recordWriteSettled('last-ordinary', false)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    expect(ledger.counters.acceptedRecords).toBe(LEDGER_LIMITS.totalRecords - 1)
    ledger.recordWriteSettled('one-too-many', false)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    expect(ledger.counters.acceptedRecords).toBe(LEDGER_LIMITS.totalRecords - 1)
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.kind).toBe('footer')
    expect(footer.truncated).toBe(true)
    expect(footer.incomplete).toBe(true)
  })

  it('allows at most one in-flight write and one scheduled flush', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordWriteSettled('a', false)
    expect(scheduler.tasks.length).toBe(1)
    scheduler.run()
    expect(sink.writes.length).toBe(1)
    expect(sink.pending.length).toBe(1)
    // While the first write is in flight no second flush may start.
    ledger.recordWriteSettled('b', false)
    scheduler.runAll()
    expect(sink.writes.length).toBe(1)
    expect(sink.pending.length).toBe(1)
    sink.settle()
    scheduler.runAll()
    expect(sink.writes.length).toBe(2)
    expect(sink.pending.length).toBe(1)
    sink.settle()
  })

  it('fails irreversibly when the stream errors while a batch is in flight', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordWriteSettled('a', false)
    scheduler.run()
    expect(sink.pending.length).toBe(1)
    ledger.requestStop()
    scheduler.runAll()
    // Stream error keeps the original callback pending; fail() clears all
    // queue and footer state while the batch callback is still outstanding.
    sink.emitError(new Error('stream error'))
    expect(ledger.state).toBe('failed')
    const written = sink.writes.length
    const records = ledger.counters.recordsWritten
    // The original batch callback now succeeds late: no resurrection.
    sink.settle(null)
    expect(ledger.state).toBe('failed')
    expect(sink.writes.length).toBe(written)
    expect(ledger.counters.recordsWritten).toBe(records)
    expect(ledger.counters.footerWritten).toBe(false)
    expect(sink.closeCount).toBe(1)
    ledger.recordWriteSettled('b', false)
    scheduler.runAll()
    sink.settle(null)
    expect(ledger.state).toBe('failed')
    expect(ledger.counters.footerWritten).toBe(false)
  })

  it('fails on a synchronous sink throw and on a throwing sink factory', () => {
    const inline = { now: () => 0, schedule: (fn: () => void) => fn() }
    const factoryFail = TransportLedger.open({
      path: '/unused',
      launchId: null,
      appPid: 1,
      platform: 'test',
      controls: inline,
      sinkFactory: () => {
        throw new Error('no sink')
      },
    })
    expect(factoryFail.state).toBe('failed')
    factoryFail.recordWriteSettled('a', false)
    expect(factoryFail.counters.queueLength).toBe(0)

    const syncThrow = TransportLedger.open({
      path: '/unused',
      launchId: null,
      appPid: 1,
      platform: 'test',
      controls: inline,
      sinkFactory: () =>
        ({
          write: () => {
            throw new Error('sync')
          },
          close: () => undefined,
          onClose: () => undefined,
          onError: () => undefined,
        }) as unknown as LedgerSink,
    })
    expect(syncThrow.state).toBe('failed')
  })

  it('never waits on a missing callback: bounded queue, footer pending confirmation', () => {
    const { ledger, scheduler, sink } = harness()
    for (let index = 0; index < LEDGER_LIMITS.queueSlots + 5; index += 1)
      ledger.recordWriteSettled(`id-${index}`, false)
    expect(ledger.counters.queueLength).toBe(LEDGER_LIMITS.queueSlots)
    ledger.recordSessionStart(9, null)
    ledger.recordChildClosed(9, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    // The footer has been assembled into the single in-flight batch: it is no
    // longer pending assembly, and it is not yet confirmed.
    expect(ledger.counters.inFlight).toBe(true)
    expect(ledger.counters.footerPending).toBe(false)
    expect(ledger.counters.footerWritten).toBe(false)
    expect(sink.writes.length).toBe(1)
  })

  it('separates stopRequested from a confirmed footer and drains normally', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordSessionStart(1, 111)
    ledger.recordWriteSettled('a', false)
    ledger.requestStop()
    // Children still open: stopRequested alone must not seal.
    expect(ledger.counters.footerWritten).toBe(false)
    ledger.recordChildClosed(1, 0, null)
    scheduler.runAll()
    sink.settle()
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.kind).toBe('footer')
    expect(footer.stopRequested).toBe(true)
    expect(footer.truncated).toBe(false)
    expect(footer.incomplete).toBe(false)
    // Prefix totals describe every JSONL line before the footer line itself.
    expect(footer.recordsWritten).toBe(all.length - 1)
    const footerBytes = footer.bytesWritten as number
    const footerLine = JSON.stringify(footer)
    expect(footerBytes + Buffer.byteLength(`${footerLine}\n`, 'utf8')).toBe(
      Buffer.byteLength(sink.text(), 'utf8'),
    )
    expect(sink.closeCount).toBe(1)
    expect(ledger.state).toBe('closed')
  })

  it('keeps footer counters accurate with one batch in flight and one queued', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordWriteSettled('a', false)
    scheduler.run() // batch A (header + a) in flight
    ledger.recordWriteSettled('b', false)
    ledger.recordSessionStart(1, 5)
    ledger.recordChildClosed(1, 0, null)
    ledger.requestStop()
    scheduler.runAll() // nothing while A is in flight
    expect(sink.writes.length).toBe(1)
    sink.settle() // A succeeds
    scheduler.runAll() // B + session + close + footer batch
    sink.settle()
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(all[all.length - 2]).toMatchObject({ kind: 'childClosed' })
    expect(footer.recordsWritten).toBe(all.length - 1)
    const footerBytes = footer.bytesWritten as number
    expect(footerBytes + Buffer.byteLength(`${JSON.stringify(footer)}\n`, 'utf8')).toBe(
      Buffer.byteLength(sink.text(), 'utf8'),
    )
  })

  it('covers the footer-in-flight window: sealing is idempotent', () => {
    const { ledger, scheduler, sink } = harness()
    sink.deferClose()
    ledger.recordSessionStart(1, 7)
    ledger.recordChildClosed(1, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    // Footer batch is in flight; repeated stop/close must not schedule more.
    expect(ledger.counters.inFlight).toBe(true)
    ledger.requestStop()
    ledger.recordChildClosed(1, 0, null)
    scheduler.runAll()
    expect(sink.writes.length).toBe(1)
    sink.settle()
    const all = lines(sink.text())
    expect(all.filter((line) => line.kind === 'footer')).toHaveLength(1)
    expect(ledger.state).toBe('sealed')
    expect(sink.closeCount).toBe(1)
    // Close event arrives late: the ledger only now reports closed.
    sink.flushClose()
    expect(ledger.state).toBe('closed')
  })

  it('covers the footer-success-close-pending window without further writes', () => {
    const { ledger, scheduler, sink } = harness()
    sink.deferClose()
    ledger.recordSessionStart(1, 7)
    ledger.recordChildClosed(1, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    sink.settle()
    expect(ledger.state).toBe('sealed')
    const writes = sink.writes.length
    // Late stop and close events after a confirmed footer stay inert.
    ledger.requestStop()
    ledger.recordChildClosed(1, 0, null)
    scheduler.runAll()
    sink.settle()
    expect(sink.writes.length).toBe(writes)
    expect(sink.closeCount).toBe(1)
    const all = lines(sink.text())
    expect(all.filter((line) => line.kind === 'footer')).toHaveLength(1)
    sink.flushClose()
    expect(ledger.state).toBe('closed')
  })

  it('shares caps and file across generations; late old-child close keeps its generation', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordSessionStart(1, 11)
    ledger.recordChildClosed(1, 0, null)
    ledger.recordSessionStart(2, 22)
    ledger.recordFence(2, 'TIMEOUT', 0)
    ledger.recordChildClosed(1, 1, 'SIGTERM') // late close of the old child
    ledger.recordChildClosed(2, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const late = all.find((line) => line.kind === 'childClosed' && line.exitCode === 1)
    expect(late).toMatchObject({ generation: 1, signalCode: 'SIGTERM' })
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.childrenOpenCount).toBe(0)
    expect(footer.incomplete).toBe(false)
  })

  it('bounds tracked children and never claims all closed after overflow', () => {
    const { ledger, scheduler, sink } = harness()
    for (let generation = 1; generation <= LEDGER_LIMITS.childrenCap; generation += 1)
      ledger.recordSessionStart(generation, null)
    ledger.recordSessionStart(LEDGER_LIMITS.childrenCap + 1, null)
    expect(ledger.counters.childrenOpen).toBe(LEDGER_LIMITS.childrenCap)
    expect(ledger.counters.childrenOverflow).toBe(true)
    for (let generation = 1; generation <= LEDGER_LIMITS.childrenCap + 1; generation += 1)
      ledger.recordChildClosed(generation, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.childrenOverflow).toBe(true)
    expect(footer.incomplete).toBe(true)
  })

  it('stops registering children after terminal sealing', () => {
    const { ledger } = harness()
    ledger.requestStop()
    expect(ledger.counters.stopRequested).toBe(true)
    const before = ledger.counters.childrenOpen
    ledger.recordSessionStart(77, null)
    expect(ledger.counters.childrenOpen).toBe(before)
  })

  it('fails irreversibly on a direct callback error with the footer pending', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordWriteSettled('a', false)
    scheduler.run()
    ledger.requestStop()
    scheduler.runAll()
    expect(ledger.counters.footerPending).toBe(true)
    expect(sink.pending.length).toBe(1)
    sink.settle(new Error('direct callback error'))
    expect(ledger.state).toBe('failed')
    const writes = sink.writes.length
    sink.settle(null)
    expect(ledger.state).toBe('failed')
    expect(sink.writes.length).toBe(writes)
    expect(ledger.counters.footerWritten).toBe(false)
    expect(sink.closeCount).toBe(1)
  })

  it('treats a sink-reported short write as immediate failure without retry', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordSessionStart(1, 7)
    ledger.recordChildClosed(1, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    expect(sink.pending.length).toBe(1)
    sink.settleShort()
    expect(ledger.state).toBe('failed')
    const writes = sink.writes.length
    ledger.recordWriteSettled('late', false)
    scheduler.runAll()
    expect(sink.writes.length).toBe(writes)
    expect(ledger.counters.footerWritten).toBe(false)
    expect(ledger.counters.inFlight).toBe(false)
  })

  it('saturates drop attempts at the fixed bound and forces incomplete', () => {
    const { ledger, scheduler, sink } = harness()
    // Header occupies one queue slot; fill the rest and overflow the bound.
    const flood = LEDGER_LIMITS.queueSlots + LEDGER_LIMITS.counterSaturation + 5
    for (let index = 0; index < flood; index += 1) ledger.recordWriteSettled(`id-${index}`, false)
    expect(ledger.counters.queueLength).toBe(LEDGER_LIMITS.queueSlots)
    expect(ledger.counters.droppedQueue).toBe(LEDGER_LIMITS.counterSaturation)
    expect(ledger.counters.saturated).toBe(true)
    ledger.requestStop()
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.droppedQueue).toBe(LEDGER_LIMITS.counterSaturation)
    expect(footer.saturated).toBe(true)
    expect(footer.incomplete).toBe(true)
  })

  it('commits sequence numbers only for accepted records', () => {
    const { ledger, scheduler, sink } = harness()
    for (let index = 0; index < LEDGER_LIMITS.queueSlots + 6; index += 1)
      ledger.recordWriteSettled(`id-${index}`, false)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    ledger.recordWriteSettled('after-drop', false)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const seqs = lines(sink.text()).map((line) => line.seq as number)
    expect(seqs).toEqual(Array.from({ length: seqs.length }, (_, index) => index + 1))
  })

  it('reaches the total byte cap before the record cap', () => {
    const { ledger, scheduler, sink } = harness()
    // Sized to stay just under the per-record cap so each line is ~1KB.
    const id128 = 'f'.repeat(128)
    const id100 = 'g'.repeat(100)
    const clone = {
      id: id128,
      method: id128,
      params: {
        operationId: id100,
        jobId: id100,
        projectId: id100,
        capability: id100,
      },
    }
    // Fat records (~1KB each) exhaust 512KiB far below the 4096 record cap.
    let guard = 0
    while (
      !ledger.counters.saturated &&
      ledger.counters.acceptedRecords < LEDGER_LIMITS.totalRecords - 2 &&
      guard < 2000
    ) {
      ledger.recordRequestPrepared(1, clone, id128, 'request', 262144)
      guard += 1
      if (ledger.counters.queueLength >= 16) {
        scheduler.runAll()
        while (sink.pending.length > 0) sink.settle()
      }
      if (ledger.state === 'failed') break
    }
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.kind).toBe('footer')
    expect(footer.truncated).toBe(true)
    expect(footer.incomplete).toBe(true)
    // The byte cap ended acceptance well before the record cap.
    expect(ledger.counters.acceptedRecords).toBeLessThan(LEDGER_LIMITS.totalRecords - 1)
    const totalFileBytes = Buffer.byteLength(sink.text(), 'utf8')
    expect(totalFileBytes).toBeLessThanOrEqual(LEDGER_LIMITS.totalBytes)
    expect(totalFileBytes).toBe(
      (footer.bytesWritten as number) + Buffer.byteLength(`${JSON.stringify(footer)}\n`, 'utf8'),
    )
  })

  it('closes the exact reserved-byte boundary with flight, queue and overflow', () => {
    const { ledger, clock, scheduler, sink } = harness()
    expect(ledger.counters.queueBytes).toBeGreaterThan(0) // the queued header
    scheduler.run()
    expect(sink.pending.length).toBe(1) // its batch leaves in flight
    // One real overflow replacement joins the same account.
    const fat = {
      id: 'f'.repeat(128),
      method: 'f'.repeat(128),
      params: {
        operationId: 'g'.repeat(128),
        jobId: 'g'.repeat(128),
        projectId: 'g'.repeat(128),
        capability: 'g'.repeat(128),
      },
    }
    ledger.recordRequestPrepared(1, fat, 'f'.repeat(128), 'f'.repeat(128), 262144)
    expect(ledger.counters.overflow).toBe(1)
    // A writeSettled line mirrors the writer serialization key order exactly.
    const settledJson = (length: number, seq: number, ms: number) =>
      JSON.stringify({
        kind: 'writeSettled',
        requestId: 'x'.repeat(length),
        writeError: false,
        seq,
        monotonicMs: ms,
      })
    const inFlightBytes = () => (sink.pending.length > 0 ? sink.writes.at(-1)!.byteLength : 0)
    // Settled batches, queued lines and the one live flight are disjoint
    // accounting sets; together with the footer reserve they are the whole
    // live reservation.
    const reserved = () =>
      LEDGER_LIMITS.totalBytes -
      (1025 + ledger.counters.bytesWritten + ledger.counters.queueBytes + inFlightBytes())
    // Coarse fillers flush and settle so the queue never nears its slot cap.
    const id128 = 'f'.repeat(128)
    const id60 = 'g'.repeat(60)
    const coarse = {
      id: id128,
      method: id128,
      params: { operationId: id60, jobId: id60, projectId: id60, capability: id60 },
    }
    while (reserved() > 600) {
      ledger.recordRequestPrepared(1, coarse, 'unused', 'request', 262144)
      scheduler.runAll()
      while (sink.pending.length > 0) sink.settle()
      expect(ledger.counters.queueLength).toBeLessThan(LEDGER_LIMITS.queueSlots)
    }
    clock.advance(7)
    // A writeSettled line's length moves one byte per requestId character.
    const lenAt = (length: number) =>
      Buffer.byteLength(settledJson(length, ledger.counters.acceptedRecords + 1, 7), 'utf8')
    // Fine step with mid-size ids until the tail fits held-flight + exact-fit.
    while (reserved() > 380) {
      ledger.recordWriteSettled('y'.repeat(32), false)
      scheduler.runAll()
      while (sink.pending.length > 0) sink.settle()
    }
    // Choose the held record's own length so that after it crosses the
    // boundary in flight, one final legal-length record fits exactly.
    const reserveBefore = reserved()
    let heldLength = 1
    for (; heldLength <= 128; heldLength += 1) {
      const remaining = reserveBefore - (lenAt(heldLength) + 1)
      const filler = remaining - lenAt(1)
      if (filler >= 1 && filler <= 128) break
    }
    expect(heldLength).toBeLessThanOrEqual(128)
    // Hold one real batch in flight across the critical boundary: its bytes
    // are neither in bytesWritten nor in queueBytes until it settles.
    ledger.recordWriteSettled('h'.repeat(heldLength), false)
    scheduler.runAll()
    expect(sink.pending.length).toBe(1)
    const seqNow = ledger.counters.acceptedRecords + 1
    const exactLength = reserved() - 1
    const fillerLength = exactLength - lenAt(1) + 1
    expect(fillerLength).toBeGreaterThanOrEqual(1)
    expect(fillerLength).toBeLessThanOrEqual(128)
    const exactId = 'z'.repeat(fillerLength)
    expect(Buffer.byteLength(settledJson(fillerLength, seqNow, 7), 'utf8')).toBe(exactLength)
    const acceptedBefore = ledger.counters.acceptedRecords
    const queueBefore = ledger.counters.queueBytes
    const writesBefore = sink.writes.length
    // The last fitting record is accepted while the held flight stays open.
    ledger.recordWriteSettled(exactId, false)
    expect(ledger.counters.acceptedRecords).toBe(acceptedBefore + 1)
    expect(ledger.counters.queueBytes).toBe(queueBefore + exactLength + 1)
    expect(reserved()).toBe(0)
    expect(sink.pending.length).toBe(1)
    // The next record no longer fits: rejected with the count unchanged and
    // no second flight scheduled behind the open one.
    ledger.recordWriteSettled(exactId, false)
    expect(ledger.counters.acceptedRecords).toBe(acceptedBefore + 1)
    expect(ledger.counters.queueBytes).toBe(queueBefore + exactLength + 1)
    scheduler.runAll()
    expect(sink.pending.length).toBe(1)
    expect(sink.writes.length).toBe(writesBefore)
    while (sink.pending.length > 0) sink.settle()
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.kind).toBe('footer')
    expect(footer.truncated).toBe(true)
    expect(footer.incomplete).toBe(true)
    const lastRecord = all[all.length - 2]! as Record<string, unknown>
    expect(lastRecord.requestId).toBe(exactId)
    const totalFileBytes = Buffer.byteLength(sink.text(), 'utf8')
    expect(totalFileBytes).toBeLessThanOrEqual(LEDGER_LIMITS.totalBytes)
    expect(totalFileBytes).toBe(
      (footer.bytesWritten as number) + Buffer.byteLength(`${JSON.stringify(footer)}\n`, 'utf8'),
    )
  })

  it('accepts a deterministic exactly-1024-byte record with full correlation', () => {
    // The exact cap is reached across several whitelisted fields, each one
    // individually legal (bounded length, whitelisted charset); no single
    // field is inflated past its own protocol bound.
    const filler = (length: number) => 'x'.repeat(length)
    const lengths: Record<string, number> = {
      requestId: 1,
      method: 1,
      phase: 1,
      operationId: 1,
      jobId: 1,
      projectId: 1,
      capability: 1,
    }
    const build = () => ({
      kind: 'requestPrepared',
      seq: 2,
      monotonicMs: 0,
      generation: 1,
      requestId: filler(lengths.requestId!),
      method: filler(lengths.method!),
      phase: filler(lengths.phase!),
      paramsByteLength: 262144,
      operationId: filler(lengths.operationId!),
      jobId: filler(lengths.jobId!),
      projectId: filler(lengths.projectId!),
      capability: filler(lengths.capability!),
    })
    let needed = LEDGER_LIMITS.maxRecordBytes - Buffer.byteLength(JSON.stringify(build()), 'utf8')
    expect(needed).toBeGreaterThan(0)
    for (const field of Object.keys(lengths)) {
      const room = Math.min(127, needed)
      lengths[field] = 1 + room
      needed -= room
    }
    expect(needed).toBe(0)
    for (const [field, length] of Object.entries(lengths)) {
      expect(length, field).toBeLessThanOrEqual(128)
    }
    const exact = build()
    for (const value of [
      exact.requestId,
      exact.method,
      exact.phase,
      exact.operationId,
      exact.jobId,
      exact.projectId,
      exact.capability,
    ]) {
      expect(value).toMatch(/^[A-Za-z0-9._:-]+$/)
    }
    expect(Buffer.byteLength(JSON.stringify(exact), 'utf8')).toBe(LEDGER_LIMITS.maxRecordBytes)
    const { ledger, scheduler, sink } = harness()
    ledger.recordRequestPrepared(
      1,
      {
        id: exact.requestId,
        method: exact.method,
        params: {
          operationId: exact.operationId,
          jobId: exact.jobId,
          projectId: exact.projectId,
          capability: exact.capability,
        },
      },
      exact.method,
      exact.phase,
      262144,
    )
    ledger.requestStop()
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    const all = lines(sink.text())
    const record = all.find(
      (line) => line.kind === 'requestPrepared' && line.method === exact.method,
    ) as Record<string, unknown>
    expect(record).toBeDefined()
    // A maximal valid record keeps its ordinary full correlation fields.
    expect(record).toMatchObject({
      requestId: exact.requestId,
      method: exact.method,
      phase: exact.phase,
      operationId: exact.operationId,
      jobId: exact.jobId,
      projectId: exact.projectId,
      capability: exact.capability,
      paramsByteLength: 262144,
    })
    // JSON bytes and the LF are accounted separately in the file budget.
    expect(Buffer.byteLength(JSON.stringify(record), 'utf8')).toBe(LEDGER_LIMITS.maxRecordBytes)
    const footer = all[all.length - 1]! as Record<string, unknown>
    expect(footer.incomplete).toBe(false)
    // One byte over the cap, still with every field individually legal.
    const grow = Object.keys(lengths).find((field) => lengths[field]! < 128)!
    lengths[grow] = lengths[grow]! + 1
    const over = build()
    expect(Buffer.byteLength(JSON.stringify(over), 'utf8')).toBe(LEDGER_LIMITS.maxRecordBytes + 1)
    const overHarness = harness()
    overHarness.ledger.recordRequestPrepared(
      1,
      {
        id: over.requestId,
        method: over.method,
        params: {
          operationId: over.operationId,
          jobId: over.jobId,
          projectId: over.projectId,
          capability: over.capability,
        },
      },
      over.method,
      over.phase,
      262144,
    )
    overHarness.ledger.requestStop()
    overHarness.scheduler.runAll()
    while (overHarness.sink.pending.length > 0) overHarness.sink.settle()
    const overLines = lines(overHarness.sink.text())
    expect(
      overLines.some((line) => line.kind === 'requestPrepared' && line.method === over.method),
    ).toBe(false)
    expect(overLines.some((line) => line.kind === 'recordOverflowNote')).toBe(true)
    const overFooter = overLines[overLines.length - 1]! as Record<string, unknown>
    expect(overFooter.overflow).toBe(1)
    expect(overFooter.incomplete).toBe(true)
  })

  it('bounds queue, bytes, schedule and flight while a callback never arrives', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordWriteSettled('first', false)
    scheduler.run() // single batch in flight, callback withheld
    expect(sink.writes.length).toBe(1)
    for (let index = 0; index < LEDGER_LIMITS.queueSlots + 40; index += 1)
      ledger.recordWriteSettled(`held-${index}`, false)
    expect(scheduler.tasks.length).toBeLessThanOrEqual(1)
    expect(ledger.counters.queueLength).toBeLessThanOrEqual(LEDGER_LIMITS.queueSlots)
    expect(ledger.counters.queueBytes).toBeLessThanOrEqual(
      LEDGER_LIMITS.queueSlots * (LEDGER_LIMITS.maxRecordBytes + 1),
    )
    expect(sink.writes.length).toBe(1)
    ledger.recordSessionStart(9, null)
    ledger.recordChildClosed(9, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    // Still one in-flight write; the footer stays pending confirmation.
    expect(sink.writes.length).toBe(1)
    expect(ledger.counters.inFlight).toBe(true)
    expect(ledger.counters.footerWritten).toBe(false)
    sink.settle()
    scheduler.runAll()
    sink.settle()
    const all = lines(sink.text())
    expect(all[all.length - 1]).toMatchObject({ kind: 'footer' })
  })

  it('fails when a success callback omits the byte completion', () => {
    const inline = { now: () => 0, schedule: (fn: () => void) => fn() }
    const unknownBytes = TransportLedger.open({
      path: '/unused',
      launchId: null,
      appPid: 1,
      platform: 'test',
      controls: inline,
      sinkFactory: () =>
        ({
          write: (
            _chunk: Buffer,
            callback: (error: Error | null | undefined, bytesWritten?: number) => void,
          ) => {
            callback(null) // success without any completion count
          },
          close: () => undefined,
          onClose: () => undefined,
          onError: () => undefined,
        }) as unknown as LedgerSink,
    })
    expect(unknownBytes.state).toBe('failed')
    expect(unknownBytes.counters.footerWritten).toBe(false)
  })

  it('requests exactly one bounded failure close of the opened sink', () => {
    const { ledger, scheduler, sink } = harness()
    ledger.recordWriteSettled('a', false)
    scheduler.run()
    expect(sink.pending.length).toBe(1)
    sink.settleShort()
    expect(ledger.state).toBe('failed')
    expect(sink.closeCount).toBe(1)
    // Repeated failures never request a second close.
    ledger.recordWriteSettled('b', false)
    sink.emitError(new Error('late stream error'))
    expect(sink.closeCount).toBe(1)
    expect(ledger.state).toBe('failed')
  })

  it('production adapter writes complete files and confirms closed', async () => {
    const { ledger, path } = await productionSinkHarness()
    ledger.recordSessionStart(1, 11)
    ledger.recordChildClosed(1, 0, null)
    ledger.requestStop()
    const deadline = Date.now() + 5000
    while (!['closed', 'failed'].includes(ledger.state) && Date.now() < deadline) {
      await new Promise((done) => setImmediate(done))
      await new Promise((done) => setTimeout(done, 10))
    }
    expect(ledger.state).toBe('closed')
    expect(ledger.counters.footerWritten).toBe(true)
    const { readFile } = await import('node:fs/promises')
    const text = await readFile(path, 'utf8')
    const all = lines(text)
    expect(all[0]).toMatchObject({ kind: 'header' })
    expect(all[all.length - 1]).toMatchObject({ kind: 'footer', incomplete: false })
  })

  it('production adapter keeps failure semantics on an existing file', async () => {
    const { mkdtemp, writeFile, readFile } = await import('node:fs/promises')
    const { tmpdir } = await import('node:os')
    const { join } = await import('node:path')
    const root = await mkdtemp(join(tmpdir(), 'engine-ledger-prod-'))
    const path = join(root, 'engine-transport-ledger.jsonl')
    await writeFile(path, 'pre-existing\n', 'utf8')
    const ledger = TransportLedger.open({
      path,
      launchId: null,
      appPid: process.pid,
      platform: 'test',
    })
    ledger.recordWriteSettled('a', false)
    await new Promise((done) => setImmediate(done))
    await new Promise((done) => setTimeout(done, 20))
    expect(ledger.state).toBe('failed')
    // Exclusive create never touches the stale file.
    expect(await readFile(path, 'utf8')).toBe('pre-existing\n')
  })

  it('a failing real close keeps the ledger failed instead of confirming closed', () => {
    const { ledger, scheduler, sink } = harness()
    sink.deferClose()
    ledger.recordSessionStart(1, 7)
    ledger.recordChildClosed(1, 0, null)
    ledger.requestStop()
    scheduler.runAll()
    sink.settle() // footer batch succeeds: sealed, close requested
    expect(ledger.state).toBe('sealed')
    sink.flushClose(new Error('real close failed'))
    expect(ledger.state).toBe('failed')
    // The footer itself was written; the close failure keeps evidence
    // incomplete by state, and no further writes happen.
    const writes = sink.writes.length
    sink.flushClose(new Error('again'))
    expect(ledger.state).toBe('failed')
    expect(sink.writes.length).toBe(writes)
  })

  it('record internals never propagate extraction failures', () => {
    const { ledger, scheduler, sink } = harness()
    const hostile = new Proxy(
      {},
      {
        get() {
          throw new Error('no reads')
        },
      },
    )
    ledger.recordRequestPrepared(1, hostile, 'health', 'request', 3)
    ledger.recordResponse(1, hostile, true, 3, hostile)
    ledger.recordNotification(1, hostile)
    ledger.recordHello(1, hostile)
    ledger.recordFence(1, hostile, 0)
    scheduler.runAll()
    while (sink.pending.length > 0) sink.settle()
    expect(ledger.state).not.toBe('failed')
    expect(ledger.counters.recordErrors).toBe(0)
  })
})
