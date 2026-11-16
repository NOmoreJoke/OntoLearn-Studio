import { test, expect, _electron as electron, type Locator, type Page } from '@playwright/test'
import { resolve } from 'node:path'
import type { BridgeResult } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'

/**
 * B1b real Electron E2E: whole-project checkpoint, mixed-impact restore preview,
 * result invalidation isolation and FR-804 single-step undo.
 *
 * Every launch owns an isolated profile directory; the default Electron profile is
 * never used. The restart leg reuses this test's own isolated userData directory
 * so the persisted project library, checkpoint history and restored state must
 * survive a real process restart.
 */

function data<T>(value: BridgeResult<T>): T {
  if (!value.ok) throw new Error(`Actual B1b bridge refused: ${value.error.code}`)
  return value.data
}

function launchEnv(): Record<string, string> {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  return env
}

/** Source mode and packaged mode share one launch shape. */
function launchOptions(userDataDir?: string) {
  const env = launchEnv()
  const base = {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
    acceptDownloads: true,
  }
  return userDataDir ? { ...base, args: [...base.args, `--user-data-dir=${userDataDir}`] } : base
}

/**
 * The isolated launch helper owns one profile per launch. This leg reuses the
 * directory the previous launch reported, so the restart reads the same
 * persisted project library instead of a fresh empty profile.
 */
async function launchWithProfile(userDataDir?: string) {
  if (!userDataDir) return launchIsolatedDesktop(launchOptions())
  const application = await electron.launch(launchOptions(userDataDir))
  const actual = await application.evaluate(({ app }) => app.getPath('userData'))
  expect(actual).toBe(userDataDir)
  return application
}

function checkpoints(page: Page): Locator {
  return page.getByTestId('project-checkpoints')
}

async function ontologyPanel(page: Page): Promise<Locator> {
  await page.getByRole('link', { name: '本体构建', exact: true }).click()
  const panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
  await expect(panel).toBeVisible()
  return panel
}

async function queryPanel(page: Page): Promise<Locator> {
  await page.getByRole('link', { name: '本体查询', exact: true }).click()
  const panel = page.getByRole('region', { name: '本体查询工作台', exact: true })
  await expect(panel).toBeVisible()
  return panel
}

/** Confirms the real project management dialog (rename / mode switch). */
async function confirmManagement(page: Page): Promise<void> {
  const dialog = page.getByRole('dialog', { name: '项目管理确认', exact: true })
  await expect(dialog).toBeVisible()
  await dialog.getByRole('checkbox').check()
  await dialog.getByRole('button', { name: '确认并提交项目更改', exact: true }).click()
  await expect(dialog).not.toBeVisible({ timeout: 15000 })
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 15000 })
}

/** Submits one ontology definition through the real preview → confirm path. */
async function commitDefinition(
  page: Page,
  panel: Locator,
  identifier: string,
  label: string,
): Promise<void> {
  await panel.getByRole('button', { name: '新建概念', exact: true }).click()
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  await form.getByLabel('英文标识', { exact: true }).fill(identifier)
  const group = form.getByRole('group', { name: '名称（保留所有语言）', exact: true })
  await group.getByRole('button', { name: '添加名称', exact: true }).click()
  await group.getByRole('textbox', { name: '名称 1', exact: true }).fill(label)
  await group.getByLabel('语言标签 1', { exact: true }).fill('zh')
  await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
  const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
  await expect(diff).toBeVisible()
  await diff.getByRole('button', { name: '我已核对完整差异，确认提交', exact: true }).click()
  const receipt = panel.getByRole('region', { name: '已提交回执', exact: true })
  await expect(receipt).toBeVisible({ timeout: 30000 })
}

