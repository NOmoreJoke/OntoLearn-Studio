import { randomUUID } from 'node:crypto'
import {
  accessSync,
  closeSync,
  constants,
  fstatSync,
  fsyncSync,
  lstatSync,
  mkdirSync,
  openSync,
  readSync,
  readdirSync,
  realpathSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { basename, dirname, isAbsolute, join, resolve } from 'node:path'
import { z } from 'zod'
import { parseStrictJson } from './jsonl'
import {
  safeBusiness3Error,
  type BridgeResult,
  type LibraryLocationChoice,
  type LibraryLocationView,
  type LibraryWorkspaceReport,
  type MainlineLibraryStatusDTO,
} from '@ontolearn/contracts'

const identitySchema = z
  .object({ dev: z.string().regex(/^\d+$/), ino: z.string().regex(/^\d+$/) })
  .strict()
const locatorSchema = z
  .object({
    path: z.string().min(1).max(4096).refine(isAbsolute),
    parent: identitySchema,
    file: identitySchema.nullable(),
  })
  .strict()
const configSchema = z
  .object({
    version: z.literal(1),
    active: locatorSchema,
    libraryId: z.string().min(1).max(256).nullable(),
    pending: z
      .object({
        phase: z.enum(['prepared', 'closed']),
        target: locatorSchema,
        intent: z.enum(['create', 'open']),
      })
      .strict()
      .nullable(),
  })
  .strict()
type Identity = z.infer<typeof identitySchema>
export type LibraryLocator = z.infer<typeof locatorSchema>
type Config = z.infer<typeof configSchema>
const reportSchema = z
  .object({
    documentNonce: z.string().uuid(),
    generation: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER),
    dirty: z.boolean(),
    unresolved: z.boolean(),
  })
  .strict()
const switchSchema = z
  .object({
    choiceRef: z.string().uuid(),
    documentNonce: z.string().uuid(),
    workspaceGeneration: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER),
  })
  .strict()
function invalid(): Error {
  return new Error('LIBRARY_LOCATION_INVALID')
}
function failure<T>(): BridgeResult<T> {
  return {
    ok: false,
    error: safeBusiness3Error({
      code: 'INVALID_STATE',
      messageKey: 'protocol.invalidState',
      params: {},
      retryable: false,
    }),
  }
}
function identity(path: string, directory: boolean): Identity {
  const value = lstatSync(path, { bigint: true })
  if (
    value.isSymbolicLink() ||
    (directory ? !value.isDirectory() : !value.isFile()) ||
    (!directory && value.nlink !== 1n)
  )
    throw invalid()
  return { dev: String(value.dev), ino: String(value.ino) }
}
function equal(a: Identity, b: Identity): boolean {
  return a.dev === b.dev && a.ino === b.ino
}
function canonical(path: string): string {
  if (!isAbsolute(path) || path.length > 4096 || path.includes('\0')) throw invalid()
  const absolute = resolve(path),
    real = realpathSync(absolute)
  // Windows normalizes drive/case; other platforms must match exactly. This rejects aliases.
  if (
    process.platform === 'win32' ? real.toLowerCase() !== absolute.toLowerCase() : real !== absolute
  )
    throw invalid()
  return real
}
function existing(path: string): LibraryLocator {
  const normalized = canonical(path)
  accessSync(normalized, constants.R_OK | constants.W_OK)
  accessSync(dirname(normalized), constants.R_OK | constants.W_OK | constants.X_OK)
  return {
    path: normalized,
    parent: identity(dirname(normalized), true),
    file: identity(normalized, false),
  }
}
function absent(path: string): LibraryLocator {
  const parent = canonical(dirname(path)),
    target = join(parent, basename(path))
  accessSync(parent, constants.R_OK | constants.W_OK | constants.X_OK)
  try {
    lstatSync(target)
    throw invalid()
  } catch (cause) {
    if ((cause as NodeJS.ErrnoException).code !== 'ENOENT') throw cause
  }
  return { path: target, parent: identity(parent, true), file: null }
}
function requireSqliteHeader(value: LibraryLocator): void {
  verifyLibraryLocator(value)
  if (!value.file) throw invalid()
  const fd = openSync(value.path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0))
  try {
    const opened = fstatSync(fd, { bigint: true })
    if (
      !opened.isFile() ||
      String(opened.dev) !== value.file.dev ||
      String(opened.ino) !== value.file.ino
    )
      throw invalid()
    const header = Buffer.alloc(16)
    if (
      readSync(fd, header, 0, header.length, 0) !== 16 ||
      header.toString('binary') !== 'SQLite format 3\0'
    )
      throw invalid()
  } finally {
    closeSync(fd)
  }
}
/** Check again immediately before handing the main-only path to the engine. */
export function verifyLibraryLocator(value: LibraryLocator): void {
  const parent = canonical(dirname(value.path))
  if (!equal(value.parent, identity(parent, true))) throw invalid()
  if (value.file) {
    if (canonical(value.path) !== value.path || !equal(value.file, identity(value.path, false)))
      throw invalid()
  } else {
    absent(value.path)
  }
}

