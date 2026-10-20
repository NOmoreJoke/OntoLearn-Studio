import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import bindings from '../../packages/contracts/v2/binding-regressions.json'
import errors from '../../packages/contracts/v2/errors.json'
import schema from '../../packages/contracts/v2/schema.json'
import {
  isModelMethod,
  matchesModelResult,
  validateModelParams,
  validateModelReply,
  validateModelResult,
  validateModelValue,
  validateV2,
  v2Registry,
} from '../../packages/contracts/src/v2'
import {
  modelGatewayError,
  modelGatewayErrorCodeMap,
  modelInvalidRequestError,
  safeError,
} from '../../packages/contracts/src/index'

const id = '00000000-0000-4000-8000-000000000001'
type Case = { name: string; method: string; part: string; valid: boolean; value: unknown }
type Binding = { name: string; method: string; params: unknown; result: unknown; valid: boolean }

describe('I06 strict main-only model contract corpus', () => {
  for (const test of fixtures.mainCases as unknown as Case[]) {
    it(test.name, () => {
      expect(isModelMethod(test.method)).toBe(true)
      if (!isModelMethod(test.method)) return
      const check =
        test.part === 'params'
          ? validateModelParams
          : test.part === 'result'
            ? validateModelResult
            : validateModelReply
      expect(check(test.method, test.value)).toBe(test.valid)
    })
  }
  for (const test of bindings.mainCases as unknown as Binding[]) {
    it(test.name, () => {
      expect(isModelMethod(test.method)).toBe(true)
      if (!isModelMethod(test.method)) return
      expect(matchesModelResult(test.method, test.params, test.result)).toBe(test.valid)
    })
  }
})

describe('I06 strict public gateway errors', () => {
  it('uses ten exact catalog mappings and leaves cancellation out of error identity', () => {
    expect(Object.keys(modelGatewayErrorCodeMap)).toHaveLength(10)
    expect(Object.keys(errors.codes).filter((code) => code.startsWith('GATEWAY_'))).toEqual(
      Object.values(modelGatewayErrorCodeMap),
    )
    for (const [internal, code] of Object.entries(modelGatewayErrorCodeMap)) {
      const actual = modelGatewayError(internal)
      expect(actual).toEqual({
        code,
        messageKey: errors.codes[code].messageKey,
        params: {},
        retryable: false,
      })
      expect(validateV2('error', actual)).toBe(true)
      expect(validateV2('error', { ...actual, params: { secret: 'synthetic' } })).toBe(false)
    }
    expect(modelGatewayError('CANCELLED').code).toBe('INTERNAL_ERROR')
    expect(
      validateV2('error', {
        code: 'CANCELLED',
        messageKey: 'gateway.cancelled',
        params: {},
        retryable: false,
      }),
    ).toBe(false)
  })
  it('keeps malformed params separate from semantically invalid gateway input', () => {
    expect(modelInvalidRequestError()).toEqual({
      code: 'INVALID_REQUEST',
      messageKey: 'protocol.invalidRequest',
      params: { field: 'params' },
      retryable: false,
    })
    expect(modelGatewayError('INVALID_INPUT').code).toBe('GATEWAY_INVALID_INPUT')
  })
  it('never takes upstream identity, prototype entries or mutable error params as authority', () => {
    for (const value of ['toString', 'constructor', '__proto__', {}, null])
      expect(modelGatewayError(value)).toEqual(safeError(undefined))
    modelGatewayError('LOCAL_ONLY').params.changed = 'synthetic'
    expect(modelGatewayError('LOCAL_ONLY').params).toEqual({})
  })
})

