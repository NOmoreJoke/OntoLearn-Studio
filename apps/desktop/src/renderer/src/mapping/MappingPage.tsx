import { useState } from 'react'
import type { MappingSuggestionDTO } from '@ontolearn/contracts'
import { canConfirm, currentPreview, mappingDraftValid } from './model'
import type { FieldDraft, MappingDraft, ValueKind, Wizard } from './model'
import './mapping.css'

type Props = {
  state: Wizard
  busy: boolean
  error?: { summary: string; remedy: string }
  chooser?: {
    format: 'csv' | 'xlsx'
    sheets: string[]
    onReparse: (sheet?: string, encoding?: string) => void
    suggestions?: MappingSuggestionDTO[]
  }
  samplePage?: { offset: number; total: number; limit: number; onPage: (offset: number) => void }
  onPrepareCommit?: (resultId: string) => void
  onDraft: (draft: MappingDraft) => void
  onChooseSource?: (encoding: string) => void
  onPreview?: () => void
  onConfirm?: (resultId: string) => void
  onConfirmation: (confirmed: boolean) => void
  onCancel: () => void
}
const kinds: ValueKind[] = ['string', 'integer', 'decimal', 'boolean', 'date', 'datetime']
const emptyField = (column: string): FieldDraft => ({
  column,
  predicate: '',
  kind: 'string',
  trim: false,
  empty: 'omit',
  referenceNamespace: '',
  referenceColumns: [],
})

