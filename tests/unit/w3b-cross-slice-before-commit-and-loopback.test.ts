import { createCipheriv, createDecipheriv, createHash, randomBytes, randomUUID } from 'node:crypto'
import { mkdtemp, rm, mkdir, realpath } from 'node:fs/promises'
import { createServer, type ServerResponse } from 'node:http'
import { join, resolve } from 'node:path'
import { afterEach, expect, it } from 'vitest'
import type {
  AgentDispatchArgs,
  BridgeResult,
  MainlineChangePlanDTO,
  QualityConstraintDefinitionDTO,
} from '@ontolearn/contracts'
import { AgentModeStore } from '../../apps/desktop/src/main/agent/agent-mode-store'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
  encodeChatRequest,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import { FORMAL_WRITE_TOOLS } from '../../apps/desktop/src/main/agent/domain-ports'
import { AgentHostComposition } from '../../apps/desktop/src/main/agent/host-composition'
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { PrivateCiphertextRepository } from '../../apps/desktop/src/main/model-gateway/ciphertext-repository'
import { ConfigurationRepository } from '../../apps/desktop/src/main/model-gateway/configuration-repository'
import { EncryptedCredentialBoundary } from '../../apps/desktop/src/main/model-gateway/credentials'
import { ModelGatewayCore } from '../../apps/desktop/src/main/model-gateway/gateway'
import {
  ModelGatewayService,
  type AgentProviderApproval,
} from '../../apps/desktop/src/main/model-gateway/model-service'
import { PersistentGatewayAudit } from '../../apps/desktop/src/main/model-gateway/persistent-audit'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { prepareLearningTaskFixture } from '../../apps/desktop/src/renderer/src/learning/task-fixture'
import { newManualFactPlan } from '../../apps/desktop/src/renderer/src/ontology/mainline-facts'
import {
  commitWorkspaceChange,
  prepareWorkspaceChange,
} from '../../apps/desktop/src/renderer/src/ontology/workspace-change'

const cleanup: Array<() => unknown> = []
afterEach(async () => {
  const errors: unknown[] = []
  for (const close of cleanup.splice(0).reverse()) {
    try {
      await close()
    } catch (error) {
      errors.push(error)
    }
  }
  if (errors.length) throw new AggregateError(errors, 'Loopback fixture cleanup failed')
})

function unwrap<T>(reply: BridgeResult<T>): T {
  if (!reply.ok) throw new Error(JSON.stringify(reply.error))
  return reply.data
}

function completion(message: object, finishReason: 'stop' | 'tool_calls') {
  return JSON.stringify({
    id: randomUUID(),
    object: 'chat.completion',
    created: 0,
    model: REQUEST_MODEL,
    choices: [
      { index: 0, finish_reason: finishReason, message: { role: 'assistant', ...message } },
    ],
  })
}

function toolCall(name: string, args: object) {
  return { id: randomUUID(), type: 'function', function: { name, arguments: JSON.stringify(args) } }
}

const learning = 'urn:ontolearn:learning:'
const proposedClass = learning + 'AgentIntroducedClass'
const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const owlClass = '<http://www.w3.org/2002/07/owl#Class>'
const constraintId = 'name-required'
function equipmentConstraint(): QualityConstraintDefinitionDTO {
  return {
    layer: 'constraint',
    id: constraintId,
    value: {
      schemaVersion: 1,
      kind: 'constraint',
      id: constraintId,
      revision: 1,
      label: '设备名称必填',
      enabled: true,
      targetClass: learning + 'Equipment',
      path: learning + 'name',
      template: 'required',
      parameters: {},
    },
  }
}
const ontologyTool = () =>
  toolCall('ontology_propose', { instruction: JSON.stringify({ classIri: proposedClass }) })

