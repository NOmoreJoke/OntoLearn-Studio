/** Real local stdio/Store/finite worker. No spawn, authority or Job doubles.
 * SOURCE definition only until the parent runs this exact candidate. This is
 * main-process service evidence, not Electron/preload/renderer/packaging proof.
 */
import { it, expect, vi } from 'vitest'
import { ChildProcess } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  reassembleChangeSetDocument,
  type BridgeResult,
  type ChangeSetPage,
  type JobView,
  type MainlineChangePlanDTO,
  type MainlineCreateRequestDTO,
  type QueryCellDTO,
  type QueryRowsPageDTO,
  type TaskUpdate,
} from '@ontolearn/contracts'
import {
  EngineSupervisor,
  getEngineCommand,
  getEngineEnvironment,
} from '../../apps/desktop/src/main/engine'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const location = {
  packaged: false,
  appPath: join(repoRoot, 'apps/desktop'),
  resourcesPath: repoRoot,
}
const queryText =
  'SELECT ?subject ?value WHERE { ?subject <urn:runtime:value> ?value } ORDER BY ?subject'

function data<T>(value: BridgeResult<T>): T {
  if (!value.ok) throw new Error(`Actual business RPC rejected: ${JSON.stringify(value.error)}`)
  return value.data
}

/** Observe our actual Node-owned handle, without replacing spawn or discovering
 * OS processes by name. This narrow test-only observation supplies close/reap
 * evidence missing from the public synchronous Supervisor.stop() interface.
 */
function ownedChildren(directory: string): ChildProcess[] {
  const handles = (
    process as typeof process & { _getActiveHandles(): unknown[] }
  )._getActiveHandles()
  const executable = getEngineCommand(location).command
  const backup = `--t01-internal-backup=${join(directory, '.t01-backup-')}`
  return handles.filter(
    (value): value is ChildProcess =>
      value instanceof ChildProcess &&
      value.spawnfile === executable &&
      value.spawnargs.includes('--t01-internal-profile=business3') &&
      value.spawnargs.some((argument) => argument.startsWith(backup)),
  )
}

type Runtime = {
  supervisor: EngineSupervisor
  tasks: TaskService
  projects: ProjectMainlineService
  replies: ReturnType<EngineSupervisor['mainlineReplyReceiver']>
  children: Set<ChildProcess>
  events: TaskUpdate[]
}

function runtime(database: string): Runtime {
  const supervisor = new EngineSupervisor(location, { profile: 'business3', dataPath: database })
  const tasks = new TaskService(supervisor)
  const events: TaskUpdate[] = []
  const projects = new ProjectMainlineService(supervisor, tasks, () => {
    tasks.attachView((update) => events.push(update))
  })
  return {
    supervisor,
    tasks,
    projects,
    replies: supervisor.mainlineReplyReceiver(),
    children: new Set(),
    events,
  }
}

