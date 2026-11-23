import { z } from 'zod'
import type {
  BridgeResult,
  ChangeSetConfirmation,
  JobView,
  MainlineChangePlanDTO,
  QuerySelectionDTO,
} from './index'
import { validateBusiness3 } from './v2'

export const agentScopeSchema = z.enum(['asserted', 'asserted+derived'])
export const agentModuleSchema = z.enum([
  'learn',
  'ontology',
  'mapping',
  'query',
  'quality',
  'behavior',
  'scenario',
])
export const agentModeSchema = z.enum(['tutor', 'project'])
export const agentPrivacySchema = z.enum(['local', 'minimal', 'project'])
export const agentToolScopeSchema = z.enum(['asserted', 'asserted-and-derived', 'selected-history'])

export type AgentScope = z.infer<typeof agentScopeSchema>
export type AgentModule = z.infer<typeof agentModuleSchema>
export type AgentMode = z.infer<typeof agentModeSchema>
export type AgentPrivacy = z.infer<typeof agentPrivacySchema>
export type AgentToolScope = z.infer<typeof agentToolScopeSchema>

export function agentScopeToQueryScope(
  value: AgentToolScope,
  inputSnapshotId: string,
): { scope: AgentScope; selection: QuerySelectionDTO } {
  switch (value) {
    case 'asserted':
      return { scope: 'asserted', selection: { kind: 'current' } }
    case 'asserted-and-derived':
      return { scope: 'asserted+derived', selection: { kind: 'current' } }
    case 'selected-history':
      if (typeof inputSnapshotId !== 'string' || inputSnapshotId.trim().length === 0)
        throw new Error('AGENT_SNAPSHOT_REQUIRED')
      return { scope: 'asserted', selection: { kind: 'historical', snapshotId: inputSnapshotId } }
    default:
      throw new Error('AGENT_SCOPE_INVALID')
  }
}

export type AgentCapabilityStatus = 'passed' | 'failed' | 'not-run'
export type AgentCapabilitiesDTO = {
  connection: AgentCapabilityStatus
  structuredOutput: AgentCapabilityStatus
  toolRoundTrip: AgentCapabilityStatus
  mode: 'unverified' | 'synthetic' | 'provider-verified'
}

export type AgentModelConfigurationSummaryDTO = {
  configurationId: string
  configurationVersion: string
  displayName: string
  endpoint: string
  model: string
  credentialState: 'missing' | 'configured' | 'unavailable'
  enabled: boolean
}

export type AgentContextDTO = {
  projectId: string | null
  projectRevision: number | null
  inputSnapshotId: string | null
  scopeRef: string | null
  module: AgentModule
  mode: AgentMode
  selectedObjectIds: string[]
  privacy: AgentPrivacy
  modelReady: boolean
  capabilities: AgentCapabilitiesDTO
  configurations: AgentModelConfigurationSummaryDTO[]
}

export type AgentPurpose = 'explain' | 'suggest' | 'review'
const agentDraftTypeSchema = z.enum(['ontology', 'mapping', 'query'])
export type AgentDraftType = z.infer<typeof agentDraftTypeSchema>

export type AgentReceiptDTO = { callId: string; tool: string } & (
  | {
      purpose: 'suggest'
      outcome: {
        kind: 'draft'
        draftType: AgentDraftType
        summary: string
        detail: string
        projectId: string
        baseRevision: number
        inputSnapshotId: string
        requiresHumanDiffConfirmation: true
      }
    }
  | {
      purpose: AgentPurpose
      outcome: {
        kind: 'evidence'
        projectId: string
        inputSnapshotId: string
        scopeRef: string
        resultId: string
        status: 'current' | 'stale' | 'historical' | 'failed' | 'cancelled'
        traceRefs: string[]
        fields: Array<{ fieldId: string; value: string | number | boolean | null }>
      }
    }
  | { purpose: AgentPurpose; outcome: { kind: 'failure'; code: string } }
)

const projectId = z.uuidv4()
const operationId = z.uuidv4()
const configurationId = z.uuidv4()
const selectedObjectIds = z.array(z.string().min(1).max(128)).max(100)
const projectSelection = { projectId: projectId.nullable().optional() }
export const agentDispatchArgsSchema = z.strictObject({
  operationId,
  question: z
    .string()
    .max(16000)
    .refine((value) => value.trim().length > 0),
  module: agentModuleSchema,
  mode: agentModeSchema,
  selectedObjectIds,
  scope: agentScopeSchema,
  preferredAction: z.string().min(1).max(128).optional(),
})
export type AgentDispatchArgs = z.infer<typeof agentDispatchArgsSchema>
export type AgentDispatchResultDTO = { operationId: string; exchangeId: number }

export type AgentStateDTO = {
  operationId: string | null
  exchangeId: number | null
  status: 'idle' | 'dispatching' | 'answered' | 'failed' | 'cancelled'
  context: AgentContextDTO | null
  receipts: AgentReceiptDTO[]
  retainedQuestion: string | null
  answerText: string | null
  failureCode: string | null
}

export type AgentDraftPlanDTO = {
  operationId: string
  draftType: AgentDraftType
  baseRevision: number
  inputSnapshotId: string
  summary: string
  plan: MainlineChangePlanDTO
}

