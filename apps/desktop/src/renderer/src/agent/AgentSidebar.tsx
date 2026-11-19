import { useEffect, useId, useRef, useState } from 'react'
import type { AgentMode, AgentPrivacy, AgentReceiptDTO } from '@ontolearn/contracts'
import type { ToolReceipt, TrustedContext } from '../../../main/agent/agent-service'
import { contextActions, assistanceLevel, type AgentAction } from './context-actions'
import {
  canPreviewDraft,
  describeAgentError,
  displayScalar,
  preparedDraft,
  resultLabels,
  sidebarContextKey,
  sidebarInteraction,
  sidebarIsCurrent,
  toolLabels,
  updateSidebarInteraction,
  type SidebarInteraction,
  type SidebarInteractions,
  type SidebarState,
} from './sidebar-presentation'
import './agent-sidebar.css'

export interface AgentSidebarProps {
  context: TrustedContext
  state: SidebarState | null
  /** Frozen privacy vocabulary: `local | minimal | project`. */
  privacy: AgentPrivacy
  modelReady: boolean
  localActions: readonly AgentAction[]
  /** Optional mode switch; without a handler the control stays disabled. */
  onModeChange?: (mode: AgentMode) => void | Promise<void>
  onAction?: (
    action: AgentAction,
    target: 'local' | 'agent',
    assistance: 'hint' | 'full-assistance',
  ) => void | Promise<void>
  onSubmit?: (question: string) => void | Promise<void>
  onCancel?: () => void
  onRetry?: () => void | Promise<void>
  onPreviewDraft?: (receipt: ToolReceipt) => void | Promise<void>
  /** Receipts read from the named Agent bridge (frozen contract DTOs). */
  receipts?: readonly AgentReceiptDTO[]
  /** Opens the real diff for a bridge receipt. */
  onPreviewAgentDraft?: (receipt: AgentReceiptDTO) => void | Promise<void>
}
/**
 * The frozen contract vocabulary is `minimal`. Legacy callers may still send
 * the retired `minimum`; it is read as `minimal` and never surfaced as a
 * separate privacy level.
 */
function normalizePrivacy(privacy: AgentPrivacy | 'minimum'): AgentPrivacy {
  return privacy === 'minimum' ? 'minimal' : privacy
}
const toolNames = new Set([
  'ontology_read',
  'ontology_propose',
  'mapping_propose',
  'query_draft',
  'query_execute',
  'quality_check',
  'reasoning_run',
  'behavior_test',
  'scenario_run',
  'result_read',
])
function toolLabel(tool: string): string {
  return toolNames.has(tool) ? toolLabels[tool as keyof typeof toolLabels] : '本地工具记录'
}
/**
 * A bridge draft may only be previewed when it is bound to the very same
 * project, revision and input snapshot as the current context.
 */
