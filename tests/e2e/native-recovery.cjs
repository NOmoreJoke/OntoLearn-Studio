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
        `({ status: document.querySelector('[role=status]').textContent, bridge: typeof window.ontolearn?.getEngineHealth })`,
      )
      if (!state.status.includes('尚未检查') || state.bridge !== 'function')
        throw new Error('unexpected initial state')
      evidence.health.push(
        await window.webContents.executeJavaScript('window.ontolearn.getEngineHealth()'),
      )
      if (!evidence.health.at(-1).ok) throw new Error('health unavailable')
      if (index === 1) window.webContents.forcefullyCrashRenderer()
      else if (index === 2) {
        await window.webContents.executeJavaScript('setTimeout(() => { for (;;) {} }, 50); "armed"')
        setTimeout(() => {
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
        }, 200)
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
