import type {
  Assistance,
  CheckFeedbackView,
  HintLevel,
  LearningRecordView,
  TaskContext,
} from './types'

export const assistanceLabels: Readonly<Record<Assistance, string>> = {
  independent: '独立完成',
  'partial-hints': '使用部分提示',
  'full-demonstration': '使用完整示范',
  'agent-full-assistance': '使用 Agent 完整辅助',
}

export const hintLabels: Readonly<Record<HintLevel, string>> = {
  1: '概念提示',
  2: '操作提示',
  3: '部分示范',
  4: '完整示范',
}

export function sameContext(a: TaskContext, b: TaskContext): boolean {
  return (
    a.projectId === b.projectId &&
    a.taskId === b.taskId &&
    a.attemptId === b.attemptId &&
    a.inputVersion === b.inputVersion
  )
}

export function contextKey(context: TaskContext): string {
  return JSON.stringify([
    context.projectId,
    context.taskId,
    context.attemptId,
    context.inputVersion,
  ])
}

export function validRecord(record: LearningRecordView, context: TaskContext): boolean {
  return (
    sameContext(record.context, context) &&
    Number.isSafeInteger(record.recordVersion) &&
    record.recordVersion >= 0 &&
    Number.isInteger(record.maxHintLevel) &&
    record.maxHintLevel >= 0 &&
    record.maxHintLevel <= 4 &&
    Object.hasOwn(assistanceLabels, record.assistance) &&
    !(record.maxHintLevel > 0 && record.assistance === 'independent') &&
    !(record.maxHintLevel === 4 && record.assistance === 'partial-hints') &&
    (!record.operationComplete ||
      (record.checkStatus === 'passed' &&
        record.evidenceIds.length > 0 &&
        record.evidenceIds.every((id) => typeof id === 'string' && id.length > 0))) &&
    (!record.independentTransferSuccess ||
      (record.operationComplete &&
        record.assistance === 'independent' &&
        record.maxHintLevel === 0))
  )
}

export function assistanceRank(value: Assistance): number {
  return ['independent', 'partial-hints', 'full-demonstration', 'agent-full-assistance'].indexOf(
    value,
  )
}

export function validFeedback(
  feedback: CheckFeedbackView,
  context: TaskContext,
  highestHint: number,
  previous?: RecordFloor,
): boolean {
  return (
    sameContext(feedback.context, context) &&
    validRecord(feedback.record, context) &&
    feedback.record.maxHintLevel >= highestHint &&
    (!previous ||
      (feedback.record.recordVersion >= previous.recordVersion &&
        assistanceRank(feedback.record.assistance) >= assistanceRank(previous.assistance))) &&
    !(feedback.record.independentTransferSuccess && highestHint > 0)
  )
}

export function recordLabel(record: LearningRecordView | undefined): string {
  if (!record || record.checkStatus === 'not-checked') return '尚未检查'
  if (record.checkStatus === 'stale') return '结果已过期 · 请重新检查'
  if (record.checkStatus === 'pending-dependency') return '检查暂不可用'
  if (!record.operationComplete) return record.checkStatus === 'failed' ? '检查未完成' : '需要修复'
  return assistanceLabels[record.assistance]
}

/** Monotonic, disposable view floor. The owning store still decides durable provenance. */
export type RecordFloor = Pick<LearningRecordView, 'recordVersion' | 'maxHintLevel' | 'assistance'>
export interface RecordProjection {
  latest: LearningRecordView
  floor: RecordFloor
  conflictVersion: number | null
}
function fingerprint(record: LearningRecordView): string {
  return JSON.stringify([
    record.recordVersion,
    record.maxHintLevel,
    record.assistance,
    record.operationComplete,
    record.independentTransferSuccess,
    record.checkStatus,
    [...record.evidenceIds],
  ])
}
export function observeRecord(
  previous: RecordProjection | undefined,
  next: LearningRecordView,
): RecordProjection {
  const nextFloor: RecordFloor = {
    recordVersion:
      Number.isSafeInteger(next.recordVersion) && next.recordVersion >= 0 ? next.recordVersion : 0,
    maxHintLevel:
      Number.isInteger(next.maxHintLevel) && next.maxHintLevel >= 0 && next.maxHintLevel <= 4
        ? next.maxHintLevel
        : 0,
    assistance: Object.hasOwn(assistanceLabels, next.assistance) ? next.assistance : 'independent',
  }
  if (!previous) return { latest: next, floor: nextFloor, conflictVersion: null }
  const invalidVersion = (value: number) => !Number.isSafeInteger(value) || value < 0
  const latest =
    invalidVersion(next.recordVersion) ||
    invalidVersion(previous.latest.recordVersion) ||
    next.recordVersion > previous.latest.recordVersion
      ? next
      : previous.latest
  const conflictVersion =
    next.recordVersion === previous.latest.recordVersion &&
    fingerprint(next) !== fingerprint(previous.latest)
      ? next.recordVersion
      : previous.conflictVersion !== null && next.recordVersion > previous.conflictVersion
        ? null
        : previous.conflictVersion
  return {
    latest,
    conflictVersion,
    floor: {
      recordVersion: Math.max(previous.floor.recordVersion, nextFloor.recordVersion),
      maxHintLevel: Math.max(previous.floor.maxHintLevel, nextFloor.maxHintLevel),
      assistance:
        assistanceRank(nextFloor.assistance) > assistanceRank(previous.floor.assistance)
          ? nextFloor.assistance
          : previous.floor.assistance,
    },
  }
}
export function projectionRecord(
  projection: RecordProjection | undefined,
  context: TaskContext,
): LearningRecordView | undefined {
  if (!projection || projection.conflictVersion !== null) return undefined
  const { latest, floor } = projection
  return validRecord(latest, context) &&
    latest.recordVersion >= floor.recordVersion &&
    latest.maxHintLevel >= floor.maxHintLevel &&
    assistanceRank(latest.assistance) >= assistanceRank(floor.assistance)
    ? latest
    : undefined
}
export function observeRecords(
  previous: Readonly<Record<string, RecordProjection>>,
  records: readonly LearningRecordView[],
): Record<string, RecordProjection> {
  const result = { ...previous }
  for (const record of records) {
    // Retain newer contradictory records so an old pass cannot remain current.
    const key = contextKey(record.context)
    result[key] = observeRecord(result[key], record)
  }
  return result
}
