// Private T10 preparation; no IPC registration, Store access or native picker invocation.
// The picker adapter must remain in the trusted main process. Never accept a path from
// renderer/package/model input or treat this draft projection as approved source evidence.
import * as fs from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { isAbsolute, join } from 'node:path'
import { z } from 'zod'
import { renderPreparedReport } from '../../renderer/src/transfer/report'

const selectionSchema = z
  .object({ directory: z.string().min(1).max(4096), filename: z.string().min(6).max(180) })
  .strict()

type Selection = z.infer<typeof selectionSchema>
export type MainReportDestinationPicker = () => Promise<Selection | null>
export type ReportFileCheckpoint =
  | 'temporary-created'
  | 'written'
  | 'file-synced'
  | 'before-publication'
  | 'link-completed'
  | 'published'

type Cleanup = 'complete' | 'pending'
type FailureCode =
  | 'REPORT_EXPORT_BUSY'
  | 'REPORT_ALREADY_PUBLISHED'
  | 'REPORT_CLEANUP_PENDING'
  | 'REPORT_PUBLICATION_UNCONFIRMED'
  | 'REPORT_DESTINATION_INVALID'
  | 'REPORT_TARGET_EXISTS'
  | 'REPORT_EXPORT_FAILED'
export type PreparedReportFileReceipt =
  | {
      state: 'published'
      sha256: string
      byteLength: number
      durability: 'confirmed' | 'unconfirmed'
      postPublicationError: boolean
      cleanup: Cleanup
    }
  | { state: 'cancelled'; cleanup: Cleanup }
  | { state: 'failed'; code: FailureCode; cleanup: Cleanup }
  | { state: 'publication-unconfirmed'; sha256: string; byteLength: number; cleanup: Cleanup }

export type FileIdentity = { dev: number; ino: number }
type Staging = {
  root: string
  file: string
  rootIdentity?: FileIdentity
  fileIdentity?: FileIdentity
}
export const sameFile = (a: FileIdentity, b: FileIdentity) => a.dev === b.dev && a.ino === b.ino
export const sameRealPath = (real: string, candidate: string): boolean =>
  process.platform === 'win32' ? real.toLowerCase() === candidate.toLowerCase() : real === candidate
export function errno(error: unknown): unknown {
  try {
    if (error === null || typeof error !== 'object') return undefined
    const descriptor = Object.getOwnPropertyDescriptor(error, 'code')
    return descriptor && 'value' in descriptor ? descriptor.value : undefined
  } catch {
    return undefined
  }
}

export type TransferExtension = '.html' | '.ontolearn.zip'

