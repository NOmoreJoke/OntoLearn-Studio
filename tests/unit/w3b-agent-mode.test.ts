/** W3b S2-4: frozen Agent mode / privacy vocabulary and the shared context store. */
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi } from 'vitest'
import {
  AGENT_SELECTED_OBJECT_LIMIT,
  agentModeMirrorKey,
  createAgentContextStore,
  normalizeSelectedObjectIds,
  readAgentModeMirror,
  writeAgentModeMirror,
} from '../../apps/desktop/src/renderer/src/agent/agent-context-store'
import {
  AGENT_MAX_QUICK_ACTIONS,
  contextActions,
  toAgentModule,
} from '../../apps/desktop/src/renderer/src/agent/context-actions'
import { AgentSidebar } from '../../apps/desktop/src/renderer/src/agent/AgentSidebar'
import type { TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'

const context: TrustedContext = {
  projectId: 'p1',
  projectRevision: 3,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: ['urn:a'],
}
const render = (overrides: Record<string, unknown> = {}) =>
  renderToStaticMarkup(
    createElement(AgentSidebar, {
      context,
      state: null,
      privacy: 'minimal',
      modelReady: false,
      localActions: ['hint'],
      ...overrides,
    }),
  )

describe('W3b S2-4: shared Agent context store', () => {
  it('keeps one source of truth for project, module, mode and selection', () => {
    const store = createAgentContextStore()
    expect(store.getSnapshot()).toEqual({
      projectId: null,
      module: 'query',
      mode: 'tutor',
      selectedObjectIds: [],
    })
    store.setProjectId('p1')
    store.setModule('ontology')
    store.setMode('project')
    store.setSelectedObjectIds(['urn:b', 'urn:a'])
    expect(store.getSnapshot()).toEqual({
      projectId: 'p1',
      module: 'ontology',
      mode: 'project',
      selectedObjectIds: ['urn:b', 'urn:a'],
    })
  })

  it('notifies subscribers only on a real change and can be released', () => {
    const store = createAgentContextStore()
    let calls = 0
    const release = store.subscribe(() => {
      calls++
    })
    store.setMode('project')
    expect(calls).toBe(1)
    store.setMode('project')
    expect(calls).toBe(1)
    store.setSelectedObjectIds(['urn:a'])
    expect(calls).toBe(2)
    release()
    store.setMode('tutor')
    expect(calls).toBe(2)
  })

  it('preserves the selection order, drops blanks and duplicates, and caps the list', () => {
    const many = Array.from({ length: 150 }, (_, index) => `urn:${index}`)
    const normalized = normalizeSelectedObjectIds([' urn:b ', 'urn:a', 'urn:b', '', '   ', 'urn:a'])
    expect(normalized).toEqual(['urn:b', 'urn:a'])
    const capped = normalizeSelectedObjectIds(many)
    expect(capped).toHaveLength(AGENT_SELECTED_OBJECT_LIMIT)
    expect(capped[0]).toBe('urn:0')
    expect(capped.at(-1)).toBe(`urn:${AGENT_SELECTED_OBJECT_LIMIT - 1}`)
  })

  it('mirrors the mode per project in browser storage only (FR-005)', () => {
    const storage = new Map<string, string>()
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => storage.get(key) ?? null,
      setItem: (key: string, value: string) => void storage.set(key, value),
      removeItem: (key: string) => void storage.delete(key),
    })
    expect(agentModeMirrorKey('p1')).toBe('ontolearn.agent.mode.p1')
    expect(readAgentModeMirror('p1')).toBe('tutor')
    expect(writeAgentModeMirror('p1', 'project')).toBe(true)
    expect(readAgentModeMirror('p1')).toBe('project')
    expect(storage.get('ontolearn.agent.mode.p1')).toBe('project')
    // Another project keeps its own preference.
    expect(readAgentModeMirror('p2')).toBe('tutor')
    vi.unstubAllGlobals()
  })

  it('falls back to the tutor mode when the browser storage is unavailable', () => {
    vi.stubGlobal('localStorage', {
      getItem: () => {
        throw new Error('blocked')
      },
      setItem: () => {
        throw new Error('blocked')
      },
    })
    expect(readAgentModeMirror('p1')).toBe('tutor')
    expect(writeAgentModeMirror('p1', 'project')).toBe(false)
    vi.unstubAllGlobals()
  })
})

