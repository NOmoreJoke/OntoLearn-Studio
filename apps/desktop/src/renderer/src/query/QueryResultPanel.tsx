import { useState } from 'react'
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
import './typed-results.css'

function downloadCsv(csv: string, filename: string) {
  const url = URL.createObjectURL(new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

function RowConnections({
  page,
  descriptor,
}: {
  page: DisplayRowsPage
  descriptor: DisplayDescriptor
}) {
  const [selectedKey, setSelectedKey] = useState('')
  const [windowIndex, setWindowIndex] = useState(0)
  const row = page.rows.find((value) => value.rowKey === selectedKey) ?? page.rows[0]
  if (!row) return null
  const connections = iriConnections(row, descriptor)
  const currentWindow = Math.min(windowIndex, Math.max(0, Math.ceil(connections.length / 16) - 1))
  const visible = connections.slice(currentWindow * 16, (currentWindow + 1) * 16)
  return (
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
          <button disabled={currentWindow === 0} onClick={() => setWindowIndex(currentWindow - 1)}>
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
        执行范围：断言事实；执行输入：
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
                  <RowConnections page={rows} descriptor={descriptor} />
                </>
              )}
            </>
          )}
        </>
      )}
    </section>
  )
}
