import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import regressions from '../../packages/contracts/v2/binding-regressions.json'
import {
  acceptsBusiness3JobEvent,
  business3HelloOutcome,
  matchesBusiness3Response,
  validateBusiness3,
  validateV2,
  type EventBinding,
} from '../../packages/contracts/src/v2'

const profile = fixtures.business3
const actualHash = createHash('sha256')
  .update(readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)))
  .digest('hex')

describe('T01 business3 canonical foundation (runtime disabled)', () => {
  it('binds the complete hello fixture to the actual same-build registry bytes', () => {
    expect(profile.registryHash).toBe(actualHash)
    expect(profile.profile).toBe('validator-only-runtime-disabled')
  })
  for (const c of profile.cases)
    it(`schema: ${c.name}`, () => {
      expect(validateBusiness3(c.schema, c.value)).toBe(c.valid)
    })
  for (const c of profile.hello)
    it(`hello: ${c.name}`, () => {
      const before = JSON.stringify(c)
      expect(business3HelloOutcome(c.request, c.response, actualHash)).toBe(c.outcome)
      expect(JSON.stringify(c)).toBe(before)
    })
  for (const c of profile.responses)
    it(`binding: ${c.name}`, () => {
      const before = JSON.stringify(c)
      expect(matchesBusiness3Response(c.request, c.response, actualHash)).toBe(c.valid)
      expect(JSON.stringify(c)).toBe(before)
    })
  for (const c of [...profile.routing, ...regressions.business3])
    it(`routing: ${c.name}`, () => {
      expect(acceptsBusiness3JobEvent(c.value, c.binding as unknown as EventBinding)).toBe(c.valid)
    })
  it('keeps production v2 project and envelope validation strict', () => {
    for (const c of profile.cases.filter((c) => c.valid && c.value.protocolVersion === 3))
      expect(validateV2('envelope', c.value)).toBe(false)
    expect(validateBusiness3('not-registered', {})).toBe(false)
    expect(matchesBusiness3Response(null, {}, actualHash)).toBe(false)
    expect(business3HelloOutcome({}, null, actualHash)).toBe('invalid-close')
  })
})
