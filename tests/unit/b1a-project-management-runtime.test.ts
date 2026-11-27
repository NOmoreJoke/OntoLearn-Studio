/** Real Python stdio / Store / main-process service. No Electron or OS picker claim. */
import { expect, it } from 'vitest'
import { randomUUID } from 'node:crypto'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import type { BridgeResult, MainlineManagementAction } from '@ontolearn/contracts'
import { EngineSupervisor, getEngineCommand } from '../../apps/desktop/src/main/engine'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'

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
    { managementJournalPath: join(directory, 'intents.json') },
  )
  const replies = supervisor.mainlineReplyReceiver()
  return {
    supervisor,
    projects,
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
async function prepared(r: ReturnType<typeof runtime>, action: MainlineManagementAction) {
  const item = await r.call(() => r.projects.getProjectManagementState())
  const preview = await r.call(() =>
    r.projects.previewProjectManagement({
      action,
      expectedCheckpointRef: item.checkpointRef,
      expectedLifecycleVersion: item.lifecycle.version,
    }),
  )
  const confirmation = await r.call(() =>
    r.projects.confirmProjectManagement({
      previewRef: preview.previewRef,
      documentHash: preview.documentHash,
    }),
  )
  return {
    operationId: randomUUID(),
    confirmationRef: confirmation.confirmationRef,
    documentHash: confirmation.documentHash,
  }
}

it('real management commits metadata, copies current state, trashes and restores the original project', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'b1a-management-'))
  const r = runtime(directory)
  try {
    const created = await r.call(() =>
      r.projects.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: '原项目',
        initialization: { kind: 'blank' },
      }),
    )
    await r.call(() => r.projects.openProject({ projectId: created.projectId }))
    const first = await r.call(() => r.projects.getProjectManagementState())
    const rename = await prepared(r, { kind: 'rename', name: '已重命名' })
    const renamed = await r.call(() => r.projects.applyProjectManagement(rename))
    expect(renamed).toMatchObject({
      projectId: created.projectId,
      targetProjectId: created.projectId,
      kind: 'rename',
      domainRevision: first.domainRevision,
      metadataVersion: first.metadataVersion + 1,
    })
    expect(r.projects.hasUnresolvedResponsibility).toBe(false)
    const next = await r.call(() => r.projects.getProjectManagementState())
    expect(next.metadata.name).toBe('已重命名')
    expect(next.checkpointRef).not.toBe(first.checkpointRef)
    const copy = await prepared(r, { kind: 'copy-current', name: '独立副本' })
    const copied = await r.call(() => r.projects.applyProjectManagement(copy))
    expect(copied.targetProjectId).not.toBe(created.projectId)
    expect(copied).toMatchObject({
      domainRevision: 1,
      operationSequence: 1,
      lifecycleState: 'active',
    })
    expect(r.projects.source.current()?.project.projectId).toBe(created.projectId)
    const trash = await prepared(r, { kind: 'trash' })
    const trashed = await r.call(() => r.projects.applyProjectManagement(trash))
    expect(trashed.lifecycleState).toBe('trashed')
    expect(r.projects.source.current()).toBe(null)
    expect(
      await r.call(() =>
        r.projects.getProjectManagementOperation({ operationId: trash.operationId }),
      ),
    ).toMatchObject({ state: 'applied', result: trashed })
    const denied = await r.replies.receive(() =>
      r.projects.openProject({ projectId: created.projectId }),
    )
    r.replies.consume(denied.receipt)
    expect(denied.value.ok).toBe(false)
    const deleted = await r.call(() =>
      r.projects.getProjectManagementCatalog({ state: 'trashed', pageSize: 10, cursor: null }),
    )
    expect(deleted.items.map((item) => item.projectId)).toEqual([created.projectId])
    const item = deleted.items[0]
    const preview = await r.call(() =>
      r.projects.previewProjectManagement({
        action: { kind: 'restore-trash' },
        restoreProjectId: item.projectId,
        expectedCheckpointRef: item.checkpointRef,
        expectedLifecycleVersion: item.lifecycle.version,
      }),
    )
    const confirmation = await r.call(() =>
      r.projects.confirmProjectManagement({
        previewRef: preview.previewRef,
        documentHash: preview.documentHash,
      }),
    )
    const restored = await r.call(() =>
      r.projects.applyProjectManagement({
        operationId: randomUUID(),
        confirmationRef: confirmation.confirmationRef,
        documentHash: confirmation.documentHash,
      }),
    )
    expect(restored).toMatchObject({
      targetProjectId: created.projectId,
      lifecycleState: 'active',
      lifecycleVersion: trashed.lifecycleVersion + 1,
    })
    await r.call(() => r.projects.openProject({ projectId: created.projectId }))
    expect((await r.call(() => r.projects.getProjectManagementState())).metadata.name).toBe(
      '已重命名',
    )
    const catalog = await r.call(() =>
      r.projects.getProjectManagementCatalog({ state: 'active', pageSize: 10, cursor: null }),
    )
    expect(catalog.items.map((item) => item.projectId).sort()).toEqual(
      [created.projectId, copied.targetProjectId].sort(),
    )
  } finally {
    await r.close()
    await rm(directory, { recursive: true, force: true })
  }
}, 45000)

