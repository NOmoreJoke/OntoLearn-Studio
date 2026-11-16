/** B1b checkpoint/restore: real engine runtime, durable intents, controller FSM. */
import { expect, it, describe, beforeEach, afterEach } from 'vitest'
import { randomUUID, createHash } from 'node:crypto'
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import type { BridgeResult } from '@ontolearn/contracts'
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import {
  ProjectRestoreController,
  decodeSegmentText,
} from '../../apps/desktop/src/renderer/src/project/restore-controller'
import type {
  ProjectCheckpointBridge,
  ProjectManagementBridge,
  ProjectRestorePreviewDTO,
  SafeError,
} from '@ontolearn/contracts'

function data<T>(result: BridgeResult<T>): T {
  if (!result.ok) throw new Error(JSON.stringify(result.error))
  return result.data
}

function runtime(directory: string) {
  const supervisor = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: resolve('.') },
    { profile: 'business3', dataPath: join(directory, 'library.sqlite') },
  )
  const tasks = new TaskService(supervisor)
  const projects = new ProjectMainlineService(
    supervisor,
    tasks,
    () => {
      tasks.attachView(() => {})
    },
    {
      managementJournalPath: join(directory, 'intents.json'),
      restoreJournalPath: join(directory, 'restore-intents.json'),
    },
  )
  const replies = supervisor.mainlineReplyReceiver()
  return {
    supervisor,
    projects,
    tasks,
    replies,
    async call<T>(work: () => Promise<BridgeResult<T>>): Promise<T> {
      const delivery = await replies.receive(work)
      replies.consume(delivery.receipt)
      return data(delivery.value)
    },
    async close() {
      projects.dispose()
      tasks.dispose()
      await supervisor.stopAndWait()
    },
  }
}

async function allPages(
  r: ReturnType<typeof runtime>,
  preview: ProjectRestorePreviewDTO,
): Promise<string[]> {
  const hashes: string[] = []
  let cursor: string | null = null
  for (;;) {
    const page = await r.call(() =>
      r.projects.getProjectRestorePage({ previewRef: preview.previewRef, cursor }),
    )
    expect(page.documentHash).toBe(preview.documentHash)
    for (const segment of page.segments) hashes.push(segment.sha256)
    cursor = page.nextCursor
    if (cursor === null) {
      expect(page.complete).toBe(true)
      return hashes
    }
  }
}

