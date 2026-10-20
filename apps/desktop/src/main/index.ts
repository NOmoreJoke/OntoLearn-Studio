import { app, BrowserWindow, ipcMain, session } from 'electron'
import { isAbsolute, join } from 'node:path'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { z } from 'zod'
import { pathToFileURL } from 'node:url'
import { EngineSupervisor } from './engine'
import { TaskService } from './task-service'
import { PrivateCiphertextRepository } from './model-gateway/ciphertext-repository'
import { ConfigurationRepository } from './model-gateway/configuration-repository'
import { PersistentGatewayAudit } from './model-gateway/persistent-audit'
import { createElectronCredentialBoundary } from './model-gateway/electron-safe-storage'
import { ModelGatewayService, unavailableModelStatus } from './model-gateway/model-service'
import { finiteFixturePolicy } from './model-gateway/finite-fixture-policy'
import { isTrustedDocument } from './trusted-document'
import { contentSecurityPolicy } from '../csp'
import { hardenWebContents, securePreferences } from './window-security'
import { installWindowRecovery } from './window-recovery'
import { installViewNavigation } from './view-navigation'
import {
  safeError,
  modelGatewayError,
  modelInvalidRequestError,
  type HealthResult,
  type ModelMethod,
} from '@ontolearn/contracts'
import { validateV2, validateModelParams } from '../../../../packages/contracts/src/v2'

declare const __DEV_CSP_NONCE__: string

app.enableSandbox()
// The profile owns one main gateway/configuration authority. A second process must
// not keep using old in-memory grants after another owner changes this profile.
const ownsProfile = app.requestSingleInstanceLock()
if (!ownsProfile) app.quit()

let quitting = false
app.on('before-quit', (event) => {
  if (quitting) return
  event.preventDefault()
  quitting = true
  // Closing the gateway first cancels network/material waits. Bound app shutdown;
  // synchronous OS credential prompts cannot be revoked by a JavaScript timer.
  void (async () => {
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
      tasks?.dispose()
      supervisor?.stop()
      app.quit()
    }
  })().catch(() => {
    tasks?.dispose()
    supervisor?.stop()
    app.quit()
  })
})

let window: BrowserWindow | null = null
let supervisor: EngineSupervisor
let tasks: TaskService
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
    else owner.selectProject(tasks.projectContext())
  } catch {
    // Model/storage/backend failure is isolated from deterministic local tasks and windows.
    await closeModels()
  }
}
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
  if (!ownsProfile) return
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
  const databasePath = fixture?.databasePath ?? join(app.getPath('userData'), 'engine.sqlite')
  supervisor = new EngineSupervisor(
    { packaged: app.isPackaged, appPath: app.getAppPath(), resourcesPath: process.resourcesPath },
    {
      dataPath: databasePath,
      ...(fixture ? { allowedProjects: [fixture.projectId], testMode: true } : {}),
    },
  )
  tasks = new TaskService(supervisor, (projectId) => models?.selectProject(projectId))
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
  const permission = () => ({
    ok: false as const,
    error: safeError({
      code: 'PERMISSION_DENIED',
      messageKey: 'permission.denied',
      params: {},
      retryable: false,
    }),
  })
  ipcMain.handle('engine:health', async (event): Promise<HealthResult> => {
    if (!trusted(event)) return permission()
    try {
      return { ok: true, data: await supervisor.health() }
    } catch (error) {
      return { ok: false, error: safeError((error as { error?: unknown } | null)?.error) }
    }
  })
  // This routing table is main-only and finite. No generic method crosses preload.
  const routes: Record<string, (argument: never) => Promise<unknown>> = {
    'tasks:restore': () => tasks.restore(),
    'project:active': () => tasks.activeProject(),
    'job:get': (id) => tasks.getJob(id),
    'job:list': (options) => tasks.listJobs(options),
    'job:cancel': (id) => tasks.cancelJob(id),
    'job:subscribe': (id) => tasks.subscribeJob(id),
    'job:unsubscribe': (request) => tasks.unsubscribeView(request),
    'result:get': (id) => tasks.getResult(id),
    'result:page': (options) => tasks.getResultPage(options),
    'operation:get': (id) => tasks.getOperation(id),
  }
  for (const [channel, handler] of Object.entries(routes)) {
    ipcMain.handle(channel, (event, argument) =>
      trusted(event) ? handler(argument as never) : permission(),
    )
  }
  const modelRoutes: Record<string, ModelMethod> = {
    'model:status': 'getModelAccessStatus',
    'model:configure': 'configureModel',
    'model:credential': 'storeModelCredential',
    'model:privacy': 'setModelPrivacy',
    'model:select-results': 'selectModelResults',
    'model:field-catalog': 'getModelFieldCatalog',
    'model:select-fields': 'selectModelFields',
    'model:preview': 'previewModelExplanation',
    'model:confirm': 'confirmModelAuthorization',
    'model:start': 'startModelExplanation',
    'model:outcome': 'getModelExplanationOutcome',
    'model:cancel': 'cancelModelExplanation',
  }
  for (const [channel, method] of Object.entries(modelRoutes))
    ipcMain.handle(channel, (event, argument) => {
      if (!trusted(event)) return permission()
      if (!validateModelParams(method, argument))
        return { ok: false, error: modelInvalidRequestError() }
      if (models) return models.handle(method, argument)
      return method === 'getModelAccessStatus'
        ? { ok: true, data: unavailableModelStatus() }
        : { ok: false, error: modelGatewayError('MODEL_UNAVAILABLE') }
    })
  createWindow()
  // Never gate the local window/Store on private gateway startup or credential availability.
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
