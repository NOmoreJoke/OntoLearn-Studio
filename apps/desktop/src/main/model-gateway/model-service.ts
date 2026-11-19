import { randomUUID } from 'node:crypto'
import {
  safeError,
  modelGatewayError,
  modelInvalidRequestError,
  type AgentAuditRecordDTO,
  type AgentCapabilitiesDTO,
  type AgentModelConfigurationSummaryDTO,
  type AgentPurpose,
  type BridgeResult,
  type ModelAccessStatus,
  type ModelConfiguration,
  type ModelExplanationOutcome,
  type ModelFieldCatalog,
  type ModelMethod,
  type ModelParamsMap,
  type ModelResultMap,
  type ModelSelection,
  type ModelWholeResultSelection,
  type SafeError,
} from '@ontolearn/contracts'
import {
  validateModelParams,
  validateModelResult,
  matchesModelResult,
} from '@ontolearn/contracts/v2'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
  decodeChatResponse,
  decodeStructuredContent,
  encodeChatRequest,
} from '../agent/deepseek-codec'
import { providerSignatureSchema, type ProviderSignature } from '../agent/capabilities'
import { parseToolArguments } from '../agent/tools'
import { z } from 'zod'
import { readBodyFields, type ApprovedBodyRequest } from './pre-encoded-body'
import type { EngineSupervisor } from '../engine'
import { EngineError } from '../engine'
import { ConfigurationRepository, type StoredConfiguration } from './configuration-repository'
import { EncryptedCredentialBoundary } from './credentials'
import { ModelGatewayCore, type AuditSink } from './gateway'
import { GatewayApplication, type ApplicationOutcome } from './gateway-application'
import { GatewayFailure, normalizeEndpoint, type EndpointPolicy } from './policy'
import { StoredResultSource, materialCanonical } from './stored-result-source'
import type { StoredFieldModel } from './stored-field-projector'
import type { PersistentGatewayAudit } from './persistent-audit'

export const unverifiedCapabilities: Readonly<AgentCapabilitiesDTO> = Object.freeze({
  connection: 'not-run',
  structuredOutput: 'not-run',
  toolRoundTrip: 'not-run',
  mode: 'unverified',
})

/** Installed by main only after an approved real-provider evaluation. */
export type AgentProviderApproval = {
  configurationId: string
  configurationVersion: string
  signature: ProviderSignature
  confirmBody(
    input: Readonly<{
      projectId: string
      endpoint: string
      principal: string
      purpose: AgentPurpose
      body: string
      scopes: readonly string[]
      privacy: 'minimal' | 'project'
      configurationId: string
      configVersion: string
    }>,
    signal: AbortSignal,
  ): Promise<boolean>
}

type Context = {
  id: string
  projectId: string
  privacy: 'local' | 'minimal' | 'project'
  application: GatewayApplication
  selections: Map<string, ModelSelection>
  catalogs: Map<string, ModelFieldCatalog>
  previews: Map<string, { configurationId: string; version: string; key: string }>
  grants: Map<string, string>
  invocations: Map<string, ModelExplanationOutcome>
}
export function modelSafeError(error: unknown): SafeError {
  if (error instanceof EngineError) return safeError(error.error)
  return modelGatewayError(
    error instanceof GatewayFailure && error.code !== 'CANCELLED'
      ? error.code
      : 'MODEL_UNAVAILABLE',
  )
}
export const unavailableModelStatus = (): ModelAccessStatus => ({
  availability: 'unavailable',
  contextId: null,
  projectId: null,
  privacy: 'local',
  configurations: [],
  selections: [],
  invocations: [],
})

