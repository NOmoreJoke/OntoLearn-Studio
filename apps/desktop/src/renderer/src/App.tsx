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

type WorkspaceModule = 'query' | 'ontology'
type OntologyContext = {
  session: OntologySession
  contextKey: string
  projectId: string
  generation: number
}

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
  const checkpointBlocked =
    !!checkpointState &&
    (checkpointState.busy || checkpointState.recovery.length > 0 || !checkpointState.recoveryLoaded)
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
    next.session.subscribe(() => workspaceNotify.current())
    ontologyOwner.current = next
    setOntologyContext(next)
  }, [management, retireOntology, selectQueryWorkspace, setOntologyContext])
  function selectWorkspace(module: WorkspaceModule) {
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
      else if (management && value.project)
        await settleManagementTail(management, value.project.projectId)
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
      // 完成全部 management 读取；单并发模型下不允许留下在飞行的调用。
      const tail = settleManagementTail(management, projectId, { refresh: true })
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
  async function createProject(example = false) {
    const bridge = window.ontolearn
    const name = projectName.trim() ? projectName : example ? '设备运维示例' : ''
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
      // 与 openProject 相同的准入尾段：全部 management 读取串行完成后，才允许
      // restore() 渲染新项目版本并把工作台交还出去。
      await management?.refresh()
      if (opened.ok) {
        const tail = settleManagementTail(management, created.data.projectId)
        admissionTail.current = tail
        await tail
        await restore()
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
  }
  const aggregateWorkspace = useCallback(() => {
    const queries = [...queryControllers.current.values()]
    const ontology = ontologyOwner.current?.session.getSnapshot()
    return {
      dirty: ontologyDirty.current || queries.some((controller) => controller.getSnapshot().dirty),
      unresolved:
        !!createIntent.current ||
        libraryBusy.current ||
        uncertain.current ||
        !!management?.unresolved ||
        !!checkpointCtl?.unresolved ||
        queries.some(
          (controller) => controller.hasUnresolvedWrite || controller.getSnapshot().busy,
        ) ||
        ontologyOperations.hasUnresolved ||
        (!!ontology && ['reading', 'preparing', 'submitting', 'unknown'].includes(ontology.phase)),
    }
  }, [management, checkpointCtl])
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
  const onOntologyDirty = useCallback((dirty: boolean) => {
    ontologyDirty.current = dirty
    workspaceNotify.current()
  }, [])
  const freezeWorkspace = useCallback((value: boolean) => {
    frozen.current = value
    setWorkspaceFrozen(value)
  }, [])
  useEffect(() => {
    if (!management) return
    const stop = management.subscribe(() => {
      setManagementState(management.getSnapshot())
      workspaceNotify.current()
    })
    void management.initialize()
    return stop
  }, [management])
  useEffect(() => {
    management?.setAppliedHandler((receipt) => {
      // The old operation owns its receipt, never a newer selected workspace.
      if (receipt.kind === 'trash' && current.current?.project?.projectId === receipt.projectId) {
        retireOntology()
        disconnectQuery()
        readyWorkspace.current = undefined
        current.current = undefined
        setTasks(undefined)
        management?.select(undefined)
      }
      // Metadata-only edits preserve the editor instance and its draft. The
      // controller reads current metadata; no domain restore or remount occurs.
      workspaceNotify.current()
    })
  }, [management, retireOntology, disconnectQuery])
  useEffect(() => {
    if (!checkpointCtl) return
    const stop = checkpointCtl.subscribe(() => {
      setCheckpointState(checkpointCtl.getSnapshot())
      workspaceNotify.current()
    })
    void checkpointCtl.initialize()
    checkpointCtl.setAppliedHandler((result) => {
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
    return stop
  }, [checkpointCtl])
  useEffect(() => {
    checkpointCtl?.select(tasks?.project?.projectId)
    // 打开/创建/恢复后的新选中项目：management 尾段已在 applyRestored 内串行
    // 完成，此处同步刷新一次检查点列表；无选中项目时不发起列表请求。
    if (tasks?.project?.projectId) void checkpointCtl?.refreshWhenIdle()
  }, [checkpointCtl, tasks?.project?.projectId])
  useEffect(() => {
    if (!checkpointApplied) return
    // Reload the restored workspace through the real open path after the
    // applying event settles; a microtask keeps setState out of the effect body.
    const pending = checkpointApplied
    queueMicrotask(() => {
      void openProject(pending.projectId).finally(() => {
        void management?.refresh()
        void checkpointCtl?.refresh()
      })
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
  }, [management, checkpointCtl, retireOntology, disconnectQuery])
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
          <a href="#modules">
            模块规划 <span>06</span>
          </a>
          {tasks?.project && (
            <>
              <a
                href="#query-workspace"
                aria-current={workspaceModule === 'query' ? 'page' : undefined}
                aria-disabled={
                  projectBusy || Boolean(connection) || workspaceFrozen || managementBlocked
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
                  projectBusy || Boolean(connection) || workspaceFrozen || managementBlocked
                }
                onClick={(event) => {
                  event.preventDefault()
                  selectWorkspace('ontology')
                }}
              >
                本体构建
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
          className="project-library"
          aria-labelledby="project-library-title"
          data-testid="project-library"
        >
          <h2 id="project-library-title">我的项目</h2>
          <p>在本机创建项目，或打开已保存的项目继续编辑。无需配置模型 API。</p>
          <div className="project-quickstart" aria-label="首次启动入口">
            <button
              type="button"
              disabled={projectBusy || workspaceFrozen || managementBlocked}
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
              disabled={projectBusy || hasCreateIntent || workspaceFrozen || managementBlocked}
              required
            />
            <button
              type="submit"
              data-testid="project-create"
              disabled={projectBusy || !projectName.trim() || workspaceFrozen || managementBlocked}
            >
              {hasCreateIntent ? '核对创建结果' : '新建空白项目'}
            </button>
            <button
              type="button"
              data-testid="project-create-example"
              disabled={projectBusy || hasCreateIntent || workspaceFrozen || managementBlocked}
              onClick={() => void createProject(true)}
            >
              从设备运维示例开始
            </button>
            {!management && (
              <button
                type="button"
                data-testid="project-list-refresh"
                onClick={() => void listProjects()}
                disabled={projectBusy}
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
                      disabled={projectBusy}
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
                  disabled={projectBusy}
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
              disabled={projectBusy || workspaceFrozen || Boolean(connection)}
              destructiveBlocked={workspaceStatus.dirty || workspaceStatus.unresolved}
              openProject={(id) => void openProject(id)}
            />
          )}
          {checkpointCtl && (
            <ProjectCheckpointRestorePanel
              controller={checkpointCtl}
              disabled={
                projectBusy ||
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
              disabled={projectBusy || managementBlocked}
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
                <OntologyMainlinePage
                  session={ontologyContext.session}
                  contextKey={ontologyContext.contextKey}
                  onDirtyChange={onOntologyDirty}
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
              <button onClick={() => void restore()} disabled={connection.state === 'reconnecting'}>
                重新连接并对账
              </button>
            </section>
          )}
          {tasks?.project && (
            <section className="health-panel" aria-label="后台任务状态">
              <h2>后台任务</h2>
              <p>窗口恢复后读取持久状态；不会重发写任务。</p>
              <button onClick={() => void restore()} disabled={Boolean(connection)}>
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
                    <button onClick={() => void loadSummary(job)} disabled={Boolean(connection)}>
                      查看运行摘要
                    </button>
                  )}
                  {summaries[job.jobId] && <p>{summaries[job.jobId]}</p>}
                </article>
              ))}
            </section>
          )}
        </fieldset>
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
