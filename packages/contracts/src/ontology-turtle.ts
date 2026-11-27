import { z } from 'zod'
import type { MainlineChangePlanDTO } from './index'

type OntologyTurtleUnsupportedCode =
  | 'UNSUPPORTED_OWL'
  | 'UNSUPPORTED_RDFS'
  | 'UNSUPPORTED_SHACL'
  | 'UNSUPPORTED_SHACL_PATH'
  | 'UNSUPPORTED_BLANK_NODE'
  | 'UNSUPPORTED_LITERAL_DATATYPE'
type OntologyTurtleInvalidCode = 'INVALID_TURTLE' | 'UNSUPPORTED_FORMAT'

export type OntologyTurtleRejectionCode = OntologyTurtleUnsupportedCode | OntologyTurtleInvalidCode
export type OntologyTurtleRejectionItem<
  Code extends OntologyTurtleRejectionCode = OntologyTurtleRejectionCode,
> = {
  code: Code
  field: string
  detail: string
}

export type OntologyTurtleExportResultDTO =
  | {
      status: 'ok'
      turtle: string
      tripleCount: number
      inputSnapshotId: string
      projectRevision: number
    }
  | { status: 'rejected'; reasons: OntologyTurtleRejectionItem<OntologyTurtleUnsupportedCode>[] }

export const ontologyTurtleImportCheckArgsSchema = z.strictObject({
  baseUri: z.string().min(1).max(4096),
  turtleText: z.string().max(262144),
  format: z.literal('turtle').optional(),
})
export type OntologyTurtleImportCheckArgs = z.infer<typeof ontologyTurtleImportCheckArgsSchema>

export type OntologyTurtleImportSummaryDTO = {
  baseRevision: number
  inputSnapshotId: string
  tripleCount: number
  definitionCount: number
  manualFactCount: number
}
export type OntologyTurtleImportPlanDTO = {
  definitions?: Array<
    Extract<
      NonNullable<MainlineChangePlanDTO['definitions']>[number],
      { layer: 'ontology' | 'constraint' }
    >
  >
  manual?: MainlineChangePlanDTO['manual']
}

export type OntologyTurtleImportCheckResultDTO =
  | {
      status: 'ok'
      summary: OntologyTurtleImportSummaryDTO
      plan: OntologyTurtleImportPlanDTO
    }
  | { status: 'rejected'; reasons: OntologyTurtleRejectionItem<OntologyTurtleUnsupportedCode>[] }
  | { status: 'invalid'; reasons: OntologyTurtleRejectionItem<OntologyTurtleInvalidCode>[] }