test('B1b whole-project restore rolls back mixed impacts and survives a real restart', async () => {
  test.setTimeout(120000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  let application: Awaited<ReturnType<typeof launchIsolatedDesktop>> | undefined =
    await launchIsolatedDesktop(launchOptions())
  try {
    const page = await application.firstWindow()

    stage = 'create a blank project and enter the ontology flow'
    await page.getByTestId('project-name').fill('B1b 整项目恢复')
    await page.getByTestId('project-create').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
      { timeout: 15000 },
    )
    await expect(page.getByTestId('selected-project-version')).toBeVisible({ timeout: 15000 })
    const projectId = await page.evaluate(async () => {
      const catalog = await window.ontolearn!.getProjectManagementCatalog({
        state: 'active',
        pageSize: 10,
        cursor: null,
      })
      if (!catalog.ok) throw new Error('Actual project catalog refused')
      return catalog.data.items[0]!.projectId
    })
    evidence.projectId = projectId

    stage = 'create the first manual checkpoint'
    await expect(checkpoints(page).getByTestId('checkpoint-create')).toBeEnabled({ timeout: 15000 })
    await checkpoints(page).getByLabel('检查点备注').fill('导入映射之前')
    await checkpoints(page).getByTestId('checkpoint-create').click()
    await expect(checkpoints(page).getByTestId('checkpoint-notice')).toContainText(
      '已创建手动检查点',
      {
        timeout: 15000,
      },
    )
    const catalog = checkpoints(page).getByTestId('checkpoint-list')
    await expect(catalog).toBeVisible({ timeout: 15000 })
    const cp1 = catalog.locator('li').filter({ hasText: '导入映射之前' })
    await expect(cp1).toHaveCount(1)
    const cp1Ref = await cp1.getAttribute('data-checkpoint-ref')
    if (!cp1Ref) throw new Error('Actual checkpoint list exposes no checkpoint reference')
    evidence.cp1Ref = cp1Ref

    stage = 'commit one domain change so the checkpoint predates a real domain write'
    let panel = await ontologyPanel(page)
    await commitDefinition(page, panel, 'b1b-equipment', '设备')

    stage = 'run one query so a current result exists'
    panel = await queryPanel(page)
    await panel.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
    await expect(panel.getByRole('button', { name: '新建查询草稿', exact: true })).toBeEnabled({
      timeout: 15000,
    })
    await panel.getByRole('button', { name: '新建查询草稿', exact: true }).click()
    await panel.getByLabel('项目内查询标识', { exact: true }).fill('b1b-query')
    await panel.getByLabel('名称', { exact: true }).fill('B1b 恢复核对查询')
    await panel
      .getByRole('textbox', { name: '可见 SPARQL', exact: true })
      .fill(
        'PREFIX l: <urn:ontolearn:learning:>\n' +
          'SELECT ?equipment WHERE { ?equipment a l:Equipment . } ORDER BY ?equipment',
      )
    await panel.getByRole('button', { name: '保存工作草稿（不提交正式定义）', exact: true }).click()
    await expect(panel.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '工作草稿已持久化；正式定义尚未提交。',
    )
    const prepare = panel.getByRole('button', { name: '读取正式保存的完整差异', exact: true })
    await expect(prepare).toBeEnabled()
    await prepare.click()
    const diff = panel.getByRole('region', { name: '正式提交完整差异', exact: true })
    await expect(diff).toBeVisible()
    await diff
      .getByRole('checkbox', { name: '我已核对完整差异，确认提交此版本', exact: true })
      .check()
    await diff.getByRole('button', { name: '明确确认并提交真实任务', exact: true }).click()
    await expect(
      panel.getByRole('region', { name: '真实查询或提交任务', exact: true }),
    ).toContainText('：succeeded；', { timeout: 60000 })
    const execute = panel.getByRole('button', {
      name: '执行已载入且未改变的受管定义',
      exact: true,
    })
    await expect(execute).toBeEnabled({ timeout: 30000 })
    await execute.click()
    await expect(
      panel.getByRole('region', { name: '真实查询或提交任务', exact: true }),
    ).toContainText('：succeeded；', { timeout: 60000 })
    const refresh = panel.getByRole('button', {
      name: '刷新任务、原操作与固定结果',
      exact: true,
    })
    await expect(refresh).toBeEnabled()
    await refresh.click()
    const resultPanel = panel.getByRole('region', { name: '查询结果', exact: true })
    await expect(resultPanel).toBeVisible({ timeout: 30000 })
    await expect(resultPanel).toContainText('当前结果')
    const currentDescriptor = data(
      await page
        .evaluate(() => window.ontolearn!.getQueryResultDescriptor({ resultId: '' }))
        .catch(() => ({ ok: false, error: { code: 'INVALID_REQUEST' } }) as never),
    )
    void currentDescriptor

    stage = 'rename, switch mode and save a durable draft without invalidating the result'
    await page.getByLabel('新名称或副本名称', { exact: true }).fill('B1b 恢复前改名')
    await page.getByRole('button', { name: '预览重命名', exact: true }).click()
    await confirmManagement(page)
    await page.getByLabel('界面模式', { exact: true }).selectOption('assisted')
    await confirmManagement(page)
    const afterManagement = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    evidence.afterManagement = {
      mode: afterManagement.workspace.metadata.mode,
      name: afterManagement.workspace.metadata.name,
    }
    expect(afterManagement.workspace.metadata.mode).toBe('assisted')
    expect(afterManagement.workspace.metadata.name).toBe('B1b 恢复前改名')

    stage = 'create a second checkpoint so both checkpoints remain in the history'
    await checkpoints(page).getByLabel('检查点备注').fill('改名之后')
    await checkpoints(page).getByTestId('checkpoint-create').click()
    await expect(checkpoints(page).getByTestId('checkpoint-notice')).toContainText(
      '已创建手动检查点',
      {
        timeout: 15000,
      },
    )
    await expect(
      checkpoints(page)
        .getByTestId('checkpoint-list')
        .locator('li')
        .filter({ hasText: '导入映射之前' }),
    ).toHaveCount(1)

    stage = 'preview the whole-project restore of the first checkpoint'
    const cp1Preview = checkpoints(page)
      .getByTestId('checkpoint-list')
      .locator('li')
      .filter({ hasText: '导入映射之前' })
      .getByTestId('checkpoint-restore-preview')
    await expect(cp1Preview).toBeEnabled({ timeout: 15000 })
    await cp1Preview.click()
    const preview = checkpoints(page).getByTestId('restore-preview')
    await expect(preview).toBeVisible({ timeout: 30000 })
    await expect(preview.getByTestId('restore-read-progress')).toHaveAttribute(
      'data-complete',
      'true',
      {
        timeout: 30000,
      },
    )
    await expect(preview).toContainText('领域差异')
    await expect(preview).toContainText('元数据 / 草稿 / 学习状态差异')
    const operations = preview.getByTestId('restore-impact-ops')
    await expect(operations).toBeVisible()
    await expect(operations).toContainText('rename')
    await expect(operations).toContainText('draft-save')
    await expect(operations).toContainText('application')
    await expect(preview).toContainText('覆盖范围')
    await expect(preview).toContainText('保留不变')

    stage = 'confirm the restore and type the explicit consent'
    await preview.getByTestId('restore-confirm').click()
    await expect(checkpoints(page).getByTestId('restore-consent')).toBeVisible({ timeout: 30000 })
    const apply = checkpoints(page).getByTestId('restore-apply')
    await expect(apply).toBeDisabled()
    await checkpoints(page).getByTestId('restore-consent').fill('恢复')
    await expect(apply).toBeEnabled()
    await apply.click()
    await expect(checkpoints(page).getByTestId('checkpoint-notice')).toContainText(
      '整项目恢复已完成',
      { timeout: 60000 },
    )

    stage = 'verify the restored project state'
    const restored = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    evidence.restored = {
      mode: restored.workspace.metadata.mode,
      name: restored.workspace.metadata.name,
      revision: restored.domain.projectRevision,
    }
    expect(restored.workspace.metadata.name).toBe('B1b 整项目恢复')
    expect(restored.workspace.metadata.mode).toBe('guided')
    await expect(page.getByTestId('selected-project-version')).toContainText(
      `当前项目版本 ${restored.domain.projectRevision}`,
    )
    const restoredCheckpoints = data(
      await page.evaluate(() =>
        window.ontolearn!.listProjectCheckpoints({ pageSize: 50, cursor: null }),
      ),
    )
    evidence.restoredCheckpoints = restoredCheckpoints.items.map((item) => ({
      checkpointRef: item.checkpointRef,
      reason: item.reason,
      label: item.label,
      isCurrent: item.isCurrent,
    }))
    expect(restoredCheckpoints.items.some((item) => item.checkpointRef === cp1Ref)).toBe(true)
    expect(
      restoredCheckpoints.items.some((item) => item.reason === 'restore' && item.isCurrent),
    ).toBe(true)

    stage = 'restart the same isolated profile and verify the restored state persisted'
    const launch = await application.evaluate(({ app }) => ({
      userData: app.getPath('userData'),
      sessionData: app.getPath('sessionData'),
      appPath: app.getAppPath(),
      packaged: app.isPackaged,
      pid: process.pid,
    }))
    evidence.launch = launch
    await application.close()
    application = undefined

    application = await launchWithProfile(launch.userData)
    const restarted = await application.firstWindow()
    await expect(restarted.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 30000 })
    const open = restarted.locator(`[data-testid="project-open"][data-project-id="${projectId}"]`)
    await expect(open).toBeVisible({ timeout: 30000 })
    await open.click()
    await expect(restarted.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 30000 })
    const afterRestart = data(
      await restarted.evaluate(() =>
        window.ontolearn!.readProject({ editor: 'query-workspace-v1' }),
      ),
    )
    evidence.afterRestart = {
      mode: afterRestart.workspace.metadata.mode,
      name: afterRestart.workspace.metadata.name,
      revision: afterRestart.domain.projectRevision,
    }
    expect(afterRestart.workspace.metadata.name).toBe('B1b 整项目恢复')
    expect(afterRestart.workspace.metadata.mode).toBe('guided')
    expect(afterRestart.domain.projectRevision).toBe(restored.domain.projectRevision)
    const restartCheckpoints = data(
      await restarted.evaluate(() =>
        window.ontolearn!.listProjectCheckpoints({ pageSize: 50, cursor: null }),
      ),
    )
    evidence.restartCheckpoints = restartCheckpoints.items.map((item) => ({
      checkpointRef: item.checkpointRef,
      reason: item.reason,
      label: item.label,
      isCurrent: item.isCurrent,
    }))
    expect(restartCheckpoints.items.some((item) => item.checkpointRef === cp1Ref)).toBe(true)
    expect(
      restartCheckpoints.items.some((item) => item.reason === 'restore' && item.isCurrent),
    ).toBe(true)
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('b1b-restore-invalidation-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application?.close()
    }
  }
})

