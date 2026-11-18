import {
  safeError,
  type LearningAssistance,
  type LearningLedgerBridge,
  type LearningObservationDTO,
  type LearningSelectedOriginsDTO,
  type LearningTaskStateDTO,
  type ProjectLearningReadDTO,
  type ProjectLearningTaskCheckDTO,
  type SafeError,
} from '@ontolearn/contracts'

/** Same persisted-status set the engine treats as a real executed check; only
 *  then can a later domain edit project the derived "stale" view. */
export const EXECUTED_CHECK_STATUSES: ReadonlySet<string> = new Set([
  'passed',
  'needs-repair',
  'failed',
  'tool-not-successful',
  'missing-evidence',
])

/** S0 §6/§8 status mapping; every state carries explicit Chinese text. */
export const mentorStatusTexts: Readonly<Record<string, string>> = {
  'not-checked': '待检查',
  passed: '已通过',
  'needs-repair': '需要修复',
  stale: '已过期 / 需重跑',
  'pending-dependency': '依赖未就绪',
  failed: '检查失败 / 已取消',
  'tool-not-successful': '检查失败 / 已取消',
  'missing-evidence': '检查失败 / 已取消',
  'rerun-required': '检查失败 / 已取消',
}

export const mentorAssistanceTexts: Readonly<Record<LearningAssistance, string>> = {
  independent: '独立完成',
  'partial-hints': '使用部分提示完成',
  'full-demonstration': '使用完整示范完成',
  'agent-full-assistance': 'Agent 完整协助',
}

export function mentorStatusText(task: LearningTaskStateDTO | undefined): string {
  if (!task) return mentorStatusTexts['not-checked']!
  return mentorStatusTexts[task.checkStatus] ?? mentorStatusTexts['not-checked']!
}

export function mentorAssistanceText(task: LearningTaskStateDTO | undefined): string | undefined {
  if (!task) return undefined
  // Attribution text appears once it is meaningful: a completed operation, or
  // durably recorded assistance provenance (any hint/demonstration write). A
  // bare not-checked or needs-repair task without assistance stays unlabeled.
  if (!task.operationComplete && task.maxHintLevel === 0) return undefined
  return mentorAssistanceTexts[task.assistance]
}

/** UI-derived staleness: a persisted check result was bound to the domain
 *  snapshot its engine receipt recorded (task.boundSnapshotRef; falling back
 *  to the learning read's snapshot). When the workspace has advanced past that
 *  binding (ChangeSet commit, restore, …) the result projects as stale locally
 *  — no background RPC; the next explicit check or project open performs the
 *  authoritative engine-side sync. */
export function deriveTaskStale(
  task: LearningTaskStateDTO | undefined,
  currentDomainSnapshotId: string | undefined,
  domainSnapshotRef: string | undefined,
): boolean {
  if (!task || !currentDomainSnapshotId) return false
  if (!EXECUTED_CHECK_STATUSES.has(task.checkStatus)) return false
  const bound = task.boundSnapshotRef ?? domainSnapshotRef
  if (!bound) return false
  return bound !== currentDomainSnapshotId
}

/** Displayed status after applying the derived stale projection locally. */
export function displayedCheckStatus(
  task: LearningTaskStateDTO | undefined,
  currentDomainSnapshotId: string | undefined,
  domainSnapshotRef: string | undefined,
): string {
  if (!task) return mentorStatusTexts['not-checked']!
  if (deriveTaskStale(task, currentDomainSnapshotId, domainSnapshotRef))
    return mentorStatusTexts.stale!
  return mentorStatusText(task)
}

export type LearningControllerState = {
  selectedProjectId?: string
  learning?: ProjectLearningReadDTO
  focusedTaskId: string
  busy: boolean
  error?: SafeError
  notice: string
  lastCheck?: ProjectLearningTaskCheckDTO
  lastAssessment?: {
    readingId: string
    questionIndex: number
    selectedOptionId: string
    correct: boolean
    explanation: string
  }
}

/** Presentation state only, in the shape of ProjectRestoreController. Every
 *  learning mutation goes through the Step 1 named bridge and only through the
 *  serial admission tails in App; nothing here persists to browser storage. */
