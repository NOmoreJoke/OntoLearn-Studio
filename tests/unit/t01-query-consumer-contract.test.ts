/** Definitions only in the SOURCE window. Explicit doubles are logic evidence only. */
import { describe, expect, it, vi } from 'vitest'
import { EventEmitter } from 'node:events'
import { PassThrough, Writable } from 'node:stream'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const processDouble = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn: processDouble.spawn }))
import {
  EngineError,
  EngineSupervisor,
  OrdinaryLibraryAuthority,
  OrdinaryLibraryTransport,
  OrdinaryRetentionBook,
  QueryMainReadBudget,
  QueryProjectReadTicket,
  type OrdinaryRetentionAccount,
  type EngineConnectionState,
} from '../../apps/desktop/src/main/engine'
import { OrdinaryProjectSource } from '../../apps/desktop/src/main/ordinary-project-source'
import { QueryDefinitionService } from '../../apps/desktop/src/main/query-definition-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import {
  matchesQueryConsumerResponse,
  matchesResponse,
  normalizeQueryDraft,
  validateV2,
} from '../../packages/contracts/src/v2'
import corpus from '../../packages/contracts/v2/fixtures.json'
import bindings from '../../packages/contracts/v2/binding-regressions.json'
import type { JobView, ProjectView, QueryDraftDTO } from '@ontolearn/contracts'

type RecordValue = Record<string, unknown>
const data = corpus.queryConsumer
const samples = data.samples
const sampleDraft = samples.draft as QueryDraftDTO
const clone = <T>(value: T): T => structuredClone(value)
function checkedJob(): JobView {
  const value: unknown = clone(samples.job)
  if (!validateV2('job', value)) throw Error('Invalid real Job fixture')
  return value as JobView
}
const id = (n: number) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
const denied = () =>
  new EngineError({
    code: 'PERMISSION_DENIED',
    messageKey: 'permission.denied',
    params: {},
    retryable: false,
  })
