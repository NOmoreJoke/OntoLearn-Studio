import { test, expect, _electron as electron, type Page } from '@playwright/test'
import { resolve } from 'node:path'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { runNativeRecovery } from './native-driver'
import { tmpdir } from 'node:os'
import { mkdtemp } from 'node:fs/promises'
import { compareCspViolations, type CspViolationTuple } from '../helpers/csp-violation-projection'

// Independent semantic expectations; identical tuples may repeat in the raw event stream.
const expectedCspViolations: Record<'production' | 'development', readonly CspViolationTuple[]> = {
  production: [
    ['script-src-elem', 'enforce', 'inline'],
    ['script-src-elem', 'enforce', 'probe-origin'],
    ['style-src-elem', 'enforce', 'inline'],
    ['style-src-attr', 'enforce', 'inline'],
    ['img-src', 'enforce', 'probe-origin'],
    ['connect-src', 'enforce', 'probe-origin'],
    ['frame-src', 'enforce', 'probe-origin'],
  ],
  development: [
    ['script-src-elem', 'enforce', 'inline'],
    ['script-src-elem', 'enforce', 'probe-origin'],
    ['img-src', 'enforce', 'probe-origin'],
    ['connect-src', 'enforce', 'probe-origin'],
    ['frame-src', 'enforce', 'probe-origin'],
  ],
}

