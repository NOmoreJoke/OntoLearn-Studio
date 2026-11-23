/** L1 learning ledger contract, named IPC/preload bridge and service wiring. */
import { describe, expect, it, vi } from 'vitest'
import { EventEmitter } from 'node:events'
import { PassThrough, Writable } from 'node:stream'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { randomUUID } from 'node:crypto'
const processDouble = vi.hoisted(() => ({ spawn: vi.fn() }))
vi.mock('node:child_process', () => ({ spawn: processDouble.spawn }))
import { EngineSupervisor } from '../../apps/desktop/src/main/engine'
import { ProjectMainlineService } from '../../apps/desktop/src/main/project-mainline-service'
import { registerDesktopIpc } from '../../apps/desktop/src/main/desktop-ipc'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import {
  validateBusiness3,
  matchesBusiness3Response,
  v2Registry,
} from '../../packages/contracts/src/v2'
import schema from '../../packages/contracts/v2/schema.json'
import corpus from '../../packages/contracts/v2/fixtures.json'
import type { BridgeResult } from '@ontolearn/contracts'

type Row = Record<string, unknown>
const id = (n: number) => '00000000-0000-4000-8000-' + String(n).padStart(12, '0')
const registryPath = fileURLToPath(
  new URL('../../packages/contracts/v2/registry.json', import.meta.url),
)
const registryHash = createHash('sha256').update(readFileSync(registryPath)).digest('hex')
const limits = structuredClone(corpus.queryConsumer.samples.prepared.executionIdentity.limits)
const projectId = id(1)
const operationId = id(3)
const snapshot = 'a'.repeat(64)

const LEARNING_METHODS = [
  'project.learning.read',
  'project.learning.attempt.start',
  'project.learning.hint.record',
  'project.learning.observation.record',
  'project.learning.task.check',
] as const

const taskState = (): Row => ({
  taskId: 'business-ontology',
  module: '本体构建',
  goal: '把业务问题变成概念、属性、个体与关系。',
  instructions: '独立还原 G-base。',
  steps: [
    {
      index: 0,
      kind: 'observation',
      scored: false,
      readingRef: 'business-question',
      title: '先观察，不计分',
      text: '先读 business-question。',
    },
  ],
  completionCondition: '实际批准工具的当前版本完整结果与固定预期一致。',
  commonErrors: ['把个体建成类'],
  knowledgePoints: ['类与个体'],
  transfer: false,
  next: 'mapping',
  checks: ['ontology-model'],
  readings: [
    {
      id: 'business-question',
      title: '业务问题',
      sourceRef: 'PRD 附录G',
      optional: false,
      summary: '设备运维业务问题',
      content: '哪些设备存在未闭环高危告警？',
      selfAssessment: [
        {
          question: '设备是什么？',
          options: [
            { id: 'a', text: '类' },
            { id: 'b', text: '个体' },
          ],
        },
      ],
    },
  ],
  attemptCount: 1,
  withdrawnAttemptCount: 0,
  attemptId: id(9),
  attemptActivationEpoch: 1,
  recordVersion: 2,
  assistance: 'partial-hints',
  maxHintLevel: 1,
  revealedHints: [{ level: 1, kind: 'concept', text: '先问：哪台设备有未闭环高危告警？' }],
  operationComplete: false,
  independentTransferSuccess: false,
  checkStatus: 'not-checked',
  staleInput: false,
  lastFeedback: null,
  observations: { openedReadingIds: [], answeredAssessments: [] },
  completedGuidedStages: [],
  guidedStageCheckpointRef: null,
  rootSnapshotRef: snapshot,
  boundSnapshotRef: null,
  boundDomainRevision: null,
  inputVersion: 'rev-2:' + snapshot,
})

const readResult = (): Row => ({
  learningReadVersion: 1,
  projectId,
  domainRevision: 2,
  domainSnapshotRef: snapshot,
  inputVersion: 'rev-2:' + snapshot,
  templateRef: null,
  withdrawnAttemptCount: 0,
  tasks: [taskState()],
  courseMeta: {
    courseVersion: 'offline-course-2',
    glossaryVersion: 'glossary-2',
    checksVersion: 'learning-checks-2',
    courseExtensionVersion: null,
    manifestSha256: 'b'.repeat(64),
    case: '设备运维',
    businessQuestion: '哪些设备存在未闭环高危告警？',
    firstTask: 'business-ontology',
  },
  glossary: [
    {
      term: 'IRI / 稳定身份',
      aliases: ['主键'],
      plain: '全局唯一标识',
      example: 'urn:example:1',
      technical: 'IRI',
      boundary: '与业务主键不同。',
    },
  ],
})

