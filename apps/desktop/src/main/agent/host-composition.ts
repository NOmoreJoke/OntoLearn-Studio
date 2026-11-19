import { createHash, randomUUID } from 'node:crypto'
import { isDeepStrictEqual } from 'node:util'
import {
  agentModeSchema,
  type AgentBridge,
  type AgentCapabilitiesDTO,
  type AgentCommitDraftArgs,
  type AgentCommitDraftResultDTO,
  type AgentContextDTO,
  type AgentDispatchArgs,
  type AgentDraftPlanDTO,
  type AgentMode,
  type AgentModule,
  type AgentPurpose,
  type AgentReceiptDTO,
  type AgentStateDTO,
  type BridgeResult,
  type ChangeSetConfirmation,
  type ChangeSetPreview,
  type MainlinePreviewArgs,
  type ProjectView,
} from '@ontolearn/contracts'
import type { MainlineReplyReceiver } from '../engine'
import {
  unverifiedCapabilities,
  type AgentProviderApproval,
  type ModelGatewayService,
} from '../model-gateway/model-service'
import { GatewayFailure } from '../model-gateway/policy'
import type { ProjectMainlineService } from '../project-mainline-service'
import type { TaskService } from '../task-service'
import { AgentModeStore } from './agent-mode-store'
import { assertDraftBase, contextSchema, type TrustedContext } from './agent-service'
import { AgentConversation } from './conversation'
import { AgentToolRegistry, draftDetailToPlan } from './domain-ports'
import { AgentError, normalizeAgentError } from './errors'

type Selection = {
  project: ProjectView
  owner: object
  engineSessionId: string
  selectionSeq: number
}
type Projects = Pick<
  ProjectMainlineService,
  | 'readProject'
  | 'getProjectQualityState'
  | 'runProjectQualityCheck'
  | 'recordAgentBeforeCommit'
  | 'commitProjectChangeSet'
> & {
  queries: Pick<
    ProjectMainlineService['queries'],
    'loadQueryDefinition' | 'executeSavedQuery' | 'getQueryResultDescriptor'
  >
}
type Models = Pick<
  ModelGatewayService,
  | 'status'
  | 'agentReady'
  | 'invokeAgentBody'
  | 'listConfigurationSummaries'
  | 'setConfigurationEnabled'
  | 'removeConfiguration'
  | 'probeCapabilities'
  | 'listAuditEntries'
>
type Dependencies = {
  modes: AgentModeStore
  selection(): Selection | null
  blocked(): boolean
  projects: Projects
  tasks: Pick<TaskService, 'getJob' | 'getResult'>
  replies: Pick<MainlineReplyReceiver, 'receive' | 'consume'>
  models(): Models | undefined
  providerApproval?: AgentProviderApproval
  onStateChange?: (state: AgentStateDTO) => void
}
type Turn = {
  state: AgentStateDTO
  selection: Selection
  context: TrustedContext
  controller: AbortController
  conversation?: AgentConversation
}
type DraftBinding = {
  turn: Turn
  draft: AgentDraftPlanDTO
  preview?: Extract<ChangeSetPreview, { status: 'ready' }>
  confirmation?: ChangeSetConfirmation
  pending?: Promise<BridgeResult<AgentCommitDraftResultDTO>>
  committed?: AgentCommitDraftResultDTO
  label?: string | null
}

const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
const failed = (code: string): BridgeResult<never> => ({
  ok: false,
  error: { code, messageKey: `agent.${code.toLowerCase()}`, params: {}, retryable: false },
})
const errorCode = (error: unknown) =>
  error instanceof GatewayFailure ? error.code : normalizeAgentError(error).code
const idle = (): AgentStateDTO => ({
  operationId: null,
  exchangeId: null,
  status: 'idle',
  context: null,
  receipts: [],
  retainedQuestion: null,
  answerText: null,
  failureCode: null,
})
const safeId = /^[A-Za-z0-9:_-]{1,128}$/
const scopeToken = (value: string) =>
  safeId.test(value) ? value : 'selected-' + createHash('sha256').update(value).digest('hex')
