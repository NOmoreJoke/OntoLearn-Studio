import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import type { JobView, TaskUpdate, TaskView } from '@ontolearn/contracts'
import { TaskProgressBuffer } from '../../apps/desktop/src/renderer/src/task-progress'

function input() {
  const job = structuredClone(
    fixtures.cases.find((item) => item.name === 'job running')!.value,
  ) as JobView
  const update: Extract<TaskUpdate, { kind: 'job' }> = {
    kind: 'job',
    generation: 4,
    job,
    progress: { stage: 'computing', completed: null, total: null },
  }
  const view: TaskView = {
    generation: 4,
    project: {
      projectId: job.projectId,
      projectRevision: 0,
      inputSnapshotId: job.inputSnapshotId,
      dependencyVector: {},
      formatVersion: 2,
    },
    jobs: [job],
  }
  return { update, view }
}

describe('progress delivery before the authority view', () => {
  it('keeps unknown totals and copies transient data across initial and explicit restores', () => {
    const buffer = new TaskProgressBuffer()
    const { update, view } = input()
    buffer.remember(update)
    update.progress!.stage = 'committing'
    const first = buffer.restore(view)
    expect(first).toEqual({
      [update.job.jobId]: { stage: 'computing', completed: null, total: null },
    })
    first[update.job.jobId].stage = 'loading'
    expect(buffer.restore(view)[update.job.jobId].stage).toBe('computing')
  })

  it.each(['generation', 'project', 'input', 'version', 'membership', 'terminal'])(
    'does not display progress without a matching %s',
    (mismatch) => {
      const buffer = new TaskProgressBuffer()
      const { update, view } = input()
      buffer.remember(update)
      const restored = structuredClone(view)
      if (mismatch === 'generation') restored.generation++
      if (mismatch === 'project') restored.project!.projectId = 'other-project'
      if (mismatch === 'input') restored.jobs[0].inputSnapshotId = 'b'.repeat(64)
      if (mismatch === 'version') restored.jobs[0].stateVersion++
      if (mismatch === 'membership') restored.jobs = []
      if (mismatch === 'terminal') restored.jobs[0].state = 'failed'
      expect(buffer.restore(restored)).toEqual({})
    },
  )

  it('rejects late old-generation and old-version delivery', () => {
    const buffer = new TaskProgressBuffer()
    const { update, view } = input()
    buffer.remember(update)
    buffer.remember({
      ...update,
      generation: 3,
      progress: { stage: 'loading', completed: null, total: null },
    })
    buffer.remember({
      ...update,
      job: { ...update.job, stateVersion: update.job.stateVersion - 1 },
      progress: { stage: 'loading', completed: null, total: null },
    })
    expect(buffer.restore(view)[update.job.jobId].stage).toBe('computing')
  })

  it('retains a future-generation hint while an earlier restore is still in flight', () => {
    const buffer = new TaskProgressBuffer()
    const { update, view } = input()
    buffer.remember(update)
    expect(buffer.restore({ ...view, generation: 3 })).toEqual({})
    expect(buffer.restore(view)[update.job.jobId].stage).toBe('computing')
  })

  it('bounds early entries to the same sixteen-job view limit', () => {
    const buffer = new TaskProgressBuffer()
    const { update, view } = input()
    const jobs = Array.from({ length: 17 }, (_, i) => ({
      ...update.job,
      jobId: `00000000-0000-4000-8000-${String(i + 100).padStart(12, '0')}`,
    }))
    jobs.forEach((job) => buffer.remember({ ...update, job }))
    expect(Object.keys(buffer.restore({ ...view, jobs: jobs.slice(1) }))).toEqual(
      jobs.slice(1).map((job) => job.jobId),
    )
  })

  it('forgets superseded job state and clears pending delivery on disconnect', () => {
    const buffer = new TaskProgressBuffer()
    const { update, view } = input()
    buffer.remember(update)
    buffer.forget(update.job.jobId)
    expect(buffer.restore(view)).toEqual({})
    buffer.remember(update)
    buffer.clear()
    expect(buffer.restore(view)).toEqual({})
  })
})