async function fixture() {
  await mkdir(resolve('build'), { recursive: true })
  const directory = await realpath(await mkdtemp(resolve('build/w3b-loopback-')))
  cleanup.push(() => rm(directory, { recursive: true, force: true }))
  const data = join(directory, 'library')
  const userDataPath = join(directory, 'profile')
  await Promise.all([mkdir(data, { mode: 0o700 }), mkdir(userDataPath, { mode: 0o700 })])
  const engine = new EngineSupervisor(
    { packaged: false, appPath: resolve('apps/desktop'), resourcesPath: resolve('.') },
    { profile: 'business3', dataPath: join(data, 'owned.sqlite') },
  )
  cleanup.push(() => engine.stopAndWait())
  const owners: { host?: AgentHostComposition; models?: ModelGatewayService } = {}
  const tasks = new TaskService(engine, (projectId) => {
    owners.host?.refresh(true)
    owners.models?.selectProject(projectId)
  })
  cleanup.push(() => tasks.dispose())
  const projects = new ProjectMainlineService(engine, tasks, () => tasks.attachView(() => {}), {
    managementJournalPath: join(userDataPath, 'management.json'),
    restoreJournalPath: join(userDataPath, 'restore.json'),
  })
  cleanup.push(() => projects.dispose())
  const replies = engine.mainlineReplyReceiver()
  async function receive<T>(work: () => Promise<BridgeResult<T>>) {
    const { value, receipt } = await replies.receive(work)
    replies.consume(receipt)
    return value
  }
  const bridge = {
    readProject: (args: { editor: string }) => receive(() => projects.readProject(args)),
    previewProjectChangeset: (args: Parameters<typeof projects.previewProjectChangeset>[0]) =>
      receive(() => projects.previewProjectChangeset(args)),
    getProjectDiffPage: (args: Parameters<typeof projects.getProjectDiffPage>[0]) =>
      receive(() => projects.getProjectDiffPage(args)),
    confirmProjectChangeset: (args: Parameters<typeof projects.confirmProjectChangeset>[0]) =>
      receive(() => projects.confirmProjectChangeset(args)),
    commitProjectChangeSet: (args: Parameters<typeof projects.commitProjectChangeSet>[0]) =>
      receive(() => projects.commitProjectChangeSet(args)),
    getJob: (id: string) => tasks.getJob(id),
  }
  const read = async () => unwrap(await bridge.readProject({ editor: 'ontology' }))
  const { projectId } = unwrap(
    await receive(() =>
      projects.createBlankProject({
        requestVersion: 1,
        operationId: randomUUID(),
        name: 'W3b loopback',
        initialization: { kind: 'blank' },
      }),
    ),
  )
  unwrap(await receive(() => projects.openProject({ projectId })))

  const requests: { body: Buffer; method?: string; authorization?: string; url?: string }[] = []
  const responders: ((response: ServerResponse) => void)[] = []
  const server = createServer(async (request, response) => {
    const chunks: Buffer[] = []
    for await (const chunk of request) chunks.push(Buffer.from(chunk))
    requests.push({
      body: Buffer.concat(chunks),
      method: request.method,
      authorization: request.headers.authorization,
      url: request.url,
    })
    const respond = responders.shift()
    if (respond) respond(response)
    else response.writeHead(500).end()
  })
  await new Promise<void>((ready, reject) => {
    server.once('error', reject)
    server.listen(0, '127.0.0.1', ready)
  })
  cleanup.push(
    () =>
      new Promise<void>((done, reject) => {
        server.close((error) => (error ? reject(error) : done()))
        server.closeAllConnections()
      }),
  )
  const address = server.address()
  if (address === null || typeof address === 'string') throw new Error('Missing loopback address')
  const endpoint = `http://127.0.0.1:${address.port}/chat/completions`
  const policy = 'loopback-probe-only' as const
  const location = { userDataPath, excludedRoots: [data] }
  const repository = await ConfigurationRepository.open(location)
  cleanup.push(() => repository.close())
  const audit = await PersistentGatewayAudit.open(location)
  cleanup.push(() => audit.close())
  const ciphertext = await PrivateCiphertextRepository.open(location)
  cleanup.push(() => ciphertext.close())

  // Node owns a throwaway AES key in place of Electron's OS keyring. Credentials,
  // configuration, audit, scope admission and socket transport use their real paths.
  const key = randomBytes(32)
  const credentials = new EncryptedCredentialBoundary(
    {
      isEncryptionAvailable: () => true,
      getSelectedStorageBackend: () => 'gnome_libsecret',
      encryptString(text) {
        const nonce = randomBytes(12)
        const cipher = createCipheriv('aes-256-gcm', key, nonce)
        const body = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()])
        return Buffer.concat([nonce, cipher.getAuthTag(), body])
      },
      decryptString(bytes) {
        const decipher = createDecipheriv('aes-256-gcm', key, bytes.subarray(0, 12))
        decipher.setAuthTag(bytes.subarray(12, 28))
        return Buffer.concat([decipher.update(bytes.subarray(28)), decipher.final()]).toString(
          'utf8',
        )
      },
    },
    ciphertext,
    process.platform,
  )
  const service = await ModelGatewayService.open({
    engine,
    repository,
    credentials,
    audit,
    endpointPolicy: policy,
  })
  owners.models = service
  cleanup.push(() => service.close())
  service.selectProject(projectId)
  const contextId = service.status().contextId!
  const configured = await service.configure({
    contextId,
    configurationId: null,
    configurationVersion: null,
    displayName: 'Loopback fixture',
    endpoint,
    model: REQUEST_MODEL,
  })
  const secret = 'synthetic-' + randomUUID()
  const credential = await service.storeCredential({
    contextId,
    configurationId: configured.configurationId,
    configurationVersion: configured.configurationVersion,
    secret,
  })
  service.setPrivacy({ contextId, privacy: 'project' })
  const approved: Buffer[] = []
  const approval: AgentProviderApproval = {
    configurationId: credential.configurationId,
    configurationVersion: credential.configurationVersion,
    signature: {
      endpoint: DEEPSEEK_ENDPOINT,
      requestedModel: REQUEST_MODEL,
      returnedModel: REQUEST_MODEL,
      fingerprint: null,
      codecVersion: CODEC_VERSION,
      mode: 'disabled',
      effort: 'low',
    },
    async confirmBody(input) {
      expect(input).toMatchObject({ endpoint, projectId, privacy: 'project' })
      approved.push(Buffer.from(input.body, 'utf8'))
      return true
    },
  }
  const agent = new AgentHostComposition({
    selection: () => projects.source.current(),
    blocked: () => projects.managementBlocked || projects.restoreBlocked,
    modes: new AgentModeStore(join(userDataPath, 'agent', 'modes.json')),
    projects,
    tasks,
    replies,
    models: () => service,
    providerApproval: approval,
  })
  owners.host = agent
  projects.source.observe(() => agent.refresh())
  cleanup.push(() => agent.close())

  async function call<T>(work: () => Promise<BridgeResult<T>>) {
    return unwrap(await receive(work))
  }
  function respond(message: object, finishReason: 'stop' | 'tool_calls') {
    responders.push((response) =>
      response
        .writeHead(200, { 'Content-Type': 'application/json' })
        .end(completion(message, finishReason)),
    )
  }
  function dispatch(args: Partial<AgentDispatchArgs> = {}) {
    return agent
      .dispatchAgentQuestion({
        operationId: randomUUID(),
        question: '设备需要什么？',
        module: 'ontology',
        mode: 'tutor',
        scope: 'asserted',
        selectedObjectIds: [],
        ...args,
      })
      .then(unwrap)
  }
  async function status(expected: 'answered' | 'failed') {
    await expect
      .poll(async () => {
        const { status, failureCode } = unwrap(await agent.getAgentState())
        return status === 'failed' && expected === 'answered' ? failureCode : status
      })
      .toBe(expected)
    return unwrap(await agent.getAgentState())
  }
  const unguarded = () => {}
  async function change(plan: MainlineChangePlanDTO) {
    const preview = await prepareWorkspaceChange(bridge, await read(), plan, unguarded)
    const job = await commitWorkspaceChange(bridge, preview, randomUUID(), unguarded)
    expect(job.state, job.error?.code).toBe('succeeded')
  }
  function quality(constraintId: string) {
    return call(() =>
      projects.runProjectQualityCheck({
        projectId,
        operationId: randomUUID(),
        constraintId,
        selection: { kind: 'current' },
        validationScope: 'asserted',
      }),
    )
  }
  return {
    projectId,
    projects,
    tasks,
    bridge,
    read,
    call,
    agent,
    service,
    audit,
    credentials,
    repository,
    contextId,
    endpoint,
    policy,
    secret,
    approval,
    approved,
    requests,
    responders,
    respond,
    dispatch,
    status,
    change,
    quality,
  }
}

