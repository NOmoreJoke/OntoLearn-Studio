import type { BridgeResult } from './index'

export type BehaviorPublicError =
  | {
      code: 'conflict'
      messageKey: 'behavior.conflict'
    }
  | {
      code: 'invalid_input'
      messageKey: 'behavior.invalidInput'
    }
  | {
      code: 'unavailable'
      messageKey: 'behavior.unavailable'
    }
  | {
      code: 'execution_failed'
      messageKey: 'behavior.executionFailed'
    }
  | {
      code: 'cancel_failed'
      messageKey: 'behavior.cancelFailed'
    }

export type BehaviorValue =
  | {
      kind: 'string'
      value: string
    }
  | {
      kind: 'iri'
      value: string
    }
  | {
      kind: 'boolean'
      value: boolean
    }
  | {
      kind: 'number'
      value: number
    }

export type BehaviorExpression =
  | {
      kind: 'value'
      value: BehaviorValue
    }
  | {
      kind: 'eventField'
      field: string
    }
  | {
      kind: 'eventId'
    }
  | {
      kind: 'instanceId'
      prefix: string
    }
  | {
      kind: 'eventTemplate'
      template: string
    }

export type BehaviorTrigger = {
  eventType: string
  eventId?: string
}

export type BehaviorCondition =
  | {
      op: 'always'
    }
  | {
      op: 'has' | 'equals'
      subject: BehaviorExpression
      property: string
      value: BehaviorExpression
    }
  | {
      op: 'exists'
      subject: BehaviorExpression
      property: string
    }
  | {
      op: 'type'
      subject: BehaviorExpression
      classId: string
    }

export type BehaviorAction =
  | {
      kind: 'create'
      object: BehaviorExpression
      classId?: string
      initial?: Array<{
        property: string
        value: BehaviorExpression
      }>
    }
  | {
      kind: 'set'
      subject: BehaviorExpression
      property: string
      value: BehaviorExpression
    }
  | {
      kind: 'add'
      subject: BehaviorExpression
      property: string
      value: BehaviorExpression
    }
  | {
      kind: 'notify'
      message: BehaviorExpression
      id?: BehaviorExpression
    }

export type BehaviorEventEdit =
  | {
      kind: 'create'
      object: string
      initial?: Array<{
        property: string
        value: BehaviorValue
      }>
    }
  | {
      kind: 'delete_object'
      object: string
    }
  | {
      kind: 'declare'
      object: string
    }
  | {
      kind: 'set' | 'add' | 'remove'
      subject: string
      property: string
      value: BehaviorValue
    }

export type BehaviorEvent = {
  id: string
  type: string
  sequence: number
  version: number
  payload: Record<string, null | boolean | string | number>
  edits: Array<BehaviorEventEdit>
}

export type BehaviorDraft = {
  id: string
  name: string
  description: string
  effect: string
  trigger: BehaviorTrigger
  enabled: boolean
  priority: number
  version: number
  conditions: Array<BehaviorCondition>
  actions: Array<BehaviorAction>
}

export type BehaviorBinding = {
  projectId: string
  baseRevision: number
  inputSnapshotId: string
  behaviorVersion: string
  scopeId: string
  requestId: string
}

export type IsolatedRunScope =
  | {
      mode: 'sample'
      scopeId: string
    }
  | {
      mode: 'scenario'
      scopeId: string
    }

export type BehaviorDiffItem =
  | {
      kind: 'object'
      objectId: string
    }
  | {
      kind: 'fact'
      fact: {
        subject: string
        property: string
        value: BehaviorValue
      }
    }
  | {
      kind: 'notification'
      notification: {
        id: string
        eventId: string
        behaviorId: string
        message: string
      }
    }

export type BehaviorDecisionDTO = {
  eventId: string
  behaviorId: string
  triggered: boolean
  reason: 'triggered' | 'disabled' | 'event_mismatch' | 'condition_not_satisfied'
  conditions: Array<{
    index: number
    satisfied: boolean
    reason: 'explicit_always' | 'frozen_snapshot' | 'not_recorded_in_snapshot'
  }>
}

type BehaviorRunProjection = {
  projectId: string
  operationId: string
  runId: string
  binding: BehaviorBinding
  scope: 'sample'
  freshness: 'current' | 'stale' | 'historical'
  staleReason:
    | null
    | 'project-revision-changed'
    | 'snapshot-changed'
    | 'behavior-version-changed'
    | 'scope-replaced'
  assertionVersion: string | null
  inferenceVersion: string | null
  semanticsVersion: string
  conditions: BehaviorDecisionDTO[]
}
type BehaviorActionTrace<State> = {
  eventId: string
  behaviorId: string
  index: number
  kind: BehaviorAction['kind']
  state: State
}
type BehaviorNotification<State> = Extract<
  BehaviorDiffItem,
  { kind: 'notification' }
>['notification'] & { state: State }
type BehaviorDiff = { added: BehaviorDiffItem[]; removed: BehaviorDiffItem[] }

export type BehaviorRunResultDTO = BehaviorRunProjection &
  (
    | {
        state: 'candidate'
        committed: false
        error: null
        assertionVersion: string
        inferenceVersion: string
        actions: BehaviorActionTrace<'planned' | 'deduplicated' | 'skipped'>[]
        diff: BehaviorDiff
        notifications: BehaviorNotification<'candidate'>[]
      }
    | {
        state: 'completed'
        committed: true
        error: null
        assertionVersion: string
        inferenceVersion: string
        actions: BehaviorActionTrace<'applied' | 'deduplicated' | 'skipped'>[]
        diff: BehaviorDiff
        notifications: BehaviorNotification<'recorded'>[]
      }
    | ({
        actions: BehaviorActionTrace<'rolled_back' | 'skipped'>[]
        diff: { added: []; removed: [] }
        notifications: BehaviorNotification<'discarded'>[]
      } & (
        | { state: 'failed'; committed: false; error: BehaviorPublicError }
        | { state: 'cancelled'; committed: false; error: null }
      ))
  )

