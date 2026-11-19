import { useEffect, useMemo, useState } from 'react'
import type {
  ScenarioBridge,
  ScenarioCompareResultDTO,
  ScenarioMetrics,
  ScenarioReadResultDTO,
  ScenarioRunDTO,
  ScenarioSummaryDTO,
} from '@ontolearn/contracts'
import { useWorkspaceOperation, type ReportWorkspaceStatus } from '../mapping/workspace-operation'
import { SCENARIO_ROUND_PAGE, scenarioRunView, scenarioServices, scenarioView } from './bridge'
import { RunDetails, ScenarioPage } from './ScenarioPage'

const active = (status: ScenarioRunDTO['status']) =>
  status === 'queued' || status === 'running' || status === 'cancelling'
const metricText = (metrics: ScenarioMetrics | null) =>
  metrics
    ? `积压 ${metrics.backlog} · 完成工单 ${metrics.completed} · 未关闭高危告警 ${metrics.openHighAlerts}`
    : '无已提交指标'

export function ConnectedScenarioWorkspace({
  bridge,
  projectId,
  revision,
  inputSnapshotId,
  disabled,
  onStatus,
}: {
  bridge: ScenarioBridge
  projectId: string
  revision: number
  inputSnapshotId: string
  disabled: boolean
  onStatus: ReportWorkspaceStatus
}) {
  const services = useMemo(
    () =>
      scenarioServices(bridge, projectId, {
        projectVersion: revision,
        inputSnapshotId,
      }),
    [bridge, inputSnapshotId, projectId, revision],
  )
  const [items, setItems] = useState<ScenarioSummaryDTO[]>([])
  const [cursor, setCursor] = useState<string | null>(null)
  const [initialized, setInitialized] = useState(false)
  const [initialReadFailed, setInitialReadFailed] = useState(false)
  const [detail, setDetail] = useState<ScenarioReadResultDTO>()
  const [run, setRun] = useState<ScenarioRunDTO>()
  const [picks, setPicks] = useState<ScenarioRunDTO[]>([])
  const [comparison, setComparison] = useState<ScenarioCompareResultDTO>()
  const [dirty, setDirty] = useState(false)
  const [deleteApproved, setDeleteApproved] = useState(false)
  const [restoreApproved, setRestoreApproved] = useState(false)
  const [inFlight, setInFlight] = useState<Set<string>>(() => new Set())
  const { busy, error, perform } = useWorkspaceOperation(onStatus, dirty, inFlight.size > 0)

  function setRunStatus(value: ScenarioRunDTO) {
    setRun(value)
    rememberActive([value])
  }
  function rememberActive(values: { runId: string; status: ScenarioRunDTO['status'] }[]) {
    setInFlight((old) => {
      const next = new Set(old)
      values.forEach(({ runId, status }) => {
        if (active(status)) next.add(runId)
        else next.delete(runId)
      })
      return next
    })
  }
  function readList(from: string | null) {
    void perform(async (current) => {
      const reply = await services.list(from)
      current()
      setItems((old) => [
        ...new Map(
          [...(from ? old : []), ...reply.items].map((item) => [item.identity.scenarioId, item]),
        ).values(),
      ])
      setCursor(reply.nextCursor)
      setInitialReadFailed(false)
      setInitialized(true)
    })
  }
  useEffect(() => {
    if (disabled || initialized) return
    let live = true
    void services
      .list(null)
      .then((reply) => {
        if (!live) return
        setItems(reply.items)
        setCursor(reply.nextCursor)
      })
      .catch(() => {
        if (live) setInitialReadFailed(true)
      })
      .finally(() => {
        if (live) setInitialized(true)
      })
    return () => {
      live = false
    }
  }, [disabled, initialized, services])

  function loadDetail(id: string) {
    void perform(async (current) => {
      const next = await services.read(id)
      current()
      setDetail(next)
      setRun(undefined)
      setDeleteApproved(false)
      setRestoreApproved(false)
      rememberActive(next.runs)
    })
  }
  function loadRun(ref: { scenarioId: string; runId: string }, offset = 0) {
    void perform(async (current) => {
      const next = await services.readRun(ref, offset)
      current()
      setRunStatus(next)
    })
  }
  function execute(action: () => Promise<ScenarioRunDTO>) {
    void perform(async (current) => {
      const next = await action()
      current()
      setRunStatus(next)
      setDeleteApproved(false)
      const refreshed = await services.read(next.identity.scenarioId)
      current()
      setDetail(refreshed)
      rememberActive(refreshed.runs)
    })
  }

  const chosen = detail?.scenario
  const runRef = run ? { runId: run.runId, scenarioId: run.identity.scenarioId } : undefined
  const locked = disabled || busy || !initialized
  const terminal = run && !active(run.status)
  return (
    <fieldset disabled={locked} aria-busy={busy || !initialized}>
      <ScenarioPage
        scenarios={items.map(scenarioView)}
        actions={{
          create: async (draft, sourceId) => {
            const source = sourceId
              ? items.find((item) => item.identity.scenarioId === sourceId)?.identity
              : undefined
            if (sourceId && !source) throw new Error('MISSING_SOURCE')
            let created = false
            await perform(async (current) => {
              const scenario = await services.create(draft, source)
              current()
              setItems((old) => [
                scenario,
                ...old.filter((item) => item.identity.scenarioId !== scenario.identity.scenarioId),
              ])
              setDetail({ projectId, scenario, runs: [] })
              setRun(undefined)
              created = true
            })
            if (!created) throw new Error('CREATE_FAILED')
          },
        }}
        connected={{
          selectedScenarioId: chosen?.identity.scenarioId,
          onSelect: loadDetail,
          onDirty: setDirty,
          listControls: (
            <>
              <button type="button" onClick={() => readList(null)}>
                刷新场景列表
              </button>
              <button type="button" disabled={!cursor} onClick={() => readList(cursor)}>
                下一页场景
              </button>
            </>
          ),
          runContent:
            chosen && detail ? (
              <section className="scenario-panel" aria-label="已保存场景和隔离运行">
                <h2>{chosen.configuration.name}</h2>
                <p>
                  基准项目版本 {chosen.identity.projectVersion} · 快照{' '}
                  {chosen.identity.inputSnapshotId}
                </p>
                <p>
                  规则 {chosen.identity.ruleVersion} · 行为 {chosen.identity.behaviorVersion}
                </p>
                <button
                  type="button"
                  disabled={detail.runs.some((item) => active(item.status))}
                  onClick={() => execute(() => services.run(chosen.identity))}
                >
                  运行场景
                </button>
                <button type="button" onClick={() => loadDetail(chosen.identity.scenarioId)}>
                  刷新运行列表
                </button>
                <label>
                  <input
                    type="checkbox"
                    checked={restoreApproved}
                    onChange={(e) => setRestoreApproved(e.target.checked)}
                  />
                  确认将此场景恢复到所示基准
                </label>
                <button
                  type="button"
                  disabled={!restoreApproved || detail.runs.some((item) => active(item.status))}
                  onClick={() =>
                    void perform(async (current) => {
                      const scenario = await services.restore(chosen.identity)
                      current()
                      setRestoreApproved(false)
                      setDetail({ ...detail, scenario, runs: [] })
                      setRun(undefined)
                      setDeleteApproved(false)
                      setPicks((old) =>
                        old.filter(
                          (item) => item.identity.scenarioId !== scenario.identity.scenarioId,
                        ),
                      )
                      setComparison(undefined)
                    })
                  }
                >
                  恢复基准场景
                </button>
                <ul>
                  {detail.runs.map((item) => (
                    <li key={item.runId}>
                      <button
                        type="button"
                        aria-pressed={run?.runId === item.runId}
                        onClick={() => {
                          setDeleteApproved(false)
                          loadRun({ scenarioId: chosen.identity.scenarioId, runId: item.runId })
                        }}
                      >
                        读取运行 {item.runId} · {item.status} · 已提交 {item.lastCommittedRound} 轮
                      </button>
                    </li>
                  ))}
                </ul>
                {run && runRef && (
                  <>
                    <button type="button" onClick={() => loadRun(runRef, run.roundOffset)}>
                      刷新此运行
                    </button>
                    <button
                      type="button"
                      disabled={!active(run.status) || run.status === 'cancelling'}
                      onClick={() => execute(() => services.cancel(run))}
                    >
                      请求取消运行
                    </button>
                    <button
                      type="button"
                      disabled={
                        !run.resumeAvailable ||
                        !run.checkpointRef ||
                        !terminal ||
                        run.status === 'succeeded'
                      }
                      onClick={() => execute(() => services.resume(run))}
                    >
                      从最后提交检查点显式续跑
                    </button>
                    <label>
                      <input
                        type="checkbox"
                        checked={deleteApproved}
                        onChange={(e) => setDeleteApproved(e.target.checked)}
                      />
                      确认删除此运行记录
                    </label>
                    <button
                      type="button"
                      disabled={!terminal || !deleteApproved}
                      onClick={() =>
                        void perform(async (current) => {
                          await services.remove(run)
                          current()
                          setRun(undefined)
                          setDeleteApproved(false)
                          setDetail({
                            ...detail,
                            runs: detail.runs.filter((item) => item.runId !== run.runId),
                          })
                          setPicks((old) => old.filter((item) => item.runId !== run.runId))
                          setComparison(undefined)
                        })
                      }
                    >
                      删除此运行记录
                    </button>
                    <button
                      type="button"
                      disabled={
                        run.status !== 'succeeded' ||
                        picks.length >= 10 ||
                        picks.some((item) => item.runId === run.runId)
                      }
                      onClick={() => {
                        setPicks([...picks, run])
                        setComparison(undefined)
                      }}
                    >
                      加入运行对比
                    </button>
                    <RunDetails
                      run={scenarioRunView(run)}
                      scenario={scenarioView(chosen)}
                      actions={{}}
                      busy={locked}
                      perform={async (action) => {
                        await action()
                      }}
                      connected
                    />
                    <nav aria-label="运行轮次分页">
                      <button
                        type="button"
                        disabled={!run.roundOffset}
                        onClick={() =>
                          loadRun(runRef, Math.max(0, run.roundOffset - SCENARIO_ROUND_PAGE))
                        }
                      >
                        上一页轮次
                      </button>
                      <button
                        type="button"
                        disabled={run.roundOffset + run.rounds.length >= run.lastCommittedRound}
                        onClick={() => loadRun(runRef, run.roundOffset + run.rounds.length)}
                      >
                        下一页轮次
                      </button>
                    </nav>
                  </>
                )}
              </section>
            ) : (
              <p>选择场景以读取运行记录。</p>
            ),
        }}
      />
      {(error || initialReadFailed) && (
        <p role="alert">场景操作未完成。请刷新持久记录并检查项目版本与输入配置。</p>
      )}
      <section className="scenario-panel" aria-label="逐轮与最终指标对比">
        <h2>运行对比（选择 2–10 项）</h2>
        <ul>
          {picks.map((item) => (
            <li key={item.runId}>
              {item.identity.scenarioId} / {item.runId}
              <button
                type="button"
                onClick={() => {
                  setPicks(picks.filter((candidate) => candidate.runId !== item.runId))
                  setComparison(undefined)
                }}
              >
                移出对比
              </button>
            </li>
          ))}
        </ul>
        <button type="button" disabled={picks.length < 2} onClick={() => compare(0)}>
          对比所选成功运行
        </button>
        {comparison && (
          <>
            {comparison.runs.map((item, index) => (
              <article key={item.runId}>
                <h3>{item.runId}</h3>
                <p>
                  场景 {item.identity.scenarioId} · 项目版本 {item.identity.projectVersion} · 输入{' '}
                  {item.identity.inputVersion} / {item.identity.inputSnapshotId}
                </p>
                <p>
                  规则 {item.identity.ruleVersion} · 行为 {item.identity.behaviorVersion} · 语义{' '}
                  {item.identity.semantics} · 引擎 {item.identity.engineVersion} · 依赖锁{' '}
                  {item.identity.dependencyLockHash} · 配置 {item.identity.configurationDigest}
                </p>
                <p>
                  期末（第 {item.lastCommittedRound} 轮） · {metricText(item.finalMetrics)}
                </p>
                <p>
                  未处理事件 {picks[index].pendingEvents.length} ·{' '}
                  {picks[index].pendingEvents.join('、') || '无'}
                </p>
                <ul>
                  {item.metrics.map((row) => (
                    <li key={row.round}>
                      第 {row.round} 轮 · {metricText(row.values)}
                    </li>
                  ))}
                </ul>
              </article>
            ))}
            <button
              type="button"
              disabled={!comparison.roundOffset}
              onClick={() => compare(Math.max(0, comparison.roundOffset - SCENARIO_ROUND_PAGE))}
            >
              上一页对比
            </button>
            <button
              type="button"
              disabled={
                !comparison.runs.some(
                  (item) => item.lastCommittedRound > comparison.roundOffset + SCENARIO_ROUND_PAGE,
                )
              }
              onClick={() => compare(comparison.roundOffset + SCENARIO_ROUND_PAGE)}
            >
              下一页对比
            </button>
          </>
        )}
      </section>
    </fieldset>
  )

  function compare(offset: number) {
    void perform(async (current) => {
      const result = await services.compare(
        picks.map((item) => ({ scenarioId: item.identity.scenarioId, runId: item.runId })),
        offset,
      )
      current()
      if (
        result.runs.some(
          (item, index) =>
            item.identity.configurationDigest !== picks[index].identity.configurationDigest ||
            item.identity.inputSnapshotId !== picks[index].identity.inputSnapshotId,
        )
      )
        throw new Error('RUN_VERSION_CHANGED')
      setComparison(result)
    })
  }
}
