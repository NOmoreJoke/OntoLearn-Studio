import { createHash } from 'node:crypto'
import { EventEmitter } from 'node:events'
import * as fs from 'node:fs/promises'
import { join } from 'node:path'
import { PassThrough, Writable } from 'node:stream'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type {
  BehaviorRunArgs,
  BridgeResult,
  MainlineChangePlanDTO,
  MainlineProjectBridge,
  HtmlReportExportResultDTO,
  PackageExportResultDTO,
  ScenarioCopyResultDTO,
  ScenarioReadResultDTO,
  ScenarioRunResultDTO,
  SafeError,
} from '@ontolearn/contracts'
import {
  AgentToolRegistry,
  FORMAL_WRITE_TOOLS,
} from '../../apps/desktop/src/main/agent/domain-ports'
import { outcomeSchema } from '../../apps/desktop/src/main/agent/agent-service'
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { validateBusiness3, v2Registry } from '../../packages/contracts/src/v2'
import fixtures from '../../packages/contracts/v2/fixtures.json'

const doubles = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn: doubles.spawn }))
vi.mock('node:fs/promises', async (original) => {
  const actual = await original<typeof fs>()
  return { ...actual, link: vi.fn(actual.link), lstat: vi.fn(actual.lstat) }
})
const actualFs = await vi.importActual<typeof fs>('node:fs/promises')

const id = (n: number) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
const projectId = id(1)
const snapshot = 'a'.repeat(64)
const sha256 = (data: Buffer) => createHash('sha256').update(data).digest('hex')
const denied: SafeError = {
  code: 'PERMISSION_DENIED',
  messageKey: 'permission.denied',
  params: {},
  retryable: false,
}
const permission = { ok: false, error: denied }
const unwrap = <T>(result: BridgeResult<T>): T => {
  if (!result.ok) throw new Error(JSON.stringify(result.error))
  return result.data
}

type Params = Record<string, unknown>
type Request = { id: string; method: string; params: Params }
const corpus = (method: string) =>
  fixtures.business3.responses.find(
    (item) => item.valid && item.name.startsWith('W4 ') && item.request.method === method,
  )!
const fixtureResult = <T>(method: string): T =>
  structuredClone((corpus(method).response as { result: unknown }).result) as T
const fixtureArgs = <T>(method: string): T => {
  const params = structuredClone(corpus(method).request.params) as Params
  delete params.projectId
  return params as T
}
const registryPath = join(process.cwd(), 'packages/contracts/v2/registry.json')

// Real supervisor, handoff, selection and service over an in-memory Engine peer.
// Only the peer answers frozen methods. Staging and publication use the real filesystem.
class Peer extends EventEmitter {
  readonly stdout = new PassThrough()
  readonly stderr = new PassThrough()
  readonly calls: Request[] = []
  exitCode: number | null = null
  signalCode: NodeJS.Signals | null = null
  handlers = new Map<string, (params: Params) => unknown>()
  readonly stdin = new Writable({
    write: (buffer, _encoding, done) => {
      const request = JSON.parse(buffer.toString()) as Request
      this.calls.push(request)
      void this.respond(request).then(() => done(), done)
    },
  })

  constructor(readonly session = id(90)) {
    super()
  }

  async respond({ method, params, id }: Request) {
    const result = this.handlers.has(method)
      ? await this.handlers.get(method)!(params)
      : await this.normal(method, params)
    const error = result && typeof result === 'object' && Object.hasOwn(result, 'messageKey')
    if (this.exitCode === null)
      this.stdout.write(
        JSON.stringify({
          kind: 'response',
          protocolVersion: method === 'hello' ? 2 : 3,
          engineSessionId: this.session,
          id,
          method,
          ok: !error,
          ...(error ? { error: result } : { result }),
        }) + '\n',
      )
  }

  async normal(method: string, params: Params) {
    switch (method) {
      case 'hello':
        return {
          selectedVersion: 3,
          engineVersion: '0.1.0',
          engineSessionId: this.session,
          capabilities: [
            'health',
            'session.ping',
            'project.get',
            'project.catalog',
            'project.create',
            'project.read',
            'project.open',
            'changeset.preview',
            ...Object.keys(v2Registry.wave4ResponseBindings),
          ],
          registryHash: sha256(await fs.readFile(registryPath)),
          limits: fixtures.queryConsumer.samples.prepared.executionIdentity.limits,
        }
      case 'session.ping':
        return { nonce: params.nonce }
      case 'project.open':
        return {
          projectId: params.projectId,
          projectRevision: 0,
          inputSnapshotId: snapshot,
          dependencyVector: { 'facts:asserted': 0 },
          formatVersion: 3,
        }
      default:
        return fixtureResult(method)
    }
  }

  async kill() {
    this.exitCode = 0
    queueMicrotask(() => this.emit('close', 0))
    return true
  }
}

