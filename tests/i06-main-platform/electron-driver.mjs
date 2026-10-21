import { spawn } from 'node:child_process'
import { chromium } from '@playwright/test'

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))
class Inspector {
  constructor(socket) {
    this.socket = socket
    this.next = 1
    this.pending = new Map()
    socket.addEventListener('message', ({ data }) => {
      const message = JSON.parse(data)
      if (!message.id) return
      const entry = this.pending.get(message.id)
      if (!entry) return
      this.pending.delete(message.id)
      clearTimeout(entry.timer)
      if (message.error) entry.reject(new Error('MAIN_INSPECTOR_PROTOCOL_ERROR'))
      else entry.resolve(message.result)
    })
    socket.addEventListener('close', () => {
      for (const entry of this.pending.values()) {
        clearTimeout(entry.timer)
        entry.reject(new Error('MAIN_INSPECTOR_CLOSED'))
      }
      this.pending.clear()
    })
  }
  request(method, params) {
    const id = this.next++
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error('MAIN_INSPECTOR_DEADLINE'))
      }, 10000)
      this.pending.set(id, { resolve, reject, timer })
      this.socket.send(JSON.stringify({ id, method, params }))
    })
  }
  async evaluate(fn) {
    const expression = `(${fn.toString()})(process.getBuiltinModule('node:module').createRequire('/workspace/apps/desktop/package.json')('electron'))`
    const result = await this.request('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true,
    })
    if (result.exceptionDetails) throw new Error('MAIN_INSPECTOR_EVALUATION_FAILED')
    return result.result.value
  }
  close() {
    this.socket.close()
  }
}

/** No Playwright Electron loader: it forcibly installs basic_text/mock-keychain switches. */
export async function launchActualElectron({ args, cwd, env, onLog }) {
  const child = spawn(
    '/workspace/node_modules/electron/dist/electron',
    ['--inspect=0', '--remote-debugging-port=0', ...args],
    { cwd, env, stdio: ['ignore', 'pipe', 'pipe'] },
  )
  let diagnostic = ''
  let exited = false
  let spawnFailed = false
  child.once('error', () => {
    spawnFailed = true
  })
  let exitResult
  const closed = new Promise((resolve) =>
    child.once('close', (code, signal) => {
      exited = true
      exitResult = { code, signal }
      resolve(exitResult)
    }),
  )
  child.stdout.on('data', onLog)
  child.stderr.on('data', (bytes) => {
    onLog(bytes)
    diagnostic += bytes.toString('utf8')
    if (diagnostic.length > 1048576) diagnostic = diagnostic.slice(-1048576)
  })
  let inspector, browser
  try {
    const deadline = Date.now() + 25000
    let nodeURL, browserURL
    while (Date.now() < deadline) {
      if (spawnFailed) throw new Error('NORMAL_ELECTRON_SPAWN_FAILED')
      if (exited) throw new Error('NORMAL_ELECTRON_EXITED_BEFORE_ATTACH')
      nodeURL = diagnostic.match(/Debugger listening on (ws:\/\/127\.0\.0\.1:\d+\/[^\s]+)/)?.[1]
      browserURL = diagnostic.match(
        /DevTools listening on (ws:\/\/127\.0\.0\.1:\d+\/devtools\/browser\/[^\s]+)/,
      )?.[1]
      if (nodeURL && browserURL) break
      await delay(20)
    }
    if (!nodeURL || !browserURL) throw new Error('NORMAL_ELECTRON_DEBUG_ENDPOINT_DEADLINE')
    const socket = new WebSocket(nodeURL)
    await new Promise((resolve, reject) => {
      socket.addEventListener('open', resolve, { once: true })
      socket.addEventListener('error', () => reject(new Error('MAIN_INSPECTOR_CONNECT_FAILED')), {
        once: true,
      })
    })
    inspector = new Inspector(socket)
    browser = await chromium.connectOverCDP(browserURL)
    let page
    while (Date.now() < deadline) {
      page = browser
        .contexts()
        .flatMap((context) => context.pages())
        .find((value) => value.url().startsWith('file:///workspace/apps/desktop/out/renderer/'))
      if (page) break
      await delay(20)
    }
    if (!page) throw new Error('NORMAL_ELECTRON_PRODUCT_WINDOW_DEADLINE')
    return {
      process: () => child,
      evaluate: (fn) => inspector.evaluate(fn),
      firstWindow: async () => page,
      async close() {
        if (!exited) await inspector.evaluate(({ app }) => app.quit()).catch(() => {})
        inspector.close()
        await browser.close().catch(() => {})
        const timer = setTimeout(() => child.kill('SIGTERM'), 15000)
        const result = await closed
        clearTimeout(timer)
        if (result.code !== 0 || result.signal) throw new Error('NORMAL_ELECTRON_UNCLEAN_CLOSE')
      },
    }
  } catch (error) {
    inspector?.close()
    await browser?.close().catch(() => {})
    if (!exited) child.kill('SIGTERM')
    await closed
    throw error
  }
}
