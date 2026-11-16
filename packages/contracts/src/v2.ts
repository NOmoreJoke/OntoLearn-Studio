/** Shared v2 value validators. Transport additionally validates raw JSONL bytes. */
import { z } from 'zod'
import document from '../v2/schema.json'
import registry from '../v2/registry.json'
import errorCatalog from '../v2/errors.json'
import { permitsTransition } from './states-v2'

interface Schema {
  $ref?: string
  const?: unknown
  enum?: unknown[]
  oneOf?: Schema[]
  type?: string
  properties?: Record<string, Schema>
  required?: string[]
  additionalProperties?: boolean | Schema
  propertyNames?: Schema
  minProperties?: number
  maxProperties?: number
  items?: Schema
  minItems?: number
  maxItems?: number
  minLength?: number
  maxLength?: number
  pattern?: string
  minimum?: number
  maximum?: number
}
const definitions = document.$defs as unknown as Record<string, Schema>
// A shared conservative encoded-byte budget: numeric tokens cost 32 bytes. This
// avoids ECMAScript/Python float-format differences while bounding actual JSON.
function utf8(value: unknown): number {
  if (typeof value === 'number') return 32
  if (Array.isArray(value))
    return 2 + Math.max(0, value.length - 1) + value.reduce((n, v) => n + utf8(v), 0)
  if (value && typeof value === 'object') {
    const entries = Object.entries(value)
    return (
      2 +
      Math.max(0, entries.length - 1) +
      entries.reduce((n, [k, v]) => n + utf8(k) + 1 + utf8(v), 0)
    )
  }
  return new TextEncoder().encode(JSON.stringify(value)).byteLength
}
const fail = () => {
  throw new Error('INVALID_REQUEST')
}

// Only the documented JSON Schema subset is supported; unknown vocabulary fails closed.
const keywords = new Set([
  '$ref',
  'const',
  'enum',
  'oneOf',
  'type',
  'properties',
  'required',
  'additionalProperties',
  'propertyNames',
  'minProperties',
  'maxProperties',
  'items',
  'minItems',
  'maxItems',
  'minLength',
  'maxLength',
  'pattern',
  'minimum',
  'maximum',
])
function compile(s: Schema): z.ZodType {
  if (Object.keys(s).some((key) => !keywords.has(key))) return fail()
  if (s.$ref) {
    if (!s.$ref.startsWith('#/$defs/') || !definitions[s.$ref.slice(8)]) return fail()
    return compile(definitions[s.$ref.slice(8)])
  }
  if ('const' in s) return z.unknown().refine((v) => v === s.const)
  if (s.enum) return z.unknown().refine((v) => s.enum!.includes(v))
  if (s.oneOf) {
    const alternatives = s.oneOf.map(compile)
    return z
      .unknown()
      .refine((v) => alternatives.filter((schema) => schema.safeParse(v).success).length === 1)
  }
  if (s.type === 'object') {
    const shape = Object.fromEntries(
      Object.entries(s.properties ?? {}).map(([key, value]) => [
        key,
        (s.required ?? []).includes(key) ? compile(value) : compile(value).optional(),
      ]),
    )
    const object =
      s.additionalProperties === false
        ? z.object(shape).strict()
        : z
            .object(shape)
            .catchall(
              typeof s.additionalProperties === 'object'
                ? compile(s.additionalProperties)
                : z.unknown(),
            )
    const keys = s.propertyNames ? compile(s.propertyNames) : null
    return object.refine(
      (v) =>
        Object.keys(v).length >= (s.minProperties ?? 0) &&
        Object.keys(v).length <= (s.maxProperties ?? Infinity) &&
        (!keys || Object.keys(v).every((key) => keys.safeParse(key).success)),
    )
  }
  if (s.type === 'array')
    return z
      .array(compile(s.items!))
      .min(s.minItems ?? 0)
      .max(s.maxItems ?? 100000)
  if (s.type === 'string')
    return z
      .string()
      .refine(
        (v) =>
          [...v].length >= (s.minLength ?? 0) &&
          [...v].length <= (s.maxLength ?? Infinity) &&
          [...v].every((c) => c.codePointAt(0)! < 0xd800 || c.codePointAt(0)! > 0xdfff) &&
          (!s.pattern || new RegExp(s.pattern).exec(v)?.[0] === v),
      )
  if (s.type === 'boolean') return z.boolean()
  if (s.type === 'integer')
    return z
      .number()
      .int()
      .min(s.minimum ?? -Number.MAX_SAFE_INTEGER)
      .max(s.maximum ?? Number.MAX_SAFE_INTEGER)
  if (s.type === 'number')
    return z
      .number()
      .finite()
      .min(s.minimum ?? -Number.MAX_SAFE_INTEGER)
      .max(s.maximum ?? Number.MAX_SAFE_INTEGER)
  return fail()
}
const compiled = new Map<string, z.ZodType>()
export const v2Registry = registry
export const v2SchemaNames = Object.keys(definitions)

