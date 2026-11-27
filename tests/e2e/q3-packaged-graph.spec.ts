import { test, expect, type Locator, type Page } from '@playwright/test'
import { createHash } from 'node:crypto'
import { createServer } from 'node:http'
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { performance } from 'node:perf_hooks'
import { cpus, totalmem, release, platform, arch } from 'node:os'
import type { BridgeResult } from '@ontolearn/contracts'
import { launchIsolatedDesktop } from './isolated-desktop'

const take = <T>(reply: BridgeResult<T>): T => {
  if (!reply.ok) throw new Error(JSON.stringify(reply.error))
  return reply.data
}
const button = (root: Locator, name: string) => root.getByRole('button', { name, exact: true })
const task = (root: Locator) =>
  root.getByRole('region', { name: '真实查询或提交任务', exact: true })
async function terminal(page: Page, workspace: Locator, notice: string, previous?: string) {
  try {
    const code = task(workspace).locator('code')
    if (previous) await expect(code).not.toHaveText(previous)
    await expect(code).toHaveText(/^[0-9a-f-]{36}$/)
    await expect(task(workspace)).toContainText('：succeeded；')
    const refresh = button(task(workspace), '刷新任务、原操作与固定结果')
    await expect(refresh).toBeEnabled()
    await refresh.click()
    // A succeeded commit is not yet a reusable loaded query. Wait for the actual
    // historical/current definition reconciliation, exactly as the Q3 UI tests do.
    await expect(workspace.locator('p[role="status"][aria-live="polite"]')).toHaveText(notice)
    await expect(refresh).toBeEnabled()
    const id = await code.textContent()
    if (!id) throw new Error('Missing actual job ID')
    return take(await page.evaluate((id) => window.ontolearn!.getJob(id), id))
  } catch (error) {
    // Electron's test trace may omit page snapshots. Preserve real UI error text,
    // without replacing the first assertion failure with a diagnostic failure.
    try {
      await test.info().attach('q3-terminal-workspace.txt', {
        body: await workspace.innerText(),
        contentType: 'text/plain',
      })
      await test.info().attach('q3-terminal-workspace.png', {
        body: await workspace.screenshot(),
        contentType: 'image/png',
      })
    } catch {
      /* The original failure remains authoritative. */
    }
    throw error
  }
}

