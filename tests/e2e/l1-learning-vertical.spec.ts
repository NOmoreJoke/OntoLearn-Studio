import { test, expect, _electron as electron, type Locator, type Page } from '@playwright/test'
import { resolve } from 'node:path'
import { launchIsolatedDesktop } from './isolated-desktop'

/**
 * L1 Step 2 real Electron E2E: the offline first-lesson vertical (learning
 * center → mentor panel → real ChangeSet mistakes and repairs → persisted
 * ontology-model check → FR-004 guided-stage checkpoint → derived stale), and
 * the level-4 full demonstration with restart persistence. No model API, no
 * browser storage: every learning fact flows through the Step 1 named bridge.
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
  return userDataDir ? { ...base, args: [...base.args, '--user-data-dir=' + userDataDir] } : base
}

async function launchWithProfile(userDataDir?: string) {
  if (!userDataDir) return launchIsolatedDesktop(launchOptions())
  const application = await electron.launch(launchOptions(userDataDir))
  const actual = await application.evaluate(({ app }) => app.getPath('userData'))
  expect(actual).toBe(userDataDir)
  return application
}

function mentorPanel(page: Page): Locator {
  return page.getByTestId('mentor-panel')
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

type EntityKind = 'class' | 'objectProperty' | 'dataProperty' | 'individual'

/** One definition through the real form → preview → full-diff → confirm path. */
async function commitEntity(
  panel: Locator,
  options: {
    kind: EntityKind
    iri: string
    identifier: string
    label?: string
    classType?: 'owl' | 'rdfs'
    types?: string[]
  },
): Promise<void> {
  const expectedRevision = (await panelRevision(panel)) + 1
  await panel.getByRole('button', { name: '新建概念', exact: true }).click()
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  // The selects sit inside wrapping labels, so their accessible label text also
  // contains the option texts; substring matching stays unambiguous here.
  await form.getByLabel('类型').selectOption(options.kind)
  if (options.kind === 'class')
    await form.getByLabel('类声明').selectOption(options.classType ?? 'owl')
  await form.getByLabel('稳定 IRI', { exact: true }).fill(options.iri)
  await form.getByLabel('英文标识', { exact: true }).fill(options.identifier)
  if (options.label) {
    const group = form.getByRole('group', { name: '名称（保留所有语言）', exact: true })
    await group.getByRole('button', { name: '添加名称', exact: true }).click()
    await group.getByRole('textbox', { name: '名称 1', exact: true }).fill(options.label)
    await group.getByLabel('语言标签 1', { exact: true }).fill('zh')
  }
  if (options.types?.length) await form.getByLabel('所属类 IRI').fill(options.types.join('\n'))
  await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
  const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
  await expect(diff).toBeVisible({ timeout: 30000 })
  await confirmOntologyDiffAndSettle(panel, expectedRevision)
}

/** Delete one entity through the real deletion-impact → preview → confirm path. */
async function deleteEntity(
  panel: Locator,
  options: { identifier: string; iri: string },
): Promise<void> {
  const expectedRevision = (await panelRevision(panel)) + 1
  await panel.getByLabel('查找概念', { exact: true }).fill(options.identifier)
  await panel.getByRole('button', { name: '查看 ' + options.identifier, exact: true }).click()
  const detail = panel.getByRole('article', { name: '选中对象详情' })
  await expect(detail.locator('code')).toHaveText(options.iri)
  await detail.getByRole('button', { name: '查看删除影响', exact: true }).click()
  await expect(
    detail.getByRole('button', { name: '预览删除（尚不提交）', exact: true }),
  ).toBeEnabled({ timeout: 15000 })
  await detail.getByRole('button', { name: '预览删除（尚不提交）', exact: true }).click()
  const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
  await expect(diff).toBeVisible({ timeout: 30000 })
  await confirmOntologyDiffAndSettle(panel, expectedRevision)
}

async function commitManualFact(
  panel: Locator,
  subject: string,
  predicate: string,
  object: string,
): Promise<void> {
  const expectedRevision = (await panelRevision(panel)) + 1
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

async function startLearningExample(page: Page): Promise<void> {
  await page.getByTestId('learning-start-example').click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
    '项目已创建并打开',
    { timeout: 30000 },
  )
  const mentor = mentorPanel(page)
  await expect(mentor).toBeVisible({ timeout: 30000 })
  await expect(mentor.getByTestId('learning-check-status')).toHaveText('待检查', {
    timeout: 30000,
  })
}

