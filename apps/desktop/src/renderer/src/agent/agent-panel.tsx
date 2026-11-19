/**
 * Workspace Agent panel.
 *
 * This is the only place that talks to the named Agent bridge. It:
 *  - reads the frozen `AgentContextDTO` / `AgentStateDTO` from the host,
 *  - dispatches a question, cancels an exchange and builds a draft plan,
 *  - renders at most four page quick actions through the shared policy, and
 *  - hands a validated `query` draft to the query workspace.
 *
 * It never writes project data by itself: an ontology draft only becomes a
 * reviewable diff through `buildAgentDraftPlan` and the change-set chain.
 *
 * Every answer of the host is bound to the project and the workspace
 * generation that asked for it: an outdated answer is dropped instead of
 * overwriting the current context, the current run state or the current
 * selection.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type {
  AgentContextDTO,
  AgentDraftPlanDTO,
  AgentMode,
  AgentReceiptDTO,
  AgentStateDTO,
} from '@ontolearn/contracts'
import { AgentSidebar } from './AgentSidebar'
import { contextActions, type AgentAction } from './context-actions'
import { draftSchema } from '../query/draft'
import type { QueryDraftDTO } from '../query/api002-source-types'
import type { SidebarState } from './sidebar-presentation'

export type AgentPanelProps = {
  /** Selected project; `null` keeps every project bound action disabled. */
  projectId: string | null
  /** Committed project revision of the selected project. */
  projectRevision: number | null
  /** Committed input snapshot of the selected project. */
  inputSnapshotId: string | null
  /** Current workspace module (frozen vocabulary). */
  module: AgentContextDTO['module']
  /** Current mode (frozen vocabulary). */
  mode: AgentMode
  /** Currently selected ontology objects, in selection order. */
  selectedObjectIds: string[]
  /** Offline actions this workspace can really serve. */
  localActions: readonly AgentAction[]
  /** Mode switch; the host persists it and mirrors it in local storage. */
  onModeChange?: (mode: AgentMode) => void | Promise<void>
  /** Receives a validated upstream query draft. */
  onQueryDraft?: (draft: QueryDraftDTO) => void
  /** Receives the host-built ontology draft plan for diff review. */
  onDraftPlan?: (plan: AgentDraftPlanDTO) => void
  /** Offline action handler (hint / check / demonstrate / explain). */
  onLocalAction?: (action: AgentAction) => void | Promise<void>
  /** Incremented whenever the model configuration changed upstream. */
  modelSyncVersion?: number
}

/**
 * Extract a query draft from a host-built change plan.
 * Only a `query` layer definition with a real descriptor is accepted.
 */
export function queryDraftFromPlan(plan: AgentDraftPlanDTO): QueryDraftDTO | undefined {
  const definition = plan.plan.definitions?.find(
    (value): value is Extract<typeof value, { layer: 'query' }> => value.layer === 'query',
  )
  if (!definition) return undefined
  const descriptor = definition.value.descriptor
  const parsed = draftSchema.safeParse({
    name: descriptor.name,
    description: descriptor.description,
    sparql: definition.value.text,
    scope: descriptor.scope,
    capabilityQuestion: descriptor.capabilityQuestion,
    source: 'model',
  })
  return parsed.success ? parsed.data : undefined
}

/**
 * Extract a query draft from a receipt detail payload.
 * The detail is untrusted text; only a fully valid draft is accepted.
 */
export function queryDraftFromDetail(detail: string): QueryDraftDTO | undefined {
  let value: unknown
  try {
    value = JSON.parse(detail)
  } catch {
    return undefined
  }
  const parsed = draftSchema.safeParse(value)
  return parsed.success ? { ...parsed.data, source: 'model' } : undefined
}

const take = <T,>(reply: { ok: true; data: T } | { ok: false; error: { code: string } }): T => {
  if (!reply.ok) throw new Error(reply.error.code)
  return reply.data
}

/** The error codes the sidebar can explain. Anything else is a tool failure. */
const knownErrorCodes = new Set([
  'INVALID_PROTOCOL',
  'INVALID_JSON',
  'INCOMPLETE_RESPONSE',
  'TOOL_NOT_ALLOWED',
  'TOOL_UNAVAILABLE',
  'INVALID_TOOL_ARGUMENTS',
  'INVALID_EVIDENCE',
  'STALE_CONTEXT',
  'BUDGET_EXCEEDED',
  'BUSY',
  'PROVIDER_DRIFT',
  'CANCELLED',
  'TIMED_OUT',
  'TOOL_FAILED',
])

