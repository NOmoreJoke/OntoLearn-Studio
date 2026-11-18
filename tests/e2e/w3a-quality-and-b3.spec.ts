import { test, expect, _electron as electron, type Locator, type Page } from '@playwright/test'
import type { BridgeResult } from '@ontolearn/contracts'
import { execFileSync } from 'node:child_process'
import { join, resolve } from 'node:path'
import { launchIsolatedDesktop } from './isolated-desktop'

const learning = 'urn:ontolearn:learning:'
const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const equipment = (number: string) => learning + 'equipment/' + number
const person = (number: string) => learning + 'person/' + number
const term = (iri: string) => '<' + iri + '>'
const jsonText = (text: string) => JSON.stringify(text)
const longSourceRow = '源😀A'.repeat(100) + '行尾'
const mappingOwner = 'w3a-test-source'
const mappedDevice = 'urn:ontolearn:w3a:source-device'

function take<T>(reply: BridgeResult<T>): T {
  if (!reply.ok) throw new Error('Actual named bridge refused: ' + JSON.stringify(reply.error))
  return reply.data
}

function desktopOptions() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.ELECTRON_RENDERER_URL
  delete env.I04_TEST_FIXTURE
  return {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  }
}

async function projectId(page: Page) {
  const active = take(await page.evaluate(() => window.ontolearn!.getActiveProject()))
  if (!active) throw new Error('Expected a real active project')
  return active.projectId
}

async function startExample(page: Page) {
  await page.getByTestId('learning-start-example').click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
    '项目已创建并打开',
  )
  return projectId(page)
}

/**
 * There is no mapping editor on this desktop. Seed one genuinely persisted
 * managed fact through the engine's atomic mapping Store API, only while this
 * test's Electron profile is closed. All result reads and toggles use the UI.
 */
function seedLongSource(profile: string, project: string) {
  const python = resolve(
    '.venv',
    process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
  )
  const script = [
    'import sys',
    'from contextlib import closing',
    'from pathlib import Path',
    'from uuid import uuid4',
    'from ontolearn_engine.job_store import JobStore',
    'from ontolearn_engine.resources import CONTRACT',
    'from ontolearn_engine.storage import digest',
    'db, project, owner, row, subject, predicate, obj = sys.argv[1:]',
    'with closing(JobStore(Path(db).resolve(strict=True), contract=CONTRACT, target_format=3)) as store:',
    '    internal = store._project(project)',
    '    fact = dict(id=digest([subject, predicate, obj]), subject=subject, predicate=predicate, object=obj)',
    '    mapping = dict(id=owner, rows=[dict(row=row, facts=[fact])])',
    '    store.commit(internal, store.revision(internal), str(uuid4()), str(uuid4()), mapping=mapping)',
  ].join('\n')
  execFileSync(python, [
    '-c',
    script,
    join(profile, 'engine.sqlite'),
    project,
    mappingOwner,
    longSourceRow,
    mappedDevice,
    learning + 'alarm',
    term(learning + 'alarm/A01'),
  ])
}

const button = (panel: Locator, name: string) => panel.getByRole('button', { name, exact: true })
const wizard = (page: Page) => page.getByTestId('mentor-panel')

async function openQuality(page: Page, fromMentor = false) {
  if (fromMentor) {
    await wizard(page).getByTestId('learning-open-quality-workspace').click()
  } else {
    await page.getByRole('link', { name: '质量与推导', exact: true }).click()
  }
  const panel = page.locator('#quality-workspace')
  await expect(panel.getByTestId('quality-btn-run-check')).toBeEnabled()
  return panel
}

async function saveQualityDefinition(panel: Locator, id: string) {
  await button(panel, '读取完整差异').click()
  const confirm = button(panel, '确认并提交')
  await expect(confirm).toBeEnabled()
  await expect(panel.locator('pre').filter({ hasText: id })).toBeVisible()
  await confirm.click()
  await expect(panel.getByText('定义已提交。', { exact: true })).toBeVisible()
  await expect(confirm).toHaveCount(0)
  await expect(panel.getByTestId('quality-btn-run-check')).toBeEnabled()
}

