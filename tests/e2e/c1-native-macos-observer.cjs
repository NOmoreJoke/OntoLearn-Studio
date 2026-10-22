// Main-only test observer. Never replaces native dialog, IPC, health, or renderer preferences.
/* eslint-disable @typescript-eslint/no-require-imports */
const { app, BrowserWindow } = require('electron')
const inspector = require('node:inspector')
const { ChildProcess } = require('node:child_process')
const { writeFileSync, renameSync, appendFileSync, statSync, realpathSync } = require('node:fs')
const { join, isAbsolute } = require('node:path')

const config = JSON.parse(process.env.T01_C1_NATIVE_CONFIG ?? 'null')
if (!config || typeof config.runId !== 'string') throw new Error('missing native observer identity')
for (const key of ['runRoot', 'userData', 'evidenceRoot', 'appPath', 'executable'])
  if (typeof config[key] !== 'string' || !isAbsolute(config[key])) throw new Error(`invalid ${key}`)
if (
  config.userData !== join(config.runRoot, 'user-data') ||
  config.evidenceRoot !== join(config.runRoot, 'evidence')
)
  throw new Error('observer paths are not this run children')
const installed = Symbol.for('T01.C1.native.observer')
if (globalThis[installed]) throw new Error('native observer already installed')
globalThis[installed] = true

const evidence = {
  schema: 1,
  runId: config.runId,
  pid: process.pid,
  startedAt: new Date().toISOString(),
  argv: process.argv,
  versions: process.versions,
  windows: [],
  events: [],
  health: [],
  children: [],
  outcome: 'pending',
  nativeDialogEvidence: 'EXTERNAL_VISIBLE_DIALOG_AND_ACTUAL_CLICK_RECORDS_REQUIRED',
}
const output = join(config.evidenceRoot, 'observer.json')
const events = join(config.evidenceRoot, 'observer-events.jsonl')
const prefix = 'T01_C1_NATIVE_EVENT '
const originalSpawn = ChildProcess.prototype.spawn
let finishing = false
let terminalEmitted = false
let timer
const seen = new Set()
const children = new Map()
const sleep = (ms) => new Promise((done) => setTimeout(done, ms))

function check(condition, message) {
  if (!condition) throw new Error(message)
}

function save() {
  const temporary = output + '.next'
  writeFileSync(temporary, JSON.stringify(evidence, null, 2) + '\n', { mode: 0o600 })
  renameSync(temporary, output)
}

function event(kind, data = {}) {
  check(evidence.events.length < 512, 'observer event limit exceeded')
  const value = { runId: config.runId, kind, at: new Date().toISOString(), ...data }
  evidence.events.push(value)
  appendFileSync(events, JSON.stringify(value) + '\n', { mode: 0o600 })
  process.stdout.write(prefix + JSON.stringify(value) + '\n')
  save()
}

function phase(value) {
  evidence.phase = value
  event('phase', { phase: value })
  event('metrics', { processes: app.getAppMetrics().map(({ pid, type }) => ({ pid, type })) })
}

function emitResult() {
  if (terminalEmitted) return
  terminalEmitted = true
  event('result', { outcome: evidence.outcome, error: evidence.error ?? null })
}

function fail(error) {
  if (!evidence.error) evidence.error = String(error?.stack ?? error)
  evidence.outcome = 'failed'
  try {
    save()
  } catch (writeError) {
    console.error('native observer evidence write failed', writeError)
  }
  if (!finishing) {
    finishing = true
    setImmediate(() => app.quit())
  }
}

// Observe original ChildProcess objects before the first real health request.
// The original spawn return/exception and stream contents are never substituted.
ChildProcess.prototype.spawn = function (...args) {
  const result = Reflect.apply(originalSpawn, this, args)
  try {
    check(children.size < 16, 'native observer child limit exceeded')
    const record = {
      ordinal: children.size,
      pid: this.pid ?? null,
      file: this.spawnfile,
      argv: this.spawnargs,
      createdAt: new Date().toISOString(),
    }
    children.set(this, record)
    evidence.children.push(record)
    const note = (name, extra = {}) => {
      try {
        record.pid = this.pid ?? record.pid
        record[name] = { at: new Date().toISOString(), ...extra }
        if (record.pid)
          event('child', {
            pid: record.pid,
            file: record.file,
            argv: record.argv,
            event: name,
            ...extra,
          })
        else save()
      } catch (error) {
        fail(error)
      }
    }
    this.on('spawn', () => note('spawn'))
    this.on('error', (error) => note('error', { message: String(error) }))
    this.on('exit', (code, signal) => note('exit', { code, signal }))
    this.on('close', (code, signal) => note('close', { code, signal }))
    note('created')
  } catch (error) {
    setImmediate(() => fail(error))
  }
  return result
}

