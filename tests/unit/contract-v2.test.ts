import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import schema from '../../packages/contracts/v2/schema.json'
import rules from '../../packages/engine/src/ontolearn_engine/invalidation-v2.json'
import errors from '../../packages/contracts/v2/errors.json'
import {
  acceptsJobEvent,
  cursorMatches,
  jobListCursorMatches,
  deriveDependencies,
  matchesResponse,
  permitsTransition,
  validateV2,
  validationProjectionMatchesResources,
  v2Registry,
} from '../../packages/contracts/src/design-v2'

function objectValue(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new Error('Expected an object fixture')
  return value as Record<string, unknown>
}
function objectFixture(name: string): Record<string, unknown> {
  const fixture = fixtures.cases.find((c) => c.name === name)
  if (!fixture) throw new Error(`Missing fixture: ${name}`)
  return objectValue(fixture.value)
}

describe('shared v2 contract corpus', () => {
  for (const c of fixtures.validationBindings)
    it(c.name, () =>
      expect(validationProjectionMatchesResources(c.projection, c.resources)).toBe(c.valid),
    )
  for (const c of fixtures.transitions)
    it(c.name, () =>
      expect(
        permitsTransition(
          c.from,
          c.to,
          Number(c.beforeVersion),
          Number(c.afterVersion),
          c.finalBeforeCancel,
        ),
      ).toBe(c.valid),
    )
  for (const c of fixtures.dependencyChains)
    it(c.name, () => {
      const definitions = Array.from({ length: c.length }, (_, i) => ({
        family: 'query',
        id: `Q${i}`,
        version: 1,
        references: i + 1 < c.length ? [`query:Q${i + 1}`] : [],
      }))
      if (c.valid)
        expect(deriveDependencies('query.execute', 'Q0', 'asserted', definitions).keys).toEqual(
          ['facts:asserted', ...definitions.map((d) => `query:${d.id}`)].sort(),
        )
      else
        expect(() => deriveDependencies('query.execute', 'Q0', 'asserted', definitions)).toThrow(
          'INVALID_REQUEST',
        )
    })

  for (const c of fixtures.unicodeMutations)
    it(c.name, () => expect(validateV2(c.schema, String.fromCharCode(c.codeUnit))).toBe(c.valid))
  for (const c of fixtures.responses)
    it(c.name, () => expect(matchesResponse(c.request, c.response)).toBe(c.valid))
  for (const c of fixtures.jobListCursors)
    it(c.name, () => expect(jobListCursorMatches(c.record, c.request, c.nowMs)).toBe(c.valid))
  for (const c of fixtures.cases)
    it(c.name, () => expect(validateV2(c.schema, c.value)).toBe(c.valid))
  for (const c of fixtures.routing)
    it(c.name, () => expect(acceptsJobEvent(c.value, c.binding)).toBe(c.valid))
  for (const c of fixtures.cursors)
    it(c.name, () => expect(cursorMatches(c.record, c.request, c.nowMs)).toBe(c.valid))
  it('rejects oversized multi-byte page before serving', () => {
    const page = structuredClone(fixtures.cases.find((c) => c.name === 'unicode cell')!.value) as {
      rows: Array<{ cells: string[] }>
    }
    page.rows[0].cells = Array(20).fill('汉'.repeat(8000))
    expect(validateV2('page', page)).toBe(false)
  })
  it('all error catalog entries equal canonical schema alternatives', () => {
    expect(schema.$defs.error.oneOf).toEqual(
      Object.entries(errors.codes).map(([code, e]) => ({
        type: 'object',
        properties: {
          code: { const: code },
          messageKey: { const: e.messageKey },
          retryable: { const: e.retryable },
          params: e.paramsSchema,
        },
        required: ['code', 'messageKey', 'retryable', 'params'],
        additionalProperties: false,
      })),
    )
  })
  it('domain stale codes come only from S1; model has no code', () => {
    expect(schema.$defs.staleReason.oneOf.map((s) => s.properties.code.const)).toEqual(
      rules.rules.filter((r) => r.staleReason).map((r) => r.staleReason),
    )
    expect(rules.rules.find((r) => r.family === 'model')!.staleReason).toBeNull()
  })
  it('registry schema references resolve and the v2 method surface stays explicit', () => {
    for (const entry of Object.values(v2Registry.capabilities))
      for (const ref of [entry.paramsSchema, entry.resultSchema])
        expect(ref.slice(8) in schema.$defs).toBe(true)
    expect(v2Registry.v2Runtime).toEqual([
      'hello',
      'health',
      'session.ping',
      'project.get',
      'job.create',
      'job.get',
      'job.cancel',
      'job.list',
      'job.subscribe',
      'job.unsubscribe',
      'result.get',
      'result.current',
      'result.page',
      'operation.get',
      'query.definition.load',
      'query.execution.prepare',
      'query.result.describe',
      'query.result.textPage',
      'query.result.rowsPage',
    ])
    expect(v2Registry.v2Runtime.some((name) => name.startsWith('test.'))).toBe(false)
    expect(v2Registry.productRuntime).toEqual(['health'])
  })
})

