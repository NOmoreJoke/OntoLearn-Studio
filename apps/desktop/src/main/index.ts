import { app, BrowserWindow, ipcMain, session, Menu } from 'electron'
import { isAbsolute, join, resolve } from 'node:path'
import { readFileSync } from 'node:fs'
import { z } from 'zod'
import { pathToFileURL } from 'node:url'
import { EngineSupervisor } from './engine'
import { resolveTransportLedger } from './engine-ledger'
import { TaskService } from './task-service'
import { OrdinaryProjectSource, type OrdinaryCurrent } from './ordinary-project-source'
import { QueryDefinitionService } from './query-definition-service'
import { ProjectMainlineService } from './project-mainline-service'
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
  // Release stays pinned to the original owner; stop below remains the original process owner.
  void ordinary?.dispose().catch(() => {})
  queries?.dispose()
  projects?.dispose()
  tasks?.dispose()
  supervisor?.stop()
})

let window: BrowserWindow | null = null
let supervisor: EngineSupervisor
let tasks: TaskService
let ordinary: OrdinaryProjectSource | undefined
let queries: QueryDefinitionService | undefined
let projects: ProjectMainlineService | undefined
const retiredQueries = new Set<QueryDefinitionService>()
function retireQueries(): void {
  if (!queries) return
  const old = queries
  old.dispose()
  if (old.hasOutstanding) retiredQueries.add(old)
  queries = undefined
}
let selectedOrdinary: OrdinaryCurrent = null
const retiredOrdinary = new Set<OrdinaryProjectSource>()
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