export function agentDraftIsCurrent(receipt: AgentReceiptDTO, context: TrustedContext): boolean {
  const outcome = receipt.outcome
  return (
    outcome.kind === 'draft' &&
    outcome.projectId === context.projectId &&
    outcome.baseRevision === context.projectRevision &&
    outcome.inputSnapshotId === context.inputSnapshotId &&
    outcome.requiresHumanDiffConfirmation === true
  )
}
function AgentReceiptView({
  receipt,
  context,
  isCurrent,
  onPreview,
}: {
  receipt: AgentReceiptDTO
  context: TrustedContext
  isCurrent: boolean
  onPreview?: (receipt: AgentReceiptDTO) => void
}) {
  const outcome = receipt.outcome
  return (
    <article
      className="t08-receipt"
      data-testid={`agent-receipt-${receipt.callId}`}
      aria-label={`${toolLabel(receipt.tool)} ${receipt.callId}`}
    >
      <div className="t08-receipt-heading">
        <strong>{toolLabel(receipt.tool)}</strong>
        <code>{receipt.callId}</code>
      </div>
      {outcome.kind === 'failure' ? (
        <div data-testid="agent-failure">
          <p role="status">{outcome.code}：本轮不能据此认定通过。</p>
        </div>
      ) : outcome.kind === 'draft' ? (
        <>
          <p className="t08-record-state">建议草稿 · 尚未正式写入</p>
          <p>{outcome.summary}</p>
          <details>
            <summary>查看详细建议</summary>
            <pre>{outcome.detail}</pre>
          </details>
          <p className="t08-meta">
            生成基准 V{outcome.baseRevision} · {outcome.inputSnapshotId}
          </p>
          <button
            type="button"
            disabled={!isCurrent || !agentDraftIsCurrent(receipt, context) || !onPreview}
            onClick={() => onPreview?.(receipt)}
          >
            查看真实 Diff
          </button>
          <p className="t08-meta">仅打开预览；正式提交仍需独立确认及版本复验。</p>
        </>
      ) : (
        <>
          <p className="t08-record-state">{resultLabels[outcome.status]}</p>
          <p className="t08-meta">
            输入 {outcome.inputSnapshotId} · 结果 {outcome.resultId}
          </p>
          {outcome.fields.length ? (
            <dl className="t08-fields">
              {outcome.fields.map((field, index) => (
                <div key={`${index}:${field.fieldId}`}>
                  <dt>{field.fieldId}</dt>
                  <dd>{displayScalar(field.value)}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p>此记录没有可展示的字段；不能据此推断不存在相关事实。</p>
          )}
          {outcome.traceRefs.length > 0 && (
            <details>
              <summary>查看依据引用</summary>
              <ul>
                {outcome.traceRefs.map((reference, index) => (
                  <li key={`${index}:${reference}`}>
                    <code>{reference}</code>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
    </article>
  )
}
function ReceiptView({
  receipt,
  context,
  isCurrent,
  onPreview,
}: {
  receipt: ToolReceipt
  context: TrustedContext
  isCurrent: boolean
  onPreview?: (receipt: ToolReceipt) => void
}) {
  const outcome = receipt.outcome
  const draft = preparedDraft(receipt)
  return (
    <article
      className="t08-receipt"
      data-testid={`agent-receipt-${receipt.callId}`}
      aria-label={`${toolLabels[receipt.tool]} ${receipt.callId}`}
    >
      <div className="t08-receipt-heading">
        <strong>{toolLabels[receipt.tool]}</strong>
        <code>{receipt.callId}</code>
      </div>
      {outcome.kind === 'failure' ? (
        <div data-testid="agent-failure">
          <p role="status">{describeAgentError(outcome.code)} 本轮不能据此认定通过。</p>
        </div>
      ) : outcome.kind === 'draft' ? (
        <>
          <p className="t08-record-state">建议草稿 · 尚未正式写入</p>
          <p>{outcome.summary}</p>
          <details>
            <summary>查看详细建议</summary>
            <pre>{outcome.detail}</pre>
          </details>
          <p className="t08-meta">
            {draft
              ? `生成基准 V${draft.baseRevision} · ${draft.inputSnapshotId}`
              : '缺少版本基准，无法提交预览'}
          </p>
          <button
            type="button"
            disabled={!isCurrent || !canPreviewDraft(receipt, context) || !onPreview}
            onClick={() => onPreview?.(receipt)}
          >
            查看真实 Diff
          </button>
          <p className="t08-meta">仅打开预览；正式提交仍需独立确认及版本复验。</p>
        </>
      ) : (
        <>
          <p className="t08-record-state">{resultLabels[outcome.status]}</p>
          <p className="t08-meta">
            输入 {outcome.inputSnapshotId} · 结果 {outcome.resultId}
          </p>
          {outcome.fields.length ? (
            <dl className="t08-fields">
              {outcome.fields.map((field, index) => (
                <div key={`${index}:${field.fieldId}`}>
                  <dt>{field.fieldId}</dt>
                  <dd>{displayScalar(field.value)}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p>此记录没有可展示的字段；不能据此推断不存在相关事实。</p>
          )}
          {outcome.traceRefs.length > 0 && (
            <details>
              <summary>查看依据引用</summary>
              <ul>
                {outcome.traceRefs.map((reference, index) => (
                  <li key={`${index}:${reference}`}>
                    <code>{reference}</code>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
    </article>
  )
}

/** Prop-driven view only; no bridge, network, credentials, grants, or project writes. */
export function AgentSidebar(props: AgentSidebarProps) {
  const { context, state, modelReady } = props
  const privacy = normalizePrivacy(props.privacy)
  const [interactions, setInteractions] = useState<SidebarInteractions>({})
  const key = sidebarContextKey(context)
  const { question, dispatching, localError } = sidebarInteraction(interactions, key)
  const inFlight = useRef(new Set<string>())
  // Every run gets a monotonically increasing token. A run that was started
  // under an earlier mount of the same semantic key may never write the
  // current busy or error state (A -> B -> A).
  const runTokens = useRef(new Map<string, number>())
  // Every visit of a semantic key is counted. A callback of an earlier visit
  // of the same key is stale even when the key itself did not change.
  const visit = useRef(0)
  const visitedKey = useRef(key)
  const mounted = useRef(true)
  useEffect(() => {
    if (visitedKey.current !== key) {
      visitedKey.current = key
      visit.current += 1
    }
  }, [key])
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])
  function updateInteraction(patch: Partial<SidebarInteraction>) {
    // Async callbacks retain their starting key and merge into its latest UI state.
    setInteractions((previous) => updateSidebarInteraction(previous, key, patch))
  }
  const titleId = useId(),
    inputId = useId()
  const isCurrent = sidebarIsCurrent(state, context)
  const busy =
    dispatching || state?.phase === 'awaiting-provider' || state?.phase === 'executing-tools'
  const modelAvailable = privacy !== 'local' && modelReady
  const actions = contextActions(context.module, modelAvailable, props.localActions)
  const nextMode: AgentMode = context.mode === 'tutor' ? 'project' : 'tutor'
  async function invoke(operation: () => void | Promise<void>) {
    const myKey = key
    if (inFlight.current.has(myKey)) return
    inFlight.current.add(myKey)
    const token = (runTokens.current.get(myKey) ?? 0) + 1
    runTokens.current.set(myKey, token)
    const myVisit = visit.current
    const owns = () =>
      mounted.current && runTokens.current.get(myKey) === token && visit.current === myVisit
    updateInteraction({ dispatching: true, localError: false })
    try {
      await operation()
    } catch {
      if (owns()) updateInteraction({ localError: true })
    } finally {
      if (owns()) {
        inFlight.current.delete(myKey)
        updateInteraction({ dispatching: false })
      }
    }
  }
  return (
    <aside className="t08-agent" data-testid="agent-sidebar" aria-labelledby={titleId}>
      <div className="t08-agent-heading">
        <div>
          <p className="t08-kicker">当前任务助手</p>
          <h2 id={titleId}>{context.mode === 'tutor' ? '导师模式' : '项目模式'}</h2>
        </div>
        <span>
          {privacy === 'local' ? '完全本地' : privacy === 'minimal' ? '最小上下文' : '项目上下文'}
        </span>
      </div>
      <button
        type="button"
        data-testid="agent-mode-toggle"
        disabled={busy || !props.onModeChange}
        onClick={() => {
          if (!props.onModeChange) return
          void invoke(() => props.onModeChange?.(nextMode))
        }}
      >
        {nextMode === 'project' ? '切换到项目模式' : '切换到导师模式'}
      </button>
      <p className="t08-context">
        项目 {context.projectId} · V{context.projectRevision}
        <br />
        选中对象：
        {context.selectedObjectIds.length ? context.selectedObjectIds.join('、') : '尚未选择'}
      </p>
      {!modelAvailable && (
        <p className="t08-note" data-testid="agent-degraded">
          {privacy === 'local' ? '当前使用本地功能。' : '模型尚未通过能力验证，当前使用本地功能。'}
          未接线动作会明确禁用。
        </p>
      )}
      {!isCurrent && (
        <p className="t08-warning" role="status">
          以下记录来自先前项目或输入版本，不能当作当前结果。请返回对应上下文或重新运行。
        </p>
      )}
      <div className="t08-actions" data-testid="agent-quick-actions" aria-label="页面快捷动作">
        {actions.map((action) => (
          <div key={action.action} data-testid={`agent-action-${action.action}`}>
            <button
              type="button"
              disabled={busy || !isCurrent || action.target === 'unavailable' || !props.onAction}
              onClick={() => {
                if (action.target !== 'unavailable')
                  void invoke(() =>
                    props.onAction?.(
                      action.action,
                      action.target as 'local' | 'agent',
                      assistanceLevel(context.mode, action.action),
                    ),
                  )
              }}
            >
              <strong>{action.label}</strong>
              <small>{props.onAction ? action.availabilityText : '动作尚未接线'}</small>
            </button>
          </div>
        ))}
      </div>
      {state?.error && (
        <div className="t08-warning" data-testid="agent-state-failure" role="status">
          <p>{describeAgentError(state.error)}</p>
          <p>输入和已完成记录仍保留；请查看实际状态，或显式重试/使用本地工具。</p>
          {props.onRetry && (
            <button
              type="button"
              disabled={busy || !isCurrent || !modelAvailable}
              onClick={() => void invoke(() => props.onRetry?.())}
            >
              重试本次操作
            </button>
          )}
        </div>
      )}
      <div className="t08-records" aria-label="本轮真实工具记录">
        {props.receipts?.map((receipt) => (
          <AgentReceiptView
            key={receipt.callId}
            receipt={receipt}
            context={context}
            isCurrent={isCurrent && !busy}
            onPreview={
              props.onPreviewAgentDraft
                ? (value) => {
                    void invoke(() => props.onPreviewAgentDraft?.(structuredClone(value)))
                  }
                : undefined
            }
          />
        ))}
        {state?.localReceipts.map((receipt) => (
          <ReceiptView
            key={receipt.callId}
            receipt={receipt}
            context={context}
            isCurrent={isCurrent && !busy}
            onPreview={
              props.onPreviewDraft
                ? (value) => {
                    void invoke(() => props.onPreviewDraft?.(structuredClone(value)))
                  }
                : undefined
            }
          />
        ))}
      </div>
      {state?.answer && state.answer.kind !== 'evidence' && (
        <p className="t08-answer">
          {state.answer.kind === 'suggestion' && <strong>{state.answer.label}：</strong>}
          {state.answer.text}
        </p>
      )}
      {!state?.localReceipts.length && !state?.answer && (
        <p className="t08-empty">
          从页面动作开始，或描述当前问题。查询、检查和沙盘结论会显示真实工具依据。
        </p>
      )}
      <form
        className="t08-question"
        onSubmit={(event) => {
          event.preventDefault()
          if (!busy && isCurrent && modelAvailable && question.trim() && props.onSubmit)
            void invoke(() => props.onSubmit?.(question.trim()))
        }}
      >
        <label htmlFor={inputId}>当前问题</label>
        <textarea
          id={inputId}
          maxLength={32000}
          rows={4}
          value={question}
          onChange={(event) => updateInteraction({ question: event.target.value })}
          placeholder="描述目标或希望获得的提示"
        />
        <p className="t08-meta">发送前仍需由唯一网关检查最终内容及授权范围；失败不会清空输入。</p>
        <div className="t08-controls">
          <button
            type="submit"
            disabled={busy || !isCurrent || !modelAvailable || !props.onSubmit || !question.trim()}
          >
            发送问题
          </button>
          {(state?.phase === 'awaiting-provider' || state?.phase === 'executing-tools') &&
            props.onCancel && (
              <button
                type="button"
                disabled={!isCurrent}
                onClick={() => {
                  if (!isCurrent) return
                  try {
                    props.onCancel?.()
                  } catch {
                    updateInteraction({ localError: true })
                  }
                }}
              >
                取消本地等待
              </button>
            )}
        </div>
        {localError && (
          <p className="t08-warning" role="status">
            操作未完成，输入已保留。请检查实际任务状态后重试。
          </p>
        )}
        {busy && (
          <p role="status">
            {state?.phase === 'executing-tools'
              ? '正在等待本地工具；完成记录将持续保留。'
              : state?.phase === 'awaiting-provider'
                ? '正在等待响应；已发送数据无法撤回。'
                : '正在处理操作，输入将保留。'}
          </p>
        )}
      </form>
    </aside>
  )
}
