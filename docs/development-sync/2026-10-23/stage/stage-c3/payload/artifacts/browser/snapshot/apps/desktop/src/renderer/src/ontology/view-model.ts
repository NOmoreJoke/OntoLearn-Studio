/** T02 presentation projection only. Canonical boundary validation belongs to T00. */
export type ObjectKind = 'class' | 'objectProperty' | 'dataProperty' | 'individual'
export type LocalizedText = readonly [text: string, language: string]
export type ObjectRow = Readonly<{
  iri: string
  kind: ObjectKind
  classType?: 'rdfs' | 'owl'
  identifier: string
  labels: readonly LocalizedText[]
  definitions: readonly LocalizedText[]
  synonyms: readonly string[]
  examples: readonly string[]
  parents: readonly string[]
  domain: readonly string[]
  range: readonly string[]
  types: readonly string[]
}>
export type RdfRow = Readonly<{ subject: string; predicate: string; object: string }>
export type OntologyView = Readonly<{
  project: string
  revision: number
  objects: readonly ObjectRow[]
  triples: readonly RdfRow[]
}>
export type TreeRow = Readonly<{ iri: string; depth: number; repeated: boolean }>

export function classTree(objects: readonly ObjectRow[]): readonly TreeRow[] {
  const classes = objects.filter((row) => row.kind === 'class')
  const byId = new Map(classes.map((row) => [row.iri, row]))
  const result: TreeRow[] = []
  const visited = new Set<string>()
  const sorted = (values: readonly ObjectRow[]) =>
    [...values].sort((a, b) => (a.iri < b.iri ? -1 : a.iri > b.iri ? 1 : 0))
  const walk = (start: ObjectRow) => {
    const stack = [{ row: start, depth: 0, ancestors: new Set<string>() }]
    while (stack.length) {
      const { row, depth, ancestors } = stack.pop()!
      const repeated = ancestors.has(row.iri) || visited.has(row.iri)
      result.push({ iri: row.iri, depth, repeated })
      if (repeated) continue
      visited.add(row.iri)
      const next = new Set([...ancestors, row.iri])
      for (const child of sorted(
        classes.filter((item) => item.parents.includes(row.iri)),
      ).reverse())
        stack.push({ row: child, depth: depth + 1, ancestors: next })
    }
  }
  for (const root of sorted(classes.filter((row) => !row.parents.some((id) => byId.has(id)))))
    walk(root)
  // Closed cycles have no root; still display every class with an explicit reference marker.
  for (const row of sorted(classes)) if (!visited.has(row.iri)) walk(row)
  return result
}

export function localGraph(view: OntologyView, focus: string, limit = 30) {
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) throw new Error('invalid_limit')
  const all = view.triples
    .filter((row) => row.subject === focus || row.object === `<${focus}>`)
    .sort((a, b) => {
      const x = JSON.stringify([a.subject, a.predicate, a.object])
      const y = JSON.stringify([b.subject, b.predicate, b.object])
      return x < y ? -1 : x > y ? 1 : 0
    })
  const edges = all.slice(0, limit)
  const ids = new Set([focus])
  for (const edge of edges) {
    ids.add(edge.subject)
    if (edge.object.startsWith('<')) ids.add(edge.object.slice(1, -1))
  }
  return { nodes: [...ids].sort(), edges, total: all.length, truncated: all.length > edges.length }
}

export const kindLabels: Record<ObjectKind, string> = {
  class: '类',
  objectProperty: '对象属性',
  dataProperty: '数据属性',
  individual: '个体',
}
export function identity(view: Pick<OntologyView, 'project' | 'revision'>): string {
  return JSON.stringify([view.project, view.revision])
}

/** A late/old project preview never enables a current-project confirmation. */
export function isCurrentPreview(
  view: Pick<OntologyView, 'project' | 'revision'>,
  preview: { project: string; revision: number },
): boolean {
  return identity(view) === identity(preview)
}

export function labelOf(row: ObjectRow): string {
  return (
    row.labels.find(([, language]) => language === 'zh')?.[0] ??
    row.labels[0]?.[0] ??
    row.identifier
  )
}
export function definitionOf(row: ObjectRow): string {
  return (
    row.definitions.find(([, language]) => language === 'zh')?.[0] ?? row.definitions[0]?.[0] ?? ''
  )
}
