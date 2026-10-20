// Temporary read-only probe in /tmp: renderer-initiated navigation behaviour under
// the app's global will-navigate / will-frame-navigate hardening.
import { createRequire } from 'node:module'
const repo = '/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio'
const { _electron: electron } = createRequire(`${repo}/package.json`)('@playwright/test')

const executable = `${repo}/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio`
const app = await electron.launch({ executablePath: executable, args: [], cwd: `${repo}/apps/desktop` })
try {
  const page = await app.firstWindow()
  await page.evaluate(() => {
    window.__marker = 'before-reload'
  })
  const reloadOutcome = await page.evaluate(async () => {
    let pushStateError = null
    try {
      history.pushState({}, '', '/modules')
    } catch (error) {
      pushStateError = String(error)
    }
    let locationReloadError = null
    try {
      location.reload()
    } catch (error) {
      locationReloadError = String(error)
    }
    await new Promise((r) => setTimeout(r, 1500))
    return {
      pushStateError,
      locationReloadError,
      markerSurvived: window.__marker === 'before-reload',
      href: location.href,
      hash: location.hash,
      pathname: location.pathname,
    }
  })
  // The page may have been torn down by a successful reload; re-read after settle.
  let after = null
  try {
    after = await page.evaluate(() => ({
      marker: window.__marker ?? null,
      href: location.href,
      pathname: location.pathname,
      hash: location.hash,
    }))
  } catch (error) {
    after = { evaluationError: String(error).slice(0, 200) }
  }
  console.log(JSON.stringify({ reloadOutcome, after }, null, 2))
} finally {
  app.process().kill('SIGKILL')
  await app.close().catch(() => undefined)
}
