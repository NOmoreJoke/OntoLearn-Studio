import { isValidElement, type ReactElement } from 'react'
import { describe, expect, it, vi } from 'vitest'

vi.mock('react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react')>()
  return {
    ...actual,
    useState: <T>(initial: T | (() => T)) => [
      typeof initial === 'function' ? (initial as () => T)() : initial,
      vi.fn(),
    ],
    useMemo: <T>(fn: () => T) => fn(),
  }
})
import {
  buildRetailQualitySample,
  FOUNDATION_MICRO_STEPS,
  getRetailRows,
  RETAIL_MICRO_10_ROWS,
  RETAIL_NS,
  RETAIL_STRESS_80_ROWS,
  RETAIL_VOCABULARY,
  summarizeRetailDataset,
} from '../../apps/desktop/src/renderer/src/learning/scenarios/retail-membership-orders'
import { DualTrackRoadmapHeader } from '../../apps/desktop/src/renderer/src/learning/DualTrackRoadmapHeader'
import {
  DERIVED_CHURN_TRIPLE,
  REIFIED_SO101_TRIPLES,
} from '../../apps/desktop/src/renderer/src/foundation/foundation-types'
import { LiveTripleMiniGraph } from '../../apps/desktop/src/renderer/src/foundation/LiveTripleMiniGraph'
import { PrdConceptClinic } from '../../apps/desktop/src/renderer/src/foundation/PrdConceptClinic'
import { SidebarNav } from '../../apps/desktop/src/renderer/src/shell/SidebarNav'
import {
  compactIri,
  decodeRdfObjectToZeroCode,
  encodeZeroCodeObject,
  expandCompactIri,
  summarizePreparedDiffRows,
} from '../../apps/desktop/src/renderer/src/ontology/rdf-display-adapter'
import { ReadableBusinessDiff } from '../../apps/desktop/src/renderer/src/ontology/ReadableBusinessDiff'
import { ZeroCodeTripleBuilder } from '../../apps/desktop/src/renderer/src/ontology/ZeroCodeTripleBuilder'
import { RetailSimulationBanner } from '../../apps/desktop/src/renderer/src/quality/RetailSimulationBanner'
import * as fc from './helpers/fast-check-lite'

function flattenElements(node: unknown): ReactElement<Record<string, unknown>>[] {
  if (Array.isArray(node)) return node.flatMap(flattenElements)
  if (!isValidElement<Record<string, unknown>>(node)) return []
  return [node, ...flattenElements(node.props.children)]
}

