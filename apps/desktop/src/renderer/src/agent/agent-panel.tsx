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
  onModeChange?: (mode: AgentMode) => void
  /** Receives a validated upstream query draft. */
  onQueryDraft?: (draft: QueryDraftDTO) => void
  /** Receives the host-built ontology draft plan for diff review. */
  onDraftPlan?: (plan: AgentDraftPlanDTO) => void
  /** Offline action handler (hint / check / demonstrate / explain). */
  onLocalAction?: (action: AgentAction) => void | Promise<void>
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

export function AgentPanel(props: AgentPanelProps) {
  const { projectId, projectRevision, inputSnapshotId, module, mode, selectedObjectIds } = props
  const [context, setContext] = useState<AgentContextDTO | null>(null)
  const [state, setState] = useState<AgentStateDTO | null>(null)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')
  const live = useRef(true)
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
    }
  }, [])

  const refresh = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    try {
      const reply = await bridge.getAgentContext({
        projectId,
        module,
        selectedObjectIds,
      })
      if (!live.current) return
      if (reply.ok) setContext(reply.data)
      else setFailure(reply.error.code)
    } catch {
      if (live.current) setFailure('AGENT_CONTEXT_UNAVAILABLE')
    }
    try {
      const reply = await bridge.getAgentState({ projectId })
      if (live.current && reply.ok) setState(reply.data)
    } catch {
      /* An unavailable state channel simply means no receipts are shown. */
    }
  }, [projectId, module, selectedObjectIds])

  useEffect(() => {
    // Deferred: the effect body itself never triggers a state update.
    const timer = setTimeout(() => void refresh(), 0)
    return () => clearTimeout(timer)
  }, [refresh])

  // A new upstream `query` draft is handed to the query workspace as soon as
  // it validates. An invalid draft is never silently applied.
  const lastQueryReceipt = useRef('')
  useEffect(() => {
    // Deferred: the effect body itself never triggers a state update.
    const timer = setTimeout(() => {
      const receipts = state?.receipts ?? []
      const operationId = state?.operationId
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
        onQueryDraft.current?.(fromDetail)
        setNotice('已收到上游查询草稿，请在查询工作台核对后手动载入。')
        return
      }
      const bridge = window.ontolearn
      if (!bridge) return
      void (async () => {
        try {
          const plan = take(await bridge.buildAgentDraftPlan({ operationId }))
          if (!live.current) return
          const query = queryDraftFromPlan(plan)
          if (query) {
            onQueryDraft.current?.(query)
            setNotice('已收到上游查询草稿，请在查询工作台核对后手动载入。')
          } else setNotice('上游查询草稿未通过校验，未载入编辑器。')
        } catch {
          if (live.current) setNotice('上游查询草稿不可用；编辑器内容未被修改。')
        }
      })()
    }, 0)
    return () => clearTimeout(timer)
  }, [state])

  const dispatch = useCallback(
    async (question: string) => {
      const bridge = window.ontolearn
      if (!bridge || !projectId) return
      setBusy(true)
      setFailure('')
      setNotice('')
      try {
        await bridge.dispatchAgentQuestion({
          operationId: crypto.randomUUID(),
          question,
          module,
          mode,
          selectedObjectIds,
          scope: 'asserted',
        })
        if (!live.current) return
        await refresh()
      } catch (cause) {
        if (live.current)
          setFailure(cause instanceof Error ? cause.message : 'AGENT_DISPATCH_FAILED')
      } finally {
        if (live.current) setBusy(false)
      }
    },
    [projectId, module, mode, selectedObjectIds, refresh],
  )

  const cancel = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    try {
      const reply = await bridge.cancelAgentExchange({ exchangeId: state?.exchangeId ?? null })
      if (live.current && reply.ok) setState(reply.data)
    } catch {
      if (live.current) setFailure('AGENT_CANCEL_FAILED')
    }
  }, [state])

  const buildPlan = useCallback(
    async (receipt: AgentReceiptDTO) => {
      const bridge = window.ontolearn
      const operationId = state?.operationId
      if (!bridge || !operationId || receipt.outcome.kind !== 'draft') return
      setBusy(true)
      setFailure('')
      try {
        const plan = take(await bridge.buildAgentDraftPlan({ operationId }))
        if (live.current) onDraftPlan.current?.(plan)
      } catch (cause) {
        if (live.current)
          setFailure(cause instanceof Error ? cause.message : 'AGENT_DRAFT_PLAN_FAILED')
      } finally {
        if (live.current) setBusy(false)
      }
    },
    [state],
  )

  const actions = useMemo(
    () => contextActions(module, !!context?.modelReady, props.localActions),
    [module, context?.modelReady, props.localActions],
  )
  // Every page offers at most four quick actions, and an action whose target
  // is unavailable stays disabled — there is never a silent no-op button.
  const unavailable = actions.filter((action) => action.target === 'unavailable')

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
        scopeRef: context.scopeRef ?? 'unavailable',
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
          state={null}
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
