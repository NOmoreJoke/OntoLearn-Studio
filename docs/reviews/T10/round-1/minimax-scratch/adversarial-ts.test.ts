// Reviewer-local independent checks against the frozen TS candidate.
// Does not modify reviewed sources, tests, fixtures or evidence.
import { readFileSync } from 'node:fs'
import * as fs from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { describe, expect, it } from 'vitest'
import {
  escapeReportText,
  parsePreparedReport,
  renderPreparedReport,
} from '../../../../apps/desktop/src/renderer/src/transfer/report'
import { PreparedHtmlReportFile } from '../../../../apps/desktop/src/main/project-transfer/prepared-report-file'

const root = new URL('../../../../', import.meta.url)
const read = (p: string) => readFileSync(new URL(p, root), 'utf8')
const input = () => JSON.parse(read('tests/fixtures/transfer/report-input.json'))
const attacks = (): string[] => JSON.parse(read('tests/fixtures/transfer/malicious-texts.json'))

const TAG = /<\/?([a-zA-Z][a-zA-Z0-9-]*)\b[^>]*>/g

describe('reviewer: rendered report HTML structure', () => {
  it('emits only the allowlisted elements, for every attack in every field', () => {
    const allow = new Set([
      'html', 'head', 'meta', 'title', 'body', 'p', 'h1', 'h2', 'section', 'pre', 'span',
    ])
    const report = input()
    const list = attacks()
    const big = list.join('') // fits the 16_384-char text fields
    const small = list[1] // fits the 160-char id fields
    report.title = list[0]
    for (const key of [
      'goals', 'competencyQuestions', 'ontologySummary', 'dataSummary', 'assumptions', 'unresolved',
    ] as const)
      report[key] = [big]
    const attempt = report.learning[0]
    attempt.taskId = attempt.attemptId = attempt.check.evidenceRef = small
    attempt.check.summary = big
    attempt.stageOutcomes = [big]
    for (const group of [
      report.queryResults, report.validationResults, report.behaviorResults, report.scenarioComparisons,
    ])
      for (const r of group) {
        r.resultId = r.semanticsVersion = small
        r.scope = r.statusNote = r.summary = big
      }

    const html = renderPreparedReport(report)
    const tags = [...html.matchAll(TAG)]
    const names = tags.map((m) => m[1].toLowerCase())
    const unexpected = [...new Set(names)].filter((t) => !allow.has(t))
    console.log('tags used:', [...new Set(names)].sort().join(','))
    expect(unexpected).toEqual([])
    // Every attribute that survives must be one of the four static ones; no event
    // handler, no URL-bearing attribute, and no attribute may carry dynamic text.
    const attributes = new Set<string>()
    for (const match of tags) {
      for (const attr of match[0].matchAll(/([a-zA-Z-]+)\s*=/g)) attributes.add(attr[1].toLowerCase())
    }
    console.log('attributes used:', [...attributes].sort().join(','))
    expect([...attributes].sort()).toEqual(['charset', 'content', 'http-equiv', 'lang'])
    // no raw javascript: / data: URL can reach an attribute position
    expect(html).not.toMatch(/<[^>]*javascript:/i)
    expect(html).not.toMatch(/<[^>]*\son[a-z]+\s*=/i)
  })

  it('CSP meta content decodes to the production policy (no unsafe-inline, connect none)', () => {
    const html = renderPreparedReport(input())
    const meta = html.match(/<meta http-equiv="Content-Security-Policy" content="([^"]*)">/)
    expect(meta).not.toBeNull()
    const decoded = meta![1]
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
    console.log('decoded CSP:', decoded)
    expect(decoded).toContain("connect-src 'none'")
    expect(decoded).toContain("default-src 'self'")
    expect(decoded).not.toContain('unsafe-inline')
    expect(decoded).not.toContain('unsafe-eval')
    expect(decoded).not.toContain('http://')
    expect(decoded).not.toContain('https://')
    expect(decoded.split(';').map((d) => d.trim().split(' ')[0])).toEqual([
      'default-src', 'script-src', 'style-src', 'img-src', 'connect-src',
      'object-src', 'base-uri', 'frame-src', 'form-action',
    ])
  })

  it('leading LF survives inside <pre> for the last attack (raw byte check)', () => {
    const report = input()
    report.goals = attacks()
    const html = renderPreparedReport(report)
    const last = attacks()[attacks().length - 1]
    expect(last.startsWith('\n')).toBe(true)
    // the escaped payload must appear immediately after <pre><span> with no inserted text
    expect(html).toContain(`<pre><span>${escapeReportText(last)}</span></pre>`)
    // and there must be no raw LF directly between <pre> and the payload
    expect(html).not.toMatch(/<pre>\n/)
  })
})

