/** W3b S2-4: the workspace Agent panel consumes the named bridge, never project data. */
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import type { AgentDraftPlanDTO, AgentReceiptDTO, DesktopBridge } from '@ontolearn/contracts'
import {
  AgentPanel,
  queryDraftFromDetail,
  queryDraftFromPlan,
} from '../../apps/desktop/src/renderer/src/agent/agent-panel'
import {
  AgentSidebar,
  agentDraftIsCurrent,
} from '../../apps/desktop/src/renderer/src/agent/AgentSidebar'
import { DraftDiffPreview } from '../../apps/desktop/src/renderer/src/ontology/draft-diff-preview'
import type { TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'

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
