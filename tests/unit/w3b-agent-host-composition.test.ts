import { randomUUID } from 'node:crypto'
import { mkdtemp, rm, stat } from 'node:fs/promises'
import { join } from 'node:path'
import { describe, expect, it, vi } from 'vitest'
import type { AgentDispatchArgs, AgentPrivacy, BridgeResult } from '@ontolearn/contracts'
import { AgentModeStore } from '../../apps/desktop/src/main/agent/agent-mode-store'
import { AgentHostComposition } from '../../apps/desktop/src/main/agent/host-composition'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import { MainlineReplyReceipt } from '../../apps/desktop/src/main/engine'

type Dependencies = ConstructorParameters<typeof AgentHostComposition>[0]
const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
function reply(message: object, id: string, toolCalls = false) {
  return JSON.stringify({
    id,
    object: 'chat.completion',
    created: 0,
    model: REQUEST_MODEL,
    choices: [
      {
        index: 0,
        finish_reason: toolCalls ? 'tool_calls' : 'stop',
        message: { role: 'assistant', ...message },
      },
    ],
  })
}

function fixture(privacy: AgentPrivacy = 'project', approved = true) {
  const projectId = randomUUID()
  const operationId = randomUUID()
  const args: AgentDispatchArgs = {
    operationId,
    question: '请检验已选结果',
    module: 'query',
    mode: 'tutor',
    scope: 'asserted',
    selectedObjectIds: ['result-1'],
  }
  const selection = {
    owner: {},
    selectionSeq: 1,
    engineSessionId: 'session',
    project: {
      projectId,
      projectRevision: 3,
      inputSnapshotId: 'snap-3',
      formatVersion: 3 as const,
      dependencyVector: {},
    },
  }
  const invokeAgentBody =
    vi.fn<NonNullable<ReturnType<Dependencies['models']>>['invokeAgentBody']>()
  const providerApproval: Dependencies['providerApproval'] = {
    configurationId: randomUUID(),
    configurationVersion: randomUUID(),
    confirmBody: async () => true,
    signature: {
      endpoint: DEEPSEEK_ENDPOINT,
      requestedModel: REQUEST_MODEL,
      returnedModel: REQUEST_MODEL,
      fingerprint: null,
      codecVersion: CODEC_VERSION,
      mode: 'disabled',
      effort: 'low',
    },
  }
  const getResult = vi.fn<Dependencies['tasks']['getResult']>()
  const receipt = new (class extends MainlineReplyReceipt {})()
  const dependencies: Dependencies = {
    selection: () => selection,
    blocked: () => false,
    modes: new AgentModeStore(),
    providerApproval: approved ? providerApproval : undefined,
    replies: { receive: async (work) => ({ value: await work(), receipt }), consume: vi.fn() },
    tasks: { getResult, getJob: vi.fn() },
    projects: {
      readProject: vi.fn(),
      recordAgentBeforeCommit: vi.fn(),
      commitProjectChangeSet: vi.fn(),
      getProjectQualityState: vi.fn(),
      runProjectQualityCheck: vi.fn(),
      queries: {
        loadQueryDefinition: vi.fn(),
        executeSavedQuery: vi.fn(),
        getQueryResultDescriptor: vi.fn(),
      },
    },
    models: () => ({
      status: () => ({
        availability: 'ready',
        contextId: 'context',
        projectId,
        privacy,
        configurations: [],
        selections: [],
        invocations: [],
      }),
      agentReady: () => privacy !== 'local' && approved,
      invokeAgentBody,
      listConfigurationSummaries: () => [],
      setConfigurationEnabled: vi.fn(),
      removeConfiguration: vi.fn(),
      probeCapabilities: vi.fn(),
      listAuditEntries: vi.fn(),
    }),
  }
  return {
    host: new AgentHostComposition(dependencies),
    args,
    projectId,
    selection,
    invokeAgentBody,
    getResult,
    dependencies,
  }
}