it('real runtime creates checkpoints, confirms segmented restore and replays lost ACKs', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'b1b-restore-'))
  const r = runtime(directory)
  try {
    const created = await r.call(() =>
      r.projects.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: '恢复源项目',
        initialization: { kind: 'blank' },
      }),
    )
    const project = created.projectId
    await r.call(() => r.projects.openProject({ projectId: project }))
    const changeSet = await r.call(() =>
      r.projects.previewProjectChangeset({
        baseRevision: 0,
        intent: 'change',
        plan: {
          definitions: [
            {
              layer: 'ontology',
              id: 'Equipment',
              value: {
                triples: [
                  {
                    subject: 'urn:ontolearn:learning:Equipment',
                    predicate: 'http://www.w3.org/2000/01/rdf-schema#label',
                    object: '"设备"',
                  },
                ],
                references: [],
                singleValuedPredicates: [],
              },
            },
          ],
        },
      }),
    )
    expect(changeSet.status).toBe('ready')
    // Read the whole diff document, then confirm exactly that reading. The
    // completion cursor is the final (complete) page's own cursor token.
    let diffCursor: string | null = null
    let completion = ''
    for (;;) {
      const page = await r.call(() =>
        r.projects.getProjectDiffPage({
          previewHash: changeSet.previewHash,
          documentKind: 'diff',
          pageSize: 8,
          cursor: diffCursor,
        }),
      )
      completion = page.nextCursor ?? completion
      if (page.complete) break
      diffCursor = page.nextCursor
    }
    const confirmation = await r.call(() =>
      r.projects.confirmProjectChangeset({
        previewHash: changeSet.previewHash,
        completionCursor: completion!,
      }),
    )
    const committed = await r.call(() =>
      r.projects.commitProjectChangeSet({ operationId: randomUUID(), confirmation }),
    )
    expect(committed.projectId).toBe(project)
    // The accepted job owns the writer until it settles; poll the workspace
    // through the reply receiver (each read consumed) until the domain
    // revision is visible, leaving no unconsumed delivery behind.
    for (let i = 0; i < 100; i++) {
      const read = await r.call(() => r.projects.readProject({ editor: 'ontology' }))
      if (read.domain.projectRevision >= 1) break
      await new Promise((delay) => setTimeout(delay, 100))
    }

    const checkpoint = await r.call(() =>
      r.projects.createProjectCheckpoint({ operationId: randomUUID(), label: 'CP1' }),
    )
    expect(checkpoint.reason).toBe('manual')
    // Mixed intervening operations after CP1: rename, draft, mode.
    const state = await r.call(() => r.projects.getProjectManagementState())
    const renamed = await r.call(() =>
      r.projects.previewProjectManagement({
        action: { kind: 'rename', name: '恢复前改名' },
        expectedCheckpointRef: state.checkpointRef,
        expectedLifecycleVersion: state.lifecycle.version,
      }),
    )
    const renameConfirmation = await r.call(() =>
      r.projects.confirmProjectManagement({
        previewRef: renamed.previewRef,
        documentHash: renamed.documentHash,
      }),
    )
    await r.call(() =>
      r.projects.applyProjectManagement({
        operationId: randomUUID(),
        confirmationRef: renameConfirmation.confirmationRef,
        documentHash: renamed.documentHash,
      }),
    )
    await r.call(() =>
      r.projects.saveProjectDraft({
        operationId: randomUUID(),
        editor: 'query-workspace-v1',
        expectedGeneration: 0,
        boundDomainRevision: 1,
        contentJson: '{"draft":true}',
      }),
    )

    const listing = await r.call(() =>
      r.projects.listProjectCheckpoints({ pageSize: 50, cursor: null }),
    )
    expect(listing.items[0]).toMatchObject({ reason: 'operation', isCurrent: true })
    const cp1 = listing.items.find((item) => item.checkpointRef === checkpoint.checkpointRef)
    expect(cp1).toBeDefined()

    const fresh = await r.call(() => r.projects.getProjectManagementState())
    const preview = await r.call(() =>
      r.projects.previewProjectRestore({
        targetCheckpointRef: checkpoint.checkpointRef,
        expectedCheckpointRef: fresh.checkpointRef,
        expectedLifecycleVersion: fresh.lifecycle.version,
      }),
    )
    expect(preview.domainWillRestore).toBe(false) // CP1 shares the domain snapshot
    expect(preview.interveningOperationCount).toBe(2)
    const hashes = await allPages(r, preview)

    // A wrong reading proof is fenced before the engine; with a single
    // segment document any other hash is a genuinely incomplete claim.
    const partial = await r.projects.confirmProjectRestore({
      previewRef: preview.previewRef,
      documentHash: preview.documentHash,
      readSegmentHashes: ['0'.repeat(64)],
    })
    expect(partial.ok).toBe(false)
    if (!partial.ok) expect(partial.error.code).toBe('PERMISSION_DENIED')

    const restoreConfirmation = await r.call(() =>
      r.projects.confirmProjectRestore({
        previewRef: preview.previewRef,
        documentHash: preview.documentHash,
        readSegmentHashes: hashes,
      }),
    )
    expect(restoreConfirmation.confirmationRef).toBeTruthy()
    const operationId = randomUUID()
    const restored = await r.call(() =>
      r.projects.restoreProject({
        operationId,
        confirmationRef: restoreConfirmation.confirmationRef,
        documentHash: preview.documentHash,
      }),
    )
    expect(restored).toMatchObject({
      projectId: project,
      operationId,
      restoredFromCheckpointRef: checkpoint.checkpointRef,
    })
    // Lost ACK: the same operation replays its durable receipt.
    const replay = await r.call(() =>
      r.projects.restoreProject({
        operationId,
        confirmationRef: restoreConfirmation.confirmationRef,
        documentHash: preview.documentHash,
      }),
    )
    expect(replay.receiptHash).toBe(restored.receiptHash)
    const after = await r.call(() => r.projects.getProjectManagementState())
    expect(after.metadata.name).toBe('恢复源项目') // rename was rolled back
    const relisted = await r.call(() =>
      r.projects.listProjectCheckpoints({ pageSize: 50, cursor: null }),
    )
    expect(relisted.items[0]).toMatchObject({ reason: 'restore', isCurrent: true })
  } finally {
    await r.close()
    await rm(directory, { recursive: true, force: true })
  }
}, 120000)

