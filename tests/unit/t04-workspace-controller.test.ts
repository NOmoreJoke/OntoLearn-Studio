import { readFileSync } from 'node:fs'
import path from 'node:path'
import ts from 'typescript'
import { createElement, type ComponentType } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createHash } from 'node:crypto'
import { describe, it, expect, vi } from 'vitest'
import { validateV2 } from '../../packages/contracts/src/v2'
import canonicalFixtures from '../../packages/contracts/v2/fixtures.json'
import {
  QueryWorkspaceController,
  QUERY_EDITOR,
  canonicalQueryJson,
  type QueryWorkspaceBridge,
} from '../../apps/desktop/src/renderer/src/query/workspace-controller'
import type {
  MainlineProjectReadDTO,
  QueryDraftDTO,
  JobView,
  TaskUpdate,
  TaskView,
  MainlineDraftSaveArgs,
  QueryDescriptorDTO,
} from '../../apps/desktop/src/renderer/src/query/api002-source-types'

// Fault-injection unit transport only. These replies are not production issuer,
// Store, confirmation, backend or App evidence.
const pid = '20000000-0000-4000-8000-000000000001',
  jid = '20000000-0000-4000-8000-000000000002',
  ref = '20000000-0000-4000-8000-000000000003'
const hash = (text: string) => createHash('sha256').update(text).digest('hex')
const pageModule = '../../apps/desktop/src/renderer/src/query/QueryWorkspacePage'
const {
  QueryWorkspacePage,
}: {
  QueryWorkspacePage: ComponentType<{
    controller: QueryWorkspaceController
    modelDraft?: QueryDraftDTO
  }>
} = await import(pageModule)
const markerFor = (job: JobView) => ({
  projectId: pid,
  operationId: job.operationId,
  jobId: job.jobId,
  planHash: hash('different marker fingerprint domain'),
  projectRevision: 2,
  beforeSnapshotId: job.inputSnapshotId,
  afterSnapshotId: hash('snapshot2'),
})
const succeeded = (job: JobView): JobView => {
  const { projectRevision, beforeSnapshotId, afterSnapshotId, planHash } = markerFor(job)
  return {
    ...job,
    state: 'succeeded',
    stateVersion: 3,
    updatedAtMs: 3,
    finishedAtMs: 3,
    resultRef: { resultId: ref, inputSnapshotId: job.inputSnapshotId },
    commitProgress: {
      mode: 'atomic',
      operationId: job.operationId,
      marker: { projectRevision, beforeSnapshotId, afterSnapshotId, planHash },
    },
  }
}
const unsuccessful = (job: JobView, state: 'failed' | 'cancelled', version = 3): JobView => ({
  ...job,
  state,
  stateVersion: version,
  updatedAtMs: version,
  finishedAtMs: version,
  resultRef: null,
  error:
    state === 'failed'
      ? { code: 'ENGINE_EXITED', messageKey: 'engine.exited', retryable: true, params: {} }
      : null,
})
const draft: QueryDraftDTO = {
  name: '设备',
  description: '',
  sparql: 'SELECT ?s WHERE {?s ?p ?o}',
  scope: 'asserted',
  capabilityQuestion: '',
  source: 'editor',
}
function read(revision = 1): MainlineProjectReadDTO {
  return {
    readVersion: 1,
    projectId: pid,
    inputSnapshotId: hash(`snapshot${revision}`),
    workspace: {
      workspaceVersion: 1,
      projectId: pid,
      inputSnapshotId: hash(`snapshot${revision}`),
      domainRevision: revision,
      metadataVersion: 1,
      metadata: {
        name: 'test',
        templateRef: null,
        archived: false,
        mode: 'guided',
        origin: 'created',
      },
      operationSequence: 1,
      checkpointRef: hash('checkpoint'),
      draft: { editor: QUERY_EDITOR, state: 'missing' },
    },
    domain: {
      projectRevision: revision,
      dependencyVector: { 'facts:asserted': 1 },
      state: { definitions: [], facts: [], mappingState: {} },
    },
  }
}
const ok = <T>(data: T) => ({ ok: true as const, data })
const failed = {
  ok: false as const,
  error: {
    code: 'INVALID_STATE',
    messageKey: 'protocol.invalidState',
    params: {},
    retryable: false,
  },
}
const defer = <T>() => {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((fn) => {
    resolve = fn
  })
  return { promise, resolve }
}
function setup(project = read()) {
  let listener: (update: TaskUpdate) => void = () => {}
  let lastOp = ''
  const job = (
    operationId: string,
    kind = 'changeset.commit',
    state: JobView['state'] = 'queued',
    version = 1,
  ): JobView => ({
    ...structuredClone(
      canonicalFixtures.cases.find((value) => value.name === 'job queued')!.value as Record<
        string,
        unknown
      >,
    ),
    jobId: jid,
    projectId: pid,
    operationId,
    inputSnapshotId: project.inputSnapshotId,
    state,
    stateVersion: version,
    resultRef: null,
    error: null,
    capability: kind,
    parametersHash: hash('params'),
    scope: 'asserted',
    createdAtMs: 1,
    updatedAtMs: 1,
    finishedAtMs: null,
    input: {
      inputSnapshotId: project.inputSnapshotId,
      scope: 'asserted',
      definitionId: kind === 'query.execute' ? 'q01' : 'changeset',
      parametersHash: hash('params'),
      derivedResultIds: [],
      preparedPlanRef: kind === 'query.execute' ? null : hash('plan'),
    },
    confirmationRef: kind === 'query.execute' ? null : ref,
    commitProgress:
      kind === 'query.execute' ? { mode: 'none' } : { mode: 'atomic', operationId, marker: null },
  })
  const loaded = () => ({
    projectId: pid,
    definitionId: 'q01',
    baseProjectRevision: project.domain.projectRevision,
    inputSnapshotId: project.inputSnapshotId,
    definitionVersion: 1,
    definitionSha256: hash('def'),
    kind: 'managed' as const,
    descriptorVersion: 1 as const,
    descriptorSha256: hash('desc'),
    draft,
    loadRef: ref,
  })
  const preview = {
    status: 'ready' as const,
    projectId: pid,
    baseRevision: project.domain.projectRevision,
    previewHash: hash('preview'),
    preparedPlanRef: hash('plan'),
    inputSnapshotId: project.inputSnapshotId,
    parametersHash: hash('params'),
    intent: 'change' as const,
    targetOperationId: null,
    summary: 'unit',
    manifest: {
      documentKind: 'diff' as const,
      documentHash: hash('diff'),
      totalBytes: 2,
      segmentCount: 1,
      segments: [{ ordinal: 0, byteOffset: 0, rawByteLength: 2, sha256: hash('[]') }],
    },
  }
  const confirmation = {
    projectId: pid,
    previewHash: preview.previewHash,
    preparedPlanRef: preview.preparedPlanRef,
    confirmationRef: ref,
    inputSnapshotId: project.inputSnapshotId,
    parametersHash: preview.parametersHash,
  }
  const bridge = {
    readProject: vi.fn(async () => ok(project)),
    getQueryDefinitionBase: vi.fn(async () =>
      ok({
        baseRef: ref,
        projectRevision: project.domain.projectRevision,
        inputSnapshotId: project.inputSnapshotId,
      }),
    ),
    loadQueryDefinition: vi.fn(
      async (args: Parameters<QueryWorkspaceBridge['loadQueryDefinition']>[0]) => {
        void args
        return ok(loaded())
      },
    ),
    saveProjectDraft: vi.fn(async (args: MainlineDraftSaveArgs) =>
      ok({
        draftSaveVersion: 1 as const,
        projectId: pid,
        operationId: args.operationId,
        operationSequence: 2,
        editor: args.editor,
        generation: args.expectedGeneration + 1,
        boundDomainRevision: args.boundDomainRevision,
        contentHash: hash(args.contentJson),
        afterCheckpointRef: hash('after'),
      }),
    ),
    previewProjectChangeset: vi.fn(async () => ok(preview)),
    getProjectDiffPage: vi.fn(async () =>
      ok({
        projectId: pid,
        previewHash: preview.previewHash,
        documentKind: 'diff' as const,
        documentHash: hash('diff'),
        segments: [
          { ordinal: 0, byteOffset: 0, rawByteLength: 2, sha256: hash('[]'), dataBase64: 'W10=' },
        ],
        nextCursor: ref,
        complete: true,
      }),
    ),
    confirmProjectChangeset: vi.fn(async () => ok(confirmation)),
    commitProjectChangeSet: vi.fn(
      async (args: { operationId: string; confirmation: typeof confirmation }) => {
        lastOp = args.operationId
        return ok(job(lastOp))
      },
    ),
    executeSavedQuery: vi.fn(async (args: { operationId: string }) => {
      lastOp = args.operationId
      return ok({
        operationId: lastOp,
        acceptedJob: job(lastOp, 'query.execute'),
        watch: { state: 'subscribed' as const },
      })
    }),
    getJob: vi.fn(async () => ok(job(lastOp))),
    getOperation: vi.fn(async () => ok(null as Record<string, unknown> | null)),
    listJobs: vi.fn(async (options: Parameters<QueryWorkspaceBridge['listJobs']>[0]) => {
      void options
      return ok({
        binding: {
          projectId: pid,
          listSnapshotId: ref,
          filter: 'all',
          order: 'createdAtMs+jobId:asc',
        },
        jobs: [],
        nextCursor: null,
      })
    }),
    cancelJob: vi.fn(async () =>
      ok({ jobId: jid, disposition: 'alreadyTerminal', state: 'succeeded', stateVersion: 3 }),
    ),
    getQueryResultDescriptor: vi.fn(async () => failed),
    getQueryExecutedTextPage: vi.fn(async () => failed),
    getQueryRowsPage: vi.fn(async () => failed),
    onTaskUpdate: vi.fn((fn: (update: TaskUpdate) => void) => {
      listener = fn
      return () => {
        listener = () => {}
      }
    }),
  }
  const verifier = vi.fn(async () => [] as unknown[])
  const controller = new QueryWorkspaceController(pid, bridge as QueryWorkspaceBridge, verifier)
  const edit = async () => {
    await controller.open()
    controller.setDefinitionId('q01')
    controller.editDraft(draft)
  }
  const acceptedCommit = async () => {
    await edit()
    await controller.prepare()
    await controller.confirmAndCommit()
  }
  const acceptedQuery = async () => {
    await controller.open()
    controller.setDefinitionId('q01')
    await controller.load()
    await controller.execute()
  }
  return {
    bridge,
    controller,
    verifier,
    preview,
    confirmation,
    project,
    job,
    loaded,
    edit,
    acceptedCommit,
    acceptedQuery,
    emit: (update: TaskUpdate) => listener(update),
  }
}

