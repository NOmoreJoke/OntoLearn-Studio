import { z } from 'zod'

const text = z.string().trim().min(1).max(500)
const identifier = z.string().trim().min(1).max(200)
export const valueSchema = z.discriminatedUnion('kind', [
  z.object({ kind: z.literal('string'), value: z.string().max(2000) }).strict(),
  z.object({ kind: z.literal('number'), value: z.number().finite() }).strict(),
  z.object({ kind: z.literal('boolean'), value: z.boolean() }).strict(),
  z.object({ kind: z.literal('iri'), value: identifier }).strict(),
])
export type Value = z.infer<typeof valueSchema>
const conditionSchema = z.discriminatedUnion('kind', [
  z
    .object({
      kind: z.literal('equals'),
      object: identifier,
      property: identifier,
      value: valueSchema,
    })
    .strict(),
  z.object({ kind: z.literal('exists'), object: identifier, property: identifier }).strict(),
  z.object({ kind: z.literal('type'), object: identifier, classId: identifier }).strict(),
])
export type Condition = z.infer<typeof conditionSchema>
export const actionSchema = z.discriminatedUnion('kind', [
  z.object({ kind: z.literal('create'), object: identifier, classId: identifier }).strict(),
  z
    .object({
      kind: z.literal('update'),
      object: identifier,
      property: identifier,
      value: valueSchema,
    })
    .strict(),
  z
    .object({
      kind: z.literal('relate'),
      object: identifier,
      property: identifier,
      target: identifier,
    })
    .strict(),
  z.object({ kind: z.literal('notify'), message: text }).strict(),
])
export type Action = z.infer<typeof actionSchema>
export const draftSchema = z
  .object({
    id: identifier,
    name: text,
    description: text,
    trigger: identifier,
    conditions: z.array(conditionSchema).min(1).max(50),
    actions: z.array(actionSchema).min(1).max(100),
    effect: text,
    enabled: z.boolean(),
    priority: z.number().int().min(-1000000).max(1000000),
    version: z.number().int().positive(),
  })
  .strict()
export type BehaviorDraft = z.infer<typeof draftSchema>
export interface Catalog {
  objects: readonly string[]
  classes: readonly string[]
  properties: readonly { id: string; kind: 'single' | 'multi' }[]
  behaviorIds: readonly string[]
  editingBehaviorId?: string
}
export interface Context {
  projectId: string
  inputVersion: string
  behaviorVersion: string
  scopeId: string
}
export interface EventChange {
  operation: 'add' | 'remove' | 'set'
  object: string
  property: string
  value: Value
}
export interface SampleEvent {
  id: string
  type: string
  payload: string
  changes: EventChange[]
}
const contextSchema = z
  .object({
    projectId: identifier,
    inputVersion: identifier,
    behaviorVersion: identifier,
    scopeId: identifier,
  })
  .strict()
export const bindingSchema = contextSchema.extend({ requestId: identifier }).strict()
export type Binding = z.infer<typeof bindingSchema>
const fact = z.object({ object: identifier, property: identifier, value: valueSchema }).strict()
export const resultSchema = z
  .object({
    binding: bindingSchema,
    runId: identifier,
    state: z.enum(['candidate', 'completed', 'failed', 'cancelled']),
    committed: z.boolean(),
    freshness: z.enum(['current', 'stale', 'historical']),
    freshnessDetail: z.string().max(500),
    assertionVersion: identifier,
    inferenceVersion: identifier,
    semanticsVersion: identifier,
    conditions: z
      .array(
        z
          .object({
            eventId: identifier,
            behaviorId: identifier,
            triggered: z.boolean(),
            reason: text,
          })
          .strict(),
      )
      .max(10000),
    actions: z
      .array(
        z
          .object({
            eventId: identifier,
            behaviorId: identifier,
            index: z.number().int().nonnegative(),
            kind: z.enum(['create', 'update', 'relate', 'notify']),
            state: z.enum(['planned', 'applied', 'deduplicated', 'rolled_back', 'skipped']),
            detail: text,
          })
          .strict(),
      )
      .max(10000),
    diff: z.object({ added: z.array(fact).max(10000), removed: z.array(fact).max(10000) }).strict(),
    notifications: z
      .array(
        z
          .object({
            eventId: identifier,
            behaviorId: identifier,
            message: text,
            state: z.enum(['candidate', 'recorded', 'discarded']),
          })
          .strict(),
      )
      .max(10000),
    error: z
      .enum(['conflict', 'invalid_input', 'unavailable', 'execution_failed', 'cancel_failed'])
      .nullable(),
  })
  .strict()
  .superRefine((result, ctx) => {
    if (result.committed !== (result.state === 'completed'))
      ctx.addIssue({ code: 'custom', message: '结果提交状态不一致' })
    if ((result.state === 'failed') !== (result.error !== null))
      ctx.addIssue({ code: 'custom', message: '结果错误状态不一致' })
    if (result.freshness === 'stale' && !result.freshnessDetail.trim())
      ctx.addIssue({ code: 'custom', message: '过期结果缺少说明' })
  })
