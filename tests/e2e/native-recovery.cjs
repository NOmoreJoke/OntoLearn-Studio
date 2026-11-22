// Test-only instrumentation bootstrapped into the unmodified app main process.
// Main inspector is closed before faults; renderer never has inspector/CDP.
// eslint-disable-next-line @typescript-eslint/no-require-imports
const electron = require('electron')
const { app } = electron
// eslint-disable-next-line @typescript-eslint/no-require-imports
const { writeFileSync } = require('node:fs')
// -r preload runs this file before app readiness; the inspector bootstrap runs
// the same helper only after the Electron main API finished installing.
const preloadedBeforeReady = typeof app.isReady === 'function' && app.isReady() === false
const evidence = {
  windows: 0,
  prompts: [],
  events: [],
  health: [],
  packaged: app.isPackaged,
  hangMonitorEnabled: !app.commandLine.hasSwitch('disable-hang-monitor'),
  noSandboxSwitch: app.commandLine.hasSwitch('no-sandbox'),
  versions: process.versions,
}
// Passive main-process evidence only. Issued calls and synchronous input returns
// do not acknowledge renderer execution or entry into product recovery handlers.
const passiveFailure = (() => {
  const max = 2147483647
  const limitRecords = 16
  const limitBytes = 4096
  const counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  const rows = []
  let sequence = 0
  let cursor = 0
  let size = 0
  let overwritten = 0
  let readErrors = 0
  let latestWindow
  const increment = (value) => (value < max ? value + 1 : max)
  const number = (value) => (Number.isInteger(value) && value >= 0 && value <= max ? value : -1)
  const read = (work) => {
    try {
      return work()
    } catch {
      readErrors = increment(readErrors)
      return undefined
    }
  }
  const flag = (work) => {
    const value = read(work)
    return value === true ? 1 : value === false ? 0 : -1
  }
  const record = (code, window) => {
    try {
      if (code === 0) latestWindow = window // At most one retained window alias.
      sequence = increment(sequence)
      counts[code] = increment(counts[code])
      const target = window ?? latestWindow
      const contents = read(() => target.webContents)
      const destroyed = flag(() => target.isDestroyed())
      rows[cursor] = [
        sequence,
        code,
        number(read(() => target.id)),
        number(read(() => contents.id)),
        destroyed,
        destroyed === 1 ? -1 : flag(() => target.isVisible()),
        destroyed === 1 ? -1 : flag(() => target.isFocused()),
        flag(() => contents.isDestroyed()),
      ]
      cursor = (cursor + 1) % limitRecords
      if (size < limitRecords) size++
      else overwritten = increment(overwritten)
    } catch {
      // Even failed diagnostic reads/recording must not change the original path.
    }
  }
  const failure = () => {
    try {
      record(15, latestWindow)
      const records = []
      for (let i = 0; i < size; i++)
        records.push(rows[(cursor - size + i + limitRecords) % limitRecords])
      const value = {
        schema: 'c1-native-passive-v1',
        limitBytes,
        limitRecords,
        sequence,
        overwritten,
        readErrors,
        counts,
        codes: [
          'observe-window',
          'registered',
          'drive-enter',
          'render-gone',
          'unresponsive',
          'dialog-stub',
          'fault-call-boundary',
          'fault-promise-returned',
          'fault-rejected',
          'input-callback',
          'down-call-boundary',
          'down-returned',
          'up-call-boundary',
          'up-returned',
          'drive-error',
          'save-failure',
        ],
        fields: [
          'sequence',
          'code',
          'windowId',
          'webContentsId',
          'destroyed',
          'visible',
          'focused',
          'webContentsDestroyed',
        ],
        records,
        rendererLoopStarted: 'UNKNOWN',
        productHandlerEntered: 'UNKNOWN',
      }
      // Match the original two-space save format, including this added property.
      if (
        Buffer.byteLength(JSON.stringify({ failureObservation: value }, null, 2), 'utf8') >
        limitBytes
      )
        return {
          schema: value.schema,
          limitBytes,
          unavailable: 'byte-cap',
          rendererLoopStarted: 'UNKNOWN',
          productHandlerEntered: 'UNKNOWN',
        }
      return value
    } catch {
      return undefined
    }
  }
  return { record, failure }
})()
const save = (error) => {
  if (error) {
    evidence.error = String(error)
    try {
      const extra = passiveFailure.failure()
      if (extra !== undefined) evidence.failureObservation = extra
    } catch {
      // Original error formatting, write and exit remain the authoritative path.
    }
  }
  writeFileSync(process.env.I02_NATIVE_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
  app.exit(error ? 1 : 0)
}
setTimeout(() => save('native recovery timeout'), 40000).unref()
function installDialogStub() {
  electron.dialog.showMessageBox = async (_window, options) => {
    passiveFailure.record(5, _window)
    evidence.prompts.push(options)
    return { response: 0, checkboxChecked: false }
  }
}
function observeWindow(window, freshlyCreated = false) {
  const index = ++evidence.windows
  let renderGone = false
  passiveFailure.record(0, window)
  window.webContents.on('render-process-gone', (_e, details) => {
    renderGone = true
    passiveFailure.record(3, window)
    return evidence.events.push(details.reason)
  })
  window.on('unresponsive', () => {
    passiveFailure.record(4, window)
    return evidence.events.push('unresponsive')
  })
  passiveFailure.record(1, window)
  const drive = async () => {
    try {
      passiveFailure.record(2, window)
      const state = await window.webContents.executeJavaScript(
        `({ status: document.querySelector('.health-result').textContent, bridge: typeof window.ontolearn?.getEngineHealth })`,
      )
      if (!state.status.includes('尚未检查') || state.bridge !== 'function')
        throw new Error('unexpected initial state')
      evidence.health.push(
        await window.webContents.executeJavaScript('window.ontolearn.getEngineHealth()'),
      )
      if (!evidence.health.at(-1).ok) throw new Error('health unavailable')
      if (index === 1) {
        if (process.platform === 'win32') {
          if (preloadedBeforeReady) {
            // Wait until the renderer OS process actually exists (visible window
            // with a live OS PID), then let Win32 launch/watchers settle 400ms.
            const crashTargetReady = () =>
              !window.isDestroyed() &&
              !window.webContents.isDestroyed() &&
              (typeof window.isVisible !== 'function' || window.isVisible()) &&
              (typeof window.webContents.getOSProcessId !== 'function' ||
                window.webContents.getOSProcessId() > 0)
            const pollDeadline = Date.now() + 5000
            while (!crashTargetReady()) {
              if (Date.now() >= pollDeadline)
                throw new Error('win32 crash target never became ready')
              await new Promise((resolve) => setTimeout(resolve, 50))
            }
            await new Promise((resolve) => setTimeout(resolve, 400))
          } else {
            // Step out of the executeJavaScript Mojo IPC reply microtask before crashing.
            await new Promise((resolve) => setTimeout(resolve, 0))
          }
          if (!renderGone && !window.isDestroyed() && !window.webContents.isDestroyed())
            window.webContents.forcefullyCrashRenderer()
          if (!renderGone) {
            setTimeout(() => {
              try {
                if (renderGone || window.isDestroyed() || window.webContents.isDestroyed()) return
                evidence.win32CrashRetry = {
                  osPid:
                    typeof window.webContents.getOSProcessId === 'function'
                      ? window.webContents.getOSProcessId()
                      : null,
                  crashed:
                    typeof window.webContents.isCrashed === 'function'
                      ? window.webContents.isCrashed()
                      : null,
                }
                window.webContents.forcefullyCrashRenderer()
                setTimeout(() => {
                  try {
                    if (renderGone || window.isDestroyed() || window.webContents.isDestroyed())
                      return
                    const pid =
                      typeof window.webContents.getOSProcessId === 'function'
                        ? window.webContents.getOSProcessId()
                        : 0
                    evidence.win32CrashKillFallback = { pid }
                    if (pid > 0 && typeof process.kill === 'function') process.kill(pid)
                  } catch (killError) {
                    evidence.win32CrashKillError = String(killError)
                    try {
                      evidence.win32PostKillState = {
                        osPid:
                          typeof window.webContents.getOSProcessId === 'function'
                            ? window.webContents.getOSProcessId()
                            : null,
                        processId:
                          typeof window.webContents.getProcessId === 'function'
                            ? window.webContents.getProcessId()
                            : null,
                        crashed:
                          typeof window.webContents.isCrashed === 'function'
                            ? window.webContents.isCrashed()
                            : null,
                        destroyed: window.isDestroyed(),
                        webContentsDestroyed: window.webContents.isDestroyed(),
                        windowCount:
                          typeof electron.BrowserWindow?.getAllWindows === 'function'
                            ? electron.BrowserWindow.getAllWindows().length
                            : null,
                      }
                    } catch {
                      // Bounded diagnostics must never mask the original kill error.
                    }
                  }
                }, 1500).unref()
              } catch (retryError) {
                evidence.win32CrashRetryError = String(retryError)
              }
            }, 1500).unref()
          }
        } else window.webContents.forcefullyCrashRenderer()
      } else if (index === 2) {
        window.show()
        app.focus({ steal: true })
        window.focus()
        const focusDeadline = Date.now() + 3000
        while (!window.isFocused() || !window.isVisible()) {
          if (Date.now() >= focusDeadline)
            throw new Error('native hang requires a focused visible window')
          await new Promise((resolve) => setTimeout(resolve, 50))
        }
        // Start the actual blocking script directly. A renderer timer can be throttled,
        // allowing input to be handled before the scheduled loop begins.
        evidence.hangFault = 'executeJavaScript-infinite-loop'
        passiveFailure.record(6, window)
        void window.webContents.executeJavaScript('for (;;) {}').catch((error) => {
          passiveFailure.record(8, window)
          if (window.isDestroyed()) evidence.hangScriptDisposed = String(error)
          else save(error)
        })
        passiveFailure.record(7, window)
        setTimeout(() => {
          passiveFailure.record(9, window)
          evidence.hangTrigger = {
            time: new Date().toISOString(),
            visible: window.isVisible(),
            focused: window.isFocused(),
            hangMonitorEnabled: !app.commandLine.hasSwitch('disable-hang-monitor'),
          }
          if (!evidence.hangTrigger.visible || !evidence.hangTrigger.focused) {
            save('native hang input requires a focused visible window')
            return
          }
          passiveFailure.record(10, window)
          window.webContents.sendInputEvent({
            type: 'mouseDown',
            x: 400,
            y: 400,
            button: 'left',
            clickCount: 1,
          })
          passiveFailure.record(11, window)
          passiveFailure.record(12, window)
          window.webContents.sendInputEvent({
            type: 'mouseUp',
            x: 400,
            y: 400,
            button: 'left',
            clickCount: 1,
          })
          passiveFailure.record(13, window)
        }, 250)
      } else if (index === 3) {
        if (!evidence.events.includes('unresponsive') || evidence.prompts.length !== 2)
          throw new Error('missing native events/prompts')
        // Both prompts must mirror window-recovery.ts exactly. The unit-test VM
        // harness records bare option objects, so only present fields compare;
        // real dialog options always carry every field below.
        const expectedPrompts = [
          {
            type: 'warning',
            title: 'OntoLearn Studio 窗口恢复',
            message: '显示窗口已停止运行。',
            detail: '不会重新执行写任务',
          },
          {
            type: 'warning',
            title: 'OntoLearn Studio 窗口恢复',
            message: '显示窗口暂时没有响应。',
            detail: '不会重新执行写任务',
          },
        ]
        expectedPrompts.forEach((expected, position) => {
          const prompt = evidence.prompts[position]
          for (const [field, value] of Object.entries(expected)) {
            const recorded = prompt[field]
            if (recorded === undefined) continue
            const matches =
              field === 'detail' ? String(recorded).includes(value) : String(recorded) === value
            if (!matches) throw new Error(`recovery prompt ${position} ${field} mismatch`)
          }
        })
        evidence.result = 'PASS'
        save()
      } else throw new Error('unexpected automatic restart')
    } catch (error) {
      passiveFailure.record(14, window)
      save(error)
    }
  }
  if (freshlyCreated || window.webContents.isLoadingMainFrame())
    window.webContents.once('did-finish-load', drive)
  else void drive()
}
if (!preloadedBeforeReady) {
  installDialogStub()
  // Close the bootstrap MAIN inspector before fault injection. Renderer was never attached.
  setTimeout(() => {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const inspector = require('node:inspector')
    inspector.close()
    evidence.inspectorClosedBeforeFaults = inspector.url() === undefined
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { BrowserWindow } = require('electron')
    app.on('browser-window-created', (_event, window) => observeWindow(window, true))
    for (const window of BrowserWindow.getAllWindows()) observeWindow(window)
  }, 150)
} else {
  // Preloaded before readiness: defer every dialog/BrowserWindow touch to whenReady.
  void app.whenReady().then(() => {
    evidence.packaged = app.isPackaged
    evidence.hangMonitorEnabled = !app.commandLine.hasSwitch('disable-hang-monitor')
    evidence.noSandboxSwitch = app.commandLine.hasSwitch('no-sandbox')
    installDialogStub()
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const inspector = require('node:inspector')
    inspector.close()
    evidence.inspectorClosedBeforeFaults = inspector.url() === undefined
    const { BrowserWindow } = electron
    app.on('browser-window-created', (_event, window) => observeWindow(window, true))
    for (const window of BrowserWindow.getAllWindows()) observeWindow(window)
  })
}
