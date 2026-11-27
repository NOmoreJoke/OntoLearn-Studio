// Interpret unchanged repository e2e results independently from S3 custom probe gates.
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
const directory = path.resolve(process.argv[2])
const read = async (name) => JSON.parse(await readFile(path.join(directory, name), 'utf8'))
const binding = await read('binding-evidence.json')
assert.equal(binding.gates.runtimeUnchanged, true)
assert.equal(binding.gates.containerExitedZero, true)
const modes = {}
for (const mode of ['source', 'packaged']) {
  const report = await read(`results/regression/${mode}-playwright.json`)
  const exit = Number(
    await readFile(path.join(directory, `results/regression/${mode}-exit.txt`), 'utf8'),
  )
  const cases = []
  function walk(suite) {
    for (const spec of suite.specs ?? [])
      for (const test of spec.tests)
        cases.push({
          file: spec.file,
          line: spec.line,
          title: spec.title,
          expectedStatus: test.expectedStatus,
          status: test.status,
          results: test.results.map((result) => ({
            status: result.status,
            error: result.error?.message ?? null,
          })),
        })
    for (const child of suite.suites ?? []) walk(child)
  }
  for (const suite of report.suites) walk(suite)
  modes[mode] = {
    exit,
    stats: report.stats,
    cases,
    command:
      mode === 'source'
        ? 'npm run test:e2e -- --output=/probe-data/main-platform/regression/source-traces --reporter=list,json'
        : 'ONTOLEARN_PACKAGED_EXECUTABLE=/workspace/release/linux-arm64-unpacked/@ontolearndesktop npm run test:e2e -- --output=/probe-data/main-platform/regression/packaged-traces --reporter=list,json',
  }
}
const runtime = binding.executedSourceArtifactAndBinaryHashes
const receipt = {
  result: Object.values(modes).every((entry) => entry.exit === 0 && entry.stats.unexpected === 0)
    ? 'passed'
    : 'failed',
  candidate: binding.candidate,
  modes,
  imageId: binding.imageId,
  containerId: binding.containerId,
  runtimeAndSourceBindingSha256: createHash('sha256')
    .update(await readFile(path.join(directory, 'binding-evidence.json')))
    .digest('hex'),
  runtimeSourcesUnchanged: true,
  sourceHashes: runtime.sources,
  regressionOnly:
    'Existing Playwright Electron loader and existing native helper stubs are not actual safeStorage/native proof.',
  fixtureGates:
    'Default CI full-suite command; no I04_TEST_FIXTURE/I04_NATIVE_ISOLATED. Three fixture-gated scenarios skipped in each mode. Targeted CI fixture scenarios remain separate.',
  noHostGUI: true,
  runtimeNetwork: 'none',
  addedCapability: 'SYS_ADMIN',
  seccomp: 'Docker default',
}
await writeFile(
  path.join(directory, 'regression-receipt.json'),
  JSON.stringify(receipt, null, 2) + '\n',
)
console.log(
  JSON.stringify({
    result: receipt.result,
    modes: Object.fromEntries(
      Object.entries(modes).map(([name, value]) => [
        name,
        { exit: value.exit, stats: value.stats },
      ]),
    ),
  }),
)
