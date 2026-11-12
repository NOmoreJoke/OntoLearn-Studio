import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import {
  parseKnownOptions,
  receiveCiFinalState,
  sha256Hex,
} from '../../scripts/lib/ci-reception.mjs'
import { parsePolicyText } from '../../scripts/lib/review-policy.mjs'

const policyText = readFileSync('.github/review-policy.yml', 'utf8')
const policy = parsePolicyText(policyText, 'policy')
const policySha256 = sha256Hex(policyText)

const BASE = 'a'.repeat(40)
const HEAD = 'b'.repeat(40)
const CHECKOUT = 'c'.repeat(40)
const RUN_ID = 12345

function goodReport(overrides: Record<string, unknown> = {}) {
  return {
    schemaVersion: 1,
    status: 'pass',
    mode: 'report_only',
    bootstrap: { untrusted: false, reason: null },
    repository: 'owner/repo',
    pullRequestNumber: 16,
    targetBaseSha: BASE,
    prHeadSha: HEAD,
    prHeadTree: 'd'.repeat(40),
    ciCheckoutSha: CHECKOUT,
    ciCheckoutTree: 'e'.repeat(40),
    trustedPolicySha256: policySha256,
    verifierProvenance: { source: 'base-tree', base: BASE, files: [] },
    classification: { level: 'L1', pendingTriage: [] },
    checks: [{ name: 'merge-tuple', expected: 'x', actual: 'x', pass: true }],
    ci: {
      event: 'pull_request',
      runId: String(RUN_ID),
      runAttempt: '1',
      workflowPath: '.github/workflows/ci.yml',
      workflowSha256: createHash('sha256').update('ci').digest('hex'),
      expectedArtifactNames: ['verify-candidate-evidence'],
      finalStateReceived: false,
    },
    ...overrides,
  }
}

function goodRun() {
  return {
    id: RUN_ID,
    run_attempt: 1,
    status: 'completed',
    conclusion: 'success',
    head_sha: HEAD,
    path: 'owner/repo/.github/workflows/ci.yml',
  }
}

function goodJobs() {
  return {
    jobs: (policy as { validation: { full_ci: string[] } }).validation.full_ci.map((name) => ({
      name,
      status: 'completed',
      conclusion: 'success',
      run_id: RUN_ID,
      run_attempt: 1,
    })),
  }
}

function goodArtifacts() {
  return {
    artifacts: [
      {
        name: 'verify-candidate-evidence',
        workflow_run: { id: RUN_ID },
        expired: false,
        digest: 'f'.repeat(64),
      },
    ],
  }
}

function goodPull() {
  return {
    number: 16,
    state: 'open',
    head: { sha: HEAD },
    base: { sha: BASE, ref: 'develop' },
  }
}

function goodManifest() {
  return { commands: ['gh api …'], fetchedAtUtc: '2026-10-29T00:00:00Z', operator: 'controller' }
}

function goodInput(): Record<string, unknown> {
  return {
    report: goodReport(),
    policy,
    policySha256,
    run: goodRun(),
    jobsPayload: goodJobs(),
    artifactsPayload: goodArtifacts(),
    currentPull: goodPull(),
    currentBaseSha: BASE,
    fetchManifest: goodManifest(),
    evidenceSource: 'github-api',
  }
}

describe('parseKnownOptions（W01）', () => {
  it('正常解析已知参数', () => {
    const { parsed, errors } = parseKnownOptions(['--report', 'a.json', '--output', 'b.json'], {
      report: 'value',
      output: 'value',
    })
    expect(errors).toEqual([])
    expect(parsed).toEqual({ report: 'a.json', output: 'b.json' })
  })
  it('未知参数、缺值、重复分别是错误', () => {
    const unknown = parseKnownOptions(['--unknown', 'x'], { report: 'value' })
    expect(unknown.errors.join('\n')).toContain('未知参数')
    const missing = parseKnownOptions(['--report', '--output', 'b'], {
      report: 'value',
      output: 'value',
    })
    expect(missing.errors.join('\n')).toContain('缺少取值')
    const duplicated = parseKnownOptions(['--report', 'a', '--report', 'b'], {
      report: 'value',
    })
    expect(duplicated.errors.join('\n')).toContain('重复')
  })
})

