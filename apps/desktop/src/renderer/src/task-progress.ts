import type { ProgressView, TaskUpdate, TaskView } from '@ontolearn/contracts'

interface Entry {
  projectId: string
  inputSnapshotId: string
  stateVersion: number
  progress: ProgressView
}

// Transient delivery cache only: a restored authority view must confirm each
// identity/version before early progress can become visible. Never a job store.
export class TaskProgressBuffer {
  private generation = -1
  private entries = new Map<string, Entry>()
  remember(update: Extract<TaskUpdate, { kind: 'job' }>): void {
    if (!update.progress || update.generation < this.generation) return
    if (update.generation > this.generation) {
      this.entries.clear()
      this.generation = update.generation
    }
    const job = update.job
    if (!['queued', 'running', 'cancelling'].includes(job.state)) return
    const previous = this.entries.get(job.jobId)
    if (previous && previous.stateVersion > job.stateVersion) return
    this.entries.delete(job.jobId)
    if (this.entries.size >= 16) this.entries.delete(this.entries.keys().next().value!)
    this.entries.set(job.jobId, {
      projectId: job.projectId,
      inputSnapshotId: job.inputSnapshotId,
      stateVersion: job.stateVersion,
      progress: structuredClone(update.progress),
    })
  }
  restore(view: TaskView): Record<string, ProgressView> {
    if (view.generation < this.generation) return {}
    if (view.generation > this.generation) this.entries.clear()
    this.generation = view.generation
    const result: Record<string, ProgressView> = {}
    for (const [identity, entry] of this.entries) {
      const job = view.jobs.find((job) => job.jobId === identity)
      if (
        !job ||
        job.projectId !== view.project?.projectId ||
        entry.projectId !== job.projectId ||
        entry.inputSnapshotId !== job.inputSnapshotId ||
        entry.stateVersion !== job.stateVersion ||
        !['queued', 'running', 'cancelling'].includes(job.state)
      ) {
        this.entries.delete(identity)
        continue
      }
      result[identity] = structuredClone(entry.progress)
    }
    return result
  }
  forget(identity: string): void {
    this.entries.delete(identity)
  }
  clear(): void {
    this.entries.clear()
    this.generation = -1
  }
}
