import type { BridgeResult } from './index'

export type ProjectPackageRole =
  | 'definitions'
  | 'assertions'
  | 'ownership'
  | 'checkpoint'
  | 'agent-session'
  | 'raw-source'
  | 'derived'
  | 'history'

export type ProjectPackageOptions = {
  agentSessions: boolean
  rawSources: boolean
  derived: boolean
  history: boolean
}

export type ProjectPackageKind = 'full' | 'template'

export type ProjectPackageManifestDTO = {
  formatVersion: 'ontolearn-project-package-v1'
  kind: ProjectPackageKind
  dbFormatVersion: number
  checkpointSchemaVersion: number
  applicationStateVersion: number
  minReaderVersion: number
  minWriterVersion: number
  options: ProjectPackageOptions
  files: Array<{
    path: string
    role: ProjectPackageRole
    size: number
    sha256: string
  }>
}

export type TransferPickerPurpose = 'package-export' | 'package-import' | 'report-html'

export type TransferPickerArgs = {
  purpose: TransferPickerPurpose
}

export type TransferPickerResultDTO =
  | {
      projectId: string
      selectionId: string
      purpose: 'report-html'
      extension: '.html'
    }
  | {
      projectId: string
      selectionId: string
      purpose: 'package-export' | 'package-import'
      extension: '.ontolearn.zip'
    }

export type ProjectPackageConflictPolicy = {
  version: 1
  ownership: 'reject'
  projectIdentity: 'new-project-id'
  fingerprint: string
}

export type ProjectPackagePortabilityDTO = {
  restoreCurrent: boolean
  rerunMapping: boolean
  replayScenario: boolean
  missing: Array<
    | 'raw-source'
    | 'mapping-definition'
    | 'history'
    | 'scenario-input'
    | 'scenario-configuration'
    | 'execution-semantics'
  >
}

export type PackageExportCheckArgs = {
  projectId: string
  selectionId: string
  kind: ProjectPackageKind
  baseRevision: number
  options: ProjectPackageOptions
}

export type PackageExportCheckResultDTO = {
  projectId: string
  selectionId: string
  kind: ProjectPackageKind
  baseRevision: number
  options: ProjectPackageOptions
  checkRef: string
  manifest: ProjectPackageManifestDTO
  conflictPolicy: ProjectPackageConflictPolicy
  portability: ProjectPackagePortabilityDTO
}

export type PackageExportArgs = {
  projectId: string
  selectionId: string
  checkRef: string
  operationId: string
}

type PublicationFile = { sha256: string; byteLength: number }
type PublicationCleanup = 'complete' | 'pending'

export type TransferPublicationReceiptDTO =
  | (PublicationFile & {
      state: 'published'
      cleanup: PublicationCleanup
      durability: 'confirmed' | 'unconfirmed'
      postPublicationError: boolean
    })
  | (PublicationFile & { state: 'publication-unconfirmed'; cleanup: PublicationCleanup })
  | { state: 'cancelled'; cleanup: PublicationCleanup }
  | {
      state: 'failed'
      cleanup: PublicationCleanup
      code: 'destination-invalid' | 'target-exists' | 'busy' | 'cleanup-pending' | 'write-failed'
    }

export type PackageExportResultDTO = {
  projectId: string
  selectionId: string
  checkRef: string
  operationId: string
  kind: ProjectPackageKind
  publication: TransferPublicationReceiptDTO
}

export type PackageImportCheckArgs = {
  projectId: string
  selectionId: string
  expectedKind: ProjectPackageKind
}

export type PackageImportCheckResultDTO =
  | {
      projectId: string
      selectionId: string
      expectedKind: ProjectPackageKind
      status: 'compatible'
      checkRef: string
      manifest: ProjectPackageManifestDTO
      packageSha256: string
      conflictPolicy: ProjectPackageConflictPolicy
      portability: ProjectPackagePortabilityDTO
    }
  | {
      projectId: string
      selectionId: string
      expectedKind: ProjectPackageKind
      status: 'rejected'
      reason:
        | 'format-unsupported'
        | 'reader-too-old'
        | 'writer-too-old'
        | 'database-unsupported'
        | 'checkpoint-unsupported'
        | 'application-unsupported'
        | 'kind-mismatch'
        | 'unsafe-package'
    }

export type PackageImportArgs = {
  projectId: string
  selectionId: string
  checkRef: string
  operationId: string
  expectedKind: ProjectPackageKind
  packageSha256: string
}

