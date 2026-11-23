/** L1 Step 2 mentor controller unit coverage: derived stale projection, hint
 *  level progression, status/assistance text mapping, response fencing and the
 *  zero-browser-storage rule. No OS engine process is spawned. */
import { describe, expect, it, vi } from 'vitest'
import type {
  BridgeResult,
  LearningLedgerBridge,
  LearningTaskStateDTO,
  ProjectLearningHintRecordDTO,
  ProjectLearningReadDTO,
  ProjectLearningTaskCheckDTO,
  ProjectLearningTaskCheckDTO as CheckDTO,
} from '@ontolearn/contracts'
import {
  EXECUTED_CHECK_STATUSES,
  LearningController,
  deriveTaskStale,
  displayedCheckStatus,
  mentorAssistanceText,
  mentorStatusText,
} from '../../apps/desktop/src/renderer/src/learning/learning-controller'

const projectId = '00000000-0000-4000-8000-000000000001'
const otherProjectId = '00000000-0000-4000-8000-000000000002'

function taskState(overrides: Partial<LearningTaskStateDTO> = {}): LearningTaskStateDTO {
  return {
    taskId: 'business-ontology',
    module: '本体构建',
    goal: '把业务问题变成概念、属性、个体与关系。',
    instructions: '独立还原 G-base。',
    steps: [],
    completionCondition: '实际批准工具的当前版本完整结果与固定预期一致。',
    commonErrors: ['把类当个体：检查rdf:type两端。'],
    knowledgePoints: ['本体构建'],
    transfer: false,
    next: 'mapping',
    checks: ['ontology-model'],
    readings: [
      {
        id: 'business-question',
        title: '业务问题与能力问题',
        sourceRef: 'content/learning/course.json',
        optional: false,
        summary: '区分业务问题与能力问题。',
        content: '业务问题提出关注点；能力问题可被模型直接回答并核对。',
        selfAssessment: [
          {
            question: '哪一句是能力问题？',
            options: [
              { id: 'a', text: '选项甲' },
              { id: 'b', text: '选项乙' },
            ],
          },
        ],
      },
    ],
    attemptCount: 1,
    withdrawnAttemptCount: 0,
    attemptId: 'attempt-1',
    attemptActivationEpoch: 1,
    recordVersion: 1,
    assistance: 'independent',
    maxHintLevel: 0,
    revealedHints: [],
    operationComplete: false,
    independentTransferSuccess: false,
    checkStatus: 'not-checked',
    staleInput: false,
    lastFeedback: null,
    observations: { openedReadingIds: [], answeredAssessments: [] },
    completedGuidedStages: [],
    guidedStageCheckpointRef: null,
    rootSnapshotRef: 'a'.repeat(64),
    boundSnapshotRef: null,
    boundDomainRevision: null,
    inputVersion: 'rev-0:' + 'a'.repeat(64),
    ...overrides,
  }
}

function learningRead(
  tasks: LearningTaskStateDTO[],
  refinements: Partial<ProjectLearningReadDTO> = {},
): ProjectLearningReadDTO {
  return {
    learningReadVersion: 1,
    projectId,
    domainRevision: 0,
    domainSnapshotRef: 'a'.repeat(64),
    inputVersion: 'rev-0:' + 'a'.repeat(64),
    templateRef: null,
    withdrawnAttemptCount: 0,
    tasks,
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
    glossary: [],
    ...refinements,
  }
}

function hintReceipt(
  level: 1 | 2 | 3 | 4,
  learningState: LearningTaskStateDTO,
): ProjectLearningHintRecordDTO {
  return {
    learningHintRecordVersion: 1,
    projectId,
    operationId: 'op-hint',
    taskId: learningState.taskId,
    attemptId: learningState.attemptId ?? 'attempt-1',
    recordVersion: (learningState.recordVersion ?? 0) + 1,
    assistanceEventId: 'event-1',
    level,
    revealedHint: { level, kind: 'concept', text: `第 ${level} 级提示文本` },
    record: {
      attemptId: learningState.attemptId ?? 'attempt-1',
      recordVersion: (learningState.recordVersion ?? 0) + 1,
      course: 'offline-course-2',
      task: learningState.taskId,
      activationEpoch: 1,
      assistance: level === 4 ? 'full-demonstration' : 'partial-hints',
      maxHintLevel: level,
      operationComplete: false,
      independentTransferSuccess: false,
      checkStatus: learningState.checkStatus,
      guidedStageCheckpointRef: null,
    },
    learningState,
  }
}

