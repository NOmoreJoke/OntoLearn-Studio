import { z } from 'zod'
import { AgentError } from './errors'
import { parseToolArguments, toolDefinitions, toolNameSchema } from './tools'

export const CODEC_VERSION = 'deepseek-chat-text-v1'
export const DEEPSEEK_ENDPOINT = 'https://api.deepseek.com/chat/completions'
export const REQUEST_MODEL = 'deepseek-v4-pro'
const text = z.string().max(262144)
const callId = z.string().min(1).max(128)
export const toolCallSchema = z
  .object({
    id: callId,
    type: z.literal('function'),
    function: z.object({ name: z.string().min(1).max(64), arguments: text }).strict(),
  })
  .strict()
export const assistantSchema = z
  .object({
    role: z.literal('assistant'),
    content: text.nullable(),
    reasoning_content: text.nullable().optional(),
    tool_calls: z.array(toolCallSchema).min(1).max(16).optional(),
  })
  .strict()
const messageSchema = z.discriminatedUnion('role', [
  z.object({ role: z.literal('system'), content: text.min(1) }).strict(),
  z.object({ role: z.literal('user'), content: text.min(1) }).strict(),
  assistantSchema,
  z.object({ role: z.literal('tool'), content: text.min(1), tool_call_id: callId }).strict(),
])
export type ChatMessage = z.infer<typeof messageSchema>
export type AssistantMessage = z.infer<typeof assistantSchema>
export type ToolCall = z.infer<typeof toolCallSchema>
export type ThinkingMode = 'enabled' | 'disabled'
const requestInputSchema = z
  .object({
    messages: z.array(messageSchema).min(2).max(100),
    mode: z.enum(['enabled', 'disabled']),
    effort: z.enum(['low', 'high', 'max']),
    availableTools: z.array(toolNameSchema).max(10),
    maxTokens: z.number().int().min(1).max(32768),
  })
  .strict()

/** Only produces data. The sole I06 gateway must inspect these exact final bytes. */
export function encodeChatRequest(input: unknown) {
  const parsed = requestInputSchema.safeParse(input)
  if (!parsed.success) throw new AgentError('INVALID_PROTOCOL')
  const { messages, mode, effort, availableTools, maxTokens } = parsed.data
  const pending = new Set<string>()
  const seen = new Set<string>()
  if (messages[0].role !== 'system' || messages[1].role !== 'user') {
    throw new AgentError('INVALID_PROTOCOL')
  }
  for (const [index, message] of messages.entries()) {
    if (message.role === 'system' && index !== 0) throw new AgentError('INVALID_PROTOCOL')
    if (message.role === 'tool') {
      if (!pending.delete(message.tool_call_id)) throw new AgentError('INVALID_PROTOCOL')
      continue
    }
    if (pending.size) throw new AgentError('INVALID_PROTOCOL')
    if (message.role !== 'assistant') continue
    if (
      mode === 'enabled' &&
      availableTools.length &&
      typeof message.reasoning_content !== 'string'
    ) {
      throw new AgentError('INVALID_PROTOCOL')
    }
    if (!message.tool_calls && !message.content?.trim()) throw new AgentError('INVALID_PROTOCOL')
    for (const call of message.tool_calls ?? []) {
      if (seen.has(call.id)) throw new AgentError('INVALID_PROTOCOL')
      if (!availableTools.some((name) => name === call.function.name))
        throw new AgentError('TOOL_NOT_ALLOWED')
      parseToolArguments(call.function.name, call.function.arguments)
      seen.add(call.id)
      pending.add(call.id)
    }
  }
  if (pending.size) throw new AgentError('INVALID_PROTOCOL')
  // This instruction is application-owned; imported text must only be in user/tool data.
  const system = messages[0]
  if (!system.content?.toLowerCase().includes('json')) throw new AgentError('INVALID_PROTOCOL')
  const body = {
    model: REQUEST_MODEL,
    messages,
    thinking: { type: mode },
    ...(mode === 'enabled' ? { reasoning_effort: effort } : {}),
    max_tokens: maxTokens,
    stream: false as const,
    response_format: { type: 'json_object' as const },
    ...(availableTools.length ? { tools: toolDefinitions(availableTools) } : {}),
  }
  if (Buffer.byteLength(JSON.stringify(body), 'utf8') > 524288) {
    throw new AgentError('BUDGET_EXCEEDED')
  }
  return body
}

const tokens = z.number().int().nonnegative()
const usageSchema = z
  .object({
    prompt_tokens: tokens,
    completion_tokens: tokens,
    total_tokens: tokens,
    prompt_cache_hit_tokens: tokens.optional(),
    prompt_cache_miss_tokens: tokens.optional(),
    prompt_tokens_details: z.object({ cached_tokens: tokens.optional() }).strict().optional(),
    completion_tokens_details: z
      .object({ reasoning_tokens: tokens.optional() })
      .strict()
      .optional(),
  })
  .strict()
  .superRefine((v, ctx) => {
    if (v.total_tokens !== v.prompt_tokens + v.completion_tokens)
      ctx.addIssue({ code: 'custom', message: 'token total' })
  })
const responseSchema = z
  .object({
    id: z.string().min(1).max(256),
    object: z.literal('chat.completion'),
    created: tokens,
    model: z.string().min(1).max(256),
    system_fingerprint: z.string().max(256).nullable().optional(),
    choices: z
      .array(
        z
          .object({
            index: z.literal(0),
            message: assistantSchema,
            finish_reason: z.enum([
              'stop',
              'tool_calls',
              'length',
              'content_filter',
              'insufficient_system_resource',
              'aborted',
            ]),
            logprobs: z.null().optional(),
          })
          .strict(),
      )
      .length(1),
    usage: usageSchema.optional(),
  })
  .strict()
export function decodeChatResponse(json: string) {
  if (Buffer.byteLength(json, 'utf8') > 524288) throw new AgentError('BUDGET_EXCEEDED')
  let value: unknown
  try {
    value = JSON.parse(json)
  } catch {
    throw new AgentError('INVALID_JSON')
  }
  const parsed = responseSchema.safeParse(value)
  if (!parsed.success) throw new AgentError('INVALID_PROTOCOL')
  const response = parsed.data
  const choice = response.choices[0]
  if (choice.finish_reason !== 'stop' && choice.finish_reason !== 'tool_calls') {
    throw new AgentError('INCOMPLETE_RESPONSE')
  }
  const calls = choice.message.tool_calls
  if ((choice.finish_reason === 'tool_calls') !== Boolean(calls?.length)) {
    throw new AgentError('INVALID_PROTOCOL')
  }
  if (!calls && !choice.message.content?.trim()) throw new AgentError('INVALID_JSON')
  if (calls && new Set(calls.map((call) => call.id)).size !== calls.length) {
    throw new AgentError('INVALID_PROTOCOL')
  }
  return response
}
export function decodeStructuredContent<T>(message: AssistantMessage, schema: z.ZodType<T>): T {
  if (message.tool_calls || !message.content?.trim()) throw new AgentError('INVALID_JSON')
  try {
    return schema.parse(JSON.parse(message.content))
  } catch {
    throw new AgentError('INVALID_JSON')
  }
}
