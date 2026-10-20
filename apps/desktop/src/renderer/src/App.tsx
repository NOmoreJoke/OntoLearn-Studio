import { useEffect, useRef, useState } from 'react'
import {
  safeError,
  type HealthResult,
  type TaskView,
  type SafeError,
  type ProgressView,
} from '@ontolearn/contracts'
import { explainError, jobStatus, resultSummary } from './task-presentation'

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
  const current = useRef<TaskView | undefined>(undefined)
  const updateTasks = (value: TaskView) => {
    if (current.current && value.generation < current.current.generation) return
    current.current = value
    setTasks(value)
  }
  async function restore() {
    const response = await window.ontolearn?.restoreTasks()
    if (response?.ok) {
      updateTasks(response.data)
      setTaskError(undefined)
    } else if (response) setTaskError(response.error)
  }
  useEffect(() => {
    let live = true
    const stop = window.ontolearn?.onTaskUpdate((update) => {
      const view = current.current
      if (
        live &&
        update.restoredView &&
        (!view || update.generation > view.generation) &&
        update.restoredView.generation === update.generation &&
        (!view || update.restoredView.project?.projectId === view.project?.projectId)
      ) {
        updateTasks(update.restoredView)
        setProgress({})
        setSummaries({})
        setTaskError(undefined)
        return
      }
      if (
        !live ||
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
      updateTasks({
        ...view,
        jobs: view.jobs.map((job) => (job.jobId === update.job.jobId ? update.job : job)),
      })
    })
    void window.ontolearn?.restoreTasks().then((response) => {
      if (!live) return
      if (response.ok) updateTasks(response.data)
      else if (!current.current) setTaskError(response.error)
    })
    return () => {
      live = false
      stop?.()
      for (const job of current.current?.jobs ?? [])
        void window.ontolearn?.unsubscribeJob(job.jobId, current.current!.generation)
    }
  }, [])
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
      setResult(response)
    } catch {
      setResult({ ok: false, error: safeError(undefined) })
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
              '尚未检查 · 当前仅开放连接检查能力。'
            )}
          </div>
        </section>
        {tasks?.project && (
          <section className="health-panel" aria-label="后台任务状态">
            <h2>后台任务</h2>
            <p>窗口恢复后读取持久状态；不会重发写任务。</p>
            <button onClick={() => void restore()}>刷新任务状态</button>
            {tasks.jobs.map((job) => (
              <article key={job.jobId} data-testid="durable-job" data-job-id={job.jobId}>
                <p>
                  {jobStatus(job)} · 状态版本 {job.stateVersion}
                </p>
                <p>
                  输入快照 {job.inputSnapshotId.slice(0, 12)} ·
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
                {job.error && <ErrorDetails error={job.error} context="task" />}
                {['queued', 'running'].includes(job.state) && (
                  <button
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
                  <button onClick={() => void loadSummary(job)}>查看运行摘要</button>
                )}
                {summaries[job.jobId] && <p>{summaries[job.jobId]}</p>}
              </article>
            ))}
          </section>
        )}
        {taskError && <ErrorDetails error={taskError} context="task" />}
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
          需求基准 PRD V0.6<span>项目编辑、自动保存、模型调用与六模块业务能力尚未接入。</span>
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
