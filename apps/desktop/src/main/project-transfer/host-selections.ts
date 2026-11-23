import { createHash, randomUUID } from 'node:crypto'
import { constants } from 'node:fs'
import * as fs from 'node:fs/promises'
import { basename, dirname, isAbsolute, join, normalize } from 'node:path'
import type {
  MappingEncoding,
  TransferPickerPurpose,
  TransferPublicationReceiptDTO,
} from '@ontolearn/contracts'
import {
  errno,
  PreparedTransferFile,
  sameFile,
  sameRealPath,
  type FileIdentity,
  type TransferExtension,
} from './prepared-report-file'

type Purpose = 'mapping-source' | TransferPickerPurpose
export type PickerResult = { canceled: true } | { filePath: string }
export type SelectionBinding = {
  projectId: string
  owner: object
  engineSessionId: string
  epoch: number
}

type InputFile =
  | { purpose: 'mapping-source'; extension: '.csv' | '.xlsx'; format: 'csv' | 'xlsx' }
  | { purpose: 'package-import'; extension: '.ontolearn.zip'; format: 'zip' }
type OutputFile = {
  purpose: 'package-export' | 'report-html'
  extension: TransferExtension
  outputFile: 'output.html' | 'output.ontolearn.zip'
  destinationPath: string
  destinationDirectory: FileIdentity
}
type SelectionDirectory = { root: FileIdentity; path: string; identity: FileIdentity }
type SelectionRecord = SelectionBinding &
  (InputFile | OutputFile) & {
    selectionId: string
    directory: SelectionDirectory
    controller: AbortController
    active: number
    exclusive: boolean
    mappingOptions?: { sheet: string; encoding: MappingEncoding | null }
    cleanup?: Promise<Cleanup>
  }
type Cleanup = TransferPublicationReceiptDTO['cleanup']
type FileDigest = { sha256: string; byteLength: number }

const mappingLimit = 8 * 1024 * 1024 // Engine mapping/source.py
const archiveLimit = 40 * 1024 * 1024 // Engine transfer/inspection.py and W4 publication schema
const selectionPattern = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/
const validId = (id: unknown): id is string =>
  typeof id === 'string' && selectionPattern.test(id) && !id.includes('..')
const matches = (record: SelectionBinding, binding: SelectionBinding) =>
  record.projectId === binding.projectId &&
  record.owner === binding.owner &&
  record.engineSessionId === binding.engineSessionId &&
  record.epoch === binding.epoch

function digest(bytes: Buffer): FileDigest {
  return { sha256: createHash('sha256').update(bytes).digest('hex'), byteLength: bytes.length }
}

function rejectSelection(): never {
  throw new Error('HOST_SELECTION_DENIED')
}

async function directoryAt(path: string): Promise<FileIdentity> {
  const stat = await fs.lstat(path)
  if (!stat.isDirectory()) rejectSelection()
  return { dev: stat.dev, ino: stat.ino }
}

async function regularBytes(path: string, maxBytes: number): Promise<Buffer> {
  const entry = await fs.lstat(path)
  if (!entry.isFile() || entry.size > maxBytes) rejectSelection()
  const file = await fs.open(
    path,
    constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0),
  )
  try {
    const opened = await file.stat()
    if (!opened.isFile() || !sameFile(entry, opened) || opened.size > maxBytes) rejectSelection()
    const bytes = Buffer.alloc(opened.size + 1)
    let offset = 0
    while (offset < bytes.length) {
      const { bytesRead } = await file.read(bytes, offset, bytes.length - offset, offset)
      if (!bytesRead) break
      offset += bytesRead
    }
    const final = await file.stat()
    const current = await fs.lstat(path)
    if (
      offset !== opened.size ||
      final.mtimeMs !== opened.mtimeMs ||
      final.ctimeMs !== opened.ctimeMs ||
      !current.isFile() ||
      !sameFile(opened, current)
    )
      rejectSelection()
    return bytes.subarray(0, offset)
  } finally {
    await file.close()
  }
}

async function atomicPrivateWrite(directory: string, name: string, data: Buffer | string) {
  const temp = join(directory, '.tmp-' + randomUUID())
  const file = await fs.open(temp, 'wx', 0o600)
  try {
    await file.writeFile(data)
    await file.sync()
  } finally {
    await file.close()
  }
  await fs.rename(temp, join(directory, name))
}

