/**
 * Cross-workspace Agent context. UI state only.
 *
 * Single source of truth for `{ projectId, module, mode, selectedObjectIds }`.
 * It never reads project data, never issues a ChangeSet and never authorizes
 * an outbound request: the host bridge remains the only authority for scope,
 * data range and permission.
 */
import type { AgentMode, AgentModule } from '@ontolearn/contracts'

/** Frozen upper bound for a selection payload (see `selectedObjectIds` schema). */
export const AGENT_SELECTED_OBJECT_LIMIT = 100

export type AgentContextSnapshot = Readonly<{
  projectId: string | null
  module: AgentModule
  mode: AgentMode
  selectedObjectIds: string[]
}>

export const emptyAgentContext: AgentContextSnapshot = Object.freeze({
  projectId: null,
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: Object.freeze([]) as unknown as string[],
})

/**
 * Preserve the caller's order, drop blanks and duplicates, and cap the list at
 * the frozen upper bound. Never reorders: the sidebar compares positions.
 */
export function normalizeSelectedObjectIds(ids: readonly string[]): string[] {
  const seen = new Set<string>()
  const result: string[] = []
  for (const id of ids) {
    if (typeof id !== 'string') continue
    const trimmed = id.trim()
    if (!trimmed || seen.has(trimmed)) continue
    seen.add(trimmed)
    result.push(trimmed)
    if (result.length >= AGENT_SELECTED_OBJECT_LIMIT) break
  }
  return result
}

export type AgentContextStore = {
  getSnapshot(): AgentContextSnapshot
  subscribe(listener: () => void): () => void
  setProjectId(projectId: string | null): void
  setModule(module: AgentModule): void
  setMode(mode: AgentMode): void
  setSelectedObjectIds(ids: readonly string[]): void
  reset(): void
}

export function createAgentContextStore(
  initial?: Partial<AgentContextSnapshot>,
): AgentContextStore {
  let state: AgentContextSnapshot = {
    projectId: initial?.projectId ?? null,
    module: initial?.module ?? emptyAgentContext.module,
    mode: initial?.mode ?? emptyAgentContext.mode,
    selectedObjectIds: normalizeSelectedObjectIds(initial?.selectedObjectIds ?? []),
  }
  const listeners = new Set<() => void>()
  function publish(next: AgentContextSnapshot) {
    if (
      next.projectId === state.projectId &&
      next.module === state.module &&
      next.mode === state.mode &&
      next.selectedObjectIds.length === state.selectedObjectIds.length &&
      next.selectedObjectIds.every((id, index) => id === state.selectedObjectIds[index])
    )
      return
    state = next
    for (const listener of [...listeners]) listener()
  }
  return {
    getSnapshot: () => state,
    subscribe: (listener) => {
      listeners.add(listener)
      return () => {
        listeners.delete(listener)
      }
    },
    setProjectId: (projectId) => publish({ ...state, projectId }),
    setModule: (module) => publish({ ...state, module }),
    setMode: (mode) => publish({ ...state, mode }),
    setSelectedObjectIds: (ids) =>
      publish({ ...state, selectedObjectIds: normalizeSelectedObjectIds(ids) }),
    reset: () => publish({ ...emptyAgentContext, selectedObjectIds: [] }),
  }
}

/** Process-wide instance shared by the shell and the workspace pages. */
export const agentContextStore: AgentContextStore = createAgentContextStore()

/**
 * FR-005: the mode is a *UI disclosure preference*. It is mirrored per project
 * in browser local storage only, so a reload keeps the user's choice. It is
 * never written into project data and never starts a ChangeSet.
 */
export function agentModeMirrorKey(projectId: string): string {
  return `ontolearn.agent.mode.${projectId}`
}

export function readAgentModeMirror(projectId: string): AgentMode {
  try {
    const stored = globalThis.localStorage?.getItem(agentModeMirrorKey(projectId)) ?? null
    return stored === 'project' ? 'project' : 'tutor'
  } catch {
    return 'tutor'
  }
}

export function writeAgentModeMirror(projectId: string, mode: AgentMode): boolean {
  try {
    globalThis.localStorage?.setItem(agentModeMirrorKey(projectId), mode)
    return true
  } catch {
    return false
  }
}
