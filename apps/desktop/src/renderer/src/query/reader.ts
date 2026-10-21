import { z } from 'zod'
import {
  internalError,
  isTaskUpdate,
  safeError,
  type DesktopBridge,
  type JobView,
  type SafeError,
  type TaskView,
} from '../../../../../../packages/contracts/src'
import { validateV2 } from '../../../../../../packages/contracts/src/v2'
import {
  acceptPage,
  queryJob,
  queryMetadata,
  sameResult,
  type QueryPageData,
  type QueryResultIdentity,
  type QueryResultMetadata,
} from './results'

// Private presentation input from the owning query-definition adapter. Until
// T00 approves columns/executed text metadata, it must remain unavailable in App.
// Matching identity is required; this never guesses text from the current draft.
export interface QueryPresentation {
  binding: QueryResultIdentity & { order: 'ordinal+rowId:asc' }
  columns: string[]
  executedSparql: string
}
const presentationSchema = z
  .object({
    binding: z.custom<QueryPresentation['binding']>((value) => validateV2('pageBinding', value)),
    columns: z.array(z.string().min(1).max(128)).max(64),
    executedSparql: z.string().trim().min(1).max(65536),
  })
  .strict()

type ReadBridge = Pick<DesktopBridge, 'getResult' | 'getResultPage' | 'getJob' | 'cancelJob'>
export interface QueryReaderSnapshot {
  generation: number
  projectId: string | null
  phase: 'idle' | 'loading' | 'ready' | 'error' | 'disposed'
  result: {
    metadata: QueryResultMetadata
    page: QueryPageData | null
    columns: string[]
    executedSparql: string
  } | null
  job: JobView | null
  cancelRequested: boolean
  error: SafeError | null
}
const invalid = () =>
  safeError({
    code: 'INVALID_REQUEST',
    messageKey: 'protocol.invalidRequest',
    retryable: false,
    params: {},
  })
const terminal = (job: JobView) => ['succeeded', 'failed', 'cancelled'].includes(job.state)

/** Ephemeral renderer reads only. Main/engine remain the sole state authority.
 * No execute, save, cursor issuance, network, persistent cache or implicit retry.
 */
export class QueryResultReader {
  private epoch = 0
  private readToken = 0
  private cancelToken = 0
  private jobToken = 0
  private cancelBusy = false
  private authority: TaskView | null = null
  private presentation: QueryPresentation | null = null
  private pageSize = 100
  private state: QueryReaderSnapshot = {
    generation: -1,
    projectId: null,
    phase: 'idle',
    result: null,
    job: null,
    cancelRequested: false,
    error: null,
  }

  constructor(private readonly bridge: ReadBridge) {}

  snapshot(): QueryReaderSnapshot {
    return structuredClone(this.state)
  }

  bind(view: TaskView): boolean {
    if (
      this.state.phase === 'disposed' ||
      !isTaskUpdate({ kind: 'restored', generation: view?.generation, view }) ||
      view.generation < this.state.generation
    )
      return false
    const before = this.authority?.project
    const changed =
      view.generation !== this.state.generation ||
      before?.projectId !== view.project?.projectId ||
      before?.inputSnapshotId !== view.project?.inputSnapshotId ||
      before?.projectRevision !== view.project?.projectRevision
    this.authority = structuredClone(view)
    if (changed) {
      this.epoch++
      this.readToken++
      this.cancelToken++
      this.jobToken++
      this.cancelBusy = false
      this.presentation = null
      this.state = {
        generation: view.generation,
        projectId: view.project?.projectId ?? null,
        phase: 'idle',
        result: null,
        job: null,
        cancelRequested: false,
        error: null,
      }
    }
    return true
  }

  receiveUpdate(raw: unknown): boolean {
    if (this.state.phase === 'disposed' || !isTaskUpdate(raw)) return false
    if (raw.kind === 'restored') return this.bind(raw.view)
    if (
      raw.generation !== this.state.generation ||
      (raw.kind === 'connection' && raw.projectId !== this.state.projectId)
    )
      return false
    if (raw.kind === 'connection') {
      this.readToken++
      this.cancelToken++
      this.jobToken++
      this.cancelBusy = false
      this.state = { ...this.state, phase: 'error', result: null, error: safeError(raw.error) }
      return true
    }
    if (raw.job.projectId !== this.state.projectId) return false
    const job = queryJob(raw.job, this.state.projectId!)
    if (
      !job ||
      job.jobId !== this.state.job?.jobId ||
      job.stateVersion < this.state.job.stateVersion
    )
      return false
    this.state.job = job
    if (terminal(job)) this.state.cancelRequested = false
    return true
  }

  private alive(epoch: number): boolean {
    return epoch === this.epoch && this.state.phase !== 'disposed'
  }

  private current(epoch: number, token: number): boolean {
    return this.epoch === epoch && this.readToken === token && this.state.phase !== 'disposed'
  }

  private fail(error: unknown, epoch: number, token: number): false {
    if (this.current(epoch, token))
      this.state = { ...this.state, phase: 'error', result: null, error: safeError(error) }
    return false
  }

  async read(raw: QueryPresentation, pageSize = 100): Promise<boolean> {
    const epoch = this.epoch
    const token = ++this.readToken
    const parsed = presentationSchema.safeParse(raw)
    if (
      !this.authority?.project ||
      !parsed.success ||
      !Number.isInteger(pageSize) ||
      pageSize < 1 ||
      pageSize > 200 ||
      parsed.data.binding.projectId !== this.state.projectId ||
      this.state.phase === 'disposed'
    ) {
      return this.fail(invalid(), epoch, token)
    }
    this.presentation = structuredClone(parsed.data)
    this.pageSize = pageSize
    this.state = { ...this.state, phase: 'loading', result: null, error: null }
    return this.fetchPage(null, epoch, token, null)
  }

