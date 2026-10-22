// Reviewer-local: exact diff between the archived browser artifact and a fresh render
// from the current frozen source. Read-only.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { describe, expect, it } from 'vitest'
import { renderPreparedReport } from '../../../../apps/desktop/src/renderer/src/transfer/report'

const root = new URL('../../../../', import.meta.url)
const read = (p: string) => readFileSync(new URL(p, root), 'utf8')
const digest = (b: Buffer | string) => createHash('sha256').update(b).digest('hex')

const archived = read('docs/reviews/T10/evidence/legacy-raw-archive/report-file-runtime/published-report.html')
const input = JSON.parse(read('tests/fixtures/transfer/report-input.json'))
const attacks: string[] = JSON.parse(read('tests/fixtures/transfer/malicious-texts.json'))
input.goals = attacks
const current = renderPreparedReport(input)

describe('reviewer: archived browser artifact vs current source render', () => {
  it('prints the first differing region', () => {
    console.log('archived bytes :', Buffer.byteLength(archived), digest(archived))
    console.log('current  bytes :', Buffer.byteLength(current), digest(current))
    const a = archived.split('\n')
    const c = current.split('\n')
    console.log('archived lines :', a.length, ' current lines :', c.length)
    const max = Math.max(a.length, c.length)
    let shown = 0
    for (let i = 0; i < max && shown < 6; i++) {
      if (a[i] !== c[i]) {
        console.log(`--- line ${i} differs ---`)
        console.log('ARCHIVED:', JSON.stringify(a[i]))
        console.log('CURRENT :', JSON.stringify(c[i]))
        shown++
      }
    }
    expect(digest(archived)).not.toBe(digest(current))
  })

  it('tries the render-probe variant (title replaced by attacks[0])', () => {
    const probe = JSON.parse(read('tests/fixtures/transfer/report-input.json'))
    probe.goals = attacks
    probe.title = attacks[0]
    const html = renderPreparedReport(probe)
    console.log('probe variant bytes :', Buffer.byteLength(html), digest(html))
    console.log('archived bytes      :', Buffer.byteLength(archived), digest(archived))
  })
})
