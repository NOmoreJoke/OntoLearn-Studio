// Verbatim API002 type-only source excerpts. No runtime bridge or issuer.
// Source SHA d885838a1b6e13643f3503e1a413fa98bf220cb83350a5c498b1258fa3c46475
export interface SafeError {
  code: string
  messageKey: string
  params: Record<string, unknown>
  retryable: boolean
}

export type BridgeResult<T> = { ok: true; data: T } | { ok: false; error: SafeError }

export interface ProjectView {
  projectId: string
  projectRevision: number
  inputSnapshotId: string
  dependencyVector: Record<string, number>
  formatVersion: 2 | 3
}

export interface JobView extends Record<string, unknown> {
  inputSnapshotId: string
  projectId: string
  jobId: string
  operationId: string
  state: 'queued' | 'running' | 'cancelling' | 'succeeded' | 'failed' | 'cancelled'
  stateVersion: number
  resultRef: { resultId: string; inputSnapshotId: string } | null
  error: SafeError | null
}

export interface TaskView {
  generation: number
  project: ProjectView | null
  jobs: JobView[]
}

export interface ProgressView {
  stage: 'queued' | 'loading' | 'computing' | 'committing' | 'reconciling'
  completed: number | null
  total: number | null
}

export type TaskUpdate =
  | { kind: 'job'; generation: number; job: JobView; progress?: ProgressView }
  | { kind: 'restored'; generation: number; view: TaskView }
  | {
      kind: 'connection'
      generation: number
      projectId: string
      state: 'reconnecting' | 'offline'
      attempt: number
      error: SafeError
    }

export type ResultScopeDTO = 'asserted' | 'asserted+derived' | 'scenario'

export type ResultDefinitionLayerDTO =
  'ontology' | 'rule' | 'constraint' | 'behavior' | 'scenario' | 'mapping' | 'query'

export type ResultStaleDependenciesDTO = {
  ONTOLOGY_CHANGED: `ontology:${string}`
  FACTS_CHANGED: 'facts:asserted'
  MAPPING_INPUT_CHANGED: `mapping:${string}`
  VALIDATION_DEFINITION_CHANGED: `constraint:${string}`
  RULE_CHANGED: `rule:${string}`
  BEHAVIOR_CHANGED: `behavior:${string}`
  SCENARIO_CHANGED: `scenario:${string}`
  QUERY_CHANGED: `query:${string}`
}

export type ResultStaleReasonDTO = {
  [Code in keyof ResultStaleDependenciesDTO]: {
    code: Code
    dependency: ResultStaleDependenciesDTO[Code]
    before: number
    after: number
  }
}[keyof ResultStaleDependenciesDTO]

export type ResultMetadataDTO = {
  resultId: string
  projectId: string
  jobId: string
  kind: 'query' | 'reasoning' | 'validation' | 'behavior' | 'scenario' | 'test' | 'receipt'
  definitionId: string
  inputSnapshotId: string
  inputProjectRevision: number
  dependencyVector: Record<string, number>
  definitionSetDigests: Partial<Record<ResultDefinitionLayerDTO, string>>
  implementation: {
    executionSemanticsVersion: string
    engineVersion: string
    dependencyLockHash: string
  }
  scope: ResultScopeDTO
  parametersHash: string
  state: 'current' | 'stale' | 'historical'
  staleReason: ResultStaleReasonDTO[]
  payloadStatus: 'available' | 'evicted'
  createdAtMs: number
  historicalSelectionRequired: boolean
}

export type ResultPageBindingDTO = {
  projectId: string
  resultId: string
  inputSnapshotId: string
  scope: ResultScopeDTO
  parametersHash: string
  order: 'ordinal+rowId:asc'
}

export type ResultRowDTO = {
  rowId: string
  ordinal: number
  cells: Array<string | number | boolean | null>
}

export type ResultPageDTO = {
  binding: ResultPageBindingDTO
  rows: ResultRowDTO[]
  nextCursor: string | null
}

export interface ChangeSetSegmentDescriptor {
  ordinal: number
  byteOffset: number
  rawByteLength: number
  sha256: string
}

export interface ChangeSetManifest {
  documentKind: 'diff' | 'undo-impact'
  documentHash: string
  totalBytes: number
  segmentCount: number
  segments: ChangeSetSegmentDescriptor[]
}

export interface ChangeSetPage {
  projectId: string
  previewHash: string
  documentKind: 'diff' | 'undo-impact'
  documentHash: string
  segments: Array<ChangeSetSegmentDescriptor & { dataBase64: string }>
  nextCursor: string
  complete: boolean
}

export type ChangeSetPreview =
  | {
      status: 'ready'
      projectId: string
      baseRevision: number
      previewHash: string
      preparedPlanRef: string
      inputSnapshotId: string
      parametersHash: string
      intent: 'change' | 'undo'
      targetOperationId: string | null
      summary: string
      manifest: ChangeSetManifest
    }
  | {
      status: 'conflict'
      projectId: string
      baseRevision: number
      previewHash: string
      targetOperationId: string
      summary: string
      impactComplete: boolean
      manifest: ChangeSetManifest
    }