export class HostSelections {
  readonly #records = new Map<string, SelectionRecord>()
  readonly #retired = new Set<SelectionRecord>()
  readonly #uncertain = new Map<string, { record: SelectionRecord; identity: FileIdentity }>()

  constructor(private readonly root: string | undefined) {}

  get available(): boolean {
    return this.root !== undefined
  }

  async stage(
    purpose: Purpose,
    filePath: string,
    binding: SelectionBinding,
    current: () => boolean,
  ) {
    const root = this.root
    if (!root || !isAbsolute(filePath) || normalize(filePath) !== filePath || !current())
      rejectSelection()

    const selected = await this.#file(purpose, filePath, binding)
    if (!current() || this.#records.size + this.#retired.size + this.#uncertain.size >= 32)
      rejectSelection()

    try {
      await fs.mkdir(root, { mode: 0o700 })
    } catch (error) {
      if (errno(error) !== 'EEXIST') throw error
    }
    const rootIdentity = await directoryAt(root)
    const selectionId = randomUUID()
    const path = join(root, selectionId)
    await fs.mkdir(path, { mode: 0o700 })
    const directory = { root: rootIdentity, path, identity: await directoryAt(path) }
    const record: SelectionRecord = {
      ...binding,
      ...selected,
      selectionId,
      directory,
      controller: new AbortController(),
      active: 1,
      exclusive: false,
    }
    this.#retired.add(record)
    try {
      const meta = {
        version: 1,
        selectionId,
        projectId: binding.projectId,
        engineSessionId: binding.engineSessionId,
        purpose: record.purpose,
      }
      const createdAt = new Date().toISOString()
      let metadata: object
      if ('format' in record) {
        const bytes = await regularBytes(
          filePath,
          record.purpose === 'mapping-source' ? mappingLimit : archiveLimit,
        )
        await this.#checkDirectory(directory)
        const payloadFile = 'payload' + record.extension
        await atomicPrivateWrite(path, payloadFile, bytes)
        metadata = {
          ...meta,
          format: record.format,
          extension: record.extension,
          payloadFile,
          ...digest(bytes),
          createdAt,
        }
      } else {
        metadata = {
          ...meta,
          extension: record.extension,
          outputFile: record.outputFile,
          createdAt,
        }
      }
      await this.#checkDirectory(directory)
      await atomicPrivateWrite(path, 'meta.json', JSON.stringify(metadata))
      if (!current()) rejectSelection()
      this.#retired.delete(record)
      this.#records.set(selectionId, record)
      return record
    } catch (error) {
      void this.retire(record)
      throw error
    } finally {
      await this.release(record)
    }
  }

  async #file(
    purpose: Purpose,
    path: string,
    binding: SelectionBinding,
  ): Promise<InputFile | OutputFile> {
    const name = basename(path)
    if (name.includes('\0')) rejectSelection()
    const lower = name.toLowerCase()
    if (purpose === 'mapping-source') {
      if (lower.endsWith('.csv')) return { purpose, extension: '.csv', format: 'csv' }
      if (lower.endsWith('.xlsx')) return { purpose, extension: '.xlsx', format: 'xlsx' }
      return rejectSelection()
    }
    const extension = purpose === 'report-html' ? '.html' : '.ontolearn.zip'
    if (name.length <= extension.length || !lower.endsWith(extension)) rejectSelection()
    if (purpose === 'package-import') return { purpose, extension: '.ontolearn.zip', format: 'zip' }
    const parent = dirname(path)
    if (!sameRealPath(await fs.realpath(parent), parent)) rejectSelection()
    const destinationDirectory = await directoryAt(parent)
    const uncertain = this.#uncertain.get(path)
    try {
      const entry = await fs.lstat(path)
      if (!entry.isFile()) rejectSelection()
      if (uncertain && matches(uncertain.record, binding)) {
        this.#uncertain.delete(path)
        if (sameFile(entry, uncertain.identity)) rejectSelection()
      }
    } catch (error) {
      if (errno(error) !== 'ENOENT') throw error
      if (uncertain && matches(uncertain.record, binding)) this.#uncertain.delete(path)
    }
    return {
      purpose,
      extension,
      outputFile: purpose === 'report-html' ? 'output.html' : 'output.ontolearn.zip',
      destinationPath: path,
      destinationDirectory,
    }
  }

