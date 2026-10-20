import { randomUUID } from 'node:crypto'
import type { SafeStorage } from 'electron'
import { GatewayFailure, opaqueId, parse } from './policy'

export type CredentialBinding = { ref: string; principal: string; version: string }
export type OpenCredential = CredentialBinding & { secret: string }
export interface CredentialReader {
  read(ref: string): Promise<OpenCredential>
}
// Future application-private repository. Never implement this with a project Store/export.
export interface CiphertextRepository {
  write(binding: CredentialBinding, ciphertext: Buffer): Promise<void>
  read(ref: string): Promise<{ binding: CredentialBinding; ciphertext: Buffer }>
}
type EncryptionAdapter = Pick<
  SafeStorage,
  'isEncryptionAvailable' | 'getSelectedStorageBackend' | 'encryptString' | 'decryptString'
>

export class EncryptedCredentialBoundary implements CredentialReader {
  constructor(
    private readonly encryption: EncryptionAdapter,
    private readonly repository: CiphertextRepository,
    private readonly platform: NodeJS.Platform,
  ) {}

  private requireSecureBackend(): void {
    if (!this.encryption.isEncryptionAvailable()) throw new Error()
    if (this.platform === 'linux') {
      const backend = this.encryption.getSelectedStorageBackend()
      if (!['gnome_libsecret', 'kwallet', 'kwallet5', 'kwallet6'].includes(backend))
        throw new Error()
    }
  }

  async store(principal: string, secret: string): Promise<CredentialBinding> {
    parse(opaqueId, principal)
    if (typeof secret !== 'string' || !/^[\x21-\x7e]{1,4096}$/.test(secret))
      throw new GatewayFailure('INVALID_INPUT')
    try {
      this.requireSecureBackend()
      const ciphertext = this.encryption.encryptString(secret)
      const binding = { ref: randomUUID(), principal, version: randomUUID() }
      await this.repository.write(binding, Buffer.from(ciphertext))
      return { ...binding }
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }

  async read(ref: string): Promise<OpenCredential> {
    parse(opaqueId, ref)
    try {
      this.requireSecureBackend()
      const record = await this.repository.read(ref)
      // Awaiting the repository must not bypass a newly locked/unavailable backend.
      this.requireSecureBackend()
      if (record.binding.ref !== ref) throw new Error()
      parse(opaqueId, record.binding.principal)
      parse(opaqueId, record.binding.version)
      const secret = this.encryption.decryptString(Buffer.from(record.ciphertext))
      if (!/^[\x21-\x7e]{1,4096}$/.test(secret)) throw new Error()
      return { ...record.binding, secret }
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }
}
