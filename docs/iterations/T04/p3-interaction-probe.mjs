// Real DOM interaction with the isolated QueryPage fixture. No App/IPC/Store/CSP claim.
import { chromium, expect } from '@playwright/test'
import react from '@vitejs/plugin-react'
import { build } from 'vite'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..')
const runName = process.argv[3]
if (!runName || !/^[a-z0-9-]+$/.test(runName)) throw new Error('Pass a unique evidence run name.')
const runtime = path.join(root, 'test-results/t04-p3-repair/browser', runName)
if (existsSync(runtime)) throw new Error('Preserve existing browser evidence; use a new run name.')
const output = path.join(runtime, 'fixture-build')
const executablePath = process.argv[2]
if (!executablePath || !existsSync(executablePath))
  throw new Error('Pass the installed browser executable path; this probe never downloads one.')
mkdirSync(runtime, { recursive: true })
await build({
  root,
  configFile: false,
  plugins: [react()],
  define: { 'process.env.NODE_ENV': JSON.stringify('production') },
  build: {
    outDir: output,
    emptyOutDir: true,
    minify: false,
    lib: {
      entry: path.join(root, 'tests/fixtures/query/p3-interaction.tsx'),
      name: 'T04QueryFixture',
      formats: ['iife'],
      fileName: () => 'fixture.js',
    },
  },
})
const javascript = readFileSync(path.join(output, 'fixture.js'), 'utf8')
const styles = readdirSync(output)
  .filter((name) => name.endsWith('.css'))
  .map((name) => readFileSync(path.join(output, name), 'utf8'))
  .join('\n')
