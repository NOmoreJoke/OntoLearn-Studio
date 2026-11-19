import { randomUUID } from 'node:crypto'
import {
  agentIpcMethods,
  type AgentCommitDraftArgs,
  type AgentDispatchArgs,
  type ChangeSetPreview,
} from '@ontolearn/contracts'
import type { IpcMainInvokeEvent } from 'electron'
import { describe, expect, it, vi } from 'vitest'
import {
  registerDesktopIpc,
  type DesktopIpcDependencies,
} from '../../apps/desktop/src/main/desktop-ipc'
import {
  AgentHostComposition,
  deriveBeforeCommitOp,
} from '../../apps/desktop/src/main/agent/host-composition'
import { AgentModeStore } from '../../apps/desktop/src/main/agent/agent-mode-store'
import {
  CODEC_VERSION,
  DEEPSEEK_ENDPOINT,
  REQUEST_MODEL,
} from '../../apps/desktop/src/main/agent/deepseek-codec'
import { MainlineReplyReceipt } from '../../apps/desktop/src/main/engine'

type HostDependencies = ConstructorParameters<typeof AgentHostComposition>[0]
const hash = 'a'.repeat(64)
const snapshot = 'b'.repeat(64)
const receipt = new (class extends MainlineReplyReceipt {})()
const goodSender = {} as IpcMainInvokeEvent['sender']
const trustedEvent = { sender: goodSender, senderFrame: {} } as IpcMainInvokeEvent
const untrustedEvent = { sender: {}, senderFrame: {} } as IpcMainInvokeEvent