function semantic(value: unknown): boolean {
  if (Array.isArray(value)) return value.every(semantic)
  if (!value || typeof value !== 'object') return true
  const v = value as Record<string, unknown>
  if (v.projectionVersion === 1 && v.projectionPolicy === 'selected-facts-v1' && v.derived) {
    const derived = v.derived as Record<string, unknown>
    const expected = v.implementation as Record<string, unknown>
    const actual = derived.implementation as Record<string, unknown>
    if (
      derived.projectId !== v.projectId ||
      derived.inputSnapshotId !== v.inputSnapshotId ||
      Object.keys(expected).some((key) => expected[key] !== actual[key])
    )
      return false
  }
  if ('code' in v && 'messageKey' in v && utf8(v) > errorCatalog.maxEncodedBytes) return false
  if (typeof v.completed === 'number' && typeof v.total === 'number' && v.completed > v.total)
    return false
  if ('staleReason' in v) {
    const reasons = v.staleReason as Array<{ dependency: string; before: number; after: number }>
    const vector = v.dependencyVector as Record<string, number>
    const sets = v.definitionSetDigests as Record<string, unknown>
    if (
      !Object.hasOwn(vector, 'facts:asserted') ||
      new Set(reasons.map((r) => r.dependency)).size !== reasons.length
    )
      return false
    if (
      reasons.some((r) =>
        Object.hasOwn(vector, r.dependency)
          ? vector[r.dependency] !== r.before
          : r.before !== 0 || r.after < 1 || !Object.hasOwn(sets, r.dependency.split(':')[0]),
      )
    )
      return false
    if ((v.state === 'stale') !== reasons.length > 0 || reasons.some((r) => r.before === r.after))
      return false
    if (
      v.state === 'current' &&
      (v.payloadStatus !== 'available' || v.historicalSelectionRequired !== false)
    )
      return false
    if (v.state === 'historical' && v.historicalSelectionRequired !== true) return false
    if (v.kind === 'receipt' && v.state !== 'historical') return false
  }
  if ('createdAtMs' in v && 'updatedAtMs' in v && Number(v.updatedAtMs) < Number(v.createdAtMs))
    return false
  if (typeof v.finishedAtMs === 'number' && v.finishedAtMs < Number(v.createdAtMs)) return false
  if (typeof v.finishedAtMs === 'number' && v.finishedAtMs !== v.updatedAtMs) return false
  if (
    'supportedVersions' in v &&
    new Set(v.supportedVersions as unknown[]).size !== (v.supportedVersions as unknown[]).length
  )
    return false
  if (
    'capabilities' in v &&
    new Set(v.capabilities as unknown[]).size !== (v.capabilities as unknown[]).length
  )
    return false
  if ('disposition' in v) {
    const terminal = ['succeeded', 'failed', 'cancelled'].includes(String(v.state))
    if ((v.disposition === 'alreadyTerminal') !== terminal) return false
    if (v.disposition === 'alreadyRequested' && v.state !== 'cancelling') return false
  }
  if (v.event === 'job.state') {
    const data = v.data as Record<string, unknown>
    if (data.projectId !== v.projectId || data.jobId !== v.jobId) return false
  }
  if (v.kind === 'response' && v.method === 'hello' && v.ok) {
    const r = v.result as Record<string, unknown>
    if (v.engineSessionId !== r.engineSessionId) return false
  }
  if (v.method === 'job.list' && v.kind === 'request') {
    const p = v.params as Record<string, unknown>
    if ((p.cursor === null) !== (p.listSnapshotId === null)) return false
  }
  if (v.method === 'job.create' && v.kind === 'request') {
    const p = v.params as Record<string, unknown>
    const c = registry.capabilities[p.capability as keyof typeof registry.capabilities]
    const i = p.input as Record<string, unknown>
    if (!(c.dataScopes as string[]).includes(String(i.scope))) return false
    if (c.requiresConfirmation && (p.confirmationRef === null || i.preparedPlanRef === null))
      return false
    if (!c.requiresConfirmation && (p.confirmationRef !== null || i.preparedPlanRef !== null))
      return false
  }
  if ('capability' in v && 'commitProgress' in v) {
    const c = registry.capabilities[v.capability as keyof typeof registry.capabilities]
    if (!(c.dataScopes as string[]).includes(String(v.scope))) return false
    if (!Object.hasOwn(v.dependencyVector as object, 'facts:asserted')) return false
    const input = v.input as Record<string, unknown>
    if (['inputSnapshotId', 'scope', 'parametersHash'].some((k) => v[k] !== input[k])) return false
    if (
      c.requiresConfirmation
        ? v.confirmationRef === null || input.preparedPlanRef === null
        : v.confirmationRef !== null || input.preparedPlanRef !== null
    )
      return false
    const commit = v.commitProgress as Record<string, unknown>
    const mode = commit.mode
    if (
      (c.cancelBoundary === 'whole-transaction'
        ? 'atomic'
        : c.cancelBoundary === 'uncommitted-round'
          ? 'rounds'
          : 'none') !== mode
    )
      return false
    if (mode === 'atomic' && commit.operationId !== v.operationId) return false
    if (
      v.state === 'queued' &&
      ((mode === 'atomic' && commit.marker !== null) ||
        (mode === 'rounds' && commit.committedProgress !== null))
    )
      return false
    if (
      v.state === 'succeeded' &&
      ((mode === 'atomic' && commit.marker === null) ||
        (mode === 'rounds' && commit.committedProgress === null))
    )
      return false
    if (
      v.resultRef &&
      (v.resultRef as Record<string, unknown>).inputSnapshotId !== v.inputSnapshotId
    )
      return false
  }
  if ('rows' in v && 'binding' in v) {
    const rows = v.rows as Array<{ ordinal: number; rowId: string }>
    if (
      utf8(v) > 131072 ||
      new Set(rows.map((r) => r.rowId)).size !== rows.length ||
      rows.some(
        (r, i) =>
          i > 0 &&
          (r.ordinal < rows[i - 1].ordinal ||
            (r.ordinal === rows[i - 1].ordinal && r.rowId <= rows[i - 1].rowId)),
      )
    )
      return false
  }
  if ('jobs' in v && 'binding' in v) {
    const jobs = v.jobs as Array<{
      jobId: string
      createdAtMs: number
      state: string
      projectId: string
    }>
    const binding = v.binding as Record<string, unknown>
    if (
      new Set(jobs.map((j) => j.jobId)).size !== jobs.length ||
      jobs.some(
        (j, i) =>
          j.projectId !== binding.projectId ||
          (binding.filter === 'active' && ['succeeded', 'failed', 'cancelled'].includes(j.state)) ||
          (binding.filter === 'terminal' &&
            !['succeeded', 'failed', 'cancelled'].includes(j.state)) ||
          (i > 0 &&
            (j.createdAtMs < jobs[i - 1].createdAtMs ||
              (j.createdAtMs === jobs[i - 1].createdAtMs && j.jobId <= jobs[i - 1].jobId))),
      )
    )
      return false
  }
  return Object.values(v).every(semantic)
}
export function validateV2(name: string, value: unknown): boolean {
  if (!Object.hasOwn(definitions, name)) return false
  if (!compiled.has(name)) compiled.set(name, compile(definitions[name]))
  if (!compiled.get(name)!.safeParse(value).success || !semantic(value) || utf8(value) > 262144)
    return false
  if (
    !changeSetSemantics(name, value) ||
    !queryConsumerSemantics(name, value) ||
    !checkpointSemantics(name, value)
  )
    return false
  if (name === 'params_job.create' || name === 'params_job.list')
    return semantic({ kind: 'request', method: name.slice(7), params: value })
  return true
}

// B1b checkpoint/restore invariants: contiguous segmented documents and a
// complete, duplicate-free read proof before any restore authority is signed.
function checkpointSemantics(name: string, value: unknown): boolean {
  const v = value as Record<string, unknown>
  if (['request3', 'response3', 'envelope3'].includes(name)) {
    const target = /^project\.(checkpoint|restore)\./
    if (v.kind === 'request' && target.test(String(v.method)))
      return checkpointSemantics(`params_${v.method}`, v.params)
    if (v.kind === 'response' && v.ok && target.test(String(v.method)))
      return checkpointSemantics(`result_${v.method}`, v.result)
    return true
  }
  if (name === 'restore.manifest') {
    const parts = v.segments as Array<Record<string, unknown>>
    let offset = 0
    if (parts.length !== v.segmentCount) return false
    for (const [ordinal, part] of parts.entries()) {
      if (part.ordinal !== ordinal || part.byteOffset !== offset) return false
      offset += part.rawByteLength as number
    }
    return offset === v.totalBytes
  }
  if (name === 'restore.segment') {
    const encoded = v.dataBase64 as string
    const padding = encoded.endsWith('==') ? 2 : encoded.endsWith('=') ? 1 : 0
    return Math.floor(encoded.length / 4) * 3 - padding === v.rawByteLength
  }
  if (name === 'result_project.restore.page') {
    const parts = v.segments as Array<Record<string, unknown>>
    return parts.every((part, index) => {
      if (!checkpointSemantics('restore.segment', part)) return false
      if (index === 0) return true
      const previous = parts[index - 1]
      return (
        part.ordinal === (previous.ordinal as number) + 1 &&
        part.byteOffset === (previous.byteOffset as number) + (previous.rawByteLength as number)
      )
    })
  }
  if (name === 'params_project.restore.confirm') {
    const read = v.readSegmentHashes as string[]
    return new Set(read).size === read.length
  }
  return true
}

// Additional invariants apply only to the new typed ChangeSet definitions/strict3 methods.
function changeSetSemantics(name: string, value: unknown): boolean {
  const v = value as Record<string, unknown>
  if (['request3', 'response3', 'envelope3'].includes(name)) {
    if (v.kind === 'request' && v.method === 'changeset.preview')
      return changeSetSemantics('params_changeset.preview', v.params)
    if (v.kind === 'response' && v.ok && String(v.method).startsWith('changeset.'))
      return changeSetSemantics(`result_${v.method}`, v.result)
    return true
  }
  if (name === 'params_changeset.preview')
    return v.intent !== 'change' || changeSetSemantics('changeSetPlan', v.plan)
  if (name === 'changeSetPlan')
    return ((v.definitions ?? []) as unknown[]).every((item) =>
      changeSetSemantics('changeSetDefinition', item),
    )
  if (name === 'changeSetDefinition' || name === 'changeSetOntologyDefinition')
    return v.layer !== 'ontology' || changeSetSemantics('changeSetOntologyValue', v.value)
  if (name === 'changeSetOntologyValue')
    return !Object.hasOwn(v, 'entityMetadata') || entityMetadataSemantics(v.entityMetadata)
  if (name === 'changeSetEntityMetadata') return entityMetadataSemantics(value)
  if (name === 'changeSetManifest') {
    const parts = v.segments as Array<Record<string, unknown>>
    let offset = 0
    if (parts.length !== v.segmentCount) return false
    for (const [ordinal, part] of parts.entries()) {
      if (part.ordinal !== ordinal || part.byteOffset !== offset) return false
      offset += part.rawByteLength as number
    }
    return offset === v.totalBytes
  }
  if (name === 'result_changeset.preview') {
    const manifest = v.manifest as Record<string, unknown>
    return (
      changeSetSemantics('changeSetManifest', manifest) &&
      (v.status === 'conflict'
        ? manifest.documentKind === 'undo-impact'
        : manifest.documentKind === 'diff' &&
          (v.intent === 'change' ? v.targetOperationId === null : v.targetOperationId !== null))
    )
  }
  if (name === 'changeSetSegment') {
    const encoded = v.dataBase64 as string
    const padding = encoded.endsWith('==') ? 2 : encoded.endsWith('=') ? 1 : 0
    return (encoded.length / 4) * 3 - padding === v.rawByteLength
  }
  if (name === 'changeSetPage' || name === 'result_changeset.diff.page') {
    const parts = v.segments as Array<Record<string, unknown>>
    return parts.every(
      (part, index) =>
        changeSetSemantics('changeSetSegment', part) &&
        (index === 0 ||
          (part.ordinal === (parts[index - 1].ordinal as number) + 1 &&
            part.byteOffset ===
              (parts[index - 1].byteOffset as number) +
                (parts[index - 1].rawByteLength as number))),
    )
  }
  return true
}

