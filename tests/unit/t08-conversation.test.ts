import { describe, expect, it, vi } from 'vitest'
import { AgentConversation } from '../../apps/desktop/src/main/agent/conversation'
import type { TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'
const context: TrustedContext = {
  projectId: 'p1',
  projectRevision: 1,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: ['001'],
}
const options = {
  mode: 'enabled',
  effort: 'high',
  maxTokens: 1024,
  maxExchanges: 4,
  maxTotalRequestedTokens: 4096,
  toolTimeoutMs: 1000,
  projectedFieldIds: ['public'],
}
const evidence = {
  kind: 'evidence',
  projectId: 'p1',
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  resultId: 'result1',
  status: 'current',
  traceRefs: ['trace1'],
  fields: [
    { fieldId: 'public', value: '001' },
    { fieldId: 'private', value: 'secret synthetic column' },
  ],
}
const call = {
  id: 'call.provider/1',
  type: 'function',
  function: {
    name: 'query_execute',
    arguments: '{"sparql":"SELECT ?id WHERE {?s <urn:id> ?id}","scope":"asserted"}',
  },
}
const raw = (
  id: string,
  content: string | null,
  tool_calls?: unknown[],
  reasoning_content: string | undefined = 'synthetic reasoning',
) =>
  JSON.stringify({
    id,
    object: 'chat.completion',
    created: 1,
    model: 'synthetic-model',
    choices: [
      {
        index: 0,
        finish_reason: tool_calls ? 'tool_calls' : 'stop',
        message: {
          role: 'assistant',
          content,
          reasoning_content,
          ...(tool_calls ? { tool_calls } : {}),
        },
      },
    ],
  })
const current = () => context
const signal = () => new AbortController().signal

describe('T08 pure conversation, synthetic protocol-to-adapter round trips; no transport', () => {
  it('round-trips thinking tools with final field projection, exact host evidence, and preserved reasoning in next user turn', async () => {
    const execute = vi.fn(async () => evidence)
    const conversation = new AgentConversation(context, '列出设备', options, {
      query_execute: { execute },
    })
    const first = conversation.prepareExchange(current)
    expect(first.exchangeId).toBe(1)
    expect(first.body.tools?.map((tool) => tool.function.name)).toEqual(['query_execute'])
    first.body.messages[1].content = 'mutating returned snapshot must not change internal state'
    const toolResponse = raw('r1', null, [call])
    expect(
      (await conversation.acceptResponse(1, toolResponse, current, signal())).state.phase,
    ).toBe('ready')
    const second = conversation.prepareExchange(current)
    expect(second.body.messages[1].content).toBe('列出设备')
    expect(second.body.messages.slice(2)).toEqual([
      {
        role: 'assistant',
        content: null,
        reasoning_content: 'synthetic reasoning',
        tool_calls: [call],
      },
      {
        role: 'tool',
        tool_call_id: call.id,
        content:
          '{"kind":"evidence","status":"current","fields":[{"fieldId":"public","value":"001"}]}',
      },
    ])
    const answer = await conversation.acceptResponse(
      2,
      raw('r2', '{"kind":"evidence","callIds":["call.provider/1"]}'),
      current,
      signal(),
    )
    expect(answer.state).toEqual({
      phase: 'answered',
      exchanges: 2,
      requestedTokenCeiling: 2048,
      error: null,
      answer: {
        kind: 'evidence',
        receipts: [{ callId: call.id, tool: 'query_execute', outcome: evidence }],
      },
    })
    expect(execute).toHaveBeenCalledTimes(1)
    conversation.addUserTurn('再解释', current)
    const third = conversation.prepareExchange(current)
    expect(third.body.messages.at(-2)).toMatchObject({
      role: 'assistant',
      reasoning_content: 'synthetic reasoning',
    })
    expect(third.body.messages.at(-1)).toEqual({ role: 'user', content: '再解释' })
  })
  it('does not consume the pending exchange for an old/mismatched response and refuses concurrent/duplicate completion', async () => {
    const conversation = new AgentConversation(context, '提示', options)
    conversation.prepareExchange(current)
    await expect(
      conversation.acceptResponse(99, raw('r1', '{"kind":"uncertain"}'), current, signal()),
    ).rejects.toThrow('INVALID_PROTOCOL')
    expect(conversation.state().phase).toBe('awaiting-provider')
    expect(() => conversation.prepareExchange(current)).toThrow('INVALID_PROTOCOL')
    await conversation.acceptResponse(1, raw('r1', '{"kind":"uncertain"}'), current, signal())
    await expect(
      conversation.acceptResponse(1, raw('r1', '{"kind":"uncertain"}'), current, signal()),
    ).rejects.toThrow('INVALID_PROTOCOL')
    conversation.addUserTurn('继续', current)
    conversation.prepareExchange(current)
    await expect(
      conversation.acceptResponse(2, raw('r1', '{"kind":"uncertain"}'), current, signal()),
    ).rejects.toThrow('INVALID_PROTOCOL')
  })
  it('rejects missing thinking fields before executing any tool and does not silently fallback', async () => {
    const execute = vi.fn(async () => evidence)
    const conversation = new AgentConversation(context, '查询', options, {
      query_execute: { execute },
    })
    conversation.prepareExchange(current)
    const response = JSON.parse(raw('r1', null, [call]))
    delete response.choices[0].message.reasoning_content
    await expect(
      conversation.acceptResponse(1, JSON.stringify(response), current, signal()),
    ).rejects.toThrow('INVALID_PROTOCOL')
    expect(execute).not.toHaveBeenCalled()
    expect(conversation.state()).toMatchObject({ phase: 'failed', error: 'INVALID_PROTOCOL' })
  })
  it('drops old-context replies and sanitizes a failed host context read', async () => {
    const execute = vi.fn(async () => evidence)
    const conversation = new AgentConversation(context, '查询', options, {
      query_execute: { execute },
    })
    conversation.prepareExchange(current)
    await expect(
      conversation.acceptResponse(
        1,
        raw('r1', null, [call]),
        () => ({ ...context, projectRevision: 2 }),
        signal(),
      ),
    ).rejects.toThrow('STALE_CONTEXT')
    expect(execute).not.toHaveBeenCalled()
    const other = new AgentConversation(context, '提示', options)
    expect(() =>
      other.prepareExchange(() => {
        throw Error('secret/path')
      }),
    ).toThrow('STALE_CONTEXT')
    expect(JSON.stringify(other.state())).not.toContain('secret')
  })
  it('bounds attempts and requested output tokens, including provider failures, without automatic retries', async () => {
    const conversation = new AgentConversation(context, '提示', { ...options, maxExchanges: 1 })
    conversation.prepareExchange(current)
    await conversation.acceptResponse(1, raw('r1', '{"kind":"uncertain"}'), current, signal())
    conversation.addUserTurn('继续', current)
    expect(() => conversation.prepareExchange(current)).toThrow('BUDGET_EXCEEDED')
    const budget = new AgentConversation(context, '提示', {
      ...options,
      maxTotalRequestedTokens: 100,
    })
    expect(() => budget.prepareExchange(current)).toThrow('BUDGET_EXCEEDED')
    const failed = new AgentConversation(context, '提示', options)
    failed.prepareExchange(current)
    failed.providerFailed(1, 'TIMED_OUT')
    expect(failed.state()).toEqual({
      phase: 'failed',
      exchanges: 1,
      requestedTokenCeiling: 1024,
      error: 'TIMED_OUT',
      answer: null,
    })
    expect(() => failed.prepareExchange(current)).toThrow('INVALID_PROTOCOL')
  })
  it('cancels in-flight tools without accepting a late fulfillment or issuing another request', async () => {
    let finish: (value: unknown) => void = () => undefined
    const conversation = new AgentConversation(context, '查询', options, {
      query_execute: {
        execute: async () =>
          new Promise((resolve) => {
            finish = resolve
          }),
      },
    })
    conversation.prepareExchange(current)
    const pending = conversation.acceptResponse(1, raw('r1', null, [call]), current, signal())
    await Promise.resolve()
    conversation.cancel()
    await expect(pending).rejects.toThrow('CANCELLED')
    finish(evidence)
    await Promise.resolve()
    expect(conversation.state()).toMatchObject({
      phase: 'cancelled',
      answer: null,
      error: 'CANCELLED',
    })
    expect(() => conversation.prepareExchange(current)).toThrow('CANCELLED')
  })
  it('rejects malformed final JSON while preserving safe terminal metadata', async () => {
    const conversation = new AgentConversation(context, '查询', options)
    conversation.prepareExchange(current)
    await expect(
      conversation.acceptResponse(
        1,
        raw('r1', '{"kind":"suggestion","text":"检查通过"}'),
        current,
        signal(),
      ),
    ).rejects.toThrow('INVALID_JSON')
    expect(conversation.state()).toMatchObject({
      phase: 'failed',
      error: 'INVALID_JSON',
      answer: null,
    })
  })
})
