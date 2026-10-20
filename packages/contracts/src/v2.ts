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
  if (name === 'params_job.create' || name === 'params_job.list')
    return semantic({ kind: 'request', method: name.slice(7), params: value })
  return true
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

export function matchesResponse(request: unknown, response: unknown): boolean {
  if (!validateV2('request', request) || !validateV2('response', response)) return false
  const q = request as Record<string, unknown>,
    r = response as Record<string, unknown>
  if (q.id !== r.id || q.method !== r.method) return false
  if (q.method !== 'hello' && q.engineSessionId !== r.engineSessionId) return false
  if (!r.ok) return true
  const p = q.params as Record<string, unknown>,
    data = r.result as Record<string, unknown> | null
  if (q.method === 'hello') {
    return (
      (p.supportedVersions as number[]).includes(2) &&
      (data!.capabilities as string[]).every((c) => (registry.v2Runtime as string[]).includes(c))
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
