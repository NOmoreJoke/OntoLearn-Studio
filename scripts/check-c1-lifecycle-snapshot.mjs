// Runs only extracted accounting functions. Never imports or starts the native CLI.
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import vm from 'node:vm'

const path = process.argv[2] ?? 'tests/e2e/c1-native-macos-driver.mjs'
assert(process.argv.length <= 3, 'only an optional source path is accepted')
const source = readFileSync(path, 'utf8')
const pureStart = source.indexOf('// BEGIN pure process-accounting classifier')
const pureEnd = source.indexOf('// END pure process-accounting classifier.')
const updateStart = source.indexOf('  function updateEntry(')
const updateEnd = source.indexOf('  async function sample(', updateStart)
assert(pureStart >= 0 && pureEnd > pureStart && updateStart >= 0 && updateEnd > updateStart)
const pure = source.slice(pureStart, pureEnd)
const update = source.slice(updateStart, updateEnd)
const finiteStart = source.indexOf('// BEGIN finite termination projection')
const finiteEnd = source.indexOf('// END finite termination projection.')
const finite =
  finiteStart >= 0 && finiteEnd > finiteStart ? source.slice(finiteStart, finiteEnd) : ''
const results = []
const birth = 'Fri Oct 23 01:54:47 2026'
const original = { pid: 42, ppid: 12, start: birth, stat: 'S', command: '/owned/python' }
const row = { ...original, rawLine: `42 12 ${birth} S /owned/python` }
const observation = {
  sequence: 7,
  startedAtMs: 80,
  endedAtMs: 140,
  endedAt: 'sample-end',
  parseComplete: true,
}
const closed = () => ({
  exit: { at: 'exit-event', code: 0, signal: null, receivedAtMs: 100 },
  close: { at: 'close-event', code: 0, signal: null, receivedAtMs: 110 },
})
function entry(sourceKind = 'main-child-object') {
  return {
    ...original,
    source: sourceKind,
    ownershipEstablished: true,
    firstSeenAtMs: 10,
    lastPresentEndedMs: 20,
    originalRow: { ...row },
  }
}
function harness(readLifecycle, now = 500) {
  let lifecycleReads = 0
  let clockReads = 0
  const calls = []
  const failures = []
  const context = {
    Buffer,
    structuredClone,
    Date: {
      parse: Date.parse,
      now: () => {
        clockReads++
        return now
      },
    },
    lifecycle: () => {
      lifecycleReads++
      return readLifecycle()
    },
    fail: (error) => failures.push(String(error)),
    capture: (args) => calls.push(args),
  }
  const actual = vm.runInNewContext(
    pure +
      '\n' +
      finite +
      '\n' +
      'const actualClassifier = classifyProcess; classifyProcess = (...args) => { capture(args); return actualClassifier(...args) };\n' +
      update +
      '\n;({ updateEntry, classifyProcess })',
    context,
  )
  return { ...actual, calls, failures, counts: () => ({ lifecycleReads, clockReads }) }
}
function check(name, fn) {
  try {
    fn()
    results.push({ name, outcome: 'passed' })
  } catch (error) {
    results.push({ name, outcome: 'failed', error: String(error.stack) })
  }
}
function plain(value) {
  return JSON.parse(JSON.stringify(value))
}

