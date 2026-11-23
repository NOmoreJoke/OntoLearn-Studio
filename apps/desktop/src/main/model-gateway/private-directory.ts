import fs, { type FileHandle } from 'node:fs/promises'
import { constants, type Stats } from 'node:fs'
import path from 'node:path'
import { randomUUID } from 'node:crypto'
import { z } from 'zod'

const absolutePath = z
  .string()
  .min(1)
  .max(4096)
  .refine((value) => path.isAbsolute(value) && !value.includes(String.fromCharCode(0)))
export const privateLocationSchema = z
  .object({ userDataPath: absolutePath, excludedRoots: z.array(absolutePath).min(1).max(128) })
  .strict()
export type PrivateLocation = z.infer<typeof privateLocationSchema>
export type PrivateWritePhase =
  | 'partial-written'
  | 'temp-written'
  | 'file-synced'
  | 'published'
  | 'temp-unlinked'
  | 'directory-synced'
// Fault observation is an internal test seam, never a bridge/request parameter.
export type PrivateWriteObserver = (phase: PrivateWritePhase) => void | Promise<void>
const pendingName = /^\.pending-[1-9][0-9]*-[0-9a-f-]{36}$/
const recordName = /^[0-9a-f-]{36}\.(credential|audit|configuration)$/
const unavailable = () => new Error('PRIVATE_STORAGE_UNAVAILABLE')
const within = (parent: string, child: string) => {
  const relative = path.relative(parent, child)
  return (
    relative === '' ||
    (!path.isAbsolute(relative) && relative !== '..' && !relative.startsWith('..' + path.sep))
  )
}

async function prospectiveRealPath(input: string): Promise<string> {
  let current = path.resolve(input)
  const suffix: string[] = []
  for (;;) {
    try {
      return path.join(await fs.realpath(current), ...suffix)
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT' || path.dirname(current) === current)
        throw unavailable()
      suffix.unshift(path.basename(current))
      current = path.dirname(current)
    }
  }
}

function requireOwned(stats: Stats, mode: number): void {
  if (
    !stats.isDirectory() ||
    stats.isSymbolicLink() ||
    stats.uid !== process.getuid!() ||
    (stats.mode & 0o7777) !== mode
  )
    throw unavailable()
}

async function requireTrustedAncestors(input: string): Promise<void> {
  let current = input
  for (;;) {
    const stats = await fs.lstat(current)
    const rootSticky = stats.uid === 0 && (stats.mode & 0o1000) !== 0
    if (
      !stats.isDirectory() ||
      stats.isSymbolicLink() ||
      ![0, process.getuid!()].includes(stats.uid) ||
      ((stats.mode & 0o022) !== 0 && !rootSticky)
    )
      throw unavailable()
    const parent = path.dirname(current)
    if (parent === current) return
    current = parent
  }
}

async function requireTrustedInput(input: string): Promise<void> {
  let current = path.resolve(input)
  for (;;) {
    try {
      const stats = await fs.lstat(current)
      if (stats.isSymbolicLink()) {
        // Permit only OS-owned aliases such as macOS /tmp -> /private/tmp.
        if (stats.uid !== 0) throw unavailable()
      } else if (
        !stats.isDirectory() ||
        ![0, process.getuid!()].includes(stats.uid) ||
        ((stats.mode & 0o022) !== 0 && !(stats.uid === 0 && (stats.mode & 0o1000) !== 0))
      )
        throw unavailable()
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error
    }
    const parent = path.dirname(current)
    if (parent === current) return
    current = parent
  }
}

async function requireOutside(candidate: string, excludedRoots: readonly string[]): Promise<void> {
  for (const excluded of excludedRoots) {
    const canonical = await prospectiveRealPath(excluded)
    if (within(canonical, candidate) || within(candidate, canonical)) throw unavailable()
  }
}

async function syncDirectory(input: string): Promise<void> {
  const handle = await fs.open(
    input,
    constants.O_RDONLY | constants.O_DIRECTORY | constants.O_NOFOLLOW,
  )
  try {
    await handle.sync()
  } finally {
    await handle.close()
  }
}

async function ensureApplicationDirectory(input: string): Promise<string> {
  let current = input
  const missing: string[] = []
  for (;;) {
    try {
      const existing = await fs.lstat(current)
      if (current === input && (existing.isSymbolicLink() || !existing.isDirectory()))
        throw unavailable()
      break
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error
      missing.unshift(path.basename(current))
      current = path.dirname(current)
    }
  }
  current = await fs.realpath(current)
  await requireTrustedAncestors(current)
  for (const name of missing) {
    const parent = current
    current = path.join(parent, name)
    await fs.mkdir(current, { mode: 0o700 }).catch((error: NodeJS.ErrnoException) => {
      if (error.code !== 'EEXIST') throw error
    })
    requireOwned(await fs.lstat(current), 0o700)
    await syncDirectory(parent)
  }
  // Also reconcile an existing directory created by a previously failed open.
  await syncDirectory(path.dirname(current))
  return current
}