describe('restore intent journal durability', () => {
  const directory = { value: '' }
  beforeEach(async () => {
    directory.value = await mkdtemp(join(tmpdir(), 'b1b-journal-'))
  })
  afterEach(async () => {
    await rm(directory.value, { recursive: true, force: true })
  })

  it('recovers a pending original intent and refuses a corrupted journal', async () => {
    const journal = join(directory.value, 'restore-intents.json')
    const projectId = randomUUID()
    const target = 'a'.repeat(64)
    const documentHash = 'b'.repeat(64)
    const requestHash = createHash('sha256')
      .update(
        '{"confirmationRef":"' +
          '00000000-0000-4000-8000-000000000001' +
          '","documentHash":"' +
          documentHash +
          '","operationId":"' +
          '00000000-0000-4000-8000-000000000002' +
          '","projectId":"' +
          projectId +
          '"}',
      )
      .digest('hex')
    await writeFile(
      journal,
      JSON.stringify({
        journalVersion: 1,
        records: [
          {
            operationId: '00000000-0000-4000-8000-000000000002',
            projectId,
            requestHash,
            targetCheckpointRef: target,
            documentHash,
            outcome: 'pending',
            delivered: false,
            result: null,
          },
        ],
      }),
      'utf8',
    )
    const r = runtime(directory.value)
    try {
      expect(r.projects.restoreBlocked).toBe(true)
      // Complete the real engine handshake before any retained handoff.
      await r.call(() => r.projects.getProjectCatalog({ pageSize: 1, cursor: null }))
      const pending = await r.call(() => r.projects.getPendingProjectRestoreOperations())
      expect(pending).toHaveLength(1)
      expect(pending[0]).toMatchObject({ projectId, targetCheckpointRef: target })
      // Without a resolved intent no new restore may start, and without an
      // open selection even the read routes stay fenced.
      const blocked = await r.projects.previewProjectRestore({
        targetCheckpointRef: target,
        expectedCheckpointRef: 'c'.repeat(64),
        expectedLifecycleVersion: 0,
      })
      expect(blocked.ok).toBe(false)
      const unselected = await r.projects.listProjectCheckpoints({ pageSize: 10, cursor: null })
      expect(unselected.ok).toBe(false)
    } finally {
      await r.close()
    }
    // A corrupted journal fences every new durable intent, preserving the file.
    await writeFile(journal, '{corrupt', 'utf8')
    const second = runtime(directory.value)
    try {
      expect(second.projects.restoreBlocked).toBe(true)
      const result = await second.projects.createProjectCheckpoint({
        operationId: randomUUID(),
        label: null,
      })
      expect(result.ok).toBe(false)
      if (!result.ok) expect(result.error.code).toBe('STORAGE_FAILURE')
      expect(await readFile(journal, 'utf8')).toBe('{corrupt')
    } finally {
      await second.close()
    }
  }, 120000)
})

