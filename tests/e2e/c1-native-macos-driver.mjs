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
import { connect } from 'node:net'

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

// BEGIN pure process-accounting classifier (extracted verbatim by focused checks).
const processQuarantineMs = 2000

function parseProcessRows(stdout) {
  const rows = new Map()
  const unparsed = []
  for (const line of stdout.split('\n')) {
    if (!line.trim()) continue
    const match =
      /^\s*(\d+)\s+(\d+)\s+(\w{3}\s+\w{3}\s+\d+\s+\d\d:\d\d:\d\d\s+\d{4})\s+(\S+)\s+(.+)$/.exec(
        line,
      )
    if (!match) {
      unparsed.push({ pid: Number(/^\s*(\d+)/.exec(line)?.[1]) || null, rawLine: line })
      continue
    }
    const pid = Number(match[1])
    const row = {
      pid,
      ppid: Number(match[2]),
      start: match[3].replace(/\s+/g, ' '),
      stat: match[4],
      command: match[5],
      rawLine: line,
    }
    if (
      !Number.isSafeInteger(pid) ||
      pid < 0 ||
      !Number.isSafeInteger(row.ppid) ||
      row.ppid < 0 ||
      !Number.isFinite(Date.parse(row.start)) ||
      !/^[A-Z?][A-Za-z0-9+<>=-]*$/.test(row.stat) ||
      rows.has(pid)
    )
      unparsed.push({ pid, rawLine: line })
    else rows.set(pid, row)
  }
  return { rows, unparsed, parseComplete: unparsed.length === 0 }
}

function originalClose(lifecycle) {
  return Boolean(
    lifecycle?.exit &&
    lifecycle?.close &&
    !lifecycle.error &&
    lifecycle.exit.code === 0 &&
    lifecycle.exit.signal === null &&
    lifecycle.close.code === 0 &&
    lifecycle.close.signal === null &&
    Number.isFinite(lifecycle.exit.receivedAtMs) &&
    Number.isFinite(lifecycle.close.receivedAtMs) &&
    lifecycle.exit.receivedAtMs <= lifecycle.close.receivedAtMs,
  )
}

function classifyProcess(entry, row, sample, lifecycle, nowMs) {
  const requiresClose = entry.source === 'direct-spawn' || entry.source === 'main-child-object'
  const lifecycleClosed = Boolean(lifecycle?.close)
  const trustedOriginalClose = originalClose(lifecycle)
  const invalidLifecycle = Boolean(
    lifecycle?.error ||
    (lifecycle?.exit && (lifecycle.exit.code !== 0 || lifecycle.exit.signal !== null)) ||
    (lifecycle?.close && !trustedOriginalClose),
  )
  const diagnosticIncomplete = Boolean(entry.diagnosticIncomplete || !sample.parseComplete)
  const rowPresent = Boolean(row)
  const birthMismatch = Boolean(entry.birthMismatch || (row && row.start !== entry.start))
  const changedDisplay = Boolean(row && row.command !== entry.command)
  const displayMismatch = Boolean(entry.displayMismatch || changedDisplay)
  const postTerminalRow = Boolean(entry.postTerminalRow || (entry.resolvedTerminal && rowPresent))
  // A terminal-looking display is only pending. Active/unknown display changes
  // remain unexplained, even if a later close or absence arrives.
  const unexplainedDisplay = Boolean(
    entry.unexplainedDisplay || (changedDisplay && !row.stat.startsWith('Z')),
  )
  const quarantine = Boolean(displayMismatch || birthMismatch || postTerminalRow)
  const quarantineSinceMs = entry.quarantineSinceMs ?? (quarantine ? nowMs : null)
  const lastPresentEndedMs = rowPresent ? sample.endedAtMs : entry.lastPresentEndedMs
  const absenceAfterMs = Math.max(
    entry.firstSeenAtMs,
    lastPresentEndedMs ?? entry.firstSeenAtMs,
    requiresClose ? (lifecycle?.close?.receivedAtMs ?? Infinity) : entry.firstSeenAtMs,
  )
  const freshAbsence = Boolean(
    !rowPresent && sample.parseComplete && sample.startedAtMs > absenceAfterMs,
  )
  const resolvedTerminal = Boolean(
    entry.ownershipEstablished &&
    freshAbsence &&
    !birthMismatch &&
    !diagnosticIncomplete &&
    !postTerminalRow &&
    !unexplainedDisplay &&
    !invalidLifecycle &&
    (!displayMismatch || trustedOriginalClose) &&
    (!requiresClose || trustedOriginalClose),
  )
  const terminalPending = Boolean(
    !resolvedTerminal &&
    (quarantine || lifecycle?.exit || lifecycleClosed || row?.stat.startsWith('Z')),
  )
  const signalEligible = Boolean(
    entry.ownershipEstablished &&
    rowPresent &&
    !birthMismatch &&
    !displayMismatch &&
    !postTerminalRow &&
    !diagnosticIncomplete &&
    !lifecycle?.exit &&
    !lifecycleClosed &&
    !invalidLifecycle &&
    !row.stat.startsWith('Z') &&
    /^[IRSUTW]/.test(row.stat),
  )
  const quarantineExpired = Boolean(
    terminalPending &&
    quarantineSinceMs !== null &&
    nowMs - quarantineSinceMs >= processQuarantineMs,
  )
  const failureReason = birthMismatch
    ? 'birth-conflict'
    : diagnosticIncomplete
      ? 'diagnostic-incomplete'
      : postTerminalRow
        ? 'row-after-terminal'
        : invalidLifecycle
          ? 'original-lifecycle-failed'
          : quarantineExpired && !resolvedTerminal
            ? 'quarantine-unresolved'
            : null
  return {
    rowPresent,
    birthMismatch,
    displayMismatch,
    unexplainedDisplay,
    postTerminalRow,
    quarantine,
    quarantineSinceMs,
    lastPresentEndedMs,
    trustedOriginalClose,
    lifecycleClosed,
    terminalPending,
    freshAbsence,
    resolvedTerminal,
    signalEligible,
    diagnosticIncomplete,
    failureReason,
  }
}

