import type { IpcMainInvokeEvent } from 'electron'
import { describe, expect, expectTypeOf, it, vi } from 'vitest'
import {
  agentIpcArgumentSchemas,
  agentIpcMethods,
  agentPrivacySchema,
  agentScopeToQueryScope,
  type AgentBridge,
  type AgentIpcMap,
  type DesktopBridge,
  type DesktopIpcMap,
} from '@ontolearn/contracts'
import { matchesBusiness3Response, validateBusiness3, v2Registry } from '@ontolearn/contracts/v2'
import {
  registerDesktopIpc,
  type DesktopIpcDependencies,
} from '../../apps/desktop/src/main/desktop-ipc'
import { business3 } from '../../packages/contracts/v2/fixtures.json'

const projectId = '00000000-0000-4000-8000-000000000001'
const operationId = '00000000-0000-4000-8000-000000000002'
const confirmationRef = '00000000-0000-4000-8000-000000000003'
const sha256 = 'a'.repeat(64)
const confirmation = {
  projectId,
  confirmationRef,
  previewHash: sha256,
  preparedPlanRef: sha256,
  inputSnapshotId: sha256,
  parametersHash: sha256,
}

const agentArgs = {
  'agent:context': { projectId, module: 'ontology', selectedObjectIds: ['001'] },
  'agent:set-mode': { projectId, mode: 'project' },
  'agent:dispatch': {
    operationId,
    module: 'ontology',
    mode: 'project',
    scope: 'asserted',
    question: '  概念如何关联？  ',
    selectedObjectIds: ['001'],
  },
  'agent:state': { projectId },
  'agent:cancel': { exchangeId: 1 },
  'agent:draft-plan': { operationId },
  'agent:commit-draft': { operationId, draftType: 'ontology', confirmation },
  'agent:audit': { projectId, limit: 10 },
  'agent-model:set-enabled': { configurationId: projectId, enabled: false },
  'agent-model:remove': { configurationId: projectId },
  'agent-model:probe': { configurationId: projectId, scope: 'synthetic' },
} satisfies { [K in keyof AgentIpcMap]: AgentIpcMap[K]['args'][0] }

const ontologyChannels = ['project:ontology-export', 'project:ontology-import-check'] as const
const internalMethod = 'project.agent.before_commit'
const methods = ['project.ontology.export', 'project.ontology.import.check', internalMethod]

describe('Agent vocabulary', () => {
  it('has one scope mapping and one spelling for the middle privacy level', () => {
    expect(agentScopeToQueryScope('asserted', '')).toEqual({
      scope: 'asserted',
      selection: { kind: 'current' },
    })
    expect(agentScopeToQueryScope('asserted-and-derived', '')).toEqual({
      scope: 'asserted+derived',
      selection: { kind: 'current' },
    })
    expect(agentScopeToQueryScope('selected-history', '001')).toEqual({
      scope: 'asserted',
      selection: { kind: 'historical', snapshotId: '001' },
    })
    expect(agentPrivacySchema.options).toEqual(['local', 'minimal', 'project'])
  })

  it('preserves generated host snapshot IDs byte-for-byte and rejects blank IDs', () => {
    for (let n = 0; n < 256; n++) {
      const ids = [String(n).padStart(3, '0'), n.toString(16).padStart(64, '0'), ` A${n}中 `]
      for (const snapshotId of ids) {
        const result = agentScopeToQueryScope('selected-history', snapshotId)
        expect(result.scope).toBe('asserted')
        expect(result.selection).toEqual({ kind: 'historical', snapshotId })
      }
    }
    for (const blank of ['', ' ', '\t\n', '\u3000', null, undefined])
      expect(() => agentScopeToQueryScope('selected-history', blank as string)).toThrow(
        'AGENT_SNAPSHOT_REQUIRED',
      )
  })
})

