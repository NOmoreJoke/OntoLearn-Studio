import { createHash } from 'node:crypto'
import { createElement, type ComponentType } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it, vi } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { validateV2 } from '../../packages/contracts/src/v2'
import {
  QueryWorkspaceController,
  type QueryWorkspaceBridge,
} from '../../apps/desktop/src/renderer/src/query/workspace-controller'
import {
  currentPageCsv,
  type DisplayDescriptor,
  type DisplayRowsPage,
} from '../../apps/desktop/src/renderer/src/query/typed-results'
import type {
  JobView,
  TaskUpdate,
} from '../../apps/desktop/src/renderer/src/query/api002-source-types'

// Consumer fault injection + real TSX SSR only; no actual Store, issuer, worker,
// App project switch, native download or cross-session runtime is claimed.
const pageModule = '../../apps/desktop/src/renderer/src/query/QueryWorkspacePage'
const {
  QueryWorkspacePage,
}: { QueryWorkspacePage: ComponentType<{ controller: QueryWorkspaceController }> } = await import(
  pageModule
)
const id = (n: number) => `30000000-0000-4000-8000-${String(n).padStart(12, '0')}`
const pid = id(1),
  jid = id(2),
  op = id(3),
  rid = id(4),
  descriptorRef = id(5),
  listRef = id(6),
  cursor = id(7)
const hash = (value: string) => createHash('sha256').update(value).digest('hex')
const ok = <T>(data: T) => ({ ok: true as const, data })
const failed = {
  ok: false as const,
  error: {
    code: 'INVALID_STATE',
    messageKey: 'protocol.invalidState',
    retryable: false,
    params: {},
  },
}
const deferred = <T>() => {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((fn) => {
    resolve = fn
  })
  return { resolve, promise }
}
function job(): JobView {
  const value = structuredClone(
    fixtures.cases.find((item) => item.name === 'job succeeded')!.value,
  ) as JobView
  return {
    ...value,
    projectId: pid,
    jobId: jid,
    operationId: op,
    capability: 'query.execute',
    scope: 'asserted',
    inputSnapshotId: hash('original-snapshot'),
    parametersHash: hash('parameters'),
    input: {
      inputSnapshotId: hash('original-snapshot'),
      scope: 'asserted',
      parametersHash: hash('parameters'),
      definitionId: 'saved-query',
      derivedResultIds: [],
      preparedPlanRef: null,
    },
    confirmationRef: null,
    commitProgress: { mode: 'none' },
    resultRef: { resultId: rid, inputSnapshotId: hash('original-snapshot') },
  }
}
function descriptor(
  j: JobView,
  selection: 'current' | 'historical' = 'current',
  state: 'current' | 'stale' | 'historical' = 'current',
): DisplayDescriptor {
  const text = 'SELECT ?device WHERE { ?device ?p ?o }'
  const implementation = j.implementation as DisplayDescriptor['identity']['implementation']
  return {
    identity: {
      projectId: pid,
      resultId: rid,
      jobId: jid,
      inputSnapshotId: j.inputSnapshotId,
      inputProjectRevision: 1,
      scope: 'asserted',
      definitionId: 'saved-query',
      parametersHash: j.parametersHash as string,
      implementation,
      payloadSha256: hash('payload'),
      definitionSha256: hash('definition'),
      inputSelection: selection,
      projectionVersion: 1,
      lengthPolicyId: 'query-presentation-scalars-v1',
    },
    descriptorRef,
    metadata: {
      projectId: pid,
      resultId: rid,
      jobId: jid,
      kind: 'query',
      definitionId: 'saved-query',
      inputSnapshotId: j.inputSnapshotId,
      inputProjectRevision: 1,
      scope: 'asserted',
      parametersHash: j.parametersHash,
      implementation,
      dependencyVector: { 'facts:asserted': 1 },
      definitionSetDigests: {},
      state,
      staleReason:
        state === 'stale'
          ? [{ code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 1, after: 2 }]
          : [],
      payloadStatus: 'available',
      createdAtMs: 1,
      historicalSelectionRequired: state !== 'current',
    } as DisplayDescriptor['metadata'],
    executedText: {
      sha256: hash(text),
      utf8Bytes: Buffer.byteLength(text),
      unicodeScalars: [...text].length,
      utf16Units: text.length,
    },
    query: { kind: 'SELECT', rowCount: 1, columns: [{ index: 0, name: 'device' }] },
  }
}
function setup() {
  const original = job(),
    d = descriptor(original)
  let listener: (value: TaskUpdate) => void = () => {}
  const page = (jobs = [original], nextCursor: string | null = null) => ({
    binding: {
      projectId: pid,
      listSnapshotId: listRef,
      filter: 'terminal',
      order: 'createdAtMs+jobId:asc',
    },
    jobs,
    nextCursor,
  })
  const bridge = {
    listJobs: vi.fn(async (options: Parameters<QueryWorkspaceBridge['listJobs']>[0]) => {
      void options
      return ok(page())
    }),
    getJob: vi.fn(async () => ok(original)),
    getQueryResultDescriptor: vi.fn(async () => ok(d)),
    getQueryRowsPage: vi.fn(async () =>
      ok({
        identity: d.identity,
        kind: 'rows' as const,
        order: 'query-index:asc' as const,
        rows: [
          {
            index: 0,
            rowKey: hash('row'),
            cells: [{ kind: 'iri', iri: 'urn:original-device', n3: '<urn:original-device>' }],
          },
        ],
        nextCursor: null as string | null,
      }),
    ),
    getQueryExecutedTextPage: vi.fn(async () =>
      ok({
        identity: d.identity,
        kind: 'text' as const,
        order: 'utf8-byte:asc' as const,
        startUtf8Byte: 0,
        utf8Length: d.executedText.utf8Bytes,
        text: 'SELECT ?device WHERE { ?device ?p ?o }',
        nextCursor: null,
      }),
    ),
    executeSavedQuery: vi.fn(async () => failed),
    confirmProjectChangeset: vi.fn(async () => failed),
    commitProjectChangeSet: vi.fn(async () => failed),
    saveProjectDraft: vi.fn(async () => failed),
    onTaskUpdate: vi.fn((fn: (value: TaskUpdate) => void) => {
      listener = fn
      return () => {
        listener = () => {}
      }
    }),
  }
  const verifier = vi.fn(async () => [])
  const controller = new QueryWorkspaceController(
    pid,
    bridge as unknown as QueryWorkspaceBridge,
    verifier,
  )
  const markup = () => renderToStaticMarkup(createElement(QueryWorkspacePage, { controller }))
  return {
    original,
    d,
    page,
    bridge,
    verifier,
    controller,
    markup,
    emit: (value: TaskUpdate) => listener(value),
  }
}

