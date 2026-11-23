import { launchIsolatedDesktop } from './isolated-desktop'
import { test, expect, type Page } from '@playwright/test'
import { resolve } from 'node:path'
import { mkdir, mkdtemp, readFile, realpath, writeFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { runNativeRecovery } from './native-driver'
import { tmpdir } from 'node:os'

test('C1 real CSP, normal functionality and renderer recovery', async () => {
  test.setTimeout(90000)
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
  const development = Boolean(env.ELECTRON_RENDERER_URL)
  const evidence: Record<string, unknown> = { development, target }
  const stage = (value: string) => {
    evidence.stage = value
    console.info(`[I02] ${value}`)
  }
  stage('launch')
  const application = await launchIsolatedDesktop({
    chromiumSandbox: true,
    ...(env.ONTOLEARN_PACKAGED_EXECUTABLE
      ? { executablePath: env.ONTOLEARN_PACKAGED_EXECUTABLE, args: [] }
      : { args: [resolve('apps/desktop')] }),
    cwd: resolve('apps/desktop'),
    env,
  })
  stage('launched')
  let applicationClosed = false
  const closeApplication = async () => {
    if (applicationClosed) return
    applicationClosed = true
    await Promise.race([
      application.close().catch(() => undefined),
      new Promise<void>((done) => setTimeout(done, 3000).unref()),
    ])
    try {
      application.process().kill('SIGKILL')
    } catch {
      // Process may already have exited cleanly during application.close().
    }
    await application.close().catch(() => undefined)
  }
  const normal = async (page: Page) => {
    await expect(page.getByRole('heading', { level: 1 })).toContainText('转化为可验证的知识')
    expect(
      await page.locator('.app-shell').evaluate((node) => getComputedStyle(node).display),
    ).toBe('grid')
    await page.getByRole('link', { name: '模块规划' }).click()
    await expect(page.getByRole('heading', { name: '六个模块，一条学习路径' })).toBeInViewport()
    await page.getByRole('button', { name: '检查本地引擎' }).click()
    await expect(page.locator('.health-result')).toContainText('本地引擎已连接')
  }
  try {
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
        await expect(page.locator('.health-result')).toContainText('本地引擎已连接')
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
    await application.evaluate(({ BrowserWindow }) => {
      const target = BrowserWindow.getAllWindows().find(
        (candidate) => !candidate.isDestroyed() && !candidate.webContents.isDestroyed(),
      )
      if (!target) throw new Error('no live BrowserWindow to crash')
      const state = globalThis as unknown as {
        crashDiagnostics?: {
          platform: string
          initialOsPid: number | null
          renderGone: boolean
          reason: string | null
          retried: boolean
          retryOsPid: number | null
          retryCrashed: boolean | null
          killFallbackPid: number | null
          killError: string | null
        }
      }
      const diag = {
        platform: process.platform,
        initialOsPid:
          typeof target.webContents.getOSProcessId === 'function'
            ? target.webContents.getOSProcessId()
            : null,
        renderGone: false,
        reason: null as string | null,
        retried: false,
        retryOsPid: null as number | null,
        retryCrashed: null as boolean | null,
        killFallbackPid: null as number | null,
        killError: null as string | null,
      }
      state.crashDiagnostics = diag
      const timers: ReturnType<typeof setTimeout>[] = []
      const clearTimers = () => {
        for (const timer of timers) clearTimeout(timer)
        timers.length = 0
      }
      target.webContents.once('render-process-gone', (_event, details) => {
        diag.renderGone = true
        diag.reason = details.reason
        clearTimers()
      })
      target.webContents.once('destroyed', clearTimers)
      target.once('closed', clearTimers)
      // Step out of the evaluate IPC reply tick before crashing, matching native-recovery.cjs.
      const kick = setTimeout(() => {
        try {
          if (diag.renderGone || target.isDestroyed() || target.webContents.isDestroyed()) {
            clearTimers()
            return
          }
          target.webContents.forcefullyCrashRenderer()
          if (process.platform === 'win32') {
            const retryTimer = setTimeout(() => {
              try {
                if (diag.renderGone || target.isDestroyed() || target.webContents.isDestroyed()) {
                  clearTimers()
                  return
                }
                diag.retried = true
                diag.retryOsPid =
                  typeof target.webContents.getOSProcessId === 'function'
                    ? target.webContents.getOSProcessId()
                    : null
                diag.retryCrashed =
                  typeof target.webContents.isCrashed === 'function'
                    ? target.webContents.isCrashed()
                    : null
                target.webContents.forcefullyCrashRenderer()
                const fallbackTimer = setTimeout(() => {
                  try {
                    if (
                      diag.renderGone ||
                      target.isDestroyed() ||
                      target.webContents.isDestroyed()
                    ) {
                      clearTimers()
                      return
                    }
                    const pid =
                      typeof target.webContents.getOSProcessId === 'function'
                        ? target.webContents.getOSProcessId()
                        : 0
                    diag.killFallbackPid = pid
                    if (pid > 0 && typeof process.kill === 'function') process.kill(pid)
                  } catch (killError) {
                    diag.killError = String(killError)
                  }
                }, 1500)
                fallbackTimer.unref()
                timers.push(fallbackTimer)
              } catch (retryError) {
                diag.killError = String(retryError)
              }
            }, 1500)
            retryTimer.unref()
            timers.push(retryTimer)
          }
        } catch (kickError) {
          diag.killError = String(kickError)
        }
      }, 0)
      kick.unref()
      timers.push(kick)
    })
    stage('reopened-window-event')
    try {
      page = await reopened
    } catch (error) {
      let crashDiagnostics: unknown = null
      let recoveryPrompts: unknown = null
      try {
        const snapshot = await application.evaluate(() => {
          const state = globalThis as unknown as {
            crashDiagnostics?: unknown
            recoveryPrompts?: unknown
          }
          return {
            crashDiagnostics: state.crashDiagnostics ?? null,
            recoveryPrompts: state.recoveryPrompts ?? null,
          }
        })
        crashDiagnostics = snapshot.crashDiagnostics
        recoveryPrompts = snapshot.recoveryPrompts
      } catch (diagError) {
        crashDiagnostics = { evaluateError: String(diagError) }
      }
      evidence.crashDiagnostics = crashDiagnostics
      evidence.recoveryPrompts = recoveryPrompts
      console.error(
        '[I02] crash-reopen-failed',
        JSON.stringify({ crashDiagnostics, recoveryPrompts }),
      )
      throw error
    }
    evidence.crashDiagnostics = await application.evaluate(
      () => (globalThis as unknown as { crashDiagnostics?: unknown }).crashDiagnostics ?? null,
    )
    stage('reopened-window-ui')
    await expect(page.locator('.health-result')).toContainText('尚未检查')
    await normal(page)
    evidence.recoveryPrompts = await application.evaluate(
      () => (globalThis as unknown as { recoveryPrompts: unknown[] }).recoveryPrompts,
    )
    expect((evidence.recoveryPrompts as unknown[]).length).toBe(1)
    // The captured dialog options must mirror window-recovery.ts exactly.
    const recoveryPrompt = (evidence.recoveryPrompts as Array<Record<string, unknown>>)[0]
    expect(recoveryPrompt.type).toBe('warning')
    expect(recoveryPrompt.title).toBe('OntoLearn Studio 窗口恢复')
    expect(recoveryPrompt.message).toBe('显示窗口已停止运行。')
    expect(String(recoveryPrompt.detail)).toContain('不会重新执行写任务')
    // Native executable: the test hook closes its main bootstrap inspector before faults.
    // Renderer never has CDP/Playwright's disable-hang-monitor loader.
    const nativeDir = await realpath(await mkdtemp(resolve(tmpdir(), 'ontolearn-i02-')))
    const nativeOutput = resolve(nativeDir, 'native.json')
    // Playwright uses a shell launcher on Windows: process().spawnfile can be cmd.exe.
    // Read the real Electron executable from the running main process instead.
    const executable =
      env.ONTOLEARN_PACKAGED_EXECUTABLE ?? (await application.evaluate(() => process.execPath))
    const args = [`--user-data-dir=${nativeDir}`]
    if (!env.ONTOLEARN_PACKAGED_EXECUTABLE) args.push(resolve('apps/desktop'))
    evidence.nativeLaunch = { executable, args }
    stage('close-playwright-desktop-before-native')
    await closeApplication()
    stage('native-recovery')
    try {
      await runNativeRecovery(
        executable,
        args,
        { ...env, I02_NATIVE_EVIDENCE: nativeOutput },
        !env.ONTOLEARN_PACKAGED_EXECUTABLE && process.platform === 'win32'
          ? { bootstrap: 'preload', cwd: resolve('apps/desktop') }
          : undefined,
      )
    } catch (error) {
      // Failure-only evidence: Windows does not set I02_EVIDENCE. Read once,
      // preserve the actual bytes, and distinguish read, parse and attachment failures.
      const capture: Record<string, unknown> = {
        source: 'existing nativeOutput after original native failure',
        path: nativeOutput,
        read: 'not-attempted',
        parse: 'not-attempted',
        rawAttachment: 'not-attempted',
      }
      try {
        evidence.nativeFailure = String(error)
        let raw: Buffer | undefined
        try {
          raw = await readFile(nativeOutput)
          capture.read = 'succeeded'
          capture.bytes = raw.byteLength
        } catch (readError) {
          capture.read =
            readError !== null &&
            typeof readError === 'object' &&
            'code' in readError &&
            readError.code === 'ENOENT'
              ? 'not-found'
              : 'failed'
          capture.readError = String(readError)
        }
        if (raw !== undefined) {
          try {
            evidence.nativeRecovery = JSON.parse(raw.toString('utf8'))
            capture.parse = 'succeeded'
          } catch (parseError) {
            capture.parse = 'failed'
            capture.parseError = String(parseError)
          }
          try {
            await test.info().attach('c1-native-failure-original-bytes', {
              body: raw,
              contentType: 'application/octet-stream',
            })
            capture.rawAttachment = 'succeeded'
          } catch (attachmentError) {
            capture.rawAttachment = 'failed'
            capture.rawAttachmentError = String(attachmentError)
          }
        }
        evidence.nativeFailureCapture = capture
        await test.info().attach('c1-native-failure-capture-status', {
          body: JSON.stringify(capture),
          contentType: 'application/json',
        })
      } catch (captureError) {
        // This is diagnostic failure, never a substitute for the native error.
        try {
          capture.captureError = String(captureError)
          evidence.nativeFailureCapture = capture
        } catch {
          // Even diagnostic error formatting may fail; preserve the native error.
        }
      }
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
      prompts?: Array<Record<string, unknown>>
    }
    expect(native.result).toBe('PASS')
    expect(native.inspectorClosedBeforeFaults).toBe(true)
    expect(native.hangMonitorEnabled).toBe(true)
    expect(native.noSandboxSwitch).toBe(false)
    expect(native.packaged).toBe(Boolean(env.ONTOLEARN_PACKAGED_EXECUTABLE))
    // Electron documents forcefullyCrashRenderer as killed or crashed across platforms.
    expect(native.events.some((reason) => reason === 'killed' || reason === 'crashed')).toBe(true)
    expect(native.events).toContain('unresponsive')
    // Both native recovery dialogs must mirror window-recovery.ts exactly.
    expect(native.prompts?.length).toBe(2)
    expect(native.prompts?.[0]?.type).toBe('warning')
    expect(native.prompts?.[0]?.title).toBe('OntoLearn Studio 窗口恢复')
    expect(native.prompts?.[0]?.message).toBe('显示窗口已停止运行。')
    expect(String(native.prompts?.[0]?.detail)).toContain('不会重新执行写任务')
    expect(native.prompts?.[1]?.type).toBe('warning')
    expect(native.prompts?.[1]?.title).toBe('OntoLearn Studio 窗口恢复')
    expect(native.prompts?.[1]?.message).toBe('显示窗口暂时没有响应。')
    expect(String(native.prompts?.[1]?.detail)).toContain('不会重新执行写任务')
    evidence.result = 'PASS'
  } finally {
    evidence.lastStageBeforeCleanup = evidence.stage
    stage('cleanup-enter')
    // Preserve the last reached stage even when transport cleanup itself stalls.
    if (env.I02_EVIDENCE) {
      await mkdir(resolve(env.I02_EVIDENCE, '..'), { recursive: true })
      await writeFile(env.I02_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
    }
    await closeApplication()
    server.close()
    if (env.I02_EVIDENCE) {
      await mkdir(resolve(env.I02_EVIDENCE, '..'), { recursive: true })
      await writeFile(env.I02_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
    }
  }
})
