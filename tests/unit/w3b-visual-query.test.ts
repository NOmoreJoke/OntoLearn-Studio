/** W3b S2-4: the query workbench derives its templates from the really read ontology. */
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi } from 'vitest'
import {
  alarmTemplate,
  alarmVocabulary,
  compileVisual,
  draftSchema,
  resolveAlarmVocabulary,
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

/* --------------------------------------------------------------------------
 * B10: the alarm template only binds attributes that really belong to the
 * alarm class of the project that was really read.
 * ----------------------------------------------------------------------- */

const learning = 'urn:ontolearn:learning:'
const owlClass = '<http://www.w3.org/2002/07/owl#Class>'
const rdfsDomain = 'http://www.w3.org/2000/01/rdf-schema#domain'

describe('W3b B10: the alarm vocabulary is resolved from the really read ontology', () => {
  it('resolves the G-base instance vocabulary', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [
        { subject: `${learning}alarm/A01`, predicate: rdfType, object: `<${learning}Alarm>` },
        { subject: `${learning}alarm/A01`, predicate: `${learning}level`, object: '"High"' },
        { subject: `${learning}alarm/A01`, predicate: `${learning}status`, object: '"Open"' },
        {
          subject: `${learning}equipment/001`,
          predicate: rdfType,
          object: `<${learning}Equipment>`,
        },
        {
          subject: `${learning}equipment/001`,
          predicate: `${learning}name`,
          object: '"泵站A"',
        },
      ],
      ontologyTriples: [
        { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
        { subject: `${learning}Equipment`, predicate: rdfType, object: owlClass },
      ],
    })
    expect(resolution.status).toBe('resolved')
    expect(resolution.status === 'resolved' && resolution.vocabulary).toEqual({
      alarmClass: `${learning}Alarm`,
      severity: `${learning}level`,
      status: `${learning}status`,
    })
  })

  it('never counts a tombstoned fact as a class or an attribute', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [
        { subject: `${learning}alarm/A01`, predicate: rdfType, object: `<${learning}Alarm>` },
        // A deleted alarm level: the tombstone must not define the vocabulary.
        { subject: `${learning}alarm/A01`, predicate: `${learning}level`, object: null },
        { subject: `${learning}alarm/A01`, predicate: `${learning}status`, object: '"Open"' },
      ],
      ontologyTriples: [],
    })
    expect(resolution.status).toBe('missing')
    expect(resolution.status === 'missing' && resolution.reason).toContain('等级属性')
  })

  it('never binds an attribute of an unrelated entity', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [
        { subject: `${learning}alarm/A01`, predicate: rdfType, object: `<${learning}Alarm>` },
        { subject: `${learning}alarm/A01`, predicate: `${learning}level`, object: '"High"' },
        { subject: `${learning}alarm/A01`, predicate: `${learning}status`, object: '"Open"' },
        // A work order carries its own status attribute; it is not the alarm one.
        { subject: `${learning}order/1`, predicate: rdfType, object: `<${learning}WorkOrder>` },
        {
          subject: `${learning}order/1`,
          predicate: `${learning}workOrderStatus`,
          object: '"Open"',
        },
      ],
      ontologyTriples: [],
    })
    expect(resolution.status).toBe('resolved')
    expect(resolution.status === 'resolved' && resolution.vocabulary.status).toBe(
      `${learning}status`,
    )
  })

  it('resolves a definition-only ontology through rdfs:domain', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [],
      ontologyTriples: [
        { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
        { subject: `${learning}level`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
        { subject: `${learning}status`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
      ],
    })
    expect(resolution.status).toBe('resolved')
    expect(resolution.status === 'resolved' && resolution.vocabulary).toEqual({
      alarmClass: `${learning}Alarm`,
      severity: `${learning}level`,
      status: `${learning}status`,
    })
  })

  it('refuses an ambiguous alarm class', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [],
      ontologyTriples: [
        { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
        { subject: `${learning}Alert`, predicate: rdfType, object: owlClass },
        { subject: `${learning}level`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
        { subject: `${learning}status`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
      ],
    })
    expect(resolution.status).toBe('ambiguous')
    expect(resolution.status === 'ambiguous' && resolution.candidates).toHaveLength(2)
    expect(resolution.status === 'ambiguous' && resolution.reason).toContain('告警类')
  })

  it('refuses an ambiguous attribute instead of taking the first hit', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [],
      ontologyTriples: [
        { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
        { subject: `${learning}level`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
        { subject: `${learning}alarmLevel`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
        { subject: `${learning}status`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
      ],
    })
    expect(resolution.status).toBe('ambiguous')
    expect(resolution.status === 'ambiguous' && resolution.candidates).toHaveLength(2)
  })

  it('never mixes the severity and the status attribute', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [],
      ontologyTriples: [
        { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
        { subject: `${learning}alarmLevel`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
      ],
    })
    expect(resolution.status).toBe('missing')
  })

  it('offers no template at all when the alarm class is unknown', () => {
    const resolution = resolveAlarmVocabulary({
      liveFacts: [
        { subject: `${learning}pump/1`, predicate: rdfType, object: `<${learning}Pump>` },
        { subject: `${learning}pump/1`, predicate: `${learning}severity`, object: '"High"' },
        { subject: `${learning}pump/1`, predicate: `${learning}status`, object: '"Open"' },
      ],
      ontologyTriples: [],
    })
    expect(resolution.status).toBe('missing')
  })
})