it(
  'preserves signed request bytes and rejects unregistered text and local privacy before HTTP',
  { timeout: 20_000 },
  async () => {
    const f = await fixture()
    const messages = [
      { role: 'system', content: 'Return JSON.' },
      { role: 'user', content: '设备 🎛 "标签"\n第二行' },
    ]
    const body = JSON.stringify(
      encodeChatRequest({
        messages,
        mode: 'disabled',
        effort: 'low',
        maxTokens: 64,
        availableTools: [],
      }),
      null,
      2,
    )
    const input = { projectId: f.projectId, purpose: 'suggest' as const, body }
    const signal = new AbortController().signal
    const stored = (await f.repository.load())[0]
    expect(stored.binding).not.toBeNull()
    const core = new ModelGatewayCore(f.credentials, f.audit, f.policy)
    const configId = stored.configurationId
    const { ref, principal, version: credentialVersion } = stored.binding!
    const { version } = core.configure({
      id: configId,
      endpoint: f.endpoint,
      model: REQUEST_MODEL,
      credentialRef: ref,
      principal,
      credentialVersion,
    })
    core.setPrivacy(f.projectId, 'project')
    const scopes = [randomUUID()]
    const { previewId } = core.previewAuthorization({
      projectId: f.projectId,
      configId,
      scopes,
      purpose: 'suggest',
    })
    const grantId = core.confirmAuthorization(previewId)
    const parts = messages.map(({ content }, index) => {
      const kind = index === 0 ? 'history' : 'selected'
      return {
        path: `messages.${index}.content`,
        kind,
        materialId: core.registerMaterial({ projectId: f.projectId, scopes, kind, text: content }),
      }
    })
    await expect(
      core.invokeApprovedBody({
        ...input,
        configId,
        configVersion: version,
        grantId,
        scopes,
        parts,
        body: body.replace('第二行', '未核准的合成文本'),
      }),
    ).resolves.toEqual({ ok: false, code: 'SCOPE_EXCEEDED' })
    expect(f.requests).toHaveLength(0)

    f.service.setPrivacy({ contextId: f.contextId, privacy: 'local' })
    await expect(
      f.service.invokeAgentBody(input, f.approval, signal, () => true),
    ).rejects.toMatchObject({ code: 'LOCAL_ONLY' })
    await f.dispatch({ question: messages[1].content })
    expect(await f.status('failed')).toMatchObject({
      failureCode: 'LOCAL_ONLY',
      retainedQuestion: messages[1].content,
      receipts: [],
    })
    expect(f.approved).toHaveLength(0)
    expect(f.requests).toHaveLength(0)

    f.service.setPrivacy({ contextId: f.contextId, privacy: 'project' })
    f.respond({ content: '{"kind":"uncertain"}' }, 'stop')
    await expect(
      f.service.invokeAgentBody(input, f.approval, signal, () => true),
    ).resolves.toContain(REQUEST_MODEL)
    expect(f.approved).toEqual([Buffer.from(body)])
    expect(f.requests).toEqual([
      {
        body: f.approved[0],
        method: 'POST',
        url: '/chat/completions',
        authorization: `Bearer ${f.secret}`,
      },
    ])
    expect(await f.audit.readEntries()).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          record: expect.objectContaining({ event: 'attempt-intent', decision: 'authorized' }),
        }),
      ]),
    )
    expect(JSON.stringify(await f.audit.readEntries())).not.toContain(f.secret)
  },
)

