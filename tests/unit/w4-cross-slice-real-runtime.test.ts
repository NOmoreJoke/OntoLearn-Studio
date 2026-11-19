import { execFileSync } from 'node:child_process'
import { createHash, randomUUID } from 'node:crypto'
import { copyFile, mkdir, mkdtemp, readFile, realpath, rm, writeFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { expect, it, vi } from 'vitest'
import type {
  AgentModule,
  BehaviorRunArgs,
  BridgeResult,
  MappingDraft,
  ScenarioConfiguration,
  ScenarioRunDTO,
} from '@ontolearn/contracts'
import { AgentModeStore } from '../../apps/desktop/src/main/agent/agent-mode-store'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import { FORMAL_WRITE_TOOLS } from '../../apps/desktop/src/main/agent/domain-ports'
import { AgentHostComposition } from '../../apps/desktop/src/main/agent/host-composition'
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import {
  commitWorkspaceChange,
  prepareWorkspaceChange,
} from '../../apps/desktop/src/renderer/src/ontology/workspace-change'

const uid = randomUUID
const python = resolve('.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python')
const unchanged = () => {}
const sha256 = (bytes: Buffer) => createHash('sha256').update(bytes).digest('hex')
function take<T>(reply: BridgeResult<T>): T {
  if (!reply.ok) throw new Error(JSON.stringify(reply.error))
  return reply.data
}

const draft: MappingDraft = {
  identity: 'equipment-csv',
  version: 1,
  namespace: 'urn:ontolearn:learning:equipment/',
  classIri: 'urn:ontolearn:learning:Equipment',
  keys: ['equipment_id'],
  fields: [
    {
      column: 'equipment_name',
      predicate: 'urn:ontolearn:learning:name',
      kind: 'string',
      trim: true,
      empty: 'omit',
      referenceNamespace: '',
      referenceColumns: [],
    },
  ],
}

const scenario: ScenarioConfiguration = {
  name: 'Isolation and capacity',
  maxRounds: 2,
  capacity: { mode: 'direct', direct: 1 },
  initialEdits: [],
  events: [
    {
      id: 'alarm-1',
      round: 1,
      sequence: 0,
      payload: { alarmId: 'A', level: 'High', status: 'Open' },
    },
    { id: 'alarm-2', round: 1, sequence: 1, payload: {} },
  ],
  parameters: {},
  source: 'Integration fixture',
  assumptions: ['Fixed capacity'],
  ruleVersion: 'rules-v1',
  behaviorVersion: 'behavior-v1',
}

it('crosses the real business3 process for mapping, isolated runs, transfer and Agent tools', async () => {
  await mkdir(resolve('build'), { recursive: true })
  const root = await realpath(await mkdtemp(resolve('build/w4-runtime-')))
  const csv = join(root, 'equipment.csv')
  const xlsx = join(root, 'equipment.xlsx')
  const archive = join(root, 'result.ontolearn.zip')
  const html = join(root, 'result.html')
  const occupiedHtml = join(root, 'occupied.html')
  let chosenHtml = occupiedHtml
  const library = join(root, 'library')
  await mkdir(library, { mode: 0o700 })
  const engine = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: resolve('.') },
    { profile: 'business3', dataPath: join(library, 'store.sqlite') },
  )
  const tasks = new TaskService(engine)
  let nextSource = xlsx
  const projects = new ProjectMainlineService(engine, tasks, () => tasks.attachView(() => {}), {
    pickMappingSource: async () => ({ filePath: nextSource }),
    pickTransferFile: async (purpose) => ({
      filePath: purpose === 'report-html' ? chosenHtml : archive,
    }),
    managementJournalPath: join(root, 'management.json'),
    restoreJournalPath: join(root, 'restore.json'),
  })
  const replies = engine.mainlineReplyReceiver()
  const receive = async <T>(work: () => Promise<BridgeResult<T>>) => {
    const { value, receipt } = await replies.receive(work)
    replies.consume(receipt)
    return value
  }
  const call = async <T>(work: () => Promise<BridgeResult<T>>) => take(await receive(work))
  const read = () => call(() => projects.readProject({ editor: 'ontology' }))
  const changeBridge = {
    previewProjectChangeset: (args: Parameters<typeof projects.previewProjectChangeset>[0]) =>
      receive(() => projects.previewProjectChangeset(args)),
    getProjectDiffPage: (args: Parameters<typeof projects.getProjectDiffPage>[0]) =>
      receive(() => projects.getProjectDiffPage(args)),
    confirmProjectChangeset: (args: Parameters<typeof projects.confirmProjectChangeset>[0]) =>
      receive(() => projects.confirmProjectChangeset(args)),
    commitProjectChangeSet: (args: Parameters<typeof projects.commitProjectChangeSet>[0]) =>
      receive(() => projects.commitProjectChangeSet(args)),
    getJob: (jobId: string) => tasks.getJob(jobId),
  }
  let agent: AgentHostComposition | undefined
  try {
    await copyFile(resolve('tests/fixtures/product-baselines/equipment.csv'), csv)
    execFileSync(python, [
      '-c',
      'import sys; from openpyxl import Workbook; w=Workbook(); w.active.title="First"; w.active.append(["id"]); w.active.append(["1"]); s=w.create_sheet("Second"); s.append(["id"]); s.append(["2"]); w.save(sys.argv[1])',
      xlsx,
    ])
    const { projectId } = await call(() =>
      projects.createBlankProject({
        requestVersion: 1,
        operationId: uid(),
        name: 'W4 integration',
        initialization: { kind: 'blank' },
      }),
    )
    await call(() => projects.openProject({ projectId }))
    const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    const ontology = await prepareWorkspaceChange(
      changeBridge,
      await read(),
      {
        definitions: [
          {
            layer: 'ontology',
            id: 'catalog',
            value: {
              triples: [
                {
                  subject: draft.classIri,
                  predicate: rdfType,
                  object: '<http://www.w3.org/2002/07/owl#Class>',
                },
                {
                  subject: draft.fields[0]!.predicate,
                  predicate: rdfType,
                  object: '<http://www.w3.org/2002/07/owl#DatatypeProperty>',
                },
                {
                  subject: 'urn:ontolearn:learning:equipment_name',
                  predicate: rdfType,
                  object: '<http://www.w3.org/2002/07/owl#DatatypeProperty>',
                },
              ],
            },
          },
        ],
      },
      unchanged,
    )
    expect((await commitWorkspaceChange(changeBridge, ontology, uid(), unchanged)).state).toBe(
      'succeeded',
    )
    const first = await call(() => projects.selectMappingSource({}))
    expect(first.sheets).toEqual(['First', 'Second'])
    const second = await call(() =>
      projects.selectMappingSource({ selectionId: first.selectionId, sheet: 'Second' }),
    )
    expect(second).toMatchObject({ sheet: 'Second', encoding: null, totalRows: 1 })
    nextSource = csv
    const source = await call(() => projects.selectMappingSource({}))
    const chosen = await call(() =>
      projects.selectMappingSource({ selectionId: source.selectionId, encoding: 'utf-8' }),
    )
    expect(chosen.suggestions).toEqual([
      {
        column: 'equipment_name',
        predicate: 'urn:ontolearn:learning:equipment_name',
        basis: 'exact-field-name',
        samples: ['泵站A', '泵站B'],
      },
    ])
    const selected = join(library, '.ontolearn-host-selections', source.selectionId)
    expect(JSON.parse(await readFile(join(selected, 'meta.json'), 'utf8'))).toMatchObject({
      projectId,
      sha256: source.fingerprint,
      purpose: 'mapping-source',
    })
    expect(await readFile(join(selected, 'payload.csv'))).toEqual(await readFile(csv))
    const before = await read()
    const currentDraft = await call(() => projects.readMappingDraft({ mappingId: draft.identity }))
    const save = {
      operationId: uid(),
      draft,
      baseRevision: before.domain.projectRevision,
      expectedGeneration: currentDraft.generation,
    }
    const saved = await call(() => projects.saveMappingDraft(save))
    expect(
      await call(() => projects.readMappingDraft({ mappingId: draft.identity })),
    ).toMatchObject({
      draft,
      generation: saved.generation,
    })
    expect(
      await receive(() => projects.saveMappingDraft({ ...save, operationId: uid() })),
    ).toMatchObject({
      ok: false,
    })
    const input = {
      selectionId: chosen.selectionId,
      sheet: chosen.sheet,
      encoding: chosen.encoding,
      draft,
    }
    const preview = await call(() =>
      projects.previewMapping({ ...input, page: { offset: 0, limit: 1 } }),
    )
    expect(preview.rows).toHaveLength(1)
    expect(preview).toMatchObject({
      totalRows: 2,
      issues: [],
      conflicts: [],
      identitiesAdded: [draft.namespace + '001', draft.namespace + '002'],
    })
    const preparation = {
      resultId: preview.resultId,
      selectionId: preview.selectionId,
      sourceFingerprint: preview.sourceFingerprint,
      baseRevision: preview.baseRevision,
      operationId: uid(),
    }
    const stagedPayload = join(selected, 'payload.csv')
    await writeFile(stagedPayload, Buffer.concat([await readFile(csv), Buffer.from('003,drift\n')]))
    expect(await receive(() => projects.prepareMappingCommit(preparation))).toMatchObject({
      ok: false,
      error: { code: 'IDENTITY_CONFLICT' },
    })
    await copyFile(csv, stagedPayload)
    const prepared = await call(() => projects.prepareMappingCommit(preparation))
    const proposal = await prepareWorkspaceChange(changeBridge, before, prepared.plan, unchanged)
    expect(proposal.rows.length).toBeGreaterThan(0)
    const mappingOperation = uid()
    expect(
      (await commitWorkspaceChange(changeBridge, proposal, mappingOperation, unchanged)).state,
    ).toBe('succeeded')
    const firstMapping = await read()
    expect(firstMapping.domain.state.facts).toHaveLength(4)
    expect(
      firstMapping.domain.state.facts.every(
        (fact) => fact.owner === draft.identity && fact.source_row !== null,
      ),
    ).toBe(true)
    expect(
      await receive(() => projects.prepareMappingCommit({ ...preparation, operationId: uid() })),
    ).toMatchObject({ ok: false, error: { code: 'REVISION_CONFLICT' } })
    const retry = await call(() => projects.previewMapping(input))
    expect(retry).toMatchObject({ added: [], removed: [], modified: [], conflicts: [] })
    const checkMapping = () =>
      call(() =>
        projects.checkLearningTask({
          projectId,
          taskId: 'mapping',
          operationId: uid(),
        }),
      )
    expect(await checkMapping()).toMatchObject({ operationComplete: false })
    const repeatedMapping = await call(() =>
      projects.prepareMappingCommit({
        ...preparation,
        operationId: uid(),
        resultId: retry.resultId,
        baseRevision: retry.baseRevision,
      }),
    )
    const noChange = await prepareWorkspaceChange(
      changeBridge,
      firstMapping,
      repeatedMapping.plan,
      unchanged,
    )
    const repeatedOperation = uid()
    expect(
      (await commitWorkspaceChange(changeBridge, noChange, repeatedOperation, unchanged)).state,
    ).toBe('succeeded')
    const mapped = await read()
    expect(mapped.domain.state.facts).toEqual(firstMapping.domain.state.facts)
    const learning = await call(() =>
      projects.checkLearningTask({
        projectId,
        taskId: 'mapping',
        operationId: uid(),
      }),
    )
    expect(learning).toMatchObject({
      checkStatus: 'passed',
      guidedStageCheckpointRef: null,
      evidenceIds: [mapped.inputSnapshotId, repeatedOperation],
    })
    const undo = await call(() =>
      projects.previewProjectChangeset({
        baseRevision: mapped.domain.projectRevision,
        intent: 'undo',
        targetOperationId: mappingOperation,
      }),
    )
    expect(undo).toMatchObject({ status: 'ready', targetOperationId: mappingOperation })
    expect((await read()).domain.state.facts).toEqual(mapped.domain.state.facts)

    const base = {
      projectVersion: mapped.domain.projectRevision,
      inputSnapshotId: mapped.inputSnapshotId,
    }
    const sample: Omit<BehaviorRunArgs, 'projectId'> = {
      operationId: uid(),
      runId: uid(),
      scope: 'sample',
      binding: {
        projectId,
        baseRevision: base.projectVersion,
        inputSnapshotId: base.inputSnapshotId,
        behaviorVersion: '1',
        scopeId: uid(),
        requestId: uid(),
      },
      draft: {
        id: 'notify-alarm',
        name: 'Notify',
        description: 'Sample',
        effect: 'Notification',
        trigger: { eventType: 'alarm' },
        enabled: true,
        priority: 0,
        version: 1,
        conditions: [{ op: 'always' }],
        actions: [
          {
            kind: 'notify',
            message: { kind: 'value', value: { kind: 'string', value: 'Isolated notification' } },
          },
        ],
      },
      events: [{ id: 'alarm-1', type: 'alarm', sequence: 0, version: 1, payload: {}, edits: [] }],
    }
    const identity = {
      operationId: sample.operationId,
      runId: sample.runId,
      binding: sample.binding,
      scope: sample.scope,
    }
    const candidate = await call(() => projects.runBehaviorSample(sample))
    expect(candidate, JSON.stringify(candidate.error)).toMatchObject({
      state: 'candidate',
      committed: false,
      freshness: 'current',
    })
    expect(await call(() => projects.readBehaviorRun(identity))).toMatchObject({
      state: 'candidate',
      freshness: 'current',
    })
    const beforeBehavior = await call(() =>
      projects.recordRunBeforeCommit({
        projectId,
        operationId: sample.operationId,
        domain: 'behavior',
        baseRevision: base.projectVersion,
        label: null,
      }),
    )
    expect(beforeBehavior).toMatchObject({
      reason: 'before-run',
      domainRevision: base.projectVersion,
    })
    const checkpoints = await call(() =>
      projects.listProjectCheckpoints({ cursor: null, pageSize: 30 }),
    )
    expect(checkpoints.items).toContainEqual(
      expect.objectContaining({
        checkpointRef: beforeBehavior.checkpointRef,
        operationId: sample.operationId,
        reason: 'before-run',
      }),
    )
    const created = await call(() =>
      projects.createScenario({ ...base, configuration: scenario, operationId: uid() }),
    )
    const scenarioId = created.scenario.identity.scenarioId
    const copy = await call(() =>
      projects.copyScenario({ ...base, scenarioId, name: 'Comparison copy', operationId: uid() }),
    )
    const copyId = copy.scenario.identity.scenarioId
    expect(
      (await call(() => projects.listScenarios({ cursor: null, limit: 10 }))).items,
    ).toHaveLength(2)
    const runs: Array<{ scenarioId: string; runId: string }> = []
    for (const id of [scenarioId, copyId]) {
      const args = { ...base, scenarioId: id, operationId: uid(), runId: uid() }
      const result = await call(() => projects.startScenarioRun(args))
      expect(result.run).toMatchObject({ status: 'succeeded', lastCommittedRound: 2 })
      const receipt = await call(() =>
        projects.recordRunBeforeCommit({
          projectId,
          operationId: args.operationId,
          domain: 'scenario',
          baseRevision: base.projectVersion,
          label: null,
        }),
      )
      expect(result.beforeRunCheckpointRef).toBe(receipt.checkpointRef)
      expect(await call(() => projects.readScenario({ scenarioId: id }))).toMatchObject({
        runs: [{ runId: args.runId, status: 'succeeded' }],
      })
      const page = await call(() =>
        projects.readScenarioRun({ scenarioId: id, runId: args.runId, roundOffset: 1, limit: 1 }),
      )
      expect(page.run.rounds).toMatchObject([
        { number: 2, metrics: { backlog: 0, openHighAlerts: 1 } },
      ])
      runs.push({ scenarioId: id, runId: args.runId })
    }
    const comparison = await call(() =>
      projects.compareScenarioRuns({ runs, roundOffset: 0, limit: 2 }),
    )
    expect(comparison.runs.map((run) => run.metrics)).toEqual([
      comparison.runs[0]?.metrics,
      comparison.runs[0]?.metrics,
    ])
    expect(
      await receive(() =>
        projects.resumeScenarioRun({
          ...base,
          scenarioId,
          sourceRunId: runs[0]!.runId,
          checkpointRef: '0'.repeat(64),
          operationId: uid(),
          runId: uid(),
        }),
      ),
    ).toMatchObject({ ok: false })
    expect(
      await call(() =>
        projects.readSelectedMappingSource(source.selectionId, new AbortController().signal),
      ),
    ).toMatchObject({ selectionId: source.selectionId })

    type Dependencies = ConstructorParameters<typeof AgentHostComposition>[0]
    const provider = vi.fn<NonNullable<ReturnType<Dependencies['models']>>['invokeAgentBody']>()
    agent = new AgentHostComposition({
      modes: new AgentModeStore(),
      selection: () => projects.source.current(),
      blocked: () => projects.managementBlocked || projects.restoreBlocked,
      projects,
      tasks,
      replies,
      waveFourEnabled: true,
      providerApproval: {
        configurationId: uid(),
        configurationVersion: uid(),
        confirmBody: async () => true,
        signature: {
          endpoint: DEEPSEEK_ENDPOINT,
          requestedModel: REQUEST_MODEL,
          returnedModel: REQUEST_MODEL,
          codecVersion: CODEC_VERSION,
          fingerprint: null,
          mode: 'disabled',
          effort: 'low',
        },
      },
      models: () => ({
        status: () => ({
          availability: 'ready',
          contextId: 'fixture',
          projectId,
          privacy: 'project',
          configurations: [],
          selections: [],
          invocations: [],
        }),
        agentReady: () => true,
        invokeAgentBody: provider,
        listConfigurationSummaries: () => [],
        setConfigurationEnabled: vi.fn(),
        removeConfiguration: vi.fn(),
        probeCapabilities: vi.fn(),
        listAuditEntries: vi.fn(),
      }),
    })
    const host = agent
    expect(FORMAL_WRITE_TOOLS).toHaveLength(0)
    const tools: Array<{
      module: AgentModule
      tool: string
      selected: Record<string, string>
      outcome: string
    }> = [
      {
        module: 'mapping',
        tool: 'mapping_propose',
        selected: { sourceId: source.selectionId },
        outcome: 'draft',
      },
      {
        module: 'behavior',
        tool: 'behavior_test',
        selected: { behaviorId: sample.draft.id, sampleId: sample.binding.scopeId },
        outcome: 'evidence',
      },
      { module: 'scenario', tool: 'scenario_run', selected: { scenarioId }, outcome: 'evidence' },
    ]
    for (const { module, tool, selected: ids, outcome } of tools) {
      provider.mockReset()
      const callId = uid()
      const complete = (message: object, reason: string) =>
        JSON.stringify({
          id: uid(),
          object: 'chat.completion',
          created: 0,
          model: REQUEST_MODEL,
          choices: [
            { index: 0, finish_reason: reason, message: { role: 'assistant', ...message } },
          ],
        })
      provider.mockImplementationOnce(async ({ body }) => {
        const { messages } = JSON.parse(body)
        const prompt = JSON.parse(
          messages.find((item: { role: string }) => item.role === 'user').content,
        )
        const args = Object.fromEntries(
          Object.keys(ids).map((key, index) => [key, prompt.selectedObjectRefs[index]]),
        )
        if (module === 'mapping') args.instruction = 'Inspect selected source'
        return complete(
          {
            content: null,
            tool_calls: [
              {
                id: callId,
                type: 'function',
                function: { name: tool, arguments: JSON.stringify(args) },
              },
            ],
          },
          'tool_calls',
        )
      })
      provider.mockResolvedValueOnce(
        complete({ content: JSON.stringify({ kind: 'evidence', callIds: [callId] }) }, 'stop'),
      )
      take(
        await host.dispatchAgentQuestion({
          operationId: uid(),
          question: '检查选中对象',
          module,
          mode: 'tutor',
          scope: 'asserted',
          selectedObjectIds: Object.values(ids),
        }),
      )
      await vi.waitFor(async () => {
        expect(await host.getAgentState()).toMatchObject({ data: { status: 'answered' } })
      })
      const state = take(await host.getAgentState())
      expect(state.receipts, JSON.stringify(state.receipts)).toMatchObject([
        { tool, outcome: { kind: outcome } },
      ])
      const exposed = JSON.stringify([
        state.receipts,
        provider.mock.calls.map(([args]) => args.body),
      ])
      expect(exposed).not.toContain(root)
      expect(exposed).not.toContain('.ontolearn-host-selections')
      expect(exposed.length).toBeLessThan(20000)
    }
    expect((await read()).domain.state.facts).toEqual(mapped.domain.state.facts)

    const report = await call(() =>
      projects.prepareProjectHtmlReport({ baseRevision: base.projectVersion }),
    )
    expect(report.credentialScan.status).toBe('clear')
    expect(report.report.behaviorResults.some((entry) => entry.resultId === sample.runId)).toBe(
      true,
    )
    expect(report.report.scenarioComparisons.length).toBeGreaterThanOrEqual(2)
    expect(report.report.learning).toContainEqual(
      expect.objectContaining({
        taskId: 'mapping',
        operationCompleted: true,
        independentTransferSuccess: false,
      }),
    )
    const output = await call(() => projects.selectTransferFile({ purpose: 'package-export' }))
    const exportCheck = await call(() =>
      projects.checkProjectPackageExport({
        selectionId: output.selectionId,
        kind: 'full',
        baseRevision: base.projectVersion,
        options: { agentSessions: false, rawSources: false, derived: false, history: false },
      }),
    )
    const published = await call(() =>
      projects.exportProjectPackage({
        selectionId: output.selectionId,
        checkRef: exportCheck.checkRef,
        operationId: uid(),
      }),
    )
    const zipBytes = await readFile(archive)
    expect(published.publication).toMatchObject({
      state: 'published',
      durability: 'confirmed',
      sha256: sha256(zipBytes),
    })
    const importedSelection = await call(() =>
      projects.selectTransferFile({ purpose: 'package-import' }),
    )
    const importArgs = { selectionId: importedSelection.selectionId, expectedKind: 'full' as const }
    const compatible = await call(() => projects.checkProjectPackageImport(importArgs))
    if (compatible.status !== 'compatible') throw new Error(JSON.stringify(compatible))
    const imported = await call(() =>
      projects.importProjectPackage({
        ...importArgs,
        operationId: uid(),
        checkRef: compatible.checkRef,
        packageSha256: compatible.packageSha256,
      }),
    )
    expect(imported.importedProjectId).not.toBe(projectId)
    await writeFile(occupiedHtml, 'Keep original', 'utf8')
    const occupied = await call(() => projects.selectTransferFile({ purpose: 'report-html' }))
    const rejectedHtml = await call(() =>
      projects.exportProjectHtmlReport({
        selectionId: occupied.selectionId,
        operationId: uid(),
        baseRevision: base.projectVersion,
        reportRef: report.reportRef,
      }),
    )
    expect(rejectedHtml.publication).toMatchObject({ state: 'failed', code: 'target-exists' })
    expect(await readFile(occupiedHtml, 'utf8')).toBe('Keep original')
    expect(
      await call(() =>
        projects.checkLearningTask({
          projectId,
          taskId: 'report',
          operationId: uid(),
        }),
      ),
    ).toMatchObject({ operationComplete: false })
    chosenHtml = html
    const htmlOutput = await call(() => projects.selectTransferFile({ purpose: 'report-html' }))
    const htmlResult = await call(() =>
      projects.exportProjectHtmlReport({
        selectionId: htmlOutput.selectionId,
        operationId: uid(),
        baseRevision: base.projectVersion,
        reportRef: report.reportRef,
      }),
    )
    const bytes = await readFile(html)
    expect(htmlResult.publication).toMatchObject({
      state: 'published',
      durability: 'confirmed',
      sha256: sha256(bytes),
    })
    expect(bytes.toString()).toContain('Content-Security-Policy')
    expect(bytes.toString()).not.toMatch(/<script|\.ontolearn-host-selections/iu)
    expect(bytes.toString()).not.toContain(root)
    expect(
      await call(() =>
        projects.checkLearningTask({
          projectId,
          taskId: 'report',
          operationId: uid(),
        }),
      ),
    ).toMatchObject({ checkStatus: 'passed', evidenceIds: [report.reportRef] })

    await call(() => projects.deleteScenarioRun({ ...runs[1]!, operationId: uid() }))
    await call(() =>
      projects.restoreScenarioBaseline({
        ...base,
        scenarioId,
        operationId: uid(),
        configurationDigest: created.scenario.identity.configurationDigest,
      }),
    )
    expect((await call(() => projects.readScenario({ scenarioId }))).runs).toEqual([])
    expect((await read()).domain.state.facts).toEqual(mapped.domain.state.facts)
    if (undo.status !== 'ready') throw new Error(JSON.stringify(undo))
    let cursor: string | null = null
    for (let index = 0; index < undo.manifest.segmentCount; index++) {
      const page = await call(() =>
        projects.getProjectDiffPage({
          previewHash: undo.previewHash,
          documentKind: 'diff',
          pageSize: 1,
          cursor,
        }),
      )
      cursor = page.nextCursor
      if (page.complete) break
    }
    if (cursor === null) throw new Error('Undo diff did not return its completion cursor')
    const undoJob = await commitWorkspaceChange(
      changeBridge,
      {
        preview: undo,
        rows: [],
        completionCursor: cursor,
      },
      uid(),
      unchanged,
    )
    expect(undoJob.state).toBe('succeeded')
    expect((await read()).domain.state.facts).toEqual(before.domain.state.facts)
    expect(await call(() => projects.readBehaviorRun(identity))).toMatchObject({
      state: 'candidate',
      freshness: 'stale',
      staleReason: 'project-revision-changed',
    })
    expect(await call(() => projects.cancelBehaviorRun(identity))).toMatchObject({
      state: 'cancelled',
    })
    await call(() => projects.openProject({ projectId: imported.importedProjectId }))
    expect((await read()).domain.state.facts).toEqual(mapped.domain.state.facts)
  } finally {
    agent?.close()
    try {
      await projects.dispose()
      await tasks.dispose()
      await engine.stopAndWait()
    } finally {
      await rm(root, { recursive: true, force: true })
    }
  }
}, 30000)