const taskView = (generation: number, jobs: JobView[], revision = 1): TaskView => ({
  generation,
  project: {
    projectId: pid,
    projectRevision: revision,
    inputSnapshotId: hash(`snapshot${revision}`),
    dependencyVector: { 'facts:asserted': 1 },
    formatVersion: 3,
  },
  jobs,
})

describe('T04 original Job observation handoff', () => {
  it('holds an early terminal candidate without accepting it until the actual ACK', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    await x.edit()
    await x.controller.prepare()
    const entered = defer<JobView>(),
      receipt = defer<ReturnType<typeof ok<JobView>>>()
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    x.bridge.commitProjectChangeSet.mockImplementationOnce((args) => {
      const queued = x.job(args.operationId)
      x.emit({ kind: 'job', generation: 1, job: succeeded(queued) })
      entered.resolve(queued)
      return receipt.promise
    })
    const saving = x.controller.confirmAndCommit()
    const queued = await entered.promise
    expect(x.controller.getSnapshot().job).toBeUndefined()
    expect(x.controller.getSnapshot().pending?.kind).toBe('commit')
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getJob).not.toHaveBeenCalled()
    receipt.resolve(ok(queued))
    await saving
    expect(x.controller.getSnapshot().job).toEqual(succeeded(queued))
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.getSnapshot().pending).toBeUndefined()
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    expect(x.bridge.confirmProjectChangeset).toHaveBeenCalledTimes(1)
    expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    expect(x.bridge.getOperation).not.toHaveBeenCalled()
  })

  it('reads the accepted original Job once when subscription has no initial terminal event', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockImplementationOnce(async () => {
      const args = x.bridge.commitProjectChangeSet.mock.calls[0][0]
      return ok(succeeded(x.job(args.operationId)))
    })
    await x.acceptedCommit()
    expect(x.controller.getSnapshot().job?.state).toBe('succeeded')
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
    expect(x.bridge.getOperation).not.toHaveBeenCalled()
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    expect(x.bridge.readProject).toHaveBeenCalledTimes(1)
  })

  it('hands off an early query terminal and preserves the actual pending-watch receipt', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.executeSavedQuery.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId, 'query.execute')
      const done = unsuccessful(queued, 'cancelled')
      x.emit({ kind: 'restored', generation: 2, view: taskView(2, [done]) })
      return {
        ok: true,
        data: {
          operationId: args.operationId,
          acceptedJob: queued,
          watch: { state: 'pending', error: failed.error },
        },
      } as never
    })
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.acceptedQuery()
    const job = x.controller.getSnapshot().job!
    expect(job).toEqual(unsuccessful(x.job(job.operationId, 'query.execute'), 'cancelled'))
    expect(x.controller.getSnapshot().watchPending).toBe(true)
    expect(x.controller.getSnapshot().result).toBeUndefined()
    expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
    expect(x.bridge.executeSavedQuery).toHaveBeenCalledTimes(1)
    expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(x.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
  })

  it('does not promote a candidate when the actual receipt fails original input validation', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId)
      x.emit({ kind: 'job', generation: 1, job: succeeded(queued) })
      return ok({ ...queued, confirmationRef: jid })
    })
    await x.acceptedCommit()
    expect(x.controller.getSnapshot().job).toBeUndefined()
    expect(x.controller.getSnapshot().pending?.kind).toBe('commit')
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getJob).not.toHaveBeenCalled()
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
  })

  it('consumes restored terminal before ACK despite the old action view being fenced', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId)
      x.emit({ kind: 'restored', generation: 2, view: taskView(2, [succeeded(queued)], 2) })
      return ok(queued)
    })
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.acceptedCommit()
    expect(x.controller.getSnapshot().job?.state).toBe('succeeded')
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.getSnapshot().read).toBeUndefined()
    expect(x.controller.getSnapshot().draft).toEqual(draft)
    expect(x.controller.getSnapshot().draftBaseRevision).toBe(1)
    expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
  })

  it('observes restored terminal after ACK and rejects a read from the preceding generation', async () => {
    for (const restoredTerminal of [true, false]) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      const reading = defer<JobView>(),
        response = defer<ReturnType<typeof ok<JobView>>>()
      x.bridge.getJob.mockImplementationOnce(() => {
        const queued = x.controller.getSnapshot().job!
        reading.resolve(queued)
        return response.promise
      })
      const saving = x.acceptedCommit()
      const queued = await reading.promise
      x.emit({
        kind: 'restored',
        generation: 2,
        view: taskView(2, [restoredTerminal ? succeeded(queued) : queued], 2),
      })
      response.resolve(ok(succeeded(queued)))
      await saving
      expect(x.controller.getSnapshot().job).toEqual(restoredTerminal ? succeeded(queued) : queued)
      expect(x.controller.getSnapshot().jobReconciled).toBe(false)
      expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    }
  })

  it('keeps UNKNOWN and authenticated marker evidence through detach and explicit original retry', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      x.emit({ kind: 'job', generation: 1, job: succeeded(x.job(args.operationId)) })
      throw new Error('lost original ACK')
    })
    await x.acceptedCommit()
    const original = structuredClone(x.controller.getSnapshot().pending)
    expect(original?.kind).toBe('commit')
    expect(x.controller.getSnapshot().job).toBeUndefined()
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getJob).not.toHaveBeenCalled()
    x.controller.disconnect()
    x.controller.connect(taskView(2, [], 2))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.controller.recoverOriginalCommit()
    expect(x.bridge.commitProjectChangeSet.mock.calls[1][0]).toEqual(
      x.bridge.commitProjectChangeSet.mock.calls[0][0],
    )
    const job = x.controller.getSnapshot().job!
    expect(job.state).toBe('succeeded')
    expect(job.commitProgress).toEqual(succeeded(x.job(job.operationId)).commitProgress)
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
    expect(x.bridge.confirmProjectChangeset).toHaveBeenCalledTimes(1)
  })

  it('retains a prior authenticated marker if the later ACK contradicts its mutable facts', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId)
      x.emit({ kind: 'job', generation: 1, job: succeeded(queued) })
      return ok(unsuccessful(queued, 'failed', 4))
    })
    await x.acceptedCommit()
    const job = x.controller.getSnapshot().job!
    expect(job).toEqual(succeeded(x.job(job.operationId)))
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getOperation).not.toHaveBeenCalled()
  })

  it('holds contradictions from every observation entry through later refresh and write attempts', async () => {
    for (const entry of ['pending', 'ack', 'event', 'restored', 'automatic', 'manual'] as const) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
        const queued = x.job(args.operationId)
        if (entry === 'pending' || entry === 'ack') {
          x.emit({ kind: 'job', generation: 1, job: succeeded(queued) })
          if (entry === 'pending')
            x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'failed', 4) })
        }
        return ok(entry === 'ack' ? unsuccessful(queued, 'failed', 4) : queued)
      })
      x.bridge.getJob.mockImplementationOnce(async () => {
        if (entry !== 'automatic') return failed as never
        const queued = x.controller.getSnapshot().job!
        x.emit({ kind: 'job', generation: 1, job: succeeded(queued) })
        return ok(unsuccessful(queued, 'failed', 4))
      })
      await x.acceptedCommit()
      const initial = x.controller.getSnapshot().job!,
        done = succeeded(x.job(initial.operationId))
      if (entry === 'event' || entry === 'restored' || entry === 'manual') {
        x.emit({ kind: 'job', generation: 1, job: done })
        const contradiction = unsuccessful(x.job(initial.operationId), 'failed', 4)
        if (entry === 'event') x.emit({ kind: 'job', generation: 1, job: contradiction })
        if (entry === 'restored')
          x.emit({ kind: 'restored', generation: 2, view: taskView(2, [contradiction], 2) })
        if (entry === 'manual') {
          x.bridge.getJob.mockResolvedValueOnce(ok(contradiction))
          await x.controller.refreshJob()
        }
      }
      expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
      expect(x.controller.getSnapshot().job).toEqual(done)
      expect(x.controller.getSnapshot().jobReconciled).toBe(false)
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(done)))
      await x.controller.refreshJob()
      expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
      expect(x.controller.getSnapshot().jobReconciled).toBe(false)
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.bridge.getOperation).not.toHaveBeenCalled()
      expect(
        renderToStaticMarkup(createElement(QueryWorkspacePage, { controller: x.controller })),
      ).toContain('原任务状态记录互相矛盾')
      await x.controller.execute()
      await x.controller.prepare()
      expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      expect(x.bridge.confirmProjectChangeset).toHaveBeenCalledTimes(1)
    }
  })

  it('never settles a failed/null candidate after observing a contradictory successful ACK marker', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId)
      x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'failed', 4) })
      return ok(succeeded(queued))
    })
    await x.acceptedCommit()
    const job = x.controller.getSnapshot().job!
    expect(job.state).toBe('failed')
    expect(job.stateVersion).toBe(4)
    expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
    x.controller.disconnect()
    x.controller.connect(taskView(2, [job], 2))
    x.bridge.getJob.mockResolvedValueOnce(ok(job))
    x.bridge.getOperation.mockResolvedValueOnce(ok(null))
    await x.controller.refreshJob()
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getOperation).not.toHaveBeenCalled()
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
  })

  it('does not mistake compatible older or repeated observations for contradictory authority', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId),
        done = succeeded(queued)
      x.emit({ kind: 'job', generation: 1, job: done })
      x.emit({ kind: 'job', generation: 1, job: queued })
      x.emit({ kind: 'job', generation: 1, job: done })
      return ok(queued)
    })
    await x.acceptedCommit()
    const done = x.controller.getSnapshot().job!
    x.emit({ kind: 'restored', generation: 2, view: taskView(2, [x.job(done.operationId)], 2) })
    expect(x.controller.getSnapshot().job).toEqual(done)
    expect(x.controller.getSnapshot().jobObservationConflict).toBe(false)
  })

  it('keeps an old Job conflict when a previously entered new operation receives its real ACK', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.acceptedQuery()
    const old = x.controller.getSnapshot().job!
    x.bridge.getJob.mockResolvedValueOnce(ok(unsuccessful(old, 'cancelled')))
    await x.controller.refreshJob()
    expect(x.controller.hasUnresolvedWrite).toBe(false)
    const entered = defer<JobView>(),
      receipt = defer<Awaited<ReturnType<typeof x.bridge.executeSavedQuery>>>()
    x.bridge.executeSavedQuery.mockImplementationOnce((args) => {
      const next = { ...x.job(args.operationId, 'query.execute'), jobId: ref }
      entered.resolve(next)
      return receipt.promise
    })
    const executing = x.controller.execute()
    const next = await entered.promise
    x.emit({ kind: 'job', generation: 1, job: unsuccessful(old, 'failed', 4) })
    expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    receipt.resolve(
      ok({
        operationId: next.operationId,
        acceptedJob: next,
        watch: { state: 'subscribed' },
      }),
    )
    await executing
    expect(x.controller.getSnapshot().job).toEqual(next)
    expect(x.controller.getSnapshot().pending).toBeUndefined()
    expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
    const done = unsuccessful(next, 'cancelled')
    x.bridge.getJob.mockResolvedValueOnce(ok(done))
    await x.controller.refreshJob()
    expect(x.controller.getSnapshot().job).toEqual(done)
    expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    await x.controller.execute()
    expect(x.bridge.executeSavedQuery).toHaveBeenCalledTimes(2)
    expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(x.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
  })

  it('does not bind an early candidate with different complete immutable identity', async () => {
    const changes: Array<(job: JobView) => void> = [
      (job) => {
        job.jobId = ref
      },
      (job) => {
        job.operationId = ref
      },
      (job) => {
        job.projectId = ref
      },
      (job) => {
        job.inputSnapshotId = hash('other')
      },
      (job) => {
        job.capability = 'query.execute'
      },
      (job) => {
        job.scope = 'scenario'
      },
      (job) => {
        job.createdAtMs = 0
      },
      (job) => {
        job.confirmationRef = jid
      },
      (job) => {
        job.dependencyVector = { 'facts:asserted': 2 }
      },
      (job) => {
        job.definitionSetDigests = { query: hash('other') }
      },
      (job) => {
        job.implementation = { ...(job.implementation as object), engineVersion: 'other' }
      },
      (job) => {
        job.limits = { ...(job.limits as object), maxPageItems: 99 }
      },
      (job) => {
        job.input = { ...(job.input as object), preparedPlanRef: hash('other') }
      },
      (job) => {
        job.commitProgress = { mode: 'none' }
      },
    ]
    for (const change of changes) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      x.bridge.getJob.mockResolvedValueOnce(failed as never)
      x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
        const queued = x.job(args.operationId),
          candidate = succeeded(queued)
        change(candidate)
        x.emit({ kind: 'job', generation: 1, job: candidate })
        return ok(queued)
      })
      await x.acceptedCommit()
      expect(x.controller.getSnapshot().job?.state).toBe('queued')
      expect(x.controller.getSnapshot().job?.stateVersion).toBe(1)
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
    }
  })

  it('keeps pending candidate and restored observations monotone without settling the write', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async (args) => {
      const queued = x.job(args.operationId),
        done = succeeded(queued)
      x.emit({ kind: 'job', generation: 1, job: done })
      x.emit({ kind: 'job', generation: 1, job: queued })
      x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'cancelled', 4) })
      return ok(queued)
    })
    await x.acceptedCommit()
    const done = x.controller.getSnapshot().job!
    x.emit({ kind: 'restored', generation: 2, view: taskView(2, [x.job(done.operationId)], 2) })
    x.emit({ kind: 'job', generation: 1, job: unsuccessful(done, 'cancelled', 9) })
    expect(x.controller.getSnapshot().job).toEqual(done)
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.hasUnresolvedWrite).toBe(true)
  })

  it('preserves the accepted Job on safe read errors and thrown reads without retrying', async () => {
    for (const mode of ['safe-error', 'throw'] as const) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      x.bridge.getJob.mockImplementationOnce(async () => {
        if (mode === 'throw') throw new Error('read failed')
        return failed as never
      })
      await x.acceptedCommit()
      expect(x.controller.getSnapshot().job?.state).toBe('queued')
      expect(x.controller.getSnapshot().pending).toBeUndefined()
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.bridge.getJob).toHaveBeenCalledExactlyOnceWith(jid)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    }
  })

  it('does not read another selected project after a detached late ACK', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    const entered = defer<JobView>(),
      receipt = defer<ReturnType<typeof ok<JobView>>>()
    x.bridge.commitProjectChangeSet.mockImplementationOnce((args) => {
      entered.resolve(x.job(args.operationId))
      return receipt.promise
    })
    const saving = x.acceptedCommit()
    const queued = await entered.promise
    x.controller.disconnect()
    receipt.resolve(ok(queued))
    await saving
    expect(x.controller.getSnapshot().job).toEqual(queued)
    expect(x.bridge.getJob).not.toHaveBeenCalled()
    expect(x.controller.hasUnresolvedWrite).toBe(true)
  })

  it('seeds a retained instance and makes every old cleanup harmless to its successor', async () => {
    const x = setup()
    const pageStop = x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.acceptedCommit()
    const queued = x.controller.getSnapshot().job!,
      oldCallback = x.bridge.onTaskUpdate.mock.calls[0][0]
    x.controller.disconnect()
    const appStop = x.controller.connect(taskView(2, [succeeded(queued)], 2)),
      nextPageStop = x.controller.connect()
    pageStop()
    pageStop()
    expect(x.controller.getSnapshot().job).toEqual(succeeded(queued))
    oldCallback({ kind: 'job', generation: 99, job: unsuccessful(queued, 'failed', 5) })
    const higher = taskView(3, [succeeded(queued)], 2)
    x.emit({ kind: 'restored', generation: 3, view: higher })
    nextPageStop()
    expect(x.bridge.onTaskUpdate).toHaveBeenCalledTimes(2)
    appStop()
    const lastCallback = x.bridge.onTaskUpdate.mock.calls[1][0]
    lastCallback({ kind: 'restored', generation: 100, view: taskView(100, [], 2) })
    const finalStop = x.controller.connect(taskView(4, [succeeded(queued)], 2))
    expect(x.bridge.onTaskUpdate).toHaveBeenCalledTimes(3)
    expect(x.controller.getSnapshot().job).toEqual(succeeded(queued))
    finalStop()
  })

  it('does not let an older seed override a synchronous newer notification', async () => {
    const x = setup()
    await x.acceptedCommit()
    const queued = x.controller.getSnapshot().job!
    x.bridge.onTaskUpdate.mockImplementationOnce((listener) => {
      listener({ kind: 'job', generation: 5, job: succeeded(queued) })
      return () => {}
    })
    const stop = x.controller.connect(taskView(2, [queued]))
    expect(x.controller.getSnapshot().job).toEqual(succeeded(queued))
    stop()
  })

  it('rejects a detached readback after reconnection even with the same task generation', async () => {
    const x = setup()
    const firstStop = x.controller.connect(taskView(1, []))
    const reading = defer<JobView>(),
      reply = defer<ReturnType<typeof ok<JobView>>>()
    x.bridge.getJob.mockImplementationOnce(() => {
      reading.resolve(x.controller.getSnapshot().job!)
      return reply.promise
    })
    const saving = x.acceptedCommit()
    const queued = await reading.promise
    x.controller.disconnect()
    const nextStop = x.controller.connect(taskView(1, [queued]))
    firstStop()
    reply.resolve(ok(succeeded(queued)))
    await saving
    expect(x.controller.getSnapshot().job).toEqual(queued)
    x.emit({ kind: 'restored', generation: 2, view: taskView(2, [succeeded(queued)], 2) })
    expect(x.controller.getSnapshot().job).toEqual(succeeded(queued))
    expect(x.bridge.getJob).toHaveBeenCalledTimes(1)
    nextStop()
  })

  it('fences offline readbacks and accepts only a trusted restored successor', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    const reading = defer<JobView>(),
      reply = defer<ReturnType<typeof ok<JobView>>>()
    x.bridge.getJob.mockImplementationOnce(() => {
      reading.resolve(x.controller.getSnapshot().job!)
      return reply.promise
    })
    const saving = x.acceptedCommit()
    const queued = await reading.promise
    x.emit({
      kind: 'connection',
      generation: 2,
      projectId: pid,
      state: 'offline',
      attempt: 1,
      error: failed.error,
    })
    x.emit({ kind: 'job', generation: 2, job: succeeded(queued) })
    reply.resolve(ok(succeeded(queued)))
    await saving
    expect(x.controller.getSnapshot().job).toEqual(queued)
    x.emit({ kind: 'restored', generation: 3, view: taskView(3, [succeeded(queued)], 2) })
    expect(x.controller.getSnapshot().job).toEqual(succeeded(queued))
    expect(x.bridge.getJob).toHaveBeenCalledTimes(1)
  })
})