function deferred<T>() {
  let resolve!: (value: T) => void, reject!: (cause: unknown) => void
  const promise = new Promise<T>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
const tick = async () => {
  for (let i = 0; i < 8; i++) await Promise.resolve()
}
const shapeCases = corpus.cases.filter((c) => c.name.startsWith('query consumer '))

describe('query shared concrete corpus: 33 shape, 73 binding, 7 service association', () => {
  for (const c of shapeCases) it(c.name, () => expect(validateV2(c.schema, c.value)).toBe(c.valid))
  for (const c of bindings.queryConsumer)
    it(c.name, () => {
      const q = c.request,
        r = c.response
      expect(
        q.method === 'job.create'
          ? matchesResponse(q, r)
          : matchesQueryConsumerResponse(q, r, c.binding),
      ).toBe(c.valid)
    })
  for (const c of data.service)
    it(c.name + ' legal error is associated, service code checked separately', () => {
      expect(matchesQueryConsumerResponse(c.request, c.response)).toBe(true)
      expect(c.response.error.code).toBe(c.expectedCode)
      expect(c.response.error.params).toEqual(c.expectedParams)
    })
  it('D1 draft UTF16 and fixed trim differ from L2 presentation scalars', () => {
    expect(normalizeQueryDraft({ ...samples.draft, name: '😀'.repeat(64) })).not.toBeNull()
    expect(normalizeQueryDraft({ ...samples.draft, name: '😀'.repeat(64) + 'x' })).toBeNull()
    expect(normalizeQueryDraft({ ...samples.draft, name: '\u001c Query\ufeff' })?.name).toBe(
      'Query',
    )
    expect(normalizeQueryDraft({ ...samples.draft, sparql: '\ud800' })).toBeNull()
    expect(normalizeQueryDraft({ ...samples.draft, sparql: 'é' })?.sparql).toBe('é')
    expect(normalizeQueryDraft({ ...samples.draft, sparql: 'e\u0301' })?.sparql).toBe('e\u0301')
  })
})

class ReadTicket extends QueryProjectReadTicket {
  attaches: unknown[] = []
  releases = 0
  failure: unknown
  attachDispatch(value: unknown): void {
    this.attaches.push(value)
  }
  release(): void {
    if (this.failure) throw this.failure
    this.releases++
  }
}
class Budget extends QueryMainReadBudget {
  fees: unknown[] = []
  holding: unknown[] = []
  tickets: ReadTicket[] = []
  during: () => void = () => {}
  reserve(...value: [string, number, number, number]): void {
    this.fees.push(value)
    this.during()
  }
  beforeArguments(value: unknown): void {
    this.fees.push(['args', value])
  }
  handoff(value: unknown): void {
    this.holding.push(value)
  }
  existingProjectGet(): ReadTicket {
    const ticket = new ReadTicket()
    this.tickets.push(ticket)
    return ticket
  }
}
/** Synthetic transport: no actual IPC, Store, issuer, OS process, or physical budget. */
class Port extends OrdinaryLibraryTransport {
  readonly ownerId = id(11)
  readonly supervisor = new EngineSupervisor({
    packaged: false,
    appPath: '/fixture/no-engine',
    resourcesPath: '/fixture/no-engine',
  })
  readonly book = new OrdinaryRetentionBook()
  readonly accounts = this.book.pair()
  readonly listeners = new Set<(value: EngineConnectionState) => void>()
  session = id(2)
  claimSource(_owner: object): OrdinaryRetentionAccount {
    void _owner
    return this.accounts[1]
  }
  get engineSessionId(): string {
    return this.session
  }
  observe(listener: (value: EngineConnectionState) => void): () => void {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }
  async request(p: RecordValue): Promise<unknown> {
    if (p.op === 'choices') return { ...p, choices: [{ choiceRef: id(13), projectId: id(1) }] }
    if (p.op === 'release') return { ...p }
    const rest = { ...p }
    delete rest.choiceRef
    return { ...rest, leaseRef: id(14), project: project() }
  }
  disconnect(): void {
    for (const listener of this.listeners)
      listener({
        state: 'disconnected',
        generation: 1,
        engineSessionId: this.session,
        error: denied().error,
      })
  }
}
function project(): ProjectView {
  return {
    projectId: id(1),
    projectRevision: 1,
    inputSnapshotId: 'a'.repeat(64),
    dependencyVector: { 'facts:asserted': 1, 'query:Q1': 1 },
    formatVersion: 2,
  }
}
async function service(realTasks = false) {
  const port = new Port(),
    source = new OrdinaryProjectSource(port)
  const [choice] = await source.choices()
  expect((await source.open(choice)).ok).toBe(true)
  const budget = new Budget(),
    tasks = new TaskService(port.supervisor)
  // Only the read-budget and transport are doubles; these are never production grants.
  vi.spyOn(port.supervisor, 'queryReadBudget').mockReturnValue(budget)
  vi.spyOn(port.supervisor, 'issueQueryPin').mockImplementation(() => Object.freeze({}))
  vi.spyOn(port.supervisor, 'querySessionIdentity').mockReturnValue({
    engineSessionId: port.session,
    registryHash: samples.prepared.executionIdentity.registryHash,
    limits: samples.prepared.executionIdentity.limits,
    engineVersion: samples.prepared.executionIdentity.implementation.engineVersion,
  })
  vi.spyOn(port.supervisor, 'queryWriteEntered').mockReturnValue(false)
  const watch = new Set<object>()
  if (realTasks) {
    // Actual TaskService generation, reservation and watch code. Only its engine
    // I/O is synthetic; this is not a Store/issuer/OS-worker integration proof.
    vi.spyOn(port.supervisor, 'engineSessionId', 'get').mockReturnValue(port.session)
    tasks.selectProject(id(1))
    tasks.attachView(() => {})
    vi.spyOn(port.supervisor, 'request').mockImplementation(async (method, p) => {
      if (method === 'job.get') return clone(samples.job)
      if (method === 'job.subscribe')
        return { subscriptionId: id(77), seq: 0, stateVersion: samples.job.stateVersion }
      if (method === 'job.unsubscribe')
        return { subscriptionId: p.subscriptionId, unsubscribed: true }
      throw denied()
    })
  } else {
    vi.spyOn(tasks, 'queryViewGeneration').mockReturnValue(1)
    vi.spyOn(tasks, 'reserveQueryWatch').mockImplementation(() => {
      const t = {}
      watch.add(t)
      return t
    })
    vi.spyOn(tasks, 'releaseQueryWatch').mockImplementation((t) => {
      watch.delete(t)
    })
    vi.spyOn(tasks, 'queryWatchReserved').mockImplementation((t) => watch.has(t))
    vi.spyOn(tasks, 'watchAcceptedQuery').mockImplementation(async (t, job) => {
      watch.delete(t)
      return { ok: true, data: job }
    })
  }
  const send = vi.spyOn(port.supervisor, 'requestPinned').mockImplementation(async (method) => {
    if (method === 'query.definition.load') return clone(samples.managed)
    if (method === 'query.execution.prepare') return clone(samples.prepared)
    if (method === 'query.result.describe') return clone(samples.descriptor)
    if (method === 'query.result.textPage') return clone(samples.text)
    if (method === 'query.result.rowsPage') return clone(samples.rows)
    if (method === 'job.create') return clone(samples.job)
    throw denied()
  })
  const query = new QueryDefinitionService(source, tasks)
  return { port, source, budget, tasks, query, send, watch }
}
async function loaded(s: Awaited<ReturnType<typeof service>>) {
  const result = await s.query.loadQueryDefinition({
    definitionId: 'Q1',
    selection: { kind: 'current' },
  })
  expect(result.ok).toBe(true)
  if (!result.ok || result.data.kind !== 'managed') throw Error('fixture load')
  return result.data
}

describe('main lifecycle with finite explicit doubles', () => {
  it('missing original issuer denies without Store/transport', async () => {
    const s = await service()
    vi.spyOn(s.port.supervisor, 'queryReadBudget').mockImplementation(() => {
      throw denied()
    })
    expect(
      (await s.query.loadQueryDefinition({ definitionId: 'Q1', selection: { kind: 'current' } }))
        .ok,
    ).toBe(false)
    expect(s.send).not.toHaveBeenCalled()
    s.query.dispose()
  })
  it('malformed args are rejected before a request and stored A is never replaced by B', async () => {
    const s = await service(),
      record = await loaded(s)
    s.send.mockClear()
    const changed = { ...sampleDraft, sparql: 'ASK {}' }
    const result = await s.query.executeSavedQuery({
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: changed,
      selection: { kind: 'current' },
    })
    expect(result).toMatchObject({ ok: false, error: { code: 'INVALID_STATE' } })
    expect(s.send).not.toHaveBeenCalled()
    expect(s.watch.size).toBe(0)
    s.query.dispose()
  })
  it('combined sixteen includes base/load/descriptor/intent', async () => {
    const s = await service()
    for (let i = 0; i < 16; i++)
      expect(
        (await s.query.loadQueryDefinition({ definitionId: 'Q1', selection: { kind: 'current' } }))
          .ok,
      ).toBe(true)
    expect(await s.query.getQueryResultDescriptor({ resultId: id(6) })).toMatchObject({
      ok: false,
      error: { code: 'INVALID_STATE' },
    })
    s.query.dispose()
  })
  it('base uses real project.get purpose ticket and checks actual returned project', async () => {
    const s = await service()
    const get = vi.spyOn(s.port.supervisor, 'requestQueryProjectGet').mockResolvedValue(project())
    const result = await s.query.getQueryDefinitionBase()
    expect(result.ok).toBe(true)
    expect(get).toHaveBeenCalledTimes(1)
    const [, pin, ticket, binding] = get.mock.calls[0]
    expect(pin).toBeTruthy()
    expect(ticket).toBe(s.budget.tickets[0])
    expect(binding).toMatchObject({
      generation: 1,
      selectionSeq: s.source.current()!.selectionSeq,
      projectRevision: 1,
    })
    expect(s.budget.tickets[0].releases).toBe(1)
    s.query.dispose()
  })
  it('base release unknown retains exact ticket and original failed result', async () => {
    const s = await service(),
      first = denied()
    vi.spyOn(s.port.supervisor, 'requestQueryProjectGet').mockRejectedValue(first)
    vi.spyOn(s.port.supervisor, 'projectFailure').mockReturnValue(first.error)
    const original = s.budget.existingProjectGet.bind(s.budget)
    vi.spyOn(s.budget, 'existingProjectGet').mockImplementation(() => {
      const t = original()
      t.failure = Error('unknown release')
      return t
    })
    expect(await s.query.getQueryDefinitionBase()).toMatchObject({
      ok: false,
      error: { code: 'PERMISSION_DENIED' },
    })
    expect(s.query.hasOutstanding).toBe(true)
    s.budget.tickets[0].failure = undefined
    s.query.retryReadCleanup()
    expect(s.budget.tickets[0].releases).toBe(1)
    expect(s.query.hasOutstanding).toBe(false)
    s.query.dispose()
  })
  it('caller mutation cannot change the captured historical request across await', async () => {
    const s = await service(),
      wait = deferred<unknown>()
    s.send.mockReturnValueOnce(wait.promise)
    const args = {
      definitionId: 'Q1',
      selection: { kind: 'historical' as const, snapshotId: 'a'.repeat(64) },
    }
    const pending = s.query.loadQueryDefinition(args)
    args.selection.snapshotId = 'b'.repeat(64)
    expect((s.send.mock.calls[0][1].selection as RecordValue).snapshotId).toBe('a'.repeat(64))
    wait.resolve(clone(samples.managed))
    expect((await pending).ok).toBe(true)
    s.query.dispose()
  })
  it('late load after fence cannot issue a usable handle', async () => {
    const s = await service(),
      wait = deferred<unknown>()
    s.send.mockReturnValueOnce(wait.promise)
    const pending = s.query.loadQueryDefinition({
      definitionId: 'Q1',
      selection: { kind: 'current' },
    })
    await tick()
    s.port.disconnect()
    wait.resolve(clone(samples.managed))
    expect((await pending).ok).toBe(false)
    s.query.dispose()
  })
  it('ACK unknown exact retry reuses original job.create material and operation', async () => {
    const s = await service(),
      record = await loaded(s),
      requests: RecordValue[] = []
    vi.spyOn(s.port.supervisor, 'queryWriteEntered').mockReturnValue(true)
    let lose = true
    s.send.mockImplementation(async (method, p) => {
      if (method === 'query.execution.prepare') return clone(samples.prepared)
      if (method === 'job.create') {
        requests.push(clone(p))
        if (lose) {
          lose = false
          throw denied()
        }
        return clone(samples.job)
      }
      throw Error(method)
    })
    const args = {
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: clone(sampleDraft),
      selection: { kind: 'current' } as const,
    }
    expect((await s.query.executeSavedQuery(args)).ok).toBe(false)
    expect(s.query.hasOutstanding).toBe(true)
    expect((await s.query.executeSavedQuery(args)).ok).toBe(true)
    expect(requests).toHaveLength(2)
    expect(requests[1]).toEqual(requests[0])
    expect(s.send.mock.calls.filter((c) => c[0] === 'query.execution.prepare')).toHaveLength(1)
    expect(s.watch.size).toBe(0)
    s.query.dispose()
  })
  it('same operation with changed visible material is rejected during unknown recovery', async () => {
    const s = await service(),
      record = await loaded(s)
    vi.spyOn(s.port.supervisor, 'queryWriteEntered').mockReturnValue(true)
    s.send.mockImplementation(async (method) => {
      if (method === 'query.execution.prepare') return clone(samples.prepared)
      throw denied()
    })
    const args = {
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: clone(sampleDraft),
      selection: { kind: 'current' } as const,
    }
    await s.query.executeSavedQuery(args)
    const before = s.send.mock.calls.length
    expect(
      await s.query.executeSavedQuery({
        ...args,
        visibleDraft: { ...args.visibleDraft, description: 'B' },
      }),
    ).toMatchObject({ ok: false, error: { code: 'IDENTITY_CONFLICT' } })
    expect(s.send.mock.calls.length).toBe(before)
    s.query.dispose()
  })
  it('actual accepted job with subscription failure stays accepted, retry never recreates', async () => {
    const s = await service(),
      record = await loaded(s)
    vi.spyOn(s.tasks, 'watchAcceptedQuery').mockResolvedValue({ ok: false, error: denied().error })
    const args = {
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: clone(sampleDraft),
      selection: { kind: 'current' } as const,
    }
    const first = await s.query.executeSavedQuery(args)
    expect(first).toMatchObject({
      ok: true,
      data: { acceptedJob: { jobId: id(3) }, watch: { state: 'pending' } },
    })
    await s.query.executeSavedQuery(args)
    expect(s.send.mock.calls.filter((c) => c[0] === 'job.create')).toHaveLength(1)
    s.query.dispose()
  })
  it('pages pin descriptor and lanes; no SELECT reconstruction from evidence leaves', async () => {
    const s = await service(),
      result = await s.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!result.ok) throw Error('descriptor fixture')
    const page = await s.query.getQueryRowsPage({
      descriptorRef: result.data.descriptorRef,
      pageSize: 2,
      cursor: null,
    })
    expect(page.ok).toBe(true)
    expect(s.send.mock.calls.at(-1)?.[0]).toBe('query.result.rowsPage')
    s.query.dispose()
  })
})

