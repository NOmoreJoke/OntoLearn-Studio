// 审查分级核心逻辑（纯函数，无 I/O）。规则说明见 docs/process/review-policy.md。
const ORDER = { L0: 0, L1: 1, L2: 2 }
const DEP_FIELDS = [
  'dependencies',
  'devDependencies',
  'optionalDependencies',
  'peerDependencies',
  'overrides',
  'resolutions',
]

// 不可通过任何策略 JSON 覆盖的 L2 硬底线：以下路径在任何策略下最低为 L2，
// 防止策略文件删改或降级规则实现自我降级（与 .github/review-policy.json 第一条规则互相印证）。
// tests/unit/review-level* 同时锁定 .test.ts 与 160 条清单 fixture（review-level-checklist-fixture.txt）。
export const IMMUTABLE_L2_PATTERNS = [
  '.github/review-policy.json',
  'docs/process/review-policy.md',
  'docs/process/review-checklist.md',
  'scripts/review-level*',
  'tests/unit/review-level*',
  '.github/workflows/**',
  'scripts/ci-quality-schedule.py',
  'scripts/run-engine-tests.py',
  'scripts/verify-*',
  'scripts/i04_matrix_evidence.py',
  'docs/source-manifest.json',
  'packages/contracts/**',
  'docs/prd/**',
]

export function maxLevel(...levels) {
  return levels.reduce((a, b) => (ORDER[b] > ORDER[a] ? b : a), 'L0')
}

export function globToRegExp(glob) {
  let re = ''
  for (let i = 0; i < glob.length; i++) {
    const c = glob[i]
    if (c === '*' && glob[i + 1] === '*') {
      i++
      if (glob[i + 1] === '/') {
        i++
        re += '(?:.*/)?'
      } else re += '.*'
    } else if (c === '*') re += '[^/]*'
    else if (c === '?') re += '[^/]'
    else re += c.replace(/[.+^${}()|[\]\\]/g, '\\$&')
  }
  return new RegExp(`^${re}$`)
}

const IMMUTABLE_L2 = IMMUTABLE_L2_PATTERNS.map((g) => globToRegExp(g))

/**
 * 规范仓库路径防线（Fail-Closed）：拒绝空路径、反斜杠、前导 `/`、前导 `./`、
 * `..`/`.` 路径段与空段（同时涵盖 `a//b`、尾部 `/`）。防止 `./.github/review-policy.json`
 * 之类的写法绕过精确路径/glob 匹配后误落入默认等级。
 */
export function assertCanonicalRepoPath(path) {
  if (typeof path !== 'string' || path === '')
    throw new Error(`路径必须是非空字符串，收到 ${JSON.stringify(path)}（Fail-Closed）`)
  if (path.includes('\\'))
    throw new Error(`路径不得包含反斜杠：「${path}」（Fail-Closed，要求仓库相对 POSIX 路径）`)
  const bad = path.split('/').findIndex((seg) => seg === '' || seg === '.' || seg === '..')
  if (bad !== -1)
    throw new Error(
      `路径包含非法段（空/./..）：「${path}」第 ${bad + 1} 段（Fail-Closed，要求规范仓库相对路径）`,
    )
  return path
}

export function classifyPath(path, policy) {
  assertCanonicalRepoPath(path)
  for (const rule of policy.rules) {
    if (rule.paths.some((g) => globToRegExp(g).test(path)))
      return { level: rule.level, reason: rule.reason }
  }
  return { level: policy.defaultLevel, reason: '未匹配规则，按默认等级' }
}

// 单一简单版本：可选 ^/~ 前缀 + 完整 x.y.z 三元组，其余（区间/通配/prerelease/URL 等）一律不匹配。
const SIMPLE_SPEC = /^([\^~])?(\d+)\.(\d+)\.(\d+)$/

/**
 * 严格比较完整依赖 spec：仅当两侧都是单一简单版本字符串时才做三元组比较；
 * 任一侧不是字符串（嵌套 overrides 对象、数组、null 等）一律返回 'unknown'，
 * 禁止 String() 字符串化后把两个不同对象误判为 'none'；
 * 含 `||`、`<`、`>`、`-`、`x`、`*`、prerelease、build metadata、URL、file:/workspace:、
 * latest/next 或空格等无法安全归约的 spec 一律返回 'unknown'，由调用方保守分级；
 * 区间前缀改变（如 1.0.0 -> ^1.0.0）同样不算无变化。
 */