describe('W7-1 retail membership & orders simulation datasets', () => {
  it('provides exact deterministic 10-row micro sandbox and 80-row stress datasets without randomness or stale placeholders', () => {
    expect(RETAIL_NS).toBe('urn:ontolearn:retail:')
    expect(RETAIL_MICRO_10_ROWS).toHaveLength(10)
    expect(RETAIL_STRESS_80_ROWS).toHaveLength(80)
    expect(getRetailRows('micro10')).toBe(RETAIL_MICRO_10_ROWS)
    expect(getRetailRows('stress80')).toBe(RETAIL_STRESS_80_ROWS)

    const microSummary = summarizeRetailDataset('micro10')
    expect(microSummary.totalRows).toBe(10)

    const stressSummary = summarizeRetailDataset('stress80')
    expect(stressSummary.totalRows).toBe(80)
    expect(stressSummary.missingStoreCount).toBe(3)
    expect(stressSummary.negativeAmountCount).toBe(2)
    expect(stressSummary.danglingManagerCount).toBe(2)
    expect(stressSummary.churnTargetCount).toBe(4)

    const serialized = JSON.stringify({
      micro: RETAIL_MICRO_10_ROWS,
      stress: RETAIL_STRESS_80_ROWS,
      vocab: RETAIL_VOCABULARY,
      steps: FOUNDATION_MICRO_STEPS,
    })
    expect(serialized).not.toContain('待开发')
    expect(serialized).not.toContain('待实现')
  })

  it('covers homonym Wang Min pair, renamed staff, and #SO-101 multi-cup order in micro10', () => {
    const wangMinRows = RETAIL_MICRO_10_ROWS.filter(
      (r) => r.table === 'members' && r.cells.displayName === '王敏',
    )
    expect(wangMinRows).toHaveLength(2)
    expect(wangMinRows.map((r) => r.rowId)).toEqual(['M-018', 'M-209'])

    const s01 = RETAIL_MICRO_10_ROWS.find((r) => r.rowId === 'S-01')
    expect(s01?.cells.managerId).toBe('#EMP-07')
    expect(s01?.cells.formerName).toBe('阿杰')
    expect(s01?.cells.managerName).toBe('Jie')

    const so101 = RETAIL_MICRO_10_ROWS.find((r) => r.rowId === 'SO-101')
    expect(so101?.cells.paidAmount).toBe(36)
    expect(so101?.cells.overtimeMinutes).toBe(25)
  })

  it('builds valid QualityRuleTestRequestDTO samples for micro10 and stress80', () => {
    const microSample = buildRetailQualitySample('micro10')
    expect(microSample.request.rules).toHaveLength(1)
    expect(microSample.request.expectedOutputs).toHaveLength(2)

    const stressSample = buildRetailQualitySample('stress80')
    expect(stressSample.request.expectedOutputs).toHaveLength(4)
    expect(
      (stressSample.request.ontologyTriples?.length ?? 0) +
        stressSample.request.inputTriples.length,
    ).toBeLessThanOrEqual(72)
    expect(stressSample.anomalySummary.missingStoreCount).toBe(3)
    expect(stressSample.anomalySummary.negativeAmountCount).toBe(2)
    expect(stressSample.anomalySummary.danglingManagerCount).toBe(2)
    expect(stressSample.anomalySummary.churnTargetCount).toBe(4)
  })

  it('renders 6 foundation step cards with w7-foundation-step-card and never learning-path-task', () => {
    const onSelectTrack = vi.fn()
    const onOpenFoundationStep = vi.fn()
    const tree = DualTrackRoadmapHeader({
      selectedTrack: 'retail',
      onSelectTrack,
      onOpenFoundationStep,
    })
    const elements = flattenElements(tree)
    const stepCards = elements.filter((el) => el.props['data-testid'] === 'w7-foundation-step-card')
    expect(stepCards).toHaveLength(6)
    expect(elements.filter((el) => el.props['data-testid'] === 'learning-path-task')).toHaveLength(
      0,
    )

    ;(stepCards[4]!.props.onClick as () => void)()
    expect(onOpenFoundationStep).toHaveBeenCalledWith('step-05')
  })
})

