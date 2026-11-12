#!/usr/bin/env node
// verify-candidate：分级审查候选机械核验 CLI（报告模式）。
// 只做机械一致性：Git 真实对象、完整 SHA、merge tuple、政策/清单/manifest 绑定、
// 逐变更分级。fail/unknown 不可充当 pass；needs_triage 是合法分类结果而非失败。
// 本脚本不证明语义无变、FR 完成或运行验收充分，也不在运行中声明任何 CI 已成功。
// 信任链说明：政策从 base 树读取；校验器自身的来源由 --verifier-provenance 记录，
// 终态接收只接受 base-tree 来源的报告（CI 由工作流从基线树提取脚本运行）。
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname } from 'node:path'
import { argv, cwd, env } from 'node:process'
import {
  assertFullSha,
  assertObjectType,
  blobBytes,
  blobExistsAt,
  blobTextAt,
  commitInfo,
  diffTreeChanges,
  gitIgnoreableWhitespace,
  rangeDiffRaw,
  treeManifest,
} from './lib/candidate-git.mjs'
import {
  isTestCodePath,
  isTestSupportPath,
  parsePolicyText,
  provenLineEndingOnly,
  sha256Hex,
} from './lib/review-policy.mjs'
import {
  applyTriageDecisions,
  classifyCandidate,
  dependencyChanges,
  lockMatchesManifest,
  lockVersionDelta,
} from './lib/classify.mjs'
import { parseConflictsEvidence, parseRangeDiff } from './lib/range-diff.mjs'
import { verifySourceChecklist } from './lib/checklist.mjs'

const POLICY_PATH = '.github/review-policy.yml'
const CHECKLIST_ORIGINAL = 'docs/checklists/user-review-checklist-20261024.txt'
const CHECKLIST_INDEX = 'docs/checklists/source-checklist-index.json'
const EXPECTED_ARTIFACT_NAMES = ['verify-candidate-evidence']

class VerificationError extends Error {}

function parseCliArgs(argvList) {
  const parsed = {}
  for (let i = 0; i < argvList.length; i++) {
    const arg = argvList[i]
    if (!arg.startsWith('--')) {
      throw new VerificationError(`无法识别的参数：${arg}`)
    }
    const key = arg.slice(2)
    const value = argvList[i + 1]
    if (value === undefined || value.startsWith('--')) {
      throw new VerificationError(`参数 --${key} 缺少取值`)
    }
    parsed[key] = value
    i++
  }
  return parsed
}

function prNumberFromRef(ref) {
  const match = /^refs\/pull\/(\d+)\/merge$/.exec(ref ?? '')
  return match ? Number(match[1]) : null
}

// GITHUB_WORKFLOW_REF 形如 owner/repo/.github/workflows/ci.yml@refs/...，
// 需要剥掉 owner/repo 前缀才能在工作树内定位工作流文件（W05）。
function workflowRefPath(value) {
  const at = value.indexOf('@')
  const raw = (at === -1 ? value : value.slice(0, at)).replace(/^\/+/, '')
  const segments = raw.split('/')
  const githubIndex = segments.indexOf('.github')
  return githubIndex >= 0 ? segments.slice(githubIndex).join('/') : raw
}

function textOrNull(bytes) {
  if (bytes === null || bytes === undefined) return null
  if (bytes.includes(0)) return null
  return new TextDecoder('utf8', { fatal: false }).decode(bytes)
}

