import { describe, expect, it, vi } from 'vitest'
import {
  AgentSession,
  AGENT_SYSTEM_PROMPT,
  projectToolMessage,
  sameContext,
  type ToolReceipt,
  type TrustedContext,
} from '../../apps/desktop/src/main/agent/agent-service'
import { AgentConversation } from '../../apps/desktop/src/main/agent/conversation'
import { AgentError, type AgentErrorCode } from '../../apps/desktop/src/main/agent/errors'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
  encodeChatRequest,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import {
  sidebarContextKey,
  sidebarInteraction,
  sidebarIsCurrent,
  updateSidebarInteraction,
} from '../../apps/desktop/src/renderer/src/agent/sidebar-presentation'

const context: TrustedContext = {
  projectId: 'p1',
  projectRevision: 1,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: ['001', '002'],
}
const signature = {
  endpoint: DEEPSEEK_ENDPOINT,
  requestedModel: REQUEST_MODEL,
  returnedModel: 'synthetic-tested-version',
  fingerprint: 'synthetic-fp1',
  mode: 'enabled',
  effort: 'high',
  codecVersion: CODEC_VERSION,
}
const options = {
  mode: 'enabled',
  effort: 'high',
  maxTokens: 32,
  maxExchanges: 4,
  maxTotalRequestedTokens: 128,
  toolTimeoutMs: 1000,
  projectedFieldIds: [],
  expectedProviderSignature: signature,
}
const current = () => context
const signal = () => new AbortController().signal
const call = {
  id: 'review.call/1',
  type: 'function',
  function: { name: 'ontology_propose', arguments: '{"instruction":"建立设备类"}' },
}
const draft = { kind: 'draft', draftType: 'ontology', summary: '设备类', detail: '建议草稿' }
function response(overrides: Record<string, unknown> = {}) {
  return JSON.stringify({
    id: 'response1',
    object: 'chat.completion',
    created: 1,
    model: signature.returnedModel,
    system_fingerprint: signature.fingerprint,
    choices: [
      {
        index: 0,
        finish_reason: 'stop',
        message: { role: 'assistant', content: '{"kind":"uncertain"}', reasoning_content: 'test' },
      },
    ],
    ...overrides,
  })
}
const toolChoice = [
  {
    index: 0,
    finish_reason: 'tool_calls',
    message: { role: 'assistant', content: null, reasoning_content: 'test', tool_calls: [call] },
  },
]

