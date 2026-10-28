#!/usr/bin/env node
// 计算一组提交所需的审查等级（L0/L1/L2）。只读，不修改仓库。
// 用法：node scripts/review-level.mjs [base=origin/develop] [head=HEAD] [--json]
import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { classifyChange } from './review-level-core.mjs'

const args = process.argv.slice(2)
const json = args.includes('--json')
const [base = 'origin/develop', head = 'HEAD'] = args.filter((a) => !a.startsWith('--'))
const policy = JSON.parse(
  readFileSync(new URL('../.github/review-policy.json', import.meta.url), 'utf8'),
)

const git = (...a) =>
  execFileSync('git', ['-c', 'core.quotepath=false', ...a], {
    encoding: 'utf8',
    maxBuffer: 256 * 1024 * 1024,
  })
const show = (rev, path) => {
  try {
    return git('show', `${rev}:${path}`)
  } catch {
    return null
  }
}

const mergeBase = git('merge-base', base, head).trim()
const paths = git('diff', '--name-only', '-z', '--no-renames', mergeBase, head)
  .split('\0')
  .filter(Boolean)
const manifests = new Set(policy.dependencies?.manifests ?? [])
const files = paths.map((path) =>
  manifests.has(path) ? { path, base: show(mergeBase, path), head: show(head, path) } : { path },
)
const result = classifyChange(files, policy)

if (json) {
  console.log(JSON.stringify({ base, head, mergeBase, ...result }, null, 2))
} else {
  console.log(
    `审查等级：${result.level}（${paths.length} 个文件，基于 ${mergeBase.slice(0, 12)}..${head}）`,
  )
  for (const level of ['L2', 'L1', 'L0']) {
    const group = result.files.filter((f) => f.level === level)
    if (group.length === 0) continue
    console.log(`\n[${level}] ${group.length} 个文件`)
    for (const f of group.slice(0, 50)) console.log(`  ${f.path} — ${f.reason}`)
    if (group.length > 50) console.log(`  … 另有 ${group.length - 50} 个`)
  }
}
