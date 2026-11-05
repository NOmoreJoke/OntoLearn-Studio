import {
  test,
  expect,
  _electron as electron,
  type ConsoleMessage,
  type Locator,
  type Page,
} from '@playwright/test'
import { createHash } from 'node:crypto'
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import type { BridgeResult, JobView, QueryDraftDTO } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'
import { validateV2 } from '../../packages/contracts/src/v2'

const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/
const hash = /^[0-9a-f]{64}$/
const equipment = [
  'urn:ontolearn:learning:equipment/001',
  'urn:ontolearn:learning:equipment/002',
  'urn:ontolearn:learning:equipment/003',
]
const equipmentType = 'urn:ontolearn:learning:Equipment'
const typePredicate = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const managedNotice = '真实提交终态、原operation、历史与当前定义均已核对；可执行受管查询。'
const resultNotice = '已取得真实结果描述；按固定引用分别读取文本与结果页。'
const historyNotice = '已恢复原查询结果；输入快照与过期状态以该结果的真实描述为准，未重新执行。'

function take<T>(reply: BridgeResult<T>): T {
  if (!reply.ok) throw new Error(`Actual bridge refused: ${JSON.stringify(reply.error)}`)
  return reply.data
}
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    const raw = JSON.stringify(value)
    if (raw === undefined) throw new Error('Invalid independent fixture')
    return raw
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
const definition = (draft: QueryDraftDTO) => ({
  text: draft.sparql,
  references: [],
  descriptor: {
    version: 1,
    name: draft.name,
    description: draft.description,
    scope: draft.scope,
    capabilityQuestion: draft.capabilityQuestion,
    source: draft.source,
  },
})
const draftFor = (name: string, sparql: string): QueryDraftDTO => ({
  name,
  description: '真实 UI 正式保存、受管执行及固定结果读取；不使用模型或推导。',
  sparql,
  scope: 'asserted',
  capabilityQuestion: '固定断言输入的完整预期结果是否相同？',
  source: 'editor',
})
const status = (workspace: Locator) => workspace.locator('p[role="status"][aria-live="polite"]')
const button = (workspace: Locator, name: string) =>
  workspace.getByRole('button', { name, exact: true })
const taskPanel = (workspace: Locator) =>
  workspace.getByRole('region', { name: '真实查询或提交任务', exact: true })
const resultLane = (workspace: Locator) =>
  workspace.getByRole('region', { name: '本次执行结果', exact: true })
