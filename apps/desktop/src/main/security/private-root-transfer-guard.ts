import { z } from 'zod'

/** Metadata only. No API in this module grants or performs content I/O. */
export const TRANSFER_GUARD_LIMITS = Object.freeze({
  roots: 8,
  identities: 256,
  locations: 64,
  segments: 32,
  suffix: 16,
  string: 128,
  nodes: 8192,
  depth: 12,
  keys: 24,
  array: 512,
  tokens: 16,
  observations: 2,
  observationMs: 5000,
  tokenMs: 30000,
})

type Reason =
  | 'invalid'
  | 'unsupported'
  | 'incomplete'
  | 'stale'
  | 'conflict'
  | 'budget'
  | 'cancelled'
  | 'expired'
  | 'released'
  | 'closed'
export type MetadataRejection = Readonly<{ status: 'rejected'; reason: Reason }>
export type RequestToken = Readonly<{ kind: 'transfer-metadata-request' }>
export type MetadataToken = Readonly<{ kind: 'transfer-metadata-candidate' }>
export type MetadataCandidate = Readonly<{
  status: 'metadata-eligible'
  token: MetadataToken
  contentIo: 'unsupported'
}>

const id = z.string().regex(/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/)
const natural = z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER)
const segment = z
  .string()
  .min(1)
  .max(128)
  .refine(
    (value) =>
      value !== '.' &&
      value !== '..' &&
      [...value].every((char) => {
        const code = char.charCodeAt(0)
        return code >= 32 && code <= 126 && !'/\\:'.includes(char)
      }),
  )
const path = z.array(segment).max(32)
const none = z.object({ kind: z.literal('none') }).strict()
const file = z.object({ kind: z.literal('file'), ref: id }).strict()
const refs = z.array(id).min(1).max(64)
const contextSchema = z
  .object({
    profileEpoch: id,
    projectId: id,
    checkpointId: id,
    requestId: id,
    generation: natural,
    purpose: z.enum(['export', 'import']),
  })
  .strict()
const descriptorSchema = z
  .object({
    version: z.literal(1),
    sourceRead: z.union([none, z.object({ kind: z.literal('files'), refs }).strict()]),
    inputPackage: z.union([none, file]),
    final: z.union([none, file]),
    staging: z.union([none, z.object({ kind: z.literal('members'), refs }).strict()]),
    unpack: z.union([none, z.object({ kind: z.literal('members'), refs }).strict()]),
    newProject: z.union([none, z.object({ kind: z.literal('writer-location'), ref: id }).strict()]),
    backup: none,
  })
  .strict()
const identitySchema = z
  .object({
    kind: z.literal('posix-devino'),
    volume: id,
    device: z.string().regex(/^(0|[1-9][0-9]{0,19})$/),
    inode: z.string().regex(/^(0|[1-9][0-9]{0,19})$/),
    lifecycle: id,
    state: z.enum(['active', 'retired', 'unknown']),
    objectType: z.enum(['file', 'directory', 'unknown']),
  })
  .strict()
const snapshotSchema = z
  .object({
    version: z.literal(1),
    profileEpoch: id,
    revision: natural,
    completeness: z.enum(['complete', 'incomplete', 'unknown', 'recovering', 'failed']),
    platform: z.object({ kind: z.literal('posix-sensitive'), namespace: id, volume: id }).strict(),
    protectedRoots: z
      .array(
        z
          .object({
            role: z.enum(['private-root', 'database', 'database-wal', 'database-shm', 'task-root']),
            segments: path,
            identity: identitySchema.nullable(),
          })
          .strict(),
      )
      .max(8),
    protectedIdentities: z.array(identitySchema).max(256),
    locations: z
      .array(
        z
          .object({
            ref: id,
            anchor: z.object({ segments: path, identity: identitySchema }).strict(),
            suffix: z.array(segment).min(1).max(16),
            identity: identitySchema.nullable(),
          })
          .strict(),
      )
      .max(64),
  })
  .strict()