export class LearningController {
  #state: LearningControllerState = { focusedTaskId: 'business-ontology', busy: false, notice: '' }
  #listeners = new Set<() => void>()
  #closed = false
  constructor(
    private readonly bridge: LearningLedgerBridge,
    private readonly makeId: () => string = () => crypto.randomUUID(),
  ) {}
  getSnapshot = () => this.#state
  subscribe = (listener: () => void) => {
    this.#listeners.add(listener)
    return () => {
      this.#listeners.delete(listener)
    }
  }
  #set(patch: Partial<LearningControllerState>): void {
    if (this.#closed) return
    this.#state = { ...this.#state, ...patch }
    for (const listener of this.#listeners) listener()
  }
  get unresolved(): boolean {
    return this.#state.busy
  }
  /** Synchronous selection change only; never starts a background RPC. */
  select(projectId: string | undefined): void {
    if (this.#state.selectedProjectId === projectId) return
    this.#set({
      selectedProjectId: projectId,
      learning: undefined,
      lastCheck: undefined,
      lastAssessment: undefined,
      notice: '',
      error: undefined,
    })
  }
  focusTask(taskId: string): void {
    if (this.#state.focusedTaskId === taskId) return
    this.#set({ focusedTaskId: taskId, lastCheck: undefined, lastAssessment: undefined })
  }
  /** The single learning read, called only from the serial open/create/restore
   *  admission tail after the checkpoint read has settled. Never throws so an
   *  old test's open flow can not be blocked by a learning failure. */
  async selectAndRefresh(projectId: string): Promise<void> {
    if (this.#closed) return
    this.select(projectId)
    if (!this.#state.busy) {
      this.#set({ busy: true, error: undefined })
      try {
        const response = await this.bridge.getProjectLearningState({ projectId })
        if (this.#closed || this.#state.selectedProjectId !== projectId) return
        if (!response.ok || response.data.projectId !== projectId) {
          // A reply naming another project is never a learning state for this one.
          this.#set({ error: response.ok ? safeError(undefined) : response.error })
        } else {
          this.#set({
            learning: response.data,
            // Keep the focused task stable across re-reads of the same project.
            focusedTaskId: response.data.tasks.some(
              (task) => task.taskId === this.#state.focusedTaskId,
            )
              ? this.#state.focusedTaskId
              : response.data.courseMeta.firstTask,
          })
        }
      } catch {
        if (this.#state.selectedProjectId === projectId) this.#set({ error: safeError(undefined) })
      } finally {
        // Exactly one operation can be in flight; always release its busy flag,
        // even when the selection moved on while the reply was in flight.
        this.#set({ busy: false })
      }
    }
  }
  #currentTask(): LearningTaskStateDTO | undefined {
    return this.#state.learning?.tasks.find((task) => task.taskId === this.#state.focusedTaskId)
  }
  #mergeTaskState(view: LearningTaskStateDTO, projectId: string): void {
    const learning = this.#state.learning
    if (!learning || learning.projectId !== projectId) return
    this.#set({
      learning: {
        ...learning,
        tasks: learning.tasks.map((task) => (task.taskId === view.taskId ? view : task)),
      },
    })
  }
  #guard(projectId: string): boolean {
    return !this.#closed && !this.#state.busy && this.#state.selectedProjectId === projectId
  }
  /** Late replies still land only while this project owns the selection. */
  #accepting(projectId: string): boolean {
    return !this.#closed && this.#state.selectedProjectId === projectId
  }
  /** FR-801 hint: persist the assistance event first; the returned hint text is
   *  rendered only after the durable write succeeded. */
  async requestHint(): Promise<void> {
    const task = this.#currentTask()
    const projectId = this.#state.selectedProjectId
    if (!task || !projectId || !this.#guard(projectId)) return
    if (task.maxHintLevel >= 3) {
      this.#set({
        notice:
          '概念、操作与部分示范提示已全部解锁；如需完整步骤，可点击"查看示范"（将记录为使用完整示范完成）。',
      })
      return
    }
    const level = Math.min(task.maxHintLevel + 1, 3) as 1 | 2 | 3
    this.#set({ busy: true, error: undefined, notice: '' })
    try {
      const response = await this.bridge.recordLearningHint({
        projectId,
        operationId: this.makeId(),
        taskId: task.taskId,
        level,
      })
      if (!this.#accepting(projectId)) return
      if (!response.ok) {
        this.#set({ error: response.error, notice: '提示记录未保存；提示内容不会展示，请重试。' })
        return
      }
      if (response.data.level !== level) {
        this.#set({ notice: '提示记录与请求层级不一致，请重试。' })
        return
      }
      this.#mergeTaskState(response.data.learningState, projectId)
      this.#set({ notice: '' })
    } catch {
      if (this.#accepting(projectId))
        this.#set({ error: safeError(undefined), notice: '提示记录未保存，请重试。' })
    } finally {
      // Exactly one operation can be in flight; always release its busy flag,
      // even when the selection moved on while the reply was in flight.
      this.#set({ busy: false })
    }
  }
  /** FR-801 level-4 full demonstration: the complete answer stays locked until
   *  the assistance event is durably recorded in app_assistance. */
  async requestDemonstration(): Promise<void> {
    const task = this.#currentTask()
    const projectId = this.#state.selectedProjectId
    if (!task || !projectId || !this.#guard(projectId)) return
    this.#set({ busy: true, error: undefined, notice: '' })
    try {
      const response = await this.bridge.recordLearningHint({
        projectId,
        operationId: this.makeId(),
        taskId: task.taskId,
        level: 4,
      })
      if (!this.#accepting(projectId)) return
      if (!response.ok) {
        this.#set({ error: response.error, notice: '完整示范未记录；示范内容保持锁定，请重试。' })
        return
      }
      if (response.data.level !== 4) {
        this.#set({ notice: '示范记录与请求不一致，请重试。' })
        return
      }
      this.#mergeTaskState(response.data.learningState, projectId)
      this.#set({ notice: '' })
    } catch {
      if (this.#accepting(projectId))
        this.#set({ error: safeError(undefined), notice: '完整示范未记录，请重试。' })
    } finally {
      // Exactly one operation can be in flight; always release its busy flag,
      // even when the selection moved on while the reply was in flight.
      this.#set({ busy: false })
    }
  }
  async recordObservation(observation: LearningObservationDTO): Promise<void> {
    const task = this.#currentTask()
    const projectId = this.#state.selectedProjectId
    if (!task || !projectId || !this.#guard(projectId)) return
    this.#set({ busy: true, error: undefined })
    try {
      const response = await this.bridge.recordLearningObservation({
        projectId,
        operationId: this.makeId(),
        taskId: task.taskId,
        observation,
      })
      if (!this.#accepting(projectId)) return
      if (!response.ok) {
        this.#set({ error: response.error })
        return
      }
      if (response.data.observation.kind === 'self-assessment-answered') {
        const outcome = response.data.assessmentOutcome
        this.#set({
          lastAssessment: outcome
            ? {
                readingId: response.data.observation.readingId,
                questionIndex: response.data.observation.questionIndex,
                selectedOptionId: response.data.observation.selectedOptionId,
                correct: outcome.correct,
                explanation: outcome.explanation,
              }
            : undefined,
        })
      }
      this.#mergeTaskState(response.data.learningState, projectId)
    } catch {
      if (this.#accepting(projectId)) this.#set({ error: safeError(undefined) })
    } finally {
      // Exactly one operation can be in flight; always release its busy flag,
      // even when the selection moved on while the reply was in flight.
      this.#set({ busy: false })
    }
  }
  /** The real persisted-evidence check. Returns the engine receipt so the host
   *  can refresh the checkpoint panel when a guided-stage checkpoint appeared. */
  async checkTask(
    selectedOrigins?: LearningSelectedOriginsDTO,
  ): Promise<ProjectLearningTaskCheckDTO | undefined> {
    const task = this.#currentTask()
    const projectId = this.#state.selectedProjectId
    if (!task || !projectId || !this.#guard(projectId)) return undefined
    this.#set({ busy: true, error: undefined, notice: '' })
    try {
      const response = await this.bridge.checkLearningTask({
        projectId,
        operationId: this.makeId(),
        taskId: task.taskId,
        ...(selectedOrigins === undefined ? {} : { selectedOrigins }),
      })
      if (!this.#accepting(projectId)) return undefined
      if (!response.ok) {
        this.#set({ error: response.error, notice: '检查未完成，请重试；当前不会标记为通过。' })
        return undefined
      }
      if (this.#state.focusedTaskId === task.taskId) this.#set({ lastCheck: response.data })
      this.#mergeTaskState(response.data.learningState, projectId)
      return response.data
    } catch {
      if (this.#accepting(projectId))
        this.#set({ error: safeError(undefined), notice: '检查未完成，请重试。' })
      return undefined
    } finally {
      // Exactly one operation can be in flight; always release its busy flag,
      // even when the selection moved on while the reply was in flight.
      this.#set({ busy: false })
    }
  }
  /** Optional redo exercise: a fresh attempt keeps the durable assistance floor. */
  async restartAttempt(): Promise<void> {
    const task = this.#currentTask()
    const projectId = this.#state.selectedProjectId
    if (!task || !projectId || !this.#guard(projectId)) return
    this.#set({ busy: true, error: undefined, notice: '' })
    try {
      const response = await this.bridge.startLearningAttempt({
        projectId,
        operationId: this.makeId(),
        taskId: task.taskId,
      })
      if (!this.#accepting(projectId)) return
      if (!response.ok) {
        this.#set({ error: response.error })
        return
      }
      this.#mergeTaskState(response.data.learningState, projectId)
      this.#set({ notice: '已开始新的任务尝试；此前的辅助记录仍保留。' })
    } catch {
      if (this.#accepting(projectId)) this.#set({ error: safeError(undefined) })
    } finally {
      // Exactly one operation can be in flight; always release its busy flag,
      // even when the selection moved on while the reply was in flight.
      this.#set({ busy: false })
    }
  }
  close(): void {
    this.#closed = true
    for (const listener of this.#listeners) listener()
    this.#listeners.clear()
  }
}
