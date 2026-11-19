import { randomUUID } from 'node:crypto'
import { readFile, rm } from 'node:fs/promises'
import { resolve } from 'node:path'
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

const learning = 'urn:ontolearn:learning:'
const unsavedClass = learning + 'W3bUnsavedClass'

function take<T>(reply: BridgeResult<T>): T {
  if (!reply.ok) throw new Error(JSON.stringify(reply.error))
  return reply.data
}

function desktopOptions() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  for (const key of ['ELECTRON_RUN_AS_NODE', 'ELECTRON_RENDERER_URL', 'I04_TEST_FIXTURE'])
    delete env[key]
  return {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    acceptDownloads: true,
    env,
  }
}

async function visibleDesktop(application: ElectronApplication) {
  const page = await application.firstWindow()
  await expect
    .poll(() =>
      application.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0]?.isVisible()),
    )
    .toBe(true)
  await expect(page.getByTestId('project-library')).toBeVisible()
  await recordB1aApplication(application)
  return page
}

async function activeProject(page: Page) {
  const active = take(await page.evaluate(() => window.ontolearn!.getActiveProject()))
  if (!active) throw new Error('Expected an open project')
  return active
}

async function openExample(page: Page) {
  await page.getByTestId('learning-start-example').click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
    '项目已创建并打开',
  )
  return activeProject(page)
}

function openWorkspace(page: Page, name: '本体构建' | '本体查询') {
  return page.getByRole('link', { name, exact: true }).click()
}

async function downloadOntology(page: Page, name: string) {
  const panel = page.getByTestId('ontology-import-export')
  const downloading = page.waitForEvent('download')
  await panel.getByTestId('ontology-export-button').click()
  const download = await downloading
  const path = test.info().outputPath(name + '.ttl')
  await download.saveAs(path)
  const bytes = await readFile(path)
  const sum = panel.getByTestId('ontology-export-summary')
  const current = await activeProject(page)
  await expect(sum).toHaveText(
    new RegExp(
      '^[1-9][0-9]* 条三元组 · 快照 ' +
        current.inputSnapshotId +
        ' · 版本 ' +
        current.projectRevision +
        '$',
    ),
  )
  const tripleCount = Number((await sum.textContent())?.split(' ')[0])
  expect(bytes.length).toBeGreaterThan(0)
  return { bytes, tripleCount }
}

async function uploadTurtle(page: Page, name: string, data: string | Buffer) {
  await page.getByTestId('ontology-import-file').setInputFiles({
    name,
    mimeType: 'text/turtle',
    buffer: Buffer.from(data),
  })
  return page.getByTestId('ontology-import-check-result')
}

async function jobs(page: Page) {
  const listing = take(
    await page.evaluate(() =>
      window.ontolearn!.listJobs({
        filter: 'all',
        pageSize: 32,
        cursor: null,
        listSnapshotId: null,
      }),
    ),
  )
  expect(listing.nextCursor).toBeNull()
  if (!Array.isArray(listing.jobs)) throw new Error('Expected a real job list')
  return listing.jobs.map(({ jobId, capability }) => {
    if (typeof jobId !== 'string' || typeof capability !== 'string')
      throw new Error('Expected persisted Job identities')
    return { jobId, capability }
  })
}

