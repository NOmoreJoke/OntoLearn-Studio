import {
  hintsFor,
  highestHint,
  isGovernancePath,
  isStatusDocument,
  isTestCodePath,
  isTestSupportPath,
  matchPathHint,
} from './review-policy.mjs'

const LEVEL_RANK = { L0: 0, L1: 1, L2: 2 }
const DEP_SECTIONS = ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies']
const IPC_MARKERS =
  /(contextBridge|ipcRenderer|window\.ontolearn|window\.api|\.invoke\(|exposeInMainWorld|webContents\.send|postMessage)/
const ASSERTION_MARKERS =
  /(expect\s*\(|\bassert\b|\.toBe|\.toEqual|\.to(Throw|Reject|Contain|HaveLength)|pytest\.raises|\.should\(|assertEquals|fail\()/
const COMPLETION_MARKERS =
  /(已完成|已通过|验收通过|已验收|发布候选|release candidate|\bdone\b|\bpassed\b|\bcompleted\b)/
const GATE_KEYWORDS = /(门禁|审查|双审|verify-candidate|required|合并条件|full_ci|merge_requires)/
const OUTER_COMPLETION_RE =
  /(?:FR[-‑ ]?\d+|I0?\d+|S\d+|C\d+|B\d+|U\d+)[^\n]{0,60}(完成|验收|通过)|发布候选|release candidate|里程碑[^\n]{0,20}完成/
const TAUTOLOGY_RE =
  /assert True\b|expect\(true\)\.toBe\(true\)|expect\(1\)\.toBe\(1\)|expect\.anything\(\)|assert ok\b/

function textOrNull(bytes) {
  if (bytes === null || bytes === undefined) return null
  if (bytes.includes(0)) return null
  return new TextDecoder('utf8', { fatal: false }).decode(bytes)
}

function splitLines(text) {
  return text === null ? [] : text.split(/\r\n|\r|\n/)
}

// 多重集合差：新增行与删除行（按内容计数，不依赖 patch 解析）。
export function lineDelta(beforeText, afterText) {
  const before = splitLines(beforeText)
  const after = splitLines(afterText)
  const beforeCount = new Map()
  for (const line of before) beforeCount.set(line, (beforeCount.get(line) ?? 0) + 1)
  const added = []
  for (const line of after) {
    const count = beforeCount.get(line) ?? 0
    if (count > 0) beforeCount.set(line, count - 1)
    else added.push(line)
  }
  const afterCount = new Map()
  for (const line of after) afterCount.set(line, (afterCount.get(line) ?? 0) + 1)
  const removed = []
  for (const line of before) {
    const count = afterCount.get(line) ?? 0
    if (count > 0) afterCount.set(line, count - 1)
    else removed.push(line)
  }
  return { added, removed }
}

function parseJson(text) {
  if (text === null || text === undefined) return null
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

// 严格版本解析：整个 spec 必须是可选范围前缀 + 语义化版本；workspace/file/git/tag
// 等其它形态返回 null，由调用方保守处理（不把含版本号的任意字符串当 semver）。
export function semverOf(spec) {
  if (typeof spec !== 'string') return null
  const match = /^[\^~>=<|= ]*v?(\d+)\.(\d+)\.(\d+)(?:[-+][0-9A-Za-z.-]+)?$/.exec(spec.trim())
  if (!match) return null
  return { major: Number(match[1]), minor: Number(match[2]), patch: Number(match[3]) }
}

function bumpOf(from, to) {
  if (from === null || to === null) return 'unparseable'
  if (from.major !== to.major) return 'major'
  if (from.minor !== to.minor) return 'minor'
  if (from.patch !== to.patch) return 'patch'
  return 'specifier-only'
}

// 依赖区变更分析。major 不论 dev/prod 都是 L2 语义风险；无法解析的版本保守处理。
export function dependencyChanges(beforeText, afterText) {
  const before = parseJson(beforeText)
  const after = parseJson(afterText)
  if (!before || !after) return null
  const changes = []
  for (const section of DEP_SECTIONS) {
    const beforeDeps = before[section] ?? {}
    const afterDeps = after[section] ?? {}
    for (const name of new Set([...Object.keys(beforeDeps), ...Object.keys(afterDeps)])) {
      const from = beforeDeps[name]
      const to = afterDeps[name]
      if (from === to) continue
      if (from === undefined) {
        changes.push({ name, section, from: null, to, bump: 'added' })
        continue
      }
      if (to === undefined) {
        changes.push({ name, section, from, to: null, bump: 'removed' })
        continue
      }
      changes.push({ name, section, from, to, bump: bumpOf(semverOf(from), semverOf(to)) })
    }
  }
  return changes
}

// 依赖区之外的全部 manifest 字段对比（scripts/build/engines/overrides/任意键）。
// 依赖补丁例外只在非依赖字段完全未变时成立（W06）。
export function manifestNonDependencyChanges(beforeText, afterText) {
  const before = parseJson(beforeText)
  const after = parseJson(afterText)
  if (!before || !after) return null
  const changed = []
  for (const key of new Set([...Object.keys(before), ...Object.keys(after)])) {
    if (DEP_SECTIONS.includes(key)) continue
    if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) changed.push(key)
  }
  return changed
}

// package-lock 实际差异：按 packages 路径收集版本变化（W06：锁文件不再只看
// "manifest 有 bump"就继承等级，必须自身差异与 manifest bump 一致）。
export function lockVersionDelta(beforeText, afterText) {
  const before = parseJson(beforeText)
  const after = parseJson(afterText)
  if (!before || !after) return null
  const collect = (lock) => {
    const map = new Map()
    for (const [pkgPath, entry] of Object.entries(lock.packages ?? {})) {
      if (entry && typeof entry.version === 'string') map.set(pkgPath || '<root>', entry.version)
    }
    return map
  }
  const beforeMap = collect(before)
  const afterMap = collect(after)
  const delta = { added: [], removed: [], changed: [] }
  for (const [name, to] of afterMap) {
    const from = beforeMap.get(name)
    if (from === undefined) delta.added.push(name)
    else if (from !== to) delta.changed.push({ name, from, to })
  }
  for (const name of beforeMap.keys()) if (!afterMap.has(name)) delta.removed.push(name)
  return delta
}

export function lockMatchesManifest(lockDelta, depChanges) {
  if (!lockDelta || !depChanges) return false
  const consumed = new Set()
  for (const change of depChanges) {
    const match = lockDelta.changed.find((entry) => {
      const path = entry.name === '' || entry.name === '<root>' ? change.name : entry.name
      return (
        (path === change.name || path.endsWith(`/${change.name}`)) &&
        bumpOf(semverOf(entry.from), semverOf(entry.to)) === change.bump
      )
    })
    if (match) consumed.add(match.name)
  }
  const extraChanged = lockDelta.changed.filter((entry) => !consumed.has(entry.name))
  return extraChanged.length === 0 && lockDelta.added.length === 0 && lockDelta.removed.length === 0
}

export function completionClaim(beforeText, afterText) {
  const checkboxCount = (text) => (text === null ? 0 : (text.match(/\[x\]|\[X\]/g) ?? []).length)
  if (checkboxCount(afterText) > checkboxCount(beforeText)) {
    return { claimed: true, evidence: 'checkbox-completion-increased' }
  }
  const { added } = lineDelta(beforeText, afterText)
  if (added.some((line) => COMPLETION_MARKERS.test(line))) {
    return { claimed: true, evidence: 'new-completion-marker-line' }
  }
  return { claimed: false }
}

// 普通文档中的完成声明（W12）：不能仅靠文件名证明"不是结算"，检测到时转
// needs_triage，由可信声明/裁定确认范围，不得自动按 L0 放行。
export function completionClaimOutsideStatusDocument(beforeText, afterText) {
  const { added } = lineDelta(beforeText, afterText)
  const hit = added.find((line) => OUTER_COMPLETION_RE.test(line))
  if (hit) return { claimed: true, evidence: hit.trim().slice(0, 120) }
  return { claimed: false }
}

// 恒真断言嫌疑（W08）：真实断言被替换为恒真形式时数量不变也会被识别。
export function tautologySuspicion(beforeText, afterText) {
  const { added, removed } = lineDelta(beforeText, afterText)
  const addedTautology = added.some((line) => TAUTOLOGY_RE.test(line))
  const removedReal = removed.some((line) => ASSERTION_MARKERS.test(line))
  return addedTautology && removedReal
}

// workflow 变更分档（W08）：pin 升级是常见低风险操作；禁用条件与内容性变更
// 不能靠"没匹配到削弱关键词"证明安全。
export function workflowChangeKind(beforeText, afterText) {
  const { added, removed } = lineDelta(beforeText, afterText)
  const touched = [...added, ...removed].filter((line) => line.trim() !== '')
  const beforeHas = (re) => new RegExp(re).test(beforeText ?? '')
  const afterHas = (re) => new RegExp(re).test(afterText ?? '')
  if (
    (afterHas('if:\\s*false\\b') && !beforeHas('if:\\s*false\\b')) ||
    (afterHas('continue-on-error:\\s*true\\b') && !beforeHas('continue-on-error:\\s*true\\b'))
  ) {
    return 'job-disabling-condition'
  }
  if (touched.length > 0 && touched.every((line) => /^\s*-?\s*uses:\s+\S+@\S+/.test(line))) {
    return 'actions-pin-only'
  }
  return 'content-change'
}

// 门禁削弱检测：结构性字段对比（政策）、job/关键步骤/禁用条件（CI）。
// 这是"检出削弱"，与"未检出即安全"相反：未检出的 workflow 内容变更仍走 needs_triage。
export function gateWeakening(path, beforeText, afterText) {
  if (path.startsWith('.github/workflows/')) {
    if (workflowChangeKind(beforeText, afterText) === 'job-disabling-condition') {
      return { weakened: true, evidence: 'job-disabling-condition-introduced' }
    }
    const jobNames = (text) =>
      text === null ? [] : [...text.matchAll(/^ {2}([a-zA-Z0-9_-]+):$/gm)].map((m) => m[1])
    const requiredSteps = (text) =>
      text === null
        ? 0
        : (
            text.match(
              /npm run check|test:e2e|package:dir|verify:sources|verify-candidate|verify-i04-package/g,
            ) ?? []
          ).length
    const beforeJobs = jobNames(beforeText)
    const afterJobs = jobNames(afterText)
    const lost = beforeJobs.filter((job) => !afterJobs.includes(job))
    if (lost.length > 0) return { weakened: true, evidence: `ci-jobs-removed:${lost.join(',')}` }
    if (requiredSteps(afterText) < requiredSteps(beforeText)) {
      return { weakened: true, evidence: 'required-verification-steps-reduced' }
    }
    return { weakened: false }
  }
  if (path === '.github/review-policy.yml') {
    const before = parseJson(beforeText)
    const after = parseJson(afterText)
    if (!before || !after) return { weakened: false, unparseable: true }
    const listLen = (obj, keys) => keys.reduce((acc, key) => acc + (obj?.[key]?.length ?? 0), 0)
    if (
      listLen(after.validation ?? {}, ['full_ci']) < listLen(before.validation ?? {}, ['full_ci'])
    )
      return { weakened: true, evidence: 'required-ci-list-reduced' }
    if (
      (after.validation?.non_success_blocks?.length ?? 1) <
      (before.validation?.non_success_blocks?.length ?? 1)
    )
      return { weakened: true, evidence: 'non-success-blocks-reduced' }
    for (const level of ['L0', 'L1', 'L2']) {
      if (
        listLen(after.levels?.[level] ?? {}, ['merge_requires']) <
        listLen(before.levels?.[level] ?? {}, ['merge_requires'])
      )
        return { weakened: true, evidence: `merge-requires-reduced:${level}` }
    }
    if (listLen(after.path_hints ?? {}, ['L2']) < listLen(before.path_hints ?? {}, ['L2']))
      return { weakened: true, evidence: 'L2-path-hints-reduced' }
    if (listLen(after.semantic_rules ?? {}, ['L2']) < listLen(before.semantic_rules ?? {}, ['L2']))
      return { weakened: true, evidence: 'L2-semantic-rules-reduced' }
    if (Object.keys(after.reviewers ?? {}).length < Object.keys(before.reviewers ?? {}).length)
      return { weakened: true, evidence: 'reviewers-reduced' }
    if (
      (after.same_logical_change?.maximum_rounds ?? 2) >
      (before.same_logical_change?.maximum_rounds ?? 2)
    )
      return { weakened: true, evidence: 'maximum-rounds-increased' }
    if (
      before.same_logical_change?.rounds_count_across_candidate_renames === true &&
      after.same_logical_change?.rounds_count_across_candidate_renames !== true
    )
      return { weakened: true, evidence: 'round-count-reset-across-renames-enabled' }
    return { weakened: false }
  }
  // AGENTS / 清单文档：关键词净删除仅是嫌疑，不能自证未削弱 → needs_triage。
  if (isGovernancePath(path, { path_hints: { L2: [], L1: [], L0: [] } })) {
    const { added, removed } = lineDelta(beforeText, afterText)
    const removedGate = removed.filter((line) => GATE_KEYWORDS.test(line)).length
    const addedGate = added.filter((line) => GATE_KEYWORDS.test(line)).length
    if (removedGate > addedGate)
      return { weakened: true, evidence: 'gate-keyword-lines-net-removed' }
  }
  return { weakened: false }
}

function ipcSemanticsTouched(beforeText, afterText) {
  const { added, removed } = lineDelta(beforeText, afterText)
  return [...added, ...removed].some((line) => IPC_MARKERS.test(line))
}

function assertionWeakened(beforeText, afterText) {
  const { added, removed } = lineDelta(beforeText, afterText)
  const addedCount = added.filter((line) => ASSERTION_MARKERS.test(line)).length
  const removedCount = removed.filter((line) => ASSERTION_MARKERS.test(line)).length
  return removedCount > addedCount
}

// 敏感代码模块映射：跨模块行为（≥2 个模块被实质变更触及）在候选级强制 L2。
const SENSITIVE_MODULES = [
  ['main', ['apps/desktop/src/main/**']],
  ['preload', ['apps/desktop/src/preload/**']],
  ['csp', ['apps/desktop/src/csp.ts']],
  ['renderer', ['apps/desktop/src/renderer/**']],
  ['contracts', ['packages/contracts/**']],
  ['engine-src', ['packages/engine/src/ontolearn_engine/**']],
  ['packaging', ['build/**', '**/electron-builder.*', 'package.json', 'pyproject.toml']],
]

function sensitiveModuleOf(path) {
  for (const [module, patterns] of SENSITIVE_MODULES) {
    if (patterns.some((pattern) => matchPathHint(path, pattern))) return module
  }
  return null
}

// 防御性非功能证明（W11）：字节级 CR 判定必须同时满足修改型、模式不变、
// 两侧都是文本（无 NUL 字节）；否则证明无效。
function effectiveProvenFormat(change, beforeText, afterText) {
  if (!change.provenFormat?.proven)
    return { proven: false, reason: change.provenFormat?.reason ?? 'none' }
  if (change.status !== 'M') return { proven: false, reason: 'not-a-modification' }
  if (change.oldMode !== change.newMode) return { proven: false, reason: 'mode-change' }
  if (beforeText === null || afterText === null) return { proven: false, reason: 'binary-content' }
  return change.provenFormat
}

// 逐变更分类：严格按政策 per_change_algorithm 顺序。
// basis 区分语义证明（semantic-proof，不可被决策降级）与路径保守提示
// （path-hint，可被可信决策按"非核心引擎单模块例外"等理由定级，W09）。
export function classifyChange(change, ctx) {
  const reasons = []
  const hintLevel = highestHint(change.path, ctx.policy)
  const hints = hintsFor(change.path, ctx.policy)
  reasons.push(
    `path-hints:${hintLevel ?? 'none'}` +
      `(${Object.entries(hints)
        .filter(([, patterns]) => patterns.length > 0)
        .map(([level, patterns]) => `${level}=${patterns.length}`)
        .join(',')})`,
  )
  const beforeText = textOrNull(change.beforeBytes)
  const afterText = textOrNull(change.afterBytes)
  const provenFormat = effectiveProvenFormat(change, beforeText, afterText)
  const substantive = !provenFormat.proven
  const result = (level, basis, extraReasons, flags = {}) => ({
    path: change.path,
    status: change.status,
    level,
    basis,
    reasons: [...reasons, ...extraReasons],
    flags,
  })

  if (provenFormat.proven) {
    reasons.push(`proven-nonfunctional:${provenFormat.reason}`)
  } else if (change.provenFormat?.proven) {
    reasons.push(`nonfunctional-proof-invalidated:${provenFormat.reason}`)
  } else if (change.gitIgnoreableWhitespace && substantive) {
    reasons.push(
      'whitespace-ignorable-but-unproven:字符串内空格/缩进/注释指令可能改变行为，不自动判 L0',
    )
  }

  // 步骤 1：实际 L2 语义风险（机器可证语义），basis=semantic-proof。
  if (substantive && change.path === 'apps/desktop/src/csp.ts') {
    return result('L2', 'semantic-proof', ['csp-single-source-behavior-change'])
  }
  if (substantive && (beforeText !== null || afterText !== null)) {
    const weakening = gateWeakening(change.path, beforeText, afterText)
    if (weakening.weakened && change.path.startsWith('.github/')) {
      return result('L2', 'semantic-proof', [`weakening-required-gate:${weakening.evidence}`])
    }
    if (change.path.endsWith('package.json')) {
      const deps = dependencyChanges(beforeText, afterText)
      const nonDeps = manifestNonDependencyChanges(beforeText, afterText)
      const major = deps?.find(
        (entry) => entry.bump === 'major' || (entry.bump === 'unparseable' && entry.from !== null),
      )
      if (major) {
        const withSideEffects = nonDeps && nonDeps.length > 0
        return result('L2', 'semantic-proof', [
          `dependency-major:${major.name}:${major.section}:${major.from}->${major.to}` +
            (withSideEffects ? `+non-dependency-fields:${nonDeps.join(',')}` : ''),
        ])
      }
    }
    if (ipcSemanticsTouched(beforeText, afterText)) {
      return result('L2', 'semantic-proof', ['ipc-bridge-semantics-touched'])
    }
    if (isStatusDocument(change.path)) {
      const claim = completionClaim(beforeText, afterText)
      if (claim.claimed) {
        return result('L2', 'semantic-proof', [`fr-completion-claim:${claim.evidence}`])
      }
    }
  }

  // 步骤 2：治理改动。workflow 内容性变更不能证明未削弱 → needs_triage（W08）。
  if (change.path.startsWith('.github/workflows/')) {
    const kind = workflowChangeKind(beforeText, afterText)
    if (kind === 'actions-pin-only') {
      return result('L1', 'rule', ['governance:workflow-actions-pin-only'])
    }
    return result('needs_triage', 'rule', [
      `governance:workflow-${kind}-not-proven-safe:CI 内容变更须人工确认未削弱必需验证`,
    ])
  }
  if (isGovernancePath(change.path, ctx.policy)) {
    const weakening = gateWeakening(change.path, beforeText, afterText)
    if (weakening.weakened) {
      return result('needs_triage', 'rule', [
        `suspected-gate-weakening:${weakening.evidence}:须人工确认未实际削弱门禁`,
      ])
    }
    if (change.path === 'docs/source-manifest.json') {
      return result(
        'L1',
        'rule',
        ['governance:authority-bearing-manifest-requires-source-verification'],
        { requiresSourceVerification: true },
      )
    }
    return result('L1', 'rule', ['governance-change-minimum-L1'])
  }

  // 步骤 3：已证明非功能例外（仅字节级 CR 规范化证明）。
  if (provenFormat.proven) {
    return result('L0', 'rule', [`proven-nonfunctional:${provenFormat.reason}`])
  }

  // 步骤 4：已证明纯测试例外：候选全部变更位于测试范围、仅测试用例文件、
  // 未削弱断言、无恒真替换；夹具/支持代码（conftest/helper/fixtures）修改不能
  // 自动继承例外，按实际风险转 needs_triage（W08）。
  if (ctx.testsOnlyCandidate && isTestSupportPath(change.path) && substantive) {
    return result('needs_triage', 'rule', [
      'test-support-code-change-needs-review:夹具/配置修改可能绕过真实验收',
    ])
  }
  if (ctx.testsOnlyCandidate && isTestCodePath(change.path) && substantive) {
    if (assertionWeakened(beforeText, afterText)) {
      return result('needs_triage', 'rule', ['tests-only-but-assertions-net-removed'], {
        testsAcceptanceWeakened: true,
      })
    }
    if (tautologySuspicion(beforeText, afterText)) {
      return result('needs_triage', 'rule', ['tests-only-but-tautological-assertion-added'], {
        testsAcceptanceWeakened: true,
      })
    }
    return result('L1', 'rule', ['proven-tests-only'])
  }
  if (ctx.testsOnlyCandidate && isTestCodePath(change.path) && !substantive) {
    return result('L0', 'rule', [`proven-nonfunctional:${provenFormat.reason}`])
  }

  // 步骤 5：已证明非核心引擎单模块改动：机器不能自动证明（无法排除跨模块行为
  // 与 L2 风险），通过 basis=path-hint 的变更 + 可信人工决策实现（W09）。

  // 步骤 6：适用语义规则或最高路径提示；无法分类输出 needs_triage。
  if (change.path.endsWith('package.json') && substantive) {
    const deps = dependencyChanges(beforeText, afterText)
    const nonDeps = manifestNonDependencyChanges(beforeText, afterText)
    if (nonDeps && nonDeps.length > 0) {
      return result('needs_triage', 'rule', [
        `manifest-non-dependency-fields-changed:${nonDeps.join(',')}`,
      ])
    }
    if (deps && deps.length > 0 && nonDeps) {
      if (deps.every((entry) => entry.bump === 'patch' && entry.section === 'devDependencies')) {
        return result(
          'L0',
          'rule',
          [`dev-dependency-patch-only:${deps.map((e) => e.name).join(',')}`],
          { lockfileMustMatch: true },
        )
      }
      if (deps.every((entry) => entry.bump === 'minor')) {
        const builderMinor = deps.find((entry) => entry.name === 'electron-builder')
        return result(
          'L1',
          'rule',
          [`dependency-minor:${deps.map((e) => `${e.name}:${e.section}`).join(',')}`],
          builderMinor ? { packageValidationRequired: true } : {},
        )
      }
      return result('needs_triage', 'rule', [
        `dependency-change-unclassified:${deps.map((e) => `${e.name}:${e.bump}`).join(',')}`,
      ])
    }
  }
  if (change.path === 'package-lock.json') {
    if (ctx.lockMatchesManifest === true) {
      return result(ctx.dependencyBumpLevel, 'rule', [
        `lockfile-follows-manifest:${ctx.dependencyBumpReason ?? ''}`,
      ])
    }
    return result('needs_triage', 'rule', ['lockfile-diff-not-proven-consistent-with-manifest'])
  }
  if (change.path === 'uv.lock' || change.path === 'pyproject.toml') {
    return result('needs_triage', 'rule', [
      'python-manifest-or-lock-needs-review:无法无依赖机器解析 TOML 依赖语义',
    ])
  }
  if (!isStatusDocument(change.path) && /\.(md|json)$/.test(change.path) && substantive) {
    const outerClaim = completionClaimOutsideStatusDocument(beforeText, afterText)
    if (outerClaim.claimed) {
      return result('needs_triage', 'rule', [
        `completion-claim-outside-status-document:${outerClaim.evidence}:须可信声明/裁定确认是否 FR 结算或发布候选`,
      ])
    }
  }
  if (hintLevel) {
    return result(hintLevel, hintLevel === 'L2' ? 'path-hint' : 'rule', [
      `highest-path-hint:${hintLevel}`,
    ])
  }
  return result('needs_triage', 'rule', ['no-rule-and-no-path-hint'])
}

// 候选级组合与强制规则（跨模块行为、可信声明 FR 结算/发布候选）。提取为独立
// 函数，人工决策应用后重跑同一规则，保证决策不能移除候选级强制 L2（W07）。
export function recomputeCandidateLevel(perChange, changes, ctx, baseReasons = []) {
  const decided = perChange.filter((entry) => entry.level !== 'needs_triage')
  const provisionalLevel =
    decided.length === 0
      ? null
      : decided.reduce(
          (max, entry) => (LEVEL_RANK[entry.level] > LEVEL_RANK[max] ? entry.level : max),
          'L0',
        )
  const pendingTriage = perChange.filter((entry) => entry.level === 'needs_triage')
  const reasons = [...baseReasons]
  let level = pendingTriage.length > 0 ? 'needs_triage' : provisionalLevel
  if (pendingTriage.length > 0) {
    reasons.push(`pending-triage:${pendingTriage.map((entry) => entry.path).join(',')}`)
  }
  const touchedModules = new Set()
  for (const change of changes) {
    const beforeText = textOrNull(change.beforeBytes)
    const afterText = textOrNull(change.afterBytes)
    if (effectiveProvenFormat(change, beforeText, afterText).proven) continue
    const module = sensitiveModuleOf(change.path)
    if (module) touchedModules.add(module)
  }
  if (touchedModules.size >= 2) {
    reasons.push(`cross-module-behavior:${[...touchedModules].sort().join('+')}`)
    level = 'L2'
  }
  if (ctx.declaration?.isFrSettlement) {
    reasons.push('fr-settlement-declared-by-trusted-scope')
    level = 'L2'
  }
  if (ctx.declaration?.isReleaseCandidate) {
    reasons.push('release-candidate-declared-by-trusted-scope')
    level = 'L2'
  }
  return { level, provisionalLevel, pendingTriage, reasons }
}

export function classifyCandidate(changes, ctx) {
  const perChange = changes.map((change) => classifyChange(change, ctx))
  const recomputed = recomputeCandidateLevel(perChange, changes, ctx)
  const flags = {}
  for (const entry of perChange) Object.assign(flags, entry.flags)
  const pendingSemanticReview = perChange.filter(
    (entry) => entry.level === 'L2' && entry.basis === 'path-hint',
  )
  return {
    level: recomputed.level,
    provisionalLevel: recomputed.provisionalLevel,
    reasons: recomputed.reasons,
    perChange,
    flags,
    pendingTriage: recomputed.pendingTriage,
    pendingSemanticReview,
  }
}

// 可信人工决策：等级必须合法；needs_triage 可定级、任何变更可升级；
// 仅 basis=path-hint（路径保守提示，非机器证明的 L2 语义风险）允许降级，
// semantic-proof 降级被拒绝；应用后重算候选级强制规则（W07）。
export function applyTriageDecisions(classification, decisions, changes, ctx) {
  const errors = []
  const applied = []
  for (const decision of decisions ?? []) {
    if (!decision || typeof decision !== 'object') {
      errors.push('决策条目不是对象')
      continue
    }
    if (!['L0', 'L1', 'L2'].includes(decision.level)) {
      errors.push(`决策等级非法：${JSON.stringify(decision.level)}`)
      continue
    }
    if (!Array.isArray(decision.paths) || decision.paths.length === 0) {
      errors.push('决策缺少 paths')
      continue
    }
    if (typeof decision.reason !== 'string' || decision.reason.trim() === '') {
      errors.push('决策缺少 reason')
      continue
    }
    for (const pattern of decision.paths) {
      const targets = classification.perChange.filter((entry) =>
        pattern.endsWith('/**')
          ? entry.path.startsWith(pattern.slice(0, -2))
          : entry.path === pattern,
      )
      if (targets.length === 0) {
        errors.push(`决策路径未命中任何变更：${pattern}`)
        continue
      }
      for (const target of targets) {
        const machineRank = LEVEL_RANK[target.level]
        if (machineRank === undefined) {
          target.level = decision.level
          target.basis = 'triage-decision'
          target.reasons.push(`triage-decision:${decision.level}:${decision.reason.slice(0, 100)}`)
          applied.push(target.path)
        } else if (LEVEL_RANK[decision.level] > machineRank) {
          target.level = decision.level
          target.basis = 'triage-decision'
          target.reasons.push(`triage-decision-upgrade:${decision.level}`)
          applied.push(target.path)
        } else if (LEVEL_RANK[decision.level] < machineRank) {
          if (target.basis === 'path-hint') {
            target.level = decision.level
            target.basis = 'triage-decision'
            target.reasons.push(
              `triage-decision-downgrade:path-hint-L2->${decision.level}:${decision.reason.slice(0, 100)}`,
            )
            applied.push(target.path)
          } else {
            errors.push(
              `决策试图把机器${target.basis}判 ${target.level} 的变更降级为 ${decision.level}：${target.path}`,
            )
          }
        }
      }
    }
  }
  const recomputed = recomputeCandidateLevel(
    classification.perChange,
    changes,
    ctx,
    classification.baseReasons ?? [],
  )
  classification.level = recomputed.level
  classification.provisionalLevel = recomputed.provisionalLevel
  classification.pendingTriage = recomputed.pendingTriage
  classification.reasons = recomputed.reasons
  classification.appliedDecisions = applied
  classification.errors = [...(classification.errors ?? []), ...errors]
  return classification
}
