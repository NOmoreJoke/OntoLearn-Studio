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
  MainlineLibraryStatusDTO,
  MainlineManagementApplyParams,
  MainlineManagementCatalogDTO,
  MainlineManagementConfirmationDTO,
  MainlineManagementItemDTO,
  MainlineManagementKind,
  MainlineManagementOperationDTO,
  MainlineManagementPreviewDTO,
  MainlineManagementResultDTO,
  ProjectManagementBridge,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '../../../../packages/contracts/src/v2'
import {
  EngineError,
  type MainlineMethod,
  type MainlineProjectTransport,
  type QueryMainReadBudget,
} from './engine'

type Value = Record<string, unknown>
type Selection = { projectId: string; owner: object; session: string; epoch: number }
type Dependencies = {
  client: () => MainlineProjectTransport
  selection: () => Selection | null
  epoch: () => number
  call: <T>(client: MainlineProjectTransport, method: MainlineMethod, params: Value) => Promise<T>
  retireSelection: (projectId: string, epoch: number) => void
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
  value: MainlineManagementPreviewDTO
  scope: Scope
  budget: QueryMainReadBudget
  entry: object
  confirmation?: MainlineManagementConfirmationDTO
}
type Intent = {
  params: MainlineManagementApplyParams
  requestHash: string
  kind: MainlineManagementKind
  label: string | null
  libraryId: string
  outcome: 'pending' | 'applied' | 'not-found'
  delivered: boolean
  result: MainlineManagementResultDTO | null
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

export function managementCanonical(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    const text = JSON.stringify(value)
    if (typeof text !== 'string') throw failure()
    return text
  }
  if (Array.isArray(value)) return '[' + value.map(managementCanonical).join(',') + ']'
  const row = value as Value
  return (
    '{' +
    Object.keys(row)
      .sort()
      .map((key) => JSON.stringify(key) + ':' + managementCanonical(row[key]))
      .join(',') +
    '}'
  )
}
const hash = (value: unknown) =>
  createHash('sha256').update(managementCanonical(value)).digest('hex')
const keys = (value: unknown, expected: string[]): value is Value =>
  value !== null &&
  typeof value === 'object' &&
  !Array.isArray(value) &&
  Object.keys(value).length === expected.length &&
  expected.every((key) => Object.hasOwn(value, key))

function resultMatches(result: MainlineManagementResultDTO, intent: Intent): boolean {
  return (
    validateBusiness3('management.result', result) &&
    result.projectId === intent.params.projectId &&
    result.operationId === intent.params.operationId &&
    result.requestHash === intent.requestHash &&
    result.kind === intent.kind &&
    (result.kind === 'copy-current'
      ? result.targetProjectId !== result.projectId &&
        result.domainRevision === 1 &&
        result.operationSequence === 1 &&
        result.lifecycleState === 'active'
      : result.targetProjectId === result.projectId) &&
    (result.kind !== 'trash' || result.lifecycleState === 'trashed') &&
    (result.kind !== 'restore-trash' || result.lifecycleState === 'active')
  )
}

/** App-owned intent journal, never an engine receipt or permission to replay a write. */
class ManagementJournal {
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
            'params',
            'requestHash',
            'kind',
            'label',
            'libraryId',
            'outcome',
            'delivered',
            'result',
          ]) ||
          !validateBusiness3('params_project.management.apply', raw.params) ||
          raw.requestHash !== hash(raw.params) ||
          !validateBusiness3('management.kind', raw.kind) ||
          !validateBusiness3('hash', raw.libraryId) ||
          (raw.label !== null &&
            (typeof raw.label !== 'string' || Buffer.byteLength(raw.label) > 16384)) ||
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
          this.records.has(record.params.operationId)
        )
          throw failure('STORAGE_FAILURE')
        this.records.set(record.params.operationId, record)
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
    next.set(value.params.operationId, value)
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
        // A rename followed by fsync failure is not evidence that nothing was
        // persisted. Keep the file and fence further use until a fresh read.
        this.failed = true
        throw failure('STORAGE_FAILURE')
      }
    }
    this.records = next
  }
}

