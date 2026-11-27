import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import regressions from '../../packages/contracts/v2/binding-regressions.json'
import {
  acceptsBusiness3JobEvent,
  business3HelloOutcome,
  matchesBusiness3Response,
  matchesOwnershipDetail,
  validateBusiness3,
  validateV2,
  type EventBinding,
} from '../../packages/contracts/src/v2'

const profile = fixtures.business3
const actualHash = createHash('sha256')
  .update(readFileSync(new URL('../../packages/contracts/v2/registry.json', import.meta.url)))
  .digest('hex')

describe('owned ownership segment contracts', () => {
  for (const length of [2, 55, 56, 63, 64, 65, 32767, 32768])
    it(`checks actual SHA-256 against Node for ${length} raw bytes`, () => {
      const raw = Buffer.from(Array.from({ length }, (_, i) => (i * 37 + 19) % 256))
      const hash = createHash('sha256').update(raw).digest('hex')
      const params = {
        projectId: '00000000-0000-4000-8000-000000000003',
        detailRef: '00000000-0000-4000-8000-000000000004',
        documentHash: null,
        startOrdinal: 0,
        pageSize: 1,
      }
      const value = {
        detailReadVersion: 1,
        projectId: params.projectId,
        detailRef: params.detailRef,
        manifest: {
          documentKind: 'ownership-conflict',
          documentHash: hash,
          totalBytes: length,
          segmentCount: 1,
        },
        startOrdinal: 0,
        segments: [
          {
            ordinal: 0,
            byteOffset: 0,
            rawByteLength: length,
            sha256: hash,
            dataBase64: raw.toString('base64'),
          },
        ],
        nextOrdinal: null,
        complete: true,
      }
      expect(matchesOwnershipDetail(params, value)).toBe(true)
      expect(
        matchesOwnershipDetail(params, {
          ...value,
          segments: [{ ...value.segments[0], sha256: 'f'.repeat(64) }],
        }),
      ).toBe(false)
      expect(
        matchesOwnershipDetail(params, {
          ...value,
          manifest: { ...value.manifest, segmentCount: 2 },
        }),
      ).toBe(false)
      expect(matchesOwnershipDetail(params, { ...value, complete: false })).toBe(false)
      expect(
        validateV2('request', {
          kind: 'request',
          id: params.projectId,
          protocolVersion: 2,
          engineSessionId: params.detailRef,
          method: 'project.ownership.detail',
          params,
        }),
      ).toBe(false)
    })
  it('allows only correlated first/continuation pages and legitimate errors', () => {
    const sample = profile.responses.find((c) => c.name === 'named ownership page')!
    expect(matchesBusiness3Response(sample.request, sample.response, actualHash)).toBe(true)
    const error = {
      ...sample.response,
      ok: false,
      error: {
        code: 'NOT_FOUND',
        messageKey: 'resource.notFound',
        retryable: false,
        params: { resource: 'result' },
      },
    } as Record<string, unknown>
    delete error.result
    expect(matchesBusiness3Response(sample.request, error, actualHash)).toBe(true)
    expect(
      matchesBusiness3Response(
        sample.request,
        { ...error, engineSessionId: sample.request.id },
        actualHash,
      ),
    ).toBe(false)
    const forbidden = structuredClone(sample.request) as Record<string, unknown>
    forbidden.params = { ...sample.request.params, ownerId: sample.request.id }
    expect(validateBusiness3('request', forbidden)).toBe(false)
  })
})

describe('T01 business3 canonical (explicit internal opt-in, default2)', () => {
  it('binds the complete hello fixture to the actual same-build registry bytes', () => {
    expect(profile.registryHash).toBe(actualHash)
    expect(profile.profile).toBe('explicit-internal-opt-in-default2')
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