/** Small application config journal. It never opens, copies, or rewrites SQLite content. */
export class LibraryLocationConfig {
  #value: Config
  constructor(
    readonly configPath: string,
    readonly defaultDataPath: string,
  ) {
    if (!isAbsolute(configPath) || !isAbsolute(defaultDataPath)) throw invalid()
    mkdirSync(dirname(configPath), { recursive: true, mode: 0o700 })
    canonical(dirname(configPath))
    let bytes: Buffer
    try {
      const info = lstatSync(configPath, { bigint: true })
      if (!info.isFile() || info.isSymbolicLink() || info.size > 65536n) throw invalid()
      const fd = openSync(configPath, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0))
      try {
        const opened = fstatSync(fd, { bigint: true })
        if (
          !opened.isFile() ||
          opened.dev !== info.dev ||
          opened.ino !== info.ino ||
          opened.size > 65536n
        )
          throw invalid()
        const bounded = Buffer.alloc(65537)
        let used = 0
        while (used < bounded.length) {
          const count = readSync(fd, bounded, used, bounded.length - used, null)
          if (count === 0) break
          used += count
        }
        if (used > 65536) throw invalid()
        bytes = bounded.subarray(0, used)
      } finally {
        closeSync(fd)
      }
    } catch (cause) {
      if ((cause as NodeJS.ErrnoException).code !== 'ENOENT') throw cause
      let active: LibraryLocator
      try {
        active = existing(defaultDataPath)
      } catch (missing) {
        if ((missing as NodeJS.ErrnoException).code !== 'ENOENT') throw missing
        active = absent(defaultDataPath)
      }
      this.#value = { version: 1, active, libraryId: null, pending: null }
      return
    }
    this.#value = configSchema.parse(
      parseStrictJson(new TextDecoder('utf-8', { fatal: true }).decode(bytes)),
    )
  }
  get pending(): boolean {
    return this.#value.pending !== null
  }
  get needsRecovery(): boolean {
    return this.#value.pending?.phase === 'prepared'
  }
  get active(): LibraryLocator {
    return structuredClone(this.#value.active)
  }
  get libraryId(): string | null {
    return this.#value.libraryId
  }
  get startupTarget(): LibraryLocator {
    if (this.needsRecovery) throw invalid()
    return structuredClone(this.#value.pending?.target ?? this.#value.active)
  }
  #save(next: Config): void {
    const validated = configSchema.parse(next),
      bytes = JSON.stringify(validated)
    if (Buffer.byteLength(bytes) > 65536) throw invalid()
    // Never follow a replaced config/parent symlink.
    canonical(dirname(this.configPath))
    try {
      const info = lstatSync(this.configPath)
      if (!info.isFile() || info.isSymbolicLink()) throw invalid()
    } catch (cause) {
      if ((cause as NodeJS.ErrnoException).code !== 'ENOENT') throw cause
    }
    const temporary = this.configPath + '.' + randomUUID() + '.tmp'
    const fd = openSync(temporary, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL, 0o600)
    try {
      writeFileSync(fd, bytes, 'utf8')
      fsyncSync(fd)
    } finally {
      closeSync(fd)
    }
    try {
      renameSync(temporary, this.configPath)
      // Rename may have committed even if directory fsync subsequently fails.
      // Keep the in-memory phase conservative in that uncertain durability case.
      this.#value = validated
      // Directory fsync is supported on POSIX. Windows rename is still atomic.
      if (process.platform !== 'win32') {
        const directory = openSync(dirname(this.configPath), constants.O_RDONLY)
        try {
          fsyncSync(directory)
        } finally {
          closeSync(directory)
        }
      }
    } finally {
      try {
        unlinkSync(temporary)
      } catch {
        // A leftover private temporary file is never read as the active config.
      }
    }
  }
  prepare(target: LibraryLocator, intent: 'create' | 'open'): void {
    if (this.pending) throw invalid()
    verifyLibraryLocator(this.#value.active)
    verifyLibraryLocator(target)
    this.#save({ ...this.#value, pending: { phase: 'prepared', target, intent } })
  }
  markClosed(): void {
    if (this.#value.pending?.phase !== 'prepared') throw invalid()
    this.#save({ ...this.#value, pending: { ...this.#value.pending, phase: 'closed' } })
  }
  /** Explicit native recovery only; never selected as an automatic startup fallback. */
  restoreOriginal(): void {
    verifyLibraryLocator(this.#value.active)
    this.#save({ ...this.#value, pending: null })
  }
  prepareStartupFile(): LibraryLocator & { initialize: boolean } {
    let target = this.startupTarget
    let initialize = false
    verifyLibraryLocator(target)
    if (target.file) requireSqliteHeader(target)
    if (!target.file) {
      // Reserve exclusively; a raced-in file is rejected, never opened as a new library.
      const fd = openSync(
        target.path,
        constants.O_RDWR | constants.O_CREAT | constants.O_EXCL,
        0o600,
      )
      try {
        fsyncSync(fd)
      } finally {
        closeSync(fd)
      }
      target = existing(target.path)
      initialize = true
      this.#save(
        this.#value.pending
          ? { ...this.#value, pending: { ...this.#value.pending, target } }
          : { ...this.#value, active: target },
      )
    }
    return { ...target, initialize }
  }
  completeStartup(libraryId: string): void {
    const active = this.startupTarget
    verifyLibraryLocator(active)
    this.#save({ version: 1, active, libraryId, pending: null })
  }
}

export interface LibraryLocationDependencies {
  /** create selects an empty directory; open selects an existing SQLite library file. */
  pick(intent: 'create' | 'open'): Promise<string | null>
  hasUnresolvedResponsibility(): boolean
  status(): Promise<MainlineLibraryStatusDTO>
  freezeAdmission(): void
  unfreezeAdmission(): void
  stopAndWait(): Promise<void>
  relaunch(): void
}
export class LibraryLocationService {
  #switching = false
  #choosing = false
  #choices = new Map<
    string,
    { locator: LibraryLocator; intent: 'create' | 'open'; expires: number }
  >()
  #document?: object
  #report?: LibraryWorkspaceReport
  constructor(
    readonly config: LibraryLocationConfig,
    readonly dependencies: LibraryLocationDependencies,
  ) {}
  get switching(): boolean {
    return this.#switching
  }
  getLocation(): BridgeResult<LibraryLocationView> {
    return {
      ok: true,
      data: {
        label: this.config.active.path,
        libraryId: this.config.libraryId,
        pending: this.config.pending,
      },
    }
  }
  invalidateDocument(document?: object): void {
    if (document && this.#document !== document) return
    this.#report = undefined
    this.#document = undefined
  }
  reportWorkspace(value: LibraryWorkspaceReport, document: object): BridgeResult<null> {
    const parsed = reportSchema.safeParse(value)
    if (!parsed.success || !document || this.#switching) return failure()
    if (
      this.#document === document &&
      this.#report &&
      (parsed.data.documentNonce !== this.#report.documentNonce ||
        parsed.data.generation < this.#report.generation ||
        (parsed.data.generation === this.#report.generation &&
          (parsed.data.dirty !== this.#report.dirty ||
            parsed.data.unresolved !== this.#report.unresolved)))
    )
      return failure()
    this.#document = document
    this.#report = parsed.data
    return { ok: true, data: null }
  }
  async choose(args: {
    intent: 'create' | 'open'
  }): Promise<BridgeResult<LibraryLocationChoice | null>> {
    if (
      this.#switching ||
      this.#choosing ||
      !z
        .object({ intent: z.enum(['create', 'open']) })
        .strict()
        .safeParse(args).success
    )
      return failure()
    this.#choosing = true
    try {
      const selected = await this.dependencies.pick(args.intent)
      if (selected === null) return { ok: true, data: null }
      let locator: LibraryLocator
      if (args.intent === 'create') {
        const directory = canonical(selected)
        identity(directory, true)
        if (readdirSync(directory).length !== 0) throw invalid()
        locator = absent(join(directory, 'engine.sqlite'))
      } else {
        locator = existing(selected)
        requireSqliteHeader(locator)
      }
      const active = this.config.active
      if (
        locator.path === active.path ||
        (locator.file && active.file && equal(locator.file, active.file))
      )
        throw invalid()
      this.#choices.clear()
      const choiceRef = randomUUID()
      this.#choices.set(choiceRef, { locator, intent: args.intent, expires: Date.now() + 300000 })
      return { ok: true, data: { choiceRef, label: locator.path, intent: args.intent } }
    } catch {
      return failure()
    } finally {
      this.#choosing = false
    }
  }
  async switchLocation(
    args: { choiceRef: string; documentNonce: string; workspaceGeneration: number },
    document: object,
  ): Promise<BridgeResult<{ restartRequested: true }>> {
    if (!switchSchema.safeParse(args).success || this.#switching || this.#choosing) return failure()
    const choice = this.#choices.get(args.choiceRef)
    const clean = () =>
      this.#document === document &&
      this.#report?.documentNonce === args.documentNonce &&
      this.#report.generation === args.workspaceGeneration &&
      !this.#report.dirty &&
      !this.#report.unresolved
    if (
      !choice ||
      choice.expires < Date.now() ||
      !clean() ||
      this.dependencies.hasUnresolvedResponsibility()
    )
      return failure()
    this.#switching = true
    let prepared = false
    try {
      this.dependencies.freezeAdmission()
      const status = await this.dependencies.status()
      if (
        status.libraryEvidenceRef !== this.config.libraryId ||
        status.activeJobs !== 0 ||
        !clean() ||
        this.dependencies.hasUnresolvedResponsibility()
      )
        throw invalid()
      verifyLibraryLocator(choice.locator)
      if (choice.intent === 'open') requireSqliteHeader(choice.locator)
      if (choice.intent === 'create' && readdirSync(dirname(choice.locator.path)).length !== 0)
        throw invalid()
      this.config.prepare(choice.locator, choice.intent)
      prepared = true
      await this.dependencies.stopAndWait()
      this.config.markClosed()
      this.#choices.clear()
      // Schedule after the IPC result has a chance to reach the frozen view.
      setTimeout(() => this.dependencies.relaunch(), 50)
      return { ok: true, data: { restartRequested: true } }
    } catch {
      // A prepared close failure remains fenced with the old active selection.
      // The next launch requires explicit recovery. Never launch a second owner.
      if (!prepared && !this.config.pending) {
        this.#switching = false
        this.dependencies.unfreezeAdmission()
      }
      return failure()
    }
  }
}
