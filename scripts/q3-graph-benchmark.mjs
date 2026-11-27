#!/usr/bin/env node
import { createServer } from 'vite'
import { createHash } from 'node:crypto'
import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { execFileSync } from 'node:child_process'
import { cpus, totalmem, release, platform, arch } from 'node:os'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const [destination, seedText = '20261112', repetitionsText = '25'] = process.argv.slice(2)
if (!destination || process.argv.length > 5)
  throw new Error(
    'Usage: node scripts/q3-graph-benchmark.mjs NEW_OUTPUT_DIRECTORY [uint32_seed] [repetitions_5_to_1000]',
  )
const seed = Number(seedText),
  repetitions = Number(repetitionsText)
if (
  !Number.isSafeInteger(seed) ||
  seed < 0 ||
  seed > 0xffffffff ||
  !Number.isInteger(repetitions) ||
  repetitions < 5 ||
  repetitions > 1000
)
  throw new Error('Invalid benchmark parameters')
const output = resolve(destination)
// Atomic new directory refuses to overwrite earlier runs or first failures.
await mkdir(output, { recursive: false })
const hash = (data) => createHash('sha256').update(data).digest('hex')
const git = (args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim()
const paths = [
  'scripts/q3-graph-benchmark.mjs',
  'scripts/q3-graph-benchmark-runner.ts',
  'scripts/q3-graph-benchmark-fixture.ts',
  'apps/desktop/src/renderer/src/query/result-graph.ts',
  'apps/desktop/src/renderer/src/query/QueryResultPanel.tsx',
  'apps/desktop/src/renderer/src/query/typed-results.ts',
  'packages/contracts/v2/fixtures.json',
  'packages/contracts/v2/schema.json',
  'packages/contracts/src/v2.ts',
  'package-lock.json',
  'uv.lock',
]
const sources = Object.fromEntries(
  await Promise.all(paths.map(async (path) => [path, hash(await readFile(resolve(root, path)))])),
)
const environment = {
  atUTC: new Date().toISOString(),
  platform: platform(),
  release: release(),
  arch: arch(),
  cpuModels: [...new Set(cpus().map((cpu) => cpu.model))],
  logicalCPUs: cpus().length,
  totalMemoryBytes: totalmem(),
  runtimeVersions: process.versions,
  powerMode: process.env.Q3_BENCHMARK_POWER_MODE ?? 'not recorded',
  powerModeEvidence: 'operator supplied; not independently detected',
  head: git(['rev-parse', 'HEAD']),
  tree: git(['rev-parse', 'HEAD^{tree}']),
  gitStatus: git(['status', '--short']),
  sources,
  method:
    'Synthetic contract-valid fixtures; fixed size/profile order; first 5 measured invocations warmup; 25 default retained samples; no forced GC; timings exclude fixture generation, hashing and memory sampling. SSR includes whole panel server markup, not browser paint or selected-row interaction. Memory readings are process snapshots, not peak/retained allocation.',
  scope:
    'Local Node/V8 consumer baseline only. No product build, Electron, mapping, query execution, SLA or improvement claim.',
}
await writeFile(resolve(output, 'environment.json'), JSON.stringify(environment, null, 2) + '\n', {
  flag: 'wx',
})
const server = await createServer({
  root,
  configFile: false,
  server: { middlewareMode: true, hmr: false },
  esbuild: { jsx: 'automatic' },
  logLevel: 'error',
})
try {
  const { runBenchmark } = await server.ssrLoadModule('/scripts/q3-graph-benchmark-runner.ts')
  const results = runBenchmark(seed, 5, repetitions)
  await writeFile(resolve(output, 'raw.json'), JSON.stringify(results, null, 2) + '\n', {
    flag: 'wx',
  })
  const summary = results.cases.map(({ samples, ...value }) => ({
    ...value,
    rawSamples: samples.length,
  }))
  await writeFile(resolve(output, 'summary.json'), JSON.stringify(summary, null, 2) + '\n', {
    flag: 'wx',
  })
  const header =
    'facts,profile,mode,iteration,warmup,milliseconds,heapBefore,heapAfter,rssBefore,rssAfter,outputSha256'
  const rows = results.cases.flatMap((entry) =>
    entry.samples.map((sample) =>
      [
        entry.factCount,
        entry.profile.name,
        entry.mode,
        sample.iteration,
        sample.warmup,
        sample.milliseconds,
        sample.heapUsedBefore,
        sample.heapUsedAfter,
        sample.rssBefore,
        sample.rssAfter,
        sample.outputSha256,
      ].join(','),
    ),
  )
  await writeFile(resolve(output, 'raw.csv'), [header, ...rows].join('\n') + '\n', { flag: 'wx' })
  console.log(
    JSON.stringify({
      output,
      cases: results.cases.length,
      rawSamples: rows.length,
      scope: environment.scope,
    }),
  )
} catch (error) {
  await writeFile(resolve(output, 'failure.txt'), String(error?.stack ?? error) + '\n', {
    flag: 'wx',
  })
  throw error
} finally {
  await server.close()
}
