import type {
  ScenarioBridge,
  ScenarioConfiguration,
  ScenarioIdentity,
  ScenarioRunDTO,
  ScenarioSummaryDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import { requireWorkspaceReply } from '../ontology/workspace-change'
import type { RunView, ScenarioDraft, ScenarioView } from './presentation'

const capacity = (value: ScenarioConfiguration['capacity']) =>
  value.mode === 'direct' ? value.direct : value.people * value.perPerson

export function scenarioConfiguration(draft: ScenarioDraft): ScenarioConfiguration {
  const inputs = draft.inputs
  if (!inputs) throw new Error('CONFIGURATION_REQUIRED')
  const configuration: ScenarioConfiguration = {
    name: draft.name.trim(),
    maxRounds: draft.maxRounds,
    capacity:
      draft.capacityMode === 'people'
        ? { mode: 'people', people: draft.people!, perPerson: draft.perPerson! }
        : { mode: 'direct', direct: draft.capacity },
    initialEdits: JSON.parse(inputs.initialState),
    events: JSON.parse(inputs.events),
    parameters: JSON.parse(inputs.parameters),
    ruleVersion: inputs.rules.trim(),
    behaviorVersion: inputs.behaviors.trim(),
    source: inputs.source.trim(),
    assumptions: inputs.assumptions
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean),
  }
  if (!validateBusiness3('w4.scenario.config', configuration))
    throw new Error('INVALID_CONFIGURATION')
  return configuration
}
const identityView = (identity: ScenarioIdentity) => ({
  ...identity,
  projectVersion: String(identity.projectVersion),
})
export function scenarioView({ identity, configuration }: ScenarioSummaryDTO): ScenarioView {
  return {
    identity: identityView(identity),
    name: configuration.name,
    maxRounds: configuration.maxRounds,
    capacity: capacity(configuration.capacity),
    source: configuration.source,
    assumptions: configuration.assumptions,
    runs: [],
  }
}
export function scenarioRunView(run: ScenarioRunDTO): RunView {
  return {
    id: run.runId,
    identity: identityView(run.identity),
    status: run.status,
    lastCommittedRound: run.lastCommittedRound,
    rounds: run.rounds.map((round) => ({
      ...round,
      completed: round.resourceCompleted,
      behaviorTrace: round.behaviorTrace.map(
        (trace) => `${trace.eventId} / ${trace.behaviorId} · 动作 ${trace.actionIndex + 1}`,
      ),
    })),
    pendingEvents: run.pendingEvents,
    evidence: {
      ...run.evidence,
      capacity: capacity(run.evidence.capacity),
      parameters: JSON.stringify(run.evidence.parameters),
    },
    replayAvailable: run.replayAvailable,
    replayUnavailableReason: run.replayUnavailableReason ?? undefined,
    errorMessage: run.error
      ? {
          conflict: '检测到冲突，当前轮次未提交。',
          invalid_input: '运行输入无效。',
          unavailable: '运行能力暂不可用。',
          execution_failed: '执行失败，保留已提交轮次。',
          resume_unavailable: '该检查点无法续跑。',
        }[run.error]
      : undefined,
  }
}

type Input = Pick<ScenarioIdentity, 'projectVersion' | 'inputSnapshotId'>
type RunRef = { scenarioId: string; runId: string }
const newOperation = () => crypto.randomUUID()
export const SCENARIO_ROUND_PAGE = 5

