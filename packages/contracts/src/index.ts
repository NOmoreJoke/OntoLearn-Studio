import { z } from 'zod'
import { matchesOwnershipDetail, validateBusiness3, validateStartupError, validateV2 } from './v2'
import type { LibraryLocationBridge, ProjectManagementBridge } from './project-management'
export type * from './project-management'
import type { ProjectCheckpointBridge } from './project-checkpoints'
export type * from './project-checkpoints'
import type { LearningLedgerBridge } from './learning-ledger'
export type * from './learning-ledger'

export const PROTOCOL_VERSION = 2 as const
// Private preload delivery protocol. These are never exposed on DesktopBridge
// and grant no project, read, write, or backend terminal authority.
export const mainlineDeliveryEnvelopeSchema = z
  .object({ deliveryVersion: z.literal(1), deliveryId: z.uuid(), payload: z.unknown() })
  .strict()
export const mainlineDeliveryAckSchema = z
  .object({ deliveryVersion: z.literal(1), deliveryId: z.uuid() })
  .strict()
export const mainlineDeliveryAcceptedSchema = mainlineDeliveryAckSchema
  .extend({ accepted: z.literal(true) })
  .strict()
export const mainlineNoDeliverySchema = z
  .object({
    ok: z.literal(false),
    error: z
      .object({
        code: z.literal('PERMISSION_DENIED'),
        messageKey: z.literal('permission.denied'),
        params: z.object({}).strict(),
        retryable: z.literal(false),
      })
      .strict(),
  })
  .strict()
export const healthSchema = z
  .object({
    protocolVersion: z.literal(PROTOCOL_VERSION),
    engineVersion: z.string().min(1).max(128),
    status: z.literal('ok'),
    capabilities: z.array(z.literal('health')).max(1),
  })
  .strict()
// Display DTO only. Runtime protocol selection remains supervisor-owned.
export const displayHealthSchema = z.union([
  healthSchema,
  healthSchema.extend({ protocolVersion: z.literal(3) }).strict(),
])
export type EngineHealth = z.infer<typeof displayHealthSchema>
export interface SafeError {
  code: string
  messageKey: string
  params: Record<string, unknown>
  retryable: boolean
}
export const internalError: SafeError = {
  code: 'INTERNAL_ERROR',
  messageKey: 'engine.internal',
  params: {},
  retryable: false,
}
export function safeError(value: unknown): SafeError {
  return validateV2('error', value)
    ? structuredClone(value as SafeError)
    : structuredClone(internalError)
}
export function safeBusiness3Error(value: unknown): SafeError {
  return validateBusiness3('error', value)
    ? structuredClone(value as SafeError)
    : structuredClone(internalError)
}
export function safeStartupError(value: unknown): SafeError {
  return validateStartupError(value)
    ? structuredClone(value as SafeError)
    : structuredClone(internalError)
}
// For already-authorized display DTOs only. This does not authenticate provenance.
export function safeDisplayError(value: unknown): SafeError {
  return validateV2('error', value) ||
    validateBusiness3('error', value) ||
    validateStartupError(value)
    ? structuredClone(value as SafeError)
    : structuredClone(internalError)
}
export type BridgeResult<T> = { ok: true; data: T } | { ok: false; error: SafeError }
export type HealthResult = BridgeResult<EngineHealth>
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
const generationSchema = z.number().int().min(0).max(Number.MAX_SAFE_INTEGER)
const jobViewSchema = z.custom<JobView>((value) => validateV2('job', value))
const projectViewSchema = z.custom<ProjectView>(
  (value) =>
    validateV2('result_project.get', value) || validateBusiness3('result_project.get', value),
)
const taskViewSchema = z
  .object({
    generation: generationSchema,
    project: projectViewSchema.nullable(),
    jobs: z.array(jobViewSchema).max(16),
  })
  .strict()
  .refine(
    (view) =>
      new Set(view.jobs.map((job) => job.jobId)).size === view.jobs.length &&
      view.jobs.every((job) => job.projectId === view.project?.projectId),
  )
