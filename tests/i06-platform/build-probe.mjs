import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const root = new URL('../../', import.meta.url)
const destination = new URL('./out/', import.meta.url)
await mkdir(destination, { recursive: true })
const sources = {}
for (const name of ['policy', 'credentials', 'electron-safe-storage']) {
  const path = `apps/desktop/src/main/model-gateway/${name}.ts`
  const source = await readFile(new URL(path, root), 'utf8')
  sources[path] = createHash('sha256').update(source).digest('hex')
  const result = ts.transpileModule(source, {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
  })
  await writeFile(new URL(`${name}.js`, destination), result.outputText)
}
await writeFile(new URL('package.json', destination), JSON.stringify({ type: 'commonjs' }))
await writeFile(new URL('sources.json', destination), JSON.stringify(sources, null, 2) + '\n')
process.stdout.write(`Prepared isolated probe at ${fileURLToPath(destination)}\n`)
