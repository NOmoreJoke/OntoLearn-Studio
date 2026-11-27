/** Real contract reassembly and renderer consumption; no engine or GUI evidence. */
import { createHash } from 'node:crypto'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { isTaskUpdate } from '@ontolearn/contracts'
import type {
  BridgeResult,
  OwnershipDetailDocument,
  OwnershipDetailPage,
} from '@ontolearn/contracts'
import type {
  DomainRead,
  MainlineTaskUpdate,
  OntologyMainlineBridge,
  Preview,
} from '../../apps/desktop/src/renderer/src/ontology/mainline-api'
import { readOwnershipConflictDetail } from '../../apps/desktop/src/renderer/src/ontology/mainline-ownership'
import { OntologySession } from '../../apps/desktop/src/renderer/src/ontology/mainline-session'
import { OntologyOperationBook } from '../../apps/desktop/src/renderer/src/ontology/mainline-operations'

const projectId = '00000000-0000-4000-8000-000000000003'
const detailRef = '00000000-0000-4000-8000-000000000005'
const otherId = '00000000-0000-4000-8000-000000000006'
const sha = (value: Uint8Array) => createHash('sha256').update(value).digest('hex')
const ok = <T>(data: T): BridgeResult<T> => ({ ok: true, data })
const failure = (code = 'INTERNAL_ERROR'): Extract<BridgeResult<never>, { ok: false }> => ({
  ok: false,
  error: { code, messageKey: 'engine.internal', params: {}, retryable: false },
})
const conflict = (): BridgeResult<Preview> => ({
  ok: false,
  error: {
    code: 'OWNERSHIP_CONFLICT',
    messageKey: 'project.ownershipConflict',
    params: { detailRef },
    retryable: false,
  },
})
const slot = { subject: '<urn:original:主体𠮷>', predicate: '<urn:original:predicate>' }
const existing = {
  id: '  historical original ID\n𠮷  ',
  owner: ' mapping original owner ',
  sourceRow: ' sheet 01!0007 ',
  slot,
}
const incoming = { id: 'd'.repeat(64), owner: null, sourceRow: null, slot }
const documentFor = (
  reason: OwnershipDetailDocument['reason'] = 'reservedIdentity',
): OwnershipDetailDocument =>
  reason === 'singleDeclaration'
    ? {
        ownershipDetailVersion: 1,
        kind: 'single-declaration-conflict',
        stage: 'preview',
        projectId,
        sourceBaseRevision: 7,
        reason,
        declaration: { layer: 'ontology', id: ' raw declaration ', predicate: slot.predicate },
        slot,
        existing: [
          { id: existing.id, owner: existing.owner, sourceRow: existing.sourceRow },
          { id: 'second original', owner: null, sourceRow: null },
        ],
      }
    : {
        ownershipDetailVersion: 1,
        kind: 'manual-ownership-conflict',
        stage: 'preview',
        projectId,
        sourceBaseRevision: 7,
        reason,
        existing: structuredClone(existing),
        incoming: structuredClone(incoming),
      }

