import { describe, expect, it } from 'vitest'
import type {
  ProjectQualityCheckArgs,
  ProjectQualityPrepareDTO,
  ProjectQualityReadDTO,
  QualityRuleTestRequestDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import {
  compareStatements,
  type Statement,
} from '../../apps/desktop/src/renderer/src/quality/presentation'
import {
  detectRuleChainDependencies,
  prepareEditorDraft,
  type Pattern,
} from '../../apps/desktop/src/renderer/src/quality/draft'
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

  it('accepts optional ruleTest reads and full coverage fields on both quality wire schemas', () => {
    const ruleTest: QualityRuleTestRequestDTO = {
      ontologyTriples: [
        [
          'urn:ontolearn:learning:assignedTo',
          'http://www.w3.org/2000/01/rdf-schema#range',
          '<urn:ontolearn:learning:Person>',
        ],
      ],
      inputTriples: [
        [
          'urn:ontolearn:learning:equipment/002',
          'urn:ontolearn:learning:assignedTo',
          '<urn:ontolearn:learning:person/L02>',
        ],
      ],
      rules: [
        {
          id: 'rdfs-trigger',
          label: '读取 Person 推导 Flagged',
          enabled: true,
          conditions: [
            { kind: 'type', subject: '?person', class: 'urn:ontolearn:learning:Person' },
          ],
          conclusions: [
            { kind: 'type', subject: '?person', class: 'urn:ontolearn:learning:Flagged' },
          ],
        },
      ],
      expectedOutputs: [
        [
          'urn:ontolearn:learning:person/L02',
          'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
          '<urn:ontolearn:learning:Flagged>',
        ],
      ],
    }
    expect(validateBusiness3('params_project.quality.read', { projectId })).toBe(true)
    expect(validateBusiness3('params_project.quality.read', { projectId, ruleTest })).toBe(true)
    expect(
      validateBusiness3('params_project.quality.read', {
        projectId,
        ruleTest: { ...ruleTest, inputTriples: [] },
      }),
    ).toBe(false)
    expect(
      validateBusiness3('params_project.quality.read', {
        projectId,
        ruleTest: { ...ruleTest, unknown: true },
      }),
    ).toBe(false)

    const resultId = 'c0000000-0000-4000-8000-000000000003'
    const jobId = 'c0000000-0000-4000-8000-000000000004'
    const hash = 'a'.repeat(64)
    const covered: ProjectQualityReadDTO = {
      qualityReadVersion: 1,
      projectId,
      rules: [],
      constraints: [],
      reasoning: {
        resultId,
        jobId,
        state: 'current',
        staleReasons: [],
        inputSnapshotId: hash,
        scope: 'asserted',
        definitionId: 'all-rules',
      },
      validation: {
        resultId,
        jobId,
        state: 'current',
        staleReasons: [],
        inputSnapshotId: hash,
        scope: 'asserted',
        definitionId: 'name-required',
        conforms: null,
        inputProjectRevision: 7,
        checkedConstraintIds: ['name-required'],
        unverifiedConstraintIds: ['disabled-shape'],
        failedConstraintIds: ['broken-shape'],
        findings: [
          {
            tier: 'warning',
            focusNode: 'urn:test:pump',
            path: 'urn:test:name',
            constraint: 'required',
            sourceShape: null,
            value: null,
            definitionId: 'name-required',
            targets: { subject: 'urn:test:pump', predicate: 'urn:test:name', object: null },
          },
        ],
      },
      snapshotsAligned: false,
      ruleTestResult: {
        valid: true,
        matchesExpected: true,
        actualOutputs: [
          [
            'urn:ontolearn:learning:person/L02',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            '<urn:ontolearn:learning:Flagged>',
          ],
        ],
        rdfsOutputs: [
          [
            'urn:ontolearn:learning:person/L02',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
            '<urn:ontolearn:learning:Person>',
          ],
        ],
        expectedOutputs: [],
        missingOutputs: [],
        unexpectedOutputs: [],
        ruleTraces: [{ rule: 'rdfs-trigger', output: null, inputs: [] }],
        warnings: ['RULE_CHAIN_UNSUPPORTED:rdfs-trigger'],
        diagnostics: [
          {
            stage: 'input',
            index: 0,
            ruleId: null,
            field: '2',
            code: 'INVALID_TERM',
            message: 'INVALID_TERM：input[0] 2 校验失败',
          },
        ],
      },
    }
    expect(validateBusiness3('result_project.quality.read', covered)).toBe(true)
    expect(
      validateBusiness3('result_project.quality.read', {
        ...covered,
        ruleTestResult: { valid: true },
      }),
    ).toBe(false)
    expect(
      validateBusiness3('result_project.quality.read', {
        ...covered,
        validation: { ...covered.validation!, conforms: 'unknown' },
      }),
    ).toBe(false)
    expect(
      validateBusiness3('result_project.quality.read', {
        ...covered,
        validation: {
          ...covered.validation!,
          findings: [{ ...covered.validation!.findings[0]!, definitionId: '不合法 标识' }],
        },
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

  it('predicts engine rule-chain pairs for draft rules including self chains', () => {
    const type = (value: string): Pattern => ({ kind: 'type', subject: '?x', path: '', value })
    const property = (path: string, value: string): Pattern => ({
      kind: 'property',
      subject: '?x',
      path,
      value,
    })
    const rule = (id: string, conditions: Pattern[], conclusions: Pattern[], enabled = true) => ({
      id,
      enabled,
      conditions,
      conclusions,
    })
    const existing = [
      rule('R-risk', [type('urn:test:Equipment')], [type('urn:test:HighRisk')]),
      rule('R-off', [type('urn:test:Off')], [type('urn:test:OffOut')], false),
    ]
    // Exact (kind, target) overlap: R-risk writes what R-next reads; the type
    // read additionally matches R-next's own conclusions (enabled self chain).
    expect(
      detectRuleChainDependencies(
        rule('R-next', [type('urn:test:HighRisk')], [type('urn:test:Inspect')]),
        existing,
      ),
    ).toEqual([
      { producerRuleId: 'R-risk', consumerRuleId: 'R-next' },
      { producerRuleId: 'R-next', consumerRuleId: 'R-next' },
    ])
    // A type read matches any producer conclusion (and the enabled draft itself).
    expect(
      detectRuleChainDependencies(
        rule('R-any', [type('urn:test:Unrelated')], [type('urn:test:Out')]),
        existing,
      ),
    ).toEqual([
      { producerRuleId: 'R-risk', consumerRuleId: 'R-any' },
      { producerRuleId: 'R-any', consumerRuleId: 'R-any' },
    ])
    // rdf:type property rows are type signatures; compare rows never read.
    const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    expect(
      detectRuleChainDependencies(
        rule(
          'R-via-path',
          [property(rdfType, '<urn:test:HighRisk>')],
          [property('urn:test:tag', '"yes"')],
        ),
        existing,
      ),
    ).toEqual([
      { producerRuleId: 'R-risk', consumerRuleId: 'R-via-path' },
      { producerRuleId: 'R-via-path', consumerRuleId: 'R-via-path' },
    ])
    // Disjoint property signatures without a type read stay silent, including self.
    expect(
      detectRuleChainDependencies(
        rule('R-quiet', [property('urn:test:risk', '"High"')], [property('urn:test:tag', '"yes"')]),
        [rule('R-risk', [type('urn:test:Equipment')], [type('urn:test:HighRisk')])],
      ),
    ).toEqual([])
    // Disabled drafts lose the self chain; editing a rule replaces its saved copy.
    expect(
      detectRuleChainDependencies(
        rule('R-risk', [type('urn:test:Equipment')], [type('urn:test:HighRisk')], false),
        [rule('R-risk', [type('urn:test:Equipment')], [type('urn:test:HighRisk')])],
      ),
    ).toEqual([])
    // Disabled existing rules are never producers; only the enabled self remains.
    expect(
      detectRuleChainDependencies(
        rule('R-next', [type('urn:test:OffOut')], [type('urn:test:Inspect')]),
        [rule('R-off', [type('urn:test:Off')], [type('urn:test:OffOut')], false)],
      ),
    ).toEqual([{ producerRuleId: 'R-next', consumerRuleId: 'R-next' }])
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
