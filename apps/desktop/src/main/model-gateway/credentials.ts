import { randomUUID } from 'node:crypto'
import type { SafeStorage } from 'electron'
import { z } from 'zod'
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
const bindingSchema = z.object({ ref: opaqueId, principal: opaqueId, version: opaqueId }).strict()
const secretSchema = z.string().regex(/^[\x21-\x7e]{1,4096}$/)
const envelopeSchema = z
  .object({ format: z.literal(1), binding: bindingSchema, secret: secretSchema })
  .strict()

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
    parse(secretSchema, secret)
    try {
      this.requireSecureBackend()
      const binding = { ref: randomUUID(), principal, version: randomUUID() }
      // The encrypted object binds the credential to the exact ref/principal/version.
      // Plain repository metadata cannot relabel another valid ciphertext.
      const ciphertext = this.encryption.encryptString(
        JSON.stringify({ format: 1, binding, secret }),
      )
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
      const metadata = parse(bindingSchema, record.binding)
      if (metadata.ref !== ref) throw new Error()
      const decrypted = this.encryption.decryptString(Buffer.from(record.ciphertext))
      const envelope = parse(envelopeSchema, JSON.parse(decrypted))
      if (
        envelope.binding.ref !== ref ||
        envelope.binding.principal !== metadata.principal ||
        envelope.binding.version !== metadata.version
      )
        throw new Error()
      return { ...envelope.binding, secret: envelope.secret }
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }
}