/** Real Supervisor state machine, but in-memory stdio. Not an OS/worker proof. */
class MemoryChild extends EventEmitter {
  stdout = new PassThrough()
  stderr = new PassThrough()
  stdin: Writable
  exitCode: number | null = null
  signalCode: NodeJS.Signals | null = null
  calls: RecordValue[] = []
  spawnNotifications = 0
  ordinaryAcquire?: RecordValue
  ordinaryCommitAck?: RecordValue
  constructor(
    readonly session: string,
    readonly registryHash: string,
  ) {
    super()
    this.stdin = new Writable({
      write: (bytes, _encoding, done) => {
        const q = JSON.parse(bytes.toString()) as RecordValue
        this.calls.push(q)
        const p = q.params as RecordValue
        let result: unknown
        if (q.method === 'hello')
          result = {
            selectedVersion: 2,
            engineVersion: '0.1.0',
            engineSessionId: session,
            capabilities: ['health', 'session.ping', 'ordinary.library', 'query.definition.load'],
            registryHash,
            limits: clone(samples.prepared.executionIdentity.limits),
          }
        else if (q.method === 'health') result = { status: 'ok', engineVersion: '0.1.0' }
        else if (q.method === 'ordinary.library' && p.op === 'choices')
          result = { ...p, choices: [{ choiceRef: id(13), projectId: id(1) }] }
        else if (q.method === 'ordinary.library' && p.op === 'acquire') {
          const rest = { ...p }
          delete rest.choiceRef
          this.ordinaryAcquire = { ...rest, leaseRef: id(14), project: project() }
          result = this.ordinaryAcquire
        } else if (q.method === 'ordinary.library' && p.op === 'commit') {
          const acquired = this.ordinaryAcquire
          if (
            !acquired ||
            p.ownerId !== acquired.ownerId ||
            p.actionId !== acquired.actionId ||
            p.actionSeq !== acquired.actionSeq ||
            p.leaseRef !== acquired.leaseRef
          )
            throw Error('fixture commit must bind original acquire')
          this.ordinaryCommitAck = {
            op: 'commit',
            ownerId: p.ownerId,
            actionId: p.actionId,
            actionSeq: p.actionSeq,
            leaseRef: p.leaseRef,
            project: clone(acquired.project),
          }
          result = this.ordinaryCommitAck
        } else if (q.method === 'query.definition.load') result = clone(samples.managed)
        else result = { ...p }
        queueMicrotask(() =>
          this.stdout.write(
            JSON.stringify({
              kind: 'response',
              protocolVersion: 2,
              id: q.id,
              method: q.method,
              engineSessionId: session,
              ok: true,
              result,
            }) + '\n',
          ),
        )
        done()
      },
    })
  }
  notifySpawn(): void {
    if (this.spawnNotifications) throw Error('duplicate fixture spawn')
    this.spawnNotifications++
    this.emit('spawn')
  }
  kill(): boolean {
    this.exitCode = 0
    queueMicrotask(() => this.emit('close', 0))
    return true
  }
}
class Authority extends OrdinaryLibraryAuthority {
  allows(): boolean {
    return true
  }
}
async function realSupervisor() {
  const registryPath = fileURLToPath(
    new URL('../../packages/contracts/v2/registry.json', import.meta.url),
  )
  const hash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
  const child = new MemoryChild(id(2), hash)
  processDouble.spawn.mockReset().mockImplementationOnce(() => {
    // Queue only when the actual Supervisor calls spawn, not when this fixture
    // object is constructed before the async #ensure path installs listeners.
    queueMicrotask(() => child.notifySpawn())
    return child
  })
  const supervisor = new EngineSupervisor(
    { packaged: false, appPath: '/fixture/no-engine', resourcesPath: '/fixture/no-engine' },
    {
      registryPath,
      ordinaryLibrary: { ownerId: id(11), authority: new Authority() },
      command: { command: '/in-memory/engine', args: [] },
    },
  )
  const source = new OrdinaryProjectSource(supervisor.ordinaryLibraryClient())
  const [choice] = await source.choices()
  expect(choice.projectId).toBe(id(1))
  const opened = await source.open(choice)
  expect(opened).toEqual({ ok: true, data: project() })
  const ordinaryCalls = child.calls.filter((q) => q.method === 'ordinary.library')
  expect(ordinaryCalls.map((q) => (q.params as RecordValue).op)).toEqual([
    'choices',
    'acquire',
    'commit',
  ])
  const committed = ordinaryCalls[2].params as RecordValue
  expect(validateV2('result_ordinary.library', child.ordinaryAcquire)).toBe(true)
  expect(validateV2('result_ordinary.library', child.ordinaryCommitAck)).toBe(true)
  expect(child.ordinaryCommitAck).toEqual({
    op: 'commit',
    ownerId: committed.ownerId,
    actionId: committed.actionId,
    actionSeq: committed.actionSeq,
    leaseRef: committed.leaseRef,
    project: project(),
  })
  expect(child.ordinaryCommitAck?.project).toEqual(child.ordinaryAcquire?.project)
  expect(source.current()?.project).toEqual(project())
  expect(child.spawnNotifications).toBe(1)
  expect(child.calls[0].method).toBe('hello')
  expect(supervisor.engineSessionId).toBe(id(2))
  return { supervisor, source, child }
}

