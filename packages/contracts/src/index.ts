import { z } from 'zod'
import { validateV2 } from './v2'

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
export interface SemanticRunOptions {
  definitionId: string
  scope: 'asserted' | 'asserted+derived'
  inputSelection: 'current' | 'historical'
  inputSnapshotId: string | null
  derivedResultId: string | null
}
export type ReasoningRunOptions = SemanticRunOptions & {
  scope: 'asserted'
  derivedResultId: null
}
// Renderer receives named operations only; project authority comes from main, never a supplied UUID.
export interface DesktopBridge {
  getEngineHealth(): Promise<HealthResult>
  runSavedQuery(options: SemanticRunOptions): Promise<BridgeResult<JobView>>
  runReasoning(options: ReasoningRunOptions): Promise<BridgeResult<JobView>>
  runValidation(options: SemanticRunOptions): Promise<BridgeResult<JobView>>
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
