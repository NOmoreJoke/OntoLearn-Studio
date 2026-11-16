import { describe, expect, it, vi } from 'vitest'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import {
  libraryAdmissionBlocked,
  settleManagementTail,
  type LibraryAdmissionState,
  type ManagementAdmissionTail,
} from '../../apps/desktop/src/renderer/src/project/lifecycle-admission'

function deferredTail() {
  const order: string[] = []
  const release: Record<'refresh' | 'read', (() => void) | undefined> = {
    refresh: undefined,
    read: undefined,
  }
  const management = {
    select: vi.fn((projectId?: string) => {
      order.push(`select:${projectId ?? 'undefined'}`)
    }),
    refresh: vi.fn(
      () =>
        new Promise<void>((resolve) => {
          order.push('refresh:start')
          release.refresh = resolve
        }),
    ),
    readSelected: vi.fn(
      () =>
        new Promise<void>((resolve) => {
          order.push('read:start')
          release.read = resolve
        }),
    ),
  } satisfies ManagementAdmissionTail
  return { order, release, management }
}

describe('B1a lifecycle admission serialization and switching policy', () => {
  it('settles every management read serially before resolving the tail (open/create)', async () => {
    const { order, release, management } = deferredTail()
    const tail = settleManagementTail(management, 'project-b', { refresh: true })
    await Promise.resolve()
    // refresh 仍在飞行时，readSelected 不允许开始（单并发模型）。
    expect(order).toEqual(['select:project-b', 'refresh:start'])
    expect(management.readSelected).not.toHaveBeenCalled()
    release.refresh!()
    await vi.waitFor(() => expect(release.read).toBeTypeOf('function'))
    expect(order).toEqual(['select:project-b', 'refresh:start', 'read:start'])
    release.read!()
    await expect(tail).resolves.toBeUndefined()
    expect(management.select).toHaveBeenCalledTimes(1)
    expect(management.refresh).toHaveBeenCalledTimes(1)
    expect(management.readSelected).toHaveBeenCalledTimes(1)
  })
  it('serializes autonomous restores as select then the selected-state read only', async () => {
    const { order, release, management } = deferredTail()
    const tail = settleManagementTail(management, 'project-a')
    await Promise.resolve()
    expect(order).toEqual(['select:project-a', 'read:start'])
    expect(management.refresh).not.toHaveBeenCalled()
    release.read!()
    await expect(tail).resolves.toBeUndefined()
  })
  it('keeps a missing management surface or selection a no-op tail', async () => {
    const { management } = deferredTail()
    await expect(settleManagementTail(undefined, 'project-a')).resolves.toBeUndefined()
    await expect(settleManagementTail(management, undefined)).resolves.toBeUndefined()
    expect(management.select).not.toHaveBeenCalled()
    expect(management.readSelected).not.toHaveBeenCalled()
  })
  it('admits project and module switching while an ontology form is dirty', () => {
    const idle: LibraryAdmissionState = {
      documentLeaving: false,
      libraryBusy: false,
      frozen: false,
      managementUnresolved: false,
    }
    // 未保存编辑（ontologyDirty）不是准入输入：闸门结构上没有该字段，
    // 切换通过 retireOntology() 自动退役旧会话；dirty 只保留在
    // aggregateWorkspace 报告里拦截高危库操作。
    expect(Object.keys(idle).sort()).toEqual([
      'documentLeaving',
      'frozen',
      'libraryBusy',
      'managementUnresolved',
    ])
    expect(libraryAdmissionBlocked(idle)).toBe(false)
    for (const key of Object.keys(idle) as Array<keyof LibraryAdmissionState>)
      expect(libraryAdmissionBlocked({ ...idle, [key]: true })).toBe(true)
  })
})

describe('B1a overview structure regression (static, not a rendering proof)', () => {
  const app = readFileSync(
    fileURLToPath(new URL('../../apps/desktop/src/renderer/src/App.tsx', import.meta.url)),
    'utf8',
  )
  it('keeps the engine check panel inside the first viewport band above the project library', () => {
    // 1024x720 视口断言（desktop.spec.ts）由真实 E2E 负责；这里锚定 DOM 顺序：
    // 检查本地引擎面板必须位于项目库之前，否则会被长面板挤出首屏。
    expect(app.indexOf('id="health-title"')).toBeGreaterThanOrEqual(0)
    expect(app.indexOf('id="health-title"')).toBeLessThan(
      app.indexOf('data-testid="project-library"'),
    )
  })
  it('no longer hard-blocks project or module switching on a dirty ontology form', () => {
    expect(app).not.toContain('请先提交或清空本体编辑表单')
    expect(app).not.toContain('本体表单有未保存编辑')
  })
  it('still reports ontology dirty state for destructive library operations', () => {
    expect(app).toContain('dirty: ontologyDirty.current ||')
  })
  it('keeps the engine check disabled while the workspace is frozen or management is unresolved', () => {
    expect(app).toMatch(/disabled=\{checking \|\| workspaceFrozen \|\| managementBlocked\}/)
  })
})
