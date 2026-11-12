import { describe, expect, it, vi } from 'vitest'
import type {
  BridgeResult,
  MainlineManagementAction,
  MainlineManagementItemDTO,
  MainlineManagementPreviewDTO,
  MainlineManagementResultDTO,
  ProjectManagementBridge,
} from '@ontolearn/contracts'
import { ProjectManagementController } from '../../apps/desktop/src/renderer/src/project/management-controller'

const source = '00000000-0000-4000-8000-000000000001'
const target = '00000000-0000-4000-8000-000000000002'
const operationId = '00000000-0000-4000-8000-000000000003'
const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
const item: MainlineManagementItemDTO = {
  projectId: source,
  domainRevision: 7,
  operationSequence: 9,
  metadataVersion: 2,
  checkpointRef: 'a'.repeat(64),
  lifecycle: { state: 'active', version: 4 },
  metadata: {
    name: '原项目',
    templateRef: null,
    archived: false,
    mode: 'guided',
    origin: 'created',
  },
}
function preview(action: MainlineManagementAction): MainlineManagementPreviewDTO {
  return {
    managementPreviewVersion: 1,
    previewRef: '00000000-0000-4000-8000-000000000004',
    projectId: source,
    action,
    documentHash: 'b'.repeat(64),
    expiresAtMs: Date.now() + 60000,
    document: {
      projectName: '原项目',
      checkpointRef: item.checkpointRef,
      domainRevision: 7,
      operationSequence: 9,
      metadataVersion: 2,
      lifecycleVersion: 4,
      beforeMetadata: item.metadata,
      afterMetadata: { ...item.metadata, name: '副本' },
      counts: {
        definitions: 2,
        facts: 5,
        tombstones: 1,
        drafts: 0,
        learning: 0,
        historyRuns: 3,
        activeJobs: 0,
      },
      coverage: ['当前定义、事实与控制版本'],
      exclusions: ['历史运行保留在源项目'],
      seedHash: 'c'.repeat(64),
    },
  }
}
function receipt(
  kind: MainlineManagementAction['kind'] = 'copy-current',
): MainlineManagementResultDTO {
  return {
    managementResultVersion: 1,
    kind,
    projectId: source,
    operationId,
    targetProjectId: kind === 'copy-current' ? target : source,
    requestHash: 'd'.repeat(64),
    receiptHash: 'e'.repeat(64),
    checkpointRef: 'f'.repeat(64),
    domainRevision: 1,
    metadataVersion: 1,
    operationSequence: 1,
    lifecycleVersion: 0,
    lifecycleState: kind === 'trash' ? 'trashed' : 'active',
  }
}
function fixture() {
  let lastPreview = preview({ kind: 'copy-current', name: '副本' })
  const bridge = {
    getPendingProjectManagementOperations: vi.fn(async () => ok([])),
    getProjectManagementCatalog: vi.fn(async () =>
      ok({
        catalogVersion: 1 as const,
        snapshotId: 'catalog',
        items: [item],
        total: 1,
        offset: 0,
        nextCursor: null,
      }),
    ),
    getProjectManagementState: vi.fn(async () => ok(item)),
    previewProjectManagement: vi.fn(
      async (args: Parameters<ProjectManagementBridge['previewProjectManagement']>[0]) => {
        lastPreview = preview(args.action)
        return ok(lastPreview)
      },
    ),
    confirmProjectManagement: vi.fn(async () =>
      ok({
        confirmationRef: 'confirmation',
        previewRef: lastPreview.previewRef,
        documentHash: lastPreview.documentHash,
        projectId: source,
        kind: lastPreview.action.kind,
      }),
    ),
    applyProjectManagement: vi.fn(async () => ok(receipt())),
    getProjectManagementOperation: vi.fn(async () =>
      ok({ state: 'applied' as const, result: receipt() }),
    ),
  } satisfies ProjectManagementBridge
  const applied = vi.fn()
  const controller = new ProjectManagementController(bridge, applied, () => operationId)
  const ready = async () => {
    await controller.initialize()
    controller.select(source)
  }
  return { bridge, applied, controller, ready }
}

