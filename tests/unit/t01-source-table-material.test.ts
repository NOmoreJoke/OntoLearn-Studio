import { createHash } from 'node:crypto'
import { describe, expect, it, vi } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { sourceTableDigest, sourceTableMaterial } from '../../packages/contracts/src/v2'

interface Input {
  table: unknown
  options: unknown
  implementation: unknown
  expectedSourceHash: unknown
  maxEncodedBytes: unknown
}
interface Table {
  source_hash: string
  sheet: string
  fields: string[]
  rows: Array<{ number: number; cells: Array<{ text: unknown; kind: unknown }> }>
}
const corpus = fixtures.sourceTable
const base = corpus.cases[0]
const input = () => structuredClone(base)
const args = (c: Input): Parameters<typeof sourceTableMaterial> => [
  c.table,
  c.options,
  c.implementation,
  c.expectedSourceHash as string,
  c.maxEncodedBytes as number,
]
const hash = (bytes: Uint8Array) => createHash('sha256').update(bytes).digest('hex')

describe('T01 complete source-table material (synthetic producer only)', () => {
  for (const c of corpus.cases)
    it(c.name, async () => {
      const before = JSON.stringify(c)
      if (!c.valid) expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
      else {
        const bytes = sourceTableMaterial(...args(c))
        expect(Array.from(bytes)).toEqual(Array.from(new TextEncoder().encode(c.material!)))
        expect(bytes.length).toBe(c.encodedBytes)
        expect(hash(bytes)).toBe(c.sha256)
        expect(await sourceTableDigest(...args(c))).toEqual({
          sha256: c.sha256,
          encodedBytes: c.encodedBytes,
        })
        expect(
          hash(sourceTableMaterial(...args({ ...c, maxEncodedBytes: c.encodedBytes! + 1 }))),
        ).toBe(c.sha256)
        expect(() =>
          sourceTableMaterial(...args({ ...c, maxEncodedBytes: c.encodedBytes! - 1 })),
        ).toThrow('INVALID_REQUEST')
      }
      expect(JSON.stringify(c)).toBe(before)
    })

  it('binds all five explicit encoding choices and every identity field', () => {
    const encoding = corpus.cases.filter((c) => c.name.startsWith('explicit encoding '))
    expect(encoding).toHaveLength(5)
    expect(new Set(encoding.map((c) => c.sha256)).size).toBe(5)
    for (const name of [
      'all tail cells retained',
      'source identity changes',
      'execution semantics changes',
      'engine version changes',
      'whole lock changes',
      'physical row gaps retained',
      'field order exact',
    ])
      expect(corpus.cases.find((c) => c.name === name)!.sha256).not.toBe(base.sha256)
    const empty = corpus.cases.filter((c) => c.name.startsWith('empty text distinct kind '))
    expect(new Set(empty.map((c) => c.sha256)).size).toBe(2)
  })

  it('encodes a complete material larger than the single-frame wire budget', () => {
    const c = input()
    c.table = {
      source_hash: 'e'.repeat(64),
      sheet: 'CSV',
      fields: ['a', 'b', 'c'],
      rows: [
        {
          number: 2,
          cells: Array.from({ length: 3 }, () => ({ text: '汉'.repeat(32768), kind: 'string' })),
        },
      ],
    } as typeof c.table
    c.expectedSourceHash = 'e'.repeat(64)
    c.maxEncodedBytes = corpus.large.encodedBytes
    const bytes = sourceTableMaterial(...args(c))
    expect(bytes.length).toBe(corpus.large.encodedBytes)
    expect(bytes.length).toBeGreaterThan(262144)
    expect(hash(bytes)).toBe(corpus.large.sha256)
  })

  for (const where of ['table', 'options', 'implementation', 'row', 'cell', 'array-index'])
    it(`rejects ${where} accessor without invoking it`, () => {
      const c = input()
      const t = c.table as unknown as Table
      const targets: Record<string, [object, string]> = {
        table: [t, 'sheet'],
        options: [c.options, 'format'],
        implementation: [c.implementation, 'engineVersion'],
        row: [t.rows[0], 'number'],
        cell: [t.rows[0].cells[0], 'text'],
        'array-index': [t.rows, '0'],
      }
      const getter = vi.fn(() => {
        t.rows[0].cells[1].text = 'changed by callback'
        return 'x'
      })
      const [target, key] = targets[where]
      Object.defineProperty(target, key, { get: getter, enumerable: true })
      expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
      expect(getter).not.toHaveBeenCalled()
    })

  for (const callback of ['toJSON', 'valueOf', 'toString', Symbol.iterator])
    it(`rejects own callback ${String(callback)} without invoking it`, () => {
      const c = input()
      const fn = vi.fn(() => 'unexpected')
      Object.defineProperty(c.table, callback, { value: fn, enumerable: true })
      expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
      expect(fn).not.toHaveBeenCalled()
    })

  it('rejects holes, hidden fields, array subclasses and scalar host objects', () => {
    const variants = [input(), input(), input(), input()]
    delete (variants[0].table as unknown as Table).rows[0]
    Object.defineProperty(variants[1].table, 'hidden', { value: true })
    class HostArray extends Array {}
    const host = new HostArray()
    host.push('id', 'name')
    ;(variants[2].table as unknown as Table).fields = host
    const valueOf = vi.fn(() => 2)
    ;(variants[3].table as unknown as Table).rows[0].number = { valueOf } as unknown as number
    for (const c of variants)
      expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
    expect(valueOf).not.toHaveBeenCalled()
  })

  it('encodes only private captured values when caller objects change during output', () => {
    const c = input()
    const original = TextEncoder.prototype.encodeInto
    let changed = false
    const spy = vi.spyOn(TextEncoder.prototype, 'encodeInto').mockImplementation(function (
      this: TextEncoder,
      text,
      dest,
    ) {
      if (!changed) {
        changed = true
        ;(c.table as unknown as Table).rows[0].cells[0].text = '\ud800'
        c.options.encoding = 'big5'
        c.implementation.engineVersion = 'caller-changed'
      }
      return original.call(this, text, dest)
    })
    try {
      const bytes = sourceTableMaterial(...args(c))
      expect(changed).toBe(true)
      expect(hash(bytes)).toBe(base.sha256)
    } finally {
      spy.mockRestore()
    }
  })

  it('finishes material capture before the asynchronous digest and later caller edits', async () => {
    const c = input()
    const result = sourceTableDigest(...args(c))
    ;(c.table as unknown as Table).fields[0] = 'changed'
    c.implementation.dependencyLockHash = 'f'.repeat(64)
    expect(await result).toEqual({ sha256: base.sha256, encodedBytes: base.encodedBytes })
  })

  it('stops a long unbounded sheet before escaping or encoding that scalar', () => {
    const c = input()
    const sheet = '汉'.repeat(1_000_000)
    ;(c.table as unknown as Table).sheet = sheet
    c.options = { format: 'xlsx', encoding: null, sheet } as typeof c.options
    c.maxEncodedBytes = 400
    const original = JSON.stringify
    let escapedLong = false
    const spy = vi.spyOn(JSON, 'stringify').mockImplementation((...values) => {
      if (values[0] === sheet) escapedLong = true
      return original(...values)
    })
    try {
      expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
      expect(escapedLong).toBe(false)
    } finally {
      spy.mockRestore()
    }
  })

  it('rejects invalid Unicode, safe-integer boundaries and field/row/text limits', () => {
    const mutations: Array<(t: Table) => void> = [
      (t) => {
        t.fields[0] = '\ud800'
      },
      (t) => {
        t.rows[0].cells[0].text = '\udfff'
      },
      (t) => {
        t.rows[0].number = Number.NaN
      },
      (t) => {
        t.rows[0].number = Number.POSITIVE_INFINITY
      },
      (t) => {
        t.rows[0].number = Number.MAX_SAFE_INTEGER + 1
      },
      (t) => {
        t.fields = Array.from({ length: 257 }, (_, i) => `f${i}`)
      },
      (t) => {
        t.rows = Array.from({ length: 50001 }, () => t.rows[0])
      },
      (t) => {
        t.rows[0].cells[0].text = 'x'.repeat(32769)
      },
      (t) => {
        t.fields[0] = 'x'.repeat(32769)
      },
    ]
    for (const mutate of mutations) {
      const c = input()
      c.maxEncodedBytes = 2_000_000
      mutate(c.table as unknown as Table)
      expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
    }
  })

  it('does not claim hostile Proxy reflection can be identified without running traps', () => {
    const c = input()
    const trap = vi.fn(() => {
      throw new Error('host-only detail')
    })
    c.table = new Proxy(c.table, { ownKeys: trap })
    expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
    expect(trap).toHaveBeenCalled()
  })

  for (const name of ['fields-256', 'rows-50000', 'nonbmp-32768'] as const)
    it(`accepts the full upper boundary ${name} with a fixed independent oracle`, () => {
      const c = input()
      const table: Table = { source_hash: 'e'.repeat(64), sheet: 'CSV', fields: ['v'], rows: [] }
      if (name === 'fields-256') table.fields = Array.from({ length: 256 }, (_, i) => `f${i}`)
      else if (name === 'rows-50000')
        table.rows = Array.from({ length: 50000 }, (_, i) => ({
          number: i + 2,
          cells: [{ text: String(i), kind: 'string' }],
        }))
      else table.rows = [{ number: 2, cells: [{ text: '𐀀'.repeat(32768), kind: 'string' }] }]
      c.table = table as typeof c.table
      c.expectedSourceHash = table.source_hash
      c.maxEncodedBytes = corpus.generated[name].encodedBytes
      const bytes = sourceTableMaterial(...args(c))
      expect(bytes.length).toBe(corpus.generated[name].encodedBytes)
      expect(hash(bytes)).toBe(corpus.generated[name].sha256)
      expect(() =>
        sourceTableMaterial(...args({ ...c, maxEncodedBytes: bytes.length - 1 })),
      ).toThrow('INVALID_REQUEST')
    })

  for (const cp of corpus.blankFieldCodePoints)
    it(`rejects the exact Python whitespace field U+${cp.toString(16)}`, () => {
      const c = input()
      ;(c.table as unknown as Table).fields[0] = String.fromCodePoint(cp)
      expect(() => sourceTableMaterial(...args(c))).toThrow('INVALID_REQUEST')
    })

  for (const c of corpus.budgetJsonTokens)
    it(`shares the JSON budget value semantics ${c.token}`, () => {
      const candidate = { ...input(), maxEncodedBytes: JSON.parse(c.token) as unknown }
      if (c.valid) expect(hash(sourceTableMaterial(...args(candidate)))).toBe(base.sha256)
      else expect(() => sourceTableMaterial(...args(candidate))).toThrow('INVALID_REQUEST')
    })
})
