import type { SandboxTriple } from './foundation-types'

export type LiveTripleMiniGraphProps = {
  triples: readonly SandboxTriple[]
  onRemoveTriple?(id: string): void
}

type NodePoint = {
  key: string
  label: string
  kind: 'entity' | 'literal'
  derived: boolean
  x: number
  y: number
}

function truncateLabel(text: string, max = 14): string {
  const chars = Array.from(text)
  return chars.length > max ? `${chars.slice(0, max - 1).join('')}…` : text
}

export function LiveTripleMiniGraph({ triples, onRemoveTriple }: LiveTripleMiniGraphProps) {
  const nodesMap = new Map<string, Omit<NodePoint, 'x' | 'y'>>()
  for (const triple of triples) {
    const subjKey = `E:${triple.subjectId}`
    if (!nodesMap.has(subjKey)) {
      nodesMap.set(subjKey, {
        key: subjKey,
        label: triple.subjectLabel,
        kind: 'entity',
        derived: false,
      })
    }
    const objKey =
      triple.objectKind === 'entity'
        ? `E:${triple.objectValue}`
        : `L:${triple.id}:${triple.objectValue}`
    if (!nodesMap.has(objKey)) {
      nodesMap.set(objKey, {
        key: objKey,
        label: triple.objectLabel,
        kind: triple.objectKind,
        derived: Boolean(triple.derived),
      })
    } else if (triple.derived) {
      const prev = nodesMap.get(objKey)!
      nodesMap.set(objKey, { ...prev, derived: true })
    }
  }

  const rawNodes = [...nodesMap.values()]
  const centerX = 280
  const centerY = 185
  const nodes: NodePoint[] = rawNodes.map((node, idx) => {
    if (rawNodes.length === 1) return { ...node, x: centerX, y: centerY }
    if (idx === 0) return { ...node, x: centerX, y: centerY }
    const count = rawNodes.length - 1
    const angle = -Math.PI / 2 + (2 * Math.PI * (idx - 1)) / count
    const rx = count > 5 ? 195 : 175
    const ry = count > 5 ? 132 : 120
    return {
      ...node,
      x: Math.round(centerX + Math.cos(angle) * rx),
      y: Math.round(centerY + Math.sin(angle) * ry),
    }
  })

  const pointByKey = new Map(nodes.map((n) => [n.key, n]))

  return (
    <section
      className="foundation-graph-panel"
      data-testid="live-triple-mini-graph"
      aria-label="实时双色知识图谱"
    >
      <div className="foundation-graph-head">
        <h3>实时双色知识图谱</h3>
        <span className="foundation-count-pill">{triples.length} 条三元组</span>
      </div>

      <div className="foundation-graph-legend" aria-label="节点与连线语义说明">
        <span className="legend-item is-entity">● 圆节点：对象个体（可继续连线）</span>
        <span className="legend-item is-literal">■ 方盒子：文字/数值（到此为止）</span>
        <span className="legend-item is-derived">┄ 虚线：规则自动推导</span>
      </div>

      {triples.length === 0 ? (
        <div className="foundation-graph-empty" data-testid="foundation-graph-empty">
          <p>画布暂无三元组。</p>
          <p>请从左侧点选 Excel 业务行或触发事件重构，生成第一条 S–P–O 事实。</p>
        </div>
      ) : (
        <svg
          className="foundation-graph-svg"
          viewBox="0 0 560 370"
          role="img"
          aria-label="实时三元组知识图谱"
        >
          <title>知味茶饮三元组可视化：圆角节点代表对象个体，直角方框代表文字或数值。</title>
          {triples.map((triple) => {
            const from = pointByKey.get(`E:${triple.subjectId}`)
            const objKey =
              triple.objectKind === 'entity'
                ? `E:${triple.objectValue}`
                : `L:${triple.id}:${triple.objectValue}`
            const to = pointByKey.get(objKey)
            if (!from || !to) return null
            const midX = (from.x + to.x) / 2
            const midY = (from.y + to.y) / 2
            const tipX = from.x + (to.x - from.x) * 0.72
            const tipY = from.y + (to.y - from.y) * 0.72
            const angle = (Math.atan2(to.y - from.y, to.x - from.x) * 180) / Math.PI
            return (
              <g key={triple.id}>
                <title>{`${triple.subjectLabel} —[${triple.predicateLabel}]→ ${triple.objectLabel}`}</title>
                <line
                  className={triple.derived ? 'graph-edge is-derived' : 'graph-edge'}
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  strokeDasharray={triple.derived ? '6 4' : undefined}
                />
                <path
                  className={triple.derived ? 'graph-arrow is-derived' : 'graph-arrow'}
                  d="M -7 -4 L 0 0 L -7 4"
                  transform={`translate(${tipX} ${tipY}) rotate(${angle})`}
                />
                <rect
                  className="graph-edge-pill"
                  x={midX - 42}
                  y={midY - 10}
                  width={84}
                  height={20}
                  rx={10}
                />
                <text className="graph-edge-label" x={midX} y={midY + 4} textAnchor="middle">
                  {truncateLabel(triple.predicateLabel, 8)}
                </text>
              </g>
            )
          })}

          {nodes.map((node) => (
            <g key={node.key} data-node-kind={node.kind}>
              <title>{node.label}</title>
              {node.kind === 'entity' ? (
                <rect
                  className={node.derived ? 'graph-node-entity is-derived' : 'graph-node-entity'}
                  x={node.x - 62}
                  y={node.y - 20}
                  width={124}
                  height={40}
                  rx={20}
                />
              ) : (
                <rect
                  className="graph-node-literal"
                  x={node.x - 56}
                  y={node.y - 18}
                  width={112}
                  height={36}
                  rx={4}
                />
              )}
              <text className="graph-node-text" x={node.x} y={node.y + 4} textAnchor="middle">
                {node.kind === 'entity' ? '● ' : '■ '}
                {truncateLabel(node.label, 12)}
              </text>
            </g>
          ))}
        </svg>
      )}

      {triples.length > 0 && (
        <ul className="foundation-triple-list" aria-label="画布已构建三元组清单">
          {triples.map((triple) => (
            <li key={triple.id} className={triple.derived ? 'is-derived' : undefined}>
              <span className="triple-sentence">
                <strong>{triple.subjectLabel}</strong>
                <span className="triple-pred"> — {triple.predicateLabel} → </span>
                <span
                  className={triple.objectKind === 'entity' ? 'is-entity-tag' : 'is-literal-tag'}
                >
                  {triple.objectKind === 'entity' ? '● ' : '■ '}
                  {triple.objectLabel}
                </span>
                {triple.derived && <span className="triple-derived-badge">规则推导</span>}
              </span>
              {onRemoveTriple && (
                <button
                  type="button"
                  className="triple-remove-btn"
                  onClick={() => onRemoveTriple(triple.id)}
                >
                  移除
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
