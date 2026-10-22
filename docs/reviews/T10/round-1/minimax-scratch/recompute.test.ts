// Reviewer-local independent re-derivation of the frozen native/browser artifacts.
// Never modifies reviewed sources, tests, fixtures or evidence.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { describe, expect, it } from 'vitest'
import { renderPreparedReport } from '../../../../apps/desktop/src/renderer/src/transfer/report'

const root = new URL('../../../../', import.meta.url)
const read = (p: string) => readFileSync(new URL(p, root), 'utf8')
const readBytes = (p: string) => readFileSync(new URL(p, root))

const input = () => JSON.parse(read('tests/fixtures/transfer/report-input.json'))
const attacks = (): string[] => JSON.parse(read('tests/fixtures/transfer/malicious-texts.json'))

const digest = (b: Buffer | string) => createHash('sha256').update(b).digest('hex')

describe('reviewer: re-derive frozen artifacts from the current frozen source', () => {
  it('native attempt-3 published file equals a fresh render of the current source', () => {
    const report = input()
    report.goals = attacks()
    const payload = Buffer.from(renderPreparedReport(report), 'utf8')
    const native = JSON.parse(
      read('docs/reviews/T10/evidence/isolated-native/attempt-3/native.json'),
    )
    console.log('recomputed byteLength :', payload.length)
    console.log('recomputed sha256     :', digest(payload))
    console.log('native   byteLength   :', native.actualFile.byteLength)
    console.log('native   sha256       :', native.actualFile.sha256)
    expect(payload.length).toBe(native.actualFile.byteLength)
    expect(digest(payload)).toBe(native.actualFile.sha256)
    expect(native.actualFile.mode).toBe(0o600)
    expect(native.save.sha256).toBe(native.actualFile.sha256)
  })

  it('archived browser artifact identity', () => {
    const archive = JSON.parse(
      read('docs/reviews/T10/evidence/legacy-raw-archive/index.json'),
    )
    const browser = archive.files['report-file-runtime/published-report.html']
    const malicious = archive.files['report-file-runtime/malicious-report.html']
    console.log('browser published-report.html :', browser.byteLength, browser.sha256)
    console.log('browser malicious-report.html :', malicious.byteLength, malicious.sha256)
    const onDisk = readBytes('docs/reviews/T10/evidence/legacy-raw-archive/report-file-runtime/published-report.html')
    expect(onDisk.length).toBe(browser.byteLength)
    expect(digest(onDisk)).toBe(browser.sha256)
    expect(malicious.sha256).toBe(browser.sha256)

    // Does the archived browser artifact still equal a render of the current source?
    const report = input()
    report.goals = attacks()
    const payload = Buffer.from(renderPreparedReport(report), 'utf8')
    console.log('current-source render length  :', payload.length)
    console.log('current-source render sha256  :', digest(payload))
    console.log('archived browser artifact      :', browser.byteLength, browser.sha256)
  })

  it('compiled postrun readback copies match the current frozen sources', () => {
    const index = JSON.parse(
      read('docs/reviews/T10/evidence/native-compiled-postrun-readback/index.json'),
    )
    console.log('compiled readback index:', JSON.stringify(index, null, 2))
    const compiled = JSON.parse(
      read('docs/reviews/T10/evidence/isolated-native/attempt-3/compiled-sources.json'),
    )
    for (const [source, sha] of Object.entries(compiled)) {
      console.log('compiled-sources', source, sha, 'current:', digest(read(source)))
    }
  })
})
