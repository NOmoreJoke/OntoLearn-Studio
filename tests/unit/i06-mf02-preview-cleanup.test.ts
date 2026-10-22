// MF02: post-await preview ownership and bounded lifetime regression.
// Real service/application/core lifecycle; repository/source/credentials are explicit doubles.
// No Store, filesystem, safeStorage, receiver, native, or provider evidence is claimed.
import { randomUUID, createHash } from 'node:crypto'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import type { ConfigurationRepository } from '../../apps/desktop/src/main/model-gateway/configuration-repository'
import type { EncryptedCredentialBoundary } from '../../apps/desktop/src/main/model-gateway/credentials'
import type { ModelGatewayCore } from '../../apps/desktop/src/main/model-gateway/gateway'
import type { GatewayApplication } from '../../apps/desktop/src/main/model-gateway/gateway-application'
import { ModelGatewayService } from '../../apps/desktop/src/main/model-gateway/model-service'
import type {
  StoredResultSource,
  StoredResultMaterial,
} from '../../apps/desktop/src/main/model-gateway/stored-result-source'

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}
type Internal = {
  core: ModelGatewayCore
  context: {
    application: GatewayApplication
    previews: Map<string, unknown>
  }
}
const owners: ModelGatewayService[] = []
afterEach(async () => {
  vi.restoreAllMocks()
  for (const owner of owners.splice(0)) await owner.close()
})

async function setup() {
  const configurationId = randomUUID()
  const credentials = {
    read: vi.fn(async () => {
      throw new Error('UNEXPECTED_CREDENTIAL_READ')
    }),
  }
  const append = vi.fn(async () => {})
  const repository = {
    load: async () => [
      {
        configurationId,
        configurationVersion: randomUUID(),
        displayName: 'Synthetic lifecycle only',
        endpoint: 'https://example.invalid/model',
        model: 'synthetic',
        binding: { ref: randomUUID(), principal: randomUUID(), version: randomUUID() },
      },
    ],
  }
  const owner = await ModelGatewayService.open({
    engine: {} as EngineSupervisor,
    repository: repository as unknown as ConfigurationRepository,
    credentials: credentials as unknown as EncryptedCredentialBoundary,
    audit: { append },
  })
  owners.push(owner)
  owner.selectProject(randomUUID())
  const contextId = owner.status().contextId!
  owner.setPrivacy({ contextId, privacy: 'minimal' })
  const internal = owner as unknown as Internal
  const application = internal.context.application
  const source = (application as unknown as { source: StoredResultSource }).source
  const bodyText = JSON.stringify({ rows: [] })
  const material: StoredResultMaterial = {
    // Deliberately not a public ExistingV2Result fixture: these tests target only
    // lifecycle cleanup via direct typed selection calls, not source/schema proof.
    metadata: {},
    bodyText,
    bodyHash: createHash('sha256').update(bodyText).digest('hex'),
    sourceFingerprint: createHash('sha256').update('synthetic-source').digest('hex'),
  }
  const load = vi.spyOn(source, 'load').mockImplementation(() => Promise.resolve(material))
  const result = { resultId: randomUUID(), selection: 'current' as const }
  await owner.selectResults({ contextId, results: [result] })
  const created: string[] = []
  const events: string[] = []
  const originalPreview = internal.core.previewAuthorization.bind(internal.core)
  vi.spyOn(internal.core, 'previewAuthorization').mockImplementation((input) => {
    const value = originalPreview(input)
    created.push(value.previewId)
    events.push('preview-created')
    return value
  })
  const releaseSelection = application.releaseSelection.bind(application)
  vi.spyOn(application, 'releaseSelection').mockImplementation((selectionId) => {
    events.push('release-selection')
    releaseSelection(selectionId)
  })
  const invoke = vi.spyOn(internal.core, 'invoke')
  const applicationPreviews = (application as unknown as { previews: Set<string> }).previews
  const corePreviews = (internal.core as unknown as { previews: Map<string, unknown> }).previews

  async function replaceDuringPreview() {
    const createdBefore = created.length
    events.length = 0
    const selectionIds = owner.status().selections.map((value) => value.selectionId)
    const refreshing = deferred<StoredResultMaterial>()
    const replacing = deferred<StoredResultMaterial>()
    const replacementEntered = deferred<void>()
    load.mockImplementationOnce(() => refreshing.promise)
    load.mockImplementationOnce(() => {
      replacementEntered.resolve(undefined)
      return replacing.promise
    })
    const preview = owner.handle('previewModelExplanation', {
      contextId,
      configurationId,
      selectionIds,
    })
    const replacement = owner.selectResults({ contextId, results: [result] })
    await replacementEntered.promise
    // No added await/hook in application.preview or service.preview. Fulfill both
    // real source await boundaries in FIFO order within this same JS stack:
    // refresh continuation -> selectStoredResult continuation -> app.preview
    // creates P -> selectResults replaces S -> service.preview rechecks old S.
    refreshing.resolve(material)
    replacing.resolve(material)
    const [failed] = await Promise.all([preview, replacement])
    expect(created).toHaveLength(createdBefore + 1)
    expect(events).toEqual(['preview-created', 'release-selection'])
    return { failed, orphanId: created.at(-1)! }
  }
  return {
    owner,
    contextId,
    configurationId,
    replaceDuringPreview,
    applicationPreviews,
    corePreviews,
    servicePreviews: internal.context.previews,
    credentials,
    append,
    invoke,
  }
}

