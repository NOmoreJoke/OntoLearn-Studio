// CLI-only compilation of the exact candidate modules; does not start any app.
import { createRequire } from 'node:module'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'

if (
  process.platform !== 'linux' ||
  process.getuid() !== 1110 ||
  process.env.T10_ISOLATED_NATIVE !== '1'
) {
  throw new Error('ISOLATED_LINUX_REQUIRED')
}
const root = resolve('/opt/t10')
const ts = createRequire(resolve(root, 'package.json'))('typescript')
const output = resolve(root, 'build/t10-native-runtime')
await mkdir(output, { recursive: true })
const modules = [
  ['apps/desktop/src/csp.ts', 'csp.cjs'],
  ['apps/desktop/src/renderer/src/transfer/report.ts', 'report.cjs'],
  ['apps/desktop/src/main/project-transfer/prepared-report-file.ts', 'prepared-report-file.cjs'],
]
const hashes = {}
for (const [source, target] of modules) {
  const original = await readFile(resolve(root, source), 'utf8')
  hashes[source] = createHash('sha256').update(original).digest('hex')
  const rewritten = original
    .replace("'../../../csp'", "'./csp.cjs'")
    .replace("'../../renderer/src/transfer/report'", "'./report.cjs'")
  const result = ts.transpileModule(rewritten, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  })
  await writeFile(resolve(output, target), result.outputText)
}
await writeFile('/opt/t10-evidence/compiled-sources.json', JSON.stringify(hashes, null, 2) + '\n')
