import { z } from 'zod'
import { validateV2 } from './v2'
import errorCatalog from '../v2/errors.json'

export const PROTOCOL_VERSION = 2 as const
export const healthSchema = z
  .object({
    protocolVersion: z.literal(PROTOCOL_VERSION),
    engineVersion: z.string().min(1).max(128),
    status: z.literal('ok'),
    capabilities: z.array(z.literal('health')).max(1),
  })
  .strict()
export type EngineHealth = z.infer<typeof healthSchema>
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
export const modelGatewayErrorCodeMap = Object.freeze({
  INVALID_INPUT: 'GATEWAY_INVALID_INPUT',
  LOCAL_ONLY: 'GATEWAY_LOCAL_ONLY',
  AUTHORIZATION_REQUIRED: 'GATEWAY_AUTHORIZATION_REQUIRED',
  SCOPE_EXCEEDED: 'GATEWAY_SCOPE_EXCEEDED',
  CONFIGURATION_CHANGED: 'GATEWAY_CONFIGURATION_CHANGED',
  CREDENTIAL_UNAVAILABLE: 'GATEWAY_CREDENTIAL_UNAVAILABLE',
  AUDIT_UNAVAILABLE: 'GATEWAY_AUDIT_UNAVAILABLE',
  REDIRECT_REJECTED: 'GATEWAY_REDIRECT_REJECTED',
  MODEL_UNAVAILABLE: 'GATEWAY_MODEL_UNAVAILABLE',
  RESPONSE_LIMIT: 'GATEWAY_RESPONSE_LIMIT',
} as const)
export type ModelGatewayFailureCode = keyof typeof modelGatewayErrorCodeMap
/** CANCELLED is intentionally absent: project it to the independent outcome branch. */
export function modelGatewayError(code: unknown): SafeError {
  if (typeof code !== 'string' || !Object.hasOwn(modelGatewayErrorCodeMap, code))
    return structuredClone(internalError)
  const publicCode = modelGatewayErrorCodeMap[code as ModelGatewayFailureCode]
  const entry = errorCatalog.codes[publicCode]
  return safeError({ code: publicCode, messageKey: entry.messageKey, params: {}, retryable: false })
}
export function modelInvalidRequestError(): SafeError {
  return safeError({
    code: 'INVALID_REQUEST',
    messageKey: 'protocol.invalidRequest',
    params: { field: 'params' },
    retryable: false,
  })
}
export type BridgeResult<T> = { ok: true; data: T } | { ok: false; error: SafeError }
export type HealthResult = BridgeResult<EngineHealth>
export interface ProjectView {
  projectId: string
  projectRevision: number
  inputSnapshotId: string
  dependencyVector: Record<string, number>
  formatVersion: 2
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
const projectViewSchema = z.custom<ProjectView>((value) => validateV2('result_project.get', value))
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
      error: z.custom<SafeError>((value) => validateV2('error', value)),
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
// Main-owned S3 DTOs. These methods never enter the Python JSONL method registry.
export type ModelPrivacy = 'local' | 'minimal' | 'project'
export type ModelStoredSelection = 'current' | 'historical'
export interface ModelResultMetadata {
  resultId: string
  projectId: string
  jobId: string
  kind: 'query' | 'reasoning' | 'validation' | 'behavior' | 'scenario' | 'test' | 'receipt'
  definitionId: string
  inputSnapshotId: string
  inputProjectRevision: number
  dependencyVector: Record<string, number>
  definitionSetDigests: Record<string, string>
  implementation: {
    executionSemanticsVersion: string
    engineVersion: string
    dependencyLockHash: string
  }
  scope: 'asserted' | 'asserted+derived' | 'scenario'
  parametersHash: string
  state: 'current' | 'stale' | 'historical'
  staleReason: { code: string; dependency: string; before: number; after: number }[]
  payloadStatus: 'available' | 'evicted'
  createdAtMs: number
  historicalSelectionRequired: boolean
}
export interface ModelConfiguration {
  configurationId: string
  configurationVersion: string
  displayName: string
  endpoint: string
  model: string
  credentialState: 'missing' | 'configured' | 'unavailable'
}
export interface ModelWholeResultSelection {
  kind: 'whole-result'
  selectionId: string
  metadata: ModelResultMetadata
  selection: ModelStoredSelection
  bodyHash: string
  rowCount: number
  byteCount: number
}
export interface ModelFieldSelection {
  kind: 'fields'
  selectionId: string
  metadata: ModelResultMetadata
  selection: ModelStoredSelection
  catalogId: string
  fieldIds: string[]
  fields: ModelCatalogField[]
  projectionHash: string
  rowCount: number
  byteCount: number
}
export type ModelSelection = ModelWholeResultSelection | ModelFieldSelection
export interface ModelCatalogField {
  fieldId: string
  label: string
  type: 'string' | 'number' | 'boolean'
  nullable: boolean
  requires: string[]
}
export interface ModelFieldCatalog {
  catalogId: string
  metadata: ModelResultMetadata
  selection: ModelStoredSelection
  fields: ModelCatalogField[]
}
export type ModelInvocationState = 'running' | 'cancelling' | 'completed' | 'cancelled' | 'failed'
export type ModelExplanationOutcome =
  | { invocationId: string; state: 'running' }
  | { invocationId: string; state: 'cancelling' }
  | { invocationId: string; state: 'completed'; text: string }
  | { invocationId: string; state: 'cancelled'; externalEffect: 'unknown' }
  | { invocationId: string; state: 'failed'; error: SafeError }
export interface ModelAccessStatus {
  availability: 'ready' | 'unavailable'
  contextId: string | null
  projectId: string | null
  privacy: ModelPrivacy
  configurations: ModelConfiguration[]
  selections: ModelSelection[]
  invocations: { invocationId: string; state: ModelInvocationState }[]
}
export interface ModelExplanationPreview {
  previewId: string
  configurationId: string
  configurationVersion: string
  endpoint: string
  model: string
  principal: string
  purpose: 'explain'
  privacy: 'minimal' | 'project'
  selections: ModelSelection[]
  authorization: { state: 'required' } | { state: 'reusable'; grantId: string }
}
export interface ModelParamsMap {
  getModelAccessStatus: Record<string, never>
  configureModel: {
    contextId: string
    displayName: string
    endpoint: string
    model: string
  } & (
    | { configurationId: null; configurationVersion: null }
    | { configurationId: string; configurationVersion: string }
  )
  storeModelCredential: {
    contextId: string
    configurationId: string
    configurationVersion: string
    secret: string
  }
  setModelPrivacy: { contextId: string; privacy: ModelPrivacy }
  selectModelResults: {
    contextId: string
    results: { resultId: string; selection: ModelStoredSelection }[]
  }
  getModelFieldCatalog: { contextId: string; resultId: string; selection: ModelStoredSelection }
  selectModelFields: { contextId: string; catalogId: string; fieldIds: string[] }
  previewModelExplanation: {
    contextId: string
    configurationId: string
    selectionIds: string[]
  }
  confirmModelAuthorization: { contextId: string; previewId: string }
  startModelExplanation: {
    contextId: string
    configurationId: string
    grantId: string
    selectionIds: string[]
  }
  getModelExplanationOutcome: { contextId: string; invocationId: string }
  cancelModelExplanation: { contextId: string; invocationId: string }
}
export interface ModelResultMap {
  getModelAccessStatus: ModelAccessStatus
  configureModel: ModelConfiguration
  storeModelCredential: {
    configurationId: string
    configurationVersion: string
    credentialState: 'configured'
  }
  setModelPrivacy: { privacy: ModelPrivacy }
  selectModelResults: { selections: ModelWholeResultSelection[] }
  getModelFieldCatalog: ModelFieldCatalog
  selectModelFields: ModelFieldSelection
  previewModelExplanation: ModelExplanationPreview
  confirmModelAuthorization: { grantId: string; configurationVersion: string }
  startModelExplanation: { invocationId: string; state: 'running' }
  getModelExplanationOutcome: ModelExplanationOutcome
  cancelModelExplanation: Exclude<ModelExplanationOutcome, { state: 'running' }>
}
export type ModelMethod = keyof ModelParamsMap
export type ModelBridge = {
  [M in ModelMethod]: (params: ModelParamsMap[M]) => Promise<BridgeResult<ModelResultMap[M]>>
}
// Renderer receives named operations only; project authority comes from main, never a supplied UUID.
export interface DesktopBridge extends ModelBridge {
  getEngineHealth(): Promise<HealthResult>
  restoreTasks(): Promise<BridgeResult<TaskView>>
  getActiveProject(): Promise<BridgeResult<ProjectView | null>>
  getJob(jobId: string): Promise<BridgeResult<JobView>>
  listJobs(options: JobListOptions): Promise<BridgeResult<Record<string, unknown>>>
  cancelJob(jobId: string): Promise<BridgeResult<Record<string, unknown>>>
  subscribeJob(jobId: string): Promise<BridgeResult<JobView>>
  unsubscribeJob(jobId: string, generation: number): Promise<BridgeResult<null>>
  getResult(resultId: string): Promise<BridgeResult<Record<string, unknown>>>
  getResultPage(options: ResultPageOptions): Promise<BridgeResult<Record<string, unknown>>>
  getOperation(operationId: string): Promise<BridgeResult<Record<string, unknown> | null>>
  onTaskUpdate(listener: (update: TaskUpdate) => void): () => void
}
