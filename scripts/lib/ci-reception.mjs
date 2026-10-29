// 可信 CI 终态接收：输入必须来自明确 run/attempt 的 GitHub 官方 API 数据
// （受控抓取落盘的 runs/:id、attempt jobs、artifacts、当前 PR JSON）。
// 拒绝：failed/cancelled/skipped/missing/unknown、bootstrap/needs_triage/
// 机械检查未过的报告、政策版本错配、verifier 来自候选树、旧 base/head、
// 重复冒名 job、attempt 无法证明、artifact 缺失、来源清单缺失。
// local-fixture 证据源只用于本地测试，永远不构成真实 CI 通过。
import { createHash } from 'node:crypto'

export function sha256Hex(data) {
  return createHash('sha256').update(data).digest('hex')
}

// 结构化 CLI 参数解析（W01：receive 脚本不得从 process.argv[0] 开始解析）。
// spec: { optionName: 'flag'|'value' }；未知参数、缺值、重复均为错误。
export function parseKnownOptions(argvList, spec) {
  const parsed = {}
  const errors = []
  for (let i = 0; i < argvList.length; i++) {
    const arg = argvList[i]
    if (!arg.startsWith('--')) {
      errors.push(`无法识别的参数：${arg}`)
      continue
    }
    const key = arg.slice(2)
    const kind = spec[key]
    if (kind !== 'value') {
      errors.push(`未知参数：--${key}`)
      continue
    }
    if (key in parsed) {
      errors.push(`参数重复：--${key}`)
      continue
    }
    const value = argvList[i + 1]
    if (value === undefined || value.startsWith('--')) {
      errors.push(`参数 --${key} 缺少取值`)
      continue
    }
    parsed[key] = value
    i++
  }
  return { parsed, errors }
}

// 抓取辅助：用 gh CLI 拉取官方数据并落盘（受控执行，仅读取，不执行 PR 内容）。
export const CONTROLLED_FETCH_COMMANDS = [
  'gh api repos/{owner}/{repo}/actions/runs/{run_id} > run.json',
  'gh api repos/{owner}/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs > jobs.json',
  'gh api repos/{owner}/{repo}/actions/runs/{run_id}/artifacts > artifacts.json',
  'gh api repos/{owner}/{repo}/pulls/{number} > current-pr.json',
  'gh api repos/{owner}/{repo}/git/ref/heads/{base_branch} > current-base.json',
]