// Explicit opt-in: this test never silently substitutes a development build.
test('Q3 packaged actual graph, enforced CSP and raw row-selection timings', async () => {
  test.skip(!process.env.ONTOLEARN_PACKAGED_EXECUTABLE, 'Requires an actual packaged executable')
  test.setTimeout(90000)
  const executable = resolve(process.env.ONTOLEARN_PACKAGED_EXECUTABLE!)
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => entry[1] !== undefined,
    ),
  )
  delete env.ELECTRON_RUN_AS_NODE
  delete env.ELECTRON_RENDERER_URL
  delete env.I04_TEST_FIXTURE
  const evidence: Record<string, unknown> = {
    boundary: 'Real packaged manual assertions/query/UI. No mapping execution or performance SLA.',
    executable,
    environment: {
      platform: platform(),
      osRelease: release(),
      arch: arch(),
      cpuModels: [...new Set(cpus().map((cpu) => cpu.model))],
      logicalCPUs: cpus().length,
      totalMemoryBytes: totalmem(),
      automationVersions: process.versions,
      powerMode: process.env.Q3_BENCHMARK_POWER_MODE ?? 'not recorded',
    },
    executableSha256: createHash('sha256')
      .update(await readFile(executable))
      .digest('hex'),
  }
  const requests: string[] = []
  const server = createServer((request, response) => {
    requests.push(request.url ?? '')
    response.setHeader('Access-Control-Allow-Origin', '*')
    response.end('window.__q3Remote=true')
  })
  await new Promise<void>((done) => server.listen(0, '127.0.0.1', done))
  const address = server.address()
  if (!address || typeof address === 'string') throw new Error('Missing CSP receiver')
  let application: Awaited<ReturnType<typeof launchIsolatedDesktop>> | undefined
  try {
    application = await launchIsolatedDesktop({
      executablePath: executable,
      args: [],
      cwd: resolve('apps/desktop'),
      env,
      chromiumSandbox: true,
    })
    // B1a validates the library before createWindow(), so the first window can
    // appear only after the startup awaits settle. Wait for it before reading
    // BrowserWindow state; reading it earlier throws on macOS and Linux.
    const page = await application.firstWindow()
    const pageerrors: string[] = []
    page.on('pageerror', (error) => pageerrors.push(error.message))
    evidence.pageerrors = pageerrors
    const runtime = await application.evaluate(({ app, BrowserWindow }) => ({
      packaged: app.isPackaged,
      appPath: app.getAppPath(),
      executable: process.execPath,
      userData: app.getPath('userData'),
      versions: process.versions,
      noSandbox: app.commandLine.hasSwitch('no-sandbox'),
      preferences: (
        BrowserWindow.getAllWindows()[0].webContents as unknown as {
          getLastWebPreferences(): {
            sandbox: boolean
            contextIsolation: boolean
            nodeIntegration: boolean
          }
        }
      ).getLastWebPreferences(),
    }))
    evidence.runtime = runtime
    expect(runtime.packaged).toBe(true)
    expect(runtime.noSandbox).toBe(false)
    expect(runtime.preferences).toMatchObject({
      sandbox: true,
      contextIsolation: true,
      nodeIntegration: false,
    })
    const csp = await page
      .locator('meta[http-equiv="Content-Security-Policy"]')
      .getAttribute('content')
    evidence.csp = csp
    expect(csp).toContain("connect-src 'none'")
    expect(csp).not.toMatch(/unsafe-inline|unsafe-eval/)
    await page.getByTestId('project-name').fill('Q3 packaged graph and CSP')
    await page.getByTestId('project-create-example').click()
    await expect(page.getByTestId('project-library').getByRole('status')).toContainText(
      '项目已创建并打开',
    )
    await page.getByRole('link', { name: '本体查询', exact: true }).click()
    const workspace = page.getByRole('region', { name: '本体查询工作台', exact: true })
    await button(workspace, '读取项目与持久工作草稿').click()
    await expect(button(workspace, '新建查询草稿')).toBeEnabled()
    const before = take(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(before.domain.state.facts).toHaveLength(18)
    const malicious = '<img src=x onerror=window.__q3Markup=true>'
    const sparql = `SELECT ?equipment ("${malicious}" AS ?probe) WHERE { ?equipment a <urn:ontolearn:learning:Equipment> } ORDER BY ?equipment`
    await button(workspace, '新建查询草稿').click()
    await workspace.getByLabel('项目内查询标识', { exact: true }).fill('q3-packaged-graph')
    await workspace.getByLabel('名称', { exact: true }).fill('包内真实关系图')
    await workspace
      .getByRole('textbox', { name: '说明', exact: true })
      .fill('F10 real packaged query')
    await workspace
      .getByRole('textbox', { name: '关联能力问题', exact: true })
      .fill('Which equipment?')
    await workspace.getByRole('textbox', { name: '可见 SPARQL', exact: true }).fill(sparql)
    await button(workspace, '读取正式保存的完整差异').click()
    const diff = workspace.getByRole('region', { name: '正式提交完整差异', exact: true })
    const rawDiff = await diff.locator('pre').textContent()
    if (!rawDiff) throw new Error('Missing complete Diff')
    const changes = JSON.parse(rawDiff)
    expect(changes).toHaveLength(1)
    expect(changes[0].resource).toEqual(['definition', 'query', 'q3-packaged-graph'])
    expect(changes[0].before).toBe(null)
    expect(JSON.parse(changes[0].after.payload).text).toBe(sparql)
    await expect(button(diff, '明确确认并提交真实任务')).toBeDisabled()
    await diff
      .getByRole('checkbox', { name: '我已核对完整差异，确认提交此版本', exact: true })
      .check()
    await button(diff, '明确确认并提交真实任务').click()
    const committed = await terminal(
      page,
      workspace,
      '真实提交终态、原operation、历史与当前定义均已核对；可执行受管查询。',
    )
    expect(committed.capability).toBe('changeset.commit')
    const source = take(
      await page.evaluate(() => window.ontolearn!.readProject({ editor: 'query-workspace-v1' })),
    )
    expect(source.domain.projectRevision).toBe(before.domain.projectRevision + 1)
    expect(source.domain.state.facts).toEqual(before.domain.state.facts)
    const marker = take(
      await page.evaluate((id) => window.ontolearn!.getOperation(id), committed.operationId),
    )
    expect(marker).toMatchObject({
      jobId: committed.jobId,
      afterSnapshotId: source.inputSnapshotId,
    })
    await expect(button(workspace, '执行已载入且未改变的受管定义')).toBeEnabled()
    await button(workspace, '执行已载入且未改变的受管定义').click()
    const job = await terminal(
      page,
      workspace,
      '已取得真实结果描述；按固定引用分别读取文本与结果页。',
      committed.jobId,
    )
    expect(job.capability).toBe('query.execute')
    expect(job.inputSnapshotId).toBe(source.inputSnapshotId)
    if (!job.resultRef) throw new Error('Missing actual result')
    const descriptor = take(
      await page.evaluate(
        (resultId) => window.ontolearn!.getQueryResultDescriptor({ resultId }),
        job.resultRef.resultId,
      ),
    )
    expect(descriptor.identity).toMatchObject({
      jobId: job.jobId,
      inputSnapshotId: source.inputSnapshotId,
      inputProjectRevision: source.domain.projectRevision,
    })
    const lane = workspace.getByRole('region', { name: '本次执行结果', exact: true })
    await button(lane, '读取 SELECT 结果第一页').click()
    const panel = lane.getByRole('region', { name: '查询结果', exact: true })
    await expect(panel.getByRole('table').getByText(malicious, { exact: true })).toHaveCount(3)
    await expect(panel.locator('img')).toHaveCount(0)
    expect(
      await page.evaluate(() => (window as unknown as { __q3Markup?: boolean }).__q3Markup),
    ).toBeUndefined()
    const graph = panel.getByRole('region', { name: '结果输入的局部关系图', exact: true })
    const selection = panel.getByRole('combobox', { name: '查看结果行', exact: true })
    await expect(selection.locator('option')).toHaveCount(3)
    const options = await selection
      .locator('option')
      .evaluateAll((nodes) => nodes.map((node) => (node as HTMLOptionElement).value))
    expect(options).toHaveLength(3)
    const samples: Array<{ iteration: number; row: number; milliseconds: number }> = []
    for (let iteration = 0; iteration < 15; iteration++) {
      const row = (iteration + 1) % 3
      const start = performance.now()
      await selection.selectOption(options[row])
      await expect(graph).toContainText(`当前页第 ${row + 1} 行`)
      // Two animation frames include a render opportunity, not a measured browser paint.
      await page.evaluate(
        () =>
          new Promise<void>((done) =>
            requestAnimationFrame(() => requestAnimationFrame(() => done())),
          ),
      )
      samples.push({ iteration, row, milliseconds: performance.now() - start })
      const anchor = `urn:ontolearn:learning:equipment/00${row + 1}`
      const facts = source.domain.state.facts.filter(
        (fact) =>
          fact.object?.startsWith('<') &&
          (fact.subject === anchor || fact.object === `<${anchor}>`),
      )
      expect(facts.length).toBeGreaterThan(0)
      const expected = facts
        .map((fact) => [fact.subject, fact.predicate, fact.object!.slice(1, -1)])
        .sort()
      const actual = await graph
        .locator('svg g[data-predicate]')
        .evaluateAll((nodes) =>
          nodes
            .map((node) =>
              ['data-subject', 'data-predicate', 'data-object'].map((key) =>
                node.getAttribute(key),
              ),
            )
            .sort(),
        )
      expect(actual).toEqual(expected)
      expect(
        await graph
          .locator('li[data-fact-id]')
          .evaluateAll((nodes) => nodes.map((node) => node.getAttribute('data-fact-id')).sort()),
      ).toEqual(facts.map((fact) => fact.id).sort())
    }
    await expect(graph.locator('code').first()).toHaveText(source.inputSnapshotId)
    const geometry = await graph.locator('svg').evaluate((svg) => {
      const line = svg.querySelector('line')!
      const marker = svg.querySelector('marker')!
      const box = svg.getBoundingClientRect()
      return {
        width: box.width,
        height: box.height,
        stroke: getComputedStyle(line).stroke,
        markerEnd: line.getAttribute('marker-end'),
        markerId: marker.id,
        titles: Array.from(svg.querySelectorAll('g > title')).map((node) => node.textContent),
      }
    })
    expect(geometry.width).toBeGreaterThan(0)
    expect(geometry.height).toBeGreaterThan(0)
    expect(geometry.stroke).not.toBe('none')
    expect(geometry.markerEnd).toBe(`url(#${geometry.markerId})`)
    expect(geometry.titles.every((title) => title?.includes(' → '))).toBe(true)
    await test
      .info()
      .attach('q3-packaged-graph.png', { body: await graph.screenshot(), contentType: 'image/png' })
    evidence.graph = { source, descriptor, job, committed, marker, rawDiff, geometry }
    const retained = samples
      .slice(3)
      .map((sample) => sample.milliseconds)
      .sort((a, b) => a - b)
    evidence.selectionBenchmark = {
      facts: source.domain.state.facts.length,
      pageRows: 3,
      warmupSamples: 3,
      summary: {
        count: retained.length,
        medianMs: (retained[5] + retained[6]) / 2,
        p95Ms: retained[Math.ceil(retained.length * 0.95) - 1],
        maxMs: retained[retained.length - 1],
      },
      samples,
      method:
        'Playwright selectOption + verified row label + two rAF; includes automation and frame scheduling, not pure render/paint latency.',
    }
    const probe = await graph.evaluate(async (root, target) => {
      const violations: Array<{ directive: string; blocked: string; disposition: string }> = []
      const listener = (event: SecurityPolicyViolationEvent) =>
        violations.push({
          directive: event.effectiveDirective,
          blocked: event.blockedURI,
          disposition: event.disposition,
        })
      document.addEventListener('securitypolicyviolation', listener)
      const nodes: HTMLElement[] = []
      const add = <T extends HTMLElement>(node: T) => {
        nodes.push(node)
        root.append(node)
        return node
      }
      try {
        const script = document.createElement('script')
        script.textContent = 'window.__q3Inline=true'
        add(script)
        const remote = document.createElement('script')
        remote.src = `${target}/script`
        add(remote)
        const image = document.createElement('img')
        image.src = `${target}/image`
        add(image)
        const event = add(document.createElement('button'))
        event.setAttribute('onclick', 'window.__q3Event=true')
        event.click()
        const frame = document.createElement('iframe')
        frame.src = `${target}/frame`
        add(frame)
        const fetchBlocked = await fetch(`${target}/fetch`).then(
          () => false,
          () => true,
        )
        const until = window.performance.now() + 1500
        while (
          window.performance.now() < until &&
          new Set(violations.map((v) => v.directive)).size < 5
        )
          await new Promise((done) => setTimeout(done, 20))
        const marks = window as unknown as {
          __q3Inline?: boolean
          __q3Remote?: boolean
          __q3Event?: boolean
          require?: unknown
        }
        return {
          violations,
          fetchBlocked,
          inline: marks.__q3Inline === true,
          remote: marks.__q3Remote === true,
          event: marks.__q3Event === true,
          require: typeof marks.require,
        }
      } finally {
        nodes.forEach((node) => node.remove())
        document.removeEventListener('securitypolicyviolation', listener)
      }
    }, `http://127.0.0.1:${address.port}`)
    evidence.probe = probe
    expect(probe).toMatchObject({
      fetchBlocked: true,
      inline: false,
      remote: false,
      event: false,
      require: 'undefined',
    })
    for (const directive of [
      'script-src-elem',
      'script-src-attr',
      'img-src',
      'frame-src',
      'connect-src',
    ])
      expect(
        probe.violations.some((v) => v.directive === directive && v.disposition === 'enforce'),
      ).toBe(true)
    expect(requests).toEqual([])
    expect(pageerrors).toEqual([])
    await expect(graph.locator('svg')).toBeVisible()
  } finally {
    evidence.receiverRequests = requests
    try {
      await test.info().attach('q3-packaged-graph-evidence.json', {
        body: JSON.stringify(evidence, null, 2),
        contentType: 'application/json',
      })
    } finally {
      try {
        await application?.close()
      } finally {
        await new Promise<void>((done, reject) =>
          server.close((error) => (error ? reject(error) : done())),
        )
      }
    }
  }
})
