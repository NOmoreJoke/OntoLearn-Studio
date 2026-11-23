import { isDeepStrictEqual } from 'node:util'
import { z } from 'zod'
import { assistantSchema, toolCallSchema } from '../agent/deepseek-codec'
import { toolDefinitions, toolNameSchema, type ToolName } from '../agent/tools'
import { GatewayFailure, invocationSchema, opaqueId, partKindSchema, scopesSchema } from './policy'

export const MAX_BODY_BYTES = 256 * 1024
type PartKind = z.infer<typeof partKindSchema>
export const approvedBodySchema = invocationSchema.omit({ materials: true }).extend({
  body: z.string(),
  configVersion: opaqueId,
  scopes: scopesSchema,
  parts: z
    .array(
      z.strictObject({ materialId: opaqueId, kind: partKindSchema, path: z.string().max(128) }),
    )
    .max(512),
})
export type ApprovedBodyRequest = z.infer<typeof approvedBodySchema>

const messages = z.discriminatedUnion('role', [
  z.strictObject({ role: z.literal('system'), content: z.string() }),
  z.strictObject({ role: z.literal('user'), content: z.string() }),
  assistantSchema,
  z.strictObject({
    role: z.literal('tool'),
    content: z.string(),
    tool_call_id: toolCallSchema.shape.id,
  }),
])
const request = z.strictObject({
  model: z.string(),
  messages: z.array(messages).min(2).max(100),
  thinking: z.strictObject({ type: z.enum(['enabled', 'disabled']) }),
  reasoning_effort: z.enum(['low', 'high', 'max']).optional(),
  max_tokens: z.number().int().min(1).max(32768),
  stream: z.literal(false),
  response_format: z.strictObject({ type: z.literal('json_object') }),
  tools: z.array(z.unknown()).min(1).max(10).optional(),
})
const denied = (): never => {
  throw new GatewayFailure('SCOPE_EXCEEDED')
}

// Only insignificant whitespace may differ from the encoder. Comparing tokens detects
// duplicate keys, ignored numeric variants and alternate escapes without rewriting egress.
function tokens(json: string): string {
  return json.replace(/"(?:[^"\\]|\\[\s\S])*"|[ \t\r\n]+/g, (token) =>
    token.startsWith('"') ? token : '',
  )
}

export function readBodyFields(body: string, model: string) {
  if (Buffer.byteLength(body, 'utf8') > MAX_BODY_BYTES) throw new GatewayFailure('INVALID_INPUT')
  let raw: unknown
  try {
    raw = JSON.parse(body)
  } catch {
    throw new GatewayFailure('INVALID_INPUT')
  }
  const parsed = request.safeParse(raw)
  if (!parsed.success) return denied()
  const value = parsed.data
  if (
    value.model !== model ||
    value.messages[0].role !== 'system' ||
    value.messages[1].role !== 'user' ||
    (value.thinking.type === 'enabled') !== (value.reasoning_effort !== undefined)
  )
    return denied()
  const names: ToolName[] = []
  for (const tool of value.tools ?? []) {
    const name = toolNameSchema.safeParse(
      (tool as { function?: { name?: unknown } } | null)?.function?.name,
    )
    if (!name.success || names.includes(name.data)) return denied()
    names.push(name.data)
  }
  if (
    (value.tools && !isDeepStrictEqual(value.tools, toolDefinitions(names))) ||
    tokens(body) !== tokens(JSON.stringify(raw))
  )
    return denied()

  const fields = new Map<string, { kind: PartKind; text: string }>()
  for (const [index, message] of value.messages.entries()) {
    const path = `messages.${index}`
    const kind = message.role === 'tool' ? 'tool' : message.role === 'user' ? 'selected' : 'history'
    if (message.content !== null) fields.set(`${path}.content`, { kind, text: message.content })
    if (message.role === 'tool')
      fields.set(`${path}.tool_call_id`, { kind, text: message.tool_call_id })
    if (message.role !== 'assistant') continue
    if (typeof message.reasoning_content === 'string')
      fields.set(`${path}.reasoning_content`, { kind, text: message.reasoning_content })
    for (const [callIndex, call] of (message.tool_calls ?? []).entries()) {
      if (!names.some((name) => name === call.function.name)) return denied()
      const callPath = `${path}.tool_calls.${callIndex}`
      fields.set(`${callPath}.id`, { kind, text: call.id })
      fields.set(`${callPath}.function.arguments`, { kind, text: call.function.arguments })
    }
  }
  return fields
}