// Full assistance is always attributed to an explicit task list: the ontology
// draft targets and nothing else, so unrelated transfer attempts are never
// swept in when the caller omits taskIds (B05).
const defaultFullAssistanceTaskIds = ['business-ontology', 'transfer-repair'] as const

export function deriveBeforeCommitOp(operationId: string): string {
  const hash = createHash('sha256')
    .update('before-agent:' + operationId)
    .digest('hex')
  return `${hash.slice(0, 8)}-${hash.slice(8, 12)}-4${hash.slice(13, 16)}-8${hash.slice(17, 20)}-${hash.slice(20, 32)}`
}

export class AgentHostComposition implements AgentBridge {
  private turn?: Turn
  private draft?: DraftBinding
  private nextExchangeId = 0
  private closed = false
  private readonly probes = new Map<string, { version: string; value: AgentCapabilitiesDTO }>()

  constructor(private readonly dependencies: Dependencies) {}

  private selected(projectId?: string | null): Selection | null {
    const selection = this.closed ? null : this.dependencies.selection()
    if (projectId != null && selection?.project.projectId !== projectId)
      throw new AgentError('STALE_CONTEXT')
    return selection
  }

  private current(turn: Turn): boolean {
    const current = this.selected()
    return (
      !this.dependencies.blocked() &&
      this.turn === turn &&
      current?.owner === turn.selection.owner &&
      current?.selectionSeq === turn.selection.selectionSeq &&
      current?.engineSessionId === turn.selection.engineSessionId &&
      current?.project.projectId === turn.context.projectId &&
      current.project.projectRevision === turn.context.projectRevision &&
      current.project.inputSnapshotId === turn.context.inputSnapshotId &&
      this.dependencies.modes.get(turn.context.projectId) === turn.context.mode
    )
  }

  private assertCurrent(turn: Turn): void {
    if (!this.current(turn)) throw new AgentError('STALE_CONTEXT')
    if (turn.controller.signal.aborted) throw new AgentError('CANCELLED')
  }

  /** Revoke old exchanges synchronously on project, engine or library lifecycle changes. */
  refresh(clear = false): void {
    const turn = this.turn
    if (!turn || (!clear && this.current(turn))) return
    turn.controller.abort()
    turn.conversation?.cancel()
    // A project switch must not expose the previous project's question or receipts.
    if (clear || this.selected()?.project.projectId !== turn.context.projectId) {
      this.turn = undefined
      this.draft = undefined
    } else if (turn.state.status === 'dispatching' || turn.state.status === 'answered') {
      this.failTurn(turn, 'STALE_CONTEXT')
    }
  }

  close(): void {
    this.refresh(true)
    this.closed = true
  }

  private modelService(): Models {
    const models = this.dependencies.models()
    if (this.closed || !models) throw new GatewayFailure('MODEL_UNAVAILABLE')
    return models
  }

  private context(
    selection: Selection | null,
    module: AgentModule,
    selectedObjectIds: string[],
    scopeRef: string | null,
  ): AgentContextDTO {
    const models = this.dependencies.models()
    const status = models?.status()
    const project = selection?.project
    const privacy = project && status?.projectId === project.projectId ? status.privacy : 'local'
    const configurations = models?.listConfigurationSummaries() ?? []
    const approval = this.dependencies.providerApproval
    const modelReady = Boolean(project && models?.agentReady(project.projectId, approval))
    const probe = configurations
      .map((configuration) => ({
        configuration,
        probe: this.probes.get(configuration.configurationId),
      }))
      .find(
        ({ configuration, probe }) =>
          configuration.enabled && probe?.version === configuration.configurationVersion,
      )?.probe
    return {
      projectId: project?.projectId ?? null,
      projectRevision: project?.projectRevision ?? null,
      inputSnapshotId: project?.inputSnapshotId ?? null,
      module,
      selectedObjectIds,
      scopeRef,
      privacy,
      modelReady,
      configurations,
      mode: project ? this.dependencies.modes.get(project.projectId) : 'tutor',
      capabilities: modelReady
        ? {
            connection: 'passed',
            structuredOutput: 'passed',
            toolRoundTrip: 'passed',
            mode: 'provider-verified',
          }
        : { ...(probe?.value ?? unverifiedCapabilities) },
    }
  }

