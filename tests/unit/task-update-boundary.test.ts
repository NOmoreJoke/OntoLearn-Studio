import { describe, expect, it } from 'vitest'
import { isTaskUpdate, internalError } from '@ontolearn/contracts'

describe('task connection boundary', () => {
  const connection = {
    kind: 'connection',
    generation: 3,
    projectId: '00000000-0000-4000-8000-000000000001',
    state: 'reconnecting',
    attempt: 0,
    error: internalError,
  }
  it('keeps transport uncertainty separate from durable job state', () => {
    expect(isTaskUpdate(connection)).toBe(true)
    expect(isTaskUpdate({ ...connection, state: 'offline', attempt: 3 })).toBe(true)
    for (const mutation of [
      { state: 'offline', attempt: 2 },
      { state: 'failed' },
      { attempt: 4 },
      { attempt: '1' },
      { projectId: 'unknown' },
      { generation: -1 },
      { rawPath: '/private/input' },
      { error: { ...internalError, params: { rawValue: 'private' } } },
    ])
      expect(isTaskUpdate({ ...connection, ...mutation })).toBe(false)
  })
  it('requires an authoritative restored view to carry the same generation', () => {
    const restored = {
      kind: 'restored',
      generation: 4,
      view: { generation: 4, project: null, jobs: [] },
    }
    expect(isTaskUpdate(restored)).toBe(true)
    expect(isTaskUpdate({ ...restored, generation: 3 })).toBe(false)
    expect(isTaskUpdate({ ...restored, view: { ...restored.view, jobs: [null] } })).toBe(false)
    expect(isTaskUpdate({ ...restored, rawPath: '/private/input' })).toBe(false)
  })
})
