import type { LearningTaskStateDTO } from '@ontolearn/contracts'
import { displayedCheckStatus } from '../learning/learning-controller'

export type PrimaryView = 'projects' | 'learning' | 'foundation' | 'workspace' | 'settings'

export type ConnectedModule = 'mapping' | 'behavior' | 'scenario' | 'transfer'
export type WorkspaceModule = 'query' | 'ontology' | 'quality' | ConnectedModule

export type CourseNavStep = {
  id: string
  num: string
  label: string
  module: WorkspaceModule
  href: string
  taskIds: readonly string[]
  requiresLearningUnlock?: boolean
}

export const COURSE_NAV_STEPS: readonly CourseNavStep[] = [
  {
    id: 'step-01',
    num: '01',
    label: '本体构建',
    module: 'ontology',
    href: '#ontology-workspace',
    taskIds: ['business-ontology'],
  },
  {
    id: 'step-02',
    num: '02',
    label: '数据映射',
    module: 'mapping',
    href: '#mapping-workspace',
    taskIds: ['mapping'],
  },
  {
    id: 'step-03',
    num: '03',
    label: '本体查询',
    module: 'query',
    href: '#query-workspace',
    taskIds: ['query'],
  },
  {
    id: 'step-04',
    num: '04',
    label: '质量与推导',
    module: 'quality',
    href: '#quality-workspace',
    taskIds: ['quality'],
  },
  {
    id: 'step-05',
    num: '05',
    label: '行为定义',
    module: 'behavior',
    href: '#behavior-workspace',
    taskIds: ['behavior'],
  },
  {
    id: 'step-06',
    num: '06',
    label: '情景推演',
    module: 'scenario',
    href: '#scenario-workspace',
    taskIds: ['scenario'],
  },
  {
    id: 'step-07',
    num: '07',
    label: '迁移练习',
    module: 'quality',
    href: '#transfer-practice-workspace',
    taskIds: ['transfer-repair', 'transfer-classify'],
    requiresLearningUnlock: true,
  },
  {
    id: 'step-08',
    num: '08',
    label: '导出与迁移',
    module: 'transfer',
    href: '#transfer-workspace',
    taskIds: ['report'],
  },
] as const

export function workspaceForLearningTask(taskId: string): WorkspaceModule {
  switch (taskId) {
    case 'business-ontology':
      return 'ontology'
    case 'mapping':
      return 'mapping'
    case 'query':
      return 'query'
    case 'quality':
    case 'transfer-repair':
    case 'transfer-classify':
      return 'quality'
    case 'behavior':
      return 'behavior'
    case 'scenario':
      return 'scenario'
    case 'report':
      return 'transfer'
    default:
      return 'ontology'
  }
}

export function isCourseNavStepActive(
  step: CourseNavStep,
  primaryView: PrimaryView,
  workspaceModule: WorkspaceModule,
  focusedTaskId: string | undefined,
): boolean {
  if (primaryView !== 'workspace') return false
  if (step.id === 'step-07') {
    return (
      workspaceModule === 'quality' &&
      (focusedTaskId === 'transfer-repair' || focusedTaskId === 'transfer-classify')
    )
  }
  if (step.id === 'step-04') {
    return (
      workspaceModule === 'quality' &&
      focusedTaskId !== 'transfer-repair' &&
      focusedTaskId !== 'transfer-classify'
    )
  }
  return workspaceModule === step.module
}

export type StepStatusTone = 'passed' | 'stale' | 'warn' | 'idle'

export function stepCourseStatus(
  step: CourseNavStep,
  learningTasks: readonly LearningTaskStateDTO[] | undefined,
  currentDomainSnapshotId: string | undefined,
  learningSnapshotRef: string | undefined,
): { text: string; tone: StepStatusTone } | undefined {
  if (!learningTasks?.length) return undefined
  const matched = step.taskIds
    .map((taskId) => learningTasks.find((item) => item.taskId === taskId))
    .filter((item): item is LearningTaskStateDTO => item !== undefined)
  if (!matched.length) return undefined

  const statuses = matched.map((item) =>
    displayedCheckStatus(item, currentDomainSnapshotId, learningSnapshotRef),
  )
  if (statuses.every((text) => text === '已通过')) {
    return { text: '已通过', tone: 'passed' }
  }
  if (statuses.some((text) => text === '已过期 / 需重跑')) {
    return { text: '已过期', tone: 'stale' }
  }
  if (statuses.some((text) => text === '需要修复' || text.startsWith('检查失败'))) {
    return { text: '需修复', tone: 'warn' }
  }
  if (matched.some((item) => item.operationComplete || item.maxHintLevel > 0)) {
    return { text: '进行中', tone: 'warn' }
  }
  return { text: '待检查', tone: 'idle' }
}

export function stepMetaForWorkspace(
  workspaceModule: WorkspaceModule,
  focusedTaskId: string | undefined,
): CourseNavStep {
  if (
    workspaceModule === 'quality' &&
    (focusedTaskId === 'transfer-repair' || focusedTaskId === 'transfer-classify')
  ) {
    return COURSE_NAV_STEPS[6]!
  }
  return COURSE_NAV_STEPS.find((item) => item.module === workspaceModule) ?? COURSE_NAV_STEPS[0]!
}
