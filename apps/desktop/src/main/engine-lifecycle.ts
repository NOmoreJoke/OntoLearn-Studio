/** Internal transport accounting. Nothing here grants a location, scope or OS release. */
import { type ChildProcess } from 'node:child_process'
import { type EventEmitter } from 'node:events'
import { type Readable, type Writable } from 'node:stream'

export class LifecycleFault extends Error {
  constructor(readonly reason: 'input' | 'limit' | 'state' | 'unsupported' | 'identity') {
    super(reason)
  }
}
export interface SessionFacts {
  actualSupervisor: object
  actualChildOwner: object
  generation: number
  hostClientId: string
  engineSessionId: string
  profile: string
  registryHash: string
  engineVersion: string
  limits: Readonly<Record<string, number>>
}
export interface DispatchFacts extends SessionFacts {
  privateTicket: object
  originalRequest: Readonly<Record<string, unknown>>
  actualRequest: Readonly<Record<string, unknown>>
  requestHash: string
  frameBytes: number
  sourceEpoch: number
}
/** A real issuer must implement this in its actual trusted assembly; fixtures prove mechanics only. */
export interface DispatchSource {
  installInvalidationSink(actualSupervisor: object, invalidateOnly: () => void): void
  checkBeforeSpawnSync(facts: { actualSupervisor: object; generation: number }): void
  recordValidatedSession(facts: SessionFacts): void
  checkAndConsumeDispatchSync(originalDispatch: object, facts: DispatchFacts): void
  recordSessionTerminal(facts: SessionFacts): void
  execution?: ExecutionEvidenceProducer
}
export interface ExecutionEvidenceProducer {
  readonly incarnation: object
  reserveOperation(facts: {
    actualSupervisor: object
    privateTicket: object
    originalDispatch: object
    originalRequest: Readonly<Record<string, unknown>>
    completionPort: CompletionPort
  }): object
  cancelReservation(reservation: object): void
  bindOperation(reservation: object, facts: DispatchFacts): object
  bindAcceptedJob(observation: object, actualAcceptanceSource: object): void
  observe(observation: object, terminal: (issuedObservation: object) => void): OwnedObservation
  projectTerminal(issuedObservation: object, privateTicket: object): TerminalJobFact
  projectObservationCleanup(issuedCleanup: object, observation: object): void
}
export interface CompletionPort {
  request(
    privateTicket: object,
    method: 'job.get' | 'job.subscribe' | 'job.unsubscribe',
    params: Record<string, unknown>,
    currentReadDispatch: object,
  ): Promise<unknown>
}
export interface OwnedObservation {
  closeObservation(): unknown
}
export interface TerminalJobFact {
  operationId: string
  projectId: string
  jobId: string
  state: 'succeeded' | 'failed' | 'cancelled'
}
export interface ExecutionFact {
  kind: 'foreground-returned' | 'terminal-job'
  job?: TerminalJobFact
}
export interface DispatchOperation {
  readonly logicalOutcome: Promise<unknown>
  readonly dispatchObservation: 'not-written' | 'write-attempted'
  readonly operationExecution: Promise<ExecutionFact>
}
function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => (resolve = done))
  return { promise, resolve }
}
function scalarBytes(value: string): number {
  let count = 2
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i)
    if (code >= 0xd800 && code <= 0xdbff) {
      const low = value.charCodeAt(++i)
      if (!(low >= 0xdc00 && low <= 0xdfff)) throw new LifecycleFault('input')
      count += 4
    } else if (code >= 0xdc00 && code <= 0xdfff) throw new LifecycleFault('input')
    else if (code === 34 || code === 92 || [8, 9, 10, 12, 13].includes(code)) count += 2
    else if (code < 32) count += 6
    else count += code < 128 ? 1 : code < 2048 ? 2 : 3
    if (count > 262144) throw new LifecycleFault('limit')
  }
  return count
}
/** Account before stringify/clone; reject getters, cycles and non-JSON types without invoking them. */
export function ownJson(value: unknown, maximum = 262144): { value: unknown; bytes: number } {
  let bytes = 0
  let nodes = 0
  const ancestors = new Set<object>()
  const add = (n: number): void => {
    bytes += n
    if (bytes > maximum) throw new LifecycleFault('limit')
  }
  const walk = (item: unknown, depth: number): unknown => {
    if (++nodes > 262144 || depth > 32) throw new LifecycleFault('limit')
    if (item === null) {
      add(4)
      return null
    }
    if (typeof item === 'string') {
      add(scalarBytes(item))
      return item
    }
    if (typeof item === 'boolean') {
      add(item ? 4 : 5)
      return item
    }
    if (typeof item === 'number') {
      if (!Number.isFinite(item) || Math.abs(item) > Number.MAX_SAFE_INTEGER)
        throw new LifecycleFault('input')
      add(String(Object.is(item, -0) ? 0 : item).length)
      return item
    }
    if (!item || typeof item !== 'object' || ancestors.has(item)) throw new LifecycleFault('input')
    const array = Array.isArray(item)
    if (!array && ![Object.prototype, null].includes(Object.getPrototypeOf(item)))
      throw new LifecycleFault('input')
    ancestors.add(item)
    add(2)
    const names = Object.getOwnPropertyNames(item)
    if (names.length > maximum || Object.getOwnPropertySymbols(item).length)
      throw new LifecycleFault('limit')
    const result: unknown[] | Record<string, unknown> = array ? [] : Object.create(null)
    let count = 0
    for (const key of names) {
      if (array && key === 'length') continue
      const descriptor = Object.getOwnPropertyDescriptor(item, key)!
      if (!('value' in descriptor) || !descriptor.enumerable) throw new LifecycleFault('input')
      if (array && key !== String(count)) throw new LifecycleFault('input')
      if (count++) add(1)
      if (!array) add(scalarBytes(key) + 1)
      const owned = walk(descriptor.value, depth + 1)
      if (array) (result as unknown[]).push(owned)
      else Object.defineProperty(result, key, { value: owned, enumerable: true })
    }
    if (array && (item as unknown[]).length !== count) throw new LifecycleFault('input')
    ancestors.delete(item)
    return Object.freeze(result)
  }
  const owned = walk(value, 0)
  return { value: owned, bytes }
}
export function synchronous(result: unknown): void {
  if (result !== undefined) throw new LifecycleFault('unsupported')
}

