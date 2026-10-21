import { z } from 'zod'
import { AgentError, type AgentErrorCode } from './errors'
import {
  AgentSession,
  AGENT_SYSTEM_PROMPT,
  contextSchema,
  projectToolMessage,
  sameContext,
  type DomainPort,
  type TrustedContext,
} from './agent-service'
import { decodeChatResponse, encodeChatRequest, type ChatMessage } from './deepseek-codec'
import type { ToolName } from './tools'

const optionsSchema = z
  .object({
    mode: z.enum(['enabled', 'disabled']),
    effort: z.enum(['low', 'high', 'max']),
    maxTokens: z.number().int().min(1).max(32768),
    maxExchanges: z.number().int().min(1).max(16),
    maxTotalRequestedTokens: z.number().int().min(1).max(524288),
    toolTimeoutMs: z.number().int().min(1).max(60000),
    projectedFieldIds: z.array(z.string().regex(/^[A-Za-z0-9:_-]{1,128}$/)).max(1000),
  })
  .strict()
export type ConversationOptions = z.infer<typeof optionsSchema>
type Phase = 'ready' | 'awaiting-provider' | 'executing-tools' | 'answered' | 'failed' | 'cancelled'
type Answer = ReturnType<AgentSession['resolveAnswer']>
export interface ExchangeData {
  exchangeId: number
  body: ReturnType<typeof encodeChatRequest>
}

/**
 * Private main-process conversation state only. No transport or approval API.
 * Every prepared body still requires the sole I06 final-byte authorization and send.
 * Supplied ports must be the actual approved domain adapters, never simulated runtime results.
 */
export class AgentConversation {
  private readonly context: TrustedContext
  private readonly options: ConversationOptions
  private readonly session: AgentSession
  private readonly messages: ChatMessage[]
  private readonly lifecycle = new AbortController()
  private readonly responseIds = new Set<string>()
  private phase: Phase = 'ready'
  private pending: number | null = null
  private exchanges = 0
  private requestedTokenCeiling = 0
  private answer: Answer | null = null
  private error: AgentErrorCode | null = null

