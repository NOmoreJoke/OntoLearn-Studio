import fs from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import { randomUUID, randomBytes, createCipheriv, createDecipheriv, createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { PrivateCiphertextRepository } from '../../apps/desktop/src/main/model-gateway/ciphertext-repository'
import { PersistentGatewayAudit } from '../../apps/desktop/src/main/model-gateway/persistent-audit'
import { EncryptedCredentialBoundary } from '../../apps/desktop/src/main/model-gateway/credentials'
import type { PrivateWritePhase } from '../../apps/desktop/src/main/model-gateway/private-directory'
import type { AuditRecord } from '../../apps/desktop/src/main/model-gateway/gateway'

const temporaryRoots: string[] = []
const opened: { close(): Promise<void> }[] = []
afterEach(async () => {
  vi.restoreAllMocks()
  await Promise.all(opened.splice(0).map((value) => value.close().catch(() => {})))
  await Promise.all(
    temporaryRoots.splice(0).map((value) => fs.rm(value, { recursive: true, force: true })),
  )
})
async function location() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'i06-private-'))
  temporaryRoots.push(root)
  return {
    root,
    userDataPath: path.join(root, 'application'),
    excludedRoots: [path.join(root, 'project'), path.join(root, 'exports')],
  }
}
const binding = () => ({ ref: randomUUID(), principal: randomUUID(), version: randomUUID() })
function auditRecord(): AuditRecord {
  return {
    targetId: randomUUID(),
    configVersion: randomUUID(),
    principal: randomUUID(),
    endpointOrigin: 'https://synthetic.example',
    endpointDigest: createHash('sha256').update('https://synthetic.example/final').digest('hex'),
    projectId: randomUUID(),
    purpose: 'explain',
    scopes: [randomUUID()],
    decision: 'authorized',
    event: 'attempt-intent',
    reason: 'ATTEMPT_INTENT',
    time: '2026-10-21T00:00:00.000Z',
  }
}
const leaf = (where: Awaited<ReturnType<typeof location>>, bucket: string, name: string) =>
  path.join(where.userDataPath, 'model-gateway-private-v1', bucket, name)
const options = (where: Awaited<ReturnType<typeof location>>) => ({
  userDataPath: where.userDataPath,
  excludedRoots: where.excludedRoots,
})
const keep = <T extends { close(): Promise<void> }>(value: T): T => {
  opened.push(value)
  return value
}

// Actual AES double is confined to these file tests; it is not OS safeStorage proof.
function encryptionDouble() {
  const key = randomBytes(32)
  return {
    isEncryptionAvailable: () => true,
    getSelectedStorageBackend: () => 'gnome_libsecret' as const,
    encryptString: (text: string) => {
      const iv = randomBytes(12)
      const cipher = createCipheriv('aes-256-gcm', key, iv)
      const bytes = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()])
      return Buffer.concat([iv, cipher.getAuthTag(), bytes])
    },
    decryptString: (bytes: Buffer) => {
      const cipher = createDecipheriv('aes-256-gcm', key, bytes.subarray(0, 12))
      cipher.setAuthTag(bytes.subarray(12, 28))
      return Buffer.concat([cipher.update(bytes.subarray(28)), cipher.final()]).toString('utf8')
    },
  }
}

