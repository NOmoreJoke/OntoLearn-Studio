/** W3b S2-4: frozen Agent mode / privacy vocabulary and the shared context store. */
import { readFileSync } from 'node:fs'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import ts from 'typescript'
import { describe, expect, it, vi } from 'vitest'
import * as actions from '../../apps/desktop/src/renderer/src/agent/context-actions'
import * as presentation from '../../apps/desktop/src/renderer/src/agent/sidebar-presentation'
import {
  AGENT_SELECTED_OBJECT_LIMIT,
  agentModeMirrorKey,
  bindAgentArtifact,
  createAgentContextStore,
  isAgentArtifactCurrent,
  normalizeSelectedObjectIds,
  persistAgentMode,
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

describe('W3b B07: an upstream artefact only reaches the work bench of its own generation', () => {
  const artifact = { projectId: 'p1', generation: 4, value: { name: '查询草稿' } }

  it('delivers the artefact while the project and the generation still match', () => {
    expect(isAgentArtifactCurrent(artifact, 'p1', 4)).toBe(true)
    expect(bindAgentArtifact(artifact, 'p1', 4)).toEqual({ name: '查询草稿' })
  })

  it('never delivers the artefact of a retired project or generation', () => {
    expect(isAgentArtifactCurrent(artifact, 'p2', 4)).toBe(false)
    expect(isAgentArtifactCurrent(artifact, 'p1', 5)).toBe(false)
    expect(bindAgentArtifact(artifact, 'p2', 4)).toBeUndefined()
    expect(bindAgentArtifact(artifact, 'p1', 5)).toBeUndefined()
    expect(bindAgentArtifact(undefined, 'p1', 4)).toBeUndefined()
    expect(bindAgentArtifact(artifact, null, 4)).toBeUndefined()
    expect(bindAgentArtifact(artifact, 'p1', undefined)).toBeUndefined()
  })
})

describe('W3b B09: the host is the only authority for the assistant mode', () => {
  it('mirrors the mode only after the host really persisted it', async () => {
    const applied: string[] = []
    const result = await persistAgentMode({
      host: async () => ({ ok: true as const }),
      projectId: 'p1',
      mode: 'project',
      apply: (mode) => applied.push(mode),
    })
    expect(result.ok).toBe(true)
    expect(applied).toEqual(['project'])
  })

  it('never changes the local disclosure when the host refuses', async () => {
    const applied: string[] = []
    const result = await persistAgentMode({
      host: async () => ({ ok: false as const, code: 'STALE_CONTEXT' }),
      projectId: 'p1',
      mode: 'project',
      apply: (mode) => applied.push(mode),
    })
    expect(result).toEqual({ ok: false, code: 'STALE_CONTEXT' })
    expect(applied).toEqual([])
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

/* --------------------------------------------------------------------------
 * B07: a stale callback of an earlier visit of the same semantic key may
 * never write the current busy or error state.
 * ----------------------------------------------------------------------- */

type Node = { type: unknown; props: Record<string, unknown> }

function sidebarHarness() {
  const slots: unknown[] = []
  const effects: Array<{ deps: unknown[]; cleanup?: () => void }> = []
  const pending: Array<() => void> = []
  let cursor = 0
  let ids = 0
  const sameDeps = (left: unknown[], right: unknown[]) =>
    left.length === right.length && left.every((value, index) => Object.is(value, right[index]))
  const hooks = {
    useState: (initial: unknown) => {
      const index = cursor++
      if (!(index in slots))
        slots[index] = typeof initial === 'function' ? (initial as () => unknown)() : initial
      return [
        slots[index],
        (value: unknown) => {
          slots[index] =
            typeof value === 'function' ? (value as (old: unknown) => unknown)(slots[index]) : value
        },
      ]
    },
    useRef: (value: unknown) => {
      const index = cursor++
      if (!(index in slots)) slots[index] = { current: value }
      return slots[index]
    },
    useMemo: (callback: () => unknown) => callback(),
    useCallback: (callback: unknown, deps: unknown[] = []) => {
      const index = cursor++
      const slot = slots[index] as { deps: unknown[]; value: unknown } | undefined
      if (!slot || !sameDeps(slot.deps, deps)) slots[index] = { deps, value: callback }
      return (slots[index] as { value: unknown }).value
    },
    useEffect: (callback: () => void | (() => void), deps: unknown[] = []) => {
      const index = cursor++
      const previous = effects[index]
      if (previous && sameDeps(previous.deps, deps)) return
      previous?.cleanup?.()
      effects[index] = { deps, cleanup: undefined }
      pending.push(() => {
        const result = callback()
        effects[index].cleanup = typeof result === 'function' ? result : undefined
      })
    },
    useLayoutEffect: (callback: () => void | (() => void)) => {
      callback()
    },
    useId: () => `id-${++ids}`,
  }
  const jsx = (type: unknown, props: Record<string, unknown>) => ({ type, props })
  const code = ts.transpileModule(
    readFileSync('apps/desktop/src/renderer/src/agent/AgentSidebar.tsx', 'utf8'),
    {
      compilerOptions: {
        target: ts.ScriptTarget.ES2022,
        module: ts.ModuleKind.CommonJS,
        jsx: ts.JsxEmit.ReactJSX,
      },
    },
  ).outputText
  const exported: Record<string, unknown> = {}
  new Function('require', 'exports', code)((name: string) => {
    if (name === 'react') return hooks
    if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx }
    if (name === './context-actions') return actions
    if (name === './sidebar-presentation') return presentation
    if (name === './agent-sidebar.css') return {}
    throw Error(`Unexpected renderer dependency ${name}`)
  }, exported)
  const Component = exported.AgentSidebar as unknown as (props: Record<string, unknown>) => Node
  let props: Record<string, unknown> = {
    context,
    state: null,
    privacy: 'minimal',
    modelReady: true,
    localActions: ['hint'],
  }
  let tree: Node
  function render() {
    cursor = 0
    tree = Component(props)
    for (const callback of pending.splice(0)) callback()
  }
  function nodes(value: unknown): Node[] {
    if (Array.isArray(value)) return value.flatMap((item) => nodes(item))
    if (!value || typeof value !== 'object' || !('type' in value)) return []
    const node = value as Node
    return [node, ...nodes(node.props.children)]
  }
  function textOf(value: unknown): string {
    if (Array.isArray(value)) return value.map(textOf).join('')
    if (value && typeof value === 'object' && 'props' in value)
      return textOf((value as Node).props.children)
    return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
  }
  render()
  return {
    render,
    unmount() {
      for (const effect of effects) effect?.cleanup?.()
      effects.length = 0
    },
    setProps(next: Record<string, unknown>) {
      props = { ...props, ...next }
      render()
    },
    nodes: () => nodes(tree),
    text: () => textOf(tree),
    find: (testId: string) => nodes(tree).find((node) => node.props['data-testid'] === testId),
    textarea: () => nodes(tree).find((node) => node.type === 'textarea'),
  }
}

const flush = () => new Promise((resolve) => setTimeout(resolve, 0))

describe('W3b B07: an earlier visit of the same context never writes the current state', () => {
  it('drops the stale failure of A -> B -> A and keeps the editable question', async () => {
    const sidebar = sidebarHarness()
    const question = sidebar.textarea()!
    ;(question.props.onChange as (event: unknown) => void)({ target: { value: '我的问题' } })
    sidebar.render()
    expect(sidebar.textarea()!.props.value).toBe('我的问题')
    let rejectMode: ((reason: Error) => void) | undefined
    const pendingMode = new Promise<void>((_, reject) => {
      rejectMode = reject
    })
    sidebar.setProps({ onModeChange: () => pendingMode })
    ;(sidebar.find('agent-mode-toggle')!.props.onClick as () => void)()
    // A -> B -> A: the same semantic key is entered a second time.
    sidebar.setProps({ context: { ...context, projectId: 'p2' } })
    sidebar.setProps({ context })
    rejectMode!(new Error('STALE_CONTEXT'))
    await flush()
    sidebar.render()
    expect(sidebar.text()).not.toContain('操作未完成，输入已保留')
    // The editable question of the same key is never thrown away.
    expect(sidebar.textarea()!.props.value).toBe('我的问题')
    sidebar.unmount()
  })
})
