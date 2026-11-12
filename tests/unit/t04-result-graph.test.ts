import { createHash } from 'node:crypto'
import { createElement, type ComponentType } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import fixtures from '../../packages/contracts/v2/fixtures.json'
import { validateBusiness3 } from '../../packages/contracts/src/v2'
import type { MainlineProjectReadDTO } from '../../apps/desktop/src/renderer/src/query/api002-source-types'
import {
  buildResultGraph,
  graphLimits,
} from '../../apps/desktop/src/renderer/src/query/result-graph'
import {
  displayDescriptor,
  type DisplayDescriptor,
  type DisplayRowsPage,
} from '../../apps/desktop/src/renderer/src/query/typed-results'
import type { QueryResultPanelProps } from '../../apps/desktop/src/renderer/src/query/typed-result-panel-props'

// Consumer fixtures + real TSX SSR only; mapped cases are not physical mapping runs.
const panelModule = '../../apps/desktop/src/renderer/src/query/QueryResultPanel'
const { QueryResultPanel }: { QueryResultPanel: ComponentType<QueryResultPanelProps> } =
  await import(panelModule)
const hash = (s: string) => createHash('sha256').update(s).digest('hex')
const A = 'urn:test:A',
  B = 'urn:test:B',
  C = 'urn:test:C',
  D = 'urn:test:D',
  E = 'urn:test:E'
const P = 'urn:test:links',
  Q = 'urn:test:other'
type Fact = MainlineProjectReadDTO['domain']['state']['facts'][number]
const fact = (id: number, subject: string, predicate: string, object: string | null): Fact => ({
  id: hash('stable-record-' + id),
  subject,
  predicate,
  object,
  owner: null,
  source_row: null,
  managed_value: null,
})
function setup() {
  const metadata = structuredClone(
    (
      fixtures.cases.find((x) => x.name === 'response result.get')!.value as unknown as {
        result: DisplayDescriptor['metadata']
      }
    ).result,
  )
  const descriptor: DisplayDescriptor = {
    identity: {
      projectId: metadata.projectId,
      resultId: metadata.resultId,
      jobId: metadata.jobId,
      inputSnapshotId: metadata.inputSnapshotId,
      inputProjectRevision: 1,
      scope: 'asserted',
      definitionId: metadata.definitionId,
      parametersHash: metadata.parametersHash,
      implementation: metadata.implementation,
      payloadSha256: hash('payload'),
      definitionSha256: hash('definition'),
      inputSelection: 'current',
      projectionVersion: 1,
      lengthPolicyId: 'query-presentation-scalars-v1',
    },
    descriptorRef: '40000000-0000-4000-8000-000000000001',
    metadata,
    executedText: { sha256: hash('text'), utf8Bytes: 4, unicodeScalars: 4, utf16Units: 4 },
    query: {
      kind: 'SELECT',
      rowCount: 1,
      columns: [
        { index: 0, name: 's' },
        { index: 1, name: 'p' },
      ],
    },
  }
  const source: MainlineProjectReadDTO = {
    readVersion: 1,
    projectId: metadata.projectId,
    inputSnapshotId: metadata.inputSnapshotId,
    workspace: {
      workspaceVersion: 1,
      projectId: metadata.projectId,
      inputSnapshotId: metadata.inputSnapshotId,
      domainRevision: 1,
      metadataVersion: 1,
      metadata: {
        name: 'fixture',
        templateRef: null,
        archived: false,
        mode: 'guided',
        origin: 'created',
      },
      operationSequence: 1,
      checkpointRef: hash('checkpoint'),
      draft: { editor: 'query-workspace-v1', state: 'missing' },
    },
    domain: {
      projectRevision: 1,
      dependencyVector: { 'facts:asserted': 1 },
      state: {
        definitions: [],
        facts: [fact(1, A, P, `<${B}>`), fact(2, B, Q, `<${C}>`), fact(3, C, P, `<${E}>`)],
        mappingState: {},
      },
    },
  }
  const rowKey = hash('original-row')
  const page: DisplayRowsPage = {
    identity: structuredClone(descriptor.identity),
    kind: 'rows',
    order: 'query-index:asc',
    rows: [
      {
        index: 0,
        rowKey,
        cells: [
          { kind: 'iri', iri: B, n3: `<${B}>` },
          { kind: 'iri', iri: D, n3: `<${D}>` },
        ],
      },
    ],
    nextCursor: null,
  }
  const requested = {
    descriptorRef: descriptor.descriptorRef,
    cursor: null as string | null,
    startIndex: 0,
    pageSize: 20,
  }
  expect(validateBusiness3('result_project.read', source)).toBe(true)
  expect(
    displayDescriptor(descriptor, { projectId: metadata.projectId, resultId: metadata.resultId }),
  ).toEqual(descriptor)
  const graph = () => buildResultGraph(source, descriptor, page, requested, rowKey)
  const markup = (patch: Partial<QueryResultPanelProps> = {}) =>
    renderToStaticMarkup(
      createElement(QueryResultPanel, {
        projectId: metadata.projectId,
        resultId: metadata.resultId,
        descriptor,
        graphSource: source,
        rows: { value: page, requested },
        ...patch,
      }),
    )
  return { source, descriptor, page, requested, rowKey, graph, markup }
}
const ready = (value: ReturnType<typeof buildResultGraph>) => {
  expect(value.state).toBe('ready')
  if (value.state !== 'ready') throw new Error(value.reason)
  return value
}

