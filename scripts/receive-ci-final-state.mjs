#!/usr/bin/env node
// receive-ci-final-state：可信 CI 终态接收 CLI。
// 输入必须来自明确 run/attempt 的 GitHub 官方 API 数据（受控抓取落盘，命令模板见
// CONTROLLED_FETCH_COMMANDS），或明确标注 local-fixture 的本地测试数据。
// 校验当前 PR/目标基线、全部 required job、artifact 与候选身份绑定；
// 报告模式，不自动合并；bootstrap/unknown 不是新 gate 的 Pass。
import { readFileSync, writeFileSync } from 'node:fs'
import { argv } from 'node:process'
import {
  CONTROLLED_FETCH_COMMANDS,
  parseKnownOptions,
  receiveCiFinalState,
  sha256Hex,
} from './lib/ci-reception.mjs'
import { parsePolicyText } from './lib/review-policy.mjs'

const OPTION_SPEC = {
  report: 'value',
  run: 'value',
  jobs: 'value',
  artifacts: 'value',
  policy: 'value',
  'current-pr': 'value',
  'current-base-sha': 'value',
  'fetch-manifest': 'value',
  'evidence-source': 'value',
  output: 'value',
}

function usage(extraErrors) {
  process.stderr.write(
    [
      ...(extraErrors ?? []).map((error) => `错误：${error}`),
      '用法：node scripts/receive-ci-final-state.mjs \\',
      '  --report <verify-candidate 输出 JSON> \\',
      '  --run <runs/:id 官方 JSON> \\',
      '  --jobs <attempts/:n/jobs 官方 JSON> \\',
      '  --artifacts <run artifacts 官方 JSON> \\',
      '  --policy <可信政策文件> \\',
      '  --current-pr <pulls/:number 官方 JSON> \\',
      '  --current-base-sha <当前目标基线完整 SHA> \\',
      '  [--fetch-manifest <受控抓取清单 JSON>] \\',
      '  [--evidence-source github-api|local-fixture] \\',
      '  [--output <结果 JSON 路径>]',
      '',
      '受控抓取命令模板：',
      ...CONTROLLED_FETCH_COMMANDS.map((line) => `  ${line}`),
      '',
    ].join('\n'),
  )
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch (error) {
    process.stderr.write(`${label} 读取/解析失败：${error.message}\n`)
    process.exit(2)
  }
}

// W01：只解析用户参数（跳过 node 可执行路径与脚本路径），结构化白名单校验。
const { parsed: args, errors: parseErrors } = parseKnownOptions(argv.slice(2), OPTION_SPEC)
if (parseErrors.length > 0) {
  usage(parseErrors)
  process.exit(2)
}

const requiredOptions = [
  'report',
  'run',
  'jobs',
  'artifacts',
  'policy',
  'current-pr',
  'current-base-sha',
]
for (const required of requiredOptions) {
  if (!args[required]) {
    usage([`缺少 --${required}`])
    process.exit(2)
  }
}
const evidenceSource = args['evidence-source'] ?? 'github-api'
if (evidenceSource === 'github-api' && !args['fetch-manifest']) {
  usage(['github-api 证据源必须提供 --fetch-manifest（受控抓取清单）'])
  process.exit(2)
}
if (!/^[0-9a-f]{40}$/.test(args['current-base-sha'])) {
  usage(['--current-base-sha 必须是 40 位小写十六进制完整 SHA'])
  process.exit(2)
}

const report = readJson(args.report, '候选报告')
const run = readJson(args.run, 'run 数据')
const jobsPayload = readJson(args.jobs, 'jobs 数据')
const artifactsPayload = readJson(args.artifacts, 'artifacts 数据')
const currentPull = readJson(args['current-pr'], '当前 PR 数据')
const fetchManifest = args['fetch-manifest'] ? readJson(args['fetch-manifest'], '抓取清单') : null
const policyBytes = readFileSync(args.policy)
const policy = parsePolicyText(policyBytes.toString('utf8'), args.policy)
const policySha256 = sha256Hex(policyBytes)

if (report.status !== 'pass') {
  process.stderr.write('候选报告本身不是 pass，终态接收无意义；先修复机械校验。\n')
  process.exit(2)
}

const result = receiveCiFinalState({
  report,
  policy,
  policySha256,
  run,
  jobsPayload,
  artifactsPayload,
  currentPull,
  currentBaseSha: args['current-base-sha'],
  fetchManifest,
  evidenceSource,
})

const output = JSON.stringify(result, null, 2) + '\n'
if (args.output) {
  writeFileSync(args.output, output)
} else {
  process.stdout.write(output)
}
process.exit(result.status === 'pass' ? 0 : 1)
