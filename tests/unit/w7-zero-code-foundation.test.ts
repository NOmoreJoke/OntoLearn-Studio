import { isValidElement, type ReactElement } from 'react'
import { describe, expect, it, vi } from 'vitest'
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
