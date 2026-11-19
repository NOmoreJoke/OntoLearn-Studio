import { createHash, randomUUID } from 'node:crypto'
import { z } from 'zod'
import type { CredentialReader } from './credentials'
import {
  configSchema,
  GatewayFailure,
  invocationSchema,
  normalizeEndpoint,
  opaqueId,
  parse,
  partKindSchema,
  privacySchema,
  purposeSchema,
  scopesSchema,
  type EndpointPolicy,
  type FailureCode,
} from './policy'
import { approvedBodySchema, MAX_BODY_BYTES, readBodyFields } from './pre-encoded-body'
import { sendOnce } from './transport'
import { boundedWait } from './await-boundary'

type Config = z.infer<typeof configSchema> & { version: string }
type Material = { projectId: string; scopes: string[]; kind: string; text: string }
const previewSchema = z
  .object({
    projectId: opaqueId,
    configId: opaqueId,
    purpose: purposeSchema,
    scopes: scopesSchema,
  })
  .strict()
type Preview = z.infer<typeof previewSchema> & {
  config: Config
  privacy: 'minimal' | 'project'
  epoch: number
}
export type AuditRecord = {
  targetId: string
  configVersion: string
  principal: string
  endpointOrigin: string
  endpointDigest: string
  projectId: string
  purpose: z.infer<typeof purposeSchema>
  scopes: string[]
  decision: 'authorized' | 'denied'
  event: 'attempt-intent' | 'blocked' | 'attempt-failed'
  reason: 'ATTEMPT_INTENT' | FailureCode
  time: string
}
export interface AuditSink {
  // Must resolve only after durable private local persistence; rejection blocks egress.
  append(record: AuditRecord): Promise<void>
}

/** Main-only internal core; none of these methods is registered on IPC. */
export class ModelGatewayCore {
  private readonly configs = new Map<string, Config>()
  private readonly materials = new Map<string, Material>()
  private readonly previews = new Map<string, Preview>()
  private readonly grants = new Map<string, Preview>()
  private readonly modes = new Map<string, z.infer<typeof privacySchema>>()
  private readonly epochs = new Map<string, number>()
  private readonly pending = new Map<
    AbortController,
    { projectId: string; configId: string; grantId: string }
  >()

  constructor(
    private readonly credentials: CredentialReader,
    private readonly audit: AuditSink,
    private readonly endpointPolicy: EndpointPolicy = 'https',
  ) {}

  configure(input: unknown): { id: string; version: string } {
    const value = parse(configSchema, input)
    value.endpoint = normalizeEndpoint(value.endpoint, this.endpointPolicy)
    const old = this.configs.get(value.id)
    if (
      old &&
      Object.keys(value).every(
        (key) => value[key as keyof typeof value] === old[key as keyof typeof value],
      )
    )
      return { id: old.id, version: old.version }
    if (!old && this.configs.size >= 32) throw new GatewayFailure('INVALID_INPUT')
    const config = { ...value, version: randomUUID() }
    this.configs.set(config.id, config)
    for (const [id, grant] of this.grants) if (grant.config.id === config.id) this.grants.delete(id)
    for (const [id, preview] of this.previews)
      if (preview.config.id === config.id) this.previews.delete(id)
    for (const [controller, pending] of this.pending)
      if (pending.configId === config.id) controller.abort()
    return { id: config.id, version: config.version }
  }

  setPrivacy(projectId: string, privacy: z.infer<typeof privacySchema>): void {
    parse(opaqueId, projectId)
    parse(privacySchema, privacy)
    if (this.mode(projectId) === privacy) return
    this.modes.set(projectId, privacy)
    this.epochs.set(projectId, this.epoch(projectId) + 1)
    for (const [id, grant] of this.grants) if (grant.projectId === projectId) this.grants.delete(id)
    for (const [id, preview] of this.previews)
      if (preview.projectId === projectId) this.previews.delete(id)
    for (const [controller, pending] of this.pending)
      if (pending.projectId === projectId) controller.abort()
  }

