import { describe, expect, it, vi } from 'vitest'
import type { DesktopBridge, JobView, TaskView } from '../../packages/contracts/src'
import { internalError } from '../../packages/contracts/src'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { validateV2 } from '../../packages/contracts/src/v2'
import { QueryResultReader } from '../../apps/desktop/src/renderer/src/query/reader'

const id = (n: number) => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`
const hash = 'a'.repeat(64)
const view = (generation = 1, projectId = id(1)): TaskView => ({
  generation,
  project: {
    projectId,
    projectRevision: 3,
    inputSnapshotId: hash,
    dependencyVector: { 'facts:asserted': 3 },
    formatVersion: 2,
  },
  jobs: [],
})
function metadata(resultId = id(2)) {
  return {
    projectId: id(1),
    resultId,
    jobId: id(3),
    kind: 'query',
    definitionId: 'Q-01',
    inputSnapshotId: hash,
    inputProjectRevision: 3,
    dependencyVector: { 'facts:asserted': 3 },
    definitionSetDigests: {},
    implementation: {
      executionSemanticsVersion: 'v1',
      engineVersion: '0.1.0',
      dependencyLockHash: hash,
    },
    scope: 'asserted',
    parametersHash: hash,
    state: 'current',
    staleReason: [],
    payloadStatus: 'available',
    createdAtMs: 1,
    historicalSelectionRequired: false,
  }
}
function presentation(resultId = id(2)) {
  return {
    binding: {
      projectId: id(1),
      resultId,
      inputSnapshotId: hash,
      scope: 'asserted' as const,
      parametersHash: hash,
      order: 'ordinal+rowId:asc' as const,
    },
    columns: ['告警'],
    executedSparql: 'SELECT ?alarm WHERE { ?alarm a <urn:test:Alarm> }',
  }
}
function page(ordinal = 0, nextCursor: string | null = null, resultId = id(2)) {
  return {
    binding: presentation(resultId).binding,
    rows: [{ rowId: id(4 + ordinal), ordinal, cells: ['urn:test:A01'] }],
    nextCursor,
  }
}
function job(state = 'running', stateVersion = 4, jobId = id(3)): JobView {
  const frame = fixtures.cases.find((entry) => entry.name === 'response job.get')!.value as {
    result: Record<string, unknown>
  }
  const result = {
    ...frame.result,
    capability: 'query.execute',
    scope: 'asserted',
    commitProgress: { mode: 'none' },
    input: { ...(frame.result.input as Record<string, unknown>), scope: 'asserted' },
    state,
    stateVersion,
    jobId,
    finishedAtMs: ['succeeded', 'failed', 'cancelled'].includes(state) ? 9 : null,
  }
  expect(validateV2('job', result)).toBe(true)
  return result as unknown as JobView
}
function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => {
    resolve = done
  })
  return { promise, resolve }
}
function setup() {
  const bridge = {
    getResult: vi
      .fn<DesktopBridge['getResult']>()
      .mockResolvedValue({ ok: true, data: metadata() }),
    getResultPage: vi
      .fn<DesktopBridge['getResultPage']>()
      .mockResolvedValue({ ok: true, data: page() }),
    getJob: vi.fn<DesktopBridge['getJob']>().mockResolvedValue({ ok: true, data: job() }),
    cancelJob: vi.fn<DesktopBridge['cancelJob']>().mockResolvedValue({
      ok: true,
      data: { jobId: id(3), disposition: 'accepted', state: 'cancelling', stateVersion: 5 },
    }),
  }
  const reader = new QueryResultReader(bridge)
  expect(reader.bind(view())).toBe(true)
  return { bridge, reader }
}

describe('T04 renderer read adapter; synthetic transport tests only, no query executor', () => {
  it('reads through named approved bridge methods and clones its bounded snapshot', async () => {
    const { reader, bridge } = setup()
    expect(await reader.read(presentation(), 50)).toBe(true)
    expect(bridge.getResult).toHaveBeenCalledWith(id(2))
    expect(bridge.getResultPage).toHaveBeenCalledWith({
      resultId: id(2),
      pageSize: 50,
      cursor: null,
    })
    const snapshot = reader.snapshot()
    expect(snapshot.result?.page?.rows).toEqual(page().rows)
    expect(snapshot.result?.executedSparql).toBe(presentation().executedSparql)
    snapshot.result!.columns[0] = 'changed'
    expect(reader.snapshot().result?.columns).toEqual(['告警'])
  })
  it('uses only the issued cursor, refreshes result state, and replaces one page', async () => {
    const { reader, bridge } = setup()
    bridge.getResultPage
      .mockResolvedValueOnce({ ok: true, data: page(0, id(8)) })
      .mockResolvedValueOnce({ ok: true, data: page(1) })
    await reader.read(presentation())
    expect(await reader.nextPage(id(9))).toBe(false)
    expect(bridge.getResultPage).toHaveBeenCalledTimes(1)
    bridge.getResult.mockResolvedValueOnce({
      ok: true,
      data: {
        ...metadata(),
        state: 'stale',
        staleReason: [{ code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 3, after: 4 }],
      },
    })
    expect(await reader.nextPage(id(8))).toBe(true)
    expect(bridge.getResult).toHaveBeenCalledTimes(2)
    expect(bridge.getResultPage).toHaveBeenLastCalledWith({
      resultId: id(2),
      pageSize: 100,
      cursor: id(8),
    })
    expect(reader.snapshot().result?.page?.rows).toEqual(page(1).rows)
    expect(reader.snapshot().result?.metadata.state).toBe('stale')
  })
  it('rejects repeated cursor/overlapping rows across pages', async () => {
    for (const second of [page(0), page(1, id(8))]) {
      const { reader, bridge } = setup()
      bridge.getResultPage
        .mockResolvedValueOnce({ ok: true, data: page(0, id(8)) })
        .mockResolvedValueOnce({ ok: true, data: second })
      await reader.read(presentation())
      expect(await reader.nextPage(id(8))).toBe(false)
      expect(reader.snapshot().result).toBeNull()
      expect(reader.snapshot().phase).toBe('error')
    }
  })
  it('discards late metadata after a project/generation switch before requesting any page', async () => {
    const { reader, bridge } = setup()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getResult']>>>()
    bridge.getResult.mockReturnValueOnce(pending.promise)
    const reading = reader.read(presentation())
    reader.bind(view(2, id(20)))
    pending.resolve({ ok: true, data: metadata() })
    expect(await reading).toBe(false)
    expect(bridge.getResultPage).not.toHaveBeenCalled()
    expect(reader.snapshot()).toMatchObject({
      projectId: id(20),
      generation: 2,
      phase: 'idle',
      result: null,
    })
  })
  it('does not let a superseded result read overwrite a newer selection', async () => {
    const { reader, bridge } = setup()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getResult']>>>()
    bridge.getResult
      .mockReturnValueOnce(pending.promise)
      .mockResolvedValueOnce({ ok: true, data: metadata(id(10)) })
    bridge.getResultPage.mockResolvedValueOnce({ ok: true, data: page(0, null, id(10)) })
    const first = reader.read(presentation())
    expect(await reader.read(presentation(id(10)))).toBe(true)
    pending.resolve({ ok: true, data: metadata() })
    expect(await first).toBe(false)
    expect(reader.snapshot().result?.metadata.resultId).toBe(id(10))
  })
  it('invalidates late page responses when the authority input changes', async () => {
    const { reader, bridge } = setup()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getResultPage']>>>()
    bridge.getResultPage.mockReturnValueOnce(pending.promise)
    const reading = reader.read(presentation())
    await vi.waitFor(() => expect(bridge.getResultPage).toHaveBeenCalledTimes(1))
    const updated = view()
    updated.project!.projectRevision = 4
    reader.bind(updated)
    pending.resolve({ ok: true, data: page() })
    expect(await reading).toBe(false)
    expect(reader.snapshot().result).toBeNull()
  })
  it('validates all metadata/page/presentation identities and page-size limits', async () => {
    for (const data of [
      { ...metadata(), kind: 'reasoning' },
      { ...metadata(), projectId: id(20) },
      { ...metadata(), parametersHash: 'b'.repeat(64) },
    ]) {
      const { reader, bridge } = setup()
      bridge.getResult.mockResolvedValueOnce({ ok: true, data })
      expect(await reader.read(presentation())).toBe(false)
      expect(bridge.getResultPage).not.toHaveBeenCalled()
      expect(reader.snapshot().result).toBeNull()
    }
    for (const size of [0, 201, 1.5]) {
      const { reader, bridge } = setup()
      expect(await reader.read(presentation(), size)).toBe(false)
      expect(bridge.getResult).not.toHaveBeenCalled()
    }
    const { reader, bridge } = setup()
    bridge.getResultPage.mockResolvedValueOnce({
      ok: true,
      data: { ...page(), binding: { ...page().binding, inputSnapshotId: 'b'.repeat(64) } },
    })
    expect(await reader.read(presentation())).toBe(false)
  })
  it('retains evicted historical identity without attempting to load its missing payload', async () => {
    const { reader, bridge } = setup()
    bridge.getResult.mockResolvedValueOnce({
      ok: true,
      data: {
        ...metadata(),
        state: 'historical',
        historicalSelectionRequired: true,
        payloadStatus: 'evicted',
      },
    })
    expect(await reader.read(presentation())).toBe(true)
    expect(reader.snapshot().result).toMatchObject({
      metadata: { state: 'historical', inputSnapshotId: hash },
      page: null,
    })
    expect(bridge.getResultPage).not.toHaveBeenCalled()
  })
  it('sanitizes bridge failures and rejects disposed/old authority views', async () => {
    const { reader, bridge } = setup()
    bridge.getResult.mockRejectedValueOnce(new Error('PRIVATE_PATH_SHOULD_NOT_RENDER'))
    expect(await reader.read(presentation())).toBe(false)
    expect(reader.snapshot().error).toEqual(internalError)
    expect(JSON.stringify(reader.snapshot())).not.toContain('PRIVATE_PATH')
    expect(reader.bind(view(0))).toBe(false)
    reader.dispose()
    expect(reader.bind(view(2))).toBe(false)
    expect(await reader.read(presentation())).toBe(false)
    expect(reader.snapshot().phase).toBe('disposed')
    expect(bridge.cancelJob).not.toHaveBeenCalled()
  })
  it('never sends a cancel for another capability or a switched-away project', async () => {
    const { reader, bridge } = setup()
    bridge.getJob.mockResolvedValueOnce({
      ok: true,
      data: { ...job(), capability: 'reasoning.execute' },
    })
    expect(await reader.cancel(id(3))).toBe(false)
    expect(bridge.cancelJob).not.toHaveBeenCalled()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getJob']>>>()
    bridge.getJob.mockReturnValueOnce(pending.promise)
    const cancelling = reader.cancel(id(3))
    reader.bind(view(2, id(20)))
    pending.resolve({ ok: true, data: job() })
    expect(await cancelling).toBe(false)
    expect(bridge.cancelJob).not.toHaveBeenCalled()
  })
  it('keeps cancellation acknowledgement separate from the authoritative job terminal', async () => {
    const { reader, bridge } = setup()
    bridge.getJob
      .mockResolvedValueOnce({ ok: true, data: job() })
      .mockResolvedValueOnce({ ok: true, data: job('running', 5) })
    expect(await reader.cancel(id(3))).toBe(true)
    expect(reader.snapshot()).toMatchObject({
      cancelRequested: true,
      job: { state: 'running', stateVersion: 5 },
    })
    expect(reader.receiveUpdate({ kind: 'job', generation: 1, job: job('cancelled', 6) })).toBe(
      true,
    )
    expect(reader.snapshot()).toMatchObject({
      cancelRequested: false,
      job: { state: 'cancelled', stateVersion: 6 },
    })
  })
  it('does not cancel an already terminal job or accept a mismatched acknowledgement', async () => {
    const { reader, bridge } = setup()
    bridge.getJob.mockResolvedValueOnce({ ok: true, data: job('cancelled') })
    expect(await reader.cancel(id(3))).toBe(true)
    expect(bridge.cancelJob).not.toHaveBeenCalled()
    bridge.cancelJob.mockResolvedValueOnce({
      ok: true,
      data: { jobId: id(20), disposition: 'accepted', state: 'cancelling', stateVersion: 5 },
    })
    expect(await reader.cancel(id(3))).toBe(false)
    expect(reader.snapshot().job?.state).toBe('running')
  })
  it('rejects a job read that is older than the cancel acknowledgement', async () => {
    const { reader } = setup()
    expect(await reader.cancel(id(3))).toBe(false)
    expect(reader.snapshot().job?.state).toBe('running')
    expect(reader.snapshot().error).not.toBeNull()
  })
  it('rejects duplicate in-flight cancel calls without invalidating the first one', async () => {
    const { reader, bridge } = setup()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getJob']>>>()
    bridge.getJob
      .mockReturnValueOnce(pending.promise)
      .mockResolvedValue({ ok: true, data: job('running', 5) })
    const first = reader.cancel(id(3))
    expect(await reader.cancel(id(3))).toBe(false)
    pending.resolve({ ok: true, data: job() })
    expect(await first).toBe(true)
    expect(bridge.cancelJob).toHaveBeenCalledTimes(1)
  })
  it('disposes reads without cancelling worker jobs or accepting late payloads', async () => {
    const { reader, bridge } = setup()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getResult']>>>()
    bridge.getResult.mockReturnValueOnce(pending.promise)
    const reading = reader.read(presentation())
    reader.dispose()
    pending.resolve({ ok: true, data: metadata() })
    expect(await reading).toBe(false)
    expect(reader.snapshot().phase).toBe('disposed')
    expect(bridge.cancelJob).not.toHaveBeenCalled()
  })
  it('rejects stale/cross-project task notifications and job read races', async () => {
    const { reader, bridge } = setup()
    await reader.refreshJob(id(3))
    expect(reader.receiveUpdate({ kind: 'job', generation: 0, job: job('running', 6) })).toBe(false)
    expect(reader.receiveUpdate({ kind: 'job', generation: 1, job: job('running', 3) })).toBe(false)
    expect(
      reader.receiveUpdate({
        kind: 'job',
        generation: 1,
        job: { ...job('running', 6), projectId: id(20) },
      }),
    ).toBe(false)
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getJob']>>>()
    bridge.getJob
      .mockReturnValueOnce(pending.promise)
      .mockResolvedValueOnce({ ok: true, data: job('running', 5, id(10)) })
    const old = reader.refreshJob(id(3))
    expect(await reader.refreshJob(id(10))).toBe(true)
    pending.resolve({ ok: true, data: job('running', 6) })
    expect(await old).toBe(false)
    expect(reader.snapshot().job?.jobId).toBe(id(10))
  })
  it('clears a pending cancellation only when the terminal is actually read', async () => {
    const { reader, bridge } = setup()
    bridge.getJob
      .mockResolvedValueOnce({ ok: true, data: job() })
      .mockResolvedValueOnce({ ok: true, data: job('running', 5) })
    await reader.cancel(id(3))
    expect(reader.snapshot().cancelRequested).toBe(true)
    bridge.getJob.mockResolvedValueOnce({ ok: true, data: job('cancelled', 6) })
    expect(await reader.cancel(id(3))).toBe(true)
    expect(reader.snapshot().cancelRequested).toBe(false)
    expect(bridge.cancelJob).toHaveBeenCalledTimes(1)
  })
  it('invalidates in-flight reads on a matching connection loss but ignores another project', async () => {
    const { reader, bridge } = setup()
    const pending = deferred<Awaited<ReturnType<DesktopBridge['getResult']>>>()
    bridge.getResult.mockReturnValueOnce(pending.promise)
    const reading = reader.read(presentation())
    const connection = {
      kind: 'connection',
      generation: 1,
      projectId: id(20),
      state: 'offline',
      attempt: 3,
      error: internalError,
    }
    expect(reader.receiveUpdate(connection)).toBe(false)
    expect(reader.receiveUpdate({ ...connection, projectId: id(1) })).toBe(true)
    pending.resolve({ ok: true, data: metadata() })
    expect(await reading).toBe(false)
    expect(reader.snapshot()).toMatchObject({ phase: 'error', result: null, error: internalError })
    expect(bridge.getResultPage).not.toHaveBeenCalled()
  })
})
