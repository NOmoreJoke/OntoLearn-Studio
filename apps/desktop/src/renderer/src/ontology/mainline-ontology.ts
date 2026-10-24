/** Projection/intent mapping for API003. Authority stays in the actual project service.
 * Read payloads remain intact. Only public known edits are sent; T01 inherits opaque
 * material from the same base and checks final RDF/M/support before freezing the plan.
 */
import type { EditIntent } from './edit-intent'
import type { DomainRead, EditPlan, EntityMetadata, MetadataNamespace } from './mainline-api'
import type { LocalizedText, ObjectRow, OntologyView, RdfRow } from './view-model'

const RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
const RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
const OWL = 'http://www.w3.org/2002/07/owl#'
const controlled = new Set([
  RDF + 'type',
  ...['label', 'comment', 'subClassOf', 'domain', 'range'].map((key) => RDFS + key),
])
const key = (triple: RdfRow) => JSON.stringify([triple.subject, triple.predicate, triple.object])
type Value = NonNullable<EditPlan['definitions']>[number]['value']
type Home = { id: string; value: Value }
type Support = { triple: RdfRow; id: string; kind: 'definition' | 'fact' }

/** Same quote spelling as the installed RDFLib Literal._quote_encode, with no
 * text normalization. Cross-language tests check actual RDFLib, including multiline.
 */
