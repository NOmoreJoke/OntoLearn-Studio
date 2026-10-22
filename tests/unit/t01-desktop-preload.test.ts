import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { IpcRendererEvent } from 'electron'
import {
  isTaskUpdate,
  type BridgeResult,
  type DesktopBridge,
  type ResultMetadataDTO,
  type ResultPageDTO,
} from '@ontolearn/contracts'
import fixtures from '../../packages/contracts/v2/fixtures.json'

const ports = vi.hoisted(() => {
  type Receive = (event: IpcRendererEvent, update: unknown) => void
  const state: { bridge?: DesktopBridge } = {}
  const listeners = new Set<Receive>()
  return {
    state,
    listeners,
    invoke: vi.fn<(channel: string, ...args: unknown[]) => Promise<unknown>>(),
    expose: vi.fn((name: string, bridge: DesktopBridge) => {
      if (name !== 'ontolearn') throw new Error('UNEXPECTED_UNIT_EXPOSURE')
      state.bridge = bridge
    }),
    on: vi.fn((channel: string, listener: Receive) => {
      if (channel !== 'tasks:update') throw new Error('UNEXPECTED_UNIT_EVENT')
      listeners.add(listener)
    }),
    remove: vi.fn((channel: string, listener: Receive) => {
      if (channel !== 'tasks:update') throw new Error('UNEXPECTED_UNIT_EVENT')
      listeners.delete(listener)
    }),
  }
})
vi.mock('electron', () => ({
  contextBridge: { exposeInMainWorld: ports.expose },
  ipcRenderer: { invoke: ports.invoke, on: ports.on, removeListener: ports.remove },
}))

beforeEach(async () => {
  vi.resetModules()
  ports.invoke.mockReset()
  ports.expose.mockClear()
  ports.on.mockClear()
  ports.remove.mockClear()
  ports.listeners.clear()
  ports.state.bridge = undefined
  // Import the real preload under a module-local Electron double, never Electron itself.
  await import('../../apps/desktop/src/preload/index')
})
function bridge(): DesktopBridge {
  if (!ports.state.bridge) throw new Error('MISSING_UNIT_EXPOSURE')
  return ports.state.bridge
}
function ok<T>(data: T): BridgeResult<T> {
  return { ok: true, data }
}
async function roundTrip<T>(
  call: () => Promise<T>,
  channel: string,
  args: unknown[],
  response: T,
): Promise<void> {
  ports.invoke.mockResolvedValueOnce(response)
  const before = ports.invoke.mock.calls.length
  expect(await call()).toEqual(response)
  expect(ports.invoke.mock.calls.slice(before)).toEqual([[channel, ...args]])
}
function runningJobUpdate() {
  const item = fixtures.cases.find((value) => value.name === 'job running')
  const update: unknown = { kind: 'job', generation: 1, job: structuredClone(item?.value) }
  if (!isTaskUpdate(update) || update.kind !== 'job') throw new Error('INVALID_UNIT_JOB')
  return update
}
function emit(value: unknown): void {
  // A sentinel at the Electron port boundary; it grants no sender/window authority.
  const event = Object.freeze({ unitEvent: true }) as unknown as IpcRendererEvent
  for (const listener of [...ports.listeners]) listener(event, value)
}

