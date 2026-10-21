import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'

const [container, expectedImage, directory] = process.argv.slice(2)
assert.ok(container && expectedImage && directory)
const destination = path.resolve(directory)
await mkdir(destination, { recursive: false })
const docker = (...args) => execFileSync('docker', args, { encoding: 'utf8' })
const inspect = JSON.parse(docker('inspect', container))[0]
const image = JSON.parse(docker('image', 'inspect', expectedImage))[0]
assert.equal(inspect.Image, image.Id)
assert.equal(inspect.HostConfig.NetworkMode, 'none')
assert.equal(inspect.HostConfig.Privileged, false)
assert.equal(inspect.Mounts.length, 0)
assert.equal(inspect.Config.User, 'i06')
assert.deepEqual(
  (inspect.HostConfig.CapAdd ?? []).map((cap) => cap.replace(/^CAP_/, '')),
  ['SYS_ADMIN'],
)
assert.equal((inspect.HostConfig.SecurityOpt ?? []).length, 0)
assert.equal(Object.keys(inspect.HostConfig.PortBindings ?? {}).length, 0)
assert.equal(inspect.State.Status, 'exited')
await writeFile(
  path.join(destination, 'container-inspect.json'),
  JSON.stringify(inspect, null, 2) + '\n',
)
await writeFile(path.join(destination, 'image-inspect.json'), JSON.stringify(image, null, 2) + '\n')
// Collect failed runs too; evidence preservation does not depend on exit zero.
docker('cp', `${container}:/probe-data/main-platform`, path.join(destination, 'results'))
docker('cp', `${container}:/workspace/apps/desktop/out`, path.join(destination, 'executed-app'))
docker(
  'cp',
  `${container}:/workspace/tests/i06-main-platform`,
  path.join(destination, 'executed-harness'),
)
const before = JSON.parse(
  await readFile(path.join(destination, 'results/runtime-before.json'), 'utf8'),
)
const build = JSON.parse(
  await readFile(path.join(destination, 'results/build-manifest.json'), 'utf8'),
)
const expectedIdentity = JSON.parse(
  await readFile(path.join(destination, '../context/identity.json'), 'utf8'),
)
const executedIdentity = JSON.parse(
  await readFile(path.join(destination, 'results/identity.json'), 'utf8'),
)
assert.deepEqual(executedIdentity, expectedIdentity, 'HOST_BUILD_CONTEXT_IDENTITY_MISMATCH')
assert.equal(before.candidate, expectedIdentity.candidate)
assert.deepEqual(
  before.sources,
  Object.fromEntries(
    Object.entries(expectedIdentity.sources).filter(
      ([name]) => !name.startsWith('tests/i06-main-platform/'),
    ),
  ),
)
assert.deepEqual(before, build)
for (const [name, expected] of Object.entries(before.artifacts)) {
  const relative = name.startsWith('apps/desktop/out/')
    ? 'executed-app/' + name.slice('apps/desktop/out/'.length)
    : 'executed-harness/' + name.slice('tests/i06-main-platform/'.length)
  const actual = createHash('sha256')
    .update(await readFile(path.join(destination, relative)))
    .digest('hex')
  assert.equal(actual, expected, 'EXECUTED_ARTIFACT_MISMATCH')
}
const result = JSON.parse(
  await readFile(path.join(destination, 'results/result.json'), 'utf8').catch(
    () => '{"result":"failed-before-summary"}',
  ),
)
const after = JSON.parse(
  await readFile(path.join(destination, 'results/runtime-after.json'), 'utf8').catch(() => 'null'),
)
const scan = JSON.parse(
  await readFile(path.join(destination, 'results/leak-scan.json'), 'utf8').catch(() => 'null'),
)
const receiver = JSON.parse(
  await readFile(path.join(destination, 'results/receiver-manifest.json'), 'utf8').catch(
    () => '[]',
  ),
)
let receiverBodiesBound =
  receiver.length === result.receiverRequests &&
  new Set(receiver.map((entry) => entry.index)).size === receiver.length
for (const entry of receiver) {
  const body = await readFile(path.join(destination, `results/receiver-${entry.index}.body`)).catch(
    () => null,
  )
  if (
    !body ||
    body.length !== entry.byteCount ||
    createHash('sha256').update(body).digest('hex') !== entry.sha256
  )
    receiverBodiesBound = false
}
const gates = {
  probePassed: result.result === 'passed',
  containerExitedZero: inspect.State.ExitCode === 0,
  runtimeUnchanged: JSON.stringify(after) === JSON.stringify(before),
  leakageScanPassed: scan?.result === 'passed',
  receiverBodiesBound,
}
const summary = {
  result: Object.values(gates).every(Boolean) ? 'passed' : 'failed',
  gates,
  imageId: image.Id,
  containerId: inspect.Id,
  network: 'none',
  privileged: false,
  addedCapability: 'SYS_ADMIN',
  seccomp: 'Docker default',
  mounts: 0,
  exitCode: inspect.State.ExitCode,
  candidate: before.candidate,
  hostBuildContextIdentityMatched: true,
  executedSourceArtifactAndBinaryHashes: before,
  probe: result,
}
await writeFile(
  path.join(destination, 'binding-evidence.json'),
  JSON.stringify(summary, null, 2) + '\n',
)
console.log(
  JSON.stringify({
    result: summary.result,
    candidate: before.candidate,
    evidence: path.join(destination, 'binding-evidence.json'),
  }),
)