type Context = z.infer<typeof contextSchema>
type Descriptor = z.infer<typeof descriptorSchema>
type Snapshot = z.infer<typeof snapshotSchema>
type Identity = z.infer<typeof identitySchema>
export interface MetadataObservationPort {
  observe(
    request: Readonly<{ context: Readonly<Context>; descriptor: Readonly<Descriptor> }>,
    signal: AbortSignal,
  ): Promise<unknown>
}

const internalFailures = new WeakMap<object, Reason>()
class InvalidMetadata extends Error {
  constructor(reason: Reason) {
    super(reason)
    internalFailures.set(this, reason)
  }
}
const reject = (reason: Reason): MetadataRejection => Object.freeze({ status: 'rejected', reason })
const eligible = (token: MetadataToken): MetadataCandidate =>
  Object.freeze({ status: 'metadata-eligible', token, contentIo: 'unsupported' })

/** Capture data descriptors once; never pass caller objects to Zod. */
function capture(raw: unknown): unknown {
  let count = 0
  const ancestors = new Set<object>()
  function copy(value: unknown, depth: number): unknown {
    if (++count > TRANSFER_GUARD_LIMITS.nodes || depth > TRANSFER_GUARD_LIMITS.depth)
      throw new InvalidMetadata('budget')
    if (value === null || typeof value === 'boolean') return value
    if (typeof value === 'string') {
      if (value.length > TRANSFER_GUARD_LIMITS.string) throw new InvalidMetadata('budget')
      return value
    }
    if (typeof value === 'number' && Number.isSafeInteger(value)) return value
    if (typeof value !== 'object' || ancestors.has(value)) throw new InvalidMetadata('invalid')
    const array = Array.isArray(value)
    const proto = Object.getPrototypeOf(value)
    if (proto !== (array ? Array.prototype : Object.prototype) && !(proto === null && !array))
      throw new InvalidMetadata('invalid')
    let length = 0
    if (array) {
      const field = Object.getOwnPropertyDescriptor(value, 'length')
      if (!field || !('value' in field) || !Number.isSafeInteger(field.value))
        throw new InvalidMetadata('invalid')
      length = field.value as number
      if (length > TRANSFER_GUARD_LIMITS.array) throw new InvalidMetadata('budget')
    }
    const keys = Reflect.ownKeys(value)
    if (keys.length > (array ? length + 1 : TRANSFER_GUARD_LIMITS.keys))
      throw new InvalidMetadata('budget')
    if (array && keys.length !== length + 1) throw new InvalidMetadata('invalid')
    ancestors.add(value)
    const result: unknown[] | Record<string, unknown> = array ? [] : Object.create(null)
    for (const key of keys) {
      if (array && key === 'length') continue
      if (
        typeof key !== 'string' ||
        key.length > TRANSFER_GUARD_LIMITS.string ||
        ['__proto__', 'constructor', 'prototype'].includes(key) ||
        (array && (!/^(0|[1-9][0-9]*)$/.test(key) || Number(key) >= length))
      )
        throw new InvalidMetadata('invalid')
      const field = Object.getOwnPropertyDescriptor(value, key)
      if (!field || !('value' in field) || !field.enumerable) throw new InvalidMetadata('invalid')
      const copied = copy(field.value, depth + 1)
      if (array) (result as unknown[])[Number(key)] = copied
      else (result as Record<string, unknown>)[key] = copied
    }
    ancestors.delete(value)
    return result
  }
  return copy(raw, 0)
}
function freeze<T>(value: T): T {
  if (value && typeof value === 'object') {
    for (const child of Object.values(value)) freeze(child)
    Object.freeze(value)
  }
  return value
}
function parse<T>(schema: z.ZodType<T>, raw: unknown): T {
  const result = schema.safeParse(capture(raw))
  if (!result.success) throw new InvalidMetadata('invalid')
  return freeze(result.data)
}
function failure(error: unknown): MetadataRejection {
  const known =
    error !== null && (typeof error === 'object' || typeof error === 'function')
      ? internalFailures.get(error)
      : undefined
  return reject(known ?? 'invalid')
}
function descriptorRefs(descriptor: Descriptor, context: Context): string[] {
  const { sourceRead, inputPackage, final, staging, unpack, newProject } = descriptor
  if (
    (context.purpose === 'export' &&
      (final.kind !== 'file' ||
        inputPackage.kind !== 'none' ||
        unpack.kind !== 'none' ||
        newProject.kind !== 'none')) ||
    (context.purpose === 'import' &&
      (inputPackage.kind !== 'file' ||
        newProject.kind !== 'writer-location' ||
        sourceRead.kind !== 'none' ||
        final.kind !== 'none' ||
        staging.kind !== 'none'))
  )
    throw new InvalidMetadata('invalid')
  const collected: string[] = []
  for (const role of [sourceRead, inputPackage, final, staging, unpack, newProject]) {
    if ('refs' in role) collected.push(...role.refs)
    else if ('ref' in role) collected.push(role.ref)
  }
  if (collected.length > TRANSFER_GUARD_LIMITS.locations) throw new InvalidMetadata('budget')
  if (new Set(collected).size !== collected.length) throw new InvalidMetadata('invalid')
  return collected
}
function sameIdentity(a: Identity, b: Identity): boolean {
  return a.volume === b.volume && a.device === b.device && a.inode === b.inode
}
const contains = (parent: string[], child: string[]) =>
  parent.length <= child.length && parent.every((part, index) => part === child[index])
