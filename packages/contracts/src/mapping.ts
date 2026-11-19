import type { BridgeResult } from './index'

export type MappingEncoding = 'utf-8' | 'gb18030' | 'big5' | 'utf-16'

export type MappingFieldDraft = {
  column: string
  predicate: string
  kind: 'string' | 'integer' | 'decimal' | 'boolean' | 'date' | 'datetime'
  trim: boolean
  empty: 'omit' | 'error' | 'literal'
  referenceNamespace: string
  referenceColumns: Array<string>
}

export type MappingDraft = {
  identity: string
  version: number
  namespace: string
  classIri: string
  keys: Array<string>
  fields: Array<MappingFieldDraft>
}

export type MappingIssueDTO = {
  code:
    | 'INVALID_SOURCE'
    | 'INVALID_CSV'
    | 'INVALID_XLSX'
    | 'INVALID_CELL'
    | 'XLSX_CELL_ERROR'
    | 'EMPTY_SOURCE'
    | 'EMPTY_HEADER'
    | 'INVALID_HEADER'
    | 'ROW_WIDTH'
    | 'SOURCE_LIMIT'
    | 'ENCODING_UNSUPPORTED'
    | 'INVALID_ENCODING'
    | 'ENCRYPTED_UNSUPPORTED'
    | 'MACRO_UNSUPPORTED'
    | 'UNSAFE_XML'
    | 'XLSX_PARSER_UNAVAILABLE'
    | 'SHEET_REQUIRED'
    | 'SHEET_NOT_FOUND'
    | 'FORMULA_CACHE_MISSING'
    | 'EMPTY_KEY'
    | 'DUPLICATE_KEY'
    | 'DUPLICATE_IDENTITY'
    | 'CONVERSION_FAILED'
    | 'INVALID_VALUE'
    | 'INVALID_REFERENCE'
    | 'MISSING_REFERENCE'
    | 'UNKNOWN_MAPPING_ISSUE'
  messageKey:
    | 'mapping.sourceInvalid'
    | 'mapping.sourceLimit'
    | 'mapping.encodingUnsupported'
    | 'mapping.encodingInvalid'
    | 'mapping.sourceUnsafe'
    | 'mapping.sourceUnavailable'
    | 'mapping.sheetInvalid'
    | 'mapping.formulaCacheMissing'
    | 'mapping.emptyKey'
    | 'mapping.duplicateKey'
    | 'mapping.conversionFailed'
    | 'mapping.referenceInvalid'
    | 'mapping.issueUnknown'
  sheet: string
  row: number
  column: number
  field: string
}

export type MappingConflictDTO = {
  code: 'MANUAL_DRIFT' | 'OWNERSHIP_CONFLICT'
  current: null | string
  source: null | string
  managed: null | string
  owner: null | string
  sourceRow: null | string
  subject: string
  predicate: string
}

export type MappingSourceSelectArgs = {
  projectId: string
  selectionId?: string
  sheet?: string
  encoding?: null | MappingEncoding
}

export type MappingSuggestionDTO = {
  column: string
  predicate: string
  basis: 'exact-field-name'
  samples: string[]
}

export type MappingSourceSelectResultDTO = {
  projectId: string
  selectionId: string
  fingerprint: string
  format: 'csv' | 'xlsx'
  sheets: Array<string>
  sheet: string
  encoding: null | MappingEncoding
  fields: Array<{
    name: string
    observedTypes: Array<string>
    samples: Array<string>
  }>
  totalRows: number
  suggestions?: MappingSuggestionDTO[]
}

export type MappingPreviewArgs = {
  projectId: string
  selectionId: string
  sheet: string
  encoding: null | MappingEncoding
  draft: MappingDraft
  page?: {
    offset: number
    limit: number
  }
}

export type MappingPreviewResultDTO = {
  projectId: string
  resultId: string
  baseRevision: number
  selectionId: string
  sheet: string
  encoding: null | MappingEncoding
  sourceFingerprint: string
  rows: Array<{
    sourceRow: string
    input: Array<string>
    rdf: Array<string>
  }>
  offset: number
  totalRows: number
  identitiesAdded: Array<string>
  identitiesRemoved: Array<string>
  issues: Array<MappingIssueDTO>
  conflicts: Array<MappingConflictDTO>
  added: Array<string>
  removed: Array<string>
  modified: Array<{
    subject: string
    predicate: string
    before: Array<string>
    after: Array<string>
  }>
}

