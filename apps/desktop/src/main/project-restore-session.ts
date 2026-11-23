import { createHash, randomUUID } from 'node:crypto'
import {
  closeSync,
  constants,
  existsSync,
  fstatSync,
  fsyncSync,
  lstatSync,
  mkdirSync,
  openSync,
  readSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { dirname, isAbsolute } from 'node:path'
import { parseStrictJson } from './jsonl'
import type {
  PendingProjectRestoreOperationDTO,
  ProjectCheckpointCreateDTO,
  ProjectCheckpointListDTO,
  ProjectRestoreApplyArgs,
  ProjectRestoreConfirmationDTO,
  ProjectRestoreOperationDTO,
  ProjectRestorePageDTO,
  ProjectRestorePreviewDTO,
  ProjectRestoreResultDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '../../../../packages/contracts/src/v2'
import {
  EngineError,
  type MainlineMethod,
  type MainlineProjectTransport,
  type QueryMainReadBudget,
} from './engine'
import { managementCanonical } from './project-management-session'

type Value = Record<string, unknown>
type Selection = { projectId: string; owner: object; session: string; epoch: number }
type Dependencies = {
  client: () => MainlineProjectTransport
  selection: () => Selection | null
  epoch: () => number
  call: <T>(client: MainlineProjectTransport, method: MainlineMethod, params: Value) => Promise<T>
  hasOtherUnresolvedResponsibility: () => boolean
  journalPath?: string
}
type Scope = {
  client: MainlineProjectTransport
  projectId: string
  session: string
  epoch: number
  selected: boolean
}
type Preview = {
  value: ProjectRestorePreviewDTO
  scope: Scope
  budget: QueryMainReadBudget
  entry: object
  readSegmentHashes: string[]
  confirmation?: ProjectRestoreConfirmationDTO
}
type Intent = {
  operationId: string
  projectId: string
  requestHash: string
  targetCheckpointRef: string
  documentHash: string
  outcome: 'pending' | 'applied' | 'not-found'
  delivered: boolean
  result: ProjectRestoreResultDTO | null
}
const MAX_PENDING = 16
const MAX_JOURNAL = 64
const MAX_JOURNAL_BYTES = 1048576
const failure = (
  code: 'INVALID_STATE' | 'PERMISSION_DENIED' | 'STORAGE_FAILURE' = 'INVALID_STATE',
) =>
  new EngineError({
    code,
    messageKey:
      code === 'PERMISSION_DENIED'
        ? 'permission.denied'
        : code === 'STORAGE_FAILURE'
          ? 'storage.failure'
          : 'protocol.invalidState',
    params: {},
    retryable: false,
  })
const hash = (value: unknown) =>
  createHash('sha256').update(managementCanonical(value)).digest('hex')
const keys = (value: unknown, expected: string[]): value is Value =>
  value !== null &&
  typeof value === 'object' &&
  !Array.isArray(value) &&
  Object.keys(value).length === expected.length &&
  expected.every((key) => Object.hasOwn(value, key))

/**
 * Element-wise ordered comparison of two hash lists.
 * Array reference comparison (`!==`) is always true for fresh arrays, so the
 * segment-completeness proof must compare length and each sorted element.
 */
function sameHashList(actual: readonly string[], expected: readonly string[]): boolean {
  if (actual.length !== expected.length) return false
  const left = [...actual].sort()
  const right = [...expected].sort()
  return left.every((item, index) => item === right[index])
}

function resultMatches(result: ProjectRestoreResultDTO, intent: Intent): boolean {
  return (
    validateBusiness3('result_project.restore.apply', result) &&
    result.projectId === intent.projectId &&
    result.operationId === intent.operationId &&
    result.requestHash === intent.requestHash
  )
}

/** App-owned restore intent journal, never an engine receipt or replay grant. */
class RestoreJournal {
  records = new Map<string, Intent>()
  failed = false
  constructor(private readonly path?: string) {
    try {
      if (path && !isAbsolute(path)) throw failure('STORAGE_FAILURE')
      if (!path || !existsSync(path)) return
      const before = lstatSync(path)
      if (!before.isFile() || before.nlink !== 1) throw failure('STORAGE_FAILURE')
      const fd = openSync(
        path,
        constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0),
      )
      let value: unknown
      try {
        const stat = fstatSync(fd)
        if (
          !stat.isFile() ||
          stat.nlink !== 1 ||
          stat.size > MAX_JOURNAL_BYTES ||
          stat.dev !== before.dev ||
          stat.ino !== before.ino
        )
          throw failure('STORAGE_FAILURE')
        const bytes = Buffer.alloc(MAX_JOURNAL_BYTES + 1)
        let length = 0
        for (;;) {
          const count = readSync(fd, bytes, length, bytes.length - length, null)
          length += count
          if (!count || length === bytes.length) break
        }
        if (length > MAX_JOURNAL_BYTES) throw failure('STORAGE_FAILURE')
        const after = fstatSync(fd)
        if (after.size !== stat.size || after.mtimeMs !== stat.mtimeMs)
          throw failure('STORAGE_FAILURE')
        value = parseStrictJson(
          new TextDecoder('utf-8', { fatal: true }).decode(bytes.subarray(0, length)),
        )
      } finally {
        closeSync(fd)
      }
      if (
        !keys(value, ['journalVersion', 'records']) ||
        value.journalVersion !== 1 ||
        !Array.isArray(value.records) ||
        value.records.length > MAX_JOURNAL
      )
        throw failure('STORAGE_FAILURE')
      for (const raw of value.records) {
        if (
          !keys(raw, [
            'operationId',
            'projectId',
            'requestHash',
            'targetCheckpointRef',
            'documentHash',
            'outcome',
            'delivered',
            'result',
          ]) ||
          !validateBusiness3('id', raw.operationId) ||
          !validateBusiness3('id', raw.projectId) ||
          !validateBusiness3('hash', raw.requestHash) ||
          !validateBusiness3('hash', raw.targetCheckpointRef) ||
          !validateBusiness3('hash', raw.documentHash) ||
          !['pending', 'applied', 'not-found'].includes(String(raw.outcome)) ||
          typeof raw.delivered !== 'boolean'
        )
          throw failure('STORAGE_FAILURE')
        const record = raw as unknown as Intent
        if (
          (record.outcome === 'applied'
            ? !record.result || !resultMatches(record.result, record)
            : record.result !== null) ||
          (record.outcome === 'pending' && record.delivered) ||
          this.records.has(record.operationId)
        )
          throw failure('STORAGE_FAILURE')
        this.records.set(record.operationId, record)
      }
      if (this.pending.length > MAX_PENDING) throw failure('STORAGE_FAILURE')
    } catch {
      this.failed = true // Preserve the original file and refuse new writes.
    }
  }
  get pending(): Intent[] {
    return [...this.records.values()].filter((record) => !record.delivered)
  }
  put(value: Intent): void {
    if (this.failed) throw failure('STORAGE_FAILURE')
    const next = new Map(this.records)
    next.set(value.operationId, value)
    while (next.size > MAX_JOURNAL) {
      const old = [...next].find(([, record]) => record.delivered)
      if (!old) throw failure()
      next.delete(old[0])
    }
    if ([...next.values()].filter((record) => !record.delivered).length > MAX_PENDING)
      throw failure()
    const text = managementCanonical({ journalVersion: 1, records: [...next.values()] }) + '\n'
    if (Buffer.byteLength(text) > MAX_JOURNAL_BYTES) throw failure()
    if (this.path) {
      const temporary = this.path + '.' + randomUUID() + '.tmp'
      let fd: number | undefined
      try {
        mkdirSync(dirname(this.path), { recursive: true })
        fd = openSync(temporary, 'wx', 0o600)
        writeFileSync(fd, text, 'utf8')
        fsyncSync(fd)
        closeSync(fd)
        fd = undefined
        renameSync(temporary, this.path)
        if (process.platform !== 'win32') {
          const directory = openSync(dirname(this.path), 'r')
          try {
            fsyncSync(directory)
          } finally {
            closeSync(directory)
          }
        }
      } catch {
        if (fd !== undefined) closeSync(fd)
        if (existsSync(temporary)) unlinkSync(temporary)
        this.failed = true
        throw failure('STORAGE_FAILURE')
      }
    }
    this.records = next
  }
}

/** Trusted bounded restore refs, collected segment reads and durable intents. */
export class ProjectRestoreSession {
  #previews = new Map<string, Preview>()
  #holdings = new Set<{ entry: object; budget: QueryMainReadBudget }>()
  #journal: RestoreJournal
  #active = 0
  #closed = false
  constructor(private readonly deps: Dependencies) {
    this.#journal = new RestoreJournal(deps.journalPath)
  }
  get busy(): boolean {
    return this.#active > 0
  }
  get hasUnresolvedResponsibility(): boolean {
    return (
      this.busy ||
      this.#journal.failed ||
      this.#journal.pending.length > 0 ||
      this.#holdings.size > 0
    )
  }
  #check(): void {
    if (this.#closed) throw failure('PERMISSION_DENIED')
    if (this.#journal.failed) throw failure('STORAGE_FAILURE')
  }
  async #work<T>(work: () => Promise<T>): Promise<T> {
    this.#check()
    if (this.#active) throw failure()
    this.#active++
    try {
      return await work()
    } finally {
      this.#active--
    }
  }
  #valid(scope: Scope): boolean {
    if (
      this.#closed ||
      this.deps.epoch() !== scope.epoch ||
      scope.client.engineSessionId !== scope.session ||
      !scope.client.supervisor.ownsMainlineClient(scope.client)
    )
      return false
    const selected = this.deps.selection()
    return (
      !!selected &&
      selected.projectId === scope.projectId &&
      selected.owner === scope.client.owner &&
      selected.session === scope.session &&
      selected.epoch === scope.epoch
    )
  }
  #remove(preview: Preview): void {
    preview.budget.releaseHolding(preview.entry)
    this.#previews.delete(preview.value.previewRef)
  }
  #prune(): void {
    for (const preview of this.#previews.values())
      if (!this.#valid(preview.scope) || preview.value.expiresAtMs <= Date.now())
        this.#remove(preview)
  }
  #selected(): { projectId: string; client: MainlineProjectTransport; epoch: number } {
    const current = this.deps.selection()
    if (!current) throw failure('PERMISSION_DENIED')
    const client = this.deps.client()
    if (client.owner !== current.owner) throw failure('PERMISSION_DENIED')
    return { projectId: current.projectId, client, epoch: this.deps.epoch() }
  }
  list(args: { pageSize: number; cursor: string | null }) {
    return this.#work(async () => {
      const { projectId, client } = this.#selected()
      const params = { ...args, projectId }
      if (!validateBusiness3('params_project.checkpoint.list', params)) throw failure()
      const value = await this.deps.call<ProjectCheckpointListDTO>(
        client,
        'project.checkpoint.list',
        params,
      )
      if (
        !validateBusiness3('result_project.checkpoint.list', value) ||
        value.projectId !== projectId
      )
        throw failure()
      return value
    })
  }
  create(args: { operationId: string; label: string | null }) {
    return this.#work(async () => {
      const { projectId, client } = this.#selected()
      const params = { ...args, projectId }
      if (!validateBusiness3('params_project.checkpoint.create', params)) throw failure()
      const value = await this.deps.call<ProjectCheckpointCreateDTO>(
        client,
        'project.checkpoint.create',
        params,
      )
      if (
        !validateBusiness3('result_project.checkpoint.create', value) ||
        value.projectId !== projectId ||
        value.operationId !== args.operationId ||
        value.label !== args.label
      )
        throw failure()
      return value
    })
  }
  preview(args: {
    targetCheckpointRef: string
    expectedCheckpointRef: string
    expectedLifecycleVersion: number
  }) {
    return this.#work(async () => {
      this.#prune()
      if (!keys(args, ['targetCheckpointRef', 'expectedCheckpointRef', 'expectedLifecycleVersion']))
        throw failure()
      if (this.#previews.size >= MAX_PENDING) throw failure()
      const { projectId, client, epoch } = this.#selected()
      const params = { ...args, projectId }
      if (!validateBusiness3('params_project.restore.preview', params)) throw failure()
      const value = await this.deps.call<ProjectRestorePreviewDTO>(
        client,
        'project.restore.preview',
        params,
      )
      const scope: Scope = {
        client,
        projectId,
        session: client.engineSessionId!,
        epoch,
        selected: true,
      }
      const manifest = value.manifest
      if (
        !this.#valid(scope) ||
        !validateBusiness3('result_project.restore.preview', value) ||
        value.projectId !== projectId ||
        value.targetCheckpointRef !== args.targetCheckpointRef ||
        value.currentCheckpointRef !== args.expectedCheckpointRef ||
        value.documentHash !== manifest.documentHash ||
        value.expiresAtMs <= Date.now() ||
        this.#previews.has(value.previewRef)
      )
        throw failure()
      const budget = client.supervisor.queryReadBudget(client.owner)
      const entry = Object.freeze({})
      budget.retainHolding(entry, value)
      this.#previews.set(value.previewRef, {
        value,
        scope,
        budget,
        entry,
        readSegmentHashes: [],
      })
      return value
    })
  }
  page(args: { previewRef: string; cursor: string | null }) {
    return this.#work(async () => {
      this.#prune()
      if (!keys(args, ['previewRef', 'cursor'])) throw failure()
      const preview = this.#previews.get(args.previewRef)
      if (!preview) throw failure('PERMISSION_DENIED')
      const params = { ...args, projectId: preview.scope.projectId }
      if (!validateBusiness3('params_project.restore.page', params)) throw failure()
      const value = await this.deps.call<ProjectRestorePageDTO>(
        preview.scope.client,
        'project.restore.page',
        params,
      )
      if (
        !this.#valid(preview.scope) ||
        !validateBusiness3('result_project.restore.page', value) ||
        value.previewRef !== args.previewRef ||
        value.documentHash !== preview.value.documentHash
      )
        throw failure()
      // Accumulate the actual served proof; confirm refuses unread segments.
      for (const segment of value.segments) {
        if (preview.readSegmentHashes.includes(segment.sha256)) continue
        preview.readSegmentHashes.push(segment.sha256)
      }
      return value
    })
  }
  confirm(args: { previewRef: string; documentHash: string; readSegmentHashes: string[] }) {
    return this.#work(async () => {
      this.#prune()
      if (!keys(args, ['previewRef', 'documentHash', 'readSegmentHashes'])) throw failure()
      const preview = this.#previews.get(args.previewRef)
      if (!preview || args.documentHash !== preview.value.documentHash) throw failure()
      const expected = preview.value.manifest.segments.map((segment) => segment.sha256)
      // Both the renderer claim and the actually served pages must be complete.
      if (
        !sameHashList(args.readSegmentHashes, expected) ||
        !sameHashList(preview.readSegmentHashes, expected)
      )
        throw failure('PERMISSION_DENIED')
      if (preview.confirmation) {
        preview.budget.handoff(preview.confirmation)
        return preview.confirmation
      }
      const params = {
        projectId: preview.scope.projectId,
        previewRef: args.previewRef,
        documentHash: args.documentHash,
        readSegmentHashes: expected,
      }
      if (!validateBusiness3('params_project.restore.confirm', params)) throw failure()
      const value = await this.deps.call<ProjectRestoreConfirmationDTO>(
        preview.scope.client,
        'project.restore.confirm',
        params,
      )
      if (
        !this.#valid(preview.scope) ||
        !validateBusiness3('result_project.restore.confirm', value) ||
        value.projectId !== preview.scope.projectId ||
        value.previewRef !== args.previewRef ||
        value.documentHash !== args.documentHash
      )
        throw failure()
      preview.budget.retainHolding(preview.entry, {
        preview: preview.value,
        confirmation: value,
      })
      preview.confirmation = value
      return value
    })
  }
  #offer<T>(client: MainlineProjectTransport, intent: Intent, value: T): T {
    const budget = client.supervisor.queryReadBudget(client.owner)
    if (this.#holdings.size >= MAX_PENDING) throw failure()
    const holding = { budget, entry: Object.freeze({}) }
    budget.retainHolding(holding.entry, { params: intent, value })
    this.#holdings.add(holding)
    const original = holding
    budget.onReplyConsumed(original.entry, () => {
      const latest = this.#journal.records.get(intent.operationId)
      if (!latest || latest.requestHash !== intent.requestHash || latest.outcome === 'pending')
        throw failure()
      this.#journal.put({ ...latest, delivered: true })
      original.budget.releaseHolding(original.entry)
      this.#holdings.delete(original)
    })
    return value
  }
  apply(args: ProjectRestoreApplyArgs) {
    return this.#work(async () => {
      this.#prune()
      if (!keys(args, ['operationId', 'confirmationRef', 'documentHash'])) throw failure()
      const existing = this.#journal.records.get(args.operationId)
      if (existing) {
        // An acknowledged original may be replayed: the engine returns its own
        // durable receipt for the same operation and performs no second write.
        // An unresolved original must be reconciled, never replayed.
        if (!existing.delivered || existing.outcome !== 'applied' || !existing.result)
          throw failure()
        const { projectId, client } = this.#selected()
        if (projectId !== existing.projectId) throw failure('PERMISSION_DENIED')
        // The exact original request identity, never a reworded one.
        if (
          hash({
            projectId,
            operationId: args.operationId,
            confirmationRef: args.confirmationRef,
            documentHash: args.documentHash,
          }) !== existing.requestHash
        )
          throw failure()
        const params = { ...args, projectId }
        if (!validateBusiness3('params_project.restore.apply', params)) throw failure()
        const value = await this.deps.call<ProjectRestoreResultDTO>(
          client,
          'project.restore.apply',
          params,
        )
        if (!resultMatches(value, existing)) throw failure()
        return this.#offer(client, existing, value)
      }
      if (this.#journal.pending.length || this.deps.hasOtherUnresolvedResponsibility())
        throw failure()
      const preview = [...this.#previews.values()].find(
        (item) => item.confirmation?.confirmationRef === args.confirmationRef,
      )
      if (!preview || !preview.confirmation || args.documentHash !== preview.value.documentHash)
        throw failure()
      const projectId = preview.scope.projectId
      const params = { ...args, projectId }
      if (!validateBusiness3('params_project.restore.apply', params)) throw failure()
      const requestHash = hash({
        projectId,
        operationId: args.operationId,
        confirmationRef: args.confirmationRef,
        documentHash: args.documentHash,
      })
      const intent: Intent = {
        operationId: args.operationId,
        projectId,
        requestHash,
        targetCheckpointRef: preview.value.targetCheckpointRef,
        documentHash: args.documentHash,
        outcome: 'pending',
        delivered: false,
        result: null,
      }
      this.#journal.put(intent) // Durably record the exact request before the write.
      const value = await this.deps.call<ProjectRestoreResultDTO>(
        preview.scope.client,
        'project.restore.apply',
        params,
      )
      if (!resultMatches(value, intent)) throw failure()
      const accepted: Intent = { ...intent, outcome: 'applied', result: value }
      this.#journal.put(accepted)
      this.#remove(preview)
      return this.#offer(preview.scope.client, accepted, value)
    })
  }
  operation(args: { operationId: string }) {
    return this.#work(async () => {
      if (!keys(args, ['operationId']) || !validateBusiness3('id', args.operationId))
        throw failure()
      const intent = this.#journal.records.get(args.operationId)
      if (!intent) throw failure('PERMISSION_DENIED')
      const client = this.deps.client()
      if (!client.supervisor.ownsMainlineClient(client)) throw failure('PERMISSION_DENIED')
      const current = this.deps.selection()
      if (current && (current.owner !== client.owner || current.projectId !== intent.projectId))
        throw failure('PERMISSION_DENIED')
      const value = await this.deps.call<ProjectRestoreOperationDTO>(
        client,
        'project.restore.operation.get',
        {
          projectId: intent.projectId,
          operationId: intent.operationId,
          requestHash: intent.requestHash,
        },
      )
      if (
        !validateBusiness3('result_project.restore.operation.get', value) ||
        (value.state === 'applied' && !resultMatches(value.result, intent)) ||
        (intent.outcome === 'applied' &&
          (value.state !== 'applied' ||
            managementCanonical(value.result) !== managementCanonical(intent.result))) ||
        (intent.outcome === 'not-found' && value.state !== 'not-found')
      )
        throw failure()
      const resolved: Intent = {
        ...intent,
        outcome: value.state === 'applied' ? 'applied' : 'not-found',
        result: value.result,
        delivered: false,
      }
      this.#journal.put(resolved)
      return this.#offer(client, resolved, value)
    })
  }
  pending(): Promise<PendingProjectRestoreOperationDTO[]> {
    return this.#work(async () => {
      const pending = this.#journal.pending
      const client = this.deps.client()
      const value = pending.map((intent) => ({
        operationId: intent.operationId,
        projectId: intent.projectId,
        targetCheckpointRef: intent.targetCheckpointRef,
        documentHash: intent.documentHash,
      }))
      client.supervisor.queryReadBudget(client.owner).handoff(value)
      return value
    })
  }
  dispose(): void {
    this.#closed = true
    this.#prune()
  }
}
