// Standalone native test. This never imports Playwright's Electron loader.
import { spawn, execFile } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import {
  accessSync,
  constants,
  createReadStream,
  closeSync,
  lstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  realpathSync,
  renameSync,
  statSync,
  writeFileSync,
  writeSync,
} from 'node:fs'
import { dirname, isAbsolute, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { setTimeout as delay } from 'node:timers/promises'
import { StringDecoder } from 'node:string_decoder'

const tree = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const observerPath = join(tree, 'tests/e2e/c1-native-macos-observer.cjs')
const prefix = 'T01_C1_NATIVE_EVENT '
const cleanupMs = 300000
const logLimit = 4 * 1024 * 1024
const usage = `Usage: node tests/e2e/c1-native-macos-driver.mjs \
  --executable=<this-tree>/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron \
  --app=<this-tree>/apps/desktop \
  --run-root=/tmp/t01-c1-remediation-20261022/native-macos-run-01 \
  --deadline-ms=120000
Requires a separately authorized visible macOS GUI slot and an operator for BOTH real dialogs.
No install/build is performed. Machine success still requires external native-dialog evidence.`

function requireCondition(value, message) {
  if (!value) throw new Error(message)
}

function parseArgs(args) {
  const names = new Set(['executable', 'app', 'run-root', 'deadline-ms'])
  const values = Object.create(null)
  for (const argument of args) {
    const match = /^--([a-z-]+)=(.+)$/.exec(argument)
    requireCondition(match && names.has(match[1]), `unknown or malformed argument: ${argument}`)
    requireCondition(values[match[1]] === undefined, `duplicate argument: ${match[1]}`)
    values[match[1]] = match[2]
  }
  for (const name of names) requireCondition(values[name] !== undefined, `missing --${name}`)
  for (const name of ['executable', 'app', 'run-root']) {
    const value = values[name]
    requireCondition(
      isAbsolute(value) && resolve(value) === value && !/[\0\r\n]/.test(value),
      `--${name} must be a normalized absolute path`,
    )
  }
  requireCondition(values['deadline-ms'] === '120000', 'the authorized runtime is exactly 120000ms')
  requireCondition(
    values.executable ===
      join(tree, 'node_modules/electron/dist/Electron.app/Contents/MacOS/Electron'),
    'executable must be this worktree Electron',
  )
  requireCondition(values.app === join(tree, 'apps/desktop'), 'app must be this worktree desktop')
  requireCondition(
    /^\/tmp\/t01-c1-remediation-20261022\/native-macos-run-[0-9]{2,4}$/.test(values['run-root']),
    'run root must be a new numbered native-macos-run under the authorized /tmp parent',
  )
  return values
}

async function fingerprint(path) {
  const hash = createHash('sha256')
  let bytes = 0
  for await (const chunk of createReadStream(path)) {
    bytes += chunk.length
    hash.update(chunk)
  }
  return { path, bytes, sha256: hash.digest('hex') }
}

function writeJson(path, value) {
  const temporary = `${path}.next`
  writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n', { mode: 0o600 })
  renameSync(temporary, path)
}

function processTable(pids) {
  return new Promise((done, reject) => {
    // comm avoids collecting unrelated users' argument strings.
    execFile(
      '/bin/ps',
      pids
        ? ['-p', pids.join(','), '-o', 'pid=,ppid=,lstart=,command=']
        : ['-axo', 'pid=,ppid=,lstart=,comm='],
      { timeout: 2000, maxBuffer: 4 * 1024 * 1024, env: { ...process.env, LC_ALL: 'C' } },
      (error, stdout) => {
        if (error && !(pids && error.code === 1 && stdout.trim() === '')) return reject(error)
        const rows = new Map()
        for (const line of stdout.split('\n')) {
          const match =
            /^\s*(\d+)\s+(\d+)\s+(\w{3}\s+\w{3}\s+\d+\s+\d\d:\d\d:\d\d\s+\d{4})\s+(.+)$/.exec(line)
          if (match)
            rows.set(Number(match[1]), {
              pid: Number(match[1]),
              ppid: Number(match[2]),
              start: match[3].replace(/\s+/g, ' '),
              command: match[4],
            })
        }
        if (!pids && !rows.has(process.pid))
          return reject(new Error('ps did not include the runner'))
        done(rows)
      },
    )
  })
}

async function run(options) {
  requireCondition(process.platform === 'darwin', 'this native runner requires macOS')
  requireCondition(Number(process.versions.node.split('.')[0]) === 24, 'requires this tree Node 24')
  for (const directory of ['node_modules', '.venv']) {
    const path = join(tree, directory)
    requireCondition(!lstatSync(path).isSymbolicLink(), `${directory} cannot be a borrowed symlink`)
    requireCondition(realpathSync(path) === path, `${directory} must belong to the exact worktree`)
  }
  accessSync(options.executable, constants.X_OK)
  accessSync(join(tree, '.venv/bin/python'), constants.X_OK)
  const packageInfo = JSON.parse(
    readFileSync(join(tree, 'node_modules/electron/package.json'), 'utf8'),
  )
  requireCondition(packageInfo.version === '44.9.0', 'expected pinned Electron 44.9.0')
  const inputs = [
    fileURLToPath(import.meta.url),
    observerPath,
    join(tree, 'apps/desktop/package.json'),
    join(tree, 'apps/desktop/out/main/index.js'),
    join(tree, 'apps/desktop/out/preload/index.js'),
    join(tree, 'apps/desktop/out/renderer/index.html'),
    options.executable,
  ]
  for (const path of inputs) requireCondition(statSync(path).isFile(), `missing input: ${path}`)
  const fingerprints = await Promise.all(inputs.map(fingerprint))
  requireCondition(
    !lstatSync(dirname(options['run-root'])).isSymbolicLink(),
    'run parent cannot be a symlink',
  )
  const parent = realpathSync(dirname(options['run-root']))
  requireCondition(
    parent === realpathSync('/tmp/t01-c1-remediation-20261022'),
    'run parent must resolve to the authorized directory',
  )
  // Non-recursive mkdir is the exclusive claim; never reuse or remove an old run.
  mkdirSync(options['run-root'], { mode: 0o700 })
  const runRoot = realpathSync(options['run-root'])
  for (const name of ['tmp', 'user-data', 'evidence'])
    mkdirSync(join(runRoot, name), { mode: 0o700 })
  const evidenceRoot = join(runRoot, 'evidence')
  const receiptPath = join(evidenceRoot, 'driver.json')
  const descriptors = {
    stdout: openSync(join(evidenceRoot, 'stdout.log'), 'wx', 0o600),
    stderr: openSync(join(evidenceRoot, 'stderr.log'), 'wx', 0o600),
  }
  const receipt = {
    schema: 1,
    runId: randomUUID(),
    tree,
    requestedRunRoot: options['run-root'],
    runRoot,
    startedAt: new Date().toISOString(),
    runner: {
      pid: process.pid,
      argv: process.argv,
      cwd: process.cwd(),
      versions: process.versions,
    },
    inputs: fingerprints,
    runtimeLimitMs: 120000,
    cleanupLimitMs: cleanupMs,
    nativeEvidence: 'REQUIRES_EXTERNAL_RECORDS_OF_BOTH_REAL_DIALOGS_AND_CLICKS',
    machineOutcome: 'pending',
    failures: [],
    cleanup: [],
    processes: [],
  }
  let child
  let socket
  let runtimeTimer
  let polling = true
  let monitor
  let firstFailure
  let observerResult
  let mainClosed = false
  let mainExit
  let cleanupDeadline
  let stdoutText = ''
  const stdoutDecoder = new StringDecoder('utf8')
  let stderrTail = ''
  const logBytes = { stdout: 0, stderr: 0 }
  const known = new Map()
  const reported = new Map()
  let failRun
  const failure = new Promise((_, reject) => {
    failRun = reject
  })
  void failure.catch(() => {})
  const persist = () => {
    receipt.processes = [...known.values()]
    writeJson(receiptPath, receipt)
  }
  const fail = (error) => {
    const message = String(error?.stack ?? error)
    if (receipt.failures.length < 64)
      receipt.failures.push({ at: new Date().toISOString(), message })
    if (!firstFailure) {
      firstFailure = error instanceof Error ? error : new Error(String(error))
      failRun(firstFailure)
    }
  }
  const onSignal = (signal) => fail(new Error(`runner received ${signal}`))
  const interrupt = () => onSignal('SIGINT')
  const terminate = () => onSignal('SIGTERM')
  process.on('SIGINT', interrupt)
  process.on('SIGTERM', terminate)
  const bounded = (promise) => Promise.race([promise, failure])

  function consumeEvent(event) {
    requireCondition(event.runId === receipt.runId, 'observer run identity mismatch')
    if (event.kind === 'child') {
      requireCondition(Number.isSafeInteger(event.pid) && event.pid > 1, 'invalid child pid')
      const record = reported.get(event.pid) ?? { pid: event.pid, firstReportedAt: event.at }
      Object.assign(record, event)
      reported.set(event.pid, record)
      requireCondition(reported.size <= 64, 'observer child limit exceeded')
      if (known.has(event.pid)) known.get(event.pid).childLifecycle = { ...record }
    } else if (event.kind === 'metrics') {
      requireCondition(
        Array.isArray(event.processes) && event.processes.length <= 64,
        'invalid app metric inventory',
      )
      for (const entry of event.processes) {
        requireCondition(Number.isSafeInteger(entry.pid) && entry.pid > 1, 'invalid app metric pid')
        if (!reported.has(entry.pid))
          reported.set(entry.pid, {
            ...entry,
            firstReportedAt: event.at,
            event: 'metric',
            source: 'app.getAppMetrics',
          })
      }
      requireCondition(reported.size <= 128, 'reported process limit exceeded')
    } else if (event.kind === 'result') {
      requireCondition(!observerResult, 'duplicate observer result')
      observerResult = event
      if (event.outcome !== 'succeeded') fail(new Error(`observer failed: ${event.error}`))
    } else if (event.kind === 'phase') {
      console.log(`[native ${receipt.runId}] ${event.phase}`)
    }
  }

  function log(which, chunk) {
    try {
      const room = Math.max(0, logLimit - logBytes[which])
      if (room) writeSync(descriptors[which], chunk.subarray(0, room))
      logBytes[which] += chunk.length
      if (logBytes[which] > logLimit)
        throw new Error(`${which} exceeded 4MiB; original log incomplete`)
      if (which === 'stderr') stderrTail = (stderrTail + chunk.toString('utf8')).slice(-65536)
      if (which !== 'stdout') return
      stdoutText += stdoutDecoder.write(chunk)
      let end
      while ((end = stdoutText.indexOf('\n')) !== -1) {
        const line = stdoutText.slice(0, end)
        stdoutText = stdoutText.slice(end + 1)
        if (line.startsWith(prefix)) consumeEvent(JSON.parse(line.slice(prefix.length)))
      }
      requireCondition(Buffer.byteLength(stdoutText) <= 65536, 'stdout line exceeded 64KiB')
    } catch (error) {
      fail(error)
    }
  }

  async function sample() {
    const rows = await processTable()
    const root = child?.pid
    if (!receipt.runner.identity) receipt.runner.identity = rows.get(process.pid)
    const ownedNow = new Set()
    if (root && !mainClosed && rows.has(root)) ownedNow.add(root)
    for (const entry of known.values()) {
      const current = rows.get(entry.pid)
      if (entry.pid === root && mainClosed) continue
      if (
        !entry.identityChanged &&
        current?.start === entry.start &&
        current.command === entry.command
      )
        ownedNow.add(entry.pid)
    }
    for (let depth = 0; depth < 32; depth++) {
      let changed = false
      for (const row of rows.values())
        if (ownedNow.has(row.ppid) && !ownedNow.has(row.pid)) {
          ownedNow.add(row.pid)
          changed = true
        }
      if (!changed) break
      requireCondition(depth !== 31, 'process ancestry exceeded 32 levels')
    }
    // Original ChildProcess events from our trusted main hook also survive reparenting.
    for (const entry of reported.values()) {
      if (entry.pid === root && mainClosed) continue
      const current = rows.get(entry.pid)
      if (current && Date.parse(current.start) > Date.parse(entry.firstReportedAt) + 1000)
        throw new Error(
          `reported PID has a newer start time: ${entry.pid}; ownership not established`,
        )
      if (entry.event !== 'close' && !known.has(entry.pid) && current) ownedNow.add(entry.pid)
    }
    const discovered = []
    for (const pid of ownedNow) {
      const row = rows.get(pid)
      const existing = known.get(pid)
      if (existing && (existing.start !== row.start || existing.command !== row.command)) {
        existing.identityChanged = true
        fail(new Error(`owned PID identity changed: ${pid}; it will not be signalled`))
        continue
      }
      if (!existing) {
        requireCondition(known.size < 256, 'owned PID limit exceeded')
        known.set(pid, {
          ...row,
          firstSeenAt: new Date().toISOString(),
          source:
            pid === root
              ? 'direct-spawn'
              : reported.get(pid)?.source === 'app.getAppMetrics'
                ? 'app.getAppMetrics'
                : reported.has(pid)
                  ? 'main-child-object'
                  : 'ancestry',
          ...(reported.has(pid) ? { childLifecycle: { ...reported.get(pid) } } : {}),
        })
        discovered.push(pid)
      }
    }
    if (discovered.length) {
      const argumentsNow = await processTable(discovered)
      for (const pid of discovered) {
        const entry = known.get(pid)
        const detail = argumentsNow.get(pid)
        if (detail?.start === entry.start) entry.observedArgv = detail.command
        else
          entry.argvObservation =
            'process disappeared or changed before targeted ps; not reconstructed'
      }
    }
    for (const entry of known.values()) {
      const current = rows.get(entry.pid)
      entry.lastCheckedAt = new Date().toISOString()
      entry.alive = Boolean(
        current && current.start === entry.start && current.command === entry.command,
      )
      if (current && !entry.alive) entry.identityChanged = true
    }
    persist()
    return rows
  }

  async function cleanup() {
    // Reserve five seconds for the final finite inventory and receipt.
    const until = cleanupDeadline - 5000
    receipt.cleanupStartedAt = new Date().toISOString()
    await sample()
    const naturalUntil = Date.now() + 1000
    while (Date.now() < naturalUntil && [...known.values()].some((entry) => entry.alive)) {
      await delay(100)
      await sample()
    }
    receipt.naturalTrackedProcessesAbsent =
      mainClosed && [...known.values()].every((entry) => !entry.alive && !entry.identityChanged)
    // Keep collecting ancestry until the main process is closed. Never kill by name/group.
    for (const signal of ['SIGTERM', 'SIGKILL']) {
      let rows
      try {
        rows = await sample()
      } catch (error) {
        receipt.cleanup.push({ error: `identity unavailable; no blind signal: ${error}` })
        break
      }
      const entries = [...known.values()].sort((a, b) =>
        a.pid === child?.pid ? 1 : b.pid === child?.pid ? -1 : 0,
      )
      for (const entry of entries) {
        if (Date.now() >= until) break
        if (!entry.alive || entry.identityChanged) continue
        if (
          entry.pid === child?.pid &&
          (mainClosed || child.exitCode !== null || child.signalCode !== null)
        )
          continue
        // Refresh immediately before each signal, rather than reusing an old poll snapshot.
        rows = await processTable()
        const current = rows.get(entry.pid)
        if (!current || current.start !== entry.start || current.command !== entry.command) {
          receipt.cleanup.push({ pid: entry.pid, signal, skipped: 'gone or identity changed' })
          continue
        }
        try {
          process.kill(entry.pid, signal)
          receipt.cleanup.push({ pid: entry.pid, signal, at: new Date().toISOString() })
          receipt.testCleanupSignalled = true
        } catch (error) {
          if (error.code !== 'ESRCH')
            receipt.cleanup.push({ pid: entry.pid, signal, error: String(error) })
        }
      }
      const waitUntil = Math.min(until, Date.now() + (signal === 'SIGTERM' ? 3000 : 5000))
      while (Date.now() < waitUntil) {
        await delay(100)
        await sample()
        if ([...known.values()].every((entry) => !entry.alive) && mainClosed) break
      }
      if ([...known.values()].every((entry) => !entry.alive) && mainClosed) break
    }
    await sample()
    receipt.cleanupFinishedAt = new Date().toISOString()
    receipt.trackedProcessesAbsent = [...known.values()].every(
      (entry) => !entry.alive && !entry.identityChanged,
    )
    receipt.mainCloseObserved = mainClosed
    requireCondition(mainClosed, 'direct Electron child close was not observed')
    requireCondition(
      receipt.trackedProcessesAbsent,
      'tracked PID cleanup unresolved; preserve run root',
    )
    requireCondition(
      receipt.naturalTrackedProcessesAbsent && !receipt.testCleanupSignalled,
      'natural product termination incomplete; test cleanup is not product success',
    )
  }

  try {
    persist()
    const observerHash = fingerprints.find((entry) => entry.path === observerPath).sha256
    const config = {
      runId: receipt.runId,
      runRoot,
      userData: join(runRoot, 'user-data'),
      evidenceRoot,
      appPath: realpathSync(options.app),
      executable: realpathSync(options.executable),
    }
    const env = { ...process.env }
    for (const key of [
      'ELECTRON_RUN_AS_NODE',
      'ELECTRON_RENDERER_URL',
      'ONTOLEARN_PACKAGED_EXECUTABLE',
      'I02_HMR',
      'I04_TEST_FIXTURE',
      'I04_NATIVE_ISOLATED',
      'NODE_OPTIONS',
      'ELECTRON_DISABLE_SANDBOX',
    ])
      delete env[key]
    Object.assign(env, {
      TMPDIR: join(runRoot, 'tmp') + '/',
      TMP: join(runRoot, 'tmp'),
      TEMP: join(runRoot, 'tmp'),
      T01_C1_NATIVE_CONFIG: JSON.stringify(config),
    })
    const args = ['--inspect=0', `--user-data-dir=${config.userData}`, options.app]
    receipt.launch = { executable: options.executable, args, cwd: options.app, config }
    child = spawn(options.executable, args, {
      cwd: options.app,
      env,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    receipt.launch.pid = child.pid
    child.stdout.on('data', (chunk) => log('stdout', chunk))
    child.stderr.on('data', (chunk) => log('stderr', chunk))
    child.on('error', fail)
    child.on('exit', (code, signal) => {
      receipt.mainExit = { code, signal, at: new Date().toISOString() }
    })
    const closed = new Promise((done) =>
      child.on('close', (code, signal) => {
        mainClosed = true
        mainExit = { code, signal, at: new Date().toISOString() }
        receipt.mainClose = mainExit
        done(mainExit)
      }),
    )
    runtimeTimer = setTimeout(
      () => fail(new Error('120000ms native runtime deadline exceeded')),
      120000,
    )
    monitor = (async () => {
      while (polling) {
        try {
          await sample()
        } catch (error) {
          fail(error)
        }
        await delay(250)
      }
    })()
    const endpointUntil = Date.now() + 10000
    let endpoint
    while (!endpoint) {
      requireCondition(!mainClosed, 'Electron closed before inspector bootstrap')
      requireCondition(Date.now() < endpointUntil, 'main inspector endpoint timeout')
      endpoint = /Debugger listening on (ws:\/\/127\.0\.0\.1:\d+\/[a-f0-9-]+)/.exec(stderrTail)?.[1]
      if (!endpoint) await bounded(delay(25))
    }
    receipt.inspectorEndpoint = endpoint
    socket = new WebSocket(endpoint)
    await bounded(
      new Promise((done, reject) => {
        socket.addEventListener('open', done, { once: true })
        socket.addEventListener(
          'error',
          () => reject(new Error('main inspector connection failed')),
          { once: true },
        )
        socket.addEventListener(
          'close',
          () => reject(new Error('main inspector closed before open')),
          { once: true },
        )
      }),
    )
    await bounded(
      new Promise((done, reject) => {
        socket.addEventListener(
          'close',
          () => reject(new Error('main inspector closed before injection reply')),
          { once: true },
        )
        socket.addEventListener('message', ({ data }) => {
          try {
            const message = JSON.parse(String(data))
            if (message.id !== 1) return
            if (message.error || message.result?.exceptionDetails)
              reject(new Error(JSON.stringify(message)))
            else done()
          } catch (error) {
            reject(error)
          }
        })
        const expression = `(() => {
        const r = process.getBuiltinModule('module').createRequire(process.execPath);
        const p = ${JSON.stringify(observerPath)};
        const h = r('node:crypto').createHash('sha256').update(r('node:fs').readFileSync(p)).digest('hex');
        if (h !== ${JSON.stringify(observerHash)}) throw new Error('observer changed before injection');
        r(p); return true;
      })()`
        socket.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate', params: { expression } }))
      }),
    )
    socket.close()
    const exit = await bounded(closed)
    requireCondition(
      exit.code === 0 && exit.signal === null,
      `Electron closed ${exit.code}/${exit.signal}`,
    )
    requireCondition(observerResult?.outcome === 'succeeded', 'missing successful observer result')
    const observer = JSON.parse(readFileSync(join(evidenceRoot, 'observer.json'), 'utf8'))
    requireCondition(observer.runId === receipt.runId, 'observer evidence identity mismatch')
    receipt.observer = observer
    receipt.recoveryOutcome = observer.outcome
    requireCondition(
      observer.inspectorClosedBeforeFaults === true,
      'main inspector not proven closed',
    )
    receipt.naturalEngineChildClosesObserved =
      observer.children.length > 0 && observer.children.every((entry) => entry.close)
    requireCondition(
      receipt.naturalEngineChildClosesObserved,
      'original engine child close missing; observer did not delay product quit',
    )
    requireCondition(
      observer.windows.length === 3,
      'expected exactly three real window generations',
    )
    receipt.machineOutcome = 'succeeded'
  } catch (error) {
    fail(error)
    receipt.machineOutcome = 'failed'
  } finally {
    cleanupDeadline = Date.now() + cleanupMs
    receipt.cleanupBudgetStartedAt = new Date().toISOString()
    clearTimeout(runtimeTimer)
    socket?.close()
    polling = false
    if (monitor) await monitor
    try {
      if (child) await cleanup()
    } catch (error) {
      fail(error)
      receipt.machineOutcome = 'failed'
    }
    for (const input of fingerprints.slice(0, -1)) {
      try {
        const after = await fingerprint(input.path)
        requireCondition(after.sha256 === input.sha256, `input changed during run: ${input.path}`)
      } catch (error) {
        fail(error)
        receipt.machineOutcome = 'failed'
      }
    }
    receipt.finishedAt = new Date().toISOString()
    receipt.logBytes = logBytes
    if (firstFailure) receipt.machineOutcome = 'failed'
    try {
      persist()
    } finally {
      for (const descriptor of Object.values(descriptors)) closeSync(descriptor)
      process.off('SIGINT', interrupt)
      process.off('SIGTERM', terminate)
      if (child && !mainClosed) {
        // The bounded cleanup failed. Release only runner-owned pipe/watch handles,
        // preserve the recorded unresolved PID, and let the controller recover it.
        child.stdout.destroy()
        child.stderr.destroy()
        child.unref()
      }
    }
  }
  console.log(
    JSON.stringify({
      receipt: receiptPath,
      machineOutcome: receipt.machineOutcome,
      nativeEvidence: receipt.nativeEvidence,
    }),
  )
  if (firstFailure) throw firstFailure
}

if (process.argv.length === 3 && process.argv[2] === '--help') console.log(usage)
else {
  let options
  try {
    options = parseArgs(process.argv.slice(2))
  } catch (error) {
    console.error(String(error.message) + '\n' + usage)
    process.exitCode = 2
  }
  if (options) {
    try {
      await run(options)
    } catch (error) {
      console.error(error.stack ?? String(error))
      process.exitCode = 1
    }
  }
}
