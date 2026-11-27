/** Real Supervisor -> same-candidate entrypoint -> provider -> named creation.
 * No command/spawn/Store/authority doubles. Definitions only until parent runs
 * the adopted candidate with its own installed venv and fixed controlled stage.
 */
import { ChildProcess } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import type { BridgeResult, MainlineExampleCreateRequestDTO } from '@ontolearn/contracts'
import {
  EngineError,
  EngineSupervisor,
  getEngineCommand,
  getEngineEnvironment,
  type SupervisorOptions,
} from '../../apps/desktop/src/main/engine'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const location = {
  packaged: false,
  appPath: join(repoRoot, 'apps', 'desktop'),
  resourcesPath: repoRoot,
}
const entrypoint = join(repoRoot, 'packages', 'engine', 'entrypoint.py')
const adoptedRoot = join(
  repoRoot,
  'build',
  'release-resources',
  'fr003-bundle-v2',
  'examples',
  'equipment-maintenance',
  'loader',
)
const manifestHash = 'a2200250856474ebbae669151891d5495e7fcd042e8f8f0a77ccbb0553b521ee'
const inputDigest = '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e'
const entrypointHash = 'fa06c28ee67f919767e03fdf7e230d7a90703a1db73670208991915647ca7f32'
const unavailable = {
  ok: false,
  error: {
    code: 'NOT_FOUND',
    messageKey: 'resource.notFound',
    params: { resource: 'snapshot' },
    retryable: false,
  },
}
function data<T>(value: BridgeResult<T>): T {
  if (!value.ok) throw new Error(`Actual example host RPC rejected: ${JSON.stringify(value.error)}`)
  return value.data
}
function namedRequest(): MainlineExampleCreateRequestDTO {
  return {
    exampleCreateRequestVersion: 1,
    operationId: randomUUID(),
    name: '受控设备运维示例',
    exampleId: 'equipment-maintenance',
    inputDigest,
  }
}
function activeChildren(): ChildProcess[] {
  return (process as typeof process & { _getActiveHandles(): unknown[] })
    ._getActiveHandles()
    .filter((value): value is ChildProcess => value instanceof ChildProcess)
}
function ownedSupervisor(
  database: string,
  options: Pick<SupervisorOptions, 'profile' | 'exampleRoot'>,
) {
  const expected = getEngineCommand(location, options)
  const baseline = new Set(activeChildren())
  const supervisor = new EngineSupervisor(location, { ...options, dataPath: database })
  return { supervisor, expected, baseline, children: new Set<ChildProcess>() }
}
type Owned = ReturnType<typeof ownedSupervisor>
function capture(value: Owned): void {
  for (const child of activeChildren()) {
    if (
      !value.baseline.has(child) &&
      child.spawnfile === value.expected.command &&
      value.expected.args.every((arg, index) => child.spawnargs[index + 1] === arg)
    ) {
      value.children.add(child)
    }
  }
  expect(value.children.size).toBe(1)
}
function runtime(database: string, exampleRoot?: string) {
  const core = ownedSupervisor(database, { profile: 'business3', exampleRoot })
  const tasks = new TaskService(core.supervisor)
  const projects = new ProjectMainlineService(core.supervisor, tasks, () => {
    tasks.attachView(() => {})
  })
  return { ...core, tasks, projects, replies: core.supervisor.mainlineReplyReceiver() }
}
type Runtime = ReturnType<typeof runtime>
async function receive<T>(
  value: Runtime,
  work: () => Promise<BridgeResult<T>>,
): Promise<BridgeResult<T>> {
  const delivered = await value.replies.receive(work)
  capture(value)
  value.replies.consume(delivered.receipt)
  expect(value.replies.diagnostic().slots).toBe(0)
  return delivered.value
}
async function closeOwned(value: Owned): Promise<void> {
  capture(value)
  // Retain our exact handles and install listeners before stop can change them.
  const waits = [...value.children].map(async (child) => {
    if (
      (child.exitCode !== null || child.signalCode !== null) &&
      child.stdout?.destroyed &&
      child.stderr?.destroyed
    )
      return
    let timer: ReturnType<typeof setTimeout> | undefined
    let killTimer: ReturnType<typeof setTimeout> | undefined
    try {
      await new Promise<void>((done, reject) => {
        const closed = () => {
          child.removeListener('error', failed)
          done()
        }
        const failed = (cause: Error) => {
          child.removeListener('close', closed)
          reject(cause)
        }
        child.once('close', closed)
        child.once('error', failed)
        killTimer = setTimeout(() => {
          if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL')
        }, 1500)
        timer = setTimeout(() => {
          child.removeListener('close', closed)
          child.removeListener('error', failed)
          reject(new Error('Exact owned example host did not close/reap'))
        }, 3500)
      })
    } finally {
      clearTimeout(timer)
      clearTimeout(killTimer)
    }
    expect(child.exitCode !== null || child.signalCode !== null).toBe(true)
  })
  value.supervisor.stop()
  await Promise.all(waits)
}
async function closeRuntime(value: Runtime): Promise<void> {
  try {
    value.projects.dispose()
    value.tasks.dispose()
  } finally {
    await closeOwned(value)
  }
}
async function fixedResources(): Promise<{ manifest: Buffer; input: Buffer }> {
  const manifest = await readFile(join(adoptedRoot, 't01-provider.json'))
  const input = await readFile(join(adoptedRoot, 'load-input.json'))
  expect(manifest.byteLength).toBe(198)
  expect(input.byteLength).toBe(10930)
  expect(createHash('sha256').update(manifest).digest('hex')).toBe(manifestHash)
  expect(createHash('sha256').update(input).digest('hex')).toBe(inputDigest)
  return { manifest, input }
}
async function copyLoader(root: string): Promise<void> {
  const { manifest, input } = await fixedResources()
  await mkdir(root, { recursive: true })
  await writeFile(join(root, 't01-provider.json'), manifest, { flag: 'w' })
  await writeFile(join(root, 'load-input.json'), input, { flag: 'w' })
}
function actualArguments(value: Runtime, root?: string): void {
  const [child] = value.children
  expect(child.spawnargs.slice(1, 3)).toEqual(root ? ['-I', entrypoint] : ['-I', '-m'])
  expect(child.spawnargs.filter((arg) => arg.startsWith('--t11-internal-example-root'))).toEqual(
    root ? [`--t11-internal-example-root=${root}`] : [],
  )
  expect(child.spawnargs).toContain('--t01-internal-profile=business3')
  expect(child.pid).toBeGreaterThan(0)
}