describe('W7-2 00 foundation triple sandbox, graph, clinic, and sidebar entry', () => {
  it('renders empty state and dual-shape entity/literal/derived SVG graph nodes cleanly', () => {
    const emptyTree = flattenElements(LiveTripleMiniGraph({ triples: [] }))
    expect(emptyTree.some((el) => el.props['data-testid'] === 'foundation-graph-empty')).toBe(true)

    const fullTree = flattenElements(
      LiveTripleMiniGraph({
        triples: [...REIFIED_SO101_TRIPLES, DERIVED_CHURN_TRIPLE],
      }),
    )
    const entityNodes = fullTree.filter((el) => el.props['data-node-kind'] === 'entity')
    const literalNodes = fullTree.filter((el) => el.props['data-node-kind'] === 'literal')
    expect(entityNodes.length).toBeGreaterThanOrEqual(5)
    expect(literalNodes).toHaveLength(1)
    expect(fullTree.some((el) => el.type === 'line' && el.props.strokeDasharray === '6 4')).toBe(
      true,
    )
  })

  it('wires PRD concept clinic bad model vs #SO-101 reification and draft apply', () => {
    const onReifyOrderModel = vi.fn()
    const onApplyDraftToOntology = vi.fn()

    const beforeReify = flattenElements(
      PrdConceptClinic({
        hasProject: true,
        reified: false,
        onReifyOrderModel,
        onApplyDraftToOntology,
      }),
    )
    const applyBefore = beforeReify.find(
      (el) => el.props['data-testid'] === 'foundation-apply-to-ontology',
    )
    expect(applyBefore?.props.disabled).toBe(true)
    const reifyBtn = beforeReify.find((el) => el.props['data-testid'] === 'clinic-reify-btn')
    ;(reifyBtn!.props.onClick as () => void)()
    expect(onReifyOrderModel).toHaveBeenCalledOnce()

    const afterReify = flattenElements(
      PrdConceptClinic({
        hasProject: true,
        reified: true,
        onReifyOrderModel,
        onApplyDraftToOntology,
      }),
    )
    const applyAfter = afterReify.find(
      (el) => el.props['data-testid'] === 'foundation-apply-to-ontology',
    )
    expect(applyAfter?.props.disabled).toBe(false)
    ;(applyAfter!.props.onClick as () => void)()
    expect(onApplyDraftToOntology).toHaveBeenCalledWith(REIFIED_SO101_TRIPLES)
  })

  it('exposes permanent nav-step-00 in SidebarNav both with and without an open project', () => {
    const onSelectPrimaryView = vi.fn()
    const noProjectNav = flattenElements(
      SidebarNav({
        primaryView: 'projects',
        hasProject: false,
        workspaceModule: 'query',
        workspaceControlsDisabled: false,
        qualityStepDisabled: false,
        connectionOffline: false,
        mobileOpen: false,
        onCloseMobile: vi.fn(),
        onSelectPrimaryView,
        onSelectStep: vi.fn(),
      }),
    )
    const step00NoProject = noProjectNav.find((el) => el.props['data-testid'] === 'nav-step-00')
    expect(step00NoProject).toBeDefined()
    expect(step00NoProject?.props['aria-disabled']).toBe(false)
    ;(step00NoProject!.props.onClick as (e: { preventDefault(): void }) => void)({
      preventDefault() {},
    })
    expect(onSelectPrimaryView).toHaveBeenCalledWith('foundation')

    const withProjectNav = flattenElements(
      SidebarNav({
        primaryView: 'foundation',
        hasProject: true,
        workspaceModule: 'ontology',
        workspaceControlsDisabled: false,
        qualityStepDisabled: false,
        connectionOffline: false,
        mobileOpen: false,
        onCloseMobile: vi.fn(),
        onSelectPrimaryView,
        onSelectStep: vi.fn(),
      }),
    )
    const step00WithProject = withProjectNav.find((el) => el.props['data-testid'] === 'nav-step-00')
    expect(step00WithProject?.props['aria-current']).toBe('page')
  })
})