function pagesFor(document: unknown): OwnershipDetailPage[] {
  const raw = Buffer.from(JSON.stringify(document))
  const segmentCount = Math.ceil(raw.length / 32768)
  return Array.from({ length: segmentCount }, (_, ordinal) => {
    const bytes = raw.subarray(ordinal * 32768, (ordinal + 1) * 32768)
    return {
      detailReadVersion: 1,
      projectId,
      detailRef,
      manifest: {
        documentKind: 'ownership-conflict',
        documentHash: sha(raw),
        totalBytes: raw.length,
        segmentCount,
      },
      startOrdinal: ordinal,
      segments: [
        {
          ordinal,
          byteOffset: ordinal * 32768,
          rawByteLength: bytes.length,
          sha256: sha(bytes),
          dataBase64: bytes.toString('base64'),
        },
      ],
      nextOrdinal: ordinal + 1 === segmentCount ? null : ordinal + 1,
      complete: ordinal + 1 === segmentCount,
    }
  })
}
function largeDocument() {
  const document = documentFor('sameStatement')
  if (document.reason === 'singleDeclaration') throw new Error('wrong fixture')
  document.existing.id = `  legacy:${'界𠮷'.repeat(7000)}:END  `
  document.existing.owner = '<script>raw owner & "value"</script>'
  return document
}
function reader(pages = pagesFor(documentFor())) {
  const getter = vi.fn<OntologyMainlineBridge['getOwnershipConflictDetailPage']>(async (args) =>
    ok(structuredClone(pages[args.startOrdinal]!)),
  )
  return { getter, bridge: { getOwnershipConflictDetailPage: getter } }
}
const binding = { projectId, detailRef, sourceBaseRevision: 7 }
const connection = (generation: number): MainlineTaskUpdate => ({
  kind: 'connection',
  generation,
  projectId,
  state: 'offline',
  attempt: 3,
  error: failure().error,
})
function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason: Error) => void
  const promise = new Promise<T>((yes, no) => {
    resolve = yes
    reject = no
  })
  return { promise, resolve, reject }
}
const flush = async () => {
  for (let i = 0; i < 30; i++) await Promise.resolve()
}
afterEach(() => vi.restoreAllMocks())

