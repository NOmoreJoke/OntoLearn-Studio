import { createHash, randomUUID } from 'node:crypto'
import { z } from 'zod'
import {
  safeError,
  safeDisplayError,
  type BridgeResult,
  type JobView,
  type QueryConsumerBridge,
  type QueryDefinitionRecordDTO,
  type QueryDefinitionLoadDTO,
  type QueryDescriptorWireDTO,
  type QueryDescriptorDTO,
  type QueryExecuteArgs,
  type QueryExecutionIdentityDTO,
  type QueryExecutionReceiptDTO,
  type QueryRowsPageDTO,
  type QueryTextPageDTO,
} from '@ontolearn/contracts'
import {
  queryConsumerResultMatches,
  normalizeQueryDraft,
  validateBusiness3,
  validateV2,
} from '../../../../packages/contracts/src/v2'
import { EngineError, QueryProjectReadTicket, type QueryMainReadBudget } from './engine'
import { OrdinaryProjectSource, type OrdinaryCurrent } from './ordinary-project-source'
import type { TaskService } from './task-service'

type Current = NonNullable<OrdinaryCurrent> & Readonly<{ viewGeneration: number }>
type WireRecord = Record<string, unknown>
const sources = new WeakSet<OrdinaryProjectSource>()
const error = (
  code: 'PERMISSION_DENIED' | 'INVALID_STATE' | 'IDENTITY_CONFLICT' | 'CURSOR_MISMATCH',
) =>
  new EngineError({
    code,
    messageKey:
      code === 'PERMISSION_DENIED'
        ? 'permission.denied'
        : code === 'IDENTITY_CONFLICT'
          ? 'operation.identityConflict'
          : code === 'CURSOR_MISMATCH'
            ? 'result.cursorMismatch'
            : 'protocol.invalidState',
    params: {},
    retryable: false,
  })
const invalidParams = () =>
  new EngineError({
    code: 'INVALID_REQUEST',
    messageKey: 'protocol.invalidRequest',
    params: { field: 'params' },
    retryable: false,
  })
const id = z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/)
function same(a: unknown, b: unknown): boolean {
  if (a === b) return true
  if (Array.isArray(a) && Array.isArray(b))
    return a.length === b.length && a.every((v, i) => same(v, b[i]))
  if (!a || !b || typeof a !== 'object' || typeof b !== 'object') return false
  const x = a as WireRecord,
    y = b as WireRecord
  return (
    Object.keys(x).length === Object.keys(y).length &&
    Object.keys(x).every((k) => Object.hasOwn(y, k) && same(x[k], y[k]))
  )
}
function copy<T>(value: T): T {
  return freeze(JSON.parse(JSON.stringify(value)) as T)
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') for (const v of Object.values(value)) freeze(v)
  return (value && typeof value === 'object' ? Object.freeze(value) : value) as T
}
type Entry = {
  ref: string
  kind: 'base' | 'load' | 'descriptor' | 'intent'
  context: Current
  budget: QueryMainReadBudget
  state: 'pending' | 'live' | 'retired' | 'unknown'
  busy: number
  value?: WireRecord
  textBusy?: boolean
  rowsBusy?: boolean
  nextUtf8Byte?: number
  nextIndex?: number
  textCursor?: string
  rowsCursor?: string
  textDone?: boolean
  rowsDone?: boolean
  lastTextCursor?: string
  lastTextStart?: number
  lastTextSize?: number
  lastRowsCursor?: string
  lastRowsStart?: number
  lastRowsSize?: number
  operationId?: string
  request?: WireRecord
  executionIdentity?: QueryExecutionIdentityDTO
  intent?: QueryExecuteArgs
  accepted?: JobView
  watch?: object
  writeEntered?: boolean
  readResponsibility?: QueryProjectReadTicket
}

const holdingFields = [
  'value',
  'request',
  'intent',
  'executionIdentity',
  'accepted',
  'operationId',
  'nextUtf8Byte',
  'nextIndex',
  'textCursor',
  'rowsCursor',
  'textDone',
  'rowsDone',
  'lastTextCursor',
  'lastTextStart',
  'lastTextSize',
  'lastRowsCursor',
  'lastRowsStart',
  'lastRowsSize',
] as const
type EntryHolding = Pick<Entry, (typeof holdingFields)[number]>

