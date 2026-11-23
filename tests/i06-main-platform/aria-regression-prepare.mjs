import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdir, readFile, readdir, writeFile, cp } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// No source-root option: only this worktree's explicitly merged, committed candidate is built.
const directory = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(directory, '../..')
const [candidate, attempt] = process.argv.slice(2)
assert.match(candidate ?? '', /^[a-f0-9]{40}$/)
assert.match(attempt ?? '', /^[a-z][a-z0-9-]{0,24}$/)
const run = (command, args) => execFileSync(command, args, { cwd: root, encoding: 'utf8' })
assert.equal(candidate, 'e2c269ad78a78e1a042cadc93b1c81a874707153')
for (const lock of ['package-lock.json', 'uv.lock'])
  assert.equal(
    run('git', ['show', `${candidate}:${lock}`]),
    run('git', ['show', `9fcba6634d5c16983c36ef671d4ec8e79694b6d6:${lock}`]),
    'DEPENDENCY_LOCK_DRIFT',
  )
run('git', ['merge-base', '--is-ancestor', candidate, 'HEAD'])
for (const name of run('git', ['diff', '--name-only', '-z', candidate, 'HEAD'])
  .split('\0')
  .filter(Boolean))
  assert.ok(
    name.startsWith('tests/i06-main-platform/') ||
      name.startsWith('docs/reviews/I06/main-platform/'),
    'PRODUCT_SOURCE_DRIFT',
  )
assert.match(run('git', ['branch', '--show-current']).trim(), /^feature\/I06-main-platform$/)
const protectedHash = createHash('sha256')
  .update(await readFile(path.join(root, 'AGENTS.md')))
  .digest('hex')
assert.equal(protectedHash, 'db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786')
const dirty = run('git', ['status', '--porcelain', '--untracked-files=all'])
  .split('\n')
  .filter(Boolean)
for (const entry of dirty) {
  const relative = entry.slice(3)
  assert.ok(
    relative === 'AGENTS.md' ||
      relative.startsWith('tests/i06-main-platform/') ||
      relative.startsWith('docs/reviews/I06/main-platform/'),
    'OUT_OF_SCOPE_DIRTY_SOURCE',
  )
}
const base = 'sha256:0497417676f686d3b35a17d6c08a2c28a4c7e81169e9f72c17a50d748ae33a44'
assert.equal(
  run('docker', [
    'image',
    'inspect',
    'i06-safe-storage-platform:base-0497417676f6',
    '--format',
    '{{.Id}}',
  ]).trim(),
  base,
)
assert.equal(
  run('docker', [
    'image',
    'inspect',
    'i06-main-packaged:9fcba663-base2',
    '--format',
    '{{.Id}}',
  ]).trim(),
  'sha256:b7bba605ea11528cbfcadf6ab3e8e341243fa19d9cf384f84427b3d899b07dc0',
)
const output = path.join(directory, 'out', candidate.slice(0, 12) + '-' + attempt)
await mkdir(output, { recursive: false }) // Never overwrite a failed/frozen build context.
const context = path.join(output, 'context')
await mkdir(path.join(context, 'source'), { recursive: true })
const archive = path.join(output, 'candidate.tar')
run('git', ['archive', '--format=tar', '--output', archive, candidate])
run('tar', ['-xf', archive, '-C', path.join(context, 'source')])
await mkdir(path.join(context, 'harness'))
for (const name of await readdir(directory)) {
  if (name === 'out') continue
  await cp(path.join(directory, name), path.join(context, 'harness', name), { recursive: true })
}
await cp(path.join(directory, 'Dockerfile.aria-regression'), path.join(context, 'Dockerfile'))
const sourceFiles = run('git', ['ls-tree', '-r', '--name-only', '-z', candidate])
  .split('\0')
  .filter(Boolean)
const sources = {}
for (const name of sourceFiles)
  sources[name] = createHash('sha256')
    .update(await readFile(path.join(context, 'source', name)))
    .digest('hex')
const harness = {}
for (const name of await readdir(path.join(context, 'harness')))
  harness[name] = createHash('sha256')
    .update(await readFile(path.join(context, 'harness', name)))
    .digest('hex')
await writeFile(
  path.join(context, 'identity.json'),
  JSON.stringify(
    {
      candidate,
      baseImage: 'sha256:b7bba605ea11528cbfcadf6ab3e8e341243fa19d9cf384f84427b3d899b07dc0',
      sourceDependencyBase: base,
      protectedGuidanceHash: protectedHash,
      sources,
      harness,
    },
    null,
    2,
  ) + '\n',
)
console.log(JSON.stringify({ candidate, context, output, baseImage: base }))