test('W3b FR-202/203/400 · G-base 视图、已提交 Turtle 往返、模板草稿', async () => {
  const application = await launchIsolatedDesktop(desktopOptions())
  let userData: string | undefined
  try {
    userData = await application.evaluate(({ app }) => app.getPath('userData'))
    const page = await visibleDesktop(application)
    const example = await openExample(page)
    await openWorkspace(page, '本体构建')
    const ontology = page.locator('#ontology-workspace')
    const browse = ontology.getByRole('region', { name: '对象浏览' })

    await browse.getByTestId('ontology-view-table').click()
    await browse.getByLabel('查找概念').fill('Alarm')
    await browse.getByRole('button', { name: '查看 Alarm', exact: true }).click()
    const selection = browse.getByRole('article', { name: '选中对象详情' })
    await expect(selection.locator('code')).toHaveText(learning + 'Alarm')
    const sidebar = page.getByTestId('agent-panel').getByTestId('agent-sidebar')
    // The sidebar reads its selection from the real getAgentContext reply.
    await expect(sidebar).toContainText('选中对象：' + learning + 'Alarm')
    await expect(page.getByTestId('agent-panel')).toContainText('模块 ontology')

    await browse.getByTestId('ontology-view-tree').click()
    await expect(browse.getByTestId('ontology-view-tree')).toHaveAttribute('aria-pressed', 'true')
    await expect(browse.locator('.ontology-tree').getByRole('button').first()).toBeVisible()
    await browse.getByTestId('ontology-view-graph').click()
    const graph = browse.getByTestId('ontology-local-graph')
    await expect(graph.getByRole('img')).toBeVisible()
    await expect(graph.locator('svg .ontology-focus-node')).toBeVisible()
    await expect(graph.locator('svg circle').nth(1)).toBeVisible()
    await expect(graph.locator('svg g > line').first()).toBeAttached()
    await expect(graph.locator('svg g > path').first()).toBeVisible()
    await expect(graph.getByRole('list', { name: '邻近关系' })).toContainText(learning + 'Alarm')

    const io = ontology.getByTestId('ontology-import-export')
    await expect(io).toContainText('导出仅包含当前已提交态（不含未提交草稿）')
    await ontology.getByRole('button', { name: '新建概念', exact: true }).click()
    await ontology.getByLabel('稳定 IRI', { exact: true }).fill(unsavedClass)
    const identifier = ontology.getByLabel('英文标识', { exact: true })
    await identifier.fill('W3bUnsavedClass')
    await expect(identifier).toHaveValue('W3bUnsavedClass')
    const first = await downloadOntology(page, 'g-base-committed')
    expect(first.bytes.toString('utf8')).toContain('<' + learning + 'Alarm>')
    expect(first.bytes.toString('utf8')).not.toContain(unsavedClass)
    expect(await activeProject(page)).toEqual(example)

    const unsupported = await uploadTurtle(
      page,
      'unsupported.ttl',
      '@prefix owl: <http://www.w3.org/2002/07/owl#> .\n<urn:test:Class> owl:equivalentClass <urn:test:Other> .',
    )
    await expect(unsupported).toHaveAttribute('data-status', 'rejected')
    await expect(
      unsupported.getByTestId('ontology-import-rejection-UNSUPPORTED_OWL').first(),
    ).toBeVisible()
    await expect(unsupported).toContainText('原文件与当前项目保持不变')
    expect(await activeProject(page)).toEqual(example)

    const invalid = await uploadTurtle(page, 'invalid.ttl', '<urn:test:Entity> a [')
    await expect(invalid).toHaveAttribute('data-ontology-status', 'invalid')
    await expect(invalid).toContainText('文件语法或格式错误')
    await expect(invalid).toContainText('原文件与当前项目保持不变')
    expect(await activeProject(page)).toEqual(example)

    await ontology.getByRole('button', { name: '新建概念', exact: true }).click()
    await page.getByTestId('project-name').fill('W3b Turtle 往返目标')
    await page.getByTestId('project-create').click()
    await expect.poll(async () => (await activeProject(page)).projectId).not.toBe(example.projectId)
    const blank = await activeProject(page)
    expect(blank.projectRevision).toBe(0)
    await openWorkspace(page, '本体构建')

    const checked = await uploadTurtle(page, 'g-base-committed.ttl', first.bytes)
    await expect(checked).toHaveAttribute('data-status', 'ok')
    await expect(checked.getByTestId('ontology-import-summary')).toContainText(
      first.tripleCount + ' 条三元组',
    )
    await io.getByTestId('ontology-import-preview').click()
    await expect(io.getByTestId('ontology-import-diff-summary')).toContainText(
      /完整差异已核验：[1-9][0-9]* 项/,
    )
    expect(await activeProject(page)).toEqual(blank)
    const commit = io.getByTestId('ontology-import-commit')
    await expect(commit).toBeDisabled()
    await io.getByTestId('ontology-import-consent').check()
    await commit.click()
    await expect
      .poll(async () => (await activeProject(page)).projectRevision)
      .toBe(blank.projectRevision + 1)
    const imported = await activeProject(page)
    expect(imported.inputSnapshotId).not.toBe(blank.inputSnapshotId)
    const second = await downloadOntology(page, 'g-base-round-trip')
    expect(second.tripleCount).toBe(first.tripleCount)
    expect(
      second.bytes.equals(first.bytes),
      'canonical Turtle download differs after the committed round trip',
    ).toBe(true)

    await openWorkspace(page, '本体查询')
    const templates = page.getByTestId('query-template-list')
    await expect(templates).toContainText('模板依据当前已读取的本体推导')
    await expect(templates).toContainText(learning + 'Alarm')
    const beforeJobs = await jobs(page)
    await templates.getByTestId('query-template-alarm').click()
    const editor = page.getByRole('region', { name: '查询编辑' })
    await expect(editor).toContainText('来源：template')
    await expect(editor.getByLabel('名称', { exact: true })).toHaveValue('高危未闭环告警')
    await expect(editor.getByLabel('可见 SPARQL')).toHaveValue(/SELECT[\s\S]+Alarm/i)
    await expect(page.getByRole('region', { name: '本次执行结果' })).toHaveCount(0)
    // Compare persisted job identities across two list snapshots.
    expect(await jobs(page)).toEqual(beforeJobs)
    expect(await activeProject(page)).toEqual(imported)
  } finally {
    await closeB1aApplication(application)
    if (userData) await rm(userData, { recursive: true, force: true })
  }
})