export type BehaviorRunArgs = {
  projectId: string
  operationId: string
  runId: string
  scope: 'sample'
  binding: BehaviorBinding
  draft: BehaviorDraft
  events: Array<BehaviorEvent>
}

export type BehaviorRunReplyDTO = BehaviorRunResultDTO

export type BehaviorReadArgs = {
  projectId: string
  operationId: string
  runId: string
  scope: 'sample'
  binding: BehaviorBinding
}

export type BehaviorReadResultDTO = BehaviorRunResultDTO

export type BehaviorCancelArgs = {
  projectId: string
  operationId: string
  runId: string
  scope: 'sample'
  binding: BehaviorBinding
}

export type BehaviorCancelResultDTO = Extract<BehaviorRunResultDTO, { state: 'cancelled' }>

export const behaviorPublicErrorKeys = {
  conflict: 'behavior.conflict',
  invalid_input: 'behavior.invalidInput',
  unavailable: 'behavior.unavailable',
  execution_failed: 'behavior.executionFailed',
  cancel_failed: 'behavior.cancelFailed',
} as const
export type BehaviorPublicErrorCode = keyof typeof behaviorPublicErrorKeys

export interface BehaviorBridge {
  runBehaviorSample(
    args: Omit<BehaviorRunArgs, 'projectId'>,
  ): Promise<BridgeResult<BehaviorRunReplyDTO>>
  readBehaviorRun(
    args: Omit<BehaviorReadArgs, 'projectId'>,
  ): Promise<BridgeResult<BehaviorReadResultDTO>>
  cancelBehaviorRun(
    args: Omit<BehaviorCancelArgs, 'projectId'>,
  ): Promise<BridgeResult<BehaviorCancelResultDTO>>
}

const rdfType = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

/** Exact public projection of a private reason. The exception and its evidence stay in the host. */
export function projectBehaviorError(
  reason: unknown,
  phase: 'run' | 'cancel' = 'run',
): BehaviorPublicError {
  switch (reason) {
    case 'competing_write':
    case 'event_identity_conflict':
    case 'stale_reasoning':
      return { code: 'conflict', messageKey: behaviorPublicErrorKeys.conflict }
    case 'unavailable_condition':
    case 'unavailable_action':
    case 'formal_data_forbidden':
      return { code: 'unavailable', messageKey: behaviorPublicErrorKeys.unavailable }
    case 'invalid_shape':
    case 'invalid_text':
    case 'invalid_property':
    case 'invalid_object':
    case 'invalid_class':
    case 'invalid_scalar':
    case 'invalid_expression':
    case 'duplicate_behavior_id':
    case 'duplicate_identity':
    case 'missing_condition':
    case 'missing_trigger':
    case 'missing_action':
    case 'missing_event_field':
    case 'cardinality_action_mismatch':
      return { code: 'invalid_input', messageKey: behaviorPublicErrorKeys.invalid_input }
    default:
      return phase === 'cancel'
        ? { code: 'cancel_failed', messageKey: behaviorPublicErrorKeys.cancel_failed }
        : { code: 'execution_failed', messageKey: behaviorPublicErrorKeys.execution_failed }
  }
}

type PlannerCondition =
  | { op: 'always' }
  | { op: 'has'; subject: BehaviorExpression; property: string; value: BehaviorExpression }

function lowerBehaviorCondition(
  condition: BehaviorCondition,
  typeAssertionAvailable: boolean,
): { ok: true; condition: PlannerCondition } | { ok: false; error: BehaviorPublicError } {
  switch (condition.op) {
    case 'always':
      return { ok: true, condition: { op: 'always' } }
    case 'has':
    case 'equals':
      return { ok: true, condition: { ...condition, op: 'has' } }
    case 'type':
      if (typeAssertionAvailable)
        return {
          ok: true,
          condition: {
            op: 'has',
            subject: condition.subject,
            property: rdfType,
            value: { kind: 'value', value: { kind: 'iri', value: condition.classId } },
          },
        }
      break
    case 'exists':
      // The private planner has no wildcard value predicate.
      break
  }
  return { ok: false, error: projectBehaviorError('unavailable_condition') }
}

/** Normative conversion table. Stage 1 owns catalog lookup, private scalar
 * lowering, snapshot admission, durable execution and renderer presentation. */
export const BehaviorAdapterContract = {
  trigger: { trigger: 'eventType', eventType: 'event_type', eventId: 'event_id' },
  lowerCondition: lowerBehaviorCondition,
  actions: {
    create: { kind: 'create', classProperty: rdfType, classPlacement: 'initial' },
    update: { kind: 'set', cardinality: 'one', target: 'subject' },
    relate: { kind: 'add', cardinality: 'many', target: 'value' },
    notify: { kind: 'notify', effect: 'isolated-record' },
  },
  event: {
    reservedPayloadKeys: ['__proto__', 'constructor', 'prototype'],
    wireEdits: ['create', 'declare', 'delete_object', 'set', 'add', 'remove'],
    sequence: 'stable-input-order',
    version: 'host-bound-event-version',
  },
  request: { scope: 'sample', snapshotAuthority: 'host', consumptionAuthority: 'host' },
  diff: {
    object: 'objectId',
    fact: 'fact',
    notification: 'notification',
  },
  run: {
    candidate: false,
    completed: true,
    failed: false,
    cancelled: false,
  },
  cancel: 'reconcile-original-binding-and-run-id',
  projectError: projectBehaviorError,
} as const
