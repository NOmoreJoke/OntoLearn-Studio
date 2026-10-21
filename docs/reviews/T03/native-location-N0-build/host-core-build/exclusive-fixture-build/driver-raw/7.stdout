import { z } from 'zod'

/** Main-private, fixture-only projection. Native fixture-host assembly supplies the
 * method table; schema/WeakMap checks do not certify that arbitrary JS is native.
 * This file never loads an addon or constructs an owner from a path/fd/PID.
 * Returned views always have productionAdmission:'unsupported'. */
export type NativeLocationStatus =
  | 'ok'
  | 'invalid'
  | 'stale'
  | 'denied'
  | 'unsupported'
  | 'budget'
  | 'busy'
  | 'retained'
  | 'internal'

const statuses = [
  'ok',
  'invalid',
  'stale',
  'denied',
  'unsupported',
  'budget',
  'busy',
  'retained',
  'internal',
] as const
const codeSchema = z.number().int().min(0).max(8)
const metadataSchema = z
  .object({
    kind: z.union([z.literal(1), z.literal(2)]),
    volume: z.string().regex(/^[0-9a-f]{16}$/),
    file: z.string().regex(/^[0-9a-f]{32}$/),
    links: z.string().regex(/^[1-9][0-9]{0,19}$/),
    aclChecked: z.literal(1),
    heldObjectOnly: z.literal(1),
    productionAdmission: z.literal(0),
  })
  .strict()
  .refine((value) => {
    if (typeof value.links !== 'string' || !/^[1-9][0-9]{0,19}$/.test(value.links)) return false
    try {
      return (
        BigInt(value.links) <= 18446744073709551615n && (value.kind !== 2 || value.links === '1')
      )
    } catch {
      return false
    }
  })
const snapshotSchema = z
  .object({
    status: z.literal(0),
    abiVersion: z.literal(1),
    epoch: z.union([z.literal(1), z.literal(2)]),
    accepting: z.union([z.literal(0), z.literal(1)]),
    closed: z.union([z.literal(0), z.literal(1)]),
    heldObjects: z.number().int().min(0).max(128),
    unknownObjects: z.number().int().min(0).max(132),
    pendingChildren: z.number().int().min(0).max(2),
    heldPipes: z.number().int().min(0).max(4),
    inflight: z.number().int().min(0).max(2),
    everCaps: z.number().int().min(1).max(128),
    nameBytes: z.number().int().min(0).max(16384),
    productionAdmission: z.literal(0),
  })
  .strict()
  .refine(
    (value) =>
      value.closed === 0 ||
      (value.accepting === 0 &&
        value.epoch === 2 &&
        value.heldObjects === 0 &&
        value.unknownObjects === 0 &&
        value.pendingChildren === 0 &&
        value.heldPipes === 0),
  )
const metadataKeys = [
  'kind',
  'volume',
  'file',
  'links',
  'aclChecked',
  'heldObjectOnly',
  'productionAdmission',
]
const snapshotKeys = [
  'status',
  'abiVersion',
  'epoch',
  'accepting',
  'closed',
  'heldObjects',
  'unknownObjects',
  'pendingChildren',
  'heldPipes',
  'inflight',
  'everCaps',
  'nameBytes',
  'productionAdmission',
]
const methodNames = [
  'root',
  'directory',
  'file',
  'observe',
  'release',
  'snapshot',
  'revoke',
  'close',
] as const
const bindingKeys = ['abiVersion', 'fixtureBound', 'productionAdmission', ...methodNames]
type MethodName = (typeof methodNames)[number]
type Method = (...args: unknown[]) => unknown
const methodSchema = z.custom<Method>((value) => typeof value === 'function')
const bindingSchema = z
  .object({
    abiVersion: z.literal(1),
    fixtureBound: z.literal(1),
    productionAdmission: z.literal(0),
    root: methodSchema,
    directory: methodSchema,
    file: methodSchema,
    observe: methodSchema,
    release: methodSchema,
    snapshot: methodSchema,
    revoke: methodSchema,
    close: methodSchema,
  })
  .strict()

