import { describe, expect, it, vi } from 'vitest'
import type {
  BehaviorBridge,
  BehaviorRunResultDTO,
  MainlineProjectReadDTO,
  ScenarioBridge,
  ScenarioCompareResultDTO,
  ScenarioReadResultDTO,
  ScenarioRunDTO,
  ScenarioRunResultDTO,
  ScenarioSummaryDTO,
} from '@ontolearn/contracts'
import { BehaviorAdapterContract } from '@ontolearn/contracts'
import {
  behaviorServices,
  lowerBehaviorSample,
  projectBehaviorResult,
  readBehaviorCatalog,
} from '../../apps/desktop/src/renderer/src/behavior/bridge'
import {
  emptyDraft,
  resultSchema,
  type SampleRequest,
} from '../../apps/desktop/src/renderer/src/behavior/model'
import { resultSections } from '../../apps/desktop/src/renderer/src/behavior/presentation'
import {
  scenarioConfiguration,
  scenarioRunView,
  scenarioServices,
} from '../../apps/desktop/src/renderer/src/scenario/bridge'
import fixtures from '../../packages/contracts/v2/fixtures.json'

const projectId = '00000000-0000-4000-8000-000000000001'
const runId = '00000000-0000-4000-8000-000000000002'
const operationId = '00000000-0000-4000-8000-000000000004'
const requestId = '00000000-0000-4000-8000-000000000005'
const inputSnapshotId = 'a'.repeat(64)
const rdfType = BehaviorAdapterContract.actions.create.classProperty
const owl = 'http://www.w3.org/2002/07/owl#'

function contractReply<T>(method: string): T {
  const fixture = fixtures.business3.responses.find(
    (item) => item.name === `W4 ${method} valid binding`,
  )
  if (!fixture || !('result' in fixture.response)) throw new Error('missing frozen fixture')
  return structuredClone(fixture.response.result) as T
}
const ok = <T>(data: T) => ({ ok: true as const, data })

function behaviorRequest(): SampleRequest {
  return {
    binding: {
      projectId,
      inputVersion: inputSnapshotId,
      scopeId: projectId,
      behaviorVersion: '1',
      requestId,
    },
    draft: {
      ...emptyDraft(),
      id: 'B-01',
      name: '工单',
      description: '创建测试',
      effect: '验证触发',
      trigger: 'alarm',
      triggerEventId: 'event-2',
      version: 4,
      conditions: [
        { kind: 'always' },
        { kind: 'type', object: 'urn:equipment', classId: 'urn:Equipment' },
        {
          kind: 'equals',
          object: 'urn:equipment',
          property: 'urn:score',
          value: { kind: 'number', value: 7 },
        },
        {
          kind: 'has',
          object: 'urn:equipment',
          property: 'urn:active',
          value: { kind: 'boolean', value: false },
        },
      ],
      actions: [
        { kind: 'create', object: 'urn:order-new', classId: 'urn:Order' },
        {
          kind: 'update',
          object: 'urn:equipment',
          property: 'urn:score',
          value: { kind: 'number', value: 1 },
        },
        {
          kind: 'relate',
          object: 'urn:equipment',
          property: 'urn:orders',
          target: 'urn:order-new',
        },
        { kind: 'notify', message: '已创建测试工单' },
      ],
    },
    events: [
      {
        id: 'event-1',
        type: 'inspect',
        version: 16,
        payload: { location: '001', counted: false },
        changes: [],
      },
      {
        id: 'event-2',
        type: 'alarm',
        version: 37,
        payload: { severity: 'High' },
        objectEdits: [{ kind: 'declare', object: 'urn:alarm' }],
        changes: [
          {
            operation: 'set',
            object: 'urn:equipment',
            property: 'urn:score',
            value: { kind: 'number', value: 7 },
          },
        ],
      },
    ],
  }
}
function behaviorCatalog() {
  const definition = {
    layer: 'ontology' as const,
    id: 'sample',
    payload: JSON.stringify({
      singleValuedPredicates: ['urn:score', 'urn:active'],
      triples: [
        ['urn:Equipment', owl + 'Class'],
        ['urn:Order', owl + 'Class'],
        ['urn:score', owl + 'DatatypeProperty'],
        ['urn:active', owl + 'DatatypeProperty'],
        ['urn:orders', owl + 'ObjectProperty'],
      ].map(([subject, object]) => ({ subject, predicate: rdfType, object: `<${object}>` })),
    }),
  }
  return readBehaviorCatalog({
    domain: {
      state: {
        definitions: [definition],
        facts: [{ subject: 'urn:equipment', predicate: rdfType, object: '<urn:Equipment>' }],
      },
    },
  } as MainlineProjectReadDTO)
}