async function addRequiredConstraint(panel: Locator, id: string, path: string) {
  await panel.getByLabel('定义类型', { exact: true }).selectOption('constraint')
  await panel.getByLabel('现有定义', { exact: true }).selectOption('')
  await panel.getByLabel('稳定标识', { exact: true }).fill(id)
  await panel.getByLabel('名称', { exact: true }).fill('必填 · ' + path)
  await panel.getByLabel('目标类 IRI', { exact: true }).fill(learning + 'Equipment')
  await panel.getByLabel('直接属性路径 IRI', { exact: true }).fill(learning + path)
  await panel.getByLabel('模板', { exact: true }).selectOption('required')
  await saveQualityDefinition(panel, id)
}

type Pattern =
  | { kind: 'type'; subject: string; class: string }
  | { kind: 'property'; subject: string; path: string; object: string }
  | { kind: 'compare'; subject: string; op: 'eq'; object: string }

async function fillPatterns(group: Locator, patterns: Pattern[], conclusion = false) {
  for (const [index, pattern] of patterns.entries()) {
    if (index > 0) await button(group, conclusion ? '添加结论' : '添加条件').click()
    const row = group.locator('.quality-pattern').nth(index)
    await row
      .getByLabel('第 ' + (index + 1) + ' 项类型', { exact: true })
      .selectOption(pattern.kind)
    await row
      .getByLabel(pattern.kind === 'compare' ? '比较左值' : '主体变量或 IRI', { exact: true })
      .fill(pattern.subject)
    if (pattern.kind === 'property') {
      await row.getByLabel('属性 IRI', { exact: true }).fill(pattern.path)
    }
    if (pattern.kind === 'compare') {
      await row.getByLabel('运算符', { exact: true }).selectOption(pattern.op)
    }
    await row
      .getByLabel(pattern.kind === 'type' ? '类 IRI' : '右值 / RDF 项 / 变量', { exact: true })
      .fill(pattern.kind === 'type' ? pattern.class : pattern.object)
  }
}

async function addRule(panel: Locator, id: string, conditions: Pattern[], outputClass: string) {
  await panel.getByLabel('定义类型', { exact: true }).selectOption('rule')
  await panel.getByLabel('现有定义', { exact: true }).selectOption('')
  await panel.getByLabel('稳定标识', { exact: true }).fill(id)
  await panel.getByLabel('名称', { exact: true }).fill(id + ' 分类')
  await fillPatterns(panel.getByRole('group', { name: '全部满足以下条件（合取）' }), conditions)
  await fillPatterns(
    panel.getByRole('group', { name: '推导一个或多个新事实' }),
    [{ kind: 'type', subject: '?equipment', class: outputClass }],
    true,
  )
  await saveQualityDefinition(panel, id)
}

async function addRiskRule(panel: Locator, compare: boolean) {
  const conditions: Pattern[] = [
    { kind: 'type', subject: '?equipment', class: learning + 'Equipment' },
    { kind: 'property', subject: '?equipment', path: learning + 'alarm', object: '?alarm' },
    { kind: 'property', subject: '?alarm', path: learning + 'level', object: '"High"' },
    {
      kind: 'property',
      subject: '?alarm',
      path: learning + 'status',
      object: compare ? '?status' : '"Open"',
    },
  ]
  if (compare) conditions.push({ kind: 'compare', subject: '?status', op: 'eq', object: '"Open"' })
  await addRule(panel, 'R-risk', conditions, learning + 'HighRiskEquipment')
}

async function runQuality(panel: Locator, scope: 'asserted' | 'asserted+derived', validate = true) {
  await panel.getByLabel('验证范围', { exact: true }).selectOption(scope)
  const run = panel.getByTestId('quality-btn-run-check')
  await run.click()
  await expect(run).toBeEnabled()
  await expect(
    panel.getByText(validate ? '检查已完成。' : '推导已完成。当前没有启用的验证约束。', {
      exact: true,
    }),
  ).toBeVisible()
  await expect(panel.getByTestId('quality-reasoning-state')).toHaveAttribute(
    'data-state',
    'current',
  )
  if (validate)
    await expect(panel.getByTestId('quality-validation-state')).toHaveAttribute(
      'data-state',
      'current',
    )
}

async function openOntology(page: Page, navigate = true) {
  if (navigate) await page.getByRole('link', { name: '本体构建', exact: true }).click()
  const panel = page.getByRole('region', { name: '本体项目编辑', exact: true })
  await expect(panel.getByRole('region', { name: '本体编辑表单', exact: true })).toBeVisible()
  return panel
}

async function revision(panel: Locator) {
  const version = panel.locator('header p').first()
  await expect(version).toHaveText(/项目版本 \d+/)
  return Number((await version.textContent())!.match(/项目版本 (\d+)/)![1])
}

