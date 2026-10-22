import { afterEach, describe, expect, it } from 'vitest'
import {
  safeDisplayError,
  type ResultMetadataDTO,
  type ResultPageDTO,
  type ResultPageOptions,
} from '@ontolearn/contracts'
import { validateV2 } from '../../packages/contracts/src/v2'
import type { EngineConnectionState } from '../../apps/desktop/src/main/engine'
import { TaskService } from '../../apps/desktop/src/main/task-service'

const projectId = '00000000-0000-4000-8000-000000000001'
const otherProjectId = '00000000-0000-4000-8000-000000000011'
const resultId = '00000000-0000-4000-8000-000000000006'
const cursor = '00000000-0000-4000-8000-000000000007'
const snapshot = 'a'.repeat(64)
const parametersHash = 'b'.repeat(64)
function metadata(): ResultMetadataDTO {
  return {
    resultId,
    projectId,
    jobId: '00000000-0000-4000-8000-000000000003',
    kind: 'query',
    definitionId: 'query1',
    inputSnapshotId: snapshot,
    inputProjectRevision: 7,
    dependencyVector: { 'facts:asserted': 7, 'query:query1': 2 },
    definitionSetDigests: { query: 'c'.repeat(64), ontology: 'd'.repeat(64) },
    implementation: {
      executionSemanticsVersion: 'E1',
      engineVersion: '0.1.0',
      dependencyLockHash: 'e'.repeat(64),
    },
    scope: 'asserted',
    parametersHash,
    state: 'current',
    staleReason: [],
    payloadStatus: 'available',
    createdAtMs: 8,
    historicalSelectionRequired: false,
  }
}
function page(): ResultPageDTO {
  return {
    binding: {
      projectId,
      resultId,
      inputSnapshotId: snapshot,
      scope: 'asserted',
      parametersHash,
      order: 'ordinal+rowId:asc',
    },
    rows: [
      {
        rowId: '00000000-0000-4000-8000-000000000021',
        ordinal: 0,
        cells: ['查询😀', null, true, 3.5],
      },
      { rowId: '00000000-0000-4000-8000-000000000022', ordinal: 4, cells: ['', false, -2] },
      { rowId: '00000000-0000-4000-8000-000000000023', ordinal: 9, cells: [0, '末行'] },
    ],
    nextCursor: null,
  }
}
const invalid = {
  ok: false,
  error: {
    code: 'INVALID_REQUEST',
    messageKey: 'protocol.invalidRequest',
    params: { field: 'params' },
    retryable: false,
  },
}
const denied = {
  ok: false,
  error: {
    code: 'PERMISSION_DENIED',
    messageKey: 'permission.denied',
    params: {},
    retryable: false,
  },
}
const internal = {
  ok: false,
  error: { code: 'INTERNAL_ERROR', messageKey: 'engine.internal', params: {}, retryable: false },
}

// A service-layer port only: no owned Supervisor, ready proof, Store, process or IPC.
class LayerEngine {
  engineSessionId: string | undefined = '00000000-0000-4000-8000-000000000002'
  readonly calls: Array<{ method: string; params: Record<string, unknown> }> = []
  readonly notifications = new Set<(value: unknown) => void>()
  readonly states = new Set<(value: EngineConnectionState) => void>()
  metadataResponse: unknown = metadata()
  pageResponse: unknown = page()
  response: ((method: string, params: Record<string, unknown>) => Promise<unknown>) | undefined
  failure: unknown
  onNotification(listener: (value: unknown) => void): () => void {
    this.notifications.add(listener)
    return () => {
      this.notifications.delete(listener)
    }
  }
  onConnectionState(listener: (value: EngineConnectionState) => void): () => void {
    this.states.add(listener)
    return () => {
      this.states.delete(listener)
    }
  }
  async request(method: string, params: Record<string, unknown>): Promise<unknown> {
    this.calls.push({ method, params: structuredClone(params) })
    if (this.response) return await this.response(method, params)
    if (this.failure !== undefined) throw this.failure
    if (method === 'result.get') return structuredClone(this.metadataResponse)
    if (method === 'result.page') return structuredClone(this.pageResponse)
    throw new Error('UNEXPECTED_UNIT_ENGINE_METHOD')
  }
}
const allocated: Array<{ tasks: TaskService; engine: LayerEngine }> = []
function setup(select = true, engine = new LayerEngine()) {
  const tasks = new TaskService(engine)
  if (select) tasks.selectProject(projectId)
  allocated.push({ tasks, engine })
  return { tasks, engine }
}
afterEach(() => {
  for (const { tasks, engine } of allocated.splice(0)) {
    tasks.dispose()
    expect(engine.notifications.size).toBe(0)
    expect(engine.states.size).toBe(0)
  }
})