function main() {
  const args = parseCliArgs(argv.slice(2))
  const errors = []
  const checks = []

  const repoDir = args['repo-dir'] ?? cwd()
  const base = assertFullSha('--base', args.base)
  const head = assertFullSha('--head', args.head)
  const checkoutInput = args.checkout ?? env.GITHUB_SHA ?? head
  const checkout = assertFullSha('--checkout', checkoutInput)
  const event = args.event ?? env.GITHUB_EVENT_NAME ?? 'local'
  if (!['pull_request', 'push', 'workflow_dispatch', 'local'].includes(event)) {
    throw new VerificationError(`--event 取值非法：${event}`)
  }
  const prNumber =
    args.pr !== undefined
      ? /^\d+$/.test(args.pr)
        ? Number(args.pr)
        : null
      : (prNumberFromRef(env.GITHUB_REF) ?? null)
  if (args.pr !== undefined && prNumber === null) {
    throw new VerificationError(`--pr 必须是数字：${args.pr}`)
  }
  const repository = args.repo ?? env.GITHUB_REPOSITORY ?? 'local/unset'
  const runId = args['run-id'] ?? env.GITHUB_RUN_ID ?? null
  const runAttempt = args['run-attempt'] ?? env.GITHUB_RUN_ATTEMPT ?? null
  const workflowPathRaw = args['workflow-path'] ?? env.GITHUB_WORKFLOW_REF ?? null
  const workflowPath = workflowPathRaw ? workflowRefPath(workflowPathRaw) : null

  const fail = (message) => errors.push(message)
  const record = (name, expected, actual, pass) => checks.push({ name, expected, actual, pass })

  // ---- Git 对象存在性 ----
  for (const [label, sha] of [
    ['base', base],
    ['head', head],
    ['checkout', checkout],
  ]) {
    try {
      assertObjectType(repoDir, sha, 'commit', label)
      record(`object:${label}`, 'commit', 'commit', true)
    } catch (error) {
      record(`object:${label}`, 'commit', 'missing/other', false)
      fail(error.message)
    }
  }
  if (errors.length > 0) {
    emitReport({ report: minimalFailReport({ errors, checks }), args })
    process.exit(1)
  }

  const headInfo = commitInfo(repoDir, head)
  const checkoutInfo = commitInfo(repoDir, checkout)

  // ---- merge tuple：CI 验证的合并树必须对应当前 base/head ----
  if (event === 'pull_request') {
    const ok =
      checkoutInfo.parents.length === 2 &&
      checkoutInfo.parents[0] === base &&
      checkoutInfo.parents[1] === head
    record('merge-tuple', `${base}+${head}`, checkoutInfo.parents.join('+'), ok)
    if (!ok) {
      fail(
        `pull_request 事件的 checkout 必须是 base+head 的合并提交，实际父提交为 ${checkoutInfo.parents.join('+')}`,
      )
    }
    // 独立事件来源核对（W05）：merge 父提交必须与事件 JSON 提供的 base/head 一致。
    if (args['expect-pr-head']) {
      const expectPrHead = assertFullSha('--expect-pr-head', args['expect-pr-head'])
      const okHead = checkoutInfo.parents[1] === expectPrHead
      record('expect-pr-head', expectPrHead, checkoutInfo.parents[1], okHead)
      if (!okHead) fail('事件提供的 PR head 与 merge tuple 第二父不一致')
    }
    if (args['expect-base']) {
      const expectBase = assertFullSha('--expect-base', args['expect-base'])
      const okBase = checkoutInfo.parents[0] === expectBase
      record('expect-base', expectBase, checkoutInfo.parents[0], okBase)
      if (!okBase) fail('事件提供的目标 base 与 merge tuple 第一父不一致')
    }
  } else {
    const ok = checkout === head
    record('merge-tuple', head, checkout, ok)
    if (!ok) fail(`非 PR 事件的 checkout 必须等于 head：${checkout} != ${head}`)
  }

  // ---- 可信政策：从 base 读取；候选政策仅作为待审对象，不得自我降级 ----
  let trustedPolicy = null
  let trustedPolicyBytes = null
  let bootstrap = { untrusted: false, reason: null }
  if (blobExistsAt(repoDir, base, POLICY_PATH)) {
    trustedPolicyBytes = blobTextAt(repoDir, base, POLICY_PATH)
    trustedPolicy = parsePolicyText(
      new TextDecoder().decode(trustedPolicyBytes),
      `base:${POLICY_PATH}`,
    )
  }
  const candidatePolicyBytes = blobTextAt(repoDir, head, POLICY_PATH)
  let candidatePolicy = null
  if (candidatePolicyBytes !== null) {
    try {
      candidatePolicy = parsePolicyText(
        new TextDecoder().decode(candidatePolicyBytes),
        `head:${POLICY_PATH}`,
      )
    } catch (error) {
      fail(error.message)
    }
  }
  const trustedPolicySha256 = trustedPolicyBytes ? sha256Hex(trustedPolicyBytes) : null
  const candidatePolicyChanged =
    candidatePolicyBytes !== null &&
    (trustedPolicyBytes === null || !candidatePolicyBytes.equals(trustedPolicyBytes))

  let classifyPolicy = trustedPolicy
  if (!trustedPolicy) {
    if (!candidatePolicy) {
      fail(`base 与 head 都没有 ${POLICY_PATH}，无法分级`)
      emitReport({ report: minimalFailReport({ errors, checks }), args })
      process.exit(1)
    }
    bootstrap = {
      untrusted: true,
      reason:
        'base 无可信政策（首次部署）：分类使用候选自身政策，结论是 untrusted_bootstrap，不能自证达到任何门禁；终态接收将拒绝本报告',
    }
    classifyPolicy = candidatePolicy
    record('trusted-policy', 'present-in-base', 'absent-in-bootstrap', false)
  } else {
    record('trusted-policy', 'parsed-from-base', 'parsed-from-base', true)
  }

  // ---- 变更清单与证据（全部来自 Git 对象，不从可变工作区读取）----
  const changes = diffTreeChanges(repoDir, base, head)
  for (const change of changes) {
    change.beforeBytes = blobBytes(repoDir, change.oldBlobSha)
    change.afterBytes = blobBytes(repoDir, change.newBlobSha)
    change.gitIgnoreableWhitespace = gitIgnoreableWhitespace(repoDir, base, head, change.path)
    // W11：非功能证明仅对"修改型 + 模式不变 + 双侧文本"计算；二进制 CRLF 或
    // 可执行位变化都不构成纯行尾格式变更。
    const eligibleForProof =
      change.status === 'M' &&
      change.oldMode === change.newMode &&
      change.beforeBytes !== null &&
      change.afterBytes !== null &&
      !change.beforeBytes.includes(0) &&
      !change.afterBytes.includes(0)
    change.provenFormat = eligibleForProof
      ? provenLineEndingOnly(change.beforeBytes, change.afterBytes)
      : {
          proven: false,
          reason:
            change.status !== 'M'
              ? 'not-a-modification'
              : change.oldMode !== change.newMode
                ? 'mode-change'
                : 'binary-content',
        }
  }

  // ---- 依赖与锁文件上下文（W06）----
  const manifestDeps = []
  for (const change of changes) {
    if (!change.path.endsWith('package.json')) continue
    const beforeText = textOrNull(change.beforeBytes)
    const afterText = textOrNull(change.afterBytes)
    const deps = dependencyChanges(beforeText, afterText)
    if (deps) manifestDeps.push(...deps)
  }
  let lockDelta = null
  for (const change of changes) {
    if (change.path !== 'package-lock.json') continue
    lockDelta = lockVersionDelta(textOrNull(change.beforeBytes), textOrNull(change.afterBytes))
  }
  const lockMatches =
    lockDelta !== null && manifestDeps.length > 0
      ? lockMatchesManifest(lockDelta, manifestDeps)
      : false
  let dependencyBumpLevel = null
  let dependencyBumpReason = null
  if (manifestDeps.length > 0) {
    if (manifestDeps.some((entry) => entry.bump === 'major')) dependencyBumpLevel = 'L2'
    else if (
      manifestDeps.some(
        (entry) =>
          entry.bump === 'unparseable' || entry.bump === 'added' || entry.bump === 'removed',
      )
    )
      dependencyBumpLevel = 'needs_triage'
    else if (manifestDeps.some((entry) => entry.bump === 'minor')) dependencyBumpLevel = 'L1'
    else if (
      manifestDeps.every((entry) => entry.bump === 'patch' || entry.bump === 'specifier-only') &&
      manifestDeps.every((entry) => entry.section === 'devDependencies')
    )
      dependencyBumpLevel = 'L0'
    else dependencyBumpLevel = 'needs_triage'
    dependencyBumpReason = manifestDeps
      .map((entry) => `${entry.name}:${entry.section}:${entry.bump}`)
      .join(',')
  }
  record(
    'lock-manifest-consistency',
    'consistent-or-absent',
    lockDelta === null ? 'no-lock-change' : String(lockMatches),
    lockDelta === null || lockMatches,
  )

  // ---- 可信声明（W12：FR 结算/发布候选身份来自声明输入，不靠文件名猜测）----
  let declaration = null
  if (args['candidate-declaration']) {
    let doc = null
    try {
      doc = JSON.parse(readFileSync(args['candidate-declaration'], 'utf8'))
    } catch (error) {
      fail(`候选声明文件读取/解析失败：${error.message}`)
    }
    if (doc) {
      const bindingOk = doc.binding?.candidateHeadSha === head
      record(
        'declaration-binding',
        'candidate-head-bound',
        bindingOk ? '匹配' : '不匹配',
        bindingOk,
      )
      if (!bindingOk) {
        fail('候选声明文件未绑定当前 head，拒收')
      } else if (
        doc.schemaVersion !== 1 ||
        typeof doc.declaredBy !== 'string' ||
        doc.declaredBy.trim() === '' ||
        typeof doc.isFrSettlement !== 'boolean' ||
        typeof doc.isReleaseCandidate !== 'boolean'
      ) {
        fail('候选声明 schema 不完整（schemaVersion/declaredBy/isFrSettlement/isReleaseCandidate）')
      } else {
        declaration = {
          isFrSettlement: doc.isFrSettlement,
          isReleaseCandidate: doc.isReleaseCandidate,
          declaredBy: doc.declaredBy,
          provenance: 'controller-declared',
        }
      }
    }
  }

  const ctx = {
    policy: classifyPolicy,
    testsOnlyCandidate:
      changes.length > 0 &&
      changes.every((change) => isTestCodePath(change.path) || isTestSupportPath(change.path)),
    lockMatchesManifest: lockMatches,
    dependencyBumpLevel,
    dependencyBumpReason,
    declaration,
  }
  let classification = classifyCandidate(changes, ctx)

  // ---- 可信人工决策：policy/head 双重绑定后才可用（W07 schema 强化）----
  if (args['triage-decisions']) {
    let decisionDoc = null
    try {
      decisionDoc = JSON.parse(readFileSync(args['triage-decisions'], 'utf8'))
    } catch (error) {
      fail(`人工决策文件读取/解析失败：${error.message}`)
    }
    if (decisionDoc) {
      const bindingPolicySha =
        trustedPolicySha256 ?? (candidatePolicyBytes ? sha256Hex(candidatePolicyBytes) : null)
      const bindingOk =
        decisionDoc.binding?.policySha256 === bindingPolicySha &&
        decisionDoc.binding?.candidateHeadSha === head
      record('triage-binding', 'policy+head 双绑定匹配', bindingOk ? '匹配' : '不匹配', bindingOk)
      if (!bindingOk) {
        fail('人工决策文件与当前政策版本或候选 head 不绑定，拒收')
      } else if (
        !decisionDoc.decidedBy ||
        decisionDoc.decidedBy.trim() === '' ||
        !Array.isArray(decisionDoc.decisions)
      ) {
        fail('人工决策文件缺少 decidedBy 或 decisions')
      } else {
        classification = applyTriageDecisions(classification, decisionDoc.decisions, changes, ctx)
        for (const error of classification.errors ?? []) fail(`人工决策错误：${error}`)
      }
    }
  }

  // ---- 清单三件套完整性（原文锚点 + 原文提取逐位核对，W10）----
  let sourceChecklist = { status: 'absent', summary: null, changed: false }
  const checklistChanged = changes.some((change) => change.path.startsWith('docs/checklists/'))
  if (
    blobExistsAt(repoDir, head, CHECKLIST_ORIGINAL) &&
    blobExistsAt(repoDir, head, CHECKLIST_INDEX)
  ) {
    const original = blobTextAt(repoDir, head, CHECKLIST_ORIGINAL)
    const index = blobTextAt(repoDir, head, CHECKLIST_INDEX)
    const result = verifySourceChecklist(original, index)
    sourceChecklist = {
      status: result.status,
      summary: result.summary,
      changed: checklistChanged,
      checks: result.checks,
    }
    for (const check of result.checks)
      if (!check.pass) record(`checklist:${check.name}`, check.expected, check.actual, false)
    for (const error of result.errors) fail(`清单校验：${error}`)
  } else if (blobExistsAt(repoDir, base, CHECKLIST_ORIGINAL)) {
    sourceChecklist = { status: 'missing-in-head', summary: null, changed: true }
    fail('候选删除了仓内原始清单（docs/checklists），政策证据链不完整')
  }

  // ---- 候选 manifest：head tree 全量清单，不循环 hash 自身 ----
  const headTreeManifest = treeManifest(repoDir, headInfo.tree)
  const headPayload = JSON.stringify({
    tree: headTreeManifest.tree,
    files: headTreeManifest.files.map((f) => ({ path: f.path, mode: f.mode, sha: f.sha })),
  })
  const manifest = {
    status: 'pass',
    fileCount: headTreeManifest.files.length,
    sha256: sha256Hex(headPayload),
    tree: headInfo.tree,
  }
  if (args['expect-manifest']) {
    let expected = null
    try {
      expected = JSON.parse(readFileSync(args['expect-manifest'], 'utf8'))
    } catch (error) {
      fail(`expect-manifest 读取失败：${error.message}`)
    }
    if (expected) {
      const match = expected.sha256 === manifest.sha256 && expected.tree === manifest.tree
      record('manifest', manifest.sha256, expected.sha256, match)
      if (!match) {
        manifest.status = 'fail'
        fail('候选 manifest 与期望不一致（树内容或文件集合变化）')
      }
    }
  }

  // ---- range-diff 与冲突证据（W02：保存原始输出，解析单侧条目；冲突只认附带证据）----
  const comparison = {
    previousBase: null,
    previousHead: null,
    rangeDiffStatus: null,
    patchUnchanged: null,
    conflicts: 'unknown',
    conflictsSource: null,
    rawSavedTo: null,
  }
  if (args['previous-base'] || args['previous-head']) {
    const previousBase = assertFullSha('--previous-base', args['previous-base'])
    const previousHead = assertFullSha('--previous-head', args['previous-head'])
    comparison.previousBase = previousBase
    comparison.previousHead = previousHead
    const raw = rangeDiffRaw(repoDir, previousBase, previousHead, base, head)
    const parsed = parseRangeDiff(raw)
    comparison.rangeDiffStatus = parsed.status
    comparison.patchUnchanged = parsed.patchUnchanged
    if (parsed.reason) comparison.rangeDiffReason = parsed.reason
    record('range-diff', 'entries-parsed', parsed.status, parsed.status !== 'unknown')
    if (args['artifact-dir']) {
      mkdirSync(args['artifact-dir'], { recursive: true })
      const rawPath = `${args['artifact-dir'].replace(/\/$/, '')}/range-diff.txt`
      writeFileSync(rawPath, raw)
      comparison.rawSavedTo = rawPath
    }
  }
  if (args['conflicts-file']) {
    let doc = null
    try {
      doc = JSON.parse(readFileSync(args['conflicts-file'], 'utf8'))
    } catch (error) {
      fail(`冲突证据文件读取/解析失败：${error.message}`)
    }
    if (doc) {
      const parsed = parseConflictsEvidence(doc)
      comparison.conflicts = parsed.status
      comparison.conflictsSource = parsed.source ?? parsed.reason ?? null
    }
  }
  if (comparison.conflicts === 'unknown') {
    record('conflict-proof', 'attached-evidence', 'unknown', false)
  }

  // ---- 校验器来源（W03）：由调用环境记录，终态接收只接受 base-tree ----
  let verifierProvenance = { source: 'local-worktree', files: [] }
  if (args['verifier-provenance']) {
    try {
      verifierProvenance = JSON.parse(readFileSync(args['verifier-provenance'], 'utf8'))
    } catch (error) {
      fail(`verifier-provenance 读取失败：${error.message}`)
      verifierProvenance = { source: 'invalid', files: [], error: error.message }
    }
  }

  // ---- workflow 文件身份（从 checkout 对象读取字节并求 hash）----
  let workflowSha256 = null
  if (workflowPath) {
    const workflowBytes = blobTextAt(repoDir, checkout, workflowPath)
    if (workflowBytes !== null) workflowSha256 = sha256Hex(workflowBytes)
  }

  const report = buildReport({
    repository,
    prNumber,
    base,
    head,
    headInfo,
    checkout,
    checkoutInfo,
    trustedPolicySha256,
    candidatePolicyChanged,
    bootstrap,
    policy: classifyPolicy,
    event,
    runId,
    runAttempt,
    workflowPath,
    workflowSha256,
    verifierProvenance,
    declaration,
    classification,
    manifest,
    sourceChecklist,
    comparison,
    errors,
    checks,
  })
  emitReport({ report, args })
  process.exit(errors.length === 0 ? 0 : 1)
}

