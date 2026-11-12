// range-diff 输出解析。git range-diff 的退出码不代表补丁一致（几乎总是 0），
// 必须解析条目本身；任何无法识别的条目行都判 unknown，不得用"解析到的都是
// 等号"推定全部相等。
// 条目形态：
//   双侧：  `1:  abc1234 = 1:  def5678 标题`（= 相同补丁 / ! 修改）
//   仅右侧：`-:  ------- > 2:  fed1234 新增补丁`
//   仅左侧：`3:  abc1234 < -:  ------- 删除补丁`
const BOTH_RE = /^\s*(\d+):\s+[0-9a-f]+ ([=!<>]) (\d+):\s+[0-9a-f]+ /
const RIGHT_ONLY_RE = /^\s*-:\s+-+ > (\d+):\s+[0-9a-f]+ /
const LEFT_ONLY_RE = /^\s*(\d+):\s+[0-9a-f]+ < -:\s+-+ /
const ENTRY_HEAD_RE = /^\s*(?:\d+|-):/

export function parseRangeDiff(rawOutput) {
  const entries = []
  let unrecognized = 0
  for (const line of rawOutput.split('\n')) {
    if (!ENTRY_HEAD_RE.test(line)) continue
    const both = BOTH_RE.exec(line)
    if (both) {
      entries.push({ left: Number(both[1]), op: both[2], right: Number(both[3]) })
      continue
    }
    const rightOnly = RIGHT_ONLY_RE.exec(line)
    if (rightOnly) {
      entries.push({ left: null, op: '>', right: Number(rightOnly[1]) })
      continue
    }
    const leftOnly = LEFT_ONLY_RE.exec(line)
    if (leftOnly) {
      entries.push({ left: Number(leftOnly[1]), op: '<', right: null })
      continue
    }
    unrecognized++
  }
  if (unrecognized > 0) {
    return {
      status: 'unknown',
      patchUnchanged: null,
      entries,
      reason: `unrecognized-entry-lines:${unrecognized}`,
    }
  }
  if (entries.length === 0) {
    return { status: 'unknown', patchUnchanged: null, entries: [], reason: 'no-entries-parsed' }
  }
  const ops = new Set(entries.map((entry) => entry.op))
  if (ops.size === 1 && ops.has('=')) {
    return { status: 'unchanged', patchUnchanged: true, entries }
  }
  return {
    status: 'changed',
    patchUnchanged: false,
    entries,
    reason: `ops:${[...ops].sort().join(',')}`,
  }
}

// 可信冲突证据文件解析：冲突状态只能来自附带来源的记录（如 rebase 输出），
// 不接受自由填写的 conflicts=false。文件缺失时冲突状态为 unknown。
export function parseConflictsEvidence(doc) {
  if (!doc || doc.schemaVersion !== 1 || typeof doc.producedBy !== 'string') {
    return { status: 'unknown', reason: 'invalid-or-missing-conflicts-evidence' }
  }
  if (!Array.isArray(doc.conflictPaths) || typeof doc.conflictCount !== 'number') {
    return { status: 'unknown', reason: 'invalid-conflicts-evidence-schema' }
  }
  if (doc.conflictPaths.length !== doc.conflictCount) {
    return { status: 'unknown', reason: 'conflicts-evidence-count-mismatch' }
  }
  if (doc.conflictCount === 0) {
    return { status: 'none-proven-by-attached-evidence', source: doc.producedBy }
  }
  return { status: 'present', count: doc.conflictCount, paths: doc.conflictPaths }
}