describe('W3b S2-4: frozen module and quick-action policy', () => {
  it('maps every shell workspace onto the frozen module vocabulary', () => {
    expect(toAgentModule('query')).toBe('query')
    expect(toAgentModule('ontology')).toBe('ontology')
    expect(toAgentModule('quality')).toBe('quality')
    expect(toAgentModule('learn')).toBe('learn')
    expect(toAgentModule('mapping')).toBe('mapping')
    expect(toAgentModule('behavior')).toBe('behavior')
    expect(toAgentModule('scenario')).toBe('scenario')
  })

  it('offers at most four actions and keeps an unwired action unavailable', () => {
    for (const page of [
      'learn',
      'ontology',
      'mapping',
      'query',
      'quality',
      'behavior',
      'scenario',
    ] as const) {
      const actions = contextActions(page, false, ['hint'])
      expect(actions.length).toBeLessThanOrEqual(AGENT_MAX_QUICK_ACTIONS)
      expect(actions.every((action) => action.action)).toBe(true)
      const unavailable = actions.filter((action) => action.target === 'unavailable')
      expect(unavailable.length).toBeGreaterThan(0)
      expect(unavailable.every((action) => action.availabilityText === '本地服务尚未接线')).toBe(
        true,
      )
      expect(actions.find((action) => action.action === 'hint')?.target).toBe('local')
    }
    expect(contextActions('query', true, []).every((action) => action.target === 'agent')).toBe(
      true,
    )
  })
})

describe('W3b S2-4: AgentSidebar privacy vocabulary and mode switch', () => {
  it('uses the frozen privacy words and never shows the retired one', () => {
    expect(render({ privacy: 'local' })).toContain('完全本地')
    expect(render({ privacy: 'minimal' })).toContain('最小上下文')
    expect(render({ privacy: 'project' })).toContain('项目上下文')
    const html = render({ privacy: 'minimal' })
    expect(html).not.toContain('minimum')
    expect(html).not.toContain('最小上下文和项目上下文')
  })

  it('reads the retired privacy word as the frozen minimal level', () => {
    const html = render({ privacy: 'minimum' })
    expect(html).toContain('最小上下文')
    expect(html).not.toContain('minimum')
  })

  it('renders a stable mode switch that stays disabled without a handler', () => {
    const html = render()
    expect(html).toContain('data-testid="agent-mode-toggle"')
    expect(html).toMatch(/<button type="button" data-testid="agent-mode-toggle" disabled=""/)
    expect(html).toContain('切换到项目模式')
  })

  it('enables the mode switch as soon as the host supplies a handler', () => {
    const html = render({ onModeChange: () => undefined })
    expect(html).toContain('data-testid="agent-mode-toggle"')
    expect(html).not.toMatch(/data-testid="agent-mode-toggle" disabled/)
    expect(html).toContain('切换到项目模式')
  })

  it('offers the project mode switch when the context already is in project mode', () => {
    const html = render({ context: { ...context, mode: 'project' }, onModeChange: () => undefined })
    expect(html).toContain('切换到导师模式')
  })

  it('keeps the stable test ids for the container, the quick actions and every action', () => {
    const html = render()
    expect(html).toContain('data-testid="agent-sidebar"')
    expect(html).toContain('data-testid="agent-quick-actions"')
    for (const action of ['hint', 'check', 'explain']) {
      expect(html).toContain(`data-testid="agent-action-${action}"`)
    }
    expect(html).toContain('aria-label="页面快捷动作"')
  })
})
