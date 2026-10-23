import {
  test,
  expect,
  _electron as electron,
  type ElectronApplication,
  type Locator,
  type Page,
} from '@playwright/test'
import { resolve } from 'node:path'
import type { BridgeResult, MainlineProjectReadDTO } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'

// Test-side constants and encoding only. No renderer/domain adapter is imported.
const RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
const RDFS = 'http://www.w3.org/2000/01/rdf-schema#'
const OWL = 'http://www.w3.org/2002/07/owl#'
const UUID = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
const uuid = new RegExp(`^${UUID}$`)
const hash = /^[0-9a-f]{64}$/
const fields = {
  identifier: 'T02_Asset',
  labels: [
    ['  运维"设备"\n第二行😀  ', 'zh'],
    ['  Asset "A"  ', 'en'],
  ],
  definitions: [
    ['  第一行\n第二行"原文"  ', 'zh'],
    ['  An asset definition.  ', 'en'],
  ],
  synonyms: ['  资产 A  ', '设备别称\n"二"'],
  examples: ['  泵站 "甲"  ', 'Line 1\nLine 2'],
} satisfies {
  identifier: string
  labels: [string, string][]
  definitions: [string, string][]
  synonyms: string[]
  examples: string[]
}
type Definition = MainlineProjectReadDTO['domain']['state']['definitions'][number]
type DiffRow = {
  resource: string[]
  before: Definition | null
  after: Definition | null
}
function data<T>(reply: BridgeResult<T>): T {
  if (!reply.ok) throw new Error(`Actual named read refused: ${JSON.stringify(reply.error)}`)
  return reply.data
}
function canonical(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    const encoded = JSON.stringify(value)
    if (encoded === undefined) throw new Error('Invalid independent fixture')
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
// Deliberately literal N3 expectations, not calls to T02 literalN3/entityRdf.
function expectedValue(iri: string, owl: boolean) {
  return {
    triples: [
      { subject: iri, predicate: RDF + 'type', object: `<${owl ? OWL : RDFS}Class>` },
      {
        subject: iri,
        predicate: RDFS + 'label',
        object: '"""  运维"设备"\n第二行😀  """@zh',
      },
      { subject: iri, predicate: RDFS + 'label', object: '"  Asset \\"A\\"  "@en' },
      {
        subject: iri,
        predicate: RDFS + 'comment',
        object: '"""  第一行\n第二行"原文"  """@zh',
      },
      { subject: iri, predicate: RDFS + 'comment', object: '"  An asset definition.  "@en' },
    ],
    entityMetadata: { entityMetadataVersion: 1, entities: { [iri]: fields } },
  }
}
function record(id: string, value: unknown): Definition {
  return { layer: 'ontology', id, payload: canonical(value) }
}
async function readCurrent(page: Page): Promise<MainlineProjectReadDTO> {
  return data(
    await page.evaluate(() => window.ontolearn!.readProject({ editor: 'ontology-transaction' })),
  )
}
function ontology(page: Page) {
  return page.getByRole('region', { name: '本体项目编辑', exact: true })
}
async function enterOntology(page: Page) {
  await page.getByRole('link', { name: '本体构建', exact: true }).click()
  const panel = ontology(page)
  await expect(panel).toBeVisible()
  await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
  await expect(panel.getByRole('region', { name: '本体编辑表单', exact: true })).toBeVisible()
  return panel
}
async function fillMetadata(panel: Locator) {
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  await form.getByLabel('英文标识', { exact: true }).fill(fields.identifier)
  for (const [title, pairs] of [
    ['名称', fields.labels],
    ['定义', fields.definitions],
  ] as const) {
    const group = form.getByRole('group', { name: `${title}（保留所有语言）`, exact: true })
    for (const [index, [text, language]] of pairs.entries()) {
      await group.getByRole('button', { name: `添加${title}`, exact: true }).click()
      await group.getByRole('textbox', { name: `${title} ${index + 1}`, exact: true }).fill(text)
      await group.getByLabel(`语言标签 ${index + 1}`, { exact: true }).fill(language)
    }
  }
  for (const [title, values] of [
    ['同义词', fields.synonyms],
    ['示例', fields.examples],
  ] as const) {
    const group = form.getByRole('group', { name: `${title}（保留原文与顺序）`, exact: true })
    for (const [index, text] of values.entries()) {
      await group.getByRole('button', { name: `添加${title}`, exact: true }).click()
      await group.getByRole('textbox', { name: `${title} ${index + 1}`, exact: true }).fill(text)
    }
  }
}
async function assertForm(panel: Locator, iri: string) {
  const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
  await expect(form.getByLabel('稳定 IRI', { exact: true })).toHaveValue(iri)
  await expect(form.getByLabel('英文标识', { exact: true })).toHaveValue(fields.identifier)
  for (const [title, pairs] of [
    ['名称', fields.labels],
    ['定义', fields.definitions],
  ] as const) {
    const group = form.getByRole('group', { name: `${title}（保留所有语言）`, exact: true })
    await expect(group.getByRole('textbox')).toHaveCount(4)
    for (const [index, [text, language]] of pairs.entries()) {
      await expect(
        group.getByRole('textbox', { name: `${title} ${index + 1}`, exact: true }),
      ).toHaveValue(text)
      await expect(group.getByLabel(`语言标签 ${index + 1}`, { exact: true })).toHaveValue(language)
    }
  }
  for (const [title, values] of [
    ['同义词', fields.synonyms],
    ['示例', fields.examples],
  ] as const) {
    const group = form.getByRole('group', { name: `${title}（保留原文与顺序）`, exact: true })
    await expect(group.getByRole('textbox')).toHaveCount(2)
    for (const [index, text] of values.entries())
      await expect(
        group.getByRole('textbox', { name: `${title} ${index + 1}`, exact: true }),
      ).toHaveValue(text)
  }
}
async function displayedDiff(panel: Locator): Promise<unknown[]> {
  const diff = panel.getByRole('region', { name: '完整事务差异', exact: true })
  await expect(diff).toBeVisible()
  await expect(
    diff.getByRole('button', { name: '我已核对完整差异，确认提交', exact: true }),
  ).toBeEnabled()
  const raw = await diff.locator('pre').textContent()
  if (raw === null) throw new Error('Actual complete Diff is missing')
  const rows: unknown = JSON.parse(raw)
  if (!Array.isArray(rows)) throw new Error('Complete Diff must be an array')
  return rows
}
async function inspectDiff(panel: Locator, expected: DiffRow[]) {
  expect(await displayedDiff(panel)).toEqual(expected)
  await expect(panel.getByRole('region', { name: '完整事务差异', exact: true })).toContainText(
    `全部 ${expected.length} 项；`,
  )
}
async function confirmAndRead(page: Page, before: MainlineProjectReadDTO, revision: number) {
  const panel = ontology(page)
  await panel
    .getByRole('region', { name: '完整事务差异', exact: true })
    .getByRole('button', { name: '我已核对完整差异，确认提交', exact: true })
    .click()
  const receipt = panel.getByRole('region', { name: '已提交回执', exact: true })
  const pending = panel.getByRole('region', { name: '原操作状态', exact: true })
  // A terminal word is not a saved receipt. Ask the real page to reconcile
  // the original operation when its first immediate lookup preceded commit.
  let needsReconciliation = false
  await expect
    .poll(async () => {
      if (await receipt.count()) {
        const text = await receipt.textContent()
        if (text?.includes(`提交版本 ${revision}。`)) return 'receipt'
      }
      if (await pending.count()) {
        const text = await pending.textContent()
        if (text?.includes('succeeded')) {
          needsReconciliation = true
          return 'terminal-needs-reconciliation'
        }
      }
      return 'waiting'
    })
    .not.toBe('waiting')
  if (needsReconciliation) {
    const reconcile = pending.getByRole('button', { name: '核对原操作与提交回执', exact: true })
    await expect(reconcile).toBeEnabled()
    await reconcile.click()
  }
  await expect(receipt).toContainText(`提交版本 ${revision}。`)
  await expect(receipt).toContainText(`当前已读版本 ${revision}。`)
  await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
  await expect(panel.getByRole('region', { name: '原操作状态', exact: true })).toHaveCount(0)
  const text = await receipt.locator('p').first().textContent()
  const operationId = text?.match(new RegExp(`操作 (${UUID})，`))?.[1]
  if (!operationId) throw new Error('Committed UI receipt lacks its original operation identity')
  // Read-only named observation after the UI has completed its computing window.
  const marker = data(await page.evaluate((id) => window.ontolearn!.getOperation(id), operationId))
  if (!marker || typeof marker.jobId !== 'string') throw new Error('Missing actual original marker')
  expect(marker.jobId).toMatch(uuid)
  const job = data(await page.evaluate((id) => window.ontolearn!.getJob(id), marker.jobId))
  const after = await readCurrent(page)
  expect(after.projectId).toBe(before.projectId)
  expect(after.domain.projectRevision).toBe(revision)
  expect(after.inputSnapshotId).toMatch(hash)
  expect(after.inputSnapshotId).not.toBe(before.inputSnapshotId)
  expect(marker).toEqual({
    projectId: before.projectId,
    operationId,
    jobId: job.jobId,
    projectRevision: revision,
    beforeSnapshotId: before.inputSnapshotId,
    afterSnapshotId: after.inputSnapshotId,
    planHash: expect.stringMatching(hash),
  })
  expect(job).toMatchObject({
    projectId: before.projectId,
    operationId,
    capability: 'changeset.commit',
    state: 'succeeded',
    error: null,
    inputSnapshotId: before.inputSnapshotId,
  })
  expect(job.input).toEqual({
    inputSnapshotId: before.inputSnapshotId,
    scope: 'asserted',
    definitionId: 'changeset',
    parametersHash: job.parametersHash,
    derivedResultIds: [],
    preparedPlanRef: expect.stringMatching(hash),
  })
  expect(job.confirmationRef).toEqual(expect.any(String))
  expect(job.confirmationRef).not.toBe('')
  expect(job.commitProgress).toEqual({
    mode: 'atomic',
    operationId,
    marker: {
      projectRevision: revision,
      beforeSnapshotId: before.inputSnapshotId,
      afterSnapshotId: after.inputSnapshotId,
      planHash: marker.planHash,
    },
  })
  return { after, job, marker }
}
function options() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.I04_TEST_FIXTURE
  return {
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
    acceptDownloads: true,
  }
}
async function createProject(page: Page, example: boolean) {
  await page.getByTestId('project-name').fill(example ? 'T02 真实旧home编辑' : 'T02 真实五字段')
  await page.getByTestId(example ? 'project-create-example' : 'project-create').click()
  await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
    '项目已创建并打开',
  )
  await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
  await expect(page.getByTestId('selected-project-version')).toContainText(
    `版本 ${example ? 1 : 0}`,
  )
}

