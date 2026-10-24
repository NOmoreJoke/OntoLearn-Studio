/** Actual component + real React SSR. No engine, IPC, browser, or GUI evidence. */
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'

import {
  OwnershipConflictDetailView,
  type OwnershipConflictDetailViewModel,
} from '../../apps/desktop/src/renderer/src/ontology/OwnershipConflictDetailView'

const existing = {
  role: 'existing' as const,
  id: '  historical:original-id  ',
  owner: ' mapping:raw-owner ',
  sourceRow: ' sheet A!0007 ',
  slot: { subject: '<urn:raw:subject>', predicate: '<urn:raw:predicate>' },
}
const incoming = {
  role: 'incoming' as const,
  id: 'incoming:original-id',
  owner: null,
  sourceRow: null,
  slot: { subject: '<urn:incoming:subject>', predicate: '<urn:incoming:predicate>' },
}
const render = (viewModel: OwnershipConflictDetailViewModel) =>
  renderToStaticMarkup(createElement(OwnershipConflictDetailView, { viewModel }))
const escaped = (text: string) =>
  renderToStaticMarkup(createElement('span', null, text)).slice(6, -7)

describe('OwnershipConflictDetailView: validated private presentation data', () => {
  it.each([
    ['reservedIdentity', '保留身份冲突'],
    ['sameStatement', '相同事实的来源冲突'],
    ['singleSlot', '单值属性槽位冲突'],
  ] as const)(
    '%s displays both original locations and the preview base revision',
    (reason, label) => {
      const html = render({ previewBaseRevision: 27, reason, records: [existing, incoming] })
      expect(html).toContain('<h2>首个阻断冲突定位</h2>')
      expect(html).toContain('<dt>预览基准修订</dt><dd>27</dd>')
      expect(html).toContain(label)
      expect(html).toContain('<h3>现有记录</h3>')
      expect(html).toContain('<h3>传入记录</h3>')
      for (const record of [existing, incoming]) {
        for (const value of [record.id, record.slot.subject, record.slot.predicate]) {
          expect(html).toContain(escaped(value))
        }
      }
      expect(html).toContain(escaped(existing.owner))
      expect(html).toContain(escaped(existing.sourceRow))
      expect(html).toContain('人工（owner = null）')
      expect(html).toContain('无源行（sourceRow = null）')
      expect(html).not.toContain('冲突声明')
      expect(html).not.toContain('全部冲突')
      expect(html).not.toContain('已提交')
    },
  )

  it('singleDeclaration shows the actual declaration and two existing records, without incoming', () => {
    const declaration = {
      layer: 'ontology' as const,
      id: ' original declaration ID ',
      predicate: existing.slot.predicate,
    }
    const second = { ...existing, id: 'second:existing', owner: null, sourceRow: null }
    const html = render({
      previewBaseRevision: 28,
      reason: 'singleDeclaration',
      declaration,
      records: [existing, second],
    })
    expect(html).toContain('单值属性声明与现有事实冲突')
    expect(html).toContain('<h3>冲突声明</h3>')
    for (const value of Object.values(declaration)) expect(html).toContain(escaped(value))
    expect(html.match(/<h3>现有记录<\/h3>/g)).toHaveLength(2)
    expect(html).toContain(existing.id)
    expect(html).toContain(second.id)
    expect(html).not.toContain('传入记录')
    expect(html).not.toContain(incoming.id)
    expect(html.match(/&lt;urn:raw:subject&gt;/g)).toHaveLength(2)
    expect(html.match(/&lt;urn:raw:predicate&gt;/g)).toHaveLength(3)
  })

  it('retains a historical ID over 16 KiB without normalization, truncation, or IRI inference', () => {
    const id = `  historical-not-an-iri:${'a'.repeat(17 * 1024)}:END  `
    const html = render({
      previewBaseRevision: 0,
      reason: 'reservedIdentity',
      records: [{ ...existing, id }, incoming],
    })
    expect(Buffer.byteLength(id)).toBeGreaterThan(16 * 1024)
    expect(html).toContain(`>${id}</code>`)
    expect(html).toContain('white-space:pre-wrap;overflow-wrap:anywhere')
    expect(html).not.toContain('…')
    expect(html).not.toContain('href=')
  })

  it('renders HTML-like values only as escaped text in every original and declaration field', () => {
    const hostile = '<script>alert("x")</script><img src=x onerror="bad()">&\' javascript:bad()'
    const html = render({
      previewBaseRevision: 29,
      reason: 'singleDeclaration',
      declaration: { layer: 'ontology', id: hostile, predicate: hostile },
      records: [
        {
          ...existing,
          id: hostile,
          owner: hostile,
          sourceRow: hostile,
          slot: { subject: hostile, predicate: hostile },
        },
        { ...existing, id: 'second:existing' },
      ],
    })
    expect(html.split(escaped(hostile))).toHaveLength(8)
    expect(html).not.toContain(hostile)
    expect(html).not.toMatch(/<(?:script|img|a|iframe)\b/i)
    expect(html).not.toMatch(/<[^>]*\s(?:href|src|onerror)=/i)
  })

  it('is a readonly display with no write, confirmation, or automatic operation surface', () => {
    const records = Object.freeze([
      Object.freeze({ ...existing, slot: Object.freeze({ ...existing.slot }) }),
      Object.freeze({ ...incoming, slot: Object.freeze({ ...incoming.slot }) }),
    ])
    const model = Object.freeze({
      previewBaseRevision: 30,
      reason: 'sameStatement' as const,
      records,
    })
    const before = JSON.stringify(model)
    const html = render(model)
    expect(JSON.stringify(model)).toBe(before)
    expect(render(model)).toBe(html)
    expect(html).not.toMatch(/<(?:button|input|form|a|script|iframe)\b/i)
    expect(html).not.toMatch(/确认|提交|写入|自动执行|chunk|hash|detailRef/)
  })
})
