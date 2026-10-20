import { EventEmitter } from 'node:events'
import { describe, expect, it } from 'vitest'
import type { WebContents } from 'electron'
import type { JobView, TaskUpdate } from '@ontolearn/contracts'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { TaskService } from '../../apps/desktop/src/main/task-service'
import { installViewNavigation } from '../../apps/desktop/src/main/view-navigation'

it('keeps actual task subscription and generation across anchors, and replaces them for a new document', async () => {
  const job = structuredClone(
    fixtures.cases.find((item) => item.name === 'job running')!.value,
  ) as JobView
  const session = '00000000-0000-4000-8000-000000000002'
  const subscription = '00000000-0000-4000-8000-000000000008'
  const notifications = new EventEmitter()
  const requests: string[] = []
  const engine = {
    engineSessionId: session,
    onConnectionState() {
      return () => {}
    },
    onNotification(listener: (value: unknown) => void) {
      notifications.on('wire', listener)
      return () => {
        notifications.off('wire', listener)
      }
    },
    async request(method: string, params: Record<string, unknown>): Promise<unknown> {
      requests.push(method)
      if (method === 'project.get')
        return {
          projectId: job.projectId,
          projectRevision: 1,
          inputSnapshotId: job.inputSnapshotId,
          dependencyVector: { 'facts:asserted': 1 },
          formatVersion: 2,
        }
      if (method === 'job.get') return job
      if (method === 'job.subscribe')
        return {
          subscriptionId: subscription,
          projectId: job.projectId,
          jobId: job.jobId,
          seq: 0,
          stateVersion: job.stateVersion,
        }
      if (method === 'job.unsubscribe')
        return { subscriptionId: params.subscriptionId, unsubscribed: true }
      throw new Error('Unexpected unit adapter request')
    },
  }
  const tasks = new TaskService(engine)
  const updates: TaskUpdate[] = []
  tasks.selectProject(job.projectId, [job.jobId])
  const attach = () => tasks.attachView((update) => updates.push(update))
  attach()
  const contents = new EventEmitter()
  // This is the exact registration adapter used by createWindow, not a copy of
  // its navigation condition. TaskService itself owns generation/subscriptions.
  installViewNavigation(contents as unknown as Pick<WebContents, 'on'>, attach)
  try {
    const before = await tasks.restore()
    expect(before.ok).toBe(true)
    const count = requests.length
    for (const hash of ['#modules', '#overview'])
      contents.emit('did-start-navigation', {
        url: `file:///app/index.html${hash}`,
        isMainFrame: true,
        isSameDocument: true,
      })
    contents.emit('did-start-navigation', {
      url: 'file:///frame.html',
      isMainFrame: false,
      isSameDocument: false,
    })
    expect(requests).toHaveLength(count)
    const final = {
      ...(structuredClone(
        fixtures.cases.find((item) => item.name === 'job succeeded')!.value,
      ) as JobView),
      stateVersion: job.stateVersion + 1,
    } as JobView
    const event = {
      kind: 'notification',
      protocolVersion: 2,
      engineSessionId: session,
      projectId: job.projectId,
      jobId: job.jobId,
      subscriptionId: subscription,
      seq: 1,
      event: 'job.state',
      data: final,
    }
    notifications.emit('wire', event)
    expect(updates).toHaveLength(1)
    expect(before.ok && updates[0].generation).toBe(before.ok && before.data.generation)
    expect(updates[0].kind === 'job' && updates[0].job.state).toBe('succeeded')
    contents.emit('did-start-navigation', {
      url: 'file:///app/index.html',
      isMainFrame: true,
      isSameDocument: false,
    })
    expect(requests.slice(count)).toEqual(['job.unsubscribe'])
    notifications.emit('wire', event)
    expect(updates).toHaveLength(1)
    const after = await tasks.restore()
    expect(after.ok && before.ok && after.data.generation > before.data.generation).toBe(true)
  } finally {
    tasks.dispose()
  }
})

describe('navigation adapter', () => {
  it('registers exactly one main document navigation listener', () => {
    const contents = new EventEmitter()
    let replacements = 0
    installViewNavigation(contents as unknown as Pick<WebContents, 'on'>, () => replacements++)
    expect(contents.eventNames()).toEqual(['did-start-navigation'])
    contents.emit('did-start-navigation', { isMainFrame: true, isSameDocument: false })
    expect(replacements).toBe(1)
  })
})
