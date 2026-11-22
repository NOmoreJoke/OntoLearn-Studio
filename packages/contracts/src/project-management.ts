import type { BridgeResult, MainlineCatalogItemDTO, MainlineMetadataDTO } from './index'

/** Finite local project actions. No caller-provided patch, path or database handle. */
export type MainlineManagementAction =
  | { kind: 'rename'; name: string }
  | { kind: 'archive'; archived: boolean }
  | { kind: 'set-mode'; mode: 'guided' | 'assisted' }
  | { kind: 'copy-current'; name: string }
  | { kind: 'trash' }
  | { kind: 'restore-trash' }

export type MainlineManagementKind = MainlineManagementAction['kind']
export type MainlineManagementCatalogState = 'active' | 'archived' | 'trashed'
export type MainlineManagementItemDTO = MainlineCatalogItemDTO & {
  lifecycle: { state: 'active' | 'trashed'; version: number }
}
export type MainlineManagementCatalogDTO = {
  catalogVersion: 1
  snapshotId: string
  items: MainlineManagementItemDTO[]
  total: number
  offset: number
  nextCursor: string | null
}
export type MainlineManagementDocumentDTO = {
  projectName: string | null
  checkpointRef: string
  domainRevision: number
  operationSequence: number
  metadataVersion: number
  lifecycleVersion: number
  beforeMetadata: MainlineMetadataDTO
  afterMetadata: MainlineMetadataDTO
  counts: {
    definitions: number
    facts: number
    tombstones: number
    drafts: number
    learning: number
    historyRuns: number
    activeJobs: number
  }
  coverage: string[]
  exclusions: string[]
  seedHash: string | null
}
export type MainlineManagementPreviewDTO = {
  managementPreviewVersion: 1
  previewRef: string
  projectId: string
  action: MainlineManagementAction
  documentHash: string
  document: MainlineManagementDocumentDTO
  expiresAtMs: number
}
export type MainlineManagementConfirmationDTO = {
  confirmationRef: string
  previewRef: string
  documentHash: string
  projectId: string
  kind: MainlineManagementKind
}
export type MainlineManagementApplyParams = {
  projectId: string
  operationId: string
  confirmationRef: string
  documentHash: string
}
export type MainlineManagementResultDTO = {
  managementResultVersion: 1
  kind: MainlineManagementKind
  projectId: string
  operationId: string
  targetProjectId: string
  requestHash: string
  receiptHash: string
  checkpointRef: string
  domainRevision: number
  metadataVersion: number
  operationSequence: number
  lifecycleVersion: number
  lifecycleState: 'active' | 'trashed'
}
export type MainlineManagementOperationDTO =
  { state: 'not-found'; result: null } | { state: 'applied'; result: MainlineManagementResultDTO }
export type MainlineLibraryStatusDTO = { libraryEvidenceRef: string; activeJobs: number }
export type PendingProjectManagementOperationDTO = {
  operationId: string
  projectId: string
  kind: MainlineManagementKind
  label: string | null
}

export interface ProjectManagementBridge {
  getPendingProjectManagementOperations(): Promise<
    BridgeResult<PendingProjectManagementOperationDTO[]>
  >
  getProjectManagementCatalog(args: {
    state: MainlineManagementCatalogState
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<MainlineManagementCatalogDTO>>
  getProjectManagementState(): Promise<BridgeResult<MainlineManagementItemDTO>>
  previewProjectManagement(args: {
    action: MainlineManagementAction
    expectedCheckpointRef: string
    expectedLifecycleVersion: number
    /** Only the finite restore-trash action may address a library catalog row. */
    restoreProjectId?: string
  }): Promise<BridgeResult<MainlineManagementPreviewDTO>>
  confirmProjectManagement(args: {
    previewRef: string
    documentHash: string
  }): Promise<BridgeResult<MainlineManagementConfirmationDTO>>
  applyProjectManagement(args: {
    operationId: string
    confirmationRef: string
    documentHash: string
  }): Promise<BridgeResult<MainlineManagementResultDTO>>
  getProjectManagementOperation(args: {
    operationId: string
  }): Promise<BridgeResult<MainlineManagementOperationDTO>>
}

export type LibraryLocationView = { label: string; libraryId: string | null; pending: boolean }
export type LibraryLocationChoice = {
  choiceRef: string
  label: string
  intent: 'create' | 'open'
}
export type LibraryWorkspaceReport = {
  documentNonce: string
  generation: number
  dirty: boolean
  unresolved: boolean
}
export interface LibraryLocationBridge {
  getLibraryLocation(): Promise<BridgeResult<LibraryLocationView>>
  chooseLibraryLocation(args: {
    intent: 'create' | 'open'
  }): Promise<BridgeResult<LibraryLocationChoice | null>>
  reportLibraryWorkspace(args: LibraryWorkspaceReport): Promise<BridgeResult<null>>
  switchLibraryLocation(args: {
    choiceRef: string
    documentNonce: string
    workspaceGeneration: number
  }): Promise<BridgeResult<{ restartRequested: true }>>
}
