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
  it('registry schema references resolve, and v2 advertises no unimplemented runtime', () => {
    for (const entry of Object.values(v2Registry.capabilities))
      for (const ref of [entry.paramsSchema, entry.resultSchema])
        expect(ref.slice(8) in schema.$defs).toBe(true)
    expect(v2Registry.v2Runtime).toEqual([])
    expect(v2Registry.productRuntime).toEqual(['health'])
  })
})

it('responses bind request, method, project, job, session and heartbeat nonce', () => {
  const q = fixtures.cases.find((c) => c.name === 'request job.get')!.value
  const r = fixtures.cases.find((c) => c.name === 'response job.get')!.value
  expect(matchesResponse(q, r)).toBe(true)
  for (const key of ['id', 'engineSessionId'])
    expect(matchesResponse(q, { ...r, [key]: '00000000-0000-4000-8000-000000000099' })).toBe(false)
  const bad = structuredClone(r) as { result: { projectId: string } }
  bad.result.projectId = '00000000-0000-4000-8000-000000000099'
  expect(matchesResponse(q, bad)).toBe(false)
  const hello = fixtures.cases.find((c) => c.name === 'request hello')!.value
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

it('error category descriptions cover exactly the bounded wire categories', () => {
  expect(Object.keys(errors.parameterMeanings.UNSUPPORTED_CONSTRUCT)).toEqual(
    errors.codes.UNSUPPORTED_CONSTRUCT.paramsSchema.properties.construct.enum,
  )
  expect(Object.keys(errors.parameterMeanings.RESOURCE_LIMIT)).toEqual(
    errors.codes.RESOURCE_LIMIT.paramsSchema.properties.resource.enum,
  )
})
