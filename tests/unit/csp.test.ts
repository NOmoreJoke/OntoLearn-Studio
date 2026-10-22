import { describe, expect, it } from 'vitest'
import { contentSecurityPolicy } from '../../apps/desktop/src/csp'

type PolicyOracle = Record<string, readonly string[]>

// Independent acceptance literals: do not obtain expected values from the factory.
const production: PolicyOracle = {
  'default-src': ["'self'"],
  'script-src': ["'self'"],
  'style-src': ["'self'"],
  'img-src': ["'self'", 'data:'],
  'connect-src': ["'none'"],
  'object-src': ["'none'"],
  'base-uri': ["'none'"],
  'frame-src': ["'none'"],
  'form-action': ["'none'"],
}

function development(nonce: string): PolicyOracle {
  return {
    'default-src': ["'self'"],
    'script-src': ["'self'", `'nonce-${nonce}'`],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", 'data:'],
    'connect-src': ['http://127.0.0.1:5173', 'ws://127.0.0.1:5173'],
    'object-src': ["'none'"],
    'base-uri': ["'none'"],
    'frame-src': ["'none'"],
    'form-action': ["'none'"],
  }
}

function ordered(rows: string[][]): string[][] {
  // Preserve every directive and token occurrence; sorting never deduplicates.
  return rows
    .map(([name, ...sources]) => [name, ...sources.sort()])
    .sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)))
}

function assertPolicy(policy: string, expected: PolicyOracle): void {
  const actual = policy
    .split(';')
    .map((directive) => directive.trim())
    .filter(Boolean)
    .map((directive) => directive.split(/\s+/))
  expect(ordered(actual)).toEqual(
    ordered(Object.entries(expected).map(([name, sources]) => [name, ...sources])),
  )
}

const origin = 'http://127.0.0.1:5173'
const nonce = 'Abc123+/='

describe('CSP delivery variants', () => {
  it('matches all production directives and source occurrences', () => {
    assertPolicy(contentSecurityPolicy(), production)
  })

  it.each(['Abc123+/=', '_-A2='])('matches the exact supplied development nonce %s', (value) => {
    assertPolicy(contentSecurityPolicy({ nonce: value, origin }), development(value))
  })

  it('changes only the corresponding script nonce token for two valid inputs', () => {
    const first = contentSecurityPolicy({ nonce, origin })
    const secondNonce = '_-A2='
    const second = contentSecurityPolicy({ nonce: secondNonce, origin })
    assertPolicy(first, development(nonce))
    assertPolicy(second, development(secondNonce))
    expect(second).toBe(first.replace(`'nonce-${nonce}'`, `'nonce-${secondNonce}'`))
  })

  it.each([`${origin}/`, `${origin}/hmr/path?version=2#module`])(
    'accepts and normalizes the existing same-origin contract: %s',
    (value) => assertPolicy(contentSecurityPolicy({ nonce, origin: value }), development(nonce)),
  )

  it.each(['', "a'; unsafe", 'a b', 'a\nb'])('rejects invalid nonce %j', (value) => {
    expect(() => contentSecurityPolicy({ nonce: value, origin })).toThrow()
  })

  it.each([
    'http://localhost:5173',
    'http://127.0.0.1:5174',
    'https://127.0.0.1:5173',
    'https://evil.example',
  ])('rejects an origin outside the existing fixed loopback contract: %s', (value) => {
    expect(() => contentSecurityPolicy({ nonce, origin: value })).toThrow()
  })
})

describe('independent policy oracle counterexamples', () => {
  const literal = Object.entries(production)
    .map(([name, sources]) => `${name} ${sources.join(' ')}`)
    .join('; ')

  it('ignores directive/source order and insignificant whitespace without losing multiplicity', () => {
    const reordered = Object.entries(production)
      .reverse()
      .map(([name, sources]) => `  ${name}\t${[...sources].reverse().join('  ')}  `)
      .join(';')
    assertPolicy(`${reordered};`, production)
  })

  it.each(Object.keys(production))('rejects missing directive %s', (name) => {
    const missing = literal
      .split('; ')
      .filter((part) => !part.startsWith(`${name} `))
      .join('; ')
    expect(() => assertPolicy(missing, production)).toThrow()
  })

  it.each(Object.keys(production))('rejects a changed source on %s', (name) => {
    const changed = literal
      .split('; ')
      .map((part) => (part.startsWith(`${name} `) ? `${name} https://unexpected.example` : part))
      .join('; ')
    expect(() => assertPolicy(changed, production)).toThrow()
  })

  it.each([
    ['extra directive', `${literal}; worker-src 'none'`],
    ['duplicate directive', `${literal}; script-src 'self'`],
    ['duplicate conflicting directive', `${literal}; script-src 'unsafe-eval'`],
    [
      'duplicate source token',
      literal.replace("img-src 'self' data:", "img-src 'self' data: data:"),
    ],
  ])('rejects %s instead of overwriting or deduplicating', (_label, policy) => {
    expect(() => assertPolicy(policy, production)).toThrow()
  })

  it.each(["'unsafe-inline'", "'unsafe-eval'"])(
    'rejects development script token %s missed by the former text predicates',
    (token) => {
      const changed = contentSecurityPolicy({ nonce, origin }).replace(
        `'nonce-${nonce}'`,
        `'nonce-${nonce}' ${token}`,
      )
      // Static policy-string counterexample only; no browser execution is inferred.
      expect(changed).toContain("'nonce-Abc123+/='")
      expect(changed).toContain('ws://127.0.0.1:5173')
      expect(() => assertPolicy(changed, development(nonce))).toThrow()
    },
  )

  it('detects form-action removal missed by the former production predicates', () => {
    const changed = contentSecurityPolicy().replace("; form-action 'none'", '')
    expect(changed).toContain("script-src 'self';")
    expect(changed).toContain("connect-src 'none'")
    expect(changed).toContain("frame-src 'none'")
    expect(changed).not.toMatch(/unsafe|nonce|localhost|127\.0\.0\.1/)
    expect(() => assertPolicy(changed, production)).toThrow()
  })
})
