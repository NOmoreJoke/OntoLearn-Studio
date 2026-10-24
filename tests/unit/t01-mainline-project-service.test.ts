/** SOURCE definitions. Real Supervisor/TaskService with in-memory stdio, no OS process. */
import { describe, expect, it, vi } from 'vitest'
import { EventEmitter } from 'node:events'
import { PassThrough, Writable } from 'node:stream'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const processDouble = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn: processDouble.spawn }))
import {
  EngineSupervisor,
  EngineError,
  MainlineProjectTransport,
} from '../../apps/desktop/src/main/engine'
import {
  ProjectMainlineService,
  MainlineProjectSource,
} from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { v2Registry } from '../../packages/contracts/src/v2'
import corpus from '../../packages/contracts/v2/fixtures.json'
import type { ProjectView, BridgeResult } from '@ontolearn/contracts'

type Row = Record<string, unknown>
const id = (n: number) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
const registryPath = fileURLToPath(
  new URL('../../packages/contracts/v2/registry.json', import.meta.url),
)
const registryHash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const limits = structuredClone(corpus.queryConsumer.samples.prepared.executionIdentity.limits)
const project = (): ProjectView => ({
  projectId: id(1),
  projectRevision: 1,
  inputSnapshotId: 'a'.repeat(64),
  dependencyVector: { 'facts:asserted': 1, 'query:Q1': 1 },
  formatVersion: 3,
})
class MemoryChild extends EventEmitter {
  stdout = new PassThrough()
  stderr = new PassThrough()
  stdin: Writable
  exitCode: number | null = null
  signalCode: NodeJS.Signals | null = null
  calls: Row[] = []
  responses: Row[] = []
  projection: ProjectView = project()
  holdGet = false
  holdHello = false
  holdOpen = false
  pendingHelloFrame?: string
  pendingOpenFrame?: string
  selectedProject: string | null = null
  failOpen = false
  openError?: Row
  forgeCreateHash = false
  forgeDraftHash = false
  pendingGet?: Row
  constructor(
    readonly session: string,
    readonly advertise = true,
  ) {
    super()
    this.stdin = new Writable({
      write: (bytes, _encoding, done) => {
        const q = JSON.parse(bytes.toString()) as Row
        this.calls.push(q)
        if (q.method === 'project.get' && this.holdGet) {
          this.pendingGet = q
          done()
          return
        }
        this.reply(q)
        done()
      },
    })
  }
  reply(q: Row): void {
    let result: unknown
    let error: unknown
    if (q.method === 'hello')
      result = {
        selectedVersion: 3,
        engineVersion: '0.1.0',
        engineSessionId: this.session,
        capabilities: this.advertise
          ? [
              'health',
              'session.ping',
              'project.get',
              'project.catalog',
              'project.create',
              'project.example.create',
              'project.draft.save',
              'project.open',
              'project.read',
              'query.definition.load',
            ]
          : ['health', 'session.ping'],
        registryHash,
        limits,
      }
    else if (q.method === 'session.ping') result = { nonce: (q.params as Row).nonce }
    else if (q.method === 'project.open' && this.failOpen)
      error = this.openError ?? {
        code: 'PERMISSION_DENIED',
        messageKey: 'permission.denied',
        retryable: false,
        params: {},
      }
    else if (q.method === 'project.open') {
      this.selectedProject = String((q.params as Row).projectId)
      this.projection = { ...this.projection, projectId: this.selectedProject }
      result = { ...this.projection }
    } else if (q.method === 'project.get') {
      if (this.selectedProject !== (q.params as Row).projectId)
        error = {
          code: 'PERMISSION_DENIED',
          messageKey: 'permission.denied',
          params: {},
          retryable: false,
        }
      else result = this.projection
    } else if (q.method === 'project.create' || q.method === 'project.example.create') {
      const params = q.params as Row
      const canonical = Object.fromEntries(
        Object.keys(params)
          .sort()
          .map((key) => [key, params[key]]),
      )
      const requestHash = this.forgeCreateHash
        ? 'f'.repeat(64)
        : createHash('sha256').update(JSON.stringify(canonical), 'utf8').digest('hex')
      const receipt = {
        libraryEvidenceRef: 'a'.repeat(64),
        projectId: id(1),
        operationId: params.operationId,
        requestHash,
        contextHash: 'a'.repeat(64),
        planHash: 'a'.repeat(64),
        operationSequence: 1,
        metadataVersion: 1,
        inputSnapshotId: 'a'.repeat(64),
        beforeCheckpointRef: 'a'.repeat(64),
        afterCheckpointRef: 'b'.repeat(64),
      }
      result = {
        createResultVersion: 1,
        projectId: id(1),
        operationId: params.operationId,
        requestHash,
        receipt:
          q.method === 'project.create'
            ? { ...receipt, projectCreateReceiptVersion: 1, domainRevision: 0 }
            : {
                ...receipt,
                exampleCreateReceiptVersion: 1,
                domainRevision: 1,
                exampleId: params.exampleId,
                inputDigest: params.inputDigest,
              },
      }
    } else if (q.method === 'project.draft.save') {
      const params = q.params as Row
      result = {
        draftSaveVersion: 1,
        projectId: params.projectId,
        operationId: params.operationId,
        operationSequence: 2,
        editor: params.editor,
        generation: Number(params.expectedGeneration) + 1,
        boundDomainRevision: params.boundDomainRevision,
        afterCheckpointRef: 'b'.repeat(64),
        contentHash: this.forgeDraftHash
          ? 'f'.repeat(64)
          : createHash('sha256').update(String(params.contentJson), 'utf8').digest('hex'),
      }
    } else if (q.method === 'query.definition.load')
      result = structuredClone(corpus.queryConsumer.samples.managed)
    else if (q.method === 'project.catalog')
      result = {
        catalogVersion: 1,
        snapshotId: id(4),
        items: [],
        total: 0,
        offset: 0,
        nextCursor: null,
      }
    else result = { status: 'ok', engineVersion: '0.1.0' }
    const frame =
      JSON.stringify({
        kind: 'response',
        protocolVersion: q.method === 'hello' ? 2 : 3,
        engineSessionId: this.session,
        id: q.id,
        method: q.method,
        ok: !error,
        ...(error ? { error } : { result }),
      }) + '\n'
    this.responses.push(JSON.parse(frame) as Row)
    // Hold delivery of the authentic response, after applying the host selection.
    // These finite transport gates never grant project access or mint a Job.
    if (q.method === 'hello' && this.holdHello) this.pendingHelloFrame = frame
    else if (q.method === 'project.open' && this.holdOpen) this.pendingOpenFrame = frame
    else queueMicrotask(() => this.stdout.write(frame))
  }
  kill(): boolean {
    this.exitCode = 0
    queueMicrotask(() => this.emit('close', 0))
    return true
  }
}
async function setup(advertise = true, requestMs = 100) {
  const child = new MemoryChild(id(2), advertise)
  processDouble.spawn.mockReset().mockImplementationOnce(() => {
    queueMicrotask(() => child.emit('spawn'))
    return child
  })
  const supervisor = new EngineSupervisor(
    { packaged: false, appPath: '/memory/desktop', resourcesPath: '/memory/resources' },
    {
      profile: 'business3',
      registryPath,
      command: { command: '/memory/engine', args: [] },
      requestMs,
    },
  )
  const tasks = new TaskService(supervisor),
    reattach = vi.fn()
  const service = new ProjectMainlineService(supervisor, tasks, reattach)
  return {
    child,
    supervisor,
    tasks,
    service,
    reattach,
    close: () => {
      service.dispose()
      tasks.dispose()
      supervisor.stop()
    },
  }
}

