import fs from 'node:fs/promises'
import http from 'node:http'
import https from 'node:https'
import tls from 'node:tls'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { randomUUID, createHash } from 'node:crypto'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { EngineSupervisor, getEngineCommand } from '../../apps/desktop/src/main/engine'
import {
  StoredResultSource,
  materialCanonical,
} from '../../apps/desktop/src/main/model-gateway/stored-result-source'
import { GatewayApplication } from '../../apps/desktop/src/main/model-gateway/gateway-application'
import { ModelGatewayCore } from '../../apps/desktop/src/main/model-gateway/gateway'
import { PersistentGatewayAudit } from '../../apps/desktop/src/main/model-gateway/persistent-audit'
import { PrivateCiphertextRepository } from '../../apps/desktop/src/main/model-gateway/ciphertext-repository'
import { ConfigurationRepository } from '../../apps/desktop/src/main/model-gateway/configuration-repository'
import { EncryptedCredentialBoundary } from '../../apps/desktop/src/main/model-gateway/credentials'
import { ModelGatewayService } from '../../apps/desktop/src/main/model-gateway/model-service'
import type { ModelMethod, ModelParamsMap } from '@ontolearn/contracts'
import type { PrivateWriteObserver } from '../../apps/desktop/src/main/model-gateway/private-directory'
import { finiteFixturePolicy } from '../../apps/desktop/src/main/model-gateway/finite-fixture-policy'
import type { CredentialReader } from '../../apps/desktop/src/main/model-gateway/credentials'
import {
  StoredFieldProjector,
  type StoredFieldModel,
} from '../../apps/desktop/src/main/model-gateway/stored-field-projector'

type Row = { rowId: string; ordinal: number; cells: (string | boolean | number | null)[] }
type Fixture = {
  projectId: string
  otherProjectId: string
  workerFile: string
  extraParametersHash: string
  atomicPreparedPlanRef: string
  atomicConfirmationRef: string
  input: Record<string, unknown>
}
const cleanups: (() => Promise<unknown> | void)[] = []
afterEach(async () => {
  vi.restoreAllMocks()
  for (const cleanup of cleanups.splice(0).reverse()) await cleanup()
})
const location = { packaged: false, appPath: path.resolve('apps/desktop'), resourcesPath: '' }
const python = getEngineCommand(location).command
function fixtureAction(database: string, action: string, data: unknown): Record<string, unknown> {
  const child = spawnSync(
    python,
    [
      '-I',
      path.resolve('tests/i06-stored-material/fixture.py'),
      action,
      database,
      JSON.stringify(data),
    ],
    {
      cwd: process.cwd(),
      encoding: 'utf8',
      timeout: 10000,
      maxBuffer: 1048576,
    },
  )
  expect(child.error).toBeUndefined()
  expect(child.status, child.stderr).toBe(0)
  return JSON.parse(child.stdout)
}
const rows = (count = 2, prefix = 'SYNTHETIC_RESULT') =>
  Array.from({ length: count }, (_, ordinal) => ({
    rowId: randomUUID(),
    ordinal,
    cells: [prefix + ordinal, ordinal],
  }))
async function fixture(payload: Row[] = rows(), sameWriterCollectionHook = false) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'i06-stored-result-'))
  cleanups.push(() => fs.rm(root, { recursive: true, force: true }))
  await fs.mkdir(path.join(root, 'project'))
  const database = path.join(root, 'project', 'engine.sqlite')
  const prepared = fixtureAction(database, 'prepare', payload) as unknown as Fixture
  expect(prepared.workerFile).toBe(path.resolve('packages/engine/src/ontolearn_engine/worker.py'))
  const engine = new EngineSupervisor(location, {
    dataPath: database,
    allowedProjects: [prepared.projectId, prepared.otherProjectId],
    testMode: true,
    registryPath: path.resolve('packages/contracts/v2/registry.json'),
    ...(sameWriterCollectionHook
      ? {
          command: {
            command: python,
            args: ['-I', path.resolve('tests/i06-stored-material/coordinator-fixture.py')],
          },
        }
      : {}),
  })
  cleanups.push(() => engine.stop())
  async function create(
    input = prepared.input,
    capability = 'test.read',
    confirmationRef: string | null = null,
  ): Promise<{ resultId: string; jobId: string; operationId: string }> {
    const operationId = randomUUID()
    const job = (await engine.request('job.create', {
      projectId: prepared.projectId,
      operationId,
      capability,
      input,
      confirmationRef,
    })) as Record<string, unknown>
    const deadline = Date.now() + 8000
    for (;;) {
      const latest = (await engine.request('job.get', {
        projectId: prepared.projectId,
        jobId: job.jobId,
      })) as Record<string, unknown>
      if (latest.state === 'succeeded')
        return {
          resultId: (latest.resultRef as { resultId: string }).resultId,
          jobId: String(job.jobId),
          operationId,
        }
      expect(['queued', 'running']).toContain(latest.state)
      if (Date.now() > deadline) throw new Error('SYNTHETIC_JOB_DEADLINE')
      await new Promise((resolve) => setTimeout(resolve, 10))
    }
  }
  const result = await create()
  const source = new StoredResultSource(engine, prepared.projectId, 'synthetic-test-runtime')
  cleanups.push(() => source.close())
  return { root, database, prepared, engine, source, result, create, payload }
}
function restartedSource(f: { database: string; prepared: Fixture }): StoredResultSource {
  const engine = new EngineSupervisor(location, {
    dataPath: f.database,
    allowedProjects: [f.prepared.projectId],
    testMode: true,
    registryPath: path.resolve('packages/contracts/v2/registry.json'),
  })
  const source = new StoredResultSource(engine, f.prepared.projectId, 'synthetic-test-runtime')
  cleanups.push(
    () => engine.stop(),
    () => source.close(),
  )
  return source
}
async function application(
  f: Awaited<ReturnType<typeof fixture>>,
  options: { read?: CredentialReader['read']; status?: number; models?: StoredFieldModel[] } = {},
) {
  const received: { body: string; authorization: string | undefined }[] = []
  const server = http.createServer((request, response) => {
    let body = ''
    request.on('data', (chunk) => {
      body += chunk
    })
    request.on('end', () => {
      received.push({ body, authorization: request.headers.authorization })
      response.writeHead(options.status ?? 200)
      response.end('SYNTHETIC_RESPONSE')
    })
  })
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve))
  cleanups.push(
    () =>
      new Promise<void>((resolve) => {
        server.closeAllConnections()
        server.close(() => resolve())
      }),
  )
  const address = server.address()
  if (!address || typeof address === 'string') throw new Error('RECEIVER')
  const audit = await PersistentGatewayAudit.open({
    userDataPath: path.join(f.root, 'userData'),
    excludedRoots: [path.join(f.root, 'project'), path.join(f.root, 'exports')],
  })
  cleanups.push(() => audit.close())
  const credential = {
    ref: randomUUID(),
    principal: randomUUID(),
    version: randomUUID(),
    secret: 'SYNTHETIC_GATEWAY_SECRET',
  }
  const core = new ModelGatewayCore(
    { read: options.read ?? (async () => ({ ...credential })) },
    audit,
    'loopback-probe-only',
  )
  const configId = randomUUID()
  core.configure({
    id: configId,
    endpoint: `http://127.0.0.1:${address.port}/synthetic`,
    credentialRef: credential.ref,
    principal: credential.principal,
    credentialVersion: credential.version,
    model: 'synthetic-only',
  })
  core.setPrivacy(f.prepared.projectId, 'minimal')
  const app = new GatewayApplication(core, f.source, options.models)
  cleanups.push(() => app.close())
  const selected = await app.selectStoredResult({
    resultId: f.result.resultId,
    selection: 'current',
  })
  async function authorize(selectionIds = [selected.selectionId]) {
    const preview = await app.preview({ configId, purpose: 'explain', selectionIds })
    return app.confirm(preview.previewId)
  }
  return { app, audit, received, core, configId, credential, selected, authorize }
}
function deferred() {
  let resolve!: () => void
  const promise = new Promise<void>((done) => {
    resolve = done
  })
  return { promise, resolve }
}