  removeConfiguration(configId: string): void {
    parse(opaqueId, configId)
    this.configs.delete(configId)
    for (const [id, grant] of this.grants) if (grant.config.id === configId) this.grants.delete(id)
    for (const [id, preview] of this.previews)
      if (preview.config.id === configId) this.previews.delete(id)
    for (const [controller, pending] of this.pending)
      if (pending.configId === configId) controller.abort()
  }
  discardAuthorizationPreview(previewId: string): void {
    this.previews.delete(parse(opaqueId, previewId))
  }

  // Trusted application assembler only. Never accept scope labels from model text,
  // Python notifications, imports, tool results or renderer without owner validation.
  registerMaterial(input: unknown): string {
    const material = parse(
      z
        .object({
          projectId: opaqueId,
          scopes: scopesSchema,
          kind: partKindSchema,
          text: z.string().max(65536),
        })
        .strict(),
      input,
    )
    if (Buffer.byteLength(material.text) > 65536 || this.materials.size >= 512)
      throw new GatewayFailure('INVALID_INPUT')
    const id = randomUUID()
    this.materials.set(id, { ...material, scopes: [...new Set(material.scopes)].sort() })
    return id
  }

  deriveMaterial(input: unknown): string {
    const value = parse(
      z
        .object({
          projectId: opaqueId,
          inputs: z.array(opaqueId).min(1).max(64),
          kind: partKindSchema,
          text: z.string().max(65536),
        })
        .strict(),
      input,
    )
    const inputs = this.resolveMaterials(value.projectId, value.inputs)
    return this.registerMaterial({
      projectId: value.projectId,
      kind: value.kind,
      text: value.text,
      scopes: [...new Set(inputs.flatMap((part) => part.scopes))],
    })
  }

  releaseMaterial(id: string): void {
    this.materials.delete(parse(opaqueId, id))
  }

  closeProject(projectId: string): void {
    parse(opaqueId, projectId)
    this.setPrivacy(projectId, 'local')
    for (const [id, material] of this.materials)
      if (material.projectId === projectId) this.materials.delete(id)
    this.modes.delete(projectId)
    this.epochs.delete(projectId)
  }