describe('W4 behavior R7 renderer bridge', () => {
  it.each(['B-01', 'B-02'])(
    'lowers type, typed AND predicates, class initialization and ordered events for %s',
    (id) => {
      const request = behaviorRequest()
      request.draft.id = id
      const args = lowerBehaviorSample(request, behaviorCatalog(), 17, runId, operationId)
      expect(args).toMatchObject({
        runId,
        operationId,
        scope: 'sample',
        binding: {
          projectId,
          baseRevision: 17,
          inputSnapshotId,
          behaviorVersion: '4',
          scopeId: projectId,
          requestId,
        },
        draft: {
          trigger: { eventType: 'alarm', eventId: 'event-2' },
          conditions: [
            { op: 'always' },
            {
              op: 'has',
              property: rdfType,
              value: { kind: 'value', value: { kind: 'iri', value: 'urn:Equipment' } },
            },
            {
              op: 'has',
              property: 'urn:score',
              value: { kind: 'value', value: { kind: 'number', value: 7 } },
            },
            {
              op: 'has',
              property: 'urn:active',
              value: { kind: 'value', value: { kind: 'boolean', value: false } },
            },
          ],
          actions: [
            {
              kind: 'create',
              initial: [
                {
                  property: rdfType,
                  value: { kind: 'value', value: { kind: 'iri', value: 'urn:Order' } },
                },
              ],
            },
            { kind: 'set', subject: { value: { value: 'urn:equipment' } } },
            { kind: 'add', value: { value: { kind: 'iri', value: 'urn:order-new' } } },
            { kind: 'notify', message: { value: { kind: 'string', value: '已创建测试工单' } } },
          ],
        },
        events: [
          {
            id: 'event-1',
            type: 'inspect',
            sequence: 0,
            version: 16,
            payload: { location: '001', counted: false },
            edits: [],
          },
          {
            id: 'event-2',
            type: 'alarm',
            sequence: 1,
            version: 37,
            edits: [
              { kind: 'declare', object: 'urn:alarm' },
              {
                kind: 'set',
                subject: 'urn:equipment',
                property: 'urn:score',
                value: { kind: 'number', value: 7 },
              },
            ],
          },
        ],
      })
    },
  )

  it('rejects unavailable conditions, conflicting class assertions, unknown triggers and cardinality mismatches', () => {
    const catalog = behaviorCatalog()
    const lower = (request: SampleRequest, supported = catalog) =>
      lowerBehaviorSample(request, supported, 17, runId, operationId)
    const request = behaviorRequest()
    expect(() => lower(request, { ...catalog, typeAssertions: false })).toThrow(
      'behavior.unavailable',
    )
    request.draft.conditions = [{ kind: 'exists', object: 'urn:equipment', property: 'urn:score' }]
    expect(() => lower(request)).toThrow('behavior.unavailable')
    request.draft.conditions = []
    expect(() => lower(request)).toThrow('behavior.invalidInput')
    request.draft.conditions = [{ kind: 'always' }]
    request.draft.triggerEventId = 'event-1'
    expect(() => lower(request)).toThrow('behavior.invalidInput')
    request.draft.triggerEventId = undefined
    request.draft.trigger = 'missing'
    expect(() => lower(request)).toThrow('behavior.invalidInput')
    request.draft.trigger = 'alarm'
    request.draft.actions = [
      {
        kind: 'update',
        object: 'urn:equipment',
        property: 'urn:orders',
        value: { kind: 'iri', value: 'urn:order-existing' },
      },
    ]
    expect(() => lower(request)).toThrow('behavior.invalidInput')
    request.draft.actions = [
      { kind: 'relate', object: 'urn:equipment', property: 'urn:score', target: 'urn:order-new' },
    ]
    expect(() => lower(request)).toThrow('behavior.invalidInput')
    request.draft.actions = [
      {
        kind: 'create',
        object: 'urn:order-new',
        classId: 'urn:Order',
        initial: [{ property: rdfType, value: { kind: 'iri', value: 'urn:Equipment' } }],
      },
    ]
    expect(() => lower(request)).toThrow('behavior.invalidInput')
  })

  it.each(['__proto__', 'prototype', 'constructor'])(
    'rejects a payload with own %s before calling the host',
    async (key) => {
      const request = behaviorRequest()
      request.events[0].payload = JSON.parse(`{"ordinary":"001","${key}":true}`)
      const bridge: BehaviorBridge = {
        runBehaviorSample: vi.fn(),
        cancelBehaviorRun: vi.fn(),
        readBehaviorRun: vi.fn(),
      }
      await expect(
        behaviorServices(bridge, behaviorCatalog(), 17).runSample!(request),
      ).rejects.toThrow('behavior.invalidInput')
      expect(bridge.runBehaviorSample).not.toHaveBeenCalled()
    },
  )

  it('preserves candidate and isolated completed diffs, freshness and persisted cancellation binding', async () => {
    const request = behaviorRequest()
    const fixture = contractReply<BehaviorRunResultDTO>('project.behavior.run')
    const notification = {
      id: 'notice-1',
      eventId: 'event-2',
      behaviorId: 'B-01',
      message: '工单已创建',
    }
    const createFixture = ({
      binding,
      runId,
      operationId,
    }: Parameters<BehaviorBridge['runBehaviorSample']>[0]): BehaviorRunResultDTO => ({
      ...fixture,
      binding,
      runId,
      operationId,
      state: 'candidate',
      committed: false,
      error: null,
      assertionVersion: 'assert-17',
      inferenceVersion: 'infer-17',
      actions: [
        { eventId: 'event-2', behaviorId: 'B-01', index: 0, kind: 'create', state: 'planned' },
      ],
      diff: {
        removed: [],
        added: [
          { kind: 'object', objectId: 'urn:order-new' },
          {
            kind: 'fact',
            fact: {
              subject: 'urn:equipment',
              property: 'urn:score',
              value: { kind: 'number', value: 7 },
            },
          },
          { kind: 'notification', notification },
        ],
      },
      notifications: [{ ...notification, state: 'candidate' }],
    })
    const run = vi.fn<BehaviorBridge['runBehaviorSample']>(async (args) => ok(createFixture(args)))
    const read = vi.fn<BehaviorBridge['readBehaviorRun']>(async (args) => {
      const candidate = createFixture({ ...run.mock.calls[0][0], ...args })
      if (candidate.state !== 'candidate') throw new Error('invalid fixture')
      return ok({
        ...candidate,
        freshness: 'historical',
        staleReason: 'scope-replaced',
        state: 'completed',
        committed: true,
        actions: [{ ...candidate.actions[0], state: 'applied' }],
        notifications: [{ ...notification, state: 'recorded' }],
      })
    })
    const cancel = vi.fn<BehaviorBridge['cancelBehaviorRun']>(async (args) =>
      ok({
        ...fixture,
        ...args,
        state: 'cancelled',
        committed: false,
        error: null,
        assertionVersion: null,
        inferenceVersion: null,
        actions: [
          {
            eventId: 'event-2',
            behaviorId: 'B-01',
            index: 0,
            kind: 'create',
            state: 'rolled_back',
          },
        ],
        diff: { added: [], removed: [] },
        notifications: [{ ...notification, state: 'discarded' }],
      }),
    )
    const services = behaviorServices(
      { runBehaviorSample: run, readBehaviorRun: read, cancelBehaviorRun: cancel },
      behaviorCatalog(),
      17,
    )
    const candidate = resultSchema.parse(await services.runSample!(request))
    expect(candidate.committed).toBe(false)
    expect(resultSections(candidate).added).toEqual([
      'urn:equipment · urn:score · 7',
      '对象 · urn:order-new',
      '通知 · notice-1 / event-2 / B-01 · 工单已创建',
    ])
    const historical = resultSchema.parse(
      await services.refreshResult!(request.binding, candidate.runId),
    )
    expect(historical).toMatchObject({
      committed: true,
      state: 'completed',
      freshness: 'historical',
      freshnessDetail: '隔离副本已替换',
    })
    expect(resultSchema.parse(await services.cancelSample!(request.binding))).toMatchObject({
      committed: false,
      state: 'cancelled',
      diff: { added: [], removed: [] },
    })
    expect(read.mock.calls[0][0]).toEqual(cancel.mock.calls[0][0])
    expect(read.mock.calls[0][0]).not.toHaveProperty('events')
    await expect(services.refreshResult!(request.binding, 'other-run')).rejects.toThrow()
  })

  it('accepts an allowlisted failed result and rejects private diagnostics and forged cancellation', () => {
    const base = contractReply<BehaviorRunResultDTO>('project.behavior.run')
    const { binding, runId, operationId, scope } = base
    const expected = { binding, runId, operationId, scope }
    const failed: BehaviorRunResultDTO = {
      ...base,
      state: 'failed',
      committed: false,
      freshness: 'stale',
      staleReason: 'snapshot-changed',
      error: BehaviorAdapterContract.projectError('stale_reasoning'),
      actions: [],
      notifications: [],
      diff: { added: [], removed: [] },
    }
    expect(projectBehaviorResult(failed, expected, behaviorRequest().binding, 'run')).toMatchObject(
      {
        freshness: 'stale',
        freshnessDetail: '输入快照已变化',
        error: 'conflict',
      },
    )
    const leaked = { ...failed, error: { ...failed.error, evidence: '/Users/example/private' } }
    expect(() =>
      projectBehaviorResult(
        leaked as BehaviorRunResultDTO,
        expected,
        behaviorRequest().binding,
        'run',
      ),
    ).toThrow('behavior.invalidInput')
    expect(() =>
      projectBehaviorResult(base, expected, behaviorRequest().binding, 'cancel'),
    ).toThrow()
  })
})

