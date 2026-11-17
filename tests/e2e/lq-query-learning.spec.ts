import { test, expect, _electron as electron, type Locator, type Page } from '@playwright/test'
import { mkdtemp, realpath } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

/**
 * Lq real Electron E2E: the query learning vertical (learning center → mentor
 * rail → independent G-base practice reset → real persisted Q-01/Q-02 checks on
 * the integrated query workspace → A01 fact edit through the ontology page →
 * derived stale after a further commit → restart persistence on the same
 * isolated profile). No model API; zero browser storage: every learning fact
 * flows through the Step 1 named bridge.
 */

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

function launchOptions(userDataDir: string) {
  const env = launchEnv()
  const base = {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
    acceptDownloads: true,
  }
  return { ...base, args: [...base.args, '--user-data-dir=' + userDataDir] }
}

async function launchWithProfile(userDataDir: string) {
  const application = await electron.launch(launchOptions(userDataDir))
  const actual = await application.evaluate(({ app }) => app.getPath('userData'))
  expect(actual).toBe(userDataDir)
  return application
}

function mentorPanel(page: Page): Locator {
  return page.getByTestId('mentor-panel')
}

async function activeProjectId(page: Page): Promise<string> {
  return page.evaluate(async () => {
    const active = await window.ontolearn!.getActiveProject()
    if (!active.ok || !active.data) throw new Error('No active project')
    return active.data.projectId
  })
}

async function catalogRevision(page: Page, projectId: string): Promise<number | undefined> {
  return page.evaluate(async (id) => {
    const listed = await window.ontolearn!.getProjectCatalog({ pageSize: 64, cursor: null })
    if (!listed.ok) throw new Error('Actual catalog refused: ' + listed.error.code)
    const item = listed.data.items.find((entry) => entry.projectId === id)
    return item?.domainRevision
  }, projectId)
}

async function openOntologyPanel(page: Page): Promise<Locator> {
  await page.getByRole('link', { name: '本体构建', exact: true }).click()
  const panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
  await expect(panel).toBeVisible()
  await expect(panel.getByRole('region', { name: '本体编辑表单', exact: true })).toBeVisible({
    timeout: 30000,
  })
  return panel
}

/** The real revision the ontology editor currently displays. */
async function panelRevision(panel: Locator): Promise<number> {
  const text = (await panel.locator('header p').first().textContent()) ?? ''
  const match = text.match(/项目版本 (\d+)/)
  if (!match) throw new Error('Actual ontology panel exposes no revision: ' + text)
  return Number(match[1])
}

/** Wait until the (re)activated ontology session finished its first real read. */
async function awaitPanelRevision(panel: Locator): Promise<number> {
  await expect(panel.locator('header p').first()).toHaveText(/项目版本 \d+/, { timeout: 30000 })
  return panelRevision(panel)
}

async function confirmOntologyDiffAndSettle(
  panel: Locator,
  expectedRevision: number,
): Promise<void> {
  await panel
    .getByRole('region', { name: '完整事务差异', exact: true })
    .getByRole('button', { name: '我已核对完整差异，确认提交', exact: true })
    .click()
  const receipt = panel.getByRole('region', { name: '已提交回执', exact: true })
  const pending = panel.getByRole('region', { name: '原操作状态', exact: true })
  let needsReconciliation = false
  await expect
    .poll(
      async () => {
        const snapshot = await receipt.or(pending).evaluateAll((regions) => {
          const receipts = regions.filter(
            (node) => node.getAttribute('aria-label') === '已提交回执',
          )
          const operations = regions.filter(
            (node) => node.getAttribute('aria-label') === '原操作状态',
          )
          if (receipts.length > 1 || operations.length > 1)
            throw new Error('Duplicate original commit status regions')
          return { receipt: receipts[0]?.textContent, pending: operations[0]?.textContent }
        })
        if (snapshot.receipt?.includes('提交版本 ' + expectedRevision + '。')) return 'receipt'
        if (
          snapshot.pending?.includes('状态：failed') ||
          snapshot.pending?.includes('状态：cancelled')
        ) {
          throw new Error('Ontology operation failed: ' + String(snapshot.pending))
        }
        if (snapshot.pending?.includes('succeeded')) {
          needsReconciliation = true
          return 'terminal-needs-reconciliation'
        }
        return 'waiting'
      },
      { timeout: 30000 },
    )
    .not.toBe('waiting')
  if (needsReconciliation) {
    const reconcile = pending.getByRole('button', { name: '核对原操作与提交回执', exact: true })
    await expect(reconcile).toBeEnabled({ timeout: 15000 })
    await reconcile.click()
  }
  await expect(receipt).toContainText('提交版本 ' + expectedRevision + '。', { timeout: 30000 })
  await expect(receipt).toContainText('当前已读版本 ' + expectedRevision + '。', {
    timeout: 30000,
  })
  await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled({
    timeout: 15000,
  })
  await expect(pending).toHaveCount(0)
}