describe('business3 wire contract', () => {
  const cases = business3.cases.filter(
    (entry) => typeof entry.value.method === 'string' && methods.includes(entry.value.method),
  )
  const bindings = business3.responses.filter((entry) => methods.includes(entry.request.method))
  it.each(cases)('$name', ({ schema, value, valid }) => {
    expect(validateBusiness3(schema, value)).toBe(valid)
    expect(validateBusiness3('envelope', value)).toBe(valid)
    if ('params' in value)
      expect(validateBusiness3('params_' + value.method, value.params)).toBe(valid)
    if ('result' in value)
      expect(validateBusiness3('result_' + value.method, value.result)).toBe(valid)
  })
  it.each(bindings)('$name', ({ request, response, valid }) => {
    expect(matchesBusiness3Response(request, response, business3.registryHash)).toBe(valid)
  })

  it('keeps the existing model routes and confines the checkpoint to business3', () => {
    expect(v2Registry.mainRuntime).toEqual([
      'getModelAccessStatus',
      'configureModel',
      'storeModelCredential',
      'setModelPrivacy',
      'selectModelResults',
      'getModelFieldCatalog',
      'selectModelFields',
      'previewModelExplanation',
      'confirmModelAuthorization',
      'startModelExplanation',
      'getModelExplanationOutcome',
      'cancelModelExplanation',
    ])
    const { methods: registered, mainlineProjectMethods } = v2Registry.foundationProfiles.business3
    expect(registered).toEqual(expect.arrayContaining(methods))
    expect(mainlineProjectMethods).toEqual(expect.arrayContaining(methods.slice(0, 2)))
    expect(mainlineProjectMethods).not.toContain(internalMethod)
    expect(v2Registry.projectAgentBeforeCommit).toMatchObject({
      method: internalMethod,
      agentEligible: false,
      exposure: 'main-process-only',
    })
    expect(
      validateBusiness3('params_project.checkpoint.create', {
        projectId,
        operationId,
        label: null,
        reason: 'before-agent',
      }),
    ).toBe(false)
  })
})

type Handler = (event: IpcMainInvokeEvent, ...raw: unknown[]) => Promise<unknown>
const trusted = {} as IpcMainInvokeEvent
const foreign = {} as IpcMainInvokeEvent
function register(options: Partial<DesktopIpcDependencies> = {}) {
  const handlers = new Map<string, Handler>()
  registerDesktopIpc({
    ipcMain: {
      handle: (channel: string, fn: Handler) => handlers.set(channel, fn),
    } as DesktopIpcDependencies['ipcMain'],
    trusted: (event) => event === trusted,
    tasks: {} as DesktopIpcDependencies['tasks'],
    supervisor: {} as DesktopIpcDependencies['supervisor'],
    ...options,
  })
  return handlers
}