  acquire(id: unknown, purpose: Purpose, binding: SelectionBinding, exclusive: boolean) {
    const record = validId(id) ? this.#records.get(id) : undefined
    if (
      !record ||
      record.purpose !== purpose ||
      !matches(record, binding) ||
      record.exclusive ||
      (exclusive && record.active)
    )
      return undefined
    record.active++
    record.exclusive = exclusive
    return record
  }

  async validate(record: SelectionRecord) {
    await this.#checkDirectory(record.directory)
    const meta = await fs.lstat(join(record.directory.path, 'meta.json'))
    if (!meta.isFile()) rejectSelection()
    if ('format' in record) {
      const payload = await fs.lstat(join(record.directory.path, 'payload' + record.extension))
      if (!payload.isFile()) rejectSelection()
    }
  }

  async #checkDirectory(directory: SelectionDirectory) {
    if (
      !this.root ||
      !sameFile(await directoryAt(this.root), directory.root) ||
      !sameFile(await directoryAt(directory.path), directory.identity)
    )
      rejectSelection()
  }

  async publish(
    record: SelectionRecord,
    expected: FileDigest,
    current: () => boolean,
  ): Promise<TransferPublicationReceiptDTO> {
    if (!('outputFile' in record))
      return { state: 'failed', code: 'destination-invalid', cleanup: 'complete' }
    try {
      await this.validate(record)
      const bytes = await regularBytes(
        join(record.directory.path, record.outputFile),
        expected.byteLength,
      )
      const actual = digest(bytes)
      await this.#checkDirectory(record.directory)
      if (actual.sha256 !== expected.sha256 || actual.byteLength !== expected.byteLength)
        rejectSelection()
      if (!current()) return { state: 'cancelled', cleanup: 'complete' }
      const file = new PreparedTransferFile(bytes, record.extension, record.destinationDirectory)
      const destination = record.destinationPath
      const receipt = await file.save(
        async () => ({ directory: dirname(destination), filename: basename(destination) }),
        {
          signal: record.controller.signal,
          canPublish: current,
        },
      )
      if (receipt.state === 'publication-unconfirmed' && file.pendingPublication && current()) {
        this.#uncertain.set(destination, { record, identity: file.pendingPublication })
      }
      if (receipt.state !== 'failed') return receipt
      const code =
        receipt.code === 'REPORT_DESTINATION_INVALID'
          ? 'destination-invalid'
          : receipt.code === 'REPORT_TARGET_EXISTS'
            ? 'target-exists'
            : 'write-failed'
      return { state: 'failed', code, cleanup: receipt.cleanup }
    } catch {
      return { state: 'failed', code: 'write-failed', cleanup: 'complete' }
    }
  }

  async acknowledgeReportPublication(
    record: SelectionRecord,
    reportRef: string,
    operationId: string,
    { sha256, byteLength }: FileDigest,
  ) {
    if (record.purpose !== 'report-html') rejectSelection()
    await this.#checkDirectory(record.directory)
    await atomicPrivateWrite(
      record.directory.path,
      'report-published.json',
      JSON.stringify({ version: 1, reportRef, operationId, sha256, byteLength }),
    )
  }

  retire(record: SelectionRecord): Promise<Cleanup> {
    this.#records.delete(record.selectionId)
    record.controller.abort()
    this.#retired.add(record)
    return this.#cleanup(record)
  }

  release(record: SelectionRecord): Promise<Cleanup> {
    record.active--
    record.exclusive = false
    return record.controller.signal.aborted ? this.#cleanup(record) : Promise.resolve('complete')
  }

  invalidate(): void {
    this.#uncertain.clear()
    for (const record of this.#records.values()) void this.retire(record)
    for (const record of this.#retired) {
      record.controller.abort()
      void this.#cleanup(record)
    }
  }

  #cleanup(record: SelectionRecord): Promise<Cleanup> {
    if (record.active) return Promise.resolve('pending')
    record.cleanup ??= (async () => {
      try {
        await this.#checkDirectory(record.directory)
        await fs.rm(record.directory.path, { recursive: true, force: true })
      } catch (error) {
        if (errno(error) !== 'ENOENT') return 'pending'
      }
      this.#retired.delete(record)
      return 'complete'
    })().finally(() => {
      record.cleanup = undefined
    })
    return record.cleanup
  }
}
