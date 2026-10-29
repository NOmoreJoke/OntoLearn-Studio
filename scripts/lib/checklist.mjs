import { createHash } from 'node:crypto'

// 外部权威锚点：原始用户审查清单的全文 SHA-256（见
// iteration-control/2026-10-21-weekly-release/review-policy-20261029/ 交接）。
// 锚点硬编码在校验器中，防止候选同时改写仓内副本与索引后自洽通过。
export const ANCHOR_SOURCE_SHA256 =
  '1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c'

// 原文条目格式：以 `> ` 开头的引用行，按出现顺序即 1..160 条（147 产品/工程检查
// 在前，13 条角色附录在后，共用同一编号序列）。提取规则与外部批准索引一致。
export function extractOriginalEntries(originalBytes) {
  const text = new TextDecoder('utf8', { fatal: false }).decode(originalBytes)
  return text
    .split('\n')
    .filter((line) => line.startsWith('> '))
    .map((line) => line.slice(2))
}

function sha256Hex(data) {
  return createHash('sha256').update(data).digest('hex')
}

// 校验仓内清单三件套的一致性（W10 加强）：
// 1. 原文副本与权威锚点 hash 一致；
// 2. 从锚定原文按序提取 160 条，逐位核对索引的 sourceOrdinal、text、逐条 sha256
//    （索引改一个 text 并重算其 sha256 也无法通过，因为 text 必须等于原文条目）；
// 3. 计数 147+13、section 与原始附录边界一致、ID 唯一；
// 4. 任何原文/条目/顺序改动都判 fail，不做"恢复原文造相等"。
export function verifySourceChecklist(originalBytes, indexBytes) {
  const errors = []
  const checks = []
  const push = (name, expected, actual, pass) => checks.push({ name, expected, actual, pass })

  const originalSha = sha256Hex(originalBytes)
  const anchorPass = originalSha === ANCHOR_SOURCE_SHA256
  push('original-anchor-sha256', ANCHOR_SOURCE_SHA256, originalSha, anchorPass)
  if (!anchorPass) errors.push('原始清单仓内副本与权威锚点 hash 不一致')

  const index = (() => {
    try {
      return JSON.parse(new TextDecoder('utf8', { fatal: false }).decode(indexBytes))
    } catch (error) {
      errors.push(`清单索引 JSON 解析失败：${error.message}`)
      return null
    }
  })()
  if (!index) {
    return { status: 'fail', errors, checks, summary: null }
  }

  const indexSourcePass = index.sourceSha256 === originalSha
  push('index-source-sha256', originalSha, index.sourceSha256, indexSourcePass)
  if (!indexSourcePass) errors.push('索引记录的 sourceSha256 与仓内原文副本不一致')

  const entries = extractOriginalEntries(originalBytes)
  push('original-entry-count', 160, String(entries.length), entries.length === 160)
  if (entries.length !== 160) {
    errors.push(`锚定原文提取到 ${entries.length} 条（> 行），要求 160`)
  }

  const items = index.items ?? []
  const expectedCounts = { total: 160, productEngineering: 147, roleAppendix: 13 }
  const actualCounts = {
    total: items.length,
    productEngineering: items.filter((item) => item.section === 'product_engineering').length,
    roleAppendix: items.filter((item) => item.section === 'role_appendix').length,
  }
  for (const key of Object.keys(expectedCounts)) {
    const pass = actualCounts[key] === expectedCounts[key]
    push(`count-${key}`, String(expectedCounts[key]), String(actualCounts[key]), pass)
    if (!pass) errors.push(`清单计数 ${key} 期望 ${expectedCounts[key]}，实际 ${actualCounts[key]}`)
  }

  const ids = new Set(items.map((item) => item.id))
  push('ids-unique', String(items.length), String(ids.size), ids.size === items.length)
  if (ids.size !== items.length) errors.push('清单条目 ID 存在重复')

  // 逐位核对：数组顺序必须等于原文顺序（不做 sort），sourceOrdinal 连续，
  // text 与原文条目全等，逐条 sha256 与记录一致，147/13 边界与原文一致。
  const mismatches = []
  const compareLength = Math.max(items.length, entries.length)
  for (let position = 0; position < compareLength; position++) {
    const item = items[position]
    const entry = entries[position]
    if (!item || entry === undefined) {
      mismatches.push(`position:${position + 1}`)
      continue
    }
    if (item.sourceOrdinal !== position + 1 || item.text !== entry) {
      mismatches.push(`${item.id ?? `position:${position + 1}`}`)
      continue
    }
    if (sha256Hex(new TextEncoder().encode(item.text)) !== item.sha256) {
      mismatches.push(`${item.id}:hash`)
    }
  }
  const positionalPass = mismatches.length === 0 && items.length === 160 && entries.length === 160
  push(
    'items-match-original-order-and-hashes',
    '0 mismatches',
    `${mismatches.length} mismatches`,
    positionalPass,
  )
  if (mismatches.length > 0) {
    errors.push(
      `索引与锚定原文逐位不匹配：${mismatches.slice(0, 10).join(',')}${mismatches.length > 10 ? '…' : ''}`,
    )
  }

  const appendixBoundaryPass =
    items.slice(0, 147).every((item) => item.section === 'product_engineering') &&
    items.slice(147).every((item) => item.section === 'role_appendix')
  push(
    'section-boundary-147-13',
    'first 147 product, last 13 appendix',
    appendixBoundaryPass ? 'consistent' : 'inconsistent',
    appendixBoundaryPass,
  )
  if (!appendixBoundaryPass) errors.push('section 与原文 147/13 边界不一致')

  return {
    status: errors.length === 0 ? 'pass' : 'fail',
    errors,
    checks,
    summary: {
      sourceSha256: originalSha,
      total: actualCounts.total,
      checkItems: actualCounts.productEngineering,
      roleAppendixItems: actualCounts.roleAppendix,
    },
  }
}