export type PackageImportResultDTO = {
  projectId: string
  selectionId: string
  checkRef: string
  operationId: string
  kind: ProjectPackageKind
  packageSha256: string
  importedProjectId: string
  conflictPolicy: ProjectPackageConflictPolicy
}

export type ReportLearningAttemptDTO = {
  taskId: string
  attemptId: string
  transferTask: boolean
  operationCompleted: boolean
  hint: 'none' | 'concept' | 'operation' | 'partial' | 'full'
  agentAssistance: 'none' | 'partial' | 'full'
  check: {
    status: 'not-run' | 'passed' | 'failed' | 'error'
    evidenceRef: null | string
    summary: string
  }
  stageOutcomes: Array<string>
  independentTransferSuccess: boolean
}

export type PreparedHtmlReportDTO = {
  projectionVersion: 'ontolearn-report-v1'
  projectId: string
  title: string
  generatedAt: string
  projectRevision: number
  goals: Array<string>
  competencyQuestions: Array<string>
  learning: Array<ReportLearningAttemptDTO>
  ontologySummary: Array<string>
  dataSummary: Array<string>
  queryResults: Array<{
    resultId: string
    inputRevision: number
    semanticsVersion: string
    scope: string
    status: 'current' | 'stale' | 'historical' | 'failed' | 'cancelled'
    statusNote: string
    summary: string
  }>
  validationResults: Array<{
    resultId: string
    inputRevision: number
    semanticsVersion: string
    scope: string
    status: 'current' | 'stale' | 'historical' | 'failed' | 'cancelled'
    statusNote: string
    summary: string
  }>
  behaviorResults: Array<{
    resultId: string
    inputRevision: number
    semanticsVersion: string
    scope: string
    status: 'current' | 'stale' | 'historical' | 'failed' | 'cancelled'
    statusNote: string
    summary: string
  }>
  scenarioComparisons: Array<{
    resultId: string
    inputRevision: number
    semanticsVersion: string
    scope: string
    status: 'current' | 'stale' | 'historical' | 'failed' | 'cancelled'
    statusNote: string
    summary: string
  }>
  assumptions: Array<string>
  unresolved: Array<string>
}

export type ReportCredentialScan = {
  version: 1
  status: 'clear' | 'redacted'
}

export type HtmlReportPrepareArgs = {
  projectId: string
  baseRevision: number
}

export type HtmlReportPrepareResultDTO = {
  projectId: string
  baseRevision: number
  state: 'prepared'
  reportRef: string
  report: PreparedHtmlReportDTO
  credentialScan: ReportCredentialScan
}

export type HtmlReportExportArgs = {
  projectId: string
  selectionId: string
  reportRef: string
  baseRevision: number
  operationId: string
}

export type HtmlReportExportResultDTO = {
  projectId: string
  selectionId: string
  reportRef: string
  baseRevision: number
  operationId: string
  format: 'html'
  credentialScan: ReportCredentialScan
  publication: TransferPublicationReceiptDTO
}

export const projectPackageRoleOptions = {
  agentSessions: 'agent-session',
  rawSources: 'raw-source',
  derived: 'derived',
  history: 'history',
} as const
export const projectPackageCoreRoles = [
  'definitions',
  'assertions',
  'ownership',
  'checkpoint',
] as const
export const defaultProjectPackageOptions: Readonly<ProjectPackageOptions> = Object.freeze({
  agentSessions: false,
  rawSources: false,
  derived: false,
  history: false,
})

export interface TransferBridge {
  checkProjectPackageExport(
    args: Omit<PackageExportCheckArgs, 'projectId'>,
  ): Promise<BridgeResult<PackageExportCheckResultDTO>>
  exportProjectPackage(
    args: Omit<PackageExportArgs, 'projectId'>,
  ): Promise<BridgeResult<PackageExportResultDTO>>
  checkProjectPackageImport(
    args: Omit<PackageImportCheckArgs, 'projectId'>,
  ): Promise<BridgeResult<PackageImportCheckResultDTO>>
  importProjectPackage(
    args: Omit<PackageImportArgs, 'projectId'>,
  ): Promise<BridgeResult<PackageImportResultDTO>>
  prepareProjectHtmlReport(
    args: Omit<HtmlReportPrepareArgs, 'projectId'>,
  ): Promise<BridgeResult<HtmlReportPrepareResultDTO>>
  exportProjectHtmlReport(
    args: Omit<HtmlReportExportArgs, 'projectId'>,
  ): Promise<BridgeResult<HtmlReportExportResultDTO>>
  selectTransferFile(args: TransferPickerArgs): Promise<BridgeResult<TransferPickerResultDTO>>
}
