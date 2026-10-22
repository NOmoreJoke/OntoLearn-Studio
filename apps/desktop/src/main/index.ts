import { app, BrowserWindow, ipcMain, session } from 'electron'
import { isAbsolute, join } from 'node:path'
import { readFileSync } from 'node:fs'
import { z } from 'zod'
import { pathToFileURL } from 'node:url'
import { EngineSupervisor } from './engine'
import { TaskService } from './task-service'
import { isTrustedDocument } from './trusted-document'
import { contentSecurityPolicy } from '../csp'
import { hardenWebContents, securePreferences } from './window-security'
import { installWindowRecovery } from './window-recovery'
import { installViewNavigation } from './view-navigation'
import { registerDesktopIpc } from './desktop-ipc'
import { validateV2 } from '../../../../packages/contracts/src/v2'

declare const __DEV_CSP_NONCE__: string

app.enableSandbox()

let quitting = false
app.on('before-quit', () => {
  quitting = true
  tasks?.dispose()
  supervisor?.stop()
})

let window: BrowserWindow | null = null
let supervisor: EngineSupervisor
let tasks: TaskService
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
  const attach = () =>
    tasks.attachView((update) => {
      if (!created.isDestroyed() && window === created)
        created.webContents.send('tasks:update', update)
    })
  attach()
  installViewNavigation(created.webContents, () => {
    if (window === created) attach()
  })
  created.webContents.on('render-process-gone', () => {
    if (window === created) tasks.detachView()
  })
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
    if (window === created) {
      tasks.detachView()
      window = null
    }
  })
  if (devURL) void window.loadURL(devURL)
  else void window.loadFile(rendererPath)
}

app.on('web-contents-created', (_event, contents) => hardenWebContents(contents))

void app.whenReady().then(async () => {
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
  // Test fixtures are accepted only through a main-process launch argument. They are
  // never supplied by renderer IPC, and do not enable task creation in the product.
  const fixtureArg = process.argv.find((arg) => arg.startsWith('--i04-test-fixture='))
  const fixturePath = fixtureArg?.slice('--i04-test-fixture='.length)
  const fixture =
    fixturePath && isAbsolute(fixturePath) && process.env.I04_TEST_FIXTURE === fixturePath
      ? z
          .object({
            projectId: z.string().uuid(),
            jobIds: z.array(z.string().uuid()).max(16),
            databasePath: z.string().refine(isAbsolute),
            startRequests: z
              .array(
                z
                  .record(z.string(), z.unknown())
                  .refine(
                    (value) =>
                      validateV2('params_job.create', value) &&
                      ['test.read', 'test.atomic', 'test.rounds'].includes(
                        String(value.capability),
                      ),
                  ),
              )
              .max(2)
              .optional(),
          })
          .strict()
          .parse(JSON.parse(readFileSync(fixturePath, 'utf8')))
      : undefined
  supervisor = new EngineSupervisor(
    { packaged: app.isPackaged, appPath: app.getAppPath(), resourcesPath: process.resourcesPath },
    {
      profile:
        !app.isPackaged && process.argv.includes('--t01-internal-business3')
          ? 'business3'
          : 'legacy2',
      dataPath: fixture?.databasePath ?? join(app.getPath('userData'), 'engine.sqlite'),
      ...(fixture ? { allowedProjects: [fixture.projectId], testMode: true } : {}),
    },
  )
  tasks = new TaskService(supervisor)
  if (fixture) {
    const jobIds = [...fixture.jobIds]
    for (const request of fixture.startRequests ?? []) {
      if (request.projectId !== fixture.projectId) throw new Error('INVALID_TEST_FIXTURE')
      const job = (await supervisor.request('job.create', request)) as { jobId: string }
      jobIds.push(job.jobId)
    }
    tasks.selectProject(fixture.projectId, jobIds)
  }
  function trusted(event: Electron.IpcMainInvokeEvent): boolean {
    return (
      !!window &&
      event.sender === window.webContents &&
      event.senderFrame === window.webContents.mainFrame &&
      isTrustedDocument(event.senderFrame.url, trustedURL)
    )
  }
  registerDesktopIpc({ ipcMain, trusted, tasks, supervisor })
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
