import { open, type FileHandle } from 'node:fs/promises'
import { randomUUID } from 'node:crypto'
import { join, resolve } from 'node:path'

/**
 * Bounded passive transport evidence for explicitly observed T02 Windows
 * unpackaged E2E launches. Diagnostics only: records prove main-process
 * observations (client write settle, matched response/notification delivery),
 * never durable commits or independent engine acceptance. Any loss, dropped
 * record, overflow replacement, failed/short write, missing callback or
 * missing footer leaves the file incomplete evidence.
 *
 * Footer semantics: a footer line is serialized lazily at batch assembly, so
 * its recordsWritten/bytesWritten are prefix totals of everything written
 * before the footer line itself; the footer confirmation only happens when
 * the batch that actually contains the footer succeeds. `failed` is
 * irreversible: late callbacks neither account nor resurrect sealing.
 */

export const LEDGER_FILE_NAME = 'engine-transport-ledger.jsonl'
export const LEDGER_FLAG = 'ONTOLEARN_E2E_TRANSPORT_LEDGER'
export const LEDGER_LAUNCH_ID = 'ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID'

const QUEUE_SLOTS = 64
const CHILDREN_CAP = 64
const TOTAL_RECORDS = 4096
const TOTAL_BYTES = 524288
const MAX_RECORD_BYTES = 1024
const FOOTER_RESERVE_BYTES = MAX_RECORD_BYTES + 1
const FOOTER_RESERVE_RECORDS = 1
// Saturation bound for attempt counters that total caps do not already bound
// (drop attempts and guarded-record failures). Saturated counters force
// incomplete evidence and never wrap.
const COUNTER_SATURATION = 4096
const ID_TEXT_LIMIT = 128
const ID_TEXT_PATTERN = /^[A-Za-z0-9._:-]+$/
const PROFILE_PREFIX = 'ontolearn-e2e-profile-'
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/

/** Fixed caps shared with tests and the bounded collector. */
export const LEDGER_LIMITS = {
  queueSlots: QUEUE_SLOTS,
  childrenCap: CHILDREN_CAP,
  totalRecords: TOTAL_RECORDS,
  totalBytes: TOTAL_BYTES,
  maxRecordBytes: MAX_RECORD_BYTES,
  counterSaturation: COUNTER_SATURATION,
  collectionCapBytes: TOTAL_BYTES + 1,
} as const

export interface LedgerSink {
  write(
    chunk: Buffer,
    callback: (error: Error | null | undefined, bytesWritten?: number) => void,
  ): void
  close(): void
  onClose(listener: (error: Error | null) => void): void
  onError(listener: (error: Error) => void): void
}

export interface LedgerControls {
  now(): number
  schedule(fn: () => void): void
}

const productionControls: LedgerControls = {
  now: () => performance.now(),
  schedule: (fn) => {
    setImmediate(fn)
  },
}

/**
 * Byte-explicit exclusive-create sink over one owned FileHandle. Each write is
 * a single bounded write(2): the callback reports the actual byte completion,
 * and a short write fails immediately — no continuation, no retry. The close
 * listeners fire only after the real close completes; a failing close keeps
 * failure semantics and never confirms success. Exclusive creation keeps an
 * existing file from ever being replaced or qualified as this launch.
 */
