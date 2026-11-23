import { useEffect, useRef, useState } from 'react'
import { offlineCourse, offlineGlossary } from './content'
import {
  assistanceLabels,
  assistanceRank,
  contextKey,
  hintLabels,
  observeRecords,
  projectionRecord,
  searchGlossary,
  type RecordFloor,
  recordLabel,
  sameContext,
  statusLabel,
  validFeedback,
  validRecord,
} from './presentation'
import type {
  CheckFeedbackView,
  CourseReading,
  CourseTask,
  HintLevel,
  LearningActions,
  LearningRecordView,
  LearningWorkspaceProps,
  TaskContext,
} from './types'
import './learning.css'

const EMPTY_RECORDS: readonly LearningRecordView[] = []
const EMPTY_CONTEXTS: Readonly<Record<string, TaskContext>> = {}

export function LearningWorkspace(props: LearningWorkspaceProps) {
  return <WorkspaceSession key={JSON.stringify([props.generation, props.projectId])} {...props} />
}

function WorkspaceSession({
  projectId,
  contexts = EMPTY_CONTEXTS,
  records = EMPTY_RECORDS,
  actions,
  initialTaskId,
}: LearningWorkspaceProps) {
  const [selectedId, setSelectedId] = useState(
    offlineCourse.tasks.some((task) => task.id === initialTaskId)
      ? initialTaskId!
      : offlineCourse.firstTask,
  )
  // A disposable projection of acknowledged owner records; no local persistence or writes.
  const [observed, setObserved] = useState(records)
  const [acknowledged, setAcknowledged] = useState(() => observeRecords({}, records))
  if (records !== observed) {
    setObserved(records)
    setAcknowledged((old) => observeRecords(old, records))
  }
  const [term, setTerm] = useState('本体')
  const [termQuery, setTermQuery] = useState('')
  const selected = offlineCourse.tasks.find((task) => task.id === selectedId)!
  const index = offlineCourse.tasks.indexOf(selected)
  const glossary = offlineGlossary.find((entry) => entry.term === term)!
  const termMatches = searchGlossary(offlineGlossary, termQuery)
  function currentContext(taskId: string) {
    const value = contexts[taskId]
    return value?.projectId === projectId && value.taskId === taskId ? value : undefined
  }
  function currentFloor(context: TaskContext): RecordFloor | undefined {
    const related = Object.values(acknowledged).filter(
      ({ latest }) =>
        latest.context.projectId === context.projectId &&
        latest.context.taskId === context.taskId &&
        latest.context.attemptId === context.attemptId,
    )
    if (!related.length) return undefined
    return {
      recordVersion: acknowledged[contextKey(context)]?.floor.recordVersion ?? 0,
      maxHintLevel: Math.max(...related.map(({ floor }) => floor.maxHintLevel)),
      assistance: related
        .map(({ floor }) => floor.assistance)
        .sort((a, b) => assistanceRank(b) - assistanceRank(a))[0],
    }
  }
  function currentRecord(taskId: string) {
    const context = currentContext(taskId)
    if (!context) return undefined
    const record = projectionRecord(acknowledged[contextKey(context)], context)
    const floor = currentFloor(context)
    return record &&
      floor &&
      record.maxHintLevel >= floor.maxHintLevel &&
      assistanceRank(record.assistance) >= assistanceRank(floor.assistance)
      ? record
      : undefined
  }
  const current = currentContext(selectedId)
  const record = currentRecord(selectedId)
  const projection = current && acknowledged[contextKey(current)]
  const floor = current && currentFloor(current)
  const completed = offlineCourse.tasks.filter((task) => currentRecord(task.id)?.operationComplete)
  const transferSuccess = offlineCourse.tasks.filter(
    (task) => task.transfer && currentRecord(task.id)?.independentTransferSuccess,
  )
  const priorInput = records.some(
    (item) =>
      item.context.projectId === projectId &&
      item.context.taskId === selectedId &&
      (!current || !sameContext(item.context, current)),
  )
  function searchTerm(value: string) {
    setTermQuery(value)
    const match = searchGlossary(offlineGlossary, value)[0]
    if (match) setTerm(match.entry.term)
  }
  return (
    <div className="learning-workspace">
      <div className="learning-topline">
        <span>
          学习 / {offlineCourse.case} · 课程 {offlineCourse.version}
        </span>
        <span className="learning-offline">离线课程 · 无需模型 API</span>
      </div>
      <div className="learning-heading">
        <div>
          <p className="learning-kicker">从业务问题开始</p>
          <h1>一步一步，把知识用起来。</h1>
          <p>{offlineCourse.businessQuestion}</p>
        </div>
        <div className="learning-progress" aria-label="当前输入学习进度">
          <strong>
            {completed.length}
            <span> / {offlineCourse.tasks.length}</span>
          </strong>
          <span>任务经实际检查完成</span>
          <small>独立迁移成功 {transferSuccess.length} / 2</small>
        </div>
      </div>
      <div className="learning-grid">
        <aside className="learning-path" aria-label="学习路径">
          <h2>你的学习路径</h2>
          <ol>
            {offlineCourse.tasks.map((task, ordinal) => (
              <li key={task.id}>
                <button
                  type="button"
                  aria-current={task.id === selectedId ? 'step' : undefined}
                  onClick={() => setSelectedId(task.id)}
                >
                  <span className="learning-step-number">
                    {String(ordinal + 1).padStart(2, '0')}
                  </span>
                  <span>
                    <b>{task.module}</b>
                    <small>{recordLabel(currentRecord(task.id))}</small>
                  </span>
                </button>
              </li>
            ))}
          </ol>
          <p className="learning-path-note">提示随时可用。任务是否完成，以实际检查结果为准。</p>
        </aside>
        <TaskPanel
          key={current ? contextKey(current) : 'preview:' + selectedId}
          task={selected}
          index={index}
          context={current}
          record={record}
          floor={floor}
          recordConflict={Boolean(projection && !record)}
          actions={actions}
          priorInput={priorInput}
          onRecord={(value) => setAcknowledged((old) => observeRecords(old, [value]))}
          onNext={() => selected.next && setSelectedId(selected.next)}
          onTerm={(value) => {
            if (offlineGlossary.some((entry) => entry.term === value)) {
              setTerm(value)
              setTermQuery('')
            }
          }}
        />
        <aside className="learning-reference" aria-label="术语与学习说明">
          <section className="learning-glossary">
            <p className="learning-kicker">随用随查</p>
            <h2>术语帮助</h2>
            <label htmlFor="learning-term-search">搜索术语或别名</label>
            <input
              id="learning-term-search"
              type="search"
              placeholder="例如 主键 / PK"
              value={termQuery}
              onChange={(event) => searchTerm(event.target.value)}
            />
            {termMatches.length > 0 && (
              <ul className="learning-term-matches" aria-label="术语匹配结果">
                {termMatches.slice(0, 6).map(({ entry }) => (
                  <li key={entry.term}>
                    <button
                      type="button"
                      onClick={() => {
                        setTerm(entry.term)
                        setTermQuery('')
                      }}
                    >
                      {entry.term}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <label htmlFor="learning-term">选择一个术语</label>
            <select
              id="learning-term"
              value={term}
              onChange={(event) => {
                setTerm(event.target.value)
                setTermQuery('')
              }}
            >
              {offlineGlossary.map((entry) => (
                <option key={entry.term}>{entry.term}</option>
              ))}
            </select>
            <h3>{glossary.term}</h3>
            <p>{glossary.plain}</p>
            <p className="learning-example">
              <b>在这个项目里</b>
              {glossary.example}
            </p>
            <p className="learning-boundary-note">
              <b>边界</b>
              {glossary.boundary}
            </p>
            {glossary.aliases.length > 0 && (
              <p className="learning-aliases">
                <b>别名</b>
                {glossary.aliases.join('、')}
              </p>
            )}
            <details>
              <summary>查看技术定义</summary>
              <p>{glossary.technical}</p>
            </details>
          </section>
          <section className="learning-boundary">
            <h2>完成，不等于独立掌握</h2>
            <p>
              独立完成、部分提示、完整示范会分别记录。接受 Agent
              完整修改后，操作可以完成，该次尝试不计独立迁移成功。
            </p>
            <p>沙盘展示给定条件下的结果，不代表真实未来。</p>
            <p>阅读与自评只记录理解，不改变操作完成与独立迁移的判定。</p>
          </section>
        </aside>
      </div>
    </div>
  )
}

interface PanelProps {
  task: CourseTask
  index: number
  context: TaskContext | undefined
  record: LearningRecordView | undefined
  floor: RecordFloor | undefined
  recordConflict: boolean
  actions: LearningActions | undefined
  priorInput: boolean
  onRecord(record: LearningRecordView): void
  onNext(): void
  onTerm(term: string): void
}

function TaskPanel({
  task,
  index,
  context,
  record,
  floor,
  recordConflict,
  actions,
  priorInput,
  onRecord,
  onNext,
  onTerm,
}: PanelProps) {
  const [hint, setHint] = useState<{ level: HintLevel; text: string }>()
  const [feedback, setFeedback] = useState<CheckFeedbackView>()
  const [busy, setBusy] = useState<'hint' | 'check' | 'report'>()
  const [notice, setNotice] = useState('')
  const [collapsed, setCollapsed] = useState(false)
  const live = useRef(true)
  useEffect(() => {
    live.current = true
    return () => {
      live.current = false
    }
  }, [])
  const highestHint = Math.max(floor?.maxHintLevel ?? 0, hint?.level ?? 0)
  async function showHint(level: HintLevel) {
    const text = task.hints.find((item) => item.level === level)!.text
    setNotice('')
    if (!context) {
      if (task.transfer) {
        setNotice('请先打开迁移练习，记录提示使用后查看提示。')
        return
      }
      setHint({ level, text })
      return
    }
    if (!actions?.recordHint) {
      setNotice('提示使用记录暂不可用，请稍后重试。')
      return
    }
    setBusy('hint')
    try {
      const receipt = await actions.recordHint(context, level)
      if (!live.current) return
      if (
        !sameContext(receipt.context, context) ||
        receipt.level !== level ||
        !validRecord(receipt.record, context) ||
        receipt.record.maxHintLevel < Math.max(highestHint, level) ||
        receipt.record.assistance === 'independent' ||
        (floor &&
          (receipt.record.recordVersion <= floor.recordVersion ||
            assistanceRank(receipt.record.assistance) < assistanceRank(floor.assistance)))
      ) {
        setNotice('提示使用记录与当前任务不一致，请重试。')
        return
      }
      onRecord(receipt.record)
      setHint({ level, text })
    } catch {
      if (live.current) setNotice('提示使用记录未保存，请重试。')
    } finally {
      if (live.current) setBusy(undefined)
    }
  }
  async function checkTask() {
    if (!context || !actions?.checkTask) {
      setNotice('此任务的检查暂不可用，可先查看离线提示。')
      return
    }
    setBusy('check')
    setNotice('')
    try {
      const value = await actions.checkTask(context)
      if (!live.current) return
      if (
        !validFeedback(value, context, highestHint, floor) ||
        (floor && value.record.recordVersion <= floor.recordVersion) ||
        (!task.transfer && value.record.independentTransferSuccess)
      ) {
        setNotice('检查结果与当前输入或提示记录不一致，请重新检查。')
        return
      }
      onRecord(value.record)
      setFeedback(value)
    } catch {
      if (live.current) setNotice('检查未完成，请重试；当前不会标记为通过。')
    } finally {
      if (live.current) setBusy(undefined)
    }
  }
  async function exportReport() {
    if (!context || !actions?.exportReport) return
    setBusy('report')
    setNotice('')
    try {
      const result = await actions.exportReport(context)
      if (live.current)
        setNotice(
          sameContext(result.context, context) && result.exported
            ? '学习报告已导出。'
            : '报告尚未导出，请重试。',
        )
    } catch {
      if (live.current) setNotice('报告导出未完成，请重试。')
    } finally {
      if (live.current) setBusy(undefined)
    }
  }
  const visibleFeedback =
    feedback && context && validFeedback(feedback, context, highestHint, floor) && !recordConflict
      ? feedback
      : undefined
  const readings = task.readings ?? []
  return (
    <section className="learning-task" aria-labelledby="learning-task-title">
      <div className="learning-task-top">
        <span>
          任务 {String(index + 1).padStart(2, '0')} / {task.transfer ? '迁移练习' : task.module}
        </span>
        <span className="learning-state">
          <span className="learning-state-text">{statusLabel(record)}</span>
          {record && record.checkStatus === 'passed' && (
            <span className="learning-state-assist"> · {recordLabel(record)}</span>
          )}
        </span>
      </div>
      <button
        type="button"
        className="learning-task-collapse"
        aria-expanded={!collapsed}
        aria-controls="learning-task-body"
        onClick={() => setCollapsed((value) => !value)}
      >
        {collapsed ? `展开任务卡：${task.goal}` : '收起任务卡'}
      </button>
      <div
        id="learning-task-body"
        className={collapsed ? 'learning-task-body is-collapsed' : 'learning-task-body'}
      >
        <h2 id="learning-task-title">{task.goal}</h2>
        <p className="learning-task-instructions">{task.instructions}</p>
        {task.steps && task.steps.length > 0 && (
          <ol className="learning-steps" aria-label="任务步骤">
            {task.steps.map((step) => (
              <li key={step.index}>
                <b>
                  第 {step.index} 步 · {step.title}
                </b>
                <span className="learning-step-flag">{step.scored ? '计分' : '观察，不计分'}</span>
                <p>{step.text}</p>
              </li>
            ))}
          </ol>
        )}
        {context ? (
          <p className="learning-version">当前输入：{context.inputVersion}</p>
        ) : (
          <p className="learning-preview">课程预览 · 提示可阅读，当前不会保存学习进度。</p>
        )}
        {recordConflict && <p className="learning-warning">学习记录不一致，请重新检查。</p>}
        {priorInput && (
          <p className="learning-warning">之前的检查使用另一输入或尝试，本次需要重新检查。</p>
        )}
        <div className="learning-actions">
          <button
            type="button"
            className="learning-primary"
            disabled={Boolean(busy)}
            onClick={() => void checkTask()}
          >
            {busy === 'check' ? '正在检查…' : '检查我的操作'}
          </button>
          {actions?.openWorkspace && (
            <button
              type="button"
              className="learning-secondary"
              onClick={() => actions.openWorkspace?.(task.id)}
            >
              打开对应模块 ↗
            </button>
          )}
        </div>
        {readings.length > 0 && (
          <section className="learning-readings" aria-label="任务阅读">
            <div className="learning-section-heading">
              <h3>任务阅读</h3>
              <span>只读理解，不计为实作完成</span>
            </div>
            {readings.map((reading) => (
              <ReadingPanel key={reading.id} reading={reading} />
            ))}
          </section>
        )}
        <section className="learning-help" aria-label="离线分级提示">
          <div className="learning-section-heading">
            <h3>需要一点帮助？</h3>
            <span>从概念开始，也可直接查看完整示范</span>
          </div>
          <div className="learning-hint-levels">
            {([1, 2, 3, 4] as const).map((level) => (
              <button
                type="button"
                key={level}
                className={hint?.level === level ? 'is-selected' : ''}
                disabled={Boolean(busy)}
                aria-pressed={hint?.level === level}
                onClick={() => void showHint(level)}
              >
                <span>{String(level).padStart(2, '0')}</span>
                {hintLabels[level]}
              </button>
            ))}
          </div>
          <div className="learning-hint-content" aria-live="polite">
            {hint ? (
              <>
                <h4>{hintLabels[hint.level]}</h4>
                <p>{hint.text}</p>
                {hint.level === 4 && (
                  <p className="learning-assistance-note">
                    对应知识点：{task.knowledgePoints.join('、')}
                    。使用完整示范会记录辅助来源，不计本次独立迁移成功。
                  </p>
                )}
              </>
            ) : (
              <p>先试着完成操作，再选择你需要的提示层级。</p>
            )}
          </div>
        </section>
        <section className="learning-feedback" aria-label="检查反馈" aria-live="polite">
          <h3>检查反馈</h3>
          {feedback && !visibleFeedback && (
            <p className="learning-warning">学习记录已更新，请重新检查。</p>
          )}
          {notice && (
            <p className="learning-warning" role="status">
              {notice}
            </p>
          )}
          {visibleFeedback ? (
            <>
              <p className="learning-feedback-status">
                <span className="learning-feedback-status-text">
                  {statusLabel(visibleFeedback.record)}
                </span>
                <span className="learning-feedback-assist">
                  {recordLabel(visibleFeedback.record)}
                </span>
              </p>
              {task.transfer && (
                <p>
                  {visibleFeedback.record.independentTransferSuccess
                    ? '本次独立迁移成功。'
                    : '本次未计入独立迁移成功。'}
                </p>
              )}
              <FeedbackList
                title="已完成内容"
                values={visibleFeedback.completed}
                empty="尚无经实际检查确认的完成内容。"
              />
              <FeedbackList
                title="需要修复"
                values={visibleFeedback.repairs}
                empty="本次检查未报告待修复项。"
              />
              <FeedbackList
                title="改进建议"
                values={visibleFeedback.suggestions}
                empty="暂无额外建议。"
              />
              <p className="learning-evidence">
                检查依据：{visibleFeedback.record.evidenceIds.join('、') || '暂无实际依据'}
              </p>
            </>
          ) : (
            <p className="learning-muted">完成操作后运行检查，反馈将来自实际结果。</p>
          )}
          {record && (
            <p className="learning-assistance-note">
              本次提示最高层级：{record.maxHintLevel || '未使用'} ·{' '}
              {record.operationComplete
                ? assistanceLabels[record.assistance]
                : '辅助记录：' +
                  (record.assistance === 'independent'
                    ? '尚未使用提示'
                    : assistanceLabels[record.assistance])}
            </p>
          )}
        </section>
        <details className="learning-errors">
          <summary>常见错误与完成条件</summary>
          <ul>
            {task.commonErrors.map((text) => (
              <li key={text}>{text}</li>
            ))}
          </ul>
          <p>{task.completionCondition}</p>
        </details>
        <div className="learning-knowledge" aria-label="相关知识点">
          {task.knowledgePoints.map((point) =>
            offlineGlossary.some((entry) => entry.term === point) ? (
              <button type="button" key={point} onClick={() => onTerm(point)}>
                {point}
              </button>
            ) : (
              <span key={point}>{point}</span>
            ),
          )}
        </div>
        <div className="learning-bottom">
          {task.next ? (
            <button type="button" className="learning-next" onClick={onNext}>
              下一步：{offlineCourse.tasks.find((item) => item.id === task.next)!.module} →
            </button>
          ) : (
            <button
              type="button"
              className="learning-secondary"
              disabled={!context || !actions?.exportReport || Boolean(busy)}
              onClick={() => void exportReport()}
            >
              导出学习报告
            </button>
          )}
          {!task.next && !actions?.exportReport && <small>报告导出暂不可用。</small>}
        </div>
      </div>
    </section>
  )
}

function ReadingPanel({ reading }: { reading: CourseReading }) {
  return (
    <article className="learning-reading">
      <h4>
        {reading.title}
        {reading.optional && <span className="learning-reading-flag">可选</span>}
      </h4>
      <p className="learning-reading-source">来源：{reading.sourceRef}</p>
      <p className="learning-reading-summary">{reading.summary}</p>
      <details>
        <summary>展开阅读正文</summary>
        <p className="learning-reading-content">{reading.content}</p>
      </details>
      {reading.selfAssessment && reading.selfAssessment.length > 0 && (
        <SelfAssessment reading={reading} />
      )}
    </article>
  )
}

/** Local fixed answer key; reading and self assessment never change a score. */
function SelfAssessment({ reading }: { reading: CourseReading }) {
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [revealed, setRevealed] = useState<Record<string, boolean>>({})
  return (
    <fieldset className="learning-self-assessment">
      <legend>自评（只用于理解，不计入实作完成）</legend>
      {(reading.selfAssessment ?? []).map((item, index) => {
        const key = `${reading.id}:${index}`
        const chosen = answers[key]
        const shown = Boolean(revealed[key])
        return (
          <div key={key} className="learning-self-assessment-item">
            <p className="learning-self-assessment-question">{item.question}</p>
            {item.options.map((option) => (
              <label key={option.id} className="learning-self-assessment-option">
                <input
                  type="radio"
                  name={key}
                  value={option.id}
                  checked={chosen === option.id}
                  onChange={() => setAnswers((old) => ({ ...old, [key]: option.id }))}
                />
                <span>{option.text}</span>
              </label>
            ))}
            <button
              type="button"
              disabled={!chosen}
              onClick={() => setRevealed((old) => ({ ...old, [key]: true }))}
            >
              查看解析
            </button>
            {shown && (
              <p className="learning-self-assessment-result">
                {chosen === item.answerKey ? '回答正确。' : '回答不正确。'}
                {item.explanation}
              </p>
            )}
          </div>
        )
      })}
    </fieldset>
  )
}

function FeedbackList({
  title,
  values,
  empty,
}: {
  title: string
  values: readonly string[]
  empty: string
}) {
  return (
    <div className="learning-feedback-group">
      <h4>{title}</h4>
      {values.length ? (
        <ul>
          {values.map((text, index) => (
            <li key={index}>{text}</li>
          ))}
        </ul>
      ) : (
        <p>{empty}</p>
      )}
    </div>
  )
}