describe('inside actual Supervisor await-ensure fences with in-memory process', () => {
  it('owner fence after operation scheduling but before send makes zero new write', async () => {
    const s = await realSupervisor(),
      current = s.source.current()!
    let live = true,
      checks = 0
    const pin = s.supervisor.issueQueryPin(current.owner, current.engineSessionId, () => {
      checks++
      return live
    })
    const count = s.child.calls.length
    const pending = s.supervisor.requestPinned(
      'query.definition.load',
      clone(samples.params['query.definition.load']),
      pin,
    )
    await Promise.resolve() // Initial pin check ran; #ensure's await continuation has not.
    expect(checks).toBeGreaterThanOrEqual(2)
    live = false
    await expect(pending).rejects.toBeInstanceOf(EngineError)
    expect(s.child.calls.length).toBe(count)
    await s.supervisor.stop()
  })
  it('foreign pin and disposed original source cannot be reused', async () => {
    const s = await realSupervisor()
    await expect(
      s.supervisor.requestPinned(
        'query.definition.load',
        clone(samples.params['query.definition.load']),
        {},
      ),
    ).rejects.toBeInstanceOf(EngineError)
    const current = s.source.current()!,
      pin = s.supervisor.issueQueryPin(
        current.owner,
        current.engineSessionId,
        () => s.source.current() === current,
      )
    s.source.dispose()
    await expect(
      s.supervisor.requestPinned(
        'query.definition.load',
        clone(samples.params['query.definition.load']),
        pin,
      ),
    ).rejects.toBeInstanceOf(EngineError)
    await s.supervisor.stop()
  })
  it('base requires original bound purpose and denies a fieldwise foreign binding', async () => {
    const s = await realSupervisor(),
      current = s.source.current()!,
      binding = {
        projectId: id(1),
        engineSessionId: id(2),
        generation: 1,
        selectionSeq: current.selectionSeq,
        projectRevision: 1,
        inputSnapshotId: 'a'.repeat(64),
      }
    const pin = s.supervisor.issueQueryPin(
      current.owner,
      current.engineSessionId,
      () => s.source.current() === current,
      binding,
    )
    const read = new ReadTicket(),
      count = s.child.calls.length
    await expect(
      s.supervisor.requestQueryProjectGet({ projectId: id(1) }, pin, read, {
        ...binding,
        generation: 2,
      }),
    ).rejects.toBeInstanceOf(EngineError)
    expect(read.attaches).toHaveLength(0)
    expect(s.child.calls.length).toBe(count)
    await s.supervisor.stop()
  })
  it('synchronous dispatch-attachment revocation is checked before actual write', async () => {
    const s = await realSupervisor(),
      current = s.source.current()!,
      binding = {
        projectId: id(1),
        engineSessionId: id(2),
        generation: 1,
        selectionSeq: current.selectionSeq,
        projectRevision: 1,
        inputSnapshotId: 'a'.repeat(64),
      }
    let live = true
    const pin = s.supervisor.issueQueryPin(
      current.owner,
      current.engineSessionId,
      () => live,
      binding,
    )
    const read = new ReadTicket(),
      count = s.child.calls.length
    vi.spyOn(read, 'attachDispatch').mockImplementation(() => {
      live = false
    })
    await expect(
      s.supervisor.requestQueryProjectGet({ projectId: id(1) }, pin, read, binding),
    ).rejects.toBeInstanceOf(EngineError)
    expect(read.attachDispatch).toHaveBeenCalledTimes(1)
    expect(s.supervisor.queryWriteEntered(pin)).toBe(false)
    expect(s.child.calls.length).toBe(count)
    s.supervisor.stop()
  })
})