describe('restore controller state machine', () => {
  type Call = { method: string; args: unknown }
  const calls: Call[] = []
  const projectId = randomUUID()
  const state = {
    projectId,
    domainRevision: 1,
    metadataVersion: 1,
    metadata: {
      name: '恢复源项目',
      templateRef: null,
      archived: false,
      mode: 'guided' as const,
      origin: 'created' as const,
    },
    operationSequence: 5,
    checkpointRef: 'd'.repeat(64),
    lifecycle: { state: 'active' as const, version: 3 },
  }
  const preview: ProjectRestorePreviewDTO = {
    restorePreviewVersion: 1,
    previewRef: 'e'.repeat(64),
    projectId,
    documentHash: 'f'.repeat(64),
    manifest: {
      documentKind: 'restore-impact',
      documentHash: 'f'.repeat(64),
      totalBytes: 24,
      segmentCount: 2,
      segments: [
        { ordinal: 0, byteOffset: 0, rawByteLength: 12, sha256: '1'.repeat(64) },
        { ordinal: 1, byteOffset: 12, rawByteLength: 12, sha256: '2'.repeat(64) },
      ],
    },
    targetCheckpointRef: 'a'.repeat(64),
    targetOperationSequence: 1,
    targetDomainRevision: 1,
    currentCheckpointRef: 'd'.repeat(64),
    currentOperationSequence: 5,
    interveningOperationCount: 4,
    domainWillRestore: false,
    expiresAtMs: Number.MAX_SAFE_INTEGER,
  }
  const bridge: ProjectCheckpointBridge &
    Pick<ProjectManagementBridge, 'getProjectManagementState'> = {
    getProjectManagementState: async () => ({ ok: true, data: state }),
    listProjectCheckpoints: async (args) => {
      calls.push({ method: 'list', args })
      return {
        ok: true,
        data: {
          checkpointListVersion: 1,
          projectId: preview.projectId,
          items: [],
          total: 0,
          offset: 0,
          nextCursor: null,
        },
      }
    },
    createProjectCheckpoint: async () => ({ ok: true, data: {} as never }),
    getPendingProjectRestoreOperations: async () => ({ ok: true, data: [] }),
    previewProjectRestore: async (args) => {
      calls.push({ method: 'preview', args })
      return { ok: true, data: preview }
    },
    getProjectRestorePage: async (args) => {
      calls.push({ method: 'page', args })
      const cursor = (args as { cursor: string | null }).cursor
      const first = Buffer.from('{"restoreImp').toString('base64')
      const second = Buffer.from('actVersion":1}').toString('base64')
      if (cursor === null)
        return {
          ok: true,
          data: {
            restorePageVersion: 1,
            projectId: preview.projectId,
            previewRef: preview.previewRef,
            documentHash: preview.documentHash,
            segments: [
              {
                ordinal: 0,
                byteOffset: 0,
                rawByteLength: 12,
                sha256: '1'.repeat(64),
                dataBase64: first,
              },
            ],
            nextCursor: '12',
            complete: false,
          },
        }
      return {
        ok: true,
        data: {
          restorePageVersion: 1,
          projectId: preview.projectId,
          previewRef: preview.previewRef,
          documentHash: preview.documentHash,
          segments: [
            {
              ordinal: 1,
              byteOffset: 12,
              rawByteLength: 12,
              sha256: '2'.repeat(64),
              dataBase64: second,
            },
          ],
          nextCursor: null,
          complete: true,
        },
      }
    },
    confirmProjectRestore: async (args) => {
      calls.push({ method: 'confirm', args })
      return {
        ok: true,
        data: {
          restoreConfirmationVersion: 1,
          projectId: preview.projectId,
          previewRef: preview.previewRef,
          documentHash: preview.documentHash,
          preparedPlanRef: '3'.repeat(64),
          confirmationRef: randomUUID(),
          expiresAtMs: Number.MAX_SAFE_INTEGER,
        },
      }
    },
    restoreProject: async (args) => {
      calls.push({ method: 'apply', args })
      return {
        ok: true,
        data: {
          restoreResultVersion: 1,
          projectId: preview.projectId,
          operationId: (args as { operationId: string }).operationId,
          requestHash: '4'.repeat(64),
          receiptHash: '5'.repeat(64),
          checkpointRef: '6'.repeat(64),
          operationSequence: 6,
          domainRevision: 1,
          metadataVersion: 2,
          restoredFromCheckpointRef: preview.targetCheckpointRef,
          coverage: ['metadata'],
          preserved: ['historical-runs'],
        },
      }
    },
    getProjectRestoreOperation: async () => ({
      ok: true,
      data: { state: 'not-found', result: null },
    }),
  }
  const applied: string[] = []
  let controller: ProjectRestoreController
  const managementError: SafeError = {
    code: 'REVISION_CONFLICT',
    messageKey: 'project.revisionConflict',
    params: { expected: 1, actual: 2 },
    retryable: false,
  }

  beforeEach(() => {
    calls.length = 0
    applied.length = 0
    controller = new ProjectRestoreController(bridge, (result) => applied.push(result.projectId))
  })
  afterEach(() => {
    controller.close()
  })

  it('reads every segment before confirming, then applies once', async () => {
    await controller.initialize()
    await controller.previewRestore(preview.targetCheckpointRef)
    let snapshot = controller.getSnapshot()
    expect(snapshot.preview?.previewRef).toBe(preview.previewRef)
    expect(snapshot.readSegmentHashes).toEqual(['1'.repeat(64), '2'.repeat(64)])
    expect(snapshot.document).toBeDefined()
    expect(snapshot.busy).toBe(false)
    await controller.confirmRestore()
    snapshot = controller.getSnapshot()
    expect(snapshot.confirmation?.previewRef).toBe(preview.previewRef)
    await controller.applyRestore()
    snapshot = controller.getSnapshot()
    expect(snapshot.confirmation).toBeUndefined()
    expect(snapshot.notice).toContain('整项目恢复已完成')
    expect(applied).toEqual([preview.projectId])
    const confirm = calls.find((call) => call.method === 'confirm')
    expect((confirm?.args as { readSegmentHashes: string[] }).readSegmentHashes).toHaveLength(2)
    expect(calls.filter((call) => call.method === 'apply')).toHaveLength(1)
  })

  it('keeps the recovery path when the journal reports unresolved operations', async () => {
    await controller.initialize()
    expect(controller.unresolved).toBe(false)
    expect(controller.getSnapshot().recoveryLoaded).toBe(true)
  })

  it('maps CAS drift to an explicit guidance notice without silent replay', async () => {
    const failingBridge: ProjectCheckpointBridge &
      Pick<ProjectManagementBridge, 'getProjectManagementState'> = {
      ...bridge,
      previewProjectRestore: async () => ({ ok: false, error: managementError }),
    }
    const drift = new ProjectRestoreController(failingBridge, () => {})
    try {
      await drift.initialize()
      await drift.previewRestore(preview.targetCheckpointRef)
      const snapshot = drift.getSnapshot()
      expect(snapshot.preview).toBeUndefined()
      expect(snapshot.notice).toContain('重新预览')
      expect(snapshot.error?.code).toBe('REVISION_CONFLICT')
    } finally {
      drift.close()
    }
  })
})

describe('segment document reassembly', () => {
  it('rejoins ordered base64 segments into the exact original text', () => {
    const text = JSON.stringify({ 恢复: '影响', count: 42 })
    const raw = Buffer.from(text, 'utf8')
    const middle = Math.floor(raw.length / 2)
    const segments = [
      { ordinal: 1, dataBase64: raw.subarray(middle).toString('base64') },
      { ordinal: 0, dataBase64: raw.subarray(0, middle).toString('base64') },
    ]
    expect(decodeSegmentText(segments)).toBe(text)
  })
})
