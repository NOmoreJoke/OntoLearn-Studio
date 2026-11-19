import {
  BehaviorAdapterContract,
  behaviorPublicErrorKeys,
  type BehaviorBridge,
  type BehaviorDiffItem,
  type BehaviorEvent,
  type BehaviorExpression,
  type BehaviorPublicErrorCode,
  type BehaviorReadArgs,
  type BehaviorRunArgs,
  type BehaviorRunResultDTO,
  type MainlineProjectReadDTO,
} from '@ontolearn/contracts'
import { validateBusiness3 } from '@ontolearn/contracts/v2'
import { withoutLocalPaths } from '../mapping/local-text'
import {
  draftSchema,
  type BehaviorResult,
  type BehaviorServices,
  type Binding,
  type Catalog,
  type SampleRequest,
  type Value,
} from './model'

const rdfType = BehaviorAdapterContract.actions.create.classProperty
const owl = 'http://www.w3.org/2002/07/owl#'
const rdfs = 'http://www.w3.org/2000/01/rdf-schema#'
type SnapshotCatalog = Catalog & { relations: ReadonlySet<string>; typeAssertions: boolean }
const iriTerm = (value: string) =>
  value.startsWith('<') && value.endsWith('>') ? value.slice(1, -1) : value
export function readBehaviorCatalog(source: MainlineProjectReadDTO): SnapshotCatalog {
  const classes = new Set<string>()
  const propertyTypes = new Map<string, Set<string>>()
  const singles = new Set<string>()
  const behaviors: string[] = []
  for (const definition of source.domain.state.definitions) {
    if (definition.layer === 'behavior') behaviors.push(definition.id)
    if (definition.layer !== 'ontology') continue
    const value = JSON.parse(definition.payload) as {
      triples: { subject: string; predicate: string; object: string }[]
      singleValuedPredicates?: string[]
    }
    for (const predicate of value.singleValuedPredicates ?? []) singles.add(predicate)
    for (const triple of value.triples) {
      if (iriTerm(triple.predicate) !== rdfType) continue
      const kind = iriTerm(triple.object)
      const subject = iriTerm(triple.subject)
      if (kind === owl + 'Class' || kind === rdfs + 'Class') classes.add(subject)
      if (kind === owl + 'ObjectProperty' || kind === owl + 'DatatypeProperty') {
        const declared = propertyTypes.get(subject) ?? new Set()
        declared.add(kind)
        propertyTypes.set(subject, declared)
      }
    }
  }
  const relations = new Set<string>()
  const properties: Catalog['properties'][number][] = []
  for (const [id, kinds] of propertyTypes) {
    if (kinds.size !== 1) continue
    if (kinds.has(owl + 'ObjectProperty')) relations.add(id)
    properties.push({ id, kind: singles.has(id) ? 'single' : 'multi' })
  }
  const typeAssertions = classes.size > 0
  if (typeAssertions)
    properties.push({ id: rdfType, kind: singles.has(rdfType) ? 'single' : 'multi' })
  const objects = new Set<string>()
  for (const fact of source.domain.state.facts) {
    objects.add(iriTerm(fact.subject))
    if (fact.object?.startsWith('<') && relations.has(iriTerm(fact.predicate)))
      objects.add(iriTerm(fact.object))
  }
  return {
    classes: [...classes],
    objects: [...objects],
    properties,
    relations,
    typeAssertions,
    behaviorIds: behaviors,
  }
}

