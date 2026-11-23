/** Lq query-course unit coverage: the cross-workspace snapshot selection and
 *  the mentor panel's G-base reset / query-workspace entries. Static React
 *  markup assertions run in plain node (no jsdom); the real interactive flow
 *  is proven by tests/e2e/lq-query-learning.spec.ts. Zero browser storage. */
import { describe, expect, it, vi } from 'vitest'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import type {
  BridgeResult,
  LearningLedgerBridge,
  LearningTaskStateDTO,
  ProjectLearningReadDTO,
} from '@ontolearn/contracts'
import {
  pickLatestDomainSnapshotId,
  type DomainSnapshotCandidate,
} from '../../apps/desktop/src/renderer/src/learning/domain-snapshot'
import { LearningController } from '../../apps/desktop/src/renderer/src/learning/learning-controller'
import {
  MentorPanel,
  scrollToProjectCheckpoints,
} from '../../apps/desktop/src/renderer/src/learning/MentorPanel'

const projectId = '00000000-0000-4000-8000-0000000000aa'
const otherProjectId = '00000000-0000-4000-8000-0000000000bb'

describe('pickLatestDomainSnapshotId', () => {
  const snap = (suffix: string) => suffix.repeat(64)
  const candidate = (
    id: string,
    revision: number,
    snapshotId: string,
  ): DomainSnapshotCandidate => ({ projectId: id, revision, snapshotId })
  it('returns undefined without an active project or any usable candidate', () => {
    expect(
      pickLatestDomainSnapshotId(undefined, [candidate(projectId, 3, snap('a'))]),
    ).toBeUndefined()
    expect(pickLatestDomainSnapshotId(projectId, [])).toBeUndefined()
    expect(pickLatestDomainSnapshotId(projectId, [undefined])).toBeUndefined()
    expect(
      pickLatestDomainSnapshotId(projectId, [
        { projectId, snapshotId: snap('a') },
        { projectId, revision: 2 },
      ]),
    ).toBeUndefined()
  })
  it('ignores candidates belonging to other projects', () => {
    expect(
      pickLatestDomainSnapshotId(projectId, [candidate(otherProjectId, 9, snap('b'))]),
    ).toBeUndefined()
  })
  it('a committed query revision outranks the older cached ontology snapshot', () => {
    // The ontology workspace last read revision 1; the learner then switched to
    // the query workspace, submitted a managed definition (revision 2) and read
    // it back. The freshest identity is the query read's snapshot, so the old
    // ontology cache cannot falsely project "stale".
    expect(
      pickLatestDomainSnapshotId(projectId, [
        candidate(projectId, 1, snap('a')),
        candidate(projectId, 2, snap('b')),
      ]),
    ).toBe(snap('b'))
    // Symmetrically, a newer ontology commit outranks an older query read.
    expect(
      pickLatestDomainSnapshotId(projectId, [
        candidate(projectId, 5, snap('c')),
        candidate(projectId, 4, snap('d')),
      ]),
    ).toBe(snap('c'))
  })
  it('keeps the first candidate on equal revisions', () => {
    expect(
      pickLatestDomainSnapshotId(projectId, [
        candidate(projectId, 3, snap('a')),
        candidate(projectId, 3, snap('b')),
      ]),
    ).toBe(snap('a'))
  })
  it('ignores non-finite numeric revisions such as NaN and Infinity', () => {
    expect(
      pickLatestDomainSnapshotId(projectId, [
        candidate(projectId, Number.NaN, snap('a')),
        candidate(projectId, Number.POSITIVE_INFINITY, snap('b')),
        candidate(projectId, 1, snap('c')),
      ]),
    ).toBe(snap('c'))
    expect(
      pickLatestDomainSnapshotId(projectId, [
        candidate(projectId, Number.NaN, snap('a')),
        candidate(projectId, Number.NEGATIVE_INFINITY, snap('b')),
      ]),
    ).toBeUndefined()
  })
})

// --- Mentor panel markup contract -------------------------------------------