function record(raw: unknown, allowed: readonly string[]): Record<string, unknown> | undefined {
  try {
    if (typeof raw !== 'object' || raw === null) return undefined
    const prototype = Object.getPrototypeOf(raw)
    if (prototype !== null && prototype !== Object.prototype) return undefined
    const keys = Reflect.ownKeys(raw)
    if (keys.length > allowed.length) return undefined
    const result: Record<string, unknown> = Object.create(null) as Record<string, unknown>
    for (const key of keys) {
      if (typeof key !== 'string' || !allowed.includes(key)) return undefined
      const descriptor = Object.getOwnPropertyDescriptor(raw, key)
      if (!descriptor || !Object.hasOwn(descriptor, 'value')) return undefined
      result[key] = descriptor.value as unknown
    }
    return result
  } catch {
    return undefined
  }
}

export interface NativeLocationCap {
  readonly heldObjectOnly: true
}
export type NativeLocationMetadata = Readonly<z.infer<typeof metadataSchema>>
export type NativeLocationSnapshot = Readonly<z.infer<typeof snapshotSchema>>
export type NativeLocationAcquired = Readonly<{
  cap: NativeLocationCap
  metadata: NativeLocationMetadata
}>
export type NativeLocationResult<T = undefined> = Readonly<{
  status: NativeLocationStatus
  productionAdmission: 'unsupported'
  value?: T
}>
const result = <T>(status: NativeLocationStatus, value?: T): NativeLocationResult<T> =>
  Object.freeze(
    value === undefined
      ? { status, productionAdmission: 'unsupported' as const }
      : { status, productionAdmission: 'unsupported' as const, value },
  )

/** Trusted native-harness injection only. No public IPC/preload/main wiring. A
 * synthetic table in unit tests exercises projection mechanics, never OS facts. */