/**
 * Map the real host run state onto the sidebar state.
 *
 * Only a run that really belongs to `expectedProjectId` is mapped; a foreign
 * run is never presented as the current result.
 */
export function agentDtoToSidebarState(
  dto: AgentStateDTO,
  expectedProjectId: string,
): SidebarState | null {
  const context = dto.context
  if (!context || context.projectId !== expectedProjectId) return null
  const phase =
    dto.status === 'idle'
      ? 'ready'
      : dto.status === 'dispatching'
        ? 'awaiting-provider'
        : dto.status
  const failure =
    dto.status === 'failed' || dto.status === 'cancelled'
      ? knownErrorCodes.has(dto.failureCode ?? '')
        ? (dto.failureCode as SidebarState['error'])
        : 'TOOL_FAILED'
      : null
  const answer =
    dto.status === 'answered' && dto.answerText
      ? ({
          kind: 'suggestion',
          label: '模型建议，未经确定性工具验证',
          text: dto.answerText,
        } as SidebarState['answer'])
      : null
  return {
    phase,
    exchanges: dto.exchangeId ?? 0,
    requestedTokenCeiling: 0,
    error: failure,
    inputContext: {
      projectId: context.projectId,
      projectRevision: context.projectRevision ?? 0,
      inputSnapshotId: context.inputSnapshotId ?? 'unavailable',
      scopeRef: context.scopeRef ?? 'unavailable',
      module: context.module,
      mode: context.mode,
      selectedObjectIds: [...context.selectedObjectIds],
    },
    localReceipts: [],
    answer,
  }
}

/** True when the host context really belongs to the selected project and module. */
export function agentContextMatches(
  context: AgentContextDTO | null,
  projectId: string | null,
  module: AgentContextDTO['module'],
): boolean {
  if (!context || !projectId) return false
  return context.projectId === projectId && context.module === module
}

