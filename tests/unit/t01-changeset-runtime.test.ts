import { afterEach, describe, expect, it, vi } from 'vitest'
import { createHash, randomUUID } from 'node:crypto'
import { mkdtempSync, rmSync, mkdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'
import {
  reassembleChangeSetDocument,
  type ChangeSetPreview,
  type ChangeSetPage,
  type ChangeSetConfirmation,
  type JobView,
} from '@ontolearn/contracts'
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'

// Delegate every spawn to the OS; this test owns only its own captured children.
// Wire capture makes no claim about the supervisor's private pending map.
const processState = vi.hoisted(() => ({
  children: [] as Array<{
    child: import('node:child_process').ChildProcess
    command: unknown[]
    stdin: Buffer[]
    stdout: Buffer[]
    stderr: Buffer[]
    closed: Promise<void>
    code?: number | null
    signal?: string | null
  }>,
}))
vi.mock('node:child_process', async (original) => {
  const actual = await original<typeof import('node:child_process')>()
  return {
    ...actual,
    spawn: (...args: Parameters<typeof actual.spawn>) => {
      const child = Reflect.apply(actual.spawn, undefined, args)
      let closed!: () => void
      const capture = {
        child,
        command: [args[0], args[1]],
        stdin: [] as Buffer[],
        stdout: [] as Buffer[],
        stderr: [] as Buffer[],
        closed: new Promise<void>((done) => {
          closed = done
        }),
        code: undefined as number | null | undefined,
        signal: undefined as string | null | undefined,
      }
      child.once('close', (code, signal) => {
        capture.code = code
        capture.signal = signal
        closed()
      })
      if (child.stdin) {
        child.stdin.write = new Proxy(child.stdin.write, {
          apply(target, receiver, input) {
            const value = input[0]
            capture.stdin.push(
              Buffer.isBuffer(value)
                ? Buffer.from(value)
                : Buffer.from(
                    value,
                    typeof input[1] === 'string' ? (input[1] as BufferEncoding) : undefined,
                  ),
            )
            return Reflect.apply(target, receiver, input)
          },
        })
      }
      child.stdout?.on('data', (data: Buffer) => capture.stdout.push(Buffer.from(data)))
      child.stderr?.on('data', (data: Buffer) => capture.stderr.push(Buffer.from(data)))
      processState.children.push(capture)
      return child
    },
  }
})

const engines: EngineSupervisor[] = []
const directories: string[] = []
const location = { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: '' }
const python = resolve('.venv/bin/python')

function pythonJSON<T>(source: string, arguments_: string[]): T {
  const result = spawnSync(python, ['-I', '-c', source, ...arguments_], {
    encoding: 'utf8',
    timeout: 15000,
    maxBuffer: 4 * 1024 * 1024,
  })
  expect({ status: result.status, signal: result.signal, error: result.error }).toEqual({
    status: 0,
    signal: null,
    error: undefined,
  })
  expect(result.stderr).toBe('')
  return JSON.parse(result.stdout) as T
}

function fixture(large = false): {
  database: string
  projectId: string
  before?: unknown
  old?: string
} {
  const directory = mkdtempSync(join(tmpdir(), 't01-changeset-node-'))
  directories.push(directory)
  const database = join(directory, 'project.sqlite')
  return {
    database,
    ...pythonJSON<{ projectId: string; before?: unknown; old?: string }>(
      String.raw`
import json,sys
from uuid import uuid4
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
s=JobStore(sys.argv[1],contract=CONTRACT,target_format=3); p=str(uuid4()); s.create_project(p)
out={'projectId':p}
if sys.argv[2]=='large':
    value='"'+('界😀'*60000)+'"'
    payload={'triples':[{'subject':'urn:Asset','predicate':'urn:label','object':value}], 'references':[], 'singleValuedPredicates':[]}
    # A real typed old baseline larger than a frame, not a claimed T02 producer.
    s.commit(s._project(p),0,str(uuid4()),str(uuid4()),definitions=[{'layer':'ontology','id':'Asset','value':payload}])
    out.update(old=value,before=s.state(s._project(p))['definitions'][0])
s.close(); print(json.dumps(out,ensure_ascii=False))
`,
      [database, large ? 'large' : 'empty'],
    ),
  }
}

function engineFor(
  database: string,
  projectId: string,
  profile: 'business3' | 'legacy2' = 'business3',
) {
  const engine = new EngineSupervisor(location, {
    profile,
    dataPath: database,
    allowedProjects: [projectId],
  })
  engines.push(engine)
  return engine
}

async function preview(
  engine: EngineSupervisor,
  projectId: string,
  baseRevision: number,
  plan: object,
) {
  return (await engine.request('changeset.preview', {
    projectId,
    baseRevision,
    intent: 'change',
    plan,
  })) as ChangeSetPreview
}

async function entireDocument(engine: EngineSupervisor, document: ChangeSetPreview) {
  const pages: ChangeSetPage[] = []
  let cursor: string | null = null
  for (let count = 0; count < 512; count++) {
    const page = (await engine.request('changeset.diff.page', {
      projectId: document.projectId,
      previewHash: document.previewHash,
      documentKind: document.manifest.documentKind,
      pageSize: 200,
      cursor,
    })) as ChangeSetPage
    pages.push(page)
    cursor = page.nextCursor
    if (page.complete) {
      const value = await reassembleChangeSetDocument(document, pages)
      return { value, pages, completionCursor: cursor }
    }
  }
  throw new Error('Expected the actual finite document to complete')
}

async function accepted(engine: EngineSupervisor, document: ChangeSetPreview) {
  expect(document.status).toBe('ready')
  const assembled = await entireDocument(engine, document)
  const confirmation = (await engine.request('changeset.confirm', {
    projectId: document.projectId,
    previewHash: document.previewHash,
    completionCursor: assembled.completionCursor,
  })) as ChangeSetConfirmation
  const request = {
    projectId: document.projectId,
    operationId: randomUUID(),
    capability: 'changeset.commit',
    input: {
      inputSnapshotId: confirmation.inputSnapshotId,
      scope: 'asserted',
      definitionId: 'changeset',
      parametersHash: confirmation.parametersHash,
      derivedResultIds: [],
      preparedPlanRef: confirmation.preparedPlanRef,
    },
    confirmationRef: confirmation.confirmationRef,
  }
  return { ...assembled, request, job: (await engine.request('job.create', request)) as JobView }
}

async function terminal(engine: EngineSupervisor, job: JobView) {
  const deadline = Date.now() + 8000
  while (Date.now() < deadline) {
    const value = (await engine.request('job.get', {
      projectId: job.projectId,
      jobId: job.jobId,
    })) as JobView
    if (['succeeded', 'failed', 'cancelled'].includes(value.state)) return value
    await new Promise((done) => setTimeout(done, 5))
  }
  throw new Error('Actual formal Job did not terminate')
}

async function stop(engine: EngineSupervisor) {
  engine.stop()
  await Promise.race([
    Promise.all(processState.children.map((capture) => capture.closed)),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Own engine close timed out')), 5000),
    ),
  ])
}

