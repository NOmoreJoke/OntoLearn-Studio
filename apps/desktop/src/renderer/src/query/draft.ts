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
