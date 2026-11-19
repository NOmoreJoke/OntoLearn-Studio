import type { IpcMain, IpcMainInvokeEvent } from 'electron'
import {
  agentIpcArgumentSchemas,
  internalError,
  modelInvalidRequestError,
  safeError,
  type AgentBridge,
  type AgentContextDTO,
  type AgentIpcMap,
  type AgentStateDTO,
} from '@ontolearn/contracts'
import type { ZodType } from 'zod'

export function registerAgentIpc({
  ipcMain,
  trusted,
  switching,
  blocked,
  getAgent,
}: {
  ipcMain: Pick<IpcMain, 'handle'>
  trusted: (event: IpcMainInvokeEvent) => boolean
  switching: () => boolean
  blocked: () => boolean
  getAgent?: () => AgentBridge | undefined
}): void {
  const permission = () => ({
    ok: false as const,
    error: safeError({
      code: 'PERMISSION_DENIED',
      messageKey: 'permission.denied',
      params: {},
      retryable: false,
    }),
  })
  const unavailable = (code: 'MODEL_UNAVAILABLE' | 'TOOL_UNAVAILABLE') => ({
    ok: false as const,
    error: {
      code,
      messageKey: code === 'MODEL_UNAVAILABLE' ? 'agent.modelUnavailable' : 'agent.toolUnavailable',
      params: {},
      retryable: false,
    },
  })
  const registerAgent = <Channel extends keyof AgentIpcMap>(
    channel: Channel,
    schema: ZodType<AgentIpcMap[Channel]['args'][0]>,
    handle: (
      service: AgentBridge | undefined,
      args: AgentIpcMap[Channel]['args'][0],
    ) => AgentIpcMap[Channel]['result'] | Promise<AgentIpcMap[Channel]['result']>,
    blockedDuringRecovery = false,
  ): void => {
    ipcMain.handle(channel, async (event, ...raw: unknown[]) => {
      if (!trusted(event) || switching() || (blockedDuringRecovery && blocked()))
        return permission()
      const parsed = schema.safeParse(raw[0])
      if (raw.length > 1 || !parsed.success) return { ok: false, error: modelInvalidRequestError() }
      try {
        return await handle(getAgent?.(), parsed.data)
      } catch {
        return { ok: false, error: internalError }
      }
    })
  }
  registerAgent('agent:context', agentIpcArgumentSchemas['agent:context'], (agent, args) => {
    if (agent) return agent.getAgentContext(args)
    const data: AgentContextDTO = {
      projectId: null,
      projectRevision: null,
      inputSnapshotId: null,
      scopeRef: null,
      module: args?.module ?? 'learn',
      mode: 'tutor',
      selectedObjectIds: [],
      privacy: 'local',
      modelReady: false,
      capabilities: {
        connection: 'not-run',
        structuredOutput: 'not-run',
        toolRoundTrip: 'not-run',
        mode: 'unverified',
      },
      configurations: [],
    }
    return { ok: true, data }
  })
  registerAgent(
    'agent:set-mode',
    agentIpcArgumentSchemas['agent:set-mode'],
    (agent, args) => agent?.setAgentMode(args) ?? unavailable('TOOL_UNAVAILABLE'),
    true,
  )
  registerAgent(
    'agent:dispatch',
    agentIpcArgumentSchemas['agent:dispatch'],
    (agent, args) => agent?.dispatchAgentQuestion(args) ?? unavailable('MODEL_UNAVAILABLE'),
    true,
  )
  registerAgent('agent:state', agentIpcArgumentSchemas['agent:state'], (agent, args) => {
    if (agent) return agent.getAgentState(args)
    const data: AgentStateDTO = {
      operationId: null,
      exchangeId: null,
      status: 'idle',
      context: null,
      receipts: [],
      retainedQuestion: null,
      answerText: null,
      failureCode: null,
    }
    return { ok: true, data }
  })
  registerAgent(
    'agent:cancel',
    agentIpcArgumentSchemas['agent:cancel'],
    (agent, args) => agent?.cancelAgentExchange(args) ?? unavailable('TOOL_UNAVAILABLE'),
  )
  registerAgent(
    'agent:draft-plan',
    agentIpcArgumentSchemas['agent:draft-plan'],
    (agent, args) => agent?.buildAgentDraftPlan(args) ?? unavailable('TOOL_UNAVAILABLE'),
  )
  registerAgent(
    'agent:commit-draft',
    agentIpcArgumentSchemas['agent:commit-draft'],
    (agent, args) => agent?.commitAgentDraft(args) ?? unavailable('TOOL_UNAVAILABLE'),
    true,
  )
  registerAgent(
    'agent:audit',
    agentIpcArgumentSchemas['agent:audit'],
    (agent, args) => agent?.listAgentAudit(args) ?? { ok: true, data: { items: [] } },
  )
  registerAgent(
    'agent-model:set-enabled',
    agentIpcArgumentSchemas['agent-model:set-enabled'],
    (agent, args) => agent?.setModelConfigurationEnabled(args) ?? unavailable('MODEL_UNAVAILABLE'),
    true,
  )
  registerAgent(
    'agent-model:remove',
    agentIpcArgumentSchemas['agent-model:remove'],
    (agent, args) => agent?.removeModelConfiguration(args) ?? unavailable('MODEL_UNAVAILABLE'),
    true,
  )
  registerAgent(
    'agent-model:probe',
    agentIpcArgumentSchemas['agent-model:probe'],
    (agent, args) => agent?.probeModelCapabilities(args) ?? unavailable('MODEL_UNAVAILABLE'),
    true,
  )
}