describe('R2 main page retry state with finite authenticated-I/O doubles', () => {
  it('both complete single-page lanes accept exact initial-null retries', async () => {
    const s = await service(),
      descriptor = await s.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!descriptor.ok) throw Error('descriptor fixture')
    const rows = { descriptorRef: descriptor.data.descriptorRef, pageSize: 2, cursor: null }
    const text = { descriptorRef: descriptor.data.descriptorRef, maxUtf8Bytes: 32768, cursor: null }
    const a = await s.query.getQueryRowsPage(rows),
      b = await s.query.getQueryRowsPage(rows)
    expect(a.ok).toBe(true)
    expect(b).toEqual(a)
    const c = await s.query.getQueryExecutedTextPage(text),
      d = await s.query.getQueryExecutedTextPage(text)
    expect(c.ok).toBe(true)
    expect(d).toEqual(c)
    s.query.dispose()
  })
  it('both lanes restart after terminal and retry last and older nonnull cursors without a growing main cursor book', async () => {
    const s = await service(),
      desc = clone(samples.descriptor),
      text = samples.text.text
    desc.query.rowCount = 4
    const rows = Array.from({ length: 4 }, (_, index) => ({
      index,
      rowKey: createHash('sha256')
        .update(JSON.stringify([desc.identity.resultId, desc.identity.payloadSha256, index]))
        .digest('hex'),
      cells: clone(samples.rows.rows[0].cells),
    }))
    const rowPositions: Record<string, number> = { [id(201)]: 1, [id(202)]: 2, [id(203)]: 3 }
    const textPositions: Record<string, number> = {}
    for (let start = 8; start < text.length; start += 8) textPositions[id(300 + start)] = start
    s.send.mockImplementation(async (method, p) => {
      if (method === 'query.result.describe') return clone(desc)
      if (method === 'query.result.rowsPage') {
        const start = p.cursor === null ? 0 : rowPositions[String(p.cursor)]
        if (start === undefined) throw denied()
        return {
          identity: clone(desc.identity),
          kind: 'rows',
          order: 'query-index:asc',
          rows: clone(rows.slice(start, start + 1)),
          nextCursor: start + 1 < 4 ? id(201 + start) : null,
        }
      }
      if (method === 'query.result.textPage') {
        const start = p.cursor === null ? 0 : textPositions[String(p.cursor)]
        if (start === undefined) throw denied()
        const stop = Math.min(text.length, start + 8),
          part = text.slice(start, stop)
        return {
          identity: clone(desc.identity),
          kind: 'text',
          order: 'utf8-byte:asc',
          startUtf8Byte: start,
          utf8Length: Buffer.byteLength(part, 'utf8'),
          text: part,
          nextCursor: stop < text.length ? id(300 + stop) : null,
        }
      }
      throw Error(method)
    })
    const descriptor = await s.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!descriptor.ok) throw Error('descriptor fixture')
    const ref = descriptor.data.descriptorRef
    async function row(cursor: string | null) {
      const result = await s.query.getQueryRowsPage({ descriptorRef: ref, pageSize: 1, cursor })
      if (!result.ok) throw Error(JSON.stringify(result.error))
      return result.data
    }
    async function page(cursor: string | null) {
      const result = await s.query.getQueryExecutedTextPage({
        descriptorRef: ref,
        maxUtf8Bytes: 8,
        cursor,
      })
      if (!result.ok) throw Error(JSON.stringify(result.error))
      return result.data
    }
    let cursor: string | null = null
    for (let i = 0; i < 4; i++) {
      const result = await row(cursor)
      expect(result.rows[0].index).toBe(i)
      cursor = result.nextCursor
    }
    expect(cursor).toBeNull()
    expect((await row(id(203))).rows[0].index).toBe(3) // terminal nonnull exact retry
    expect((await row(id(201))).rows[0].index).toBe(1) // older than frontier and last memo
    expect((await row(id(201))).rows[0].index).toBe(1)
    expect((await row(null)).rows[0].index).toBe(0)
    expect((await row(id(201))).rows[0].index).toBe(1) // actual start, never cumulative old index
    const parts: string[] = []
    cursor = null
    let last: string | null = null
    for (let i = 0; i < 8; i++) {
      const result = await page(cursor)
      parts.push(result.text)
      last = cursor
      cursor = result.nextCursor
      if (cursor === null) break
    }
    expect(cursor).toBeNull()
    expect(parts.join('')).toBe(text)
    expect(createHash('sha256').update(parts.join(''), 'utf8').digest('hex')).toBe(
      desc.executedText.sha256,
    )
    if (last !== null) expect((await page(last)).nextCursor).toBeNull()
    expect((await page(id(308))).startUtf8Byte).toBe(8)
    expect((await page(id(308))).startUtf8Byte).toBe(8)
    expect((await page(null)).startUtf8Byte).toBe(0)
    expect((await page(id(308))).startUtf8Byte).toBe(8)
    s.query.dispose()
  })
  it('a known issued frontier still rejects a discontinuous row response', async () => {
    const s = await service(),
      desc = clone(samples.descriptor)
    let count = 0
    s.send.mockImplementation(async (method) => {
      if (method === 'query.result.describe') return clone(desc)
      if (method === 'query.result.rowsPage') {
        count++
        return {
          identity: clone(desc.identity),
          kind: 'rows',
          order: 'query-index:asc',
          rows: [clone(samples.rows.rows[0])],
          nextCursor: count === 1 ? id(201) : id(202),
        }
      }
      throw Error(method)
    })
    const descriptor = await s.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!descriptor.ok) throw Error('descriptor fixture')
    expect(
      (
        await s.query.getQueryRowsPage({
          descriptorRef: descriptor.data.descriptorRef,
          pageSize: 1,
          cursor: null,
        })
      ).ok,
    ).toBe(true)
    expect(
      await s.query.getQueryRowsPage({
        descriptorRef: descriptor.data.descriptorRef,
        pageSize: 1,
        cursor: id(201),
      }),
    ).toMatchObject({ ok: false, error: { code: 'IDENTITY_CONFLICT' } })
    s.query.dispose()
  })
})