describe('I06 actual private filesystem persistence (POSIX, no OS credential APIs)', () => {
  it('persists only bound ciphertext and restores it from a new repository', async () => {
    const where = await location()
    const repository = keep(await PrivateCiphertextRepository.open(options(where)))
    const encryption = encryptionDouble()
    const first = new EncryptedCredentialBoundary(encryption, repository, process.platform)
    const identity = await first.store(randomUUID(), 'SYNTHETIC_KEY_MUST_NOT_PERSIST_CLEAR')
    const filename = leaf(where, 'credentials', `${identity.ref}.credential`)
    const bytes = await fs.readFile(filename)
    expect(bytes.toString()).not.toContain('SYNTHETIC_KEY_MUST_NOT_PERSIST_CLEAR')
    expect((await fs.stat(path.dirname(filename))).mode & 0o777).toBe(0o700)
    expect((await fs.stat(filename)).mode & 0o777).toBe(0o600)
    await repository.close()
    const restored = keep(await PrivateCiphertextRepository.open(options(where)))
    const vault = new EncryptedCredentialBoundary(encryption, restored, process.platform)
    expect(await vault.read(identity.ref)).toEqual({
      ...identity,
      secret: 'SYNTHETIC_KEY_MUST_NOT_PERSIST_CLEAR',
    })
    expect(await restored.listBindings()).toEqual([identity])
    expect(await fs.readdir(where.root)).toEqual(['application'])
  })

  it('preserves immutable ref bytes, permits identical reconciliation, rejects replacement', async () => {
    const where = await location()
    const store = keep(await PrivateCiphertextRepository.open(options(where)))
    const identity = binding()
    await store.write(identity, Buffer.from('ciphertext-A'))
    const before = await fs.readFile(leaf(where, 'credentials', `${identity.ref}.credential`))
    await store.write(identity, Buffer.from('ciphertext-A'))
    await expect(store.write(identity, Buffer.from('ciphertext-B'))).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    expect(await fs.readFile(leaf(where, 'credentials', `${identity.ref}.credential`))).toEqual(
      before,
    )
  })

  it.skipIf(process.getuid?.() === 0)(
    'rejects a caller-owned ancestor alias before creating private files',
    async () => {
      const where = await location()
      const safe = path.join(where.root, 'safe')
      const alias = path.join(where.root, 'alias')
      await fs.mkdir(safe, { mode: 0o700 })
      await fs.symlink(safe, alias)
      await expect(
        PrivateCiphertextRepository.open({
          userDataPath: path.join(alias, 'application'),
          excludedRoots: where.excludedRoots,
        }),
      ).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
      expect(await fs.readdir(safe)).toEqual([])
    },
  )

  it('rechecks a declared export alias before reading or publishing more records', async () => {
    const where = await location()
    const store = keep(await PrivateCiphertextRepository.open(options(where)))
    const identity = binding()
    await store.write(identity, Buffer.from('synthetic-cipher'))
    await fs.symlink(where.userDataPath, where.excludedRoots[1])
    await expect(store.read(identity.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    await expect(store.write(binding(), Buffer.from('synthetic-cipher'))).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    expect(await fs.readdir(leaf(where, 'credentials', ''))).toEqual([`${identity.ref}.credential`])
  })

  it('recovers a bounded concurrent admission overshoot without treating valid history as corruption', async () => {
    const where = await location()
    const store = keep(await PrivateCiphertextRepository.open(options(where)))
    const first = binding()
    await store.write(first, Buffer.from('synthetic-cipher'))
    await store.close()
    const sample = JSON.parse(
      await fs.readFile(leaf(where, 'credentials', `${first.ref}.credential`), 'utf8'),
    )
    // Fixture models two writers both admitted just below 4096. Production never overwrites a ref.
    for (let offset = 0; offset < 4096; offset += 32) {
      await Promise.all(
        Array.from({ length: 32 }, async () => {
          const identity = binding()
          const payload = { format: 1, binding: identity, ciphertext: sample.ciphertext }
          const digest = createHash('sha256').update(JSON.stringify(payload)).digest('hex')
          await fs.writeFile(
            leaf(where, 'credentials', `${identity.ref}.credential`),
            JSON.stringify({ ...payload, digest }),
            { mode: 0o600 },
          )
        }),
      )
    }
    const restored = keep(await PrivateCiphertextRepository.open(options(where)))
    expect(await restored.listBindings()).toHaveLength(4097)
    await expect(restored.write(binding(), Buffer.from('new-cipher'))).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    expect((await restored.read(first.ref)).binding).toEqual(first)
  }, 60000)

  it('allows two independent writers without lost audit records or ref overwrite', async () => {
    const where = await location()
    const one = keep(await PrivateCiphertextRepository.open(options(where)))
    const two = keep(await PrivateCiphertextRepository.open(options(where)))
    const identity = binding()
    const results = await Promise.allSettled([
      one.write(identity, Buffer.from('cipher-A')),
      two.write(identity, Buffer.from('cipher-B')),
    ])
    expect(results.map((result) => result.status).sort()).toEqual(['fulfilled', 'rejected'])
    const committed = (await one.read(identity.ref)).ciphertext.toString()
    expect(['cipher-A', 'cipher-B']).toContain(committed)
    const auditOne = keep(await PersistentGatewayAudit.open(options(where)))
    const auditTwo = keep(await PersistentGatewayAudit.open(options(where)))
    const records = Array.from({ length: 12 }, () => auditRecord())
    await Promise.all(
      records.map((record, index) => (index % 2 ? auditOne : auditTwo).append(record)),
    )
    const restored = (await auditOne.readEntries()).map(({ record }) => record)
    expect(restored.map(({ targetId }) => targetId).sort()).toEqual(
      records.map(({ targetId }) => targetId).sort(),
    )
  })

  it.each(['credentials', 'audit'])(
    'rejects private %s inside or above a declared project/export root',
    async (bucket) => {
      const where = await location()
      const open =
        bucket === 'credentials' ? PrivateCiphertextRepository.open : PersistentGatewayAudit.open
      await expect(
        open({
          userDataPath: path.join(where.root, 'project'),
          excludedRoots: [path.join(where.root, 'project')],
        }),
      ).rejects.toThrow(/UNAVAILABLE$/)
      await expect(
        open({
          userDataPath: where.userDataPath,
          excludedRoots: [
            path.join(where.userDataPath, 'model-gateway-private-v1', bucket, 'export'),
          ],
        }),
      ).rejects.toThrow(/UNAVAILABLE$/)
      await expect(
        open({ userDataPath: where.userDataPath, excludedRoots: [path.parse(where.root).root] }),
      ).rejects.toThrow(/UNAVAILABLE$/)
      expect(await fs.readdir(where.root)).toEqual([])
    },
  )

  it.each(['userData', 'namespace', 'bucket'])(
    'refuses a symlink at the %s private component',
    async (component) => {
      const where = await location()
      const outside = path.join(where.root, 'outside')
      await fs.mkdir(outside, { mode: 0o700 })
      if (component === 'userData') await fs.symlink(outside, where.userDataPath)
      else {
        await fs.mkdir(where.userDataPath, { mode: 0o700 })
        const namespace = path.join(where.userDataPath, 'model-gateway-private-v1')
        if (component === 'namespace') await fs.symlink(outside, namespace)
        else {
          await fs.mkdir(namespace, { mode: 0o700 })
          await fs.symlink(outside, path.join(namespace, 'credentials'))
        }
      }
      await expect(PrivateCiphertextRepository.open(options(where))).rejects.toThrow(
        /^CREDENTIAL_UNAVAILABLE$/,
      )
      expect(await fs.readdir(outside)).toEqual([])
    },
  )

  it('rejects unsafe existing modes and final symlinks without repairing permissions', async () => {
    const where = await location()
    const store = keep(await PrivateCiphertextRepository.open(options(where)))
    const identity = binding()
    await store.write(identity, Buffer.from('cipher'))
    const filename = leaf(where, 'credentials', `${identity.ref}.credential`)
    await fs.chmod(filename, 0o644)
    await expect(store.read(identity.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    expect((await fs.stat(filename)).mode & 0o777).toBe(0o644)
    await fs.chmod(filename, 0o600)
    await fs.rename(filename, filename + '.outside')
    await fs.symlink(filename + '.outside', filename)
    await expect(store.read(identity.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    await fs.unlink(filename)
    await fs.rename(filename + '.outside', filename)
    await fs.chmod(path.dirname(filename), 0o755)
    await expect(store.read(identity.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    expect((await fs.stat(path.dirname(filename))).mode & 0o777).toBe(0o755)
  })

  it('detects a replaced directory and does not clean up outside its held namespace', async () => {
    const where = await location()
    const outside = path.join(where.root, 'outside')
    await fs.mkdir(outside, { mode: 0o700 })
    const identity = binding()
    let pendingName = ''
    const store = keep(
      await PrivateCiphertextRepository.open(options(where), async (phase) => {
        if (phase !== 'temp-written') return
        const directory = leaf(where, 'credentials', '')
        pendingName = (await fs.readdir(directory))[0]
        await fs.rename(directory, directory + '-old')
        await fs.writeFile(path.join(outside, pendingName), 'outside-sentinel', { mode: 0o600 })
        await fs.symlink(outside, directory)
      }),
    )
    await expect(store.write(identity, Buffer.from('cipher'))).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    expect(await fs.readFile(path.join(outside, pendingName), 'utf8')).toBe('outside-sentinel')
  })

  it.each(['digest', 'base64', 'format', 'identity', 'unknown', 'oversize'])(
    'refuses corrupted credential %s on reopen',
    async (variant) => {
      const where = await location()
      const store = keep(await PrivateCiphertextRepository.open(options(where)))
      const identity = binding()
      await store.write(identity, Buffer.from('cipher'))
      const filename = leaf(where, 'credentials', `${identity.ref}.credential`)
      const record = JSON.parse(await fs.readFile(filename, 'utf8'))
      if (variant === 'digest') record.digest = '0'.repeat(64)
      if (variant === 'base64') record.ciphertext += '\n'
      if (variant === 'format') record.format = 2
      if (variant === 'identity') record.binding.ref = randomUUID()
      if (variant === 'unknown') record.secret = 'must-be-rejected'
      await fs.writeFile(
        filename,
        variant === 'oversize' ? 'x'.repeat(128 * 1024 + 1) : JSON.stringify(record),
      )
      await store.close()
      await expect(PrivateCiphertextRepository.open(options(where))).rejects.toThrow(
        /^CREDENTIAL_UNAVAILABLE$/,
      )
    },
  )

  it('recovers exact audit metadata with no payload, credential or filesystem path', async () => {
    const where = await location()
    const audit = keep(await PersistentGatewayAudit.open(options(where)))
    const record = auditRecord()
    await audit.append(record)
    await audit.close()
    const reopened = keep(await PersistentGatewayAudit.open(options(where)))
    const entries = await reopened.readEntries()
    expect(entries.map(({ record }) => record)).toEqual([record])
    const names = await fs.readdir(leaf(where, 'audit', ''))
    const raw = await fs.readFile(leaf(where, 'audit', names[0]), 'utf8')
    expect(raw).not.toContain(where.root)
    expect(Object.keys(JSON.parse(raw)).sort()).toEqual(['digest', 'eventId', 'format', 'record'])
    expect((await fs.stat(leaf(where, 'audit', names[0]))).mode & 0o777).toBe(0o600)
    expect((await fs.stat(leaf(where, 'audit', ''))).mode & 0o777).toBe(0o700)
  })

  it.each([
    'payload',
    'path-origin',
    'userinfo-origin',
    'time',
    'reason',
    'pairing',
    'duplicate-scope',
  ])('rejects unsafe audit %s without publishing any record', async (variant) => {
    const where = await location()
    const audit = keep(await PersistentGatewayAudit.open(options(where)))
    const record = auditRecord()
    if (variant === 'payload') Object.assign(record, { body: 'SYNTHETIC_BUSINESS_SECRET' })
    if (variant === 'path-origin') record.endpointOrigin += '/secret?key=secret'
    if (variant === 'userinfo-origin')
      record.endpointOrigin = 'https://key:secret@synthetic.example'
    if (variant === 'time') record.time = 'invalid private/path'
    if (variant === 'reason') Object.assign(record, { reason: 'raw exception' })
    if (variant === 'pairing') record.decision = 'denied'
    if (variant === 'duplicate-scope') record.scopes.push(record.scopes[0])
    await expect(audit.append(record)).rejects.toThrow(/^AUDIT_UNAVAILABLE$/)
    expect(await audit.readEntries()).toEqual([])
  })

  it('refuses a corrupted published audit without erasing evidence', async () => {
    const where = await location()
    const audit = keep(await PersistentGatewayAudit.open(options(where)))
    await audit.append(auditRecord())
    await audit.close()
    const names = await fs.readdir(leaf(where, 'audit', ''))
    const filename = leaf(where, 'audit', names[0])
    const record = JSON.parse(await fs.readFile(filename, 'utf8'))
    record.record.targetId = randomUUID()
    await fs.writeFile(filename, JSON.stringify(record))
    await expect(PersistentGatewayAudit.open(options(where))).rejects.toThrow(/^AUDIT_UNAVAILABLE$/)
    expect(await fs.readdir(leaf(where, 'audit', ''))).toEqual(names)
  })

  it('refuses operations after close, preserving committed files', async () => {
    const where = await location()
    const store = keep(await PrivateCiphertextRepository.open(options(where)))
    const identity = binding()
    await store.write(identity, Buffer.from('cipher'))
    await store.close()
    await expect(store.read(identity.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    await expect(store.write(binding(), Buffer.from('cipher'))).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    expect(await fs.readdir(leaf(where, 'credentials', ''))).toEqual([`${identity.ref}.credential`])
  })
})

describe('I06 real process-exit recovery at private publication boundaries', () => {
  const phases: PrivateWritePhase[] = [
    'partial-written',
    'temp-written',
    'file-synced',
    'published',
    'temp-unlinked',
    'directory-synced',
  ]
  it.each(phases)('restores credential evidence after SIGKILL at %s', async (phase) => {
    const where = await location()
    const identity = binding()
    const result = await new Promise<{
      code: number | null
      signal: NodeJS.Signals | null
      stderr: string
    }>((resolve) => {
      const child = spawn(
        process.execPath,
        [
          'tests/i06-private/crash-child.mjs',
          process.cwd(),
          JSON.stringify(options(where)),
          JSON.stringify(identity),
          phase,
          'credential',
        ],
        { cwd: process.cwd(), stdio: ['ignore', 'ignore', 'pipe'] },
      )
      let stderr = ''
      child.stderr.on('data', (chunk) => {
        stderr += chunk
      })
      child.on('exit', (code, signal) => resolve({ code, signal, stderr }))
    })
    expect(result).toEqual({ code: null, signal: 'SIGKILL', stderr: '' })
    const store = keep(await PrivateCiphertextRepository.open(options(where)))
    if (['published', 'temp-unlinked', 'directory-synced'].includes(phase))
      expect(await store.read(identity.ref)).toEqual({
        binding: identity,
        ciphertext: Buffer.from('SYNTHETIC_CIPHERTEXT_BYTES'),
      })
    else expect(await store.listBindings()).toEqual([])
    // Recovery never deletes a pending name; a live or ambiguous writer may own it.
    const names = await fs.readdir(leaf(where, 'credentials', ''))
    expect(names.some((name) => name.startsWith('.pending-'))).toBe(
      !['temp-unlinked', 'directory-synced'].includes(phase),
    )
  })
  it.each(phases)(
    'restores audit evidence after SIGKILL at %s without replaying anything',
    async (phase) => {
      const where = await location()
      const record = auditRecord()
      const result = await new Promise<{
        code: number | null
        signal: NodeJS.Signals | null
        stderr: string
      }>((resolve) => {
        const child = spawn(
          process.execPath,
          [
            'tests/i06-private/crash-child.mjs',
            process.cwd(),
            JSON.stringify(options(where)),
            JSON.stringify(record),
            phase,
            'audit',
          ],
          { cwd: process.cwd(), stdio: ['ignore', 'ignore', 'pipe'] },
        )
        let stderr = ''
        child.stderr.on('data', (chunk) => {
          stderr += chunk
        })
        child.on('exit', (code, signal) => resolve({ code, signal, stderr }))
      })
      expect(result).toEqual({ code: null, signal: 'SIGKILL', stderr: '' })
      const audit = keep(await PersistentGatewayAudit.open(options(where)))
      expect((await audit.readEntries()).map(({ record }) => record)).toEqual(
        ['published', 'temp-unlinked', 'directory-synced'].includes(phase) ? [record] : [],
      )
    },
  )
})