export type MappingPreparedChangePlan = {
  mappingPreparation: {
    resultId: string
    preparationRef: string
  }
}

export type MappingPrepareCommitArgs = {
  projectId: string
  resultId: string
  selectionId: string
  sourceFingerprint: string
  baseRevision: number
  operationId: string
}

export type MappingPrepareCommitResultDTO = {
  projectId: string
  resultId: string
  selectionId: string
  sourceFingerprint: string
  baseRevision: number
  operationId: string
  plan: MappingPreparedChangePlan
}

export type MappingDraftReadArgs = {
  projectId: string
  mappingId: string
}

export type MappingDraftReadResultDTO = {
  projectId: string
  mappingId: string
  generation: number
  baseRevision: number
  draft: null | MappingDraft
}

export type MappingDraftSaveArgs = {
  projectId: string
  operationId: string
  expectedGeneration: number
  baseRevision: number
  draft: MappingDraft
}

export type MappingDraftSaveResultDTO = {
  projectId: string
  operationId: string
  generation: number
  baseRevision: number
  draft: MappingDraft
}

export const mappingPublicIssueKeys = {
  INVALID_SOURCE: 'mapping.sourceInvalid',
  INVALID_CSV: 'mapping.sourceInvalid',
  INVALID_XLSX: 'mapping.sourceInvalid',
  INVALID_CELL: 'mapping.sourceInvalid',
  XLSX_CELL_ERROR: 'mapping.sourceInvalid',
  EMPTY_SOURCE: 'mapping.sourceInvalid',
  EMPTY_HEADER: 'mapping.sourceInvalid',
  INVALID_HEADER: 'mapping.sourceInvalid',
  ROW_WIDTH: 'mapping.sourceInvalid',
  SOURCE_LIMIT: 'mapping.sourceLimit',
  ENCODING_UNSUPPORTED: 'mapping.encodingUnsupported',
  INVALID_ENCODING: 'mapping.encodingInvalid',
  ENCRYPTED_UNSUPPORTED: 'mapping.sourceUnsafe',
  MACRO_UNSUPPORTED: 'mapping.sourceUnsafe',
  UNSAFE_XML: 'mapping.sourceUnsafe',
  XLSX_PARSER_UNAVAILABLE: 'mapping.sourceUnavailable',
  SHEET_REQUIRED: 'mapping.sheetInvalid',
  SHEET_NOT_FOUND: 'mapping.sheetInvalid',
  FORMULA_CACHE_MISSING: 'mapping.formulaCacheMissing',
  EMPTY_KEY: 'mapping.emptyKey',
  DUPLICATE_KEY: 'mapping.duplicateKey',
  DUPLICATE_IDENTITY: 'mapping.duplicateKey',
  CONVERSION_FAILED: 'mapping.conversionFailed',
  INVALID_VALUE: 'mapping.conversionFailed',
  INVALID_REFERENCE: 'mapping.referenceInvalid',
  MISSING_REFERENCE: 'mapping.referenceInvalid',
  UNKNOWN_MAPPING_ISSUE: 'mapping.issueUnknown',
} as const

export interface MappingBridge {
  selectMappingSource(
    args: Omit<MappingSourceSelectArgs, 'projectId'>,
  ): Promise<BridgeResult<MappingSourceSelectResultDTO>>
  previewMapping(
    args: Omit<MappingPreviewArgs, 'projectId'>,
  ): Promise<BridgeResult<MappingPreviewResultDTO>>
  prepareMappingCommit(
    args: Omit<MappingPrepareCommitArgs, 'projectId'>,
  ): Promise<BridgeResult<MappingPrepareCommitResultDTO>>
  readMappingDraft(
    args: Omit<MappingDraftReadArgs, 'projectId'>,
  ): Promise<BridgeResult<MappingDraftReadResultDTO>>
  saveMappingDraft(
    args: Omit<MappingDraftSaveArgs, 'projectId'>,
  ): Promise<BridgeResult<MappingDraftSaveResultDTO>>
}