// Passive only: do not prevent quit, wait in the product lifecycle, or stop children.
// Missing natural child-close evidence is a failure for the driver, never repaired here.
app.on('before-quit', () => {
  clearTimeout(timer)
  evidence.productBeforeQuitAt = new Date().toISOString()
  if (evidence.outcome !== 'succeeded' && !evidence.error)
    fail(new Error('app quit before native sequence completed'))
  try {
    save()
  } catch (error) {
    console.error(error)
  }
})
app.on('will-quit', () => {
  ChildProcess.prototype.spawn = originalSpawn
  evidence.productWillQuitAt = new Date().toISOString()
  try {
    emitResult()
    save()
  } catch (error) {
    console.error(error)
  }
})

async function healthy(window, ordinal) {
  check(!window.isDestroyed(), 'window destroyed before health')
  const readyUntil = Date.now() + 5000
  let initial
  do {
    initial = await window.webContents.executeJavaScript(`({
    initial: document.querySelector('[role=status]')?.textContent,
    bridge: typeof window.ontolearn?.getEngineHealth,
    require: typeof window.require
  })`)
    if (initial.initial?.includes('尚未检查') && initial.bridge === 'function') break
    check(Date.now() < readyUntil, 'real renderer initial state did not become ready')
    await sleep(25)
  } while (Date.now() <= readyUntil)
  check(
    initial.initial?.includes('尚未检查') && initial.bridge === 'function',
    'unexpected actual initial renderer state',
  )
  check(initial.require === 'undefined', 'renderer exposes Node require')
  const preferences = window.webContents.getLastWebPreferences()
  check(
    preferences.contextIsolation === true &&
      preferences.sandbox === true &&
      preferences.nodeIntegration === false,
    'actual renderer isolation preferences invalid',
  )
  const result = await window.webContents.executeJavaScript('window.ontolearn.getEngineHealth()')
  evidence.health.push({
    ordinal,
    at: new Date().toISOString(),
    result,
    initial,
    preferences: {
      contextIsolation: preferences.contextIsolation,
      sandbox: preferences.sandbox,
      nodeIntegration: preferences.nodeIntegration,
    },
  })
  check(result?.ok === true, 'real engine health unavailable')
  event('health', { ordinal, ok: true, rendererPid: window.webContents.getOSProcessId() })
}

async function drive(window, ordinal) {
  if (finishing) return
  try {
    check(
      evidence.inspectorClosedBeforeFaults === true && inspector.url() === undefined,
      'main inspector still open',
    )
    window.show()
    app.focus({ steal: true })
    window.focus()
    const focusUntil = Date.now() + 3000
    while (!window.isFocused() || !window.isVisible()) {
      check(Date.now() < focusUntil, 'requires a focused visible native window')
      await sleep(50)
    }
    await healthy(window, ordinal)
    check(!finishing && !evidence.error, 'observer stopped during actual health request')
    if (ordinal === 1) {
      phase('crash: operator must record real stopped-window dialog and click 重新打开窗口')
      evidence.crashFaultAt = new Date().toISOString()
      save()
      window.webContents.forcefullyCrashRenderer()
    } else if (ordinal === 2) {
      check(
        evidence.windows[0].goneReason === 'killed' || evidence.windows[0].goneReason === 'crashed',
        'missing real renderer crash',
      )
      check(evidence.windows[0].closedAt, 'first window not actually destroyed')
      check(!app.commandLine.hasSwitch('disable-hang-monitor'), 'hang monitor disabled before hang')
      phase('hang: operator must record real unresponsive dialog and click 重新打开窗口')
      evidence.hangFaultAt = new Date().toISOString()
      save()
      void window.webContents.executeJavaScript('for (;;) {}').catch((error) => {
        if (window.isDestroyed() || window.webContents.isDestroyed()) {
          evidence.hangScriptDisposed = String(error)
          try {
            save()
          } catch (writeError) {
            fail(writeError)
          }
        } else fail(error)
      })
      setTimeout(() => {
        try {
          check(!finishing && !window.isDestroyed(), 'window lost before hang trigger')
          check(
            window.isVisible() && window.isFocused(),
            'hang trigger requires actual visible focused window',
          )
          check(
            !app.commandLine.hasSwitch('disable-hang-monitor'),
            'hang monitor disabled at trigger',
          )
          event('hang-input', { ordinal, visible: true, focused: true, x: 400, y: 400 })
          for (const type of ['mouseDown', 'mouseUp'])
            window.webContents.sendInputEvent({
              type,
              x: 400,
              y: 400,
              button: 'left',
              clickCount: 1,
            })
        } catch (error) {
          fail(error)
        }
      }, 250)
    } else if (ordinal === 3) {
      check(evidence.windows[1].unresponsiveAt, 'missing real unresponsive event')
      check(evidence.windows[1].closedAt, 'hung window not actually destroyed')
      check(
        evidence.windows.length === 3 && evidence.health.length === 3,
        'unexpected recovery generations',
      )
      check(evidence.children.length > 0, 'real engine ChildProcess was not observed')
      evidence.outcome = 'succeeded'
      evidence.engineDatabase = {
        path: join(config.userData, 'engine.sqlite'),
        existsAsFile: (() => {
          try {
            return statSync(join(config.userData, 'engine.sqlite')).isFile()
          } catch {
            return false
          }
        })(),
      }
      phase(
        'machine assertions complete; real dialog screenshots/click records remain external evidence',
      )
      finishing = true
      app.quit()
    } else throw new Error('unexpected fourth window generation')
  } catch (error) {
    fail(error)
  }
}

