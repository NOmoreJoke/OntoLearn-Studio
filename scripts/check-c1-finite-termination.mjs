// Proposal only. Extracts actual source functions; never imports or starts native CLI.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import vm from 'node:vm'
const path = process.argv[2]
assert(path && process.argv.length === 3, 'pass one proposed/applied driver source path')
const source = readFileSync(path, 'utf8')
const extract = (start, end) => {
  const a = source.indexOf(start),
    b = source.indexOf(end, a)
  assert(a >= 0 && b > a, start)
  return source.slice(a, b)
}
const legacy = extract(
  '// BEGIN pure process-accounting classifier',
  '// END pure process-accounting classifier.',
)
const finite = extract(
  '// BEGIN finite termination projection',
  '// END finite termination projection.',
)
const update = extract('  function updateEntry(', '  async function sample(')
const actual = vm.runInNewContext(
  legacy +
    '\n' +
    finite +
    '\n;({classifyProcess,finiteObservation,validFiniteSample,projectFiniteTermination,completeFiniteClosure,finiteRunClosed})',
  { structuredClone, Buffer, Date },
)
const results = []
async function check(name, run) {
  try {
    await run()
    results.push({ name, outcome: 'passed' })
  } catch (error) {
    results.push({ name, outcome: 'failed', error: String(error.stack) })
  }
}
const hash = '1'.repeat(64),
  birth = 'Fri Oct 23 01:54:47 2026'
