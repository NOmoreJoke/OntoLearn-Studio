import { describe, expect, it } from 'vitest'
import type { DomainRead } from '../../apps/desktop/src/renderer/src/ontology/mainline-api'
import {
  entityDeletionImpact,
  entityEditPlan,
  entityRdf,
  literalN3,
  projectOntology,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-ontology'
import type { ObjectRow } from '../../apps/desktop/src/renderer/src/ontology/view-model'

const row = (iri = 'urn:Equipment'): ObjectRow => ({
  iri,
  kind: 'class',
  classType: 'rdfs',
  identifier: 'Equipment',
  labels: [
    ['设备', 'zh'],
    ['Equipment', 'en'],
  ],
  definitions: [['A maintained\nasset.', 'en']],
  synonyms: [' 资产 ', '多行\n同义词'],
  examples: ['泵站A'],
  parents: [],
  domain: [],
  range: [],
  types: [],
})
const source = (): DomainRead => {
  const entity = row()
  const other = row('urn:Other')
  return {
    readVersion: 1,
    projectId: 'project-a',
    inputSnapshotId: 'a'.repeat(64),
    workspace: { draft: { state: 'missing', editor: 'ontology-transaction' } },
    domain: {
      projectRevision: 8,
      dependencyVector: { 'ontology:home-a': 4 },
      state: {
        definitions: [
          {
            layer: 'ontology',
            id: 'home-a',
            payload: JSON.stringify({
              triples: [...entityRdf(entity), ...entityRdf(other)],
              references: [],
              singleValuedPredicates: [],
              entityMetadata: {
                entityMetadataVersion: 1,
                entities: Object.fromEntries(
                  [entity, other].map((item) => [
                    item.iri,
                    {
                      identifier: item.identifier,
                      labels: item.labels,
                      definitions: item.definitions,
                      synonyms: item.synonyms,
                      examples: item.examples,
                    },
                  ]),
                ),
              },
              legacyOpaque: { retainedBy: 'actual backend same-base inheritance' },
            }),
          },
        ],
        facts: [],
        mappingState: {},
      },
    },
  }
}

describe('T02 API003 M/RDF consumer mapping; no backend/Job evidence', () => {
  it('changes label/identifier/synonyms together, preserves all five fields and the other entity', () => {
    const read = source()
    const before = structuredClone(read)
    const projected = projectOntology(read)
    const original = projected.view.objects.find((item) => item.iri === 'urn:Equipment')!
    expect(original).toEqual(row())
    const changed = {
      ...original,
      identifier: 'MaintainableEquipment',
      labels: [
        ['运维设备', 'zh'],
        ['Equipment', 'en'],
      ] as const,
      synonyms: [...original.synonyms, '维护对象'],
    }
    const plan = entityEditPlan(projected, { action: 'edit', object: changed })
    expect(plan.definitions?.[0]?.id).toBe('home-a')
    const value = plan.definitions![0]!.value
    expect(value.entityMetadata?.entities['urn:Equipment']).toEqual({
      identifier: 'MaintainableEquipment',
      labels: changed.labels,
      definitions: original.definitions,
      synonyms: changed.synonyms,
      examples: original.examples,
    })
    expect(value.entityMetadata?.entities['urn:Other']).toEqual(
      JSON.parse(read.domain.state.definitions[0]!.payload).entityMetadata.entities['urn:Other'],
    )
    expect(new Set(value.triples.map((triple) => JSON.stringify(triple)))).toEqual(
      new Set(
        [...entityRdf(row('urn:Other')), ...entityRdf(changed)].map((triple) =>
          JSON.stringify(triple),
        ),
      ),
    )
    expect(value).not.toHaveProperty('legacyOpaque') // Backend inherits it; renderer must not inject opaque.
    expect(read).toEqual(before)
  })
  it('keeps M-only changes out of RDF, including whitespace and multiline metadata', () => {
    const projection = projectOntology(source())
    const original = projection.view.objects.find((item) => item.iri === 'urn:Equipment')!
    const changed = {
      ...original,
      identifier: '0_new',
      examples: [' 前后空格 ', '多行\n示例'],
      synonyms: ['\ufeff'],
    }
    const value = entityEditPlan(projection, { action: 'edit', object: changed }).definitions![0]!
      .value
    expect(value.triples).toEqual(projection.homes[0]!.value.triples)
    expect(value.entityMetadata?.entities[changed.iri]?.examples).toEqual(changed.examples)
    expect(value.entityMetadata?.entities[changed.iri]?.synonyms).toEqual(['\ufeff'])
  })
  it('creates a real independently named definition home, without deriving metadata identity from an IRI', () => {
    const projected = projectOntology(source())
    const changed = { ...row('urn:New'), identifier: 'Equipment' }
    const plan = entityEditPlan(projected, { action: 'create', object: changed })
    expect(plan.definitions?.[0]?.id).toMatch(/^t02-[a-f0-9-]{36}$/)
    expect(plan.definitions?.[0]?.value.entityMetadata?.entities[changed.iri]?.identifier).toBe(
      'Equipment',
    )
    expect(() => entityEditPlan(projected, { action: 'create', object: row() })).toThrow(
      'ENTITY_ALREADY_EXISTS',
    )
  })
  it('projects legacy RDF without inventing an English identifier, and can explicitly add M', () => {
    const read = source()
    const value = JSON.parse(read.domain.state.definitions[0]!.payload)
    delete value.entityMetadata
    read.domain.state.definitions[0]!.payload = JSON.stringify(value)
    const projection = projectOntology(read)
    const original = projection.view.objects.find((item) => item.iri === 'urn:Equipment')!
    expect(original.identifier).toBe('')
    expect(original.labels).toEqual(row().labels)
    const plan = entityEditPlan(projection, {
      action: 'edit',
      object: { ...original, identifier: 'Equipment' },
    })
    expect(plan.definitions![0]!.value.entityMetadata?.entities[original.iri]?.identifier).toBe(
      'Equipment',
    )
    expect(plan.definitions![0]!.value.triples).toEqual(value.triples)
  })
  it('keeps record-level data when deleting one unreferenced entity from a multi-entity home', () => {
    const projection = projectOntology(source())
    const plan = entityEditPlan(projection, { action: 'delete', iri: 'urn:Equipment' })
    expect(plan.remove_definitions).toBeUndefined()
    expect(plan.definitions![0]!.value.entityMetadata?.entities).toEqual({
      'urn:Other': JSON.parse(source().domain.state.definitions[0]!.payload).entityMetadata
        .entities['urn:Other'],
    })
    expect(plan.definitions![0]!.value.triples).toEqual(entityRdf(row('urn:Other')))
  })
  it('shows exact referencing facts and blocks deletion, preserving mapped provenance and tombstones', () => {
    const read = source()
    read.domain.state.facts = [
      {
        id: 'f'.repeat(64),
        subject: 'urn:001',
        predicate: 'urn:type',
        object: '<urn:Equipment>',
        owner: 'mapping-a',
        source_row: 'row-1',
        managed_value: '<urn:Equipment>',
      },
    ]
    const projection = projectOntology(read)
    expect(entityDeletionImpact(projection, 'urn:Equipment')).toEqual([
      `fact:${'f'.repeat(64)} · <urn:001> <urn:type> <urn:Equipment>`,
    ])
    expect(() => entityEditPlan(projection, { action: 'delete', iri: 'urn:Equipment' })).toThrow(
      'DELETION_REFERENCED',
    )
    expect(read.domain.state.facts[0]?.owner).toBe('mapping-a')
  })
  it('refuses ambiguous homes/supports and incompatible RDF rather than silently choosing or merging', () => {
    const read = source()
    read.domain.state.definitions.push({ ...read.domain.state.definitions[0]!, id: 'home-b' })
    expect(() => entityEditPlan(projectOntology(read), { action: 'edit', object: row() })).toThrow(
      'AMBIGUOUS_ENTITY_HOME',
    )
    const single = source()
    const value = JSON.parse(single.domain.state.definitions[0]!.payload)
    value.entityMetadata.entities['urn:Equipment'].labels = [['漂移', 'zh']]
    single.domain.state.definitions[0]!.payload = JSON.stringify(value)
    expect(() =>
      entityEditPlan(projectOntology(single), { action: 'edit', object: row() }),
    ).toThrow('UNREPRESENTABLE_ENTITY_RDF')
  })
  it('preserves unchanged typed string annotations, for legacy and recognized M homes', () => {
    for (const withMetadata of [true, false]) {
      const read = source()
      const value = JSON.parse(read.domain.state.definitions[0]!.payload)
      if (!withMetadata) delete value.entityMetadata
      value.triples = value.triples.map((triple: { predicate: string; object: string }) =>
        triple.predicate.endsWith('#label') && !triple.object.includes('@')
          ? { ...triple, object: triple.object + '^^<http://www.w3.org/2001/XMLSchema#string>' }
          : triple,
      )
      // Use an untagged label; typed strings have no language.
      const label = value.triples.find(
        (triple: { subject: string; predicate: string }) =>
          triple.subject === 'urn:Equipment' && triple.predicate.endsWith('#label'),
      )
      label.object = '"设备"^^<http://www.w3.org/2001/XMLSchema#string>'
      if (withMetadata) value.entityMetadata.entities['urn:Equipment'].labels[0] = ['设备', '']
      read.domain.state.definitions[0]!.payload = JSON.stringify(value)
      const projection = projectOntology(read)
      const original = projection.view.objects.find((item) => item.iri === 'urn:Equipment')!
      expect(original.labels[0]).toEqual(['设备', ''])
      const plan = entityEditPlan(projection, {
        action: 'edit',
        object: { ...original, identifier: 'New' },
      })
      expect(plan.definitions![0]!.value.triples).toEqual(value.triples)
    }
  })
  it('isolates opaque namespace collisions from unrelated editable homes', () => {
    const read = source()
    const opaque = JSON.parse(read.domain.state.definitions[0]!.payload)
    opaque.entityMetadata = 'legacy-note'
    read.domain.state.definitions.push({
      layer: 'ontology',
      id: 'opaque-home',
      payload: JSON.stringify(opaque),
    })
    // Collision home has a different entity and no support overlap.
    read.domain.state.definitions[1]!.payload = JSON.stringify({
      ...opaque,
      triples: entityRdf(row('urn:Legacy')),
    })
    const projection = projectOntology(read)
    expect(projection.readOnlyHomes.has('opaque-home')).toBe(true)
    expect(() => entityEditPlan(projection, { action: 'edit', object: row('urn:Legacy') })).toThrow(
      'METADATA_NAMESPACE_CONFLICT',
    )
    expect(
      entityEditPlan(projection, { action: 'edit', object: { ...row(), identifier: 'New' } })
        .definitions![0]!.id,
    ).toBe('home-a')
    expect(read.domain.state.definitions[1]!.payload).toContain('legacy-note')
  })
  it('reports cross-layer references even when the source and home IDs match', () => {
    const read = source()
    read.domain.state.definitions.push({
      layer: 'query',
      id: 'home-a',
      payload: JSON.stringify({ references: [{ layer: 'ontology', id: 'home-a' }] }),
    })
    const projection = projectOntology(read)
    expect(entityDeletionImpact(projection, 'urn:Equipment')).toEqual([
      'query:home-a · references ontology:home-a',
    ])
    expect(() => entityEditPlan(projection, { action: 'delete', iri: 'urn:Equipment' })).toThrow(
      'DELETION_REFERENCED',
    )
  })
  const RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
  const RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
  const OWL = 'http://www.w3.org/2002/07/owl#'
  const XSD = 'http://www.w3.org/2001/XMLSchema#'
  const variants = [
    { kind: 'class', classType: 'rdfs', declaration: RDFS + 'Class' },
    { kind: 'class', classType: 'owl', declaration: OWL + 'Class' },
    { kind: 'objectProperty', declaration: OWL + 'ObjectProperty' },
    { kind: 'dataProperty', declaration: OWL + 'DatatypeProperty' },
    { kind: 'individual', declaration: '' },
  ] as const
  function matrixRow(variant: (typeof variants)[number], iri: string): ObjectRow {
    const fields = row(iri)
    return {
      iri,
      kind: variant.kind,
      identifier: 'Matrix',
      labels: fields.labels,
      definitions: fields.definitions,
      synonyms: fields.synonyms,
      examples: fields.examples,
      parents: variant.kind === 'class' ? ['urn:Other'] : [],
      domain:
        variant.kind === 'objectProperty' || variant.kind === 'dataProperty'
          ? ['urn:Equipment']
          : [],
      range:
        variant.kind === 'objectProperty'
          ? ['urn:Other']
          : variant.kind === 'dataProperty'
            ? [XSD + 'string']
            : [],
      types: variant.kind === 'individual' ? ['urn:Equipment'] : [],
      ...(variant.kind === 'class' ? { classType: variant.classType } : {}),
    }
  }
  function independentlyExpected(variant: (typeof variants)[number], iri: string, edited = false) {
    const triples: { subject: string; predicate: string; object: string }[] = []
    if (variant.kind !== 'individual')
      triples.push({ subject: iri, predicate: RDF + 'type', object: `<${variant.declaration}>` })
    triples.push(
      { subject: iri, predicate: RDFS + 'label', object: edited ? '"更名"@zh' : '"设备"@zh' },
      { subject: iri, predicate: RDFS + 'label', object: '"Equipment"@en' },
      { subject: iri, predicate: RDFS + 'comment', object: '"""A maintained\nasset."""@en' },
    )
    if (variant.kind === 'class')
      triples.push({
        subject: iri,
        predicate: RDFS + 'subClassOf',
        object: edited ? '<urn:Equipment>' : '<urn:Other>',
      })
    if (variant.kind === 'objectProperty' || variant.kind === 'dataProperty') {
      triples.push({
        subject: iri,
        predicate: RDFS + 'domain',
        object: edited ? '<urn:Other>' : '<urn:Equipment>',
      })
      triples.push({
        subject: iri,
        predicate: RDFS + 'range',
        object:
          variant.kind === 'objectProperty'
            ? '<urn:Other>'
            : `<${XSD + (edited ? 'integer' : 'string')}>`,
      })
    }
    if (variant.kind === 'individual')
      triples.push({
        subject: iri,
        predicate: RDF + 'type',
        object: edited ? '<urn:Other>' : '<urn:Equipment>',
      })
    return triples
  }
  it.each(variants)(
    'covers C-subset $kind $declaration create/edit/copy/delete RDF with exact five-field M',
    (variant) => {
      const read = source()
      const originalRead = structuredClone(read)
      const iri = `urn:matrix:${variant.kind}:${variant.declaration.endsWith('owl#Class') ? 'owl' : 'base'}`
      const entity = matrixRow(variant, iri)
      const create = entityEditPlan(projectOntology(read), { action: 'create', object: entity })
      const definition = create.definitions![0]!
      expect(definition.value.triples).toEqual(independentlyExpected(variant, iri))
      expect(definition.value.entityMetadata?.entities[iri]).toEqual({
        identifier: 'Matrix',
        labels: entity.labels,
        definitions: entity.definitions,
        synonyms: [' 资产 ', '多行\n同义词'],
        examples: ['泵站A'],
      })
      expect(create.manual).toBeUndefined()
      expect(read).toEqual(originalRead)
      const created = structuredClone(read)
      created.domain.state.definitions.push({
        layer: 'ontology',
        id: definition.id,
        payload: JSON.stringify(definition.value),
      })
      const projection = projectOntology(created)
      expect(projection.view.objects.find((item) => item.iri === iri)).toEqual(entity)
      const changed: ObjectRow = {
        ...entity,
        identifier: 'MatrixEdited',
        labels: [
          ['更名', 'zh'],
          ['Equipment', 'en'],
        ],
        parents: variant.kind === 'class' ? ['urn:Equipment'] : [],
        domain:
          variant.kind === 'objectProperty' || variant.kind === 'dataProperty' ? ['urn:Other'] : [],
        range: variant.kind === 'dataProperty' ? [XSD + 'integer'] : entity.range,
        types: variant.kind === 'individual' ? ['urn:Other'] : [],
      }
      const edit = entityEditPlan(projection, { action: 'edit', object: changed })
      expect(edit.definitions![0]!.id).toBe(definition.id)
      expect(
        new Set(edit.definitions![0]!.value.triples.map((triple) => JSON.stringify(triple))),
      ).toEqual(
        new Set(independentlyExpected(variant, iri, true).map((triple) => JSON.stringify(triple))),
      )
      expect(edit.definitions![0]!.value.entityMetadata?.entities[iri]).toEqual({
        identifier: 'MatrixEdited',
        labels: changed.labels,
        definitions: changed.definitions,
        synonyms: changed.synonyms,
        examples: changed.examples,
      })
      expect(created.domain.state.facts).toEqual(read.domain.state.facts)
      const copyIri = iri + ':copy'
      const copy = entityEditPlan(projection, {
        action: 'create',
        object: { ...entity, iri: copyIri },
      })
      expect(copy.definitions![0]!.id).not.toBe(definition.id)
      expect(copy.definitions![0]!.value.triples).toEqual(independentlyExpected(variant, copyIri))
      expect(copy.definitions![0]!.value.entityMetadata?.entities[copyIri]).toEqual(
        definition.value.entityMetadata?.entities[iri],
      )
      expect(copy.manual).toBeUndefined()
      expect(entityDeletionImpact(projection, iri)).toEqual([])
      const removed = entityEditPlan(projection, { action: 'delete', iri })
      expect(removed).toEqual({
        definitions: [
          {
            layer: 'ontology',
            id: definition.id,
            value: { triples: [], entityMetadata: { entityMetadataVersion: 1, entities: {} } },
          },
        ],
      })
      expect(created.domain.state.definitions.slice(0, -1)).toEqual(read.domain.state.definitions)
      expect(created.domain.state.facts).toEqual(read.domain.state.facts)
    },
  )
  it.each(variants)(
    'reports exact external references before deleting $kind $declaration',
    (variant) => {
      const read = source()
      const iri = `urn:referenced:${variant.kind}`
      const created = entityEditPlan(projectOntology(read), {
        action: 'create',
        object: matrixRow(variant, iri),
      }).definitions![0]!
      read.domain.state.definitions.push({
        layer: 'ontology',
        id: created.id,
        payload: JSON.stringify(created.value),
      })
      const usesPredicate = variant.kind === 'objectProperty' || variant.kind === 'dataProperty'
      read.domain.state.facts.push({
        id: 'e'.repeat(64),
        subject: 'urn:external',
        predicate: usesPredicate ? iri : RDF + 'type',
        object: usesPredicate ? '"kept"' : `<${iri}>`,
        owner: null,
        source_row: null,
        managed_value: null,
      })
      const before = structuredClone(read)
      const projection = projectOntology(read)
      expect(entityDeletionImpact(projection, iri)).toEqual([
        `fact:${'e'.repeat(64)} · <urn:external> <${usesPredicate ? iri : RDF + 'type'}> ${usesPredicate ? '"kept"' : `<${iri}>`}`,
      ])
      expect(() => entityEditPlan(projection, { action: 'delete', iri })).toThrow(
        'DELETION_REFERENCED',
      )
      expect(read).toEqual(before)
    },
  )
  it('rejects isolated surrogate RDF text instead of replacing it', () => {
    expect(() => literalN3('\ud800', 'zh')).toThrow('UNREPRESENTABLE_RDF_LITERAL')
  })
})
