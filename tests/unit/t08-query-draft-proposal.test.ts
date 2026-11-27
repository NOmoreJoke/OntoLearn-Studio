import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import type { AssistantMessage } from '../../apps/desktop/src/main/agent/deepseek-codec'
import { AgentError } from '../../apps/desktop/src/main/agent/errors'
import { decodeQueryDraftProposal } from '../../apps/desktop/src/main/agent/query-draft/proposal'

interface ReplacementSpec {
  name: string
  unit: string
  repeat: string
  count: number
}

interface VectorCase {
  id: string
  modelContent?: Record<string, unknown>
  hostInput?: Record<string, unknown>
  expected?: Record<string, unknown>
  expectedError?: string
  expectedFrom?: string
  base?: string
  literalFieldReplacement?: ReplacementSpec
  assertions?: string[]
}

interface VectorSuite {
  kind: string
  version: number
  status: string
  purpose: string
  messageConstruction: string
  cases: VectorCase[]
  notRetested: string[]
}

// vite's builtin json plugin rejects the fixture's isolated-surrogate escapes, so the exact
// a2fd bytes are loaded with V8's spec-compliant JSON.parse instead of an ESM json import.
const fixturePath = resolve(
  import.meta.dirname,
  '../fixtures/agent/query-draft/proposal-cases.v1.json',
)
const suite = JSON.parse(readFileSync(fixturePath, 'utf8')) as VectorSuite
const baseCase = suite.cases.find((vector) => vector.id === 'QD01')

interface HostInput {
  inputContext: { projectId: string; selectedObjectIds: string[] }
  queryScope: string
}

/** messageConstruction: literal AssistantMessage, no real provider response is claimed. */
function assistantMessage(modelContent: Record<string, unknown>): AssistantMessage {
  return {
    role: 'assistant',
    content: JSON.stringify(modelContent),
    reasoning_content: 'synthetic-plan',
  }
}

/** Replacement cases copy QD01 and replace exactly the named content field, count times. */
function materialize(vector: VectorCase): {
  modelContent: Record<string, unknown>
  hostInput: unknown
  expected?: Record<string, unknown>
  expectedError?: string
} {
  if (!vector.literalFieldReplacement) {
    return {
      modelContent: vector.modelContent as Record<string, unknown>,
      hostInput: structuredClone(vector.hostInput),
      expected: vector.expected,
      expectedError: vector.expectedError,
    }
  }
  const spec = vector.literalFieldReplacement
  const baseModel = baseCase?.modelContent
  const baseExpected = baseCase?.expected
  const baseHost = baseCase?.hostInput
  if (!baseModel || !baseExpected || !baseHost) {
    throw new Error('fixture is missing the QD01 replacement base')
  }
  const replacement = spec.repeat.repeat(spec.count)
  const modelContent = structuredClone(baseModel)
  modelContent[spec.name] = replacement
  const expected = structuredClone(baseExpected)
  ;(expected.draft as Record<string, unknown>)[spec.name] = replacement
  return {
    modelContent,
    hostInput: structuredClone(baseHost),
    expected,
    expectedError: vector.expectedError,
  }
}

/** Any fixture-valid model body works for hostile-host cases; the model side is not under test. */
function validModelContent(): Record<string, unknown> {
  const vector = suite.cases.find((item) => item.id === 'QD01')
  const modelContent = vector?.modelContent
  if (!modelContent) throw new Error('fixture is missing QD01 model content')
  return modelContent
}