  constructor(
    context: unknown,
    userText: unknown,
    options: unknown,
    ports: Partial<Record<ToolName, DomainPort>> = {},
  ) {
    const parsedContext = contextSchema.safeParse(context)
    const parsedOptions = optionsSchema.safeParse(options)
    const parsedText = z.string().trim().min(1).max(32000).safeParse(userText)
    if (!parsedContext.success || !parsedOptions.success || !parsedText.success)
      throw new AgentError('INVALID_PROTOCOL')
    this.context = parsedContext.data
    this.options = parsedOptions.data
    this.session = new AgentSession(this.context, ports)
    this.messages = [
      {
        role: 'system',
        content: `${AGENT_SYSTEM_PROMPT}\n当前模式：${this.context.mode === 'tutor' ? '导师，优先提问和分步提示' : '项目，可生成完整草稿'}。`,
      },
      { role: 'user', content: parsedText.data },
    ]
  }
  private assertCurrent(readCurrent: () => unknown) {
    let current: unknown
    try {
      current = readCurrent()
    } catch {
      throw new AgentError('STALE_CONTEXT')
    }
    const parsed = contextSchema.safeParse(current)
    if (!parsed.success || !sameContext(this.context, parsed.data))
      throw new AgentError('STALE_CONTEXT')
  }
  private fail(code: AgentErrorCode) {
    this.phase = code === 'CANCELLED' ? 'cancelled' : 'failed'
    this.pending = null
    this.error = code
    this.answer = null
  }
  /** A snapshot for local UI; excludes prompt/history/body/provider diagnostics. */
  state() {
    return {
      phase: this.phase,
      exchanges: this.exchanges,
      requestedTokenCeiling: this.requestedTokenCeiling,
      error: this.error,
      answer: structuredClone(this.answer),
    }
  }
  /** Pure request preparation. Returned data confers no permission to send. */
  prepareExchange(readCurrent: () => unknown): ExchangeData {
    if (this.phase !== 'ready')
      throw new AgentError(this.phase === 'cancelled' ? 'CANCELLED' : 'INVALID_PROTOCOL')
    try {
      this.assertCurrent(readCurrent)
      if (
        this.exchanges >= this.options.maxExchanges ||
        this.requestedTokenCeiling + this.options.maxTokens > this.options.maxTotalRequestedTokens
      ) {
        throw new AgentError('BUDGET_EXCEEDED')
      }
      const body = encodeChatRequest({
        messages: this.messages,
        mode: this.options.mode,
        effort: this.options.effort,
        availableTools: this.session.availableTools().map((tool) => tool.function.name),
        maxTokens: this.options.maxTokens,
      })
      this.exchanges++
      this.requestedTokenCeiling += this.options.maxTokens
      this.pending = this.exchanges
      this.phase = 'awaiting-provider'
      return { exchangeId: this.exchanges, body: structuredClone(body) }
    } catch (error) {
      const safe = error instanceof AgentError ? error : new AgentError('INVALID_PROTOCOL')
      this.fail(safe.code)
      throw safe
    }
  }
  /** Called by the composition root for the matching I06 exchange, never by a model tool. */
  providerFailed(exchangeId: number, code: 'TIMED_OUT' | 'CANCELLED' | 'INVALID_PROTOCOL') {
    if (this.phase !== 'awaiting-provider' || this.pending !== exchangeId)
      throw new AgentError('INVALID_PROTOCOL')
    if (!['TIMED_OUT', 'CANCELLED', 'INVALID_PROTOCOL'].includes(code))
      throw new AgentError('INVALID_PROTOCOL')
    this.fail(code)
  }
  async acceptResponse(
    exchangeId: number,
    json: string,
    readCurrent: () => unknown,
    signal: AbortSignal,
  ) {
    // Mismatched/replayed replies must not consume the currently pending exchange.
    if (this.phase !== 'awaiting-provider' || this.pending !== exchangeId)
      throw new AgentError('INVALID_PROTOCOL')
    this.phase = 'executing-tools'
    this.pending = null
    const combined = AbortSignal.any([signal, this.lifecycle.signal])
    try {
      if (combined.aborted) throw new AgentError('CANCELLED')
      this.assertCurrent(readCurrent)
      const response = decodeChatResponse(json)
      if (this.responseIds.has(response.id)) throw new AgentError('INVALID_PROTOCOL')
      const message = response.choices[0].message
      if (
        this.options.mode === 'enabled' &&
        this.session.availableTools().length &&
        typeof message.reasoning_content !== 'string'
      ) {
        throw new AgentError('INVALID_PROTOCOL')
      }
      this.responseIds.add(response.id)
      if (message.tool_calls) {
        const receipts = await this.session.executeCalls(
          message.tool_calls,
          readCurrent,
          combined,
          this.options.toolTimeoutMs,
        )
        if (combined.aborted) throw new AgentError('CANCELLED')
        this.assertCurrent(readCurrent)
        const projected = receipts.map((receipt) =>
          projectToolMessage(receipt, this.options.projectedFieldIds),
        )
        this.messages.push(message, ...projected)
        this.phase = 'ready'
      } else {
        let value: unknown
        try {
          value = JSON.parse(message.content!)
        } catch {
          throw new AgentError('INVALID_JSON')
        }
        this.assertCurrent(readCurrent)
        this.answer = this.session.resolveAnswer(value, this.context)
        this.messages.push(message)
        this.phase = 'answered'
      }
      return {
        returnedModel: response.model,
        fingerprint: response.system_fingerprint ?? null,
        usage: response.usage ?? null,
        state: this.state(),
      }
    } catch (error) {
      const safe = error instanceof AgentError ? error : new AgentError('INVALID_PROTOCOL')
      this.fail(safe.code)
      throw safe
    }
  }
  /** Additional user turns retain prior assistant reasoning when tools remain in the request. */
  addUserTurn(text: unknown, readCurrent: () => unknown) {
    if (this.phase !== 'answered') throw new AgentError('INVALID_PROTOCOL')
    this.assertCurrent(readCurrent)
    const parsed = z.string().trim().min(1).max(32000).safeParse(text)
    if (!parsed.success) throw new AgentError('INVALID_PROTOCOL')
    this.messages.push({ role: 'user', content: parsed.data })
    this.phase = 'ready'
    this.answer = null
  }
  cancel() {
    if (this.phase === 'answered' || this.phase === 'failed' || this.phase === 'cancelled') return
    this.lifecycle.abort()
    this.fail('CANCELLED')
  }
}
