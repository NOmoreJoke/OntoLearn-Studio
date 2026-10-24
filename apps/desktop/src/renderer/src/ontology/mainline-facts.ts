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
  const original = { subject: fact.subject, predicate: fact.predicate, object: fact.object }
  const replacement = { ...original, object }
  if (
    source.domain.state.facts.some(
      (row) =>
        row.id !== fact.id &&
        row.object !== null &&
        row.subject === fact.subject &&
        row.predicate === fact.predicate &&
        (row.owner !== null ||
          row.source_row !== null ||
          row.managed_value !== null ||
          row.object === original.object ||
          (action === 'edit' && row.object === replacement.object)),
    )
  )
    throw new Error('AMBIGUOUS_FACT_SUPPORT')
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

export async function newManualFactPlan(source: DomainRead, fact: RdfRow): Promise<EditPlan> {
  const triple = { subject: fact.subject, predicate: fact.predicate, object: fact.object }
  if (!triple.subject || !triple.predicate || !triple.object) throw new Error('INVALID_FACT')
  // Store canonical JSON encodes Unicode scalars as UTF-8. Reject lone surrogates
  // rather than hash JSON.stringify's surrogate escape as a different statement.
  for (const value of Object.values(triple))
    for (const character of value) {
      const code = character.codePointAt(0)!
      if (code >= 0xd800 && code <= 0xdfff) throw new Error('INVALID_FACT')
    }
  if (
    source.domain.state.facts.some(
      (row) => row.object !== null && sameTriple({ ...row, object: row.object }, triple),
    )
  )
    throw new Error('FACT_ALREADY_EXISTS')
  for (const definition of source.domain.state.definitions) {
    if (definition.layer !== 'ontology') continue
    const value = JSON.parse(definition.payload) as { triples?: RdfRow[] }
    if (value.triples?.some((row) => sameTriple(row, triple)))
      throw new Error('FACT_ALREADY_EXISTS')
  }
  // Match Store.digest([S,P,O]) for creation only. Edits/removals keep the old ID.
  const bytes = new TextEncoder().encode(
    JSON.stringify([triple.subject, triple.predicate, triple.object]),
  )
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))
  const id = Array.from(digest, (byte) => byte.toString(16).padStart(2, '0')).join('')
  return { manual: [{ id, ...triple }] }
}