describe('actual ownership adapter and public reassembly', () => {
  it.each(['reservedIdentity', 'sameStatement', 'singleSlot', 'singleDeclaration'] as const)(
    'maps %s from the validated canonical document without changing originals',
    async (reason) => {
      const document = documentFor(reason),
        h = reader(pagesFor(document))
      const view = await readOwnershipConflictDetail(h.bridge, binding, () => {})
      expect(view.previewBaseRevision).toBe(7)
      expect(view.reason).toBe(reason)
      if (document.reason === 'singleDeclaration') {
        expect(view.declaration).toEqual(document.declaration)
        expect(view.records).toEqual(
          document.existing.map((record) => ({ ...record, role: 'existing', slot: document.slot })),
        )
      } else {
        expect(view.declaration).toBeUndefined()
        expect(view.records).toEqual([
          { ...document.existing, role: 'existing' },
          { ...document.incoming, role: 'incoming' },
        ])
      }
      expect(h.getter).toHaveBeenCalledWith({
        detailRef,
        documentHash: null,
        startOrdinal: 0,
        pageSize: 64,
      })
    },
  )

  it('assembles multiple actual segments and preserves >17KiB raw Unicode ID, owner, sourceRow and nulls', async () => {
    const document = largeDocument(),
      pages = pagesFor(document),
      h = reader(pages)
    expect(pages.length).toBeGreaterThan(1)
    expect(Buffer.byteLength(document.existing.id)).toBeGreaterThan(17 * 1024)
    const view = await readOwnershipConflictDetail(h.bridge, binding, () => {})
    expect(view.records).toEqual([
      { ...document.existing, role: 'existing' },
      { ...document.incoming, role: 'incoming' },
    ])
    expect(h.getter).toHaveBeenCalledTimes(pages.length)
    expect(h.getter.mock.calls.map(([args]) => args)).toEqual(
      pages.map((page, i) => ({
        detailRef,
        documentHash: i === 0 ? null : pages[0]!.manifest.documentHash,
        startOrdinal: page.startOrdinal,
        pageSize: 64,
      })),
    )
  })

  it.each([6, 8])('rejects document revision %i against preview revision 7', async (revision) => {
    const h = reader(pagesFor({ ...documentFor(), sourceBaseRevision: revision }))
    await expect(readOwnershipConflictDetail(h.bridge, binding, () => {})).rejects.toThrow(
      'INVALID_OWNERSHIP_DETAIL',
    )
  })

  it.each([
    [
      'project',
      (p: OwnershipDetailPage) => {
        p.projectId = otherId
      },
    ],
    [
      'reference',
      (p: OwnershipDetailPage) => {
        p.detailRef = otherId
      },
    ],
    [
      'start ordinal',
      (p: OwnershipDetailPage) => {
        p.startOrdinal = 1
      },
    ],
    [
      'segment ordinal',
      (p: OwnershipDetailPage) => {
        p.segments[0]!.ordinal++
      },
    ],
    [
      'segment offset',
      (p: OwnershipDetailPage) => {
        p.segments[0]!.byteOffset++
      },
    ],
    [
      'segment length',
      (p: OwnershipDetailPage) => {
        p.segments[0]!.rawByteLength++
      },
    ],
    [
      'segment hash',
      (p: OwnershipDetailPage) => {
        p.segments[0]!.sha256 = 'f'.repeat(64)
      },
    ],
    [
      'base64',
      (p: OwnershipDetailPage) => {
        p.segments[0]!.dataBase64 = 'not-base64!'
      },
    ],
    [
      'budget',
      (p: OwnershipDetailPage) => {
        p.manifest.totalBytes = 16 * 1024 * 1024 + 1
      },
    ],
    [
      'segment budget',
      (p: OwnershipDetailPage) => {
        p.manifest.segmentCount = 513
      },
    ],
    [
      'no progress',
      (p: OwnershipDetailPage) => {
        p.nextOrdinal = 0
        p.complete = false
      },
    ],
    [
      'premature complete',
      (p: OwnershipDetailPage) => {
        p.complete = true
        p.nextOrdinal = null
      },
    ],
    [
      'missing segment',
      (p: OwnershipDetailPage) => {
        p.segments = []
      },
    ],
    [
      'duplicate segment',
      (p: OwnershipDetailPage) => {
        p.segments.push(structuredClone(p.segments[0]!))
      },
    ],
  ] as const)(
    'rejects %s without reading further or publishing a partial VM',
    async (_name, mutate) => {
      const pages = pagesFor(largeDocument())
      mutate(pages[0]!)
      const h = reader(pages)
      await expect(readOwnershipConflictDetail(h.bridge, binding, () => {})).rejects.toThrow(
        'INVALID_OWNERSHIP_DETAIL',
      )
      expect(h.getter).toHaveBeenCalledTimes(1)
    },
  )

  it.each(['hash', 'total', 'repeat', 'skip', 'denied', 'throw'] as const)(
    'rejects bad later page: %s',
    async (kind) => {
      const pages = pagesFor(largeDocument()),
        h = reader(pages)
      const second = structuredClone(pages[1]!)
      if (kind === 'hash') second.manifest.documentHash = 'f'.repeat(64)
      if (kind === 'total') second.manifest.totalBytes++
      if (kind === 'repeat') second.startOrdinal = 0
      if (kind === 'skip') second.startOrdinal++
      h.getter.mockResolvedValueOnce(ok(pages[0]!))
      if (kind === 'denied') h.getter.mockResolvedValueOnce(failure('PERMISSION_DENIED'))
      else if (kind === 'throw')
        h.getter.mockRejectedValueOnce(new Error('private filesystem exception'))
      else h.getter.mockResolvedValueOnce(ok(second))
      await expect(readOwnershipConflictDetail(h.bridge, binding, () => {})).rejects.toThrow()
      expect(h.getter).toHaveBeenCalledTimes(2)
    },
  )

  it.each([
    'document hash',
    'document project',
    'old three-field object',
    'invalid reason',
  ] as const)('lets the public reassembler reject %s', async (kind) => {
    let document: unknown = documentFor()
    if (kind === 'document project') document = { ...documentFor(), projectId: otherId }
    if (kind === 'old three-field object')
      document = { category: 'fact_owner', resource: 'old', projectId }
    if (kind === 'invalid reason') document = { ...documentFor(), reason: 'unknown' }
    const pages = pagesFor(document)
    if (kind === 'document hash') pages[0]!.manifest.documentHash = 'f'.repeat(64)
    const h = reader(pages)
    await expect(readOwnershipConflictDetail(h.bridge, binding, () => {})).rejects.toThrow(
      'INVALID_OWNERSHIP_DETAIL',
    )
  })

  it('guards after the real public reassembler SHA await', async () => {
    const pages = pagesFor(documentFor()),
      h = reader(pages)
    const digest = deferred<ArrayBuffer>()
    vi.spyOn(crypto.subtle, 'digest').mockReturnValueOnce(digest.promise)
    let current = true
    const promise = readOwnershipConflictDetail(h.bridge, binding, () => {
      if (!current) throw new Error('STALE_CONTEXT')
    })
    await flush()
    expect(crypto.subtle.digest).toHaveBeenCalledTimes(1)
    current = false
    digest.resolve(Uint8Array.from(Buffer.from(pages[0]!.manifest.documentHash, 'hex')).buffer)
    await expect(promise).rejects.toThrow('STALE_CONTEXT')
  })
  it('owns a private page capture while the public SHA await is pending', async () => {
    const document = documentFor(),
      pages = pagesFor(document),
      h = reader(pages)
    h.getter.mockResolvedValueOnce(ok(pages[0]!))
    const digest = deferred<ArrayBuffer>()
    vi.spyOn(crypto.subtle, 'digest').mockReturnValueOnce(digest.promise)
    const promise = readOwnershipConflictDetail(h.bridge, binding, () => {})
    await flush()
    expect(crypto.subtle.digest).toHaveBeenCalledTimes(1)
    const expectedHash = pages[0]!.manifest.documentHash
    pages[0]!.segments[0]!.dataBase64 = ''
    digest.resolve(Uint8Array.from(Buffer.from(expectedHash, 'hex')).buffer)
    expect((await promise).records[0]).toEqual({ ...existing, role: 'existing' })
  })
})

