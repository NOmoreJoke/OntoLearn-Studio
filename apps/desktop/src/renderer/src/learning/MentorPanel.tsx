import { useSyncExternalStore, useState } from 'react'
import type {
  LearningReadingDTO,
  LearningTaskStateDTO,
  ProjectLearningReadDTO,
} from '@ontolearn/contracts'
import { explainError } from '../task-presentation'
import {
  offlineCourse,
  offlineGlossary,
  supportsLearningFixture,
  type LearningFixtureTaskId,
} from './content'
import { hintLabels, searchGlossary } from './presentation'
import {
  LearningController,
  type LearningControllerState,
  deriveTaskStale,
  displayedCheckStatus,
  mentorAssistanceText,
} from './learning-controller'
import { selectedTaskOrigins, TaskOriginSelectors, type TaskOriginChoices } from './task-origins'
import './mentor.css'

export type MentorPanelProps = {
  controller: LearningController
  /** projectBusy || workspaceFrozen || managementBlocked || checkpointBlocked. */
  disabled: boolean
  /** The workspace's freshest domain snapshot identity (project read or the
   *  live ontology session). Differing from the learning read's bound snapshot
   *  projects the derived stale view without any background RPC. */
  currentDomainSnapshotId?: string
  /** Switch the workspace to the ontology editor for a repair ChangeSet. */
  onOpenOntologyRepair(): void
  /** Switch the workspace to the query workbench (optional for older hosts). */
  onOpenQueryWorkspace?: () => void
  onOpenQualityWorkspace?: () => void
  onLoadTaskFixture?: (taskId: LearningFixtureTaskId) => void
  taskFixtureStatus?: string
  taskFixture?: {
    taskId: LearningFixtureTaskId
    rows: readonly unknown[]
    approve(): void
    discard(): void
  }
  /** Independent G-base practice reset: create a fresh practice project. */
  onResetToGBase?: (taskId: string) => void
  /** Open the workspace checkpoints drawer instead of scrolling across waterfall sections. */
  onOpenCheckpoints?: () => void
  /** Serialized checkpoint refresh after a check that created a checkpoint. */
  refreshCheckpoints(): Promise<void>
}

/** Tasks whose G-base practice domain is a fresh example project. */
const GBASE_RESET_TASKS: ReadonlySet<string> = new Set(['business-ontology', 'query', 'quality'])

/** Scroll the checkpoints panel into view without inventing extra navigation state. */
export function scrollToProjectCheckpoints(
  root: Pick<Document, 'getElementById'> = document,
): boolean {
  const target = root.getElementById('project-checkpoints')
  if (!target) return false
  target.scrollIntoView({ block: 'start', behavior: 'auto' })
  return true
}

/** PRD 8.2/8.9 mentor rail inside the workspace split; never a third sidebar.
 *  All persistence flows through the Step 1 named bridge, never storage. */
export function MentorPanel(props: MentorPanelProps) {
  const { controller } = props
  const state = useSyncExternalStore(
    controller.subscribe,
    controller.getSnapshot,
    controller.getSnapshot,
  )
  return (
    <MentorSession
      key={JSON.stringify([state.selectedProjectId, state.focusedTaskId])}
      {...props}
      state={state}
    />
  )
}

