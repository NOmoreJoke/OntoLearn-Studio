// Headless synthetic UI probe only. No Electron, domain runtime, HTTP server or model call.
import { mkdtemp, readFile, writeFile, readdir, rm } from 'node:fs/promises'
import path from 'node:path'
import { pathToFileURL } from 'node:url'
import { build } from 'vite'
import { chromium } from '@playwright/test'

const root = process.cwd()
const evidence = path.join(root, 'docs/reviews/T07/evidence')
const scratch = await mkdtemp(path.join(root, '.t07-ui-'))
const fixture = JSON.parse(await readFile('tests/fixtures/scenario/e5.json', 'utf8'))
const identity = { projectId: 'project-1', engineVersion: 'engine-1', dependencyLockHash: 'lock-1', projectVersion: 'P1', scenarioId: 'S1', inputVersion: 'V1', ruleVersion: 'R1', behaviorVersion: 'B1', configurationDigest: 'C1', semantics: 'scenario-e2-v1' }
const runs = (capacity) => [{
  id: `probe-${capacity}`, identity: { ...identity, scenarioId: `S${capacity}` }, status: 'succeeded',
  rounds: fixture.expected[String(capacity)].map((round) => ({
    number: round.round, created: round.created, completed: round.completed, backlog: round.backlog,
    metrics: { ...round.metrics, openHighAlerts: round.metrics.open_high_alerts },
    inputEvents: fixture.events.filter((event) => event.round === round.round).map((event) => event.id),
    behaviorTrace: ['synthetic probe · 仅用于页面检查'], beforeInference: '合成编排探针', endInference: '合成编排探针',
  })), pendingEvents: capacity === 3 ? ['future-event'] : [],
    evidence: { source: 'V1 历史来源', assumptions: ['V1 原始假设（不沿用V2）'], maxRounds: 4, capacity, parameters: '{}' }, replayAvailable: false,
  replayUnavailableReason: '页面测试数据不具有真实推理和存储证据',
}]
const scenarios = [3, 4].map((capacity) => ({
  identity: { ...identity, scenarioId: `S${capacity}`, inputVersion: capacity === 3 ? 'V2' : 'V1' },
  name: capacity === 3 ? '基准场景 <script>bad()</script>' : '产能对比',
  capacity, maxRounds: 4, source: 'PRD E.5 · 合成页面探针',
  assumptions: ['每轮四事件，单事件单工单；页面探针不表示真实业务闭环。'], runs: runs(capacity),
}))
try {
  const entry = path.join(scratch, 'probe.jsx')
  await writeFile(entry, `import React from 'react'; import {createRoot} from 'react-dom/client'; import {ScenarioPage} from ${JSON.stringify(path.join(root, 'apps/desktop/src/renderer/src/scenario/ScenarioPage.tsx'))};
const scenarios=${JSON.stringify(scenarios)};
window.probeCalls=[];
createRoot(document.getElementById('root')).render(React.createElement(ScenarioPage,{scenarios,actions:{create:async(...args)=>{window.probeCalls.push(['create',...args])},run:async(...args)=>{window.probeCalls.push(['run',...args])},resume:async(...args)=>{window.probeCalls.push(['resume',...args])},restore:async()=>{throw Error('probe private detail')}}}));`)
  await build({ configFile: false, logLevel: 'error', define: { 'process.env.NODE_ENV': '"production"' }, build: { outDir: path.join(scratch, 'dist'), lib: { entry, name: 'T07Probe', formats: ['iife'], fileName: () => 'probe.js' }, minify: true } })
  const js = await readFile(path.join(scratch, 'dist/probe.js'), 'utf8')
  const files = await readdir(path.join(scratch, 'dist'))
  const css = (await Promise.all(files.filter((name) => name.endsWith('.css')).map((name) => readFile(path.join(scratch, 'dist', name), 'utf8')))).join('\n')
  const html = `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>T07 合成页面探针</title><style>body{margin:0;background:#f4f6f2;font-family:system-ui}${css}</style><div id="root"></div><script>${js.replaceAll('</script', '<\\/script')}</script></html>`
  await writeFile(path.join(scratch, 'probe.html'), html)
  const browser = await chromium.launch({ headless: true, chromiumSandbox: true, executablePath: process.env.T07_HEADLESS_EXECUTABLE })
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } })
    const errors = []
    page.on('pageerror', (error) => errors.push(error.message))
    await page.goto(pathToFileURL(path.join(scratch, 'probe.html')).href)
    await page.getByRole('heading', { name: '沙盘', exact: true }).waitFor()
    await page.getByRole('checkbox').nth(0).check()
    await page.getByRole('checkbox').nth(1).check()
    if (await page.locator('table tbody tr').count() !== 4) throw Error('Missing comparison rounds')
    await page.getByText('历史结果 · 输入版本已变化', { exact: true }).first().waitFor()
    await page.getByText('存在未处理事件（1）', { exact: true }).first().waitFor()
    await page.getByRole('button', { name: '运行场景', exact: true }).click()
    await page.waitForFunction(() => window.probeCalls.length === 1)
    await page.getByRole('button', { name: '恢复基准场景', exact: true }).click()
    await page.getByRole('alert').filter({ hasText: '操作未完成' }).waitFor()
    await page.getByLabel('场景名称', { exact: true }).fill('新增探针')
    await page.getByLabel('产能输入方式', { exact: true }).selectOption('people')
    await page.getByLabel('人员数', { exact: true }).fill('2')
    await page.getByLabel('每人每轮处理数', { exact: true }).fill('3')
    await page.getByText('配置场景输入、规则、事件与业务参数', { exact: true }).click()
    await page.getByLabel('自定义输入（替换复制的输入）', { exact: true }).check()
    await page.getByLabel('逐轮事件（列表，含 id、round、sequence、payload）', { exact: true }).fill('[{"id":"new","round":1,"sequence":0,"payload":{}}]')
    await page.getByLabel('数据来源', { exact: true }).fill('合成输入来源')
    await page.getByRole('button', { name: '复制选中场景', exact: true }).click()
    await page.waitForFunction(() => window.probeCalls.length === 2)
    await page.screenshot({ path: path.join(evidence, 'page-wide.png'), fullPage: true })
    await page.setViewportSize({ width: 390, height: 844 })
    await page.screenshot({ path: path.join(evidence, 'page-narrow.png'), fullPage: true })
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)
    const calls = await page.evaluate(() => window.probeCalls)
    if (overflow || errors.length) throw Error(JSON.stringify({ overflow, errors }))
    if (calls[1][1].capacity !== 6 || calls[1][1].inputs.source !== '合成输入来源') throw Error('People capacity/custom inputs not forwarded')
    await page.getByLabel('创建来源', { exact: true }).selectOption('project')
    await page.getByRole('button', { name: '从项目创建场景', exact: true }).click()
    await page.waitForFunction(() => window.probeCalls.length === 3)
    const projectSource = await page.evaluate(() => window.probeCalls[2][2])
    const finalCalls = await page.evaluate(() => window.probeCalls)
    if (projectSource !== undefined) throw Error('Project source incorrectly copied existing scenario')
    await page.getByLabel('逐轮事件（列表，含 id、round、sequence、payload）', { exact: true }).fill('[{"id":"new","round":0,"sequence":0,"payload":{}}]')
    if (!(await page.getByRole('button', { name: '从项目创建场景', exact: true }).isDisabled())) throw Error('Invalid events enabled create')
    await writeFile(path.join(evidence, 'ui-probe.json'), JSON.stringify({
      evidence: 'synthetic headless UI only, no actual business adapters',
      viewports: ['1440x1100', '390x844'], browserVersion: browser.version(), executablePath: process.env.T07_HEADLESS_EXECUTABLE ?? 'Playwright default', comparisonRounds: 4,
      lateV1MarkedHistorical: true, pendingExposed: true, errorRedacted: true, projectSourceReachableWithExistingScenario: true,
      scriptTextEscaped: errors.length === 0, noPageOverflow: !overflow, calls: finalCalls,
    }, null, 2) + '\n')
  } finally { await browser.close() }
} finally { await rm(scratch, { recursive: true, force: true }) }
