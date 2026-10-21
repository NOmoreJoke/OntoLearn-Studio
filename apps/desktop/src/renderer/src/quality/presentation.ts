/** Private display model. T00 must map validated public responses to this model.
 * It is neither an IPC schema nor authority for job/result state.
 */
export type Statement = readonly [subject: string, predicate: string, object: string]
export type TraceNode = {
  id: string
  kind: 'asserted' | 'axiom' | 'rdfs' | 'rule'
  statement: Statement
  inputs: readonly string[]
  ruleId: string | null
}
export type QualityObservation = {
  projectId: string
  inputSnapshotId: string
  inputVersion: number
  constraintVersion: string
  ruleVersion: string
  executionSemanticsVersion: string
  dataScope: string
  includesDerived: boolean
  resultState: 'current' | 'stale' | 'historical'
  staleReasons: readonly string[]
  checks: readonly {
    category: 'parse' | 'shacl' | 'rules' | 'reasoning'
    state: 'passed' | 'failed' | 'unsupported' | 'not-executed'
    detail: string
  }[]
  findings: readonly {
    id: string
    severity: 'repair' | 'improve' | 'knowledge'
    message: string
    target: { kind: 'concept' | 'data' | 'constraint' | 'rule'; id: string }
  }[]
  expected: readonly Statement[]
  actual: readonly Statement[] | null
  difference: {
    added: readonly Statement[]
    withdrawn: readonly Statement[]
    changed: readonly Statement[]
  } | null
  trace: readonly TraceNode[]
}

export function compareStatements(expected: readonly Statement[], actual: readonly Statement[]) {
  const wanted = new Map(expected.map((item) => [JSON.stringify(item), item]))
  const observed = new Map(actual.map((item) => [JSON.stringify(item), item]))
  const sorted = (values: Map<string, Statement>, other: Map<string, Statement>) =>
    [...values.entries()]
      .filter(([key]) => !other.has(key))
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([, statement]) => statement)
  return { missing: sorted(wanted, observed), unexpected: sorted(observed, wanted) }
}

export function visibleObservation(
  observation: QualityObservation | null,
  projectId: string,
): QualityObservation | null {
  return observation?.projectId === projectId ? observation : null
}

export function openWorldText(recordedCount: number | null): string {
  if (recordedCount === null) return '尚未查询记录'
  return recordedCount === 0 ? '未记录' : `已记录 ${recordedCount} 条`
}

export const checkText = {
  passed: '已通过',
  failed: '需要修复',
  unsupported: '不支持',
  'not-executed': '未执行',
} as const