describe('trusted example host configuration', () => {
  it('routes explicitly and rejects a root outside business3 before spawn', () => {
    const original = getEngineCommand(location)
    expect(original.args).toEqual(['-I', '-m', 'ontolearn_engine'])
    expect(getEngineCommand(location, { profile: 'business3', exampleRoot: adoptedRoot })).toEqual({
      command: original.command,
      args: ['-I', entrypoint],
    })
    const packaged = {
      ...location,
      packaged: true,
      resourcesPath: join(repoRoot, 'package-resources'),
    }
    expect(getEngineCommand(packaged, { profile: 'business3', exampleRoot: adoptedRoot })).toEqual({
      command: join(
        packaged.resourcesPath,
        'engine',
        process.platform === 'win32' ? 'ontolearn-engine.exe' : 'ontolearn-engine',
      ),
      args: [],
    })
    for (const exampleRoot of ['', 'relative/loader', adoptedRoot + '\0']) {
      expect(() => new EngineSupervisor(location, { profile: 'business3', exampleRoot })).toThrow(
        EngineError,
      )
    }
    expect(
      () => new EngineSupervisor(location, { profile: 'legacy2', exampleRoot: adoptedRoot }),
    ).toThrow(EngineError)
    expect(() => new EngineSupervisor(location, { exampleRoot: adoptedRoot })).toThrow(EngineError)
    expect(
      getEngineEnvironment({ T11_INTERNAL_EXAMPLE_ROOT: adoptedRoot, PYTHONPATH: repoRoot }),
    ).toEqual({ ONTOLEARN_ALLOWED_PROJECTS: '[]' })
  })
})

it('real host consumes the fixed provider and persists the named example', async () => {
  await fixedResources()
  expect(
    createHash('sha256')
      .update(await readFile(entrypoint))
      .digest('hex'),
  ).toBe(entrypointHash)
  const directory = await mkdtemp(join(tmpdir(), 't01-example-host-positive-'))
  const database = join(directory, 'owned.sqlite')
  const first = runtime(database, adoptedRoot)
  let second: Runtime | undefined
  let firstClosed = false
  let completed = false
  try {
    const catalog = data(
      await receive(first, () => first.projects.getProjectCatalog({ pageSize: 64, cursor: null })),
    )
    expect(catalog.items).toEqual([])
    actualArguments(first, adoptedRoot)
    const request = namedRequest()
    const created = data(await receive(first, () => first.projects.createExampleProject(request)))
    expect(created.operationId).toBe(request.operationId)
    expect(created.receipt.exampleId).toBe('equipment-maintenance')
    expect(created.receipt.inputDigest).toBe(inputDigest)
    expect(created.receipt.domainRevision).toBe(1)
    expect(created.receipt.operationSequence).toBe(1)
    expect(data(await receive(first, () => first.projects.createExampleProject(request)))).toEqual(
      created,
    )
    data(await receive(first, () => first.projects.openProject({ projectId: created.projectId })))
    const material = data(
      await receive(first, () => first.projects.readProject({ editor: 'query' })),
    )
    expect(material.domain.projectRevision).toBe(1)
    expect(material.domain.state.facts).toHaveLength(18)
    expect(material.domain.state.definitions).toHaveLength(11)
    expect(material.domain.state.mappingState).toEqual({})
    expect(material.workspace.metadata.templateRef).toBe(`equipment-maintenance@${inputDigest}`)
    expect(material.domain.state.facts).toContainEqual(
      expect.objectContaining({
        subject: 'urn:ontolearn:learning:equipment/001',
        predicate: 'urn:ontolearn:learning:name',
        object: '"泵站A"',
        owner: null,
        source_row: null,
        managed_value: null,
      }),
    )
    expect(material.domain.state.definitions).toContainEqual(
      expect.objectContaining({ layer: 'query', id: 'unclosed-high' }),
    )
    await closeRuntime(first)
    firstClosed = true
    // Reopen reads the accepted immutable domain; it does not replay a create
    // under a new hostClientId/engineSessionId origin.
    const reopened = runtime(database, adoptedRoot)
    second = reopened
    data(
      await receive(reopened, () =>
        reopened.projects.openProject({ projectId: created.projectId }),
      ),
    )
    const read = data(
      await receive(reopened, () => reopened.projects.readProject({ editor: 'query' })),
    )
    expect(read.domain).toEqual(material.domain)
    actualArguments(reopened, adoptedRoot)
    await fixedResources() // No product writes to the fixed stage.
    completed = true
  } finally {
    if (!firstClosed) await closeRuntime(first)
    if (second) await closeRuntime(second)
    if (completed) await rm(directory, { recursive: true, force: true })
  }
}, 30000)