test.describe('T02 actual mainline ontology UI', () => {
  test('five fields, complete Diff, original receipt, Undo/Redo and owned restart', async () => {
    // Same explicit60s allowance as the existing real mainline restart chain; no retries added.
    test.setTimeout(60000)
    const launchOptions = options()
    let application: ElectronApplication | undefined = await launchIsolatedDesktop(launchOptions)
    const evidence: Record<string, unknown> = {}
    let stage = 'launch'
    try {
      let page = await application.firstWindow()
      stage = 'create blank through UI'
      await createProject(page, false)
      const initial = await readCurrent(page)
      expect(initial.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })
      const iri = 'urn:t02:e2e:Asset'
      let panel = await enterOntology(page)
      await panel.getByRole('button', { name: '新建概念', exact: true }).click()
      const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
      await form.getByRole('combobox', { name: '类型', exact: true }).selectOption('class')
      await form.getByRole('combobox', { name: '类声明', exact: true }).selectOption('rdfs')
      await form.getByLabel('稳定 IRI', { exact: true }).fill(iri)
      await fillMetadata(panel)
      await assertForm(panel, iri)
      stage = 'read independent complete create Diff before confirmation'
      await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
      const rows = await displayedDiff(panel)
      expect(rows).toHaveLength(1)
      // Only the unpredictable home identity comes from the actual document.
      const identity = rows[0] as { resource?: unknown }
      expect(identity.resource).toEqual(['definition', 'ontology', expect.any(String)])
      const home = (identity.resource as string[])[2]!
      expect(home).toMatch(new RegExp(`^t02-${UUID}$`))
      const expected = record(home, expectedValue(iri, false))
      const createDiff = [
        { resource: ['definition', 'ontology', home], before: null, after: expected },
      ]
      await inspectDiff(panel, createDiff)
      expect((await readCurrent(page)).domain).toEqual(initial.domain)
      stage = 'explicit UI confirmation and original durable receipt'
      const committed = await confirmAndRead(page, initial, 1)
      expect(committed.after.domain.state).toEqual({
        definitions: [expected],
        facts: [],
        mappingState: {},
      })
      await panel.getByRole('button', { name: '读取当前项目', exact: true }).click()
      await expect(panel.getByRole('button', { name: '读取当前项目', exact: true })).toBeEnabled()
      expect((await readCurrent(page)).domain).toEqual(committed.after.domain)

      stage = 'actual Undo with independent reverse complete Diff'
      await panel.getByRole('button', { name: '预览撤销本次修改', exact: true }).click()
      await inspectDiff(panel, [
        { resource: ['definition', 'ontology', home], before: expected, after: null },
      ])
      const undone = await confirmAndRead(page, committed.after, 2)
      expect(undone.after.domain.state).toEqual(initial.domain.state)
      expect(undone.job.operationId).not.toBe(committed.job.operationId)
      stage = 'actual Undo-of-Undo with independent forward Diff'
      await panel.getByRole('button', { name: '预览撤销本次修改', exact: true }).click()
      await inspectDiff(panel, createDiff)
      const redone = await confirmAndRead(page, undone.after, 3)
      expect(redone.after.domain.state).toEqual(committed.after.domain.state)
      expect(new Set([committed.job.jobId, undone.job.jobId, redone.job.jobId]).size).toBe(3)
      expect(
        new Set([committed.job.operationId, undone.job.operationId, redone.job.operationId]).size,
      ).toBe(3)
      await panel.getByRole('button', { name: `查看 ${fields.identifier}`, exact: true }).click()
      await panel.getByRole('button', { name: '将对象载入编辑表单', exact: true }).click()
      await assertForm(panel, iri)
      evidence.initial = initial
      evidence.independentDiff = createDiff
      evidence.committed = committed
      evidence.undone = undone
      evidence.redone = redone
      const owned = await application.evaluate(({ app }) => ({
        userData: app.getPath('userData'),
        sessionData: app.getPath('sessionData'),
        pid: process.pid,
      }))
      expect(owned.sessionData).toBe(owned.userData)
      evidence.owned = owned
      await page.screenshot({ path: test.info().outputPath('t02-m-before-restart.png') })
      await application.close()
      application = undefined
      stage = 'restart only this owned profile and explicitly open same project'
      application = await electron.launch({
        ...launchOptions,
        args: [...launchOptions.args, `--user-data-dir=${owned.userData}`],
      })
      expect(await application.evaluate(({ app }) => app.getPath('userData'))).toBe(owned.userData)
      expect(await application.evaluate(({ app }) => app.getPath('sessionData'))).toBe(
        owned.userData,
      )
      page = await application.firstWindow()
      await page.getByTestId('project-list-refresh').click()
      await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
      await page
        .locator(`[data-testid="project-open"][data-project-id="${initial.projectId}"]`)
        .click()
      await expect(page.getByTestId('selected-project-version')).toContainText('版本 3')
      await expect(page.getByTestId('project-list-refresh')).toBeEnabled()
      panel = await enterOntology(page)
      await panel.getByRole('button', { name: `查看 ${fields.identifier}`, exact: true }).click()
      await panel.getByRole('button', { name: '将对象载入编辑表单', exact: true }).click()
      await assertForm(panel, iri)
      const reopened = await readCurrent(page)
      expect(reopened.domain).toEqual(redone.after.domain)
      expect(reopened.inputSnapshotId).toBe(redone.after.inputSnapshotId)
      for (const original of [committed, undone, redone]) {
        expect(
          data(await page.evaluate((id) => window.ontolearn!.getJob(id), original.job.jobId)),
        ).toEqual(original.job)
        expect(
          data(
            await page.evaluate(
              (id) => window.ontolearn!.getOperation(id),
              original.job.operationId,
            ),
          ),
        ).toEqual(original.marker)
      }
      evidence.reopened = reopened
      await page.screenshot({ path: test.info().outputPath('t02-m-after-restart.png') })
      stage = 'completed'
    } finally {
      try {
        await test.info().attach('t02-real-m-undo-restart', {
          body: JSON.stringify({ stage, ...evidence }, null, 2),
          contentType: 'application/json',
        })
      } finally {
        await application?.close()
      }
    }
  })

  test('edit real example home, preserve other material, then query through T04 UI', async () => {
    test.setTimeout(60000)
    const application = await launchIsolatedDesktop(options())
    const evidence: Record<string, unknown> = {}
    let stage = 'launch'
    try {
      const page = await application.firstWindow()
      await createProject(page, true)
      const initial = await readCurrent(page)
      const iri = 'urn:ontolearn:learning:Equipment'
      const home = 'equipment-maintenance-00'
      const oldValue = {
        triples: [{ subject: iri, predicate: RDF + 'type', object: `<${OWL}Class>` }],
        singleValuedPredicates: ['urn:ontolearn:learning:workOrderStatus'],
      }
      const before = record(home, oldValue)
      expect(initial.domain.state.definitions.filter((d) => d.layer === 'ontology')).toHaveLength(
        10,
      )
      expect(initial.domain.state.definitions).toHaveLength(11)
      expect(initial.domain.state.facts).toHaveLength(18)
      expect(
        initial.domain.state.definitions.find((d) => d.layer === 'ontology' && d.id === home),
      ).toEqual(before)
      const panel = await enterOntology(page)
      stage = 'discover existing entity by actual visible detail IRI'
      const browser = panel.getByRole('region', { name: '对象浏览', exact: true })
      await expect(browser.locator('tbody tr')).toHaveCount(16)
      const choices = browser.getByRole('button', { name: '查看', exact: true })
      const count = await choices.count()
      expect(count).toBe(16)
      let selected = false
      for (let index = 0; index < count; index++) {
        await choices.nth(index).click()
        const actual = await panel
          .getByRole('article', { name: '选中对象详情', exact: true })
          .locator('code')
          .textContent()
        if (actual === iri) {
          selected = true
          break
        }
      }
      expect(selected).toBe(true)
      await panel.getByRole('button', { name: '将对象载入编辑表单', exact: true }).click()
      const form = panel.getByRole('region', { name: '本体编辑表单', exact: true })
      await expect(form.getByLabel('稳定 IRI', { exact: true })).toHaveValue(iri)
      await expect(form.getByLabel('稳定 IRI', { exact: true })).toBeDisabled()
      await expect(form.getByRole('combobox', { name: '类声明', exact: true })).toHaveValue('owl')
      await fillMetadata(panel)
      const newValue = {
        ...expectedValue(iri, true),
        singleValuedPredicates: ['urn:ontolearn:learning:workOrderStatus'],
      }
      const after = record(home, newValue)
      stage = 'complete independent legacy-home Diff and explicit confirmation'
      await form.getByRole('button', { name: '预览定义修改', exact: true }).click()
      await inspectDiff(panel, [{ resource: ['definition', 'ontology', home], before, after }])
      expect((await readCurrent(page)).domain).toEqual(initial.domain)
      const committed = await confirmAndRead(page, initial, 2)
      expect(committed.after.domain.state.facts).toEqual(initial.domain.state.facts)
      expect(committed.after.domain.state.mappingState).toEqual(initial.domain.state.mappingState)
      expect(committed.after.domain.state.definitions.filter((d) => d.id !== home)).toEqual(
        initial.domain.state.definitions.filter((d) => d.id !== home),
      )
      expect(committed.after.domain.state.definitions.find((d) => d.id === home)).toEqual(after)
      // Assert original OWL lexical spelling, not just an RDF-equivalent type.
      expect(JSON.parse(after.payload).triples[0]).toEqual(oldValue.triples[0])
      evidence.initial = initial
      evidence.independentDiff = [{ resource: ['definition', 'ontology', home], before, after }]
      evidence.committed = committed
      stage = 'load existing managed query through actual T04 controls'
      await page.getByRole('link', { name: '本体查询', exact: true }).click()
      const query = page.getByRole('region', { name: '本体查询工作台', exact: true })
      const notice = query.locator('p[role="status"][aria-live="polite"]')
      await query.getByRole('button', { name: '读取项目与持久工作草稿', exact: true }).click()
      await expect(notice).toHaveText('项目与持久工作草稿已读回；工作草稿不代表正式查询定义。')
      await query
        .getByRole('combobox', { name: '已提交查询', exact: true })
        .selectOption('unclosed-high')
      const consent = query.getByRole('checkbox', {
        name: '我已保留当前编辑，允许重新载入或新建替换它',
        exact: true,
      })
      await expect(consent).toBeVisible()
      await consent.check()
      const load = query.getByRole('button', { name: '按所选当前/历史输入载入定义', exact: true })
      await expect(load).toBeEnabled()
      await load.click()
      await expect(notice).toHaveText('已载入真实受管定义；后续编辑需先正式提交。')
      const sparql =
        'PREFIX l: <urn:ontolearn:learning:>\n' +
        'SELECT ?alarm WHERE { ?equipment a l:Equipment ; l:alarm ?alarm . ' +
        '?alarm l:level "High" ; l:status "Open" . } ORDER BY ?alarm'
      await expect(query.getByRole('textbox', { name: '可见 SPARQL', exact: true })).toHaveValue(
        sparql,
      )
      await expect(query.getByRole('combobox', { name: '执行输入', exact: true })).toHaveValue(
        'current',
      )
      await query.getByRole('button', { name: '执行已载入且未改变的受管定义', exact: true }).click()
      const task = query.getByRole('region', { name: '真实查询或提交任务', exact: true })
      await expect(task.locator('code')).toHaveText(uuid)
      const queryJobId = await task.locator('code').textContent()
      if (!queryJobId) throw new Error('Actual T04 UI did not expose its original Job')
      await expect(task).toContainText('：succeeded；')
      await task.getByRole('button', { name: '刷新任务、原操作与固定结果', exact: true }).click()
      await expect(notice).toHaveText('已取得真实结果描述；按固定引用分别读取文本与结果页。')
      const result = query.getByRole('region', { name: '查询结果', exact: true })
      await expect(result).toContainText('完整结果共 1 行')
      await query.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true }).click()
      const table = result.getByRole('table')
      await expect(table.getByRole('columnheader')).toHaveText(['alarm'])
      await expect(table.locator('tbody tr')).toHaveCount(1)
      await expect(table.locator('tbody td > span')).toHaveText([
        'urn:ontolearn:learning:alarm/A01',
      ])
      await table.getByText('RDF 原文', { exact: true }).click()
      await expect(table.locator('tbody code')).toHaveText('<urn:ontolearn:learning:alarm/A01>')
      // Wait for that page's real computation to finish before the next read.
      await expect(
        query.getByRole('button', { name: '读取 SELECT 结果第一页', exact: true }),
      ).toBeEnabled()
      await query.getByRole('button', { name: '读取执行文本第一页', exact: true }).click()
      await result.getByText('本次实际执行的 SPARQL', { exact: true }).click()
      await expect(result.locator('pre')).toHaveText(sparql)
      await expect(
        query.getByRole('button', { name: '读取执行文本第一页', exact: true }),
      ).toBeEnabled()
      const job = data(await page.evaluate((id) => window.ontolearn!.getJob(id), queryJobId))
      expect(job).toMatchObject({
        projectId: initial.projectId,
        capability: 'query.execute',
        state: 'succeeded',
        error: null,
        inputSnapshotId: committed.after.inputSnapshotId,
        confirmationRef: null,
      })
      expect(job.input).toEqual({
        inputSnapshotId: committed.after.inputSnapshotId,
        scope: 'asserted',
        definitionId: 'unclosed-high',
        parametersHash: job.parametersHash,
        derivedResultIds: [],
        preparedPlanRef: null,
      })
      expect(job.resultRef).toEqual({
        resultId: expect.stringMatching(uuid),
        inputSnapshotId: committed.after.inputSnapshotId,
      })
      expect(job.commitProgress).toEqual({ mode: 'none' })
      expect((await readCurrent(page)).domain).toEqual(committed.after.domain)
      evidence.queryJob = job
      await page.screenshot({ path: test.info().outputPath('t02-m-to-real-query.png') })
      stage = 'completed'
    } finally {
      try {
        await test.info().attach('t02-existing-home-to-t04-query', {
          body: JSON.stringify({ stage, ...evidence }, null, 2),
          contentType: 'application/json',
        })
      } finally {
        await application.close()
      }
    }
  })
})
