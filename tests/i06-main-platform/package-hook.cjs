/* eslint-disable @typescript-eslint/no-require-imports */
// Observer only: no replacement of native dialogs or product recovery functions.
const { app, BrowserWindow, safeStorage } = require('electron')
const fs = require('node:fs')
const inspector = require('node:inspector')
const assert = require('node:assert/strict')
const output = process.env.I06_NATIVE_EVIDENCE
const prepared = JSON.parse(fs.readFileSync(process.env.I06_NATIVE_FIXTURE_EVIDENCE, 'utf8'))
const evidence = {
  result: 'running',
  windows: [],
  events: [],
  recoveryCalls: [],
  rendererCDPEverAttached: false,
}
const save = () => fs.writeFileSync(output, JSON.stringify(evidence, null, 2) + '\n')
const fail = (error) => {
  evidence.result = 'failed'
  evidence.error = String(error)
  save()
  app.exit(1)
}
const deadline = setTimeout(() => fail('NATIVE_INCREMENTAL_DEADLINE'), 70000)
let ordinal = 0,
  invocationId
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
async function call(window, method, params = {}) {
  if (ordinal === 2) evidence.recoveryCalls.push(method)
  const reply = await window.webContents.executeJavaScript(
    `window.ontolearn[${JSON.stringify(method)}](${JSON.stringify(params)})`,
  )
  if (!reply.ok) throw new Error('NATIVE_BRIDGE_REJECTED_' + method + '_' + reply.error.code)
  assert.equal(JSON.stringify(reply).includes(process.env.I06_NATIVE_SECRET), false)
  return reply.data
}
async function until(work, code) {
  const end = Date.now() + 15000
  while (Date.now() < end) {
    const value = await work()
    if (value) return value
    await delay(50)
  }
  throw new Error(code)
}
function runtime(window) {
  const proc = (pid) =>
    Object.fromEntries(
      fs
        .readFileSync(`/proc/${pid}/status`, 'utf8')
        .split('\n')
        .map((line) => line.split(/:\s*/))
        .filter(([key]) =>
          ['Uid', 'NSpid', 'NoNewPrivs', 'Seccomp', 'Seccomp_filters', 'CapEff'].includes(key),
        ),
    )
  const value = {
    mainPid: process.pid,
    packaged: app.isPackaged,
    executable: process.execPath,
    resourcesPath: process.resourcesPath,
    appPath: app.getAppPath(),
    versions: process.versions,
    type: process.type,
    ready: app.isReady(),
    uid: process.getuid(),
    argv: process.argv,
    encryptionAvailable: safeStorage.isEncryptionAvailable(),
    backend: safeStorage.getSelectedStorageBackend(),
    noSandboxSwitch: app.commandLine.hasSwitch('no-sandbox'),
    disabledHangMonitorSwitch: app.commandLine.hasSwitch('disable-hang-monitor'),
    remoteDebuggingSwitch: app.commandLine.hasSwitch('remote-debugging-port'),
    inspectorURL: inspector.url() ?? null,
    preferences: {
      sandbox: window.webContents.getLastWebPreferences().sandbox,
      contextIsolation: window.webContents.getLastWebPreferences().contextIsolation,
      nodeIntegration: window.webContents.getLastWebPreferences().nodeIntegration,
    },
    mainProc: proc(process.pid),
    rendererProc: proc(window.webContents.getOSProcessId()),
  }
  assert.equal(value.packaged, true)
  assert.equal(value.executable, '/workspace/release/linux-arm64-unpacked/@ontolearndesktop')
  assert.equal(value.resourcesPath, '/workspace/release/linux-arm64-unpacked/resources')
  assert.equal(value.noSandboxSwitch, false)
  assert.equal(value.disabledHangMonitorSwitch, false)
  assert.equal(value.remoteDebuggingSwitch, false)
  assert.equal(value.inspectorURL, null)
  assert.equal(value.backend, 'gnome_libsecret')
  assert.equal(value.encryptionAvailable, true)
  assert.equal(value.uid, 1106)
  assert.equal(value.rendererProc.NoNewPrivs, '1')
  assert.equal(value.rendererProc.Seccomp, '2')
  assert.ok(Number(value.rendererProc.Seccomp_filters) > Number(value.mainProc.Seccomp_filters))
  return value
}
async function snapshot(window) {
  const status = await call(window, 'getModelAccessStatus')
  const outcome = await call(window, 'getModelExplanationOutcome', {
    contextId: status.contextId,
    invocationId,
  })
  const view = await call(window, 'restoreTasks')
  const marker = await call(window, 'getOperation', prepared.atomic.operationId)
  assert.ok(marker)
  assert.equal(outcome.state, 'completed')
  return { status, outcome, view, marker, runtime: runtime(window) }
}
function observe(window, newlyCreated = false) {
  const index = ++ordinal
  const entry = { index, windowId: window.id }
  evidence.windows.push(entry)
  window.webContents.on('render-process-gone', (_event, details) => {
    evidence.events.push(details.reason)
    save()
  })
  const drive = async () => {
    try {
      if (index === 1) {
        await until(
          async () =>
            (
              await call(window, 'restoreTasks').catch((error) => {
                if (!String(error).endsWith('restoreTasks_PERMISSION_DENIED')) throw error
                evidence.initialReadFenceRetries = (evidence.initialReadFenceRetries ?? 0) + 1
                save()
                return { jobs: [] }
              })
            ).jobs.find(
              (job) => job.operationId === prepared.atomic.operationId && job.state === 'succeeded',
            ),
          'NATIVE_ATOMIC_BASELINE',
        )
        if (process.env.I06_PACKAGE_FINITE_DENIAL === '1') {
          const status = await call(window, 'getModelAccessStatus')
          assert.equal(status.availability, 'unavailable')
          assert.equal(status.contextId, null)
          evidence.rejections = []
          const fake = '00000000-0000-4000-8000-000000000001'
          for (const [method, params] of [
            [
              'configureModel',
              {
                contextId: fake,
                configurationId: null,
                configurationVersion: null,
                displayName: 'Denied synthetic',
                endpoint: process.env.I06_NATIVE_ENDPOINT,
                model: 'synthetic-native',
              },
            ],
            [
              'storeModelCredential',
              {
                contextId: fake,
                configurationId: fake,
                configurationVersion: fake,
                secret: process.env.I06_NATIVE_SECRET,
              },
            ],
            [
              'startModelExplanation',
              { contextId: fake, configurationId: fake, grantId: fake, selectionIds: [fake] },
            ],
          ]) {
            const reply = await window.webContents.executeJavaScript(
              `window.ontolearn[${JSON.stringify(method)}](${JSON.stringify(params)})`,
            )
            assert.equal(reply.ok, false)
            assert.equal(reply.error.code, 'GATEWAY_MODEL_UNAVAILABLE')
            assert.equal(JSON.stringify(reply).includes(process.env.I06_NATIVE_SECRET), false)
            evidence.rejections.push({ method, reply })
          }
          evidence.result = 'passed'
          evidence.finitePolicyDenied = true
          evidence.status = status
          evidence.runtime = runtime(window)
          save()
          clearTimeout(deadline)
          app.quit()
          return
        }
        evidence.engineProcesses = []
        evidence.excludedEngineProcesses = []
        const parentOf = (pid) =>
          Number(fs.readFileSync(`/proc/${pid}/status`, 'utf8').match(/^PPid:\s*(\d+)/m)[1])
        for (const pidText of fs.readdirSync('/proc').filter((name) => /^\d+$/.test(name))) {
          const pid = Number(pidText)
          try {
            const executable = fs.readlinkSync(`/proc/${pid}/exe`)
            if (!executable.startsWith('/workspace/release/linux-arm64-unpacked/resources/engine/'))
              continue
            const ancestors = []
            let cursor = pid
            for (let count = 0; cursor > 0 && count < 32; count++) {
              const ppid = parentOf(cursor)
              ancestors.push({ pid: cursor, ppid })
              if (cursor === process.pid) break
              cursor = ppid
            }
            const record = {
              pid,
              executable,
              argv: fs.readFileSync(`/proc/${pid}/cmdline`).toString().split('\0').filter(Boolean),
              ancestors,
              currentMainPid: process.pid,
            }
            if (ancestors.some((item) => item.pid === process.pid))
              evidence.engineProcesses.push(record)
            else evidence.excludedEngineProcesses.push(record)
          } catch {
            /* Child may exit between observations. */
          }
        }
        assert.ok(evidence.engineProcesses.length > 0, 'ACTUAL_PACKAGED_ENGINE_PROCESS_REQUIRED')
        const status = await until(async () => {
          const value = await call(window, 'getModelAccessStatus')
          return value.availability === 'ready' ? value : false
        }, 'NATIVE_MODEL_READY')
        const configuration = await call(window, 'configureModel', {
          contextId: status.contextId,
          configurationId: null,
          configurationVersion: null,
          displayName: 'Native synthetic receiver',
          endpoint: process.env.I06_NATIVE_ENDPOINT,
          model: 'synthetic-native',
        })
        await call(window, 'storeModelCredential', {
          contextId: status.contextId,
          configurationId: configuration.configurationId,
          configurationVersion: configuration.configurationVersion,
          secret: process.env.I06_NATIVE_SECRET,
        })
        await call(window, 'setModelPrivacy', { contextId: status.contextId, privacy: 'minimal' })
        const resultId = prepared.firstJob.resultRef.resultId
        const sourceMetadata = await call(window, 'getResult', resultId)
        const sourcePage = await call(window, 'getResultPage', {
          resultId,
          pageSize: 200,
          cursor: null,
        })
        const selected = (
          await call(window, 'selectModelResults', {
            contextId: status.contextId,
            results: [{ resultId, selection: 'historical' }],
          })
        ).selections[0]
        assert.equal(selected.kind, 'whole-result')
        const preview = await call(window, 'previewModelExplanation', {
          contextId: status.contextId,
          configurationId: configuration.configurationId,
          selectionIds: [selected.selectionId],
        })
        const confirmation = await call(window, 'confirmModelAuthorization', {
          contextId: status.contextId,
          previewId: preview.previewId,
        })
        invocationId = (
          await call(window, 'startModelExplanation', {
            contextId: status.contextId,
            configurationId: configuration.configurationId,
            grantId: confirmation.grantId,
            selectionIds: [selected.selectionId],
          })
        ).invocationId
        await until(
          async () =>
            (
              await call(window, 'getModelExplanationOutcome', {
                contextId: status.contextId,
                invocationId,
              })
            ).state === 'completed',
          'NATIVE_MODEL_COMPLETION',
        )
        evidence.selection = { sourceMetadata, sourcePage, selected, preview, confirmation }
        entry.snapshot = await snapshot(window)
        evidence.inspectorClosedBeforeFault = inspector.url() === undefined
        assert.equal(evidence.inspectorClosedBeforeFault, true)
        evidence.stage = 'awaiting-real-crash-dialog'
        save()
        window.webContents.forcefullyCrashRenderer()
      } else if (index === 2) {
        entry.snapshot = await snapshot(window)
        const before = evidence.windows[0].snapshot,
          after = entry.snapshot
        assert.equal(after.status.contextId, before.status.contextId)
        assert.equal(after.status.projectId, before.status.projectId)
        assert.deepEqual(after.status.invocations, before.status.invocations)
        assert.deepEqual(after.status.selections, before.status.selections)
        assert.deepEqual(after.outcome, before.outcome)
        assert.deepEqual(after.marker, before.marker)
        assert.deepEqual(
          after.view.jobs.map((job) => [
            job.jobId,
            job.operationId,
            job.resultRef,
            job.state,
            job.stateVersion,
          ]),
          before.view.jobs.map((job) => [
            job.jobId,
            job.operationId,
            job.resultRef,
            job.state,
            job.stateVersion,
          ]),
        )
        assert.deepEqual(after.view.project, before.view.project)
        assert.ok(evidence.events.some((reason) => ['crashed', 'killed'].includes(reason)))
        assert.equal(evidence.recoveryCalls.includes('startModelExplanation'), false)
        evidence.result = 'passed'
        evidence.stage = 'recovered-after-real-native-action'
        save()
        clearTimeout(deadline)
        app.quit()
      } else throw new Error('UNEXPECTED_EXTRA_NATIVE_RECOVERY')
    } catch (error) {
      fail(error)
    }
  }
  if (newlyCreated || window.webContents.isLoadingMainFrame() || !window.webContents.getURL())
    window.webContents.once('did-finish-load', drive)
  else void drive()
}
setTimeout(() => {
  inspector.close()
  evidence.inspectorClosedBeforeFault = inspector.url() === undefined
  save()
  app.on('browser-window-created', (_event, window) => observe(window, true))
  for (const window of BrowserWindow.getAllWindows()) observe(window)
}, 150)
