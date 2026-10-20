import { useCallback, useEffect, useRef, useState } from 'react'
import {
  safeError,
  type HealthResult,
  type TaskView,
  type SafeError,
  type ProgressView,
  type TaskUpdate,
  type JobView,
  type SemanticRunOptions,
} from '@ontolearn/contracts'
import { explainError, jobStatus, resultSummary } from './task-presentation'
import { TaskProgressBuffer } from './task-progress'

const modules = [
  ['01', '定义业务概念', '本体构建'],
  ['02', '连接业务数据', '数据映射'],
  ['03', '向知识提问', '本体查询'],
  ['04', '检查并发现新知识', '知识推理'],
  ['05', '描述业务如何行动', '行为定义'],
  ['06', '比较不同方案', '沙盘推演'],
]

export function App() {
  const [result, setResult] = useState<HealthResult>()
  const [tasks, setTasks] = useState<TaskView>()
  const [progress, setProgress] = useState<Record<string, ProgressView>>({})
  const [taskError, setTaskError] = useState<SafeError>()
  const [summaries, setSummaries] = useState<Record<string, string>>({})
  const [connection, setConnection] = useState<Extract<TaskUpdate, { kind: 'connection' }>>()
  const [definitionIds, setDefinitionIds] = useState({ query: '', reasoning: '', validation: '' })
  const [semanticScope, setSemanticScope] = useState<'asserted' | 'asserted+derived'>('asserted')
  const [inputSelection, setInputSelection] = useState<'' | 'current' | 'historical'>('')
  const [snapshotId, setSnapshotId] = useState('')
  const [derivedResultId, setDerivedResultId] = useState('')
  const [starting, setStarting] = useState(false)
  const [pages, setPages] = useState<
    Record<
      string,
      {
        metadata: Record<string, unknown>
        rows: Array<{ rowId: string; ordinal: number; cells: unknown[] }>
        nextCursor: string | null
      }
    >
  >({})
  const [history, setHistory] = useState<{
    jobs: JobView[]
    nextCursor: string | null
    listSnapshotId: string
  }>()
  const current = useRef<TaskView | undefined>(undefined)
  const latestGeneration = useRef(-1)
  const uncertain = useRef(false)
  const connectionEpoch = useRef(0)
  const pendingProgress = useRef(new TaskProgressBuffer())
  const updateTasks = useCallback((value: TaskView) => {
    if (value.generation < latestGeneration.current) return false
    latestGeneration.current = value.generation
    current.current = value
    setTasks(value)
    return true
  }, [])
  const applyRestored = useCallback(
    (value: TaskView) => {
      if (!updateTasks(value)) return
      if (uncertain.current) setResult(undefined)
      uncertain.current = false
      setConnection(undefined)
      setTaskError(undefined)
      setProgress(pendingProgress.current.restore(value))
      setSummaries({})
      setPages({})
      setHistory(undefined)
    },
    [updateTasks],
  )
  async function restore() {
    const response = await window.ontolearn?.restoreTasks()
    if (response?.ok) {
      applyRestored(response.data)
    } else if (response) setTaskError(response.error)
  }
  useEffect(() => {
    let live = true
    const progressBuffer = pendingProgress.current
    const stop = window.ontolearn?.onTaskUpdate((update) => {
      if (!live || update.generation < latestGeneration.current) return
      const view = current.current
      if (update.kind === 'connection') {
        if (
          view &&
          update.generation === view.generation &&
          view.project?.projectId !== update.projectId
        )
          return
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
        setPages({})
        setHistory(undefined)
        return
      }
      if (update.kind === 'restored') {
        applyRestored(update.view)
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
    void window.ontolearn?.restoreTasks().then((response) => {
      if (!live) return
      if (response.ok) applyRestored(response.data)
      else if (!current.current) setTaskError(response.error)
    })
    return () => {
      live = false
      stop?.()
      progressBuffer.clear()
      for (const job of current.current?.jobs ?? [])
        void window.ontolearn?.unsubscribeJob(job.jobId, current.current!.generation)
    }
  }, [applyRestored, updateTasks])
  async function loadSummary(job: JobView, cursor: string | null = null) {
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
      cursor,
    })
    if (current.current?.generation !== generation) return
    if (!page.ok) {
      setTaskError(page.error)
      return
    }
    setPages((old) => ({
      ...old,
      [job.jobId]: {
        metadata: metadata.data,
        rows: page.data.rows as Array<{ rowId: string; ordinal: number; cells: unknown[] }>,
        nextCursor: page.data.nextCursor as string | null,
      },
    }))
    const label =
      metadata.data.state === 'stale'
        ? '结果已过期；显示原输入的历史计算。'
        : metadata.data.state === 'historical'
          ? '历史结果；不代表当前项目状态。'
          : '当前结果。'
    setSummaries((old) => ({
      ...old,
      [job.jobId]: `${label}${['query.execute', 'reasoning.execute', 'validation.execute'].includes(String(job.capability)) ? '下方为实际结果、告警与依据分页。' : resultSummary(page.data, job)}`,
    }))
  }
  async function runSemantic(kind: 'query' | 'reasoning' | 'validation') {
    const bridge = window.ontolearn
    const view = current.current
    if (!bridge || !view?.project || !inputSelection || starting || uncertain.current) return
    const generation = view.generation
    const projectId = view.project.projectId
    const epoch = connectionEpoch.current
    const acceptsReply = () =>
      current.current?.generation === generation &&
      current.current?.project?.projectId === projectId &&
      connectionEpoch.current === epoch
    const options: SemanticRunOptions = {
      definitionId: definitionIds[kind],
      scope: kind === 'reasoning' ? 'asserted' : semanticScope,
      inputSelection,
      inputSnapshotId: inputSelection === 'historical' ? snapshotId : null,
      derivedResultId:
        kind !== 'reasoning' && semanticScope === 'asserted+derived' ? derivedResultId : null,
    }
    setStarting(true)
    try {
      const response =
        kind === 'query'
          ? await bridge.runSavedQuery(options)
          : kind === 'validation'
            ? await bridge.runValidation(options)
            : await bridge.runReasoning({ ...options, scope: 'asserted', derivedResultId: null })
      if (!acceptsReply()) return
      if (!response.ok) setTaskError(response.error)
      else await restore()
    } catch {
      if (acceptsReply()) setTaskError(safeError(undefined))
    } finally {
      setStarting(false)
    }
  }
  async function loadHistory(next = false) {
    const bridge = window.ontolearn
    const view = current.current
    if (!bridge || !view?.project || uncertain.current) return
    const epoch = connectionEpoch.current
    const response = await bridge.listJobs({
      filter: 'all',
      pageSize: 20,
      listSnapshotId: next ? (history?.listSnapshotId ?? null) : null,
      cursor: next ? (history?.nextCursor ?? null) : null,
    })
    if (current.current?.generation !== view.generation || connectionEpoch.current !== epoch) return
    if (!response.ok) setTaskError(response.error)
    else {
      const binding = response.data.binding as { listSnapshotId: string }
      setHistory({
        jobs: response.data.jobs as JobView[],
        nextCursor: response.data.nextCursor as string | null,
        listSnapshotId: binding.listSnapshotId,
      })
    }
  }
  function resultPage(job: JobView) {
    const page = pages[job.jobId]
    if (!page) return null
    return (
      <div aria-label="不可变结果与完整来源">
        <p>
          结果 {String(page.metadata.resultId)} · 输入快照 {String(page.metadata.inputSnapshotId)} ·
          范围 {String(page.metadata.scope)} · {String(page.metadata.state)}
        </p>
        <details>
          <summary>结果版本、依赖和过期原因</summary>
          <pre>{JSON.stringify(page.metadata, null, 2)}</pre>
        </details>
        {page.rows.length ? (
          <table>
            <caption>固定顺序结果与来源；逐页查看全部记录</caption>
            <thead>
              <tr>
                <th>序号</th>
                <th>结果 / 告警 / 依据</th>
              </tr>
            </thead>
            <tbody>
              {page.rows.map((row) => (
                <tr key={row.rowId}>
                  <td>{row.ordinal}</td>
                  <td>
                    <pre>{JSON.stringify(row.cells, null, 2)}</pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>本页无结果。请核对数据范围、输入版本、筛选条件和保存的定义。</p>
        )}
        {page.nextCursor && (
          <button
            disabled={Boolean(connection)}
            onClick={() => void loadSummary(job, page.nextCursor)}
          >
            下一页结果与来源
          </button>
        )}
      </div>
    )
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
    <div className="app-shell">
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
            开发概览 <span>↗</span>
          </a>
          <a href="#modules">
            模块规划 <span>06</span>
          </a>
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
          <span>工作台 / 开发概览</span>
          <span className="badge">M0 · 开发骨架</span>
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
          <button onClick={() => void checkEngine()} disabled={checking}>
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
              '尚未检查本地引擎连接。'
            )}
          </div>
        </section>
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
                  输入快照 {job.inputSnapshotId} · 范围 {String(job.scope)} ·
                  {job.inputSnapshotId === tasks.project?.inputSnapshotId
                    ? '当前输入'
                    : '历史输入；此任务保留原执行依据'}
                </p>
                {progress[job.jobId] && ['queued', 'running', 'cancelling'].includes(job.state) && (
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
                <p>
                  任务 {job.jobId} · 操作 {job.operationId}
                </p>
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
                    查看结果与来源
                  </button>
                )}
                {summaries[job.jobId] && <p>{summaries[job.jobId]}</p>}
                {resultPage(job)}
              </article>
            ))}
          </section>
        )}
        {tasks?.project && (
          <section className="health-panel" aria-label="本地语义技术验证">
            <h2>运行已保存的本地语义定义</h2>
            <p>
              技术验证入口：项目必须由可信应用配置授权。当前没有项目创建或定义编辑流程；仅执行该项目已保存的查询、规则和约束。
            </p>
            <p>
              项目 {tasks.project.projectId} · 当前快照 {tasks.project.inputSnapshotId}
            </p>
            <label>
              执行输入{' '}
              <select
                value={inputSelection}
                onChange={(event) =>
                  setInputSelection(event.target.value as '' | 'current' | 'historical')
                }
              >
                <option value="">请明确选择输入</option>
                <option value="current">当前项目输入</option>
                <option value="historical">指定历史快照</option>
              </select>
            </label>
            {inputSelection === 'historical' && (
              <label>
                历史输入快照标识{' '}
                <input
                  value={snapshotId}
                  onChange={(event) => setSnapshotId(event.target.value)}
                  maxLength={64}
                />
              </label>
            )}
            <label>
              查询与验证范围{' '}
              <select
                value={semanticScope}
                onChange={(event) =>
                  setSemanticScope(event.target.value as 'asserted' | 'asserted+derived')
                }
              >
                <option value="asserted">断言事实</option>
                <option value="asserted+derived">断言事实＋明确选中的已有推导结果</option>
              </select>
            </label>
            {semanticScope === 'asserted+derived' && (
              <label>
                已有推理结果标识{' '}
                <input
                  value={derivedResultId}
                  onChange={(event) => setDerivedResultId(event.target.value)}
                  maxLength={36}
                />
              </label>
            )}
            <p>
              推理只读取所选输入的断言事实与本体；不会为了查询或检查自动重算已有推导。规则链、递归及范围外构造仍不支持；当前候选范围等待
              Q6 确认。
            </p>
            {(['query', 'reasoning', 'validation'] as const).map((kind) => (
              <div key={kind}>
                <label>
                  {
                    {
                      query: '已保存查询标识',
                      reasoning: '已保存规则集标识',
                      validation: '已保存约束标识',
                    }[kind]
                  }
                  <input
                    value={definitionIds[kind]}
                    maxLength={128}
                    onChange={(event) =>
                      setDefinitionIds((old) => ({ ...old, [kind]: event.target.value }))
                    }
                  />
                </label>
                <button
                  disabled={
                    starting || Boolean(connection) || !inputSelection || !definitionIds[kind]
                  }
                  onClick={() => void runSemantic(kind)}
                >
                  {{ query: '运行查询', reasoning: '运行推理', validation: '运行检查' }[kind]}
                </button>
              </div>
            ))}
            <p>请求只提交一次。连接中断后请先查询持久任务历史，核对原操作，勿直接重复提交。</p>
          </section>
        )}
        {tasks?.project && (
          <section aria-label="持久任务历史">
            <h2>持久任务历史</h2>
            <button disabled={Boolean(connection)} onClick={() => void loadHistory()}>
              读取任务历史首页
            </button>
            {history?.jobs.map((job) => (
              <article key={job.jobId}>
                <p>
                  {jobStatus(job)} · 任务 {job.jobId} · 操作 {job.operationId}
                </p>
                <p>
                  输入快照 {job.inputSnapshotId} · 范围 {String(job.scope)} ·{' '}
                  {job.inputSnapshotId === tasks.project?.inputSnapshotId ? '当前输入' : '历史输入'}
                </p>
                {job.error && <ErrorDetails error={job.error} context="task" />}
                {job.resultRef && (
                  <button disabled={Boolean(connection)} onClick={() => void loadSummary(job)}>
                    查看结果与来源
                  </button>
                )}
                {resultPage(job)}
              </article>
            ))}
            {history?.nextCursor && (
              <button disabled={Boolean(connection)} onClick={() => void loadHistory(true)}>
                下一页任务历史
              </button>
            )}
          </section>
        )}
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
          <span>
            当前为开发与语义验证入口；项目编辑、自动保存、模型调用和完整六模块流程尚未接入。
          </span>
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