type Anchor = { name: string; handle: FileHandle; dev: number; ino: number; privateMode: boolean }
/** POSIX private application files. Same-UID hostile namespace control is outside this boundary. */
export class PrivateDirectory {
  private closed = false
  private constructor(
    private readonly anchors: Anchor[],
    private readonly location: PrivateLocation,
    private readonly observer?: PrivateWriteObserver,
  ) {}

  static async open(
    input: PrivateLocation,
    bucket: 'credentials' | 'audit' | 'configurations',
    observer?: PrivateWriteObserver,
  ): Promise<PrivateDirectory> {
    const anchors: Anchor[] = []
    try {
      if (!process.getuid || process.platform === 'win32') throw unavailable()
      const parsed = privateLocationSchema.parse(input)
      const original = path.resolve(parsed.userDataPath)
      await requireTrustedInput(original)
      const candidate = path.join(
        await prospectiveRealPath(original),
        'model-gateway-private-v1',
        bucket,
      )
      await requireOutside(candidate, parsed.excludedRoots)
      const userData = await ensureApplicationDirectory(original)
      await requireTrustedInput(original)
      await requireOutside(
        path.join(userData, 'model-gateway-private-v1', bucket),
        parsed.excludedRoots,
      )
      await requireTrustedAncestors(userData)
      const places = [
        userData,
        path.join(userData, 'model-gateway-private-v1'),
        path.join(userData, 'model-gateway-private-v1', bucket),
      ]
      for (let i = 0; i < places.length; i++) {
        if (i > 0)
          await fs.mkdir(places[i], { mode: 0o700 }).catch((error: NodeJS.ErrnoException) => {
            if (error.code !== 'EEXIST') throw error
          })
        const stats = await fs.lstat(places[i])
        if (i > 0) requireOwned(stats, 0o700)
        else if (
          !stats.isDirectory() ||
          stats.isSymbolicLink() ||
          stats.uid !== process.getuid() ||
          (stats.mode & 0o022) !== 0
        )
          throw unavailable()
        const handle = await fs.open(
          places[i],
          constants.O_RDONLY | constants.O_DIRECTORY | constants.O_NOFOLLOW,
        )
        anchors.push({
          name: places[i],
          handle,
          dev: stats.dev,
          ino: stats.ino,
          privateMode: i > 0,
        })
        if (i > 0) await anchors[i - 1].handle.sync()
      }
      const directory = new PrivateDirectory(anchors, parsed, observer)
      await directory.assertSafe()
      return directory
    } catch {
      await Promise.all(anchors.map((anchor) => anchor.handle.close().catch(() => {})))
      throw unavailable()
    }
  }

  private get directory(): Anchor {
    return this.anchors[this.anchors.length - 1]
  }
  private leaf(name: string): string {
    if (!recordName.test(name) && !pendingName.test(name)) throw unavailable()
    return path.join(this.directory.name, name)
  }

  private async names(): Promise<string[]> {
    const names: string[] = []
    const directory = await fs.opendir(this.directory.name)
    for await (const entry of directory) {
      if (names.length >= 11024 || (!recordName.test(entry.name) && !pendingName.test(entry.name)))
        throw unavailable()
      names.push(entry.name)
    }
    return names
  }

  private async assertSafe(): Promise<void> {
    if (this.closed) throw unavailable()
    await requireTrustedInput(this.location.userDataPath)
    if ((await fs.realpath(this.location.userDataPath)) !== this.anchors[0].name)
      throw unavailable()
    await requireOutside(this.directory.name, this.location.excludedRoots)
    await requireTrustedAncestors(this.anchors[0].name)
    for (const anchor of this.anchors) {
      const stats = await fs.lstat(anchor.name)
      const held = await anchor.handle.stat()
      if (
        stats.isSymbolicLink() ||
        !stats.isDirectory() ||
        stats.dev !== anchor.dev ||
        stats.ino !== anchor.ino ||
        held.dev !== stats.dev ||
        held.ino !== stats.ino ||
        held.uid !== process.getuid!()
      )
        throw unavailable()
      if (anchor.privateMode) requireOwned(stats, 0o700)
      else if (stats.uid !== process.getuid!() || (stats.mode & 0o022) !== 0) throw unavailable()
    }
  }

  async list(): Promise<string[]> {
    try {
      await this.assertSafe()
      const names = await this.names()
      await this.assertSafe()
      // Never remove pending files: another process may still own its live write.
      return names.filter((name) => !pendingName.test(name)).sort()
    } catch {
      throw unavailable()
    }
  }