type Picks = NonNullable<ConstructorParameters<typeof ProjectMainlineService>[3]>
let directory: string
let release: (() => void) | undefined
beforeEach(async () => {
  directory = await fs.realpath(await fs.mkdtemp(join(process.cwd(), 'node_modules/.w4-main-')))
})
afterEach(async () => {
  release?.()
  release = undefined
  vi.mocked(fs.link).mockReset().mockImplementation(actualFs.link)
  vi.mocked(fs.lstat).mockReset().mockImplementation(actualFs.lstat)
  await fs.rm(directory, { recursive: true, force: true })
})

async function setup(options: Picks = {}, withDataPath = true) {
  const peer = new Peer()
  doubles.spawn.mockReset().mockImplementation(() => {
    queueMicrotask(() => peer.emit('spawn'))
    return peer
  })
  const diagnostics: string[] = []
  const supervisor = new EngineSupervisor(
    { packaged: false, appPath: directory, resourcesPath: directory },
    {
      profile: 'business3',
      onDiagnostic: (event) => diagnostics.push(event),
      registryPath,
      command: { command: 'test-peer', args: [] },
      ...(withDataPath ? { dataPath: join(directory, 'library.db') } : {}),
    },
  )
  const tasks = new TaskService(supervisor)
  const service = new ProjectMainlineService(supervisor, tasks, () => {}, options)
  const receiver = supervisor.mainlineReplyReceiver()
  const receive = async <T>(work: () => Promise<BridgeResult<T>>): Promise<BridgeResult<T>> => {
    const { value, receipt } = await receiver.receive(work)
    receiver.consume(receipt)
    return value
  }
  release = () => {
    service.dispose()
    tasks.dispose()
    supervisor.stop()
  }
  const opened = await receive(() => service.openProject({ projectId }))
  if (!opened.ok)
    throw new Error(
      JSON.stringify({
        error: opened.error,
        diagnostics,
        calls: peer.calls.map(({ method }) => method),
      }),
    )
  return {
    service,
    peer,
    tasks,
    receiver,
    receive,
    root: options.stagingRoot ?? join(directory, '.ontolearn-host-selections'),
  }
}

const selectSource = 'project.mapping.source.select'
const beforeRun = 'project.run.before_commit'
const transportCalls = (peer: Peer) => peer.calls.map(({ method }) => method)
const selectedMeta = async (root: string, selectionId: string) => {
  const folder = join(root, selectionId)
  const metaPath = join(folder, 'meta.json')
  const meta: Params = JSON.parse(await fs.readFile(metaPath, 'utf8'))
  if (process.platform !== 'win32') {
    expect((await fs.stat(folder)).mode & 0o777).toBe(0o700)
    expect((await fs.stat(metaPath)).mode & 0o777).toBe(0o600)
  }
  expect(JSON.stringify(meta)).not.toContain(directory)
  return { folder, meta }
}
const installMapping = (peer: Peer) => {
  peer.handlers.set(selectSource, (params) => ({
    ...fixtureResult<Params>(selectSource),
    ...params,
    fields: [{ name: 'equipment', observedTypes: ['string'], samples: ['001'] }],
    totalRows: 1,
  }))
}
const expectAbsent = (path: string) =>
  expect(fs.lstat(path)).rejects.toMatchObject({ code: 'ENOENT' })