describe('persistent query result restoration in the same page', () => {
  it('lists and explicitly restores a durable query after a fresh controller without executing or replacing edits', async () => {
    const x = setup()
    expect(validateV2('job', x.original)).toBe(true)
    expect(x.controller.getSnapshot().job).toBeUndefined()
    x.controller.editDraft({ name: 'unsaved editor', sparql: 'different visible text' })
    const before = x.controller.getSnapshot().draft
    await x.controller.readQueryHistory(true)
    expect(x.bridge.listJobs).toHaveBeenCalledWith({
      filter: 'terminal',
      pageSize: 100,
      listSnapshotId: null,
      cursor: null,
    })
    expect(x.markup()).toContain('恢复此查询任务的结果')
    await x.controller.restoreQueryResult(jid)
    expect(x.bridge.getJob).toHaveBeenCalledWith(jid)
    expect(x.bridge.getQueryResultDescriptor).toHaveBeenCalledWith({ resultId: rid })
    expect(x.controller.getSnapshot().draft).toEqual(before)
    expect(x.controller.getSnapshot().job).toBeUndefined()
    expect(x.controller.getSnapshot().historyResult?.descriptor).toEqual(x.d)
    expect(x.markup()).toContain('所选历史任务结果')
    expect(x.markup()).toContain(x.original.inputSnapshotId)
    expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    expect(x.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
    expect(x.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    expect(x.bridge.saveProjectDraft).not.toHaveBeenCalled()
    expect(x.verifier).not.toHaveBeenCalled()
  })

  it('shows historical input and stale metadata independently, with original text/table/CSV still readable', async () => {
    for (const input of ['current', 'historical'] as const) {
      const x = setup()
      Object.assign(x.d, descriptor(x.original, input, 'stale'))
      await x.controller.readQueryHistory(true)
      await x.controller.restoreQueryResult(jid)
      await x.controller.readRows(null, 0, 'historyResult')
      await x.controller.readText(null, 0, 'historyResult')
      const result = x.controller.getSnapshot().historyResult!
      expect(result.text?.value).toMatchObject({ text: 'SELECT ?device WHERE { ?device ?p ?o }' })
      const csv = currentPageCsv(x.d, result.rows!.value as DisplayRowsPage, result.rows!.requested)
      expect(csv).toContain('<urn:original-device>')
      const markup = x.markup()
      expect(markup).toContain('FACTS_CHANGED')
      expect(markup).toContain('已过期')
      expect(markup).toContain('导出当前页 CSV')
      expect(markup).toContain(
        input === 'historical' ? '显式选择的历史快照' : '执行时的当前已提交输入',
      )
      expect(markup).toContain(x.original.inputSnapshotId)
      expect(x.controller.getSnapshot().result).toBeUndefined()
    }
  })

  it('keeps fixed list binding across pages including a page without query jobs', async () => {
    const x = setup(),
      nonquery = structuredClone(x.original)
    nonquery.capability = 'test.read'
    nonquery.jobId = id(0)
    nonquery.operationId = id(8)
    x.bridge.listJobs
      .mockResolvedValueOnce(ok(x.page([nonquery], cursor)))
      .mockResolvedValueOnce(ok(x.page()))
    await x.controller.readQueryHistory(true)
    expect(x.controller.getSnapshot().history?.jobs).toEqual([])
    await x.controller.readQueryHistory()
    expect(x.bridge.listJobs.mock.calls[1][0]).toEqual({
      filter: 'terminal',
      pageSize: 100,
      listSnapshotId: listRef,
      cursor,
    })
    expect(x.controller.getSnapshot().history?.jobs).toEqual([x.original])
    await x.controller.readQueryHistory()
    expect(x.bridge.listJobs).toHaveBeenCalledTimes(2)
    await x.controller.readQueryHistory(true)
    expect(x.bridge.listJobs.mock.calls[2][0]).toEqual({
      filter: 'terminal',
      pageSize: 100,
      listSnapshotId: null,
      cursor: null,
    })
  })

  it('rejects wrong project, list snapshot, repeated cursor and duplicate page order', async () => {
    for (const variant of ['project', 'snapshot', 'cursor', 'order']) {
      const x = setup()
      x.bridge.listJobs.mockResolvedValueOnce(ok(x.page([], cursor)))
      await x.controller.readQueryHistory(true)
      const old = x.controller.getSnapshot().history,
        bad = x.page()
      if (variant === 'project') bad.binding.projectId = id(99)
      if (variant === 'snapshot') bad.binding.listSnapshotId = id(99)
      if (variant === 'cursor') bad.nextCursor = cursor
      if (variant === 'order') bad.jobs = [x.original, x.original]
      x.bridge.listJobs.mockResolvedValueOnce(ok(bad))
      await x.controller.readQueryHistory()
      expect(x.controller.getSnapshot().history).toEqual(old)
      expect(x.controller.getSnapshot().historyResult).toBeUndefined()
    }
  })

  it('rejects a fresh Job that no longer matches its original durable list identity and immutable input', async () => {
    for (const field of [
      'projectId',
      'operationId',
      'input',
      'implementation',
      'limits',
      'stateVersion',
    ]) {
      const x = setup(),
        bad = structuredClone(x.original)
      if (field === 'input') bad.input = { ...(bad.input as object), definitionId: 'other-query' }
      else if (field === 'implementation')
        bad.implementation = { ...(bad.implementation as object), engineVersion: 'other' }
      else if (field === 'limits') bad.limits = { ...(bad.limits as object), totalMs: 99999 }
      else bad[field] = field === 'stateVersion' ? 1 : id(99)
      x.bridge.getJob.mockResolvedValueOnce(ok(bad))
      await x.controller.readQueryHistory(true)
      await x.controller.restoreQueryResult(jid)
      expect(x.controller.getSnapshot().historyResult).toBeUndefined()
      expect(x.bridge.getQueryResultDescriptor).not.toHaveBeenCalled()
    }
  })

  it('rejects descriptor identity/implementation mismatches instead of binding a different result to the old job', async () => {
    for (const field of [
      'inputSnapshotId',
      'definitionId',
      'parametersHash',
      'implementation',
    ] as const) {
      const x = setup()
      if (field === 'implementation') {
        x.d.identity.implementation = { ...x.d.identity.implementation, engineVersion: 'other' }
        x.d.metadata.implementation = x.d.identity.implementation
      } else {
        const value = field === 'definitionId' ? 'other-query' : hash('other')
        x.d.identity[field] = value
        x.d.metadata[field] = value
      }
      await x.controller.readQueryHistory(true)
      await x.controller.restoreQueryResult(jid)
      expect(x.controller.getSnapshot().historyResult).toBeUndefined()
      expect(x.markup()).not.toContain('导出当前页 CSV')
    }
  })

  it('preserves original result/snapshot identity when payload has been evicted', async () => {
    const x = setup()
    x.bridge.getQueryResultDescriptor.mockResolvedValueOnce({
      ok: false,
      error: {
        code: 'PAYLOAD_EVICTED',
        messageKey: 'result.payloadEvicted',
        retryable: false,
        params: { resultId: rid },
      },
    } as never)
    await x.controller.readQueryHistory(true)
    await x.controller.restoreQueryResult(jid)
    expect(x.markup()).toContain('此结果载荷已回收')
    expect(x.markup()).toContain(x.original.inputSnapshotId)
    expect(x.markup()).not.toContain('导出当前页 CSV')
    expect(x.controller.getSnapshot().historySelection?.jobId).toBe(jid)
    expect(x.controller.getSnapshot().notice).toContain('描述读取未完成')
  })

  it('restores historical ASK false with its snapshot and historical metadata without SELECT row reads', async () => {
    const x = setup()
    Object.assign(x.d, descriptor(x.original, 'historical', 'historical'))
    x.d.query = { kind: 'ASK', value: false }
    await x.controller.readQueryHistory(true)
    await x.controller.restoreQueryResult(jid)
    expect(x.markup()).toContain('历史结果')
    expect(x.markup()).toContain('false（未满足查询条件）')
    expect(x.markup()).toContain('导出 ASK 结果 CSV')
    expect(x.markup()).toContain(x.original.inputSnapshotId)
    expect(x.bridge.getQueryRowsPage).not.toHaveBeenCalled()
  })

  it('shows a failed/cancelled query without fabricating a result or executing it again', async () => {
    for (const state of ['failed', 'cancelled'] as const) {
      const x = setup()
      Object.assign(x.original, {
        state,
        resultRef: null,
        error: state === 'failed' ? failed.error : null,
      })
      await x.controller.readQueryHistory(true)
      await x.controller.restoreQueryResult(jid)
      expect(x.controller.getSnapshot().historySelection?.state).toBe(state)
      expect(x.controller.getSnapshot().historyResult).toBeUndefined()
      expect(x.bridge.getQueryResultDescriptor).not.toHaveBeenCalled()
      expect(x.bridge.executeSavedQuery).not.toHaveBeenCalled()
    }
  })

  it('discards a late historical descriptor after detach and requires a new authenticated read', async () => {
    const x = setup(),
      reply = deferred<ReturnType<typeof ok<DisplayDescriptor>>>()
    x.bridge.getQueryResultDescriptor.mockImplementationOnce(() => reply.promise)
    await x.controller.readQueryHistory(true)
    const reading = x.controller.restoreQueryResult(jid)
    await vi.waitFor(() => expect(x.bridge.getQueryResultDescriptor).toHaveBeenCalled())
    x.controller.disconnect()
    reply.resolve(ok(x.d))
    await reading
    expect(x.controller.getSnapshot().historyResult).toBeUndefined()
    expect(x.controller.getSnapshot().historySelection?.jobId).toBe(jid)
    await x.controller.restoreQueryResult(jid)
    expect(x.controller.getSnapshot().historyResult?.descriptor).toEqual(x.d)
  })

  it('pages a restored table on its original descriptor and exports only the selected page', async () => {
    const x = setup()
    if (x.d.query.kind !== 'SELECT') throw new Error('expected SELECT')
    x.d.query.rowCount = 2
    const first = (await x.bridge.getQueryRowsPage.getMockImplementation()!()).data
    x.bridge.getQueryRowsPage
      .mockResolvedValueOnce(ok({ ...first, nextCursor: cursor }))
      .mockResolvedValueOnce(
        ok({
          ...first,
          rows: [
            {
              ...first.rows[0],
              index: 1,
              rowKey: hash('row1'),
              cells: [{ kind: 'iri', iri: 'urn:second-device', n3: '<urn:second-device>' }],
            },
          ],
          nextCursor: null,
        }),
      )
    await x.controller.readQueryHistory(true)
    await x.controller.restoreQueryResult(jid)
    await x.controller.readRows(null, 0, 'historyResult')
    await x.controller.readRows(cursor, 1, 'historyResult')
    expect(x.bridge.getQueryRowsPage).toHaveBeenNthCalledWith(2, {
      descriptorRef,
      cursor,
      pageSize: 200,
    })
    const result = x.controller.getSnapshot().historyResult!
    const csv = currentPageCsv(x.d, result.rows!.value as DisplayRowsPage, result.rows!.requested)
    expect(csv).toContain('urn:second-device')
    expect(csv).not.toContain('urn:original-device')
  })

  it('fences history payload on a new source generation and restores a fresh stale descriptor explicitly', async () => {
    const x = setup()
    x.controller.connect()
    x.emit({ kind: 'job', generation: 1, job: x.original })
    await x.controller.readQueryHistory(true)
    await x.controller.restoreQueryResult(jid)
    x.emit({ kind: 'job', generation: 2, job: x.original })
    expect(x.controller.getSnapshot().historyResult).toBeUndefined()
    expect(x.controller.getSnapshot().history).toBeUndefined()
    expect(x.markup()).toContain('刷新历史查询任务')
    Object.assign(x.d, descriptor(x.original, 'current', 'stale'))
    await x.controller.readQueryHistory(true)
    await x.controller.restoreQueryResult(jid)
    expect(x.markup()).toContain('已过期')
    expect(x.controller.getSnapshot().historyResult?.descriptor).toMatchObject({
      metadata: { state: 'stale' },
    })
  })
})
