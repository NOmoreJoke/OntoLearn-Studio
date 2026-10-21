import { useEffect, useRef, useState } from 'react'
import type { JobView } from '../../../../../../packages/contracts/src'
import {
  alarmTemplate,
  compileVisual,
  draftSchema,
  emptyDirections,
  type QueryDraft,
  type VisualQuery,
} from './draft'
import {
  acceptPage,
  exportPageCsv,
  queryMetadata,
  resultNotice,
  type QueryPageData,
} from './results'
import './query.css'

export interface QueryPageProps {
  // Catalog and saved drafts come from the owning project adapter, never inferred
  // from labels or fixtures. Parent must key this component by project identity.
  projectId: string
  historicalSnapshots?: { snapshotId: string; label: string }[]
  modelDraft?: QueryDraft
  catalog: {
    classes: { iri: string; label: string }[]
    predicates: { iri: string; label: string }[]
  }
  alarmVocabulary?: { alarmClass: string; severity: string; status: string }
  savedQueries?: QueryDraft[]
  job?: JobView
  result?: { metadata: unknown; page: unknown; columns: string[]; executedSparql: string }
  onExecuteDraft?: (
    draft: QueryDraft,
    input: { selection: 'current' | 'historical'; snapshotId: string | null },
  ) => Promise<void>
  onSaveDraft?: (draft: QueryDraft) => Promise<void>
  onNextPage?: (cursor: string) => Promise<void>
  onCancelJob?: (jobId: string) => Promise<void>
}
const initialDraft: QueryDraft = {
  name: '',
  description: '',
  sparql: '',
  scope: 'asserted',
  capabilityQuestion: '',
  source: 'editor',
}