async function commitOntology(panel: Locator, expectedRevision: number) {
  const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
  await expect(diff).toBeVisible()
  await button(diff, '我已核对完整差异，确认提交').click()
  const receipt = panel.getByRole('region', { name: '已提交回执', exact: true })
  const pending = panel.getByRole('region', { name: '原操作状态', exact: true })
  // Either the UI has reconciled the original commit or exposes its successful
  // original job for the user to reconcile. An older receipt cannot satisfy it.
  const accepted = receipt.filter({ hasText: '提交版本 ' + expectedRevision + '。' })
  const needsReconciliation = pending.filter({ hasText: '状态：succeeded' })
  await expect(accepted.or(needsReconciliation).first()).toBeVisible()
  if (await needsReconciliation.isVisible()) {
    await button(needsReconciliation, '核对原操作与提交回执').click()
  }
  await expect(accepted).toContainText('当前已读版本 ' + expectedRevision + '。')
  await expect(pending).toHaveCount(0)
}

async function addFact(panel: Locator, subject: string, predicate: string, object: string) {
  const next = (await revision(panel)) + 1
  const facts = panel.getByRole('region', { name: '实例事实', exact: true })
  await button(facts, '新建事实并读取当前基准').click()
  await facts.getByLabel('主体个体 IRI', { exact: true }).fill(subject)
  await facts.getByLabel('属性 IRI', { exact: true }).fill(predicate)
  await facts.getByLabel('规范 RDF 对象', { exact: true }).fill(object)
  await button(facts, '预览新增事实').click()
  await commitOntology(panel, next)
}

async function removeFact(panel: Locator, subject: string, predicate: string, object: string) {
  const next = (await revision(panel)) + 1
  const facts = panel.getByRole('region', { name: '实例事实', exact: true })
  await facts.getByLabel('查找事实', { exact: true }).fill(subject)
  const row = facts
    .getByRole('row')
    .filter({ has: panel.getByRole('cell', { name: predicate, exact: true }) })
    .filter({ has: panel.getByRole('cell', { name: object, exact: true }) })
  await button(row, '载入事实').click()
  await button(facts, '预览移除原事实').click()
  await commitOntology(panel, next)
}

async function addNeedsInspection(panel: Locator) {
  const next = (await revision(panel)) + 1
  await button(panel, '新建概念').click()
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  await form.getByLabel('类型').selectOption('class')
  await form.getByLabel('类声明').selectOption('owl')
  await form.getByLabel('稳定 IRI', { exact: true }).fill(learning + 'NeedsInspection')
  await form.getByLabel('英文标识', { exact: true }).fill('NeedsInspection')
  await button(form, '预览定义修改').click()
  await commitOntology(panel, next)
}

async function setAssignedToAxioms(panel: Locator) {
  const next = (await revision(panel)) + 1
  await panel.getByLabel('查找概念', { exact: true }).fill('assignedTo')
  await button(panel, '查看 assignedTo').click()
  const detail = panel.getByRole('article', { name: '选中对象详情' })
  await button(detail, '将对象载入编辑表单').click()
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  await form.getByLabel('适用主体类 IRI（定义域）').fill(learning + 'Equipment')
  await form.getByLabel('客体类 / 数据类型 IRI（值域）').fill(learning + 'Person')
  await button(form, '预览定义修改').click()
  await commitOntology(panel, next)
}

const queryStatus = (panel: Locator) => panel.locator('p[role="status"][aria-live="polite"]')
const queryTask = (panel: Locator) => panel.getByRole('region', { name: '真实查询或提交任务' })
const refreshQuery = (panel: Locator) => button(queryTask(panel), '刷新任务、原操作与固定结果')
const derivedQueryId = 'w3a-derived-risk'
const derivedQueryText = [
  'PREFIX l: <urn:ontolearn:learning:>',
  'SELECT ?equipment ?class WHERE {',
  '  ?equipment a ?class .',
  '  FILTER (?class = l:HighRiskEquipment)',
  '} ORDER BY ?equipment',
].join('\n')

async function openQuery(page: Page) {
  await page.getByRole('link', { name: '本体查询', exact: true }).click()
  const panel = page.getByRole('region', { name: '本体查询工作台', exact: true })
  await button(panel, '读取项目与持久工作草稿').click()
  await expect(queryStatus(panel)).toHaveText(
    '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
  )
  return panel
}

