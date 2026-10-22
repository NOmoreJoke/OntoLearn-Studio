import { formatValue, type BehaviorResult } from './model'
export const errorText = {
  conflict: '竞争写入冲突；请检查不同触发实例是否写入同一单值属性的不同值。',
  invalid_input: '输入未通过执行服务验证；请检查对象、条件和动作。',
  unavailable: '执行能力当前不可用；请恢复连接后对账。',
  execution_failed: '执行失败；本轮未取得成功提交证据。',
  cancel_failed: '取消未成功收尾；请刷新运行状态。',
}
export function resultHeading(result: BehaviorResult): string {
  const state = {
    candidate: '候选计划 · 尚未提交',
    completed: '隔离副本已提交',
    failed: '运行失败 · 本轮未提交',
    cancelled: '运行已取消 · 本轮未提交',
  }[result.state]
  const freshness = { current: '当前输入', stale: '已过期', historical: '历史结果' }[
    result.freshness
  ]
  return `${state} / ${freshness}`
}
export function resultSections(result: BehaviorResult) {
  return {
    conditions: result.conditions.map(
      (item) =>
        `${item.eventId} / ${item.behaviorId} · ${item.triggered ? '触发' : '未触发'} · ${item.reason}`,
    ),
    actions: result.actions.map(
      (item) =>
        `${item.eventId} / ${item.behaviorId} · 动作 ${item.index + 1} · ${{ create: '创建个体', update: '更新属性', relate: '添加关系', notify: '通知记录' }[item.kind]} · ${{ planned: '计划', applied: '已执行', deduplicated: '同值去重', rolled_back: '已回滚', skipped: '未执行' }[item.state]} · ${item.detail}`,
    ),
    added: result.diff.added.map(
      (item) => `${item.object} · ${item.property} · ${formatValue(item.value)}`,
    ),
    removed: result.diff.removed.map(
      (item) => `${item.object} · ${item.property} · ${formatValue(item.value)}`,
    ),
    notifications: result.notifications.map(
      (item) =>
        `${item.eventId} / ${item.behaviorId} · ${{ candidate: '候选', recorded: '隔离记录', discarded: '已丢弃' }[item.state]} · ${item.message}`,
    ),
  }
}