// Python str.isspace(), without normalization or ECMAScript-only FEFF whitespace.
const metadataWhitespace = new Set([
  9, 10, 11, 12, 13, 28, 29, 30, 31, 32, 133, 160, 5760, 8192, 8193, 8194, 8195, 8196, 8197, 8198,
  8199, 8200, 8201, 8202, 8232, 8233, 8239, 8287, 12288,
])
function entityMetadataSemantics(value: unknown): boolean {
  const metadata = value as { entities: Record<string, Record<string, unknown>> }
  const text = (v: string) =>
    [...v].length <= 16000 && [...v].some((c) => !metadataWhitespace.has(c.codePointAt(0)!))
  for (const [iri, entity] of Object.entries(metadata.entities)) {
    if (
      !/^[A-Za-z][A-Za-z0-9+.-]*:/.test(iri) ||
      [...iri].some((c) => metadataWhitespace.has(c.codePointAt(0)!) || '<>"{}|^`\\'.includes(c))
    )
      return false
    for (const field of ['labels', 'definitions']) {
      const pairs = entity[field] as string[][]
      if (
        new Set(pairs.map((pair) => JSON.stringify(pair))).size !== pairs.length ||
        pairs.some(
          ([literal, language]) =>
            !text(literal) || /^(?:[a-z]+(?:-[a-z0-9]+)*)?$/.exec(language)?.[0] !== language,
        )
      )
        return false
    }
    for (const field of ['synonyms', 'examples']) {
      const values = entity[field] as string[]
      if (new Set(values).size !== values.length || values.some((v) => !text(v))) return false
    }
  }
  return true
}

/** A value check only: provenance, pre-hello, profile and once belong to the supervisor. */
export function validateStartupError(value: unknown): boolean {
  try {
    return validateV2('error_startup', value)
  } catch {
    return false
  }
}

/** payloadByteLength must come from the transport's original bytes, never re-encoding. */
export function validateStartupFailure(
  value: unknown,
  payloadByteLength: number,
  expectedRegistryHash: string,
): boolean {
  return (
    Number.isSafeInteger(payloadByteLength) &&
    payloadByteLength > 0 &&
    payloadByteLength <= errorCatalog.startup.maxPayloadBytes &&
    typeof expectedRegistryHash === 'string' &&
    /^[0-9a-f]{64}$/.test(expectedRegistryHash) &&
    validateV2('startupFailure', value) &&
    (value as Record<string, unknown>).registryHash === expectedRegistryHash
  )
}

/** Strict explicit profile validation. It never selects runtime or attests readiness. */

export function validateBusiness3(name: string, value: unknown): boolean {
  const profiles: Record<string, string> = {
    request: 'request3',
    response: 'response3',
    notification: 'notification3',
    envelope: 'envelope3',
    error: 'error3',
    bootstrapError: 'error_bootstrap3',
    project: 'project3',
    'result_project.get': 'result_project.get3',
    result_hello: 'result_hello3',
  }
  try {
    return validateV2(profiles[name] ?? name, value)
  } catch {
    return false
  }
}

