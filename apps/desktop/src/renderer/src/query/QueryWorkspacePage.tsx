import { useEffect, useState, useSyncExternalStore } from 'react'
import { QueryResultPanel } from './QueryResultPanel'
import {
  alarmTemplate,
  alarmVocabulary,
  compileVisual,
  draftSchema,
  visualSchema,
  type VisualQuery,
} from './draft'
import { QueryWorkspaceController } from './workspace-controller'
import type { QueryDraftDTO } from './api002-source-types'
import './workspace.css'

export interface QueryWorkspacePageProps {
  /** App owns one retained instance per selected project, including unresolved intents. */
  controller: QueryWorkspaceController
  /** A real upstream draft only; no model call or permission is initiated here. */
  modelDraft?: QueryDraftDTO
}
const emptyVisual = (): VisualQuery => ({ classIri: '', fields: [], conditions: [] })
const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

export function QueryWorkspacePage({ controller, modelDraft }: QueryWorkspacePageProps) {
  const state = useSyncExternalStore(
    controller.subscribe,
    controller.getSnapshot,
    controller.getSnapshot,
  )
  useEffect(() => controller.connect(), [controller])
  return (
    <WorkspaceDocument
      key={state.document}
      controller={controller}
      modelDraft={modelDraft}
      state={state}
    />
  )
}
function WorkspaceDocument({
  controller,
  modelDraft,
  state,
}: QueryWorkspacePageProps & { state: ReturnType<QueryWorkspaceController['getSnapshot']> }) {
  const [discardConfirmed, setDiscardConfirmed] = useState(false)
  const [diffConsent, setDiffConsent] = useState('')
  const [visual, setVisual] = useState<VisualQuery>(emptyVisual)
  const [builderError, setBuilderError] = useState('')
  const [historicalId, setHistoricalId] = useState('')
  const facts = state.read?.domain.state.facts ?? []
  const classes = [
    ...new Set(
      facts
        .filter(
          (fact) =>
            fact.predicate === rdfType && fact.object?.startsWith('<') && fact.object.endsWith('>'),
        )
        .map((fact) => fact.object!.slice(1, -1)),
    ),
  ].sort()
  const predicates = [...new Set(facts.map((fact) => fact.predicate))].sort()
  const definitions =
    state.read?.domain.state.definitions.filter((value) => value.layer === 'query') ?? []
  const change = (patch: Partial<QueryDraftDTO>) => {
    setDiscardConfirmed(false)
    controller.editDraft(patch)
  }
  const active = state.job && !['succeeded', 'failed', 'cancelled'].includes(state.job.state)
  const blocked = state.busy || controller.hasUnresolvedWrite
  const replaceBlocked = blocked || (state.dirty && !discardConfirmed)
  const viewingHistory = state.resultView === 'history'
  const result = viewingHistory ? state.historyResult : state.result
  const resultLane = viewingHistory ? 'historyResult' : 'result'
  const consentKey = state.preview ? `${state.preview.ready.previewHash}:${state.preview.edit}` : ''
  const build = (template: boolean) => {
    try {
      const selected = template ? { classIri: visual.classIri, fields: [], conditions: [] } : visual
      const sparql = compileVisual(selected)
      if (template) setVisual(selected)
      change({
        sparql,
        source: template ? 'template' : 'visual',
        ...(template ? { name: '列出所选对象' } : {}),
      })
      setBuilderError('')
    } catch {
      setBuilderError('请核对对象、返回属性和 RDF 条件。未生成或执行查询。')
    }
  }
  // The template is only derived from the ontology that was really read.
  const templateVocabulary = alarmVocabulary(classes, predicates)
  const loadAlarmTemplate = () => {
    if (!templateVocabulary) return
    try {
      const template = alarmTemplate(templateVocabulary)
      setVisual(template)
      change({
        sparql: compileVisual(template),
        source: 'template',
        name: '高危未闭环告警',
      })
      setBuilderError('')
    } catch {
      setBuilderError('无法生成告警模板；请核对当前本体中的类与属性。未生成或执行查询。')
    }
  }
  return (
    <section className="query-workspace-page" aria-label="本体查询工作台">
      <header>
        <p>项目内 · 只读查询</p>
        <h1>查询、核对与复用</h1>
        <p>工作草稿、正式定义提交、查询执行分别记录；只有真实任务终态代表执行完成。</p>
      </header>
      <p>
        当前项目：<code>{state.projectId}</code>；领域版本{' '}
        {state.read?.domain.projectRevision ?? '待读取'}；工作草稿代际{' '}
        {state.read?.workspace.draft.state === 'missing'
          ? 0
          : (state.read?.workspace.draft.generation ?? '待读取')}
      </p>
      {state.dirty && (
        <label>
          <input
            type="checkbox"
            checked={discardConfirmed}
            onChange={(event) => setDiscardConfirmed(event.target.checked)}
          />
          我已保留当前编辑，允许重新载入或新建替换它
        </label>
      )}
      <div className="query-workspace-actions">
        <button
          disabled={replaceBlocked}
          onClick={() => {
            setDiscardConfirmed(false)
            void controller.open()
          }}
        >
          读取项目与持久工作草稿
        </button>
        <button
          disabled={replaceBlocked}
          onClick={() => {
            setDiscardConfirmed(false)
            setVisual(emptyVisual())
            controller.newQuery()
          }}
        >
          新建查询草稿
        </button>
      </div>
      {controller.hasUnresolvedWrite && (
        <p role="status">
          原操作或任务尚未完成对账。保留本工作台实例，不自动换 operation 或丢弃任务。
        </p>
      )}
      {state.read && state.draftBaseRevision !== state.read.domain.projectRevision && (
        <section role="alert">
          <p>
            工作草稿原领域基线 {state.draftBaseRevision ?? '未知'}，当前已读领域版本{' '}
            {state.read.domain.projectRevision}。未自动重绑旧稿。
          </p>
          <button disabled={blocked} onClick={() => controller.reviewCurrentBase()}>
            我已复核当前项目，明确把本草稿用于当前已读基线
          </button>
        </section>
      )}
      <div className="query-workspace-range">
        <label>
          数据范围
          <select
            value={state.draft.scope}
            onChange={(event) => change({ scope: event.target.value as QueryDraftDTO['scope'] })}
          >
            <option value="asserted">断言事实</option>
            <option value="asserted+derived">断言事实＋当前推导结果</option>
          </select>
        </label>
        {state.draft.scope === 'asserted+derived' && (
          <p>查询读取所选快照的断言事实及该快照可用的推导结论。请先在质量与推导工作台运行检查。</p>
        )}
        <label>
          执行输入
          <select
            value={state.selection.kind}
            onChange={(event) =>
              controller.setSelection(
                event.target.value === 'current'
                  ? { kind: 'current' }
                  : { kind: 'historical', snapshotId: historicalId },
              )
            }
          >
            <option value="current">当前已提交输入</option>
            <option value="historical">明确指定历史快照</option>
          </select>
        </label>
        {state.selection.kind === 'historical' && (
          <label>
            历史快照标识
            <input
              value={historicalId}
              onChange={(event) => {
                setHistoricalId(event.target.value)
                controller.setSelection({ kind: 'historical', snapshotId: event.target.value })
              }}
            />
          </label>
        )}
        <p>
          {state.selection.kind === 'historical'
            ? `已选择历史快照：${state.selection.snapshotId || '尚未填写'}`
            : '执行前由真实服务核对当前已提交输入。'}
        </p>
      </div>
      <div className="query-workspace-columns">
        <section aria-label="离线查询构建">
          <h2>模板与条件构建</h2>
          <section data-testid="query-template-list" aria-label="常用问题模板">
            <h3>常用问题模板</h3>
            <ul>
              <li>
                <button
                  type="button"
                  data-testid="query-template-alarm"
                  disabled={!templateVocabulary || replaceBlocked}
                  onClick={loadAlarmTemplate}
                >
                  高危未闭环告警
                </button>
              </li>
            </ul>
            {templateVocabulary ? (
              <p>
                模板依据当前已读取的本体推导：类 <code>{templateVocabulary.alarmClass}</code>
                ，等级属性 <code>{templateVocabulary.severity}</code>，状态属性{' '}
                <code>{templateVocabulary.status}</code>。载入只写入工作草稿，不会自动执行。
              </p>
            ) : (
              <p>当前已读取的本体尚未提供可识别的告警类与等级／状态属性；不会填入示例词表。</p>
            )}
          </section>
          <label>
            选择对象
            <select
              value={visual.classIri}
              onChange={(event) => setVisual({ ...visual, classIri: event.target.value })}
            >
              <option value="">请选择实际实例的对象类型</option>
              {classes.map((iri) => (
                <option key={iri} value={iri}>
                  {iri}
                </option>
              ))}
            </select>
          </label>
          <button disabled={!visual.classIri} onClick={() => build(true)}>
            模板：列出所选对象
          </button>
          {!classes.length && <p>已读取的断言事实尚未提供对象类型；不会填入示例目录。</p>}
          <fieldset>
            <legend>返回字段（对象 IRI 保留，最多 16 项）</legend>
            {predicates.map((iri) => (
              <label key={iri}>
                <input
                  type="checkbox"
                  checked={visual.fields.some((field) => field.predicate === iri)}
                  disabled={
                    visual.fields.length >= 16 &&
                    !visual.fields.some((field) => field.predicate === iri)
                  }
                  onChange={(event) =>
                    setVisual({
                      ...visual,
                      fields: event.target.checked
                        ? [...visual.fields, { predicate: iri, label: iri }]
                        : visual.fields.filter((field) => field.predicate !== iri),
                    })
                  }
                />
                {iri}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>筛选条件（全部满足）</legend>
            {visual.conditions.map((condition, index) => (
              <div className="query-workspace-condition" key={index}>
                <label>
                  条件 {index + 1} 属性
                  <select
                    value={condition.predicate}
                    onChange={(event) =>
                      setVisual({
                        ...visual,
                        conditions: visual.conditions.map((value, i) =>
                          i === index ? { ...value, predicate: event.target.value } : value,
                        ),
                      })
                    }
                  >
                    <option value="">请选择实际属性</option>
                    {predicates.map((iri) => (
                      <option key={iri} value={iri}>
                        {iri}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  运算
                  <select
                    value={condition.operator}
                    onChange={(event) => {
                      const operator = event.target
                        .value as VisualQuery['conditions'][number]['operator']
                      const value =
                        operator === 'exists' || operator === 'not-exists'
                          ? { predicate: condition.predicate, operator }
                          : {
                              predicate: condition.predicate,
                              operator,
                              value:
                                'value' in condition
                                  ? condition.value
                                  : {
                                      kind: 'literal' as const,
                                      value: '',
                                      language: null,
                                      datatype: null,
                                    },
                            }
                      setVisual({
                        ...visual,
                        conditions: visual.conditions.map((old, i) => (i === index ? value : old)),
                      })
                    }}
                  >
                    {[
                      ['eq', '等于'],
                      ['ne', '不等于'],
                      ['lt', '小于'],
                      ['le', '小于等于'],
                      ['gt', '大于'],
                      ['ge', '大于等于'],
                      ['exists', '有记录'],
                      ['not-exists', '未记录'],
                    ].map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
                {'value' in condition && (
                  <>
                    <label>
                      RDF 类型
                      <select
                        value={condition.value.kind}
                        onChange={(event) =>
                          setVisual({
                            ...visual,
                            conditions: visual.conditions.map((old, i) =>
                              i === index && 'value' in old
                                ? {
                                    ...old,
                                    value:
                                      event.target.value === 'iri'
                                        ? { kind: 'iri', value: old.value.value }
                                        : {
                                            kind: 'literal',
                                            value: old.value.value,
                                            language: null,
                                            datatype: null,
                                          },
                                  }
                                : old,
                            ),
                          })
                        }
                      >
                        <option value="literal">字面量</option>
                        <option value="iri">IRI</option>
                      </select>
                    </label>
                    <label>
                      条件值
                      <input
                        value={condition.value.value}
                        onChange={(event) =>
                          setVisual({
                            ...visual,
                            conditions: visual.conditions.map((old, i) =>
                              i === index && 'value' in old
                                ? { ...old, value: { ...old.value, value: event.target.value } }
                                : old,
                            ),
                          })
                        }
                      />
                    </label>
                    {condition.value.kind === 'literal' && (
                      <>
                        <label>
                          语言标签
                          <input
                            value={condition.value.language ?? ''}
                            onChange={(event) =>
                              setVisual({
                                ...visual,
                                conditions: visual.conditions.map((old, i) =>
                                  i === index && 'value' in old && old.value.kind === 'literal'
                                    ? {
                                        ...old,
                                        value: {
                                          ...old.value,
                                          language: event.target.value || null,
                                        },
                                      }
                                    : old,
                                ),
                              })
                            }
                          />
                        </label>
                        <label>
                          数据类型 IRI
                          <input
                            value={condition.value.datatype ?? ''}
                            onChange={(event) =>
                              setVisual({
                                ...visual,
                                conditions: visual.conditions.map((old, i) =>
                                  i === index && 'value' in old && old.value.kind === 'literal'
                                    ? {
                                        ...old,
                                        value: {
                                          ...old.value,
                                          datatype: event.target.value || null,
                                        },
                                      }
                                    : old,
                                ),
                              })
                            }
                          />
                        </label>
                      </>
                    )}
                  </>
                )}
                <button
                  onClick={() =>
                    setVisual({
                      ...visual,
                      conditions: visual.conditions.filter((_, i) => i !== index),
                    })
                  }
                >
                  移除条件 {index + 1}
                </button>
              </div>
            ))}
            <button
              disabled={visual.conditions.length >= 32}
              onClick={() =>
                setVisual({
                  ...visual,
                  conditions: [
                    ...visual.conditions,
                    {
                      predicate: '',
                      operator: 'eq',
                      value: { kind: 'literal', value: '', language: null, datatype: null },
                    },
                  ],
                })
              }
            >
              添加条件
            </button>
          </fieldset>
          <button disabled={!visualSchema.safeParse(visual).success} onClick={() => build(false)}>
            生成可见 SPARQL 草稿
          </button>
          {builderError && <p role="alert">{builderError}</p>}
        </section>
        <section aria-label="查询编辑">
          <h2>查询草稿</h2>
          <label>
            项目内查询标识
            <input
              maxLength={128}
              value={state.definitionId}
              onChange={(event) => controller.setDefinitionId(event.target.value)}
            />
          </label>
          <p>新标识只是拟提交目标；正式保存与身份以真实提交、原操作和重读定义为准。同名不合并。</p>
          <label>
            已提交查询
            <select value="" onChange={(event) => controller.setDefinitionId(event.target.value)}>
              <option value="">选择真实项目定义</option>
              {definitions.map((value) => (
                <option key={value.id} value={value.id}>
                  {value.id}
                </option>
              ))}
            </select>
          </label>
          <button
            disabled={replaceBlocked || !state.definitionId}
            onClick={() => void controller.load()}
          >
            按所选当前/历史输入载入定义
          </button>
          <label>
            名称
            <input
              maxLength={128}
              value={state.draft.name}
              onChange={(event) => change({ name: event.target.value })}
            />
          </label>
          <label>
            说明
            <textarea
              maxLength={4096}
              value={state.draft.description}
              onChange={(event) => change({ description: event.target.value })}
            />
          </label>
          <label>
            关联能力问题
            <textarea
              maxLength={4096}
              value={state.draft.capabilityQuestion}
              onChange={(event) => change({ capabilityQuestion: event.target.value })}
            />
          </label>
          <label>
            可见 SPARQL
            <textarea
              className="query-workspace-code"
              spellCheck={false}
              maxLength={65536}
              value={state.draft.sparql}
              onChange={(event) => change({ sparql: event.target.value, source: 'editor' })}
            />
          </label>
          <p>
            来源：{state.draft.source}
            。SERVICE、FROM、更新及其他不支持的能力由真实执行器拒绝，不以只读替代外联控制。
          </p>
          <button
            disabled={
              state.busy || (controller.hasUnresolvedWrite && state.pending?.kind !== 'draft')
            }
            onClick={() => void controller.saveDraft()}
          >
            {state.pending?.kind === 'draft'
              ? '以原 operation 和原参数重试草稿保存'
              : '保存工作草稿（不提交正式定义）'}
          </button>
          <button
            disabled={blocked || !state.read || state.selection.kind !== 'current'}
            onClick={() => void controller.prepare()}
          >
            读取正式保存的完整差异
          </button>
          <button
            disabled={
              state.busy || !!active || (!!state.pending && state.pending.kind !== 'execute')
            }
            onClick={() => void controller.execute()}
          >
            {state.pending?.kind === 'execute'
              ? '以原 intent 重取受理'
              : '执行已载入且未改变的受管定义'}
          </button>
          <h3>自然语言草稿</h3>
          <p>仅消费上游真实草稿；当前页面不调用模型，不把手写 SPARQL 计作模型验证。</p>
          <div data-testid="query-model-draft">
            <button
              disabled={!modelDraft || (state.dirty && !discardConfirmed)}
              onClick={() => {
                const parsed = draftSchema.safeParse(modelDraft)
                if (parsed.success) controller.replaceDraft({ ...parsed.data, source: 'model' })
              }}
            >
              将上游模型草稿放入编辑器（替换当前内容）
            </button>
            {modelDraft && (
              <p data-testid="query-model-draft-summary">
                上游草稿：{modelDraft.name} · 来源 {modelDraft.source}
                ；载入后仍需人工核对，未自动提交。
              </p>
            )}
          </div>
        </section>
      </div>
      <p role="status" aria-live="polite">
        {state.notice}
      </p>
      {state.error && (
        <p role="alert">受限错误码：{state.error.code}。当前编辑、原操作与真实任务保留。</p>
      )}
      {state.draftReceipt && (
        <p>
          工作草稿持久回执：operation <code>{state.draftReceipt.operationId}</code>；generation{' '}
          {state.draftReceipt.generation}；不代表正式定义保存。
        </p>
      )}
      {state.preview && (
        <section aria-label="正式提交完整差异">
          <h2>正式提交前核对全部差异</h2>
          <p>
            基线 {state.preview.ready.baseRevision}；Diff SHA{' '}
            <code>{state.preview.ready.manifest.documentHash}</code>；全部分段已核验。
          </p>
          <pre>{JSON.stringify(state.preview.diff, null, 2)}</pre>
          <label>
            <input
              type="checkbox"
              checked={diffConsent === consentKey}
              onChange={(event) => setDiffConsent(event.target.checked ? consentKey : '')}
            />
            我已核对完整差异，确认提交此版本
          </label>
          <button
            disabled={blocked || diffConsent !== consentKey}
            onClick={() => void controller.confirmAndCommit()}
          >
            明确确认并提交真实任务
          </button>
        </section>
      )}
      {state.pending && (
        <p>
          保留原 {state.pending.kind} 操作：
          <code>
            {state.pending.kind === 'commit'
              ? state.pending.operationId
              : state.pending.args.operationId}
          </code>
        </p>
      )}
      {state.pending?.kind === 'commit' && (
        <button disabled={state.busy} onClick={() => void controller.reconcileCommit()}>
          按原 operation 对账（不重提提交）
        </button>
      )}
      {state.pending?.kind === 'commit' && (
        <div>
          <button disabled={state.busy} onClick={() => void controller.recoverOriginalCommit()}>
            按原确认与 operation 取回受理（不生成新操作）
          </button>
          <button disabled={state.busy} onClick={() => controller.restartCommitList()}>
            开始新一轮固定列表对账（保留原操作）
          </button>
          <button disabled={state.busy} onClick={() => void controller.findOriginalCommitJob()}>
            读取原 operation 的固定 Job 列表下一页
          </button>
        </div>
      )}
      <section aria-label="历史查询结果恢复">
        <h2>历史查询结果</h2>
        <p>
          读取本项目已持久化的查询任务，明确选择原任务恢复结果；不会重新执行查询或替换当前编辑。
        </p>
        <button disabled={state.busy} onClick={() => void controller.readQueryHistory(true)}>
          刷新历史查询任务
        </button>
        {state.history && (
          <>
            <p>
              固定任务列表第 {state.history.page} 页；本页查询任务 {state.history.jobs.length} 项。
            </p>
            <ul>
              {state.history.jobs.map((job) => (
                <li key={job.jobId}>
                  <p>
                    查询 {String((job.input as Record<string, unknown>).definitionId)} · {job.state}
                  </p>
                  <p>
                    原任务 <code>{job.jobId}</code>；原输入快照 <code>{job.inputSnapshotId}</code>
                  </p>
                  <button
                    disabled={state.busy}
                    onClick={() => void controller.restoreQueryResult(job.jobId)}
                  >
                    恢复此查询任务的结果
                  </button>
                </li>
              ))}
            </ul>
            {state.history.jobs.length === 0 && (
              <p>本页没有查询任务；可继续读取后页，未判定整个项目无结果。</p>
            )}
            <button
              disabled={state.busy || state.history.cursor === null}
              onClick={() => void controller.readQueryHistory()}
            >
              历史任务下一页
            </button>
          </>
        )}
        {viewingHistory && state.historySelection && (
          <>
            <p>
              正在查看原任务 <code>{state.historySelection.jobId}</code>，原输入快照{' '}
              <code>{state.historySelection.inputSnapshotId}</code>。
            </p>
            <p>结果的当前／历史输入及过期状态分别显示在结果面板；不套用编辑器此刻的数据选择。</p>
            <button
              disabled={state.busy}
              onClick={() => void controller.restoreQueryResult(state.historySelection!.jobId)}
            >
              重新读取所选结果与过期状态
            </button>
            <button disabled={state.busy} onClick={() => controller.showCurrentResult()}>
              返回本次执行结果
            </button>
          </>
        )}
      </section>
      {state.job && (
        <section aria-label="真实查询或提交任务">
          {state.jobObservationConflict && (
            <p role="alert">原任务状态记录互相矛盾；保留相关原任务与提交责任，暂不能完成核验。</p>
          )}
          <p>
            原 Job <code>{state.job.jobId}</code>：{state.job.state}；原定义 {state.jobDefinitionId}
            。编辑变化不会改变该任务输入。
          </p>
          {state.cancelRequested && <p>取消请求已受理，等待真实终态。</p>}
          {state.watchPending && <p>受理已保留；观察失败可刷新原任务，不能新建替代。</p>}
          <button disabled={state.busy} onClick={() => void controller.refreshJob()}>
            刷新任务、原操作与固定结果
          </button>
          <button
            disabled={state.busy || !active || state.jobKind !== 'execute' || state.cancelRequested}
            onClick={() => void controller.cancel()}
          >
            请求取消原查询任务
          </button>
        </section>
      )}
      {result && (
        <section aria-label={viewingHistory ? '所选历史任务结果' : '本次执行结果'}>
          <button
            disabled={state.busy || !result.descriptor}
            onClick={() => void controller.readText(null, 0, resultLane)}
          >
            读取执行文本第一页
          </button>
          <button
            disabled={
              state.busy ||
              (result.descriptor as { query?: { kind: string } } | undefined)?.query?.kind !==
                'SELECT'
            }
            onClick={() => void controller.readRows(null, 0, resultLane)}
          >
            读取 SELECT 结果第一页
          </button>
          <QueryResultPanel
            key={`${resultLane}:${result.resultId}`}
            {...result}
            graphSource={state.read}
            rowsLoading={state.busy}
            textLoading={state.busy}
            onNextRows={(request) =>
              void controller.readRows(request.cursor, request.startIndex, resultLane)
            }
            onNextText={(request) =>
              void controller.readText(request.cursor, request.startUtf8Byte, resultLane)
            }
          />
        </section>
      )}
    </section>
  )
}
