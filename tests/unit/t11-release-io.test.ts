import { afterEach, describe, expect, it, vi } from 'vitest'
import * as fs from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { digest, readBound, readJsonFile, verifyLargeFile } from '../../scripts/release/verify.mjs'

vi.mock('node:fs', async (importOriginal) => {
  const original = await importOriginal<typeof import('node:fs')>()
  return {
    ...original,
    readSync: vi.fn(original.readSync),
    openSync: vi.fn(original.openSync),
    closeSync: vi.fn(original.closeSync),
  }
})
const roots: string[] = []
afterEach(() => {
  vi.restoreAllMocks()
  vi.mocked(fs.readSync).mockReset().mockImplementation(realRead)
  vi.mocked(fs.openSync).mockReset().mockImplementation(realOpen)
  vi.mocked(fs.closeSync).mockReset().mockImplementation(realClose)
  for (const root of roots.splice(0)) fs.rmSync(root, { recursive: true, force: true })
})
const realRead = vi.mocked(fs.readSync).getMockImplementation()!
const realOpen = vi.mocked(fs.openSync).getMockImplementation()!
const realClose = vi.mocked(fs.closeSync).getMockImplementation()!
function fixture(bytes: Buffer | string = '{"ok":true}') {
  const root = fs.mkdtempSync(join(tmpdir(), 't11-io-'))
  roots.push(root)
  const path = join(root, 'data')
  fs.writeFileSync(path, bytes)
  return { root, path, file: { path: 'data', sha256: digest(bytes) } }
}
function closed() {
  const fd = vi.mocked(fs.openSync).mock.results.find((r) => r.type === 'return')?.value as number
  expect(() => fs.fstatSync(fd)).toThrow()
}
describe('bounded release IO with small deterministic files', () => {
  it('reads and hashes complete bytes and closes its fd', () => {
    const { root, path, file } = fixture()
    expect(readBound(root, file).toString()).toBe('{"ok":true}')
    expect(readJsonFile(path)).toEqual({ ok: true })
    closed()
  })
  it('rejects oversized JSON before reading or parsing (sparse file, no large allocation)', () => {
    const { path } = fixture()
    fs.truncateSync(path, 16 * 1024 * 1024 + 1)
    const parse = vi.spyOn(JSON, 'parse')
    expect(() => readJsonFile(path)).toThrow('FILE_BOUNDS')
    expect(fs.readSync).not.toHaveBeenCalled()
    expect(parse).not.toHaveBeenCalled()
    closed()
  })
  it('enforces each caller bound before reading and rejects nonregular files', () => {
    const { root, file } = fixture('1234')
    expect(() => readBound(root, file, 3)).toThrow('FILE_BOUNDS')
    expect(fs.readSync).not.toHaveBeenCalled()
    expect(() => readJsonFile(root)).toThrow('FILE_BOUNDS')
    closed()
  })
  it('rejects growth during a read and closes the fd', () => {
    const { root, path, file } = fixture('abcd')
    vi.mocked(fs.readSync).mockImplementationOnce((...args: Parameters<typeof fs.readSync>) => {
      fs.appendFileSync(path, 'e')
      return realRead(...args)
    })
    expect(() => readBound(root, file)).toThrow('FILE_CHANGED')
    closed()
  })
  it('rejects truncation/short reads and closes the fd', () => {
    const { root, path, file } = fixture('abcd')
    vi.mocked(fs.readSync).mockImplementationOnce((...args: Parameters<typeof fs.readSync>) => {
      fs.truncateSync(path, 1)
      return realRead(...args)
    })
    expect(() => readBound(root, file)).toThrow('FILE_SHORT_READ')
    closed()
  })
  it('closes the fd on read exceptions and rejects wrong hashes', () => {
    const { root, file } = fixture()
    vi.mocked(fs.readSync).mockImplementationOnce(() => {
      throw new Error('TEST_IO')
    })
    expect(() => readBound(root, file)).toThrow('TEST_IO')
    closed()
    expect(() => readBound(root, { ...file, sha256: '0'.repeat(64) })).toThrow('FILE_HASH')
  })
  it('rejects outside symlinks and replacement of the resolved leaf before open', () => {
    const outside = fixture('outside'),
      inside = fixture('inside')
    fs.symlinkSync(outside.path, join(inside.root, 'link'))
    expect(() => readBound(inside.root, { path: 'link', sha256: outside.file.sha256 })).toThrow(
      'UNSAFE_PATH',
    )
    vi.mocked(fs.openSync).mockImplementationOnce((...args: Parameters<typeof fs.openSync>) => {
      fs.unlinkSync(inside.path)
      fs.symlinkSync(outside.path, inside.path)
      return realOpen(...args)
    })
    expect(() => readBound(inside.root, inside.file)).toThrow()
  })
  it('checks large-file hash and PE/DMG structures using the opened fd', () => {
    const pe = Buffer.alloc(70)
    pe.writeUInt16LE(0x5a4d)
    pe.writeUInt32LE(64, 0x3c)
    pe.writeUInt32LE(0x4550, 64)
    pe.writeUInt16LE(0x8664, 68)
    const win = fixture(pe)
    expect(verifyLargeFile(win.root, win.file, false)).toEqual({ size: 70, format: true })
    pe.writeUInt32LE(0xffffffff, 0x3c)
    fs.writeFileSync(win.path, pe)
    expect(verifyLargeFile(win.root, { ...win.file, sha256: digest(pe) }, false).format).toBe(false)
    const mac = fixture(Buffer.concat([Buffer.from('koly'), Buffer.alloc(508)]))
    expect(verifyLargeFile(mac.root, mac.file, true)).toEqual({ size: 512, format: true })
    closed()
  })
  it('rejects streaming-file growth before accepting the hash or structure', () => {
    const { root, path, file } = fixture('abcd')
    vi.mocked(fs.readSync).mockImplementationOnce((...args: Parameters<typeof fs.readSync>) => {
      fs.appendFileSync(path, 'e')
      return realRead(...args)
    })
    expect(() => verifyLargeFile(root, file, false)).toThrow('FILE_CHANGED')
    closed()
  })
})
