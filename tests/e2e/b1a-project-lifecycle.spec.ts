import { test, expect, type Page } from '@playwright/test'
import { resolve } from 'node:path'
import type { BridgeResult } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'
import { recordB1aApplication, closeB1aApplication } from './b1a-process-evidence'

function data<T>(value: BridgeResult<T>): T {
  if (!value.ok) throw new Error(`B1a actual bridge refused: ${value.error.code}`)
  return value.data
}
async function launch() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  const application = await launchIsolatedDesktop({
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })
  await recordB1aApplication(application)
  return application
}
async function confirm(page: Page) {
  const dialog = page.getByRole('dialog', { name: '项目管理确认', exact: true })
  await expect(dialog).toBeVisible()
  await expect(dialog).toContainText('本次覆盖')
  await expect(dialog).toContainText('保留或排除')
  await expect(
    dialog.getByRole('button', { name: '确认并提交项目更改', exact: true }),
  ).toBeDisabled()
  await dialog.getByRole('checkbox').check()
  await dialog.getByRole('button', { name: '确认并提交项目更改', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
}

test('B1a first launch, metadata modes and archive retain the live query draft', async () => {
  const application = await launch()
  try {
    const page = await application.firstWindow()
    await expect(page.getByTestId('project-create')).toBeVisible()
    await expect(page.getByTestId('project-create-example')).toBeVisible()
    await expect(page.getByRole('button', { name: '打开已有项目', exact: true })).toBeVisible()
    await page.getByRole('button', { name: '查看快速介绍', exact: true }).click()
    const intro = page.getByRole('dialog', { name: '快速介绍', exact: true })
    await expect(intro).toContainText('完整项目导出仍待接入')
    await intro.getByRole('button', { name: '关闭介绍' }).click()
    await page.getByRole('button', { name: '查看快速介绍', exact: true }).click()
    await expect(intro).toBeVisible()
    await intro.getByRole('button', { name: '关闭介绍' }).click()
    await page.getByTestId('project-name').fill('B1a 模式与草稿')
    await page.getByTestId('project-create').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    const workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    await workspace.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
    await expect(workspace.getByRole('button', { name: '新建查询草稿', exact: true })).toBeEnabled()
    await workspace.getByRole('button', { name: '新建查询草稿', exact: true }).click()
    const input = workspace.getByLabel('名称', { exact: true })
    await input.fill('还没有保存的查询')
    await input.evaluate((node) => node.setAttribute('data-b1a-instance', 'same-live-editor'))
    const before = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    await page.getByLabel('界面模式', { exact: true }).selectOption('assisted')
    await confirm(page)
    await expect(page.locator('.app-shell')).toHaveAttribute('data-workspace-mode', 'assisted')
    await expect(input).toHaveValue('还没有保存的查询')
    await expect(input).toHaveAttribute('data-b1a-instance', 'same-live-editor')
    await expect(page.locator('.guided-help')).not.toBeVisible()
    const after = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(after.domain).toEqual(before.domain)
    expect(after.workspace.metadata.mode).toBe('assisted')
    await expect(page.getByRole('button', { name: '删除项目…', exact: true })).toBeDisabled()
    await page.getByRole('button', { name: '选择空目录建立项目库', exact: true }).click()
    await expect(page.getByTestId('library-location-notice')).toContainText(
      '请先保存或清空编辑表单',
    )
    await expect(input).toBeEnabled()
    await expect(input).toHaveValue('还没有保存的查询')
    await page.getByRole('button', { name: '预览归档', exact: true }).click()
    await confirm(page)
    await expect(page.getByRole('region', { name: '当前项目管理' })).toContainText(
      '仍可显式编辑和运行',
    )
    await expect(input).toHaveValue('还没有保存的查询')
    await page.getByRole('button', { name: '已归档', exact: true }).click()
    await expect(page.getByTestId('project-open')).toHaveCount(1)
    await page.getByLabel('界面模式', { exact: true }).selectOption('guided')
    await confirm(page)
    await expect(page.locator('.guided-help')).toBeVisible()
    await expect(input).toHaveAttribute('data-b1a-instance', 'same-live-editor')
    await test.info().attach('b1a-mode-metadata-evidence', {
      body: JSON.stringify({ before, after }),
      contentType: 'application/json',
    })
  } finally {
    await closeB1aApplication(application)
  }
})

test('B1a explicit current-state copy, trash default archive, and restore use actual management receipts', async () => {
  const application = await launch()
  try {
    const page = await application.firstWindow()
    await page.getByTestId('project-name').fill('B1a 原设备示例')
    await page.getByTestId('project-create-example').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    const source = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    await page.getByLabel('新名称或副本名称', { exact: true }).fill('B1a 独立当前态副本')
    await page.getByRole('button', { name: '预览复制当前状态', exact: true }).click()
    await confirm(page)
    const unchanged = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(unchanged).toEqual(source)
    await expect(page.getByTestId('project-management-notice')).toContainText('当前仍是源项目')
    await page.getByTestId('project-open-copy').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开',
    )
    const copied = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(copied.projectId).not.toBe(source.projectId)
    expect(copied.domain.projectRevision).toBe(1)
    expect(copied.domain.state).toEqual(source.domain.state)
    expect(data(await page.evaluate(() => window.ontolearn!.restoreTasks())).jobs).toEqual([])
    await page.getByRole('button', { name: '删除项目…', exact: true }).click()
    const options = page.getByRole('dialog', { name: '选择归档或删除', exact: true })
    await expect(
      options.getByRole('button', { name: '预览归档（推荐）', exact: true }),
    ).toBeVisible()
    await options.getByRole('button', { name: '取消', exact: true }).click()
    expect(
      data(await page.evaluate(() => window.ontolearn!.getProjectManagementState())).lifecycle
        .state,
    ).toBe('active')
    await page.getByRole('button', { name: '删除项目…', exact: true }).click()
    await options.getByRole('button', { name: '仍要移至回收站：查看影响', exact: true }).click()
    await expect(page.getByRole('dialog', { name: '项目管理确认', exact: true })).toContainText(
      '不会永久删除历史',
    )
    await confirm(page)
    await expect(page.getByTestId('selected-project-version')).not.toBeVisible()
    await page.getByRole('button', { name: '回收站', exact: true }).click()
    const restore = page.getByTestId('project-restore-trash')
    await expect(restore).toHaveAttribute('data-project-id', copied.projectId)
    await restore.click()
    await confirm(page)
    await page.getByRole('button', { name: '使用中', exact: true }).click()
    await page
      .locator(`[data-testid="project-open"][data-project-id="${copied.projectId}"]`)
      .click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开',
    )
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    const restored = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(restored.domain).toEqual(copied.domain)
    expect(data(await page.evaluate(() => window.ontolearn!.restoreTasks())).jobs).toEqual([])
    await test.info().attach('b1a-copy-trash-restore-evidence', {
      body: JSON.stringify({ source, unchanged, copied, restored }),
      contentType: 'application/json',
    })
  } finally {
    await closeB1aApplication(application)
  }
})