async function commitManualFact(
  panel: Locator,
  subject: string,
  predicate: string,
  object: string,
): Promise<void> {
  const expectedRevision = (await awaitPanelRevision(panel)) + 1
  const facts = panel.getByRole('region', { name: '实例事实', exact: true })
  const resetFacts = facts.getByRole('button', { name: '新建事实并读取当前基准', exact: true })
  await expect(resetFacts).toBeEnabled({ timeout: 15000 })
  await resetFacts.click()
  await facts.getByLabel('主体个体 IRI', { exact: true }).fill(subject)
  await facts.getByLabel('属性 IRI', { exact: true }).fill(predicate)
  await facts.getByLabel('规范 RDF 对象', { exact: true }).fill(object)
  const previewFact = facts.getByRole('button', { name: '预览新增事实', exact: true })
  await expect(previewFact).toBeEnabled({ timeout: 15000 })
  await previewFact.click()
  await expect(panel.getByRole('region', { name: '完整事务差异', exact: true })).toBeVisible({
    timeout: 30000,
  })
  await confirmOntologyDiffAndSettle(panel, expectedRevision)
  await expect(resetFacts).toBeEnabled({ timeout: 15000 })
  await resetFacts.click()
}

/** Edit one existing fact through the real load → edit → preview → confirm path. */
async function editExistingFact(panel: Locator, rowText: string, newObject: string): Promise<void> {
  const expectedRevision = (await awaitPanelRevision(panel)) + 1
  const facts = panel.getByRole('region', { name: '实例事实', exact: true })
  await facts.getByLabel('查找事实', { exact: true }).fill(rowText)
  const row = facts.locator('tbody tr').filter({ hasText: 'urn:ontolearn:learning:status' })
  await expect(row).toHaveCount(1)
  await row.getByRole('button', { name: '载入事实', exact: true }).click()
  const object = facts.getByLabel('规范 RDF 对象', { exact: true })
  await expect(object).toHaveValue('"Open"')
  await object.fill(newObject)
  await facts.getByRole('button', { name: '预览事实修改', exact: true }).click()
  await expect(panel.getByRole('region', { name: '完整事务差异', exact: true })).toBeVisible({
    timeout: 30000,
  })
  await confirmOntologyDiffAndSettle(panel, expectedRevision)
  const resetFacts = facts.getByRole('button', { name: '新建事实并读取当前基准', exact: true })
  await expect(resetFacts).toBeEnabled({ timeout: 15000 })
  await resetFacts.click()
}

async function queryPanel(page: Page): Promise<Locator> {
  const panel = page.getByRole('region', { name: '本体查询工作台', exact: true })
  await expect(panel).toBeVisible()
  return panel
}

/**
 * Loads the managed unclosed-high definition from the already-read project and
 * executes it through the real accepted-job path, then refreshes the fixed
 * result so the result panel holds the settled real rows.
 */
