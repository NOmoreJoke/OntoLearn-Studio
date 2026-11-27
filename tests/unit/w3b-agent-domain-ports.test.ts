import { describe, expect, it, vi } from 'vitest'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import type {
  BridgeResult,
  JobView,
  QueryDraftDTO,
  QueryDescriptorDTO,
  ResultMetadataDTO,
  MainlineProjectReadDTO,
} from '@ontolearn/contracts'
import { AgentSession, type TrustedContext } from '../../apps/desktop/src/main/agent/agent-service'
import {
  AgentToolRegistry,
  draftDetailToPlan,
  FORMAL_WRITE_TOOLS,
} from '../../apps/desktop/src/main/agent/domain-ports'
import { toolAccess, toolNames } from '../../apps/desktop/src/main/agent/tools'

const context: TrustedContext = {
  projectId: 'project-1',
  projectRevision: 12,
  inputSnapshotId: '001',
  scopeRef: 'scope-1',
  module: 'ontology',
  mode: 'project',
  selectedObjectIds: ['definition-1', 'saved-1', 'result-1'],
}
const signal = new AbortController().signal
const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
const selectedTriple = {
  subject: 'urn:example:equipment',
  predicate: 'urn:example:type',
  object: '<urn:example:asset>',
}
const otherTriple = {
  subject: 'urn:private:equipment',
  predicate: 'urn:private:predicate',
  object: '<urn:private:asset>',
}
const query: QueryDraftDTO = {
  name: '设备检查',
  description: '',
  sparql: 'ASK { ?s ?p ?o }',
  scope: 'asserted',
  capabilityQuestion: '是否有事实？',
  source: 'editor',
}

function fixture() {
  const project = {
    projectId: context.projectId,
    inputSnapshotId: context.inputSnapshotId,
    domain: {
      projectRevision: 12,
      state: {
        definitions: [
          {
            layer: 'ontology',
            id: 'definition-1',
            payload: JSON.stringify({ triples: [selectedTriple] }),
          },
          {
            layer: 'ontology',
            id: 'definition-2',
            payload: JSON.stringify({ triples: [otherTriple] }),
          },
          { layer: 'query', id: 'saved-1', payload: '{}' },
        ],
        facts: [{ id: 'private-fact', ...otherTriple, owner: '/Users/private/secret' }],
      },
    },
  } as MainlineProjectReadDTO
  const job: JobView = {
    projectId: context.projectId,
    jobId: 'job-1',
    operationId: 'op-1',
    state: 'succeeded',
    stateVersion: 3,
    inputSnapshotId: '001',
    resultRef: { resultId: 'result-1', inputSnapshotId: '001' },
    error: null,
  }
  const result = {
    resultId: 'result-1',
    projectId: context.projectId,
    inputSnapshotId: '001',
    inputProjectRevision: 12,
    scope: 'asserted',
    kind: 'query',
    payloadStatus: 'available',
    state: 'historical',
    hiddenPath: '/Users/private/data',
  } as unknown as ResultMetadataDTO
  let live = true
  const loadQueryDefinition =
    vi.fn<
      ConstructorParameters<
        typeof AgentToolRegistry
      >[0]['projects']['queries']['loadQueryDefinition']
    >()
  loadQueryDefinition.mockImplementation(async ({ selection }) =>
    ok({
      kind: 'managed',
      descriptorVersion: 1,
      descriptorSha256: 'hash',
      definitionSha256: 'def',
      projectId: context.projectId,
      definitionId: 'saved-1',
      definitionVersion: 1,
      loadRef: 'loaded-1',
      baseProjectRevision: 12,
      inputSnapshotId: selection.kind === 'historical' ? selection.snapshotId : '001',
      draft: { ...query, scope: selection.kind === 'current' ? 'asserted+derived' : 'asserted' },
    }),
  )
  const executeSavedQuery =
    vi.fn<
      ConstructorParameters<typeof AgentToolRegistry>[0]['projects']['queries']['executeSavedQuery']
    >()
  executeSavedQuery.mockImplementation(async ({ operationId }) =>
    ok({
      operationId,
      acceptedJob: { ...job, operationId },
      watch: { state: 'subscribed' },
    }),
  )
  const getQueryResultDescriptor =
    vi.fn<
      ConstructorParameters<
        typeof AgentToolRegistry
      >[0]['projects']['queries']['getQueryResultDescriptor']
    >()
  getQueryResultDescriptor.mockImplementation(async () =>
    ok({
      descriptorRef: 'descriptor',
      identity: {
        projectId: context.projectId,
        jobId: job.jobId,
        resultId: result.resultId,
        scope: result.scope,
        inputSnapshotId: result.inputSnapshotId,
        inputSelection: result.state === 'historical' ? 'historical' : 'current',
      },
      metadata: result,
      query: { kind: 'ASK', value: true },
    } as QueryDescriptorDTO),
  )
  const readProject = vi.fn(async () => ok(project))
  const getResult = vi.fn(async () => ok(result))
  const getProjectQualityState =
    vi.fn<
      ConstructorParameters<typeof AgentToolRegistry>[0]['projects']['getProjectQualityState']
    >()
  const runProjectQualityCheck =
    vi.fn<
      ConstructorParameters<typeof AgentToolRegistry>[0]['projects']['runProjectQualityCheck']
    >()
  const registry = new AgentToolRegistry({
    projects: {
      readProject,
      queries: { loadQueryDefinition, executeSavedQuery, getQueryResultDescriptor },
      getProjectQualityState,
      runProjectQualityCheck,
    },
    tasks: { getJob: async () => ok(job), getResult },
    receive: (work) => work(),
    current: () => live,
    scope: 'asserted+derived',
  })
  return {
    registry,
    readProject,
    getResult,
    result,
    job,
    loadQueryDefinition,
    executeSavedQuery,
    getProjectQualityState,
    runProjectQualityCheck,
    fence: () => {
      live = false
    },
  }
}