export function AgentPanel(props: AgentPanelProps) {
  const {
    projectId,
    projectRevision,
    inputSnapshotId,
    module,
    mode,
    selectedObjectIds,
    modelSyncVersion,
  } = props
  const [context, setContext] = useState<AgentContextDTO | null>(null)
  const [state, setState] = useState<AgentStateDTO | null>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')
  const live = useRef(true)
  const refreshSeq = useRef(0)
  const dispatchSeq = useRef(0)
  const planSeq = useRef(0)
  // The last upstream query receipt that was already delivered.
  const lastQueryReceipt = useRef('')
  const pollTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const onQueryDraft = useRef(props.onQueryDraft)
  const onDraftPlan = useRef(props.onDraftPlan)
  const onLocalAction = useRef(props.onLocalAction)
  useEffect(() => {
    onQueryDraft.current = props.onQueryDraft
    onDraftPlan.current = props.onDraftPlan
    onLocalAction.current = props.onLocalAction
  })

  useEffect(() => {
    live.current = true
    return () => {
      live.current = false
      if (pollTimer.current !== undefined) clearTimeout(pollTimer.current)
      pollTimer.current = undefined
    }
  }, [])

  const stopPolling = useCallback(() => {
    if (pollTimer.current !== undefined) clearTimeout(pollTimer.current)
    pollTimer.current = undefined
  }, [])

  const refresh = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    const mySeq = ++refreshSeq.current
    try {
      const reply = await bridge.getAgentContext({
        projectId,
        module,
        selectedObjectIds,
      })
      if (!live.current || refreshSeq.current !== mySeq) return
      if (!reply.ok) {
        setContext(null)
        setState(null)
        setFailure(reply.error.code)
        return
      }
      if (!agentContextMatches(reply.data, projectId, module)) {
        // A foreign context is never kept: the old context is dropped instead
        // of being shown as if it belonged to the selected project.
        setContext(null)
        setState(null)
        setFailure('AGENT_CONTEXT_MISMATCH')
        return
      }
      setContext(reply.data)
    } catch {
      if (!live.current || refreshSeq.current !== mySeq) return
      setContext(null)
      setState(null)
      setFailure('AGENT_CONTEXT_UNAVAILABLE')
    }
    try {
      const reply = await bridge.getAgentState({ projectId })
      if (!live.current || refreshSeq.current !== mySeq) return
      if (!reply.ok) return
      if (reply.data.context && reply.data.context.projectId !== projectId) {
        setState(null)
        return
      }
      setState(reply.data)
      // An upstream `query` draft is handed to the query workspace as soon as
      // it validates — but only while this request still owns the view and
      // the run really belongs to the selected project.
      const receipts = reply.data.receipts ?? []
      const operationId = reply.data.operationId
      const draft = [...receipts]
        .reverse()
        .find(
          (receipt): receipt is Extract<AgentReceiptDTO, { outcome: { kind: 'draft' } }> =>
            receipt.outcome.kind === 'draft' && receipt.outcome.draftType === 'query',
        )
      if (!draft || !operationId) return
      if (lastQueryReceipt.current === operationId) return
      lastQueryReceipt.current = operationId
      const fromDetail = queryDraftFromDetail(draft.outcome.detail)
      if (fromDetail) {
        if (!live.current || refreshSeq.current !== mySeq) return
        if (reply.data.context?.projectId !== projectId) return
        onQueryDraft.current?.(fromDetail)
        setNotice('已收到上游查询草稿，请在查询工作台核对后手动载入。')
        return
      }
      let plan: AgentDraftPlanDTO
      try {
        plan = take(await bridge.buildAgentDraftPlan({ operationId }))
      } catch {
        if (live.current && refreshSeq.current === mySeq)
          setNotice('上游查询草稿不可用；编辑器内容未被修改。')
        return
      }
      if (!live.current || refreshSeq.current !== mySeq) return
      if (reply.data.context?.projectId !== projectId) return
      const query = queryDraftFromPlan(plan)
      if (query) {
        onQueryDraft.current?.(query)
        setNotice('已收到上游查询草稿，请在查询工作台核对后手动载入。')
      } else setNotice('上游查询草稿未通过校验，未载入编辑器。')
    } catch {
      /* An unavailable state channel simply means no receipts are shown. */
    }
  }, [projectId, module, selectedObjectIds])

  useEffect(() => {
    // Deferred: the effect body itself never triggers a state update.
    const timer = setTimeout(() => void refresh(), 0)
    return () => clearTimeout(timer)
  }, [refresh, modelSyncVersion])

  // A project or module change retires the pending run watch.
  useEffect(() => {
    stopPolling()
  }, [projectId, module, stopPolling])

  /**
   * Follow one exchange until the host leaves the `dispatching` status. The
   * timer is always owned: an outdated dispatch never writes the state.
   */
  const pollExchange = useCallback(
    (exchangeId: number, myDispatch: number) => {
      stopPolling()
      const tick = async () => {
        const bridge = window.ontolearn
        if (!bridge || !live.current || dispatchSeq.current !== myDispatch) return
        try {
          const reply = await bridge.getAgentState({ projectId })
          if (!live.current || dispatchSeq.current !== myDispatch) return
          if (!reply.ok) return
          setState(reply.data)
          if (reply.data.status === 'dispatching' && reply.data.exchangeId === exchangeId) {
            pollTimer.current = setTimeout(() => void tick(), 150)
          }
        } catch {
          /* The channel may be unavailable; the next refresh reports the truth. */
        }
      }
      pollTimer.current = setTimeout(() => void tick(), 150)
    },
    [projectId, stopPolling],
  )

  const dispatch = useCallback(
    async (question: string) => {
      const bridge = window.ontolearn
      if (!bridge || !projectId) return
      const myDispatch = ++dispatchSeq.current
      stopPolling()
      setBusy(true)
      setFailure('')
      setNotice('')
      let failureCode: string | null = null
      try {
        const reply = await bridge.dispatchAgentQuestion({
          operationId: crypto.randomUUID(),
          question,
          module,
          mode,
          selectedObjectIds,
          scope: 'asserted',
        })
        if (!live.current || dispatchSeq.current !== myDispatch) return
        if (!reply.ok) {
          // The structured failure is reported immediately and re-thrown, so
          // the sidebar keeps the question and shows the failure.
          failureCode = reply.error.code
          setFailure(reply.error.code)
          throw new Error(reply.error.code)
        }
        await refresh()
        if (!live.current || dispatchSeq.current !== myDispatch) return
        pollExchange(reply.data.exchangeId, myDispatch)
      } catch (cause) {
        if (failureCode === null && live.current && dispatchSeq.current === myDispatch)
          setFailure(cause instanceof Error ? cause.message : 'AGENT_DISPATCH_FAILED')
        throw cause
      } finally {
        if (live.current && dispatchSeq.current === myDispatch) setBusy(false)
      }
    },
    [projectId, module, mode, selectedObjectIds, refresh, pollExchange, stopPolling],
  )

  const cancel = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    const myDispatch = dispatchSeq.current
    try {
      const reply = await bridge.cancelAgentExchange({ exchangeId: state?.exchangeId ?? null })
      if (live.current && dispatchSeq.current === myDispatch && reply.ok) setState(reply.data)
    } catch {
      if (live.current) setFailure('AGENT_CANCEL_FAILED')
    }
  }, [state])

  const buildPlan = useCallback(
    async (receipt: AgentReceiptDTO) => {
      const bridge = window.ontolearn
      const operationId = state?.operationId
      if (!bridge || !operationId || receipt.outcome.kind !== 'draft') return
      const mySeq = ++planSeq.current
      setBusy(true)
      setFailure('')
      try {
        const plan = take(await bridge.buildAgentDraftPlan({ operationId }))
        if (!live.current || planSeq.current !== mySeq) return
        if (state?.context?.projectId !== projectId) return
        onDraftPlan.current?.(plan)
      } catch (cause) {
        if (live.current && planSeq.current === mySeq)
          setFailure(cause instanceof Error ? cause.message : 'AGENT_DRAFT_PLAN_FAILED')
      } finally {
        if (live.current && planSeq.current === mySeq) setBusy(false)
      }
    },
    [state, projectId],
  )

  const actions = useMemo(
    () => contextActions(module, !!context?.modelReady, props.localActions),
    [module, context?.modelReady, props.localActions],
  )
  // Every page offers at most four quick actions, and an action whose target
  // is unavailable stays disabled — there is never a silent no-op button.
  const unavailable = actions.filter((action) => action.target === 'unavailable')
  // The real host run state, mapped onto the sidebar vocabulary.
  const sidebarState = useMemo(
    () => (state ? agentDtoToSidebarState(state, projectId ?? '') : null),
    [state, projectId],
  )

  if (!projectId) {
    return (
      <section
        className="agent-panel"
        data-testid="agent-panel"
        data-busy={busy}
        aria-label="工作台助手"
      >
        <p role="status">尚未打开项目；助手不会在没有项目的情况下读取或修改任何数据。</p>
      </section>
    )
  }
  const sidebarContext = context
    ? {
        projectId: context.projectId ?? projectId,
        projectRevision: context.projectRevision ?? projectRevision ?? 0,
        inputSnapshotId: context.inputSnapshotId ?? inputSnapshotId ?? 'unavailable',
        scopeRef: context.scopeRef ?? sidebarState?.inputContext.scopeRef ?? 'unavailable',
        module: context.module,
        mode: context.mode,
        selectedObjectIds: context.selectedObjectIds,
      }
    : null
  return (
    <section
      className="agent-panel"
      data-testid="agent-panel"
      data-busy={busy}
      aria-label="工作台助手"
    >
      <header className="agent-panel-heading">
        <h2>工作台助手</h2>
        <span>
          {context ? `模块 ${context.module} · 模式 ${context.mode}` : '正在读取助手上下文…'}
        </span>
      </header>
      <p data-testid="agent-panel-quick-actions-summary">
        本页快捷动作 {actions.length} 项
        {unavailable.length ? `；其中 ${unavailable.length} 项尚未接线并保持禁用` : ''}
      </p>
      {failure && (
        <p role="alert" data-testid="agent-panel-failure">
          助手操作未完成（{failure}）；项目数据未被本次操作修改。
        </p>
      )}
      {notice && (
        <p role="status" data-testid="agent-panel-notice">
          {notice}
        </p>
      )}
      {sidebarContext ? (
        <AgentSidebar
          context={sidebarContext}
          state={sidebarState}
          receipts={state?.receipts}
          privacy={context?.privacy ?? 'local'}
          modelReady={!!context?.modelReady}
          localActions={props.localActions}
          onModeChange={props.onModeChange}
          onAction={async (action, target) => {
            if (target === 'local') {
              await onLocalAction.current?.(action)
              return
            }
            await dispatch(action)
          }}
          onSubmit={(question) => dispatch(question)}
          onCancel={() => void cancel()}
          onPreviewAgentDraft={(receipt) => void buildPlan(receipt)}
        />
      ) : (
        <p role="status">助手上下文尚未就绪；暂不提供任何动作。</p>
      )}
    </section>
  )
}
