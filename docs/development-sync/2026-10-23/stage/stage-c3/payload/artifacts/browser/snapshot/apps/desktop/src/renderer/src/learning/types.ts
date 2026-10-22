/** Private renderer view models; no IPC/Store authority is granted by these values. */
export type HintLevel = 1 | 2 | 3 | 4
export type Assistance =
  'independent' | 'partial-hints' | 'full-demonstration' | 'agent-full-assistance'

export interface TaskContext {
  projectId: string
  taskId: string
  attemptId: string
  inputVersion: string
}

export interface LearningRecordView {
  context: TaskContext
  recordVersion: number
  maxHintLevel: number
  assistance: Assistance
  operationComplete: boolean
  independentTransferSuccess: boolean
  checkStatus: 'not-checked' | 'passed' | 'needs-repair' | 'stale' | 'failed' | 'pending-dependency'
  evidenceIds: readonly string[]
}

export interface CheckFeedbackView {
  context: TaskContext
  record: LearningRecordView
  completed: readonly string[]
  repairs: readonly string[]
  suggestions: readonly string[]
  knowledgePoints: readonly string[]
}

export interface HintReceipt {
  context: TaskContext
  level: HintLevel
  record: LearningRecordView
}

export interface LearningActions {
  /** Persist actual hint provenance via T01 before revealing the requested answer. */
  recordHint?(context: TaskContext, level: HintLevel): Promise<HintReceipt>
  /** Return actual approved tool evidence, never the fixture expected payload. */
  checkTask?(context: TaskContext): Promise<CheckFeedbackView>
  openWorkspace?(taskId: string): void
  exportReport?(context: TaskContext): Promise<{ context: TaskContext; exported: boolean }>
}

export interface CourseTask {
  id: string
  module: string
  goal: string
  instructions: string
  checks: readonly string[]
  completionCondition: string
  next: string | null
  hints: readonly { level: number; kind: string; text: string }[]
  commonErrors: readonly string[]
  transfer: boolean
  knowledgePoints: readonly string[]
}

export interface Course {
  version: string
  case: string
  businessQuestion: string
  firstTask: string
  tasks: readonly CourseTask[]
}

export interface GlossaryEntry {
  term: string
  plain: string
  example: string
  technical: string
}

export interface LearningWorkspaceProps {
  /** Changes on project/window lifecycle. Late replies from older generations are ignored. */
  generation: number
  projectId: string | null
  contexts?: Readonly<Record<string, TaskContext>>
  records?: readonly LearningRecordView[]
  actions?: LearningActions
  initialTaskId?: string
}
