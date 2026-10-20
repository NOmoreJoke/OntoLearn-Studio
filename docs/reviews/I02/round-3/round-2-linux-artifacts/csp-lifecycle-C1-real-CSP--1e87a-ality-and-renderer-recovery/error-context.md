# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: csp-lifecycle.spec.ts >> C1 real CSP, normal functionality and renderer recovery
- Location: tests/e2e/csp-lifecycle.spec.ts:9:5

# Error details

```
Error: expect(received).toContain(expected) // indexOf

Expected value: "killed"
Received array: ["crashed", "unresponsive"]
```

# Test source

```ts
  195 |     evidence.newContents = await application.evaluate(({ app, BrowserWindow }, url) => {
  196 |       const current = BrowserWindow.getAllWindows()[0]
  197 |       const alien = new BrowserWindow({
  198 |         show: false,
  199 |         webPreferences: {
  200 |           ...current.webContents.getLastWebPreferences(),
  201 |           preload: `${app.getAppPath()}/out/preload/index.js`,
  202 |         },
  203 |       })
  204 |       void alien.loadURL(url)
  205 |       return {
  206 |         id: alien.id,
  207 |         navigate: alien.webContents.listenerCount('will-navigate'),
  208 |         frame: alien.webContents.listenerCount('will-frame-navigate'),
  209 |         webview: alien.webContents.listenerCount('will-attach-webview'),
  210 |         preferences: alien.webContents.getLastWebPreferences(),
  211 |       }
  212 |     }, url)
  213 |     stage('foreign-window-event')
  214 |     const alien = await alienWindowEvent
  215 |     await alien.waitForFunction(() => Boolean(window.ontolearn))
  216 |     expect(await alien.evaluate(() => window.ontolearn.getEngineHealth())).toEqual({
  217 |       ok: false,
  218 |       error: '请求来源不受信任。',
  219 |     })
  220 |     await application.evaluate(
  221 |       ({ BrowserWindow }, id) => BrowserWindow.fromId(id)?.destroy(),
  222 |       (evidence.newContents as { id: number }).id,
  223 |     )
  224 |     const hardened = evidence.newContents as {
  225 |       navigate: number
  226 |       frame: number
  227 |       webview: number
  228 |       preferences: { sandbox: boolean; contextIsolation: boolean; nodeIntegration: boolean }
  229 |     }
  230 |     expect(hardened.navigate).toBeGreaterThan(0)
  231 |     expect(hardened.frame).toBeGreaterThan(0)
  232 |     expect(hardened.webview).toBeGreaterThan(0)
  233 |     expect(hardened.preferences.sandbox).toBe(true)
  234 |     expect(hardened.preferences.contextIsolation).toBe(true)
  235 |     expect(hardened.preferences.nodeIntegration).toBe(false)
  236 |     evidence.foreignSenderRejected = true
  237 |     // Capture the real native-dialog request; automate the user's recovery choice.
  238 |     await application.evaluate(({ dialog }) => {
  239 |       const state = globalThis as unknown as { recoveryPrompts: unknown[] }
  240 |       state.recoveryPrompts = []
  241 |       dialog.showMessageBox = (async (_window: unknown, options: unknown) => {
  242 |         state.recoveryPrompts.push(options)
  243 |         return { response: 0, checkboxChecked: false }
  244 |       }) as typeof dialog.showMessageBox
  245 |     })
  246 |     stage('crash-reopen')
  247 |     const reopened = application.waitForEvent('window')
  248 |     await application.evaluate(({ BrowserWindow }) =>
  249 |       BrowserWindow.getAllWindows()[0].webContents.forcefullyCrashRenderer(),
  250 |     )
  251 |     stage('reopened-window-event')
  252 |     page = await reopened
  253 |     stage('reopened-window-ui')
  254 |     await expect(page.getByRole('status')).toContainText('尚未检查')
  255 |     await normal(page)
  256 |     evidence.recoveryPrompts = await application.evaluate(
  257 |       () => (globalThis as unknown as { recoveryPrompts: unknown[] }).recoveryPrompts,
  258 |     )
  259 |     expect((evidence.recoveryPrompts as unknown[]).length).toBe(1)
  260 |     // Native executable: the test hook closes its main bootstrap inspector before faults.
  261 |     // Renderer never has CDP/Playwright's disable-hang-monitor loader.
  262 |     const nativeDir = await mkdtemp(resolve(tmpdir(), 'ontolearn-i02-'))
  263 |     const nativeOutput = resolve(nativeDir, 'native.json')
  264 |     // Playwright uses a shell launcher on Windows: process().spawnfile can be cmd.exe.
  265 |     // Read the real Electron executable from the running main process instead.
  266 |     const executable =
  267 |       env.ONTOLEARN_PACKAGED_EXECUTABLE ?? (await application.evaluate(() => process.execPath))
  268 |     const args = [`--user-data-dir=${nativeDir}`]
  269 |     if (!env.ONTOLEARN_PACKAGED_EXECUTABLE) args.push(resolve('apps/desktop'))
  270 |     evidence.nativeLaunch = { executable, args }
  271 |     stage('native-recovery')
  272 |     try {
  273 |       await runNativeRecovery(executable, args, { ...env, I02_NATIVE_EVIDENCE: nativeOutput })
  274 |     } catch (error) {
  275 |       evidence.nativeFailure = String(error)
  276 |       evidence.nativeRecovery = await readFile(nativeOutput, 'utf8')
  277 |         .then((value) => JSON.parse(value))
  278 |         .catch(() => undefined)
  279 |       throw error
  280 |     }
  281 |     evidence.nativeRecovery = JSON.parse(await readFile(nativeOutput, 'utf8'))
  282 |     const native = evidence.nativeRecovery as {
  283 |       result: string
  284 |       inspectorClosedBeforeFaults: boolean
  285 |       packaged: boolean
  286 |       hangMonitorEnabled: boolean
  287 |       noSandboxSwitch: boolean
  288 |       events: string[]
  289 |     }
  290 |     expect(native.result).toBe('PASS')
  291 |     expect(native.inspectorClosedBeforeFaults).toBe(true)
  292 |     expect(native.hangMonitorEnabled).toBe(true)
  293 |     expect(native.noSandboxSwitch).toBe(false)
  294 |     expect(native.packaged).toBe(Boolean(env.ONTOLEARN_PACKAGED_EXECUTABLE))
> 295 |     expect(native.events).toContain('killed')
      |                           ^ Error: expect(received).toContain(expected) // indexOf
  296 |     expect(native.events).toContain('unresponsive')
  297 |     evidence.result = 'PASS'
  298 |   } finally {
  299 |     evidence.lastStageBeforeCleanup = evidence.stage
  300 |     stage('cleanup-enter')
  301 |     // Preserve the last reached stage even when transport cleanup itself stalls.
  302 |     if (env.I02_EVIDENCE) {
  303 |       await mkdir(resolve(env.I02_EVIDENCE, '..'), { recursive: true })
  304 |       await writeFile(env.I02_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
  305 |     }
  306 |     application.process().kill('SIGKILL')
  307 |     await application.close().catch(() => undefined)
  308 |     server.close()
  309 |     if (env.I02_EVIDENCE) {
  310 |       await mkdir(resolve(env.I02_EVIDENCE, '..'), { recursive: true })
  311 |       await writeFile(env.I02_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
  312 |     }
  313 |   }
  314 | })
  315 | 
```