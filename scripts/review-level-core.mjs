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
export const IMMUTABLE_L2_PATTERNS = [
  '.github/review-policy.json',
  'docs/process/review-policy.md',
  'docs/process/review-checklist.md',
  'scripts/review-level*',
  'tests/unit/review-level*.test.ts',
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

export function classifyPath(path, policy) {
  for (const rule of policy.rules) {
    if (rule.paths.some((g) => globToRegExp(g).test(path)))
      return { level: rule.level, reason: rule.reason }
  }
  return { level: policy.defaultLevel, reason: '未匹配规则，按默认等级' }
}

// 单一简单版本：可选 ^/~ 前缀 + 完整 x.y.z 三元组，其余（区间/通配/prerelease/URL 等）一律不匹配。
const SIMPLE_SPEC = /^([\^~])?(\d+)\.(\d+)\.(\d+)$/

/**
 * 严格比较完整依赖 spec：仅当两侧都是单一简单版本时才做三元组比较；
 * 含 `||`、`<`、`>`、`-`、`x`、`*`、prerelease、build metadata、URL、file:/workspace:、
 * latest/next 或空格等无法安全归约的 spec 一律返回 'unknown'，由调用方保守分级；
 * 区间前缀改变（如 1.0.0 -> ^1.0.0）同样不算无变化。
 */
export function bumpKind(from, to) {
  const a = String(from ?? '').trim()
  const b = String(to ?? '').trim()
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
      const kind = bumpKind(fa[name], fb[name])
      if (kind === 'none') continue
      const desc = `${tag} ${name} ${fa[name]} → ${fb[name]}（${kind}）`
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

function manifestTouchedUnder(files, policy) {
  const manifests = new Set((policy.dependencies ?? {}).manifests ?? [])
  return files.some((f) => manifests.has(f.path))
}

function classifyOne(file, policy, manifestTouched) {
  const deps = policy.dependencies ?? {}
  const manifests = new Set(deps.manifests ?? [])
  const lockfiles = new Set(deps.lockfiles ?? [])
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
  if (lockfiles.has(file.path)) {
    return manifestTouched
      ? { path: file.path, level: 'L0', reason: '锁文件随清单变化' }
      : { path: file.path, level: 'L1', reason: '锁文件单独变化' }
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
 */
export function classifyChange(files, headPolicy, basePolicy = null) {
  const headTouched = manifestTouchedUnder(files, headPolicy)
  const baseTouched = basePolicy ? manifestTouchedUnder(files, basePolicy) : false
  const results = files.map((file) => {
    const headResult = withImmutableFloor(file.path, classifyOne(file, headPolicy, headTouched))
    if (!basePolicy) return headResult
    const baseResult = withImmutableFloor(file.path, classifyOne(file, basePolicy, baseTouched))
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
