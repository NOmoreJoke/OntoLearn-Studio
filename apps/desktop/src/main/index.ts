import { app, BrowserWindow, ipcMain, session, Menu, dialog } from 'electron'
import { createHash } from 'node:crypto'
import { isAbsolute, join, resolve } from 'node:path'
import { readFileSync } from 'node:fs'
import { z } from 'zod'
import { pathToFileURL } from 'node:url'
import { EngineSupervisor } from './engine'
import {
  LibraryLocationConfig,
  LibraryLocationService,
  verifyLibraryLocator,
} from './library-location-service'
import { resolveTransportLedger } from './engine-ledger'
import { TaskService } from './task-service'
import { PrivateCiphertextRepository } from './model-gateway/ciphertext-repository'
import { ConfigurationRepository } from './model-gateway/configuration-repository'
import { PersistentGatewayAudit } from './model-gateway/persistent-audit'
import { createElectronCredentialBoundary } from './model-gateway/electron-safe-storage'
import { ModelGatewayService } from './model-gateway/model-service'
import { finiteFixturePolicy } from './model-gateway/finite-fixture-policy'
import { OrdinaryProjectSource, type OrdinaryCurrent } from './ordinary-project-source'
import { QueryDefinitionService } from './query-definition-service'
import { ProjectMainlineService } from './project-mainline-service'
import { isTrustedDocument } from './trusted-document'
import { contentSecurityPolicy } from '../csp'
import { hardenWebContents, securePreferences } from './window-security'
import { installWindowRecovery } from './window-recovery'
import { installViewNavigation } from './view-navigation'
import { registerDesktopIpc } from './desktop-ipc'
import { convergeStartupLibraryFailure } from './startup-library-failure'
import { validateV2 } from '../../../../packages/contracts/src/v2'

declare const __DEV_CSP_NONCE__: string

app.enableSandbox()

let quitting = false
let quitBarrier = false
const singleInstance = app.requestSingleInstanceLock()
if (!singleInstance) app.quit()
app.on('before-quit', (event) => {
  if (quitBarrier) return
  if (!supervisor) {
    // A quit signal before the supervisor exists must still fence the async
    // whenReady continuation away from creating a supervisor or a window.
    quitting = true
    return
  }
  event.preventDefault()
  if (quitting) return
  quitting = true
  void (async () => {
    const modelShutdown = finishModelShutdown().catch(() => {})
    await ordinary?.dispose().catch(() => {})
    // A service cleanup failure cannot skip the actual process-close barrier.
    for (const service of [queries, projects, tasks]) {
      try {
        service?.dispose()
      } catch {
        /* Existing durable intents remain unchanged. */
      }
    }
    try {
      await Promise.all([supervisor.stopAndWait(), modelShutdown])
      quitBarrier = true
      app.quit()
    } catch {
      quitting = false
      dialog.showErrorBox(
        '引擎尚未关闭',
        '未能确认全部引擎进程已退出。项目库选择保持不变，请稍后重试退出。',
      )
    }
  })()
})

