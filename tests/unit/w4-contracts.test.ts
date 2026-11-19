import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import type { IpcMainInvokeEvent } from 'electron'
import { describe, expect, expectTypeOf, it, vi } from 'vitest'
import {
  type BehaviorBridge,
  type DesktopBridge,
  type DesktopIpcMap,
  type MappingBridge,
  type ScenarioBridge,
  type TransferBridge,
  BehaviorAdapterContract,
  behaviorPublicErrorKeys,
  defaultProjectPackageOptions,
  mappingPublicIssueKeys,
  projectPackageCoreRoles,
  projectPackageRoleOptions,
} from '../../packages/contracts/src'
import {
  matchesBusiness3Response,
  validateBusiness3,
  v2Registry,
} from '../../packages/contracts/src/v2'
import errors from '../../packages/contracts/v2/errors.json'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import regressions from '../../packages/contracts/v2/binding-regressions.json'
import {
  registerDesktopIpc,
  type DesktopIpcDependencies,
} from '../../apps/desktop/src/main/desktop-ipc'

const registryHash = createHash('sha256')
  .update(readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)))
  .digest('hex')
const privateMethod = 'project.run.before_commit'
const privateAgentMethod = 'project.agent.before_commit'
const publicRoutes = {
  'project:mapping-source-select': 'selectMappingSource',
  'project:mapping-preview': 'previewMapping',
  'project:mapping-prepare-commit': 'prepareMappingCommit',
  'project:mapping-draft-read': 'readMappingDraft',
  'project:mapping-draft-save': 'saveMappingDraft',
  'project:behavior-run': 'runBehaviorSample',
  'project:behavior-read': 'readBehaviorRun',
  'project:behavior-cancel': 'cancelBehaviorRun',
  'project:scenario-create': 'createScenario',
  'project:scenario-copy': 'copyScenario',
  'project:scenario-list': 'listScenarios',
  'project:scenario-read': 'readScenario',
  'project:scenario-run-read': 'readScenarioRun',
  'project:scenario-run': 'startScenarioRun',
  'project:scenario-cancel': 'cancelScenarioRun',
  'project:scenario-resume': 'resumeScenarioRun',
  'project:scenario-compare': 'compareScenarioRuns',
  'project:scenario-run-delete': 'deleteScenarioRun',
  'project:scenario-restore': 'restoreScenarioBaseline',
  'project:transfer-package-export-check': 'checkProjectPackageExport',
  'project:transfer-package-export': 'exportProjectPackage',
  'project:transfer-package-import-check': 'checkProjectPackageImport',
  'project:transfer-package-import': 'importProjectPackage',
  'project:transfer-report-prepare': 'prepareProjectHtmlReport',
  'project:transfer-report-export': 'exportProjectHtmlReport',
  'project:transfer-select': 'selectTransferFile',
} as const satisfies Partial<Record<keyof DesktopIpcMap, keyof DesktopBridge>>
type Route = keyof typeof publicRoutes
type Wave4Bridge = MappingBridge & BehaviorBridge & ScenarioBridge & TransferBridge
const routes = Object.keys(publicRoutes) as Route[]
const readRoutes = new Set<Route>([
  'project:mapping-draft-read',
  'project:behavior-read',
  'project:scenario-list',
  'project:scenario-read',
  'project:scenario-run-read',
  'project:scenario-compare',
])

