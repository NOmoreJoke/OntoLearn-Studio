import type {
  DesktopBridge,
  MainlineChangePlanDTO,
  MainlineProjectReadDTO,
  QualityFr505PatternDTO,
} from '@ontolearn/contracts'
import { newManualFactPlan } from '../ontology/mainline-facts'
import {
  commitWorkspaceChange,
  prepareWorkspaceChange,
  requireWorkspaceReply,
  type WorkspaceChangePreview,
} from '../ontology/workspace-change'
import { learningFixtureData, type LearningFixtureTaskId } from './content'

export type { LearningFixtureTaskId } from './content'

const RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const LEARNING = 'urn:ontolearn:learning:'
const OWL_CLASS = '<http://www.w3.org/2002/07/owl#Class>'
const RDFS_CLASS = '<http://www.w3.org/2000/01/rdf-schema#Class>'

type Statement = { subject: string; predicate: string; object: string }
type FixtureBridge = Pick<
  DesktopBridge,
  'readProject' | 'previewProjectChangeset' | 'getProjectDiffPage'
>

function sameStatement(
  left: Statement,
  right: Omit<Statement, 'object'> & { object: string | null },
) {
  return (
    left.subject === right.subject &&
    left.predicate === right.predicate &&
    (left.object === right.object ||
      (left.predicate === RDF_TYPE && left.object === RDFS_CLASS && right.object === OWL_CLASS))
  )
}

function formalPattern(statement: Statement): QualityFr505PatternDTO {
  return statement.predicate === RDF_TYPE
    ? { kind: 'type', subject: statement.subject, class: statement.object.slice(1, -1) }
    : {
        kind: 'property',
        subject: statement.subject,
        path: statement.predicate,
        object: statement.object,
      }
}

export async function buildLearningFixturePlan(
  source: MainlineProjectReadDTO,
  taskId: LearningFixtureTaskId,
): Promise<MainlineChangePlanDTO | undefined> {
  const current = source.domain.state
  const definitions: NonNullable<MainlineChangePlanDTO['definitions']> = []
  const input = learningFixtureData(taskId)
  let ontology = input.ontology
  let facts = input.facts

  if (taskId === 'quality') {
    if (
      !current.facts.some(
        (fact) =>
          fact.subject === `${LEARNING}equipment/001` &&
          fact.predicate === RDF_TYPE &&
          fact.object === `<${LEARNING}Equipment>`,
      )
    ) {
      throw new Error('LEARNING_FIXTURE_REQUIRES_G_BASE')
    }
    const currentOntology: Statement[] = current.definitions
      .filter(({ layer }) => layer === 'ontology')
      .flatMap(({ payload }) => JSON.parse(payload).triples ?? [])
    ontology = ontology.filter(
      (statement) => !currentOntology.some((existing) => sameStatement(statement, existing)),
    )
    facts = facts.filter(
      (statement) => !current.facts.some((existing) => sameStatement(statement, existing)),
    )
  } else {
    if (current.definitions.length || current.facts.length)
      throw new Error('LEARNING_FIXTURE_REQUIRES_BLANK_PROJECT')
    if ('constraints' in input) {
      for (const constraint of input.constraints) {
        definitions.push({
          layer: 'constraint',
          id: constraint.id,
          value: {
            schemaVersion: 1,
            kind: 'constraint',
            id: constraint.id,
            revision: 1,
            label: '设备名称必填',
            enabled: true,
            targetClass: constraint.targetClass,
            path: constraint.path,
            template: 'required',
            parameters: {},
          },
        })
      }
    }
    if ('rules' in input) {
      for (const rule of input.rules) {
        definitions.push({
          layer: 'rule',
          id: rule.id,
          value: {
            schemaVersion: 1,
            kind: 'rule',
            id: rule.id,
            revision: rule.version,
            label: '识别高风险设备',
            enabled: rule.enabled,
            conditions: rule.conditions.map(formalPattern),
            conclusions: rule.conclusions.map(formalPattern),
          },
        })
      }
    }
  }
  if (ontology.length) {
    definitions.unshift({
      layer: 'ontology',
      id: taskId === 'quality' ? `learning-lx01.${crypto.randomUUID()}` : `${taskId}.ontology`,
      value: { triples: ontology },
    })
  }
  if (!definitions.length && !facts.length) return undefined
  const manual = await Promise.all(facts.map((fact) => newManualFactPlan(source, fact)))
  return { definitions, manual: manual.flatMap((plan) => plan.manual ?? []) }
}

export async function prepareLearningTaskFixture(
  bridge: FixtureBridge,
  projectId: string,
  taskId: LearningFixtureTaskId,
  requireCurrent: () => void,
): Promise<WorkspaceChangePreview | undefined> {
  requireCurrent()
  const source = requireWorkspaceReply(await bridge.readProject({ editor: 'quality' }))
  requireCurrent()
  if (source.projectId !== projectId) throw new Error('STALE_CONTEXT')
  const plan = await buildLearningFixturePlan(source, taskId)
  if (!plan) return undefined
  return prepareWorkspaceChange(bridge, source, plan, requireCurrent)
}

export const commitLearningTaskFixture = commitWorkspaceChange