check('classifier contract remains byte-identical to 650', () => {
  assert.equal(
    createHash('sha256').update(pure).digest('hex'),
    '68238542607e8992a4b58f38fa1b2c82a58bb3bbbbd874fff1de435dfb104c89',
  )
})
check('later original child events cannot rewrite an earlier transition', () => {
  const reported = {
    pid: 42,
    file: '/owned/python',
    argv: ['/owned/python', '-I'],
    created: { at: 'created', receivedAtMs: 50 },
  }
  const h = harness(() => reported)
  const transition = h.updateEntry(entry(), row, observation)
  const before = JSON.stringify(transition)
  Object.assign(reported, closed(), { error: { message: 'later-error', nested: { value: 1 } } })
  reported.argv[0] = '/other/python'
  reported.created.receivedAtMs = 999
  assert.equal(JSON.stringify(transition), before)
  assert.equal(transition.lifecycle.exit, undefined)
  assert.equal(transition.classification.trustedOriginalClose, false)
})
check('preexisting nested lifecycle values are detached from both directions', () => {
  const reported = { ...closed(), argv: ['/owned/python'], error: { nested: { value: 1 } } }
  const h = harness(() => reported)
  const transition = h.updateEntry(entry(), undefined, observation)
  reported.exit.code = 7
  reported.error.nested.value = 2
  reported.argv.push('changed')
  assert.equal(transition.lifecycle.exit.code, 0)
  assert.equal(transition.lifecycle.error.nested.value, 1)
  assert.equal(transition.lifecycle.argv.length, 1)
  transition.lifecycle.close.code = 8
  assert.equal(reported.close.code, 0)
})
check('one lifecycle capture and clock value feed classification and its record', () => {
  const first = { created: { receivedAtMs: 50 } }
  let reads = 0
  const h = harness(() => (++reads === 1 ? first : closed()), 170)
  const transition = h.updateEntry(entry(), row, observation)
  assert.deepEqual(h.counts(), { lifecycleReads: 1, clockReads: 1 })
  assert.equal(h.calls.length, 1)
  assert.equal(h.calls[0][3], transition.lifecycle)
  assert.notEqual(transition.lifecycle, first)
  assert.equal(h.calls[0][4], 170)
  assert.equal(transition.classifiedAtMs, 170)
  assert.equal(transition.consumedAtMs, 170)
})
check('main lifecycle event and receive times and sample interval survive unchanged', () => {
  const mainLifecycle = closed()
  const h = harness(() => ({ ...mainLifecycle }), 150)
  const transition = h.updateEntry(entry('direct-spawn'), undefined, observation)
  assert.deepEqual(plain(transition.lifecycle), mainLifecycle)
  assert.equal(transition.sampleStartedAtMs, 80)
  assert.equal(transition.sampleEndedAtMs, 140)
  assert.equal(transition.classification.trustedOriginalClose, true)
  assert.equal(transition.classification.freshAbsence, false)
  assert.equal(transition.classification.resolvedTerminal, false)
})
check('a later snapshot sees close without mutating the first snapshot', () => {
  const reported = { created: { receivedAtMs: 50 } }
  const h = harness(() => reported)
  const target = entry()
  const first = h.updateEntry(target, row, observation)
  const before = JSON.stringify(first)
  Object.assign(reported, closed())
  const second = h.updateEntry(target, undefined, {
    ...observation,
    sequence: 8,
    startedAtMs: 160,
    endedAtMs: 170,
  })
  assert.equal(JSON.stringify(first), before)
  assert.equal(second.classification.trustedOriginalClose, true)
  assert.equal(second.classification.freshAbsence, true)
  assert.equal(second.classification.resolvedTerminal, true)
})
check('missing lifecycle records null and invents no natural close', () => {
  const h = harness(() => undefined)
  const transition = h.updateEntry(entry(), undefined, observation)
  assert.equal(transition.lifecycle, null)
  assert.equal(transition.classification.trustedOriginalClose, false)
  assert.equal(transition.classification.resolvedTerminal, false)
})
check('run02-style active mismatch remains unresolved after close and fresh absence', () => {
  const h = harness(() => closed())
  const target = entry()
  const changed = { ...row, command: '(python3.12)', stat: 'R' }
  h.updateEntry(target, changed, observation)
  const last = h.updateEntry(target, undefined, {
    ...observation,
    sequence: 8,
    startedAtMs: 200,
    endedAtMs: 210,
  })
  assert.equal(last.classification.unexplainedDisplay, true)
  assert.equal(last.classification.resolvedTerminal, false)
  assert.equal(last.classification.signalEligible, false)
})
check('run03-style helper mismatch cannot borrow main close or later absence', () => {
  const h = harness(() => undefined)
  const target = entry('ancestry')
  h.updateEntry(target, { ...row, command: '(Electron Helper)', stat: 'S' }, observation)
  const last = h.updateEntry(target, undefined, {
    ...observation,
    sequence: 8,
    startedAtMs: 200,
    endedAtMs: 210,
  })
  assert.equal(last.classification.trustedOriginalClose, false)
  assert.equal(last.classification.resolvedTerminal, false)
  assert.equal(last.classification.signalEligible, false)
})
check('birth conflict remains permanent after natural close and absence', () => {
  const h = harness(() => closed())
  const target = entry()
  h.updateEntry(target, { ...row, start: 'Fri Oct 23 01:54:48 2026' }, observation)
  const last = h.updateEntry(target, undefined, {
    ...observation,
    sequence: 8,
    startedAtMs: 200,
    endedAtMs: 210,
  })
  assert.equal(last.classification.failureReason, 'birth-conflict')
  assert.equal(last.classification.resolvedTerminal, false)
  assert.equal(last.classification.signalEligible, false)
})

console.log(
  JSON.stringify(
    { source: path, sourceSHA256: createHash('sha256').update(source).digest('hex'), results },
    null,
    2,
  ),
)
process.exitCode = results.some((result) => result.outcome === 'failed') ? 1 : 0