/** Correlate a pending request; this does not attest Store/Job readiness. */
function ownershipSha256(raw: Uint8Array): string {
  // Bounded (<=32KiB) segments. Synchronous SHA keeps both contract matchers
  // independent of transport metadata; the owning transport prepays the frame.
  const k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ]
  const h = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ]
  const bytes = new Uint8Array(Math.ceil((raw.length + 9) / 64) * 64)
  bytes.set(raw)
  bytes[raw.length] = 0x80
  const view = new DataView(bytes.buffer)
  view.setUint32(bytes.length - 4, raw.length * 8)
  const w = new Uint32Array(64)
  const rotate = (x: number, n: number) => (x >>> n) | (x << (32 - n))
  for (let offset = 0; offset < bytes.length; offset += 64) {
    for (let i = 0; i < 16; i++) w[i] = view.getUint32(offset + 4 * i)
    for (let i = 16; i < 64; i++) {
      const x = w[i - 15]!,
        y = w[i - 2]!
      w[i] =
        (w[i - 16]! +
          (rotate(x, 7) ^ rotate(x, 18) ^ (x >>> 3)) +
          w[i - 7]! +
          (rotate(y, 17) ^ rotate(y, 19) ^ (y >>> 10))) >>>
        0
    }
    let [a, b, c, d, e, f, g, j] = h as [
      number,
      number,
      number,
      number,
      number,
      number,
      number,
      number,
    ]
    for (let i = 0; i < 64; i++) {
      const t =
        (j +
          (rotate(e, 6) ^ rotate(e, 11) ^ rotate(e, 25)) +
          ((e & f) ^ (~e & g)) +
          k[i]! +
          w[i]!) >>>
        0
      const u =
        ((rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0
      j = g
      g = f
      f = e
      e = (d + t) >>> 0
      d = c
      c = b
      b = a
      a = (t + u) >>> 0
    }
    const next = [a, b, c, d, e, f, g, j]
    for (let i = 0; i < 8; i++) h[i] = (h[i]! + next[i]!) >>> 0
  }
  return h.map((n) => n.toString(16).padStart(8, '0')).join('')
}

export function matchesOwnershipDetail(params: unknown, value: unknown): boolean {
  if (
    !validateBusiness3('params_project.ownership.detail', params) ||
    !validateBusiness3('result_project.ownership.detail', value)
  )
    return false
  const p = params as {
    projectId: string
    detailRef: string
    documentHash: string | null
    startOrdinal: number
    pageSize: number
  }
  const v = value as {
    projectId: string
    detailRef: string
    manifest: { documentHash: string; totalBytes: number; segmentCount: number }
    startOrdinal: number
    segments: Array<{
      ordinal: number
      byteOffset: number
      rawByteLength: number
      sha256: string
      dataBase64: string
    }>
    nextOrdinal: number | null
    complete: boolean
  }
  const count = Math.ceil(v.manifest.totalBytes / 32768),
    end = p.startOrdinal + v.segments.length
  if (
    v.projectId !== p.projectId ||
    v.detailRef !== p.detailRef ||
    v.startOrdinal !== p.startOrdinal ||
    count !== v.manifest.segmentCount ||
    v.segments.length > p.pageSize ||
    end > count ||
    (p.documentHash !== null && p.documentHash !== v.manifest.documentHash) ||
    v.nextOrdinal !== (end === count ? null : end) ||
    v.complete !== (end === count)
  )
    return false
  return v.segments.every((s, index) => {
    const ordinal = p.startOrdinal + index,
      length = Math.min(32768, v.manifest.totalBytes - ordinal * 32768)
    if (s.ordinal !== ordinal || s.byteOffset !== ordinal * 32768 || s.rawByteLength !== length)
      return false
    try {
      const raw = Uint8Array.from(atob(s.dataBase64), (c) => c.charCodeAt(0))
      return raw.length === length && ownershipSha256(raw) === s.sha256
    } catch {
      return false
    }
  })
}

export function matchesBusiness3Response(
  request: unknown,
  response: unknown,
  expectedRegistryHash: string,
): boolean {
  if (
    !validateV2('hash', expectedRegistryHash) ||
    !validateBusiness3('request', request) ||
    !validateBusiness3('response', response)
  )
    return false
  const q = request as Record<string, unknown>
  const r = response as Record<string, unknown>
  if (q.id !== r.id || q.method !== r.method) return false
  if (String(q.method).startsWith('project.management.') || q.method === 'project.library.status') {
    if (q.engineSessionId !== r.engineSessionId) return false
    if (!r.ok) return true
    const p = q.params as Record<string, unknown>
    const value = r.result as Record<string, unknown>
    if (q.method === 'project.library.status') return true
    if (q.method === 'project.management.catalog') {
      const items = value.items as Array<Record<string, unknown>>
      const end = Number(value.offset) + items.length
      return (
        items.length <= Number(p.pageSize) &&
        new Set(items.map((item) => item.projectId)).size === items.length &&
        end <= Number(value.total) &&
        (value.nextCursor === null
          ? end === value.total
          : items.length > 0 && end < Number(value.total)) &&
        items.every((item) => {
          const lifecycle = item.lifecycle as Record<string, unknown>
          const metadata = item.metadata as Record<string, unknown>
          return p.state === 'trashed'
            ? lifecycle.state === 'trashed'
            : lifecycle.state === 'active' && metadata.archived === (p.state === 'archived')
        })
      )
    }
    if (q.method === 'project.management.operation.get') {
      if (value.state === 'not-found') return value.result === null
      const result = value.result as Record<string, unknown>
      return (
        result.projectId === p.projectId &&
        result.operationId === p.operationId &&
        result.requestHash === p.requestHash &&
        (result.kind === 'copy-current'
          ? result.targetProjectId !== result.projectId
          : result.targetProjectId === result.projectId)
      )
    }
    if (value.projectId !== p.projectId) return false
    if (q.method === 'project.management.read') return true
    if (q.method === 'project.management.preview') {
      const action = value.action as Record<string, unknown>
      const requested = p.action as Record<string, unknown>
      const document = value.document as Record<string, unknown>
      return (
        Object.keys(action).length === Object.keys(requested).length &&
        Object.keys(action).every((key) => action[key] === requested[key]) &&
        document.checkpointRef === p.expectedCheckpointRef &&
        document.lifecycleVersion === p.expectedLifecycleVersion
      )
    }
    if (q.method === 'project.management.confirm')
      return value.previewRef === p.previewRef && value.documentHash === p.documentHash
    // Main additionally verifies the original canonical request's SHA-256.
    return (
      q.method === 'project.management.apply' &&
      value.operationId === p.operationId &&
      (value.kind === 'copy-current'
        ? value.targetProjectId !== value.projectId
        : value.targetProjectId === value.projectId)
    )
  }
  if (/^project\.(checkpoint|restore)\./.test(String(q.method))) {
    if (q.engineSessionId !== r.engineSessionId) return false
    if (!r.ok) return true
    const p = q.params as Record<string, unknown>
    const value = r.result as Record<string, unknown>
    if (value.projectId !== p.projectId) return false
    const method = String(q.method)
    if (method === 'project.checkpoint.list') {
      const items = value.items as Array<Record<string, unknown>>
      const end = Number(value.offset) + items.length
      const current = items.filter((item) => item.isCurrent === true)
      return (
        items.length <= Number(p.pageSize) &&
        end <= Number(value.total) &&
        (value.nextCursor === null
          ? end === Number(value.total)
          : items.length > 0 && end < Number(value.total)) &&
        new Set(items.map((item) => item.checkpointRef)).size === items.length &&
        current.length <= 1
      )
    }
    if (method === 'project.checkpoint.create')
      return value.operationId === p.operationId && value.reason === 'manual'
    if (method === 'project.restore.preview') {
      const manifest = value.manifest as Record<string, unknown>
      return (
        value.targetCheckpointRef === p.targetCheckpointRef &&
        value.currentCheckpointRef === p.expectedCheckpointRef &&
        value.documentHash === manifest.documentHash
      )
    }
    if (method === 'project.restore.page') return value.previewRef === p.previewRef
    if (method === 'project.restore.confirm')
      return value.previewRef === p.previewRef && value.documentHash === p.documentHash
    if (method === 'project.restore.apply') return value.operationId === p.operationId
    if (method !== 'project.restore.operation.get') return false
    if (value.state === 'not-found') return value.result === null
    const result = value.result as Record<string, unknown>
    return result.operationId === p.operationId && result.requestHash === p.requestHash
  }
  if (/^project\.learning\./.test(String(q.method))) {
    if (q.engineSessionId !== r.engineSessionId) return false
    if (!r.ok) return true
    const p = q.params as Record<string, unknown>
    const value = r.result as Record<string, unknown>
    if (value.projectId !== p.projectId) return false
    const method = String(q.method)
    if (method === 'project.learning.read') return true
    if (value.operationId !== p.operationId || value.taskId !== p.taskId) return false
    if (method === 'project.learning.hint.record') return value.level === p.level
    if (method === 'project.learning.observation.record')
      return JSON.stringify(value.observation) === JSON.stringify(p.observation)
    return method === 'project.learning.attempt.start' || method === 'project.learning.task.check'
  }
  if (q.method === 'project.ownership.detail')
    return (
      q.engineSessionId === r.engineSessionId &&
      (!r.ok || matchesOwnershipDetail(q.params, r.result))
    )
  if (q.method === 'project.draft.save') {
    if (q.engineSessionId !== r.engineSessionId) return false
    if (!r.ok) return true
    const p = q.params as Record<string, unknown>,
      value = r.result as Record<string, unknown>
    // The production main service verifies SHA-256 of the original UTF-8 JSON.
    return (
      value.projectId === p.projectId &&
      value.operationId === p.operationId &&
      value.editor === p.editor &&
      value.generation === Number(p.expectedGeneration) + 1 &&
      value.boundDomainRevision === p.boundDomainRevision
    )
  }
  if (
    [
      'project.catalog',
      'project.create',
      'project.example.create',
      'project.open',
      'project.read',
    ].includes(String(q.method))
  ) {
    if (q.engineSessionId !== r.engineSessionId) return false
    if (!r.ok) return true
    const p = q.params as Record<string, unknown>
    const value = r.result as Record<string, unknown>
    if (q.method === 'project.catalog') {
      const items = value.items as unknown[]
      const end = Number(value.offset) + items.length
      return (
        items.length <= Number(p.pageSize) &&
        end <= Number(value.total) &&
        (value.nextCursor === null
          ? end === value.total
          : items.length > 0 && end < Number(value.total))
      )
    }
    if (q.method === 'project.create' || q.method === 'project.example.create') {
      const receipt = value.receipt as Record<string, unknown>
      // The main-process client additionally binds requestHash to SHA-256 of
      // the actual canonical request before publishing the accepted project.
      return (
        p.operationId === value.operationId &&
        receipt.operationId === p.operationId &&
        receipt.projectId === value.projectId &&
        receipt.requestHash === value.requestHash
      )
    }
    if (value.projectId !== p.projectId) return false
    if (q.method === 'project.open') return true
    const workspace = value.workspace as Record<string, unknown>
    const domain = value.domain as Record<string, unknown>
    const draft = workspace.draft as Record<string, unknown>
    return (
      workspace.projectId === p.projectId &&
      workspace.inputSnapshotId === value.inputSnapshotId &&
      domain.projectRevision === workspace.domainRevision &&
      draft.editor === p.editor &&
      (draft.state === 'missing' ||
        (draft.state === 'present'
          ? draft.present === true &&
            typeof draft.contentJson === 'string' &&
            typeof draft.contentHash === 'string'
          : draft.present === false && draft.contentJson === null && draft.contentHash === null))
    )
  }
  if (String(q.method).startsWith('changeset.')) {
    if (q.engineSessionId !== r.engineSessionId) return false
    if (!r.ok) return true
    const p = q.params as Record<string, unknown>
    const data = r.result as Record<string, unknown>
    if (p.projectId !== data.projectId) return false
    if (q.method === 'changeset.preview')
      return (
        p.baseRevision === data.baseRevision &&
        (p.intent === 'change'
          ? data.status === 'ready' && data.intent === 'change' && data.targetOperationId === null
          : data.targetOperationId === p.targetOperationId &&
            (data.status === 'conflict' || data.intent === 'undo'))
      )
    if (p.previewHash !== data.previewHash) return false
    if (q.method === 'changeset.diff.page')
      return (
        p.documentKind === data.documentKind &&
        (data.segments as unknown[]).length <= (p.pageSize as number)
      )
    return q.method === 'changeset.confirm'
  }
  if (q.method === 'hello' && r.ok) {
    const offered = (q.params as Record<string, unknown>).supportedVersions as number[]
    const result = r.result as Record<string, unknown>
    if (
      !offered.includes(3) ||
      result.registryHash !== expectedRegistryHash ||
      !(result.capabilities as string[]).every((c) =>
        (registry.foundationProfiles.business3.methods as string[]).includes(c),
      )
    )
      return false
    // A successful strict3 hello may advertise internal3-only methods. Projecting
    // it through the legacy2 capability allowlist would reject this valid build.
    return true
  }
  // Strict v3 validation precedes this binding-only projection. It never sends
  // a v2 fallback, drops unknown fields or changes the caller's actual objects.
  const projectedRequest = structuredClone(q)
  const projectedResponse = structuredClone(r)
  projectedRequest.protocolVersion = projectedResponse.protocolVersion = 2
  if (q.method === 'hello') {
    ;(projectedRequest.params as Record<string, unknown>).supportedVersions = [2]
    if (r.ok) (projectedResponse.result as Record<string, unknown>).selectedVersion = 2
  }
  if (q.method === 'project.get' && r.ok)
    (projectedResponse.result as Record<string, unknown>).formatVersion = 2
  if (!r.ok) {
    const error = projectedResponse.error as Record<string, unknown>
    if (error.code === 'VERSION_INCOMPATIBLE') error.params = { supportedVersions: [2] }
  }
  return matchesResponse(projectedRequest, projectedResponse)
}

export function business3HelloOutcome(
  request: unknown,
  response: unknown,
  expectedRegistryHash: string,
): 'success' | 'incompatible-close' | 'rejected-close' | 'invalid-close' {
  if (
    !matchesBusiness3Response(request, response, expectedRegistryHash) ||
    (request as Record<string, unknown>).method !== 'hello'
  )
    return 'invalid-close'
  const r = response as Record<string, unknown>
  if (r.ok) return 'success'
  return (r.error as Record<string, unknown>).code === 'VERSION_INCOMPATIBLE'
    ? 'incompatible-close'
    : 'rejected-close'
}

export function acceptsBusiness3JobEvent(value: unknown, binding: EventBinding): boolean {
  if (!validateBusiness3('notification', value)) return false
  const projected = structuredClone(value) as Record<string, unknown>
  projected.protocolVersion = 2
  return acceptsJobEvent(projected, binding)
}

/** Owner-internal data-only capture, not an arbitrary-host-object sandbox.
 * Inputs must come from bounded decoding or the trusted producer adapter.
 * Descriptor reflection cannot absolutely identify hostile same-process Proxies.
 */
export function sourceTableMaterial(
  table: unknown,
  options: unknown,
  implementation: unknown,
  expectedSourceHash: string,
  maxEncodedBytes: number,
): Uint8Array {
  try {
    return captureSourceTable(table, options, implementation, expectedSourceHash, maxEncodedBytes)
  } catch {
    return fail()
  }
}

function captureSourceTable(
  table: unknown,
  options: unknown,
  implementation: unknown,
  expectedSourceHash: string,
  maxEncodedBytes: number,
): Uint8Array {
  if (
    !Number.isSafeInteger(maxEncodedBytes) ||
    maxEncodedBytes < 1 ||
    !validateV2('hash', expectedSourceHash)
  )
    return fail()
  const ownShape = (value: object, names: string[]) => {
    // Stop oversized enumerable records before allocating an own-key list.
    // The owner data-only precondition excludes giant hidden/symbol host trees.
    let count = 0
    for (const key in value) {
      if (!Object.hasOwn(value, key) || ++count > names.length || !names.includes(key))
        return fail()
    }
    const keys = Reflect.ownKeys(value)
    if (keys.length !== names.length) return fail()
    if (keys.some((key) => typeof key !== 'string' || !names.includes(key))) return fail()
  }
  const record = (value: unknown, names: string[]): Record<string, unknown> => {
    if (
      !value ||
      typeof value !== 'object' ||
      Array.isArray(value) ||
      ![Object.prototype, null].includes(Object.getPrototypeOf(value))
    )
      return fail()
    ownShape(value, names)
    const captured: Record<string, unknown> = Object.create(null)
    for (const key of names) {
      const descriptor = Object.getOwnPropertyDescriptor(value, key)
      if (!descriptor || !('value' in descriptor) || !descriptor.enumerable) return fail()
      captured[key] = descriptor.value
    }
    return captured
  }
  const array = (value: unknown, maximum: number): { length: number; at(i: number): unknown } => {
    if (!Array.isArray(value) || Object.getPrototypeOf(value) !== Array.prototype) return fail()
    const descriptor = Object.getOwnPropertyDescriptor(value, 'length')
    const length = descriptor?.value as unknown
    if (
      typeof length !== 'number' ||
      !Number.isSafeInteger(length) ||
      length > maximum ||
      length > maxEncodedBytes
    )
      return fail()
    let count = 0
    for (const key in value) {
      const index = Number(key)
      if (
        !Object.hasOwn(value, key) ||
        ++count > length ||
        !Number.isSafeInteger(index) ||
        index < 0 ||
        index >= length ||
        String(index) !== key
      )
        return fail()
    }
    if (count !== length) return fail()
    // The data-only tree's key allocation is bounded by both the domain count
    // and the encoded-byte lower bound above, not an unbounded descriptor clone.
    if (Reflect.ownKeys(value).length !== length + 1) return fail()
    return {
      length,
      at(i) {
        const item = Object.getOwnPropertyDescriptor(value, String(i))
        if (!item || !('value' in item) || !item.enumerable) return fail()
        return item.value
      },
    }
  }
  const t = record(table, ['source_hash', 'sheet', 'fields', 'rows'])
  const o = record(options, ['format', 'encoding', 'sheet'])
  const impl = record(implementation, [
    'executionSemanticsVersion',
    'engineVersion',
    'dependencyLockHash',
  ])
  if (
    t.source_hash !== expectedSourceHash ||
    typeof t.sheet !== 'string' ||
    (o.format === 'csv'
      ? !['utf-8', 'utf-8-sig', 'gb18030', 'big5', 'utf-16'].includes(o.encoding as string) ||
        o.sheet !== null ||
        t.sheet !== 'CSV'
      : o.format !== 'xlsx' || o.encoding !== null || !t.sheet || o.sheet !== t.sheet) ||
    Object.values(impl).some((value) => typeof value !== 'string') ||
    !validateV2('implementation', impl)
  )
    return fail()
  const fields = array(t.fields, 256)
  const rows = array(t.rows, 50000)
  if (!fields.length) return fail()
  const chunks: Array<{ text: string; bytes: number }> = []
  let total = 0
  const reserve = (bytes: number) => {
    if (bytes > maxEncodedBytes - total) return fail()
    total += bytes
  }
  const token = (text: string) => {
    reserve(text.length)
    chunks.push({ text, bytes: text.length })
  }
  const whitespace = (cp: number) =>
    (cp >= 9 && cp <= 13) ||
    (cp >= 28 && cp <= 32) ||
    [0x85, 0xa0, 0x1680, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000].includes(cp) ||
    (cp >= 0x2000 && cp <= 0x200a)
  const string = (value: unknown, maximum?: number, field = false, noNul = false) => {
    if (typeof value !== 'string') return fail()
    let bytes = 2
    let count = 0
    let blank = true
    if (bytes > maxEncodedBytes - total) return fail()
    for (let i = 0; i < value.length; i++) {
      let cp = value.charCodeAt(i)
      if (cp >= 0xd800 && cp <= 0xdbff) {
        const low = value.charCodeAt(++i)
        if (!(low >= 0xdc00 && low <= 0xdfff)) return fail()
        cp = 0x10000 + ((cp - 0xd800) << 10) + low - 0xdc00
      } else if (cp >= 0xdc00 && cp <= 0xdfff) return fail()
      if (noNul && cp === 0) return fail()
      if (!whitespace(cp)) blank = false
      if (++count > (maximum ?? Number.MAX_SAFE_INTEGER)) return fail()
      bytes +=
        cp === 34 || cp === 92 || [8, 9, 10, 12, 13].includes(cp)
          ? 2
          : cp < 32
            ? 6
            : cp < 128
              ? 1
              : cp < 2048
                ? 2
                : cp < 65536
                  ? 3
                  : 4
      if (bytes > maxEncodedBytes - total) return fail()
    }
    if (field && (!count || blank)) return fail()
    reserve(bytes)
    // Immutable captured primitive only, after exact charging. No caller object
    // or toJSON is passed to the scalar stringifier or saved for later encoding.
    chunks.push({ text: JSON.stringify(value), bytes })
  }
  token('[')
  string('ontolearn.source-table')
  token(',1,')
  string(t.source_hash)
  token(',[')
  string(o.format)
  token(',')
  if (o.encoding === null) token('null')
  else string(o.encoding)
  token(',')
  if (o.sheet === null) token('null')
  else string(o.sheet)
  token('],[')
  for (const [i, key] of [
    'executionSemanticsVersion',
    'engineVersion',
    'dependencyLockHash',
  ].entries()) {
    if (i) token(',')
    string(impl[key])
  }
  token('],')
  string(t.sheet)
  token(',[')
  const seen = new Set<string>()
  for (let i = 0; i < fields.length; i++) {
    const field = fields.at(i)
    if (i) token(',')
    string(field, 32768, true, true)
    if (seen.has(field as string)) return fail()
    seen.add(field as string)
  }
  token('],[')
  let previous = 1
  const kinds = new Set(['string', 'empty', 'boolean', 'datetime', 'date', 'number'])
  for (let i = 0; i < rows.length; i++) {
    const row = record(rows.at(i), ['number', 'cells'])
    const number = row.number
    if (
      typeof number !== 'number' ||
      !Number.isSafeInteger(number) ||
      number <= previous ||
      number > 50001
    )
      return fail()
    previous = number
    const cells = array(row.cells, 256)
    if (cells.length !== fields.length) return fail()
    if (i) token(',')
    token(`[${number},[`)
    for (let j = 0; j < cells.length; j++) {
      const cell = record(cells.at(j), ['text', 'kind'])
      if (
        !kinds.has(cell.kind as string) ||
        (o.format === 'csv' && cell.kind !== 'string') ||
        (cell.kind === 'empty' && cell.text !== '') ||
        (cell.kind === 'boolean' && !['true', 'false'].includes(cell.text as string))
      )
        return fail()
      if (j) token(',')
      token('[')
      string(cell.text, 32768, false, true)
      token(',')
      string(cell.kind)
      token(']')
    }
    token(']]')
  }
  token(']]')
  const output = new Uint8Array(total)
  const encoder = new TextEncoder()
  let offset = 0
  for (const chunk of chunks) {
    const result = encoder.encodeInto(chunk.text, output.subarray(offset))
    if (result.written !== chunk.bytes || result.read !== chunk.text.length) return fail()
    offset += chunk.bytes
  }
  if (offset !== total) return fail()
  return output
}

export async function sourceTableDigest(
  ...args: Parameters<typeof sourceTableMaterial>
): Promise<{ sha256: string; encodedBytes: number }> {
  const bytes = sourceTableMaterial(...args)
  const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes.buffer as ArrayBuffer)
  return {
    sha256: Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, '0')).join(''),
    encodedBytes: bytes.length,
  }
}