describe('Wave 4 business3 freeze', () => {
  const cases = fixtures.cases.filter((c) => c.name.startsWith('W4 '))
  const bindings = fixtures.business3.responses.filter((c) => c.name.startsWith('W4 '))
  it.each(cases)('$name', ({ schema, value, valid }) => {
    expect(validateBusiness3(schema, value)).toBe(valid)
  })
  it.each(fixtures.wave4Raw)('$name', ({ schema, wireUtf8, valid }) => {
    // Preserve own keys that may carry special meaning in JS object literals.
    expect(validateBusiness3(schema, JSON.parse(wireUtf8))).toBe(valid)
  })
  it.each([...bindings, ...regressions.wave4])('$name', ({ request, response, valid }) => {
    expect(matchesBusiness3Response(request, response, registryHash)).toBe(valid)
  })
  it('covers every new method on both sides of the envelope', () => {
    expect(fixtures.business3.registryHash).toBe(registryHash)
    expect(new Set(bindings.map(({ request }) => request.method))).toEqual(
      new Set(Object.keys(v2Registry.wave4ResponseBindings)),
    )
    const profile = v2Registry.foundationProfiles.business3
    for (const method of [
      ...v2Registry.projectMapping.methods,
      ...v2Registry.projectBehavior.methods,
      ...v2Registry.projectScenario.methods,
      ...v2Registry.projectTransfer.methods,
    ]) {
      expect(profile.methods).toContain(method)
      expect(profile.mainlineProjectMethods).toContain(method)
    }
    expect(profile.methods).toContain(privateMethod)
    expect(profile.mainlineProjectMethods).not.toContain(privateMethod)
    expect(profile.mainlineProjectMethods).not.toContain(privateAgentMethod)
    expect(v2Registry.projectRunBeforeCommit).toEqual({
      profile: 'business3',
      method: privateMethod,
      agentEligible: false,
      exposure: 'main-process-only',
    })
  })
  it('leaves manual checkpoints and the existing model and capability boundaries intact', () => {
    const params = {
      projectId: '00000000-0000-4000-8000-000000000001',
      operationId: '00000000-0000-4000-8000-000000000002',
      label: null,
    }
    expect(validateBusiness3('params_project.checkpoint.create', params)).toBe(true)
    for (const reason of ['before-run', 'before-agent', 'guided-stage']) {
      expect(validateBusiness3('params_project.checkpoint.create', { ...params, reason })).toBe(
        false,
      )
    }
    expect(v2Registry.mainRuntime).toHaveLength(12)
    expect(Object.keys(v2Registry.mainCapabilities).sort()).toEqual(
      [...v2Registry.mainRuntime].sort(),
    )
    for (const cap of ['mapping.commit', 'behavior.test', 'scenario.run'] as const) {
      expect(v2Registry.capabilities[cap].implementation).toBe('design-only')
    }
  })
  it('freezes B-01 and B-02 condition lowering with deterministic unsupported results', () => {
    const subject = { kind: 'value', value: { kind: 'iri', value: 'urn:equipment/001' } } as const
    const value = { kind: 'value', value: { kind: 'string', value: 'High' } } as const
    const typeCondition = { op: 'type', subject, classId: 'urn:HighRiskEquipment' } as const
    expect(BehaviorAdapterContract.trigger).toEqual({
      trigger: 'eventType',
      eventType: 'event_type',
      eventId: 'event_id',
    })
    expect(BehaviorAdapterContract.lowerCondition(typeCondition, true)).toEqual({
      ok: true,
      condition: {
        op: 'has',
        subject,
        property: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
        value: { kind: 'value', value: { kind: 'iri', value: 'urn:HighRiskEquipment' } },
      },
    })
    expect(
      BehaviorAdapterContract.lowerCondition(
        { op: 'equals', subject, property: 'urn:level', value },
        false,
      ),
    ).toEqual({ ok: true, condition: { op: 'has', subject, property: 'urn:level', value } })
    for (const unsupported of [
      typeCondition,
      { op: 'exists', subject, property: 'urn:level' },
    ] as const) {
      expect(BehaviorAdapterContract.lowerCondition(unsupported, false)).toEqual({
        ok: false,
        error: { code: 'unavailable', messageKey: 'behavior.unavailable' },
      })
    }
    expect(BehaviorAdapterContract.actions.update).toMatchObject({
      kind: 'set',
      cardinality: 'one',
    })
    expect(BehaviorAdapterContract.actions.relate).toMatchObject({
      kind: 'add',
      cardinality: 'many',
    })
  })
  it('projects only allowlisted errors and package roles', () => {
    expect(behaviorPublicErrorKeys).toEqual(errors.wave4.behaviorPublicMessageKeys)
    expect(mappingPublicIssueKeys).toEqual(errors.wave4.mappingIssueMessageKeys)
    for (const [reason, code, phase] of [
      ['competing_write', 'conflict', 'run'],
      ['invalid_shape', 'invalid_input', 'run'],
      ['unavailable_condition', 'unavailable', 'run'],
      [new Error('/private/engine'), 'execution_failed', 'run'],
      [{ evidence: 'private record' }, 'cancel_failed', 'cancel'],
    ] as const) {
      const error = BehaviorAdapterContract.projectError(reason, phase)
      expect(error).toEqual({ code, messageKey: behaviorPublicErrorKeys[code] })
      expect(validateBusiness3('w4.behavior.error', { ...error, evidence: {} })).toBe(false)
    }
    expect(defaultProjectPackageOptions).toEqual({
      agentSessions: false,
      rawSources: false,
      derived: false,
      history: false,
    })
    expect(projectPackageCoreRoles).toEqual([
      'definitions',
      'assertions',
      'ownership',
      'checkpoint',
    ])
    expect(projectPackageRoleOptions).toEqual({
      agentSessions: 'agent-session',
      rawSources: 'raw-source',
      derived: 'derived',
      history: 'history',
    })
    expect(v2Registry.projectTransfer.packageRoleOptions).toEqual(projectPackageRoleOptions)
    expect(
      new Set([...projectPackageCoreRoles, ...Object.values(projectPackageRoleOptions)]),
    ).toHaveProperty('size', 8)
  })
})

type Handler = (event: IpcMainInvokeEvent, ...args: unknown[]) => Promise<unknown>
const trusted = {} as IpcMainInvokeEvent
const foreign = {} as IpcMainInvokeEvent