describe('reviewer: prepared report file service, extra independent checks', () => {
  it('publishes via a same-inode hard link and removes the staging directory', async () => {
    const dir = await fs.mkdtemp(join(tmpdir(), 't10-review-'))
    try {
      let stagingInode = 0
      let stagingMode = 0
      let stagingDirMode = 0
      const artifact = new PreparedHtmlReportFile(input())
      const result = await artifact.save(
        async () => ({ directory: dir, filename: 'r.html' }),
        {
          checkpoint: async (phase) => {
            if (phase === 'before-publication') {
              const names = await fs.readdir(dir)
              const root = names.find((n) => n.startsWith('.ontolearn-report-'))!
              stagingDirMode = (await fs.stat(join(dir, root))).mode & 0o777
              const st = await fs.lstat(join(dir, root, 'report.html'))
              stagingInode = st.ino
              stagingMode = st.mode & 0o777
            }
          },
        },
      )
      expect(result.state).toBe('published')
      const published = await fs.lstat(join(dir, 'r.html'))
      console.log('staging file mode :', stagingMode.toString(8))
      console.log('staging dir mode  :', stagingDirMode.toString(8))
      console.log('published mode    :', (published.mode & 0o777).toString(8))
      console.log('staging ino       :', stagingInode, ' published ino:', published.ino)
      expect(stagingMode).toBe(0o600)
      expect(stagingDirMode).toBe(0o700)
      expect(published.ino).toBe(stagingInode) // published by hard link, not by copy
      expect(await fs.readdir(dir)).toEqual(['r.html']) // staging root removed
    } finally {
      await fs.chmod(dir, 0o700)
      await fs.rm(dir, { recursive: true, force: true })
    }
  })

  it('two independent artifacts can publish concurrently to different targets', async () => {
    const dir = await fs.mkdtemp(join(tmpdir(), 't10-review-'))
    try {
      const a = new PreparedHtmlReportFile(input())
      const b = new PreparedHtmlReportFile(input())
      const [ra, rb] = await Promise.all([
        a.save(async () => ({ directory: dir, filename: 'a.html' })),
        b.save(async () => ({ directory: dir, filename: 'b.html' })),
      ])
      console.log('concurrent results:', ra.state, rb.state)
      expect(ra.state).toBe('published')
      expect(rb.state).toBe('published')
      expect((await fs.readdir(dir)).sort()).toEqual(['a.html', 'b.html'])
    } finally {
      await fs.chmod(dir, 0o700)
      await fs.rm(dir, { recursive: true, force: true })
    }
  })

  it('a failed export leaves the artifact reusable and does not publish anything', async () => {
    const dir = await fs.mkdtemp(join(tmpdir(), 't10-review-'))
    try {
      const artifact = new PreparedHtmlReportFile(input())
      const failed = await artifact.save(
        async () => ({ directory: dir, filename: 'x.html' }),
        {
          checkpoint: (phase) => {
            if (phase === 'file-synced') throw new Error('synthetic')
          },
        },
      )
      expect(failed).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'complete' })
      expect(await fs.readdir(dir)).toEqual([])
      const again = await artifact.save(async () => ({ directory: dir, filename: 'x.html' }))
      expect(again.state).toBe('published')
    } finally {
      await fs.chmod(dir, 0o700)
      await fs.rm(dir, { recursive: true, force: true })
    }
  })

  it('does not create the destination when the picker directory does not exist', async () => {
    const dir = await fs.mkdtemp(join(tmpdir(), 't10-review-'))
    try {
      const artifact = new PreparedHtmlReportFile(input())
      const result = await artifact.save(async () => ({
        directory: join(dir, 'missing'),
        filename: 'y.html',
      }))
      console.log('missing-directory result:', JSON.stringify(result))
      expect(result.state).toBe('failed')
      expect(await fs.readdir(dir)).toEqual([])
    } finally {
      await fs.chmod(dir, 0o700)
      await fs.rm(dir, { recursive: true, force: true })
    }
  })

  it('published bytes are exactly the current render of the same projection', async () => {
    const dir = await fs.mkdtemp(join(tmpdir(), 't10-review-'))
    try {
      const projection = input()
      const artifact = new PreparedHtmlReportFile(projection)
      const result = await artifact.save(async () => ({ directory: dir, filename: 'z.html' }))
      expect(result.state).toBe('published')
      const bytes = await fs.readFile(join(dir, 'z.html'))
      const expected = Buffer.from(renderPreparedReport(projection), 'utf8')
      expect(bytes.equals(expected)).toBe(true)
      expect(createHash('sha256').update(bytes).digest('hex')).toBe(result.sha256)
      expect(bytes.length).toBe(result.byteLength)
    } finally {
      await fs.chmod(dir, 0o700)
      await fs.rm(dir, { recursive: true, force: true })
    }
  })
})