let window: BrowserWindow | null = null
let supervisor: EngineSupervisor
let tasks: TaskService
let ordinary: OrdinaryProjectSource | undefined
let queries: QueryDefinitionService | undefined
let projects: ProjectMainlineService | undefined
let library: LibraryLocationService | undefined
let models: ModelGatewayService | undefined
let modelInitialization: Promise<void> | undefined
let modelCiphertexts: PrivateCiphertextRepository | undefined
let modelConfigurations: ConfigurationRepository | undefined
let modelAudit: PersistentGatewayAudit | undefined
async function closeModels(): Promise<void> {
  const owner = models
  models = undefined
  await owner?.close().catch(() => {})
  await Promise.allSettled([
    modelConfigurations?.close(),
    modelAudit?.close(),
    modelCiphertexts?.close(),
  ])
  modelConfigurations = undefined
  modelAudit = undefined
  modelCiphertexts = undefined
}
async function initializeModels(
  databasePath: string,
  testRuntime: boolean,
  finiteFields: boolean,
): Promise<void> {
  try {
    const location = {
      userDataPath: app.getPath('userData'),
      // These are the actual current Store files; no exporter/project-folder capability
      // exists in this approved baseline. Do not invent an export exclusion proof.
      excludedRoots: [databasePath, databasePath + '-wal', databasePath + '-shm'],
    }
    modelCiphertexts = await PrivateCiphertextRepository.open(location)
    modelConfigurations = await ConfigurationRepository.open(location)
    modelAudit = await PersistentGatewayAudit.open(location)
    if (finiteFields && (!testRuntime || app.isPackaged)) throw new Error('INVALID_TEST_FIXTURE')
    const fieldModels = finiteFields
      ? [
          finiteFixturePolicy(
            createHash('sha256')
              .update(readFileSync(join(app.getAppPath(), '../../uv.lock')))
              .digest('hex'),
          ),
        ]
      : []
    const owner = await ModelGatewayService.open({
      engine: supervisor,
      repository: modelConfigurations,
      credentials: createElectronCredentialBoundary(modelCiphertexts),
      audit: modelAudit,
      producerPolicy: testRuntime ? 'synthetic-test-runtime' : 'runtime-only',
      fieldModels,
    })
    models = owner
    if (quitting) await closeModels()
    else if (!library?.switching) owner.selectProject(tasks.projectContext())
  } catch {
    // Model/storage/backend failure is isolated from deterministic local tasks and windows.
    await closeModels()
  }
}
async function finishModelShutdown(): Promise<void> {
  let timer: ReturnType<typeof setTimeout> | undefined
  try {
    await Promise.race([
      (async () => {
        await modelInitialization
        await closeModels()
      })(),
      new Promise<void>((resolve) => {
        timer = setTimeout(resolve, 5000)
      }),
    ])
  } finally {
    clearTimeout(timer)
  }
}
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
  if (!singleInstance) return
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
  // Yield one macrotask turn so PreMainMessageLoopRun returns and Chromium's main
  // message loop is pumping before any library config or engine process spawn.
  await new Promise<void>((resolve) => setTimeout(resolve, 0))
  if (quitting || quitBarrier) return
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
            modelFieldPolicy: z.literal('i06-finite-probe-v1').optional(),
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
  let locationConfig: LibraryLocationConfig | undefined
  let startupLocation: ReturnType<LibraryLocationConfig['prepareStartupFile']> | undefined
  if (!fixture && profile === 'business3') {
    try {
      locationConfig = new LibraryLocationConfig(
        join(app.getPath('userData'), 'library-location.json'),
        join(app.getPath('userData'), 'engine.sqlite'),
      )
      if (locationConfig.needsRecovery) {
        const answer = await dialog.showMessageBox({
          type: 'warning',
          title: '项目库切换尚未完成',
          message: '上次未能确认旧引擎已经关闭。',
          detail:
            '选择继续使用原项目库会重新核验原库及写入锁；不会打开目标库，也不会丢弃或重放原操作。',
          buttons: ['退出', '继续使用原项目库'],
          defaultId: 0,
          cancelId: 0,
        })
        if (answer.response !== 1) {
          app.quit()
          return
        }
        locationConfig.restoreOriginal()
      }
      startupLocation = locationConfig.prepareStartupFile()
      verifyLibraryLocator(startupLocation)
    } catch {
      dialog.showErrorBox(
        '无法打开项目库位置',
        '项目库位置记录或文件身份校验失败。未改用默认库，请检查原文件和位置后重试。',
      )
      app.quit()
      return
    }
  }
  const databasePath =
    fixture?.databasePath ?? startupLocation?.path ?? join(app.getPath('userData'), 'engine.sqlite')
  supervisor = new EngineSupervisor(
    { packaged: app.isPackaged, appPath: app.getAppPath(), resourcesPath: process.resourcesPath },
    {
      // Desktop cold start (Windows Defender scanning .venv imports of rdflib/
      // pyshacl) needs a far larger budget than the supervisor class defaults.
      startupMs: 30000,
      handshakeMs: 30000,
      requestMs: 15000,
      profile,
      exampleRoot,
      dataPath: databasePath,
      ...(startupLocation?.file
        ? {
            libraryFileIdentity: startupLocation.file,
            libraryRequireExisting: !startupLocation.initialize,
          }
        : {}),
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
  if (locationConfig) {
    try {
      const status = await supervisor.libraryStatus()
      if (
        locationConfig.libraryId &&
        !locationConfig.pending &&
        status.libraryEvidenceRef !== locationConfig.libraryId
      )
        throw new Error('LIBRARY_IDENTITY_CHANGED')
      locationConfig.completeStartup(status.libraryEvidenceRef)
    } catch {
      // A before-quit that fires while whenReady() still awaits this startup
      // verification makes libraryStatus() fail spuriously. The convergence
      // helper returns without any blocking dialog in that case, so the
      // before-quit stopAndWait() → app.quit() sequence completes instead of
      // deadlocking the main thread on a synchronous error box.
      const config = locationConfig
      await convergeStartupLibraryFailure({
        quitConverging: () => quitting || quitBarrier,
        stopAndWait: () => supervisor.stopAndWait(),
        engineExitUnconfirmed: () =>
          dialog.showErrorBox('项目库启动未完成', '引擎退出尚未得到确认。不会打开其它项目库。'),
        reportFailure: async () => {
          if (config.pending) {
            const answer = await dialog.showMessageBox({
              type: 'error',
              title: '目标项目库无法打开',
              message: '目标库格式、身份或写入锁校验失败，未覆盖目标文件。',
              detail: '可以明确恢复原库选择后重启，或退出并检查目标文件。',
              buttons: ['退出', '恢复原库并重启'],
              defaultId: 0,
              cancelId: 0,
            })
            if (answer.response === 1) {
              try {
                config.restoreOriginal()
                app.relaunch()
              } catch {
                dialog.showErrorBox('原库恢复失败', '原库文件身份已变化。位置记录保持待恢复状态。')
              }
            }
          } else
            dialog.showErrorBox(
              '项目库无法打开',
              '项目库格式、身份或写入锁校验失败。未创建替代库，请检查原文件后重试。',
            )
          quitBarrier = true
          app.quit()
        },
      })
      return
    }
  }
  tasks = new TaskService(supervisor, (projectId) => models?.selectProject(projectId))
  if (!fixture && supervisor.profile === 'business3')
    projects = new ProjectMainlineService(supervisor, tasks, attachCurrentTaskView, {
      managementJournalPath: join(
        app.getPath('userData'),
        'project-intents',
        createHash('sha256').update(startupLocation!.path).digest('hex') + '.json',
      ),
      restoreJournalPath: join(
        app.getPath('userData'),
        'project-restore-intents',
        createHash('sha256').update(startupLocation!.path).digest('hex') + '.json',
      ),
    })
  if (locationConfig) {
    library = new LibraryLocationService(locationConfig, {
      pick: async (intent) => {
        const options: Electron.OpenDialogOptions =
          intent === 'create'
            ? { title: '选择空目录创建项目库', properties: ['openDirectory', 'createDirectory'] }
            : {
                title: '打开已有项目库',
                properties: ['openFile'],
                filters: [{ name: 'SQLite 项目库', extensions: ['sqlite', 'db'] }],
              }
        const result = window
          ? await dialog.showOpenDialog(window, options)
          : await dialog.showOpenDialog(options)
        return result.canceled || result.filePaths.length !== 1 ? null : result.filePaths[0]!
      },
      hasUnresolvedResponsibility: () =>
        !!projects?.hasUnresolvedResponsibility ||
        supervisor.hasUnresolvedResponsibility ||
        [...retiredQueries].some((query) => query.hasOutstanding) ||
        retiredOrdinary.size > 0,
      status: () => supervisor.libraryStatus(),
      freezeAdmission: () => {
        supervisor.freezeAdmission()
        models?.selectProject(null)
      },
      unfreezeAdmission: () => {
        supervisor.unfreezeAdmission()
        models?.selectProject(tasks.projectContext())
      },
      stopAndWait: () => supervisor.stopAndWait(),
      relaunch: () => {
        app.relaunch()
        app.quit()
      },
    })
  }
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
  // A quit that began during the startup awaits above must not build a late
  // first window while the before-quit shutdown is already converging.
  if (quitting || quitBarrier) return
  registerDesktopIpc({
    ipcMain,
    trusted,
    tasks,
    supervisor,
    projects,
    replies: projects ? supervisor.mainlineReplyReceiver() : undefined,
    library,
    getModels: () => (quitting || quitBarrier ? undefined : models),
  })
  createWindow()
  // Local startup and recovery do not wait for platform secure storage.
  modelInitialization = initializeModels(
    databasePath,
    !!fixture,
    fixture?.modelFieldPolicy === 'i06-finite-probe-v1',
  )
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
