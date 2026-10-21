// Test-only MAIN instrumentation. Never register IPC or modify the app/renderer source.
/* eslint-disable @typescript-eslint/no-require-imports */
if (
  process.platform !== 'linux' ||
  process.getuid() !== 1110 ||
  !process.env.DISPLAY ||
  process.env.T10_ISOLATED_NATIVE !== '1'
)
  throw new Error('ISOLATED_LINUX_DISPLAY_REQUIRED')
const { app, BrowserWindow, dialog } = require('electron')
const fs = require('node:fs')
const path = require('node:path')
const crypto = require('node:crypto')
const inspector = require('node:inspector')
const {
  PreparedHtmlReportFile,
} = require('/opt/t10/build/t10-native-runtime/prepared-report-file.cjs')

const output = '/opt/t10-evidence'
const savePath = path.join(output, 'native-report.html')
const cancelPath = path.join(output, 'cancelled-report.html')
const originalPicker = dialog.showSaveDialog
const evidence = { stage: 'bootstrap', selections: [], nativeDialogs: 0 }
const write = () =>
  fs.writeFileSync(path.join(output, 'native.json'), JSON.stringify(evidence, null, 2) + '\n')
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function run() {
  inspector.close()
  evidence.mainInspectorClosed = inspector.url() === undefined
  await app.whenReady()
  let window
  for (let attempt = 0; attempt < 200; attempt++) {
    window = BrowserWindow.getAllWindows().find((item) => !item.isDestroyed())
    if (
      window &&
      !window.webContents.isLoadingMainFrame() &&
      window.webContents.getURL().startsWith('file:')
    )
      break
    await wait(50)
  }
  if (!window || window.webContents.isLoadingMainFrame())
    throw new Error('NATIVE_WINDOW_UNAVAILABLE')
  const preferences = window.webContents.getLastWebPreferences()
  evidence.rendererBridge = await window.webContents.executeJavaScript(
    `({ bridge: typeof window.ontolearn?.getEngineHealth, require: typeof window.require })`,
  )
  if (
    evidence.rendererBridge.bridge !== 'function' ||
    evidence.rendererBridge.require !== 'undefined'
  ) {
    throw new Error('NATIVE_BRIDGE_UNAVAILABLE')
  }
  evidence.engineHealth = await window.webContents.executeJavaScript(
    'window.ontolearn.getEngineHealth()',
  )
  if (!evidence.engineHealth.ok) throw new Error('NATIVE_ENGINE_UNAVAILABLE')
  evidence.runtime = {
    uid: process.getuid(),
    platform: process.platform,
    arch: process.arch,
    versions: process.versions,
    noSandbox: app.commandLine.hasSwitch('no-sandbox'),
    hangMonitorEnabled: !app.commandLine.hasSwitch('disable-hang-monitor'),
    mockKeychain: app.commandLine.hasSwitch('use-mock-keychain'),
    preferences: {
      sandbox: preferences.sandbox,
      contextIsolation: preferences.contextIsolation,
      nodeIntegration: preferences.nodeIntegration,
    },
    rendererDevTools: window.webContents.isDevToolsOpened(),
  }
  if (
    !evidence.mainInspectorClosed ||
    evidence.runtime.uid === 0 ||
    evidence.runtime.noSandbox ||
    !evidence.runtime.hangMonitorEnabled ||
    evidence.runtime.mockKeychain ||
    !preferences.sandbox ||
    !preferences.contextIsolation ||
    preferences.nodeIntegration
  ) {
    throw new Error('NATIVE_ISOLATION_INVALID')
  }
  const rendererPid = window.webContents.getOSProcessId()
  const status = fs.readFileSync(`/proc/${rendererPid}/status`, 'utf8')
  evidence.rendererIsolation = Object.fromEntries(
    status
      .split('\n')
      .filter((line) => /^(NoNewPrivs|Seccomp|Seccomp_filters|CapEff|NSpid):/.test(line))
      .map((line) => {
        const colon = line.indexOf(':')
        return [line.slice(0, colon), line.slice(colon + 1).trim()]
      }),
  )
  if (
    evidence.rendererIsolation.NoNewPrivs !== '1' ||
    evidence.rendererIsolation.Seccomp !== '2' ||
    !/^0+$/.test(evidence.rendererIsolation.CapEff ?? '') ||
    evidence.runtime.rendererDevTools
  )
    throw new Error('NATIVE_RENDERER_ISOLATION_INVALID')
  const input = JSON.parse(
    fs.readFileSync('/opt/t10/tests/fixtures/transfer/report-input.json', 'utf8'),
  )
  const attacks = JSON.parse(
    fs.readFileSync('/opt/t10/tests/fixtures/transfer/malicious-texts.json', 'utf8'),
  )
  input.goals = attacks
  const picker = (title, defaultPath) => async () => {
    evidence.stage = title
    evidence.nativeDialogs++
    write()
    const selected = await dialog.showSaveDialog(window, {
      title,
      defaultPath,
      filters: [{ name: 'HTML report', extensions: ['html'] }],
    })
    evidence.selections.push({
      cancelled: selected.canceled,
      filename: selected.filePath ? path.basename(selected.filePath) : null,
    })
    return selected.canceled
      ? null
      : { directory: path.dirname(selected.filePath), filename: path.basename(selected.filePath) }
  }
  const artifact = new PreparedHtmlReportFile(input)
  evidence.save = await artifact.save(picker('T10 01a15bce save', savePath))
  const actual = fs.readFileSync(savePath)
  evidence.actualFile = {
    byteLength: actual.length,
    sha256: crypto.createHash('sha256').update(actual).digest('hex'),
    mode: fs.statSync(savePath).mode & 0o777,
  }
  if (
    evidence.save.state !== 'published' ||
    evidence.actualFile.sha256 !== artifact.metadata.sha256 ||
    evidence.actualFile.byteLength !== artifact.metadata.byteLength
  )
    throw new Error('NATIVE_FILE_MISMATCH')
  evidence.cancel = await new PreparedHtmlReportFile(input).save(
    picker('T10 01a15bce cancel', cancelPath),
  )
  evidence.cancelFileAbsent = !fs.existsSync(cancelPath)
  evidence.pickerUnchanged = originalPicker === dialog.showSaveDialog
  if (
    evidence.cancel.state !== 'cancelled' ||
    !evidence.cancelFileAbsent ||
    !evidence.pickerUnchanged ||
    evidence.nativeDialogs !== 2
  )
    throw new Error('NATIVE_CANCEL_MISMATCH')
  evidence.stage = 'complete'
  evidence.result = 'PASS'
  evidence.boundary =
    'Private service and real Linux save/cancel dialog; no public App/bridge, trusted projection, credentials, Windows/macOS or G.6 claim.'
  write()
  app.exit(0)
}

setTimeout(() => {
  void run().catch((error) => {
    evidence.result = 'FAIL'
    evidence.error = error instanceof Error ? error.message : 'NATIVE_PROBE_FAILED'
    write()
    app.exit(1)
  })
}, 200)
