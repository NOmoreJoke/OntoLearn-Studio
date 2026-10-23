/** Structural consumer types from approved API002 (ENTRY cd80abe3…).
 * These are presentation types, not a second wire validator or source authority.
 * T01 supplies the actual DesktopBridge; this module never exposes generic IPC.
 */
import type { BridgeResult, JobView, ProjectView, TaskUpdate } from '@ontolearn/contracts'
import type { RdfRow } from './view-model'

/** Exact API003 phase1 presentation shape, not an independent public validator. */
export type EntityMetadata = {
  identifier: string
  labels: [string, string][]
  definitions: [string, string][]
  synonyms: string[]
  examples: string[]
}
export type MetadataNamespace = {
  entityMetadataVersion: 1
  entities: Record<string, EntityMetadata>
}

export type CurrentProject = Omit<ProjectView, 'formatVersion'> & { formatVersion: 2 | 3 }
export type MainlineTaskUpdate =
  | Exclude<TaskUpdate, { kind: 'restored' }>
  | {
      kind: 'restored'
      generation: number
      view: { generation: number; project: CurrentProject | null; jobs: JobView[] }
    }

export type DomainRead = {
  readVersion: 1
  projectId: string
  inputSnapshotId: string
  workspace: {
    draft:
      | { state: 'missing'; editor: string }
      | {
          state: 'present' | 'tombstone'
          editor: string
          generation: number
          present: boolean
          boundDomainRevision: number
          contentHash: string | null
          contentJson: string | null
        }
  }
  domain: {
    projectRevision: number
    dependencyVector: Record<string, number>
    state: {
      definitions: Array<{ layer: string; id: string; payload: string }>
      facts: Array<{
        id: string
        subject: string
        predicate: string
        object: string | null
        owner: string | null
        source_row: string | null
        managed_value: string | null
      }>
      mappingState: Record<string, unknown>
    }
  }
}
export type EditPlan = {
  definitions?: Array<{
    layer: 'ontology'
    id: string
    value: {
      triples: RdfRow[]
      references?: Array<{ layer: string; id: string }>
      singleValuedPredicates?: string[]
      entityMetadata?: MetadataNamespace
    }
  }>
  remove_definitions?: Array<{ layer: 'ontology'; id: string }>
  manual?: Array<{ id: string; subject: string; predicate: string; object: string }>
  edits?: Record<string, string>
  remove?: string[]
}
export type PreviewArgs =
  | { baseRevision: number; intent: 'change'; plan: EditPlan }
  | { baseRevision: number; intent: 'undo'; targetOperationId: string }
export type Segment = {
  ordinal: number
  byteOffset: number
  rawByteLength: number
  sha256: string
}
export type Manifest = {
  documentKind: 'diff' | 'undo-impact'
  documentHash: string
  totalBytes: number
  segmentCount: number
  segments: Segment[]
}
export type DiffPage = {
  projectId: string
  previewHash: string
  documentKind: 'diff' | 'undo-impact'
  documentHash: string
  segments: Array<Segment & { dataBase64: string }>
  nextCursor: string
  complete: boolean
}
export type Preview = {
  projectId: string
  baseRevision: number
  previewHash: string
  summary: string
  manifest: Manifest
} & (
  | {
      status: 'ready'
      preparedPlanRef: string
      inputSnapshotId: string
      parametersHash: string
      intent: 'change' | 'undo'
      targetOperationId: string | null
    }
  | { status: 'conflict'; targetOperationId: string; impactComplete: boolean }
)
export type Confirmation = {
  projectId: string
  previewHash: string
  preparedPlanRef: string
  confirmationRef: string
  inputSnapshotId: string
  parametersHash: string
}
export type DraftSaveArgs = {
  operationId: string
  editor: string
  expectedGeneration: number
  boundDomainRevision: number
  contentJson: string
}
export interface OntologyMainlineBridge {
  saveProjectDraft(args: DraftSaveArgs): Promise<
    BridgeResult<{
      draftSaveVersion: 1
      projectId: string
      operationId: string
      operationSequence: number
      editor: string
      generation: number
      boundDomainRevision: number
      contentHash: string
      afterCheckpointRef: string
    }>
  >
  readProject(args: { editor: string }): Promise<BridgeResult<DomainRead>>
  getActiveProject(): Promise<BridgeResult<CurrentProject | null>>
  previewProjectChangeset(args: PreviewArgs): Promise<BridgeResult<Preview>>
  getProjectDiffPage(args: {
    previewHash: string
    documentKind: 'diff' | 'undo-impact'
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<DiffPage>>
  confirmProjectChangeset(args: {
    previewHash: string
    completionCursor: string
  }): Promise<BridgeResult<Confirmation>>
  commitProjectChangeSet(args: {
    operationId: string
    confirmation: Confirmation
  }): Promise<BridgeResult<JobView>>
  getJob(jobId: string): Promise<BridgeResult<JobView>>
  listJobs(args: {
    filter: 'all' | 'active' | 'terminal'
    pageSize: number
    listSnapshotId: string | null
    cursor: string | null
  }): Promise<BridgeResult<Record<string, unknown>>>
  getOperation(operationId: string): Promise<BridgeResult<Record<string, unknown> | null>>
  cancelJob(jobId: string): Promise<BridgeResult<Record<string, unknown>>>
  onTaskUpdate(listener: (update: MainlineTaskUpdate) => void): () => void
}
