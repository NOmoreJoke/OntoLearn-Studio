import { test, expect, _electron as electron } from '@playwright/test'
import { createHash } from 'node:crypto'
import { copyFile, mkdtemp, readFile, realpath, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import type { BridgeResult, QueryDraftDTO } from '@ontolearn/contracts'
import type { MainlineProjectReadDTO } from '../../apps/desktop/src/renderer/src/query/api002-source-types'

interface FilePin {
  path: string
  sha256: string
}
interface Fixture {
  schema: 'q3-f11-physical-fixture/v1'
  projectId: string
  definitionId: string
  draft: QueryDraftDTO
  database: FilePin
  expectedProjectRead: FilePin
  expectedRows: string[][]
  sourcePins: FilePin
  boundary: string
}
const sha256 = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex')
function data<T>(value: BridgeResult<T>): T {
  if (!value.ok)
    throw new Error(`Physical mapping consumer rejected: ${JSON.stringify(value.error)}`)
  return value.data
}

test('Q3 packaged graph consumes physically mapped facts through the real query worker', async () => {
  const fixturePath = process.env.ONTOLEARN_Q3_MAPPING_FIXTURE
  const executablePath = process.env.ONTOLEARN_PACKAGED_EXECUTABLE
  test.skip(
    !fixturePath || !executablePath,
    'Requires explicit pinned physical mapping fixture and packaged executable.',
  )
  if (!fixturePath || !executablePath || !isAbsolute(fixturePath) || !isAbsolute(executablePath))
    throw new Error('Explicit absolute fixture and packaged executable required')
  const fixtureBytes = await readFile(fixturePath)
  const fixture = JSON.parse(fixtureBytes.toString('utf8')) as Fixture
  expect(fixture.schema).toBe('q3-f11-physical-fixture/v1')
  const base = dirname(fixturePath)
  const readPinned = async (pin: FilePin) => {
    expect(pin.sha256).toMatch(/^[0-9a-f]{64}$/)
    const bytes = await readFile(resolve(base, pin.path))
    expect(sha256(bytes)).toBe(pin.sha256)
    return bytes
  }
  const database = await readPinned(fixture.database)
  const expectedRead = JSON.parse(
    (await readPinned(fixture.expectedProjectRead)).toString('utf8'),
  ) as MainlineProjectReadDTO
  const sourcePins = JSON.parse((await readPinned(fixture.sourcePins)).toString('utf8')) as unknown
  expect(expectedRead.projectId).toBe(fixture.projectId)
  const userData = await realpath(await mkdtemp(join(tmpdir(), 'ontolearn-q3-mapping-')))
  await copyFile(resolve(base, fixture.database.path), join(userData, 'engine.sqlite'))
  expect(sha256(await readFile(join(userData, 'engine.sqlite')))).toBe(sha256(database))
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  for (const key of [
    'ELECTRON_RUN_AS_NODE',
    'ELECTRON_RENDERER_URL',
    'NODE_OPTIONS',
    'I04_TEST_FIXTURE',
    'ONTOLEARN_DB_PATH',
    'ONTOLEARN_TEST_MODE',
    'ONTOLEARN_ALLOWED_PROJECTS',
  ])
    delete env[key]
  const evidence: Record<string, unknown> = {
    fixturePath,
    fixtureSha256: sha256(fixtureBytes),
    inputDatabaseSha256: sha256(database),
    sourcePins,
    boundary: fixture.boundary,
    userData,
  }
  let application: Awaited<ReturnType<typeof electron.launch>> | undefined
  try {
    application = await electron.launch({
      executablePath,
      chromiumSandbox: true,
      args: [`--user-data-dir=${userData}`],
      env,
      timeout: 30000,
    })
    const launch = await application.evaluate(({ app, BrowserWindow }) => ({
      packaged: app.isPackaged,
      appPath: app.getAppPath(),
      executable: process.execPath,
      userData: app.getPath('userData'),
      sessionData: app.getPath('sessionData'),
      argv: process.argv,
      versions: process.versions,
      preferences: BrowserWindow.getAllWindows().map((window) =>
        (
          window.webContents as unknown as {
            getLastWebPreferences(): {
              sandbox: boolean
              contextIsolation: boolean
              nodeIntegration: boolean
            }
          }
        ).getLastWebPreferences(),
      ),
    }))
    expect(launch.packaged).toBe(true)
    expect(launch.userData).toBe(userData)
    expect(launch.sessionData).toBe(userData)
    expect(await realpath(launch.executable)).toBe(await realpath(executablePath))
    expect(
      launch.argv.some((arg) => arg === '--no-sandbox' || arg.startsWith('--i04-test-fixture')),
    ).toBe(false)
    evidence.launch = launch
    evidence.executableSha256 = sha256(await readFile(executablePath))
    evidence.appAsarSha256 = sha256(await readFile(launch.appPath))
    const page = await application.firstWindow()
    const errors: string[] = []
    page.on('pageerror', (error) => errors.push(String(error)))
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await page.getByTestId('project-list-refresh').click()
    const open = page.locator(
      `[data-testid="project-open"][data-project-id="${fixture.projectId}"]`,
    )
    await expect(open).toHaveCount(1)
    await open.click()
    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    const workspace = page.getByRole('region', {
      name: '本体查询工作台',
      exact: true,
    })
    await workspace.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
    )
    const actualRead = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(actualRead).toEqual(expectedRead)
    evidence.actualRead = actualRead
    await workspace.getByLabel('项目内查询标识', { exact: true }).fill(fixture.definitionId)
    await workspace
      .getByRole('checkbox', { name: '我已保留当前编辑，允许重新载入或新建替换它', exact: true })
      .check()
    await workspace
      .getByRole('button', { name: '按所选当前/历史输入载入定义', exact: true })
      .click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '已载入真实受管定义；后续编辑需先正式提交。',
    )
    await expect(workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      fixture.draft.sparql,
    )
    await workspace
      .getByRole('button', {
        name: '执行已载入且未改变的受管定义',
        exact: true,
      })
      .click()
    const task = workspace.getByRole('region', {
      name: '真实查询或提交任务',
      exact: true,
    })
    await expect(task.locator('code')).toHaveText(/^[0-9a-f-]{36}$/)
    const jobId = await task.locator('code').textContent()
    if (!jobId) throw new Error('No actual query Job identity')
    await expect(task).toContainText('：succeeded；')
    await task.getByRole('button', { name: '刷新任务、原操作与固定结果', exact: true }).click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '已取得真实结果描述；按固定引用分别读取文本与结果页。',
    )
    await workspace.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true }).click()
    const result = workspace.getByRole('region', {
      name: '查询结果',
      exact: true,
    })
    await expect(result.getByRole('table').locator('tbody tr')).toHaveCount(
      fixture.expectedRows.length,
    )
    const job = data(await page.evaluate((id) => window.ontolearn!.getJob(id), jobId))
    expect(job).toMatchObject({
      projectId: fixture.projectId,
      capability: 'query.execute',
      state: 'succeeded',
      inputSnapshotId: expectedRead.inputSnapshotId,
      error: null,
    })
    if (!job.resultRef) throw new Error('Real worker did not retain its result')
    const descriptor = data(
      await page.evaluate(
        (resultId) => window.ontolearn!.getQueryResultDescriptor({ resultId }),
        job.resultRef.resultId,
      ),
    )
    const rows = data(
      await page.evaluate(
        (descriptorRef) =>
          window.ontolearn!.getQueryRowsPage({
            descriptorRef,
            pageSize: 200,
            cursor: null,
          }),
        descriptor.descriptorRef,
      ),
    )
    expect(rows.identity).toEqual(descriptor.identity)
    expect(descriptor.identity.inputSnapshotId).toBe(expectedRead.inputSnapshotId)
    expect(descriptor.identity.inputProjectRevision).toBe(expectedRead.domain.projectRevision)
    expect(rows.rows.map((row) => row.cells.map((cell) => cell?.n3 ?? null))).toEqual(
      fixture.expectedRows,
    )
    expect(rows.nextCursor).toBeNull()
    evidence.job = job
    evidence.descriptor = descriptor
    evidence.rows = rows
    const graph = result.getByRole('region', {
      name: '结果输入的局部关系图',
      exact: true,
    })
    const observations = []
    for (const row of rows.rows) {
      await result
        .getByRole('combobox', { name: '查看结果行', exact: true })
        .selectOption(row.rowKey)
      await expect(
        graph.getByRole('img', {
          name: '来自同快照事实记录的有向关系',
          exact: true,
        }),
      ).toBeVisible()
      await expect(graph).toContainText(expectedRead.inputSnapshotId)
      const anchors = row.cells.flatMap((cell) => (cell?.kind === 'iri' ? [cell.iri] : []))
      const relevant = expectedRead.domain.state.facts.filter(
        (fact) =>
          fact.object?.startsWith('<') &&
          fact.object.endsWith('>') &&
          (anchors.includes(fact.subject) || anchors.includes(fact.object.slice(1, -1))),
      )
      const actualEdges = await graph
        .locator('svg g[data-subject]')
        .evaluateAll((nodes) =>
          nodes.map((node) => [
            node.getAttribute('data-subject'),
            node.getAttribute('data-predicate'),
            node.getAttribute('data-object'),
          ]),
        )
      expect(actualEdges).toEqual(
        relevant.map((fact) => [fact.subject, fact.predicate, fact.object!.slice(1, -1)]),
      )
      for (const fact of relevant) {
        const support = graph.locator(`[data-fact-id="${fact.id}"]`)
        await expect(support).toHaveCount(1)
        expect(fact.owner).not.toBeNull()
        await expect(support).toContainText(fact.owner!)
        await expect(support).toContainText(fact.source_row!)
        expect(fact.managed_value).toBe(fact.object)
        const state = expectedRead.domain.state.mappingState[fact.owner!]
        expect(state).toBeDefined()
        await expect(support).toContainText(`映射生成版本 ${state.generatedVersion}`)
        await expect(support).toContainText('未标记过期')
      }
      observations.push({
        rowKey: row.rowKey,
        anchors,
        actualEdges,
        supportFactIds: relevant.map((fact) => fact.id),
      })
    }
    evidence.graphObservations = observations
    const runtime = await page.evaluate(() => ({
      node: typeof (globalThis as { require?: unknown }).require,
      bridge: typeof window.ontolearn,
    }))
    expect(runtime).toEqual({ node: 'undefined', bridge: 'object' })
    const preferences = await application.evaluate(({ BrowserWindow }) =>
      BrowserWindow.getAllWindows().map((window) =>
        (
          window.webContents as unknown as {
            getLastWebPreferences(): {
              sandbox: boolean
              contextIsolation: boolean
              nodeIntegration: boolean
            }
          }
        ).getLastWebPreferences(),
      ),
    )
    expect(preferences.length).toBeGreaterThan(0)
    for (const preference of preferences)
      expect(preference).toMatchObject({
        sandbox: true,
        contextIsolation: true,
        nodeIntegration: false,
      })
    evidence.preferences = preferences
    expect(errors).toEqual([])
    evidence.pageErrors = errors
    await page.screenshot({
      path: test.info().outputPath('q3-physical-mapping-packaged.png'),
      fullPage: true,
    })
  } finally {
    try {
      await test.info().attach('q3-physical-mapping-evidence', {
        body: JSON.stringify(evidence, null, 2),
        contentType: 'application/json',
      })
    } finally {
      try {
        await application?.close()
      } finally {
        await rm(userData, { recursive: true, force: true })
      }
    }
  }
})