async function runUnclosedHigh(page: Page): Promise<Locator> {
  const panel = await queryPanel(page)
  const notice = panel.locator('p[role="status"][aria-live="polite"]')
  await panel.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
  await expect(notice).toHaveText('项目与持久工作草稿已读回；工作草稿不代表正式查询定义。', {
    timeout: 30000,
  })
  await panel
    .getByRole('combobox', { name: '已提交查询', exact: true })
    .selectOption('unclosed-high')
  // Selecting a definition marks the editor dirty; the explicit reload consent
  // is part of the real product flow before a load can replace the draft.
  const consent = panel.getByRole('checkbox', {
    name: '我已保留当前编辑，允许重新载入或新建替换它',
    exact: true,
  })
  await expect(consent).toBeVisible()
  await consent.check()
  await panel.getByRole('button', { name: '按所选当前/历史输入载入定义', exact: true }).click()
  await expect(notice).toHaveText('已载入真实受管定义；后续编辑需先正式提交。', {
    timeout: 30000,
  })
  const task = panel.getByRole('region', { name: '真实查询或提交任务', exact: true })
  // Bind the wait to THIS run's original Job identity: the previous run's
  // terminal text must never satisfy the succeeded expectation.
  const previousJobId =
    (await task
      .locator('code')
      .first()
      .textContent()
      .catch(() => null)) ?? ''
  await panel.getByRole('button', { name: '执行已载入且未改变的受管定义', exact: true }).click()
  await expect
    .poll(
      async () => {
        const identity =
          (await task
            .locator('code')
            .first()
            .textContent()
            .catch(() => '')) ?? ''
        if (!identity || identity === previousJobId) return ''
        const text = (await task.textContent().catch(() => '')) ?? ''
        return identity !== previousJobId && text.includes('：succeeded；') ? identity : ''
      },
      { timeout: 30000 },
    )
    .not.toBe('')
  const refreshedNotice = '已取得真实结果描述；按固定引用分别读取文本与结果页。'
  const terminalNotice = '收到真实终态，请刷新并核对持久结果。'
  const refresh = panel.getByRole('button', { name: '刷新任务、原操作与固定结果', exact: true })
  for (let round = 0; round < 3; round++) {
    await expect(refresh).toBeEnabled({ timeout: 30000 })
    await refresh.click()
    await expect(notice).toHaveText(new RegExp(`${refreshedNotice}|${terminalNotice}`), {
      timeout: 30000,
    })
    if (((await notice.textContent()) ?? '') === refreshedNotice) break
  }
  await expect(notice).toHaveText(refreshedNotice, { timeout: 30000 })
  await expect(refresh).toBeEnabled({ timeout: 30000 })
  return panel
}

async function readFirstResultPage(panel: Locator): Promise<Locator> {
  const result = panel.getByRole('region', { name: '查询结果', exact: true })
  await expect(result).toBeVisible({ timeout: 30000 })
  await panel.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true }).click()
  await expect(result.getByRole('table')).toBeVisible({ timeout: 30000 })
  return result
}

function guidedStageCheckpoints(page: Page): Locator {
  return page
    .getByTestId('checkpoint-list')
    .getByTestId('checkpoint-item-summary')
    .filter({ hasText: '引导阶段完成「完成引导阶段：业务本体建模」' })
}