const taskUpdateSchema = z.union([
  z
    .object({
      kind: z.literal('job'),
      generation: generationSchema,
      job: jobViewSchema,
      progress: z.custom<ProgressView>((value) => validateV2('progress', value)).optional(),
    })
    .strict(),
  z
    .object({ kind: z.literal('restored'), generation: generationSchema, view: taskViewSchema })
    .strict()
    .refine((update) => update.view.generation === update.generation),
  z
    .object({
      kind: z.literal('connection'),
      generation: generationSchema,
      projectId: z.string().uuid(),
      state: z.enum(['reconnecting', 'offline']),
      attempt: z.number().int().min(0).max(3),
      error: z.custom<SafeError>(
        (value) =>
          validateV2('error', value) ||
          validateBusiness3('error', value) ||
          validateStartupError(value),
      ),
    })
    .strict()
    .refine((update) => update.state !== 'offline' || update.attempt === 3),
])
export function isTaskUpdate(value: unknown): value is TaskUpdate {
  return taskUpdateSchema.safeParse(value).success
}
export interface JobListOptions {
  filter: 'all' | 'active' | 'terminal'
  pageSize: number
  listSnapshotId: string | null
  cursor: string | null
}
export interface ResultPageOptions {
  resultId: string
  pageSize: number
  cursor: string | null
}
// Display DTOs for already-validated result payloads. Runtime bounds and authority remain
// with the profile-selected canonical validators and the original request binding.
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
// Renderer receives named operations only; project authority comes from main, never a supplied UUID.
export interface DesktopBridge
  extends
    QueryConsumerBridge,
    MainlineProjectBridge,
    LibraryLocationBridge,
    ProjectCheckpointBridge,
    LearningLedgerBridge {
  getEngineHealth(): Promise<HealthResult>
  restoreTasks(): Promise<BridgeResult<TaskView>>
  getActiveProject(): Promise<BridgeResult<ProjectView | null>>
  getJob(jobId: string): Promise<BridgeResult<JobView>>
  listJobs(options: JobListOptions): Promise<BridgeResult<Record<string, unknown>>>
  cancelJob(jobId: string): Promise<BridgeResult<Record<string, unknown>>>
  subscribeJob(jobId: string): Promise<BridgeResult<JobView>>
  unsubscribeJob(jobId: string, generation: number): Promise<BridgeResult<null>>
  getResult(resultId: string): Promise<BridgeResult<ResultMetadataDTO>>
  getResultPage(options: ResultPageOptions): Promise<BridgeResult<ResultPageDTO>>
  getOperation(operationId: string): Promise<BridgeResult<Record<string, unknown> | null>>
  onTaskUpdate(listener: (update: TaskUpdate) => void): () => void
}