async function saveDerivedQuery(panel: Locator) {
  await button(panel, '新建查询草稿').click()
  await panel.getByLabel('项目内查询标识', { exact: true }).fill(derivedQueryId)
  await panel.getByLabel('名称', { exact: true }).fill('当前高风险设备')
  await panel.getByLabel('说明', { exact: true }).fill('返回基于当前快照实际推导的风险分类。')
  await panel.getByLabel('关联能力问题', { exact: true }).fill('哪些设备属于高风险设备？')
  await panel.getByLabel('可见 SPARQL', { exact: true }).fill(derivedQueryText)
  await panel.getByLabel('数据范围', { exact: true }).selectOption('asserted+derived')
  await button(panel, '保存工作草稿（不提交正式定义）').click()
  await expect(queryStatus(panel)).toHaveText('工作草稿已持久化；正式定义尚未提交。')

  await button(panel, '读取正式保存的完整差异').click()
  const diff = panel.getByRole('region', { name: '正式提交完整差异', exact: true })
  await expect(diff.locator('pre')).toContainText(derivedQueryId)
  await expect(diff.locator('pre')).toContainText('asserted+derived')
  await diff.getByLabel('我已核对完整差异，确认提交此版本').check()
  await button(diff, '明确确认并提交真实任务').click()
  await expect(queryTask(panel)).toContainText('：succeeded；')
  await refreshQuery(panel).click()
  await expect(queryStatus(panel)).toHaveText(
    '真实提交终态、原operation、历史与当前定义均已核对；可执行受管查询。',
  )
}

async function loadQuery(panel: Locator, id: string) {
  await panel.getByRole('combobox', { name: '已提交查询', exact: true }).selectOption(id)
  const consent = panel.getByRole('checkbox', {
    name: '我已保留当前编辑，允许重新载入或新建替换它',
    exact: true,
  })
  if (await consent.isVisible()) await consent.check()
  await button(panel, '按所选当前/历史输入载入定义').click()
  await expect(queryStatus(panel)).toHaveText('已载入真实受管定义；后续编辑需先正式提交。')
}

async function executeQuery(page: Page, panel: Locator) {
  const task = queryTask(panel)
  const code = task.locator('code').first()
  const [previous] = await code.allTextContents()
  await button(panel, '执行已载入且未改变的受管定义').click()
  if (previous) await expect(code).not.toHaveText(previous)
  await expect(code).toHaveText(/^[0-9a-f-]{36}$/)
  const jobId = await code.textContent()
  if (!jobId) throw new Error('No original query job identity')
  await expect(task).toContainText('：succeeded；')
  await refreshQuery(panel).click()
  await expect(queryStatus(panel)).toHaveText(
    '已取得真实结果描述；按固定引用分别读取文本与结果页。',
  )
  await button(panel, '读取 SELECT 结果第一页').click()
  const result = panel
    .getByRole('region', { name: '本次执行结果', exact: true })
    .getByRole('region', { name: '查询结果', exact: true })
  await expect(result.getByRole('table')).toBeVisible()
  const job = take(await page.evaluate((id) => window.ontolearn!.getJob(id), jobId))
  expect(job.capability).toBe('query.execute')
  expect(job.state).toBe('succeeded')
  if (!job.resultRef) throw new Error('No real query result reference')
  const descriptor = take(
    await page.evaluate(
      (resultId) => window.ontolearn!.getQueryResultDescriptor({ resultId }),
      job.resultRef.resultId,
    ),
  )
  return { result, job, descriptor }
}

async function assertF08(result: Locator) {
  const graph = result.getByRole('region', { name: '结果输入的局部关系图', exact: true })
  const source = graph.locator('li[data-fact-id]').filter({ hasText: mappingOwner })
  const toggle = button(source, '展开全文').or(button(source, '收起全文'))
  const collapsed = Array.from(longSourceRow).slice(0, 256).join('') + '…'
  await expect(source.getByText(collapsed, { exact: true })).toBeVisible()
  await expect(toggle).toHaveText('展开全文')
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await toggle.click()
  await expect(toggle).toHaveText('收起全文')
  await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  await expect(source.getByText(longSourceRow, { exact: true })).toBeVisible()
  await toggle.click()
  await expect(toggle).toHaveText('展开全文')
  await expect(toggle).toHaveAttribute('aria-expanded', 'false')
  await expect(source.getByText(collapsed, { exact: true })).toBeVisible()
}

