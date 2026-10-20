import { createHash } from 'node:crypto'
import { z } from 'zod'
import {
  credentialBindingSchema,
  type CiphertextRepository,
  type CredentialBinding,
} from './credentials'
import { GatewayFailure, opaqueId } from './policy'
import {
  PrivateDirectory,
  PrivateOperations,
  type PrivateLocation,
  type PrivateWriteObserver,
} from './private-directory'

const base64 = z
  .string()
  .min(4)
  .max(87384)
  .refine(
    (value) =>
      /^[A-Za-z0-9+/]+={0,2}$/.test(value) &&
      Buffer.from(value, 'base64').toString('base64') === value,
  )
const payloadSchema = z
  .object({ format: z.literal(1), binding: credentialBindingSchema, ciphertext: base64 })
  .strict()
const recordSchema = payloadSchema.extend({ digest: z.string().regex(/^[a-f0-9]{64}$/) }).strict()
const digest = (value: unknown) => createHash('sha256').update(JSON.stringify(value)).digest('hex')

/** Immutable encrypted records, outside all project/export roots supplied by the trusted owner. */
export class PrivateCiphertextRepository implements CiphertextRepository {
  private readonly operations = new PrivateOperations()
  private constructor(private readonly files: PrivateDirectory) {}

  static async open(
    location: PrivateLocation,
    observer?: PrivateWriteObserver,
  ): Promise<PrivateCiphertextRepository> {
    let files: PrivateDirectory | undefined
    try {
      files = await PrivateDirectory.open(location, 'credentials', observer)
      const repository = new PrivateCiphertextRepository(files)
      await repository.scan()
      return repository
    } catch {
      await files?.close().catch(() => {})
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }

  private async load(ref: string): Promise<{ binding: CredentialBinding; ciphertext: Buffer }> {
    opaqueId.parse(ref)
    const record = recordSchema.parse(
      JSON.parse((await this.files.read(`${ref}.credential`, 128 * 1024)).toString('utf8')),
    )
    const { digest: recorded, ...payload } = record
    const ciphertext = Buffer.from(payload.ciphertext, 'base64')
    if (payload.binding.ref !== ref || digest(payload) !== recorded || ciphertext.length > 65536)
      throw new Error()
    return { binding: { ...payload.binding }, ciphertext }
  }

  private async scan(): Promise<CredentialBinding[]> {
    const names = await this.files.list()
    if (names.some((name) => !name.endsWith('.credential'))) throw new Error()
    const result: CredentialBinding[] = []
    for (const name of names)
      result.push((await this.load(name.slice(0, -'.credential'.length))).binding)
    return result
  }

  async write(binding: CredentialBinding, ciphertext: Buffer): Promise<void> {
    try {
      // Copy before the first await so later caller mutation cannot alter publication.
      const identity = credentialBindingSchema.parse(binding)
      if (!Buffer.isBuffer(ciphertext) || ciphertext.length === 0 || ciphertext.length > 65536)
        throw new Error()
      const payload = payloadSchema.parse({
        format: 1,
        binding: identity,
        ciphertext: Buffer.from(ciphertext).toString('base64'),
      })
      const bytes = Buffer.from(JSON.stringify({ ...payload, digest: digest(payload) }))
      await this.operations.run(async () => {
        const bindings = await this.scan()
        if (bindings.length >= 4096 && !bindings.some((entry) => entry.ref === identity.ref))
          throw new Error()
        await this.files.publish(`${identity.ref}.credential`, bytes)
      })
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }

  async read(ref: string): Promise<{ binding: CredentialBinding; ciphertext: Buffer }> {
    try {
      return await this.operations.run(() => this.load(ref))
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }

  async listBindings(): Promise<CredentialBinding[]> {
    try {
      return await this.operations.run(() => this.scan())
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }

  async close(): Promise<void> {
    try {
      await this.operations.close(() => this.files.close())
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }
}
