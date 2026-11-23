import { useId, useState } from 'react'
import {
  cellText,
  currentPageCsv,
  displayDescriptor,
  displayRows,
  displayReadFailure,
  displayText,
  iriConnections,
  type DisplayDescriptor,
  type DisplayRowsPage,
} from './typed-results'
import type { QueryResultPanelProps } from './typed-result-panel-props'
import { emptyDirections } from './draft'
import { buildResultGraph, graphLimits } from './result-graph'
import './typed-results.css'

function downloadCsv(csv: string, filename: string) {
  const url = URL.createObjectURL(new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const sourceTextLimit = 256

export function sourceText(value: string): string {
  const points = Array.from(value)
  return points.length <= sourceTextLimit ? value : points.slice(0, sourceTextLimit).join('') + '…'
}

export function TruncatedSourceText({ value }: { value: string }) {
  return <SourceText key={value} value={value} />
}

function SourceText({ value }: { value: string }) {
  const [expanded, setExpanded] = useState(false)
  const id = useId()
  const excerpt = sourceText(value)
  return (
    <>
      <code id={id}>{expanded ? value : excerpt}</code>
      {excerpt !== value && (
        <button
          type="button"
          className="query-source-toggle"
          aria-controls={id}
          aria-expanded={expanded}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '收起全文' : '展开全文'}
        </button>
      )}
    </>
  )
}

function ActualRelations({
  page,
  descriptor,
  requested,
  source,
  rowKey,
  blocked,
}: {
  page: DisplayRowsPage
  descriptor: DisplayDescriptor
  requested: NonNullable<QueryResultPanelProps['rows']>['requested']
  source: unknown
  rowKey: string
  blocked: boolean
}) {
  const arrow = useId()
  const graph = blocked
    ? { state: 'unavailable' as const, reason: '正在读取或核对结果，暂不绘制关系。' }
    : buildResultGraph(source, descriptor, page, requested, rowKey)
  return (
    <section className="typed-query-actual-graph" aria-label="结果输入的局部关系图">
      <h3>结果输入的局部关系图</h3>
      {graph.state === 'unavailable' ? (
        <p role="status">{graph.reason}</p>
      ) : (
        <>
          <p>
            来源：此结果同一输入快照 <code>{graph.snapshotId}</code>，项目版本 {graph.revision}
            ，断言事实。
          </p>
          <p>
            以当前页第 {graph.rowIndex + 1} 行的 IRI 为起点，只展示一跳实例断言；箭头严格按原主体 →
            对象，标注原谓词。结构定义中的三元组未纳入本图。
          </p>
          <p>
            最多 {graphLimits.anchors} 个起点、{graphLimits.edges} 条关系；当前显示{' '}
            {graph.edges.length} / {graph.totalEdges} 条。
            {graph.omittedAnchors > 0 && `另有 ${graph.omittedAnchors} 个行内起点未显示。`}
          </p>
          {graph.edges.length === 0 ? (
            <p>此局部范围未显示可呈现的关系，不表示该快照不存在关系。</p>
          ) : (
            <>
              <div className="typed-query-relation-canvas">
                <svg
                  viewBox={`0 0 960 ${graph.edges.length * 100 + 20}`}
                  role="img"
                  aria-label="来自同快照事实记录的有向关系"
                >
                  <defs>
                    <marker
                      id={arrow}
                      viewBox="0 0 10 10"
                      refX="9"
                      refY="5"
                      markerWidth="8"
                      markerHeight="8"
                      orient="auto"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" />
                    </marker>
                  </defs>
                  {graph.edges.map((edge, index) => (
                    <g
                      key={JSON.stringify([edge.subject, edge.predicate, edge.object])}
                      data-subject={edge.subject}
                      data-predicate={edge.predicate}
                      data-object={edge.object}
                    >
                      <title>{`${edge.subject} → ${edge.predicate} → ${edge.object}`}</title>
                      <circle cx="56" cy={index * 100 + 55} r="12" />
                      <line
                        x1="68"
                        y1={index * 100 + 55}
                        x2="892"
                        y2={index * 100 + 55}
                        markerEnd={`url(#${arrow})`}
                      />
                      <circle cx="908" cy={index * 100 + 55} r="12" />
                      <text x="24" y={index * 100 + 24}>
                        主体 {index + 1}
                      </text>
                      <text x="860" y={index * 100 + 24}>
                        对象 {index + 1}
                      </text>
                      <text x="200" y={index * 100 + 42}>
                        {Array.from(edge.predicate).slice(0, 64).join('')}
                        {Array.from(edge.predicate).length > 64 ? '…' : ''}
                      </text>
                    </g>
                  ))}
                </svg>
              </div>
              <ol className="typed-query-relation-evidence">
                {graph.edges.map((edge) => (
                  <li
                    key={JSON.stringify([edge.subject, edge.predicate, edge.object])}
                    data-subject={edge.subject}
                    data-predicate={edge.predicate}
                    data-object={edge.object}
                  >
                    <p>
                      主体 <code>{edge.subject}</code> → 谓词 <code>{edge.predicate}</code> → 对象{' '}
                      <code>{edge.object}</code>
                    </p>
                    <ul>
                      {edge.supports.slice(0, graphLimits.visibleSupports).map((support) => (
                        <li key={support.id} data-fact-id={support.id}>
                          事实记录 <code>{support.id}</code>；
                          {support.owner === null ? (
                            '人工来源'
                          ) : (
                            <>
                              映射 <TruncatedSourceText value={support.owner} />
                              ，源行 <TruncatedSourceText value={support.source_row!} />。
                              {support.object !== support.managed_value && (
                                <p>
                                  当前值与映射生成值不同；边使用当前实际对象，生成值仅供溯源：
                                  <TruncatedSourceText value={support.managed_value!} />。
                                </p>
                              )}
                              {support.mappingState === null ? (
                                <p>映射来源状态未提供。</p>
                              ) : (
                                <>
                                  <p>
                                    映射生成版本 {support.mappingState.generatedVersion}；来源状态
                                    {support.mappingState.stale.length
                                      ? '有过期记录'
                                      : '未标记过期'}
                                    ，不据此删除实际断言。
                                  </p>
                                  {support.mappingState.stale.slice(0, 8).map((reason, index) => (
                                    <p key={index}>
                                      {reason.code} ·{' '}
                                      <TruncatedSourceText value={reason.dependency} /> ·{' '}
                                      {reason.before} → {reason.after}
                                    </p>
                                  ))}
                                  {support.mappingState.stale.length > 8 && (
                                    <p>其余来源状态未展开。</p>
                                  )}
                                </>
                              )}
                            </>
                          )}
                        </li>
                      ))}
                    </ul>
                    {edge.supports.length > graphLimits.visibleSupports && (
                      <p>
                        另有 {edge.supports.length - graphLimits.visibleSupports} 个来源记录未展开。
                      </p>
                    )}
                  </li>
                ))}
              </ol>
            </>
          )}
          <p>
            同一 SPO 的多个来源合为一条边，原记录 ID 保留；墓碑不成边。输入中 {graph.omittedRecords}{' '}
            条字面量、超出本图 IRI 支持范围或来源字段不完整的记录未作为对象关系显示。
          </p>
        </>
      )}
    </section>
  )
}

function RowConnections({
  page,
  descriptor,
  requested,
  source,
  blocked,
}: {
  page: DisplayRowsPage
  descriptor: DisplayDescriptor
  requested: NonNullable<QueryResultPanelProps['rows']>['requested']
  source: unknown
  blocked: boolean
}) {
  const [selectedKey, setSelectedKey] = useState('')
  const [windowIndex, setWindowIndex] = useState(0)
  const row = page.rows.find((value) => value.rowKey === selectedKey) ?? page.rows[0]
  if (!row) return null
  const connections = iriConnections(row, descriptor)
  const currentWindow = Math.min(windowIndex, Math.max(0, Math.ceil(connections.length / 16) - 1))
  const visible = connections.slice(currentWindow * 16, (currentWindow + 1) * 16)
  return (
    <>
      <section className="typed-query-graph" aria-label="当前页 IRI 关联">
        <h3>当前页 IRI 关联</h3>
        <label>
          查看结果行
          <select
            value={row.rowKey}
            onChange={(event) => {
              setSelectedKey(event.target.value)
              setWindowIndex(0)
            }}
          >
            {page.rows.map((value) => (
              <option key={value.rowKey} value={value.rowKey}>
                第 {value.index + 1} 行
              </option>
            ))}
          </select>
        </label>
        <p>连线表示结果行包含该列的 IRI 单元格，不推断本体关系。字面量不作为 IRI 节点。</p>
        {visible.length === 0 ? (
          <p>此行没有 IRI 单元格。</p>
        ) : (
          <>
            <svg
              viewBox={`0 0 640 ${Math.max(100, visible.length * 60)}`}
              role="img"
              aria-label={`第 ${row.index + 1} 行的 IRI 关联示意`}
            >
              <title>结果行与实际 IRI 单元格的关联；完整 IRI 列在图后</title>
              <circle cx="72" cy="40" r="24" />
              <text x="72" y="44" textAnchor="middle">
                {row.index + 1}
              </text>
              {visible.map((connection, index) => (
                <g key={currentWindow * 16 + index}>
                  <line x1="96" y1="40" x2="400" y2={30 + index * 60} />
                  <circle cx="412" cy={30 + index * 60} r="8" />
                  <text x="180" y={22 + index * 60}>
                    {Array.from(connection.column).slice(0, 24).join('')}
                  </text>
                  <text x="432" y={34 + index * 60}>
                    IRI {currentWindow * 16 + index + 1}
                  </text>
                </g>
              ))}
            </svg>
            <p>
              图中显示第 {currentWindow * 16 + 1}–{currentWindow * 16 + visible.length} 个 IRI
              关联，共 {connections.length} 个。
            </p>
            <ul>
              {visible.map((connection, index) => (
                <li key={index}>
                  <strong>{connection.column}</strong>：<code>{connection.iri}</code>
                </li>
              ))}
            </ul>
            <button
              disabled={currentWindow === 0}
              onClick={() => setWindowIndex(currentWindow - 1)}
            >
              前一组关联
            </button>
            <button
              disabled={(currentWindow + 1) * 16 >= connections.length}
              onClick={() => setWindowIndex(currentWindow + 1)}
            >
              后一组关联
            </button>
          </>
        )}
      </section>
      <ActualRelations
        page={page}
        descriptor={descriptor}
        requested={requested}
        source={source}
        rowKey={row.rowKey}
        blocked={blocked}
      />
    </>
  )
}

export function QueryResultPanel(props: QueryResultPanelProps) {
  let descriptor: DisplayDescriptor | undefined
  try {
    descriptor = displayDescriptor(props.descriptor, props)
  } catch {
    /* No rejected payload is displayed. */
  }
  let failure: ReturnType<typeof displayReadFailure> | undefined
  let failureInvalid = false
  try {
    if (props.readFailure)
      failure = displayReadFailure(props.readFailure, {
        projectId: props.projectId,
        resultId: props.resultId,
        descriptorRef: descriptor?.descriptorRef,
      })
  } catch {
    failureInvalid = true
  }
  if (!descriptor) {
    return (
      <section aria-label="查询结果">
        {failure ? (
          <>
            <p>
              结果 <code>{props.resultId}</code>；项目 <code>{props.projectId}</code>。
            </p>
            <p role="alert">
              {failure.code === 'PAYLOAD_EVICTED'
                ? '此结果载荷已回收，请明确选择输入后重新执行。'
                : `结果读取未完成（${failure.code}），请重新读取该结果。`}
            </p>
          </>
        ) : (
          <p role="alert">结果身份或描述不匹配，未显示该载荷。请重新获取项目结果。</p>
        )}
      </section>
    )
  }
  const unavailable = failure?.code === 'PAYLOAD_EVICTED'
  let rows: ReturnType<typeof displayRows> | undefined
  let text: ReturnType<typeof displayText> | undefined
  let rowsInvalid = false
  let textInvalid = false
  try {
    if (props.rows && !unavailable && !failure)
      rows = displayRows(props.rows.value, descriptor, props.rows.requested)
  } catch {
    rowsInvalid = true
  }
  try {
    if (props.text && !unavailable && !failure)
      text = displayText(props.text.value, descriptor, props.text.requested)
  } catch {
    textInvalid = true
  }
  const metadata = descriptor.metadata
  const textEnd = text ? text.startUtf8Byte + text.utf8Length : 0
  const rowEnd = rows
    ? (rows.rows.at(-1)?.index ?? (props.rows?.requested.startIndex ?? 0) - 1) + 1
    : 0
  const stateText = {
    current: '当前结果',
    stale: '已过期，请明确选择输入后重新执行',
    historical: '历史结果',
  }[metadata.state]
  return (
    <section className="typed-query-results" aria-label="查询结果">
      <h2>查询结果</h2>
      <p>
        {stateText}；快照 <code>{descriptor.identity.inputSnapshotId}</code>；项目版本{' '}
        {descriptor.identity.inputProjectRevision}
      </p>
      <p>
        执行范围：
        {descriptor.identity.scope === 'asserted+derived' ? '断言事实＋当前推导结果' : '断言事实'}
        ；执行输入：
        {descriptor.identity.inputSelection === 'historical'
          ? '显式选择的历史快照'
          : '执行时的当前已提交输入'}
        。
      </p>
      {metadata.historicalSelectionRequired && <p>用于后续操作需显式选择历史输入。</p>}
      <ul>
        {metadata.staleReason.map((reason, index) => (
          <li key={index}>
            {reason.code} · {reason.dependency} · {reason.before} → {reason.after}
          </li>
        ))}
      </ul>
      {failureInvalid && <p role="alert">读取回执与当前结果不匹配，未应用该回执。</p>}
      {unavailable ? (
        <p role="status">此结果载荷已回收。结果和快照身份保留，请明确选择输入后重新执行。</p>
      ) : failure ? (
        <p role="alert">结果读取未完成（{failure.code}），请检查连接或重新读取该结果。</p>
      ) : (
        <>
          <details>
            <summary>本次实际执行的 SPARQL</summary>
            <p>
              文本摘要：<code>{descriptor.executedText.sha256}</code>
            </p>
            {props.textLoading && <p role="status">正在读取固定结果的文本片段…</p>}
            {textInvalid && <p role="alert">文本身份、字节范围或分页不匹配，未显示该片段。</p>}
            {!props.text && <p>尚未取得实际执行文本；编辑器内容不会代替此处原文。</p>}
            {text && (
              <>
                <p>
                  本片段 UTF-8 字节 {text.startUtf8Byte}–{textEnd}，全文{' '}
                  {descriptor.executedText.utf8Bytes} 字节。
                  {text.startUtf8Byte === 0 && textEnd === descriptor.executedText.utf8Bytes
                    ? '本片段包含全部执行原文。'
                    : '当前仅展示执行原文的一个片段。'}
                </p>
                <pre>{text.text}</pre>
                <button
                  disabled={!text.nextCursor || !props.onNextText || props.textLoading}
                  onClick={() => {
                    if (text?.nextCursor)
                      props.onNextText?.({
                        descriptorRef: descriptor.descriptorRef,
                        cursor: text.nextCursor,
                        startUtf8Byte: textEnd,
                        maxUtf8Bytes: props.text!.requested.maxUtf8Bytes,
                      })
                  }}
                >
                  下一段执行文本
                </button>
              </>
            )}
          </details>
          {descriptor.query.kind === 'ASK' ? (
            <>
              <p className="typed-query-ask">
                ASK：{descriptor.query.value ? 'true（满足查询条件）' : 'false（未满足查询条件）'}
              </p>
              <p>这是布尔结果，不是 SELECT 空表。</p>
              <button
                onClick={() =>
                  downloadCsv(
                    `"ASK"\r\n"${descriptor.query.kind === 'ASK' && descriptor.query.value}"\r\n`,
                    'query-ask.csv',
                  )
                }
              >
                导出 ASK 结果 CSV
              </button>
            </>
          ) : (
            <>
              <p>完整结果共 {descriptor.query.rowCount} 行；表格与导出仅包含当前页。</p>
              {props.rowsLoading && <p role="status">正在读取固定结果页…</p>}
              {rowsInvalid && <p role="alert">结果页身份、行次序或列宽不匹配，未显示该页。</p>}
              {!props.rows && <p>尚未取得结果页，不以缺少页面解释为空结果。</p>}
              {rows && (
                <>
                  <div className="typed-query-table">
                    <table>
                      <caption>
                        当前结果页
                        {rows.rows.length
                          ? `：第 ${rows.rows[0].index + 1}–${rowEnd} 行`
                          : '：0 行'}
                      </caption>
                      <thead>
                        <tr>
                          {descriptor.query.columns.map((column) => (
                            <th scope="col" key={column.index}>
                              {column.name}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {rows.rows.map((row) => (
                          <tr key={row.rowKey}>
                            {row.cells.map((cell, index) => (
                              <td key={index}>
                                <span>{cellText(cell)}</span>
                                {cell && (
                                  <details>
                                    <summary>RDF 原文</summary>
                                    <code>{cell.n3}</code>
                                  </details>
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {descriptor.query.rowCount === 0
                    ? !props.rowsLoading &&
                      !failureInvalid && (
                        <section aria-label="SELECT 空结果检查">
                          <p>SELECT 完整结果为空。以下是检查方向，不是对数据原因的判断。</p>
                          <p>
                            请先查看本次实际执行的
                            SPARQL，并按上方显示的数据范围、输入快照和结果状态逐项检查。
                          </p>
                          <ul>
                            {emptyDirections.map((direction) => (
                              <li key={direction}>{direction}</li>
                            ))}
                          </ul>
                        </section>
                      )
                    : rows.rows.length === 0 && <p>本页没有记录；完整结果不为空。</p>}
                  <button
                    onClick={() =>
                      downloadCsv(
                        currentPageCsv(descriptor, rows!, props.rows!.requested),
                        'query-current-page.csv',
                      )
                    }
                  >
                    导出当前页 CSV
                  </button>
                  <button
                    disabled={!rows.nextCursor || !props.onNextRows || props.rowsLoading}
                    onClick={() => {
                      if (rows?.nextCursor)
                        props.onNextRows?.({
                          descriptorRef: descriptor.descriptorRef,
                          cursor: rows.nextCursor,
                          startIndex: rowEnd,
                          pageSize: props.rows!.requested.pageSize,
                        })
                    }}
                  >
                    下一页结果
                  </button>
                  <RowConnections
                    page={rows}
                    descriptor={descriptor}
                    requested={props.rows!.requested}
                    source={props.graphSource}
                    blocked={!!props.rowsLoading || failureInvalid}
                  />
                </>
              )}
            </>
          )}
        </>
      )}
    </section>
  )
}
