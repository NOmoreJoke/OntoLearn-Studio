import { describe, expect, it } from 'vitest'
import {
  compareCspViolations,
  type CspViolation,
  type CspViolationTuple,
} from '../helpers/csp-violation-projection'

const receiver = 'http://127.0.0.1:45123'
// Independent semantic expectations, not derived from observed events or a policy factory.
const production: CspViolationTuple[] = [
  ['script-src-elem', 'enforce', 'inline'],
  ['script-src-elem', 'enforce', 'probe-origin'],
  ['style-src-elem', 'enforce', 'inline'],
  ['style-src-attr', 'enforce', 'inline'],
  ['img-src', 'enforce', 'probe-origin'],
  ['connect-src', 'enforce', 'probe-origin'],
  ['frame-src', 'enforce', 'probe-origin'],
]
const development: CspViolationTuple[] = [
  ['script-src-elem', 'enforce', 'inline'],
  ['script-src-elem', 'enforce', 'probe-origin'],
  ['img-src', 'enforce', 'probe-origin'],
  ['connect-src', 'enforce', 'probe-origin'],
  ['frame-src', 'enforce', 'probe-origin'],
]
const productionEvents: CspViolation[] = [
  { directive: 'script-src-elem', disposition: 'enforce', blocked: 'inline' },
  {
    directive: 'script-src-elem',
    disposition: 'enforce',
    blocked: `${receiver}/script`,
  },
  { directive: 'style-src-elem', disposition: 'enforce', blocked: 'inline' },
  { directive: 'style-src-attr', disposition: 'enforce', blocked: 'inline' },
  {
    directive: 'img-src',
    disposition: 'enforce',
    blocked: `${receiver}/image`,
  },
  {
    directive: 'connect-src',
    disposition: 'enforce',
    blocked: `${receiver}/fetch`,
  },
  { directive: 'frame-src', disposition: 'enforce', blocked: `${receiver}/` },
]
const developmentEvents: CspViolation[] = [
  { directive: 'script-src-elem', disposition: 'enforce', blocked: 'inline' },
  {
    directive: 'script-src-elem',
    disposition: 'enforce',
    blocked: `${receiver}/script`,
  },
  {
    directive: 'img-src',
    disposition: 'enforce',
    blocked: `${receiver}/image`,
  },
  {
    directive: 'connect-src',
    disposition: 'enforce',
    blocked: `${receiver}/fetch`,
  },
  { directive: 'frame-src', disposition: 'enforce', blocked: receiver },
]

function formerPresenceCheck(events: readonly CspViolation[]): boolean {
  return ['script-src-elem', 'img-src', 'connect-src', 'frame-src'].every((directive) =>
    events.some((event) => event.directive === directive && event.disposition === 'enforce'),
  )
}

describe.each([
  { mode: 'production', expected: production, events: productionEvents },
  { mode: 'development', expected: development, events: developmentEvents },
])('$mode CSP semantic projection', ({ expected, events }) => {
  it('matches the complete independent set, regardless of event order', () => {
    const result = compareCspViolations([...events].reverse(), receiver, expected)
    expect(result.matches).toBe(true)
    expect(result.missing).toEqual([])
    expect(result.extra).toEqual([])
    expect(result.counts.map(({ tuple }) => tuple)).toEqual(expect.arrayContaining(expected))
  })

  it.each(expected.map((tuple, index) => ({ tuple, index })))(
    'reports the precise missing tuple $tuple',
    ({ tuple, index }) => {
      const result = compareCspViolations(
        events.filter((_, i) => i !== index),
        receiver,
        expected,
      )
      expect(result.matches).toBe(false)
      expect(result.missing).toEqual([tuple])
      expect(result.extra).toEqual([])
    },
  )

  it('allows identical semantic repeats while retaining all raw records and counts', () => {
    const repeated = [...events, { ...events[1] }, { ...events[1], blocked: `${receiver}/other` }]
    const result = compareCspViolations(repeated, receiver, expected)
    expect(result.matches).toBe(true)
    expect(result.raw).toEqual(repeated)
    expect(result.raw).not.toBe(repeated)
    expect(result.raw[0]).not.toBe(repeated[0])
    expect(
      result.counts.find(({ tuple }) => JSON.stringify(tuple) === JSON.stringify(expected[1])),
    ).toEqual({ tuple: expected[1], count: 3 })
    expect(result.counts.reduce((sum, { count }) => sum + count, 0)).toBe(repeated.length)
    expect(result.counts).toHaveLength(expected.length)
  })
})

