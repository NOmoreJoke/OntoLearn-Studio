import { validateBusiness3 } from '../../../../../../packages/contracts/src/v2'
import type { MainlineProjectReadDTO } from './api002-source-types'
import { iriSchema } from './draft'
import { displayRows, type DisplayDescriptor, type DisplayRowsPage } from './typed-results'
import type { QueryResultPanelProps } from './typed-result-panel-props'

// Presentation limits only; no query, transport, or execution budget is changed.
export const graphLimits = { anchors: 16, edges: 24, visibleSupports: 8 } as const
type Fact = MainlineProjectReadDTO['domain']['state']['facts'][number]
export type GraphSupport = Fact & {
  mappingState: MainlineProjectReadDTO['domain']['state']['mappingState'][string] | null
}
export type GraphEdge = {
  subject: string
  predicate: string
  object: string
  supports: GraphSupport[]
}
export type ResultGraph =
  | { state: 'unavailable'; reason: string }
  | {
      state: 'ready'
      snapshotId: string
      revision: number
      rowIndex: number
      anchors: string[]
      omittedAnchors: number
      edges: GraphEdge[]
      totalEdges: number
      omittedRecords: number
    }
const unavailable = (reason: string): ResultGraph => ({ state: 'unavailable', reason })
const iriObject = (raw: string): string | undefined => {
  if (!raw.startsWith('<') || !raw.endsWith('>')) return undefined
  const iri = raw.slice(1, -1)
  return iriSchema.safeParse(iri).success ? iri : undefined
}

/** One hop around a selected, verified result row. Only actual same-input facts
 * supply SPO edges. Metadata is provenance, never another triple or a target.
 */
export function buildResultGraph(
  source: unknown,
  descriptor: DisplayDescriptor,
  page: DisplayRowsPage,
  requested: NonNullable<QueryResultPanelProps['rows']>['requested'],
  rowKey: string,
): ResultGraph {
  if (
    descriptor.identity.scope !== 'asserted' ||
    descriptor.identity.inputSelection !== 'current' ||
    descriptor.metadata.state !== 'current' ||
    descriptor.metadata.staleReason.length !== 0 ||
    descriptor.metadata.historicalSelectionRequired ||
    descriptor.metadata.payloadStatus !== 'available'
  )
    return unavailable('历史或过期结果尚无对应快照的关系事实来源；不使用当前项目为它补边。')
  if (!validateBusiness3('result_project.read', source))
    return unavailable('尚未取得可核对的项目事实来源；请读取当前项目。')
  const read = source as MainlineProjectReadDTO
  if (
    read.projectId !== descriptor.identity.projectId ||
    read.workspace.projectId !== descriptor.identity.projectId ||
    read.inputSnapshotId !== descriptor.identity.inputSnapshotId ||
    read.workspace.inputSnapshotId !== descriptor.identity.inputSnapshotId ||
    read.domain.projectRevision !== descriptor.identity.inputProjectRevision ||
    read.workspace.domainRevision !== descriptor.identity.inputProjectRevision ||
    read.workspace.draft.editor !== 'query-workspace-v1' ||
    Object.entries(descriptor.metadata.dependencyVector).some(
      ([key, version]) => read.domain.dependencyVector[key] !== version,
    )
  )
    return unavailable('项目事实来源与此结果的项目、快照或版本不一致，未绘制关系。')
  let rows: DisplayRowsPage
  try {
    rows = displayRows(page, descriptor, requested)
  } catch {
    return unavailable('结果页尚未通过身份与分页核对，未绘制关系。')
  }
  const row = rows.rows.find((value) => value.rowKey === rowKey)
  if (!row) return unavailable('所选行不在已核对的当前结果页中，未绘制关系。')
  const candidates = [
    ...new Set(
      row.cells.flatMap((cell) =>
        cell?.kind === 'iri' && cell.n3 === `<${cell.iri}>` && iriSchema.safeParse(cell.iri).success
          ? [cell.iri]
          : [],
      ),
    ),
  ]
  const anchors = candidates.slice(0, graphLimits.anchors)
  const anchorSet = new Set(anchors)
  const facts = read.domain.state.facts
  if (new Set(facts.map((fact) => fact.id)).size !== facts.length)
    return unavailable('事实来源含重复记录身份，未绘制关系。')
  const edges = new Map<string, GraphEdge>()
  let omittedRecords = 0
  for (const fact of facts) {
    if (fact.object === null) continue // Tombstones are provenance, never assertions.
    const object = iriObject(fact.object)
    if (
      !object ||
      !iriSchema.safeParse(fact.subject).success ||
      !iriSchema.safeParse(fact.predicate).success
    ) {
      omittedRecords++
      continue
    }
    if (!anchorSet.has(fact.subject) && !anchorSet.has(object)) continue
    const manual = fact.owner === null && fact.source_row === null && fact.managed_value === null
    const mapped =
      typeof fact.owner === 'string' &&
      fact.owner.length > 0 &&
      typeof fact.source_row === 'string' &&
      fact.source_row.length > 0 &&
      typeof fact.managed_value === 'string' &&
      fact.managed_value.length > 0
    if (!manual && !mapped) {
      omittedRecords++
      continue
    }
    const key = JSON.stringify([fact.subject, fact.predicate, object])
    let edge = edges.get(key)
    if (!edge) {
      edge = { subject: fact.subject, predicate: fact.predicate, object, supports: [] }
      edges.set(key, edge)
    }
    edge.supports.push({
      ...fact,
      mappingState:
        fact.owner === null ? null : (read.domain.state.mappingState[fact.owner] ?? null),
    })
  }
  return {
    state: 'ready',
    snapshotId: read.inputSnapshotId,
    revision: read.domain.projectRevision,
    rowIndex: row.index,
    anchors,
    omittedAnchors: candidates.length - anchors.length,
    edges: [...edges.values()].slice(0, graphLimits.edges),
    totalEdges: edges.size,
    omittedRecords,
  }
}
