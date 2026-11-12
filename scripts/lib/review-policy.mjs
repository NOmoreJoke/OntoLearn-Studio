import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'

// 政策文件是标准 YAML 的 JSON 子集，直接用 JSON.parse 读取，不引入 YAML 依赖。
// 政策字节保持精确（.prettierignore 排除），因此其 sha256 可作为可信版本绑定。
export function parsePolicyText(text, sourceLabel) {
  let policy
  try {
    policy = JSON.parse(text)
  } catch (error) {
    throw new Error(`政策 ${sourceLabel} 不是合法的 JSON 子集：${error.message}`, { cause: error })
  }
  for (const key of ['schema_version', 'status', 'classification', 'levels', 'path_hints']) {
    if (!(key in policy)) throw new Error(`政策 ${sourceLabel} 缺少字段 ${key}`)
  }
  if (policy.schema_version !== 1) {
    throw new Error(`政策 ${sourceLabel} schema_version 必须是 1`)
  }
  return policy
}

export function loadPolicyFile(path) {
  return parsePolicyText(readFileSync(path, 'utf8'), path)
}

export function sha256Hex(data) {
  return createHash('sha256').update(data).digest('hex')
}

// 路径提示匹配器：支持 `**` 跨目录段、段内 `*` 通配、其余字符字面匹配。
// `**/*.md` 可匹配根级与任意深度的 .md；`build/**` 匹配 build 目录下全部路径。
export function matchPathHint(path, pattern) {
  return matchSegments(pattern.split('/'), path.split('/'))
}

function matchSegments(pat, seg) {
  if (pat.length === 0) return seg.length === 0
  if (pat[0] === '**') {
    for (let skip = 0; skip <= seg.length; skip++) {
      if (matchSegments(pat.slice(1), seg.slice(skip))) return true
    }
    return false
  }
  if (seg.length === 0) return false
  if (!segmentRegExp(pat[0]).test(seg[0])) return false
  return matchSegments(pat.slice(1), seg.slice(1))
}

const segmentCache = new Map()

function segmentRegExp(segment) {
  let re = segmentCache.get(segment)
  if (!re) {
    const escaped = segment.replace(/[.+^${}()|[\]\\?]/g, '\\$&').replace(/\*/g, '[^/]*')
    re = new RegExp(`^${escaped}$`)
    segmentCache.set(segment, re)
  }
  return re
}

const LEVELS = ['L2', 'L1', 'L0']

export function hintsFor(path, policy) {
  const hits = {}
  for (const level of LEVELS) {
    hits[level] = (policy.path_hints[level] ?? []).filter((pattern) => matchPathHint(path, pattern))
  }
  return hits
}

export function highestHint(path, policy) {
  const hints = hintsFor(path, policy)
  for (const level of LEVELS) if (hints[level].length > 0) return level
  return null
}

// 治理路径：评审政策、候选证据脚本、CI、清单与证据权威文件。改动最低 L1，
// 削弱必需门禁时升 L2；由 scripts/verify-candidate.mjs 与测试共同维护。
const GOVERNANCE_PATTERNS = [
  'AGENTS.md',
  '.github/**',
  'scripts/**',
  'docs/checklists/**',
  'docs/source-manifest.json',
]

export function isGovernancePath(path, policy) {
  const patterns = [...GOVERNANCE_PATTERNS]
  for (const level of LEVELS) {
    for (const pattern of policy.path_hints[level] ?? []) {
      if (pattern.includes('review-policy') || pattern.includes('verify-candidate')) {
        patterns.push(pattern)
      }
    }
  }
  return patterns.some((pattern) => matchPathHint(path, pattern))
}

// 测试代码路径：tests-only 例外的适用范围。只有真正的测试用例文件可继承例外；
// 夹具、conftest、helper、测试配置是"测试支持代码"，修改可能绕过真实验收，
// 不能自动继承 tests-only 例外（W08）。
export function isTestCodePath(path) {
  if (
    matchPathHint(path, 'packages/engine/tests/**') ||
    matchPathHint(path, 'apps/desktop/tests/**')
  ) {
    return /(?:^|\/)(?:test_[^/]+\.py|[^/]+_test\.py)$/.test(path)
  }
  if (matchPathHint(path, 'tests/**')) {
    return /\.(?:test|spec)\.[cm]?[jt]sx?$/.test(path)
  }
  return false
}

// 测试目录内的非测试代码（夹具、conftest、helper、配置）：按实际风险处理。
export function isTestSupportPath(path) {
  const inTests =
    matchPathHint(path, 'tests/**') ||
    matchPathHint(path, 'packages/engine/tests/**') ||
    matchPathHint(path, 'apps/desktop/tests/**')
  return inTests && !isTestCodePath(path)
}

// 状态文档：完成声明出现在这些文件时按 FR 结算处理（L2）。
export function isStatusDocument(path) {
  if (path === 'docs/m0-checklist.md') return true
  return /(?:^|\/)status\.md$/.test(path) && matchPathHint(path, 'docs/**')
}

// 字节级非功能证明：唯一自动判 L0 的情形是行尾 CR 的增删（CRLF/LF 规范化），
// 且每个被增删的 CR 都必须紧邻 LF 或处于文件末尾。其余空白差异（行内空格、
// 缩进、空白行、行尾空白）都可能改变字符串字面量、Python/YAML 语义或注释指令，
// 一律不自动证明，保守按原路径风险或 needs_triage 处理。
export function provenLineEndingOnly(before, after) {
  const identical =
    before.length === after.length && before.every((byte, index) => byte === after[index])
  if (identical) return { proven: false, reason: 'identical-bytes' }
  let i = 0
  let j = 0
  let removed = 0
  let added = 0
  while (i < before.length && j < after.length) {
    if (before[i] === after[j]) {
      i++
      j++
      continue
    }
    if (before[i] === 0x0d && atLineEnd(before, i)) {
      i++
      removed++
      continue
    }
    if (after[j] === 0x0d && atLineEnd(after, j)) {
      j++
      added++
      continue
    }
    return { proven: false, reason: 'non-carriage-return-byte-diff' }
  }
  while (i < before.length) {
    if (before[i] !== 0x0d || !atLineEnd(before, i)) {
      return { proven: false, reason: 'trailing-non-line-ending-diff' }
    }
    i++
    removed++
  }
  while (j < after.length) {
    if (after[j] !== 0x0d || !atLineEnd(after, j)) {
      return { proven: false, reason: 'trailing-non-line-ending-diff' }
    }
    j++
    added++
  }
  if (removed === 0 && added === 0) return { proven: false, reason: 'no-carriage-change' }
  return { proven: true, reason: `line-ending-only(cr-removed=${removed},cr-added=${added})` }
}

function atLineEnd(bytes, index) {
  return index + 1 === bytes.length || bytes[index + 1] === 0x0a
}
