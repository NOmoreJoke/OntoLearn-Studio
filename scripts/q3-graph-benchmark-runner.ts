import { performance } from 'node:perf_hooks'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { QueryResultPanel } from '../apps/desktop/src/renderer/src/query/QueryResultPanel'
import { buildResultGraph } from '../apps/desktop/src/renderer/src/query/result-graph'
import { graphFixture, profiles, sha256, summarize } from './q3-graph-benchmark-fixture'

export function runBenchmark(seed: number, warmup: number, repetitions: number) {
  const cases = []
  for (const count of [0, 32, 512, 1024, 2048, 4096]) {
    for (const profile of profiles) {
      const fixture = graphFixture(count, profile, seed)
      const call = () =>
        buildResultGraph(
          fixture.source,
          fixture.descriptor,
          fixture.page,
          fixture.requested,
          fixture.rowKey,
        )
      const expected = call()
      const expectedHash = sha256(JSON.stringify(expected))
      const render = () =>
        renderToStaticMarkup(
          createElement(QueryResultPanel, {
            projectId: fixture.source.projectId,
            resultId: fixture.descriptor.identity.resultId,
            descriptor: fixture.descriptor,
            graphSource: fixture.source,
            rows: { value: fixture.page, requested: fixture.requested },
          }),
        )
      const markupHash = sha256(render())
      for (const mode of ['buildResultGraph', 'QueryResultPanel-SSR'] as const) {
        const samples = []
        for (let iteration = 0; iteration < warmup + repetitions; iteration++) {
          const before = process.memoryUsage()
          const start = performance.now()
          const output = mode === 'buildResultGraph' ? call() : render()
          const milliseconds = performance.now() - start
          const after = process.memoryUsage()
          const outputSha256 = sha256(typeof output === 'string' ? output : JSON.stringify(output))
          if (outputSha256 !== (mode === 'buildResultGraph' ? expectedHash : markupHash))
            throw new Error('NONDETERMINISTIC_BENCHMARK_OUTPUT')
          samples.push({
            iteration,
            warmup: iteration < warmup,
            milliseconds,
            heapUsedBefore: before.heapUsed,
            heapUsedAfter: after.heapUsed,
            rssBefore: before.rss,
            rssAfter: after.rss,
            outputSha256,
          })
        }
        cases.push({
          factCount: count,
          profile,
          mode,
          seed,
          inputSha256: fixture.inputSha256,
          sourceBytes: fixture.sourceBytes,
          sourceAccepted: fixture.sourceAccepted,
          pageBytes: Buffer.byteLength(JSON.stringify(fixture.page)),
          outputGraph:
            expected.state === 'ready'
              ? {
                  state: expected.state,
                  anchors: expected.anchors.length,
                  totalEdges: expected.totalEdges,
                  displayedEdges: expected.edges.length,
                  omittedRecords: expected.omittedRecords,
                }
              : { state: expected.state, reason: expected.reason },
          summary: summarize(
            samples.filter((sample) => !sample.warmup).map((sample) => sample.milliseconds),
          ),
          samples,
        })
      }
    }
  }
  return { seed, warmup, repetitions, cases }
}