/** Attach to the actual current window after selectProject/clearProject detached its old sink. */
function attachCurrentTaskView(): void {
  const created = window
  if (!created || created.isDestroyed()) return
  tasks.attachView((update) => {
    if (window === created && !created.isDestroyed())
      created.webContents.send('tasks:update', update)
  })
}
function publishOrdinary(value: OrdinaryCurrent): void {
  const previous = selectedOrdinary
  selectedOrdinary = value
  if (!value) {
    tasks.clearProject()
    attachCurrentTaskView()
    return
  }
  // Atomic successors update the source projection, not the durable Job/view selection.
  if (
    previous &&
    previous.owner === value.owner &&
    previous.supervisor === value.supervisor &&
    previous.engineSessionId === value.engineSessionId &&
    previous.selectionSeq === value.selectionSeq
  )
    return
  tasks.selectProject(value.project.projectId)
  attachCurrentTaskView()
  void tasks.restore().then((result) => {
    const current = ordinary?.current(),
      created = window
    if (
      !result.ok ||
      !current ||
      current.owner !== value.owner ||
      current.selectionSeq !== value.selectionSeq ||
      current.supervisor !== value.supervisor ||
      current.engineSessionId !== value.engineSessionId ||
      result.data.project?.projectId !== current.project.projectId ||
      result.data.project.projectRevision !== current.project.projectRevision ||
      result.data.project.inputSnapshotId !== current.project.inputSnapshotId ||
      !created ||
      created.isDestroyed()
    )
      return
    created.webContents.send('tasks:update', {
      kind: 'restored',
      generation: result.data.generation,
      view: result.data,
    })
  })
}
function installOrdinaryMenu(source: OrdinaryProjectSource): void {
  const library: Electron.MenuItemConstructorOptions = {
    label: '项目',
    submenu: [
      { label: '创建空白项目', enabled: false },
      {
        label: '打开默认库中的项目',
        enabled: source.available,
        click: () => {
          void source
            .choices()
            .then((choices) => {
              if (ordinary !== source || quitting) return
              const entries: Electron.MenuItemConstructorOptions[] = choices.length
                ? choices.map((choice) => ({
                    label: choice.projectId,
                    click: () => {
                      void source.open(choice)
                    },
                  }))
                : [{ label: '没有可打开的项目', enabled: false }]
              const menu = Menu.buildFromTemplate(entries)
              if (window && !window.isDestroyed()) menu.popup({ window })
            })
            .catch(() => {})
        },
      },
      {
        label: '关闭活动选择',
        click: () => {
          void source.closeSelection().catch(() => {})
        },
      },
    ],
  }
  const template: Electron.MenuItemConstructorOptions[] = [
    ...(process.platform === 'darwin' ? [{ role: 'appMenu' as const }] : []),
    library,
    { role: 'editMenu' },
    { role: 'viewMenu' },
    { role: 'windowMenu' },
  ]
  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
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
  const profile =
    !fixture || (!app.isPackaged && process.argv.includes('--t01-internal-business3'))
      ? 'business3'
      : 'legacy2'
  // The host owns these exact adopted layouts. No existence search or fallback.
  const exampleRoot =
    profile === 'business3' && !fixture
      ? app.isPackaged
        ? join(process.resourcesPath, 'examples', 'equipment-maintenance', 'loader')
        : resolve(
            app.getAppPath(),
            '../../build/release-resources/fr003-bundle-v2/examples/equipment-maintenance/loader',
          )
      : undefined
  supervisor = new EngineSupervisor(
    { packaged: app.isPackaged, appPath: app.getAppPath(), resourcesPath: process.resourcesPath },
    {
      profile,
      exampleRoot,
      dataPath: fixture?.databasePath ?? join(app.getPath('userData'), 'engine.sqlite'),
      // Main-side gate: boolean flag, a valid launch id, the Windows platform
      // and the actual unique isolated E2E profile argv must all agree with the
      // live userData path; the supervisor independently rejects packaged.
      ...(resolveTransportLedger({
        flag: process.env.ONTOLEARN_E2E_TRANSPORT_LEDGER,
        launchId: process.env.ONTOLEARN_E2E_TRANSPORT_LEDGER_LAUNCH_ID,
        userDataPath: app.getPath('userData'),
        packaged: app.isPackaged,
        platform: process.platform,
        userDataArg: process.argv
          .find((argument) => argument.startsWith('--user-data-dir='))
          ?.slice('--user-data-dir='.length),
      }) ?? {}),
      ...(fixture ? { allowedProjects: [fixture.projectId], testMode: true } : {}),
    },
  )
  tasks = new TaskService(supervisor)
  if (!fixture && supervisor.profile === 'business3')
    projects = new ProjectMainlineService(supervisor, tasks, attachCurrentTaskView)
  if (!fixture && supervisor.profile === 'legacy2') {
    const refreshOrdinary = () => {
      let transport: ReturnType<EngineSupervisor['ordinaryLibraryClient']>
      try {
        transport = supervisor.ordinaryLibraryClient()
      } catch {
        // The shared active+retired owner book is full. Fence old view, retain
        // every old responsibility, and refuse issuance without a new grant.
        if (ordinary) {
          const previous = ordinary
          if (previous.available) retiredOrdinary.add(previous)
          void previous.dispose().catch(() => {})
          retireQueries()
          ordinary = undefined
        }
        return
      }
      if (ordinary?.hasTransport(transport)) return
      if (ordinary) {
        const previous = ordinary
        if (previous.available) retiredOrdinary.add(previous)
        // dispose fences synchronously before new publication. It never clears
        // an unresolved action or returns its shared book credit.
        void previous.dispose().catch(() => {})
        retireQueries()
        ordinary = undefined
      }
      const source = new OrdinaryProjectSource(transport)
      ordinary = source
      queries = new QueryDefinitionService(source, tasks)
      source.observe((value) => {
        if (ordinary === source) publishOrdinary(value)
      })
      installOrdinaryMenu(source)
    }
    // Subscribe before initial factory/current read. A same-project new Session
    // receives a fresh source owner; old client records never bind that Session.
    supervisor.onConnectionState((state) => {
      if (state.state === 'ready') refreshOrdinary()
    })
    refreshOrdinary()
    tasks.observeActiveProject((project, session) => {
      if (project && session) ordinary?.observeProject(project, supervisor, session)
    })
  }
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
  registerDesktopIpc({
    ipcMain,
    trusted,
    tasks,
    supervisor,
    projects,
    replies: projects ? supervisor.mainlineReplyReceiver() : undefined,
  })
  createWindow()
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