describe('named desktop IPC and preload', () => {
  it('aligns bridge signatures, registrations, and actual preload invocations', async () => {
    expectTypeOf<(typeof agentIpcMethods)[keyof AgentIpcMap]>().toEqualTypeOf<keyof AgentBridge>()
    expectTypeOf<Pick<DesktopIpcMap, keyof AgentIpcMap>>().toEqualTypeOf<AgentIpcMap>()
    expectTypeOf<Pick<DesktopBridge, keyof AgentBridge>>().toEqualTypeOf<AgentBridge>()
    expectTypeOf<
      'recordAgentBeforeCommit' extends keyof DesktopBridge ? true : false
    >().toEqualTypeOf<false>()
    expectTypeOf<
      typeof internalMethod extends keyof DesktopIpcMap ? true : false
    >().toEqualTypeOf<false>()

    const handlers = register()
    const agentRoutes = [...handlers.keys()].filter((name) => /^agent(?:-model)?:/.test(name))
    expect(agentRoutes.sort()).toEqual(Object.keys(agentIpcMethods).sort())
    expect(agentRoutes).toHaveLength(11)
    expect(handlers.has(internalMethod)).toBe(false)
    for (const channel of ontologyChannels) expect(handlers.has(channel)).toBe(true)

    let bridge: DesktopBridge | undefined
    const invoke = vi.fn(async (channel: string, ...args: unknown[]) => {
      if (ontologyChannels.some((name) => name === channel))
        return { deliveryVersion: 1, deliveryId: operationId, payload: { ok: true, data: channel } }
      if (channel === 'project:reply-received')
        return { deliveryVersion: 1, deliveryId: operationId, accepted: true }
      return handlers.get(channel)!(trusted, ...args)
    })
    vi.doMock('electron', () => ({
      contextBridge: {
        exposeInMainWorld: (_name: string, value: DesktopBridge) => {
          bridge = value
        },
      },
      ipcRenderer: { invoke },
    }))
    try {
      await import('../../apps/desktop/src/preload/index')
      expect(bridge).toBeDefined()
      expect(
        Object.keys(bridge!)
          .filter((key) => /checkpoint/i.test(key))
          .sort(),
      ).toEqual(['createProjectCheckpoint', 'listProjectCheckpoints'])
      expect(bridge).not.toHaveProperty('recordAgentBeforeCommit')
      expect(bridge).not.toHaveProperty(internalMethod)
      for (const channel of Object.keys(agentIpcMethods) as Array<keyof AgentIpcMap>) {
        const method = bridge![agentIpcMethods[channel]] as (args: unknown) => Promise<unknown>
        await method(agentArgs[channel])
        expect(invoke).toHaveBeenLastCalledWith(channel, agentArgs[channel])
      }
      await expect(bridge!.exportProjectOntology({})).resolves.toEqual({
        ok: true,
        data: 'project:ontology-export',
      })
      const input = { baseUri: 'urn:test:', turtleText: '' }
      await expect(bridge!.checkProjectOntologyImport(input)).resolves.toEqual({
        ok: true,
        data: 'project:ontology-import-check',
      })
      expect(invoke.mock.calls.slice(-4)).toEqual([
        ['project:ontology-export'],
        ['project:reply-received', { deliveryVersion: 1, deliveryId: operationId }],
        ['project:ontology-import-check', input],
        ['project:reply-received', { deliveryVersion: 1, deliveryId: operationId }],
      ])
    } finally {
      vi.doUnmock('electron')
    }
  })

  it('checks trust and strict arguments before service lookup on all 11 routes', async () => {
    const getAgent = vi.fn(() => undefined)
    const handlers = register({ getAgent })
    for (const channel of Object.keys(agentIpcMethods) as Array<keyof AgentIpcMap>) {
      const invoke = handlers.get(channel)!
      const args = agentArgs[channel]
      expect(agentIpcArgumentSchemas[channel].safeParse(args).success).toBe(true)
      await expect(invoke(foreign, args)).resolves.toMatchObject({
        ok: false,
        error: { code: 'PERMISSION_DENIED' },
      })
      for (const malformed of [null, [], 42, { ...args, inputSnapshotId: sha256 }])
        await expect(invoke(trusted, malformed)).resolves.toMatchObject({
          ok: false,
          error: { code: 'INVALID_REQUEST' },
        })
      await expect(invoke(trusted, args, args)).resolves.toMatchObject({
        ok: false,
        error: { code: 'INVALID_REQUEST' },
      })
    }
    const commit = agentArgs['agent:commit-draft']
    await expect(
      handlers.get('agent:commit-draft')!(trusted, {
        ...commit,
        confirmation: { ...confirmation, previewHash: 'unbound' },
      }),
    ).resolves.toMatchObject({ ok: false, error: { code: 'INVALID_REQUEST' } })
    for (const channel of ontologyChannels)
      await expect(handlers.get(channel)!(foreign)).resolves.toMatchObject({
        ok: false,
        error: { code: 'PERMISSION_DENIED' },
      })
    expect(getAgent).not.toHaveBeenCalled()
  })

  it('denies persistence and external actions during switch, management and restore', async () => {
    const getAgent = vi.fn(() => undefined)
    const blockers = [
      { library: { switching: true } as DesktopIpcDependencies['library'] },
      { projects: { managementBlocked: true } as DesktopIpcDependencies['projects'] },
      { projects: { restoreBlocked: true } as DesktopIpcDependencies['projects'] },
    ]
    const blockedRoutes = [
      'agent:set-mode',
      'agent:dispatch',
      'agent:commit-draft',
      'agent-model:set-enabled',
      'agent-model:remove',
      'agent-model:probe',
    ] as const
    for (const blocker of blockers) {
      const handlers = register({ getAgent, ...blocker })
      for (const channel of blockedRoutes)
        await expect(handlers.get(channel)!(trusted, agentArgs[channel])).resolves.toMatchObject({
          ok: false,
          error: { code: 'PERMISSION_DENIED' },
        })
    }
    expect(getAgent).not.toHaveBeenCalled()
  })

  it('returns empty local state or fixed errors until the optional service is installed', async () => {
    const handlers = register()
    await expect(
      handlers.get('agent:context')!(trusted, agentArgs['agent:context']),
    ).resolves.toMatchObject({
      ok: true,
      data: {
        projectId: null,
        module: 'ontology',
        privacy: 'local',
        modelReady: false,
        capabilities: {
          connection: 'not-run',
          structuredOutput: 'not-run',
          toolRoundTrip: 'not-run',
          mode: 'unverified',
        },
        configurations: [],
        selectedObjectIds: [],
      },
    })
    await expect(handlers.get('agent:state')!(trusted)).resolves.toMatchObject({
      ok: true,
      data: { status: 'idle', context: null, receipts: [] },
    })
    await expect(handlers.get('agent:audit')!(trusted)).resolves.toEqual({
      ok: true,
      data: { items: [] },
    })
    for (const channel of [
      'agent:set-mode',
      'agent:cancel',
      'agent:draft-plan',
      'agent:commit-draft',
    ] as const)
      await expect(handlers.get(channel)!(trusted, agentArgs[channel])).resolves.toMatchObject({
        ok: false,
        error: { code: 'TOOL_UNAVAILABLE', params: {}, retryable: false },
      })
    for (const channel of [
      'agent:dispatch',
      'agent-model:set-enabled',
      'agent-model:remove',
      'agent-model:probe',
    ] as const)
      await expect(handlers.get(channel)!(trusted, agentArgs[channel])).resolves.toMatchObject({
        ok: false,
        error: { code: 'MODEL_UNAVAILABLE', params: {}, retryable: false },
      })
  })

  it('forwards a validated question to the optional service exactly once without trimming it', async () => {
    const dispatchAgentQuestion = vi
      .fn<AgentBridge['dispatchAgentQuestion']>()
      .mockResolvedValue({ ok: true, data: { operationId, exchangeId: 1 } })
    const unused = () => {
      throw new Error('unexpected service method')
    }
    const getAgent = (): AgentBridge => ({
      getAgentContext: unused,
      setAgentMode: unused,
      dispatchAgentQuestion,
      getAgentState: unused,
      cancelAgentExchange: unused,
      buildAgentDraftPlan: unused,
      commitAgentDraft: unused,
      listAgentAudit: unused,
      setModelConfigurationEnabled: unused,
      removeModelConfiguration: unused,
      probeModelCapabilities: unused,
    })
    const invoke = register({ getAgent }).get('agent:dispatch')!
    await expect(invoke(trusted, agentArgs['agent:dispatch'])).resolves.toEqual({
      ok: true,
      data: { operationId, exchangeId: 1 },
    })
    expect(dispatchAgentQuestion).toHaveBeenCalledExactlyOnceWith(agentArgs['agent:dispatch'])
  })
})