/** Main/preload-only finite channel association; no generic invoke is exposed to renderer. */
export type DesktopIpcMap = {
  'project:checkpoint-list': {
    args: [args: Parameters<ProjectCheckpointBridge['listProjectCheckpoints']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['listProjectCheckpoints']>>
  }
  'project:checkpoint-create': {
    args: [args: Parameters<ProjectCheckpointBridge['createProjectCheckpoint']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['createProjectCheckpoint']>>
  }
  'project:learning-read': {
    args: [args: Parameters<LearningLedgerBridge['getProjectLearningState']>[0]]
    result: Awaited<ReturnType<LearningLedgerBridge['getProjectLearningState']>>
  }
  'project:learning-attempt-start': {
    args: [args: Parameters<LearningLedgerBridge['startLearningAttempt']>[0]]
    result: Awaited<ReturnType<LearningLedgerBridge['startLearningAttempt']>>
  }
  'project:learning-hint-record': {
    args: [args: Parameters<LearningLedgerBridge['recordLearningHint']>[0]]
    result: Awaited<ReturnType<LearningLedgerBridge['recordLearningHint']>>
  }
  'project:learning-observation-record': {
    args: [args: Parameters<LearningLedgerBridge['recordLearningObservation']>[0]]
    result: Awaited<ReturnType<LearningLedgerBridge['recordLearningObservation']>>
  }
  'project:learning-task-check': {
    args: [args: Parameters<LearningLedgerBridge['checkLearningTask']>[0]]
    result: Awaited<ReturnType<LearningLedgerBridge['checkLearningTask']>>
  }
  'project:restore-pending': {
    args: []
    result: Awaited<ReturnType<ProjectCheckpointBridge['getPendingProjectRestoreOperations']>>
  }
  'project:restore-preview': {
    args: [args: Parameters<ProjectCheckpointBridge['previewProjectRestore']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['previewProjectRestore']>>
  }
  'project:restore-page': {
    args: [args: Parameters<ProjectCheckpointBridge['getProjectRestorePage']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['getProjectRestorePage']>>
  }
  'project:restore-confirm': {
    args: [args: Parameters<ProjectCheckpointBridge['confirmProjectRestore']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['confirmProjectRestore']>>
  }
  'project:restore-apply': {
    args: [args: Parameters<ProjectCheckpointBridge['restoreProject']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['restoreProject']>>
  }
  'project:restore-operation': {
    args: [args: Parameters<ProjectCheckpointBridge['getProjectRestoreOperation']>[0]]
    result: Awaited<ReturnType<ProjectCheckpointBridge['getProjectRestoreOperation']>>
  }
  'project:management-pending': {
    args: []
    result: Awaited<ReturnType<ProjectManagementBridge['getPendingProjectManagementOperations']>>
  }
  'project:management-catalog': {
    args: [args: Parameters<ProjectManagementBridge['getProjectManagementCatalog']>[0]]
    result: Awaited<ReturnType<ProjectManagementBridge['getProjectManagementCatalog']>>
  }
  'project:management-state': {
    args: []
    result: Awaited<ReturnType<ProjectManagementBridge['getProjectManagementState']>>
  }
  'project:management-preview': {
    args: [args: Parameters<ProjectManagementBridge['previewProjectManagement']>[0]]
    result: Awaited<ReturnType<ProjectManagementBridge['previewProjectManagement']>>
  }
  'project:management-confirm': {
    args: [args: Parameters<ProjectManagementBridge['confirmProjectManagement']>[0]]
    result: Awaited<ReturnType<ProjectManagementBridge['confirmProjectManagement']>>
  }
  'project:management-apply': {
    args: [args: Parameters<ProjectManagementBridge['applyProjectManagement']>[0]]
    result: Awaited<ReturnType<ProjectManagementBridge['applyProjectManagement']>>
  }
  'project:management-operation': {
    args: [args: Parameters<ProjectManagementBridge['getProjectManagementOperation']>[0]]
    result: Awaited<ReturnType<ProjectManagementBridge['getProjectManagementOperation']>>
  }
  'library:location': {
    args: []
    result: Awaited<ReturnType<LibraryLocationBridge['getLibraryLocation']>>
  }
  'library:choose': {
    args: [args: Parameters<LibraryLocationBridge['chooseLibraryLocation']>[0]]
    result: Awaited<ReturnType<LibraryLocationBridge['chooseLibraryLocation']>>
  }
  'library:workspace': {
    args: [args: Parameters<LibraryLocationBridge['reportLibraryWorkspace']>[0]]
    result: Awaited<ReturnType<LibraryLocationBridge['reportLibraryWorkspace']>>
  }
  'library:switch': {
    args: [args: Parameters<LibraryLocationBridge['switchLibraryLocation']>[0]]
    result: Awaited<ReturnType<LibraryLocationBridge['switchLibraryLocation']>>
  }
  'project:draft-save': {
    args: [args: Parameters<MainlineProjectBridge['saveProjectDraft']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['saveProjectDraft']>>
  }
  'project:catalog': {
    args: [args: Parameters<MainlineProjectBridge['getProjectCatalog']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['getProjectCatalog']>>
  }
  'project:create-blank': {
    args: [args: Parameters<MainlineProjectBridge['createBlankProject']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['createBlankProject']>>
  }
  'project:create-example': {
    args: [args: Parameters<MainlineProjectBridge['createExampleProject']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['createExampleProject']>>
  }
  'project:open': {
    args: [args: Parameters<MainlineProjectBridge['openProject']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['openProject']>>
  }
  'project:read': {
    args: [args: Parameters<MainlineProjectBridge['readProject']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['readProject']>>
  }
  'project:ownership-detail': {
    args: [args: Parameters<MainlineProjectBridge['getOwnershipConflictDetailPage']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['getOwnershipConflictDetailPage']>>
  }
  'project:changeset-preview': {
    args: [args: Parameters<MainlineProjectBridge['previewProjectChangeset']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['previewProjectChangeset']>>
  }
  'project:changeset-diff-page': {
    args: [args: Parameters<MainlineProjectBridge['getProjectDiffPage']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['getProjectDiffPage']>>
  }
  'project:changeset-confirm': {
    args: [args: Parameters<MainlineProjectBridge['confirmProjectChangeset']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['confirmProjectChangeset']>>
  }
  'project:changeset-commit': {
    args: [args: Parameters<MainlineProjectBridge['commitProjectChangeSet']>[0]]
    result: Awaited<ReturnType<MainlineProjectBridge['commitProjectChangeSet']>>
  }
  'query:definition-base': {
    args: []
    result: Awaited<ReturnType<QueryConsumerBridge['getQueryDefinitionBase']>>
  }
  'query:definition-load': {
    args: [args: Parameters<QueryConsumerBridge['loadQueryDefinition']>[0]]
    result: Awaited<ReturnType<QueryConsumerBridge['loadQueryDefinition']>>
  }
  'query:execute-saved': {
    args: [args: QueryExecuteArgs]
    result: Awaited<ReturnType<QueryConsumerBridge['executeSavedQuery']>>
  }
  'query:result-describe': {
    args: [args: { resultId: string }]
    result: Awaited<ReturnType<QueryConsumerBridge['getQueryResultDescriptor']>>
  }
  'query:result-text-page': {
    args: [args: Parameters<QueryConsumerBridge['getQueryExecutedTextPage']>[0]]
    result: Awaited<ReturnType<QueryConsumerBridge['getQueryExecutedTextPage']>>
  }
  'query:result-rows-page': {
    args: [args: Parameters<QueryConsumerBridge['getQueryRowsPage']>[0]]
    result: Awaited<ReturnType<QueryConsumerBridge['getQueryRowsPage']>>
  }
  'engine:health': { args: []; result: Awaited<ReturnType<DesktopBridge['getEngineHealth']>> }
  'tasks:restore': { args: []; result: Awaited<ReturnType<DesktopBridge['restoreTasks']>> }
  'project:active': { args: []; result: Awaited<ReturnType<DesktopBridge['getActiveProject']>> }
  'job:get': { args: [jobId: string]; result: Awaited<ReturnType<DesktopBridge['getJob']>> }
  'job:list': {
    args: [options: JobListOptions]
    result: Awaited<ReturnType<DesktopBridge['listJobs']>>
  }
  'job:cancel': { args: [jobId: string]; result: Awaited<ReturnType<DesktopBridge['cancelJob']>> }
  'job:subscribe': {
    args: [jobId: string]
    result: Awaited<ReturnType<DesktopBridge['subscribeJob']>>
  }
  'job:unsubscribe': {
    args: [request: { jobId: string; generation: number }]
    result: Awaited<ReturnType<DesktopBridge['unsubscribeJob']>>
  }
  'result:get': {
    args: [resultId: string]
    result: Awaited<ReturnType<DesktopBridge['getResult']>>
  }
  'result:page': {
    args: [options: ResultPageOptions]
    result: Awaited<ReturnType<DesktopBridge['getResultPage']>>
  }
  'operation:get': {
    args: [operationId: string]
    result: Awaited<ReturnType<DesktopBridge['getOperation']>>
  }
}
export type DesktopIpcChannel = keyof DesktopIpcMap
export type DesktopIpcHandlers = {
  [Channel in DesktopIpcChannel]: (
    ...args: DesktopIpcMap[Channel]['args']
  ) => Promise<DesktopIpcMap[Channel]['result']>
}

/** Immutable ChangeSet transport DTOs; none of these values grants confirmation authority. */
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

/** Reassemble the entire frozen document. Completion is explicit, never a null cursor. */
export async function reassembleChangeSetDocument(
  expected: { projectId: string; previewHash: string; manifest: ChangeSetManifest },
  pages: readonly ChangeSetPage[],
): Promise<unknown[]> {
  const invalid = (): never => {
    throw new Error('INVALID_CHANGESET_DOCUMENT')
  }
  // Capture data-only own properties once, without executing accessors/toJSON.
  // Reflection on a hostile Proxy is outside this data-only input contract;
  // every captured value is nevertheless privately bounded before allocation.
  let nodes = 0
  let stringCharacters = 0
  const capture = (value: unknown, depth = 0): unknown => {
    if (++nodes > 16384 || depth > 8) return invalid()
    if (value === null || typeof value === 'boolean') return value
    if (typeof value === 'number') return Number.isFinite(value) ? value : invalid()
    if (typeof value === 'string') {
      stringCharacters += value.length
      if (value.length > 43692 || stringCharacters > 512 * (43692 + 1024)) return invalid()
      return value
    }
    if (!value || typeof value !== 'object') return invalid()
    const prototype = Object.getPrototypeOf(value)
    if (Array.isArray(value)) {
      if (prototype !== Array.prototype) return invalid()
      const lengthDescriptor = Object.getOwnPropertyDescriptor(value, 'length')
      const length = lengthDescriptor?.value as unknown
      if (!Number.isSafeInteger(length) || (length as number) < 0 || (length as number) > 512)
        return invalid()
      let enumerable = 0
      for (const key in value) {
        if (!Object.hasOwn(value, key) || ++enumerable > (length as number)) return invalid()
      }
      const keys = Reflect.ownKeys(value)
      if (keys.length !== (length as number) + 1 || keys.some((key) => typeof key !== 'string'))
        return invalid()
      const output: unknown[] = []
      for (let index = 0; index < (length as number); index++) {
        const descriptor = Object.getOwnPropertyDescriptor(value, String(index))
        if (!descriptor || !Object.hasOwn(descriptor, 'value') || !descriptor.enumerable)
          return invalid()
        output.push(capture(descriptor.value, depth + 1))
      }
      return output
    }
    if (prototype !== Object.prototype && prototype !== null) return invalid()
    let enumerable = 0
    for (const key in value) {
      if (!Object.hasOwn(value, key) || ++enumerable > 8) return invalid()
    }
    const keys = Reflect.ownKeys(value)
    if (keys.length > 8 || keys.some((key) => typeof key !== 'string' || key.length > 64))
      return invalid()
    const output: Record<string, unknown> = Object.create(null)
    for (const key of keys) {
      const descriptor = Object.getOwnPropertyDescriptor(value, key)
      if (!descriptor || !Object.hasOwn(descriptor, 'value') || !descriptor.enumerable)
        return invalid()
      output[key as string] = capture(descriptor.value, depth + 1)
    }
    return output
  }
  let privateInput: { expected: typeof expected; pages: ChangeSetPage[] }
  try {
    // Structural callers may pass the entire ready/conflict DTO. Capture only
    // the three required binding fields by descriptor, never invoking extras.
    if (
      !expected ||
      typeof expected !== 'object' ||
      Array.isArray(expected) ||
      ![Object.prototype, null].includes(Object.getPrototypeOf(expected))
    )
      return invalid()
    const projection: Record<string, unknown> = Object.create(null)
    for (const field of ['projectId', 'previewHash', 'manifest']) {
      const descriptor = Object.getOwnPropertyDescriptor(expected, field)
      if (!descriptor || !Object.hasOwn(descriptor, 'value') || !descriptor.enumerable)
        return invalid()
      projection[field] = descriptor.value
    }
    privateInput = capture({ expected: projection, pages }) as typeof privateInput
  } catch {
    return invalid()
  }
  const binding = privateInput.expected
  const capturedPages = privateInput.pages
  if (
    !binding ||
    !validateV2('id', binding.projectId) ||
    !validateV2('hash', binding.previewHash) ||
    !validateV2('changeSetManifest', binding.manifest) ||
    !Array.isArray(capturedPages) ||
    capturedPages.length < 1 ||
    capturedPages.length > 512
  )
    return invalid()
  const manifest = binding.manifest
  // From this point onward, budget checks and async work use only private data.
  let suppliedSegments = 0
  let suppliedBytes = 0
  for (const page of capturedPages) {
    if (!validateV2('changeSetPage', page)) return invalid()
    suppliedSegments += page.segments.length
    for (const part of page.segments) suppliedBytes += part.rawByteLength
    if (suppliedSegments > manifest.segmentCount || suppliedBytes > manifest.totalBytes)
      return invalid()
  }
  if (suppliedSegments !== manifest.segmentCount || suppliedBytes !== manifest.totalBytes)
    return invalid()
  const bytes = new Uint8Array(manifest.totalBytes)
  const sha256 = async (value: Uint8Array): Promise<string> => {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', Uint8Array.from(value))
    return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('')
  }
  let next = 0
  let complete = false
  for (const page of capturedPages) {
    if (
      complete ||
      !validateV2('changeSetPage', page) ||
      page.projectId !== binding.projectId ||
      page.previewHash !== binding.previewHash ||
      page.documentKind !== manifest.documentKind ||
      page.documentHash !== manifest.documentHash ||
      (!page.complete && page.segments.length === 0)
    )
      return invalid()
    for (const segment of page.segments) {
      const descriptor = manifest.segments[next]
      if (
        !descriptor ||
        segment.ordinal !== descriptor.ordinal ||
        segment.byteOffset !== descriptor.byteOffset ||
        segment.rawByteLength !== descriptor.rawByteLength ||
        segment.sha256 !== descriptor.sha256
      )
        return invalid()
      let binary: string
      try {
        binary = atob(segment.dataBase64)
      } catch {
        return invalid()
      }
      if (btoa(binary) !== segment.dataBase64 || binary.length !== descriptor.rawByteLength)
        return invalid()
      const part = Uint8Array.from(binary, (character) => character.charCodeAt(0))
      if ((await sha256(part)) !== descriptor.sha256) return invalid()
      bytes.set(part, descriptor.byteOffset)
      next++
    }
    if (page.complete !== (next === manifest.segmentCount)) return invalid()
    complete = page.complete
  }
  if (
    !complete ||
    next !== manifest.segmentCount ||
    (await sha256(bytes)) !== manifest.documentHash
  )
    return invalid()
  let value: unknown
  try {
    value = JSON.parse(new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes))
  } catch {
    return invalid()
  }
  // JSON.parse can produce nonfinite numeric values and escaped lone surrogates.
  const data = (v: unknown): boolean => {
    if (typeof v === 'number') return Number.isFinite(v)
    if (typeof v === 'string') {
      for (const character of v) {
        const codepoint = character.codePointAt(0)!
        if (codepoint >= 0xd800 && codepoint <= 0xdfff) return false
      }
      return true
    }
    if (Array.isArray(v)) return v.every(data)
    if (v && typeof v === 'object')
      return Object.entries(v).every(([key, item]) => data(key) && data(item))
    return v === null || typeof v === 'boolean'
  }
  return Array.isArray(value) && data(value) ? value : invalid()
}

/** Query consumer contract, source ticket 2026-10-23. Save/confirm is not registered. */
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
export interface OntologyEntityMetadataDTO {
  entityMetadataVersion: 1
  entities: Record<
    string,
    {
      identifier: string
      labels: Array<[string, string]>
      definitions: Array<[string, string]>
      synonyms: string[]
      examples: string[]
    }
  >
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
          entityMetadata?: OntologyEntityMetadataDTO
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
export interface MainlineProjectBridge
  extends ProjectManagementBridge, ProjectCheckpointBridge, LearningLedgerBridge {
  getOwnershipConflictDetailPage(
    args: OwnershipDetailArgs,
  ): Promise<BridgeResult<OwnershipDetailPage>>
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

export type OwnershipDetailArgs =
  | { detailRef: string; documentHash: null; startOrdinal: 0; pageSize: number }
  | { detailRef: string; documentHash: string; startOrdinal: number; pageSize: number }
export type OwnershipLocator = {
  id: string
  owner: string | null
  sourceRow: string | null
  slot: { subject: string; predicate: string }
}
export type OwnershipDetailDocument =
  | {
      ownershipDetailVersion: 1
      kind: 'manual-ownership-conflict'
      stage: 'preview'
      projectId: string
      sourceBaseRevision: number
      reason: 'reservedIdentity' | 'sameStatement' | 'singleSlot'
      existing: OwnershipLocator
      incoming: OwnershipLocator
    }
  | {
      ownershipDetailVersion: 1
      kind: 'single-declaration-conflict'
      stage: 'preview'
      projectId: string
      sourceBaseRevision: number
      reason: 'singleDeclaration'
      declaration: { layer: 'ontology'; id: string; predicate: string }
      slot: { subject: string; predicate: string }
      existing: [Omit<OwnershipLocator, 'slot'>, Omit<OwnershipLocator, 'slot'>]
    }
export type OwnershipDetailPage = {
  detailReadVersion: 1
  projectId: string
  detailRef: string
  manifest: {
    documentKind: 'ownership-conflict'
    documentHash: string
    totalBytes: number
    segmentCount: number
  }
  startOrdinal: number
  segments: ChangeSetPage['segments']
  nextOrdinal: number | null
  complete: boolean
}

/** First/last page receipt is not completeness: verify a private, complete byte stream. */
export async function reassembleOwnershipDetail(
  expected: { projectId: string; detailRef: string },
  pages: readonly OwnershipDetailPage[],
): Promise<OwnershipDetailDocument> {
  const invalid = (): never => {
    throw new Error('INVALID_OWNERSHIP_DETAIL')
  }
  let nodes = 0,
    characters = 0
  const capture = (value: unknown, depth = 0): unknown => {
    if (++nodes > 16384 || depth > 8) return invalid()
    if (value === null || typeof value === 'boolean') return value
    if (typeof value === 'number') return Number.isFinite(value) ? value : invalid()
    if (typeof value === 'string') {
      characters += value.length
      if (value.length > 43692 || characters > 512 * (43692 + 1024)) return invalid()
      return value
    }
    if (
      !value ||
      typeof value !== 'object' ||
      ![Object.prototype, null, Array.prototype].includes(Object.getPrototypeOf(value))
    )
      return invalid()
    const keys = Reflect.ownKeys(value)
    if (keys.length > (Array.isArray(value) ? 513 : 10) || keys.some((k) => typeof k !== 'string'))
      return invalid()
    if (Array.isArray(value)) {
      const length = Object.getOwnPropertyDescriptor(value, 'length')?.value
      if (!Number.isSafeInteger(length) || length < 0 || length > 512 || keys.length !== length + 1)
        return invalid()
      const result: unknown[] = []
      for (let i = 0; i < length; i++) {
        const d = Object.getOwnPropertyDescriptor(value, String(i))
        if (!d || !Object.hasOwn(d, 'value') || !d.enumerable) return invalid()
        result.push(capture(d.value, depth + 1))
      }
      return result
    }
    const result: Record<string, unknown> = Object.create(null)
    for (const key of keys as string[]) {
      const d = Object.getOwnPropertyDescriptor(value, key)
      if (key.length > 64 || !d || !Object.hasOwn(d, 'value') || !d.enumerable) return invalid()
      result[key] = capture(d.value, depth + 1)
    }
    return result
  }
  const input = capture({ expected, pages }) as {
    expected: typeof expected
    pages: OwnershipDetailPage[]
  }
  if (
    !validateV2('id', input.expected.projectId) ||
    !validateV2('id', input.expected.detailRef) ||
    input.pages.length < 1
  )
    return invalid()
  const first = input.pages[0]!
  if (!validateBusiness3('result_project.ownership.detail', first)) return invalid()
  let ordinal = 0
  for (const page of input.pages) {
    if (
      !matchesOwnershipDetail(
        {
          ...input.expected,
          documentHash: ordinal === 0 ? null : first.manifest.documentHash,
          startOrdinal: ordinal,
          pageSize: 64,
        },
        page,
      ) ||
      page.manifest.totalBytes !== first.manifest.totalBytes ||
      page.manifest.segmentCount !== first.manifest.segmentCount
    )
      return invalid()
    ordinal += page.segments.length
  }
  if (ordinal !== first.manifest.segmentCount || !input.pages.at(-1)!.complete) return invalid()
  // All declared totals were checked before allocation; raw binary, decoded
  // text and typed result remain bounded by the original 16MiB document policy.
  const bytes = new Uint8Array(first.manifest.totalBytes)
  for (const page of input.pages)
    for (const part of page.segments) {
      const raw = Uint8Array.from(atob(part.dataBase64), (c) => c.charCodeAt(0))
      bytes.set(raw, part.byteOffset)
    }
  const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes)
  const hex = Array.from(new Uint8Array(hash), (n) => n.toString(16).padStart(2, '0')).join('')
  if (hex !== first.manifest.documentHash) return invalid()
  let document: unknown
  try {
    document = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes))
  } catch {
    return invalid()
  }
  if (
    !validateBusiness3('ownershipDetailDocument', document) ||
    (document as OwnershipDetailDocument).projectId !== input.expected.projectId
  )
    return invalid()
  return document as OwnershipDetailDocument
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