/** Main-only consumer of the actual external issuer; no save/confirm grant. */
export class QueryDefinitionService implements QueryConsumerBridge {
  #projectedErrors = new WeakSet<EngineError>()
  #entries = new Map<string, Entry>()
  #release: () => void
  #disposed = false
  #budget?: { owner: object; value: QueryMainReadBudget }
  constructor(
    readonly source: OrdinaryProjectSource,
    private readonly tasks: TaskService,
  ) {
    if (!(source instanceof OrdinaryProjectSource) || sources.has(source))
      throw error('INVALID_STATE')
    sources.add(source)
    this.#release = source.observe(() => this.#fence())
  }
  get hasOutstanding(): boolean {
    return [...this.#entries.values()].some((e) => e.busy > 0 || e.state === 'unknown')
  }
  #current(): Current {
    const current = this.source.current()
    if (this.#disposed || !current) throw error('PERMISSION_DENIED')
    // TaskService view replacement does not notify OrdinaryProjectSource.
    // Fence retired entries at every admission and capture this actual generation.
    this.#fence()
    const viewGeneration = this.tasks.queryViewGeneration(
      current.project.projectId,
      current.supervisor,
    )
    return Object.freeze({ ...current, viewGeneration })
  }
  #live(current: Current, revision = true): boolean {
    const now = this.source.current()
    if (
      this.#disposed ||
      !now ||
      now.owner !== current.owner ||
      now.supervisor !== current.supervisor ||
      now.engineSessionId !== current.engineSessionId ||
      now.selectionSeq !== current.selectionSeq ||
      now.project.projectId !== current.project.projectId ||
      (revision &&
        (now.project.projectRevision !== current.project.projectRevision ||
          now.project.inputSnapshotId !== current.project.inputSnapshotId))
    )
      return false
    try {
      return (
        this.tasks.queryViewGeneration(current.project.projectId, current.supervisor) ===
        current.viewGeneration
      )
    } catch {
      return false
    }
  }
  #keep(e: Entry, updates: Partial<EntryHolding>): void {
    if (e.context.supervisor.profile === 'business3') {
      // Only finite plain data crosses the budget boundary, never the issuer graph.
      const projection: WireRecord = {
        ref: e.ref,
        kind: e.kind,
        engineSessionId: e.context.engineSessionId,
        projectId: e.context.project.projectId,
        project: e.context.project,
        selectionSeq: e.context.selectionSeq,
        viewGeneration: e.context.viewGeneration,
      }
      for (const key of holdingFields) {
        const value = Object.hasOwn(updates, key) ? updates[key] : e[key]
        if (value !== undefined) projection[key] = value
      }
      e.budget.retainHolding(e, projection)
    }
    Object.assign(e, updates)
  }
  #drop(e: Entry): void {
    if (this.#entries.get(e.ref) !== e) return
    if (e.state === 'unknown' || e.readResponsibility) return
    if (e.kind === 'intent' && (e.writeEntered || e.accepted) && e.watch) {
      e.state = 'unknown'
      return
    }
    if (e.busy > 0) {
      e.state = 'retired'
      return
    }
    // A cleanup failure keeps the original entry and cannot replace a primary error.
    try {
      if (e.watch) this.tasks.releaseQueryWatch(e.watch)
    } catch {
      e.state = 'unknown'
      return
    }
    const saved: Partial<EntryHolding> = {}
    for (const key of holdingFields)
      if (e[key] !== undefined) Object.assign(saved, { [key]: e[key] })
    e.watch = undefined
    for (const key of holdingFields) delete e[key]
    this.#entries.delete(e.ref)
    if (e.context.supervisor.profile === 'business3') {
      try {
        e.budget.releaseHolding(e)
      } catch {
        Object.assign(e, saved)
        e.state = 'unknown'
        this.#entries.set(e.ref, e)
      }
    }
  }
  #fence(): void {
    for (const e of this.#entries.values())
      if (!this.#live(e.context)) {
        if (
          e.readResponsibility ||
          (e.kind === 'intent' && (e.writeEntered || !!e.accepted) && !!e.watch) ||
          e.state === 'unknown'
        )
          e.state = 'unknown'
        else this.#drop(e)
      }
  }
  #scope(current: Current, value: unknown): QueryMainReadBudget {
    if (!this.#live(current)) throw error('PERMISSION_DENIED')
    if (this.#budget?.owner !== current.owner)
      this.#budget = {
        owner: current.owner,
        value: current.supervisor.queryReadBudget(current.owner),
      }
    const budget = this.#budget.value
    budget.beforeArguments(value)
    if (!this.#live(current)) throw error('PERMISSION_DENIED')
    return budget
  }
  #pay(budget: QueryMainReadBudget, stage: string): void {
    // Pay before IPC argument validation, clone/parse/retention and async reply overlap.
    // This consumes the actual original issuer's account, not a new capacity grant.
    budget.reserve(
      stage,
      32 * 262144,
      this.source.current()?.supervisor.profile === 'business3' ? 263168 : 16 * 262144,
      32 * 262144,
    )
  }
  #entry(kind: Entry['kind'], context: Current, budget: QueryMainReadBudget): Entry {
    if (this.#entries.size >= 16) throw error('INVALID_STATE')
    this.#pay(budget, 'query combined record before allocation')
    if (!this.#live(context) || this.#entries.size >= 16) throw error('PERMISSION_DENIED')
    const e: Entry = { ref: randomUUID(), kind, context, budget, state: 'pending', busy: 0 }
    this.#keep(e, {})
    this.#entries.set(e.ref, e)
    return e
  }
  #ref(value: string, kind: Entry['kind'], current: Current): Entry {
    const e = this.#entries.get(value)
    if (
      !e ||
      e.kind !== kind ||
      e.state !== 'live' ||
      !this.#live(e.context) ||
      !this.#live(current)
    )
      throw error('PERMISSION_DENIED')
    return e
  }
  #operationError(current: Current, cause: unknown, operation: Promise<unknown>): EngineError {
    const error = new EngineError(current.supervisor.projectFailure(cause, operation))
    this.#projectedErrors.add(error)
    return error
  }
  async #wire(
    e: Entry,
    current: Current,
    method: string,
    params: WireRecord,
    expected?: WireRecord,
  ): Promise<unknown> {
    this.#pay(e.budget, 'query request/reply prepaid')
    const request = copy(params),
      facts = expected ? copy(expected) : undefined
    const pin = current.supervisor.issueQueryPin(current.owner, current.engineSessionId, () =>
      this.#live(current),
    )
    e.busy++
    try {
      const operation = current.supervisor.requestPinned(method, request, pin)
      const value = await operation.catch((cause) => {
        throw this.#operationError(current, cause, operation)
      })
      if (!this.#live(current)) throw error('PERMISSION_DENIED')
      // Canonical does not treat an authenticated error envelope as a binding failure.
      if (!queryConsumerResultMatches(method, request, value, facts))
        throw error('IDENTITY_CONFLICT')
      return value
    } finally {
      e.busy--
      if (e.state === 'retired' && e.busy === 0) this.#drop(e)
    }
  }
  #result<T>(e: Entry, value: T, current = e.context): T {
    if (!this.#live(current)) throw error('PERMISSION_DENIED')
    e.budget.handoff(value)
    if (!this.#live(current)) throw error('PERMISSION_DENIED')
    return value
  }
  async #run<T>(work: () => Promise<T>): Promise<BridgeResult<T>> {
    let context: Current | undefined
    let finish: (() => void) | undefined
    try {
      context = this.#current()
      if (context.supervisor.profile === 'business3')
        finish = context.supervisor.queryReadBudget(context.owner).beginConsumerRequest()
      const data = await work()
      // Include the wrapper's own await, after the operation's local cleanup.
      if (!this.#live(context)) throw error('PERMISSION_DENIED')
      return { ok: true, data }
    } catch (cause) {
      if (context && !this.#live(context))
        return { ok: false, error: safeError(error('PERMISSION_DENIED').error) }
      return {
        ok: false,
        error:
          cause instanceof EngineError && this.#projectedErrors.has(cause)
            ? safeDisplayError(cause.error)
            : safeError(cause instanceof EngineError ? cause.error : undefined),
      }
    } finally {
      finish?.()
    }
  }
  getQueryDefinitionBase(): ReturnType<QueryConsumerBridge['getQueryDefinitionBase']> {
    return this.#run(async () => {
      const current = this.#current(),
        budget = this.#scope(current, null),
        e = this.#entry('base', current, budget)
      let read: QueryProjectReadTicket | undefined,
        failed = false
      let cleanupFailure: { cause: unknown } | undefined
      let result: { baseRef: string; projectRevision: number; inputSnapshotId: string }
      // Register an unsettled owner record before invoking any issuer callback.
      e.busy++
      try {
        this.#pay(budget, 'base project get')
        const generation = current.viewGeneration
        const binding = Object.freeze({
          projectId: current.project.projectId,
          engineSessionId: current.engineSessionId,
          generation,
          selectionSeq: current.selectionSeq,
          projectRevision: current.project.projectRevision,
          inputSnapshotId: current.project.inputSnapshotId,
        })
        const pin = current.supervisor.issueQueryPin(
          current.owner,
          current.engineSessionId,
          () =>
            this.#live(current) &&
            this.tasks.queryViewGeneration(current.project.projectId, current.supervisor) ===
              generation,
          binding,
        )
        read = budget.existingProjectGet(binding)
        if (!(read instanceof QueryProjectReadTicket)) throw error('PERMISSION_DENIED')
        e.readResponsibility = read
        const operation = current.supervisor.requestQueryProjectGet(
          { projectId: current.project.projectId },
          pin,
          read,
          binding,
        )
        const value = await operation.catch((cause) => {
          throw this.#operationError(current, cause, operation)
        })
        if (
          !this.#live(current) ||
          !(current.supervisor.profile === 'business3'
            ? validateBusiness3('result_project.get', value)
            : validateV2('result_project.get', value)) ||
          !same(value, current.project)
        )
          throw error('IDENTITY_CONFLICT')
        this.#keep(e, { value: copy(value as WireRecord) })
        e.state = 'live'
        result = this.#result(e, {
          baseRef: e.ref,
          projectRevision: current.project.projectRevision,
          inputSnapshotId: current.project.inputSnapshotId,
        })
      } catch (cause) {
        failed = true
        throw cause
      } finally {
        e.busy--
        if (read instanceof QueryProjectReadTicket) {
          try {
            read.release()
            e.readResponsibility = undefined
            if (failed || e.state === 'retired') this.#drop(e)
          } catch (cleanup) {
            e.state = 'unknown'
            if (!failed) cleanupFailure = { cause: cleanup } // Keep the ticket and first cause.
          }
        } else this.#drop(e)
      }
      if (cleanupFailure) throw cleanupFailure.cause
      return result
    })
  }
  loadQueryDefinition(
    args: Parameters<QueryConsumerBridge['loadQueryDefinition']>[0],
  ): ReturnType<QueryConsumerBridge['loadQueryDefinition']> {
    return this.#run(async () => {
      const current = this.#current(),
        budget = this.#scope(current, args)
      this.#pay(budget, 'definition args')
      if (
        !z
          .object({
            definitionId: z.string().regex(/^[A-Za-z0-9_.-]{1,128}$/),
            selection: z.unknown(),
          })
          .strict()
          .safeParse(args).success
      )
        throw invalidParams()
      const params = { ...args, projectId: current.project.projectId }
      if (!validateV2('params_query.definition.load', params)) throw invalidParams()
      const e = this.#entry('load', current, budget)
      try {
        const expected: WireRecord = {
          projectId: current.project.projectId,
          definitionId: args.definitionId,
        }
        if (args.selection.kind === 'current')
          Object.assign(expected, {
            inputSnapshotId: current.project.inputSnapshotId,
            baseProjectRevision: current.project.projectRevision,
            definitionVersion: current.project.dependencyVector['query:' + args.definitionId],
          })
        const value = (await this.#wire(
          e,
          current,
          'query.definition.load',
          params,
          expected,
        )) as QueryDefinitionRecordDTO
        this.#keep(e, { value: copy(value) as unknown as WireRecord })
        e.state = 'live'
        return this.#result(e, copy({ ...value, loadRef: e.ref }) as QueryDefinitionLoadDTO)
      } catch (cause) {
        this.#drop(e)
        throw cause
      }
    })
  }
  executeSavedQuery(args: QueryExecuteArgs): ReturnType<QueryConsumerBridge['executeSavedQuery']> {
    return this.#run(async () => {
      const current = this.#current(),
        budget = this.#scope(current, args)
      this.#pay(budget, 'execute args')
      const parsed = z
        .object({ operationId: id, loadRef: id, visibleDraft: z.unknown(), selection: z.unknown() })
        .strict()
        .safeParse(args)
      const visible = parsed.success ? normalizeQueryDraft(args.visibleDraft) : null
      if (!parsed.success || !visible || !validateV2('query.consumer.selection', args.selection))
        throw invalidParams()
      args = copy({ ...args, visibleDraft: visible }) as QueryExecuteArgs
      let e = [...this.#entries.values()].find(
        (x) => x.kind === 'intent' && x.operationId === args.operationId,
      )
      if (e) {
        if (
          e.context.owner !== current.owner ||
          e.context.supervisor !== current.supervisor ||
          e.context.engineSessionId !== current.engineSessionId ||
          e.context.project.projectId !== current.project.projectId ||
          !same({ ...args, visibleDraft: visible }, e.intent)
        )
          throw error('IDENTITY_CONFLICT')
        // Retain an old accepted/UNKNOWN responsibility, but never replay or
        // transfer its request/watch into a successor view generation.
        if (e.context.viewGeneration !== current.viewGeneration) throw error('PERMISSION_DENIED')
      } else {
        const loaded = this.#ref(args.loadRef, 'load', current),
          record = loaded.value as unknown as QueryDefinitionRecordDTO
        if (record.kind !== 'managed' || !same(visible, record.draft)) throw error('INVALID_STATE')
        e = this.#entry('intent', current, budget)
        const binding = {
          definitionId: record.definitionId,
          definitionVersion: record.definitionVersion,
          definitionSha256: record.definitionSha256,
          descriptorVersion: record.descriptorVersion,
          descriptorSha256: record.descriptorSha256,
        }
        try {
          this.#keep(e, {
            operationId: args.operationId,
            intent: copy({ ...args, visibleDraft: visible }) as QueryExecuteArgs,
          })
          e.watch = this.tasks.reserveQueryWatch(current.project.projectId, current.supervisor)
          const prepared = (await this.#wire(e, current, 'query.execution.prepare', {
            projectId: current.project.projectId,
            operationId: args.operationId,
            definitionBinding: binding,
            visibleDraft: visible,
            selection: args.selection,
          })) as WireRecord
          if (!this.#live(current)) throw error('PERMISSION_DENIED')
          this.#keep(e, {
            executionIdentity: copy(prepared.executionIdentity) as QueryExecutionIdentityDTO,
            request: copy({
              projectId: current.project.projectId,
              operationId: args.operationId,
              capability: 'query.execute',
              input: prepared.input,
              confirmationRef: null,
            }),
          })
        } catch (cause) {
          this.#drop(e)
          throw cause
        }
      }
      if (e.busy) throw error('INVALID_STATE')
      if (!e.accepted) {
        let pin: object | undefined
        const expected = e.executionIdentity!
        e.busy++
        try {
          pin = current.supervisor.issueQueryPin(current.owner, current.engineSessionId, () =>
            this.#live(current),
          )
          const actual = current.supervisor.querySessionIdentity(pin)
          if (
            actual.registryHash !== expected.registryHash ||
            actual.engineVersion !== expected.implementation.engineVersion ||
            !same(actual.limits, expected.limits)
          )
            throw error('IDENTITY_CONFLICT')
          this.#pay(e.budget, 'original execute intent write/reply')
          const operation = current.supervisor.requestPinned('job.create', e.request!, pin)
          const accepted = (await operation.catch((cause) => {
            throw this.#operationError(current, cause, operation)
          })) as JobView
          e.writeEntered = !!pin && current.supervisor.queryWriteEntered(pin)
          // Persist genuine acceptance before checking whether its original view is still current.
          if (
            !(current.supervisor.profile === 'business3'
              ? validateBusiness3('job', accepted)
              : validateV2('job', accepted)) ||
            accepted.operationId !== args.operationId ||
            accepted.projectId !== current.project.projectId ||
            accepted.capability !== 'query.execute' ||
            !same(accepted.input, e.request!.input) ||
            !same(accepted.implementation, expected.implementation) ||
            !same(accepted.limits, expected.limits)
          )
            throw error('IDENTITY_CONFLICT')
          this.#keep(e, { accepted: copy(accepted) })
          e.state = 'live'
        } catch (cause) {
          e.writeEntered = !!pin && current.supervisor.queryWriteEntered(pin)
          if (e.writeEntered) e.state = 'unknown'
          else this.#drop(e)
          throw cause
        } finally {
          e.busy--
          if (e.state === 'retired') this.#drop(e)
          this.#fence()
        }
      }
      if (!this.#live(current)) throw error('PERMISSION_DENIED')
      let watched: BridgeResult<JobView>
      if (e.watch) {
        watched = await this.tasks.watchAcceptedQuery(e.watch, e.accepted!, current.supervisor)
        if (!this.tasks.queryWatchReserved(e.watch)) e.watch = undefined
      } else watched = await this.tasks.subscribeJob(e.accepted!.jobId)
      if (!this.#live(current)) throw error('PERMISSION_DENIED')
      // A real transfer into TaskService's original remembered book closes this
      // admission reservation; failed subscribe still retains the genuine Job.
      if (!e.watch) {
        e.state = 'live'
        e.context = current
      }
      const receipt: QueryExecutionReceiptDTO = {
        operationId: args.operationId,
        acceptedJob: e.accepted!,
        watch: watched.ok ? { state: 'subscribed' } : { state: 'pending', error: watched.error },
      }
      return this.#result(e, copy(receipt), current)
    })
  }
  getQueryResultDescriptor(args: {
    resultId: string
  }): ReturnType<QueryConsumerBridge['getQueryResultDescriptor']> {
    return this.#run(async () => {
      const current = this.#current(),
        budget = this.#scope(current, args)
      this.#pay(budget, 'describe args')
      if (!z.object({ resultId: id }).strict().safeParse(args).success) throw invalidParams()
      const e = this.#entry('descriptor', current, budget)
      try {
        const value = (await this.#wire(e, current, 'query.result.describe', {
          projectId: current.project.projectId,
          resultId: args.resultId,
        })) as QueryDescriptorWireDTO
        this.#keep(e, { value: copy(value) as unknown as WireRecord })
        e.state = 'live'
        this.#keep(e, { nextIndex: 0, nextUtf8Byte: 0, textDone: false, rowsDone: false })
        return this.#result(e, copy({ ...value, descriptorRef: e.ref }) as QueryDescriptorDTO)
      } catch (cause) {
        this.#drop(e)
        throw cause
      }
    })
  }
  getQueryExecutedTextPage(
    args: Parameters<QueryConsumerBridge['getQueryExecutedTextPage']>[0],
  ): ReturnType<QueryConsumerBridge['getQueryExecutedTextPage']> {
    return this.#page('text', args) as ReturnType<QueryConsumerBridge['getQueryExecutedTextPage']>
  }
  getQueryRowsPage(
    args: Parameters<QueryConsumerBridge['getQueryRowsPage']>[0],
  ): ReturnType<QueryConsumerBridge['getQueryRowsPage']> {
    return this.#page('rows', args) as ReturnType<QueryConsumerBridge['getQueryRowsPage']>
  }
  #page(
    kind: 'text' | 'rows',
    args: {
      descriptorRef: string
      cursor: string | null
      maxUtf8Bytes?: number
      pageSize?: number
    },
  ): Promise<BridgeResult<QueryRowsPageDTO | QueryTextPageDTO>> {
    return this.#run(async () => {
      const current = this.#current(),
        budget = this.#scope(current, args)
      this.#pay(budget, 'page args')
      const shape =
        kind === 'text'
          ? z
              .object({
                descriptorRef: id,
                cursor: id.nullable(),
                maxUtf8Bytes: z.number().int().min(4).max(32768),
              })
              .strict()
          : z
              .object({
                descriptorRef: id,
                cursor: id.nullable(),
                pageSize: z.number().int().min(1).max(200),
              })
              .strict()
      if (!shape.safeParse(args).success) throw invalidParams()
      args = copy(args)
      const e = this.#ref(args.descriptorRef, 'descriptor', current),
        flag = kind === 'text' ? 'textBusy' : 'rowsBusy'
      if (e[flag]) throw error('INVALID_STATE')
      const descriptor = e.value as unknown as QueryDescriptorWireDTO
      const expected: WireRecord = {
        query: descriptor.query,
        executedText: descriptor.executedText,
      }
      // null always names the initial page, never the terminal frontier. Keep
      // one frontier plus one last nonnull request per lane, flat in this Entry.
      // Older nonnull tokens remain engine-authenticated under the same complete
      // identity; validate their range/width without an unbounded cursor history.
      if (kind === 'text') {
        if (args.cursor === null) expected.nextUtf8Byte = 0
        else if (!e.textDone && args.cursor === e.textCursor) expected.nextUtf8Byte = e.nextUtf8Byte
        else if (args.cursor === e.lastTextCursor && args.maxUtf8Bytes === e.lastTextSize)
          expected.nextUtf8Byte = e.lastTextStart
      } else {
        if (args.cursor === null) expected.nextIndex = 0
        else if (!e.rowsDone && args.cursor === e.rowsCursor) expected.nextIndex = e.nextIndex
        else if (args.cursor === e.lastRowsCursor && args.pageSize === e.lastRowsSize)
          expected.nextIndex = e.lastRowsStart
      }
      e[flag] = true
      try {
        const method = kind === 'text' ? 'query.result.textPage' : 'query.result.rowsPage'
        const params = {
          binding: descriptor.identity,
          cursor: args.cursor,
          ...(kind === 'text' ? { maxUtf8Bytes: args.maxUtf8Bytes } : { pageSize: args.pageSize }),
        }
        const page = (await this.#wire(e, current, method, params, expected)) as
          QueryRowsPageDTO | QueryTextPageDTO
        if (!this.#live(current)) throw error('PERMISSION_DENIED')
        if (page.kind === 'rows') {
          for (const row of page.rows)
            if (
              row.rowKey !==
              createHash('sha256')
                .update(
                  JSON.stringify([page.identity.resultId, page.identity.payloadSha256, row.index]),
                )
                .digest('hex')
            )
              throw error('IDENTITY_CONFLICT')
          if (descriptor.query.kind !== 'SELECT') throw error('IDENTITY_CONFLICT')
          const start = page.rows[0]?.index ?? descriptor.query.rowCount
          this.#keep(e, {
            lastRowsCursor: args.cursor ?? undefined,
            lastRowsStart: start,
            lastRowsSize: args.pageSize,
            nextIndex: start + page.rows.length,
            rowsCursor: page.nextCursor ?? undefined,
            rowsDone: page.nextCursor === null,
          })
        } else {
          this.#keep(e, {
            lastTextCursor: args.cursor ?? undefined,
            lastTextStart: page.startUtf8Byte,
            lastTextSize: args.maxUtf8Bytes,
            nextUtf8Byte: page.startUtf8Byte + page.utf8Length,
            textCursor: page.nextCursor ?? undefined,
            textDone: page.nextCursor === null,
          })
        }
        return this.#result(e, copy(page))
      } finally {
        e[flag] = false
      }
    })
  }
  /** Trusted owner cleanup only. A failed/unknown actual bridge release keeps the record. */
  retryReadCleanup(): void {
    for (const e of this.#entries.values())
      if (e.readResponsibility && e.busy === 0) {
        try {
          e.readResponsibility.release()
          e.readResponsibility = undefined
          e.state = 'retired'
          this.#drop(e)
        } catch {
          e.state = 'unknown'
        }
      }
  }
  dispose(): void {
    if (!this.#disposed) {
      this.#disposed = true
      this.#release()
      this.#fence()
    }
    this.retryReadCleanup()
  }
}