type Stream = Readable | Writable
export interface DrainSnapshot {
  state: 'ended' | 'pending'
  ownedChildren: number
  starting: number
}
export interface TransportDrainOperation {
  readonly transportOwnershipLifetime: Promise<Readonly<{ kind: 'transport-ended' }>>
  observe(options: { waitMs: number }): Promise<Readonly<DrainSnapshot>>
}
export class ChildOwnership {
  #entries = new Set<OwnedChild>()
  #stopped = false
  #observers = new Set<() => void>()
  #done = deferred<Readonly<{ kind: 'transport-ended' }>>()
  #ended = false
  readonly operation: TransportDrainOperation
  constructor(readonly onClosed: (owner: object) => void) {
    this.operation = Object.freeze({
      transportOwnershipLifetime: this.#done.promise,
      observe: (options: { waitMs: number }) => this.#observe(options),
    })
  }
  reserve(): OwnedChild {
    if (this.#stopped) throw new LifecycleFault('state')
    if (this.#entries.size >= 2) throw new LifecycleFault('limit')
    const entry = new OwnedChild(this)
    this.#entries.add(entry)
    return entry
  }
  stopped(): void {
    this.#stopped = true
    this.changed()
  }
  entries(): readonly OwnedChild[] {
    return [...this.#entries]
  }
  release(entry: OwnedChild): void {
    if (!this.#entries.delete(entry)) return
    this.onClosed(entry.identity)
    this.changed()
  }
  changed(): void {
    if (this.#stopped && !this.#entries.size && !this.#ended) {
      this.#ended = true
      this.#done.resolve(Object.freeze({ kind: 'transport-ended' }))
    }
    for (const notify of [...this.#observers]) notify()
  }
  snapshot(): Readonly<DrainSnapshot> {
    return Object.freeze({
      state: this.#ended ? 'ended' : 'pending',
      ownedChildren: this.#entries.size,
      starting: [...this.#entries].filter((e) => !e.child).length,
    })
  }
  #observe(options: { waitMs: number }): Promise<Readonly<DrainSnapshot>> {
    if (
      !options ||
      Object.keys(options).length !== 1 ||
      !Number.isSafeInteger(options.waitMs) ||
      options.waitMs < 1 ||
      options.waitMs > 60000
    )
      return Promise.reject(new LifecycleFault('input'))
    if (this.#observers.size >= 8) return Promise.reject(new LifecycleFault('limit'))
    if (this.#ended) return Promise.resolve(this.snapshot())
    return new Promise((resolve) => {
      const finish = (): void => {
        clearTimeout(timer)
        this.#observers.delete(notify)
        resolve(this.snapshot())
      }
      const notify = (): void => {
        if (this.#ended) finish()
      }
      const timer = setTimeout(finish, options.waitMs)
      this.#observers.add(notify)
    })
  }
}
export class OwnedChild {
  readonly identity = Object.freeze({})
  child?: ChildProcess
  spawnEntered = false
  startingDone = false
  #childClosed = false
  #exited = false
  #retired = false
  #released = false
  #streams: Stream[] = []
  #protocolCleanups: (() => void)[] = []
  #terminalCleanups: (() => void)[] = []
  #killTimer?: ReturnType<typeof setTimeout>
  constructor(readonly book: ChildOwnership) {}
  listen<A extends unknown[]>(
    target: EventEmitter,
    event: string,
    listener: (...args: A) => void,
    once = false,
  ) {
    const forward = (...args: unknown[]) => listener(...(args as A))
    if (once) target.once(event, forward)
    else target.on(event, forward)
    this.#protocolCleanups.push(() => target.off(event, forward))
  }
  bind(child: ChildProcess): void {
    if (this.child || this.#released) throw new LifecycleFault('state')
    this.child = child
    this.#streams = [child.stdin, child.stdout, child.stderr].filter((s): s is Stream => !!s)
    const listen = (target: EventEmitter, event: string, listener: () => void): void => {
      target.on(event, listener)
      this.#terminalCleanups.push(() => target.off(event, listener))
    }
    listen(child, 'error', () => undefined)
    listen(child, 'exit', () => {
      this.#exited = true
      clearTimeout(this.#killTimer)
      this.#killTimer = undefined
      this.#check()
    })
    listen(child, 'close', () => {
      this.#childClosed = true
      clearTimeout(this.#killTimer)
      this.#killTimer = undefined
      this.#check()
    })
    for (const stream of this.#streams) {
      listen(stream, 'error', () => undefined)
      listen(stream, 'close', () => this.#check())
    }
  }
  finishStarting(): void {
    this.startingDone = true
    this.#check()
  }
  cancelNeverCreated(): void {
    if (this.spawnEntered || this.child) return
    this.#retired = true
    this.#check()
  }
  retire(): void {
    if (this.#retired) return
    this.#retired = true
    for (const cleanup of this.#protocolCleanups.splice(0)) cleanup()
    if (this.child && !this.#childClosed && !this.#exited) {
      try {
        this.child.kill()
      } catch {
        // A failed signal is not terminal; keep the real owner until close.
      }
      if (!this.#childClosed && !this.#exited) {
        this.#killTimer = setTimeout(() => {
          this.#killTimer = undefined
          if (!this.#exited && !this.#childClosed) {
            try {
              this.child?.kill('SIGKILL')
            } catch {
              // No unbounded retry or deletion of unknown ownership.
            }
          }
          this.#check()
        }, 1000)
        this.#killTimer.unref()
      }
    }
    this.#check()
  }
  #check(): void {
    if (this.#released || !this.#retired || !this.startingDone || this.#killTimer) return
    const neverCreated = !this.spawnEntered && !this.child
    if (
      !neverCreated &&
      (!this.child || !this.#childClosed || this.#streams.some((s) => !s.closed))
    )
      return
    this.#released = true
    for (const cleanup of this.#terminalCleanups.splice(0)) cleanup()
    this.book.release(this)
  }
}

export interface Ticket {
  readonly identity: object
  readonly pool: 'business' | 'completion' | 'hello' | 'ping'
  readonly method: string
  completionFor?: Ticket
  subscriptionIds: Set<string>
  request: Readonly<Record<string, unknown>> | undefined
  frame: Buffer | undefined
  originalDispatch: object | undefined
  bytes: number
  attempted: boolean
  foregroundDone: boolean
  executionEnded?: boolean
  background: boolean
  owner?: object
  producer?: ExecutionEvidenceProducer
  producerIncarnation?: object
  producerReservation?: object
  producerReserveEntered?: boolean
  cancelRequested?: boolean
  attemptedCancellation?: object
  observation?: object
  subscription?: OwnedObservation
  reservedRequest?: Readonly<Record<string, unknown>>
  watch: boolean
  jobId?: string
  operationId?: string
  projectId?: string
  execution: ReturnType<typeof deferred<ExecutionFact>>
}
export class DispatchAccounting {
  #tickets = new Set<Ticket>()
  #watches = new Set<Ticket>()
  #consumed = new WeakSet<object>()
  #operations = new Map<string, Ticket>()
  #counts = { business: 0, completion: 0, hello: 0, ping: 0 }
  #poolBytes = { business: 0, completion: 0, hello: 0, ping: 0 }
  constructor(readonly maximum: number) {}
  find(operationId: string): Ticket | undefined {
    return this.#operations.get(operationId)
  }
  owns(identity: object): Ticket | undefined {
    for (const ticket of this.#tickets) if (ticket.identity === identity) return ticket
    for (const ticket of this.#watches) if (ticket.identity === identity) return ticket
    return undefined
  }
  reserve(
    request: Readonly<Record<string, unknown>>,
    frame: Buffer | number,
    originalDispatch?: object,
    producer?: ExecutionEvidenceProducer,
    pool: Ticket['pool'] = 'business',
  ): Ticket {
    const params = request.params as Record<string, unknown>
    const bytes = typeof frame === 'number' ? frame : frame.byteLength
    if (!Number.isSafeInteger(bytes) || bytes < 1 || bytes > 262144)
      throw new LifecycleFault('limit')
    const background = request.method === 'job.create'
    if (originalDispatch && this.#consumed.has(originalDispatch))
      throw new LifecycleFault('identity')
    if (
      this.#counts[pool] >= (pool === 'business' ? this.maximum : 1) ||
      ((pool === 'hello' || pool === 'ping') && this.#counts.hello + this.#counts.ping >= 1) ||
      this.#poolBytes[pool] + bytes > (pool === 'business' ? 8388608 : 262144) ||
      (background && this.#watches.size >= 128)
    )
      throw new LifecycleFault('limit')
    const operationId =
      background && typeof params.operationId === 'string' ? params.operationId : undefined
    if (operationId && this.#operations.has(operationId)) throw new LifecycleFault('identity')
    const ticket: Ticket = {
      identity: Object.freeze({}),
      pool,
      method: String(request.method),
      subscriptionIds: new Set(),
      request,
      frame: typeof frame === 'number' ? undefined : frame,
      originalDispatch,
      bytes,
      attempted: false,
      foregroundDone: false,
      background,
      watch: background,
      producer,
      producerIncarnation: producer?.incarnation,
      operationId,
      projectId: typeof params.projectId === 'string' ? params.projectId : undefined,
      execution: deferred<ExecutionFact>(),
    }
    this.#tickets.add(ticket)
    ticket.reservedRequest = request
    this.#counts[pool]++
    this.#poolBytes[pool] += ticket.bytes
    if (operationId) this.#operations.set(operationId, ticket)
    if (background) this.#watches.add(ticket)
    if (originalDispatch) this.#consumed.add(originalDispatch)
    return ticket
  }
  foreground(ticket: Ticket): void {
    ticket.foregroundDone = true
    if (!ticket.background) {
      ticket.execution.resolve(Object.freeze({ kind: 'foreground-returned' }))
      this.#release(ticket)
    }
  }
  terminal(ticket: Ticket, fact: TerminalJobFact): void {
    if (
      fact.operationId !== ticket.operationId ||
      fact.projectId !== ticket.projectId ||
      !ticket.jobId ||
      fact.jobId !== ticket.jobId ||
      !['succeeded', 'failed', 'cancelled'].includes(fact.state)
    )
      throw new LifecycleFault('identity')
    ticket.executionEnded = true
    ticket.execution.resolve(
      Object.freeze({ kind: 'terminal-job', job: Object.freeze({ ...fact }) }),
    )
    this.#release(ticket)
  }
  cancelUnwritten(ticket: Ticket): void {
    if (ticket.attempted) return
    ticket.cancelRequested = true
    this.#release(ticket)
    if (ticket.producerReservation && ticket.producer) {
      if (ticket.attemptedCancellation === ticket.producerReservation) return
      ticket.attemptedCancellation = ticket.producerReservation
      try {
        synchronous(ticket.producer.cancelReservation(ticket.producerReservation))
        if (!ticket.observation) this.releaseWatch(ticket)
      } catch {
        // Real observation/capacity cleanup is unknown; retain its watch slot.
      }
    } else if (!ticket.producerReserveEntered) this.releaseWatch(ticket)
  }
  releaseWatch(ticket: Ticket): void {
    this.#watches.delete(ticket)
    ticket.watch = false
    ticket.subscription = undefined
    ticket.producerReservation = undefined
    ticket.attemptedCancellation = undefined
    // Ending this connection's notification ownership does not revoke an actual
    // producer's later terminal evidence for the still-counted original operation.
    if (!this.#tickets.has(ticket)) {
      ticket.observation = undefined
      ticket.producer = undefined
    }
  }
  ownerEnded(owner: object): void {
    for (const ticket of this.#watches) if (ticket.owner === owner) this.releaseWatch(ticket)
    for (const ticket of this.#tickets)
      if (ticket.owner === owner && (ticket.pool === 'hello' || ticket.pool === 'ping'))
        this.#release(ticket)
  }
  stopUnwritten(): void {
    for (const ticket of [...this.#tickets]) if (!ticket.attempted) this.cancelUnwritten(ticket)
  }
  #release(ticket: Ticket): void {
    if (!this.#tickets.delete(ticket)) return
    this.#counts[ticket.pool]--
    this.#poolBytes[ticket.pool] -= ticket.bytes
    if (ticket.operationId && this.#operations.get(ticket.operationId) === ticket)
      this.#operations.delete(ticket.operationId)
    ticket.bytes = 0
    ticket.request = undefined
    ticket.frame = undefined
    ticket.originalDispatch = undefined
    ticket.reservedRequest = undefined
    if (!ticket.watch) {
      ticket.observation = undefined
      ticket.producer = undefined
    }
  }
  snapshot() {
    return Object.freeze({
      tickets: this.#counts.business,
      frameBytes: this.#poolBytes.business,
      watches: this.#watches.size,
      completion: this.#counts.completion,
    })
  }
}