describe('selected files at the main process boundary', () => {
  it('stages the native source and package with exact private metadata and forwards only scoped tokens', async () => {
    const source = join(directory, '表格.CSV')
    const pack = join(directory, '源.ontolearn.zip')
    const bytes = Buffer.from('equipment\n001\n')
    await fs.writeFile(source, bytes)
    await fs.writeFile(pack, bytes)
    const pickMappingSource = vi.fn(async () => ({ filePath: source }))
    const pickTransferFile = vi.fn(async () => ({ filePath: pack }))
    const h = await setup({ pickMappingSource, pickTransferFile })
    installMapping(h.peer)
    const mapping = unwrap(
      await h.receive(() => h.service.selectMappingSource({ encoding: 'gb18030' })),
    )
    const selected = unwrap(
      await h.receive(() => h.service.selectTransferFile({ purpose: 'package-import' })),
    )
    expect(pickMappingSource).toHaveBeenCalledOnce()
    expect(pickTransferFile).toHaveBeenCalledExactlyOnceWith('package-import')
    expect(selected).toEqual({
      projectId,
      selectionId: selected.selectionId,
      purpose: 'package-import',
      extension: '.ontolearn.zip',
    })
    const expected = [
      [mapping.selectionId, 'mapping-source', 'csv', '.csv'],
      [selected.selectionId, 'package-import', 'zip', '.ontolearn.zip'],
    ] as const
    for (const [selectionId, purpose, format, extension] of expected) {
      const { folder, meta } = await selectedMeta(h.root, selectionId)
      expect(meta).toEqual({
        version: 1,
        selectionId,
        projectId,
        engineSessionId: h.peer.session,
        purpose,
        format,
        extension,
        payloadFile: 'payload' + extension,
        sha256: sha256(bytes),
        byteLength: bytes.length,
        createdAt: expect.stringMatching(/^\d{4}-\d\d-\d\dT.*Z$/),
      })
      const payload = join(folder, String(meta.payloadFile))
      if (process.platform !== 'win32') {
        expect((await fs.stat(payload)).mode & 0o777).toBe(0o600)
      }
      expect(await fs.readFile(payload)).toEqual(bytes)
      expect(await fs.readdir(folder)).toEqual(['meta.json', 'payload' + extension])
    }
    expect(
      JSON.stringify(h.peer.calls.filter(({ method }) => method === selectSource)),
    ).not.toContain(source)
    await h.receive(() =>
      h.service.readSelectedMappingSource(mapping.selectionId, new AbortController().signal),
    )
    expect(h.peer.calls.at(-1)?.params).toMatchObject({
      selectionId: mapping.selectionId,
      encoding: 'gb18030',
    })
    expect(
      await h.receive(() => h.service.selectMappingSource({ selectionId: selected.selectionId })),
    ).toEqual(permission)
    const importArgs = fixtureArgs<
      Parameters<MainlineProjectBridge['checkProjectPackageImport']>[0]
    >('project.transfer.package.import.check')
    h.peer.handlers.set('project.transfer.package.import.check', (params) => ({
      ...fixtureResult<Params>('project.transfer.package.import.check'),
      ...params,
    }))
    expect(
      (
        await h.receive(() =>
          h.service.checkProjectPackageImport({ ...importArgs, selectionId: selected.selectionId }),
        )
      ).ok,
    ).toBe(true)
    await h.receive(() => h.service.openProject({ projectId: id(2) }))
    await vi.waitFor(() => expect(fs.readdir(h.root)).resolves.toEqual([]))
    const calls = h.peer.calls.length
    expect(
      await h.receive(() => h.service.selectMappingSource({ selectionId: mapping.selectionId })),
    ).toEqual(permission)
    expect(
      await h.receive(() =>
        h.service.checkProjectPackageImport({ ...importArgs, selectionId: selected.selectionId }),
      ),
    ).toEqual(permission)
    expect(h.peer.calls).toHaveLength(calls)
  })

  it('stages XLSX with its exact format and only forwards owned preview and preparation requests', async () => {
    const filePath = join(directory, 'input.xlsx')
    const bytes = Buffer.from('synthetic workbook bytes')
    await fs.writeFile(filePath, bytes)
    const h = await setup({ pickMappingSource: async () => ({ filePath }) })
    h.peer.handlers.set(selectSource, (params) => ({
      ...fixtureResult<Params>(selectSource),
      ...params,
      format: 'xlsx',
      encoding: null,
      sheets: ['设备'],
      sheet: '设备',
    }))
    const source = unwrap(await h.receive(() => h.service.selectMappingSource({})))
    const { folder, meta } = await selectedMeta(h.root, source.selectionId)
    expect(meta).toMatchObject({ format: 'xlsx', extension: '.xlsx', payloadFile: 'payload.xlsx' })
    expect(await fs.readFile(join(folder, 'payload.xlsx'))).toEqual(bytes)
    const preview = 'project.mapping.preview'
    const prepare = 'project.mapping.prepare'
    for (const method of [preview, prepare])
      h.peer.handlers.set(method, (params) => ({
        ...fixtureResult<Params>(method),
        selectionId: params.selectionId,
        ...(method === preview ? { sheet: params.sheet, encoding: params.encoding } : {}),
      }))
    const args = {
      ...fixtureArgs<Parameters<MainlineProjectBridge['previewMapping']>[0]>(preview),
      sheet: '设备',
      encoding: null,
    }
    const prepareArgs =
      fixtureArgs<Parameters<MainlineProjectBridge['prepareMappingCommit']>[0]>(prepare)
    expect(await h.receive(() => h.service.previewMapping(args))).toEqual(permission)
    expect(await h.receive(() => h.service.prepareMappingCommit(prepareArgs))).toEqual(permission)
    expect(transportCalls(h.peer)).not.toContain(preview)
    expect(transportCalls(h.peer)).not.toContain(prepare)
    expect(
      (
        await h.receive(() =>
          h.service.previewMapping({ ...args, selectionId: source.selectionId }),
        )
      ).ok,
    ).toBe(true)
    expect(
      (
        await h.receive(() =>
          h.service.prepareMappingCommit({ ...prepareArgs, selectionId: source.selectionId }),
        )
      ).ok,
    ).toBe(true)
    expect(transportCalls(h.peer).slice(-2)).toEqual([preview, prepare])
  })

  it('retains Stage 0 fallback and validates both the request and selected project first', async () => {
    const h = await setup()
    expect(await h.receive(() => h.service.selectMappingSource({}))).toMatchObject({
      error: { code: 'UNSUPPORTED_CAPABILITY' },
    })
    expect(
      await h.receive(() => h.service.selectTransferFile({ purpose: 'report-html' })),
    ).toMatchObject({ error: { code: 'UNSUPPORTED_CAPABILITY' } })
    expect(await h.receive(() => h.service.selectMappingSource({ sheet: '' }))).toMatchObject({
      error: { code: 'INVALID_STATE' },
    })
    await h.service.source.closeSelection()
    expect(await h.service.selectTransferFile({ purpose: 'report-html' })).toEqual(permission)
  })

  it('fails before opening either configured picker when the staging root is absent from configuration', async () => {
    const pick = vi.fn(async () => ({ filePath: join(directory, 'source.csv') }))
    const h = await setup({ pickMappingSource: pick, pickTransferFile: pick }, false)
    expect(await h.receive(() => h.service.selectMappingSource({}))).toEqual(permission)
    expect(
      await h.receive(() => h.service.selectTransferFile({ purpose: 'package-import' })),
    ).toEqual(permission)
    expect(pick).not.toHaveBeenCalled()
  })

  it('rejects dialog cancellation, traversal, unknown tokens, suffix mismatch, symlinks and oversized input', async () => {
    const source = join(directory, 'source.csv')
    const large = join(directory, 'large.csv')
    await fs.writeFile(source, 't\n001\n')
    const handle = await fs.open(large, 'wx')
    await handle.truncate(8 * 1024 * 1024 + 1)
    await handle.close()
    const pick = vi
      .fn<Picks['pickMappingSource'] & (() => Promise<{ canceled: true } | { filePath: string }>)>()
      .mockResolvedValueOnce({ canceled: true })
    if (process.platform !== 'win32') {
      const alias = join(directory, 'alias.csv')
      await fs.symlink(source, alias)
      pick.mockResolvedValueOnce({ filePath: alias })
    }
    pick
      .mockResolvedValueOnce({ filePath: join(directory, 'source.csv.exe') })
      .mockResolvedValueOnce({ filePath: large })
      .mockResolvedValue({ filePath: source })
    const h = await setup({
      pickMappingSource: pick,
      pickTransferFile: async () => ({ filePath: join(directory, 'report.html.txt') }),
    })
    const rejectionCalls = process.platform === 'win32' ? 3 : 4
    for (let i = 0; i < rejectionCalls; i++)
      expect(await h.receive(() => h.service.selectMappingSource({}))).toEqual(permission)
    for (const selectionId of ['..', 'a..b', '../x', id(74)]) {
      const reply = await h.receive(() => h.service.selectMappingSource({ selectionId }))
      expect(reply.ok).toBe(false)
    }
    expect(await h.receive(() => h.service.selectTransferFile({ purpose: 'report-html' }))).toEqual(
      permission,
    )
    expect(h.peer.calls.some(({ method }) => method === selectSource)).toBe(false)
    expect(await fs.readdir(h.root)).toEqual([])
  })

  it.skipIf(process.platform === 'win32').each(['root', 'directory', 'meta.json', 'payload.csv'])(
    'rejects a replaced %s on an already selected source',
    async (entry) => {
      const source = join(directory, 'source.csv')
      await fs.writeFile(source, 'equipment\n001\n')
      const h = await setup({ pickMappingSource: async () => ({ filePath: source }) })
      installMapping(h.peer)
      const result = unwrap(await h.receive(() => h.service.selectMappingSource({})))
      const folder = join(h.root, result.selectionId)
      const path = entry === 'root' ? h.root : entry === 'directory' ? folder : join(folder, entry)
      const original = path + '-original'
      await fs.rename(path, original)
      await fs.symlink(original, path)
      try {
        const count = transportCalls(h.peer).length
        expect(
          await h.receive(() => h.service.selectMappingSource({ selectionId: result.selectionId })),
        ).toEqual(permission)
        expect(h.peer.calls).toHaveLength(count)
      } finally {
        await fs.unlink(path)
        await fs.rename(original, path)
      }
    },
  )

  it.each(['close', 'session', 'dispose'])(
    'invalidates and cleans selection on %s',
    async (action) => {
      const stagingRoot = join(directory, 'explicit-staging-root')
      const destination = join(directory, 'report.html')
      const h = await setup({
        stagingRoot,
        pickTransferFile: async () => ({ filePath: destination }),
      })
      const { selectionId } = unwrap(
        await h.receive(() => h.service.selectTransferFile({ purpose: 'report-html' })),
      )
      const staged = join(stagingRoot, selectionId)
      if (action === 'close') await h.service.source.closeSelection()
      else if (action === 'session') await h.peer.kill()
      else h.service.dispose()
      await vi.waitFor(() => expectAbsent(staged))
      const reportArgs = fixtureArgs<
        Parameters<MainlineProjectBridge['exportProjectHtmlReport']>[0]
      >('project.transfer.report.export')
      expect(await h.service.exportProjectHtmlReport({ ...reportArgs, selectionId })).toEqual(
        permission,
      )
    },
  )

  it('does not resurrect a native selection after an ABA project switch', async () => {
    const source = join(directory, 'source.csv')
    await fs.writeFile(source, 'equipment\n001\n')
    let chosen!: (value: { filePath: string }) => void
    const pick = vi.fn(
      () =>
        new Promise<{ filePath: string }>((resolve) => {
          chosen = resolve
        }),
    )
    const h = await setup({ pickMappingSource: pick })
    const outstanding = h.service.selectMappingSource({})
    expect(pick).toHaveBeenCalledOnce()
    await h.receive(() => h.service.openProject({ projectId: id(2) }))
    await h.receive(() => h.service.openProject({ projectId }))
    chosen({ filePath: source })
    expect(await outstanding).toEqual(permission)
    await expectAbsent(h.root)
    expect(transportCalls(h.peer)).not.toContain(selectSource)
  })
})

