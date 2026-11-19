import { randomUUID } from 'node:crypto'
import { describe, expect, it, vi } from 'vitest'
import {
  EncryptedCredentialBoundary,
  type CiphertextRepository,
  type CredentialBinding,
} from '../../apps/desktop/src/main/model-gateway/credentials'

// Boundary doubles only: these tests make no claim about actual OS encryption.
function fixture(backend = 'gnome_libsecret', platform: NodeJS.Platform = 'linux') {
  const records = new Map<string, { binding: CredentialBinding; ciphertext: Buffer }>()
  const encrypted = new Map<string, string>()
  const encryption = {
    isEncryptionAvailable: vi.fn(() => true),
    getSelectedStorageBackend: vi.fn(() => backend as 'gnome_libsecret'),
    encryptString: vi.fn((plaintext: string) => {
      const token = randomUUID()
      encrypted.set(token, plaintext)
      return Buffer.from(token)
    }),
    decryptString: vi.fn((ciphertext: Buffer) => {
      const plaintext = encrypted.get(ciphertext.toString())
      if (plaintext === undefined) throw new Error('invalid test ciphertext')
      return plaintext
    }),
  }
  const repository: CiphertextRepository = {
    write: vi.fn(async (binding, ciphertext) => {
      records.set(binding.ref, { binding: { ...binding }, ciphertext: Buffer.from(ciphertext) })
    }),
    read: vi.fn(async (ref) => {
      const record = records.get(ref)
      if (!record) throw new Error('private missing path')
      return record
    }),
  }
  return {
    records,
    encryption,
    repository,
    vault: new EncryptedCredentialBoundary(encryption, repository, platform),
  }
}

describe('I06 encrypted credential boundary (no real safeStorage calls)', () => {
  it('returns opaque binding only and sends ciphertext only to private repository', async () => {
    const f = fixture()
    const principal = randomUUID()
    const binding = await f.vault.store(principal, 'SYNTHETIC_TEST_KEY')
    expect(Object.keys(binding).sort()).toEqual(['principal', 'ref', 'version'])
    expect(binding.principal).toBe(principal)
    expect(f.records.get(binding.ref)?.ciphertext.toString()).not.toContain('SYNTHETIC_TEST_KEY')
    expect(JSON.stringify([...f.records])).not.toContain('SYNTHETIC_TEST_KEY')
    expect(await f.vault.read(binding.ref)).toEqual({ ...binding, secret: 'SYNTHETIC_TEST_KEY' })
    const next = await f.vault.store(principal, 'SYNTHETIC_TEST_KEY')
    expect(next.ref).not.toBe(binding.ref)
    expect(next.version).not.toBe(binding.version)
  })
  it.each(['basic_text', 'unknown'])(
    'rejects insecure Linux backend %s without writing plaintext',
    async (backend) => {
      const f = fixture(backend)
      await expect(f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')).rejects.toThrow(
        'CREDENTIAL_UNAVAILABLE',
      )
      await expect(f.vault.read(randomUUID())).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
      expect(f.repository.write).not.toHaveBeenCalled()
      expect(f.encryption.encryptString).not.toHaveBeenCalled()
    },
  )
  it('rejects unavailable encryption with no fallback repository write', async () => {
    const f = fixture()
    f.encryption.isEncryptionAvailable.mockReturnValue(false)
    await expect(f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')).rejects.toThrow(
      'CREDENTIAL_UNAVAILABLE',
    )
    expect(f.repository.write).not.toHaveBeenCalled()
  })
  it('redacts encrypt/decrypt/write failures', async () => {
    const f = fixture()
    f.encryption.encryptString.mockImplementationOnce(() => {
      throw new Error('secret path key stack')
    })
    await expect(f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    const binding = await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
    f.encryption.decryptString.mockImplementationOnce(() => {
      throw new Error('secret path key stack')
    })
    await expect(f.vault.read(binding.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    vi.mocked(f.repository.write).mockRejectedValueOnce(new Error('secret disk path'))
    await expect(f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')).rejects.toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
  })
  it('rejects repository identity mismatch and a backend locked across await', async () => {
    const f = fixture()
    const binding = await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
    f.records.get(binding.ref)!.binding.ref = randomUUID()
    await expect(f.vault.read(binding.ref)).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    f.encryption.isEncryptionAvailable.mockReturnValueOnce(true).mockReturnValueOnce(false)
    await expect(f.vault.read(binding.ref)).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    expect(f.encryption.decryptString).not.toHaveBeenCalled()
  })
  it.each(['principal', 'version'] as const)(
    'rejects tampered %s metadata instead of relabeling an existing encrypted credential',
    async (field) => {
      const f = fixture()
      const binding = await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
      f.records.get(binding.ref)!.binding[field] = randomUUID()
      await expect(f.vault.read(binding.ref)).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
    },
  )
  it('rejects valid ciphertext exchanged between credential references', async () => {
    const f = fixture()
    const first = await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
    const second = await f.vault.store(randomUUID(), 'ANOTHER_SYNTHETIC_KEY')
    f.records.get(first.ref)!.ciphertext = f.records.get(second.ref)!.ciphertext
    await expect(f.vault.read(first.ref)).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
  })
  it('rejects unknown repository binding fields rather than returning them', async () => {
    const f = fixture()
    const binding = await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
    Object.assign(f.records.get(binding.ref)!.binding, { unexpected: 'raw repository detail' })
    await expect(f.vault.read(binding.ref)).rejects.toThrow('CREDENTIAL_UNAVAILABLE')
  })
  it.each([
    'raw-key',
    'invalid-json',
    'future-format',
    'extra-field',
    'extra-binding-field',
    'invalid-secret',
  ])('rejects decrypted %s without a plaintext or permissive fallback', async (variant) => {
    const f = fixture()
    const binding = await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
    const envelope = JSON.parse(f.encryption.encryptString.mock.calls[0][0])
    let plaintext: string
    if (variant === 'raw-key') plaintext = 'SYNTHETIC_TEST_KEY'
    else if (variant === 'invalid-json') plaintext = '{'
    else {
      if (variant === 'future-format') envelope.format = 2
      if (variant === 'extra-field') envelope.unknown = 'raw detail'
      if (variant === 'extra-binding-field') envelope.binding.unknown = 'raw detail'
      if (variant === 'invalid-secret') envelope.secret = 'key\r\nInjected: header'
      plaintext = JSON.stringify(envelope)
    }
    f.encryption.decryptString.mockReturnValueOnce(plaintext)
    await expect(f.vault.read(binding.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
  })
  it.each(['', 'key\nheader: bad', 'key\u0000', 'x'.repeat(4097)])(
    'rejects malformed credential without persistence',
    async (secret) => {
      const f = fixture()
      await expect(f.vault.store(randomUUID(), secret)).rejects.toThrow('INVALID_INPUT')
      expect(f.repository.write).not.toHaveBeenCalled()
    },
  )
  it.each(['darwin', 'win32'] as const)(
    'does not call Linux-only backend API on %s (type-level adapter only)',
    async (platform) => {
      const f = fixture('unknown', platform)
      await f.vault.store(randomUUID(), 'SYNTHETIC_TEST_KEY')
      expect(f.encryption.getSelectedStorageBackend).not.toHaveBeenCalled()
    },
  )
})