function protectionView(snapshot: Snapshot): string {
  const {
    version,
    profileEpoch,
    revision,
    completeness,
    platform,
    protectedRoots,
    protectedIdentities,
  } = snapshot
  return JSON.stringify({
    version,
    profileEpoch,
    revision,
    completeness,
    platform,
    protectedRoots,
    protectedIdentities,
  })
}
function locationView(snapshot: Snapshot): string {
  return JSON.stringify(
    [...snapshot.locations].sort((a, b) => (a.ref < b.ref ? -1 : a.ref > b.ref ? 1 : 0)),
  )
}
function inspect(snapshot: Snapshot, descriptor: Descriptor, context: Context): void {
  if (snapshot.completeness !== 'complete') throw new InvalidMetadata('incomplete')
  if (snapshot.profileEpoch !== context.profileEpoch) throw new InvalidMetadata('stale')
  for (const role of ['private-root', 'database', 'database-wal', 'database-shm']) {
    if (snapshot.protectedRoots.filter((root) => root.role === role).length !== 1)
      throw new InvalidMetadata('incomplete')
  }
  const protectedIds = [...snapshot.protectedIdentities]
  for (const root of snapshot.protectedRoots) {
    if (root.identity) {
      const expected = ['private-root', 'task-root'].includes(root.role) ? 'directory' : 'file'
      if (root.identity.objectType !== expected) throw new InvalidMetadata('incomplete')
      protectedIds.push(root.identity)
    }
  }
  for (const identity of protectedIds) {
    if (identity.state === 'unknown' || identity.objectType === 'unknown')
      throw new InvalidMetadata('incomplete')
    if (identity.volume !== snapshot.platform.volume) throw new InvalidMetadata('unsupported')
  }
  const expected = descriptorRefs(descriptor, context)
  const locations = snapshot.locations
  if (
    locations.length !== expected.length ||
    new Set(locations.map((location) => location.ref)).size !== locations.length ||
    locations.some((location) => !expected.includes(location.ref))
  )
    throw new InvalidMetadata('invalid')
  const paths: string[][] = []
  const candidateIds: Identity[] = []
  for (const location of locations) {
    const { anchor, suffix, identity, ref } = location
    const candidate = [...anchor.segments, ...suffix]
    if (candidate.length > TRANSFER_GUARD_LIMITS.segments) throw new InvalidMetadata('budget')
    if (anchor.identity.state !== 'active' || anchor.identity.objectType !== 'directory')
      throw new InvalidMetadata('unsupported')
    for (const value of [anchor.identity, ...(identity ? [identity] : [])]) {
      if (value.volume !== snapshot.platform.volume) throw new InvalidMetadata('unsupported')
      if (protectedIds.some((protectedId) => sameIdentity(value, protectedId)))
        throw new InvalidMetadata('conflict')
    }
    if (identity && (identity.state !== 'active' || identity.objectType !== 'file'))
      throw new InvalidMetadata('unsupported')
    const read =
      (descriptor.sourceRead.kind === 'files' && descriptor.sourceRead.refs.includes(ref)) ||
      (descriptor.inputPackage.kind === 'file' && descriptor.inputPackage.ref === ref)
    const prospective =
      (descriptor.final.kind === 'file' && descriptor.final.ref === ref) ||
      (descriptor.newProject.kind === 'writer-location' && descriptor.newProject.ref === ref)
    if ((read && !identity) || (prospective && identity)) throw new InvalidMetadata('invalid')
    if (
      snapshot.protectedRoots.some(
        (root) => contains(root.segments, candidate) || contains(candidate, root.segments),
      ) ||
      paths.some((other) => contains(other, candidate) || contains(candidate, other)) ||
      (identity && candidateIds.some((other) => sameIdentity(other, identity)))
    )
      throw new InvalidMetadata('conflict')
    paths.push(candidate)
    if (identity) candidateIds.push(identity)
  }
}