describe('T08 designated review regressions: synthetic pure-module boundaries', () => {
  it('keeps input and late async transitions bound to their originating context', () => {
    const a = sidebarContextKey(context)
    const b = sidebarContextKey({ ...context, projectId: 'p2' })
    let interactions = updateSidebarInteraction({}, a, {
      question: 'A private question',
      dispatching: true,
    })
    expect(sidebarInteraction(interactions, b)).toEqual({
      question: '',
      dispatching: false,
      localError: false,
    })
    interactions = updateSidebarInteraction(interactions, b, {
      question: 'B question',
      dispatching: true,
    })
    interactions = updateSidebarInteraction(interactions, a, { question: 'A later edit' })
    interactions = updateSidebarInteraction(interactions, a, {
      localError: true,
      dispatching: false,
    })
    expect(sidebarInteraction(interactions, a)).toEqual({
      question: 'A later edit',
      dispatching: false,
      localError: true,
    })
    expect(sidebarInteraction(interactions, b)).toEqual({
      question: 'B question',
      dispatching: true,
      localError: false,
    })
  })
  it.each([
    { projectId: 'p2' },
    { projectRevision: 2 },
    { inputSnapshotId: 's2' },
    { scopeRef: 'scope2' },
    { module: 'mapping' as const },
    { mode: 'project' as const },
    { selectedObjectIds: ['002', '001'] },
  ])('binds interaction memory to each context field without sorting: %j', (change) => {
    expect(sidebarContextKey({ ...context, ...change })).not.toBe(sidebarContextKey(context))
  })
  it('ignores property insertion order when deriving the sidebar interaction identity', () => {
    const reordered = Object.fromEntries(Object.entries(context).reverse()) as TrustedContext
    expect(sidebarContextKey(reordered)).toBe(sidebarContextKey(context))
  })
  it('rechecks context at the deferred port invocation before executing the first call', async () => {
    let active = context
    const execute = vi.fn(async () => draft)
    const session = new AgentSession(context, { ontology_propose: { execute } })
    const pending = session.executeCalls([call], () => active, signal())
    active = { ...context, projectId: 'p2' }
    await expect(pending).rejects.toThrow('STALE_CONTEXT')
    expect(execute).not.toHaveBeenCalled()
    expect(session.currentTurnReceipts()).toEqual([])
  })
  it('rechecks each deferred call and retains the preceding completed receipt', async () => {
    let active = context
    const execute = vi.fn(async () => draft)
    const session = new AgentSession(context, { ontology_propose: { execute } })
    let scheduled = false
    const readCurrent = () => {
      if (execute.mock.calls.length === 1 && !scheduled) {
        scheduled = true
        queueMicrotask(() => {
          active = { ...context, inputSnapshotId: 's2' }
        })
      }
      return active
    }
    await expect(
      session.executeCalls([call, { ...call, id: 'review.call/2' }], readCurrent, signal()),
    ).rejects.toThrow('STALE_CONTEXT')
    expect(execute).toHaveBeenCalledTimes(1)
    expect(session.currentTurnReceipts()).toMatchObject([{ callId: call.id, outcome: draft }])
  })
  it('fails closed with a safe context code when authority becomes unreadable before dispatch', async () => {
    let readable = true
    const execute = vi.fn(async () => draft)
    const session = new AgentSession(context, { ontology_propose: { execute } })
    const pending = session.executeCalls(
      [call],
      () => {
        if (!readable) throw new Error('private-path/private-cell')
        return context
      },
      signal(),
    )
    readable = false
    await expect(pending).rejects.toThrow('STALE_CONTEXT')
    expect(execute).not.toHaveBeenCalled()
    expect(session.currentTurnReceipts()).toEqual([])
  })
  it('preserves the same ordered selection identity in main and sidebar, without sorting', () => {
    const reordered = { ...context, selectedObjectIds: ['002', '001'] }
    expect(sameContext(context, reordered)).toBe(false)
    expect(
      sidebarIsCurrent(
        {
          phase: 'ready',
          exchanges: 0,
          requestedTokenCeiling: 0,
          error: null,
          inputContext: context,
          localReceipts: [],
          answer: null,
        },
        reordered,
      ),
    ).toBe(false)
  })
  it('requires a preexisting strict host pin; request alias is not a returned-version pin', async () => {
    const missing = Object.fromEntries(
      Object.entries(options).filter(([name]) => name !== 'expectedProviderSignature'),
    )
    expect(() => new AgentConversation(context, '提示', missing)).toThrow('INVALID_PROTOCOL')
    for (const changed of [{ mode: 'disabled' }, { effort: 'max' }]) {
      expect(() => new AgentConversation(context, '提示', { ...options, ...changed })).toThrow(
        'INVALID_PROTOCOL',
      )
    }
    const external = structuredClone(options)
    const conversation = new AgentConversation(context, '提示', external)
    external.expectedProviderSignature.returnedModel = 'changed-after-construction'
    expect(conversation.prepareExchange(current).body.model).toBe(REQUEST_MODEL)
    const accepted = await conversation.acceptResponse(1, response(), current, signal())
    expect(accepted.returnedModel).toBe('synthetic-tested-version')
    expect(accepted.usage).toBeNull() // absent usage is unknown, never a recorded zero
  })
  it.each([
    { model: 'different-version' },
    { system_fingerprint: 'changed-fp' },
    { system_fingerprint: undefined },
  ])('rejects identity drift before any domain call: %j', async (change) => {
    const execute = vi.fn(async () => draft)
    const conversation = new AgentConversation(context, '建类', options, {
      ontology_propose: { execute },
    })
    conversation.prepareExchange(current)
    await expect(
      conversation.acceptResponse(
        1,
        response({ choices: toolChoice, ...change }),
        current,
        signal(),
      ),
    ).rejects.toThrow('PROVIDER_DRIFT')
    expect(execute).not.toHaveBeenCalled()
    expect(conversation.state()).toMatchObject({ phase: 'failed', error: 'PROVIDER_DRIFT' })
  })
  it.each(['drift', 'output-overrun'])(
    'preserves prior completed draft after %s',
    async (failure) => {
      const execute = vi.fn(async () => draft)
      const conversation = new AgentConversation(context, '建类', options, {
        ontology_propose: { execute },
      })
      conversation.prepareExchange(current)
      await conversation.acceptResponse(1, response({ choices: toolChoice }), current, signal())
      const prior = conversation.state().localReceipts
      expect(prior[0].outcome).toMatchObject({ kind: 'draft', requiresHumanDiffConfirmation: true })
      conversation.prepareExchange(current)
      const changed =
        failure === 'drift'
          ? { model: 'other-model' }
          : { usage: { prompt_tokens: 10, completion_tokens: 33, total_tokens: 43 } }
      await expect(
        conversation.acceptResponse(
          2,
          response({ id: 'response2', ...changed }),
          current,
          signal(),
        ),
      ).rejects.toThrow(failure === 'drift' ? 'PROVIDER_DRIFT' : 'INVALID_PROTOCOL')
      expect(conversation.state().localReceipts).toEqual(prior)
      expect(conversation.state().requestedTokenCeiling).toBe(64)
      expect(execute).toHaveBeenCalledTimes(1)
    },
  )
  it.each([undefined, null])(
    'rejects missing enabled response reasoning without tools: %s',
    async (reasoning) => {
      const conversation = new AgentConversation(context, '提示', options)
      conversation.prepareExchange(current)
      const choices = [
        {
          index: 0,
          finish_reason: 'stop',
          message: {
            role: 'assistant',
            content: '{"kind":"uncertain"}',
            reasoning_content: reasoning,
          },
        },
      ]
      await expect(
        conversation.acceptResponse(1, response({ choices }), current, signal()),
      ).rejects.toThrow('INVALID_PROTOCOL')
    },
  )
  it('keeps disabled response and tool-free historical replay rules distinct', async () => {
    const disabled = {
      ...options,
      mode: 'disabled',
      expectedProviderSignature: { ...signature, mode: 'disabled' },
    }
    const conversation = new AgentConversation(context, '提示', disabled)
    expect(conversation.prepareExchange(current).body).not.toHaveProperty('reasoning_effort')
    const choices = [
      {
        index: 0,
        finish_reason: 'stop',
        message: { role: 'assistant', content: '{"kind":"uncertain"}' },
      },
    ]
    expect(
      (await conversation.acceptResponse(1, response({ choices }), current, signal())).state.phase,
    ).toBe('answered')
    expect(
      encodeChatRequest({
        messages: [
          { role: 'system', content: AGENT_SYSTEM_PROMPT },
          { role: 'user', content: '提示' },
          { role: 'assistant', content: '{"kind":"uncertain"}' },
          { role: 'user', content: '继续' },
        ],
        mode: 'enabled',
        effort: 'high',
        availableTools: [],
        maxTokens: 32,
      }).thinking,
    ).toEqual({ type: 'enabled' })
  })
  it('rejects reported output overrun before tools without treating input tokens as output budget', async () => {
    const execute = vi.fn(async () => draft)
    const conversation = new AgentConversation(
      context,
      '建类',
      { ...options, maxTokens: 1 },
      { ontology_propose: { execute } },
    )
    conversation.prepareExchange(current)
    await expect(
      conversation.acceptResponse(
        1,
        response({
          choices: toolChoice,
          usage: { prompt_tokens: 10, completion_tokens: 100, total_tokens: 110 },
        }),
        current,
        signal(),
      ),
    ).rejects.toThrow('INVALID_PROTOCOL')
    expect(execute).not.toHaveBeenCalled()
    const valid = new AgentConversation(context, '提示', {
      ...options,
      maxTokens: 1,
      maxTotalRequestedTokens: 1,
    })
    valid.prepareExchange(current)
    expect(
      (
        await valid.acceptResponse(
          1,
          response({ usage: { prompt_tokens: 10000, completion_tokens: 1, total_tokens: 10001 } }),
          current,
          signal(),
        )
      ).state.phase,
    ).toBe('answered')
    expect(valid.state().requestedTokenCeiling).toBe(1)
  })
  it.each([
    'TIMED_OUT',
    'CANCELLED',
    'STALE_CONTEXT',
    'INVALID_TOOL_ARGUMENTS',
    'BUSY',
    'PROVIDER_DRIFT',
  ] as const)('projects only a fixed safe failure code: %s', (code) => {
    expect(
      projectToolMessage(
        { callId: 'c1', tool: 'query_execute', outcome: { kind: 'failure', code } },
        [],
      ).content,
    ).toBe(JSON.stringify({ kind: 'failure', code }))
  })
  it('does not externalize forged error codes or private draft bodies', () => {
    const secret = 'secret/path/private-cell'
    const receipt = {
      callId: 'c1',
      tool: 'query_execute',
      outcome: { kind: 'failure', code: secret },
    } as unknown as ToolReceipt
    expect(projectToolMessage(receipt, []).content).toBe('{"kind":"failure","code":"TOOL_FAILED"}')
    expect(new AgentError(secret as AgentErrorCode).message).toBe('TOOL_FAILED')
    expect(
      projectToolMessage(
        {
          callId: 'c2',
          tool: 'ontology_propose',
          outcome: { ...draft, kind: 'draft', draftType: 'ontology', detail: secret },
        },
        [],
      ).content,
    ).toBe('{"kind":"draft"}')
  })
  it.each(['mutated-code', 'throwing-getter'])(
    'normalizes an adapter-owned AgentError before local receipt storage: %s',
    async (variant) => {
      const error = new AgentError('TIMED_OUT')
      if (variant === 'mutated-code') Reflect.set(error, 'code', 'secret/path/private-cell')
      else
        Object.defineProperty(error, 'code', {
          get: () => {
            throw Error('secret getter')
          },
        })
      const session = new AgentSession(context, {
        ontology_propose: {
          execute: async () => {
            throw error
          },
        },
      })
      const receipts = await session.executeCalls([call], current, signal())
      expect(receipts).toEqual([
        {
          callId: call.id,
          tool: 'ontology_propose',
          outcome: { kind: 'failure', code: 'TOOL_FAILED' },
        },
      ])
      expect(session.currentTurnReceipts()).toEqual(receipts)
      expect(JSON.stringify(receipts)).not.toContain('secret')
    },
  )
  it('detects duplicate call IDs before invalid later arguments with zero execution', async () => {
    const execute = vi.fn(async () => draft)
    const session = new AgentSession(context, { ontology_propose: { execute } })
    await expect(
      session.executeCalls(
        [call, { ...call, function: { ...call.function, arguments: '{}' } }],
        current,
        signal(),
      ),
    ).rejects.toThrow('INVALID_PROTOCOL')
    expect(execute).not.toHaveBeenCalled()
    expect(() =>
      encodeChatRequest({
        messages: [
          { role: 'system', content: AGENT_SYSTEM_PROMPT },
          { role: 'user', content: '建类' },
          { role: 'assistant', content: null, reasoning_content: 'test', tool_calls: [call] },
          { role: 'tool', content: '{}', tool_call_id: call.id },
          { role: 'assistant', content: null, reasoning_content: 'test', tool_calls: [call] },
          { role: 'tool', content: '{}', tool_call_id: call.id },
        ],
        mode: 'enabled',
        effort: 'high',
        availableTools: ['ontology_propose'],
        maxTokens: 32,
      }),
    ).toThrow('INVALID_PROTOCOL')
  })
})