async function fieldModel(): Promise<StoredFieldModel> {
  return finiteFixturePolicy(
    createHash('sha256')
      .update(await fs.readFile('uv.lock'))
      .digest('hex'),
  )
}

function fieldRows(): Row[] {
  // Worker echoes actual structured fixture rows. Derived semantics are trusted finite-model policy,
  // not a claim that the approved synthetic worker computes arbitrary business provenance.
  return rows(3).map((row) => ({
    ...row,
    ordinal: 854736291 + row.ordinal,
    cells: [
      'I06_FINITE_FIELDS',
      `PUBLIC_VALUE_${row.ordinal}`,
      `PRIVATE_VALUE_SENTINEL_${row.ordinal}`,
      `PRIVATE_DERIVED_SENTINEL_${row.ordinal}`,
    ],
  }))
}

async function service(f: Awaited<ReturnType<typeof fixture>>, observer?: PrivateWriteObserver) {
  const certPath = path.join(f.root, 'synthetic-cert.pem'),
    keyPath = path.join(f.root, 'synthetic-key.pem')
  const generated = spawnSync(
    'openssl',
    [
      'req',
      '-x509',
      '-newkey',
      'rsa:2048',
      '-nodes',
      '-keyout',
      keyPath,
      '-out',
      certPath,
      '-subj',
      '/CN=127.0.0.1',
      '-addext',
      'subjectAltName=IP:127.0.0.1',
      '-days',
      '1',
    ],
    { encoding: 'utf8', timeout: 10000 },
  )
  expect(generated.status, generated.stderr).toBe(0)
  const cert = await fs.readFile(certPath, 'utf8'),
    key = await fs.readFile(keyPath, 'utf8')
  const oldCertificates = tls.getCACertificates('default')
  tls.setDefaultCACertificates([...oldCertificates, cert])
  cleanups.push(async () => {
    tls.setDefaultCACertificates(oldCertificates)
  })
  const received: string[] = []
  const server = https.createServer({ cert, key }, (request, response) => {
    let body = ''
    request.on('data', (chunk) => {
      body += chunk
    })
    request.on('end', () => {
      received.push(body)
      response.end('SYNTHETIC_SERVICE_RESPONSE <img src=x onerror=alert(1)>')
    })
  })
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve))
  cleanups.push(
    () =>
      new Promise<void>((resolve) => {
        server.closeAllConnections()
        server.close(() => resolve())
      }),
  )
  const address = server.address()
  if (!address || typeof address === 'string') throw new Error('RECEIVER')
  const endpoint = `https://127.0.0.1:${address.port}/synthetic`
  const location = {
    userDataPath: path.join(f.root, 'service-private'),
    excludedRoots: [path.join(f.root, 'project')],
  }
  const ciphertexts = await PrivateCiphertextRepository.open(location)
  const configurations = await ConfigurationRepository.open(location, observer)
  const audit = await PersistentGatewayAudit.open(location)
  cleanups.push(
    () => ciphertexts.close(),
    () => configurations.close(),
    () => audit.close(),
  )
  // Explicit safeStorage double in this headless service test; not OS encryption evidence.
  const boundary = new EncryptedCredentialBoundary(
    {
      isEncryptionAvailable: () => true,
      getSelectedStorageBackend: () => 'gnome_libsecret',
      encryptString: (value) => Buffer.from(Buffer.from(value).map((byte) => byte ^ 0xa5)),
      decryptString: (bytes) =>
        Buffer.from(Buffer.from(bytes).map((byte) => byte ^ 0xa5)).toString('utf8'),
    },
    ciphertexts,
    'linux',
  )
  const owner = await ModelGatewayService.open({
    engine: f.engine,
    repository: configurations,
    credentials: boundary,
    audit,
    producerPolicy: 'synthetic-test-runtime',
    fieldModels: [await fieldModel()],
  })
  cleanups.push(() => owner.close())
  expect(owner.status()).toMatchObject({
    availability: 'unavailable',
    contextId: null,
    projectId: null,
  })
  owner.selectProject(f.prepared.projectId)
  const contextId = owner.status().contextId!
  async function call<M extends ModelMethod>(method: M, params: ModelParamsMap[M]) {
    const reply = await owner.handle(method, params)
    expect(reply, method).toMatchObject({ ok: true })
    if (!reply.ok) throw new Error(reply.error.code)
    return reply.data
  }
  const configuration = await call('configureModel', {
    contextId,
    configurationId: null,
    configurationVersion: null,
    displayName: 'Synthetic local receiver',
    endpoint,
    model: 'synthetic',
  })
  const configured = await call('storeModelCredential', {
    contextId,
    configurationId: configuration.configurationId,
    configurationVersion: configuration.configurationVersion,
    secret: 'SYNTHETIC_SERVICE_SECRET',
  })
  async function terminal(invocationId: string) {
    const deadline = Date.now() + 8000
    for (;;) {
      const outcome = await call('getModelExplanationOutcome', { contextId, invocationId })
      if (outcome.state !== 'running' && outcome.state !== 'cancelling') return outcome
      if (Date.now() > deadline) throw new Error('SYNTHETIC_MODEL_DEADLINE')
      await new Promise((resolve) => setTimeout(resolve, 10))
    }
  }
  return {
    owner,
    configurations,
    boundary,
    endpoint,
    call,
    contextId,
    configuration: { ...configuration, ...configured },
    received,
    terminal,
    audit,
  }
}