type Request = { token: RequestToken; context: Context }
type Entry = {
  request: Request
  token: MetadataToken
  binding?: { descriptor: Descriptor; protection: string; locations: string }
  revision: number
  deadline: number
  state: 'candidate' | 'invalidated' | 'released' | 'expired'
}
type Observation = { request: Request; cancel(): void }
type Observed = { raw: unknown; deadline: number } | MetadataRejection

export function createPrivateRootTransferGuard(owner?: MetadataObservationPort) {
  const requests = new WeakMap<object, Request>()
  const tokens = new WeakMap<object, Entry>()
  const active = new Set<Entry>()
  const pending = new Set<Observation>()
  let current: Request | undefined
  let profileEpoch: string | undefined
  let revision: number | undefined
  let protection: string | undefined
  let closed = false
  let poisoned: Reason | undefined
  let sequence = 0
  let reservations = 0
  let lastNow = -Infinity
  // The port identity is a factory trust assumption, never an OS provenance proof.
  let observe: MetadataObservationPort['observe'] | undefined
  try {
    const method = owner?.observe
    if (owner && typeof method === 'function') observe = method.bind(owner)
  } catch {
    observe = undefined
  }
  function retireEntry(entry: Entry, state: Entry['state']) {
    entry.state = state
    entry.binding = undefined
    active.delete(entry)
  }
  function invalidateEntries(request?: Request) {
    for (const entry of active) {
      if (!request || entry.request === request) {
        retireEntry(entry, 'invalidated')
      }
    }
  }
  function invalidateCurrent() {
    sequence++
    const previous = current
    current = undefined
    const operations = [...pending].filter((operation) => operation.request === previous)
    if (previous) invalidateEntries(previous)
    // Snapshot the old operations before synchronous abort listeners can reenter.
    for (const operation of operations) operation.cancel()
  }
  function now(): number {
    let value: number
    try {
      value = performance.now()
    } catch {
      value = NaN
    }
    if (!Number.isFinite(value) || value < lastNow) {
      poisoned = 'stale'
      invalidateCurrent()
      throw new InvalidMetadata('stale')
    }
    lastNow = value
    for (const entry of active) {
      if (value >= entry.deadline) {
        retireEntry(entry, 'expired')
      }
    }
    return value
  }
  function requestOf(token: unknown): Request {
    if (closed) throw new InvalidMetadata('closed')
    if (poisoned) throw new InvalidMetadata(poisoned)
    const request = token && typeof token === 'object' ? requests.get(token) : undefined
    if (!request) throw new InvalidMetadata('invalid')
    if (request !== current) throw new InvalidMetadata('stale')
    return request
  }
  function entryOf(request: Request, token: unknown): Entry {
    const entry = token && typeof token === 'object' ? tokens.get(token) : undefined
    if (!entry || entry.request !== request) throw new InvalidMetadata('invalid')
    if (entry.state !== 'candidate') {
      const reason = entry.state === 'invalidated' ? 'stale' : entry.state
      throw new InvalidMetadata(reason)
    }
    if (entry.revision !== revision) throw new InvalidMetadata('stale')
    return entry
  }
  function observeOnce(request: Request, descriptor: Descriptor): Promise<Observed> {
    if (!observe) return Promise.resolve(reject('unsupported'))
    if (pending.size >= TRANSFER_GUARD_LIMITS.observations) return Promise.resolve(reject('budget'))
    const call = observe
    const deadline = now() + TRANSFER_GUARD_LIMITS.observationMs
    return new Promise((resolve) => {
      const controller = new AbortController()
      let done = false
      const finish = (result: Observed) => {
        if (done) return
        done = true
        clearTimeout(timer)
        resolve(result)
      }
      const operation: Observation = {
        request,
        cancel() {
          finish(reject('cancelled'))
          controller.abort()
        },
      }
      const timer = setTimeout(() => {
        finish(reject('expired'))
        controller.abort()
      }, TRANSFER_GUARD_LIMITS.observationMs)
      pending.add(operation)
      Promise.resolve()
        .then(() => {
          if (done || current !== request || closed || poisoned) return undefined
          return call(freeze({ context: request.context, descriptor }), controller.signal)
        })
        .then(
          (raw) => {
            pending.delete(operation)
            if (done) return
            try {
              if (now() >= deadline) {
                finish(reject('expired'))
                controller.abort()
              } else finish({ raw, deadline })
            } catch (error) {
              finish(failure(error))
              controller.abort()
            }
          },
          () => {
            pending.delete(operation)
            finish(reject('unsupported'))
          },
        )
    })
  }
  function acceptObservation(raw: unknown, request: Request): Snapshot {
    const inert = capture(raw)
    requestOf(request.token)
    if (
      inert &&
      typeof inert === 'object' &&
      'platform' in inert &&
      inert.platform &&
      typeof inert.platform === 'object' &&
      'kind' in inert.platform &&
      inert.platform.kind !== 'posix-sensitive'
    )
      throw new InvalidMetadata('unsupported')
    if (inert && typeof inert === 'object') {
      for (const [key, limit] of [
        ['protectedRoots', 8],
        ['protectedIdentities', 256],
        ['locations', 64],
      ] as const) {
        const values = (inert as Record<string, unknown>)[key]
        if (Array.isArray(values) && values.length > limit) throw new InvalidMetadata('budget')
      }
    }
    const parsed = snapshotSchema.safeParse(inert)
    if (!parsed.success) throw new InvalidMetadata('invalid')
    const snapshot = freeze(parsed.data)
    requestOf(request.token)
    if (snapshot.profileEpoch !== request.context.profileEpoch) throw new InvalidMetadata('stale')
    const view = protectionView(snapshot)
    if (revision !== undefined && snapshot.revision < revision) throw new InvalidMetadata('stale')
    if (snapshot.revision === revision && view !== protection) {
      poisoned = 'conflict'
      invalidateEntries()
      throw new InvalidMetadata('conflict')
    }
    if (snapshot.revision !== revision) invalidateEntries()
    revision = snapshot.revision
    protection = view
    return snapshot
  }
  function check(requestToken: unknown, token: unknown): MetadataCandidate | MetadataRejection {
    try {
      now()
      const request = requestOf(requestToken)
      return eligible(entryOf(request, token).token)
    } catch (error) {
      return failure(error)
    }
  }
  return Object.freeze({
    openRequest(
      rawContext: unknown,
    ): Readonly<{ status: 'request-opened'; token: RequestToken }> | MetadataRejection {
      if (closed) return reject('closed')
      const opening = sequence + 1
      invalidateCurrent()
      if (opening !== sequence) return reject('cancelled')
      try {
        now()
        if (poisoned) return reject(poisoned)
        const context = parse(contextSchema, rawContext)
        if (opening !== sequence) return reject('cancelled')
        if (profileEpoch !== undefined && profileEpoch !== context.profileEpoch)
          return reject('stale')
        profileEpoch = context.profileEpoch
        const token: RequestToken = Object.freeze({ kind: 'transfer-metadata-request' })
        current = { token, context }
        requests.set(token, current)
        return Object.freeze({ status: 'request-opened', token })
      } catch (error) {
        return failure(error)
      }
    },
    async evaluate(
      requestToken: unknown,
      rawDescriptor: unknown,
    ): Promise<MetadataCandidate | MetadataRejection> {
      let reserved = false
      try {
        const started = now()
        const request = requestOf(requestToken)
        const descriptor = parse(descriptorSchema, rawDescriptor)
        descriptorRefs(descriptor, request.context)
        requestOf(requestToken)
        if (active.size + reservations >= TRANSFER_GUARD_LIMITS.tokens) return reject('budget')
        reservations++
        reserved = true
        const observed = await observeOnce(request, descriptor)
        now()
        requestOf(requestToken)
        if ('status' in observed) return observed
        const snapshot = acceptObservation(observed.raw, request)
        inspect(snapshot, descriptor, request.context)
        const completed = now()
        requestOf(requestToken)
        if (completed >= observed.deadline || completed >= started + TRANSFER_GUARD_LIMITS.tokenMs)
          return reject('expired')
        const token: MetadataToken = Object.freeze({ kind: 'transfer-metadata-candidate' })
        const entry: Entry = {
          request,
          token,
          binding: {
            descriptor,
            protection: protectionView(snapshot),
            locations: locationView(snapshot),
          },
          revision: snapshot.revision,
          deadline: started + TRANSFER_GUARD_LIMITS.tokenMs,
          state: 'candidate',
        }
        active.add(entry)
        tokens.set(token, entry)
        return eligible(token)
      } catch (error) {
        return failure(error)
      } finally {
        if (reserved) reservations--
      }
    },
    check,
    async revalidate(
      requestToken: unknown,
      token: unknown,
    ): Promise<MetadataCandidate | MetadataRejection> {
      let entry: Entry | undefined
      try {
        now()
        const request = requestOf(requestToken)
        entry = entryOf(request, token)
        const binding = entry.binding
        if (!binding) throw new InvalidMetadata('stale')
        const observed = await observeOnce(request, binding.descriptor)
        now()
        requestOf(requestToken)
        entryOf(request, token)
        if ('status' in observed) throw new InvalidMetadata(observed.reason)
        const snapshot = acceptObservation(observed.raw, request)
        inspect(snapshot, binding.descriptor, request.context)
        const completed = now()
        requestOf(requestToken)
        entryOf(request, token)
        if (completed >= observed.deadline) throw new InvalidMetadata('expired')
        if (
          protectionView(snapshot) !== binding.protection ||
          locationView(snapshot) !== binding.locations
        )
          throw new InvalidMetadata('stale')
        return eligible(entry.token)
      } catch (error) {
        if (entry && entry.state === 'candidate') {
          retireEntry(entry, 'invalidated')
        }
        return failure(error)
      }
    },
    release(
      requestToken: unknown,
      token: unknown,
    ): MetadataRejection | Readonly<{ status: 'released' }> {
      try {
        now()
        const entry = entryOf(requestOf(requestToken), token)
        retireEntry(entry, 'released')
        return Object.freeze({ status: 'released' })
      } catch (error) {
        return failure(error)
      }
    },
    invalidate: invalidateCurrent,
    close() {
      closed = true
      invalidateCurrent()
    },
    contentIo(): MetadataRejection {
      return reject('unsupported')
    },
  })
}