/** Trusted bounded refs and durable original intents for the finite management routes. */
export class ProjectManagementSession {
  #previews = new Map<string, Preview>()
  #confirmations = new Map<string, Preview>()
  #journal: ManagementJournal
  #active = 0
  #closed = false
  #holdings = new Set<{ entry: object; budget: QueryMainReadBudget }>()
  constructor(private readonly deps: Dependencies) {
    this.#journal = new ManagementJournal(deps.journalPath)
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
    if (!scope.selected) return true
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
    if (preview.confirmation) this.#confirmations.delete(preview.confirmation.confirmationRef)
  }
  #prune(): void {
    for (const preview of this.#previews.values())
      if (!this.#valid(preview.scope) || preview.value.expiresAtMs <= Date.now())
        this.#remove(preview)
  }
  async #status(client: MainlineProjectTransport): Promise<MainlineLibraryStatusDTO> {
    const value = await this.deps.call<MainlineLibraryStatusDTO>(
      client,
      'project.library.status',
      {},
    )
    if (!validateBusiness3('result_project.library.status', value)) throw failure()
    return value
  }
  catalog(args: Parameters<ProjectManagementBridge['getProjectManagementCatalog']>[0]) {
    return this.#work(async () => {
      if (!validateBusiness3('params_project.management.catalog', args)) throw failure()
      return this.deps.call<MainlineManagementCatalogDTO>(
        this.deps.client(),
        'project.management.catalog',
        args,
      )
    })
  }
  state(): Promise<MainlineManagementItemDTO> {
    return this.#work(async () => {
      const selected = this.deps.selection()
      if (!selected) throw failure('PERMISSION_DENIED')
      const value = await this.deps.call<MainlineManagementItemDTO>(
        this.deps.client(),
        'project.management.read',
        { projectId: selected.projectId },
      )
      if (this.deps.epoch() !== selected.epoch || value.projectId !== selected.projectId)
        throw failure('PERMISSION_DENIED')
      return value
    })
  }
  preview(args: Parameters<ProjectManagementBridge['previewProjectManagement']>[0]) {
    return this.#work(async () => {
      this.#prune()
      if (
        !keys(args, [
          'action',
          'expectedCheckpointRef',
          'expectedLifecycleVersion',
          ...(Object.hasOwn(args, 'restoreProjectId') ? ['restoreProjectId'] : []),
        ]) ||
        !validateBusiness3('management.action', args.action) ||
        this.#previews.size >= MAX_PENDING
      )
        throw failure()
      const restore = args.action.kind === 'restore-trash'
      if (restore !== Object.hasOwn(args, 'restoreProjectId')) throw failure()
      const current = this.deps.selection()
      const projectId = restore ? args.restoreProjectId : current?.projectId
      const params = {
        projectId,
        action: args.action,
        expectedCheckpointRef: args.expectedCheckpointRef,
        expectedLifecycleVersion: args.expectedLifecycleVersion,
      }
      if (!validateBusiness3('params_project.management.preview', params)) throw failure()
      const client = this.deps.client(),
        epoch = this.deps.epoch()
      const value = await this.deps.call<MainlineManagementPreviewDTO>(
        client,
        'project.management.preview',
        params,
      )
      const scope: Scope = {
        client,
        projectId: projectId!,
        session: client.engineSessionId!,
        epoch,
        selected: !restore,
      }
      if (
        !this.#valid(scope) ||
        !validateBusiness3('result_project.management.preview', value) ||
        value.projectId !== projectId ||
        managementCanonical(value.action) !== managementCanonical(args.action) ||
        value.documentHash !== hash({ action: value.action, document: value.document }) ||
        value.document.checkpointRef !== args.expectedCheckpointRef ||
        value.document.lifecycleVersion !== args.expectedLifecycleVersion ||
        value.expiresAtMs <= Date.now() ||
        value.expiresAtMs > Date.now() + 300000 ||
        this.#previews.has(value.previewRef)
      )
        throw failure()
      const budget = client.supervisor.queryReadBudget(client.owner),
        entry = Object.freeze({})
      budget.retainHolding(entry, value)
      this.#previews.set(value.previewRef, { value, scope, budget, entry })
      return value
    })
  }
  confirm(args: Parameters<ProjectManagementBridge['confirmProjectManagement']>[0]) {
    return this.#work(async () => {
      this.#prune()
      if (!keys(args, ['previewRef', 'documentHash'])) throw failure()
      const preview = this.#previews.get(args.previewRef)
      if (!preview || args.documentHash !== preview.value.documentHash) throw failure()
      if (preview.confirmation) {
        preview.budget.handoff(preview.confirmation)
        return preview.confirmation
      }
      const value = await this.deps.call<MainlineManagementConfirmationDTO>(
        preview.scope.client,
        'project.management.confirm',
        { projectId: preview.scope.projectId, ...args },
      )
      if (
        !this.#valid(preview.scope) ||
        !validateBusiness3('result_project.management.confirm', value) ||
        value.projectId !== preview.scope.projectId ||
        value.previewRef !== args.previewRef ||
        value.documentHash !== args.documentHash ||
        value.kind !== preview.value.action.kind ||
        this.#confirmations.has(value.confirmationRef)
      )
        throw failure()
      preview.budget.retainHolding(preview.entry, { preview: preview.value, confirmation: value })
      preview.confirmation = value
      this.#confirmations.set(value.confirmationRef, preview)
      return value
    })
  }
  #offer<T>(client: MainlineProjectTransport, intent: Intent, value: T): T {
    const budget = client.supervisor.queryReadBudget(client.owner)
    if (this.#holdings.size >= MAX_PENDING) throw failure()
    const holding = { budget, entry: Object.freeze({}) }
    budget.retainHolding(holding.entry, { params: intent.params, value })
    this.#holdings.add(holding)
    const original = holding
    budget.onReplyConsumed(original.entry, () => {
      const latest = this.#journal.records.get(intent.params.operationId)
      if (!latest || latest.requestHash !== intent.requestHash || latest.outcome === 'pending')
        throw failure()
      this.#journal.put({ ...latest, delivered: true })
      original.budget.releaseHolding(original.entry)
      this.#holdings.delete(original)
    })
    return value
  }
  apply(args: Parameters<ProjectManagementBridge['applyProjectManagement']>[0]) {
    return this.#work(async () => {
      this.#prune()
      if (!keys(args, ['operationId', 'confirmationRef', 'documentHash'])) throw failure()
      if (this.#journal.records.has(args.operationId)) throw failure() // Reconcile, never replay.
      if (this.#journal.pending.length || this.deps.hasOtherUnresolvedResponsibility())
        throw failure()
      const preview = this.#confirmations.get(args.confirmationRef)
      if (!preview || preview.value.documentHash !== args.documentHash) throw failure()
      const params = { projectId: preview.scope.projectId, ...args }
      if (!validateBusiness3('params_project.management.apply', params)) throw failure()
      const status = await this.#status(preview.scope.client)
      if (!this.#valid(preview.scope)) throw failure('PERMISSION_DENIED')
      const intent: Intent = {
        params,
        requestHash: hash(params),
        kind: preview.value.action.kind,
        label: preview.value.document.projectName,
        libraryId: status.libraryEvidenceRef,
        outcome: 'pending',
        delivered: false,
        result: null,
      }
      this.#journal.put(intent) // Durably record the exact request before entering the write.
      const value = await this.deps.call<MainlineManagementResultDTO>(
        preview.scope.client,
        'project.management.apply',
        params,
      )
      if (!resultMatches(value, intent)) throw failure()
      const accepted: Intent = { ...intent, outcome: 'applied', result: value }
      this.#journal.put(accepted)
      this.#remove(preview)
      if (value.kind === 'trash') this.deps.retireSelection(value.projectId, preview.scope.epoch)
      return this.#offer(preview.scope.client, accepted, value)
    })
  }
  operation(args: Parameters<ProjectManagementBridge['getProjectManagementOperation']>[0]) {
    return this.#work(async () => {
      if (!keys(args, ['operationId']) || !validateBusiness3('id', args.operationId))
        throw failure()
      const intent = this.#journal.records.get(args.operationId)
      if (!intent) throw failure('PERMISSION_DENIED')
      const client = this.deps.client(),
        status = await this.#status(client)
      if (status.libraryEvidenceRef !== intent.libraryId) throw failure('PERMISSION_DENIED')
      const value = await this.deps.call<MainlineManagementOperationDTO>(
        client,
        'project.management.operation.get',
        {
          projectId: intent.params.projectId,
          operationId: intent.params.operationId,
          requestHash: intent.requestHash,
        },
      )
      if (
        !validateBusiness3('result_project.management.operation.get', value) ||
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
  pending() {
    return this.#work(async () => {
      const pending = this.#journal.pending
      const client = this.deps.client()
      const status = await this.#status(client)
      if (pending.some((intent) => intent.libraryId !== status.libraryEvidenceRef))
        throw failure('PERMISSION_DENIED')
      const value = pending.map((intent) => ({
        operationId: intent.params.operationId,
        projectId: intent.params.projectId,
        kind: intent.kind,
        label: intent.label,
      }))
      client.supervisor.queryReadBudget(client.owner).handoff(value)
      return value
    })
  }
  dispose(): void {
    this.#closed = true
    this.#prune()
    // Pending intents and unconsumed original holdings remain owned; closing a
    // view is neither a durable outcome nor a receipt acknowledgment.
  }
}
