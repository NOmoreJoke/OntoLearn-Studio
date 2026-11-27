import { describe, expect, it } from 'vitest'
import { graphFixture, profiles, summarize } from '../../scripts/q3-graph-benchmark-fixture'
import { buildResultGraph } from '../../apps/desktop/src/renderer/src/query/result-graph'

describe('Q3 reproducible performance inputs and statistics', () => {
  it('preserves seed identity and records actual consumer acceptance or rejection at each scale', () => {
    for (const count of [0, 32, 512, 1024, 2048, 4096])
      for (const profile of profiles) {
        const x = graphFixture(count, profile, 20261112)
        expect(x.source.domain.state.facts).toHaveLength(count)
        expect(x.sourceBytes).toBeLessThanOrEqual(1572864)
        expect(graphFixture(count, profile, 20261112).inputSha256).toBe(x.inputSha256)
        const result = buildResultGraph(x.source, x.descriptor, x.page, x.requested, x.rowKey)
        expect(result.state).toBe(x.sourceAccepted ? 'ready' : 'unavailable')
        if (count <= 512) expect(x.sourceAccepted).toBe(true)
        if (count >= 2048) expect(x.sourceAccepted).toBe(false)
        if (result.state !== 'ready') continue
        const expected = x.source.domain.state.facts.filter(
          (fact) => fact.object?.startsWith('<') && result.anchors.includes(fact.subject),
        )
        expect(result.totalEdges).toBe(expected.length)
        expect(result.edges.flatMap((edge) => edge.supports.map((fact) => fact.id))).toEqual(
          expected.slice(0, 24).map((fact) => fact.id),
        )
      }
  })
  it('rejects out-of-contract size rather than benchmarking an invalid success', () => {
    expect(() => graphFixture(4097, profiles[0], 1)).toThrow('FACT_COUNT_OUTSIDE_READ_CONTRACT')
    expect(() => graphFixture(32, profiles[0], -1)).toThrow('INVALID_SEED')
  })
  it('computes even median and nearest-rank p95 without discarding slow samples', () => {
    expect(summarize([4, 1, 2, 100])).toEqual({
      count: 4,
      minMs: 1,
      medianMs: 3,
      p95Ms: 100,
      maxMs: 100,
    })
    expect(() => summarize([])).toThrow('INVALID_SAMPLES')
    expect(() => summarize([NaN])).toThrow('INVALID_SAMPLES')
  })
})
