#!/usr/bin/env node
// 计算一组提交所需的审查等级（L0/L1/L2）。只读，不修改仓库。
// 用法：node scripts/review-level.mjs [base=origin/develop] [head=HEAD] [--json]
// 仅接受 --json 选项与至多 2 个位置参数；策略取自 git 对象（merge-base 与 head 双读、
// 取最高等级）而非工作树，并叠加不可降级 L2 硬底线；--json 附带 §4.6 机械核对结论。
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { classifyChange, validateSourceManifest } from './review-level-core.mjs'

const USAGE = '用法：node scripts/review-level.mjs [base=origin/develop] [head=HEAD] [--json]'

const args = process.argv.slice(2)
let json = false
const positional = []
for (const arg of args) {
  if (arg === '--json') json = true
  else if (arg.startsWith('--')) {
    process.stderr.write(`未知选项「${arg}」。${USAGE}\n`)
    process.exit(2)
  } else positional.push(arg)
}
if (positional.length > 2) {
  process.stderr.write(
    `位置参数最多 2 个（[base] [head]），收到 ${positional.length} 个。${USAGE}\n`,
  )
  process.exit(2)
}
const [base = 'origin/develop', head = 'HEAD'] = positional

const git = (...a) =>
  execFileSync('git', ['-c', 'core.quotepath=false', ...a], {
    encoding: 'utf8',
    maxBuffer: 256 * 1024 * 1024,
  })
const gitBuffer = (...a) =>
  execFileSync('git', ['-c', 'core.quotepath=false', ...a], { maxBuffer: 256 * 1024 * 1024 })

function resolveCommit(ref, role) {
  if (!ref || ref.startsWith('-')) {
    process.stderr.write(`错误：${role} 引用「${ref}」非法。\n${USAGE}\n`)
    process.exit(1)
  }
  try {
    return git('rev-parse', '--verify', `${ref}^{commit}`).trim()
  } catch {
    process.stderr.write(
      `错误：${role} 引用「${ref}」无法解析为有效提交（git rev-parse --verify 失败）。请确认分支、标签或 SHA 存在。\n`,
    )
    process.exit(1)
  }
}

function blobExists(obj) {
  try {
    execFileSync('git', ['-c', 'core.quotepath=false', 'cat-file', '-e', obj], { stdio: 'ignore' })
    return true
  } catch {
    return false
  }
}

/** 读取 ${rev}:${path} 的原始字节；文件不存在返回 null；存在但读取失败抛错。 */
function readBlobAt(rev, path) {
  const obj = `${rev}:${path}`
  if (!blobExists(obj)) return null
  return gitBuffer('cat-file', 'blob', obj)
}

const POLICY_PATH = '.github/review-policy.json'

function validatePolicy(p, label) {
  if (!Array.isArray(p.rules)) throw new Error(`${label} 缺少 rules 数组`)
  if (!['L0', 'L1', 'L2'].includes(p.defaultLevel)) throw new Error(`${label} defaultLevel 非法`)
  for (const [i, rule] of p.rules.entries()) {
    if (!['L0', 'L1', 'L2'].includes(rule.level)) throw new Error(`${label} rules[${i}].level 非法`)
    if (!Array.isArray(rule.paths)) throw new Error(`${label} rules[${i}].paths 不是数组`)
  }
  if (p.dependencies !== undefined) {
    if (
      typeof p.dependencies !== 'object' ||
      p.dependencies === null ||
      Array.isArray(p.dependencies)
    )
      throw new Error(`${label} dependencies 不是对象`)
    for (const key of ['manifests', 'lockfiles', 'critical']) {
      if (key in p.dependencies && !Array.isArray(p.dependencies[key]))
        throw new Error(`${label} dependencies.${key} 不是数组`)
    }
    if ('lockfileGroups' in p.dependencies) {
      if (!Array.isArray(p.dependencies.lockfileGroups))
        throw new Error(`${label} dependencies.lockfileGroups 不是数组`)
      for (const [i, g] of p.dependencies.lockfileGroups.entries()) {
        if (typeof g !== 'object' || g === null || Array.isArray(g))
          throw new Error(`${label} dependencies.lockfileGroups[${i}] 不是对象`)
        for (const key of ['lockfiles', 'manifests']) {
          if (key in g && !Array.isArray(g[key]))
            throw new Error(`${label} dependencies.lockfileGroups[${i}].${key} 不是数组`)
        }
      }
    }
  }
  return p
}

