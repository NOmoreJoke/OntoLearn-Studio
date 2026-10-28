// 审查分级核心逻辑（纯函数，无 I/O）。规则说明见 docs/process/review-policy.md。
const ORDER = { L0: 0, L1: 1, L2: 2 }
const DEP_FIELDS = ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies']

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

export function classifyPath(path, policy) {
  for (const rule of policy.rules) {
    if (rule.paths.some((g) => globToRegExp(g).test(path)))
      return { level: rule.level, reason: rule.reason }
  }
  return { level: policy.defaultLevel, reason: '未匹配规则，按默认等级' }
}

function parseVersion(spec) {
  const m = /^[\^~>=v\s]*(\d+)\.(\d+)\.(\d+)/.exec(String(spec ?? ''))
  return m ? m.slice(1, 4).map(Number) : null
}

export function bumpKind(from, to) {
  const a = parseVersion(from)
  const b = parseVersion(to)
  if (!a || !b) return 'unknown'
  if (a[0] !== b[0]) return 'major'
  // 0.x 的次版本视为破坏性变更
  if (a[1] !== b[1]) return a[0] === 0 ? 'major' : 'minor'
  if (a[2] !== b[2]) return 'patch'
  return 'none'
}

function stripDeps(pkg) {
  const rest = { ...pkg }
  for (const f of DEP_FIELDS) delete rest[f]
  return JSON.stringify(rest)
}

/** 比较 package.json 前后文本，返回等级与逐项原因。 */
export function classifyPackageJson(baseText, headText, policy) {
  const critical = new Set(policy.dependencies?.critical ?? [])
  let base, head
  try {
    base = baseText ? JSON.parse(baseText) : {}
    head = headText ? JSON.parse(headText) : {}
  } catch {
    return { level: 'L1', reasons: ['package.json 无法解析'] }
  }
  const out = []
  const add = (level, reason) => out.push({ level, reason })
  if (stripDeps(base) !== stripDeps(head)) add('L1', '非依赖字段变化（scripts/配置等）')
  for (const field of DEP_FIELDS) {
    const a = base[field] ?? {}
    const b = head[field] ?? {}
    const runtime = field === 'dependencies'
    for (const name of new Set([...Object.keys(a), ...Object.keys(b)])) {
      const tag = critical.has(name) ? '关键依赖' : runtime ? '运行时依赖' : '开发依赖'
      if (!(name in a) || !(name in b)) {
        const verb = name in b ? '新增' : '移除'
        add(critical.has(name) || runtime ? 'L2' : 'L1', `${tag} ${name} ${verb}`)
        continue
      }
      const kind = bumpKind(a[name], b[name])
      if (kind === 'none') continue
      const desc = `${tag} ${name} ${a[name]} → ${b[name]}（${kind}）`
      if (kind === 'unknown') add('L1', desc)
      else if (critical.has(name)) add(kind === 'major' ? 'L2' : 'L1', desc)
      else if (runtime) add(kind === 'major' ? 'L2' : 'L1', desc)
      else add(kind === 'patch' ? 'L0' : 'L1', desc)
    }
  }
  if (out.length === 0) return { level: 'L0', reasons: ['无实质变化'] }
  return { level: maxLevel(...out.map((o) => o.level)), reasons: out.map((o) => o.reason) }
}

/**
 * files: [{ path, base?: string|null, head?: string|null }]
 * base/head 仅对 package.json 类 manifest 需要。
 */
export function classifyChange(files, policy) {
  const deps = policy.dependencies ?? {}
  const manifests = new Set(deps.manifests ?? [])
  const lockfiles = new Set(deps.lockfiles ?? [])
  const manifestTouched = files.some((f) => manifests.has(f.path))
  const results = files.map((f) => {
    if (manifests.has(f.path)) {
      if (f.path.endsWith('package.json')) {
        const r = classifyPackageJson(f.base ?? null, f.head ?? null, policy)
        return { path: f.path, level: r.level, reason: r.reasons.join('；') }
      }
      return { path: f.path, level: 'L1', reason: '依赖清单变化' }
    }
    if (lockfiles.has(f.path))
      return manifestTouched
        ? { path: f.path, level: 'L0', reason: '锁文件随清单变化' }
        : { path: f.path, level: 'L1', reason: '锁文件单独变化' }
    return { path: f.path, ...classifyPath(f.path, policy) }
  })
  return { level: maxLevel(...results.map((r) => r.level)), files: results }
}
