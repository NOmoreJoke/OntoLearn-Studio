import { createHash } from 'node:crypto'
import { copyFile, mkdir, readFile, realpath, rm } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import {
  _electron as electron,
  expect,
  test,
  type ElectronApplication,
  type Page,
} from '@playwright/test'
import type { BridgeResult } from '@ontolearn/contracts'
import { closeB1aApplication, recordB1aApplication } from './b1a-process-evidence'
import { launchIsolatedDesktop } from './isolated-desktop'

function take<T>(result: BridgeResult<T>): T {
  if (!result.ok) throw new Error(JSON.stringify(result.error))
  return result.data
}

async function visible(app: ElectronApplication) {
  const page = await app.firstWindow()
  await expect
    .poll(() => app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0]?.isVisible()))
    .toBe(true)
  await expect(page.getByTestId('project-library')).toBeVisible()
  await recordB1aApplication(app)
  return page
}

async function state(page: Page) {
  return take(await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology' })))
}

async function reopenProject(page: Page, projectId: string) {
  const opens = page.locator(`[data-testid="project-open"][data-project-id="${projectId}"]`).first()
  await opens.click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText('项目已打开')
  await expect(opens).toBeEnabled()
  await expect
    .poll(() =>
      page.evaluate(async () => {
        const reply = await window.ontolearn!.getActiveProject()
        return reply.ok ? reply.data?.projectId : null
      }),
    )
    .toBe(projectId)
  const project = await state(page)
  expect(project.projectId).toBe(projectId)
  return project
}

async function openScenarioFromEditedBehavior(page: Page) {
  const confirmation = page.waitForEvent('dialog')
  const click = page.locator('a[href="#scenario-workspace"]').click()
  const dialog = await confirmation
  try {
    expect(dialog.type()).toBe('confirm')
    expect(dialog.message()).toContain('切换工作台将放弃此处未保存的编辑')
  } finally {
    await dialog.accept()
    await click
  }
}

test('W4 mapping, isolated behavior and scenario, package and HTML transfer survive desktop restart', async () => {
  const info = test.info()
  await mkdir(info.outputDir, { recursive: true })
  const directory = await realpath(info.outputDir)
  const source = join(directory, 'equipment.csv')
  const archive = join(directory, 'workspace.ontolearn.zip')
  const report = join(directory, 'learning.html')
  await copyFile(resolve('tests/fixtures/product-baselines/equipment.csv'), source)
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  for (const name of ['ELECTRON_RUN_AS_NODE', 'ELECTRON_RENDERER_URL', 'I04_TEST_FIXTURE'])
    delete env[name]
  env.ONTOLEARN_E2E_W4_PICKERS = JSON.stringify([
    { purpose: 'mapping-source', filePath: null },
    { purpose: 'mapping-source', filePath: source },
    { purpose: 'package-export', filePath: null },
    { purpose: 'package-export', filePath: archive },
    { purpose: 'package-import', filePath: archive },
    { purpose: 'report-html', filePath: report },
  ])
  const options = {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] as string[] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  }
  let app: ElectronApplication | undefined
  let userData: string | undefined
  try {
    app = await launchIsolatedDesktop(options)
    const page = await visible(app)
    userData = await app.evaluate(({ app }) => app.getPath('userData'))
    await page.getByTestId('learning-start-example').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    const baseline = await state(page)

    await page.locator('a[href="#mapping-workspace"]').click()
    const mapping = page.locator('#mapping-workspace')
    const choose = mapping.getByRole('button', { name: '选择 CSV / XLSX 与工作表' })
    await choose.click()
    await expect(mapping.getByRole('alert')).toBeVisible()
    await choose.click()
    await expect(mapping.getByText('工作表 CSV · 2 行')).toBeVisible()
    await mapping.getByLabel('映射标识').fill('w4-desktop')
    await mapping.getByLabel('实体命名空间（以 / 结尾）').fill('urn:ontolearn:w4:equipment/')
    await mapping.getByLabel('概念 IRI').fill('urn:ontolearn:learning:Equipment')
    await mapping.getByLabel('equipment_id 参与主键').check()
    const nameField = mapping
      .locator('.mapping-field')
      .filter({ hasText: 'equipment_name 参与主键' })
    await nameField.getByLabel('映射此字段').check()
    await nameField.getByLabel('属性 / 关系 IRI').fill('urn:ontolearn:learning:name')
    await mapping.getByRole('button', { name: '生成完整预览' }).click()
    await expect(mapping.getByText('新增 4 · 删除 0 · 修改 0 · 冲突 0')).toBeVisible()
    await mapping.getByRole('button', { name: '检查正式变更' }).click()
    await expect(mapping.getByRole('list', { name: '已核验变更明细' })).toContainText(
      'urn:ontolearn:w4:equipment/001',
    )
    await mapping.getByLabel('我已检查全部变更，确认提交到当前项目').check()
    await mapping.getByRole('button', { name: '提交映射 ChangeSet' }).click()
    await expect(page.getByTestId('selected-project-version')).toHaveText(
      '当前项目版本 ' + (baseline.domain.projectRevision + 1),
    )
    await expect(page.locator('a[href="#behavior-workspace"]')).toHaveAttribute(
      'aria-disabled',
      'false',
    )
    const mapped = await state(page)
    expect(mapped.domain.state.facts.filter(({ owner }) => owner === 'w4-desktop')).toHaveLength(4)

    await page.locator('a[href="#behavior-workspace"]').click()
    const behavior = page.locator('#behavior-workspace')
    await behavior.getByLabel('唯一行为 ID').fill('w4-notice')
    await behavior.getByLabel('行为名称').fill('隔离告警通知')
    await behavior.getByLabel('业务说明').fill('保留隔离副本差异')
    await behavior.getByLabel('触发事件类型', { exact: true }).fill('alarm')
    await behavior.getByLabel('启用此行为').check()
    await behavior.getByRole('button', { name: /添加条件/ }).click()
    await behavior.getByLabel('条件类型').selectOption('always')
    await behavior.getByRole('button', { name: /添加动作/ }).click()
    await behavior.getByLabel('动作类型').selectOption('notify')
    await behavior.getByLabel('通知内容').fill('W4 isolated notification')
    await behavior.getByLabel('预期业务效果').fill('显示隔离通知')
    await behavior.getByLabel('唯一事件 ID').fill('E-W4')
    await behavior.getByLabel('事件类型', { exact: true }).fill('alarm')
    await behavior.getByLabel('事件版本').fill('1')
    await behavior.getByRole('button', { name: '在隔离副本中测试' }).click()
    await expect(behavior.getByText('隔离副本已提交 / 当前输入', { exact: true })).toBeVisible()
    await expect(behavior.getByRole('heading', { name: '隔离副本 Diff · 新增' })).toBeVisible()
    await expect(behavior.getByText(/隔离记录 · W4 isolated notification/)).toBeVisible()
    await expect(behavior.getByText(/通知记录 · 已执行/)).toBeVisible()
    await expect(behavior.getByRole('button', { name: '请求取消测试' })).toHaveCount(0)
    await expect(behavior.getByRole('button', { name: '在隔离副本中测试' })).toBeEnabled()
    expect((await state(page)).domain.state.facts).toEqual(mapped.domain.state.facts)

    await openScenarioFromEditedBehavior(page)
    const scenario = page.locator('#scenario-workspace')
    await scenario.getByLabel('场景名称').fill('W4 容量场景')
    await scenario.getByLabel('最大轮数').fill('2')
    await scenario.getByLabel('每轮处理产能').fill('1')
    await scenario.getByLabel('规则版本').fill('w4-rules-v1')
    await scenario.getByLabel('行为版本').fill('w4-behavior-v1')
    await scenario.getByLabel('数据来源').fill('W4 固定测试输入')
    await scenario.getByLabel(/逐轮事件（列表/).fill(
      JSON.stringify([
        {
          id: 'E1',
          round: 1,
          sequence: 0,
          payload: { alarmId: 'A1', level: 'High', status: 'Open' },
        },
        { id: 'E2', round: 1, sequence: 1, payload: {} },
      ]),
    )
    await scenario.getByRole('button', { name: '从项目创建场景' }).click()
    const scenarioDetail = scenario.getByRole('region', { name: '已保存场景和隔离运行' })
    await expect(scenarioDetail.getByRole('heading', { name: 'W4 容量场景' })).toBeVisible()
    for (let count = 1; count <= 2; count++) {
      await scenarioDetail.getByRole('button', { name: '运行场景', exact: true }).click()
      await expect(
        scenarioDetail.getByRole('button', { name: /succeeded · 已提交 2 轮/ }),
      ).toHaveCount(count)
      await scenarioDetail.getByRole('button', { name: '加入运行对比' }).click()
    }
    await scenario.getByRole('button', { name: '对比所选成功运行' }).click()
    await expect(
      scenario.getByText(/期末（第 2 轮） · 积压 0 · 完成工单 2 · 未关闭高危告警 1/),
    ).toHaveCount(2)
    expect((await state(page)).domain.state.facts).toEqual(mapped.domain.state.facts)

    const check = async (taskId: string) =>
      take(
        await page.evaluate(
          ({ projectId, taskId }) =>
            window.ontolearn!.checkLearningTask({
              projectId,
              taskId,
              operationId: crypto.randomUUID(),
            }),
          { projectId: mapped.projectId, taskId },
        ),
      )
    for (const taskId of ['mapping', 'behavior', 'scenario', 'report']) {
      expect(await check(taskId)).toMatchObject({
        operationComplete: false,
        guidedStageCheckpointRef: null,
      })
    }

    await page.locator('a[href="#transfer-workspace"]').click()
    const transfer = page.locator('#transfer-workspace')
    const publication = transfer.getByRole('status', { name: '文件写入回执' })
    const choosePackage = transfer.getByRole('button', { name: '选择目标并检查项目包' })
    await choosePackage.click()
    await expect(transfer.getByText('未完成文件选择。')).toBeVisible()
    await choosePackage.click()
    await transfer.getByRole('button', { name: '确认导出项目包' }).click()
    await expect(publication).toContainText('已发布 · 持久性已确认')
    const packageBytes = await readFile(archive)
    expect(packageBytes.subarray(0, 4).toString('hex')).toBe('504b0304')
    await expect(publication).toContainText(createHash('sha256').update(packageBytes).digest('hex'))
    await transfer.getByRole('button', { name: '选择并检查待导入项目包' }).click()
    await transfer.getByRole('button', { name: '确认导入为新项目' }).click()
    const imported = transfer.getByText(/^已导入新项目 /)
    await expect(imported).toBeVisible()
    const importedId = (await imported.innerText()).replace('已导入新项目 ', '')
    expect(importedId).not.toBe(mapped.projectId)
    await transfer.getByRole('button', { name: '准备并预览 HTML 报告' }).click()
    await expect(transfer.getByRole('region', { name: 'HTML 报告纯文本预览' })).toBeVisible()
    await transfer.getByRole('button', { name: '选择目标并导出 HTML 报告' }).click()
    await expect
      .poll(async () => {
        const bytes = await readFile(report).catch(() => null)
        return bytes ? createHash('sha256').update(bytes).digest('hex') : ''
      })
      .toMatch(/^[a-f0-9]{64}$/)
    const html = await readFile(report, 'utf8')
    await expect(publication).toContainText(createHash('sha256').update(html).digest('hex'))
    expect(html).toMatch(/Content-Security-Policy.+default-src/su)
    expect(html).not.toMatch(/<script|\.ontolearn-host-selections|api[_-]?key/iu)
    expect(html).not.toContain(userData)
    expect(html).not.toContain(directory)
    expect(await check('report')).toMatchObject({
      checkStatus: 'passed',
      operationComplete: true,
      guidedStageCheckpointRef: null,
    })

    await page.locator('a[href="#scenario-workspace"]').click()
    await scenario.getByRole('button', { name: /^W4 容量场景/ }).click()
    await expect(scenarioDetail.getByRole('button', { name: /读取运行/ })).toHaveCount(2)
    await scenarioDetail.getByLabel('确认将此场景恢复到所示基准').check()
    await scenarioDetail.getByRole('button', { name: '恢复基准场景' }).click()
    await expect(scenarioDetail.getByRole('button', { name: /读取运行/ })).toHaveCount(0)
    expect((await state(page)).domain.state.facts).toEqual(mapped.domain.state.facts)

    await closeB1aApplication(app)
    app = undefined
    delete env.ONTOLEARN_E2E_W4_PICKERS
    app = await electron.launch({
      ...options,
      args: [...options.args, '--user-data-dir=' + userData],
    })
    const restarted = await visible(app)
    expect(await app.evaluate(({ app }) => app.getPath('userData'))).toBe(userData)
    expect((await reopenProject(restarted, mapped.projectId)).domain.state.facts).toEqual(
      mapped.domain.state.facts,
    )
    expect((await reopenProject(restarted, importedId)).domain.state.facts).toEqual(
      mapped.domain.state.facts,
    )
  } finally {
    if (app) await closeB1aApplication(app)
    if (userData) await rm(userData, { recursive: true, force: true })
  }
})