describe('W7-3 zero-code adapter, builder, ReadableBusinessDiff, and simulation banner', () => {
  it('compacts and expands known retail/rdf prefixes idempotently', () => {
    expect(compactIri(`${RETAIL_NS}StoreOrder`)).toBe('retail:StoreOrder')
    expect(compactIri('retail:StoreOrder')).toBe('retail:StoreOrder')
    expect(expandCompactIri('retail:StoreOrder')).toBe(`${RETAIL_NS}StoreOrder`)
    expect(expandCompactIri(`${RETAIL_NS}StoreOrder`)).toBe(`${RETAIL_NS}StoreOrder`)
    expect(compactIri('urn:custom:Foo')).toBe('urn:custom:Foo')
  })

  it('encodes and decodes all 6 zero-code object modes and raw passthrough', () => {
    const entityN3 = encodeZeroCodeObject({ mode: 'entity', iri: 'retail:member/M-018' })
    expect(entityN3).toBe(`<${RETAIL_NS}member/M-018>`)
    expect(decodeRdfObjectToZeroCode(entityN3)).toEqual({
      mode: 'entity',
      iri: `${RETAIL_NS}member/M-018`,
    })

    const zhN3 = encodeZeroCodeObject({ mode: 'zhText', text: '王敏"黑金"\n二行' })
    expect(zhN3).toBe('"王敏\\"黑金\\"\\n二行"@zh')
    expect(decodeRdfObjectToZeroCode(zhN3)).toEqual({ mode: 'zhText', text: '王敏"黑金"\n二行' })

    const decN3 = encodeZeroCodeObject({ mode: 'decimal', text: '36.00' })
    expect(decodeRdfObjectToZeroCode(decN3)).toEqual({ mode: 'decimal', text: '36.00' })

    const intN3 = encodeZeroCodeObject({ mode: 'integer', text: '25' })
    expect(decodeRdfObjectToZeroCode(intN3)).toEqual({ mode: 'integer', text: '25' })

    const boolN3 = encodeZeroCodeObject({ mode: 'boolean', booleanValue: false })
    expect(decodeRdfObjectToZeroCode(boolN3)).toEqual({ mode: 'boolean', booleanValue: false })

    expect(decodeRdfObjectToZeroCode('"""multiline"""@en')).toEqual({
      mode: 'raw',
      rawValue: '"""multiline"""@en',
    })
  })

  it('renders ReadableBusinessDiff with 3-column table and single <pre> inside <details>', () => {
    const rows = [
      {
        resource: ['fact', 'f1'],
        before: null,
        after: {
          subject: `${RETAIL_NS}order/SO-101`,
          predicate: `${RETAIL_NS}paidAmount`,
          object: '"36.00"^^<http://www.w3.org/2001/XMLSchema#decimal>',
        },
      },
    ]
    const summaries = summarizePreparedDiffRows(rows)
    expect(summaries).toHaveLength(1)
    expect(summaries[0]!.action).toBe('新增')
    expect(summaries[0]!.businessFactSummary).toContain('36.00')

    const tree = ReadableBusinessDiff({ rows, rawJson: JSON.stringify(rows, null, 2) })
    const elements = flattenElements(tree)
    const pres = elements.filter((el) => el.type === 'pre')
    const details = elements.filter((el) => el.type === 'details')
    expect(pres).toHaveLength(1)
    expect(details).toHaveLength(1)
    const preInsideDetails = flattenElements(details[0]!).filter((el) => el.type === 'pre')
    expect(preInsideDetails).toHaveLength(1)
  })

  it('emits compiled RDF tuple when clicking zc-preview-add-fact in ZeroCodeTripleBuilder', () => {
    const onPreviewTriple = vi.fn()
    const tree = ZeroCodeTripleBuilder({
      foundationDraftTriples: REIFIED_SO101_TRIPLES,
      disabled: false,
      onPreviewTriple,
    })
    const elements = flattenElements(tree)
    const previewBtn = elements.find((el) => el.props['data-testid'] === 'zc-preview-add-fact')
    expect(previewBtn).toBeDefined()
    ;(previewBtn!.props.onClick as () => void)()
    expect(onPreviewTriple).toHaveBeenCalledWith({
      subject: `${RETAIL_NS}order/SO-101`,
      predicate: `${RETAIL_NS}orderedBy`,
      object: `<${RETAIL_NS}member/M-018>`,
    })
  })

  it('renders RetailSimulationBanner 4 anomaly cards and triggers onRunSimulation', () => {
    const onRunSimulation = vi.fn()
    const tree = RetailSimulationBanner({
      scale: 'stress80',
      disabled: false,
      running: false,
      result: null,
      onSelectScale: vi.fn(),
      onRunSimulation,
    })
    const elements = flattenElements(tree)
    expect(elements.some((el) => el.props['data-testid'] === 'retail-anomaly-summary')).toBe(true)
    const runBtn = elements.find((el) => el.props['data-testid'] === 'retail-run-simulation')
    ;(runBtn!.props.onClick as () => void)()
    expect(onRunSimulation).toHaveBeenCalledWith('stress80')
  })
})