export function bumpKind(from, to) {
  if (typeof from !== 'string' || typeof to !== 'string') return 'unknown'
  const a = from.trim()
  const b = to.trim()
  if (a === b) return 'none'
  const ma = SIMPLE_SPEC.exec(a)
  const mb = SIMPLE_SPEC.exec(b)
  if (!ma || !mb) return 'unknown'
  if (ma[1] !== mb[1]) return 'unknown' // 范围前缀变化（^1.0.0 -> ~1.0.0 等）改变可安装区间
  const [x, y, z] = [Number(ma[2]), Number(ma[3]), Number(ma[4])]
  const [X, Y, Z] = [Number(mb[2]), Number(mb[3]), Number(mb[4])]
  if (x !== X) return 'major'
  // 0.x 的次版本视为破坏性变更
  if (y !== Y) return x === 0 ? 'major' : 'minor'
  if (z !== Z) return 'patch'
  return 'none'
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize)
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((k) => [k, canonicalize(value[k])]),
    )
  }
  return value
}

/** 去除依赖字段后按键序无关的规范化序列化，纯 key 重排不算变化。 */
function stripDeps(pkg) {
  const rest = { ...pkg }
  for (const f of DEP_FIELDS) delete rest[f]
  return JSON.stringify(canonicalize(rest))
}

const DEP_FIELD_TAGS = {
  dependencies: '运行时依赖',
  optionalDependencies: '可选运行时依赖',
  peerDependencies: '运行时依赖（peer）',
  overrides: '依赖覆写（overrides）',
  resolutions: '依赖覆写（resolutions）',
}

/**
 * 递归收集嵌套 spec（如 npm overrides 的对象写法）的逐叶差异。
 * findings: [{ kind: 'structural' | 'unknown' | 'major' | 'minor' | 'patch', at, from?, to? }]
 * - 键新增/删除、对象↔标量类型切换、数组取值 → structural；
 * - 两侧均为字符串叶子 → bumpKind 归类（'none' 不记录）；
 * - 其余（含 null 等非对象）→ structural。
 */
function collectNestedFindings(from, to, at, out) {
  const fromObj = from !== null && typeof from === 'object' && !Array.isArray(from)
  const toObj = to !== null && typeof to === 'object' && !Array.isArray(to)
  if (!fromObj || !toObj) {
    if (typeof from === 'string' && typeof to === 'string') {
      const kind = bumpKind(from, to)
      if (kind !== 'none') out.push({ kind, at, from, to })
    } else {
      out.push({ kind: 'structural', at })
    }
    return
  }
  for (const key of new Set([...Object.keys(from), ...Object.keys(to)])) {
    const next = at === '' ? key : `${at}.${key}`
    if (!(key in from) || !(key in to)) {
      out.push({ kind: 'structural', at: next, added: key in to })
      continue
    }
    collectNestedFindings(from[key], to[key], next, out)
  }
}

// 嵌套 spec 按 runtime = true 保守分级：结构/不可解析/主版本（含 0.x 次版本）→ L2；次/补丁 → L1。
const NESTED_FINDING_LEVEL = {
  structural: 'L2',
  unknown: 'L2',
  major: 'L2',
  minor: 'L1',
  patch: 'L1',
}

function describeNestedFinding(f) {
  if (f.kind === 'structural') {
    if (f.added === true) return `新增 ${f.at}`
    if (f.added === false) return `移除 ${f.at}`
    return `结构变化 ${f.at}`
  }
  return `${f.at} ${f.from} → ${f.to}（${f.kind}）`
}

function classifyNestedSpec(from, to) {
  const findings = []
  collectNestedFindings(from, to, '', findings)
  if (findings.length === 0) return { level: 'L0', detail: '无实质变化' }
  const shown = findings.slice(0, 5).map(describeNestedFinding)
  if (findings.length > 5) shown.push(`…另有 ${findings.length - 5} 处`)
  return {
    level: maxLevel(...findings.map((f) => NESTED_FINDING_LEVEL[f.kind])),
    detail: shown.join('；'),
  }
}

function parseManifestObject(text, side) {
  if (text === undefined)
    throw new Error(`package.json ${side} 内容未提供（undefined），拒绝猜测分级（Fail-Closed）`)
  if (text === null) return null
  let value
  try {
    value = JSON.parse(text)
  } catch (e) {
    throw new Error(`package.json ${side} JSON 解析失败（Fail-Closed）：${e.message}`, { cause: e })
  }
  if (value === null || typeof value !== 'object' || Array.isArray(value))
    throw new Error(`package.json ${side} 解析结果不是 JSON 对象（Fail-Closed）`)
  return value
}

