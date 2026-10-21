import { useState } from 'react'
import type { ScenarioDraft, ScenarioView, RunView } from './presentation'
import {
  compareRuns,
  completionLabel,
  metricDefinitions,
  resultLabel,
  validDraft,
  type ScenarioInputDraft,
} from './presentation'
import './scenario.css'

/** Callbacks are supplied only by approved business adapters; never a generic invoke channel. */
export interface ScenarioActions {
  create?: (draft: ScenarioDraft, sourceScenarioId?: string) => Promise<void>
  run?: (scenarioId: string, inputVersion: string) => Promise<void>
  cancel?: (runId: string) => Promise<void>
  replay?: (runId: string) => Promise<void>
  resume?: (runId: string, round: number) => Promise<void>
  restore?: (scenarioId: string) => Promise<void>
  deleteRun?: (runId: string) => Promise<void>
}

export function ScenarioPage({
  scenarios,
  actions,
  unavailableReason,
}: {
  scenarios: readonly ScenarioView[]
  actions: ScenarioActions
  unavailableReason?: string
}) {
  const [selected, setSelected] = useState('')
  const [sourceMode, setSourceMode] = useState<'project' | 'scenario'>('scenario')
  const [compared, setCompared] = useState<readonly string[]>([])
  const [draft, setDraft] = useState<ScenarioDraft>({ name: '', maxRounds: 4, capacity: 3 })
  const [inputs, setInputs] = useState<ScenarioInputDraft | null>(null)
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const current = scenarios.find((item) => item.identity.scenarioId === selected) ?? scenarios[0]
  const copySource = sourceMode === 'scenario' ? current?.identity.scenarioId : undefined
  const configuredDraft: ScenarioDraft = {
    ...draft,
    capacity:
      draft.capacityMode === 'people'
        ? (draft.people ?? NaN) * (draft.perPerson ?? NaN)
        : draft.capacity,
    ...(inputs ? { inputs } : {}),
  }
  const run = current?.runs.at(-1)
  const active = run && ['queued', 'running', 'cancelling'].includes(run.status)
  const comparison = scenarios
    .filter((item) => compared.includes(item.identity.scenarioId))
    .map((item) => ({ scenario: item, run: item.runs.at(-1) }))
  const comparisonRuns = comparison.flatMap((item) => (item.run ? [item.run] : []))
  const rows = comparisonRuns.length === comparison.length ? compareRuns(comparisonRuns) : []

  async function perform(action: () => Promise<void>) {
    if (busy) return
    setBusy(true)
    setMessage('')
    try {
      await action()
    } catch {
      setMessage('操作未完成。请查看任务状态和最后已提交轮次后重试。')
    } finally {
      setBusy(false)
    }
  }

  function runButton(label: string, enabled: boolean, action: () => Promise<void>) {
    return (
      <button type="button" disabled={busy || !enabled} onClick={() => void perform(action)}>
        {label}
      </button>
    )
  }

  return (
    <main className="scenario-page" aria-busy={busy}>
      <header className="scenario-heading">
        <div>
          <p className="scenario-kicker">固定轮次情景推演</p>
          <h1>沙盘</h1>
          <p>复制场景，改变资源假设，再对照每一轮的真实运行记录。</p>
        </div>
        <p className="scenario-notice">推演基于选定输入和假设，不代表无条件的事实预测。</p>
      </header>
      {unavailableReason && <p role="status">{unavailableReason}</p>}
      {message && <p role="alert">{message}</p>}
      <section className="scenario-panel" aria-labelledby="scenario-create">
        <h2 id="scenario-create">创建或复制场景</h2>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            if (validDraft(configuredDraft) && actions.create)
              void perform(() => actions.create!(configuredDraft, copySource))
          }}
        >
          <label>
            创建来源
            <select
              aria-label="创建来源"
              value={copySource ? 'scenario' : 'project'}
              onChange={(event) => setSourceMode(event.target.value as 'project' | 'scenario')}
            >
              <option value="project">基准项目</option>
              <option value="scenario" disabled={!current}>
                选中场景
              </option>
            </select>
          </label>
          <label>
            场景名称
            <input
              required
              value={draft.name}
              onChange={(event) => setDraft({ ...draft, name: event.target.value })}
            />
          </label>
          <label>
            最大轮数（1–1000）
            <input
              type="number"
              min="1"
              max="1000"
              step="1"
              required
              value={draft.maxRounds}
              onChange={(event) => setDraft({ ...draft, maxRounds: event.target.valueAsNumber })}
            />
          </label>
          <label>
            每轮处理产能（单）
            <input
              type="number"
              min="0"
              step="1"
              required
              value={draft.capacity}
              disabled={draft.capacityMode === 'people'}
              onChange={(event) => setDraft({ ...draft, capacity: event.target.valueAsNumber })}
            />
          </label>
          <label>
            产能输入方式
            <select
              aria-label="产能输入方式"
              value={draft.capacityMode ?? 'direct'}
              onChange={(event) =>
                setDraft({
                  ...draft,
                  capacityMode: event.target.value as 'direct' | 'people',
                  people: 1,
                  perPerson: 3,
                })
              }
            >
              <option value="direct">直接设置每轮产能</option>
              <option value="people">人数 × 每人每轮处理数</option>
            </select>
          </label>
          {draft.capacityMode === 'people' && (
            <>
              <label>
                人员数
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={draft.people}
                  onChange={(event) => setDraft({ ...draft, people: event.target.valueAsNumber })}
                />
              </label>
              <label>
                每人每轮处理数
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={draft.perPerson}
                  onChange={(event) =>
                    setDraft({ ...draft, perPerson: event.target.valueAsNumber })
                  }
                />
              </label>
            </>
          )}
          <button type="submit" disabled={busy || !actions.create || !validDraft(configuredDraft)}>
            {copySource ? '复制选中场景' : '从项目创建场景'}
          </button>
        </form>
        <p>初始状态、事件、行为和规则从所选来源复制；运行记录不会被复制为新场景结果。</p>
        <details>
          <summary>配置场景输入、规则、事件与业务参数</summary>
          <p>
            默认沿用来源场景。需要自定义时，编辑结构化内容；行为条件和规则内容仍按相应模块的支持范围校验。
          </p>
          <label>
            <input
              type="checkbox"
              checked={inputs !== null}
              onChange={(event) =>
                setInputs(
                  event.target.checked
                    ? {
                        initialState: '{}',
                        events: '[]',
                        rules: '{}',
                        behaviors: '{}',
                        parameters: '{}',
                        assumptions: '',
                        source: '',
                      }
                    : null,
                )
              }
            />
            自定义输入（替换复制的输入）
          </label>
          {inputs && (
            <div className="scenario-inputs">
              {(
                [
                  ['initialState', '初始状态（对象）'],
                  ['events', '逐轮事件（列表，含 id、round、sequence、payload）'],
                  ['rules', '启用规则与版本（对象）'],
                  ['behaviors', '启用行为与版本（对象）'],
                  ['parameters', '业务参数（对象）'],
                  ['assumptions', '主要假设'],
                  ['source', '数据来源'],
                ] as const
              ).map(([key, label]) => (
                <label key={key}>
                  {label}
                  <textarea
                    aria-label={label}
                    rows={3}
                    value={inputs[key]}
                    onChange={(event) => setInputs({ ...inputs, [key]: event.target.value })}
                  />
                </label>
              ))}
            </div>
          )}
          {inputs && !validDraft(configuredDraft) && (
            <p role="status">请检查结构化输入格式、事件身份、轮次与产能；当前配置尚不能提交。</p>
          )}
          <p>观察指标：工单积压、累计完成、未闭环高危告警。每轮与期末均保留，定义见下方。</p>
        </details>
      </section>
      <div className="scenario-layout">
        <section className="scenario-panel" aria-labelledby="scenario-list">
          <h2 id="scenario-list">场景与对比</h2>
          {scenarios.length === 0 && <p>尚无场景。接通项目服务后，可从当前已提交项目创建。</p>}
          {scenarios.map((scenario) => (
            <div className="scenario-choice" key={scenario.identity.scenarioId}>
              <button
                type="button"
                aria-pressed={current?.identity.scenarioId === scenario.identity.scenarioId}
                onClick={() => setSelected(scenario.identity.scenarioId)}
              >
                {scenario.name}
                <small>
                  {scenario.maxRounds} 轮 · 产能 {scenario.capacity} 单/轮
                </small>
              </button>
              <label>
                <input
                  type="checkbox"
                  checked={compared.includes(scenario.identity.scenarioId)}
                  onChange={(event) =>
                    setCompared(
                      event.target.checked
                        ? [...compared, scenario.identity.scenarioId]
                        : compared.filter((id) => id !== scenario.identity.scenarioId),
                    )
                  }
                />
                加入对比：{scenario.name}
              </label>
            </div>
          ))}
        </section>
        <section className="scenario-panel" aria-labelledby="scenario-details">
          <h2 id="scenario-details">{current?.name ?? '运行详情'}</h2>
          {current && (
            <>
              <p>
                项目 {current.identity.projectId} / {current.identity.projectVersion} · 输入{' '}
                {current.identity.inputVersion}
              </p>
              <p>
                规则 {current.identity.ruleVersion} · 行为 {current.identity.behaviorVersion} · 语义{' '}
                {current.identity.semantics}
              </p>
              <p>数据来源：{current.source || '未记录'}</p>
              <ul>
                {current.assumptions.map((text, index) => (
                  <li key={index}>{text}</li>
                ))}
              </ul>
              <div className="scenario-actions">
                {runButton('运行场景', !!actions.run && !active, () =>
                  actions.run!(current.identity.scenarioId, current.identity.inputVersion),
                )}
                {runButton('恢复基准场景', !!actions.restore && !active, () =>
                  actions.restore!(current.identity.scenarioId),
                )}
                {run &&
                  runButton(
                    '取消运行',
                    !!actions.cancel && !!active && run.status !== 'cancelling',
                    () => actions.cancel!(run.id),
                  )}
              </div>
              {run ? (
                <RunDetails
                  run={run}
                  scenario={current}
                  actions={actions}
                  busy={busy}
                  perform={perform}
                />
              ) : (
                <p>还没有运行记录。运行后显示逐轮状态、指标和依据。</p>
              )}
              {current.runs.length > 1 && (
                <details>
                  <summary>历史运行（{current.runs.length - 1}）</summary>
                  {current.runs.slice(0, -1).map((history) => (
                    <RunDetails
                      key={history.id}
                      run={history}
                      scenario={current}
                      actions={actions}
                      busy={busy}
                      perform={perform}
                    />
                  ))}
                </details>
              )}
            </>
          )}
        </section>
      </div>
      <section className="scenario-panel" aria-labelledby="scenario-compare">
        <h2 id="scenario-compare">逐轮与最终指标对比</h2>
        {rows.length === 0 ? (
          <p>选择至少两个已有成功运行的场景。失败或尚未完成的运行不能作为成功结果对比。</p>
        ) : (
          <>
            <div className="scenario-table-scroll">
              <table>
                <caption>
                  每格依次为积压 / 累计完成 / 未闭环高危告警；最后一行为各场景该轮指标。
                </caption>
                <thead>
                  <tr>
                    <th scope="col">轮次</th>
                    {comparison.map(({ scenario, run: item }) => (
                      <th scope="col" key={scenario.identity.scenarioId}>
                        {scenario.name}
                        <small>
                          {item && resultLabel(item, scenario.identity)} ·{' '}
                          {item?.identity.inputVersion}
                        </small>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.round}>
                      <th scope="row">{row.round}</th>
                      {row.values.map((value, index) => (
                        <td key={comparison[index].scenario.identity.scenarioId}>
                          {value
                            ? `${value.backlog} / ${value.completed} / ${value.openHighAlerts}`
                            : '无该轮记录'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3>各场景最终已提交指标</h3>
            <ul>
              {comparison.map(({ scenario, run: item }) => {
                const final = item?.rounds.at(-1)
                return (
                  <li key={scenario.identity.scenarioId}>
                    {scenario.name}：
                    {final
                      ? `第 ${final.number} 轮 · 积压 ${final.metrics.backlog} 单 · 累计完成 ${final.metrics.completed} 单 · 未闭环高危 ${final.metrics.openHighAlerts} 条`
                      : '没有已提交轮次'}
                  </li>
                )
              })}
            </ul>
            <ul>
              {comparison.map(({ scenario, run: item }) => (
                <li key={scenario.identity.scenarioId}>
                  {scenario.name}：{item && completionLabel(item)}
                </li>
              ))}
            </ul>
          </>
        )}
        <dl>
          {metricDefinitions.map(([name, formula]) => (
            <div key={name}>
              <dt>{name}</dt>
              <dd>{formula}</dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  )
}

function RunDetails({
  run,
  scenario,
  actions,
  busy,
  perform,
}: {
  run: RunView
  scenario: ScenarioView
  actions: ScenarioActions
  busy: boolean
  perform: (action: () => Promise<void>) => Promise<void>
}) {
  const terminal = ['succeeded', 'failed', 'cancelled'].includes(run.status)
  const last = run.rounds.at(-1)
  return (
    <article className="scenario-run">
      <h3>{resultLabel(run, scenario.identity)}</h3>
      <p>
        运行 {run.id} · 输入 {run.identity.inputVersion} · 最后已提交轮次 {last?.number ?? 0}
      </p>
      <p>
        项目 {run.identity.projectId} / {run.identity.projectVersion} · 规则{' '}
        {run.identity.ruleVersion} · 行为 {run.identity.behaviorVersion} · 语义{' '}
        {run.identity.semantics}
      </p>
      <p>
        引擎 {run.identity.engineVersion} · 依赖锁 {run.identity.dependencyLockHash}
      </p>
      <p>
        本次运行参数：最多 {run.evidence.maxRounds} 轮 · 产能 {run.evidence.capacity} 单/轮 ·{' '}
        {run.evidence.parameters}
      </p>
      <p>本次运行来源：{run.evidence.source || '未记录'}</p>
      <ul>
        {run.evidence.assumptions.map((text, index) => (
          <li key={index}>{text}</li>
        ))}
      </ul>
      <p role="status">{completionLabel(run)}</p>
      {run.errorMessage && <p role="alert">{run.errorMessage}</p>}
      {run.pendingEvents.length > 0 && (
        <details>
          <summary>未处理事件</summary>
          <p>{run.pendingEvents.join('、')}</p>
        </details>
      )}
      <p>
        {run.replayAvailable
          ? '重放所需记录已齐全'
          : `不可重放：${run.replayUnavailableReason || '输入或执行版本记录尚未齐全'}`}
      </p>
      <div className="scenario-actions">
        <button
          type="button"
          disabled={busy || !terminal || !run.replayAvailable || !actions.replay}
          onClick={() => void perform(() => actions.replay!(run.id))}
        >
          独立重放（从初始消费状态）
        </button>
        <button
          type="button"
          disabled={busy || !terminal || !last || !actions.resume}
          onClick={() => void perform(() => actions.resume!(run.id, last!.number))}
        >
          显式从最后快照续跑
        </button>
        <button
          type="button"
          disabled={busy || !terminal || !actions.deleteRun}
          onClick={() => void perform(() => actions.deleteRun!(run.id))}
        >
          删除此运行记录
        </button>
      </div>
      {run.rounds.map((round) => (
        <details key={round.number}>
          <summary>
            第 {round.number} 轮 · 积压 {round.metrics.backlog} 单 · 累计完成{' '}
            {round.metrics.completed} 单 · 未闭环高危 {round.metrics.openHighAlerts} 条
          </summary>
          <dl>
            <dt>输入事件</dt>
            <dd>{round.inputEvents.join('、') || '无'}</dd>
            <dt>本轮创建</dt>
            <dd>{round.created.join('、') || '无'}</dd>
            <dt>资源阶段完成</dt>
            <dd>{round.completed.join('、') || '无'}</dd>
            <dt>轮末积压（处理队列顺序）</dt>
            <dd>{round.backlog.join('、') || '无'}</dd>
            <dt>行为前推理</dt>
            <dd>{round.beforeInference}</dd>
            <dt>行为执行顺序</dt>
            <dd>{round.behaviorTrace.join(' → ') || '无触发'}</dd>
            <dt>轮末推理</dt>
            <dd>{round.endInference}</dd>
          </dl>
          <button
            type="button"
            disabled={busy || !terminal || !actions.resume}
            onClick={() => void perform(() => actions.resume!(run.id, round.number))}
          >
            显式从第 {round.number} 轮快照创建续跑
          </button>
        </details>
      ))}
    </article>
  )
}
