import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  createProjectCohortLifecycle,
  cohortHolderRoles,
  cohortLimits,
  type CohortEngineToken,
  type CohortHolderRole,
  type CohortOwnerToken,
  type CohortToken,
} from '../../apps/desktop/src/main/security/project-cohort-lifecycle'

type Lifecycle = ReturnType<typeof createProjectCohortLifecycle>
const boundary = { mechanismOnly: true, productionAdmission: 'unsupported' }
function good<T extends { ok: boolean }>(value: T): Extract<T, { ok: true }> {
  expect(value).toMatchObject({ ...boundary, ok: true })
  if (!value.ok) throw new Error('EXPECTED_MECHANISM_SUCCESS')
  return value as Extract<T, { ok: true }>
}
function deferred() {
  let resolve!: () => void
  let reject!: (value: unknown) => void
  const promise = new Promise<void>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
const flush = async () => {
  await Promise.resolve()
  await Promise.resolve()
}
function begin(lifecycle: Lifecycle, projectId = 'project-A', engine?: CohortEngineToken) {
  return good(
    lifecycle.prepareTransition({
      projectId,
      profileEpoch: 'profile-A',
      engine: engine ?? good(lifecycle.createEngineIdentity()).engine,
      reason: 'reopen',
    }),
  )
}
function owner(l: Lifecycle, c: CohortToken, role: CohortHolderRole) {
  return good(l.registerOwner(c, role)).owner
}
async function prepare(l: Lifecycle, model: 'disabled' | 'enabled' = 'disabled') {
  const candidate = begin(l)
  const roles: CohortHolderRole[] =
    model === 'enabled'
      ? cohortHolderRoles.filter((r) => r !== 'health-probe')
      : ['main-host', 'task-service', 'engine', 'store', 'worker', 'model-service']
  const registered = new Map<CohortHolderRole, CohortOwnerToken>()
  for (const role of roles) {
    const o = owner(l, candidate.candidate, role)
    registered.set(role, o)
    good(l.track(o, 'initialize', Promise.resolve()))
    good(l.track(o, 'binding', Promise.resolve()))
  }
  good(l.track(registered.get('store'), 'store-ready', Promise.resolve()))
  good(l.track(registered.get('worker'), 'job-ready', Promise.resolve()))
  good(l.track(registered.get('task-service'), 'scope-ready', Promise.resolve()))
  good(l.track(registered.get('model-service'), `model-${model}`, Promise.resolve()))
  await flush()
  return { ...candidate, registered }
}
afterEach(() => vi.useRealTimers())

describe('I06 cohort bookkeeping is mechanism-only', () => {
  it('cannot publish with missing owners, self-reported ready or an invented zero count', () => {
    const l = createProjectCohortLifecycle()
    const c = begin(l)
    expect(l.publish(c.transition)).toMatchObject({ ...boundary, ok: false, reason: 'incomplete' })
    const o = owner(l, c.candidate, 'main-host')
    expect(l.track(o, 'binding', { then: () => {}, count: 0 })).toMatchObject({
      ok: false,
      reason: 'invalid',
    })
    expect(l.registerOwner(c.candidate, 'unknown-role')).toMatchObject({ ok: false })
    expect(l.contentIo()).toEqual({ ...boundary, ok: false, reason: 'unsupported' })
  })

  it('publishes only after all role-bound initialization/binding and two ready layers plus scope', async () => {
    const l = createProjectCohortLifecycle()
    const c = await prepare(l)
    expect(good(l.publish(c.transition))).toMatchObject({ ...boundary, model: 'disabled' })
    expect(good(l.snapshot())).toMatchObject({
      active: c.candidate,
      candidate: null,
      transition: null,
    })
    expect(l.publish(c.transition)).toMatchObject({ ok: false, reason: 'stale' })
    expect(l.contentIo()).toMatchObject({ reason: 'unsupported' })
  })

  it('enabled models require the whole fixed indirect holder chain', async () => {
    const l = createProjectCohortLifecycle()
    const c = await prepare(l, 'enabled')
    expect(good(l.publish(c.transition))).toMatchObject({ model: 'enabled' })
    const l2 = createProjectCohortLifecycle()
    const c2 = await prepare(l2)
    good(l2.track(c2.registered.get('model-service'), 'model-enabled', Promise.resolve()))
    await flush()
    expect(l2.publish(c2.transition)).toMatchObject({ ok: false, reason: 'incomplete' })
  })

  it('disabled binding cannot hide a still-live model source owner', async () => {
    const l = createProjectCohortLifecycle()
    const c = await prepare(l)
    const source = owner(l, c.candidate, 'stored-result-source')
    expect(l.publish(c.transition)).toMatchObject({ ok: false, reason: 'incomplete' })
    good(l.releaseOwner(source, Promise.resolve()))
    await flush()
    expect(good(l.publish(c.transition))).toMatchObject({ model: 'disabled' })
  })

  it('rejects clone/foreign/wrong-role tokens and never exposes caller identity strings', () => {
    const l = createProjectCohortLifecycle(),
      other = createProjectCohortLifecycle()
    const c = begin(l),
      o = owner(l, c.candidate, 'main-host')
    expect(l.registerOwner({ ...c.candidate }, 'store')).toMatchObject({ ok: false })
    expect(other.inspect(c.candidate)).toMatchObject({ ok: false })
    expect(l.track({ ...o }, 'fs', Promise.resolve())).toMatchObject({ ok: false })
    expect(l.track(o, 'store-ready', Promise.resolve())).toMatchObject({
      ok: false,
      reason: 'invalid',
    })
    expect(JSON.stringify(l.inspect(c.candidate))).not.toContain('project-A')
    expect(JSON.stringify(l.snapshot())).not.toContain('profile-A')
  })

  it('keeps same-engine refresh/disconnect unchanged but same UUID new-engine requires full transition', async () => {
    const l = createProjectCohortLifecycle()
    const engine = good(l.createEngineIdentity()).engine
    const first = begin(l, 'same-project', engine)
    // Use a separate prepared cohort to exercise active recovery, then explicit replacement.
    good(l.abortCandidate(first.transition))
    expect(
      l.prepareTransition({
        projectId: 'same-project',
        profileEpoch: 'profile-A',
        engine,
        reason: 'reopen',
      }),
    ).toMatchObject({ ok: false })
    const active = await prepare(l)
    good(l.publish(active.transition))
    const snapshot = good(l.snapshot())
    // The active engine is deliberately not exposed by snapshot.
    expect(l.noteViewRecovery(active.candidate, engine, 'refresh')).toMatchObject({ ok: false })
    const next = await prepare(l)
    expect(l.publish(next.transition)).toMatchObject({ ok: false, reason: 'unsettled' })
    for (const old of active.registered.values()) good(l.releaseOwner(old, Promise.resolve()))
    await flush()
    good(l.publish(next.transition))
    expect(good(l.snapshot()).active).not.toBe(snapshot.active)
    expect(l.noteViewRecovery(active.candidate, engine, 'refresh')).toMatchObject({ ok: false })
  })

  it('accepts ordinary recovery only for the active actual engine identity', async () => {
    const l = createProjectCohortLifecycle(),
      engine = good(l.createEngineIdentity()).engine
    const c = begin(l, 'same-project', engine)
    const registered = new Map<CohortHolderRole, CohortOwnerToken>()
    for (const role of [
      'main-host',
      'task-service',
      'engine',
      'store',
      'worker',
      'model-service',
    ] as const) {
      const o = owner(l, c.candidate, role)
      registered.set(role, o)
      good(l.track(o, 'initialize', Promise.resolve()))
      good(l.track(o, 'binding', Promise.resolve()))
    }
    for (const [role, kind] of [
      ['store', 'store-ready'],
      ['worker', 'job-ready'],
      ['task-service', 'scope-ready'],
      ['model-service', 'model-disabled'],
    ] as const)
      good(l.track(registered.get(role), kind, Promise.resolve()))
    await flush()
    good(l.publish(c.transition))
    const before = l.snapshot()
    good(l.noteViewRecovery(c.candidate, engine, 'refresh'))
    good(l.noteViewRecovery(c.candidate, engine, 'same-engine-disconnect'))
    expect(l.snapshot()).toEqual(before)
    expect(
      l.prepareTransition({
        projectId: 'same-project',
        profileEpoch: 'profile-A',
        engine,
        reason: 'reopen',
      }),
    ).toMatchObject({ ok: false })
  })

  it('keeps picker and acquire slots across abort/epochs until real underlying settle', async () => {
    const l = createProjectCohortLifecycle()
    const c = begin(l),
      o = owner(l, c.candidate, 'main-host')
    const picker = deferred(),
      a = deferred(),
      b = deferred()
    const operation = good(l.track(o, 'picker', picker.promise)).operation
    good(l.track(o, 'acquire', a.promise))
    good(l.track(o, 'acquire', b.promise))
    good(l.cancelOperation(o, operation))
    good(l.abortCandidate(c.transition))
    const next = begin(l),
      nextOwner = owner(l, next.candidate, 'main-host')
    expect(l.track(nextOwner, 'picker', Promise.resolve())).toMatchObject({ reason: 'busy' })
    expect(l.track(nextOwner, 'acquire', Promise.resolve())).toMatchObject({ reason: 'busy' })
    expect(good(l.snapshot())).toMatchObject({ unsettled: 3, picker: 1, acquire: 2 })
    picker.resolve()
    a.resolve()
    await flush()
    expect(good(l.snapshot())).toMatchObject({ unsettled: 1, picker: 0, acquire: 1 })
    good(l.track(nextOwner, 'picker', Promise.resolve()))
    good(l.track(nextOwner, 'acquire', Promise.resolve()))
    b.resolve()
    await flush()
    expect(good(l.snapshot())).toMatchObject({ unsettled: 0 })
    expect(good(l.inspect(c.candidate)).phase).not.toBe('active')
  })

  it('does not turn a five-second timeout or early release success into drain', async () => {
    vi.useFakeTimers()
    let time = 0
    const l = createProjectCohortLifecycle(() => time)
    const c = begin(l),
      o = owner(l, c.candidate, 'engine'),
      child = deferred()
    good(l.track(o, 'child', child.promise))
    good(l.quiesce(c.candidate))
    good(l.releaseOwner(o, Promise.resolve()))
    await flush()
    const waiting = l.waitForDrain(c.candidate)
    time = 5000
    await vi.advanceTimersByTimeAsync(5000)
    expect(await waiting).toMatchObject({ ...boundary, ok: false, reason: 'unsettled' })
    expect(good(l.snapshot()).unsettled).toBe(1)
    child.resolve()
    await flush()
    expect(good(l.inspect(c.candidate)).phase).toBe('released')
  })

  it('old late init/release cannot install into a newer candidate or clear its owners', async () => {
    const l = createProjectCohortLifecycle()
    const old = begin(l),
      oldOwner = owner(l, old.candidate, 'model-service'),
      init = deferred()
    good(l.track(oldOwner, 'initialize', init.promise))
    good(l.abortCandidate(old.transition))
    const next = await prepare(l)
    init.resolve()
    good(l.releaseOwner(oldOwner, Promise.resolve()))
    await flush()
    const before = l.inspect(next.candidate)
    expect(good(l.publish(next.transition))).toMatchObject({ cohort: next.candidate })
    expect(good(before).owners).toHaveLength(6)
    expect(good(l.snapshot()).active).toBe(next.candidate)
    expect(l.publish(old.transition)).toMatchObject({ ok: false, reason: 'stale' })
  })

  it('release failures stay retained; failed initialization can drain but never publish', async () => {
    const l = createProjectCohortLifecycle(),
      c = begin(l),
      o = owner(l, c.candidate, 'engine')
    good(l.track(o, 'initialize', Promise.reject(new Error('PRIVATE_PATH_SECRET'))))
    await flush()
    good(l.quiesce(c.candidate))
    good(l.releaseOwner(o, Promise.resolve()))
    await flush()
    expect(good(l.inspect(c.candidate)).phase).toBe('released')
    expect(JSON.stringify(l.inspect(c.candidate))).not.toContain('PRIVATE_PATH_SECRET')
    const l2 = createProjectCohortLifecycle(),
      c2 = begin(l2),
      o2 = owner(l2, c2.candidate, 'store')
    good(l2.quiesce(c2.candidate))
    good(l2.releaseOwner(o2, Promise.reject({ secret: 'HIDDEN' })))
    await flush()
    expect(good(l2.inspect(c2.candidate)).phase).toBe('draining')
    expect(good(l2.inspect(c2.candidate)).owners[0]).toMatchObject({
      failed: true,
      state: 'draining',
    })
  })

  it('expires candidates at the exact monotonic deadline without releasing operations', async () => {
    let time = 0
    const l = createProjectCohortLifecycle(() => time),
      c = await prepare(l),
      o = c.registered.get('main-host')!
    const native = deferred()
    good(l.track(o, 'acquire', native.promise))
    time = 29999
    expect(good(l.inspect(c.candidate)).phase).toBe('candidate')
    time = 30000
    expect(good(l.inspect(c.candidate)).phase).toBe('draining')
    expect(l.publish(c.transition)).toMatchObject({ ok: false })
    expect(good(l.snapshot()).acquire).toBe(1)
    native.resolve()
    await flush()
    expect(good(l.snapshot()).acquire).toBe(0)
  })

  it('clock rollback, infinity or unknown thrown objects fail closed without inspecting the throw', () => {
    let time = 10
    const l = createProjectCohortLifecycle(() => time),
      c = begin(l)
    time = 9
    expect(l.publish(c.transition)).toMatchObject({ ok: false, reason: 'clock' })
    time = 11
    expect(l.createEngineIdentity()).toMatchObject({ ok: false, reason: 'clock' })
    expect(
      createProjectCohortLifecycle(() => Number.MAX_VALUE).createEngineIdentity(),
    ).toMatchObject({ reason: 'clock' })
    expect(createProjectCohortLifecycle(() => Infinity).createEngineIdentity()).toMatchObject({
      reason: 'clock',
    })
    const trap = new Proxy(
      {},
      {
        get() {
          throw new Error('MUST_NOT_READ_THROW')
        },
        getPrototypeOf() {
          throw new Error('MUST_NOT_READ_THROW')
        },
      },
    )
    expect(
      createProjectCohortLifecycle(() => {
        throw trap
      }).createEngineIdentity(),
    ).toMatchObject({ reason: 'clock' })
  })

  it('rejects getters, thenables, Promise proxies/subclasses and own species hooks without invoking them', () => {
    const l = createProjectCohortLifecycle(),
      c = begin(l),
      o = owner(l, c.candidate, 'main-host')
    let calls = 0
    const l2 = createProjectCohortLifecycle()
    const getter = {
      get projectId() {
        calls++
        return 'x'
      },
      profileEpoch: 'p',
      engine: {},
      reason: 'open',
    }
    expect(l2.prepareTransition(getter)).toMatchObject({ ok: false, reason: 'invalid' })
    const thenable = {
      get then() {
        calls++
        return () => {}
      },
    }
    expect(l.track(o, 'fs', thenable)).toMatchObject({ reason: 'invalid' })
    expect(
      l.track(
        o,
        'fs',
        new Proxy(Promise.resolve(), {
          get() {
            calls++
            return undefined
          },
        }),
      ),
    ).toMatchObject({ reason: 'invalid' })
    class SubPromise extends Promise<void> {}
    expect(l.track(o, 'fs', new SubPromise((resolve) => resolve()))).toMatchObject({
      reason: 'invalid',
    })
    const p = Promise.resolve()
    Object.defineProperty(p, 'constructor', {
      get() {
        calls++
        throw new Error()
      },
    })
    expect(l.track(o, 'fs', p)).toMatchObject({ reason: 'invalid' })
    expect(calls).toBe(0)
  })

  it('fences Proxy and clock reentry before installing owner/transition state', () => {
    let reenter = false
    const l = createProjectCohortLifecycle(() => {
      if (reenter) expect(l.close()).toMatchObject({ ok: false, reason: 'busy' })
      return 1
    })
    reenter = true
    const engine = good(l.createEngineIdentity()).engine
    const context = new Proxy(
      { projectId: 'p', profileEpoch: 'e', engine, reason: 'open' },
      {
        ownKeys(target) {
          expect(l.close()).toMatchObject({ reason: 'busy' })
          return Reflect.ownKeys(target)
        },
      },
    )
    const c = good(l.prepareTransition(context))
    expect(good(l.snapshot()).closed).toBe(false)
    expect(good(l.inspect(c.candidate)).phase).toBe('candidate')
  })

  it('rejects wrong-owner cancellation and duplicate Promise registration', async () => {
    const l = createProjectCohortLifecycle(),
      c = begin(l),
      a = owner(l, c.candidate, 'main-host'),
      b = owner(l, c.candidate, 'engine'),
      d = deferred()
    const operation = good(l.track(a, 'fs', d.promise)).operation
    expect(l.track(b, 'fs', d.promise)).toMatchObject({ reason: 'invalid' })
    expect(l.cancelOperation(b, operation)).toMatchObject({ reason: 'invalid' })
    good(l.cancelOperation(a, operation))
    d.resolve()
    await flush()
    expect(l.cancelOperation(a, operation)).toMatchObject({ reason: 'stale' })
  })

  it('bounds owners, per-owner pending and transition count; frozen snapshots cannot mutate internals', () => {
    const l = createProjectCohortLifecycle(),
      c = begin(l),
      o = owner(l, c.candidate, 'main-host')
    expect(l.registerOwner(c.candidate, 'main-host')).toMatchObject({ reason: 'invalid' })
    expect(l.prepareTransition({})).toMatchObject({ reason: 'busy' })
    for (let i = 0; i < cohortLimits.perOwner; i++) good(l.track(o, 'fs', new Promise(() => {})))
    expect(l.track(o, 'fs', Promise.resolve())).toMatchObject({ reason: 'budget' })
    const view = good(l.inspect(c.candidate))
    expect(Object.isFrozen(view)).toBe(true)
    expect(Object.isFrozen(view.owners)).toBe(true)
    expect(Object.isFrozen(view.owners[0])).toBe(true)
    expect(() => {
      ;(view.owners as unknown[]).pop()
    }).toThrow()
    expect(good(l.inspect(c.candidate)).owners).toHaveLength(1)
  })

  it('lifetime token exhaustion is finite, permanent and never wraps an epoch', () => {
    const l = createProjectCohortLifecycle(() => 0)
    for (let i = 0; i < cohortLimits.issuedTokens; i++) good(l.createEngineIdentity())
    expect(l.createEngineIdentity()).toMatchObject({ ok: false, reason: 'budget' })
    expect(l.createEngineIdentity()).toMatchObject({ ok: false, reason: 'budget' })
  })

  it('close preserves pending and allows only cleanup; no stale completion can publish', async () => {
    const l = createProjectCohortLifecycle(),
      c = begin(l),
      o = owner(l, c.candidate, 'main-host'),
      d = deferred()
    good(l.track(o, 'picker', d.promise))
    expect(good(l.close()).unsettled).toBe(1)
    expect(l.track(o, 'fs', Promise.resolve())).toMatchObject({ reason: 'closed' })
    good(l.releaseOwner(o, Promise.resolve()))
    await flush()
    expect(good(l.snapshot()).unsettled).toBe(1)
    d.resolve()
    await flush()
    expect(good(l.snapshot()).unsettled).toBe(0)
    expect(l.publish(c.transition)).toMatchObject({ reason: 'closed' })
  })

  it('a ready active cohort can retain real child/Store lifetime promises, then replacement waits for them', async () => {
    const l = createProjectCohortLifecycle(),
      first = await prepare(l)
    const child = deferred(),
      connection = deferred()
    good(l.track(first.registered.get('engine'), 'child', child.promise))
    good(l.track(first.registered.get('store'), 'store-connection', connection.promise))
    good(l.publish(first.transition))
    const next = await prepare(l)
    for (const o of first.registered.values()) good(l.releaseOwner(o, Promise.resolve()))
    await flush()
    expect(l.publish(next.transition)).toMatchObject({ reason: 'unsettled' })
    child.resolve()
    await flush()
    expect(l.publish(next.transition)).toMatchObject({ reason: 'unsettled' })
    connection.resolve()
    await flush()
    good(l.publish(next.transition))
  })

  it('shares drain waiting without multiplying timers and wakes closed waits safely', async () => {
    vi.useFakeTimers()
    const l = createProjectCohortLifecycle(() => 0),
      c = begin(l),
      o = owner(l, c.candidate, 'engine')
    good(l.track(o, 'child', new Promise(() => {})))
    good(l.quiesce(c.candidate))
    const first = l.waitForDrain(c.candidate)
    for (let i = 0; i < 100; i++) expect(l.waitForDrain(c.candidate)).toBe(first)
    expect(vi.getTimerCount()).toBe(1)
    good(l.close())
    await flush()
    expect(await first).toMatchObject({ reason: 'closed' })
    expect(vi.getTimerCount()).toBe(0)
  })

  it.each(['initialize', 'binding', 'store-ready', 'job-ready', 'scope-ready'] as const)(
    'missing %s proof leaves active pointer unchanged',
    async (missing) => {
      const l = createProjectCohortLifecycle(),
        c = begin(l)
      const registered = new Map<CohortHolderRole, CohortOwnerToken>()
      for (const role of [
        'main-host',
        'task-service',
        'engine',
        'store',
        'worker',
        'model-service',
      ] as const) {
        const o = owner(l, c.candidate, role)
        registered.set(role, o)
        if (missing !== 'initialize') good(l.track(o, 'initialize', Promise.resolve()))
        if (missing !== 'binding') good(l.track(o, 'binding', Promise.resolve()))
      }
      for (const [role, kind] of [
        ['store', 'store-ready'],
        ['worker', 'job-ready'],
        ['task-service', 'scope-ready'],
        ['model-service', 'model-disabled'],
      ] as const)
        if (kind !== missing) good(l.track(registered.get(role), kind, Promise.resolve()))
      await flush()
      expect(l.publish(c.transition)).toMatchObject({ reason: 'incomplete' })
      expect(good(l.snapshot()).active).toBeNull()
    },
  )

  it('keeps the global operation and retained-cohort bounds across abandoned candidates', () => {
    const l = createProjectCohortLifecycle()
    for (let i = 0; i < cohortLimits.retainedCohorts; i++) {
      const c = begin(l),
        o = owner(l, c.candidate, 'main-host')
      good(l.track(o, 'fs', new Promise(() => {})))
      good(l.abortCandidate(c.transition))
    }
    const engine = good(l.createEngineIdentity()).engine
    expect(
      l.prepareTransition({ projectId: 'p', profileEpoch: 'p', reason: 'open', engine }),
    ).toMatchObject({ reason: 'budget' })
    expect(good(l.snapshot()).unsettled).toBe(cohortLimits.retainedCohorts)
    const l2 = createProjectCohortLifecycle(),
      c2 = begin(l2)
    for (const role of cohortHolderRoles.slice(0, 8)) {
      const o = owner(l2, c2.candidate, role)
      for (let j = 0; j < cohortLimits.perOwner; j++) good(l2.track(o, 'fs', new Promise(() => {})))
    }
    const more = owner(l2, c2.candidate, cohortHolderRoles[8])
    expect(l2.track(more, 'fs', Promise.resolve())).toMatchObject({ reason: 'budget' })
    expect(good(l2.snapshot()).unsettled).toBe(cohortLimits.operations)
  })

  it.each(['ownKeys', 'getOwnPropertyDescriptor'] as const)(
    'capture %s cannot install an expired half-candidate or quiesce the active cohort',
    async (trap) => {
      let time = 0
      const l = createProjectCohortLifecycle(() => time),
        current = await prepare(l)
      good(l.publish(current.transition))
      const engine = good(l.createEngineIdentity()).engine
      const input = { projectId: 'project-A', profileEpoch: 'profile-A', engine, reason: 'reopen' }
      const raw = new Proxy(input, {
        ownKeys(target) {
          if (trap === 'ownKeys') time = 30000
          return Reflect.ownKeys(target)
        },
        getOwnPropertyDescriptor(target, key) {
          if (trap === 'getOwnPropertyDescriptor') time = 30000
          return Reflect.getOwnPropertyDescriptor(target, key)
        },
      })
      expect(l.prepareTransition(raw)).toMatchObject({ ok: false, reason: 'expired' })
      expect(good(l.snapshot())).toMatchObject({
        active: current.candidate,
        candidate: null,
        transition: null,
      })
      expect(good(l.inspect(current.candidate)).phase).toBe('active')
      // Failure did not consume/rebind this otherwise unused engine identity.
      good(l.prepareTransition(input))
    },
  )

  it('publish rechecks the monotonic deadline immediately before the pointer swap', async () => {
    let armed = false,
      calls = 0
    const l = createProjectCohortLifecycle(() => (armed && ++calls >= 2 ? 30000 : 0))
    const c = await prepare(l)
    armed = true
    expect(l.publish(c.transition)).toMatchObject({ ok: false, reason: 'expired' })
    expect(good(l.snapshot()).active).toBeNull()
  })

  it.each([
    ['child', 'engine', 'candidate'],
    ['store-connection', 'store', 'candidate'],
    ['child', 'engine', 'active'],
    ['store-connection', 'store', 'active'],
  ] as const)(
    '%s lifetime ending in %s holder during %s invalidates the whole cohort',
    async (kind, role, phase) => {
      const l = createProjectCohortLifecycle(),
        c = await prepare(l),
        lifetime = deferred()
      const holder = c.registered.get(role)!
      good(l.track(holder, kind, lifetime.promise))
      if (phase === 'active') good(l.publish(c.transition))
      lifetime.resolve()
      await flush()
      expect(good(l.inspect(c.candidate)).phase).toBe('draining')
      expect(l.publish(c.transition)).toMatchObject({ ok: false })
      // Even a sibling owner may not admit new work after the lifetime ends.
      expect(l.track(c.registered.get('main-host'), 'fs', Promise.resolve())).toMatchObject({
        ok: false,
        reason: 'stale',
      })
      expect(good(l.inspect(c.candidate)).owners.every((o) => o.state === 'draining')).toBe(true)
      if (phase === 'active') {
        // The old engine identity is not exposed; neither a clone nor a same-kind
        // token may turn this terminal active cohort into ordinary recovery.
        const nextEngine = good(l.createEngineIdentity()).engine
        expect(l.noteViewRecovery(c.candidate, nextEngine, 'refresh')).toMatchObject({ ok: false })
      }
    },
  )
})
