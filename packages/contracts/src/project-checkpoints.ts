import type { BridgeResult, MainlineMetadataDTO } from './index'

/** Whole-project checkpoints and restore. Wire creation only mints manual
 *  checkpoints; the other trigger reasons belong to their real providers. */
export type ProjectCheckpointReason =
  'genesis' | 'manual' | 'before-run' | 'guided-stage' | 'before-agent' | 'restore' | 'operation'

export type ProjectCheckpointItemDTO = {
  checkpointRef: string
  operationSequence: number
  domainRevision: number
  domainSnapshotRef: string
  metadataVersion: number
  reason: ProjectCheckpointReason
  label: string | null
  operationId: string | null
  operationKind: 'legacy-domain' | 'domain' | 'application' | 'combined' | null
  counts: { definitions: number; facts: number; drafts: number; learning: number }
  coverage: string[]
  preserved: string[]
  isCurrent: boolean
}

export type ProjectCheckpointListDTO = {
  checkpointListVersion: 1
  projectId: string
  items: ProjectCheckpointItemDTO[]
  total: number
  offset: number
  nextCursor: string | null
}

export type ProjectCheckpointCreateDTO = {
  checkpointCreateVersion: 1
  projectId: string
  operationId: string
  operationSequence: number
  checkpointRef: string
  reason: 'manual'
  label: string | null
  domainRevision: number
  metadataVersion: number
}

export type RestoreSegmentDTO = {
  ordinal: number
  byteOffset: number
  rawByteLength: number
  sha256: string
  dataBase64: string
}

export type RestoreManifestDTO = {
  documentKind: 'restore-impact'
  documentHash: string
  totalBytes: number
  segmentCount: number
  segments: Array<Omit<RestoreSegmentDTO, 'dataBase64'>>
}

export type ProjectRestorePreviewDTO = {
  restorePreviewVersion: 1
  previewRef: string
  projectId: string
  documentHash: string
  manifest: RestoreManifestDTO
  targetCheckpointRef: string
  targetOperationSequence: number
  targetDomainRevision: number
  currentCheckpointRef: string
  currentOperationSequence: number
  interveningOperationCount: number
  domainWillRestore: boolean
  expiresAtMs: number
}

export type ProjectRestorePageDTO = {
  restorePageVersion: 1
  projectId: string
  previewRef: string
  documentHash: string
  segments: RestoreSegmentDTO[]
  nextCursor: string | null
  complete: boolean
}

export type ProjectRestoreConfirmationDTO = {
  restoreConfirmationVersion: 1
  projectId: string
  previewRef: string
  documentHash: string
  preparedPlanRef: string
  confirmationRef: string
  expiresAtMs: number
}

export type ProjectRestoreApplyArgs = {
  operationId: string
  confirmationRef: string
  documentHash: string
}

export type ProjectRestoreResultDTO = {
  restoreResultVersion: 1
  projectId: string
  operationId: string
  requestHash: string
  receiptHash: string
  checkpointRef: string
  operationSequence: number
  domainRevision: number
  metadataVersion: number
  restoredFromCheckpointRef: string
  coverage: string[]
  preserved: string[]
}

export type ProjectRestoreOperationDTO =
  { state: 'not-found'; result: null } | { state: 'applied'; result: ProjectRestoreResultDTO }

export type PendingProjectRestoreOperationDTO = {
  operationId: string
  projectId: string
  targetCheckpointRef: string
  documentHash: string
}

export interface ProjectCheckpointBridge {
  listProjectCheckpoints(args: {
    pageSize: number
    cursor: string | null
  }): Promise<BridgeResult<ProjectCheckpointListDTO>>
  createProjectCheckpoint(args: {
    operationId: string
    label: string | null
  }): Promise<BridgeResult<ProjectCheckpointCreateDTO>>
  getPendingProjectRestoreOperations(): Promise<BridgeResult<PendingProjectRestoreOperationDTO[]>>
  previewProjectRestore(args: {
    targetCheckpointRef: string
    expectedCheckpointRef: string
    expectedLifecycleVersion: number
  }): Promise<BridgeResult<ProjectRestorePreviewDTO>>
  getProjectRestorePage(args: {
    previewRef: string
    cursor: string | null
  }): Promise<BridgeResult<ProjectRestorePageDTO>>
  confirmProjectRestore(args: {
    previewRef: string
    documentHash: string
    readSegmentHashes: string[]
  }): Promise<BridgeResult<ProjectRestoreConfirmationDTO>>
  restoreProject(args: ProjectRestoreApplyArgs): Promise<BridgeResult<ProjectRestoreResultDTO>>
  getProjectRestoreOperation(args: {
    operationId: string
  }): Promise<BridgeResult<ProjectRestoreOperationDTO>>
}

/** Decoded restore-impact document; the raw segments remain the authority. */
export type RestoreImpactDocument = {
  restoreImpactVersion: 1
  projectId: string
  targetCheckpointRef: string
  target: {
    operationSequence: number
    domainRevision: number
    domainSnapshotRef: string
    metadataVersion: number
  }
  current: {
    checkpointRef: string
    operationSequence: number
    domainRevision: number
    metadataVersion: number
  }
  domainWillRestore: boolean
  domainDiff: Array<{ resource: string[]; before: unknown; after: unknown }>
  metadata: { before: MainlineMetadataDTO; after: MainlineMetadataDTO }
  drafts: Array<{ editor: string; before: unknown; after: unknown }>
  learning: Array<{
    attempt: string
    before: unknown
    after: unknown
    withdrawnByRestore: boolean
  }>
  interveningOperations: Array<{
    sequence: number
    operationId: string
    operationKind: string
    changeType: string
  }>
  coverage: string[]
  preserved: string[]
}