function MentorSession({
  controller,
  disabled,
  currentDomainSnapshotId,
  onOpenOntologyRepair,
  onOpenQueryWorkspace,
  onOpenQualityWorkspace,
  onLoadTaskFixture,
  taskFixture,
  taskFixtureStatus,
  onResetToGBase,
  onOpenCheckpoints,
  refreshCheckpoints,
  state,
}: MentorPanelProps & { state: LearningControllerState }) {
  const learning: ProjectLearningReadDTO | undefined = state.learning
  const task = learning?.tasks.find((item) => item.taskId === state.focusedTaskId)
  const courseTask = offlineCourse.tasks.find((item) => item.id === state.focusedTaskId)
  const stale = deriveTaskStale(task, currentDomainSnapshotId, learning?.domainSnapshotRef)
  const [glossaryQuery, setGlossaryQuery] = useState('')
  const [explanationOpen, setExplanationOpen] = useState(false)
  const [checking, setChecking] = useState(false)
  const [originChoices, setOriginChoices] = useState<TaskOriginChoices>(['', ''])
  const [openingReading, setOpeningReading] = useState<string>()
  const ordinal = courseTask ? offlineCourse.tasks.indexOf(courseTask) + 1 : undefined
  const fixture = taskFixture?.taskId === task?.taskId ? taskFixture : undefined
  const setupTask = task && supportsLearningFixture(task.taskId) ? task.taskId : undefined
  const blocked = disabled || state.busy || !!fixture
  const feedback = state.lastCheck?.feedback ?? task?.lastFeedback ?? undefined
  const assistance = mentorAssistanceText(task)
  return (
    <aside className="mentor-panel" data-testid="mentor-panel" aria-label="导师与学习任务">
      <header className="mentor-heading">
        <p className="eyebrow">导师 · 离线课程</p>
        <h2>
          任务 {ordinal ? String(ordinal).padStart(2, '0') : '--'} ·{' '}
          {courseTask?.module ?? '学习任务'}
        </h2>
        <p className="mentor-task-goal">{courseTask?.goal}</p>
        <p className="mentor-check-state">
          <span data-testid="learning-check-status">
            {displayedCheckStatus(task, currentDomainSnapshotId, learning?.domainSnapshotRef)}
          </span>
          {assistance && (
            <>
              {' · '}
              <span data-testid="learning-assistance-label">{assistance}</span>
            </>
          )}
        </p>
      </header>
      {!learning && (
        <p className="mentor-notice" data-testid="mentor-learning-unavailable">
          {state.error
            ? '学习状态读取失败；可重新打开项目后再试。'
            : '学习状态尚未读取；打开项目后会自动加载。'}
        </p>
      )}
      {state.error && (
        <div role="alert" data-testid="mentor-error" className="mentor-error">
          {explainError(state.error, 'task').what}
        </div>
      )}
      {task && (
        <>
          <section className="mentor-task-card" aria-label="当前任务卡">
            <p className="mentor-instructions">{task.instructions}</p>
            <p className="mentor-completion">
              <b>完成条件</b>
              {task.completionCondition}
            </p>
            {task.steps.length > 0 && (
              <ol className="mentor-steps" aria-label="任务步骤">
                {task.steps.map((step) => (
                  <li key={step.index}>
                    <b>
                      第 {step.index} 步 · {step.title}
                    </b>
                    <span className="mentor-step-flag">
                      {step.scored ? '计分' : '观察，不计分'}
                    </span>
                    <p>{step.text}</p>
                  </li>
                ))}
              </ol>
            )}
            <p className="mentor-version">当前绑定输入：{task.inputVersion}</p>
            {setupTask && onOpenQualityWorkspace && (
              <button
                type="button"
                data-testid="learning-open-quality-workspace"
                disabled={blocked}
                onClick={onOpenQualityWorkspace}
              >
                打开质量与推导工作台
              </button>
            )}
            {setupTask && onLoadTaskFixture && (
              <button
                type="button"
                className="mentor-secondary"
                data-testid="learning-load-task-fixture"
                disabled={blocked}
                onClick={() => onLoadTaskFixture(setupTask)}
              >
                载入本关初始数据
              </button>
            )}
            {setupTask && taskFixtureStatus && (
              <p className="mentor-notice" role="status" data-testid="learning-task-fixture-status">
                {taskFixtureStatus}
              </p>
            )}
            {fixture && (
              <section data-testid="learning-task-fixture-preview" aria-label="本关初始数据差异">
                <h3>本关初始数据差异</h3>
                <pre className="mentor-fixture-diff">{JSON.stringify(fixture.rows, null, 2)}</pre>
                <button
                  type="button"
                  data-testid="learning-confirm-task-fixture"
                  disabled={disabled || state.busy}
                  onClick={fixture.approve}
                >
                  确认载入初始数据
                </button>
                <button
                  type="button"
                  className="mentor-secondary"
                  disabled={disabled || state.busy}
                  onClick={fixture.discard}
                >
                  放弃载入
                </button>
              </section>
            )}
            <button
              type="button"
              className="mentor-secondary"
              disabled={blocked}
              onClick={() => void controller.restartAttempt()}
            >
              重新开始本任务尝试
            </button>
            {onResetToGBase && GBASE_RESET_TASKS.has(task.taskId) && (
              <button
                type="button"
                className="mentor-secondary"
                data-testid="learning-reset-gbase"
                disabled={blocked}
                onClick={() => onResetToGBase(task.taskId)}
              >
                独立还原 G-base（新建练习项目）
              </button>
            )}
            <button
              type="button"
              className="mentor-secondary"
              data-testid="learning-scroll-checkpoints"
              onClick={() => {
                if (onOpenCheckpoints) onOpenCheckpoints()
                else scrollToProjectCheckpoints()
              }}
            >
              查看检查点恢复（当前项目内还原）
            </button>
          </section>
          {task.readings.length > 0 && (
            <section className="mentor-readings" aria-label="任务阅读与自测">
              <h3>任务阅读</h3>
              <p className="mentor-muted">阅读与自测仅记录理解，不改变操作完成或独立迁移判定。</p>
              {task.readings.map((reading) => (
                <ReadingCard
                  key={reading.id}
                  reading={reading}
                  task={task}
                  busy={blocked}
                  opening={openingReading === reading.id}
                  onOpen={(readingId) => {
                    setOpeningReading(readingId)
                    void controller
                      .recordObservation({ kind: 'reading-opened', readingId })
                      .finally(() => setOpeningReading(undefined))
                  }}
                  onAnswer={(readingId, questionIndex, selectedOptionId) =>
                    void controller.recordObservation({
                      kind: 'self-assessment-answered',
                      readingId,
                      questionIndex,
                      selectedOptionId,
                    })
                  }
                  lastAssessment={state.lastAssessment}
                />
              ))}
            </section>
          )}
          <section className="mentor-glossary" aria-label="实时术语帮助">
            <h3>术语帮助</h3>
            <label htmlFor="mentor-glossary-search">搜索术语或别名</label>
            <input
              id="mentor-glossary-search"
              type="search"
              data-testid="mentor-glossary-search"
              placeholder="例如 主键 / Primary Key / PK"
              value={glossaryQuery}
              onChange={(event) => setGlossaryQuery(event.target.value)}
            />
            {(glossaryQuery.trim()
              ? searchGlossary(learning?.glossary ?? offlineGlossary, glossaryQuery)
              : []
            )
              .slice(0, 3)
              .map(({ entry }) => (
                <article
                  key={entry.term}
                  className="mentor-glossary-entry"
                  data-testid="mentor-glossary-entry"
                >
                  <h4>{entry.term}</h4>
                  <p>{entry.plain}</p>
                  <p className="mentor-boundary">
                    <b>边界</b>
                    {entry.boundary}
                  </p>
                  {entry.aliases.length > 0 && (
                    <p className="mentor-aliases">
                      <b>别名</b>
                      {entry.aliases.join('、')}
                    </p>
                  )}
                </article>
              ))}
          </section>
          <section className="mentor-actions" aria-label="离线学习辅助">
            <TaskOriginSelectors
              taskId={task.taskId}
              values={originChoices}
              disabled={blocked}
              onChange={setOriginChoices}
            />
            <div className="mentor-action-buttons">
              <button
                type="button"
                data-testid="mentor-btn-hint"
                disabled={blocked}
                onClick={() => void controller.requestHint()}
              >
                给我提示
              </button>
              <button
                type="button"
                data-testid="mentor-btn-check"
                disabled={blocked || checking}
                onClick={() => {
                  setChecking(true)
                  void controller
                    .checkTask(selectedTaskOrigins(task.taskId, originChoices))
                    .then(async (receipt) => {
                      // FR-004: surface a newly created guided-stage checkpoint
                      // immediately, strictly after the check reply settled.
                      if (receipt?.guidedStageCheckpointRef) await refreshCheckpoints()
                    })
                    .finally(() => setChecking(false))
                }}
              >
                {checking ? '正在检查…' : '检查我的操作'}
              </button>
              <button
                type="button"
                data-testid="mentor-btn-demo"
                disabled={blocked}
                onClick={() => void controller.requestDemonstration()}
              >
                查看示范
              </button>
              <button
                type="button"
                data-testid="mentor-btn-explain"
                disabled={blocked}
                aria-expanded={explanationOpen}
                onClick={() => setExplanationOpen((value) => !value)}
              >
                解释结果
              </button>
            </div>
            {state.notice && (
              <p className="mentor-notice" role="status">
                {state.notice}
              </p>
            )}
            {task.revealedHints.length > 0 && (
              <div className="mentor-hints" aria-label="已解锁提示（只读）">
                <h4>已解锁提示</h4>
                <ul>
                  {task.revealedHints.map((hint) => (
                    <li key={hint.level} data-testid="mentor-revealed-hint" data-level={hint.level}>
                      <b>
                        第 {hint.level} 级 · {hintLabels[hint.level] ?? hint.kind}
                      </b>
                      <p>{hint.text}</p>
                    </li>
                  ))}
                </ul>
                <p className="mentor-muted">
                  提示按写入顺序只读展示；使用完整示范会记录辅助来源，不计独立迁移成功。
                </p>
              </div>
            )}
            {explanationOpen && (
              <div
                className="mentor-explanation"
                data-testid="mentor-explanation"
                aria-label="离线检查解释"
              >
                <h4>离线解释（无需模型）</h4>
                {stale && <p>当前检查结果已过期：输入在本检查后发生了新的提交，请重新检查。</p>}
                {feedback ? (
                  <>
                    <FeedbackGroup
                      title="已完成内容"
                      values={feedback.completed}
                      empty="尚无经实际检查确认的完成内容。"
                    />
                    <FeedbackGroup
                      title="需要修复"
                      values={feedback.repairs}
                      empty="本次检查未报告待修复项。"
                    />
                    <FeedbackGroup
                      title="改进建议"
                      values={feedback.suggestions}
                      empty="暂无额外建议。"
                    />
                    <FeedbackGroup
                      title="相关知识点"
                      values={feedback.knowledgePoints}
                      empty="暂无。"
                    />
                  </>
                ) : (
                  <p>尚无检查反馈；先运行“检查我的操作”。</p>
                )}
                <FeedbackGroup title="常见错误" values={task.commonErrors} empty="暂无。" />
                <FeedbackGroup title="本任务知识点" values={task.knowledgePoints} empty="暂无。" />
              </div>
            )}
          </section>
          <section className="mentor-check-panel" aria-label="检查结果面板">
            <h3>检查结果</h3>
            <p className="mentor-check-state">
              状态：
              <span data-testid="learning-check-status-body">
                {displayedCheckStatus(task, currentDomainSnapshotId, learning?.domainSnapshotRef)}
              </span>
              {assistance && (
                <>
                  {' '}
                  · 归因：<span data-testid="learning-assistance-label-body">{assistance}</span>
                </>
              )}
            </p>
            <p data-testid="learning-operation-state">
              {task.operationComplete ? '操作完成：是' : '操作完成：否'}
              {task.transfer
                ? task.independentTransferSuccess
                  ? ' · 独立迁移成功：是'
                  : ' · 独立迁移成功：否'
                : ''}
            </p>
            {(task.guidedStageCheckpointRef || state.lastCheck?.guidedStageCheckpointRef) && (
              <p className="mentor-checkpoint-badge" data-testid="learning-guided-stage-badge">
                已自动创建引导阶段检查点（FR-004，同一任务仅一次）
              </p>
            )}
            {feedback && !stale && (
              <div className="mentor-feedback">
                <FeedbackGroup
                  title="已完成内容"
                  values={feedback.completed}
                  empty="尚无经实际检查确认的完成内容。"
                />
                <FeedbackGroup
                  title="需要修复"
                  values={feedback.repairs}
                  empty="本次检查未报告待修复项。"
                />
                <FeedbackGroup
                  title="改进建议"
                  values={feedback.suggestions}
                  empty="暂无额外建议。"
                />
                <FeedbackGroup
                  title="相关知识点"
                  values={feedback.knowledgePoints}
                  empty="暂无。"
                />
                {feedback.evidenceIds.length > 0 && (
                  <p className="mentor-evidence">检查依据：{feedback.evidenceIds.join('、')}</p>
                )}
              </div>
            )}
            {stale && (
              <p className="mentor-warning" role="status">
                检查结果已过期：输入在本检查后发生了新的提交。重新运行“检查我的操作”以获得当前结果。
              </p>
            )}
            <button
              type="button"
              data-testid="learning-open-ontology-repair"
              className="mentor-secondary"
              disabled={blocked}
              onClick={onOpenOntologyRepair}
            >
              打开本体构建修复
            </button>
            {onOpenQualityWorkspace && !setupTask && (
              <button
                type="button"
                data-testid="learning-open-quality-workspace"
                className="mentor-secondary"
                disabled={blocked}
                onClick={onOpenQualityWorkspace}
              >
                打开质量与推导工作台
              </button>
            )}
            {onOpenQueryWorkspace && (
              <button
                type="button"
                data-testid="learning-open-query-workspace"
                disabled={blocked}
                onClick={() => onOpenQueryWorkspace?.()}
              >
                打开本体查询
              </button>
            )}
            <p className="mentor-muted">
              修复需新建 ChangeSet；检查只报告偏差，不会自动回滚已提交的更改。
            </p>
          </section>
        </>
      )}
    </aside>
  )
}