it(
  'runs real read, quality and draft tools and fences an outdated second HTTP turn',
  { timeout: 25_000 },
  async () => {
    const f = await fixture()
    const id = 'sample-ontology'
    const subject = learning + 'SampleEquipment'
    await f.change({
      definitions: [
        {
          layer: 'ontology',
          id,
          value: { triples: [{ subject, predicate: rdfType, object: owlClass }] },
        },
        equipmentConstraint(),
      ],
    })
    const before = await f.read()
    const query = {
      kind: 'query-draft',
      name: '设备',
      description: '',
      sparql: 'SELECT ?s WHERE { ?s ?p ?o }',
      capabilityQuestion: '有哪些设备？',
    }
    f.respond(
      {
        content: null,
        tool_calls: [
          toolCall('ontology_read', { objectIds: [id] }),
          ontologyTool(),
          toolCall('query_draft', { question: JSON.stringify(query), scope: 'asserted' }),
          toolCall('quality_check', { scope: 'asserted' }),
        ],
      },
      'tool_calls',
    )
    f.respond({ content: '{"kind":"uncertain"}' }, 'stop')
    await f.dispatch({ selectedObjectIds: [id] })
    const answered = await f.status('answered')
    expect(answered.receipts, JSON.stringify(answered.receipts)).toMatchObject([
      {
        tool: 'ontology_read',
        outcome: {
          kind: 'evidence',
          status: 'current',
          inputSnapshotId: before.inputSnapshotId,
          fields: [
            { fieldId: 'triple-0-subject', value: subject },
            { fieldId: 'triple-0-predicate', value: rdfType },
            { fieldId: 'triple-0-object', value: owlClass },
          ],
        },
      },
      {
        tool: 'ontology_propose',
        outcome: {
          kind: 'draft',
          draftType: 'ontology',
          requiresHumanDiffConfirmation: true,
          baseRevision: before.domain.projectRevision,
        },
      },
      {
        tool: 'query_draft',
        outcome: { kind: 'draft', draftType: 'query', requiresHumanDiffConfirmation: true },
      },
      {
        tool: 'quality_check',
        outcome: { kind: 'evidence', status: 'current', inputSnapshotId: before.inputSnapshotId },
      },
    ])
    expect(JSON.parse((answered.receipts[2].outcome as { detail: string }).detail)).toEqual({
      name: query.name,
      description: query.description,
      sparql: query.sparql,
      scope: 'asserted',
      capabilityQuestion: query.capabilityQuestion,
      source: 'model',
    })
    const quality = await f.call(() =>
      f.projects.getProjectQualityState({ projectId: f.projectId }),
    )
    expect(quality.validation?.resultId).toBe(
      (answered.receipts[3].outcome as { resultId: string }).resultId,
    )
    expect((await f.read()).domain.state).toEqual(before.domain.state)
    expect(f.requests.map(({ body }) => body)).toEqual(f.approved)
    expect(f.requests).toHaveLength(2)
    const second = JSON.parse(f.requests[1].body.toString('utf8'))
    expect(second.messages.filter(({ role }: { role: string }) => role === 'tool')).toHaveLength(4)
    expect(f.requests[1].body.toString('utf8')).not.toContain(subject)
    const audit = unwrap(await f.agent.listAgentAudit({ projectId: f.projectId }))
    expect(audit.items).toHaveLength(2)
    for (const value of [answered.receipts, audit, await f.audit.readEntries()]) {
      expect(JSON.stringify(value)).not.toContain(f.secret)
    }

    expect(FORMAL_WRITE_TOOLS).toHaveLength(0)
    f.respond(
      {
        content: null,
        tool_calls: [toolCall('mapping_propose', { sourceId: 'sample', instruction: '提议映射' })],
      },
      'tool_calls',
    )
    await f.dispatch()
    expect(await f.status('failed')).toMatchObject({
      failureCode: 'TOOL_UNAVAILABLE',
      receipts: [],
    })
    expect(f.requests).toHaveLength(3)

    f.respond(
      { content: null, tool_calls: [toolCall('ontology_read', { objectIds: [id] })] },
      'tool_calls',
    )
    let responseClosed = false
    f.responders.push((response) =>
      response.once('close', () => {
        responseClosed = true
      }),
    )
    const stale = await f.dispatch({ selectedObjectIds: [id] })
    await expect.poll(() => f.requests.length).toBe(5)
    await f.change({
      definitions: [
        {
          layer: 'ontology',
          id: 'changed-during-turn',
          value: {
            triples: [{ subject: learning + 'NewClass', predicate: rdfType, object: owlClass }],
          },
        },
      ],
    })
    expect((await f.read()).domain.projectRevision).toBe(before.domain.projectRevision + 1)
    expect(await f.status('failed')).toMatchObject({
      failureCode: 'STALE_CONTEXT',
      operationId: stale.operationId,
      receipts: [],
    })
    await expect.poll(() => responseClosed).toBe(true)
    await expect(
      f.agent.buildAgentDraftPlan({ operationId: stale.operationId }),
    ).resolves.toMatchObject({ error: { code: 'STALE_CONTEXT' } })
    expect(f.requests).toHaveLength(5)
  },
)

