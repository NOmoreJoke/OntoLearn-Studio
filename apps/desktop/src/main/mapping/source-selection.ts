/** Main-process private source authority. No IPC, renderer paths, parsing or Store writes. */
import { createHash, randomUUID } from 'node:crypto'
import { constants } from 'node:fs'
import { open } from 'node:fs/promises'
import { extname, isAbsolute } from 'node:path'

export const MAX_SOURCE_BYTES = 8 * 1024 * 1024
const encodings = ['utf-8', 'utf-8-sig', 'gb18030', 'big5', 'utf-16'] as const
export type CsvEncoding = (typeof encodings)[number]
export type SourceScope = Readonly<{ projectId: string; lifecycleId: string }>
export type SourceOptions = Readonly<{ encoding: CsvEncoding | null; sheet: string | null }>
export type SourceSummary = Readonly<{
  selectionId: string
  projectId: string
  lifecycleId: string
  generation: number
  format: 'csv' | 'xlsx'
  encoding: CsvEncoding | null
  sheet: string | null
  byteLength: number
  sha256: string
}>
/** Object identity is checked. Never serialize/accept this proof from a renderer. */
export type SourceProof = Readonly<{ sourceProof: string }>
export type SourceSnapshot = Readonly<{
  summary: SourceSummary
  bytes: Uint8Array
  proof: SourceProof
}>
/** Main-only bytes for format/sheet inspection; conveys no preview/commit authority. */
export type SourceInspection = Readonly<{ summary: SourceSummary; bytes: Uint8Array }>
export type SourceFailureKind =
  | 'invalid-input'
  | 'invalid-choice'
  | 'picker-failed'
  | 'unsupported-file'
  | 'unavailable'
  | 'limit'
  | 'busy'
  | 'source-changed'
  | 'sheet-required'
  | 'stale-context'
  | 'stale-proof'
  | 'disposed'

/** Internal safe tags only. Canonical owner must map these to the one public error schema. */
export class SourceFailure extends Error {
  constructor(readonly kind: SourceFailureKind) {
    super('Source selection failed')
    this.name = 'SourceFailure'
  }
}

/** Supplied only by the trusted host, never by renderer input or a public callback transport. */
export type TrustedPicker = (signal: AbortSignal) => Promise<string | null>
type Selection = { path: string; summary: SourceSummary }
type Stamp = { selectionId: string; generation: number; scope: SourceScope }

function encodingValid(value: unknown): value is CsvEncoding {
  return typeof value === 'string' && encodings.some((encoding) => encoding === value)
}
function fingerprint(bytes: Uint8Array): string {
  return createHash('sha256').update(bytes).digest('hex')
}
function staleIfAborted(signal: AbortSignal): void {
  if (signal.aborted) throw new SourceFailure('stale-context')
}

export class SourceSelectionBroker {
  private scope: SourceScope | null = null
  private selection: Selection | null = null
  private configuring: number | null = null
  private generation = 0
  private disposed = false
  private proofs = new WeakMap<SourceProof, Stamp>()
  private readonly pending = new Set<AbortController>()
  private readonly maxBytes: number

  constructor(
    private readonly pickFile: TrustedPicker,
    limits: { maxBytes?: number } = {},
  ) {
    const max = limits.maxBytes ?? MAX_SOURCE_BYTES
    if (!Number.isSafeInteger(max) || max < 1 || max > MAX_SOURCE_BYTES) {
      throw new SourceFailure('invalid-input')
    }
    this.maxBytes = max
  }

