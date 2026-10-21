import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
const [directory, retryDirectory] = process.argv.slice(2).map((value) => path.resolve(value))
const read = async (root, name) => JSON.parse(await readFile(path.join(root, name), 'utf8'))
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex')
const binding = await read(directory, 'binding-evidence.json')
assert.equal(binding.candidate, 'e2c269ad78a78e1a042cadc93b1c81a874707153')
assert.equal(binding.gates.runtimeUnchanged, true)
assert.equal(binding.gates.containerExitedZero, true)
assert.equal(
  binding.executedSourceArtifactAndBinaryHashes.sources['apps/desktop/src/renderer/src/App.tsx'],
  'd66e74cd77b4ef1e5b0e97f3ddefe10481dccd8466bbc40c1f403eaee1b22716',
)
const gates = {},
  expectedFailures = []
for (const mode of ['source', 'packaged']) {
  for (const scenario of ['', '-aria', '-native', '-reload', '-disconnect']) {
    const name = mode + scenario
    const exit = Number(
      await readFile(path.join(directory, `results/regression/${name}-exit.txt`), 'utf8'),
    )
    if (scenario === '-aria') {
      const result = await read(directory, `results/regression/${mode}-aria-live.json`)
      assert.equal(result.result, 'passed')
      assert.equal(exit, 0)
      assert.equal(result.runtime.packaged, mode === 'packaged')
      assert.deepEqual(
        result.snapshots.map((entry) => [
          entry.stage,
          entry.ariaLive,
          entry.role,
          entry.statusCount,
        ]),
        [
          ['initial', 'polite', null, 1],
          ['reload', 'polite', null, 1],
        ],
      )
      gates[name] = { exit, result: result.result }
    } else {
      const report = await read(directory, `results/regression/${name}-playwright.json`)
      const stats = report.stats
      if (name === 'source-native' && exit !== 0) {
        assert.equal(stats.unexpected, 1)
        assert.equal(stats.skipped, 0)
        expectedFailures.push(name)
      } else {
        assert.equal(exit, 0)
        assert.equal(stats.unexpected, 0)
        assert.equal(stats.flaky, 0)
        assert.equal(stats.expected, scenario === '' ? 3 : 1)
        assert.equal(stats.skipped, scenario === '' ? 3 : 0)
      }
      gates[name] = { exit, stats }
    }
  }
}
assert.deepEqual(expectedFailures, ['source-native'])
const retry = await read(retryDirectory, 'binding-evidence.json')
assert.equal(retry.candidate, binding.candidate)
assert.equal(retry.imageId, binding.imageId)
assert.equal(retry.gates.runtimeUnchanged, true)
assert.equal(retry.gates.containerExitedZero, true)
assert.deepEqual(
  retry.executedSourceArtifactAndBinaryHashes,
  binding.executedSourceArtifactAndBinaryHashes,
)
const retryExit = Number(
  await readFile(
    path.join(retryDirectory, 'results/regression/source-native-retry-exit.txt'),
    'utf8',
  ),
)
const retryReport = await read(
  retryDirectory,
  'results/regression/source-native-retry-playwright.json',
)
assert.equal(retryExit, 0)
assert.equal(retryReport.stats.expected, 1)
assert.equal(retryReport.stats.skipped, 0)
assert.equal(retryReport.stats.unexpected, 0)
const retryInspect = await read(retryDirectory, 'container-inspect.json')
const retryScript = await readFile(path.join(retryDirectory, '../run-script.sh'), 'utf8')
assert.deepEqual(retryInspect.Config.Entrypoint, ['bash'])
assert.deepEqual(retryInspect.Config.Cmd, ['-c', retryScript])
const before = await read(directory, 'results/package-before.json')
assert.equal(before.productCandidate, binding.candidate)
assert.deepEqual(before, await read(directory, 'results/package-after.json'))
execFileSync('docker', [
  'cp',
  `${binding.containerId}:/workspace/release/linux-arm64-unpacked`,
  path.join(directory, 'executed-package'),
])
for (const [name, expected] of Object.entries(before.files)) {
  const bytes = await readFile(path.join(directory, 'executed-package', name))
  assert.equal(hash(bytes), expected.sha256)
  assert.equal(bytes.length, expected.bytes)
}
// Independently bind actual asar-built code to this run's normal build output.
const asar = await readFile(path.join(directory, 'executed-package/resources/app.asar'))
const header = JSON.parse(asar.subarray(16, 16 + asar.readUInt32LE(12)).toString())
const dataOffset = 8 + asar.readUInt32LE(4),
  compiled = {}
for (const [name, expected] of Object.entries(
  binding.executedSourceArtifactAndBinaryHashes.artifacts,
)) {
  if (!name.startsWith('apps/desktop/out/')) continue
  const relative = 'out/' + name.slice('apps/desktop/out/'.length)
  let entry = header
  for (const part of relative.split('/')) entry = entry.files[part]
  const start = dataOffset + Number(entry.offset),
    bytes = asar.subarray(start, start + entry.size)
  assert.equal(bytes.length, entry.size)
  assert.equal(hash(bytes), expected)
  compiled[relative] = expected
}
const receipt = {
  result: 'passed-on-targeted-retry-with-initial-failure-retained',
  candidate: binding.candidate,
  imageId: binding.imageId,
  initialContainerId: binding.containerId,
  retryContainerId: retry.containerId,
  initialGates: gates,
  initialGatePasses: 9,
  initialGateFailures: ['source-native'],
  targetedRetry: {
    result: 'passed',
    exit: retryExit,
    stats: retryReport.stats,
    sameImmutableImageSourceAndRuntime: true,
    inlineRunnerSha256: hash(Buffer.from(retryScript)),
  },
  firstFailure: {
    originalCodeDeadline: 'Date.now()+30000 per crash/hang phase',
    totalReportDurationMs: gates['source-native'].stats.duration,
    observation:
      'crashed; two windows; inspector closed; focused second window; hang native prompt not observed before original assertion. Cause not established.',
  },
  packageFilesReadBack: Object.keys(before.files).length,
  packageFileMap: before,
  asarCompiledOutputHashesMatched: compiled,
  sourceHashMap: binding.executedSourceArtifactAndBinaryHashes.sources,
  scope:
    'Original unchanged repository e2e source/packaged default suites, six fresh CI fixture gates, and unavailable-model aria-live checks. This does not rerun or relabel old 9fc S3 credential/domain platform evidence.',
  defaultFixtureSkips:
    'Three per default full suite, each separately covered by a real non-skipped fresh-fixture invocation.',
  nativeEvidenceBoundary:
    'C1 original helper stubs dialog; actual I04 native targeted cases use real visible prompt and focus observers. Do not substitute one for the other.',
  initialCaptureSha256: hash(await readFile(path.join(directory, 'binding-evidence.json'))),
  retryCaptureSha256: hash(await readFile(path.join(retryDirectory, 'binding-evidence.json'))),
}
await writeFile(
  path.join(directory, 'aria-regression-receipt.json'),
  JSON.stringify(receipt, null, 2) + '\n',
)
console.log(
  JSON.stringify({
    result: receipt.result,
    candidate: receipt.candidate,
    initialPassed: 9,
    initialFailed: 1,
    targetedRetryPassed: true,
    packageFiles: receipt.packageFilesReadBack,
    compiledFiles: Object.keys(compiled).length,
  }),
)
