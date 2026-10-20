import policies from '../v2/dependencies.json'
import registry from '../v2/registry.json'
import { validateV2, type DefinitionIdentity, type DependencyPlan } from './v2'

export function deriveDependencies(
  capability: string,
  definitionId: string,
  scope: string,
  definitions: DefinitionIdentity[],
): DependencyPlan {
  const policy = policies.policies[capability as keyof typeof policies.policies]
  if (!policy || !['asserted', 'asserted+derived', 'scenario'].includes(scope))
    throw new Error('INVALID_REQUEST')
  if (definitions.length > 4096 || definitions.some((d) => !validateV2('definitionIdentity', d)))
    throw new Error('INVALID_REQUEST')
  const capabilityEntry = registry.capabilities[capability as keyof typeof registry.capabilities]
  if (!capabilityEntry || !(capabilityEntry.dataScopes as string[]).includes(scope))
    throw new Error('INVALID_REQUEST')
  const byKey = new Map(definitions.map((d) => [`${d.family}:${d.id}`, d]))
  if (byKey.size !== definitions.length) throw new Error('INVALID_REQUEST')
  const sets: Record<string, string[]> = {}
  const selected = new Set<string>(['facts:asserted'])
  for (const family of [
    ...policy.sets,
    ...(scope === 'asserted+derived' ? policy.withDerived : []),
  ]) {
    sets[family] = definitions
      .filter((d) => d.family === family)
      .map((d) => `${family}:${d.id}`)
      .sort()
    sets[family].forEach((key) => selected.add(key))
  }
  if (policy.selectedFamily) selected.add(`${policy.selectedFamily}:${definitionId}`)
  const pending = [...selected].filter((key) => key !== 'facts:asserted')
  const visited = new Set<string>()
  while (pending.length) {
    const key = pending.pop()!
    if (visited.has(key)) continue
    visited.add(key)
    const definition = byKey.get(key)
    if (!definition) throw new Error('INVALID_REQUEST')
    for (const reference of definition.references) {
      selected.add(reference)
      if (selected.size > 4096) throw new Error('INVALID_REQUEST')
      if (reference !== 'facts:asserted' && !visited.has(reference)) pending.push(reference)
    }
  }
  if (selected.size > 4096) throw new Error('INVALID_REQUEST')
  return { keys: [...selected].sort(), sets }
}