it(
  'commits an Agent draft after its checkpoint, excludes full assistance from transfer success, and restores the prior ontology',
  { timeout: 30_000 },
  async () => {
    const f = await fixture()
    const { projectId, projects } = f
    const taskId = 'transfer-repair'
    const unguarded = () => {}
    const lesson = await prepareLearningTaskFixture(f.bridge, projectId, taskId, unguarded)
    expect(lesson).toBeDefined()
    const seeded = await commitWorkspaceChange(f.bridge, lesson!, randomUUID(), unguarded)
    expect(seeded.state, seeded.error?.code).toBe('succeeded')
    await f.change({ definitions: [equipmentConstraint()] })
    for (const target of ['business-ontology', taskId] as const) {
      const task = await f.call(() =>
        projects.startLearningAttempt({ projectId, taskId: target, operationId: randomUUID() }),
      )
      expect(task.learningState).toMatchObject({
        assistance: 'independent',
        operationComplete: false,
      })
    }
    const baselineValidation = (await f.quality(constraintId)).qualityState.validation
    expect(baselineValidation).toMatchObject({ state: 'current', conforms: false })
    expect(baselineValidation?.findings.length).toBeGreaterThan(0)
    await f.change(
      await newManualFactPlan(await f.read(), {
        subject: learning + 'equipment/102',
        predicate: learning + 'name',
        object: '"供水泵"',
      }),
    )
    const before = await f.read()
    unwrap(await f.agent.setAgentMode({ projectId, mode: 'project' }))
    f.respond({ content: null, tool_calls: [ontologyTool()] }, 'tool_calls')
    f.respond({ content: '{"kind":"uncertain"}' }, 'stop')
    const { operationId } = await f.dispatch({ mode: 'project' })
    expect(await f.status('answered')).toMatchObject({ receipts: [{ tool: 'ontology_propose' }] })
    const draft = unwrap(await f.agent.buildAgentDraftPlan({ operationId }))
    const preview = await prepareWorkspaceChange(
      {
        ...f.bridge,
        async previewProjectChangeset(args) {
          const reply = await f.bridge.previewProjectChangeset(args)
          if (reply.ok) f.agent.observeDraftPreview(args, reply.data)
          return reply
        },
      },
      before,
      draft.plan,
      unguarded,
    )
    expect(preview.rows.length).toBeGreaterThan(0)
    const confirmation = unwrap(
      await f.bridge.confirmProjectChangeset({
        previewHash: preview.preview.previewHash,
        completionCursor: preview.completionCursor,
      }),
    )
    f.agent.observeDraftConfirmation(confirmation)
    expect(confirmation).toMatchObject({
      projectId,
      previewHash: preview.preview.previewHash,
      inputSnapshotId: before.inputSnapshotId,
      preparedPlanRef: preview.preview.preparedPlanRef,
      parametersHash: preview.preview.parametersHash,
    })
    await expect(
      f.agent.commitAgentDraft({
        operationId,
        draftType: 'ontology',
        confirmation: { ...confirmation, confirmationRef: randomUUID() },
      }),
    ).resolves.toMatchObject({ ok: false, error: { code: 'STALE_CONTEXT' } })
    const priorCheckpoints = await f.call(() =>
      projects.listProjectCheckpoints({ pageSize: 50, cursor: null }),
    )
    expect(priorCheckpoints.items.map(({ reason }) => reason)).not.toContain('before-agent')
    const committed = unwrap(
      await f.agent.commitAgentDraft({
        operationId,
        draftType: 'ontology',
        confirmation,
      }),
    )
    expect(committed).toMatchObject({
      operationId,
      reason: 'before-agent',
      assistanceUpdatedTaskIds: expect.arrayContaining(['business-ontology', taskId]),
    })
    await expect
      .poll(async () => {
        const job = unwrap(await f.tasks.getJob(committed.job.jobId))
        return job.state === 'failed' ? job.error?.code : job.state
      })
      .toBe('succeeded')
    const after = await f.read()
    expect(after.domain.projectRevision).toBe(before.domain.projectRevision + 1)
    expect(JSON.stringify(before.domain.state.definitions)).not.toContain(proposedClass)
    expect(JSON.stringify(after.domain.state.definitions)).toContain(proposedClass)
    const { items } = await f.call(() =>
      projects.listProjectCheckpoints({ pageSize: 50, cursor: null }),
    )
    const checkpoint = items.find(
      ({ checkpointRef }) => checkpointRef === committed.beforeAgentCheckpointRef,
    )
    expect(checkpoint).toMatchObject({
      reason: 'before-agent',
      domainRevision: before.domain.projectRevision,
    })
    expect(items[0]).toMatchObject({ domainRevision: after.domain.projectRevision })
    expect(checkpoint!.operationSequence).toBeLessThan(items[0].operationSequence)

    await f.quality(constraintId)
    const checked = await f.call(() =>
      projects.checkLearningTask({ projectId, taskId, operationId: randomUUID() }),
    )
    expect(checked, JSON.stringify(checked.feedback)).toMatchObject({
      checkStatus: 'passed',
      operationComplete: true,
      assistance: 'agent-full-assistance',
      independentTransferSuccess: false,
    })

    const current = await f.call(() => projects.getProjectManagementState())
    const restore = await f.call(() =>
      projects.previewProjectRestore({
        targetCheckpointRef: committed.beforeAgentCheckpointRef,
        expectedCheckpointRef: current.checkpointRef,
        expectedLifecycleVersion: current.lifecycle.version,
      }),
    )
    expect(restore.domainWillRestore).toBe(true)
    const readSegmentHashes: string[] = []
    let cursor: string | null = null
    do {
      const page = await f.call(() =>
        projects.getProjectRestorePage({ previewRef: restore.previewRef, cursor }),
      )
      expect(page.documentHash).toBe(restore.documentHash)
      for (const segment of page.segments) {
        const bytes = Buffer.from(segment.dataBase64, 'base64')
        expect(bytes.length).toBe(segment.rawByteLength)
        expect(createHash('sha256').update(bytes).digest('hex')).toBe(segment.sha256)
        readSegmentHashes.push(segment.sha256)
      }
      cursor = page.nextCursor
      expect(page.complete).toBe(cursor === null)
    } while (cursor !== null)
    const confirmed = await f.call(() =>
      projects.confirmProjectRestore({
        previewRef: restore.previewRef,
        documentHash: restore.documentHash,
        readSegmentHashes,
      }),
    )
    const restored = await f.call(() =>
      projects.restoreProject({
        operationId: randomUUID(),
        confirmationRef: confirmed.confirmationRef,
        documentHash: restore.documentHash,
      }),
    )
    expect(restored.restoredFromCheckpointRef).toBe(committed.beforeAgentCheckpointRef)
    expect((await f.read()).domain.state).toEqual(before.domain.state)
  },
)