describe('actual business3 runtime issuer with memory transport only', () => {
  it('keeps original ordinary issuer denied and rejects caller owner DTO', async () => {
    const s = await setup()
    try {
      expect(s.supervisor.ordinaryLibraryClient()).toBeNull()
      expect(() => s.supervisor.queryReadBudget({ ownerId: id(10) })).toThrow(EngineError)
      expect(s.child.calls).toHaveLength(0)
    } finally {
      s.close()
    }
  })
  it('a branded subclass outside the actual supervisor registry cannot publish', () => {
    const supervisor = new EngineSupervisor(
      { packaged: false, appPath: '/memory/desktop', resourcesPath: '/memory/resources' },
      { profile: 'business3' },
    )
    const forged = new (class extends MainlineProjectTransport {
      readonly owner = { ownerId: id(10) }
      readonly supervisor = supervisor
      get engineSessionId(): string {
        return id(2)
      }
      get selected(): ProjectView {
        return project()
      }
      request(): Promise<unknown> {
        throw Error('must not dispatch')
      }
      acceptProject(): void {
        throw Error('must not publish')
      }
    })()
    const source = new MainlineProjectSource()
    expect(() => source.publish(forged)).toThrow(EngineError)
    expect(() => supervisor.issueMainlineRecovery(forged, () => true)).toThrow(EngineError)
    expect(source.current()).toBeNull()
    supervisor.stop()
  })
  it('requires all four actual hello capabilities before named dispatch', async () => {
    const s = await setup(false)
    try {
      const result = await s.service.openProject({ projectId: id(1) })
      expect(result.ok).toBe(false)
      expect(s.child.calls.map((q) => q.method)).toEqual(['hello'])
      expect(s.service.source.current()).toBeNull()
    } finally {
      s.close()
    }
  })
  it('publishes exact business3 project only after real open reply and reattaches view', async () => {
    const s = await setup()
    try {
      expect(await s.service.openProject({ projectId: id(1) })).toEqual({
        ok: true,
        data: project(),
      })
      expect(s.reattach).toHaveBeenCalledTimes(1)
      expect(s.service.source.current()?.project).toEqual(project())
      expect(s.service.source.current()?.supervisor).toBe(s.supervisor)
      expect(s.child.calls.map((q) => q.method)).toEqual(['hello', 'project.open'])
      expect(v2Registry.foundationProfiles.business3.methods).toContain('project.open')
    } finally {
      s.close()
    }
  })
  it('binds base project read to the original real frame before terminal release', async () => {
    const s = await setup()
    try {
      await s.service.openProject({ projectId: id(1) })
      const result = await s.service.queries.getQueryDefinitionBase()
      expect(result.ok).toBe(true)
      expect(s.child.calls.at(-1)?.method).toBe('project.get')
      expect(s.child.calls.at(-1)?.engineSessionId).toBe(id(2))
      expect(s.child.calls.at(-1)?.params).toEqual({ projectId: id(1) })
    } finally {
      s.close()
    }
  })
  it('small normal base plus definition load is not rejected by duplicate peak objects', async () => {
    const s = await setup()
    try {
      await s.service.openProject({ projectId: id(1) })
      expect((await s.service.queries.getQueryDefinitionBase()).ok).toBe(true)
      expect(
        (
          await s.service.queries.loadQueryDefinition({
            definitionId: 'Q1',
            selection: { kind: 'current' },
          })
        ).ok,
      ).toBe(true)
      expect(s.child.calls.map((q) => q.method)).toEqual([
        'hello',
        'project.open',
        'project.get',
        'query.definition.load',
      ])
    } finally {
      s.close()
    }
  })
  it('copies of selected DTO cannot mint a successor authenticated projection', async () => {
    const s = await setup()
    try {
      await s.service.openProject({ projectId: id(1) })
      expect(() =>
        s.service.source.observeProject({ ...project(), projectRevision: 2 }, s.supervisor, id(2)),
      ).toThrow(EngineError)
      expect(s.service.source.current()?.project.projectRevision).toBe(1)
    } finally {
      s.close()
    }
  })
  it('authenticated atomic successor updates projection without selecting again', async () => {
    const s = await setup()
    try {
      await s.service.openProject({ projectId: id(1) })
      const original = s.service.source.current()!
      s.child.projection = {
        ...project(),
        projectRevision: 2,
        inputSnapshotId: 'b'.repeat(64),
        dependencyVector: { 'facts:asserted': 2, 'query:Q1': 1 },
      }
      expect((await s.tasks.activeProject()).ok).toBe(true)
      const current = s.service.source.current()!
      expect(current.owner).toBe(original.owner)
      expect(current.selectionSeq).toBe(original.selectionSeq)
      expect(current.project.projectRevision).toBe(2)
      expect(s.reattach).toHaveBeenCalledTimes(1)
    } finally {
      s.close()
    }
  })
  it('unmatched project.get timeout retains unknown and forbids reuse instead of releasing', async () => {
    const s = await setup()
    try {
      await s.service.openProject({ projectId: id(1) })
      s.child.holdGet = true
      const result = await s.service.queries.getQueryDefinitionBase()
      expect(result.ok).toBe(false)
      expect(s.service.queries.hasOutstanding).toBe(true)
      const before = s.child.calls.length
      expect((await s.service.queries.getQueryDefinitionBase()).ok).toBe(false)
      expect(s.child.calls).toHaveLength(before)
      expect(s.child.pendingGet).toBeDefined()
    } finally {
      s.close()
    }
  })
  it('selection fence before the send microtask prevents the original query write', async () => {
    const s = await setup()
    try {
      await s.service.openProject({ projectId: id(1) })
      const current = s.service.source.current()!
      const pin = s.supervisor.issueQueryPin(
        current.owner,
        current.engineSessionId,
        () => s.service.source.current() === current,
      )
      const count = s.child.calls.length
      const request = s.supervisor.requestPinned(
        'query.definition.load',
        { projectId: id(1), definitionId: 'Q1', selection: { kind: 'current' } },
        pin,
      )
      s.service.source.fence()
      await expect(request).rejects.toBeInstanceOf(EngineError)
      expect(s.child.calls).toHaveLength(count)
    } finally {
      s.close()
    }
  })
  for (const named of [false, true]) {
    it(`${named ? 'named' : 'blank'} create returns durable receipt before any explicit open`, async () => {
      const s = await setup()
      try {
        const result = named
          ? await s.service.createExampleProject({
              exampleCreateRequestVersion: 1,
              operationId: id(8),
              name: '设备𠮷',
              exampleId: 'equipment-maintenance',
              inputDigest: '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e',
            })
          : await s.service.createBlankProject({
              requestVersion: 1,
              operationId: id(8),
              name: '设备𠮷',
              initialization: { kind: 'blank' },
            })
        expect(result.ok).toBe(true)
        if (!result.ok) throw Error('expected durable create receipt')
        const receiptBeforeOpen = structuredClone(result.data)
        expect(result.data.operationId).toBe(id(8))
        expect(result.data.receipt.projectId).toBe(id(1))
        expect(s.child.calls.map((q) => q.method)).toEqual([
          'hello',
          named ? 'project.example.create' : 'project.create',
        ])
        expect(s.service.source.current()).toBeNull()
        expect(s.reattach).not.toHaveBeenCalled()
        s.child.failOpen = true
        expect((await s.service.openProject({ projectId: result.data.projectId })).ok).toBe(false)
        expect(result.data).toEqual(receiptBeforeOpen)
        expect(s.child.calls.map((q) => q.method)).toEqual([
          'hello',
          named ? 'project.example.create' : 'project.create',
          'project.open',
        ])
        expect(s.service.source.current()).toBeNull()
        expect(s.reattach).not.toHaveBeenCalled()
      } finally {
        s.close()
      }
    })
    it(`${named ? 'named' : 'blank'} create rejects coherent wrong request hash before publication`, async () => {
      const s = await setup()
      try {
        s.child.forgeCreateHash = true
        const result = named
          ? await s.service.createExampleProject({
              exampleCreateRequestVersion: 1,
              operationId: id(8),
              name: '设备𠮷',
              exampleId: 'equipment-maintenance',
              inputDigest: '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e',
            })
          : await s.service.createBlankProject({
              requestVersion: 1,
              operationId: id(8),
              name: '设备𠮷',
              initialization: { kind: 'blank' },
            })
        expect(result.ok).toBe(false)
        expect(s.child.calls.map((q) => q.method)).toEqual([
          'hello',
          named ? 'project.example.create' : 'project.create',
        ])
        expect(s.service.source.current()).toBeNull()
        expect(s.reattach).not.toHaveBeenCalled()
      } finally {
        s.close()
      }
    })
  }
  for (const forged of [false, true]) {
    it(`typed draft save ${forged ? 'rejects forged' : 'accepts original Unicode UTF8'} content hash`, async () => {
      const s = await setup()
      try {
        expect((await s.service.openProject({ projectId: id(1) })).ok).toBe(true)
        s.child.forgeDraftHash = forged
        const args = {
          operationId: id(9),
          editor: 'query',
          expectedGeneration: 0,
          boundDomainRevision: 1,
          contentJson: '{"name":"设备𠮷","text":"ASK {}"}',
        }
        const result = await s.service.saveProjectDraft(args)
        expect(result.ok).toBe(!forged)
        if (!forged) {
          if (!result.ok) throw Error('expected authenticated draft receipt')
          expect(result.data.contentHash).toBe(
            createHash('sha256').update(args.contentJson, 'utf8').digest('hex'),
          )
          expect(result.data.generation).toBe(1)
          expect(result.data.operationId).toBe(args.operationId)
        }
        expect(s.child.calls.map((q) => q.method)).toEqual([
          'hello',
          'project.open',
          'project.draft.save',
        ])
        expect(s.child.calls.at(-1)?.params).toEqual({ ...args, projectId: id(1) })
        expect(s.reattach).toHaveBeenCalledTimes(1)
        expect(s.service.source.current()?.project).toEqual(project())
      } finally {
        s.close()
      }
    })
  }
})