function observerProjection(observer, runId, mainExit, mainClose) {
  if (!observer || observer.runId !== runId) throw new Error('observer evidence identity mismatch')
  const children = observer.children
  if (
    !Array.isArray(children) ||
    children.length > 16 ||
    !Array.isArray(observer.events) ||
    observer.events.length > 512 ||
    !Array.isArray(observer.windows) ||
    observer.windows.length > 3 ||
    !Array.isArray(observer.health) ||
    observer.health.length > 3
  )
    throw new Error('observer evidence shape unavailable')
  const childCloses =
    children.length > 0 &&
    children.every(
      (entry) =>
        entry.exit?.code === 0 &&
        entry.exit.signal === null &&
        entry.close?.code === 0 &&
        entry.close.signal === null,
    )
  return {
    observer,
    recoveryOutcome: observer.outcome,
    childLifecycleOutcome: {
      outcome: childCloses ? 'succeeded' : 'incomplete',
      source: 'observer-file',
      records: children,
    },
    naturalEngineChildClosesObserved: childCloses,
    mainLifecycleOutcome: {
      outcome:
        mainExit?.code === 0 &&
        mainExit.signal === null &&
        mainClose?.code === 0 &&
        mainClose.signal === null
          ? 'succeeded'
          : 'incomplete',
      exit: mainExit ?? null,
      close: mainClose ?? null,
    },
  }
}
// END pure process-accounting classifier.

// BEGIN finite termination projection (distinct from the preserved 650 classifier).
function validFiniteSample(sample, scope) {
  return Boolean(
    sample &&
    sample.scope === scope &&
    sample.parseComplete &&
    sample.validUtf8 &&
    !sample.timedOut &&
    !sample.truncated &&
    !sample.signal &&
    Number.isFinite(sample.startedAtMs) &&
    Number.isFinite(sample.endedAtMs) &&
    sample.endedAtMs >= sample.startedAtMs &&
    /^[a-f0-9]{64}$/.test(sample.stdoutSHA256 ?? '') &&
    (sample.exitCode === 0 ||
      (scope === 'targets' &&
        sample.exitCode === 1 &&
        sample.emptyOutput &&
        sample.stderrBytes === 0)) &&
    (scope !== 'full-table' || sample.runnerAnchorPresent),
  )
}

function finiteObservation(entry, row, sample, lifecycleSnapshot, nowMs, argv = false) {
  const requiresClose = entry.source === 'direct-spawn' || entry.source === 'main-child-object'
  const naturallyClosed = requiresClose ? originalClose(lifecycleSnapshot) : null
  const executableConflict =
    entry.confirmedExecutableConflict ||
    Boolean(
      !argv &&
      row &&
      row.command.startsWith('/') &&
      entry.command.startsWith('/') &&
      row.command !== entry.command,
    )
  const lifecycleFailed = Boolean(
    lifecycleSnapshot?.error ||
    (lifecycleSnapshot?.exit &&
      (lifecycleSnapshot.exit.code !== 0 || lifecycleSnapshot.exit.signal !== null)) ||
    (lifecycleSnapshot?.close && !originalClose(lifecycleSnapshot)),
  )
  const hard =
    entry.finiteHardConflict ||
    (entry.argvBirthConflict
      ? 'argv-birth-conflict'
      : executableConflict
        ? 'confirmed-executable-conflict'
        : entry.birthMismatch || (row && row.start !== entry.start)
          ? 'birth-conflict'
          : entry.postTerminalRow || (entry.finiteTerminationEstablished && row)
            ? 'post-termination-row'
            : entry.diagnosticIncomplete || !sample.parseComplete
              ? 'diagnostic-incomplete'
              : lifecycleFailed
                ? 'original-lifecycle-conflict'
                : null)
  const lastPresent = row
    ? Math.max(entry.finiteLastPresentEndedMs ?? 0, sample.endedAtMs)
    : (entry.finiteLastPresentEndedMs ?? entry.lastPresentEndedMs ?? entry.firstSeenAtMs)
  const absenceAfter = Math.max(
    entry.firstSeenAtMs,
    lastPresent,
    requiresClose ? (lifecycleSnapshot?.close?.receivedAtMs ?? Infinity) : entry.firstSeenAtMs,
  )
  return {
    confirmedExecutableConflict: Boolean(executableConflict),
    finiteHardConflict: hard,
    signalEligible: Boolean(!hard && entry.signalEligible),
    historicalUnknown: Boolean(
      entry.historicalUnknown ||
      entry.displayMismatch ||
      entry.unexplainedDisplay ||
      (row && !argv && row.command !== entry.command),
    ),
    originalClosedNaturally: naturallyClosed,
    finiteLastPresentEndedMs: lastPresent,
    absentAtValidSample: Boolean(
      !row && validFiniteSample(sample, 'full-table') && sample.startedAtMs > absenceAfter,
    ),
    finiteTerminationEstablished: Boolean(entry.finiteTerminationEstablished && !row && !hard),
    finiteConsumedAtMs: nowMs,
  }
}