const publicationOutcomes =
  process.platform === 'win32'
    ? [
        'published',
        'target-exists',
        'publication-unconfirmed',
        'hash',
        'size',
        'missing',
        'engine-cancelled',
      ]
    : [
        'published',
        'target-exists',
        'destination-symlink',
        'publication-unconfirmed',
        'hash',
        'size',
        'symlink',
        'missing',
        'engine-cancelled',
      ]

describe.each([
  { purpose: 'report-html' as const, extension: '.html', method: 'project.transfer.report.export' },
  {
    purpose: 'package-export' as const,
    extension: '.ontolearn.zip',
    method: 'project.transfer.package.export',
  },
])('main publication of $extension', ({ purpose, extension, method }) => {
  it.each(publicationOutcomes)('projects %s from private staged bytes', async (outcome) => {
    const destination = join(directory, 'target' + extension)
    const bytes = Buffer.from('exact staged output\n')
    const h = await setup({ pickTransferFile: async () => ({ filePath: destination }) })
    const { selectionId } = unwrap(await h.receive(() => h.service.selectTransferFile({ purpose })))
    const { folder, meta } = await selectedMeta(h.root, selectionId)
    expect(meta).toEqual({
      version: 1,
      selectionId,
      projectId,
      engineSessionId: h.peer.session,
      purpose,
      extension,
      outputFile: 'output' + extension,
      createdAt: expect.any(String),
    })
    const engineOutput = join(folder, String(meta.outputFile))
    if (outcome === 'target-exists') await fs.writeFile(destination, 'unrelated')
    const unrelated = join(directory, 'unrelated')
    if (outcome === 'destination-symlink') {
      await fs.writeFile(unrelated, 'leave this intact')
      await fs.symlink(unrelated, destination)
    }
    if (outcome === 'publication-unconfirmed') {
      vi.mocked(fs.link).mockImplementationOnce(async (src, dst) => {
        await actualFs.link(src, dst)
        vi.mocked(fs.lstat).mockImplementationOnce(async () => {
          throw Object.assign(new Error(destination), { code: 'EIO' })
        })
        throw Object.assign(new Error(destination), { code: 'EIO' })
      })
    }
    h.peer.handlers.set(method, async (params) => {
      expect(Object.keys(params)).not.toContain('destinationPath')
      if (outcome === 'symlink') {
        const real = join(directory, 'other' + extension)
        await fs.writeFile(real, bytes)
        await fs.symlink(real, engineOutput)
      } else if (outcome !== 'missing' && outcome !== 'engine-cancelled') {
        await fs.writeFile(engineOutput, bytes, { mode: 0o600 })
      }
      return {
        ...fixtureResult<Params>(method),
        selectionId,
        publication:
          outcome === 'engine-cancelled'
            ? { state: 'cancelled', cleanup: 'complete' }
            : {
                state: 'published',
                sha256: outcome === 'hash' ? snapshot : sha256(bytes),
                byteLength: outcome === 'size' ? bytes.length + 1 : bytes.length,
                cleanup: 'complete',
                durability: 'confirmed',
                postPublicationError: false,
              },
      }
    })
    const exportFile = () =>
      purpose === 'report-html'
        ? h.service.exportProjectHtmlReport({
            ...fixtureArgs<Parameters<MainlineProjectBridge['exportProjectHtmlReport']>[0]>(method),
            selectionId,
          })
        : h.service.exportProjectPackage({
            ...fixtureArgs<Parameters<MainlineProjectBridge['exportProjectPackage']>[0]>(method),
            selectionId,
          })
    const reply = unwrap(
      await h.receive<HtmlReportExportResultDTO | PackageExportResultDTO>(exportFile),
    )
    expect(validateBusiness3('result_' + method, reply)).toBe(true)
    expect(JSON.stringify(reply)).not.toContain(destination)
    await expectAbsent(folder)
    if (outcome === 'published' || outcome === 'publication-unconfirmed') {
      expect(reply.publication).toMatchObject({
        state: outcome,
        sha256: sha256(bytes),
        byteLength: bytes.length,
        cleanup: 'complete',
      })
      expect(await fs.readFile(destination)).toEqual(bytes)
      if (process.platform !== 'win32') {
        expect((await fs.stat(destination)).mode & 0o777).toBe(0o600)
      }
    } else if (outcome === 'target-exists') {
      expect(reply.publication).toEqual({ state: 'failed', code: outcome, cleanup: 'complete' })
      expect(await fs.readFile(destination, 'utf8')).toBe('unrelated')
    } else if (outcome === 'destination-symlink') {
      expect(reply.publication).toEqual({
        state: 'failed',
        code: 'destination-invalid',
        cleanup: 'complete',
      })
      expect(await fs.readlink(destination)).toBe(unrelated)
      expect(await fs.readFile(unrelated, 'utf8')).toBe('leave this intact')
    } else {
      expect(reply.publication).toEqual(
        outcome === 'engine-cancelled'
          ? { state: 'cancelled', cleanup: 'complete' }
          : { state: 'failed', code: 'write-failed', cleanup: 'complete' },
      )
      await expectAbsent(destination)
    }
    expect(await exportFile()).toEqual(permission)
  })
})