/** Unique app main owner. Context survives renderer recovery; no execution is restored/replayed. */
export class ModelGatewayService {
  private closed = false
  private failed = false
  private context: Context | undefined
  private configurations: StoredConfiguration[] = []
  private tail: Promise<void> = Promise.resolve()
  private queued = 0
  private readonly core: ModelGatewayCore
  private auditReading = false
  private readonly changing = new Set<string>()
  private constructor(
    private readonly engine: EngineSupervisor,
    private readonly repository: ConfigurationRepository,
    private readonly credentials: EncryptedCredentialBoundary,
    private readonly audit: AuditSink & Partial<Pick<PersistentGatewayAudit, 'readEntries'>>,
    private readonly policy: EndpointPolicy,
    private readonly producerPolicy: 'runtime-only' | 'synthetic-test-runtime',
    private readonly fieldModels: StoredFieldModel[],
  ) {
    this.core = new ModelGatewayCore(credentials, audit, policy)
  }
  static async open(input: {
    engine: EngineSupervisor
    repository: ConfigurationRepository
    credentials: EncryptedCredentialBoundary
    audit: AuditSink & Partial<Pick<PersistentGatewayAudit, 'readEntries'>>
    endpointPolicy?: EndpointPolicy
    producerPolicy?: 'runtime-only' | 'synthetic-test-runtime'
    fieldModels?: StoredFieldModel[]
  }): Promise<ModelGatewayService> {
    const owner = new ModelGatewayService(
      input.engine,
      input.repository,
      input.credentials,
      input.audit,
      input.endpointPolicy ?? 'https',
      input.producerPolicy ?? 'runtime-only',
      input.fieldModels ?? [],
    )
    owner.configurations = await input.repository.load()
    for (const configuration of owner.configurations) {
      if (normalizeEndpoint(configuration.endpoint, owner.policy) !== configuration.endpoint)
        throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
      owner.install(configuration)
    }
    return owner
  }
  private open(): void {
    if (this.closed || this.failed) throw new GatewayFailure('MODEL_UNAVAILABLE')
  }
  private current(contextId: string): Context {
    this.open()
    if (!this.context || this.context.id !== contextId)
      throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    return this.context
  }
  private same(context: Context): void {
    if (this.current(context.id) !== context) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
  }
  private configuration(id: string): StoredConfiguration {
    const configuration = this.configurations.find((value) => value.configurationId === id)
    if (!configuration) throw new GatewayFailure('CONFIGURATION_CHANGED')
    return configuration
  }
  private configured(id: string): StoredConfiguration {
    const configuration = this.configuration(id)
    if (configuration.enabled === false) throw new GatewayFailure('CONFIGURATION_CHANGED')
    if (!configuration.binding) throw new GatewayFailure('CREDENTIAL_UNAVAILABLE')
    return configuration
  }
  private visible(configuration: StoredConfiguration): ModelConfiguration {
    return {
      configurationId: configuration.configurationId,
      configurationVersion: configuration.configurationVersion,
      displayName: configuration.displayName,
      endpoint: configuration.endpoint,
      model: configuration.model,
      credentialState: configuration.binding ? 'configured' : 'missing',
    }
  }
  private install(configuration: StoredConfiguration): void {
    if (configuration.binding && configuration.enabled !== false)
      this.core.configure({
        id: configuration.configurationId,
        endpoint: configuration.endpoint,
        model: configuration.model,
        credentialRef: configuration.binding.ref,
        principal: configuration.binding.principal,
        credentialVersion: configuration.binding.version,
      })
    else this.core.removeConfiguration(configuration.configurationId)
  }
  selectProject(projectId: string | null): void {
    if (this.closed) return
    this.context?.application.close()
    this.context = undefined
    if (projectId)
      this.context = {
        id: randomUUID(),
        projectId,
        privacy: 'local',
        application: new GatewayApplication(
          this.core,
          new StoredResultSource(this.engine, projectId, this.producerPolicy),
          this.fieldModels,
        ),
        selections: new Map(),
        catalogs: new Map(),
        previews: new Map(),
        grants: new Map(),
        invocations: new Map(),
      }
  }
  status(): ModelAccessStatus {
    if (this.closed || this.failed) return unavailableModelStatus()
    this.open()
    const context = this.context
    return structuredClone({
      availability: context ? 'ready' : 'unavailable',
      contextId: context?.id ?? null,
      projectId: context?.projectId ?? null,
      privacy: context?.privacy ?? 'local',
      configurations: this.configurations.map((value) => this.visible(value)),
      selections: [...(context?.selections.values() ?? [])],
      invocations: [...(context?.invocations.values() ?? [])].map(({ invocationId, state }) => ({
        invocationId,
        state,
      })),
    })
  }
  private async readAudit(contextId: string): Promise<ModelAccessStatus> {
    const context = this.current(contextId)
    const audit = await this.listAuditEntries(context.projectId, 20)
    this.same(context)
    return { ...this.status(), audit }
  }
  async listAuditEntries(projectId: string, limit: number): Promise<AgentAuditRecordDTO[]> {
    if (!Number.isInteger(limit) || limit < 1 || limit > 100)
      throw new GatewayFailure('INVALID_INPUT')
    const context = this.context
    if (!context || context.projectId !== projectId)
      throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    this.same(context)
    if (!this.audit.readEntries || this.auditReading) throw new GatewayFailure('AUDIT_UNAVAILABLE')
    this.auditReading = true
    try {
      const entries = await this.audit.readEntries()
      this.same(context)
      return entries
        .filter(({ record }) => record.projectId === projectId)
        .slice(-limit)
        .reverse()
        .map(({ eventId, record }) => ({
          eventId,
          targetId: record.targetId,
          endpointOrigin: record.endpointOrigin,
          purpose: record.purpose,
          scopes: record.scopes,
          decision: record.decision,
          event: record.event,
          time: record.time,
        }))
    } finally {
      this.auditReading = false
    }
  }
  listConfigurationSummaries(): AgentModelConfigurationSummaryDTO[] {
    if (this.closed || this.failed) return []
    return this.configurations.map((configuration) => ({
      ...this.visible(configuration),
      enabled: configuration.enabled ?? true,
    }))
  }
  private invalidateApprovals(): void {
    if (!this.context) return
    this.clearPreviews(this.context)
    this.context.grants.clear()
  }
  async setConfigurationEnabled(
    id: string,
    enabled: boolean,
  ): Promise<AgentModelConfigurationSummaryDTO> {
    return this.serial(async () => {
      const before = this.configuration(id)
      if ((before.enabled ?? true) !== enabled) {
        await this.updateConfiguration(id, () =>
          this.repository.setEnabled(id, enabled, this.configurations),
        )
      }
      const configuration = this.configuration(id)
      return { ...this.visible(configuration), enabled }
    })
  }
  async removeConfiguration(id: string): Promise<{ configurationId: string; removed: true }> {
    return this.serial(async () => {
      this.configuration(id)
      await this.updateConfiguration(id, () =>
        this.repository.removeConfiguration(id, this.configurations),
      )
      return { configurationId: id, removed: true }
    })
  }
  private async updateConfiguration(
    id: string,
    persist: () => Promise<StoredConfiguration[]>,
  ): Promise<void> {
    this.core.removeConfiguration(id)
    this.invalidateApprovals()
    await this.persist(persist)
    const configuration = this.configurations.find((value) => value.configurationId === id)
    if (configuration) this.install(configuration)
  }
  probeCapabilities(id: string, scope: 'synthetic' = 'synthetic'): AgentCapabilitiesDTO {
    this.open()
    this.configuration(id)
    if (scope !== 'synthetic') throw new GatewayFailure('INVALID_INPUT')
    const result: AgentCapabilitiesDTO = { ...unverifiedCapabilities, mode: scope }
    const response = (message: unknown, finish_reason: string) =>
      JSON.stringify({
        id: 'offline-probe',
        object: 'chat.completion',
        created: 0,
        model: REQUEST_MODEL,
        choices: [{ index: 0, message, finish_reason }],
      })
    const messages = [
      { role: 'system', content: 'Return JSON.' },
      { role: 'user', content: 'Synthetic fixture.' },
    ]
    const options = { mode: 'disabled', effort: 'low', maxTokens: 64 }
    try {
      const decoded = decodeChatResponse(
        response({ role: 'assistant', content: '{"kind":"uncertain"}' }, 'stop'),
      )
      decodeStructuredContent(
        decoded.choices[0].message,
        z.strictObject({ kind: z.literal('uncertain') }),
      )
      result.structuredOutput = 'passed'
    } catch {
      result.structuredOutput = 'failed'
    }
    try {
      const decoded = decodeChatResponse(
        response(
          {
            role: 'assistant',
            content: null,
            tool_calls: [
              {
                id: 'offline-call',
                type: 'function',
                function: {
                  name: 'ontology_read',
                  arguments: '{"objectIds":["synthetic-object"]}',
                },
              },
            ],
          },
          'tool_calls',
        ),
      )
      const message = decoded.choices[0].message
      const call = message.tool_calls![0]
      parseToolArguments(call.function.name, call.function.arguments)
      encodeChatRequest({
        ...options,
        availableTools: ['ontology_read'],
        messages: [
          ...messages,
          message,
          { role: 'tool', tool_call_id: call.id, content: '{"fields":[]}' },
        ],
      })
      result.toolRoundTrip = 'passed'
    } catch {
      result.toolRoundTrip = 'failed'
    }
    return result
  }