function ReadingCard({
  reading,
  task,
  busy,
  opening,
  onOpen,
  onAnswer,
  lastAssessment,
}: {
  reading: LearningReadingDTO
  task: LearningTaskStateDTO
  busy: boolean
  opening: boolean
  onOpen(readingId: string): void
  onAnswer(readingId: string, questionIndex: number, selectedOptionId: string): void
  lastAssessment?: {
    readingId: string
    questionIndex: number
    selectedOptionId: string
    correct: boolean
    explanation: string
  }
}) {
  const opened = task.observations.openedReadingIds.includes(reading.id)
  return (
    <article className="mentor-reading" data-reading-id={reading.id}>
      <h4>
        {reading.title}
        {reading.optional && <span className="mentor-reading-flag">可选</span>}
      </h4>
      <p className="mentor-reading-summary">{reading.summary}</p>
      <button
        type="button"
        data-testid="learning-reading-open"
        disabled={busy || (opened && !opening)}
        onClick={() => onOpen(reading.id)}
      >
        {opening ? '正在打开…' : opened ? '已打开阅读' : `打开阅读：${reading.title}`}
      </button>
      {opened && (
        <div className="mentor-reading-body">
          <p className="mentor-reading-source">来源：{reading.sourceRef}</p>
          <p className="mentor-reading-content">{reading.content}</p>
        </div>
      )}
      {opened &&
        reading.selfAssessment?.map((item, questionIndex) => {
          const answered = task.observations.answeredAssessments.find(
            (entry) => entry.readingId === reading.id && entry.questionIndex === questionIndex,
          )
          const live =
            lastAssessment &&
            lastAssessment.readingId === reading.id &&
            lastAssessment.questionIndex === questionIndex
              ? lastAssessment
              : undefined
          const outcome = live ?? answered
          return (
            <fieldset key={questionIndex} className="mentor-self-assessment">
              <legend>自测（只用于理解，不计入实作完成）</legend>
              <p className="mentor-question">{item.question}</p>
              {item.options.map((option) => (
                <button
                  type="button"
                  key={option.id}
                  data-testid="learning-assessment-option"
                  data-option-id={option.id}
                  className={
                    (outcome?.selectedOptionId ?? answered?.selectedOptionId) === option.id
                      ? 'is-selected'
                      : ''
                  }
                  disabled={busy}
                  onClick={() => onAnswer(reading.id, questionIndex, option.id)}
                >
                  {option.text}
                </button>
              ))}
              {live && (
                <p className="mentor-assessment-outcome" data-testid="learning-assessment-outcome">
                  {live.correct ? '回答正确。' : '回答不正确。'}
                  {live.explanation}
                </p>
              )}
            </fieldset>
          )
        })}
    </article>
  )
}

function FeedbackGroup({
  title,
  values,
  empty,
}: {
  title: string
  values: readonly string[]
  empty: string
}) {
  return (
    <div className="mentor-feedback-group">
      <h5>{title}</h5>
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