describe('run checkpoint and ChangeSet forwarding', () => {
  it.each([
    ['project.behavior.run', 'runBehaviorSample', 'behavior'],
    ['project.scenario.run', 'startScenarioRun', 'scenario'],
    ['project.scenario.resume', 'resumeScenarioRun', 'scenario'],
  ] as const)(
    'registers an exact checkpoint before %s and fails closed otherwise',
    async (method, entry, domain) => {
      const h = await setup()
      const checkpoint = fixtureResult<Params>(beforeRun)
      let reply: unknown = denied
      h.peer.handlers.set(beforeRun, () => reply)
      const request = fixtureArgs<never>(method)
      const call = () => h.service[entry](request) as Promise<BridgeResult<unknown>>
      const offset = h.peer.calls.length
      expect(await h.receive(call)).toEqual(permission)
      expect(transportCalls(h.peer).slice(offset)).toEqual([beforeRun])
      reply = checkpoint
      expect((await h.receive(call)).ok).toBe(true)
      expect(transportCalls(h.peer).slice(offset)).toEqual([beforeRun, beforeRun, method])
      expect(h.peer.calls[offset + 1]?.params).toEqual({
        projectId,
        operationId: id(1),
        domain,
        baseRevision: 0,
        label: null,
      })
    },
  )

  it('rejects a checkpoint response bound to another operation and never starts the run', async () => {
    const h = await setup()
    h.peer.handlers.set(beforeRun, () => ({
      ...fixtureResult<Params>(beforeRun),
      operationId: id(2),
    }))
    const failed = await h.receiver.receive(() =>
      h.service.runBehaviorSample(fixtureArgs<BehaviorRunArgs>('project.behavior.run')),
    )
    expect(failed.value.ok).toBe(false)
    expect(() => h.receiver.consume(failed.receipt)).toThrow('INVALID_STATE')
    expect(transportCalls(h.peer).at(-1)).toBe(beforeRun)
  })

  it('keeps the old run fenced when the selected project changes during before-run', async () => {
    const h = await setup()
    let resolve!: (result: unknown) => void
    h.peer.handlers.set(
      beforeRun,
      () =>
        new Promise((settle) => {
          resolve = settle
        }),
    )
    const pending = h.service.runBehaviorSample(
      fixtureArgs<BehaviorRunArgs>('project.behavior.run'),
    )
    await vi.waitFor(() => expect(resolve).toBeDefined())
    await h.service.source.closeSelection()
    resolve(fixtureResult(beforeRun))
    expect(await pending).toEqual(permission)
    expect(transportCalls(h.peer)).not.toContain('project.behavior.run')
  })

  it('forwards prepared and manual plans via the ordinary validator and rejects a mixed plan', async () => {
    const h = await setup()
    // Use a valid engine error as a sentinel that the pinned call really reached the peer.
    h.peer.handlers.set('changeset.preview', () => denied)
    const prepared = fixtures.cases.find(
      ({ name }) => name === 'W4 mapping preparation uses existing ChangeSet type',
    )!.value as MainlineChangePlanDTO
    const manual = {
      manual: [{ id: 'b'.repeat(64), subject: 'urn:one', predicate: 'urn:two', object: '"ok"' }],
    }
    for (const plan of [prepared, manual]) {
      const result = await h.receive(() =>
        h.service.previewProjectChangeset({ baseRevision: 0, intent: 'change', plan }),
      )
      expect(result).toEqual(permission)
      expect(h.peer.calls.at(-1)).toMatchObject({
        method: 'changeset.preview',
        params: { projectId, baseRevision: 0, intent: 'change', plan },
      })
    }
    const count = h.peer.calls.length
    expect(
      await h.receive(() =>
        h.service.previewProjectChangeset({
          baseRevision: 0,
          intent: 'change',
          plan: { ...prepared, ...manual } as MainlineChangePlanDTO,
        }),
      ),
    ).toMatchObject({ error: { code: 'INVALID_STATE' } })
    expect(h.peer.calls).toHaveLength(count)
  })
})

