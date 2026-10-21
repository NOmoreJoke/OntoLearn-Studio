import { describe, expect, it } from 'vitest'
import {
  classTree,
  isCurrentPreview,
  localGraph,
  type ObjectRow,
  type OntologyView,
} from '../../apps/desktop/src/renderer/src/ontology/view-model'

const row = (iri: string, parents: string[] = []): ObjectRow => ({
  iri,
  parents,
  kind: 'class',
  identifier: iri,
  labels: [[iri, 'zh']],
  definitions: [],
  synonyms: [],
  examples: [],
  domain: [],
  range: [],
  types: [],
})
describe('T02 view projection', () => {
  it('displays every class with explicit cycle and multiple-parent reference rows', () => {
    const rows = [
      row('urn:b', ['urn:a']),
      row('urn:a', ['urn:b']),
      row('urn:c', ['urn:a', 'urn:b']),
    ]
    expect(classTree(rows)).toEqual([
      { iri: 'urn:a', depth: 0, repeated: false },
      { iri: 'urn:b', depth: 1, repeated: false },
      { iri: 'urn:a', depth: 2, repeated: true },
      { iri: 'urn:c', depth: 2, repeated: false },
      { iri: 'urn:c', depth: 1, repeated: true },
    ])
    expect(classTree([...rows].reverse())).toEqual(classTree(rows))
  })
  it('focuses on one-hop incoming and outgoing edges and shows truncation', () => {
    const view: OntologyView = {
      project: 'a',
      revision: 7,
      objects: [],
      triples: [
        { subject: 'urn:b', predicate: 'urn:p', object: '<urn:a>' },
        { subject: 'urn:a', predicate: 'urn:p', object: '"name"' },
        { subject: 'urn:c', predicate: 'urn:p', object: '<urn:d>' },
      ],
    }
    expect(localGraph(view, 'urn:a')).toEqual({
      nodes: ['urn:a', 'urn:b'],
      edges: [
        { subject: 'urn:a', predicate: 'urn:p', object: '"name"' },
        { subject: 'urn:b', predicate: 'urn:p', object: '<urn:a>' },
      ],
      total: 2,
      truncated: false,
    })
    expect(localGraph(view, 'urn:a', 1)).toEqual({
      nodes: ['urn:a'],
      edges: [view.triples[1]],
      total: 2,
      truncated: true,
    })
    expect(() => localGraph(view, 'urn:a', 0)).toThrow('invalid_limit')
  })
  it('refuses current status for another project or old version', () => {
    expect(isCurrentPreview({ project: 'a', revision: 7 }, { project: 'a', revision: 7 })).toBe(
      true,
    )
    expect(isCurrentPreview({ project: 'a', revision: 8 }, { project: 'a', revision: 7 })).toBe(
      false,
    )
    expect(isCurrentPreview({ project: 'b', revision: 7 }, { project: 'a', revision: 7 })).toBe(
      false,
    )
  })
})
