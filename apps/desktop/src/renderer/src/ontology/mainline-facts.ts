import type { DomainRead, EditPlan } from './mainline-api'
import type { RdfRow } from './view-model'

const sameTriple = (a: RdfRow, b: RdfRow) =>
  a.subject === b.subject && a.predicate === b.predicate && a.object === b.object

/** Preserve the original fact identity and every opaque definition payload.
 * Mapped/overlapping supports require their owning service's conflict workflow.
 */
export function manualFactPlan(
  source: DomainRead,
  action: 'edit' | 'remove',
  recordId: string,
  object: string,
): EditPlan {
  const fact = source.domain.state.facts.find((row) => row.id === recordId)
  if (!fact || fact.object === null) throw new Error('FACT_NOT_FOUND')
  if (fact.owner !== null || fact.source_row !== null || fact.managed_value !== null)
    throw new Error('MANAGED_FACT_REQUIRES_OWNER')
  const live = source.domain.state.facts.filter(
    (row) =>
      row.object !== null && row.subject === fact.subject && row.predicate === fact.predicate,
  )
  if (live.length !== 1) throw new Error('AMBIGUOUS_FACT_SUPPORT')
  const original = { subject: fact.subject, predicate: fact.predicate, object: fact.object }
  const replacement = { ...original, object }
  for (const definition of source.domain.state.definitions) {
    if (definition.layer !== 'ontology') continue
    const value = JSON.parse(definition.payload) as { triples?: RdfRow[] }
    if (
      value.triples?.some(
        (triple) =>
          sameTriple(triple, original) || (action === 'edit' && sameTriple(triple, replacement)),
      )
    )
      throw new Error('AMBIGUOUS_FACT_SUPPORT')
  }
  if (action === 'remove') return { remove: [fact.id] }
  if (!object || object === fact.object) throw new Error('NO_FACT_CHANGE')
  return { edits: { [fact.id]: object } }
}

export function newManualFactPlan(source: DomainRead, fact: RdfRow): EditPlan {
  if (!fact.subject || !fact.predicate || !fact.object) throw new Error('INVALID_FACT')
  if (
    source.domain.state.facts.some(
      (row) => row.object !== null && sameTriple({ ...row, object: row.object }, fact),
    )
  )
    throw new Error('FACT_ALREADY_EXISTS')
  for (const definition of source.domain.state.definitions) {
    if (definition.layer !== 'ontology') continue
    const value = JSON.parse(definition.payload) as { triples?: RdfRow[] }
    if (value.triples?.some((row) => sameTriple(row, fact))) throw new Error('FACT_ALREADY_EXISTS')
  }
  // New manual records get a fresh stable identity, retained by the prepared plan.
  // Editing an existing record never enters this path or changes its record ID.
  const id = Array.from(crypto.getRandomValues(new Uint8Array(32)), (byte) =>
    byte.toString(16).padStart(2, '0'),
  ).join('')
  return { manual: [{ id, ...fact }] }
}