function guidedStageCheckpoints(page: Page): Locator {
  return page
    .getByTestId('checkpoint-list')
    .getByTestId('checkpoint-item-summary')
    .filter({ hasText: '引导阶段完成「完成引导阶段：业务本体建模」' })
}

/** The closed-whitelist correct model: G-base plus exactly the L02 additions. */
async function commitCorrectModel(page: Page, panel: Locator): Promise<void> {
  await commitEntity(panel, {
    kind: 'class',
    classType: 'owl',
    iri: 'urn:ontolearn:learning:Person',
    identifier: 'Person',
    label: '人员',
  })
  await commitEntity(panel, {
    kind: 'objectProperty',
    iri: 'urn:ontolearn:learning:assignedTo',
    identifier: 'assignedTo',
  })
  await commitEntity(panel, {
    kind: 'individual',
    iri: 'urn:ontolearn:learning:person/L01',
    identifier: 'L01',
    label: '巡检员 L01',
    types: ['urn:ontolearn:learning:Person'],
  })
  await commitManualFact(
    panel,
    'urn:ontolearn:learning:equipment/001',
    'urn:ontolearn:learning:assignedTo',
    '<urn:ontolearn:learning:person/L01>',
  )
}

test('L1 offline first lesson: reading isolation, glossary, wrong class, closed-whitelist repair and the single guided-stage checkpoint', async () => {
  test.setTimeout(360000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  const application = await launchIsolatedDesktop(launchOptions())
  try {
    const page = await application.firstWindow()

    stage = 'open the learning center and start the equipment case'
    await expect(page.getByTestId('learning-center')).toBeVisible()
    await page.getByTestId('nav-learning-center').click()
    await expect(page.getByTestId('learning-center')).toBeInViewport()
    await expect(page.getByTestId('learning-center')).toContainText('离线课程 · 无需模型 API')
    await expect(page.getByTestId('learning-center')).toContainText('设备运维')
    await expect(page.getByTestId('learning-path-task')).toHaveCount(9)
    await startLearningExample(page)
    evidence.projectId = await page.evaluate(async () => {
      const active = await window.ontolearn!.getActiveProject()
      if (!active.ok || !active.data) throw new Error('No active project after learning start')
      return active.data.projectId
    })

    stage = 'mounted reading and self assessment never change the completion verdict'
    const mentor = mentorPanel(page)
    await expect(mentor).toContainText('任务 01 · 本体构建')
    await mentor.getByTestId('learning-reading-open').click()
    await expect(mentor.getByTestId('learning-reading-open')).toContainText('已打开阅读', {
      timeout: 30000,
    })
    await expect(mentor).toContainText('来源：')
    await mentor.getByTestId('learning-assessment-option').first().click()
    await expect(mentor.getByTestId('learning-assessment-outcome')).toBeVisible({
      timeout: 30000,
    })
    await expect(mentor.getByTestId('learning-assessment-outcome')).toContainText(
      /回答(正确|不正确)。/,
    )
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('待检查')
    evidence.readingIsolatedFromCompletion = true

    stage = 'the glossary reaches the IRI card through aliases and boundaries'
    await mentor.getByTestId('mentor-glossary-search').fill('主键')
    const iriEntry = mentor
      .getByTestId('mentor-glossary-entry')
      .filter({ hasText: 'IRI / 稳定身份' })
    await expect(iriEntry).toBeVisible()
    await expect(iriEntry).toContainText('Palantir 主键 ≠ 本软件 IRI')
    await expect(iriEntry).toContainText('PK')
    await mentor.getByTestId('mentor-glossary-search').fill('Primary Key')
    await expect(iriEntry).toBeVisible()
    await mentor.getByTestId('mentor-glossary-search').fill('PK')
    await expect(iriEntry).toBeVisible()

    stage = 'commit the wrong person/L01 class through the real ChangeSet flow'
    let panel = await openOntologyPanel(page)
    evidence.revisionBeforeMistake = await panelRevision(panel)
    await commitEntity(panel, {
      kind: 'class',
      classType: 'owl',
      iri: 'urn:ontolearn:learning:person/L01',
      identifier: 'L01',
      label: '误建为类的人员',
    })

    stage = 'the persisted check reports the person-as-class deviation without a checkpoint'
    await expect(mentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await mentor.getByTestId('mentor-btn-check').click()
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('需要修复', {
      timeout: 30000,
    })
    await expect(mentor).toContainText('具体人员建成了类', { timeout: 30000 })
    await expect(
      page.getByTestId('checkpoint-item-summary').filter({ hasText: '引导阶段完成' }),
    ).toHaveCount(0)
    await mentor.getByTestId('mentor-btn-explain').click()
    const explanation = mentor.getByTestId('mentor-explanation')
    await expect(explanation).toBeVisible()
    await expect(explanation).toContainText('具体人员建成了类')
    await expect(explanation).toContainText('把类当个体')
    await expect(mentor.getByTestId('learning-assistance-label')).toHaveCount(0)

    stage = 'repair through a real deletion ChangeSet plus the closed-whitelist model'
    await mentor.getByTestId('learning-open-ontology-repair').click()
    await expect(page.getByRole('region', { name: '本体项目编辑', exact: true })).toBeVisible()
    panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
    await deleteEntity(panel, {
      identifier: 'L01',
      iri: 'urn:ontolearn:learning:person/L01',
    })
    await commitCorrectModel(page, panel)

    stage = 'the persisted check passes independently and creates exactly one checkpoint'
    await expect(mentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await mentor.getByTestId('mentor-btn-check').click()
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('已通过', {
      timeout: 30000,
    })
    await expect(mentor.getByTestId('learning-assistance-label')).toHaveText('独立完成')
    await expect(mentor.getByTestId('learning-operation-state')).toContainText('操作完成：是')
    await expect(mentor.getByTestId('learning-guided-stage-badge')).toBeVisible()
    const guided = guidedStageCheckpoints(page)
    await expect(guided).toHaveCount(1, { timeout: 30000 })
    await expect(guided.first()).toContainText('引导阶段完成「完成引导阶段：业务本体建模」')
    evidence.passedCheckpoint = await guided.first().textContent()

    stage = 'a second check never duplicates the guided-stage checkpoint'
    await mentor.getByTestId('mentor-btn-check').click()
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('已通过', {
      timeout: 30000,
    })
    await expect(guided).toHaveCount(1)

    stage = 'one more committed fact flips the derived stale view without any RPC'
    await commitManualFact(
      panel,
      'urn:ontolearn:learning:equipment/002',
      'urn:ontolearn:learning:assignedTo',
      '<urn:ontolearn:learning:person/L01>',
    )
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('已过期 / 需重跑', {
      timeout: 30000,
    })
    await expect(mentor).toContainText('输入在本检查后发生了新的提交')
    evidence.staleAfterExtraFact = true
    evidence.storageUsed = await page.evaluate(() => ({
      localStorage: window.localStorage.length,
      sessionStorage: window.sessionStorage.length,
    }))
    expect(evidence.storageUsed).toEqual({ localStorage: 0, sessionStorage: 0 })
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('l1-learning-vertical-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application.close()
    }
  }
})

test('L1 level-4 full demonstration persists across a real restart without browser storage', async () => {
  test.setTimeout(360000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  let application: Awaited<ReturnType<typeof launchIsolatedDesktop>> | undefined =
    await launchIsolatedDesktop(launchOptions())
  try {
    const page = await application.firstWindow()

    stage = 'start the example and unlock the level-4 demonstration'
    await startLearningExample(page)
    const mentor = mentorPanel(page)
    await expect(mentor.getByTestId('mentor-revealed-hint')).toHaveCount(0)
    await mentor.getByTestId('mentor-btn-demo').click()
    await expect(mentor.getByTestId('mentor-revealed-hint')).toHaveCount(4, { timeout: 30000 })
    const demonstration = mentor.locator('[data-testid="mentor-revealed-hint"][data-level="4"]')
    await expect(demonstration).toBeVisible()
    await expect(demonstration).toContainText('完整示范')
    await expect(mentor.getByTestId('learning-assistance-label')).toHaveText('使用完整示范完成')
    evidence.assistanceAfterDemonstration = '使用完整示范完成'

    stage = 'the correct model still passes, attributed to the full demonstration'
    const panel = await openOntologyPanel(page)
    await commitCorrectModel(page, panel)
    await expect(mentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await mentor.getByTestId('mentor-btn-check').click()
    await expect(mentor.getByTestId('learning-check-status')).toHaveText('已通过', {
      timeout: 30000,
    })
    await expect(mentor.getByTestId('learning-assistance-label')).toHaveText('使用完整示范完成')
    evidence.projectId = await page.evaluate(async () => {
      const active = await window.ontolearn!.getActiveProject()
      if (!active.ok || !active.data) throw new Error('No active project')
      return active.data.projectId
    })

    stage = 'restart on the same isolated profile and reopen the project'
    const userData = await application.evaluate(({ app }) => app.getPath('userData'))
    await application.close()
    application = undefined
    application = await launchWithProfile(userData)
    const restarted = await application.firstWindow()
    await expect(restarted.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 30000 })
    const open = restarted.locator(
      '[data-testid="project-open"][data-project-id="' + evidence.projectId + '"]',
    )
    await expect(open).toBeVisible({ timeout: 30000 })
    await open.click()
    await expect(restarted.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开',
      { timeout: 30000 },
    )

    stage = 'the persisted level-4 demonstration and attribution survive the restart'
    // The mentor rail starts collapsed on a fresh launch; expand it like a user.
    await restarted.getByTestId('mentor-panel-toggle').click()
    const reopenedMentor = restarted.getByTestId('mentor-panel')
    await expect(reopenedMentor).toBeVisible({ timeout: 30000 })
    await expect(
      restarted.locator('[data-testid="mentor-revealed-hint"][data-level="4"]'),
    ).toBeVisible({ timeout: 30000 })
    await expect(reopenedMentor.getByTestId('mentor-revealed-hint')).toHaveCount(4)
    await expect(reopenedMentor.getByTestId('learning-check-status')).toHaveText('已通过', {
      timeout: 30000,
    })
    await expect(reopenedMentor.getByTestId('learning-assistance-label')).toHaveText(
      '使用完整示范完成',
    )

    stage = 'restarting the task keeps the full-demonstration floor and single guided checkpoint'
    await reopenedMentor.getByRole('button', { name: '重新开始本任务尝试', exact: true }).click()
    await expect(reopenedMentor.getByTestId('learning-check-status')).toHaveText('待检查', {
      timeout: 30000,
    })
    await expect(reopenedMentor.getByTestId('learning-assistance-label')).toHaveText(
      '使用完整示范完成',
    )
    await expect(reopenedMentor.getByTestId('mentor-revealed-hint')).toHaveCount(4)
    await expect(reopenedMentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await reopenedMentor.getByTestId('mentor-btn-check').click()
    await expect(reopenedMentor.getByTestId('learning-check-status')).toHaveText('已通过', {
      timeout: 30000,
    })
    await expect(reopenedMentor.getByTestId('learning-assistance-label')).toHaveText(
      '使用完整示范完成',
    )
    await expect(reopenedMentor.getByTestId('mentor-btn-check')).toBeEnabled({ timeout: 30000 })
    await expect(guidedStageCheckpoints(restarted)).toHaveCount(1, { timeout: 30000 })
    const checkpointList = await restarted.evaluate(async () =>
      window.ontolearn!.listProjectCheckpoints({ pageSize: 20, cursor: null }),
    )
    expect(checkpointList.ok).toBe(true)
    if (checkpointList.ok) {
      expect(
        checkpointList.data.items.filter((item) => item.reason === 'guided-stage'),
      ).toHaveLength(1)
    }

    evidence.afterRestartStorage = await restarted.evaluate(() => ({
      localStorage: window.localStorage.length,
      sessionStorage: window.sessionStorage.length,
    }))
    expect(evidence.afterRestartStorage).toEqual({ localStorage: 0, sessionStorage: 0 })
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('l1-level4-restart-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application?.close()
    }
  }
})
