// Post-run readback only; original runtime/scanner receipts remain unchanged.
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
const [container, directory] = process.argv.slice(2)
const output = path.resolve(directory)
const docker = (...args) => execFileSync('docker', args, { encoding: 'utf8' })
const inspect = JSON.parse(docker('inspect', container))[0]
assert.equal(inspect.State.Status, 'exited')
assert.equal(inspect.HostConfig.NetworkMode, 'none')
assert.equal(inspect.Mounts.length, 0)
const scan = JSON.parse(await readFile(path.join(output, 'results/leak-scan.json'), 'utf8'))
assert.equal(scan.result, 'passed')
const target = path.join(output, 'storage-readback')
await mkdir(target)
const hashes = {}
for (const entry of scan.rawDatabaseFiles) {
  assert.match(entry.path, /^\/probe-data\/fixtures\//)
  const name = entry.path.slice('/probe-data/fixtures/'.length).replaceAll('/', '--')
  docker('cp', `${container}:${entry.path}`, path.join(target, name))
}
// Private directory holds only metadata, ciphertext and durable audit, never raw bodies.
const profiles = docker('cp', `${container}:/probe-data/profiles/.`, path.join(target, 'profiles'))
void profiles
// Remove Chromium profile/cache copies immediately; retain only the reviewed gateway-private data.
const { rm, rename } = await import('node:fs/promises')
for (const profile of await readdir(path.join(target, 'profiles'))) {
  const source = path.join(target, 'profiles', profile, 'model-gateway-private-v1')
  try {
    await rename(source, path.join(target, 'private--' + profile))
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
  }
}
await rm(path.join(target, 'profiles'), { recursive: true })
async function walk(relative) {
  for (const entry of await readdir(path.join(target, relative), { withFileTypes: true })) {
    const name = path.join(relative, entry.name)
    if (entry.isDirectory()) await walk(name)
    else if (entry.isFile())
      hashes[name] = createHash('sha256')
        .update(await readFile(path.join(target, name)))
        .digest('hex')
  }
}
await walk('')
await writeFile(
  path.join(output, 'storage-readback.json'),
  JSON.stringify(
    {
      containerId: inspect.Id,
      collectedAfterExit: true,
      originalRuntimeReceiptUnchanged: true,
      scannerSha256: createHash('sha256')
        .update(await readFile(path.join(output, 'executed-harness/scan.mjs')))
        .digest('hex'),
      files: hashes,
    },
    null,
    2,
  ) + '\n',
)
console.log('Stopped-container synthetic storage readback archived')
