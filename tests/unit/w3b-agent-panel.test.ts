/** W3b S2-4: the workspace Agent panel consumes the named bridge, never project data. */
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import ts from 'typescript'
import { describe, expect, it, vi } from 'vitest'
import * as contracts from '@ontolearn/contracts'
import type {
  AgentDraftPlanDTO,
  AgentReceiptDTO,
  AgentStateDTO,
  ChangeSetManifest,
  ChangeSetPage,
  ChangeSetPreview,
  DesktopBridge,
} from '@ontolearn/contracts'
import {
  AgentPanel,
  agentContextMatches,
  agentDtoToSidebarState,
  queryDraftFromDetail,
  queryDraftFromPlan,
} from '../../apps/desktop/src/renderer/src/agent/agent-panel'
import * as agentSidebarModule from '../../apps/desktop/src/renderer/src/agent/AgentSidebar'
import * as contextActionsModule from '../../apps/desktop/src/renderer/src/agent/context-actions'
import * as queryDraftModule from '../../apps/desktop/src/renderer/src/query/draft'
import {
  DraftDiffPreview,
  commitDraftDiff,
  draftIdentityOf,
  prepareDraftDiff,
} from '../../apps/desktop/src/renderer/src/ontology/draft-diff-preview'
import type { TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'

const { AgentSidebar, agentDraftIsCurrent } = agentSidebarModule

// The unit program does not include the renderer's `env.d.ts`; the same
// optional bridge declaration is repeated here so the real renderer modules
// keep their exact types under `npm run typecheck:unit`.
declare global {
  interface Window {
    ontolearn?: DesktopBridge
  }
}

const context: TrustedContext = {
  projectId: 'p1',
  projectRevision: 3,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'ontology',
  mode: 'tutor',
  selectedObjectIds: [],
}
const draftReceipt: AgentReceiptDTO = {
  callId: 'call-1',
  tool: 'ontology_propose',
  purpose: 'suggest',
  outcome: {
    kind: 'draft',
    draftType: 'ontology',
    summary: '建立设备类',
    detail: '新增 urn:Equipment',
    projectId: 'p1',
    baseRevision: 3,
    inputSnapshotId: 's1',
    requiresHumanDiffConfirmation: true,
  },
}
const evidenceReceipt: AgentReceiptDTO = {
  callId: 'call-2',
  tool: 'query_execute',
  purpose: 'explain',
  outcome: {
    kind: 'evidence',
    projectId: 'p1',
    inputSnapshotId: 's1',
    scopeRef: 'scope1',
    resultId: 'result-1',
    status: 'current',
    traceRefs: ['trace-1'],
    fields: [{ fieldId: 'id', value: '001' }],
  },
}
const failureReceipt: AgentReceiptDTO = {
  callId: 'call-3',
  tool: 'query_execute',
  purpose: 'review',
  outcome: { kind: 'failure', code: 'TOOL_UNAVAILABLE' },
}

describe('W3b S2-4: AgentPanel host wiring', () => {
  it('offers nothing at all while no project is selected', () => {
    const html = renderToStaticMarkup(
      createElement(AgentPanel, {
        projectId: null,
        projectRevision: null,
        inputSnapshotId: null,
        module: 'query',
        mode: 'tutor',
        selectedObjectIds: [],
        localActions: [],
      }),
    )
    expect(html).toContain('data-testid="agent-panel"')
    expect(html).toContain('尚未打开项目')
    expect(html).not.toContain('data-testid="agent-quick-actions"')
    expect(html).not.toContain('<button')
  })

  it('does not offer an action before the real bridge context arrived', () => {
    const html = renderToStaticMarkup(
      createElement(AgentPanel, {
        projectId: 'p1',
        projectRevision: 3,
        inputSnapshotId: 's1',
        module: 'ontology',
        mode: 'tutor',
        selectedObjectIds: [],
        localActions: ['hint'],
      }),
    )
    expect(html).toContain('data-testid="agent-panel"')
    expect(html).toContain('助手上下文尚未就绪')
    expect(html).not.toContain('data-testid="agent-quick-actions"')
  })
})

describe('W3b S2-4: upstream query drafts are validated before they reach the editor', () => {
  it('accepts a fully valid upstream draft and marks it as a model draft', () => {
    const draft = queryDraftFromDetail(
      JSON.stringify({
        name: '列出设备',
        description: '来自上游',
        sparql: 'SELECT * WHERE { ?s ?p ?o }',
        scope: 'asserted',
        capabilityQuestion: '有哪些设备？',
        source: 'model',
      }),
    )
    expect(draft).toEqual({
      name: '列出设备',
      description: '来自上游',
      sparql: 'SELECT * WHERE { ?s ?p ?o }',
      scope: 'asserted',
      capabilityQuestion: '有哪些设备？',
      source: 'model',
    })
  })

  it('never accepts an invalid or non-JSON upstream payload', () => {
    expect(queryDraftFromDetail('not json')).toBeUndefined()
    expect(queryDraftFromDetail(JSON.stringify({ name: 'x' }))).toBeUndefined()
    expect(
      queryDraftFromDetail(JSON.stringify({ ...{ name: 'x' }, sparql: '   ' })),
    ).toBeUndefined()
  })

  it('derives a validated query draft from a host-built change plan', () => {
    const plan: AgentDraftPlanDTO = {
      operationId: 'op-1',
      draftType: 'query',
      baseRevision: 3,
      inputSnapshotId: 's1',
      summary: '列出设备',
      plan: {
        definitions: [
          {
            layer: 'query',
            id: 'q1',
            value: {
              text: 'SELECT * WHERE { ?s ?p ?o }',
              references: [],
              descriptor: {
                name: '列出设备',
                description: '',
                scope: 'asserted',
                capabilityQuestion: '',
                source: 'model',
                version: 1,
              },
            },
          },
        ],
      },
    }
    expect(queryDraftFromPlan(plan)).toEqual({
      name: '列出设备',
      description: '',
      sparql: 'SELECT * WHERE { ?s ?p ?o }',
      scope: 'asserted',
      capabilityQuestion: '',
      source: 'model',
    })
  })

  it('returns nothing when the plan carries no query definition', () => {
    const plan: AgentDraftPlanDTO = {
      operationId: 'op-1',
      draftType: 'ontology',
      baseRevision: 3,
      inputSnapshotId: 's1',
      summary: '建立设备类',
      plan: { manual: [] },
    }
    expect(queryDraftFromPlan(plan)).toBeUndefined()
  })
})

describe('W3b S2-4: bridge receipts are rendered with stable ids and a real diff gate', () => {
  const render = (overrides: Record<string, unknown> = {}) =>
    renderToStaticMarkup(
      createElement(AgentSidebar, {
        context,
        state: null,
        receipts: [draftReceipt, evidenceReceipt, failureReceipt],
        privacy: 'minimal',
        modelReady: true,
        localActions: ['hint'],
        ...overrides,
      }),
    )

  it('renders every real receipt with its own stable id', () => {
    const html = render()
    expect(html).toContain('data-testid="agent-receipt-call-1"')
    expect(html).toContain('data-testid="agent-receipt-call-2"')
    expect(html).toContain('data-testid="agent-receipt-call-3"')
    expect(html).toContain('建立设备类')
    expect(html).toContain('001')
    expect(html).toContain('trace-1')
  })

  it('marks a failed receipt explicitly and never as a passed check', () => {
    const html = render()
    expect(html).toContain('data-testid="agent-failure"')
    expect(html).toContain('TOOL_UNAVAILABLE')
    expect(html).not.toContain('检查通过')
  })

  it('only enables the real diff for a draft bound to the current context', () => {
    expect(agentDraftIsCurrent(draftReceipt, context)).toBe(true)
    expect(agentDraftIsCurrent(draftReceipt, { ...context, projectRevision: 4 })).toBe(false)
    expect(agentDraftIsCurrent(draftReceipt, { ...context, projectId: 'p2' })).toBe(false)
    expect(agentDraftIsCurrent(draftReceipt, { ...context, inputSnapshotId: 's2' })).toBe(false)
    expect(agentDraftIsCurrent(evidenceReceipt, context)).toBe(false)

    const enabled = render({ onPreviewAgentDraft: () => undefined })
    expect(enabled).toMatch(/<button type="button">查看真实 Diff<\/button>/)
    const disabled = render({
      onPreviewAgentDraft: () => undefined,
      context: { ...context, projectRevision: 4 },
    })
    expect(disabled).toMatch(/<button type="button" disabled="">查看真实 Diff<\/button>/)
    const withoutHandler = render()
    expect(withoutHandler).toMatch(/<button type="button" disabled="">查看真实 Diff<\/button>/)
  })
})

describe('W3b S2-4: the Agent draft diff never commits before the full document was verified', () => {
  const plan: AgentDraftPlanDTO = {
    operationId: 'op-1',
    draftType: 'ontology',
    baseRevision: 3,
    inputSnapshotId: 's1',
    summary: '建立设备类',
    plan: { manual: [] },
  }

  it('renders an empty state while no draft plan exists', () => {
    const html = renderToStaticMarkup(createElement(DraftDiffPreview, { projectId: 'p1' }))
    expect(html).toContain('data-testid="ontology-draft-diff"')
    expect(html).toContain('尚无 Agent 草稿差异可核对')
    expect(html).not.toContain('data-testid="ontology-draft-commit"')
  })

  it('shows the plan facts but no commit control before the diff was verified', () => {
    const html = renderToStaticMarkup(createElement(DraftDiffPreview, { projectId: 'p1', plan }))
    expect(html).toContain('data-testid="ontology-draft-summary"')
    expect(html).toContain('建立设备类')
    expect(html).toContain('基准版本 3')
    expect(html).not.toContain('data-testid="ontology-draft-commit"')
    expect(html).not.toContain('data-testid="ontology-draft-consent"')
  })
})

/* --------------------------------------------------------------------------
 * B06: one mount, many drafts. The view, the consent and the commit must
 * always belong to the draft the user is actually looking at.
 * ----------------------------------------------------------------------- */

const hash = (value: Uint8Array) => createHash('sha256').update(value).digest('hex')
const diffProjectId = '00000000-0000-4000-8000-000000000001'
const diffPreviewHash = 'b'.repeat(64)
const diffRows = [{ resource: ['fact', 'f1'], before: null, after: { subject: 'urn:Pump' } }]

function diffFixture(): { manifest: ChangeSetManifest; page: ChangeSetPage } {
  const raw = Buffer.from(JSON.stringify(diffRows), 'utf8')
  const segment = {
    ordinal: 0,
    byteOffset: 0,
    rawByteLength: raw.length,
    sha256: hash(raw),
    dataBase64: raw.toString('base64'),
  }
  const manifest: ChangeSetManifest = {
    documentKind: 'diff',
    documentHash: hash(raw),
    totalBytes: raw.length,
    segmentCount: 1,
    segments: [
      {
        ordinal: segment.ordinal,
        byteOffset: segment.byteOffset,
        rawByteLength: segment.rawByteLength,
        sha256: segment.sha256,
      },
    ],
  }
  return {
    manifest,
    page: {
      projectId: diffProjectId,
      previewHash: diffPreviewHash,
      documentKind: 'diff',
      documentHash: manifest.documentHash,
      segments: [segment],
      nextCursor: '00000000-0000-4000-8000-000000000004',
      complete: true,
    },
  }
}

const { manifest, page } = diffFixture()
const previewReady: ChangeSetPreview = {
  status: 'ready',
  projectId: diffProjectId,
  baseRevision: 3,
  previewHash: diffPreviewHash,
  preparedPlanRef: 'prepared-plan-1',
  inputSnapshotId: 's1',
  parametersHash: 'c'.repeat(64),
  intent: 'change',
  targetOperationId: null,
  summary: '建立设备类',
  manifest,
}
const draftPlan = (operationId: string): AgentDraftPlanDTO => ({
  operationId,
  draftType: 'ontology',
  baseRevision: 3,
  inputSnapshotId: 's1',
  summary: '建立设备类',
  plan: { manual: [] },
})

describe('W3b B06: a new draft retires the previous difference and the previous consent', () => {
  it('gives every draft its own identity', () => {
    const first = draftIdentityOf(draftPlan('op-1'), 'p1')
    const second = draftIdentityOf(draftPlan('op-2'), 'p1')
    expect(first).not.toBe(second)
    expect(first).toContain('op-1')
    expect(draftIdentityOf(undefined, 'p1')).toBe('')
    expect(draftIdentityOf(draftPlan('op-1'), null)).toBe('')
  })

  it('drops an outdated prepare answer instead of overwriting the current one', async () => {
    const bridge = {
      previewProjectChangeset: async () => ({ ok: true as const, data: previewReady }),
      getProjectDiffPage: async () => ({ ok: true as const, data: page }),
      confirmProjectChangeset: async () => ({ ok: true as const, data: confirmationFixture() }),
      commitAgentDraft: async () => ({ ok: true as const, data: {} as never }),
    }
    const outcome = await prepareDraftDiff({
      bridge,
      plan: draftPlan('op-1'),
      projectId: diffProjectId,
      isCurrent: () => false,
    })
    expect(outcome.status).toBe('stale')
  })

  it('refuses a confirmation that describes another preview', async () => {
    const bridge = {
      previewProjectChangeset: async () => ({ ok: true as const, data: previewReady }),
      getProjectDiffPage: async () => ({ ok: true as const, data: page }),
      confirmProjectChangeset: async () => ({
        ok: true as const,
        data: { ...confirmationFixture(), inputSnapshotId: 'other' },
      }),
      commitAgentDraft: async () => ({ ok: true as const, data: {} as never }),
    }
    await expect(
      commitDraftDiff({
        bridge,
        plan: draftPlan('op-1'),
        preview: previewReady,
        completionCursor: page.nextCursor,
        isCurrent: () => true,
      }),
    ).rejects.toThrow('INVALID_CONFIRMATION')
  })

  it('never commits an outdated draft', async () => {
    const commit = vi.fn(async () => ({ ok: true as const, data: {} as never }))
    const bridge = {
      previewProjectChangeset: async () => ({ ok: true as const, data: previewReady }),
      getProjectDiffPage: async () => ({ ok: true as const, data: page }),
      confirmProjectChangeset: async () => ({ ok: true as const, data: confirmationFixture() }),
      commitAgentDraft: commit,
    }
    const outcome = await commitDraftDiff({
      bridge,
      plan: draftPlan('op-1'),
      preview: previewReady,
      completionCursor: page.nextCursor,
      isCurrent: () => false,
    })
    expect(outcome.status).toBe('stale')
    expect(commit).not.toHaveBeenCalled()
  })
})

function confirmationFixture() {
  return {
    projectId: diffProjectId,
    previewHash: diffPreviewHash,
    preparedPlanRef: 'prepared-plan-1',
    confirmationRef: '00000000-0000-4000-8000-000000000006',
    inputSnapshotId: 's1',
    parametersHash: 'c'.repeat(64),
  }
}

type Node = { type: unknown; props: Record<string, unknown> }

function createTsxHarness(
  sourceFile: string,
  exportName: string,
  initialProps: Record<string, unknown>,
  extraRequires: Record<string, unknown> = {},
) {
  const slots: unknown[] = []
  const effects: Array<{ deps: unknown[]; cleanup?: () => void }> = []
  const pending: Array<() => void> = []
  let cursor = 0
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
      // React runs the previous cleanup before the next effect of the same hook.
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
  }
  const jsx = (type: unknown, props: Record<string, unknown>) => ({ type, props })
  const code = ts.transpileModule(readFileSync(sourceFile, 'utf8'), {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      jsx: ts.JsxEmit.ReactJSX,
    },
  }).outputText
  const exported: Record<string, unknown> = {}
  new Function('require', 'exports', code)((name: string) => {
    if (name === 'react') return hooks
    if (name === 'react/jsx-runtime') return { jsx, jsxs: jsx }
    if (name === '@ontolearn/contracts') return contracts
    if (name in extraRequires) return extraRequires[name]
    throw Error(`Unexpected renderer dependency ${name}`)
  }, exported)
  const Component = exported[exportName] as unknown as (props: Record<string, unknown>) => Node
  let props: Record<string, unknown> = { ...initialProps }
  let tree: Node
  function render() {
    cursor = 0
    tree = Component(props)
    for (const callback of pending.splice(0)) callback()
  }
  render()
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
    findButton: (label: string) =>
      nodes(tree).find(
        (node) => node.type === 'button' && textOf(node.props.children).includes(label),
      ),
  }
}

