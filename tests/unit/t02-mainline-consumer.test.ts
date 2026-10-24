/** Unit consumers of the fixed API002 shape. Mocks are not engine/Electron evidence. */
import { createHash } from 'node:crypto'
import { describe, expect, it, vi } from 'vitest'
import type { BridgeResult, JobView } from '@ontolearn/contracts'
import type {
  DomainRead,
  DiffPage,
  MainlineTaskUpdate,
  OntologyMainlineBridge,
  Preview,
  PreviewArgs,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-api'
import { readFullDiff } from '../../apps/desktop/src/renderer/src/ontology/mainline-diff'
import {
  manualFactPlan,
  newManualFactPlan,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-facts'
import { OntologySession } from '../../apps/desktop/src/renderer/src/ontology/mainline-session'
import { OntologyOperationBook } from '../../apps/desktop/src/renderer/src/ontology/mainline-operations'

const hash = (value: Uint8Array) => createHash('sha256').update(value).digest('hex')
const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
const failed = <T>(): Extract<BridgeResult<T>, { ok: false }> => ({
  ok: false,
  error: { code: 'INTERNAL_ERROR', messageKey: 'engine.internal', params: {}, retryable: false },
})
const source = (): DomainRead => ({
  readVersion: 1,
  projectId: 'project-a',
  inputSnapshotId: 'a'.repeat(64),
  workspace: { draft: { state: 'missing', editor: 'ontology-transaction' } },
  domain: {
    projectRevision: 7,
    dependencyVector: { 'facts:asserted': 2 },
    state: {
      definitions: [{ layer: 'ontology', id: 'all', payload: '{"triples":[],"references":[]}' }],
      facts: [
        {
          id: 'f'.repeat(64),
          subject: 'urn:001',
          predicate: 'urn:name',
          object: '"泵站A"@zh',
          owner: null,
          source_row: null,
          managed_value: null,
        },
      ],
      mappingState: {},
    },
  },
})
function documentFor(preview: Preview, rows: unknown[]) {
  const bytes = new TextEncoder().encode(JSON.stringify(rows))
  // Deliberately split a multibyte UTF-8 codepoint between raw segments.
  const split = Math.max(1, bytes.findIndex((value) => value > 127) + 1)
  const parts = [bytes.slice(0, split), bytes.slice(split)]
  let offset = 0
  const segments = parts.map((part, ordinal) => {
    const descriptor = {
      ordinal,
      byteOffset: offset,
      rawByteLength: part.length,
      sha256: hash(part),
    }
    offset += part.length
    return { ...descriptor, dataBase64: Buffer.from(part).toString('base64') }
  })
  preview.manifest = {
    documentKind: preview.status === 'ready' ? 'diff' : 'undo-impact',
    documentHash: hash(bytes),
    totalBytes: bytes.length,
    segmentCount: segments.length,
    segments: segments.map(({ ordinal, byteOffset, rawByteLength, sha256 }) => ({
      ordinal,
      byteOffset,
      rawByteLength,
      sha256,
    })),
  }
  return segments.map((segment, index): DiffPage => ({
    projectId: preview.projectId,
    previewHash: preview.previewHash,
    documentKind: preview.manifest.documentKind,
    documentHash: hash(bytes),
    segments: [segment],
    nextCursor: `cursor-${index}`,
    complete: index === segments.length - 1,
  }))
}
function harness() {
  let read = source()
  let preview!: Extract<Preview, { status: 'ready' }>
  let pages: DiffPage[] = []
  let job!: JobView
  let operation: Record<string, unknown> | null = null
  let listener: ((update: MainlineTaskUpdate) => void) | undefined
  const release = vi.fn()
  const bridge: OntologyMainlineBridge = {
    saveProjectDraft: vi.fn(async (args) => {
      const contentHash = hash(new TextEncoder().encode(args.contentJson))
      read = {
        ...read,
        workspace: {
          draft: {
            state: 'present',
            editor: args.editor,
            generation: args.expectedGeneration + 1,
            present: true,
            boundDomainRevision: args.boundDomainRevision,
            contentHash,
            contentJson: args.contentJson,
          },
        },
      }
      return ok({
        draftSaveVersion: 1 as const,
        projectId: read.projectId,
        operationId: args.operationId,
        operationSequence: 1,
        editor: args.editor,
        generation: args.expectedGeneration + 1,
        boundDomainRevision: args.boundDomainRevision,
        contentHash,
        afterCheckpointRef: 'a'.repeat(64),
      })
    }),
    readProject: vi.fn(async () => ok(structuredClone(read))),
    getActiveProject: vi.fn(async () =>
      ok({
        projectId: read.projectId,
        projectRevision: read.domain.projectRevision,
        inputSnapshotId: read.inputSnapshotId,
        dependencyVector: read.domain.dependencyVector,
        formatVersion: 3 as const,
      }),
    ),
    previewProjectChangeset: vi.fn(async (args: PreviewArgs) => {
      preview = {
        status: 'ready',
        projectId: read.projectId,
        baseRevision: args.baseRevision,
        previewHash: 'b'.repeat(64),
        preparedPlanRef: 'c'.repeat(64),
        inputSnapshotId: read.inputSnapshotId,
        parametersHash: 'd'.repeat(64),
        intent: args.intent,
        targetOperationId: args.intent === 'undo' ? args.targetOperationId : null,
        summary: '真实接口形状的单测数据',
        manifest: {} as Preview['manifest'],
      }
      pages = documentFor(preview, [{ kind: '事实变化', before: '泵站A', after: '泵站B' }])
      return ok(structuredClone(preview))
    }),
    getProjectDiffPage: vi.fn(async (args) =>
      ok(structuredClone(pages[args.cursor === null ? 0 : 1]!)),
    ),
    confirmProjectChangeset: vi.fn(async () =>
      ok({
        projectId: preview.projectId,
        previewHash: preview.previewHash,
        preparedPlanRef: preview.preparedPlanRef,
        inputSnapshotId: preview.inputSnapshotId,
        parametersHash: preview.parametersHash,
        confirmationRef: crypto.randomUUID(),
      }),
    ),
    commitProjectChangeSet: vi.fn(async (args) => {
      job = {
        capability: 'changeset.commit',
        confirmationRef: args.confirmation.confirmationRef,
        createdAtMs: 1,
        updatedAtMs: 1,
        finishedAtMs: null,
        implementation: {
          executionSemanticsVersion: 'unit',
          engineVersion: 'unit',
          dependencyLockHash: '0'.repeat(64),
        },
        limits: { requestMs: 1000 },
        projectId: read.projectId,
        operationId: args.operationId,
        jobId: crypto.randomUUID(),
        inputSnapshotId: preview.inputSnapshotId,
        state: 'queued',
        stateVersion: 0,
        resultRef: null,
        error: null,
        input: {
          preparedPlanRef: preview.preparedPlanRef,
          inputSnapshotId: preview.inputSnapshotId,
          parametersHash: preview.parametersHash,
          scope: 'asserted',
          definitionId: 'changeset',
          derivedResultIds: [],
        },
        commitProgress: { mode: 'atomic', operationId: args.operationId, marker: null },
      }
      return ok(structuredClone(job))
    }),
    getJob: vi.fn(async () => ok(structuredClone(job))),
    listJobs: vi.fn(async () =>
      ok({
        binding: {
          projectId: read.projectId,
          filter: 'all',
          listSnapshotId: 'list-one',
          order: 'createdAtMs+jobId:asc',
        },
        jobs: job ? [structuredClone(job)] : [],
        nextCursor: null,
      }),
    ),
    getOperation: vi.fn(async () => ok(structuredClone(operation))),
    cancelJob: vi.fn(async () => ok({})),
    onTaskUpdate: vi.fn((fn) => {
      listener = fn
      return release
    }),
  }
  const session = new OntologySession(bridge, new OntologyOperationBook())
  session.connect()
  return {
    bridge,
    session,
    release,
    emit: (update: MainlineTaskUpdate) => listener?.(update),
    source: () => read,
    setSource: (next: DomainRead) => {
      read = next
    },
    job: () => job,
    setJob: (next: JobView) => {
      job = next
    },
    setMarker: (next: Record<string, unknown> | null) => {
      operation = next
    },
    pages: () => pages,
    finish: () => {
      job = { ...job, state: 'succeeded', stateVersion: 2 }
      operation = {
        projectId: read.projectId,
        operationId: job.operationId,
        jobId: job.jobId,
        planHash: 'e'.repeat(64),
        projectRevision: read.domain.projectRevision + 1,
        beforeSnapshotId: read.inputSnapshotId,
        afterSnapshotId: 'f'.repeat(64),
      }
      job.commitProgress = {
        mode: 'atomic',
        operationId: job.operationId,
        marker: {
          planHash: operation.planHash,
          projectRevision: operation.projectRevision,
          beforeSnapshotId: operation.beforeSnapshotId,
          afterSnapshotId: operation.afterSnapshotId,
        },
      }
      read = {
        ...read,
        inputSnapshotId: 'f'.repeat(64),
        domain: { ...read.domain, projectRevision: read.domain.projectRevision + 1 },
      }
    },
  }
}

describe('T02 actual named API consumer state (unit only)', () => {
  it('requires complete Diff and explicit confirmation, queued is not saved, then reconciles', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ edits: { ['f'.repeat(64)]: '"泵站B"@zh' } })
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().prepared?.rows).toEqual([
      { kind: '事实变化', before: '泵站A', after: '泵站B' },
    ])
    await h.session.confirm()
    expect(h.bridge.saveProjectDraft).toHaveBeenCalledOnce()
    const bookmark = vi.mocked(h.bridge.saveProjectDraft).mock.calls[0]![0]
    expect(bookmark.editor).toBe('ontology-transaction')
    expect(JSON.parse(bookmark.contentJson).pending.operationId).toBe(h.job().operationId)
    expect(vi.mocked(h.bridge.saveProjectDraft).mock.invocationCallOrder[0]).toBeLessThan(
      vi.mocked(h.bridge.commitProjectChangeSet).mock.invocationCallOrder[0]!,
    )
    expect(h.session.getSnapshot().phase).toBe('pending')
    expect(h.session.getSnapshot().receipt).toBeUndefined()
    expect(h.bridge.confirmProjectChangeset).toHaveBeenCalledWith({
      previewHash: 'b'.repeat(64),
      completionCursor: 'cursor-1',
    })
    h.finish()
    await h.session.reconcile()
    expect(h.session.getSnapshot().phase).toBe('saved')
    expect(h.session.getSnapshot().source?.domain.projectRevision).toBe(8)
    expect(h.session.getSnapshot().receipt?.operationId).toBe(h.job().operationId)
    expect(h.bridge.readProject).toHaveBeenCalledTimes(2)
    h.session.dispose()
    expect(h.release).toHaveBeenCalledOnce()
  })
  it('undo reads a new base and repeats full preview/confirmation under a new operation ID', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    const original = h.job().operationId
    h.finish()
    await h.session.reconcile()
    await h.session.prepareUndo()
    expect(h.bridge.previewProjectChangeset).toHaveBeenLastCalledWith({
      baseRevision: 8,
      intent: 'undo',
      targetOperationId: original,
    })
    expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    await h.session.confirm()
    expect(h.job().operationId).not.toBe(original)
    expect(h.bridge.confirmProjectChangeset).toHaveBeenCalledTimes(2)
  })
  it('retains the original unknown operation and does not replay or create another write', async () => {
    const h = harness()
    vi.mocked(h.bridge.commitProjectChangeSet).mockImplementationOnce(async () => failed())
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    const original = h.session.getSnapshot().pending?.operationId
    expect(original).toBeTruthy()
    await h.session.reconcile()
    await h.session.prepare({ remove: ['another'] })
    await h.session.confirm()
    expect(h.session.getSnapshot().phase).toBe('unknown')
    expect(h.session.getSnapshot().pending?.operationId).toBe(original)
    expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
  })
  it('cancel acknowledgement does not declare rollback and a later real success survives', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    await h.session.cancel()
    expect(h.session.getSnapshot().pending).toBeDefined()
    expect(h.session.getSnapshot().receipt).toBeUndefined()
    h.finish()
    await h.session.reconcile()
    expect(h.session.getSnapshot().receipt).toBeDefined()
  })
  it('rejects old revisions before confirmation and never calls commit', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    h.setSource({ ...h.source(), inputSnapshotId: '9'.repeat(64) })
    await h.session.confirm()
    expect(h.session.getSnapshot().error).toBe('STALE_CONTEXT')
    expect(h.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
  })
  it('ignores a late preview after context invalidation and allows a fresh read', async () => {
    const h = harness()
    await h.session.read()
    const actual = h.bridge.previewProjectChangeset
    let release!: () => void
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    h.bridge.previewProjectChangeset = async (args) => {
      await gate
      return actual(args)
    }
    const pending = h.session.prepare({ remove: ['f'.repeat(64)] })
    await Promise.resolve()
    h.session.invalidate()
    release()
    await pending
    expect(h.session.getSnapshot().prepared).toBeUndefined()
    expect(h.session.getSnapshot().phase).toBe('idle')
    await h.session.read()
    expect(h.session.getSnapshot().stale).toBe(false)
  })
  it('retains a known committed receipt when refreshing the current projection fails', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.finish()
    vi.mocked(h.bridge.readProject).mockResolvedValueOnce(failed())
    await h.session.reconcile()
    expect(h.session.getSnapshot().receipt?.operationId).toBe(h.job().operationId)
    expect(h.session.getSnapshot().stale).toBe(true)
    expect(h.session.getSnapshot().pending).toBeUndefined()
  })
  it('rejects an unbound receipt without claiming success', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.finish()
    h.setMarker({ projectId: 'another', operationId: h.job().operationId })
    await h.session.reconcile()
    expect(h.session.getSnapshot().phase).toBe('unknown')
    expect(h.session.getSnapshot().receipt).toBeUndefined()
  })
  it('does not enter a domain write if the durable attempted-operation bookmark fails', async () => {
    const h = harness()
    vi.mocked(h.bridge.saveProjectDraft).mockResolvedValueOnce(failed())
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().receipt).toBeUndefined()
    expect(h.session.getSnapshot().pending).toBeUndefined()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    expect(h.session.getSnapshot().phase).toBe('ready')
  })
  it('closes a saved bookmark after context invalidation before the actual domain call', async () => {
    const h = harness()
    const actual = h.bridge.saveProjectDraft
    vi.mocked(h.bridge.saveProjectDraft).mockImplementationOnce(async (args) => {
      const reply = await actual(args)
      h.session.invalidate()
      return reply
    })
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().pending).toBeUndefined()
    expect(h.session.getSnapshot().receipt).toBeUndefined()
    const draft = h.source().workspace.draft
    expect(draft.state === 'present' && JSON.parse(draft.contentJson!).pending).toBeNull()
  })
  it('retries a failed cleanup with its original save ID/arguments instead of retrying the domain write', async () => {
    const h = harness()
    vi.mocked(h.bridge.saveProjectDraft)
      .mockResolvedValueOnce(failed())
      .mockResolvedValueOnce(failed())
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    expect(h.session.getSnapshot().pending?.unsubmitted).toBe(true)
    const cleanup = vi.mocked(h.bridge.saveProjectDraft).mock.calls[1]![0]
    await h.session.reconcile()
    expect(vi.mocked(h.bridge.saveProjectDraft).mock.calls[2]![0]).toEqual(cleanup)
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().pending).toBeUndefined()
  })
  it.each(['revision', 'generation'] as const)(
    'rebuilds only the unsubmitted UI cleanup after a returned %s CAS refusal',
    async (kind) => {
      const h = harness()
      const actualSave = h.bridge.saveProjectDraft
      let count = 0
      let bookmark!: Parameters<typeof actualSave>[0]
      h.bridge.saveProjectDraft = vi.fn(async (args) => {
        count++
        if (count === 1) {
          bookmark = args
          return failed()
        }
        if (count === 2) {
          if (kind === 'revision')
            h.setSource({ ...h.source(), domain: { ...h.source().domain, projectRevision: 8 } })
          else await actualSave(bookmark) // Late original UI bookmark wins its CAS.
        }
        const read = h.source()
        const generation =
          read.workspace.draft.state === 'missing' ? 0 : read.workspace.draft.generation
        const code =
          args.boundDomainRevision !== read.domain.projectRevision
            ? 'REVISION_CONFLICT'
            : args.expectedGeneration !== generation
              ? 'INVALID_STATE'
              : null
        if (code)
          return {
            ok: false as const,
            error: { code, messageKey: 'engine.internal', params: {}, retryable: false },
          }
        return actualSave(args)
      })
      await h.session.read()
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      await h.session.confirm()
      expect(h.session.getSnapshot().pending?.unsubmitted).toBe(true)
      expect(h.session.getSnapshot().pending?.cleanupNeedsRefresh).toBe(true)
      const rejected = vi.mocked(h.bridge.saveProjectDraft).mock.calls[1]![0]
      await h.session.reconcile()
      const replacement = vi.mocked(h.bridge.saveProjectDraft).mock.calls[2]![0]
      expect(replacement.operationId).not.toBe(rejected.operationId)
      expect(replacement.boundDomainRevision).toBe(kind === 'revision' ? 8 : 7)
      expect(replacement.expectedGeneration).toBe(kind === 'generation' ? 1 : 0)
      expect(h.session.getSnapshot().pending).toBeUndefined()
      expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    },
  )
  it('keeps original cleanup arguments when INVALID_STATE has no observed CAS change', async () => {
    const h = harness()
    vi.mocked(h.bridge.saveProjectDraft)
      .mockResolvedValueOnce(failed())
      .mockResolvedValueOnce({
        ok: false,
        error: {
          code: 'INVALID_STATE',
          messageKey: 'engine.internal',
          params: {},
          retryable: false,
        },
      })
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    const original = vi.mocked(h.bridge.saveProjectDraft).mock.calls[1]![0]
    await h.session.reconcile()
    expect(vi.mocked(h.bridge.saveProjectDraft).mock.calls[2]![0]).toEqual(original)
    expect(h.session.getSnapshot().pending).toBeUndefined()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
  })
  it('does not overwrite a different pending bookmark observed while rebasing cleanup', async () => {
    const h = harness()
    const actualSave = h.bridge.saveProjectDraft
    let count = 0
    let foreign = ''
    h.bridge.saveProjectDraft = vi.fn(async (args) => {
      count++
      if (count === 1) return failed()
      if (count === 2) {
        const bookmark = JSON.parse(
          vi.mocked(h.bridge.saveProjectDraft).mock.calls[0]![0].contentJson,
        )
        bookmark.pending.operationId = crypto.randomUUID()
        foreign = JSON.stringify(bookmark)
        await actualSave({ ...args, operationId: crypto.randomUUID(), contentJson: foreign })
        return {
          ok: false as const,
          error: {
            code: 'INVALID_STATE',
            messageKey: 'engine.internal',
            params: {},
            retryable: false,
          },
        }
      }
      return actualSave(args)
    })
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    await h.session.reconcile()
    expect(h.bridge.saveProjectDraft).toHaveBeenCalledTimes(2)
    expect(h.session.getSnapshot().pending?.unsubmitted).toBe(true)
    expect(h.session.getSnapshot().error).toBe('INVALID_STATE')
    const draft = h.source().workspace.draft
    expect(draft.state === 'present' && draft.contentJson).toBe(foreign)
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
  })
  it.each(['{"\ue000":1,"😀":2}', '{"value":1e-07}'])(
    'preserves original canonical draft bytes as opaque text: %s',
    async (original) => {
      const h = harness()
      h.setSource({
        ...h.source(),
        workspace: {
          draft: {
            editor: 'ontology-transaction',
            state: 'present',
            present: true,
            generation: 4,
            boundDomainRevision: 7,
            contentHash: hash(new TextEncoder().encode(original)),
            contentJson: original,
          },
        },
      })
      await h.session.read()
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      await h.session.confirm()
      const args = vi.mocked(h.bridge.saveProjectDraft).mock.calls[0]![0]
      expect(JSON.parse(args.contentJson).preservedDraft).toBe(original)
      expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledOnce()
    },
  )
  it('does not revive a terminal original operation from a late queued acknowledgement', async () => {
    const h = harness()
    const actual = h.bridge.commitProjectChangeSet
    let entered!: () => void
    const didEnter = new Promise<void>((resolve) => {
      entered = resolve
    })
    let release!: () => void
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    h.bridge.commitProjectChangeSet = async (args) => {
      const ack = await actual(args)
      entered()
      await gate
      return ack
    }
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    const pending = h.session.confirm()
    await didEnter
    const other = new OntologySession(h.bridge, h.session.operations)
    other.connect()
    await other.read()
    h.finish()
    await other.reconcile()
    release()
    await pending
    expect(h.session.getSnapshot().pending).toBeUndefined()
    expect(h.session.getSnapshot().receipt?.operationId).toBe(h.job().operationId)
    expect(other.getSnapshot().pending).toBeUndefined()
    other.dispose()
  })
  it('restores the same unknown operation after page/bridge remount and accepts its late ACK', async () => {
    const h = harness()
    const actual = h.bridge.commitProjectChangeSet
    let release!: () => void
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    let entered!: () => void
    const didEnter = new Promise<void>((resolve) => {
      entered = resolve
    })
    h.bridge.commitProjectChangeSet = async (args) => {
      entered()
      await gate
      return actual(args)
    }
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    const request = h.session.confirm()
    await didEnter
    const operationId = h.session.getSnapshot().pending?.operationId
    expect(operationId).toBeTruthy()
    h.session.dispose()
    const next = new OntologySession({ ...h.bridge }, h.session.operations)
    next.connect()
    await next.read()
    expect(next.getSnapshot().pending?.operationId).toBe(operationId)
    release()
    await request
    expect(next.getSnapshot().pending?.job?.jobId).toBe(h.job().jobId)
    h.finish()
    await next.reconcile()
    expect(next.getSnapshot().receipt?.operationId).toBe(operationId)
    next.dispose()
  })
  it('recovers the original ID from the owning durable draft with an empty in-memory book', async () => {
    const h = harness()
    const actual = h.bridge.commitProjectChangeSet
    h.bridge.commitProjectChangeSet = vi.fn(async (args) => {
      await actual(args)
      return failed<JobView>()
    })
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    const operationId = h.session.getSnapshot().pending?.operationId
    h.session.dispose()
    const reopened = new OntologySession(h.bridge, new OntologyOperationBook())
    reopened.connect()
    await reopened.read()
    expect(reopened.getSnapshot().pending?.operationId).toBe(operationId)
    expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    h.finish()
    await reopened.reconcile()
    expect(reopened.getSnapshot().receipt?.operationId).toBe(operationId)
    expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    reopened.dispose()
  })
  it.each(['failed', 'cancelled'] as const)(
    'recovers a lost ACK original Job reaching %s without a commit marker',
    async (terminal) => {
      const h = harness()
      const actual = h.bridge.commitProjectChangeSet
      h.bridge.commitProjectChangeSet = vi.fn(async (args) => {
        await actual(args)
        return failed<JobView>()
      })
      await h.session.read()
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      await h.session.confirm()
      expect(h.session.getSnapshot().pending?.job).toBeUndefined()
      const original = h.session.getSnapshot().pending?.operationId
      h.setJob({
        ...h.job(),
        state: terminal,
        stateVersion: h.job().stateVersion + 1,
        updatedAtMs: 2,
        finishedAtMs: 2,
        error:
          terminal === 'failed'
            ? {
                code: 'INTERNAL_ERROR',
                messageKey: 'engine.internal',
                params: {},
                retryable: false,
              }
            : null,
      })
      await h.session.reconcile()
      expect(h.bridge.listJobs).toHaveBeenCalledOnce()
      expect(h.session.getSnapshot().pending).toBeUndefined()
      expect(h.session.getSnapshot().receipt).toBeUndefined()
      expect(h.session.getSnapshot().stale).toBe(true)
      expect(h.job().operationId).toBe(original)
      expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      await h.session.read()
      expect(h.session.getSnapshot().pending).toBeUndefined()
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      expect(h.session.getSnapshot().phase).toBe('ready')
    },
  )
  it('rejects mismatched succeeded Job marker even when operation marker and input are correct', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.finish()
    h.setJob({
      ...h.job(),
      commitProgress: { mode: 'atomic', operationId: h.job().operationId, marker: {} },
    })
    await h.session.reconcile()
    expect(h.session.getSnapshot().error).toBe('INVALID_RECEIPT')
    expect(h.session.getSnapshot().receipt).toBeUndefined()
  })
  it('allows a newer current read without rebinding the original success marker', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.finish()
    h.setSource({
      ...h.source(),
      inputSnapshotId: '9'.repeat(64),
      domain: { ...h.source().domain, projectRevision: 10 },
    })
    await h.session.reconcile()
    expect(h.session.getSnapshot().receipt?.projectRevision).toBe(8)
    expect(h.session.getSnapshot().source?.domain.projectRevision).toBe(10)
    expect(h.session.getSnapshot().receipt?.afterSnapshotId).toBe('f'.repeat(64))
    expect(h.session.getSnapshot().stale).toBe(false)
  })
  it.each(['INTERNAL_ERROR', 'PERMISSION_DENIED', 'RESOURCE_LIMIT', 'NOT_FOUND'] as const)(
    'preserves an authenticated terminal Job when operation read returns %s',
    async (code) => {
      const h = harness()
      await h.session.read()
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      await h.session.confirm()
      const terminal: JobView = {
        ...h.job(),
        state: 'cancelled',
        stateVersion: 2,
        updatedAtMs: 2,
        finishedAtMs: 2,
      }
      h.setJob(terminal)
      h.emit({ kind: 'job', generation: 2, job: terminal })
      h.bridge.getOperation = vi.fn(async () => ({
        ok: false as const,
        error: { code, messageKey: 'engine.internal', params: {}, retryable: false },
      }))
      await h.session.reconcile()
      expect(h.session.getSnapshot().pending?.job).toEqual(terminal)
      expect(h.session.getSnapshot().phase).toBe('unknown')
      expect(h.session.getSnapshot().receipt).toBeUndefined()
      expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      expect(h.bridge.previewProjectChangeset).toHaveBeenCalledTimes(1)
    },
  )
  it('retains observed commit evidence across failed Job and later null operation reads', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.finish()
    const actualGetJob = h.bridge.getJob
    h.bridge.getJob = vi.fn(async () => failed<JobView>())
    await h.session.reconcile()
    const marker = h.session.getSnapshot().pending?.observedMarker
    expect(marker?.operationId).toBe(h.job().operationId)
    h.bridge.getJob = actualGetJob
    h.setMarker(null)
    h.setJob({
      ...h.job(),
      state: 'cancelled',
      stateVersion: 3,
      finishedAtMs: 3,
      updatedAtMs: 3,
      commitProgress: { mode: 'atomic', operationId: h.job().operationId, marker: null },
    })
    await h.session.reconcile()
    expect(h.session.getSnapshot().pending?.observedMarker).toEqual(marker)
    expect(h.session.getSnapshot().error).toBe('INVALID_RECEIPT')
    expect(h.session.getSnapshot().receipt).toBeUndefined()
    expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
  })
  it('does not erase a terminal event marker when operation read contradicts it', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.finish()
    const terminal = structuredClone(h.job())
    h.emit({ kind: 'job', generation: 2, job: terminal })
    h.setMarker(null)
    h.emit({ kind: 'job', generation: 2, job: { ...terminal, state: 'queued', stateVersion: 3 } })
    await h.session.reconcile()
    expect(h.session.getSnapshot().pending?.job).toEqual(terminal)
    expect(h.session.getSnapshot().phase).toBe('unknown')
    expect(h.session.getSnapshot().receipt).toBeUndefined()
  })
  it.each(['confirmation', 'derived', 'implementation', 'limits', 'version', 'timestamp', 'mode'])(
    'rejects a terminal cancellation with changed original %s',
    async (field) => {
      const h = harness()
      await h.session.read()
      await h.session.prepare({ remove: ['f'.repeat(64)] })
      await h.session.confirm()
      const bad = {
        ...h.job(),
        state: 'cancelled',
        stateVersion: 2,
        updatedAtMs: 2,
        finishedAtMs: 2,
      } as JobView
      if (field === 'confirmation') bad.confirmationRef = crypto.randomUUID()
      if (field === 'derived')
        bad.input = { ...(bad.input as Record<string, unknown>), derivedResultIds: ['other'] }
      if (field === 'implementation')
        bad.implementation = {
          ...(bad.implementation as Record<string, unknown>),
          engineVersion: 'other',
        }
      if (field === 'limits')
        bad.limits = { ...(bad.limits as Record<string, unknown>), requestMs: 999 }
      if (field === 'version') bad.stateVersion = 0
      if (field === 'timestamp') bad.finishedAtMs = 0
      if (field === 'mode') bad.commitProgress = { mode: 'none' }
      h.setJob(bad)
      await h.session.reconcile()
      expect(h.session.getSnapshot().pending?.operationId).toBe(h.job().operationId)
      expect(h.session.getSnapshot().phase).toBe('unknown')
      expect(h.session.getSnapshot().receipt).toBeUndefined()
      expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledTimes(1)
    },
  )
  it('ignores lower-generation, lower-version and same-version changed-state events', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    const current = { ...h.job(), state: 'running', stateVersion: 2 } as JobView
    h.emit({ kind: 'job', generation: 3, job: current })
    for (const [generation, job] of [
      [2, { ...current, state: 'queued', stateVersion: 4 }],
      [3, { ...current, state: 'queued', stateVersion: 1 }],
      [3, { ...current, state: 'cancelled', stateVersion: 2 }],
    ] as const)
      h.emit({ kind: 'job', generation, job: job as JobView })
    expect(h.session.getSnapshot().pending?.job).toEqual(current)
  })
  it('recovers the original Job from a restored task event and supports StrictMode cleanup/reconnect', async () => {
    const h = harness()
    const actual = h.bridge.commitProjectChangeSet
    h.bridge.commitProjectChangeSet = async (args) => {
      await actual(args)
      return failed()
    }
    await h.session.read()
    await h.session.prepare({ remove: ['f'.repeat(64)] })
    await h.session.confirm()
    h.session.dispose()
    h.session.connect()
    await h.session.read()
    h.emit({ kind: 'job', generation: 2, job: h.job() })
    expect(h.session.getSnapshot().pending?.job?.jobId).toBe(h.job().jobId)
    h.session.dispose()
    expect(h.release).toHaveBeenCalledTimes(2)
  })
})

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}