export interface EventBinding {
  engineSessionId: string
  projectId: string
  jobId: string
  subscriptionId: string
  lastSeq: number
  stateVersion: number
  state: string
}
export function acceptsJobEvent(value: unknown, binding: EventBinding): boolean {
  if (
    !binding ||
    typeof binding !== 'object' ||
    Object.keys(binding).sort().join(',') !==
      'engineSessionId,jobId,lastSeq,projectId,state,stateVersion,subscriptionId' ||
    !['engineSessionId', 'projectId', 'jobId', 'subscriptionId'].every((key) =>
      validateV2('id', binding[key as keyof EventBinding]),
    ) ||
    !Number.isSafeInteger(binding.lastSeq) ||
    binding.lastSeq < 0 ||
    !Number.isSafeInteger(binding.stateVersion) ||
    binding.stateVersion < 1 ||
    !['queued', 'running', 'cancelling', 'succeeded', 'failed', 'cancelled'].includes(binding.state)
  )
    return false
  if (!validateV2('notification', value)) return false
  const v = value as Record<string, unknown>
  if (v.event === 'session.status') return false
  const data = v.data as Record<string, unknown>
  if (!(
    ['engineSessionId', 'projectId', 'jobId', 'subscriptionId'].every(
      (key) => v[key] === binding[key as keyof EventBinding],
    ) &&
    Number(v.seq) === binding.lastSeq + 1 &&
    !['succeeded', 'failed', 'cancelled'].includes(binding.state)
  ))
    return false
  if (v.event === 'job.progress') return Number(data.stateVersion) === binding.stateVersion
  if (Number(data.stateVersion) !== binding.stateVersion + 1) return false
  return (
    data.state === binding.state ||
    permitsTransition(
      binding.state,
      String(data.state),
      binding.stateVersion,
      Number(data.stateVersion),
      false,
    )
  )
}
export function cursorMatches(record: unknown, request: unknown, nowMs: number): boolean {
  if (!validateV2('cursorRecord', record) || !validateV2('params_result.page', request))
    return false
  const c = record as {
    token: string
    binding: Record<string, unknown>
    pageSize: number
    expiresAtMs: number
  }
  const p = request as { cursor: string; binding: Record<string, unknown>; pageSize: number }
  return (
    c.token === p.cursor &&
    c.pageSize === p.pageSize &&
    c.expiresAtMs > nowMs &&
    Object.keys(c.binding).every((key) => c.binding[key] === p.binding[key])
  )
}

