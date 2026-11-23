import { test, expect, _electron as electron, type Locator, type Page } from '@playwright/test'
import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
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

/**
 * Clicks the fixed-result refresh and waits until the whole refresh round-trip
 * settles, so a later descriptor read can never race the in-flight refresh.
 */
async function refreshQueryResultAndSettle(
  panel: Locator,
  expectedResultText: string,
): Promise<void> {
  const refresh = panel.getByRole('button', {
    name: '刷新任务、原操作与固定结果',
    exact: true,
  })
  await expect(refresh).toBeEnabled({ timeout: 30000 })
  await refresh.click()
  await expect(panel.locator('p[role="status"][aria-live="polite"]')).toHaveText(
    '已取得真实结果描述；按固定引用分别读取文本与结果页。',
    { timeout: 30000 },
  )
  await expect(refresh).toBeEnabled({ timeout: 30000 })
  const resultPanel = panel.getByRole('region', { name: '查询结果', exact: true })
  await expect(resultPanel).toBeVisible({ timeout: 30000 })
  await expect(resultPanel).toContainText(expectedResultText, { timeout: 30000 })
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

/**
 * Confirms the real ontology diff and settles the receipt / original-operation
 * pair until the receipt reports the exact committed revision.
 */
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
        if (snapshot.receipt?.includes(`提交版本 ${expectedRevision}。`)) return 'receipt'
        if (
          snapshot.pending?.includes('状态：failed') ||
          snapshot.pending?.includes('状态：cancelled')
        ) {
          throw new Error(`Ontology operation failed: ${snapshot.pending}`)
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
  await expect(receipt).toContainText(`提交版本 ${expectedRevision}。`, { timeout: 30000 })
  await expect(receipt).toContainText(`当前已读版本 ${expectedRevision}。`, { timeout: 30000 })
  await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled({
    timeout: 15000,
  })
  await expect(pending).toHaveCount(0)
}

/** Submits one ontology definition through the real preview → confirm path. */
async function commitDefinition(
  panel: Locator,
  identifier: string,
  label: string,
  expectedRevision: number,
  iri: string = `urn:ontolearn:learning:${identifier}`,
): Promise<void> {
  await panel.getByRole('button', { name: '新建概念', exact: true }).click()
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  // 稳定 IRI 是必填项；缺失时浏览器会拒绝提交，预览定义修改不会产生完整事务差异。
  await form.getByLabel('稳定 IRI', { exact: true }).fill(iri)
  await form.getByLabel('英文标识', { exact: true }).fill(identifier)
  const group = form.getByRole('group', { name: '名称（保留所有语言）', exact: true })
  await group.getByRole('button', { name: '添加名称', exact: true }).click()
  await group.getByRole('textbox', { name: '名称 1', exact: true }).fill(label)
  await group.getByLabel('语言标签 1', { exact: true }).fill('zh')
  await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
  const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
  await expect(diff).toBeVisible({ timeout: 30000 })
  await confirmOntologyDiffAndSettle(panel, expectedRevision)
}

/** Submits one asserted manual fact through the real preview → confirm path. */
async function commitManualFact(
  panel: Locator,
  subject: string,
  predicate: string,
  object: string,
  expectedRevision: number,
): Promise<void> {
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

/** The original Job identity rendered by the real task region. */
const jobIdPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/

async function originalJobId(task: Locator): Promise<string> {
  const identity = task.locator('code').first()
  await expect(identity).toHaveText(jobIdPattern)
  const value = await identity.textContent()
  if (!value || !jobIdPattern.test(value))
    throw new Error('Actual task region exposes no original Job')
  return value
}

/**
 * The real resultId of the latest succeeded query execution. The result identity
 * comes from the durable job list, never from a guessed or empty identifier.
 */
async function latestQueryResultId(page: Page): Promise<string> {
  return page.evaluate(async () => {
    const listed = await window.ontolearn!.listJobs({
      filter: 'all',
      pageSize: 100,
      listSnapshotId: null,
      cursor: null,
    })
    if (!listed.ok) throw new Error(`Actual job list refused: ${listed.error.code}`)
    const jobs = (listed.data as unknown as { jobs?: Array<Record<string, unknown>> }).jobs ?? []
    const executions = jobs.filter(
      (job) => job.capability === 'query.execute' && job.state === 'succeeded',
    )
    const latest = executions.at(-1)
    const resultRef = latest?.resultRef as { resultId?: string } | null | undefined
    if (!resultRef?.resultId) throw new Error('Actual query job exposes no result reference')
    return resultRef.resultId
  })
}

/** The real descriptor of one fixed query result. */
async function queryDescriptor(page: Page, resultId: string) {
  return data(
    await page.evaluate(
      (id) => window.ontolearn!.getQueryResultDescriptor({ resultId: id }),
      resultId,
    ),
  )
}

/**
 * The original operation identity recorded by the real receipt region. The
 * receipt renders "操作 <operationId>，提交版本 <revision>。"; the identity is
 * read from that text, never from a fabricated value.
 */
async function receiptOperation(receipt: Locator): Promise<string> {
  const text = await receipt.locator('p').first().textContent()
  const match = /操作\s*([^\s，,]+)/.exec(text ?? '')
  if (!match) throw new Error('Actual receipt exposes no original operation')
  return match[1]!
}

test('B1b whole-project restore rolls back mixed impacts and survives a real restart', async () => {
  test.setTimeout(240000)
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
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 15000 })
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
    await commitDefinition(panel, 'b1b-equipment', '设备', 1, 'urn:ontolearn:learning:Equipment')

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
      .getByRole('textbox', { name: '说明', exact: true })
      .fill('B1b 检查点恢复与失效验证查询')
    await panel
      .getByRole('textbox', { name: '关联能力问题', exact: true })
      .fill('哪些设备已被录入？')
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
    const task = panel.getByRole('region', { name: '真实查询或提交任务', exact: true })
    await expect(task).toContainText('：succeeded；', { timeout: 60000 })
    // The committed definition only becomes executable after the original task
    // and its operation have been reconciled by one explicit refresh.
    const refreshTask = task.getByRole('button', {
      name: '刷新任务、原操作与固定结果',
      exact: true,
    })
    await expect(refreshTask).toBeEnabled({ timeout: 30000 })
    await refreshTask.click()
    await expect(panel.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '真实提交终态、原operation、历史与当前定义均已核对；可执行受管查询。',
      { timeout: 30000 },
    )
    const execute = panel.getByRole('button', {
      name: '执行已载入且未改变的受管定义',
      exact: true,
    })
    await expect(execute).toBeEnabled({ timeout: 30000 })
    const commitJobId = await originalJobId(task)
    await execute.click()
    // The query execution replaces the commit Job inside the very same region.
    await expect(task.locator('code').first()).not.toHaveText(commitJobId, { timeout: 60000 })
    await expect(task).toContainText('：succeeded；', { timeout: 60000 })
    const executeJobId = await originalJobId(task)
    expect(executeJobId).not.toBe(commitJobId)
    evidence.commitJobId = commitJobId
    evidence.executeJobId = executeJobId
    await refreshQueryResultAndSettle(panel, '当前结果')

    stage = 'read the real result identity of the executed query'
    const resultId = await latestQueryResultId(page)
    evidence.resultId = resultId
    const currentDescriptor = await queryDescriptor(page, resultId)
    expect(currentDescriptor.metadata.state).toBe('current')
    const originalInputSnapshotId = currentDescriptor.identity.inputSnapshotId
    expect(originalInputSnapshotId).toBeTruthy()
    evidence.originalInputSnapshotId = originalInputSnapshotId

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

    stage = 'modify and persist one query draft so no unsaved form remains'
    const sparql = panel.getByRole('textbox', { name: '可见 SPARQL', exact: true })
    await expect(sparql).toBeVisible()
    await sparql.fill(`${await sparql.inputValue()}\n# B1b 恢复前草稿修改`)
    await panel.getByRole('button', { name: '保存工作草稿（不提交正式定义）', exact: true }).click()
    await expect(panel.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '工作草稿已持久化；正式定义尚未提交。',
    )

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

    stage = 'the metadata and draft changes did not invalidate the executed result'
    // Re-read the fixed result instead of trusting a previous render, so the
    // panel text and the descriptor always describe the same real read.
    await refreshQueryResultAndSettle(panel, '当前结果')
    const afterMetadataDescriptor = await queryDescriptor(page, resultId)
    expect(afterMetadataDescriptor.metadata.state).toBe('current')
    expect(afterMetadataDescriptor.identity.inputSnapshotId).toBe(originalInputSnapshotId)
    expect(afterMetadataDescriptor.metadata.staleReason).toHaveLength(0)

    stage = 'commit a second domain change so the executed result becomes stale'
    const ontology = await ontologyPanel(page)
    await commitManualFact(
      ontology,
      'urn:ontolearn:learning:eq-1',
      'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
      '<urn:ontolearn:learning:Equipment>',
      3,
    )

    stage = 'the fixed result is now stale while the history keeps its original input'
    panel = await queryPanel(page)
    // Switching back to the query workbench keeps the original execute Job, so
    // the fixed result can be refreshed and read as the very same execution.
    const staleTask = panel.getByRole('region', { name: '真实查询或提交任务', exact: true })
    await expect(staleTask.locator('code').first()).toHaveText(executeJobId, { timeout: 30000 })
    await refreshQueryResultAndSettle(panel, '已过期，请明确选择输入后重新执行')
    const staleDescriptor = await queryDescriptor(page, resultId)
    expect(staleDescriptor.metadata.state).toBe('stale')
    expect(staleDescriptor.metadata.staleReason.length).toBeGreaterThan(0)
    expect(
      staleDescriptor.metadata.staleReason.some((reason) => reason.code === 'FACTS_CHANGED'),
    ).toBe(true)
    expect(staleDescriptor.identity.inputSnapshotId).toBe(originalInputSnapshotId)
    evidence.staleReason = staleDescriptor.metadata.staleReason

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
    // The engine's authoritative change identities: a domain write, a metadata
    // edit, a durable draft save and a manual checkpoint creation.
    await expect(operations).toContainText('domain')
    await expect(operations).toContainText('metadata')
    await expect(operations).toContainText('draft.save')
    await expect(operations).toContainText('checkpoint.create')
    await expect(preview).toContainText('覆盖范围')
    await expect(preview).toContainText('保留不变')

    stage = 'no unsaved draft or dirty form blocks the destructive restore'
    // The destructive path is only reachable when no workspace edit is pending.
    await expect(preview.getByTestId('restore-destructive-blocked')).toHaveCount(0)
    await expect(preview.getByTestId('restore-confirm')).toBeEnabled()

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
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开 · 版本 4',
      { timeout: 60000 },
    )
    await expect(page.getByTestId('selected-project-version')).toContainText('当前项目版本 4', {
      timeout: 60000,
    })
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 30000 })

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
    expect(restored.domain.projectRevision).toBe(4)
    expect(restored.domain.state.definitions).toHaveLength(0)
    expect(restored.domain.state.facts).toHaveLength(0)
    await expect(page.getByTestId('selected-project-version')).toContainText(
      `当前项目版本 ${restored.domain.projectRevision}`,
    )

    stage = 'the restored project never revives the newer high-version result'
    const restoredDescriptor = await queryDescriptor(page, resultId)
    expect(restoredDescriptor.metadata.state).toBe('stale')
    expect(restoredDescriptor.identity.inputSnapshotId).toBe(originalInputSnapshotId)
    evidence.restoredResultState = restoredDescriptor.metadata.state

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

    stage = 'inject a crashed pending restore intent before the restart'
    // Simulate the crash window after ProjectRestoreSession.apply durably wrote
    // the pending intent but before the engine reply arrived: rewrite the last
    // journal record back to pending/undelivered directly on disk.
    const intentsDir = join(launch.userData, 'project-restore-intents')
    const journalFile = readdirSync(intentsDir)
      .filter((name) => name.endsWith('.json'))
      .map((name) => join(intentsDir, name))
      .find(
        (path) =>
          (JSON.parse(readFileSync(path, 'utf8')) as { records?: unknown[] }).records!.length > 0,
      )
    if (!journalFile) throw new Error('restore journal with records not found')
    const journal = JSON.parse(readFileSync(journalFile, 'utf8')) as {
      records: Array<Record<string, unknown>>
    }
    const lastIndex = journal.records.length - 1
    journal.records[lastIndex] = {
      ...journal.records[lastIndex]!,
      outcome: 'pending',
      delivered: false,
      result: null,
    }
    writeFileSync(journalFile, JSON.stringify(journal), 'utf8')
    evidence.injectedIntent = journal.records[lastIndex]

    application = await launchWithProfile(launch.userData)
    const restarted = await application.firstWindow()
    // No project is open after the crash restart, yet the recovery panel must
    // still be reachable and the pending intent keeps the library fenced.
    await expect(restarted.getByTestId('checkpoint-no-project')).toBeVisible({ timeout: 30000 })
    await expect(checkpoints(restarted).getByTestId('restore-recovery')).toBeVisible({
      timeout: 30000,
    })
    await expect(restarted.getByTestId('project-list-refresh')).toBeDisabled({ timeout: 30000 })
    // Unselected crash reconciliation runs through the reconcile control.
    stage = 'reconcile the unselected crashed restore intent'
    await checkpoints(restarted).getByTestId('restore-reconcile').click()
    await expect(checkpoints(restarted).getByTestId('restore-recovery')).toHaveCount(0, {
      timeout: 30000,
    })
    await expect(restarted.getByTestId('project-list-refresh')).toBeEnabled({ timeout: 30000 })
    // The applied handler reopens the restored project through the real open path.
    await expect(restarted.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开 · 版本 4',
      { timeout: 30000 },
    )
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
  test.setTimeout(240000)
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

    stage = 'commit one definition and undo it cleanly'
    const panel = await ontologyPanel(page)
    await commitDefinition(panel, 'b1b-undo-clean', '干净撤销定义', 1)
    const cleanReceipt = panel.getByRole('region', { name: '已提交回执', exact: true })
    await expect(cleanReceipt).toBeVisible({ timeout: 30000 })
    const cleanOperation = await receiptOperation(cleanReceipt)
    evidence.cleanOperation = cleanOperation

    await cleanReceipt.getByRole('button', { name: '预览撤销本次修改', exact: true }).click()
    const cleanDiff = panel.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(cleanDiff).toBeVisible({ timeout: 30000 })
    await expect(cleanDiff).toContainText('完整事务差异 · 尚未提交')
    await expect(cleanDiff).not.toContainText('撤销冲突影响')
    await confirmOntologyDiffAndSettle(panel, 2)
    const afterCleanUndo = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
    )
    expect(afterCleanUndo.domain.projectRevision).toBe(2)
    expect(
      afterCleanUndo.domain.state.definitions.some((item) =>
        item.payload.includes('b1b-undo-clean'),
      ),
    ).toBe(false)

    stage = 'commit the conflicting definition through the interface'
    await panel.getByRole('button', { name: '读取当前项目', exact: true }).click()
    await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled({
      timeout: 15000,
    })
    await commitDefinition(panel, 'b1b-undo-first', '首个定义', 3)
    const firstReceipt = panel.getByRole('region', { name: '已提交回执', exact: true })
    await expect(firstReceipt).toBeVisible({ timeout: 30000 })
    const firstOperation = await receiptOperation(firstReceipt)
    evidence.firstOperation = firstOperation
    expect(firstOperation).not.toBe(cleanOperation)

    stage = 'commit a later change on the same resource through the real named bridge'
    const op2 = await page.evaluate(async () => {
      const bridge = window.ontolearn!
      const read = await bridge.readProject({ editor: 'ontology-transaction' })
      if (!read.ok) throw new Error(`Actual project read refused: ${read.error.code}`)
      const baseRevision = read.data.domain.projectRevision
      const target = read.data.domain.state.definitions.find(
        (item) => item.layer === 'ontology' && item.payload.includes('b1b-undo-first'),
      )
      if (!target) throw new Error('Actual project exposes no b1b-undo-first definition')
      const value = JSON.parse(target.payload) as {
        triples?: Array<{ subject: string; predicate: string; object: string }>
        entityMetadata?: {
          entityMetadataVersion: 1
          entities: Record<
            string,
            {
              identifier: string
              labels: Array<[string, string]>
              definitions: Array<[string, string]>
              synonyms: string[]
              examples: string[]
            }
          >
        }
      }
      const triples = (value.triples ?? []).map((triple) =>
        triple.predicate.endsWith('#label') ? { ...triple, object: '"冲突后的定义"@zh' } : triple,
      )
      if (!triples.length) throw new Error('Actual definition exposes no triples')
      const entityMetadata = value.entityMetadata
        ? {
            ...value.entityMetadata,
            entities: Object.fromEntries(
              Object.entries(value.entityMetadata.entities).map(([iri, meta]) => [
                iri,
                { ...meta, labels: [['冲突后的定义', 'zh']] as Array<[string, string]> },
              ]),
            ),
          }
        : undefined
      const nextValue = entityMetadata
        ? { ...value, triples, entityMetadata }
        : { ...value, triples }
      const preview = await bridge.previewProjectChangeset({
        baseRevision,
        intent: 'change',
        plan: {
          definitions: [{ layer: 'ontology', id: target.id, value: nextValue }],
        },
      })
      if (!preview.ok) throw new Error(`Actual preview refused: ${preview.error.code}`)
      if (preview.data.status !== 'ready')
        throw new Error('Actual preview is not a ready changeset')
      let cursor: string | null = null
      let completion: string | null = null
      for (let index = 0; index < 64; index++) {
        const page = await bridge.getProjectDiffPage({
          previewHash: preview.data.previewHash,
          documentKind: preview.data.manifest.documentKind,
          pageSize: 32,
          cursor,
        })
        if (!page.ok) throw new Error(`Actual diff page refused: ${page.error.code}`)
        completion = page.data.nextCursor
        if (page.data.complete) break
        cursor = page.data.nextCursor
      }
      if (!completion) throw new Error('Actual diff document exposes no completion cursor')
      const confirmation = await bridge.confirmProjectChangeset({
        previewHash: preview.data.previewHash,
        completionCursor: completion,
      })
      if (!confirmation.ok)
        throw new Error(`Actual confirmation refused: ${confirmation.error.code}`)
      const job = await bridge.commitProjectChangeSet({
        operationId: crypto.randomUUID(),
        confirmation: confirmation.data,
      })
      if (!job.ok) throw new Error(`Actual commit refused: ${job.error.code}`)
      return { definitionId: target.id, jobId: job.data.jobId, baseRevision }
    })
    evidence.op2 = op2
    await expect
      .poll(
        async () => {
          const op2Job = data(await page.evaluate((id) => window.ontolearn!.getJob(id), op2.jobId))
          if (op2Job.state === 'failed' || op2Job.state === 'cancelled')
            throw new Error(`Actual op2 job settled to ${op2Job.state}`)
          return op2Job.state
        },
        { timeout: 30000 },
      )
      .toBe('succeeded')
    const op2Settled = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
    )
    const op2Revision = op2Settled.domain.projectRevision
    expect(op2Revision).toBe(op2.baseRevision + 1)
    evidence.op2Revision = op2Revision

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

    stage = 'the paused undo wrote nothing at all'
    const afterConflict = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
    )
    expect(afterConflict.domain.projectRevision).toBe(op2Revision)
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