test('C1 real CSP, normal functionality and renderer recovery', async () => {
  test.setTimeout(90000)
  const testInfo = test.info()
  const requests: string[] = []
  const server = createServer((request, response) => {
    requests.push(request.url ?? '')
    response.setHeader('Access-Control-Allow-Origin', '*')
    response.end('window.__remoteScript = true')
  })
  await new Promise<void>((done) => server.listen(0, '127.0.0.1', done))
  const address = server.address()
  if (!address || typeof address === 'string') throw new Error('missing probe port')
  const target = `http://127.0.0.1:${address.port}`
  const env = { ...process.env }
  delete env.ELECTRON_RUN_AS_NODE
  const expectedUserDataPath = testInfo.outputPath('electron-user-data')
  const userDataArg = `--user-data-dir=${expectedUserDataPath}`
  const development = Boolean(env.ELECTRON_RENDERER_URL)
  const evidence: Record<string, unknown> = { development, target }
  const stage = (value: string) => {
    evidence.stage = value
    console.info(`[I02] ${value}`)
  }
  stage('launch')
  const application = await electron.launch({
    chromiumSandbox: true,
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [userDataArg] }
      : { args: [userDataArg, resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })
  stage('launched')
  const normal = async (page: Page) => {
    await expect(page.getByRole('heading', { level: 1 })).toContainText('转化为可验证的知识')
    expect(
      await page.locator('.app-shell').evaluate((node) => getComputedStyle(node).display),
    ).toBe('grid')
    await page.getByRole('link', { name: '模块规划' }).click()
    await expect(page.getByRole('heading', { name: '六个模块，一条学习路径' })).toBeInViewport()
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.getByRole('status')).toContainText('本地引擎已连接')
  }
  try {
    const actualUserDataPath = await application.evaluate(({ app }) => app.getPath('userData'))
    const userDataEvidencePath = testInfo.outputPath('electron-user-data.json')
    await writeFile(
      userDataEvidencePath,
      JSON.stringify({ expected: expectedUserDataPath, actual: actualUserDataPath }, null, 2) +
        '\n',
    )
    await testInfo.attach('electron-user-data', {
      path: userDataEvidencePath,
      contentType: 'application/json',
    })
    expect(actualUserDataPath).toBe(expectedUserDataPath)
    stage('first-window')
    let page = await application.firstWindow()
    stage('normal-ui')
    await normal(page)
    evidence.runtime = await application.evaluate(({ app, BrowserWindow }) => ({
      packaged: app.isPackaged,
      nativeHangMonitorEnabled: !app.commandLine.hasSwitch('disable-hang-monitor'),
      noSandboxSwitch: app.commandLine.hasSwitch('no-sandbox'),
      versions: process.versions,
      preferences: BrowserWindow.getAllWindows()[0].webContents.getLastWebPreferences(),
    }))
    expect((evidence.runtime as { noSandboxSwitch: boolean }).noSandboxSwitch).toBe(false)
    const metas = await page.locator('meta[http-equiv="Content-Security-Policy"]').allTextContents()
    expect(metas).toHaveLength(development ? 0 : 1)
    evidence.meta = development
      ? null
      : await page
          .locator('meta[http-equiv="Content-Security-Policy"]')
          .getAttribute('content')
          .catch(() => null)
    const response = await page.reload()
    evidence.responseCSP = response?.headers()['content-security-policy'] ?? null
    if (development) expect(evidence.responseCSP).toContain("'nonce-")
    else expect(evidence.responseCSP).toBe(null)
    await normal(page)
    if (development && env.I02_HMR === '1') {
      // Explicit developer-only HMR probe, always restores the exact source bytes.
      const cssPath = resolve('apps/desktop/src/renderer/src/style.css')
      const appPath = resolve('apps/desktop/src/renderer/src/App.tsx')
      const css = await readFile(cssPath)
      const component = await readFile(appPath)
      try {
        await page.evaluate(() => {
          ;(window as unknown as { hmrCanary: string }).hmrCanary = 'retained'
        })
        await writeFile(
          cssPath,
          Buffer.concat([css, Buffer.from('\n:root { --i02-hmr-probe: verified; }\n')]),
        )
        await expect
          .poll(() =>
            page.evaluate(() =>
              getComputedStyle(document.documentElement).getPropertyValue('--i02-hmr-probe').trim(),
            ),
          )
          .toBe('verified')
        await writeFile(
          appPath,
          component.toString().replace('LEARN. MODEL. UNDERSTAND.', 'I02 REFRESH VERIFIED.'),
        )
        await expect(page.getByText('I02 REFRESH VERIFIED.')).toBeVisible()
        expect(
          await page.evaluate(() => (window as unknown as { hmrCanary: string }).hmrCanary),
        ).toBe('retained')
        await expect(page.getByRole('status')).toContainText('本地引擎已连接')
        evidence.hmr = { css: true, reactRefresh: true, documentAndStateRetained: true }
      } finally {
        await writeFile(cssPath, css)
        await writeFile(appPath, component)
      }
      await expect(page.getByText('LEARN. MODEL. UNDERSTAND.')).toBeVisible()
    }
    // Native CSP violations plus visible effects and a real local HTTP receiver.
    stage('csp-probe')
    const probe = await page.evaluate(async (target) => {
      const violations: { directive: string; blocked: string; disposition: string }[] = []
      const handler = (event: SecurityPolicyViolationEvent) =>
        violations.push({
          directive: event.effectiveDirective,
          blocked: event.blockedURI,
          disposition: event.disposition,
        })
      document.addEventListener('securitypolicyviolation', handler)
      const nodes: HTMLElement[] = []
      const add = <T extends HTMLElement>(node: T): T => {
        nodes.push(node)
        document.body.append(node)
        return node
      }
      const script = document.createElement('script')
      script.textContent = 'window.__inlineProbe = true'
      add(script)
      const remote = document.createElement('script')
      remote.src = `${target}/script`
      add(remote)
      const image = document.createElement('img')
      image.src = `${target}/image`
      add(image)
      const frame = document.createElement('iframe')
      frame.src = `${target}/frame`
      add(frame)
      const style = document.createElement('style')
      style.textContent = '#csp-style-element { color: rgb(1, 2, 3) }'
      add(style)
      const element = add(document.createElement('div'))
      element.id = 'csp-style-element'
      const attribute = add(document.createElement('div'))
      attribute.setAttribute('style', 'color: rgb(2, 3, 4)')
      const cssom = add(document.createElement('div'))
      cssom.style.color = 'rgb(3, 4, 5)'
      const fetchBlocked = await fetch(`${target}/fetch`).then(
        () => false,
        () => true,
      )
      await new Promise((done) => setTimeout(done, 300))
      const marks = window as unknown as { __inlineProbe?: boolean; __remoteScript?: boolean }
      const result = {
        inlineExecuted: marks.__inlineProbe === true,
        remoteExecuted: marks.__remoteScript === true,
        styleElement: getComputedStyle(element).color === 'rgb(1, 2, 3)',
        styleAttribute: getComputedStyle(attribute).color === 'rgb(2, 3, 4)',
        cssom: getComputedStyle(cssom).color === 'rgb(3, 4, 5)',
        fetchBlocked,
        violations,
        require: typeof (window as unknown as { require?: unknown }).require,
      }
      nodes.forEach((node) => node.remove())
      document.removeEventListener('securitypolicyviolation', handler)
      return result
    }, target)
    evidence.probe = probe
    const violationProjection = compareCspViolations(
      probe.violations,
      target,
      expectedCspViolations[development ? 'development' : 'production'],
    )
    evidence.cspViolationProjection = violationProjection
    expect(probe.inlineExecuted).toBe(false)
    expect(probe.remoteExecuted).toBe(false)
    expect(probe.fetchBlocked).toBe(true)
    expect(probe.styleElement).toBe(development)
    expect(probe.styleAttribute).toBe(development)
    expect(probe.cssom).toBe(true)
    expect(probe.require).toBe('undefined')
    for (const directive of ['script-src-elem', 'img-src', 'connect-src', 'frame-src']) {
      expect(
        probe.violations.some((v) => v.directive === directive && v.disposition === 'enforce'),
      ).toBe(true)
    }
    expect(requests).toEqual([])
    evidence.receiverRequests = requests
    expect(
      { missing: violationProjection.missing, extra: violationProjection.extra },
      'complete CSP directive/disposition/blocked-class set',
    ).toEqual({ missing: [], extra: [] })
    const url = page.url()
    await page.evaluate((target) => {
      window.open(target)
      window.location.href = target
    }, target)
    await page.waitForTimeout(150)
    expect(page.url()).toBe(url)
    expect(application.windows()).toHaveLength(1)
    stage('foreign-window-create')
    const alienWindowEvent = application.waitForEvent('window')
    evidence.newContents = await application.evaluate(({ app, BrowserWindow }, url) => {
      const current = BrowserWindow.getAllWindows()[0]
      const alien = new BrowserWindow({
        show: false,
        webPreferences: {
          ...current.webContents.getLastWebPreferences(),
          preload: `${app.getAppPath()}/out/preload/index.js`,
        },
      })
      void alien.loadURL(url)
      return {
        id: alien.id,
        navigate: alien.webContents.listenerCount('will-navigate'),
        frame: alien.webContents.listenerCount('will-frame-navigate'),
        webview: alien.webContents.listenerCount('will-attach-webview'),
        preferences: alien.webContents.getLastWebPreferences(),
      }
    }, url)
    stage('foreign-window-event')
    const alien = await alienWindowEvent
    await alien.waitForFunction(() => Boolean(window.ontolearn))
    expect(await alien.evaluate(() => window.ontolearn.getEngineHealth())).toEqual({
      ok: false,
      error: {
        code: 'PERMISSION_DENIED',
        messageKey: 'permission.denied',
        params: {},
        retryable: false,
      },
    })
    await application.evaluate(
      ({ BrowserWindow }, id) => BrowserWindow.fromId(id)?.destroy(),
      (evidence.newContents as { id: number }).id,
    )
    const hardened = evidence.newContents as {
      navigate: number
      frame: number
      webview: number
      preferences: { sandbox: boolean; contextIsolation: boolean; nodeIntegration: boolean }
    }
    expect(hardened.navigate).toBeGreaterThan(0)
    expect(hardened.frame).toBeGreaterThan(0)
    expect(hardened.webview).toBeGreaterThan(0)
    expect(hardened.preferences.sandbox).toBe(true)
    expect(hardened.preferences.contextIsolation).toBe(true)
    expect(hardened.preferences.nodeIntegration).toBe(false)
    evidence.foreignSenderRejected = true
    // Capture the real native-dialog request; automate the user's recovery choice.
    await application.evaluate(({ dialog }) => {
      const state = globalThis as unknown as { recoveryPrompts: unknown[] }
      state.recoveryPrompts = []
      dialog.showMessageBox = (async (_window: unknown, options: unknown) => {
        state.recoveryPrompts.push(options)
        return { response: 0, checkboxChecked: false }
      }) as typeof dialog.showMessageBox
    })
    stage('crash-reopen')
    const reopened = application.waitForEvent('window')
    await application.evaluate(({ BrowserWindow }) =>
      BrowserWindow.getAllWindows()[0].webContents.forcefullyCrashRenderer(),
    )
    stage('reopened-window-event')
    page = await reopened
    stage('reopened-window-ui')
    await expect(page.getByRole('status')).toContainText('尚未检查')
    await normal(page)
    evidence.recoveryPrompts = await application.evaluate(
      () => (globalThis as unknown as { recoveryPrompts: unknown[] }).recoveryPrompts,
    )
    expect((evidence.recoveryPrompts as unknown[]).length).toBe(1)
    // Native executable: the test hook closes its main bootstrap inspector before faults.
    // Renderer never has CDP/Playwright's disable-hang-monitor loader.
    const nativeDir = await mkdtemp(resolve(tmpdir(), 'ontolearn-i02-'))
    const nativeOutput = resolve(nativeDir, 'native.json')
    // Playwright uses a shell launcher on Windows: process().spawnfile can be cmd.exe.
    // Read the real Electron executable from the running main process instead.
    const executable =
      env.ONTOLEARN_PACKAGED_EXECUTABLE ?? (await application.evaluate(() => process.execPath))
    const args = [`--user-data-dir=${nativeDir}`]
    if (!env.ONTOLEARN_PACKAGED_EXECUTABLE) args.push(resolve('apps/desktop'))
    evidence.nativeLaunch = { executable, args }
    stage('native-recovery')
    try {
      await runNativeRecovery(executable, args, { ...env, I02_NATIVE_EVIDENCE: nativeOutput })
    } catch (error) {
      evidence.nativeFailure = String(error)
      evidence.nativeRecovery = await readFile(nativeOutput, 'utf8')
        .then((value) => JSON.parse(value))
        .catch(() => undefined)
      throw error
    }
    evidence.nativeRecovery = JSON.parse(await readFile(nativeOutput, 'utf8'))
    const native = evidence.nativeRecovery as {
      result: string
      inspectorClosedBeforeFaults: boolean
      packaged: boolean
      hangMonitorEnabled: boolean
      noSandboxSwitch: boolean
      events: string[]
    }
    expect(native.result).toBe('PASS')
    expect(native.inspectorClosedBeforeFaults).toBe(true)
    expect(native.hangMonitorEnabled).toBe(true)
    expect(native.noSandboxSwitch).toBe(false)
    expect(native.packaged).toBe(Boolean(env.ONTOLEARN_PACKAGED_EXECUTABLE))
    // Electron documents forcefullyCrashRenderer as killed or crashed across platforms.
    expect(native.events.some((reason) => reason === 'killed' || reason === 'crashed')).toBe(true)
    expect(native.events).toContain('unresponsive')
    evidence.result = 'PASS'
  } finally {
    evidence.lastStageBeforeCleanup = evidence.stage
    stage('cleanup-enter')
    // Preserve the last reached stage even when transport cleanup itself stalls.
    if (env.I02_EVIDENCE) {
      await mkdir(resolve(env.I02_EVIDENCE, '..'), { recursive: true })
      await writeFile(env.I02_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
    }
    application.process().kill('SIGKILL')
    await application.close().catch(() => undefined)
    server.close()
    if (env.I02_EVIDENCE) {
      await mkdir(resolve(env.I02_EVIDENCE, '..'), { recursive: true })
      await writeFile(env.I02_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
    }
  }
})
