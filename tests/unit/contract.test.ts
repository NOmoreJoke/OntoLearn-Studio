import { describe, expect, it } from 'vitest'
import { healthSchema } from '@ontolearn/contracts'
import { readEngineHealth, getEngineCommand } from '../../apps/desktop/src/main/engine'

describe('engine boundary', () => {
  it('rejects unimplemented capabilities and unexpected fields', () => {
    const valid = {
      protocolVersion: 1,
      engineVersion: '0.1.0',
      status: 'ok',
      capabilities: ['health'],
    }
    expect(healthSchema.safeParse(valid).success).toBe(true)
    expect(healthSchema.safeParse({ ...valid, capabilities: ['query'] }).success).toBe(false)
    expect(healthSchema.safeParse({ ...valid, token: 'secret' }).success).toBe(false)
    expect(healthSchema.safeParse({ ...valid, protocolVersion: 2 }).success).toBe(false)
  })
  it('uses a bundled executable rather than system Python when packaged', () => {
    const result = getEngineCommand({
      packaged: true,
      appPath: '/unused',
      resourcesPath: '/resources',
    })
    expect(result.command).toContain('engine')
    expect(result.command).toContain('ontolearn-engine')
    expect(result.args).toEqual([])
  })
})

import { isTrustedDocument } from '../../apps/desktop/src/main/trusted-document'

describe('trusted document', () => {
  it('allows local anchors without weakening document identity', () => {
    expect(isTrustedDocument('file:///app/index.html#modules', 'file:///app/index.html')).toBe(true)
    expect(isTrustedDocument('http://127.0.0.1:5173/#overview', 'http://127.0.0.1:5173')).toBe(true)
    expect(isTrustedDocument('https://evil.example/#modules', 'file:///app/index.html')).toBe(false)
    expect(isTrustedDocument('file:///app/other.html', 'file:///app/index.html')).toBe(false)
    expect(isTrustedDocument('file:///app/index.html?injected=1', 'file:///app/index.html')).toBe(
      false,
    )
  })
  it('reports a missing engine instead of claiming a healthy connection', async () => {
    await expect(
      readEngineHealth({
        packaged: true,
        appPath: '/unused',
        resourcesPath: '/ontolearn-no-such-directory',
      }),
    ).rejects.toThrow('ENGINE_UNAVAILABLE')
  })
})
