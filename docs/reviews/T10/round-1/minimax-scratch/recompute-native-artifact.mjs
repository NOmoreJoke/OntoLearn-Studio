// Independent re-derivation of the attempt-3 native published artifact.
// Reproduces exactly what docs/iterations/T10/isolated/native-hook.cjs does:
//   input = report-input.json ; input.goals = malicious-texts.json
//   payload = renderPreparedReport(input)
// and compares against docs/reviews/T10/evidence/isolated-native/attempt-3/native.json
// (actualFile.sha256 / byteLength / mode) and the browser evidence separately.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { renderPreparedReport } from '../../../apps/desktop/src/renderer/src/transfer/report.ts'

const root = new URL('../../../../', import.meta.url)
const read = (p) => readFileSync(new URL(p, root), 'utf8')

const input = JSON.parse(read('tests/fixtures/transfer/report-input.json'))
const attacks = JSON.parse(read('tests/fixtures/transfer/malicious-texts.json'))
input.goals = attacks

const html = renderPreparedReport(input)
const payload = Buffer.from(html, 'utf8')
const sha256 = createHash('sha256').update(payload).digest('hex')

const native = JSON.parse(read('docs/reviews/T10/evidence/isolated-native/attempt-3/native.json'))
const browser = JSON.parse(read('docs/reviews/T10/evidence/browser-summary.json'))

console.log('--- recomputed from current frozen source ---')
console.log('byteLength :', payload.length)
console.log('sha256     :', sha256)
console.log('native actualFile.byteLength :', native.actualFile.byteLength)
console.log('native actualFile.sha256     :', native.actualFile.sha256)
console.log('native actualFile.mode       :', native.actualFile.mode, '(0o600 =', 0o600, ')')
console.log('MATCH native byteLength:', payload.length === native.actualFile.byteLength)
console.log('MATCH native sha256    :', sha256 === native.actualFile.sha256)
console.log('--- browser evidence ---')
console.log(JSON.stringify(browser, null, 2))