function setup(privacy: 'local' | 'project' = 'project') {
  const projectId = randomUUID()
  const operationId = randomUUID()
  const modes = new AgentModeStore()
  modes.set(projectId, 'project')
  const question: AgentDispatchArgs = {
    operationId,
    question: '请建议新增设备类',
    module: 'ontology',
    mode: 'project',
    scope: 'asserted',
    selectedObjectIds: [],
  }
  const preview: Extract<ChangeSetPreview, { status: 'ready' }> = {
    status: 'ready',
    projectId,
    previewHash: hash,
    preparedPlanRef: hash,
    inputSnapshotId: snapshot,
    parametersHash: hash,
    baseRevision: 5,
    summary: '新增设备类',
    intent: 'change',
    targetOperationId: null,
    manifest: {
      documentKind: 'diff',
      documentHash: hash,
      totalBytes: 0,
      segmentCount: 0,
      segments: [],
    },
  }
  const confirmation: AgentCommitDraftArgs['confirmation'] = {
    projectId,
    previewHash: hash,
    preparedPlanRef: hash,
    inputSnapshotId: snapshot,
    parametersHash: hash,
    confirmationRef: randomUUID(),
  }
  const commitArgs: AgentCommitDraftArgs = { operationId, draftType: 'ontology', confirmation }
  const selection = {
    owner: {},
    engineSessionId: 'engine-1',
    selectionSeq: 1,
    project: {
      projectId,
      projectRevision: 5,
      inputSnapshotId: snapshot,
      dependencyVector: {},
      formatVersion: 3 as const,
    },
  }
  const calls: string[] = []
  const recordAgentBeforeCommit = vi.fn<HostDependencies['projects']['recordAgentBeforeCommit']>()
  recordAgentBeforeCommit.mockImplementation(async (args) => {
    calls.push('checkpoint')
    return {
      ok: true,
      data: {
        projectId,
        operationId: args.operationId,
        reason: 'before-agent',
        checkpointRef: 'real-checkpoint',
        domainRevision: 5,
        agentBeforeCommitVersion: 1,
        assistanceUpdatedTaskIds: ['task-active'],
      },
    }
  })
  const commitProjectChangeSet = vi.fn<HostDependencies['projects']['commitProjectChangeSet']>()
  commitProjectChangeSet.mockImplementation(async (args) => {
    calls.push('commit')
    return {
      ok: true,
      data: {
        projectId,
        operationId: args.operationId,
        inputSnapshotId: snapshot,
        jobId: 'job-1',
        state: 'queued',
        stateVersion: 1,
        resultRef: null,
        error: null,
      },
    }
  })
  const invokeAgentBody =
    vi.fn<NonNullable<ReturnType<HostDependencies['models']>>['invokeAgentBody']>()
  const response = (id: string, message: object, toolCalls = false) =>
    JSON.stringify({
      id,
      object: 'chat.completion',
      created: 0,
      model: REQUEST_MODEL,
      choices: [
        {
          index: 0,
          finish_reason: toolCalls ? 'tool_calls' : 'stop',
          message: { role: 'assistant', ...message },
        },
      ],
    })
  invokeAgentBody.mockResolvedValueOnce(
    response(
      'tool-turn',
      {
        content: null,
        tool_calls: [
          {
            id: 'class-draft',
            type: 'function',
            function: {
              name: 'ontology_propose',
              arguments: JSON.stringify({
                instruction: JSON.stringify({ classIri: 'urn:example:Equipment' }),
              }),
            },
          },
        ],
      },
      true,
    ),
  )
  invokeAgentBody.mockResolvedValueOnce(
    response('final-turn', { content: '{"kind":"evidence","callIds":["class-draft"]}' }),
  )
  const flags = { switching: false, managementBlocked: false, restoreBlocked: false }
  const replies = {
    receive: async <T>(work: () => Promise<T>) => ({ value: await work(), receipt }),
    binding: () => ({ engineSessionId: selection.engineSessionId }),
    consume: vi.fn(),
    diagnostic: vi.fn(),
  }
  const projects = {
    get managementBlocked() {
      return flags.managementBlocked
    },
    get restoreBlocked() {
      return flags.restoreBlocked
    },
    readProject: vi.fn(),
    getProjectQualityState: vi.fn(),
    runProjectQualityCheck: vi.fn(),
    queries: {
      loadQueryDefinition: vi.fn(),
      executeSavedQuery: vi.fn(),
      getQueryResultDescriptor: vi.fn(),
    },
    recordAgentBeforeCommit,
    commitProjectChangeSet,
    previewProjectChangeset: vi.fn(async () => ({ ok: true as const, data: preview })),
    confirmProjectChangeset: vi.fn(async () => ({ ok: true as const, data: confirmation })),
  }
  const host = new AgentHostComposition({
    selection: () => selection,
    blocked: () => Object.values(flags).some(Boolean),
    modes,
    projects,
    replies,
    tasks: { getJob: vi.fn(), getResult: vi.fn() },
    providerApproval: {
      configurationId: randomUUID(),
      configurationVersion: randomUUID(),
      confirmBody: async () => true,
      signature: {
        endpoint: DEEPSEEK_ENDPOINT,
        requestedModel: REQUEST_MODEL,
        returnedModel: REQUEST_MODEL,
        fingerprint: null,
        codecVersion: CODEC_VERSION,
        mode: 'disabled',
        effort: 'low',
      },
    },
    models: () => ({
      status: () => ({
        availability: 'ready',
        contextId: 'context',
        projectId,
        privacy,
        configurations: [],
        selections: [],
        invocations: [],
      }),
      agentReady: () => privacy === 'project',
      invokeAgentBody,
      listConfigurationSummaries: () => [],
      setConfigurationEnabled: vi.fn(),
      removeConfiguration: vi.fn(),
      probeCapabilities: vi.fn(),
      listAuditEntries: vi.fn(),
    }),
  })
  const handlers = new Map<string, Parameters<DesktopIpcDependencies['ipcMain']['handle']>[1]>()
  const getAgent = vi.fn(() => host)
  registerDesktopIpc({
    ipcMain: {
      handle: (channel, handler) => {
        handlers.set(channel, handler)
      },
    },
    trusted: (event) =>
      event.sender === goodSender && event.senderFrame === trustedEvent.senderFrame,
    tasks: {} as DesktopIpcDependencies['tasks'],
    supervisor: {
      engineSessionId: selection.engineSessionId,
      health: vi.fn(),
      projectFailure: vi.fn(),
    },
    library: {
      get switching() {
        return flags.switching
      },
    } as DesktopIpcDependencies['library'],
    projects: projects as unknown as DesktopIpcDependencies['projects'],
    replies: replies as DesktopIpcDependencies['replies'],
    getAgent,
  })
  const invoke = (channel: string, input?: unknown, event = trustedEvent) =>
    handlers.get(channel)!(event, input)
  const prepare = async (confirm = true) => {
    expect(await invoke('agent:dispatch', question)).toMatchObject({ ok: true })
    await vi.waitFor(async () =>
      expect(await invoke('agent:state')).toMatchObject({ data: { status: 'answered' } }),
    )
    const plan = await host.buildAgentDraftPlan({ operationId })
    if (!plan.ok) throw new Error(plan.error.code)
    const result = await invoke('project:changeset-preview', {
      intent: 'change',
      baseRevision: plan.data.baseRevision,
      plan: plan.data.plan,
    })
    expect(result).toMatchObject({ payload: { ok: true } })
    if (confirm)
      expect(
        await invoke('project:changeset-confirm', { previewHash: hash, completionCursor: 'end' }),
      ).toMatchObject({ payload: { ok: true } })
  }
  return {
    getAgent,
    invoke,
    flags,
    question,
    prepare,
    commitArgs,
    selection,
    calls,
    invokeAgentBody,
    recordAgentBeforeCommit,
    commitProjectChangeSet,
  }
}