describe('T02 page effect replay with one admitted read; mock receiver only', () => {
  function oneReadAtATime(h: ReturnType<typeof harness>) {
    const gate = deferred<void>()
    const started = deferred<void>()
    const actual = h.bridge.readProject
    let busy = false
    let rejections = 0
    h.bridge.readProject = vi.fn(async (args) => {
      if (busy) {
        rejections++
        return {
          ok: false as const,
          error: {
            code: 'PERMISSION_DENIED',
            messageKey: 'engine.internal',
            params: {},
            retryable: false,
          },
        }
      }
      busy = true
      const result = await actual(args)
      started.resolve()
      await gate.promise
      busy = false
      return result
    })
    return { gate, started, rejected: () => rejections }
  }
  it('dispatches one initial read for setup-cleanup-setup without awaiting the first read', async () => {
    const h = harness()
    const receiver = oneReadAtATime(h)
    const firstCleanup = h.session.connectForPage()
    firstCleanup()
    const finalCleanup = h.session.connectForPage()
    await receiver.started.promise
    expect(h.bridge.readProject).toHaveBeenCalledOnce()
    expect(receiver.rejected()).toBe(0)
    receiver.gate.resolve()
    await vi.waitFor(() => expect(h.session.getSnapshot().stale).toBe(false))
    expect(h.session.getSnapshot().phase).toBe('idle')
    finalCleanup()
  })
  it('serializes an already dispatched read and the new attachment fresh read', async () => {
    const h = harness()
    const receiver = oneReadAtATime(h)
    const observed: number[] = []
    h.session.subscribe(() => {
      const revision = h.session.getSnapshot().source?.domain.projectRevision
      if (revision !== undefined) observed.push(revision)
    })
    const cleanup = h.session.connectForPage()
    await receiver.started.promise
    cleanup()
    const latestCleanup = h.session.connectForPage()
    await Promise.resolve()
    await Promise.resolve()
    expect(h.bridge.readProject).toHaveBeenCalledOnce()
    h.setSource({
      ...source(),
      inputSnapshotId: '8'.repeat(64),
      domain: { ...source().domain, projectRevision: 8 },
    })
    receiver.gate.resolve()
    await vi.waitFor(() => expect(h.session.getSnapshot().source?.domain.projectRevision).toBe(8))
    expect(h.bridge.readProject).toHaveBeenCalledTimes(2)
    expect(receiver.rejected()).toBe(0)
    expect(observed).not.toContain(7)
    latestCleanup()
  })
  it.each([true, false])(
    'coalesces repeated attachments; final attachment active=%s',
    async (active) => {
      const h = harness()
      const receiver = oneReadAtATime(h)
      let cleanup = h.session.connectForPage()
      await receiver.started.promise
      for (let index = 0; index < 8; index++) {
        cleanup()
        cleanup = h.session.connectForPage()
        await Promise.resolve()
        await Promise.resolve()
      }
      if (!active) cleanup()
      expect(h.bridge.readProject).toHaveBeenCalledOnce()
      receiver.gate.resolve()
      if (active) await vi.waitFor(() => expect(h.session.getSnapshot().stale).toBe(false))
      else for (let index = 0; index < 12; index++) await Promise.resolve()
      expect(h.bridge.readProject).toHaveBeenCalledTimes(active ? 2 : 1)
      expect(receiver.rejected()).toBe(0)
      cleanup()
    },
  )
  it.each(['returned-error', 'throw'] as const)(
    'releases a failed old read slot after %s',
    async (failure) => {
      const h = harness()
      const actual = h.bridge.readProject
      const gate = deferred<void>()
      const started = deferred<void>()
      let calls = 0
      h.bridge.readProject = vi.fn(async (args) => {
        if (++calls === 1) {
          started.resolve()
          await gate.promise
          if (failure === 'throw') throw new Error('ENGINE_DISCONNECTED')
          return failed<DomainRead>()
        }
        return actual(args)
      })
      const cleanup = h.session.connectForPage()
      await started.promise
      cleanup()
      const latestCleanup = h.session.connectForPage()
      gate.resolve()
      await vi.waitFor(() => expect(h.session.getSnapshot().stale).toBe(false))
      expect(h.bridge.readProject).toHaveBeenCalledTimes(2)
      expect(h.session.getSnapshot().error).toBeUndefined()
      latestCleanup()
    },
  )
  it('awaits the actual queued fresh read when an explicit read overlaps automatic read', async () => {
    const h = harness()
    const receiver = oneReadAtATime(h)
    const cleanup = h.session.connectForPage()
    await receiver.started.promise
    let finished = false
    const refresh = h.session.read().then(() => {
      finished = true
    })
    await Promise.resolve()
    expect(finished).toBe(false)
    expect(h.bridge.readProject).toHaveBeenCalledOnce()
    h.setSource({
      ...source(),
      inputSnapshotId: '8'.repeat(64),
      domain: { ...source().domain, projectRevision: 8 },
    })
    receiver.gate.resolve()
    await refresh
    expect(finished).toBe(true)
    expect(h.session.getSnapshot().source?.domain.projectRevision).toBe(8)
    expect(h.bridge.readProject).toHaveBeenCalledTimes(2)
    expect(receiver.rejected()).toBe(0)
    cleanup()
  })
  it('undo waits for its queued fresh base instead of using the old in-flight response', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    await h.session.confirm()
    h.finish()
    await h.session.reconcile()
    const original = h.session.getSnapshot().receipt!.operationId
    const receiver = oneReadAtATime(h)
    const cleanup = h.session.connectForPage()
    await receiver.started.promise
    const undo = h.session.prepareUndo()
    expect(h.bridge.previewProjectChangeset).toHaveBeenCalledTimes(1)
    h.setSource({
      ...h.source(),
      inputSnapshotId: '9'.repeat(64),
      domain: { ...h.source().domain, projectRevision: 9 },
    })
    receiver.gate.resolve()
    await undo
    expect(h.bridge.previewProjectChangeset).toHaveBeenLastCalledWith({
      baseRevision: 9,
      intent: 'undo',
      targetOperationId: original,
    })
    expect(h.bridge.readProject).toHaveBeenCalledTimes(2)
    expect(receiver.rejected()).toBe(0)
    cleanup()
  })
  it('does not dispatch a scheduled or queued read after retirement', async () => {
    const early = harness()
    const earlyCleanup = early.session.connectForPage()
    early.session.retire()
    early.session.connectForPage()()
    await Promise.resolve()
    await Promise.resolve()
    expect(early.bridge.readProject).not.toHaveBeenCalled()
    earlyCleanup()
    const h = harness()
    const receiver = oneReadAtATime(h)
    const firstCleanup = h.session.connectForPage()
    await receiver.started.promise
    firstCleanup()
    const cleanup = h.session.connectForPage()
    await Promise.resolve()
    h.session.retire()
    receiver.gate.resolve()
    for (let index = 0; index < 12; index++) await Promise.resolve()
    expect(h.bridge.readProject).toHaveBeenCalledOnce()
    expect(h.session.getSnapshot().stale).toBe(true)
    cleanup()
  })
  it('checks retirement again immediately before a queued read dispatch', async () => {
    const h = harness()
    const receiver = oneReadAtATime(h)
    let reads = 0
    h.session.subscribe(() => {
      if (h.session.getSnapshot().phase === 'reading' && ++reads === 2) h.session.retire()
    })
    const first = h.session.read()
    await receiver.started.promise
    const queued = h.session.read()
    receiver.gate.resolve()
    await Promise.all([first, queued])
    expect(h.bridge.readProject).toHaveBeenCalledOnce()
    expect(receiver.rejected()).toBe(0)
    expect(h.session.getSnapshot().stale).toBe(true)
  })
  it('does not dispatch an automatic read if cleanup occurs before the scheduled microtask', async () => {
    const h = harness()
    const cleanup = h.session.connectForPage()
    cleanup()
    await Promise.resolve()
    expect(h.bridge.readProject).not.toHaveBeenCalled()
  })
})

