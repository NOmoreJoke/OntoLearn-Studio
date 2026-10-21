/** UI policy only. Actual handlers are provided by approved local pages/T09 or T08 wiring. */
export type AgentPage =
  'learn' | 'ontology' | 'mapping' | 'query' | 'quality' | 'behavior' | 'scenario'
export type AgentAction = 'hint' | 'check' | 'demonstrate' | 'explain'
const labels: Record<AgentAction, string> = {
  hint: '给我一点提示',
  check: '检查我的操作',
  demonstrate: '演示下一步',
  explain: '解释当前结果',
}
const pageActions: Record<AgentPage, readonly AgentAction[]> = {
  learn: ['hint', 'check', 'demonstrate', 'explain'],
  ontology: ['hint', 'check', 'demonstrate'],
  mapping: ['hint', 'check', 'demonstrate'],
  query: ['hint', 'check', 'explain'],
  quality: ['hint', 'check', 'explain'],
  behavior: ['hint', 'check', 'explain'],
  scenario: ['hint', 'check', 'explain'],
}
export function contextActions(
  page: AgentPage,
  modelAvailable: boolean,
  localHandlers: readonly AgentAction[],
) {
  return pageActions[page].map((action) => ({
    action,
    label: labels[action],
    target: modelAvailable
      ? ('agent' as const)
      : localHandlers.includes(action)
        ? ('local' as const)
        : ('unavailable' as const),
    availabilityText: modelAvailable
      ? '模型增强'
      : localHandlers.includes(action)
        ? '离线本地功能'
        : '本地服务尚未接线',
  }))
}
export function assistanceLevel(mode: 'tutor' | 'project', action: AgentAction) {
  return action === 'demonstrate' || mode === 'project' ? 'full-assistance' : 'hint'
}