// Transport scheduling counterexamples; the production service/TaskService and
// Supervisor remain real. The Python business3 positive lives in task-runtime.
describe('business3 recovery selection authority at actual transport boundaries', () => {
  const waitFor = async (predicate: () => boolean): Promise<void> => {
    await vi.waitFor(() => expect(predicate()).toBe(true), { timeout: 2000, interval: 5 })
  }
  const begin = async (gate: 'hello' | 'open' | 'none' = 'none') => {
    const s = await setup(true, 1500)
    const replies = s.supervisor.mainlineReplyReceiver()
    const receive = async <T>(work: () => Promise<BridgeResult<T>>): Promise<BridgeResult<T>> => {
      const delivery = await replies.receive(work)
      if (delivery.value.ok) replies.consume(delivery.receipt)
      return delivery.value
    }
    expect((await receive(() => s.service.openProject({ projectId: id(1) }))).ok).toBe(true)
    const next = new MemoryChild(id(3))
    next.holdHello = gate === 'hello'
    next.holdOpen = gate === 'open'
    processDouble.spawn.mockImplementationOnce(() => {
      queueMicrotask(() => next.emit('spawn'))
      return next
    })
    const updates: import('@ontolearn/contracts').TaskUpdate[] = []
    s.tasks.attachView((update) => updates.push(update))
    return { ...s, next, receive, updates }
  }
  const disconnect = (s: Awaited<ReturnType<typeof begin>>) => {
    s.child.exitCode = 73
    s.child.emit('close', 73)
  }
  it('reopens the trusted project before any new-session project read and shares manual restore', async () => {
    const s = await begin('open')
    try {
      const old = s.service.source.current()!
      disconnect(s)
      await waitFor(() => !!s.next.pendingOpenFrame)
      expect(s.service.source.current()).toBeNull()
      expect(s.next.calls.filter((q) => q.method === 'project.get')).toHaveLength(0)
      const manual = s.tasks.restore()
      s.next.stdout.write(s.next.pendingOpenFrame!)
      const restored = await manual
      expect(restored.ok).toBe(true)
      if (!restored.ok) throw Error('expected original project recovery')
      expect(restored.data.project?.projectId).toBe(id(1))
      expect(s.next.calls.filter((q) => q.method === 'project.open')).toHaveLength(1)
      expect(s.next.calls.findIndex((q) => q.method === 'project.open')).toBeLessThan(
        s.next.calls.findIndex((q) => q.method === 'project.get'),
      )
      const current = s.service.source.current()!
      expect(current.project.projectId).toBe(id(1))
      expect(current.engineSessionId).toBe(id(3))
      expect(current.owner).not.toBe(old.owner)
      expect(
        s.updates.some((u) => u.kind === 'restored' && u.view.project?.projectId === id(1)),
      ).toBe(true)
      expect(
        s.next.calls.some((q) => ['job.create', 'job.cancel'].includes(String(q.method))),
      ).toBe(false)
    } finally {
      s.close()
    }
  })
  const switchSelection = (s: Awaited<ReturnType<typeof begin>>) => {
    const generation = s.tasks.queryViewGeneration(id(1), s.supervisor)
    const watermark = s.updates.length
    // Enter the real main-only selection before receiver admission can refuse
    // a concurrent Q request. This is service authority, not an IPC success.
    const selection = s.service.openProject({ projectId: id(4) })
    expect(() => s.tasks.queryViewGeneration(id(1), s.supervisor)).toThrow(EngineError)
    expect(
      s.updates
        .slice(watermark)
        .some((u) => u.kind === 'restored' && u.generation > generation && u.view.project === null),
    ).toBe(true)
    return selection
  }
  for (const action of ['switch', 'close', 'dispose'] as const) {
    it(`${action} during new hello prevents a stale recovery project.open send`, async () => {
      const s = await begin('hello')
      try {
        disconnect(s)
        await waitFor(() => !!s.next.pendingHelloFrame)
        const selection =
          action === 'switch'
            ? switchSelection(s).catch((cause: unknown) => {
                if (!(cause instanceof EngineError)) throw cause
                expect(['INVALID_STATE', 'RESOURCE_LIMIT']).toContain(cause.error.code)
                return { ok: false as const, error: cause.error }
              })
            : undefined
        if (action === 'close') await s.service.source.closeSelection()
        if (action === 'dispose') s.service.dispose()
        s.next.stdout.write(s.next.pendingHelloFrame!)
        const selected = selection ? await selection : undefined
        if (selected && !selected.ok)
          expect(['INVALID_STATE', 'RESOURCE_LIMIT']).toContain(selected.error.code)
        await new Promise<void>((done) => setImmediate(done))
        expect(
          s.next.calls.some(
            (q) => q.method === 'project.open' && (q.params as Row).projectId === id(1),
          ),
        ).toBe(false)
        expect(s.service.source.current()?.project.projectId ?? null).toBe(
          selected?.ok ? id(4) : null,
        )
      } finally {
        s.close()
      }
    })
    it(`${action} after an open was sent rejects its late selected-project publication`, async () => {
      const s = await begin('open')
      try {
        disconnect(s)
        await waitFor(() => !!s.next.pendingOpenFrame)
        const late = s.next.pendingOpenFrame!
        s.next.holdOpen = false
        let selected = false
        if (action === 'switch') {
          const result = await switchSelection(s).catch((cause: unknown) => {
            if (!(cause instanceof EngineError)) throw cause
            expect(['INVALID_STATE', 'RESOURCE_LIMIT']).toContain(cause.error.code)
            return { ok: false as const, error: cause.error }
          })
          if (!result.ok) expect(['INVALID_STATE', 'RESOURCE_LIMIT']).toContain(result.error.code)
          selected = result.ok
        }
        if (action === 'close') await s.service.source.closeSelection()
        if (action === 'dispose') s.service.dispose()
        s.next.stdout.write(late)
        await new Promise<void>((done) => setImmediate(done))
        expect(s.service.source.current()?.project.projectId ?? null).toBe(selected ? id(4) : null)
        expect(
          s.next.calls.filter(
            (q) => q.method === 'project.open' && (q.params as Row).projectId === id(1),
          ),
        ).toHaveLength(1)
        expect(
          s.updates.some((u) => u.kind === 'restored' && u.view.project?.projectId === id(1)),
        ).toBe(false)
      } finally {
        s.close()
      }
    })
  }
  it('does not emit a stale ready after a synchronous source observer disposes its owner', async () => {
    const s = await begin()
    let released = () => {}
    try {
      released = s.service.source.observe((current) => {
        if (current?.engineSessionId === id(3)) s.service.dispose()
      })
      disconnect(s)
      await waitFor(() => s.next.calls.some((q) => q.method === 'project.get'))
      await new Promise<void>((done) => setImmediate(done))
      expect(s.service.source.current()).toBeNull()
      expect(
        s.updates.some((u) => u.kind === 'restored' && u.view.project?.projectId === id(1)),
      ).toBe(false)
    } finally {
      released()
      s.close()
    }
  })
  it('never refunds an unmatched old reply when a recovery uses another session', async () => {
    const s = await begin()
    try {
      s.child.holdGet = true
      expect((await s.receive(() => s.service.queries.getQueryDefinitionBase())).ok).toBe(false)
      const before = s.supervisor.mainlineReplyReceiver().diagnostic()
      expect(before.unknown).toBeGreaterThan(0)
      disconnect(s)
      await s.tasks.restore()
      const after = s.supervisor.mainlineReplyReceiver().diagnostic()
      expect(after.unknown).toBeGreaterThanOrEqual(before.unknown)
      expect(after.slots).toBeGreaterThanOrEqual(before.unknown)
      expect(
        s.next.calls.some((q) => ['job.create', 'job.cancel'].includes(String(q.method))),
      ).toBe(false)
    } finally {
      s.close()
    }
  })
  for (const error of [
    { code: 'PERMISSION_DENIED', messageKey: 'permission.denied', params: {}, retryable: false },
    {
      code: 'RESOURCE_LIMIT',
      messageKey: 'resource.limitExceeded',
      params: { resource: 'memory' },
      retryable: false,
    },
    { code: 'STORAGE_FAILURE', messageKey: 'storage.failure', params: {}, retryable: false },
  ])
    it(`preserves ${error.code} refusal/offline without a new issuer or project read`, async () => {
      const s = await begin()
      s.next.failOpen = true
      s.next.openError = error
      const before = s.supervisor.mainlineReplyReceiver().diagnostic()
      expect(
        s.supervisor.isMainlineRecoveryRefusal(new EngineError(error), Promise.resolve(null)),
      ).toBe(false)
      try {
        disconnect(s)
        await waitFor(() => s.updates.some((u) => u.kind === 'connection' && u.state === 'offline'))
        expect(s.service.source.current()).toBeNull()
        const offline = s.updates.find((u) => u.kind === 'connection' && u.state === 'offline')
        expect(offline?.kind === 'connection' && offline.error).toEqual(error)
        expect(offline?.kind === 'connection' && offline.attempt).toBe(1)
        const opens = s.next.calls.filter((q) => q.method === 'project.open')
        expect(opens).toHaveLength(1)
        expect(opens[0].params).toEqual({ projectId: id(1) })
        const frame = s.next.responses.find((r) => r.id === opens[0].id)
        expect(frame).toMatchObject({
          kind: 'response',
          method: 'project.open',
          engineSessionId: id(3),
          protocolVersion: 3,
          ok: false,
          error,
        })
        const after = s.supervisor.mainlineReplyReceiver().diagnostic()
        expect(after.unknown).toBeGreaterThanOrEqual(before.unknown + 1)
        expect(after.slots).toBeGreaterThanOrEqual(before.slots + 1)
        expect(s.next.calls.some((q) => q.method === 'project.get')).toBe(false)
        expect(s.updates.some((u) => u.kind === 'restored' && u.view.project !== null)).toBe(false)
        expect(
          s.next.calls.some((q) => ['job.create', 'job.cancel'].includes(String(q.method))),
        ).toBe(false)
      } finally {
        s.close()
      }
    })
})
