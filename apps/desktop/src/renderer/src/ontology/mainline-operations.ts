import type { CommitMarker, PendingEdit } from './mainline-session'

type Entry = { pending?: PendingEdit; receipt?: CommitMarker; closedOperationId?: string }
/** UI reconciliation memory across page/bridge remounts; never a write capability.
 * Original Job/operation queries remain authoritative. Unknown entries are never evicted.
 */
export class OntologyOperationBook {
  #entries = new Map<string, Entry>()
  #listeners = new Set<() => void>()
  get(projectId: string): Entry | undefined {
    const entry = this.#entries.get(projectId)
    return entry && structuredClone(entry)
  }
  subscribe(listener: () => void): () => void {
    this.#listeners.add(listener)
    return () => this.#listeners.delete(listener)
  }
  pending(value: PendingEdit): void {
    const projectId = value.preview.projectId
    const old = this.#entries.get(projectId)
    if (old?.closedOperationId === value.operationId) return
    if (old?.pending && old.pending.operationId !== value.operationId)
      throw new Error('INVALID_STATE')
    if (!old && this.#entries.size >= 16) {
      const terminal = [...this.#entries].find(([, entry]) => !entry.pending)
      if (!terminal) throw new Error('RESOURCE_LIMIT')
      this.#entries.delete(terminal[0])
    }
    this.#entries.set(projectId, { ...old, pending: structuredClone(value) })
    for (const fn of this.#listeners) fn()
  }
  terminal(pending: PendingEdit, receipt?: CommitMarker): void {
    const projectId = pending.preview.projectId
    const old = this.#entries.get(projectId)
    if (old?.pending?.operationId !== pending.operationId) return
    this.#entries.set(projectId, {
      receipt: receipt ?? old.receipt,
      closedOperationId: pending.operationId,
    })
    for (const fn of this.#listeners) fn()
  }
}

export const ontologyOperations = new OntologyOperationBook()