function fileSink(path: string): LedgerSink {
  let handle: FileHandle | null = null
  let openError: Error | null = null
  let opening: Promise<boolean> | null = null
  let closed = false
  const errorListeners: ((error: Error) => void)[] = []
  const closeListeners: ((error: Error | null) => void)[] = []
  const ensure = (): Promise<boolean> => {
    if (opening) return opening
    opening = open(path, 'ax')
      .then((file) => {
        handle = file
        return true
      })
      .catch((error: unknown) => {
        openError = error instanceof Error ? error : new Error(String(error))
        for (const listener of errorListeners) listener(openError)
        return false
      })
    return opening
  }
  return {
    write(chunk, callback) {
      void ensure().then((ready) => {
        if (!ready) {
          callback(openError ?? new Error('ledger file unavailable'))
          return
        }
        handle!
          .write(chunk)
          .then((result) => {
            if (result.bytesWritten !== chunk.byteLength) {
              callback(new Error(`short write: ${result.bytesWritten}/${chunk.byteLength}`))
              return
            }
            callback(null, result.bytesWritten)
          })
          .catch((error: unknown) => {
            callback(error instanceof Error ? error : new Error(String(error)))
          })
      })
    },
    close() {
      if (closed) return
      closed = true
      void ensure().then(async (ready) => {
        let closeError: Error | null = null
        try {
          if (ready) await handle!.close()
        } catch (error: unknown) {
          closeError = error instanceof Error ? error : new Error(String(error))
        } finally {
          for (const listener of closeListeners) listener(closeError)
        }
      })
    },
    onClose(listener) {
      closeListeners.push(listener)
    },
    onError(listener) {
      errorListeners.push(listener)
    },
  }
}

/** One self-guarded whitelisted id read per field; callers never rely on an outer catch. */
function readId(source: unknown, key: string): string | null {
  let value: unknown
  try {
    if (source === null || typeof source !== 'object') return null
    value = (source as Record<string, unknown>)[key]
  } catch {
    return null
  }
  if (typeof value !== 'string') return null
  return value.length <= ID_TEXT_LIMIT && ID_TEXT_PATTERN.test(value) ? value : null
}

function readObject(source: unknown, key: string): unknown {
  try {
    if (source === null || typeof source !== 'object') return null
    const value = (source as Record<string, unknown>)[key]
    return value !== null && typeof value === 'object' ? value : null
  } catch {
    return null
  }
}

interface HeaderRecord {
  kind: 'header'
  schema: 1
  owner: string
  launchId: string | null
  appPid: number
  platform: string
  seq: number
  monotonicMs: number
}

interface FooterRecord {
  kind: 'footer'
  stopRequested: boolean
  childrenOpenCount: number
  childrenOverflow: boolean
  saturated: boolean
  recordsWritten: number
  bytesWritten: number
  droppedQueue: number
  overflow: number
  writeErrors: number
  recordErrors: number
  truncated: boolean
  incomplete: boolean
  seq: number
  monotonicMs: number
}

export type PendingLedgerEvent = Omit<LedgerEvent, 'seq' | 'monotonicMs'>

export interface LedgerEvent {
  kind:
    | 'requestRejected'
    | 'requestPrepared'
    | 'writeSettled'
    | 'writeThrown'
    | 'requestTimeout'
    | 'response'
    | 'notification'
    | 'sessionStart'
    | 'hello'
    | 'fence'
    | 'childClosed'
  seq: number
  monotonicMs: number
  generation?: number
  requestId?: string | null
  method?: string | null
  reason?: string
  phase?: string | null
  paramsByteLength?: number
  writeError?: boolean
  ok?: boolean
  payloadByteLength?: number
  engineSessionId?: string | null
  operationId?: string | null
  jobId?: string | null
  projectId?: string | null
  capability?: string | null
  state?: string | null
  childPid?: number | null
  exitCode?: number | null
  signalCode?: string | null
  fenceCode?: string | null
  anomalies?: number
}

export type LedgerState = 'arming' | 'active' | 'sealed' | 'closed' | 'failed'

/** Launch-level enablement resolved by main from its trusted environment. */
export function resolveTransportLedger(input: {
  flag: string | undefined
  launchId: string | undefined
  userDataPath: string
  packaged: boolean
  platform: string
  /** The actual --user-data-dir argv value; must match the live userData path. */
  userDataArg: string | undefined
}): { transportLedger: { path: string; launchId: string | null } } | undefined {
  if (input.packaged || input.flag !== '1' || input.platform !== 'win32') return undefined
  if (typeof input.launchId !== 'string' || !UUID_PATTERN.test(input.launchId)) return undefined
  if (typeof input.userDataArg !== 'string' || input.userDataArg.length === 0) return undefined
  const profile = input.userDataPath.split(/[\\/]/).pop() ?? ''
  const suffix = profile.slice(PROFILE_PREFIX.length)
  if (
    !profile.startsWith(PROFILE_PREFIX) ||
    suffix.length < 6 ||
    suffix.length > 48 ||
    !/^[A-Za-z0-9_-]+$/.test(suffix) ||
    resolve(input.userDataArg) !== resolve(input.userDataPath)
  )
    return undefined
  return {
    transportLedger: {
      path: join(input.userDataPath, LEDGER_FILE_NAME),
      launchId: input.launchId,
    },
  }
}