  agentReady(projectId: string, approval?: AgentProviderApproval): boolean {
    if (
      this.closed ||
      this.failed ||
      this.context?.projectId !== projectId ||
      this.context.privacy === 'local' ||
      !approval
    )
      return false
    const configuration = this.configurations.find(
      (value) => value.configurationId === approval.configurationId,
    )
    return Boolean(
      configuration?.binding &&
      configuration.enabled !== false &&
      !this.changing.has(approval.configurationId) &&
      configuration.configurationVersion === approval.configurationVersion &&
      // The explicit test policy already validates every endpoint at load and save.
      // Production still requires the exact endpoint pinned by the provider signature.
      (this.policy === 'loopback-probe-only' || configuration.endpoint === DEEPSEEK_ENDPOINT) &&
      configuration.model === REQUEST_MODEL &&
      approval.signature.codecVersion === CODEC_VERSION &&
      providerSignatureSchema.safeParse(approval.signature).success,
    )
  }

  async invokeAgentBody(
    input: { projectId: string; purpose: AgentPurpose; body: string },
    approval: AgentProviderApproval,
    signal: AbortSignal,
    finalContext: () => boolean,
  ): Promise<string> {
    input = { ...input }
    const context = this.context
    if (!context || context.projectId !== input.projectId)
      throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    if (context.privacy === 'local') throw new GatewayFailure('LOCAL_ONLY')
    const configuration = this.configured(approval.configurationId)
    const privacy = context.privacy
    const fields = readBodyFields(input.body, configuration.model)
    const scopes = [randomUUID()]
    const live = () =>
      !signal.aborted &&
      finalContext() &&
      this.context === context &&
      context.privacy === privacy &&
      this.agentReady(input.projectId, approval)
    if (!live()) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    // Create the core preview before the user decision so a privacy/configuration ABA
    // invalidates it, even if the same visible values return before confirmation.
    const preview = this.core.previewAuthorization({
      projectId: input.projectId,
      configId: configuration.configurationId,
      purpose: input.purpose,
      scopes,
    })
    const parts: ApprovedBodyRequest['parts'] = []
    let grantId: string | undefined
    let abort = () => {}
    const cancelled = new Promise<never>((_, reject) => {
      abort = () => reject(new GatewayFailure('CANCELLED'))
      signal.addEventListener('abort', abort, { once: true })
    })
    try {
      const approved = await Promise.race([
        cancelled,
        Promise.resolve().then(() => {
          if (signal.aborted) throw new GatewayFailure('CANCELLED')
          return approval.confirmBody(
            Object.freeze({
              ...input,
              endpoint: preview.endpoint,
              principal: preview.principal,
              scopes: Object.freeze([...scopes]),
              privacy,
              configurationId: configuration.configurationId,
              configVersion: preview.configVersion,
            }),
            signal,
          )
        }),
      ])
      if (!approved || !live()) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
      grantId = this.core.confirmAuthorization(preview.previewId)
      for (const [path, field] of fields) {
        parts.push({
          path,
          kind: field.kind,
          materialId: this.core.registerMaterial({
            projectId: input.projectId,
            scopes,
            ...field,
          }),
        })
      }
      const result = await context.application.invokeApprovedBody(
        {
          ...input,
          configId: configuration.configurationId,
          configVersion: preview.configVersion,
          grantId,
          parts,
          scopes,
        },
        signal,
        live,
      )
      if (!result.ok) throw new GatewayFailure(result.code)
      return result.text
    } finally {
      signal.removeEventListener('abort', abort)
      this.core.discardAuthorizationPreview(preview.previewId)
      if (grantId) this.core.revokeAuthorization(grantId)
      for (const { materialId } of parts) this.core.releaseMaterial(materialId)
    }
  }