describe('unexpected CSP evidence and former weak-predicate counterexamples', () => {
  it.each([
    {
      directive: 'worker-src',
      disposition: 'enforce',
      blocked: `${receiver}/worker`,
    },
    {
      directive: 'img-src',
      disposition: 'report',
      blocked: `${receiver}/image`,
    },
    {
      directive: 'img-src',
      disposition: 'enforce',
      blocked: 'http://127.0.0.1:45124/image',
    },
    {
      directive: 'img-src',
      disposition: 'enforce',
      blocked: 'http://127.0.0.1.evil.example:45123/image',
    },
    {
      directive: 'img-src',
      disposition: 'enforce',
      blocked: `${receiver}@evil.example/image`,
    },
    { directive: 'img-src', disposition: 'enforce', blocked: '' },
    { directive: 'img-src', disposition: 'enforce', blocked: 'INLINE' },
    {
      directive: 'img-src',
      disposition: 'enforce',
      blocked: 'data:text/plain,unexpected',
    },
  ])('retains and rejects an extra semantic record: %j', (unexpected) => {
    const events = [...productionEvents, unexpected, { ...unexpected }]
    expect(formerPresenceCheck(events)).toBe(true)
    const result = compareCspViolations(events, receiver, production)
    const classification = unexpected.blocked.startsWith(`${receiver}/`)
      ? 'probe-origin'
      : `unexpected:${JSON.stringify(unexpected.blocked)}`
    const tuple: CspViolationTuple = [unexpected.directive, unexpected.disposition, classification]
    expect(result.matches).toBe(false)
    expect(result.missing).toEqual([])
    expect(result.extra).toEqual([tuple])
    expect(result.raw.slice(-2)).toEqual([unexpected, unexpected])
    expect(
      result.counts.find((entry) => JSON.stringify(entry.tuple) === JSON.stringify(tuple)),
    ).toEqual({ tuple, count: 2 })
  })

  it.each([
    { index: 0, blocked: `${receiver}/script`, missing: production[0] },
    { index: 1, blocked: 'inline', missing: production[1] },
  ])('distinguishes inline and external script classes: %j', ({ index, blocked, missing }) => {
    const events = productionEvents.map((event, i) => (i === index ? { ...event, blocked } : event))
    expect(formerPresenceCheck(events)).toBe(true)
    const result = compareCspViolations(events, receiver, production)
    expect(result.matches).toBe(false)
    expect(result.missing).toEqual([missing])
    expect(result.extra).toEqual([])
  })

  it('does not accept a report disposition in place of an enforce tuple', () => {
    const events = productionEvents.map((event, i) =>
      i === 4 ? { ...event, disposition: 'report' } : event,
    )
    const result = compareCspViolations(events, receiver, production)
    expect(result.missing).toEqual([['img-src', 'enforce', 'probe-origin']])
    expect(result.extra).toEqual([['img-src', 'report', 'probe-origin']])
    expect(result.matches).toBe(false)
  })

  it('normalizes receiver paths and frame origin spelling without claiming resource-path identity', () => {
    for (const blocked of [receiver, `${receiver}/`, `${receiver}/different-path?x=1`]) {
      const events = developmentEvents.map((event, i) => (i === 4 ? { ...event, blocked } : event))
      expect(compareCspViolations(events, `${receiver}/context#probe`, development).matches).toBe(
        true,
      )
    }
  })

  it('retains unexpected raw strings as distinct unambiguous tuple keys', () => {
    const events = ['a|b', 'a,b', 'a"b', 'unexpected:'].map((blocked) => ({
      directive: 'unknown',
      disposition: 'unknown',
      blocked,
    }))
    const result = compareCspViolations(events, receiver, [])
    expect(result.raw).toEqual(events)
    expect(result.extra).toEqual(
      events.map((event) => ['unknown', 'unknown', `unexpected:${JSON.stringify(event.blocked)}`]),
    )
    expect(result.counts).toHaveLength(events.length)
    expect(result.matches).toBe(false)
  })

  it('rejects a duplicate expected tuple instead of hiding an oracle mistake', () => {
    expect(() =>
      compareCspViolations(productionEvents, receiver, [...production, production[0]]),
    ).toThrow('DUPLICATE_EXPECTED_CSP_TUPLE')
  })

  it.each(['not a URL', 'file:///opaque'])('rejects an invalid receiver context %s', (value) => {
    expect(() => compareCspViolations([], value, [])).toThrow()
  })
})
