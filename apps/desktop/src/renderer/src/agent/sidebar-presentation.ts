import type { AgentConversation } from '../../../main/agent/conversation'
import type { PreparedDraft, ToolReceipt, TrustedContext } from '../../../main/agent/agent-service'
import type { AgentErrorCode } from '../../../main/agent/errors'
import type { ToolName } from '../../../main/agent/tools'
export type SidebarState = ReturnType<AgentConversation['state']>
export const toolLabels: Record<ToolName, string> = {
  ontology_read: '读取选中本体对象',
  ontology_propose: '本体草稿',
  mapping_propose: '映射草稿',
  query_draft: '查询草稿',
  query_execute: '本地查询',
  quality_check: '数据质量检查',
  reasoning_run: '推理',
  behavior_test: '行为样本测试',
  scenario_run: '沙盘运行',
  result_read: '读取运行记录',
}
export const resultLabels = {
  current: '当前结果',
  stale: '已过期，需重跑',
  historical: '历史结果',
  failed: '失败，不能据此认定通过',
  cancelled: '已取消，不能据此认定通过',
} as const
const errorText: Record<AgentErrorCode, string> = {
  INVALID_PROTOCOL: '模型响应不符合受测协议。',
  INVALID_JSON: '模型返回格式不正确。',
  INCOMPLETE_RESPONSE: '模型输出未完整结束。',
  TOOL_NOT_ALLOWED: '该工具或范围不在白名单中。',
  TOOL_UNAVAILABLE: '所需领域工具尚不可用。',
  INVALID_TOOL_ARGUMENTS: '工具参数不符合要求。',
  INVALID_EVIDENCE: '结果缺少有效依据或身份不匹配。',
  STALE_CONTEXT: '项目或输入版本已变化。',
  BUDGET_EXCEEDED: '本次操作已达请求上限。',
  BUSY: '本次操作仍在执行，请等待完成。',
  PROVIDER_DRIFT: '模型返回标识与受测配置不一致，请重新验证。',
  CANCELLED: '本地等待已取消；实际任务状态请查运行记录。',
  TIMED_OUT: '等待超时；实际任务状态请查运行记录。',
  TOOL_FAILED: '工具执行失败。',
}
export function describeAgentError(code: AgentErrorCode) {
  return errorText[code]
}
export function sidebarIsCurrent(state: SidebarState | null, current: TrustedContext) {
  return (
    !state ||
    (state.inputContext.projectId === current.projectId &&
      state.inputContext.projectRevision === current.projectRevision &&
      state.inputContext.inputSnapshotId === current.inputSnapshotId &&
      state.inputContext.scopeRef === current.scopeRef &&
      state.inputContext.module === current.module &&
      state.inputContext.mode === current.mode &&
      state.inputContext.selectedObjectIds.length === current.selectedObjectIds.length &&
      state.inputContext.selectedObjectIds.every(
        (id, index) => id === current.selectedObjectIds[index],
      ))
  )
}
export function canPreviewDraft(receipt: ToolReceipt, current: TrustedContext): boolean {
  const value = receipt.outcome
  return (
    value.kind === 'draft' &&
    'baseRevision' in value &&
    value.projectId === current.projectId &&
    value.baseRevision === current.projectRevision &&
    value.inputSnapshotId === current.inputSnapshotId &&
    value.requiresHumanDiffConfirmation === true
  )
}
export function preparedDraft(receipt: ToolReceipt): PreparedDraft | null {
  return receipt.outcome.kind === 'draft' && 'baseRevision' in receipt.outcome
    ? receipt.outcome
    : null
}
export function displayScalar(value: string | number | boolean | null) {
  return value === null
    ? '空值（null）'
    : typeof value === 'boolean'
      ? value
        ? 'true'
        : 'false'
      : String(value)
}
