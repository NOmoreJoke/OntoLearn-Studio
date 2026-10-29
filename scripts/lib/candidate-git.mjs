import { spawnSync } from 'node:child_process'

const SHA40 = /^[0-9a-f]{40}$/

// 完整 40 位小写十六进制 SHA 是唯一接受的提交标识输入；短 SHA、大写、对象名一律拒绝。
export function assertFullSha(label, value) {
  if (typeof value !== 'string' || !SHA40.test(value)) {
    throw new Error(`${label} 必须是 40 位小写十六进制完整 SHA，收到：${JSON.stringify(value)}`)
  }
  return value
}

// 所有 git 调用都通过参数数组传参，绝不拼接 shell 字符串，不执行任何 PR 内容。
export function gitRaw(repoDir, args) {
  const result = spawnSync('git', ['-C', repoDir, ...args], {
    encoding: 'buffer',
    maxBuffer: 128 * 1024 * 1024,
    timeout: 60_000,
  })
  if (result.error) throw new Error(`git 调用失败：${result.error.message}`)
  return result
}

export function gitOk(repoDir, args) {
  const result = gitRaw(repoDir, args)
  if (result.status !== 0) {
    const stderr = result.stderr.toString('utf8').trim()
    throw new Error(`git ${args[0]} 退出 ${result.status}：${stderr}`)
  }
  return result.stdout
}

function decode(bytes) {
  return new TextDecoder('utf8', { fatal: false }).decode(bytes)
}

// 验证对象存在且类型符合预期，防止把 tree/blob 当 commit 使用。
export function assertObjectType(repoDir, sha, expected, label) {
  const output = gitOk(repoDir, ['cat-file', '-t', sha]).toString('utf8').trim()
  if (output !== expected) {
    throw new Error(`${label} ${sha} 的对象类型是 ${output}，要求 ${expected}`)
  }
}

export function commitInfo(repoDir, sha) {
  const text = decode(gitOk(repoDir, ['cat-file', 'commit', sha]))
  const tree = /^tree ([0-9a-f]{40})$/m.exec(text)
  const parents = [...text.matchAll(/^parent ([0-9a-f]{40})$/gm)].map((m) => m[1])
  if (!tree) throw new Error(`提交 ${sha} 缺少 tree`)
  return { sha, tree: tree[1], parents }
}

// diff-tree --no-renames -z：重命名拆为删除+新增，旧路径与新路径都计入变更清单。
// -z 输出以 NUL 分隔，路径按原始字节解码，空格、引号、Unicode 文件名都安全。
export function diffTreeChanges(repoDir, base, head) {
  const out = gitOk(repoDir, ['diff-tree', '-r', '--no-renames', '--raw', '-z', base, head])
  const parts = []
  let start = 0
  for (let i = 0; i <= out.length; i++) {
    if (i === out.length || out[i] === 0) {
      parts.push(out.subarray(start, i))
      start = i + 1
    }
  }
  const changes = []
  let i = 0
  const metaRe = /^:([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40}) ([0-9a-f]{40}) ([A-Z])\d*$/
  while (i < parts.length) {
    const meta = decode(parts[i])
    const match = metaRe.exec(meta)
    if (!match) break
    const pathBytes = parts[i + 1]
    if (pathBytes === undefined) throw new Error('diff-tree -z 输出不完整：缺少路径')
    changes.push({
      path: decode(pathBytes),
      oldMode: match[1],
      newMode: match[2],
      oldBlobSha: match[3],
      newBlobSha: match[4],
      status: match[5],
    })
    i += 2
  }
  return changes
}

export function blobBytes(repoDir, sha) {
  if (/^0+$/.test(sha)) return null
  return gitOk(repoDir, ['cat-file', 'blob', sha])
}

// git -w --ignore-cr-at-eol 语义下的"忽略空白后无差异"。这只证明忽略空白后内容一致，
// 不证明行为不变：字符串字面量内空格、Python/YAML 缩进、注释中的工具指令都可能被 -w
// 忽略却真实改变行为。可机器证明的非功能变更仅限 provenLineEndingOnly 的字节级判定。
export function gitIgnoreableWhitespace(repoDir, base, head, path) {
  const result = gitRaw(repoDir, [
    'diff',
    '-w',
    '--ignore-cr-at-eol',
    '--quiet',
    base,
    head,
    '--',
    path,
  ])
  if (result.status === 0) return true
  if (result.status === 1) return false
  throw new Error(`git diff 退出 ${result.status}：${result.stderr.toString('utf8').trim()}`)
}

// ls-tree -r -z：候选 manifest 的唯一来源，覆盖 head tree 的全部 blob。
export function treeManifest(repoDir, treeSha) {
  const out = gitOk(repoDir, ['ls-tree', '-r', '-z', treeSha])
  const files = []
  let start = 0
  for (let i = 0; i <= out.length; i++) {
    if (i !== out.length && out[i] !== 0) continue
    const record = decode(out.subarray(start, i))
    start = i + 1
    if (!record) continue
    const match = /^([0-7]{6}) (blob|commit|tree) ([0-9a-f]{40})\t(.*)$/.exec(record)
    if (!match) throw new Error(`ls-tree 记录无法解析：${record.slice(0, 80)}`)
    files.push({ mode: match[1], type: match[2], sha: match[3], path: match[4] })
  }
  files.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0))
  return { tree: treeSha, files }
}

export function blobExistsAt(repoDir, commitSha, path) {
  const result = gitRaw(repoDir, ['cat-file', '-e', `${commitSha}:${path}`])
  return result.status === 0
}

export function blobTextAt(repoDir, commitSha, path) {
  const result = gitRaw(repoDir, ['cat-file', 'blob', `${commitSha}:${path}`])
  if (result.status !== 0) return null
  return result.stdout
}

// range-diff 原始输出必须保存为证据；退出码不代表补丁一致，解析由 classify 侧完成。
export function rangeDiffRaw(repoDir, previousBase, previousHead, base, head) {
  const result = gitRaw(repoDir, [
    'range-diff',
    `${previousBase}..${previousHead}`,
    `${base}..${head}`,
  ])
  if (result.error || result.status > 1) {
    throw new Error(
      `git range-diff 失败（退出 ${result.status}）：${result.stderr.toString('utf8').trim()}`,
    )
  }
  return result.stdout.toString('utf8')
}
