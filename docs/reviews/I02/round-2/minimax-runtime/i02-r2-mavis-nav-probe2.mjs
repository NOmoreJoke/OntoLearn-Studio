// Temporary read-only probe in /tmp (isolated cases):
// A) renderer-initiated location.reload() alone, no pushState
// B) health IPC trust check after history.pushState
import { createRequire } from 'node:module'
const repo = '/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio'
const { _electron: electron } = createRequire(`${repo}/package.json`)('@playwright/test')
const executable = `${repo}/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio`

// ---- Case A: reload only ----
{
  const app = await electron.launch({ executablePath: executable, args: [], cwd: `${repo}/apps/desktop` })
  try {
    const page = await app.firstWindow()
    await page.evaluate(() => {
      window.__marker = 'before-reload'
    })
    const r = await page.evaluate(async () => {
      let err = null
      try {
        location.reload()
      } catch (error) {
        err = String(error)
      }
      await new Promise((r) => setTimeout(r, 2000))
      return { err, markerSurvived: window.__marker === 'before-reload', href: location.href }
    })
    console.log('CASE A (reload only):', JSON.stringify(r))
  } finally {
    app.process().kill('SIGKILL')
    await app.close().catch(() => undefined)
  }
}

// ---- Case B: pushState then health IPC ----
{
  const app = await electron.launch({ executablePath: executable, args: [], cwd: `${repo}/apps/desktop` })
  try {
    const page = await app.firstWindow()
    const r = await page.evaluate(async () => {
      const before = await window.ontolearn.getEngineHealth()
      let pushError = null
      try {
        history.pushState({}, '', '/modules')
      } catch (error) {
        pushError = String(error)
      }
      const after = await window.ontolearn.getEngineHealth()
      return { before, pushError, after, href: location.href }
    })
    console.log('CASE B (pushState + health):', JSON.stringify(r))
  } finally {
    app.process().kill('SIGKILL')
    await app.close().catch(() => undefined)
  }
}