describe('MF02 post-await preview cleanup with explicit source doubles', () => {
  it('preserves the stale-selection error while reclaiming both hidden previews', async () => {
    const s = await setup()
    const { failed, orphanId } = await s.replaceDuringPreview()
    expect(failed).toMatchObject({
      ok: false,
      error: { code: 'GATEWAY_SCOPE_EXCEEDED', params: {}, retryable: false },
    })
    expect(s.servicePreviews.size).toBe(0)
    expect(s.applicationPreviews.size).toBe(0)
    expect(s.corePreviews.size).toBe(0)
    expect(
      await s.owner.handle('confirmModelAuthorization', {
        contextId: s.contextId,
        previewId: orphanId,
      }),
    ).toMatchObject({ ok: false, error: { code: 'GATEWAY_AUTHORIZATION_REQUIRED' } })
    expect(s.invoke).not.toHaveBeenCalled()
    expect(s.credentials.read).not.toHaveBeenCalled()
    expect(s.append).not.toHaveBeenCalled()
  })

  it('does not exhaust the 128 slots and preserves a normal preview until explicit confirmation', async () => {
    const s = await setup()
    for (let round = 0; round < 128; round++) {
      const { failed, orphanId } = await s.replaceDuringPreview()
      expect(failed).toMatchObject({
        ok: false,
        error: { code: 'GATEWAY_SCOPE_EXCEEDED', params: {}, retryable: false },
      })
      expect(s.servicePreviews.size).toBe(0)
      expect(s.applicationPreviews.size).toBe(0)
      expect(s.corePreviews.size).toBe(0)
      expect(
        await s.owner.handle('confirmModelAuthorization', {
          contextId: s.contextId,
          previewId: orphanId,
        }),
      ).toMatchObject({ ok: false, error: { code: 'GATEWAY_AUTHORIZATION_REQUIRED' } })
      expect(s.invoke).not.toHaveBeenCalled()
      expect(s.credentials.read).not.toHaveBeenCalled()
      expect(s.append).not.toHaveBeenCalled()
    }
    // Direct owner call keeps this metadata double outside public DTO success validation.
    // Also exercise successful ownership after repeated failures: cleanup must
    // not discard a normal required preview before the explicit confirmation.
    const preview = await s.owner.preview({
      contextId: s.contextId,
      configurationId: s.configurationId,
      selectionIds: s.owner.status().selections.map((value) => value.selectionId),
    })
    expect(preview.authorization).toEqual({ state: 'required' })
    expect(s.servicePreviews.size).toBe(1)
    expect(s.applicationPreviews.size).toBe(1)
    expect(s.corePreviews.size).toBe(1)
    expect(
      s.owner.confirm({ contextId: s.contextId, previewId: preview.previewId }).grantId,
    ).toEqual(expect.any(String))
    expect(s.servicePreviews.size).toBe(0)
    expect(s.applicationPreviews.size).toBe(0)
    expect(s.corePreviews.size).toBe(0)
    expect(s.invoke).not.toHaveBeenCalled()
    expect(s.credentials.read).not.toHaveBeenCalled()
    expect(s.append).not.toHaveBeenCalled()
  })
})