async function testWindowDenials(application: ElectronApplication, page: Page, projectId: string) {
  const newWindow = application.waitForEvent('window')
  const alienId = await application.evaluate(({ BrowserWindow, app }, url) => {
    const alien = new BrowserWindow({
      show: true,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true,
        preload: app.getAppPath() + '/out/preload/index.js',
      },
    })
    void alien.loadURL(url)
    return alien.id
  }, page.url())
  try {
    const foreign = await newWindow
    await foreign.waitForFunction(() => Boolean(window.ontolearn))
    const results = await foreign.evaluate(
      async ({ projectId, operationId, ref }) => {
        const bridge = window.ontolearn
        if (!bridge) throw new Error('Expected the named preload bridge')
        return {
          'agent:context': await bridge.getAgentContext({ projectId }),
          'agent:dispatch': await bridge.dispatchAgentQuestion({
            operationId,
            question: '合成问题',
            module: 'ontology',
            mode: 'project',
            scope: 'asserted',
            selectedObjectIds: [],
          }),
          'agent:commit-draft': await bridge.commitAgentDraft({
            operationId,
            draftType: 'ontology',
            confirmation: {
              projectId,
              previewHash: ref,
              preparedPlanRef: ref,
              confirmationRef: ref,
              inputSnapshotId: ref,
              parametersHash: ref,
            },
          }),
          'agent-model:probe': await bridge.probeModelCapabilities({
            configurationId: operationId,
            scope: 'synthetic',
          }),
          'project:ontology-export': await bridge.exportProjectOntology({}),
          'project:ontology-import-check': await bridge.checkProjectOntologyImport({
            baseUri: 'urn:ontolearn:w3b:',
            turtleText: '',
            format: 'turtle',
          }),
        }
      },
      { projectId, operationId: randomUUID(), ref: 'a'.repeat(64) },
    )
    expect(Object.keys(results)).toHaveLength(6)
    for (const [channel, result] of Object.entries(results)) {
      expect(result, channel).toMatchObject({ ok: false, error: { code: 'PERMISSION_DENIED' } })
    }
  } finally {
    await application.evaluate(
      ({ BrowserWindow }, id) => BrowserWindow.fromId(id)?.destroy(),
      alienId,
    )
  }
}