describe('W7-4 property-based tests on rdf-display-adapter (300+ runs per property)', () => {
  const iriSegmentArb = fc.unicodeText({
    minLength: 1,
    maxLength: 24,
    pool: [...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-/'],
  })

  const validEntityInputArb = fc.oneof(
    fc.record({
      mode: fc.constantFrom('entity' as const),
      iri: iriSegmentArb,
    }),
  )

  it('satisfies round-trip conservation across all 6 zero-code object modes', () => {
    const anyInputArb = fc.oneof<Parameters<typeof encodeZeroCodeObject>[0]>(
      fc.record({
        mode: fc.constantFrom('entity' as const),
        iri: fc.constantFrom('retail:member/M-018', 'learning:equipment/001', 'urn:test:item/A1'),
      }),
      fc.record({
        mode: fc.constantFrom('zhText' as const),
        text: fc.unicodeText(),
      }),
      fc.record({
        mode: fc.constantFrom('string' as const),
        text: fc.unicodeText(),
      }),
      fc.record({
        mode: fc.constantFrom('decimal' as const),
        text: fc.tuple(fc.integer({ min: -99999, max: 99999 }), fc.integer({ min: 0, max: 99 })),
      }) as unknown as fc.Arbitrary<Parameters<typeof encodeZeroCodeObject>[0]>,
    )
    void validEntityInputArb
    void anyInputArb

    fc.assert(
      fc.property(
        fc.constantFrom('retail:', 'learning:', 'urn:custom:', 'http://example.org/'),
        iriSegmentArb,
        fc.unicodeText(),
        fc.integer({ min: -999999, max: 999999 }),
        fc.integer({ min: 0, max: 99 }),
        fc.boolean(),
        (prefix, seg, text, intPart, fracPart, boolVal) => {
          const iriInput = { mode: 'entity' as const, iri: `${prefix}${seg}` }
          const encodedEntity = encodeZeroCodeObject(iriInput)
          const decodedEntity = decodeRdfObjectToZeroCode(encodedEntity)
          expect(decodedEntity).toEqual({
            mode: 'entity',
            iri: expandCompactIri(`${prefix}${seg}`),
          })

          const zhEncoded = encodeZeroCodeObject({ mode: 'zhText', text })
          expect(zhEncoded.startsWith('"')).toBe(true)
          expect(zhEncoded.endsWith('"@zh')).toBe(true)
          expect(decodeRdfObjectToZeroCode(zhEncoded)).toEqual({ mode: 'zhText', text })

          const strEncoded = encodeZeroCodeObject({ mode: 'string', text })
          expect(strEncoded.startsWith('"')).toBe(true)
          expect(strEncoded.endsWith('"')).toBe(true)
          expect(decodeRdfObjectToZeroCode(strEncoded)).toEqual({ mode: 'string', text })

          const decText = `${intPart}.${String(fracPart).padStart(2, '0')}`
          const decEncoded = encodeZeroCodeObject({ mode: 'decimal', text: decText })
          expect(decodeRdfObjectToZeroCode(decEncoded)).toEqual({
            mode: 'decimal',
            text: decText,
          })

          const intText = String(intPart)
          const intEncoded = encodeZeroCodeObject({ mode: 'integer', text: intText })
          expect(decodeRdfObjectToZeroCode(intEncoded)).toEqual({
            mode: 'integer',
            text: intText,
          })

          const boolEncoded = encodeZeroCodeObject({ mode: 'boolean', booleanValue: boolVal })
          expect(decodeRdfObjectToZeroCode(boolEncoded)).toEqual({
            mode: 'boolean',
            booleanValue: boolVal,
          })
        },
      ),
      { numRuns: 320 },
    )
  })

  it('satisfies idempotency for compactIri and expandCompactIri', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          RETAIL_NS,
          'retail:',
          'urn:ontolearn:learning:',
          'learning:',
          'http://www.w3.org/2001/XMLSchema#',
          'urn:unmatched:',
        ),
        iriSegmentArb,
        (ns, seg) => {
          const raw = `${ns}${seg}`
          const c1 = compactIri(raw)
          const c2 = compactIri(c1)
          expect(c2).toBe(c1)

          const e1 = expandCompactIri(raw)
          const e2 = expandCompactIri(e1)
          expect(e2).toBe(e1)
          expect(expandCompactIri(c1)).toBe(e1)
        },
      ),
      { numRuns: 320 },
    )
  })

  it('rejects malformed decimals, integers, IRIs, and lone surrogates fail-closed', () => {
    for (const badDec of ['', 'abc', '12.34.56', '12元', 'NaN', 'Infinity']) {
      expect(() => encodeZeroCodeObject({ mode: 'decimal', text: badDec })).toThrow(
        'INVALID_ZERO_CODE_DECIMAL',
      )
    }
    for (const badInt of ['', '12.5', 'abc', '1e3']) {
      expect(() => encodeZeroCodeObject({ mode: 'integer', text: badInt })).toThrow(
        'INVALID_ZERO_CODE_INTEGER',
      )
    }
    for (const badIri of ['', 'no-scheme', 'urn:has space', 'urn:bad<angle>']) {
      expect(() => encodeZeroCodeObject({ mode: 'entity', iri: badIri })).toThrow(
        'INVALID_ZERO_CODE_IRI',
      )
    }
    expect(() => encodeZeroCodeObject({ mode: 'zhText', text: 'bad\ud800' })).toThrow(
      'UNREPRESENTABLE_ZERO_CODE_LITERAL',
    )
  })
})
