/** B1b restore journal/fencing unit coverage: durable intents, journal refusal,
 * lost-ACK reconciliation, segmented confirm gating, late-reply fencing and the
 * restore controller/panel state machine. No OS engine process is spawned. */
import { describe, expect, it, beforeEach, afterEach } from 'vitest'
import { createHash, randomUUID } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { lstat, mkdtemp, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createElement, type ComponentType } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import {
  EngineError,
  MainlineProjectTransport,
  QueryMainReadBudget,
  QueryProjectReadTicket,
  type EngineSupervisor,
  type MainlineMethod,
} from '../../apps/desktop/src/main/engine'
import { ProjectRestoreSession } from '../../apps/desktop/src/main/project-restore-session'
import { managementCanonical } from '../../apps/desktop/src/main/project-management-session'
import { ProjectRestoreController } from '../../apps/desktop/src/renderer/src/project/restore-controller'
import type {
  BridgeResult,
  MainlineManagementItemDTO,
  PendingProjectRestoreOperationDTO,
  ProjectCheckpointBridge,
  ProjectCheckpointItemDTO,
  ProjectManagementBridge,
  ProjectRestoreConfirmationDTO,
  ProjectRestoreOperationDTO,
  ProjectRestorePageDTO,
  ProjectRestorePreviewDTO,
  ProjectRestoreResultDTO,
} from '@ontolearn/contracts'
import { matchesBusiness3Response } from '../../packages/contracts/src/v2'

const sha256 = (value: string | Buffer) => createHash('sha256').update(value).digest('hex')
const hashOf = (value: unknown) => sha256(managementCanonical(value))
const uuid = () => randomUUID()
const id = (n: number) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
const code = async (work: Promise<unknown>): Promise<string> => {
  try {
    await work
    return 'none'
  } catch (error) {
    return error instanceof EngineError ? error.error.code : `unexpected:${String(error)}`
  }
}

/* ------------------------------------------------------------------ */
/* Part A: ProjectRestoreSession against a scripted in-memory transport */
/* ------------------------------------------------------------------ */

class ScriptedBudget extends QueryMainReadBudget {
  retireClaims: Array<() => void> = []
  reserve(): void {}
  handoff(): void {}
  beforeArguments(): void {}
  existingProjectGet(): QueryProjectReadTicket {
    return new (class extends QueryProjectReadTicket {
      attachDispatch(): void {}
      release(): void {}
    })()
  }
  retainHolding(): void {}
  releaseHolding(): void {}
  onReplyConsumed(_entry: object, retire: () => void): void {
    this.retireClaims.push(retire)
  }
}

function transportFixture(sessionId = id(2)) {
  const budget = new ScriptedBudget()
  const state = { sessionId, owns: true }
  const supervisor = {
    ownsMainlineClient: () => state.owns,
    queryReadBudget: () => budget,
  } as unknown as EngineSupervisor
  const owner = { ownerId: id(9) }
  const transport = new (class extends MainlineProjectTransport {
    readonly owner = owner
    readonly supervisor = supervisor
    get engineSessionId(): string | undefined {
      return state.sessionId
    }
    get selected(): undefined {
      return undefined
    }
    request(): Promise<unknown> {
      throw new Error('must not dispatch')
    }
    acceptProject(): void {}
  })()
  return { transport, budget, state }
}

type Selection = { projectId: string; owner: object; session: string; epoch: number }

function impactDocument(projectId: string, targetCheckpointRef: string) {
  return Buffer.from(
    JSON.stringify({
      restoreImpactVersion: 1,
      projectId,
      targetCheckpointRef,
      domainWillRestore: false,
      domainDiff: [],
      metadata: {
        before: { name: '恢复前改名', mode: 'guided' },
        after: { name: '源项目', mode: 'assisted' },
      },
      drafts: [{ editor: 'query-workspace-v1', before: null, after: { draft: true } }],
      learning: [],
      interveningOperations: [
        { sequence: 2, operationId: id(31), operationKind: 'application', changeType: 'rename' },
        {
          sequence: 3,
          operationId: id(32),
          operationKind: 'application',
          changeType: 'draft-save',
        },
      ],
      coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
      preserved: [
        'historical-runs',
        'jobs-and-results',
        'assistance-audit',
        'operation-evidence',
        'checkpoints',
      ],
    }),
    'utf8',
  )
}