async function focusTask(page: Page, task: 'quality' | 'transfer-repair' | 'transfer-classify') {
  await page.locator('[data-testid="learning-path-task"][data-task-id="' + task + '"]').click()
  await expect(wizard(page).getByTestId('learning-open-quality-workspace')).toBeEnabled()
}

async function loadTaskFixture(page: Page) {
  const mentor = wizard(page)
  await mentor.getByTestId('learning-load-task-fixture').click()
  await expect(page.getByTestId('learning-task-fixture-preview')).toBeVisible()
  await page.getByTestId('learning-confirm-task-fixture').click()
  await expect(page.getByTestId('learning-task-fixture-status')).toHaveText('本关初始数据已载入。')
  await expect(page.getByTestId('learning-task-fixture-preview')).toHaveCount(0)
  return projectId(page)
}

async function checkLearning(page: Page, status: '需要修复' | '已通过') {
  const mentor = wizard(page)
  const check = mentor.getByTestId('mentor-btn-check')
  await check.click()
  await expect(check).toBeEnabled()
  await expect(mentor.getByTestId('learning-check-status')).toHaveText(status)
}

test('W3a quality edits, explanation, snapshot invalidation, derived query and F08 expansion', async () => {
  test.setTimeout(180000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  let application: Awaited<ReturnType<typeof launchIsolatedDesktop>> | undefined =
    await launchIsolatedDesktop(desktopOptions())
  try {
    let page = await application.firstWindow()
    await expect(page.locator('body')).toBeVisible()
    stage = 'create real G-base project and seed mapped source in its closed, isolated library'
    const project = await startExample(page)
    evidence.projectId = project
    const profile = await application.evaluate(({ app }) => app.getPath('userData'))
    await application.close()
    application = undefined
    seedLongSource(profile, project)
    const options = desktopOptions()
    application = await electron.launch({
      ...options,
      args: [...options.args, '--user-data-dir=' + profile],
    })
    expect(await application.evaluate(({ app }) => app.getPath('userData'))).toBe(profile)
    page = await application.firstWindow()
    expect(
      await application.evaluate(({ BrowserWindow }) =>
        BrowserWindow.getAllWindows().some((window) => window.isVisible()),
      ),
    ).toBe(true)
    await page.locator('[data-testid="project-open"][data-project-id="' + project + '"]').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已打开',
    )

    stage = 'commit formal FR-504/505 definitions and produce one violation'
    let quality = await openQuality(page)
    await addRequiredConstraint(quality, 'name-required', 'name')
    await addRiskRule(quality, true)
    let ontology = await openOntology(page)
    await removeFact(ontology, equipment('003'), learning + 'name', '"备用泵C"')
    quality = await openQuality(page)
    await expect(quality.getByLabel('验证范围', { exact: true })).toHaveValue('asserted+derived')
    await runQuality(quality, 'asserted+derived')
    const finding = quality
      .getByTestId('quality-findings')
      .getByRole('region', { name: '违规', exact: true })
      .getByRole('listitem')
      .filter({ hasText: 'equipment/003' })
    await expect(finding).toContainText(learning + 'name')
    const trace = quality.getByTestId('quality-rule-traces')
    await expect(trace).toContainText('R-risk')
    await expect(trace).toContainText(learning + 'HighRiskEquipment')
    await expect(trace).toContainText(learning + 'alarm/A01')

    stage = 'locate the violation then repair its fact in ontology'
    await button(finding, '定位').click()
    ontology = await openOntology(page, false)
    const located = page.getByTestId('quality-locate-target')
    await expect(located).toBeVisible()
    await expect(located).toContainText(equipment('003'))
    await expect(located).toContainText(learning + 'name')
    await addFact(ontology, equipment('003'), learning + 'name', '"备用泵C"')
    quality = await openQuality(page)
    await expect(quality.getByTestId('quality-reasoning-state')).toHaveAttribute(
      'data-state',
      'stale',
    )
    await expect(quality.getByTestId('quality-validation-state')).toHaveAttribute(
      'data-state',
      'stale',
    )
    await expect(quality.getByTestId('quality-stale-reasons')).toContainText('FACTS_CHANGED')

    stage = 'save a derived-scope managed query, then rerun on that committed snapshot'
    await saveDerivedQuery(await openQuery(page))
    quality = await openQuality(page)
    await runQuality(quality, 'asserted+derived')
    await expect(quality.getByTestId('quality-validation-state')).toHaveAttribute(
      'data-conforms',
      'true',
    )
    await expect(quality.getByTestId('quality-findings').getByText(equipment('003'))).toHaveCount(0)

    stage = 'run derived query through its loaded definition and read fixed rows and executed text'
    const query = await openQuery(page)
    await loadQuery(query, derivedQueryId)
    await expect(query.getByLabel('数据范围', { exact: true })).toHaveValue('asserted+derived')
    const derived = await executeQuery(page, query)
    expect(derived.descriptor.identity.scope).toBe('asserted+derived')
    expect(derived.job.input).toMatchObject({ derivedResultIds: [expect.any(String)] })
    await expect(derived.result.getByRole('columnheader')).toHaveText(['equipment', 'class'])
    await expect(derived.result.locator('tbody tr')).toHaveCount(1)
    await expect(derived.result.locator('tbody td > span')).toHaveText([
      equipment('001'),
      learning + 'HighRiskEquipment',
    ])
    const text = take(
      await page.evaluate(
        (descriptorRef) =>
          window.ontolearn!.getQueryExecutedTextPage({
            descriptorRef,
            maxUtf8Bytes: 32768,
            cursor: null,
          }),
        derived.descriptor.descriptorRef,
      ),
    )
    expect(text.identity).toEqual(derived.descriptor.identity)
    expect(text.text).toBe(derivedQueryText)
    evidence.derivedJob = derived.job.jobId
    evidence.inputSnapshotId = derived.job.inputSnapshotId

    stage = 'run the asserted-scope query on the same snapshot and toggle real mapped source text'
    await loadQuery(query, 'unclosed-high')
    const asserted = await executeQuery(page, query)
    expect(asserted.descriptor.identity.scope).toBe('asserted')
    expect(asserted.job.inputSnapshotId).toBe(derived.job.inputSnapshotId)
    await expect(asserted.result.locator('tbody td > span')).toHaveText([learning + 'alarm/A01'])
    await assertF08(asserted.result)
    evidence.assertedJob = asserted.job.jobId
    evidence.sourceCodePoints = Array.from(longSourceRow).length
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('w3a-quality-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application?.close()
    }
  }
})

