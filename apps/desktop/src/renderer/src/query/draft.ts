import { z } from 'zod'

// Private editor state. This is not an IPC schema or an execution permission.
const scalarText = z.string().refine((s) => !/[\uD800-\uDFFF]/u.test(s), '无效 Unicode')
export const iriSchema = scalarText
  .min(1)
  .max(2048)
  .refine(
    (s) =>
      /^[A-Za-z][A-Za-z0-9+.-]*:/.test(s) &&
      !/[\s<>"{}|^`\\]/u.test(s) &&
      !Array.from(s).some((c) => c.charCodeAt(0) <= 32 || c.charCodeAt(0) === 127),
    '需要完整 IRI；不能包含空白或 SPARQL 语法字符',
  )
const literalSchema = z
  .object({
    kind: z.literal('literal'),
    value: scalarText.max(8192),
    language: z
      .string()
      .regex(/^[A-Za-z]+(?:-[A-Za-z0-9]+)*$/)
      .max(64)
      .nullable(),
    datatype: iriSchema.nullable(),
  })
  .strict()
  .refine((v) => !(v.language && v.datatype), '语言和数据类型不能同时指定')
export const termSchema = z.union([
  z.object({ kind: z.literal('iri'), value: iriSchema }).strict(),
  literalSchema,
])
export type Term = z.infer<typeof termSchema>
export const scopeSchema = z.enum(['asserted', 'asserted+derived'])
export type QueryScope = z.infer<typeof scopeSchema>
const fieldSchema = z.object({ predicate: iriSchema, label: scalarText.min(1).max(128) }).strict()
const conditionSchema = z.discriminatedUnion('operator', [
  z
    .object({
      predicate: iriSchema,
      operator: z.enum(['eq', 'ne', 'lt', 'le', 'gt', 'ge']),
      value: termSchema,
    })
    .strict(),
  z.object({ predicate: iriSchema, operator: z.literal('exists') }).strict(),
  z.object({ predicate: iriSchema, operator: z.literal('not-exists') }).strict(),
])
export const visualSchema = z
  .object({
    classIri: iriSchema,
    fields: z.array(fieldSchema).max(16),
    conditions: z.array(conditionSchema).max(32),
  })
  .strict()
export type VisualQuery = z.infer<typeof visualSchema>
// Raw UTF-16 limit, then the fixed union of Python/ECMAScript edge whitespace.
const draftEdgeSpace =
  '\t\n\v\f\r\u001c\u001d\u001e\u001f \u0085\u00a0\u1680' +
  '\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a' +
  '\u2028\u2029\u202f\u205f\u3000\ufeff'
const draftText = (maximum: number) =>
  scalarText
    .refine((s) => s.length <= maximum, '超过长度上限')
    .transform((s) => {
      let start = 0
      let end = s.length
      while (start < end && draftEdgeSpace.includes(s[start])) start++
      while (end > start && draftEdgeSpace.includes(s[end - 1])) end--
      return s.slice(start, end)
    })
    .refine((s) => s.length > 0, '不能为空')
export const draftSchema = z
  .object({
    name: draftText(128),
    description: scalarText.max(4096),
    sparql: draftText(65536),
    scope: scopeSchema,
    capabilityQuestion: scalarText.max(4096),
    source: z.enum(['template', 'visual', 'editor', 'model']),
  })
  .strict()
export type QueryDraft = z.infer<typeof draftSchema>

export function serializeTerm(input: Term): string {
  const term = termSchema.parse(input)
  if (term.kind === 'iri') return `<${term.value}>`
  // JSON short-string escapes are also SPARQL ECHAR/UCHAR escapes; escape the
  // remaining controls, and never interpolate a raw literal as query syntax.
  const quoted = JSON.stringify(term.value).replace(/\u007f/g, '\\u007F')
  return (
    quoted +
    (term.language
      ? `@${term.language.toLowerCase()}`
      : term.datatype
        ? `^^<${term.datatype}>`
        : '')
  )
}
export function compileVisual(input: VisualQuery): string {
  const query = visualSchema.parse(input)
  const select = ['?item', ...query.fields.map((_, i) => `?field${i}`)]
  const lines = [`  ?item a <${query.classIri}> .`]
  query.conditions.forEach((condition, i) => {
    const triple = `?item <${condition.predicate}> ?condition${i} .`
    if (condition.operator === 'exists' || condition.operator === 'not-exists') {
      lines.push(
        `  FILTER ${condition.operator === 'not-exists' ? 'NOT ' : ''}EXISTS { ${triple} }`,
      )
    } else {
      const operators = { eq: '=', ne: '!=', lt: '<', le: '<=', gt: '>', ge: '>=' }
      lines.push(
        `  ${triple}`,
        `  FILTER (?condition${i} ${operators[condition.operator]} ${serializeTerm(condition.value)})`,
      )
    }
  })
  query.fields.forEach((field, i) =>
    lines.push(`  OPTIONAL { ?item <${field.predicate}> ?field${i} . }`),
  )
  return `SELECT DISTINCT ${select.join(' ')} WHERE {\n${lines.join('\n')}\n}\nORDER BY ${select.join(' ')}`
}

export function alarmTemplate(vocabulary: {
  alarmClass: string
  severity: string
  status: string
}): VisualQuery {
  return visualSchema.parse({
    classIri: vocabulary.alarmClass,
    fields: [
      { predicate: vocabulary.severity, label: '告警等级' },
      { predicate: vocabulary.status, label: '告警状态' },
    ],
    conditions: [
      {
        predicate: vocabulary.severity,
        operator: 'eq',
        value: { kind: 'literal', value: 'High', language: null, datatype: null },
      },
      {
        predicate: vocabulary.status,
        operator: 'eq',
        value: { kind: 'literal', value: 'Open', language: null, datatype: null },
      },
    ],
  })
}

/**
 * Resolve the alarm vocabulary from the *actually read* ontology classes and
 * predicates. Nothing is invented: when the current project does not expose a
 * recognisable alarm class together with a severity and a status attribute,
 * no template is offered at all.
 *
 * A slot is only accepted when exactly one candidate matches; an ambiguous
 * slot never falls back to "the first regular expression hit".
 */
export function alarmVocabulary(
  classes: readonly string[],
  predicates: readonly string[],
): { alarmClass: string; severity: string; status: string } | undefined {
  const alarmClasses = classes.filter((iri) => /alarm|alert|告警/i.test(iri))
  if (alarmClasses.length !== 1) return undefined
  const severity = predicates.filter((iri) => /severity|level|grade|等级|严重/i.test(iri))
  const status = predicates.filter((iri) => /status|state|状态/i.test(iri))
  if (severity.length !== 1 || status.length !== 1) return undefined
  if (severity[0] === status[0]) return undefined
  return { alarmClass: alarmClasses[0]!, severity: severity[0]!, status: status[0]! }
}

/* --------------------------------------------------------------------------
 * Strict alarm vocabulary resolution (B10).
 *
 * The template must only ever bind attributes that really belong to the alarm
 * class. A predicate that only occurs on an unrelated entity, or that only
 * survives as a tombstone, must never be attached to the alarm template.
 * ----------------------------------------------------------------------- */

export type LiveFactLike = { subject: string; predicate: string; object: string | null }
export type OntologyTripleLike = { subject: string; predicate: string; object: string }

export type AlarmVocabulary = { alarmClass: string; severity: string; status: string }

export type AlarmVocabularyResolution =
  | { status: 'resolved'; vocabulary: AlarmVocabulary }
  | { status: 'missing'; reason: string }
  | { status: 'ambiguous'; reason: string; candidates: string[] }

export const RDF_TYPE_IRI = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
export const RDFS_DOMAIN_IRI = 'http://www.w3.org/2000/01/rdf-schema#domain'
export const RDFS_SUBCLASS_OF_IRI = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
export const OWL_CLASS_IRI = 'http://www.w3.org/2002/07/owl#Class'
export const RDFS_CLASS_IRI = 'http://www.w3.org/2000/01/rdf-schema#Class'

const ALARM_CLASS_PATTERN = /alarm|alert|告警/i
const SEVERITY_PATTERN = /severity|level|grade|等级|严重/i
const STATUS_PATTERN = /status|state|状态/i

/** Read an IRI out of an N3-ish term (`<iri>`); literals and blanks are not IRIs. */
export function iriTerm(object: string | null | undefined): string | undefined {
  if (typeof object !== 'string') return undefined
  const trimmed = object.trim()
  if (!trimmed.startsWith('<') || !trimmed.endsWith('>') || trimmed.length < 3) return undefined
  return trimmed.slice(1, -1)
}

/** Every ancestor class of `iri` through `rdfs:subClassOf` (the class itself excluded). */
export function ontologyAncestors(
  iri: string,
  parents: ReadonlyMap<string, ReadonlySet<string>>,
): Set<string> {
  const seen = new Set<string>()
  const queue = [...(parents.get(iri) ?? [])]
  while (queue.length) {
    const next = queue.shift()!
    if (seen.has(next) || next === iri) continue
    seen.add(next)
    for (const parent of parents.get(next) ?? []) queue.push(parent)
  }
  return seen
}

/** Every descendant class of `iri` through `rdfs:subClassOf` (the class itself excluded). */
export function ontologyDescendants(
  iri: string,
  children: ReadonlyMap<string, ReadonlySet<string>>,
): Set<string> {
  const seen = new Set<string>()
  const queue = [...(children.get(iri) ?? [])]
  while (queue.length) {
    const next = queue.shift()!
    if (seen.has(next) || next === iri) continue
    seen.add(next)
    for (const child of children.get(next) ?? []) queue.push(child)
  }
  return seen
}

/**
 * Resolve the alarm vocabulary from the really read project state.
 *
 * - Tombstoned facts (`object === null`) never contribute a class or a predicate.
 * - Only predicates that are *really* associated with the alarm class count:
 *   either declared through `rdfs:domain`, or observed on a live instance of
 *   the alarm class (or of one of its subclasses).
 * - A missing or ambiguous slot refuses the template and explains why.
 */
export function resolveAlarmVocabulary(input: {
  liveFacts: readonly LiveFactLike[]
  ontologyTriples: readonly OntologyTripleLike[]
}): AlarmVocabularyResolution {
  const live = input.liveFacts.filter((fact) => fact.object !== null && fact.object !== undefined)
  const instanceTypes = new Map<string, Set<string>>()
  for (const fact of live) {
    if (fact.predicate !== RDF_TYPE_IRI) continue
    const type = iriTerm(fact.object)
    if (!type) continue
    const types = instanceTypes.get(fact.subject) ?? new Set<string>()
    types.add(type)
    instanceTypes.set(fact.subject, types)
  }
  const declaredClasses = new Set<string>()
  const parents = new Map<string, Set<string>>()
  const children = new Map<string, Set<string>>()
  const domainPredicates = new Map<string, Set<string>>()
  for (const triple of input.ontologyTriples) {
    if (triple.predicate === RDF_TYPE_IRI) {
      const type = iriTerm(triple.object)
      if (type === OWL_CLASS_IRI || type === RDFS_CLASS_IRI) declaredClasses.add(triple.subject)
      continue
    }
    const object = iriTerm(triple.object)
    if (!object) continue
    if (triple.predicate === RDFS_SUBCLASS_OF_IRI) {
      const set = parents.get(triple.subject) ?? new Set<string>()
      set.add(object)
      parents.set(triple.subject, set)
      const kids = children.get(object) ?? new Set<string>()
      kids.add(triple.subject)
      children.set(object, kids)
    }
  }
  // `rdfs:domain` points at the *class*; the attribute is the subject.
  for (const triple of input.ontologyTriples) {
    if (triple.predicate !== RDFS_DOMAIN_IRI) continue
    const object = iriTerm(triple.object)
    if (!object) continue
    const set = domainPredicates.get(object) ?? new Set<string>()
    set.add(triple.subject)
    domainPredicates.set(object, set)
  }
  const alarmCandidates = [
    ...new Set([...[...instanceTypes.values()].flatMap((types) => [...types]), ...declaredClasses]),
  ]
    .filter((iri) => ALARM_CLASS_PATTERN.test(iri))
    .sort()
  if (alarmCandidates.length === 0)
    return {
      status: 'missing',
      reason: '当前已读取的本体没有可识别的告警类；不会填入示例词表。',
    }
  if (alarmCandidates.length > 1)
    return {
      status: 'ambiguous',
      reason: `当前已读取的本体存在多个告警类候选（${alarmCandidates.join('、')}）；请先明确唯一告警类。`,
      candidates: alarmCandidates,
    }
  const alarmClass = alarmCandidates[0]!
  const ancestors = ontologyAncestors(alarmClass, parents)
  const descendants = ontologyDescendants(alarmClass, children)
  const associated = new Set<string>()
  for (const iri of [alarmClass, ...ancestors])
    for (const predicate of domainPredicates.get(iri) ?? []) associated.add(predicate)
  for (const [subject, types] of instanceTypes) {
    const isAlarm = types.has(alarmClass) || [...types].some((type) => descendants.has(type))
    if (!isAlarm) continue
    for (const fact of live)
      if (fact.subject === subject && fact.predicate !== RDF_TYPE_IRI)
        associated.add(fact.predicate)
  }
  associated.delete(RDF_TYPE_IRI)
  const severity = [...associated].filter((iri) => SEVERITY_PATTERN.test(iri)).sort()
  const status = [...associated].filter((iri) => STATUS_PATTERN.test(iri)).sort()
  if (severity.length === 0)
    return {
      status: 'missing',
      reason: '当前已读取的本体没有与告警类真实关联的等级属性；不会填入示例词表。',
    }
  if (severity.length > 1)
    return {
      status: 'ambiguous',
      reason: `告警类关联了多个等级属性（${severity.join('、')}）；请先明确唯一等级属性。`,
      candidates: severity,
    }
  if (status.length === 0)
    return {
      status: 'missing',
      reason: '当前已读取的本体没有与告警类真实关联的状态属性；不会填入示例词表。',
    }
  if (status.length > 1)
    return {
      status: 'ambiguous',
      reason: `告警类关联了多个状态属性（${status.join('、')}）；请先明确唯一状态属性。`,
      candidates: status,
    }
  if (severity[0] === status[0])
    return {
      status: 'ambiguous',
      reason: '告警类的等级属性与状态属性解析到同一项；请先明确区分两者。',
      candidates: severity,
    }
  return {
    status: 'resolved',
    vocabulary: { alarmClass, severity: severity[0]!, status: status[0]! },
  }
}

export const emptyDirections = [
  '检查所选数据范围；断言事实不包含尚未推导的事实。',
  '检查过期标识；明确选择当前输入或历史快照后重新执行。',
  '检查筛选值、类型、语言标签和条件；可逐项放宽条件后复查。',
  '检查字段是否有记录，以及映射是否成功提交到当前项目。',
  '空结果表示本次查询未记录匹配项，不能据此证明业务事实不存在。',
] as const

// Saved record identity is private UI state; the owning project service still
// validates revision, authority and the formal ChangeSet at commit time.
export const definitionIdSchema = z.string().regex(/^[A-Za-z0-9_.-]{1,128}$/)
export const savedQuerySchema = z
  .object({
    definitionId: definitionIdSchema,
    draft: draftSchema,
  })
  .strict()
export type SavedQuery = z.infer<typeof savedQuerySchema>