describe('B1a project management presentation responsibility', () => {
  it('uses freshly read checkpoint/lifecycle and exposes no write before explicit apply', async () => {
    const { bridge, controller, ready } = fixture()
    await ready()
    await controller.preview({ kind: 'copy-current', name: '副本' })
    expect(bridge.previewProjectManagement).toHaveBeenCalledWith({
      action: { kind: 'copy-current', name: '副本' },
      expectedCheckpointRef: item.checkpointRef,
      expectedLifecycleVersion: 4,
    })
    expect(controller.getSnapshot().preview?.document.counts.historyRuns).toBe(3)
    controller.cancelPreview()
    await controller.apply()
    expect(bridge.confirmProjectManagement).not.toHaveBeenCalled()
    expect(bridge.applyProjectManagement).not.toHaveBeenCalled()
  })
  it('retains a lost acknowledgement and queries exactly its operation without replay', async () => {
    const { bridge, controller, applied, ready } = fixture()
    await ready()
    bridge.applyProjectManagement.mockRejectedValueOnce(new Error('lost UI ack'))
    await controller.preview({ kind: 'copy-current', name: '副本' })
    await controller.apply()
    expect(controller.getSnapshot().pending?.operationId).toBe(operationId)
    expect(controller.getSnapshot().notice).toContain('勿重复提交')
    await controller.apply()
    expect(bridge.applyProjectManagement).toHaveBeenCalledTimes(1)
    await controller.reconcile()
    expect(bridge.getProjectManagementOperation).toHaveBeenCalledWith({ operationId })
    expect(bridge.applyProjectManagement).toHaveBeenCalledTimes(1)
    expect(applied).toHaveBeenCalledWith(receipt())
    expect(controller.getSnapshot().selectedProjectId).toBe(source)
    expect(controller.getSnapshot().receipt?.targetProjectId).toBe(target)
  })
  it('does not adopt a receipt naming another target for a non-copy action', async () => {
    const { bridge, controller, applied, ready } = fixture()
    await ready()
    bridge.applyProjectManagement.mockResolvedValueOnce(
      ok({ ...receipt('trash'), targetProjectId: target }),
    )
    await controller.preview({ kind: 'trash' })
    await controller.apply()
    expect(applied).not.toHaveBeenCalled()
    expect(controller.getSnapshot().pending?.operationId).toBe(operationId)
  })
  it('drops a late preview when selection has changed', async () => {
    const { bridge, controller, ready } = fixture()
    await ready()
    let deliver!: (value: BridgeResult<MainlineManagementPreviewDTO>) => void
    bridge.previewProjectManagement.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          deliver = resolve
        }),
    )
    const request = controller.preview({ kind: 'trash' })
    await Promise.resolve()
    controller.select(target)
    deliver(ok(preview({ kind: 'trash' })))
    await request
    expect(controller.getSnapshot().preview).toBeUndefined()
    expect(bridge.applyProjectManagement).not.toHaveBeenCalled()
  })
  it('rejects expired confirmation and an action-substituted preview', async () => {
    const { bridge, controller, ready } = fixture()
    await ready()
    bridge.previewProjectManagement.mockResolvedValueOnce(ok(preview({ kind: 'trash' })))
    await controller.preview({ kind: 'copy-current', name: '副本' })
    expect(controller.getSnapshot().preview).toBeUndefined()
    bridge.previewProjectManagement.mockResolvedValueOnce(
      ok({ ...preview({ kind: 'trash' }), expiresAtMs: Date.now() - 1 }),
    )
    await controller.preview({ kind: 'trash' })
    await controller.apply()
    expect(bridge.confirmProjectManagement).not.toHaveBeenCalled()
  })
  it('keeps restart recovery operations and only reads the original operation', async () => {
    const f = fixture()
    const original = {
      operationId,
      projectId: source,
      kind: 'copy-current' as const,
      label: '原副本操作',
    }
    const bridge: ProjectManagementBridge = {
      ...f.bridge,
      getPendingProjectManagementOperations: vi.fn(async () => ok([original])),
    }
    const controller = new ProjectManagementController(bridge, f.applied)
    await controller.initialize()
    expect(controller.unresolved).toBe(true)
    expect(controller.getSnapshot().recovery).toEqual([original])
    await controller.reconcile(operationId)
    expect(bridge.getProjectManagementOperation).toHaveBeenCalledWith({ operationId })
    expect(bridge.applyProjectManagement).not.toHaveBeenCalled()
    expect(bridge.confirmProjectManagement).not.toHaveBeenCalled()
    expect(controller.getSnapshot().recovery).toEqual([])
    expect(controller.getSnapshot().selectedProjectId).toBeUndefined()
  })
  it('keeps recovery records on query failure; only an explicit not-found clears one', async () => {
    const f = fixture()
    let found = false
    const bridge: ProjectManagementBridge = {
      ...f.bridge,
      getPendingProjectManagementOperations: async () =>
        ok([
          { operationId, projectId: source, kind: 'trash', label: '删除' },
          { operationId: 'other', projectId: target, kind: 'archive', label: '归档' },
        ]),
      getProjectManagementOperation: async () =>
        found
          ? ok({ state: 'not-found', result: null })
          : {
              ok: false,
              error: {
                code: 'ENGINE_EXITED',
                messageKey: 'engine.exited',
                params: {},
                retryable: true,
              },
            },
    }
    const controller = new ProjectManagementController(bridge)
    await controller.initialize()
    await controller.reconcile(operationId)
    expect(controller.getSnapshot().recovery).toHaveLength(2)
    expect(controller.getSnapshot().notice).toContain('关闭并重新打开')
    found = true
    await controller.reconcile(operationId)
    expect(controller.getSnapshot().recovery.map((item) => item.operationId)).toEqual(['other'])
  })
  for (const path of ['apply', 'reconcile'] as const) {
    it(`keeps ${path} busy through the entire catalog and selected-state read tail`, async () => {
      const { bridge, controller, ready } = fixture()
      await ready()
      await controller.preview({ kind: 'copy-current', name: '副本' })
      if (path === 'reconcile') {
        bridge.applyProjectManagement.mockRejectedValueOnce(new Error('lost ack'))
        await controller.apply()
      }
      let releaseCatalog!: (
        value: Awaited<ReturnType<typeof bridge.getProjectManagementCatalog>>,
      ) => void
      let releaseState!: (value: BridgeResult<MainlineManagementItemDTO>) => void
      bridge.getProjectManagementCatalog.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            releaseCatalog = resolve
          }),
      )
      bridge.getProjectManagementState.mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            releaseState = resolve
          }),
      )
      const busy: boolean[] = []
      const release = controller.subscribe(() => busy.push(controller.getSnapshot().busy))
      const request = path === 'apply' ? controller.apply() : controller.reconcile()
      await vi.waitFor(() => expect(releaseCatalog).toBeTypeOf('function'))
      expect(controller.getSnapshot().busy).toBe(true)
      expect(busy).not.toContain(false)
      releaseCatalog(
        ok({
          catalogVersion: 1,
          snapshotId: 'tail',
          items: [item],
          total: 1,
          offset: 0,
          nextCursor: null,
        }),
      )
      await vi.waitFor(() => expect(releaseState).toBeTypeOf('function'))
      expect(controller.getSnapshot().busy).toBe(true)
      expect(busy).not.toContain(false)
      releaseState(ok(item))
      await request
      expect(controller.getSnapshot().busy).toBe(false)
      expect(busy.filter((value) => !value)).toHaveLength(1)
      release()
    })
  }
  it('settles a selected-state read waiting on busy when its document closes', async () => {
    const { bridge, controller, ready } = fixture()
    await ready()
    let releaseCatalog!: (
      value: Awaited<ReturnType<typeof bridge.getProjectManagementCatalog>>,
    ) => void
    bridge.getProjectManagementCatalog.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          releaseCatalog = resolve
        }),
    )
    const refresh = controller.refresh()
    const read = controller.readSelected()
    controller.close()
    await expect(read).resolves.toBeUndefined()
    expect(bridge.getProjectManagementState).not.toHaveBeenCalled()
    releaseCatalog(
      ok({
        catalogVersion: 1,
        snapshotId: 'closed',
        items: [],
        total: 0,
        offset: 0,
        nextCursor: null,
      }),
    )
    await refresh
  })
  it('starts each filter with a fresh cursor and retains a fixed cursor only for its next page', async () => {
    const { bridge, controller, ready } = fixture()
    await ready()
    await controller.refresh('archived', 'fixed-page')
    await controller.refresh('trashed')
    expect(bridge.getProjectManagementCatalog).toHaveBeenNthCalledWith(2, {
      state: 'archived',
      pageSize: 50,
      cursor: 'fixed-page',
    })
    expect(bridge.getProjectManagementCatalog).toHaveBeenNthCalledWith(3, {
      state: 'trashed',
      pageSize: 50,
      cursor: null,
    })
  })
})
