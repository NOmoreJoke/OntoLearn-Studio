import { useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from 'react'
import { manualFactPlan, newManualFactPlan } from './mainline-facts'
import { type OntologySession, sourceIdentity } from './mainline-session'
import { OntologyPage } from './OntologyPage'
import { entityDeletionImpact, entityEditPlan, projectOntology } from './mainline-ontology'
import type { RdfRow } from './view-model'
import './ontology.css'
import { OwnershipConflictDetailView } from './OwnershipConflictDetailView'

export type OntologyMainlinePageProps = {
  /** Host owns this instance and retires it synchronously before changing selection.
   * Construct a new instance with the actual bridge only after selection settles.
   */
  session: OntologySession
  /** Shell's actual document/session/selection generation; presentation fence only. */
  contextKey: string
}

export function OntologyMainlinePage(props: OntologyMainlinePageProps) {
  return <MainlineEditor key={props.contextKey} session={props.session} />
}

function MainlineEditor({ session }: { session: OntologySession }) {
  useEffect(() => session.connectForPage(), [session])
  return <SessionEditor session={session} />
}

function SessionEditor({ session }: { session: OntologySession }) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot)
  const factLifetime = useRef<
    { session: OntologySession; sequence: number; active: boolean } | undefined
  >(undefined)
  // Detach synchronously at commit, before the owner's passive session disposal.
  // A new attachment never revives an older hash continuation, even in StrictMode.
  useLayoutEffect(() => {
    const lifetime = { session, sequence: 0, active: true }
    factLifetime.current = lifetime
    return () => {
      lifetime.active = false
      lifetime.sequence++
      session.discardPreview()
      if (factLifetime.current === lifetime) factLifetime.current = undefined
    }
  }, [session])
  const [recordId, setRecordId] = useState('')
  const [fact, setFact] = useState<RdfRow>({ subject: '', predicate: '', object: '' })
  const [draftBase, setDraftBase] = useState('')
  const [formError, setFormError] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const source = state.source
  const projection = useMemo(() => {
    if (!source) return undefined
    try {
      return projectOntology(source)
    } catch {
      return undefined
    }
  }, [source])
  const identity = source ? sourceIdentity(source) : ''
  const staleDraft = !!draftBase && identity !== draftBase
  const busy = ['reading', 'preparing', 'submitting'].includes(state.phase)
  const blocked = !source || state.stale || busy || !!state.pending || staleDraft
  const facts =
    source?.domain.state.facts.filter(
      (row) =>
        row.object !== null &&
        [row.id, row.subject, row.predicate, row.object].some((cell) => cell?.includes(search)),
    ) ?? []
  const currentPage = Math.min(page, Math.max(0, Math.ceil(facts.length / 20) - 1))
  function invalidateFactPreview() {
    const lifetime = factLifetime.current
    const sequence = lifetime ? ++lifetime.sequence : undefined
    session.discardPreview()
    return sequence
  }
  function reset() {
    invalidateFactPreview()
    setRecordId('')
    setFact({ subject: '', predicate: '', object: '' })
    setDraftBase(identity)
    setFormError('')
  }
  async function preview(action: 'edit' | 'remove' | 'add') {
    if (!source || blocked) return
    const lifetime = factLifetime.current
    if (!lifetime?.active || lifetime.session !== session) return
    const sequence = invalidateFactPreview()
    // Capture after discardPreview's synchronous subscribers have settled.
    const snapshot = session.getSnapshot()
    const boundSource = snapshot.source
    if (!boundSource || boundSource !== source) return
    const boundIdentity = sourceIdentity(boundSource)
    if (boundIdentity !== identity) return
    const current = () => {
      const live = session.getSnapshot()
      return (
        lifetime.active &&
        factLifetime.current === lifetime &&
        lifetime.sequence === sequence &&
        lifetime.session === session &&
        live === snapshot &&
        live.source === boundSource &&
        sourceIdentity(boundSource) === boundIdentity &&
        !live.stale &&
        !live.pending &&
        !['reading', 'preparing', 'submitting'].includes(live.phase)
      )
    }
    if (!current()) return
    const tuple = { subject: fact.subject, predicate: fact.predicate, object: fact.object }
    setFormError('')
    try {
      const plan =
        action === 'add'
          ? await newManualFactPlan(boundSource, tuple)
          : manualFactPlan(boundSource, action, recordId, tuple.object)
      if (!current()) return
      // No await/publication between this fence and Session's existing dispatch guard.
      await session.prepare(plan)
    } catch (cause) {
      if (!current()) return
      const errors: Record<string, string> = {
        FACT_NOT_FOUND: '原事实已不存在，请读取当前项目后重新选择。',
        MANAGED_FACT_REQUIRES_OWNER: '此事实由映射管理，须在对应管理流程处理冲突。',
        AMBIGUOUS_FACT_SUPPORT: '存在多个事实或定义支持，不能按单条人工事实修改。',
        NO_FACT_CHANGE: '请填写与原值不同的 RDF 对象。',
        INVALID_FACT: '请完整填写主体、属性和 RDF 对象。',
        FACT_ALREADY_EXISTS: '此三元组已有事实或定义支持，请核对原记录。',
      }
      setFormError(
        cause instanceof Error
          ? (errors[cause.message] ?? '无法预览，请核对当前源记录。')
          : '无法预览。',
      )
    }
  }
  return (
    <section className="ontology-page" aria-label="本体项目编辑">
      <header className="ontology-heading">
        <div>
          <h1>本体构建</h1>
          <p>{source ? `项目版本 ${source.domain.projectRevision}` : '尚未读取当前项目'}</p>
        </div>
        <button
          disabled={busy}
          onClick={() => {
            invalidateFactPreview()
            void session.read()
          }}
        >
          读取当前项目
        </button>
      </header>
      <p className="ontology-note">
        结构定义描述类和属性的适用范围；实例事实记录具体个体的关系或值。定义域和值域不表示必填校验。
      </p>
      {state.stale && (
        <p role="alert">当前上下文尚未确认。请重新读取项目；旧草稿仍保留，旧预览不能确认。</p>
      )}
      {source && (
        <>
          <section aria-label="结构定义">
            <h2>结构定义与元数据</h2>
            {projection && (projection.readOnly.size > 0 || projection.readOnlyHomes.size > 0) && (
              <p role="alert">
                部分历史定义无法无损编辑，已保留为只读。其他定义仍可编辑；原始内容见下方。
              </p>
            )}
            {projection ? (
              <OntologyPage
                view={projection.view}
                transactionBusy={busy || !!state.pending || state.stale}
                factsManagedExternally
                onDraftChange={invalidateFactPreview}
                previewManagedEdit={async (intent, base) => {
                  if (
                    base.project !== source.projectId ||
                    base.revision !== source.domain.projectRevision
                  )
                    throw new Error('STALE_CONTEXT')
                  if ('fact' in intent) throw new Error('INVALID_STATE')
                  await session.prepare(entityEditPlan(projection, intent))
                  if (!session.getSnapshot().prepared) throw new Error('INVALID_STATE')
                }}
                requestDeleteImpact={async (iri, base) => {
                  if (
                    base.project !== source.projectId ||
                    base.revision !== source.domain.projectRevision
                  )
                    throw new Error('STALE_CONTEXT')
                  return entityDeletionImpact(projection, iri)
                }}
              />
            ) : (
              <p role="alert">当前定义无法无损映射到表单。原始内容保留，请核对来源或刷新项目。</p>
            )}
            {source.domain.state.definitions.map((definition) => (
              <details key={`${definition.layer}:${definition.id}`}>
                <summary>
                  {definition.layer} · {definition.id}
                </summary>
                <pre>{definition.payload}</pre>
              </details>
            ))}
            {source.domain.state.definitions.length === 0 && <p>当前项目尚无结构定义。</p>}
          </section>
          <section aria-label="实例事实">
            <h2>实例事实</h2>
            <label>
              查找事实
              <input
                value={search}
                onChange={(event) => {
                  setSearch(event.target.value)
                  setPage(0)
                }}
              />
            </label>
            <table>
              <caption>当前断言 · 共 {facts.length} 条 · 每页 20 条</caption>
              <thead>
                <tr>
                  <th>主体</th>
                  <th>属性</th>
                  <th>RDF 对象</th>
                  <th>来源</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {facts.slice(currentPage * 20, currentPage * 20 + 20).map((row) => (
                  <tr key={row.id}>
                    <td>{row.subject}</td>
                    <td>{row.predicate}</td>
                    <td>
                      <code>{row.object}</code>
                    </td>
                    <td>{row.owner === null ? '人工' : `映射 ${row.owner}`}</td>
                    <td>
                      <button
                        disabled={busy || !!state.pending}
                        onClick={() => {
                          invalidateFactPreview()
                          setRecordId(row.id)
                          setFact({
                            subject: row.subject,
                            predicate: row.predicate,
                            object: row.object!,
                          })
                          setDraftBase(identity)
                          setFormError('')
                        }}
                      >
                        载入事实
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {facts.length === 0 && <p>尚无匹配的当前事实。</p>}
            <button disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>
              上一页
            </button>
            <span> 第 {currentPage + 1} 页 </span>
            <button
              disabled={(currentPage + 1) * 20 >= facts.length}
              onClick={() => setPage(currentPage + 1)}
            >
              下一页
            </button>
            <h3>{recordId ? '修改已选事实' : '新增实例事实'}</h3>
            <button disabled={busy || !!state.pending} onClick={reset}>
              新建事实并读取当前基准
            </button>
            {staleDraft && (
              <p role="alert">事实草稿来自旧快照，内容已保留。请重新载入原事实或新建表单。</p>
            )}
            {recordId && (
              <p>
                原记录 ID：<code>{recordId}</code>
              </p>
            )}
            <form
              onSubmit={(event) => {
                event.preventDefault()
                void preview(recordId ? 'edit' : 'add')
              }}
            >
              {(['subject', 'predicate', 'object'] as const).map((field) => (
                <label key={field}>
                  {
                    { subject: '主体个体 IRI', predicate: '属性 IRI', object: '规范 RDF 对象' }[
                      field
                    ]
                  }
                  <input
                    required
                    value={fact[field]}
                    disabled={busy || !!state.pending || (!!recordId && field !== 'object')}
                    onChange={(event) => {
                      invalidateFactPreview()
                      if (!draftBase) setDraftBase(identity)
                      setFact((old) => ({ ...old, [field]: event.target.value }))
                    }}
                  />
                </label>
              ))}
              <p>
                对象示例：<code>&lt;urn:example:A01&gt;</code> 或 <code>&quot;泵站A&quot;@zh</code>
                。事务服务校验规范 RDF 后生成实际差异。
              </p>
              <button disabled={blocked}>{recordId ? '预览事实修改' : '预览新增事实'}</button>
              {recordId && (
                <button type="button" disabled={blocked} onClick={() => void preview('remove')}>
                  预览移除原事实
                </button>
              )}
            </form>
          </section>
        </>
      )}
      {formError && <p role="alert">{formError}</p>}
      {state.error && (
        <p role="alert">
          操作未能完成：{state.error}。
          {state.error === 'OWNERSHIP_CONFLICT'
            ? '事实来源、保留身份或属性约束存在冲突。请核对原记录，修改输入后重新预览；已输入内容保留。'
            : '请核对当前项目或查询原操作；已输入内容保留。'}
        </p>
      )}
      {state.error === 'OWNERSHIP_CONFLICT' && !state.stale && state.ownershipDetail && (
        <>
          {state.ownershipDetail.status === 'reading' && <p role="status">正在读取冲突定位…</p>}
          {state.ownershipDetail.status === 'unavailable' && (
            <p role="status">冲突详情暂不可用。请重新读取项目，核对原记录后再预览。</p>
          )}
          {state.ownershipDetail.status === 'ready' && (
            <OwnershipConflictDetailView viewModel={state.ownershipDetail.viewModel} />
          )}
        </>
      )}
      {state.prepared && (
        <section className="ontology-diff" aria-label="完整事务差异">
          <h2>
            {state.prepared.preview.status === 'conflict'
              ? '撤销冲突影响'
              : '完整事务差异 · 尚未提交'}
          </h2>
          <p>{state.prepared.preview.summary}</p>
          <p>全部 {state.prepared.rows.length} 项；分段顺序、长度、SHA 与完整文档已核对。</p>
          <pre>{JSON.stringify(state.prepared.rows, null, 2)}</pre>
          <button
            disabled={
              state.prepared.preview.status !== 'ready' || state.stale || busy || !!state.pending
            }
            onClick={() => void session.confirm()}
          >
            我已核对完整差异，确认提交
          </button>
          <button disabled={busy || !!state.pending} onClick={() => session.discardPreview()}>
            放弃此预览
          </button>
        </section>
      )}
      {state.pending && (
        <section aria-label="原操作状态">
          <h2>
            {state.pending.unsubmitted
              ? '正式提交尚未发起'
              : state.phase === 'unknown'
                ? '原提交意图与结果待核对'
                : '原操作正在处理'}
          </h2>
          <p>
            操作 ID：<code>{state.pending.operationId}</code>；状态：
            {state.pending.job?.state ?? '未知'}。受理不等于保存完成。
          </p>
          <button disabled={busy} onClick={() => void session.reconcile()}>
            {state.pending.unsubmitted ? '清理未提交意图并重新读取' : '核对原操作与提交回执'}
          </button>
          {state.pending.job && (
            <button disabled={busy} onClick={() => void session.cancel()}>
              请求取消原任务
            </button>
          )}
        </section>
      )}
      {state.receipt && (
        <section aria-label="已提交回执">
          <h2>已提交</h2>
          <p>
            操作 {state.receipt.operationId}，提交版本 {state.receipt.projectRevision}。
          </p>
          <p>
            {state.stale
              ? '提交回执已保留，当前投影仍需重新读取。'
              : `当前已读版本 ${source?.domain.projectRevision}。`}
          </p>
          <button disabled={busy || !!state.pending} onClick={() => void session.prepareUndo()}>
            预览撤销本次修改
          </button>
          <p>撤销将读取新基准、展示完整影响，并要求再次确认。</p>
        </section>
      )}
    </section>
  )
}