afterEach(async () => {
  for (const engine of engines.splice(0)) engine.stop()
  await Promise.race([
    Promise.all(processState.children.map((capture) => capture.closed)),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error('Own children did not close')), 5000),
    ),
  ])
  const destination = '/tmp/t01-changeset-node-traces'
  mkdirSync(destination, { recursive: true })
  const raw = (chunks: Buffer[]) => {
    const bytes = Buffer.concat(chunks)
    return {
      bytes: bytes.length,
      sha256: createHash('sha256').update(bytes).digest('hex'),
      base64: bytes.toString('base64'),
    }
  }
  for (const capture of processState.children.splice(0)) {
    writeFileSync(
      join(destination, `${randomUUID()}.json`),
      JSON.stringify(
        {
          command: capture.command,
          code: capture.code,
          signal: capture.signal,
          stdin: raw(capture.stdin),
          stdout: raw(capture.stdout),
          stderr: raw(capture.stderr),
        },
        null,
        2,
      ) + '\n',
    )
  }
  for (const directory of directories.splice(0)) rmSync(directory, { recursive: true, force: true })
})

describe('formal ChangeSet through the real supervisor and Python coordinator', () => {
  it('assembles the complete actual Diff, commits and undoes, then reconciles the same operation in a new Session', async () => {
    const fixture_ = fixture()
    const engine = engineFor(fixture_.database, fixture_.projectId)
    const definition = {
      layer: 'ontology',
      id: 'Asset',
      value: { triples: [], references: [], singleValuedPredicates: [] },
    }
    const first = await accepted(
      engine,
      await preview(engine, fixture_.projectId, 0, { definitions: [definition] }),
    )
    expect(first.value).toEqual([
      {
        resource: ['definition', 'ontology', 'Asset'],
        before: null,
        after: {
          layer: 'ontology',
          id: 'Asset',
          payload: '{"references":[],"singleValuedPredicates":[],"triples":[]}',
        },
      },
    ])
    const complete = await terminal(engine, first.job)
    expect(complete.state).toBe('succeeded')
    expect(complete.capability).toBe('changeset.commit')
    const undo = (await engine.request('changeset.preview', {
      projectId: fixture_.projectId,
      baseRevision: 1,
      intent: 'undo',
      targetOperationId: first.request.operationId,
    })) as ChangeSetPreview
    const reversed = await accepted(engine, undo)
    expect(reversed.value).toEqual([
      {
        resource: ['definition', 'ontology', 'Asset'],
        before: {
          layer: 'ontology',
          id: 'Asset',
          payload: '{"references":[],"singleValuedPredicates":[],"triples":[]}',
        },
        after: null,
      },
    ])
    expect((await terminal(engine, reversed.job)).state).toBe('succeeded')
    await stop(engine)
    const successor = engineFor(fixture_.database, fixture_.projectId)
    expect(await successor.request('job.create', first.request)).toMatchObject({
      jobId: first.job.jobId,
      state: 'succeeded',
    })
    expect(
      await successor.request('operation.get', {
        projectId: fixture_.projectId,
        operationId: reversed.request.operationId,
      }),
    ).toMatchObject({ jobId: reversed.job.jobId, projectRevision: 2 })
    const replacement = successor.request('job.create', {
      ...first.request,
      operationId: randomUUID(),
    })
    try {
      await replacement
      throw new Error('Old Session confirmation unexpectedly created a new operation')
    } catch (cause) {
      expect(successor.projectFailure(cause, replacement).code).toBe('IDENTITY_CONFLICT')
    }
    await stop(successor)
    const persisted = pythonJSON<{ facts: unknown[]; definitions: unknown[]; claims: number }>(
      String.raw`
import json,sys
from ontolearn_engine.job_store import JobStore
from ontolearn_engine.resources import CONTRACT
s=JobStore(sys.argv[1],contract=CONTRACT,target_format=3)
state=s.state(s._project(sys.argv[2]));state['claims']=s._db.execute('SELECT count(*) FROM operation_claims').fetchone()[0]
s.close();print(json.dumps(state))
`,
      [fixture_.database, fixture_.projectId],
    )
    expect(persisted.facts).toEqual([])
    expect(persisted.definitions).toEqual([])
    expect(persisted.claims).toBe(2)
  }, 20000)

  it('returns a multi-frame old typed value in full and rejects reordered pages in the actual consumer helper', async () => {
    const fixture_ = fixture(true)
    const engine = engineFor(fixture_.database, fixture_.projectId)
    const value = {
      triples: [{ subject: 'urn:Asset', predicate: 'urn:label', object: '"new"' }],
      references: [],
      singleValuedPredicates: [],
    }
    const document = await preview(engine, fixture_.projectId, 1, {
      definitions: [{ layer: 'ontology', id: 'Asset', value }],
    })
    expect(document.manifest.totalBytes).toBeGreaterThan(262144)
    const assembled = await entireDocument(engine, document)
    expect(assembled.pages.length).toBeGreaterThan(1)
    expect(assembled.value).toEqual([
      {
        resource: ['definition', 'ontology', 'Asset'],
        before: fixture_.before,
        after: {
          layer: 'ontology',
          id: 'Asset',
          payload: JSON.stringify({
            references: [],
            singleValuedPredicates: [],
            triples: [{ object: '"new"', predicate: 'urn:label', subject: 'urn:Asset' }],
          }),
        },
      },
    ])
    await expect(
      reassembleChangeSetDocument(document, [...assembled.pages].reverse()),
    ).rejects.toThrow('INVALID_CHANGESET_DOCUMENT')
    await expect(reassembleChangeSetDocument(document, assembled.pages.slice(1))).rejects.toThrow(
      'INVALID_CHANGESET_DOCUMENT',
    )
    expect(await engine.request('project.get', { projectId: fixture_.projectId })).toMatchObject({
      projectRevision: 1,
    })
  }, 20000)
})