  async read(name: string, maxBytes: number): Promise<Buffer> {
    let handle: FileHandle | undefined
    try {
      if (!Number.isSafeInteger(maxBytes) || maxBytes < 1 || maxBytes > 128 * 1024)
        throw unavailable()
      await this.assertSafe()
      handle = await fs.open(
        this.leaf(name),
        constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK,
      )
      const before = await handle.stat()
      if (
        !before.isFile() ||
        before.uid !== process.getuid!() ||
        (before.mode & 0o7777) !== 0o600 ||
        before.dev !== this.directory.dev ||
        before.size > maxBytes ||
        before.nlink < 1 ||
        before.nlink > 2
      )
        throw unavailable()
      if (before.nlink === 2) {
        // A crash between publication and temp unlink can leave these exact two names.
        const names = await this.names()
        let matched = false
        for (const candidate of names.filter((entry) => pendingName.test(entry))) {
          try {
            const stats = await fs.lstat(this.leaf(candidate))
            if (
              stats.isFile() &&
              !stats.isSymbolicLink() &&
              stats.dev === before.dev &&
              stats.ino === before.ino
            )
              matched = true
          } catch (error) {
            if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error
          }
        }
        if (!matched && (await handle.stat()).nlink !== 1) throw unavailable()
      }
      const buffer = Buffer.alloc(maxBytes + 1)
      let offset = 0
      while (offset < buffer.length) {
        const result = await handle.read(buffer, offset, buffer.length - offset, offset)
        if (result.bytesRead === 0) break
        offset += result.bytesRead
      }
      const after = await handle.stat()
      const named = await fs.lstat(this.leaf(name))
      if (
        offset > maxBytes ||
        offset !== before.size ||
        after.size !== before.size ||
        after.mtimeMs !== before.mtimeMs ||
        named.isSymbolicLink() ||
        named.dev !== before.dev ||
        named.ino !== before.ino
      )
        throw unavailable()
      await this.assertSafe()
      return Buffer.from(buffer.subarray(0, offset))
    } catch {
      throw unavailable()
    } finally {
      await handle?.close().catch(() => {})
    }
  }

  async publish(name: string, bytes: Buffer): Promise<void> {
    let temporary: string | undefined
    let handle: FileHandle | undefined
    try {
      if (
        !recordName.test(name) ||
        !Buffer.isBuffer(bytes) ||
        bytes.length === 0 ||
        bytes.length > 128 * 1024
      )
        throw unavailable()
      const snapshot = Buffer.from(bytes)
      await this.assertSafe()
      temporary = `.pending-${process.pid}-${randomUUID()}`
      handle = await fs.open(
        this.leaf(temporary),
        constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW,
        0o600,
      )
      const created = await handle.stat()
      if (
        !created.isFile() ||
        created.uid !== process.getuid!() ||
        (created.mode & 0o7777) !== 0o600
      )
        throw unavailable()
      const middle = Math.max(1, Math.floor(snapshot.length / 2))
      await handle.writeFile(snapshot.subarray(0, middle))
      await this.observer?.('partial-written')
      await handle.writeFile(snapshot.subarray(middle))
      await this.observer?.('temp-written')
      await handle.sync()
      await this.observer?.('file-synced')
      await handle.close()
      handle = undefined
      await this.assertSafe()
      try {
        await fs.link(this.leaf(temporary), this.leaf(name))
      } catch (error) {
        if (
          (error as NodeJS.ErrnoException).code !== 'EEXIST' ||
          !(await this.read(name, 128 * 1024)).equals(snapshot)
        )
          throw unavailable()
      }
      await this.observer?.('published')
      await this.assertSafe()
      await fs.unlink(this.leaf(temporary))
      temporary = undefined
      await this.observer?.('temp-unlinked')
      await this.directory.handle.sync()
      await this.observer?.('directory-synced')
      await this.assertSafe()
    } catch {
      throw unavailable()
    } finally {
      await handle?.close().catch(() => {})
      // A possibly published final record is never deleted on failure.
      if (temporary) {
        try {
          await this.assertSafe()
          await fs.unlink(this.leaf(temporary))
        } catch {
          /* preserve if the namespace is no longer trusted */
        }
      }
    }
  }

  async close(): Promise<void> {
    if (this.closed) return
    this.closed = true
    await Promise.all(this.anchors.map((anchor) => anchor.handle.close()))
  }
}

export class PrivateOperations {
  private closed = false
  private readonly pending = new Set<Promise<unknown>>()
  private closing?: Promise<void>
  run<T>(action: () => Promise<T>): Promise<T> {
    if (this.closed || this.pending.size >= 32) return Promise.reject(unavailable())
    const operation = Promise.resolve().then(action)
    this.pending.add(operation)
    void operation.finally(() => this.pending.delete(operation)).catch(() => {})
    return operation
  }
  close(action: () => Promise<void>): Promise<void> {
    if (this.closing) return this.closing
    this.closed = true
    this.closing = Promise.allSettled([...this.pending]).then(action)
    return this.closing
  }
}
