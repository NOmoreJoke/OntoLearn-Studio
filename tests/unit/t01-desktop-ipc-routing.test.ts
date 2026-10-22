import { describe, expect, it, vi } from 'vitest'
import type { IpcMain, IpcMainInvokeEvent } from 'electron'
import {
  isTaskUpdate,
  type BridgeResult,
  type DesktopIpcChannel,
  type EngineHealth,
  type ResultMetadataDTO,
  type ResultPageDTO,
  type SafeError,
} from '@ontolearn/contracts'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import {
  registerDesktopIpc,
  type DesktopIpcDependencies,
} from '../../apps/desktop/src/main/desktop-ipc'

const projectId = '00000000-0000-4000-8000-000000000001'
const resultId = '00000000-0000-4000-8000-000000000006'
const hash = 'a'.repeat(64)
const health: EngineHealth = {
  protocolVersion: 2,
  engineVersion: '0.1.0',
  status: 'ok',
  capabilities: ['health'],
}
const metadata: ResultMetadataDTO = {
  resultId,
  projectId,
  jobId: '00000000-0000-4000-8000-000000000003',
  kind: 'query',
  definitionId: 'query1',
  inputSnapshotId: hash,
  inputProjectRevision: 1,
  dependencyVector: { 'facts:asserted': 1 },
  definitionSetDigests: { query: hash },
  implementation: {
    executionSemanticsVersion: 'E1',
    engineVersion: '0.1.0',
    dependencyLockHash: hash,
  },
  scope: 'asserted',
  parametersHash: hash,
  state: 'current',
  staleReason: [],
  payloadStatus: 'available',
  createdAtMs: 1,
  historicalSelectionRequired: false,
}
const page: ResultPageDTO = {
  binding: {
    projectId,
    resultId,
    inputSnapshotId: hash,
    scope: 'asserted',
    parametersHash: hash,
    order: 'ordinal+rowId:asc',
  },
  rows: [
    {
      rowId: '00000000-0000-4000-8000-000000000009',
      ordinal: 0,
      cells: ['路由', null, true, 4],
    },
  ],
  nextCursor: null,
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
const channels: DesktopIpcChannel[] = [
  'engine:health',
  'tasks:restore',
  'project:active',
  'job:get',
  'job:list',
  'job:cancel',
  'job:subscribe',
  'job:unsubscribe',
  'result:get',
  'result:page',
  'operation:get',
]
function ok<T>(data: T): BridgeResult<T> {
  return { ok: true, data }
}
function setup(allowed = true) {
  const fixture = fixtures.cases.find((item) => item.name === 'job running')
  const update: unknown = { kind: 'job', generation: 1, job: structuredClone(fixture?.value) }
  if (!isTaskUpdate(update) || update.kind !== 'job') throw new Error('INVALID_UNIT_JOB')
  const job = update.job
  const project = {
    projectId,
    projectRevision: 1,
    inputSnapshotId: hash,
    dependencyVector: { 'facts:asserted': 1 },
    formatVersion: 2 as const,
  }
  const list = {
    binding: {
      projectId,
      listSnapshotId: '00000000-0000-4000-8000-000000000008',
      filter: 'all',
      order: 'createdAtMs+jobId:asc',
    },
    jobs: [job],
    nextCursor: null,
  }
  const cancelled = {
    jobId: job.jobId,
    disposition: 'accepted',
    state: 'cancelling',
    stateVersion: 5,
  }
  const tasks = {
    restore: vi
      .fn<DesktopIpcDependencies['tasks']['restore']>()
      .mockResolvedValue(ok({ generation: 1, project, jobs: [job] })),
    activeProject: vi
      .fn<DesktopIpcDependencies['tasks']['activeProject']>()
      .mockResolvedValue(ok(project)),
    getJob: vi.fn<DesktopIpcDependencies['tasks']['getJob']>().mockResolvedValue(ok(job)),
    listJobs: vi.fn<DesktopIpcDependencies['tasks']['listJobs']>().mockResolvedValue(ok(list)),
    cancelJob: vi
      .fn<DesktopIpcDependencies['tasks']['cancelJob']>()
      .mockResolvedValue(ok(cancelled)),
    subscribeJob: vi
      .fn<DesktopIpcDependencies['tasks']['subscribeJob']>()
      .mockResolvedValue(ok(job)),
    unsubscribeView: vi
      .fn<DesktopIpcDependencies['tasks']['unsubscribeView']>()
      .mockResolvedValue(ok(null)),
    getResult: vi
      .fn<DesktopIpcDependencies['tasks']['getResult']>()
      .mockResolvedValue(ok(metadata)),
    getResultPage: vi
      .fn<DesktopIpcDependencies['tasks']['getResultPage']>()
      .mockResolvedValue(ok(page)),
    getOperation: vi
      .fn<DesktopIpcDependencies['tasks']['getOperation']>()
      .mockResolvedValue(ok(null)),
  } satisfies DesktopIpcDependencies['tasks']
  const operation = Promise.resolve(health)
  const supervisor = {
    health: vi.fn<DesktopIpcDependencies['supervisor']['health']>().mockReturnValue(operation),
    projectFailure: vi.fn<DesktopIpcDependencies['supervisor']['projectFailure']>(),
  }
  const callbacks = new Map<string, Parameters<IpcMain['handle']>[1]>()
  const handle: IpcMain['handle'] = (channel, callback) => {
    if (callbacks.has(channel)) throw new Error('DUPLICATE_UNIT_CHANNEL')
    callbacks.set(channel, callback)
  }
  // Only a sentinel for the injected trust seam; this is not a BrowserWindow/subframe fixture.
  const event = Object.freeze({ unitEvent: true }) as unknown as IpcMainInvokeEvent
  const trusted = vi.fn<DesktopIpcDependencies['trusted']>().mockReturnValue(allowed)
  registerDesktopIpc({ ipcMain: { handle }, trusted, tasks, supervisor })
  async function invoke(channel: DesktopIpcChannel, ...args: unknown[]): Promise<unknown> {
    const callback = callbacks.get(channel)
    if (!callback) throw new Error('MISSING_UNIT_CHANNEL')
    return await callback(event, ...args)
  }
  return {
    tasks,
    supervisor,
    callbacks,
    trusted,
    event,
    invoke,
    operation,
    job,
    project,
    list,
    cancelled,
  }
}

describe('production finite IPC registration (ordinary unit seam)', () => {
  it('registers eleven names with complete responses and original tuples', async () => {
    const f = setup()
    expect([...f.callbacks.keys()]).toEqual(channels)
    const listOptions = { filter: 'all' as const, pageSize: 20, listSnapshotId: null, cursor: null }
    const pageOptions = { resultId, pageSize: 20, cursor: null }
    const unsubscribe = { jobId: f.job.jobId, generation: 1 }
    expect(await f.invoke('engine:health')).toEqual(ok(health))
    expect(await f.invoke('tasks:restore')).toEqual(
      ok({ generation: 1, project: f.project, jobs: [f.job] }),
    )
    expect(await f.invoke('project:active')).toEqual(ok(f.project))
    expect(await f.invoke('job:get', f.job.jobId)).toEqual(ok(f.job))
    expect(await f.invoke('job:list', listOptions)).toEqual(ok(f.list))
    expect(await f.invoke('job:cancel', f.job.jobId)).toEqual(ok(f.cancelled))
    expect(await f.invoke('job:subscribe', f.job.jobId)).toEqual(ok(f.job))
    expect(await f.invoke('job:unsubscribe', unsubscribe)).toEqual(ok(null))
    expect(await f.invoke('result:get', resultId)).toEqual(ok(metadata))
    expect(await f.invoke('result:page', pageOptions)).toEqual(ok(page))
    expect(await f.invoke('operation:get', f.job.operationId)).toEqual(ok(null))
    expect(f.supervisor.health.mock.calls).toEqual([[]])
    expect(f.supervisor.projectFailure.mock.calls).toEqual([])
    expect(f.tasks.restore.mock.calls).toEqual([[]])
    expect(f.tasks.activeProject.mock.calls).toEqual([[]])
    expect(f.tasks.getJob.mock.calls).toEqual([[f.job.jobId]])
    expect(f.tasks.listJobs.mock.calls).toEqual([[listOptions]])
    expect(f.tasks.cancelJob.mock.calls).toEqual([[f.job.jobId]])
    expect(f.tasks.subscribeJob.mock.calls).toEqual([[f.job.jobId]])
    expect(f.tasks.unsubscribeView.mock.calls).toEqual([[unsubscribe]])
    expect(f.tasks.getResult.mock.calls).toEqual([[resultId]])
    expect(f.tasks.getResultPage.mock.calls).toEqual([[pageOptions]])
    expect(f.tasks.getOperation.mock.calls).toEqual([[f.job.operationId]])
    expect(f.trusted.mock.calls).toEqual(channels.map(() => [f.event]))
    const firstDownstream = f.supervisor.health.mock.invocationCallOrder[0]
    expect(f.trusted.mock.invocationCallOrder[0]).toBeLessThan(firstDownstream)
  })

  it.each(channels)('trust denial for %s performs zero downstream calls', async (channel) => {
    const f = setup(false)
    expect(await f.invoke(channel, { untrusted: true })).toEqual(denied)
    expect(f.trusted.mock.calls).toEqual([[f.event]])
    for (const method of Object.values(f.tasks)) {
      expect(method.mock.calls).toEqual([])
    }
    expect(f.supervisor.health.mock.calls).toEqual([])
    expect(f.supervisor.projectFailure.mock.calls).toEqual([])
  })

  it('passes the original health promise and cause to the supervisor projection', async () => {
    const f = setup()
    const cause = new Error('unit-private-health-detail')
    const operation = Promise.reject(cause)
    const projected: SafeError = {
      code: 'INTERNAL_ERROR',
      messageKey: 'engine.internal',
      params: {},
      retryable: false,
    }
    f.supervisor.health.mockReturnValueOnce(operation)
    f.supervisor.projectFailure.mockReturnValueOnce(projected)
    expect(await f.invoke('engine:health')).toEqual({ ok: false, error: projected })
    expect(f.supervisor.projectFailure).toHaveBeenCalledExactlyOnceWith(cause, operation)
  })
})