async function closeRuntime(value: Runtime, directory: string): Promise<void> {
  for (const child of ownedChildren(directory)) value.children.add(child)
  value.projects.dispose()
  value.tasks.dispose()
  // Install close listeners before stop can emit a synchronous transition.
  const waits = [...value.children].map(async (child) => {
    if (child.exitCode !== null || child.signalCode !== null) {
      if (child.stdout?.destroyed && child.stderr?.destroyed) return
    }
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
        // Only the retained exact handle may be signalled. No PID guessing.
        killTimer = setTimeout(() => {
          if (child.exitCode === null && child.signalCode === null) child.kill('SIGKILL')
        }, 1500)
        timer = setTimeout(() => {
          child.removeListener('close', closed)
          child.removeListener('error', failed)
          reject(new Error('Owned real engine did not close/reap'))
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

it('real business3 creates, saves, commits, queries and reopens its own persistent project', async () => {
  const directory = await mkdtemp(join(tmpdir(), 't01-mainline-real-'))
  const database = join(directory, 'owned.sqlite')
  const deadline = Date.now() + 25000
  const instances: Runtime[] = []
  const live = new Set<Runtime>()
  const step = async <T>(operation: Promise<T>): Promise<T> => {
    let timer: ReturnType<typeof setTimeout> | undefined
    try {
      return await Promise.race([
        operation,
        new Promise<never>((_, reject) => {
          timer = setTimeout(
            () => reject(new Error('Real mainline flow deadline')),
            Math.max(1, deadline - Date.now()),
          )
        }),
      ])
    } finally {
      clearTimeout(timer)
    }
  }
  const receive = async <T>(
    value: Runtime,
    work: () => Promise<BridgeResult<T>>,
  ): Promise<BridgeResult<T>> => {
    const delivered = await value.replies.receive(work)
    // This trusted Node receiver observed the original service Promise/value.
    // Close delivery responsibility only; service cache holdings remain owned.
    expect(typeof delivered.value.ok).toBe('boolean')
    value.replies.consume(delivered.receipt)
    return delivered.value
  }
  const start = () => {
    const value = runtime(database)
    instances.push(value)
    live.add(value)
    return value
  }
  const terminal = async (value: Runtime, accepted: JobView): Promise<JobView> => {
    while (Date.now() < deadline) {
      const current = data(await step(value.tasks.getJob(accepted.jobId)))
      expect(current.operationId).toBe(accepted.operationId)
      expect(current.projectId).toBe(accepted.projectId)
      if (['succeeded', 'failed', 'cancelled'].includes(current.state)) {
        expect(current.state, JSON.stringify(current.error)).toBe('succeeded')
        return current
      }
      await step(new Promise<void>((done) => setTimeout(done, 20)))
    }
    throw new Error('Actual finite worker Job did not reach terminal')
  }
  try {
    // No caller-supplied allowedProjects, testMode, command, grant or issuer.
    const environment = getEngineEnvironment(process.env, { dataPath: database })
    expect(environment.ONTOLEARN_ALLOWED_PROJECTS).toBe('[]')
    expect(environment.ONTOLEARN_TEST_MODE).toBeUndefined()
    expect(
      Object.keys(environment).some((key) => /TOKEN|SECRET|KEY|PROXY|PYTHONPATH/i.test(key)),
    ).toBe(false)
    const first = start()
    const catalog = data(
      await step(
        receive(first, () => first.projects.getProjectCatalog({ pageSize: 64, cursor: null })),
      ),
    )
    expect(catalog.total).toBe(0)
    expect(catalog.items).toEqual([])
    expect(first.projects.source.current()).toBeNull()
    for (const child of ownedChildren(directory)) first.children.add(child)
    expect(first.children.size).toBe(1)

    const create: MainlineCreateRequestDTO = {
      requestVersion: 1,
      operationId: randomUUID(),
      name: '真实主链路',
      initialization: { kind: 'blank' },
    }
    const created = data(
      await step(receive(first, () => first.projects.createBlankProject(create))),
    )
    expect(
      data(await step(receive(first, () => first.projects.createBlankProject(create)))),
    ).toEqual(created)
    expect(created.receipt.operationSequence).toBe(1)
    const projectId = created.projectId
    expect(
      data(await step(receive(first, () => first.projects.openProject({ projectId })))).projectId,
    ).toBe(projectId)
    const initial = data(
      await step(receive(first, () => first.projects.readProject({ editor: 'query' }))),
    )
    expect(initial.domain.state).toEqual({ definitions: [], facts: [], mappingState: {} })
    for (let i = 0; i < 24; i++) {
      const next = data(
        await step(receive(first, () => first.projects.readProject({ editor: 'query' }))),
      )
      expect(next.domain).toEqual(initial.domain)
    }

    const contentJson = JSON.stringify({ kind: 'query-draft', text: '尚未提交的草稿' })
    const saveArgs = {
      operationId: randomUUID(),
      editor: 'query',
      expectedGeneration: 0,
      boundDomainRevision: 0,
      contentJson,
    }
    const saved = data(await step(receive(first, () => first.projects.saveProjectDraft(saveArgs))))
    expect(saved.generation).toBe(1)
    expect(saved.contentHash).toBe(createHash('sha256').update(contentJson).digest('hex'))
    const stale = await step(
      receive(first, () =>
        first.projects.saveProjectDraft({ ...saveArgs, operationId: randomUUID() }),
      ),
    )
    expect(stale.ok).toBe(false)
    if (!stale.ok) expect(stale.error.code).toBe('INVALID_STATE')
    const afterRefusal = data(
      await step(receive(first, () => first.projects.readProject({ editor: 'query' }))),
    )
    expect(afterRefusal.workspace.draft).toMatchObject({
      state: 'present',
      generation: 1,
      contentJson,
    })

    const makeFact = (subject: string, object: string) => {
      const predicate = 'urn:runtime:value'
      return {
        id: createHash('sha256')
          .update(JSON.stringify([subject, predicate, object]))
          .digest('hex'),
        subject,
        predicate,
        object,
      }
    }
    const definition = {
      text: queryText,
      references: [{ layer: 'ontology', id: 'O1' }],
      descriptor: {
        version: 1 as const,
        name: '真实查询',
        description: '有限 SELECT',
        scope: 'asserted' as const,
        capabilityQuestion: 'Which values?',
        source: 'editor' as const,
      },
    }
    const plan: MainlineChangePlanDTO = {
      definitions: [
        {
          layer: 'ontology',
          id: 'O1',
          value: {
            triples: [
              {
                subject: 'urn:runtime:Thing',
                predicate: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                object: '<http://www.w3.org/2002/07/owl#Class>',
              },
            ],
          },
        },
        { layer: 'query', id: 'Q1', value: definition },
      ],
      manual: [
        makeFact('urn:runtime:a', '"甲"@zh'),
        makeFact('urn:runtime:b', '"7"^^<http://www.w3.org/2001/XMLSchema#integer>'),
      ],
    }
    const preview = data(
      await step(
        receive(first, () =>
          first.projects.previewProjectChangeset({ baseRevision: 0, intent: 'change', plan }),
        ),
      ),
    )
    if (preview.status !== 'ready') throw new Error('Actual ChangeSet unexpectedly conflicts')
    const pages: ChangeSetPage[] = []
    let cursor: string | null = null
    for (let index = 0; index < 8; index++) {
      const page: ChangeSetPage = data(
        await step(
          receive(first, () =>
            first.projects.getProjectDiffPage({
              previewHash: preview.previewHash,
              documentKind: 'diff',
              pageSize: 1,
              cursor,
            }),
          ),
        ),
      )
      pages.push(page)
      cursor = page.nextCursor
      if (page.complete) break
    }
    expect(pages.at(-1)?.complete).toBe(true)
    const document = await step(reassembleChangeSetDocument(preview, pages))
    expect(document).toHaveLength(4) // Ontology + managed query + two real manual facts.
    const confirmation = data(
      await step(
        receive(first, () =>
          first.projects.confirmProjectChangeset({
            previewHash: preview.previewHash,
            completionCursor: cursor!,
          }),
        ),
      ),
    )
    const committed = data(
      await step(
        receive(first, () =>
          first.projects.commitProjectChangeSet({ operationId: randomUUID(), confirmation }),
        ),
      ),
    )
    const commitTerminal = await terminal(first, committed)
    expect(commitTerminal.capability).toBe('changeset.commit')
    expect(data(await step(first.tasks.getOperation(committed.operationId)))).toMatchObject({
      jobId: committed.jobId,
    })
    const material = data(
      await step(receive(first, () => first.projects.readProject({ editor: 'query' }))),
    )
    expect(material.domain.projectRevision).toBe(1)
    expect(material.domain.state.definitions).toHaveLength(2)
    expect(material.domain.state.facts).toHaveLength(2)

    const loaded = data(
      await step(
        receive(first, () =>
          first.projects.queries.loadQueryDefinition({
            definitionId: 'Q1',
            selection: { kind: 'current' },
          }),
        ),
      ),
    )
    if (loaded.kind !== 'managed') throw new Error('New managed definition was returned as legacy')
    expect(loaded.draft.sparql).toBe(queryText)
    const executed = data(
      await step(
        receive(first, () =>
          first.projects.queries.executeSavedQuery({
            operationId: randomUUID(),
            loadRef: loaded.loadRef,
            visibleDraft: loaded.draft,
            selection: { kind: 'current' },
          }),
        ),
      ),
    )
    expect(executed.acceptedJob.capability).toBe('query.execute')
    expect(
      (executed.acceptedJob.implementation as { executionSemanticsVersion: string })
        .executionSemanticsVersion,
    ).toBe('i05-finite-6')
    const queryTerminal = await terminal(first, executed.acceptedJob)
    expect(queryTerminal.resultRef).not.toBeNull()
    const descriptor = data(
      await step(
        receive(first, () =>
          first.projects.queries.getQueryResultDescriptor({
            resultId: queryTerminal.resultRef!.resultId,
          }),
        ),
      ),
    )
    expect(descriptor.executedText.sha256).toBe(
      createHash('sha256').update(queryText).digest('hex'),
    )
    expect(descriptor.executedText.utf8Bytes).toBe(Buffer.byteLength(queryText, 'utf8'))
    expect(descriptor.query).toEqual({
      kind: 'SELECT',
      columns: [
        { index: 0, name: 'subject' },
        { index: 1, name: 'value' },
      ],
      rowCount: 2,
    })
    const cells: QueryCellDTO[][] = []
    cursor = null
    for (let index = 0; index < 3; index++) {
      const page: QueryRowsPageDTO = data(
        await step(
          receive(first, () =>
            first.projects.queries.getQueryRowsPage({
              descriptorRef: descriptor.descriptorRef,
              pageSize: 1,
              cursor,
            }),
          ),
        ),
      )
      cells.push(...page.rows.map((row) => row.cells))
      cursor = page.nextCursor
      if (cursor === null) break
    }
    expect(cursor).toBeNull()
    expect(cells).toEqual([
      [
        { kind: 'iri', iri: 'urn:runtime:a', n3: '<urn:runtime:a>' },
        {
          kind: 'literal',
          lexical: '甲',
          n3: '"甲"@zh',
          literalType: { kind: 'language', tag: 'zh' },
        },
      ],
      [
        { kind: 'iri', iri: 'urn:runtime:b', n3: '<urn:runtime:b>' },
        {
          kind: 'literal',
          lexical: '7',
          n3: '"7"^^<http://www.w3.org/2001/XMLSchema#integer>',
          literalType: { kind: 'datatype', iri: 'http://www.w3.org/2001/XMLSchema#integer' },
        },
      ],
    ])

    await step(closeRuntime(first, directory))
    live.delete(first)
    const reopened = start()
    const listed = data(
      await step(
        receive(reopened, () =>
          reopened.projects.getProjectCatalog({ pageSize: 64, cursor: null }),
        ),
      ),
    )
    expect(listed.items.map((item) => item.projectId)).toEqual([projectId])
    expect(reopened.projects.source.current()).toBeNull() // No first-row auto-selection.
    for (const child of ownedChildren(directory)) reopened.children.add(child)
    expect(reopened.children.size).toBe(1)
    data(await step(receive(reopened, () => reopened.projects.openProject({ projectId }))))
    const restored = data(
      await step(receive(reopened, () => reopened.projects.readProject({ editor: 'query' }))),
    )
    expect(restored.domain).toEqual(material.domain)
    expect(restored.workspace.draft).toEqual(material.workspace.draft)
    expect(restored.workspace.draft).toMatchObject({ state: 'present', contentJson, generation: 1 })
  } finally {
    await Promise.all([...live].map((value) => closeRuntime(value, directory)))
    expect(
      instances.every((value) =>
        [...value.children].every((child) => child.exitCode !== null || child.signalCode !== null),
      ),
    ).toBe(true)
    // A cleanup failure preserves its own directory instead of deleting a DB
    // still held by an unreaped child. The failure remains visible to the runner.
    await rm(directory, { recursive: true, force: true })
  }
}, 30000)

it('seventeen acknowledged real commits preserve old operation identity without replay', async () => {
  const directory = await mkdtemp(join(tmpdir(), 't01-intent-lifetime-real-'))
  const value = runtime(join(directory, 'owned.sqlite'))
  const issued = vi.spyOn(value.supervisor, 'requestPinned') // Observe real dispatch; no replacement.
  const deadline = Date.now() + 25000
  const receive = async <T>(
    work: () => Promise<BridgeResult<T>>,
    context = 'real business RPC',
  ): Promise<T> => {
    const offered = await value.replies.receive(work)
    expect(offered.value.ok, context).toBe(true)
    const result = data(offered.value)
    value.replies.consume(offered.receipt)
    return result
  }
  let original: Parameters<ProjectMainlineService['commitProjectChangeSet']>[0] | undefined
  let originalJob: JobView | undefined
  try {
    await receive(() => value.projects.getProjectCatalog({ pageSize: 64, cursor: null }))
    const created = await receive(() =>
      value.projects.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: 'ACK 生命周期回归',
        initialization: { kind: 'blank' },
      }),
    )
    await receive(() => value.projects.openProject({ projectId: created.projectId }))
    for (let index = 0; index < 17; index++) {
      expect(Date.now()).toBeLessThan(deadline)
      const current = await receive(() => value.projects.readProject({ editor: 'ontology' }))
      const subject = `urn:intent-lifetime:${index}`
      const predicate = 'urn:intent-lifetime:value'
      const object = `"value-${index}"`
      const preview = await receive(() =>
        value.projects.previewProjectChangeset({
          baseRevision: current.domain.projectRevision,
          intent: 'change',
          plan: {
            manual: [
              {
                id: createHash('sha256')
                  .update(JSON.stringify([subject, predicate, object]))
                  .digest('hex'),
                subject,
                predicate,
                object,
              },
            ],
          },
        }),
      )
      if (preview.status !== 'ready') throw new Error('Actual capacity preview conflicts')
      let cursor: string | null = null
      let complete = false
      for (let page = 0; page < 8; page++) {
        const part: ChangeSetPage = await receive(() =>
          value.projects.getProjectDiffPage({
            previewHash: preview.previewHash,
            documentKind: 'diff',
            pageSize: 32,
            cursor,
          }),
        )
        cursor = part.nextCursor
        if (part.complete) {
          complete = true
          break
        }
      }
      expect(complete).toBe(true)
      const confirmation = await receive(() =>
        value.projects.confirmProjectChangeset({
          previewHash: preview.previewHash,
          completionCursor: cursor!,
        }),
      )
      const request = { operationId: randomUUID(), confirmation }
      let accepted: JobView
      if (index === 0) {
        const first = await value.replies.receive(() =>
          value.projects.commitProjectChangeSet(request),
        )
        accepted = data(first.value)
        const duplicate = await value.replies.receive(() =>
          value.projects.commitProjectChangeSet(request),
        )
        expect(data(duplicate.value).jobId).toBe(accepted.jobId)
        const holdings = value.replies.diagnostic().holdingCount
        value.replies.consume(first.receipt)
        expect(value.replies.diagnostic().holdingCount).toBe(holdings) // Another exact ACK remains.
        const budget = value.supervisor.queryReadBudget(value.projects.source.current()!.owner)
        const failure = vi.spyOn(budget, 'releaseHolding').mockImplementationOnce(() => {
          throw new Error('injected exact payload cleanup failure')
        })
        try {
          expect(() => value.replies.consume(duplicate.receipt)).toThrow(
            'injected exact payload cleanup failure',
          )
          expect(value.replies.diagnostic().holdingCount).toBe(holdings)
          expect(value.replies.diagnostic().offered).toBe(1)
        } finally {
          failure.mockRestore()
        }
        value.replies.consume(duplicate.receipt)
        expect(value.replies.diagnostic().holdingCount).toBe(holdings - 1)
      } else {
        accepted = await receive(
          () => value.projects.commitProjectChangeSet(request),
          `real acknowledged commit ${index + 1}`,
        )
      }
      if (!original) {
        original = request
        originalJob = accepted
      }
      let terminal: JobView = accepted
      while (!['succeeded', 'failed', 'cancelled'].includes(terminal.state)) {
        if (Date.now() >= deadline) throw new Error('Actual intent lifetime deadline')
        await new Promise<void>((done) => setTimeout(done, 10))
        terminal = data(await value.tasks.getJob(accepted.jobId))
      }
      expect(terminal.state, JSON.stringify(terminal.error)).toBe('succeeded')
      expect(value.replies.diagnostic().slots).toBe(0)
    }
    const restored = await receive(() => value.projects.commitProjectChangeSet(original!))
    expect(restored.jobId).toBe(originalJob!.jobId)
    expect(restored.operationId).toBe(original!.operationId)
    expect(issued.mock.calls.filter(([method]) => method === 'job.create')).toHaveLength(17)
    expect(issued.mock.calls.at(-1)?.[0]).toBe('job.get')
    const mismatched = await value.projects.commitProjectChangeSet({
      ...original!,
      confirmation: { ...original!.confirmation, confirmationRef: randomUUID() },
    })
    expect(mismatched.ok).toBe(false)
    expect(issued.mock.calls.filter(([method]) => method === 'job.create')).toHaveLength(17)
    const final = await receive(() => value.projects.readProject({ editor: 'ontology' }))
    expect(final.domain.projectRevision).toBe(17)
    expect(final.domain.state.facts).toHaveLength(17)
  } finally {
    issued.mockRestore()
    await closeRuntime(value, directory)
    await rm(directory, { recursive: true, force: true })
  }
}, 30000)