describe('Agent routes in production desktop registration', () => {
  it('denies each of the 11 channels from an external window, foreign frame or switching library', async () => {
    const { invoke, flags, getAgent } = setup()
    const denied = { ok: false, error: { code: 'PERMISSION_DENIED' } }
    const channels = Object.keys(agentIpcMethods)
    expect(channels).toHaveLength(11)
    for (const channel of channels) {
      expect(await invoke(channel, undefined, untrustedEvent)).toMatchObject(denied)
      expect(
        await invoke(channel, undefined, {
          ...trustedEvent,
          senderFrame: {} as IpcMainInvokeEvent['senderFrame'],
        }),
      ).toMatchObject(denied)
    }
    flags.switching = true
    for (const channel of channels) expect(await invoke(channel)).toMatchObject(denied)
    expect(getAgent).not.toHaveBeenCalled()
  })
  it.each(['managementBlocked', 'restoreBlocked'] as const)(
    'fences protected routes while %s',
    async (flag) => {
      const { invoke, flags, getAgent } = setup()
      flags[flag] = true
      for (const channel of [
        'agent:dispatch',
        'agent:set-mode',
        'agent:commit-draft',
        'agent-model:probe',
        'agent-model:set-enabled',
        'agent-model:remove',
      ]) {
        expect(await invoke(channel)).toMatchObject({ error: { code: 'PERMISSION_DENIED' } })
      }
      expect(getAgent).not.toHaveBeenCalled()
      expect(await invoke('agent:context')).toMatchObject({ ok: true })
    },
  )
  it('never sends under local privacy and retains the question in state', async () => {
    const { invoke, question, invokeAgentBody } = setup('local')
    expect(await invoke('agent:dispatch', question)).toMatchObject({ ok: true })
    expect(await invoke('agent:state')).toMatchObject({
      data: { status: 'failed', failureCode: 'LOCAL_ONLY', retainedQuestion: question.question },
    })
    expect(invokeAgentBody).not.toHaveBeenCalled()
  })
  it('requires the actual confirmation and calls the checkpoint before committing with a stable operation id', async () => {
    const f = setup()
    await f.prepare(false)
    expect(await f.invoke('agent:commit-draft', f.commitArgs)).toMatchObject({
      error: { code: 'STALE_CONTEXT' },
    })
    expect(f.calls).toEqual([])
    await f.invoke('project:changeset-confirm', { previewHash: hash, completionCursor: 'end' })
    const forged = {
      ...f.commitArgs,
      confirmation: { ...f.commitArgs.confirmation, confirmationRef: randomUUID() },
    }
    expect(await f.invoke('agent:commit-draft', forged)).toMatchObject({
      error: { code: 'STALE_CONTEXT' },
    })
    const outcomes = await Promise.all([
      f.invoke('agent:commit-draft', f.commitArgs),
      f.invoke('agent:commit-draft', f.commitArgs),
    ])
    expect(outcomes[0]).toMatchObject({
      ok: true,
      data: {
        beforeAgentCheckpointRef: 'real-checkpoint',
        reason: 'before-agent',
        assistanceUpdatedTaskIds: ['task-active'],
        job: { jobId: 'job-1' },
      },
    })
    expect(outcomes[0]).toEqual(outcomes[1])
    expect(f.calls).toEqual(['checkpoint', 'commit'])
    expect(f.recordAgentBeforeCommit).toHaveBeenCalledExactlyOnceWith({
      projectId: f.selection.project.projectId,
      operationId: deriveBeforeCommitOp(f.commitArgs.operationId),
      baseRevision: 5,
      recordFullAssistance: true,
      taskIds: ['business-ontology', 'transfer-repair'],
      label: null,
    })
    expect(f.commitProjectChangeSet).toHaveBeenCalledExactlyOnceWith({
      operationId: f.commitArgs.operationId,
      confirmation: f.commitArgs.confirmation,
    })
  })
  it('forwards an explicit taskIds selection instead of the default full-assistance list', async () => {
    const f = setup()
    await f.prepare()
    const result = await f.invoke('agent:commit-draft', {
      ...f.commitArgs,
      taskIds: ['quality'],
    })
    expect(result).toMatchObject({ ok: true })
    expect(f.recordAgentBeforeCommit).toHaveBeenCalledExactlyOnceWith({
      projectId: f.selection.project.projectId,
      operationId: deriveBeforeCommitOp(f.commitArgs.operationId),
      baseRevision: 5,
      recordFullAssistance: true,
      taskIds: ['quality'],
      label: null,
    })
  })
  it('stops a stale commit after the checkpoint await without entering ChangeSet commit', async () => {
    const f = setup()
    await f.prepare()
    const original = f.recordAgentBeforeCommit.getMockImplementation()!
    f.recordAgentBeforeCommit.mockImplementationOnce(async (args) => {
      const result = await original(args)
      f.selection.project.projectRevision++
      return result
    })
    expect(await f.invoke('agent:commit-draft', f.commitArgs)).toMatchObject({
      error: { code: 'STALE_CONTEXT' },
    })
    expect(f.commitProjectChangeSet).not.toHaveBeenCalled()
  })
})
