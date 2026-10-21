import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { randomUUID, createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { resolve, join, dirname, isAbsolute } from 'node:path'
import {
  safeError,
  safeBusiness3Error,
  safeStartupError,
  type SafeError,
  type EngineHealth,
} from '@ontolearn/contracts'
import {
  matchesResponse,
  matchesBusiness3Response,
  validateBusiness3,
  validateStartupFailure,
  validateV2,
  v2Registry,
} from '@ontolearn/contracts/v2'
import { JsonlReader, parseStrictJson } from './jsonl'
import {
  ChildOwnership,
  DispatchAccounting,
  LifecycleFault,
  ownJson,
  synchronous,
  type DispatchSource,
  type DispatchFacts,
  type DispatchOperation,
  type ExecutionEvidenceProducer,
  type SessionFacts,
  type Ticket,
  type OwnedChild,
  type TransportDrainOperation,
} from './engine-lifecycle'
export type {
  DispatchSource,
  DispatchOperation,
  ExecutionEvidenceProducer,
  TransportDrainOperation,
}

export interface EngineLocation {
  packaged: boolean
  appPath: string
  resourcesPath: string
}
export function getEngineCommand(location: EngineLocation): { command: string; args: string[] } {
  const executable = process.platform === 'win32' ? 'ontolearn-engine.exe' : 'ontolearn-engine'
  if (location.packaged)
    return { command: join(location.resourcesPath, 'engine', executable), args: [] }
  const root = resolve(location.appPath, '../..')
  const python =
    process.platform === 'win32'
      ? join(root, '.venv', 'Scripts', 'python.exe')
      : join(root, '.venv', 'bin', 'python')
  return { command: python, args: ['-I', '-m', 'ontolearn_engine'] }
}
export interface SafeEngineError {
  code: string
  messageKey: string
  params: Record<string, unknown>
  retryable: boolean
}
/** Process generations are transport identities, never durable job outcomes. */
export type EngineConnectionState =
  | { generation: number; engineSessionId: string; state: 'ready' }
  | { generation: number; engineSessionId: string; state: 'disconnected'; error: SafeEngineError }

export class EngineError extends Error {
  constructor(readonly error: SafeEngineError) {
    super(error.code)
    this.name = 'EngineError'
  }
}
function exited(): EngineError {
  return new EngineError({
    code: 'ENGINE_EXITED',
    messageKey: 'engine.exited',
    params: {},
    retryable: true,
  })
}
function invalid(): EngineError {
  return new EngineError({
    code: 'INVALID_REQUEST',
    messageKey: 'protocol.invalidRequest',
    params: { field: 'envelope' },
    retryable: false,
  })
}
function timeout(phase: string): EngineError {
  return new EngineError({
    code: 'TIMEOUT',
    messageKey: 'job.timeout',
    params: { phase },
    retryable: true,
  })
}
interface Pending {
  request: Record<string, unknown>
  resolve(value: unknown): void
  reject(error: EngineError): void
  timer: ReturnType<typeof setTimeout>
  ticket: Ticket
}
interface Hello {
  selectedVersion: 2 | 3
  engineVersion: string
  engineSessionId: string
  capabilities: string[]
  limits: Record<string, number>
  registryHash: string
}
interface Session {
  child: ChildProcessWithoutNullStreams
  generation: number
  reader: JsonlReader
  pending: Map<string, Pending>
  retained: Map<string, Ticket>
  hello?: Hello
  terminal: boolean
  anomalies: number
  stderrBytes: number
  expectedRegistryHash: string
  profile: EngineProfile
  startupPromise: Promise<Session>
  resolveStart(session: Session): void
  rejectStart(error: EngineError): void
  startupCause?: EngineError
  startupTimer?: ReturnType<typeof setTimeout>
  heartbeat?: ReturnType<typeof setTimeout>
  owner: OwnedChild
  hostClientId: string
}
interface SourceAttachment {
  source: DispatchSource
  epoch: number
  closed: boolean
  producer?: ExecutionEvidenceProducer
}
export type EngineProfile = 'legacy2' | 'business3'
interface FailureOrigin {
  session: Session
  profile: EngineProfile
  generation: number
  preHello: boolean
  startupPromise: Promise<Session>
  provenance: 'startup3' | 'bootstrap3' | 'bootstrap2' | 'business3' | 'business2' | 'local'
  value: SafeError
}
export interface SupervisorOptions {
  /** Trusted main-process option; never derived from inherited environment or renderer. */
  profile?: EngineProfile
  dataPath?: string
  allowedProjects?: string[]
  testMode?: boolean
  registryPath?: string
  startupMs?: number
  handshakeMs?: number
  requestMs?: number
  heartbeatMs?: number
  maxPending?: number
  /** Fixed local diagnostic events only; child stderr contents are never forwarded. */
  onDiagnostic?: (
    event: 'stderrDiscarded' | 'unmatchedResponse' | 'invalidFrame' | 'listenerFailed',
  ) => void
  /** Trusted test harness only. Never passed from a renderer. */
  command?: { command: string; args: string[] }
}
/** No inherited credentials, proxies, executable search paths or loader injection.
 * Engine and worker executables are absolute paths. Only OS directories/locale
 * are inherited; project authority is issued separately by the main process.
 */
export function getEngineEnvironment(
  source: NodeJS.ProcessEnv,
  options: Pick<SupervisorOptions, 'dataPath' | 'allowedProjects' | 'testMode'> = {},
  platform: NodeJS.Platform = process.platform,
): NodeJS.ProcessEnv {
  const common = ['HOME', 'TMPDIR', 'TMP', 'TEMP', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ']
  const names =
    platform === 'win32'
      ? [...common, 'SystemRoot', 'WINDIR', 'USERPROFILE', 'LOCALAPPDATA']
      : common
  const canonical = new Map(
    names.map((name) => [platform === 'win32' ? name.toUpperCase() : name, name]),
  )
  const env: NodeJS.ProcessEnv = {}
  for (const [key, value] of Object.entries(source)) {
    const accepted = canonical.get(platform === 'win32' ? key.toUpperCase() : key)
    if (accepted && typeof value === 'string') env[accepted] = value
  }
  if (options.dataPath) env.ONTOLEARN_DB_PATH = options.dataPath
  env.ONTOLEARN_ALLOWED_PROJECTS = JSON.stringify(options.allowedProjects ?? [])
  if (options.testMode === true) env.ONTOLEARN_TEST_MODE = '1'
  return env
}

function bounded(value: number | undefined, fallback: number, maximum: number): number {
  if (value === undefined) return fallback
  if (!Number.isSafeInteger(value) || value < 1 || value > maximum) throw invalid()
  return value
}

/** Owns transport only. Durable job outcomes always come from SQLite queries. */
export class EngineSupervisor {
  /** Runtime brand check: legacy transport adapters never acquire startup authority. */
  static owns(value: unknown): value is EngineSupervisor {
    return !!value && typeof value === 'object' && #origins in value
  }
  #origins = new WeakMap<object, FailureOrigin>()
  #operations = new WeakMap<Promise<unknown>, { cause: object; origin: FailureOrigin }>()
  #connections = new WeakMap<object, { session: Session; state: EngineConnectionState }>()
  #profile: EngineProfile
  get profile(): EngineProfile {
    return this.#profile
  }
  #location: EngineLocation
  #options: SupervisorOptions
  #session?: Session
  #starting?: Promise<Session>
  #generation = 0
  #stopped = false
  #starts: number[] = []
  #retryAt = 0
  #failures = 0
  #listeners = new Set<(event: unknown) => void>()
  #connectionListeners = new Set<(state: EngineConnectionState) => void>()
  readonly #startupMs: number
  readonly #handshakeMs: number
  readonly #requestMs: number
  readonly #heartbeatMs: number
  readonly #maxPending: number
  readonly #accounting: DispatchAccounting
  readonly #ownership: ChildOwnership
  #source?: SourceAttachment
  #sourceAttached = false
  #businessSeen = false
  #guarding = false
  #startingAttempt?: { owner: OwnedChild; rejectDelay?: (error: EngineError) => void }
  constructor(location: EngineLocation, options: SupervisorOptions = {}) {
    if (options.profile !== undefined && !['legacy2', 'business3'].includes(options.profile))
      throw invalid()
    this.#profile = options.profile ?? 'legacy2'
    this.#location = { ...location }
    this.#options = {
      ...options,
      allowedProjects: options.allowedProjects ? [...options.allowedProjects] : undefined,
      command: options.command
        ? { command: options.command.command, args: [...options.command.args] }
        : undefined,
    }
    this.#startupMs = bounded(options.startupMs, 10000, 60000)
    this.#handshakeMs = bounded(options.handshakeMs, 5000, 60000)
    this.#requestMs = bounded(options.requestMs, 5000, 60000)
    this.#heartbeatMs = bounded(options.heartbeatMs, 10000, 60000)
    this.#maxPending = bounded(options.maxPending, 128, 128)
    this.#accounting = new DispatchAccounting(this.#maxPending)
    this.#ownership = new ChildOwnership((owner) => this.#accounting.ownerEnded(owner))
  }
  get engineSessionId(): string | undefined {
    return this.#session?.hello?.engineSessionId
  }
  onNotification(listener: (event: unknown) => void): () => void {
    if (this.#stopped || this.#listeners.size >= 64)
      throw this.#lifecycleError(new LifecycleFault('limit'))
    this.#listeners.add(listener)
    return () => this.#listeners.delete(listener)
  }
  /** Events only: callers subscribe before starting a connection. No automatic replay. */
  onConnectionState(listener: (state: EngineConnectionState) => void): () => void {
    if (this.#stopped || this.#connectionListeners.size >= 64)
      throw this.#lifecycleError(new LifecycleFault('limit'))
    this.#connectionListeners.add(listener)
    return () => this.#connectionListeners.delete(listener)
  }
  /** Main-private consumer only; this class never constructs a real issuer. */
  attachDispatchSource(source: DispatchSource): void {
    if (
      this.#stopped ||
      this.#sourceAttached ||
      this.#guarding ||
      this.#businessSeen ||
      this.#starting ||
      this.#generation !== 0
    )
      throw exited()
    this.#sourceAttached = true
    const names = [
      'installInvalidationSink',
      'checkBeforeSpawnSync',
      'recordValidatedSession',
      'checkAndConsumeDispatchSync',
      'recordSessionTerminal',
    ] as const
    for (const key of names) if (typeof source?.[key] !== 'function') throw invalid()
    const attached: SourceAttachment = {
      source,
      epoch: 0,
      closed: false,
      producer: source.execution,
    }
    this.#source = attached
    try {
      synchronous(
        source.installInvalidationSink(this, () => {
          if (attached.epoch >= Number.MAX_SAFE_INTEGER) attached.closed = true
          else attached.epoch++
        }),
      )
    } catch {
      attached.closed = true
      throw this.#lifecycleError(new LifecycleFault('unsupported'))
    }
  }
  #lifecycleError(error: unknown): EngineError {
    if (error instanceof EngineError) return error
    if (error instanceof LifecycleFault && error.reason === 'limit')
      return new EngineError({
        code: 'QUEUE_FULL',
        messageKey: 'job.queueFull',
        params: { retryAfterMs: 100 },
        retryable: true,
      })
    if (error instanceof LifecycleFault && error.reason === 'input') return invalid()
    return new EngineError({
      code: 'INVALID_STATE',
      messageKey: 'protocol.invalidState',
      params: {},
      retryable: false,
    })
  }
  #facts(session: Session): SessionFacts {
    const hello = session.hello!
    return Object.freeze({
      actualSupervisor: this,
      actualChildOwner: session.owner.identity,
      generation: session.generation,
      hostClientId: session.hostClientId,
      engineSessionId: hello.engineSessionId,
      profile: session.profile,
      registryHash: hello.registryHash,
      engineVersion: hello.engineVersion,
      limits: Object.freeze({ ...hello.limits }),
    })
  }
  #prepare(
    method: string,
    params: Record<string, unknown>,
    originalDispatch?: object,
    pool: Ticket['pool'] = 'business',
  ): Ticket {
    if (this.#stopped || this.#guarding) throw exited()
    if (typeof method !== 'string' || method.length > 128) throw invalid()
    if (pool === 'business' && method === 'hello')
      throw this.#lifecycleError(new LifecycleFault('state'))
    const business = !['hello', 'health', 'session.ping'].includes(method)
    if (this.#sourceAttached && !this.#source)
      throw this.#lifecycleError(new LifecycleFault('unsupported'))
    if ((originalDispatch && !this.#source) || (business && this.#source && !originalDispatch))
      throw this.#lifecycleError(new LifecycleFault('unsupported'))
    if (originalDispatch && (typeof originalDispatch !== 'object' || originalDispatch === null))
      throw invalid()
    const producer = method === 'job.create' ? this.#source?.producer : undefined
    if (method === 'job.create' && this.#source && !producer)
      throw this.#lifecycleError(new LifecycleFault('unsupported'))
    const request = ownJson({ method, params }).value as Readonly<Record<string, unknown>>
    if (
      !(this.#profile === 'business3'
        ? validateBusiness3(`params_${method}`, request.params)
        : validateV2(`params_${method}`, request.params))
    )
      throw invalid()
    // Reserve the full maximum envelope overhead before any ensure/operation microtask.
    // This is a numeric reservation, never an invented Session or an encoded frame.
    const frameBytes = Buffer.byteLength(JSON.stringify(request), 'utf8') + 192
    if (frameBytes > 262144) throw this.#lifecycleError(new LifecycleFault('limit'))
    if (producer && (!producer.incarnation || typeof producer.incarnation !== 'object'))
      throw invalid()
    const ticket = this.#accounting.reserve(request, frameBytes, originalDispatch, producer, pool)
    if (business) this.#businessSeen = true
    if (producer && originalDispatch) {
      try {
        ticket.producerReserveEntered = true
        ticket.producerReservation = producer.reserveOperation({
          actualSupervisor: this,
          privateTicket: ticket.identity,
          originalDispatch,
          originalRequest: request,
          completionPort: Object.freeze({
            request: (
              identity: object,
              method: 'job.get' | 'job.subscribe' | 'job.unsubscribe',
              params: Record<string, unknown>,
              currentReadDispatch: object,
            ) => this.#completion(identity, method, params, currentReadDispatch),
          }),
        })
        if (!ticket.producerReservation || typeof ticket.producerReservation !== 'object')
          throw invalid()
      } catch (error) {
        this.#accounting.cancelUnwritten(ticket)
        throw this.#lifecycleError(error)
      }
    }
    return ticket
  }
  #completion(
    identity: object,
    method: 'job.get' | 'job.subscribe' | 'job.unsubscribe',
    params: Record<string, unknown>,
    currentReadDispatch: object,
  ): Promise<unknown> {
    const original = this.#accounting.owns(identity)
    const session = this.#session
    let ticket: Ticket
    try {
      params = ownJson(params).value as Record<string, unknown>
      if (
        !original?.producer ||
        !original.jobId ||
        !session?.hello ||
        original.owner !== session.owner.identity ||
        params.projectId !== original.projectId ||
        params.jobId !== original.jobId ||
        !['job.get', 'job.subscribe', 'job.unsubscribe'].includes(method) ||
        (method === 'job.subscribe' && original.subscriptionIds.size !== 0) ||
        (method === 'job.unsubscribe' &&
          !original.subscriptionIds.has(String(params.subscriptionId)))
      )
        throw new LifecycleFault('unsupported')
      ticket = this.#prepare(method, params, currentReadDispatch, 'completion')
      ticket.completionFor = original
    } catch (error) {
      return Promise.reject(this.#lifecycleError(error))
    }
    return this.#operation(() =>
      this.#send(
        session!,
        method,
        params,
        Math.min(this.#requestMs, session!.hello!.limits.requestMs),
        'request',
        false,
        ticket,
      ),
    )
  }
  #connectionState(session: Session, state: EngineConnectionState): void {
    for (const listener of [...this.#connectionListeners]) {
      try {
        const delivered = structuredClone(state)
        this.#connections.set(delivered, { session, state: structuredClone(state) })
        listener(delivered)
      } catch {
        this.#diagnostic('listenerFailed')
      }
    }
  }
  /** Projection authenticates the original rejection and the actual public operation promise. */
  projectFailure(cause: unknown, originatingPromise: Promise<unknown>): SafeError {
    const issued = this.#operations.get(originatingPromise)
    if (issued && issued.cause === cause && this.#origins.get(issued.cause) === issued.origin) {
      const origin = issued.origin
      return origin.provenance === 'startup3'
        ? safeStartupError(origin.value)
        : origin.provenance === 'bootstrap2'
          ? safeError(origin.value)
          : origin.provenance === 'bootstrap3' || origin.profile === 'business3'
            ? safeBusiness3Error(origin.value)
            : safeError(origin.value)
    }
    // Legacy adapters have no startup authority; neither classes nor shapes confer it.
    try {
      return safeError((cause as { error?: unknown } | null)?.error)
    } catch {
      return safeError(null)
    }
  }
  projectConnectionFailure(
    event: unknown,
  ): Extract<EngineConnectionState, { state: 'disconnected' }> | undefined {
    if (!event || typeof event !== 'object') return undefined
    const issued = this.#connections.get(event)
    if (!issued || issued.state.state !== 'disconnected') return undefined
    return structuredClone(issued.state)
  }
  #sign(
    session: Session,
    error: EngineError,
    provenance: FailureOrigin['provenance'] = 'local',
  ): EngineError {
    const previous = this.#origins.get(error)
    if (previous) return error
    const value =
      provenance === 'startup3'
        ? safeStartupError(error.error)
        : provenance === 'bootstrap2'
          ? safeError(error.error)
          : provenance === 'bootstrap3' || session.profile === 'business3'
            ? safeBusiness3Error(error.error)
            : safeError(error.error)
    this.#origins.set(
      error,
      Object.freeze({
        session,
        profile: session.profile,
        generation: session.generation,
        preHello: !session.hello,
        startupPromise: session.startupPromise,
        provenance,
        value: structuredClone(value),
      }),
    )
    return error
  }
  #operation<T>(work: () => Promise<T>): Promise<T> {
    const promise = Promise.resolve()
      .then(work)
      .catch((cause: unknown) => {
        if (cause && typeof cause === 'object') {
          const origin = this.#origins.get(cause)
          if (origin) this.#operations.set(promise, { cause, origin })
        }
        throw cause
      })
    return promise
  }
  #validate(session: Session, name: string, value: unknown): boolean {
    return session.profile === 'business3'
      ? validateBusiness3(name, value)
      : validateV2(name, value)
  }
  #diagnostic(event: Parameters<NonNullable<SupervisorOptions['onDiagnostic']>>[0]): void {
    try {
      this.#options.onDiagnostic?.(event)
    } catch {
      /* Diagnostics cannot change transport outcomes. */
    }
  }
  #current(session: Session): boolean {
    return !session.terminal && this.#session === session && session.generation === this.#generation
  }
  #finish(session: Session, error: EngineError): void {
    if (session.terminal) return
    error = session.startupCause ?? this.#sign(session, error)
    if (!session.hello) session.startupCause = error
    session.terminal = true
    session.reader.stop()
    session.rejectStart(error)
    clearTimeout(session.startupTimer)
    clearTimeout(session.heartbeat)
    for (const pending of session.pending.values()) {
      clearTimeout(pending.timer)
      pending.reject(error)
    }
    session.pending.clear()
    session.retained.clear()
    try {
      if (session.hello && this.#source)
        synchronous(this.#source.source.recordSessionTerminal(this.#facts(session)))
    } catch {
      if (this.#source) this.#source.closed = true
    }
    if (this.#session === session) {
      this.#session = undefined
      this.#failures++
      this.#retryAt = Date.now() + Math.min(2000, 100 * 2 ** Math.min(this.#failures - 1, 5))
    }
    session.owner.retire()
    if (!this.#stopped && session.hello) {
      this.#connectionState(session, {
        state: 'disconnected',
        generation: session.generation,
        engineSessionId: session.hello.engineSessionId,
        error:
          session.profile === 'business3'
            ? safeBusiness3Error(error.error)
            : safeError(error.error),
      })
    }
  }
  stop(): void {
    if (this.#stopped) return
    this.#stopped = true
    this.#generation++
    if (this.#source) this.#source.closed = true
    this.#startingAttempt?.rejectDelay?.(exited())
    this.#accounting.stopUnwritten()
    if (this.#session) this.#finish(this.#session, exited())
    for (const owner of this.#ownership.entries()) owner.retire()
    this.#listeners.clear()
    this.#connectionListeners.clear()
    this.#ownership.stopped()
  }
  stopAndDrain(): TransportDrainOperation {
    this.stop()
    return this.#ownership.operation
  }
  async #ensure(): Promise<Session> {
    if (this.#stopped) throw exited()
    if (this.#session?.hello && this.#current(this.#session)) return this.#session
    if (this.#starting) return this.#starting
    this.#starting = this.#start().finally(() => {
      this.#starting = undefined
    })
    return this.#starting
  }
  async #start(): Promise<Session> {
    let owner: OwnedChild
    try {
      owner = this.#ownership.reserve()
    } catch (error) {
      throw this.#lifecycleError(error)
    }
    const attempt: { owner: OwnedChild; rejectDelay?: (error: EngineError) => void } = { owner }
    this.#startingAttempt = attempt
    try {
      const delay = this.#retryAt - Date.now()
      if (delay > 0)
        await new Promise<void>((resolveDelay, rejectDelay) => {
          const timer = setTimeout(() => {
            attempt.rejectDelay = undefined
            resolveDelay()
          }, delay)
          attempt.rejectDelay = (error) => {
            clearTimeout(timer)
            attempt.rejectDelay = undefined
            rejectDelay(error)
          }
        })
      if (this.#stopped) throw exited()
      const now = Date.now()
      this.#starts = this.#starts.filter((time) => now - time < 60000)
      if (this.#starts.length >= 5) throw exited()
      this.#starts.push(now)
      let registryHash: string
      try {
        const path =
          this.#options.registryPath ??
          (this.#location.packaged
            ? join(this.#location.resourcesPath, 'contracts', 'v2', 'registry.json')
            : resolve(this.#location.appPath, '../../packages/contracts/v2/registry.json'))
        const bytes = readFileSync(path)
        if (
          bytes.length > 262144 ||
          JSON.stringify(
            parseStrictJson(
              new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes),
            ),
          ) !== JSON.stringify(v2Registry)
        )
          throw invalid()
        registryHash = createHash('sha256').update(bytes).digest('hex')
      } catch {
        throw exited()
      }
      const selected = this.#options.command ?? getEngineCommand(this.#location)
      const command = selected.command
      const args = [...selected.args]
      if (this.profile === 'business3') {
        const database = this.#options.dataPath
        if (database && !isAbsolute(database)) throw invalid()
        args.push('--t01-internal-profile=business3')
        if (database)
          args.push(
            `--t01-internal-backup=${join(dirname(database), `.t01-backup-${randomUUID()}.sqlite`)}`,
          )
      }
      const env = getEngineEnvironment(process.env, this.#options)
      const source = this.#source
      const epoch = source?.epoch
      const generation = this.#generation
      if (source) {
        if (source.closed) throw this.#lifecycleError(new LifecycleFault('unsupported'))
        this.#guarding = true
        try {
          synchronous(
            source.source.checkBeforeSpawnSync({
              actualSupervisor: this,
              generation: generation + 1,
            }),
          )
        } finally {
          this.#guarding = false
        }
        if (
          this.#stopped ||
          this.#source !== source ||
          source.closed ||
          source.epoch !== epoch ||
          this.#generation !== generation
        )
          throw exited()
      }
      let child: ChildProcessWithoutNullStreams
      try {
        owner.spawnEntered = true
        child = spawn(command, args, {
          shell: false,
          windowsHide: true,
          stdio: ['pipe', 'pipe', 'pipe'],
          env,
        })
        owner.bind(child)
      } catch {
        throw exited()
      }
      let resolveStart!: (session: Session) => void
      let rejectStart!: (error: EngineError) => void
      const startupPromise = new Promise<Session>((resolve, reject) => {
        resolveStart = resolve
        rejectStart = reject
      })
      const session: Session = {
        child,
        owner,
        hostClientId: randomUUID(),
        profile: this.profile,
        startupPromise,
        resolveStart,
        rejectStart,
        generation: ++this.#generation,
        pending: new Map(),
        retained: new Map(),
        terminal: false,
        anomalies: 0,
        stderrBytes: 0,
        expectedRegistryHash: registryHash,
        reader: new JsonlReader(
          (value, metadata) => this.#receive(session, value, metadata.payloadByteLength),
          (reason) => {
            this.#diagnostic('invalidFrame')
            this.#finish(
              session,
              reason === 'frame'
                ? new EngineError({
                    code: 'RESOURCE_LIMIT',
                    messageKey: 'resource.limitExceeded',
                    params: { resource: 'frame' },
                    retryable: false,
                  })
                : invalid(),
            )
          },
        ),
      }
      this.#session = session
      if (child.stdout)
        owner.listen(child.stdout, 'data', (chunk: Buffer) => {
          if (this.#current(session)) session.reader.push(chunk)
        })
      if (child.stdout)
        owner.listen(
          child.stdout,
          'end',
          () => {
            session.reader.end()
            this.#finish(session, exited())
          },
          true,
        )
      if (child.stderr)
        owner.listen(child.stderr, 'data', (chunk: Buffer) => {
          if (!this.#current(session) || session.stderrBytes >= 16384) return
          // Store neither raw bytes nor lines. A single bounded fixed event is sufficient.
          if (session.stderrBytes === 0) this.#diagnostic('stderrDiscarded')
          session.stderrBytes = Math.min(16384, session.stderrBytes + chunk.byteLength)
        })
      if (child.stdin) owner.listen(child.stdin, 'error', () => this.#finish(session, exited()))
      const fail = (error: EngineError): void => this.#finish(session, error)
      session.startupTimer = setTimeout(() => fail(timeout('startup')), this.#startupMs)
      owner.listen(child, 'error', () => fail(exited()), true)
      owner.listen(child, 'close', () => fail(exited()), true)
      owner.listen(
        child,
        'spawn',
        () => {
          if (!this.#current(session)) {
            fail(exited())
            return
          }
          void this.#send(
            session,
            'hello',
            {
              supportedVersions: [session.profile === 'business3' ? 3 : 2],
              clientId: session.hostClientId,
            },
            this.#handshakeMs,
            'handshake',
          ).then((value) => {
            const hello = value as Hello
            if (!this.#current(session) || hello.registryHash !== registryHash) {
              fail(invalid())
              return
            }
            clearTimeout(session.startupTimer)
            this.#failures = 0
            this.#scheduleHeartbeat(session)
            session.resolveStart(session)
          }, fail)
        },
        true,
      )
      if (this.#stopped) fail(exited())
      return await startupPromise
    } catch (error) {
      if (!owner.spawnEntered) owner.cancelNeverCreated()
      else owner.retire()
      throw error
    } finally {
      owner.finishStarting()
      if (this.#startingAttempt === attempt) this.#startingAttempt = undefined
    }
  }

  #scheduleHeartbeat(session: Session): void {
    if (!this.#current(session)) return
    const interval = Math.min(this.#heartbeatMs, session.hello!.limits.heartbeatMs)
    session.heartbeat = setTimeout(() => {
      if (!this.#current(session)) return
      void this.#send(
        session,
        'session.ping',
        { nonce: randomUUID() },
        interval,
        'heartbeat',
        true,
      ).then(
        () => this.#scheduleHeartbeat(session),
        () => this.#finish(session, timeout('heartbeat')),
      )
    }, interval)
    session.heartbeat.unref()
  }
  #closeObservation(ticket: Ticket): void {
    if (!ticket.watch) return
    const producer = ticket.producer
    const observation = ticket.observation
    const subscription = ticket.subscription
    if (!producer || !observation || !subscription) return
    try {
      const cleanup = subscription.closeObservation()
      void Promise.resolve(cleanup).then(
        (issued) => {
          if (!ticket.watch || ticket.producer !== producer || ticket.observation !== observation)
            return
          try {
            if (!issued || typeof issued !== 'object') return
            synchronous(producer.projectObservationCleanup(issued, observation))
            this.#accounting.releaseWatch(ticket)
          } catch {
            /* Unknown real cleanup retains its bounded watch. */
          }
        },
        () => undefined,
      )
    } catch {
      /* close is an attempt, never release evidence by itself. */
    }
  }
  #bindObservation(ticket: Ticket, facts: DispatchFacts): void {
    const producer = ticket.producer
    if (!producer) return
    if (!ticket.producerReservation || producer.incarnation !== ticket.producerIncarnation)
      throw new LifecycleFault('identity')
    const observation = producer.bindOperation(ticket.producerReservation, facts)
    if (!observation || typeof observation !== 'object') throw new LifecycleFault('identity')
    ticket.observation = observation
    ticket.subscription = producer.observe(observation, (issued) => {
      if (
        !ticket.attempted ||
        ticket.executionEnded ||
        producer.incarnation !== ticket.producerIncarnation ||
        ticket.producer !== producer ||
        ticket.observation !== observation
      )
        return
      try {
        const fact = ownJson(producer.projectTerminal(issued, ticket.identity), 4096)
          .value as import('./engine-lifecycle').TerminalJobFact
        if (Object.keys(fact).length !== 4) throw new LifecycleFault('identity')
        this.#accounting.terminal(ticket, fact)
        this.#closeObservation(ticket)
      } catch {
        /* Forged, premature or stale observations have no releasing authority. */
      }
    })
    if (!ticket.subscription || typeof ticket.subscription.closeObservation !== 'function')
      throw new LifecycleFault('identity')
  }
  #foreground(session: Session, ticket: Ticket, response: Record<string, unknown>): void {
    const producer = ticket.producer
    if (ticket.background && response.ok) {
      const result = response.result as Record<string, unknown>
      // The complete strictly matched acceptance is passed to the actual producer.
      ticket.jobId = String(result.jobId)
      if (producer && ticket.observation) {
        try {
          synchronous(producer.bindAcceptedJob(ticket.observation, response))
        } catch {
          /* A failed producer binding leaves the execution unknown. */
        }
      }
    }
    const original = ticket.completionFor
    if (original && response.ok && ticket.method === 'job.subscribe') {
      const id = (response.result as Record<string, unknown>).subscriptionId
      if (typeof id === 'string' && original.subscriptionIds.size < 1)
        original.subscriptionIds.add(id)
    }
    if (original && response.ok && ticket.method === 'job.unsubscribe') {
      const id = (ticket.request?.params as Record<string, unknown> | undefined)?.subscriptionId
      if (typeof id === 'string') original.subscriptionIds.delete(id)
    }
    this.#accounting.foreground(ticket)
    session.retained.delete(String(response.id))
  }
  #receive(session: Session, value: unknown, payloadByteLength: number): void {
    if (!this.#current(session)) return
    if (
      value &&
      typeof value === 'object' &&
      (value as Record<string, unknown>).kind === 'startupFailure'
    ) {
      if (
        session.profile === 'business3' &&
        !session.hello &&
        !session.startupCause &&
        validateStartupFailure(value, payloadByteLength, session.expectedRegistryHash)
      ) {
        const error = this.#sign(
          session,
          new EngineError((value as { error: SafeError }).error),
          'startup3',
        )
        session.startupCause = error
        this.#finish(session, error)
      } else this.#finish(session, invalid())
      return
    }
    if (this.#validate(session, 'notification', value)) {
      const event = value as Record<string, unknown>
      if (!session.hello || event.engineSessionId !== session.hello.engineSessionId) {
        if (session.profile === 'business3') this.#finish(session, invalid())
        return
      }
      for (const listener of this.#listeners) {
        try {
          listener(value)
        } catch {
          this.#diagnostic('listenerFailed')
        }
      }
      return
    }
    const response = value as Record<string, unknown>
    const pending = response && session.pending.get(String(response.id))
    const retained = response && session.retained.get(String(response.id))
    const originalRequest = pending?.request ?? retained?.request
    // A strict incompatible bootstrap is a terminating diagnostic, never a v3 session.
    const incompatible3 =
      session.profile === 'legacy2' &&
      !session.hello &&
      pending?.request.method === 'hello' &&
      response.ok === false &&
      (response.error as SafeError | undefined)?.code === 'VERSION_INCOMPATIBLE' &&
      matchesBusiness3Response(pending.request, value, session.expectedRegistryHash)
    if (!incompatible3 && !this.#validate(session, 'response', value)) {
      this.#finish(session, invalid())
      return
    }
    if (
      !originalRequest ||
      !(
        incompatible3 ||
        (session.profile === 'business3'
          ? matchesBusiness3Response(originalRequest, value, session.expectedRegistryHash)
          : matchesResponse(originalRequest, value))
      )
    ) {
      this.#diagnostic('unmatchedResponse')
      if (session.profile === 'business3' || ++session.anomalies >= 3)
        this.#finish(session, invalid())
      return
    }
    if (!pending && retained) {
      this.#diagnostic('unmatchedResponse')
      this.#foreground(session, retained, response)
      return
    }
    if (!pending) return
    // Apply the negotiated byte budget synchronously, including a following frame
    // in this same stdout chunk. Never wait for a promise microtask to enforce it.
    if (response.ok && pending.request.method === 'hello') {
      const hello = response.result as Hello
      if (hello.registryHash !== session.expectedRegistryHash) {
        this.#finish(session, invalid())
        return
      }
      session.reader.restrictLimit(hello.limits.maxFrameBytes)
      session.hello = hello
      try {
        if (this.#source) {
          if (this.#source.closed) throw exited()
          synchronous(this.#source.source.recordValidatedSession(this.#facts(session)))
        }
        if (!this.#current(session)) return
      } catch {
        this.#finish(session, invalid())
        return
      }
      this.#connectionState(session, {
        state: 'ready',
        generation: session.generation,
        engineSessionId: hello.engineSessionId,
      })
    }
    clearTimeout(pending.timer)
    session.pending.delete(String(response.id))
    this.#foreground(session, pending.ticket, response)
    if (response.ok) pending.resolve(response.result)
    else {
      const error = this.#sign(
        session,
        new EngineError(response.error as SafeEngineError),
        incompatible3
          ? 'bootstrap3'
          : pending.request.method === 'hello' &&
              (response.error as SafeError).code === 'VERSION_INCOMPATIBLE' &&
              (response.error as SafeError).params.supportedVersions instanceof Array &&
              ((response.error as SafeError).params.supportedVersions as number[])[0] === 2
            ? 'bootstrap2'
            : session.profile === 'business3'
              ? 'business3'
              : 'business2',
      )
      pending.reject(error)
      if (pending.request.method === 'hello') this.#finish(session, error)
    }
  }
  #send(
    session: Session,
    method: string,
    params: Record<string, unknown>,
    duration: number,
    phase: string,
    reservedControl = false,
    reserved?: Ticket,
  ): Promise<unknown> {
    let ticket: Ticket
    try {
      ticket =
        reserved ??
        this.#prepare(
          method,
          params,
          undefined,
          method === 'hello' ? 'hello' : reservedControl ? 'ping' : 'business',
        )
    } catch (error) {
      return Promise.reject(this.#lifecycleError(error))
    }
    if (!this.#current(session)) {
      this.#accounting.cancelUnwritten(ticket)
      return Promise.reject(exited())
    }
    try {
      if (!ticket.request || ticket.attempted) throw new LifecycleFault('state')
      const request = Object.freeze({
        kind: 'request',
        id: randomUUID(),
        protocolVersion: method === 'hello' ? 2 : session.profile === 'business3' ? 3 : 2,
        engineSessionId: method === 'hello' ? null : session.hello?.engineSessionId,
        method,
        params: ticket.request.params,
      }) as Record<string, unknown>
      if (!this.#validate(session, 'request', request)) throw invalid()
      const encoded = Buffer.from(JSON.stringify(request) + '\n', 'utf8')
      if (
        encoded.byteLength > ticket.bytes ||
        encoded.byteLength - 1 > (session.hello?.limits.maxFrameBytes ?? 262144)
      )
        throw new LifecycleFault('limit')
      ticket.request = request
      ticket.frame = encoded
      ticket.owner = session.owner.identity
      const source = this.#source
      const originalDispatch = ticket.originalDispatch
      const facts =
        source && originalDispatch
          ? Object.freeze({
              ...this.#facts(session),
              privateTicket: ticket.identity,
              originalRequest: ticket.reservedRequest!,
              actualRequest: request,
              requestHash: createHash('sha256').update(encoded).digest('hex'),
              frameBytes: encoded.byteLength,
              sourceEpoch: source.epoch,
            })
          : undefined
      if (facts) this.#bindObservation(ticket, facts)
      // Resolve every method/getter, bind all observers and encode before the critical section.
      const write = session.child.stdin.write.bind(session.child.stdin)
      const check = source?.source.checkAndConsumeDispatchSync.bind(source.source)
      return new Promise((resolveRequest, rejectRequest) => {
        const timer = setTimeout(() => {
          session.pending.delete(String(request.id))
          if (ticket.request && ticket.attempted) session.retained.set(String(request.id), ticket)
          rejectRequest(this.#sign(session, timeout(phase)))
        }, duration)
        session.pending.set(String(request.id), {
          request,
          resolve: resolveRequest,
          reject: rejectRequest,
          timer,
          ticket,
        })
        try {
          const epoch = source?.epoch
          if (source && originalDispatch && facts && check) {
            if (source.closed || facts.sourceEpoch !== epoch) throw exited()
            this.#guarding = true
            try {
              synchronous(check(originalDispatch, facts))
            } finally {
              this.#guarding = false
            }
          }
          // No external calls or property reads with user-defined getters between consume and write.
          if (
            !this.#current(session) ||
            this.#stopped ||
            this.#source !== source ||
            (source && (source.closed || source.epoch !== epoch))
          )
            throw exited()
          ticket.attempted = true
          write(encoded, (error) => {
            if (error) this.#finish(session, exited())
          })
        } catch (error) {
          clearTimeout(timer)
          session.pending.delete(String(request.id))
          if (!ticket.attempted) {
            this.#accounting.cancelUnwritten(ticket)
            this.#closeObservation(ticket)
          } else this.#finish(session, exited())
          rejectRequest(this.#sign(session, this.#lifecycleError(error)))
        }
      })
    } catch (error) {
      this.#accounting.cancelUnwritten(ticket)
      this.#closeObservation(ticket)
      return Promise.reject(this.#sign(session, this.#lifecycleError(error)))
    }
  }
  #request(ticket: Ticket): Promise<unknown> {
    return this.#operation(async () => {
      try {
        const session = await this.#ensure()
        return await this.#send(
          session,
          ticket.method,
          {},
          Math.min(this.#requestMs, session.hello!.limits.requestMs),
          'request',
          false,
          ticket,
        )
      } catch (error) {
        this.#accounting.cancelUnwritten(ticket)
        throw error
      }
    })
  }
  request(method: string, params: Record<string, unknown>): Promise<unknown> {
    try {
      if (method === 'job.create' && !this.#source) {
        const owned = ownJson(params).value as Record<string, unknown>
        const existing =
          typeof owned.operationId === 'string'
            ? this.#accounting.find(owned.operationId)
            : undefined
        if (existing?.jobId && JSON.stringify(existing.request?.params) === JSON.stringify(owned))
          return this.#request(
            this.#prepare('job.get', { projectId: existing.projectId, jobId: existing.jobId }),
          )
      }
      return this.#request(this.#prepare(method, params))
    } catch (error) {
      return Promise.reject(this.#lifecycleError(error))
    }
  }
  requestWithDispatch(
    originalDispatch: object,
    method: string,
    params: Record<string, unknown>,
  ): DispatchOperation {
    let ticket: Ticket
    try {
      ticket = this.#prepare(method, params, originalDispatch)
    } catch (error) {
      return Object.freeze({
        logicalOutcome: Promise.reject(this.#lifecycleError(error)),
        dispatchObservation: 'not-written' as const,
        operationExecution: new Promise<import('./engine-lifecycle').ExecutionFact>(
          () => undefined,
        ),
      })
    }
    const logicalOutcome = this.#request(ticket)
    return Object.freeze({
      logicalOutcome,
      get dispatchObservation() {
        return ticket.attempted ? ('write-attempted' as const) : ('not-written' as const)
      },
      operationExecution: ticket.execution.promise,
    })
  }

  health(): Promise<EngineHealth> {
    let ticket: Ticket
    try {
      ticket = this.#prepare('health', {})
    } catch (error) {
      return Promise.reject(this.#lifecycleError(error))
    }
    return this.#operation(async () => {
      let session: Session
      try {
        session = await this.#ensure()
      } catch (error) {
        this.#accounting.cancelUnwritten(ticket)
        throw error
      }
      const value = (await this.#send(
        session,
        'health',
        {},
        Math.min(this.#requestMs, session.hello!.limits.requestMs),
        'request',
        false,
        ticket,
      )) as { engineVersion: string; status: 'ok' }
      if (!this.#current(session)) throw this.#sign(session, exited())
      const hello = session.hello!
      if (value.engineVersion !== hello.engineVersion) throw this.#sign(session, invalid())
      return {
        protocolVersion: hello.selectedVersion,
        ...value,
        capabilities: hello.capabilities.filter((capability) => capability === 'health'),
      } as EngineHealth
    })
  }
}

/** Compatibility for callers that explicitly want a one-shot probe. Desktop uses one instance. */
export async function readEngineHealth(location: EngineLocation): Promise<EngineHealth> {
  const supervisor = new EngineSupervisor(location)
  try {
    return await supervisor.health()
  } finally {
    supervisor.stop()
  }
}