function workflowTail(value) {
  return (value ?? '')
    .replace(/^\.?\//, '')
    .split('/')
    .slice(-2)
    .join('/')
}

export function receiveCiFinalState({
  report,
  policy,
  policySha256,
  run,
  jobsPayload,
  artifactsPayload,
  currentPull,
  currentBaseSha,
  fetchManifest,
  evidenceSource,
}) {
  const errors = []
  const checks = []
  const push = (name, expected, actual, pass) => checks.push({ name, expected, actual, pass })

  if (!['github-api', 'local-fixture'].includes(evidenceSource ?? '')) {
    return { status: 'fail', errors: [`未知证据源：${evidenceSource}`], checks }
  }
  if (evidenceSource === 'local-fixture') {
    errors.push('本地 fixture 证据：仅用于测试，不构成真实 CI 通过证据')
  }

  // ---- 候选报告自身必须机械干净（W04）----
  push('report-status', 'pass', report.status, report.status === 'pass')
  if (report.status !== 'pass') errors.push('候选报告不是 pass，终态接收无意义')
  if (report.bootstrap?.untrusted === true) {
    push('report-bootstrap', 'trusted', 'untrusted_bootstrap', false)
    errors.push('不可信 bootstrap 报告不能作为新 gate 终态通过（须先建立可信基线）')
  }
  const failedChecks = (report.checks ?? []).filter((check) => !check.pass)
  push(
    'report-mechanical-checks',
    '0 failures',
    `${failedChecks.length} failures`,
    failedChecks.length === 0,
  )
  if (failedChecks.length > 0) {
    errors.push(`候选报告存在未通过的机械检查：${failedChecks.map((c) => c.name).join(',')}`)
  }
  const pendingTriage = report.classification?.pendingTriage ?? []
  push(
    'report-pending-triage',
    'empty',
    `${pendingTriage.length} items`,
    pendingTriage.length === 0,
  )
  if (report.classification?.level === 'needs_triage' || pendingTriage.length > 0) {
    errors.push('候选分级仍是 needs_triage（人工裁定未闭合），不能接收')
  }

  // ---- 政策与校验器版本绑定（W03/W04）----
  push(
    'policy-sha256',
    report.trustedPolicySha256 ?? '<missing>',
    policySha256,
    policySha256 === report.trustedPolicySha256,
  )
  if (policySha256 !== report.trustedPolicySha256) {
    errors.push('接收所用政策与候选报告绑定的可信政策版本不一致')
  }
  if (report.ci?.workflowSha256 === null || report.ci?.workflowSha256 === undefined) {
    push('workflow-sha256', 'present', 'missing', false)
    errors.push('候选报告缺少 workflow 文件 hash，无法绑定工作流身份')
  }
  const verifierSource = report.verifierProvenance?.source
  push(
    'verifier-provenance',
    'base-tree',
    verifierSource ?? '<missing>',
    verifierSource === 'base-tree',
  )
  if (verifierSource !== 'base-tree') {
    errors.push(
      `校验器来源不可信（${verifierSource ?? 'missing'}）：终态通过只接受目标基线树内校验器产生的报告`,
    )
  }

  // ---- 受控抓取来源（W05）----
  if (evidenceSource === 'github-api') {
    const manifestOk =
      fetchManifest &&
      Array.isArray(fetchManifest.commands) &&
      typeof fetchManifest.fetchedAtUtc === 'string' &&
      typeof fetchManifest.operator === 'string'
    push('fetch-manifest', 'present', manifestOk ? 'present' : 'missing', Boolean(manifestOk))
    if (!manifestOk)
      errors.push('github-api 证据源缺少受控抓取清单（commands/fetchedAtUtc/operator）')
  }

  // ---- run 身份（W05）----
  if (!run || typeof run.id !== 'number') {
    return { status: 'fail', errors: [...errors, '缺少 run 官方数据'], checks }
  }
  const expectRunId = String(report.ci.runId)
  if (String(run.id) !== expectRunId) {
    push('run-id', expectRunId, String(run.id), false)
    errors.push('run 身份与候选报告不一致')
  }
  if (String(run.run_attempt) !== String(report.ci.runAttempt)) {
    push('run-attempt', String(report.ci.runAttempt), String(run.run_attempt), false)
    errors.push('run attempt 与候选报告不一致')
  }
  if (run.status !== 'completed') {
    push('run-status', 'completed', run.status, false)
    errors.push(`run 尚未结束（status=${run.status}）`)
  }
  const headMatches = run.head_sha === report.prHeadSha || run.head_sha === report.ciCheckoutSha
  push('run-head-sha', `${report.prHeadSha} 或 ${report.ciCheckoutSha}`, run.head_sha, headMatches)
  if (!headMatches)
    errors.push('run 的 head_sha 与候选 head/checkout 均不匹配（拒绝旧运行/错配运行）')
  const workflowMatch = workflowTail(run.path) === workflowTail(report.ci.workflowPath)
  push('workflow-path', report.ci.workflowPath, run.path, workflowMatch)
  if (!workflowMatch) errors.push('run 所属 workflow 与候选报告不一致')
  if (run.conclusion !== 'success') {
    push('workflow-conclusion', 'success', String(run.conclusion), false)
    errors.push(`workflow 结论是 ${run.conclusion ?? 'unknown'}，不是 success`)
  }

  // ---- 当前 PR 与目标基线（W05：旧绿灯拒绝）----
  if (!currentPull || typeof currentPull.number !== 'number') {
    errors.push('缺少当前 PR 官方数据')
  } else {
    const prChecks = [
      ['pr-state', 'open', currentPull.state],
      ['pr-number', String(report.pullRequestNumber), String(currentPull.number)],
      ['pr-head-sha', report.prHeadSha, currentPull.head?.sha],
      ['pr-base-sha', report.targetBaseSha, currentPull.base?.sha],
      ['pr-base-current', currentPull.base?.sha, currentBaseSha],
    ]
    for (const [name, expected, actual] of prChecks) {
      const pass = expected === actual
      push(name, String(expected), String(actual), pass)
      if (!pass) errors.push(`当前 PR 校验失败：${name}`)
    }
  }
  if (!currentBaseSha) errors.push('缺少当前目标基线 SHA（无法证明目标分支未前进）')

  // ---- 必需 job：存在、唯一、成功、归属当前 run/attempt（W05）----
  const requiredNames = policy.validation.full_ci
  const jobs = jobsPayload?.jobs ?? []
  for (const required of requiredNames) {
    const matches = jobs.filter((job) => job.name === required)
    if (matches.length === 0) {
      push(`required-job:${required}`, 'success', 'missing', false)
      errors.push(`必需 job 缺失：${required}`)
      continue
    }
    if (matches.length > 1) {
      push(`required-job:${required}:uniqueness`, 'exactly-1', String(matches.length), false)
      errors.push(`必需 job ${required} 存在 ${matches.length} 个同名条目（冒名/重复拒绝）`)
      continue
    }
    const job = matches[0]
    const conclusion = job.conclusion ?? 'unknown'
    const pass = job.status === 'completed' && conclusion === 'success'
    push(`required-job:${required}`, 'success', `${job.status}/${conclusion}`, pass)
    if (!pass) errors.push(`必需 job ${required} 非成功：${job.status}/${conclusion}`)
    if (String(job.run_id) !== String(run.id)) {
      errors.push(`job ${required} 属于另一个 run（${job.run_id}）`)
    }
    if (job.run_attempt === undefined || job.run_attempt === null) {
      push(`required-job:${required}:attempt`, 'present', 'missing', false)
      errors.push(`job ${required} 缺少 run_attempt 归属（须使用 attempts/:n/jobs 端点数据）`)
    } else if (String(job.run_attempt) !== String(run.run_attempt)) {
      push(
        `required-job:${required}:attempt`,
        String(run.run_attempt),
        String(job.run_attempt),
        false,
      )
      errors.push(`job ${required} 属于另一次 attempt（${job.run_attempt}）`)
    }
  }

  // ---- artifact 绑定（W05）----
  const artifacts = artifactsPayload?.artifacts ?? []
  const expectedArtifacts = report.ci.expectedArtifactNames ?? []
  for (const name of expectedArtifacts) {
    const match = artifacts.find((artifact) => artifact.name === name)
    if (!match) {
      push(`artifact:${name}`, 'present', 'missing', false)
      errors.push(`候选证据 artifact 缺失：${name}`)
      continue
    }
    if (String(match.workflow_run?.id ?? run.id) !== String(run.id)) {
      push(`artifact:${name}:run`, String(run.id), String(match.workflow_run?.id), false)
      errors.push(`artifact ${name} 不属于当前 run`)
    }
    if (match.expired === true) {
      push(`artifact:${name}:expired`, 'false', 'true', false)
      errors.push(`artifact ${name} 已过期`)
    }
    if (match.digest && report.ci.expectedArtifactDigests?.[name]) {
      const pass = match.digest === report.ci.expectedArtifactDigests[name]
      push(`artifact:${name}:digest`, report.ci.expectedArtifactDigests[name], match.digest, pass)
      if (!pass) errors.push(`artifact ${name} 的 digest 与本地证据不一致`)
    }
  }

  return {
    status: errors.length === 0 ? 'pass' : 'fail',
    evidenceSource,
    checks,
    errors,
    note: '报告模式：接收结论不触发合并，合并仍须人工/总控按政策执行；bootstrap/unknown 不是新 gate 的 Pass',
  }
}