function readPolicyAt(rev, label) {
  const buf = readBlobAt(rev, POLICY_PATH)
  if (buf === null) return null
  let parsed
  try {
    parsed = JSON.parse(buf.toString('utf8'))
  } catch (e) {
    throw new Error(`${label}（${rev}:${POLICY_PATH}）不是合法 JSON：${e.message}`, { cause: e })
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed))
    throw new Error(`${label}（${rev}:${POLICY_PATH}）不是 JSON 对象`)
  return validatePolicy(parsed, label)
}

try {
  const baseSha = resolveCommit(base, 'base')
  const headSha = resolveCommit(head, 'head')
  const mergeBase = git('merge-base', baseSha, headSha).trim()
  const baseTree = git('rev-parse', `${baseSha}^{tree}`).trim()
  const headTree = git('rev-parse', `${headSha}^{tree}`).trim()

  // 可信基线：从 git 对象读取 merge-base 与 head 的策略（不信任工作树未审内容），等级取两侧最高
  const basePolicy = readPolicyAt(mergeBase, '基线审查策略')
  let headPolicy = readPolicyAt(headSha, 'head 审查策略')
  if (headPolicy === null) headPolicy = basePolicy
  if (headPolicy === null)
    throw new Error(`${POLICY_PATH} 在 ${mergeBase} 与 ${headSha} 均不存在，无法分级`)

  const diffOut = git('diff', '--name-status', '-z', '--no-renames', mergeBase, headSha)
  const tokens = diffOut.split('\0')
  const entries = []
  for (let i = 0; i + 1 < tokens.length; i += 2) {
    if (!tokens[i]) continue
    entries.push({ status: tokens[i], path: tokens[i + 1] })
  }

  // manifest 集合取 head 与基线策略双方 dependencies.manifests 的并集（Fail-Closed 读取）：
  // 任一侧新增声明的清单都必须读取前后文本，绝不因单侧缺失而漏判清单变化；
  // 双方声明存在分歧时明确提示基线分歧，避免误导性的静默行为。
  const headManifests = (headPolicy.dependencies ?? {}).manifests ?? []
  const baseManifests = (basePolicy?.dependencies ?? {}).manifests ?? []
  const manifests = new Set([...headManifests, ...baseManifests])
  const manifestDivergence = [
    ...headManifests.filter((m) => !baseManifests.includes(m)),
    ...baseManifests.filter((m) => !headManifests.includes(m)),
  ]
  if (basePolicy && manifestDivergence.length > 0)
    process.stderr.write(
      `注意：基线与 head 策略的 dependencies.manifests 存在分歧（${manifestDivergence.join('、')}），已按并集读取（Fail-Closed）。\n`,
    )
  // 只有 status 为 A 允许 base 为 null，只有 D 允许 head 为 null；其余读取失败一律抛错
  const manifestText = (rev, path, status, side) => {
    if ((side === 'base' && status === 'A') || (side === 'head' && status === 'D')) return null
    const buf = readBlobAt(rev, path)
    if (buf === null)
      throw new Error(`无法读取 ${rev}:${path}（${side} 侧按 diff 状态应存在，Fail-Closed）`)
    return buf.toString('utf8')
  }
  const files = entries.map(({ status, path }) =>
    manifests.has(path)
      ? {
          path,
          base: manifestText(mergeBase, path, status, 'base'),
          head: manifestText(headSha, path, status, 'head'),
        }
      : { path },
  )

  const result = classifyChange(files, headPolicy, basePolicy)

  // §4.6 机械核对：变更文件原始字节与 SHA-256 摘要（head 侧；删除文件为 null）
  const changedFileDigests = entries.map(({ status, path }) => {
    let bytes = null
    let sha256 = null
    if (status !== 'D') {
      const buf = readBlobAt(headSha, path)
      if (buf === null) throw new Error(`无法读取 ${headSha}:${path} 以计算摘要（Fail-Closed）`)
      bytes = buf.length
      sha256 = createHash('sha256').update(buf).digest('hex')
    }
    return { path, status, bytes, sha256 }
  })

  const sourceManifest = (() => {
    const buf = readBlobAt(headSha, 'docs/source-manifest.json')
    if (buf === null)
      return {
        ok: false,
        checkedCount: 0,
        mismatches: [{ path: 'docs/source-manifest.json', expected: null, actual: null }],
      }
    let manifest
    try {
      manifest = JSON.parse(buf.toString('utf8'))
    } catch (e) {
      throw new Error(`head 的 docs/source-manifest.json 不是合法 JSON：${e.message}`, { cause: e })
    }
    // 严格证据架构校验（Fail-Closed）：{}、空/缺失 files、非法条目一律失败，杜绝 0 条假成功
    validateSourceManifest(manifest)
    const mismatches = []
    let checkedCount = 0
    for (const entry of manifest.files) {
      checkedCount++
      const blob = readBlobAt(headSha, entry.path)
      const actual = blob === null ? null : createHash('sha256').update(blob).digest('hex')
      if (actual !== entry.sha256)
        mismatches.push({ path: entry.path, expected: entry.sha256, actual })
    }
    return { ok: mismatches.length === 0, checkedCount, mismatches }
  })()
  const mechanical = { ok: sourceManifest.ok, changedFileDigests, sourceManifest }

  // 只读自检元信息：候选是否触及策略/分级器自身路径；G0 合入后此类候选必须以
  // 可信基线（origin/develop）脚本副本执行分级并比对输出（见 docs/process/review-policy.md §5）。
  const POLICY_OR_CLASSIFIER_PATHS = new Set([
    '.github/review-policy.json',
    'docs/process/review-policy.md',
    'docs/process/review-checklist.md',
  ])
  const policyOrClassifierTouched = entries.some(
    (e) =>
      POLICY_OR_CLASSIFIER_PATHS.has(e.path) ||
      e.path.startsWith('scripts/review-level') ||
      e.path.startsWith('tests/unit/review-level'),
  )
  const selfCheck = {
    policyOrClassifierTouched,
    trustedBaselineRule: 'run_from_trusted_base_after_g0',
  }

  if (json) {
    console.log(
      JSON.stringify(
        {
          base,
          head,
          baseSha,
          headSha,
          mergeBase,
          baseTree,
          headTree,
          ...result,
          mechanical,
          selfCheck,
        },
        null,
        2,
      ),
    )
  } else {
    console.log(
      `审查等级：${result.level}（${entries.length} 个文件，基于 ${mergeBase.slice(0, 12)}..${headSha.slice(0, 12)}）`,
    )
    for (const level of ['L2', 'L1', 'L0']) {
      const group = result.files.filter((f) => f.level === level)
      if (group.length === 0) continue
      console.log(`\n[${level}] ${group.length} 个文件`)
      for (const f of group.slice(0, 50)) console.log(`  ${f.path} — ${f.reason}`)
      if (group.length > 50) console.log(`  … 另有 ${group.length - 50} 个`)
    }
    const baseNote = !basePolicy
      ? '基线无策略文件，按 head 策略 + 不可降级 L2 硬底线'
      : headPolicy === basePolicy
        ? 'head 策略缺失，回退基线策略'
        : '基线与 head 策略取最高等级'
    console.log(`\n策略基线：${baseNote}`)
    if (policyOrClassifierTouched)
      console.log(
        '自检：本候选触及策略/分级器自身路径，强制 L2；G0 合入后总控与自动门禁必须以可信基线（origin/develop）脚本副本执行分级并比对输出（见 docs/process/review-policy.md §5）。',
      )
    console.log(
      `机械核对：${mechanical.ok ? '通过' : '未通过'}（${changedFileDigests.length} 个变更文件摘要、${sourceManifest.checkedCount} 个清单条目）`,
    )
    if (!mechanical.ok)
      for (const m of sourceManifest.mismatches) console.log(`  不一致：${JSON.stringify(m)}`)
  }
  if (!mechanical.ok) process.exit(1)
} catch (e) {
  process.stderr.write(`错误：${e instanceof Error ? e.message : String(e)}\n`)
  process.exit(1)
}