function checkReceipt(
  learningState: LearningTaskStateDTO,
  refinements: Partial<CheckDTO> = {},
): ProjectLearningTaskCheckDTO {
  return {
    learningTaskCheckVersion: 1,
    projectId,
    operationId: 'op-check',
    taskId: learningState.taskId,
    attemptId: learningState.attemptId ?? 'attempt-1',
    recordVersion: (learningState.recordVersion ?? 0) + 1,
    inputVersion: learningState.inputVersion,
    checkStatus: learningState.checkStatus,
    operationComplete: learningState.operationComplete,
    independentTransferSuccess: learningState.independentTransferSuccess,
    assistance: learningState.assistance,
    feedback: learningState.lastFeedback,
    evidenceIds: learningState.lastFeedback?.evidenceIds ?? [],
    guidedStageCheckpointRef: learningState.guidedStageCheckpointRef,
    operationSequence: 3,
    afterCheckpointRef: 'c'.repeat(64),
    learningState,
    ...refinements,
  }
}

type ScriptedBridge = LearningLedgerBridge & {
  reads: number
  hints: Array<{ taskId: string; level: number }>
  checks: number
  observations: unknown[]
  attempts: number
}

function scriptedBridge(initial: ProjectLearningReadDTO): ScriptedBridge {
  let current = initial
  const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
  const bridge: ScriptedBridge = {
    reads: 0,
    hints: [],
    checks: 0,
    observations: [],
    attempts: 0,
    getProjectLearningState: async () => {
      bridge.reads++
      return ok(structuredClone(current))
    },
    startLearningAttempt: async () => {
      bridge.attempts++
      return ok({
        learningAttemptStartVersion: 1,
        projectId,
        operationId: 'op-attempt',
        taskId: 'business-ontology',
        attemptId: 'attempt-2',
        activationEpoch: 2,
        recordVersion: 2,
        inputVersion: current.tasks[0]!.inputVersion,
        rootSnapshotRef: 'a'.repeat(64),
        operationSequence: null,
        afterCheckpointRef: null,
        replayed: false,
        learningState: structuredClone(current.tasks[0]!),
      })
    },
    recordLearningHint: async ({ level }) => {
      bridge.hints.push({ taskId: 'business-ontology', level })
      const previous = current.tasks[0]!
      const revealed = Array.from({ length: level }, (_, index) => ({
        level: (index + 1) as 1 | 2 | 3 | 4,
        kind: 'concept',
        text: `第 ${index + 1} 级提示文本`,
      }))
      const learningState: LearningTaskStateDTO = {
        ...previous,
        recordVersion: (previous.recordVersion ?? 0) + 1,
        maxHintLevel: level,
        assistance: level === 4 ? 'full-demonstration' : 'partial-hints',
        revealedHints: revealed,
      }
      current = {
        ...current,
        tasks: current.tasks.map((task, index) => (index === 0 ? learningState : task)),
      }
      return ok(hintReceipt(level, learningState))
    },
    recordLearningObservation: async (args) => {
      bridge.observations.push(args.observation)
      const previous = current.tasks[0]!
      const openedReadingIds = [...previous.observations.openedReadingIds]
      const answered = [...previous.observations.answeredAssessments]
      if (args.observation.kind === 'reading-opened') {
        if (!openedReadingIds.includes(args.observation.readingId))
          openedReadingIds.push(args.observation.readingId)
      } else
        answered.push({
          readingId: args.observation.readingId,
          questionIndex: args.observation.questionIndex,
          selectedOptionId: args.observation.selectedOptionId,
          correct: args.observation.selectedOptionId === 'a',
        })
      const learningState: LearningTaskStateDTO = {
        ...previous,
        recordVersion: (previous.recordVersion ?? 0) + 1,
        observations: { openedReadingIds, answeredAssessments: answered },
      }
      current = {
        ...current,
        tasks: current.tasks.map((task, index) => (index === 0 ? learningState : task)),
      }
      return ok({
        learningObservationRecordVersion: 1,
        projectId,
        operationId: 'op-observation',
        taskId: args.taskId,
        attemptId: previous.attemptId ?? 'attempt-1',
        recordVersion: learningState.recordVersion ?? 1,
        observation: args.observation,
        assessmentOutcome:
          args.observation.kind === 'self-assessment-answered'
            ? {
                correct: args.observation.selectedOptionId === 'a',
                explanation: '能力问题可核对。',
              }
            : null,
        learningState,
      })
    },
    checkLearningTask: async () => {
      bridge.checks++
      const previous = current.tasks[0]!
      const learningState: LearningTaskStateDTO = {
        ...previous,
        recordVersion: (previous.recordVersion ?? 0) + 1,
        checkStatus: 'passed',
        operationComplete: true,
        guidedStageCheckpointRef: 'd'.repeat(64),
        completedGuidedStages: ['business-ontology'],
        lastFeedback: {
          status: 'passed',
          completed: ['ontology-model'],
          repairs: [],
          suggestions: [],
          knowledgePoints: ['本体构建'],
          evidenceIds: ['e'.repeat(64)],
        },
      }
      current = {
        ...current,
        tasks: current.tasks.map((task, index) => (index === 0 ? learningState : task)),
      }
      return ok(checkReceipt(learningState))
    },
  }
  return bridge
}

