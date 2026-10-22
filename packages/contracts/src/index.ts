import { z } from 'zod'
import { validateBusiness3, validateStartupError, validateV2 } from './v2'

export const PROTOCOL_VERSION = 2 as const
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
export interface DesktopBridge {
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