describe('receiveCiFinalState（W04/W05 全阻断矩阵）', () => {
  it('全部绑定与终态满足时 pass（github-api + 抓取清单）', () => {
    const result = receiveCiFinalState(goodInput())
    expect(result.errors).toEqual([])
    expect(result.status).toBe('pass')
  })
  it('untrusted bootstrap 报告被拒绝（新 gate 无可信基线时不可 Pass）', () => {
    const input = goodInput()
    input.report = goodReport({ bootstrap: { untrusted: true, reason: '首次部署' } })
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('bootstrap')
  })
  it('workflow_dispatch fail-closed unknown 报告被拒绝（no-trusted-dispatch-baseline）', () => {
    const input = goodInput()
    input.report = {
      schemaVersion: 1,
      status: 'unknown',
      mode: 'report_only',
      event: 'workflow_dispatch',
      reason: 'no-trusted-dispatch-baseline',
    }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('不是 pass')
  })
  it('needs_triage 未闭合被拒绝', () => {
    const input = goodInput()
    input.report = goodReport({
      classification: { level: 'needs_triage', pendingTriage: [{ path: 'x.ts' }] },
    })
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('needs_triage')
  })
  it('报告存在未通过机械检查被拒绝', () => {
    const input = goodInput()
    input.report = goodReport({
      checks: [{ name: 'merge-tuple', expected: 'x', actual: 'y', pass: false }],
    })
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('机械检查')
  })
  it('政策版本与报告绑定不一致被拒绝', () => {
    const input = goodInput()
    input.policySha256 = '0'.repeat(64)
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('政策')
  })
  it('校验器来源非 base-tree（bootstrap/候选树）被拒绝（W03）', () => {
    const input = goodInput()
    input.report = goodReport({
      verifierProvenance: { source: 'candidate-tree-bootstrap', files: [] },
    })
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('校验器来源')
  })
  it('报告缺少 workflowSha256 被拒绝（W05 路径前缀缺陷的接收端防线）', () => {
    const input = goodInput()
    input.report = goodReport({ ci: { ...goodReport().ci, workflowSha256: null } })
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('workflow 文件 hash')
  })
  it('github-api 证据源缺抓取清单被拒绝', () => {
    const input = goodInput()
    input.fetchManifest = null
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('抓取清单')
  })
  it('目标 base 已前进（PR base 与当前基线不一致）拒绝旧绿灯', () => {
    const input = goodInput()
    input.currentBaseSha = 'f'.repeat(40)
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('pr-base-current')
  })
  it('PR head 与报告不一致被拒绝（另一 PR 不可混入）', () => {
    const input = goodInput()
    input.currentPull = { ...goodPull(), head: { sha: '9'.repeat(40) } }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('pr-head-sha')
  })
  it('PR 已关闭被拒绝', () => {
    const input = goodInput()
    input.currentPull = { ...goodPull(), state: 'closed' }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('pr-state')
  })
  it('旧 run / attempt 不匹配被拒绝', () => {
    const input = goodInput()
    input.run = { ...goodRun(), id: 99999 }
    expect(receiveCiFinalState(input).status).toBe('fail')
    const input2 = goodInput()
    input2.run = { ...goodRun(), run_attempt: 2 }
    const result2 = receiveCiFinalState(input2)
    expect(result2.status).toBe('fail')
    expect(result2.errors.join('\n')).toContain('attempt')
  })
  it('run 未结束或非 success 被拒绝', () => {
    const input = goodInput()
    input.run = { ...goodRun(), status: 'in_progress', conclusion: null }
    expect(receiveCiFinalState(input).status).toBe('fail')
    const input2 = goodInput()
    input2.run = { ...goodRun(), conclusion: 'failure' }
    const result2 = receiveCiFinalState(input2)
    expect(result2.status).toBe('fail')
    expect(result2.errors.join('\n')).toContain('不是 success')
  })
  it('必需 job cancelled / missing 被拒绝', () => {
    const input = goodInput()
    input.jobsPayload = {
      jobs: (goodJobs().jobs ?? []).map((job) =>
        job.name === 'Quality' ? { ...job, conclusion: 'cancelled' } : job,
      ),
    }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('cancelled')
    const input2 = goodInput()
    input2.jobsPayload = { jobs: (goodJobs().jobs ?? []).filter((job) => job.name !== 'Quality') }
    const result2 = receiveCiFinalState(input2)
    expect(result2.status).toBe('fail')
    expect(result2.errors.join('\n')).toContain('缺失')
  })
  it('必需 job 缺 run_attempt 归属被拒绝（须用 attempts/:n/jobs 数据）', () => {
    const input = goodInput()
    input.jobsPayload = {
      jobs: (goodJobs().jobs ?? []).map((job) => ({ ...job, run_attempt: undefined })),
    }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('run_attempt 归属')
  })
  it('同名重复 job（冒名）被拒绝', () => {
    const input = goodInput()
    const jobs = goodJobs().jobs ?? []
    input.jobsPayload = { jobs: [...jobs, { ...jobs[0], conclusion: 'success' }] }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('同名条目')
  })
  it('artifact 缺失 / 过期 / digest 不一致被拒绝', () => {
    const input = goodInput()
    input.artifactsPayload = { artifacts: [] }
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('artifact 缺失')
    const input2 = goodInput()
    input2.artifactsPayload = {
      artifacts: [{ ...(goodArtifacts().artifacts ?? [])[0], expired: true }],
    }
    const result2 = receiveCiFinalState(input2)
    expect(result2.status).toBe('fail')
    expect(result2.errors.join('\n')).toContain('过期')
    const input3 = goodInput()
    input3.report = goodReport({
      ci: {
        ...goodReport().ci,
        expectedArtifactDigests: { 'verify-candidate-evidence': '1'.repeat(64) },
      },
    })
    const result3 = receiveCiFinalState(input3)
    expect(result3.status).toBe('fail')
    expect(result3.errors.join('\n')).toContain('digest')
  })
  it('local-fixture 证据源永不构成通过', () => {
    const input = goodInput()
    input.evidenceSource = 'local-fixture'
    input.fetchManifest = null
    const result = receiveCiFinalState(input)
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('fixture')
  })
})