  private serial<T>(action: () => Promise<T>): Promise<T> {
    this.open()
    if (this.queued >= 32) return Promise.reject(new GatewayFailure('MODEL_UNAVAILABLE'))
    this.queued++
    const operation = this.tail.then(() => {
      this.open()
      return action()
    })
    this.tail = operation.then(
      () => {},
      () => {},
    )
    return operation.finally(() => {
      this.queued--
    })
  }
  private clearPreviews(context: Context): void {
    for (const id of context.previews.keys()) context.application.discardPreview(id)
    context.previews.clear()
  }
  private save(next: StoredConfiguration[]): Promise<void> {
    return this.persist(async () => {
      await this.repository.replace(this.configurations, next)
      return next
    })
  }
  private async persist(write: () => Promise<StoredConfiguration[]>): Promise<void> {
    let next: StoredConfiguration[]
    try {
      next = await write()
    } catch (error) {
      // A final record may exist despite a fsync/reconciliation failure. Continuing
      // with old memory, endpoints or grants would hide an uncertain durable update.
      this.failed = true
      this.context?.application.close()
      this.context = undefined
      for (const configuration of this.configurations)
        this.core.removeConfiguration(configuration.configurationId)
      throw error
    }
    this.open()
    this.configurations = next
  }
  async configure(input: ModelParamsMap['configureModel']): Promise<ModelConfiguration> {
    const context = this.current(input.contextId)
    return this.serial(async () => {
      this.same(context)
      const old = input.configurationId ? this.configuration(input.configurationId) : undefined
      if ((old?.configurationVersion ?? null) !== input.configurationVersion)
        throw new GatewayFailure('CONFIGURATION_CHANGED')
      if (!old && this.configurations.length >= 32) throw new GatewayFailure('INVALID_INPUT')
      const endpoint = normalizeEndpoint(input.endpoint, this.policy)
      const identityChanged = !old || endpoint !== old.endpoint || input.model !== old.model
      const next: StoredConfiguration = {
        configurationId: old?.configurationId ?? randomUUID(),
        configurationVersion: identityChanged ? randomUUID() : old.configurationVersion,
        displayName: input.displayName,
        endpoint,
        model: input.model,
        binding: old && endpoint === old.endpoint ? old.binding : null,
        ...(old?.enabled === undefined ? {} : { enabled: old.enabled }),
      }
      if (identityChanged) this.changing.add(next.configurationId)
      try {
        await this.save([
          ...this.configurations.filter((value) => value.configurationId !== next.configurationId),
          next,
        ])
        this.install(next)
        if (identityChanged) this.invalidateApprovals()
      } finally {
        this.changing.delete(next.configurationId)
      }
      // Saving global settings can finish after project changes, but no old project response is exposed.
      this.same(context)
      return this.visible(next)
    })
  }
  async storeCredential(
    input: ModelParamsMap['storeModelCredential'],
  ): Promise<ModelResultMap['storeModelCredential']> {
    const context = this.current(input.contextId)
    return this.serial(async () => {
      this.same(context)
      const before = this.configuration(input.configurationId)
      if (before.configurationVersion !== input.configurationVersion)
        throw new GatewayFailure('CONFIGURATION_CHANGED')
      this.changing.add(input.configurationId)
      try {
        const binding = await this.credentials.store(randomUUID(), input.secret)
        this.same(context)
        if (this.configuration(input.configurationId) !== before)
          throw new GatewayFailure('CONFIGURATION_CHANGED')
        const next = { ...before, configurationVersion: randomUUID(), binding }
        await this.save(this.configurations.map((value) => (value === before ? next : value)))
        this.install(next)
        if (this.context) {
          this.clearPreviews(this.context)
          this.context.grants.clear()
        }
        this.same(context)
        return {
          configurationId: next.configurationId,
          configurationVersion: next.configurationVersion,
          credentialState: 'configured',
        }
      } finally {
        this.changing.delete(input.configurationId)
      }
    })
  }
  setPrivacy(input: ModelParamsMap['setModelPrivacy']): ModelResultMap['setModelPrivacy'] {
    const context = this.current(input.contextId)
    if (context.privacy !== input.privacy) {
      this.core.setPrivacy(context.projectId, input.privacy)
      this.clearPreviews(context)
      context.grants.clear()
      context.privacy = input.privacy
    }
    return { privacy: context.privacy }
  }
  private replaceSelections(context: Context, selections: ModelSelection[]): void {
    this.same(context)
    this.clearPreviews(context)
    for (const id of context.selections.keys()) context.application.releaseSelection(id)
    context.selections = new Map(selections.map((value) => [value.selectionId, value]))
  }
  async selectResults(
    input: ModelParamsMap['selectModelResults'],
  ): Promise<ModelResultMap['selectModelResults']> {
    const context = this.current(input.contextId)
    return this.serial(async () => {
      this.same(context)
      const selections: ModelWholeResultSelection[] = []
      try {
        for (const result of input.results) {
          const selected = await context.application.selectStoredResult(result)
          selections.push({
            ...selected,
            kind: 'whole-result',
            selection: result.selection,
            metadata: selected.metadata as unknown as ModelWholeResultSelection['metadata'],
          })
          this.same(context)
        }
        this.replaceSelections(context, selections)
        return { selections: structuredClone(selections) }
      } catch (error) {
        for (const selection of selections)
          context.application.releaseSelection(selection.selectionId)
        throw error
      }
    })
  }
  async getCatalog(input: ModelParamsMap['getModelFieldCatalog']): Promise<ModelFieldCatalog> {
    const context = this.current(input.contextId)
    const catalog = await context.application.getFieldCatalog({
      resultId: input.resultId,
      selection: input.selection,
    })
    this.same(context)
    const visible: ModelFieldCatalog = {
      ...catalog,
      selection: input.selection,
      fields: catalog.fields as ModelFieldCatalog['fields'],
      metadata: catalog.metadata as unknown as ModelFieldCatalog['metadata'],
    }
    context.catalogs.set(catalog.catalogId, visible)
    const protectedIds = new Set(
      [...context.selections.values()]
        .filter((value) => value.kind === 'fields')
        .map((value) => value.catalogId),
    )
    for (const id of context.catalogs.keys()) {
      if (context.catalogs.size <= 16) break
      if (protectedIds.has(id)) continue
      context.catalogs.delete(id)
      context.application.releaseFieldCatalog(id)
    }
    return structuredClone(visible)
  }
  async selectFields(
    input: ModelParamsMap['selectModelFields'],
  ): Promise<ModelResultMap['selectModelFields']> {
    const context = this.current(input.contextId)
    return this.serial(async () => {
      this.same(context)
      const catalog = context.catalogs.get(input.catalogId)
      if (!catalog) throw new GatewayFailure('SCOPE_EXCEEDED')
      const projection = await context.application.selectFields({
        catalogId: input.catalogId,
        fieldIds: input.fieldIds,
      })
      try {
        this.same(context)
        const selection: ModelResultMap['selectModelFields'] = {
          kind: 'fields',
          selectionId: projection.selectionId,
          metadata: catalog.metadata,
          selection: catalog.selection,
          catalogId: input.catalogId,
          fieldIds: [...input.fieldIds],
          fields: catalog.fields.filter((field) => input.fieldIds.includes(field.fieldId)),
          projectionHash: projection.bodyHash,
          rowCount: projection.rowCount,
          byteCount: projection.byteCount,
        }
        this.replaceSelections(context, [selection])
        return structuredClone(selection)
      } catch (error) {
        context.application.releaseSelection(projection.selectionId)
        throw error
      }
    })
  }
  private choices(context: Context, ids: string[]): ModelSelection[] {
    return ids.map((id) => {
      const selection = context.selections.get(id)
      if (!selection) throw new GatewayFailure('SCOPE_EXCEEDED')
      return selection
    })
  }
  async preview(
    input: ModelParamsMap['previewModelExplanation'],
  ): Promise<ModelResultMap['previewModelExplanation']> {
    const context = this.current(input.contextId),
      configuration = this.configured(input.configurationId)
    const choices = this.choices(context, input.selectionIds)
    const preview = await context.application.preview({
      configId: input.configurationId,
      purpose: 'explain',
      selectionIds: input.selectionIds,
    })
    this.same(context)
    if (
      configuration !== this.configuration(input.configurationId) ||
      choices.some((value, index) => this.choices(context, input.selectionIds)[index] !== value)
    ) {
      context.application.discardPreview(preview.previewId)
      throw new GatewayFailure('CONFIGURATION_CHANGED')
    }
    const key = materialCanonical({
      version: preview.configVersion,
      scopes: preview.scopes,
      privacy: preview.privacy,
      purpose: 'explain',
    })
    const reusable = context.grants.get(key)
    if (reusable) context.application.discardPreview(preview.previewId)
    else
      context.previews.set(preview.previewId, {
        configurationId: configuration.configurationId,
        version: configuration.configurationVersion,
        key,
      })
    return {
      previewId: preview.previewId,
      configurationId: configuration.configurationId,
      configurationVersion: configuration.configurationVersion,
      endpoint: preview.endpoint,
      model: configuration.model,
      principal: preview.principal,
      purpose: 'explain',
      privacy: preview.privacy as 'minimal' | 'project',
      selections: structuredClone(choices),
      authorization: reusable ? { state: 'reusable', grantId: reusable } : { state: 'required' },
    }
  }
  confirm(
    input: ModelParamsMap['confirmModelAuthorization'],
  ): ModelResultMap['confirmModelAuthorization'] {
    const context = this.current(input.contextId),
      preview = context.previews.get(input.previewId)
    if (!preview) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    context.previews.delete(input.previewId)
    const configuration = this.configured(preview.configurationId)
    if (configuration.configurationVersion !== preview.version)
      throw new GatewayFailure('CONFIGURATION_CHANGED')
    const grantId = context.application.confirm(input.previewId)
    context.grants.set(preview.key, grantId)
    return { grantId, configurationVersion: configuration.configurationVersion }
  }
  private outcome(id: string, value: ApplicationOutcome): ModelExplanationOutcome {
    if (value.status === 'completed')
      return { invocationId: id, state: 'completed', text: value.text }
    if (value.status === 'cancelled')
      return { invocationId: id, state: 'cancelled', externalEffect: 'unknown' }
    return {
      invocationId: id,
      state: 'failed',
      error:
        value.failure.kind === 'source'
          ? safeError(value.failure.error)
          : modelSafeError(new GatewayFailure(value.failure.code)),
    }
  }
  private prune(context: Context): void {
    const terminal = [...context.invocations].filter(
      ([, value]) => value.state !== 'running' && value.state !== 'cancelling',
    )
    for (const [id] of terminal.slice(0, Math.max(0, terminal.length - 64)))
      context.invocations.delete(id)
  }
  start(input: ModelParamsMap['startModelExplanation']): ModelResultMap['startModelExplanation'] {
    const context = this.current(input.contextId)
    this.configured(input.configurationId)
    this.choices(context, input.selectionIds)
    const invocation = context.application.start({
      configId: input.configurationId,
      grantId: input.grantId,
      purpose: 'explain',
      selectionIds: input.selectionIds,
    })
    const running = { invocationId: invocation.invocationId, state: 'running' as const }
    context.invocations.set(running.invocationId, running)
    void invocation.completion
      .then((value) => {
        if (this.context !== context || this.closed) return
        context.invocations.set(running.invocationId, this.outcome(running.invocationId, value))
        this.prune(context)
      })
      .catch(() => {
        if (this.context !== context || this.closed) return
        context.invocations.set(running.invocationId, {
          invocationId: running.invocationId,
          state: 'failed',
          error: modelSafeError(undefined),
        })
        this.prune(context)
      })
    return running
  }
  getOutcome(input: ModelParamsMap['getModelExplanationOutcome']): ModelExplanationOutcome {
    const context = this.current(input.contextId),
      outcome = context.invocations.get(input.invocationId)
    if (!outcome) throw new GatewayFailure('AUTHORIZATION_REQUIRED')
    return structuredClone(outcome)
  }
  cancel(
    input: ModelParamsMap['cancelModelExplanation'],
  ): ModelResultMap['cancelModelExplanation'] {
    const context = this.current(input.contextId),
      outcome = this.getOutcome(input)
    if (outcome.state === 'running') {
      context.application.cancel(input.invocationId)
      const cancelling = {
        invocationId: input.invocationId,
        state: 'cancelling' as const,
      }
      context.invocations.set(input.invocationId, cancelling)
      return cancelling
    }
    return outcome
  }
  async close(): Promise<void> {
    if (this.closed) return
    this.closed = true
    this.context?.application.close()
    this.context = undefined
    await this.tail
  }
  async handle<M extends ModelMethod>(
    method: M,
    value: unknown,
  ): Promise<BridgeResult<ModelResultMap[M]>> {
    if (!validateModelParams(method, value)) return { ok: false, error: modelInvalidRequestError() }
    const copied = structuredClone(value) as ModelParamsMap[M]
    const handlers: {
      [K in ModelMethod]: (
        input: ModelParamsMap[K],
      ) => ModelResultMap[K] | Promise<ModelResultMap[K]>
    } = {
      getModelAccessStatus: ({ auditContextId }) =>
        auditContextId === undefined ? this.status() : this.readAudit(auditContextId),
      configureModel: (input) => this.configure(input),
      storeModelCredential: (input) => this.storeCredential(input),
      setModelPrivacy: (input) => this.setPrivacy(input),
      selectModelResults: (input) => this.selectResults(input),
      getModelFieldCatalog: (input) => this.getCatalog(input),
      selectModelFields: (input) => this.selectFields(input),
      previewModelExplanation: (input) => this.preview(input),
      confirmModelAuthorization: (input) => this.confirm(input),
      startModelExplanation: (input) => this.start(input),
      getModelExplanationOutcome: (input) => this.getOutcome(input),
      cancelModelExplanation: (input) => this.cancel(input),
    }
    try {
      const data = await handlers[method](copied)
      if (!validateModelResult(method, data) || !matchesModelResult(method, copied, data))
        return { ok: false, error: safeError(undefined) }
      return { ok: true, data }
    } catch (error) {
      return { ok: false, error: modelSafeError(error) }
    }
  }
}