  previewAuthorization(input: unknown): {
    previewId: string
    endpoint: string
    principal: string
    configVersion: string
    scopes: string[]
    privacy: string
  } {
    const value = parse(previewSchema, input)
    const privacy = this.mode(value.projectId)
    if (privacy === 'local') throw new GatewayFailure('LOCAL_ONLY')
    const config = this.configs.get(value.configId)
    if (!config) throw new GatewayFailure('CONFIGURATION_CHANGED')
    if (this.previews.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const previewId = randomUUID()
    const scopes = [...new Set(value.scopes)].sort()
    this.previews.set(previewId, {
      ...value,
      scopes,
      config,
      privacy,
      epoch: this.epoch(value.projectId),
    })
    return {
      previewId,
      endpoint: config.endpoint,
      principal: config.principal,
      configVersion: config.version,
      scopes: [...scopes],
      privacy,
    }
  }

  confirmAuthorization(previewId: string): string {
    const preview = this.previews.get(parse(opaqueId, previewId))
    if (!preview) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    this.previews.delete(previewId)
    this.checkPreview(preview)
    if (this.grants.size >= 128) throw new GatewayFailure('INVALID_INPUT')
    const grantId = randomUUID()
    this.grants.set(grantId, preview)
    return grantId
  }

  revokeAuthorization(grantId: string): void {
    this.grants.delete(parse(opaqueId, grantId))
    for (const [controller, pending] of this.pending)
      if (pending.grantId === grantId) controller.abort()
  }

  private mode(projectId: string) {
    return this.modes.get(projectId) ?? 'local'
  }
  private epoch(projectId: string) {
    return this.epochs.get(projectId) ?? 0
  }
  private checkPreview(value: Preview): void {
    if (this.mode(value.projectId) === 'local') throw new GatewayFailure('LOCAL_ONLY')
    if (
      this.configs.get(value.config.id) !== value.config ||
      this.epoch(value.projectId) !== value.epoch
    )
      throw new GatewayFailure('CONFIGURATION_CHANGED')
  }

  private resolveMaterials(projectId: string, ids: string[]): Material[] {
    return ids.map((id) => {
      const material = this.materials.get(id)
      if (!material || material.projectId !== projectId) throw new GatewayFailure('SCOPE_EXCEEDED')
      return material
    })
  }

  private async record(value: AuditRecord): Promise<void> {
    try {
      await boundedWait(this.audit.append(structuredClone(value)), 'AUDIT_UNAVAILABLE')
    } catch {
      throw new GatewayFailure('AUDIT_UNAVAILABLE')
    }
  }

  invokeApprovedBody(input: unknown, signal?: AbortSignal, finalContext?: () => boolean) {
    return this.send(input, signal, true, finalContext)
  }

  invoke(input: unknown, cancellation?: AbortSignal) {
    return this.send(input, cancellation)
  }

  private async send(
    input: unknown,
    cancellation?: AbortSignal,
    preEncoded = false,
    finalContext?: () => boolean,
  ): Promise<{ ok: true; text: string } | { ok: false; code: FailureCode }> {
    let metadata: Omit<AuditRecord, 'decision' | 'event' | 'reason' | 'time'> | undefined
    let dispatched = false
    const controller = new AbortController()
    const cancel = () => controller.abort()
    cancellation?.addEventListener('abort', cancel, { once: true })
    if (cancellation?.aborted) cancel()
    try {
      const approved = preEncoded ? parse(approvedBodySchema, input) : undefined
      const value = approved ?? parse(invocationSchema, input)
      if (approved && this.mode(value.projectId) === 'local') throw new GatewayFailure('LOCAL_ONLY')
      const ids = 'parts' in value ? value.parts.map((part) => part.materialId) : value.materials
      const config = this.configs.get(value.configId)
      if (!config) throw new GatewayFailure('CONFIGURATION_CHANGED')
      if (approved && new Set(ids).size !== ids.length) throw new GatewayFailure('SCOPE_EXCEEDED')
      if (approved && Buffer.byteLength(approved.body, 'utf8') > MAX_BODY_BYTES)
        throw new GatewayFailure('INVALID_INPUT')
      const parts = this.resolveMaterials(value.projectId, ids)
      const scopes = [...new Set(parts.flatMap((part) => part.scopes))].sort()
      if (approved && approved.configVersion !== config.version)
        throw new GatewayFailure('CONFIGURATION_CHANGED')
      if (
        approved &&
        (scopes.length !== approved.scopes.length ||
          scopes.some((scope) => !approved.scopes.includes(scope)))
      )
        throw new GatewayFailure('SCOPE_EXCEEDED')
      // Authorization and durable audit share the same bounded scope vocabulary.
      // An oversized request has no valid audit metadata; never truncate its provenance.
      parse(scopesSchema, scopes)
      metadata = {
        targetId: config.id,
        configVersion: config.version,
        principal: config.principal,
        endpointOrigin: new URL(config.endpoint).origin,
        endpointDigest: createHash('sha256').update(config.endpoint).digest('hex'),
        projectId: value.projectId,
        purpose: value.purpose,
        scopes,
      }
      const grant = this.grants.get(value.grantId)
      const guard = () => {
        if (cancellation?.aborted) throw new GatewayFailure('CANCELLED')
        if (this.mode(value.projectId) === 'local') throw new GatewayFailure('LOCAL_ONLY')
        if (finalContext && !finalContext()) throw new GatewayFailure('CANCELLED')
        if (approved && this.configs.get(config.id) !== config)
          throw new GatewayFailure('CONFIGURATION_CHANGED')
        if (!grant || this.grants.get(value.grantId) !== grant)
          throw new GatewayFailure('AUTHORIZATION_REQUIRED')
        this.checkPreview(grant)
        if (
          grant.projectId !== value.projectId ||
          grant.config !== config ||
          grant.purpose !== value.purpose
        )
          throw new GatewayFailure('AUTHORIZATION_REQUIRED')
        const currentParts = this.resolveMaterials(value.projectId, ids)
        if (
          currentParts.some((part, i) => part !== parts[i]) ||
          parts.some((part) => part.scopes.some((scope) => !grant.scopes.includes(scope)))
        )
          throw new GatewayFailure('SCOPE_EXCEEDED')
      }
      guard()
      if (approved) {
        const fields = readBodyFields(approved.body, config.model)
        for (const [index, { path, kind }] of approved.parts.entries()) {
          const field = fields.get(path)
          const derivedKind =
            field &&
            path.endsWith('.content') &&
            ((field.kind === 'tool' && kind === 'error') ||
              (field.kind === 'history' && path !== 'messages.0.content' && kind === 'summary'))
          if (
            !field ||
            (field.kind !== kind && !derivedKind) ||
            parts[index].kind !== kind ||
            parts[index].text !== field.text
          )
            throw new GatewayFailure('SCOPE_EXCEEDED')
          fields.delete(path)
        }
        if (fields.size) throw new GatewayFailure('SCOPE_EXCEEDED')
      }
      const body =
        approved?.body ??
        JSON.stringify({
          model: config.model,
          parts: parts.map(({ kind, text }) => ({ kind, text })),
        })
      if (Buffer.byteLength(body) > MAX_BODY_BYTES) throw new GatewayFailure('INVALID_INPUT')
      if (this.pending.size >= 4) throw new GatewayFailure('MODEL_UNAVAILABLE')
      this.pending.set(controller, {
        projectId: value.projectId,
        configId: config.id,
        grantId: value.grantId,
      })
      for (let attempt = 0; attempt < 2; attempt++) {
        guard()
        let credential
        try {
          credential = await boundedWait(
            this.credentials.read(config.credentialRef),
            'CREDENTIAL_UNAVAILABLE',
            controller.signal,
          )
        } catch {
          throw new GatewayFailure(
            controller.signal.aborted ? 'CANCELLED' : 'CREDENTIAL_UNAVAILABLE',
          )
        }
        if (
          credential.ref !== config.credentialRef ||
          credential.principal !== config.principal ||
          credential.version !== config.credentialVersion ||
          !/^[\x21-\x7e]{1,4096}$/.test(credential.secret)
        )
          throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
        guard()
        await this.record({
          ...metadata,
          decision: 'authorized',
          event: 'attempt-intent',
          reason: 'ATTEMPT_INTENT',
          time: new Date().toISOString(),
        })
        guard()
        const response = await sendOnce(
          config.endpoint,
          credential.secret,
          body,
          controller.signal,
          () => {
            guard()
            dispatched = true
          },
        )
        guard()
        if (response.status >= 200 && response.status < 300)
          return { ok: true, text: response.body }
        // Never include upstream error bodies in returned errors, logs, or retries.
        if (!approved && attempt === 0 && [429, 503].includes(response.status)) continue
        throw new GatewayFailure('MODEL_UNAVAILABLE')
      }
      throw new GatewayFailure('MODEL_UNAVAILABLE')
    } catch (error) {
      let code: FailureCode = error instanceof GatewayFailure ? error.code : 'MODEL_UNAVAILABLE'
      if (metadata && code !== 'AUDIT_UNAVAILABLE') {
        try {
          await this.record({
            ...metadata,
            decision: dispatched ? 'authorized' : 'denied',
            event: dispatched ? 'attempt-failed' : 'blocked',
            reason: code,
            time: new Date().toISOString(),
          })
        } catch {
          code = 'AUDIT_UNAVAILABLE'
        }
      }
      return { ok: false, code }
    } finally {
      cancellation?.removeEventListener('abort', cancel)
      this.pending.delete(controller)
    }
  }
}