describe('W4 scenario bridge', () => {
  const inputs = {
    initialState: '[{"kind":"declare","object":"urn:sample"}]',
    events: '[{"id":"alarm","round":1,"sequence":0,"payload":{"severity":"High"}}]',
    rules: 'R4',
    behaviors: 'B6',
    parameters: '{"batch":2}',
    source: '基准项目',
    assumptions: '固定产能\n无额外人工',
  }

  it('admits both capacity modes and validates structured inputs through the frozen schema', () => {
    const draft = { name: '运维', maxRounds: 8, capacity: 0, inputs }
    expect(scenarioConfiguration(draft)).toMatchObject({
      capacity: { mode: 'direct', direct: 0 },
      ruleVersion: 'R4',
      behaviorVersion: 'B6',
      initialEdits: [{ kind: 'declare', object: 'urn:sample' }],
      assumptions: ['固定产能', '无额外人工'],
      events: [{ id: 'alarm', round: 1, sequence: 0, payload: { severity: 'High' } }],
      parameters: { batch: 2 },
    })
    expect(
      scenarioConfiguration({ ...draft, capacityMode: 'people', people: 2, perPerson: 4 }).capacity,
    ).toEqual({ mode: 'people', people: 2, perPerson: 4 })
    expect(() =>
      scenarioConfiguration({ ...draft, inputs: { ...inputs, parameters: '{"__proto__":1}' } }),
    ).toThrow('INVALID_CONFIGURATION')
  })

  it('binds all persisted paths and only resumes with the original run and checkpoint', async () => {
    const started = contractReply<ScenarioRunResultDTO>('project.scenario.run')
    const summary: ScenarioSummaryDTO = {
      identity: started.run.identity,
      configuration: scenarioConfiguration({ name: '基准', maxRounds: 8, capacity: 3, inputs }),
    }
    const round = {
      number: 1,
      created: [],
      resourceCompleted: ['order-1'],
      backlog: [],
      metrics: { backlog: 0, completed: 1, openHighAlerts: 0 },
      inputEvents: ['event-1'],
      behaviorTrace: [],
      beforeInference: inputSnapshotId,
      endInference: inputSnapshotId,
      checkpointRef: inputSnapshotId,
    }
    const completedRound = {
      ...started.run,
      lastCommittedRound: 1,
      rounds: [round],
      status: 'cancelled',
      checkpointRef: inputSnapshotId,
      resumeAvailable: true,
      pendingEvents: ['event-2'],
    } satisfies ScenarioRunDTO
    const read = { projectId, scenario: summary, runs: [] } satisfies ScenarioReadResultDTO
    const data = {
      listScenarios: vi.fn<ScenarioBridge['listScenarios']>(async () =>
        ok({ projectId, items: [summary], nextCursor: runId }),
      ),
      readScenario: vi.fn<ScenarioBridge['readScenario']>(async () => ok(read)),
      createScenario: vi.fn<ScenarioBridge['createScenario']>(async (args) =>
        ok({
          projectId,
          operationId: args.operationId,
          scenario: { ...summary, configuration: args.configuration },
        }),
      ),
      copyScenario: vi.fn<ScenarioBridge['copyScenario']>(async (args) =>
        ok({
          projectId,
          operationId: args.operationId,
          sourceScenarioId: args.scenarioId,
          scenario: {
            identity: { ...summary.identity, scenarioId: runId },
            configuration: { ...summary.configuration, name: args.name },
          },
        }),
      ),
      startScenarioRun: vi.fn<ScenarioBridge['startScenarioRun']>(async (args) =>
        ok({
          ...started,
          operationId: args.operationId,
          run: { ...started.run, runId: args.runId },
        }),
      ),
      readScenarioRun: vi.fn<ScenarioBridge['readScenarioRun']>(async (args) =>
        ok({ projectId, run: { ...completedRound, runId: args.runId } }),
      ),
      cancelScenarioRun: vi.fn<ScenarioBridge['cancelScenarioRun']>(async (args) =>
        ok({
          projectId,
          operationId: args.operationId,
          run: { ...completedRound, runId: args.runId },
        }),
      ),
      resumeScenarioRun: vi.fn<ScenarioBridge['resumeScenarioRun']>(async (args) =>
        ok({
          ...started,
          operationId: args.operationId,
          sourceRunId: args.sourceRunId,
          resumedFrom: args.checkpointRef,
          run: { ...started.run, runId: args.runId },
        }),
      ),
      compareScenarioRuns: vi.fn<ScenarioBridge['compareScenarioRuns']>(async () =>
        ok(contractReply<ScenarioCompareResultDTO>('project.scenario.compare')),
      ),
      deleteScenarioRun: vi.fn<ScenarioBridge['deleteScenarioRun']>(async (args) =>
        ok({ projectId, ...args, deleted: true }),
      ),
      restoreScenarioBaseline: vi.fn<ScenarioBridge['restoreScenarioBaseline']>(async (args) =>
        ok({
          projectId,
          operationId: args.operationId,
          configurationDigest: args.configurationDigest,
          scenario: summary,
        }),
      ),
    }
    const services = scenarioServices(data, projectId, { inputSnapshotId, projectVersion: 0 })
    expect((await services.list(null)).nextCursor).toBe(runId)
    expect(await services.read(summary.identity.scenarioId)).toEqual(read)
    const draft = { name: '运维新方案', maxRounds: 6, capacity: 2, inputs }
    expect((await services.create(draft)).configuration.maxRounds).toBe(6)
    expect((await services.create(draft, summary.identity)).identity.scenarioId).toBe(runId)
    const run = await services.run(summary.identity)
    expect(run.status).toBe('queued')
    const ref = { runId: run.runId, scenarioId: summary.identity.scenarioId }
    const paged = await services.readRun(ref, 0)
    expect(scenarioRunView(paged)).toMatchObject({
      lastCommittedRound: 1,
      pendingEvents: ['event-2'],
      rounds: [{ completed: ['order-1'] }],
    })
    const cancelled = await services.cancel(run)
    expect(cancelled).toMatchObject({ status: 'cancelled', lastCommittedRound: 1 })
    await expect(services.resume({ ...cancelled, checkpointRef: null })).rejects.toThrow(
      'RESUME_UNAVAILABLE',
    )
    expect(data.resumeScenarioRun).not.toHaveBeenCalled()
    const resumed = await services.resume(cancelled)
    expect(resumed.runId).not.toBe(run.runId)
    expect(data.resumeScenarioRun).toHaveBeenCalledWith(
      expect.objectContaining({ sourceRunId: run.runId, checkpointRef: inputSnapshotId }),
    )
    const other = contractReply<ScenarioCompareResultDTO>('project.scenario.compare')
    const picks = other.runs.map((row) => ({
      scenarioId: row.identity.scenarioId,
      runId: row.runId,
    }))
    expect((await services.compare(picks, 0)).runs).toHaveLength(2)
    await expect(services.compare(picks.slice(0, 1), 0)).rejects.toThrow('INVALID_COMPARISON')
    await expect(
      services.compare(
        Array.from({ length: 11 }, () => picks[0]),
        0,
      ),
    ).rejects.toThrow('INVALID_COMPARISON')
    await services.remove(cancelled)
    expect((await services.restore(summary.identity)).identity).toEqual(summary.identity)
  })
})