export class TransportLedger {
  readonly owner = randomUUID()
  readonly launchId: string | null
  readonly appPid: number
  readonly platform: string
  #state: LedgerState
  #controls: LedgerControls
  #sinkFactory: () => LedgerSink
  #sink: LedgerSink | undefined
  #queue: string[] = []
  #queueBytes = 0
  #inFlight = false
  #flushScheduled = false
  #acceptedRecords = 0
  #reservedBytes = FOOTER_RESERVE_BYTES
  #recordsWritten = 0
  #bytesWritten = 0
  #droppedQueue = 0
  #overflow = 0
  #writeErrors = 0
  #recordErrors = 0
  #saturated = false
  #sinkCloseRequested = false
  #seq = 0
  #terminal = false
  #truncated = false
  #footerPending = false
  #footerWritten = false
  #stopRequested = false
  #childrenOpen = new Set<number>()
  #childrenOverflow = false

  private constructor(options: {
    launchId: string | null
    appPid: number
    platform: string
    controls?: LedgerControls
    sinkFactory: () => LedgerSink
  }) {
    this.launchId = options.launchId
    this.appPid = options.appPid
    this.platform = options.platform
    this.#state = 'arming'
    this.#controls = options.controls ?? productionControls
    this.#sinkFactory = options.sinkFactory
    this.#enqueueHeader()
  }

  static open(options: {
    path: string
    launchId: string | null
    appPid: number
    platform: string
    controls?: LedgerControls
    sinkFactory?: () => LedgerSink
  }): TransportLedger {
    const path = options.path
    return new TransportLedger({
      launchId: options.launchId,
      appPid: options.appPid,
      platform: options.platform,
      controls: options.controls,
      sinkFactory: options.sinkFactory ?? (() => fileSink(path)),
    })
  }

  get state(): LedgerState {
    return this.#state
  }

  get counters(): {
    acceptedRecords: number
    recordsWritten: number
    bytesWritten: number
    droppedQueue: number
    overflow: number
    writeErrors: number
    recordErrors: number
    queueLength: number
    queueBytes: number
    inFlight: boolean
    stopRequested: boolean
    childrenOpen: number
    childrenOverflow: boolean
    saturated: boolean
    footerPending: boolean
    footerWritten: boolean
  } {
    return {
      acceptedRecords: this.#acceptedRecords,
      recordsWritten: this.#recordsWritten,
      bytesWritten: this.#bytesWritten,
      droppedQueue: this.#droppedQueue,
      overflow: this.#overflow,
      writeErrors: this.#writeErrors,
      recordErrors: this.#recordErrors,
      queueLength: this.#queue.length,
      queueBytes: this.#queueBytes,
      inFlight: this.#inFlight,
      stopRequested: this.#stopRequested,
      childrenOpen: this.#childrenOpen.size,
      childrenOverflow: this.#childrenOverflow,
      saturated: this.#saturated,
      footerPending: this.#footerPending,
      footerWritten: this.#footerWritten,
    }
  }

  recordSessionStart(generation: number, childPid: number | null): void {
    this.#guarded(() => {
      if (this.#terminal || this.#state === 'failed' || this.#state === 'closed') return
      if (this.#childrenOpen.size >= CHILDREN_CAP) this.#childrenOverflow = true
      else this.#childrenOpen.add(generation)
      this.#accept({ kind: 'sessionStart', generation, childPid })
    })
  }