export type BehaviorResult = z.infer<typeof resultSchema>
export interface SampleRequest {
  binding: Binding
  draft: BehaviorDraft
  events: {
    id: string
    type: string
    payload: Record<string, string | number | boolean | null>
    changes: EventChange[]
  }[]
}
/** Private component callbacks; these are not registered bridge methods. */
export interface BehaviorServices {
  runSample?: (request: SampleRequest) => Promise<unknown>
  refreshResult?: (binding: Binding, runId: string) => Promise<unknown>
  cancelSample?: (binding: Binding) => Promise<unknown>
}
export interface Issue {
  path: string
  message: string
}
export function emptyDraft(): BehaviorDraft {
  return {
    id: '',
    name: '',
    description: '',
    trigger: '',
    conditions: [],
    actions: [],
    effect: '',
    enabled: true,
    priority: 0,
    version: 1,
  }
}
export function sameContext(a: Context, b: Context): boolean {
  return (
    a.projectId === b.projectId &&
    a.inputVersion === b.inputVersion &&
    a.behaviorVersion === b.behaviorVersion &&
    a.scopeId === b.scopeId
  )
}
export function validateDraft(draft: BehaviorDraft, catalog: Catalog): Issue[] {
  const parsed = draftSchema.safeParse(draft)
  if (!parsed.success)
    return parsed.error.issues.map((issue) => ({
      path: issue.path.join('.'),
      message: '请填写完整且有效的值',
    }))
  draft = parsed.data
  const issues: Issue[] = []
  if (catalog.behaviorIds.includes(draft.id) && draft.id !== catalog.editingBehaviorId)
    issues.push({ path: 'id', message: '行为 ID 在项目中已存在' })
  const known = new Set(catalog.objects)
  const properties = new Map(catalog.properties.map((property) => [property.id, property.kind]))
  for (const [index, condition] of draft.conditions.entries()) {
    if (!known.has(condition.object))
      issues.push({ path: `conditions.${index}`, message: '条件引用了未知对象' })
    if (condition.kind !== 'type' && !properties.has(condition.property))
      issues.push({ path: `conditions.${index}`, message: '条件引用了未知属性' })
    if (
      condition.kind === 'equals' &&
      condition.value.kind === 'iri' &&
      !known.has(condition.value.value)
    )
      issues.push({ path: `conditions.${index}`, message: '条件值引用了未知对象' })
    if (condition.kind === 'type' && !catalog.classes.includes(condition.classId))
      issues.push({ path: `conditions.${index}`, message: '条件引用了未知类' })
  }
  for (const [index, action] of draft.actions.entries()) {
    const path = `actions.${index}`
    if (action.kind === 'create') {
      if (known.has(action.object)) issues.push({ path, message: '创建动作的对象 ID 已存在或重复' })
      if (!catalog.classes.includes(action.classId))
        issues.push({ path, message: '创建动作引用了未知类' })
      known.add(action.object)
    } else if (action.kind !== 'notify') {
      if (!known.has(action.object))
        issues.push({ path, message: '动作引用了未知或尚未创建的对象' })
      if (!properties.has(action.property)) issues.push({ path, message: '动作引用了未知属性' })
      if (action.kind === 'relate' && properties.get(action.property) === 'single')
        issues.push({ path, message: '单值关系请使用更新属性动作' })
      if (action.kind === 'relate' && !known.has(action.target))
        issues.push({ path, message: '关系目标不存在' })
      if (action.kind === 'update' && properties.get(action.property) === 'multi')
        issues.push({ path, message: '多值关系请使用添加关系动作' })
      if (action.kind === 'update' && action.value.kind === 'iri' && !known.has(action.value.value))
        issues.push({ path, message: '属性值引用了未知对象' })
    }
  }
  return issues
}
const payloadSchema = z.record(
  z.string().min(1).max(200),
  z.union([z.string().max(2000), z.number().finite(), z.boolean(), z.null()]),
)
export function parseEvents(events: SampleEvent[]): {
  events: SampleRequest['events']
  issues: Issue[]
} {
  const issues: Issue[] = []
  const seen = new Set<string>()
  const parsed: SampleRequest['events'] = []
  if (!events.length || events.length > 100)
    issues.push({ path: 'events', message: '请提供 1–100 个事件' })
  events.forEach((event, index) => {
    const path = `events.${index}`
    if (!identifier.safeParse(event.id).success || !identifier.safeParse(event.type).success)
      issues.push({ path, message: '事件 ID 和类型不能为空或过长' })
    if (seen.has(event.id.trim()))
      issues.push({ path, message: '本批次事件 ID 重复；重放幂等请重复运行原事件' })
    seen.add(event.id.trim())
    try {
      if (event.payload.length > 20000) throw new Error('size')
      const payload = payloadSchema.parse(JSON.parse(event.payload))
      if (Object.keys(payload).length > 100) throw new Error('size')
      const changes = z
        .array(
          z
            .object({
              operation: z.enum(['add', 'remove', 'set']),
              object: identifier,
              property: identifier,
              value: valueSchema,
            })
            .strict(),
        )
        .max(100)
        .parse(event.changes)
      parsed.push({ id: event.id.trim(), type: event.type.trim(), payload, changes })
    } catch {
      issues.push({
        path,
        message:
          '事件内容须为有限大小的 JSON 对象（字符串、数字、布尔值、null）；事实变更必须填写完整',
      })
    }
  })
  return { events: parsed, issues }
}
export function formatValue(value: Value): string {
  return value.kind === 'iri' ? `<${value.value}>` : JSON.stringify(value.value)
}