  openProject(projectId: string): SourceScope {
    if (this.disposed) throw new SourceFailure('disposed')
    if (
      typeof projectId !== 'string' ||
      !projectId.trim() ||
      Buffer.byteLength(projectId, 'utf8') > 512 ||
      [...projectId].some(
        (character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127,
      )
    ) {
      throw new SourceFailure('invalid-input')
    }
    this.scope = null
    const ticket = this.invalidate()
    if (this.disposed) throw new SourceFailure('disposed')
    if (this.generation !== ticket) throw new SourceFailure('stale-context')
    this.scope = Object.freeze({ projectId, lifecycleId: randomUUID() })
    return this.scope
  }

  cancel(scope: SourceScope): void {
    this.assertScope(scope)
    this.invalidate()
  }

  closeProject(scope: SourceScope): void {
    this.assertScope(scope)
    this.scope = null
    this.invalidate()
  }

  dispose(): void {
    this.disposed = true
    this.scope = null
    this.invalidate()
  }

  async pick(
    scope: SourceScope,
    encoding: CsvEncoding = 'utf-8-sig',
  ): Promise<SourceSummary | null> {
    this.assertScope(scope)
    if (!encodingValid(encoding)) throw new SourceFailure('invalid-input')
    const ticket = this.invalidate()
    this.assertTicket(scope, ticket)
    const operation = this.operation()
    try {
      const path = await this.pickFile(operation.signal)
      this.assertTicket(scope, ticket)
      if (path === null) return null // Picker cancellation is not a formal mapping/job outcome.
      if (typeof path !== 'string' || !isAbsolute(path) || path.includes('\0')) {
        throw new SourceFailure('invalid-choice')
      }
      const extension = extname(path).toLowerCase()
      if (extension !== '.csv' && extension !== '.xlsx') {
        throw new SourceFailure('unsupported-file')
      }
      const bytes = await this.readBounded(path, operation.signal)
      this.assertTicket(scope, ticket)
      return this.install(
        scope,
        path,
        extension === '.csv' ? 'csv' : 'xlsx',
        extension === '.csv' ? encoding : null,
        null,
        bytes,
      )
    } catch (error) {
      this.assertTicket(scope, ticket)
      throw error instanceof SourceFailure ? error : new SourceFailure('picker-failed')
    } finally {
      this.pending.delete(operation)
    }
  }

  async configure(
    scope: SourceScope,
    selectionId: string,
    options: SourceOptions,
  ): Promise<SourceSummary> {
    const selected = this.current(scope, selectionId, true)
    if (
      !options ||
      typeof options !== 'object' ||
      Object.keys(options).sort().join(',') !== 'encoding,sheet' ||
      (selected.summary.format === 'csv'
        ? !encodingValid(options.encoding) || options.sheet !== null
        : options.encoding !== null ||
          (options.sheet !== null &&
            (typeof options.sheet !== 'string' ||
              !options.sheet.length ||
              Buffer.byteLength(options.sheet, 'utf8') > 256 ||
              options.sheet.includes('\0'))))
    ) {
      throw new SourceFailure('invalid-input')
    }
    const encoding = options.encoding
    const sheet = options.sheet
    const ticket = this.invalidate()
    this.assertTicket(scope, ticket)
    // Keep the source available for a newer configuration request, but block previews
    // until its latest options have been verified. Old proofs were already revoked.
    this.selection = selected
    this.configuring = ticket
    try {
      const bytes = await this.readVerified(scope, selected)
      this.assertTicket(scope, ticket)
      return this.install(scope, selected.path, selected.summary.format, encoding, sheet, bytes)
    } catch (error) {
      if (this.generation === ticket) this.invalidate()
      throw error
    } finally {
      if (this.configuring === ticket) this.configuring = null
    }
  }

  async readForInspection(scope: SourceScope, selectionId: string): Promise<SourceInspection> {
    const selected = this.current(scope, selectionId)
    const ticket = this.generation
    const bytes = await this.readVerified(scope, selected)
    this.assertTicket(scope, ticket)
    // An XLSX needs this read before selecting a real sheet. No proof is minted.
    return Object.freeze({ summary: selected.summary, bytes: new Uint8Array(bytes) })
  }

  async readForPreview(scope: SourceScope, selectionId: string): Promise<SourceSnapshot> {
    const selected = this.current(scope, selectionId)
    if (selected.summary.format === 'xlsx' && selected.summary.sheet === null) {
      throw new SourceFailure('sheet-required')
    }
    const ticket = this.generation
    const bytes = await this.readVerified(scope, selected)
    this.assertTicket(scope, ticket)
    const proof: SourceProof = Object.freeze({ sourceProof: randomUUID() })
    this.proofs.set(proof, { selectionId, generation: this.generation, scope })
    // Main-only fresh byte copy; never return it or this proof through a renderer bridge.
    return Object.freeze({ summary: selected.summary, bytes: new Uint8Array(bytes), proof })
  }

  async readForCommit(
    scope: SourceScope,
    proof: SourceProof,
  ): Promise<
    Readonly<{
      summary: SourceSummary
      bytes: Uint8Array
    }>
  > {
    this.assertScope(scope)
    if (!proof || typeof proof !== 'object') throw new SourceFailure('stale-proof')
    const stamp = this.proofs.get(proof)
    if (!stamp || stamp.scope !== scope || stamp.generation !== this.generation) {
      throw new SourceFailure('stale-proof')
    }
    const selected = this.current(scope, stamp.selectionId)
    const ticket = this.generation
    const bytes = await this.readVerified(scope, selected)
    this.assertTicket(scope, ticket)
    return Object.freeze({ summary: selected.summary, bytes: new Uint8Array(bytes) })
  }

  private assertScope(scope: SourceScope): void {
    if (this.disposed) throw new SourceFailure('disposed')
    if (!this.scope || scope !== this.scope) throw new SourceFailure('stale-context')
  }

  private assertTicket(scope: SourceScope, generation: number): void {
    this.assertScope(scope)
    if (generation !== this.generation) throw new SourceFailure('stale-context')
  }

  private current(scope: SourceScope, selectionId: string, allowConfiguring = false): Selection {
    this.assertScope(scope)
    if (!this.selection || this.selection.summary.selectionId !== selectionId) {
      throw new SourceFailure('stale-context')
    }
    if (!allowConfiguring && this.configuring !== null) throw new SourceFailure('busy')
    return this.selection
  }

  private operation(): AbortController {
    // Aborted host/FS operations retain their slot until they actually settle.
    if (this.pending.size >= 2) throw new SourceFailure('busy')
    const operation = new AbortController()
    this.pending.add(operation)
    return operation
  }

  private invalidate(): number {
    const previous = [...this.pending]
    this.selection = null
    this.configuring = null
    this.proofs = new WeakMap()
    const ticket = ++this.generation
    // Abort listeners are synchronous and may reenter the host. Invalidate first.
    for (const operation of previous) operation.abort()
    return ticket
  }

  private install(
    scope: SourceScope,
    path: string,
    format: 'csv' | 'xlsx',
    encoding: CsvEncoding | null,
    sheet: string | null,
    bytes: Uint8Array,
  ): SourceSummary {
    const summary: SourceSummary = Object.freeze({
      selectionId: randomUUID(),
      projectId: scope.projectId,
      lifecycleId: scope.lifecycleId,
      generation: this.generation,
      format,
      encoding,
      sheet,
      byteLength: bytes.byteLength,
      sha256: fingerprint(bytes),
    })
    this.selection = { path, summary }
    return summary
  }

  private async readVerified(scope: SourceScope, selected: Selection): Promise<Uint8Array> {
    const ticket = this.generation
    this.assertTicket(scope, ticket)
    const operation = this.operation()
    let bytes: Uint8Array
    try {
      bytes = await this.readBounded(selected.path, operation.signal)
    } catch (error) {
      this.assertTicket(scope, ticket) // A late error must never invalidate the new project/choice.
      this.invalidate()
      throw error instanceof SourceFailure ? error : new SourceFailure('unavailable')
    } finally {
      this.pending.delete(operation)
    }
    this.assertTicket(scope, ticket)
    if (
      bytes.byteLength !== selected.summary.byteLength ||
      fingerprint(bytes) !== selected.summary.sha256
    ) {
      this.invalidate()
      throw new SourceFailure('source-changed')
    }
    return bytes
  }

  private async readBounded(path: string, signal: AbortSignal): Promise<Uint8Array> {
    try {
      // NONBLOCK prevents a selected FIFO/device from hanging before fstat rejects it.
      const handle = await open(path, constants.O_RDONLY | constants.O_NONBLOCK)
      try {
        staleIfAborted(signal)
        const before = await handle.stat({ bigint: true })
        if (!before.isFile()) throw new SourceFailure('unsupported-file')
        if (before.size > BigInt(this.maxBytes)) throw new SourceFailure('limit')
        const buffer = Buffer.allocUnsafe(this.maxBytes + 1)
        let total = 0
        for (;;) {
          staleIfAborted(signal)
          const { bytesRead } = await handle.read(buffer, total, buffer.length - total, null)
          total += bytesRead
          if (total > this.maxBytes) throw new SourceFailure('limit')
          if (!bytesRead) break
        }
        const after = await handle.stat({ bigint: true })
        staleIfAborted(signal)
        if (
          before.size !== after.size ||
          before.mtimeNs !== after.mtimeNs ||
          before.ctimeNs !== after.ctimeNs ||
          BigInt(total) !== after.size
        ) {
          throw new SourceFailure('source-changed')
        }
        return new Uint8Array(buffer.subarray(0, total))
      } finally {
        await handle.close()
      }
    } catch (error) {
      throw error instanceof SourceFailure ? error : new SourceFailure('unavailable')
    }
  }
}
