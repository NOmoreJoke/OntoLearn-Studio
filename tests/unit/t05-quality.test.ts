import { describe, expect, it } from 'vitest'
import type {
  ProjectQualityCheckArgs,
  ProjectQualityPrepareDTO,
  ProjectQualityReadDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import {
  compareStatements,
  type Statement,
} from '../../apps/desktop/src/renderer/src/quality/presentation'
import { prepareEditorDraft } from '../../apps/desktop/src/renderer/src/quality/draft'
import fixtures from '../../packages/contracts/v2/fixtures.json'

const projectId = 'c0000000-0000-4000-8000-000000000001'
const operationId = 'c0000000-0000-4000-8000-000000000002'
const digest = '1'.repeat(64)
const form = {
  kind: 'constraint',
  identity: 'equipment-limit',
  label: '设备约束',
  revision: '1',
  enabled: true,
  targetClass: 'urn:test:Equipment',
  path: 'urn:test:name',
  template: 'maxCount',
  parameter: '1',
  upper: '',
  conditions: [],
  conclusions: [],
} satisfies Parameters<typeof prepareEditorDraft>[0]

function prng(seed: number) {
  return (bound: number) => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0
    return Math.floor((seed / 2 ** 32) * bound)
  }
}

describe('formal quality workspace contracts', () => {
  it('validates read and prepare arguments and results against the wire schemas', () => {
    const args: ProjectQualityCheckArgs = {
      projectId,
      operationId,
      selection: { kind: 'current' },
      validationScope: 'asserted+derived',
    }
    expect(validateBusiness3('params_project.quality.read', { projectId })).toBe(true)
    expect(validateBusiness3('params_project.quality.read', { projectId, operationId })).toBe(false)
    expect(validateBusiness3('params_project.quality.prepare', args)).toBe(true)
    expect(
      validateBusiness3('params_project.quality.prepare', {
        ...args,
        validationScope: 'historical',
      }),
    ).toBe(false)
    const state: ProjectQualityReadDTO = {
      qualityReadVersion: 1,
      projectId,
      rules: [],
      constraints: [],
      reasoning: null,
      validation: null,
    }
    expect(validateBusiness3('result_project.quality.read', state)).toBe(true)
    expect(
      validateBusiness3('result_project.quality.read', { ...state, qualityReadVersion: 2 }),
    ).toBe(false)

    const hello = fixtures.cases.find((entry) => entry.name === 'response hello')!
      .value as unknown as {
      result: {
        registryHash: string
        limits: ProjectQualityPrepareDTO['executionIdentity']['limits']
      }
    }
    const input = {
      inputSnapshotId: digest,
      parametersHash: digest,
      scope: 'asserted' as const,
      definitionId: 'all-rules',
      derivedResultIds: [],
      preparedPlanRef: null,
    }
    const prepared: ProjectQualityPrepareDTO = {
      projectId,
      operationId,
      chain: ['reasoning.execute', 'validation.execute'],
      reasoningInput: input,
      validationInput: null,
      validationInputs: [],
      executionIdentity: {
        registryHash: hello.result.registryHash,
        limits: hello.result.limits,
        implementation: {
          executionSemanticsVersion: 'finite6',
          engineVersion: '0.1.0',
          dependencyLockHash: digest,
        },
      },
    }
    expect(validateBusiness3('result_project.quality.prepare', prepared)).toBe(true)
    expect(
      validateBusiness3('result_project.quality.prepare', {
        ...prepared,
        validationInputs: [null],
      }),
    ).toBe(false)
  })

  it('validates formal upserts and removals at the ChangeSet preview boundary', () => {
    const params = {
      projectId,
      baseRevision: 3,
      intent: 'change',
      plan: {
        definitions: [
          {
            layer: 'constraint',
            id: form.identity,
            value: JSON.parse(prepareEditorDraft({ ...form, template: 'required' }).draft),
          },
          {
            layer: 'rule',
            id: 'R-next',
            value: {
              schemaVersion: 1,
              kind: 'rule',
              id: 'R-next',
              revision: 1,
              label: '规则',
              enabled: true,
              conditions: [{ kind: 'type', subject: '?x', class: 'urn:test:A' }],
              conclusions: [{ kind: 'type', subject: '?x', class: 'urn:test:B' }],
            },
          },
        ],
        remove_definitions: [
          { layer: 'rule', id: 'retired' },
          { layer: 'constraint', id: 'retired' },
        ],
      },
    }
    expect(validateBusiness3('params_changeset.preview', params)).toBe(true)
    expect(
      validateBusiness3('params_changeset.preview', {
        ...params,
        plan: { ...params.plan, remove_definitions: [{ layer: 'mapping', id: 'retired' }] },
      }),
    ).toBe(false)
  })
})

describe('seeded quality properties', () => {
  it('round-trips canonical maxCount drafts and rejects invalid revisions and counts', () => {
    const next = prng(0x5040505)
    for (let index = 0; index < 128; index++) {
      const revision = next(1_000_000) + 1
      const maxCount = next(100_000)
      const label = `约束 ${index} · ${next(1_000_000)}`
      const input = {
        ...form,
        revision: String(revision),
        parameter: String(maxCount),
        label,
        enabled: Boolean(next(2)),
      }
      const draft = prepareEditorDraft(input)
      expect(draft.error).toBe('')
      const parsed = JSON.parse(draft.draft)
      expect(parsed).toEqual({
        schemaVersion: 1,
        kind: 'constraint',
        id: form.identity,
        revision,
        label,
        enabled: input.enabled,
        targetClass: form.targetClass,
        path: form.path,
        template: 'maxCount',
        parameters: { maxCount },
      })
      expect(
        prepareEditorDraft({
          ...input,
          revision: String(parsed.revision),
          parameter: String(parsed.parameters.maxCount),
        }),
      ).toEqual(draft)
      expect(prepareEditorDraft({ ...input, revision: '-' + revision }).error).toBeTruthy()
      expect(prepareEditorDraft({ ...input, parameter: `${maxCount}.1` }).error).toBeTruthy()
    }
    expect(prepareEditorDraft({ ...form, revision: '0' }).error).toBeTruthy()
    expect(
      prepareEditorDraft({ ...form, parameter: String(Number.MAX_SAFE_INTEGER + 1) }).error,
    ).toBeTruthy()
  })

  it('compares statement sets symmetrically and ignores duplicates and order', () => {
    const next = prng(0x502)
    const statements = (): Statement[] =>
      Array.from({ length: next(16) }, () => [
        `urn:test:${next(10)}`,
        'urn:test:P',
        `<urn:test:${next(4)}>`,
      ])
    for (let index = 0; index < 128; index++) {
      const expected = statements()
      const actual = statements()
      const forward = compareStatements(expected, actual)
      const backward = compareStatements(actual, expected)
      expect(forward).toEqual({ missing: backward.unexpected, unexpected: backward.missing })
      expect(compareStatements(expected, [...expected, ...[...expected].reverse()])).toEqual({
        missing: [],
        unexpected: [],
      })
      expect(compareStatements([...expected, ...expected], [...actual].reverse())).toEqual(forward)
    }
  })
})
