import { readFileSync } from 'node:fs'
import * as fs from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  PreparedHtmlReportFile,
  type MainReportDestinationPicker,
  type ReportFileCheckpoint,
} from '../../apps/desktop/src/main/project-transfer/prepared-report-file'
import { renderPreparedReport } from '../../apps/desktop/src/renderer/src/transfer/report'

// Ordinary operations use real Node fs. Named fault tests override link acknowledgements
// and one real directory handle's sync; native chooser/OS failure claims are not inferred.
vi.mock('node:fs/promises', async (original) => {
  const actual = await original<typeof import('node:fs/promises')>()
  return { ...actual, link: vi.fn(actual.link), open: vi.fn(actual.open) }
})
const actualFs = await vi.importActual<typeof fs>('node:fs/promises')

const input = () =>
  JSON.parse(
    readFileSync(new URL('../fixtures/transfer/report-input.json', import.meta.url), 'utf8'),
  )
const pick =
  (selection: unknown): MainReportDestinationPicker =>
  async () =>
    selection as Awaited<ReturnType<MainReportDestinationPicker>>

describe('T10 real filesystem publication of one immutable prepared report', () => {
  let directory: string
  const selection = () => pick({ directory, filename: '学习报告.html' })
  const target = () => join(directory, '学习报告.html')
  const stageRoot = async () => {
    const name = (await fs.readdir(directory)).find((name) => name.startsWith('.ontolearn-report-'))
    if (!name) throw new Error('TEST_STAGING_MISSING')
    return join(directory, name)
  }

  beforeEach(async () => {
    directory = await fs.mkdtemp(join(tmpdir(), 'ontolearn-t10-report-'))
  })
  afterEach(async () => {
    vi.mocked(fs.link).mockReset().mockImplementation(actualFs.link)
    vi.mocked(fs.open).mockReset().mockImplementation(actualFs.open)
    vi.restoreAllMocks()
    await fs.chmod(directory, 0o700)
    await fs.rm(directory, { recursive: true, force: true })
  })

  it('publishes exact immutable UTF-8 bytes and metadata, with no temporary files left', async () => {
    const report = input()
    const expected = Buffer.from(renderPreparedReport(report), 'utf8')
    const artifact = new PreparedHtmlReportFile(report)
    report.title = 'mutated after preparation'
    report.goals = ['must not enter prepared artifact']
    expect(artifact.metadata).toEqual({
      sha256: createHash('sha256').update(expected).digest('hex'),
      byteLength: expected.length,
    })
    expect(() => Object.assign(artifact.metadata, { sha256: 'changed' })).toThrow()
    expect(() => Object.assign(artifact, { metadata: { sha256: 'changed' } })).toThrow()
    const result = await artifact.save(selection())
    expect(result).toMatchObject({ state: 'published', ...artifact.metadata, cleanup: 'complete' })
    expect(await fs.readFile(target())).toEqual(expected)
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
    if (process.platform !== 'win32') expect((await fs.stat(target())).mode & 0o777).toBe(0o600)
    expect(await artifact.save(selection())).toEqual({
      state: 'failed',
      code: 'REPORT_ALREADY_PUBLISHED',
      cleanup: 'complete',
    })
  })

  it('validates the report before destination selection or IO', () => {
    expect(() => new PreparedHtmlReportFile({ apiKey: 'synthetic-secret' })).toThrow(
      /^REPORT_PROJECTION_INVALID$/,
    )
  })

  it('cancels before or in the native-picker adapter without filesystem effects', async () => {
    let called = false
    const abort = new AbortController()
    abort.abort()
    const artifact = new PreparedHtmlReportFile(input())
    expect(
      await artifact.save(
        async () => {
          called = true
          return null
        },
        { signal: abort.signal },
      ),
    ).toEqual({ state: 'cancelled', cleanup: 'complete' })
    expect(called).toBe(false)
    expect(await artifact.save(pick(null))).toEqual({ state: 'cancelled', cleanup: 'complete' })
    expect(await fs.readdir(directory)).toEqual([])
  })

  for (const filename of [
    '../outside.html',
    'a/b.html',
    'a\\b.html',
    'CON.html',
    'con .html',
    'LPT1.extra.html',
    'report.html.',
    'report.txt',
    'report\0.html',
    'report\n.html',
    'a:b.html',
    '   .html',
  ]) {
    it(`rejects a nonportable or unsafe chosen basename ${JSON.stringify(filename)}`, async () => {
      const artifact = new PreparedHtmlReportFile(input())
      expect(await artifact.save(pick({ directory, filename }))).toEqual({
        state: 'failed',
        code: 'REPORT_DESTINATION_INVALID',
        cleanup: 'complete',
      })
      expect(await fs.readdir(directory)).toEqual([])
    })
  }

  it('rejects relative directories and unrecognized picker fields', async () => {
    for (const value of [
      { directory: '.', filename: 'report.html' },
      { directory: `${directory}\0private`, filename: 'report.html' },
      { directory, filename: 'report.html', overwrite: true },
    ]) {
      expect(await new PreparedHtmlReportFile(input()).save(pick(value))).toEqual({
        state: 'failed',
        code: 'REPORT_DESTINATION_INVALID',
        cleanup: 'complete',
      })
    }
    expect(await fs.readdir(directory)).toEqual([])
  })

  it('refuses to replace an existing file or directory', async () => {
    await fs.writeFile(target(), 'existing user file')
    const artifact = new PreparedHtmlReportFile(input())
    expect(await artifact.save(selection())).toEqual({
      state: 'failed',
      code: 'REPORT_TARGET_EXISTS',
      cleanup: 'complete',
    })
    expect(await fs.readFile(target(), 'utf8')).toBe('existing user file')
    await fs.unlink(target())
    await fs.mkdir(target())
    expect(await artifact.save(selection())).toEqual({
      state: 'failed',
      code: 'REPORT_TARGET_EXISTS',
      cleanup: 'complete',
    })
    expect((await fs.stat(target())).isDirectory()).toBe(true)
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  it.skipIf(process.platform === 'win32')(
    'does not follow or replace a final symlink',
    async () => {
      const other = join(directory, 'other.txt')
      await fs.writeFile(other, 'preserve other file')
      await fs.symlink(other, target())
      expect(await new PreparedHtmlReportFile(input()).save(selection())).toEqual({
        state: 'failed',
        code: 'REPORT_TARGET_EXISTS',
        cleanup: 'complete',
      })
      expect(await fs.readlink(target())).toBe(other)
      expect(await fs.readFile(other, 'utf8')).toBe('preserve other file')
    },
  )

  it('does not overwrite a winner created after the picker returned', async () => {
    const result = await new PreparedHtmlReportFile(input()).save(selection(), {
      checkpoint: async (phase) => {
        if (phase === 'before-publication') await fs.writeFile(target(), 'racing writer')
      },
    })
    expect(result).toEqual({ state: 'failed', code: 'REPORT_TARGET_EXISTS', cleanup: 'complete' })
    expect(await fs.readFile(target(), 'utf8')).toBe('racing writer')
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  const beforePublication: ReportFileCheckpoint[] = [
    'temporary-created',
    'written',
    'file-synced',
    'before-publication',
  ]
  for (const phase of beforePublication) {
    it(`cancels at ${phase} with no published/partial output`, async () => {
      const abort = new AbortController()
      const result = await new PreparedHtmlReportFile(input()).save(selection(), {
        signal: abort.signal,
        checkpoint: (current) => {
          if (current === phase) abort.abort()
        },
      })
      expect(result).toEqual({ state: 'cancelled', cleanup: 'complete' })
      expect(await fs.readdir(directory)).toEqual([])
    })
    it(`fails at ${phase} without publishing or exposing the source exception`, async () => {
      const result = await new PreparedHtmlReportFile(input()).save(selection(), {
        checkpoint: (current) => {
          if (current === phase) throw new Error('synthetic-sensitive-diagnostic')
        },
      })
      expect(result).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'complete' })
      expect(await fs.readdir(directory)).toEqual([])
    })
  }

  it('keeps a storage failure distinct from a coincident cancellation', async () => {
    const abort = new AbortController()
    const result = await new PreparedHtmlReportFile(input()).save(selection(), {
      signal: abort.signal,
      checkpoint: (phase) => {
        if (phase === 'written') {
          abort.abort()
          throw Object.assign(new Error('synthetic disk failure'), { code: 'ENOSPC' })
        }
      },
    })
    expect(result).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'complete' })
    expect(await fs.readdir(directory)).toEqual([])
  })

  for (const phase of ['link-completed', 'published'] as const) {
    it(`reconciles actual publication when acknowledgement is lost at ${phase}`, async () => {
      const report = input()
      const artifact = new PreparedHtmlReportFile(report)
      const result = await artifact.save(selection(), {
        checkpoint: (current) => {
          if (current === phase) throw new Error('synthetic lost acknowledgement')
        },
      })
      expect(result).toMatchObject({
        state: 'published',
        postPublicationError: true,
        cleanup: 'complete',
      })
      expect(await fs.readFile(target(), 'utf8')).toBe(renderPreparedReport(report))
      expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
      expect((await artifact.save(selection())).state).toBe('failed')
    })
  }

  it('does not call a completed publication cancelled', async () => {
    const abort = new AbortController()
    const result = await new PreparedHtmlReportFile(input()).save(selection(), {
      signal: abort.signal,
      checkpoint: (phase) => {
        if (phase === 'published') abort.abort()
      },
    })
    expect(result).toMatchObject({ state: 'published', cleanup: 'complete' })
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  it('does not reinterpret a post-link EEXIST hook failure as a target collision', async () => {
    const artifact = new PreparedHtmlReportFile(input())
    const result = await artifact.save(selection(), {
      checkpoint: (phase) => {
        if (phase === 'link-completed') {
          throw Object.assign(new Error('synthetic callback error'), { code: 'EEXIST' })
        }
      },
    })
    expect(result).toMatchObject({
      state: 'published',
      postPublicationError: true,
      cleanup: 'complete',
    })
    expect(await artifact.save(pick({ directory, filename: 'second.html' }))).toEqual({
      state: 'failed',
      code: 'REPORT_ALREADY_PUBLISHED',
      cleanup: 'complete',
    })
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  it('reads back the real inode after the link operation rejects with an ambiguous IO response', async () => {
    vi.mocked(fs.link).mockImplementationOnce(async (source, destination) => {
      await actualFs.link(source, destination)
      throw Object.assign(new Error('synthetic IO acknowledgement loss'), { code: 'EIO' })
    })
    const result = await new PreparedHtmlReportFile(input()).save(selection())
    expect(result).toMatchObject({
      state: 'published',
      postPublicationError: true,
      cleanup: 'complete',
    })
    expect(await fs.readFile(target(), 'utf8')).toBe(renderPreparedReport(input()))
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  it('preserves a published result when directory durability cannot be confirmed', async () => {
    const parent = await fs.realpath(directory)
    let injected = 0
    vi.mocked(fs.open).mockImplementation(async (path, flags, mode) => {
      const handle = await actualFs.open(path, flags, mode)
      if (path === parent) {
        injected++
        vi.spyOn(handle, 'sync').mockRejectedValueOnce(
          Object.assign(new Error('synthetic unsupported directory sync'), { code: 'ENOTSUP' }),
        )
      }
      return handle
    })
    const result = await new PreparedHtmlReportFile(input()).save(selection())
    expect(injected).toBe(1)
    expect(result).toMatchObject({
      state: 'published',
      durability: 'unconfirmed',
      postPublicationError: true,
      cleanup: 'complete',
    })
    expect(await fs.readFile(target(), 'utf8')).toBe(renderPreparedReport(input()))
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  it('bounds concurrent saves to one picker and one artifact', async () => {
    let finish!: (value: null) => void
    let calls = 0
    const artifact = new PreparedHtmlReportFile(input())
    const first = artifact.save(
      () =>
        new Promise((resolve) => {
          finish = resolve
        }),
    )
    const second = await artifact.save(async () => {
      calls++
      return null
    })
    expect(second).toEqual({ state: 'failed', code: 'REPORT_EXPORT_BUSY', cleanup: 'complete' })
    expect(calls).toBe(0)
    finish(null)
    expect(await first).toEqual({ state: 'cancelled', cleanup: 'complete' })
    expect(await fs.readdir(directory)).toEqual([])
  })

  it('keeps unrecognized files during cleanup and refuses unlimited retry staging', async () => {
    const artifact = new PreparedHtmlReportFile(input())
    let root = ''
    const result = await artifact.save(selection(), {
      checkpoint: async (phase) => {
        if (phase === 'written') {
          root = await stageRoot()
          await fs.writeFile(join(root, 'foreign.txt'), 'do not recursively erase')
          throw new Error('synthetic failure')
        }
      },
    })
    expect(result).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'pending' })
    expect(await fs.readFile(join(root, 'foreign.txt'), 'utf8')).toBe('do not recursively erase')
    expect(await artifact.save(selection())).toEqual({
      state: 'failed',
      code: 'REPORT_CLEANUP_PENDING',
      cleanup: 'pending',
    })
    expect(await artifact.retryCleanup()).toBe('pending')
    await fs.unlink(join(root, 'foreign.txt')) // Test removes only its own injected file.
    expect(await Promise.all([artifact.retryCleanup(), artifact.retryCleanup()])).toEqual([
      'complete',
      'complete',
    ])
    expect(await fs.readdir(directory)).toEqual([])
    expect((await artifact.save(selection())).state).toBe('published')
  })

  it.skipIf(process.platform === 'win32')(
    'rejects a replaced staging file without following it',
    async () => {
      const other = join(directory, 'other.txt')
      await fs.writeFile(other, 'not this report')
      const result = await new PreparedHtmlReportFile(input()).save(selection(), {
        checkpoint: async (phase) => {
          if (phase === 'before-publication') {
            const root = await stageRoot()
            await fs.unlink(join(root, 'report.html'))
            await fs.symlink(other, join(root, 'report.html'))
          }
        },
      })
      expect(result).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'pending' })
      await expect(fs.lstat(target())).rejects.toMatchObject({ code: 'ENOENT' })
      expect(await fs.readFile(other, 'utf8')).toBe('not this report')
    },
  )

  for (const sameLength of [false, true]) {
    it(`rejects in-place staging mutation even with the same inode, sameLength=${sameLength}`, async () => {
      const artifact = new PreparedHtmlReportFile(input())
      const result = await artifact.save(selection(), {
        checkpoint: async (phase) => {
          if (phase === 'before-publication') {
            const file = join(await stageRoot(), 'report.html')
            const original = await fs.readFile(file)
            const changed = sameLength
              ? Buffer.from(original)
              : Buffer.from('<script>changed</script>')
            if (sameLength) changed[0] ^= 1
            await fs.writeFile(file, changed)
          }
        },
      })
      expect(result).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'complete' })
      expect(await fs.readdir(directory)).toEqual([])
    })
  }

  it('reports actual pending cleanup on repeated calls after successful publication', async () => {
    const artifact = new PreparedHtmlReportFile(input())
    let foreign = ''
    const result = await artifact.save(selection(), {
      checkpoint: async (phase) => {
        if (phase === 'published') {
          foreign = join(await stageRoot(), 'foreign.txt')
          await fs.writeFile(foreign, 'keep this file')
        }
      },
    })
    expect(result).toMatchObject({ state: 'published', cleanup: 'pending' })
    expect(await artifact.save(selection())).toEqual({
      state: 'failed',
      code: 'REPORT_ALREADY_PUBLISHED',
      cleanup: 'pending',
    })
    expect(await fs.readFile(foreign, 'utf8')).toBe('keep this file')
    await fs.unlink(foreign)
    expect(await artifact.retryCleanup()).toBe('complete')
    expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
  })

  it('does not execute or expose a thrown error code accessor', async () => {
    let invoked = false
    const error = Object.defineProperty({}, 'code', {
      get() {
        invoked = true
        throw new Error('synthetic-sensitive-diagnostic')
      },
    })
    const result = await new PreparedHtmlReportFile(input()).save(async () => {
      throw error
    })
    expect(result).toEqual({ state: 'failed', code: 'REPORT_EXPORT_FAILED', cleanup: 'complete' })
    expect(invoked).toBe(false)
    expect(await fs.readdir(directory)).toEqual([])
  })

  it.skipIf(process.platform === 'win32')(
    'holds an unreadable publication uncertain until actual readback',
    async () => {
      const artifact = new PreparedHtmlReportFile(input())
      vi.mocked(fs.link).mockImplementationOnce(async (source, destination) => {
        await actualFs.link(source, destination)
        await fs.chmod(directory, 0o000)
        throw Object.assign(
          new Error('synthetic lost acknowledgement and inaccessible directory'),
          {
            code: 'EIO',
          },
        )
      })
      const result = await artifact.save(selection())
      try {
        expect(result).toMatchObject({ state: 'publication-unconfirmed', cleanup: 'pending' })
        expect(await artifact.reconcilePublication()).toBe('unconfirmed')
        expect(await artifact.save(selection())).toEqual({
          state: 'failed',
          code: 'REPORT_PUBLICATION_UNCONFIRMED',
          cleanup: 'pending',
        })
      } finally {
        await fs.chmod(directory, 0o700)
      }
      expect(await artifact.reconcilePublication()).toBe('published')
      expect(await artifact.retryCleanup()).toBe('complete')
      expect(await fs.readFile(target(), 'utf8')).toBe(renderPreparedReport(input()))
      expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
    },
  )

  it.skipIf(process.platform === 'win32')(
    'allows an explicit retry only after unknown publication reads back absent and cleanup finishes',
    async () => {
      const artifact = new PreparedHtmlReportFile(input())
      vi.mocked(fs.link).mockImplementationOnce(async () => {
        await fs.chmod(directory, 0o000)
        throw Object.assign(new Error('synthetic IO failure before link outcome was returned'), {
          code: 'EIO',
        })
      })
      const result = await artifact.save(selection())
      expect(result).toMatchObject({ state: 'publication-unconfirmed', cleanup: 'pending' })
      await fs.chmod(directory, 0o700)
      expect(await artifact.reconcilePublication()).toBe('not-present')
      expect(await artifact.save(selection())).toEqual({
        state: 'failed',
        code: 'REPORT_CLEANUP_PENDING',
        cleanup: 'pending',
      })
      expect(await artifact.retryCleanup()).toBe('complete')
      expect((await artifact.save(selection())).state).toBe('published')
      expect(await fs.readdir(directory)).toEqual(['学习报告.html'])
    },
  )
})
