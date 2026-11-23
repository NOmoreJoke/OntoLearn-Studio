import type {
  BridgeResult,
  JobView,
  QueryExecutionIdentityDTO,
  QuerySelectionDTO,
  ResultScopeDTO,
} from './index'

export type QualityFr505PatternDTO =
  | { kind: 'type'; subject: string; class: string }
  | { kind: 'property'; subject: string; path: string; object: string }
  | {
      kind: 'compare'
      left: string
      operator: 'eq' | 'ne' | 'lt' | 'le' | 'gt' | 'ge'
      right: string
    }

export type QualityFr505TripleDTO = [string, string, string]

export type QualityRuleViewDTO = { id: string; enabled: boolean; revision?: number } & (
  | {
      format: 'fr505'
      label: string | null
      conditions: QualityFr505PatternDTO[]
      conclusions: QualityFr505PatternDTO[]
    }
  | { format: 'legacy'; when: QualityFr505TripleDTO[]; then: QualityFr505TripleDTO | null }
)

export type QualityConstraintViewDTO = { id: string; enabled: boolean; revision?: number } & (
  | {
      format: 'fr504'
      label: string | null
      targetClass: string | null
      path: string | null
      template: string | null
      parameters: Record<string, unknown>
    }
  | { format: 'turtle'; turtle: string | null }
)

type QualityDefinitionValueDTO = {
  schemaVersion: 1
  id: string
  revision: number
  label: string
  enabled: boolean
}

export type QualityRuleDefinitionDTO = {
  layer: 'rule'
  id: string
  value: QualityDefinitionValueDTO & {
    kind: 'rule'
    conditions: QualityFr505PatternDTO[]
    conclusions: QualityFr505PatternDTO[]
  }
}

export type QualityConstraintTemplateDTO =
  | { template: 'required'; parameters: Record<string, never> }
  | { template: 'datatype'; parameters: { datatype: string } }
  | { template: 'maxCount'; parameters: { maxCount: number } }
  | { template: 'allowedValues'; parameters: { values: string[] } }
  | {
      template: 'numericRange'
      parameters: { minInclusive: string | null; maxInclusive: string | null }
    }

export type QualityConstraintDefinitionDTO = {
  layer: 'constraint'
  id: string
  value: QualityDefinitionValueDTO & {
    kind: 'constraint'
    targetClass: string
    path: string
  } & QualityConstraintTemplateDTO
}

export type QualityFindingDTO = {
  tier: 'violation' | 'warning' | 'info'
  focusNode: string | null
  path: string | null
  constraint: string | null
  sourceShape: string | null
  value: string | null
  definitionId?: string
  targets: { subject: string | null; predicate: string | null; object: string | null }
}

export type QualityDerivationDTO = {
  executionSemanticsVersion: string | null
  rules: QualityFr505TripleDTO[]
  rdfs: QualityFr505TripleDTO[]
  ruleTraces: Array<{
    rule: string | null
    output: QualityFr505TripleDTO | null
    inputs: QualityFr505TripleDTO[]
  }>
  rdfsTraces: Array<{ output: QualityFr505TripleDTO; basis: QualityFr505TripleDTO[] }>
  warnings: string[]
}

export type QualityStaleReasonDTO = {
  code: string
  dependency: string
  before: number
  after: number
}

type QualityResultDTO = {
  resultId: string
  jobId: string
  state: 'current' | 'stale' | 'historical'
  staleReasons: QualityStaleReasonDTO[]
  inputSnapshotId: string
  scope: ResultScopeDTO
  definitionId: string
}

export type QualityRuleTestSampleRuleDTO = {
  id: string
  label: string
  enabled: boolean
  conditions: QualityFr505PatternDTO[]
  conclusions: QualityFr505PatternDTO[]
}

export type QualityRuleTestRequestDTO = {
  ontologyTriples?: QualityFr505TripleDTO[]
  inputTriples: QualityFr505TripleDTO[]
  rules: QualityRuleTestSampleRuleDTO[]
  expectedOutputs: QualityFr505TripleDTO[]
}

export type QualityRuleTestDiagnosticDTO = {
  stage: 'rule' | 'ontology' | 'input' | 'expected'
  index: number
  ruleId: string | null
  field: string
  code: string
  message: string
}

export type QualityConstraintVersionDTO = { definitionId: string; version: number }

export type QualityRuleTestResultDTO = {
  valid: boolean
  matchesExpected: boolean
  actualOutputs: QualityFr505TripleDTO[]
  rdfsOutputs: QualityFr505TripleDTO[]
  expectedOutputs: QualityFr505TripleDTO[]
  missingOutputs: QualityFr505TripleDTO[]
  unexpectedOutputs: QualityFr505TripleDTO[]
  ruleTraces: Array<{
    rule: string | null
    output: QualityFr505TripleDTO | null
    inputs: QualityFr505TripleDTO[]
  }>
  warnings: string[]
  diagnostics: QualityRuleTestDiagnosticDTO[]
  omittedDiagnosticCount?: number
}

export type ProjectQualityReadDTO = {
  qualityReadVersion: 1
  projectId: string
  rules: QualityRuleViewDTO[]
  constraints: QualityConstraintViewDTO[]
  reasoning: (QualityResultDTO & { derivation?: QualityDerivationDTO }) | null
  validation:
    | (QualityResultDTO & {
        conforms: boolean | null
        findings: QualityFindingDTO[]
        inputProjectRevision?: number
        checkedConstraintIds?: string[]
        unverifiedConstraintIds?: string[]
        failedConstraintIds?: string[]
        constraintVersions?: QualityConstraintVersionDTO[]
      })
    | null
  snapshotsAligned?: boolean | null
  ruleTestResult?: QualityRuleTestResultDTO | null
}

export type ProjectQualityReadArgs = {
  projectId: string
  ruleTest?: QualityRuleTestRequestDTO
}

export type QualityJobInputDTO = {
  inputSnapshotId: string
  scope: ResultScopeDTO
  definitionId: string
  parametersHash: string
  derivedResultIds: string[]
  preparedPlanRef: string | null
}

export type ProjectQualityPrepareDTO = {
  projectId: string
  operationId: string
  chain: ['reasoning.execute', 'validation.execute']
  reasoningInput: QualityJobInputDTO
  validationInput: QualityJobInputDTO | null
  validationInputs: QualityJobInputDTO[]
  executionIdentity: QueryExecutionIdentityDTO
}

export type QualityRunReceiptDTO = {
  qualityRunVersion: 1
  projectId: string
  operationId: string
  reasoningJob: JobView
  validationJobs: JobView[]
  qualityState: ProjectQualityReadDTO
}

export type ProjectQualityCheckArgs = {
  projectId: string
  operationId: string
  selection: QuerySelectionDTO
  validationScope?: 'asserted' | 'asserted+derived'
  constraintId?: string
}

export interface QualityWorkspaceBridge {
  getProjectQualityState(args: ProjectQualityReadArgs): Promise<BridgeResult<ProjectQualityReadDTO>>
  prepareProjectQualityCheck(
    args: ProjectQualityCheckArgs,
  ): Promise<BridgeResult<ProjectQualityPrepareDTO>>
  runProjectQualityCheck(args: ProjectQualityCheckArgs): Promise<BridgeResult<QualityRunReceiptDTO>>
}