const startResult = (): Row => ({
  learningAttemptStartVersion: 1,
  projectId,
  operationId,
  taskId: 'business-ontology',
  attemptId: id(9),
  activationEpoch: 1,
  recordVersion: 1,
  inputVersion: 'rev-2:' + snapshot,
  rootSnapshotRef: snapshot,
  operationSequence: 3,
  afterCheckpointRef: 'c'.repeat(64),
  replayed: false,
  learningState: taskState(),
})

const hintResult = (): Row => ({
  learningHintRecordVersion: 1,
  projectId,
  operationId,
  taskId: 'business-ontology',
  attemptId: id(9),
  recordVersion: 2,
  assistanceEventId: id(11),
  level: 1,
  revealedHint: { level: 1, kind: 'concept', text: '先问：哪台设备有未闭环高危告警？' },
  record: {
    attemptId: id(9),
    recordVersion: 2,
    course: 'offline-course-2',
    task: 'business-ontology',
    activationEpoch: 1,
    assistance: 'partial-hints',
    maxHintLevel: 1,
    operationComplete: false,
    independentTransferSuccess: false,
    checkStatus: 'not-checked',
    guidedStageCheckpointRef: null,
  },
  learningState: taskState(),
})

const observationResult = (): Row => ({
  learningObservationRecordVersion: 1,
  projectId,
  operationId,
  taskId: 'business-ontology',
  attemptId: id(9),
  recordVersion: 2,
  observation: { kind: 'reading-opened', readingId: 'business-question' },
  assessmentOutcome: null,
  learningState: taskState(),
})

const checkResult = (): Row => ({
  learningTaskCheckVersion: 1,
  projectId,
  operationId,
  taskId: 'business-ontology',
  attemptId: id(9),
  recordVersion: 3,
  inputVersion: 'rev-2:' + snapshot,
  checkStatus: 'passed',
  operationComplete: true,
  independentTransferSuccess: false,
  assistance: 'partial-hints',
  feedback: {
    status: 'passed',
    completed: ['ontology-model'],
    repairs: [],
    suggestions: ['按当前输入版本查看完整实际结果。'],
    knowledgePoints: ['类与个体'],
    evidenceIds: [snapshot],
  },
  evidenceIds: [snapshot],
  guidedStageCheckpointRef: 'd'.repeat(64),
  operationSequence: 5,
  afterCheckpointRef: 'd'.repeat(64),
  learningState: taskState(),
})

const params = {
  'project.learning.read': { projectId },
  'project.learning.attempt.start': { projectId, operationId, taskId: 'business-ontology' },
  'project.learning.hint.record': {
    projectId,
    operationId,
    taskId: 'business-ontology',
    level: 1,
  },
  'project.learning.observation.record': {
    projectId,
    operationId,
    taskId: 'business-ontology',
    observation: { kind: 'reading-opened', readingId: 'business-question' },
  },
  'project.learning.task.check': { projectId, operationId, taskId: 'business-ontology' },
} as Record<string, Row>

const results = {
  'project.learning.read': readResult,
  'project.learning.attempt.start': startResult,
  'project.learning.hint.record': hintResult,
  'project.learning.observation.record': observationResult,
  'project.learning.task.check': checkResult,
} as Record<string, () => Row>