  async nextPage(cursor: string): Promise<boolean> {
    const result = this.state.result
    if (
      this.state.phase !== 'ready' ||
      !result?.page ||
      !cursor ||
      cursor !== result.page.nextCursor
    )
      return false
    const last = result.page.rows.at(-1) ?? null
    const epoch = this.epoch
    const token = ++this.readToken
    this.state = { ...this.state, phase: 'loading', error: null }
    return this.fetchPage(cursor, epoch, token, last)
  }

  private async fetchPage(
    cursor: string | null,
    epoch: number,
    token: number,
    after: QueryPageData['rows'][number] | null,
  ): Promise<boolean> {
    const presentation = this.presentation
    if (!presentation) return false
    try {
      const response = await this.bridge.getResult(presentation.binding.resultId)
      if (!this.current(epoch, token)) return false
      if (!response.ok) return this.fail(response.error, epoch, token)
      const metadata = queryMetadata(response.data)
      if (
        !sameResult(metadata, presentation.binding) ||
        metadata.projectId !== this.state.projectId
      )
        return this.fail(invalid(), epoch, token)
      if (metadata.payloadStatus === 'evicted') {
        this.state = {
          ...this.state,
          phase: 'ready',
          result: {
            metadata,
            page: null,
            columns: presentation.columns,
            executedSparql: presentation.executedSparql,
          },
          error: null,
        }
        return true
      }
      const responsePage = await this.bridge.getResultPage({
        resultId: metadata.resultId,
        pageSize: this.pageSize,
        cursor,
      })
      if (!this.current(epoch, token)) return false
      if (!responsePage.ok) return this.fail(responsePage.error, epoch, token)
      const page = acceptPage(responsePage.data, metadata, presentation.columns)
      const first = page.rows[0]
      if (
        (after &&
          first &&
          (first.ordinal < after.ordinal ||
            (first.ordinal === after.ordinal && first.rowId <= after.rowId))) ||
        (cursor !== null && page.nextCursor === cursor)
      )
        return this.fail(invalid(), epoch, token)
      this.state = {
        ...this.state,
        phase: 'ready',
        result: {
          metadata,
          page,
          columns: presentation.columns,
          executedSparql: presentation.executedSparql,
        },
        error: null,
      }
      return true
    } catch {
      return this.fail(internalError, epoch, token)
    }
  }

  async refreshJob(jobId: string, minimumStateVersion = 0): Promise<boolean> {
    const epoch = this.epoch
    const token = ++this.jobToken
    const projectId = this.state.projectId
    if (!projectId || this.state.phase === 'disposed') return false
    try {
      const response = await this.bridge.getJob(jobId)
      if (!this.alive(epoch) || token !== this.jobToken) return false
      if (!response.ok) {
        this.state.error = safeError(response.error)
        return false
      }
      const job = queryJob(response.data, projectId)
      if (
        !job ||
        job.jobId !== jobId ||
        job.stateVersion < minimumStateVersion ||
        (this.state.job?.jobId === jobId && job.stateVersion < this.state.job.stateVersion)
      ) {
        this.state.error = invalid()
        return false
      }
      this.state.cancelRequested =
        this.state.job?.jobId === jobId && !terminal(job) && this.state.cancelRequested
      this.state.job = job
      this.state.error = null
      return true
    } catch {
      if (this.alive(epoch) && token === this.jobToken)
        this.state.error = structuredClone(internalError)
      return false
    }
  }

  async cancel(jobId: string): Promise<boolean> {
    const epoch = this.epoch
    const projectId = this.state.projectId
    if (
      !projectId ||
      this.cancelBusy ||
      this.state.phase === 'disposed' ||
      (this.state.job && this.state.job.jobId !== jobId)
    )
      return false
    const token = ++this.cancelToken
    const selection = this.jobToken
    this.cancelBusy = true
    const current = () =>
      epoch === this.epoch && token === this.cancelToken && this.state.phase !== 'disposed'
    try {
      const before = await this.bridge.getJob(jobId)
      if (!current()) return false
      if (!before.ok) {
        this.state.error = safeError(before.error)
        return false
      }
      const job = queryJob(before.data, projectId)
      if (
        !job ||
        job.jobId !== jobId ||
        selection !== this.jobToken ||
        (this.state.job?.jobId === jobId && job.stateVersion < this.state.job.stateVersion)
      ) {
        this.state.error = invalid()
        return false
      }
      this.state.job = job
      this.state.error = null
      if (terminal(job)) {
        this.state.cancelRequested = false
        return true
      }
      const response = await this.bridge.cancelJob(jobId)
      if (!current()) return false
      if (!response.ok) {
        this.state.error = safeError(response.error)
        return false
      }
      if (
        !validateV2('result_job.cancel', response.data) ||
        response.data.jobId !== jobId ||
        Number(response.data.stateVersion) < job.stateVersion
      ) {
        this.state.error = invalid()
        return false
      }
      // Acknowledgement cannot turn this job into cancelled/succeeded in the UI.
      if (selection !== this.jobToken) return false
      this.state.cancelRequested = response.data.disposition !== 'alreadyTerminal'
      return this.refreshJob(jobId, Number(response.data.stateVersion))
    } catch {
      if (current()) this.state.error = structuredClone(internalError)
      return false
    } finally {
      if (current()) this.cancelBusy = false
    }
  }

  dispose(): void {
    this.epoch++
    this.readToken++
    this.cancelToken++
    this.jobToken++
    this.authority = null
    this.presentation = null
    this.cancelBusy = false
    this.state = {
      generation: this.state.generation,
      projectId: null,
      phase: 'disposed',
      result: null,
      job: null,
      cancelRequested: false,
      error: null,
    }
  }
}
