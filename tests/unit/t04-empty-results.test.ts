import { createHash } from 'node:crypto'
import { createElement, type ComponentType } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import {
  currentPageCsv,
  type DisplayDescriptor,
} from '../../apps/desktop/src/renderer/src/query/typed-results'
import type { QueryResultPanelProps } from '../../apps/desktop/src/renderer/src/query/typed-result-panel-props'

// Real TSX rendering with consumer fixtures; not a Store/Q-02/native-download run.
const panelModule = '../../apps/desktop/src/renderer/src/query/QueryResultPanel'
const { QueryResultPanel }: { QueryResultPanel: ComponentType<QueryResultPanelProps> } =
  await import(panelModule)
const hash = (value: string) => createHash('sha256').update(value).digest('hex')
const descriptorRef = '40000000-0000-4000-8000-000000000001'
const cursor = '40000000-0000-4000-8000-000000000002'
const emptyHeading = 'SELECT 完整结果为空。以下是检查方向，不是对数据原因的判断。'

function setup() {
  const metadata = structuredClone(
    (
      fixtures.cases.find((item) => item.name === 'response result.get')!.value as unknown as {
        result: DisplayDescriptor['metadata']
      }
    ).result,
  )
  const text = 'SELECT ?alarm ?equipment WHERE { ?alarm ?p ?equipment }'
  const descriptor: DisplayDescriptor = {
    identity: {
      projectId: metadata.projectId,
      resultId: metadata.resultId,
      jobId: metadata.jobId,
      inputSnapshotId: metadata.inputSnapshotId,
      inputProjectRevision: metadata.inputProjectRevision,
      scope: 'asserted',
      definitionId: metadata.definitionId,
      parametersHash: metadata.parametersHash,
      implementation: metadata.implementation,
      payloadSha256: hash('empty-select-payload'),
      definitionSha256: hash('saved-definition'),
      inputSelection: 'current',
      projectionVersion: 1,
      lengthPolicyId: 'query-presentation-scalars-v1',
    },
    descriptorRef,
    metadata,
    executedText: {
      sha256: hash(text),
      utf8Bytes: Buffer.byteLength(text),
      unicodeScalars: [...text].length,
      utf16Units: text.length,
    },
    query: {
      kind: 'SELECT',
      rowCount: 0,
      columns: [
        { index: 0, name: 'alarm' },
        { index: 1, name: 'equipment' },
      ],
    },
  }
  const rows = {
    value: {
      identity: structuredClone(descriptor.identity),
      kind: 'rows' as const,
      order: 'query-index:asc' as const,
      rows: [],
      nextCursor: null as string | null,
    },
    requested: { descriptorRef, cursor: null as string | null, startIndex: 0, pageSize: 20 },
  }
  const props: QueryResultPanelProps = {
    projectId: metadata.projectId,
    resultId: metadata.resultId,
    descriptor,
    rows,
  }
  const render = () => renderToStaticMarkup(createElement(QueryResultPanel, props))
  return { descriptor, rows, props, render }
}