function minimalFailReport({ errors, checks }) {
  return {
    schemaVersion: 1,
    status: 'fail',
    mode: 'report_only',
    checks,
    errors,
    note: '机械校验在早期阶段失败，候选身份字段不完整，不可作为任何放行依据',
  }
}

function buildReport(input) {
  return {
    schemaVersion: 1,
    status: input.errors.length === 0 ? 'pass' : 'fail',
    mode: 'report_only',
    bootstrap: input.bootstrap,
    repository: input.repository,
    pullRequestNumber: input.prNumber,
    targetBaseSha: input.base,
    prHeadSha: input.head,
    prHeadTree: input.headInfo.tree,
    ciCheckoutSha: input.checkout,
    ciCheckoutTree: input.checkoutInfo.tree,
    trustedPolicySha256: input.trustedPolicySha256,
    candidatePolicyChanged: input.candidatePolicyChanged,
    policyActivation: {
      status: input.policy.status,
      enforced: input.policy.activation?.enforced === true,
      startsWith: input.policy.activation?.starts_with ?? null,
      legacyGate: input.policy.activation?.legacy_gate ?? [],
    },
    verifierProvenance: input.verifierProvenance,
    declaration: input.declaration,
    ci: {
      event: input.event,
      runId: input.runId,
      runAttempt: input.runAttempt,
      workflowPath: input.workflowPath,
      workflowSha256: input.workflowSha256,
      expectedArtifactNames: EXPECTED_ARTIFACT_NAMES,
      requiredJobs: (input.policy.validation?.full_ci ?? []).map((name) => ({
        name,
        jobId: null,
        conclusion: 'unknown',
        note: '候选 job 运行中无法证明自身与后续 job 的终态，须由 receive-ci-final-state 以官方 run/attempt 数据补齐',
      })),
      artifacts: [],
      finalStateReceived: false,
    },
    classification: {
      level: input.classification.level,
      provisionalLevel: input.classification.provisionalLevel,
      reasons: input.classification.reasons,
      flags: input.classification.flags,
      pendingTriage: input.classification.pendingTriage?.map((entry) => ({
        path: entry.path,
        reasons: entry.reasons,
      })),
      pendingSemanticReview: input.classification.pendingSemanticReview?.map((entry) => ({
        path: entry.path,
        note: 'path-hint 型 L2：可由可信人工决策按非核心引擎单模块例外等理由定级',
      })),
      perChange: input.classification.perChange,
    },
    manifest: input.manifest,
    sourceChecklist: input.sourceChecklist,
    comparison: input.comparison,
    checks: input.checks,
    errors: input.errors,
  }
}

