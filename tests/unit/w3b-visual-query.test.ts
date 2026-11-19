/** W3b S2-4: the query workbench derives its templates from the really read ontology. */
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi } from 'vitest'
import {
  alarmTemplate,
  alarmVocabulary,
  compileVisual,
  draftSchema,
} from '../../apps/desktop/src/renderer/src/query/draft'
import { QueryWorkspacePage } from '../../apps/desktop/src/renderer/src/query/QueryWorkspacePage'
import type { QueryDraftDTO } from '../../apps/desktop/src/renderer/src/query/api002-source-types'

const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const fact = (subject: string, predicate: string, object: string) => ({
  id: `${subject}-${predicate}`,
  subject,
  predicate,
  object,
  owner: null,
  source_row: null,
  managed_value: null,
})

function stubController(facts: ReturnType<typeof fact>[]) {
  const state = {
    projectId: 'p1',
    draft: {
      name: '',
      description: '',
      sparql: '',
      scope: 'asserted',
      capabilityQuestion: '',
      source: 'editor',
    },
    definitionId: '',
    selection: { kind: 'current' },
    edit: 0,
    document: 1,
    dirty: false,
    busy: false,
    notice: '请读取当前项目。',
    resultView: 'current',
    read: {
      readVersion: 1,
      projectId: 'p1',
      inputSnapshotId: 's1',
      workspace: { draft: { editor: 'query', state: 'missing' } },
      domain: {
        projectRevision: 3,
        dependencyVector: {},
        state: { definitions: [], facts, mappingState: {} },
      },
    },
  }
  const controller = {
    projectId: 'p1',
    getSnapshot: () => state,
    subscribe: () => () => {},
    connect: vi.fn(),
    editDraft: vi.fn(),
    replaceDraft: vi.fn(),
    hasUnresolvedWrite: false,
  } as unknown as React.ComponentProps<typeof QueryWorkspacePage>['controller']
  return controller
}

const modelDraft: QueryDraftDTO = {
  name: '列出设备',
  description: '来自上游',
  sparql: 'SELECT * WHERE { ?s ?p ?o }',
  scope: 'asserted',
  capabilityQuestion: '',
  source: 'model',
}

describe('W3b S2-4: alarm template resolution', () => {
  it('resolves the alarm class, the severity and the status from the read ontology', () => {
    expect(alarmVocabulary(['urn:Alarm'], ['urn:severity', 'urn:status', rdfType])).toEqual({
      alarmClass: 'urn:Alarm',
      severity: 'urn:severity',
      status: 'urn:status',
    })
  })

  it('offers no template when the read ontology does not expose the vocabulary', () => {
    expect(alarmVocabulary(['urn:Pump'], ['urn:severity', 'urn:status'])).toBeUndefined()
    expect(alarmVocabulary(['urn:Alarm'], ['urn:status'])).toBeUndefined()
    expect(alarmVocabulary([], [])).toBeUndefined()
  })

  it('never mixes the severity and the status attribute', () => {
    expect(alarmVocabulary(['urn:Alarm'], ['urn:status'])).toBeUndefined()
  })

  it('compiles the resolved template into a valid visible SPARQL draft', () => {
    const vocabulary = alarmVocabulary(['urn:Alarm'], ['urn:severity', 'urn:status'])!
    const template = alarmTemplate(vocabulary)
    expect(template.classIri).toBe('urn:Alarm')
    const sparql = compileVisual(template)
    expect(sparql).toContain('<urn:Alarm>')
    expect(sparql).toContain('<urn:severity>')
    expect(sparql).toContain('<urn:status>')
    expect(sparql).toContain('"High"')
    expect(sparql).toContain('"Open"')
  })

  it('rejects a template whose vocabulary is not a real IRI', () => {
    expect(() =>
      alarmTemplate({ alarmClass: 'not an iri', severity: 'urn:severity', status: 'urn:status' }),
    ).toThrow()
  })
})

describe('W3b S2-4: query workspace template list and upstream draft', () => {
  it('renders the template list and enables the alarm template for a real vocabulary', () => {
    const controller = stubController([
      fact('urn:Pump', rdfType, '<urn:Alarm>'),
      fact('urn:Pump', 'urn:severity', '"High"'),
      fact('urn:Pump', 'urn:status', '"Open"'),
    ])
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
    expect(html).toContain('data-testid="query-template-list"')
    expect(html).toContain('urn:Alarm')
    expect(html).toContain('urn:severity')
    expect(html).toContain('urn:status')
    expect(html).toContain('载入只写入工作草稿，不会自动执行')
    expect(html).not.toMatch(/data-testid="query-template-alarm" disabled/)
  })

  it('keeps the template disabled and explains why when the vocabulary is missing', () => {
    const controller = stubController([fact('urn:Pump', rdfType, '<urn:Pump>')])
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
    expect(html).toContain('data-testid="query-template-list"')
    expect(html).toMatch(/data-testid="query-template-alarm" disabled/)
    expect(html).toContain('不会填入示例词表')
  })

  it('shows the upstream model draft with a stable id and never submits it', () => {
    const controller = stubController([])
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller, modelDraft }))
    expect(html).toContain('data-testid="query-model-draft"')
    expect(html).toContain('列出设备')
    expect(html).toContain('未自动提交')
    expect(html).toContain('当前页面不调用模型')
  })

  it('keeps the upstream draft button disabled when no upstream draft exists', () => {
    const controller = stubController([])
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
    expect(html).toContain('data-testid="query-model-draft"')
    expect(html).toMatch(/<button disabled="">将上游模型草稿放入编辑器（替换当前内容）<\/button>/)
  })

  it('accepts the upstream draft shape through the shared draft schema', () => {
    const parsed = draftSchema.safeParse({ ...modelDraft, source: 'model' })
    expect(parsed.success).toBe(true)
    expect(draftSchema.safeParse({ ...modelDraft, source: 'model', extra: 1 }).success).toBe(false)
  })
})
