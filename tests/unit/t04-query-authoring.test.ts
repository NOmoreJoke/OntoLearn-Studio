import { describe, expect, it } from 'vitest'
import fixture from '../fixtures/query/authoring-case.json'
import boundaries from '../fixtures/query/draft-boundaries.json'
import {
  alarmTemplate,
  compileVisual,
  draftSchema,
  serializeTerm,
  savedQuerySchema,
  visualSchema,
} from '../../apps/desktop/src/renderer/src/query/draft'

describe('T04 offline query authoring', () => {
  const baseDraft = {
    name: 'q',
    description: '',
    sparql: 'SELECT ?item WHERE { ?item a <urn:Class> }',
    scope: 'asserted',
    capabilityQuestion: '',
    source: 'editor',
  }
  it.each(boundaries.cases)('uses the shared raw length policy: $label', (entry) => {
    const core = entry.unit.repeat(entry.count)
    const input = { ...baseDraft, [entry.field]: entry.prefix + core + entry.suffix }
    if (entry.valid) {
      const parsed = draftSchema.parse(input)
      expect(parsed[entry.field as 'name' | 'sparql']).toBe(core)
    } else expect(() => draftSchema.parse(input)).toThrow()
  })
  it.each(boundaries.trimEdgeCodePoints)('normalizes edge whitespace U+%s consistently', (cp) => {
    const edge = String.fromCodePoint(cp)
    for (const field of ['name', 'sparql'] as const) {
      expect(draftSchema.parse({ ...baseDraft, [field]: edge + 'q' + edge })[field]).toBe('q')
      expect(() => draftSchema.parse({ ...baseDraft, [field]: edge })).toThrow()
    }
  })
  it('continues rejecting lone surrogates in bounded draft text', () => {
    for (const field of ['name', 'sparql'])
      for (const value of ['\ud800', '\udfff'])
        expect(() => draftSchema.parse({ ...baseDraft, [field]: value })).toThrow()
  })
  it('builds the exact standards query with project supplied vocabulary', () => {
    const visual = alarmTemplate(fixture.vocabulary)
    expect(visual).toEqual(fixture.visual)
    expect(compileVisual(visual)).toBe(fixture.sparql)
  })
  it('escapes values and rejects code in IRI/variable positions', () => {
    expect(
      serializeTerm({
        kind: 'literal',
        value: '" . } SERVICE <https://invalid.example> { ?s ?p ?o } #',
        language: null,
        datatype: null,
      }),
    ).toBe('"\\" . } SERVICE <https://invalid.example> { ?s ?p ?o } #"')
    expect(
      serializeTerm({
        kind: 'literal',
        value: '泵站\n"\\\t\u0000\u007f',
        language: 'ZH-cn',
        datatype: null,
      }),
    ).toBe('"泵站\\n\\"\\\\\\t\\u0000\\u007F"@zh-cn')
    for (const iri of [
      'relative',
      'urn:x> . } #',
      'urn:a b',
      'urn:a\\u003E',
      'urn:a\u007f',
      'urn:\ud800',
    ]) {
      expect(() => serializeTerm({ kind: 'iri', value: iri })).toThrow()
    }
  })
  it('requires exact term shapes and bounded private editor state', () => {
    expect(() =>
      serializeTerm({ kind: 'literal', value: 'x', language: 'en', datatype: 'urn:type' }),
    ).toThrow()
    expect(() => visualSchema.parse({ ...fixture.visual, arbitraryCode: '?' })).toThrow()
    expect(() =>
      visualSchema.parse({ ...fixture.visual, fields: Array(17).fill(fixture.visual.fields[0]) }),
    ).toThrow()
    expect(() =>
      draftSchema.parse({
        name: 'q',
        description: '',
        sparql: 'ASK {}',
        scope: 'scenario',
        capabilityQuestion: '',
        source: 'editor',
      }),
    ).toThrow()
  })
  it('keeps optional returns independent from required filter triples', () => {
    expect(
      compileVisual({
        classIri: 'urn:Class',
        fields: [{ predicate: 'urn:label', label: '名称' }],
        conditions: [{ predicate: 'urn:missing', operator: 'not-exists' }],
      }),
    ).toBe(
      'SELECT DISTINCT ?item ?field0 WHERE {\n  ?item a <urn:Class> .\n  FILTER NOT EXISTS { ?item <urn:missing> ?condition0 . }\n  OPTIONAL { ?item <urn:label> ?field0 . }\n}\nORDER BY ?item ?field0',
    )
  })
  it('saves descriptive fields and model text only as untrusted draft', () => {
    const value = {
      name: '模型草稿',
      description: '未执行',
      sparql: 'untrusted model text',
      scope: 'asserted',
      capabilityQuestion: '问题',
      source: 'model',
    }
    expect(draftSchema.parse(value)).toEqual(value)
  })
  it('retains distinct saved definition identities even when names match', () => {
    const draft = {
      name: '同名查询',
      description: '',
      sparql: 'ASK {}',
      scope: 'asserted',
      capabilityQuestion: '问题',
      source: 'editor',
    }
    const first = savedQuerySchema.parse({ definitionId: 'Q-01', draft })
    const second = savedQuerySchema.parse({ definitionId: 'Q-02', draft })
    expect(first.definitionId).not.toBe(second.definitionId)
    expect(first.draft).toEqual(second.draft)
    expect(() => savedQuerySchema.parse({ definitionId: '../Q', draft })).toThrow()
    expect(() => savedQuerySchema.parse({ definitionId: 'Q-01', draft, extra: true })).toThrow()
  })
})