function sessionFixture(options: { journalPath: string }) {
  const projectId = id(1)
  const targetCheckpointRef = 'a'.repeat(64)
  const currentCheckpointRef = 'd'.repeat(64)
  const document = impactDocument(projectId, targetCheckpointRef)
  const documentHash = sha256(document)
  const cut = Math.floor(document.length / 2)
  const segments = [document.subarray(0, cut), document.subarray(cut)]
  const manifestSegments = segments.map((bytes, ordinal) => ({
    ordinal,
    byteOffset: ordinal === 0 ? 0 : cut,
    rawByteLength: bytes.length,
    sha256: sha256(bytes),
  }))
  const previewRef = 'e'.repeat(64)
  const confirmationRef = uuid()
  const preview: ProjectRestorePreviewDTO = {
    restorePreviewVersion: 1,
    previewRef,
    projectId,
    documentHash,
    manifest: {
      documentKind: 'restore-impact',
      documentHash,
      totalBytes: document.length,
      segmentCount: segments.length,
      segments: manifestSegments,
    },
    targetCheckpointRef,
    targetOperationSequence: 1,
    targetDomainRevision: 1,
    currentCheckpointRef,
    currentOperationSequence: 3,
    interveningOperationCount: 2,
    domainWillRestore: false,
    expiresAtMs: Date.now() + 60000,
  }
  const confirmation: ProjectRestoreConfirmationDTO = {
    restoreConfirmationVersion: 1,
    projectId,
    previewRef,
    documentHash,
    preparedPlanRef: '3'.repeat(64),
    confirmationRef,
    expiresAtMs: Date.now() + 60000,
  }
  const { transport, budget, state } = transportFixture()
  const calls: Array<{ method: MainlineMethod; params: Record<string, unknown> }> = []
  const selectionRef: { current: Selection | null } = {
    current: { projectId, owner: transport.owner, session: id(2), epoch: 7 },
  }
  const epochRef = { value: 7 }
  const other = { unresolved: false }
  const applyResultFor = (operationId: string): ProjectRestoreResultDTO => ({
    restoreResultVersion: 1,
    projectId,
    operationId,
    requestHash: hashOf({ projectId, operationId, confirmationRef, documentHash }),
    receiptHash: '5'.repeat(64),
    checkpointRef: '6'.repeat(64),
    operationSequence: 4,
    domainRevision: 1,
    metadataVersion: 2,
    restoredFromCheckpointRef: targetCheckpointRef,
    coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
    preserved: [
      'historical-runs',
      'jobs-and-results',
      'assistance-audit',
      'operation-evidence',
      'checkpoints',
    ],
  })
  const router: {
    handlers: Partial<Record<MainlineMethod, (params: Record<string, unknown>) => unknown>>
  } = {
    handlers: {
      'project.checkpoint.list': () => ({
        checkpointListVersion: 1,
        projectId,
        items: [],
        total: 0,
        offset: 0,
        nextCursor: null,
      }),
      'project.restore.preview': () => structuredClone(preview),
      'project.restore.page': (params) => {
        if ((params.cursor as string | null) === null)
          return {
            restorePageVersion: 1,
            projectId,
            previewRef,
            documentHash,
            segments: [
              {
                ordinal: 0,
                byteOffset: 0,
                rawByteLength: segments[0]!.length,
                sha256: manifestSegments[0]!.sha256,
                dataBase64: segments[0]!.toString('base64'),
              },
            ],
            nextCursor: String(cut),
            complete: false,
          }
        return {
          restorePageVersion: 1,
          projectId,
          previewRef,
          documentHash,
          segments: [
            {
              ordinal: 1,
              byteOffset: cut,
              rawByteLength: segments[1]!.length,
              sha256: manifestSegments[1]!.sha256,
              dataBase64: segments[1]!.toString('base64'),
            },
          ],
          nextCursor: null,
          complete: true,
        }
      },
      'project.restore.confirm': () => structuredClone(confirmation),
      'project.restore.apply': (params) => applyResultFor(String(params.operationId)),
      'project.restore.operation.get': () => ({ state: 'applied', result: null }),
    },
  }
  const session = new ProjectRestoreSession({
    client: () => transport,
    selection: () => selectionRef.current,
    epoch: () => epochRef.value,
    call: async <T>(
      _client: MainlineProjectTransport,
      method: MainlineMethod,
      params: Record<string, unknown>,
    ): Promise<T> => {
      calls.push({ method, params })
      const handler = router.handlers[method]
      if (!handler) throw new Error(`unscripted method ${method}`)
      return handler(params) as T
    },
    hasOtherUnresolvedResponsibility: () => other.unresolved,
    journalPath: options.journalPath,
  })
  const readPage = async (cursor: string | null): Promise<ProjectRestorePageDTO> =>
    session.page({ previewRef, cursor })
  return {
    session,
    budget,
    transportState: state,
    calls,
    selectionRef,
    epochRef,
    router,
    fixture: { projectId, preview, confirmation, manifestSegments, applyResultFor },
    readPage,
    async readBothPages(): Promise<void> {
      const first = await readPage(null)
      await readPage(first.nextCursor)
    },
  }
}

