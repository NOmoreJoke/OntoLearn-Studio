import { afterEach, describe, expect, it } from 'vitest'
import { spawnSync } from 'node:child_process'
import {
  copyFile,
  mkdir,
  mkdtemp,
  readFile,
  rename,
  rm,
  symlink,
  unlink,
  writeFile,
} from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { tmpdir } from 'node:os'

const prefix = 'docs/reviews/T01/designated-review-backlog-20261022/'
const paths = [
  'coverage/build_coverage.py',
  'preparation-scripts/build_inventory.py',
  'preparation-scripts/build_submission.py',
  'preparation-scripts/verify_persistent_package.py',
].map((name) => prefix + name)
const owned: string[] = []
afterEach(async () => {
  await Promise.all(owned.splice(0).map((root) => rm(root, { recursive: true, force: true })))
})
async function fixture() {
  const root = await mkdtemp(join(tmpdir(), 't01-frozen-review-guard-'))
  owned.push(root)
  const script = join(root, 'scripts/verify-frozen-review-sources.mjs')
  await mkdir(join(root, 'scripts'))
  await copyFile(resolve('scripts/verify-frozen-review-sources.mjs'), script)
  for (const path of paths) {
    const destination = join(root, path)
    await mkdir(resolve(destination, '..'), { recursive: true })
    await copyFile(resolve(path), destination)
  }
  return { root, script, leaf: join(root, paths[0]) }
}
function execute(script: string) {
  return spawnSync(process.execPath, [script], {
    encoding: 'utf8',
    timeout: 2000,
    maxBuffer: 32768,
  })
}
function rejected(result: ReturnType<typeof execute>) {
  expect(result.error).toBeUndefined()
  expect(result.signal).toBeNull()
  expect(result.status).toBe(1)
}
describe('immutable archived review source guard', () => {
  it('accepts exact originals without executing the archived generators', async () => {
    const f = await fixture(),
      result = execute(f.script)
    expect({ code: result.status, signal: result.signal, error: result.error }).toEqual({
      code: 0,
      signal: null,
      error: undefined,
    })
    expect(result.stdout).toBe('Verified 4 immutable review source files.\n')
    expect(result.stderr).toBe('')
  })
  it('rejects a same-length content mutation by its original hash', async () => {
    const f = await fixture(),
      raw = await readFile(f.leaf)
    raw[0] ^= 1
    await writeFile(f.leaf, raw)
    const result = execute(f.script)
    rejected(result)
    expect(result.stderr).toContain('Frozen evidence changed:')
  })
  it('rejects a missing original', async () => {
    const f = await fixture()
    await unlink(f.leaf)
    rejected(execute(f.script))
  })
  it.skipIf(process.platform === 'win32')(
    'rejects a leaf symlink before reading its target',
    async () => {
      const f = await fixture(),
        original = f.leaf + '.source'
      await rename(f.leaf, original)
      await symlink(original, f.leaf)
      const result = execute(f.script)
      rejected(result)
      expect(result.stderr).toContain('Frozen evidence is a symlink:')
    },
  )
  it.skipIf(process.platform === 'win32')('rejects an ancestor symlink', async () => {
    const f = await fixture(),
      docs = join(f.root, 'docs'),
      original = docs + '-source'
    await rename(docs, original)
    await symlink(original, docs)
    const result = execute(f.script)
    rejected(result)
    expect(result.stderr).toContain('Frozen evidence is a symlink:')
  })
  it.skipIf(process.platform === 'win32')(
    'rejects a FIFO without waiting for a writer',
    async () => {
      const f = await fixture()
      await unlink(f.leaf)
      const fifo = spawnSync('mkfifo', [f.leaf], { encoding: 'utf8', timeout: 2000 })
      expect({ code: fifo.status, error: fifo.error }).toEqual({ code: 0, error: undefined })
      const result = execute(f.script)
      rejected(result)
      expect(result.stderr).toContain('Frozen evidence is not a regular file:')
    },
  )
})