describe('W3b B10: the query workbench never offers an unbound template', () => {
  const definition = (
    id: string,
    triples: Array<{ subject: string; predicate: string; object: string }>,
  ) => ({
    layer: 'ontology',
    id,
    payload: JSON.stringify({ triples }),
  })

  function stubControllerWith(
    facts: ReturnType<typeof fact>[],
    definitions: Array<{ layer: string; id: string; payload: string }> = [],
  ) {
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
          state: { definitions, facts, mappingState: {} },
        },
      },
    }
    return {
      projectId: 'p1',
      getSnapshot: () => state,
      subscribe: () => () => {},
      connect: vi.fn(),
      editDraft: vi.fn(),
      replaceDraft: vi.fn(),
      hasUnresolvedWrite: false,
    } as unknown as React.ComponentProps<typeof QueryWorkspacePage>['controller']
  }

  it('keeps the template disabled and explains the ambiguity', () => {
    const controller = stubControllerWith(
      [],
      [
        definition('alarm', [
          { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
          { subject: `${learning}Alert`, predicate: rdfType, object: owlClass },
          { subject: `${learning}level`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
          { subject: `${learning}status`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
        ]),
      ],
    )
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
    expect(html).toMatch(/data-testid="query-template-alarm" disabled/)
    expect(html).toContain('data-testid="query-template-alarm-reason"')
    expect(html).toContain('多个告警类候选')
    expect(html).not.toContain(`${learning}Alarm</code>，等级属性`)
  })

  it('offers the template for a definition-only ontology', () => {
    const controller = stubControllerWith(
      [],
      [
        definition('alarm', [
          { subject: `${learning}Alarm`, predicate: rdfType, object: owlClass },
          { subject: `${learning}level`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
          { subject: `${learning}status`, predicate: rdfsDomain, object: `<${learning}Alarm>` },
        ]),
      ],
    )
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
    expect(html).toContain('模板依据当前已读取的本体推导')
    expect(html).toContain(`${learning}Alarm`)
    expect(html).not.toMatch(/data-testid="query-template-alarm" disabled/)
  })

  it('never offers a template that is bound to an unrelated entity', () => {
    const controller = stubControllerWith([
      fact(`${learning}order/1`, rdfType, `<${learning}WorkOrder>`),
      fact(`${learning}order/1`, `${learning}workOrderStatus`, '"Open"'),
      fact(`${learning}pump/1`, rdfType, `<${learning}Pump>`),
      fact(`${learning}pump/1`, `${learning}severity`, '"High"'),
      fact(`${learning}pump/1`, `${learning}status`, '"Open"'),
    ])
    const html = renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
    expect(html).toMatch(/data-testid="query-template-alarm" disabled/)
    // The template list itself never names the unrelated attribute.
    const list = html.slice(html.indexOf('data-testid="query-template-list"'))
    const section = list.slice(0, list.indexOf('</section>'))
    expect(section).not.toContain(`${learning}workOrderStatus`)
    expect(section).not.toContain(`${learning}severity`)
  })
})
