import { useEffect, useMemo, useRef, useState } from 'react'
import {
  classTree,
  identity,
  isCurrentPreview,
  kindLabels,
  localGraph,
  labelOf,
  definitionOf,
  type LocalizedText,
  type ObjectKind,
  type ObjectRow,
  type OntologyView,
  type RdfRow,
} from './view-model'
import './ontology.css'
import type { EditIntent } from './edit-intent'
export type { EditIntent } from './edit-intent'

/** Local legacy preview presentation. Managed transactions render their actual
 * complete document in the owning consumer.
 */
export type EditPreview = Readonly<{
  project: string
  revision: number
  summary: string
  added: readonly RdfRow[]
  removed: readonly RdfRow[]
  metadataChanges: readonly string[]
  impact: readonly string[]
}>
export type OntologyPageProps = {
  view: OntologyView
  /** Owning service supplies validated views and previews; no browser storage authority. */
  previewEdit?: (intent: EditIntent, base: OntologyView) => Promise<EditPreview>
  requestDeleteImpact?: (iri: string, base: OntologyView) => Promise<readonly string[]>
  /** Actual transaction document/confirmation is rendered by the owning consumer. */
  previewManagedEdit?: (intent: EditIntent, base: OntologyView) => Promise<void>
  transactionBusy?: boolean
  factsManagedExternally?: boolean
  onDraftChange?: () => void
}
const blank = (): ObjectRow => ({
  iri: '',
  kind: 'class',
  identifier: '',
  labels: [],
  definitions: [],
  synonyms: [],
  examples: [],
  parents: [],
  domain: [],
  range: [],
  types: [],
})
// Preserve trailing empty lines while typing; normalize only when requesting a preview.
const lines = (value: string) => value.split('\n')
function normalizedDraft(draft: ObjectRow): ObjectRow {
  const normalized = (values: readonly string[]) => values.map((v) => v.trim()).filter(Boolean)
  return {
    ...draft,
    synonyms: [...draft.synonyms],
    examples: [...draft.examples],
    parents: normalized(draft.parents),
    domain: normalized(draft.domain),
    range: normalized(draft.range),
    types: normalized(draft.types),
  }
}

export function OntologyPage(props: OntologyPageProps) {
  return <Editor key={props.view.project} {...props} />
}

