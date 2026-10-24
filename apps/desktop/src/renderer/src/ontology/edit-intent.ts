import type { ObjectRow, RdfRow } from './view-model'

/** Local form intent, not a public wire DTO. Copying creates a complete edited
 * definition in a new form; it does not persist copy lineage or instance facts.
 */
export type EditIntent =
  | { action: 'create' | 'edit'; object: ObjectRow }
  | { action: 'delete'; iri: string }
  | { action: 'assert' | 'retract'; fact: RdfRow }