// The resolver receives a trusted projection of the immutable S1 snapshot, never client claims.
export interface DefinitionIdentity {
  family: string
  id: string
  version: number
  references: string[]
}
export interface DependencyPlan {
  keys: string[]
  sets: Record<string, string[]>
}

/** Structural association only; the private transport supplies its issued choice/lease binding. */
export interface OrdinaryResponseBinding {
  projectId: string
  project?: Record<string, unknown>
}
export function matchesOrdinaryResponse(
  request: unknown,
  response: unknown,
  binding?: unknown,
): boolean {
  if (!validateV2('request', request) || !validateV2('response', response)) return false
  const q = request as Record<string, unknown>,
    r = response as Record<string, unknown>
  if (
    q.method !== 'ordinary.library' ||
    r.method !== q.method ||
    r.id !== q.id ||
    r.engineSessionId !== q.engineSessionId
  )
    return false
  if (!r.ok) return true
  const p = q.params as Record<string, unknown>,
    d = r.result as Record<string, unknown>
  if (p.op !== d.op || p.ownerId !== d.ownerId) return false
  if (p.op === 'choices')
    return (
      p.menuSeq === d.menuSeq &&
      new Set((d.choices as Array<{ choiceRef: string }>).map((c) => c.choiceRef)).size ===
        (d.choices as unknown[]).length &&
      new Set((d.choices as Array<{ projectId: string }>).map((c) => c.projectId)).size ===
        (d.choices as unknown[]).length
    )
  if (p.actionId !== d.actionId || p.actionSeq !== d.actionSeq) return false
  if (p.op === 'release') return true
  if (p.op === 'commit' && p.leaseRef !== d.leaseRef) return false
  if (!binding || typeof binding !== 'object' || Array.isArray(binding)) return false
  const project = d.project as Record<string, unknown>
  const issued = binding as Record<string, unknown>
  if (project.projectId !== issued.projectId) return false
  const provided = Object.prototype.hasOwnProperty.call(issued, 'project')
  if (provided && !validateV2('result_project.get', issued.project)) return false
  if (p.op === 'commit' && !provided) return false
  if (!provided) return true
  const expected = issued.project as Record<string, unknown>
  if (
    ['projectId', 'projectRevision', 'inputSnapshotId', 'formatVersion'].some(
      (key) => expected[key] !== project[key],
    )
  )
    return false
  const vector = project.dependencyVector as Record<string, number>
  const expectedVector = expected.dependencyVector as Record<string, number>
  const keys = Object.keys(expectedVector)
  return (
    keys.length === Object.keys(vector).length &&
    keys.every(
      (key) =>
        Object.prototype.hasOwnProperty.call(vector, key) && expectedVector[key] === vector[key],
    )
  )
}

