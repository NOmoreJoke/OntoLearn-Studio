import { describe, expect, it } from 'vitest'
import { validateV2 } from '../../packages/contracts/src/v2'
import {
  acceptPage,
  exportPageCsv,
  queryMetadata,
  resultNotice,
} from '../../apps/desktop/src/renderer/src/query/results'

const id = (n: number) => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`
const hash = 'a'.repeat(64)
function metadata() {
  return {
    projectId: id(1),
    resultId: id(2),
    jobId: id(3),
    kind: 'query' as const,
    definitionId: 'Q-01',
    inputSnapshotId: hash,
    inputProjectRevision: 3,
    dependencyVector: { 'facts:asserted': 3 },
    definitionSetDigests: {},
    implementation: {
      executionSemanticsVersion: 'v1',
      engineVersion: '0.1.0',
      dependencyLockHash: hash,
    },
    scope: 'asserted' as const,
    parametersHash: hash,
    state: 'current' as const,
    staleReason: [],
    payloadStatus: 'available' as const,
    createdAtMs: 1,
    historicalSelectionRequired: false,
  }
}
function page() {
  const { projectId, resultId, inputSnapshotId, scope, parametersHash } = metadata()
  return {
    binding: {
      projectId,
      resultId,
      inputSnapshotId,
      scope,
      parametersHash,
      order: 'ordinal+rowId:asc' as const,
    },
    rows: [{ rowId: id(4), ordinal: 0, cells: ['urn:t04:A01', 'High', 'Open'] }],
    nextCursor: null,
  }
}
const columns = ['告警', '等级', '状态']

describe('T04 result display uses approved result/page validators', () => {
  it('accepts full bounded rows, preserves identity and clones inputs', () => {
    expect(validateV2('result', metadata())).toBe(true)
    expect(validateV2('page', page())).toBe(true)
    const input = page()
    const result = acceptPage(input, queryMetadata(metadata()), columns)
    input.rows[0].cells[0] = 'changed'
    expect(result.rows).toEqual([
      { rowId: id(4), ordinal: 0, cells: ['urn:t04:A01', 'High', 'Open'] },
    ])
  })
  it('rejects every identity mismatch, unknown fields, evicted data and wrong result kind', () => {
    for (const patch of [
      { projectId: id(20) },
      { resultId: id(21) },
      { inputSnapshotId: 'b'.repeat(64) },
      { scope: 'asserted+derived' },
      { parametersHash: 'c'.repeat(64) },
    ]) {
      expect(() =>
        acceptPage(
          { ...page(), binding: { ...page().binding, ...patch } },
          queryMetadata(metadata()),
          columns,
        ),
      ).toThrow()
    }
    expect(() => queryMetadata({ ...metadata(), kind: 'reasoning' })).toThrow()
    expect(() => queryMetadata({ ...metadata(), scope: 'scenario' })).toThrow()
    expect(() => queryMetadata({ ...metadata(), extra: 'unknown' })).toThrow()
    expect(() =>
      acceptPage({ ...page(), extra: true }, queryMetadata(metadata()), columns),
    ).toThrow()
    expect(() =>
      acceptPage(page(), queryMetadata({ ...metadata(), payloadStatus: 'evicted' }), columns),
    ).toThrow()
  })
  it('rejects duplicate/out of order rows, field mismatches and more than one page', () => {
    for (const rows of [
      [...page().rows, ...page().rows],
      [page().rows[0], { rowId: id(5), ordinal: 0, cells: [] }],
      [
        { ...page().rows[0], ordinal: 1 },
        { ...page().rows[0], rowId: id(5), ordinal: 0 },
      ],
      Array(201).fill(page().rows[0]),
    ]) {
      expect(() => acceptPage({ ...page(), rows }, queryMetadata(metadata()), columns)).toThrow()
    }
  })
  it('never promotes historical or stale metadata into current results', () => {
    const historical = queryMetadata({
      ...metadata(),
      state: 'historical',
      historicalSelectionRequired: true,
    })
    expect(resultNotice(historical)).toContain('历史结果')
    expect(resultNotice(historical)).toContain(hash)
    const stale = queryMetadata({
      ...metadata(),
      state: 'stale',
      staleReason: [{ code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 3, after: 4 }],
    })
    expect(resultNotice(stale)).toContain('已过期')
    expect(stale.staleReason).toEqual([
      { code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 3, after: 4 },
    ])
  })
  it('exports the accepted page only with safe text cells and formula handling', () => {
    const input = {
      ...page(),
      rows: [{ rowId: id(4), ordinal: 0, cells: ['=SUM(1)', '"quoted"\nnext', null] }],
    }
    const accepted = acceptPage(input, queryMetadata(metadata()), columns)
    expect(exportPageCsv(accepted, columns)).toBe(
      '"告警","等级","状态"\r\n"\'=SUM(1)","""quoted""\nnext",""\r\n',
    )
  })
})