const browser = await chromium.launch({ executablePath, headless: true })
const context = await browser.newContext({ offline: true, viewport: { width: 1440, height: 1000 } })
const requests = []
const pageErrors = []
const checks = []
await context.route('**/*', async (route) => {
  requests.push(route.request().url())
  await route.abort()
})
await context.tracing.start({ screenshots: true, snapshots: true, sources: false })
const generate = (page) => page.getByRole('button', { name: '生成可见 SPARQL 草稿', exact: true })
const prime = async (page) => {
  await page.getByRole('button', { name: '模板：未闭环高危告警', exact: true }).click()
  await expect(page.getByRole('combobox', { name: /^选择对象/u })).toHaveValue('urn:ClassA')
  await expect(page.getByRole('checkbox', { checked: true })).toHaveCount(2)
  await expect(page.getByLabel('条件 1 属性', { exact: true })).toHaveValue('urn:p1')
}
const expectCleared = async (page) => {
  await expect(page.getByRole('combobox', { name: /^选择对象/u })).toHaveValue('')
  await expect(page.getByRole('checkbox', { checked: true })).toHaveCount(0)
  await expect(page.getByLabel('条件 1 属性', { exact: true })).toHaveCount(0)
  await expect(generate(page)).toBeDisabled()
}
const cases = [
  {
    name: 'invalid-rdf-type-blocks-generation',
    run: async (page) => {
      await prime(page)
      const editor = page.getByRole('textbox', { name: /^SPARQL/u })
      const original = await editor.inputValue()
      await page.getByLabel('条件 1 RDF 类型', { exact: true }).selectOption('iri')
      await expect(generate(page)).toBeDisabled()
      await expect(
        page.getByText('请选择有效对象，并检查属性和 RDF 条件值后生成草稿。', { exact: true }),
      ).toBeVisible()
      await expect(editor).toHaveValue(original)
      await page.getByLabel('条件 1 值', { exact: true }).fill('urn:High')
      await expect(generate(page)).toBeEnabled()
      await generate(page).click()
      await expect(editor).toHaveValue(original.replace('"High"', '<urn:High>'))
    },
  },
  {
    name: 'sixteen-fields-and-reselection',
    run: async (page) => {
      await page.getByRole('combobox', { name: /^选择对象/u }).selectOption('urn:ClassA')
      for (let i = 1; i <= 16; i++)
        await page.getByRole('checkbox', { name: `字段${String(i).padStart(2, '0')}` }).check()
      await expect(page.getByRole('checkbox', { name: '字段17' })).toBeDisabled()
      await expect(page.getByRole('checkbox', { name: '字段01' })).toBeEnabled()
      await expect(page.getByText('已选 16/16', { exact: true })).toBeVisible()
      await page.getByRole('checkbox', { name: '字段01' }).uncheck()
      await page.getByRole('checkbox', { name: '字段17' }).check()
      await generate(page).click()
      const selected = Array.from({ length: 16 }, (_, i) => i + 2)
      const variables = ['?item', ...selected.map((_, i) => `?field${i}`)].join(' ')
      const expected = `SELECT DISTINCT ${variables} WHERE {\n  ?item a <urn:ClassA> .\n${selected.map((n, i) => `  OPTIONAL { ?item <urn:p${n}> ?field${i} . }`).join('\n')}\n}\nORDER BY ${variables}`
      await expect(page.getByRole('textbox', { name: /^SPARQL/u })).toHaveValue(expected)
    },
  },
  {
    name: 'saved-load-clears-old-builder',
    run: async (page) => {
      await prime(page)
      await page.getByRole('button', { name: '已保存B', exact: true }).click()
      await expectCleared(page)
      await expect(page.getByLabel('名称', { exact: true })).toHaveValue('已保存B')
      await expect(page.getByRole('textbox', { name: /^SPARQL/u })).toHaveValue(
        'SELECT ?b WHERE { ?b a <urn:ClassB> }',
      )
      await expect(page.getByRole('button', { name: '保存到项目（更新 Saved-B）' })).toBeDisabled()
      await page.getByRole('combobox', { name: /^选择对象/u }).selectOption('urn:ClassA')
      await page.getByRole('checkbox', { name: '字段03' }).check()
      await generate(page).click()
      await expect(page.getByRole('textbox', { name: /^SPARQL/u })).toHaveValue(
        'SELECT DISTINCT ?item ?field0 WHERE {\n  ?item a <urn:ClassA> .\n  OPTIONAL { ?item <urn:p3> ?field0 . }\n}\nORDER BY ?item ?field0',
      )
    },
  },
  {
    name: 'new-query-clears-old-builder',
    run: async (page) => {
      await prime(page)
      await page.getByRole('button', { name: '新建查询', exact: true }).click()
      await expectCleared(page)
      await expect(page.getByLabel('名称', { exact: true })).toHaveValue('')
      await expect(page.getByRole('textbox', { name: /^SPARQL/u })).toHaveValue('')
      await expect(page.getByRole('button', { name: '保存到项目（新查询）' })).toBeDisabled()
    },
  },
  {
    name: 'model-load-clears-old-builder',
    run: async (page) => {
      await prime(page)
      await page.getByRole('button', { name: '查看 T08 提供的模型草稿', exact: true }).click()
      await expectCleared(page)
      await expect(page.getByLabel('名称', { exact: true })).toHaveValue('模型M')
      await expect(page.getByRole('textbox', { name: /^SPARQL/u })).toHaveValue(
        'SELECT ?m WHERE { ?m a <urn:ClassM> }',
      )
    },
  },
]
try {
  for (const entry of cases) {
    const page = await context.newPage()
    page.on('pageerror', (error) => pageErrors.push(error.message))
    try {
      await page.setContent('<!doctype html><html><body><div id="root"></div></body></html>')
      await page.addStyleTag({ content: styles })
      await page.addScriptTag({ content: javascript })
      await entry.run(page)
      checks.push({ name: entry.name, passed: true })
    } catch (error) {
      checks.push({ name: entry.name, passed: false, error: String(error).slice(0, 3000) })
      await page.screenshot({ path: path.join(runtime, `failure-${entry.name}.png`) })
    } finally {
      await page.close()
    }
  }
  const result = {
    probe: 'T04 isolated QueryPage real DOM interaction',
    browserVersion: browser.version(),
    executablePath,
    headless: true,
    offline: true,
    requests,
    pageErrors,
    checks,
    passed: checks.every((entry) => entry.passed) && !requests.length && !pageErrors.length,
    boundary:
      'No App, IPC, executor, persistence, model call, production CSP or native acceptance.',
  }
  writeFileSync(
    path.join(runtime, 'interaction-results.json'),
    JSON.stringify(result, null, 2) + '\n',
  )
  console.log(JSON.stringify(result))
  if (!result.passed) process.exitCode = 1
} finally {
  await context.tracing.stop({ path: path.join(runtime, 'interaction-trace.zip') })
  await browser.close()
}