describe('L1 mentor status and assistance text mapping', () => {
  it('maps every persisted status to the exact non-colour Chinese text', () => {
    expect(mentorStatusText(undefined)).toBe('待检查')
    expect(mentorStatusText(taskState({ checkStatus: 'not-checked' }))).toBe('待检查')
    expect(mentorStatusText(taskState({ checkStatus: 'passed' }))).toBe('已通过')
    expect(mentorStatusText(taskState({ checkStatus: 'needs-repair' }))).toBe('需要修复')
    expect(mentorStatusText(taskState({ checkStatus: 'stale' }))).toBe('已过期 / 需重跑')
    expect(mentorStatusText(taskState({ checkStatus: 'pending-dependency' }))).toBe('依赖未就绪')
    for (const status of ['failed', 'tool-not-successful', 'missing-evidence', 'rerun-required'])
      expect(
        mentorStatusText(taskState({ checkStatus: status as LearningTaskStateDTO['checkStatus'] })),
      ).toBe('检查失败 / 已取消')
  })
  it('maps assistance attribution labels exactly and hides them before any check', () => {
    expect(mentorAssistanceText(taskState({ assistance: 'independent' }))).toBeUndefined()
    // A needs-repair check without assistance stays unlabeled too.
    expect(
      mentorAssistanceText(taskState({ checkStatus: 'needs-repair', assistance: 'independent' })),
    ).toBeUndefined()
    const executed = {
      checkStatus: 'passed',
      operationComplete: true,
    } as Partial<LearningTaskStateDTO>
    expect(mentorAssistanceText(taskState({ ...executed, assistance: 'independent' }))).toBe(
      '独立完成',
    )
    expect(mentorAssistanceText(taskState({ ...executed, assistance: 'partial-hints' }))).toBe(
      '使用部分提示完成',
    )
    expect(mentorAssistanceText(taskState({ ...executed, assistance: 'full-demonstration' }))).toBe(
      '使用完整示范完成',
    )
    expect(
      mentorAssistanceText(taskState({ ...executed, assistance: 'agent-full-assistance' })),
    ).toBe('Agent 完整协助')
  })
})

