import { afterEach, describe, expect, it, vi } from 'vitest'
import * as fs from 'node:fs'
import {
  mkdtempSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  renameSync,
  rmSync,
  symlinkSync,
  writeFileSync,
  existsSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { randomUUID } from 'node:crypto'
import {
  LibraryLocationConfig,
  LibraryLocationService,
  verifyLibraryLocator,
} from '../../apps/desktop/src/main/library-location-service'
const fsFault = vi.hoisted(() => ({ directoryFsync: false }))
vi.mock('node:fs', async (importOriginal) => {
  const actual = await importOriginal<typeof import('node:fs')>()
  return {
    ...actual,
    fsyncSync: (fd: number) => {
      if (fsFault.directoryFsync && actual.fstatSync(fd).isDirectory())
        throw new Error('directory durability unknown')
      actual.fsyncSync(fd)
    },
  }
})
const roots: string[] = []
function fixture() {
  const root = realpathSync(mkdtempSync(join(tmpdir(), 'b1a-library-')))
  roots.push(root)
  const current = join(root, 'current'),
    target = join(root, 'target')
  mkdirSync(current)
  mkdirSync(target)
  const original = join(current, 'engine.sqlite'),
    configPath = join(current, 'library-location.json')
  writeFileSync(original, 'original library is not overwritten')
  const config = new LibraryLocationConfig(configPath, original)
  config.completeStartup('library-1')
  const deps = {
    pick: vi.fn(async () => target as string | null),
    hasUnresolvedResponsibility: vi.fn(() => false),
    status: vi.fn(async () => ({ libraryEvidenceRef: 'library-1', activeJobs: 0 })),
    freezeAdmission: vi.fn(),
    unfreezeAdmission: vi.fn(),
    stopAndWait: vi.fn(async () => {}),
    relaunch: vi.fn(),
  }
  const service = new LibraryLocationService(config, deps),
    doc = {},
    nonce = randomUUID()
  service.reportWorkspace(
    { documentNonce: nonce, generation: 1, dirty: false, unresolved: false },
    doc,
  )
  const choose = async () => {
    const choice = await service.choose({ intent: 'create' })
    if (!choice.ok || !choice.data) throw new Error('fixture choose failed')
    return { choiceRef: choice.data.choiceRef, documentNonce: nonce, workspaceGeneration: 1 }
  }
  return { root, original, target, configPath, config, deps, service, doc, nonce, choose }
}
afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
  fsFault.directoryFsync = false
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true })
})
describe('B1a native location authority and journal', () => {
  it('picker cancellation writes no configuration or target and cannot pass a renderer path', async () => {
    const f = fixture(),
      before = readFileSync(f.configPath)
    f.deps.pick.mockResolvedValue(null)
    expect(await f.service.choose({ intent: 'create' })).toEqual({ ok: true, data: null })
    expect(await f.service.choose({ intent: 'create', path: f.target } as never)).toMatchObject({
      ok: false,
    })
    expect(readFileSync(f.configPath)).toEqual(before)
    expect(existsSync(join(f.target, 'engine.sqlite'))).toBe(false)
  })
  it('rejects dirty/unknown editors, stale document/generation, and all-library jobs before shutdown', async () => {
    const f = fixture(),
      args = await f.choose()
    f.service.reportWorkspace(
      { documentNonce: f.nonce, generation: 2, dirty: true, unresolved: false },
      f.doc,
    )
    expect(
      await f.service.switchLocation({ ...args, workspaceGeneration: 2 }, f.doc),
    ).toMatchObject({ ok: false })
    f.service.reportWorkspace(
      { documentNonce: f.nonce, generation: 3, dirty: false, unresolved: true },
      f.doc,
    )
    expect(
      await f.service.switchLocation({ ...args, workspaceGeneration: 3 }, f.doc),
    ).toMatchObject({ ok: false })
    f.service.reportWorkspace(
      { documentNonce: f.nonce, generation: 4, dirty: false, unresolved: false },
      f.doc,
    )
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(await f.service.switchLocation({ ...args, workspaceGeneration: 4 }, {})).toMatchObject({
      ok: false,
    })
    f.deps.status.mockResolvedValue({ libraryEvidenceRef: 'library-1', activeJobs: 1 })
    expect(
      await f.service.switchLocation({ ...args, workspaceGeneration: 4 }, f.doc),
    ).toMatchObject({ ok: false })
    expect(f.deps.stopAndWait).not.toHaveBeenCalled()
    expect(f.config.pending).toBe(false)
    expect(f.service.switching).toBe(false)
  })
  it('refuses host retired responsibility without querying or cancelling jobs', async () => {
    const f = fixture(),
      args = await f.choose()
    f.deps.hasUnresolvedResponsibility.mockReturnValue(true)
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(f.deps.status).not.toHaveBeenCalled()
    expect(f.deps.stopAndWait).not.toHaveBeenCalled()
  })
  it('persists prepared before closing and refuses relaunch when close times out', async () => {
    const f = fixture(),
      args = await f.choose()
    f.deps.stopAndWait.mockImplementation(async () => {
      expect(JSON.parse(readFileSync(f.configPath, 'utf8')).pending.phase).toBe('prepared')
      throw new Error('close timeout')
    })
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(f.service.switching).toBe(true)
    expect(f.deps.relaunch).not.toHaveBeenCalled()
    const restarted = new LibraryLocationConfig(f.configPath, f.original)
    expect(restarted.needsRecovery).toBe(true)
    expect(() => restarted.prepareStartupFile()).toThrow()
    expect(restarted.active.path).toBe(f.original)
    expect(readFileSync(f.original, 'utf8')).toBe('original library is not overwritten')
  })
  it('switches only after close and exclusive new-file reservation, preserving original bytes', async () => {
    vi.useFakeTimers()
    const f = fixture(),
      args = await f.choose()
    expect(await f.service.switchLocation(args, f.doc)).toEqual({
      ok: true,
      data: { restartRequested: true },
    })
    expect(f.deps.stopAndWait).toHaveBeenCalledOnce()
    expect(existsSync(join(f.target, 'engine.sqlite'))).toBe(false)
    await vi.advanceTimersByTimeAsync(50)
    expect(f.deps.relaunch).toHaveBeenCalledOnce()
    const restarted = new LibraryLocationConfig(f.configPath, f.original),
      selected = restarted.prepareStartupFile()
    expect(selected.path).toBe(join(f.target, 'engine.sqlite'))
    expect(selected.file).not.toBeNull()
    expect(readFileSync(selected.path).length).toBe(0)
    restarted.completeStartup('library-2')
    expect(restarted.libraryId).toBe('library-2')
    expect(restarted.pending).toBe(false)
    expect(readFileSync(f.original, 'utf8')).toBe('original library is not overwritten')
  })
  it('rejects raced-in target files, symlink choices, and same-library aliases', async () => {
    const f = fixture(),
      args = await f.choose()
    writeFileSync(join(f.target, 'engine.sqlite'), 'unrelated data')
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(f.deps.stopAndWait).not.toHaveBeenCalled()
    expect(readFileSync(join(f.target, 'engine.sqlite'), 'utf8')).toBe('unrelated data')
    f.deps.pick.mockResolvedValue(f.original)
    expect(await f.service.choose({ intent: 'open' })).toMatchObject({ ok: false })
    if (process.platform !== 'win32') {
      const alias = join(f.root, 'alias.sqlite')
      symlinkSync(f.original, alias)
      f.deps.pick.mockResolvedValue(alias)
      expect(await f.service.choose({ intent: 'open' })).toMatchObject({ ok: false })
    }
  })
  it('rejects file identity replacement and corrupt config instead of falling back', () => {
    const f = fixture(),
      locator = f.config.active
    renameSync(f.original, f.original + '.old')
    writeFileSync(f.original, 'replacement')
    expect(() => verifyLibraryLocator(locator)).toThrow()
    writeFileSync(f.configPath, '{broken')
    expect(() => new LibraryLocationConfig(f.configPath, f.original)).toThrow()
  })
  it('invalidated document cannot authorize the second check after status resolves', async () => {
    const f = fixture(),
      args = await f.choose()
    f.deps.status.mockImplementation(async () => {
      f.service.invalidateDocument(f.doc)
      return { libraryEvidenceRef: 'library-1', activeJobs: 0 }
    })
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(f.config.pending).toBe(false)
    expect(f.deps.stopAndWait).not.toHaveBeenCalled()
  })
  it('retains the switch fence when config rename succeeded but directory fsync failed', async () => {
    if (process.platform === 'win32') return // POSIX directory fsync branch only.
    const f = fixture(),
      args = await f.choose()
    fsFault.directoryFsync = true
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(f.config.pending).toBe(true)
    expect(f.service.switching).toBe(true)
    expect(f.deps.unfreezeAdmission).not.toHaveBeenCalled()
    expect(f.deps.stopAndWait).not.toHaveBeenCalled()
    expect(new LibraryLocationConfig(f.configPath, f.original).needsRecovery).toBe(true)
  })
  it('rejects a replaced parent directory and hardlinked database aliases', async () => {
    const f = fixture(),
      args = await f.choose()
    renameSync(f.target, f.target + '.old')
    mkdirSync(f.target)
    expect(await f.service.switchLocation(args, f.doc)).toMatchObject({ ok: false })
    expect(f.deps.stopAndWait).not.toHaveBeenCalled()
    const foreign = join(f.target, 'foreign.sqlite'),
      alias = join(f.target, 'alias.sqlite')
    writeFileSync(foreign, 'other database')
    fs.linkSync(foreign, alias)
    f.deps.pick.mockResolvedValue(alias)
    expect(await f.service.choose({ intent: 'open' })).toMatchObject({ ok: false })
  })
  it('cannot replace an unsafe report at the same generation with a clean report', () => {
    const f = fixture()
    expect(
      f.service.reportWorkspace(
        { documentNonce: f.nonce, generation: 2, dirty: true, unresolved: false },
        f.doc,
      ),
    ).toMatchObject({ ok: true })
    expect(
      f.service.reportWorkspace(
        { documentNonce: f.nonce, generation: 2, dirty: false, unresolved: false },
        f.doc,
      ),
    ).toMatchObject({ ok: false })
  })
  it('rejects duplicate-key and oversized config without manufacturing a default selection', () => {
    const f = fixture(),
      original = readFileSync(f.configPath, 'utf8')
    writeFileSync(f.configPath, original.replace('{', '{"version":1,'))
    expect(() => new LibraryLocationConfig(f.configPath, f.original)).toThrow()
    writeFileSync(f.configPath, ' '.repeat(65537))
    expect(() => new LibraryLocationConfig(f.configPath, f.original)).toThrow()
  })
  it('opening a zero-byte or non-SQLite existing file cannot initialize a new library', async () => {
    const f = fixture(),
      empty = join(f.target, 'empty.sqlite')
    writeFileSync(empty, '')
    f.deps.pick.mockResolvedValue(empty)
    expect(await f.service.choose({ intent: 'open' })).toMatchObject({ ok: false })
    writeFileSync(empty, 'this is not a sqlite database')
    expect(await f.service.choose({ intent: 'open' })).toMatchObject({ ok: false })
    expect(readFileSync(empty, 'utf8')).toBe('this is not a sqlite database')
  })
})