describe('Agent host composition', () => {
  it.each([
    ['local', true, 'LOCAL_ONLY'],
    ['project', false, 'MODEL_UNAVAILABLE'],
  ] as const)(
    'retains the original question under %s privacy with approval %s',
    async (privacy, approved, failureCode) => {
      const { host, args, invokeAgentBody } = fixture(privacy, approved)
      expect(await host.dispatchAgentQuestion(args)).toMatchObject({ ok: true })
      expect(await host.getAgentState()).toMatchObject({
        data: { status: 'failed', failureCode, retainedQuestion: args.question, receipts: [] },
      })
      expect(invokeAgentBody).not.toHaveBeenCalled()
    },
  )
  it('preserves all receipts and projects no raw tool rows, errors or provider call ids into the next request', async () => {
    const { host, args, invokeAgentBody, getResult } = fixture()
    const callId = '/Users/private/provider-call'
    getResult.mockResolvedValue({
      ok: false,
      error: {
        code: 'INTERNAL_ERROR',
        messageKey: 'internal',
        params: { path: '/Users/private/engine' },
        retryable: false,
      },
    })
    invokeAgentBody.mockResolvedValueOnce(
      reply(
        {
          content: null,
          tool_calls: [
            {
              id: callId,
              type: 'function',
              function: { name: 'result_read', arguments: '{"resultId":"result-1"}' },
            },
            {
              id: 'other',
              type: 'function',
              function: { name: 'result_read', arguments: '{"resultId":"unselected"}' },
            },
          ],
        },
        'r1',
        true,
      ),
    )
    invokeAgentBody.mockResolvedValueOnce(
      reply(
        {
          content: JSON.stringify({ kind: 'evidence', callIds: [callId] }),
        },
        'r2',
      ),
    )
    await host.dispatchAgentQuestion(args)
    await vi.waitFor(async () =>
      expect(await host.getAgentState()).toMatchObject({
        data: {
          status: 'answered',
          answerText: null,
          receipts: [
            { outcome: { kind: 'failure', code: 'TOOL_FAILED' } },
            { outcome: { kind: 'failure', code: 'TOOL_NOT_ALLOWED' } },
          ],
        },
      }),
    )
    expect(getResult).toHaveBeenCalledExactlyOnceWith('result-1')
    const body = JSON.parse(invokeAgentBody.mock.calls[1][0].body)
    expect(
      body.messages
        .filter((message: { role: string }) => message.role === 'tool')
        .map((message: { content: string }) => JSON.parse(message.content)),
    ).toEqual([
      { kind: 'failure', code: 'TOOL_FAILED' },
      { kind: 'failure', code: 'TOOL_NOT_ALLOWED' },
    ])
    expect(JSON.stringify(await host.getAgentState())).not.toContain('/Users/private/')
    expect(JSON.stringify(body)).not.toContain('/Users/private/engine')
  })
  it('rejects a response after either the revision or snapshot changes', async () => {
    for (const change of ['revision', 'snapshot'] as const) {
      const { host, args, selection, invokeAgentBody } = fixture()
      let respond!: (result: string) => void
      invokeAgentBody.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            respond = resolve
          }),
      )
      await host.dispatchAgentQuestion(args)
      if (change === 'revision') selection.project.projectRevision++
      else selection.project.inputSnapshotId = 'new-snapshot'
      host.refresh()
      const signal = invokeAgentBody.mock.calls[0][2]
      expect(signal.aborted).toBe(true)
      respond(reply({ content: '{"kind":"uncertain"}' }, 'late'))
      expect(await host.getAgentState()).toMatchObject({
        data: {
          status: 'failed',
          failureCode: 'STALE_CONTEXT',
          retainedQuestion: args.question,
          receipts: [],
        },
      })
      expect(await host.buildAgentDraftPlan({ operationId: args.operationId })).toMatchObject({
        error: { code: 'STALE_CONTEXT' },
      })
    }
  })
  it('rejects a mismatched cancellation id and fences old data when an owner changes', async () => {
    const { host, args, invokeAgentBody, selection } = fixture()
    invokeAgentBody.mockImplementationOnce(() => new Promise(() => {}))
    const result = await host.dispatchAgentQuestion(args)
    if (!result.ok) throw new Error(result.error.code)
    expect(
      await host.cancelAgentExchange({ exchangeId: result.data.exchangeId + 1 }),
    ).toMatchObject({
      error: { code: 'STALE_CONTEXT' },
    })
    const signal = invokeAgentBody.mock.calls[0][2]
    expect(signal.aborted).toBe(false)
    selection.project.projectId = randomUUID()
    host.refresh()
    expect(signal.aborted).toBe(true)
    expect(await host.getAgentState()).toEqual(
      ok(expect.objectContaining({ status: 'idle', retainedQuestion: null })),
    )
  })
  it('persists the project presentation preference and leaves other project IDs on tutor', async () => {
    const directory = await mkdtemp(join(process.cwd(), 'build', 'w3b-mode-'))
    try {
      const file = join(directory, 'agent', 'modes.json')
      const { dependencies, projectId } = fixture()
      const host = new AgentHostComposition({ ...dependencies, modes: new AgentModeStore(file) })
      expect(await host.setAgentMode({ projectId, mode: 'project' })).toEqual(
        ok({ projectId, mode: 'project' }),
      )
      const restored = new AgentModeStore(file)
      expect(restored.get(projectId)).toBe('project')
      expect(restored.get(randomUUID())).toBe('tutor')
      expect((await stat(file)).mode & 0o777).toBe(0o600)
      const otherId = randomUUID()
      expect(await host.setAgentMode({ projectId: otherId, mode: 'project' })).toMatchObject({
        error: { code: 'STALE_CONTEXT' },
      })
      expect(restored.get(otherId)).toBe('tutor')
    } finally {
      await rm(directory, { recursive: true, force: true })
    }
  })
})
