// Invoke only inside the private T10 Docker/Xvfb session. No Playwright Electron loader.
import { spawn, execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { createRequire } from 'node:module'
import { mkdir, writeFile, readFile } from 'node:fs/promises'

if (
  process.platform !== 'linux' ||
  process.getuid() !== 1110 ||
  !process.env.DISPLAY ||
  process.env.T10_ISOLATED_NATIVE !== '1'
) {
  throw new Error('ISOLATED_LINUX_DISPLAY_REQUIRED')
}
const output = '/opt/t10-evidence'
await mkdir(output, { recursive: true })
const executeFile = promisify(execFile)
const execute = (file, args) =>
  bounded(executeFile(file, args, { timeout: 5000, killSignal: 'SIGKILL' }))
const executable = createRequire('/opt/t10/package.json')('electron')
const hook = '/opt/t10-controls/native-hook.cjs'
const events = []
let stdout = ''
let stderr = ''
let socket
let child
let exit
let timer
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))
const bounded = (promise) => Promise.race([promise, deadline])
const deadline = new Promise((_, reject) => {
  timer = setTimeout(() => reject(new Error('T10_NATIVE_DEADLINE')), 55_000)
})
void deadline.catch(() => {})

async function waitFor(predicate) {
  for (;;) {
    const value = await predicate()
    if (value) return value
    if (exit) throw new Error('NATIVE_EXITED_BEFORE_EXPECTED_EVENT')
    await sleep(100)
  }
}

async function dialogInput(title, key) {
  const window = await bounded(
    waitFor(async () => {
      try {
        const found = await execute('xdotool', ['search', '--onlyvisible', '--name', `^${title}$`])
        const ids = found.stdout
          .trim()
          .split(/\s+/)
          .filter((id) => /^\d+$/.test(id))
        if (ids.length === 1) return ids[0]
        if (ids.length > 1) throw new Error('AMBIGUOUS_NATIVE_DIALOG')
      } catch (error) {
        if (error.message === 'AMBIGUOUS_NATIVE_DIALOG') throw error
      }
      return undefined
    }),
  )
  const actualTitle = (await execute('xdotool', ['getwindowname', window])).stdout.trim()
  const pid = (await execute('xdotool', ['getwindowpid', window])).stdout.trim()
  await execute('xdotool', ['windowactivate', '--sync', window])
  const focused = (await execute('xdotool', ['getwindowfocus'])).stdout.trim()
  if (actualTitle !== title || focused !== window || Number(pid) !== child.pid)
    throw new Error('NATIVE_DIALOG_NOT_FOCUSED_OR_OWNED')
  await bounded(sleep(750))
  await execute('import', [
    '-window',
    window,
    `${output}/${title.endsWith('save') ? 'save' : 'cancel'}-dialog.png`,
  ])
  events.push({ window, pid, title: actualTitle, focused: true, key })
  // Real X keyboard input to the currently verified, focused native dialog.
  await execute('xdotool', ['key', '--clearmodifiers', key])
}

try {
  const env = { ...process.env }
  for (const key of [
    'ELECTRON_RUN_AS_NODE',
    'ELECTRON_DISABLE_SANDBOX',
    'ELECTRON_RENDERER_URL',
    'NODE_OPTIONS',
  ]) {
    delete env[key]
  }
  child = spawn(
    executable,
    ['--inspect=0', '--user-data-dir=/opt/t10-evidence/profile', '/opt/t10/apps/desktop'],
    { cwd: '/opt/t10/apps/desktop', env, detached: true, stdio: ['ignore', 'pipe', 'pipe'] },
  )
  child.stdout.on('data', (part) => {
    stdout = (stdout + part).slice(-65536)
  })
  child.stderr.on('data', (part) => {
    stderr = (stderr + part).slice(-65536)
  })
  child.on('error', (error) => {
    exit = { error: error.message }
  })
  child.on('exit', (code, signal) => {
    exit = { code, signal }
  })
  const endpoint = await bounded(waitFor(() => stderr.match(/ws:\/\/127\.0\.0\.1:[^\s]+/)?.[0]))
  socket = new WebSocket(endpoint)
  await bounded(
    new Promise((resolve, reject) => {
      socket.addEventListener('open', resolve, { once: true })
      socket.addEventListener('error', () => reject(new Error('MAIN_BOOTSTRAP_CONNECT_FAILED')), {
        once: true,
      })
    }),
  )
  const reply = new Promise((resolve, reject) => {
    socket.addEventListener('message', (event) => {
      const message = JSON.parse(String(event.data))
      if (message.id !== 1) return
      if (message.error || message.result?.exceptionDetails)
        reject(new Error('MAIN_BOOTSTRAP_FAILED'))
      else resolve()
    })
    socket.addEventListener('close', () => reject(new Error('MAIN_BOOTSTRAP_CLOSED')), {
      once: true,
    })
  })
  socket.send(
    JSON.stringify({
      id: 1,
      method: 'Runtime.evaluate',
      params: {
        expression: `process.getBuiltinModule('module').createRequire(process.execPath)(${JSON.stringify(hook)})`,
      },
    }),
  )
  await bounded(reply)
  socket.close()
  await dialogInput('T10 01a15bce save', 'alt+s')
  await dialogInput('T10 01a15bce cancel', 'Escape')
  await bounded(waitFor(() => exit))
  if (exit.code !== 0) throw new Error('NATIVE_PROCESS_FAILED')
  const result = JSON.parse(await readFile(`${output}/native.json`, 'utf8'))
  if (result.result !== 'PASS' || !result.pickerUnchanged || !result.mainInspectorClosed) {
    throw new Error('NATIVE_EVIDENCE_FAILED')
  }
  await writeFile(
    `${output}/driver.json`,
    JSON.stringify(
      {
        result: 'PASS',
        childPid: child.pid,
        executable,
        events,
        exit,
        boundary:
          'Actual native save/cancel on container-only display; no host/native-desktop or product App/bridge wiring claim.',
      },
      null,
      2,
    ) + '\n',
  )
} catch (error) {
  await writeFile(
    `${output}/driver.json`,
    JSON.stringify(
      {
        result: 'FAIL',
        events,
        exit: exit ?? null,
        error: error instanceof Error ? error.message : 'NATIVE_DRIVER_FAILED',
      },
      null,
      2,
    ) + '\n',
  )
  process.exitCode = 1
} finally {
  clearTimeout(timer)
  socket?.close()
  if (child?.pid) {
    // This detached group was created by this driver in the private container only.
    try {
      process.kill(-child.pid, 'SIGKILL')
    } catch {
      /* Already exited. */
    }
  }
  await writeFile(`${output}/native-stdout.txt`, stdout)
  await writeFile(`${output}/native-stderr.txt`, stderr)
}
