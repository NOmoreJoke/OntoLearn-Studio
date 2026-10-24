import { EventEmitter } from 'node:events'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { PassThrough, Writable } from 'node:stream'
import { fileURLToPath } from 'node:url'
import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  EngineError,
  EngineSupervisor,
  MainlineReplyReceipt,
} from '../../apps/desktop/src/main/engine'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { v2Registry } from '../../packages/contracts/src/v2'

const controlled = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn: controlled.spawn }))
const id = (n: number) => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`
const registryPath = fileURLToPath(
  new URL('../../packages/contracts/v2/registry.json', import.meta.url),
)
const registryHash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const limits = {
  startupMs: 1000,
  handshakeMs: 1000,
  requestMs: 1000,
  totalMs: 120000,
  heartbeatMs: 10000,
  cancelGraceMs: 1000,
  maxFrameBytes: 262144,
  maxQueuedJobs: 32,
  maxConcurrentJobs: 2,
  maxPageItems: 100,
  maxPageBytes: 131072,
  maxWorkerMemoryBytes: 536870912,
}
type Wire = { id: string; method: string; params: Record<string, unknown> }
class MemoryChild extends EventEmitter {
  stdout = new PassThrough()
  stderr = new PassThrough()
  stdin: Writable
  exitCode: number | null = null
  signalCode: NodeJS.Signals | null = null
  holdCatalog = false
  holdOpen = false
  pendingOpenFrame?: string
  wrongId = false
  calls: Wire[] = []
  constructor(readonly session: string) {
    super()
    this.stdin = new Writable({
      write: (bytes, _encoding, done) => {
        const q = JSON.parse(bytes.toString()) as Wire
        this.calls.push(q)
        if (q.method === 'project.catalog' && this.holdCatalog) {
          done()
          return
        }
        const result =
          q.method === 'hello'
            ? {
                selectedVersion: 3,
                engineVersion: '0.1.0',
                engineSessionId: session,
                capabilities: v2Registry.foundationProfiles.business3.methods,
                limits,
                registryHash,
              }
            : q.method === 'project.open' || q.method === 'project.get'
              ? {
                  projectId: id(1),
                  projectRevision: 0,
                  inputSnapshotId: 'a'.repeat(64),
                  dependencyVector: { 'facts:asserted': 0 },
                  formatVersion: 3,
                }
              : q.method === 'session.ping'
                ? { nonce: q.params.nonce }
                : {
                    catalogVersion: 1,
                    snapshotId: id(9),
                    items: [],
                    total: 0,
                    offset: 0,
                    nextCursor: null,
                  }
        const frame =
          JSON.stringify({
            kind: 'response',
            protocolVersion: q.method === 'hello' ? 2 : 3,
            id: this.wrongId && q.method !== 'hello' ? id(99) : q.id,
            engineSessionId: session,
            method: q.method,
            ok: true,
            result,
          }) + '\n'
        if (q.method === 'project.open' && this.holdOpen) this.pendingOpenFrame = frame
        else queueMicrotask(() => this.stdout.write(frame))
        done()
      },
    })
  }
  kill(): boolean {
    if (this.exitCode === null) this.exitCode = 0
    queueMicrotask(() => this.emit('close', this.exitCode))
    return true
  }
}
const supervisors: EngineSupervisor[] = []
function setup(requestMs = 20) {
  const children: MemoryChild[] = []
  controlled.spawn.mockReset().mockImplementation(() => {
    const child = new MemoryChild(id(2 + children.length))
    children.push(child)
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
  supervisors.push(supervisor)
  const receiver = supervisor.mainlineReplyReceiver()
  const catalog = () => {
    const client = supervisor.mainlineProjectClient()
    if (!client) throw Error('expected real runtime mainline issuer')
    return client.request('project.catalog', { pageSize: 1, cursor: null })
  }
  const open = () => {
    const client = supervisor.mainlineProjectClient()
    if (!client) throw Error('expected real runtime mainline issuer')
    return client.request('project.open', { projectId: id(1) })
  }
  return { supervisor, receiver, children, catalog, open }
}
afterEach(() => {
  for (const supervisor of supervisors.splice(0)) supervisor.stop()
})

describe('main-only delivery receipts with actual supervisor and memory stdio', () => {
  it('completes more than20 windows whose lifetime work exceeds512MiB without resetting scratch', async () => {
    const s = setup()
    let previousScratch = 0
    for (let i = 0; i < 24; i++) {
      const offered = await s.receiver.receive(s.catalog)
      expect(offered.value).toEqual({
        catalogVersion: 1,
        snapshotId: id(9),
        items: [],
        total: 0,
        offset: 0,
        nextCursor: null,
      })
      expect(s.receiver.binding(offered.receipt)).toEqual({ engineSessionId: id(2) })
      expect(s.receiver.diagnostic().offered).toBe(1)
      s.receiver.consume(offered.receipt)
      s.receiver.consume(offered.receipt)
      const book = s.receiver.diagnostic()
      expect(book.slots).toBe(0)
      expect(book.deliveryBytes).toBe(0)
      expect(book.deliveryObjects).toBe(0)
      expect(book.scratchBytes).toBeGreaterThanOrEqual(previousScratch)
      expect(book.scratchBytes).toBeGreaterThan(0)
      previousScratch = book.scratchBytes
      expect(book.maxWindowWork).toBeLessThanOrEqual(536870912)
      expect(book.retainedBytes).toBeLessThanOrEqual(134217728)
      expect(book.retainedObjects).toBeLessThanOrEqual(1048576)
    }
    expect(s.receiver.diagnostic().totalWork).toBeGreaterThan(536870912)
    expect(s.children).toHaveLength(1)
    expect(s.children[0].calls.filter((q) => q.method === 'project.catalog')).toHaveLength(24)
  })
  it('allows16 pending deliveries and rejects17 before calling its callback', async () => {
    const s = setup(),
      receipts: MainlineReplyReceipt[] = []
    for (let i = 0; i < 16; i++) receipts.push((await s.receiver.receive(s.catalog)).receipt)
    expect(s.receiver.diagnostic().slots).toBe(16)
    const forbidden = vi.fn(s.catalog)
    await expect(s.receiver.receive(forbidden)).rejects.toBeInstanceOf(EngineError)
    expect(forbidden).not.toHaveBeenCalled()
    expect(s.children[0].calls.filter((q) => q.method === 'project.catalog')).toHaveLength(16)
    s.receiver.consume(receipts[0])
    const next = await s.receiver.receive(s.catalog)
    expect(s.receiver.diagnostic().slots).toBe(16)
    for (const receipt of receipts.slice(1)) s.receiver.consume(receipt)
    s.receiver.consume(next.receipt)
    expect(s.receiver.diagnostic().slots).toBe(0)
  })
  it('rejects copied, caller-branded and other-supervisor receipts without changing the book', async () => {
    const s = setup(),
      offered = await s.receiver.receive(s.catalog)
    const before = s.receiver.diagnostic()
    const forged = new (class extends MainlineReplyReceipt {})()
    expect(() => s.receiver.consume(forged)).toThrow(EngineError)
    expect(() => s.receiver.consume(structuredClone(offered.receipt))).toThrow(EngineError)
    const other = new EngineSupervisor(
      { packaged: false, appPath: '/memory/desktop', resourcesPath: '' },
      { profile: 'business3' },
    )
    supervisors.push(other)
    expect(() => other.mainlineReplyReceiver().consume(offered.receipt)).toThrow(EngineError)
    expect(s.receiver.diagnostic()).toEqual(before)
    s.receiver.consume(offered.receipt)
    expect(s.receiver.diagnostic().slots).toBe(0)
  })
  it('does not refund a direct orphan call in a later unrelated receive', async () => {
    const s = setup()
    await s.catalog()
    expect(s.receiver.diagnostic().orphans).toBe(1)
    const offered = await s.receiver.receive(s.catalog)
    s.receiver.consume(offered.receipt)
    expect(s.receiver.diagnostic().slots).toBe(1)
    expect(s.receiver.diagnostic().orphans).toBe(1)
    expect(s.receiver.diagnostic().deliveryBytes).toBeGreaterThan(0)
  })
  it('retains exact cache holding across ACK and only drops its original logical responsibility', async () => {
    const s = setup(),
      entry = {},
      value = { query: 'ASK {}', text: 'x'.repeat(300000) }
    const opened = await s.receiver.receive(s.open)
    s.receiver.consume(opened.receipt)
    const client = s.supervisor.mainlineProjectClient()
    if (!client) throw Error('expected actual client')
    const budget = s.supervisor.queryReadBudget(client.owner)
    const offered = await s.receiver.receive(async () => {
      const finish = budget.beginConsumerRequest()
      try {
        budget.retainHolding(entry, value)
        budget.retainHolding(entry, value)
        return { ok: true, data: { held: true } }
      } finally {
        finish()
      }
    })
    const before = s.receiver.diagnostic()
    expect(before.holdingCount).toBe(2)
    s.receiver.consume(offered.receipt)
    const after = s.receiver.diagnostic()
    expect(after.holdingCount).toBe(2)
    expect(after.deliveryBytes).toBe(0)
    expect(after.retainedBytes).toBeGreaterThan(after.scratchBytes)
    expect(after.retainedBytes).toBeLessThan(before.retainedBytes)
    expect(() => budget.releaseHolding({})).toThrow(EngineError)
    budget.releaseHolding(entry)
    budget.releaseHolding(entry)
    expect(s.receiver.diagnostic().holdingCount).toBe(1)
    expect(s.receiver.diagnostic().scratchBytes).toBe(after.scratchBytes)
  })
  it('keeps the engine selected projection charged after the source closes its own alias', async () => {
    const s = setup(),
      tasks = new TaskService(s.supervisor)
    const projects = new ProjectMainlineService(s.supervisor, tasks, () => {})
    try {
      const offered = await s.receiver.receive(() => projects.openProject({ projectId: id(1) }))
      expect(offered.value.ok).toBe(true)
      s.receiver.consume(offered.receipt)
      const client = s.supervisor.mainlineProjectClient()!
      const selected = client.selected
      expect(projects.source.current()?.project).toBe(selected)
      expect(s.receiver.diagnostic().holdingCount).toBe(3) // selected, source, principal
      projects.source.fence()
      expect(projects.source.current()).toBeNull()
      expect(client.selected).toBe(selected)
      expect(s.receiver.diagnostic().holdingCount).toBe(2) // raw fence retains recovery authority
      expect(s.receiver.diagnostic().slots).toBe(0)
      await projects.source.closeSelection()
      expect(s.receiver.diagnostic().holdingCount).toBe(1) // actual owner close retires principal
      expect(client.selected).toBe(selected)
    } finally {
      projects.dispose()
      tasks.dispose()
    }
  })
  it('retires completed principal holdings on reselection and repeated actual disposal', async () => {
    const s = setup(),
      tasks = new TaskService(s.supervisor)
    const projects = new ProjectMainlineService(s.supervisor, tasks, () => {})
    try {
      for (let i = 0; i < 5; i++) {
        const reply = await s.receiver.receive(() => projects.openProject({ projectId: id(1) }))
        expect(reply.value.ok).toBe(true)
        s.receiver.consume(reply.receipt)
        expect(s.receiver.diagnostic().holdingCount).toBe(3)
        expect(s.receiver.diagnostic().slots).toBe(0)
      }
      const before = s.receiver.diagnostic()
      projects.dispose()
      expect(s.receiver.diagnostic().holdingCount).toBe(1)
      projects.dispose()
      expect(s.receiver.diagnostic().holdingCount).toBe(1)
      expect(s.receiver.diagnostic().scratchBytes).toBe(before.scratchBytes)
      expect(s.receiver.diagnostic().totalWork).toBeGreaterThanOrEqual(before.totalWork)
      expect(s.receiver.diagnostic().unknown).toBe(before.unknown)
    } finally {
      projects.dispose()
      tasks.dispose()
    }
  })
  it('authenticates exact retirement tokens and origin owners without refunding other responsibility', async () => {
    const s = setup()
    let token: object | undefined
    const offered = await s.receiver.receive(async () => {
      const value = await s.open()
      const client = s.supervisor.mainlineProjectClient()!
      token = s.supervisor.issueMainlineRecovery(client, () => true)
      return value
    })
    s.receiver.consume(offered.receipt)
    const origin = s.supervisor.mainlineProjectClient()!
    expect(token).toBeDefined()
    const before = s.receiver.diagnostic()
    const foreign = setup()
    const foreignClient = foreign.supervisor.mainlineProjectClient()!
    expect(() => s.supervisor.retireMainlineRecovery(origin, {})).toThrow(EngineError)
    expect(() => s.supervisor.retireMainlineRecovery(foreignClient, token!)).toThrow(EngineError)
    expect(() => foreign.supervisor.retireMainlineRecovery(origin, token!)).toThrow(EngineError)
    s.children[0].exitCode = 1
    s.children[0].emit('close', 1)
    const successor = s.supervisor.mainlineProjectClient()!
    expect(successor.owner).not.toBe(origin.owner)
    expect(() => s.supervisor.retireMainlineRecovery(successor, token!)).toThrow(EngineError)
    expect(s.receiver.diagnostic().holdingCount).toBe(before.holdingCount)
    expect(s.supervisor.retireMainlineRecovery(origin, token!)).toBe(true)
    expect(s.supervisor.retireMainlineRecovery(origin, token!)).toBe(true)
    const after = s.receiver.diagnostic()
    expect(after.holdingCount).toBe(before.holdingCount - 1)
    expect(after.unknown).toBe(before.unknown)
    expect(after.slots).toBe(before.slots)
    expect(after.scratchBytes).toBe(before.scratchBytes)
    expect(after.totalWork).toBeGreaterThanOrEqual(before.totalWork)
  })
  it('keeps a retired principal charged until its actual pending open finally ends', async () => {
    const s = setup(1500),
      tasks = new TaskService(s.supervisor)
    const updates: import('@ontolearn/contracts').TaskUpdate[] = []
    const projects = new ProjectMainlineService(s.supervisor, tasks, () =>
      tasks.attachView((u) => updates.push(u)),
    )
    try {
      const offered = await s.receiver.receive(() => projects.openProject({ projectId: id(1) }))
      expect(offered.value.ok).toBe(true)
      s.receiver.consume(offered.receipt)
      const next = new MemoryChild(id(3))
      next.holdOpen = true
      controlled.spawn.mockImplementationOnce(() => {
        s.children.push(next)
        queueMicrotask(() => next.emit('spawn'))
        return next
      })
      s.children[0].exitCode = 1
      s.children[0].emit('close', 1)
      await vi.waitFor(() => expect(next.pendingOpenFrame).toBeDefined(), {
        timeout: 1000,
        interval: 5,
      })
      const before = s.receiver.diagnostic()
      const watermark = updates.length
      expect(before.holdingCount).toBe(2) // old selected + principal, real open pending
      await projects.source.closeSelection()
      expect(s.receiver.diagnostic().holdingCount).toBe(before.holdingCount)
      expect(projects.source.current()).toBeNull()
      next.stdout.write(next.pendingOpenFrame!)
      await vi.waitFor(
        () => {
          const after = s.receiver.diagnostic()
          expect(after.computing).toBe(0)
          expect(after.holdingCount).toBe(before.holdingCount - 1)
        },
        { timeout: 1000, interval: 5 },
      )
      const after = s.receiver.diagnostic()
      expect(after.unknown).toBeGreaterThanOrEqual(before.unknown + 1)
      expect(after.slots).toBeGreaterThanOrEqual(before.slots)
      expect(after.scratchBytes).toBe(before.scratchBytes)
      expect(after.totalWork).toBeGreaterThanOrEqual(before.totalWork)
      expect(projects.source.current()).toBeNull()
      expect(
        updates.slice(watermark).some((u) => u.kind === 'restored' && u.view.project !== null),
      ).toBe(false)
      expect(next.calls.filter((q) => q.method === 'project.open')).toHaveLength(1)
      expect(
        next.calls.some((q) => ['project.get', 'job.create', 'job.cancel'].includes(q.method)),
      ).toBe(false)
    } finally {
      projects.dispose()
      tasks.dispose()
    }
  })
  it('keeps timeout UNKNOWN across a real supervisor Session replacement', async () => {
    const s = setup(),
      opened = await s.receiver.receive(s.open)
    s.receiver.consume(opened.receipt)
    s.children[0].holdCatalog = true
    await expect(s.receiver.receive(s.catalog)).rejects.toMatchObject({
      error: { code: 'TIMEOUT' },
    })
    const old = s.receiver.diagnostic()
    expect(old.unknown).toBe(1)
    expect(old.slots).toBe(1)
    s.children[0].exitCode = 1
    s.children[0].emit('close', 1)
    await new Promise((done) => setTimeout(done, 250))
    const successor = await s.receiver.receive(s.open)
    expect(s.receiver.binding(successor.receipt)).toEqual({ engineSessionId: id(3) })
    s.receiver.consume(successor.receipt)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    expect(s.receiver.diagnostic().slots).toBe(1)
    expect(s.receiver.diagnostic().deliveryBytes).toBeGreaterThanOrEqual(old.deliveryBytes)
    expect(s.children).toHaveLength(2)
  })
  it('preserves the original callback throw after handoff without consumption', async () => {
    const s = setup(),
      first = await s.receiver.receive(s.open)
    s.receiver.consume(first.receipt)
    const original = Error('original callback failure')
    await expect(
      s.receiver.receive(async () => {
        await s.catalog()
        throw original
      }),
    ).rejects.toBe(original)
    expect(s.receiver.diagnostic().unknown).toBe(1)
  })
  it('requires the final service data to be the exact handed-off object', async () => {
    const s = setup()
    await expect(
      s.receiver.receive(async () => {
        const value = await s.catalog()
        return { ok: true, data: structuredClone(value) }
      }),
    ).rejects.toBeInstanceOf(EngineError)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    expect(s.receiver.diagnostic().slots).toBe(1)
  })
  it('error wrappers after an accepted alias remain UNKNOWN even with a receipt', async () => {
    const s = setup()
    const offered = await s.receiver.receive(async () => {
      await s.catalog()
      return { ok: false, error: { code: 'INTERNAL_ERROR' } }
    })
    expect(offered.value.ok).toBe(false)
    expect(() => s.receiver.consume(offered.receipt)).toThrow(EngineError)
    expect(s.receiver.diagnostic().unknown).toBe(1)
  })
  it('binds an offered receipt to its old Session and preserves it after disconnect', async () => {
    const s = setup(),
      offered = await s.receiver.receive(s.open)
    expect(s.receiver.binding(offered.receipt)).toEqual({ engineSessionId: id(2) })
    s.children[0].exitCode = 1
    s.children[0].emit('close', 1)
    expect(s.receiver.binding(offered.receipt)).toEqual({ engineSessionId: id(2) })
    expect(() => s.receiver.consume(offered.receipt)).toThrow(EngineError)
    expect(s.receiver.diagnostic().unknown).toBe(1)
  })
  it('keeps an unmatched response UNKNOWN and never offers a replacement receipt', async () => {
    const s = setup(),
      first = await s.receiver.receive(s.open)
    s.receiver.consume(first.receipt)
    s.children[0].wrongId = true
    await expect(s.receiver.receive(s.catalog)).rejects.toBeInstanceOf(EngineError)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    expect(s.receiver.diagnostic().offered).toBe(0)
    expect(s.receiver.diagnostic().deliveryBytes).toBeGreaterThan(0)
  })
  it('prepays a cached success with no new handoff and captures its original live Session', async () => {
    const s = setup(),
      first = await s.receiver.receive(s.open)
    s.receiver.consume(first.receipt)
    const cached = { ok: true, data: { accepted: true } }
    const before = s.children[0].calls.length
    const offered = await s.receiver.receive(async () => cached)
    expect(offered.value).toBe(cached)
    expect(s.receiver.binding(offered.receipt)).toEqual({ engineSessionId: id(2) })
    expect(s.children[0].calls).toHaveLength(before)
    expect(s.receiver.diagnostic().deliveryBytes).toBeGreaterThan(4096)
    s.receiver.consume(offered.receipt)
    expect(s.receiver.diagnostic().deliveryBytes).toBe(0)
    expect(s.receiver.diagnostic().scratchBytes).toBeGreaterThan(0)
  })
  it('retains the original cache charge when replacement cannot fit the shared book', async () => {
    const s = setup(),
      first = await s.receiver.receive(s.open)
    s.receiver.consume(first.receipt)
    const client = s.supervisor.mainlineProjectClient()
    if (!client) throw Error('expected actual client')
    const budget = s.supervisor.queryReadBudget(client.owner),
      entry = {}
    const offered = await s.receiver.receive(async () => {
      const finish = budget.beginConsumerRequest()
      try {
        budget.retainHolding(entry, { text: 'original' })
        return { ok: true, data: { saved: true } }
      } finally {
        finish()
      }
    })
    s.receiver.consume(offered.receipt)
    const before = s.receiver.diagnostic()
    await expect(
      s.receiver.receive(async () => {
        const finish = budget.beginConsumerRequest()
        try {
          budget.retainHolding(entry, { text: 'x'.repeat(4 * 1024 * 1024) })
          return { ok: true, data: { saved: true } }
        } finally {
          finish()
        }
      }),
    ).rejects.toBeInstanceOf(EngineError)
    expect(s.receiver.diagnostic().holdingCount).toBe(2)
    expect(s.receiver.diagnostic().retainedBytes).toBeGreaterThanOrEqual(before.retainedBytes)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    // This closes the previous known holding only, never the failed delivery.
    budget.releaseHolding(entry)
    expect(s.receiver.diagnostic().holdingCount).toBe(1)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    expect(s.receiver.diagnostic().slots).toBe(1)
  })
  it('never closes an unfinished consumer computation from a callback success wrapper', async () => {
    const s = setup(),
      first = await s.receiver.receive(s.open)
    s.receiver.consume(first.receipt)
    const client = s.supervisor.mainlineProjectClient()
    if (!client) throw Error('expected actual client')
    const budget = s.supervisor.queryReadBudget(client.owner)
    await expect(
      s.receiver.receive(async () => {
        budget.beginConsumerRequest() // Deliberately no finish: ownership must remain unsettled.
        return { ok: true, data: { computed: false } }
      }),
    ).rejects.toBeInstanceOf(EngineError)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    expect(s.receiver.diagnostic().slots).toBe(1)
  })
  it('keeps the exact receipt after partial cache cleanup failure without double refund', async () => {
    const s = setup(),
      opened = await s.receiver.receive(s.open)
    s.receiver.consume(opened.receipt)
    const client = s.supervisor.mainlineProjectClient()!
    const budget = s.supervisor.queryReadBudget(client.owner)
    const first = {},
      second = {}
    const cleaned = vi.fn(() => budget.releaseHolding(first))
    let fail = true
    const retried = vi.fn(() => {
      if (fail) throw new Error('cleanup remains owned')
      budget.releaseHolding(second)
    })
    const offered = await s.receiver.receive(async () => {
      budget.retainHolding(first, { full: 'first' })
      budget.retainHolding(second, { full: 'second' })
      budget.onReplyConsumed(first, cleaned)
      budget.onReplyConsumed(second, retried)
      return { ok: true, data: { ready: true } }
    })
    expect(cleaned).not.toHaveBeenCalled()
    expect(retried).not.toHaveBeenCalled()
    const before = s.receiver.diagnostic()
    expect(() => s.receiver.consume(new (class extends MainlineReplyReceipt {})())).toThrow(
      EngineError,
    )
    expect(() => s.receiver.consume(offered.receipt)).toThrow('cleanup remains owned')
    expect(cleaned).toHaveBeenCalledTimes(1)
    expect(s.receiver.diagnostic().holdingCount).toBe(before.holdingCount - 1)
    expect(s.receiver.diagnostic().deliveryBytes).toBe(before.deliveryBytes)
    expect(s.receiver.diagnostic().offered).toBe(1)
    fail = false
    s.receiver.consume(offered.receipt)
    s.receiver.consume(offered.receipt)
    expect(cleaned).toHaveBeenCalledTimes(1)
    expect(retried).toHaveBeenCalledTimes(2)
    expect(s.receiver.diagnostic().holdingCount).toBe(before.holdingCount - 2)
    expect(s.receiver.diagnostic().slots).toBe(0)
  })
  it('does not run registered cache retirement when the original delivery becomes UNKNOWN', async () => {
    const s = setup(),
      opened = await s.receiver.receive(s.open)
    s.receiver.consume(opened.receipt)
    const budget = s.supervisor.queryReadBudget(s.supervisor.mainlineProjectClient()!.owner)
    const entry = {},
      retire = vi.fn(() => budget.releaseHolding(entry))
    const before = s.receiver.diagnostic().holdingCount
    await expect(
      s.receiver.receive(async () => {
        budget.retainHolding(entry, { full: 'unacknowledged' })
        budget.onReplyConsumed(entry, retire)
        throw new Error('original delivery failure')
      }),
    ).rejects.toThrow('original delivery failure')
    expect(retire).not.toHaveBeenCalled()
    expect(s.receiver.diagnostic().holdingCount).toBe(before + 1)
    expect(s.receiver.diagnostic().unknown).toBe(1)
    expect(s.receiver.diagnostic().slots).toBe(1)
  })
})
