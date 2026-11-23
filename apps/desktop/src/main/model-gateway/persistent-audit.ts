import { createHash, randomUUID } from 'node:crypto'
import { z } from 'zod'
import type { AuditRecord, AuditSink } from './gateway'
import { failureCodes, GatewayFailure, opaqueId, purposeSchema } from './policy'
import {
  PrivateDirectory,
  PrivateOperations,
  type PrivateLocation,
  type PrivateWriteObserver,
} from './private-directory'

const origin = z
  .string()
  .min(1)
  .max(2048)
  .refine((value) => {
    try {
      const url = new URL(value)
      return (
        url.origin === value &&
        !url.username &&
        !url.password &&
        (url.protocol === 'https:' ||
          (url.protocol === 'http:' && url.hostname === '127.0.0.1' && Boolean(url.port)))
      )
    } catch {
      return false
    }
  })
const canonicalTime = z
  .string()
  .length(24)
  .refine((value) => {
    try {
      return new Date(value).toISOString() === value
    } catch {
      return false
    }
  })
export const auditRecordSchema = z
  .object({
    targetId: opaqueId,
    configVersion: opaqueId,
    principal: opaqueId,
    endpointOrigin: origin,
    endpointDigest: z.string().regex(/^[a-f0-9]{64}$/),
    projectId: opaqueId,
    purpose: purposeSchema,
    scopes: z
      .array(opaqueId)
      .min(1)
      .max(256)
      .refine((value) => new Set(value).size === value.length),
    decision: z.enum(['authorized', 'denied']),
    event: z.enum(['attempt-intent', 'blocked', 'attempt-failed']),
    reason: z.enum(['ATTEMPT_INTENT', ...failureCodes]),
    time: canonicalTime,
  })
  .strict()
  .refine((record) => {
    if (record.event === 'attempt-intent')
      return record.decision === 'authorized' && record.reason === 'ATTEMPT_INTENT'
    return (
      record.reason !== 'ATTEMPT_INTENT' &&
      (record.event === 'blocked' ? record.decision === 'denied' : record.decision === 'authorized')
    )
  })
const payloadSchema = z
  .object({ format: z.literal(1), eventId: opaqueId, record: auditRecordSchema })
  .strict()
const envelopeSchema = payloadSchema.extend({ digest: z.string().regex(/^[a-f0-9]{64}$/) }).strict()
const digest = (value: unknown) => createHash('sha256').update(JSON.stringify(value)).digest('hex')

/** Each acknowledged record is independently durable; recovery never replays requests. */
export class PersistentGatewayAudit implements AuditSink {
  private readonly operations = new PrivateOperations()
  private constructor(private readonly files: PrivateDirectory) {}
  static async open(
    location: PrivateLocation,
    observer?: PrivateWriteObserver,
  ): Promise<PersistentGatewayAudit> {
    let files: PrivateDirectory | undefined
    try {
      files = await PrivateDirectory.open(location, 'audit', observer)
      const audit = new PersistentGatewayAudit(files)
      await audit.recover()
      return audit
    } catch {
      await files?.close().catch(() => {})
      throw new GatewayFailure('AUDIT_UNAVAILABLE')
    }
  }

  private async recover(): Promise<{ eventId: string; record: AuditRecord }[]> {
    const names = await this.files.list()
    if (names.some((name) => !name.endsWith('.audit'))) throw new Error()
    const entries: { eventId: string; record: AuditRecord }[] = []
    for (const name of names) {
      const envelope = envelopeSchema.parse(
        JSON.parse((await this.files.read(name, 128 * 1024)).toString('utf8')),
      )
      const { digest: recorded, ...payload } = envelope
      if (`${payload.eventId}.audit` !== name || digest(payload) !== recorded) throw new Error()
      entries.push({ eventId: payload.eventId, record: payload.record })
    }
    return entries.sort(
      (left, right) =>
        left.record.time.localeCompare(right.record.time) ||
        left.eventId.localeCompare(right.eventId),
    )
  }

  async append(record: AuditRecord): Promise<void> {
    try {
      const payload = payloadSchema.parse({ format: 1, eventId: randomUUID(), record })
      const bytes = Buffer.from(JSON.stringify({ ...payload, digest: digest(payload) }))
      await this.operations.run(async () => {
        if ((await this.recover()).length >= 10000) throw new Error()
        await this.files.publish(`${payload.eventId}.audit`, bytes)
      })
    } catch {
      throw new GatewayFailure('AUDIT_UNAVAILABLE')
    }
  }

  async readEntries(): Promise<{ eventId: string; record: AuditRecord }[]> {
    try {
      return await this.operations.run(() => this.recover())
    } catch {
      throw new GatewayFailure('AUDIT_UNAVAILABLE')
    }
  }
  async close(): Promise<void> {
    try {
      await this.operations.close(() => this.files.close())
    } catch {
      throw new GatewayFailure('AUDIT_UNAVAILABLE')
    }
  }
}
