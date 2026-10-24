// Test-only instrumentation bootstrapped into the unmodified app main process.
// Main inspector is closed before faults; renderer never has inspector/CDP.
// eslint-disable-next-line @typescript-eslint/no-require-imports
const { app, dialog } = require('electron')
// eslint-disable-next-line @typescript-eslint/no-require-imports
const { writeFileSync } = require('node:fs')
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
const save = (error) => {
  if (error) evidence.error = String(error)
  writeFileSync(process.env.I02_NATIVE_EVIDENCE, JSON.stringify(evidence, null, 2) + '\n')
  app.exit(error ? 1 : 0)
}
setTimeout(() => save('native recovery timeout'), 40000).unref()
dialog.showMessageBox = async (_window, options) => {
  evidence.prompts.push(options)
  return { response: 0, checkboxChecked: false }
}
function observeWindow(window, freshlyCreated = false) {
  const index = ++evidence.windows
  window.webContents.on('render-process-gone', (_e, details) =>
    evidence.events.push(details.reason),
  )
  window.on('unresponsive', () => evidence.events.push('unresponsive'))
  const drive = async () => {
    try {
      const state = await window.webContents.executeJavaScript(
        `({ status: document.querySelector('.health-result').textContent, bridge: typeof window.ontolearn?.getEngineHealth })`,
      )
      if (!state.status.includes('尚未检查') || state.bridge !== 'function')
        throw new Error('unexpected initial state')
      evidence.health.push(
        await window.webContents.executeJavaScript('window.ontolearn.getEngineHealth()'),
      )
      if (!evidence.health.at(-1).ok) throw new Error('health unavailable')
      if (index === 1) window.webContents.forcefullyCrashRenderer()
      else if (index === 2) {
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
        void window.webContents.executeJavaScript('for (;;) {}').catch((error) => {
          if (window.isDestroyed()) evidence.hangScriptDisposed = String(error)
          else save(error)
        })
        setTimeout(() => {
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
          window.webContents.sendInputEvent({
            type: 'mouseDown',
            x: 400,
            y: 400,
            button: 'left',
            clickCount: 1,
          })
          window.webContents.sendInputEvent({
            type: 'mouseUp',
            x: 400,
            y: 400,
            button: 'left',
            clickCount: 1,
          })
        }, 250)
      } else if (index === 3) {
        if (!evidence.events.includes('unresponsive') || evidence.prompts.length !== 2)
          throw new Error('missing native events/prompts')
        evidence.result = 'PASS'
        save()
      } else throw new Error('unexpected automatic restart')
    } catch (error) {
      save(error)
    }
  }
  if (freshlyCreated || window.webContents.isLoadingMainFrame())
    window.webContents.once('did-finish-load', drive)
  else void drive()
}
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