describe('same-input authoritative one-hop relationship graph', () => {
  it('keeps actual incoming/outgoing direction and predicate, never cooccurrence or transitive guesses', () => {
    const x = setup(),
      g = ready(x.graph())
    expect(g.edges.map(({ subject, predicate, object }) => [subject, predicate, object])).toEqual([
      [A, P, B],
      [B, Q, C],
    ])
    expect(g.edges.map((edge) => edge.supports.map((s) => s.id))).toEqual([
      [hash('stable-record-1')],
      [hash('stable-record-2')],
    ])
    expect(g.anchors).toEqual([B, D])
    expect(g.snapshotId).toBe(x.source.inputSnapshotId)
    expect(g.revision).toBe(1)
    const markup = x.markup()
    expect(markup).toContain('aria-label="当前页 IRI 关联"')
    expect(markup).toContain('aria-label="来自同快照事实记录的有向关系"')
    expect(markup).toContain(`data-subject="${A}" data-predicate="${P}" data-object="${B}"`)
    expect(markup).toContain(hash('stable-record-1'))
    expect(markup).not.toContain(`data-subject="${B}" data-predicate="${D}"`)
  })

  it('shows legitimate mapped actual SPO with original identity and drift provenance, not the managed target', () => {
    const x = setup()
    x.page.rows[0].cells[0] = { kind: 'iri', iri: A, n3: `<${A}>` }
    x.source.domain.state.facts = [
      {
        ...fact(1, A, P, `<${C}>`),
        owner: 'mapping-M',
        source_row: 'row-7',
        managed_value: `<${B}>`,
      },
    ]
    x.source.domain.state.mappingState['mapping-M'] = {
      generatedVersion: 1,
      stale: [
        { code: 'MAPPING_INPUT_CHANGED', dependency: 'mapping:mapping-M', before: 1, after: 2 },
      ],
    }
    const g = ready(x.graph())
    expect(g.edges.map(({ subject, predicate, object }) => [subject, predicate, object])).toEqual([
      [A, P, C],
    ])
    expect(g.edges[0].supports[0]).toMatchObject({
      id: hash('stable-record-1'),
      owner: 'mapping-M',
      source_row: 'row-7',
      managed_value: `<${B}>`,
    })
    expect(x.markup()).toContain('当前值与映射生成值不同')
    expect(x.markup()).toContain('MAPPING_INPUT_CHANGED')
    delete x.source.domain.state.mappingState['mapping-M']
    expect(ready(x.graph()).edges).toHaveLength(1)
    expect(x.markup()).toContain('映射来源状态未提供')
  })

  it('merges identical SPO without erasing multiple actual provenance records', () => {
    const x = setup()
    x.source.domain.state.facts.push({
      ...fact(8, A, P, `<${B}>`),
      owner: 'M',
      source_row: 'r',
      managed_value: `<${B}>`,
    })
    expect(ready(x.graph()).edges[0].supports.map((s) => s.id)).toEqual([
      hash('stable-record-1'),
      hash('stable-record-8'),
    ])
    expect(ready(x.graph()).totalEdges).toBe(2)
  })

  it('never turns tombstones, typed literals, metadata, or incomplete mapped provenance into edges', () => {
    const x = setup()
    x.source.domain.state.facts = [
      { ...fact(1, B, P, null), owner: 'M', source_row: 'r', managed_value: `<${C}>` },
      fact(2, B, P, `"${C}"^^<urn:test:Datatype>`),
      { ...fact(3, B, P, `<${C}>`), owner: 'M', source_row: null, managed_value: `<${C}>` },
      fact(4, B, P, `<${C}> <${D}>`),
    ]
    expect(ready(x.graph()).edges).toEqual([])
    expect(x.markup()).toContain('不表示该快照不存在关系')
    expect(x.markup()).not.toContain('aria-label="来自同快照事实记录的有向关系"')
  })

  it('requires coherent source project, snapshot, revision, editor and dependency vector bindings', () => {
    for (const field of [
      'project',
      'workspaceProject',
      'snapshot',
      'workspaceSnapshot',
      'revision',
      'workspaceRevision',
      'editor',
      'vector',
    ]) {
      const x = setup()
      if (field === 'project') x.source.projectId = '50000000-0000-4000-8000-000000000001'
      if (field === 'workspaceProject')
        x.source.workspace.projectId = '50000000-0000-4000-8000-000000000001'
      if (field === 'snapshot') x.source.inputSnapshotId = hash('wrong')
      if (field === 'workspaceSnapshot') x.source.workspace.inputSnapshotId = hash('wrong')
      if (field === 'revision') x.source.domain.projectRevision = 2
      if (field === 'workspaceRevision') x.source.workspace.domainRevision = 2
      if (field === 'editor') x.source.workspace.draft.editor = 'another-editor'
      if (field === 'vector') x.source.domain.dependencyVector['facts:asserted'] = 2
      expect(x.graph().state).toBe('unavailable')
      expect(x.markup()).not.toContain('aria-label="来自同快照事实记录的有向关系"')
    }
  })

  it('withholds historical/stale/evicted results even if an offered current source happens to match', () => {
    for (const field of [
      'historical-input',
      'stale',
      'historical',
      'evicted',
      'reason',
      'selection-required',
    ]) {
      const x = setup()
      if (field === 'historical-input') x.descriptor.identity.inputSelection = 'historical'
      if (field === 'stale' || field === 'historical') x.descriptor.metadata.state = field
      if (field === 'evicted') x.descriptor.metadata.payloadStatus = 'evicted'
      if (field === 'reason')
        x.descriptor.metadata.staleReason = [
          { code: 'FACTS_CHANGED', dependency: 'facts:asserted', before: 1, after: 2 },
        ]
      if (field === 'selection-required') x.descriptor.metadata.historicalSelectionRequired = true
      expect(x.graph().state).toBe('unavailable')
    }
  })

  it('requires the selected row in the verified page and exact typed IRI/N3 agreement', () => {
    const x = setup()
    expect(
      buildResultGraph(x.source, x.descriptor, x.page, x.requested, hash('foreign-row')).state,
    ).toBe('unavailable')
    x.page.identity.inputSnapshotId = hash('wrong')
    expect(x.graph().state).toBe('unavailable')
    x.page.identity = structuredClone(x.descriptor.identity)
    x.page.rows[0].cells[0] = {
      kind: 'literal',
      lexical: B,
      n3: `"${B}"`,
      literalType: { kind: 'plain' },
    }
    expect(ready(x.graph()).edges).toEqual([])
    x.page.rows[0].cells[0] = { kind: 'iri', iri: B, n3: `<${C}>` }
    expect(ready(x.graph()).edges).toEqual([])
  })

  it('rejects malformed source and duplicate record identities instead of authenticating ids by SPO hashes', () => {
    const x = setup()
    for (const source of [undefined, null, { ...x.source, extra: true }])
      expect(buildResultGraph(source, x.descriptor, x.page, x.requested, x.rowKey).state).toBe(
        'unavailable',
      )
    x.source.domain.state.facts.push({ ...x.source.domain.state.facts[0], object: `<${C}>` })
    expect(x.graph().state).toBe('unavailable')
  })

  it('bounds anchors and edges with explicit partial counts', () => {
    const x = setup()
    if (x.descriptor.query.kind !== 'SELECT') throw new Error('expected SELECT')
    x.descriptor.query.columns = Array.from({ length: 18 }, (_, index) => ({
      index,
      name: 'column' + index,
    }))
    x.page.rows[0].cells = Array.from({ length: 18 }, (_, index) => ({
      kind: 'iri' as const,
      iri: 'urn:anchor:' + index,
      n3: `<urn:anchor:${index}>`,
    }))
    x.source.domain.state.facts = Array.from({ length: 30 }, (_, index) =>
      fact(index, 'urn:anchor:0', P, `<urn:neighbor:${index}>`),
    )
    const g = ready(x.graph())
    expect(g.anchors).toHaveLength(graphLimits.anchors)
    expect(g.omittedAnchors).toBe(2)
    expect(g.edges).toHaveLength(graphLimits.edges)
    expect(g.totalEdges).toBe(30)
    expect(x.markup()).toContain('24 / 30 条')
    expect(x.markup()).toContain('另有 2 个行内起点未显示')
  })

  it('withholds diagram during loading or a mismatched read failure while keeping the ordinary table', () => {
    const x = setup()
    for (const patch of [{ rowsLoading: true }, { readFailure: { invalid: true } }]) {
      expect(x.markup(patch)).toContain('当前结果页')
      expect(x.markup(patch)).not.toContain('aria-label="来自同快照事实记录的有向关系"')
    }
  })

  it('renders complete edge titles as single-expression SSR text with zero React title errors', () => {
    const x = setup()
    const errors: unknown[][] = []
    const originalError = console.error
    console.error = (...args: unknown[]) => {
      errors.push(args)
    }
    let markup: string
    try {
      markup = x.markup()
    } finally {
      console.error = originalError
    }
    expect(markup).toContain(`<title>${A} → ${P} → ${B}</title>`)
    expect(markup).toContain(`<title>${B} → ${Q} → ${C}</title>`)
    expect(markup).not.toContain('<title></title>')
    expect(errors).toEqual([])
  })

  it('takes mapping state from own properties only so inherited keys never reach the panel', () => {
    const x = setup()
    x.page.rows[0].cells[0] = { kind: 'iri', iri: A, n3: `<${A}>` }
    x.source.domain.state.facts = [
      {
        ...fact(1, A, P, `<${C}>`),
        owner: 'constructor',
        source_row: 'row-1',
        managed_value: `<${B}>`,
      },
      {
        ...fact(2, A, Q, `<${D}>`),
        owner: '__proto__',
        source_row: 'row-2',
        managed_value: `<${E}>`,
      },
    ]
    expect(x.source.domain.state.mappingState).toEqual({})
    expect(validateBusiness3('result_project.read', x.source)).toBe(true)
    const g = ready(x.graph())
    expect(g.edges.map(({ subject, predicate, object }) => [subject, predicate, object])).toEqual([
      [A, P, C],
      [A, Q, D],
    ])
    expect(g.edges.map((edge) => edge.supports.map((s) => s.mappingState))).toEqual([
      [null],
      [null],
    ])
    const markup = x.markup()
    expect(markup).toContain('映射来源状态未提供')
    expect(markup).toContain('当前结果页')
  })

  it('preserves contract-valid own mapping state for reserved names instead of blanket rejection', () => {
    const x = setup()
    x.page.rows[0].cells[0] = { kind: 'iri', iri: A, n3: `<${A}>` }
    x.source.domain.state.facts = [
      {
        ...fact(1, A, P, `<${C}>`),
        owner: 'constructor',
        source_row: 'row-1',
        managed_value: `<${B}>`,
      },
      {
        ...fact(2, A, Q, `<${D}>`),
        owner: '__proto__',
        source_row: 'row-2',
        managed_value: `<${E}>`,
      },
    ]
    // JSON.parse creates own data properties even for '__proto__'; an object literal
    // would set the prototype instead and fake the coverage.
    x.source.domain.state.mappingState = JSON.parse(
      '{"constructor":{"generatedVersion":3,"stale":[]},"__proto__":{"generatedVersion":4,"stale":[]}}',
    )
    expect(validateBusiness3('result_project.read', x.source)).toBe(true)
    const g = ready(x.graph())
    expect(g.edges.map((edge) => edge.supports.map((s) => s.mappingState))).toEqual([
      [{ generatedVersion: 3, stale: [] }],
      [{ generatedVersion: 4, stale: [] }],
    ])
    const markup = x.markup()
    expect(markup).toContain('映射生成版本 3')
    expect(markup).toContain('映射生成版本 4')
    expect(markup).toContain('未标记过期')
  })

  it('counts omitted records uniformly over the whole input regardless of anchors', () => {
    const x = setup()
    x.source.domain.state.facts = [
      fact(1, B, P, `<${C}>`),
      { ...fact(2, B, Q, `<${D}>`), owner: 'M', source_row: null, managed_value: `<${D}>` },
      { ...fact(3, E, P, `<${C}>`), owner: 'M', source_row: null, managed_value: `<${C}>` },
      fact(4, E, Q, `<${C}>`),
      fact(5, E, P, `"plain"^^<urn:test:Datatype>`),
      fact(6, B, P, null),
    ]
    const g = ready(x.graph())
    expect(g.edges.map(({ subject, predicate, object }) => [subject, predicate, object])).toEqual([
      [B, P, C],
    ])
    expect(g.omittedRecords).toBe(3)
    expect(x.markup()).toContain('输入中 3 条')
    expect(x.markup()).not.toContain(`data-subject="${E}"`)
  })
})
