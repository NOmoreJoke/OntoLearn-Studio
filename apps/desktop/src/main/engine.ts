import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { randomUUID, createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { resolve, join } from 'node:path'
import { type EngineHealth } from '@ontolearn/contracts'
import { matchesResponse, validateV2, v2Registry, isModelMethod } from '@ontolearn/contracts/v2'
import { JsonlReader, parseStrictJson } from './jsonl'

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
}
interface Hello {
  selectedVersion: 2
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
  hello?: Hello
  terminal: boolean
  anomalies: number
  stderrBytes: number
  expectedRegistryHash: string
  startupTimer?: ReturnType<typeof setTimeout>
  heartbeat?: ReturnType<typeof setTimeout>
}
export interface SupervisorOptions {
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
  private session?: Session
  private starting?: Promise<Session>
  private generation = 0
  private stopped = false
  private starts: number[] = []
  private retryAt = 0
  private failures = 0
  private listeners = new Set<(event: unknown) => void>()
  private connectionListeners = new Set<(state: EngineConnectionState) => void>()
  private readonly startupMs: number
  private readonly handshakeMs: number
  private readonly requestMs: number
  private readonly heartbeatMs: number
  private readonly maxPending: number
  constructor(
    private readonly location: EngineLocation,
    private readonly options: SupervisorOptions = {},
  ) {
    this.startupMs = bounded(options.startupMs, 10000, 60000)
    this.handshakeMs = bounded(options.handshakeMs, 5000, 60000)
    this.requestMs = bounded(options.requestMs, 5000, 60000)
    this.heartbeatMs = bounded(options.heartbeatMs, 10000, 60000)
    this.maxPending = bounded(options.maxPending, 128, 128)
  }
  get engineSessionId(): string | undefined {
    return this.session?.hello?.engineSessionId
  }
  onNotification(listener: (event: unknown) => void): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
  /** Events only: callers subscribe before starting a connection. No automatic replay. */
  onConnectionState(listener: (state: EngineConnectionState) => void): () => void {
    this.connectionListeners.add(listener)
    return () => this.connectionListeners.delete(listener)
  }
  private connectionState(state: EngineConnectionState): void {
    for (const listener of [...this.connectionListeners]) {
      try {
        listener(structuredClone(state))
      } catch {
        this.diagnostic('listenerFailed')
      }
    }
  }
  private diagnostic(event: Parameters<NonNullable<SupervisorOptions['onDiagnostic']>>[0]): void {
    try {
      this.options.onDiagnostic?.(event)
    } catch {
      /* Diagnostics cannot change transport outcomes. */
    }
  }
  private current(session: Session): boolean {
    return !session.terminal && this.session === session && session.generation === this.generation
  }
  private finish(session: Session, error: EngineError): void {
    if (session.terminal) return
    session.terminal = true
    session.reader.stop()
    clearTimeout(session.startupTimer)
    clearTimeout(session.heartbeat)
    for (const pending of session.pending.values()) {
      clearTimeout(pending.timer)
      pending.reject(error)
    }
    session.pending.clear()
    if (this.session === session) {
      this.session = undefined
      this.failures++
      this.retryAt = Date.now() + Math.min(2000, 100 * 2 ** Math.min(this.failures - 1, 5))
    }
    session.child.kill()
    const killTimer = setTimeout(() => {
      if (session.child.exitCode === null && session.child.signalCode === null)
        session.child.kill('SIGKILL')
    }, 1000)
    killTimer.unref()
    session.child.once('close', () => clearTimeout(killTimer))
    if (!this.stopped && session.hello) {
      this.connectionState({
        state: 'disconnected',
        generation: session.generation,
        engineSessionId: session.hello.engineSessionId,
        error: validateV2('error', error.error)
          ? error.error
          : {
              code: 'INTERNAL_ERROR',
              messageKey: 'engine.internal',
              params: {},
              retryable: false,
            },
      })
    }
  }
  stop(): void {
    this.stopped = true
    this.generation++
    if (this.session) this.finish(this.session, exited())
    this.listeners.clear()
    this.connectionListeners.clear()
  }
  private async ensure(): Promise<Session> {
    if (this.stopped) throw exited()
    if (this.session?.hello && this.current(this.session)) return this.session
    if (this.starting) return this.starting
    this.starting = this.start().finally(() => {
      this.starting = undefined
    })
    return this.starting
  }
  private async start(): Promise<Session> {
    const delay = this.retryAt - Date.now()
    if (delay > 0) await new Promise<void>((resolveDelay) => setTimeout(resolveDelay, delay))
    if (this.stopped) throw exited()
    const now = Date.now()
    this.starts = this.starts.filter((time) => now - time < 60000)
    if (this.starts.length >= 5) throw exited()
    this.starts.push(now)
    let registryHash: string
    try {
      const path =
        this.options.registryPath ??
        (this.location.packaged
          ? join(this.location.resourcesPath, 'contracts', 'v2', 'registry.json')
          : resolve(this.location.appPath, '../../packages/contracts/v2/registry.json'))
      const bytes = readFileSync(path)
      if (
        bytes.length > 262144 ||
        JSON.stringify(
          parseStrictJson(new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes)),
        ) !== JSON.stringify(v2Registry)
      )
        throw invalid()
      registryHash = createHash('sha256').update(bytes).digest('hex')
    } catch {
      throw exited()
    }
    const { command, args } = this.options.command ?? getEngineCommand(this.location)
    const env = getEngineEnvironment(process.env, this.options)
    let child: ChildProcessWithoutNullStreams
    try {
      child = spawn(command, args, {
        shell: false,
        windowsHide: true,
        stdio: ['pipe', 'pipe', 'pipe'],
        env,
      })
    } catch {
      throw exited()
    }
    const session: Session = {
      child,
      generation: ++this.generation,
      pending: new Map(),
      terminal: false,
      anomalies: 0,
      stderrBytes: 0,
      expectedRegistryHash: registryHash,
      reader: new JsonlReader(
        (value) => this.receive(session, value),
        (reason) => {
          this.diagnostic('invalidFrame')
          this.finish(
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
    this.session = session
    child.stdout.on('data', (chunk: Buffer) => {
      if (this.current(session)) session.reader.push(chunk)
    })
    child.stdout.once('end', () => {
      session.reader.end()
      this.finish(session, exited())
    })
    child.stderr.on('data', (chunk: Buffer) => {
      if (!this.current(session) || session.stderrBytes >= 16384) return
      // Store neither raw bytes nor lines. A single bounded fixed event is sufficient.
      if (session.stderrBytes === 0) this.diagnostic('stderrDiscarded')
      session.stderrBytes = Math.min(16384, session.stderrBytes + chunk.byteLength)
    })
    child.stdin.on('error', () => this.finish(session, exited()))
    return new Promise<Session>((resolveStart, rejectStart) => {
      const fail = (error: EngineError): void => {
        this.finish(session, error)
        rejectStart(error)
      }
      session.startupTimer = setTimeout(() => fail(timeout('startup')), this.startupMs)
      child.once('error', () => fail(exited()))
      child.once('close', () => fail(exited()))
      child.once('spawn', () => {
        if (!this.current(session)) {
          fail(exited())
          return
        }
        void this.send(
          session,
          'hello',
          { supportedVersions: [2], clientId: randomUUID() },
          this.handshakeMs,
          'handshake',
        ).then((value) => {
          const hello = value as Hello
          if (!this.current(session) || hello.registryHash !== registryHash) {
            fail(invalid())
            return
          }
          clearTimeout(session.startupTimer)
          this.failures = 0
          this.scheduleHeartbeat(session)
          resolveStart(session)
        }, fail)
      })
    })
  }
  private scheduleHeartbeat(session: Session): void {
    if (!this.current(session)) return
    const interval = Math.min(this.heartbeatMs, session.hello!.limits.heartbeatMs)
    session.heartbeat = setTimeout(() => {
      if (!this.current(session)) return
      void this.send(
        session,
        'session.ping',
        { nonce: randomUUID() },
        interval,
        'heartbeat',
        true,
      ).then(
        () => this.scheduleHeartbeat(session),
        () => this.finish(session, timeout('heartbeat')),
      )
    }, interval)
    session.heartbeat.unref()
  }
  private receive(session: Session, value: unknown): void {
    if (!this.current(session)) return
    if (validateV2('notification', value)) {
      const event = value as Record<string, unknown>
      if (!session.hello || event.engineSessionId !== session.hello.engineSessionId) return
      for (const listener of this.listeners) {
        try {
          listener(value)
        } catch {
          this.diagnostic('listenerFailed')
        }
      }
      return
    }
    if (!validateV2('response', value)) {
      this.finish(session, invalid())
      return
    }
    const response = value as Record<string, unknown>
    const pending = session.pending.get(String(response.id))
    if (!pending || !matchesResponse(pending.request, value)) {
      this.diagnostic('unmatchedResponse')
      if (++session.anomalies >= 3) this.finish(session, invalid())
      return
    }
    // Apply the negotiated byte budget synchronously, including a following frame
    // in this same stdout chunk. Never wait for a promise microtask to enforce it.
    if (response.ok && pending.request.method === 'hello') {
      const hello = response.result as Hello
      if (hello.registryHash !== session.expectedRegistryHash) {
        this.finish(session, invalid())
        return
      }
      session.reader.restrictLimit(hello.limits.maxFrameBytes)
      session.hello = hello
      this.connectionState({
        state: 'ready',
        generation: session.generation,
        engineSessionId: hello.engineSessionId,
      })
    }
    clearTimeout(pending.timer)
    session.pending.delete(String(response.id))
    if (response.ok) pending.resolve(response.result)
    else pending.reject(new EngineError(response.error as SafeEngineError))
  }
  private send(
    session: Session,
    method: string,
    params: Record<string, unknown>,
    duration: number,
    phase: string,
    reservedControl = false,
  ): Promise<unknown> {
    if (!this.current(session)) return Promise.reject(exited())
    if (session.pending.size >= this.maxPending + (reservedControl ? 1 : 0))
      return Promise.reject(
        new EngineError({
          code: 'QUEUE_FULL',
          messageKey: 'job.queueFull',
          params: { retryAfterMs: 100 },
          retryable: true,
        }),
      )
    const request = {
      kind: 'request',
      id: randomUUID(),
      protocolVersion: 2,
      engineSessionId: method === 'hello' ? null : session.hello?.engineSessionId,
      method,
      params,
    }
    if (!validateV2('request', request)) return Promise.reject(invalid())
    const encoded = Buffer.from(JSON.stringify(request) + '\n', 'utf8')
    if (encoded.length - 1 > (session.hello?.limits.maxFrameBytes ?? 262144))
      return Promise.reject(
        new EngineError({
          code: 'RESOURCE_LIMIT',
          messageKey: 'resource.limitExceeded',
          params: { resource: 'frame' },
          retryable: false,
        }),
      )
    return new Promise((resolveRequest, rejectRequest) => {
      const timer = setTimeout(() => {
        session.pending.delete(request.id)
        rejectRequest(timeout(phase))
      }, duration)
      session.pending.set(request.id, {
        request: parseStrictJson(encoded.subarray(0, -1).toString('utf8')) as Record<
          string,
          unknown
        >,
        resolve: resolveRequest,
        reject: rejectRequest,
        timer,
      })
      session.child.stdin.write(encoded, (error) => {
        if (error) this.finish(session, exited())
      })
    })
  }
  async request(method: string, params: Record<string, unknown>): Promise<unknown> {
    if (method === 'hello' || isModelMethod(method))
      throw new EngineError({
        code: 'INVALID_STATE',
        messageKey: 'protocol.invalidState',
        params: {},
        retryable: false,
      })
    const session = await this.ensure()
    return this.send(
      session,
      method,
      params,
      Math.min(this.requestMs, session.hello!.limits.requestMs),
      'request',
    )
  }
  async health(): Promise<EngineHealth> {
    const session = await this.ensure()
    const value = (await this.send(
      session,
      'health',
      {},
      Math.min(this.requestMs, session.hello!.limits.requestMs),
      'request',
    )) as { engineVersion: string; status: 'ok' }
    if (!this.current(session)) throw exited()
    const hello = session.hello!
    if (value.engineVersion !== hello.engineVersion) throw invalid()
    // A short health response does not declare any unimplemented business capability.
    return {
      protocolVersion: 2,
      ...value,
      capabilities: hello.capabilities.filter((capability) => capability === 'health'),
    } as unknown as EngineHealth
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
