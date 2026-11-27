import type { LearningSelectedOriginsDTO } from '@ontolearn/contracts'

/** Private renderer view models; no IPC/Store authority is granted by these values. */
export type HintLevel = 1 | 2 | 3 | 4
export type Assistance =
  'independent' | 'partial-hints' | 'full-demonstration' | 'agent-full-assistance'

export type CheckStatus =
  | 'not-checked'
  | 'passed'
  | 'needs-repair'
  | 'stale'
  | 'failed'
  | 'pending-dependency'
  | 'rerun-required'
  | 'missing-evidence'
  | 'tool-not-successful'

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
  checkStatus: CheckStatus
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
  checkTask?(
    context: TaskContext,
    selectedOrigins?: LearningSelectedOriginsDTO,
  ): Promise<CheckFeedbackView>
  openWorkspace?(taskId: string): void
  exportReport?(context: TaskContext): Promise<{ context: TaskContext; exported: boolean }>
}

export interface SelfAssessmentOption {
  id: string
  text: string
}

/** Offline self assessment; the answer key is local and never changes a score. */
export interface SelfAssessmentItem {
  question: string
  options: readonly SelfAssessmentOption[]
  answerKey: string
  explanation: string
}

/** Read-only mounted material; it is never a learning task and never scores. */
export interface CourseReading {
  id: string
  title: string
  sourceRef: string
  optional: boolean
  summary: string
  content: string
  selfAssessment?: readonly SelfAssessmentItem[]
}

export interface CourseStep {
  index: number
  kind: string
  scored: boolean
  readingRef: string | null
  title: string
  text: string
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
  steps?: readonly CourseStep[]
  readings?: readonly CourseReading[]
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
  boundary: string
  aliases: readonly string[]
}

export interface LearningWorkspaceProps {
  /** Changes on project/window lifecycle. Late replies from older generations are ignored. */
  generation: number
  projectId: string | null
  contexts?: Readonly<Record<string, TaskContext>>
  records?: readonly LearningRecordView[]
  actions?: LearningActions
  initialTaskId?: string
  onOpenQualityWorkspace?: () => void
}
