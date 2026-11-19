import { randomUUID } from 'node:crypto'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CiphertextRepository } from '../../apps/desktop/src/main/model-gateway/credentials'

const electron = vi.hoisted(() => ({
  app: { isReady: vi.fn(() => true) },
  safeStorage: {
    isEncryptionAvailable: vi.fn(() => true),
    getSelectedStorageBackend: vi.fn(() => 'gnome_libsecret'),
    encryptString: vi.fn(() => Buffer.from('opaque synthetic ciphertext')),
    decryptString: vi.fn(() => ''),
  },
}))
vi.mock('electron', () => electron)
import { createElectronCredentialBoundary } from '../../apps/desktop/src/main/model-gateway/electron-safe-storage'

function fixture(type = 'browser', ready = true, version: string | null = '44.9.0') {
  vi.stubGlobal('process', {
    ...process,
    type,
    platform: 'linux',
    versions: { ...process.versions, electron: version },
  })
  electron.app.isReady.mockReturnValue(ready)
  const repository: CiphertextRepository = {
    write: vi.fn(async () => {}),
    read: vi.fn(async () => {
      throw new Error('private path must not escape')
    }),
  }
  return repository
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.clearAllMocks()
  electron.safeStorage.isEncryptionAvailable.mockReturnValue(true)
  electron.safeStorage.getSelectedStorageBackend.mockReturnValue('gnome_libsecret')
})

describe('I06 actual Electron factory wiring (module doubles, not OS evidence)', () => {
  it.each(['renderer', 'utility', ''])('rejects non-main runtime %s', (type) => {
    const repository = fixture(type)
    expect(() => createElectronCredentialBoundary(repository)).toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    expect(electron.safeStorage.isEncryptionAvailable).not.toHaveBeenCalled()
  })
  it('rejects before ready and normal Node mode', () => {
    expect(() => createElectronCredentialBoundary(fixture('browser', false))).toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
    expect(() => createElectronCredentialBoundary(fixture('browser', true, null))).toThrow(
      /^CREDENTIAL_UNAVAILABLE$/,
    )
  })
  it('uses the imported Electron safeStorage without caller encryption injection', async () => {
    const repository = fixture()
    const vault = createElectronCredentialBoundary(repository)
    const binding = await vault.store(randomUUID(), 'SYNTHETIC_PLATFORM_TEST')
    expect(electron.safeStorage.encryptString).toHaveBeenCalledOnce()
    expect(repository.write).toHaveBeenCalledWith(
      binding,
      Buffer.from('opaque synthetic ciphertext'),
    )
    await expect(vault.read(binding.ref)).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
  })
  it.each(['basic_text', 'unknown'])('rejects backend %s without encrypting', async (backend) => {
    const repository = fixture()
    electron.safeStorage.getSelectedStorageBackend.mockReturnValue(backend)
    await expect(
      createElectronCredentialBoundary(repository).store(randomUUID(), 'SYNTHETIC_PLATFORM_TEST'),
    ).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    expect(electron.safeStorage.encryptString).not.toHaveBeenCalled()
    expect(repository.write).not.toHaveBeenCalled()
  })
  it('rejects unavailable encryption and sanitizes construction errors', async () => {
    const repository = fixture()
    electron.safeStorage.isEncryptionAvailable.mockReturnValue(false)
    await expect(
      createElectronCredentialBoundary(repository).store(randomUUID(), 'SYNTHETIC_PLATFORM_TEST'),
    ).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    electron.app.isReady.mockImplementationOnce(() => {
      throw new Error('private OS path')
    })
    expect(() => createElectronCredentialBoundary(repository)).toThrow(/^CREDENTIAL_UNAVAILABLE$/)
  })
  it('sanitizes an actual adapter method exception without repository fallback', async () => {
    const repository = fixture()
    electron.safeStorage.encryptString.mockImplementationOnce(() => {
      throw new Error('private OS detail synthetic secret path')
    })
    await expect(
      createElectronCredentialBoundary(repository).store(randomUUID(), 'SYNTHETIC_PLATFORM_TEST'),
    ).rejects.toThrow(/^CREDENTIAL_UNAVAILABLE$/)
    expect(repository.write).not.toHaveBeenCalled()
  })
})
