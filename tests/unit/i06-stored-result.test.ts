import fs from 'node:fs/promises'
import http from 'node:http'
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
import type { CredentialReader } from '../../apps/desktop/src/main/model-gateway/credentials'

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
async function fixture(payload = rows(), sameWriterCollectionHook = false) {
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
  options: { read?: CredentialReader['read']; status?: number } = {},
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
  const app = new GatewayApplication(core, f.source)
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