describe('T04 refresh settlement after same-generation conflicts', () => {
  it('does not settle a terminal-null Job after conflict during the operation read', async () => {
    for (const markerReturned of [false, true]) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      x.bridge.getJob.mockResolvedValueOnce(failed as never)
      await x.acceptedCommit()
      const queued = x.controller.getSnapshot().job!,
        done = unsuccessful(queued, 'failed'),
        waiting = defer<void>(),
        reply = defer<Awaited<ReturnType<typeof x.bridge.getOperation>>>()
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      x.bridge.getOperation.mockImplementationOnce(() => {
        waiting.resolve()
        return reply.promise
      })
      const refreshing = x.controller.refreshJob()
      await waiting.promise
      x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'cancelled', 4) })
      const marker = markerReturned ? markerFor(done) : null
      reply.resolve(ok(marker))
      await refreshing
      expect(x.controller.getSnapshot().job).toEqual(done)
      expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
      expect(x.controller.getSnapshot().jobReconciled).toBe(false)
      expect(x.controller.getSnapshot().notice).toContain('暂不能完成核验')
      expect(x.controller.getSnapshot().notice).not.toContain('均核对无领域提交')
      expect(x.controller.getSnapshot().operationMarker).toEqual(marker ?? undefined)
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      expect(x.bridge.getOperation).toHaveBeenCalledTimes(1)
    }
  })

  it('retains a successful operation marker without settling after an in-flight conflict', async () => {
    const x = setup()
    x.controller.connect(taskView(1, []))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.acceptedCommit()
    const queued = x.controller.getSnapshot().job!,
      done = succeeded(queued),
      waiting = defer<void>(),
      reply = defer<Awaited<ReturnType<typeof x.bridge.getOperation>>>()
    x.bridge.getJob.mockResolvedValueOnce(ok(done))
    x.bridge.getOperation.mockImplementationOnce(() => {
      waiting.resolve()
      return reply.promise
    })
    const refreshing = x.controller.refreshJob()
    await waiting.promise
    x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'failed', 4) })
    reply.resolve(ok(markerFor(done)))
    await refreshing
    expect(x.controller.getSnapshot().operationMarker).toEqual(markerFor(done))
    expect(x.controller.getSnapshot().job).toEqual(done)
    expect(x.controller.getSnapshot().jobReconciled).toBe(false)
    expect(x.controller.getSnapshot().notice).toContain('暂不能完成核验')
    expect(x.bridge.loadQueryDefinition).not.toHaveBeenCalled()
    expect(x.bridge.readProject).toHaveBeenCalledTimes(1)
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
  })

  it('stops late historical load, project read and current load from publishing success under HOLD', async () => {
    for (const stage of ['historical', 'project', 'current'] as const) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      x.bridge.getJob.mockResolvedValueOnce(failed as never)
      await x.acceptedCommit()
      const queued = x.controller.getSnapshot().job!,
        done = succeeded(queued),
        originalRead = x.controller.getSnapshot().read,
        saved = { ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 },
        waiting = defer<void>(),
        gate = defer<void>()
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(done)))
      x.bridge.loadQueryDefinition.mockImplementation(async (args) => {
        if (stage === args.selection.kind) {
          waiting.resolve()
          await gate.promise
        }
        return ok(saved)
      })
      x.bridge.readProject.mockImplementation(async () => {
        if (stage === 'project') {
          waiting.resolve()
          await gate.promise
        }
        return ok(read(2))
      })
      const refreshing = x.controller.refreshJob()
      await waiting.promise
      x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'failed', 4) })
      gate.resolve()
      await refreshing
      expect(x.controller.getSnapshot().operationMarker).toEqual(markerFor(done))
      expect(x.controller.getSnapshot().jobReconciled).toBe(false)
      expect(x.controller.getSnapshot().jobObservationConflict).toBe(true)
      expect(x.controller.getSnapshot().notice).toContain('暂不能完成核验')
      expect(x.controller.getSnapshot().read).toEqual(originalRead)
      expect(x.controller.getSnapshot().loaded).toBeUndefined()
      expect(x.controller.getSnapshot().draftBaseRevision).toBe(1)
      expect(x.controller.getSnapshot().draft).toEqual(draft)
      expect(x.bridge.loadQueryDefinition).toHaveBeenCalledTimes(stage === 'current' ? 2 : 1)
      expect(x.bridge.readProject).toHaveBeenCalledTimes(stage === 'historical' ? 1 : 2)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    }
  })

  it('publishes a valid descriptor only when no same-generation conflict arose during its read', async () => {
    for (const conflict of [false, true]) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      x.bridge.getJob.mockResolvedValueOnce(failed as never)
      await x.acceptedQuery()
      const queued = x.controller.getSnapshot().job!,
        done: JobView = {
          ...queued,
          state: 'succeeded',
          stateVersion: 3,
          updatedAtMs: 3,
          finishedAtMs: 3,
          resultRef: { resultId: ref, inputSnapshotId: queued.inputSnapshotId },
        },
        implementation = queued.implementation as QueryDescriptorDTO['identity']['implementation'],
        parametersHash = queued.parametersHash as string,
        descriptor: QueryDescriptorDTO = {
          identity: {
            projectId: pid,
            jobId: jid,
            resultId: ref,
            inputSnapshotId: queued.inputSnapshotId,
            inputProjectRevision: 1,
            scope: 'asserted',
            definitionId: 'q01',
            parametersHash,
            implementation,
            payloadSha256: hash('payload'),
            definitionSha256: hash('definition'),
            inputSelection: 'current',
            projectionVersion: 1,
            lengthPolicyId: 'query-presentation-scalars-v1',
          },
          descriptorRef: ref,
          metadata: {
            projectId: pid,
            jobId: jid,
            resultId: ref,
            inputSnapshotId: queued.inputSnapshotId,
            inputProjectRevision: 1,
            scope: 'asserted',
            definitionId: 'q01',
            parametersHash,
            implementation,
            kind: 'query',
            dependencyVector: { 'facts:asserted': 1 },
            definitionSetDigests: {},
            state: 'current',
            staleReason: [],
            payloadStatus: 'available',
            createdAtMs: 1,
            historicalSelectionRequired: false,
          },
          executedText: { sha256: hash('ASK {}'), utf8Bytes: 6, unicodeScalars: 6, utf16Units: 6 },
          query: { kind: 'ASK', value: true },
        },
        waiting = defer<void>(),
        gate = defer<void>()
      expect(validateV2('job', done)).toBe(true)
      expect(validateV2('result', descriptor.metadata)).toBe(true)
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      x.bridge.getQueryResultDescriptor.mockImplementationOnce(async () => {
        waiting.resolve()
        await gate.promise
        return ok(descriptor) as never
      })
      const refreshing = x.controller.refreshJob()
      await waiting.promise
      if (conflict)
        x.emit({ kind: 'job', generation: 1, job: unsuccessful(queued, 'cancelled', 4) })
      gate.resolve()
      await refreshing
      expect(x.controller.getSnapshot().jobReconciled).toBe(!conflict)
      expect(x.controller.getSnapshot().result?.descriptor).toEqual(
        conflict ? undefined : descriptor,
      )
      if (conflict) expect(x.controller.getSnapshot().notice).toContain('暂不能完成核验')
      expect(x.bridge.executeSavedQuery).toHaveBeenCalledTimes(1)
      expect(x.bridge.getQueryResultDescriptor).toHaveBeenCalledTimes(1)
      expect(x.bridge.getOperation).not.toHaveBeenCalled()
    }
  })
})

