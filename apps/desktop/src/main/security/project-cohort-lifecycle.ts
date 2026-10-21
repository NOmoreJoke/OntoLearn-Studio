import { types } from 'node:util'

const boundary = { mechanismOnly: true, productionAdmission: 'unsupported' } as const
export const cohortLimits = Object.freeze({
  candidateMs: 30000,
  waitMs: 5000,
  picker: 1,
  acquire: 2,
  operations: 256,
  perOwner: 32,
  retainedCohorts: 32,
  // Finite lifetime issuance budget; exhaustion requires a new mechanism instance.
  issuedTokens: 65536,
})
export const cohortHolderRoles = Object.freeze([
  'main-host',
  'task-service',
  'engine',
  'store',
  'worker',
  'model-service',
  'gateway-application',
  'stored-result-source',
  'field-projector',
  'gateway-core',
  'credential-boundary',
  'configuration-repository',
  'ciphertext-repository',
  'audit-repository',
  'private-directory',
  'transport',
  'health-probe',
] as const)
export type CohortHolderRole = (typeof cohortHolderRoles)[number]
const kinds = [
  'initialize',
  'fs',
  'source',
  'network',
  // Whole-cohort engine/Store ownership lifetime, not a restartable transport
  // session. Future B/T01 owners must aggregate actual child/connection terminal
  // evidence after permanent stopAndDrain before settling these promises.
  'child',
  'store-connection',
  'store',
  'picker',
  'acquire',
  'binding',
  'store-ready',
  'job-ready',
  'scope-ready',
  'model-enabled',
  'model-disabled',
  'release',
] as const
export type CohortOperationKind = (typeof kinds)[number]
type Reason =
  | 'invalid'
  | 'busy'
  | 'stale'
  | 'closed'
  | 'expired'
  | 'unsettled'
  | 'failed'
  | 'incomplete'
  | 'budget'
  | 'clock'
  | 'unsupported'
type Mechanism = typeof boundary
export type CohortToken = Mechanism & { readonly kind: 'cohort' }
export type CohortOwnerToken = Mechanism & { readonly kind: 'owner' }
export type CohortOperationToken = Mechanism & { readonly kind: 'operation' }
export type CohortTransitionToken = Mechanism & { readonly kind: 'transition' }
export type CohortEngineToken = Mechanism & { readonly kind: 'engine' }
type Tokens =
  CohortToken | CohortOwnerToken | CohortOperationToken | CohortTransitionToken | CohortEngineToken
type Result<T extends object = Record<never, never>> =
  | (Mechanism & { readonly ok: true } & T)
  | (Mechanism & { readonly ok: false; readonly reason: Reason })
type Phase = 'candidate' | 'active' | 'draining' | 'released'
type Owner = {
  token: CohortOwnerToken
  cohort: Cohort
  role: CohortHolderRole
  state: 'open' | 'draining' | 'released'
  failed: boolean
  pending: Set<Operation>
  satisfied: Set<CohortOperationKind>
  releaseSucceeded: boolean
  releaseFailed: boolean
}
type Cohort = {
  token: CohortToken
  epoch: number
  projectId: string
  profileEpoch: string
  engine: CohortEngineToken
  phase: Phase
  deadline: number
  owners: Map<CohortHolderRole, Owner>
  failure?: Reason
}
type Transition = { token: CohortTransitionToken; old?: Cohort; candidate: Cohort; live: boolean }
type Operation = {
  token: CohortOperationToken
  owner: Owner
  kind: CohortOperationKind
  state: 'pending' | 'fulfilled' | 'rejected'
  cancelled: boolean
}
const nativeThen = Promise.prototype.then
const required = [
  'main-host',
  'task-service',
  'engine',
  'store',
  'worker',
  'model-service',
] as const
const modelRoles = cohortHolderRoles.filter(
  (r) => !required.some((x) => x === r) && r !== 'health-probe',
)
const id = (v: unknown): v is string => typeof v === 'string' && /^[A-Za-z0-9._:-]{1,128}$/.test(v)