export interface ChangeSetConfirmation {
  projectId: string
  previewHash: string
  preparedPlanRef: string
  confirmationRef: string
  inputSnapshotId: string
  parametersHash: string
}

export type QuerySelectionDTO = { kind: 'current' } | { kind: 'historical'; snapshotId: string }

export type QueryDraftDTO = {
  name: string
  description: string
  sparql: string
  scope: 'asserted' | 'asserted+derived'
  capabilityQuestion: string
  source: 'template' | 'visual' | 'editor' | 'model'
}

export type QueryDefinitionBindingDTO = {
  definitionId: string
  definitionVersion: number
  definitionSha256: string
  descriptorVersion: 1
  descriptorSha256: string
}

export type QueryExecutionIdentityDTO = {
  implementation: ResultMetadataDTO['implementation']
  limits: Record<string, number>
  registryHash: string
}

export type QueryDefinitionRecordDTO = {
  projectId: string
  definitionId: string
  baseProjectRevision: number
  inputSnapshotId: string
  definitionVersion: number
  definitionSha256: string
} & (
  | { kind: 'legacy'; text: string }
  | { kind: 'managed'; descriptorVersion: 1; descriptorSha256: string; draft: QueryDraftDTO }
)

export type QueryDefinitionLoadDTO = QueryDefinitionRecordDTO & { loadRef: string }

export type QueryIdentityDTO = {
  projectId: string
  resultId: string
  jobId: string
  inputSnapshotId: string
  inputProjectRevision: number
  scope: 'asserted'
  definitionId: string
  parametersHash: string
  implementation: ResultMetadataDTO['implementation']
  payloadSha256: string
  definitionSha256: string
  inputSelection: 'current' | 'historical'
  projectionVersion: 1
  lengthPolicyId: 'query-presentation-scalars-v1'
}

export type QueryCellDTO =
  | null
  | { kind: 'iri'; iri: string; n3: string }
  | {
      kind: 'literal'
      lexical: string
      n3: string
      literalType:
        { kind: 'plain' } | { kind: 'language'; tag: string } | { kind: 'datatype'; iri: string }
    }

export type QueryDescriptorWireDTO = {
  identity: QueryIdentityDTO
  metadata: ResultMetadataDTO
  executedText: { sha256: string; utf8Bytes: number; unicodeScalars: number; utf16Units: number }
  query:
    | { kind: 'ASK'; value: boolean }
    | { kind: 'SELECT'; columns: Array<{ index: number; name: string }>; rowCount: number }
}

export type QueryDescriptorDTO = QueryDescriptorWireDTO & { descriptorRef: string }

export type QueryTextPageDTO = {
  identity: QueryIdentityDTO
  kind: 'text'
  order: 'utf8-byte:asc'
  startUtf8Byte: number
  utf8Length: number
  text: string
  nextCursor: string | null
}

export type QueryRowsPageDTO = {
  identity: QueryIdentityDTO
  kind: 'rows'
  order: 'query-index:asc'
  rows: Array<{ index: number; rowKey: string; cells: QueryCellDTO[] }>
  nextCursor: string | null
}

export type QueryExecutionReceiptDTO = {
  operationId: string
  acceptedJob: JobView
  watch: { state: 'subscribed' } | { state: 'pending'; error: SafeError }
}

export type QueryExecuteArgs = {
  operationId: string
  loadRef: string
  visibleDraft: QueryDraftDTO
  selection: QuerySelectionDTO
}

