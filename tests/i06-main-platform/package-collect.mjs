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
assert.equal(binding.candidate, normal.candidate)
assert.deepEqual(
  binding.executedSourceArtifactAndBinaryHashes.sources,
  normal.executedSourceArtifactAndBinaryHashes.sources,
)
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
const packageBefore = await read('results/package-before.json')
assert.deepEqual(packageBefore, await read('results/package-after.json'))
assert.deepEqual(packageBefore, await read('results/package-build-manifest.json'))
assert.equal(observer.windows[0].snapshot.runtime.packaged, true)
assert.ok(observer.engineProcesses.length > 0)
const finite = await read('results/package-finite-denial.json')
assert.equal(finite.result, 'passed')
assert.equal(finite.credentialFiles, 0)
const finiteReceiver = await read('results/package-finite-receiver.json')
assert.equal(finiteReceiver.receiverActiveDuringDeniedBridgeCalls, true)
assert.equal(finiteReceiver.actualRequestDelta, 0)
assert.equal(finite.rejections.length, 3)
for (const entry of finite.rejections)
  assert.equal(entry.reply.error.code, 'GATEWAY_MODEL_UNAVAILABLE')
const mainPid = observer.windows[0].snapshot.runtime.mainPid
for (const entry of observer.engineProcesses) {
  assert.equal(entry.currentMainPid, mainPid)
  assert.ok(entry.ancestors.some((item) => item.pid === mainPid))
  for (let index = 1; index < entry.ancestors.length; index++)
    assert.equal(entry.ancestors[index - 1].ppid, entry.ancestors[index].pid)
}
assert.equal(finite.appIsPackaged, true)
execFileSync('docker', [
  'cp',
  `${container}:/workspace/release/linux-arm64-unpacked`,
  path.join(root, 'executed-package'),
])
for (const [name, expected] of Object.entries(packageBefore.files)) {
  const actual = await readFile(path.join(root, 'executed-package', name))
  assert.equal(
    createHash('sha256').update(actual).digest('hex'),
    expected.sha256,
    'ACTUAL_PACKAGED_FILE_READBACK_MISMATCH',
  )
  assert.equal(actual.length, expected.bytes)
}
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
  path.join(root, 'package-binding-evidence.json'),
  JSON.stringify(
    {
      result: 'passed',
      normalBindingSha256: createHash('sha256')
        .update(await readFile(path.resolve(normalEvidence)))
        .digest('hex'),
      sameProductSourcesAsNormalRun: true,
      packageManifest: packageBefore,
      finitePolicyRejected: true,
      observerAndNativeActionPassed: true,
      hashes,
      binding,
    },
    null,
    2,
  ) + '\n',
)
console.log('Packaged executable/engine/whole-result/real prompt evidence bound')