function register(options: Partial<DesktopIpcDependencies> = {}) {
  const handlers = new Map<string, Handler>()
  registerDesktopIpc({
    ipcMain: { handle: (channel: string, fn: Handler) => handlers.set(channel, fn) },
    trusted: (event) => event === trusted,
    tasks: {} as DesktopIpcDependencies['tasks'],
    supervisor: {} as DesktopIpcDependencies['supervisor'],
    ...options,
  })
  return handlers
}

describe('Wave 4 named preload and guarded registration', () => {
  it('exposes exactly the typed Wave 4 methods and preserves the delivery acknowledgment', async () => {
    expectTypeOf<(typeof publicRoutes)[Route]>().toEqualTypeOf<keyof Wave4Bridge>()
    expectTypeOf<Pick<DesktopBridge, keyof Wave4Bridge>>().toEqualTypeOf<{
      [Key in keyof Wave4Bridge]: Wave4Bridge[Key]
    }>()
    expectTypeOf<
      'recordRunBeforeCommit' extends keyof DesktopBridge ? true : false
    >().toEqualTypeOf<false>()
    expectTypeOf<
      typeof privateMethod extends keyof DesktopIpcMap ? true : false
    >().toEqualTypeOf<false>()
    const registered = register()
    expect(
      [...registered.keys()]
        .filter((key) => /^project:(mapping|behavior|scenario|transfer)-/.test(key))
        .sort(),
    ).toEqual([...routes].sort())
    for (const key of [privateMethod, privateAgentMethod, 'project:run-before-commit']) {
      expect(registered.has(key)).toBe(false)
    }
    expect([...registered.keys()].filter((key) => key.startsWith('model:'))).toHaveLength(12)

    let bridge: DesktopBridge | undefined
    const deliveryId = '00000000-0000-4000-8000-000000000002'
    const invoke = vi.fn(async (channel: string) =>
      channel === 'project:reply-received'
        ? { deliveryVersion: 1, deliveryId, accepted: true }
        : { deliveryVersion: 1, deliveryId, payload: { ok: true, data: channel } },
    )
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
      for (const key of [
        privateMethod,
        privateAgentMethod,
        'recordRunBeforeCommit',
        'recordAgentBeforeCommit',
        'invoke',
      ]) {
        expect(bridge).not.toHaveProperty(key)
      }
      for (const route of routes) {
        invoke.mockClear()
        const method = bridge![publicRoutes[route]] as (args: unknown) => Promise<unknown>
        const args = Object.freeze({ caller: route })
        await expect(method(args)).resolves.toEqual({ ok: true, data: route })
        expect(invoke.mock.calls).toEqual([
          [route, args],
          ['project:reply-received', { deliveryVersion: 1, deliveryId }],
        ])
      }
    } finally {
      vi.doUnmock('electron')
    }
  })

  it('rejects foreign and switching calls before service and fences all mutation paths', async () => {
    const denied = { ok: false, error: { code: 'PERMISSION_DENIED' } }
    const receive = vi.fn(async (work: () => Promise<unknown>) => ({
      value: await work(),
      receipt: {},
    }))
    const service = vi.fn(async () => ({ ok: true, data: {} }))
    const projects = Object.fromEntries(routes.map((route) => [publicRoutes[route], service]))
    const replies = {
      receive,
      binding: () => ({ engineSessionId: 'test' }),
    } as unknown as DesktopIpcDependencies['replies']
    for (const blocked of ['managementBlocked', 'restoreBlocked'] as const) {
      const handlers = register({
        replies,
        projects: { ...projects, [blocked]: true } as unknown as DesktopIpcDependencies['projects'],
      })
      for (const route of routes) {
        receive.mockClear()
        service.mockClear()
        await expect(handlers.get(route)!(foreign, {})).resolves.toMatchObject(denied)
        expect(receive).not.toHaveBeenCalled()
        if (readRoutes.has(route)) {
          await expect(handlers.get(route)!(trusted, {})).resolves.toMatchObject({
            deliveryVersion: 1,
          })
          expect(service).toHaveBeenCalledOnce()
        } else {
          await expect(handlers.get(route)!(trusted, {})).resolves.toMatchObject(denied)
          expect(service).not.toHaveBeenCalled()
          expect(receive).not.toHaveBeenCalled()
        }
      }
    }
    const switched = register({
      replies,
      projects: projects as unknown as DesktopIpcDependencies['projects'],
      library: { switching: true } as DesktopIpcDependencies['library'],
    })
    receive.mockClear()
    for (const route of routes) {
      await expect(switched.get(route)!(trusted, {})).resolves.toMatchObject(denied)
    }
    expect(receive).not.toHaveBeenCalled()

    service.mockClear()
    for (const route of routes) {
      const handlers = register({
        replies,
        projects: projects as unknown as DesktopIpcDependencies['projects'],
      })
      await expect(handlers.get(route)!(trusted, {}, {})).resolves.toMatchObject({
        deliveryVersion: 1,
        payload: { ok: false, error: { code: 'INVALID_REQUEST' } },
      })
    }
    expect(service).not.toHaveBeenCalled()
  })
})