test('W3b FR-900/800..806/005 and IPC isolation · 本地配置、离线助手、重启与外窗拒绝', async () => {
  const options = desktopOptions()
  let application: ElectronApplication | undefined = await launchIsolatedDesktop(options)
  let userData: string | undefined
  try {
    userData = await application.evaluate(({ app }) => app.getPath('userData'))
    const page = await visibleDesktop(application)
    const { projectId } = await openExample(page)
    const context = () =>
      page
        .evaluate((id) => window.ontolearn!.getAgentContext({ projectId: id }), projectId)
        .then(take)
    const audit = () =>
      page
        .evaluate((id) => window.ontolearn!.listAgentAudit({ projectId: id, limit: 20 }), projectId)
        .then(take)

    await page.getByRole('link', { name: '模型设置', exact: true }).click()
    const model = page.locator('#model-settings')
    const modelPanel = model.getByTestId('agent-model-panel')
    const privacy = model.getByLabel('项目模型隐私模式')
    await expect(privacy).toBeEnabled()
    await expect(privacy).toHaveValue('local')
    await model.getByText('模型接收配置与凭据', { exact: true }).click()
    await model.locator('input[name="displayName"]').fill('W3b local model')
    await model.getByLabel('HTTPS 接收地址').fill('https://w3b-fixture.invalid/v1/chat/completions')
    await model.getByLabel('模型名称', { exact: true }).fill('deepseek-v4-pro')
    await model.getByRole('button', { name: '保存配置', exact: true }).click()
    await expect
      .poll(async () => (await context()).configurations.map(({ displayName }) => displayName))
      .toEqual(['W3b local model'])
    const refreshModel = modelPanel.getByRole('button', {
      name: '读取 Agent 模型配置与能力',
      exact: true,
    })
    await refreshModel.click()
    const row = modelPanel.getByRole('listitem').filter({ hasText: 'W3b local model' })
    await expect(row).toContainText('已启用')
    await row.getByRole('button', { name: '停用此配置', exact: true }).click()
    await expect(row).toContainText('未启用')
    await row.getByRole('button', { name: '启用此配置', exact: true }).click()
    await expect(row).toContainText('已启用')
    await row.getByRole('button', { name: '运行合成探测（不代表厂商已验证）', exact: true }).click()
    await expect(modelPanel.getByTestId('agent-capability-source')).toHaveText(
      '合成探测（仅本地自测，不代表厂商已验证）',
    )
    expect(await context()).toMatchObject({
      privacy: 'local',
      modelReady: false,
      capabilities: {
        mode: 'synthetic',
        connection: 'not-run',
        structuredOutput: 'passed',
        toolRoundTrip: 'passed',
      },
    })
    expect((await audit()).items).toEqual([])
    await modelPanel
      .getByRole('button', { name: '读取最近 20 条 Agent 审计记录', exact: true })
      .click()
    await expect(modelPanel.getByTestId('agent-audit-list').locator('li')).toHaveCount(0)

    const sidebar = page.getByTestId('agent-sidebar')
    await expect(sidebar.getByRole('heading', { name: '导师模式', exact: true })).toBeVisible()
    const actionButtons = sidebar.getByTestId('agent-quick-actions').getByRole('button')
    for (const [link, module] of [
      ['本体构建', 'ontology'],
      ['本体查询', 'query'],
    ] as const) {
      await openWorkspace(page, link)
      await expect(page.getByTestId('agent-panel')).toContainText('模块 ' + module)
      await expect(actionButtons.first()).toBeVisible()
      expect(await actionButtons.count()).toBeLessThanOrEqual(4)
    }
    await expect(sidebar.getByTestId('agent-action-explain').getByRole('button')).toBeDisabled()
    const hint = sidebar.getByTestId('agent-action-hint').getByRole('button')
    await expect(hint).toBeEnabled()
    await hint.click()
    await expect(
      page.getByTestId('mentor-panel').getByTestId('mentor-revealed-hint').first(),
    ).toBeVisible()
    await expect(sidebar.getByTestId('agent-degraded')).toContainText('当前使用本地功能')

    // The renderer disables send in local mode. Exercise the real named bridge too,
    // while observing Node HTTP(S) requests initiated in the real main process.
    await application.evaluate(() => {
      const channel = process
        .getBuiltinModule('node:diagnostics_channel')!
        .channel('http.client.request.start')
      const monitor = {
        count: 0,
        onRequest: () => {
          monitor.count++
        },
      }
      channel.subscribe(monitor.onRequest)
      Object.assign(process, { w3bLocalMonitor: monitor })
    })
    const question = '完全本地模式保留这条合成问题'
    const questionBox = sidebar.getByLabel('当前问题')
    await questionBox.fill(question)
    await expect(sidebar.getByRole('button', { name: '发送问题', exact: true })).toBeDisabled()
    take(
      await page.evaluate(
        ({ operationId, question }) =>
          window.ontolearn!.dispatchAgentQuestion({
            operationId,
            question,
            module: 'query',
            mode: 'tutor',
            scope: 'asserted',
            selectedObjectIds: [],
          }),
        { operationId: randomUUID(), question },
      ),
    )
    const state = take(
      await page.evaluate((id) => window.ontolearn!.getAgentState({ projectId: id }), projectId),
    )
    expect(state).toMatchObject({
      status: 'failed',
      failureCode: 'LOCAL_ONLY',
      retainedQuestion: question,
      receipts: [],
    })
    expect(
      await application.evaluate(() => {
        const host = process as typeof process & {
          w3bLocalMonitor?: { count: number; onRequest: () => void }
        }
        const monitor = host.w3bLocalMonitor!
        process
          .getBuiltinModule('node:diagnostics_channel')!
          .channel('http.client.request.start')
          .unsubscribe(monitor.onRequest)
        delete host.w3bLocalMonitor
        return monitor.count
      }),
    ).toBe(0)
    expect((await audit()).items).toEqual([])
    await expect(questionBox).toHaveValue(question)

    await page.getByRole('link', { name: '模型设置', exact: true }).click()
    await row.getByRole('button', { name: '移除此配置', exact: true }).click()
    await expect(modelPanel.getByText('当前项目尚无 Agent 模型配置。')).toBeVisible()
    expect((await context()).configurations).toEqual([])

    const beforeMode = await activeProject(page)
    const toggle = sidebar.getByTestId('agent-mode-toggle')
    await toggle.click()
    await expect.poll(async () => (await context()).mode).toBe('project')
    expect(await activeProject(page)).toEqual(beforeMode)
    await openWorkspace(page, '本体构建')
    await expect(sidebar.getByRole('heading', { name: '项目模式', exact: true })).toBeVisible()
    await toggle.click()
    await expect.poll(async () => (await context()).mode).toBe('tutor')
    expect(await activeProject(page)).toEqual(beforeMode)
    await openWorkspace(page, '本体查询')
    await expect(sidebar.getByRole('heading', { name: '导师模式', exact: true })).toBeVisible()
    await toggle.click()
    await expect.poll(async () => (await context()).mode).toBe('project')
    expect(await activeProject(page)).toEqual(beforeMode)

    await closeB1aApplication(application)
    application = undefined
    application = await electron.launch({
      ...options,
      args: [...options.args, '--user-data-dir=' + userData],
    })
    const restarted = await visibleDesktop(application)
    expect(await application.evaluate(({ app }) => app.getPath('userData'))).toBe(userData)
    await restarted
      .locator('[data-testid="project-open"][data-project-id="' + projectId + '"]')
      .click()
    await expect(
      restarted
        .getByTestId('agent-sidebar')
        .getByRole('heading', { name: '项目模式', exact: true }),
    ).toBeVisible()
    expect(take(await restarted.evaluate(() => window.ontolearn!.getAgentContext())).mode).toBe(
      'project',
    )
    const reopened = await activeProject(restarted)
    expect(reopened).toEqual(beforeMode)
    await testWindowDenials(application, restarted, projectId)
    expect(await activeProject(restarted)).toEqual(reopened)
  } finally {
    if (application) await closeB1aApplication(application)
    if (userData) await rm(userData, { recursive: true, force: true })
  }
})
