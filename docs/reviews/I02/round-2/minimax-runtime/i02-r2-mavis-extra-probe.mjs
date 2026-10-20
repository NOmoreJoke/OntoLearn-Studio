// Read-only adversarial probe (temporary, /tmp only).
// Verifies CSP directives not covered by the frozen matrix and the preload surface.
import { createServer } from 'node:http'
import { resolve } from 'node:path'
import { createRequire } from 'node:module'

const repo = '/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio'
const { _electron: electron } = createRequire(`${repo}/package.json`)('@playwright/test')
const executable = `${repo}/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio`
const requests = []
const server = createServer((req, res) => {
  requests.push(req.url ?? '')
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.end('ok')
})
await new Promise((r) => server.listen(0, '127.0.0.1', r))
const port = server.address().port
const target = `http://127.0.0.1:${port}`

const app = await electron.launch({ executablePath: executable, args: [], cwd: resolve(repo, 'apps/desktop') })
try {
  const page = await app.firstWindow()
  const out = await page.evaluate(async (t) => {
    const violations = []
    const handler = (e) => violations.push({ d: e.effectiveDirective, disp: e.disposition, uri: e.blockedURI })
    document.addEventListener('securitypolicyviolation', handler)
    const base = document.createElement('base')
    base.setAttribute('href', 'https://evil.example/')
    document.head.append(base)
    const form = document.createElement('form')
    form.setAttribute('action', t)
    document.body.append(form)
    form.submit()
    const obj = document.createElement('object')
    obj.setAttribute('data', `${t}/object`)
    document.body.append(obj)
    await new Promise((r) => setTimeout(r, 400))
    const r = {
      baseURI: document.baseURI,
      baseUriViolation: violations.some((v) => v.d === 'base-uri' && v.disp === 'enforce'),
      formActionViolation: violations.some((v) => v.d === 'form-action' && v.disp === 'enforce'),
      objectSrcViolation: violations.some((v) => v.d === 'object-src' && v.disp === 'enforce'),
      allViolations: violations.map((v) => `${v.d}:${v.disp}`),
      bridgeKeys: Object.keys(window.ontolearn ?? {}),
      bridgeProto: Object.getOwnPropertyNames(Object.getPrototypeOf(window.ontolearn ?? {})),
      hasIpcRenderer: typeof window.ipcRenderer,
      hasRequire: typeof window.require,
      hasProcess: typeof window.process,
      hasElectron: typeof window.electron,
      location: window.location.href,
    }
    document.removeEventListener('securitypolicyviolation', handler)
    return r
  }, target)
  console.log(JSON.stringify({ probe: out, receiverRequests: requests }, null, 2))
} finally {
  app.process().kill('SIGKILL')
  await app.close().catch(() => undefined)
  server.close()
}
