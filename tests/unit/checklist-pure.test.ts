import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import {
  ANCHOR_SOURCE_SHA256,
  extractOriginalEntries,
  verifySourceChecklist,
} from '../../scripts/lib/checklist.mjs'

const original = readFileSync('docs/checklists/user-review-checklist-20261024.txt')
const indexText = readFileSync('docs/checklists/source-checklist-index.json', 'utf8')
const index = JSON.parse(indexText)

function sha256(text: string) {
  return createHash('sha256').update(new TextEncoder().encode(text)).digest('hex')
}

describe('清单完整性校验（W10：锚定原文逐位核对）', () => {
  it('仓内三件套通过：原文锚点、160 逐位、147+13 边界', () => {
    const result = verifySourceChecklist(original, Buffer.from(indexText))
    expect(result.errors).toEqual([])
    expect(result.status).toBe('pass')
    expect(result.summary).toEqual({
      sourceSha256: ANCHOR_SOURCE_SHA256,
      total: 160,
      checkItems: 147,
      roleAppendixItems: 13,
    })
  })
  it('锚定原文提取 160 条且与索引顺序一致', () => {
    const entries = extractOriginalEntries(original)
    expect(entries).toHaveLength(160)
    expect(entries[0]).toBe(index.items[0].text)
    expect(entries[146]).toBe(index.items[146].text)
    expect(entries[147]).toBe(index.items[147].text)
    expect(entries[159]).toBe(index.items[159].text)
  })
  it('篡改索引条目 text 并重算其 sha256 仍被原文逐位核对拒绝', () => {
    const tampered = JSON.parse(indexText)
    expect(tampered.items[35].text).toContain('secrets')
    tampered.items[35].text = tampered.items[35].text.replace('secrets', 'SECRETS')
    tampered.items[35].sha256 = sha256(tampered.items[35].text)
    const result = verifySourceChecklist(original, Buffer.from(JSON.stringify(tampered)))
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('逐位不匹配')
  })
  it('重排索引条目顺序被拒绝（先排序号不能掩盖乱序）', () => {
    const reordered = JSON.parse(indexText)
    const swap = reordered.items[0]
    reordered.items[0] = reordered.items[1]
    reordered.items[1] = swap
    const result = verifySourceChecklist(original, Buffer.from(JSON.stringify(reordered)))
    expect(result.status).toBe('fail')
  })
  it('删除条目被计数与逐位双重拒绝（原 160 条不可静默缩减）', () => {
    const trimmed = JSON.parse(indexText)
    trimmed.items.splice(50, 1)
    const result = verifySourceChecklist(original, Buffer.from(JSON.stringify(trimmed)))
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('清单计数')
  })
  it('原文副本字节改动被锚点拒绝', () => {
    const mutated = Buffer.from(original)
    mutated[100] ^= 1
    const result = verifySourceChecklist(mutated, Buffer.from(indexText))
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('锚点')
  })
  it('索引记录的 sourceSha256 与副本不一致被拒绝', () => {
    const mismatch = JSON.parse(indexText)
    mismatch.sourceSha256 = '0'.repeat(64)
    const result = verifySourceChecklist(original, Buffer.from(JSON.stringify(mismatch)))
    expect(result.status).toBe('fail')
    expect(result.errors.join('\n')).toContain('sourceSha256')
  })
})