/**
 * 比较 package.json 前后文本，返回等级与逐项原因。
 * base/head 任一侧 undefined、双侧同时为 null、非 null 文本解析失败或非对象时直接抛错（Fail-Closed）。
 * 依赖项值为嵌套对象（overrides/resolutions 对象写法）或其他非字符串时，
 * 先做规范化（key 序无关）比对：纯 key 重排不算变化；否则递归逐叶检查 spec，
 * 存在新增/删除/结构变化/不可解析/主版本（含 0.x 次版本）一律保守按 L2。
 */
export function classifyPackageJson(baseText, headText, policy) {
  const critical = new Set(policy.dependencies?.critical ?? [])
  const base = parseManifestObject(baseText, 'base')
  const head = parseManifestObject(headText, 'head')
  if (base === null && head === null)
    throw new Error('package.json base 与 head 同时缺失，拒绝分级（Fail-Closed）')
  const a = base ?? {}
  const b = head ?? {}
  const out = []
  const add = (level, reason) => out.push({ level, reason })
  if (stripDeps(a) !== stripDeps(b)) add('L1', '非依赖字段变化（scripts/配置等）')
  for (const field of DEP_FIELDS) {
    const fa = a[field] ?? {}
    const fb = b[field] ?? {}
    const runtime = field !== 'devDependencies'
    for (const name of new Set([...Object.keys(fa), ...Object.keys(fb)])) {
      const tag = critical.has(name) ? '关键依赖' : (DEP_FIELD_TAGS[field] ?? '依赖')
      if (!(name in fa) || !(name in fb)) {
        const verb = name in fb ? '新增' : '移除'
        add(critical.has(name) || runtime ? 'L2' : 'L1', `${tag} ${name} ${verb}`)
        continue
      }
      const va = fa[name]
      const vb = fb[name]
      if (typeof va !== 'string' || typeof vb !== 'string') {
        // 嵌套对象/非字符串 spec：先规范化比对（纯 key 重排不算变化），再递归逐叶检查
        if (JSON.stringify(canonicalize(va)) === JSON.stringify(canonicalize(vb))) continue
        const nested = classifyNestedSpec(va, vb)
        add(nested.level, `${tag} ${name} 嵌套 spec 变化（${nested.detail}）`)
        continue
      }
      const kind = bumpKind(va, vb)
      if (kind === 'none') continue
      const desc = `${tag} ${name} ${va} → ${vb}（${kind}）`
      if (kind === 'unknown') {
        // spec 无法可靠解析：关键或运行时依赖保守按 L2，仅非关键开发依赖按 L1
        if (critical.has(name) || runtime) add('L2', `${desc}（spec 不可解析，保守 L2）`)
        else add('L1', desc)
      } else if (critical.has(name) || runtime) {
        add(kind === 'major' ? 'L2' : 'L1', desc)
      } else {
        add(kind === 'patch' ? 'L0' : 'L1', desc)
      }
    }
  }
  if (out.length === 0) return { level: 'L0', reasons: ['无实质变化'] }
  return { level: maxLevel(...out.map((o) => o.level)), reasons: out.map((o) => o.reason) }
}

// 锁文件生态兜底：未在 lockfileGroups 显式分组时按文件名归属生态，只跟随同生态 manifest。
const NODE_LOCKFILE_BASENAMES = new Set([
  'package-lock.json',
  'npm-shrinkwrap.json',
  'yarn.lock',
  'pnpm-lock.yaml',
])
const PYTHON_LOCKFILE_BASENAMES = new Set(['uv.lock', 'poetry.lock'])

/**
 * 判断锁文件本次是否随其**所属生态**的清单一起变化：
 * 先查 policy.dependencies.lockfileGroups 的显式分组；未分组时按生态文件名兜底
 * （npm 系锁文件只随 package.json 系 manifest，uv/poetry 锁文件只随 pyproject.toml 系 manifest）；
 * 未知生态不跟随任何清单（单独变化按 L1，绝不因其他生态清单变化被降为 L0）。
 */
function lockfileFollowsManifest(lockfilePath, files, policy) {
  const deps = policy.dependencies ?? {}
  const group = (deps.lockfileGroups ?? []).find((g) => (g.lockfiles ?? []).includes(lockfilePath))
  let associated
  if (group) {
    associated = new Set(group.manifests ?? [])
  } else {
    const base = lockfilePath.slice(lockfilePath.lastIndexOf('/') + 1)
    const manifests = deps.manifests ?? []
    if (NODE_LOCKFILE_BASENAMES.has(base)) {
      associated = new Set(
        manifests.filter((m) => m === 'package.json' || m.endsWith('/package.json')),
      )
    } else if (PYTHON_LOCKFILE_BASENAMES.has(base)) {
      associated = new Set(
        manifests.filter((m) => m === 'pyproject.toml' || m.endsWith('/pyproject.toml')),
      )
    } else {
      associated = new Set()
    }
  }
  return files.some((f) => associated.has(f.path))
}