describe('I06 named main model service with actual Store/worker and verified HTTPS receiver', () => {
  it('requires explicit consent, reuses public-field grant after a new actual worker result and restores only reads', async () => {
    const f = await fixture(fieldRows()),
      s = await service(f),
      { contextId } = s
    expect((await s.call('getModelAccessStatus', {})).privacy).toBe('local')
    const catalog = await s.call('getModelFieldCatalog', {
      contextId,
      resultId: f.result.resultId,
      selection: 'current',
    })
    const selected = await s.call('selectModelFields', {
      contextId,
      catalogId: catalog.catalogId,
      fieldIds: [catalog.fields[0].fieldId],
    })
    expect(selected.fields.map((field) => field.label)).toEqual(['Public label'])
    const input = {
      contextId,
      configurationId: s.configuration.configurationId,
      selectionIds: [selected.selectionId],
    }
    expect(await s.owner.handle('previewModelExplanation', input)).toMatchObject({
      ok: false,
      error: { code: 'GATEWAY_LOCAL_ONLY', params: {}, retryable: false },
    })
    await s.call('setModelPrivacy', { contextId, privacy: 'minimal' })
    const preview = await s.call('previewModelExplanation', input)
    expect(preview.authorization.state).toBe('required')
    const confirmation = await s.call('confirmModelAuthorization', {
      contextId,
      previewId: preview.previewId,
    })
    const second = await f.create()
    const fullSource = await f.source.load({ resultId: second.resultId, selection: 'current' })
    const nextCatalog = await s.call('getModelFieldCatalog', {
      contextId,
      resultId: second.resultId,
      selection: 'current',
    })
    const next = await s.call('selectModelFields', {
      contextId,
      catalogId: nextCatalog.catalogId,
      fieldIds: [nextCatalog.fields[0].fieldId],
    })
    const nextInput = { ...input, selectionIds: [next.selectionId] }
    const nextPreview = await s.call('previewModelExplanation', nextInput)
    expect(nextPreview.authorization).toEqual({ state: 'reusable', grantId: confirmation.grantId })
    const invocation = await s.call('startModelExplanation', {
      ...nextInput,
      grantId: confirmation.grantId,
    })
    const outcome = await s.terminal(invocation.invocationId)
    expect(outcome).toMatchObject({
      state: 'completed',
      text: expect.stringContaining('<img src=x onerror=alert(1)>'),
    })
    expect(s.received).toHaveLength(1)
    const actual = s.received[0]
    expect(actual).toContain('PUBLIC_VALUE_0')
    for (const marker of [
      'PRIVATE_',
      'SYNTHETIC_SERVICE_SECRET',
      fullSource.bodyHash,
      fullSource.sourceFingerprint,
      ...f.payload.flatMap((row) => [row.rowId, String(row.ordinal)]),
    ])
      expect(actual).not.toContain(marker)
    await s.call('getModelAccessStatus', {})
    await s.call('getModelExplanationOutcome', { contextId, invocationId: invocation.invocationId })
    expect(s.received).toHaveLength(1)
    const auditStatus = await s.call('getModelAccessStatus', { auditContextId: contextId })
    expect(auditStatus.audit).toEqual([
      {
        eventId: expect.any(String),
        targetId: s.configuration.configurationId,
        endpointOrigin: new URL(s.endpoint).origin,
        purpose: 'explain',
        scopes: [expect.any(String)],
        decision: 'authorized',
        event: 'attempt-intent',
        time: expect.any(String),
      },
    ])
    s.owner.selectProject(f.prepared.otherProjectId)
    expect(
      (await s.call('getModelAccessStatus', { auditContextId: s.owner.status().contextId! })).audit,
    ).toEqual([])
    s.owner.selectProject(f.prepared.projectId)
    expect(s.owner.status().privacy).toBe('local')
    expect(
      await s.owner.handle('getModelAccessStatus', { auditContextId: contextId }),
    ).toMatchObject({
      ok: false,
      error: { code: 'GATEWAY_AUTHORIZATION_REQUIRED' },
    })
    const raw = path.resolve('tests/i06-stored-material/out', `named-service-${randomUUID()}`)
    await fs.mkdir(raw, { recursive: true })
    await fs.writeFile(path.join(raw, 'receiver-body.json'), actual)
    await fs.writeFile(path.join(raw, 'source-tool-result.json'), fullSource.bodyText)
    await fs.writeFile(
      path.join(raw, 'receipt.json'),
      JSON.stringify(
        {
          contextId,
          firstResult: f.result.resultId,
          secondResult: second.resultId,
          preview,
          confirmation,
          nextPreview,
          outcome,
          receiverBodySHA256: createHash('sha256').update(actual).digest('hex'),
          boundary:
            'SafeStorage double; actual private ciphertext/configuration/audit stores and approved Store/worker; HTTPS certificate verified using test-worker-local CA only; no headers recorded',
        },
        null,
        2,
      ),
    )
  })

  it('rejects stale credential forms and leaves endpoint replacement missing credentials without copying the old key', async () => {
    const f = await fixture(fieldRows()),
      s = await service(f),
      { contextId } = s
    const changed = await s.call('configureModel', {
      contextId,
      configurationId: s.configuration.configurationId,
      configurationVersion: s.configuration.configurationVersion,
      displayName: 'Changed target',
      endpoint: s.endpoint + '/changed',
      model: 'synthetic',
    })
    expect(changed.credentialState).toBe('missing')
    expect(changed.configurationVersion).not.toBe(s.configuration.configurationVersion)
    const store = vi.spyOn(s.boundary, 'store')
    expect(
      await s.owner.handle('storeModelCredential', {
        contextId,
        configurationId: s.configuration.configurationId,
        configurationVersion: s.configuration.configurationVersion,
        secret: 'STALE_SECRET_MUST_NOT_INSTALL',
      }),
    ).toMatchObject({ ok: false, error: { code: 'GATEWAY_CONFIGURATION_CHANGED' } })
    expect(store).not.toHaveBeenCalled()
    const restored = (await s.configurations.load())[0]
    expect(restored).toMatchObject({ endpoint: changed.endpoint, binding: null })
    expect(s.received).toEqual([])
  })

  it('stops the model owner after post-publication failure and preserves the actual durable replacement for restart', async () => {
    let fail = false
    const f = await fixture(fieldRows()),
      s = await service(f, (phase) => {
        if (fail && phase === 'published') throw new Error('SYNTHETIC_POST_LINK_EIO')
      })
    const { contextId } = s
    await s.call('setModelPrivacy', { contextId, privacy: 'minimal' })
    const selected = await s.call('selectModelResults', {
      contextId,
      results: [{ resultId: f.result.resultId, selection: 'current' }],
    })
    const input = {
      contextId,
      configurationId: s.configuration.configurationId,
      selectionIds: selected.selections.map((value) => value.selectionId),
    }
    const preview = await s.call('previewModelExplanation', input)
    const confirmation = await s.call('confirmModelAuthorization', {
      contextId,
      previewId: preview.previewId,
    })
    const gate = deferred(),
      entered = deferred(),
      originalRead = s.boundary.read.bind(s.boundary)
    vi.spyOn(s.boundary, 'read').mockImplementation(async (ref) => {
      entered.resolve()
      await gate.promise
      return originalRead(ref)
    })
    const invocation = await s.call('startModelExplanation', {
      ...input,
      grantId: confirmation.grantId,
    })
    await entered.promise
    fail = true
    expect(
      await s.owner.handle('configureModel', {
        contextId,
        configurationId: s.configuration.configurationId,
        configurationVersion: s.configuration.configurationVersion,
        displayName: 'Uncertain replacement',
        endpoint: s.endpoint + '/after-publish',
        model: 'synthetic',
      }),
    ).toMatchObject({ ok: false, error: { code: 'GATEWAY_CREDENTIAL_UNAVAILABLE' } })
    gate.resolve()
    expect(await s.call('getModelAccessStatus', {})).toMatchObject({
      availability: 'unavailable',
      contextId: null,
    })
    expect(
      await s.owner.handle('startModelExplanation', { ...input, grantId: confirmation.grantId }),
    ).toMatchObject({ ok: false })
    expect(
      await s.owner.handle('getModelExplanationOutcome', {
        contextId,
        invocationId: invocation.invocationId,
      }),
    ).toMatchObject({ ok: false })
    expect((await s.configurations.load())[0]).toMatchObject({
      endpoint: s.endpoint + '/after-publish',
      binding: null,
    })
    expect(s.received).toEqual([])
  })
})