it('responses bind request, method, project, job, session and heartbeat nonce', () => {
  const q = fixtures.cases.find((c) => c.name === 'request job.get')!.value
  const r = objectFixture('response job.get')
  expect(matchesResponse(q, r)).toBe(true)
  for (const key of ['id', 'engineSessionId'])
    expect(matchesResponse(q, { ...r, [key]: '00000000-0000-4000-8000-000000000099' })).toBe(false)
  const bad = structuredClone(r) as { result: { projectId: string } }
  bad.result.projectId = '00000000-0000-4000-8000-000000000099'
  expect(matchesResponse(q, bad)).toBe(false)
  const hello = objectFixture('request hello')
  const answer = fixtures.cases.find((c) => c.name === 'response hello')!.value
  expect(matchesResponse(hello, answer)).toBe(true)
  expect(
    matchesResponse(
      {
        ...hello,
        params: { supportedVersions: [1], clientId: '00000000-0000-4000-8000-000000000007' },
      },
      answer,
    ),
  ).toBe(false)
})

it('terminal states never regress and partial rounds cannot resolve cancelling to success', () => {
  const states = ['queued', 'running', 'cancelling', 'succeeded', 'failed', 'cancelled']
  const allowed = [
    'queued>running',
    'queued>cancelled',
    'queued>failed',
    'running>cancelling',
    'running>succeeded',
    'running>failed',
    'cancelling>cancelled',
    'cancelling>failed',
    'cancelling>succeeded',
  ]
  for (const from of states)
    for (const to of states)
      expect(permitsTransition(from, to, 1, 2, true)).toBe(allowed.includes(`${from}>${to}`))
  expect(permitsTransition('cancelling', 'succeeded', 1, 2, false)).toBe(false)
  expect(permitsTransition('running', 'failed', 2, 2, true)).toBe(false)
})

