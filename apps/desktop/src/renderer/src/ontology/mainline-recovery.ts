import { z } from 'zod'
import type { DomainRead } from './mainline-api'
import type { PendingEdit } from './mainline-session'

const hash = z.string().regex(/^[a-f0-9]{64}$/)
const pendingSchema = z
  .object({
    operationId: z.string().uuid(),
    confirmationRef: z.string().uuid(),
    preview: z
      .object({
        projectId: z.string().min(1),
        baseRevision: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER),
        inputSnapshotId: hash,
        preparedPlanRef: hash,
        parametersHash: hash,
      })
      .strict(),
  })
  .strict()

/** An attempted-operation bookmark, never a confirmation, prepared plan or receipt. */
export function recoveredPending(source: DomainRead): PendingEdit | undefined {
  const draft = source.workspace.draft
  if (draft.state !== 'present' || !draft.contentJson) return
  const value: unknown = JSON.parse(draft.contentJson)
  if (
    !value ||
    typeof value !== 'object' ||
    !('reconciliationVersion' in value) ||
    value.reconciliationVersion !== 1
  )
    return
  if (!('pending' in value)) throw new Error('INVALID_STATE')
  if (value.pending === null) return
  const parsed = pendingSchema.safeParse(value.pending)
  if (!parsed.success || parsed.data.preview.projectId !== source.projectId)
    throw new Error('INVALID_STATE')
  return parsed.data
}
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`
  if (value && typeof value === 'object')
    return `{${Object.entries(value)
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([key, item]) => `${JSON.stringify(key)}:${canonical(item)}`)
      .join(',')}}`
  const encoded = JSON.stringify(value)
  if (typeof encoded !== 'string') throw new Error('INVALID_STATE')
  return encoded
}
export function pendingBookmark(source: DomainRead, pending: PendingEdit): string {
  const { projectId, baseRevision, inputSnapshotId, preparedPlanRef, parametersHash } =
    pending.preview
  const bookmark = {
    operationId: pending.operationId,
    confirmationRef: pending.confirmationRef,
    preview: { projectId, baseRevision, inputSnapshotId, preparedPlanRef, parametersHash },
  }
  const draft = source.workspace.draft
  const previous: unknown =
    draft.state === 'present' && draft.contentJson ? JSON.parse(draft.contentJson) : null
  const own =
    previous &&
    typeof previous === 'object' &&
    'reconciliationVersion' in previous &&
    previous.reconciliationVersion === 1
  const content = canonical({
    reconciliationVersion: 1,
    pending: bookmark,
    preservedDraft:
      own &&
      'preservedDraft' in previous &&
      (previous.preservedDraft === null || typeof previous.preservedDraft === 'string')
        ? previous.preservedDraft
        : draft.state === 'present'
          ? draft.contentJson
          : null,
  })
  if (new TextEncoder().encode(content).length > 65536) throw new Error('RESOURCE_LIMIT')
  return content
}

export function closedBookmark(source: DomainRead, operationId: string): string {
  const draft = source.workspace.draft
  const previous: unknown =
    draft.state === 'present' && draft.contentJson ? JSON.parse(draft.contentJson) : null
  const own =
    previous &&
    typeof previous === 'object' &&
    'reconciliationVersion' in previous &&
    previous.reconciliationVersion === 1
  const content = canonical({
    reconciliationVersion: 1,
    pending: null,
    closedOperationId: operationId,
    preservedDraft:
      own &&
      'preservedDraft' in previous &&
      (previous.preservedDraft === null || typeof previous.preservedDraft === 'string')
        ? previous.preservedDraft
        : draft.state === 'present'
          ? draft.contentJson
          : null,
  })
  if (new TextEncoder().encode(content).length > 65536) throw new Error('RESOURCE_LIMIT')
  return content
}
