import { useCallback, useEffect, useRef, useState } from 'react'
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
} from '@ontolearn/contracts'
import { explainError, jobStatus, resultSummary } from './task-presentation'
import { TaskProgressBuffer } from './task-progress'
import { QueryWorkspaceController, QueryWorkspacePage } from './query'
import { OntologyMainlinePage } from './ontology/OntologyMainlinePage'
import { OntologySession } from './ontology/mainline-session'
import { ontologyOperations } from './ontology/mainline-operations'
import type { OntologyMainlineBridge } from './ontology/mainline-api'
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
import { MentorPanel } from './learning/MentorPanel'
import { offlineCourse } from './learning/content'
import {
  commitLearningTaskFixture,
  prepareLearningTaskFixture,
  type LearningFixtureTaskId,
} from './learning/task-fixture'
import { QualityWorkspace } from './quality/QualityWorkspace'
import { ModelPanel } from './ModelPanel'

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

type WorkspaceModule = 'query' | 'ontology' | 'quality'
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

const modules = [
  ['01', '定义业务概念', '本体构建'],
  ['02', '连接业务数据', '数据映射'],
  ['03', '向知识提问', '本体查询'],
  ['04', '检查并发现新知识', '知识推理'],
  ['05', '描述业务如何行动', '行为定义'],
  ['06', '比较不同方案', '沙盘推演'],
]