describe('result service composition with controlled engine responses', () => {
  it('preserves complete metadata, binding and rows across get → get → page', async () => {
    const { tasks, engine } = setup()
    const expectedMetadata = metadata()
    const expectedPage = page()
    expect(validateV2('result_result.get', expectedMetadata)).toBe(true)
    expect(validateV2('result_result.page', expectedPage)).toBe(true)
    const first = await tasks.getResult(resultId)
    const second = await tasks.getResultPage({ resultId, pageSize: 20, cursor: null })
    expect(first).toEqual({ ok: true, data: expectedMetadata })
    expect(second).toEqual({ ok: true, data: expectedPage })
    if (!first.ok || !second.ok) throw new Error('UNIT_RESULT_NOT_SUCCESSFUL')
    expect(Object.keys(first.data).sort()).toEqual(
      [
        'resultId',
        'projectId',
        'jobId',
        'kind',
        'definitionId',
        'inputSnapshotId',
        'inputProjectRevision',
        'dependencyVector',
        'definitionSetDigests',
        'implementation',
        'scope',
        'parametersHash',
        'state',
        'staleReason',
        'payloadStatus',
        'createdAtMs',
        'historicalSelectionRequired',
      ].sort(),
    )
    expect(Object.keys(second.data.binding).sort()).toEqual(
      ['projectId', 'resultId', 'inputSnapshotId', 'scope', 'parametersHash', 'order'].sort(),
    )
    expect(engine.calls).toEqual([
      { method: 'result.get', params: { projectId, resultId } },
      { method: 'result.get', params: { projectId, resultId } },
      {
        method: 'result.page',
        params: { binding: expectedPage.binding, pageSize: 20, cursor: null },
      },
    ])
  })

  it('constructs page binding from the second metadata response', async () => {
    const { tasks, engine } = setup()
    expect(await tasks.getResult(resultId)).toEqual({ ok: true, data: metadata() })
    const next = {
      ...metadata(),
      inputSnapshotId: 'f'.repeat(64),
      scope: 'scenario' as const,
      parametersHash: '9'.repeat(64),
    }
    const nextPage = {
      ...page(),
      binding: {
        ...page().binding,
        inputSnapshotId: next.inputSnapshotId,
        scope: next.scope,
        parametersHash: next.parametersHash,
      },
    }
    engine.metadataResponse = next
    engine.pageResponse = nextPage
    expect(await tasks.getResultPage({ resultId, pageSize: 20, cursor: null })).toEqual({
      ok: true,
      data: nextPage,
    })
    expect(engine.calls).toEqual([
      { method: 'result.get', params: { projectId, resultId } },
      { method: 'result.get', params: { projectId, resultId } },
      { method: 'result.page', params: { binding: nextPage.binding, pageSize: 20, cursor: null } },
    ])
  })

  it.each([1, 200])('transports pageSize %s and cursor with complete binding', async (pageSize) => {
    const { tasks, engine } = setup()
    const firstPage = { ...page(), rows: page().rows.slice(0, 1), nextCursor: cursor }
    engine.pageResponse = firstPage
    expect(await tasks.getResultPage({ resultId, pageSize, cursor: null })).toEqual({
      ok: true,
      data: firstPage,
    })
    const finalPage = { ...page(), rows: page().rows.slice(1, 2) }
    engine.pageResponse = finalPage
    expect(await tasks.getResultPage({ resultId, pageSize, cursor })).toEqual({
      ok: true,
      data: finalPage,
    })
    expect(engine.calls).toEqual([
      { method: 'result.get', params: { projectId, resultId } },
      { method: 'result.page', params: { binding: firstPage.binding, pageSize, cursor: null } },
      { method: 'result.get', params: { projectId, resultId } },
      { method: 'result.page', params: { binding: finalPage.binding, pageSize, cursor } },
    ])
  })

  it('rejects an invalid result ID before any engine request', async () => {
    const { tasks, engine } = setup()
    expect(await tasks.getResult('not-a-uuid')).toEqual(invalid)
    expect(engine.calls).toEqual([])
  })

  const malformedPages: Array<{ name: string; value: unknown }> = [
    { name: 'missing resultId', value: { pageSize: 20, cursor: null } },
    { name: 'missing pageSize', value: { resultId, cursor: null } },
    { name: 'missing cursor', value: { resultId, pageSize: 20 } },
    { name: 'zero', value: { resultId, pageSize: 0, cursor: null } },
    { name: '201', value: { resultId, pageSize: 201, cursor: null } },
    { name: 'fraction', value: { resultId, pageSize: 1.5, cursor: null } },
    { name: 'invalid cursor', value: { resultId, pageSize: 20, cursor: 'not-a-uuid' } },
    {
      name: 'extra projectId',
      value: { resultId, pageSize: 20, cursor: null, projectId: otherProjectId },
    },
    {
      name: 'extra binding',
      value: { resultId, pageSize: 20, cursor: null, binding: page().binding },
    },
    { name: 'extra order', value: { resultId, pageSize: 20, cursor: null, order: 'descending' } },
  ]
  it.each(malformedPages)('rejects $name options before engine access', async ({ value }) => {
    const { tasks, engine } = setup()
    // Deliberately malformed input: retain its actual missing/extra fields at the API boundary.
    const options = value as unknown as ResultPageOptions
    expect(await tasks.getResultPage(options)).toEqual(invalid)
    expect(engine.calls).toEqual([])
  })

  it('denies valid result queries without an active project, with zero engine calls', async () => {
    const { tasks, engine } = setup(false)
    expect(await tasks.getResult(resultId)).toEqual(denied)
    expect(await tasks.getResultPage({ resultId, pageSize: 20, cursor: null })).toEqual(denied)
    expect(engine.calls).toEqual([])
  })

  it.each(['schema', 'project', 'result'] as const)(
    'rejects %s-invalid metadata before requesting a page',
    async (fault) => {
      const { tasks, engine } = setup()
      engine.metadataResponse =
        fault === 'schema'
          ? { resultId }
          : {
              ...metadata(),
              ...(fault === 'project' ? { projectId: otherProjectId } : { resultId: cursor }),
            }
      expect(await tasks.getResultPage({ resultId, pageSize: 20, cursor: null })).toEqual(internal)
      expect(engine.calls).toEqual([{ method: 'result.get', params: { projectId, resultId } }])
    },
  )

  it('fences metadata after project selection changes before any page request', async () => {
    const { tasks, engine } = setup()
    let finish: (value: unknown) => void = () => {
      throw new Error('UNIT_NOT_WAITING')
    }
    engine.response = () =>
      new Promise((resolve) => {
        finish = resolve
      })
    const response = tasks.getResultPage({ resultId, pageSize: 20, cursor: null })
    expect(engine.calls).toEqual([{ method: 'result.get', params: { projectId, resultId } }])
    tasks.selectProject(otherProjectId)
    finish(metadata())
    expect(await response).toEqual(denied)
    expect(engine.calls).toEqual([{ method: 'result.get', params: { projectId, resultId } }])
  })

  it('fences an in-flight page response when its originating view is detached', async () => {
    const { tasks, engine } = setup()
    let finish: ((value: unknown) => void) | undefined
    let started: (() => void) | undefined
    const pageStarted = new Promise<void>((resolve) => {
      started = resolve
    })
    engine.response = async (method) => {
      if (method === 'result.get') return metadata()
      if (method !== 'result.page') throw new Error('UNEXPECTED_UNIT_METHOD')
      started?.()
      return await new Promise((resolve) => {
        finish = resolve
      })
    }
    const response = tasks.getResultPage({ resultId, pageSize: 20, cursor: null })
    await pageStarted
    tasks.detachView()
    if (!finish) throw new Error('UNIT_PAGE_NOT_WAITING')
    finish(page())
    expect(await response).toEqual(denied)
    expect(engine.calls).toEqual([
      { method: 'result.get', params: { projectId, resultId } },
      { method: 'result.page', params: { binding: page().binding, pageSize: 20, cursor: null } },
    ])
  })

  it('projects unsafe legacy port failures to the fixed full safe error', async () => {
    const { tasks, engine } = setup()
    engine.failure = {
      error: {
        code: 'INTERNAL_ERROR',
        messageKey: 'engine.internal',
        params: { path: '/unit-private', cell: 'unit-secret' },
        retryable: false,
      },
      stack: '/unit-private-stack',
    }
    expect(await tasks.getResult(resultId)).toEqual(internal)
    expect(engine.calls).toEqual([{ method: 'result.get', params: { projectId, resultId } }])
  })

  it('does not grant a structural fake the owned Supervisor startup-error authority', async () => {
    const startupError = {
      code: 'PROJECT_FORMAT_UNSUPPORTED',
      messageKey: 'project.formatUnsupported',
      params: { supportedFormats: [3] },
      retryable: false,
    }
    expect(safeDisplayError(startupError)).toEqual(startupError)
    const engine = Object.assign(new LayerEngine(), {
      profile: 'business3',
      projectFailure: () => {
        throw new Error('UNOWNED_PROJECTION_MUST_NOT_BE_USED')
      },
    })
    const { tasks } = setup(true, engine)
    engine.failure = { error: startupError }
    expect(await tasks.getResult(resultId)).toEqual(internal)
    expect(engine.calls).toEqual([{ method: 'result.get', params: { projectId, resultId } }])
  })
})