  async getAgentContext(args: Parameters<AgentBridge['getAgentContext']>[0] = {}) {
    try {
      const selection = this.selected(args.projectId)
      const turn = this.turn
      const live = turn && this.current(turn) ? turn.state.context : undefined
      return ok(
        this.context(
          selection,
          args.module ?? live?.module ?? 'learn',
          args.selectedObjectIds ?? live?.selectedObjectIds ?? [],
          args.selectedObjectIds || args.module ? null : (live?.scopeRef ?? null),
        ),
      )
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async setAgentMode({ projectId, mode }: { projectId: string; mode: AgentMode }) {
    try {
      this.selected(projectId)
      if (this.dependencies.blocked()) throw new AgentError('STALE_CONTEXT')
      this.dependencies.modes.set(projectId, agentModeSchema.parse(mode))
      this.refresh()
      return ok({ projectId, mode })
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async getAgentState(args: Parameters<AgentBridge['getAgentState']>[0] = {}) {
    try {
      this.selected(args.projectId)
      this.refresh()
      return ok(structuredClone(this.turn?.state ?? idle()))
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async listAgentAudit(args: Parameters<AgentBridge['listAgentAudit']>[0] = {}) {
    try {
      const selection = this.selected(args.projectId)
      const models = this.dependencies.models()
      if (!selection || !models) return ok({ items: [] })
      const items = await models.listAuditEntries(selection.project.projectId, args.limit ?? 20)
      const current = this.selected(selection.project.projectId)
      if (current?.owner !== selection.owner || current.selectionSeq !== selection.selectionSeq)
        throw new AgentError('STALE_CONTEXT')
      return ok({ items })
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async setModelConfigurationEnabled({
    configurationId,
    enabled,
  }: Parameters<AgentBridge['setModelConfigurationEnabled']>[0]) {
    try {
      return ok(await this.modelService().setConfigurationEnabled(configurationId, enabled))
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async removeModelConfiguration({
    configurationId,
  }: Parameters<AgentBridge['removeModelConfiguration']>[0]) {
    try {
      const removed = await this.modelService().removeConfiguration(configurationId)
      this.probes.delete(configurationId)
      return ok(removed)
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async probeModelCapabilities({
    configurationId,
    scope,
  }: Parameters<AgentBridge['probeModelCapabilities']>[0]) {
    try {
      const models = this.modelService()
      const configuration = models
        .listConfigurationSummaries()
        .find((value) => value.configurationId === configurationId)
      const value = models.probeCapabilities(configurationId, scope)
      if (configuration)
        this.probes.set(configurationId, { version: configuration.configurationVersion, value })
      return ok(value)
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  async dispatchAgentQuestion(args: AgentDispatchArgs) {
    try {
      this.refresh()
      const selection = this.selected()
      if (!selection || this.dependencies.blocked()) throw new AgentError('STALE_CONTEXT')
      if (this.turn?.state.status === 'dispatching' || this.draft?.pending)
        throw new AgentError('BUSY')
      const scopeRef = randomUUID()
      const objectIds = [...new Set(args.selectedObjectIds)]
      const objectRefs = new Map(objectIds.map((id) => [scopeToken(id), id]))
      const view = this.context(selection, args.module, objectIds, scopeRef)
      if (args.mode !== view.mode) throw new AgentError('STALE_CONTEXT')
      const context = contextSchema.parse({
        projectId: view.projectId,
        projectRevision: view.projectRevision,
        inputSnapshotId: view.inputSnapshotId,
        scopeRef,
        module: view.module,
        mode: view.mode,
        selectedObjectIds: [...objectRefs.keys()],
      })
      const state: AgentStateDTO = {
        ...idle(),
        context: view,
        operationId: args.operationId,
        exchangeId: ++this.nextExchangeId,
        status: 'dispatching',
        retainedQuestion: args.question,
      }
      const turn: Turn = { state, selection, context, controller: new AbortController() }
      this.turn = turn
      this.draft = undefined
      const approval = this.dependencies.providerApproval
      if (view.privacy === 'local') this.failTurn(turn, 'LOCAL_ONLY')
      else if (!approval || !view.modelReady) this.failTurn(turn, 'MODEL_UNAVAILABLE')
      else {
        const models = this.modelService()
        const ports = new AgentToolRegistry({
          projects: this.dependencies.projects,
          tasks: this.dependencies.tasks,
          receive: (work) => this.consume(work),
          scope: args.scope,
          current: () => this.current(turn),
          objectRefs,
        })
        const question = JSON.stringify({
          question: args.question,
          module: args.module,
          selectedObjectRefs: [...objectRefs.keys()],
          scope: args.scope,
          draftFormats: {
            ontology_propose: 'instruction: JSON {classIri, parentIri?}',
            query_draft:
              'question: JSON {kind:"query-draft",name,description,sparql,capabilityQuestion}',
          },
        })
        const { signature } = approval
        turn.conversation = new AgentConversation(
          context,
          question,
          {
            mode: signature.mode,
            effort: signature.effort,
            maxTokens: 2048,
            maxExchanges: 4,
            maxTotalRequestedTokens: 8192,
            toolTimeoutMs: 15000,
            projectedFieldIds: [],
            expectedProviderSignature: signature,
          },
          ports.buildPorts(),
        )
        void this.run(turn, models, approval)
      }
      return ok({ operationId: args.operationId, exchangeId: state.exchangeId! })
    } catch (error) {
      if (
        this.turn?.state.status === 'dispatching' &&
        this.turn.state.operationId === args.operationId &&
        !this.turn.conversation
      )
        this.failTurn(this.turn, errorCode(error))
      return failed(errorCode(error))
    }
  }

  async cancelAgentExchange(args: Parameters<AgentBridge['cancelAgentExchange']>[0] = {}) {
    const turn = this.turn
    if (args.exchangeId != null && args.exchangeId !== turn?.state.exchangeId)
      return failed('STALE_CONTEXT')
    if (turn?.state.status === 'dispatching') {
      turn.controller.abort()
      turn.conversation?.cancel()
      this.failTurn(turn, 'CANCELLED')
    }
    return this.getAgentState()
  }

  private async consume<T>(work: () => Promise<BridgeResult<T>>): Promise<BridgeResult<T>> {
    const { value, receipt } = await this.dependencies.replies.receive(work)
    this.dependencies.replies.consume(receipt)
    return value
  }

  private receipts(turn: Turn): AgentReceiptDTO[] {
    return (turn.conversation?.state().localReceipts ?? []).map(({ callId, tool, outcome }) => {
      const identity = {
        callId: createHash('sha256').update(callId).digest('hex'),
        tool,
        purpose: 'suggest' as const,
      }
      if (outcome.kind === 'draft') {
        return {
          ...identity,
          outcome: {
            ...outcome,
            projectId: turn.context.projectId,
            baseRevision: turn.context.projectRevision,
            inputSnapshotId: turn.context.inputSnapshotId,
            requiresHumanDiffConfirmation: true,
          },
        }
      }
      if (outcome.kind === 'failure') return { ...identity, outcome }
      return { ...identity, outcome }
    })
  }

  private failTurn(turn: Turn, code: string): void {
    turn.state.status = code === 'CANCELLED' ? 'cancelled' : 'failed'
    turn.state.failureCode = code
    turn.state.answerText = null
    turn.state.receipts = code === 'STALE_CONTEXT' ? [] : this.receipts(turn)
    this.dependencies.onStateChange?.(structuredClone(turn.state))
  }

  private async run(turn: Turn, models: Models, approval: AgentProviderApproval): Promise<void> {
    const conversation = turn.conversation!
    const signal = turn.controller.signal
    const read = () => (this.current(turn) ? turn.context : null)
    const purpose: AgentPurpose = 'suggest'
    try {
      while (true) {
        this.assertCurrent(turn)
        const exchange = conversation.prepareExchange(read)
        const response = await models.invokeAgentBody(
          {
            projectId: turn.context.projectId,
            purpose,
            body: JSON.stringify(exchange.body),
          },
          approval,
          signal,
          () => this.current(turn),
        )
        this.assertCurrent(turn)
        const { state } = await conversation.acceptResponse(
          exchange.exchangeId,
          response,
          read,
          signal,
        )
        this.assertCurrent(turn)
        turn.state.receipts = this.receipts(turn)
        if (state.phase !== 'answered' || !state.answer) continue
        turn.state.status = 'answered'
        const answer = state.answer
        turn.state.answerText =
          answer.kind === 'evidence'
            ? null
            : answer.kind === 'suggestion'
              ? answer.label + '\n' + answer.text
              : answer.text
        this.dependencies.onStateChange?.(structuredClone(turn.state))
        return
      }
    } catch (error) {
      if (this.turn === turn && turn.state.status === 'dispatching') {
        const code = this.current(turn) ? errorCode(error) : 'STALE_CONTEXT'
        this.failTurn(turn, code)
      }
      conversation.cancel()
    }
  }

  async buildAgentDraftPlan({ operationId }: { operationId: string }) {
    try {
      const turn = this.turn
      if (!turn || turn.state.operationId !== operationId) throw new AgentError('STALE_CONTEXT')
      this.assertCurrent(turn)
      const drafts = turn.state.receipts.flatMap(({ outcome }) =>
        outcome.kind === 'draft' ? [outcome] : [],
      )
      if (turn.state.status !== 'answered' || drafts.length !== 1)
        throw new AgentError('INVALID_EVIDENCE')
      const draft = drafts[0]
      assertDraftBase(draft, turn.context)
      if (!this.draft)
        this.draft = {
          turn,
          draft: {
            operationId,
            draftType: draft.draftType,
            baseRevision: draft.baseRevision,
            inputSnapshotId: draft.inputSnapshotId,
            summary: draft.summary,
            plan: draftDetailToPlan(draft.draftType, draft.detail),
          },
        }
      return ok(structuredClone(this.draft.draft))
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  /** Bind the actual named ChangeSet preview to this operation before accepting any confirmation. */
  observeDraftPreview(args: MainlinePreviewArgs, preview: ChangeSetPreview): void {
    const binding = this.draft
    // Compare structured DTO data across the host, reply receiver and IPC realms.
    if (
      !binding ||
      binding.confirmation ||
      !this.current(binding.turn) ||
      args.intent !== 'change' ||
      args.baseRevision !== binding.draft.baseRevision ||
      !isDeepStrictEqual(structuredClone(args.plan), structuredClone(binding.draft.plan)) ||
      preview.status !== 'ready' ||
      preview.intent !== 'change' ||
      preview.projectId !== binding.turn.context.projectId ||
      preview.baseRevision !== binding.draft.baseRevision ||
      preview.inputSnapshotId !== binding.draft.inputSnapshotId
    )
      return
    binding.preview = structuredClone(preview)
  }

  observeDraftConfirmation(confirmation: ChangeSetConfirmation): void {
    const binding = this.draft
    const preview = binding?.preview
    if (
      !binding ||
      !preview ||
      binding.confirmation ||
      !this.current(binding.turn) ||
      confirmation.projectId !== preview.projectId ||
      confirmation.previewHash !== preview.previewHash ||
      confirmation.inputSnapshotId !== preview.inputSnapshotId ||
      confirmation.preparedPlanRef !== preview.preparedPlanRef ||
      confirmation.parametersHash !== preview.parametersHash
    )
      return
    binding.confirmation = structuredClone(confirmation)
  }

  async commitAgentDraft(
    args: AgentCommitDraftArgs,
  ): Promise<BridgeResult<AgentCommitDraftResultDTO>> {
    try {
      const binding = this.draft
      if (
        !binding ||
        binding.draft.operationId !== args.operationId ||
        binding.draft.draftType !== args.draftType ||
        !isDeepStrictEqual(binding.confirmation, structuredClone(args.confirmation))
      )
        throw new AgentError('STALE_CONTEXT')
      const label = args.label ?? null
      if (binding.label !== undefined && binding.label !== label)
        throw new AgentError('STALE_CONTEXT')
      if (binding.committed) return ok(structuredClone(binding.committed))
      this.assertCurrent(binding.turn)
      if (!binding.pending) {
        binding.label = label
        binding.pending = this.persistDraft(binding, structuredClone(args))
      }
      try {
        return await binding.pending
      } finally {
        binding.pending = undefined
      }
    } catch (error) {
      return failed(errorCode(error))
    }
  }

  private async persistDraft(
    binding: DraftBinding,
    args: AgentCommitDraftArgs,
  ): Promise<BridgeResult<AgentCommitDraftResultDTO>> {
    const { projectId, mode } = binding.turn.context
    const { baseRevision, draftType } = binding.draft
    const operationId = deriveBeforeCommitOp(args.operationId)
    const checkpoint = await this.consume(() =>
      this.dependencies.projects.recordAgentBeforeCommit({
        projectId,
        operationId,
        baseRevision,
        recordFullAssistance: mode === 'project' && draftType === 'ontology',
        taskIds: args.taskIds ?? [...defaultFullAssistanceTaskIds],
        label: args.label ?? null,
      }),
    )
    this.assertCurrent(binding.turn)
    if (!checkpoint.ok) return failed('TOOL_FAILED')
    const receipt = checkpoint.data
    if (
      receipt.agentBeforeCommitVersion !== 1 ||
      receipt.reason !== 'before-agent' ||
      receipt.projectId !== projectId ||
      receipt.operationId !== operationId ||
      receipt.domainRevision !== baseRevision ||
      !safeId.test(receipt.checkpointRef) ||
      receipt.assistanceUpdatedTaskIds.some((id) => !safeId.test(id))
    )
      throw new AgentError('INVALID_EVIDENCE')
    const accepted = await this.consume(() =>
      this.dependencies.projects.commitProjectChangeSet({
        operationId: args.operationId,
        confirmation: args.confirmation,
      }),
    )
    if (!accepted.ok) return failed('TOOL_FAILED')
    if (
      accepted.data.projectId !== projectId ||
      accepted.data.operationId !== args.operationId ||
      accepted.data.inputSnapshotId !== args.confirmation.inputSnapshotId
    )
      throw new AgentError('INVALID_EVIDENCE')
    const result = {
      operationId: args.operationId,
      job: accepted.data,
      beforeAgentCheckpointRef: receipt.checkpointRef,
      reason: 'before-agent' as const,
      assistanceUpdatedTaskIds: receipt.assistanceUpdatedTaskIds,
    }
    binding.committed = structuredClone(result)
    if (this.selected()?.owner !== binding.turn.selection.owner || this.draft !== binding)
      throw new AgentError('STALE_CONTEXT')
    return ok(structuredClone(result))
  }
}
