import { useEffect, useId, useState, useSyncExternalStore } from 'react'
import { BehaviorController } from './controller'
import {
  emptyDraft,
  sameContext,
  type Action,
  type BehaviorDraft,
  type BehaviorResult,
  type BehaviorServices,
  type Catalog,
  type Context,
  type Condition,
  type EventChange,
  type Value,
} from './model'
import { errorText, resultHeading, resultSections } from './presentation'
import './behavior.css'

export interface BehaviorWorkspaceProps {
  context: Context
  catalog: Catalog
  initialDraft?: BehaviorDraft
  services?: BehaviorServices
  onDraftChange?: (draft: BehaviorDraft) => void
}
const unavailableServices: BehaviorServices = {}
export function BehaviorWorkspace({
  context,
  catalog,
  initialDraft,
  services = unavailableServices,
  onDraftChange,
}: BehaviorWorkspaceProps) {
  const [controller] = useState(
    () => new BehaviorController(context, catalog, initialDraft, services),
  )
  const state = useSyncExternalStore(
    controller.subscribe,
    controller.getSnapshot,
    controller.getSnapshot,
  )
  const id = useId()
  useEffect(() => {
    controller.configure(context, catalog, services, initialDraft)
  }, [controller, context, catalog, services, initialDraft])
  useEffect(() => () => controller.invalidate(), [controller])
  const matches = sameContext(context, state.context)
  const draft = state.draft
  const patch = (value: Partial<BehaviorDraft>) => {
    const next = { ...draft, ...value }
    controller.editDraft(next)
    onDraftChange?.(structuredClone(next))
  }
  const updateAction = (index: number, value: Action) =>
    patch({ actions: draft.actions.map((action, i) => (i === index ? value : action)) })
  const updateChanges = (index: number, changes: EventChange[]) =>
    controller.editEvents(
      state.events.map((event, i) => (i === index ? { ...event, changes } : event)),
    )
  const updateEvent = (index: number, value: Partial<(typeof state.events)[number]>) =>
    controller.editEvents(
      state.events.map((event, i) => (i === index ? { ...event, ...value } : event)),
    )
  return (
    <section className="behavior-workspace" aria-labelledby={`${id}-title`}>
      <div className="behavior-topline">
        <div>
          <p className="behavior-kicker">05 / 行为定义</p>
          <h1 id={`${id}-title`}>把业务规则，写成可验证的行动。</h1>
          <p>先描述「当、如果、那么」，再在隔离副本中核对每一步。</p>
        </div>
        <span className="behavior-badge">内部安全动作</span>
      </div>
      <aside className="behavior-isolation" aria-label="隔离范围">
        <strong>仅测试副本 / 沙盘快照</strong>
        <p>正式项目数据不在执行范围内。失败或取消须由真实服务确认收尾。</p>
        <dl>
          <div>
            <dt>项目</dt>
            <dd>{context.projectId || '未选择'}</dd>
          </div>
          <div>
            <dt>输入版本</dt>
            <dd>{context.inputVersion || '未提供'}</dd>
          </div>
          <div>
            <dt>行为版本</dt>
            <dd>{context.behaviorVersion || '未提供'}</dd>
          </div>
          <div>
            <dt>隔离副本</dt>
            <dd>{context.scopeId || '未提供'}</dd>
          </div>
        </dl>
      </aside>
      <div className="behavior-columns">
        <div className="behavior-editor" aria-label="行为草稿编辑">
          <section className="behavior-card">
            <div className="behavior-section-heading">
              <h2>行为草稿</h2>
              <span>本地编辑 · 尚未保存</span>
            </div>
            <div className="behavior-fields">
              <Field label="唯一行为 ID">
                <input
                  value={draft.id}
                  onChange={(e) => patch({ id: e.target.value })}
                  maxLength={200}
                />
              </Field>
              <Field label="行为名称">
                <input
                  value={draft.name}
                  onChange={(e) => patch({ name: e.target.value })}
                  maxLength={500}
                />
              </Field>
              <Field label="业务说明" wide>
                <textarea
                  value={draft.description}
                  onChange={(e) => patch({ description: e.target.value })}
                  maxLength={500}
                />
              </Field>
              <Field label="优先级（高值先执行）">
                <input
                  type="number"
                  value={Number.isFinite(draft.priority) ? draft.priority : ''}
                  onChange={(e) => patch({ priority: e.target.valueAsNumber })}
                />
              </Field>
              <Field label="草稿版本">
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={Number.isFinite(draft.version) ? draft.version : ''}
                  onChange={(e) => patch({ version: e.target.valueAsNumber })}
                />
              </Field>
              <label className="behavior-checkbox">
                <input
                  type="checkbox"
                  checked={draft.enabled}
                  onChange={(e) => patch({ enabled: e.target.checked })}
                />
                启用此行为
              </label>
            </div>
          </section>
          <section className="behavior-card">
            <p className="behavior-step">当</p>
            <h2>发生什么事件？</h2>
            <Field label="触发事件类型">
              <input
                value={draft.trigger}
                onChange={(e) => patch({ trigger: e.target.value })}
                maxLength={200}
              />
            </Field>
          </section>
          <section className="behavior-card">
            <p className="behavior-step">如果</p>
            <div className="behavior-section-heading">
              <h2>满足这一组条件</h2>
              <span>全部满足 · 仅一组</span>
            </div>
            <p className="behavior-help">
              所有实例读取同一份行为前「断言＋推导」冻结快照。未知对象不会当作已验证。
            </p>
            {draft.conditions.map((condition, index) => (
              <fieldset key={index} className="behavior-entry">
                <legend>条件 {index + 1}</legend>
                <ConditionEditor
                  condition={condition}
                  onChange={(value) =>
                    patch({
                      conditions: draft.conditions.map((item, i) => (i === index ? value : item)),
                    })
                  }
                />
                <button
                  className="behavior-secondary"
                  onClick={() =>
                    patch({ conditions: draft.conditions.filter((_, i) => i !== index) })
                  }
                >
                  移除条件 {index + 1}
                </button>
              </fieldset>
            ))}
            <button
              className="behavior-secondary"
              disabled={draft.conditions.length >= 50}
              onClick={() =>
                patch({
                  conditions: [
                    ...draft.conditions,
                    {
                      kind: 'equals',
                      object: '',
                      property: '',
                      value: { kind: 'string', value: '' },
                    },
                  ],
                })
              }
            >
              ＋ 添加条件
            </button>
          </section>
          <section className="behavior-card">
            <p className="behavior-step">那么</p>
            <h2>依次执行安全动作</h2>
            <p className="behavior-help">
              仅创建个体、更新属性、添加关系、生成内部通知记录。没有邮件、消息或外部数据库操作。
            </p>
            {draft.actions.map((action, index) => (
              <fieldset className="behavior-entry" key={index}>
                <legend>动作 {index + 1}</legend>
                <Field label="动作类型">
                  <select
                    value={action.kind}
                    onChange={(e) =>
                      updateAction(index, newAction(e.target.value as Action['kind']))
                    }
                  >
                    <option value="create">创建个体</option>
                    <option value="update">更新单值属性</option>
                    <option value="relate">添加关系</option>
                    <option value="notify">生成通知记录</option>
                  </select>
                </Field>
                {action.kind === 'notify' ? (
                  <Field label="通知内容">
                    <textarea
                      value={action.message}
                      onChange={(e) => updateAction(index, { ...action, message: e.target.value })}
                      maxLength={500}
                    />
                  </Field>
                ) : (
                  <>
                    <Field label={action.kind === 'create' ? '新对象 ID' : '对象 ID'}>
                      <input
                        value={action.object}
                        onChange={(e) => updateAction(index, { ...action, object: e.target.value })}
                      />
                    </Field>
                    {action.kind === 'create' ? (
                      <Field label="类 ID">
                        <input
                          value={action.classId}
                          onChange={(e) =>
                            updateAction(index, { ...action, classId: e.target.value })
                          }
                        />
                      </Field>
                    ) : (
                      <Field label="属性 / 关系 ID">
                        <input
                          value={action.property}
                          onChange={(e) =>
                            updateAction(index, { ...action, property: e.target.value })
                          }
                        />
                      </Field>
                    )}
                    {action.kind === 'update' && (
                      <ValueEditor
                        value={action.value}
                        onChange={(value) => updateAction(index, { ...action, value })}
                      />
                    )}
                    {action.kind === 'relate' && (
                      <Field label="关系目标对象 ID">
                        <input
                          value={action.target}
                          onChange={(e) =>
                            updateAction(index, { ...action, target: e.target.value })
                          }
                        />
                      </Field>
                    )}
                  </>
                )}
                <div className="behavior-actions">
                  <button
                    className="behavior-secondary"
                    disabled={index === 0}
                    onClick={() => patch({ actions: move(draft.actions, index, -1) })}
                  >
                    上移
                  </button>
                  <button
                    className="behavior-secondary"
                    disabled={index === draft.actions.length - 1}
                    onClick={() => patch({ actions: move(draft.actions, index, 1) })}
                  >
                    下移
                  </button>
                  <button
                    className="behavior-secondary"
                    onClick={() => patch({ actions: draft.actions.filter((_, i) => i !== index) })}
                  >
                    移除动作 {index + 1}
                  </button>
                </div>
              </fieldset>
            ))}
            <button
              className="behavior-secondary"
              disabled={draft.actions.length >= 100}
              onClick={() => patch({ actions: [...draft.actions, newAction('create')] })}
            >
              ＋ 添加动作
            </button>
            <Field label="预期业务效果">
              <textarea
                value={draft.effect}
                onChange={(e) => patch({ effect: e.target.value })}
                maxLength={500}
              />
            </Field>
          </section>
        </div>
        <div className="behavior-testing">
          <section className="behavior-card">
            <div className="behavior-section-heading">
              <h2>样本事件</h2>
              <span>按输入次序</span>
            </div>
            <p className="behavior-help">
              输入项目内对象和事件载荷；此私有编辑器的载荷为 JSON
              键值对象，不执行代码。重复运行原事件用于核对幂等，不自动换 ID。
            </p>
            {state.events.map((event, index) => (
              <fieldset className="behavior-entry" key={index}>
                <legend>事件 {index + 1}</legend>
                <Field label="唯一事件 ID">
                  <input
                    value={event.id}
                    onChange={(e) => updateEvent(index, { id: e.target.value })}
                  />
                </Field>
                <Field label="事件类型">
                  <input
                    value={event.type}
                    onChange={(e) => updateEvent(index, { type: e.target.value })}
                  />
                </Field>
                <Field label="事件内容（JSON 对象）">
                  <textarea
                    className="behavior-code"
                    value={event.payload}
                    onChange={(e) => updateEvent(index, { payload: e.target.value })}
                    maxLength={20000}
                    spellCheck={false}
                  />
                </Field>
                <div className="behavior-event-changes">
                  <p className="behavior-help">场景断言变更（按顺序应用）</p>
                  {event.changes.map((change, changeIndex) => (
                    <fieldset className="behavior-entry" key={changeIndex}>
                      <legend>事实变更 {changeIndex + 1}</legend>
                      <Field label="变更方式">
                        <select
                          value={change.operation}
                          onChange={(e) =>
                            updateChanges(
                              index,
                              event.changes.map((item, i) =>
                                i === changeIndex
                                  ? {
                                      ...item,
                                      operation: e.target.value as EventChange['operation'],
                                    }
                                  : item,
                              ),
                            )
                          }
                        >
                          <option value="add">添加断言</option>
                          <option value="remove">删除指定断言</option>
                          <option value="set">更新单值属性</option>
                        </select>
                      </Field>
                      <Field label="事实对象 ID">
                        <input
                          value={change.object}
                          onChange={(e) =>
                            updateChanges(
                              index,
                              event.changes.map((item, i) =>
                                i === changeIndex ? { ...item, object: e.target.value } : item,
                              ),
                            )
                          }
                        />
                      </Field>
                      <Field label="事实属性 ID">
                        <input
                          value={change.property}
                          onChange={(e) =>
                            updateChanges(
                              index,
                              event.changes.map((item, i) =>
                                i === changeIndex ? { ...item, property: e.target.value } : item,
                              ),
                            )
                          }
                        />
                      </Field>
                      <ValueEditor
                        value={change.value}
                        onChange={(value) =>
                          updateChanges(
                            index,
                            event.changes.map((item, i) =>
                              i === changeIndex ? { ...item, value } : item,
                            ),
                          )
                        }
                      />
                      <button
                        className="behavior-secondary"
                        onClick={() =>
                          updateChanges(
                            index,
                            event.changes.filter((_, i) => i !== changeIndex),
                          )
                        }
                      >
                        移除事实变更 {changeIndex + 1}
                      </button>
                    </fieldset>
                  ))}
                  <button
                    className="behavior-secondary"
                    disabled={event.changes.length >= 100}
                    onClick={() =>
                      updateChanges(index, [
                        ...event.changes,
                        {
                          operation: 'add',
                          object: '',
                          property: '',
                          value: { kind: 'string', value: '' },
                        },
                      ])
                    }
                  >
                    ＋ 添加事实变更
                  </button>
                </div>
                <div className="behavior-actions">
                  <button
                    className="behavior-secondary"
                    disabled={index === 0}
                    onClick={() => controller.editEvents(move(state.events, index, -1))}
                  >
                    事件上移
                  </button>
                  <button
                    className="behavior-secondary"
                    disabled={index === state.events.length - 1}
                    onClick={() => controller.editEvents(move(state.events, index, 1))}
                  >
                    事件下移
                  </button>
                  <button
                    className="behavior-secondary"
                    onClick={() =>
                      controller.editEvents(state.events.filter((_, i) => i !== index))
                    }
                  >
                    移除事件 {index + 1}
                  </button>
                </div>
              </fieldset>
            ))}
            <button
              className="behavior-secondary"
              disabled={state.events.length >= 100}
              onClick={() =>
                controller.editEvents([
                  ...state.events,
                  { id: '', type: '', payload: '{}', changes: [] },
                ])
              }
            >
              ＋ 添加样本事件
            </button>
            <div className="behavior-run">
              <button
                className="behavior-secondary"
                disabled={!matches}
                onClick={() => controller.validate()}
              >
                检查本地结构
              </button>
              <button
                disabled={!matches || !services.runSample || Boolean(state.pending)}
                onClick={() => void controller.run()}
              >
                {state.pending?.kind === 'run' ? '测试请求进行中…' : '在隔离副本中测试'}
              </button>
              {state.pending?.kind === 'run' && (
                <button
                  className="behavior-secondary"
                  disabled={!services.cancelSample || state.cancelling}
                  onClick={() => void controller.cancel()}
                >
                  {state.cancelling ? '等待取消确认…' : '请求取消测试'}
                </button>
              )}
            </div>
            {!services.runSample && (
              <p className="behavior-pending">
                隔离执行能力待接入。当前可编辑并检查本地结构，不能取得行为通过结论。
              </p>
            )}
            {state.issues.length > 0 && (
              <ul className="behavior-errors" aria-label="本地结构问题">
                {state.issues.map((issue, index) => (
                  <li key={index}>
                    {issue.path}：{issue.message}
                  </li>
                ))}
              </ul>
            )}
            <p role="status" aria-live="polite" className="behavior-notice">
              {matches ? state.notice : '正在切换输入上下文；旧结果已隔离。'}
            </p>
          </section>
          <section className="behavior-card" aria-label="执行结果">
            <div className="behavior-section-heading">
              <h2>执行依据与轨迹</h2>
              <button
                className="behavior-secondary"
                disabled={
                  !matches || !state.result || !services.refreshResult || Boolean(state.pending)
                }
                onClick={() => void controller.refresh()}
              >
                刷新此运行
              </button>
            </div>
            <p className="behavior-help">
              稳定顺序：优先级高→低，行为 ID 升序，事件输入序号升序，事件 ID
              升序；实例内按动作序号执行。
            </p>
            {matches && state.result ? (
              <>
                <p className="behavior-result-heading">{resultHeading(state.result)}</p>
                {state.resultRevision !== state.revision && (
                  <p className="behavior-pending">
                    草稿或样本已修改；以下结果保留原请求依据，请重新测试当前编辑内容。
                  </p>
                )}
                <ResultDetails result={state.result} />
              </>
            ) : (
              <div className="behavior-empty">
                <strong>尚无可核验的运行结果</strong>
                <p>真实服务返回后显示触发原因、动作顺序、差异和通知记录。</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </section>
  )
}
function Field({
  label,
  children,
  wide,
}: {
  label: string
  children: React.ReactNode
  wide?: boolean
}) {
  return (
    <label className={`behavior-field${wide ? ' behavior-wide' : ''}`}>
      <span>{label}</span>
      {children}
    </label>
  )
}
function ConditionEditor({
  condition,
  onChange,
}: {
  condition: Condition
  onChange: (condition: Condition) => void
}) {
  return (
    <>
      <Field label="条件类型">
        <select
          value={condition.kind}
          onChange={(e) => {
            const kind = e.target.value as Condition['kind']
            const object = condition.kind === 'always' ? '' : condition.object
            onChange(
              kind === 'always'
                ? { kind }
                : kind === 'type'
                  ? { kind, object, classId: '' }
                  : kind === 'exists'
                    ? { kind, object, property: '' }
                    : {
                        kind,
                        object,
                        property: '',
                        value: { kind: 'string', value: '' },
                      },
            )
          }}
        >
          <option value="always">无额外条件（恒真）</option>
          <option value="equals">属性值等于</option>
          <option value="exists">已记录属性</option>
          <option value="type">属于类型（含行为前推导）</option>
        </select>
      </Field>
      {condition.kind === 'always' ? (
        <p className="behavior-help">显式恒真；此项不附加对象或属性限制，同组其他条件仍须满足。</p>
      ) : (
        <>
          <Field label="条件对象 ID">
            <input
              value={condition.object}
              onChange={(e) => onChange({ ...condition, object: e.target.value })}
            />
          </Field>
          {condition.kind === 'type' ? (
            <Field label="条件类 ID">
              <input
                value={condition.classId}
                onChange={(e) => onChange({ ...condition, classId: e.target.value })}
              />
            </Field>
          ) : (
            <Field label="条件属性 ID">
              <input
                value={condition.property}
                onChange={(e) => onChange({ ...condition, property: e.target.value })}
              />
            </Field>
          )}
        </>
      )}
      {condition.kind === 'equals' && (
        <ValueEditor
          value={condition.value}
          onChange={(value) => onChange({ ...condition, value })}
        />
      )}
    </>
  )
}
function ValueEditor({ value, onChange }: { value: Value; onChange: (value: Value) => void }) {
  return (
    <div className="behavior-fields">
      <Field label="值类型">
        <select
          value={value.kind}
          onChange={(e) => {
            const kind = e.target.value as Value['kind']
            onChange(
              kind === 'boolean'
                ? { kind, value: false }
                : kind === 'number'
                  ? { kind, value: 0 }
                  : { kind, value: '' },
            )
          }}
        >
          <option value="string">文字</option>
          <option value="number">数值</option>
          <option value="boolean">布尔</option>
          <option value="iri">对象 IRI</option>
        </select>
      </Field>
      <Field label="比较 / 写入值">
        {value.kind === 'boolean' ? (
          <select
            value={String(value.value)}
            onChange={(e) => onChange({ kind: 'boolean', value: e.target.value === 'true' })}
          >
            <option value="true">true</option>
            <option value="false">false</option>
          </select>
        ) : value.kind === 'number' ? (
          <input
            type="number"
            value={Number.isFinite(value.value) ? value.value : ''}
            onChange={(e) => onChange({ kind: 'number', value: e.target.valueAsNumber })}
          />
        ) : (
          <input
            value={value.value}
            onChange={(e) => onChange({ kind: value.kind, value: e.target.value })}
          />
        )}
      </Field>
    </div>
  )
}
function newAction(kind: Action['kind']): Action {
  switch (kind) {
    case 'create':
      return { kind, object: '', classId: '' }
    case 'update':
      return { kind, object: '', property: '', value: { kind: 'string', value: '' } }
    case 'relate':
      return { kind, object: '', property: '', target: '' }
    case 'notify':
      return { kind, message: '' }
  }
}
function move<T>(values: T[], index: number, direction: number): T[] {
  const next = [...values]
  const target = index + direction
  if (target < 0 || target >= next.length) return values
  ;[next[index], next[target]] = [next[target], next[index]]
  return next
}
function ResultDetails({ result }: { result: BehaviorResult }) {
  const sections = resultSections(result)
  const diffLabel = result.committed
    ? '隔离副本 Diff'
    : result.state === 'candidate'
      ? '候选 Diff'
      : '未提交尝试 Diff'
  return (
    <>
      <dl className="behavior-versions">
        <div>
          <dt>运行</dt>
          <dd>{result.runId}</dd>
        </div>
        <div>
          <dt>请求</dt>
          <dd>{result.binding.requestId}</dd>
        </div>
        <div>
          <dt>断言快照版本</dt>
          <dd>{result.assertionVersion}</dd>
        </div>
        <div>
          <dt>推导快照版本</dt>
          <dd>{result.inferenceVersion}</dd>
        </div>
        <div>
          <dt>执行语义版本</dt>
          <dd>{result.semanticsVersion}</dd>
        </div>
      </dl>
      {result.freshnessDetail && <p className="behavior-pending">{result.freshnessDetail}</p>}
      {result.error && (
        <p role="alert" className="behavior-errors">
          {errorText[result.error]}
        </p>
      )}
      <ResultList title="条件评估 / 触发原因" items={sections.conditions} />
      <ResultList title="动作轨迹（服务返回顺序）" items={sections.actions} ordered />
      <ResultList title={`${diffLabel} · 新增`} items={sections.added} />
      <ResultList title={`${diffLabel} · 撤回`} items={sections.removed} />
      <ResultList title="内部通知记录" items={sections.notifications} />
      <p className="behavior-help">
        候选计划展示拟议差异；失败、取消中的动作轨迹由服务标明回滚或未执行，不能据此推断正式数据变化。
      </p>
    </>
  )
}
function ResultList({
  title,
  items,
  ordered,
}: {
  title: string
  items: string[]
  ordered?: boolean
}) {
  const List = ordered ? 'ol' : 'ul'
  return (
    <section className="behavior-result-section">
      <h3>{title}</h3>
      {items.length ? (
        <List>
          {items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </List>
      ) : (
        <p>服务未提供条目。</p>
      )}
    </section>
  )
}
export { emptyDraft }
