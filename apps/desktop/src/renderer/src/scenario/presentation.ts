/** Private view values. Public bridge validation belongs to the sole contracts owner. */
export interface ScenarioIdentity {
  projectId: string
  engineVersion: string
  dependencyLockHash: string
  projectVersion: string
  scenarioId: string
  inputVersion: string
  ruleVersion: string
  behaviorVersion: string
  configurationDigest: string
  semantics: string
}

export interface MetricValues {
  backlog: number
  completed: number
  openHighAlerts: number
}

export interface RoundView {
  number: number
  created: readonly string[]
  completed: readonly string[]
  backlog: readonly string[]
  metrics: MetricValues
  inputEvents: readonly string[]
  behaviorTrace: readonly string[]
  beforeInference: string
  endInference: string
}

export interface RunView {
  id: string
  identity: ScenarioIdentity
  status: 'queued' | 'running' | 'cancelling' | 'cancelled' | 'succeeded' | 'failed'
  rounds: readonly RoundView[]
  pendingEvents: readonly string[]
  evidence: {
    source: string
    assumptions: readonly string[]
    maxRounds: number
    capacity: number
    parameters: string
  }
  replayAvailable: boolean
  replayUnavailableReason?: string
  errorMessage?: string
}

export interface ScenarioView {
  identity: ScenarioIdentity
  name: string
  maxRounds: number
  capacity: number
  source: string
  assumptions: readonly string[]
  runs: readonly RunView[]
}

export interface ScenarioInputDraft {
  initialState: string
  events: string
  rules: string
  behaviors: string
  parameters: string
  assumptions: string
  source: string
}

export interface ScenarioDraft {
  name: string
  maxRounds: number
  capacity: number
  capacityMode?: 'direct' | 'people'
  people?: number
  perPerson?: number
  inputs?: ScenarioInputDraft
}

export function validInputs(inputs: ScenarioInputDraft): boolean {
  try {
    for (const value of [inputs.initialState, inputs.rules, inputs.behaviors, inputs.parameters]) {
      const parsed: unknown = JSON.parse(value)
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return false
    }
    const events: unknown = JSON.parse(inputs.events)
    if (!Array.isArray(events)) return false
    const catalog = new Map<string, string>()
    for (const event of events) {
      if (!event || typeof event !== 'object' || Array.isArray(event)) return false
      const item = event as Record<string, unknown>
      if (Object.keys(item).some((key) => !['id', 'round', 'sequence', 'payload'].includes(key)))
        return false
      if (
        typeof item.id !== 'string' ||
        !item.id ||
        !Number.isSafeInteger(item.round) ||
        (item.round as number) < 1 ||
        !Number.isSafeInteger(item.sequence) ||
        (item.sequence as number) < 0
      )
        return false
      if (!item.payload || typeof item.payload !== 'object' || Array.isArray(item.payload))
        return false
      const serialized = JSON.stringify([item.round, item.sequence, item.payload])
      if (catalog.has(item.id) && catalog.get(item.id) !== serialized) return false
      catalog.set(item.id, serialized)
    }
    return true
  } catch {
    return false
  }
}

export const metricDefinitions = [
  ['工单积压', '提交时状态不为“已完成”的工单总数，单位：单。'],
  ['累计完成', '从本次运行开始，累计变为“已完成”的工单数，单位：单。'],
  ['未闭环高危告警', '提交时等级为 High 且告警状态不为 Closed 的告警数，单位：条。'],
] as const

export function sameInput(a: ScenarioIdentity, b: ScenarioIdentity): boolean {
  return (
    a.projectId === b.projectId &&
    a.engineVersion === b.engineVersion &&
    a.dependencyLockHash === b.dependencyLockHash &&
    a.projectVersion === b.projectVersion &&
    a.scenarioId === b.scenarioId &&
    a.inputVersion === b.inputVersion &&
    a.ruleVersion === b.ruleVersion &&
    a.behaviorVersion === b.behaviorVersion &&
    a.configurationDigest === b.configurationDigest &&
    a.semantics === b.semantics
  )
}

export function resultLabel(run: RunView, current: ScenarioIdentity): string {
  const statuses = {
    queued: '排队中',
    running: '运行中',
    cancelling: '取消中',
    cancelled: '已取消 · 历史运行',
    failed: '失败 · 历史运行',
    succeeded: '成功',
  }
  if (run.status !== 'succeeded') return statuses[run.status]
  return sameInput(run.identity, current) ? '当前结果' : '历史结果 · 输入版本已变化'
}

export function completionLabel(run: RunView): string {
  if (run.pendingEvents.length > 0) return `存在未处理事件（${run.pendingEvents.length}）`
  if (run.status === 'succeeded') return '已配置轮次执行完毕，无未处理事件'
  return '运行尚未成功结束'
}

export function validDraft(draft: ScenarioDraft): boolean {
  return (
    draft.name.trim().length > 0 &&
    Number.isSafeInteger(draft.maxRounds) &&
    draft.maxRounds >= 1 &&
    draft.maxRounds <= 1000 &&
    Number.isSafeInteger(draft.capacity) &&
    draft.capacity >= 0 &&
    (draft.capacityMode !== 'people' ||
      (Number.isSafeInteger(draft.people) &&
        draft.people! >= 0 &&
        Number.isSafeInteger(draft.perPerson) &&
        draft.perPerson! >= 0 &&
        Number.isSafeInteger(draft.people! * draft.perPerson!))) &&
    (!draft.inputs || validInputs(draft.inputs))
  )
}

export interface ComparisonRow {
  round: number
  values: readonly (MetricValues | null)[]
}

export function compareRuns(runs: readonly RunView[]): readonly ComparisonRow[] {
  if (runs.length < 2 || runs.some((run) => run.status !== 'succeeded')) return []
  const rounds = [...new Set(runs.flatMap((run) => run.rounds.map((round) => round.number)))].sort(
    (a, b) => a - b,
  )
  return rounds.map((round) => ({
    round,
    values: runs.map((run) => run.rounds.find((item) => item.number === round)?.metrics ?? null),
  }))
}
