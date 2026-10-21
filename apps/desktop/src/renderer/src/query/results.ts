import { z } from 'zod'
import { validateV2 } from '../../../../../../packages/contracts/src/v2'

// Display types narrow already-approved common result/page schemas. They do not
// introduce a transport, a result store, or a second invalidation policy.
export interface QueryResultIdentity {
  projectId: string
  resultId: string
  inputSnapshotId: string
  scope: 'asserted' | 'asserted+derived'
  parametersHash: string
}
export interface QueryResultMetadata extends QueryResultIdentity {
  kind: 'query'
  state: 'current' | 'stale' | 'historical'
  payloadStatus: 'available' | 'evicted'
  historicalSelectionRequired: boolean
  inputProjectRevision: number
  staleReason: { code: string; dependency: string; before: number; after: number }[]
}
export interface QueryPageData {
  binding: QueryResultIdentity & { order: 'ordinal+rowId:asc' }
  rows: { rowId: string; ordinal: number; cells: (string | number | boolean | null)[] }[]
  nextCursor: string | null
}
const metadataSchema = z.custom<QueryResultMetadata>((v) => validateV2('result', v))
const pageSchema = z.custom<QueryPageData>((v) => validateV2('page', v))
export function queryMetadata(raw: unknown): QueryResultMetadata {
  const value = metadataSchema.parse(raw)
  if (value.kind !== 'query' || !['asserted', 'asserted+derived'].includes(value.scope))
    throw new Error('query.invalidResult')
  return structuredClone(value)
}
export function sameResult(a: QueryResultIdentity, b: QueryResultIdentity): boolean {
  return (
    a.projectId === b.projectId &&
    a.resultId === b.resultId &&
    a.inputSnapshotId === b.inputSnapshotId &&
    a.scope === b.scope &&
    a.parametersHash === b.parametersHash
  )
}
export function acceptPage(
  raw: unknown,
  metadata: QueryResultMetadata,
  columns: readonly string[],
): QueryPageData {
  const page = pageSchema.parse(raw)
  if (
    !sameResult(page.binding, metadata) ||
    metadata.payloadStatus !== 'available' ||
    columns.length > 64 ||
    columns.some((s) => typeof s !== 'string' || s.length > 128) ||
    new Set(page.rows.map((row) => row.rowId)).size !== page.rows.length ||
    page.rows.some(
      (row, i) =>
        row.cells.length !== columns.length ||
        (i > 0 &&
          (row.ordinal < page.rows[i - 1].ordinal ||
            (row.ordinal === page.rows[i - 1].ordinal && row.rowId <= page.rows[i - 1].rowId))),
    )
  ) {
    throw new Error('query.invalidPage')
  }
  return structuredClone(page)
}

export function resultNotice(metadata: QueryResultMetadata): string {
  const snapshot = `快照 ${metadata.inputSnapshotId}；项目版本 ${metadata.inputProjectRevision}`
  const state =
    metadata.state === 'historical'
      ? '历史结果'
      : metadata.state === 'stale'
        ? '已过期，请明确选择输入后重新执行'
        : '当前结果'
  return `${state}；${snapshot}${metadata.historicalSelectionRequired ? '；用于后续操作需显式选择历史输入' : ''}`
}

export function exportPageCsv(page: QueryPageData, columns: readonly string[]): string {
  // Export only this accepted bounded page. Larger exports are a separate flow.
  if (
    columns.length > 64 ||
    page.rows.length > 200 ||
    page.rows.some((r) => r.cells.length !== columns.length)
  ) {
    throw new Error('query.invalidPage')
  }
  const escape = (value: unknown) => {
    let text = value === null ? '' : String(value)
    if (/^[\s]*[=+\-@]/u.test(text) || /^[\t\r\n]/u.test(text)) text = `'${text}`
    return `"${text.replaceAll('"', '""')}"`
  }
  return (
    [columns, ...page.rows.map((row) => row.cells)]
      .map((row) => row.map(escape).join(','))
      .join('\r\n') + '\r\n'
  )
}