describe('R2 actual TaskService generation with finite engine/issuer I/O doubles', () => {
  it('same-project attachView invalidates old load and descriptor refs without changing ordinary selection', async () => {
    const s = await service(true),
      record = await loaded(s),
      descriptor = await s.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!descriptor.ok) throw Error('descriptor fixture')
    const current = s.source.current(),
      generation = s.tasks.queryViewGeneration(id(1), s.port.supervisor)
    s.tasks.attachView(() => {})
    expect(s.source.current()).toBe(current)
    expect(s.tasks.queryViewGeneration(id(1), s.port.supervisor)).toBe(generation + 1)
    s.send.mockClear()
    expect(
      await s.query.executeSavedQuery({
        operationId: id(4),
        loadRef: record.loadRef,
        visibleDraft: clone(sampleDraft),
        selection: { kind: 'current' },
      }),
    ).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    expect(
      await s.query.getQueryRowsPage({
        descriptorRef: descriptor.data.descriptorRef,
        pageSize: 2,
        cursor: null,
      }),
    ).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    expect(s.send).not.toHaveBeenCalled()
    s.query.dispose()
  })
  it('late prepare after a real view replacement makes no job.create and releases only its known-unsent watch reservation', async () => {
    const s = await service(true),
      record = await loaded(s),
      wait = deferred<unknown>()
    const reserve = vi.spyOn(s.tasks, 'reserveQueryWatch')
    s.send.mockImplementation(async (method) => {
      if (method === 'query.execution.prepare') return wait.promise
      throw Error(method)
    })
    const pending = s.query.executeSavedQuery({
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: clone(sampleDraft),
      selection: { kind: 'current' },
    })
    await tick()
    expect(reserve).toHaveBeenCalledTimes(1)
    const token = reserve.mock.results[0].value
    s.tasks.attachView(() => {})
    wait.resolve(clone(samples.prepared))
    expect(await pending).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    expect(s.send.mock.calls.some((c) => c[0] === 'job.create')).toBe(false)
    expect(s.tasks.queryWatchReserved(token)).toBe(false)
    s.query.dispose()
  })
  it('accepted ACK after view replacement stays owned and is neither watched in the successor nor recreated', async () => {
    const s = await service(true),
      record = await loaded(s),
      wait = deferred<unknown>()
    const reserve = vi.spyOn(s.tasks, 'reserveQueryWatch'),
      watch = vi.spyOn(s.tasks, 'watchAcceptedQuery')
    vi.spyOn(s.port.supervisor, 'queryWriteEntered').mockReturnValue(true)
    s.send.mockImplementation(async (method) => {
      if (method === 'query.execution.prepare') return clone(samples.prepared)
      if (method === 'job.create') return wait.promise
      throw Error(method)
    })
    const args = {
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: clone(sampleDraft),
      selection: { kind: 'current' } as const,
    }
    const pending = s.query.executeSavedQuery(args)
    await tick()
    expect(s.send.mock.calls.filter((c) => c[0] === 'job.create')).toHaveLength(1)
    const token = reserve.mock.results[0].value
    s.tasks.attachView(() => {})
    wait.resolve(clone(samples.job))
    expect(await pending).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    expect(watch).not.toHaveBeenCalled()
    expect(s.tasks.queryWatchReserved(token)).toBe(true)
    expect(s.query.hasOutstanding).toBe(true)
    expect(await s.query.executeSavedQuery(args)).toMatchObject({
      ok: false,
      error: { code: 'PERMISSION_DENIED' },
    })
    expect(s.send.mock.calls.filter((c) => c[0] === 'job.create')).toHaveLength(1)
    expect(s.tasks.queryWatchReserved(token)).toBe(true)
    s.query.dispose()
  })
  it('write UNKNOWN survives real view replacement and still counts in the combined sixteen', async () => {
    const s = await service(true),
      record = await loaded(s),
      wait = deferred<unknown>()
    const reserve = vi.spyOn(s.tasks, 'reserveQueryWatch')
    vi.spyOn(s.port.supervisor, 'queryWriteEntered').mockReturnValue(true)
    vi.spyOn(s.port.supervisor, 'projectFailure').mockReturnValue(denied().error)
    s.send.mockImplementation(async (method) => {
      if (method === 'query.execution.prepare') return clone(samples.prepared)
      if (method === 'job.create') return wait.promise
      if (method === 'query.definition.load') return clone(samples.managed)
      throw Error(method)
    })
    const pending = s.query.executeSavedQuery({
      operationId: id(4),
      loadRef: record.loadRef,
      visibleDraft: clone(sampleDraft),
      selection: { kind: 'current' },
    })
    await tick()
    expect(s.send.mock.calls.filter((c) => c[0] === 'job.create')).toHaveLength(1)
    const token = reserve.mock.results[0].value
    s.tasks.attachView(() => {})
    wait.reject(denied())
    expect((await pending).ok).toBe(false)
    expect(s.tasks.queryWatchReserved(token)).toBe(true)
    expect(s.query.hasOutstanding).toBe(true)
    for (let i = 0; i < 15; i++)
      expect(
        (await s.query.loadQueryDefinition({ definitionId: 'Q1', selection: { kind: 'current' } }))
          .ok,
      ).toBe(true)
    expect(
      await s.query.loadQueryDefinition({ definitionId: 'Q1', selection: { kind: 'current' } }),
    ).toMatchObject({ ok: false, error: { code: 'INVALID_STATE' } })
    expect(s.tasks.queryWatchReserved(token)).toBe(true)
    s.query.dispose()
  })
  it('actual stale-generation watch reservation refuses transfer and retains the exact accepted responsibility', async () => {
    const s = await service(true),
      token = s.tasks.reserveQueryWatch(id(1), s.port.supervisor)
    const get = vi.spyOn(s.port.supervisor, 'request')
    get.mockClear()
    s.tasks.attachView(() => {})
    expect(await s.tasks.watchAcceptedQuery(token, checkedJob(), s.port.supervisor)).toMatchObject({
      ok: false,
      error: { code: 'PERMISSION_DENIED' },
    })
    expect(s.tasks.queryWatchReserved(token)).toBe(true)
    expect(get).not.toHaveBeenCalled()
    s.query.dispose()
  })
  it('view change during a real watch await keeps the Job in the original remembered book', async () => {
    const s = await service(true),
      wait = deferred<unknown>(),
      token = s.tasks.reserveQueryWatch(id(1), s.port.supervisor)
    const io = vi.spyOn(s.port.supervisor, 'request').mockImplementation(async (method) => {
      if (method === 'job.get') return wait.promise
      throw Error('unexpected I/O after old generation: ' + method)
    })
    const pending = s.tasks.watchAcceptedQuery(token, checkedJob(), s.port.supervisor)
    expect(s.tasks.queryWatchReserved(token)).toBe(false) // transferred, not released/unaccepted
    s.tasks.attachView(() => {})
    wait.resolve(clone(samples.job))
    expect(await pending).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    expect(io.mock.calls.some((c) => c[0] === 'job.subscribe' || c[0] === 'job.cancel')).toBe(false)
    for (let i = 0; i < 15; i++) s.tasks.reserveQueryWatch(id(1), s.port.supervisor)
    expect(() => s.tasks.reserveQueryWatch(id(1), s.port.supervisor)).toThrow('RESOURCE_LIMIT')
    s.query.dispose()
  })
  it('the outer reply await also fences a view replacement queued during handoff', async () => {
    const s = await service(true),
      handoff = s.budget.handoff.bind(s.budget)
    vi.spyOn(s.budget, 'handoff').mockImplementation((value) => {
      handoff(value)
      queueMicrotask(() => s.tasks.attachView(() => {}))
    })
    expect(
      await s.query.loadQueryDefinition({ definitionId: 'Q1', selection: { kind: 'current' } }),
    ).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    s.query.dispose()
  })
})

