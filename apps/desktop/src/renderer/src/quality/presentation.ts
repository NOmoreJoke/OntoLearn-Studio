export type Statement = readonly [subject: string, predicate: string, object: string]

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
