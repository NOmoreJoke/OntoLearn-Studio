import { app, BrowserWindow, ipcMain, session } from 'electron'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { readEngineHealth } from './engine'
import { isTrustedDocument } from './trusted-document'
import { contentSecurityPolicy } from '../csp'
import { hardenWebContents, securePreferences } from './window-security'
import { installWindowRecovery } from './window-recovery'
import type { HealthResult } from '@ontolearn/contracts'

declare const __DEV_CSP_NONCE__: string

app.enableSandbox()

let quitting = false
app.on('before-quit', () => {
  quitting = true
})

let window: BrowserWindow | null = null
let pendingHealth: Promise<HealthResult> | undefined
const devURL = !app.isPackaged ? process.env.ELECTRON_RENDERER_URL : undefined
const rendererPath = join(__dirname, '../renderer/index.html')
const trustedURL = devURL ?? pathToFileURL(rendererPath).href

function createWindow(): void {
  window = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 1024,
    minHeight: 720,
    title: 'OntoLearn Studio',
    backgroundColor: '#F5F9F7',
    webPreferences: securePreferences(join(__dirname, '../preload/index.js')),
  })
  const created = window
  installWindowRecovery(
    created,
    () => {
      // Create before destroy to avoid window-all-closed quitting on Windows/Linux.
      createWindow()
      created.destroy()
    },
    () => quitting,
  )
  window.on('closed', () => {
    if (window === created) window = null
  })
  if (devURL) void window.loadURL(devURL)
  else void window.loadFile(rendererPath)
}

app.on('web-contents-created', (_event, contents) => hardenWebContents(contents))

void app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_webContents, _permission, callback) =>
    callback(false),
  )
  session.defaultSession.setPermissionCheckHandler(() => false)
  if (devURL) {
    const policy = contentSecurityPolicy({ nonce: __DEV_CSP_NONCE__, origin: devURL })
    session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
      callback({
        responseHeaders: { ...details.responseHeaders, 'Content-Security-Policy': [policy] },
      })
    })
  }
  ipcMain.handle('engine:health', (event): Promise<HealthResult> => {
    if (
      !window ||
      event.sender !== window.webContents ||
      event.senderFrame !== window.webContents.mainFrame ||
      !isTrustedDocument(event.senderFrame.url, trustedURL)
    ) {
      return Promise.resolve({ ok: false, error: '请求来源不受信任。' })
    }
    // 并发复用健康探针，避免渲染端反复点击创建无界子进程。
    pendingHealth ??= readEngineHealth({
      packaged: app.isPackaged,
      appPath: app.getAppPath(),
      resourcesPath: process.resourcesPath,
    })
      .then((data): HealthResult => ({ ok: true, data }))
      .catch((): HealthResult => ({
        ok: false,
        error: '本地引擎未就绪。开发环境请先执行 uv sync --frozen，再重试。',
      }))
      .finally(() => {
        pendingHealth = undefined
      })
    return pendingHealth
  })
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
