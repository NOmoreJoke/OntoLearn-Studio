import { randomUUID } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import type { EngineConnectionState } from '../../apps/desktop/src/main/engine'
import {
  safeError,
  type JobView,
  type SemanticRunOptions,
  type TaskUpdate,
} from '@ontolearn/contracts'
import { validateV2 } from '../../packages/contracts/src/v2'

const projectId = '00000000-0000-4000-8000-000000000001'
const otherProject = '00000000-0000-4000-8000-000000000099'
const session = '00000000-0000-4000-8000-000000000002'
const current: SemanticRunOptions = {
  definitionId: 'Q01',
  scope: 'asserted',
  inputSelection: 'current',
  inputSnapshotId: null,
  derivedResultId: null,
}
class Engine {
  engineSessionId: string | undefined = session
  calls: Array<{ method: string; params: Record<string, unknown> }> = []
  jobs = new Map<string, JobView>()
  failure: unknown
  start?: (params: Record<string, unknown>) => Promise<unknown>
  subscriptionFailure = false
  onNotification(listener: (value: unknown) => void) {
    void listener
    return () => {}
  }
  onConnectionState(listener: (value: EngineConnectionState) => void) {
    void listener
    return () => {}
  }
  accepted(params: Record<string, unknown>): JobView {
    const template = structuredClone(
      fixtures.cases.find((item) => item.name === 'job running')!.value,
    ) as JobView
    const inputSnapshotId = String(params.inputSnapshotId ?? 'a'.repeat(64))
    const job: JobView = {
      ...template,
      jobId: randomUUID(),
      projectId: String(params.projectId),
      operationId: String(params.operationId),
      capability: params.capability,
      inputSnapshotId,
      scope: params.scope,
      state: 'queued',
      stateVersion: 1,
      commitProgress: { mode: 'none' },
      input: {
        inputSnapshotId,
        definitionId: params.definitionId,
        scope: params.scope,
        parametersHash: template.parametersHash,
        preparedPlanRef: null,
        derivedResultIds: params.derivedResultId ? [params.derivedResultId] : [],
      },
    }
    expect(validateV2('job', job)).toBe(true)
    this.jobs.set(job.jobId, job)
    return job
  }
  async request(method: string, params: Record<string, unknown>): Promise<unknown> {
    this.calls.push({ method, params: structuredClone(params) })
    if (this.failure) throw this.failure
    if (method === 'semantic.start') return this.start ? this.start(params) : this.accepted(params)
    if (method === 'project.get')
      return {
        projectId: params.projectId,
        projectRevision: 1,
        inputSnapshotId: 'a'.repeat(64),
        dependencyVector: { 'facts:asserted': 1 },
        formatVersion: 2,
      }
    if (method === 'job.get') return structuredClone(this.jobs.get(String(params.jobId)))
    if (method === 'job.subscribe') {
      if (this.subscriptionFailure) throw { error: safeError(undefined) }
      return {
        projectId: params.projectId,
        jobId: params.jobId,
        subscriptionId: randomUUID(),
        seq: 0,
        stateVersion: this.jobs.get(String(params.jobId))!.stateVersion,
      }
    }
    if (method === 'job.unsubscribe')
      return { subscriptionId: params.subscriptionId, unsubscribed: true }
    throw new Error('unexpected engine method')
  }
}
function setup(selected = true) {
  const engine = new Engine()
  const service = new TaskService(engine)
  if (selected) service.selectProject(projectId)
  const updates: TaskUpdate[] = []
  service.attachView((value) => updates.push(value))
  return { engine, service, updates }
}

