import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { mkdir, readFile, writeFile, stat, readdir } from 'node:fs/promises'
import { resolve, relative, join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { build } from 'vite'
import react from '@vitejs/plugin-react'
import { chromium, expect } from '@playwright/test'

const root = process.cwd()
const args = process.argv.slice(2)
assert.equal(args.length, 4, 'required: --candidate SHA --output NEW_OWN_RUNTIME')
assert.equal(args[0], '--candidate')
assert.match(args[1], /^[a-f0-9]{40}$/)
assert.equal(args[2], '--output')
const candidate = args[1],
  output = resolve(args[3])
const runtime = resolve(root, 'docs/reviews/T08/review-runtime-post-designated-20261023')
assert.ok(relative(runtime, output) && !relative(runtime, output).startsWith('..'))
await mkdir(output) // Refuse existing output; failed profiles/raw are never erased.
const out = join(output, 'out')
await mkdir(out)
const sha = (data) => createHash('sha256').update(data).digest('hex')
const manifestPath = 'docs/reviews/T08/dispatch-boundary-20261023/candidate-and-acceptance.json'
const factsPath =
  'docs/reviews/T08/mounted-harness-preparation-20261023/actual-browser-and-electron-facts.json'
const fixturePaths = [
  'tests/fixtures/agent/sidebar-mounted-harness.tsx',
  'tests/fixtures/agent/sidebar-mounted-probe.mjs',
]
let paths = []
const hashes = async () =>
  Object.fromEntries(
    await Promise.all(paths.map(async (path) => [path, sha(await readFile(path))])),
  )
const report = {
  candidate,
  base: '5f910b52c69d86a1076b2032e5d3c63e715947f3',
  cwd: root,
  argv: process.argv,
  startedAt: new Date().toISOString(),
  cases: [],
  pageErrors: [],
  requests: [],
  boundary:
    'real ReactDOM/UI and real pure Node orchestration with synthetic ports; no actual domain/provider/I04 job/production bridge',
  exitCode: 1,
}
let browserContext, page, conversation, completeLate
let nodeCurrent,
  portAborted = false
const context = {
  projectId: 'p1',
  projectRevision: 1,
  inputSnapshotId: 's1',
  scopeRef: 'scope1',
  module: 'query',
  mode: 'tutor',
  selectedObjectIds: ['001', '002'],
}
const draft = {
  callId: 'draft1',
  tool: 'query_draft',
  outcome: {
    kind: 'draft',
    draftType: 'query',
    summary: '查询草稿',
    detail: 'SELECT ?id WHERE {\n  ?id <urn:status> "Open"\n}',
    projectId: 'p1',
    baseRevision: 1,
    inputSnapshotId: 's1',
    requiresHumanDiffConfirmation: true,
  },
}
const state = (patch = {}) => ({
  phase: 'answered',
  exchanges: 1,
  requestedTokenCeiling: 32,
  error: null,
  inputContext: context,
  localReceipts: [draft],
  answer: null,
  ...patch,
})
const run = async (name, fn) => {
  try {
    await fn()
    report.cases.push({ name, status: 'passed' })
    console.log('PASS', name)
  } catch (error) {
    report.cases.push({ name, status: 'failed', error: String(error) })
    throw error
  }
}
const events = () => page.evaluate(() => window.t08.events())
const reset = async (options = {}) => {
  nodeCurrent = options.context ?? structuredClone(context)
  await page.evaluate((value) => window.t08.reset(value), options)
}
const update = async (patch) => {
  if (patch.context) nodeCurrent = patch.context
  await page.evaluate((value) => window.t08.update(value), patch)
}
const publish = () => update({ state: conversation.state() })
try {
  report.fixedInputs = {}
  for (const path of [manifestPath, factsPath]) {
    const expected = execFileSync('git', ['show', `${candidate}:${path}`])
    assert.equal(sha(await readFile(path)), sha(expected), path)
    report.fixedInputs[path] = sha(expected)
  }
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'))
  paths = [...Object.keys(manifest.sourceHashes), ...fixturePaths]
  report.sourceBefore = await hashes()
  for (const path of paths)
    assert.equal(
      sha(execFileSync('git', ['show', `${candidate}:${path}`])),
      report.sourceBefore[path],
      path,
    )
  const facts = JSON.parse(await readFile(factsPath, 'utf8'))
  const executablePath = facts.systemChromeExecutable.path
  report.browserExecutable = {
    path: executablePath,
    bytes: (await stat(executablePath)).size,
    sha256: sha(await readFile(executablePath)),
  }
  assert.equal(
    report.browserExecutable.sha256,
    facts.systemChromeExecutable.sha256,
    'Chrome changed since preparation',
  )
  report.playwrightVersion = JSON.parse(
    await readFile('node_modules/playwright/package.json', 'utf8'),
  ).version
  assert.equal(report.playwrightVersion, facts.lockIdentity.playwright)
  await build({
    configFile: false,
    root,
    publicDir: false,
    plugins: [react()],
    define: { 'process.env.NODE_ENV': JSON.stringify('production') },
    build: {
      outDir: join(out, 'browser'),
      minify: false,
      lib: {
        entry: resolve(fixturePaths[0]),
        formats: ['iife'],
        name: 'T08Mounted',
        fileName: () => 'harness.js',
      },
    },
  })
  const nodeEntry = join(out, 'node-entry.mjs')
  await writeFile(
    nodeEntry,
    `export { AgentConversation } from ${JSON.stringify(resolve('apps/desktop/src/main/agent/conversation.ts'))};\n` +
      `export { CODEC_VERSION, DEEPSEEK_ENDPOINT, REQUEST_MODEL } from ${JSON.stringify(resolve('apps/desktop/src/main/agent/deepseek-codec.ts'))};\n`,
  )
  await build({
    configFile: false,
    root,
    publicDir: false,
    build: {
      ssr: nodeEntry,
      outDir: join(out, 'node'),
      minify: false,
      rollupOptions: { output: { entryFileNames: 'conversation.mjs' } },
    },
  })
  const { AgentConversation, CODEC_VERSION, DEEPSEEK_ENDPOINT, REQUEST_MODEL } = await import(
    pathToFileURL(join(out, 'node/conversation.mjs')).href
  )
  browserContext = await chromium.launchPersistentContext(join(out, 'chrome-profile'), {
    executablePath,
    headless: true,
    viewport: { width: 1100, height: 1000 },
    offline: true,
    args: ['--disable-background-networking', '--disable-component-update', '--no-first-run'],
  })
  report.actualBrowserVersion = browserContext.browser().version()
  assert.equal(
    report.actualBrowserVersion,
    facts.files['/Applications/Google Chrome.app/Contents/Info.plist'].version,
  )
  await browserContext.route('**/*', async (route) => {
    report.requests.push(route.request().url())
    await route.abort()
  })
  page = await browserContext.newPage()
  page.on('pageerror', (error) => report.pageErrors.push(error.message))
  await page.exposeBinding('t08Node', async (_source, kind, question) => {
    if (kind === 'cancel') {
      conversation.cancel()
      await publish()
      return
    }
    assert.equal(kind, 'submit')
    const signature = {
      endpoint: DEEPSEEK_ENDPOINT,
      requestedModel: REQUEST_MODEL,
      returnedModel: 'synthetic-mounted-version',
      fingerprint: null,
      mode: 'enabled',
      effort: 'high',
      codecVersion: CODEC_VERSION,
    }
    const options = {
      mode: 'enabled',
      effort: 'high',
      maxTokens: 32,
      maxExchanges: 4,
      maxTotalRequestedTokens: 128,
      toolTimeoutMs: 15000,
      projectedFieldIds: [],
      expectedProviderSignature: signature,
    }
    conversation = new AgentConversation(nodeCurrent, question, options, {
      query_draft: {
        execute: async () => ({
          kind: 'draft',
          draftType: 'query',
          summary: '已完成草稿',
          detail: draft.outcome.detail,
        }),
      },
      query_execute: {
        execute: async (_ctx, _args, signal) => {
          signal.addEventListener(
            'abort',
            () => {
              portAborted = true
            },
            { once: true },
          )
          void publish().catch((error) => report.pageErrors.push(error.message))
          return new Promise((resolveLate) => {
            completeLate = resolveLate
          })
        },
      },
    })
    conversation.prepareExchange(() => nodeCurrent)
    const pending = conversation.acceptResponse(
      1,
      JSON.stringify({
        id: 'synthetic-mounted-response',
        object: 'chat.completion',
        created: 1,
        model: signature.returnedModel,
        choices: [
          {
            index: 0,
            finish_reason: 'tool_calls',
            message: {
              role: 'assistant',
              content: null,
              reasoning_content: 'synthetic',
              tool_calls: [
                {
                  id: 'draft1',
                  type: 'function',
                  function: {
                    name: 'query_draft',
                    arguments: '{"question":"设备","scope":"asserted"}',
                  },
                },
                {
                  id: 'query1',
                  type: 'function',
                  function: {
                    name: 'query_execute',
                    arguments: '{"sparql":"SELECT ?s WHERE {?s ?p ?o}","scope":"asserted"}',
                  },
                },
              ],
            },
          },
        ],
      }),
      () => nodeCurrent,
      new AbortController().signal,
    )
    await publish()
    try {
      await pending
    } finally {
      await publish()
    }
  })
  await page.setContent('<!doctype html><html lang="zh"><body><div id="root"></div></body></html>')
  await page.addScriptTag({ path: join(out, 'browser/harness.js') })
  for (const name of await readdir(join(out, 'browser')))
    if (name.endsWith('.css')) await page.addStyleTag({ path: join(out, 'browser', name) })
  const input = page.getByLabel('当前问题'),
    submit = page.getByRole('button', { name: '发送问题', exact: true })
  await run('seven modules/two modes: bounded actions and actual local callback', async () => {
    for (const module of [
      'learn',
      'ontology',
      'mapping',
      'query',
      'quality',
      'behavior',
      'scenario',
    ]) {
      for (const mode of ['tutor', 'project']) {
        await reset({ context: { ...context, module, mode }, privacy: 'local', modelReady: false })
        assert.ok((await page.locator('.t08-actions button').count()) <= 4)
        await page.getByRole('button', { name: /给我一点提示/ }).click()
        await expect.poll(async () => (await events()).length).toBe(1)
        assert.equal(
          (await events())[0].assistance,
          mode === 'project' ? 'full-assistance' : 'hint',
        )
        assert.equal((await events())[0].target, 'local')
        await expect(submit).toBeDisabled()
      }
    }
    await reset({ handlers: false })
    await expect(page.locator('.t08-actions button').first()).toBeDisabled()
    assert.equal((await events()).length, 0)
  })
  await run('native double submit, safe rejection,001 retained', async () => {
    await reset({ deferred: true })
    await input.fill('保留001')
    await page.locator('form').evaluate((form) => {
      form.requestSubmit()
      form.requestSubmit()
    })
    await expect.poll(async () => (await events()).length).toBe(1)
    await expect(submit).toBeDisabled()
    await page.evaluate((id) => window.t08.settle(id, false), (await events())[0].id)
    await expect(page.getByText('操作未完成，输入已保留。请检查实际任务状态后重试。')).toBeVisible()
    await expect(input).toHaveValue('保留001')
    assert.ok(!(await page.locator('body').innerText()).includes('private-path/private-cell'))
  })
  await run('A/B input and late callback isolation with switchback lock', async () => {
    await reset({ deferred: true })
    await input.fill('A original')
    await submit.click()
    const a = (await events())[0].id
    await update({ context: { ...context, projectId: 'p2' }, state: null })
    await expect(input).toHaveValue('')
    await input.fill('B original')
    await submit.click()
    const b = (await events())[1].id
    await update({ context })
    await expect(input).toHaveValue('A original')
    await expect(submit).toBeDisabled()
    await input.fill('A later edit')
    await update({ context: { ...context, projectId: 'p2' }, state: null })
    await page.evaluate((id) => window.t08.settle(id, false), a)
    await expect(input).toHaveValue('B original')
    await expect(submit).toBeDisabled()
    await expect(page.getByText('操作未完成，输入已保留。请检查实际任务状态后重试。')).toHaveCount(
      0,
    )
    await page.evaluate((id) => window.t08.settle(id, true), b)
    await expect(submit).toBeEnabled()
    await update({ context })
    await expect(input).toHaveValue('A later edit')
    await expect(page.getByText('操作未完成，输入已保留。请检查实际任务状态后重试。')).toBeVisible()
  })
  await run(
    'all context axes block stale preview/cancel and preserve ordered identity',
    async () => {
      for (const change of [
        { projectId: 'p2' },
        { projectRevision: 2 },
        { inputSnapshotId: 's2' },
        { scopeRef: 'scope2' },
        { module: 'mapping' },
        { mode: 'project' },
        { selectedObjectIds: ['002', '001'] },
      ]) {
        await reset({ state: state({ phase: 'awaiting-provider' }) })
        await update({ context: { ...context, ...change } })
        await expect(page.getByRole('button', { name: '查看真实 Diff' })).toBeDisabled()
        await expect(page.getByRole('button', { name: '取消本地等待' })).toBeDisabled()
        await page.getByRole('button', { name: '取消本地等待' }).dispatchEvent('click')
        assert.equal((await events()).length, 0)
      }
      await reset()
      await input.fill('same identity')
      await update({ context: Object.fromEntries(Object.entries(context).reverse()) })
      await expect(input).toHaveValue('same identity')
    },
  )
  await run('draft/evidence update, clone, states and text-only malicious payload', async () => {
    await reset({ state: state() })
    await page.getByText('查看详细建议', { exact: true }).click()
    await expect(page.locator('pre')).toBeVisible()
    await expect(page.locator('pre')).toHaveText(draft.outcome.detail)
    await page.getByRole('button', { name: '查看真实 Diff' }).click()
    await expect.poll(async () => (await events()).length).toBe(1)
    assert.equal((await events())[0].receipt.outcome.baseRevision, 1)
    await expect(page.locator('pre')).toHaveText(draft.outcome.detail)
    for (const status of ['current', 'stale', 'historical', 'failed', 'cancelled']) {
      const evidence = {
        callId: 'e1',
        tool: 'query_execute',
        outcome: {
          kind: 'evidence',
          projectId: 'p1',
          inputSnapshotId: 's1',
          scopeRef: 'scope1',
          resultId: 'r1',
          status,
          traceRefs: ['trace1'],
          fields: [
            { fieldId: 'id', value: '001' },
            { fieldId: 'zero', value: 0 },
            { fieldId: 'flag', value: false },
            { fieldId: 'nil', value: null },
          ],
        },
      }
      await update({
        state: state({ phase: 'failed', error: 'TIMED_OUT', localReceipts: [draft, evidence] }),
      })
      await expect(page.locator('pre')).toHaveText(draft.outcome.detail)
      await expect(page.locator('.t08-records')).toContainText('001')
      await expect(page.locator('.t08-records')).toContainText('false')
      await expect(page.locator('.t08-records')).toContainText('空值（null）')
      await expect(
        page
          .locator('.t08-fields div')
          .filter({ has: page.locator('dt', { hasText: 'zero' }) })
          .locator('dd'),
      ).toHaveText('0')
      await expect(page.locator('.t08-record-state').last()).toHaveText(
        {
          current: '当前结果',
          stale: '已过期，需重跑',
          historical: '历史结果',
          failed: '失败，不能据此认定通过',
          cancelled: '已取消，不能据此认定通过',
        }[status],
      )
      await expect(page.locator('.t08-records')).toContainText('trace1')
    }
    const malicious = {
      ...draft,
      outcome: {
        ...draft.outcome,
        summary: '<img src="https://invalid.example/x"><script>bad</script>',
      },
    }
    await update({ state: state({ localReceipts: [malicious] }) })
    assert.equal(await page.locator('.t08-records img,.t08-records script').count(), 0)
    await page.screenshot({ path: join(output, 'draft-visible.png') })
  })
  await run(
    'local retry disabled,demonstration assistance and actual pure-tool abort/late result',
    async () => {
      await reset({ privacy: 'local', state: state({ phase: 'failed', error: 'TIMED_OUT' }) })
      await expect(page.getByRole('button', { name: '重试本次操作' })).toBeDisabled()
      await reset({ context: { ...context, module: 'ontology' } })
      await page.getByRole('button', { name: /演示下一步/ }).click()
      assert.equal((await events())[0].assistance, 'full-assistance')
      await reset({ tools: true })
      await input.fill('合成协议取消案例')
      await submit.click()
      await expect(page.getByText('已完成草稿', { exact: true })).toBeVisible()
      await page.getByRole('button', { name: '取消本地等待' }).click()
      await expect.poll(() => portAborted).toBe(true)
      await expect.poll(() => conversation.state().phase).toBe('cancelled')
      completeLate({
        kind: 'evidence',
        projectId: 'p1',
        inputSnapshotId: 's1',
        scopeRef: 'scope1',
        resultId: 'late1',
        status: 'current',
        traceRefs: [],
        fields: [],
      })
      await expect(page.getByText('已完成草稿', { exact: true })).toBeVisible()
      assert.equal(conversation.state().phase, 'cancelled')
      assert.equal(conversation.state().localReceipts.length, 1)
      report.pureToolCancellation = {
        signalAborted: portAborted,
        state: conversation.state(),
        actualI04Job: false,
      }
    },
  )
  assert.deepEqual(report.pageErrors, [])
  assert.deepEqual(report.requests, [])
  report.exitCode = 0
} catch (error) {
  report.error = String(error)
  console.error(error)
  report.exitCode = 1
} finally {
  try {
    if (browserContext) await browserContext.close()
  } catch (error) {
    report.closeError = String(error)
    report.exitCode = 1
  }
  try {
    report.sourceAfter = await hashes()
    report.fixedInputsAfter = Object.fromEntries(
      await Promise.all(
        [manifestPath, factsPath].map(async (path) => [path, sha(await readFile(path))]),
      ),
    )
    if (JSON.stringify(report.fixedInputs) !== JSON.stringify(report.fixedInputsAfter))
      report.exitCode = 1
  } catch (error) {
    report.sourceError = String(error)
    report.exitCode = 1
  }
  report.sourceUnchanged =
    JSON.stringify(report.sourceBefore) === JSON.stringify(report.sourceAfter)
  if (!report.sourceUnchanged) report.exitCode = 1
  report.finishedAt = new Date().toISOString()
  await writeFile(join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n')
  console.log(
    JSON.stringify({
      exitCode: report.exitCode,
      cases: report.cases.length,
      sourceUnchanged: report.sourceUnchanged,
    }),
  )
  process.exitCode = report.exitCode
}