test('Lq query course: G-base practice reset, persisted Q-01/Q-02, derived stale and restart persistence', async () => {
  test.setTimeout(420000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  // realpath keeps macOS /var ↔ /private/var identical across both launches.
  const userData = await realpath(await mkdtemp(join(tmpdir(), 'ontolearn-lq-profile-')))
  let application: Awaited<ReturnType<typeof launchWithProfile>> | undefined =
    await launchWithProfile(userData)
  try {
    const page = await application.firstWindow()

    stage = 'project 1: start the case, add one extra fact, focus the query task'
    await page.getByTestId('learning-start-example').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
      { timeout: 30000 },
    )
    const projectOne = await activeProjectId(page)
    evidence.projectOne = projectOne
    const mentor = mentorPanel(page)
    await expect(mentor).toBeVisible({ timeout: 30000 })
    let panel = await openOntologyPanel(page)
    await commitManualFact(
      panel,
      'urn:ontolearn:learning:equipment/002',
      'urn:ontolearn:learning:assignedTo',
      '<urn:ontolearn:learning:person/L01>',
    )
    const projectOneRevision = await catalogRevision(page, projectOne)
    expect(projectOneRevision).toBe(2)
    // The learning path focuses the query task without touching any project.
    await page.locator('[data-testid="learning-path-task"][data-task-id="query"]').click()
    await expect(mentor).toContainText('任务 03 · 本体查询')
    await mentor.getByTestId('learning-reading-open').click()
    await expect(mentor.getByTestId('learning-reading-open')).toContainText('已打开阅读', {
      timeout: 30000,
    })
    const correctOptions = mentor.locator(
      '[data-testid="learning-assessment-option"][data-option-id="b"]',
    )
    await expect(correctOptions).toHaveCount(2)
    await correctOptions.first().click()
    await expect(mentor.getByTestId('learning-assessment-outcome')).toBeVisible({
      timeout: 30000,
    })
    await expect(mentor.getByTestId('learning-assessment-outcome')).toContainText('回答正确。')
    await correctOptions.nth(1).click()
    await expect(
      mentor.locator('.is-selected[data-testid="learning-assessment-option"]'),
    ).toHaveCount(2)
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('待检查')

    stage = 'independent G-base reset opens a fresh practice project on the query workspace'
    await mentor.getByTestId('learning-reset-gbase').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
      { timeout: 30000 },
    )
    const projectTwo = await activeProjectId(page)
    evidence.projectTwo = projectTwo
    expect(projectTwo).not.toBe(projectOne)
    await expect(page.getByRole('region', { name: '本体查询工作台', exact: true })).toBeVisible({
      timeout: 30000,
    })
    await expect(mentor).toContainText('任务 03 · 本体查询')
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('待检查', {
      timeout: 30000,
    })
    // Project 1 stays in the library, untouched by the practice reset.
    expect(await catalogRevision(page, projectOne)).toBe(projectOneRevision)
    evidence.projectOneRevisionAfterReset = await catalogRevision(page, projectOne)

    stage = 'practice project: mounted reading and self assessments never change the verdict'
    await mentor.getByTestId('learning-reading-open').click()
    await expect(mentor.getByTestId('learning-reading-open')).toContainText('已打开阅读', {
      timeout: 30000,
    })
    const practiceOptions = mentor.locator(
      '[data-testid="learning-assessment-option"][data-option-id="b"]',
    )
    await expect(practiceOptions).toHaveCount(2)
    await practiceOptions.first().click()
    await expect(mentor.getByTestId('learning-assessment-outcome')).toContainText('回答正确。', {
      timeout: 30000,
    })
    await practiceOptions.nth(1).click()
    await expect(
      mentor.locator('.is-selected[data-testid="learning-assessment-option"]'),
    ).toHaveCount(2)
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('待检查')

    stage = 'Q-01: run unclosed-high on the pure G-base of project 2'
    let query = await runUnclosedHigh(page)
    let result = await readFirstResultPage(query)
    await expect(result.getByRole('columnheader')).toHaveText(['alarm'])
    await expect(result.locator('tbody tr')).toHaveCount(1)
    await expect(result.locator('tbody td > span')).toHaveText(['urn:ontolearn:learning:alarm/A01'])
    await expect(result).not.toContainText('alarm/A02')
    await expect(result).not.toContainText('alarm/A03')
    evidence.q01Rows = await result.locator('tbody td > span').allTextContents()
    await expect(mentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await mentor.getByTestId('mentor-btn-check').click()
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('需要修复', {
      timeout: 30000,
    })
    await expect(mentor).toContainText('Q-01')
    await expect(mentor).toContainText('Q-02')
    await expect(mentor.getByTestId('learning-check-status')).not.toHaveText('已通过')
    evidence.q01CheckStatus = '需要修复'

    stage = 'Q-02: edit A01 to Closed through the real fact-edit flow and rerun'
    await mentor.getByTestId('learning-open-ontology-repair').click()
    panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
    await expect(panel).toBeVisible()
    await editExistingFact(panel, 'alarm/A01', '"Closed"')
    await mentor.getByTestId('learning-open-query-workspace').click()
    query = await runUnclosedHigh(page)
    result = await readFirstResultPage(query)
    await expect(result).toContainText('完整结果共 0 行')
    await expect(result.locator('tbody tr')).toHaveCount(0)
    evidence.q02RowCount = 0

    stage = 'the persisted check passes independently without any guided checkpoint'
    await expect(mentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await mentor.getByTestId('mentor-btn-check').click()
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('已通过', {
      timeout: 30000,
    })
    await expect(mentor.getByTestId('learning-assistance-label')).toHaveText('独立完成')
    await expect(mentor.getByTestId('learning-operation-state')).toContainText('操作完成：是')
    await expect(mentor.getByTestId('learning-guided-stage-badge')).toHaveCount(0)
    await expect(guidedStageCheckpoints(page)).toHaveCount(0)
    evidence.storageAfterPass = await page.evaluate(() => ({
      localStorage: window.localStorage.length,
      sessionStorage: window.sessionStorage.length,
    }))
    expect(evidence.storageAfterPass).toEqual({ localStorage: 0, sessionStorage: 0 })
    evidence.passedCheckStatus = '已通过'

    stage = 'one more committed fact flips the derived stale view without any RPC'
    await page.getByRole('link', { name: '本体构建', exact: true }).click()
    panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
    await expect(panel).toBeVisible()
    await commitManualFact(
      panel,
      'urn:ontolearn:learning:equipment/002',
      'urn:ontolearn:learning:assignedTo',
      '<urn:ontolearn:learning:person/L02>',
    )
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('已过期 / 需重跑', {
      timeout: 30000,
    })
    await expect(mentor).toContainText('输入在本检查后发生了新的提交')
    evidence.staleAfterExtraFact = true

    stage = 'restart on the same isolated profile and reopen project 2'
    await application.close()
    application = undefined
    application = await launchWithProfile(userData)
    const restarted = await application.firstWindow()
    await expect(restarted.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 30000 })
    const open = restarted.locator(
      '[data-testid="project-open"][data-project-id="' + projectTwo + '"]',
    )
    await expect(open).toBeVisible({ timeout: 30000 })
    await open.click()
    await expect(restarted.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开',
      { timeout: 30000 },
    )

    stage = 'the persisted stale verdict, assistance and observations survive the restart'
    await restarted.getByTestId('mentor-panel-toggle').click()
    const reopenedMentor = restarted.getByTestId('mentor-panel')
    await expect(reopenedMentor).toBeVisible({ timeout: 30000 })
    await restarted.locator('[data-testid="learning-path-task"][data-task-id="query"]').click()
    await expect(reopenedMentor).toContainText('任务 03 · 本体查询')
    await expect(reopenedMentor.getByTestId('learning-check-status')).toHaveText(
      '已过期 / 需重跑',
      { timeout: 30000 },
    )
    await expect(reopenedMentor.getByTestId('learning-assistance-label')).toHaveText('独立完成')
    await expect(reopenedMentor.getByTestId('learning-reading-open')).toContainText('已打开阅读')
    await expect(
      reopenedMentor.locator('.is-selected[data-testid="learning-assessment-option"]'),
    ).toHaveCount(2)
    evidence.afterRestartStorage = await restarted.evaluate(() => ({
      localStorage: window.localStorage.length,
      sessionStorage: window.sessionStorage.length,
    }))
    expect(evidence.afterRestartStorage).toEqual({ localStorage: 0, sessionStorage: 0 })
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('lq-query-learning-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application?.close()
    }
  }
})