test('B1b FR-804 single-step undo pauses on conflict and cleanly undoes the latest commit', async () => {
  test.setTimeout(120000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  const application = await launchIsolatedDesktop(launchOptions())
  try {
    const page = await application.firstWindow()
    stage = 'create a blank project'
    await page.getByTestId('project-name').fill('B1b 单步撤销')
    await page.getByTestId('project-create').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
      { timeout: 15000 },
    )

    stage = 'commit the first definition'
    const panel = await ontologyPanel(page)
    await commitDefinition(page, panel, 'b1b-undo-first', '首个定义')
    const firstReceipt = panel.getByRole('region', { name: '已提交回执', exact: true })
    await expect(firstReceipt).toBeVisible({ timeout: 30000 })
    const firstOperation = await firstReceipt.locator('code').first().textContent()
    if (!firstOperation) throw new Error('Actual receipt exposes no original operation')
    evidence.firstOperation = firstOperation

    stage = 'commit a second change on the same resource to arm the undo conflict'
    await panel.getByRole('button', { name: '读取当前项目', exact: true }).click()
    await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled({
      timeout: 15000,
    })
    await commitDefinition(page, panel, 'b1b-undo-first', '改名后的定义')
    const secondReceipt = panel.getByRole('region', { name: '已提交回执', exact: true })
    await expect(secondReceipt).toBeVisible({ timeout: 30000 })
    const secondOperation = await secondReceipt.locator('code').first().textContent()
    if (!secondOperation) throw new Error('Actual receipt exposes no original operation')
    evidence.secondOperation = secondOperation
    expect(secondOperation).not.toBe(firstOperation)

    stage = 'the newest commit undoes cleanly'
    await secondReceipt.getByRole('button', { name: '预览撤销本次修改', exact: true }).click()
    const cleanDiff = panel.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(cleanDiff).toBeVisible({ timeout: 30000 })
    await expect(cleanDiff).toContainText('完整事务差异 · 尚未提交')
    await expect(cleanDiff).not.toContainText('撤销冲突影响')
    await cleanDiff.getByRole('button', { name: '我已核对完整差异，确认提交', exact: true }).click()
    await expect(panel.getByRole('region', { name: '已提交回执', exact: true })).toBeVisible({
      timeout: 30000,
    })

    stage = 'the earlier commit now conflicts and the undo is paused without a partial write'
    const afterUndo = panel.getByRole('region', { name: '已提交回执', exact: true })
    await expect(afterUndo).toBeVisible({ timeout: 30000 })
    await afterUndo.getByRole('button', { name: '预览撤销本次修改', exact: true }).click()
    const conflictDiff = panel.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(conflictDiff).toBeVisible({ timeout: 30000 })
    await expect(conflictDiff).toContainText('撤销冲突影响')
    const paused = conflictDiff.getByTestId('undo-conflict-paused')
    await expect(paused).toBeVisible()
    await expect(paused).toContainText('撤销已暂停')
    await expect(
      conflictDiff.getByRole('button', { name: '我已核对完整差异，确认提交', exact: true }),
    ).toBeDisabled()
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('b1b-fr804-undo-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application.close()
    }
  }
})
