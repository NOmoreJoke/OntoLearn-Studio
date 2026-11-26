import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react'
import {
  safeError,
  reassembleChangeSetDocument,
  type HealthResult,
  type TaskView,
  type SafeError,
  type ProgressView,
  type TaskUpdate,
  type MainlineCatalogDTO,
  type MainlineCreateRequestDTO,
  type MainlineExampleCreateRequestDTO,
  type LibraryWorkspaceReport,
  type QualityFindingDTO,
  type AgentDraftPlanDTO,
  type AgentMode,
  type QueryDraftDTO,
} from '@ontolearn/contracts'
import { explainError, resultSummary } from './task-presentation'
import { TaskProgressBuffer } from './task-progress'
import { QueryWorkspaceController, QueryWorkspacePage } from './query'
import { OntologyMainlinePage } from './ontology/OntologyMainlinePage'
import { ImportExportPanel } from './ontology/import-export-panel'
import { DraftDiffPreview } from './ontology/draft-diff-preview'
import { OntologySession } from './ontology/mainline-session'
import { ontologyOperations } from './ontology/mainline-operations'
import type { OntologyMainlineBridge } from './ontology/mainline-api'
import {
  agentContextStore,
  bindAgentArtifact,
  persistAgentMode,
  readAgentModeMirror,
  writeAgentModeMirror,
  type SourcedAgentArtifact,
} from './agent/agent-context-store'
import { toAgentModule, type AgentAction } from './agent/context-actions'
import { ProjectManagementController } from './project/management-controller'
import { ProjectManagementPanel } from './project/ProjectManagementPanel'
import { ProjectCheckpointRestorePanel } from './project/ProjectCheckpointRestorePanel'
import { ProjectRestoreController } from './project/restore-controller'
import { LibraryLocationPanel } from './project/LibraryLocationPanel'
import { libraryAdmissionBlocked, settleManagementTail } from './project/lifecycle-admission'
import {
  LearningController,
  displayedCheckStatus,
  mentorAssistanceText,
} from './learning/learning-controller'
import { pickLatestDomainSnapshotId } from './learning/domain-snapshot'
import { offlineCourse, offlineGlossary } from './learning/content'
import { DualTrackRoadmapHeader, type LearningTrackId } from './learning/DualTrackRoadmapHeader'
import type { FoundationMicroStepId } from './learning/scenarios/retail-membership-orders'
import {
  commitLearningTaskFixture,
  prepareLearningTaskFixture,
  type LearningFixtureTaskId,
} from './learning/task-fixture'
import { QualityWorkspace } from './quality/QualityWorkspace'
import { ModelPanel } from './ModelPanel'
import { MappingWorkspace } from './mapping/MappingWorkspace'
import type { WorkspaceStatus } from './mapping/workspace-operation'
import { ConnectedBehaviorWorkspace } from './behavior/ConnectedBehaviorWorkspace'
import { ConnectedScenarioWorkspace } from './scenario/ConnectedScenarioWorkspace'
import { TransferWorkspace } from './transfer/TransferWorkspace'
import { SidebarNav } from './shell/SidebarNav'
import { TopContextBar } from './shell/TopContextBar'
import { WorkspaceDrawers } from './shell/WorkspaceDrawers'
import { UnifiedAssistantRail, type AssistantRailTab } from './shell/UnifiedAssistantRail'
import {
  workspaceForLearningTask,
  type ConnectedModule,
  type CourseNavStep,
  type PrimaryView,
  type WorkspaceModule,
} from './shell/shell-routing'
import './shell/shell.css'

type FixtureProposal = {
  taskId: LearningFixtureTaskId
  generation: number
  operationId: string
  diff: NonNullable<Awaited<ReturnType<typeof prepareLearningTaskFixture>>>
}
type QualityLocation = {
  projectId: string
  generation: number
  module: WorkspaceModule
  finding: QualityFindingDTO
}

const connectedModules = {
  mapping: { label: '数据映射', title: '当前项目数据映射' },
  behavior: { label: '行为定义', title: '当前项目行为定义' },
  scenario: { label: '情景推演', title: '当前项目情景推演' },
  transfer: { label: '导出与迁移', title: '当前项目导出与迁移' },
} as const
const cleanConnectedStatus: WorkspaceStatus = { dirty: false, unresolved: false }

function isConnectedModule(module: WorkspaceModule): module is ConnectedModule {
  return Object.hasOwn(connectedModules, module)
}
type OntologyContext = {
  session: OntologySession
  contextKey: string
  projectId: string
  generation: number
}
// Pure cross-workspace snapshot selection, re-exported for direct unit tests.
export {
  pickLatestDomainSnapshotId,
  type DomainSnapshotCandidate,
} from './learning/domain-snapshot'

