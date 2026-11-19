/** UI policy only. Actual handlers are provided by approved local pages/T09 or T08 wiring. */
import type { AgentMode, AgentModule } from '@ontolearn/contracts'

/** The frozen module vocabulary (see `agentModuleSchema`). */
export type AgentPage = AgentModule
export type AgentAction = 'hint' | 'check' | 'demonstrate' | 'explain'
/** Every workspace renders at most this many quick actions. */
export const AGENT_MAX_QUICK_ACTIONS = 4
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
/** Transfer uses the learning context because the frozen Agent contract has no transfer module. */
export function toAgentModule(workspace: AgentModule | 'transfer'): AgentModule {
  return workspace === 'transfer' ? 'learn' : workspace
}
export function contextActions(
  page: AgentPage,
  modelAvailable: boolean,
  localHandlers: readonly AgentAction[],
) {
  return pageActions[page].slice(0, AGENT_MAX_QUICK_ACTIONS).map((action) => ({
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
export function assistanceLevel(mode: AgentMode, action: AgentAction) {
  return action === 'demonstrate' || mode === 'project' ? 'full-assistance' : 'hint'
}