function Editor({
  view,
  previewEdit,
  requestDeleteImpact,
  previewManagedEdit,
  transactionBusy = false,
  factsManagedExternally = false,
  onDraftChange,
}: OntologyPageProps) {
  const canPreview = !!previewEdit || !!previewManagedEdit
  const [tab, setTab] = useState<'table' | 'tree' | 'graph'>('table')
  const [selected, setSelected] = useState<string>('')
  const [draft, setDraft] = useState<ObjectRow>(blank)
  const [draftBase, setDraftBase] = useState(() => identity(view))
  const [factBase, setFactBase] = useState(() => identity(view))
  const [editing, setEditing] = useState(false)
  const [preview, setPreview] = useState<EditPreview>()
  const [impact, setImpact] = useState<{ base: string; iri: string; items: readonly string[] }>()
  const [error, setError] = useState('')
  const [localPending, setPending] = useState(false)
  const pending = localPending || transactionBusy
  const [fact, setFact] = useState<RdfRow>({ subject: '', predicate: '', object: '' })
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const request = useRef(0)
  useEffect(
    () => () => {
      request.current++
    },
    [],
  )
  const currentIdentity = identity(view)
  const chosen = view.objects.find((row) => row.iri === selected)
  const rows = view.objects
    .filter((row) =>
      [...row.labels.map(([text]) => text), row.identifier, row.iri].some((value) =>
        value.toLowerCase().includes(search.toLowerCase()),
      ),
    )
    .sort((a, b) => (a.iri < b.iri ? -1 : a.iri > b.iri ? 1 : 0))
  const currentPage = Math.min(page, Math.max(0, Math.ceil(rows.length / 20) - 1))
  const tree = useMemo(() => (tab === 'tree' ? classTree(view.objects) : []), [tab, view.objects])
  const graph = useMemo(
    () => (tab === 'graph' ? localGraph(view, selected, 12) : undefined),
    [tab, view, selected],
  )
  const invalidateDraft = () => {
    request.current++
    onDraftChange?.()
  }
  const update = <K extends keyof ObjectRow>(key: K, value: ObjectRow[K]) => {
    invalidateDraft()
    setPending(false)
    setPreview(undefined)
    setDraft((old) => ({ ...old, [key]: value }))
  }
  function select(row: ObjectRow) {
    invalidateDraft()
    setPending(false)
    setSelected(row.iri)
    // Selection deliberately does not replace an unsaved form draft.
    setImpact(undefined)
    setPreview(undefined)
    setError('')
  }
  async function plan(intent: EditIntent) {
    if (!canPreview || pending) return
    const base = intent.action === 'assert' || intent.action === 'retract' ? factBase : draftBase
    if (intent.action !== 'delete' && base !== identity(view)) {
      setError('草稿基准已变化，请重新载入当前对象或新建表单后再预览。')
      return
    }
    const seq = ++request.current
    setPending(true)
    setPreview(undefined)
    setError('')
    try {
      if (previewManagedEdit) {
        await previewManagedEdit(intent, view)
        return
      }
      const result = await previewEdit!(intent, view)
      if (seq !== request.current) return
      if (!isCurrentPreview(view, result)) {
        setError('预览与请求的项目或版本不一致，请刷新后重试。')
        return
      }
      setPreview(result)
    } catch {
      if (seq === request.current)
        setError('未能生成预览。正式项目未获保存确认，请检查输入或重新读取项目。')
    } finally {
      if (seq === request.current) setPending(false)
    }
  }
  async function inspectDeletion() {
    if (!chosen || !requestDeleteImpact) return
    onDraftChange?.()
    const seq = ++request.current
    setPending(true)
    setError('')
    setImpact(undefined)
    setPreview(undefined)
    try {
      const items = await requestDeleteImpact(chosen.iri, view)
      if (seq === request.current) setImpact({ base: currentIdentity, iri: chosen.iri, items })
    } catch {
      if (seq === request.current) setError('无法读取完整引用影响，暂不能预览删除。')
    } finally {
      if (seq === request.current) setPending(false)
    }
  }
  const canDelete = impact?.base === currentIdentity && impact.iri === selected
  return (
    <section className="ontology-page" aria-label="本体构建">
      <header className="ontology-heading">
        <div>
          <p className="eyebrow">定义业务概念</p>
          <h1>本体构建</h1>
          <p>项目版本 {view.revision} · 当前断言与结构定义</p>
        </div>
        <button
          onClick={() => {
            invalidateDraft()
            setPending(false)
            setDraft(blank())
            setDraftBase(currentIdentity)
            setEditing(false)
            setPreview(undefined)
            setError('')
          }}
        >
          新建概念
        </button>
      </header>
      <p className="ontology-note">
        结构关系描述适用类型，不表示每个对象都存在该关系，也不等同必填校验。
      </p>
      {!canPreview && (
        <p role="status">编辑预览服务尚未接入。可浏览已提供的对象；正式提交须经项目事务确认。</p>
      )}
      <div className="ontology-workbench">
        <section aria-label="对象浏览">
          <nav aria-label="本体视图">
            {(['table', 'tree', 'graph'] as const).map((value) => (
              <button key={value} aria-pressed={tab === value} onClick={() => setTab(value)}>
                {{ table: '表格', tree: '类树', graph: '局部关系图' }[value]}
              </button>
            ))}
          </nav>
          {tab === 'table' && (
            <>
              <label>
                查找概念
                <input
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value)
                    setPage(0)
                  }}
                />
              </label>
              <table>
                <caption>对象表 · 共 {rows.length} 项 · 每页 20 项</caption>
                <thead>
                  <tr>
                    <th>名称 / 英文标识</th>
                    <th>类型</th>
                    <th>选择</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(currentPage * 20, currentPage * 20 + 20).map((row) => (
                    <tr key={row.iri}>
                      <td>
                        {labelOf(row)}
                        <small>{row.identifier}</small>
                      </td>
                      <td>{kindLabels[row.kind]}</td>
                      <td>
                        <button onClick={() => select(row)}>查看 {row.identifier}</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {rows.length === 0 && <p>尚无匹配对象。新建一个类开始建模。</p>}
              <button disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>
                上一页
              </button>
              <span> 第 {currentPage + 1} 页 </span>
              <button
                disabled={(currentPage + 1) * 20 >= rows.length}
                onClick={() => setPage(currentPage + 1)}
              >
                下一页
              </button>
            </>
          )}
          {tab === 'tree' && (
            <ul className="ontology-tree">
              {tree.map((row, index) => (
                <li key={`${row.iri}:${index}`}>
                  <span aria-hidden="true">{'· '.repeat(Math.min(row.depth, 12))}</span>
                  <button
                    onClick={() => select(view.objects.find((item) => item.iri === row.iri)!)}
                  >
                    {labelOf(view.objects.find((item) => item.iri === row.iri)!)}
                    {row.repeated ? '（已展示的类 / 循环引用）' : ''}
                  </button>
                </li>
              ))}
            </ul>
          )}
          {tab === 'graph' && graph && (
            <div className="ontology-local-graph">
              <p>
                仅展示当前对象的一跳关系。
                {graph.truncated ? `显示前 12 条，共 ${graph.total} 条。` : ''}
              </p>
              {!selected ? (
                <p>先从表格或类树选择对象。</p>
              ) : (
                <>
                  <strong>{chosen ? labelOf(chosen) : selected}</strong>
                  <NeighborhoodGraph focus={selected} edges={graph.edges} />
                  <ul aria-label="邻近关系">
                    {graph.edges.map((edge, index) => (
                      <li key={index}>
                        <span>{edge.subject}</span>
                        <span aria-label="关系"> → {edge.predicate} → </span>
                        <span>{edge.object}</span>
                      </li>
                    ))}
                  </ul>
                  {graph.edges.length === 0 && <p>未记录邻近关系。</p>}
                </>
              )}
            </div>
          )}
          {chosen && (
            <article aria-label="选中对象详情">
              <h2>{labelOf(chosen)}</h2>
              <code>{chosen.iri}</code>
              <p>{definitionOf(chosen) || '尚未填写定义'}</p>
              <p>同义词：{chosen.synonyms.join('、') || '未记录'}</p>
              <p>示例：{chosen.examples.join('；') || '未记录'}</p>
              <button
                onClick={() => {
                  invalidateDraft()
                  setPending(false)
                  setPreview(undefined)
                  setDraft(chosen)
                  setDraftBase(currentIdentity)
                  setEditing(true)
                }}
              >
                将对象载入编辑表单
              </button>
              <button
                onClick={() => {
                  invalidateDraft()
                  setPending(false)
                  setPreview(undefined)
                  setDraft({ ...chosen, iri: '', identifier: '' })
                  setDraftBase(currentIdentity)
                  setEditing(false)
                }}
              >
                复制定义到新表单
              </button>
              <button
                disabled={!requestDeleteImpact || pending}
                onClick={() => void inspectDeletion()}
              >
                查看删除影响
              </button>
              {canDelete && (
                <div>
                  <h3>删除影响</h3>
                  <p>
                    基准快照（项目版本 {view.revision}）中的引用；包括本次修改计划将解除的引用。
                  </p>
                  <ul>
                    {impact.items.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                  {impact.items.length === 0 && <p>当前未发现已登记的引用。</p>}
                  <button
                    disabled={!canPreview || pending}
                    onClick={() => void plan({ action: 'delete', iri: selected })}
                  >
                    预览删除（尚不提交）
                  </button>
                </div>
              )}
            </article>
          )}
        </section>
        <section aria-label="本体编辑表单">
          {draftBase !== currentIdentity && (
            <p role="alert">草稿保留在旧版本。请重新载入当前对象，或点击“新建概念”重新开始。</p>
          )}
          <h2>{editing ? '编辑定义' : '新建定义'}</h2>
          <form
            onSubmit={(event) => {
              event.preventDefault()
              void plan({ action: editing ? 'edit' : 'create', object: normalizedDraft(draft) })
            }}
          >
            <label>
              类型
              <select
                value={draft.kind}
                disabled={editing}
                onChange={(event) => {
                  update('kind', event.target.value as ObjectKind)
                  setDraft((old) => ({
                    ...old,
                    parents: [],
                    domain: [],
                    range: [],
                    types: [],
                    classType: undefined,
                  }))
                }}
              >
                {Object.entries(kindLabels).map(([value, label]) => (
                  <option value={value} key={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            {draft.kind === 'class' && (
              <label>
                类声明
                <select
                  value={draft.classType ?? 'rdfs'}
                  onChange={(event) => {
                    const value = event.target.value
                    if (value === 'rdfs' || value === 'owl') update('classType', value)
                  }}
                >
                  <option value="rdfs">rdfs:Class</option>
                  <option value="owl">owl:Class</option>
                </select>
              </label>
            )}
            <label>
              稳定 IRI
              <input
                required
                disabled={editing}
                value={draft.iri}
                onChange={(event) => update('iri', event.target.value)}
              />
            </label>
            <label>
              英文标识
              <input
                required
                pattern="[A-Za-z0-9_][A-Za-z0-9_-]*"
                value={draft.identifier}
                onChange={(event) => update('identifier', event.target.value)}
              />
            </label>
            <LocalizedFields
              title="名称"
              values={draft.labels}
              onChange={(values) => update('labels', values)}
            />
            <LocalizedFields
              title="定义"
              values={draft.definitions}
              onChange={(values) => update('definitions', values)}
            />
            {(['synonyms', 'examples'] as const).map((key) => (
              <TextListFields
                key={key}
                title={key === 'synonyms' ? '同义词' : '示例'}
                values={draft[key]}
                onChange={(values) => update(key, values)}
              />
            ))}
            {(draft.kind === 'class'
              ? (['parents'] as const)
              : draft.kind === 'individual'
                ? (['types'] as const)
                : (['domain', 'range'] as const)
            ).map((key) => (
              <label key={key}>
                {
                  {
                    parents: '上级类 IRI',
                    types: '所属类 IRI',
                    domain: '适用主体类 IRI（定义域）',
                    range: '客体类 / 数据类型 IRI（值域）',
                  }[key]
                }
                （每行一项）
                <textarea
                  value={draft[key].join('\n')}
                  onChange={(event) => update(key, lines(event.target.value))}
                />
              </label>
            ))}
            <button
              disabled={!canPreview || pending || draftBase !== currentIdentity}
              type="submit"
            >
              {pending ? '正在生成预览…' : '预览定义修改'}
            </button>
          </form>
          {!factsManagedExternally && (
            <>
              <h2>创建实例事实</h2>
              {factBase !== currentIdentity && (
                <p role="alert">事实草稿基准已变化，请重新填写当前版本的事实。</p>
              )}
              <button
                onClick={() => {
                  invalidateDraft()
                  setPending(false)
                  setPreview(undefined)
                  setFact({ subject: '', predicate: '', object: '' })
                  setFactBase(currentIdentity)
                }}
              >
                清空事实表单并读取当前版本
              </button>
              <p>
                选择具体个体，记录实际发生的关系或属性值。RDF 对象使用规范 n3 单术语，例如
                <code>&lt;urn:t02:A01&gt;</code>、<code>&quot;名称&quot;@zh</code> 或
                <code>&quot;3&quot;^^&lt;http://www.w3.org/2001/XMLSchema#integer&gt;</code>
                。预览服务检查格式和语义。
              </p>
              <form
                onSubmit={(event) => {
                  event.preventDefault()
                  void plan({ action: 'assert', fact })
                }}
              >
                {(['subject', 'predicate', 'object'] as const).map((key) => (
                  <label key={key}>
                    {{ subject: '主体个体 IRI', predicate: '属性 IRI', object: 'RDF 对象' }[key]}
                    <input
                      required
                      value={fact[key]}
                      onChange={(event) => {
                        invalidateDraft()
                        setPending(false)
                        setPreview(undefined)
                        setFact((old) => ({ ...old, [key]: event.target.value }))
                      }}
                    />
                  </label>
                ))}
                <button disabled={!canPreview || pending || factBase !== currentIdentity}>
                  预览新增事实
                </button>
                <button
                  type="button"
                  disabled={!canPreview || pending || factBase !== currentIdentity}
                  onClick={() => void plan({ action: 'retract', fact })}
                >
                  预览移除事实
                </button>
              </form>
            </>
          )}
        </section>
      </div>
      {error && <p role="alert">{error}</p>}
      {preview && (
        <section className="ontology-diff" aria-label="修改预览">
          <h2>修改预览 · 尚未提交</h2>
          <p>{preview.summary}</p>
          {!isCurrentPreview(view, preview) && (
            <p role="alert">基准已变化，请重新生成预览。旧预览不能确认。</p>
          )}
          <p>基准项目版本 {preview.revision}。正式确认和撤销由项目事务服务接入后提供。</p>
          <h3>元数据变化</h3>
          <ul>
            {preview.metadataChanges.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
          <h3>完整 RDF Diff</h3>
          <pre>
            {[
              ...preview.removed.map((t) => `− <${t.subject}> <${t.predicate}> ${t.object} .`),
              ...preview.added.map((t) => `+ <${t.subject}> <${t.predicate}> ${t.object} .`),
            ].join('\n') || '无 RDF 变化'}
          </pre>
          <h3>引用影响</h3>
          <p>基准快照（项目版本 {preview.revision}）中的引用；包括本次修改计划将解除的引用。</p>
          <ul>
            {preview.impact.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </section>
      )}
    </section>
  )
}

function LocalizedFields({
  title,
  values,
  onChange,
}: {
  title: string
  values: readonly LocalizedText[]
  onChange: (values: readonly LocalizedText[]) => void
}) {
  return (
    <fieldset>
      <legend>{title}（保留所有语言）</legend>
      {values.map(([text, language], index) => (
        <div key={index}>
          <label>
            {title} {index + 1}
            <textarea
              required
              rows={title === '定义' ? 3 : 1}
              value={text}
              onChange={(event) => {
                onChange(
                  values.map((value, i) => (i === index ? [event.target.value, language] : value)),
                )
              }}
            />
          </label>
          <label>
            语言标签 {index + 1}
            <input
              value={language}
              pattern="[a-z]+(-[a-z0-9]+)*|"
              placeholder="zh / en / 留空"
              onChange={(event) => {
                onChange(
                  values.map((value, i) => (i === index ? [text, event.target.value] : value)),
                )
              }}
            />
          </label>
          <button type="button" onClick={() => onChange(values.filter((_, i) => i !== index))}>
            移除此{title}
          </button>
        </div>
      ))}
      <button type="button" onClick={() => onChange([...values, ['', 'zh']])}>
        添加{title}
      </button>
    </fieldset>
  )
}

function TextListFields({
  title,
  values,
  onChange,
}: {
  title: string
  values: readonly string[]
  onChange: (values: readonly string[]) => void
}) {
  return (
    <fieldset>
      <legend>{title}（保留原文与顺序）</legend>
      {values.map((value, index) => (
        <div key={index}>
          <label>
            {title} {index + 1}
            <textarea
              required
              value={value}
              onChange={(event) =>
                onChange(values.map((item, i) => (i === index ? event.target.value : item)))
              }
            />
          </label>
          <button type="button" onClick={() => onChange(values.filter((_, i) => i !== index))}>
            移除此{title}
          </button>
        </div>
      ))}
      <button type="button" onClick={() => onChange([...values, ''])}>
        添加{title}
      </button>
    </fieldset>
  )
}

function NeighborhoodGraph({ focus, edges }: { focus: string; edges: readonly RdfRow[] }) {
  const neighbors = [
    ...new Set(edges.map((edge) => (edge.subject === focus ? edge.object : `<${edge.subject}>`))),
  ]
  const center = { x: 260, y: 260 }
  const points = neighbors.map((value, index) => {
    const angle = (2 * Math.PI * index) / Math.max(1, neighbors.length)
    return { value, x: center.x + Math.cos(angle) * 188, y: center.y + Math.sin(angle) * 188 }
  })
  return (
    <svg viewBox="0 0 520 520" role="img" aria-label="当前对象及一跳邻居关系图">
      <title>当前对象及一跳邻居。完整 IRI 和关系见下方列表。</title>
      {edges.map((edge, index) => {
        const neighbor = edge.subject === focus ? edge.object : `<${edge.subject}>`
        const point = points.find((p) => p.value === neighbor)!
        const from = edge.subject === focus ? center : point
        const to = edge.subject === focus ? point : center
        const x = from.x + (to.x - from.x) * 0.72
        const y = from.y + (to.y - from.y) * 0.72
        const angle = (Math.atan2(to.y - from.y, to.x - from.x) * 180) / Math.PI
        return (
          <g key={index}>
            <title>{`${edge.subject} → ${edge.predicate} → ${edge.object}`}</title>
            <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} />
            <path d="M -7 -4 L 0 0 L -7 4" transform={`translate(${x} ${y}) rotate(${angle})`} />
          </g>
        )
      })}
      {points.map((point) => (
        <g key={point.value}>
          <title>{point.value}</title>
          <circle cx={point.x} cy={point.y} r="28" />
          <text x={point.x} y={point.y + 4} textAnchor="middle">
            {point.value.replace(/[<>]/g, '').split(/[:/#]/).pop()?.slice(0, 12)}
          </text>
        </g>
      ))}
      <circle className="ontology-focus-node" cx={center.x} cy={center.y} r="34" />
      <text x={center.x} y={center.y + 4} textAnchor="middle">
        <title>{focus}</title>
        {focus.split(/[:/#]/).pop()?.slice(0, 12)}
      </text>
    </svg>
  )
}