describe('T08 B3 query-draft proposal (synthetic vectors, no transport)', () => {
  it('keeps the prepared vector fixture intact and complete', () => {
    expect(suite.kind).toBe('proposed_acceptance_vectors_not_test_results')
    expect(suite.version).toBe(1)
    expect(suite.status).toBe('PREPARED_NOT_EXECUTED')
    expect(suite.cases).toHaveLength(26)
    expect(new Set(suite.cases.map((vector) => vector.id)).size).toBe(26)
  })

  for (const vector of suite.cases) {
    it(`case ${vector.id}: ${vector.expectedError ?? 'maps to a host-stamped proposal'}`, () => {
      const materialized = materialize(vector)
      const message = assistantMessage(materialized.modelContent)
      const host = materialized.hostInput as HostInput

      if (materialized.expectedError) {
        let thrown: unknown
        try {
          decodeQueryDraftProposal(message, host)
        } catch (error) {
          thrown = error
        }
        expect(thrown).toBeInstanceOf(AgentError)
        expect((thrown as AgentError).code).toBe(materialized.expectedError)
        // Fixed code only: the boundary never echoes Zod issues, stacks or original text.
        expect((thrown as AgentError).message).toBe(materialized.expectedError)
        return
      }

      const proposal = decodeQueryDraftProposal(message, host)
      expect(proposal).toEqual(materialized.expected)

      if (vector.id === 'QD01') {
        expect(proposal.draft.sparql.endsWith('\n')).toBe(true)
        expect(proposal.draft.name).toBe('设备😀')
        expect(proposal.draft.description).toContain('001')
        // Exact shapes: no job/result/passed/confirmation fields can ride along.
        expect(Object.keys(proposal).sort()).toEqual([
          'draft',
          'inputContext',
          'kind',
          'requiresHumanReview',
        ])
        expect(Object.keys(proposal.draft).sort()).toEqual([
          'capabilityQuestion',
          'description',
          'name',
          'scope',
          'source',
          'sparql',
        ])
      }
      if (vector.id === 'QD07') {
        // Untrusted draft text passes through verbatim; this is no execution or safe-query claim.
        expect(proposal.draft.sparql).toContain('SERVICE <https://invalid.example/sparql>')
      }
      if (vector.id === 'QD08') {
        // Mutating the returned proposal never rewrites the host or model input.
        const modelInput = structuredClone(materialized.modelContent)
        const hostInputA = structuredClone(materialized.hostInput) as HostInput
        const returnedA = decodeQueryDraftProposal(assistantMessage(modelInput), hostInputA)
        returnedA.inputContext.selectedObjectIds.push('999')
        returnedA.draft.name = 'mutated'
        expect(hostInputA.inputContext.selectedObjectIds).toEqual(['001', '002'])
        expect(modelInput.name).toBe('设备😀')

        // Mutating the host input after the call never rewrites the returned proposal.
        const hostInputB = structuredClone(materialized.hostInput) as HostInput
        const returnedB = decodeQueryDraftProposal(
          assistantMessage(structuredClone(materialized.modelContent)),
          hostInputB,
        )
        hostInputB.inputContext.selectedObjectIds.push('host-999')
        hostInputB.inputContext.projectId = 'p9'
        expect(returnedB.inputContext.selectedObjectIds).toEqual(['001', '002'])
        expect(returnedB.inputContext.projectId).toBe('p1')
        expect(returnedB.draft.name).toBe('设备😀')
        expect(returnedB.draft.sparql).toBe('SELECT ?s WHERE { ?s a <urn:Equipment> }\n')
      }
      if (vector.literalFieldReplacement?.count && vector.expectedFrom) {
        // At-raw-limit cases keep the exact replaced length: no normalization ever runs.
        const field = vector.literalFieldReplacement.name
        const replaced = (proposal.draft as unknown as Record<string, unknown>)[field]
        expect(replaced).toHaveLength(vector.literalFieldReplacement.count)
      }
    })
  }
})

describe('T08 B3 query-draft proposal hostile host input (fixed code, no raw leak)', () => {
  /** zod safeParse lets property-access throws escape; the decoder must collapse them itself. */
  function expectInvalidProtocol(hostInput: unknown) {
    let thrown: unknown
    try {
      decodeQueryDraftProposal(assistantMessage(validModelContent()), hostInput)
    } catch (error) {
      thrown = error
    }
    expect(thrown).toBeInstanceOf(AgentError)
    expect((thrown as AgentError).code).toBe('INVALID_PROTOCOL')
    expect((thrown as AgentError).message).toBe('INVALID_PROTOCOL')
    expect((thrown as AgentError).message).not.toContain('LEAK')
  }

  it('collapses a throwing top-level inputContext getter', () => {
    expectInvalidProtocol({
      queryScope: 'asserted',
      get inputContext() {
        throw new Error('LEAK /private/top-level-getter')
      },
    })
  })

  it('collapses a throwing nested context selectedObjectIds getter', () => {
    expectInvalidProtocol({
      queryScope: 'asserted',
      inputContext: {
        projectId: 'p1',
        projectRevision: 3,
        inputSnapshotId: 's3',
        scopeRef: 'authorized-scope',
        module: 'query',
        mode: 'project',
        get selectedObjectIds() {
          throw new Error('LEAK /private/nested-getter')
        },
      },
    })
  })
})