describe('L1 learning ledger v2 contract', () => {
  it('registers the five methods on the business3 profile and the named bridge', () => {
    const profile = v2Registry.foundationProfiles.business3
    const defs = schema.$defs as Record<string, unknown>
    for (const method of LEARNING_METHODS) {
      expect(profile.methods).toContain(method)
      expect(profile.mainlineProjectMethods).toContain(method)
      expect(profile.newSourceOrLearningMethods).toContain(method)
      expect(v2Registry.projectLearning.methods).toContain(method)
      expect(v2Registry.projectLearning.agentEligible).toBe(false)
      expect(v2Registry.projectLearning.exposure).toBe('business-named-bridge-only')
      expect(defs['params_' + method]).toBeDefined()
      expect(defs['result_' + method]).toBeDefined()
    }
  })

  for (const method of LEARNING_METHODS) {
    it(`schema: request and response ${method}`, () => {
      const request = {
        kind: 'request',
        protocolVersion: 3,
        id: id(20),
        engineSessionId: id(2),
        method,
        params: structuredClone(params[method]),
      }
      expect(validateBusiness3('request', request)).toBe(true)
      const downgraded = structuredClone(request)
      downgraded.protocolVersion = 2
      expect(validateBusiness3('request', downgraded)).toBe(false)
      const response = {
        kind: 'response',
        protocolVersion: 3,
        id: id(20),
        engineSessionId: id(2),
        method,
        ok: true,
        result: results[method](),
      }
      expect(validateBusiness3('response', response)).toBe(true)
      const forged = structuredClone(response)
      forged.result = { ...forged.result, extra: true }
      expect(validateBusiness3('response', forged)).toBe(false)
      expect(matchesBusiness3Response(request, response, registryHash)).toBe(true)
      expect(
        matchesBusiness3Response(request, { ...response, engineSessionId: id(21) }, registryHash),
      ).toBe(false)
      expect(
        matchesBusiness3Response(
          request,
          {
            ...response,
            ok: false,
            error: {
              code: 'INVALID_STATE',
              messageKey: 'engine.invalidState',
              retryable: false,
              params: {},
            },
            result: undefined,
          },
          registryHash,
        ),
      ).toBe(false)
    })
  }

  it('binds mutation results to their echoed operation, task, level and observation', () => {
    const session = id(2)
    const base = (method: string) => ({
      kind: 'request' as const,
      protocolVersion: 3,
      id: id(20),
      engineSessionId: session,
      method,
      params: structuredClone(params[method]),
    })
    const reply = (method: string, result: Row) => ({
      kind: 'response' as const,
      protocolVersion: 3,
      id: id(20),
      engineSessionId: session,
      method,
      ok: true as const,
      result,
    })
    const swapped = hintResult()
    swapped.level = 2
    expect(
      matchesBusiness3Response(
        base('project.learning.hint.record'),
        reply('project.learning.hint.record', swapped),
        registryHash,
      ),
    ).toBe(false)
    const otherTask = startResult()
    otherTask.taskId = 'mapping'
    expect(
      matchesBusiness3Response(
        base('project.learning.attempt.start'),
        reply('project.learning.attempt.start', otherTask),
        registryHash,
      ),
    ).toBe(false)
    const otherObservation = observationResult()
    otherObservation.observation = { kind: 'reading-opened', readingId: 'other' }
    expect(
      matchesBusiness3Response(
        base('project.learning.observation.record'),
        reply('project.learning.observation.record', otherObservation),
        registryHash,
      ),
    ).toBe(false)
    const foreign = readResult()
    foreign.projectId = id(22)
    expect(
      matchesBusiness3Response(
        base('project.learning.read'),
        reply('project.learning.read', foreign),
        registryHash,
      ),
    ).toBe(false)
  })
})

class MemoryChild extends EventEmitter {
  stdout = new PassThrough()
  stderr = new PassThrough()
  stdin: Writable
  calls: Row[] = []
  selectedProject: string | null = null
  learningError: Row | null = null
  constructor(readonly session: string) {
    super()
    this.stdin = new Writable({
      write: (bytes, _encoding, done) => {
        const q = JSON.parse(bytes.toString()) as Row
        this.calls.push(q)
        queueMicrotask(() => this.stdout.write(this.frame(q)))
        done()
      },
    })
  }
  private frame(q: Row): string {
    let result: unknown
    let error: unknown
    if (q.method === 'hello')
      result = {
        selectedVersion: 3,
        engineVersion: '0.1.0',
        engineSessionId: this.session,
        capabilities: [
          'health',
          'session.ping',
          'project.get',
          'project.catalog',
          'project.create',
          'project.open',
          'project.read',
          ...LEARNING_METHODS,
        ],
        registryHash,
        limits,
      }
    else if (q.method === 'session.ping') result = { nonce: (q.params as Row).nonce }
    else if (q.method === 'project.open') {
      this.selectedProject = String((q.params as Row).projectId)
      result = {
        projectId: this.selectedProject,
        projectRevision: 2,
        inputSnapshotId: snapshot,
        dependencyVector: { 'facts:asserted': 1 },
        formatVersion: 3,
      }
    } else if (String(q.method).startsWith('project.learning.')) {
      const method = String(q.method)
      if (this.learningError) error = this.learningError
      else result = { ...results[method](), ...(q.params as Row as Row) }
    } else result = { status: 'ok', engineVersion: '0.1.0' }
    // The scripted engine echoes request params so the service echo checks pass.
    if (result && typeof result === 'object' && !Array.isArray(result)) {
      const params = q.params as Row
      const merged = result as Row
      for (const key of ['projectId', 'operationId', 'taskId', 'level', 'observation'])
        if (key in params && key in merged) merged[key] = params[key]
    }
    return (
      JSON.stringify({
        kind: 'response',
        protocolVersion: q.method === 'hello' ? 2 : 3,
        engineSessionId: this.session,
        id: q.id,
        method: q.method,
        ok: !error,
        ...(error ? { error } : { result }),
      }) + '\n'
    )
  }
  kill(): boolean {
    queueMicrotask(() => this.emit('close', 0))
    return true
  }
}