export function literalN3(text: string, language: string): string {
  for (const character of text) {
    const code = character.codePointAt(0)!
    if (code >= 0xd800 && code <= 0xdfff) throw new Error('UNREPRESENTABLE_RDF_LITERAL')
  }
  let encoded = text.replaceAll('\\', '\\\\')
  if (text.includes('\n')) {
    encoded = encoded.replaceAll('"""', '\\"\\"\\"')
    if (encoded.endsWith('"') && encoded.at(-2) !== '\\') encoded = encoded.slice(0, -1) + '\\"'
    encoded = '"""' + encoded.replaceAll('\r', '\\r') + '"""'
  } else encoded = '"' + encoded.replaceAll('"', '\\"').replaceAll('\r', '\\r') + '"'
  return encoded + (language ? `@${language}` : '')
}
function literalPair(value: string): LocalizedText {
  const stringType = '^^<http://www.w3.org/2001/XMLSchema#string>'
  if (value.endsWith(stringType)) value = value.slice(0, -stringType.length)
  const match = /^(?:"""([\s\S]*)"""|"((?:[^"\\]|\\[\s\S])*)")(@([a-z]+(?:-[a-z0-9]+)*))?$/.exec(
    value,
  )
  if (!match) throw new Error('UNREPRESENTABLE_RDF_LITERAL')
  const body = match[1] ?? match[2]!
  const text = body.replace(
    /\\([\\"rn])/g,
    (_, escape: string) => ({ '\\': '\\', '"': '"', r: '\r', n: '\n' })[escape]!,
  )
  const pair: LocalizedText = [text, match[4] ?? '']
  if (literalN3(...pair) !== value) throw new Error('UNREPRESENTABLE_RDF_LITERAL')
  return pair
}
// Annotation comparison uses the displayed pair, while unchanged RDF keeps its
// original lexical spelling and xsd:string datatype in the submitted home.
function rdfIdentity(triple: RdfRow): string {
  return key(
    triple.predicate === RDFS + 'label' || triple.predicate === RDFS + 'comment'
      ? { ...triple, object: literalN3(...literalPair(triple.object)) }
      : triple,
  )
}
function displayableNamespace(value: unknown): value is MetadataNamespace {
  if (
    !value ||
    typeof value !== 'object' ||
    !('entityMetadataVersion' in value) ||
    value.entityMetadataVersion !== 1 ||
    !('entities' in value) ||
    !value.entities ||
    typeof value.entities !== 'object' ||
    Array.isArray(value.entities)
  )
    return false
  return Object.values(value.entities).every((item: unknown) => {
    if (
      !item ||
      typeof item !== 'object' ||
      !('identifier' in item) ||
      typeof item.identifier !== 'string'
    )
      return false
    return (
      ['labels', 'definitions'].every((field) => {
        const pairs = (item as Record<string, unknown>)[field]
        return (
          Array.isArray(pairs) &&
          pairs.every(
            (pair: unknown) =>
              Array.isArray(pair) &&
              pair.length === 2 &&
              pair.every((part: unknown) => typeof part === 'string'),
          )
        )
      }) &&
      ['synonyms', 'examples'].every((field) => {
        const entries = (item as Record<string, unknown>)[field]
        return (
          Array.isArray(entries) && entries.every((entry: unknown) => typeof entry === 'string')
        )
      })
    )
  })
}
export function entityRdf(row: ObjectRow): RdfRow[] {
  const triples: RdfRow[] = []
  const emit = (predicate: string, object: string) =>
    triples.push({ subject: row.iri, predicate, object })
  if (row.kind !== 'individual')
    emit(
      RDF + 'type',
      `<${
        row.kind === 'class'
          ? row.classType === 'owl'
            ? OWL + 'Class'
            : RDFS + 'Class'
          : OWL + (row.kind === 'objectProperty' ? 'ObjectProperty' : 'DatatypeProperty')
      }>`,
    )
  for (const [field, predicate] of [
    ['labels', 'label'],
    ['definitions', 'comment'],
  ] as const)
    for (const [text, language] of row[field]) emit(RDFS + predicate, literalN3(text, language))
  for (const [field, predicate] of [
    ['parents', RDFS + 'subClassOf'],
    ['domain', RDFS + 'domain'],
    ['range', RDFS + 'range'],
    ['types', RDF + 'type'],
  ] as const)
    for (const iri of row[field]) emit(predicate, `<${iri}>`)
  return [...new Map(triples.map((triple) => [key(triple), triple])).values()]
}
function metadata(row: ObjectRow): EntityMetadata {
  return {
    identifier: row.identifier,
    labels: row.labels.map(([text, lang]) => [text, lang]),
    definitions: row.definitions.map(([text, lang]) => [text, lang]),
    synonyms: [...row.synonyms],
    examples: [...row.examples],
  }
}
export type OntologyProjection = {
  view: OntologyView
  homes: Home[]
  supports: Support[]
  metadataHomes: Map<string, Home[]>
  raw: DomainRead
  readOnly: Map<string, string>
  readOnlyHomes: Set<string>
}

export function projectOntology(read: DomainRead): OntologyProjection {
  const homes: Home[] = []
  const readOnly = new Map<string, string>()
  const readOnlyHomes = new Set<string>()
  const supports: Support[] = []
  const metadataHomes = new Map<string, Home[]>()
  for (const definition of read.domain.state.definitions) {
    if (definition.layer !== 'ontology') continue
    const value: Value = JSON.parse(definition.payload)
    if (!value || !Array.isArray(value.triples)) continue // Opaque legacy material stays read-only.
    const home = { id: definition.id, value }
    homes.push(home)
    for (const triple of value.triples) supports.push({ triple, id: home.id, kind: 'definition' })
    if ('entityMetadata' in value) {
      if (!displayableNamespace(value.entityMetadata)) {
        readOnlyHomes.add(home.id)
        continue
      }
      for (const iri of Object.keys(value.entityMetadata.entities))
        metadataHomes.set(iri, [...(metadataHomes.get(iri) ?? []), home])
    }
  }
  for (const fact of read.domain.state.facts)
    if (fact.object !== null)
      supports.push({
        triple: { subject: fact.subject, predicate: fact.predicate, object: fact.object },
        id: fact.id,
        kind: 'fact',
      })
  const triples = [...new Map(supports.map(({ triple }) => [key(triple), triple])).values()]
  const subjects = new Set([
    ...metadataHomes.keys(),
    ...triples
      .filter((triple) => triple.predicate === RDF + 'type')
      .map((triple) => triple.subject),
  ])
  const objects: ObjectRow[] = []
  for (const iri of subjects) {
    try {
      const own = triples.filter((triple) => triple.subject === iri)
      const targets = (predicate: string) =>
        own
          .filter(
            (triple) =>
              triple.predicate === predicate &&
              triple.object.startsWith('<') &&
              triple.object.endsWith('>'),
          )
          .map((triple) => triple.object.slice(1, -1))
      const types = targets(RDF + 'type')
      const kind =
        types.includes(RDFS + 'Class') || types.includes(OWL + 'Class')
          ? 'class'
          : types.includes(OWL + 'ObjectProperty')
            ? 'objectProperty'
            : types.includes(OWL + 'DatatypeProperty')
              ? 'dataProperty'
              : 'individual'
      const saved = metadataHomes.get(iri)?.[0]?.value.entityMetadata?.entities[iri]
      const pairs = (predicate: string): LocalizedText[] =>
        own
          .filter((triple) => triple.predicate === predicate)
          .map((triple) => literalPair(triple.object))
      objects.push({
        iri,
        kind,
        identifier: saved?.identifier ?? '',
        labels: saved?.labels ?? pairs(RDFS + 'label'),
        definitions: saved?.definitions ?? pairs(RDFS + 'comment'),
        synonyms: saved?.synonyms ?? [],
        examples: saved?.examples ?? [],
        parents: targets(RDFS + 'subClassOf'),
        domain: targets(RDFS + 'domain'),
        range: targets(RDFS + 'range'),
        types: kind === 'individual' ? types : [],
        ...(kind === 'class'
          ? { classType: types.includes(OWL + 'Class') ? ('owl' as const) : ('rdfs' as const) }
          : {}),
      })
    } catch {
      readOnly.set(iri, '无法无损映射注释；原 RDF 保留，只读。')
    }
  }
  return {
    readOnly,
    readOnlyHomes,
    view: { project: read.projectId, revision: read.domain.projectRevision, objects, triples },
    homes,
    supports,
    metadataHomes,
    raw: read,
  }
}
function homeFor(projection: OntologyProjection, iri: string): Home {
  const explicit = projection.metadataHomes.get(iri)
  if (explicit && explicit.length !== 1) throw new Error('AMBIGUOUS_ENTITY_HOME')
  // Legacy candidate provenance comes from actual source records, never an IRI
  // suffix or guessed identifier. The actual service validates the final home.
  const candidates =
    explicit ??
    projection.homes.filter((home) =>
      home.value.triples.some(
        (triple) => triple.subject === iri && controlled.has(triple.predicate),
      ),
    )
  if (candidates.length !== 1) throw new Error('AMBIGUOUS_ENTITY_HOME')
  const home = candidates[0]!
  if (projection.readOnlyHomes.has(home.id)) throw new Error('METADATA_NAMESPACE_CONFLICT')
  return home
}
export function entityDeletionImpact(projection: OntologyProjection, iri: string): string[] {
  const home = homeFor(projection, iri)
  const impact = projection.supports
    .filter(
      ({ triple, id, kind }) =>
        (triple.subject === iri || triple.predicate === iri || triple.object === `<${iri}>`) &&
        !(
          kind === 'definition' &&
          id === home.id &&
          triple.subject === iri &&
          controlled.has(triple.predicate)
        ),
    )
    .map(
      ({ triple, id, kind }) =>
        `${kind}:${id} · <${triple.subject}> <${triple.predicate}> ${triple.object}`,
    )
  for (const record of projection.raw.domain.state.definitions) {
    const payload: unknown = JSON.parse(record.payload)
    if (
      !payload ||
      typeof payload !== 'object' ||
      !('references' in payload) ||
      !Array.isArray(payload.references)
    )
      continue
    for (const ref of payload.references as Array<{ layer: string; id: string }>)
      if (
        ref.layer === 'ontology' &&
        ref.id === home.id &&
        (record.layer !== 'ontology' || record.id !== home.id)
      )
        impact.push(`${record.layer}:${record.id} · references ontology:${home.id}`)
  }
  return impact
}
export function entityEditPlan(
  projection: OntologyProjection,
  intent: Extract<EditIntent, { action: 'create' | 'edit' | 'delete' }>,
): EditPlan {
  if (intent.action === 'create') {
    const row = intent.object
    if (
      projection.view.objects.some((item) => item.iri === row.iri) ||
      projection.supports.some(
        ({ triple }) => triple.subject === row.iri || triple.object === `<${row.iri}>`,
      )
    )
      throw new Error('ENTITY_ALREADY_EXISTS')
    return {
      definitions: [
        {
          layer: 'ontology',
          id: `t02-${crypto.randomUUID()}`,
          value: {
            triples: entityRdf(row),
            entityMetadata: { entityMetadataVersion: 1, entities: { [row.iri]: metadata(row) } },
          },
        },
      ],
    }
  }
  const iri = intent.action === 'delete' ? intent.iri : intent.object.iri
  const home = homeFor(projection, iri)
  const original = projection.view.objects.find((row) => row.iri === iri)
  if (!original) throw new Error('ENTITY_NOT_FOUND')
  if (
    projection.supports.some(
      ({ triple, id, kind }) =>
        triple.subject === iri &&
        controlled.has(triple.predicate) &&
        (kind !== 'definition' || id !== home.id),
    )
  )
    throw new Error('AMBIGUOUS_ENTITY_SUPPORT')
  const actual = new Set(
    home.value.triples
      .filter((triple) => triple.subject === iri && controlled.has(triple.predicate))
      .map(rdfIdentity),
  )
  const expected = new Set(entityRdf(original).map(rdfIdentity))
  if (actual.size !== expected.size || [...actual].some((value) => !expected.has(value)))
    throw new Error('UNREPRESENTABLE_ENTITY_RDF')
  if (intent.action === 'delete' && entityDeletionImpact(projection, iri).length)
    throw new Error('DELETION_REFERENCED')
  if (intent.action === 'edit' && intent.object.kind !== original.kind)
    throw new Error('ENTITY_KIND_CHANGE')
  const entities: MetadataNamespace['entities'] = structuredClone(
    home.value.entityMetadata?.entities ?? {},
  )
  if (intent.action === 'delete') delete entities[iri]
  else entities[iri] = metadata(intent.object)
  const replacement = intent.action === 'edit' ? entityRdf(intent.object) : []
  const wanted = new Set(replacement.map(rdfIdentity))
  const triples = home.value.triples.filter(
    (triple) =>
      !(triple.subject === iri && controlled.has(triple.predicate)) ||
      wanted.has(rdfIdentity(triple)),
  )
  const retained = new Set(triples.filter((triple) => triple.subject === iri).map(rdfIdentity))
  triples.push(...replacement.filter((triple) => !retained.has(rdfIdentity(triple))))
  return {
    definitions: [
      {
        layer: 'ontology',
        id: home.id,
        value: {
          triples,
          ...(home.value.references === undefined
            ? {}
            : { references: structuredClone(home.value.references) }),
          ...(home.value.singleValuedPredicates === undefined
            ? {}
            : { singleValuedPredicates: [...home.value.singleValuedPredicates] }),
          entityMetadata: { entityMetadataVersion: 1, entities },
        },
      },
    ],
  }
}