describe('Agent tool ports', () => {
  it('offers seven Wave 3 ports, reserves three disabled Wave 4 ports, and has no formal write tool', async () => {
    const { registry } = fixture()
    expect(FORMAL_WRITE_TOOLS.length).toBe(0)
    expect(Object.isFrozen(FORMAL_WRITE_TOOLS)).toBe(true)
    expect(new Set(Object.values(toolAccess))).toEqual(new Set(['read', 'draft', 'isolated-run']))
    const registrations = registry.entries()
    expect(registrations.map(({ name }) => name)).toEqual([...toolNames])
    const ports = registry.buildPorts()
    expect(Object.keys(ports)).toHaveLength(7)
    for (const { name, wave, enabled, access } of registrations) {
      expect(access).toBe(toolAccess[name])
      expect(enabled).toBe(wave === 3)
      expect(Boolean(ports[name])).toBe(enabled)
      if (!enabled)
        await expect(registry.execute(name, context, {}, signal)).rejects.toThrow(
          'TOOL_UNAVAILABLE',
        )
    }
  })
  it('reads only host-selected declarations and rejects before IO on an out-of-scope object', async () => {
    const { registry, readProject } = fixture()
    await expect(
      registry.execute('ontology_read', context, { objectIds: ['definition-2'] }, signal),
    ).rejects.toThrow('TOOL_NOT_ALLOWED')
    expect(readProject).not.toHaveBeenCalled()
    const response = await registry.execute(
      'ontology_read',
      context,
      { objectIds: ['definition-1'] },
      signal,
    )
    expect(response).toMatchObject({
      status: 'current',
      inputSnapshotId: '001',
      fields: [
        { fieldId: 'triple-0-subject', value: selectedTriple.subject },
        { fieldId: 'triple-0-predicate', value: selectedTriple.predicate },
        { fieldId: 'triple-0-object', value: selectedTriple.object },
      ],
    })
    expect(JSON.stringify(response)).not.toMatch(/private|owner/)
  })
  it('produces deterministic, engine-schema-compatible drafts with stamped human confirmation', async () => {
    const { registry, readProject, executeSavedQuery } = fixture()
    const session = new AgentSession(context, registry.buildPorts())
    const receipts = await session.executeCalls(
      [
        {
          id: 'c1',
          type: 'function',
          function: {
            name: 'ontology_propose',
            arguments: JSON.stringify({
              instruction: JSON.stringify({ classIri: 'urn:example:equipment' }),
            }),
          },
        },
        {
          id: 'c2',
          type: 'function',
          function: {
            name: 'query_draft',
            arguments: JSON.stringify({
              scope: 'asserted',
              question: JSON.stringify({
                kind: 'query-draft',
                name: query.name,
                description: query.description,
                capabilityQuestion: query.capabilityQuestion,
                sparql: query.sparql,
              }),
            }),
          },
        },
      ],
      () => context,
      signal,
    )
    for (const { outcome } of receipts) {
      expect(outcome).toMatchObject({
        kind: 'draft',
        requiresHumanDiffConfirmation: true,
        baseRevision: 12,
      })
      if (outcome.kind !== 'draft') throw new Error('expected a draft')
      const plan = draftDetailToPlan(outcome.draftType, outcome.detail)
      expect(plan).toEqual(draftDetailToPlan(outcome.draftType, outcome.detail))
      expect(
        validateBusiness3('params_changeset.preview', {
          projectId: '11111111-1111-4111-8111-111111111111',
          baseRevision: 12,
          intent: 'change',
          plan,
        }),
      ).toBe(true)
    }
    expect(readProject).not.toHaveBeenCalled()
    expect(executeSavedQuery).not.toHaveBeenCalled()
  })
  it.each([
    ['selected-history', { kind: 'historical', snapshotId: '001' }, 'asserted'],
    ['asserted-and-derived', { kind: 'current' }, 'asserted+derived'],
  ] as const)(
    'passes normalized %s through load, prepare/execute and read-back',
    async (scope, selection, queryScope) => {
      const f = fixture()
      f.result.scope = queryScope
      if (selection.kind === 'current') f.result.state = 'current'
      await expect(
        f.registry.execute('query_execute', context, { scope, sparql: query.sparql }, signal),
      ).resolves.toMatchObject({
        kind: 'evidence',
        status: f.result.state,
        resultId: 'result-1',
        fields: expect.arrayContaining([{ fieldId: 'ask-value', value: true }]),
      })
      expect(f.loadQueryDefinition).toHaveBeenCalledWith({ definitionId: 'saved-1', selection })
      expect(f.executeSavedQuery).toHaveBeenCalledWith({
        loadRef: 'loaded-1',
        operationId: expect.any(String),
        visibleDraft: { ...query, scope: queryScope },
        selection,
      })
      expect(f.getResult).toHaveBeenCalledWith('result-1')
    },
  )
  it('rejects a changed context after an awaited read before entering the next async operation', async () => {
    const f = fixture()
    const original = f.loadQueryDefinition.getMockImplementation()!
    f.loadQueryDefinition.mockImplementationOnce(async (input) => {
      f.fence()
      return original(input)
    })
    await expect(
      f.registry.execute(
        'query_execute',
        context,
        {
          scope: 'asserted-and-derived',
          sparql: query.sparql,
        },
        signal,
      ),
    ).rejects.toThrow('STALE_CONTEXT')
    expect(f.executeSavedQuery).not.toHaveBeenCalled()
  })
  it('retains quality failure, reads real reasoning state, and projects only finite result fields', async () => {
    const f = fixture()
    f.getProjectQualityState.mockResolvedValue(
      ok({
        qualityReadVersion: 1,
        projectId: context.projectId,
        rules: [],
        constraints: [],
        validation: null,
        reasoning: {
          resultId: 'reasoning-1',
          jobId: 'job-1',
          state: 'current',
          scope: 'asserted',
          definitionId: 'reasoning',
          staleReasons: [],
          inputSnapshotId: '001',
        },
      }),
    )
    f.runProjectQualityCheck.mockResolvedValue(
      ok({
        qualityRunVersion: 1,
        projectId: context.projectId,
        operationId: 'op',
        reasoningJob: { ...f.job, state: 'failed' },
        validationJobs: [],
        qualityState: {
          qualityReadVersion: 1,
          projectId: context.projectId,
          rules: [],
          constraints: [],
          reasoning: null,
          validation: null,
        },
      }),
    )
    await expect(
      f.registry.execute('reasoning_run', context, { scope: 'asserted' }, signal),
    ).resolves.toMatchObject({ resultId: 'reasoning-1', status: 'current' })
    await expect(
      f.registry.execute('quality_check', context, { scope: 'asserted' }, signal),
    ).resolves.toMatchObject({ resultId: 'job-1', status: 'failed' })
    const evidence = await f.registry.execute(
      'result_read',
      context,
      { resultId: 'result-1' },
      signal,
    )
    expect(evidence).toMatchObject({
      status: 'historical',
      fields: [
        { fieldId: 'result-kind', value: 'query' },
        { fieldId: 'input-revision', value: 12 },
        { fieldId: 'payload-available', value: true },
      ],
    })
    expect(JSON.stringify(evidence)).not.toContain('/Users/private')
  })
})
