import { createHash, randomUUID } from 'node:crypto'
import { setTimeout as delay } from 'node:timers/promises'
import {
  agentScopeToQueryScope,
  type AgentScope,
  type BridgeResult,
  type JobView,
  type MainlineChangePlanDTO,
  type QualityRunReceiptDTO,
  type QueryDraftDTO,
  type QuerySelectionDTO,
} from '@ontolearn/contracts'
import { normalizeQueryDraft } from '@ontolearn/contracts/v2'
import { z } from 'zod'
import type { ProjectMainlineService } from '../project-mainline-service'
import type { TaskService } from '../task-service'
import type { DomainPort, Evidence, TrustedContext } from './agent-service'
import { AgentError } from './errors'
import { decodeQueryDraftProposal } from './query-draft/proposal'
import { argumentSchemas, toolAccess, toolNames, type ToolName } from './tools'

/** 正式写入项目真相的唯一通道是 project:changeset-commit；Agent 严禁拥有正式写工具。 */
export const FORMAL_WRITE_TOOLS: readonly ToolName[] = Object.freeze([])

const waveFour: readonly ToolName[] = ['mapping_propose', 'behavior_test', 'scenario_run']
const ontologyIri = z
  .string()
  .max(512)
  .regex(/^(?:https?:\/\/[A-Za-z0-9][A-Za-z0-9._~:/#%-]*|urn:[A-Za-z0-9][A-Za-z0-9._~:/#%-]*)$/)
const tripleSchema = z.strictObject({
  subject: ontologyIri,
  predicate: ontologyIri,
  object: z
    .string()
    .max(514)
    .refine(
      (value) =>
        value.startsWith('<') &&
        value.endsWith('>') &&
        ontologyIri.safeParse(value.slice(1, -1)).success,
    ),
})
const ontologyInstruction = z.strictObject({
  classIri: ontologyIri,
  parentIri: ontologyIri.optional(),
})
const ontologyDetailSchema = ontologyInstruction.extend({ kind: z.literal('ontology-class') })
const queryDetailSchema = z.strictObject({
  name: z.string().min(1).max(128),
  description: z.string().max(4096),
  sparql: z.string().min(1).max(8000),
  scope: z.enum(['asserted', 'asserted+derived']),
  capabilityQuestion: z.string().max(4096),
  source: z.literal('model'),
})
const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
const owlClass = '<http://www.w3.org/2002/07/owl#Class>'
const subClassOf = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
const protocolId = z.string().regex(/^[A-Za-z0-9:_-]{1,128}$/)

type PortsDependencies = {
  projects: Pick<
    ProjectMainlineService,
    'readProject' | 'getProjectQualityState' | 'runProjectQualityCheck'
  > & {
    queries: Pick<
      ProjectMainlineService['queries'],
      'loadQueryDefinition' | 'executeSavedQuery' | 'getQueryResultDescriptor'
    >
  }
  tasks: Pick<TaskService, 'getJob' | 'getResult'>
  receive<T>(work: () => Promise<BridgeResult<T>>): Promise<BridgeResult<T>>
  current(context: TrustedContext): boolean
  scope: AgentScope
  objectRefs?: ReadonlyMap<string, string>
}

function take<T>(result: BridgeResult<T>): T {
  if (result.ok) return result.data
  throw new AgentError('TOOL_FAILED')
}

function decode<T>(schema: z.ZodType<T>, text: string): T {
  try {
    return schema.parse(JSON.parse(text))
  } catch {
    throw new AgentError('INVALID_TOOL_ARGUMENTS')
  }
}

export function draftDetailToPlan(
  draftType: 'ontology' | 'mapping' | 'query',
  detail: string,
): MainlineChangePlanDTO {
  const id = 'agent-' + createHash('sha256').update(detail).digest('hex')
  if (draftType === 'ontology') {
    const { classIri, parentIri } = decode(ontologyDetailSchema, detail)
    const triples = [{ subject: classIri, predicate: rdfType, object: owlClass }]
    if (parentIri)
      triples.push({ subject: classIri, predicate: subClassOf, object: `<${parentIri}>` })
    return { definitions: [{ layer: 'ontology', id, value: { triples } }] }
  }
  if (draftType === 'query') {
    const normalized = normalizeQueryDraft(decode(queryDetailSchema, detail))
    if (!normalized) throw new AgentError('INVALID_TOOL_ARGUMENTS')
    const { sparql, ...descriptor } = queryDetailSchema.parse(normalized)
    return {
      definitions: [
        {
          layer: 'query',
          id,
          value: { text: sparql, references: [], descriptor: { ...descriptor, version: 1 } },
        },
      ],
    }
  }
  throw new AgentError('TOOL_UNAVAILABLE')
}

function evidence(
  context: TrustedContext,
  resultId: string,
  inputSnapshotId: string,
  status: Evidence['status'],
  fields: Evidence['fields'] = [],
): Evidence {
  if (!protocolId.safeParse(resultId).success || !protocolId.safeParse(inputSnapshotId).success)
    throw new AgentError('INVALID_EVIDENCE')
  return {
    kind: 'evidence',
    projectId: context.projectId,
    inputSnapshotId,
    scopeRef: context.scopeRef,
    resultId,
    status,
    traceRefs: [],
    fields,
  }
}

export class AgentToolRegistry {
  constructor(private readonly dependencies: PortsDependencies) {}

  entries() {
    return toolNames.map((name) => {
      const enabled = !waveFour.includes(name)
      return {
        name,
        access: toolAccess[name],
        wave: enabled ? (3 as const) : (4 as const),
        enabled,
      }
    })
  }

  buildPorts(): Partial<Record<ToolName, DomainPort>> {
    return Object.fromEntries(
      this.entries()
        .filter(({ enabled }) => enabled)
        .map(({ name }) => [
          name,
          {
            execute: (context, args, signal) => this.execute(name, context, args, signal),
          } satisfies DomainPort,
        ]),
    )
  }

  private guard(context: TrustedContext, signal: AbortSignal): void {
    if (!this.dependencies.current(context)) throw new AgentError('STALE_CONTEXT')
    if (signal.aborted) throw new AgentError('CANCELLED')
  }

  async execute(name: ToolName, context: TrustedContext, args: unknown, signal: AbortSignal) {
    if (waveFour.includes(name)) throw new AgentError('TOOL_UNAVAILABLE')
    const check = () => this.guard(context, signal)
    const run = async <T>(action: () => Promise<BridgeResult<T>>, mainline = true): Promise<T> => {
      check()
      const result = await (mainline ? this.dependencies.receive(action) : action())
      check()
      return take(result)
    }
    const parse = <N extends ToolName>(tool: N) => {
      const result = argumentSchemas[tool].safeParse(args)
      if (!result.success) throw new AgentError('INVALID_TOOL_ARGUMENTS')
      return result.data as z.infer<(typeof argumentSchemas)[N]>
    }
    const range = (scope: 'asserted' | 'asserted-and-derived' | 'selected-history') => {
      const value = agentScopeToQueryScope(scope, context.inputSnapshotId)
      if (value.scope === 'asserted+derived' && this.dependencies.scope !== value.scope)
        throw new AgentError('TOOL_NOT_ALLOWED')
      return value
    }
    const state = () => run(() => this.dependencies.projects.readProject({ editor: 'ontology' }))
    const readResult = async (resultId: string, selection?: QuerySelectionDTO) => {
      const result = await run(() => this.dependencies.tasks.getResult(resultId), false)
      if (
        result.projectId !== context.projectId ||
        result.resultId !== resultId ||
        result.scope === 'scenario' ||
        (result.scope === 'asserted+derived' && this.dependencies.scope !== result.scope)
      )
        throw new AgentError('TOOL_NOT_ALLOWED')
      if (
        (selection?.kind === 'historical' && result.inputSnapshotId !== selection.snapshotId) ||
        (result.state === 'historical' && result.inputSnapshotId !== context.inputSnapshotId)
      )
        throw new AgentError('TOOL_NOT_ALLOWED')
      const status =
        result.state === 'current' && result.inputSnapshotId !== context.inputSnapshotId
          ? 'stale'
          : result.state
      return evidence(context, result.resultId, result.inputSnapshotId, status, [
        { fieldId: 'result-kind', value: result.kind },
        { fieldId: 'input-revision', value: result.inputProjectRevision },
        { fieldId: 'payload-available', value: result.payloadStatus === 'available' },
      ])
    }

    check()
    switch (name) {
      case 'ontology_read': {
        const { objectIds } = parse(name)
        if (objectIds.some((id) => !context.selectedObjectIds.includes(id)))
          throw new AgentError('TOOL_NOT_ALLOWED')
        const project = await state()
        if (
          project.projectId !== context.projectId ||
          project.domain.projectRevision !== context.projectRevision ||
          project.inputSnapshotId !== context.inputSnapshotId
        )
          throw new AgentError('STALE_CONTEXT')
        const selected = new Set(objectIds.map((id) => this.dependencies.objectRefs?.get(id) ?? id))
        const triples: z.infer<typeof tripleSchema>[] = []
        const add = (input: unknown, definitionSelected: boolean) => {
          if (triples.length >= 24) return
          const triple = tripleSchema.safeParse(input)
          if (triple.success && (definitionSelected || selected.has(triple.data.subject)))
            triples.push(triple.data)
        }
        for (const definition of project.domain.state.definitions) {
          if (definition.layer !== 'ontology') continue
          const payload = JSON.parse(definition.payload) as { triples?: unknown[] }
          for (const triple of payload.triples ?? []) add(triple, selected.has(definition.id))
        }
        for (const { id, subject, predicate, object } of project.domain.state.facts)
          add({ subject, predicate, object }, selected.has(id))
        const fields = triples.flatMap((triple, index) =>
          Object.entries(triple).map(([field, value]) => ({
            fieldId: `triple-${index}-${field}`,
            value,
          })),
        )
        return evidence(
          context,
          context.inputSnapshotId,
          context.inputSnapshotId,
          'current',
          fields,
        )
      }
      case 'ontology_propose': {
        const proposal = decode(ontologyInstruction, parse(name).instruction)
        const detail = JSON.stringify({ kind: 'ontology-class', ...proposal })
        return {
          kind: 'draft',
          draftType: 'ontology',
          summary: proposal.parentIri ? '建议新增本体类及其父类关系' : '建议新增本体类',
          detail,
        }
      }
      case 'query_draft': {
        const { question, scope } = parse(name)
        const { draft } = decodeQueryDraftProposal(
          { role: 'assistant', content: question },
          { inputContext: context, queryScope: range(scope).scope },
        )
        const detail = JSON.stringify(queryDetailSchema.parse(draft))
        return { kind: 'draft', draftType: 'query', summary: '建议保存只读查询草稿', detail }
      }
      case 'query_execute': {
        const { sparql, scope } = parse(name)
        const { scope: queryScope, selection } = range(scope)
        const project = await state()
        if (
          project.projectId !== context.projectId ||
          project.domain.projectRevision !== context.projectRevision ||
          project.inputSnapshotId !== context.inputSnapshotId
        )
          throw new AgentError('STALE_CONTEXT')
        const candidates = project.domain.state.definitions.filter(
          ({ layer, id }) =>
            layer === 'query' &&
            context.selectedObjectIds.some(
              (ref) => (this.dependencies.objectRefs?.get(ref) ?? ref) === id,
            ),
        )
        for (const { id } of candidates) {
          const loaded = await run(() =>
            this.dependencies.projects.queries.loadQueryDefinition({
              definitionId: id,
              selection,
            }),
          )
          if (
            loaded.projectId !== context.projectId ||
            loaded.inputSnapshotId !== context.inputSnapshotId
          )
            throw new AgentError('STALE_CONTEXT')
          if (loaded.kind !== 'managed' || !matchesQuery(loaded.draft, sparql, queryScope)) continue
          const operationId = randomUUID()
          const receipt = await run(() =>
            this.dependencies.projects.queries.executeSavedQuery({
              operationId,
              loadRef: loaded.loadRef,
              visibleDraft: loaded.draft,
              selection,
            }),
          )
          const job = await this.waitForJob(receipt.acceptedJob, context, signal)
          if (job.state !== 'succeeded') return this.jobEvidence(context, job)
          if (!job.resultRef) throw new AgentError('INVALID_EVIDENCE')
          const result = await readResult(job.resultRef.resultId, selection)
          const descriptor = await run(() =>
            this.dependencies.projects.queries.getQueryResultDescriptor({
              resultId: job.resultRef!.resultId,
            }),
          )
          if (
            descriptor.identity.projectId !== context.projectId ||
            descriptor.identity.jobId !== job.jobId ||
            descriptor.identity.resultId !== result.resultId ||
            descriptor.identity.scope !== queryScope ||
            descriptor.identity.inputSnapshotId !== context.inputSnapshotId ||
            descriptor.identity.inputSelection !== selection.kind ||
            descriptor.metadata.state !== result.status
          )
            throw new AgentError('INVALID_EVIDENCE')
          const { query } = descriptor
          result.fields.push(
            query.kind === 'ASK'
              ? { fieldId: 'ask-value', value: query.value }
              : { fieldId: 'row-count', value: query.rowCount },
          )
          return result
        }
        throw new AgentError('TOOL_NOT_ALLOWED')
      }
      case 'quality_check':
      case 'reasoning_run': {
        const { scope, selection } = range(parse(name).scope)
        const { projectId } = context
        if (name === 'reasoning_run' && selection.kind === 'current') {
          const existing = await run(() =>
            this.dependencies.projects.getProjectQualityState({ projectId }),
          )
          if (existing.projectId !== projectId) throw new AgentError('INVALID_EVIDENCE')
          if (
            existing.reasoning?.state === 'current' &&
            existing.reasoning.inputSnapshotId === context.inputSnapshotId
          )
            return evidence(
              context,
              existing.reasoning.resultId,
              context.inputSnapshotId,
              'current',
            )
        }
        const receipt = await run(() =>
          this.dependencies.projects.runProjectQualityCheck({
            projectId,
            operationId: randomUUID(),
            selection,
            validationScope: scope,
          }),
        )
        return this.qualityEvidence(context, receipt, name === 'reasoning_run')
      }
      case 'result_read': {
        const { resultId } = parse(name)
        if (!context.selectedObjectIds.includes(resultId)) throw new AgentError('TOOL_NOT_ALLOWED')
        return readResult(this.dependencies.objectRefs?.get(resultId) ?? resultId)
      }
      default:
        throw new AgentError('TOOL_UNAVAILABLE')
    }
  }

  private async waitForJob(
    job: JobView,
    context: TrustedContext,
    signal: AbortSignal,
  ): Promise<JobView> {
    const { jobId, operationId } = job
    while (true) {
      this.guard(context, signal)
      if (
        job.projectId !== context.projectId ||
        job.jobId !== jobId ||
        job.operationId !== operationId ||
        job.inputSnapshotId !== context.inputSnapshotId
      )
        throw new AgentError('INVALID_EVIDENCE')
      if (job.state === 'succeeded' || job.state === 'failed' || job.state === 'cancelled')
        return job
      await delay(100, undefined, { signal })
      this.guard(context, signal)
      job = take(await this.dependencies.tasks.getJob(jobId))
    }
  }

  private jobEvidence(context: TrustedContext, job: JobView): Evidence {
    if (
      job.projectId !== context.projectId ||
      job.inputSnapshotId !== context.inputSnapshotId ||
      (job.state !== 'failed' && job.state !== 'cancelled')
    )
      throw new AgentError('INVALID_EVIDENCE')
    return evidence(context, job.jobId, job.inputSnapshotId, job.state)
  }

  private qualityEvidence(
    context: TrustedContext,
    receipt: QualityRunReceiptDTO,
    reasoningOnly: boolean,
  ) {
    if (
      receipt.projectId !== context.projectId ||
      receipt.qualityState.projectId !== context.projectId
    )
      throw new AgentError('INVALID_EVIDENCE')
    const jobs = reasoningOnly
      ? [receipt.reasoningJob]
      : [receipt.reasoningJob, ...receipt.validationJobs]
    const failed = jobs.find((job) => job.state === 'failed' || job.state === 'cancelled')
    if (failed) return this.jobEvidence(context, failed)
    const result = reasoningOnly ? receipt.qualityState.reasoning : receipt.qualityState.validation
    if (
      !result ||
      !jobs.some((job) => job.state === 'succeeded' && job.resultRef?.resultId === result.resultId)
    )
      throw new AgentError('INVALID_EVIDENCE')
    return evidence(context, result.resultId, result.inputSnapshotId, result.state)
  }
}

function matchesQuery(draft: QueryDraftDTO, sparql: string, scope: AgentScope): boolean {
  return draft.scope === scope && normalizeQueryDraft({ ...draft, sparql })?.sparql === draft.sparql
}
