import { createHash } from 'node:crypto'
import { z } from 'zod'
import { credentialBindingSchema } from './credentials'
import { GatewayFailure, opaqueId } from './policy'
import {
  PrivateDirectory,
  PrivateOperations,
  type PrivateLocation,
  type PrivateWriteObserver,
} from './private-directory'
import { materialCanonical } from './stored-result-source'

export const storedConfigurationSchema = z
  .object({
    configurationId: opaqueId,
    configurationVersion: opaqueId,
    displayName: z.string().min(1).max(128),
    endpoint: z.string().min(1).max(2048),
    model: z.string().regex(/^[A-Za-z0-9._:/-]{1,128}$/),
    binding: credentialBindingSchema.nullable(),
  })
  .strict()
export type StoredConfiguration = z.infer<typeof storedConfigurationSchema>
const configurations = z
  .array(storedConfigurationSchema)
  .max(32)
  .refine((values) => new Set(values.map((value) => value.configurationId)).size === values.length)
const hashSchema = z.string().regex(/^[a-f0-9]{64}$/)
const payloadSchema = z
  .object({
    format: z.literal(1),
    recordId: opaqueId,
    sequence: z.number().int().min(1).max(1024),
    previous: hashSchema.nullable(),
    configurations,
  })
  .strict()
const recordSchema = payloadSchema.extend({ digest: hashSchema }).strict()
const digest = (value: unknown) =>
  createHash('sha256').update(materialCanonical(value)).digest('hex')
const sequenceId = (sequence: number) =>
  `00000000-0000-4000-8000-${sequence.toString(16).padStart(12, '0')}`

/** App-private, immutable configuration journal. Contains no plaintext credentials or grants. */
export class ConfigurationRepository {
  private readonly operations = new PrivateOperations()
  private tail: Promise<void> = Promise.resolve()
  private constructor(private readonly files: PrivateDirectory) {}
  private serial<T>(action: () => Promise<T>): Promise<T> {
    const previous = this.tail
    const operation = this.operations.run(() => previous.then(action))
    this.tail = operation.then(
      () => {},
      () => {},
    )
    return operation
  }
  static async open(
    location: PrivateLocation,
    observer?: PrivateWriteObserver,
  ): Promise<ConfigurationRepository> {
    let files: PrivateDirectory | undefined
    try {
      files = await PrivateDirectory.open(location, 'configurations', observer)
      const repository = new ConfigurationRepository(files)
      await repository.scan()
      return repository
    } catch {
      await files?.close().catch(() => {})
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }
  private async scan() {
    const names = await this.files.list()
    if (names.length > 1024 || names.some((name) => !name.endsWith('.configuration')))
      throw new Error()
    const records: z.infer<typeof recordSchema>[] = []
    for (const name of names) {
      const record = recordSchema.parse(
        JSON.parse((await this.files.read(name, 128 * 1024)).toString('utf8')),
      )
      const { digest: recorded, ...payload } = record
      if (
        `${record.recordId}.configuration` !== name ||
        record.recordId !== sequenceId(record.sequence) ||
        digest(payload) !== recorded
      )
        throw new Error()
      records.push(record)
    }
    records.sort((a, b) => a.sequence - b.sequence)
    let previous: string | null = null
    for (const [index, record] of records.entries()) {
      if (record.sequence !== index + 1 || record.previous !== previous) throw new Error()
      previous = record.digest
    }
    return {
      sequence: records.length,
      digest: previous,
      configurations: records.at(-1)?.configurations ?? [],
    }
  }
  async load(): Promise<StoredConfiguration[]> {
    try {
      return await this.serial(async () => structuredClone((await this.scan()).configurations))
    } catch {
      throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    }
  }
  async replace(expected: StoredConfiguration[], next: StoredConfiguration[]): Promise<void> {
    try {
      const before = configurations.parse(expected),
        copied = configurations.parse(next)
      await this.serial(async () => {
        const current = await this.scan()
        if (
          materialCanonical(current.configurations) !== materialCanonical(before) ||
          current.sequence >= 1024
        )
          throw new Error()
        const payload = payloadSchema.parse({
          format: 1,
          // A unique immutable slot per sequence is a cross-instance atomic CAS.
          recordId: sequenceId(current.sequence + 1),
          sequence: current.sequence + 1,
          previous: current.digest,
          configurations: copied,
        })
        const bytes = Buffer.from(materialCanonical({ ...payload, digest: digest(payload) }))
        if (bytes.length > 128 * 1024) throw new Error()
        await this.files.publish(`${payload.recordId}.configuration`, bytes)
        const published = await this.scan()
        if (published.digest !== digest(payload)) throw new Error()
      })
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