export function App() {
  const [showIntroduction, setShowIntroduction] = useState(false)
  const [workspaceFrozen, setWorkspaceFrozen] = useState(false)
  const frozen = useRef(false)
  const [workspaceStatus, setWorkspaceStatus] = useState({ dirty: false, unresolved: false })
  const workspaceNotify = useRef<() => void>(() => {})
  const ontologyDirty = useRef(false)
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
  // 导师面板默认收起；学习入口打开项目后自动展开（PRD 8.2）。
  const [mentorOpen, setMentorOpen] = useState(false)
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
    workspaceNotify.current()
    setOntologyContext(undefined)
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
    if (qualityPendingRef.current || fixtureBusyRef.current || hasCurrentFixtureProposal()) return
    if (
      libraryAdmissionBlocked({
        documentLeaving: documentLeaving.current,
        libraryBusy: libraryBusy.current,
        frozen: frozen.current,
        managementUnresolved: !!management?.unresolved,
      })
    )
      return
    if (uncertain.current || !readyWorkspace.current?.project) return
    if (selectedModule.current === module) return
    retireOntology()
    disconnectQuery()
    selectedModule.current = module
    setWorkspaceModule(module)
    activateWorkspace()
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
          previous.project?.projectId !== value.project?.projectId)
      ) {
        retireOntology()
        disconnectQuery()
      }
      // 本次恢复由 open/create 持有时等待其完整 management 尾段；自主恢复则
      // 在渲染前自行串行完成同等读取。selected-project-version 渲染之后不允许
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
    if (qualityPendingRef.current || fixtureBusyRef.current || hasCurrentFixtureProposal()) return
    const bridge = window.ontolearn
    if (documentLeaving.current || !bridge || libraryBusy.current || frozen.current) return
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
    if (qualityPendingRef.current || fixtureBusyRef.current || hasCurrentFixtureProposal()) return
    const bridge = window.ontolearn
    if (
      !bridge ||
      libraryAdmissionBlocked({
        documentLeaving: documentLeaving.current,
        libraryBusy: libraryBusy.current,
        frozen: frozen.current,
        managementUnresolved: !!management?.unresolved,
      })
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
    options?: { name?: string; initialWorkspace?: WorkspaceModule; startAttemptTaskId?: string },
  ) {
    if (
      qualityPendingRef.current ||
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
      })
    )
      return
    if (
      !createIntent.current &&
      (new TextEncoder().encode(name).length > 4096 || /[\uD800-\uDFFF]/u.test(name))
    ) {
      setProjectNotice('项目名称过长或包含无效字符，请修改后重试。')
      return
    }
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
        }
        await restore()
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
    return {
      dirty: ontologyDirty.current || queries.some((controller) => controller.getSnapshot().dirty),
      unresolved:
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
  const onQualityPending = useCallback((pending: boolean) => {
    qualityPendingRef.current = pending
    setQualityPending(pending)
    workspaceNotify.current()
  }, [])
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
  const projectControlsBusy = operationBusy || Boolean(activeFixture)
  const learningDisabled =
    operationBusy ||
    workspaceFrozen ||
    managementBlocked ||
    checkpointBlocked ||
    Boolean(connection)

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
    requestAnimationFrame(() => {
      document
        .querySelector('[data-testid="quality-locate-target"]')
        ?.scrollIntoView({ block: 'nearest' })
    })
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
    setMentorOpen(true)
    requestAnimationFrame(() => {
      document
        .querySelector('[data-testid="mentor-panel"]')
        ?.scrollIntoView({ block: 'start', behavior: 'auto' })
    })
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
    setMentorOpen(true)
    void createProject(true)
  }
  function resetLearningGBase(taskId: string) {
    // 独立还原 G-base：新建独立练习项目并立刻开始该任务的新 attempt。
    // 未保存/未结算的编辑按既有破坏性操作规则拦截；创建锁与准入保护全部
    // 由 createProject 自身执行，不修改任何已有项目。
    if (learningDisabled) return
    if (workspaceStatus.dirty || workspaceStatus.unresolved) {
      setProjectNotice('当前工作区仍有未保存或未结算的编辑；请先保存或放弃后再独立还原 G-base。')
      return
    }
    learningCtl?.focusTask(taskId)
    setMentorOpen(true)
    void createProject(true, {
      initialWorkspace: taskId === 'query' ? 'query' : 'ontology',
      startAttemptTaskId: taskId,
    })
  }
  return (
    <div
      className="app-shell"
      data-workspace-mode={managementState?.selected?.metadata.mode ?? 'guided'}
    >
      <aside className="sidebar">
        <div className="wordmark">
          <span className="brand-mark" aria-hidden="true">
            O
          </span>
          <strong>
            OntoLearn<span>STUDIO</span>
          </strong>
        </div>
        <div className="side-label">本体学习与落地工作台</div>
        <nav aria-label="工作台导航">
          <a href="#overview" aria-current="page">
            项目工作台 <span>↗</span>
          </a>
          <a href="#learning-center" data-testid="nav-learning-center">
            学习中心 <span>↗</span>
          </a>
          <a href="#model-settings">模型设置</a>
          <a href="#modules">
            模块规划 <span>06</span>
          </a>
          {tasks?.project && (
            <>
              <a
                href="#query-workspace"
                aria-current={workspaceModule === 'query' ? 'page' : undefined}
                aria-disabled={
                  projectControlsBusy || Boolean(connection) || workspaceFrozen || managementBlocked
                }
                onClick={(event) => {
                  event.preventDefault()
                  selectWorkspace('query')
                }}
              >
                本体查询
              </a>
              <a
                href="#ontology-workspace"
                aria-current={workspaceModule === 'ontology' ? 'page' : undefined}
                aria-disabled={
                  projectControlsBusy || Boolean(connection) || workspaceFrozen || managementBlocked
                }
                onClick={(event) => {
                  event.preventDefault()
                  selectWorkspace('ontology')
                }}
              >
                本体构建
              </a>
              <a
                href="#quality-workspace"
                aria-current={workspaceModule === 'quality' ? 'page' : undefined}
                aria-disabled={learningDisabled || Boolean(activeFixture)}
                onClick={(event) => {
                  event.preventDefault()
                  selectWorkspace('quality')
                }}
              >
                质量与推导
              </a>
            </>
          )}
        </nav>
        <div className="sidebar-note">
          <span className="status-dot" />
          本地优先
          <p>
            无需配置模型 API
            <br />
            即可启动开发环境
          </p>
        </div>
      </aside>
      <main id="overview">
        <header>
          <span>工作台 / 项目</span>
          <span className="badge">内部演示候选</span>
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
        <section
          id="learning-center"
          className="learning-center"
          data-testid="learning-center"
          aria-labelledby="learning-center-title"
        >
          <div className="learning-center-header">
            <h2 id="learning-center-title">学习中心</h2>
            <span className="learning-center-badge">离线课程 · 无需模型 API</span>
          </div>
          <p className="learning-center-meta">
            课程案例：{learningState?.learning?.courseMeta.case ?? offlineCourse.case} ·{' '}
            {learningState?.learning?.courseMeta.businessQuestion ?? offlineCourse.businessQuestion}
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
              data-testid="learning-continue-task"
              disabled={learningDisabled || !tasks?.project}
              onClick={continueLearningTask}
            >
              继续当前任务
            </button>
          </div>
          <ol className="learning-path" aria-label="学习路径概览">
            {offlineCourse.tasks.map((task, ordinal) => {
              const state = learningTasks?.find((item) => item.taskId === task.id)
              return (
                <li key={task.id}>
                  <button
                    type="button"
                    data-testid="learning-path-task"
                    data-task-id={task.id}
                    onClick={() => openMentorForTask(task.id)}
                  >
                    <span className="learning-step-number">
                      {String(ordinal + 1).padStart(2, '0')}
                    </span>
                    <span>
                      <b>{task.module}</b>
                      <small className="learning-step-goal">{task.goal}</small>
                    </span>
                    <span className="learning-step-badges">
                      <span data-testid="learning-path-status">
                        {displayedCheckStatus(
                          state,
                          currentDomainSnapshotId,
                          learningState?.learning?.domainSnapshotRef,
                        )}
                      </span>
                    </span>
                    <span className="learning-step-assist">
                      {state?.operationComplete ? (mentorAssistanceText(state) ?? '') : ''}
                    </span>
                  </button>
                </li>
              )
            })}
          </ol>
        </section>
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
              disabled={
                projectControlsBusy || workspaceFrozen || managementBlocked || checkpointBlocked
              }
              onClick={() => void listProjects()}
            >
              打开已有项目
            </button>
            <button type="button" onClick={() => setShowIntroduction(true)}>
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
                项目可以重命名、归档，或复制当前已提交状态。删除会移至回收站，恢复不会续跑旧任务。完整项目导出仍待接入。
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
                projectControlsBusy || hasCreateIntent || workspaceFrozen || managementBlocked
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
                checkpointBlocked
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
                checkpointBlocked
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
                disabled={projectControlsBusy || checkpointBlocked}
              >
                刷新项目列表
              </button>
            )}
          </form>
          <div role="status" aria-live="polite">
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
                      disabled={projectControlsBusy}
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
                  disabled={projectControlsBusy}
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
                projectControlsBusy || workspaceFrozen || Boolean(connection) || checkpointBlocked
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
                checkpointBlocked
              }
              destructiveBlocked={workspaceStatus.dirty || workspaceStatus.unresolved}
            />
          )}
          {window.ontolearn?.getLibraryLocation && (
            <LibraryLocationPanel
              bridge={window.ontolearn}
              disabled={projectControlsBusy || managementBlocked}
              report={reportWorkspace}
              freeze={freezeWorkspace}
            />
          )}
          {projectError && <ErrorDetails error={projectError} context="task" />}
        </section>
        {tasks?.project && (
          <p className="guided-help">
            先编辑业务定义或查询，再查看完整差异并确认。项目设置不会改变领域结果；未提交表单需另外保存。
          </p>
        )}
        {workspaceFrozen && <p role="status">项目库切换确认期间，编辑与新操作已暂停。</p>}
        <div
          className="workspace-split"
          data-mentor-open={mentorOpen && !!tasks?.project ? 'true' : 'false'}
        >
          {tasks?.project && (
            <div className="workspace-split-bar">
              <button
                type="button"
                data-testid="mentor-panel-toggle"
                onClick={() => setMentorOpen((value) => !value)}
              >
                {mentorOpen ? '收起导师面板' : '展开导师面板'}
              </button>
              <span className="mentor-muted">离线导师：任务卡、分级提示、检查与术语帮助。</span>
            </div>
          )}
          <div className="workspace-split-columns">
            <fieldset className="workspace-freeze" disabled={workspaceFrozen || managementBlocked}>
              {workspaceModule === 'query' &&
                queryController &&
                tasks?.project?.projectId === queryController.projectId &&
                !connection && (
                  <section id="query-workspace" aria-label="当前项目查询">
                    <QueryWorkspacePage controller={queryController} />
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
                  <button
                    onClick={() => void restore()}
                    disabled={connection.state === 'reconnecting'}
                  >
                    重新连接并对账
                  </button>
                </section>
              )}
              {tasks?.project && (
                <section className="health-panel" aria-label="后台任务状态">
                  <h2>后台任务</h2>
                  <p>窗口恢复后读取持久状态；不会重发写任务。</p>
                  <button
                    onClick={() => void restore()}
                    disabled={projectControlsBusy || Boolean(connection)}
                  >
                    刷新任务状态
                  </button>
                  {tasks.jobs.map((job) => (
                    <article key={job.jobId} data-testid="durable-job" data-job-id={job.jobId}>
                      <p>
                        {connection ? '最后记录：' : ''}
                        {jobStatus(job)} · 状态版本 {job.stateVersion}
                      </p>
                      <p>
                        输入快照 {job.inputSnapshotId.slice(0, 12)} ·
                        {job.inputSnapshotId === tasks.project?.inputSnapshotId
                          ? '当前输入'
                          : '历史输入；此任务保留原执行依据'}
                      </p>
                      {progress[job.jobId] &&
                        ['queued', 'running', 'cancelling'].includes(job.state) && (
                          <p>
                            阶段：
                            {
                              {
                                queued: '排队',
                                loading: '加载',
                                computing: '计算',
                                committing: '提交',
                                reconciling: '对账',
                              }[progress[job.jobId].stage]
                            }
                            {progress[job.jobId].total !== null
                              ? ` · ${progress[job.jobId].completed}/${progress[job.jobId].total}`
                              : ''}
                          </p>
                        )}
                      {job.error && <ErrorDetails error={job.error} context="task" />}
                      {['queued', 'running'].includes(job.state) && (
                        <button
                          disabled={Boolean(connection)}
                          onClick={() => {
                            void window.ontolearn?.cancelJob(job.jobId).then((response) => {
                              if (!response.ok) setTaskError(response.error)
                              else void restore()
                            })
                          }}
                        >
                          请求取消
                        </button>
                      )}
                      <button
                        disabled={Boolean(connection)}
                        onClick={() => {
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
                      >
                        查看提交点
                      </button>
                      {job.resultRef && (
                        <button
                          onClick={() => void loadSummary(job)}
                          disabled={Boolean(connection)}
                        >
                          查看运行摘要
                        </button>
                      )}
                      {summaries[job.jobId] && <p>{summaries[job.jobId]}</p>}
                    </article>
                  ))}
                </section>
              )}
            </fieldset>
            {tasks?.project && mentorOpen && learningCtl && (
              <MentorPanel
                controller={learningCtl}
                disabled={learningDisabled}
                currentDomainSnapshotId={currentDomainSnapshotId}
                onOpenOntologyRepair={() => selectWorkspace('ontology')}
                onOpenQueryWorkspace={() => selectWorkspace('query')}
                onOpenQualityWorkspace={() => selectWorkspace('quality')}
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
              />
            )}
          </div>
        </div>
        {taskError && !connection && <ErrorDetails error={taskError} context="task" />}
        <section id="modules" className="modules-section">
          <div className="section-title">
            <h2>六个模块，一条学习路径</h2>
            <span>需求规划 · 待实现</span>
          </div>
          <div className="modules">
            {modules.map(([number, title, detail]) => (
              <article key={number}>
                <span className="module-number">{number}</span>
                <div>
                  <h3>{title}</h3>
                  <p>{detail}</p>
                </div>
                <span className="planned">待开发</span>
              </article>
            ))}
          </div>
        </section>
        <ModelPanel key={activeProjectId ?? 'no-project'} jobs={tasks?.jobs ?? []} />
        <footer>
          需求基准 PRD V0.6
          <span>本地项目管理、本体编辑与查询逐项接入；完整项目导出及其余模块以验收范围为准。</span>
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
