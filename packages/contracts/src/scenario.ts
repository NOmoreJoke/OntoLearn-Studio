import type { BridgeResult } from './index'
import type { BehaviorEventEdit, IsolatedRunScope } from './behavior'

export type ScenarioEvent = {
  id: string
  round: number
  sequence: number
  payload: Record<string, null | boolean | string | number>
}

export type ScenarioCapacity =
  | {
      mode: 'direct'
      direct: number
    }
  | {
      mode: 'people'
      people: number
      perPerson: number
    }

export type ScenarioConfiguration = {
  name: string
  maxRounds: number
  capacity: ScenarioCapacity
  events: Array<ScenarioEvent>
  initialEdits: Array<BehaviorEventEdit>
  parameters: Record<string, null | boolean | string | number>
  source: string
  assumptions: Array<string>
  ruleVersion: string
  behaviorVersion: string
}

export type ScenarioIdentity = {
  projectId: string
  scenarioId: string
  projectVersion: number
  inputSnapshotId: string
  inputVersion: string
  engineVersion: string
  dependencyLockHash: string
  ruleVersion: string
  behaviorVersion: string
  configurationDigest: string
  semantics: 'scenario-e2-v1'
}

export type ScenarioMetrics = {
  backlog: number
  completed: number
  openHighAlerts: number
}

export type ScenarioRoundDTO = {
  number: number
  created: Array<string>
  resourceCompleted: Array<string>
  backlog: Array<string>
  metrics: ScenarioMetrics
  inputEvents: Array<string>
  behaviorTrace: Array<{
    eventId: string
    behaviorId: string
    actionIndex: number
  }>
  beforeInference: string
  endInference: string
  checkpointRef: string
}

export type ScenarioSummaryDTO = {
  identity: ScenarioIdentity
  configuration: ScenarioConfiguration
}

export type ScenarioRunEvidenceDTO = {
  maxRounds: number
  capacity: ScenarioCapacity
  source: string
  assumptions: string[]
  parameters: ScenarioConfiguration['parameters']
}

export type ScenarioRunDTO = {
  runId: string
  identity: ScenarioIdentity
  scope: IsolatedRunScope
  status: 'queued' | 'running' | 'cancelling' | 'cancelled' | 'succeeded' | 'failed'
  lastCommittedRound: number
  rounds: Array<ScenarioRoundDTO>
  roundOffset: number
  pendingEvents: Array<string>
  checkpointRef: null | string
  resumeAvailable: boolean
  replayAvailable: boolean
  replayUnavailableReason:
    null | 'missing-input' | 'missing-configuration' | 'unsupported-semantics'
  evidence: ScenarioRunEvidenceDTO
  error:
    null | 'conflict' | 'invalid_input' | 'unavailable' | 'execution_failed' | 'resume_unavailable'
}

export type ScenarioCreateArgs = {
  projectId: string
  projectVersion: number
  inputSnapshotId: string
  operationId: string
  configuration: ScenarioConfiguration
}

export type ScenarioCreateResultDTO = {
  projectId: string
  operationId: string
  scenario: ScenarioSummaryDTO
}

export type ScenarioCopyArgs = {
  projectId: string
  scenarioId: string
  projectVersion: number
  inputSnapshotId: string
  operationId: string
  name: string
}

export type ScenarioCopyResultDTO = {
  projectId: string
  operationId: string
  sourceScenarioId: string
  scenario: ScenarioSummaryDTO
}

export type ScenarioListArgs = {
  projectId: string
  cursor: null | string
  limit: number
}

export type ScenarioListResultDTO = {
  projectId: string
  items: Array<ScenarioSummaryDTO>
  nextCursor: null | string
}

export type ScenarioReadArgs = {
  projectId: string
  scenarioId: string
}

export type ScenarioReadResultDTO = {
  projectId: string
  scenario: ScenarioSummaryDTO
  runs: Array<{
    runId: string
    status: 'queued' | 'running' | 'cancelling' | 'cancelled' | 'succeeded' | 'failed'
    lastCommittedRound: number
  }>
}