describe('Wave 4 Agent ports through the selected-project service', () => {
  const scenarioRead = 'project.scenario.read'
  const scenarioCopy = 'project.scenario.copy'
  const scenarioStart = 'project.scenario.run'
  const behaviorRun = 'project.behavior.run'
  const mappingArgs = { sourceId: 'source-ref', instruction: 'do not echo /private/model-input' }
  const context = {
    projectId,
    projectRevision: 0,
    inputSnapshotId: snapshot,
    scopeRef: id(50),
    module: 'mapping' as const,
    mode: 'project' as const,
    selectedObjectIds: ['source-ref', 'behavior-ref', 'sample-ref', 'scenario-ref'],
  }
  const makeRegistry = (
    h: Awaited<ReturnType<typeof setup>>,
    objectRefs: Map<string, string>,
    current = () => true,
  ) =>
    new AgentToolRegistry({
      waveFourEnabled: true,
      projects: h.service,
      tasks: h.tasks,
      receive: h.receive,
      scope: 'asserted',
      current,
      objectRefs,
    })

  it('generates a deterministic source-relative mapping draft from the authorized token', async () => {
    const filePath = join(directory, 'source.csv')
    const secret = 'credential-sample-opaque'
    await fs.writeFile(filePath, 'equipment\n001\n')
    const h = await setup({ pickMappingSource: async () => ({ filePath }) })
    installMapping(h.peer)
    const { selectionId } = unwrap(await h.receive(() => h.service.selectMappingSource({})))
    h.peer.handlers.set(selectSource, (params) => ({
      ...fixtureResult<Params>(selectSource),
      ...params,
      fields: [{ name: filePath, observedTypes: ['string'], samples: [secret] }],
      totalRows: 1,
      suggestions: [
        {
          column: filePath,
          predicate: 'urn:' + secret,
          basis: 'exact-field-name',
          samples: [secret],
        },
      ],
    }))
    const registry = makeRegistry(h, new Map([['source-ref', selectionId]]))
    const signal = new AbortController().signal
    expect(
      registry
        .entries()
        .filter(({ wave }) => wave === 4)
        .map(({ enabled }) => enabled),
    ).toEqual([true, true, true])
    expect(Object.keys(registry.buildPorts())).toHaveLength(10)
    expect(FORMAL_WRITE_TOOLS).toEqual([])
    const result = outcomeSchema.parse(
      await registry.execute('mapping_propose', context, mappingArgs, signal),
    )
    expect(result.kind).toBe('draft')
    if (result.kind !== 'draft') throw new Error('expected draft')
    expect(JSON.parse(result.detail)).toEqual({
      sourceId: 'source-ref',
      format: 'csv',
      fieldCount: 1,
      totalRows: 1,
      matches: [{ columnIndex: 0, suggestionIndex: 0, basis: 'exact-field-name', sampleCount: 1 }],
    })
    expect(JSON.stringify(result)).not.toContain(directory)
    expect(JSON.stringify(result)).not.toContain(secret)
    expect(JSON.stringify(result)).not.toContain('/private/model-input')
    expect(await registry.execute('mapping_propose', context, mappingArgs, signal)).toEqual(result)
    const count = h.peer.calls.length
    await expect(
      registry.execute('mapping_propose', context, { ...mappingArgs, sourceId: id(50) }, signal),
    ).rejects.toThrow('TOOL_NOT_ALLOWED')
    expect(h.peer.calls).toHaveLength(count)
  })

  it('runs a host-captured sample in a fresh isolated binding and projects the safe state', async () => {
    const h = await setup()
    const params = fixtureArgs<Omit<BehaviorRunArgs, 'projectId'>>(behaviorRun)
    params.events[0]!.payload = { privatePath: directory, token: 'sample-secret' }
    unwrap(await h.receive(() => h.service.runBehaviorSample(params)))
    h.peer.handlers.set(beforeRun, (request) => ({
      ...fixtureResult<Params>(beforeRun),
      operationId: request.operationId,
    }))
    h.peer.handlers.set(behaviorRun, (request) => ({
      ...fixtureResult<Params>(behaviorRun),
      operationId: request.operationId,
      runId: request.runId,
      binding: request.binding,
      state: 'failed',
      error: { code: 'conflict', messageKey: 'behavior.conflict' },
    }))
    const registry = makeRegistry(
      h,
      new Map([
        ['behavior-ref', params.draft.id],
        ['sample-ref', params.binding.scopeId],
      ]),
    )
    const args = { behaviorId: 'behavior-ref', sampleId: 'sample-ref' }
    const signal = new AbortController().signal
    const result = outcomeSchema.parse(
      await registry.execute('behavior_test', context, args, signal),
    )
    const [checkpoint, replay] = h.peer.calls.slice(-2)
    expect(checkpoint!.method).toBe(beforeRun)
    expect(replay!.method).toBe(behaviorRun)
    expect(checkpoint!.params.operationId).toBe(replay!.params.operationId)
    expect(replay!.params).toMatchObject({
      scope: 'sample',
      draft: params.draft,
      events: params.events,
    })
    expect(replay!.params.binding).not.toMatchObject({ scopeId: params.binding.scopeId })
    expect(replay!.params.runId).not.toBe(params.runId)
    expect(result).toMatchObject({
      kind: 'evidence',
      status: 'failed',
      resultId: replay!.params.runId,
      fields: [
        { fieldId: 'freshness', value: 'current' },
        { fieldId: 'state', value: 'failed' },
        { fieldId: 'error', value: 'conflict' },
      ],
    })
    expect(JSON.stringify(result)).not.toContain('sample-secret')
    await expect(
      registry.execute('behavior_test', { ...context, projectRevision: 1 }, args, signal),
    ).rejects.toThrow('TOOL_FAILED')
  })

  it('reads the authorized scenario, runs its isolated copy and returns bounded metrics', async () => {
    const h = await setup()
    const original = fixtureResult<ScenarioReadResultDTO>(scenarioRead)
    const scenarioId = original.scenario.identity.scenarioId
    const copyId = id(20)
    h.peer.handlers.set(scenarioCopy, (request) => {
      const copy = fixtureResult<ScenarioCopyResultDTO>(scenarioCopy)
      copy.operationId = request.operationId as string
      copy.scenario.identity.scenarioId = copyId
      copy.scenario.configuration.name = request.name as string
      return copy
    })
    h.peer.handlers.set(beforeRun, (request) => ({
      ...fixtureResult<Params>(beforeRun),
      operationId: request.operationId,
    }))
    h.peer.handlers.set(scenarioStart, (request) => {
      const result = fixtureResult<ScenarioRunResultDTO>(scenarioStart)
      result.operationId = request.operationId as string
      result.run.runId = request.runId as string
      result.run.identity.scenarioId = copyId
      result.run.scope.scopeId = copyId
      result.run.status = 'succeeded'
      result.run.lastCommittedRound = 1
      result.run.checkpointRef = snapshot
      result.run.evidence.source = directory
      result.run.evidence.assumptions = ['private-scenario-secret']
      return result
    })
    h.peer.handlers.set('project.scenario.run.read', (request) => {
      const run = (
        h.peer.handlers.get(scenarioStart)!({
          ...request,
          operationId: id(60),
        }) as ScenarioRunResultDTO
      ).run
      run.rounds = [
        {
          number: 1,
          created: [],
          resourceCompleted: [],
          backlog: [],
          metrics: { backlog: 1, completed: 2, openHighAlerts: 3 },
          inputEvents: [],
          behaviorTrace: [],
          beforeInference: snapshot,
          endInference: snapshot,
          checkpointRef: snapshot,
        },
      ]
      return { projectId, run }
    })
    const registry = makeRegistry(h, new Map([['scenario-ref', scenarioId]]))
    const result = outcomeSchema.parse(
      await registry.execute(
        'scenario_run',
        context,
        { scenarioId: 'scenario-ref' },
        new AbortController().signal,
      ),
    )
    expect(transportCalls(h.peer).slice(-5)).toEqual([
      scenarioRead,
      scenarioCopy,
      beforeRun,
      scenarioStart,
      'project.scenario.run.read',
    ])
    expect(h.peer.calls.at(-2)!.params.scenarioId).toBe(copyId)
    expect(result).toMatchObject({
      kind: 'evidence',
      status: 'current',
      resultId: h.peer.calls.at(-2)!.params.runId,
      fields: [
        { fieldId: 'status', value: 'succeeded' },
        { fieldId: 'error', value: null },
        { fieldId: 'last-committed-round', value: 1 },
        { fieldId: 'metrics-round', value: 1 },
        { fieldId: 'backlog', value: 1 },
        { fieldId: 'completed', value: 2 },
        { fieldId: 'open-high-alerts', value: 3 },
      ],
    })
    expect(JSON.stringify(result)).not.toContain(directory)
    expect(JSON.stringify(result)).not.toContain('private-scenario-secret')
  })

  it.each(['CANCELLED', 'STALE_CONTEXT'])(
    'checks %s after a real awaited domain read',
    async (reason) => {
      const h = await setup()
      const controller = new AbortController()
      let current = true
      h.peer.handlers.set(scenarioRead, async () => {
        if (reason === 'CANCELLED') controller.abort()
        else current = false
        return fixtureResult(scenarioRead)
      })
      const registry = makeRegistry(h, new Map([['scenario-ref', projectId]]), () => current)
      await expect(
        registry.execute(
          'scenario_run',
          context,
          { scenarioId: 'scenario-ref' },
          controller.signal,
        ),
      ).rejects.toThrow(reason)
      expect(transportCalls(h.peer)).not.toContain(scenarioCopy)
    },
  )
})
