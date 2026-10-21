import fs from 'node:fs/promises'
import syncFs from 'node:fs'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createPrivateResourceInventory } from '../../apps/desktop/src/main/security/private-resource-inventory'
import { createPrivateResourceOwner } from '../../apps/desktop/src/main/security/private-resource-owner'

const context = { processEpoch: 'process-A', profileEpoch: 'profile-A' }
const buckets = ['credentials', 'configurations', 'audit'] as const
const ids = {
  credential: '11111111-1111-4111-8111-111111111111.credential',
  orphan: '22222222-2222-4222-8222-222222222222.credential',
  configuration: '33333333-3333-4333-8333-333333333333.configuration',
  audit: '44444444-4444-4444-8444-444444444444.audit',
  pending: '.pending-123-55555555-5555-4555-8555-555555555555',
}
type Owner = ReturnType<typeof createPrivateResourceOwner>
type View = ReturnType<Owner['inspect']>
type Options = Parameters<typeof createPrivateResourceOwner>[2]
const cleanup: { base: string; owners: Owner[] }[] = []

async function fixture(options: { root?: boolean; buckets?: boolean } = {}) {
  // Fixture setup may write synthetic bytes; the observer may only read metadata.
  const created = await fs.mkdtemp(path.join(tmpdir(), 'i06-private-owner-'))
  const base = await fs.realpath(created)
  const rootPath = path.join(base, 'model-gateway-private-v1')
  const owners: Owner[] = []
  cleanup.push({ base, owners })
  if (options.root !== false) {
    await fs.mkdir(rootPath, { mode: 0o700 })
    if (options.buckets !== false)
      for (const bucket of buckets) await fs.mkdir(path.join(rootPath, bucket), { mode: 0o700 })
  }
  const inventory = createPrivateResourceInventory(context)
  function owner(settings?: Options) {
    const createdOwner = createPrivateResourceOwner(inventory, { ...context, rootPath }, settings)
    owners.push(createdOwner)
    return createdOwner
  }
  return { base, rootPath, inventory, owner }
}
async function file(root: string, bucket: (typeof buckets)[number], name: string) {
  const destination = path.join(root, bucket, name)
  await fs.writeFile(destination, 'synthetic fixture bytes; never observed as content', {
    mode: 0o600,
    flag: 'wx',
  })
  return destination
}
const named = (view: View, name: string) =>
  view.facts.filter((entry) => entry.components.at(-1) === name)
function boundary(view: View) {
  expect(view.mechanismOnly).toBe(true)
  expect(view.productionAdmission).toBe('unsupported')
  expect(view.nodeEvidence).toBe('node-observed-unfenced')
  expect(view.inventoryState).not.toBe('complete')
}
function hasRoleSubset(view: View) {
  expect([...new Set(view.facts.map((entry) => entry.role))].sort()).toEqual(
    [...buckets, 'private-root'].sort(),
  )
}

afterEach(async () => {
  vi.restoreAllMocks()
  for (const item of cleanup.splice(0)) {
    await Promise.allSettled(item.owners.map((owner) => owner.close()))
    await fs.chmod(item.base, 0o700)
    // Only the per-test synthetic fixture tree is removed.
    await fs.rm(item.base, { recursive: true, force: true })
  }
})