function emitReport({ report, args }) {
  const json = JSON.stringify(report, null, 2)
  if (args.output) {
    mkdirSync(dirname(args.output), { recursive: true })
    writeFileSync(args.output, json + '\n')
  } else {
    process.stdout.write(json + '\n')
  }
  if (args['summary-file']) {
    writeFileSync(args['summary-file'], renderSummary(report), { flag: 'a' })
  }
  process.stderr.write(
    `verify-candidate: status=${report.status} level=${report.classification?.level ?? 'n/a'} errors=${report.errors.length}\n`,
  )
}

function renderSummary(report) {
  const lines = [
    '## verify-candidate（报告模式）',
    '',
    `- status: ${report.status}`,
    `- base: ${report.targetBaseSha}`,
    `- head: ${report.prHeadSha} (tree ${report.prHeadTree})`,
    `- checkout: ${report.ciCheckoutSha} (tree ${report.ciCheckoutTree})`,
    `- 分级: ${report.classification.level}${report.classification.provisionalLevel ? `（provisional ${report.classification.provisionalLevel}）` : ''}`,
    `- 政策: trusted=${report.trustedPolicySha256 ?? 'untrusted-bootstrap'} candidateChanged=${report.candidatePolicyChanged} enforced=${report.policyActivation.enforced}`,
    `- 校验器来源: ${report.verifierProvenance?.source ?? 'unknown'}（终态接收只接受 base-tree）`,
    `- 清单: ${report.sourceChecklist.status}（${report.sourceChecklist.summary?.total ?? '-'} 条）`,
    `- manifest: ${report.manifest.sha256}（${report.manifest.fileCount} 文件）`,
  ]
  if (report.classification.pendingTriage?.length) {
    lines.push('', '### 待人工分级（needs_triage）')
    for (const entry of report.classification.pendingTriage) lines.push(`- \`${entry.path}\``)
  }
  if (report.classification.pendingSemanticReview?.length) {
    lines.push('', '### 路径提示型 L2（可信决策可定级）')
    for (const entry of report.classification.pendingSemanticReview)
      lines.push(`- \`${entry.path}\``)
  }
  if (report.errors.length) {
    lines.push('', '### 错误')
    for (const error of report.errors) lines.push(`- ${error}`)
  }
  return lines.join('\n') + '\n'
}

try {
  main()
} catch (error) {
  const payload = {
    schemaVersion: 1,
    status: 'unknown',
    mode: 'report_only',
    errors: [error.message],
    note: '意外异常：不作为 pass；请保留现场并核查输入',
  }
  process.stderr.write(JSON.stringify(payload, null, 2) + '\n')
  process.exit(2)
}