function diffHarness(bridge: Record<string, unknown>) {
  void bridge
  return createTsxHarness(
    'apps/desktop/src/renderer/src/ontology/draft-diff-preview.tsx',
    'DraftDiffPreview',
    {
      projectId: diffProjectId,
      plan: draftPlan('op-1'),
    },
  )
}

function agentPanelHarness(initialProps: Record<string, unknown>) {
  return createTsxHarness(
    'apps/desktop/src/renderer/src/agent/agent-panel.tsx',
    'AgentPanel',
    initialProps,
    {
      './AgentSidebar': agentSidebarModule,
      './context-actions': contextActionsModule,
      '../query/draft': queryDraftModule,
    },
  )
}

const flush = () => new Promise((resolve) => setTimeout(resolve, 0))
const flushAll = async () => {
  for (let turn = 0; turn < 12; turn++) await flush()
}

describe('W3b B06: the draft diff view follows exactly one draft', () => {
  it('clears the rows, the consent and the commit control when the plan changes', async () => {
    vi.stubGlobal('window', {
      ontolearn: {
        previewProjectChangeset: async () => ({ ok: true, data: previewReady }),
        getProjectDiffPage: async () => ({ ok: true, data: page }),
        confirmProjectChangeset: async () => ({ ok: true, data: confirmationFixture() }),
        commitAgentDraft: async () => ({ ok: true, data: {} }),
      },
    })
    const panel = diffHarness({})
    await flushAll()
    panel.render()
    expect(panel.find('ontology-draft-commit')).toBeTruthy()
    panel.setProps({ plan: draftPlan('op-2') })
    expect(panel.find('ontology-draft-commit')).toBeUndefined()
    expect(panel.find('ontology-draft-consent')).toBeUndefined()
    expect(panel.text()).not.toContain('urn:Pump')
    panel.unmount()
    vi.unstubAllGlobals()
  })

  it('never lets an outdated prepare answer overwrite the current difference', async () => {
    const gates: Array<() => void> = []
    vi.stubGlobal('window', {
      ontolearn: {
        previewProjectChangeset: async () => {
          await new Promise<void>((resolve) => gates.push(resolve))
          return { ok: true, data: previewReady }
        },
        getProjectDiffPage: async () => ({ ok: true, data: page }),
        confirmProjectChangeset: async () => ({ ok: true, data: confirmationFixture() }),
        commitAgentDraft: async () => ({ ok: true, data: {} }),
      },
    })
    const panel = diffHarness({})
    await flushAll()
    // The first draft is still waiting for its answer.
    expect(gates.length).toBe(1)
    panel.setProps({ plan: draftPlan('op-2') })
    await flushAll()
    expect(gates.length).toBe(2)
    // The second draft answers first, the first one only afterwards.
    gates[1]!()
    await flushAll()
    panel.render()
    expect(panel.find('ontology-draft-commit')).toBeTruthy()
    gates[0]!()
    await flushAll()
    panel.render()
    expect(panel.find('ontology-draft-commit')).toBeTruthy()
    expect(panel.text()).toContain('建立设备类')
    panel.unmount()
    vi.unstubAllGlobals()
  })

  it('disables the re-prepare control while a preparation is running', async () => {
    vi.stubGlobal('window', {
      ontolearn: {
        previewProjectChangeset: async () => {
          await new Promise<void>(() => {})
          return { ok: true, data: previewReady }
        },
        getProjectDiffPage: async () => ({ ok: true, data: page }),
        confirmProjectChangeset: async () => ({ ok: true, data: confirmationFixture() }),
        commitAgentDraft: async () => ({ ok: true, data: {} }),
      },
    })
    const panel = diffHarness({})
    await flushAll()
    panel.render()
    const button = panel.findButton('重新生成并核对差异')!
    expect(button.props.disabled).toBe(true)
    panel.unmount()
    vi.unstubAllGlobals()
  })

  it('stops requesting further diff pages when draft ownership lapses mid-pagination', async () => {
    let active = true
    let pageCalls = 0
    const outcome = await prepareDraftDiff({
      bridge: {
        previewProjectChangeset: async () => ({ ok: true as const, data: previewReady }),
        getProjectDiffPage: async () => {
          pageCalls += 1
          active = false
          return {
            ok: true as const,
            data: { ...page, complete: false, nextCursor: 'cursor-page-2' },
          }
        },
        confirmProjectChangeset: async () => ({ ok: true as const, data: confirmationFixture() }),
        commitAgentDraft: async () => ({ ok: true as const, data: {} as never }),
      },
      plan: draftPlan('op-1'),
      projectId: diffProjectId,
      isCurrent: () => active,
    })
    expect(outcome.status).toBe('stale')
    expect(pageCalls).toBe(1)
  })
})