function contextSource(): DomainRead {
  return {
    readVersion: 1,
    projectId,
    inputSnapshotId: 'a'.repeat(64),
    workspace: { draft: { state: 'missing', editor: 'ontology-transaction' } },
    domain: {
      projectRevision: 7,
      dependencyVector: { 'facts:asserted': 2 },
      state: { definitions: [], facts: [], mappingState: {} },
    },
  }
}
function sessionHarness(pages = pagesFor(documentFor())) {
  let source = contextSource()
  let listener: ((update: MainlineTaskUpdate) => void) | undefined
  const bridge: OntologyMainlineBridge = {
    getOwnershipConflictDetailPage: vi.fn(async (args) =>
      ok(structuredClone(pages[args.startOrdinal]!)),
    ),
    readProject: vi.fn(async () => ok(structuredClone(source))),
    getActiveProject: vi.fn(async () =>
      ok({
        projectId: source.projectId,
        projectRevision: source.domain.projectRevision,
        inputSnapshotId: source.inputSnapshotId,
        dependencyVector: source.domain.dependencyVector,
        formatVersion: 3 as const,
      }),
    ),
    previewProjectChangeset: vi.fn(async () => conflict()),
    getProjectDiffPage: vi.fn(async () => failure()),
    confirmProjectChangeset: vi.fn(async () => failure()),
    saveProjectDraft: vi.fn(async () => failure()),
    commitProjectChangeSet: vi.fn(async () => failure()),
    getJob: vi.fn(async () => failure()),
    listJobs: vi.fn(async () => failure()),
    getOperation: vi.fn(async () => failure()),
    cancelJob: vi.fn(async () => failure()),
    onTaskUpdate: vi.fn((next) => {
      listener = next
      return () => {
        listener = undefined
      }
    }),
  }
  const book = new OntologyOperationBook(),
    session = new OntologySession(bridge, book)
  session.connect()
  return {
    bridge,
    book,
    session,
    source: () => source,
    setSource: (next: DomainRead) => {
      source = next
    },
    emit: (update: MainlineTaskUpdate) => {
      expect(isTaskUpdate(update)).toBe(true)
      listener?.(update)
    },
  }
}
const plan = {
  manual: [{ id: 'd'.repeat(64), subject: 'urn:s', predicate: 'urn:p', object: '"new"' }],
}
function noWrite(h: ReturnType<typeof sessionHarness>) {
  expect(h.session.getSnapshot().prepared).toBeUndefined()
  expect(h.session.getSnapshot().pending).toBeUndefined()
  expect(h.session.getSnapshot().receipt).toBeUndefined()
  expect(h.book.get(projectId)).toBeUndefined()
  for (const name of [
    'getProjectDiffPage',
    'confirmProjectChangeset',
    'saveProjectDraft',
    'commitProjectChangeSet',
    'getJob',
    'listJobs',
    'getOperation',
    'cancelJob',
  ] as const)
    expect(h.bridge[name]).not.toHaveBeenCalled()
}

