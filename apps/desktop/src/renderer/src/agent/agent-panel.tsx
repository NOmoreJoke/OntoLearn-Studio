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

function sameSelectedIds(left: readonly string[], right: readonly string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index])
}

/** True when the host context really belongs to the selected project, module and semantic owner. */
export function agentContextMatches(
  context: AgentContextDTO | null,
  projectId: string | null,
  module: AgentContextDTO['module'],
  expected?: {
    projectRevision?: number | null
    inputSnapshotId?: string | null
    selectedObjectIds?: readonly string[]
  },
): boolean {
  if (!context || !projectId) return false
  if (context.projectId !== projectId || context.module !== module) return false
  if (
    expected?.projectRevision != null &&
    context.projectRevision != null &&
    context.projectRevision !== expected.projectRevision
  )
    return false
  if (
    expected?.inputSnapshotId &&
    context.inputSnapshotId &&
    context.inputSnapshotId !== expected.inputSnapshotId
  )
    return false
  if (
    expected?.selectedObjectIds &&
    !sameSelectedIds(context.selectedObjectIds, expected.selectedObjectIds)
  )
    return false
  return true
}

type SemanticOwner = {
  projectId: string | null
  projectRevision: number | null
  inputSnapshotId: string | null
  module: AgentContextDTO['module']
  selectedObjectIds: readonly string[]
  selectedKey: string
}

function sameViewOwner(left: SemanticOwner, right: SemanticOwner): boolean {
  return (
    left.projectId === right.projectId &&
    left.projectRevision === right.projectRevision &&
    left.inputSnapshotId === right.inputSnapshotId &&
    left.module === right.module &&
    left.selectedKey === right.selectedKey
  )
}

function viewKeyOf(owner: SemanticOwner, mode: AgentMode): string {
  return `${owner.projectId ?? ''}|${owner.projectRevision ?? ''}|${owner.inputSnapshotId ?? ''}|${owner.module}|${mode}|${owner.selectedKey}`
}

