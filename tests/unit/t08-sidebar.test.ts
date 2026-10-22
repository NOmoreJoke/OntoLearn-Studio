import { readFileSync } from 'node:fs'
import { createElement, type ComponentType } from 'react'
import * as React from 'react'
import * as jsxRuntime from 'react/jsx-runtime'
import { renderToStaticMarkup } from 'react-dom/server'
import { transpileModule, ModuleKind, JsxEmit } from 'typescript'
import { describe, expect, it } from 'vitest'
import * as actions from '../../apps/desktop/src/renderer/src/agent/context-actions'
import * as presentation from '../../apps/desktop/src/renderer/src/agent/sidebar-presentation'
import type { SidebarState } from '../../apps/desktop/src/renderer/src/agent/sidebar-presentation'
import type { ToolReceipt, TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'

// Compile the actual TSX in memory: no tsconfig/lock edits, DOM stub, window, or Electron.
const source = readFileSync(
  new URL('../../apps/desktop/src/renderer/src/agent/AgentSidebar.tsx', import.meta.url),
  'utf8',
)
const compiled = transpileModule(source, {
  compilerOptions: { module: ModuleKind.CommonJS, jsx: JsxEmit.ReactJSX },
}).outputText
const modules: Record<string, unknown> = {
  react: React,
  'react/jsx-runtime': jsxRuntime,
  './context-actions': actions,
  './sidebar-presentation': presentation,
  './agent-sidebar.css': {},
}
const exported: Record<string, unknown> = {}
new Function('require', 'exports', compiled)((name: string) => {
  if (!(name in modules)) throw Error(`Unexpected renderer dependency ${name}`)
  return modules[name]
}, exported)
const Sidebar = exported.AgentSidebar as ComponentType<Record<string, unknown>>
const context: TrustedContext = {
  projectId: 'p1',
  projectRevision: 1,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: ['001'],
}
const evidence: ToolReceipt = {
  callId: 'call1',
  tool: 'query_execute',
  outcome: {
    kind: 'evidence',
    projectId: 'p1',
    inputSnapshotId: 's1',
    scopeRef: 'scope1',
    resultId: 'result1',
    status: 'current',
    traceRefs: ['trace1'],
    fields: [
      { fieldId: 'id', value: '001' },
      { fieldId: 'zero', value: 0 },
      { fieldId: 'flag', value: false },
      { fieldId: 'missing', value: null },
    ],
  },
}
const draft: ToolReceipt = {
  callId: 'call2',
  tool: 'ontology_propose',
  outcome: {
    kind: 'draft',
    draftType: 'ontology',
    summary: '建立设备类',
    detail: '新增urn:Equipment',
    projectId: 'p1',
    baseRevision: 1,
    inputSnapshotId: 's1',
    requiresHumanDiffConfirmation: true,
  },
}
const state: SidebarState = {
  phase: 'answered',
  exchanges: 2,
  requestedTokenCeiling: 2048,
  error: null,
  inputContext: context,
  localReceipts: [evidence, draft],
  answer: { kind: 'evidence', receipts: [evidence, draft] },
}
function render(overrides: Record<string, unknown> = {}) {
  return renderToStaticMarkup(
    createElement(Sidebar, {
      context,
      state,
      privacy: 'local',
      modelReady: false,
      localActions: ['hint'],
      ...overrides,
    }),
  )
}
describe('T08 sidebar: actual React server markup, not mounted UI integration', () => {
  it('renders complete supplied evidence, zero/false/null, context and draft base without fabricating checks', () => {
    const html = render()
    for (const text of [
      '001',
      '>0<',
      '>false<',
      '空值（null）',
      '输入 s1',
      '结果 result1',
      'trace1',
      '建议草稿',
      '尚未正式写入',
      '生成基准 V1',
    ])
      expect(html).toContain(text)
    expect(html).not.toContain('检查通过')
    expect(html).toContain('完全本地')
  })
  it('escapes imported/model strings as text instead of HTML, scripts, or external resources', () => {
    const evil = '<script>alert(1)</script><img src="https://evil.example/x" onerror="x">'
    const malicious = {
      ...state,
      localReceipts: [{ ...draft, outcome: { ...draft.outcome, summary: evil, detail: evil } }],
    }
    const html = render({ state: malicious, context: { ...context, selectedObjectIds: [evil] } })
    expect(html).toContain('&lt;script&gt;')
    expect(html).not.toContain('<script>')
    expect(html).not.toContain('<img')
    expect(html).not.toMatch(/<[a-z][^>]*\sonerror=/i)
  })
  it('disables every absent handler and model action in local mode; no auto send or confirm control', () => {
    const html = render()
    const buttons = html.match(/<button[^>]*>/g) ?? []
    expect(buttons.length).toBeGreaterThan(0)
    expect(buttons.every((button) => button.includes('disabled'))).toBe(true)
    expect(html).not.toContain('确认提交')
    expect(html).not.toContain('API Key')
    expect(html).toContain('<label')
    expect(html).toContain('<textarea')
  })
  it('keeps a supplied local hint available while model actions stay disabled in local mode', () => {
    const html = render({ onAction: () => undefined, onSubmit: () => undefined })
    expect(html).toMatch(/<button type="button"><strong>给我一点提示<\/strong>/)
    expect(html).toContain('离线本地功能')
    expect(html).toMatch(/<button type="submit" disabled="">发送问题<\/button>/)
    // Markup availability is distinct from a mounted click or a real T09 lesson handler.
  })
  it('marks prior context explicitly and disables its preview even if a callback exists', () => {
    const html = render({
      context: { ...context, projectRevision: 2 },
      onPreviewDraft: () => undefined,
    })
    expect(html).toContain('先前项目或输入版本')
    expect(html).toMatch(/<button[^>]*disabled[^>]*>查看真实 Diff<\/button>/)
  })
  it.each(['stale', 'historical', 'failed', 'cancelled'] as const)(
    'renders %s exactly and does not relabel as success',
    (status) => {
      const record = { ...evidence, outcome: { ...evidence.outcome, status } }
      const html = render({ state: { ...state, localReceipts: [record] } })
      expect(html).toContain(presentation.resultLabels[status])
      expect(html).not.toContain('class="t08-record-state">当前结果<')
    },
  )
  it('retains local draft/evidence alongside a final model error and shows a safe recovery explanation', () => {
    const html = render({ state: { ...state, phase: 'failed', error: 'TIMED_OUT', answer: null } })
    expect(html).toContain('等待超时')
    expect(html).toContain('建立设备类')
    expect(html).toContain('已完成记录仍保留')
    expect(html).not.toContain('secret')
  })
})
it('T08 draft preview checks the actual project/base/snapshot and requires stamped host drafts', () => {
  expect(presentation.canPreviewDraft(draft, context)).toBe(true)
  expect(presentation.canPreviewDraft(draft, { ...context, projectRevision: 2 })).toBe(false)
  expect(presentation.canPreviewDraft(draft, { ...context, projectId: 'p2' })).toBe(false)
  expect(presentation.canPreviewDraft(draft, { ...context, inputSnapshotId: 's2' })).toBe(false)
  expect(
    presentation.canPreviewDraft(
      { ...draft, outcome: { kind: 'draft', draftType: 'ontology', summary: 'x', detail: 'y' } },
      context,
    ),
  ).toBe(false)
})

it('T08 local mode disables model retry even when the host supplies its handler', () => {
  const html = render({
    state: { ...state, phase: 'failed', error: 'TIMED_OUT', answer: null },
    onRetry: () => undefined,
  })
  expect(html).toMatch(/<button[^>]*disabled[^>]*>重试本次操作<\/button>/)
})
it.each([{ selectedObjectIds: ['002'] }, { module: 'mapping' }, { mode: 'project' }])(
  'T08 treats changed selections/module/mode as prior context %j',
  (change) => {
    const html = render({
      context: { ...context, ...change },
      onAction: () => undefined,
      onPreviewDraft: () => undefined,
      privacy: 'minimum',
      modelReady: true,
    })
    expect(html).toContain('先前项目或输入版本')
    expect(html).toMatch(/<button[^>]*disabled[^>]*>查看真实 Diff<\/button>/)
  },
)