export function matchesResponse(request: unknown, response: unknown): boolean {
  if (!validateV2('request', request) || !validateV2('response', response)) return false
  const q = request as Record<string, unknown>,
    r = response as Record<string, unknown>
  if (q.id !== r.id || q.method !== r.method) return false
  if (q.method !== 'hello' && q.engineSessionId !== r.engineSessionId) return false
  if (q.method === 'ordinary.library') return matchesOrdinaryResponse(request, response)
  if (String(q.method).startsWith('query.')) return matchesQueryConsumerResponse(request, response)
  if (!r.ok) return true
  const p = q.params as Record<string, unknown>,
    data = r.result as Record<string, unknown> | null
  if (q.method === 'hello') {
    return (
      (p.supportedVersions as number[]).includes(2) &&
      (data!.capabilities as string[]).every(
        (c) =>
          (registry.v2Runtime as string[]).includes(c) || c === registry.ordinaryLibrary.method,
      )
    )
  }
  if (!data) return true
  if (p.projectId && data.projectId && p.projectId !== data.projectId) return false
  if (p.jobId && data.jobId && p.jobId !== data.jobId) return false
  if (p.resultId && data.resultId && p.resultId !== data.resultId) return false
  if (q.method === 'operation.get' && p.operationId !== data.operationId) return false
  if (q.method === 'job.unsubscribe' && p.subscriptionId !== data.subscriptionId) return false
  if (q.method === 'job.create') {
    const input = p.input as Record<string, unknown>
    const actual = data.input as Record<string, unknown>
    if (
      p.confirmationRef !== data.confirmationRef ||
      Object.keys(input).some((k) =>
        Array.isArray(input[k])
          ? JSON.stringify(input[k]) !== JSON.stringify(actual[k])
          : input[k] !== actual[k],
      )
    )
      return false
    if (
      p.operationId !== data.operationId ||
      p.capability !== data.capability ||
      ['inputSnapshotId', 'scope', 'parametersHash'].some((k) => input[k] !== data[k])
    )
      return false
  }
  if (q.method === 'result.current') {
    if (
      data.state !== 'current' ||
      ['kind', 'definitionId', 'scope', 'parametersHash'].some((k) => p[k] !== data[k])
    )
      return false
    const expected = p.implementation as Record<string, unknown>,
      actual = data.implementation as Record<string, unknown>
    if (Object.keys(expected).some((k) => expected[k] !== actual[k])) return false
  }
  if (q.method === 'session.ping' && p.nonce !== data.nonce) return false
  if (q.method === 'result.page')
    return (
      (data.rows as unknown[]).length <= Number(p.pageSize) &&
      Object.keys(p.binding as object).every(
        (key) =>
          (p.binding as Record<string, unknown>)[key] ===
          (data.binding as Record<string, unknown>)[key],
      )
    )
  if (q.method === 'job.list') {
    const b = data.binding as Record<string, unknown>
    if ((data.jobs as unknown[]).length > Number(p.pageSize)) return false
    if (
      b.projectId !== p.projectId ||
      b.filter !== p.filter ||
      (p.listSnapshotId && p.listSnapshotId !== b.listSnapshotId)
    )
      return false
    if ((data.jobs as Array<Record<string, unknown>>).some((job) => job.projectId !== p.projectId))
      return false
  }
  return true
}

export function jobListCursorMatches(record: unknown, request: unknown, nowMs: number): boolean {
  if (!validateV2('jobListCursorRecord', record) || !validateV2('params_job.list', request))
    return false
  const c = record as {
    token: string
    binding: Record<string, unknown>
    pageSize: number
    expiresAtMs: number
  }
  const p = request as {
    cursor: string
    projectId: string
    listSnapshotId: string
    filter: string
    pageSize: number
  }
  return (
    c.token === p.cursor &&
    c.binding.projectId === p.projectId &&
    c.binding.listSnapshotId === p.listSnapshotId &&
    c.binding.filter === p.filter &&
    c.pageSize === p.pageSize &&
    c.expiresAtMs > nowMs
  )
}

/** Pure metadata association check; callers must fetch these bindings from the trusted store. */
export function validationProjectionMatchesResources(
  projection: unknown,
  resources: unknown,
): boolean {
  if (
    !validateV2('validationProjection', projection) ||
    !validateV2('validationResources', resources)
  )
    return false
  const p = projection as Record<string, unknown>
  const rows = resources as Array<Record<string, unknown>>
  const derived = p.derived as Record<string, unknown> | null
  const expected: Record<string, unknown> = {
    assertedFacts: p.assertedFactsRef,
    ontologyAxioms: p.ontologyAxiomsRef,
    constraints: p.constraintsRef,
  }
  if (derived) {
    expected.derivedFacts = derived.factsRef
    expected.derivedAxioms = derived.axiomsRef
  }
  if (rows.length !== Object.keys(expected).length) return false
  if (
    derived &&
    new Set(
      rows
        .filter((row) => row.role === 'derivedFacts' || row.role === 'derivedAxioms')
        .map((row) => row.resultState),
    ).size !== 1
  )
    return false
  return Object.entries(expected).every(([role, ref]) => {
    const matches = rows.filter((row) => row.role === role)
    if (matches.length !== 1) return false
    const row = matches[0]
    if (
      role === 'constraints'
        ? row.constraintDefinitionId !== p.constraintDefinitionId
        : row.constraintDefinitionId !== null
    )
      return false
    if (
      row.ref !== ref ||
      row.projectId !== p.projectId ||
      row.inputSnapshotId !== p.inputSnapshotId
    )
      return false
    if (role === 'derivedFacts' || role === 'derivedAxioms') {
      if (
        !derived ||
        row.resultId !== derived.resultId ||
        row.resultKind !== 'reasoning' ||
        row.payloadStatus !== 'available' ||
        !['current', 'stale', 'historical'].includes(String(row.resultState))
      )
        return false
      if (p.inputSelection === 'current' && row.resultState !== 'current') return false
      const actual = row.implementation as Record<string, unknown> | null
      const expectedImpl = derived.implementation as Record<string, unknown>
      return !!actual && Object.keys(expectedImpl).every((key) => actual[key] === expectedImpl[key])
    }
    return (
      row.resultId === null &&
      row.implementation === null &&
      row.resultKind === null &&
      row.payloadStatus === null &&
      row.resultState === null
    )
  })
}