/** Controlled local page; mounting does not register or enable a product capability. */
export function MappingPage(props: Props) {
  const { state, busy } = props
  const [encoding, setEncoding] = useState('utf-8-sig')
  const [page, setPage] = useState(0)
  const source = state.source
  const draft = state.draft
  const preview = state.preview
  const ready = currentPreview(state)
  const pages = Math.max(1, Math.ceil((preview?.rows.length ?? 0) / 50))
  const shownPage = Math.min(page, pages - 1)
  const set = (change: Partial<MappingDraft>) => props.onDraft({ ...draft, ...change })
  const setField = (column: string, change: Partial<FieldDraft>) => {
    const field = draft.fields.find((item) => item.column === column) ?? emptyField(column)
    set({
      fields: [...draft.fields.filter((item) => item.column !== column), { ...field, ...change }],
    })
  }
  return (
    <section className="mapping-page" aria-label="数据映射">
      <header>
        <p>数据映射</p>
        <h1>把源数据变成可追溯的事实</h1>
        <p>
          项目 {state.projectId} · 版本 {state.revision} · 固定替换本映射受管数据
        </p>
      </header>
      {props.error && (
        <aside role="alert">
          <strong>{props.error.summary}</strong>
          <p>{props.error.remedy}</p>
        </aside>
      )}
      <fieldset disabled={busy}>
        <legend>1 选择数据</legend>
        {(!props.chooser || props.chooser.format === 'csv') && (
          <label>
            CSV 编码
            <select
              value={props.chooser ? (source?.encoding ?? encoding) : encoding}
              onChange={(e) => {
                setEncoding(e.target.value)
                props.chooser?.onReparse(undefined, e.target.value)
              }}
            >
              {['utf-8-sig', 'utf-8', 'gb18030', 'big5', 'utf-16'].map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </label>
        )}
        {props.chooser?.format === 'xlsx' && (
          <label>
            工作表{' '}
            <select
              value={source?.sheet}
              onChange={(e) => props.chooser?.onReparse(e.target.value)}
            >
              {props.chooser.sheets.map((sheet) => (
                <option key={sheet}>{sheet}</option>
              ))}
            </select>
          </label>
        )}
        <button disabled={!props.onChooseSource} onClick={() => props.onChooseSource?.(encoding)}>
          选择 CSV / XLSX 与工作表
        </button>
        {!props.onChooseSource && (
          <p role="status">受信文件选择尚未接入。文件和工作表必须由正式入口选择。</p>
        )}
        <p>XLSX 每次选择一个工作表；只读已保存的公式值。不会执行公式或宏。</p>
        {source && (
          <>
            <p>
              工作表 {source.sheet} · {source.totalRows} 行
            </p>
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>观察类型</th>
                  <th>真实样本</th>
                </tr>
              </thead>
              <tbody>
                {source.fields.map((field) => (
                  <tr key={field.name}>
                    <th>{field.name}</th>
                    <td>{field.observedTypes.join(' / ')}</td>
                    <td>{field.samples.join('；')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
        {!!props.chooser?.suggestions?.length && (
          <details>
            <summary>离线映射建议</summary>
            <ul>
              {props.chooser.suggestions.map((item) => (
                <li key={JSON.stringify([item.column, item.predicate])}>
                  {item.column} → {item.predicate} · 精确字段名匹配 · 样本 {item.samples.join('；')}
                </li>
              ))}
            </ul>
          </details>
        )}
      </fieldset>
      <fieldset disabled={busy || !source}>
        <legend>2 配置概念、字段、关系和身份</legend>
        <div className="mapping-config">
          <label>
            映射标识
            <input value={draft.identity} onChange={(e) => set({ identity: e.target.value })} />
          </label>
          <label>
            映射版本
            <input
              type="number"
              min="1"
              value={draft.version}
              onChange={(e) => set({ version: Number(e.target.value) })}
            />
          </label>
          <label>
            实体命名空间（以 / 结尾）
            <input value={draft.namespace} onChange={(e) => set({ namespace: e.target.value })} />
          </label>
          <label>
            概念 IRI
            <input value={draft.classIri} onChange={(e) => set({ classIri: e.target.value })} />
          </label>
        </div>
        <p>
          主键始终按字符串处理；001 与 1
          身份不同。复合主键顺序参与身份计算，改变规则会生成新身份并撤回旧受管数据。
        </p>
        <p>复合主键顺序：{draft.keys.join(' → ') || '尚未选择'}</p>
        {source?.fields.map((field) => (
          <div className="mapping-field" key={field.name}>
            <label>
              <input
                type="checkbox"
                checked={draft.keys.includes(field.name)}
                onChange={(e) =>
                  set({
                    keys: e.target.checked
                      ? [...draft.keys, field.name]
                      : draft.keys.filter((key) => key !== field.name),
                  })
                }
              />
              {field.name} 参与主键
            </label>
            <label>
              <input
                type="checkbox"
                checked={draft.fields.some((item) => item.column === field.name)}
                onChange={(e) =>
                  e.target.checked
                    ? setField(field.name, {})
                    : set({ fields: draft.fields.filter((item) => item.column !== field.name) })
                }
              />
              映射此字段
            </label>
            {draft.fields
              .filter((item) => item.column === field.name)
              .map((item) => (
                <div className="mapping-config" key={item.column}>
                  <label>
                    属性 / 关系 IRI
                    <input
                      value={item.predicate}
                      onChange={(e) => setField(field.name, { predicate: e.target.value })}
                    />
                  </label>
                  <label>
                    值转换
                    <select
                      value={item.kind}
                      onChange={(e) =>
                        setField(field.name, { kind: e.target.value as ValueKind, empty: 'omit' })
                      }
                    >
                      {kinds.map((kind) => (
                        <option key={kind}>{kind}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    空值
                    <select
                      value={item.empty}
                      onChange={(e) =>
                        setField(field.name, { empty: e.target.value as FieldDraft['empty'] })
                      }
                    >
                      <option value="omit">不生成事实</option>
                      <option value="error">阻止提交</option>
                      {item.kind === 'string' && <option value="literal">保存空字符串</option>}
                    </select>
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={item.trim}
                      onChange={(e) => setField(field.name, { trim: e.target.checked })}
                    />
                    去除值首尾空格（不改变主键）
                  </label>
                  <label>
                    引用目标命名空间（留空为字面量）
                    <input
                      value={item.referenceNamespace}
                      onChange={(e) => setField(field.name, { referenceNamespace: e.target.value })}
                    />
                  </label>
                  {item.referenceNamespace && (
                    <div>
                      <p>
                        引用主键：按目标身份规则的顺序选择（{item.referenceColumns.join(' → ')}）
                      </p>
                      {source.fields.map((ref) => (
                        <label key={ref.name}>
                          <input
                            type="checkbox"
                            checked={item.referenceColumns.includes(ref.name)}
                            onChange={(e) =>
                              setField(field.name, {
                                referenceColumns: e.target.checked
                                  ? [...item.referenceColumns, ref.name]
                                  : item.referenceColumns.filter((key) => key !== ref.name),
                              })
                            }
                          />
                          {ref.name}
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              ))}
          </div>
        ))}
        <p>
          布尔值默认 true/1 与 false/0；日期使用 YYYY-MM-DD，日期时间使用 ISO 的 T
          分隔。转换错误会阻止整批提交。
        </p>
        <button disabled={!props.onPreview || !mappingDraftValid(state)} onClick={props.onPreview}>
          生成完整预览
        </button>
      </fieldset>
      <fieldset disabled={busy}>
        <legend>3 预览并执行</legend>
        {preview ? (
          <>
            <p role="status">{ready ? '预览对应当前输入' : '预览已失效，请重新检查版本和冲突'}</p>
            <p>
              新增 {preview.added.length} · 删除 {preview.removed.length} · 修改{' '}
              {preview.modified.length} · 冲突 {preview.conflicts.length}
            </p>
            <details>
              <summary>身份变化</summary>
              <p>新增：{preview.identitiesAdded.join('；') || '无'}</p>
              <p>撤回：{preview.identitiesRemoved.join('；') || '无'}</p>
            </details>
            <details>
              <summary>全部事实变化</summary>
              <pre>
                {JSON.stringify(
                  { added: preview.added, removed: preview.removed, modified: preview.modified },
                  null,
                  2,
                )}
              </pre>
            </details>
            {preview.issues.map((issue, i) => (
              <p role="alert" key={i}>
                {issue.code} · {issue.sheet} 第 {issue.row} 行、第 {issue.column} 列（{issue.field}
                ）
              </p>
            ))}
            {preview.conflicts.length > 0 && (
              <aside role="alert">
                <h2>人工值或所有权冲突，整批暂停提交</h2>
                <table>
                  <thead>
                    <tr>
                      <th>冲突类型</th>
                      <th>对象 / 属性</th>
                      <th>当前值</th>
                      <th>源值</th>
                      <th>上次受管值</th>
                      <th>来源映射 / 源行</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.conflicts.map((c, i) => (
                      <tr key={i}>
                        <td>
                          {c.code === 'MANUAL_DRIFT' ? '人工值变化' : '所有权冲突'} ({c.code})
                        </td>
                        <td>
                          {c.subject}
                          <br />
                          {c.predicate}
                        </td>
                        <td>{c.current ?? '已删除'}</td>
                        <td>{c.source ?? '不再生成'}</td>
                        <td>{c.managed ?? '手工事实'}</td>
                        <td>
                          {c.owner ?? '手工'}
                          <br />
                          {c.sourceRow}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p>冲突处理留待后续版本。请取消本次重跑，或修正源数据或人工值后重新预览。</p>
              </aside>
            )}
            <table>
              <thead>
                <tr>
                  <th>来源行</th>
                  <th>样本输入</th>
                  <th>生成 RDF</th>
                </tr>
              </thead>
              <tbody>
                {preview.rows.slice(shownPage * 50, (shownPage + 1) * 50).map((row) => (
                  <tr key={row.sourceRow}>
                    <td>{row.sourceRow}</td>
                    <td>
                      <pre>{row.input.join('\n')}</pre>
                    </td>
                    <td>
                      <pre>{row.rdf.join('\n')}</pre>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {props.samplePage ? (
              <nav aria-label="预览分页">
                <button
                  disabled={props.samplePage.offset === 0}
                  onClick={() =>
                    props.samplePage?.onPage(
                      Math.max(0, props.samplePage.offset - props.samplePage.limit),
                    )
                  }
                >
                  上一页
                </button>
                <span>
                  样本偏移 {props.samplePage.offset} · 共 {props.samplePage.total} 行
                </span>
                <button
                  disabled={
                    props.samplePage.offset + props.samplePage.limit >= props.samplePage.total
                  }
                  onClick={() =>
                    props.samplePage?.onPage(props.samplePage.offset + props.samplePage.limit)
                  }
                >
                  下一页
                </button>
              </nav>
            ) : (
              <nav aria-label="预览分页">
                <button disabled={shownPage === 0} onClick={() => setPage(shownPage - 1)}>
                  上一页
                </button>
                <span>
                  {shownPage + 1} / {pages}
                </span>
                <button disabled={shownPage + 1 >= pages} onClick={() => setPage(shownPage + 1)}>
                  下一页
                </button>
              </nav>
            )}
            {props.onPrepareCommit ? (
              <button
                disabled={!ready || !!preview.issues.length || !!preview.conflicts.length}
                onClick={() => props.onPrepareCommit?.(preview.resultId)}
              >
                检查正式变更
              </button>
            ) : (
              <>
                <label>
                  <input
                    type="checkbox"
                    checked={state.confirmed}
                    disabled={!ready || preview.issues.length > 0 || preview.conflicts.length > 0}
                    onChange={(e) => props.onConfirmation(e.target.checked)}
                  />
                  我已检查整批新增、修改、删除和身份变化
                </label>
                <button
                  disabled={!props.onConfirm || !canConfirm(state)}
                  onClick={() => props.onConfirm?.(preview.resultId)}
                >
                  确认原子提交
                </button>
              </>
            )}
          </>
        ) : (
          <p>执行前必须生成完整预览。任何阻断错误都会停止整批提交。</p>
        )}
        {!props.onConfirm && !props.onPrepareCommit && <p>正式项目事务尚未接入，不能执行提交。</p>}
      </fieldset>
      <button disabled={Boolean(props.onPrepareCommit) && busy} onClick={props.onCancel}>
        {busy ? '请求取消本次重跑' : '取消本次重跑'}
      </button>
    </section>
  )
}