describe('business named semantic bridge', () => {
  it.each([
    ['runSavedQuery', 'query.execute'],
    ['runReasoning', 'reasoning.execute'],
    ['runValidation', 'validation.execute'],
  ] as const)(
    'binds %s to the authorized project and a main-generated operation',
    async (method, capability) => {
      const { engine, service } = setup()
      const result = await service[method]({ ...current, scope: 'asserted', derivedResultId: null })
      expect(result.ok).toBe(true)
      const starts = engine.calls.filter((call) => call.method === 'semantic.start')
      expect(starts).toHaveLength(1)
      expect(starts[0].params).toEqual({
        ...current,
        projectId,
        capability,
        operationId: expect.stringMatching(/^[0-9a-f-]{36}$/),
      })
      expect(validateV2('params_semantic.start', starts[0].params)).toBe(true)
      const restored = await service.restore()
      expect(restored.ok && restored.data.jobs).toEqual(result.ok ? [result.data] : [])
      service.dispose()
    },
  )
  it('accepts the first engine session established by the single create request', async () => {
    const { engine, service } = setup()
    engine.engineSessionId = undefined
    engine.start = async (params) => {
      engine.engineSessionId = session
      return engine.accepted(params)
    }
    expect((await service.runSavedQuery(current)).ok).toBe(true)
    expect(engine.calls.filter((call) => call.method === 'semantic.start')).toHaveLength(1)
    service.dispose()
  })
  it('retains explicit historical and existing-derived selections exactly', async () => {
    const { engine, service } = setup()
    const options: SemanticRunOptions = {
      ...current,
      inputSelection: 'historical',
      inputSnapshotId: 'b'.repeat(64),
      scope: 'asserted+derived',
      derivedResultId: randomUUID(),
    }
    expect((await service.runValidation(options)).ok).toBe(true)
    expect(engine.calls[0].params).toMatchObject(options)
    service.dispose()
  })
  it.each([
    { projectId: otherProject },
    { operationId: randomUUID() },
    { path: '/private/project' },
    { graph: 'raw data' },
    { capability: 'test.read' },
    { libraryOptions: {} },
    { definitionId: '../query' },
    { definitionId: '' },
    { definitionId: 'x'.repeat(129) },
    { scope: 'scenario' },
    { inputSelection: undefined },
    { inputSelection: 'historical', inputSnapshotId: null },
    { inputSelection: 'current', inputSnapshotId: 'a'.repeat(64) },
    { inputSelection: 'historical', inputSnapshotId: 'A'.repeat(64) },
    { scope: 'asserted+derived', derivedResultId: null },
    { scope: 'asserted', derivedResultId: randomUUID() },
  ])(
    'rejects untrusted or inconsistent renderer options %j before engine access',
    async (change) => {
      const { engine, service } = setup()
      const result = await service.runSavedQuery({ ...current, ...change } as SemanticRunOptions)
      expect(result).toEqual({
        ok: false,
        error: {
          code: 'INVALID_REQUEST',
          messageKey: 'protocol.invalidRequest',
          params: { field: 'params' },
          retryable: false,
        },
      })
      expect(engine.calls).toEqual([])
      service.dispose()
    },
  )
  it('rejects derived reasoning even if the typed caller is bypassed', async () => {
    const { engine, service } = setup()
    expect(
      (
        await service.runReasoning({
          ...current,
          scope: 'asserted+derived',
          derivedResultId: randomUUID(),
        } as never)
      ).ok,
    ).toBe(false)
    expect(engine.calls).toEqual([])
    service.dispose()
  })
  it('does not create tasks without a trusted active project', async () => {
    const { engine, service } = setup(false)
    expect((await service.runSavedQuery(current)).ok).toBe(false)
    expect(engine.calls).toEqual([])
    service.dispose()
  })
  it('creates a fresh operation for each explicit invocation without reusing an operation', async () => {
    const { engine, service } = setup()
    await service.runSavedQuery(current)
    await service.runSavedQuery(current)
    const starts = engine.calls.filter((call) => call.method === 'semantic.start')
    expect(starts).toHaveLength(2)
    expect(starts[0].params.operationId).not.toBe(starts[1].params.operationId)
    service.dispose()
  })
  it('preserves safe transport errors and never automatically retries admission', async () => {
    const { engine, service, updates } = setup()
    const error = {
      code: 'TIMEOUT',
      messageKey: 'job.timeout',
      params: { phase: 'request' },
      retryable: true,
    }
    engine.failure = { error, message: '/private/path secret' }
    expect(await service.runSavedQuery(current)).toEqual({ ok: false, error })
    expect(engine.calls.map((call) => call.method)).toEqual(['semantic.start'])
    expect(updates).toEqual([])
    engine.failure = undefined
    expect((await service.restore()).ok).toBe(true)
    expect(engine.calls.filter((call) => call.method === 'semantic.start')).toHaveLength(1)
    service.dispose()
  })
  it('does not disguise accepted work as rejected when its read subscription fails', async () => {
    const { engine, service } = setup()
    engine.subscriptionFailure = true
    const result = await service.runSavedQuery(current)
    expect(result.ok).toBe(true)
    engine.subscriptionFailure = false
    const restored = await service.restore()
    expect(restored.ok && restored.data.jobs).toEqual(result.ok ? [result.data] : [])
    expect(engine.calls.filter((call) => call.method === 'semantic.start')).toHaveLength(1)
    service.dispose()
  })
  it.each(['view', 'project', 'session'] as const)(
    'fences a late admitted job across a %s change and keeps history discoverable',
    async (change) => {
      const { engine, service, updates } = setup()
      let release!: (value: unknown) => void
      let captured!: Record<string, unknown>
      engine.start = (params) => {
        captured = params
        return new Promise((done) => {
          release = done
        })
      }
      const pending = service.runSavedQuery(current)
      if (change === 'view') service.attachView((value) => updates.push(value))
      if (change === 'project') {
        service.selectProject(otherProject)
        service.attachView((value) => updates.push(value))
      }
      if (change === 'session') engine.engineSessionId = randomUUID()
      const accepted = engine.accepted(captured)
      release(accepted)
      expect((await pending).ok).toBe(false)
      expect(updates).toEqual([])
      if (change === 'project') {
        const other = await service.restore()
        expect(other.ok && other.data.jobs).toEqual([])
        service.selectProject(projectId)
      }
      const restored = await service.restore()
      expect(restored.ok && restored.data.jobs).toEqual([accepted])
      expect(engine.calls.filter((call) => call.method === 'semantic.start')).toHaveLength(1)
      service.dispose()
    },
  )
  it.each([
    'projectId',
    'operationId',
    'capability',
    'scope',
    'definitionId',
    'derivedResultIds',
    'snapshot',
  ] as const)('rejects a mismatched %s in an otherwise valid admission', async (field) => {
    const { engine, service } = setup()
    engine.start = async (params) => {
      const job = engine.accepted(params)
      if (field === 'projectId') job.projectId = otherProject
      if (field === 'operationId') job.operationId = randomUUID()
      if (field === 'capability') job.capability = 'validation.execute'
      if (field === 'scope') {
        job.scope = 'asserted+derived'
        ;(job.input as Record<string, unknown>).scope = job.scope
      }
      if (field === 'definitionId') (job.input as Record<string, unknown>).definitionId = 'OTHER'
      if (field === 'derivedResultIds')
        (job.input as Record<string, unknown>).derivedResultIds = [randomUUID()]
      if (field === 'snapshot') {
        job.inputSnapshotId = 'c'.repeat(64)
        ;(job.input as Record<string, unknown>).inputSnapshotId = job.inputSnapshotId
      }
      return job
    }
    const result = await service.runSavedQuery({
      ...current,
      inputSelection: 'historical',
      inputSnapshotId: 'b'.repeat(64),
    })
    expect(result).toEqual({ ok: false, error: safeError(undefined) })
    expect(engine.calls.map((call) => call.method)).toEqual(['semantic.start'])
    service.dispose()
  })
  it('exports only named semantic methods through preload and the checked main routing table', () => {
    const preload = readFileSync('apps/desktop/src/preload/index.ts', 'utf8')
    const main = readFileSync('apps/desktop/src/main/index.ts', 'utf8')
    for (const [method, channel] of [
      ['runSavedQuery', 'semantic:query'],
      ['runReasoning', 'semantic:reasoning'],
      ['runValidation', 'semantic:validation'],
    ]) {
      expect(preload).toContain(`${method}: (options) => ipcRenderer.invoke('${channel}', options)`)
      expect(main).toContain(`'${channel}': (options) => tasks.${method}(options)`)
    }
    expect(preload).not.toContain('semantic.start')
    expect(preload).not.toContain('invoke:')
    expect(main).toContain('trusted(event) ? handler(argument as never) : permission()')
  })
})