describe('R2 actual Supervisor send fence uses actual TaskService view generation', () => {
  it('same owner/project/session with a successor view after initial check makes zero query writes', async () => {
    const s = await realSupervisor(),
      tasks = new TaskService(s.supervisor)
    tasks.selectProject(id(1))
    tasks.attachView(() => {})
    const current = s.source.current()!,
      generation = tasks.queryViewGeneration(id(1), s.supervisor)
    let checks = 0
    const pin = s.supervisor.issueQueryPin(current.owner, current.engineSessionId, () => {
      checks++
      return (
        s.source.current() === current &&
        tasks.queryViewGeneration(id(1), s.supervisor) === generation
      )
    })
    const count = s.child.calls.length
    const pending = s.supervisor.requestPinned(
      'query.definition.load',
      clone(samples.params['query.definition.load']),
      pin,
    )
    await Promise.resolve()
    expect(checks).toBeGreaterThanOrEqual(2)
    tasks.attachView(() => {})
    expect(s.source.current()).toBe(current)
    await expect(pending).rejects.toBeInstanceOf(EngineError)
    expect(s.child.calls.length).toBe(count)
    expect(s.supervisor.queryWriteEntered(pin)).toBe(false)
    tasks.dispose()
    s.supervisor.stop()
  })
})