function observe(window, fresh = false) {
  if (seen.has(window.id)) return
  seen.add(window.id)
  const ordinal = evidence.windows.length + 1
  if (ordinal > 3) return fail(new Error('unexpected extra BrowserWindow'))
  const record = {
    ordinal,
    id: window.id,
    webContentsId: window.webContents.id,
    createdAt: new Date().toISOString(),
  }
  evidence.windows.push(record)
  window.on('closed', () => {
    record.closedAt = new Date().toISOString()
    try {
      event('window-closed', { ordinal })
    } catch (error) {
      fail(error)
    }
  })
  window.webContents.on('render-process-gone', (_event, details) => {
    record.goneReason = details.reason
    try {
      event('render-process-gone', { ordinal, details })
    } catch (error) {
      fail(error)
    }
  })
  window.on('unresponsive', () => {
    record.unresponsiveAt = new Date().toISOString()
    try {
      event('unresponsive', { ordinal })
    } catch (error) {
      fail(error)
    }
  })
  if (fresh || window.webContents.isLoadingMainFrame() || !window.webContents.getURL())
    window.webContents.once('did-finish-load', () => void drive(window, ordinal))
  else void drive(window, ordinal)
  event('window', {
    ordinal,
    id: window.id,
    webContentsId: record.webContentsId,
    rendererPid: window.webContents.getOSProcessId(),
  })
}

timer = setTimeout(() => fail(new Error('native observer runtime exceeded 115000ms')), 115000)
// Allow the one bootstrap Runtime.evaluate reply to leave before closing MAIN inspector.
setTimeout(() => {
  try {
    inspector.close()
    evidence.inspectorClosedBeforeFaults = inspector.url() === undefined
    check(evidence.inspectorClosedBeforeFaults, 'could not close main inspector')
    evidence.runtime = {
      userData: realpathSync(app.getPath('userData')),
      appPath: realpathSync(app.getAppPath()),
      executable: realpathSync(process.execPath),
      packaged: app.isPackaged,
      hangMonitorEnabled: !app.commandLine.hasSwitch('disable-hang-monitor'),
      noSandboxSwitch: app.commandLine.hasSwitch('no-sandbox'),
    }
    check(process.platform === 'darwin', 'native observer requires macOS')
    check(evidence.runtime.userData === config.userData, 'actual userData differs from this run')
    check(
      evidence.runtime.appPath === config.appPath &&
        evidence.runtime.executable === config.executable,
      'actual app/executable identity differs',
    )
    check(!evidence.runtime.packaged, 'this window covers built/file compatibility, not packaged')
    check(
      evidence.runtime.hangMonitorEnabled && !evidence.runtime.noSandboxSwitch,
      'native safety switches invalid',
    )
    check(
      !process.argv.includes('--t01-internal-business3'),
      'business3 creation is outside this native window',
    )
    phase('main inspector closed; visible default-profile health and native recovery only')
    app.on('browser-window-created', (_event, window) => {
      try {
        observe(window, true)
      } catch (error) {
        fail(error)
      }
    })
    for (const window of BrowserWindow.getAllWindows()) observe(window)
  } catch (error) {
    fail(error)
  }
}, 150)
