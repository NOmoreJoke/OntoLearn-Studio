import { summarizePreparedDiffRows } from './rdf-display-adapter'
import type { OntologyView } from './view-model'

export type ReadableBusinessDiffProps = {
  rows: readonly unknown[]
  rawJson: string
  ontologyView?: OntologyView
}

export function ReadableBusinessDiff({ rows, rawJson, ontologyView }: ReadableBusinessDiffProps) {
  const summaries = summarizePreparedDiffRows(rows, ontologyView)

  return (
    <div className="readable-diff-wrap" data-testid="readable-business-diff">
      <table className="readable-diff-table">
        <caption>业务可读变更预览（共 {summaries.length} 项）</caption>
        <thead>
          <tr>
            <th>变更动作</th>
            <th>业务可读事实</th>
            <th>影响说明</th>
          </tr>
        </thead>
        <tbody>
          {summaries.map((row, index) => (
            <tr key={`${row.resourceLabel}:${index}`}>
              <td>
                <span className={`diff-action-badge is-${row.action}`}>{row.action}</span>
              </td>
              <td>{row.businessFactSummary}</td>
              <td>{row.impactNote}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <details className="raw-diff-drawer" data-testid="raw-diff-drawer">
        <summary>展开底层 RDF 三元组 / JSON 原文</summary>
        <pre>{rawJson}</pre>
      </details>
    </div>
  )
}
