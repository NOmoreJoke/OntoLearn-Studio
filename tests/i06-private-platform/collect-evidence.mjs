import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import assert from 'node:assert/strict'

const [container, expectedImage, output] = process.argv.slice(2)
assert.ok(container && expectedImage && output)
const destination = path.resolve(output)
await mkdir(destination, { recursive: true })
const docker = (...args) => execFileSync('docker', args, { encoding: 'utf8' })
const inspect = JSON.parse(docker('inspect', container))[0]
const image = JSON.parse(docker('image', 'inspect', expectedImage))[0]
assert.equal(inspect.Image, image.Id)
assert.equal(inspect.HostConfig.NetworkMode, 'none')
assert.equal(inspect.State.Status, 'exited')
assert.equal(inspect.State.ExitCode, 0)
await writeFile(path.join(destination, 'container-inspect.json'), JSON.stringify(inspect, null, 2))
await writeFile(path.join(destination, 'image-inspect.json'), JSON.stringify(image, null, 2))
docker('cp', `${container}:/probe-data/combination-results`, path.join(destination, 'results'))
docker('cp', `${container}:/opt/i06-private-platform/out`, path.join(destination, 'executed'))
for (const file of ['probe.cjs', 'run-isolated.sh'])
  docker('cp', `${container}:/opt/i06-private-platform/${file}`, path.join(destination, file))
docker(
  'cp',
  `${container}:/opt/i06-private-platform/node_modules/zod/package.json`,
  path.join(destination, 'zod-package.json'),
)
docker(
  'cp',
  `${container}:/opt/i06-platform/node_modules/electron/package.json`,
  path.join(destination, 'electron-package.json'),
)
const digest = async (file) =>
  createHash('sha256')
    .update(await readFile(file))
    .digest('hex')
const hostDirectory = new URL('./', import.meta.url)
const comparisons = {}
const sourceManifest = JSON.parse(
  await readFile(path.join(destination, 'executed', 'sources.json'), 'utf8'),
)
assert.deepEqual(
  (await readdir(path.join(destination, 'executed'))).sort(),
  [
    ...Object.keys(sourceManifest).map((file) => path.basename(file, '.ts') + '.js'),
    'package.json',
    'sources.json',
  ].sort(),
)
for (const file of await readdir(path.join(destination, 'executed'))) {
  const actual = await digest(path.join(destination, 'executed', file))
  const expected = await digest(new URL('out/' + file, hostDirectory))
  assert.equal(actual, expected)
  comparisons['out/' + file] = { sha256: actual, hostEqualsExecuted: true }
}
for (const file of ['probe.cjs', 'run-isolated.sh']) {
  const actual = await digest(path.join(destination, file))
  assert.equal(actual, await digest(new URL(file, hostDirectory)))
  comparisons[file] = { sha256: actual, hostEqualsExecuted: true }
}
for (const [file, version] of [
  ['electron-package.json', '44.9.0'],
  ['zod-package.json', '4.6.7'],
]) {
  assert.equal(JSON.parse(await readFile(path.join(destination, file), 'utf8')).version, version)
  comparisons[file] = { sha256: await digest(path.join(destination, file)), version }
}
const manifest = JSON.parse(
  await readFile(path.join(destination, 'executed', 'sources.json'), 'utf8'),
)
for (const [relative, hashes] of Object.entries(manifest)) {
  const name = path.basename(relative, '.ts')
  assert.equal(comparisons['out/' + name + '.js'].sha256, hashes.compiledSha256)
  assert.equal(
    await digest(new URL('out/snapshot/' + name + '.ts', hostDirectory)),
    hashes.sourceSha256,
  )
}
const cases = await Promise.all(
  ['secure-send', 'recover-no-replay', 'corrupt', 'key-loss', 'basic', 'unavailable'].map(
    async (mode) => {
      const item = JSON.parse(
        await readFile(path.join(destination, 'results', mode + '.json'), 'utf8'),
      )
      assert.equal(item.result, 'passed')
      return item
    },
  ),
)
const result = {
  result: 'passed',
  imageId: image.Id,
  containerId: inspect.Id,
  network: 'none',
  state: inspect.State,
  executedComparisons: comparisons,
  sources: manifest,
  cases,
  logScan: JSON.parse(await readFile(path.join(destination, 'results', 'log-scan.json'), 'utf8')),
}
await writeFile(
  path.join(destination, 'binding-evidence.json'),
  JSON.stringify(result, null, 2) + '\n',
)
console.log(
  'Actual container artifacts, source snapshot, dependencies and execution identity matched',
)