describe('restore journal durability and reconciliation (session unit)', () => {
  const directory = { value: '' }
  beforeEach(async () => {
    directory.value = await mkdtemp(join(tmpdir(), 'b1b-unit-'))
  })
  afterEach(async () => {
    await rm(directory.value, { recursive: true, force: true })
  })
  const journalPath = () => join(directory.value, 'restore-intents.json')

  it('writes the durable intent atomically, reloads it after restart and reconciles applied without replay', async () => {
    const h = sessionFixture({ journalPath: journalPath() })
    const operationId = uuid()
    await h.session.preview({
      targetCheckpointRef: h.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: h.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await h.readBothPages()
    await h.session.confirm({
      previewRef: h.fixture.preview.previewRef,
      documentHash: h.fixture.preview.documentHash,
      readSegmentHashes: h.fixture.manifestSegments.map((segment) => segment.sha256),
    })
    const applied = await h.session.apply({
      operationId,
      confirmationRef: h.fixture.confirmation.confirmationRef,
      documentHash: h.fixture.preview.documentHash,
    })
    expect(applied.operationId).toBe(operationId)
    // The journal keeps the durable intent until its reply ACK is consumed.
    const written = JSON.parse(await readFile(journalPath(), 'utf8')) as {
      records: Array<{ operationId: string; outcome: string; delivered: boolean }>
    }
    expect(written.records).toHaveLength(1)
    expect(written.records[0]).toMatchObject({ operationId, outcome: 'applied', delivered: false })
    // Restart with the same journal: the original intent is visible and fenced.
    const restart = sessionFixture({ journalPath: journalPath() })
    expect(restart.session.hasUnresolvedResponsibility).toBe(true)
    const pending: PendingProjectRestoreOperationDTO[] = await restart.session.pending()
    expect(pending).toHaveLength(1)
    expect(pending[0]).toMatchObject({ operationId, projectId: h.fixture.projectId })
    const replay = restart.session.apply({
      operationId,
      confirmationRef: h.fixture.confirmation.confirmationRef,
      documentHash: h.fixture.preview.documentHash,
    })
    expect(await code(replay)).toBe('INVALID_STATE') // reconcile, never replay
    // Lost-ACK reconciliation confirms the original applied result, no new write.
    restart.router.handlers['project.restore.operation.get'] = () => ({
      state: 'applied',
      result: h.fixture.applyResultFor(operationId),
    })
    const record = (await restart.session.operation({ operationId })) as ProjectRestoreOperationDTO
    expect(record.state).toBe('applied')
    expect(restart.calls.filter((call) => call.method === 'project.restore.apply')).toHaveLength(0)
    // Consuming the reply ACK marks delivery and releases the unresolved hold.
    expect(restart.budget.retireClaims).toHaveLength(1)
    restart.budget.retireClaims[0]!()
    const afterAck = JSON.parse(await readFile(journalPath(), 'utf8')) as {
      records: Array<{ operationId: string; delivered: boolean }>
    }
    expect(afterAck.records[0]).toMatchObject({ operationId, delivered: true })
    const settled = sessionFixture({ journalPath: journalPath() })
    expect(settled.session.hasUnresolvedResponsibility).toBe(false)
    expect(await settled.session.pending()).toHaveLength(0)
    settled.session.dispose()
    restart.session.dispose()
    h.session.dispose()
  })

  it('reconciles an unselected restart in both applied and not-found paths, while fencing cross-project probes', async () => {
    // Applied path: the engine committed the restore, the reply ACK was lost,
    // and the crash restart lands with no project selected at all.
    const appliedJournal = join(directory.value, 'unselected-applied.json')
    const first = sessionFixture({ journalPath: appliedJournal })
    const appliedOperation = uuid()
    await first.session.preview({
      targetCheckpointRef: first.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: first.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await first.readBothPages()
    await first.session.confirm({
      previewRef: first.fixture.preview.previewRef,
      documentHash: first.fixture.preview.documentHash,
      readSegmentHashes: first.fixture.manifestSegments.map((segment) => segment.sha256),
    })
    await first.session.apply({
      operationId: appliedOperation,
      confirmationRef: first.fixture.confirmation.confirmationRef,
      documentHash: first.fixture.preview.documentHash,
    })
    first.session.dispose()
    const appliedRestart = sessionFixture({ journalPath: appliedJournal })
    appliedRestart.selectionRef.current = null
    appliedRestart.router.handlers['project.restore.operation.get'] = () => ({
      state: 'applied',
      // The result must match the original fixture's confirmation identity that
      // is durably baked into the journal intent.
      result: first.fixture.applyResultFor(appliedOperation),
    })
    const appliedRecord = (await appliedRestart.session.operation({
      operationId: appliedOperation,
    })) as ProjectRestoreOperationDTO
    expect(appliedRecord.state).toBe('applied')
    appliedRestart.budget.retireClaims.at(-1)!()
    expect(appliedRestart.session.hasUnresolvedResponsibility).toBe(false)
    appliedRestart.session.dispose()

    // Not-found path: the crash lost the delivery before the engine committed;
    // with no selection the reconciliation must still close the pending intent.
    const lostJournal = join(directory.value, 'unselected-lost.json')
    const second = sessionFixture({ journalPath: lostJournal })
    await second.session.preview({
      targetCheckpointRef: second.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: second.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await second.readBothPages()
    await second.session.confirm({
      previewRef: second.fixture.preview.previewRef,
      documentHash: second.fixture.preview.documentHash,
      readSegmentHashes: second.fixture.manifestSegments.map((segment) => segment.sha256),
    })
    second.router.handlers['project.restore.apply'] = () => {
      throw new Error('delivery lost')
    }
    const lostOperation = uuid()
    await expect(
      second.session.apply({
        operationId: lostOperation,
        confirmationRef: second.fixture.confirmation.confirmationRef,
        documentHash: second.fixture.preview.documentHash,
      }),
    ).rejects.toThrow()
    second.session.dispose()
    const lostRestart = sessionFixture({ journalPath: lostJournal })
    lostRestart.selectionRef.current = null
    lostRestart.router.handlers['project.restore.operation.get'] = () => ({
      state: 'not-found',
      result: null,
    })
    const lostRecord = (await lostRestart.session.operation({
      operationId: lostOperation,
    })) as ProjectRestoreOperationDTO
    expect(lostRecord.state).toBe('not-found')
    lostRestart.budget.retireClaims.at(-1)!()
    expect(lostRestart.session.hasUnresolvedResponsibility).toBe(false)
    lostRestart.session.dispose()

    // A selection pointing at another project may not reconcile this intent.
    const fenced = sessionFixture({ journalPath: lostJournal })
    const owner = fenced.selectionRef.current!.owner
    fenced.selectionRef.current = { projectId: id(99), owner, session: id(2), epoch: 7 }
    const denied = fenced.session.operation({ operationId: lostOperation })
    expect(await code(denied)).toBe('PERMISSION_DENIED')
    fenced.session.dispose()
  })

  it('keeps a crashed pending intent fenced from new writes until reconciled not-found', async () => {
    const h = sessionFixture({ journalPath: journalPath() })
    await h.session.preview({
      targetCheckpointRef: h.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: h.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await h.readBothPages()
    await h.session.confirm({
      previewRef: h.fixture.preview.previewRef,
      documentHash: h.fixture.preview.documentHash,
      readSegmentHashes: h.fixture.manifestSegments.map((segment) => segment.sha256),
    })
    // Crash before the engine reply: the durable pending intent survives.
    h.router.handlers['project.restore.apply'] = () => {
      throw new Error('delivery lost')
    }
    await expect(
      h.session.apply({
        operationId: uuid(),
        confirmationRef: h.fixture.confirmation.confirmationRef,
        documentHash: h.fixture.preview.documentHash,
      }),
    ).rejects.toThrow()
    expect(h.session.hasUnresolvedResponsibility).toBe(true)
    h.session.dispose()
    const restart = sessionFixture({ journalPath: journalPath() })
    expect(await restart.session.pending()).toHaveLength(1)
    // While the original is unresolved, no second restore may be issued.
    const blocked = restart.session.apply({
      operationId: uuid(),
      confirmationRef: h.fixture.confirmation.confirmationRef,
      documentHash: h.fixture.preview.documentHash,
    })
    expect(await code(blocked)).toBe('INVALID_STATE')
    // Reconciliation reads not-found: the original is closed without any write.
    restart.router.handlers['project.restore.operation.get'] = () => ({
      state: 'not-found',
      result: null,
    })
    const record = (await restart.session.operation({
      operationId: (await restart.session.pending())[0]!.operationId,
    })) as ProjectRestoreOperationDTO
    expect(record.state).toBe('not-found')
    restart.budget.retireClaims.at(-1)!()
    expect(restart.session.hasUnresolvedResponsibility).toBe(false)
    restart.session.dispose()
  })

  it('refuses confirm when segments were not fully read, even with a forged complete claim', async () => {
    const h = sessionFixture({ journalPath: journalPath() })
    await h.session.preview({
      targetCheckpointRef: h.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: h.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    // Only the first page was actually served; the claim lists every hash.
    await h.readPage(null)
    const forged = h.session.confirm({
      previewRef: h.fixture.preview.previewRef,
      documentHash: h.fixture.preview.documentHash,
      readSegmentHashes: h.fixture.manifestSegments.map((segment) => segment.sha256),
    })
    expect(await code(forged)).toBe('PERMISSION_DENIED')
    // Honest but incomplete claims are refused as well.
    await h.readPage(String(Math.floor(h.fixture.preview.manifest.totalBytes / 2)))
    const incomplete = h.session.confirm({
      previewRef: h.fixture.preview.previewRef,
      documentHash: h.fixture.preview.documentHash,
      readSegmentHashes: [h.fixture.manifestSegments[0]!.sha256],
    })
    expect(await code(incomplete)).toBe('PERMISSION_DENIED')
    expect(h.calls.filter((call) => call.method === 'project.restore.confirm')).toHaveLength(0)
    h.session.dispose()
  })

  it('rejects late replies after selection, epoch or session fencing changes', async () => {
    const h = sessionFixture({ journalPath: journalPath() })
    let resolvePreview: (value: unknown) => void = () => {}
    h.router.handlers['project.restore.preview'] = () =>
      new Promise((resolve) => {
        resolvePreview = resolve
      })
    const late = h.session.preview({
      targetCheckpointRef: h.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: h.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await new Promise((tick) => setTimeout(tick, 0))
    // The project selection moved on while the preview reply was in flight.
    h.selectionRef.current = null
    resolvePreview(structuredClone(h.fixture.preview))
    expect(await code(late)).toBe('INVALID_STATE')
    // A stale epoch rejects a same-selection reply.
    const second = sessionFixture({ journalPath: join(directory.value, 'second.json') })
    let resolveSecond: (value: unknown) => void = () => {}
    second.router.handlers['project.restore.preview'] = () =>
      new Promise((resolve) => {
        resolveSecond = resolve
      })
    const lateEpoch = second.session.preview({
      targetCheckpointRef: second.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: second.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await new Promise((tick) => setTimeout(tick, 0))
    second.epochRef.value = 8
    resolveSecond(structuredClone(second.fixture.preview))
    expect(await code(lateEpoch)).toBe('INVALID_STATE')
    // A replaced engine session (generation) fences the captured scope.
    const third = sessionFixture({ journalPath: join(directory.value, 'third.json') })
    let resolveThird: (value: unknown) => void = () => {}
    third.router.handlers['project.restore.preview'] = () =>
      new Promise((resolve) => {
        resolveThird = resolve
      })
    const lateSession = third.session.preview({
      targetCheckpointRef: third.fixture.preview.targetCheckpointRef,
      expectedCheckpointRef: third.fixture.preview.currentCheckpointRef,
      expectedLifecycleVersion: 3,
    })
    await new Promise((tick) => setTimeout(tick, 0))
    third.transportState.sessionId = id(5)
    resolveThird(structuredClone(third.fixture.preview))
    expect(await code(lateSession)).toBe('INVALID_STATE')
    second.session.dispose()
    third.session.dispose()
    h.session.dispose()
  })

  it('refuses corrupted, relative and symlinked journals while preserving the original file', async () => {
    // Relative path: refused before any file is touched.
    const relative = sessionFixture({ journalPath: 'relative-restore-intents.json' })
    expect(relative.session.hasUnresolvedResponsibility).toBe(true)
    expect(await code(relative.session.list({ pageSize: 10, cursor: null }))).toBe(
      'STORAGE_FAILURE',
    )
    relative.session.dispose()
    // Corrupted journal: original bytes preserved, no new write, no tmp leftovers.
    const corruptedPath = join(directory.value, 'corrupt.json')
    await writeFile(corruptedPath, '{corrupt', 'utf8')
    const corrupted = sessionFixture({ journalPath: corruptedPath })
    expect(await code(corrupted.session.list({ pageSize: 10, cursor: null }))).toBe(
      'STORAGE_FAILURE',
    )
    await corrupted.session.pending().catch(() => {})
    expect(await readFile(corruptedPath, 'utf8')).toBe('{corrupt')
    expect((await readdir(directory.value)).filter((name) => name.includes('corrupt'))).toEqual([
      'corrupt.json',
    ])
    corrupted.session.dispose()
    // Symlinked journal: refused without following or replacing the link.
    const realPath = join(directory.value, 'real.json')
    const linkPath = join(directory.value, 'link.json')
    await writeFile(realPath, '{"journalVersion":1,"records":[]}', 'utf8')
    await symlink(realPath, linkPath)
    const linked = sessionFixture({ journalPath: linkPath })
    expect(await code(linked.session.list({ pageSize: 10, cursor: null }))).toBe('STORAGE_FAILURE')
    expect((await lstat(linkPath)).isSymbolicLink()).toBe(true)
    expect(await readFile(realPath, 'utf8')).toBe('{"journalVersion":1,"records":[]}')
    linked.session.dispose()
  })
})

/* --------------------------------------------------------------------- */
/* Part B: ProjectRestoreController state machine and panel presentation */
/* --------------------------------------------------------------------- */

const management: MainlineManagementItemDTO = {
  projectId: id(1),
  domainRevision: 1,
  operationSequence: 3,
  metadataVersion: 2,
  checkpointRef: 'd'.repeat(64),
  lifecycle: { state: 'active', version: 4 },
  metadata: {
    name: '源项目',
    templateRef: null,
    archived: false,
    mode: 'guided',
    origin: 'created',
  },
}

function controllerBridge(options: {
  pending?: PendingProjectRestoreOperationDTO[]
  managementError?: BridgeResult<MainlineManagementItemDTO>
}) {
  const calls: Array<{ method: string; args: unknown }> = []
  // The scripted checkpoint store: created checkpoints really join the list,
  // so a refresh can be observed by its effect and not only by its call count.
  const created: Array<{ checkpointRef: string; label: string | null }> = []
  const impact = impactDocument(id(1), 'a'.repeat(64))
  const documentHash = sha256(impact)
  const cut = Math.floor(impact.length / 2)
  const segmentHashes = [sha256(impact.subarray(0, cut)), sha256(impact.subarray(cut))]
  const preview: ProjectRestorePreviewDTO = {
    restorePreviewVersion: 1,
    previewRef: 'e'.repeat(64),
    projectId: id(1),
    documentHash,
    manifest: {
      documentKind: 'restore-impact',
      documentHash,
      totalBytes: impact.length,
      segmentCount: 2,
      segments: [
        { ordinal: 0, byteOffset: 0, rawByteLength: cut, sha256: segmentHashes[0]! },
        {
          ordinal: 1,
          byteOffset: cut,
          rawByteLength: impact.length - cut,
          sha256: segmentHashes[1]!,
        },
      ],
    },
    targetCheckpointRef: 'a'.repeat(64),
    targetOperationSequence: 1,
    targetDomainRevision: 1,
    currentCheckpointRef: 'd'.repeat(64),
    currentOperationSequence: 3,
    interveningOperationCount: 2,
    domainWillRestore: false,
    expiresAtMs: Date.now() + 60000,
  }
  const confirmation: ProjectRestoreConfirmationDTO = {
    restoreConfirmationVersion: 1,
    projectId: id(1),
    previewRef: preview.previewRef,
    documentHash,
    preparedPlanRef: '3'.repeat(64),
    confirmationRef: uuid(),
    expiresAtMs: Date.now() + 60000,
  }
  const bridge: ProjectCheckpointBridge &
    Pick<ProjectManagementBridge, 'getProjectManagementState'> = {
    getProjectManagementState: async () => {
      calls.push({ method: 'management-state', args: null })
      return options.managementError ?? { ok: true, data: management }
    },
    listProjectCheckpoints: async (args) => {
      calls.push({ method: 'list', args })
      const items: ProjectCheckpointItemDTO[] = [
        {
          checkpointRef: 'a'.repeat(64),
          operationSequence: 1,
          domainRevision: 1,
          domainSnapshotRef: 'b'.repeat(64),
          metadataVersion: 1,
          reason: 'manual',
          label: '导入映射之前',
          operationId: null,
          operationKind: null,
          counts: { definitions: 1, facts: 0, drafts: 0, learning: 0 },
          coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
          preserved: [
            'historical-runs',
            'jobs-and-results',
            'assistance-audit',
            'operation-evidence',
            'checkpoints',
          ],
          isCurrent: false,
        },
        ...created.map((item, index): ProjectCheckpointItemDTO => ({
          checkpointRef: item.checkpointRef,
          operationSequence: 4 + index,
          domainRevision: 1,
          domainSnapshotRef: 'b'.repeat(64),
          metadataVersion: 2,
          reason: 'manual',
          label: item.label,
          operationId: null,
          operationKind: null,
          counts: { definitions: 1, facts: 0, drafts: 0, learning: 0 },
          coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
          preserved: [
            'historical-runs',
            'jobs-and-results',
            'assistance-audit',
            'operation-evidence',
            'checkpoints',
          ],
          isCurrent: false,
        })),
      ]
      return {
        ok: true,
        data: {
          checkpointListVersion: 1,
          projectId: id(1),
          items,
          total: items.length,
          offset: 0,
          nextCursor: null,
        },
      }
    },
    createProjectCheckpoint: async (args) => {
      calls.push({ method: 'create', args })
      const checkpointRef = sha256(`created-checkpoint-${created.length}`)
      created.push({ checkpointRef, label: args.label })
      return {
        ok: true,
        data: {
          checkpointCreateVersion: 1,
          projectId: id(1),
          operationId: args.operationId,
          operationSequence: 4,
          checkpointRef,
          reason: 'manual',
          label: args.label,
          domainRevision: 1,
          metadataVersion: 2,
        },
      }
    },
    getPendingProjectRestoreOperations: async () => {
      calls.push({ method: 'pending', args: null })
      return { ok: true, data: options.pending ?? [] }
    },
    previewProjectRestore: async (args) => {
      calls.push({ method: 'preview', args })
      return { ok: true, data: structuredClone(preview) }
    },
    getProjectRestorePage: async (args) => {
      calls.push({ method: 'page', args })
      if (args.cursor === null)
        return {
          ok: true,
          data: {
            restorePageVersion: 1,
            projectId: id(1),
            previewRef: preview.previewRef,
            documentHash,
            segments: [
              {
                ordinal: 0,
                byteOffset: 0,
                rawByteLength: cut,
                sha256: segmentHashes[0]!,
                dataBase64: impact.subarray(0, cut).toString('base64'),
              },
            ],
            nextCursor: String(cut),
            complete: false,
          },
        }
      return {
        ok: true,
        data: {
          restorePageVersion: 1,
          projectId: id(1),
          previewRef: preview.previewRef,
          documentHash,
          segments: [
            {
              ordinal: 1,
              byteOffset: cut,
              rawByteLength: impact.length - cut,
              sha256: segmentHashes[1]!,
              dataBase64: impact.subarray(cut).toString('base64'),
            },
          ],
          nextCursor: null,
          complete: true,
        },
      }
    },
    confirmProjectRestore: async (args) => {
      calls.push({ method: 'confirm', args })
      return { ok: true, data: structuredClone(confirmation) }
    },
    restoreProject: async (args) => {
      calls.push({ method: 'apply', args })
      return {
        ok: true,
        data: {
          restoreResultVersion: 1,
          projectId: id(1),
          operationId: args.operationId,
          requestHash: '4'.repeat(64),
          receiptHash: '5'.repeat(64),
          checkpointRef: '6'.repeat(64),
          operationSequence: 4,
          domainRevision: 1,
          metadataVersion: 2,
          restoredFromCheckpointRef: preview.targetCheckpointRef,
          coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
          preserved: [
            'historical-runs',
            'jobs-and-results',
            'assistance-audit',
            'operation-evidence',
            'checkpoints',
          ],
        },
      }
    },
    getProjectRestoreOperation: async (args) => {
      calls.push({ method: 'operation', args })
      return { ok: true, data: { state: 'not-found', result: null } }
    },
  }
  return { bridge, calls, preview, confirmation, segmentHashes }
}

// The panel is TSX; the unit tsconfig has no JSX setting, so it loads at
// runtime through a non-literal specifier like the t04 panel tests.
const panelModule = '../../apps/desktop/src/renderer/src/project/ProjectCheckpointRestorePanel'
const {
  ProjectCheckpointRestorePanel,
}: {
  ProjectCheckpointRestorePanel: ComponentType<{
    controller: ProjectRestoreController
    disabled: boolean
    destructiveBlocked: boolean
  }>
} = await import(panelModule)

describe('restore controller state machine', () => {
  it('initialize loads pending operations without any checkpoint list request before a project is selected', async () => {
    const { bridge, calls } = controllerBridge({})
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      expect(controller.getSnapshot().recoveryLoaded).toBe(true)
      expect(calls.filter((call) => call.method === 'list')).toHaveLength(0)
      // Selecting a project and syncing refreshes the list exactly once.
      controller.select(id(1))
      await controller.refreshWhenIdle()
      expect(calls.filter((call) => call.method === 'list')).toHaveLength(1)
      expect(controller.getSnapshot().list?.items[0]).toMatchObject({ label: '导入映射之前' })
      // Dropping the selection clears the list and issues no new request.
      controller.select(undefined)
      await controller.refresh()
      expect(calls.filter((call) => call.method === 'list')).toHaveLength(1)
      expect(controller.getSnapshot().list).toBeUndefined()
    } finally {
      controller.close()
    }
  })

  it('refreshes the checkpoint list by itself after a manual checkpoint is created', async () => {
    const { bridge, calls } = controllerBridge({})
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      controller.select(id(1))
      await controller.refresh()
      expect(calls.filter((call) => call.method === 'list')).toHaveLength(1)
      expect(controller.getSnapshot().list?.items.map((item) => item.label)).toEqual([
        '导入映射之前',
      ])
      // Creating a checkpoint owns the busy flag, so the public refresh() would
      // be skipped. The list must still be refreshed without any manual call.
      await controller.createCheckpoint('CP1')
      expect(calls.filter((call) => call.method === 'create')).toHaveLength(1)
      expect(calls.filter((call) => call.method === 'list')).toHaveLength(2)
      expect(controller.getSnapshot().list?.items.map((item) => item.label)).toEqual([
        '导入映射之前',
        'CP1',
      ])
      expect(controller.getSnapshot().notice).toContain('已创建手动检查点')
      expect(controller.getSnapshot().busy).toBe(false)
    } finally {
      controller.close()
    }
  })

  it('previews against the injected management state, requires full segment reads and applies once', async () => {
    const { bridge, calls, preview, segmentHashes, confirmation } = controllerBridge({})
    const applied: string[] = []
    const controller = new ProjectRestoreController(bridge, (result) =>
      applied.push(result.projectId),
    )
    try {
      await controller.initialize()
      controller.select(id(1))
      await controller.previewRestore(preview.targetCheckpointRef)
      let snapshot = controller.getSnapshot()
      // The management CAS frame is read through the injected bridge, not window.
      expect(calls.find((call) => call.method === 'management-state')).toBeDefined()
      expect(calls.find((call) => call.method === 'preview')?.args).toEqual({
        targetCheckpointRef: preview.targetCheckpointRef,
        expectedCheckpointRef: management.checkpointRef,
        expectedLifecycleVersion: management.lifecycle.version,
      })
      expect(snapshot.readSegmentHashes).toEqual(segmentHashes)
      expect(snapshot.document).toMatchObject({ restoreImpactVersion: 1 })
      expect(snapshot.document?.interveningOperations).toHaveLength(2)
      expect(calls.find((call) => call.method === 'confirm')).toBeUndefined()
      await controller.confirmRestore()
      snapshot = controller.getSnapshot()
      expect(snapshot.confirmation?.confirmationRef).toBe(confirmation.confirmationRef)
      await controller.applyRestore()
      snapshot = controller.getSnapshot()
      expect(snapshot.confirmation).toBeUndefined()
      expect(snapshot.notice).toContain('整项目恢复已完成')
      expect(applied).toEqual([id(1)])
      expect(calls.filter((call) => call.method === 'apply')).toHaveLength(1)
    } finally {
      controller.close()
    }
  })

  it('maps CAS drift and recovery reconciliation through explicit notices', async () => {
    const conflict: BridgeResult<MainlineManagementItemDTO> = {
      ok: false,
      error: {
        code: 'REVISION_CONFLICT',
        messageKey: 'project.revisionConflict',
        params: {},
        retryable: false,
      },
    }
    const { bridge: driftBridge } = controllerBridge({ managementError: conflict })
    const drift = new ProjectRestoreController(driftBridge)
    try {
      await drift.initialize()
      drift.select(id(1))
      await drift.previewRestore('a'.repeat(64))
      const snapshot = drift.getSnapshot()
      expect(snapshot.preview).toBeUndefined()
      expect(snapshot.notice).toContain('重新预览')
      expect(snapshot.error?.code).toBe('REVISION_CONFLICT')
    } finally {
      drift.close()
    }
    const pendingOperation: PendingProjectRestoreOperationDTO = {
      operationId: uuid(),
      projectId: id(1),
      targetCheckpointRef: 'a'.repeat(64),
      documentHash: 'f'.repeat(64),
    }
    const { bridge: recoverBridge, calls: recoverCalls } = controllerBridge({
      pending: [pendingOperation],
    })
    const recover = new ProjectRestoreController(recoverBridge)
    try {
      await recover.initialize()
      expect(recover.unresolved).toBe(true)
      expect(recover.getSnapshot().recovery).toHaveLength(1)
      await recover.reconcile()
      // not-found closes the blocked original without any restore write.
      expect(recover.getSnapshot().recovery).toHaveLength(0)
      expect(recover.getSnapshot().notice).toContain('已核实原恢复操作未提交')
      expect(recoverCalls.filter((call) => call.method === 'operation')).toHaveLength(1)
      expect(recoverCalls.find((call) => call.method === 'apply')).toBeUndefined()
      expect(recover.unresolved).toBe(false)
    } finally {
      recover.close()
    }
  })

  it('reconcile clears the recovery entry before the applied callback when the original operation was applied', async () => {
    const pendingOperation: PendingProjectRestoreOperationDTO = {
      operationId: uuid(),
      projectId: id(1),
      targetCheckpointRef: 'a'.repeat(64),
      documentHash: 'f'.repeat(64),
    }
    const { bridge, calls } = controllerBridge({ pending: [pendingOperation] })
    const appliedResults: string[] = []
    let unresolvedInApplied: boolean | undefined
    const controller = new ProjectRestoreController(bridge, (result) => {
      unresolvedInApplied = controller.unresolved
      appliedResults.push(result.operationId)
    })
    try {
      await controller.initialize()
      expect(controller.getSnapshot().recovery).toHaveLength(1)
      bridge.getProjectRestoreOperation = async (args) => {
        calls.push({ method: 'operation', args })
        return {
          ok: true,
          data: {
            state: 'applied',
            result: {
              restoreResultVersion: 1,
              projectId: id(1),
              operationId: args.operationId,
              requestHash: '4'.repeat(64),
              receiptHash: '5'.repeat(64),
              checkpointRef: '6'.repeat(64),
              operationSequence: 4,
              domainRevision: 1,
              metadataVersion: 2,
              restoredFromCheckpointRef: 'a'.repeat(64),
              coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
              preserved: [
                'historical-runs',
                'jobs-and-results',
                'assistance-audit',
                'operation-evidence',
                'checkpoints',
              ],
            },
          },
        }
      }
      await controller.reconcile()
      // The recovery entry is removed in the same state write that accepts the
      // result, so the applied callback already observes a settled controller.
      expect(unresolvedInApplied).toBe(false)
      expect(appliedResults).toEqual([pendingOperation.operationId])
      expect(controller.getSnapshot().recovery).toHaveLength(0)
      expect(controller.getSnapshot().notice).toContain('整项目恢复已完成')
      expect(controller.unresolved).toBe(false)
    } finally {
      controller.close()
    }
  })

  it('re-syncs pending intents after a failed apply and never re-submits on reconcile', async () => {
    // !result.ok variant: the main process durably persisted the intent and
    // set restoreBlocked even though the bridge reply was an error.
    const { bridge, calls, preview } = controllerBridge({})
    const journalled: PendingProjectRestoreOperationDTO[] = []
    bridge.getPendingProjectRestoreOperations = async () => {
      calls.push({ method: 'pending', args: null })
      return { ok: true as const, data: [...journalled] }
    }
    const conflict = {
      ok: false as const,
      error: {
        code: 'REVISION_CONFLICT',
        messageKey: 'project.revisionConflict',
        params: {},
        retryable: false,
      },
    }
    bridge.restoreProject = async (args) => {
      calls.push({ method: 'apply', args })
      journalled.push({
        operationId: args.operationId,
        projectId: id(1),
        targetCheckpointRef: preview.targetCheckpointRef,
        documentHash: preview.documentHash,
      })
      return conflict
    }
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      controller.select(id(1))
      await controller.previewRestore(preview.targetCheckpointRef)
      await controller.confirmRestore()
      expect(controller.getSnapshot().confirmation).toBeDefined()
      await controller.applyRestore()
      const snapshot = controller.getSnapshot()
      expect(snapshot.recovery).toHaveLength(1)
      expect(snapshot.recovery[0]).toMatchObject({ projectId: id(1) })
      expect(snapshot.preview).toBeUndefined()
      expect(snapshot.confirmation).toBeUndefined()
      expect(snapshot.error?.code).toBe('REVISION_CONFLICT')
      expect(snapshot.notice).toContain('请先核对原恢复操作，再重新预览')
      // The panel surfaces the reconcile control for the synced pending intent.
      const markup = renderToStaticMarkup(
        createElement(ProjectCheckpointRestorePanel, {
          controller,
          disabled: false,
          destructiveBlocked: false,
        }),
      )
      expect(markup).toContain('data-testid="restore-reconcile"')
      // Reconciling the unresolved original never re-submits the apply.
      await controller.reconcile()
      expect(calls.filter((call) => call.method === 'apply')).toHaveLength(1)
      expect(calls.filter((call) => call.method === 'operation')).toHaveLength(1)
      expect(controller.getSnapshot().recovery).toHaveLength(0)
      expect(controller.unresolved).toBe(false)
    } finally {
      controller.close()
    }

    // Reject variant: the transport itself threw after the write was issued.
    const { bridge: lostBridge, calls: lostCalls, preview: lostPreview } = controllerBridge({})
    const lostJournal: PendingProjectRestoreOperationDTO[] = []
    lostBridge.getPendingProjectRestoreOperations = async () => {
      lostCalls.push({ method: 'pending', args: null })
      return { ok: true as const, data: [...lostJournal] }
    }
    lostBridge.restoreProject = async (args) => {
      lostCalls.push({ method: 'apply', args })
      lostJournal.push({
        operationId: args.operationId,
        projectId: id(1),
        targetCheckpointRef: lostPreview.targetCheckpointRef,
        documentHash: lostPreview.documentHash,
      })
      throw new Error('transport lost')
    }
    const lost = new ProjectRestoreController(lostBridge)
    try {
      await lost.initialize()
      lost.select(id(1))
      await lost.previewRestore(lostPreview.targetCheckpointRef)
      await lost.confirmRestore()
      await lost.applyRestore()
      const snapshot = lost.getSnapshot()
      expect(snapshot.recovery).toHaveLength(1)
      expect(snapshot.preview).toBeUndefined()
      expect(snapshot.confirmation).toBeUndefined()
      expect(snapshot.notice).toContain('结果未知；请核对原操作，勿重复提交')
      await lost.reconcile()
      expect(lostCalls.filter((call) => call.method === 'apply')).toHaveLength(1)
      expect(lost.getSnapshot().recovery).toHaveLength(0)
    } finally {
      lost.close()
    }
  })

  it('clears the previous project error and notice on switch while keeping recovery notices', async () => {
    const conflict: BridgeResult<MainlineManagementItemDTO> = {
      ok: false,
      error: {
        code: 'REVISION_CONFLICT',
        messageKey: 'project.revisionConflict',
        params: {},
        retryable: false,
      },
    }
    const { bridge } = controllerBridge({ managementError: conflict })
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      controller.select(id(1))
      await controller.previewRestore('a'.repeat(64))
      expect(controller.getSnapshot().error?.code).toBe('REVISION_CONFLICT')
      expect(controller.getSnapshot().notice).toContain('重新预览')
      // Switching to another project with no unresolved recovery clears both.
      controller.select(id(2))
      expect(controller.getSnapshot().error).toBeUndefined()
      expect(controller.getSnapshot().notice).toBe('')
    } finally {
      controller.close()
    }
    // While a recovery is unresolved, its notice survives a project switch
    // (only the error is always cleared).
    const pendingOperation: PendingProjectRestoreOperationDTO = {
      operationId: uuid(),
      projectId: id(1),
      targetCheckpointRef: 'a'.repeat(64),
      documentHash: 'f'.repeat(64),
    }
    const { bridge: blockedBridge, calls: blockedCalls } = controllerBridge({
      pending: [pendingOperation],
    })
    blockedBridge.getProjectRestoreOperation = async (args) => {
      blockedCalls.push({ method: 'operation', args })
      return conflict
    }
    const blocked = new ProjectRestoreController(blockedBridge)
    try {
      await blocked.initialize()
      blocked.select(id(1))
      await blocked.reconcile()
      expect(blocked.getSnapshot().recovery).toHaveLength(1)
      expect(blocked.getSnapshot().notice).toContain('操作结果尚未确认')
      blocked.select(id(2))
      expect(blocked.getSnapshot().error).toBeUndefined()
      expect(blocked.getSnapshot().notice).toContain('操作结果尚未确认')
    } finally {
      blocked.close()
    }
    // The very first open from an unselected startup must not clear a recovery
    // result notice either.
    const { bridge: settledBridge } = controllerBridge({ pending: [pendingOperation] })
    const settled = new ProjectRestoreController(settledBridge)
    try {
      await settled.initialize()
      await settled.reconcile()
      expect(settled.getSnapshot().notice).toContain('已核实原恢复操作未提交')
      settled.select(id(1))
      expect(settled.getSnapshot().notice).toContain('已核实原恢复操作未提交')
    } finally {
      settled.close()
    }
  })
})

describe('checkpoint restore panel presentation gates', () => {
  const render = (controller: ProjectRestoreController, destructiveBlocked: boolean) =>
    renderToStaticMarkup(
      createElement(ProjectCheckpointRestorePanel, {
        controller,
        disabled: false,
        destructiveBlocked,
      }),
    )
  /** Whether the element carrying a testid renders with a disabled attribute. */
  const controlDisabled = (markup: string, testid: string): boolean => {
    const at = markup.indexOf(`data-testid="${testid}"`)
    if (at < 0) throw new Error(`missing control ${testid}`)
    return markup.slice(at, markup.indexOf('>', at)).includes('disabled')
  }

  it('explains and disables create/restore before a project is opened', async () => {
    const { bridge } = controllerBridge({})
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      const markup = render(controller, false)
      expect(markup).toContain('尚未打开项目')
      expect(controlDisabled(markup, 'checkpoint-create')).toBe(true)
      expect(controlDisabled(markup, 'checkpoint-list-refresh')).toBe(true)
      expect(markup).not.toContain('data-testid="checkpoint-list"')
    } finally {
      controller.close()
    }
  })

  it('keeps reconcile available while recovery blocks every restore control', async () => {
    const pendingOperation: PendingProjectRestoreOperationDTO = {
      operationId: uuid(),
      projectId: id(1),
      targetCheckpointRef: 'a'.repeat(64),
      documentHash: 'f'.repeat(64),
    }
    const { bridge } = controllerBridge({ pending: [pendingOperation] })
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      controller.select(id(1))
      await controller.refreshWhenIdle()
      const markup = render(controller, false)
      expect(markup).toContain('存在结果未确认的恢复操作')
      expect(controlDisabled(markup, 'restore-reconcile')).toBe(false)
      expect(controlDisabled(markup, 'checkpoint-create')).toBe(true)
      expect(controlDisabled(markup, 'checkpoint-restore-preview')).toBe(true)
    } finally {
      controller.close()
    }
  })

  it('requires typed consent and a settled workspace before executing the restore', async () => {
    const { bridge, preview } = controllerBridge({})
    const controller = new ProjectRestoreController(bridge)
    try {
      await controller.initialize()
      controller.select(id(1))
      await controller.previewRestore(preview.targetCheckpointRef)
      // With a settled workspace the confirm control is reachable once every
      // segment has actually been read.
      const settled = render(controller, false)
      expect(settled).not.toContain('restore-destructive-blocked')
      expect(controlDisabled(settled, 'restore-confirm')).toBe(false)
      // Unsaved edits or unresolved operations block the destructive path with a reason.
      const destructive = render(controller, true)
      expect(destructive).toContain('restore-destructive-blocked')
      expect(controlDisabled(destructive, 'restore-confirm')).toBe(true)
      // After confirmation, execution additionally requires typing “恢复”.
      await controller.confirmRestore()
      const consent = render(controller, false)
      expect(consent).toContain('restore-consent')
      expect(controlDisabled(consent, 'restore-apply')).toBe(true)
    } finally {
      controller.close()
    }
  })
})

/* ------------------------------------------------------------------ */
/* Part D: business3 envelope matcher parity for project.restore.operation.get */
/* ------------------------------------------------------------------ */

describe('business3 envelope matcher binds project.restore.operation.get (B1B-007)', () => {
  const registryHash = createHash('sha256')
    .update(readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)))
    .digest('hex')
  const projectId = id(3)
  const otherProjectId = id(4)
  const operationId = uuid()
  const requestHash = 'c'.repeat(64)
  /** A schema-valid project.restore.apply receipt; the operation.get envelope
   * carries it under `result` with no top-level projectId of its own. */
  const appliedResult = {
    restoreResultVersion: 1,
    projectId,
    operationId,
    requestHash,
    receiptHash: 'd'.repeat(64),
    checkpointRef: 'e'.repeat(64),
    operationSequence: 2,
    domainRevision: 7,
    metadataVersion: 4,
    restoredFromCheckpointRef: 'f'.repeat(64),
    coverage: ['metadata', 'drafts', 'learningCurrent', 'assistanceAudit'],
    preserved: [
      'historical-runs',
      'jobs-and-results',
      'assistance-audit',
      'operation-evidence',
      'checkpoints',
    ],
  }
  const request = {
    kind: 'request',
    protocolVersion: 3,
    id: id(5),
    engineSessionId: id(6),
    method: 'project.restore.operation.get',
    params: { projectId, operationId, requestHash },
  }
  const response = (result: unknown) => ({
    kind: 'response',
    protocolVersion: 3,
    id: request.id,
    engineSessionId: request.engineSessionId,
    method: 'project.restore.operation.get',
    ok: true,
    result,
  })

  it('binds a not-found reply with a null result', () => {
    expect(
      matchesBusiness3Response(
        request,
        response({ state: 'not-found', result: null }),
        registryHash,
      ),
    ).toBe(true)
  })
  it('rejects a not-found reply that still carries an applied receipt', () => {
    expect(
      matchesBusiness3Response(
        request,
        response({ state: 'not-found', result: appliedResult }),
        registryHash,
      ),
    ).toBe(false)
  })
  it('binds an applied receipt whose projectId and request evidence match', () => {
    expect(
      matchesBusiness3Response(
        request,
        response({ state: 'applied', result: appliedResult }),
        registryHash,
      ),
    ).toBe(true)
  })
  it('rejects an applied receipt answered for a different project', () => {
    const foreign = { ...appliedResult, projectId: otherProjectId }
    expect(
      matchesBusiness3Response(
        request,
        response({ state: 'applied', result: foreign }),
        registryHash,
      ),
    ).toBe(false)
  })
})