function stateMatchesView(
  stateData: AgentStateDTO,
  owner: SemanticOwner,
  expectedMode: AgentMode,
  expectedExchangeId?: number,
  expectedOperationId?: string,
): boolean {
  if (!owner.projectId) return false
  if (!stateData.context) {
    return (
      stateData.status === 'idle' &&
      expectedExchangeId === undefined &&
      expectedOperationId === undefined
    )
  }
  const ctx = stateData.context
  if (
    ctx.projectId !== owner.projectId ||
    ctx.module !== owner.module ||
    ctx.mode !== expectedMode ||
    !sameSelectedIds(ctx.selectedObjectIds, owner.selectedObjectIds)
  )
    return false
  if (owner.projectRevision != null && ctx.projectRevision !== owner.projectRevision) return false
  if (owner.inputSnapshotId && ctx.inputSnapshotId !== owner.inputSnapshotId) return false
  if (expectedExchangeId !== undefined && stateData.exchangeId !== expectedExchangeId) return false
  if (expectedOperationId !== undefined && stateData.operationId !== expectedOperationId)
    return false
  return true
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
  const [dispatchBusy, setDispatchBusy] = useState<{ viewKey: string; token: number } | null>(null)
  const [planBusy, setPlanBusy] = useState<{ turnKey: string; token: number } | null>(null)
  const [syncedHostMode, setSyncedHostMode] = useState<{
    projectId: string | null
    forPropMode: AgentMode
    mode: AgentMode
  } | null>(null)
  const [notice, setNotice] = useState('')
  const [failure, setFailure] = useState('')
  const live = useRef(true)
  const refreshSeq = useRef(0)
  const dispatchSeq = useRef(0)
  const planSeq = useRef(0)
  const modeSwitchSeq = useRef(0)
  // Delivered and in-flight upstream query receipts keyed by `projectId:operationId`.
  const deliveredQueryReceipts = useRef(new Set<string>())
  const inFlightQueryReceipts = useRef(new Map<string, Promise<AgentDraftPlanDTO>>())
  const pollTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const pollSeq = useRef(0)
  const selectedKey = JSON.stringify(selectedObjectIds)
  const renderViewOwner: SemanticOwner = {
    projectId,
    projectRevision,
    inputSnapshotId,
    module,
    selectedObjectIds: JSON.parse(selectedKey) as string[],
    selectedKey,
  }
  const ownerRef = useRef<SemanticOwner>(renderViewOwner)
  const propModeRef = useRef<AgentMode>(mode)
  const effectiveModeRef = useRef<AgentMode>(mode)
  const stateRef = useRef<AgentStateDTO | null>(null)
  const refreshRef = useRef<() => Promise<void>>(async () => {})
  const onQueryDraft = useRef(props.onQueryDraft)
  const onDraftPlan = useRef(props.onDraftPlan)
  const onLocalAction = useRef(props.onLocalAction)
  useEffect(() => {
    onQueryDraft.current = props.onQueryDraft
    onDraftPlan.current = props.onDraftPlan
    onLocalAction.current = props.onLocalAction
  })

  const stopPolling = useCallback(() => {
    pollSeq.current += 1
    if (pollTimer.current !== undefined) clearTimeout(pollTimer.current)
    pollTimer.current = undefined
  }, [])

  const commitState = useCallback((next: AgentStateDTO | null) => {
    const prev = stateRef.current
    if (prev?.operationId !== next?.operationId || prev?.exchangeId !== next?.exchangeId) {
      planSeq.current += 1
      const activeSeq = planSeq.current
      setPlanBusy((current) => (current && current.token < activeSeq ? null : current))
    }
    stateRef.current = next
    setState(next)
  }, [])

  useEffect(() => {
    ownerRef.current = {
      projectId,
      projectRevision,
      inputSnapshotId,
      module,
      selectedObjectIds: JSON.parse(selectedKey) as string[],
      selectedKey,
    }
    stopPolling()
    dispatchSeq.current += 1
    planSeq.current += 1
    modeSwitchSeq.current += 1
    return () => {
      setDispatchBusy(null)
      setPlanBusy(null)
    }
  }, [projectId, projectRevision, inputSnapshotId, module, selectedKey, stopPolling])

  useEffect(() => {
    propModeRef.current = mode
    effectiveModeRef.current = mode
    stopPolling()
    dispatchSeq.current += 1
    planSeq.current += 1
    return () => {
      setDispatchBusy(null)
      setPlanBusy(null)
    }
  }, [mode, stopPolling])

  useEffect(() => {
    live.current = true
    return () => {
      live.current = false
      pollSeq.current += 1
      if (pollTimer.current !== undefined) clearTimeout(pollTimer.current)
      pollTimer.current = undefined
    }
  }, [])

  const stateMatchesCurrent = useCallback(
    (
      stateData: AgentStateDTO,
      expectedExchangeId?: number,
      expectedOperationId?: string,
    ): boolean =>
      stateMatchesView(
        stateData,
        ownerRef.current,
        effectiveModeRef.current,
        expectedExchangeId,
        expectedOperationId,
      ),
    [],
  )

  const deliverQueryDraft = useCallback(
    async (
      bridge: NonNullable<Window['ontolearn']>,
      stateData: AgentStateDTO,
      isStillCurrent: () => boolean,
      expectedExchangeId?: number,
      expectedOperationId?: string,
    ) => {
      const turnStillCurrent = (): boolean => {
        if (!isStillCurrent()) return false
        if (!stateMatchesCurrent(stateData, expectedExchangeId, expectedOperationId)) return false
        const latest = stateRef.current
        if (
          !latest ||
          latest.operationId !== stateData.operationId ||
          latest.exchangeId !== stateData.exchangeId
        )
          return false
        return stateMatchesCurrent(latest, expectedExchangeId, expectedOperationId)
      }
      if (!turnStillCurrent()) return
      const cur = ownerRef.current
      if (!cur.projectId) return
      const receipts = stateData.receipts ?? []
      const operationId = stateData.operationId
      const draft = [...receipts]
        .reverse()
        .find(
          (receipt): receipt is Extract<AgentReceiptDTO, { outcome: { kind: 'draft' } }> =>
            receipt.outcome.kind === 'draft' &&
            receipt.outcome.draftType === 'query' &&
            receipt.outcome.projectId === cur.projectId &&
            (cur.projectRevision == null || receipt.outcome.baseRevision === cur.projectRevision) &&
            (!cur.inputSnapshotId || receipt.outcome.inputSnapshotId === cur.inputSnapshotId),
        )
      if (!draft || !operationId) return
      const receiptKey = `${cur.projectId}:${operationId}`
      if (deliveredQueryReceipts.current.has(receiptKey)) return
      const fromDetail = queryDraftFromDetail(draft.outcome.detail)
      if (fromDetail) {
        if (!turnStillCurrent() || deliveredQueryReceipts.current.has(receiptKey)) return
        deliveredQueryReceipts.current.add(receiptKey)
        onQueryDraft.current?.(fromDetail)
        setNotice('已收到上游查询草稿，请在查询工作台核对后手动载入。')
        return
      }
      let pendingPlan = inFlightQueryReceipts.current.get(receiptKey)
      if (!pendingPlan) {
        pendingPlan = (async () => {
          try {
            return take(await bridge.buildAgentDraftPlan({ operationId }))
          } finally {
            inFlightQueryReceipts.current.delete(receiptKey)
          }
        })()
        inFlightQueryReceipts.current.set(receiptKey, pendingPlan)
      }
      let plan: AgentDraftPlanDTO
      try {
        plan = await pendingPlan
      } catch {
        if (turnStillCurrent()) setNotice('上游查询草稿不可用；编辑器内容未被修改。')
        return
      }
      if (!turnStillCurrent() || deliveredQueryReceipts.current.has(receiptKey)) return
      const latestOwner = ownerRef.current
      if (
        plan.operationId !== operationId ||
        (latestOwner.projectRevision != null &&
          plan.baseRevision !== latestOwner.projectRevision) ||
        (latestOwner.inputSnapshotId && plan.inputSnapshotId !== latestOwner.inputSnapshotId)
      )
        return
      const query = queryDraftFromPlan(plan)
      if (query) {
        deliveredQueryReceipts.current.add(receiptKey)
        onQueryDraft.current?.(query)
        setNotice('已收到上游查询草稿，请在查询工作台核对后手动载入。')
      } else {
        setNotice('上游查询草稿未通过校验，未载入编辑器。')
      }
    },
    [stateMatchesCurrent],
  )

  /**
   * Follow one exchange until the host leaves the `dispatching` status. The
   * timer is always owned: an outdated dispatch never writes the state.
   */
  const pollExchange = useCallback(
    (
      exchangeId: number,
      expectedOperationId: string,
      myDispatch: number,
      myOwner: SemanticOwner,
      myMode: AgentMode,
    ) => {
      stopPolling()
      const myPoll = ++pollSeq.current
      const ownsViewTurn = () =>
        live.current &&
        dispatchSeq.current === myDispatch &&
        sameViewOwner(ownerRef.current, myOwner) &&
        effectiveModeRef.current === myMode
      const ownsPoll = () => pollSeq.current === myPoll && ownsViewTurn()
      const stopOwnPolling = () => {
        if (pollSeq.current === myPoll) stopPolling()
      }
      const tick = async () => {
        if (pollSeq.current === myPoll) pollTimer.current = undefined
        const bridge = window.ontolearn
        if (!bridge || !myOwner.projectId || !ownsPoll()) {
          stopOwnPolling()
          return
        }
        try {
          const reply = await bridge.getAgentState({ projectId: myOwner.projectId })
          if (!ownsPoll()) return
          if (!reply.ok) {
            stopOwnPolling()
            return
          }
          if (!stateMatchesCurrent(reply.data, exchangeId, expectedOperationId)) {
            stopOwnPolling()
            return
          }
          commitState(reply.data)
          if (reply.data.status === 'dispatching' && reply.data.exchangeId === exchangeId) {
            if (ownsPoll()) pollTimer.current = setTimeout(() => void tick(), 150)
            return
          }
          stopOwnPolling()
          await deliverQueryDraft(bridge, reply.data, ownsViewTurn, exchangeId, expectedOperationId)
        } catch {
          /* The channel may be unavailable; the next refresh reports the truth. */
        }
      }
      if (ownsPoll()) pollTimer.current = setTimeout(() => void tick(), 150)
    },
    [stopPolling, stateMatchesCurrent, commitState, deliverQueryDraft],
  )

  const refresh = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    const selectedIds = JSON.parse(selectedKey) as string[]
    const myOwner: SemanticOwner = {
      projectId,
      projectRevision,
      inputSnapshotId,
      module,
      selectedObjectIds: selectedIds,
      selectedKey,
    }
    const ownsView = () => live.current && sameViewOwner(ownerRef.current, myOwner)
    if (!ownsView()) return
    const mySeq = ++refreshSeq.current
    const stillOwnsRefresh = () => ownsView() && refreshSeq.current === mySeq
    try {
      const reply = await bridge.getAgentContext({
        projectId: myOwner.projectId,
        module: myOwner.module,
        selectedObjectIds: selectedIds,
      })
      if (!stillOwnsRefresh()) return
      if (!reply.ok) {
        stopPolling()
        setContext(null)
        commitState(null)
        setFailure(reply.error.code)
        return
      }
      if (
        !agentContextMatches(reply.data, myOwner.projectId, myOwner.module, {
          projectRevision: myOwner.projectRevision,
          inputSnapshotId: myOwner.inputSnapshotId,
          selectedObjectIds: selectedIds,
        })
      ) {
        // A foreign context is never kept: the old context is dropped instead
        // of being shown as if it belonged to the selected project.
        stopPolling()
        setContext(null)
        commitState(null)
        setFailure('AGENT_CONTEXT_MISMATCH')
        return
      }
      effectiveModeRef.current = reply.data.mode
      setSyncedHostMode({
        projectId: myOwner.projectId,
        forPropMode: propModeRef.current,
        mode: reply.data.mode,
      })
      setFailure('')
      setContext(reply.data)
    } catch {
      if (!stillOwnsRefresh()) return
      stopPolling()
      setContext(null)
      commitState(null)
      setFailure('AGENT_CONTEXT_UNAVAILABLE')
    }
    try {
      const reply = await bridge.getAgentState({ projectId: myOwner.projectId })
      if (!stillOwnsRefresh()) return
      if (!reply.ok) return
      if (!stateMatchesCurrent(reply.data)) {
        stopPolling()
        commitState(null)
        return
      }
      commitState(reply.data)
      if (
        reply.data.status === 'dispatching' &&
        reply.data.exchangeId != null &&
        reply.data.operationId
      ) {
        pollExchange(
          reply.data.exchangeId,
          reply.data.operationId,
          dispatchSeq.current,
          myOwner,
          effectiveModeRef.current,
        )
        return
      }
      stopPolling()
      await deliverQueryDraft(
        bridge,
        reply.data,
        stillOwnsRefresh,
        reply.data.exchangeId ?? undefined,
        reply.data.operationId ?? undefined,
      )
    } catch {
      /* An unavailable state channel simply means no receipts are shown. */
    }
  }, [
    projectId,
    projectRevision,
    inputSnapshotId,
    module,
    selectedKey,
    commitState,
    stateMatchesCurrent,
    deliverQueryDraft,
    pollExchange,
    stopPolling,
  ])

  useEffect(() => {
    refreshRef.current = refresh
  }, [refresh])

  useEffect(() => {
    // Deferred: the effect body itself never triggers a state update.
    const timer = setTimeout(() => void refresh(), 0)
    return () => clearTimeout(timer)
  }, [refresh, mode, modelSyncVersion])

  const dispatch = useCallback(
    async (question: string) => {
      const bridge = window.ontolearn
      const myOwner = { ...ownerRef.current }
      const myMode = effectiveModeRef.current
      if (!bridge || !myOwner.projectId) return
      const myDispatch = ++dispatchSeq.current
      planSeq.current += 1
      stopPolling()
      const myViewKey = viewKeyOf(myOwner, myMode)
      const isDispatchCurrent = () =>
        live.current &&
        dispatchSeq.current === myDispatch &&
        sameViewOwner(ownerRef.current, myOwner) &&
        effectiveModeRef.current === myMode
      setDispatchBusy({ viewKey: myViewKey, token: myDispatch })
      setFailure('')
      setNotice('')
      let failureCode: string | null = null
      try {
        const reply = await bridge.dispatchAgentQuestion({
          operationId: crypto.randomUUID(),
          question,
          module: myOwner.module,
          mode: myMode,
          selectedObjectIds: [...myOwner.selectedObjectIds],
          scope: 'asserted',
        })
        if (!isDispatchCurrent()) return
        if (!reply.ok) {
          // The structured failure is reported immediately and re-thrown, so
          // the sidebar keeps the question and shows the failure.
          failureCode = reply.error.code
          setFailure(reply.error.code)
          throw new Error(reply.error.code)
        }
        await refreshRef.current()
        if (!isDispatchCurrent()) return
        const latest = stateRef.current
        if (
          !latest ||
          latest.exchangeId !== reply.data.exchangeId ||
          latest.operationId !== reply.data.operationId ||
          (latest.status === 'dispatching' && pollTimer.current === undefined)
        )
          pollExchange(reply.data.exchangeId, reply.data.operationId, myDispatch, myOwner, myMode)
      } catch (cause) {
        if (failureCode === null && isDispatchCurrent())
          setFailure(cause instanceof Error ? cause.message : 'AGENT_DISPATCH_FAILED')
        throw cause
      } finally {
        if (live.current)
          setDispatchBusy((current) => (current?.token === myDispatch ? null : current))
      }
    },
    [pollExchange, stopPolling],
  )

  const cancel = useCallback(async () => {
    const bridge = window.ontolearn
    if (!bridge) return
    const myOwner = { ...ownerRef.current }
    const myMode = effectiveModeRef.current
    const myDispatch = dispatchSeq.current
    const targetExchangeId = stateRef.current?.exchangeId ?? null
    const ownsCancel = () =>
      live.current &&
      dispatchSeq.current === myDispatch &&
      sameViewOwner(ownerRef.current, myOwner) &&
      effectiveModeRef.current === myMode
    try {
      const reply = await bridge.cancelAgentExchange({ exchangeId: targetExchangeId })
      if (!ownsCancel()) return
      if (reply.ok) {
        stopPolling()
        if (stateMatchesCurrent(reply.data)) commitState(reply.data)
        else commitState(null)
      }
    } catch {
      if (ownsCancel()) setFailure('AGENT_CANCEL_FAILED')
    }
  }, [stopPolling, stateMatchesCurrent, commitState])

  const buildPlan = useCallback(async (receipt: AgentReceiptDTO) => {
    const bridge = window.ontolearn
    const capturedState = stateRef.current
    const expectedOperationId = capturedState?.operationId
    const expectedExchangeId = capturedState?.exchangeId
    const myOwner = { ...ownerRef.current }
    const myMode = effectiveModeRef.current
    const myDispatch = dispatchSeq.current
    if (!bridge || !capturedState || !expectedOperationId || receipt.outcome.kind !== 'draft')
      return
    if (
      !myOwner.projectId ||
      !stateMatchesView(
        capturedState,
        myOwner,
        myMode,
        expectedExchangeId ?? undefined,
        expectedOperationId,
      )
    )
      return
    if (
      receipt.outcome.projectId !== myOwner.projectId ||
      (myOwner.projectRevision != null &&
        receipt.outcome.baseRevision !== myOwner.projectRevision) ||
      (myOwner.inputSnapshotId && receipt.outcome.inputSnapshotId !== myOwner.inputSnapshotId)
    )
      return
    const mySeq = ++planSeq.current
    const myTurnKey = `${viewKeyOf(myOwner, myMode)}|${expectedOperationId}|${expectedExchangeId ?? ''}`
    setPlanBusy({ turnKey: myTurnKey, token: mySeq })
    setFailure('')
    const stillActiveTurn = () => {
      if (
        !live.current ||
        planSeq.current !== mySeq ||
        dispatchSeq.current !== myDispatch ||
        !sameViewOwner(ownerRef.current, myOwner) ||
        effectiveModeRef.current !== myMode
      )
        return false
      const latest = stateRef.current
      if (
        !latest ||
        latest.operationId !== expectedOperationId ||
        latest.exchangeId !== expectedExchangeId
      )
        return false
      return stateMatchesView(
        latest,
        ownerRef.current,
        effectiveModeRef.current,
        expectedExchangeId ?? undefined,
        expectedOperationId,
      )
    }
    try {
      const plan = take(await bridge.buildAgentDraftPlan({ operationId: expectedOperationId }))
      if (!stillActiveTurn()) return
      if (
        plan.operationId !== expectedOperationId ||
        (myOwner.projectRevision != null && plan.baseRevision !== myOwner.projectRevision) ||
        (myOwner.inputSnapshotId && plan.inputSnapshotId !== myOwner.inputSnapshotId)
      )
        return
      onDraftPlan.current?.(plan)
    } catch (cause) {
      if (stillActiveTurn())
        setFailure(cause instanceof Error ? cause.message : 'AGENT_DRAFT_PLAN_FAILED')
    } finally {
      if (live.current) setPlanBusy((current) => (current?.token === mySeq ? null : current))
    }
  }, [])

  const actions = useMemo(
    () => contextActions(module, !!context?.modelReady, props.localActions),
    [module, context?.modelReady, props.localActions],
  )
  // Every page offers at most four quick actions, and an action whose target
  // is unavailable stays disabled — there is never a silent no-op button.
  const unavailable = actions.filter((action) => action.target === 'unavailable')
  const activeMode =
    syncedHostMode && syncedHostMode.projectId === projectId && syncedHostMode.forPropMode === mode
      ? syncedHostMode.mode
      : mode
  const displayedContext =
    context &&
    agentContextMatches(context, projectId, module, {
      projectRevision,
      inputSnapshotId,
      selectedObjectIds: renderViewOwner.selectedObjectIds,
    })
      ? context
      : null
  const displayedState =
    state && stateMatchesView(state, renderViewOwner, activeMode) ? state : null
  const currentViewKey = viewKeyOf(renderViewOwner, activeMode)
  const currentTurnKey = `${currentViewKey}|${displayedState?.operationId ?? ''}|${displayedState?.exchangeId ?? ''}`
  const busy = dispatchBusy?.viewKey === currentViewKey || planBusy?.turnKey === currentTurnKey
  // The real host run state, mapped onto the sidebar vocabulary.
  const sidebarState = useMemo(
    () => (displayedState ? agentDtoToSidebarState(displayedState, projectId ?? '') : null),
    [displayedState, projectId],
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
  const sidebarContext = displayedContext
    ? {
        projectId: displayedContext.projectId ?? projectId,
        projectRevision: displayedContext.projectRevision ?? projectRevision ?? 0,
        inputSnapshotId: displayedContext.inputSnapshotId ?? inputSnapshotId ?? 'unavailable',
        scopeRef: displayedContext.scopeRef ?? sidebarState?.inputContext.scopeRef ?? 'unavailable',
        module: displayedContext.module,
        mode: displayedContext.mode,
        selectedObjectIds: displayedContext.selectedObjectIds,
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
          {displayedContext
            ? `模块 ${displayedContext.module} · 模式 ${displayedContext.mode}`
            : '正在读取助手上下文…'}
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
          receipts={displayedState?.receipts}
          privacy={displayedContext?.privacy ?? 'local'}
          modelReady={!!displayedContext?.modelReady}
          localActions={props.localActions}
          onModeChange={
            props.onModeChange
              ? async (nextMode) => {
                  const clickOwner = { ...ownerRef.current }
                  const myModeSeq = ++modeSwitchSeq.current
                  await props.onModeChange?.(nextMode)
                  if (
                    live.current &&
                    modeSwitchSeq.current === myModeSeq &&
                    sameViewOwner(ownerRef.current, clickOwner)
                  )
                    await refreshRef.current()
                }
              : undefined
          }
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