export function scenarioServices(bridge: ScenarioBridge, projectId: string, project: Input) {
  function projectReply<T extends { projectId: string }>(data: T) {
    if (data.projectId !== projectId) throw new Error('WRONG_PROJECT')
    return data
  }
  function requireScenario(identity: ScenarioIdentity, scenarioId?: string, input?: Input) {
    if (
      identity.projectId !== projectId ||
      (scenarioId && identity.scenarioId !== scenarioId) ||
      (input &&
        (identity.projectVersion !== input.projectVersion ||
          identity.inputSnapshotId !== input.inputSnapshotId))
    )
      throw new Error('WRONG_SCENARIO')
  }
  const inputOf = (identity: ScenarioIdentity): Input => ({
    projectVersion: identity.projectVersion,
    inputSnapshotId: identity.inputSnapshotId,
  })
  function requireRun(run: ScenarioRunDTO, { scenarioId, runId }: RunRef, input?: Input) {
    requireScenario(run.identity, scenarioId, input)
    if (run.runId !== runId || !validateBusiness3('w4.scenario.run', run))
      throw new Error('WRONG_RUN')
    return run
  }
  function requireOperation(actual: string, expected: string) {
    if (actual !== expected) throw new Error('WRONG_OPERATION')
  }
  return {
    async list(cursor: string | null) {
      const reply = projectReply(
        requireWorkspaceReply(await bridge.listScenarios({ cursor, limit: 12 })),
      )
      if (reply.nextCursor !== null && reply.nextCursor === cursor)
        throw new Error('REPEATED_CURSOR')
      reply.items.forEach((item) => requireScenario(item.identity))
      return reply
    },
    async read(scenarioId: string) {
      const reply = projectReply(requireWorkspaceReply(await bridge.readScenario({ scenarioId })))
      requireScenario(reply.scenario.identity, scenarioId)
      return reply
    },
    async create(draft: ScenarioDraft, source?: ScenarioIdentity) {
      const operationId = newOperation()
      const input = source ? inputOf(source) : project
      if (source) requireScenario(source)
      const reply = projectReply(
        requireWorkspaceReply(
          source
            ? await bridge.copyScenario({
                ...input,
                operationId,
                scenarioId: source.scenarioId,
                name: draft.name.trim(),
              })
            : await bridge.createScenario({
                ...input,
                operationId,
                configuration: scenarioConfiguration(draft),
              }),
        ),
      )
      requireOperation(reply.operationId, operationId)
      requireScenario(reply.scenario.identity, undefined, input)
      if (
        reply.scenario.configuration.name !== draft.name.trim() ||
        (source &&
          (!('sourceScenarioId' in reply) ||
            reply.sourceScenarioId !== source.scenarioId ||
            reply.scenario.identity.scenarioId === source.scenarioId))
      )
        throw new Error('WRONG_SCENARIO')
      return reply.scenario
    },
    async readRun(ref: RunRef, roundOffset: number, limit = SCENARIO_ROUND_PAGE) {
      const reply = projectReply(
        requireWorkspaceReply(await bridge.readScenarioRun({ ...ref, roundOffset, limit })),
      )
      if (reply.run.roundOffset !== roundOffset || reply.run.rounds.length > limit)
        throw new Error('WRONG_ROUND_PAGE')
      return requireRun(reply.run, ref)
    },
    async run(identity: ScenarioIdentity) {
      requireScenario(identity)
      const operationId = newOperation()
      const ref = { scenarioId: identity.scenarioId, runId: newOperation() }
      const input = inputOf(identity)
      const reply = projectReply(
        requireWorkspaceReply(await bridge.startScenarioRun({ ...ref, ...input, operationId })),
      )
      requireOperation(reply.operationId, operationId)
      return requireRun(reply.run, ref, input)
    },
    async cancel(run: ScenarioRunDTO) {
      const ref = { scenarioId: run.identity.scenarioId, runId: run.runId }
      const operationId = newOperation()
      const reply = projectReply(
        requireWorkspaceReply(await bridge.cancelScenarioRun({ ...ref, operationId })),
      )
      requireOperation(reply.operationId, operationId)
      return requireRun(reply.run, ref, inputOf(run.identity))
    },
    async resume(run: ScenarioRunDTO) {
      if (
        !run.resumeAvailable ||
        !run.checkpointRef ||
        (run.status !== 'failed' && run.status !== 'cancelled')
      )
        throw new Error('RESUME_UNAVAILABLE')
      const operationId = newOperation()
      const ref = { scenarioId: run.identity.scenarioId, runId: newOperation() }
      const input = inputOf(run.identity)
      const reply = projectReply(
        requireWorkspaceReply(
          await bridge.resumeScenarioRun({
            ...ref,
            ...input,
            sourceRunId: run.runId,
            checkpointRef: run.checkpointRef,
            operationId,
          }),
        ),
      )
      requireOperation(reply.operationId, operationId)
      if (reply.sourceRunId !== run.runId || reply.resumedFrom !== run.checkpointRef)
        throw new Error('WRONG_CHECKPOINT')
      return requireRun(reply.run, ref, input)
    },
    async compare(runs: RunRef[], roundOffset: number) {
      if (
        runs.length < 2 ||
        runs.length > 10 ||
        new Set(runs.map((run) => run.runId)).size !== runs.length
      )
        throw new Error('INVALID_COMPARISON')
      const reply = projectReply(
        requireWorkspaceReply(
          await bridge.compareScenarioRuns({
            runs,
            roundOffset,
            limit: SCENARIO_ROUND_PAGE,
          }),
        ),
      )
      if (reply.roundOffset !== roundOffset || reply.runs.length !== runs.length)
        throw new Error('WRONG_COMPARISON')
      reply.runs.forEach((run, index) => {
        requireScenario(run.identity, runs[index].scenarioId)
        if (run.runId !== runs[index].runId || run.status !== 'succeeded')
          throw new Error('WRONG_COMPARISON')
      })
      return reply
    },
    async remove(run: ScenarioRunDTO) {
      if (!['failed', 'succeeded', 'cancelled'].includes(run.status)) throw new Error('RUN_ACTIVE')
      const operationId = newOperation()
      const reply = projectReply(
        requireWorkspaceReply(
          await bridge.deleteScenarioRun({
            scenarioId: run.identity.scenarioId,
            runId: run.runId,
            operationId,
          }),
        ),
      )
      requireOperation(reply.operationId, operationId)
      if (
        !reply.deleted ||
        reply.scenarioId !== run.identity.scenarioId ||
        reply.runId !== run.runId
      )
        throw new Error('WRONG_DELETION')
    },
    async restore(identity: ScenarioIdentity) {
      requireScenario(identity)
      const { scenarioId, configurationDigest } = identity
      const operationId = newOperation()
      const input = inputOf(identity)
      const reply = projectReply(
        requireWorkspaceReply(
          await bridge.restoreScenarioBaseline({
            scenarioId,
            configurationDigest,
            ...input,
            operationId,
          }),
        ),
      )
      requireOperation(reply.operationId, operationId)
      requireScenario(reply.scenario.identity, scenarioId, input)
      if (
        reply.configurationDigest !== configurationDigest ||
        reply.scenario.identity.configurationDigest !== configurationDigest
      )
        throw new Error('WRONG_BASELINE')
      return reply.scenario
    },
  }
}
