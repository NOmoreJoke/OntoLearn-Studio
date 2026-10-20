import { describe, expect, it } from 'vitest'
import { JsonlReader, parseStrictJson } from '../../apps/desktop/src/main/jsonl'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import rawFixtures from '../../packages/contracts/v2/frame-fixtures.json'
import { validateV2 } from '@ontolearn/contracts/v2'

function reader(max = 262144) {
  const frames: unknown[] = []
  const errors: string[] = []
  const stream = new JsonlReader(
    (v) => frames.push(v),
    (e) => errors.push(e),
    max,
  )
  return { stream, frames, errors }
}
describe('strict raw JSONL reader', () => {
  it.each(rawFixtures.cases)('consumes shared raw frame corpus: $name', (test) => {
    const { stream, frames, errors } = reader('maxBytes' in test ? test.maxBytes : undefined)
    for (const chunk of test.chunks) stream.push(Buffer.from(chunk, 'hex'))
    if (test.end) stream.end()
    expect(frames).toEqual(test.expectedFrames)
    expect(errors).toEqual(test.expectedErrors)
    expect(stream.terminal).toBe(test.terminal)
    expect(stream.bufferedBytes).toBe(0)
  })
  it('reads split multibyte UTF-8, CRLF, and multiple frames from one chunk', () => {
    const { stream, frames, errors } = reader()
    const bytes = Buffer.from('{"值":"汉😀"}\r\n[1,true]\n')
    for (const byte of bytes.subarray(0, 13)) stream.push(Buffer.from([byte]))
    stream.push(bytes.subarray(13))
    expect(frames).toEqual([{ 值: '汉😀' }, [1, true]])
    expect(errors).toEqual([])
    expect(stream.bufferedBytes).toBe(0)
  })
  it('bounds unfinished frame bytes before copying and discards every terminal chunk', () => {
    const { stream, frames, errors } = reader(8)
    stream.push(Buffer.from('12345678'))
    expect(stream.bufferedBytes).toBe(8)
    stream.push(Buffer.alloc(1000000, 65))
    expect(stream.bufferedBytes).toBe(0)
    expect(stream.terminal).toBe(true)
    for (let n = 0; n < 5; n++) stream.push(Buffer.alloc(1000000, 65))
    stream.push(Buffer.from('{}\n'))
    expect(frames).toEqual([])
    expect(errors).toEqual(['frame'])
  })
  it('limits each frame separately instead of the total chunk', () => {
    const { stream, frames, errors } = reader(2)
    stream.push(Buffer.from('{}\n[]\n{}\n'))
    expect(frames).toEqual([{}, [], {}])
    expect(errors).toEqual([])
  })
  it.each([
    '',
    ' ',
    '\uFEFF{}',
    '{"a":1,"a":2}',
    '{"x":{"a":1,"\\u0061":2}}',
    '[{"x":1,"x":2}]',
    '{"a":NaN}',
    '1e999',
    '9007199254740992',
    '01',
    '{}{}',
    '{"x":"\\ud800"}',
    '{"x":"a\u0001"}',
    '[1,]',
    '{"x":1,}',
    '[',
  ])('rejects malformed or ambiguous JSON %j', (text) => {
    const { stream, errors, frames } = reader()
    stream.push(Buffer.from(text + '\n{}\n'))
    expect(errors).toEqual(['json'])
    expect(frames).toEqual([])
    expect(stream.bufferedBytes).toBe(0)
  })
  it('rejects invalid UTF-8 and unfinished input on EOF', () => {
    const invalid = reader()
    invalid.stream.push(Buffer.from([0xc3, 0x28, 10]))
    expect(invalid.errors).toEqual(['json'])
    const unfinished = reader()
    unfinished.stream.push(Buffer.from('{}'))
    unfinished.stream.end()
    expect(unfinished.errors).toEqual(['json'])
  })
  it('accepts 32 nested containers and rejects the 33rd', () => {
    expect(() => parseStrictJson('['.repeat(32) + '0' + ']'.repeat(32))).not.toThrow()
    expect(() => parseStrictJson('['.repeat(33) + '0' + ']'.repeat(33))).toThrow()
  })
  it('preserves prototype-looking keys as data without prototype mutation', () => {
    expect(parseStrictJson('{"__proto__":{"polluted":true}}')).toEqual({
      ['__proto__']: { polluted: true },
    })
    expect(Object.hasOwn({}, 'polluted')).toBe(false)
  })
  it('consumes the canonical public positive and negative decoded fixtures', () => {
    for (const test of fixtures.cases) {
      const { stream, errors, frames } = reader()
      stream.push(Buffer.from(JSON.stringify(test.value) + '\n'))
      expect(errors, test.name).toEqual([])
      expect(validateV2(test.schema, frames[0]), test.name).toBe(test.valid)
    }
  })
  it('stops after a consumer error and releases the partial buffer', () => {
    const errors: string[] = []
    const stream = new JsonlReader(
      () => {
        throw new Error('private data')
      },
      (e) => errors.push(e),
    )
    stream.push(Buffer.from('{}\n{}\n'))
    expect(errors).toEqual(['json'])
    expect(stream.bufferedBytes).toBe(0)
  })
})
