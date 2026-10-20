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
export interface TaskUpdate {
  generation: number
  job: JobView
  progress?: ProgressView
  restoredView?: TaskView
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
const taskUpdateSchema = z
  .object({
    generation: generationSchema,
    job: jobViewSchema,
    progress: z.custom<ProgressView>((value) => validateV2('progress', value)).optional(),
    restoredView: taskViewSchema.optional(),
  })
  .strict()
  .refine(
    (update) =>
      !update.restoredView ||
      (update.restoredView.generation === update.generation &&
        update.restoredView.project?.projectId === update.job.projectId &&
        update.restoredView.jobs.some((job) => job.jobId === update.job.jobId)),
  )
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
// Renderer receives named operations only; project authority comes from main, never a supplied UUID.
export interface DesktopBridge {
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