/* --------------------------------------------------------------------------
 * B07 / B09: the real host run state reaches the sidebar.
 * ----------------------------------------------------------------------- */

function agentState(overrides: Partial<AgentStateDTO> = {}): AgentStateDTO {
  return {
    operationId: 'op-1',
    exchangeId: 7,
    status: 'dispatching',
    context: {
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      scopeRef: 'scope1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: [],
      privacy: 'minimal',
      modelReady: true,
      capabilities: {
        mode: 'synthetic',
        connection: 'not-run',
        structuredOutput: 'passed',
        toolRoundTrip: 'passed',
      },
      configurations: [],
    },
    receipts: [],
    retainedQuestion: '合成问题',
    answerText: null,
    failureCode: null,
    ...overrides,
  }
}

describe('W3b B07/B09: the real host run state is mapped onto the sidebar', () => {
  it('never maps a run of another project', () => {
    expect(agentDtoToSidebarState(agentState(), 'p2')).toBeNull()
    expect(agentDtoToSidebarState(agentState({ context: null }), 'p1')).toBeNull()
  })

  it('maps a dispatching run to the waiting state and keeps the exchange identity', () => {
    const state = agentDtoToSidebarState(agentState(), 'p1')
    expect(state?.phase).toBe('awaiting-provider')
    expect(state?.exchanges).toBe(7)
    expect(state?.inputContext.projectId).toBe('p1')
    expect(state?.inputContext.selectedObjectIds).toEqual([])
    expect(state?.error).toBeNull()
  })

  it('maps a terminal failure to the real failure code', () => {
    const failed = agentDtoToSidebarState(
      agentState({ status: 'failed', failureCode: 'TIMED_OUT' }),
      'p1',
    )
    expect(failed?.phase).toBe('failed')
    expect(failed?.error).toBe('TIMED_OUT')
    const cancelled = agentDtoToSidebarState(
      agentState({ status: 'cancelled', failureCode: null }),
      'p1',
    )
    expect(cancelled?.phase).toBe('cancelled')
    expect(cancelled?.error).toBe('TOOL_FAILED')
  })

  it('maps an answered run to the real answer text', () => {
    const answered = agentDtoToSidebarState(
      agentState({ status: 'answered', answerText: '这是回答' }),
      'p1',
    )
    expect(answered?.phase).toBe('answered')
    expect(answered?.answer?.text).toBe('这是回答')
  })

  it('rejects a context of another project or module', () => {
    const other = agentState()
    expect(agentContextMatches(other.context, 'p1', 'ontology')).toBe(true)
    expect(agentContextMatches(other.context, 'p2', 'ontology')).toBe(false)
    expect(agentContextMatches(other.context, 'p1', 'query')).toBe(false)
    expect(agentContextMatches(null, 'p1', 'ontology')).toBe(false)
  })

  it('offers the real cancel control while the host is still waiting', () => {
    const state = agentDtoToSidebarState(agentState(), 'p1')
    const html = renderToStaticMarkup(
      createElement(AgentSidebar, {
        context,
        state,
        privacy: 'minimal',
        modelReady: true,
        localActions: ['hint'],
        onCancel: () => undefined,
      }),
    )
    expect(html).toContain('取消本地等待')
    expect(html).toContain('正在等待响应')
  })

  it('shows the terminal failure of a real run', () => {
    const state = agentDtoToSidebarState(
      agentState({ status: 'failed', failureCode: 'TIMED_OUT' }),
      'p1',
    )
    const html = renderToStaticMarkup(
      createElement(AgentSidebar, {
        context,
        state,
        privacy: 'minimal',
        modelReady: true,
        localActions: ['hint'],
      }),
    )
    expect(html).toContain('data-testid="agent-state-failure"')
    expect(html).toContain('等待超时')
  })

  it('shows the answer of a real run', () => {
    const state = agentDtoToSidebarState(
      agentState({ status: 'answered', answerText: '这是回答' }),
      'p1',
    )
    const html = renderToStaticMarkup(
      createElement(AgentSidebar, {
        context,
        state,
        privacy: 'minimal',
        modelReady: true,
        localActions: ['hint'],
      }),
    )
    expect(html).toContain('这是回答')
  })

  it('validates revision, snapshot and selected objects in agentContextMatches', () => {
    const base = agentState().context!
    expect(
      agentContextMatches(base, 'p1', 'ontology', {
        projectRevision: 3,
        inputSnapshotId: 's1',
        selectedObjectIds: [],
      }),
    ).toBe(true)
    expect(agentContextMatches(base, 'p1', 'ontology', { projectRevision: 4 })).toBe(false)
    expect(agentContextMatches(base, 'p1', 'ontology', { inputSnapshotId: 's2' })).toBe(false)
    expect(agentContextMatches(base, 'p1', 'ontology', { selectedObjectIds: ['urn:Pump'] })).toBe(
      false,
    )
  })

  it('refreshes the panel mode without switching modules and delivers delayed query drafts on terminal poll', async () => {
    vi.useFakeTimers()
    let currentMode: 'tutor' | 'project' = 'tutor'
    let pollPhase: 'dispatching' | 'answered' = 'dispatching'
    let contextCalls = 0
    const deliveredDrafts: unknown[] = []
    const validQueryJson = JSON.stringify({
      name: '列出设备',
      description: '终端轮询送达',
      sparql: 'SELECT * WHERE { ?s ?p ?o }',
      scope: 'asserted',
      capabilityQuestion: '有哪些设备？',
      source: 'model',
    })
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async () => {
          contextCalls += 1
          return {
            ok: true as const,
            data: {
              ...agentState().context!,
              mode: currentMode,
            },
          }
        },
        getAgentState: async () => ({
          ok: true as const,
          data:
            pollPhase === 'dispatching'
              ? agentState({
                  status: 'dispatching',
                  exchangeId: 7,
                  operationId: 'op-q1',
                  context: {
                    ...agentState().context!,
                    mode: currentMode,
                  },
                })
              : agentState({
                  status: 'answered',
                  exchangeId: 7,
                  operationId: 'op-q1',
                  context: {
                    ...agentState().context!,
                    mode: currentMode,
                  },
                  answerText: '已生成查询草稿',
                  receipts: [
                    {
                      callId: 'call-q1',
                      tool: 'query_draft',
                      purpose: 'suggest',
                      outcome: {
                        kind: 'draft',
                        draftType: 'query',
                        summary: '列出设备',
                        detail: validQueryJson,
                        projectId: 'p1',
                        baseRevision: 3,
                        inputSnapshotId: 's1',
                        requiresHumanDiffConfirmation: true,
                      },
                    },
                  ],
                }),
        }),
        dispatchAgentQuestion: async () => ({
          ok: true as const,
          data: { operationId: 'op-q1', exchangeId: 7 },
        }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: [],
      localActions: ['hint'],
      onQueryDraft: (draft: unknown) => deliveredDrafts.push(draft),
      onModeChange: async (next: 'tutor' | 'project') => {
        currentMode = next
      },
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(panel.text()).toContain('模式 tutor')
      expect(contextCalls).toBe(1)

      const sidebarNode = panel.nodes().find((node) => node.type === AgentSidebar)!
      await (sidebarNode.props.onModeChange as (m: 'tutor' | 'project') => Promise<void>)('project')
      panel.render()
      expect(panel.text()).toContain('模式 project')
      expect(contextCalls).toBeGreaterThanOrEqual(2)

      // Delayed query draft: dispatch finishes while host is still dispatching; poll advances to answered.
      await (sidebarNode.props.onSubmit as (q: string) => Promise<void>)('列出设备')
      expect(deliveredDrafts).toHaveLength(0)

      pollPhase = 'answered'
      await vi.advanceTimersByTimeAsync(160)
      panel.render()
      expect(deliveredDrafts).toHaveLength(1)
      expect(deliveredDrafts[0]).toMatchObject({ name: '列出设备', source: 'model' })
      expect(panel.text()).toContain('已收到上游查询草稿')

      // Reset to verifying that a mismatched baseRevision draft receipt is ignored.
      panel.setProps({ projectRevision: 4 })
      await vi.advanceTimersByTimeAsync(160)
      panel.render()
      expect(deliveredDrafts).toHaveLength(1)
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('drops late poll state, receipts and query drafts after switching selected objects in the same project (B07)', async () => {
    vi.useFakeTimers()
    let releasePumpPoll: ((reply: unknown) => void) | undefined
    let pumpPolls = 0
    let pumpPhase: 'dispatching' | 'answered' = 'dispatching'
    const deliveredDrafts: unknown[] = []
    const validQueryJson = JSON.stringify({
      name: '泵查询',
      description: '旧选区草稿',
      sparql: 'SELECT * WHERE { ?s ?p ?o }',
      scope: 'asserted',
      capabilityQuestion: '泵属性？',
      source: 'model',
    })
    const stateForSelection = (
      selected: string[],
      status: 'dispatching' | 'answered',
      answerText: string | null,
    ) => ({
      ...agentState({
        status,
        exchangeId: 11,
        operationId: 'op-pump',
        answerText,
        receipts:
          status === 'answered'
            ? [
                {
                  callId: 'call-pump',
                  tool: 'query_draft' as const,
                  purpose: 'suggest' as const,
                  outcome: {
                    kind: 'draft' as const,
                    draftType: 'query' as const,
                    summary: '泵查询',
                    detail: validQueryJson,
                    projectId: 'p1',
                    baseRevision: 3,
                    inputSnapshotId: 's1',
                    requiresHumanDiffConfirmation: true,
                  },
                },
              ]
            : [],
      }),
      context: {
        ...agentState().context!,
        selectedObjectIds: selected,
      },
    })
    let hostSelection = ['urn:Pump']
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async (args: { selectedObjectIds: string[] }) => ({
          ok: true as const,
          data: {
            ...agentState().context!,
            selectedObjectIds: [...args.selectedObjectIds],
          },
        }),
        getAgentState: async () => {
          if (hostSelection[0] === 'urn:Pump' && pumpPhase === 'answered') {
            pumpPolls += 1
            return new Promise((resolve) => {
              releasePumpPoll = resolve
            })
          }
          if (hostSelection[0] === 'urn:Pump') {
            return { ok: true as const, data: stateForSelection(['urn:Pump'], 'dispatching', null) }
          }
          return {
            ok: true as const,
            data: agentState({
              status: 'idle',
              exchangeId: null,
              operationId: null,
              context: null,
            }),
          }
        },
        dispatchAgentQuestion: async () => ({
          ok: true as const,
          data: { operationId: 'op-pump', exchangeId: 11 },
        }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: ['urn:Pump'],
      localActions: ['hint'],
      onQueryDraft: (draft: unknown) => deliveredDrafts.push(draft),
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const sidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      await (sidebar.props.onSubmit as (q: string) => Promise<void>)('查泵')

      // Hang the poll getAgentState for Pump before switching selection to Valve.
      pumpPhase = 'answered'
      await vi.advanceTimersByTimeAsync(160)
      expect(pumpPolls).toBe(1)
      expect(releasePumpPoll).toBeDefined()

      hostSelection = ['urn:Valve']
      panel.setProps({ selectedObjectIds: ['urn:Valve'] })
      await vi.advanceTimersByTimeAsync(0)
      panel.render()

      // Late Pump terminal state arrives after Valve refresh has become current.
      releasePumpPoll!({
        ok: true,
        data: stateForSelection(['urn:Pump'], 'answered', '旧选区回答'),
      })
      await Promise.resolve()
      await vi.advanceTimersByTimeAsync(200)
      panel.render()

      const valveSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      expect(valveSidebar.props.state).toBeNull()
      expect(valveSidebar.props.receipts).toEqual([])
      expect(panel.text()).not.toContain('旧选区回答')
      expect(deliveredDrafts).toHaveLength(0)
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('prevents a retired turn-1 draft plan callback from delivering after turn-2 is shown (B07)', async () => {
    vi.useFakeTimers()
    let releaseTurn1Plan: ((reply: unknown) => void) | undefined
    const deliveredPlans: AgentDraftPlanDTO[] = []
    const turn1OntologyDraft: AgentReceiptDTO = {
      callId: 'call-t1',
      tool: 'ontology_propose',
      purpose: 'suggest',
      outcome: {
        kind: 'draft',
        draftType: 'ontology',
        summary: '回合一方案',
        detail: '{"classIri":"urn:OldPump"}',
        projectId: 'p1',
        baseRevision: 3,
        inputSnapshotId: 's1',
        requiresHumanDiffConfirmation: true,
      },
    }
    let currentTurn: AgentStateDTO = agentState({
      status: 'answered',
      exchangeId: 1,
      operationId: 'op-1',
      answerText: '回合一回答',
      receipts: [turn1OntologyDraft],
    })
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async () => ({
          ok: true as const,
          data: agentState().context!,
        }),
        getAgentState: async () => ({
          ok: true as const,
          data: currentTurn,
        }),
        dispatchAgentQuestion: async () => {
          currentTurn = agentState({
            status: 'answered',
            exchangeId: 2,
            operationId: 'op-2',
            answerText: '回合二回答',
            receipts: [],
          })
          return { ok: true as const, data: { operationId: 'op-2', exchangeId: 2 } }
        },
        buildAgentDraftPlan: async () =>
          new Promise((resolve) => {
            releaseTurn1Plan = resolve
          }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: [],
      localActions: ['hint'],
      onDraftPlan: (plan: AgentDraftPlanDTO) => deliveredPlans.push(plan),
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const sidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      expect(sidebar.props.receipts).toHaveLength(1)

      // Start buildPlan for Turn 1 while buildAgentDraftPlan hangs.
      void (sidebar.props.onPreviewAgentDraft as (r: AgentReceiptDTO) => void)(turn1OntologyDraft)
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(true)
      expect(releaseTurn1Plan).toBeDefined()

      // Advance to Turn 2 in the exact same semantic context.
      await (sidebar.props.onSubmit as (q: string) => Promise<void>)('继续提问')
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(false)
      const turn2Sidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      expect(turn2Sidebar.props.state).toMatchObject({ exchanges: 2 })

      // Turn 1's plan resolves after Turn 2 is displayed and must be dropped.
      releaseTurn1Plan!({
        ok: true,
        data: {
          operationId: 'op-1',
          draftType: 'ontology',
          baseRevision: 3,
          inputSnapshotId: 's1',
          summary: '回合一方案',
          plan: { manual: [] },
        },
      })
      await Promise.resolve()
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(deliveredPlans).toHaveLength(0)
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('drops a late onModeChange refresh after switching modules so active module refresh stays valid (B09)', async () => {
    vi.useFakeTimers()
    let hostMode: 'tutor' | 'project' = 'tutor'
    let contextCalls = 0
    let releaseModeSwitch: (() => void) | undefined
    let releaseQueryContext: ((reply: unknown) => void) | undefined
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async (args: { module: 'ontology' | 'query' }) => {
          contextCalls += 1
          if (args.module === 'query') {
            return new Promise((resolve) => {
              releaseQueryContext = resolve
            })
          }
          return {
            ok: true as const,
            data: {
              ...agentState().context!,
              module: 'ontology' as const,
              mode: hostMode,
            },
          }
        },
        getAgentState: async () => ({
          ok: true as const,
          data: agentState({
            status: 'idle',
            exchangeId: null,
            operationId: null,
            context: null,
          }),
        }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: [],
      localActions: ['hint'],
      onModeChange: async (next: 'tutor' | 'project') => {
        await new Promise<void>((resolve) => {
          releaseModeSwitch = () => {
            hostMode = next
            resolve()
          }
        })
      },
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(contextCalls).toBe(1)
      expect(panel.text()).toContain('模块 ontology · 模式 tutor')

      const sidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      const pendingToggle = (
        sidebar.props.onModeChange as (m: 'tutor' | 'project') => Promise<void>
      )('project')
      expect(releaseModeSwitch).toBeDefined()

      // Switch to query module while ontology mode switch is still in flight.
      panel.setProps({ module: 'query' })
      await vi.advanceTimersByTimeAsync(0)
      expect(contextCalls).toBe(2)
      expect(releaseQueryContext).toBeDefined()

      // Resolve late mode switch from ontology; must not issue a 3rd context read or bump refreshSeq.
      releaseModeSwitch!()
      await pendingToggle
      expect(contextCalls).toBe(2)

      // Active query module context response must still be honored.
      releaseQueryContext!({
        ok: true,
        data: {
          ...agentState().context!,
          module: 'query',
          mode: hostMode,
        },
      })
      await Promise.resolve()
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(contextCalls).toBe(2)
      expect(panel.text()).toContain('模块 query · 模式 project')
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('retires fallback buildAgentDraftPlan query drafts across selection change and deduplicates repeated deliveries (B09)', async () => {
    vi.useFakeTimers()
    const deliveredDrafts: unknown[] = []
    let releaseFallbackPlan: ((reply: unknown) => void) | undefined
    const queryDraftFallbackReceipt = (opId: string): AgentReceiptDTO => ({
      callId: `call-${opId}`,
      tool: 'query_draft',
      purpose: 'suggest',
      outcome: {
        kind: 'draft',
        draftType: 'query',
        summary: '后备查询草稿',
        detail: 'non-json fallback detail',
        projectId: 'p1',
        baseRevision: 3,
        inputSnapshotId: 's1',
        requiresHumanDiffConfirmation: true,
      },
    })
    const validPlanReply = (opId: string) => ({
      ok: true as const,
      data: {
        operationId: opId,
        draftType: 'query' as const,
        baseRevision: 3,
        inputSnapshotId: 's1',
        summary: '后备查询草稿',
        plan: {
          definitions: [
            {
              layer: 'query' as const,
              id: 'q-fb',
              value: {
                text: 'SELECT * WHERE { ?s ?p ?o }',
                references: [],
                descriptor: {
                  name: '后备查询',
                  description: '',
                  scope: 'asserted' as const,
                  capabilityQuestion: '有哪些实例？',
                  source: 'model' as const,
                  version: 1,
                },
              },
            },
          ],
        },
      },
    })
    let hostSelection = ['urn:A']
    let activeOp = 'op-fb-1'
    let planCalls = 0
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async () => ({
          ok: true as const,
          data: {
            ...agentState().context!,
            selectedObjectIds: [...hostSelection],
          },
        }),
        getAgentState: async () => ({
          ok: true as const,
          data: agentState({
            status: 'answered',
            exchangeId: activeOp === 'op-fb-1' ? 21 : 22,
            operationId: activeOp,
            context: {
              ...agentState().context!,
              selectedObjectIds: [...hostSelection],
            },
            receipts: [queryDraftFallbackReceipt(activeOp)],
          }),
        }),
        buildAgentDraftPlan: async ({ operationId }: { operationId: string }) => {
          planCalls += 1
          if (operationId === 'op-fb-1') {
            return new Promise((resolve) => {
              releaseFallbackPlan = resolve
            })
          }
          return validPlanReply(operationId)
        },
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: ['urn:A'],
      localActions: ['hint'],
      onQueryDraft: (draft: unknown) => deliveredDrafts.push(draft),
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      expect(planCalls).toBe(1)
      expect(releaseFallbackPlan).toBeDefined()

      // Switch selection while op-fb-1 fallback buildAgentDraftPlan is still pending.
      hostSelection = ['urn:B']
      activeOp = 'op-fb-2'
      panel.setProps({ selectedObjectIds: ['urn:B'] })
      await vi.advanceTimersByTimeAsync(0)

      // Settling retired op-fb-1 must NOT deliver.
      releaseFallbackPlan!(validPlanReply('op-fb-1'))
      await Promise.resolve()
      await vi.advanceTimersByTimeAsync(0)

      // Active op-fb-2 delivers strictly once even if refresh runs again.
      expect(deliveredDrafts).toHaveLength(1)
      expect(deliveredDrafts[0]).toMatchObject({ name: '后备查询', source: 'model' })
      panel.setProps({ modelSyncVersion: 1 })
      await vi.advanceTimersByTimeAsync(0)
      expect(deliveredDrafts).toHaveLength(1)
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('resumes polling and delivers terminal state and query draft after A -> B -> A while dispatching (B09)', async () => {
    vi.useFakeTimers()
    let pumpPhase: 'dispatching' | 'answered' = 'dispatching'
    const deliveredDrafts: unknown[] = []
    const validQueryJson = JSON.stringify({
      name: '泵终态查询',
      description: '重返后恢复轮询',
      sparql: 'SELECT * WHERE { ?s ?p ?o }',
      scope: 'asserted',
      capabilityQuestion: '泵运行参数？',
      source: 'model',
    })
    const stateForPump = (phase: 'dispatching' | 'answered') => ({
      ...agentState({
        status: phase,
        exchangeId: 31,
        operationId: 'op-revisit',
        answerText: phase === 'answered' ? '泵分析完成' : null,
        receipts:
          phase === 'answered'
            ? [
                {
                  callId: 'call-revisit',
                  tool: 'query_draft' as const,
                  purpose: 'suggest' as const,
                  outcome: {
                    kind: 'draft' as const,
                    draftType: 'query' as const,
                    summary: '泵终态查询',
                    detail: validQueryJson,
                    projectId: 'p1',
                    baseRevision: 3,
                    inputSnapshotId: 's1',
                    requiresHumanDiffConfirmation: true,
                  },
                },
              ]
            : [],
      }),
      context: {
        ...agentState().context!,
        selectedObjectIds: ['urn:Pump'],
      },
    })
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async (args: { selectedObjectIds: string[] }) => ({
          ok: true as const,
          data: {
            ...agentState().context!,
            selectedObjectIds: [...args.selectedObjectIds],
          },
        }),
        getAgentState: async () => ({
          ok: true as const,
          data: stateForPump(pumpPhase),
        }),
        dispatchAgentQuestion: async () => ({
          ok: true as const,
          data: { operationId: 'op-revisit', exchangeId: 31 },
        }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: ['urn:Pump'],
      localActions: ['hint'],
      onQueryDraft: (draft: unknown) => deliveredDrafts.push(draft),
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const pumpSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      await (pumpSidebar.props.onSubmit as (q: string) => Promise<void>)('查泵参数')
      panel.render()
      expect(panel.nodes().find((node) => node.type === AgentSidebar)!.props.state).toMatchObject({
        phase: 'awaiting-provider',
      })

      // Switch A -> B: Valve does not show Pump's dispatching state or receipts.
      panel.setProps({ selectedObjectIds: ['urn:Valve'] })
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const valveSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      expect(valveSidebar.props.state).toBeNull()
      expect(valveSidebar.props.receipts).toBeUndefined()

      // Switch B -> A while host is STILL dispatching: Panel resumes polling cleanly.
      panel.setProps({ selectedObjectIds: ['urn:Pump'] })
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(panel.nodes().find((node) => node.type === AgentSidebar)!.props.state).toMatchObject({
        phase: 'awaiting-provider',
      })

      // Host finishes while back on A; next poll tick delivers terminal answer and query draft.
      pumpPhase = 'answered'
      await vi.advanceTimersByTimeAsync(160)
      panel.render()
      const resumedSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      expect(resumedSidebar.props.state).toMatchObject({
        phase: 'answered',
        answer: { text: '泵分析完成' },
      })
      expect(deliveredDrafts).toHaveLength(1)
      expect(deliveredDrafts[0]).toMatchObject({ name: '泵终态查询', source: 'model' })
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('never resurrects retired dispatch or buildPlan data-busy after A -> B -> A (W3B-R2D-N01)', async () => {
    vi.useFakeTimers()
    let releaseDispatch: ((reply: unknown) => void) | undefined
    let releasePlan: ((reply: unknown) => void) | undefined
    const pumpDraftReceipt: AgentReceiptDTO = {
      callId: 'call-busy-pump',
      tool: 'ontology_propose',
      purpose: 'suggest',
      outcome: {
        kind: 'draft',
        draftType: 'ontology',
        summary: '泵草稿',
        detail: '{"classIri":"urn:Pump"}',
        projectId: 'p1',
        baseRevision: 3,
        inputSnapshotId: 's1',
        requiresHumanDiffConfirmation: true,
      },
    }
    let hostSelection = ['urn:Pump']
    let pumpHasAnswer = false
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async (args: { selectedObjectIds: string[] }) => ({
          ok: true as const,
          data: {
            ...agentState().context!,
            selectedObjectIds: [...args.selectedObjectIds],
          },
        }),
        getAgentState: async () => ({
          ok: true as const,
          data:
            hostSelection[0] === 'urn:Pump' && pumpHasAnswer
              ? {
                  ...agentState({
                    status: 'answered',
                    exchangeId: 41,
                    operationId: 'op-busy',
                    answerText: '泵结果',
                    receipts: [pumpDraftReceipt],
                  }),
                  context: { ...agentState().context!, selectedObjectIds: ['urn:Pump'] },
                }
              : agentState({
                  status: 'idle',
                  exchangeId: null,
                  operationId: null,
                  context: null,
                }),
        }),
        dispatchAgentQuestion: async () =>
          new Promise((resolve) => {
            releaseDispatch = resolve
          }),
        buildAgentDraftPlan: async () =>
          new Promise((resolve) => {
            releasePlan = resolve
          }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: ['urn:Pump'],
      localActions: ['hint'],
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const pumpSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!

      // 1) Retired dispatch: leave A -> settle on B -> revisit A => busy stays false.
      const pendingDispatch = (pumpSidebar.props.onSubmit as (q: string) => Promise<void>)(
        '等待派发',
      )
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(true)

      hostSelection = ['urn:Valve']
      panel.setProps({ selectedObjectIds: ['urn:Valve'] })
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(false)

      // Even returning to A while the retired dispatch is still in flight must NOT resurrect data-busy.
      hostSelection = ['urn:Pump']
      panel.setProps({ selectedObjectIds: ['urn:Pump'] })
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(false)

      releaseDispatch!({ ok: true, data: { operationId: 'op-busy', exchangeId: 41 } })
      await pendingDispatch
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(false)

      // 2) Retired buildPlan: start buildPlan on A -> leave to B -> return to A while pending => busy stays false.
      pumpHasAnswer = true
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const pumpAnsweredSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      void (pumpAnsweredSidebar.props.onPreviewAgentDraft as (r: AgentReceiptDTO) => void)(
        pumpDraftReceipt,
      )
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(true)

      hostSelection = ['urn:Valve']
      panel.setProps({ selectedObjectIds: ['urn:Valve'] })
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(false)

      hostSelection = ['urn:Pump']
      panel.setProps({ selectedObjectIds: ['urn:Pump'] })
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(panel.find('agent-panel')?.props['data-busy']).toBe(false)

      releasePlan!({
        ok: true,
        data: {
          operationId: 'op-busy',
          draftType: 'ontology',
          baseRevision: 3,
          inputSnapshotId: 's1',
          summary: '泵草稿',
          plan: { manual: [] },
        },
      })
      await Promise.resolve()
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('delivers fallback buildAgentDraftPlan query draft across overlapping refresh without duplicate IPC (W3B-R2D-N02)', async () => {
    vi.useFakeTimers()
    const deliveredDrafts: unknown[] = []
    let releaseFallbackPlan: ((reply: unknown) => void) | undefined
    let planCalls = 0
    const fallbackReceipt: AgentReceiptDTO = {
      callId: 'call-overlap',
      tool: 'query_draft',
      purpose: 'suggest',
      outcome: {
        kind: 'draft',
        draftType: 'query',
        summary: '重叠刷新草稿',
        detail: 'non-json fallback detail',
        projectId: 'p1',
        baseRevision: 3,
        inputSnapshotId: 's1',
        requiresHumanDiffConfirmation: true,
      },
    }
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async () => ({
          ok: true as const,
          data: agentState().context!,
        }),
        getAgentState: async () => ({
          ok: true as const,
          data: agentState({
            status: 'answered',
            exchangeId: 51,
            operationId: 'op-overlap',
            receipts: [fallbackReceipt],
          }),
        }),
        buildAgentDraftPlan: async () => {
          planCalls += 1
          return new Promise((resolve) => {
            releaseFallbackPlan = resolve
          })
        },
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: [],
      localActions: ['hint'],
      onQueryDraft: (draft: unknown) => deliveredDrafts.push(draft),
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      expect(planCalls).toBe(1)
      expect(releaseFallbackPlan).toBeDefined()

      // Overlapping refresh while buildAgentDraftPlan is still pending must share the in-flight promise.
      panel.setProps({ modelSyncVersion: 1 })
      await vi.advanceTimersByTimeAsync(0)
      expect(planCalls).toBe(1)

      releaseFallbackPlan!({
        ok: true,
        data: {
          operationId: 'op-overlap',
          draftType: 'query',
          baseRevision: 3,
          inputSnapshotId: 's1',
          summary: '重叠刷新草稿',
          plan: {
            definitions: [
              {
                layer: 'query',
                id: 'q-overlap',
                value: {
                  text: 'SELECT * WHERE { ?s ?p ?o }',
                  references: [],
                  descriptor: {
                    name: '重叠草稿查询',
                    description: '',
                    scope: 'asserted',
                    capabilityQuestion: '有哪些实例？',
                    source: 'model',
                    version: 1,
                  },
                },
              },
            ],
          },
        },
      })
      await Promise.resolve()
      await vi.advanceTimersByTimeAsync(0)
      expect(deliveredDrafts).toHaveLength(1)
      expect(deliveredDrafts[0]).toMatchObject({ name: '重叠草稿查询', source: 'model' })
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })

  it('isolates superseded poll instances across same-view refresh and A -> B -> A revisit (B09)', async () => {
    vi.useFakeTimers()
    let pumpPhase: 'dispatching' | 'answered' = 'dispatching'
    let hangFirstTick = false
    let releaseFirstTick: ((reply: unknown) => void) | undefined
    const deliveredDrafts: unknown[] = []
    const validQueryJson = JSON.stringify({
      name: '竞争终态查询',
      description: '竞争后应送达',
      sparql: 'SELECT * WHERE { ?s ?p ?o }',
      scope: 'asserted',
      capabilityQuestion: '状态是否闭合？',
      source: 'model',
    })
    const stateForPump = (phase: 'dispatching' | 'answered') => ({
      ...agentState({
        status: phase,
        exchangeId: 61,
        operationId: 'op-poll-race',
        answerText: phase === 'answered' ? '竞争后终态成功' : null,
        receipts:
          phase === 'answered'
            ? [
                {
                  callId: 'call-race',
                  tool: 'query_draft' as const,
                  purpose: 'suggest' as const,
                  outcome: {
                    kind: 'draft' as const,
                    draftType: 'query' as const,
                    summary: '竞争终态查询',
                    detail: validQueryJson,
                    projectId: 'p1',
                    baseRevision: 3,
                    inputSnapshotId: 's1',
                    requiresHumanDiffConfirmation: true,
                  },
                },
              ]
            : [],
      }),
      context: {
        ...agentState().context!,
        selectedObjectIds: ['urn:Pump'],
      },
    })
    vi.stubGlobal('window', {
      ontolearn: {
        getAgentContext: async (args: { selectedObjectIds: string[] }) => ({
          ok: true as const,
          data: {
            ...agentState().context!,
            selectedObjectIds: [...args.selectedObjectIds],
          },
        }),
        getAgentState: async () => {
          if (hangFirstTick) {
            hangFirstTick = false
            return new Promise((resolve) => {
              releaseFirstTick = resolve
            })
          }
          return {
            ok: true as const,
            data: stateForPump(pumpPhase),
          }
        },
        dispatchAgentQuestion: async () => ({
          ok: true as const,
          data: { operationId: 'op-poll-race', exchangeId: 61 },
        }),
      },
    })
    const panel = agentPanelHarness({
      projectId: 'p1',
      projectRevision: 3,
      inputSnapshotId: 's1',
      module: 'ontology',
      mode: 'tutor',
      selectedObjectIds: ['urn:Pump'],
      localActions: ['hint'],
      onQueryDraft: (draft: unknown) => deliveredDrafts.push(draft),
    })
    try {
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      const pumpSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      await (pumpSidebar.props.onSubmit as (q: string) => Promise<void>)('竞争测例')
      panel.render()
      expect(panel.nodes().find((node) => node.type === AgentSidebar)!.props.state).toMatchObject({
        phase: 'awaiting-provider',
      })

      // At t=150ms, hang the first poll tick's in-flight getAgentState IPC.
      hangFirstTick = true
      await vi.advanceTimersByTimeAsync(150)
      expect(releaseFirstTick).toBeDefined()

      // At t=160ms, trigger same-view refresh (modelSyncVersion bump) starting poll instance #2.
      await vi.advanceTimersByTimeAsync(10)
      panel.setProps({ modelSyncVersion: 1 })
      await vi.advanceTimersByTimeAsync(0)

      // At t=170ms, settle the stale tick #1 IPC: it must exit without spawning an orphan timer.
      await vi.advanceTimersByTimeAsync(10)
      releaseFirstTick!({ ok: true, data: stateForPump('dispatching') })
      await Promise.resolve()

      // At t=190ms, switch A -> B -> A while dispatching.
      await vi.advanceTimersByTimeAsync(20)
      panel.setProps({ selectedObjectIds: ['urn:Valve'] })
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(panel.nodes().find((node) => node.type === AgentSidebar)!.props.state).toBeNull()

      panel.setProps({ selectedObjectIds: ['urn:Pump'] })
      await vi.advanceTimersByTimeAsync(0)
      panel.render()
      expect(panel.nodes().find((node) => node.type === AgentSidebar)!.props.state).toMatchObject({
        phase: 'awaiting-provider',
      })

      // Host flips to answered; advancing 600ms must finish polling cleanly, deliver answer + draft once, and leave 0 timers.
      pumpPhase = 'answered'
      await vi.advanceTimersByTimeAsync(600)
      panel.render()
      const finalSidebar = panel.nodes().find((node) => node.type === AgentSidebar)!
      expect(finalSidebar.props.state).toMatchObject({
        phase: 'answered',
        answer: { text: '竞争后终态成功' },
      })
      expect(deliveredDrafts).toHaveLength(1)
      expect(deliveredDrafts[0]).toMatchObject({ name: '竞争终态查询', source: 'model' })
      expect(vi.getTimerCount()).toBe(0)
    } finally {
      panel.unmount()
      vi.useRealTimers()
      vi.unstubAllGlobals()
    }
  })
})