describe.skipIf(process.platform === 'win32')(
  'I06 real private metadata owner: POSIX fixtures',
  () => {
    it('observes the four real roles while the full inventory stays incomplete', async () => {
      const f = await fixture()
      const owner = f.owner()
      boundary(owner.inspect())
      const view = await owner.observe()
      expect(
        view.state,
        JSON.stringify({ reason: view.reason, inventoryAccepted: view.inventoryAccepted }),
      ).toBe('observed')
      expect(view.inventoryAccepted).toBe(true)
      expect(view.reservedRoot).toEqual({ rootPath: f.rootPath, basis: 'observed-parent' })
      hasRoleSubset(view)
      expect(view.unsupported).toEqual([])
      expect(view.actualUnsettled).toBe(0)
      expect(view.started).toBeGreaterThan(0)
      expect(view.settled).toBe(view.started)
      boundary(view)
      const inventory = f.inventory.inspect()
      expect(
        inventory.owners.filter((entry) => entry.status !== 'missing').map((entry) => entry.role),
      ).toEqual(['private-root', 'credentials', 'configurations', 'audit'])
      for (const role of ['profile', 'database', 'tasks', 'retirement'])
        expect(inventory.owners.find((entry) => entry.role === role)?.status).toBe('missing')
      expect(f.inventory.issueSnapshot().ok).toBe(false)
    })

    it('records actual bigint file and parent identities without opening content', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      const actual = await fs.lstat(destination, { bigint: true })
      const parent = await fs.lstat(path.dirname(destination), { bigint: true })
      const readFile = vi.spyOn(fs, 'readFile')
      const readFileSync = vi.spyOn(syncFs, 'readFileSync')
      const open = vi.spyOn(fs, 'open')
      const view = await f.owner().observe()
      expect(
        view.state,
        JSON.stringify({ reason: view.reason, inventoryAccepted: view.inventoryAccepted }),
      ).toBe('observed')
      const records = named(view, ids.credential)
      expect(records).toHaveLength(1)
      expect(records[0].identity).toEqual({
        kind: 'posix',
        volume: `v${actual.dev.toString(16)}`,
        fileId: `i${actual.ino.toString(16)}`,
        type: 'file',
        links: Number(actual.nlink),
      })
      expect(records[0].parent).toEqual({
        kind: 'posix',
        volume: `v${parent.dev.toString(16)}`,
        fileId: `i${parent.ino.toString(16)}`,
        type: 'directory',
        links: Number(parent.nlink),
      })
      // These spies call through. No file content API is replaced by a mock.
      expect(readFile).not.toHaveBeenCalled()
      expect(readFileSync).not.toHaveBeenCalled()
      expect(open).not.toHaveBeenCalled()
      boundary(view)
    })

    it('includes legal orphan records and standalone pending names in all buckets', async () => {
      const f = await fixture()
      await file(f.rootPath, 'credentials', ids.credential)
      await file(f.rootPath, 'credentials', ids.orphan)
      await file(f.rootPath, 'configurations', ids.configuration)
      await file(f.rootPath, 'audit', ids.audit)
      for (const bucket of buckets) await file(f.rootPath, bucket, ids.pending)
      const view = await f.owner().observe()
      expect(
        view.state,
        JSON.stringify({ reason: view.reason, inventoryAccepted: view.inventoryAccepted }),
      ).toBe('observed')
      expect(named(view, ids.orphan)).toHaveLength(1)
      expect(named(view, ids.pending)).toHaveLength(3)
      expect(named(view, ids.configuration)[0].role).toBe('configurations')
      expect(named(view, ids.audit)[0].role).toBe('audit')
      boundary(view)
    })

    it('recognizes a real final plus pending hardlink pair as two distinct protected names', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      await fs.link(destination, path.join(f.rootPath, 'credentials', ids.pending))
      const actual = await fs.lstat(destination, { bigint: true })
      expect(actual.nlink).toBe(2n)
      const view = await f.owner().observe()
      expect(
        view.state,
        JSON.stringify({ reason: view.reason, inventoryAccepted: view.inventoryAccepted }),
      ).toBe('observed')
      const records = view.facts.filter(
        (entry) => entry.identity?.fileId === `i${actual.ino.toString(16)}`,
      )
      expect(records).toHaveLength(2)
      expect(new Set(records.map((entry) => entry.components.at(-1)))).toEqual(
        new Set([ids.credential, ids.pending]),
      )
      expect(records.every((entry) => entry.identity?.links === 2)).toBe(true)
      boundary(view)
    })

    it('closes actual aliases across two private buckets without counting directory nlink as aliases', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      await fs.link(destination, path.join(f.rootPath, 'audit', ids.audit))
      const view = await f.owner().observe()
      expect(
        view.state,
        JSON.stringify({ reason: view.reason, inventoryAccepted: view.inventoryAccepted }),
      ).toBe('observed')
      expect(named(view, ids.credential)[0].identity?.fileId).toBe(
        named(view, ids.audit)[0].identity?.fileId,
      )
      hasRoleSubset(view)
      boundary(view)
    })

    it('rejects final plus pending with an actual third link outside the protected root', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      await fs.link(destination, path.join(f.rootPath, 'credentials', ids.pending))
      await fs.link(destination, path.join(f.base, 'external-alias'))
      expect((await fs.lstat(destination, { bigint: true })).nlink).toBe(3n)
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('alias-unknown')
      expect(named(view, ids.credential)).toHaveLength(1)
      expect(named(view, ids.pending)).toHaveLength(1)
      boundary(view)
    })

    it('rejects a real file hardlink whose other name is outside the observed root', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      await fs.link(destination, path.join(f.base, 'external-alias'))
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('alias-unknown')
      expect(named(view, ids.credential)[0].identity?.links).toBe(2)
      boundary(view)
    })

    it('retains unknown root members and their metadata instead of returning a green truncation', async () => {
      const f = await fixture()
      await fs.writeFile(path.join(f.rootPath, 'unexpected.bin'), 'synthetic', { mode: 0o600 })
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(named(view, 'unexpected.bin')).toHaveLength(1)
      expect(named(view, 'unexpected.bin')[0].role).toBe('private-root')
      boundary(view)
    })

    it('retains an unknown nested directory and cannot claim the subtree is complete', async () => {
      const f = await fixture()
      await fs.mkdir(path.join(f.rootPath, 'audit', 'unexpected-directory'), { mode: 0o700 })
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(named(view, 'unexpected-directory')[0].identity?.type).toBe('directory')
      boundary(view)
    })

    it('does not follow a real symlink into a sibling fixture directory', async () => {
      const f = await fixture()
      const outside = path.join(f.base, 'outside')
      await fs.mkdir(outside, { mode: 0o700 })
      await fs.writeFile(path.join(outside, ids.orphan), 'synthetic', { mode: 0o600 })
      await fs.symlink(outside, path.join(f.rootPath, 'escape'), 'dir')
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.unsupported.some((entry) => entry.name === 'escape')).toBe(true)
      expect(named(view, ids.orphan)).toEqual([])
      boundary(view)
    })

    it('rejects a real symlink used as the private root', async () => {
      const f = await fixture({ root: false })
      const outside = path.join(f.base, 'outside')
      await fs.mkdir(outside, { mode: 0o700 })
      await fs.symlink(outside, f.rootPath, 'dir')
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.reservedRoot).toEqual({ rootPath: f.rootPath, basis: 'unverified' })
      expect(view.facts).toEqual([])
      boundary(view)
    })

    it('reserves a genuinely missing root and never creates it while observing', async () => {
      const f = await fixture({ root: false })
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('missing-root')
      expect(view.reservedRoot).toEqual({ rootPath: f.rootPath, basis: 'observed-parent' })
      expect(
        view.facts.some((entry) => entry.role === 'private-root' && entry.presence === 'absent'),
      ).toBe(true)
      await expect(fs.lstat(f.rootPath)).rejects.toMatchObject({ code: 'ENOENT' })
      boundary(view)
    })

    it('does not classify a root below a missing parent as confirmed empty', async () => {
      const f = await fixture({ root: false })
      const rootPath = path.join(f.base, 'missing-parent', 'model-gateway-private-v1')
      const owner = createPrivateResourceOwner(f.inventory, { ...context, rootPath })
      cleanup.at(-1)!.owners.push(owner)
      const view = await owner.observe()
      expect(view.state).toBe('unknown')
      expect(view.reservedRoot.rootPath).toBe(rootPath)
      expect(view.reason).toBe('missing-parent')
      await expect(fs.lstat(path.dirname(rootPath))).rejects.toMatchObject({ code: 'ENOENT' })
      boundary(view)
    })

    it('retains protection after a real root directory is moved and a new inode appears at the same name', async () => {
      const f = await fixture()
      const owner = f.owner()
      const before = await owner.observe()
      const oldIdentity = named(before, 'model-gateway-private-v1')[0].identity!
      await fs.rename(f.rootPath, path.join(f.base, 'previous-root'))
      await fs.mkdir(f.rootPath, { mode: 0o700 })
      for (const bucket of buckets) await fs.mkdir(path.join(f.rootPath, bucket), { mode: 0o700 })
      const after = await owner.observe()
      expect(after.state).toBe('unknown')
      const roots = named(after, 'model-gateway-private-v1')
      expect(roots.some((entry) => entry.identity?.fileId === oldIdentity.fileId)).toBe(true)
      expect(
        new Set(roots.flatMap((entry) => (entry.identity ? [entry.identity.fileId] : []))).size,
      ).toBeGreaterThanOrEqual(2)
      boundary(after)
    })

    it('bounds retained root identities across 33 real root generations and never admits the truncated generation', async () => {
      const f = await fixture()
      const owner = f.owner()
      const initial = await owner.observe()
      expect(initial.state).toBe('observed')
      let last = initial
      for (let generation = 1; generation <= 32; generation++) {
        await fs.rename(f.rootPath, path.join(f.base, `retained-root-${generation}`))
        await fs.mkdir(f.rootPath, { mode: 0o700 })
        for (const bucket of buckets) await fs.mkdir(path.join(f.rootPath, bucket), { mode: 0o700 })
        last = await owner.observe()
        expect(last.state).toBe('unknown')
        expect(last.inventoryAccepted).toBe(false)
        expect(last.facts.filter((entry) => entry.kind === 'root')).toHaveLength(
          Math.min(generation + 1, 32),
        )
      }
      expect(last.facts.filter((entry) => entry.kind === 'root')).toHaveLength(32)
      boundary(last)
    })

    it('retains old and new file identities and reports the frozen A same-location rejection', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      const owner = f.owner()
      const before = await owner.observe()
      const oldId = named(before, ids.credential)[0].identity!.fileId
      // Retaining the original inode avoids relying on the OS inode-reuse schedule.
      await fs.rename(destination, path.join(f.base, 'retained-original'))
      await file(f.rootPath, 'credentials', ids.credential)
      const after = await owner.observe()
      expect(after.state).toBe('unknown')
      expect(after.reason).not.toBeNull()
      expect(after.inventoryAccepted).toBe(false)
      const records = named(after, ids.credential)
      expect(records.some((entry) => entry.identity?.fileId === oldId)).toBe(true)
      expect(
        new Set(records.flatMap((entry) => (entry.identity ? [entry.identity.fileId] : []))).size,
      ).toBe(2)
      expect(
        f.inventory.inspect().protected.some((entry) => entry.identity?.fileId === oldId),
      ).toBe(true)
      boundary(after)
    })

    it('retains a removed file as retired rather than silently dropping the old identity', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      const owner = f.owner()
      const first = await owner.observe()
      const oldId = named(first, ids.credential)[0].identity!.fileId
      await fs.rename(destination, path.join(f.base, 'retained-original'))
      const next = await owner.observe()
      const retained = next.facts.find((entry) => entry.identity?.fileId === oldId)
      expect(retained).toMatchObject({ presence: 'absent', state: 'retired' })
      boundary(next)
    })

    it('invalidates an in-flight observation on mutation without issuing a mutation ticket', async () => {
      const f = await fixture()
      const owner = f.owner()
      const pending = owner.observe()
      expect(owner.inspect().actualUnsettled).toBeGreaterThan(0)
      const mutation = owner.beginMutation()
      expect(mutation).toMatchObject({ ok: false, reason: 'busy' })
      const result = await pending
      expect(['cancelled', 'unknown']).toContain(result.state)
      expect(result.actualUnsettled).toBe(0)
      boundary(result)
    })

    it('blocks observations for a real idle mutation ticket and rejects forged or reused tokens', async () => {
      const f = await fixture()
      const owner = f.owner()
      await owner.observe()
      const mutation = owner.beginMutation()
      if (!mutation.ok) throw new Error('expected idle mutation admission')
      expect(owner.endMutation({}).ok).toBe(false)
      expect(owner.endMutation({ ...mutation.mutation }).ok).toBe(false)
      expect(mutation).toMatchObject({
        mechanismOnly: true,
        productionAdmission: 'unsupported',
        nodeEvidence: 'node-observed-unfenced',
      })
      const blocked = await owner.observe()
      expect(blocked.reason).toBe('busy')
      expect(owner.endMutation(mutation.mutation).ok).toBe(true)
      expect(owner.endMutation(mutation.mutation).ok).toBe(false)
      const next = await owner.observe()
      expect(next.state).toBe('observed')
      boundary(next)
    })

    it('keeps an actual Node metadata operation charged after same-stack cancellation', async () => {
      const f = await fixture()
      const owner = f.owner()
      const pending = owner.observe()
      const before = owner.inspect()
      expect(before.actualUnsettled).toBeGreaterThan(0)
      expect(before.acquireSlots).toBeGreaterThan(0)
      const cancelled = owner.cancel()
      expect(cancelled.actualUnsettled).toBeGreaterThan(0)
      expect(cancelled.acquireSlots).toBeGreaterThan(0)
      expect(cancelled.started).toBe(before.started)
      const result = await pending
      expect(['cancelled', 'unknown']).toContain(result.state)
      expect(result.actualUnsettled).toBe(0)
      expect(result.acquireSlots).toBe(0)
      expect(result.started).toBe(result.settled)
      boundary(result)
    })

    it('blocks admission on close while the actual Node callback still occupies its slot', async () => {
      const f = await fixture()
      const owner = f.owner()
      const pending = owner.observe()
      const closing = owner.close()
      expect(owner.inspect().actualUnsettled).toBeGreaterThan(0)
      expect(owner.inspect().acquireSlots).toBeGreaterThan(0)
      const late = await owner.observe()
      expect(late.state).not.toBe('observed')
      await pending
      const closed = await closing
      expect(closed.state).toBe('closed')
      expect(closed.actualUnsettled).toBe(0)
      expect(closed.acquireSlots).toBe(0)
      expect(closed.heldDirectories).toBe(0)
      boundary(closed)
    })

    it('fails initialization after actual root reserve while retaining the reserved identity [injected fault]', async () => {
      const f = await fixture()
      const view = await f.owner({ testFault: 'after-root-reserve' }).observe()
      expect(['unknown', 'failed']).toContain(view.state)
      expect(view.reservedRoot.basis).toBe('observed-parent')
      expect(view.facts.some((entry) => entry.role === 'private-root')).toBe(true)
      expect(f.inventory.inspect().protected.some((entry) => entry.kind === 'root')).toBe(true)
      boundary(view)
    })

    it('retains a held slot on a simulated close-receipt failure after real Dir.close [injected receipt]', async () => {
      const f = await fixture()
      const owner = f.owner({ testFault: 'close-receipt-once' })
      const view = await owner.observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('release-unknown')
      expect(view.heldDirectories).toBeGreaterThan(0)
      const closed = await owner.close()
      expect(closed.state).toBe('unknown')
      expect(closed.heldDirectories).toBeGreaterThan(0)
      boundary(closed)
    })

    it('rejects a real non-private writable root without treating it as an empty inventory', async () => {
      const f = await fixture()
      await fs.chmod(f.rootPath, 0o777)
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.facts.length).toBeGreaterThan(0)
      boundary(view)
    })

    it.skipIf(process.getuid?.() === 0)(
      'rejects a real mode-000 bucket separately from injected faults',
      async () => {
        const f = await fixture()
        const denied = path.join(f.rootPath, 'audit')
        await fs.chmod(denied, 0)
        try {
          const view = await f.owner().observe()
          expect(view.state).toBe('unknown')
          expect(view.facts.length).toBeGreaterThan(0)
          boundary(view)
        } finally {
          await fs.chmod(denied, 0o700)
        }
      },
    )

    it('applies a real low entry budget to a larger fixture without reporting a truncated success', async () => {
      const f = await fixture()
      await file(f.rootPath, 'credentials', ids.credential)
      await file(f.rootPath, 'credentials', ids.orphan)
      const view = await f.owner({ limits: { entries: 1 } }).observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('budget')
      expect(view.facts.length).toBeGreaterThan(0)
      boundary(view)
    })

    it('keeps an outstanding mutation barrier after cancel until the precise token settles', async () => {
      const f = await fixture()
      const owner = f.owner()
      const mutation = owner.beginMutation()
      if (!mutation.ok) throw new Error('expected idle mutation admission')
      const cancelled = owner.cancel()
      expect(cancelled.mutationOutstanding).toBe(true)
      expect(cancelled.actualUnsettled).toBe(0)
      expect((await owner.observe()).reason).toBe('busy')
      expect(owner.endMutation({ ...mutation.mutation }).ok).toBe(false)
      expect(owner.inspect().mutationOutstanding).toBe(true)
      expect(owner.endMutation(mutation.mutation).ok).toBe(true)
      expect(owner.inspect().mutationOutstanding).toBe(false)
      expect((await owner.observe()).state).toBe('observed')
    })

    it('keeps a mutation barrier across close and permits only its exact token to finish', async () => {
      const f = await fixture()
      const owner = f.owner()
      const mutation = owner.beginMutation()
      if (!mutation.ok) throw new Error('expected idle mutation admission')
      const closing = await owner.close()
      expect(closing).toMatchObject({
        state: 'unknown',
        reason: 'mutation-unsettled',
        mutationOutstanding: true,
      })
      expect(owner.endMutation({ ...mutation.mutation }).ok).toBe(false)
      expect(owner.endMutation(mutation.mutation).ok).toBe(true)
      expect(owner.beginMutation().ok).toBe(false)
      expect((await owner.observe()).state).not.toBe('observed')
      const closed = await owner.close()
      expect(closed).toMatchObject({ state: 'closed', mutationOutstanding: false })
      boundary(closed)
    })

    it('enforces recursive depth inside the private root without treating absolute ancestors as that depth', async () => {
      const f = await fixture()
      await file(f.rootPath, 'credentials', ids.credential)
      const view = await f.owner({ limits: { depth: 1 } }).observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('budget')
      expect(named(view, 'credentials')).toHaveLength(1)
      expect(named(view, ids.credential)).toHaveLength(0)
      boundary(view)
    })

    it('measures actual absolute paths in UTF8 bytes rather than UTF16 character count', async () => {
      const f = await fixture()
      const name = '界'.repeat(16) + '.credential'
      const destination = await file(f.rootPath, 'credentials', name)
      const pathBytes = Buffer.byteLength(f.rootPath) + 42
      expect(destination.length).toBeLessThan(pathBytes)
      expect(Buffer.byteLength(destination)).toBeGreaterThan(pathBytes)
      const view = await f.owner({ limits: { pathBytes } }).observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('budget')
      expect(named(view, name)).toEqual([])
      boundary(view)
    })

    it.skipIf(process.platform !== 'linux')(
      'rejects an actual undecodable POSIX leaf name without silently observing a different replacement name',
      async () => {
        const f = await fixture()
        const destination = Buffer.concat([
          Buffer.from(path.join(f.rootPath, 'credentials') + path.sep),
          Buffer.from([0xff]),
        ])
        await fs.writeFile(destination, 'synthetic fixture', { mode: 0o600, flag: 'wx' })
        const view = await f.owner().observe()
        expect(view.state).toBe('unknown')
        expect(view.reason).toBe('unsupported-name')
        expect(
          view.facts.every((entry) => entry.components.every((part) => !part.includes('\uFFFD'))),
        ).toBe(true)
        boundary(view)
      },
    )

    it('conservatively rejects a real replacement-character leaf without claiming undecodable bytes were observed', async () => {
      const f = await fixture()
      await file(f.rootPath, 'credentials', '\uFFFD.credential')
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('unsupported-name')
      boundary(view)
    })

    it.each([
      { extra: true },
      { limits: { extra: 1 } },
      { limits: { entries: 0 } },
      { limits: { entries: 32769 } },
      { limits: { depth: 0 } },
      { limits: { depth: 129 } },
      { limits: { pathBytes: 0 } },
      { limits: { pathBytes: 16385 } },
      { limits: { observationMs: 0 } },
      { limits: { observationMs: 5001 } },
      { limits: { entries: 1.5 } },
      { limits: { depth: Number.NaN } },
      { testFault: 'arbitrary-fs-operation' },
    ])('rejects invalid strict options before starting metadata IO: %j', async (settings) => {
      const f = await fixture()
      const metadataStat = vi.spyOn(fs, 'lstat')
      const metadataOpenDir = vi.spyOn(fs, 'opendir')
      const owner = f.owner(settings)
      expect(owner.inspect()).toMatchObject({
        state: 'failed',
        started: 0,
        actualUnsettled: 0,
        acquireSlots: 0,
      })
      const view = await owner.observe()
      expect(view.state).toBe('failed')
      expect(view.started).toBe(0)
      expect(metadataStat).not.toHaveBeenCalled()
      expect(metadataOpenDir).not.toHaveBeenCalled()
      boundary(view)
    })

    it('rejects option and binding getters without executing them or starting IO', async () => {
      const f = await fixture()
      const metadataStat = vi.spyOn(fs, 'lstat')
      const metadataOpenDir = vi.spyOn(fs, 'opendir')
      const getter = vi.fn(() => {
        throw new Error('getter must not run')
      })
      const candidates = [
        Object.defineProperty({}, 'limits', { enumerable: true, get: getter }),
        { limits: Object.defineProperty({}, 'entries', { enumerable: true, get: getter }) },
      ]
      for (const candidate of candidates) {
        const owner = f.owner(candidate)
        expect(await owner.observe()).toMatchObject({ state: 'failed', started: 0 })
      }
      const binding = Object.defineProperty({ ...context }, 'rootPath', {
        enumerable: true,
        get: getter,
      })
      const owner = createPrivateResourceOwner(f.inventory, binding)
      cleanup.at(-1)!.owners.push(owner)
      expect(await owner.observe()).toMatchObject({ state: 'failed', started: 0 })
      expect(getter).not.toHaveBeenCalled()
      expect(metadataStat).not.toHaveBeenCalled()
      expect(metadataOpenDir).not.toHaveBeenCalled()
    })

    it('rejects a real group-writable bucket while retaining its metadata', async () => {
      const f = await fixture()
      await fs.chmod(path.join(f.rootPath, 'credentials'), 0o770)
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(named(view, 'credentials')).toHaveLength(1)
      boundary(view)
    })

    it('rejects a real world-writable leaf in an otherwise private directory', async () => {
      const f = await fixture()
      const destination = await file(f.rootPath, 'credentials', ids.credential)
      await fs.chmod(destination, 0o606)
      const view = await f.owner().observe()
      expect(view.state).toBe('unknown')
      expect(named(view, ids.credential)).toHaveLength(1)
      boundary(view)
    })
  },
)

describe.runIf(process.platform === 'win32')(
  'I06 real private metadata owner: unsupported Windows boundary',
  () => {
    it('reports unsupported-platform without fabricated POSIX evidence or content access', async () => {
      const inventory = createPrivateResourceInventory(context)
      const owner = createPrivateResourceOwner(inventory, {
        ...context,
        rootPath: path.join(tmpdir(), 'i06-private-owner-unsupported', 'model-gateway-private-v1'),
      })
      const view = await owner.observe()
      expect(view.state).toBe('unknown')
      expect(view.reason).toBe('unsupported-platform')
      expect(view.started).toBe(0)
      boundary(view)
      await owner.close()
    })
  },
)