describe('R2 older opaque cursor authority remains engine-owned', () => {
  it('cross-lane and changed-size requests preserve actual cursor service errors, not false wire mismatch', async () => {
    const s = await service(),
      desc = clone(samples.descriptor)
    const mismatch = () =>
      new EngineError({
        code: 'CURSOR_MISMATCH',
        messageKey: 'result.cursorMismatch',
        params: {},
        retryable: false,
      })
    // Explicit synthetic error projection; not an attestation from a real child.
    vi.spyOn(s.port.supervisor, 'projectFailure').mockImplementation((cause) =>
      cause instanceof EngineError ? cause.error : denied().error,
    )
    s.send.mockImplementation(async (method, p) => {
      if (method === 'query.result.describe') return clone(desc)
      if (method === 'query.result.rowsPage') {
        if (p.cursor === id(301) || (p.cursor === id(201) && p.pageSize !== 1)) throw mismatch()
        return {
          identity: clone(desc.identity),
          kind: 'rows',
          order: 'query-index:asc',
          rows: [clone(samples.rows.rows[0])],
          nextCursor: id(201),
        }
      }
      if (method === 'query.result.textPage') {
        if (p.cursor === id(201) || (p.cursor === id(301) && p.maxUtf8Bytes !== 8)) throw mismatch()
        const part = samples.text.text.slice(0, 8)
        return {
          identity: clone(desc.identity),
          kind: 'text',
          order: 'utf8-byte:asc',
          startUtf8Byte: 0,
          utf8Length: Buffer.byteLength(part, 'utf8'),
          text: part,
          nextCursor: id(301),
        }
      }
      throw Error(method)
    })
    const descriptor = await s.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!descriptor.ok) throw Error('descriptor fixture')
    const ref = descriptor.data.descriptorRef
    expect(
      (await s.query.getQueryRowsPage({ descriptorRef: ref, pageSize: 1, cursor: null })).ok,
    ).toBe(true)
    expect(
      (
        await s.query.getQueryExecutedTextPage({
          descriptorRef: ref,
          maxUtf8Bytes: 8,
          cursor: null,
        })
      ).ok,
    ).toBe(true)
    for (const cursor of [id(301), id(201)]) {
      const result = await s.query.getQueryRowsPage({
        descriptorRef: ref,
        pageSize: cursor === id(201) ? 2 : 1,
        cursor,
      })
      expect(result).toMatchObject({ ok: false, error: { code: 'CURSOR_MISMATCH' } })
      expect(s.send.mock.calls.at(-1)?.[1].binding).toEqual(desc.identity)
    }
    for (const cursor of [id(201), id(301)]) {
      const result = await s.query.getQueryExecutedTextPage({
        descriptorRef: ref,
        maxUtf8Bytes: cursor === id(301) ? 7 : 8,
        cursor,
      })
      expect(result).toMatchObject({ ok: false, error: { code: 'CURSOR_MISMATCH' } })
      expect(s.send.mock.calls.at(-1)?.[1].binding).toEqual(desc.identity)
    }
    s.query.dispose()
  })
  it('same literal project/session/result under another source owner cannot consume the first owner descriptor', async () => {
    const a = await service(),
      b = await service(),
      descriptor = await a.query.getQueryResultDescriptor({ resultId: id(6) })
    if (!descriptor.ok) throw Error('descriptor fixture')
    expect(a.source.current()!.project.projectId).toBe(b.source.current()!.project.projectId)
    expect(a.source.current()!.engineSessionId).toBe(b.source.current()!.engineSessionId)
    expect(a.source.current()!.owner).not.toBe(b.source.current()!.owner)
    b.send.mockClear()
    expect(
      await b.query.getQueryRowsPage({
        descriptorRef: descriptor.data.descriptorRef,
        pageSize: 2,
        cursor: null,
      }),
    ).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    expect(b.send).not.toHaveBeenCalled()
    a.query.dispose()
    b.query.dispose()
  })
})
