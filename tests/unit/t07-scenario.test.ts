import { describe, expect, it } from 'vitest'
import {
  compareRuns,
  completionLabel,
  resultLabel,
  sameInput,
  validDraft,
  type RunView,
  type ScenarioIdentity,
} from '../../apps/desktop/src/renderer/src/scenario/presentation'

const identity: ScenarioIdentity = {
  projectId: 'project-1',
  engineVersion: 'engine-1',
  dependencyLockHash: 'lock-1',
  projectVersion: 'P1',
  scenarioId: 'S1',
  inputVersion: 'V1',
  ruleVersion: 'R1',
  behaviorVersion: 'B1',
  configurationDigest: 'C1',
  semantics: 'scenario-e2-v1',
}
const run: RunView = {
  id: 'run1',
  identity,
  status: 'succeeded',
  rounds: [
    {
      number: 1,
      created: ['W001'],
      completed: [],
      backlog: ['W001'],
      metrics: { backlog: 1, completed: 0, openHighAlerts: 1 },
      inputEvents: ['E1'],
      behaviorTrace: ['E1/B1'],
      beforeInference: 'before1',
      endInference: 'end1',
    },
  ],
  pendingEvents: [],
  replayAvailable: false,
  evidence: {
    source: 'probe',
    assumptions: ['original V1 assumption'],
    maxRounds: 4,
    capacity: 3,
    parameters: '{}',
  },
}

describe('T07 scenario presentation identity and truthful states', () => {
  it('never promotes a V1 late completion as the current V2 result', () => {
    expect(resultLabel(run, { ...identity, inputVersion: 'V2' })).toContain('历史结果')
    expect(resultLabel(run, identity)).toBe('当前结果')
  })
  it.each(Object.keys(identity) as (keyof ScenarioIdentity)[])(
    'checks the complete dependency identity: %s',
    (key) => expect(sameInput(identity, { ...identity, [key]: 'changed' })).toBe(false),
  )
  it('preserves cancellation and failure labels even when input matches', () => {
    expect(resultLabel({ ...run, status: 'cancelled' }, identity)).toBe('已取消 · 历史运行')
    expect(resultLabel({ ...run, status: 'failed' }, identity)).toBe('失败 · 历史运行')
    expect(completionLabel({ ...run, status: 'failed' })).toBe('运行尚未成功结束')
  })
  it('maximum-round success still exposes all unprocessed events', () => {
    expect(completionLabel({ ...run, pendingEvents: ['E2', 'E3'] })).toBe('存在未处理事件（2）')
    expect(completionLabel(run)).toBe('已配置轮次执行完毕，无未处理事件')
  })
  it.each([0, 1001, 1.5, NaN, Infinity])('rejects invalid maxRounds %s', (maxRounds) => {
    expect(validDraft({ name: '基准', maxRounds, capacity: 3 })).toBe(false)
  })
  it.each([-1, 1.5, NaN, Infinity])('rejects invalid capacity %s', (capacity) => {
    expect(validDraft({ name: '基准', maxRounds: 4, capacity })).toBe(false)
  })
  it('allows zero capacity and the full 1000 round boundary', () => {
    expect(validDraft({ name: '资源不足场景', maxRounds: 1000, capacity: 0 })).toBe(true)
    expect(validDraft({ name: ' ', maxRounds: 4, capacity: 3 })).toBe(false)
  })
  it('compares real round values without inventing missing observations', () => {
    const second: RunView = {
      ...run,
      id: 'run2',
      identity: { ...identity, scenarioId: 'S2' },
      rounds: [
        { ...run.rounds[0], number: 2, metrics: { backlog: 0, completed: 4, openHighAlerts: 0 } },
      ],
    }
    expect(compareRuns([run, second])).toEqual([
      { round: 1, values: [{ backlog: 1, completed: 0, openHighAlerts: 1 }, null] },
      { round: 2, values: [null, { backlog: 0, completed: 4, openHighAlerts: 0 }] },
    ])
    expect(compareRuns([run])).toEqual([])
    expect(compareRuns([run, { ...second, status: 'failed' }])).toEqual([])
  })
})

describe('T07 structured local draft checks', () => {
  const inputs = {
    initialState: '{}',
    events: '[]',
    rules: '{}',
    behaviors: '{}',
    parameters: '{}',
    assumptions: '假设',
    source: '来源',
  }
  const draft = { name: '自定义', maxRounds: 4, capacity: 3, inputs }
  it('validates events with identity/round/sequence/object payload before submission', () => {
    expect(
      validDraft({
        ...draft,
        inputs: { ...inputs, events: '[{"id":"E1","round":1,"sequence":0,"payload":{}}]' },
      }),
    ).toBe(true)
    for (const events of [
      '{}',
      '[{}]',
      '[{"id":"E1","round":0,"sequence":0,"payload":{}}]',
      '[{"id":"E1","round":1,"sequence":0,"payload":"code"}]',
      '[{"id":"E1","round":1,"sequence":0,"payload":{},"unknown":1}]',
    ]) {
      expect(validDraft({ ...draft, inputs: { ...inputs, events } })).toBe(false)
    }
    expect(validDraft({ ...draft, inputs: { ...inputs, rules: 'null' } })).toBe(false)
    expect(validDraft({ ...draft, inputs: { ...inputs, initialState: '[]' } })).toBe(false)
  })
  it('rejects reused event IDs with different content', () => {
    expect(
      validDraft({
        ...draft,
        inputs: {
          ...inputs,
          events:
            '[{"id":"E1","round":1,"sequence":0,"payload":{}},{"id":"E1","round":2,"sequence":1,"payload":{}}]',
        },
      }),
    ).toBe(false)
  })
  it('validates personnel capacity and safe integer bounds', () => {
    expect(validDraft({ ...draft, capacityMode: 'people', people: 2, perPerson: 3 })).toBe(true)
    expect(validDraft({ ...draft, capacityMode: 'people', people: 2 })).toBe(false)
    expect(
      validDraft({
        ...draft,
        capacityMode: 'people',
        people: Number.MAX_SAFE_INTEGER,
        perPerson: 3,
      }),
    ).toBe(false)
  })
})