describe('I06 finite field policy over real approved Store/worker results', () => {
  it('reuses an explicitly granted public field after a second real worker result and emits zero private/derived bytes', async () => {
    const f = await fixture(fieldRows()),
      a = await application(f, { models: [await fieldModel()] })
    const first = await a.app.getFieldCatalog({ resultId: f.result.resultId, selection: 'current' })
    const selected = await a.app.selectFields({
      catalogId: first.catalogId,
      fieldIds: [first.fields[0].fieldId],
    })
    const grantId = await a.authorize([selected.selectionId])
    const secondResult = await f.create()
    expect(secondResult.resultId).not.toBe(f.result.resultId)
    const actualFullResult = await f.source.load({
      resultId: secondResult.resultId,
      selection: 'current',
    })
    expect(actualFullResult.bodyText).toContain('PRIVATE_VALUE_SENTINEL')
    expect(actualFullResult.bodyText).toContain('PRIVATE_DERIVED_SENTINEL')
    const second = await a.app.getFieldCatalog({
      resultId: secondResult.resultId,
      selection: 'current',
    })
    const next = await a.app.selectFields({
      catalogId: second.catalogId,
      fieldIds: [second.fields[0].fieldId],
    })
    let selectionId = next.selectionId
    for (const kind of ['tool', 'history', 'summary', 'error'] as const) {
      selectionId = a.app.projectFromFields({ inputs: [selectionId], kind })
      expect(() =>
        a.app.deriveFromMaterials({
          inputs: [selectionId],
          kind: 'summary',
          text: 'PRIVATE_VALUE_SENTINEL',
        }),
      ).toThrow('SCOPE_EXCEEDED')
      expect(
        await a.app.start({
          configId: a.configId,
          grantId,
          purpose: 'explain',
          selectionIds: [selectionId],
        }).completion,
      ).toMatchObject({ status: 'completed' })
    }
    expect(a.received).toHaveLength(4)
    for (const { body } of a.received) {
      expect(body).toContain('PUBLIC_VALUE_0')
      expect(body).toContain(secondResult.resultId)
      for (const row of f.payload) {
        expect(body).not.toContain(row.rowId)
        expect(body).not.toContain(String(row.ordinal))
      }
      for (const marker of [
        'PRIVATE_VALUE_SENTINEL',
        'PRIVATE_DERIVED_SENTINEL',
        'PRIVATE_LABEL_SENTINEL',
        'PRIVATE_DERIVED_LABEL_SENTINEL',
        String(f.prepared.input.parametersHash),
        actualFullResult.bodyHash,
        actualFullResult.sourceFingerprint,
      ])
        expect(body).not.toContain(marker)
    }
    const denied = await a.app.selectFields({
      catalogId: second.catalogId,
      fieldIds: [second.fields[1].fieldId],
    })
    expect(
      await a.app.start({
        configId: a.configId,
        grantId,
        purpose: 'explain',
        selectionIds: [denied.selectionId],
      }).completion,
    ).toMatchObject({ status: 'failed', failure: { code: 'SCOPE_EXCEEDED' } })
    expect(a.received).toHaveLength(4)
    expect(() =>
      a.app.projectFromFields({ inputs: [next.selectionId, a.selected.selectionId], kind: 'tool' }),
    ).toThrow('SCOPE_EXCEEDED')
    await expect(
      a.app.selectFields({ catalogId: second.catalogId, fieldIds: [first.fields[0].fieldId] }),
    ).rejects.toThrow('SCOPE_EXCEEDED')
    await expect(
      a.app.selectFields({ catalogId: second.catalogId, fieldIds: [second.fields[2].fieldId] }),
    ).rejects.toThrow('SCOPE_EXCEEDED')
    a.app.releaseFieldCatalog(second.catalogId)
    expect(
      await a.app.start({
        configId: a.configId,
        grantId,
        purpose: 'explain',
        selectionIds: [selectionId],
      }).completion,
    ).toMatchObject({ status: 'failed' })
    expect(a.received).toHaveLength(4)
  })

  it('copies trusted policy and reuses the same field scope only within that immutable model instance', async () => {
    const f = await fixture(fieldRows()),
      model = await fieldModel(),
      projector = new StoredFieldProjector(f.source, [model])
    const input = { resultId: f.result.resultId, selection: 'current' as const }
    model.fields[0].label = 'Changed after constructor'
    const catalog = await projector.catalog(input)
    expect(catalog.fields[0].label).toBe('Public label')
    const original = await projector.select({
      catalogId: catalog.catalogId,
      fieldIds: [catalog.fields[0].fieldId],
    })
    const second = await projector.catalog(input)
    expect(
      (
        await projector.select({
          catalogId: second.catalogId,
          fieldIds: [second.fields[0].fieldId],
        })
      ).scopes,
    ).toEqual(original.scopes)
    projector.close()
    await expect(projector.catalog(input)).rejects.toThrow('CANCELLED')
  })

  it('changes scope for selected values, cardinality and order, while excluding unselected values from field scope', async () => {
    const f = await fixture(fieldRows()),
      projector = new StoredFieldProjector(f.source, [await fieldModel()])
    const input = { resultId: f.result.resultId, selection: 'current' as const }
    const originalLoad = f.source.load.bind(f.source)
    const baseline = await originalLoad(input)
    let mutation = 'none'
    // Deliberate main-source boundary fault fixture; this is not a claim of a second Store mutation.
    vi.spyOn(f.source, 'load').mockImplementation(async () => {
      const value = structuredClone(baseline),
        body = JSON.parse(value.bodyText)
      if (mutation === 'selected') body.rows[0].cells[1] = 'CHANGED_PUBLIC'
      if (mutation === 'private') body.rows[0].cells[2] = 'CHANGED_PRIVATE'
      if (mutation === 'count') body.rows.pop()
      if (mutation === 'order')
        [body.rows[0].cells[1], body.rows[1].cells[1]] = [
          body.rows[1].cells[1],
          body.rows[0].cells[1],
        ]
      value.bodyText = materialCanonical(body)
      value.bodyHash = createHash('sha256').update(value.bodyText).digest('hex')
      value.sourceFingerprint = value.bodyHash
      return value
    })
    const select = async () => {
      const catalog = await projector.catalog(input)
      return projector.select({
        catalogId: catalog.catalogId,
        fieldIds: [catalog.fields[0].fieldId],
      })
    }
    const first = await select()
    mutation = 'private'
    expect((await select()).scopes).toEqual(first.scopes)
    for (mutation of ['selected', 'count', 'order'])
      expect((await select()).scopes).not.toEqual(first.scopes)
  })

  it.each(['local', 'configuration', 'cancel', 'release', 'middle'] as const)(
    'blocks the affected field request on %s before any receiver bytes',
    async (boundary) => {
      const f = await fixture(fieldRows()),
        gate = deferred(),
        entered = deferred()
      const a = await application(f, {
        models: [await fieldModel()],
        read: async () => {
          entered.resolve()
          await gate.promise
          return credential
        },
      })
      const credential = a.credential
      const catalog = await a.app.getFieldCatalog({
        resultId: f.result.resultId,
        selection: 'current',
      })
      const selected = await a.app.selectFields({
        catalogId: catalog.catalogId,
        fieldIds: [catalog.fields[0].fieldId],
      })
      const grantId = await a.authorize([selected.selectionId])
      const intermediate =
        boundary === 'middle'
          ? a.app.projectFromFields({ inputs: [selected.selectionId], kind: 'tool' })
          : selected.selectionId
      const requestSelection =
        boundary === 'middle'
          ? a.app.projectFromFields({ inputs: [intermediate], kind: 'summary' })
          : selected.selectionId
      const call = a.app.start({
        configId: a.configId,
        grantId,
        purpose: 'explain',
        selectionIds: [requestSelection],
      })
      await entered.promise
      if (boundary === 'local') a.core.setPrivacy(f.prepared.projectId, 'local')
      if (boundary === 'configuration')
        a.core.configure({
          id: a.configId,
          endpoint: 'http://127.0.0.1:65534/changed',
          credentialRef: a.credential.ref,
          principal: a.credential.principal,
          credentialVersion: a.credential.version,
          model: 'synthetic-only',
        })
      if (boundary === 'cancel')
        expect(a.app.cancel(call.invocationId)).toEqual({ requested: true })
      if (boundary === 'release') a.app.releaseSelection(selected.selectionId)
      if (boundary === 'middle') a.app.releaseSelection(intermediate)
      gate.resolve()
      expect((await call.completion).status).not.toBe('completed')
      expect(a.received).toEqual([])
      if (boundary === 'middle')
        expect(
          (
            await a.app.start({
              configId: a.configId,
              grantId,
              purpose: 'explain',
              selectionIds: [requestSelection],
            }).completion
          ).status,
        ).toBe('failed')
    },
  )

  it.each([
    [503, 2],
    [302, 1],
  ])(
    'keeps bounded field retry/redirect behavior for receiver status %i',
    async (status, count) => {
      const f = await fixture(fieldRows()),
        a = await application(f, { models: [await fieldModel()], status })
      const catalog = await a.app.getFieldCatalog({
        resultId: f.result.resultId,
        selection: 'current',
      })
      const selected = await a.app.selectFields({
        catalogId: catalog.catalogId,
        fieldIds: [catalog.fields[0].fieldId],
      })
      const grantId = await a.authorize([selected.selectionId])
      expect(
        (
          await a.app.start({
            configId: a.configId,
            grantId,
            purpose: 'explain',
            selectionIds: [selected.selectionId],
          }).completion
        ).status,
      ).toBe('failed')
      expect(a.received).toHaveLength(count)
      for (const { body } of a.received) expect(body).not.toContain('PRIVATE_')
    },
  )

  it.each(['tag', 'width', 'type'] as const)(
    'rejects actual stored %s mismatch before establishing a field catalog',
    async (failure) => {
      const payload = fieldRows()
      if (failure === 'tag') payload[0].cells[0] = 'UNKNOWN_TAG'
      if (failure === 'width') payload[0].cells.push('EXTRA_PRIVATE_SENTINEL')
      if (failure === 'type') payload[0].cells[1] = 42
      const f = await fixture(payload),
        a = await application(f, { models: [await fieldModel()] })
      await expect(
        a.app.getFieldCatalog({ resultId: f.result.resultId, selection: 'current' }),
      ).rejects.toThrow('SCOPE_EXCEEDED')
      expect(a.received).toEqual([])
    },
  )

  it('rejects unknown/ambiguous producer policies, cycles and missing transitive dependency selection', async () => {
    const f = await fixture(fieldRows()),
      model = await fieldModel()
    const input = { resultId: f.result.resultId, selection: 'current' as const }
    await expect(new StoredFieldProjector(f.source).catalog(input)).rejects.toThrow(
      'SCOPE_EXCEEDED',
    )
    await expect(new StoredFieldProjector(f.source, [model, model]).catalog(input)).rejects.toThrow(
      'SCOPE_EXCEEDED',
    )
    const cycle = structuredClone(model)
    cycle.fields[1].dependsOn = ['privateDerived']
    expect(() => new StoredFieldProjector(f.source, [cycle])).toThrow('SCOPE_EXCEEDED')
    const missing = structuredClone(model)
    missing.fields[0].dependsOn = ['absent']
    expect(() => new StoredFieldProjector(f.source, [missing])).toThrow('SCOPE_EXCEEDED')
    model.fields[0].dependsOn = ['privateDerived']
    const projector = new StoredFieldProjector(f.source, [model]),
      catalog = await projector.catalog(input)
    expect(catalog.fields[0].requires).toEqual(
      expect.arrayContaining([catalog.fields[1].fieldId, catalog.fields[2].fieldId]),
    )
    await expect(
      projector.select({
        catalogId: catalog.catalogId,
        fieldIds: [catalog.fields[0].fieldId, catalog.fields[2].fieldId],
      }),
    ).rejects.toThrow('SCOPE_EXCEEDED')
  })
})

