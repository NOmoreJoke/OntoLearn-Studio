import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFile, readdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const [container, image, directory, normalEvidence] = process.argv.slice(2)
assert.ok(normalEvidence, 'REQUIRE_SUCCESSFUL_NORMAL_RUN_BINDING')
execFileSync(
  process.execPath,
  ['tests/i06-main-platform/collect-evidence.mjs', container, image, directory],
  { stdio: 'inherit' },
)
const root = path.resolve(directory)
const read = async (name) => JSON.parse(await readFile(path.join(root, name), 'utf8'))
const binding = await read('binding-evidence.json')
const observer = await read('results/native-observer.json')
const actions = await read('results/native-actions.json')
const normal = JSON.parse(await readFile(path.resolve(normalEvidence), 'utf8'))
assert.equal(normal.result, 'passed')
assert.equal(binding.result, 'passed')
assert.equal(observer.result, 'passed')
assert.equal(observer.inspectorClosedBeforeFault, true)
assert.equal(observer.rendererCDPEverAttached, false)
assert.equal(observer.windows.length, 2)
assert.equal(actions.length, 1)
assert.equal(actions[0].prompt.title, 'OntoLearn Studio 窗口恢复')
assert.equal(actions[0].prompt.visible, true)
assert.equal(actions[0].dialogReplacement, false)
assert.deepEqual(actions[0].keys, ['shift+Tab', 'Return'])
assert.equal(binding.probe.receiverRequests, 1)
assert.equal(actions[0].receiverRequestsBeforeAction, 1)
const appArtifacts = (run) =>
  Object.fromEntries(
    Object.entries(run.executedSourceArtifactAndBinaryHashes.artifacts).filter(([name]) =>
      name.startsWith('apps/desktop/out/'),
    ),
  )
assert.deepEqual(
  appArtifacts(binding),
  appArtifacts(normal),
  'NATIVE_MUST_EXECUTE_SAME_FROZEN_APP_BUILD',
)
assert.deepEqual(
  binding.executedSourceArtifactAndBinaryHashes.binaries,
  normal.executedSourceArtifactAndBinaryHashes.binaries,
)
for (const window of observer.windows) {
  assert.equal(window.snapshot.runtime.noSandboxSwitch, false)
  assert.equal(window.snapshot.runtime.disabledHangMonitorSwitch, false)
  assert.equal(window.snapshot.runtime.inspectorURL, null)
  assert.equal(window.snapshot.runtime.remoteDebuggingSwitch, false)
}
const hashes = {}
for (const name of await readdir(path.join(root, 'results'))) {
  const file = path.join(root, 'results', name)
  try {
    hashes[name] = createHash('sha256')
      .update(await readFile(file))
      .digest('hex')
  } catch (error) {
    if (error.code !== 'EISDIR') throw error
  }
}
await writeFile(
  path.join(root, 'native-binding-evidence.json'),
  JSON.stringify(
    {
      result: 'passed',
      normalBindingSha256: createHash('sha256')
        .update(await readFile(path.resolve(normalEvidence)))
        .digest('hex'),
      sameCompiledAppAndBinariesAsNormalRun: true,
      observerAndNativeActionPassed: true,
      hashes,
      binding,
    },
    null,
    2,
  ) + '\n',
)
console.log('Native actual prompt/action/ledger evidence bound')