function safeSelection(value: unknown, extension: TransferExtension): Selection | null {
  const parsed = selectionSchema.safeParse(value)
  if (!parsed.success) return null
  const { directory, filename } = parsed.data
  const stem = filename.slice(0, -extension.length)
  if (
    !isAbsolute(directory) ||
    directory.includes('\0') ||
    !filename.toLowerCase().endsWith(extension) ||
    /[<>:"/\\|?*]/.test(filename) ||
    [...filename].some(
      (character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127,
    ) ||
    !stem.trim() ||
    /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i.test(stem.split('.')[0].trimEnd())
  ) {
    return null
  }
  return parsed.data
}

/** Publishes one immutable artifact in the destination directory using a no-replace link. */
export class PreparedTransferFile {
  #metadata: Readonly<{ sha256: string; byteLength: number }>
  #payload: Buffer
  #phase: 'prepared' | 'busy' | 'published' | 'unconfirmed' = 'prepared'
  #staging?: Staging
  #handle?: fs.FileHandle
  #unconfirmed?: { destination: string; identity: FileIdentity }
  #cleanupFlight?: Promise<Cleanup>

  constructor(
    payload: Buffer,
    private readonly extension: TransferExtension,
    private readonly destinationDirectory?: FileIdentity,
  ) {
    this.#payload = Buffer.from(payload)
    this.#metadata = Object.freeze({
      sha256: createHash('sha256').update(this.#payload).digest('hex'),
      byteLength: this.#payload.byteLength,
    })
    Object.freeze(this)
  }

  get metadata(): Readonly<{ sha256: string; byteLength: number }> {
    return this.#metadata
  }

  async #verifyStagedBytes(): Promise<void> {
    const staging = this.#staging
    const handle = this.#handle
    if (!staging?.fileIdentity || !handle) throw new Error('STAGING_MISSING')
    const opened = await handle.stat()
    if (
      !opened.isFile() ||
      !sameFile(opened, staging.fileIdentity) ||
      opened.size !== this.#payload.length
    )
      throw new Error('STAGING_CHANGED')
    const buffer = Buffer.alloc(this.#payload.length + 1)
    let read = 0
    while (read < buffer.length) {
      const chunk = await handle.read(buffer, read, buffer.length - read, read)
      if (!chunk.bytesRead) break
      read += chunk.bytesRead
    }
    if (read !== this.#payload.length || !buffer.subarray(0, read).equals(this.#payload)) {
      throw new Error('STAGING_CHANGED')
    }
    const path = await fs.lstat(staging.file)
    if (!path.isFile() || !sameFile(path, staging.fileIdentity)) throw new Error('STAGING_CHANGED')
  }

  async #cleanup(): Promise<Cleanup> {
    try {
      if (this.#handle) {
        await this.#handle.close()
        this.#handle = undefined
      }
      const staging = this.#staging
      if (!staging) return 'complete'
      let root
      try {
        root = await fs.lstat(staging.root)
      } catch (error) {
        if (errno(error) !== 'ENOENT') return 'pending'
        this.#staging = undefined
        return 'complete'
      }
      if (!root.isDirectory() || !staging.rootIdentity || !sameFile(root, staging.rootIdentity)) {
        return 'pending'
      }
      try {
        const file = await fs.lstat(staging.file)
        if (!file.isFile() || !staging.fileIdentity || !sameFile(file, staging.fileIdentity)) {
          return 'pending'
        }
        await fs.unlink(staging.file)
      } catch (error) {
        if (errno(error) !== 'ENOENT') return 'pending'
      }
      // Never recursively delete. An unexpected file keeps cleanup pending and is preserved.
      await fs.rmdir(staging.root)
      this.#staging = undefined
      return 'complete'
    } catch {
      return 'pending'
    }
  }

  async retryCleanup(): Promise<Cleanup> {
    if (this.#phase === 'busy') return 'pending'
    if (this.#cleanupFlight) return this.#cleanupFlight
    const flight = this.#cleanup()
    this.#cleanupFlight = flight
    try {
      return await flight
    } finally {
      if (this.#cleanupFlight === flight) this.#cleanupFlight = undefined
    }
  }

  #cleanupStatus(): Cleanup {
    return this.#staging || this.#handle ? 'pending' : 'complete'
  }

  get pendingPublication(): FileIdentity | undefined {
    return this.#unconfirmed?.identity
  }

  async reconcilePublication(): Promise<'published' | 'not-present' | 'unconfirmed'> {
    if (this.#phase === 'published') return 'published'
    if (this.#phase !== 'unconfirmed' || !this.#unconfirmed) return 'unconfirmed'
    const pending = this.#unconfirmed
    const current = () =>
      this.#phase === 'published' ? ('published' as const) : ('unconfirmed' as const)
    try {
      const target = await fs.lstat(pending.destination)
      if (this.#unconfirmed !== pending) return current()
      if (target.isFile() && sameFile(target, pending.identity)) {
        this.#phase = 'published'
        this.#unconfirmed = undefined
        return 'published'
      }
      // It is not our artifact at this path; never alter that file.
      this.#phase = 'prepared'
      this.#unconfirmed = undefined
      return 'not-present'
    } catch (error) {
      if (this.#unconfirmed !== pending) return current()
      if (errno(error) !== 'ENOENT') return 'unconfirmed'
      this.#phase = 'prepared'
      this.#unconfirmed = undefined
      return 'not-present'
    }
  }

  async save(
    pickDestination: MainReportDestinationPicker,
    options: {
      signal?: AbortSignal
      canPublish?: () => boolean
      // In-process fault injection only; never expose this hook through the bridge.
      checkpoint?: (phase: ReportFileCheckpoint) => void | Promise<void>
    } = {},
  ): Promise<PreparedReportFileReceipt> {
    if (this.#phase === 'busy') {
      return { state: 'failed', code: 'REPORT_EXPORT_BUSY', cleanup: this.#cleanupStatus() }
    }
    if (this.#phase === 'published') {
      return { state: 'failed', code: 'REPORT_ALREADY_PUBLISHED', cleanup: this.#cleanupStatus() }
    }
    if (this.#phase === 'unconfirmed') {
      return {
        state: 'failed',
        code: 'REPORT_PUBLICATION_UNCONFIRMED',
        cleanup: this.#cleanupStatus(),
      }
    }
    if (this.#staging) {
      return { state: 'failed', code: 'REPORT_CLEANUP_PENDING', cleanup: 'pending' }
    }
    this.#phase = 'busy'
    let outcome: 'cancelled' | 'failed' | 'published' = 'cancelled'
    let code: FailureCode = 'REPORT_EXPORT_FAILED'
    let destination: string | undefined
    let parent: string | undefined
    let published = false
    let linkReturned = false
    let linkAttempted = false
    let unconfirmed = false
    let postPublicationError = false
    let durability: 'confirmed' | 'unconfirmed' = 'unconfirmed'
    const checkpoint = options.checkpoint ?? (() => {})
    try {
      if (!options.signal?.aborted) {
        const selected = await pickDestination()
        if (selected !== null && !options.signal?.aborted) {
          const selection = safeSelection(selected, this.extension)
          if (!selection) {
            code = 'REPORT_DESTINATION_INVALID'
            outcome = 'failed'
          } else {
            parent = await fs.realpath(selection.directory)
            const directory = await fs.lstat(parent)
            if (
              !directory.isDirectory() ||
              (this.destinationDirectory &&
                (!sameRealPath(parent, selection.directory) ||
                  !sameFile(directory, this.destinationDirectory)))
            ) {
              code = 'REPORT_DESTINATION_INVALID'
              outcome = 'failed'
            } else {
              destination = join(parent, selection.filename)
              const prefix =
                this.extension === '.html' ? '.ontolearn-report-' : '.ontolearn-package-'
              const root = await fs.mkdtemp(join(parent, prefix))
              this.#staging = {
                root,
                file: join(
                  root,
                  this.extension === '.html' ? 'report.html' : 'package.ontolearn.zip',
                ),
              }
              this.#staging.rootIdentity = await fs.lstat(root)
              this.#handle = await fs.open(this.#staging.file, 'wx+', 0o600)
              this.#staging.fileIdentity = await this.#handle.stat()
              await checkpoint('temporary-created')
              await this.#handle.writeFile(this.#payload, { signal: options.signal })
              await checkpoint('written')
              await this.#handle.sync()
              await checkpoint('file-synced')
              await checkpoint('before-publication')
              if (!options.signal?.aborted) {
                await this.#verifyStagedBytes()
                if (this.destinationDirectory) {
                  const latest = await fs.lstat(parent)
                  if (!latest.isDirectory() || !sameFile(latest, this.destinationDirectory)) {
                    code = 'REPORT_DESTINATION_INVALID'
                    outcome = 'failed'
                  } else {
                    try {
                      const target = await fs.lstat(destination)
                      code = target.isSymbolicLink()
                        ? 'REPORT_DESTINATION_INVALID'
                        : 'REPORT_TARGET_EXISTS'
                      outcome = 'failed'
                    } catch (error) {
                      if (errno(error) !== 'ENOENT') throw error
                    }
                  }
                }
              }
              if (
                outcome !== 'failed' &&
                !options.signal?.aborted &&
                (options.canPublish?.() ?? true)
              ) {
                // Same-filesystem hard link is an atomic no-replace publication. Never rename
                // over an existing target or follow a final symlink, even after a chooser race.
                linkAttempted = true
                await fs.link(this.#staging.file, destination)
                linkReturned = true
                if (this.destinationDirectory) {
                  const target = await fs.lstat(destination)
                  if (!target.isFile() || !sameFile(target, this.#staging.fileIdentity))
                    throw new Error('PUBLICATION_CHANGED')
                }
                published = true
                await checkpoint('link-completed')
                await checkpoint('published')
              }
            }
          }
        }
      }
    } catch (error) {
      // Reconcile an ambiguous link response using our own temporary inode, without reading
      // an existing destination's contents or guessing from the error message.
      if (
        !published &&
        linkAttempted &&
        errno(error) !== 'EEXIST' &&
        destination &&
        this.#staging?.fileIdentity
      ) {
        try {
          const target = await fs.lstat(destination)
          published = target.isFile() && sameFile(target, this.#staging.fileIdentity)
        } catch (readError) {
          unconfirmed = errno(readError) !== 'ENOENT'
        }
        if (!published && (linkReturned || unconfirmed)) {
          unconfirmed = true
          this.#unconfirmed = { destination, identity: this.#staging.fileIdentity }
        }
      }
      if (published) postPublicationError = true
      else if (options.signal?.aborted && errno(error) === 'ABORT_ERR') outcome = 'cancelled'
      else {
        outcome = 'failed'
        code = errno(error) === 'EEXIST' ? 'REPORT_TARGET_EXISTS' : 'REPORT_EXPORT_FAILED'
      }
    }
    if (published && parent) {
      outcome = 'published'
      if (process.platform === 'win32') {
        // Directory fsync is supported on POSIX; Windows file flush completed prior to link.
        durability = 'confirmed'
      } else {
        let directoryHandle: fs.FileHandle | undefined
        try {
          directoryHandle = await fs.open(parent, 'r')
          await directoryHandle.sync()
          durability = 'confirmed'
        } catch {
          // File already exists in full. Unsupported/failed directory fsync must not turn it
          // into an ordinary failure or cancellation that invites a duplicate write.
          postPublicationError = true
        } finally {
          try {
            await directoryHandle?.close()
          } catch {
            postPublicationError = true
          }
        }
      }
    }
    const cleanup = await this.#cleanup()
    this.#phase = published ? 'published' : unconfirmed ? 'unconfirmed' : 'prepared'
    if (unconfirmed) return { state: 'publication-unconfirmed', ...this.#metadata, cleanup }
    if (outcome === 'published') {
      return { state: outcome, ...this.#metadata, durability, postPublicationError, cleanup }
    }
    if (outcome === 'failed') return { state: outcome, code, cleanup }
    return { state: 'cancelled', cleanup }
  }
}

/** Render exactly once before opening the native chooser. */
export class PreparedHtmlReportFile extends PreparedTransferFile {
  constructor(projection: unknown) {
    super(Buffer.from(renderPreparedReport(projection), 'utf8'), '.html')
  }
}
