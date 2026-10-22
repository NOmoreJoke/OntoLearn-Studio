// Independent byte-reproduction of archived artifacts from current frozen sources.
// Writes ONLY into the reviewer scratch directory.
import { createRequire } from 'node:module'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'
import ts from 'typescript'

const out = resolve('out/t10-review/round-1/zcode/counterexamples/build')
await mkdir(out, { recursive: true })
const cspUrl = new URL(`file://${resolve('apps/desktop/src/csp.ts')}`).href
const reportUrl = new URL(`file://${resolve('apps/desktop/src/renderer/src/transfer/report.ts')}`).href

const reportSource = (await readFile('apps/desktop/src/renderer/src/transfer/report.ts', 'utf8')).replace(
  "'../../../csp'",
  JSON.stringify(cspUrl),
)
await writeFile(resolve(out, 'report.mjs'), ts.transpileModule(reportSource, {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext },
}).outputText)
const { renderPreparedReport } = await import(new URL(`file://${resolve(out, 'report.mjs')}`).href)

const input = JSON.parse(await readFile('tests/fixtures/transfer/report-input.json', 'utf8'))
const attacks = JSON.parse(await readFile('tests/fixtures/transfer/malicious-texts.json', 'utf8'))

// Case 1: native attempt-3 input (goals=attacks, title=attacks[0] per native-hook.cjs)
const nativeInput = structuredClone(input)
nativeInput.goals = attacks
nativeInput.title = attacks[0]
const nativeHtml = renderPreparedReport(nativeInput)
const nativeInfo = {
  byteLength: Buffer.byteLength(nativeHtml, 'utf8'),
  sha256: createHash('sha256').update(nativeHtml).digest('hex'),
}
await writeFile(resolve(out, 'reproduced-native.html'), nativeHtml)

// Case 2: plain input (what the browser file-service probe most likely published)
const plainHtml = renderPreparedReport(input)
const plainInfo = {
  byteLength: Buffer.byteLength(plainHtml, 'utf8'),
  sha256: createHash('sha256').update(plainHtml).digest('hex'),
}
await writeFile(resolve(out, 'reproduced-plain.html'), plainHtml)

console.log(JSON.stringify({ nativeInfo, plainInfo }, null, 2))

const archivedNative = await readFile('docs/reviews/T10/evidence/isolated-native/attempt-3/native-report.html', 'utf8')
const archivedBrowser = await readFile('docs/reviews/T10/evidence/legacy-raw-archive/report-file-runtime/published-report.html', 'utf8')
console.log(JSON.stringify({
  nativeExactMatch: archivedNative === nativeHtml,
  browserPlainExactMatch: archivedBrowser === plainHtml,
  browserBytes: Buffer.byteLength(archivedBrowser, 'utf8'),
  plainBytes: plainInfo.byteLength,
}, null, 2))
if (archivedBrowser !== plainHtml) {
  // Show first difference region for honest reporting
  let i = 0
  while (i < Math.min(archivedBrowser.length, plainHtml.length) && archivedBrowser[i] === plainHtml[i]) i++
  console.log('browser-vs-plain first diff at', i)
  console.log('browser:', JSON.stringify(archivedBrowser.slice(Math.max(0, i - 60), i + 120)))
  console.log('plain  :', JSON.stringify(plainHtml.slice(Math.max(0, i - 60), i + 120)))
}