describe('I06 browser-safe size and isolation boundaries', () => {
  it('permits exactly 1MiB actual UTF-8 completed text in main only', () => {
    const result = { invocationId: id, state: 'completed', text: 'x'.repeat(1024 * 1024) }
    expect(validateModelResult('getModelExplanationOutcome', result)).toBe(true)
    expect(validateModelReply('getModelExplanationOutcome', { ok: true, data: result })).toBe(true)
    expect(
      validateModelResult('getModelExplanationOutcome', { ...result, text: result.text + 'x' }),
    ).toBe(false)
    expect(validateV2('modelExplanationOutcome', result)).toBe(false)
  })
  it('measures UTF-8 rather than JavaScript character count', () => {
    const result = { invocationId: id, state: 'completed', text: '汉'.repeat(349525) + 'a' }
    expect(new TextEncoder().encode(result.text).byteLength).toBe(1048576)
    expect(validateModelResult('getModelExplanationOutcome', result)).toBe(true)
    expect(
      validateModelResult('getModelExplanationOutcome', { ...result, text: result.text + 'b' }),
    ).toBe(false)
    expect(validateModelResult('getModelExplanationOutcome', { ...result, text: '\ud800' })).toBe(
      false,
    )
  })
  it('rejects cyclic, undefined and unknown main values without throwing', () => {
    const value: Record<string, unknown> = {}
    value.self = value
    expect(validateModelValue('modelAccessStatus', value)).toBe(false)
    expect(validateModelValue('modelPrivacy', undefined)).toBe(false)
    expect(validateModelValue('params_job.get', {})).toBe(false)
    expect(validateModelValue('modelMissingSchema', {})).toBe(false)
    expect(isModelMethod('request')).toBe(false)
    expect(isModelMethod('toString')).toBe(false)
  })
  it('keeps main methods out of every Python/product/job advertisement and envelope', () => {
    expect(v2Registry.productRuntime).toEqual(['health'])
    for (const method of v2Registry.mainRuntime) {
      expect(isModelMethod(method)).toBe(true)
      if (!isModelMethod(method)) throw new Error('missing main registry identity')
      expect(v2Registry.v2Runtime).not.toContain(method)
      expect(v2Registry.capabilities).not.toHaveProperty(method)
      expect(v2Registry.mainCapabilities[method].owner).toBe('main')
      expect(v2Registry.mainCapabilities[method].agentEligible).toBe(false)
      expect(v2Registry.mainCapabilities[method].pythonEligible).toBe(false)
      expect(
        validateV2('envelope', {
          kind: 'request',
          protocolVersion: 2,
          id,
          engineSessionId: id,
          method,
          params: {},
        }),
      ).toBe(false)
    }
  })
  it('has no credential readback, generic forwarding or secret-bearing result schema', () => {
    const definitions = schema.$defs as unknown as Record<string, Record<string, unknown>>
    const forbidden = new Set(['secret', 'credentialRef', 'credentialVersion', 'ciphertext'])
    const visit = (node: Record<string, unknown>, seen = new Set<string>()): void => {
      if (typeof node.$ref === 'string') {
        const name = node.$ref.slice(8)
        if (!seen.has(name)) {
          seen.add(name)
          visit(definitions[name], seen)
        }
      }
      if (node.properties) {
        for (const [name, child] of Object.entries(node.properties)) {
          expect(forbidden.has(name)).toBe(false)
          visit(child as Record<string, unknown>, seen)
        }
      }
      if (Array.isArray(node.oneOf)) for (const child of node.oneOf) visit(child, seen)
      if (node.items) visit(node.items as Record<string, unknown>, seen)
    }
    expect(v2Registry.mainRuntime).toEqual([
      'getModelAccessStatus',
      'configureModel',
      'storeModelCredential',
      'setModelPrivacy',
      'selectModelResults',
      'getModelFieldCatalog',
      'selectModelFields',
      'previewModelExplanation',
      'confirmModelAuthorization',
      'startModelExplanation',
      'getModelExplanationOutcome',
      'cancelModelExplanation',
    ])
    for (const method of v2Registry.mainRuntime) visit(definitions['modelResult_' + method])
  })
  it('retains the existing engine frame bound for ordinary result pages', () => {
    const fixture = fixtures.cases.find((entry) => entry.name === 'unicode cell')!
    const page = structuredClone(fixture.value) as { rows: Array<{ cells: string[] }> }
    page.rows[0].cells = Array(20).fill('汉'.repeat(8000))
    expect(validateV2('page', page)).toBe(false)
  })
})
