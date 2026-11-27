import type { BridgeResult } from './index'

/** T01 learning ledger over the named business3 bridge. Hints unlock only
 *  after their assistance event is persisted; unrevealed levels never leave
 *  the engine, and downstream tasks without an approved tool stay
 *  "pending-dependency" instead of fabricating a pass. */
export type LearningTaskStatus =
  | 'not-checked'
  | 'passed'
  | 'needs-repair'
  | 'failed'
  | 'tool-not-successful'
  | 'missing-evidence'
  | 'pending-dependency'
  | 'rerun-required'
  | 'stale'

export type LearningAssistance =
  'independent' | 'partial-hints' | 'full-demonstration' | 'agent-full-assistance'

export type LearningHintDTO = { level: 1 | 2 | 3 | 4; kind: string; text: string }

export type LearningFeedbackDTO = {
  status: Exclude<LearningTaskStatus, 'stale'>
  completed: string[]
  repairs: string[]
  suggestions: string[]
  knowledgePoints: string[]
  evidenceIds: string[]
}

export type LearningObservationDTO =
  | { kind: 'reading-opened'; readingId: string }
  | {
      kind: 'self-assessment-answered'
      readingId: string
      questionIndex: number
      selectedOptionId: string
    }

export type LearningAssessmentOutcomeDTO = { correct: boolean; explanation: string }

export type LearningReadingDTO = {
  id: string
  title: string
  sourceRef: string
  optional: boolean
  summary: string
  content: string
  selfAssessment?: Array<{
    question: string
    options: Array<{ id: string; text: string }>
  }>
}

export type LearningStepDTO = {
  index: number
  kind: string
  scored: boolean
  readingRef: string | null
  title: string
  text: string
}

export type LearningTaskStateDTO = {
  taskId: string
  module: string
  goal: string
  instructions: string
  steps: LearningStepDTO[]
  completionCondition: string
  commonErrors: string[]
  knowledgePoints: string[]
  transfer: boolean
  next: string | null
  checks: string[]
  readings: LearningReadingDTO[]
  attemptCount: number
  withdrawnAttemptCount: number
  attemptId: string | null
  attemptActivationEpoch: number | null
  recordVersion: number | null
  assistance: LearningAssistance
  maxHintLevel: number
  revealedHints: LearningHintDTO[]
  operationComplete: boolean
  independentTransferSuccess: boolean
  checkStatus: LearningTaskStatus
  staleInput: boolean
  lastFeedback: LearningFeedbackDTO | null
  observations: {
    openedReadingIds: string[]
    answeredAssessments: Array<{
      readingId: string
      questionIndex: number
      selectedOptionId: string
      correct: boolean
    }>
  }
  completedGuidedStages: string[]
  guidedStageCheckpointRef: string | null
  rootSnapshotRef: string | null
  boundSnapshotRef: string | null
  boundDomainRevision: number | null
  inputVersion: string
}

export type LearningCourseMetaDTO = {
  courseVersion: string
  glossaryVersion: string
  checksVersion: string
  courseExtensionVersion: string | null
  manifestSha256: string
  case: string
  businessQuestion: string
  firstTask: string
}

export type LearningGlossaryEntryDTO = {
  term: string
  aliases: string[]
  plain: string
  example: string
  technical: string
  boundary: string
}

export type ProjectLearningReadDTO = {
  learningReadVersion: 1
  projectId: string
  domainRevision: number
  domainSnapshotRef: string
  inputVersion: string
  templateRef: string | null
  withdrawnAttemptCount: number
  tasks: LearningTaskStateDTO[]
  courseMeta: LearningCourseMetaDTO
  glossary: LearningGlossaryEntryDTO[]
}

export type LearningRecordViewDTO = {
  attemptId: string
  recordVersion: number
  course: string
  task: string
  activationEpoch: number
  assistance: LearningAssistance
  maxHintLevel: number
  operationComplete: boolean
  independentTransferSuccess: boolean
  checkStatus: LearningTaskStatus
  guidedStageCheckpointRef: string | null
}

export type ProjectLearningAttemptStartDTO = {
  learningAttemptStartVersion: 1
  projectId: string
  operationId: string
  taskId: string
  attemptId: string
  activationEpoch: number
  recordVersion: number
  inputVersion: string
  rootSnapshotRef: string
  operationSequence: number | null
  afterCheckpointRef: string | null
  replayed: boolean
  learningState: LearningTaskStateDTO
}

export type ProjectLearningHintRecordDTO = {
  learningHintRecordVersion: 1
  projectId: string
  operationId: string
  taskId: string
  attemptId: string
  recordVersion: number
  assistanceEventId: string
  level: 1 | 2 | 3 | 4
  revealedHint: LearningHintDTO
  record: LearningRecordViewDTO
  learningState: LearningTaskStateDTO
}

export type ProjectLearningObservationRecordDTO = {
  learningObservationRecordVersion: 1
  projectId: string
  operationId: string
  taskId: string
  attemptId: string
  recordVersion: number
  observation: LearningObservationDTO
  assessmentOutcome: LearningAssessmentOutcomeDTO | null
  learningState: LearningTaskStateDTO
}

export type ProjectLearningTaskCheckDTO = {
  learningTaskCheckVersion: 1
  projectId: string
  operationId: string
  taskId: string
  attemptId: string
  recordVersion: number
  inputVersion: string
  checkStatus: LearningTaskStatus
  operationComplete: boolean
  independentTransferSuccess: boolean
  assistance: LearningAssistance
  feedback: LearningFeedbackDTO | null
  evidenceIds: string[]
  guidedStageCheckpointRef: string | null
  operationSequence: number | null
  afterCheckpointRef: string | null
  learningState: LearningTaskStateDTO
}

export type LearningOriginChoiceDTO = 'asserted' | 'derived'
export type LearningSelectedOriginsDTO =
  | Record<string, LearningOriginChoiceDTO>
  | [LearningOriginChoiceDTO, LearningOriginChoiceDTO]
  | null

export interface LearningLedgerBridge {
  getProjectLearningState(args: {
    projectId: string
  }): Promise<BridgeResult<ProjectLearningReadDTO>>
  startLearningAttempt(args: {
    projectId: string
    operationId: string
    taskId: string
  }): Promise<BridgeResult<ProjectLearningAttemptStartDTO>>
  recordLearningHint(args: {
    projectId: string
    operationId: string
    taskId: string
    level: 1 | 2 | 3 | 4
  }): Promise<BridgeResult<ProjectLearningHintRecordDTO>>
  recordLearningObservation(args: {
    projectId: string
    operationId: string
    taskId: string
    observation: LearningObservationDTO
  }): Promise<BridgeResult<ProjectLearningObservationRecordDTO>>
  checkLearningTask(args: {
    projectId: string
    operationId: string
    taskId: string
    selectedOrigins?: LearningSelectedOriginsDTO
  }): Promise<BridgeResult<ProjectLearningTaskCheckDTO>>
}
