import { test, expect, _electron as electron, type Locator, type Page } from '@playwright/test'
import { createHash } from 'node:crypto'
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import type { BridgeResult, JobView, QueryDescriptorDTO, QueryDraftDTO } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'
import { validateV2 } from '../../packages/contracts/src/v2'

const hash = /^[0-9a-f]{64}$/
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
const definitionId = 'e2e-open-high-alarms'
// The fixed input contains A01=High/Open, A02=High/Closed, A03=Low/Open.
// Use its actual existing supported query, under a new managed definition ID.
const sparql =
  'PREFIX l: <urn:ontolearn:learning:>\n' +
  'SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . ' +
  '?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm'
const draft: QueryDraftDTO = {
  name: '尚未关闭的高等级告警（真实工作台）',
  description: '核对固定设备运维输入中的 High 与 Open 条件；不请求推导或模型。',
  sparql,
  scope: 'asserted',
  capabilityQuestion: '哪些已记录的高等级告警尚未关闭？',
  source: 'editor',
}
const descriptor = {
  version: 1,
  name: draft.name,
  description: draft.description,
  scope: draft.scope,
  capabilityQuestion: draft.capabilityQuestion,
  source: draft.source,
}
const definition = { text: sparql, references: [], descriptor }
const alarm = 'urn:ontolearn:learning:alarm/A01'
function data<T>(value: BridgeResult<T>): T {
  if (!value.ok) throw new Error(`Actual query bridge refused: ${JSON.stringify(value.error)}`)
  return value.data
}
// Test-side canonical JSON for independent constant fixtures, not a production adapter.
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    const encoded = JSON.stringify(value)
    if (encoded === undefined) throw new Error('Invalid constant fixture')
    return encoded
  }
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']'
  const record = value as Record<string, unknown>
  return (
    '{' +
    Object.keys(record)
      .sort()
      .map((key) => JSON.stringify(key) + ':' + canonical(record[key]))
      .join(',') +
    '}'
  )
}
const sha256 = (text: string) => createHash('sha256').update(text, 'utf8').digest('hex')
async function jobInventory(page: Page, projectId: string) {
  const jobs: Array<{ jobId: string; operationId: string }> = []
  const jobIds = new Set<string>()
  const cursors = new Set<string>()
  let listSnapshotId: string | null = null
  let cursor: string | null = null
  for (let pageNumber = 0; pageNumber < 32; pageNumber++) {
    const raw: Record<string, unknown> = data(
      await page.evaluate((options) => window.ontolearn!.listJobs(options), {
        filter: 'all' as const,
        pageSize: 100,
        listSnapshotId,
        cursor,
      }),
    )
    expect(validateV2('jobList', raw)).toBe(true)
    const response = raw as {
      binding: { projectId: string; filter: string; order: string; listSnapshotId: string }
      jobs: JobView[]
      nextCursor: string | null
    }
    expect(response.binding.projectId).toBe(projectId)
    expect(response.binding.filter).toBe('all')
    expect(response.binding.order).toBe('createdAtMs+jobId:asc')
    expect(response.binding.listSnapshotId).toMatch(uuid)
    if (listSnapshotId !== null) expect(response.binding.listSnapshotId).toBe(listSnapshotId)
    listSnapshotId = response.binding.listSnapshotId
    expect(response.jobs.length).toBeLessThanOrEqual(100)
    for (const job of response.jobs) {
      expect(job.projectId).toBe(projectId)
      expect(job.jobId).toMatch(uuid)
      expect(job.operationId).toMatch(uuid)
      expect(jobIds.has(job.jobId)).toBe(false)
      jobIds.add(job.jobId)
      jobs.push({ jobId: job.jobId, operationId: job.operationId })
    }
    if (response.nextCursor === null)
      return jobs.sort((left, right) => left.jobId.localeCompare(right.jobId))
    expect(response.jobs.length).toBeGreaterThan(0)
    expect(response.nextCursor).toMatch(uuid)
    expect(cursors.has(response.nextCursor)).toBe(false)
    cursors.add(response.nextCursor)
    cursor = response.nextCursor
  }
  throw new Error('Actual fixed Job inventory did not terminate within this small fixture bound')
}

