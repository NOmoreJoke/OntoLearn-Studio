import { app, BrowserWindow, ipcMain, session } from 'electron'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { readEngineHealth } from './engine'
import { isTrustedDocument } from './trusted-document'
import type { HealthResult } from '@ontolearn/contracts'

declare const __DEV_CSP_NONCE__: string

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
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webviewTag: false,
    },
  })
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }))
  window.webContents.on('will-navigate', (event) => event.preventDefault())
  window.on('closed', () => {
    window = null
  })
  if (devURL) void window.loadURL(devURL)
  else void window.loadFile(rendererPath)
}

void app.whenReady().then(() => {
  session.defaultSession.setPermissionRequestHandler((_webContents, _permission, callback) =>
    callback(false),
  )
  session.defaultSession.setPermissionCheckHandler(() => false)
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          `default-src 'self'; script-src 'self' ${devURL ? `'nonce-${__DEV_CSP_NONCE__}'` : ''}; style-src 'self' ${devURL ? "'unsafe-inline'" : ''}; img-src 'self' data:; connect-src 'self' ${devURL ? 'ws://127.0.0.1:5173' : ''}; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'`,
        ],
      },
    })
  })
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