const resultPanel = (lane: Locator) => lane.getByRole('region', { name: '查询结果', exact: true })
async function jobInventory(page: Page, projectId: string) {
  const jobs: Array<{ jobId: string; operationId: string }> = []
  const jobIds = new Set<string>()
  const cursors = new Set<string>()
  let listSnapshotId: string | null = null
  let cursor: string | null = null
  for (let pageNumber = 0; pageNumber < 32; pageNumber++) {
    const raw: Record<string, unknown> = take(
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

async function taskId(workspace: Locator, previous?: string) {
  const code = taskPanel(workspace).locator('code')
  if (previous) await expect(code).not.toHaveText(previous)
  await expect(code).toHaveText(uuid)
  const id = await code.textContent()
  if (!id || !uuid.test(id)) throw new Error('Actual original Job identity is missing')
  return id
}
async function finished(workspace: Locator, notice: string) {
  await expect(taskPanel(workspace)).toContainText('：succeeded；')
  const refresh = button(taskPanel(workspace), '刷新任务、原操作与固定结果')
  await expect(refresh).toBeEnabled()
  await refresh.click()
  await expect(status(workspace)).toHaveText(notice)
  await expect(refresh).toBeEnabled()
}
async function setup(page: Page, name: string) {
  await page.getByTestId('project-name').fill(name)
  await page.getByTestId('project-create-example').click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
    '项目已创建并打开',
  )
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
  await page.getByRole('link', { name: '本体查询', exact: true }).click()
  const workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
  await button(workspace, '读取项目与持久工作草稿').click()
  await expect(status(workspace)).toHaveText(
    '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
  )
  await expect(button(workspace, '新建查询草稿')).toBeEnabled()
  const initial = take(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
  )
  expect(initial.domain.projectRevision).toBe(1)
  expect(initial.workspace.metadata.templateRef).toBe(
    'equipment-maintenance@52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e',
  )
  expect(initial.domain.state.facts).toHaveLength(18)
  expect(
    initial.domain.state.facts
      .filter((fact) => fact.predicate === typePredicate && fact.object === `<${equipmentType}>`)
      .map((fact) => fact.subject)
      .sort(),
  ).toEqual(equipment)
  return { workspace, initial }
}
async function saveDefinition(
  page: Page,
  workspace: Locator,
  id: string,
  draft: QueryDraftDTO,
  original?: { draft: QueryDraftDTO; previousJobId: string },
) {
  const before = take(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
  )
  if (!original) {
    await button(workspace, '新建查询草稿').click()
    await workspace.getByLabel('项目内查询标识', { exact: true }).fill(id)
  } else {
    await expect(workspace.getByLabel('项目内查询标识', { exact: true })).toHaveValue(id)
  }
  await workspace.getByLabel('名称', { exact: true }).fill(draft.name)
  await workspace.getByRole('textbox', { name: '说明', exact: true }).fill(draft.description)
  await workspace
    .getByRole('textbox', { name: '关联能力问题', exact: true })
    .fill(draft.capabilityQuestion)
  await workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true }).fill(draft.sparql)
  await expect(workspace.getByRole('combobox', { name: '数据范围', exact: true })).toHaveValue(
    'asserted',
  )
  await expect(workspace.getByRole('combobox', { name: '执行输入', exact: true })).toHaveValue(
    'current',
  )
  await button(workspace, '读取正式保存的完整差异').click()
  const diff = workspace.getByRole('region', { name: '正式提交完整差异', exact: true })
  await expect(diff).toBeVisible()
  const raw = await diff.locator('pre').textContent()
  if (!raw) throw new Error('Actual complete Diff missing')
  const expectedDiff = [
    {
      resource: ['definition', 'query', id],
      before: original
        ? { layer: 'query', id, payload: canonical(definition(original.draft)) }
        : null,
      after: { layer: 'query', id, payload: canonical(definition(draft)) },
    },
  ]
  expect(JSON.parse(raw)).toEqual(expectedDiff)
  await expect(diff.locator('code')).toHaveText(sha256(canonical(expectedDiff)))
  const confirm = button(diff, '明确确认并提交真实任务')
  await expect(confirm).toBeDisabled()
  await diff
    .getByRole('checkbox', { name: '我已核对完整差异，确认提交此版本', exact: true })
    .check()
  await expect(confirm).toBeEnabled()
  await confirm.click()
  const jobId = await taskId(workspace, original?.previousJobId)
  await finished(workspace, managedNotice)
  // Read-only evidence after the UI's full Diff + explicit confirmation + real Job.
  const after = take(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
  )
  const job = take(await page.evaluate((value) => window.ontolearn!.getJob(value), jobId))
  const marker = take(
    await page.evaluate((value) => window.ontolearn!.getOperation(value), job.operationId),
  )
  expect(job).toMatchObject({
    projectId: before.projectId,
    capability: 'changeset.commit',
    state: 'succeeded',
    error: null,
    inputSnapshotId: before.inputSnapshotId,
  })
  expect(after.domain.projectRevision).toBe(before.domain.projectRevision + 1)
  expect(after.domain.state.facts).toEqual(before.domain.state.facts)
  expect(
    after.domain.state.definitions.filter((value) => value.layer === 'query' && value.id === id),
  ).toEqual([{ layer: 'query', id, payload: canonical(definition(draft)) }])
  expect(marker).toEqual({
    projectId: before.projectId,
    operationId: job.operationId,
    jobId,
    projectRevision: after.domain.projectRevision,
    beforeSnapshotId: before.inputSnapshotId,
    afterSnapshotId: after.inputSnapshotId,
    planHash: expect.stringMatching(hash),
  })
  if (!marker) throw new Error('Actual commit marker missing')
  expect(job.commitProgress).toEqual({
    mode: 'atomic',
    operationId: job.operationId,
    marker: {
      projectRevision: after.domain.projectRevision,
      beforeSnapshotId: before.inputSnapshotId,
      afterSnapshotId: after.inputSnapshotId,
      planHash: marker.planHash,
    },
  })
  return { before, after, job, marker, diff: expectedDiff }
}
async function execute(page: Page, workspace: Locator, previous: string) {
  const run = button(workspace, '执行已载入且未改变的受管定义')
  await expect(run).toBeEnabled()
  await run.click()
  const id = await taskId(workspace, previous)
  await finished(workspace, resultNotice)
  const job = take(await page.evaluate((value) => window.ontolearn!.getJob(value), id))
  expect(job).toMatchObject({
    capability: 'query.execute',
    state: 'succeeded',
    error: null,
    confirmationRef: null,
  })
  if (!job.resultRef) throw new Error('Actual query result identity missing')
  return job
}
async function readBinding(page: Page, job: JobView) {
  if (!job.resultRef) throw new Error('No actual resultRef')
  const descriptor = take(
    await page.evaluate(
      (resultId) => window.ontolearn!.getQueryResultDescriptor({ resultId }),
      job.resultRef.resultId,
    ),
  )
  const text = take(
    await page.evaluate(
      (descriptorRef) =>
        window.ontolearn!.getQueryExecutedTextPage({
          descriptorRef,
          maxUtf8Bytes: 32768,
          cursor: null,
        }),
      descriptor.descriptorRef,
    ),
  )
  return { descriptor, text }
}
function assertBinding(
  actual: Awaited<ReturnType<typeof readBinding>>,
  job: JobView,
  draft: QueryDraftDTO,
  id: string,
  inputRevision: number,
  selection: 'current' | 'historical' = 'current',
  stale = false,
) {
  const resultId = job.resultRef!.resultId
  expect(actual.descriptor.identity).toEqual({
    projectId: job.projectId,
    resultId,
    jobId: job.jobId,
    inputSnapshotId: job.inputSnapshotId,
    inputProjectRevision: inputRevision,
    scope: 'asserted',
    definitionId: id,
    parametersHash: job.parametersHash,
    implementation: job.implementation,
    payloadSha256: expect.stringMatching(hash),
    definitionSha256: sha256(canonical(definition(draft))),
    inputSelection: selection,
    projectionVersion: 1,
    lengthPolicyId: 'query-presentation-scalars-v1',
  })
  expect(actual.descriptor.descriptorRef).toMatch(uuid)
  expect(job.input).toEqual({
    inputSnapshotId: job.inputSnapshotId,
    scope: 'asserted',
    definitionId: id,
    parametersHash: job.parametersHash,
    derivedResultIds: [],
    preparedPlanRef: null,
  })
  expect(job.resultRef).toEqual({ resultId, inputSnapshotId: job.inputSnapshotId })
  expect(actual.descriptor.executedText).toEqual({
    sha256: sha256(draft.sparql),
    utf8Bytes: Buffer.byteLength(draft.sparql, 'utf8'),
    unicodeScalars: [...draft.sparql].length,
    utf16Units: draft.sparql.length,
  })
  expect(actual.descriptor.metadata).toEqual({
    projectId: job.projectId,
    resultId,
    jobId: job.jobId,
    kind: 'query',
    definitionId: id,
    inputSnapshotId: job.inputSnapshotId,
    inputProjectRevision: inputRevision,
    scope: 'asserted',
    dependencyVector: job.dependencyVector,
    definitionSetDigests: job.definitionSetDigests,
    implementation: job.implementation,
    parametersHash: job.parametersHash,
    state: stale ? 'stale' : 'current',
    staleReason: stale
      ? [{ code: 'QUERY_CHANGED', dependency: `query:${id}`, before: 1, after: 2 }]
      : [],
    payloadStatus: 'available',
    createdAtMs: expect.any(Number),
    historicalSelectionRequired: stale,
  })
  expect(Number.isSafeInteger(actual.descriptor.metadata.createdAtMs)).toBe(true)
  expect(actual.text).toEqual({
    identity: actual.descriptor.identity,
    kind: 'text',
    order: 'utf8-byte:asc',
    startUtf8Byte: 0,
    utf8Length: Buffer.byteLength(draft.sparql, 'utf8'),
    text: draft.sparql,
    nextCursor: null,
  })
}
async function showText(lane: Locator, text: string) {
  const panel = resultPanel(lane)
  await panel.getByText('本次实际执行的 SPARQL', { exact: true }).click()
  const read = button(lane, '读取执行文本第一页')
  await expect(read).toBeEnabled()
  await read.click()
  await expect(panel.locator('pre')).toHaveText(text)
  await expect(button(panel, '下一段执行文本')).toBeDisabled()
  await expect(read).toBeEnabled()
}
async function downloadCsv(page: Page, panel: Locator, name: string, expected: string) {
  const pending = page.waitForEvent('download')
  await button(panel, name).click()
  const download = await pending
  expect(download.suggestedFilename()).toBe(
    name === '导出 ASK 结果 CSV' ? 'query-ask.csv' : 'query-current-page.csv',
  )
  expect(await download.failure()).toBeNull()
  const path = await download.path()
  if (!path) throw new Error('Actual downloaded CSV artifact is missing')
  const bytes = await readFile(path)
  expect(bytes.equals(Buffer.from('\uFEFF' + expected, 'utf8'))).toBe(true)
  await test.info().attach(`actual-ui-${name}-${test.info().attachments.length}.csv`, {
    body: bytes,
    contentType: 'text/csv',
  })
  return bytes.toString('utf8')
}
function csv(columns: string[], rows: string[][]) {
  // Independent fixture contains only safe ASCII headers and absolute IRI N3 cells.
  return (
    [columns, ...rows.map((row) => row.map((iri) => `<${iri}>`))]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\r\n') + '\r\n'
  )
}
async function assertUiRows(
  panel: Locator,
  columns: string[],
  values: string[][],
  start: number,
  resultId: string,
  payloadSha: string,
) {
  await expect(panel.getByRole('columnheader')).toHaveText(columns)
  const table = panel.getByRole('table')
  await expect(table.locator('tbody tr')).toHaveCount(values.length)
  await expect(table.locator('tbody td > span')).toHaveText(values.flat())
  await expect(table.locator('caption')).toHaveText(
    `当前结果页：第 ${start + 1}–${start + values.length} 行`,
  )
  const rowKeys = values.map((_, index) => sha256(canonical([resultId, payloadSha, start + index])))
  const selector = panel.getByRole('combobox', { name: '查看结果行', exact: true })
  await expect(selector.locator('option')).toHaveText(
    values.map((_, index) => `第 ${start + index + 1} 行`),
  )
  expect(
    await selector
      .locator('option')
      .evaluateAll((nodes) => nodes.map((node) => node.getAttribute('value'))),
  ).toEqual(rowKeys)
  await expect(selector).toHaveValue(rowKeys[0])
  return rowKeys
}
async function rowsPage(page: Page, ref: string, cursor: string | null) {
  return take(
    await page.evaluate(
      ({ descriptorRef, cursor }) =>
        window.ontolearn!.getQueryRowsPage({ descriptorRef, cursor, pageSize: 200 }),
      { descriptorRef: ref, cursor },
    ),
  )
}
function assertTypedRows(
  value: Awaited<ReturnType<typeof rowsPage>>,
  actual: Awaited<ReturnType<typeof readBinding>>,
  expected: string[][],
  start: number,
) {
  expect(value.identity).toEqual(actual.descriptor.identity)
  expect(value.kind).toBe('rows')
  expect(value.order).toBe('query-index:asc')
  expect(value.rows).toEqual(
    expected.map((row, index) => ({
      index: start + index,
      rowKey: sha256(
        canonical([
          actual.descriptor.identity.resultId,
          actual.descriptor.identity.payloadSha256,
          start + index,
        ]),
      ),
      cells: row.map((iri) => ({ kind: 'iri', iri, n3: `<${iri}>` })),
    })),
  )
}
async function restore(page: Page, workspace: Locator, job: JobView) {
  const jobsBefore = await jobInventory(page, job.projectId)
  const history = workspace.getByRole('region', { name: '历史查询结果恢复', exact: true })
  const refresh = button(history, '刷新历史查询任务')
  await expect(refresh).toBeEnabled()
  await refresh.click()
  await expect(status(workspace)).toHaveText(
    '已读取原持久查询任务；选择任务只恢复结果，不执行新查询。',
  )
  const item = history.getByRole('listitem').filter({ hasText: job.jobId })
  await expect(item).toHaveCount(1)
  await expect(item.locator('code')).toHaveText([job.jobId, job.inputSnapshotId])
  await button(item, '恢复此查询任务的结果').click()
  await expect(status(workspace)).toHaveText(historyNotice)
  await expect(refresh).toBeEnabled()
  const jobsAfter = await jobInventory(page, job.projectId)
  expect(jobsAfter).toEqual(jobsBefore)
  await test.info().attach(`history-no-execution-${test.info().attachments.length}.json`, {
    body: JSON.stringify(
      { originalJobId: job.jobId, before: jobsBefore, after: jobsAfter },
      null,
      2,
    ),
    contentType: 'application/json',
  })
  return workspace.getByRole('region', { name: '所选历史任务结果', exact: true })
}
async function withDesktop(work: (page: Page, evidence: Record<string, unknown>) => Promise<void>) {
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
  const evidence: Record<string, unknown> = {
    boundary:
      'Actual UI edits/full Diff/confirmation/Job/history/typed panel/download. Named APIs are read-only supplemental binding. No T02 M UI/model/derived scope.',
  }
  try {
    await work(await application.firstWindow(), evidence)
  } finally {
    try {
      await test.info().attach('t04-actual-query-variant', {
        body: JSON.stringify(evidence, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application.close()
    }
  }
}

for (const value of [true, false]) {
  test(`T04 real UI ASK ${value} stays boolean and exports its exact CSV`, async () => {
    await withDesktop(async (page, evidence) => {
      const { workspace, initial } = await setup(page, `T04 ASK ${value}`)
      const id = value ? 'e2e-ask-present' : 'e2e-ask-absent'
      const subject = value ? equipment[0] : 'urn:ontolearn:learning:equipment/missing'
      const draft = draftFor(`ASK ${value}`, `ASK { <${subject}> a <${equipmentType}> }`)
      const saved = await saveDefinition(page, workspace, id, draft)
      const job = await execute(page, workspace, saved.job.jobId)
      expect(job.inputSnapshotId).toBe(saved.after.inputSnapshotId)
      const lane = resultLane(workspace),
        panel = resultPanel(lane)
      await expect(panel).toContainText(
        value ? 'ASK：true（满足查询条件）' : 'ASK：false（未满足查询条件）',
      )
      await expect(panel).toContainText('这是布尔结果，不是 SELECT 空表。')
      await expect(panel.getByRole('table')).toHaveCount(0)
      await expect(button(lane, '读取 SELECT 结果第一页')).toBeDisabled()
      await showText(lane, draft.sparql)
      await downloadCsv(page, panel, '导出 ASK 结果 CSV', `"ASK"\r\n"${value}"\r\n`)
      const actual = await readBinding(page, job)
      assertBinding(actual, job, draft, id, 2)
      expect(actual.descriptor.query).toEqual({ kind: 'ASK', value })
      evidence.initial = initial
      evidence.saved = saved
      evidence.job = job
      evidence.result = actual
    })
  })
}

// Passive diagnostics for the existing SELECT row poll only. No bridge wrapper,
// console text, JSHandle arguments, query, cell, path or screenshot is collected.
function selectReadFailureEvidence(page: Page) {
  const observed = {
    pageerrorCount: 0,
    pageerrors: [] as Array<{ name: string; code: string | null }>,
    consoleCount: 0,
    consoleTypes: [] as string[],
  }
  const errorNames = new Set(['Error', 'TypeError', 'RangeError', 'SyntaxError'])
  const codes = [
    'INVALID_STATE',
    'IDENTITY_CONFLICT',
    'RESOURCE_LIMIT',
    'TIMEOUT',
    'PAYLOAD_EVICTED',
    'ENGINE_EXITED',
    'PERMISSION_DENIED',
    'INTERNAL_ERROR',
  ]
  const safeCodes = new Set(codes)
  const consoleTypes = new Set(['error', 'warning', 'assert', 'info', 'log', 'debug'])
  const notices = [
    managedNotice,
    resultNotice,
    historyNotice,
    '读取回执与当前结果不匹配，未应用该回执。',
    '此结果载荷已回收。结果和快照身份保留，请明确选择输入后重新执行。',
    '正在读取固定结果的文本片段…',
    '文本身份、字节范围或分页不匹配，未显示该片段。',
    '正在读取固定结果页…',
    '结果页身份、行次序或列宽不匹配，未显示该页。',
    '结果身份或描述不匹配，未显示该载荷。',
  ]
  const onPageError = (error: Error) => {
    observed.pageerrorCount = Math.min(4096, observed.pageerrorCount + 1)
    if (observed.pageerrors.length < 16) {
      observed.pageerrors.push({
        name: errorNames.has(error.name) ? error.name : 'other',
        code: error.message.length <= 64 && safeCodes.has(error.message) ? error.message : null,
      })
    }
  }
  const onConsole = (message: ConsoleMessage) => {
    observed.consoleCount = Math.min(4096, observed.consoleCount + 1)
    if (observed.consoleTypes.length < 16) {
      const kind = message.type()
      observed.consoleTypes.push(consoleTypes.has(kind) ? kind : 'other')
    }
  }
  page.on('pageerror', onPageError)
  page.on('console', onConsole)
  return {
    dispose() {
      // Remove only our exact listeners, even when an earlier operation failed.
      try {
        page.off('pageerror', onPageError)
      } catch {
        /* Evidence cleanup only. */
      }
      try {
        page.off('console', onConsole)
      } catch {
        /* Preserve the original failure. */
      }
    },
    async capture(
      workspace: Locator,
      lane: Locator,
      panel: Locator,
      pageNumber: number,
      start: number,
    ) {
      const deadline = Date.now() + 750
      let timer: ReturnType<typeof setTimeout> | undefined
      try {
        await Promise.race([
          (async () => {
            const scopes = await Promise.all(
              [workspace, lane, panel].map((scope) =>
                scope
                  .evaluateAll(
                    (nodes, allowed) => ({
                      locatorCount: nodes.length,
                      samples: nodes.slice(0, 1).map((node) => {
                        const visible = (element: Element) => element.getClientRects().length > 0
                        const messages = (role: 'alert' | 'status') =>
                          Array.from(node.querySelectorAll(`[role="${role}"]`))
                            .slice(0, 8)
                            .map((element) => {
                              if (!visible(element))
                                return {
                                  visible: false,
                                  known: null,
                                  code: null,
                                  otherTextPresent: false,
                                }
                              const raw = element.textContent ?? ''
                              const text = raw.length <= 512 ? raw.trim() : null
                              const known =
                                text !== null && allowed.notices.includes(text) ? text : null
                              const code =
                                text === null
                                  ? undefined
                                  : allowed.codes.find(
                                      (candidate) =>
                                        text ===
                                          `结果读取未完成（${candidate}），请检查连接或重新读取该结果。` ||
                                        text ===
                                          `受限错误码：${candidate}。当前编辑、原操作与真实任务保留。`,
                                    )
                              // Unrecognized text never crosses the renderer boundary.
                              return {
                                visible: true,
                                known,
                                code: code ?? null,
                                otherTextPresent:
                                  raw.length > 0 && known === null && code === undefined,
                              }
                            })
                        return {
                          visible: visible(node),
                          tableCount: node.querySelectorAll('table').length,
                          bodyRows: node.querySelectorAll('table tbody tr').length,
                          alertCount: node.querySelectorAll('[role="alert"]').length,
                          statusCount: node.querySelectorAll('[role="status"]').length,
                          buttonCount: node.querySelectorAll('button').length,
                          selectCount: node.querySelectorAll('select').length,
                          alerts: messages('alert'),
                          statuses: messages('status'),
                        }
                      }),
                    }),
                    { notices, codes },
                  )
                  .catch(() => ({ unavailable: true })),
              ),
            )
            if (Date.now() >= deadline) return
            const url = new URL(page.url())
            const knownHash = new Set([
              '',
              '#query-workspace',
              '#ontology-workspace',
              '#overview',
              '#modules',
            ])
            const detail = {
              pageNumber,
              start,
              observed,
              observationLimits: {
                saturatingCount: 4096,
                eventSamples: 16,
                messageSamples: 8,
                scopeSamples: 1,
                captureMs: 750,
              },
              url: {
                protocol: ['file:', 'http:', 'https:'].includes(url.protocol)
                  ? url.protocol
                  : 'other',
                host: ['localhost', '127.0.0.1', ''].includes(url.hostname)
                  ? url.hostname
                  : 'other',
                document: url.pathname.endsWith('/index.html') ? 'index.html' : 'other',
                hash: knownHash.has(url.hash) ? url.hash : 'other',
              },
              workspace: scopes[0],
              lane: scopes[1],
              panel: scopes[2],
              apiReply: 'not observed; no bridge replacement or additional business request',
              screenshot: 'not captured; may expose query or result cells',
            }
            await test.info().attach(`select-read-failure-${pageNumber}.json`, {
              body: JSON.stringify(detail, null, 2),
              contentType: 'application/json',
            })
          })().catch(() => undefined),
          new Promise<void>((resolve) => {
            timer = setTimeout(resolve, 750)
          }),
        ])
      } catch {
        /* Best effort only; caller rethrows its original assertion object. */
      } finally {
        if (timer !== undefined) clearTimeout(timer)
      }
    },
  }
}

test('T04 real UI SELECT reads all 243 ordered rows across actual bounded pages and page CSVs', async () => {
  await withDesktop(async (page, evidence) => {
    const { workspace, initial } = await setup(page, 'T04 SELECT 243 行')
    const id = 'e2e-equipment-cartesian'
    const columns = ['a', 'b', 'c', 'd', 'e']
    const text =
      'PREFIX l: <urn:ontolearn:learning:>\nSELECT ?a ?b ?c ?d ?e WHERE { ?a a l:Equipment . ?b a l:Equipment . ?c a l:Equipment . ?d a l:Equipment . ?e a l:Equipment . } ORDER BY ?a ?b ?c ?d ?e'
    const draft = draftFor('三个固定设备的五列有序组合', text)
    const expected = equipment.flatMap((a) =>
      equipment.flatMap((b) =>
        equipment.flatMap((c) => equipment.flatMap((d) => equipment.map((e) => [a, b, c, d, e]))),
      ),
    )
    expect(expected).toHaveLength(243)
    const saved = await saveDefinition(page, workspace, id, draft)
    const job = await execute(page, workspace, saved.job.jobId)
    expect(job.inputSnapshotId).toBe(saved.after.inputSnapshotId)
    const lane = resultLane(workspace),
      panel = resultPanel(lane)
    await expect(panel).toContainText('完整结果共 243 行；表格与导出仅包含当前页。')
    await showText(lane, text)
    const actual = await readBinding(page, job)
    assertBinding(actual, job, draft, id, 2)
    expect(actual.descriptor.query).toEqual({
      kind: 'SELECT',
      columns: columns.map((name, index) => ({ index, name })),
      rowCount: 243,
    })
    const read = button(lane, '读取 SELECT 结果第一页')
    await expect(read).toBeEnabled()
    const diagnostic = selectReadFailureEvidence(page)
    try {
      await read.click()
      const uiPages: Array<{ start: number; count: number; rowKeys: string[] }> = []
      let start = 0
      // The real page contract permits byte-bounded short pages, never more than 200.
      // Do not lower the default request or pretend it promises exactly 200 returned rows.
      for (let pageNumber = 0; pageNumber < 243; pageNumber++) {
        const bodyRows = panel.getByRole('table').locator('tbody tr')
        try {
          await expect.poll(() => bodyRows.count()).toBeGreaterThan(0)
        } catch (cause) {
          try {
            await diagnostic.capture(workspace, lane, panel, pageNumber, start)
          } catch {
            // Evidence failure never substitutes for the actual failed assertion.
          }
          throw cause
        }
        const count = await bodyRows.count()
        expect(count).toBeLessThanOrEqual(200)
        expect(start + count).toBeLessThanOrEqual(243)
        const rowKeys = await assertUiRows(
          panel,
          columns,
          expected.slice(start, start + count),
          start,
          actual.descriptor.identity.resultId,
          actual.descriptor.identity.payloadSha256,
        )
        await downloadCsv(
          page,
          panel,
          '导出当前页 CSV',
          csv(columns, expected.slice(start, start + count)),
        )
        uiPages.push({ start, count, rowKeys })
        start += count
        const next = button(panel, '下一页结果')
        if (start === 243) {
          await expect(next).toBeDisabled()
          break
        }
        await expect(next).toBeEnabled()
        await next.click()
        await expect(panel.getByRole('table').locator('caption')).toContainText(`第 ${start + 1}–`)
      }
      expect(start).toBe(243)
      expect(uiPages.length).toBeGreaterThan(1)
      expect(new Set(uiPages.flatMap((page) => page.rowKeys)).size).toBe(243)
      await expect(read).toBeEnabled()
      const actualPages: Awaited<ReturnType<typeof rowsPage>>[] = []
      const seenCursors = new Set<string>()
      let cursor: string | null = null
      let offset = 0
      for (let pageNumber = 0; pageNumber < 243; pageNumber++) {
        const fixedPage = await rowsPage(page, actual.descriptor.descriptorRef, cursor)
        expect(fixedPage.rows.length).toBeGreaterThan(0)
        expect(fixedPage.rows.length).toBeLessThanOrEqual(200)
        const end = offset + fixedPage.rows.length
        expect(end).toBeLessThanOrEqual(243)
        assertTypedRows(fixedPage, actual, expected.slice(offset, end), offset)
        actualPages.push(fixedPage)
        offset = end
        if (fixedPage.nextCursor === null) {
          expect(offset).toBe(243)
          break
        }
        expect(offset).toBeLessThan(243)
        expect(fixedPage.nextCursor).toMatch(uuid)
        expect(seenCursors.has(fixedPage.nextCursor)).toBe(false)
        seenCursors.add(fixedPage.nextCursor)
        cursor = fixedPage.nextCursor
      }
      expect(offset).toBe(243)
      expect(actualPages.at(-1)?.nextCursor).toBeNull()
      expect(actualPages.flatMap((page) => page.rows.map((row) => row.index))).toEqual(
        Array.from({ length: 243 }, (_, index) => index),
      )
      evidence.initial = initial
      evidence.saved = saved
      evidence.job = job
      evidence.result = actual
      evidence.actualPages = actualPages
      evidence.actualUiPages = uiPages
    } finally {
      diagnostic.dispose()
    }
  })
})

test('T04 history UI preserves stale result identity and explicitly executes its historical snapshot', async () => {
  await withDesktop(async (page, evidence) => {
    const { workspace, initial } = await setup(page, 'T04 历史快照与过期结果')
    const id = 'e2e-history-equipment'
    const text = `SELECT ?equipment WHERE { ?equipment a <${equipmentType}> } ORDER BY ?equipment`
    const draft = draftFor('历史设备清单', text)
    const saved = await saveDefinition(page, workspace, id, draft)
    const original = await execute(page, workspace, saved.job.jobId)
    const before = await readBinding(page, original)
    assertBinding(before, original, draft, id, 2)
    expect(before.descriptor.query).toEqual({
      kind: 'SELECT',
      columns: [{ index: 0, name: 'equipment' }],
      rowCount: 3,
    })
    const changed = { ...draft, description: '仅改受管查询说明；执行文本与断言事实保持原样。' }
    const edited = await saveDefinition(page, workspace, id, changed, {
      draft,
      previousJobId: original.jobId,
    })
    expect(edited.after.domain.projectRevision).toBe(3)
    expect(edited.after.inputSnapshotId).not.toBe(original.inputSnapshotId)
    expect(edited.after.domain.state.facts).toEqual(initial.domain.state.facts)
    let lane = await restore(page, workspace, original)
    let panel = resultPanel(lane)
    await expect(panel).toContainText('已过期，请明确选择输入后重新执行')
    await expect(panel).toContainText(`QUERY_CHANGED · query:${id} · 1 → 2`)
    await expect(panel).toContainText('执行时的当前已提交输入')
    await expect(panel.locator('code').first()).toHaveText(original.inputSnapshotId)
    await expect(workspace.getByRole('textbox', { name: '说明', exact: true })).toHaveValue(
      changed.description,
    )
    await showText(lane, text)
    await button(lane, '读取 SELECT 结果第一页').click()
    const values = equipment.map((iri) => [iri])
    await assertUiRows(
      panel,
      ['equipment'],
      values,
      0,
      before.descriptor.identity.resultId,
      before.descriptor.identity.payloadSha256,
    )
    await downloadCsv(page, panel, '导出当前页 CSV', csv(['equipment'], values))
    await expect(button(lane, '读取 SELECT 结果第一页')).toBeEnabled()
    const stale = await readBinding(page, original)
    assertBinding(stale, original, draft, id, 2, 'current', true)
    expect(stale.descriptor.identity).toEqual(before.descriptor.identity)
    expect(stale.text).toEqual(before.text)
    const staleRows = await rowsPage(page, stale.descriptor.descriptorRef, null)
    assertTypedRows(staleRows, stale, values, 0)
    expect(staleRows.nextCursor).toBeNull()
    const unchangedJob = take(
      await page.evaluate((jobId) => window.ontolearn!.getJob(jobId), original.jobId),
    )
    expect(unchangedJob).toEqual(original)

    // The user's explicit historical selector is the real owner of this new execution.
    await workspace
      .getByRole('combobox', { name: '执行输入', exact: true })
      .selectOption('historical')
    await workspace.getByLabel('历史快照标识', { exact: true }).fill(original.inputSnapshotId)
    const load = button(workspace, '按所选当前/历史输入载入定义')
    await expect(load).toBeEnabled()
    await load.click()
    await expect(status(workspace)).toHaveText('已载入真实受管定义；后续编辑需先正式提交。')
    await expect(workspace.getByRole('textbox', { name: '说明', exact: true })).toHaveValue(
      draft.description,
    )
    await expect(workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
      text,
    )
    const historical = await execute(page, workspace, edited.job.jobId)
    expect(historical.jobId).not.toBe(original.jobId)
    expect(historical.inputSnapshotId).toBe(original.inputSnapshotId)
    const historicBinding = await readBinding(page, historical)
    assertBinding(historicBinding, historical, draft, id, 2, 'historical', true)
    expect(historicBinding.descriptor.query).toEqual(before.descriptor.query)
    lane = resultLane(workspace)
    panel = resultPanel(lane)
    await expect(panel).toContainText('显式选择的历史快照')
    await expect(panel).toContainText('已过期，请明确选择输入后重新执行')
    await expect(panel.locator('code').first()).toHaveText(original.inputSnapshotId)
    await showText(lane, text)
    await button(lane, '读取 SELECT 结果第一页').click()
    await assertUiRows(
      panel,
      ['equipment'],
      values,
      0,
      historicBinding.descriptor.identity.resultId,
      historicBinding.descriptor.identity.payloadSha256,
    )
    await downloadCsv(page, panel, '导出当前页 CSV', csv(['equipment'], values))
    await expect(button(lane, '读取 SELECT 结果第一页')).toBeEnabled()
    const historicalRows = await rowsPage(page, historicBinding.descriptor.descriptorRef, null)
    assertTypedRows(historicalRows, historicBinding, values, 0)
    expect(historicalRows.nextCursor).toBeNull()
    // Restoring the old current-input Job must not retag it with the editor's historical selection.
    lane = await restore(page, workspace, original)
    panel = resultPanel(lane)
    await expect(panel).toContainText('执行时的当前已提交输入')
    await expect(panel).not.toContainText('显式选择的历史快照')
    await expect(panel).toContainText(`QUERY_CHANGED · query:${id} · 1 → 2`)
    await expect(workspace.getByRole('combobox', { name: '执行输入', exact: true })).toHaveValue(
      'historical',
    )
    evidence.initial = initial
    evidence.originalSaved = saved
    evidence.originalJob = original
    evidence.before = before
    evidence.edited = edited
    evidence.stale = stale
    evidence.staleRows = staleRows
    evidence.explicitHistoricalJob = historical
    evidence.explicitHistoricalResult = historicBinding
    evidence.explicitHistoricalRows = historicalRows
  })
})

test('T04 Q-02 closes A01 through T02 UI, preserves stale history and reopens a verified empty SELECT', async () => {
  // Keep the ordinary 30s/retries:0 budget. This adds coverage; no old case is replaced.
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
  let application: Awaited<ReturnType<typeof launchIsolatedDesktop>> | undefined =
    await launchIsolatedDesktop(options)
  const evidence: Record<string, unknown> = {
    boundary:
      'G-base Q-02: actual T02 fact edit/full Diff/confirmation; T04 UI execution, empty CSV and owned restart. Named APIs only observe after UI actions. No model, SQL, direct bridge write or inferred graph edge.',
  }
  try {
    let page = await application.firstWindow()
    const { workspace: initialWorkspace, initial } = await setup(
      page,
      'T04 Q02 关闭 A01 后查询为空',
    )
    let workspace = initialWorkspace
    const id = 'e2e-q02-open-high'
    const alarm = 'urn:ontolearn:learning:alarm/A01'
    const predicate = 'urn:ontolearn:learning:status'
    const text =
      'PREFIX l: <urn:ontolearn:learning:>\n' +
      'SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . ' +
      '?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm'
    const draft = draftFor('未闭环高等级告警 Q02', text)
    const saved = await saveDefinition(page, workspace, id, draft)
    const original = await execute(page, workspace, saved.job.jobId)
    const before = await readBinding(page, original)
    assertBinding(before, original, draft, id, 2)
    expect(before.descriptor.query).toEqual({
      kind: 'SELECT',
      columns: [{ index: 0, name: 'alarm' }],
      rowCount: 1,
    })
    await button(resultLane(workspace), '读取 SELECT 结果第一页').click()
    await assertUiRows(
      resultPanel(resultLane(workspace)),
      ['alarm'],
      [[alarm]],
      0,
      original.resultRef!.resultId,
      before.descriptor.identity.payloadSha256,
    )
    const facts = saved.after.domain.state.facts.filter(
      (fact) => fact.subject === alarm && fact.predicate === predicate,
    )
    expect(facts).toHaveLength(1)
    const fact = facts[0]
    expect(fact).toMatchObject({
      subject: alarm,
      predicate,
      object: '"Open"',
      owner: null,
      source_row: null,
      managed_value: null,
    })
    const changedFact = { ...fact, object: '"Closed"' }
    const expectedDiff = [{ resource: ['fact', fact.id], before: fact, after: changedFact }]

    await page.getByRole('link', { name: '本体构建', exact: true }).click()
    const ontology = page.getByRole('region', { name: '本体项目编辑', exact: true })
    await button(ontology, '读取当前项目').click()
    await expect(ontology).toContainText('项目版本 2')
    const factSection = ontology.getByRole('region', { name: '实例事实', exact: true })
    const factRow = factSection
      .getByRole('row')
      .filter({ hasText: alarm })
      .filter({ hasText: predicate })
    await expect(factRow).toHaveCount(1)
    await expect(factRow.locator('code')).toHaveText('"Open"')
    await button(factRow, '载入事实').click()
    await expect(factSection.getByLabel('主体个体 IRI', { exact: true })).toHaveValue(alarm)
    await expect(factSection.getByLabel('属性 IRI', { exact: true })).toHaveValue(predicate)
    await factSection.getByLabel('规范 RDF 对象', { exact: true }).fill('"Closed"')
    await button(factSection, '预览事实修改').click()
    const diff = ontology.getByRole('region', { name: '完整事务差异', exact: true })
    await expect(diff).toBeVisible()
    const diffText = await diff.locator('pre').textContent()
    if (!diffText) throw new Error('Actual complete fact Diff missing')
    expect(JSON.parse(diffText)).toEqual(expectedDiff)
    await expect(diff).toContainText('全部 1 项；分段顺序、长度、SHA 与完整文档已核对。')
    await button(diff, '我已核对完整差异，确认提交').click()
    const receipt = ontology.getByRole('region', { name: '已提交回执', exact: true })
    const pending = ontology.getByRole('region', { name: '原操作状态', exact: true })
    let reconcile = false
    await expect
      .poll(async () => {
        const state = await receipt.or(pending).evaluateAll((nodes) =>
          nodes.map((node) => ({
            kind: node.getAttribute('aria-label'),
            text: node.textContent ?? '',
          })),
        )
        if (state.some((item) => item.kind === '已提交回执' && item.text.includes('提交版本 3。')))
          return 'receipt'
        if (state.some((item) => item.kind === '原操作状态' && item.text.includes('succeeded'))) {
          reconcile = true
          return 'terminal-needs-reconciliation'
        }
        return 'waiting'
      })
      .not.toBe('waiting')
    if (reconcile) await button(pending, '核对原操作与提交回执').click()
    await expect(receipt).toContainText('提交版本 3。')
    await expect(receipt).toContainText('当前已读版本 3。')
    await expect(pending).toHaveCount(0)
    const receiptText = await receipt.locator('p').first().textContent()
    const operationId = receiptText?.match(/操作 ([a-f0-9-]{36})，/)?.[1]
    if (!operationId || !uuid.test(operationId)) throw new Error('Original fact operation missing')
    const marker = take(
      await page.evaluate((value) => window.ontolearn!.getOperation(value), operationId),
    )
    if (!marker || typeof marker.jobId !== 'string')
      throw new Error('Actual fact commit marker missing')
    const factJob = take(
      await page.evaluate((value) => window.ontolearn!.getJob(value), marker.jobId),
    )
    const after = take(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(after.domain.projectRevision).toBe(3)
    expect(after.projectId).toBe(initial.projectId)
    expect(after.domain.state.definitions).toEqual(saved.after.domain.state.definitions)
    expect(after.domain.state.facts).toEqual(
      saved.after.domain.state.facts.map((row) => (row.id === fact.id ? changedFact : row)),
    )
    expect(marker).toEqual({
      projectId: initial.projectId,
      operationId,
      jobId: factJob.jobId,
      projectRevision: 3,
      beforeSnapshotId: saved.after.inputSnapshotId,
      afterSnapshotId: after.inputSnapshotId,
      planHash: expect.stringMatching(hash),
    })
    expect(factJob).toMatchObject({
      projectId: initial.projectId,
      operationId,
      capability: 'changeset.commit',
      state: 'succeeded',
      error: null,
      inputSnapshotId: saved.after.inputSnapshotId,
      commitProgress: {
        mode: 'atomic',
        operationId,
        marker: {
          projectRevision: 3,
          beforeSnapshotId: saved.after.inputSnapshotId,
          afterSnapshotId: after.inputSnapshotId,
          planHash: marker.planHash,
        },
      },
    })
    evidence.initial = initial
    evidence.originalSaved = saved
    evidence.originalJob = original
    evidence.originalResult = before
    evidence.factChange = { diff: expectedDiff, after, job: factJob, marker }

    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    await button(workspace, '读取项目与持久工作草稿').click()
    await expect(status(workspace)).toHaveText(
      '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
    )
    let lane = await restore(page, workspace, original)
    let panel = resultPanel(lane)
    await expect(panel).toContainText('FACTS_CHANGED · facts:asserted · 1 → 2')
    await expect(panel.locator('code').first()).toHaveText(original.inputSnapshotId)
    await button(lane, '读取 SELECT 结果第一页').click()
    await assertUiRows(
      panel,
      ['alarm'],
      [[alarm]],
      0,
      original.resultRef!.resultId,
      before.descriptor.identity.payloadSha256,
    )
    const stale = await readBinding(page, original)
    const factReason = [
      { code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 1, after: 2 },
    ]
    expect(stale.descriptor.identity).toEqual(before.descriptor.identity)
    expect(stale.descriptor.metadata).toEqual({
      ...before.descriptor.metadata,
      state: 'stale',
      staleReason: factReason,
      historicalSelectionRequired: true,
    })
    expect(stale.text).toEqual(before.text)
    evidence.staleOriginal = stale

    await workspace.getByRole('combobox', { name: '已提交查询', exact: true }).selectOption(id)
    await workspace.getByRole('combobox', { name: '执行输入', exact: true }).selectOption('current')
    const currentConsent = workspace.getByRole('checkbox', {
      name: '我已保留当前编辑，允许重新载入或新建替换它',
      exact: true,
    })
    await expect(currentConsent).toBeVisible()
    await currentConsent.check()
    const load = button(workspace, '按所选当前/历史输入载入定义')
    await expect(load).toBeEnabled()
    await load.click()
    await expect(status(workspace)).toHaveText('已载入真实受管定义；后续编辑需先正式提交。')
    const empty = await execute(page, workspace, original.jobId)
    expect(empty.inputSnapshotId).toBe(after.inputSnapshotId)
    lane = resultLane(workspace)
    panel = resultPanel(lane)
    await button(lane, '读取 SELECT 结果第一页').click()
    await expect(panel.getByRole('table').locator('tbody tr')).toHaveCount(0)
    await expect(panel.getByRole('table').locator('caption')).toHaveText('当前结果页：0 行')
    const directions = panel.getByRole('region', { name: 'SELECT 空结果检查', exact: true })
    await expect(directions).toBeVisible()
    await expect(directions).toContainText('可逐项放宽条件后复查')
    await expect(directions).toContainText('检查字段是否有记录，以及映射是否成功提交到当前项目')
    await expect(directions).toContainText('不能据此证明业务事实不存在')
    await expect(panel).not.toContainText('ASK：')
    await expect(button(panel, '下一页结果')).toBeDisabled()
    await downloadCsv(page, panel, '导出当前页 CSV', csv(['alarm'], []))
    const emptyBinding = await readBinding(page, empty)
    assertBinding(emptyBinding, empty, draft, id, 3)
    expect(emptyBinding.descriptor.query).toEqual({
      kind: 'SELECT',
      columns: [{ index: 0, name: 'alarm' }],
      rowCount: 0,
    })
    const emptyRows = await rowsPage(page, emptyBinding.descriptor.descriptorRef, null)
    assertTypedRows(emptyRows, emptyBinding, [], 0)
    expect(emptyRows.nextCursor).toBeNull()
    evidence.emptyJob = empty
    evidence.emptyResult = emptyBinding
    evidence.emptyRows = emptyRows

    const userData = await application.evaluate(({ app }) => app.getPath('userData'))
    await application.close()
    application = undefined
    application = await electron.launch({
      ...options,
      args: [...options.args, `--user-data-dir=${userData}`],
    })
    expect(await application.evaluate(({ app }) => app.getPath('userData'))).toBe(userData)
    page = await application.firstWindow()
    await page.getByTestId('project-list-refresh').click()
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await page
      .locator(`[data-testid="project-open"][data-project-id="${initial.projectId}"]`)
      .click()
    await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    await button(workspace, '读取项目与持久工作草稿').click()
    await expect(status(workspace)).toHaveText(
      '项目与持久工作草稿已读回；工作草稿不代表正式查询定义。',
    )
    lane = await restore(page, workspace, empty)
    panel = resultPanel(lane)
    await expect(panel.locator('code').first()).toHaveText(after.inputSnapshotId)
    await button(lane, '读取 SELECT 结果第一页').click()
    await expect(
      panel.getByRole('region', { name: 'SELECT 空结果检查', exact: true }),
    ).toBeVisible()
    await expect(panel.getByRole('table').locator('tbody tr')).toHaveCount(0)
    await downloadCsv(page, panel, '导出当前页 CSV', csv(['alarm'], []))
    const reopened = await readBinding(page, empty)
    expect(reopened.descriptor.identity).toEqual(emptyBinding.descriptor.identity)
    expect(reopened.descriptor.metadata).toEqual(emptyBinding.descriptor.metadata)
    expect(reopened.text).toEqual(emptyBinding.text)
    evidence.reopenedEmpty = reopened

    // A new execution requires the user's explicit historical selection; restoring did not execute.
    await workspace.getByRole('combobox', { name: '已提交查询', exact: true }).selectOption(id)
    await workspace
      .getByRole('combobox', { name: '执行输入', exact: true })
      .selectOption('historical')
    await workspace.getByLabel('历史快照标识', { exact: true }).fill(original.inputSnapshotId)
    const historicalConsent = workspace.getByRole('checkbox', {
      name: '我已保留当前编辑，允许重新载入或新建替换它',
      exact: true,
    })
    await expect(historicalConsent).toBeVisible()
    await historicalConsent.check()
    await button(workspace, '按所选当前/历史输入载入定义').click()
    await expect(status(workspace)).toHaveText('已载入真实受管定义；后续编辑需先正式提交。')
    const historical = await execute(page, workspace, empty.jobId)
    expect(historical.inputSnapshotId).toBe(original.inputSnapshotId)
    const historicalBinding = await readBinding(page, historical)
    expect(historicalBinding.descriptor.identity).toEqual({
      ...before.descriptor.identity,
      resultId: historical.resultRef!.resultId,
      jobId: historical.jobId,
      parametersHash: historical.parametersHash,
      inputSelection: 'historical',
      payloadSha256: expect.stringMatching(hash),
    })
    expect(historicalBinding.descriptor.metadata).toEqual({
      ...stale.descriptor.metadata,
      resultId: historical.resultRef!.resultId,
      jobId: historical.jobId,
      parametersHash: historical.parametersHash,
      createdAtMs: expect.any(Number),
    })
    expect(historicalBinding.text).toEqual({
      ...before.text,
      identity: historicalBinding.descriptor.identity,
    })
    expect(historicalBinding.descriptor.query).toEqual(before.descriptor.query)
    lane = resultLane(workspace)
    panel = resultPanel(lane)
    await expect(panel).toContainText('显式选择的历史快照')
    await expect(panel).toContainText('FACTS_CHANGED · facts:asserted · 1 → 2')
    await button(lane, '读取 SELECT 结果第一页').click()
    await assertUiRows(
      panel,
      ['alarm'],
      [[alarm]],
      0,
      historical.resultRef!.resultId,
      historicalBinding.descriptor.identity.payloadSha256,
    )
    await expect(panel.getByRole('region', { name: 'SELECT 空结果检查', exact: true })).toHaveCount(
      0,
    )
    evidence.explicitHistoricalJob = historical
    evidence.explicitHistoricalResult = historicalBinding
  } finally {
    try {
      await test.info().attach('t04-q02-fact-change-empty-and-reopen', {
        body: JSON.stringify(evidence, null, 2),
        contentType: 'application/json',
      })
    } finally {
      await application?.close()
    }
  }
})

test('T04 same-input local graph uses actual directed assertions and withholds stale-source edges', async () => {
  await withDesktop(async (page, evidence) => {
    const { workspace, initial } = await setup(page, 'T04 同输入局部关系图')
    const id = 'e2e-authoritative-local-graph'
    const alarm = 'urn:ontolearn:learning:alarm/A01'
    const alarmType = 'urn:ontolearn:learning:Alarm'
    const alarmPredicate = 'urn:ontolearn:learning:alarm'
    const text =
      'PREFIX l: <urn:ontolearn:learning:>\n' +
      'SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . ' +
      '?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm'
    const draft = draftFor('真实实例断言关系', text)
    const saved = await saveDefinition(page, workspace, id, draft)
    const job = await execute(page, workspace, saved.job.jobId)
    const lane = resultLane(workspace),
      panel = resultPanel(lane)
    await button(lane, '读取 SELECT 结果第一页').click()
    const graph = panel.getByRole('region', { name: '结果输入的局部关系图', exact: true })
    await expect(graph).toBeVisible()
    await expect(graph.locator('code').first()).toHaveText(saved.after.inputSnapshotId)
    await expect(graph).toContainText('项目版本 2，断言事实')
    const expected = [
      [alarm, typePredicate, alarmType],
      [equipment[0], alarmPredicate, alarm],
    ].sort((a, b) => canonical(a).localeCompare(canonical(b)))
    const actual = await graph
      .locator('svg g[data-predicate]')
      .evaluateAll((nodes) =>
        nodes.map((node) =>
          ['data-subject', 'data-predicate', 'data-object'].map((key) => node.getAttribute(key)),
        ),
      )
    expect(actual.sort((a, b) => canonical(a).localeCompare(canonical(b)))).toEqual(expected)
    const facts = saved.after.domain.state.facts.filter((fact) =>
      expected.some(
        ([subject, predicate, object]) =>
          fact.subject === subject && fact.predicate === predicate && fact.object === `<${object}>`,
      ),
    )
    expect(facts).toHaveLength(2)
    expect(
      facts
        .map((fact) => [fact.subject, fact.predicate, fact.object])
        .sort((a, b) => canonical(a).localeCompare(canonical(b))),
    ).toEqual(expected.map(([subject, predicate, object]) => [subject, predicate, `<${object}>`]))
    expect(
      facts.every(
        (fact) => fact.owner === null && fact.source_row === null && fact.managed_value === null,
      ),
    ).toBe(true)
    expect(
      await graph
        .locator('li[data-fact-id]')
        .evaluateAll((nodes) => nodes.map((node) => node.getAttribute('data-fact-id')).sort()),
    ).toEqual(facts.map((fact) => fact.id).sort())
    await expect(graph).toContainText('人工来源')
    await expect(
      graph.getByRole('img', { name: '来自同快照事实记录的有向关系', exact: true }),
    ).toBeVisible()
    await expect(panel.getByRole('region', { name: '当前页 IRI 关联', exact: true })).toContainText(
      '不推断本体关系',
    )
    const binding = await readBinding(page, job)
    assertBinding(binding, job, draft, id, 2)
    await assertUiRows(
      panel,
      ['alarm'],
      [[alarm]],
      0,
      job.resultRef!.resultId,
      binding.descriptor.identity.payloadSha256,
    )
    await downloadCsv(page, panel, '导出当前页 CSV', csv(['alarm'], [[alarm]]))

    // A query-definition edit changes the input namespace. The old result remains
    // readable, but the current read must never supply edges to its stale graph.
    const changed = { ...draft, description: '只改说明，旧结果保留原输入；不能借当前库补旧图。' }
    const edited = await saveDefinition(page, workspace, id, changed, {
      draft,
      previousJobId: job.jobId,
    })
    const historyLane = await restore(page, workspace, job)
    const historyPanel = resultPanel(historyLane)
    await button(historyLane, '读取 SELECT 结果第一页').click()
    const heldGraph = historyPanel.getByRole('region', {
      name: '结果输入的局部关系图',
      exact: true,
    })
    await expect(historyPanel).toContainText(`QUERY_CHANGED · query:${id} · 1 → 2`)
    await expect(heldGraph).toContainText('历史或过期结果尚无对应快照的关系事实来源')
    await expect(
      heldGraph.getByRole('img', { name: '来自同快照事实记录的有向关系', exact: true }),
    ).toHaveCount(0)
    await assertUiRows(
      historyPanel,
      ['alarm'],
      [[alarm]],
      0,
      job.resultRef!.resultId,
      binding.descriptor.identity.payloadSha256,
    )
    evidence.initial = initial
    evidence.saved = saved
    evidence.originalJob = job
    evidence.sameInputBinding = binding
    evidence.expectedDirectedTriples = expected
    evidence.sourceFactRecords = facts
    evidence.edited = edited
    evidence.boundary =
      'Actual same-input manual asserted graph and stale hold via real UI; mapped behavior is consumer-unit evidence only. No inferred edge, extra write API, historical graph source or model proof.'
  })
})
