import { AsyncLocalStorage } from 'node:async_hooks'
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
  type ProjectView,
  type BridgeResult,
  type TaskView,
} from '@ontolearn/contracts'
import {
  matchesResponse,
  matchesOrdinaryResponse,
  type OrdinaryResponseBinding,
  matchesBusiness3Response,
  validateBusiness3,
  validateStartupFailure,
  validateV2,
  v2Registry,
} from '@ontolearn/contracts/v2'
import { JsonlReader, parseStrictJson } from './jsonl'
import { TransportLedger } from './engine-ledger'

export interface EngineLocation {
  packaged: boolean
  appPath: string
  resourcesPath: string
}
export function getEngineCommand(
  location: EngineLocation,
  options: Pick<SupervisorOptions, 'profile' | 'exampleRoot'> = {},
): { command: string; args: string[] } {
  const exampleRoot = validatedExampleRoot(options)
  const executable = process.platform === 'win32' ? 'ontolearn-engine.exe' : 'ontolearn-engine'
  if (location.packaged)
    return { command: join(location.resourcesPath, 'engine', executable), args: [] }
  const root = resolve(location.appPath, '../..')
  const python =
    process.platform === 'win32'
      ? join(root, '.venv', 'Scripts', 'python.exe')
      : join(root, '.venv', 'bin', 'python')
  return {
    command: python,
    args:
      exampleRoot === undefined
        ? ['-I', '-m', 'ontolearn_engine']
        : ['-I', join(root, 'packages', 'engine', 'entrypoint.py')],
  }
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
function deniedOrdinary(): EngineError {
  return new EngineError({
    code: 'PERMISSION_DENIED',
    messageKey: 'permission.denied',
    params: {},
    retryable: false,
  })
}
function invalidStateOrdinary(): EngineError {
  return new EngineError({
    code: 'INVALID_STATE',
    messageKey: 'protocol.invalidState',
    params: {},
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
/** Finite plain-data encoding bound before validators, cloning or stringify. */
function mainlineArgumentBound(value: unknown, maximum: number): void {
  let bytes = 0,
    nodes = 0
  const stack: unknown[] = [value],
    seen = new Set<object>()
  const charge = (amount: number) => {
    bytes += amount
    if (bytes > maximum)
      throw new EngineError({
        code: 'RESOURCE_LIMIT',
        messageKey: 'resource.limitExceeded',
        params: { resource: 'frame' },
        retryable: false,
      })
  }
  const text = (value: string) => {
    if (value.length > maximum) charge(maximum + 1)
    charge(2)
    for (const ch of value) {
      const n = ch.codePointAt(0)!
      charge(
        n < 32 || (n >= 0xd800 && n <= 0xdfff)
          ? 6
          : ch === '"' || ch === '\\'
            ? 2
            : Buffer.byteLength(ch, 'utf8'),
      )
    }
  }
  while (stack.length) {
    const item = stack.pop()
    if (++nodes > maximum) charge(maximum + 1)
    if (item === null) {
      charge(4)
      continue
    }
    if (typeof item === 'string') {
      text(item)
      continue
    }
    if (typeof item === 'boolean') {
      charge(5)
      continue
    }
    if (typeof item === 'number') {
      if (!Number.isFinite(item)) throw invalid()
      charge(32)
      continue
    }
    if (!item || typeof item !== 'object' || seen.has(item)) throw invalid()
    seen.add(item)
    if (Array.isArray(item)) {
      if (item.length > maximum) charge(maximum + 1)
      charge(2 + item.length)
      for (let i = 0; i < item.length; i++) {
        const d = Object.getOwnPropertyDescriptor(item, String(i))
        if (!d || !('value' in d)) throw invalid()
        stack.push(d.value)
      }
    } else {
      const proto = Object.getPrototypeOf(item)
      if (proto !== Object.prototype && proto !== null) throw invalid()
      charge(2)
      for (const key in item) {
        if (!Object.hasOwn(item, key)) throw invalid()
        text(key)
        charge(2)
        const d = Object.getOwnPropertyDescriptor(item, key)
        if (!d || !('value' in d)) throw invalid()
        stack.push(d.value)
        if (stack.length > maximum) charge(maximum + 1)
      }
    }
  }
}
/** Conservative JSON-sized measure without constructing an aggregate string.
 * Repeated aliases are counted at every occurrence; cycles/accessors are rejected.
 * The receiver prepaid the same bounded traversal scratch before entering service code.
 */
function mainlineHoldingMeasure(
  value: unknown,
  maximum: number,
): { bytes: number; objects: number; work: number } {
  let bytes = 0,
    nodes = 0
  const active = new Set<object>()
  const stack: Array<{ value: unknown; depth: number; exit?: object }> = [{ value, depth: 0 }]
  const charge = (n: number) => {
    bytes += n
    if (bytes > maximum) throw invalidStateOrdinary()
  }
  const text = (v: string) => {
    if (v.length > maximum) throw invalidStateOrdinary()
    charge(2)
    for (const c of v) {
      const cp = c.codePointAt(0)!
      charge(
        cp < 32 || (cp >= 0xd800 && cp <= 0xdfff)
          ? 6
          : c === '"' || c === '\\'
            ? 2
            : Buffer.byteLength(c, 'utf8'),
      )
    }
  }
  while (stack.length) {
    const next = stack.pop()!
    if (next.exit) {
      active.delete(next.exit)
      continue
    }
    const v = next.value
    if (++nodes > 263168 || next.depth > 32) throw invalidStateOrdinary()
    if (v === null) {
      charge(4)
      continue
    }
    if (typeof v === 'string') {
      text(v)
      continue
    }
    if (typeof v === 'boolean') {
      charge(5)
      continue
    }
    if (typeof v === 'number' && Number.isFinite(v)) {
      charge(32)
      continue
    }
    if (!v || typeof v !== 'object' || active.has(v)) throw invalidStateOrdinary()
    if (!Array.isArray(v) && ![Object.prototype, null].includes(Object.getPrototypeOf(v)))
      throw invalidStateOrdinary()
    active.add(v)
    stack.push({ value: undefined, depth: next.depth, exit: v })
    charge(2)
    if (Array.isArray(v)) {
      if (v.length > maximum || v.length + stack.length > 263168) throw invalidStateOrdinary()
      charge(v.length)
      for (let i = v.length - 1; i >= 0; i--) {
        const d = Object.getOwnPropertyDescriptor(v, String(i))
        if (!d || !('value' in d)) throw invalidStateOrdinary()
        stack.push({ value: d.value, depth: next.depth + 1 })
      }
    } else {
      for (const key in v) {
        if (!Object.hasOwn(v, key)) throw invalidStateOrdinary()
        text(key)
        charge(2)
        const d = Object.getOwnPropertyDescriptor(v, key)
        if (!d || !('value' in d) || stack.length >= 263168) throw invalidStateOrdinary()
        stack.push({ value: d.value, depth: next.depth + 1 })
      }
    }
  }
  return { bytes: 32 * bytes + 4096, objects: bytes + 128, work: 8 * bytes }
}
interface MainlineOwnerRecord {
  selectionEntry: object
  owner: Readonly<{ ownerId: string }>
  session?: Session
  selected?: ProjectView
  tickets: Set<{ terminal: boolean; released: boolean; requestId?: string }>
  activeDelivery?: MainlineDelivery
  lastOrphanDelivery?: MainlineDelivery
  uncertain?: boolean
  budget?: QueryMainReadBudget
}
interface MainlineRecoveryPrincipal {
  origin: MainlineOwnerRecord
  session?: Session
  project?: ProjectView
  current?: () => boolean
  active: number
  retired: boolean
  released: boolean
  cleanupFailed: boolean
}
interface MainlineDelivery {
  state: 'COMPUTING' | 'OFFERED' | 'UNKNOWN' | 'ORPHAN'
  orphan: boolean
  computations: number
  callbackDone: boolean
  bytes: number
  objects: number
  work: number
  records: Set<MainlineOwnerRecord>
  session?: Session
  aliases: unknown[]
  wires: Map<string, { session: Session; terminal: boolean }>
  consumptions: Map<object, () => void>
  consuming: boolean
}
interface MainlineHolding {
  record: MainlineOwnerRecord
  session: Session
  value?: unknown
  bytes: number
  objects: number
}
/** A brand is necessary but not sufficient: only the issuing private WeakMap authenticates it. */
export abstract class MainlineReplyReceipt {
  #receipt = true
  static owns(value: unknown): value is MainlineReplyReceipt {
    return !!value && typeof value === 'object' && #receipt in value
  }
}
export interface MainlineReplyDiagnostic {
  readonly slots: number
  readonly computing: number
  readonly offered: number
  readonly unknown: number
  readonly orphans: number
  readonly retainedBytes: number
  readonly retainedObjects: number
  readonly deliveryBytes: number
  readonly deliveryObjects: number
  readonly holdingCount: number
  readonly scratchBytes: number
  readonly scratchObjects: number
  readonly totalWork: number
  readonly maxWindowWork: number
}
/** Main-process only; this is delivery responsibility, never a project/read grant or GC proof. */
export abstract class MainlineReplyReceiver {
  abstract receive<T>(work: () => Promise<T>): Promise<{ value: T; receipt: MainlineReplyReceipt }>
  abstract consume(originalReceipt: MainlineReplyReceipt): void
  abstract binding(
    originalReceipt: MainlineReplyReceipt,
  ): Readonly<{ engineSessionId: string | undefined }>
  abstract diagnostic(): Readonly<MainlineReplyDiagnostic>
}
export type MainlineMethod =
  | 'project.catalog'
  | 'project.create'
  | 'project.example.create'
  | 'project.open'
  | 'project.read'
  | 'project.ownership.detail'
  | 'project.draft.save'
  | 'project.management.catalog'
  | 'project.management.read'
  | 'project.management.preview'
  | 'project.management.confirm'
  | 'project.management.apply'
  | 'project.management.operation.get'
  | 'project.library.status'
export abstract class MainlineProjectTransport {
  #mainlineTransport = true
  static owns(value: unknown): value is MainlineProjectTransport {
    return !!value && typeof value === 'object' && #mainlineTransport in value
  }
  abstract readonly owner: Readonly<{ ownerId: string }>
  abstract readonly supervisor: EngineSupervisor
  abstract get engineSessionId(): string | undefined
  abstract get selected(): ProjectView | undefined
  abstract request(method: MainlineMethod, params: Record<string, unknown>): Promise<unknown>
  abstract acceptProject(project: ProjectView): void
}
interface Pending {
  delivery?: MainlineDelivery
  mainlineRead?: QueryProjectReadTicket
  mainlineOwner?: MainlineOwnerRecord
  ordinaryBinding?: OrdinaryResponseBinding
  request: Record<string, unknown>
  resolve(value: unknown): void
  reject(error: EngineError): void
  timer: ReturnType<typeof setTimeout>
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
  closed: Promise<void>
  resolveClosed(): void
  generation: number
  reader: JsonlReader
  pending: Map<string, Pending>
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
/** One main-side owner book for active AND retired client/source holdings.
 * Registered owners remain strongly held; their high-water reservations are never
 * refunded merely by dispose, timeout, release failure or a new session. This is
 * the approved logical rejection cap, not a physical allocation/RSS claim.
 */
export class OrdinaryRetentionAccount {
  constructor(private readonly reserveHolding: (bytes: number, objects: number) => void) {}
  reserve(bytes: number, objects: number): void {
    this.reserveHolding(bytes, objects)
  }
}
export class OrdinaryRetentionBook {
  #accounts = new Map<object, { bytes: number; objects: number }>()
  #total(): { bytes: number; objects: number } {
    return [...this.#accounts.values()].reduce(
      (n, c) => ({ bytes: n.bytes + c.bytes, objects: n.objects + c.objects }),
      { bytes: 0, objects: 0 },
    )
  }
  #check(bytes: number, objects: number): void {
    if (
      !Number.isSafeInteger(bytes) ||
      !Number.isSafeInteger(objects) ||
      bytes < 0 ||
      objects < 0 ||
      bytes > 262144 ||
      objects > 4096
    )
      throw invalidStateOrdinary()
  }
  pair(): readonly [OrdinaryRetentionAccount, OrdinaryRetentionAccount] {
    const total = this.#total()
    this.#check(total.bytes + 8192, total.objects + 64)
    const issue = () => {
      const token = Object.freeze({})
      this.#accounts.set(token, { bytes: 4096, objects: 32 })
      return new OrdinaryRetentionAccount((bytes, objects) => {
        this.#check(bytes, objects)
        const old = this.#accounts.get(token)!
        const next = { bytes: Math.max(old.bytes, bytes), objects: Math.max(old.objects, objects) }
        const current = this.#total()
        this.#check(
          current.bytes - old.bytes + next.bytes,
          current.objects - old.objects + next.objects,
        )
        this.#accounts.set(token, next)
      })
    }
    return Object.freeze([issue(), issue()] as const)
  }
  usage(): Readonly<{ bytes: number; objects: number; accounts: number }> {
    return Object.freeze({ ...this.#total(), accounts: this.#accounts.size })
  }
}

/** Legacy injection seam remains external. The private mainline issuer below binds real business3 Sessions. */
/** Prepaid main-side read/holding consumer supplied only by the original issuer.
 * reserve is monotonic work/holding (production temporary peaks are permanent high-water reservations);
 * handoff must retain response aliases through actual delivery, not lexical exit.
 */
export abstract class QueryProjectReadTicket {
  /** Must authenticate real backend registration/ack via the external bridge;
   * mere local registration is insufficient. The mainline implementation below
   * accepts only its original matched response, without claiming backend cleanup. */
  abstract attachDispatch(
    context: Readonly<{
      requestId: string
      sessionId: string
      child: ChildProcessWithoutNullStreams
      owner: object
      binding: Readonly<Record<string, unknown>>
      params: Readonly<Record<string, unknown>>
    }>,
  ): void
  /** Releases only against actual bridge terminal evidence; unknown keeps holding. */
  abstract release(): void
}
export abstract class QueryMainReadBudget {
  beginConsumerRequest(): () => void {
    return () => {}
  }
  abstract reserve(stage: string, bytes: number, objects: number, work: number): void
  abstract handoff(value: unknown): void
  abstract beforeArguments(value: unknown): void
  abstract existingProjectGet(binding: Readonly<Record<string, unknown>>): QueryProjectReadTicket
  retainHolding(originalEntry: object, value: unknown): void
  retainHolding(): void {
    throw invalidStateOrdinary()
  }
  releaseHolding(originalEntry: object): void
  releaseHolding(): void {
    throw invalidStateOrdinary()
  }
  /** Main-only cache retirement, authenticated by this entry's original reply ACK. */
  onReplyConsumed(originalEntry: object, retire: () => void): void
  onReplyConsumed(): void {
    throw invalidStateOrdinary()
  }
}
export abstract class OrdinaryLibraryAuthority {
  #ordinaryAuthority = true
  static owns(value: unknown): value is OrdinaryLibraryAuthority {
    return !!value && typeof value === 'object' && #ordinaryAuthority in value
  }
  abstract allows(supervisor: EngineSupervisor): boolean
  queryReadScope(supervisor: EngineSupervisor, owner: object): QueryMainReadBudget | null
  queryReadScope(): QueryMainReadBudget | null {
    return null
  }
}
export abstract class OrdinaryLibraryTransport {
  #ordinaryTransport = true
  static owns(value: unknown): value is OrdinaryLibraryTransport {
    return !!value && typeof value === 'object' && #ordinaryTransport in value
  }
  abstract readonly ownerId: string
  abstract readonly supervisor: EngineSupervisor
  abstract get engineSessionId(): string | undefined
  abstract claimSource(owner: object): OrdinaryRetentionAccount
  abstract request(params: Record<string, unknown>): Promise<unknown>
  abstract observe(listener: (state: EngineConnectionState) => void): () => void
}
interface OrdinaryClientRecord {
  attempted: boolean
  starting?: Promise<Session>
  clientAccount: OrdinaryRetentionAccount
  sourceAccount: OrdinaryRetentionAccount
  sourceOwner?: object
  session?: Session
  menuSeq: number
  choices: Map<string, string>
  actions: Map<
    number,
    { actionId: string; projectId: string; leaseRef?: string; project?: Record<string, unknown> }
  >
}

export interface SupervisorOptions {
  /** Requires an actual runtime issuer, never an owner/options DTO alone. */
  ordinaryLibrary?: { ownerId: string; authority: OrdinaryLibraryAuthority }
  /** Trusted main-process option; never derived from inherited environment or renderer. */
  profile?: EngineProfile
  /** Trusted main-only loader path. Never sourced from renderer, wire, environment or cwd. */
  exampleRoot?: string
  /** Trusted main-only bounded transport evidence for observed E2E launches.
   * Resolved by main from its own environment and isolated profile; the
   * supervisor independently refuses it for packaged locations. */
  transportLedger?: { path: string; launchId: string | null }
  dataPath?: string
  /** Main-owned file identity, checked by the engine before and after acquiring its writer lease. */
  libraryFileIdentity?: { dev: string; ino: string }
  /** Explicitly reserved new files alone may initialize; existing files must be recognized databases. */
  libraryRequireExisting?: boolean
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

function validatedExampleRoot(
  options: Pick<SupervisorOptions, 'profile' | 'exampleRoot'>,
): string | undefined {
  const root = options.exampleRoot
  if (root === undefined) return undefined
  if (
    options.profile !== 'business3' ||
    typeof root !== 'string' ||
    !isAbsolute(root) ||
    root.includes('\0')
  )
    throw invalid()
  return root
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
  #mainlineClient?: MainlineProjectTransport
  #mainlineRecords = new Map<MainlineProjectTransport, MainlineOwnerRecord>()
  #mainlineTickets = new WeakMap<
    QueryProjectReadTicket,
    {
      record: MainlineOwnerRecord
      state: { terminal: boolean; released: boolean; requestId?: string }
    }
  >()
  #mainlineProjects = new WeakMap<object, { record: MainlineOwnerRecord; session: Session }>()
  #mainlineRecoveryPrincipals = new WeakMap<object, MainlineRecoveryPrincipal>()
  #mainlineRecoveryOperations = new WeakSet<Promise<unknown>>()
  #mainlineRecoveryOpen = new WeakMap<
    MainlineProjectTransport,
    (projectId: string, current: () => void) => Promise<unknown>
  >()
  #mainlineRecoveryViews = new WeakMap<MainlineOwnerRecord, object>()
  #mainlineCost = { bytes: 0, objects: 0, work: 0 }
  #mainlineScratch = { bytes: 0, objects: 0 }
  #mainlineAsync = new AsyncLocalStorage<MainlineDelivery>()
  #mainlineDeliveries = new Set<MainlineDelivery>()
  #mainlineReceipts = new WeakMap<MainlineReplyReceipt, MainlineDelivery>()
  #mainlineConsumed = new WeakSet<MainlineReplyReceipt>()
  #mainlineHoldingEntries = new WeakMap<object, MainlineHolding>()
  #mainlineHoldings = new Set<MainlineHolding>()
  #mainlineReceiver?: MainlineReplyReceiver
  #mainlineComputing?: MainlineDelivery
  #mainlineMaxWindowWork = 0
  #ordinaryClient?: OrdinaryLibraryTransport
  #queryPins = new WeakMap<
    object,
    {
      owner: object
      session: Session
      guard: () => boolean
      binding?: Readonly<Record<string, unknown>>
      writeEntered: boolean
    }
  >()
  #ordinaryRecords = new Map<OrdinaryLibraryTransport, OrdinaryClientRecord>()
  #ordinaryRetention = new OrdinaryRetentionBook()
  #ordinaryStartingRecords = new Set<OrdinaryClientRecord>()
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
  // A terminal transport can still own a live process. Retain it until real close.
  #liveChildren = new Set<Session>()
  #admissionFrozen = false
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
  readonly #ledger: TransportLedger | undefined
  constructor(location: EngineLocation, options: SupervisorOptions = {}) {
    if (options.profile !== undefined && !['legacy2', 'business3'].includes(options.profile))
      throw invalid()
    const exampleRoot = validatedExampleRoot(options)
    this.#profile = options.profile ?? 'legacy2'
    this.#location = { ...location }
    this.#options = {
      ...options,
      exampleRoot,
      libraryFileIdentity: options.libraryFileIdentity
        ? { ...options.libraryFileIdentity }
        : undefined,
      ordinaryLibrary: options.ordinaryLibrary ? { ...options.ordinaryLibrary } : undefined,
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
    // Independent packaged rejection: a packaged location never opens a ledger.
    this.#ledger =
      this.#location.packaged || !options.transportLedger
        ? undefined
        : TransportLedger.open({
            path: options.transportLedger.path,
            launchId: options.transportLedger.launchId,
            appPid: process.pid,
            platform: process.platform,
          })
  }
  #mainlineReady(record: MainlineOwnerRecord): Session {
    const session = record.session
    if (
      this.#profile !== 'business3' ||
      this.#options.testMode ||
      record.uncertain ||
      !session ||
      !this.#current(session) ||
      session.profile !== 'business3' ||
      session.hello?.selectedVersion !== 3 ||
      !['project.catalog', 'project.create', 'project.open', 'project.read'].every((method) =>
        session.hello!.capabilities.includes(method),
      )
    )
      throw deniedOrdinary()
    return session
  }
  #mainlineReserve(
    bytes: number,
    objects: number,
    work: number,
    delivery: MainlineDelivery | null | undefined = this.#mainlineAsync.getStore(),
    allowUnknownOutput = false,
  ): void {
    if (
      [bytes, objects, work].some((n) => !Number.isSafeInteger(n) || n < 0) ||
      this.#mainlineCost.bytes + bytes > 134217728 ||
      this.#mainlineCost.objects + objects > 1048576 ||
      !Number.isSafeInteger(this.#mainlineCost.work + work) ||
      (delivery &&
        (!this.#mainlineDeliveries.has(delivery) ||
          (delivery.state === 'UNKNOWN' && !allowUnknownOutput) ||
          delivery.state === 'OFFERED' ||
          delivery.work + work > 536870912))
    )
      throw invalidStateOrdinary()
    this.#mainlineCost.bytes += bytes
    this.#mainlineCost.objects += objects
    this.#mainlineCost.work += work
    if (delivery) {
      delivery.work += work
      this.#mainlineMaxWindowWork = Math.max(this.#mainlineMaxWindowWork, delivery.work)
    }
  }
  #deliveryReserve(delivery: MainlineDelivery, bytes: number, objects: number, work: number): void {
    this.#mainlineReserve(bytes, objects, work, delivery, delivery.state === 'UNKNOWN')
    delivery.bytes += bytes
    delivery.objects += objects
  }
  #scratchReserve(delivery: MainlineDelivery, bytes: number, objects: number, work: number): void {
    const nextBytes = Math.max(this.#mainlineScratch.bytes, bytes)
    const nextObjects = Math.max(this.#mainlineScratch.objects, objects)
    this.#mainlineReserve(
      nextBytes - this.#mainlineScratch.bytes,
      nextObjects - this.#mainlineScratch.objects,
      work,
      delivery,
    )
    this.#mainlineScratch.bytes = nextBytes
    this.#mainlineScratch.objects = nextObjects
  }
  #newDelivery(orphan: boolean): MainlineDelivery {
    if (this.#mainlineDeliveries.size >= 16 || this.#mainlineComputing) throw invalidStateOrdinary()
    const delivery: MainlineDelivery = {
      state: orphan ? 'ORPHAN' : 'COMPUTING',
      orphan,
      computations: 0,
      callbackDone: false,
      bytes: 0,
      objects: 0,
      work: 0,
      records: new Set(),
      aliases: [],
      wires: new Map(),
      consumptions: new Map(),
      consuming: false,
      session: this.#session && this.#current(this.#session) ? this.#session : undefined,
    }
    this.#mainlineDeliveries.add(delivery)
    try {
      this.#deliveryReserve(delivery, 4096, 128, 4096)
      // Also prepays cached/local reply traversal before the callback can return an alias.
      this.#scratchReserve(delivery, 8388608, 263168, 8388608)
    } catch (cause) {
      delivery.state = 'UNKNOWN'
      throw cause
    }
    return delivery
  }
  #delivery(record: MainlineOwnerRecord): MainlineDelivery {
    const delivery =
      this.#mainlineAsync.getStore() ?? record.activeDelivery ?? record.lastOrphanDelivery
    if (
      !delivery ||
      !this.#mainlineDeliveries.has(delivery) ||
      (delivery.state !== 'COMPUTING' && delivery.state !== 'ORPHAN')
    )
      throw invalidStateOrdinary()
    this.#bindDelivery(delivery, record)
    return delivery
  }
  #bindDelivery(delivery: MainlineDelivery, record: MainlineOwnerRecord): void {
    if (record.session) {
      if (delivery.session && delivery.session !== record.session) {
        this.#unknownDelivery(delivery)
        throw deniedOrdinary()
      }
      delivery.session = record.session
    }
    delivery.records.add(record)
  }
  #unknownDelivery(delivery: MainlineDelivery): void {
    delivery.state = 'UNKNOWN'
    for (const record of delivery.records) record.uncertain = true
  }
  #holdingSize(value: unknown): { bytes: number; objects: number; work: number } {
    mainlineArgumentBound(value, 263168)
    const raw = JSON.stringify(value)
    if (typeof raw !== 'string' || Buffer.byteLength(raw, 'utf8') > 263168)
      throw invalidStateOrdinary()
    return {
      bytes: 32 * Buffer.byteLength(raw, 'utf8') + 4096,
      objects: raw.length + 128,
      work: 8 * raw.length,
    }
  }
  #retainHolding(record: MainlineOwnerRecord, originalEntry: object, value: unknown): void {
    const session = this.#mainlineReady(record)
    if (!originalEntry || typeof originalEntry !== 'object') throw invalidStateOrdinary()
    const old = this.#mainlineHoldingEntries.get(originalEntry)
    if (old && (old.record !== record || old.session !== session)) throw deniedOrdinary()
    if (old && old.bytes !== 0 && old.value === value) return
    const inherited =
      this.#mainlineAsync.getStore() ?? record.activeDelivery ?? record.lastOrphanDelivery
    const delivery =
      inherited &&
      this.#mainlineDeliveries.has(inherited) &&
      ['COMPUTING', 'ORPHAN'].includes(inherited.state)
        ? this.#delivery(record)
        : null
    if (!delivery && (!old || old.bytes === 0)) throw invalidStateOrdinary()
    // An existing selected-source entry can be replaced by an authenticated
    // same-session notification. It cannot issue a wire call or new entry.
    // The globally prepaid scratch remains; work is one bounded local measure.
    const maximum = Math.min(
      Math.floor((134217728 - this.#mainlineCost.bytes - 4096) / 32),
      1048576 - this.#mainlineCost.objects - 128,
      delivery ? 134217728 : 263168,
    )
    if (maximum < 1) throw invalidStateOrdinary()
    // Prepay bounded measuring work before traversing the retained aggregate.
    this.#mainlineReserve(0, 0, 8388608, delivery)
    const cost = mainlineHoldingMeasure(value, maximum)
    this.#mainlineReserve(cost.bytes, cost.objects, cost.work, delivery)
    const holding = old ?? { record, session, bytes: 0, objects: 0 }
    this.#mainlineCost.bytes -= holding.bytes
    this.#mainlineCost.objects -= holding.objects
    holding.value = value
    holding.bytes = cost.bytes
    holding.objects = cost.objects
    this.#mainlineHoldingEntries.set(originalEntry, holding)
    this.#mainlineHoldings.add(holding)
  }
  #releaseHolding(record: MainlineOwnerRecord, originalEntry: object): void {
    const holding = this.#mainlineHoldingEntries.get(originalEntry)
    if (!holding || holding.record !== record) throw deniedOrdinary()
    if (holding.bytes === 0) return
    // Old owner cleanup may close its own logical holding after a session change.
    // It never grants a new request and never releases another owner's entry.
    this.#mainlineCost.bytes -= holding.bytes
    this.#mainlineCost.objects -= holding.objects
    holding.value = undefined
    holding.bytes = holding.objects = 0
    this.#mainlineHoldings.delete(holding)
  }
  #selectMainlineProject(record: MainlineOwnerRecord, project: ProjectView | undefined): void {
    if (project) {
      // This engine alias survives a source fence and owns a separate holding.
      // Replacement admits overlap before dropping the previous selected alias.
      this.#retainHolding(record, record.selectionEntry, project)
      record.selected = project
    } else {
      record.selected = undefined
      if (this.#mainlineHoldingEntries.get(record.selectionEntry)?.bytes)
        this.#releaseHolding(record, record.selectionEntry)
    }
  }
  mainlineReplyReceiver(): MainlineReplyReceiver {
    if (this.#profile !== 'business3' || this.#options.testMode) throw deniedOrdinary()
    if (this.#mainlineReceiver) return this.#mainlineReceiver
    this.#mainlineReceiver = new (class extends MainlineReplyReceiver {
      constructor(private readonly supervisor: EngineSupervisor) {
        super()
      }
      async receive<T>(
        work: () => Promise<T>,
      ): Promise<{ value: T; receipt: MainlineReplyReceipt }> {
        if (this.supervisor.#mainlineAsync.getStore() || typeof work !== 'function')
          throw invalidStateOrdinary()
        const delivery = this.supervisor.#newDelivery(false)
        this.supervisor.#mainlineComputing = delivery
        try {
          const value = await this.supervisor.#mainlineAsync.run(delivery, work)
          if (delivery.computations !== 0) throw invalidStateOrdinary()
          const cost = this.supervisor.#holdingSize(value)
          if (
            !delivery.aliases.length &&
            value &&
            typeof value === 'object' &&
            (value as Record<string, unknown>).ok === true &&
            (!delivery.session || !this.supervisor.#current(delivery.session))
          )
            throw deniedOrdinary()
          if (delivery.aliases.length) {
            const last = delivery.aliases.at(-1)
            const result =
              value && typeof value === 'object' ? (value as Record<string, unknown>) : null
            if (result?.ok === false) this.supervisor.#unknownDelivery(delivery)
            else if ((result?.ok === true ? result.data : value) !== last)
              throw invalidStateOrdinary()
          }
          // Prepaid scratch bounded the callback result before encoding/retention.
          this.supervisor.#deliveryReserve(delivery, cost.bytes, cost.objects, cost.work)
          delivery.aliases.push(value)
          if (delivery.state !== 'UNKNOWN') delivery.state = 'OFFERED'
          delivery.callbackDone = true
          const receipt = new (class extends MainlineReplyReceipt {})()
          this.supervisor.#mainlineReceipts.set(receipt, delivery)
          return { value, receipt }
        } catch (cause) {
          this.supervisor.#unknownDelivery(delivery)
          throw cause
        } finally {
          if (this.supervisor.#mainlineComputing === delivery)
            this.supervisor.#mainlineComputing = undefined
        }
      }
      consume(originalReceipt: MainlineReplyReceipt): void {
        if (!MainlineReplyReceipt.owns(originalReceipt)) throw deniedOrdinary()
        if (this.supervisor.#mainlineConsumed.has(originalReceipt)) return
        const delivery = this.supervisor.#mainlineReceipts.get(originalReceipt)
        if (
          !delivery ||
          delivery.consuming ||
          delivery.state !== 'OFFERED' ||
          !delivery.callbackDone ||
          delivery.computations !== 0 ||
          [...delivery.wires.values()].some((wire) => !wire.terminal) ||
          [...delivery.records].some((record) => record.uncertain) ||
          (delivery.session && !this.supervisor.#current(delivery.session))
        )
          throw invalidStateOrdinary()
        // A failing cache cleanup retains this exact receipt and its delivery
        // aliases. Completed cleanups are removed individually, so a retry
        // cannot refund another entry twice. No timeout/UNKNOWN runs callbacks.
        delivery.consuming = true
        try {
          for (const [entry, retire] of delivery.consumptions) {
            retire()
            delivery.consumptions.delete(entry)
          }
        } finally {
          delivery.consuming = false
        }
        this.supervisor.#mainlineCost.bytes -= delivery.bytes
        this.supervisor.#mainlineCost.objects -= delivery.objects
        delivery.aliases.length = 0
        delivery.wires.clear()
        delivery.records.clear()
        this.supervisor.#mainlineDeliveries.delete(delivery)
        this.supervisor.#mainlineReceipts.delete(originalReceipt)
        this.supervisor.#mainlineConsumed.add(originalReceipt)
      }
      binding(
        originalReceipt: MainlineReplyReceipt,
      ): Readonly<{ engineSessionId: string | undefined }> {
        if (!MainlineReplyReceipt.owns(originalReceipt)) throw deniedOrdinary()
        const delivery = this.supervisor.#mainlineReceipts.get(originalReceipt)
        if (!delivery) throw deniedOrdinary()
        return Object.freeze({ engineSessionId: delivery.session?.hello?.engineSessionId })
      }
      diagnostic(): Readonly<MainlineReplyDiagnostic> {
        const values = [...this.supervisor.#mainlineDeliveries]
        return Object.freeze({
          slots: values.length,
          computing: values.filter((x) => x.state === 'COMPUTING').length,
          offered: values.filter((x) => x.state === 'OFFERED').length,
          unknown: values.filter((x) => x.state === 'UNKNOWN').length,
          orphans: values.filter((x) => x.orphan).length,
          retainedBytes: this.supervisor.#mainlineCost.bytes,
          retainedObjects: this.supervisor.#mainlineCost.objects,
          deliveryBytes: values.reduce((n, x) => n + x.bytes, 0),
          deliveryObjects: values.reduce((n, x) => n + x.objects, 0),
          holdingCount: this.supervisor.#mainlineHoldings.size,
          scratchBytes: this.supervisor.#mainlineScratch.bytes,
          scratchObjects: this.supervisor.#mainlineScratch.objects,
          totalWork: this.supervisor.#mainlineCost.work,
          maxWindowWork: this.supervisor.#mainlineMaxWindowWork,
        })
      }
    })(this)
    return this.#mainlineReceiver
  }
  #mainlineBudget(record: MainlineOwnerRecord): QueryMainReadBudget {
    this.#mainlineReady(record)
    if (record.budget) return record.budget
    record.budget = new (class extends QueryMainReadBudget {
      constructor(private readonly supervisor: EngineSupervisor) {
        super()
      }
      beginConsumerRequest(): () => void {
        this.supervisor.#mainlineReady(record)
        const inherited = this.supervisor.#mainlineAsync.getStore()
        const delivery = inherited ?? this.supervisor.#newDelivery(true)
        if (
          record.activeDelivery ||
          (this.supervisor.#mainlineComputing && this.supervisor.#mainlineComputing !== delivery) ||
          (delivery.state !== 'COMPUTING' && delivery.state !== 'ORPHAN') ||
          [...record.tickets].some((ticket) => !ticket.terminal && !ticket.released)
        )
          throw invalidStateOrdinary()
        this.supervisor.#bindDelivery(delivery, record)
        delivery.computations++
        record.activeDelivery = delivery
        if (delivery.orphan) record.lastOrphanDelivery = delivery
        this.supervisor.#mainlineComputing = delivery
        let ended = false
        return () => {
          if (!ended) {
            ended = true
            delivery.computations--
            if (record.activeDelivery === delivery) record.activeDelivery = undefined
            if (delivery.orphan && this.supervisor.#mainlineComputing === delivery)
              this.supervisor.#mainlineComputing = undefined
          }
        }
      }
      reserve(stage: string, bytes: number, objects: number, work: number): void {
        this.supervisor.#mainlineReady(record)
        if (typeof stage !== 'string' || stage.length > 128) throw invalidStateOrdinary()
        if ([bytes, objects, work].some((n) => !Number.isSafeInteger(n) || n < 0))
          throw invalidStateOrdinary()
        this.supervisor.#scratchReserve(this.supervisor.#delivery(record), bytes, objects, work)
      }
      retainHolding(originalEntry: object, value: unknown): void {
        this.supervisor.#retainHolding(record, originalEntry, value)
      }
      releaseHolding(originalEntry: object): void {
        this.supervisor.#releaseHolding(record, originalEntry)
      }
      onReplyConsumed(originalEntry: object, retire: () => void): void {
        const session = this.supervisor.#mainlineReady(record)
        const holding = this.supervisor.#mainlineHoldingEntries.get(originalEntry)
        if (
          !holding ||
          holding.record !== record ||
          holding.session !== session ||
          holding.bytes === 0 ||
          typeof retire !== 'function'
        )
          throw deniedOrdinary()
        const delivery = this.supervisor.#delivery(record)
        if (
          delivery.session !== session ||
          delivery.consumptions.has(originalEntry) ||
          delivery.consumptions.size >= 16
        )
          throw invalidStateOrdinary()
        this.supervisor.#deliveryReserve(delivery, 512, 8, 4096)
        delivery.consumptions.set(originalEntry, retire)
      }
      beforeArguments(value: unknown): void {
        // Pay a complete admitted-frame material bound before any caller traversal.
        this.reserve('mainline arguments', 8388608, 263168, 8388608)
        if (value === undefined || ['symbol', 'function', 'bigint'].includes(typeof value))
          throw invalid()
        mainlineArgumentBound(
          value,
          Math.min(262144, this.supervisor.#mainlineReady(record).hello!.limits.maxFrameBytes),
        )
      }
      handoff(value: unknown): void {
        this.supervisor.#mainlineReady(record)
        const delivery = this.supervisor.#delivery(record)
        if (delivery.aliases.length >= 16) throw invalidStateOrdinary()
        const cost = this.supervisor.#holdingSize(value)
        try {
          this.supervisor.#deliveryReserve(delivery, cost.bytes, cost.objects, cost.work)
        } catch (cause) {
          this.supervisor.#unknownDelivery(delivery)
          throw cause
        }
        delivery.aliases.push(value)
      }
      existingProjectGet(binding: Readonly<Record<string, unknown>>): QueryProjectReadTicket {
        const session = this.supervisor.#mainlineReady(record)
        if (
          record.tickets.size >= 16 ||
          binding.projectId !== record.selected?.projectId ||
          binding.engineSessionId !== session.hello!.engineSessionId
        )
          throw deniedOrdinary()
        this.reserve('mainline project read ticket', 1048576, 1024, 1048576)
        const state: { terminal: boolean; released: boolean; requestId?: string } = {
          terminal: false,
          released: false,
        }
        const ticket = new (class extends QueryProjectReadTicket {
          constructor(private readonly supervisor: EngineSupervisor) {
            super()
          }
          attachDispatch(context: Parameters<QueryProjectReadTicket['attachDispatch']>[0]): void {
            const actual = this.supervisor.#mainlineReady(record),
              pending = actual.pending.get(context.requestId)
            if (
              state.requestId ||
              context.owner !== record.owner ||
              actual !== session ||
              context.child !== actual.child ||
              context.sessionId !== actual.hello!.engineSessionId ||
              !pending ||
              pending.request.method !== 'project.get' ||
              context.params.projectId !== binding.projectId ||
              (pending.request.params as Record<string, unknown>).projectId !== binding.projectId ||
              context.binding !== binding
            )
              throw deniedOrdinary()
            state.requestId = context.requestId
          }
          release(): void {
            if (state.released) return
            if (!state.terminal) throw invalidStateOrdinary()
            state.released = true
            record.tickets.delete(state)
          }
        })(this.supervisor)
        record.tickets.add(state)
        this.supervisor.#mainlineTickets.set(ticket, { record, state })
        return ticket
      }
    })(this)
    return record.budget
  }
  ownsMainlineClient(client: MainlineProjectTransport): boolean {
    const record = this.#mainlineRecords.get(client)
    if (!record) return false
    try {
      this.#mainlineReady(record)
      return true
    } catch {
      return false
    }
  }
  mainlineProjectClient(): MainlineProjectTransport | null {
    if (this.#profile !== 'business3' || this.#options.testMode) return null
    const previous = this.#mainlineClient && this.#mainlineRecords.get(this.#mainlineClient)
    if (this.#mainlineClient && previous && (!previous.session || this.#current(previous.session)))
      return this.#mainlineClient
    if (this.#mainlineRecords.size >= 16) throw invalidStateOrdinary()
    this.#mainlineReserve(8192, 128, 4096)
    const record: MainlineOwnerRecord = {
      selectionEntry: Object.freeze({}),
      owner: Object.freeze({ ownerId: randomUUID() }),
      tickets: new Set(),
    }
    const client = new (class extends MainlineProjectTransport {
      readonly owner = record.owner
      constructor(readonly supervisor: EngineSupervisor) {
        super()
        supervisor.#mainlineRecoveryOpen.set(this, (projectId, current) =>
          this.#request('project.open', { projectId }, current),
        )
      }
      get engineSessionId(): string | undefined {
        return record.session?.hello?.engineSessionId
      }
      get selected(): ProjectView | undefined {
        return record.selected
      }
      acceptProject(project: ProjectView): void {
        const session = this.supervisor.#mainlineReady(record),
          proof = this.supervisor.#mainlineProjects.get(project)
        const selected = record.selected
        if (
          !selected ||
          !proof ||
          proof.record !== record ||
          proof.session !== session ||
          project.projectId !== selected.projectId ||
          project.projectRevision < selected.projectRevision
        )
          throw deniedOrdinary()
        if (
          project.projectRevision === selected.projectRevision &&
          (project.inputSnapshotId !== selected.inputSnapshotId ||
            JSON.stringify(Object.entries(project.dependencyVector).sort()) !==
              JSON.stringify(Object.entries(selected.dependencyVector).sort()))
        )
          throw invalidStateOrdinary()
        this.supervisor.#selectMainlineProject(record, project)
      }
      request(method: MainlineMethod, params: Record<string, unknown>): Promise<unknown> {
        return this.#request(method, params)
      }
      #request(
        method: MainlineMethod,
        params: Record<string, unknown>,
        recoveryCurrent?: () => void,
      ): Promise<unknown> {
        return this.supervisor.#operation(async () => {
          recoveryCurrent?.()
          if (!record.session) record.session = await this.supervisor.#ensure()
          recoveryCurrent?.()
          const session = this.supervisor.#mainlineReady(record)
          if (
            ![
              'project.catalog',
              'project.create',
              'project.example.create',
              'project.draft.save',
              'project.open',
              'project.read',
              'project.ownership.detail',
              'project.management.catalog',
              'project.management.read',
              'project.management.preview',
              'project.management.confirm',
              'project.management.apply',
              'project.management.operation.get',
              'project.library.status',
            ].includes(method)
          )
            throw invalid()
          const frame = Math.min(262144, session.hello!.limits.maxFrameBytes)
          const budget = this.supervisor.#mainlineBudget(record)
          const finish = budget.beginConsumerRequest()
          try {
            budget.beforeArguments(params)
            if (!validateBusiness3('params_' + method, params)) throw invalid()
            if (
              (method === 'project.read' ||
                method === 'project.draft.save' ||
                method === 'project.ownership.detail' ||
                method === 'project.management.read') &&
              params.projectId !== record.selected?.projectId
            )
              throw deniedOrdinary()
            budget.reserve('mainline transport frame', 32 * frame, frame + 1024, 32 * frame)
            const value = await this.supervisor.#send(
              session,
              method,
              params,
              Math.min(this.supervisor.#requestMs, session.hello!.limits.requestMs),
              'request',
              false,
              undefined,
              undefined,
              undefined,
              record,
              recoveryCurrent,
            )
            this.supervisor.#mainlineReady(record)
            recoveryCurrent?.()
            if (!validateBusiness3('result_' + method, value)) throw invalid()
            if (method === 'project.open') {
              const project = value as ProjectView
              if (project.projectId !== params.projectId) throw invalid()
              const selected = Object.freeze({
                ...project,
                dependencyVector: Object.freeze({ ...project.dependencyVector }),
              })
              // Recheck immediately before selecting the actual reply. A user
              // switch during ensure/write/reply must never publish this old P.
              recoveryCurrent?.()
              this.supervisor.#selectMainlineProject(record, selected)
              this.supervisor.#mainlineProjects.set(selected, { record, session })
            } else if (method === 'project.create' || method === 'project.example.create') {
              // Actual create acceptance does not fabricate a project projection.
              this.supervisor.#selectMainlineProject(record, undefined)
            } else if (method === 'project.read') {
              const data = value as {
                projectId: string
                inputSnapshotId: string
                workspace: { domainRevision: number; inputSnapshotId: string }
                domain: { projectRevision: number; dependencyVector: Record<string, number> }
              }
              if (
                data.projectId !== params.projectId ||
                data.inputSnapshotId !== data.workspace.inputSnapshotId ||
                data.domain.projectRevision !== data.workspace.domainRevision
              )
                throw invalid()
              const selected = Object.freeze({
                projectId: data.projectId,
                projectRevision: data.domain.projectRevision,
                inputSnapshotId: data.inputSnapshotId,
                dependencyVector: Object.freeze({ ...data.domain.dependencyVector }),
                formatVersion: 3 as const,
              })
              this.supervisor.#selectMainlineProject(record, selected)
              this.supervisor.#mainlineProjects.set(selected, { record, session })
            }
            budget.handoff(value)
            return value
          } finally {
            finish()
          }
        })
      }
    })(this)
    const delivery = this.#mainlineAsync.getStore()
    if (delivery) this.#bindDelivery(delivery, record)
    this.#mainlineRecords.set(client, record)
    this.#mainlineClient = client
    return client
  }
  /** Main-only, issued while a real selected client is still authenticated.
   * The original project is independently held; retiring a principal cannot wash
   * that reservation or an unknown reply into a replacement session's book.
   */
  issueMainlineRecovery(client: MainlineProjectTransport, current: () => boolean): object {
    const record = this.#mainlineRecords.get(client)
    if (!record || !MainlineProjectTransport.owns(client) || typeof current !== 'function')
      throw deniedOrdinary()
    const session = this.#mainlineReady(record),
      project = record.selected,
      proof = project && this.#mainlineProjects.get(project)
    if (!project || proof?.record !== record || proof.session !== session) throw deniedOrdinary()
    const token = Object.freeze({})
    this.#mainlineReserve(1024, 16, 1024, this.#delivery(record))
    this.#retainHolding(record, token, {
      engineSessionId: session.hello!.engineSessionId,
      project,
    })
    this.#mainlineRecoveryPrincipals.set(token, {
      origin: record,
      session,
      project,
      current,
      active: 0,
      retired: false,
      released: false,
      cleanupFailed: false,
    })
    return token
  }
  #finishMainlineRetirement(token: object, principal: MainlineRecoveryPrincipal): boolean {
    if (principal.released) return true
    if (!principal.retired || principal.active !== 0) return false
    // End the principal's own aliases before closing its exact logical holding.
    // A failed release still has the original token/origin and funded holding;
    // retry needs neither an old project DTO nor its service-current closure.
    principal.project = undefined
    principal.session = undefined
    principal.current = undefined
    this.#releaseHolding(principal.origin, token)
    principal.released = true
    principal.cleanupFailed = false
    return true
  }
  #endMainlineRecovery(token: object, principal: MainlineRecoveryPrincipal): void {
    principal.active--
    if (principal.retired) {
      try {
        this.#finishMainlineRetirement(token, principal)
      } catch {
        // The service retains the original authenticated cleanup handle. Its
        // later retry must not be replaced by this attempt's cleanup exception.
        principal.cleanupFailed = true
      }
    }
  }
  retireMainlineRecovery(client: MainlineProjectTransport, token: object): boolean {
    const record = this.#mainlineRecords.get(client),
      principal = this.#mainlineRecoveryPrincipals.get(token)
    if (
      !MainlineProjectTransport.owns(client) ||
      !record ||
      !principal ||
      principal.origin !== record
    )
      throw deniedOrdinary()
    // Revocation precedes cleanup and is permanent, including when active work
    // or a cleanup failure keeps the original handle/holding alive.
    principal.retired = true
    try {
      return this.#finishMainlineRetirement(token, principal)
    } catch (cause) {
      principal.cleanupFailed = true
      throw cause
    }
  }
  isMainlineRecoveryRefusal(cause: unknown, operation: Promise<unknown>): boolean {
    const issued = this.#operations.get(operation)
    return (
      this.#mainlineRecoveryOperations.has(operation) &&
      !!issued &&
      issued.cause === cause &&
      this.#origins.get(issued.cause) === issued.origin &&
      issued.origin.profile === 'business3' &&
      ['business3', 'bootstrap3', 'startup3'].includes(issued.origin.provenance) &&
      issued.origin.value.retryable === false
    )
  }
  /** A fresh receiver owns this whole background attempt. No old ALS delivery,
   * receipt or client is adopted. Only a fully matched success is consumed;
   * the selected alias, principal and restored view have separate holdings.
   */
  runMainlineRecovery(
    token: object,
    current: () => boolean,
    work: (
      client: MainlineProjectTransport,
      request: (method: string, params: Record<string, unknown>) => Promise<unknown>,
    ) => Promise<BridgeResult<TaskView>>,
    publish: (view: TaskView) => void,
  ): Promise<BridgeResult<TaskView>> {
    const principal = this.#mainlineRecoveryPrincipals.get(token)
    if (!principal || principal.retired || principal.released || principal.active >= 16)
      return this.#operation(async () => {
        throw deniedOrdinary()
      })
    // Count the original attempt before #operation can queue anything. Retiring
    // during ensure, a pending wire, or a timeout cannot release this principal.
    principal.active++
    let attemptActive = true
    const operation = this.#operation(async () => {
      try {
        return await this.#mainlineAsync.exit(async () => {
          const check = () => {
            if (
              !attemptActive ||
              principal.retired ||
              principal.released ||
              !principal.project ||
              !principal.session ||
              this.#stopped ||
              typeof current !== 'function' ||
              !principal.current?.() ||
              !current()
            )
              throw deniedOrdinary()
          }
          check()
          if (typeof work !== 'function' || typeof publish !== 'function') throw deniedOrdinary()
          const receiver = this.mainlineReplyReceiver()
          let offered: { value: BridgeResult<TaskView>; receipt: MainlineReplyReceipt } | undefined
          try {
            offered = await receiver.receive(async () => {
              check()
              const client = this.mainlineProjectClient(),
                record = client && this.#mainlineRecords.get(client),
                open = client && this.#mainlineRecoveryOpen.get(client)
              if (!client || !record || !open || record === principal.origin) throw deniedOrdinary()
              // This is a real project.open in the new authentic stdio session.
              // The private transport checks before actual write and reply select.
              if (!principal.project) throw deniedOrdinary()
              const opening = open(principal.project.projectId, check)
              this.#mainlineRecoveryOperations.add(opening)
              await opening
              check()
              const session = this.#mainlineReady(record)
              if (session === principal.session) throw deniedOrdinary()
              const budget = this.#mainlineBudget(record)
              const request = (
                method: string,
                params: Record<string, unknown>,
              ): Promise<unknown> => {
                if (!attemptActive || principal.retired || principal.active >= 16)
                  return this.#operation(async () => {
                    throw deniedOrdinary()
                  })
                // Also cover a real readonly consumer that can outlive its
                // caller's wait. Its true finally, not the outer timeout, closes
                // this reference to the original principal.
                principal.active++
                const reading = this.#operation(async () => {
                  try {
                    check()
                    if (
                      this.#mainlineReady(record) !== session ||
                      ![
                        'project.get',
                        'job.get',
                        'job.subscribe',
                        'job.unsubscribe',
                        'operation.get',
                      ].includes(method) ||
                      !principal.project ||
                      params.projectId !== principal.project.projectId
                    )
                      throw deniedOrdinary()
                    const finish = budget.beginConsumerRequest()
                    try {
                      budget.beforeArguments(params)
                      const frame = Math.min(262144, session.hello!.limits.maxFrameBytes)
                      budget.reserve(
                        'mainline recovery frame',
                        32 * frame,
                        frame + 1024,
                        32 * frame,
                      )
                      const value = await this.#send(
                        session,
                        method,
                        params,
                        Math.min(this.#requestMs, session.hello!.limits.requestMs),
                        'request',
                        false,
                        undefined,
                        undefined,
                        undefined,
                        record,
                        check,
                      )
                      check()
                      if (this.#mainlineReady(record) !== session) throw deniedOrdinary()
                      return value
                    } finally {
                      finish()
                    }
                  } finally {
                    this.#endMainlineRecovery(token, principal)
                  }
                })
                this.#mainlineRecoveryOperations.add(reading)
                return reading
              }
              const result = await work(client, request)
              check()
              if (result.ok) {
                const project = result.data.project
                if (
                  !project ||
                  !principal.project ||
                  project.projectId !== principal.project.projectId ||
                  project.projectRevision < principal.project.projectRevision ||
                  !validateBusiness3('result_project.get', project) ||
                  this.#mainlineProjects.get(project)?.record !== record ||
                  this.#mainlineProjects.get(project)?.session !== session
                )
                  throw invalidStateOrdinary()
                let entry = this.#mainlineRecoveryViews.get(record)
                if (!entry) {
                  entry = Object.freeze({})
                  this.#mainlineRecoveryViews.set(record, entry)
                }
                // TaskService keeps this exact restored view after delivery closes.
                // It is not freed by consume, a source fence or a new owner.
                budget.retainHolding(entry, result.data)
                budget.handoff(result.data)
              }
              return result
            })
            check()
            if (offered.value.ok) {
              receiver.consume(offered.receipt)
              check()
              publish(offered.value.data)
              check()
            }
            return offered.value
          } catch (cause) {
            if (offered) {
              const delivery = this.#mainlineReceipts.get(offered.receipt)
              if (delivery) this.#unknownDelivery(delivery)
            }
            throw cause
          }
        })
      } finally {
        // This is the real end of the original asynchronous attempt, not the
        // outer TaskService timeout/cancellation. Other UNKNOWN/delivery/cache
        // responsibilities are untouched. Cleanup must not mask its first cause.
        attemptActive = false
        this.#endMainlineRecovery(token, principal)
      }
    })
    this.#mainlineRecoveryOperations.add(operation)
    return operation
  }
  queryReadBudget(owner: object): QueryMainReadBudget {
    const mainline = [...this.#mainlineRecords.values()].find((record) => record.owner === owner)
    if (mainline) return this.#mainlineBudget(mainline)
    const grant = this.#options.ordinaryLibrary
    const record = [...this.#ordinaryRecords.values()].find(
      (r) => r.sourceOwner === owner && r.session && this.#current(r.session),
    )
    if (!grant || !record || !grant.authority.allows(this)) throw deniedOrdinary()
    const budget = grant.authority.queryReadScope(this, owner)
    if (
      !(budget instanceof QueryMainReadBudget) ||
      !record.session ||
      !this.#current(record.session)
    )
      throw deniedOrdinary()
    return budget
  }
  issueQueryPin(
    owner: object,
    engineSessionId: string,
    guard: () => boolean,
    binding?: Readonly<Record<string, unknown>>,
  ): object {
    const mainline = [...this.#mainlineRecords.values()].find((record) => record.owner === owner)
    if (mainline) {
      const session = this.#mainlineReady(mainline)
      if (session.hello!.engineSessionId !== engineSessionId || !mainline.selected)
        throw deniedOrdinary()
      const token = Object.freeze({})
      this.#queryPins.set(token, {
        owner,
        session,
        guard,
        binding: binding ? Object.freeze({ ...binding }) : undefined,
        writeEntered: false,
      })
      this.#checkQueryPin(token, session)
      return token
    }
    const record = [...this.#ordinaryRecords.values()].find(
      (r) => r.sourceOwner === owner && r.session?.hello?.engineSessionId === engineSessionId,
    )
    if (!record?.session || !this.#current(record.session)) throw deniedOrdinary()
    const token = Object.freeze({})
    this.#queryPins.set(token, {
      owner,
      session: record.session,
      guard,
      binding: binding ? Object.freeze({ ...binding }) : undefined,
      writeEntered: false,
    })
    this.#checkQueryPin(token, record.session)
    return token
  }
  #checkQueryPin(token: object, session: Session): void {
    const pin = this.#queryPins.get(token),
      grant = this.#options.ordinaryLibrary
    const mainline =
      pin && [...this.#mainlineRecords.values()].find((record) => record.owner === pin.owner)
    if (mainline) {
      if (
        pin!.session !== session ||
        this.#mainlineReady(mainline) !== session ||
        !pin!.guard() ||
        !this.#current(session)
      )
        throw deniedOrdinary()
      return
    }
    if (
      !pin ||
      pin.session !== session ||
      !this.#current(session) ||
      !grant ||
      !grant.authority.allows(this)
    )
      throw deniedOrdinary()
    if (!pin.guard() || !this.#current(session) || pin.session !== session) throw deniedOrdinary()
  }
  queryWriteEntered(token: object): boolean {
    return this.#queryPins.get(token)?.writeEntered === true
  }
  querySessionIdentity(token: object): Readonly<{
    engineSessionId: string
    registryHash: string
    limits: Record<string, number>
    engineVersion: string
  }> {
    const pin = this.#queryPins.get(token)
    if (!pin) throw deniedOrdinary()
    this.#checkQueryPin(token, pin.session)
    const hello = pin.session.hello!
    return Object.freeze({
      engineSessionId: hello.engineSessionId,
      registryHash: hello.registryHash,
      limits: Object.freeze({ ...hello.limits }),
      engineVersion: hello.engineVersion,
    })
  }
  requestPinned(method: string, params: Record<string, unknown>, pin: object): Promise<unknown> {
    return this.#operation(async () => {
      const issued = this.#queryPins.get(pin)
      if (!issued) throw deniedOrdinary()
      this.#checkQueryPin(pin, issued.session)
      const session = await this.#ensure()
      this.#checkQueryPin(pin, session)
      const mainlineRecord = [...this.#mainlineRecords.values()].find(
        (record) => record.owner === issued.owner,
      )
      const mainline = !!mainlineRecord
      if (mainlineRecord) {
        if (!session.hello!.capabilities.includes(method)) throw deniedOrdinary()
        const project =
          params.projectId ?? (params.binding as Record<string, unknown> | undefined)?.projectId
        if (project !== mainlineRecord.selected?.projectId) throw deniedOrdinary()
      }
      if (
        ![
          'job.create',
          'query.definition.load',
          'query.execution.prepare',
          'query.result.describe',
          'query.result.textPage',
          'query.result.rowsPage',
        ].includes(method) &&
        !(
          mainline &&
          ['changeset.preview', 'changeset.diff.page', 'changeset.confirm', 'job.get'].includes(
            method,
          )
        )
      )
        throw deniedOrdinary()
      return this.#send(
        session,
        method,
        params,
        Math.min(this.#requestMs, session.hello!.limits.requestMs),
        'request',
        false,
        undefined,
        pin,
      )
    })
  }
  requestQueryProjectGet(
    params: Record<string, unknown>,
    pin: object,
    ticket: QueryProjectReadTicket,
    binding: Readonly<Record<string, unknown>>,
  ): Promise<unknown> {
    return this.#operation(async () => {
      if (!(ticket instanceof QueryProjectReadTicket)) throw deniedOrdinary()
      const issued = this.#queryPins.get(pin)
      if (!issued) throw deniedOrdinary()
      this.#checkQueryPin(pin, issued.session)
      const session = await this.#ensure()
      this.#checkQueryPin(pin, session)
      const mainline = [...this.#mainlineRecords.values()].find(
        (record) => record.owner === issued.owner,
      )
      if (mainline && !session.hello!.capabilities.includes('project.get')) throw deniedOrdinary()
      if (
        !issued.binding ||
        Object.keys(binding).length !== Object.keys(issued.binding).length ||
        Object.keys(binding).some((key) => binding[key] !== issued.binding![key]) ||
        params.projectId !== binding.projectId ||
        session.hello!.engineSessionId !== binding.engineSessionId
      )
        throw deniedOrdinary()
      return this.#send(
        session,
        'project.get',
        params,
        Math.min(this.#requestMs, session.hello!.limits.requestMs),
        'request',
        false,
        undefined,
        pin,
        { ticket, binding },
      )
    })
  }
  ordinaryLibraryClient(): OrdinaryLibraryTransport | null {
    const grant = this.#options.ordinaryLibrary
    const authorized = () =>
      this.#profile === 'legacy2' &&
      !this.#options.testMode &&
      !!grant &&
      validateV2('id', grant.ownerId) &&
      OrdinaryLibraryAuthority.owns(grant.authority) &&
      grant.authority.allows(this) === true
    if (!authorized() || !grant) return null
    const ownerId = grant.ownerId
    const previous = this.#ordinaryClient && this.#ordinaryRecords.get(this.#ordinaryClient)
    const current = this.#session
    if (this.#ordinaryClient && previous) {
      // Only an actual new ready Session can issue a successor. Never repin old ports.
      if (!current?.hello || !this.#current(current) || previous.session === current)
        return this.#ordinaryClient
      if (!previous.session && !previous.attempted) {
        previous.session = current
        return this.#ordinaryClient
      }
    }
    const [clientAccount, sourceAccount] = this.#ordinaryRetention.pair()
    const record: OrdinaryClientRecord = {
      attempted: false,
      clientAccount,
      sourceAccount,
      session: current?.hello && this.#current(current) ? current : undefined,
      menuSeq: 0,
      choices: new Map(),
      actions: new Map(),
    }
    this.#ordinaryClient = new (class extends OrdinaryLibraryTransport {
      readonly ownerId = ownerId
      constructor(readonly supervisor: EngineSupervisor) {
        super()
      }
      claimSource(owner: object): OrdinaryRetentionAccount {
        if (record.sourceOwner && record.sourceOwner !== owner) throw invalidStateOrdinary()
        record.sourceOwner = owner
        return record.sourceAccount
      }
      get engineSessionId(): string | undefined {
        return record.session?.hello?.engineSessionId
      }
      observe(listener: (state: EngineConnectionState) => void): () => void {
        return this.supervisor.onConnectionState(listener)
      }
      request(params: Record<string, unknown>): Promise<unknown> {
        return this.supervisor.#operation(async () => {
          if (
            !authorized() ||
            !validateV2('params_ordinary.library', params) ||
            params.ownerId !== grant.ownerId
          )
            throw deniedOrdinary()
          const op = params.op
          // Only the initial choices request may start a child. Every later request,
          // especially lost-ACK release, remains pinned to this original Session.
          if (!record.session) {
            if (op !== 'choices') throw deniedOrdinary()
            if (!record.attempted) {
              record.attempted = true
              record.starting = this.supervisor.#ensure(record)
            }
            if (!record.starting) throw deniedOrdinary()
            const started = await record.starting
            if (record.session !== started) throw exited()
          }
          const session = record.session
          if (
            !authorized() ||
            !this.supervisor.#current(session) ||
            !session.hello?.capabilities.includes('ordinary.library')
          )
            throw deniedOrdinary()
          let binding: OrdinaryResponseBinding | undefined
          const seq = Number(params.actionSeq)
          let action = record.actions.get(seq)
          if (op === 'choices') {
            if (Number(params.menuSeq) < record.menuSeq) throw deniedOrdinary()
          } else if (op === 'acquire') {
            const projectId = record.choices.get(String(params.choiceRef))
            if (!projectId) throw deniedOrdinary()
            if (action && (action.actionId !== params.actionId || action.projectId !== projectId))
              throw invalid()
            if (!action) {
              if (record.actions.size >= 3) throw invalidStateOrdinary()
              const held = [...record.actions.values()]
              record.clientAccount.reserve(
                4096 +
                  record.choices.size * 1024 +
                  2048 +
                  held.reduce(
                    (n, a) =>
                      n +
                      (a.project
                        ? Buffer.byteLength(JSON.stringify(a.project), 'utf8') * 4 + 2048
                        : 2048),
                    0,
                  ),
                32 +
                  record.choices.size * 16 +
                  32 +
                  held.reduce(
                    (n, a) =>
                      n +
                      32 +
                      (a.project
                        ? 3 * Object.keys(a.project.dependencyVector as object).length
                        : 0),
                    0,
                  ),
              )
              action = { actionId: String(params.actionId), projectId }
              record.actions.set(seq, action)
            }
            binding = { projectId }
          } else if (op === 'commit') {
            if (
              !action ||
              action.actionId !== params.actionId ||
              !action.project ||
              action.leaseRef !== params.leaseRef
            )
              throw deniedOrdinary()
            binding = { projectId: action.projectId, project: action.project }
          } else if (action && action.actionId !== params.actionId) throw invalidStateOrdinary()
          // No await between this identity fence and the actual original-session send.
          if (!authorized() || !this.supervisor.#current(session)) throw deniedOrdinary()
          const data = await this.supervisor.#send(
            session,
            'ordinary.library',
            params,
            Math.min(this.supervisor.#requestMs, session.hello!.limits.requestMs),
            'request',
            false,
            binding,
          )
          if (!this.supervisor.#current(session)) throw exited()
          const result = data as Record<string, unknown>
          if (op === 'choices') {
            if (Number(params.menuSeq) >= record.menuSeq) {
              const rows = result.choices as Array<{ choiceRef: string; projectId: string }>
              const bytes =
                4096 +
                rows.length * 1024 +
                [...record.actions.values()].reduce(
                  (n, a) =>
                    n +
                    (a.project
                      ? Buffer.byteLength(JSON.stringify(a.project), 'utf8') * 4 + 2048
                      : 2048),
                  0,
                )
              const objects =
                32 +
                rows.length * 16 +
                [...record.actions.values()].reduce(
                  (n, a) =>
                    n +
                    32 +
                    (a.project ? 3 * Object.keys(a.project.dependencyVector as object).length : 0),
                  0,
                )
              // New menu storage overlaps the old issued menu during replacement.
              record.clientAccount.reserve(
                bytes + record.choices.size * 1024,
                objects + record.choices.size * 16,
              )
              record.menuSeq = Number(params.menuSeq)
              record.choices = new Map(
                (result.choices as Array<{ choiceRef: string; projectId: string }>).map(
                  (choice) => [choice.choiceRef, choice.projectId],
                ),
              )
            }
          } else if (op === 'acquire' && action) {
            const project = result.project as Record<string, unknown>
            const retained = Buffer.byteLength(JSON.stringify(project), 'utf8') * 4 + 2048
            const others = [...record.actions.values()].filter((a) => a !== action)
            const total =
              retained +
              others.reduce(
                (n, a) =>
                  n +
                  (a.project
                    ? Buffer.byteLength(JSON.stringify(a.project), 'utf8') * 4 + 2048
                    : 2048),
                0,
              )
            const objects =
              128 +
              [...others, { ...action, project }].reduce(
                (n, a) =>
                  n +
                  32 +
                  (a.project ? 3 * Object.keys(a.project.dependencyVector as object).length : 0),
                0,
              )
            // Reserve this complete client holding before saving project/leaseRef.
            // The same book includes all active and retired owner accounts.
            record.clientAccount.reserve(
              4096 + total + record.choices.size * 1024,
              objects + record.choices.size * 16,
            )
            action.project = project
            action.leaseRef = String(result.leaseRef)
          } else if (op === 'release') record.actions.delete(seq)
          return data
        })
      }
    })(this)
    this.#ordinaryRecords.set(this.#ordinaryClient, record)
    return this.#ordinaryClient
  }
  get engineSessionId(): string | undefined {
    return this.#session?.hello?.engineSessionId
  }
  onNotification(listener: (event: unknown) => void): () => void {
    this.#listeners.add(listener)
    return () => this.#listeners.delete(listener)
  }
  /** Events only: callers subscribe before starting a connection. No automatic replay. */
  onConnectionState(listener: (state: EngineConnectionState) => void): () => void {
    this.#connectionListeners.add(listener)
    return () => this.#connectionListeners.delete(listener)
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
    // A session fence only; the launch ledger stays open across generations.
    this.#ledger?.recordFence(session.generation, error.error.code, session.anomalies)
    if (!session.hello) session.startupCause = error
    session.terminal = true
    for (const delivery of this.#mainlineDeliveries)
      if (delivery.session === session) this.#unknownDelivery(delivery)
    session.reader.stop()
    session.rejectStart(error)
    clearTimeout(session.startupTimer)
    clearTimeout(session.heartbeat)
    for (const pending of session.pending.values()) {
      clearTimeout(pending.timer)
      if (pending.mainlineOwner) pending.mainlineOwner.uncertain = true
      pending.reject(error)
    }
    session.pending.clear()
    if (this.#session === session) {
      this.#session = undefined
      this.#failures++
      this.#retryAt = Date.now() + Math.min(2000, 100 * 2 ** Math.min(this.#failures - 1, 5))
    }
    if (this.#liveChildren.has(session)) {
      const killTimer = setTimeout(() => {
        if (session.child.exitCode === null && session.child.signalCode === null) {
          try {
            session.child.kill('SIGKILL')
          } catch {
            /* Close remains unproven. */
          }
        }
      }, 1000)
      killTimer.unref()
      session.child.once('close', () => clearTimeout(killTimer))
      // Install the close listener before kill: tests and already-exiting children
      // can close synchronously; an exit code alone never proves stdio closure.
      try {
        session.child.kill()
      } catch {
        /* Close remains unproven. */
      }
    }
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
    this.#stopped = true
    this.#generation++
    for (const child of this.#liveChildren) this.#finish(child, exited())
    this.#listeners.clear()
    this.#connectionListeners.clear()
    // Requests sealing; a complete footer still needs all children closed and
    // all queued writes to succeed. No waiting is performed here.
    this.#ledger?.requestStop()
  }
  /** Main-process switch fence. Existing replies may settle; new business writes cannot enter. */
  freezeAdmission(): void {
    if (this.#stopped) throw exited()
    this.#admissionFrozen = true
  }
  unfreezeAdmission(): void {
    if (!this.#stopped) this.#admissionFrozen = false
  }
  get hasUnresolvedResponsibility(): boolean {
    return this.#hasUnresolvedResponsibility()
  }
  /** The management apply computation is not its own prior unacknowledged reply. */
  get hasOtherMainlineResponsibility(): boolean {
    return this.#hasUnresolvedResponsibility(this.#mainlineAsync.getStore())
  }
  #hasUnresolvedResponsibility(excludeDelivery?: MainlineDelivery): boolean {
    if (this.#starting) return true
    for (const session of this.#liveChildren)
      for (const pending of session.pending.values())
        if (!['session.ping', 'project.library.status'].includes(String(pending.request.method)))
          return true
    for (const record of this.#mainlineRecords.values())
      if (record.uncertain || [...record.tickets].some((ticket) => !ticket.terminal)) return true
    for (const delivery of this.#mainlineDeliveries) if (delivery !== excludeDelivery) return true
    for (const record of this.#ordinaryRecords.values())
      if (record.starting || record.actions.size > 0) return true
    return false
  }
  /** Independent all-library evidence; never uses selected-project TaskService cache. */
  async libraryStatus(): Promise<{ libraryEvidenceRef: string; activeJobs: number }> {
    if (this.profile !== 'business3') throw deniedOrdinary()
    const value = await this.request('project.library.status', {})
    if (!validateBusiness3('result_project.library.status', value)) throw invalid()
    return value as { libraryEvidenceRef: string; activeJobs: number }
  }
  /** A resolved barrier proves every spawned child closed, including retired/startup generations. */
  async stopAndWait(timeoutMs = 5000): Promise<void> {
    const duration = bounded(timeoutMs, 5000, 60000)
    this.stop()
    let timer: ReturnType<typeof setTimeout> | undefined
    try {
      await Promise.race([
        (async () => {
          // A start delayed by retry backoff sees #stopped before it can spawn.
          await this.#starting?.catch(() => {})
          await Promise.all([...this.#liveChildren].map((session) => session.closed))
          if (this.#liveChildren.size !== 0) throw invalidStateOrdinary()
        })(),
        new Promise<never>((_resolve, reject) => {
          timer = setTimeout(() => reject(timeout('shutdown')), duration)
        }),
      ])
    } finally {
      clearTimeout(timer)
    }
  }
  async #ensure(ordinary?: OrdinaryClientRecord): Promise<Session> {
    if (this.#stopped) throw exited()
    if (this.#session && this.#current(this.#session) && ordinary && !ordinary.session)
      ordinary.session = this.#session
    if (this.#session?.hello && this.#current(this.#session)) return this.#session
    if (ordinary && !ordinary.session) this.#ordinaryStartingRecords.add(ordinary)
    if (this.#starting) return this.#starting
    this.#starting = this.#start().finally(() => {
      this.#starting = undefined
      this.#ordinaryStartingRecords.clear()
    })
    return this.#starting
  }
  async #start(): Promise<Session> {
    const delay = this.#retryAt - Date.now()
    if (delay > 0) await new Promise<void>((resolveDelay) => setTimeout(resolveDelay, delay))
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
          parseStrictJson(new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes)),
        ) !== JSON.stringify(v2Registry)
      )
        throw invalid()
      registryHash = createHash('sha256').update(bytes).digest('hex')
    } catch {
      throw exited()
    }
    const selected = this.#options.command ?? getEngineCommand(this.#location, this.#options)
    const command = selected.command
    const args = [...selected.args]
    if (this.profile === 'business3') {
      const database = this.#options.dataPath
      if (database && !isAbsolute(database)) throw invalid()
      args.push('--t01-internal-profile=business3')
      if (this.#options.exampleRoot !== undefined)
        args.push(`--t11-internal-example-root=${this.#options.exampleRoot}`)
      if (this.#options.libraryFileIdentity) {
        const { dev, ino } = this.#options.libraryFileIdentity
        if (!/^\d+$/.test(dev) || !/^\d+$/.test(ino) || !database) throw invalid()
        args.push(`--b1-library-file-identity=${dev}:${ino}`)
      }
      if (this.#options.libraryRequireExisting) {
        if (!this.#options.libraryFileIdentity) throw invalid()
        args.push('--b1-library-require-existing=1')
      }
      if (database)
        args.push(
          `--t01-internal-backup=${join(dirname(database), `.t01-backup-${randomUUID()}.sqlite`)}`,
        )
    }
    const env = getEngineEnvironment(process.env, this.#options)
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
    let resolveClosed!: () => void
    const closed = new Promise<void>((resolve) => {
      resolveClosed = resolve
    })
    let resolveStart!: (session: Session) => void
    let rejectStart!: (error: EngineError) => void
    const startupPromise = new Promise<Session>((resolve, reject) => {
      resolveStart = resolve
      rejectStart = reject
    })
    const session: Session = {
      child,
      closed,
      resolveClosed,
      profile: this.profile,
      startupPromise,
      resolveStart,
      rejectStart,
      generation: ++this.#generation,
      pending: new Map(),
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
    this.#liveChildren.add(session)
    this.#session = session
    this.#ledger?.recordSessionStart(session.generation, child.pid ?? null)
    for (const record of this.#ordinaryStartingRecords) {
      if (!record.session) record.session = session
    }
    child.stdout.on('data', (chunk: Buffer) => {
      if (this.#current(session)) session.reader.push(chunk)
    })
    child.stdout.once('end', () => {
      session.reader.end()
      this.#finish(session, exited())
    })
    child.stderr.on('data', (chunk: Buffer) => {
      if (!this.#current(session) || session.stderrBytes >= 16384) return
      // Store neither raw bytes nor lines. A single bounded fixed event is sufficient.
      if (session.stderrBytes === 0) this.#diagnostic('stderrDiscarded')
      session.stderrBytes = Math.min(16384, session.stderrBytes + chunk.byteLength)
    })
    child.stdin.on('error', () => this.#finish(session, exited()))
    const fail = (error: EngineError): void => this.#finish(session, error)
    session.startupTimer = setTimeout(() => fail(timeout('startup')), this.#startupMs)
    child.once('error', () => fail(exited()))
    // The actual close releases process ownership; settlement and ledger still
    // execute in the same event turn before the awaiting barrier can continue.
    child.once('close', (code, signal) => {
      this.#liveChildren.delete(session)
      session.resolveClosed()
      fail(exited())
      this.#ledger?.recordChildClosed(session.generation, code, signal)
    })
    child.once('spawn', () => {
      if (!this.#current(session)) {
        fail(exited())
        return
      }
      void this.#send(
        session,
        'hello',
        { supportedVersions: [session.profile === 'business3' ? 3 : 2], clientId: randomUUID() },
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
    })
    return startupPromise
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
      // After original validation and session match, before listener delivery.
      this.#ledger?.recordNotification(session.generation, event)
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
      !pending ||
      !(
        incompatible3 ||
        (session.profile === 'business3'
          ? matchesBusiness3Response(pending.request, value, session.expectedRegistryHash)
          : pending.request.method === 'ordinary.library'
            ? matchesOrdinaryResponse(pending.request, value, pending.ordinaryBinding)
            : matchesResponse(pending.request, value))
      )
    ) {
      this.#diagnostic('unmatchedResponse')
      if (
        session.profile === 'business3' ||
        pending?.request.method === 'ordinary.library' ||
        ++session.anomalies >= 3
      )
        this.#finish(session, invalid())
      return
    }
    // Apply the negotiated byte budget synchronously, including a following frame
    // in this same stdout chunk. Never wait for a promise microtask to enforce it.
    if (response.ok && pending.request.method === 'hello') {
      const hello = response.result as Hello
      if (
        hello.registryHash !== session.expectedRegistryHash ||
        (hello.capabilities.includes('ordinary.library') && !this.ordinaryLibraryClient())
      ) {
        this.#finish(session, invalid())
        return
      }
      session.reader.restrictLimit(hello.limits.maxFrameBytes)
      session.hello = hello
      this.#ledger?.recordHello(session.generation, hello)
      this.#connectionState(session, {
        state: 'ready',
        generation: session.generation,
        engineSessionId: hello.engineSessionId,
      })
    }
    const deliveryWire = pending.delivery?.wires.get(String(response.id))
    if (deliveryWire && deliveryWire.session === session) deliveryWire.terminal = true
    if (pending.mainlineRead) {
      const ticket = this.#mainlineTickets.get(pending.mainlineRead)
      if (ticket && ticket.state.requestId === response.id && ticket.record.session === session)
        ticket.state.terminal = true
    }
    if (
      response.ok &&
      pending.request.method === 'project.get' &&
      session.profile === 'business3'
    ) {
      const project = response.result as ProjectView
      Object.freeze(project.dependencyVector)
      Object.freeze(project)
      for (const record of this.#mainlineRecords.values())
        if (record.session === session && record.selected?.projectId === project.projectId) {
          this.#mainlineProjects.set(project, { record, session })
        }
    }
    clearTimeout(pending.timer)
    session.pending.delete(String(response.id))
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
    // After original settlement: method comes from the matched pending request.
    this.#ledger?.recordResponse(
      session.generation,
      pending.request,
      response.ok === true,
      payloadByteLength,
      response.ok ? response.result : undefined,
    )
  }
  #send(
    session: Session,
    method: string,
    params: Record<string, unknown>,
    duration: number,
    phase: string,
    reservedControl = false,
    ordinaryBinding?: OrdinaryResponseBinding,
    queryPin?: object,
    queryRead?: { ticket: QueryProjectReadTicket; binding: Readonly<Record<string, unknown>> },
    mainlineOwner?: MainlineOwnerRecord,
    recoveryCurrent?: () => void,
  ): Promise<unknown> {
    if (
      this.#admissionFrozen &&
      !['hello', 'session.ping', 'project.library.status'].includes(method)
    )
      return Promise.reject(invalidStateOrdinary())
    if (!this.#current(session)) {
      this.#ledger?.recordRequestRejected('notCurrent', method)
      return Promise.reject(exited())
    }
    if (!mainlineOwner && queryPin) {
      const owner = this.#queryPins.get(queryPin)?.owner
      mainlineOwner = [...this.#mainlineRecords.values()].find((record) => record.owner === owner)
    }
    let delivery: MainlineDelivery | undefined
    if (mainlineOwner) {
      delivery = this.#mainlineAsync.getStore() ?? mainlineOwner.activeDelivery
      if (!delivery) delivery = this.#newDelivery(true)
      if (
        !this.#mainlineDeliveries.has(delivery) ||
        !['COMPUTING', 'ORPHAN'].includes(delivery.state)
      ) {
        this.#ledger?.recordRequestRejected('deliveryState', method)
        return Promise.reject(invalidStateOrdinary())
      }
      try {
        this.#bindDelivery(delivery, mainlineOwner)
        if (delivery.wires.size >= 128) throw invalidStateOrdinary()
        this.#deliveryReserve(delivery, 512, 8, 2097152)
      } catch (cause) {
        this.#ledger?.recordRequestRejected('deliveryState', method)
        return Promise.reject(cause)
      }
    }
    if (session.pending.size >= this.#maxPending + (reservedControl ? 1 : 0)) {
      this.#ledger?.recordRequestRejected('queueFull', method)
      return Promise.reject(
        new EngineError({
          code: 'QUEUE_FULL',
          messageKey: 'job.queueFull',
          params: { retryAfterMs: 100 },
          retryable: true,
        }),
      )
    }
    const request = {
      kind: 'request',
      id: randomUUID(),
      protocolVersion: method === 'hello' ? 2 : session.profile === 'business3' ? 3 : 2,
      engineSessionId: method === 'hello' ? null : session.hello?.engineSessionId,
      method,
      params,
    }
    if (!this.#validate(session, 'request', request)) {
      this.#ledger?.recordRequestRejected('validation', method)
      return Promise.reject(this.#sign(session, invalid()))
    }
    const encoded = Buffer.from(JSON.stringify(request) + '\n', 'utf8')
    if (encoded.length - 1 > (session.hello?.limits.maxFrameBytes ?? 262144)) {
      this.#ledger?.recordRequestRejected('frameLimit', method)
      return Promise.reject(
        new EngineError({
          code: 'RESOURCE_LIMIT',
          messageKey: 'resource.limitExceeded',
          params: { resource: 'frame' },
          retryable: false,
        }),
      )
    }
    return new Promise((resolveRequest, rejectRequest) => {
      const timer = setTimeout(() => {
        if (mainlineOwner) mainlineOwner.uncertain = true
        if (delivery) this.#unknownDelivery(delivery)
        session.pending.delete(request.id)
        rejectRequest(this.#sign(session, timeout(phase)))
        this.#ledger?.recordRequestTimeout(session.generation, request.id)
      }, duration)
      session.pending.set(request.id, {
        request: parseStrictJson(encoded.subarray(0, -1).toString('utf8')) as Record<
          string,
          unknown
        >,
        ordinaryBinding,
        mainlineOwner,
        delivery,
        resolve: resolveRequest,
        reject: rejectRequest,
        timer,
      })
      if (delivery) delivery.wires.set(request.id, { session, terminal: false })
      // Reads the already-registered strict clone only; never re-reads params.
      // Stays before the recovery-pin guard: no observer between pin and write.
      this.#ledger?.recordRequestPrepared(
        session.generation,
        session.pending.get(request.id)?.request,
        method,
        phase,
        encoded.length - 1,
      )
      try {
        if (queryRead) {
          if (!queryPin) throw deniedOrdinary()
          const issued = this.#queryPins.get(queryPin)
          if (!issued) throw deniedOrdinary()
          queryRead.ticket.attachDispatch(
            Object.freeze({
              requestId: request.id,
              sessionId: session.hello!.engineSessionId,
              child: session.child,
              owner: issued.owner,
              binding: queryRead.binding,
              params: Object.freeze({ ...params }),
            }),
          )
          const mainline = this.#mainlineTickets.get(queryRead.ticket)
          if (mainline) {
            if (
              mainline.record.owner !== issued.owner ||
              mainline.record.session !== session ||
              mainline.state.requestId !== request.id
            )
              throw deniedOrdinary()
            session.pending.get(request.id)!.mainlineRead = queryRead.ticket
          }
        }
        if (queryPin) this.#checkQueryPin(queryPin, session)
        // Only a private mainline recovery open/read supplies this guard. No
        // asynchronous work or observer callback may follow it before write.
        recoveryCurrent?.()
      } catch (cause) {
        clearTimeout(timer)
        session.pending.delete(request.id)
        const wire = delivery?.wires.get(request.id)
        if (wire) wire.terminal = true // Original pin failed before any stdin.write.
        rejectRequest(cause)
        this.#ledger?.recordRequestRejected('pinGuard', method)
        return
      }
      // Final pin check returned; only private bookkeeping precedes write, with no user callback.
      if (queryPin) this.#queryPins.get(queryPin)!.writeEntered = true
      try {
        session.child.stdin.write(encoded, (error) => {
          if (error) this.#finish(session, exited())
          this.#ledger?.recordWriteSettled(request.id, error != null)
        })
      } catch (cause) {
        clearTimeout(timer)
        session.pending.delete(request.id)
        if (mainlineOwner) mainlineOwner.uncertain = true
        if (delivery) this.#unknownDelivery(delivery)
        rejectRequest(cause)
        this.#finish(session, exited())
        this.#ledger?.recordWriteThrown(request.id)
      }
    })
  }
  request(method: string, params: Record<string, unknown>): Promise<unknown> {
    return this.#operation(async () => {
      if (method === 'ordinary.library') throw deniedOrdinary()
      if (method === 'hello')
        throw new EngineError({
          code: 'INVALID_STATE',
          messageKey: 'protocol.invalidState',
          params: {},
          retryable: false,
        })
      const session = await this.#ensure()
      return this.#send(
        session,
        method,
        params,
        Math.min(this.#requestMs, session.hello!.limits.requestMs),
        'request',
      )
    })
  }
  health(): Promise<EngineHealth> {
    return this.#operation(async () => {
      const session = await this.#ensure()
      const value = (await this.#send(
        session,
        'health',
        {},
        Math.min(this.#requestMs, session.hello!.limits.requestMs),
        'request',
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