async function originalJobId(panel: Locator): Promise<string> {
  const identity = panel.locator('code')
  await expect(identity).toHaveText(uuid)
  const value = await identity.textContent()
  if (!value || !uuid.test(value)) throw new Error('Actual UI did not expose its original Job')
  return value
}
async function readFixedResult(page: Page, resultId: string) {
  // Each original named call completes before the next: no competing computing window.
  const actual = data(
    await page.evaluate(
      (id) => window.ontolearn!.getQueryResultDescriptor({ resultId: id }),
      resultId,
    ),
  )
  const text = data(
    await page.evaluate(
      (ref) =>
        window.ontolearn!.getQueryExecutedTextPage({
          descriptorRef: ref,
          maxUtf8Bytes: 32768,
          cursor: null,
        }),
      actual.descriptorRef,
    ),
  )
  const rows = data(
    await page.evaluate(
      (ref) =>
        window.ontolearn!.getQueryRowsPage({ descriptorRef: ref, pageSize: 200, cursor: null }),
      actual.descriptorRef,
    ),
  )
  return { descriptor: actual, text, rows }
}
function assertResult(
  actual: Awaited<ReturnType<typeof readFixedResult>>,
  job: JobView,
  projectId: string,
  inputSnapshotId: string,
) {
  const resultId = job.resultRef?.resultId
  if (!resultId) throw new Error('Successful query lacks its actual immutable result')
  const expectedIdentity = {
    projectId,
    resultId,
    jobId: job.jobId,
    inputSnapshotId,
    inputProjectRevision: 2,
    scope: 'asserted',
    definitionId,
    parametersHash: job.parametersHash,
    implementation: job.implementation,
    payloadSha256: expect.stringMatching(hash),
    definitionSha256: sha256(canonical(definition)),
    inputSelection: 'current',
    projectionVersion: 1,
    lengthPolicyId: 'query-presentation-scalars-v1',
  }
  expect(actual.descriptor.identity).toEqual(expectedIdentity)
  expect(actual.descriptor.descriptorRef).toMatch(uuid)
  expect(actual.descriptor.executedText).toEqual({
    sha256: sha256(sparql),
    utf8Bytes: Buffer.byteLength(sparql, 'utf8'),
    unicodeScalars: [...sparql].length,
    utf16Units: sparql.length,
  })
  expect(actual.descriptor.query).toEqual({
    kind: 'SELECT',
    columns: [{ index: 0, name: 'alarm' }],
    rowCount: 1,
  })
  expect(actual.descriptor.metadata).toEqual({
    projectId,
    resultId,
    jobId: job.jobId,
    kind: 'query',
    definitionId,
    inputSnapshotId,
    inputProjectRevision: 2,
    scope: 'asserted',
    dependencyVector: job.dependencyVector,
    definitionSetDigests: job.definitionSetDigests,
    implementation: job.implementation,
    parametersHash: job.parametersHash,
    state: 'current',
    staleReason: [],
    payloadStatus: 'available',
    createdAtMs: expect.any(Number),
    historicalSelectionRequired: false,
  })
  expect(Number.isSafeInteger(actual.descriptor.metadata.createdAtMs)).toBe(true)
  expect(actual.text).toEqual({
    identity: actual.descriptor.identity,
    kind: 'text',
    order: 'utf8-byte:asc',
    startUtf8Byte: 0,
    utf8Length: Buffer.byteLength(sparql, 'utf8'),
    text: sparql,
    nextCursor: null,
  })
  expect(actual.rows).toEqual({
    identity: actual.descriptor.identity,
    kind: 'rows',
    order: 'query-index:asc',
    rows: [
      {
        index: 0,
        rowKey: sha256(canonical([resultId, actual.descriptor.identity.payloadSha256, 0])),
        cells: [{ kind: 'iri', iri: alarm, n3: `<${alarm}>` }],
      },
    ],
    nextCursor: null,
  })
}

