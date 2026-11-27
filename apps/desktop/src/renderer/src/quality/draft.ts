import type {
  QualityFr505PatternDTO,
  QualityFr505TripleDTO,
  QualityRuleViewDTO,
} from '@ontolearn/contracts'

/** Form serialization only; authoritative definition validation stays in the engine. */
export type Pattern = {
  kind: 'type' | 'property' | 'compare'
  subject: string
  path: string
  value: string
}
export type Template = 'required' | 'datatype' | 'maxCount' | 'allowedValues' | 'numericRange'

export function patternValue(row: Pattern) {
  if (row.kind === 'type') return { kind: 'type' as const, subject: row.subject, class: row.value }
  if (row.kind === 'property')
    return {
      kind: 'property' as const,
      subject: row.subject,
      path: row.path,
      object: row.value,
    }
  return { kind: 'compare' as const, left: row.subject, operator: row.path, right: row.value }
}

export function fromPattern(pattern: QualityFr505PatternDTO): Pattern {
  switch (pattern.kind) {
    case 'type':
      return { kind: 'type', subject: pattern.subject, path: '', value: pattern.class }
    case 'property':
      return {
        kind: 'property',
        subject: pattern.subject,
        path: pattern.path,
        value: pattern.object,
      }
    case 'compare':
      return {
        kind: 'compare',
        subject: pattern.left,
        path: pattern.operator,
        value: pattern.right,
      }
  }
}

export function prepareEditorDraft(input: {
  kind: 'constraint' | 'rule'
  identity: string
  label: string
  revision: string
  enabled: boolean
  targetClass: string
  path: string
  template: Template
  parameter: string
  upper: string
  conditions: Pattern[]
  conclusions: Pattern[]
}): { draft: string; error: string } {
  if (!/^[1-9][0-9]*$/.test(input.revision) || Number(input.revision) > Number.MAX_SAFE_INTEGER)
    return { draft: '', error: '草稿版本须为正整数；正式版本由项目服务复验。' }
  let parameters: object = {}
  if (input.kind === 'constraint') {
    if (input.template === 'datatype') parameters = { datatype: input.parameter }
    if (input.template === 'maxCount') {
      if (!/^[0-9]+$/.test(input.parameter) || Number(input.parameter) > Number.MAX_SAFE_INTEGER)
        return { draft: '', error: '最大数量须为非负整数。' }
      parameters = { maxCount: Number(input.parameter) }
    }
    if (input.template === 'allowedValues')
      parameters = { values: input.parameter.split('\n').filter(Boolean) }
    if (input.template === 'numericRange')
      parameters = { minInclusive: input.parameter || null, maxInclusive: input.upper || null }
  }
  const common = {
    schemaVersion: 1,
    kind: input.kind,
    id: input.identity,
    revision: Number(input.revision),
    label: input.label,
    enabled: input.enabled,
  }
  const payload =
    input.kind === 'constraint'
      ? {
          ...common,
          targetClass: input.targetClass,
          path: input.path,
          template: input.template,
          parameters,
        }
      : {
          ...common,
          conditions: input.conditions.map(patternValue),
          conclusions: input.conclusions.map(patternValue),
        }
  return { draft: JSON.stringify(payload, null, 2), error: '' }
}

const rdfTypePath = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
export type RuleChainSignature = ['type' | 'property', string]
export type RuleChainDependency = { producerRuleId: string; consumerRuleId: string }
export type RuleChainRuleInput = {
  id: string
  enabled: boolean
  conditions: Pattern[]
  conclusions: Pattern[]
}

/** Mirrors quality/planning.py:_signature for the private editor pattern rows.
 *  Blank rows (no class on a type row, no path on a property row) carry no
 *  signature: an untouched editor row must never read or write anything. */
function signatureOf(row: Pattern): RuleChainSignature | null {
  if (row.kind === 'compare') return null
  if (row.kind === 'type') {
    const target = row.value.trim()
    return target ? ['type', target] : null
  }
  const path = row.path.trim()
  if (!path) return null
  if (path === rdfTypePath) {
    const target = row.value.replace(/^</, '').replace(/>$/, '').trim()
    return target ? ['type', target] : null
  }
  return ['property', path]
}

/**
 * Predict which RULE_CHAIN_UNSUPPORTED pairs the engine will report for the
 * draft rule: existing enabled rules (excluding a saved rule the draft would
 * replace) plus the enabled draft itself (self chain). A type read matches any
 * conclusion write; other reads match the exact (kind, target) signature.
 */
export function detectRuleChainDependencies(
  draft: RuleChainRuleInput,
  existing: readonly RuleChainRuleInput[],
): RuleChainDependency[] {
  const reads = draft.conditions
    .map(signatureOf)
    .filter((signature): signature is RuleChainSignature => signature !== null)
  const readsHas = (write: RuleChainSignature) =>
    reads.some(([kind, target]) => kind === write[0] && target === write[1])
  const typeRead = reads.some(([kind]) => kind === 'type')
  const producers = [
    ...existing.filter((rule) => rule.enabled && rule.id !== draft.id),
    ...(draft.enabled ? [draft] : []),
  ]
  const dependencies: RuleChainDependency[] = []
  for (const producer of producers) {
    const writes = producer.conclusions
      .map(signatureOf)
      .filter((signature): signature is RuleChainSignature => signature !== null)
    if (writes.length === 0) continue
    if (typeRead || writes.some((write) => readsHas(write)))
      dependencies.push({ producerRuleId: producer.id, consumerRuleId: draft.id })
  }
  return dependencies
}

const stripAngleBrackets = (term: string) => term.replace(/^</, '').replace(/>$/, '')

function legacyTripleToPattern([subject, predicate, object]: QualityFr505TripleDTO): Pattern {
  if (stripAngleBrackets(predicate) === rdfTypePath)
    return { kind: 'type', subject, path: '', value: stripAngleBrackets(object) }
  return { kind: 'property', subject, path: stripAngleBrackets(predicate), value: object }
}

/**
 * Project a saved rule view into chain-detection input so legacy (imported
 * triple) rules join the live editor warning exactly like FR-505 ones; term
 * normalization stays aligned with quality/planning.py:_signature.
 */
export function ruleViewToChainInput(rule: QualityRuleViewDTO): RuleChainRuleInput {
  if (rule.format === 'fr505')
    return {
      id: rule.id,
      enabled: rule.enabled,
      conditions: rule.conditions.map(fromPattern),
      conclusions: rule.conclusions.map(fromPattern),
    }
  return {
    id: rule.id,
    enabled: rule.enabled,
    conditions: rule.when.map(legacyTripleToPattern),
    conclusions: rule.then ? [legacyTripleToPattern(rule.then)] : [],
  }
}
