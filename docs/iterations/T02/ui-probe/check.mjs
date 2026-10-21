import { chromium, expect } from '@playwright/test'
import { fileURLToPath } from 'node:url'
import { writeFile, readFile } from 'node:fs/promises'
import { resolve, extname } from 'node:path'
import { execFileSync } from 'node:child_process'

// Headless only. Do not invoke the Electron test runner, native UI or HMR.
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
  await open()
  await load()
  await expect(page.getByRole('textbox', { name: '名称 1', exact: true })).toHaveValue('设备')
  await expect(page.getByRole('textbox', { name: '名称 2', exact: true })).toHaveValue('Equipment')
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
    ['Equipment', 'en'],
  ])
  expect(received.object.synonyms).toEqual(['机器', '备件'])
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
    path: fileURLToPath(new URL('../../../reviews/T02/ui-desktop.png', import.meta.url)),
    fullPage: true,
  })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({
    path: fileURLToPath(new URL('../../../reviews/T02/ui-mobile.png', import.meta.url)),
    fullPage: true,
  })
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  evidence.push('desktop_and_mobile_graph_render_no_horizontal_overflow')
  await writeFile(
    new URL('../../../reviews/T02/ui-probe.json', import.meta.url),
    JSON.stringify(
      {
        mode: 'headless Chromium presentation probe with synthetic callback; no IPC/Store/product integration',
        browser: browser.version(),
        evidence,
      },
      null,
      2,
    ) + '\n',
  )
} finally {
  await browser.close()
}