const full = () => ({
  sequence: 10,
  scope: 'full-table',
  queriedPids: null,
  startedAtMs: 300,
  endedAtMs: 310,
  exitCode: 0,
  signal: null,
  timedOut: false,
  truncated: false,
  parseComplete: true,
  validUtf8: true,
  stdoutSHA256: hash,
  stdoutBytes: 20,
  stderrBytes: 0,
  emptyOutput: false,
  rowCount: 1,
  runnerAnchorPresent: true,
})
const target = (pids = [42, 43, 44]) => ({
  ...full(),
  sequence: 11,
  scope: 'targets',
  queriedPids: pids,
  startedAtMs: 310,
  endedAtMs: 320,
  exitCode: 1,
  emptyOutput: true,
  stdoutBytes: 0,
  rowCount: 0,
  runnerAnchorPresent: null,
})
const proof = () => ({
  complete: true,
  inputSourceHash: 'a'.repeat(64),
  knownPids: [42, 43, 44],
  reportedPids: [42, 43, 44],
  reportedUnbound: [],
  unboundCandidates: [],
  ownExecutableRows: [],
  scopeEstablished: true,
  originalMainClosedNaturally: true,
  port: { outcome: 'refused' },
  fullTable: full(),
  knownPidCheck: target(),
})
const close = () => ({
  exit: { code: 0, signal: null, receivedAtMs: 125 },
  close: { code: 0, signal: null, receivedAtMs: 130 },
})
const raw = (pid = 42) => ({
  pid,
  ppid: 12,
  start: birth,
  stat: 'S',
  command: '/owned/exe',
  rawLine: pid + ' 12 ' + birth + ' S /owned/exe',
})
const entry = (pid = 42, source = 'ancestry') => ({
  ...raw(pid),
  originalRow: raw(pid),
  source,
  ownershipEstablished: true,
  firstSeenAtMs: 10,
  lastPresentEndedMs: 20,
})
function observe(item, row, observation, life, at) {
  const state = actual.classifyProcess(item, row, observation, life, at)
  const projection = actual.finiteObservation({ ...item, ...state }, row, observation, life, at)
  Object.assign(item, state, projection, { finiteLifecycleSnapshot: structuredClone(life ?? null) })
  return item
}
function unknown(pid = 42, kind = 'ancestry') {
  const item = entry(pid, kind),
    life = kind === 'ancestry' ? undefined : close()
  observe(
    item,
    { ...raw(pid), command: '(opaque)', stat: 'S' },
    { ...full(), sequence: 7, startedAtMs: 100, endedAtMs: 120 },
    life,
    140,
  )
  observe(item, undefined, full(), life, 330)
  return item
}
function certified() {
  return [unknown(42, 'direct-spawn'), unknown(43), unknown(44)].map((item) =>
    Object.assign(item, actual.projectFiniteTermination(item, proof(), 350)),
  )
}
await check(
  '650 classifier remains exact and its unknown/helper resolvedTerminal stays false',
  () => {
    assert.equal(
      createHash('sha256').update(legacy).digest('hex'),
      '68238542607e8992a4b58f38fa1b2c82a58bb3bbbbd874fff1de435dfb104c89',
    )
    const entries = certified()
    for (const item of entries) {
      assert.equal(item.resolvedTerminal, false)
      assert.equal(item.historicalUnknown, true)
      assert.equal(item.finiteTerminationEstablished, true)
      assert.equal(item.signalEligible, false)
    }
    assert.equal(entries[0].originalClosedNaturally, true)
    assert.equal(entries[1].originalClosedNaturally, null)
    assert.match(entries[1].finiteCertificate.statement, /independent exit code not observed/)
  },
)
await check(
  'complete scope closes; extra reported74183 blocks despite three valid known certificates',
  () => {
    const entries = certified(),
      evidence = { certificate: proof(), hardFailures: [] }
    assert.equal(
      actual.finiteRunClosed(entries, [42, 43, 44], { diagnosticIncomplete: false }, evidence),
      true,
    )
    assert.equal(
      actual.finiteRunClosed(
        entries,
        [42, 43, 44, 74183],
        { diagnosticIncomplete: false },
        evidence,
      ),
      false,
    )
  },
)
await check(
  'full valid later sample and target coverage required; malformed/empty/error cannot prove absence',
  () => {
    for (const patch of [
      { parseComplete: false },
      { timedOut: true },
      { truncated: true },
      { validUtf8: false },
      { runnerAnchorPresent: false },
      { stdoutSHA256: '' },
      { exitCode: 1 },
      { signal: 'SIGTERM' },
      { endedAtMs: 299 },
    ]) {
      const p = proof()
      Object.assign(p.fullTable, patch)
      assert.equal(actual.completeFiniteClosure(p), false)
    }
    for (const patch of [
      { exitCode: 2 },
      { stderrBytes: 1 },
      { queriedPids: [42] },
      { emptyOutput: false },
      { rowCount: 1 },
      { sequence: 10 },
    ]) {
      const p = proof()
      Object.assign(p.knownPidCheck, patch)
      assert.equal(actual.completeFiniteClosure(p), false)
    }
  },
)
await check(
  'cross-close old snapshot never qualifies; both start and present interval matter',
  () => {
    for (const startedAtMs of [100, 120, 130]) {
      const item = unknown(42, 'direct-spawn'),
        p = proof()
      p.fullTable.startedAtMs = startedAtMs
      assert.equal(
        actual.projectFiniteTermination(item, p, 350).finiteTerminationEstablished,
        false,
      )
    }
  },
)
await check('helper still present or only parent close cannot establish own absence', () => {
  const item = entry(43)
  observe(item, raw(43), full(), undefined, 330)
  assert.equal(
    actual.projectFiniteTermination(item, proof(), 350).finiteTerminationEstablished,
    false,
  )
  assert.equal(item.originalClosedNaturally, null)
})
await check('missing/nonzero/signal/error/duplicate lifecycle remains hard failure', () => {
  const cases = [
    undefined,
    { exit: close().exit },
    { ...close(), close: { ...close().close, code: 1 } },
    { ...close(), exit: { ...close().exit, signal: 'SIGTERM', code: null } },
    { ...close(), error: { message: 'duplicate or post-close' } },
    { exit: { ...close().exit, receivedAtMs: 150 }, close: close().close },
  ]
  for (const life of cases) {
    const item = entry(42, 'main-child-object')
    observe(item, undefined, full(), life, 330)
    assert.equal(
      actual.projectFiniteTermination(item, proof(), 350).finiteTerminationEstablished,
      false,
    )
  }
})
await check(
  'birth, full executable, argv birth and certified-row reappearance are permanent hard conflicts',
  () => {
    const variants = [
      { row: { ...raw(), start: 'Fri Oct 23 01:54:48 2026' } },
      { row: { ...raw(), command: '/other/exe' } },
      { argvBirthConflict: { observed: { start: 'other' } } },
      { finiteTerminationEstablished: true, row: raw() },
    ]
    for (const variant of variants) {
      const item = entry()
      Object.assign(item, variant)
      observe(item, variant.row ?? raw(), full(), undefined, 330)
      observe(item, undefined, { ...full(), startedAtMs: 400, endedAtMs: 410 }, undefined, 430)
      assert(item.finiteHardConflict)
      assert.equal(
        actual.projectFiniteTermination(item, proof(), 450).finiteTerminationEstablished,
        false,
      )
      assert.equal(item.signalEligible, false)
    }
  },
)
await check(
  'unbound candidate, own executable residue, incomplete scope and overflow reject',
  () => {
    for (const patch of [
      { reportedUnbound: [74183] },
      { unboundCandidates: [{ pid: 90 }] },
      { ownExecutableRows: [raw(42)] },
      { scopeEstablished: false },
    ]) {
      const p = { ...proof(), ...patch }
      assert.equal(
        actual.projectFiniteTermination(unknown(), p, 350).finiteTerminationEstablished,
        false,
      )
    }
    assert.equal(
      actual.finiteRunClosed(
        certified(),
        [42, 43, 44],
        { diagnosticIncomplete: true },
        { certificate: proof(), hardFailures: [] },
      ),
      false,
    )
    assert.equal(
      actual.finiteRunClosed(
        certified(),
        [42, 43, 44],
        { diagnosticIncomplete: false },
        { certificate: proof(), hardFailures: ['candidate'] },
      ),
      false,
    )
  },
)
await check('port refusal alone and old post-settled summary cannot substitute for samples', () => {
  assert.equal(actual.completeFiniteClosure({ port: { outcome: 'refused' } }), false)
  const p = proof()
  p.knownPidCheck.stdoutSHA256 = ''
  assert.equal(actual.completeFiniteClosure(p), false)
})
await check(
  'late proof cannot newly qualify after2s; already timely facts retain historic unknown',
  () => {
    const item = unknown()
    assert.equal(
      actual.projectFiniteTermination(item, proof(), 2140).finiteTerminationEstablished,
      false,
    )
    const done = certified()[1]
    assert.equal(
      actual.projectFiniteTermination(done, proof(), 5000).finiteTerminationEstablished,
      true,
    )
    assert.equal(done.historicalUnknown, true)
  },
)
await check(
  'actual update suppresses only new quarantine error with whole timely closure, not missing reported',
  () => {
    for (const missing of [false, true]) {
      const entries = certified(),
        known = new Map(entries.map((x) => [x.pid, x])),
        reported = new Map([42, 43, 44, ...(missing ? [74183] : [])].map((pid) => [pid, {}])),
        failures = []
      const result = vm.runInNewContext(legacy + '\n' + finite + '\n' + update + '\n;updateEntry', {
        Buffer,
        structuredClone,
        Date: { now: () => 3000, parse: Date.parse },
        known,
        reported,
        receipt: {
          sampling: { diagnosticIncomplete: false },
          finiteEvidence: { certificate: proof(), hardFailures: [] },
        },
        lifecycle: () => undefined,
        fail: (e) => failures.push(String(e)),
      })
      const transition = result(entries[1], undefined, {
        ...full(),
        sequence: 20,
        startedAtMs: 2800,
        endedAtMs: 2900,
      })
      assert.equal(transition.classification.failureReason, 'quarantine-unresolved')
      assert.equal(failures.length, missing ? 1 : 0)
    }
  },
)
await check('actual fail keeps firstFailure; no terminal projection clears it', () => {
  const failSource = extract('  const fail = (error) => {', '  const onSignal =')
  const context = {
    receipt: { failures: [] },
    firstFailure: new Error('original first'),
    failRun: () => {
      throw new Error('must not reset')
    },
    Date,
    Error,
  }
  vm.runInNewContext(failSource + '\nfail(new Error("later quarantine"));', context)
  assert.equal(context.firstFailure.message, 'original first')
  assert.equal(context.receipt.failures.length, 1)
})
await check(
  'raw LC_ALL=C scope derives only from original direct spawn; unbound child discovery does not adopt',
  () => {
    const scopeSource = extract(
      '  function finiteScope()',
      '  async function finitePortObservation()',
    )
    const suffix = '/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron',
      rawPrefix = '/Users/\\M-raw/tree/',
      unicodeTree = '/Users/真实/tree'
    const root = {
      ...entry(42, 'direct-spawn'),
      originalRow: { ...raw(), command: rawPrefix.slice(0, -1) + suffix },
    }
    const known = new Map([[42, root]]),
      failures = []
    const get = vm.runInNewContext(scopeSource + '\n;({finiteScope,finiteClosureRows})', {
      known,
      child: { pid: 42 },
      tree: unicodeTree,
      options: { executable: unicodeTree + suffix },
      fingerprints: [{ path: unicodeTree + suffix, sha256: hash }],
      receipt: { finiteEvidence: { scope: null } },
      structuredClone,
      finiteFailure: (reason, row) => failures.push({ reason, row }),
    })
    assert.equal(get.finiteScope().rawTreePrefix, rawPrefix)
    get.finiteClosureRows({
      rows: new Map([
        [90, { ...raw(90), ppid: 42, command: '(opaque candidate)' }],
        [91, { ...raw(91), ppid: 1, command: rawPrefix + 'helper' }],
      ]),
    })
    assert.equal(failures.length, 2)
    assert.equal(known.size, 1)
  },
)
await check(
  'actual processTable metadata hashes exact buffers, rejects malformed/permission empty exit1',
  async () => {
    const tableSource = extract('let psSequence = 0', 'async function run(options)')
    for (const kind of ['ok', 'absent', 'permission', 'invalid-utf8', 'timeout', 'truncated']) {
      const stdout =
        kind === 'ok'
          ? Buffer.from('42 12 ' + birth + ' S /owned/exe\n')
          : kind === 'invalid-utf8'
            ? Buffer.from([255])
            : Buffer.alloc(0)
      const error =
        kind === 'absent' || kind === 'permission'
          ? { code: 1 }
          : kind === 'timeout'
            ? { code: null, killed: true, signal: 'SIGTERM' }
            : kind === 'truncated'
              ? { code: 'ERR_CHILD_PROCESS_STDIO_MAXBUFFER' }
              : null
      const table = vm.runInNewContext(legacy + '\n' + tableSource + '\n;processTable', {
        Buffer,
        TextDecoder,
        createHash,
        Date,
        process: { pid: 42, env: {} },
        execFile: (_file, _args, _limits, callback) =>
          callback(error, stdout, kind === 'permission' ? Buffer.from('denied') : Buffer.alloc(0)),
      })
      if (kind === 'ok') {
        const got = await table()
        assert.equal(
          got.observation.stdoutSHA256,
          createHash('sha256').update(stdout).digest('hex'),
        )
        assert.equal(got.observation.runnerAnchorPresent, true)
      } else if (kind === 'absent') {
        const got = await table([42])
        assert.equal(got.observation.emptyOutput, true)
        assert.equal(got.observation.stderrBytes, 0)
      } else await assert.rejects(table([42]), /ps unavailable/)
    }
  },
)
await check(
  'actual cleanup signal remains overall failure; terminal facts cannot wash first failure',
  async () => {
    const cleanupSource = extract(
      '  async function cleanup()',
      '  function collectObserverEvidence()',
    )
    let clock = 1000,
      absent = false,
      firstFailure = new Error('original first'),
      signals = 0
    const failures = [],
      receipt = { cleanup: [], sampling: { diagnosticIncomplete: false } },
      item = { pid: 42, signalEligible: true }
    const FakeDate = function () {
      return new Date(clock)
    }
    FakeDate.now = () => clock
    const cleanup = vm.runInNewContext(cleanupSource + '\n;cleanup', {
      Date: FakeDate,
      cleanupDeadline: 301000,
      processQuarantineMs: 2000,
      mainClosed: true,
      receipt,
      known: new Map([[42, item]]),
      child: { pid: 12 },
      allProcessesAbsent: () => absent,
      sample: async () => {},
      delay: async (ms) => {
        clock += ms
      },
      tableFor: async () => ({ rows: new Map([[42, raw()]]), observation: full() }),
      updateEntry: () => null,
      recordSampling: () => {},
      persist: () => {},
      requireCondition: (value, message) => assert(value, message),
      fail: (error) => {
        failures.push(String(error))
        firstFailure ??= error
      },
      process: {
        kill: () => {
          signals++
          absent = true
        },
      },
    })
    await assert.rejects(cleanup(), /natural product termination incomplete/)
    assert.equal(signals, 1)
    assert.equal(receipt.testCleanupSignalled, true)
    assert.match(failures[0], /test cleanup signal attempted/)
    assert.equal(firstFailure.message, 'original first')
  },
)
await check(
  'actual finite evidence overflow rejects rather than dropping candidate silently',
  () => {
    const failureSource = extract('  function finiteFailure(', '  function finiteScope()')
    const receipt = {
        sampling: { diagnosticIncomplete: false },
        finiteEvidence: { hardFailures: [], unboundCandidates: [] },
      },
      failures = []
    const fail = vm.runInNewContext(failureSource + '\n;finiteFailure', {
      receipt,
      Buffer,
      Date,
      logLimit: 8,
      fail: (e) => failures.push(String(e)),
    })
    fail('candidate:99', raw(99))
    assert.equal(receipt.sampling.diagnosticIncomplete, true)
    assert.equal(receipt.finiteEvidence.unboundCandidates.length, 0)
    assert(failures.length > 0)
  },
)
console.log(
  JSON.stringify(
    { source: path, sourceSHA256: createHash('sha256').update(source).digest('hex'), results },
    null,
    2,
  ),
)
process.exitCode = results.some((x) => x.outcome === 'failed') ? 1 : 0
