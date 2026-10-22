import { chromium, expect } from '@playwright/test'
import { fileURLToPath } from 'node:url'
import { mkdir, writeFile, readFile } from 'node:fs/promises'
import { resolve, extname } from 'node:path'
import { execFileSync } from 'node:child_process'

// Headless only. Do not invoke the Electron test runner, native UI or HMR.
const outputDir = process.env.T02_UI_OUTPUT_DIR
  ? resolve(process.env.T02_UI_OUTPUT_DIR)
  : fileURLToPath(new URL('../../../reviews/T02/', import.meta.url))
await mkdir(outputDir, { recursive: true })
const fixture = JSON.parse(await readFile(new URL('fixture.json', import.meta.url), 'utf8'))
execFileSync(process.execPath, [fileURLToPath(new URL('build.mjs', import.meta.url))], {
  stdio: 'inherit',
})
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.T02_HEADLESS_EXECUTABLE,
})
const evidence = []
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  const root = fileURLToPath(new URL('out/', import.meta.url))
  await page.route('**/*', async (route) => {
    const url = new URL(route.request().url())
    const path = resolve(root, '.' + (url.pathname === '/' ? '/index.html' : url.pathname))
    if (url.hostname !== 't02-ui.invalid' || !path.startsWith(root)) return route.abort()
    const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }
    await route.fulfill({
      body: await readFile(path),
      contentType: types[extname(path)] || 'application/octet-stream',
    })
  })
  const url = 'https://t02-ui.invalid/'
  const open = async () => {
    await page.goto(url)
    await expect(page.getByRole('heading', { name: '本体构建', exact: true })).toBeVisible()
  }
  const load = async () => {
    await page.getByRole('button', { name: '查看 Equipment', exact: true }).click()
    await page.getByRole('button', { name: '将对象载入编辑表单', exact: true }).click()
  }
  const receivedIntent = async () =>
    JSON.parse(await page.getByLabel('探针收到的意图').textContent())
  const expectBase = async (revision = fixture.revision) =>
    expect(JSON.parse(await page.getByLabel('探针收到的基准').textContent())).toEqual({
      project: fixture.project,
      revision,
    })
  await open()
  await load()
  await expect(page.getByRole('textbox', { name: '名称 1', exact: true })).toHaveValue('设备')
  await expect(page.getByRole('textbox', { name: '名称 2', exact: true })).toHaveValue(
    'Equipment\nAsset',
  )
  await page.getByRole('textbox', { name: '名称 2', exact: true }).focus()
  await page
    .getByRole('textbox', { name: '名称 2', exact: true })
    .evaluate((input) => input.setSelectionRange(input.value.length, input.value.length))
  await page.getByRole('textbox', { name: '名称 2', exact: true }).pressSequentially('s')
  await expect(page.getByRole('textbox', { name: '定义 1', exact: true })).toHaveValue(
    '第一行\n第二行',
  )
  // Position only the caret; Enter and text insertion remain real keyboard input.
  await page.getByRole('textbox', { name: '定义 1', exact: true }).focus()
  await page
    .getByRole('textbox', { name: '定义 1', exact: true })
    .evaluate((input) => input.setSelectionRange(input.value.length, input.value.length))
  await page.getByRole('textbox', { name: '定义 1', exact: true }).press('Enter')
  await page.getByRole('textbox', { name: '定义 1', exact: true }).pressSequentially('第三行')
  await page.getByRole('textbox', { name: '同义词（每行一项）', exact: true }).fill('机器')
  await page.getByRole('textbox', { name: '同义词（每行一项）', exact: true }).press('End')
  await page.getByRole('textbox', { name: '同义词（每行一项）', exact: true }).press('Enter')
  await page
    .getByRole('textbox', { name: '同义词（每行一项）', exact: true })
    .pressSequentially('备件')
  await page.getByRole('button', { name: '预览定义修改', exact: true }).click()
  const received = JSON.parse(await page.getByLabel('探针收到的意图').textContent())
  expect(received.object.labels).toEqual([
    ['设备', 'zh'],
    ['Equipment\nAssets', 'en'],
  ])
  expect(received.object.synonyms).toEqual(['机器', '备件'])
  expect(received.object.definitions).toEqual([['第一行\n第二行\n第三行', 'zh']])
  evidence.push('multiline_definition_loaded_and_edited_without_loss')
  await expect(page.getByRole('heading', { name: '修改预览 · 尚未提交' })).toBeVisible()
  evidence.push('multi_language_metadata_preserved')
  await page.getByRole('button', { name: '探针：推进版本', exact: true }).click()
  await expect(page.getByRole('button', { name: '预览定义修改', exact: true })).toBeDisabled()
  await expect(page.getByRole('textbox', { name: '同义词（每行一项）', exact: true })).toHaveValue(
    '机器\n备件',
  )
  await expect(page.getByText('基准已变化，请重新生成预览。旧预览不能确认。')).toBeVisible()
  evidence.push('old_draft_preserved_and_blocked_after_revision_change')
  await page.getByRole('button', { name: '探针：切换项目', exact: true }).click()
  await expect(page.getByRole('textbox', { name: '英文标识', exact: true })).toHaveValue('')
  evidence.push('project_switch_isolates_draft')
  await open()
  await load()
  await page.getByRole('button', { name: '探针：切换延迟', exact: true }).click()
  await page.getByRole('button', { name: '预览定义修改', exact: true }).click()
  await page.getByRole('textbox', { name: '同义词（每行一项）', exact: true }).fill('后续新草稿')
  await page.getByRole('button', { name: '探针：释放回复', exact: true }).click()
  await expect(page.getByRole('heading', { name: '修改预览 · 尚未提交' })).toHaveCount(0)
  evidence.push('late_reply_does_not_replace_new_draft')
  await open()
  await load()
  await page.getByRole('button', { name: '探针：切换延迟', exact: true }).click()
  await page.getByRole('button', { name: '预览定义修改', exact: true }).click()
  await page.getByRole('button', { name: '探针：推进版本', exact: true }).click()
  await page.getByRole('button', { name: '探针：释放回复', exact: true }).click()
  await expect(page.getByText('基准已变化，请重新生成预览。旧预览不能确认。')).toBeVisible()
  await expect(page.getByRole('button', { name: '预览定义修改', exact: true })).toBeDisabled()
  evidence.push('pending_reply_after_revision_change_is_marked_old')
  await open()
  await load()
  await page.getByRole('button', { name: '探针：切换延迟', exact: true }).click()
  await page.getByRole('button', { name: '预览定义修改', exact: true }).click()
  await page.getByRole('button', { name: '探针：切换项目', exact: true }).click()
  await page.getByRole('button', { name: '探针：释放回复', exact: true }).click()
  await expect(page.getByRole('heading', { name: '修改预览 · 尚未提交' })).toHaveCount(0)
  await expect(page.getByRole('textbox', { name: '英文标识', exact: true })).toHaveValue('')
  evidence.push('pending_reply_cannot_cross_project_unmount')
  await open()
  await page.getByRole('button', { name: '类树', exact: true }).click()
  await expect(page.getByRole('button', { name: '设备', exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Alarm', exact: true })).toBeVisible()
  evidence.push('tree_shows_class_objects')

  await open()
  await load()
  await page.getByRole('button', { name: '探针：切换失败', exact: true }).click()
  await page.getByRole('button', { name: '预览定义修改', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('未能生成预览')
  await expect(page.getByRole('heading', { name: '修改预览 · 尚未提交' })).toHaveCount(0)
  evidence.push('failure_never_claims_success')
  await open()
  await page.getByRole('button', { name: '查看 Equipment', exact: true }).click()
  await page.getByRole('button', { name: '查看删除影响', exact: true }).click()
  await expect(page.getByRole('heading', { name: '删除影响', exact: true })).toBeVisible()
  await page.getByRole('button', { name: '探针：推进版本', exact: true }).click()
  await expect(page.getByRole('button', { name: '预览删除（尚不提交）', exact: true })).toHaveCount(
    0,
  )
  evidence.push('stale_delete_impact_blocked')
  await page.getByRole('button', { name: '局部关系图', exact: true }).click()
  await expect(page.getByRole('img', { name: '当前对象及一跳邻居关系图' })).toBeVisible()
  await page.screenshot({
    path: resolve(outputDir, 'ui-desktop.png'),
    fullPage: true,
  })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({
    path: resolve(outputDir, 'ui-mobile.png'),
    fullPage: true,
  })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  evidence.push('desktop_and_mobile_graph_render_no_horizontal_overflow')
  const equipmentEdges = fixture.triples
    .filter((edge) => edge.subject === 'urn:t02:Equipment' || edge.object === '<urn:t02:Equipment>')
    .sort((a, b) => {
      const x = JSON.stringify([a.subject, a.predicate, a.object])
      const y = JSON.stringify([b.subject, b.predicate, b.object])
      return x < y ? -1 : x > y ? 1 : 0
    })
  await expect(
    page.getByText(`仅展示当前对象的一跳关系。显示前 12 条，共 ${equipmentEdges.length} 条。`),
  ).toBeVisible()
  await expect(page.getByRole('list', { name: '邻近关系' }).getByRole('listitem')).toHaveText(
    equipmentEdges
      .slice(0, 12)
      .map((edge) => `${edge.subject} → ${edge.predicate} → ${edge.object}`),
  )
  evidence.push('local_graph_truncation_and_complete_visible_edge_set')
  await page.setViewportSize({ width: 1440, height: 1000 })
  await open()
  const table = page.getByRole('table')
  const expectedObjects = [...fixture.objects].sort((a, b) => a.iri.localeCompare(b.iri))
  const expectedButtons = expectedObjects.map((row) => `查看 ${row.identifier}`)
  await expect(table.getByRole('caption')).toHaveText('对象表 · 共 25 项 · 每页 20 项')
  await expect(page.getByText('第 1 页', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: '上一页', exact: true })).toBeDisabled()
  await expect(page.getByRole('button', { name: '下一页', exact: true })).toBeEnabled()
  await expect(table.getByRole('button')).toHaveText(expectedButtons.slice(0, 20))
  const firstPage = await table.getByRole('button').allTextContents()
  await page.getByRole('button', { name: '下一页', exact: true }).click()
  await expect(page.getByText('第 2 页', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: '下一页', exact: true })).toBeDisabled()
  await expect(page.getByRole('button', { name: '上一页', exact: true })).toBeEnabled()
  await expect(table.getByRole('button')).toHaveText(expectedButtons.slice(20))
  expect([...firstPage, ...(await table.getByRole('button').allTextContents())]).toEqual(
    expectedButtons,
  )
  await page.getByRole('button', { name: '上一页', exact: true }).click()
  await expect(page.getByText('第 1 页', { exact: true })).toBeVisible()
  await expect(table.getByRole('button')).toHaveText(expectedButtons.slice(0, 20))
  evidence.push('25_objects_complete_ordered_set_forward_and_back_pagination')
  await page.getByRole('button', { name: '下一页', exact: true }).click()
  await page.getByRole('textbox', { name: '查找概念', exact: true }).fill('Equipment')
  await expect(page.getByText('第 1 页', { exact: true })).toBeVisible()
  await expect(table.getByRole('button')).toHaveText(['查看 Equipment'])
  await page.getByRole('textbox', { name: '查找概念', exact: true }).fill('不存在的概念')
  await expect(table.getByRole('button')).toHaveCount(0)
  await expect(page.getByText('尚无匹配对象。新建一个类开始建模。')).toBeVisible()
  evidence.push('search_resets_page_and_empty_result_is_explicit')

  // Cover every applicable metadata family using valid class/property/individual shapes.
  for (const identifier of ['Equipment', 'hasAlarm', 'name', '001']) {
    await open()
    const source = fixture.objects.find((row) => row.identifier === identifier)
    await page.getByRole('button', { name: `查看 ${identifier}`, exact: true }).click()
    await page.getByRole('button', { name: '复制定义到新表单', exact: true }).click()
    await expect(page.getByRole('heading', { name: '新建定义', exact: true })).toBeVisible()
    await expect(page.getByRole('textbox', { name: '稳定 IRI', exact: true })).toHaveValue('')
    await expect(page.getByRole('textbox', { name: '英文标识', exact: true })).toHaveValue('')
    await page.getByRole('textbox', { name: '稳定 IRI', exact: true }).fill(`${source.iri}_copy`)
    await page.getByRole('textbox', { name: '英文标识', exact: true }).fill(`${identifier}_copy`)
    await page
      .getByRole('textbox', { name: '示例（每行一项）', exact: true })
      .fill([...source.examples, '复制后补充'].join('\n'))
    await page.getByRole('button', { name: '预览定义修改', exact: true }).click()
    expect(await receivedIntent()).toEqual({
      action: 'create',
      object: {
        ...source,
        iri: `${source.iri}_copy`,
        identifier: `${identifier}_copy`,
        examples: [...source.examples, '复制后补充'],
      },
    })
    await expectBase()
  }
  evidence.push('copy_all_metadata_families_edit_then_create_complete_definition')
  await page.getByRole('button', { name: '新建概念', exact: true }).click()
  await expect(page.getByRole('textbox', { name: '稳定 IRI', exact: true })).toHaveValue('')
  await expect(page.getByRole('textbox', { name: '示例（每行一项）', exact: true })).toHaveValue('')
  evidence.push('new_form_clears_copied_draft')

  await open()
  const fact = { subject: 'urn:t02:001', predicate: 'urn:t02:hasAlarm', object: '<urn:t02:A01>' }
  const fillFact = async (value) => {
    await page.getByRole('textbox', { name: '主体个体 IRI', exact: true }).fill(value.subject)
    await page.getByRole('textbox', { name: '属性 IRI', exact: true }).fill(value.predicate)
    await page.getByRole('textbox', { name: 'RDF 对象', exact: true }).fill(value.object)
  }
  await fillFact(fact)
  for (const [action, button] of [
    ['assert', '预览新增事实'],
    ['retract', '预览移除事实'],
  ]) {
    await page.getByRole('button', { name: button, exact: true }).click()
    expect(await receivedIntent()).toEqual({ action, fact })
    await expectBase()
    await expect(page.getByRole('heading', { name: '修改预览 · 尚未提交' })).toBeVisible()
  }
  evidence.push('assert_and_retract_exact_fact_and_request_base')
  await page.getByRole('button', { name: '探针：推进版本', exact: true }).click()
  await expect(page.getByRole('textbox', { name: 'RDF 对象', exact: true })).toHaveValue(
    fact.object,
  )
  await expect(page.getByText('事实草稿基准已变化，请重新填写当前版本的事实。')).toBeVisible()
  await expect(page.getByRole('button', { name: '预览新增事实', exact: true })).toBeDisabled()
  await expect(page.getByRole('button', { name: '预览移除事实', exact: true })).toBeDisabled()
  await page.getByRole('button', { name: '清空事实表单并读取当前版本', exact: true }).click()
  for (const name of ['主体个体 IRI', '属性 IRI', 'RDF 对象'])
    await expect(page.getByRole('textbox', { name, exact: true })).toHaveValue('')
  await fillFact(fact)
  await page.getByRole('button', { name: '预览新增事实', exact: true }).click()
  expect(await receivedIntent()).toEqual({ action: 'assert', fact })
  await expectBase(fixture.revision + 1)
  evidence.push('fact_draft_preserved_blocked_until_explicit_current_base_reset')
  await page.getByRole('button', { name: '探针：切换项目', exact: true }).click()
  for (const name of ['主体个体 IRI', '属性 IRI', 'RDF 对象'])
    await expect(page.getByRole('textbox', { name, exact: true })).toHaveValue('')
  await fillFact(fact)
  await page.getByRole('button', { name: '预览新增事实', exact: true }).click()
  expect(JSON.parse(await page.getByLabel('探针收到的基准').textContent())).toEqual({
    project: 'project-b',
    revision: fixture.revision + 1,
  })
  evidence.push('project_switch_clears_fact_draft_and_rebinds_request_base')

  await open()
  const badFact = { ...fact, object: 'not a canonical n3 term' }
  await fillFact(badFact)
  // Simulate the owning service rejecting this bad input; this is not a second RDF parser.
  await page.getByRole('button', { name: '探针：切换失败', exact: true }).click()
  for (const [action, button] of [
    ['assert', '预览新增事实'],
    ['retract', '预览移除事实'],
  ]) {
    await page.getByRole('button', { name: button, exact: true }).click()
    expect(await receivedIntent()).toEqual({ action, fact: badFact })
    await expectBase()
    await expect(page.getByRole('alert')).toHaveText(
      '未能生成预览。正式项目未获保存确认，请检查输入或重新读取项目。',
    )
    await expect(page.getByRole('heading', { name: '修改预览 · 尚未提交' })).toHaveCount(0)
  }
  evidence.push('bad_n3_input_synthetic_service_rejection_fixed_message_assert_and_retract')
  await open()
  await page.getByRole('button', { name: '查看 Equipment', exact: true }).click()
  await page.getByRole('button', { name: '查看删除影响', exact: true }).click()
  const baselineText = `基准快照（项目版本 ${fixture.revision}）中的引用；包括本次修改计划将解除的引用。`
  await expect(page.getByText(baselineText, { exact: true })).toBeVisible()
  await expect(
    page.getByText('constraint:c1 引用了设备类（合成引用）', { exact: true }),
  ).toBeVisible()
  await page.getByRole('button', { name: '预览删除（尚不提交）', exact: true }).click()
  expect(await receivedIntent()).toEqual({ action: 'delete', iri: 'urn:t02:Equipment' })
  await expectBase()
  await expect(
    page.getByRole('region', { name: '修改预览', exact: true }).getByText(baselineText),
  ).toBeVisible()
  evidence.push('delete_impact_and_preview_explicit_baseline_reference_semantics')
  await writeFile(
    resolve(outputDir, 'ui-probe.json'),
    JSON.stringify(
      {
        mode: 'headless Chromium presentation probe with synthetic callback; no IPC/Store/product integration',
        browser: browser.version(),
        objectCount: fixture.objects.length,
        completedCheckCount: evidence.length,
        evidence,
      },
      null,
      2,
    ) + '\n',
  )
  console.log(JSON.stringify({ completedCheckCount: evidence.length, evidence }))
} catch (error) {
  await writeFile(
    resolve(outputDir, 'ui-probe-failure.json'),
    JSON.stringify(
      { completedCheckCount: evidence.length, evidence, error: String(error) },
      null,
      2,
    ) + '\n',
  )
  throw error
} finally {
  await browser.close()
}