describe('L1 mentor derived stale projection', () => {
  const ref = 'a'.repeat(64)
  const next = 'f'.repeat(64)
  it('derives stale only for executed checks after the workspace snapshot advanced', () => {
    for (const status of EXECUTED_CHECK_STATUSES)
      expect(
        deriveTaskStale(
          taskState({ checkStatus: status as LearningTaskStateDTO['checkStatus'] }),
          next,
          ref,
        ),
      ).toBe(true)
    expect(deriveTaskStale(taskState({ checkStatus: 'not-checked' }), next, ref)).toBe(false)
    expect(deriveTaskStale(taskState({ checkStatus: 'pending-dependency' }), next, ref)).toBe(false)
    expect(deriveTaskStale(taskState({ checkStatus: 'passed' }), ref, ref)).toBe(false)
    expect(deriveTaskStale(taskState({ checkStatus: 'passed' }), undefined, ref)).toBe(false)
    expect(deriveTaskStale(undefined, next, ref)).toBe(false)
  })
  it('binds the comparison to the check receipt snapshot, not the open-time read', () => {
    // The check ran after a commit: its own binding is current even though the
    // project-open learning read named an older snapshot.
    expect(
      deriveTaskStale(taskState({ checkStatus: 'passed', boundSnapshotRef: next }), next, ref),
    ).toBe(false)
    // The receipt's binding is the authority: an old read snapshot cannot
    // force a fresh check result to look stale.
    expect(
      deriveTaskStale(
        taskState({ checkStatus: 'needs-repair', boundSnapshotRef: next }),
        next,
        ref,
      ),
    ).toBe(false)
    expect(
      deriveTaskStale(taskState({ checkStatus: 'passed', boundSnapshotRef: ref }), next, ref),
    ).toBe(true)
  })
  it('displays the rerun-required text for a derived stale result', () => {
    expect(displayedCheckStatus(taskState({ checkStatus: 'passed' }), next, ref)).toBe(
      '已过期 / 需重跑',
    )
    expect(displayedCheckStatus(taskState({ checkStatus: 'passed' }), ref, ref)).toBe('已通过')
    expect(displayedCheckStatus(undefined, next, ref)).toBe('待检查')
  })
})