export const agentCommitDraftArgsSchema = z.strictObject({
  operationId,
  draftType: agentDraftTypeSchema,
  confirmation: z.custom<ChangeSetConfirmation>((value) =>
    validateBusiness3('result_changeset.confirm', value),
  ),
  label: z.string().min(1).max(256).nullable().optional(),
  taskIds: z.array(z.string().min(1).max(128)).max(32).optional(),
})
export type AgentCommitDraftArgs = z.infer<typeof agentCommitDraftArgsSchema>
export type AgentCommitDraftResultDTO = {
  operationId: string
  job: JobView
  beforeAgentCheckpointRef: string
  reason: 'before-agent'
  assistanceUpdatedTaskIds: string[]
}

export type AgentAuditRecordDTO = {
  eventId: string
  targetId: string
  endpointOrigin: string
  purpose: AgentPurpose
  scopes: string[]
  decision: 'authorized' | 'denied'
  event: 'attempt-intent' | 'blocked' | 'attempt-failed'
  time: string
}

export interface AgentBridge {
  getAgentContext(args?: {
    projectId?: string | null
    module?: AgentModule
    selectedObjectIds?: string[]
  }): Promise<BridgeResult<AgentContextDTO>>
  setAgentMode(args: {
    projectId: string
    mode: AgentMode
  }): Promise<BridgeResult<{ projectId: string; mode: AgentMode }>>
  dispatchAgentQuestion(args: AgentDispatchArgs): Promise<BridgeResult<AgentDispatchResultDTO>>
  getAgentState(args?: { projectId?: string | null }): Promise<BridgeResult<AgentStateDTO>>
  cancelAgentExchange(args?: { exchangeId?: number | null }): Promise<BridgeResult<AgentStateDTO>>
  buildAgentDraftPlan(args: { operationId: string }): Promise<BridgeResult<AgentDraftPlanDTO>>
  commitAgentDraft(args: AgentCommitDraftArgs): Promise<BridgeResult<AgentCommitDraftResultDTO>>
  listAgentAudit(args?: {
    projectId?: string | null
    limit?: number
  }): Promise<BridgeResult<{ items: AgentAuditRecordDTO[] }>>
  setModelConfigurationEnabled(args: {
    configurationId: string
    enabled: boolean
  }): Promise<BridgeResult<AgentModelConfigurationSummaryDTO>>
  removeModelConfiguration(args: {
    configurationId: string
  }): Promise<BridgeResult<{ configurationId: string; removed: true }>>
  probeModelCapabilities(args: {
    configurationId: string
    scope?: 'synthetic'
  }): Promise<BridgeResult<AgentCapabilitiesDTO>>
}

export const agentIpcMethods = Object.freeze({
  'agent:context': 'getAgentContext',
  'agent:set-mode': 'setAgentMode',
  'agent:dispatch': 'dispatchAgentQuestion',
  'agent:state': 'getAgentState',
  'agent:cancel': 'cancelAgentExchange',
  'agent:draft-plan': 'buildAgentDraftPlan',
  'agent:commit-draft': 'commitAgentDraft',
  'agent:audit': 'listAgentAudit',
  'agent-model:set-enabled': 'setModelConfigurationEnabled',
  'agent-model:remove': 'removeModelConfiguration',
  'agent-model:probe': 'probeModelCapabilities',
} as const satisfies Record<`agent:${string}` | `agent-model:${string}`, keyof AgentBridge>)

export type AgentIpcMap = {
  [Channel in keyof typeof agentIpcMethods]: {
    args: Parameters<AgentBridge[(typeof agentIpcMethods)[Channel]]>
    result: Awaited<ReturnType<AgentBridge[(typeof agentIpcMethods)[Channel]]>>
  }
}

export const agentIpcArgumentSchemas = {
  'agent:context': z
    .strictObject({
      ...projectSelection,
      module: agentModuleSchema.optional(),
      selectedObjectIds: selectedObjectIds.optional(),
    })
    .optional(),
  'agent:set-mode': z.strictObject({ projectId, mode: agentModeSchema }),
  'agent:dispatch': agentDispatchArgsSchema,
  'agent:state': z.strictObject(projectSelection).optional(),
  'agent:cancel': z.strictObject({ exchangeId: z.number().int().positive().nullish() }).optional(),
  'agent:draft-plan': z.strictObject({ operationId }),
  'agent:commit-draft': agentCommitDraftArgsSchema,
  'agent:audit': z
    .strictObject({
      ...projectSelection,
      limit: z.number().int().min(1).max(100).optional(),
    })
    .optional(),
  'agent-model:set-enabled': z.strictObject({ configurationId, enabled: z.boolean() }),
  'agent-model:remove': z.strictObject({ configurationId }),
  'agent-model:probe': z.strictObject({
    configurationId,
    scope: z.literal('synthetic').optional(),
  }),
} satisfies {
  [Channel in keyof AgentIpcMap]: z.ZodType<AgentIpcMap[Channel]['args'][0]>
}

/** Main-only business3 payload. Public checkpoint creation remains manual. */
export type AgentBeforeCommitArgs = {
  projectId: string
  operationId: string
  baseRevision: number
  recordFullAssistance: boolean
  taskIds?: string[]
  label: string | null
}
export type AgentBeforeCommitResultDTO = {
  agentBeforeCommitVersion: 1
  projectId: string
  operationId: string
  checkpointRef: string
  reason: 'before-agent'
  domainRevision: number
  assistanceUpdatedTaskIds: string[]
}