describe('T02 synchronous host retirement; mock bridges only', () => {
  const retireToB = (h: ReturnType<typeof harness>) => {
    h.session.retire()
    h.setSource({ ...source(), projectId: 'project-b', inputSnapshotId: '9'.repeat(64) })
  }
  it('retires irreversibly while normal StrictMode disposal remains reconnectable', async () => {
    const h = harness()
    await h.session.read()
    h.session.dispose()
    h.session.connect()
    await h.session.read()
    expect(h.bridge.onTaskUpdate).toHaveBeenCalledTimes(2)
    retireToB(h)
    h.session.connect()
    await h.session.read()
    await h.session.prepare({})
    await h.session.confirm()
    await h.session.clearUnsubmitted()
    await h.session.reconcile()
    await h.session.cancel()
    expect(h.bridge.onTaskUpdate).toHaveBeenCalledTimes(2)
    expect(h.bridge.readProject).toHaveBeenCalledTimes(2)
    expect(h.bridge.getActiveProject).not.toHaveBeenCalled()
    expect(h.bridge.saveProjectDraft).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().source?.projectId).toBe('project-a')
    expect(h.session.getSnapshot().stale).toBe(true)
  })
  it.each(['preview', 'confirmation', 'bookmark', 'domain'] as const)(
    'fences the caller microtask gap before %s dispatch',
    async (stage) => {
      const h = harness()
      await h.session.read()
      if (stage !== 'preview') await h.session.prepare({ remove: ['f'.repeat(64)] })
      const actualCurrent = h.bridge.getActiveProject
      let calls = 0
      const target = stage === 'bookmark' ? 2 : stage === 'domain' ? 3 : 1
      h.bridge.getActiveProject = vi.fn(() =>
        actualCurrent().then((result) => {
          calls++
          if (calls === target) queueMicrotask(() => queueMicrotask(() => retireToB(h)))
          return result
        }),
      )
      if (stage === 'preview') await h.session.prepare({})
      else await h.session.confirm()
      expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
      expect(h.bridge.saveProjectDraft).toHaveBeenCalledTimes(stage === 'domain' ? 1 : 0)
      if (stage === 'preview') expect(h.bridge.previewProjectChangeset).not.toHaveBeenCalled()
      if (stage === 'confirmation') expect(h.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
      expect(h.bridge.readProject).toHaveBeenCalledTimes(1)
      expect(h.session.getSnapshot().prepared).toBeUndefined()
      if (stage === 'domain')
        expect(h.session.operations.get('project-a')?.pending?.unsubmitted).toBe(true)
    },
  )
  it.each([2, 3])(
    'fences a deferred preflight response at confirmation step %i',
    async (target) => {
      const h = harness()
      await h.session.read()
      await h.session.prepare({})
      const gate = deferred<void>()
      const started = deferred<void>()
      const actual = h.bridge.getActiveProject
      let count = 0
      h.bridge.getActiveProject = vi.fn(async () => {
        const response = await actual()
        if (++count === target) {
          started.resolve()
          await gate.promise
        }
        return response
      })
      const confirming = h.session.confirm()
      await started.promise
      retireToB(h)
      gate.resolve()
      await confirming
      expect(h.bridge.saveProjectDraft).toHaveBeenCalledTimes(target === 3 ? 1 : 0)
      expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
      expect(h.bridge.readProject).toHaveBeenCalledTimes(1)
    },
  )
  it('does not dispatch a cached cleanup save or a new read after host retirement', async () => {
    const h = harness()
    vi.mocked(h.bridge.saveProjectDraft)
      .mockResolvedValueOnce(failed())
      .mockResolvedValueOnce(failed())
    await h.session.read()
    await h.session.prepare({})
    await h.session.confirm()
    expect(h.session.getSnapshot().pending?.cleanupSave).toBeDefined()
    const calls = vi.mocked(h.bridge.readProject).mock.calls.length
    retireToB(h)
    h.session.connect()
    await h.session.clearUnsubmitted()
    await h.session.reconcile()
    await h.session.read()
    expect(h.bridge.saveProjectDraft).toHaveBeenCalledTimes(2)
    expect(h.bridge.readProject).toHaveBeenCalledTimes(calls)
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.session.operations.get('project-a')?.pending?.unsubmitted).toBe(true)
  })
  it('does not dispatch cancel for an original queued Job after selection starts', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    await h.session.confirm()
    const queries = vi.mocked(h.bridge.getOperation).mock.calls.length
    retireToB(h)
    await h.session.cancel()
    await h.session.reconcile()
    expect(h.bridge.cancelJob).not.toHaveBeenCalled()
    expect(h.bridge.getOperation).toHaveBeenCalledTimes(queries)
    expect(h.session.operations.get('project-a')?.pending?.job?.jobId).toBe(h.job().jobId)
  })
  it('does not query a new selection after a previously dispatched cancel ACK arrives', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    await h.session.confirm()
    const queries = vi.mocked(h.bridge.getOperation).mock.calls.length
    const gate = deferred<void>()
    const started = deferred<void>()
    h.bridge.cancelJob = vi.fn(async () => {
      started.resolve()
      await gate.promise
      return ok({})
    })
    const cancelling = h.session.cancel()
    await started.promise
    retireToB(h)
    gate.resolve()
    await cancelling
    expect(h.bridge.cancelJob).toHaveBeenCalledOnce()
    expect(h.bridge.getOperation).toHaveBeenCalledTimes(queries)
    expect(h.session.operations.get('project-a')?.pending?.job?.jobId).toBe(h.job().jobId)
  })
  it('does not dispatch another Diff page after retirement during an already sent page', async () => {
    const h = harness()
    await h.session.read()
    const gate = deferred<void>()
    const started = deferred<void>()
    const actual = h.bridge.getProjectDiffPage
    h.bridge.getProjectDiffPage = vi.fn(async (args) => {
      const response = await actual(args)
      started.resolve()
      await gate.promise
      return response
    })
    const preparing = h.session.prepare({})
    await started.promise
    retireToB(h)
    gate.resolve()
    await preparing
    expect(h.bridge.getProjectDiffPage).toHaveBeenCalledOnce()
    expect(h.session.getSnapshot().prepared).toBeUndefined()
    expect(h.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
  })
  it('does not save a bookmark after retirement while confirmation is in flight', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    const gate = deferred<void>()
    const started = deferred<void>()
    const actual = h.bridge.confirmProjectChangeset
    h.bridge.confirmProjectChangeset = vi.fn(async (args) => {
      const response = await actual(args)
      started.resolve()
      await gate.promise
      return response
    })
    const confirming = h.session.confirm()
    await started.promise
    retireToB(h)
    gate.resolve()
    await confirming
    expect(h.bridge.saveProjectDraft).not.toHaveBeenCalled()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
  })
  it('retains an already sent draft under A without automatic cleanup or domain dispatch to B', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    const gate = deferred<void>()
    const started = deferred<void>()
    const actual = h.bridge.saveProjectDraft
    h.bridge.saveProjectDraft = vi.fn(async (args) => {
      const response = await actual(args)
      started.resolve()
      await gate.promise
      return response
    })
    const confirming = h.session.confirm()
    await started.promise
    const original = h.session.operations.get('project-a')?.pending?.operationId
    retireToB(h)
    gate.resolve()
    await confirming
    expect(h.session.operations.get('project-a')?.pending).toMatchObject({
      operationId: original,
      unsubmitted: true,
    })
    expect(h.session.operations.get('project-b')).toBeUndefined()
    expect(h.bridge.saveProjectDraft).toHaveBeenCalledOnce()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.bridge.readProject).toHaveBeenCalledTimes(1)
  })
  it('keeps a late original domain ACK without changing B ready preview or dispatching follow-up IPC', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    const gate = deferred<void>()
    const started = deferred<void>()
    const actual = h.bridge.commitProjectChangeSet
    h.bridge.commitProjectChangeSet = vi.fn(async (args) => {
      const response = await actual(args)
      started.resolve()
      await gate.promise
      return response
    })
    const confirming = h.session.confirm()
    await started.promise
    const original = structuredClone(h.job())
    retireToB(h)
    const next = new OntologySession(h.bridge, h.session.operations)
    next.connect()
    await next.read()
    await next.prepare({})
    expect(next.getSnapshot().phase).toBe('ready')
    const ready = next.getSnapshot()
    const reads = vi.mocked(h.bridge.readProject).mock.calls.length
    const queries = vi.mocked(h.bridge.getOperation).mock.calls.length
    gate.resolve()
    await confirming
    expect(next.getSnapshot()).toBe(ready)
    expect(next.getSnapshot().stale).toBe(false)
    expect(h.session.operations.get('project-a')?.pending?.job).toEqual(original)
    expect(h.session.operations.get('project-a')?.pending?.unsubmitted).toBe(false)
    expect(h.session.operations.get('project-b')).toBeUndefined()
    expect(h.bridge.readProject).toHaveBeenCalledTimes(reads)
    expect(h.bridge.getOperation).toHaveBeenCalledTimes(queries)
    expect(h.bridge.commitProjectChangeSet).toHaveBeenCalledOnce()
    next.dispose()
  })
  it('fences a synchronous retirement triggered by pending publication before the domain call', async () => {
    const h = harness()
    await h.session.read()
    await h.session.prepare({})
    const unsubscribe = h.session.subscribe(() => {
      if (h.session.getSnapshot().pending?.unsubmitted === false) retireToB(h)
    })
    await h.session.confirm()
    expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(h.session.operations.get('project-a')?.pending?.unsubmitted).toBe(true)
    expect(h.bridge.saveProjectDraft).toHaveBeenCalledOnce()
    unsubscribe()
  })
})