export function createNativeLocationOwner(rawBinding: unknown) {
  const captured = record(rawBinding, bindingKeys)
  const parsed = bindingSchema.safeParse(captured)
  if (!parsed.success) return undefined
  const binding = parsed.data
  const caps = new WeakMap<NativeLocationCap, { native: unknown; unknown: boolean }>()
  let accepting = true
  let closed = false
  let inCall = false
  let pendingRevoke = false
  let retained = false

  function direct(name: MethodName, args: readonly unknown[] = []): unknown {
    return Reflect.apply(binding[name], rawBinding, args)
  }
  function requestRevoke(): NativeLocationStatus {
    accepting = false
    if (inCall) {
      pendingRevoke = true
      return 'busy'
    }
    try {
      const reply = record(direct('revoke'), ['status'])
      const parsedCode = codeSchema.safeParse(reply?.status)
      if (!parsedCode.success || !reply || Object.keys(reply).length !== 1) {
        retained = true
        return 'internal'
      }
      const status = statuses[parsedCode.data] ?? 'internal'
      if (status !== 'ok') retained = true
      return status
    } catch {
      retained = true
      return 'internal'
    }
  }
  function call(
    name: MethodName,
    args: readonly unknown[],
    cleanup = false,
  ): Record<string, unknown> | undefined {
    if (closed || (!cleanup && !accepting)) return { status: 2 }
    if (inCall) return { status: 6 }
    inCall = true
    try {
      const allowed =
        name === 'snapshot'
          ? snapshotKeys
          : name === 'root' || name === 'directory' || name === 'file'
            ? ['status', 'cap', 'metadata']
            : name === 'observe'
              ? ['status', 'metadata']
              : ['status']
      const reply = record(direct(name, args), allowed)
      if (!reply || !codeSchema.safeParse(reply.status).success) {
        retained = true
        pendingRevoke = true
        accepting = false
        return undefined
      }
      if (reply.status !== 0 && Object.keys(reply).length !== 1) {
        retained = true
        pendingRevoke = true
        accepting = false
        return undefined
      }
      return reply
    } catch {
      // Unknown native outcome remains with its original native owner. No JS
      // counter, logical timeout, throw or GC can sign resource completion.
      retained = true
      pendingRevoke = true
      accepting = false
      return undefined
    } finally {
      inCall = false
      if (pendingRevoke) {
        pendingRevoke = false
        requestRevoke()
      }
    }
  }
  function decode<T>(
    reply: Record<string, unknown> | undefined,
  ): NativeLocationResult<T> | undefined {
    if (!reply) return result<T>('internal')
    const status = statuses[reply.status as number] ?? 'internal'
    return status === 'ok' ? undefined : result<T>(status)
  }
  function receiveCap(reply: Record<string, unknown> | undefined): NativeLocationResult<
    Readonly<{
      cap: NativeLocationCap
      metadata: NativeLocationMetadata
    }>
  > {
    const failure =
      decode<Readonly<{ cap: NativeLocationCap; metadata: NativeLocationMetadata }>>(reply)
    if (failure) return failure
    const observed = metadataSchema.safeParse(record(reply?.metadata, metadataKeys))
    if (
      !reply ||
      !Object.hasOwn(reply, 'cap') ||
      reply.cap === undefined ||
      reply.cap === null ||
      !observed.success
    ) {
      retained = true
      requestRevoke()
      return result('internal')
    }
    if (!accepting) {
      // A reentrant revoke in a synthetic test cannot publish the late wrapper.
      retained = true
      requestRevoke()
      return result('stale')
    }
    const cap = Object.freeze({ heldObjectOnly: true as const })
    caps.set(cap, { native: reply.cap, unknown: false })
    return result('ok', Object.freeze({ cap, metadata: Object.freeze(observed.data) }))
  }
  function acquire(
    kind: 'directory' | 'file',
    parent: NativeLocationCap,
    name: string,
    expected?: NativeLocationCap,
  ): NativeLocationResult<NativeLocationAcquired> {
    const nativeParent = caps.get(parent)
    const nativeExpected = expected === undefined ? undefined : caps.get(expected)
    if (!nativeParent || nativeParent.unknown || (expected !== undefined && !nativeExpected))
      return result('invalid')
    // Exact byte/name validation remains in native. Bound before crossing it.
    if (
      typeof name !== 'string' ||
      name.length === 0 ||
      name.length > 255 ||
      Buffer.byteLength(name, 'utf8') > 255
    )
      return result('invalid')
    const args = nativeExpected
      ? [nativeParent.native, name, nativeExpected.native]
      : [nativeParent.native, name]
    return receiveCap(call(kind, args))
  }
  return Object.freeze({
    productionAdmission: 'unsupported' as const,
    root: () => receiveCap(call('root', [])),
    directory: (parent: NativeLocationCap, name: string, expected?: NativeLocationCap) =>
      acquire('directory', parent, name, expected),
    file: (parent: NativeLocationCap, name: string, expected?: NativeLocationCap) =>
      acquire('file', parent, name, expected),
    observe(cap: NativeLocationCap): NativeLocationResult<NativeLocationMetadata> {
      const value = caps.get(cap)
      if (!value || value.unknown) return result('invalid')
      const reply = call('observe', [value.native])
      const failure = decode<NativeLocationMetadata>(reply)
      if (failure) return failure
      const observed = metadataSchema.safeParse(record(reply?.metadata, metadataKeys))
      if (!observed.success) {
        retained = true
        requestRevoke()
        return result('internal')
      }
      if (!accepting) return result('stale')
      return result('ok', Object.freeze(observed.data))
    },
    release(cap: NativeLocationCap): NativeLocationResult {
      const value = caps.get(cap)
      if (!value) return result('invalid')
      if (value.unknown) return result('retained')
      const reply = call('release', [value.native], true)
      const status = reply ? (statuses[reply.status as number] ?? 'internal') : 'internal'
      if (status === 'ok') caps.delete(cap)
      else if (status !== 'busy' && status !== 'budget') {
        value.unknown = true
        retained = true
      }
      return result(status)
    },
    snapshot(): NativeLocationResult<NativeLocationSnapshot> {
      const reply = call('snapshot', [], true)
      const failure = decode<NativeLocationSnapshot>(reply)
      if (failure) return failure
      const observed = snapshotSchema.safeParse(reply)
      if (!observed.success) {
        retained = true
        requestRevoke()
        return result('internal')
      }
      if (!observed.data.accepting) accepting = false
      return result('ok', Object.freeze(observed.data))
    },
    revoke: (): NativeLocationResult => result(requestRevoke()),
    close(): NativeLocationResult {
      if (closed) return result('ok')
      accepting = false
      const reply = call('close', [], true)
      const status = reply ? (statuses[reply.status as number] ?? 'internal') : 'internal'
      if (status === 'ok') closed = true
      else retained = true
      return result(status)
    },
    localState: () =>
      Object.freeze({ accepting, closed, retained, productionAdmission: 'unsupported' as const }),
  })
}
