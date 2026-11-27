import { createHash } from 'node:crypto'
import { mkdir, readFile, realpath, writeFile } from 'node:fs/promises'
import path from 'node:path'
import ts from 'typescript'

const argument = process.argv.indexOf('--source-root')
const sourceRoot = await realpath(
  argument < 0 ? new URL('../../', import.meta.url) : process.argv[argument + 1],
)
const destination = new URL('./out/', import.meta.url)
await mkdir(destination, { recursive: true })
await mkdir(new URL('snapshot/', destination), { recursive: true })
const names = [
  'policy',
  'credentials',
  'electron-safe-storage',
  'private-directory',
  'ciphertext-repository',
  'persistent-audit',
  'await-boundary',
  'transport',
  'gateway',
]
const snapshot = await Promise.all(
  names.map(async (name) => {
    const relative = `apps/desktop/src/main/model-gateway/${name}.ts`
    return { name, relative, source: await readFile(path.join(sourceRoot, relative), 'utf8') }
  }),
)
const manifest = {}
for (const item of snapshot) {
  // A source edit while capturing this boundary invalidates the snapshot, not its hash.
  if ((await readFile(path.join(sourceRoot, item.relative), 'utf8')) !== item.source)
    throw new Error('source changed during isolated snapshot; capture again')
  const compiled = ts.transpileModule(item.source, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      esModuleInterop: true,
    },
  }).outputText
  manifest[item.relative] = {
    sourceSha256: createHash('sha256').update(item.source).digest('hex'),
    compiledSha256: createHash('sha256').update(compiled).digest('hex'),
  }
  await writeFile(new URL(`${item.name}.js`, destination), compiled)
  await writeFile(new URL(`snapshot/${item.name}.ts`, destination), item.source)
}
await writeFile(new URL('package.json', destination), JSON.stringify({ type: 'commonjs' }))
await writeFile(new URL('sources.json', destination), JSON.stringify(manifest, null, 2) + '\n')
console.log('Prepared explicit-source-root combination snapshot with per-file hashes')