it.each(['missing-root', 'changed-input'] as const)(
  'real %s refuses partial creation and preserves blank/explicit retry',
  async (fault) => {
    const directory = await mkdtemp(join(tmpdir(), 't01-example-host-negative-'))
    const root = join(directory, 'owned-loader')
    if (fault === 'changed-input') {
      await copyLoader(root)
      await writeFile(join(root, 'load-input.json'), '{}\n')
    }
    const value = runtime(join(directory, 'owned.sqlite'), root)
    let completed = false
    try {
      const request = namedRequest()
      const failed = await receive(value, () => value.projects.createExampleProject(request))
      expect(failed).toEqual(unavailable)
      expect(JSON.stringify(failed)).not.toContain(directory)
      const before = data(
        await receive(value, () =>
          value.projects.getProjectCatalog({ pageSize: 64, cursor: null }),
        ),
      )
      expect(before.items).toEqual([])
      actualArguments(value, root)
      const blank = data(
        await receive(value, () =>
          value.projects.createBlankProject({
            requestVersion: 1,
            operationId: randomUUID(),
            name: '仍可创建空白',
            initialization: { kind: 'blank' },
          }),
        ),
      )
      expect(blank.receipt.domainRevision).toBe(0)
      // A known pre-commit NOT_FOUND can be explicitly retried with the same ID.
      await copyLoader(root)
      const accepted = data(
        await receive(value, () => value.projects.createExampleProject(request)),
      )
      expect(accepted.receipt.inputDigest).toBe(inputDigest)
      expect(accepted.receipt.domainRevision).toBe(1)
      // A committed retry consumes its immutable context, not mutable files.
      await rm(join(root, 'load-input.json'))
      const repeated = data(
        await receive(value, () => value.projects.createExampleProject(request)),
      )
      expect(repeated).toEqual(accepted)
      const catalog = data(
        await receive(value, () =>
          value.projects.getProjectCatalog({ pageSize: 64, cursor: null }),
        ),
      )
      expect(catalog.total).toBe(2)
      expect(new Set(catalog.items.map((item) => item.projectId))).toEqual(
        new Set([blank.projectId, accepted.projectId]),
      )
      completed = true
    } finally {
      await closeRuntime(value)
      if (completed) await rm(directory, { recursive: true, force: true })
    }
  },
  30000,
)

it('real business3 with no example root preserves module startup and blank creation', async () => {
  const directory = await mkdtemp(join(tmpdir(), 't01-example-host-blank-'))
  const value = runtime(join(directory, 'owned.sqlite'))
  let completed = false
  try {
    const created = data(
      await receive(value, () =>
        value.projects.createBlankProject({
          requestVersion: 1,
          operationId: randomUUID(),
          name: '原空白路径',
          initialization: { kind: 'blank' },
        }),
      ),
    )
    actualArguments(value)
    data(await receive(value, () => value.projects.openProject({ projectId: created.projectId })))
    const read = data(await receive(value, () => value.projects.readProject({ editor: 'query' })))
    expect(read.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })
    expect(read.workspace.metadata.templateRef).toBeNull()
    completed = true
  } finally {
    await closeRuntime(value)
    if (completed) await rm(directory, { recursive: true, force: true })
  }
}, 20000)

it('real legacy2 health keeps module startup without the example flag', async () => {
  const directory = await mkdtemp(join(tmpdir(), 't01-example-host-legacy-'))
  const value = ownedSupervisor(join(directory, 'owned.sqlite'), { profile: 'legacy2' })
  let completed = false
  try {
    const health = await value.supervisor.health()
    capture(value)
    expect(health.protocolVersion).toBe(2)
    expect(health.status).toBe('ok')
    const [child] = value.children
    expect(child.spawnargs.slice(1)).toEqual(['-I', '-m', 'ontolearn_engine'])
    completed = true
  } finally {
    await closeOwned(value)
    if (completed) await rm(directory, { recursive: true, force: true })
  }
}, 15000)