export class PublicBehaviorError extends Error {
  constructor(readonly code: BehaviorPublicErrorCode) {
    super(behaviorPublicErrorKeys[code])
  }
}
function reject(reason: string, phase: 'run' | 'cancel' = 'run'): never {
  throw new PublicBehaviorError(BehaviorAdapterContract.projectError(reason, phase).code)
}
const literal = (value: Value): BehaviorExpression => ({ kind: 'value', value })
const iri = (value: string) => literal({ kind: 'iri', value })
const stringValue = (value: string) => literal({ kind: 'string', value })
type BoundRequest = Omit<BehaviorReadArgs, 'projectId'>
export function lowerBehaviorSample(
  request: SampleRequest,
  catalog: SnapshotCatalog,
  baseRevision: number,
  runId: string,
  operationId: string,
): Omit<BehaviorRunArgs, 'projectId'> {
  const parsed = draftSchema.safeParse(request.draft)
  if (!parsed.success) reject('invalid_shape')
  const draft = parsed.data
  const properties = new Map(catalog.properties.map(({ id, kind }) => [id, kind]))
  const trigger = {
    eventType: draft.trigger,
    ...(draft.triggerEventId ? { eventId: draft.triggerEventId } : {}),
  }
  const events: BehaviorEvent[] = request.events.map((event, sequence) => {
    if (
      BehaviorAdapterContract.event.reservedPayloadKeys.some((key) =>
        Object.hasOwn(event.payload, key),
      )
    )
      reject('invalid_shape')
    if (event.version === undefined || !Number.isSafeInteger(event.version) || event.version < 1)
      reject('invalid_shape')
    return {
      id: event.id,
      type: event.type,
      sequence,
      version: event.version,
      payload: event.payload,
      edits: [
        ...(event.objectEdits ?? []),
        ...event.changes.map(({ operation, object, property, value }) => {
          admitWrite(operation, property, value)
          return { kind: operation, subject: object, property, value }
        }),
      ],
    }
  })
  if (
    !events.some(
      (event) =>
        event.type === trigger.eventType && (!trigger.eventId || trigger.eventId === event.id),
    )
  )
    reject('missing_trigger')
  function admitWrite(kind: 'set' | 'add' | 'remove', property: string, value: Value) {
    const cardinality = properties.get(property)
    if (
      !cardinality ||
      (kind === 'set' && cardinality !== 'single') ||
      (kind === 'add' && cardinality !== 'multi')
    )
      reject('cardinality_action_mismatch')
    admitValue(property, value)
  }
  function admitValue(property: string, value: Value) {
    if (property === rdfType) {
      if (value.kind !== 'iri' || !catalog.classes.includes(value.value)) reject('invalid_class')
    } else if (catalog.relations.has(property) !== (value.kind === 'iri')) reject('invalid_scalar')
  }
  const conditions = draft.conditions.map((condition) => {
    if (condition.kind !== 'always' && condition.kind !== 'type' && condition.kind !== 'exists') {
      if (!properties.has(condition.property)) reject('invalid_property')
      admitValue(condition.property, condition.value)
    }
    const wire =
      condition.kind === 'always'
        ? { op: 'always' as const }
        : condition.kind === 'type'
          ? { op: 'type' as const, subject: iri(condition.object), classId: condition.classId }
          : condition.kind === 'exists'
            ? {
                op: 'exists' as const,
                subject: iri(condition.object),
                property: condition.property,
              }
            : {
                op: condition.kind,
                subject: iri(condition.object),
                property: condition.property,
                value: literal(condition.value),
              }
    const lowered = BehaviorAdapterContract.lowerCondition(
      wire,
      catalog.typeAssertions &&
        (condition.kind !== 'type' || catalog.classes.includes(condition.classId)),
    )
    if (!lowered.ok) throw new PublicBehaviorError(lowered.error.code)
    return lowered.condition
  })
  const actions: BehaviorRunArgs['draft']['actions'] = draft.actions.map((action) => {
    switch (action.kind) {
      case 'create': {
        if (!catalog.typeAssertions || !catalog.classes.includes(action.classId))
          reject('unavailable_action')
        const initial = (action.initial ?? []).map(({ property, value }) => {
          if (!properties.has(property)) reject('invalid_property')
          admitValue(property, value)
          if (property === rdfType && value.value !== action.classId) reject('invalid_class')
          return { property, value: literal(value) }
        })
        if (!initial.some(({ property }) => property === rdfType))
          initial.push({ property: rdfType, value: iri(action.classId) })
        return { kind: 'create', object: iri(action.object), initial }
      }
      case 'update':
        admitWrite('set', action.property, action.value)
        return {
          kind: 'set',
          subject: iri(action.object),
          property: action.property,
          value: literal(action.value),
        }
      case 'relate':
        admitWrite('add', action.property, { kind: 'iri', value: action.target })
        return {
          kind: 'add',
          subject: iri(action.object),
          property: action.property,
          value: iri(action.target),
        }
      case 'notify':
        return { kind: 'notify', message: stringValue(action.message) }
    }
  })
  const binding = {
    projectId: request.binding.projectId,
    baseRevision,
    inputSnapshotId: request.binding.inputVersion,
    behaviorVersion: String(draft.version),
    scopeId: request.binding.scopeId,
    requestId: request.binding.requestId,
  }
  const args = {
    binding,
    runId,
    operationId,
    scope: 'sample' as const,
    draft: {
      id: draft.id,
      name: draft.name,
      description: draft.description,
      effect: draft.effect,
      enabled: draft.enabled,
      priority: draft.priority,
      version: draft.version,
      trigger,
      actions,
      conditions,
    },
    events,
  }
  if (!validateBusiness3('params_project.behavior.run', { projectId: binding.projectId, ...args }))
    reject('invalid_shape')
  return args
}

const staleReasons: Record<NonNullable<BehaviorRunResultDTO['staleReason']>, string> = {
  'project-revision-changed': '项目版本已变化',
  'snapshot-changed': '输入快照已变化',
  'behavior-version-changed': '行为版本已变化',
  'scope-replaced': '隔离副本已替换',
}
const triggerReasons = {
  triggered: '满足触发与条件',
  disabled: '行为未启用',
  event_mismatch: '事件不匹配',
  condition_not_satisfied: '冻结快照条件未满足',
}
const conditionReasons = {
  explicit_always: '显式恒真',
  frozen_snapshot: '冻结快照匹配',
  not_recorded_in_snapshot: '冻结快照中无匹配',
}