  recordHello(generation: number, hello: unknown): void {
    this.#guarded(() => {
      this.#accept({
        kind: 'hello',
        generation,
        engineSessionId: readId(hello, 'engineSessionId'),
      })
    })
  }

  recordRequestRejected(reason: string, method: string): void {
    this.#guarded(() => {
      this.#accept({
        kind: 'requestRejected',
        reason,
        method: readId({ method }, 'method'),
      })
    })
  }

  recordRequestPrepared(
    generation: number,
    preparedClone: unknown,
    method: string,
    phase: string,
    paramsByteLength: number,
  ): void {
    this.#guarded(() => {
      const params = readObject(preparedClone, 'params')
      this.#accept({
        kind: 'requestPrepared',
        generation,
        requestId: readId(preparedClone, 'id'),
        method: readId(preparedClone, 'method'),
        phase: readId({ phase }, 'phase'),
        paramsByteLength,
        operationId: readId(params, 'operationId'),
        jobId: readId(params, 'jobId'),
        projectId: readId(params, 'projectId'),
        capability: readId(params, 'capability'),
      })
    })
  }

  recordWriteSettled(requestId: string, writeError: boolean): void {
    this.#guarded(() => {
      this.#accept({
        kind: 'writeSettled',
        requestId: readId({ requestId }, 'requestId'),
        writeError,
      })
    })
  }

  recordWriteThrown(requestId: string): void {
    this.#guarded(() => {
      this.#accept({
        kind: 'writeThrown',
        requestId: readId({ requestId }, 'requestId'),
      })
    })
  }

  recordRequestTimeout(generation: number, requestId: string): void {
    this.#guarded(() => {
      this.#accept({
        kind: 'requestTimeout',
        generation,
        requestId: readId({ requestId }, 'requestId'),
      })
    })
  }

  recordResponse(
    generation: number,
    preparedClone: unknown,
    ok: boolean,
    payloadByteLength: number,
    result: unknown,
  ): void {
    this.#guarded(() => {
      const method = readId(preparedClone, 'method')
      const event: PendingLedgerEvent = {
        kind: 'response',
        generation,
        requestId: readId(preparedClone, 'id'),
        method,
        ok,
        payloadByteLength,
      }
      if (ok && method === 'job.create') {
        // Schema result_job.create is the job object itself (top-level fields).
        event.operationId = readId(result, 'operationId')
        event.jobId = readId(result, 'jobId')
        event.projectId = readId(result, 'projectId')
        event.state = readId(result, 'state')
      }
      if (ok && method === 'project.create') {
        // Synchronous creation result: operation/project only, never a Job.
        event.operationId = readId(result, 'operationId')
        event.projectId = readId(result, 'projectId')
      }
      this.#accept(event)
    })
  }

  recordNotification(generation: number, notification: unknown): void {
    this.#guarded(() => {
      const event: PendingLedgerEvent = { kind: 'notification', generation }
      if (readId(notification, 'event') === 'job.state') {
        const data = readObject(notification, 'data')
        event.projectId = readId(notification, 'projectId')
        event.jobId = readId(notification, 'jobId')
        // Job state lives in the schema-validated data.state field.
        event.state = readId(data, 'state')
        event.operationId = readId(data, 'operationId')
      }
      this.#accept(event)
    })
  }

  recordFence(generation: number, fenceCode: unknown, anomalies: number): void {
    this.#guarded(() => {
      this.#accept({
        kind: 'fence',
        generation,
        fenceCode: readId({ code: fenceCode }, 'code'),
        anomalies,
      })
    })
  }

  recordChildClosed(generation: number, exitCode: number | null, signalCode: string | null): void {
    this.#guarded(() => {
      this.#childrenOpen.delete(generation)
      this.#accept({
        kind: 'childClosed',
        generation,
        exitCode,
        signalCode: typeof signalCode === 'string' && signalCode.length <= 16 ? signalCode : null,
      })
      this.#sealIfPossible()
    })
  }

  requestStop(): void {
    this.#guarded(() => {
      this.#stopRequested = true
      this.#sealIfPossible()
    })
  }

  #guarded(body: () => void): void {
    try {
      body()
    } catch {
      this.#recordErrors = this.#saturate(this.#recordErrors)
    }
  }

  /** Fixed saturating increment: attempt counters never wrap past the cap. */
  #saturate(current: number): number {
    const next = current + 1
    if (next >= COUNTER_SATURATION) {
      this.#saturated = true
      return COUNTER_SATURATION
    }
    return next
  }

  #enqueueHeader(): void {
    const header: HeaderRecord = {
      kind: 'header',
      schema: 1,
      owner: this.owner,
      launchId: this.launchId,
      appPid: this.appPid,
      platform: this.platform,
      seq: ++this.#seq,
      monotonicMs: this.#controls.now(),
    }
    const line = JSON.stringify(header)
    this.#queue.push(line)
    this.#queueBytes += Buffer.byteLength(line, 'utf8') + 1
    this.#acceptedRecords += 1
    this.#reservedBytes += Buffer.byteLength(line, 'utf8') + 1
    this.#state = 'active'
    this.#scheduleFlush()
  }

  #accept(event: PendingLedgerEvent): void {
    if (this.#terminal || this.#state === 'failed' || this.#state === 'closed') return
    // Sequence numbers are committed only for accepted lines: rejected or
    // dropped attempts never consume sequence space, so every accepted record
    // stays uniquely identifiable up to the total record cap.
    const tentativeSeq = Math.min(this.#seq + 1, TOTAL_RECORDS)
    const record: LedgerEvent = {
      ...event,
      seq: tentativeSeq,
      monotonicMs: this.#controls.now(),
    }
    let line: string | undefined = JSON.stringify(record)
    if (line === undefined || Buffer.byteLength(line, 'utf8') > MAX_RECORD_BYTES) {
      this.#overflow = this.#saturate(this.#overflow)
      line = JSON.stringify({
        kind: 'recordOverflowNote',
        originalKind: String(event.kind).slice(0, 32),
        seq: tentativeSeq,
        monotonicMs: record.monotonicMs,
      })
    }
    const bytes = Buffer.byteLength(line, 'utf8') + 1
    if (
      this.#acceptedRecords >= TOTAL_RECORDS - FOOTER_RESERVE_RECORDS ||
      this.#reservedBytes + bytes > TOTAL_BYTES
    ) {
      // Cap exhaustion seals through the pending-footer path; queued records
      // keep their asynchronous drain, and the footer reports truncation.
      this.#truncated = true
      this.#terminal = true
      this.#footerPending = true
      this.#scheduleFlush()
      return
    }
    if (this.#queue.length >= QUEUE_SLOTS) {
      this.#droppedQueue = this.#saturate(this.#droppedQueue)
      return
    }
    this.#seq = tentativeSeq
    this.#queue.push(line)
    this.#queueBytes += bytes
    this.#acceptedRecords += 1
    this.#reservedBytes += bytes
    this.#scheduleFlush()
  }

  #sealIfPossible(): void {
    // Idempotent: once terminal (cap or seal), no later stop/close event can
    // request a second footer or write to an already-ended stream.
    if (this.#terminal || this.#footerPending) return
    if (this.#state === 'failed' || this.#state === 'closed') return
    if (this.#stopRequested && (this.#childrenOpen.size === 0 || this.#childrenOverflow)) {
      // Pending writes are not loss: the footer is serialized at batch
      // assembly after earlier batches have actually succeeded.
      this.#terminal = true
      this.#footerPending = true
      this.#scheduleFlush()
    }
  }

  #buildFooter(prefixRecords: number, prefixBytes: number): string {
    const footer: FooterRecord = {
      kind: 'footer',
      stopRequested: this.#stopRequested,
      childrenOpenCount: this.#childrenOpen.size,
      childrenOverflow: this.#childrenOverflow,
      // File-prefix totals: every JSONL line/byte that precedes the footer
      // line itself, including ordinary lines assembled in this same batch.
      recordsWritten: prefixRecords,
      bytesWritten: prefixBytes,
      droppedQueue: this.#droppedQueue,
      overflow: this.#overflow,
      writeErrors: this.#writeErrors,
      recordErrors: this.#recordErrors,
      truncated: this.#truncated,
      // Saturated counters can never support complete evidence.
      saturated: this.#saturated,
      incomplete:
        this.#truncated ||
        this.#saturated ||
        this.#droppedQueue > 0 ||
        this.#overflow > 0 ||
        this.#writeErrors > 0 ||
        this.#recordErrors > 0 ||
        this.#childrenOverflow,
      seq: Math.min(++this.#seq, TOTAL_RECORDS),
      monotonicMs: this.#controls.now(),
    }
    return JSON.stringify(footer)
  }

  #scheduleFlush(): void {
    if (this.#flushScheduled || this.#inFlight) return
    if (this.#queue.length === 0 && !this.#footerPending) return
    if (this.#state === 'failed' || this.#state === 'closed') return
    this.#flushScheduled = true
    this.#controls.schedule(() => {
      this.#flushScheduled = false
      this.#flush()
    })
  }

  #flush(): void {
    if (this.#inFlight) return
    if (this.#queue.length === 0 && !this.#footerPending) return
    if (this.#state === 'failed' || this.#state === 'closed') return
    const lines = this.#queue
    this.#queue = []
    this.#queueBytes = 0
    // The footer is appended at assembly time only: it never occupies an
    // ordinary queue slot, and its prefix counters cover every line of this
    // batch that physically precedes it in the file.
    const batchHasFooter = this.#footerPending
    if (batchHasFooter) {
      const prefixBytes =
        this.#bytesWritten +
        (lines.length > 0 ? Buffer.byteLength(`${lines.join('\n')}\n`, 'utf8') : 0)
      lines.push(this.#buildFooter(this.#recordsWritten + lines.length, prefixBytes))
      this.#footerPending = false
    }
    const chunk = Buffer.from(lines.join('\n') + '\n', 'utf8')
    this.#inFlight = true
    if (!this.#sink) {
      try {
        this.#sink = this.#sinkFactory()
        this.#sink.onError(() => this.#fail())
        this.#sink.onClose((closeError) => {
          if (this.#state === 'failed') return
          // Only a clean close after a written footer confirms 'closed'.
          this.#state = closeError || !this.#footerWritten ? 'failed' : 'closed'
        })
      } catch {
        this.#inFlight = false
        this.#fail()
        return
      }
    }
    const count = lines.length
    try {
      this.#sink.write(chunk, (error, bytesWritten) => {
        this.#inFlight = false
        if (this.#state === 'failed' || this.#state === 'closed') return
        if (error) {
          this.#fail()
          return
        }
        // The byte completion must be an explicit number equal to the chunk:
        // an unknown or short completion fails immediately with no retry, and
        // the file stays incomplete.
        if (typeof bytesWritten !== 'number' || bytesWritten !== chunk.byteLength) {
          this.#fail()
          return
        }
        this.#recordsWritten += count
        this.#bytesWritten += chunk.byteLength
        if (batchHasFooter) {
          this.#footerWritten = true
          this.#state = 'sealed'
          if (this.#sink && !this.#sinkCloseRequested) {
            this.#sinkCloseRequested = true
            this.#sink.close()
          }
          return
        }
        this.#scheduleFlush()
      })
    } catch {
      this.#inFlight = false
      this.#fail()
    }
  }

  #fail(): void {
    if (this.#state === 'failed' || this.#state === 'closed') return
    this.#state = 'failed'
    this.#writeErrors = this.#saturate(this.#writeErrors)
    this.#queue = []
    this.#queueBytes = 0
    this.#footerPending = false
    // One bounded asynchronous close of an already-opened sink; the failed
    // state absorbs its late completion, errors and callbacks. Never a write
    // retry and never a transport wait.
    if (this.#sink && !this.#sinkCloseRequested) {
      this.#sinkCloseRequested = true
      try {
        this.#sink.close()
      } catch {
        /* The already-failed state absorbs close-request errors. */
      }
    }
    // No retry and no footer: failed files stay incomplete by construction.
  }
}