function queryTaskState(overrides: Partial<LearningTaskStateDTO> = {}): LearningTaskStateDTO {
  return {
    taskId: 'query',
    module: '本体查询',
    goal: '查询完整结果并理解空结果。',
    instructions: '重置G-base，运行未闭环高危告警模板；再将A01改为Closed后重跑，核对空结果。',
    steps: [],
    completionCondition: '实际批准工具的当前版本完整结果与固定预期一致；失败、缺失或过期不通过。',
    commonErrors: ['包含A02：缺少状态过滤。'],
    knowledgePoints: ['本体查询'],
    transfer: false,
    next: 'quality',
    checks: ['Q-01', 'Q-02'],
    readings: [],
    attemptCount: 1,
    withdrawnAttemptCount: 0,
    attemptId: 'attempt-query-1',
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

function learningRead(task: LearningTaskStateDTO): ProjectLearningReadDTO {
  return {
    learningReadVersion: 1,
    projectId,
    domainRevision: 0,
    domainSnapshotRef: 'a'.repeat(64),
    inputVersion: 'rev-0:' + 'a'.repeat(64),
    templateRef: null,
    withdrawnAttemptCount: 0,
    tasks: [task],
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
  }
}

function bridge(read: ProjectLearningReadDTO): LearningLedgerBridge {
  const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
  return {
    getProjectLearningState: async () => ok(structuredClone(read)),
  } as unknown as LearningLedgerBridge
}

async function queryController(task = queryTaskState()): Promise<LearningController> {
  const controller = new LearningController(bridge(learningRead(task)), () => 'op-1')
  await controller.selectAndRefresh(projectId)
  controller.focusTask(task.taskId)
  return controller
}

type PanelOptions = {
  disabled?: boolean
  onResetToGBase?: (taskId: string) => void
  onOpenQueryWorkspace?: () => void
}

async function renderPanel(options: PanelOptions = {}, task = queryTaskState()) {
  const controller = await queryController(task)
  const markup = renderToStaticMarkup(
    createElement(MentorPanel, {
      controller,
      disabled: options.disabled ?? false,
      currentDomainSnapshotId: 'a'.repeat(64),
      onOpenOntologyRepair: () => {},
      onOpenQueryWorkspace: options.onOpenQueryWorkspace,
      onResetToGBase: options.onResetToGBase,
      refreshCheckpoints: async () => {},
    }),
  )
  return markup
}

const resetButton = (markup: string) => markup.includes('data-testid="learning-reset-gbase"')
const openQueryButton = (markup: string) =>
  markup.includes('data-testid="learning-open-query-workspace"')
const scrollButton = (markup: string) =>
  markup.includes('data-testid="learning-scroll-checkpoints"')

describe('MentorPanel Lq entries', () => {
  it('renders the G-base reset entry only for wired G-base tasks and handlers', async () => {
    const withHandler = await renderPanel({ onResetToGBase: () => {} })
    expect(resetButton(withHandler)).toBe(true)
    expect(withHandler).toContain('独立还原 G-base（新建练习项目）')
    expect(scrollButton(withHandler)).toBe(true)
    expect(withHandler).toContain('查看检查点恢复（当前项目内还原）')
    // Backward compatible: without the optional prop nothing renders.
    const withoutHandler = await renderPanel()
    expect(resetButton(withoutHandler)).toBe(false)
    expect(scrollButton(withoutHandler)).toBe(true)
    // Tasks outside the G-base practice set never see the entry.
    const mapping = await renderPanel(
      { onResetToGBase: () => {} },
      queryTaskState({ taskId: 'mapping', checks: [] }),
    )
    expect(resetButton(mapping)).toBe(false)
  })
  it('renders the query-workspace entry only when its handler exists', async () => {
    const withHandler = await renderPanel({ onOpenQueryWorkspace: () => {} })
    expect(openQueryButton(withHandler)).toBe(true)
    expect(withHandler).toContain('打开本体查询')
    const withoutHandler = await renderPanel()
    expect(openQueryButton(withoutHandler)).toBe(false)
  })
  it('disables the reset and query-workspace entries while blocked', async () => {
    const markup = await renderPanel({
      disabled: true,
      onResetToGBase: () => {},
      onOpenQueryWorkspace: () => {},
    })
    const reset = /<button[^>]*data-testid="learning-reset-gbase"[^>]*>/
    const open = /<button[^>]*data-testid="learning-open-query-workspace"[^>]*>/
    const resetMatch = markup.match(reset)?.[0]
    const openMatch = markup.match(open)?.[0]
    expect(resetMatch).toBeDefined()
    expect(openMatch).toBeDefined()
    expect(resetMatch).toContain('disabled')
    expect(openMatch).toContain('disabled')
  })
  it('exposes the checkpoint scroll helper backed by #project-checkpoints', async () => {
    const markup = await renderPanel()
    expect(scrollButton(markup)).toBe(true)

    const calls: string[] = []
    const scrolled = scrollToProjectCheckpoints({
      getElementById: (id: string) => {
        calls.push(id)
        return {
          scrollIntoView: (options?: ScrollIntoViewOptions) => {
            calls.push(JSON.stringify(options))
          },
        } as unknown as HTMLElement
      },
    })
    expect(scrolled).toBe(true)
    expect(calls).toEqual(['project-checkpoints', '{"block":"start","behavior":"auto"}'])
    expect(scrollToProjectCheckpoints({ getElementById: () => null })).toBe(false)
  })
})

describe('Lq storage boundary', () => {
  it('never touches localStorage or sessionStorage during panel rendering', async () => {
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
    const spy = vi.fn()
    try {
      const markup = await renderPanel({
        onResetToGBase: spy,
        onOpenQueryWorkspace: spy,
      })
      expect(resetButton(markup)).toBe(true)
      expect(openQueryButton(markup)).toBe(true)
      expect(accesses).toEqual([])
    } finally {
      Reflect.deleteProperty(globalThis, 'localStorage')
      Reflect.deleteProperty(globalThis, 'sessionStorage')
    }
  })
})