function classifyOne(file, files, policy) {
  const deps = policy.dependencies ?? {}
  const manifests = new Set(deps.manifests ?? [])
  if (manifests.has(file.path)) {
    if (file.path.endsWith('package.json')) {
      const r = classifyPackageJson(file.base, file.head, policy)
      return { path: file.path, level: r.level, reason: r.reasons.join('；') }
    }
    if (file.path.endsWith('pyproject.toml'))
      return {
        path: file.path,
        level: 'L2',
        reason: 'Python 依赖与包配置清单变化（含运行时依赖，保守按 L2）',
      }
    return { path: file.path, level: 'L1', reason: '依赖清单变化' }
  }
  if ((deps.lockfiles ?? []).includes(file.path)) {
    return lockfileFollowsManifest(file.path, files, policy)
      ? { path: file.path, level: 'L0', reason: '锁文件随所属生态清单变化' }
      : { path: file.path, level: 'L1', reason: '锁文件单独变化（未伴随所属生态清单）' }
  }
  return { path: file.path, ...classifyPath(file.path, policy) }
}

function withImmutableFloor(path, result) {
  if (result.level === 'L2') return result
  return IMMUTABLE_L2.some((re) => re.test(path))
    ? { ...result, level: 'L2', reason: `${result.reason}；命中不可降级 L2 硬底线` }
    : result
}

/**
 * files: [{ path, base?: string|null, head?: string|null }]
 * base/head 仅对 package.json 类 manifest 需要（缺失/损坏直接抛错）。
 * 提供 basePolicy（可信基线策略）时，每个文件与整包等级取 maxLevel(head, base)，
 * 策略删改均无法降级；IMMUTABLE_L2_PATTERNS 硬底线在任何策略下生效。
 * 所有路径先经 assertCanonicalRepoPath 做规范路径防线（Fail-Closed）。
 */
export function classifyChange(files, headPolicy, basePolicy = null) {
  for (const file of files) assertCanonicalRepoPath(file.path)
  const results = files.map((file) => {
    const headResult = withImmutableFloor(file.path, classifyOne(file, files, headPolicy))
    if (!basePolicy) return headResult
    const baseResult = withImmutableFloor(file.path, classifyOne(file, files, basePolicy))
    if (ORDER[baseResult.level] > ORDER[headResult.level])
      return {
        ...headResult,
        level: baseResult.level,
        reason: `${headResult.reason}；基线策略判定 ${baseResult.level}（取最高）`,
      }
    return headResult
  })
  return { level: maxLevel(...results.map((r) => r.level)), files: results }
}

const SHA256_RE = /^[0-9a-f]{64}$/i

/**
 * 严格校验 docs/source-manifest.json 证据架构（Fail-Closed）：
 * 必须是普通对象（非 null 非数组）、files 为非空数组，且每个条目为非 null 对象、
 * 具有非空规范仓库路径 entry.path 与 64 位十六进制 entry.sha256。
 * `{}`、`{"files":[]}`、缺 files、非法 sha/路径一律抛错，绝不返回"0 条全部通过"的假成功。
 */
export function validateSourceManifest(manifest, label = 'docs/source-manifest.json') {
  if (typeof manifest !== 'object' || manifest === null || Array.isArray(manifest))
    throw new Error(`${label} 不是 JSON 对象（Fail-Closed）`)
  if (!Array.isArray(manifest.files) || manifest.files.length === 0)
    throw new Error(`${label} 缺少非空 files 数组（Fail-Closed，空清单不等于核对通过）`)
  for (const [i, entry] of manifest.files.entries()) {
    if (typeof entry !== 'object' || entry === null || Array.isArray(entry))
      throw new Error(`${label}.files[${i}] 不是对象（Fail-Closed）`)
    try {
      assertCanonicalRepoPath(entry.path)
    } catch (e) {
      throw new Error(
        `${label}.files[${i}].path 不是合法仓库路径「${String(entry.path)}」（Fail-Closed）：${e.message}`,
        { cause: e },
      )
    }
    if (typeof entry.sha256 !== 'string' || !SHA256_RE.test(entry.sha256))
      throw new Error(
        `${label}.files[${i}].sha256 不是 64 位十六进制摘要「${String(entry.sha256)}」（Fail-Closed）`,
      )
  }
  return manifest
}