describe('verified SELECT empty results', () => {
  it('shows actionable checks only for the verified snapshot and exports a header-only CSV', () => {
    const x = setup(),
      markup = x.render()
    expect(markup).toContain(emptyHeading)
    expect(markup).toContain('aria-label="SELECT 空结果检查"')
    expect(markup).toContain('执行范围：断言事实')
    expect(markup).toContain(x.descriptor.identity.inputSnapshotId)
    expect(markup).toContain('当前结果')
    expect(markup).toContain('可逐项放宽条件后复查')
    expect(markup).toContain('检查字段是否有记录，以及映射是否成功提交到当前项目')
    expect(markup).toContain('不能据此证明业务事实不存在')
    expect(markup).toContain('导出当前页 CSV')
    expect(markup).not.toContain('typed-query-graph')
    expect(markup).not.toContain('ASK：')
    expect(currentPageCsv(x.descriptor, x.rows.value, x.rows.requested)).toBe(
      '"alarm","equipment"\r\n',
    )
  })

  it('keeps the original historical input and factual stale reason beside the checks', () => {
    const x = setup()
    x.descriptor.identity.inputSelection = 'historical'
    x.rows.value.identity.inputSelection = 'historical'
    x.descriptor.metadata.state = 'stale'
    x.descriptor.metadata.historicalSelectionRequired = true
    x.descriptor.metadata.staleReason = [
      { code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 1, after: 2 },
    ]
    const markup = x.render()
    expect(markup).toContain(emptyHeading)
    expect(markup).toContain('显式选择的历史快照')
    expect(markup).toContain('FACTS_CHANGED')
    expect(markup).toContain('已过期，请明确选择输入后重新执行')
    expect(markup).toContain(x.descriptor.identity.inputSnapshotId)
    expect(x.descriptor.identity.inputProjectRevision).toBe(1)
    expect(markup).not.toContain('因为数据过期而没有结果')
  })

  it('does not interpret missing or loading rows as a verified empty result', () => {
    const x = setup()
    x.props.rows = undefined
    expect(x.render()).toContain('尚未取得结果页，不以缺少页面解释为空结果')
    expect(x.render()).not.toContain(emptyHeading)
    expect(x.render()).not.toContain('导出当前页 CSV')
    x.props.rows = x.rows
    x.props.rowsLoading = true
    expect(x.render()).toContain('正在读取固定结果页')
    expect(x.render()).not.toContain(emptyHeading)
  })

  it('rejects empty pages with a different snapshot, descriptor, range or continuation', () => {
    for (const variant of ['snapshot', 'descriptor', 'range', 'cursor']) {
      const x = setup()
      if (variant === 'snapshot') x.rows.value.identity.inputSnapshotId = hash('different-input')
      if (variant === 'descriptor') x.rows.requested.descriptorRef = cursor
      if (variant === 'range') x.rows.requested.startIndex = 1
      if (variant === 'cursor') x.rows.value.nextCursor = cursor
      expect(x.render()).toContain('结果页身份、行次序或列宽不匹配')
      expect(x.render()).not.toContain(emptyHeading)
      expect(x.render()).not.toContain('导出当前页 CSV')
      expect(() => currentPageCsv(x.descriptor, x.rows.value, x.rows.requested)).toThrow()
    }
  })

  it('does not diagnose empty results after a failed or evicted read', () => {
    for (const code of ['INVALID_STATE', 'PAYLOAD_EVICTED']) {
      const x = setup()
      x.props.readFailure = {
        projectId: x.props.projectId,
        resultId: x.props.resultId,
        descriptorRef,
        error: {
          code,
          messageKey:
            code === 'PAYLOAD_EVICTED' ? 'result.payloadEvicted' : 'protocol.invalidState',
          retryable: false,
          params: code === 'PAYLOAD_EVICTED' ? { resultId: x.props.resultId } : {},
        },
      }
      expect(x.render()).toContain(code === 'PAYLOAD_EVICTED' ? '载荷已回收' : '结果读取未完成')
      expect(x.render()).not.toContain(emptyHeading)
      expect(x.render()).not.toContain('导出当前页 CSV')
    }
  })

  it('holds empty-result checks when a read failure receipt has the wrong result binding', () => {
    const x = setup()
    x.props.readFailure = {
      projectId: x.props.projectId,
      resultId: cursor,
      descriptorRef,
      error: {
        code: 'INVALID_STATE',
        messageKey: 'protocol.invalidState',
        retryable: false,
        params: {},
      },
    }
    expect(x.render()).toContain('读取回执与当前结果不匹配')
    expect(x.render()).not.toContain(emptyHeading)
  })

  it('keeps ASK false boolean instead of presenting SELECT empty-result checks', () => {
    const x = setup()
    x.descriptor.query = { kind: 'ASK', value: false }
    x.props.rows = undefined
    const markup = x.render()
    expect(markup).toContain('ASK：false（未满足查询条件）')
    expect(markup).toContain('这是布尔结果，不是 SELECT 空表')
    expect(markup).toContain('导出 ASK 结果 CSV')
    expect(markup).not.toContain(emptyHeading)
    expect(markup).not.toContain('导出当前页 CSV')
  })

  it('distinguishes an empty end page from a nonempty complete result', () => {
    const x = setup()
    if (x.descriptor.query.kind !== 'SELECT') throw new Error('expected SELECT')
    x.descriptor.query.rowCount = 1
    x.rows.requested.startIndex = 1
    x.rows.requested.cursor = cursor
    expect(x.render()).toContain('本页没有记录；完整结果不为空')
    expect(x.render()).not.toContain(emptyHeading)
  })
})