describe('I06 real approved Store/coordinator/worker → private material → receiver', () => {
  it('reads every stored page, binds producer/version, hashes actual copied bytes and sends only after separate consent', async () => {
    const f = await fixture(rows(130))
    const source = await f.source.load({ resultId: f.result.resultId, selection: 'current' })
    const body = JSON.parse(source.bodyText)
    expect(body.rows).toEqual(f.payload)
    expect(body.source).toMatchObject({
      projectId: f.prepared.projectId,
      resultId: f.result.resultId,
      jobId: f.result.jobId,
      inputSnapshotId: f.prepared.input.inputSnapshotId,
      producerCapability: 'test.read',
      state: 'current',
    })
    expect(source.bodyHash).toBe(createHash('sha256').update(source.bodyText).digest('hex'))
    const a = await application(f)
    const call = {
      configId: a.configId,
      grantId: String(randomUUID()),
      purpose: 'explain' as const,
      selectionIds: [a.selected.selectionId],
    }
    expect(await a.app.start(call).completion).toMatchObject({
      status: 'failed',
      failure: { kind: 'gateway', code: 'AUTHORIZATION_REQUIRED' },
    })
    expect(a.received).toEqual([])
    call.grantId = await a.authorize()
    for (let i = 0; i < 2; i++)
      expect(await a.app.start(call).completion).toEqual({
        status: 'completed',
        text: 'SYNTHETIC_RESPONSE',
      })
    expect(a.received).toHaveLength(2)
    const actual = JSON.parse(a.received[0].body)
    expect(actual.parts).toEqual([{ kind: 'selected', text: source.bodyText }])
    expect(a.received[0].authorization).toBe('Bearer ' + a.credential.secret)
    const auditEntries = await a.audit.readEntries()
    expect(auditEntries.map(({ record }) => record.event)).toEqual(
      expect.arrayContaining(['blocked', 'attempt-intent', 'attempt-intent']),
    )
    const auditPath = path.join(f.root, 'userData/model-gateway-private-v1/audit')
    for (const file of await fs.readdir(auditPath)) {
      const raw = await fs.readFile(path.join(auditPath, file), 'utf8')
      expect(raw).not.toContain('SYNTHETIC_RESULT')
      expect(raw).not.toContain(a.credential.secret)
    }
  })

  it('rejects test producer in the normal policy and project reads without main permission', async () => {
    const f = await fixture()
    await expect(
      new StoredResultSource(f.engine, f.prepared.projectId).load({
        resultId: f.result.resultId,
        selection: 'current',
      }),
    ).rejects.toMatchObject({ error: { code: 'UNSUPPORTED_CAPABILITY' } })
    await expect(
      new StoredResultSource(f.engine, randomUUID(), 'synthetic-test-runtime').load({
        resultId: f.result.resultId,
        selection: 'current',
      }),
    ).rejects.toMatchObject({ error: { code: 'PERMISSION_DENIED' } })
    await expect(
      new StoredResultSource(f.engine, f.prepared.otherProjectId, 'synthetic-test-runtime').load({
        resultId: f.result.resultId,
        selection: 'current',
      }),
    ).rejects.toMatchObject({ error: { code: 'NOT_FOUND', params: { resource: 'result' } } })
  })

  it('requires explicit historical selection and reports real cache eviction', async () => {
    const f = await fixture()
    await f.create()
    await expect(
      f.source.load({ resultId: f.result.resultId, selection: 'current' }),
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
    const historical = await f.source.load({ resultId: f.result.resultId, selection: 'historical' })
    expect(historical.metadata.state).toBe('historical')
    f.source.close()
    f.engine.stop()
    const collected = fixtureAction(f.database, 'collect', {})
    expect(collected.evicted).toContain(f.result.resultId)
    await expect(
      restartedSource(f).load({ resultId: f.result.resultId, selection: 'historical' }),
    ).rejects.toMatchObject({ error: { code: 'PAYLOAD_EVICTED' } })
  })

  it('rejects a real result becoming historical after authorization before any POST', async () => {
    const f = await fixture(),
      a = await application(f)
    const grantId = await a.authorize()
    await f.create()
    expect(
      await a.app.start({
        configId: a.configId,
        grantId,
        purpose: 'explain',
        selectionIds: [a.selected.selectionId],
      }).completion,
    ).toMatchObject({
      status: 'failed',
      failure: { kind: 'source', error: { code: 'INVALID_STATE' } },
    })
    expect(a.received).toEqual([])
    expect(await a.audit.readEntries()).toEqual([])
  })

  it('discards all fragments on real same-writer collection between pages (explicit private fault hook)', async () => {
    const f = await fixture(rows(130), true)
    await f.create()
    await expect(
      f.source.load({ resultId: f.result.resultId, selection: 'historical' }),
    ).rejects.toMatchObject({ error: { code: 'PAYLOAD_EVICTED' } })
  })

  it.each(['binding', 'duplicate', 'cursor-cycle', 'producer', 'session', 'changed-state'])(
    'rejects injected %s corruption at the real engine response boundary',
    async (variant) => {
      const f = await fixture(rows(130))
      const original = f.engine.request.bind(f.engine)
      let resultReads = 0,
        pageReads = 0
      let firstRow: Row | undefined
      vi.spyOn(f.engine, 'request').mockImplementation(async (method, params) => {
        const value = structuredClone(await original(method, params)) as Record<string, unknown>
        if (method === 'job.get' && variant === 'producer')
          (value.resultRef as { resultId: string }).resultId = randomUUID()
        if (method === 'result.get') {
          resultReads++
          if (variant === 'changed-state' && resultReads === 2) {
            value.state = 'historical'
            value.historicalSelectionRequired = true
          }
        }
        if (method === 'result.page') {
          pageReads++
          if (variant === 'binding') (value.binding as { resultId: string }).resultId = randomUUID()
          if (variant === 'duplicate') {
            const incoming = value.rows as Row[]
            if (pageReads === 1) firstRow = incoming[0]
            else incoming[0] = firstRow!
          }
          if (variant === 'cursor-cycle') value.nextCursor = '00000000-0000-4000-8000-000000000001'
          if (variant === 'session')
            vi.spyOn(f.engine, 'engineSessionId', 'get').mockReturnValue(randomUUID())
        }
        return value
      })
      await expect(
        f.source.load({ resultId: f.result.resultId, selection: 'current' }),
      ).rejects.toBeInstanceOf(Error)
    },
  )

  it('rejects whole-result byte overflow without truncating or creating material', async () => {
    const f = await fixture(rows(9).map((row) => ({ ...row, cells: ['X'.repeat(8192)] })))
    await expect(
      f.source.load({ resultId: f.result.resultId, selection: 'current' }),
    ).rejects.toMatchObject({ error: { code: 'RESOURCE_LIMIT' } })
  })

  it('retains the union for tool/history/summary/error and blocks an unauthorized second result', async () => {
    const f = await fixture(),
      a = await application(f),
      grantId = await a.authorize()
    const otherResult = await f.create({
      ...f.prepared.input,
      parametersHash: f.prepared.extraParametersHash,
    })
    const second = await a.app.selectStoredResult({
      resultId: otherResult.resultId,
      selection: 'current',
    })
    for (const kind of ['tool', 'history', 'summary', 'error'] as const) {
      const derived = a.app.deriveFromMaterials({
        inputs: [a.selected.selectionId, second.selectionId],
        kind,
        text: 'SYNTHETIC_UNTRUSTED_IGNORE_PRIVACY',
      })
      expect(
        await a.app.start({
          configId: a.configId,
          grantId,
          purpose: 'explain',
          selectionIds: [derived],
        }).completion,
      ).toMatchObject({ status: 'failed', failure: { kind: 'gateway', code: 'SCOPE_EXCEEDED' } })
    }
    expect(a.received).toEqual([])
  })

  it('cancels only the named invocation, keeps the grant reusable, and leaves another call running', async () => {
    const f = await fixture(),
      entered = deferred(),
      release = deferred()
    let calls = 0
    const a = await application(f, {
      read: async () => {
        calls++
        if (calls === 1) {
          entered.resolve()
          await release.promise
        }
        return { ...a.credential }
      },
    })
    const grantId = await a.authorize(),
      input = {
        configId: a.configId,
        grantId,
        purpose: 'explain' as const,
        selectionIds: [a.selected.selectionId],
      }
    const first = a.app.start(input)
    await entered.promise
    const second = a.app.start(input)
    expect(a.app.cancel(first.invocationId)).toEqual({ requested: true })
    expect(await first.completion).toEqual({ status: 'cancelled' })
    expect(await second.completion).toEqual({ status: 'completed', text: 'SYNTHETIC_RESPONSE' })
    release.resolve()
    expect(await a.app.start(input).completion).toEqual({
      status: 'completed',
      text: 'SYNTHETIC_RESPONSE',
    })
    expect(a.received).toHaveLength(2)
    expect(a.app.cancel(first.invocationId)).toEqual({ requested: false })
  })

  it('rejects late selection after main project close without creating authority', async () => {
    const f = await fixture(),
      entered = deferred(),
      release = deferred()
    const original = f.engine.request.bind(f.engine)
    vi.spyOn(f.engine, 'request').mockImplementation(async (method, params) => {
      const result = await original(method, params)
      if (method === 'result.page') {
        entered.resolve()
        await release.promise
      }
      return result
    })
    const core = new ModelGatewayCore(
      {
        read: async () => {
          throw new Error('must not read')
        },
      },
      { append: async () => {} },
    )
    const app = new GatewayApplication(core, f.source)
    const pending = app.selectStoredResult({ resultId: f.result.resultId, selection: 'current' })
    const rejected = expect(pending).rejects.toThrow('CANCELLED')
    await entered.promise
    app.close()
    release.resolve()
    await rejected
  })

  it('keeps real Store.commit saving available while a model credential read is waiting and then fails', async () => {
    const f = await fixture(),
      entered = deferred(),
      release = deferred()
    const a = await application(f, {
      read: async () => {
        entered.resolve()
        await release.promise
        throw new Error('SYNTHETIC_SECRET_MUST_NOT_LEAK')
      },
    })
    const grantId = await a.authorize()
    const running = a.app.start({
      configId: a.configId,
      grantId,
      purpose: 'explain',
      selectionIds: [a.selected.selectionId],
    })
    await entered.promise
    const receipt = await f.create(
      { ...f.prepared.input, preparedPlanRef: f.prepared.atomicPreparedPlanRef },
      'test.atomic',
      f.prepared.atomicConfirmationRef,
    )
    const operation = await f.engine.request('operation.get', {
      projectId: f.prepared.projectId,
      operationId: receipt.operationId,
    })
    expect(operation).toMatchObject({ jobId: receipt.jobId, projectRevision: 1 })
    release.resolve()
    expect(await running.completion).toMatchObject({
      status: 'failed',
      failure: { kind: 'gateway', code: 'CREDENTIAL_UNAVAILABLE' },
    })
    const project = (await f.engine.request('project.get', {
      projectId: f.prepared.projectId,
    })) as Record<string, unknown>
    expect(project.projectRevision).toBe(1)
    a.app.close()
    f.engine.stop()
    const saved = fixtureAction(f.database, 'inspect', { projectId: f.prepared.projectId })
    expect(saved.revision).toBe(1)
    expect(materialCanonical(saved.snapshot)).toContain('i06-local-save')
    const db = await fs.readFile(f.database)
    expect(db.includes(Buffer.from('SYNTHETIC_SECRET_MUST_NOT_LEAK'))).toBe(false)
    expect(a.received).toEqual([])
  })

  it('compares actual body bytes again, rejecting validly shaped but altered response data after consent', async () => {
    const f = await fixture(),
      a = await application(f),
      grantId = await a.authorize()
    const original = f.engine.request.bind(f.engine)
    vi.spyOn(f.engine, 'request').mockImplementation(async (method, params) => {
      const value = structuredClone(await original(method, params)) as Record<string, unknown>
      if (method === 'result.page') (value.rows as Row[])[0].cells[0] = 'INJECTED_CHANGED_CONTENT'
      return value
    })
    expect(
      await a.app.start({
        configId: a.configId,
        grantId,
        purpose: 'explain',
        selectionIds: [a.selected.selectionId],
      }).completion,
    ).toMatchObject({ status: 'failed', failure: { kind: 'gateway', code: 'SCOPE_EXCEEDED' } })
    expect(a.received).toEqual([])
  })

  it('rejects a real current-pointer change during pagination after a second actual worker completes', async () => {
    const f = await fixture(rows(130)),
      original = f.engine.request.bind(f.engine)
    let first = true
    vi.spyOn(f.engine, 'request').mockImplementation(async (method, params) => {
      const value = await original(method, params)
      if (method === 'result.page' && first) {
        first = false
        await f.create()
      }
      return value
    })
    await expect(
      f.source.load({ resultId: f.result.resultId, selection: 'current' }),
    ).rejects.toMatchObject({ error: { code: 'INVALID_STATE' } })
  })

  it('releasing a stored leaf cancels its pending derived request before dispatch', async () => {
    const f = await fixture(),
      entered = deferred(),
      release = deferred()
    const a = await application(f, {
      read: async () => {
        entered.resolve()
        await release.promise
        return { ...a.credential }
      },
    })
    const grantId = await a.authorize()
    const derived = a.app.deriveFromMaterials({
      inputs: [a.selected.selectionId],
      kind: 'summary',
      text: 'SYNTHETIC_SUMMARY',
    })
    const running = a.app.start({
      configId: a.configId,
      grantId,
      purpose: 'explain',
      selectionIds: [derived],
    })
    await entered.promise
    a.app.releaseSelection(a.selected.selectionId)
    expect(await running.completion).toEqual({ status: 'cancelled' })
    release.resolve()
    expect(a.received).toEqual([])
    expect(
      await a.app.start({
        configId: a.configId,
        grantId,
        purpose: 'explain',
        selectionIds: [derived],
      }).completion,
    ).toMatchObject({ status: 'failed', failure: { code: 'SCOPE_EXCEEDED' } })
  })

  it('bounds the complete refresh and ignores a late real read after its actual deadline', async () => {
    const f = await fixture(),
      a = await application(f),
      entered = deferred(),
      release = deferred()
    const original = f.engine.request.bind(f.engine)
    vi.spyOn(f.engine, 'request').mockImplementation(async (method, params) => {
      const value = await original(method, params)
      if (method === 'result.page') {
        entered.resolve()
        await release.promise
      }
      return value
    })
    const running = a.app.preview({
      configId: a.configId,
      purpose: 'explain',
      selectionIds: [a.selected.selectionId],
    })
    const rejected = expect(running).rejects.toMatchObject({
      error: { code: 'TIMEOUT', params: { phase: 'total' } },
    })
    try {
      await entered.promise
      await rejected
    } finally {
      release.resolve()
    }
    expect(a.received).toEqual([])
    expect(await a.audit.readEntries()).toEqual([])
  }, 10000)

  it.each(['text', 'scopes', 'producerPolicy'])(
    'rejects renderer-like injected %s instead of trusting supplied source claims',
    async (field) => {
      const f = await fixture(),
        a = await application(f)
      await expect(
        a.app.selectStoredResult({
          resultId: f.result.resultId,
          selection: 'current',
          [field]: 'UNTRUSTED_SOURCE_CLAIM',
        } as never),
      ).rejects.toThrow('INVALID_INPUT')
      expect(a.received).toEqual([])
    },
  )
})