it('derives real dependency closure, detects missing references and tracks new rule membership', () => {
  const definitions = [
    { family: 'ontology', id: 'O1', version: 1, references: [] },
    { family: 'mapping', id: 'M1', version: 1, references: [] },
    { family: 'query', id: 'Q1', version: 1, references: [] },
    { family: 'rule', id: 'R1', version: 1, references: ['ontology:O1'] },
    { family: 'constraint', id: 'C1', version: 1, references: [] },
    { family: 'model', id: 'unused', version: 9, references: [] },
  ]
  expect(deriveDependencies('query.execute', 'Q1', 'asserted', definitions)).toEqual({
    keys: ['facts:asserted', 'mapping:M1', 'ontology:O1', 'query:Q1'],
    sets: { ontology: ['ontology:O1'], mapping: ['mapping:M1'] },
  })
  expect(deriveDependencies('query.execute', 'Q1', 'asserted+derived', definitions).keys).toEqual([
    'facts:asserted',
    'mapping:M1',
    'ontology:O1',
    'query:Q1',
    'rule:R1',
  ])
  const next = [...definitions, { family: 'rule', id: 'R2', version: 0, references: [] }]
  expect(deriveDependencies('reasoning.execute', 'unused', 'asserted', next).sets.rule).toEqual([
    'rule:R1',
    'rule:R2',
  ])
  expect(() => deriveDependencies('query.execute', 'missing', 'asserted', definitions)).toThrow(
    'INVALID_REQUEST',
  )
  expect(() =>
    deriveDependencies('reasoning.execute', 'unused', 'asserted', [
      ...definitions,
      { family: 'rule', id: 'dangling', version: 1, references: ['ontology:missing'] },
    ]),
  ).toThrow('INVALID_REQUEST')
})

it('all enum parameters have complete finite meanings without extra categories', () => {
  const expected: string[] = []
  const meanings = objectValue(errors.parameterMeanings)
  for (const [code, entry] of Object.entries(errors.codes)) {
    const enumerations = Object.values(entry.paramsSchema.properties)
      .map((property) => objectValue(property).enum)
      .filter(Array.isArray)
    if (!enumerations.length) continue
    // The flat catalog format permits one enum parameter per code.
    expect(enumerations).toHaveLength(1)
    expected.push(code)
    const descriptions = objectValue(meanings[code])
    expect(Object.keys(descriptions)).toEqual(enumerations[0])
    for (const description of Object.values(descriptions)) {
      expect(typeof description).toBe('string')
      expect(String(description).trim().length).toBeGreaterThan(0)
    }
  }
  expect(Object.keys(meanings).sort()).toEqual(expected.sort())
})

it('error catalog version and byte budget govern the adapters', () => {
  expect(errors.schemaVersion).toBe(v2Registry.schemaVersion)
  expect(schema.$id).toBe(`urn:ontolearn:contracts:${errors.schemaVersion}`)
  expect(Number.isSafeInteger(errors.maxEncodedBytes)).toBe(true)
  expect(errors.maxEncodedBytes).toBeGreaterThan(0)
  const value = {
    code: 'INTERNAL_ERROR',
    messageKey: 'engine.internal',
    retryable: false,
    params: {},
  }
  expect(validateV2('error', value)).toBe(true)
  const original = errors.maxEncodedBytes
  try {
    errors.maxEncodedBytes = 1
    expect(validateV2('error', value)).toBe(false)
  } finally {
    errors.maxEncodedBytes = original
  }
  expect(validateV2('error', value)).toBe(true)
})

it('canonical schema uses the supported vocabulary and explicitly bounds every array', () => {
  const vocabulary = new Set([
    '$ref',
    'const',
    'enum',
    'oneOf',
    'type',
    'properties',
    'required',
    'additionalProperties',
    'propertyNames',
    'minProperties',
    'maxProperties',
    'items',
    'minItems',
    'maxItems',
    'minLength',
    'maxLength',
    'pattern',
    'minimum',
    'maximum',
  ])
  function visit(value: unknown): void {
    const node = objectValue(value)
    for (const key of Object.keys(node)) expect(vocabulary.has(key), key).toBe(true)
    if (node.type === 'array') {
      expect(Number.isSafeInteger(node.maxItems)).toBe(true)
      expect(Number(node.maxItems)).toBeGreaterThanOrEqual(0)
      expect(node.items).toBeDefined()
    }
    if (node.properties) Object.values(objectValue(node.properties)).forEach(visit)
    for (const key of ['items', 'propertyNames', 'additionalProperties'])
      if (node[key] && typeof node[key] === 'object') visit(node[key])
    if (Array.isArray(node.oneOf)) node.oneOf.forEach(visit)
  }
  Object.values(schema.$defs).forEach(visit)
})