/** Pure bookkeeping only. A captured clock is the sole injected service, never an IO callback. */
export function createProjectCohortLifecycle(clock: () => number = () => performance.now()) {
  const engines = new WeakSet<object>()
  const usedEngines = new WeakSet<object>()
  const cohorts = new WeakMap<object, Cohort>()
  const owners = new WeakMap<object, Owner>()
  const operations = new WeakMap<object, Operation>()
  const transitions = new WeakMap<object, Transition>()
  const tracked = new WeakSet<object>()
  const retained = new Set<Cohort>()
  const pending = new Set<Operation>()
  const waiters = new Set<() => void>()
  const draining = new WeakMap<Cohort, Promise<Result<{ phase: Phase }>>>()
  let active: Cohort | undefined
  let candidate: Cohort | undefined
  let transition: Transition | undefined
  let sequence = 0
  let lastTime = -Infinity
  let closed = false
  let fatal: Reason | undefined
  let entered = false
  let revision = 0
  const ok = <T extends object>(value: T): Result<T> =>
    Object.freeze({ ...boundary, ok: true, ...value })
  const no = (reason: Reason): Result<never> => Object.freeze({ ...boundary, ok: false, reason })
  const lookup = <T>(map: WeakMap<object, T>, value: unknown): T | undefined =>
    typeof value === 'object' && value !== null ? map.get(value) : undefined
  const quiesce = (c: Cohort, reason?: Reason) => {
    if (c.phase === 'released') return
    c.phase = 'draining'
    c.failure ??= reason
    for (const owner of c.owners.values()) if (owner.state === 'open') owner.state = 'draining'
  }
  const bump = () => {
    if (!Number.isSafeInteger(revision + 1)) {
      fatal ??= 'budget'
      for (const c of retained) quiesce(c, 'budget')
      if (transition) transition.live = false
      return
    }
    revision++
  }
  const poison = (reason: Reason) => {
    fatal ??= reason
    bump()
    for (const c of retained) quiesce(c, reason)
    if (transition) transition.live = false
  }
  const now = (): number => {
    // Clock callbacks and Proxy traps may reenter; every mutating public entry is fenced.
    let value: unknown
    try {
      value = clock()
    } catch {
      poison('clock')
      return NaN
    }
    if (
      typeof value !== 'number' ||
      !Number.isFinite(value) ||
      value < 0 ||
      value > Number.MAX_SAFE_INTEGER - cohortLimits.candidateMs ||
      value < lastTime
    ) {
      poison('clock')
      return NaN
    }
    lastTime = value
    return value
  }
  const allocate = <K extends Tokens['kind']>(
    kind: K,
  ): Extract<Tokens, { kind: K }> | undefined => {
    if (sequence >= cohortLimits.issuedTokens || !Number.isSafeInteger(sequence + 1)) {
      poison('budget')
      return undefined
    }
    sequence++
    return Object.freeze({ ...boundary, kind }) as Extract<Tokens, { kind: K }>
  }
  const refreshRelease = (owner: Owner) => {
    if (
      owner.state === 'draining' &&
      owner.releaseSucceeded &&
      !owner.releaseFailed &&
      owner.pending.size === 0
    )
      owner.state = 'released'
  }
  const released = (c: Cohort) => [...c.owners.values()].every((o) => o.state === 'released')
  const collect = () => {
    for (const c of retained) {
      if (c.phase === 'draining' && released(c)) {
        c.phase = 'released'
        if (c !== active && c !== candidate && c !== transition?.old) retained.delete(c)
      }
    }
  }
  const expire = (time: number) => {
    if (candidate?.phase === 'candidate' && time >= candidate.deadline) {
      quiesce(candidate, 'expired')
      if (transition) transition.live = false
      bump()
    }
  }
  function enter<T>(
    action: (time: number) => Result<T & object>,
    cleanup = false,
  ): Result<T & object> {
    if (entered) return no('busy')
    entered = true
    try {
      const time = now()
      expire(time)
      if (!cleanup && (closed || fatal)) return no(fatal ?? 'closed')
      return action(time)
    } catch {
      return no('invalid')
    } finally {
      entered = false
    }
  }
  // Capture only exact own data properties. Never read the caller again after capture.
  const capture = (raw: unknown, keys: string[]): Record<string, unknown> | undefined => {
    if (!raw || typeof raw !== 'object' || Object.getPrototypeOf(raw) !== Object.prototype) return
    const all = Reflect.ownKeys(raw)
    if (all.length !== keys.length || all.some((k) => typeof k !== 'string' || !keys.includes(k)))
      return
    const copy: Record<string, unknown> = Object.create(null)
    for (const key of keys) {
      const d = Object.getOwnPropertyDescriptor(raw, key)
      if (!d || !Object.hasOwn(d, 'value')) return
      copy[key] = d.value
    }
    return copy
  }
  const notify = () => {
    for (const wake of [...waiters]) wake()
  }
  const status = (c: Cohort) =>
    ok({
      phase: c.phase,
      epoch: c.epoch,
      unsettled: [...pending].filter((o) => o.owner.cohort === c).length,
      owners: Object.freeze(
        [...c.owners.values()].map((o) =>
          Object.freeze({
            role: o.role,
            state: o.state,
            failed: o.failed,
            unsettled: o.pending.size,
          }),
        ),
      ),
    })
  const getCurrent = (token: unknown) => {
    const c = lookup(cohorts, token)
    return c && (c === candidate || c === active) ? c : undefined
  }
  const proofRole = (role: CohortHolderRole, kind: CohortOperationKind): boolean => {
    if (kind === 'store-ready') return role === 'store'
    if (kind === 'job-ready') return role === 'worker'
    if (kind === 'scope-ready') return role === 'task-service'
    if (kind === 'model-enabled' || kind === 'model-disabled') return role === 'model-service'
    if (kind === 'child') return role === 'engine' || role === 'health-probe'
    if (kind === 'store-connection') return role === 'store'
    if (kind === 'picker') return role === 'main-host'
    if (kind === 'acquire') return role === 'main-host' || role === 'engine'
    return true
  }
  function track(
    ownerValue: unknown,
    kindValue: unknown,
    promise: unknown,
  ): Result<{ operation: CohortOperationToken }> {
    return enter(() => {
      const owner = lookup(owners, ownerValue)
      if (
        !owner ||
        typeof kindValue !== 'string' ||
        !(kinds as readonly string[]).includes(kindValue)
      )
        return no('invalid')
      const kind = kindValue as CohortOperationKind
      const c = owner.cohort
      if (!proofRole(owner.role, kind)) return no('invalid')
      if (owner.state !== 'open' && !(kind === 'release' && owner.state === 'draining'))
        return no('stale')
      if (c !== active && c !== candidate && kind !== 'release') return no('stale')
      if (c.phase === 'draining' && kind !== 'release') return no('stale')
      // Native brand first rejects Proxy/thenable without reading their properties.
      // Strict native prototype/own-key rules reject overridden then/species/constructor.
      if (
        !types.isPromise(promise) ||
        Object.getPrototypeOf(promise) !== Promise.prototype ||
        Reflect.ownKeys(promise).length !== 0
      )
        return no('invalid')
      if (tracked.has(promise)) return no('invalid')
      if (pending.size >= cohortLimits.operations || owner.pending.size >= cohortLimits.perOwner)
        return no('budget')
      if (
        (kind === 'picker' || kind === 'acquire') &&
        [...pending].filter((p) => p.kind === kind).length >= cohortLimits[kind]
      )
        return no('busy')
      if (
        kind === 'release' &&
        (owner.releaseSucceeded || [...owner.pending].some((p) => p.kind === 'release'))
      )
        return no('stale')
      const token = allocate('operation')
      if (!token) return no('budget')
      const operation: Operation = { token, owner, kind, state: 'pending', cancelled: false }
      operations.set(token, operation)
      owner.pending.add(operation)
      pending.add(operation)
      tracked.add(promise)
      if (kind === 'release') owner.state = 'draining'
      const settle = (success: boolean) => {
        if (operation.state !== 'pending') return
        operation.state = success ? 'fulfilled' : 'rejected'
        owner.pending.delete(operation)
        pending.delete(operation)
        if (!success) owner.failed = true
        // Only permanent whole-cohort engine/Store ownership termination belongs
        // here. A restartable same-Supervisor session ending is not this lifetime:
        // short-session work only counts as pending resource work, while T01 owns
        // actual session recovery/readiness. A does not authenticate session-ready.
        // Ordinary noteViewRecovery never quiesces a cohort or clears any grant.
        // During an already ordered drain, normal close still counts toward release.
        if (
          (kind === 'child' || kind === 'store-connection') &&
          (c.phase === 'candidate' || c.phase === 'active')
        ) {
          quiesce(c, success ? 'closed' : 'failed')
          if (transition?.candidate === c) transition.live = false
          bump()
        }
        // Old or cancelled completions never install initialization/binding/ready proof.
        if (success && !operation.cancelled && owner.state === 'open' && c.phase === 'candidate')
          owner.satisfied.add(kind)
        if (kind === 'release') {
          owner.releaseSucceeded = success
          owner.releaseFailed = !success
        }
        refreshRelease(owner)
        collect()
        notify()
      }
      try {
        nativeThen.call(
          promise,
          () => settle(true),
          () => settle(false),
        )
      } catch {
        // If subscription is uncertain, retain the slot; never pretend it settled.
        operation.cancelled = true
        owner.failed = true
        quiesce(c, 'failed')
        return no('failed')
      }
      return ok({ operation: token })
    }, kindValue === 'release')
  }
  const api = {
    createEngineIdentity: () =>
      enter(() => {
        const engine = allocate('engine')
        if (!engine) return no('budget')
        engines.add(engine)
        return ok({ engine })
      }),
    prepareTransition: (raw: unknown) =>
      enter((time) => {
        if (transition || candidate) return no('busy')
        collect()
        if (retained.size >= cohortLimits.retainedCohorts) return no('budget')
        const priorRevision = revision,
          priorActive = active
        const v = capture(raw, ['projectId', 'profileEpoch', 'engine', 'reason'])
        if (
          !v ||
          !id(v.projectId) ||
          !id(v.profileEpoch) ||
          typeof v.engine !== 'object' ||
          v.engine === null ||
          !engines.has(v.engine) ||
          usedEngines.has(v.engine) ||
          typeof v.reason !== 'string' ||
          !['open', 'reopen', 'migrate', 'replace-engine'].includes(v.reason)
        )
          return no('invalid')
        if (active?.engine === v.engine) return no('invalid')
        const capturedAt = now()
        if (fatal) return no(fatal)
        if (priorRevision !== revision || priorActive !== active || transition || candidate)
          return no('stale')
        if (capturedAt >= time + cohortLimits.candidateMs) return no('expired')
        const token = allocate('cohort'),
          transitionToken = allocate('transition')
        if (!token || !transitionToken) return no('budget')
        const c: Cohort = {
          token,
          epoch: sequence,
          projectId: v.projectId,
          profileEpoch: v.profileEpoch,
          engine: v.engine as CohortEngineToken,
          phase: 'candidate',
          deadline: time + cohortLimits.candidateMs,
          owners: new Map(),
        }
        if (!Number.isFinite(c.deadline) || c.deadline <= time) {
          poison('clock')
          return no('clock')
        }
        const t: Transition = { token: transitionToken, old: active, candidate: c, live: true }
        usedEngines.add(c.engine)
        if (active) quiesce(active)
        cohorts.set(token, c)
        transitions.set(transitionToken, t)
        retained.add(c)
        candidate = c
        transition = t
        bump()
        return ok({ candidate: token, transition: transitionToken })
      }),
    registerOwner: (cohortValue: unknown, roleValue: unknown) =>
      enter(() => {
        const c = getCurrent(cohortValue)
        if (!c || c !== candidate || c.phase !== 'candidate') return no('stale')
        if (
          typeof roleValue !== 'string' ||
          !(cohortHolderRoles as readonly string[]).includes(roleValue)
        )
          return no('invalid')
        const role = roleValue as CohortHolderRole
        if (c.owners.has(role)) return no('invalid')
        const token = allocate('owner')
        if (!token) return no('budget')
        const owner: Owner = {
          token,
          cohort: c,
          role,
          state: 'open',
          failed: false,
          pending: new Set(),
          satisfied: new Set(),
          releaseSucceeded: false,
          releaseFailed: false,
        }
        owners.set(token, owner)
        c.owners.set(role, owner)
        return ok({ owner: token })
      }),
    track,
    cancelOperation: (ownerValue: unknown, operationValue: unknown) =>
      enter(() => {
        const owner = lookup(owners, ownerValue),
          op = lookup(operations, operationValue)
        if (!owner || !op || op.owner !== owner) return no('invalid')
        if (op.state !== 'pending' || op.cancelled) return no('stale')
        op.cancelled = true
        return ok({ unsettled: true })
      }),
    quiesce: (cohortValue: unknown) =>
      enter(() => {
        const c = lookup(cohorts, cohortValue)
        if (!c || !retained.has(c)) return no('stale')
        quiesce(c)
        if (c === candidate && transition) transition.live = false
        bump()
        return status(c)
      }),
    releaseOwner: (ownerValue: unknown, completion: unknown) =>
      track(ownerValue, 'release', completion),
    waitForDrain: (cohortValue: unknown): Promise<Result<{ phase: Phase }>> => {
      const start = enter((time) => {
        const c = lookup(cohorts, cohortValue)
        if (
          !c ||
          (!retained.has(c) && c.phase !== 'released') ||
          c.phase === 'candidate' ||
          c.phase === 'active'
        )
          return no('stale')
        return ok({ cohort: c, deadline: time + cohortLimits.waitMs })
      }, true)
      if (!start.ok) return Promise.resolve(start)
      const c = start.cohort
      const existing = draining.get(c)
      if (existing) return existing
      const waiting = new Promise<Result<{ phase: Phase }>>((resolve) => {
        let done = false
        const finish = (result: Result<{ phase: Phase }>) => {
          if (done) return
          done = true
          clearTimeout(timer)
          waiters.delete(wake)
          resolve(result)
        }
        const wake = () => {
          const result = enter((time) => {
            collect()
            if (c.phase === 'released') return ok({ phase: c.phase })
            if (fatal || closed) return no(fatal ?? 'closed')
            if (time >= start.deadline) return no('unsettled')
            return ok({ phase: c.phase })
          }, true)
          if (!result.ok || result.phase === 'released') finish(result)
        }
        waiters.add(wake)
        const timer = setTimeout(() => {
          wake()
          // A clock that has not advanced cannot turn a timer into a release proof.
          if (!done) finish(no('unsettled'))
        }, cohortLimits.waitMs)
        wake()
      })
      draining.set(c, waiting)
      void waiting.then(() => draining.delete(c))
      return waiting
    },
    abortCandidate: (transitionValue: unknown) =>
      enter(() => {
        const t = lookup(transitions, transitionValue)
        if (!t || t !== transition) return no('stale')
        quiesce(t.candidate)
        t.live = false
        // Retain unfinished owners and global slots even after abandoning this candidate.
        candidate = undefined
        transition = undefined
        collect()
        bump()
        return status(t.candidate)
      }),
    publish: (transitionValue: unknown) =>
      enter(() => {
        const t = lookup(transitions, transitionValue)
        if (!t || t !== transition || !t.live || candidate !== t.candidate) return no('stale')
        const c = t.candidate
        if (c.phase !== 'candidate') return no(c.failure ?? 'stale')
        if (t.old && !released(t.old)) return no('unsettled')
        if (!required.every((role) => c.owners.has(role))) return no('incomplete')
        const model = c.owners.get('model-service')!
        const enabled = model.satisfied.has('model-enabled'),
          disabled = model.satisfied.has('model-disabled')
        if (enabled === disabled) return no('incomplete')
        if (enabled && !modelRoles.every((role) => c.owners.has(role))) return no('incomplete')
        for (const owner of c.owners.values()) {
          if (disabled && modelRoles.includes(owner.role)) {
            if (owner.state !== 'released') return no('incomplete')
            continue
          }
          if (
            owner.state !== 'open' ||
            owner.failed ||
            [...owner.pending].some(
              (op) => op.cancelled || (op.kind !== 'child' && op.kind !== 'store-connection'),
            ) ||
            !owner.satisfied.has('initialize') ||
            !owner.satisfied.has('binding')
          )
            return no('incomplete')
        }
        if (
          !c.owners.get('store')!.satisfied.has('store-ready') ||
          !c.owners.get('worker')!.satisfied.has('job-ready') ||
          !c.owners.get('task-service')!.satisfied.has('scope-ready')
        )
          return no('incomplete')
        const beforePublish = revision
        const publishedAt = now()
        if (fatal) return no(fatal)
        expire(publishedAt)
        if (
          revision !== beforePublish ||
          t !== transition ||
          !t.live ||
          candidate !== c ||
          c.phase !== 'candidate'
        )
          return no(c.failure ?? 'stale')
        if (t.old) {
          t.old.phase = 'released'
          retained.delete(t.old)
        }
        c.phase = 'active'
        active = c
        candidate = undefined
        transition = undefined
        t.live = false
        bump()
        return ok({
          cohort: c.token,
          epoch: c.epoch,
          model: disabled ? ('disabled' as const) : ('enabled' as const),
        })
      }),
    noteViewRecovery: (cohortValue: unknown, engineValue: unknown, kind: unknown) =>
      enter(() => {
        const c = lookup(cohorts, cohortValue)
        if (
          c !== active ||
          c?.phase !== 'active' ||
          engineValue !== c.engine ||
          (kind !== 'refresh' && kind !== 'same-engine-disconnect')
        )
          return no('stale')
        return ok({ cohort: c.token, epoch: c.epoch, revision })
      }),
    inspect: (cohortValue: unknown) =>
      enter(() => {
        const c = lookup(cohorts, cohortValue)
        return c ? status(c) : no('invalid')
      }, true),
    snapshot: () =>
      enter(
        () =>
          ok({
            closed,
            failure: fatal ?? null,
            revision,
            active: active?.token ?? null,
            candidate: candidate?.token ?? null,
            transition: transition?.token ?? null,
            unsettled: pending.size,
            picker: [...pending].filter((o) => o.kind === 'picker').length,
            acquire: [...pending].filter((o) => o.kind === 'acquire').length,
            retained: retained.size,
          }),
        true,
      ),
    close: () =>
      enter(() => {
        closed = true
        for (const c of retained) quiesce(c)
        if (transition) transition.live = false
        bump()
        queueMicrotask(notify)
        return ok({ unsettled: pending.size })
      }, true),
    contentIo: () => no('unsupported'),
  }
  return Object.freeze(api)
}