export function QueryPage(props: QueryPageProps) {
  const [draft, setDraft] = useState<QueryDraft>(initialDraft)
  const [visual, setVisual] = useState<VisualQuery>({ classIri: '', fields: [], conditions: [] })
  const [snapshotId, setSnapshotId] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const request = useRef(0)
  const editRevision = useRef(0)
  useEffect(
    () => () => {
      request.current++
    },
    [],
  )
  const update = (patch: Partial<QueryDraft>) => {
    editRevision.current++
    setDraft((value) => ({ ...value, ...patch }))
    setNotice('草稿未保存；修改不改变已有结果。')
  }
  const action = async (operation: (() => Promise<void>) | undefined, success: string) => {
    if (!operation || busy) return
    const token = ++request.current
    const revision = editRevision.current
    setBusy(true)
    try {
      await operation()
      if (token === request.current)
        setNotice(
          success +
            (revision !== editRevision.current ? ' 当前编辑已变化，请再次处理新草稿。' : ''),
        )
    } catch {
      if (token === request.current)
        setNotice('操作未完成。请检查连接或输入后重试；已提交项目状态请以项目记录为准。')
    } finally {
      if (token === request.current) setBusy(false)
    }
  }
  const withDraft = (operation: QueryPageProps['onSaveDraft'], success: string) => {
    const parsed = draftSchema.safeParse(draft)
    if (!parsed.success) {
      setNotice('请填写查询名称和 SPARQL，并检查字段格式。')
      return
    }
    void action(operation ? () => operation(parsed.data) : undefined, success)
  }
  const build = (value: VisualQuery, source: 'visual' | 'template') => {
    try {
      const sparql = compileVisual(value)
      setVisual(value)
      update({ sparql, source })
    } catch {
      setNotice('无法生成查询。请选择有效对象、属性和 RDF 条件值。')
    }
  }
  let result:
    | { metadata: ReturnType<typeof queryMetadata>; page: QueryPageData | null; columns: string[] }
    | undefined
  let resultError = false
  if (props.result) {
    try {
      const metadata = queryMetadata(props.result.metadata)
      if (
        metadata.projectId !== props.projectId ||
        typeof props.result.executedSparql !== 'string' ||
        !props.result.executedSparql.trim() ||
        props.result.executedSparql.length > 65536
      )
        throw new Error('query.invalidIdentity')
      result = {
        metadata,
        page:
          metadata.payloadStatus === 'available'
            ? acceptPage(props.result.page, metadata, props.result.columns)
            : null,
        columns: props.result.columns,
      }
    } catch {
      resultError = true
    }
  }
  const job = props.job?.projectId === props.projectId ? props.job : undefined
  const activeJob = job && ['queued', 'running', 'cancelling'].includes(job.state)
  const download = () => {
    if (!result?.page) return
    const blob = new Blob(['\uFEFF', exportPageCsv(result.page, result.columns)], {
      type: 'text/csv;charset=utf-8',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'query-current-page.csv'
    link.click()
    URL.revokeObjectURL(url)
  }
  return (
    <section className="query-workspace" aria-label="本体查询">
      <header>
        <p className="query-eyebrow">项目内 · 只读查询</p>
        <h1>把业务问题变成可核对的查询</h1>
        <p>先选择范围，再查看 SPARQL；执行结果始终保留自己的输入版本。</p>
      </header>
      <div className="query-range">
        <label>
          数据范围
          <select
            value={draft.scope}
            onChange={(e) => update({ scope: e.target.value as QueryDraft['scope'] })}
          >
            <option value="asserted">断言事实</option>
            <option value="asserted+derived">断言事实＋当前推导结果</option>
          </select>
        </label>
        <label>
          执行输入
          <select value={snapshotId} onChange={(e) => setSnapshotId(e.target.value)}>
            <option value="">当前已提交输入</option>
            {(props.historicalSnapshots ?? []).map((snapshot) => (
              <option key={snapshot.snapshotId} value={snapshot.snapshotId}>
                {snapshot.label} · {snapshot.snapshotId}
              </option>
            ))}
          </select>
        </label>
        <p>{snapshotId ? `已选择历史快照 ${snapshotId}` : '下一次执行将使用当前已提交输入。'}</p>
      </div>
      <div className="query-columns">
        <section aria-label="查询构建">
          <h2>离线构建</h2>
          <button
            disabled={!props.alarmVocabulary}
            onClick={() => {
              if (props.alarmVocabulary) {
                try {
                  build(alarmTemplate(props.alarmVocabulary), 'template')
                  update({ name: '未闭环高危告警', source: 'template' })
                } catch {
                  setNotice('模板与当前项目词汇不匹配，请检查本体定义。')
                }
              }
            }}
          >
            模板：未闭环高危告警
          </button>
          {!props.alarmVocabulary && <p>当前项目尚未提供模板属性关联。</p>}
          <label>
            选择对象
            <select
              value={visual.classIri}
              onChange={(e) => setVisual({ ...visual, classIri: e.target.value })}
            >
              <option value="">请选择对象类</option>
              {props.catalog.classes.map((c) => (
                <option key={c.iri} value={c.iri}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <fieldset>
            <legend>返回字段（对象 IRI 始终保留）</legend>
            {props.catalog.predicates.map((p) => (
              <label className="query-check" key={p.iri}>
                <input
                  type="checkbox"
                  checked={visual.fields.some((f) => f.predicate === p.iri)}
                  onChange={(e) =>
                    setVisual({
                      ...visual,
                      fields: e.target.checked
                        ? [...visual.fields, { predicate: p.iri, label: p.label }]
                        : visual.fields.filter((f) => f.predicate !== p.iri),
                    })
                  }
                />
                {p.label}
              </label>
            ))}
          </fieldset>
          <fieldset>
            <legend>筛选条件（全部满足）</legend>
            {visual.conditions.map((condition, i) => (
              <div className="query-condition" key={i}>
                <select
                  aria-label={`条件 ${i + 1} 属性`}
                  value={condition.predicate}
                  onChange={(e) =>
                    setVisual({
                      ...visual,
                      conditions: visual.conditions.map((c, n) =>
                        n === i ? { ...c, predicate: e.target.value } : c,
                      ),
                    })
                  }
                >
                  <option value="">请选择属性</option>
                  {props.catalog.predicates.map((p) => (
                    <option key={p.iri} value={p.iri}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <select
                  aria-label={`条件 ${i + 1} 运算符`}
                  value={condition.operator}
                  onChange={(e) => {
                    const operator = e.target.value as VisualQuery['conditions'][number]['operator']
                    const changed =
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
                      conditions: visual.conditions.map((c, n) => (n === i ? changed : c)),
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
                {'value' in condition && (
                  <>
                    <select
                      aria-label={`条件 ${i + 1} RDF 类型`}
                      value={condition.value.kind}
                      onChange={(e) =>
                        setVisual({
                          ...visual,
                          conditions: visual.conditions.map((c, n) =>
                            n === i && 'value' in c
                              ? {
                                  ...c,
                                  value:
                                    e.target.value === 'iri'
                                      ? { kind: 'iri', value: c.value.value }
                                      : {
                                          kind: 'literal',
                                          value: c.value.value,
                                          datatype: null,
                                          language: null,
                                        },
                                }
                              : c,
                          ),
                        })
                      }
                    >
                      <option value="literal">字面量</option>
                      <option value="iri">IRI</option>
                    </select>
                    <input
                      aria-label={`条件 ${i + 1} 值`}
                      value={condition.value.value}
                      onChange={(e) =>
                        setVisual({
                          ...visual,
                          conditions: visual.conditions.map((c, n) =>
                            n === i && 'value' in c
                              ? { ...c, value: { ...c.value, value: e.target.value } }
                              : c,
                          ),
                        })
                      }
                    />
                    {condition.value.kind === 'literal' && (
                      <>
                        <input
                          placeholder="语言标签（可选）"
                          aria-label={`条件 ${i + 1} 语言`}
                          value={condition.value.language ?? ''}
                          onChange={(e) =>
                            setVisual({
                              ...visual,
                              conditions: visual.conditions.map((c, n) =>
                                n === i && 'value' in c && c.value.kind === 'literal'
                                  ? {
                                      ...c,
                                      value: { ...c.value, language: e.target.value || null },
                                    }
                                  : c,
                              ),
                            })
                          }
                        />
                        <input
                          placeholder="数据类型完整 IRI（可选）"
                          aria-label={`条件 ${i + 1} 数据类型`}
                          value={condition.value.datatype ?? ''}
                          onChange={(e) =>
                            setVisual({
                              ...visual,
                              conditions: visual.conditions.map((c, n) =>
                                n === i && 'value' in c && c.value.kind === 'literal'
                                  ? {
                                      ...c,
                                      value: { ...c.value, datatype: e.target.value || null },
                                    }
                                  : c,
                              ),
                            })
                          }
                        />
                      </>
                    )}
                  </>
                )}
                <button
                  aria-label={`删除条件 ${i + 1}`}
                  onClick={() =>
                    setVisual({
                      ...visual,
                      conditions: visual.conditions.filter((_, n) => n !== i),
                    })
                  }
                >
                  移除
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
          <button onClick={() => build(visual, 'visual')}>生成可见 SPARQL 草稿</button>
        </section>
        <section aria-label="查询草稿">
          <h2>查询草稿</h2>
          <label>
            名称
            <input
              maxLength={128}
              value={draft.name}
              onChange={(e) => update({ name: e.target.value })}
            />
          </label>
          <label>
            说明
            <textarea
              maxLength={4096}
              value={draft.description}
              onChange={(e) => update({ description: e.target.value })}
            />
          </label>
          <label>
            关联能力问题
            <input
              maxLength={4096}
              value={draft.capabilityQuestion}
              onChange={(e) => update({ capabilityQuestion: e.target.value })}
            />
          </label>
          <label>
            SPARQL
            <textarea
              className="query-code"
              spellCheck={false}
              maxLength={65536}
              value={draft.sparql}
              onChange={(e) => update({ sparql: e.target.value, source: 'editor' })}
            />
          </label>
          <p>
            仅支持项目内 SELECT /
            ASK；SERVICE、FROM、更新及其他外联能力由正式执行器拒绝。编辑草稿不代表已经执行。
          </p>
          <div className="query-actions">
            <button
              disabled={!props.onExecuteDraft || busy || !!activeJob}
              onClick={() =>
                withDraft(
                  props.onExecuteDraft
                    ? (value) =>
                        props.onExecuteDraft!(value, {
                          selection: snapshotId ? 'historical' : 'current',
                          snapshotId: snapshotId || null,
                        })
                    : undefined,
                  '执行请求已受理；结果以任务终态为准。',
                )
              }
            >
              执行查询
            </button>
            <button
              disabled={!props.onSaveDraft || busy}
              onClick={() => withDraft(props.onSaveDraft, '此版本草稿保存流程已完成。')}
            >
              保存到项目
            </button>
          </div>
          {!props.onExecuteDraft && <p>真实查询服务尚未接入，当前可编写草稿。</p>}
          {!props.onSaveDraft && <p>项目事务服务尚未接入，草稿尚未持久化。</p>}
          <h3>自然语言草稿</h3>
          <p>模型生成内容先进入可见编辑器，仍需用户执行。</p>
          <button
            disabled={!props.modelDraft}
            onClick={() => {
              const parsed = draftSchema.safeParse(props.modelDraft)
              if (parsed.success) update({ ...parsed.data, source: 'model' })
              else setNotice('模型草稿格式不兼容，请重新生成。')
            }}
          >
            查看 T08 提供的模型草稿
          </button>
          <h3>复用已保存查询</h3>
          {(props.savedQueries ?? []).map((saved, i) => (
            <button
              key={i}
              onClick={() => {
                const parsed = draftSchema.safeParse(saved)
                if (parsed.success) update(parsed.data)
                else setNotice('保存的查询格式不兼容，请检查项目版本。')
              }}
            >
              {saved.name}
            </button>
          ))}
        </section>
      </div>
      <p role="status" aria-live="polite">
        {notice}
      </p>
      {job && (
        <div className="query-task">
          <p>
            查询任务：
            {
              {
                queued: '排队中',
                running: '运行中',
                cancelling: '取消中',
                cancelled: '已取消',
                succeeded: '已成功',
                failed: '失败',
              }[job.state]
            }
          </p>
          {activeJob && (
            <button
              disabled={!props.onCancelJob || job.state === 'cancelling' || busy}
              onClick={() => {
                const selectedJob = job
                if (selectedJob)
                  void action(
                    props.onCancelJob ? () => props.onCancelJob!(selectedJob.jobId) : undefined,
                    '取消请求已受理；等待真实任务终态。',
                  )
              }}
            >
              取消查询
            </button>
          )}
        </div>
      )}
      <section aria-label="查询结果">
        <h2>结果</h2>
        {resultError && (
          <p role="alert">结果身份、范围或分页不匹配，未显示该载荷。请重新获取项目结果。</p>
        )}
        {!props.result && <p>尚未取得实际执行结果。模板和草稿不会生成示例结果。</p>}
        {result && (
          <>
            <p className="query-result-identity">{resultNotice(result.metadata)}</p>
            <details>
              <summary>本次实际执行的 SPARQL</summary>
              <pre>{props.result?.executedSparql}</pre>
            </details>
            <p>
              执行范围：{result.metadata.scope === 'asserted' ? '断言事实' : '断言事实＋推导结果'}
            </p>
            <ul>
              {result.metadata.staleReason.map((r, i) => (
                <li key={i}>
                  {r.code} · {r.dependency} · {r.before} → {r.after}
                </li>
              ))}
            </ul>
            {result.page ? (
              <>
                <div className="query-table">
                  <table>
                    <thead>
                      <tr>
                        {result.columns.map((c, i) => (
                          <th key={i}>{c}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.page.rows.map((row) => (
                        <tr key={row.rowId}>
                          {row.cells.map((cell, i) => (
                            <td key={i}>{cell === null ? '未记录' : String(cell)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {result.page.rows.length === 0 && (
                  <>
                    <p>
                      {result.page.nextCursor
                        ? '本页未记录匹配项，仍有后续页。'
                        : '本页未记录匹配项。'}
                    </p>
                    <ul>
                      {emptyDirections.map((direction) => (
                        <li key={direction}>{direction}</li>
                      ))}
                    </ul>
                  </>
                )}
                <p>仅展示当前页，最多 200 行；导出也仅包含当前页。</p>
                <div className="query-actions">
                  <button onClick={download}>导出当前页 CSV</button>
                  <button
                    disabled={!result.page.nextCursor || !props.onNextPage || busy}
                    onClick={() => {
                      const cursor = result?.page?.nextCursor
                      if (cursor)
                        void action(
                          props.onNextPage ? () => props.onNextPage!(cursor) : undefined,
                          '分页请求已完成。',
                        )
                    }}
                  >
                    下一页
                  </button>
                </div>
              </>
            ) : (
              <p>此结果载荷已回收。快照与结果身份保留，请明确选择输入后重新执行。</p>
            )}
          </>
        )}
      </section>
    </section>
  )
}
