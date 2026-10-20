import { describe, expect, it } from 'vitest'
import { contentSecurityPolicy } from '../../apps/desktop/src/csp'

describe('CSP delivery variants', () => {
  it('restricts production scripts, connections and frames', () => {
    const policy = contentSecurityPolicy()
    expect(policy).toContain("script-src 'self';")
    expect(policy).toContain("connect-src 'none'")
    expect(policy).toContain("frame-src 'none'")
    expect(policy).not.toMatch(/unsafe|nonce|localhost|127\.0\.0\.1/)
  })
  it('allows only the fixed loopback development origin with a valid nonce', () => {
    const policy = contentSecurityPolicy({ nonce: 'Abc123+/=', origin: 'http://127.0.0.1:5173' })
    expect(policy).toContain("'nonce-Abc123+/='")
    expect(policy).toContain('ws://127.0.0.1:5173')
    expect(() =>
      contentSecurityPolicy({ nonce: "a'; unsafe", origin: 'http://127.0.0.1:5173' }),
    ).toThrow()
    expect(() => contentSecurityPolicy({ nonce: 'abc', origin: 'https://evil.example' })).toThrow()
  })
})