describe('API002 query workspace private consumer', () => {
  it('accepts canonical four-field atomic markers and rejects seven-field or mismatched Job markers', async () => {
    for (const variant of ['valid', 'seven-fields', 'different-fingerprint'] as const) {
      const x = setup()
      await x.acceptedCommit()
      const job = x.controller.getSnapshot().job!,
        done = succeeded(job)
      expect(validateV2('commitProgress', done.commitProgress)).toBe(true)
      expect(
        validateV2('commitProgress', {
          mode: 'atomic',
          operationId: job.operationId,
          marker: markerFor(job),
        }),
      ).toBe(false)
      if (variant === 'seven-fields') {
        done.commitProgress = {
          mode: 'atomic',
          operationId: job.operationId,
          marker: markerFor(job),
        }
      } else if (variant === 'different-fingerprint') {
        done.commitProgress = {
          mode: 'atomic',
          operationId: job.operationId,
          marker: { ...markerFor(job), planHash: hash('wrong') },
        }
        const marker = done.commitProgress as { marker: Record<string, unknown> }
        delete marker.marker.projectId
        delete marker.marker.operationId
        delete marker.marker.jobId
      }
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(job)))
      const saved = { ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 }
      x.bridge.loadQueryDefinition.mockResolvedValue(ok(saved))
      x.bridge.readProject.mockResolvedValue(ok(read(2)))
      await x.controller.refreshJob()
      expect(x.controller.getSnapshot().jobReconciled).toBe(variant === 'valid')
      expect(x.controller.getSnapshot().loaded).toEqual(variant === 'valid' ? saved : undefined)
      if (variant !== 'valid') expect(x.bridge.loadQueryDefinition).not.toHaveBeenCalled()
    }
  })

  it('rejects a current read with the marker revision but a different snapshot without undoing original settlement', async () => {
    const x = setup()
    await x.acceptedCommit()
    const job = x.controller.getSnapshot().job!
    x.bridge.getJob.mockResolvedValueOnce(ok(succeeded(job)))
    x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(job)))
    x.bridge.loadQueryDefinition.mockResolvedValueOnce(
      ok({
        ...x.loaded(),
        inputSnapshotId: hash('snapshot2'),
        baseProjectRevision: 2,
      }),
    )
    const inconsistent = read(2)
    inconsistent.inputSnapshotId = hash('wrong-current')
    inconsistent.workspace.inputSnapshotId = inconsistent.inputSnapshotId
    x.bridge.readProject.mockResolvedValueOnce(ok(inconsistent))
    await x.controller.refreshJob()
    expect(x.controller.getSnapshot().jobReconciled).toBe(true)
    expect(x.controller.getSnapshot().loaded).toBeUndefined()
    expect(x.bridge.loadQueryDefinition).toHaveBeenCalledTimes(1)
    expect(x.controller.getSnapshot().notice).toContain('结果无法确认')
  })

  it('settles full terminal-null formal failures only after successful null operation crosscheck', async () => {
    for (const state of ['failed', 'cancelled'] as const) {
      const x = setup()
      await x.acceptedCommit()
      const job = x.controller.getSnapshot().job!
      const done = unsuccessful(job, state)
      expect(validateV2('job', done)).toBe(true)
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      await x.controller.refreshJob()
      expect(x.controller.getSnapshot().job?.state).toBe(state)
      expect(x.controller.hasUnresolvedWrite).toBe(false)
      expect(x.bridge.getOperation).toHaveBeenCalledWith(job.operationId)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      expect(x.bridge.previewProjectChangeset).toHaveBeenCalledTimes(1)
      x.controller.editDraft({ description: 'explicit new preview' })
      await x.controller.prepare()
      expect(x.bridge.previewProjectChangeset).toHaveBeenCalledTimes(2)
    }
  })

  it('retains terminal facts and unresolved restoration when operation crosscheck fails', async () => {
    for (const code of ['NOT_FOUND', 'TIMEOUT', 'INVALID_STATE']) {
      const x = setup()
      await x.acceptedCommit()
      const before = x.controller.getSnapshot().job!,
        done = unsuccessful(before, 'failed')
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      x.bridge.getOperation.mockResolvedValueOnce({
        ok: false,
        error: {
          ...failed.error,
          code,
          retryable: false,
        },
      } as never)
      await x.controller.refreshJob()
      expect(x.controller.getSnapshot().job).toEqual(done)
      expect(x.controller.getSnapshot().error?.code).toBe(code)
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.controller.getSnapshot().notice).toContain('读取错误不代表未提交')
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    }
  })

  it('never declares failed/cancelled rollback when either actual reply retains a marker', async () => {
    for (const evidence of ['job', 'operation', 'mismatched-operation'] as const) {
      const x = setup()
      await x.acceptedCommit()
      const before = x.controller.getSnapshot().job!,
        done = unsuccessful(before, 'cancelled')
      if (evidence === 'job') done.commitProgress = succeeded(before).commitProgress
      expect(validateV2('job', done)).toBe(true)
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      const marker = markerFor(before)
      x.bridge.getOperation.mockResolvedValueOnce(
        ok(evidence === 'mismatched-operation' ? { ...marker, jobId: pid } : marker),
      )
      await x.controller.refreshJob()
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.controller.getSnapshot().job).toEqual(done)
      expect(x.controller.getSnapshot().jobReconciled).toBe(false)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      if (evidence === 'job') expect(x.bridge.getOperation).not.toHaveBeenCalled()
      else
        expect(x.controller.getSnapshot().operationMarker).toEqual(
          evidence === 'operation' ? marker : undefined,
        )
    }
  })

  it('preserves a known original operation marker across a later terminal-null contradiction', async () => {
    const x = setup()
    await x.edit()
    await x.controller.prepare()
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async () => {
      throw new Error('lost ACK')
    })
    await x.controller.confirmAndCommit()
    const pending = x.controller.getSnapshot().pending
    if (pending?.kind !== 'commit') throw new Error('missing original intent')
    const done = unsuccessful(x.job(pending.operationId), 'failed'),
      marker = markerFor(done)
    x.bridge.getOperation.mockResolvedValueOnce(ok(marker))
    x.bridge.getJob.mockResolvedValue(ok(done))
    await x.controller.reconcileCommit()
    await x.controller.refreshJob()
    expect(x.controller.getSnapshot().operationMarker).toEqual(marker)
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.getOperation).toHaveBeenCalledTimes(1)
  })

  it('retains a nonnull marker through failed Job lookup, later null and list-discovered terminal-null', async () => {
    const x = setup()
    await x.edit()
    await x.controller.prepare()
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async () => {
      throw new Error('lost ACK')
    })
    await x.controller.confirmAndCommit()
    const pending = x.controller.getSnapshot().pending
    if (pending?.kind !== 'commit') throw new Error('missing original intent')
    const done = unsuccessful(x.job(pending.operationId), 'failed'),
      marker = markerFor(done)
    x.bridge.getOperation.mockResolvedValueOnce(ok(marker))
    x.bridge.getJob.mockResolvedValueOnce(failed as never)
    await x.controller.reconcileCommit()
    expect(x.controller.getSnapshot().pending).toEqual(pending)
    expect(x.controller.getSnapshot().operationMarker).toEqual(marker)
    await x.controller.reconcileCommit()
    expect(x.controller.getSnapshot().operationMarker).toEqual(marker)
    x.bridge.listJobs.mockResolvedValueOnce(
      ok({
        binding: {
          projectId: pid,
          listSnapshotId: ref,
          filter: 'all',
          order: 'createdAtMs+jobId:asc',
        },
        jobs: [done],
        nextCursor: null,
      }) as never,
    )
    await x.controller.findOriginalCommitJob()
    expect(x.controller.getSnapshot().pending).toBeUndefined()
    x.bridge.getJob.mockResolvedValueOnce(ok(done))
    await x.controller.refreshJob()
    expect(x.controller.getSnapshot().job).toEqual(done)
    expect(x.controller.getSnapshot().operationMarker).toEqual(marker)
    expect(x.controller.hasUnresolvedWrite).toBe(true)
    expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    expect(x.bridge.getOperation).toHaveBeenCalledTimes(2)
  })

  it('rejects incomplete or immutable-mismatched terminal replies before no-commit reconciliation', async () => {
    for (const field of [
      'input',
      'implementation',
      'limits',
      'finishedAtMs',
      'commitProgress',
      'extra',
    ]) {
      const x = setup()
      await x.acceptedCommit()
      const before = x.controller.getSnapshot().job!,
        done = unsuccessful(before, 'failed')
      if (field === 'input')
        done.input = { ...(done.input as object), preparedPlanRef: hash('different') }
      else if (field === 'implementation')
        done.implementation = {
          ...(done.implementation as object),
          dependencyLockHash: hash('different'),
        }
      else if (field === 'limits') done.limits = { ...(done.limits as object), totalMs: 99999 }
      else if (field === 'extra') done.extra = 'not canonical'
      else delete done[field]
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      await x.controller.refreshJob()
      expect(x.controller.getSnapshot().job).toEqual(before)
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.bridge.getOperation).not.toHaveBeenCalled()
    }
  })

  it('finishes only the read-only query failure/cancellation with canonical mode none and no result claim', async () => {
    for (const state of ['failed', 'cancelled'] as const) {
      const x = setup()
      await x.acceptedQuery()
      const before = x.controller.getSnapshot().job!,
        done = unsuccessful(before, state)
      expect(validateV2('job', done)).toBe(true)
      x.bridge.getJob.mockResolvedValueOnce(ok(done))
      await x.controller.refreshJob()
      expect(x.controller.getSnapshot().jobReconciled).toBe(true)
      expect(x.controller.getSnapshot().result).toBeUndefined()
      expect(x.bridge.getOperation).not.toHaveBeenCalled()
      expect(x.bridge.getQueryResultDescriptor).not.toHaveBeenCalled()
    }
  })

  it('type-checks received API002 named source members against the integratable controller', () => {
    const root = process.cwd(),
      fixturePath = path.resolve('tests/fixtures/T04/api002-page-bridge.ts.txt')
    const manifest = JSON.parse(
      readFileSync('tests/fixtures/T04/api002-types-manifest.json', 'utf8'),
    )
    const fixture = readFileSync(fixturePath, 'utf8')
    expect(hash(fixture)).toBe(manifest.pageBridgeFixture.sha256)
    const sourcePath = path.resolve('apps/desktop/src/renderer/src/query/api002-source-types.ts')
    expect(hash(readFileSync(sourcePath, 'utf8'))).toBe(manifest.excerptsSHA256)
    const virtual = path.join(root, 'tests/fixtures/T04/api002-actual.ts'),
      proof = path.join(root, 'tests/fixtures/T04/api002-proof.ts')
    const texts = new Map([
      [virtual, fixture],
      [
        proof,
        `
      import type { ActualPageBridge } from './api002-actual';
      import {QueryWorkspaceController,type QueryWorkspaceBridge,type VerifyFullDiff} from '../../../apps/desktop/src/renderer/src/query/workspace-controller';
      declare const actual:ActualPageBridge; declare const verify:VerifyFullDiff;
      const bridge:QueryWorkspaceBridge=actual;
      const controller=new QueryWorkspaceController('project',bridge,verify);void controller;
    `,
      ],
    ])
    const options: ts.CompilerOptions = {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ESNext,
      moduleResolution: ts.ModuleResolutionKind.Bundler,
      strict: true,
      noEmit: true,
      skipLibCheck: true,
      types: ['node'],
    }
    const host = ts.createCompilerHost(options),
      read = host.readFile.bind(host),
      exists = host.fileExists.bind(host)
    host.readFile = (file) => texts.get(file) ?? read(file)
    host.fileExists = (file) => texts.has(file) || exists(file)
    host.getSourceFile = (file, version) => {
      const text = host.readFile(file)
      return text === undefined ? undefined : ts.createSourceFile(file, text, version, true)
    }
    const program = ts.createProgram([proof], options, host)
    expect(
      ts
        .getPreEmitDiagnostics(program)
        .map((d) => ts.flattenDiagnosticMessageText(d.messageText, '\n')),
    ).toEqual([])
  }, 20000)
  it('persists and restores incomplete working content without pretending it is a managed definition', async () => {
    const x = setup()
    await x.controller.open()
    x.controller.editDraft({ description: '未写完 😀' })
    await x.controller.saveDraft()
    expect(x.bridge.saveProjectDraft).toHaveBeenCalledTimes(1)
    const args = x.bridge.saveProjectDraft.mock.calls[0][0]
    expect(args.expectedGeneration).toBe(0)
    expect(args.boundDomainRevision).toBe(1)
    expect(JSON.parse(args.contentJson).draft.description).toBe('未写完 😀')
    expect(x.controller.getSnapshot().draftReceipt?.generation).toBe(1)
    expect(x.controller.getSnapshot().dirty).toBe(false)
    expect(x.controller.getSnapshot().loaded).toBeUndefined()
    expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
  })
  it('retries the frozen original draft operation after later edits and keeps the new edits dirty', async () => {
    const x = setup()
    await x.edit()
    const save = x.bridge.saveProjectDraft.getMockImplementation()!
    x.bridge.saveProjectDraft.mockImplementationOnce(async () => {
      throw new Error('lost ack')
    })
    await x.controller.saveDraft()
    const original = structuredClone(x.controller.getSnapshot().pending)
    x.controller.editDraft({ description: 'later' })
    x.bridge.saveProjectDraft.mockImplementation(save)
    await x.controller.saveDraft()
    expect(x.bridge.saveProjectDraft.mock.calls[1][0]).toEqual(
      x.bridge.saveProjectDraft.mock.calls[0][0],
    )
    expect(original?.kind).toBe('draft')
    expect(x.controller.getSnapshot().draft.description).toBe('later')
    expect(x.controller.getSnapshot().dirty).toBe(true)
  })
  it('retains a successful durable receipt when detached and advances only the original workspace generation', async () => {
    const x = setup()
    await x.edit()
    const deferred = defer<Awaited<ReturnType<typeof x.bridge.saveProjectDraft>>>()
    const original = x.bridge.saveProjectDraft.getMockImplementation()!
    x.bridge.saveProjectDraft.mockImplementationOnce(() => deferred.promise)
    const saving = x.controller.saveDraft()
    await vi.waitFor(() => expect(x.bridge.saveProjectDraft).toHaveBeenCalled())
    const args = x.bridge.saveProjectDraft.mock.calls[0][0]
    x.controller.disconnect()
    deferred.resolve(await original(args))
    await saving
    expect(x.controller.getSnapshot().draftReceipt?.operationId).toBe(args.operationId)
    const saved = x.controller.getSnapshot().read!.workspace.draft
    expect(saved.state !== 'missing' && saved.generation).toBe(1)
  })
  it('does not first dispatch a draft into a replacement project after a delayed local digest', async () => {
    const x = setup()
    await x.edit()
    const started = defer<void>()
    const digest = defer<ArrayBuffer>()
    const originalDigest = crypto.subtle.digest.bind(crypto.subtle)
    const spy = vi.spyOn(crypto.subtle, 'digest').mockImplementationOnce(() => {
      started.resolve()
      return digest.promise
    })
    try {
      const saving = x.controller.saveDraft()
      await started.promise
      const pending = structuredClone(x.controller.getSnapshot().pending)
      if (pending?.kind !== 'draft') throw new Error('expected original draft intent')
      // The App fences this view synchronously before selecting another project.
      // A global named bridge would otherwise target that newly selected project.
      x.controller.disconnect()
      digest.resolve(
        await originalDigest('SHA-256', new TextEncoder().encode(pending.args.contentJson)),
      )
      await saving
      expect(x.bridge.saveProjectDraft).not.toHaveBeenCalled()
      expect(x.controller.getSnapshot().pending).toEqual(pending)
      expect(x.controller.getSnapshot().dirty).toBe(true)
      // Return to the original project: an explicit retry keeps its exact intent.
      x.controller.connect()
      await x.controller.saveDraft()
      expect(x.bridge.saveProjectDraft).toHaveBeenCalledExactlyOnceWith(pending.args)
      expect(x.controller.getSnapshot().draftReceipt?.operationId).toBe(pending.args.operationId)
    } finally {
      spy.mockRestore()
    }
  })
  it('finishes the original pending draft receipt after a source generation clears its read', async () => {
    for (const laterEdit of [false, true]) {
      const x = setup()
      x.controller.connect(taskView(1, []))
      await x.edit()
      const started = defer<void>(),
        digest = defer<ArrayBuffer>(),
        originalDigest = crypto.subtle.digest.bind(crypto.subtle)
      const spy = vi.spyOn(crypto.subtle, 'digest').mockImplementationOnce(() => {
        started.resolve()
        return digest.promise
      })
      try {
        const saving = x.controller.saveDraft()
        await started.promise
        const pending = structuredClone(x.controller.getSnapshot().pending)
        if (pending?.kind !== 'draft') throw new Error('expected original draft intent')
        x.controller.disconnect()
        digest.resolve(
          await originalDigest('SHA-256', new TextEncoder().encode(pending.args.contentJson)),
        )
        await saving
        expect(x.bridge.saveProjectDraft).not.toHaveBeenCalled()
        expect(x.controller.getSnapshot().pending).toEqual(pending)
        // The retained A controller returns with a newer real source view.
        // This unit transport is not actual App/project-B or Store evidence.
        x.controller.connect(taskView(2, []))
        expect(x.controller.getSnapshot().read).toBeUndefined()
        expect(x.controller.getSnapshot().pending).toEqual(pending)
        expect(x.controller.hasUnresolvedWrite).toBe(true)
        if (laterEdit) x.controller.editDraft({ description: 'later retained A edit' })
        await x.controller.saveDraft()
        expect(x.bridge.saveProjectDraft).toHaveBeenCalledExactlyOnceWith(pending.args)
        expect(x.controller.getSnapshot().draftReceipt).toEqual({
          draftSaveVersion: 1,
          projectId: pid,
          operationId: pending.args.operationId,
          operationSequence: 2,
          editor: QUERY_EDITOR,
          generation: pending.args.expectedGeneration + 1,
          boundDomainRevision: pending.args.boundDomainRevision,
          contentHash: hash(pending.args.contentJson),
          afterCheckpointRef: hash('after'),
        })
        expect(x.controller.getSnapshot().projectId).toBe(pid)
        expect(x.controller.getSnapshot().pending).toBeUndefined()
        expect(x.controller.getSnapshot().read).toBeUndefined()
        expect(x.controller.getSnapshot().draftBaseRevision).toBe(pending.args.boundDomainRevision)
        expect(x.controller.getSnapshot().dirty).toBe(laterEdit)
        expect(x.controller.getSnapshot().notice).toBe(
          laterEdit
            ? '原操作草稿已保存，当前新编辑仍未保存。'
            : '工作草稿已持久化；正式定义尚未提交。',
        )
        expect(x.controller.getSnapshot().error).toBeUndefined()
        expect(x.controller.getSnapshot().busy).toBe(false)
        expect(x.controller.hasUnresolvedWrite).toBe(false)
        expect(x.bridge.readProject).toHaveBeenCalledTimes(1)
        expect(x.bridge.loadQueryDefinition).not.toHaveBeenCalled()
        expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
        expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
        expect(x.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
      } finally {
        spy.mockRestore()
      }
    }
  })
  it('does not silently rebind a restored R0 scratch to current R1', async () => {
    const r = read(1)
    r.workspace.draft = {
      editor: QUERY_EDITOR,
      state: 'present',
      present: true,
      generation: 3,
      boundDomainRevision: 0,
      contentHash: hash('scratch'),
      contentJson: canonicalQueryJson({ version: 1, definitionId: 'q01', draft }),
    }
    const x = setup(r)
    await x.controller.open()
    await x.controller.prepare()
    expect(x.controller.getSnapshot().draftBaseRevision).toBe(0)
    expect(x.bridge.previewProjectChangeset).not.toHaveBeenCalled()
    await x.controller.saveDraft()
    expect(x.bridge.saveProjectDraft).not.toHaveBeenCalled()
    expect(x.controller.getSnapshot().pending).toBeUndefined()
    x.controller.reviewCurrentBase()
    await x.controller.prepare()
    expect(x.bridge.previewProjectChangeset).toHaveBeenCalledWith(
      expect.objectContaining({ baseRevision: 1 }),
    )
  })

  it('settles the original committed snapshot even when the current definition was changed or removed', async () => {
    const x = setup()
    await x.acceptedCommit()
    const job = x.controller.getSnapshot().job!
    x.bridge.getJob.mockResolvedValueOnce(ok(succeeded(job)))
    x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(job)))
    const saved = { ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 }
    x.bridge.loadQueryDefinition
      .mockResolvedValueOnce(ok(saved))
      .mockResolvedValueOnce(failed as never)
    x.bridge.readProject.mockResolvedValueOnce(ok(read(3)))
    await x.controller.refreshJob()
    expect(x.bridge.loadQueryDefinition.mock.calls[0][0]).toEqual({
      definitionId: 'q01',
      selection: { kind: 'historical', snapshotId: hash('snapshot2') },
    })
    expect(x.controller.getSnapshot().jobReconciled).toBe(true)
    expect(x.controller.hasUnresolvedWrite).toBe(false)
    expect(x.controller.getSnapshot().loaded).toBeUndefined()
    expect(x.controller.getSnapshot().draftBaseRevision).toBe(1)
    expect(x.controller.getSnapshot().notice).toContain('当前定义已变化或不可读')
  })

  it('reuses no old-operation list cursor and allows explicit new fixed-list reconciliation', async () => {
    const x = setup()
    await x.edit()
    await x.controller.prepare()
    const commit = x.bridge.commitProjectChangeSet.getMockImplementation()!
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async () => {
      throw new Error('lost')
    })
    await x.controller.confirmAndCommit()
    await x.controller.findOriginalCommitJob()
    expect(x.controller.getSnapshot().reconcileList?.cursor).toBeNull()
    x.controller.restartCommitList()
    await x.controller.findOriginalCommitJob()
    expect(x.bridge.listJobs.mock.calls[1][0]).toEqual({
      filter: 'all',
      pageSize: 100,
      listSnapshotId: null,
      cursor: null,
    })
    x.bridge.commitProjectChangeSet.mockImplementationOnce(commit)
    await x.controller.recoverOriginalCommit()
    const job = x.controller.getSnapshot().job!
    x.bridge.getJob.mockResolvedValueOnce(ok(succeeded(job)))
    x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(job)))
    const saved = { ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 }
    x.bridge.loadQueryDefinition.mockResolvedValue(ok(saved))
    x.bridge.readProject.mockResolvedValue(ok(read(2)))
    await x.controller.refreshJob()
    expect(x.controller.hasUnresolvedWrite).toBe(false)
    Object.assign(x.project, read(2))
    Object.assign(x.preview, { baseRevision: 2, inputSnapshotId: hash('snapshot2') })
    Object.assign(x.confirmation, { inputSnapshotId: hash('snapshot2') })
    x.controller.editDraft({ description: 'second operation' })
    await x.controller.prepare()
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async () => {
      throw new Error('lost second')
    })
    await x.controller.confirmAndCommit()
    await x.controller.findOriginalCommitJob()
    expect(x.bridge.listJobs.mock.calls.at(-1)?.[0]).toEqual({
      filter: 'all',
      pageSize: 100,
      listSnapshotId: null,
      cursor: null,
    })
    expect(x.bridge.commitProjectChangeSet.mock.calls[0][0].operationId).not.toBe(
      x.bridge.commitProjectChangeSet.mock.calls.at(-1)?.[0].operationId,
    )
  })

  it('makes a verified managed commit executable only after original marker and historical/current reload', async () => {
    const x = setup()
    await x.acceptedCommit()
    const job = x.controller.getSnapshot().job!
    x.bridge.getJob.mockResolvedValueOnce(ok(succeeded(job)))
    x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(job)))
    const saved = { ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 }
    x.bridge.loadQueryDefinition.mockResolvedValue(ok(saved))
    x.bridge.readProject.mockResolvedValue(ok(read(2)))
    await x.controller.refreshJob()
    expect(x.controller.getSnapshot().loaded).toEqual(saved)
    expect(x.controller.getSnapshot().draftBaseRevision).toBe(2)
    x.bridge.executeSavedQuery.mockImplementation(async (args) =>
      ok({
        operationId: args.operationId,
        acceptedJob: {
          ...x.job(args.operationId, 'query.execute'),
          inputSnapshotId: hash('snapshot2'),
          input: {
            ...(x.job(args.operationId, 'query.execute').input as Record<string, unknown>),
            inputSnapshotId: hash('snapshot2'),
          },
        },
        watch: { state: 'subscribed' },
      }),
    )
    await x.controller.execute()
    expect(x.bridge.executeSavedQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        loadRef: saved.loadRef,
        visibleDraft: draft,
        selection: { kind: 'current' },
      }),
    )
    expect(x.controller.getSnapshot().jobKind).toBe('execute')
  })

  it('increments document identity on successful replacement so local builder state resets', async () => {
    const x = setup()
    const first = x.controller.getSnapshot().document
    await x.controller.open()
    const opened = x.controller.getSnapshot().document
    expect(opened).toBeGreaterThan(first)
    x.controller.setDefinitionId('q01')
    await x.controller.load()
    expect(x.controller.getSnapshot().document).toBeGreaterThan(opened)
    const loaded = x.controller.getSnapshot().document
    x.controller.replaceDraft({ ...draft, source: 'model' })
    expect(x.controller.getSnapshot().document).toBeGreaterThan(loaded)
    const html = renderToStaticMarkup(
      createElement(QueryWorkspacePage, { controller: x.controller }),
    )
    expect(html).toContain('生成可见 SPARQL 草稿')
    expect(html).toMatch(/<button disabled="">生成可见 SPARQL 草稿<\/button>/)
    expect(html).toContain('当前页面不调用模型')
  })
  it('requires full Diff verifier success and explicit confirmation before submitting', async () => {
    const x = setup()
    await x.edit()
    x.verifier.mockRejectedValueOnce(new Error('wrong hash'))
    await x.controller.prepare()
    expect(x.controller.getSnapshot().preview).toBeUndefined()
    expect(x.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
    await x.controller.prepare()
    expect(x.verifier).toHaveBeenCalledWith(
      expect.objectContaining({ previewHash: x.preview.previewHash }),
      expect.any(Array),
    )
    expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    await x.controller.confirmAndCommit()
    expect(x.bridge.confirmProjectChangeset).toHaveBeenCalledWith({
      previewHash: x.preview.previewHash,
      completionCursor: ref,
    })
    expect(x.controller.getSnapshot().job?.state).toBe('queued')
    expect(x.controller.getSnapshot().loaded).toBeUndefined()
    expect(x.controller.hasUnresolvedWrite).toBe(true)
  })
  it('invalidates a verified preview when editing or changing input', async () => {
    const x = setup()
    await x.edit()
    await x.controller.prepare()
    x.controller.editDraft({ name: 'changed' })
    await x.controller.confirmAndCommit()
    expect(x.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
    await x.controller.prepare()
    x.controller.setSelection({ kind: 'historical', snapshotId: hash('old') })
    await x.controller.confirmAndCommit()
    expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
  })
  it('retains exact commit confirmation and original operation after lost ACK, never replacing null marker with success', async () => {
    const x = setup()
    await x.edit()
    await x.controller.prepare()
    const commit = x.bridge.commitProjectChangeSet.getMockImplementation()!
    x.bridge.commitProjectChangeSet.mockImplementationOnce(async () => {
      throw new Error('ack lost')
    })
    await x.controller.confirmAndCommit()
    const pending = x.controller.getSnapshot().pending
    expect(pending?.kind === 'commit' && pending.confirmation).toEqual(x.confirmation)
    await x.controller.reconcileCommit()
    expect(x.controller.getSnapshot().pending).toEqual(pending)
    await x.controller.findOriginalCommitJob()
    expect(x.controller.getSnapshot().pending).toEqual(pending)
    x.bridge.commitProjectChangeSet.mockImplementation(async (args) =>
      ok(unsuccessful((await commit(args)).data, 'failed')),
    )
    await x.controller.recoverOriginalCommit()
    expect(x.bridge.commitProjectChangeSet.mock.calls[1][0]).toEqual(
      x.bridge.commitProjectChangeSet.mock.calls[0][0],
    )
    expect(x.bridge.confirmProjectChangeset).toHaveBeenCalledTimes(1)
    expect(x.controller.getSnapshot().job?.state).toBe('failed')
  })
  it('keeps higher task stateVersion when an older getJob response arrives late', async () => {
    const x = setup()
    x.controller.connect()
    await x.acceptedQuery()
    const before = x.controller.getSnapshot().job!,
      pending = defer<ReturnType<typeof ok<JobView>>>()
    x.bridge.getJob.mockImplementationOnce(() => pending.promise)
    const refreshing = x.controller.refreshJob()
    x.emit({ kind: 'job', generation: 1, job: unsuccessful(before, 'cancelled', 4) })
    pending.resolve(ok({ ...before, state: 'running', stateVersion: 2 }))
    await refreshing
    expect(x.controller.getSnapshot().job?.state).toBe('cancelled')
    expect(x.controller.getSnapshot().job?.stateVersion).toBe(4)
    x.emit({ kind: 'job', generation: 1, job: { ...before, state: 'running', stateVersion: 4 } })
    expect(x.controller.getSnapshot().job?.state).toBe('cancelled')
  })
  it('does not publish a late current load into a document switched to historical', async () => {
    const x = setup()
    await x.acceptedCommit()
    const job = x.controller.getSnapshot().job!
    x.bridge.getJob.mockResolvedValueOnce(ok(succeeded(job)))
    x.bridge.getOperation.mockResolvedValueOnce(ok(markerFor(job)))
    x.bridge.readProject.mockResolvedValueOnce(ok(read(2)))
    const pending = defer<Awaited<ReturnType<typeof x.bridge.loadQueryDefinition>>>()
    const saved = { ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 }
    x.bridge.loadQueryDefinition
      .mockResolvedValueOnce(ok(saved))
      .mockImplementationOnce(() => pending.promise)
    const refreshing = x.controller.refreshJob()
    await vi.waitFor(() => expect(x.bridge.loadQueryDefinition).toHaveBeenCalledTimes(2))
    x.controller.setSelection({ kind: 'historical', snapshotId: hash('old') })
    pending.resolve(
      ok({ ...x.loaded(), inputSnapshotId: hash('snapshot2'), baseProjectRevision: 2 }),
    )
    await refreshing
    expect(x.controller.getSnapshot().selection.kind).toBe('historical')
    expect(x.controller.getSnapshot().loaded).toBeUndefined()
    expect(x.controller.getSnapshot().jobReconciled).toBe(true)
  })
  it('keeps real accepted query identity when watch subscription is pending and rejects unsupported derived scope', async () => {
    const x = setup()
    await x.controller.open()
    x.controller.setDefinitionId('q01')
    await x.controller.load()
    x.controller.editDraft({ scope: 'asserted+derived' })
    await x.controller.execute()
    expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    x.controller.editDraft({ scope: 'asserted' })
    const execute = x.bridge.executeSavedQuery.getMockImplementation()!
    x.bridge.executeSavedQuery.mockImplementation(
      async (args) =>
        ({
          ...(await execute(args)),
          data: {
            operationId: args.operationId,
            acceptedJob: x.job(args.operationId, 'query.execute'),
            watch: { state: 'pending', error: failed.error },
          },
        }) as never,
    )
    await x.controller.execute()
    expect(x.controller.getSnapshot().job?.jobId).toBe(jid)
    expect(x.controller.getSnapshot().watchPending).toBe(true)
    expect(x.bridge.executeSavedQuery).toHaveBeenCalledTimes(1)
  })
  it('reports the actual cancellation disposition, keeping ACK separate from terminal', async () => {
    const x = setup()
    await x.acceptedQuery()
    await x.controller.cancel()
    expect(x.controller.getSnapshot().cancelRequested).toBe(false)
    expect(x.controller.getSnapshot().notice).toContain('任务已是终态')
    expect(x.controller.getSnapshot().job?.state).toBe('queued')
  })
  it('fences source view generation and preserves edits and original accepted jobs', async () => {
    const x = setup()
    x.controller.connect()
    await x.acceptedQuery()
    const job = x.controller.getSnapshot().job!
    x.emit({ kind: 'job', generation: 3, job })
    x.emit({ kind: 'job', generation: 4, job })
    expect(x.controller.getSnapshot().loaded).toBeUndefined()
    expect(x.controller.getSnapshot().read).toBeUndefined()
    expect(x.controller.getSnapshot().job?.jobId).toBe(jid)
    x.emit({ kind: 'job', generation: 3, job: unsuccessful(job, 'cancelled', 9) })
    expect(x.controller.getSnapshot().job?.state).toBe('queued')
  })
  it('keeps canonical Unicode ordering, rejects lone surrogates and nonfinite values', () => {
    expect(canonicalQueryJson({ '😀': 'x', '\ue000': 'y' })).toBe('{"":"y","😀":"x"}')
    expect(() => canonicalQueryJson({ text: '\ud800' })).toThrow()
    expect(() => canonicalQueryJson({ value: NaN })).toThrow()
  })
  it('restores a separate historical read without losing the current accepted or UNKNOWN write responsibility', async () => {
    for (const mode of ['active', 'unknown']) {
      const x = setup()
      if (mode === 'unknown')
        x.bridge.commitProjectChangeSet.mockImplementationOnce(async () => {
          throw new Error('lost ACK')
        })
      await x.acceptedCommit()
      const pending = structuredClone(x.controller.getSnapshot().pending),
        current = structuredClone(x.controller.getSnapshot().job)
      const old = unsuccessful({ ...x.job(pid, 'query.execute'), jobId: ref }, 'cancelled')
      x.bridge.listJobs.mockResolvedValueOnce(
        ok({
          binding: {
            projectId: pid,
            listSnapshotId: ref,
            filter: 'terminal',
            order: 'createdAtMs+jobId:asc',
          },
          jobs: [old],
          nextCursor: null,
        }) as never,
      )
      x.bridge.getJob.mockResolvedValueOnce(ok(old))
      await x.controller.readQueryHistory(true)
      await x.controller.restoreQueryResult(old.jobId)
      expect(x.controller.getSnapshot().job).toEqual(current)
      expect(x.controller.getSnapshot().pending).toEqual(pending)
      expect(x.controller.hasUnresolvedWrite).toBe(true)
      expect(x.controller.getSnapshot().historySelection).toEqual(old)
      expect(x.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    }
  })
})