describe('T02 complete Diff integrity', () => {
  it.each(['project', 'hash', 'segment-order', 'bytes', 'cursor', 'truncated'])(
    'rejects %s corruption',
    async (kind) => {
      const h = harness()
      await h.session.read()
      const preview = await h.bridge.previewProjectChangeset({
        baseRevision: 7,
        intent: 'change',
        plan: {},
      })
      if (!preview.ok) throw new Error('fixture')
      const pages = h.pages()
      if (kind === 'project') pages[0]!.projectId = 'other'
      if (kind === 'hash') pages[0]!.documentHash = '0'.repeat(64)
      if (kind === 'segment-order') pages[0]!.segments[0]!.ordinal = 1
      if (kind === 'bytes') pages[0]!.segments[0]!.dataBase64 = 'eA=='
      if (kind === 'cursor') pages[1]!.nextCursor = pages[0]!.nextCursor
      if (kind === 'truncated') pages[0]!.complete = true
      await expect(readFullDiff(h.bridge, preview.data, () => {})).rejects.toThrow(
        'INVALID_CHANGESET_DOCUMENT',
      )
      expect(h.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
    },
  )
})

describe('T02 fact plan retains source records', () => {
  it('edits only the original ID and never serializes full facts or rewrites definitions', () => {
    const read = source()
    const before = structuredClone(read)
    expect(manualFactPlan(read, 'edit', 'f'.repeat(64), '"new"')).toEqual({
      edits: { ['f'.repeat(64)]: '"new"' },
    })
    expect(manualFactPlan(read, 'remove', 'f'.repeat(64), '')).toEqual({ remove: ['f'.repeat(64)] })
    expect(read).toEqual(before)
  })
  it('refuses mapped facts, overlapping supports and tombstones instead of converting them to manual', () => {
    const read = source()
    read.domain.state.facts[0]!.owner = 'mapping-one'
    expect(() => manualFactPlan(read, 'edit', 'f'.repeat(64), '"new"')).toThrow(
      'MANAGED_FACT_REQUIRES_OWNER',
    )
    read.domain.state.facts[0]!.owner = null
    read.domain.state.definitions[0]!.payload = JSON.stringify({
      triples: [{ subject: 'urn:001', predicate: 'urn:name', object: '"泵站A"@zh' }],
    })
    expect(() => manualFactPlan(read, 'remove', 'f'.repeat(64), '')).toThrow(
      'AMBIGUOUS_FACT_SUPPORT',
    )
    read.domain.state.facts[0]!.object = null
    expect(() => manualFactPlan(read, 'edit', 'f'.repeat(64), '"new"')).toThrow('FACT_NOT_FOUND')
  })
  it.each([
    ['edit', 'f'.repeat(64)],
    ['remove', 'f'.repeat(64)],
    ['edit', 'a'.repeat(64)],
    ['remove', 'a'.repeat(64)],
  ] as const)(
    'handles multi-value manual %s of record %s without touching sibling supports',
    (action, id) => {
      const read = source()
      read.domain.state.facts.push(
        { ...read.domain.state.facts[0]!, id: 'a'.repeat(64), object: '"second"@en' },
        {
          ...read.domain.state.facts[0]!,
          id: 'b'.repeat(64),
          object: null,
          owner: 'retired-mapping',
          source_row: 'old-row',
          managed_value: '"old"',
        },
      )
      read.domain.state.facts.push({
        ...read.domain.state.facts[0]!,
        id: 'c'.repeat(64),
        predicate: 'urn:other',
        object: '"managed"@en',
        owner: 'another-mapping',
        source_row: 'row-other',
        managed_value: '"managed"@en',
      })
      read.domain.state.definitions[0]!.payload = JSON.stringify({
        triples: [
          {
            subject: 'urn:OtherClass',
            predicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            object: '<http://www.w3.org/2000/01/rdf-schema#Class>',
          },
        ],
        references: [],
        entityMetadata: {
          entityMetadataVersion: 1,
          entities: {
            'urn:OtherClass': {
              identifier: 'OtherClass',
              labels: [],
              definitions: [],
              synonyms: [' 原文 '],
              examples: ['示例\n第二行'],
            },
          },
        },
        legacyOpaque: { retained: ['原内容', 7] },
      })
      read.domain.state.mappingState = { original: { keep: ['opaque', 7] } }
      const before = structuredClone(read)
      const plan = manualFactPlan(read, action, id, '"changed"@zh')
      expect(plan).toEqual(
        action === 'edit' ? { edits: { [id]: '"changed"@zh' } } : { remove: [id] },
      )
      expect(read).toEqual(before)
    },
  )
  it.each([
    ['"value"', '"value"^^<http://www.w3.org/2001/XMLSchema#string>'],
    ['"value"@zh', '"value"@en'],
    [
      '"01"^^<http://www.w3.org/2001/XMLSchema#integer>',
      '"1"^^<http://www.w3.org/2001/XMLSchema#integer>',
    ],
  ])('does not collapse distinct RDF spelling %s / %s when editing one ID', (first, second) => {
    const read = source()
    read.domain.state.facts[0]!.object = first!
    read.domain.state.facts.push({
      ...read.domain.state.facts[0]!,
      id: 'a'.repeat(64),
      object: second!,
    })
    const before = structuredClone(read)
    expect(manualFactPlan(read, 'edit', 'f'.repeat(64), '"replacement"')).toEqual({
      edits: { ['f'.repeat(64)]: '"replacement"' },
    })
    expect(read).toEqual(before) // Planner does not canonicalize lexical/datatype/language.
  })
  it.each(['owner', 'source_row', 'managed_value'] as const)(
    'keeps selected-record and same-slot mapped %s conflicts fenced',
    (field) => {
      const read = source()
      read.domain.state.facts[0]![field] = 'mapped'
      expect(() => manualFactPlan(read, 'edit', 'f'.repeat(64), '"new"')).toThrow(
        'MANAGED_FACT_REQUIRES_OWNER',
      )
      read.domain.state.facts[0]![field] = null
      read.domain.state.facts.push({
        ...read.domain.state.facts[0]!,
        id: 'a'.repeat(64),
        object: '"different"',
        [field]: 'mapped',
      })
      const before = structuredClone(read)
      for (const action of ['edit', 'remove'] as const)
        expect(() => manualFactPlan(read, action, 'f'.repeat(64), '"new"')).toThrow(
          'AMBIGUOUS_FACT_SUPPORT',
        )
      expect(read).toEqual(before)
    },
  )
  it.each(['original', 'replacement'] as const)(
    'refuses exact %s support from a second manual record',
    (overlap) => {
      const read = source()
      read.domain.state.facts.push({
        ...read.domain.state.facts[0]!,
        id: 'a'.repeat(64),
        object: overlap === 'original' ? '"泵站A"@zh' : '"new"',
      })
      const before = structuredClone(read)
      expect(() => manualFactPlan(read, 'edit', 'f'.repeat(64), '"new"')).toThrow(
        'AMBIGUOUS_FACT_SUPPORT',
      )
      if (overlap === 'original')
        expect(() => manualFactPlan(read, 'remove', 'f'.repeat(64), '')).toThrow(
          'AMBIGUOUS_FACT_SUPPORT',
        )
      expect(read).toEqual(before)
    },
  )
  it.each(['original', 'replacement'] as const)(
    'keeps exact %s definition overlap fenced in a multi-value manual slot',
    (overlap) => {
      const read = source()
      read.domain.state.facts.push({
        ...read.domain.state.facts[0]!,
        id: 'a'.repeat(64),
        object: '"second"@en',
      })
      read.domain.state.definitions[0]!.payload = JSON.stringify({
        triples: [
          {
            subject: 'urn:001',
            predicate: 'urn:name',
            object: overlap === 'original' ? '"泵站A"@zh' : '"new"',
          },
        ],
      })
      const before = structuredClone(read)
      expect(() => manualFactPlan(read, 'edit', 'f'.repeat(64), '"new"')).toThrow(
        'AMBIGUOUS_FACT_SUPPORT',
      )
      if (overlap === 'original')
        expect(() => manualFactPlan(read, 'remove', 'f'.repeat(64), '')).toThrow(
          'AMBIGUOUS_FACT_SUPPORT',
        )
      else
        expect(manualFactPlan(read, 'remove', 'f'.repeat(64), '')).toEqual({
          remove: ['f'.repeat(64)],
        })
      expect(read).toEqual(before)
    },
  )
  it('new assertions use the Store content ID without copying managed records', async () => {
    const read = source()
    const before = structuredClone(read)
    const plan = await newManualFactPlan(read, {
      subject: 'urn:002',
      predicate: 'urn:name',
      object: '"new"',
    })
    expect(plan.manual).toEqual([
      {
        id: '979e31c274423dbe08c091a4ad25f11d7cb9b19e0a9ceb34f57eab6958ce4dbb',
        subject: 'urn:002',
        predicate: 'urn:name',
        object: '"new"',
      },
    ])
    expect(read).toEqual(before)
    await expect(
      newManualFactPlan(read, { subject: 'urn:001', predicate: 'urn:name', object: '"泵站A"@zh' }),
    ).rejects.toThrow('FACT_ALREADY_EXISTS')
  })
})