async function setupService() {
  const child = new MemoryChild(id(2))
  processDouble.spawn.mockReset().mockImplementationOnce(() => {
    queueMicrotask(() => child.emit('spawn'))
    return child
  })
  const supervisor = new EngineSupervisor(
    { packaged: false, appPath: '/memory/desktop', resourcesPath: '/memory/resources' },
    {
      profile: 'business3',
      registryPath,
      command: { command: '/memory/engine', args: [] },
      requestMs: 1000,
    },
  )
  const tasks = new TaskService(supervisor)
  const service = new ProjectMainlineService(supervisor, tasks, vi.fn())
  const replies = supervisor.mainlineReplyReceiver()
  const receive = async <T>(work: () => Promise<BridgeResult<T>>): Promise<BridgeResult<T>> => {
    const delivered = await replies.receive(work)
    replies.consume(delivered.receipt)
    return delivered.value
  }
  return {
    child,
    service,
    receive,
    close: () => {
      service.dispose()
      tasks.dispose()
      supervisor.stop()
    },
  }
}

describe('L1 MainlineProjectService learning bridge', () => {
  it('routes the five named methods with validated params and results', async () => {
    const h = await setupService()
    try {
      const opened = await h.receive(() => h.service.openProject({ projectId }))
      expect(opened.ok).toBe(true)
      const readValue = await h.receive(() => h.service.getProjectLearningState({ projectId }))
      if (!readValue.ok) console.log('READ RESULT', JSON.stringify(readValue).slice(0, 400))
      expect(readValue.ok).toBe(true)
      expect(
        (
          await h.receive(() =>
            h.service.startLearningAttempt({
              projectId,
              operationId,
              taskId: 'business-ontology',
            }),
          )
        ).ok,
      ).toBe(true)
      expect(
        (
          await h.receive(() =>
            h.service.recordLearningHint({
              projectId,
              operationId,
              taskId: 'business-ontology',
              level: 1,
            }),
          )
        ).ok,
      ).toBe(true)
      expect(
        (
          await h.receive(() =>
            h.service.recordLearningObservation({
              projectId,
              operationId,
              taskId: 'business-ontology',
              observation: { kind: 'reading-opened', readingId: 'business-question' },
            }),
          )
        ).ok,
      ).toBe(true)
      expect(
        (
          await h.receive(() =>
            h.service.checkLearningTask({ projectId, operationId, taskId: 'business-ontology' }),
          )
        ).ok,
      ).toBe(true)
      const called = h.child.calls
        .filter((c) => String(c.method).startsWith('project.learning.'))
        .map((c) => String(c.method))
      expect(called).toEqual([...LEARNING_METHODS])
      for (const call of h.child.calls.filter((c) =>
        String(c.method).startsWith('project.learning.'),
      ))
        expect((call.params as Row).projectId).toBe(projectId)
    } finally {
      h.close()
    }
  })

  it('denies learning calls without a selected project and rejects forged results', async () => {
    const h = await setupService()
    try {
      const unselected = await h.service.getProjectLearningState({ projectId })
      expect(unselected.ok).toBe(false)
      expect((await h.receive(() => h.service.openProject({ projectId }))).ok).toBe(true)
      h.child.learningError = {
        code: 'INVALID_STATE',
        messageKey: 'protocol.invalidState',
        retryable: false,
        params: {},
      }
      const failed = await h.receive(() =>
        h.service.checkLearningTask({ projectId, operationId, taskId: 'business-ontology' }),
      )
      expect(failed.ok).toBe(false)
    } finally {
      h.close()
    }
  })

  it('rejects learning calls whose projectId disagrees with the selected project', async () => {
    const h = await setupService()
    try {
      expect((await h.receive(() => h.service.openProject({ projectId }))).ok).toBe(true)
      const callsBefore = h.child.calls.length
      const mismatch = await h.receive(() =>
        h.service.checkLearningTask({
          projectId: id(99),
          operationId,
          taskId: 'business-ontology',
        }),
      )
      expect(mismatch.ok).toBe(false)
      if (!mismatch.ok) expect(mismatch.error.code).toBe('INVALID_STATE')
      expect(h.child.calls.length).toBe(callsBefore)
    } finally {
      h.close()
    }
  })
})