test('W3a B3 quality and LX-01 plus both independent transfer cases', async () => {
  test.setTimeout(240000)
  const evidence: Record<string, unknown> = {}
  let stage = 'launch'
  const application = await launchIsolatedDesktop(desktopOptions())
  try {
    const page = await application.firstWindow()
    expect(
      await application.evaluate(({ BrowserWindow }) =>
        BrowserWindow.getAllWindows().some((window) => window.isVisible()),
      ),
    ).toBe(true)
    const project = await startExample(page)
    evidence.qualityProject = project
    await focusTask(page, 'quality')

    stage = 'V-01 missing name and repaired results, and R-01 on exact G-base'
    let quality = await openQuality(page, true)
    await addRequiredConstraint(quality, 'name-required', 'name')
    await addRiskRule(quality, false)
    let ontology = await openOntology(page)
    await removeFact(ontology, equipment('003'), learning + 'name', '"备用泵C"')
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted')
    await expect(quality.getByTestId('quality-findings')).toContainText(equipment('003'))
    ontology = await openOntology(page)
    await addFact(ontology, equipment('003'), learning + 'name', '"备用泵C"')
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted')
    await expect(quality.getByTestId('quality-validation-state')).toHaveAttribute(
      'data-conforms',
      'true',
    )
    await expect(quality.getByTestId('quality-rule-traces')).toContainText('R-risk')
    await expect(quality.getByTestId('quality-rule-traces')).toContainText(equipment('001'))

    stage = 'R-05 projects a rule-chain warning without producing the chained conclusion'
    ontology = await openOntology(page)
    await addNeedsInspection(ontology)
    quality = await openQuality(page, true)
    await addRule(
      quality,
      'R-next',
      [{ kind: 'type', subject: '?equipment', class: learning + 'HighRiskEquipment' }],
      learning + 'NeedsInspection',
    )
    await runQuality(quality, 'asserted')
    await expect(quality.getByText(/RULE_CHAIN_UNSUPPORTED.*R-next/)).toBeVisible()
    await expect(quality.getByTestId('quality-rule-traces')).not.toContainText('NeedsInspection')

    stage = 'LX-01 loads its prerequisites, adds domain/range and tests the separate constraint'
    expect(await loadTaskFixture(page)).toBe(project)
    ontology = await openOntology(page)
    await setAssignedToAxioms(ontology)
    quality = await openQuality(page, true)
    await addRequiredConstraint(quality, 'assigned-to-required', 'assignedTo')
    await runQuality(quality, 'asserted')
    const findings = quality.getByTestId('quality-findings')
    await expect(findings).toContainText(equipment('002'))
    await expect(findings).toContainText(equipment('003'))

    stage = 'LX-01 fails with extra asserted L02 despite selecting the expected origins'
    ontology = await openOntology(page)
    await addFact(ontology, equipment('002'), learning + 'assignedTo', term(person('L02')))
    await addFact(ontology, equipment('003'), learning + 'assignedTo', term(person('L01')))
    await addFact(ontology, person('L02'), rdfType, term(learning + 'Person'))
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted')
    const mentor = wizard(page)
    const l01 = mentor.getByTestId('learning-lx01-origin-l01')
    const l02 = mentor.getByTestId('learning-lx01-origin-l02')
    await l01.selectOption('asserted')
    await l02.selectOption('derived')
    await checkLearning(page, '需要修复')
    await expect(mentor).toContainText('这样步骤 4 就没有可区分的推导了')

    stage = 'LX-01 passes after removing the assertion and recomputing its range inference'
    ontology = await openOntology(page)
    await removeFact(ontology, person('L02'), rdfType, term(learning + 'Person'))
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted')
    await expect(quality.getByTestId('quality-validation-state')).toHaveAttribute(
      'data-conforms',
      'true',
    )
    const rdfsTrace = quality.getByText(/RDFS 推导依据/)
    await rdfsTrace.click()
    await expect(rdfsTrace.locator('..')).toContainText(person('L02'))
    await expect(rdfsTrace.locator('..')).toContainText('rdf-schema#range')
    await l01.selectOption('asserted')
    await l02.selectOption('derived')
    await checkLearning(page, '已通过')
    await expect(mentor.getByTestId('learning-operation-state')).toContainText('操作完成：是')
    await expect(mentor.getByTestId('learning-guided-stage-badge')).toHaveCount(0)
    evidence.lx01Passed = true

    stage = 'transfer-repair reports only equipment 102, then passes after catalogue-based repair'
    await focusTask(page, 'transfer-repair')
    const repair = await loadTaskFixture(page)
    expect(repair).not.toBe(project)
    evidence.repairProject = repair
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted')
    await expect(quality.getByTestId('quality-findings')).toContainText(equipment('102'))
    await expect(quality.getByTestId('quality-findings')).not.toContainText(equipment('101'))
    await expect(quality.getByTestId('quality-findings')).not.toContainText(equipment('103'))
    ontology = await openOntology(page)
    await addFact(ontology, equipment('102'), learning + 'name', jsonText('供水泵'))
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted')
    await expect(quality.getByTestId('quality-validation-state')).toHaveAttribute(
      'data-conforms',
      'true',
    )
    await checkLearning(page, '已通过')
    await expect(mentor.getByTestId('learning-operation-state')).toContainText('独立迁移成功：是')
    evidence.independentRepair = true

    stage =
      'transfer-classify reasons with no enabled validation constraints and passes using origins'
    await focusTask(page, 'transfer-classify')
    const classification = await loadTaskFixture(page)
    expect(new Set([project, repair, classification]).size).toBe(3)
    evidence.classificationProject = classification
    quality = await openQuality(page, true)
    await runQuality(quality, 'asserted', false)
    await expect(quality.getByTestId('quality-rule-traces')).toContainText(equipment('201'))
    await expect(quality.getByTestId('quality-rule-traces')).toContainText('HighRiskEquipment')
    const class0 = mentor.getByTestId('learning-transfer-origin-0')
    const class1 = mentor.getByTestId('learning-transfer-origin-1')
    await expect(class0).toHaveValue('')
    await expect(class1).toHaveValue('')
    await class0.selectOption('asserted')
    await class1.selectOption('derived')
    await checkLearning(page, '已通过')
    await expect(mentor.getByTestId('learning-operation-state')).toContainText('独立迁移成功：是')
    expect(await page.evaluate(() => [localStorage.length, sessionStorage.length])).toEqual([0, 0])
    evidence.independentClassify = true
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('w3a-b3-evidence', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application.close()
    }
  }
})