describe('LearningController', () => {
  it('select resets state without any background read', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    const controller = new LearningController(bridge, () => 'op-1')
    controller.select(projectId)
    expect(bridge.reads).toBe(0)
    expect(controller.getSnapshot().learning).toBeUndefined()
    await controller.selectAndRefresh(projectId)
    expect(bridge.reads).toBe(1)
    expect(controller.getSnapshot().learning?.projectId).toBe(projectId)
    controller.select(undefined)
    expect(controller.getSnapshot().learning).toBeUndefined()
    expect(bridge.reads).toBe(1)
  })
  it('requests the next hint level, caps at three and never reveals without persistence', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    const controller = new LearningController(bridge, () => 'op-hint')
    await controller.selectAndRefresh(projectId)
    await controller.requestHint()
    expect(bridge.hints).toEqual([{ taskId: 'business-ontology', level: 1 }])
    expect(controller.getSnapshot().learning?.tasks[0]?.maxHintLevel).toBe(1)
    expect(controller.getSnapshot().learning?.tasks[0]?.revealedHints).toHaveLength(1)
    // Two more unlocks reach level three.
    await controller.requestHint()
    await controller.requestHint()
    expect(bridge.hints.map((hint) => hint.level)).toEqual([1, 2, 3])
    expect(
      controller.getSnapshot().learning?.tasks[0]?.revealedHints.map((hint) => hint.level),
    ).toEqual([1, 2, 3])
    // At level three no further RPC is made; the notice points to the demonstration.
    await controller.requestHint()
    expect(bridge.hints).toHaveLength(3)
    expect(controller.getSnapshot().notice).toContain('查看示范')
  })
  it('unlocks the level-4 demonstration only through a persisted assistance event', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    const controller = new LearningController(bridge, () => 'op-demo')
    await controller.selectAndRefresh(projectId)
    await controller.requestDemonstration()
    expect(bridge.hints).toEqual([{ taskId: 'business-ontology', level: 4 }])
    const task = controller.getSnapshot().learning?.tasks[0]
    expect(task?.assistance).toBe('full-demonstration')
    expect(task?.revealedHints.map((hint) => hint.level)).toEqual([1, 2, 3, 4])
    expect(mentorAssistanceText(task)).toBe('使用完整示范完成')
  })
  it('records reading and self-assessment observations without changing completion', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    const controller = new LearningController(bridge, () => 'op-obs')
    await controller.selectAndRefresh(projectId)
    await controller.recordObservation({ kind: 'reading-opened', readingId: 'business-question' })
    expect(controller.getSnapshot().learning?.tasks[0]?.observations.openedReadingIds).toEqual([
      'business-question',
    ])
    await controller.recordObservation({
      kind: 'self-assessment-answered',
      readingId: 'business-question',
      questionIndex: 0,
      selectedOptionId: 'a',
    })
    const outcome = controller.getSnapshot().lastAssessment
    expect(outcome).toMatchObject({ correct: true, explanation: '能力问题可核对。' })
    const task = controller.getSnapshot().learning?.tasks[0]
    expect(task?.checkStatus).toBe('not-checked')
    expect(task?.operationComplete).toBe(false)
    expect(deriveTaskStale(task, 'a'.repeat(64), 'a'.repeat(64))).toBe(false)
  })
  it('returns the check receipt, merges state and exposes the guided checkpoint ref', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    const controller = new LearningController(bridge, () => 'op-check')
    await controller.selectAndRefresh(projectId)
    const receipt = await controller.checkTask()
    expect(receipt?.checkStatus).toBe('passed')
    expect(receipt?.guidedStageCheckpointRef).toBe('d'.repeat(64))
    const task = controller.getSnapshot().learning?.tasks[0]
    expect(task?.operationComplete).toBe(true)
    expect(mentorStatusText(task)).toBe('已通过')
    expect(mentorAssistanceText(task)).toBe('独立完成')
  })
  it('ignores replies that no longer match the selected project', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    let release!: (value: BridgeResult<ProjectLearningTaskCheckDTO>) => void
    bridge.checkLearningTask = () =>
      new Promise((done) => {
        release = done
      })
    const controller = new LearningController(bridge, () => 'op-x')
    await controller.selectAndRefresh(projectId)
    const pending = controller.checkTask()
    // The selection moves on while the original reply is still in flight.
    controller.select(otherProjectId)
    release({
      ok: true,
      data: checkReceipt(taskState({ checkStatus: 'passed', operationComplete: true })),
    })
    expect(await pending).toBeUndefined()
    expect(controller.getSnapshot().learning).toBeUndefined()
    expect(controller.getSnapshot().lastCheck).toBeUndefined()
    // The scripted read still names the original project; that reply cannot
    // become the learning state of the newly selected one.
    await controller.selectAndRefresh(otherProjectId)
    expect(bridge.reads).toBe(2)
    expect(controller.getSnapshot().learning).toBeUndefined()
    expect(controller.getSnapshot().error).toBeDefined()
  })
  it('rejects mutation responses naming another project or task without merging state', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    bridge.recordLearningHint = async () => ({
      ok: true,
      data: {
        ...hintReceipt(1, taskState({ maxHintLevel: 1, assistance: 'partial-hints' })),
        projectId: otherProjectId,
      },
    })
    bridge.checkLearningTask = async () => ({
      ok: true,
      data: checkReceipt(taskState({ checkStatus: 'passed', operationComplete: true }), {
        taskId: 'mapping',
      }),
    })
    bridge.startLearningAttempt = async () => ({
      ok: true,
      data: {
        learningAttemptStartVersion: 1,
        projectId: otherProjectId,
        operationId: 'op-attempt',
        taskId: 'business-ontology',
        attemptId: 'attempt-2',
        activationEpoch: 2,
        recordVersion: 2,
        inputVersion: 'rev-0:' + 'a'.repeat(64),
        rootSnapshotRef: 'a'.repeat(64),
        operationSequence: null,
        afterCheckpointRef: null,
        replayed: false,
        learningState: taskState(),
      },
    })
    bridge.recordLearningObservation = async (args) => ({
      ok: true,
      data: {
        learningObservationRecordVersion: 1,
        projectId: otherProjectId,
        operationId: 'op-observation',
        taskId: args.taskId,
        attemptId: 'attempt-1',
        recordVersion: 2,
        observation: args.observation,
        assessmentOutcome: null,
        learningState: taskState(),
      },
    })
    const controller = new LearningController(bridge, () => 'op-z')
    await controller.selectAndRefresh(projectId)
    await controller.requestHint()
    expect(controller.getSnapshot().error).toBeDefined()
    expect(controller.getSnapshot().learning?.tasks[0]?.maxHintLevel).toBe(0)
    await controller.checkTask()
    expect(controller.getSnapshot().error).toBeDefined()
    expect(controller.getSnapshot().lastCheck).toBeUndefined()
    await controller.restartAttempt()
    expect(controller.getSnapshot().error).toBeDefined()
    await controller.recordObservation({ kind: 'reading-opened', readingId: 'business-question' })
    expect(controller.getSnapshot().error).toBeDefined()
  })
  it('queues and drains selectAndRefresh when called while another learning RPC is busy', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    let releaseHint!: (value: BridgeResult<ProjectLearningHintRecordDTO>) => void
    bridge.recordLearningHint = () =>
      new Promise((done) => {
        releaseHint = done
      })
    bridge.getProjectLearningState = async (args) => {
      bridge.reads++
      return {
        ok: true,
        data: learningRead([taskState({ taskId: 'business-ontology' })], {
          projectId: args.projectId,
        }),
      }
    }
    const controller = new LearningController(bridge, () => 'op-queue')
    await controller.selectAndRefresh(projectId)
    const inFlightHint = controller.requestHint()
    const queuedRefresh = controller.selectAndRefresh(otherProjectId)
    expect(controller.getSnapshot().selectedProjectId).toBe(otherProjectId)
    expect(controller.getSnapshot().busy).toBe(true)
    expect(bridge.reads).toBe(1)

    releaseHint({
      ok: true,
      data: hintReceipt(1, taskState({ maxHintLevel: 1, assistance: 'partial-hints' })),
    })
    await Promise.all([inFlightHint, queuedRefresh])
    expect(bridge.reads).toBe(2)
    expect(controller.getSnapshot().busy).toBe(false)
    expect(controller.getSnapshot().learning?.projectId).toBe(otherProjectId)
    expect(controller.getSnapshot().error).toBeUndefined()
  })
  it('notifies subscribers and stops after close', async () => {
    const bridge = scriptedBridge(learningRead([taskState()]))
    const controller = new LearningController(bridge, () => 'op-y')
    const notifications = vi.fn()
    const release = controller.subscribe(notifications)
    await controller.selectAndRefresh(projectId)
    expect(notifications.mock.calls.length).toBeGreaterThan(0)
    release()
    const before = notifications.mock.calls.length
    controller.close()
    await controller.checkTask()
    expect(notifications.mock.calls.length).toBe(before)
    expect(bridge.checks).toBe(0)
  })
})

describe('L1 mentor storage boundary', () => {
  it('never touches localStorage or sessionStorage during any controller flow', async () => {
    const accesses: string[] = []
    const deny = (name: string) => ({
      get() {
        accesses.push(name)
        throw new Error(`${name} access denied by test`)
      },
    })
    Object.defineProperty(globalThis, 'localStorage', {
      ...deny('localStorage'),
      configurable: true,
    })
    Object.defineProperty(globalThis, 'sessionStorage', {
      ...deny('sessionStorage'),
      configurable: true,
    })
    try {
      const bridge = scriptedBridge(learningRead([taskState()]))
      const controller = new LearningController(bridge, () => 'op-storage')
      await controller.selectAndRefresh(projectId)
      await controller.requestHint()
      await controller.requestDemonstration()
      await controller.recordObservation({
        kind: 'self-assessment-answered',
        readingId: 'business-question',
        questionIndex: 0,
        selectedOptionId: 'a',
      })
      await controller.checkTask()
      await controller.restartAttempt()
      expect(accesses).toEqual([])
    } finally {
      Reflect.deleteProperty(globalThis, 'localStorage')
      Reflect.deleteProperty(globalThis, 'sessionStorage')
    }
  })
})