it('an unacknowledged committed operation survives restart and is reconciled without replay', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'b1a-ack-restart-'))
  let r = runtime(directory)
  try {
    const created = await r.call(() =>
      r.projects.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: '原项目',
        initialization: { kind: 'blank' },
      }),
    )
    await r.call(() => r.projects.openProject({ projectId: created.projectId }))
    const args = await prepared(r, { kind: 'copy-current', name: '唯一副本' })
    const unacknowledged = await r.replies.receive(() => r.projects.applyProjectManagement(args))
    const committed = data(unacknowledged.value)
    expect(r.projects.hasUnresolvedResponsibility).toBe(true)
    let journal = JSON.parse(await readFile(join(directory, 'intents.json'), 'utf8'))
    expect(journal.records[0]).toMatchObject({ delivered: false, outcome: 'applied', params: args })
    await r.close()
    r = runtime(directory)
    const pending = await r.call(() => r.projects.getPendingProjectManagementOperations())
    expect(pending).toEqual([
      {
        projectId: created.projectId,
        operationId: args.operationId,
        kind: 'copy-current',
        label: '原项目',
      },
    ])
    const known = await r.call(() =>
      r.projects.getProjectManagementOperation({ operationId: args.operationId }),
    )
    expect(known).toEqual({ state: 'applied', result: committed })
    expect(await r.call(() => r.projects.getPendingProjectManagementOperations())).toEqual([])
    expect(r.projects.hasUnresolvedResponsibility).toBe(false)
    const replay = await r.replies.receive(() => r.projects.applyProjectManagement(args))
    r.replies.consume(replay.receipt)
    expect(replay.value.ok).toBe(false)
    const catalog = await r.call(() =>
      r.projects.getProjectManagementCatalog({ state: 'active', pageSize: 10, cursor: null }),
    )
    expect(
      catalog.items
        .filter((item) => item.metadata.name === '唯一副本')
        .map((item) => item.projectId),
    ).toEqual([committed.targetProjectId])
    journal = JSON.parse(await readFile(join(directory, 'intents.json'), 'utf8'))
    expect(journal.records[0].delivered).toBe(true)
  } finally {
    await r.close()
    await rm(directory, { recursive: true, force: true })
  }
}, 45000)

it('a corrupt persisted intent journal fences management without overwriting the first evidence', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'b1a-corrupt-intent-'))
  const original = '{"journalVersion":1,"records":[{"not":"a receipt"}]}'
  await writeFile(join(directory, 'intents.json'), original)
  const r = runtime(directory)
  try {
    expect(r.projects.hasUnresolvedResponsibility).toBe(true)
    expect(await r.projects.getPendingProjectManagementOperations()).toMatchObject({ ok: false })
    expect(await readFile(join(directory, 'intents.json'), 'utf8')).toBe(original)
  } finally {
    await r.close()
    await rm(directory, { recursive: true, force: true })
  }
})

it('rejects a not-found reconciliation that contradicts an already durable receipt after a same-library rollback', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'b1a-known-receipt-'))
  let r = runtime(directory)
  try {
    const created = await r.call(() =>
      r.projects.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: '原项目',
        initialization: { kind: 'blank' },
      }),
    )
    await r.call(() => r.projects.openProject({ projectId: created.projectId }))
    const backup = join(directory, 'before.sqlite')
    const python = getEngineCommand({
      packaged: false,
      appPath: resolve('apps/desktop'),
      resourcesPath: resolve('.'),
    }).command
    await promisify(execFile)(python, [
      '-I',
      '-c',
      'import sqlite3,sys; a=sqlite3.connect(sys.argv[1]); b=sqlite3.connect(sys.argv[2]); a.backup(b); b.close(); a.close()',
      join(directory, 'library.sqlite'),
      backup,
    ])
    const args = await prepared(r, { kind: 'rename', name: '实际已提交' })
    const delivery = await r.replies.receive(() => r.projects.applyProjectManagement(args))
    const applied = data(delivery.value)
    expect(applied.kind).toBe('rename')
    const originalJournal = await readFile(join(directory, 'intents.json'), 'utf8')
    await r.close()
    // A valid older snapshot of the same library has no record of the known commit.
    await writeFile(join(directory, 'library.sqlite'), await readFile(backup))
    r = runtime(directory)
    const rejected = await r.replies.receive(() =>
      r.projects.getProjectManagementOperation({ operationId: args.operationId }),
    )
    expect(rejected.value).toMatchObject({ ok: false })
    expect(r.projects.hasUnresolvedResponsibility).toBe(true)
    expect(await readFile(join(directory, 'intents.json'), 'utf8')).toBe(originalJournal)
  } finally {
    await r.close()
    await rm(directory, { recursive: true, force: true })
  }
}, 45000)
