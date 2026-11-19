/** Private presentation state only. T00 owns all wire schemas and bridge methods. */
export type ValueKind = 'string' | 'integer' | 'decimal' | 'boolean' | 'date' | 'datetime'
export type FieldDraft = {
  column: string
  predicate: string
  kind: ValueKind
  trim: boolean
  empty: 'omit' | 'error' | 'literal'
  referenceNamespace: string
  referenceColumns: string[]
}
export type MappingDraft = {
  identity: string
  version: number
  namespace: string
  classIri: string
  keys: string[]
  fields: FieldDraft[]
}
export type SourceView = {
  selectionId: string // trusted opaque selection, never a renderer-selected file path
  fingerprint: string
  sheet: string
  encoding: string | null
  fields: { name: string; observedTypes: string[]; samples: string[] }[]
  totalRows: number
}
export type PreviewView = {
  resultId: string
  projectId: string
  revision: number
  sourceFingerprint: string
  selectionId: string
  sheet: string
  encoding: string | null
  generation: number
  offset?: number
  totalRows?: number
  draftKey: string
  rows: { sourceRow: string; input: string[]; rdf: string[] }[]
  added: string[]
  removed: string[]
  modified: { subject: string; predicate: string; before: string[]; after: string[] }[]
  identitiesAdded: string[]
  identitiesRemoved: string[]
  issues: { code: string; sheet: string; row: number; column: number; field: string }[]
  conflicts: {
    code: string
    current: string | null
    source: string | null
    managed: string | null
    owner: string | null
    sourceRow: string | null
    subject: string
    predicate: string
  }[]
}
export type Wizard = {
  projectId: string
  revision: number
  generation: number // local request lifecycle, never a persisted authority
  source: SourceView | null
  draft: MappingDraft
  preview: PreviewView | null
  confirmed: boolean
}
export function draftKey(draft: MappingDraft): string {
  // Local draft equality only; never an authorization token or engine hash.
  return JSON.stringify([
    draft.identity,
    draft.version,
    draft.namespace,
    draft.classIri,
    draft.keys,
    draft.fields.map((field) => [
      field.column,
      field.predicate,
      field.kind,
      field.trim,
      field.empty,
      field.referenceNamespace,
      field.referenceColumns,
    ]),
  ])
}
export function currentPreview(state: Wizard): boolean {
  const p = state.preview
  return Boolean(
    p &&
    state.source &&
    p.projectId === state.projectId &&
    p.revision === state.revision &&
    p.sourceFingerprint === state.source.fingerprint &&
    p.selectionId === state.source.selectionId &&
    p.sheet === state.source.sheet &&
    p.encoding === state.source.encoding &&
    p.generation === state.generation &&
    p.draftKey === draftKey(state.draft),
  )
}
export function canConfirm(state: Wizard): boolean {
  return Boolean(
    state.confirmed &&
    currentPreview(state) &&
    state.preview?.issues.length === 0 &&
    state.preview.conflicts.length === 0,
  )
}
export function updateDraft(state: Wizard, draft: MappingDraft): Wizard {
  return { ...state, draft, generation: state.generation + 1, preview: null, confirmed: false }
}
export function selectSource(state: Wizard, source: SourceView): Wizard {
  const names = new Set(source.fields.map((field) => field.name))
  return {
    ...state,
    source,
    generation: state.generation + 1,
    draft: {
      ...state.draft,
      keys: state.draft.keys.filter((key) => names.has(key)),
      fields: state.draft.fields.filter(
        (field) => names.has(field.column) && field.referenceColumns.every((key) => names.has(key)),
      ),
    },
    preview: null,
    confirmed: false,
  }
}
export function cancelPreview(state: Wizard): Wizard {
  return { ...state, generation: state.generation + 1, preview: null, confirmed: false }
}
export function acceptPreview(state: Wizard, preview: PreviewView): Wizard {
  const next = { ...state, preview, confirmed: false }
  return currentPreview(next) ? next : state
}
export function mappingDraftValid(state: Wizard): boolean {
  if (!state.source) return false
  const names = new Set(state.source.fields.map((field) => field.name))
  const d = state.draft
  return Boolean(
    d.identity.trim() &&
    Number.isInteger(d.version) &&
    d.version >= 1 &&
    d.namespace.endsWith('/') &&
    /^[a-z][a-z0-9+.-]*:/i.test(d.namespace) &&
    /^[a-z][a-z0-9+.-]*:/i.test(d.classIri) &&
    d.keys.length > 0 &&
    new Set(d.keys).size === d.keys.length &&
    d.keys.every((key) => names.has(key)) &&
    d.fields.every(
      (field) =>
        names.has(field.column) &&
        /^[a-z][a-z0-9+.-]*:/i.test(field.predicate) &&
        (field.kind === 'string' || field.empty !== 'literal') &&
        (!field.referenceNamespace ||
          (field.referenceNamespace.endsWith('/') &&
            field.referenceColumns.length > 0 &&
            field.referenceColumns.every((key) => names.has(key)))),
    ),
  )
}