function completeFiniteClosure(certificate) {
  return Boolean(
    certificate?.complete &&
    /^[a-f0-9]{64}$/.test(certificate.inputSourceHash ?? '') &&
    validFiniteSample(certificate.fullTable, 'full-table') &&
    validFiniteSample(certificate.knownPidCheck, 'targets') &&
    certificate.knownPidCheck.startedAtMs >= certificate.fullTable.endedAtMs &&
    certificate.knownPidCheck.sequence > certificate.fullTable.sequence &&
    Array.isArray(certificate.knownPids) &&
    certificate.knownPids.length > 0 &&
    certificate.knownPids.length <= 256 &&
    certificate.knownPids.every(
      (pid, index, list) =>
        Number.isSafeInteger(pid) && pid > 1 && (index === 0 || pid > list[index - 1]),
    ) &&
    JSON.stringify(certificate.knownPidCheck.queriedPids) ===
      JSON.stringify(certificate.knownPids) &&
    certificate.reportedPids.every((pid) => certificate.knownPids.includes(pid)) &&
    certificate.knownPidCheck.emptyOutput &&
    certificate.knownPidCheck.rowCount === 0 &&
    certificate.originalMainClosedNaturally &&
    certificate.reportedUnbound.length === 0 &&
    certificate.unboundCandidates.length === 0 &&
    certificate.ownExecutableRows.length === 0 &&
    certificate.scopeEstablished &&
    certificate.port?.outcome === 'refused',
  )
}

function projectFiniteTermination(entry, certificate, issuedAtMs) {
  const requiresClose = entry.source === 'direct-spawn' || entry.source === 'main-child-object'
  const previous = entry.finiteCertificate
  const quarantineStart = entry.quarantineSinceMs
  const timely =
    (previous && entry.finiteTerminationEstablished) ||
    quarantineStart == null ||
    (issuedAtMs >= quarantineStart && issuedAtMs - quarantineStart < processQuarantineMs)
  const laterThan = Math.max(
    entry.firstSeenAtMs,
    entry.finiteLastPresentEndedMs ?? 0,
    requiresClose
      ? (entry.finiteLifecycleSnapshot?.close?.receivedAtMs ?? Infinity)
      : entry.firstSeenAtMs,
  )
  const established = Boolean(
    entry.ownershipEstablished &&
    !entry.finiteHardConflict &&
    entry.absentAtValidSample &&
    (!requiresClose || entry.originalClosedNaturally) &&
    timely &&
    completeFiniteClosure(certificate) &&
    certificate.fullTable.startedAtMs > laterThan &&
    certificate.knownPids.includes(entry.pid),
  )
  return {
    finiteTerminationEstablished: established,
    finiteCertificate: established
      ? {
          inputSourceHash: certificate.inputSourceHash,
          fullTableSequence: certificate.fullTable.sequence,
          knownPidSequence: certificate.knownPidCheck.sequence,
          fullTableStdoutSHA256: certificate.fullTable.stdoutSHA256,
          knownPidStdoutSHA256: certificate.knownPidCheck.stdoutSHA256,
          issuedAtMs: previous?.issuedAtMs ?? issuedAtMs,
          statement: requiresClose
            ? 'original object closed naturally and established-owned PID absent in valid samples'
            : 'established-owned PID absent in valid post-settle samples; independent exit code not observed',
        }
      : (previous ?? null),
  }
}

function finiteRunClosed(entries, reportedPids, sampling, evidence) {
  const knownPids = entries.map((entry) => entry.pid).sort((a, b) => a - b)
  return Boolean(
    entries.length &&
    !sampling.diagnosticIncomplete &&
    evidence.hardFailures.length === 0 &&
    completeFiniteClosure(evidence.certificate) &&
    JSON.stringify(knownPids) === JSON.stringify(evidence.certificate.knownPids) &&
    reportedPids.every((pid) => knownPids.includes(pid)) &&
    entries.every((entry) => entry.finiteTerminationEstablished && !entry.finiteHardConflict),
  )
}
// END finite termination projection.