export function App() {
  const [showIntroduction, setShowIntroduction] = useState(false)
  const [workspaceFrozen, setWorkspaceFrozen] = useState(false)
  const frozen = useRef(false)
  const [workspaceStatus, setWorkspaceStatus] = useState({ dirty: false, unresolved: false })
  const workspaceNotify = useRef<() => void>(() => {})
  const ontologyDirty = useRef(false)
  const connectedStatus = useRef(cleanConnectedStatus)
  const [connectedUnresolved, setConnectedUnresolved] = useState(false)
  const workspaceGeneration = useRef(0)
  const [management] = useState(() =>
    window.ontolearn?.getProjectManagementState
      ? new ProjectManagementController(window.ontolearn)
      : undefined,
  )
  const [managementState, setManagementState] = useState(() => management?.getSnapshot())
  const managementBlocked =
    !!managementState &&
    (managementState.busy ||
      !!managementState.pending ||
      managementState.recovery.length > 0 ||
      !managementState.recoveryLoaded)
  const [checkpointCtl] = useState(() =>
    window.ontolearn?.listProjectCheckpoints
      ? new ProjectRestoreController(window.ontolearn)
      : undefined,
  )
  const [checkpointState, setCheckpointState] = useState(() => checkpointCtl?.getSnapshot())
  const [learningCtl] = useState(() =>
    window.ontolearn?.getProjectLearningState
      ? new LearningController(window.ontolearn)
      : undefined,
  )
  const [learningState, setLearningState] = useState(() => learningCtl?.getSnapshot())
  // 右侧统一辅助栏默认收起；从学习入口或路线图切入任务时自动展开（PRD 8.2）。
  const [primaryView, setPrimaryView] = useState<PrimaryView>('projects')
  const [railOpen, setRailOpen] = useState(false)
  const [activeRailTab, setActiveRailTab] = useState<AssistantRailTab>('mentor')
  const [checkpointsDrawerOpen, setCheckpointsDrawerOpen] = useState(false)
  const [jobsDrawerOpen, setJobsDrawerOpen] = useState(false)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [portalTerm, setPortalTerm] = useState('本体')
  const [learningTrack, setLearningTrack] = useState<LearningTrackId>('retail')
  const [activeFoundationStep, setActiveFoundationStep] = useState<FoundationMicroStepId>('step-01')
  const hasAutoEnteredWorkspace = useRef(false)
  // 本体会话最近一次真实读取的域快照；ChangeSet 提交后的自动重读让它前进，
  // 供学习面板在无后台 RPC 的前提下派生“已过期 / 需重跑”。revision 取自真实
  // 读取的 projectRevision，使跨工作区比较按提交先后而不是缓存先后。
  const [sessionDomainSnapshot, setSessionDomainSnapshot] = useState<{
    projectId: string
    snapshotId: string
    revision: number
  }>()
  // 查询工作台最近一次真实读取的域快照（读取项目与持久工作草稿 / 提交结算后）。
  const [queryDomainSnapshot, setQueryDomainSnapshot] = useState<{
    projectId: string
    snapshotId: string
    revision: number
  }>()
  const [qualityDomainSnapshot, setQualityDomainSnapshot] = useState<{
    projectId: string
    snapshotId: string
    revision: number
  }>()
  const [qualityScopes, setQualityScopes] = useState<
    Record<string, 'asserted' | 'asserted+derived'>
  >({})
  const [qualityLocation, setQualityLocation] = useState<QualityLocation>()
  const [qualityPending, setQualityPending] = useState(false)
  const qualityPendingRef = useRef(false)
  const fixtureBusyRef = useRef(false)
  const [fixtureBusy, setFixtureBusy] = useState(false)
  const [fixtureProposal, setFixtureProposal] = useState<FixtureProposal>()
  const [fixtureStatus, setFixtureStatus] = useState<{
    projectId?: string
    taskId: LearningFixtureTaskId
    text: string
  }>()
  // 首启序列是否已结算。首启序列在飞、恢复读取进行中或仍有待核对恢复时，创建
  // 与打开入口保持禁用，防止在 checkpointCtl.initialize() 尚未结算前抢跑并发
  // 点击。序列结算即打开；一次读取失败不再把整个项目库永久锁死——检查点面板
  // 自身仍按自己的 recoveryLoaded 独立收口。
  const [checkpointBooted, setCheckpointBooted] = useState(false)
  const checkpointBlocked =
    !!checkpointState &&
    (!checkpointBooted || checkpointState.busy || checkpointState.recovery.length > 0)
  const [checkpointApplied, setCheckpointApplied] = useState<{ projectId: string; nonce: number }>()
  const [catalog, setCatalog] = useState<MainlineCatalogDTO>()
  const [projectName, setProjectName] = useState('')
  const [projectBusy, setProjectBusy] = useState(false)
  const [projectNotice, setProjectNotice] = useState('')
  const [projectError, setProjectError] = useState<SafeError>()
  const [hasCreateIntent, setHasCreateIntent] = useState(false)
  const queryControllers = useRef(new Map<string, QueryWorkspaceController>())
  const [queryController, setQueryController] = useState<QueryWorkspaceController>()
  const selectedQuery = useRef<QueryWorkspaceController | undefined>(undefined)
  const selectedQueryLease = useRef<(() => void) | undefined>(undefined)
  const [workspaceModule, setWorkspaceModule] = useState<WorkspaceModule>('query')
  const selectedModule = useRef<WorkspaceModule>('query')
  // 跨页共享的 Agent 上下文真值源：仅 UI 状态，不写入项目数据，也不发起 ChangeSet。
  const agentContext = useSyncExternalStore(
    agentContextStore.subscribe,
    agentContextStore.getSnapshot,
    agentContextStore.getSnapshot,
  )
  // 上游 Agent 产出的查询草稿与本体草稿计划；都需人工核对后才进入工作台。
  // 两份产物都绑定产生它们的项目与世代：退役项目的产物不会进入新工作台。
  const [agentQueryArtifact, setAgentQueryArtifact] =
    useState<SourcedAgentArtifact<QueryDraftDTO>>()
  const [agentDraftArtifact, setAgentDraftArtifact] =
    useState<SourcedAgentArtifact<AgentDraftPlanDTO>>()
  // 递增即要求助手面板重新读取模型就绪与隐私状态。
  const [modelSyncVersion, setModelSyncVersion] = useState(0)
  const agentModeMirror = useRef('')
  const documentNonce = useRef<string | undefined>(undefined)
  const contextSerial = useRef(0)
  const documentLeaving = useRef(false)
  const ontologyOwner = useRef<OntologyContext | undefined>(undefined)
  const [ontologyContext, setOntologyContext] = useState<OntologyContext>()
  const readyWorkspace = useRef<TaskView | undefined>(undefined)
  const libraryBusy = useRef(false)
  // open/create 正在进行的 management 准入尾段；期间的恢复视图必须等它完成。
  const admissionTail = useRef<Promise<void> | undefined>(undefined)
  // 首启串行序列（management 完全结算后再启动 restore 通道），全局共享一份。
  const boot = useRef<Promise<void> | undefined>(undefined)
  // 首启序列的共享存活标记：真正的卸载会关闭它，StrictMode 重挂载会重新武装。
  const bootActive = useRef(true)
  const selectionTarget = useRef<{ projectId?: string } | undefined>(undefined)
  const createIntent = useRef<
    MainlineCreateRequestDTO | MainlineExampleCreateRequestDTO | undefined
  >(undefined)
  const [result, setResult] = useState<HealthResult>()
  const [tasks, setTasks] = useState<TaskView>()
  // The upstream artefacts are only delivered while they still belong to the
  // selected project and the selected workspace generation.
  const agentQueryDraft = bindAgentArtifact(
    agentQueryArtifact,
    tasks?.project?.projectId,
    tasks?.generation,
  )
  const agentDraftPlan = bindAgentArtifact(
    agentDraftArtifact,
    tasks?.project?.projectId,
    tasks?.generation,
  )
  const [progress, setProgress] = useState<Record<string, ProgressView>>({})
  const [taskError, setTaskError] = useState<SafeError>()
  const [summaries, setSummaries] = useState<Record<string, string>>({})
  const [connection, setConnection] = useState<Extract<TaskUpdate, { kind: 'connection' }>>()
  const current = useRef<TaskView | undefined>(undefined)
  const latestGeneration = useRef(-1)
  const uncertain = useRef(false)
  const connectionEpoch = useRef(0)
  const pendingProgress = useRef(new TaskProgressBuffer())
  const retireOntology = useCallback(() => {
    contextSerial.current++
    const previous = ontologyOwner.current
    ontologyOwner.current = undefined
    previous?.session.retire()
    ontologyDirty.current = false
    // A retired context keeps neither an object selection nor an upstream
    // artefact: both belong to the project generation that just went away.
    agentContextStore.setSelectedObjectIds([])
    setAgentQueryArtifact(undefined)
    setAgentDraftArtifact(undefined)
    workspaceNotify.current()
    setOntologyContext(undefined)
    setSessionDomainSnapshot(undefined)
  }, [setOntologyContext])
  const disconnectQuery = useCallback(() => {
    selectedQuery.current?.disconnect()
    selectedQueryLease.current?.()
    selectedQueryLease.current = undefined
    selectedQuery.current = undefined
    setQueryController(undefined)
  }, [setQueryController])
  const selectQueryWorkspace = useCallback(
    (view: TaskView) => {
      const bridge = window.ontolearn
      if (!bridge || selectedModule.current !== 'query' || !view.project) return
      const projectId = view.project.projectId
      let controller = queryControllers.current.get(projectId)
      if (!controller) {
        controller = new QueryWorkspaceController(projectId, bridge, reassembleChangeSetDocument)
        queryControllers.current.set(projectId, controller)
        controller.subscribe(() => workspaceNotify.current())
      }
      // Acquire and seed the new lease before dropping only our previous lease.
      // A Page cleanup owns its own disposer and cannot disconnect this lease.
      const previousLease = selectedQueryLease.current
      const nextLease = controller.connect(view)
      selectedQueryLease.current = nextLease
      selectedQuery.current = controller
      setQueryController(controller)
      previousLease?.()
    },
    [setQueryController],
  )
  const activateWorkspace = useCallback(() => {
    const view = readyWorkspace.current
    if (
      documentLeaving.current ||
      libraryBusy.current ||
      uncertain.current ||
      management?.unresolved ||
      !view?.project
    )
      return
    if (selectedModule.current === 'query') {
      // The ready view admits this context; the current view also includes later
      // authentic Job updates received while this retained controller was away.
      const latest = current.current
      if (
        !latest?.project ||
        latest.generation !== view.generation ||
        latest.project.projectId !== view.project.projectId
      )
        return
      selectQueryWorkspace(latest)
      return
    }
    if (selectedModule.current !== 'ontology') return
    const actualBridge = window.ontolearn
    if (!actualBridge) return
    // One actual canonical object; this assignment is intentionally checked by T01.
    const canonicalBridge: OntologyMainlineBridge = actualBridge
    documentNonce.current ??= crypto.randomUUID()
    let contextKey = JSON.stringify([
      documentNonce.current,
      contextSerial.current,
      view.generation,
      view.project.projectId,
    ])
    const previous = ontologyOwner.current
    if (previous?.contextKey === contextKey && previous.session.bridge === canonicalBridge) return
    if (previous) {
      retireOntology()
      contextKey = JSON.stringify([
        documentNonce.current,
        contextSerial.current,
        view.generation,
        view.project.projectId,
      ])
    }
    const next = {
      session: new OntologySession(canonicalBridge),
      contextKey,
      projectId: view.project.projectId,
      generation: view.generation,
    }
    next.session.subscribe(() => {
      // The post-commit auto re-read publishes the workspace's freshest domain
      // snapshot; the mentor panel derives staleness from it without any RPC.
      const source = next.session.getSnapshot().source
      if (source)
        setSessionDomainSnapshot((old) =>
          old &&
          old.projectId === source.projectId &&
          old.snapshotId === source.inputSnapshotId &&
          old.revision === source.domain.projectRevision
            ? old
            : {
                projectId: source.projectId,
                snapshotId: source.inputSnapshotId,
                revision: source.domain.projectRevision,
              },
        )
      workspaceNotify.current()
    })
    ontologyOwner.current = next
    setOntologyContext(next)
  }, [management, retireOntology, selectQueryWorkspace, setOntologyContext])
  function hasCurrentFixtureProposal() {
    const view = readyWorkspace.current
    return (
      fixtureProposal &&
      fixtureProposal.diff.preview.projectId === view?.project?.projectId &&
      fixtureProposal.generation === view?.generation
    )
  }
  function selectWorkspace(module: WorkspaceModule) {
    if (
      qualityPendingRef.current ||
      fixtureBusyRef.current ||
      connectedStatus.current.unresolved ||
      hasCurrentFixtureProposal()
    )
      return
    if (
      libraryAdmissionBlocked({
        documentLeaving: documentLeaving.current,
        libraryBusy: libraryBusy.current,
        frozen: frozen.current,
        managementUnresolved: !!management?.unresolved,
      }) ||
      Boolean(learningCtl?.unresolved)
    )
      return
    if (uncertain.current || !readyWorkspace.current?.project) return
    setPrimaryView('workspace')
    if (selectedModule.current === module) return
    if (
      connectedStatus.current.dirty &&
      !window.confirm('切换工作台将放弃此处未保存的编辑。继续切换？')
    )
      return
    retireOntology()
    disconnectQuery()
    selectedModule.current = module
    setWorkspaceModule(module)
    // The Agent context follows the active workspace (UI state only).
    agentContextStore.setModule(toAgentModule(module))
    activateWorkspace()
  }
  function selectCourseStep(step: CourseNavStep) {
    if (step.id === 'step-07' && learningCtl) {
      const currentFocused = learningCtl.getSnapshot().focusedTaskId
      if (currentFocused !== 'transfer-repair' && currentFocused !== 'transfer-classify') {
        const states = learningCtl.getSnapshot().learning?.tasks
        const nextTransfer =
          states?.find(
            (item) =>
              (item.taskId === 'transfer-repair' || item.taskId === 'transfer-classify') &&
              !item.operationComplete,
          )?.taskId ?? 'transfer-repair'
        learningCtl.focusTask(nextTransfer)
      }
      setActiveRailTab('mentor')
      setRailOpen(true)
    } else if (step.id === 'step-04' && learningCtl) {
      const currentFocused = learningCtl.getSnapshot().focusedTaskId
      if (currentFocused === 'transfer-repair' || currentFocused === 'transfer-classify') {
        learningCtl.focusTask('quality')
      }
    }
    selectWorkspace(step.module)
  }
  const updateTasks = useCallback((value: TaskView) => {
    if (value.generation < latestGeneration.current) return false
    latestGeneration.current = value.generation
    current.current = value
    setTasks(value)
    return true
  }, [])
  const applyRestored = useCallback(
    async (value: TaskView) => {
      if (documentLeaving.current || value.generation < latestGeneration.current) return
      const target = selectionTarget.current
      if (target && (!target.projectId || value.project?.projectId !== target.projectId)) return
      const previous = readyWorkspace.current
      if (
        previous &&
        (previous.generation !== value.generation ||
          previous.project?.projectId !== value.project?.projectId ||
          previous.project?.inputSnapshotId !== value.project?.inputSnapshotId)
      ) {
        retireOntology()
        disconnectQuery()
        setSessionDomainSnapshot(undefined)
        setQueryDomainSnapshot(undefined)
      }
      // 本次恢复由 open/create 持有时等待其完整 management 尾段；自主恢复则
      // 在渲染前自行串行完成同等读取；selected-project-version 渲染之后不允许
      // 仍有 management 调用在飞行（单并发锁会拒绝随后的项目读取）。
      const owned = admissionTail.current
      if (owned) await owned
      else if (value.project) {
        // 自主恢复：与 open/create 相同的尾段顺序，先结算 management 读取，
        // 再结算检查点读取；单并发模型下两段不得重叠。首启序列尚未结算时
        // 必须先等它完成，否则恢复读取会与 project:management-pending /
        // project:restore-pending 抢同一个 mainline 单并发槽位。
        if (boot.current) await boot.current
        if (management) await settleManagementTail(management, value.project.projectId)
        if (checkpointCtl) {
          checkpointCtl.select(value.project.projectId)
          await checkpointCtl.refreshWhenIdle()
        }
        // 学习读取与检查点读取同样串行结算；此处绝不与 open/create 的尾段重叠。
        await learningCtl?.selectAndRefresh(value.project.projectId)
      } else {
        checkpointCtl?.select(undefined)
        learningCtl?.select(undefined)
        setSessionDomainSnapshot(undefined)
      }
      if (documentLeaving.current || value.generation < latestGeneration.current) return
      if (!updateTasks(value)) return
      readyWorkspace.current = value
      management?.select(value.project?.projectId)
      if (uncertain.current) setResult(undefined)
      uncertain.current = false
      setConnection(undefined)
      setTaskError(undefined)
      setProgress(pendingProgress.current.restore(value))
      setSummaries({})
      activateWorkspace()
      if (value.project && !libraryBusy.current && !hasAutoEnteredWorkspace.current) {
        hasAutoEnteredWorkspace.current = true
        setPrimaryView('workspace')
      }
      if (value.jobs.length > 0) setJobsDrawerOpen(true)
    },
    [
      updateTasks,
      management,
      checkpointCtl,
      learningCtl,
      retireOntology,
      disconnectQuery,
      activateWorkspace,
      setResult,
      setConnection,
      setTaskError,
      setProgress,
      setSummaries,
    ],
  )
  async function restore() {
    if (documentLeaving.current) return
    const serial = contextSerial.current
    const response = await window.ontolearn?.restoreTasks()
    if (documentLeaving.current || serial !== contextSerial.current) return
    if (response?.ok) {
      await applyRestored(response.data)
    } else if (response) setTaskError(response.error)
  }
  async function listProjects(cursor: string | null = null) {
    if (
      qualityPendingRef.current ||
      fixtureBusyRef.current ||
      connectedStatus.current.unresolved ||
      hasCurrentFixtureProposal()
    )
      return
    const bridge = window.ontolearn
    if (
      documentLeaving.current ||
      !bridge ||
      libraryBusy.current ||
      frozen.current ||
      Boolean(learningCtl?.unresolved)
    )
      return
    if (management) {
      await management.refresh()
      return
    }
    libraryBusy.current = true
    setProjectBusy(true)
    setProjectError(undefined)
    try {
      const response = await bridge.getProjectCatalog({ pageSize: 64, cursor })
      if (response.ok) setCatalog(response.data)
      else setProjectError(response.error)
    } catch {
      setProjectError(safeError(undefined))
    } finally {
      libraryBusy.current = false
      selectionTarget.current = undefined
      setProjectBusy(false)
      // No ontology auto-read can race this call's catalog/restore tail.
      activateWorkspace()
    }
  }
  async function openProject(projectId: string) {
    if (
      qualityPendingRef.current ||
      fixtureBusyRef.current ||
      connectedStatus.current.unresolved ||
      hasCurrentFixtureProposal()
    )
      return
    const bridge = window.ontolearn
    if (
      !bridge ||
      libraryAdmissionBlocked({
        documentLeaving: documentLeaving.current,
        libraryBusy: libraryBusy.current,
        frozen: frozen.current,
        managementUnresolved: !!management?.unresolved,
      }) ||
      Boolean(learningCtl?.unresolved)
    )
      return
    if (
      connectedStatus.current.dirty &&
      !window.confirm('打开项目将放弃当前工作台未保存的编辑。继续打开？')
    )
      return
    setProjectBusy(true)
    setProjectError(undefined)
    libraryBusy.current = true
    selectionTarget.current = { projectId }
    readyWorkspace.current = undefined
    try {
      retireOntology()
      disconnectQuery()
      const response = await bridge.openProject({ projectId })
      if (!response.ok) {
        setProjectError(response.error)
        return
      }
      // 版本渲染（restore → selected-project-version）与交还操作之前，先串行
      // 完成全部 management、检查点与学习状态读取；单并发模型下不允许留下在
      // 飞行的调用，管理通道与恢复通道也不得重叠。
      const tail = (async () => {
        await settleManagementTail(management, projectId, { refresh: true })
        checkpointCtl?.select(projectId)
        await checkpointCtl?.refreshWhenIdle()
        await learningCtl?.selectAndRefresh(projectId)
      })()
      admissionTail.current = tail
      await tail
      setProjectNotice(`项目已打开 · 版本 ${response.data.projectRevision}`)
      await restore()
    } catch {
      setProjectError(safeError(undefined))
    } finally {
      admissionTail.current = undefined
      libraryBusy.current = false
      selectionTarget.current = undefined
      setProjectBusy(false)
      // No ontology auto-read can race this call's catalog/restore tail.
      activateWorkspace()
    }
  }
  async function createProject(
    example = false,
    options?: {
      name?: string
      initialWorkspace?: WorkspaceModule
      startAttemptTaskId?: string
      enterWorkspace?: boolean
    },
  ) {
    if (
      qualityPendingRef.current ||
      connectedStatus.current.unresolved ||
      (fixtureBusyRef.current && !options?.name) ||
      hasCurrentFixtureProposal()
    )
      return
    const bridge = window.ontolearn
    const name = options?.name ?? (projectName.trim() ? projectName : example ? '设备运维示例' : '')
    if (
      !bridge ||
      !name.trim() ||
      libraryAdmissionBlocked({
        documentLeaving: documentLeaving.current,
        libraryBusy: libraryBusy.current,
        frozen: frozen.current,
        managementUnresolved: !!management?.unresolved,
      }) ||
      Boolean(learningCtl?.unresolved)
    )
      return
    if (
      !createIntent.current &&
      (new TextEncoder().encode(name).length > 4096 || /[\uD800-\uDFFF]/u.test(name))
    ) {
      setProjectNotice('项目名称过长或包含无效字符，请修改后重试。')
      return
    }
    if (
      connectedStatus.current.dirty &&
      !window.confirm('新建项目将放弃当前工作台未保存的编辑。继续创建？')
    )
      return
    setProjectBusy(true)
    setProjectError(undefined)
    let createdProjectId: string | undefined
    let openedProjectId: string | undefined
    libraryBusy.current = true
    selectionTarget.current = {}
    readyWorkspace.current = undefined
    try {
      retireOntology()
      disconnectQuery()
      // Keep the original operation and exact name when delivery is unknown.
      // A second click reconciles that operation instead of creating a new one.
      createIntent.current ??= example
        ? {
            exampleCreateRequestVersion: 1,
            operationId: crypto.randomUUID(),
            name,
            exampleId: 'equipment-maintenance',
            inputDigest: '52952b637b02ba283d47a9e0c34a1691c1d850b94bb9b366a9863a55507c435e',
          }
        : {
            requestVersion: 1,
            operationId: crypto.randomUUID(),
            name,
            initialization: { kind: 'blank' },
          }
      setProjectName(createIntent.current.name)
      setHasCreateIntent(true)
      const created = await ('exampleCreateRequestVersion' in createIntent.current
        ? bridge.createExampleProject(createIntent.current)
        : bridge.createBlankProject(createIntent.current))
      if (!created.ok) {
        setProjectError(created.error)
        setProjectNotice('创建结果尚未确认；再次核对将使用同一次请求。')
        return
      }
      createIntent.current = undefined
      setHasCreateIntent(false)
      createdProjectId = created.data.projectId
      setProjectName('')
      selectionTarget.current = { projectId: created.data.projectId }
      const opened = await bridge.openProject({ projectId: created.data.projectId })
      if (opened.ok) setProjectNotice('项目已创建并打开。已提交的更改将保存在本机。')
      else {
        setProjectNotice('项目已创建，但打开失败。可刷新项目列表后重新打开。')
        setProjectError(opened.error)
      }
      const listed = await bridge.getProjectCatalog({ pageSize: 64, cursor: null })
      if (listed.ok) setCatalog(listed.data)
      // 与 openProject 相同的准入尾段：全部 management、检查点与学习状态读取
      // 串行完成后，才允许 restore() 渲染新项目版本并把工作台交还出去。
      await management?.refresh()
      if (opened.ok) {
        const tail = (async () => {
          await settleManagementTail(management, created.data.projectId)
          checkpointCtl?.select(created.data.projectId)
          await checkpointCtl?.refreshWhenIdle()
          await learningCtl?.selectAndRefresh(created.data.projectId)
          if (options?.startAttemptTaskId) {
            // The practice attempt starts at the new project's own creation
            // claim: prior projects' queries can never satisfy its checks.
            learningCtl?.focusTask(options.startAttemptTaskId)
            await learningCtl?.restartAttempt()
          }
        })()
        admissionTail.current = tail
        await tail
        // Open the requested workspace only after the serial tail settled, so
        // the workspace auto-read never races the admission reads above.
        if (options?.initialWorkspace && selectedModule.current !== options.initialWorkspace) {
          selectedModule.current = options.initialWorkspace
          setWorkspaceModule(options.initialWorkspace)
          agentContextStore.setModule(toAgentModule(options.initialWorkspace))
        }
        await restore()
        if (options?.enterWorkspace || options?.initialWorkspace) {
          hasAutoEnteredWorkspace.current = true
          setPrimaryView('workspace')
        }
        openedProjectId = created.data.projectId
      }
    } catch {
      setProjectError(safeError(undefined))
      setProjectNotice(
        createdProjectId
          ? '项目已创建，打开结果尚未确认。可刷新项目列表后重新打开。'
          : '创建结果尚未确认，请核对原请求或项目列表。',
      )
    } finally {
      admissionTail.current = undefined
      libraryBusy.current = false
      selectionTarget.current = undefined
      setProjectBusy(false)
      // No ontology auto-read can race this call's catalog/restore tail.
      activateWorkspace()
    }
    return openedProjectId
  }
  const aggregateWorkspace = useCallback(() => {
    const queries = [...queryControllers.current.values()]
    const ontology = ontologyOwner.current?.session.getSnapshot()
    const dirtyEditor =
      connectedStatus.current.dirty || queries.some((controller) => controller.getSnapshot().dirty)
    return {
      dirty: ontologyDirty.current || dirtyEditor,
      unresolved:
        connectedStatus.current.unresolved ||
        qualityPendingRef.current ||
        fixtureBusyRef.current ||
        !!createIntent.current ||
        libraryBusy.current ||
        uncertain.current ||
        !!management?.unresolved ||
        !!checkpointCtl?.unresolved ||
        !!learningCtl?.unresolved ||
        queries.some(
          (controller) => controller.hasUnresolvedWrite || controller.getSnapshot().busy,
        ) ||
        ontologyOperations.hasUnresolved ||
        (!!ontology && ['reading', 'preparing', 'submitting', 'unknown'].includes(ontology.phase)),
    }
  }, [management, checkpointCtl, learningCtl])
  const reportWorkspace = useCallback((): LibraryWorkspaceReport => {
    documentNonce.current ??= crypto.randomUUID()
    return {
      documentNonce: documentNonce.current,
      generation: ++workspaceGeneration.current,
      ...aggregateWorkspace(),
    }
  }, [aggregateWorkspace])
  useEffect(() => {
    const notify = () => {
      const state = aggregateWorkspace()
      setWorkspaceStatus((old) =>
        old.dirty === state.dirty && old.unresolved === state.unresolved ? old : state,
      )
      if (window.ontolearn?.reportLibraryWorkspace && !frozen.current)
        void window.ontolearn.reportLibraryWorkspace(reportWorkspace()).catch(() => {})
    }
    workspaceNotify.current = notify
    const release = ontologyOperations.subscribe(notify)
    notify()
    return () => {
      release()
      workspaceNotify.current = () => {}
    }
  }, [
    aggregateWorkspace,
    reportWorkspace,
    hasCreateIntent,
    projectBusy,
    connection,
    ontologyContext,
  ])
  const onConnectedStatus = useCallback((status: WorkspaceStatus) => {
    connectedStatus.current = status
    setConnectedUnresolved(status.unresolved)
    workspaceNotify.current()
  }, [])
  const onQualityPending = useCallback((pending: boolean) => {
    qualityPendingRef.current = pending
    setQualityPending(pending)
    workspaceNotify.current()
  }, [])
  const activeAgentOwner = useRef<{
    projectId: string | undefined
    generation: number | undefined
  }>({
    projectId: tasks?.project?.projectId,
    generation: tasks?.generation,
  })
  useEffect(() => {
    activeAgentOwner.current = {
      projectId: tasks?.project?.projectId,
      generation: tasks?.generation,
    }
  }, [tasks?.project?.projectId, tasks?.generation])
  // 按 projectId 读取 localStorage 中的“仅 UI 披露偏好”镜像（FR-005）。
  // 这里不写项目数据、不发起 ChangeSet；真实模式由宿主 setAgentMode 持久化。
  useEffect(() => {
    const projectId = tasks?.project?.projectId
    if (!projectId) {
      agentModeMirror.current = ''
      return
    }
    const key = `ontolearn.agent.mode.${projectId}:${tasks?.generation ?? ''}`
    if (agentModeMirror.current === key) return
    agentModeMirror.current = key
    const mode = readAgentModeMirror(projectId)
    agentContextStore.setMode(mode)
  }, [tasks?.project?.projectId, tasks?.generation])
  const onAgentModeChange = useCallback(
    async (mode: AgentMode) => {
      const projectId = tasks?.project?.projectId
      const generation = tasks?.generation
      if (!projectId) {
        setProjectNotice('尚未打开项目；助手模式未改变。')
        throw new Error('NO_PROJECT')
      }
      const ownsCurrentProject = () =>
        activeAgentOwner.current.projectId === projectId &&
        activeAgentOwner.current.generation === generation
      // The host is the only authority: the local mirror is only updated
      // after the host really persisted the new mode.
      const result = await persistAgentMode({
        host: async (target, next) => {
          const reply = await window.ontolearn?.setAgentMode({ projectId: target, mode: next })
          if (!reply) return { ok: false as const, code: 'AGENT_MODE_UNAVAILABLE' }
          return reply.ok ? { ok: true as const } : { ok: false as const, code: reply.error.code }
        },
        projectId,
        mode,
        apply: (next) => {
          writeAgentModeMirror(projectId, next)
          if (ownsCurrentProject()) agentContextStore.setMode(next)
        },
      })
      if (!result.ok) {
        if (ownsCurrentProject()) setProjectNotice(`助手模式未改变（${result.code}）。`)
        throw new Error(result.code)
      }
    },
    [tasks?.project?.projectId, tasks?.generation],
  )
  const onOntologyDirty = useCallback((dirty: boolean) => {
    ontologyDirty.current = dirty
    workspaceNotify.current()
  }, [])
  const freezeWorkspace = useCallback((value: boolean) => {
    frozen.current = value
    setWorkspaceFrozen(value)
  }, [])
  useEffect(() => {
    // One strictly serial first-boot sequence. The engine's mainline reply
    // receiver settles exactly one mainline call at a time, so the management
    // channel (project:management-pending / catalog / state) and the restore
    // channel (project:restore-pending) must never overlap.
    let active = true
    const releases: Array<() => void> = []
    if (management) {
      releases.push(
        management.subscribe(() => {
          setManagementState(management.getSnapshot())
          workspaceNotify.current()
        }),
      )
    }
    if (checkpointCtl) {
      releases.push(
        checkpointCtl.subscribe(() => {
          setCheckpointState(checkpointCtl.getSnapshot())
          workspaceNotify.current()
        }),
      )
    }
    if (learningCtl) {
      releases.push(
        learningCtl.subscribe(() => {
          setLearningState(learningCtl.getSnapshot())
          workspaceNotify.current()
        }),
      )
    }
    // Both handlers are registered synchronously, so no apply event can be
    // missed while the serial initialization below is still running.
    management?.setAppliedHandler((receipt) => {
      // The old operation owns its receipt, never a newer selected workspace.
      if (receipt.kind === 'trash' && current.current?.project?.projectId === receipt.projectId) {
        retireOntology()
        disconnectQuery()
        readyWorkspace.current = undefined
        current.current = undefined
        setTasks(undefined)
        management?.select(undefined)
        // The checkpoint list belongs to the trashed project: clear the
        // selection only. The management controller refreshes its own catalog
        // and selected state after this callback returns, so no checkpoint
        // request may be started from here.
        checkpointCtl?.select(undefined)
        setCheckpointsDrawerOpen(false)
        setPrimaryView('projects')
      }
      // Metadata-only edits preserve the editor instance and its draft. The
      // controller reads current metadata; no domain restore or remount occurs.
      workspaceNotify.current()
    })
    checkpointCtl?.setAppliedHandler((result) => {
      // The restored workspace projection is reloaded through the real open
      // path; the old editor/draft instances are retired, never mutated.
      workspaceNotify.current()
      // Monotonic nonce: applying twice to the same project must retrigger
      // the open/refresh effect even though the projectId string is equal.
      setCheckpointApplied((previous) => ({
        projectId: result.projectId,
        nonce: (previous?.nonce ?? 0) + 1,
      }))
    })
    // The boot sequence is shared across mounts: a second concurrent run must
    // never restart the restore channel while the management channel is still
    // settling, which is exactly the collision the single-concurrency model
    // rejects with PERMISSION_DENIED.
    bootActive.current = true
    boot.current ??= (async () => {
      // The management channel settles completely before the restore channel
      // starts, so project:restore-pending can never collide with
      // project:management-pending or the management catalog read.
      await management?.initialize()
      // A torn-down view must not start the restore channel. The flag is shared
      // on purpose: a StrictMode remount re-arms it before this continuation
      // runs, so the restore channel is never left uninitialized.
      if (!bootActive.current) return
      await checkpointCtl?.initialize()
    })().catch(() => {})
    void boot.current.then(() => {
      // Publish the settled state even when no listener notification arrived.
      if (!active) return
      if (management) setManagementState(management.getSnapshot())
      if (checkpointCtl) setCheckpointState(checkpointCtl.getSnapshot())
      // The first-boot readiness gate opens once the whole sequence settled.
      setCheckpointBooted(true)
    })
    return () => {
      active = false
      bootActive.current = false
      for (const release of releases) release()
    }
  }, [management, checkpointCtl, learningCtl, retireOntology, disconnectQuery])
  useEffect(() => {
    // No selected project: clear the checkpoint selection synchronously. The
    // project-bound list refresh is serialized inside the open/create/restore
    // admission tail, so it never races the workspace auto-read.
    if (!tasks?.project?.projectId) {
      checkpointCtl?.select(undefined)
      learningCtl?.select(undefined)
      // Microtask avoids synchronous setState in effect body (react-hooks/set-state-in-effect);
      // re-check current ref so a rapid project switch never clears the new project's snapshot.
      queueMicrotask(() => {
        if (!current.current?.project?.projectId) setQueryDomainSnapshot(undefined)
      })
    }
  }, [checkpointCtl, learningCtl, tasks?.project?.projectId])
  useEffect(() => {
    // The active project's query workspace publishes its own last real read
    // (读取项目与持久工作草稿 or a settled commit/execute receipt re-read).
    // Recording the real projectRevision keeps cross-workspace freshness
    // comparisons monotonic; no background RPC starts here.
    if (!queryController) return
    return queryController.subscribe(() => {
      const read = queryController.getSnapshot().read
      if (!read) return
      setQueryDomainSnapshot((old) =>
        old &&
        old.projectId === read.projectId &&
        old.snapshotId === read.inputSnapshotId &&
        old.revision === read.domain.projectRevision
          ? old
          : {
              projectId: read.projectId,
              snapshotId: read.inputSnapshotId,
              revision: read.domain.projectRevision,
            },
      )
    })
  }, [queryController])
  useEffect(() => {
    if (!checkpointApplied) return
    // Reload the restored workspace through the real open path after the
    // applying event settles; a microtask keeps setState out of the effect body.
    // openProject already settles the management and checkpoint tail in one
    // strict order, so no extra concurrent refresh belongs here.
    const pending = checkpointApplied
    queueMicrotask(() => {
      void openProject(pending.projectId)
    })
  }, [checkpointApplied]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    let live = true
    const progressBuffer = pendingProgress.current
    const stop = window.ontolearn?.onTaskUpdate((update) => {
      if (documentLeaving.current || !live || update.generation < latestGeneration.current) return
      const view = current.current
      if (update.kind === 'connection') {
        if (
          view &&
          update.generation === view.generation &&
          view.project?.projectId !== update.projectId
        )
          return
        retireOntology()
        disconnectQuery()
        readyWorkspace.current = undefined
        latestGeneration.current = update.generation
        connectionEpoch.current++
        uncertain.current = true
        progressBuffer.clear()
        if (view?.project?.projectId === update.projectId)
          updateTasks({ ...view, generation: update.generation })
        else {
          current.current = undefined
          setTasks(undefined)
        }
        setConnection(update)
        setResult({ ok: false, error: update.error })
        setTaskError(undefined)
        setProgress({})
        setSummaries({})
        return
      }
      if (update.kind === 'restored') {
        void applyRestored(update.view)
        return
      }
      if (update.progress) progressBuffer.remember(update)
      if (
        uncertain.current ||
        !view ||
        update.generation !== view.generation ||
        update.job.projectId !== view.project?.projectId
      )
        return
      const old = view.jobs.find((job) => job.jobId === update.job.jobId)
      if (!old || update.job.stateVersion < old.stateVersion) return
      if (update.progress && update.job.stateVersion === old.stateVersion) {
        setProgress((previous) => ({ ...previous, [old.jobId]: update.progress! }))
        return
      }
      if (update.job.stateVersion === old.stateVersion) return
      progressBuffer.forget(old.jobId)
      setProgress((previous) => {
        const next = { ...previous }
        delete next[old.jobId]
        return next
      })
      updateTasks({
        ...view,
        jobs: view.jobs.map((job) => (job.jobId === update.job.jobId ? update.job : job)),
      })
    })
    const initialSerial = contextSerial.current
    void window.ontolearn
      ?.restoreTasks()
      .then((response) => {
        if (documentLeaving.current || !live || initialSerial !== contextSerial.current) return
        if (response.ok) void applyRestored(response.data)
        else if (!current.current) setTaskError(response.error)
      })
      .catch(() => {
        /* 初始恢复失败时保持无项目状态；显式操作会给出可见错误。 */
      })
    return () => {
      live = false
      stop?.()
      progressBuffer.clear()
      for (const job of current.current?.jobs ?? [])
        void window.ontolearn?.unsubscribeJob(job.jobId, current.current!.generation)
    }
  }, [applyRestored, updateTasks, retireOntology, disconnectQuery])
  useEffect(() => {
    const pageLeaving = () => {
      documentLeaving.current = true
      management?.close()
      checkpointCtl?.close()
      learningCtl?.close()
      retireOntology()
      disconnectQuery()
      readyWorkspace.current = undefined
    }
    window.addEventListener('pagehide', pageLeaving)
    return () => {
      window.removeEventListener('pagehide', pageLeaving)
      // Reversible cleanup supports StrictMode. Selection/document events use retire.
      ontologyOwner.current?.session.dispose()
    }
  }, [management, checkpointCtl, learningCtl, retireOntology, disconnectQuery])
  async function loadSummary(job: import('@ontolearn/contracts').JobView) {
    const bridge = window.ontolearn
    if (!bridge || !job.resultRef) return
    const generation = current.current?.generation
    const metadata = await bridge.getResult(job.resultRef.resultId)
    if (current.current?.generation !== generation) return
    if (!metadata.ok) {
      setTaskError(metadata.error)
      return
    }
    const page = await bridge.getResultPage({
      resultId: job.resultRef.resultId,
      pageSize: 20,
      cursor: null,
    })
    if (current.current?.generation !== generation) return
    if (!page.ok) {
      setTaskError(page.error)
      return
    }
    const label =
      metadata.data.state === 'stale'
        ? '结果已过期；显示原输入的历史计算。'
        : metadata.data.state === 'historical'
          ? '历史结果；不代表当前项目状态。'
          : '当前结果。'
    setSummaries((old) => ({ ...old, [job.jobId]: `${label}${resultSummary(page.data, job)}` }))
  }
  const [checking, setChecking] = useState(false)
  async function checkEngine() {
    const generation = latestGeneration.current
    const epoch = connectionEpoch.current
    const acceptsReply = () =>
      generation === latestGeneration.current && epoch === connectionEpoch.current
    setChecking(true)
    try {
      const response = window.ontolearn
        ? await window.ontolearn.getEngineHealth()
        : {
            ok: false as const,
            error: safeError({
              code: 'ENGINE_EXITED',
              messageKey: 'engine.exited',
              params: {},
              retryable: true,
            }),
          }
      if (acceptsReply()) setResult(response)
    } catch {
      if (acceptsReply()) setResult({ ok: false, error: safeError(undefined) })
    } finally {
      setChecking(false)
    }
  }
  const learningTasks = learningState?.learning?.tasks
  const learningBlocked = Boolean(learningState?.busy)
  // 跨工作区一致性：同一打开项目的全部快照候选（项目读取、本体会话、查询
  // 工作台、学习读取）中取 projectRevision 最大者，避免旧缓存把新提交误标过期。
  const activeProjectId = tasks?.project?.projectId
  const currentDomainSnapshotId = pickLatestDomainSnapshotId(activeProjectId, [
    tasks?.project
      ? {
          projectId: tasks.project.projectId,
          snapshotId: tasks.project.inputSnapshotId,
          revision: tasks.project.projectRevision,
        }
      : undefined,
    sessionDomainSnapshot,
    queryDomainSnapshot,
    qualityDomainSnapshot,
    learningState?.learning
      ? {
          projectId: learningState.learning.projectId,
          snapshotId: learningState.learning.domainSnapshotRef,
          revision: learningState.learning.domainRevision,
        }
      : undefined,
  ])
  const activeFixture =
    fixtureProposal?.diff.preview.projectId === activeProjectId &&
    fixtureProposal?.generation === tasks?.generation
      ? fixtureProposal
      : undefined
  const activeLocation =
    qualityLocation?.projectId === activeProjectId &&
    qualityLocation?.generation === tasks?.generation
      ? qualityLocation
      : undefined
  const operationBusy = projectBusy || qualityPending || fixtureBusy
  const projectControlsBusy = operationBusy || connectedUnresolved || Boolean(activeFixture)
  const learningDisabled =
    operationBusy ||
    connectedUnresolved ||
    workspaceFrozen ||
    managementBlocked ||
    checkpointBlocked ||
    learningBlocked ||
    Boolean(connection)

  const activeProject = tasks?.project
  const connectedBridge = window.ontolearn
  const connectedContext =
    activeProject && tasks
      ? {
          projectId: activeProject.projectId,
          revision: activeProject.projectRevision,
          inputSnapshotId: activeProject.inputSnapshotId,
          disabled:
            workspaceFrozen ||
            managementBlocked ||
            checkpointBlocked ||
            fixtureBusy ||
            Boolean(activeFixture),
        }
      : undefined

  function locateQualityFinding(targets: QualityFindingDTO['targets'], finding: QualityFindingDTO) {
    if (!activeProjectId || !tasks || learningDisabled || activeFixture) return
    const module = targets.subject ? 'ontology' : 'quality'
    setQualityLocation({
      projectId: activeProjectId,
      generation: tasks.generation,
      module,
      finding,
    })
    selectWorkspace(module)
  }
  function locationBanner(module: WorkspaceModule) {
    if (activeLocation?.module !== module) return null
    const { targets, sourceShape } = activeLocation.finding
    return (
      <aside className="quality-location" data-testid="quality-locate-target" role="status">
        <strong>验证问题定位</strong>
        <dl>
          {targets.subject && (
            <>
              <dt>主体</dt>
              <dd>{targets.subject}</dd>
            </>
          )}
          {targets.predicate && (
            <>
              <dt>属性</dt>
              <dd>{targets.predicate}</dd>
            </>
          )}
          {targets.object && (
            <>
              <dt>对象</dt>
              <dd>{targets.object}</dd>
            </>
          )}
          {sourceShape && (
            <>
              <dt>约束形状</dt>
              <dd>{sourceShape}</dd>
            </>
          )}
        </dl>
        <button type="button" onClick={() => setQualityLocation(undefined)}>
          关闭定位
        </button>
      </aside>
    )
  }
  function reportFixtureStatus(taskId: LearningFixtureTaskId, text: string) {
    setFixtureStatus({
      projectId: readyWorkspace.current?.project?.projectId ?? activeProjectId,
      taskId,
      text,
    })
  }
  async function runFixtureAction(taskId: LearningFixtureTaskId, work: () => Promise<void>) {
    if (fixtureBusyRef.current || learningDisabled) return
    fixtureBusyRef.current = true
    setFixtureBusy(true)
    setFixtureStatus(undefined)
    workspaceNotify.current()
    try {
      await work()
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : 'UNKNOWN'
      reportFixtureStatus(
        taskId,
        message === 'LEARNING_FIXTURE_REQUIRES_G_BASE'
          ? '请从设备运维示例打开 G-base，再载入本关初始数据。'
          : `本关初始数据操作未完成（${message}）。`,
      )
    } finally {
      fixtureBusyRef.current = false
      setFixtureBusy(false)
      workspaceNotify.current()
    }
  }
  function requireFixtureContext(
    projectId: string,
    generation: number,
    allowSuccessorGeneration = false,
    expectedEpoch = connectionEpoch.current,
  ) {
    const view = readyWorkspace.current
    const generationMatches = allowSuccessorGeneration
      ? view?.generation !== undefined && view.generation >= generation
      : view?.generation === generation
    if (
      documentLeaving.current ||
      uncertain.current ||
      frozen.current ||
      management?.unresolved ||
      checkpointCtl?.unresolved ||
      !generationMatches ||
      connectionEpoch.current !== expectedEpoch ||
      view?.project?.projectId !== projectId ||
      current.current?.project?.projectId !== projectId
    )
      throw new Error('PERMISSION_DENIED')
  }
  function loadTaskFixture(taskId: LearningFixtureTaskId) {
    const bridge = window.ontolearn
    if (!bridge || !activeProjectId || activeFixture) return
    if (workspaceStatus.dirty || workspaceStatus.unresolved) {
      reportFixtureStatus(taskId, '请先处理当前工作区未保存或未结算的编辑。')
      return
    }
    void runFixtureAction(taskId, async () => {
      // Reuse the existing project admission tail for transfer attempts.
      let projectId = activeProjectId
      if (taskId !== 'quality') {
        const opened = await createProject(false, {
          name: taskId === 'transfer-repair' ? '迁移练习 · 设备质量修复' : '迁移练习 · 设备分类',
          initialWorkspace: 'quality',
          startAttemptTaskId: taskId,
        })
        if (!opened) throw new Error('PROJECT_NOT_OPEN')
        projectId = opened
      } else {
        retireOntology()
        disconnectQuery()
        selectedModule.current = 'quality'
        setWorkspaceModule('quality')
        agentContextStore.setModule(toAgentModule('quality'))
        setPrimaryView('workspace')
      }
      const view = readyWorkspace.current
      if (!view || view.project?.projectId !== projectId) throw new Error('PROJECT_NOT_OPEN')
      const generation = view.generation
      const diff = await prepareLearningTaskFixture(bridge, projectId, taskId, () =>
        requireFixtureContext(projectId, generation),
      )
      if (diff) setFixtureProposal({ taskId, generation, diff, operationId: crypto.randomUUID() })
      else reportFixtureStatus(taskId, '本关初始数据已载入。')
    })
  }
  function commitTaskFixture(proposal: FixtureProposal) {
    const epoch = connectionEpoch.current
    const bridge = window.ontolearn
    if (!bridge) return
    void runFixtureAction(proposal.taskId, async () => {
      const projectId = proposal.diff.preview.projectId
      const requireCurrent = () =>
        requireFixtureContext(projectId, proposal.generation, false, epoch)
      const requirePostCommitCurrent = () =>
        requireFixtureContext(projectId, proposal.generation, true, epoch)
      const job = await commitLearningTaskFixture(
        bridge,
        proposal.diff,
        proposal.operationId,
        requireCurrent,
      )
      requirePostCommitCurrent()
      setFixtureProposal(undefined)
      if (job.state !== 'succeeded') throw new Error(job.error?.code ?? job.state)
      const read = await bridge.readProject({ editor: 'quality' })
      requirePostCommitCurrent()
      if (!read.ok) throw new Error(read.error.code)
      if (read.data.projectId !== projectId) throw new Error('PERMISSION_DENIED')
      setQualityDomainSnapshot({
        projectId,
        snapshotId: read.data.inputSnapshotId,
        revision: read.data.domain.projectRevision,
      })
      await learningCtl?.selectAndRefresh(projectId)
      requirePostCommitCurrent()
      reportFixtureStatus(proposal.taskId, '本关初始数据已载入。')
    })
  }
  function openMentorForTask(taskId?: string) {
    if (taskId) learningCtl?.focusTask(taskId)
    setActiveRailTab('mentor')
    setRailOpen(true)
    if (readyWorkspace.current?.project) {
      if (taskId) selectWorkspace(workspaceForLearningTask(taskId))
      else setPrimaryView('workspace')
    }
  }
  /** Offline Agent actions really run through the learning controller. */
  async function runAgentLocalAction(action: AgentAction) {
    setActiveRailTab('mentor')
    setRailOpen(true)
    if (!learningCtl) return
    if (action === 'hint') await learningCtl.requestHint()
    else if (action === 'demonstrate') await learningCtl.requestDemonstration()
    else if (action === 'check') await learningCtl.checkTask()
  }
  /** After a real Agent or workspace commit, restore() refreshes project, checkpoints, and learning before updating UI state. */
  async function refreshAfterAgentCommit() {
    await restore()
  }
  function continueLearningTask() {
    const snapshot = learningCtl?.getSnapshot()
    const states = snapshot?.learning?.tasks
    const next =
      states &&
      offlineCourse.tasks.find(
        (course) => !states.find((state) => state.taskId === course.id)?.operationComplete,
      )
    openMentorForTask(next?.id ?? snapshot?.learning?.courseMeta.firstTask)
  }
  function startLearningExample() {
    // 打开后自动聚焦首任务并保持导师面板展开；项目创建仍走真实 createProject。
    learningCtl?.focusTask('business-ontology')
    setActiveRailTab('mentor')
    setRailOpen(true)
    void createProject(true, { initialWorkspace: 'ontology', enterWorkspace: true })
  }
  function resetLearningGBase(taskId: string) {
    // 独立还原 G-base：新建独立练习项目并立刻开始该任务的新 attempt。
    // 未保存/未结算的编辑按既有破坏性操作规则拦截；创建锁与准入保护全部
    // 由 createProject 自身执行，不修改任何已有项目。
    if (learningDisabled || learningCtl?.unresolved) return
    if (workspaceStatus.dirty || workspaceStatus.unresolved) {
      setProjectNotice('当前工作区仍有未保存或未结算的编辑；请先保存或放弃后再独立还原 G-base。')
      return
    }
    learningCtl?.focusTask(taskId)
    setActiveRailTab('mentor')
    setRailOpen(true)
    void createProject(true, {
      initialWorkspace: workspaceForLearningTask(taskId),
      startAttemptTaskId: taskId,
      enterWorkspace: true,
    })
  }
  const completedTaskCount = offlineCourse.tasks.filter(
    (task) => learningTasks?.find((item) => item.taskId === task.id)?.operationComplete,
  ).length
  const transferSuccessCount = offlineCourse.tasks.filter(
    (task) =>
      task.transfer &&
      learningTasks?.find((item) => item.taskId === task.id)?.independentTransferSuccess,
  ).length
  const selectedPortalGlossary =
    offlineGlossary.find((entry) => entry.term === portalTerm) ?? offlineGlossary[0]!
  const workspaceControlsDisabled =
    projectControlsBusy || Boolean(connection) || workspaceFrozen || managementBlocked

  return (
    <div
      className="app-shell"
      data-workspace-mode={managementState?.selected?.metadata.mode ?? 'guided'}
      data-primary-view={primaryView}
    >
      <SidebarNav
        primaryView={primaryView}
        hasProject={Boolean(tasks?.project)}
        workspaceModule={workspaceModule}
        focusedTaskId={learningState?.focusedTaskId}
        workspaceControlsDisabled={workspaceControlsDisabled}
        qualityStepDisabled={learningDisabled || Boolean(activeFixture)}
        learningTasks={learningTasks}
        currentDomainSnapshotId={currentDomainSnapshotId}
        learningSnapshotRef={learningState?.learning?.domainSnapshotRef}
        engineHealth={result}
        connectionOffline={Boolean(connection)}
        mobileOpen={mobileNavOpen}
        onCloseMobile={() => setMobileNavOpen(false)}
        onSelectPrimaryView={(view) => setPrimaryView(view)}
        onSelectStep={(step) => selectCourseStep(step)}
      />
      <main id="overview">
        {primaryView === 'projects' && (
          <div className="portal-view" data-testid="portal-projects-view">
            <header className="portal-topbar">
              <div className="portal-topbar-left">
                <button
                  type="button"
                  className="mobile-nav-trigger"
                  data-testid="mobile-nav-toggle"
                  aria-label="打开导航菜单"
                  onClick={() => setMobileNavOpen(true)}
                >
                  ☰
                </button>
                <span>工作台 / 我的项目</span>
              </div>
              <div className="portal-topbar-actions">
                <button
                  type="button"
                  className="topbar-chip-btn"
                  onClick={() => setPrimaryView('learning')}
                >
                  学习路线图
                </button>
                <span className="badge">本地工作台</span>
              </div>
            </header>
            <section className="intro">
              <p className="eyebrow">LEARN. MODEL. UNDERSTAND.</p>
              <h1>
                把业务问题，
                <br />
                转化为可验证的知识。
              </h1>
              <p className="lead">从本体建模到情景推演，在一个本地项目中逐步学习与验证。</p>
            </section>
            <section className="health-panel" aria-labelledby="health-title">
              <div>
                <p className="eyebrow">DEVELOPMENT ENVIRONMENT</p>
                <h2 id="health-title">检查本地引擎连接</h2>
                <p>验证桌面应用与 Python 引擎的真实通信。</p>
              </div>
              <button
                onClick={() => void checkEngine()}
                disabled={checking || workspaceFrozen || managementBlocked}
              >
                {checking ? '正在检查…' : '检查本地引擎'}
                <span aria-hidden="true"> ↗</span>
              </button>
              <div className="health-result" role="status" aria-live="polite">
                {result ? (
                  result.ok ? (
                    `本地引擎已连接 · v${result.data.engineVersion} · 协议 v${result.data.protocolVersion}`
                  ) : (
                    <ErrorDetails error={result.error} context="health" />
                  )
                ) : (
                  '尚未检查。'
                )}
              </div>
            </section>
            {tasks?.project && (
              <section className="active-project-banner" aria-label="当前已打开项目">
                <div className="active-project-banner-meta">
                  <strong>
                    当前项目：{managementState?.selected?.metadata.name ?? '已打开项目'}
                  </strong>
                  <span>· 版本 {tasks.project.projectRevision}</span>
                </div>
                <button
                  type="button"
                  data-testid="enter-active-workspace"
                  onClick={() => setPrimaryView('workspace')}
                >
                  进入当前工作台 →
                </button>
              </section>
            )}
            <section
              className="project-library"
              aria-labelledby="project-library-title"
              data-testid="project-library"
            >
              <h2 id="project-library-title">我的项目</h2>
              <p>在本机创建项目，或打开已保存的项目继续编辑。无需配置模型 API。</p>
              <div className="project-quickstart" aria-label="首次启动入口">
                <button
                  type="button"
                  data-testid="learning-start-example"
                  disabled={learningDisabled || hasCreateIntent}
                  onClick={startLearningExample}
                >
                  从设备运维案例开始
                </button>
                <button
                  type="button"
                  className="topbar-chip-btn"
                  disabled={
                    projectControlsBusy ||
                    workspaceFrozen ||
                    managementBlocked ||
                    checkpointBlocked ||
                    learningBlocked
                  }
                  onClick={() => void listProjects()}
                >
                  打开已有项目
                </button>
                <button
                  type="button"
                  className="topbar-chip-btn"
                  onClick={() => setShowIntroduction(true)}
                >
                  查看快速介绍
                </button>
              </div>
              {showIntroduction && (
                <section role="dialog" aria-label="快速介绍" className="project-confirmation">
                  <h3>从本机项目开始</h3>
                  <p>
                    先选择空白项目或设备运维示例，再进入本体构建与查询。已提交修改保存在当前项目库；表单中的未提交编辑需先预览和确认。
                  </p>
                  <p>
                    项目可以重命名、归档，或复制当前已提交状态。删除会移至回收站，恢复不会续跑旧任务。完整项目包导出可在「导出与迁移」模块执行。
                  </p>
                  <p>引导模式显示逐步说明；辅助模式收起说明。两者使用相同编辑器与项目数据。</p>
                  <button type="button" onClick={() => setShowIntroduction(false)}>
                    关闭介绍
                  </button>
                </section>
              )}
              <form
                onSubmit={(event) => {
                  event.preventDefault()
                  void createProject()
                }}
              >
                <label htmlFor="project-name">项目名称</label>
                <input
                  id="project-name"
                  data-testid="project-name"
                  value={projectName}
                  onChange={(event) => setProjectName(event.target.value)}
                  maxLength={4096}
                  disabled={
                    projectControlsBusy ||
                    hasCreateIntent ||
                    workspaceFrozen ||
                    managementBlocked ||
                    learningBlocked
                  }
                  required
                />
                <button
                  type="submit"
                  data-testid="project-create"
                  disabled={
                    projectControlsBusy ||
                    !projectName.trim() ||
                    workspaceFrozen ||
                    managementBlocked ||
                    checkpointBlocked ||
                    learningBlocked
                  }
                >
                  {hasCreateIntent ? '核对创建结果' : '新建空白项目'}
                </button>
                <button
                  type="button"
                  data-testid="project-create-example"
                  disabled={
                    projectControlsBusy ||
                    hasCreateIntent ||
                    workspaceFrozen ||
                    managementBlocked ||
                    checkpointBlocked ||
                    learningBlocked
                  }
                  onClick={() => void createProject(true)}
                >
                  从设备运维示例开始
                </button>
                {!management && (
                  <button
                    type="button"
                    data-testid="project-list-refresh"
                    onClick={() => void listProjects()}
                    disabled={projectControlsBusy || checkpointBlocked || learningBlocked}
                  >
                    刷新项目列表
                  </button>
                )}
              </form>
              <div data-testid="project-status-notice" role="status" aria-live="polite">
                {projectBusy ? '正在处理…' : projectNotice}
              </div>
              {tasks?.project && (
                <p data-testid="selected-project-version">
                  当前项目版本 {tasks.project.projectRevision}
                </p>
              )}
              {!management && catalog && (
                <>
                  <ul>
                    {catalog.items.map((item) => (
                      <li key={item.projectId}>
                        <span>
                          {item.metadata.name ?? '未命名项目'} · 版本 {item.domainRevision}
                          {item.metadata.archived ? ' · 已归档' : ''}
                        </span>
                        <button
                          type="button"
                          data-testid="project-open"
                          data-project-id={item.projectId}
                          disabled={projectControlsBusy || learningBlocked}
                          onClick={() => void openProject(item.projectId)}
                        >
                          打开
                        </button>
                      </li>
                    ))}
                  </ul>
                  {catalog.total === 0 && <p>暂无项目。可以先新建空白项目。</p>}
                  {catalog.nextCursor && (
                    <button
                      type="button"
                      disabled={projectControlsBusy || learningBlocked}
                      onClick={() => void listProjects(catalog.nextCursor)}
                    >
                      下一页
                    </button>
                  )}
                </>
              )}
              {management && (
                <ProjectManagementPanel
                  controller={management}
                  disabled={
                    projectControlsBusy ||
                    workspaceFrozen ||
                    Boolean(connection) ||
                    checkpointBlocked ||
                    learningBlocked
                  }
                  destructiveBlocked={workspaceStatus.dirty || workspaceStatus.unresolved}
                  openProject={(id) => void openProject(id)}
                />
              )}
              {checkpointCtl && (
                <ProjectCheckpointRestorePanel
                  controller={checkpointCtl}
                  disabled={
                    projectControlsBusy ||
                    workspaceFrozen ||
                    Boolean(connection) ||
                    managementBlocked ||
                    checkpointBlocked ||
                    learningBlocked
                  }
                  destructiveBlocked={workspaceStatus.dirty || workspaceStatus.unresolved}
                />
              )}
              {window.ontolearn?.getLibraryLocation && (
                <LibraryLocationPanel
                  bridge={window.ontolearn}
                  disabled={projectControlsBusy || managementBlocked || learningBlocked}
                  report={reportWorkspace}
                  freeze={freezeWorkspace}
                />
              )}
              {projectError && <ErrorDetails error={projectError} context="task" />}
            </section>
          </div>
        )}

        {primaryView === 'learning' && (
          <div className="portal-view" data-testid="portal-learning-view">
            <header className="portal-topbar">
              <div className="portal-topbar-left">
                <button
                  type="button"
                  className="mobile-nav-trigger"
                  data-testid="mobile-nav-toggle"
                  aria-label="打开导航菜单"
                  onClick={() => setMobileNavOpen(true)}
                >
                  ☰
                </button>
                <span>工作台 / 学习路线图</span>
              </div>
              <div className="portal-topbar-actions">
                <span className="learning-center-progress-pill">
                  已完成 {completedTaskCount} / {offlineCourse.tasks.length} · 独立迁移{' '}
                  {transferSuccessCount} / 2
                </span>
                <span className="learning-center-badge">离线课程 · 无需模型 API</span>
              </div>
            </header>
            <section
              id="learning-center"
              className="learning-center"
              data-testid="learning-center"
              aria-labelledby="learning-center-title"
            >
              <div className="learning-center-header">
                <h2 id="learning-center-title">六个模块，一条学习路径</h2>
                <span className="learning-center-badge">
                  离线课程 · 无需模型 API · 实操检查为准
                </span>
              </div>
              <p className="learning-center-meta">
                课程案例：{learningState?.learning?.courseMeta.case ?? offlineCourse.case} ·{' '}
                {learningState?.learning?.courseMeta.businessQuestion ??
                  offlineCourse.businessQuestion}
                {learningState?.learning?.courseMeta.manifestSha256
                  ? ` · 课程 ${learningState.learning.courseMeta.courseVersion} · manifest ${learningState.learning.courseMeta.manifestSha256.slice(0, 12)}`
                  : ` · 课程 ${offlineCourse.version}`}
              </p>
              <div className="learning-center-actions">
                <button
                  type="button"
                  data-testid="learning-start-example"
                  disabled={learningDisabled || hasCreateIntent}
                  onClick={startLearningExample}
                >
                  从设备运维案例开始
                </button>
                <button
                  type="button"
                  className="topbar-chip-btn"
                  data-testid="learning-continue-task"
                  disabled={learningDisabled || !tasks?.project}
                  onClick={continueLearningTask}
                >
                  继续当前任务
                </button>
              </div>
              <DualTrackRoadmapHeader
                selectedTrack={learningTrack}
                onSelectTrack={setLearningTrack}
                onOpenFoundationStep={(stepId) => {
                  setActiveFoundationStep(stepId)
                }}
              />
              <ol
                className="learning-roadmap-grid"
                data-active-foundation-step={activeFoundationStep}
                aria-label="学习路径概览"
              >
                {offlineCourse.tasks.map((task, ordinal) => {
                  const state = learningTasks?.find((item) => item.taskId === task.id)
                  const statusText = displayedCheckStatus(
                    state,
                    currentDomainSnapshotId,
                    learningState?.learning?.domainSnapshotRef,
                  )
                  return (
                    <li key={task.id}>
                      <button
                        type="button"
                        data-testid="learning-path-task"
                        data-task-id={task.id}
                        onClick={() => openMentorForTask(task.id)}
                      >
                        <div className="learning-roadmap-top">
                          <span className="learning-step-number">
                            STAGE {String(ordinal + 1).padStart(2, '0')}
                          </span>
                          <span
                            className="learning-step-status-pill"
                            data-testid="learning-path-status"
                            data-status={statusText}
                          >
                            {statusText}
                          </span>
                        </div>
                        <b>{task.module}</b>
                        <small className="learning-step-goal">{task.goal}</small>
                        <span className="learning-step-assist">
                          {state?.operationComplete
                            ? (mentorAssistanceText(state) ?? '')
                            : tasks?.project
                              ? '点击进入对应工作台并打开导师 →'
                              : '新建或打开案例后可联动实操'}
                        </span>
                      </button>
                    </li>
                  )
                })}
              </ol>
              <aside className="learning-portal-glossary" aria-label="随用随查术语速览">
                <h3>随用随查 · 核心术语边界</h3>
                <div className="learning-portal-glossary-chips">
                  {offlineGlossary.slice(0, 8).map((entry) => (
                    <button
                      key={entry.term}
                      type="button"
                      aria-pressed={selectedPortalGlossary.term === entry.term}
                      onClick={() => setPortalTerm(entry.term)}
                    >
                      {entry.term}
                    </button>
                  ))}
                </div>
                <div className="learning-portal-glossary-card">
                  <strong>{selectedPortalGlossary.term}</strong>
                  <p>{selectedPortalGlossary.plain}</p>
                  <p>
                    <b>本例：</b>
                    {selectedPortalGlossary.example}
                  </p>
                  <p>
                    <b>边界：</b>
                    {selectedPortalGlossary.boundary}
                  </p>
                </div>
              </aside>
            </section>
          </div>
        )}

        {primaryView === 'settings' && (
          <div className="portal-view" data-testid="portal-settings-view">
            <header className="portal-topbar">
              <div className="portal-topbar-left">
                <button
                  type="button"
                  className="mobile-nav-trigger"
                  data-testid="mobile-nav-toggle"
                  aria-label="打开导航菜单"
                  onClick={() => setMobileNavOpen(true)}
                >
                  ☰
                </button>
                <span>工作台 / 模型与隐私设置</span>
              </div>
              <div className="portal-topbar-actions">
                {tasks?.project && (
                  <button
                    type="button"
                    className="topbar-chip-btn"
                    onClick={() => setPrimaryView('workspace')}
                  >
                    返回当前工作台
                  </button>
                )}
              </div>
            </header>
            <ModelPanel
              key={activeProjectId ?? 'no-project'}
              jobs={tasks?.jobs ?? []}
              projectId={activeProjectId ?? null}
              onAgentModelChanged={() => setModelSyncVersion((value) => value + 1)}
            />
          </div>
        )}

        {tasks?.project && (
          <div className="workspace-shell" hidden={primaryView !== 'workspace'}>
            <TopContextBar
              visible={primaryView === 'workspace'}
              projectName={managementState?.selected?.metadata.name ?? undefined}
              projectRevision={tasks.project.projectRevision}
              projectBusy={projectBusy}
              projectNotice={projectNotice}
              workspaceModule={workspaceModule}
              focusedTaskId={learningState?.focusedTaskId}
              workspaceMode={managementState?.selected?.metadata.mode ?? 'guided'}
              railOpen={railOpen}
              checkpointsDrawerOpen={checkpointsDrawerOpen}
              jobsDrawerOpen={jobsDrawerOpen}
              jobCount={tasks.jobs.length}
              onOpenMobileNav={() => setMobileNavOpen(true)}
              onBackToProjects={() => setPrimaryView('projects')}
              onToggleCheckpointsDrawer={() => setCheckpointsDrawerOpen((old) => !old)}
              onToggleJobsDrawer={() => setJobsDrawerOpen((old) => !old)}
              onToggleRail={() => setRailOpen((old) => !old)}
            />
            <WorkspaceDrawers
              visible={primaryView === 'workspace'}
              checkpointsOpen={checkpointsDrawerOpen}
              jobsOpen={jobsDrawerOpen}
              hasRecovery={Boolean(checkpointState && checkpointState.recovery.length > 0)}
              checkpointCtl={checkpointCtl}
              checkpointsDisabled={
                projectControlsBusy ||
                workspaceFrozen ||
                Boolean(connection) ||
                managementBlocked ||
                checkpointBlocked ||
                learningBlocked
              }
              destructiveBlocked={workspaceStatus.dirty || workspaceStatus.unresolved}
              projectId={tasks.project.projectId}
              inputSnapshotId={tasks.project.inputSnapshotId}
              jobs={tasks.jobs}
              progress={progress}
              summaries={summaries}
              connectionOffline={Boolean(connection)}
              controlsBusy={projectControlsBusy}
              onCloseCheckpoints={() => setCheckpointsDrawerOpen(false)}
              onCloseJobs={() => setJobsDrawerOpen(false)}
              onRestoreTasks={() => void restore()}
              onCancelJob={(jobId) => {
                void window.ontolearn?.cancelJob(jobId).then((response) => {
                  if (!response.ok) setTaskError(response.error)
                  else void restore()
                })
              }}
              onInspectOperation={(job) => {
                void window.ontolearn?.getOperation(job.operationId).then((response) => {
                  if (!response.ok) setTaskError(response.error)
                  else
                    setSummaries((old) => ({
                      ...old,
                      [job.jobId]: response.data
                        ? `已提交 · 项目版本 ${Number(response.data.projectRevision)}`
                        : '未查到完整操作提交点；已提交轮次以任务持久记录为准。',
                    }))
                })
              }}
              onLoadSummary={(job) => void loadSummary(job)}
              renderJobError={(job) =>
                job.error ? <ErrorDetails error={job.error} context="task" /> : null
              }
            />
            <p className="guided-help">
              先编辑业务定义或查询，再查看完整差异并确认。项目设置不会改变领域结果；未提交表单需另外保存。
            </p>
            {workspaceFrozen && <p role="status">项目库切换确认期间，编辑与新操作已暂停。</p>}
            <div
              className="workspace-split"
              data-mentor-open={railOpen && !!tasks?.project ? 'true' : 'false'}
            >
              <div className="workspace-split-columns">
                <fieldset
                  className="workspace-freeze"
                  disabled={workspaceFrozen || managementBlocked}
                >
                  {workspaceModule === 'query' &&
                    queryController &&
                    tasks?.project?.projectId === queryController.projectId &&
                    !connection && (
                      <section id="query-workspace" aria-label="当前项目查询">
                        <QueryWorkspacePage
                          controller={queryController}
                          modelDraft={agentQueryDraft}
                        />
                      </section>
                    )}
                  {workspaceModule === 'ontology' &&
                    ontologyContext &&
                    tasks?.project?.projectId === ontologyContext.projectId &&
                    tasks.generation === ontologyContext.generation &&
                    !connection && (
                      <section id="ontology-workspace" aria-label="当前项目本体">
                        {locationBanner('ontology')}
                        <OntologyMainlinePage
                          session={ontologyContext.session}
                          contextKey={ontologyContext.contextKey}
                          onDirtyChange={onOntologyDirty}
                          onSelectedObjectChange={(ids) =>
                            agentContextStore.setSelectedObjectIds(ids)
                          }
                          extras={
                            <>
                              <ImportExportPanel
                                key={`${tasks.project?.projectId ?? ''}:${tasks.project?.projectRevision ?? ''}`}
                                projectId={tasks.project?.projectId ?? null}
                                projectRevision={tasks.project?.projectRevision ?? null}
                                onImported={() => void refreshAfterAgentCommit()}
                                onError={(message) => setProjectNotice(message)}
                              />
                              <DraftDiffPreview
                                key={`${tasks.project?.projectId ?? ''}:${tasks.generation}:${agentDraftPlan?.operationId ?? ''}`}
                                plan={agentDraftPlan}
                                projectId={tasks.project?.projectId ?? null}
                                label="Agent 本体草稿"
                                onCommitted={() => void refreshAfterAgentCommit()}
                                onError={(message) => setProjectNotice(message)}
                              />
                            </>
                          }
                        />
                      </section>
                    )}
                  {workspaceModule === 'quality' &&
                    tasks?.project &&
                    window.ontolearn?.getProjectQualityState &&
                    !connection &&
                    !projectBusy && (
                      <section id="quality-workspace" aria-label="当前项目质量与推导">
                        {locationBanner('quality')}
                        <QualityWorkspace
                          key={JSON.stringify([
                            tasks.project.projectId,
                            tasks.generation,
                            tasks.project.projectRevision,
                          ])}
                          projectId={tasks.project.projectId}
                          bridge={window.ontolearn}
                          validationScope={
                            qualityScopes[tasks.project.projectId] ?? 'asserted+derived'
                          }
                          onValidationScopeChange={(next) => {
                            const projectId = tasks.project?.projectId
                            if (!projectId) return
                            setQualityScopes((prev) =>
                              prev[projectId] === next ? prev : { ...prev, [projectId]: next },
                            )
                          }}
                          disabled={
                            workspaceFrozen ||
                            managementBlocked ||
                            checkpointBlocked ||
                            fixtureBusy ||
                            Boolean(activeFixture)
                          }
                          onDomainSnapshotUpdated={setQualityDomainSnapshot}
                          onLocateTarget={locateQualityFinding}
                          onPendingChange={onQualityPending}
                        />
                      </section>
                    )}
                  {isConnectedModule(workspaceModule) &&
                    connectedContext &&
                    connectedBridge &&
                    !connection &&
                    !projectBusy && (
                      <section
                        key={JSON.stringify([
                          workspaceModule,
                          connectedContext.projectId,
                          tasks?.generation,
                          connectedContext.revision,
                          connectedContext.inputSnapshotId,
                        ])}
                        id={`${workspaceModule}-workspace`}
                        aria-label={connectedModules[workspaceModule].title}
                      >
                        {workspaceModule === 'mapping' && (
                          <fieldset disabled={connectedContext.disabled}>
                            <MappingWorkspace
                              onStatus={onConnectedStatus}
                              {...connectedContext}
                              bridge={connectedBridge}
                              onCommitted={refreshAfterAgentCommit}
                            />
                          </fieldset>
                        )}
                        {workspaceModule === 'behavior' && (
                          <ConnectedBehaviorWorkspace
                            onStatus={onConnectedStatus}
                            {...connectedContext}
                            bridge={connectedBridge}
                          />
                        )}
                        {workspaceModule === 'scenario' && (
                          <ConnectedScenarioWorkspace
                            onStatus={onConnectedStatus}
                            {...connectedContext}
                            bridge={connectedBridge}
                          />
                        )}
                        {workspaceModule === 'transfer' && (
                          <TransferWorkspace
                            onStatus={onConnectedStatus}
                            {...connectedContext}
                            bridge={connectedBridge}
                            onImported={async () => {
                              if (management) await management.refresh()
                              else {
                                const reply = await connectedBridge.getProjectCatalog({
                                  pageSize: 64,
                                  cursor: null,
                                })
                                if (reply.ok) setCatalog(reply.data)
                              }
                            }}
                          />
                        )}
                      </section>
                    )}
                </fieldset>
                <UnifiedAssistantRail
                  open={railOpen}
                  activeTab={activeRailTab}
                  onSelectTab={(tab) => setActiveRailTab(tab)}
                  onClose={() => setRailOpen(false)}
                  projectId={tasks.project.projectId}
                  generation={tasks.generation}
                  projectRevision={tasks.project.projectRevision}
                  inputSnapshotId={tasks.project.inputSnapshotId}
                  learningCtl={learningCtl}
                  learningDisabled={learningDisabled}
                  currentDomainSnapshotId={currentDomainSnapshotId}
                  onOpenOntologyRepair={() => selectWorkspace('ontology')}
                  onOpenQueryWorkspace={() => selectWorkspace('query')}
                  onOpenQualityWorkspace={() => selectWorkspace('quality')}
                  onOpenCheckpoints={() => setCheckpointsDrawerOpen(true)}
                  onLoadTaskFixture={loadTaskFixture}
                  taskFixture={
                    activeFixture
                      ? {
                          taskId: activeFixture.taskId,
                          rows: activeFixture.diff.rows,
                          approve: () => commitTaskFixture(activeFixture),
                          discard: () => setFixtureProposal(undefined),
                        }
                      : undefined
                  }
                  taskFixtureStatus={
                    fixtureStatus?.projectId === activeProjectId &&
                    fixtureStatus?.taskId === learningState?.focusedTaskId
                      ? fixtureStatus?.text
                      : undefined
                  }
                  onResetToGBase={resetLearningGBase}
                  refreshCheckpoints={() => checkpointCtl?.refreshWhenIdle() ?? Promise.resolve()}
                  agentContext={agentContext}
                  modelSyncVersion={modelSyncVersion}
                  onModeChange={(mode) => onAgentModeChange(mode)}
                  onQueryDraft={(draft) =>
                    setAgentQueryArtifact({
                      projectId: tasks.project?.projectId ?? '',
                      generation: tasks.generation,
                      value: draft,
                    })
                  }
                  onDraftPlan={(plan) =>
                    setAgentDraftArtifact({
                      projectId: tasks.project?.projectId ?? '',
                      generation: tasks.generation,
                      value: plan,
                    })
                  }
                  onLocalAction={(action) => runAgentLocalAction(action)}
                />
              </div>
            </div>
          </div>
        )}
        {connection && (
          <section role="status" aria-label="引擎连接状态">
            <h2>
              {connection.state === 'offline'
                ? '引擎连接已离线；任务状态待对账'
                : '引擎连接中断；正在对账'}
            </h2>
            <p>任务卡片仅显示最后记录，当前状态尚未确认。不会重发写任务。</p>
            <p>已尝试 {connection.attempt}/3 次只读恢复。</p>
            <ErrorDetails error={connection.error} context="task" />
            <button onClick={() => void restore()} disabled={connection.state === 'reconnecting'}>
              重新连接并对账
            </button>
          </section>
        )}
        {taskError && !connection && <ErrorDetails error={taskError} context="task" />}
        <footer>
          需求基准 PRD V0.6
          <span>本地工作台全模块已集成；实验与验收边界以当前项目版本与真实检查记录为准。</span>
        </footer>
      </main>
    </div>
  )
}

function ErrorDetails({ error, context }: { error: SafeError; context: 'health' | 'task' }) {
  const text = explainError(error, context)
  return (
    <div className="error-details">
      <p>发生了什么：{text.what}</p>
      <p>为什么发生：{text.why}</p>
      <p>如何修复：{text.fix}</p>
      <p>相关知识：{text.detail}</p>
    </div>
  )
}