export type ScenarioRunReadArgs = {
  projectId: string
  scenarioId: string
  runId: string
  roundOffset: number
  limit: number
}

export type ScenarioRunReadResultDTO = {
  projectId: string
  run: ScenarioRunDTO
}

export type ScenarioRunArgs = {
  projectId: string
  scenarioId: string
  projectVersion: number
  inputSnapshotId: string
  operationId: string
  runId: string
}

export type ScenarioRunResultDTO = {
  projectId: string
  operationId: string
  run: ScenarioRunDTO
  beforeRunCheckpointRef: string
}

export type ScenarioCancelArgs = {
  projectId: string
  scenarioId: string
  runId: string
  operationId: string
}

export type ScenarioCancelResultDTO = {
  projectId: string
  operationId: string
  run: ScenarioRunDTO
}

export type ScenarioResumeArgs = {
  projectId: string
  scenarioId: string
  projectVersion: number
  inputSnapshotId: string
  sourceRunId: string
  checkpointRef: string
  operationId: string
  runId: string
}

export type ScenarioResumeResultDTO = {
  projectId: string
  operationId: string
  sourceRunId: string
  resumedFrom: string
  run: ScenarioRunDTO
  beforeRunCheckpointRef: string
}

export type ScenarioCompareArgs = {
  projectId: string
  runs: Array<{
    scenarioId: string
    runId: string
  }>
  roundOffset: number
  limit: number
}

export type ScenarioCompareResultDTO = {
  projectId: string
  roundOffset: number
  runs: Array<{
    runId: string
    identity: ScenarioIdentity
    status: 'succeeded'
    lastCommittedRound: number
    finalMetrics: null | ScenarioMetrics
    metrics: Array<{
      round: number
      values: ScenarioMetrics
    }>
  }>
}

export type ScenarioRunDeleteArgs = {
  projectId: string
  scenarioId: string
  runId: string
  operationId: string
}

export type ScenarioRunDeleteResultDTO = {
  projectId: string
  scenarioId: string
  runId: string
  operationId: string
  deleted: true
}

export type ScenarioRestoreArgs = {
  projectId: string
  scenarioId: string
  projectVersion: number
  inputSnapshotId: string
  configurationDigest: string
  operationId: string
}

export type ScenarioRestoreResultDTO = {
  projectId: string
  operationId: string
  configurationDigest: string
  scenario: ScenarioSummaryDTO
}

export type RunBeforeCommitArgs = {
  projectId: string
  operationId: string
  domain: 'behavior' | 'scenario'
  baseRevision: number
  label: null | string
}

export type RunBeforeCommitResultDTO = {
  runBeforeCommitVersion: 1
  projectId: string
  operationId: string
  checkpointRef: string
  reason: 'before-run'
  domainRevision: number
}

export interface ScenarioBridge {
  createScenario(
    args: Omit<ScenarioCreateArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioCreateResultDTO>>
  copyScenario(
    args: Omit<ScenarioCopyArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioCopyResultDTO>>
  listScenarios(
    args: Omit<ScenarioListArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioListResultDTO>>
  readScenario(
    args: Omit<ScenarioReadArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioReadResultDTO>>
  readScenarioRun(
    args: Omit<ScenarioRunReadArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioRunReadResultDTO>>
  startScenarioRun(
    args: Omit<ScenarioRunArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioRunResultDTO>>
  cancelScenarioRun(
    args: Omit<ScenarioCancelArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioCancelResultDTO>>
  resumeScenarioRun(
    args: Omit<ScenarioResumeArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioResumeResultDTO>>
  compareScenarioRuns(
    args: Omit<ScenarioCompareArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioCompareResultDTO>>
  deleteScenarioRun(
    args: Omit<ScenarioRunDeleteArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioRunDeleteResultDTO>>
  restoreScenarioBaseline(
    args: Omit<ScenarioRestoreArgs, 'projectId'>,
  ): Promise<BridgeResult<ScenarioRestoreResultDTO>>
}