let psSequence = 0
function processTable(pids, argv = false) {
  const startedAtMs = Date.now()
  const observation = {
    sequence: ++psSequence,
    scope: pids ? 'targets' : 'full-table',
    queriedPids: pids ? [...pids] : null,
    executable: '/bin/ps',
    argv: pids
      ? ['-p', pids.join(','), '-o', 'pid=,ppid=,lstart=,stat=,' + (argv ? 'command=' : 'comm=')]
      : ['-axo', 'pid=,ppid=,lstart=,stat=,comm='],
    startedAtMs,
    startedAt: new Date(startedAtMs).toISOString(),
  }
  return new Promise((done, reject) => {
    // Global discovery collects comm only; full argv is limited to established owned PIDs.
    execFile(
      '/bin/ps',
      observation.argv,
      {
        timeout: 2000,
        maxBuffer: 4 * 1024 * 1024,
        encoding: 'buffer',
        env: { ...process.env, LC_ALL: 'C' },
      },
      (error, stdout, stderr) => {
        const endedAtMs = Date.now()
        const raw = Buffer.isBuffer(stdout) ? stdout : Buffer.from(stdout ?? '')
        const errorOutput = Buffer.isBuffer(stderr) ? stderr : Buffer.from(stderr ?? '')
        let text = ''
        let validUtf8 = true
        try {
          text = new TextDecoder('utf-8', { fatal: true }).decode(raw)
        } catch {
          validUtf8 = false
        }
        const parsed = validUtf8
          ? parseProcessRows(text)
          : { rows: new Map(), unparsed: [], parseComplete: false }
        Object.assign(observation, {
          endedAtMs,
          endedAt: new Date(endedAtMs).toISOString(),
          exitCode: error?.code ?? 0,
          signal: error?.signal ?? null,
          timedOut: Boolean(error?.killed),
          truncated: error?.code === 'ERR_CHILD_PROCESS_STDIO_MAXBUFFER',
          validUtf8,
          emptyOutput: text.trim().length === 0,
          stdoutBytes: raw.length,
          stdoutSHA256: createHash('sha256').update(raw).digest('hex'),
          stderrBytes: errorOutput.length,
          stderrSHA256: createHash('sha256').update(errorOutput).digest('hex'),
          runnerAnchorPresent: pids ? null : parsed.rows.has(process.pid),
          parseComplete: parsed.parseComplete,
          rowCount: parsed.rows.size,
          unparsedCount: parsed.unparsed.length,
        })
        const validAbsence =
          pids &&
          error?.code === 1 &&
          !error.killed &&
          !error.signal &&
          validUtf8 &&
          !text.trim() &&
          errorOutput.length === 0
        if (
          (error && !validAbsence) ||
          !parsed.parseComplete ||
          (!pids && !parsed.rows.has(process.pid))
        ) {
          const failure = new Error(
            'ps unavailable or parse incomplete; no absence or signal authorized',
          )
          failure.observation = observation
          failure.unparsed = parsed.unparsed
          failure.rows = parsed.rows
          reject(failure)
        } else done({ ...parsed, observation })
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
  receipt.sampling = {
    byteLimit: logLimit,
    tailLimit: 32,
    transitionLimit: 512,
    tail: [],
    transitions: [],
    diagnosticIncomplete: false,
  }
  receipt.finiteEvidence = {
    inputSourceHash: createHash('sha256').update(JSON.stringify(fingerprints)).digest('hex'),
    hardFailures: [],
    unboundCandidates: [],
    scope: null,
    latestClosure: null,
    certificate: null,
    port: null,
  }
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
      requireCondition(
        ['created', 'spawn', 'exit', 'close', 'error'].includes(event.event),
        'invalid original child event',
      )
      const record = reported.get(event.pid) ?? { pid: event.pid, firstReportedAt: event.at }
      if (record[event.event] || record.close) {
        record.error = {
          at: event.at,
          receivedAtMs: Date.now(),
          message: 'duplicate or post-close lifecycle',
        }
        fail(new Error('original lifecycle repeated; closed PID will not be adopted'))
      } else {
        if (
          record.file &&
          (record.file !== event.file || JSON.stringify(record.argv) !== JSON.stringify(event.argv))
        ) {
          record.error = {
            at: event.at,
            receivedAtMs: Date.now(),
            message: 'original child identity changed',
          }
          fail(new Error('original child identity changed'))
        } else {
          record.file = event.file
          record.argv = event.argv
          record.source = 'main-child-object'
          record[event.event] = {
            at: event.at,
            receivedAtMs: Date.now(),
            ...(event.event === 'exit' || event.event === 'close'
              ? { code: event.code, signal: event.signal }
              : {}),
          }
        }
      }
      reported.set(event.pid, record)
      requireCondition(reported.size <= 64, 'observer child limit exceeded')
      if (known.has(event.pid)) {
        known.get(event.pid).source = 'main-child-object'
        known.get(event.pid).childLifecycle = { ...record }
      }
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

  function lifecycle(entry) {
    return entry.pid === child?.pid
      ? { exit: receipt.mainExit, close: receipt.mainClose, error: receipt.mainError }
      : reported.get(entry.pid)
  }

  function finiteFailure(reason, row = null) {
    const evidence = receipt.finiteEvidence
    if (!evidence.hardFailures.includes(reason)) {
      if (evidence.hardFailures.length >= 128 || (row && Buffer.byteLength(row.rawLine) > 32768)) {
        receipt.sampling.diagnosticIncomplete = true
        fail(new Error('finite evidence capacity incomplete'))
        return
      }
      const candidate = { reason, row, atMs: Date.now() }
      if (
        Buffer.byteLength(
          JSON.stringify({
            ...evidence,
            unboundCandidates: [...evidence.unboundCandidates, candidate],
          }),
        ) > logLimit
      ) {
        receipt.sampling.diagnosticIncomplete = true
        evidence.overflow = { reason, sampleBytesExceeded: true }
        fail(new Error('finite evidence exceeded 4MiB'))
        return
      }
      evidence.hardFailures.push(reason)
      if (row) evidence.unboundCandidates.push(candidate)
      fail(new Error('finite closure hard failure: ' + reason))
    }
  }

  function finiteScope() {
    if (receipt.finiteEvidence.scope) return receipt.finiteEvidence.scope
    const root = known.get(child?.pid)
    const suffix = '/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron'
    if (
      root?.source !== 'direct-spawn' ||
      !root.originalRow.command.startsWith('/') ||
      !root.originalRow.command.endsWith(suffix) ||
      options.executable !== tree + suffix
    )
      return null
    const scope = {
      method:
        'original direct-spawn raw comm minus fixed ASCII executable suffix; LC_ALL=C representation retained',
      source: structuredClone(root.originalRow),
      suffix,
      rawTreePrefix: root.originalRow.command.slice(0, -suffix.length) + '/',
      expectedExecutable: options.executable,
      executableInput: fingerprints.find((value) => value.path === options.executable),
    }
    if (!scope.rawTreePrefix.startsWith('/') || !scope.executableInput) return null
    receipt.finiteEvidence.scope = scope
    return scope
  }

  function finiteClosureRows(table) {
    const scope = finiteScope()
    const ownRows = []
    for (const row of table.rows.values()) {
      const ownPath = Boolean(scope && row.command.startsWith(scope.rawTreePrefix))
      if (ownPath) ownRows.push(row)
      if (!known.has(row.pid) && (known.has(row.ppid) || ownPath))
        finiteFailure('unbound-candidate:' + row.pid + ':' + row.start, row)
    }
    return { scope, ownRows }
  }

  async function finitePortObservation() {
    const startedAtMs = Date.now()
    const match = /^ws:\/\/127\.0\.0\.1:(\d+)\//.exec(receipt.inspectorEndpoint ?? '')
    if (!match)
      return { startedAtMs, endedAtMs: Date.now(), outcome: 'unavailable', endpoint: null }
    return new Promise((done) => {
      let settled = false
      const socket = connect({ host: '127.0.0.1', port: Number(match[1]) })
      const finish = (outcome, code = null) => {
        if (settled) return
        settled = true
        socket.destroy()
        done({
          startedAtMs,
          endedAtMs: Date.now(),
          outcome,
          code,
          endpoint: receipt.inspectorEndpoint,
          statement:
            'auxiliary original inspector endpoint observation; never substitutes for PID closure',
        })
      }
      socket.setTimeout(200, () => finish('unknown', 'timeout'))
      socket.once('connect', () => finish('open'))
      socket.once('error', (error) =>
        finish(error.code === 'ECONNREFUSED' ? 'refused' : 'unknown', error.code),
      )
    })
  }

  async function tryFiniteClosure(table) {
    const evidence = receipt.finiteEvidence
    const { scope, ownRows } = finiteClosureRows(table)
    if (!mainClosed) return
    const unbound = [...reported.keys()].filter((pid) => !known.has(pid))
    const mainNatural = originalClose({
      exit: receipt.mainExit,
      close: receipt.mainClose,
      error: receipt.mainError,
    })
    const latestClosure = {
      fullTable: table.observation,
      inputSourceHash: evidence.inputSourceHash,
      reportedPids: [...reported.keys()],
      reportedUnbound: unbound,
      ownExecutableRows: ownRows,
      scopeEstablished: Boolean(scope),
      originalMainClosedNaturally: mainNatural,
    }
    const closureBytes = JSON.stringify({ ...evidence, latestClosure })
    if (Buffer.byteLength(closureBytes) > logLimit) {
      receipt.sampling.diagnosticIncomplete = true
      evidence.overflow = {
        bytes: Buffer.byteLength(closureBytes),
        sha256: createHash('sha256').update(closureBytes).digest('hex'),
      }
      finiteFailure('closure-capacity-exceeded')
      return
    }
    evidence.latestClosure = latestClosure
    if (unbound.length) for (const pid of unbound) finiteFailure('reported-unbound:' + pid)
    if (!scope) finiteFailure('own-executable-display-scope-unavailable')
    if (
      !validFiniteSample(table.observation, 'full-table') ||
      !mainNatural ||
      receipt.sampling.diagnosticIncomplete ||
      evidence.hardFailures.length ||
      ownRows.length ||
      [...known.values()].some((entry) => table.rows.has(entry.pid) || entry.finiteHardConflict)
    )
      return
    if (finiteRunClosed([...known.values()], [...reported.keys()], receipt.sampling, evidence))
      return
    const knownPids = [...known.keys()].sort((a, b) => a - b)
    const checked = await tableFor(knownPids, false, 'finite-known-pids')
    recordSampling(checked, 'finite-known-pids', new Set(knownPids))
    if (
      !validFiniteSample(checked.observation, 'targets') ||
      checked.rows.size ||
      evidence.hardFailures.length
    )
      return
    evidence.port = await finitePortObservation()
    const issuedAtMs = Date.now()
    const certificate = structuredClone({
      complete: true,
      issuedAtMs,
      inputSourceHash: evidence.inputSourceHash,
      fullTable: table.observation,
      knownPidCheck: checked.observation,
      knownPids,
      reportedPids: [...reported.keys()],
      reportedUnbound: [...reported.keys()].filter((pid) => !known.has(pid)),
      unboundCandidates: evidence.unboundCandidates,
      ownExecutableRows: ownRows,
      scopeEstablished: Boolean(scope),
      scope,
      originalMainClosedNaturally: mainNatural,
      port: evidence.port,
      statement:
        'finite observations of this run established-owned PIDs and explicit closure scope; no continuous identity or all-time/global escape guarantee',
    })
    for (const entry of known.values())
      Object.assign(entry, projectFiniteTermination(entry, certificate, issuedAtMs))
    if ([...known.values()].every((entry) => entry.finiteTerminationEstablished))
      evidence.certificate = certificate
  }

  function recordSampling(table, purpose, targets, transitions = []) {
    for (const entry of known.values()) {
      const row = table.rows.get(entry.pid)
      if (!row) continue
      const next = finiteObservation(
        entry,
        row,
        table.observation,
        entry.finiteLifecycleSnapshot,
        Date.now(),
        purpose === 'owned-argv',
      )
      Object.assign(entry, next)
      if (next.finiteHardConflict) finiteFailure('pid:' + entry.pid + ':' + next.finiteHardConflict)
    }
    const sampling = receipt.sampling
    const record = {
      ...table.observation,
      inputSourceHash: receipt.finiteEvidence.inputSourceHash,
      purpose,
      targets: [...targets].map((pid) => ({
        pid,
        row: table.rows.get(pid) ?? null,
        ...(known.has(pid) ? { classification: known.get(pid).classification } : {}),
      })),
    }
    const tail = [...sampling.tail, record].slice(-sampling.tailLimit)
    const history = [...sampling.transitions, ...transitions]
    const encoded = JSON.stringify({ tail, transitions: history })
    if (
      history.length > sampling.transitionLimit ||
      Buffer.byteLength(encoded) > sampling.byteLimit
    ) {
      sampling.diagnosticIncomplete = true
      sampling.overflow = {
        sequence: table.observation.sequence,
        purpose,
        bytes: Buffer.byteLength(encoded),
        sha256: createHash('sha256').update(encoded).digest('hex'),
      }
      for (const entry of known.values()) {
        entry.diagnosticIncomplete = true
        entry.signalEligible = false
      }
      fail(new Error('process diagnostic capacity exceeded; no signal or success authorized'))
      return
    }
    sampling.tail = tail
    sampling.transitions = history
  }

  async function tableFor(pids, argv, purpose) {
    try {
      return await processTable(pids, argv)
    } catch (error) {
      receipt.sampling.diagnosticIncomplete = true
      for (const entry of known.values()) {
        entry.diagnosticIncomplete = true
        entry.signalEligible = false
      }
      if (error.observation) {
        const targets = new Set([...known.keys(), process.pid])
        const unparsed = (error.unparsed ?? []).map((line) =>
          targets.has(line.pid)
            ? line
            : {
                pid: line.pid,
                bytes: Buffer.byteLength(line.rawLine),
                sha256: createHash('sha256').update(line.rawLine).digest('hex'),
              },
        )
        receipt.sampling.psFailure = {
          ...error.observation,
          inputSourceHash: receipt.finiteEvidence.inputSourceHash,
          purpose,
          unparsed: unparsed.slice(0, 64),
          targets: [...targets].map((pid) => ({ pid, row: error.rows?.get(pid) ?? null })),
        }
      }
      persist()
      throw error
    }
  }

  function updateEntry(entry, row, observation) {
    if (row && Buffer.byteLength(row.rawLine) > 32768) entry.diagnosticIncomplete = true
    const consumedAtMs = Date.now()
    const lifecycleSnapshot = structuredClone(lifecycle(entry) ?? null)
    const state = classifyProcess(entry, row, observation, lifecycleSnapshot, consumedAtMs)
    const finiteState = finiteObservation(
      { ...entry, ...state },
      row,
      observation,
      lifecycleSnapshot,
      consumedAtMs,
    )
    const previous = entry.classification
    Object.assign(entry, state, finiteState, {
      finiteLifecycleSnapshot: lifecycleSnapshot,
      lastCheckedAt: observation.endedAt,
      lastObservation: observation.sequence,
      classification: state,
    })
    // Sampling timestamps advance while an unchanged process stays present;
    // keep those in the bounded tail, not as a new identity transition.
    const transitionState = (value) => value && { ...value, lastPresentEndedMs: null }
    const changed =
      !previous ||
      JSON.stringify(transitionState(previous)) !== JSON.stringify(transitionState(state)) ||
      entry.lastRow?.start !== row?.start ||
      entry.lastRow?.stat !== row?.stat ||
      entry.lastRow?.command !== row?.command
    entry.lastRow = row ?? null
    if (finiteState.finiteHardConflict)
      fail(
        new Error(
          'finite accounting hard conflict: ' + entry.pid + '/' + finiteState.finiteHardConflict,
        ),
      )
    const timelyCertificate =
      entry.finiteTerminationEstablished &&
      finiteRunClosed(
        [...known.values()],
        [...reported.keys()],
        receipt.sampling,
        receipt.finiteEvidence,
      )
    if (
      state.failureReason &&
      !(state.failureReason === 'quarantine-unresolved' && timelyCertificate)
    )
      fail(new Error('owned process accounting failed: ' + entry.pid + '/' + state.failureReason))
    return changed
      ? {
          sequence: observation.sequence,
          original: entry.originalRow,
          observed: row ?? null,
          sampleStartedAtMs: observation.startedAtMs,
          sampleEndedAtMs: observation.endedAtMs,
          classifiedAtMs: consumedAtMs,
          consumedAtMs,
          lifecycle: lifecycleSnapshot,
          classification: state,
        }
      : null
  }

  async function sample(purpose = 'inventory') {
    const table = await tableFor(undefined, false, purpose)
    const { rows, observation } = table
    const root = child?.pid
    if (!receipt.runner.identity) receipt.runner.identity = rows.get(process.pid)
    const transitions = []
    // Classify existing identities before using any of them as ancestry roots.
    for (const entry of known.values()) {
      const changed = updateEntry(entry, rows.get(entry.pid), observation)
      if (changed) transitions.push(changed)
    }
    const ownedNow = new Set()
    const originalRoot = known.get(root)
    if (
      root &&
      !mainClosed &&
      !receipt.mainExit &&
      rows.has(root) &&
      (!originalRoot || originalRoot.signalEligible)
    ) {
      requireCondition(
        Date.parse(rows.get(root).start) <= receipt.launch.spawnRequestedAtMs + 1000,
        'direct child birth is newer than its original spawn; ownership unavailable',
      )
      ownedNow.add(root)
    }
    for (const entry of known.values()) {
      const current = rows.get(entry.pid)
      if (
        entry.resolvedTerminal ||
        lifecycle(entry)?.close ||
        lifecycle(entry)?.exit ||
        entry.quarantine ||
        entry.birthMismatch ||
        entry.diagnosticIncomplete ||
        current?.stat.startsWith('Z')
      )
        continue
      if (current?.start === entry.start && current.command === entry.command)
        ownedNow.add(entry.pid)
    }
    for (let depth = 0; depth < 32; depth++) {
      let changed = false
      for (const row of rows.values()) {
        const existing = known.get(row.pid)
        // A closed lifecycle is still classified below, but is never re-adopted
        // from ancestry, metrics or a repeated display of its PID.
        if (
          existing &&
          (lifecycle(existing)?.close ||
            lifecycle(existing)?.exit ||
            existing.resolvedTerminal ||
            existing.quarantine ||
            existing.birthMismatch)
        )
          continue
        if (reported.get(row.pid)?.close || rows.get(row.ppid)?.stat.startsWith('Z')) continue
        if (ownedNow.has(row.ppid) && !ownedNow.has(row.pid)) {
          ownedNow.add(row.pid)
          changed = true
        }
      }
      if (!changed) break
      requireCondition(depth !== 31, 'process ancestry exceeded 32 levels')
    }
    for (const entry of reported.values()) {
      const current = rows.get(entry.pid)
      if (!current || entry.exit || entry.close || known.has(entry.pid) || !entry.created) continue
      requireCondition(
        Date.parse(current.start) <= Date.parse(entry.created.at) + 1000,
        'reported PID birth is newer than original child creation; ownership unavailable',
      )
      // Original child-object provenance can survive OS reparenting. Metrics
      // without an established parent/birth are never enough to adopt an orphan.
      if (entry.source === 'main-child-object') ownedNow.add(entry.pid)
    }
    const discovered = []
    for (const pid of ownedNow) {
      if (known.has(pid)) continue
      const row = rows.get(pid)
      requireCondition(known.size < 256, 'owned PID limit exceeded')
      requireCondition(
        Buffer.byteLength(row.rawLine) <= 32768,
        'owned ps row exceeded diagnostic bound',
      )
      const parent = known.get(row.ppid) ?? rows.get(row.ppid)
      const originalChild = reported.get(pid)?.source === 'main-child-object'
      const source =
        pid === root ? 'direct-spawn' : originalChild ? 'main-child-object' : 'ancestry'
      requireCondition(
        pid === root || originalChild || (parent && ownedNow.has(row.ppid)),
        'helper original parent/birth unavailable',
      )
      known.set(pid, {
        ...row,
        originalRow: { ...row },
        firstSeenAt: observation.endedAt,
        firstSeenAtMs: observation.endedAtMs,
        source,
        ownershipEstablished: true,
        parentIdentity: parent ? { pid: parent.pid, start: parent.start } : null,
        ...(reported.has(pid) ? { childLifecycle: { ...reported.get(pid) } } : {}),
      })
      discovered.push(pid)
    }
    for (const pid of discovered) {
      const changed = updateEntry(known.get(pid), rows.get(pid), observation)
      if (changed) transitions.push(changed)
    }
    recordSampling(table, purpose, new Set([...known.keys(), process.pid]), transitions)
    persist()
    if (discovered.length) {
      const details = await tableFor(discovered, true, 'owned-argv')
      for (const pid of discovered) {
        const entry = known.get(pid)
        const detail = details.rows.get(pid)
        if (detail?.start === entry.start) {
          requireCondition(
            Buffer.byteLength(detail.command) <= 65536,
            'owned argv exceeded diagnostic bound',
          )
          entry.observedArgv = detail.command
        } else {
          entry.argvObservation = 'absent or birth changed before targeted argv; not reconstructed'
          if (detail) {
            entry.birthMismatch = true
            entry.signalEligible = false
            entry.classification = {
              ...entry.classification,
              birthMismatch: true,
              signalEligible: false,
              failureReason: 'birth-conflict',
            }
            entry.argvBirthConflict = {
              original: entry.originalRow,
              observed: detail,
              observation: details.observation,
            }
            fail(new Error('owned process birth changed during targeted argv observation: ' + pid))
          }
        }
      }
      recordSampling(details, 'owned-argv', new Set(discovered))
      persist()
    }
    await tryFiniteClosure(table)
    persist()
    return table
  }

  function allProcessesAbsent() {
    return finiteRunClosed(
      [...known.values()],
      [...reported.keys()],
      receipt.sampling,
      receipt.finiteEvidence,
    )
  }

  async function cleanup() {
    const until = cleanupDeadline - 5000
    receipt.cleanupStartedAt = new Date().toISOString()
    await sample('cleanup-initial')
    const naturalUntil = Math.min(until, Date.now() + processQuarantineMs + 250)
    while (Date.now() < naturalUntil && (!allProcessesAbsent() || !mainClosed)) {
      await delay(100)
      await sample('natural-terminal-wait')
    }
    receipt.naturalTrackedProcessesAbsent = mainClosed && allProcessesAbsent()
    // Signals are only a last-resort test cleanup. Every attempt remains an
    // overall failure; quarantined/closed/unknown identities are never targeted.
    for (const signal of ['SIGTERM', 'SIGKILL']) {
      if (allProcessesAbsent() && mainClosed) break
      const entries = [...known.values()].sort((a, b) =>
        a.pid === child?.pid ? 1 : b.pid === child?.pid ? -1 : 0,
      )
      for (const entry of entries) {
        if (Date.now() >= until) break
        if (!entry.signalEligible || receipt.sampling.diagnosticIncomplete) continue
        const table = await tableFor([entry.pid], false, 'pre-signal')
        const changed = updateEntry(entry, table.rows.get(entry.pid), table.observation)
        recordSampling(table, 'pre-signal', new Set([entry.pid]), changed ? [changed] : [])
        persist()
        if (Date.now() >= until || !entry.signalEligible || receipt.sampling.diagnosticIncomplete) {
          receipt.cleanup.push({ pid: entry.pid, signal, skipped: 'fresh identity not eligible' })
          continue
        }
        receipt.testCleanupSignalled = true
        fail(
          new Error('test cleanup signal attempted; natural product termination not established'),
        )
        try {
          process.kill(entry.pid, signal)
          receipt.cleanup.push({
            pid: entry.pid,
            signal,
            at: new Date().toISOString(),
            sampleSequence: table.observation.sequence,
          })
        } catch (error) {
          receipt.cleanup.push({ pid: entry.pid, signal, error: String(error) })
        }
      }
      const waitUntil = Math.min(until, Date.now() + (signal === 'SIGTERM' ? 3000 : 5000))
      while (Date.now() < waitUntil) {
        await delay(100)
        await sample('post-signal')
        if (allProcessesAbsent() && mainClosed) break
      }
    }
    await sample('cleanup-final')
    receipt.cleanupFinishedAt = new Date().toISOString()
    receipt.trackedProcessesAbsent = allProcessesAbsent()
    receipt.mainCloseObserved = mainClosed
    requireCondition(mainClosed, 'direct Electron child close was not observed')
    requireCondition(
      receipt.trackedProcessesAbsent,
      'tracked process accounting unresolved; preserve run root',
    )
    requireCondition(
      receipt.naturalTrackedProcessesAbsent && !receipt.testCleanupSignalled,
      'natural product termination incomplete; test cleanup is not product success',
    )
  }

  function collectObserverEvidence() {
    const path = join(evidenceRoot, 'observer.json')
    try {
      requireCondition(statSync(path).size <= logLimit, 'observer evidence exceeded 4MiB')
      const observer = JSON.parse(readFileSync(path, 'utf8'))
      const projection = observerProjection(
        observer,
        receipt.runId,
        receipt.mainExit,
        receipt.mainClose,
      )
      Object.assign(receipt, projection)
      receipt.observerEvidence = { outcome: 'available', collectedAt: new Date().toISOString() }
      if (observerResult && observerResult.outcome !== observer.outcome)
        throw new Error('observer stream/file terminal mismatch')
      requireCondition(observer.outcome === 'succeeded', 'missing successful observer recovery')
      requireCondition(
        observer.inspectorClosedBeforeFaults === true,
        'main inspector not proven closed',
      )
      requireCondition(
        projection.naturalEngineChildClosesObserved,
        'original engine exit/close0 missing',
      )
      requireCondition(observer.windows.length === 3, 'expected three real window generations')
    } catch (error) {
      receipt.observerEvidence = {
        outcome: 'unavailable-or-invalid',
        error: String(error),
        collectedAt: new Date().toISOString(),
      }
      receipt.recoveryOutcome ??= 'unavailable'
      const records = [...reported.values()].filter((entry) => entry.source === 'main-child-object')
      receipt.childLifecycleOutcome ??= {
        outcome: records.length > 0 && records.every(originalClose) ? 'succeeded' : 'incomplete',
        source: 'observer-stream',
        records,
      }
      fail(error)
    }
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
    receipt.launch.spawnRequestedAtMs = Date.now()
    child = spawn(options.executable, args, {
      cwd: options.app,
      env,
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    receipt.launch.pid = child.pid
    child.stdout.on('data', (chunk) => log('stdout', chunk))
    child.stderr.on('data', (chunk) => log('stderr', chunk))
    child.on('error', (error) => {
      receipt.mainError = {
        at: new Date().toISOString(),
        receivedAtMs: Date.now(),
        message: String(error),
      }
      fail(error)
    })
    child.on('exit', (code, signal) => {
      receipt.mainExit = { code, signal, at: new Date().toISOString(), receivedAtMs: Date.now() }
    })
    const closed = new Promise((done) =>
      child.on('close', (code, signal) => {
        mainClosed = true
        mainExit = { code, signal, at: new Date().toISOString(), receivedAtMs: Date.now() }
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
    collectObserverEvidence()
    receipt.machineOutcome = 'succeeded'
  } catch (error) {
    fail(error)
    receipt.machineOutcome = 'failed'
  } finally {
    cleanupDeadline = Date.now() + cleanupMs
    receipt.cleanupBudgetStartedAt = new Date().toISOString()
    clearTimeout(runtimeTimer)
    try {
      socket?.close()
    } catch (error) {
      fail(error)
    }
    polling = false
    try {
      if (monitor) await monitor
    } catch (error) {
      fail(error)
    }
    try {
      if (child) await cleanup()
    } catch (error) {
      fail(error)
      receipt.machineOutcome = 'failed'
    }
    // Independent recovery evidence must survive any earlier failure Promise.
    collectObserverEvidence()
    receipt.mainLifecycleOutcome = {
      outcome: originalClose({
        exit: receipt.mainExit,
        close: receipt.mainClose,
        error: receipt.mainError,
      })
        ? 'succeeded'
        : 'incomplete',
      exit: receipt.mainExit ?? null,
      close: receipt.mainClose ?? null,
      error: receipt.mainError ?? null,
    }
    receipt.processAccountingOutcome =
      allProcessesAbsent() &&
      receipt.mainLifecycleOutcome.outcome === 'succeeded' &&
      !receipt.testCleanupSignalled
        ? 'succeeded'
        : 'failed'
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
    receipt.overallOutcome = receipt.machineOutcome
    receipt.firstFailure = firstFailure ? String(firstFailure.stack ?? firstFailure) : null
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
