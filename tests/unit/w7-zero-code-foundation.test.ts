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