export interface QueryConsumerBridge {
  getQueryDefinitionBase(): Promise<
    BridgeResult<{ baseRef: string; projectRevision: number; inputSnapshotId: string }>
  >
  loadQueryDefinition(args: {
    definitionId: string
    selection: QuerySelectionDTO
  }): Promise<BridgeResult<QueryDefinitionLoadDTO>>
  executeSavedQuery(args: QueryExecuteArgs): Promise<BridgeResult<QueryExecutionReceiptDTO>>
  getQueryResultDescriptor(args: { resultId: string }): Promise<BridgeResult<QueryDescriptorDTO>>
  getQueryExecutedTextPage(args: {
    descriptorRef: string
    maxUtf8Bytes: number
    cursor: string | null
  }): Promise<BridgeResult<QueryTextPageDTO>>
  getQueryRowsPage(args: {
    descriptorRef: string
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<QueryRowsPageDTO>>
}

export type MainlineMetadataDTO = {
  name: string | null
  templateRef: string | null
  archived: boolean
  mode: 'guided' | 'assisted'
  origin: 'created' | 'migration-default'
}

export type MainlineCatalogItemDTO = {
  projectId: string
  domainRevision: number
  metadataVersion: number
  metadata: MainlineMetadataDTO
  operationSequence: number
  checkpointRef: string
}

export type MainlineCatalogDTO = {
  catalogVersion: 1
  snapshotId: string
  items: MainlineCatalogItemDTO[]
  total: number
  offset: number
  nextCursor: string | null
}

export type MainlineCreateRequestDTO = {
  requestVersion: 1
  operationId: string
  name: string
  initialization: { kind: 'blank' }
}

export type MainlineCreateResultDTO = {
  createResultVersion: 1
  operationId: string
  projectId: string
  requestHash: string
  receipt: {
    projectCreateReceiptVersion: 1
    libraryEvidenceRef: string
    projectId: string
    operationId: string
    requestHash: string
    contextHash: string
    planHash: string
    operationSequence: 1
    domainRevision: 0
    metadataVersion: 1
    inputSnapshotId: string
    beforeCheckpointRef: string
    afterCheckpointRef: string
  }
}

export type MainlineDraftDTO =
  | { editor: string; state: 'missing' }
  | {
      editor: string
      state: 'present' | 'tombstone'
      generation: number
      present: boolean
      boundDomainRevision: number
      contentHash: string | null
      contentJson: string | null
    }

export type MainlineProjectReadDTO = {
  readVersion: 1
  projectId: string
  inputSnapshotId: string
  workspace: MainlineCatalogItemDTO & {
    workspaceVersion: 1
    inputSnapshotId: string
    draft: MainlineDraftDTO
  }
  domain: {
    projectRevision: number
    dependencyVector: Record<string, number>
    state: {
      definitions: Array<{ layer: ResultDefinitionLayerDTO; id: string; payload: string }>
      facts: Array<{
        id: string
        subject: string
        predicate: string
        object: string | null
        owner: string | null
        source_row: string | null
        managed_value: string | null
      }>
      mappingState: Record<
        string,
        {
          generatedVersion: number
          stale: Array<{ code: string; dependency: string; before: number; after: number }>
        }
      >
    }
  }
}

export type MainlineChangePlanDTO = {
  definitions?: Array<
    | {
        layer: 'ontology'
        id: string
        value: {
          triples: Array<{ subject: string; predicate: string; object: string }>
          references?: Array<{ layer: string; id: string }>
          singleValuedPredicates?: string[]
        }
      }
    | {
        layer: 'query'
        id: string
        value: {
          text: string
          references: Array<{ layer: string; id: string }>
          descriptor: Omit<QueryDraftDTO, 'sparql'> & { version: 1 }
        }
      }
  >
  remove_definitions?: Array<{ layer: 'ontology' | 'query'; id: string }>
  manual?: Array<{ id: string; subject: string; predicate: string; object: string }>
  edits?: Record<string, string>
  remove?: string[]
}

export type MainlinePreviewArgs =
  | { baseRevision: number; intent: 'change'; plan: MainlineChangePlanDTO }
  | { baseRevision: number; intent: 'undo'; targetOperationId: string }

export interface MainlineProjectBridge {
  saveProjectDraft(args: MainlineDraftSaveArgs): Promise<BridgeResult<MainlineDraftSaveResultDTO>>
  getProjectCatalog(args: {
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<MainlineCatalogDTO>>
  createBlankProject(args: MainlineCreateRequestDTO): Promise<BridgeResult<MainlineCreateResultDTO>>
  createExampleProject(
    args: MainlineExampleCreateRequestDTO,
  ): Promise<BridgeResult<MainlineExampleCreateResultDTO>>
  openProject(args: { projectId: string }): Promise<BridgeResult<ProjectView>>
  readProject(args: { editor: string }): Promise<BridgeResult<MainlineProjectReadDTO>>
  previewProjectChangeset(args: MainlinePreviewArgs): Promise<BridgeResult<ChangeSetPreview>>
  getProjectDiffPage(args: {
    previewHash: string
    documentKind: 'diff' | 'undo-impact'
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<ChangeSetPage>>
  confirmProjectChangeset(args: {
    previewHash: string
    completionCursor: string
  }): Promise<BridgeResult<ChangeSetConfirmation>>
  commitProjectChangeSet(args: {
    operationId: string
    confirmation: ChangeSetConfirmation
  }): Promise<BridgeResult<JobView>>
}

export type MainlineDraftSaveArgs = {
  operationId: string
  editor: string
  expectedGeneration: number
  boundDomainRevision: number
  contentJson: string
}

export type MainlineDraftSaveResultDTO = {
  draftSaveVersion: 1
  projectId: string
  operationId: string
  operationSequence: number
  editor: string
  generation: number
  boundDomainRevision: number
  contentHash: string
  afterCheckpointRef: string
}

export type MainlineExampleCreateRequestDTO = {
  exampleCreateRequestVersion: 1
  operationId: string
  name: string
  exampleId: 'equipment-maintenance'
  inputDigest: '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e'
}

export type MainlineExampleCreateResultDTO = Omit<MainlineCreateResultDTO, 'receipt'> & {
  receipt: Omit<
    MainlineCreateResultDTO['receipt'],
    'projectCreateReceiptVersion' | 'domainRevision'
  > & {
    exampleCreateReceiptVersion: 1
    exampleId: 'equipment-maintenance'
    inputDigest: MainlineExampleCreateRequestDTO['inputDigest']
    domainRevision: 1
  }
}