export function projectBehaviorResult(
  value: BehaviorRunResultDTO,
  expected: BoundRequest,
  local: Binding,
  phase: 'run' | 'read' | 'cancel',
): BehaviorResult {
  if (
    !validateBusiness3(`result_project.behavior.${phase}`, value) ||
    value.projectId !== expected.binding.projectId ||
    value.scope !== expected.scope ||
    value.runId !== expected.runId ||
    value.operationId !== expected.operationId ||
    Object.entries(expected.binding).some(
      ([key, entry]) => value.binding[key as keyof typeof expected.binding] !== entry,
    ) ||
    (phase === 'cancel' && value.state !== 'cancelled')
  )
    reject('invalid_shape', phase === 'cancel' ? 'cancel' : 'run')
  const diff = (items: BehaviorDiffItem[]) =>
    items.flatMap((item) =>
      item.kind === 'fact'
        ? [{ object: item.fact.subject, property: item.fact.property, value: item.fact.value }]
        : [],
    )
  const extraDiff = (items: BehaviorDiffItem[]) =>
    items.flatMap((item) => {
      if (item.kind === 'object') return [`对象 · ${item.objectId}`]
      if (item.kind === 'notification') {
        const { id, eventId, behaviorId, message } = item.notification
        return [`通知 · ${id} / ${eventId} / ${behaviorId} · ${withoutLocalPaths(message)}`]
      }
      return []
    })
  return {
    binding: local,
    runId: value.runId,
    state: value.state,
    committed: value.committed,
    assertionVersion: value.assertionVersion,
    inferenceVersion: value.inferenceVersion,
    semanticsVersion: value.semanticsVersion,
    freshness: value.freshness,
    freshnessDetail: value.staleReason ? staleReasons[value.staleReason] : '',
    conditions: value.conditions.map((item) => ({
      eventId: item.eventId,
      behaviorId: item.behaviorId,
      triggered: item.triggered,
      reason: [
        triggerReasons[item.reason],
        ...item.conditions.map(
          (condition) =>
            `#${condition.index + 1} ${condition.satisfied ? '满足' : '未满足'} · ${conditionReasons[condition.reason]}`,
        ),
      ].join('；'),
    })),
    actions: value.actions.map((item) => ({
      ...item,
      kind: ({ set: 'update', add: 'relate', create: 'create', notify: 'notify' } as const)[
        item.kind
      ],
      detail: '隔离样本动作',
    })),
    diff: { added: diff(value.diff.added), removed: diff(value.diff.removed) },
    extraDiff: { added: extraDiff(value.diff.added), removed: extraDiff(value.diff.removed) },
    notifications: value.notifications.map(({ eventId, behaviorId, message, state }) => ({
      eventId,
      behaviorId,
      message: withoutLocalPaths(message),
      state,
    })),
    error: value.error?.code ?? null,
  }
}

export function behaviorServices(
  bridge: BehaviorBridge,
  catalog: SnapshotCatalog,
  baseRevision: number,
): BehaviorServices {
  // The preallocated run identity is also available during the first in-flight call so
  // cancellation can reconcile the exact persisted run without re-sending any events.
  const requests = new Map<string, BoundRequest>()
  function bound(local: Binding, runId?: string) {
    const entry = requests.get(local.requestId)
    if (
      !entry ||
      (runId !== undefined && entry.runId !== runId) ||
      entry.binding.projectId !== local.projectId ||
      entry.binding.scopeId !== local.scopeId ||
      entry.binding.inputSnapshotId !== local.inputVersion
    )
      reject('invalid_shape')
    return entry
  }
  return {
    async runSample(request) {
      const args = lowerBehaviorSample(
        request,
        catalog,
        baseRevision,
        crypto.randomUUID(),
        crypto.randomUUID(),
      )
      const { binding, operationId, runId, scope } = args
      const identity = { binding, operationId, runId, scope }
      requests.clear()
      requests.set(binding.requestId, identity)
      const response = await bridge.runBehaviorSample(args)
      if (!response.ok) {
        if (
          response.error.code === 'UNSUPPORTED_CAPABILITY' ||
          response.error.code === 'PERMISSION_DENIED'
        )
          reject('unavailable_action')
        reject('execution_failed')
      }
      return projectBehaviorResult(response.data, identity, request.binding, 'run')
    },
    async refreshResult(local, runId) {
      const identity = bound(local, runId)
      const response = await bridge.readBehaviorRun(identity)
      if (!response.ok) reject('execution_failed')
      return projectBehaviorResult(response.data, identity, local, 'read')
    },
    async cancelSample(local) {
      const identity = bound(local)
      const response = await bridge.cancelBehaviorRun(identity)
      if (!response.ok) reject('cancel_failed', 'cancel')
      return projectBehaviorResult(response.data, identity, local, 'cancel')
    },
  }
}