describe('actual Session ownership detail binding', () => {
  it.each(['reservedIdentity', 'sameStatement', 'singleSlot', 'singleDeclaration'] as const)(
    'publishes only the validated %s VM and never creates a transaction',
    async (reason) => {
      const h = sessionHarness(pagesFor(documentFor(reason)))
      await h.session.read()
      const before = structuredClone(h.session.getSnapshot().source)
      await h.session.prepare(plan)
      expect(h.session.getSnapshot().ownershipDetail).toMatchObject({
        status: 'ready',
        viewModel: { reason, previewBaseRevision: 7 },
      })
      expect(h.session.getSnapshot().error).toBe('OWNERSHIP_CONFLICT')
      expect(h.session.getSnapshot().source).toEqual(before)
      expect(h.session.getSnapshot().phase).toBe('idle')
      expect(JSON.stringify(h.session.getSnapshot())).not.toContain(detailRef)
      expect(h.bridge.previewProjectChangeset).toHaveBeenCalledTimes(1)
      noWrite(h)
    },
  )

  it.each([undefined, null, 7, {}, '', 'bad-ref', otherId + ' ', 'x'.repeat(100000)])(
    'rejects invalid detailRef without invoking the getter: %j',
    async (value) => {
      const h = sessionHarness()
      await h.session.read()
      const error = conflict()
      if (error.ok) throw new Error('wrong fixture')
      error.error.params = value === undefined ? {} : { detailRef: value }
      vi.mocked(h.bridge.previewProjectChangeset).mockResolvedValueOnce(error)
      await h.session.prepare(plan)
      expect(h.session.getSnapshot().ownershipDetail).toEqual({ status: 'unavailable' })
      expect(h.bridge.getOwnershipConflictDetailPage).not.toHaveBeenCalled()
      noWrite(h)
    },
  )

  it.each(['throw same code', 'unknown code', 'wrong message', 'extra params'] as const)(
    'does not treat %s as an authorized lookup',
    async (kind) => {
      const h = sessionHarness()
      await h.session.read()
      if (kind === 'throw same code')
        vi.mocked(h.bridge.previewProjectChangeset).mockRejectedValueOnce(
          new Error('OWNERSHIP_CONFLICT'),
        )
      else {
        const result = conflict()
        if (result.ok) throw new Error('wrong fixture')
        if (kind === 'unknown code') result.error.code = 'OWNERSHIP_CONFLICT:secret'
        if (kind === 'wrong message') result.error.messageKey = 'secret'
        if (kind === 'extra params') result.error.params.secret = 'private'
        vi.mocked(h.bridge.previewProjectChangeset).mockResolvedValueOnce(result)
      }
      await h.session.prepare(plan)
      expect(h.bridge.getOwnershipConflictDetailPage).not.toHaveBeenCalled()
      expect(JSON.stringify(h.session.getSnapshot())).not.toContain('secret')
      noWrite(h)
    },
  )

  it.each([
    'permission',
    'budget',
    'unknown',
    'exception',
    'old revision',
    'future revision',
    'wrong project',
    'old object',
  ] as const)('rejects %s safely with no automatic preview replay', async (kind) => {
    const h = sessionHarness()
    await h.session.read()
    const get = vi.mocked(h.bridge.getOwnershipConflictDetailPage)
    if (kind === 'exception') get.mockRejectedValueOnce(new Error('private absolute path /secret'))
    else if (kind === 'permission' || kind === 'budget' || kind === 'unknown')
      get.mockResolvedValueOnce(
        failure(
          kind === 'permission'
            ? 'PERMISSION_DENIED'
            : kind === 'budget'
              ? 'RESOURCE_LIMIT'
              : 'PRIVATE_ERROR',
        ),
      )
    else {
      const doc =
        kind === 'old object'
          ? { category: 'fact_owner', resource: 'secret', projectId }
          : {
              ...documentFor(),
              sourceBaseRevision: kind === 'old revision' ? 6 : kind === 'future revision' ? 8 : 7,
              projectId: kind === 'wrong project' ? otherId : projectId,
            }
      get.mockResolvedValueOnce(ok(pagesFor(doc)[0]!))
    }
    await h.session.prepare(plan)
    expect(h.session.getSnapshot().ownershipDetail).toEqual({ status: 'unavailable' })
    expect(JSON.stringify(h.session.getSnapshot())).not.toMatch(/secret|PRIVATE_ERROR|absolute/)
    expect(h.bridge.previewProjectChangeset).toHaveBeenCalledTimes(1)
    noWrite(h)
  })

  it.each(['discard', 'read', 'invalidate', 'dispose', 'retire', 'connection', 'book'] as const)(
    'clears visible details synchronously on %s',
    async (kind) => {
      const h = sessionHarness()
      await h.session.read()
      await h.session.prepare(plan)
      expect(h.session.getSnapshot().ownershipDetail?.status).toBe('ready')
      let pending: Promise<void> | undefined
      if (kind === 'discard') h.session.discardPreview()
      if (kind === 'read') pending = h.session.read()
      if (kind === 'invalidate') h.session.invalidate()
      if (kind === 'dispose') {
        h.session.dispose()
        h.session.connect()
      }
      if (kind === 'retire') h.session.retire()
      if (kind === 'connection') h.emit(connection(2))
      if (kind === 'book')
        h.book.pending({
          operationId: otherId,
          confirmationRef: detailRef,
          preview: {
            projectId,
            baseRevision: 7,
            inputSnapshotId: 'a'.repeat(64),
            preparedPlanRef: 'b'.repeat(64),
            parametersHash: 'c'.repeat(64),
          },
        })
      expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
      await pending
    },
  )

  it.each(['preview', 'first page', 'middle page', 'digest', 'final active'] as const)(
    'rejects late success/error after invalidation at %s',
    async (stage) => {
      for (const reject of [false, true]) {
        const pages = pagesFor(largeDocument()),
          h = sessionHarness(pages)
        await h.session.read()
        const delayed = deferred<BridgeResult<OwnershipDetailPage>>()
        const previewDelay = deferred<BridgeResult<Preview>>()
        const activeDelay =
          deferred<Awaited<ReturnType<OntologyMainlineBridge['getActiveProject']>>>()
        const digestDelay = deferred<ArrayBuffer>()
        if (stage === 'preview')
          vi.mocked(h.bridge.previewProjectChangeset).mockReturnValueOnce(previewDelay.promise)
        if (stage === 'first page')
          vi.mocked(h.bridge.getOwnershipConflictDetailPage).mockReturnValueOnce(delayed.promise)
        if (stage === 'middle page')
          vi.mocked(h.bridge.getOwnershipConflictDetailPage)
            .mockResolvedValueOnce(ok(pages[0]!))
            .mockReturnValueOnce(delayed.promise)
        if (stage === 'digest')
          vi.spyOn(crypto.subtle, 'digest').mockReturnValueOnce(digestDelay.promise)
        if (stage === 'final active') {
          const active = {
            projectId,
            projectRevision: 7,
            inputSnapshotId: 'a'.repeat(64),
            dependencyVector: { 'facts:asserted': 2 },
            formatVersion: 3 as const,
          }
          vi.mocked(h.bridge.getActiveProject)
            .mockResolvedValueOnce(ok(active))
            .mockResolvedValueOnce(ok(active))
            .mockReturnValueOnce(activeDelay.promise)
        }
        const preparing = h.session.prepare(plan)
        await vi.waitFor(() => {
          if (stage === 'preview') expect(h.bridge.previewProjectChangeset).toHaveBeenCalledTimes(1)
          if (stage === 'first page')
            expect(h.bridge.getOwnershipConflictDetailPage).toHaveBeenCalledTimes(1)
          if (stage === 'middle page')
            expect(h.bridge.getOwnershipConflictDetailPage).toHaveBeenCalledTimes(2)
          if (stage === 'digest') expect(crypto.subtle.digest).toHaveBeenCalledTimes(1)
          if (stage === 'final active') expect(h.bridge.getActiveProject).toHaveBeenCalledTimes(3)
        })
        h.session.discardPreview()
        const stable = h.session.getSnapshot()
        if (stage === 'preview') {
          if (reject) previewDelay.reject(new Error('private late failure'))
          else previewDelay.resolve(conflict())
        }
        if (stage === 'first page' || stage === 'middle page') {
          if (reject) delayed.reject(new Error('private late failure'))
          else delayed.resolve(ok(pages[stage === 'first page' ? 0 : 1]!))
        }
        if (stage === 'digest') {
          if (reject) digestDelay.reject(new Error('private late failure'))
          else
            digestDelay.resolve(
              Uint8Array.from(Buffer.from(pages[0]!.manifest.documentHash, 'hex')).buffer,
            )
        }
        if (stage === 'final active') {
          if (reject) activeDelay.reject(new Error('private late failure'))
          else
            activeDelay.resolve(
              ok({
                projectId,
                projectRevision: 7,
                inputSnapshotId: 'a'.repeat(64),
                dependencyVector: { 'facts:asserted': 2 },
                formatVersion: 3,
              }),
            )
        }
        await preparing
        expect(h.session.getSnapshot()).toBe(stable)
        noWrite(h)
        vi.restoreAllMocks()
      }
    },
  )

  it.each(['project', 'revision', 'snapshot', 'dependencies', 'null'] as const)(
    'rechecks active %s before publishing a complete detail',
    async (kind) => {
      const h = sessionHarness()
      await h.session.read()
      const active = {
        projectId,
        projectRevision: 7,
        inputSnapshotId: 'a'.repeat(64),
        dependencyVector: { 'facts:asserted': 2 },
        formatVersion: 3 as const,
      }
      const getter = vi.mocked(h.bridge.getActiveProject)
      getter.mockResolvedValueOnce(ok(active)).mockResolvedValueOnce(ok(active))
      const changed = { ...active }
      if (kind === 'project') changed.projectId = otherId
      if (kind === 'revision') changed.projectRevision++
      if (kind === 'snapshot') changed.inputSnapshotId = 'b'.repeat(64)
      if (kind === 'dependencies') changed.dependencyVector = { 'facts:asserted': 3 }
      getter.mockResolvedValueOnce(ok(kind === 'null' ? null : changed))
      await h.session.prepare(plan)
      expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
      expect(h.session.getSnapshot().stale).toBe(true)
      noWrite(h)
    },
  )

  it('fences a synchronous subscriber that discards as detail reading is published', async () => {
    const h = sessionHarness()
    await h.session.read()
    h.session.subscribe(() => {
      if (h.session.getSnapshot().ownershipDetail?.status === 'reading') h.session.discardPreview()
    })
    await h.session.prepare(plan)
    expect(h.bridge.getOwnershipConflictDetailPage).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
    noWrite(h)
  })

  it.each([
    'read',
    'retire',
    'dispose reconnect',
    'connection',
    'generation',
    'new preview',
    'book',
  ] as const)('isolates late first-page success/error after %s', async (kind) => {
    for (const rejects of [false, true]) {
      const h = sessionHarness(),
        delayed = deferred<BridgeResult<OwnershipDetailPage>>()
      await h.session.read()
      vi.mocked(h.bridge.getOwnershipConflictDetailPage).mockReturnValueOnce(delayed.promise)
      const old = h.session.prepare(plan)
      await vi.waitFor(() =>
        expect(h.bridge.getOwnershipConflictDetailPage).toHaveBeenCalledTimes(1),
      )
      if (kind === 'read') await h.session.read()
      if (kind === 'retire') h.session.retire()
      if (kind === 'dispose reconnect') {
        h.session.dispose()
        h.session.connect()
        await h.session.read()
      }
      if (kind === 'connection') h.emit(connection(1))
      if (kind === 'generation') {
        h.emit({
          kind: 'restored',
          generation: 1,
          view: { generation: 1, project: null, jobs: [] },
        })
        h.emit({
          kind: 'restored',
          generation: 2,
          view: { generation: 2, project: null, jobs: [] },
        })
      }
      if (kind === 'new preview') {
        h.session.discardPreview()
        await h.session.prepare(plan)
        expect(h.session.getSnapshot().ownershipDetail?.status).toBe('ready')
      }
      if (kind === 'book')
        h.book.pending({
          operationId: otherId,
          confirmationRef: detailRef,
          preview: {
            projectId,
            baseRevision: 7,
            inputSnapshotId: 'a'.repeat(64),
            preparedPlanRef: 'b'.repeat(64),
            parametersHash: 'c'.repeat(64),
          },
        })
      const stable = h.session.getSnapshot()
      if (rejects) delayed.reject(new Error('private late first page'))
      else delayed.resolve(ok(pagesFor(documentFor())[0]!))
      await old
      expect(h.session.getSnapshot()).toBe(stable)
      expect(h.bridge.confirmProjectChangeset).not.toHaveBeenCalled()
      expect(h.bridge.saveProjectDraft).not.toHaveBeenCalled()
      expect(h.bridge.commitProjectChangeSet).not.toHaveBeenCalled()
    }
  })

  it('clears an earlier ready panel at the call of a new preview, before its ACK', async () => {
    const h = sessionHarness()
    await h.session.read()
    await h.session.prepare(plan)
    const delayed = deferred<BridgeResult<Preview>>()
    vi.mocked(h.bridge.previewProjectChangeset).mockReturnValueOnce(delayed.promise)
    const preparing = h.session.prepare(plan)
    expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
    await flush()
    delayed.resolve(failure())
    await preparing
    expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
    noWrite(h)
  })

  it('does not look up details for a read failure carrying the same ownership code', async () => {
    const h = sessionHarness()
    vi.mocked(h.bridge.readProject).mockResolvedValueOnce(failure('OWNERSHIP_CONFLICT'))
    await h.session.read()
    expect(h.bridge.getOwnershipConflictDetailPage).not.toHaveBeenCalled()
    expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
  })
  it('reserves a read before detail-clearing subscribers can request a coalesced refresh', async () => {
    const h = sessionHarness()
    await h.session.read()
    await h.session.prepare(plan)
    let refresh: Promise<void> | undefined
    let requested = false
    const release = h.session.subscribe(() => {
      if (!requested && !h.session.getSnapshot().ownershipDetail) {
        requested = true
        refresh = h.session.read()
      }
    })
    await h.session.read()
    await refresh
    release()
    expect(requested).toBe(true)
    expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
    expect(h.session.getSnapshot().stale).toBe(false)
    expect(h.session.getSnapshot().phase).toBe('idle')
  })
  it.each([2, 3])(
    'fences the caller microtask gap after active-context check %i',
    async (target) => {
      const h = sessionHarness()
      await h.session.read()
      const actual = h.bridge.getActiveProject
      let calls = 0
      h.bridge.getActiveProject = vi.fn(() =>
        actual().then((result) => {
          if (++calls === target) queueMicrotask(() => queueMicrotask(() => h.session.retire()))
          return result
        }),
      )
      await h.session.prepare(plan)
      expect(h.bridge.getActiveProject).toHaveBeenCalledTimes(target)
      expect(h.bridge.getOwnershipConflictDetailPage).toHaveBeenCalledTimes(target === 2 ? 0 : 1)
      expect(h.session.getSnapshot().ownershipDetail).toBeUndefined()
      expect(h.session.getSnapshot().stale).toBe(true)
      noWrite(h)
    },
  )
})