describe('actual named preload with a controlled Electron module', () => {
  it('exposes named methods and preserves eleven IPC tuples and full responses', async () => {
    const b = bridge()
    expect(ports.expose).toHaveBeenCalledTimes(1)
    expect(Object.keys(b).sort()).toEqual(
      [
        'cancelJob',
        'getActiveProject',
        'getEngineHealth',
        'getJob',
        'getOperation',
        'getResult',
        'getResultPage',
        'listJobs',
        'onTaskUpdate',
        'restoreTasks',
        'subscribeJob',
        'unsubscribeJob',
      ].sort(),
    )
    expect('invoke' in b).toBe(false)
    expect('ipcRenderer' in b).toBe(false)
    const { job } = runningJobUpdate()
    const project = {
      projectId: job.projectId,
      projectRevision: 1,
      inputSnapshotId: job.inputSnapshotId,
      dependencyVector: { 'facts:asserted': 1 },
      formatVersion: 2 as const,
    }
    const resultId = '00000000-0000-4000-8000-000000000006'
    const metadata: ResultMetadataDTO = {
      resultId,
      projectId: job.projectId,
      jobId: job.jobId,
      kind: 'query',
      definitionId: 'query1',
      inputSnapshotId: job.inputSnapshotId,
      inputProjectRevision: 1,
      dependencyVector: { 'facts:asserted': 1 },
      definitionSetDigests: { query: 'b'.repeat(64) },
      implementation: {
        executionSemanticsVersion: 'E1',
        engineVersion: '0.1.0',
        dependencyLockHash: 'c'.repeat(64),
      },
      scope: 'asserted',
      parametersHash: 'd'.repeat(64),
      state: 'current',
      staleReason: [],
      payloadStatus: 'available',
      createdAtMs: 7,
      historicalSelectionRequired: false,
    }
    const page: ResultPageDTO = {
      binding: {
        projectId: job.projectId,
        resultId,
        inputSnapshotId: job.inputSnapshotId,
        scope: 'asserted',
        parametersHash: metadata.parametersHash,
        order: 'ordinal+rowId:asc',
      },
      rows: [
        {
          rowId: '00000000-0000-4000-8000-000000000009',
          ordinal: 4,
          cells: ['完整', null, false, 1],
        },
      ],
      nextCursor: null,
    }
    const listOptions = { filter: 'all' as const, pageSize: 20, listSnapshotId: null, cursor: null }
    const pageOptions = { resultId, pageSize: 20, cursor: null }
    await roundTrip(
      () => b.getEngineHealth(),
      'engine:health',
      [],
      ok({ protocolVersion: 2, engineVersion: '0.1.0', status: 'ok', capabilities: ['health'] }),
    )
    await roundTrip(
      () => b.restoreTasks(),
      'tasks:restore',
      [],
      ok({ generation: 1, project, jobs: [job] }),
    )
    await roundTrip(() => b.getActiveProject(), 'project:active', [], ok(project))
    await roundTrip(() => b.getJob(job.jobId), 'job:get', [job.jobId], ok(job))
    await roundTrip(
      () => b.listJobs(listOptions),
      'job:list',
      [listOptions],
      ok({
        binding: {
          projectId: job.projectId,
          listSnapshotId: '00000000-0000-4000-8000-000000000008',
          filter: 'all',
          order: 'createdAtMs+jobId:asc',
        },
        jobs: [job],
        nextCursor: null,
      }),
    )
    await roundTrip(
      () => b.cancelJob(job.jobId),
      'job:cancel',
      [job.jobId],
      ok({ jobId: job.jobId, disposition: 'accepted', state: 'cancelling', stateVersion: 5 }),
    )
    await roundTrip(() => b.subscribeJob(job.jobId), 'job:subscribe', [job.jobId], ok(job))
    await roundTrip(
      () => b.unsubscribeJob(job.jobId, 1),
      'job:unsubscribe',
      [{ jobId: job.jobId, generation: 1 }],
      ok(null),
    )
    await roundTrip(() => b.getResult(resultId), 'result:get', [resultId], ok(metadata))
    await roundTrip(() => b.getResultPage(pageOptions), 'result:page', [pageOptions], ok(page))
    await roundTrip(
      () => b.getOperation(job.operationId),
      'operation:get',
      [job.operationId],
      ok(null),
    )
    const failure = {
      ok: false as const,
      error: {
        code: 'PERMISSION_DENIED',
        messageKey: 'permission.denied',
        params: {},
        retryable: false,
      },
    }
    await roundTrip(() => b.getResult(resultId), 'result:get', [resultId], failure)
  })

  it('filters update structures and removes the same real receive listener before remount', () => {
    const first = vi.fn()
    const release = bridge().onTaskUpdate(first)
    const receive = ports.on.mock.calls[0][1]
    const update = runningJobUpdate()
    const restored = {
      kind: 'restored',
      generation: 2,
      view: { generation: 2, project: null, jobs: [] },
    }
    const connection = {
      kind: 'connection',
      generation: 2,
      projectId: update.job.projectId,
      state: 'offline',
      attempt: 3,
      error: {
        code: 'INTERNAL_ERROR',
        messageKey: 'engine.internal',
        params: {},
        retryable: false,
      },
    }
    emit(update)
    emit(restored)
    emit(connection)
    expect(first.mock.calls).toEqual([[update], [restored], [connection]])
    for (const invalid of [
      null,
      { ...update, generation: -1 },
      { ...update, job: {} },
      { ...restored, generation: 3 },
      { ...connection, error: { ...connection.error, params: { path: '/unit-private' } } },
      { kind: 'unknown', generation: 2 },
    ]) {
      emit(invalid)
    }
    expect(first.mock.calls).toEqual([[update], [restored], [connection]])
    release()
    expect(ports.remove.mock.calls).toEqual([['tasks:update', receive]])
    expect(ports.listeners.size).toBe(0)
    emit(update)
    expect(first).toHaveBeenCalledTimes(3)
    const second = vi.fn()
    const releaseSecond = bridge().onTaskUpdate(second)
    expect(ports.listeners.size).toBe(1)
    emit(update)
    expect(first).toHaveBeenCalledTimes(3)
    expect(second.mock.calls).toEqual([[update]])
    releaseSecond()
    expect(ports.remove.mock.calls[1]).toEqual(['tasks:update', ports.on.mock.calls[1][1]])
    expect(ports.listeners.size).toBe(0)
  })
})