it('cancels a durable scenario claim and resumes the exact committed checkpoint through Main', async () => {
  await mkdir(resolve('build'), { recursive: true })
  const root = await realpath(await mkdtemp(resolve('build/w4-resume-')))
  const engine = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: resolve('.') },
    { profile: 'business3', dataPath: join(root, 'w4a2.sqlite') },
  )
  const tasks = new TaskService(engine)
  const projects = new ProjectMainlineService(engine, tasks, () => tasks.attachView(() => {}))
  const receiver = engine.mainlineReplyReceiver()
  async function receive<T>(work: () => Promise<BridgeResult<T>>) {
    const { value, receipt } = await receiver.receive(work)
    receiver.consume(receipt)
    return value
  }
  const call = async <T>(work: () => Promise<BridgeResult<T>>) => take(await receive(work))
  try {
    // The wire runner is synchronous. Use the Stage 1 crash fixture in a closed
    // owned library to represent a process interrupted after an actual round.
    const setup = execFileSync(
      python,
      [
        '-c',
        [
          'import json, sys',
          'from pathlib import Path',
          'from test_w4_a2_harness import runtime, prepared_project, create_scenario, ok',
          'from test_w4_a2_scenario import run_scenario, _make_interrupted_run',
          'with runtime(Path(sys.argv[1])) as (actor, store):',
          '    project, revision, snapshot = prepared_project(actor, store)',
          '    created = ok(create_scenario(actor, project, revision, snapshot))',
          '    scenario = created["scenario"]["identity"]["scenarioId"]',
          '    _, response = run_scenario(actor, project, revision, snapshot, scenario)',
          '    whole = ok(response)["run"]',
          '    saved, _ = _make_interrupted_run(store, project, whole["runId"], keep_rounds=1)',
          '    print(json.dumps({"id": saved, "run": whole}))',
        ].join('\n'),
        root,
      ],
      {
        env: { ...process.env, PYTHONPATH: resolve('packages/engine/tests') },
        encoding: 'utf8',
      },
    )
    const { id: runId, run: whole } = JSON.parse(setup) as { id: string; run: ScenarioRunDTO }
    const { projectId, scenarioId, projectVersion, inputSnapshotId } = whole.identity
    await call(() => projects.openProject({ projectId }))
    const initial = await call(() => projects.readProject({ editor: 'ontology' }))
    const cancelled = await call(() =>
      projects.cancelScenarioRun({ scenarioId, runId, operationId: uid() }),
    )
    expect(cancelled.run).toMatchObject({
      status: 'cancelled',
      lastCommittedRound: 1,
      resumeAvailable: true,
    })
    const checkpointRef = cancelled.run.rounds[0]!.checkpointRef
    expect(checkpointRef).toBe(whole.rounds[0]!.checkpointRef)
    expect(
      await receive(() =>
        projects.resumeScenarioRun({
          scenarioId,
          projectVersion,
          inputSnapshotId,
          sourceRunId: runId,
          checkpointRef: '0'.repeat(64),
          operationId: uid(),
          runId: uid(),
        }),
      ),
    ).toMatchObject({ ok: false, error: { code: 'IDENTITY_CONFLICT' } })
    const operationId = uid()
    const resumed = await call(() =>
      projects.resumeScenarioRun({
        scenarioId,
        projectVersion,
        inputSnapshotId,
        sourceRunId: runId,
        checkpointRef,
        operationId,
        runId: uid(),
      }),
    )
    expect(resumed).toMatchObject({
      sourceRunId: runId,
      resumedFrom: checkpointRef,
      run: { status: 'succeeded', rounds: whole.rounds.slice(1), pendingEvents: [] },
    })
    const checkpoints = await call(() =>
      projects.listProjectCheckpoints({ cursor: null, pageSize: 30 }),
    )
    expect(checkpoints.items).toContainEqual(
      expect.objectContaining({
        checkpointRef: resumed.beforeRunCheckpointRef,
        operationId,
        reason: 'before-run',
      }),
    )
    const final = await call(() => projects.readProject({ editor: 'ontology' }))
    expect(final.domain.state.facts).toEqual(initial.domain.state.facts)
    expect(final.domain.projectRevision).toBe(projectVersion)
  } finally {
    try {
      projects.dispose()
      tasks.dispose()
      await engine.stopAndWait()
    } finally {
      await rm(root, { recursive: true, force: true })
    }
  }
}, 30000)