test('T04 query UI saves, executes typed results and reopens its owned profile', async () => {
  // Keep the existing ordinary e2e timeout and retries:0; failures remain failures.
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  const options = {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
    acceptDownloads: true,
  }
  const evidence: Record<string, unknown> = {
    boundary: [
      'Actual Electron/main/preload/UI writes.',
      'Reopened original Job is explicitly selected through the real history012 UI.',
      'Text, rows, rowKey option and downloaded CSV are checked through that selected panel.',
      'Named read-only APIs add complete immutable binding checks after the UI assertions.',
      'T02 M UI is not exercised.',
    ].join(' '),
  }
  let stage = 'launch'
  let application: Awaited<ReturnType<typeof launchIsolatedDesktop>> | undefined =
    await launchIsolatedDesktop(options)
  try {
    let page = await application.firstWindow()
    stage = 'create fixed example through UI'
    await page.getByTestId('project-name').fill('T04 真实查询运维示例')
    await page.getByTestId('project-create-example').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await expect(page.getByTestId('project-open')).toHaveCount(1)
    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    let workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    await workspace.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
    )
    await expect(workspace.getByRole('button', { name: '新建查询草稿', exact: true })).toBeEnabled()
    const initial = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(initial.domain.projectRevision).toBe(1)
    expect(initial.workspace.metadata.templateRef).toBe(
      'equipment-maintenance@52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e',
    )
    expect(initial.domain.state.facts).toHaveLength(18)

    stage = 'edit and persist working draft through UI'
    await workspace.getByRole('button', { name: '新建查询草稿', exact: true }).click()
    await workspace.getByLabel('项目内查询标识', { exact: true }).fill(definitionId)
    await workspace.getByLabel('名称', { exact: true }).fill(draft.name)
    await workspace.getByRole('textbox', { name: '说明', exact: true }).fill(draft.description)
    await workspace
      .getByRole('textbox', { name: '关联能力问题', exact: true })
      .fill(draft.capabilityQuestion)
    await workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true }).fill(sparql)
    await expect(workspace.getByRole('combobox', { name: '数据范围', exact: true })).toHaveValue(
      'asserted',
    )
    await expect(workspace.getByRole('combobox', { name: '执行输入', exact: true })).toHaveValue(
      'current',
    )
    await workspace
      .getByRole('button', { name: '保存工作草稿（不提交正式定义）', exact: true })
      .click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '工作草稿已持久化；正式定义尚未提交。',
    )
    const prepare = workspace.getByRole('button', { name: '读取正式保存的完整差异', exact: true })
    await expect(prepare).toBeEnabled()
    const durable = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(durable.domain).toEqual(initial.domain)
    expect(durable.workspace.draft).toMatchObject({
      editor: 'query-workspace-v1',
      state: 'present',
      present: true,
      generation: 1,
      boundDomainRevision: 1,
      contentHash: sha256(canonical({ version: 1, definitionId, draft })),
      contentJson: canonical({ version: 1, definitionId, draft }),
    })
    evidence.initial = initial
    evidence.durableDraft = durable.workspace.draft

    stage = 'inspect full actual Diff and explicitly confirm through UI'
    await prepare.click()
    const diff = workspace.getByRole('region', { name: '正式提交完整差异', exact: true })
    await expect(diff).toBeVisible()
    const rawDiff = await diff.locator('pre').textContent()
    if (rawDiff === null) throw new Error('Full actual Diff is missing')
    const document: unknown = JSON.parse(rawDiff)
    expect(document).toEqual([
      {
        resource: ['definition', 'query', definitionId],
        before: null,
        after: { layer: 'query', id: definitionId, payload: canonical(definition) },
      },
    ])
    await expect(diff.locator('code')).toHaveText(sha256(canonical(document)))
    const confirm = diff.getByRole('button', { name: '明确确认并提交真实任务', exact: true })
    await expect(confirm).toBeDisabled()
    await diff
      .getByRole('checkbox', { name: '我已核对完整差异，确认提交此版本', exact: true })
      .check()
    await expect(confirm).toBeEnabled()
    await confirm.click()
    let task = workspace.getByRole('region', { name: '真实查询或提交任务', exact: true })
    const commitJobId = await originalJobId(task)
    await expect(task).toContainText('：succeeded；')
    const refresh = task.getByRole('button', { name: '刷新任务、原操作与固定结果', exact: true })
    await expect(refresh).toBeEnabled()
    await refresh.click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '真实提交终态、原operation、历史与当前定义均已核对；可执行受管查询。',
    )
    const execute = workspace.getByRole('button', {
      name: '执行已载入且未改变的受管定义',
      exact: true,
    })
    await expect(execute).toBeEnabled()
    const committed = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(committed.projectId).toBe(initial.projectId)
    expect(committed.domain.projectRevision).toBe(2)
    expect(committed.domain.state.facts).toEqual(initial.domain.state.facts)
    expect(committed.domain.state.definitions.filter((item) => item.id === definitionId)).toEqual([
      { layer: 'query', id: definitionId, payload: canonical(definition) },
    ])
    const commitJob = data(await page.evaluate((id) => window.ontolearn!.getJob(id), commitJobId))
    const marker = data(
      await page.evaluate((id) => window.ontolearn!.getOperation(id), commitJob.operationId),
    )
    expect(commitJob).toMatchObject({
      projectId: initial.projectId,
      capability: 'changeset.commit',
      state: 'succeeded',
      error: null,
      inputSnapshotId: initial.inputSnapshotId,
    })
    expect(commitJob.input).toEqual({
      scope: 'asserted',
      definitionId: 'changeset',
      inputSnapshotId: initial.inputSnapshotId,
      parametersHash: commitJob.parametersHash,
      derivedResultIds: [],
      preparedPlanRef: expect.stringMatching(hash),
    })
    expect(typeof commitJob.confirmationRef).toBe('string')
    expect(commitJob.confirmationRef).not.toBe('')
    if (!marker) throw new Error('Actual successful Job lacks its original operation marker')
    expect(marker).toEqual({
      projectId: initial.projectId,
      operationId: commitJob.operationId,
      jobId: commitJob.jobId,
      projectRevision: 2,
      beforeSnapshotId: initial.inputSnapshotId,
      afterSnapshotId: committed.inputSnapshotId,
      planHash: expect.stringMatching(hash),
    })
    expect(commitJob.commitProgress).toEqual({
      mode: 'atomic',
      operationId: commitJob.operationId,
      marker: {
        projectRevision: 2,
        beforeSnapshotId: initial.inputSnapshotId,
        afterSnapshotId: committed.inputSnapshotId,
        planHash: marker.planHash,
      },
    })
    evidence.fullDiff = document
    evidence.commitJob = commitJob
    evidence.operationMarker = marker

    stage = 'execute original managed definition and display actual typed result'
    await execute.click()
    task = workspace.getByRole('region', { name: '真实查询或提交任务', exact: true })
    await expect(task.locator('code')).not.toHaveText(commitJobId)
    const queryJobId = await originalJobId(task)
    await expect(task).toContainText('：succeeded；')
    const refreshQuery = task.getByRole('button', {
      name: '刷新任务、原操作与固定结果',
      exact: true,
    })
    await expect(refreshQuery).toBeEnabled()
    await refreshQuery.click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '已取得真实结果描述；按固定引用分别读取文本与结果页。',
    )
    const result = workspace.getByRole('region', { name: '查询结果', exact: true })
    await expect(result).toContainText('完整结果共 1 行')
    await result.getByText('本次实际执行的 SPARQL', { exact: true }).click()
    await workspace.getByRole('button', { name: '读取执行文本第一页', exact: true }).click()
    await expect(result.locator('pre')).toHaveText(sparql)
    const readRows = workspace.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true })
    await expect(readRows).toBeEnabled()
    await readRows.click()
    const table = result.getByRole('table')
    await expect(table).toBeVisible()
    await expect(table.getByRole('columnheader')).toHaveText(['alarm'])
    await expect(table.locator('tbody tr')).toHaveCount(1)
    await expect(table.locator('tbody td > span')).toHaveText([alarm])
    await table.getByText('RDF 原文', { exact: true }).click()
    await expect(table.locator('tbody code')).toHaveText(`<${alarm}>`)
    await expect(readRows).toBeEnabled()
    const queryJob = data(await page.evaluate((id) => window.ontolearn!.getJob(id), queryJobId))
    expect(queryJob).toMatchObject({
      projectId: initial.projectId,
      capability: 'query.execute',
      state: 'succeeded',
      error: null,
      inputSnapshotId: committed.inputSnapshotId,
      confirmationRef: null,
    })
    expect(queryJob.input).toEqual({
      inputSnapshotId: committed.inputSnapshotId,
      scope: 'asserted',
      definitionId,
      parametersHash: queryJob.parametersHash,
      derivedResultIds: [],
      preparedPlanRef: null,
    })
    if (!queryJob.resultRef) throw new Error('Actual query did not retain its result identity')
    const resultId = queryJob.resultRef.resultId
    expect(queryJob.resultRef.inputSnapshotId).toBe(committed.inputSnapshotId)
    const beforeRestart = await readFixedResult(page, resultId)
    assertResult(beforeRestart, queryJob, initial.projectId, committed.inputSnapshotId)
    evidence.queryJob = queryJob
    evidence.beforeRestartResult = beforeRestart
    const launch = await application.evaluate(({ app }) => ({
      userData: app.getPath('userData'),
      sessionData: app.getPath('sessionData'),
      appPath: app.getAppPath(),
      packaged: app.isPackaged,
      pid: process.pid,
    }))
    evidence.launch = launch
    await page.screenshot({ path: test.info().outputPath('t04-query-typed-before-restart.png') })
    await application.close()
    application = undefined

    stage = 'restart the same owned profile and open through real UI'
    application = await electron.launch({
      ...options,
      args: [...options.args, `--user-data-dir=${launch.userData}`],
    })
    expect(await application.evaluate(({ app }) => app.getPath('userData'))).toBe(launch.userData)
    page = await application.firstWindow()
    await page.getByTestId('project-list-refresh').click()
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    const open = page.locator(
      `[data-testid="project-open"][data-project-id="${initial.projectId}"]`,
    )
    await expect(open).toBeVisible()
    await open.click()
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await expect(page.getByTestId('selected-project-version')).toContainText('版本 2')
    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    await workspace.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
    )
    await expect(workspace.getByLabel('项目内查询标识', { exact: true })).toHaveValue(definitionId)
    await expect(workspace.getByLabel('名称', { exact: true })).toHaveValue(draft.name)
    await expect(workspace.getByRole('textbox', { name: '说明', exact: true })).toHaveValue(
      draft.description,
    )
    await expect(workspace.getByRole('textbox', { name: '关联能力问题', exact: true })).toHaveValue(
      draft.capabilityQuestion,
    )
    await expect(workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      sparql,
    )
    await expect(workspace.getByRole('combobox', { name: '数据范围', exact: true })).toHaveValue(
      'asserted',
    )
    const load = workspace.getByRole('button', { name: '按所选当前/历史输入载入定义', exact: true })
    await expect(load).toBeEnabled()
    await load.click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '已载入真实受管定义；后续编辑需先正式提交。',
    )
    await expect(load).toBeEnabled()
    const saved = data(
      await page.evaluate(
        (id) =>
          window.ontolearn!.loadQueryDefinition({
            definitionId: id,
            selection: { kind: 'current' },
          }),
        definitionId,
      ),
    )
    expect(saved).toEqual({
      projectId: initial.projectId,
      definitionId,
      baseProjectRevision: 2,
      inputSnapshotId: committed.inputSnapshotId,
      definitionVersion: 1,
      definitionSha256: sha256(canonical(definition)),
      kind: 'managed',
      descriptorVersion: 1,
      descriptorSha256: sha256(canonical(descriptor)),
      draft,
      loadRef: expect.stringMatching(uuid),
    })
    const jobsBeforeHistoryRestore = await jobInventory(page, initial.projectId)
    stage = 'restore the original Job through history012 UI, without re-execution'
    const history = workspace.getByRole('region', { name: '历史查询结果恢复', exact: true })
    const refreshHistory = history.getByRole('button', { name: '刷新历史查询任务', exact: true })
    await expect(refreshHistory).toBeEnabled()
    await refreshHistory.click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '已读取原持久查询任务；选择任务只恢复结果，不执行新查询。',
    )
    const oldTask = history.getByRole('listitem').filter({ hasText: queryJobId })
    await expect(oldTask).toHaveCount(1)
    await expect(oldTask.locator('code')).toHaveText([queryJobId, committed.inputSnapshotId])
    await oldTask.getByRole('button', { name: '恢复此查询任务的结果', exact: true }).click()
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(
      '已恢复原查询结果；输入快照与过期状态以该结果的真实描述为准，未重新执行。',
    )
    const historyLane = workspace.getByRole('region', { name: '所选历史任务结果', exact: true })
    const restoredPanel = historyLane.getByRole('region', { name: '查询结果', exact: true })
    await expect(restoredPanel).toContainText('当前结果')
    await expect(restoredPanel).toContainText('执行时的当前已提交输入')
    await expect(restoredPanel.locator('code').first()).toHaveText(committed.inputSnapshotId)
    await expect(workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      sparql,
    )
    await restoredPanel.getByText('本次实际执行的 SPARQL', { exact: true }).click()
    const historyText = historyLane.getByRole('button', { name: '读取执行文本第一页', exact: true })
    await expect(historyText).toBeEnabled()
    await historyText.click()
    await expect(restoredPanel.locator('pre')).toHaveText(sparql)
    await expect(
      restoredPanel.getByRole('button', { name: '下一段执行文本', exact: true }),
    ).toBeDisabled()
    const historyRows = historyLane.getByRole('button', {
      name: '读取 SELECT 结果第一页',
      exact: true,
    })
    await expect(historyRows).toBeEnabled()
    await historyRows.click()
    const restoredTable = restoredPanel.getByRole('table')
    await expect(restoredTable.getByRole('columnheader')).toHaveText(['alarm'])
    await expect(restoredTable.locator('tbody tr')).toHaveCount(1)
    await expect(restoredTable.locator('tbody td > span')).toHaveText([alarm])
    await restoredTable.getByText('RDF 原文', { exact: true }).click()
    await expect(restoredTable.locator('tbody code')).toHaveText(`<${alarm}>`)
    const rowKey = sha256(canonical([resultId, beforeRestart.descriptor.identity.payloadSha256, 0]))
    await expect(
      restoredPanel.getByRole('combobox', { name: '查看结果行', exact: true }),
    ).toHaveValue(rowKey)
    await expect(
      restoredPanel.getByRole('combobox', { name: '查看结果行', exact: true }).locator('option'),
    ).toHaveText(['第 1 行'])
    await expect(
      restoredPanel.getByRole('button', { name: '下一页结果', exact: true }),
    ).toBeDisabled()
    // Download the actual UI Blob; do not call a CSV utility or intercept the bridge.
    const downloaded = page.waitForEvent('download')
    await restoredPanel.getByRole('button', { name: '导出当前页 CSV', exact: true }).click()
    const csv = await downloaded
    expect(csv.suggestedFilename()).toBe('query-current-page.csv')
    expect(await csv.failure()).toBeNull()
    const csvPath = await csv.path()
    if (!csvPath) throw new Error('Actual UI CSV download has no owned artifact')
    const csvBytes = await readFile(csvPath)
    expect(csvBytes.equals(Buffer.from(`\uFEFF"alarm"\r\n"<${alarm}>"\r\n`, 'utf8'))).toBe(true)
    await test
      .info()
      .attach('t04-reopened-history-ui.csv', { body: csvBytes, contentType: 'text/csv' })
    evidence.historyUi = {
      originalJobId: queryJobId,
      resultId,
      inputSnapshotId: committed.inputSnapshotId,
      rowKey,
    }
    await expect(historyRows).toBeEnabled()

    stage = 'add complete original named read-only binding after history UI recovery'
    const recoveredJob = data(
      await page.evaluate((id) => window.ontolearn!.getJob(id), queryJob.jobId),
    )
    expect(recoveredJob).toEqual(queryJob)
    const afterRestart = await readFixedResult(page, resultId)
    assertResult(afterRestart, recoveredJob, initial.projectId, committed.inputSnapshotId)
    const expectedRecoveredDescriptor: QueryDescriptorDTO = {
      ...beforeRestart.descriptor,
      descriptorRef: afterRestart.descriptor.descriptorRef,
    }
    expect(afterRestart.descriptor).toEqual(expectedRecoveredDescriptor)
    expect(afterRestart.text).toEqual(beforeRestart.text)
    expect(afterRestart.rows).toEqual(beforeRestart.rows)
    const restoredWorkspace = data(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(restoredWorkspace.domain).toEqual(committed.domain)
    expect(restoredWorkspace.workspace.draft).toEqual(durable.workspace.draft)
    evidence.restoredDefinition = saved
    evidence.recoveredJob = recoveredJob
    evidence.afterRestartResult = afterRestart
    evidence.restoredWorkspace = restoredWorkspace
    const jobsAfterHistoryRestore = await jobInventory(page, initial.projectId)
    expect(jobsAfterHistoryRestore).toEqual(jobsBeforeHistoryRestore)
    evidence.historyJobInventory = {
      before: jobsBeforeHistoryRestore,
      after: jobsAfterHistoryRestore,
    }
    await page.screenshot({
      path: test.info().outputPath('t04-query-definition-after-restart.png'),
    })
    stage = 'completed'
  } finally {
    try {
      await test.info().attach('t04-real-ui-query-chain', {
        body: JSON.stringify({ stage, ...evidence }, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application?.close()
    }
  }
})