const electron = vi.hoisted(() => ({ bridge: undefined as unknown, invoke: vi.fn() }))
vi.mock('electron', () => ({
  contextBridge: {
    exposeInMainWorld: (_name: string, value: unknown) => {
      electron.bridge = value
    },
  },
  ipcRenderer: { invoke: electron.invoke, on: vi.fn(), removeListener: vi.fn() },
}))

describe('L1 learning desktop IPC and preload named channels', () => {
  type Handler = (event: unknown, ...args: unknown[]) => Promise<unknown>
  const registerHandlers = (blocked: boolean) => {
    const handlers = new Map<string, Handler>()
    const learning = vi.fn(async () => ({ ok: true, data: readResult() }))
    const bindings = new WeakMap<object, string | undefined>()
    const replies = {
      receive: vi.fn(async (work: () => Promise<unknown>) => {
        const value = await work()
        const receipt = {}
        bindings.set(receipt, id(2))
        return { value, receipt }
      }),
      binding: (receipt: object) => ({ engineSessionId: bindings.get(receipt) }),
      consume: vi.fn(),
    }
    registerDesktopIpc({
      ipcMain: {
        handle: (name: string, handler: Handler) => {
          handlers.set(name, handler)
        },
      } as never,
      trusted: () => true,
      tasks: {} as never,
      supervisor: {
        get engineSessionId() {
          return id(2)
        },
      } as never,
      projects: {
        getProjectLearningState: learning,
        startLearningAttempt: learning,
        recordLearningHint: learning,
        recordLearningObservation: learning,
        checkLearningTask: learning,
        queries: {},
        managementBlocked: blocked,
        restoreBlocked: false,
      } as never,
      replies,
      library: undefined,
    } as never)
    return { handlers, learning }
  }
  const event = () => ({ sender: {}, senderFrame: {} })

  it('registers the five learning channels and forwards renderer args', async () => {
    const { handlers, learning } = registerHandlers(false)
    for (const channel of [
      'project:learning-read',
      'project:learning-attempt-start',
      'project:learning-hint-record',
      'project:learning-observation-record',
      'project:learning-task-check',
    ])
      expect(handlers.has(channel)).toBe(true)
    await handlers.get('project:learning-read')!(event(), { projectId })
    expect(learning).toHaveBeenCalledWith({ projectId })
  })

  it('blocks the four learning mutation routes while a restore is unresolved', async () => {
    const { handlers, learning } = registerHandlers(true)
    for (const channel of [
      'project:learning-attempt-start',
      'project:learning-hint-record',
      'project:learning-observation-record',
      'project:learning-task-check',
    ]) {
      const value = (await handlers.get(channel)!(event(), { projectId })) as Row
      expect(value.ok).toBe(false)
      expect((value.error as Row).code).toBe('PERMISSION_DENIED')
    }
    expect(learning).not.toHaveBeenCalled()
  })

  it('exposes the named preload bridge bound to the learning channels', async () => {
    vi.resetModules()
    electron.invoke.mockReset()
    electron.invoke.mockResolvedValue({ ok: true, data: null })
    await import('../../apps/desktop/src/preload/index')
    const bridge = electron.bridge as Row
    expect(typeof bridge.getProjectLearningState).toBe('function')
    expect(typeof bridge.startLearningAttempt).toBe('function')
    expect(typeof bridge.recordLearningHint).toBe('function')
    expect(typeof bridge.recordLearningObservation).toBe('function')
    expect(typeof bridge.checkLearningTask).toBe('function')
    await (bridge.getProjectLearningState as (args: Row) => Promise<unknown>)({ projectId })
    const channel = electron.invoke.mock.calls[0]?.[0]
    expect(channel).toBe('project:learning-read')
    electron.invoke.mockClear()
    await (bridge.checkLearningTask as (args: Row) => Promise<unknown>)({
      projectId,
      operationId,
      taskId: 'business-ontology',
    })
    expect(electron.invoke.mock.calls[0]?.[0]).toBe('project:learning-task-check')
    expect(randomUUID()).toMatch(/^[0-9a-f-]{36}$/)
  })
})
