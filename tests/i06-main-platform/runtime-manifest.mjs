import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { lstat, readFile, readdir, realpath, writeFile } from 'node:fs/promises'
import path from 'node:path'

const root = '/workspace'
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex')
const identity = JSON.parse(await readFile('/opt/i06-main-identity.json', 'utf8'))
const sources = {}
for (const [name, expected] of Object.entries(identity.sources)) {
  // Harness files may be newer than the frozen app candidate; their separate identity is explicit.
  if (name.startsWith('tests/i06-main-platform/')) continue
  sources[name] = hash(await readFile(path.join(root, name)))
  if (sources[name] !== expected) throw new Error('SOURCE_HASH_MISMATCH')
}
const artifacts = {}
async function walk(relative) {
  for (const name of (await readdir(path.join(root, relative))).sort()) {
    const file = path.join(relative, name)
    const info = await lstat(path.join(root, file))
    if (info.isDirectory()) await walk(file)
    else if (info.isFile()) artifacts[file] = hash(await readFile(path.join(root, file)))
  }
}
await walk('apps/desktop/out')
await walk('tests/i06-main-platform')
for (const [name, expected] of Object.entries(identity.harness)) {
  if (artifacts['tests/i06-main-platform/' + name] !== expected)
    throw new Error('HARNESS_HASH_MISMATCH')
}
const binaries = {}
for (const file of [
  'node_modules/electron/dist/electron',
  'node_modules/electron/dist/chrome-sandbox',
  '.venv/bin/python',
  '/usr/local/bin/node',
  '/usr/local/bin/uv',
]) {
  const actual = await realpath(path.isAbsolute(file) ? file : path.join(root, file))
  binaries[file] = { actual, sha256: hash(await readFile(actual)) }
}
const command = (file, args) => execFileSync(file, args, { cwd: root, encoding: 'utf8' }).trim()
const runtime = {
  node: process.versions,
  electron: JSON.parse(await readFile('node_modules/electron/package.json', 'utf8')).version,
  playwright: JSON.parse(await readFile('node_modules/@playwright/test/package.json', 'utf8'))
    .version,
  npm: command('npm', ['--version']),
  uv: command('uv', ['--version']),
  python: command('.venv/bin/python', ['--version']),
  pythonPackages: JSON.parse(
    command('.venv/bin/python', [
      '-I',
      '-c',
      'import importlib.metadata,json; print(json.dumps(sorted([{"name": d.metadata["Name"], "version": d.version} for d in importlib.metadata.distributions()], key=lambda d:d["name"])))',
    ]),
  ),
  osRelease: await readFile('/etc/os-release', 'utf8'),
  architecture: process.arch,
}
await writeFile(
  process.argv[2],
  JSON.stringify(
    {
      candidate: identity.candidate,
      baseImage: identity.baseImage,
      sources,
      artifacts,
      binaries,
      runtime,
    },
    null,
    2,
  ) + '\n',
)
