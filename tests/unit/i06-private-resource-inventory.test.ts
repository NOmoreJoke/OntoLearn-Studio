import { describe, expect, it } from 'vitest'
import {
  createPrivateResourceInventory,
  inventoryOwnerRoles,
  type InventoryOwner,
  type InventoryOwnerRole,
  type MetadataIdentity,
  type ProtectedResource,
} from '../../apps/desktop/src/main/security/private-resource-inventory'

const context = { processEpoch: 'process-1', profileEpoch: 'profile-1' }
const identity = (
  fileId: string,
  type: 'directory' | 'file' = 'file',
  links = 1,
): MetadataIdentity => ({ kind: 'posix', volume: 'volume-1', fileId, type, links })
const entry = (
  name: string,
  category: ProtectedResource['category'] = 'private-deny',
  links = 1,
): ProtectedResource => ({
  id: name,
  category,
  kind: 'member',
  parent: identity('parent', 'directory'),
  components: [name],
  identity: identity(name, 'file', links),
  presence: 'present',
  state: 'active',
})
const initial = (role: InventoryOwnerRole): ProtectedResource[] => {
  if (role === 'profile' || role === 'private-root')
    return [
      {
        ...entry(role, role === 'profile' ? 'profile-container' : 'private-deny'),
        kind: 'root',
        identity: identity(role, 'directory'),
      },
    ]
  if (role === 'credentials') return [entry('record-1')]
  if (role === 'database') return [entry('database-1', 'database-managed')]
  return []
}
function value<T>(r: { ok: true; value: T } | { ok: false; reason: string }): T {
  if (!r.ok) throw new Error(`unexpected fixed failure: ${r.reason}`)
  return r.value
}
function deferred() {
  let resolve!: () => void, reject!: () => void
  const promise = new Promise<void>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
function setup(options: Parameters<typeof createPrivateResourceInventory>[1] = {}) {
  const inventory = createPrivateResourceInventory(context, options)
  const owners = Object.fromEntries(
    inventoryOwnerRoles.map((r) => [r, value(inventory.registerOwner(r))]),
  ) as Record<InventoryOwnerRole, InventoryOwner>
  function payload(role: InventoryOwnerRole, list = initial(role), status = 'complete') {
    return {
      ...context,
      profileEpoch: inventory.inspect().profileEpoch,
      revision: inventory.inspect().revision,
      status,
      coverage: list.length || role === 'retirement' ? 'present' : 'confirmed-absent',
      retirementSource: role === 'retirement' ? 'mechanism-restored' : 'not-owner',
      resources: structuredClone(list),
    }
  }
  function round(overrides: Partial<Record<InventoryOwnerRole, ProtectedResource[]>> = {}) {
    for (const role of inventoryOwnerRoles)
      value(
        inventory.observe(
          value(inventory.beginObservation(owners[role])),
          payload(role, overrides[role] ?? initial(role)),
        ),
      )
    return inventory.inspect()
  }
  return { inventory, owners, payload, round }
}

describe('I06 mechanism-only resource inventory', () => {
  it('external mutation of exported roles cannot remove mandatory retirement or owners', () => {
    const original = [...inventoryOwnerRoles]
    const exposed = inventoryOwnerRoles as unknown as string[]
    try {
      try {
        exposed.splice(2)
      } catch {
        /* immutable expected set */
      }
      const inventory = createPrivateResourceInventory(context)
      const registered = (['profile', 'private-root'] as const).map((role) => ({
        role,
        owner: value(inventory.registerOwner(role)),
      }))
      for (const { role, owner } of registered) {
        value(
          inventory.observe(value(inventory.beginObservation(owner)), {
            ...context,
            revision: inventory.inspect().revision,
            status: 'complete',
            coverage: 'present',
            retirementSource: 'not-owner',
            resources: initial(role),
          }),
        )
      }
      expect(inventory.inspect().state).not.toBe('complete')
      expect(inventory.issueSnapshot().ok).toBe(false)
    } finally {
      if (!Object.isFrozen(exposed)) exposed.splice(0, exposed.length, ...original)
    }
  })
  it('release settlement updates the stable retained record after another full observation', async () => {
    const s = setup()
    s.round()
    const d = deferred()
    const tracked = value(
      s.inventory.trackDatabaseRelease(s.owners.database, ['database-1'], d.promise),
    )
    const retired = { ...entry('database-1', 'database-managed'), state: 'retired' as const }
    s.round({ database: [retired] })
    d.resolve()
    await tracked
    expect(s.inventory.inspect().actualUnsettledReleases).toBe(0)
    expect(s.inventory.inspect().protected.find((r) => r.id === 'database-1')?.state).toBe(
      'released-retained',
    )
  })
  it('never infers empty completeness from constructor or absent owners', () => {
    const i = createPrivateResourceInventory(context)
    expect(i.inspect()).toMatchObject({
      state: 'incomplete',
      productionAdmission: 'unsupported',
      mechanismOnly: true,
      protected: [],
    })
    expect(i.issueSnapshot()).toMatchObject({ ok: false, reason: 'incomplete' })
    expect(createPrivateResourceInventory({ ...context, extra: true }).inspect().state).toBe(
      'failed',
    )
  })
  it('requires every finite owner and independent restored-retirement evidence', () => {
    const s = setup()
    for (const role of inventoryOwnerRoles) {
      const p = s.payload(role)
      if (role === 'retirement') p.retirementSource = 'unavailable'
      value(s.inventory.observe(value(s.inventory.beginObservation(s.owners[role])), p))
    }
    expect(s.inventory.inspect().state).toBe('unknown')
    expect(s.inventory.inspect().protected.length).toBe(4)
  })
  it('complete means synthetic metadata consistency, never production admission', () => {
    const s = setup()
    expect(s.round()).toMatchObject({
      state: 'complete',
      productionAdmission: 'unsupported',
      mechanismOnly: true,
    })
    expect(value(s.inventory.issueSnapshot()).view.productionAdmission).toBe('unsupported')
  })
  it('rejects clone, foreign owners, duplicate registration and unknown role', () => {
    const s = setup(),
      other = setup()
    expect(s.inventory.beginMutation({ ...s.owners.profile })).toMatchObject({
      ok: false,
      reason: 'stale',
    })
    expect(s.inventory.beginObservation(other.owners.profile)).toMatchObject({
      ok: false,
      reason: 'stale',
    })
    expect(s.inventory.registerOwner('profile')).toMatchObject({ ok: false, reason: 'conflict' })
    expect(s.inventory.registerOwner('renderer-safe')).toMatchObject({
      ok: false,
      reason: 'invalid',
    })
  })
  it.each(['processEpoch', 'profileEpoch', 'revision'])('rejects mixed observation %s', (key) => {
    const s = setup(),
      observation = value(s.inventory.beginObservation(s.owners.profile))
    expect(
      s.inventory.observe(observation, {
        ...s.payload('profile'),
        [key]: key === 'revision' ? 0 : 'another',
      }),
    ).toMatchObject({ ok: false })
    expect(s.inventory.inspect().state).not.toBe('complete')
  })
  it('initialization failure retains protected data and recovers only in a new observation revision', () => {
    const s = setup()
    for (const role of inventoryOwnerRoles)
      value(
        s.inventory.observe(
          value(s.inventory.beginObservation(s.owners[role])),
          s.payload(role, initial(role), role === 'credentials' ? 'failed' : 'complete'),
        ),
      )
    expect(s.inventory.inspect().state).toBe('failed')
    expect(s.inventory.inspect().protected.some((r) => r.id === 'record-1')).toBe(true)
    expect(s.inventory.beginObservation(s.owners.credentials)).toMatchObject({
      ok: false,
      reason: 'conflict',
    })
    value(s.inventory.beginMutation(s.owners.credentials))
    expect(s.round().state).toBe('complete')
  })
  it('reserve and mutation synchronously invalidate old observations and snapshots', () => {
    const s = setup()
    s.round()
    const snapshot = value(s.inventory.issueSnapshot()).token
    value(s.inventory.beginMutation(s.owners.credentials))
    const observation = value(s.inventory.beginObservation(s.owners.credentials))
    value(s.inventory.reserve(s.owners.credentials, [entry('record-2')]))
    expect(s.inventory.checkSnapshot(snapshot)).toMatchObject({ ok: false, reason: 'stale' })
    expect(s.inventory.observe(observation, s.payload('credentials'))).toMatchObject({
      ok: false,
      reason: 'stale',
    })
    expect(s.inventory.inspect().protected.map((r) => r.id)).toContain('record-1')
    expect(s.inventory.inspect().protected.map((r) => r.id)).toContain('record-2')
  })
  it('prospective metadata binds parent and exact name and can record later materialization', () => {
    const s = setup(),
      future = { ...entry('pending-1'), identity: null, presence: 'absent' as const }
    value(s.inventory.reserve(s.owners.credentials, [future]))
    const actual = entry('pending-1')
    expect(s.round({ credentials: [entry('record-1'), actual] }).state).toBe('complete')
    expect(
      s.inventory.inspect().protected.find((r) => r.id === 'pending-1')?.identity?.fileId,
    ).toBe('pending-1')
  })
  it.each(['..', '.', '/escape', 'a\\b', 'file:stream', '\u0000', ''])(
    'rejects unsupported component %j without changing records',
    (component) => {
      const s = setup()
      expect(
        s.inventory.reserve(s.owners.credentials, [{ ...entry('bad'), components: [component] }]),
      ).toMatchObject({ ok: false })
      expect(s.inventory.inspect().protected).toEqual([])
    },
  )
  it('strict native fields and size bounds do not truncate to complete', () => {
    const s = setup()
    expect(
      s.inventory.reserve(s.owners.credentials, [
        { ...entry('bad'), identity: { ...identity('bad'), secret: 'not-accepted' } },
      ]),
    ).toMatchObject({ ok: false })
    expect(
      s.inventory.reserve(
        s.owners.credentials,
        Array.from({ length: 32769 }, (_, n) => entry(`r-${n}`)),
      ),
    ).toMatchObject({ ok: false })
    const roots = Array.from({ length: 33 }, (_, n) => ({
      ...entry(`root-${n}`),
      kind: 'root' as const,
      identity: identity(`root-${n}`, 'directory'),
    }))
    expect(s.inventory.reserve(s.owners['private-root'], roots)).toMatchObject({ ok: false })
    expect(s.inventory.inspect().protected).toEqual([])
  })
  it('rejects getters and safely denies reentry during capture', () => {
    const s = setup()
    let calls = 0
    const raw = {
      get resources() {
        calls++
        return []
      },
    }
    expect(s.inventory.reserve(s.owners.credentials, raw)).toMatchObject({ ok: false })
    expect(calls).toBe(0)
    let nested: unknown
    const proxy = new Proxy([entry('r')], {
      ownKeys(target) {
        nested = s.inventory.beginMutation(s.owners.credentials)
        return Reflect.ownKeys(target)
      },
    })
    value(s.inventory.reserve(s.owners.credentials, proxy))
    expect(nested).toMatchObject({ ok: false, reason: 'busy' })
  })
  it('same-value profile reopen invalidates old objects and retains retired paths', () => {
    const s = setup()
    s.round()
    const snapshot = value(s.inventory.issueSnapshot()).token
    value(s.inventory.beginMutation(s.owners.credentials))
    const observation = value(s.inventory.beginObservation(s.owners.credentials))
    value(s.inventory.startProfile(context.profileEpoch))
    expect(s.inventory.beginMutation(s.owners.profile)).toMatchObject({
      ok: false,
      reason: 'stale',
    })
    expect(s.inventory.observe(observation, s.payload('credentials'))).toMatchObject({
      ok: false,
      reason: 'stale',
    })
    expect(s.inventory.checkSnapshot(snapshot)).toMatchObject({ ok: false, reason: 'stale' })
    expect(s.inventory.inspect().protected).toHaveLength(4)
    expect(s.inventory.inspect().protected.every((r) => r.state === 'retired')).toBe(true)
    expect(s.inventory.inspect().state).toBe('incomplete')
  })
  it('requires distinct names to close all private hard links', () => {
    const a = { ...entry('a', 'private-deny', 3), identity: identity('same', 'file', 3) }
    const b = { ...entry('b', 'private-deny', 3), identity: identity('same', 'file', 3) }
    expect(setup().round({ credentials: [a, b] }).state).toBe('unknown')
    const two = [a, b].map((r) => ({ ...r, identity: identity('same', 'file', 2) }))
    expect(setup().round({ credentials: two }).state).toBe('complete')
    expect(setup().round({ database: [{ ...entry('alias', 'database-managed', 2) }] }).state).toBe(
      'unknown',
    )
  })
  it('retains an absent pending name while checking only current directory entries', () => {
    const s = setup()
    const pair = ['final', 'pending'].map((name) => ({
      ...entry(name),
      identity: identity('shared', 'file', 2),
    }))
    expect(s.round({ credentials: pair }).state).toBe('complete')
    value(s.inventory.beginMutation(s.owners.credentials))
    const after = [
      { ...pair[0], identity: identity('shared', 'file', 1) },
      { ...pair[1], state: 'retired' as const, presence: 'absent' as const },
    ]
    expect(s.round({ credentials: after }).state).toBe('complete')
    expect(
      s.inventory.inspect().protected.some((r) => r.id === 'pending' && r.presence === 'absent'),
    ).toBe(true)
  })
  it('cannot erase old protected entries by replacing a complete list or relabel identity', () => {
    const s = setup()
    s.round()
    value(s.inventory.beginMutation(s.owners.credentials))
    const token = value(s.inventory.beginObservation(s.owners.credentials))
    expect(s.inventory.observe(token, s.payload('credentials', []))).toMatchObject({ ok: false })
    expect(s.inventory.inspect().protected.some((r) => r.id === 'record-1')).toBe(true)
    value(s.inventory.beginMutation(s.owners.credentials))
    expect(
      s.inventory.reserve(s.owners.credentials, [
        { ...entry('record-1'), identity: identity('replacement') },
      ]),
    ).toMatchObject({ ok: false })
    expect(s.inventory.inspect().protected.find((r) => r.id === 'record-1')?.identity?.fileId).toBe(
      'record-1',
    )
  })
  it('deeply freezes captured records and returned collections', () => {
    const s = setup(),
      source = entry('record-1')
    value(s.inventory.reserve(s.owners.credentials, [source]))
    ;(source.components as string[])[0] = 'changed'
    const view = s.inventory.inspect()
    expect(view.protected[0].components[0]).toBe('record-1')
    expect(() => (view.protected as ProtectedResource[]).pop()).toThrow()
    expect(() => (view.protected[0].components as string[]).push('escape')).toThrow()
  })
  it('snapshot identity, nonrenewing TTL and issuance budget are finite', () => {
    let clock = 0
    const s = setup({ now: () => clock })
    s.round()
    const tokens = Array.from({ length: 16 }, () => value(s.inventory.issueSnapshot()).token)
    expect(s.inventory.issueSnapshot()).toMatchObject({ ok: false, reason: 'budget' })
    expect(s.inventory.checkSnapshot({ ...tokens[0] })).toMatchObject({
      ok: false,
      reason: 'stale',
    })
    clock = 29999
    expect(s.inventory.checkSnapshot(tokens[0]).ok).toBe(true)
    clock = 30000
    expect(s.inventory.checkSnapshot(tokens[0])).toMatchObject({ ok: false, reason: 'expired' })
    expect(s.inventory.issueSnapshot().ok).toBe(true)
  })
  it('enforces observation deadline after capture, not merely on entry', () => {
    let clock = 0
    const s = setup({ now: () => clock })
    const token = value(s.inventory.beginObservation(s.owners.profile))
    const raw = new Proxy(s.payload('profile'), {
      ownKeys(target) {
        clock = 5000
        return Reflect.ownKeys(target)
      },
    })
    expect(s.inventory.observe(token, raw)).toMatchObject({ ok: false, reason: 'expired' })
    expect(s.inventory.inspect().protected).toEqual([])
  })
  it('clock rollback and exhausted sequence fail closed without discarding protection', () => {
    let clock = 10
    const s = setup({ now: () => clock })
    s.round()
    clock = 9
    expect(s.inventory.issueSnapshot()).toMatchObject({ ok: false, reason: 'failed' })
    expect(s.inventory.inspect()).toMatchObject({ state: 'failed', protected: expect.any(Array) })
    expect(s.inventory.inspect().protected).toHaveLength(4)
    const tiny = createPrivateResourceInventory(context, { sequenceLimit: 1 })
    value(tiny.registerOwner('profile'))
    expect(tiny.registerOwner('private-root')).toMatchObject({ ok: false, reason: 'failed' })
    const revisions = createPrivateResourceInventory(context, { revisionLimit: 1 })
    value(revisions.registerOwner('profile'))
    expect(revisions.registerOwner('private-root')).toMatchObject({ ok: false, reason: 'failed' })
  })
  it('clock errors and values too large to add a precise deadline are terminal', () => {
    for (const now of [
      () => Number.MAX_VALUE,
      () => {
        throw Object.create(null)
      },
    ]) {
      const inventory = createPrivateResourceInventory(context, { now })
      expect(inventory.registerOwner('profile')).toMatchObject({ ok: false, reason: 'failed' })
      expect(inventory.inspect().state).toBe('failed')
    }
  })
  it('actual release Promise stays counted through time and close, then preserves released-retained DB', async () => {
    let clock = 0
    const s = setup({ now: () => clock })
    s.round()
    const d = deferred(),
      tracked = value(
        s.inventory.trackDatabaseRelease(s.owners.database, ['database-1'], d.promise),
      )
    clock = 60000
    expect(s.inventory.inspect().actualUnsettledReleases).toBe(1)
    expect(s.inventory.inspect().protected.find((r) => r.id === 'database-1')?.state).toBe(
      'retired',
    )
    value(s.inventory.close())
    expect(s.inventory.inspect().actualUnsettledReleases).toBe(1)
    d.resolve()
    await tracked
    expect(s.inventory.inspect()).toMatchObject({ state: 'closed', actualUnsettledReleases: 0 })
    expect(s.inventory.inspect().protected.find((r) => r.id === 'database-1')?.state).toBe(
      'released-retained',
    )
    expect(s.inventory.issueSnapshot()).toMatchObject({ ok: false, reason: 'closed' })
  })
  it('release failure is unknown, never an empty or released inventory', async () => {
    const s = setup()
    s.round()
    const d = deferred()
    const result = value(
      s.inventory.trackDatabaseRelease(s.owners.database, ['database-1'], d.promise),
    )
    d.reject()
    await result
    expect(s.inventory.inspect()).toMatchObject({ state: 'unknown', actualUnsettledReleases: 0 })
    expect(s.inventory.inspect().protected.find((r) => r.id === 'database-1')?.state).toBe(
      'retired',
    )
  })
  it('rejects thenable/self-reported release and retains two real unfinished slots', async () => {
    const s = setup()
    s.round({ database: [1, 2, 3].map((n) => entry(`db-${n}`, 'database-managed')) })
    expect(
      s.inventory.trackDatabaseRelease(s.owners.database, ['db-1'], {
        then() {
          throw Error('should not run')
        },
      }),
    ).toMatchObject({ ok: false, reason: 'invalid' })
    const decorated = Promise.resolve()
    Object.defineProperty(decorated, 'then', {
      get() {
        throw Error('do not read')
      },
    })
    expect(s.inventory.trackDatabaseRelease(s.owners.database, ['db-1'], decorated)).toMatchObject({
      ok: false,
      reason: 'invalid',
    })
    const a = deferred(),
      b = deferred(),
      c = deferred()
    const first = value(s.inventory.trackDatabaseRelease(s.owners.database, ['db-1'], a.promise))
    const second = value(s.inventory.trackDatabaseRelease(s.owners.database, ['db-2'], b.promise))
    expect(s.inventory.trackDatabaseRelease(s.owners.database, ['db-3'], c.promise)).toMatchObject({
      ok: false,
      reason: 'budget',
    })
    a.resolve()
    await first
    const third = value(s.inventory.trackDatabaseRelease(s.owners.database, ['db-3'], c.promise))
    b.resolve()
    c.resolve()
    await Promise.all([second, third])
    expect(
      s.inventory.inspect().protected.filter((r) => r.state === 'released-retained'),
    ).toHaveLength(3)
  })
  it('cannot reuse one release Promise concurrently or after it settled for another DB', async () => {
    const s = setup()
    s.round({ database: [1, 2, 3].map((n) => entry(`db-${n}`, 'database-managed')) })
    const d = deferred(),
      first = value(s.inventory.trackDatabaseRelease(s.owners.database, ['db-1'], d.promise))
    const simultaneous = s.inventory.trackDatabaseRelease(s.owners.database, ['db-2'], d.promise)
    d.resolve()
    await first
    expect(simultaneous).toMatchObject({ ok: false, reason: 'invalid' })
    expect(s.inventory.trackDatabaseRelease(s.owners.database, ['db-3'], d.promise)).toMatchObject({
      ok: false,
      reason: 'invalid',
    })
  })
  it('old fulfilled release Promise cannot supply a new profile owner release', async () => {
    const s = setup()
    s.round()
    const d = deferred()
    const first = value(
      s.inventory.trackDatabaseRelease(s.owners.database, ['database-1'], d.promise),
    )
    d.resolve()
    await first
    value(s.inventory.startProfile('profile-2'))
    const newOwner = value(s.inventory.registerOwner('database'))
    value(s.inventory.reserve(newOwner, [entry('new-db', 'database-managed')]))
    expect(s.inventory.trackDatabaseRelease(newOwner, ['new-db'], d.promise)).toMatchObject({
      ok: false,
      reason: 'invalid',
    })
    expect(s.inventory.inspect().protected.find((r) => r.id === 'new-db')?.state).toBe('active')
  })
  it('old release completion can only retire its original record after profile reopen', async () => {
    const s = setup()
    s.round()
    const d = deferred()
    const tracked = value(
      s.inventory.trackDatabaseRelease(s.owners.database, ['database-1'], d.promise),
    )
    value(s.inventory.startProfile(context.profileEpoch))
    d.resolve()
    await tracked
    expect(s.inventory.inspect().state).toBe('incomplete')
    expect(s.inventory.inspect().protected.find((r) => r.id === 'database-1')?.state).toBe(
      'released-retained',
    )
    expect(s.inventory.beginMutation(s.owners.database)).toMatchObject({
      ok: false,
      reason: 'stale',
    })
  })
})