/** Only the query draft is D1 UTF-16; presentation limits remain scalar L2. */
function queryConsumerSemantics(name: string, value: unknown): boolean {
  const v = value as Record<string, unknown>
  if (['request', 'response', 'envelope', 'request3', 'response3', 'envelope3'].includes(name)) {
    if (v.kind === 'request' && String(v.method).startsWith('query.'))
      return queryConsumerSemantics('params_' + v.method, v.params)
    if (v.kind === 'response' && v.ok && String(v.method).startsWith('query.'))
      return queryConsumerSemantics('result_' + v.method, v.result)
    return true
  }
  if (name === 'params_query.execution.prepare')
    return queryConsumerSemantics('query.consumer.draft', v.visibleDraft)
  if (name === 'result_query.definition.load' || name === 'query.consumer.definitionLoad')
    return v.kind !== 'managed' || queryConsumerSemantics('query.consumer.draft', v.draft)
  if (name === 'query.consumer.descriptor') {
    for (const [key, maximum] of Object.entries({
      name: 128,
      description: 4096,
      capabilityQuestion: 4096,
    }))
      if (typeof v[key] !== 'string' || (v[key] as string).length > maximum) return false
    const nameValue = v.name as string
    return (
      !!nameValue &&
      !queryEdgeSpace.includes(nameValue[0]) &&
      !queryEdgeSpace.includes(nameValue.at(-1)!)
    )
  }
  if (name !== 'query.consumer.draft') return true
  for (const [key, maximum] of Object.entries({
    name: 128,
    description: 4096,
    sparql: 65536,
    capabilityQuestion: 4096,
  }))
    if (typeof v[key] !== 'string' || (v[key] as string).length > maximum) return false
  for (const key of ['name', 'sparql']) {
    const text = v[key] as string
    let start = 0,
      end = text.length
    while (start < end && queryEdgeSpace.includes(text[start])) start++
    while (end > start && queryEdgeSpace.includes(text[end - 1])) end--
    if (start === end) return false
  }
  return true
}

/** Query consumer values share scalar L2; draft D1 alone retains its UTF-16 policy. */
const queryEdgeSpace =
  '\t\n\v\f\r\u001c\u001d\u001e\u001f \u0085\u00a0\u1680' +
  '\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a' +
  '\u2028\u2029\u202f\u205f\u3000\ufeff'
export function normalizeQueryDraft(value: unknown): Record<string, unknown> | null {
  if (!validateV2('query.consumer.draft', value)) return null
  const draft = { ...(value as Record<string, unknown>) }
  for (const [key, maximum] of Object.entries({
    name: 128,
    description: 4096,
    sparql: 65536,
    capabilityQuestion: 4096,
  }))
    if ((draft[key] as string).length > maximum) return null
  for (const key of ['name', 'sparql']) {
    const text = draft[key] as string
    let start = 0,
      end = text.length
    while (start < end && queryEdgeSpace.includes(text[start])) start++
    while (end > start && queryEdgeSpace.includes(text[end - 1])) end--
    draft[key] = text.slice(start, end)
    if (!draft[key]) return null
  }
  return draft
}
function queryEqual(left: unknown, right: unknown): boolean {
  if (left === right) return true
  if (Array.isArray(left) && Array.isArray(right))
    return left.length === right.length && left.every((v, i) => queryEqual(v, right[i]))
  if (!left || !right || typeof left !== 'object' || typeof right !== 'object') return false
  const a = left as Record<string, unknown>,
    b = right as Record<string, unknown>
  return (
    Object.keys(a).length === Object.keys(b).length &&
    Object.keys(a).every((k) => Object.hasOwn(b, k) && queryEqual(a[k], b[k]))
  )
}
/** Extra facts come only from an actual issued descriptor/load, never renderer claims. */
export function matchesQueryConsumerResponse(
  request: unknown,
  response: unknown,
  expected?: Record<string, unknown>,
): boolean {
  if (!validateV2('request', request) || !validateV2('response', response)) return false
  const q = request as Record<string, unknown>,
    r = response as Record<string, unknown>
  if (q.id !== r.id || q.method !== r.method || q.engineSessionId !== r.engineSessionId)
    return false
  if (!r.ok) return true
  return queryConsumerResultMatches(
    q.method as string,
    q.params as Record<string, unknown>,
    r.result,
    expected,
  )
}
export function queryConsumerResultMatches(
  method: string,
  p: Record<string, unknown>,
  value: unknown,
  expected?: Record<string, unknown>,
): boolean {
  if (!validateV2('params_' + method, p) || !validateV2('result_' + method, value)) return false
  const v = value as Record<string, unknown>
  if (method === 'query.definition.load') {
    const selection = p.selection as Record<string, unknown>
    if (
      v.projectId !== p.projectId ||
      v.definitionId !== p.definitionId ||
      (selection.kind === 'historical' && v.inputSnapshotId !== selection.snapshotId)
    )
      return false
    return !expected || Object.keys(expected).every((k) => queryEqual(expected[k], v[k]))
  }
  if (method === 'query.execution.prepare') {
    const input = v.input as Record<string, unknown>,
      binding = p.definitionBinding as Record<string, unknown>
    if (
      v.projectId !== p.projectId ||
      v.operationId !== p.operationId ||
      !queryEqual(v.definitionBinding, binding) ||
      input.definitionId !== binding.definitionId ||
      input.scope !== 'asserted' ||
      !Array.isArray(input.derivedResultIds) ||
      input.derivedResultIds.length !== 0 ||
      input.preparedPlanRef !== null
    )
      return false
    const selection = p.selection as Record<string, unknown>
    if (selection.kind === 'historical' && input.inputSnapshotId !== selection.snapshotId)
      return false
    return !expected || Object.keys(expected).every((k) => queryEqual(expected[k], v[k]))
  }
  if (method === 'query.result.describe') {
    const identity = v.identity as Record<string, unknown>,
      metadata = v.metadata as Record<string, unknown>
    if (
      identity.projectId !== p.projectId ||
      identity.resultId !== p.resultId ||
      metadata.kind !== 'query'
    )
      return false
    for (const key of [
      'projectId',
      'resultId',
      'jobId',
      'inputSnapshotId',
      'definitionId',
      'parametersHash',
      'scope',
      'implementation',
      'inputProjectRevision',
    ])
      if (!queryEqual(identity[key], metadata[key])) return false
    const text = v.executedText as Record<string, unknown>,
      query = v.query as Record<string, unknown>
    if (
      Number(text.utf8Bytes) < Number(text.unicodeScalars) ||
      Number(text.utf8Bytes) > 4 * Number(text.unicodeScalars) ||
      Number(text.utf16Units) < Number(text.unicodeScalars) ||
      Number(text.utf16Units) > 2 * Number(text.unicodeScalars)
    )
      return false
    if (query.kind === 'SELECT') {
      const columns = query.columns as Array<Record<string, unknown>>
      if (
        columns.some((c, i) => c.index !== i) ||
        new Set(columns.map((c) => c.name)).size !== columns.length
      )
        return false
    }
    return !expected || Object.keys(expected).every((k) => queryEqual(expected[k], v[k]))
  }
  if (method === 'query.result.textPage' || method === 'query.result.rowsPage') {
    if (!queryEqual(p.binding, v.identity)) return false
    if (method.endsWith('textPage')) {
      const bytes = new TextEncoder().encode(v.text as string).byteLength
      if (v.utf8Length !== bytes || bytes > Number(p.maxUtf8Bytes)) return false
      if (
        expected &&
        ((expected.nextUtf8Byte !== undefined && v.startUtf8Byte !== expected.nextUtf8Byte) ||
          Number(v.startUtf8Byte) + bytes >
            Number((expected.executedText as Record<string, unknown>).utf8Bytes))
      )
        return false
      if (
        expected &&
        v.nextCursor === null &&
        Number(v.startUtf8Byte) + bytes !==
          Number((expected.executedText as Record<string, unknown>).utf8Bytes)
      )
        return false
    } else {
      const rows = v.rows as Array<Record<string, unknown>>
      if (
        rows.length > Number(p.pageSize) ||
        rows.some((row, i) => i > 0 && Number(row.index) !== Number(rows[i - 1].index) + 1)
      )
        return false
      if (expected) {
        const query = expected.query as Record<string, unknown>
        if (query.kind !== 'SELECT') return false
        const width = (query.columns as unknown[]).length,
          start =
            expected.nextIndex === undefined
              ? Number(rows[0]?.index ?? query.rowCount)
              : Number(expected.nextIndex)
        if (
          rows.some(
            (row, i) => row.index !== start + i || (row.cells as unknown[]).length !== width,
          ) ||
          start + rows.length > Number(query.rowCount)
        )
          return false
        if (v.nextCursor === null && start + rows.length !== Number(query.rowCount)) return false
      }
    }
    return utf8(v) <= 131072
  }
  return false
}
