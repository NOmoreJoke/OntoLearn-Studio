import {
  RETAIL_NS,
  RETAIL_VOCABULARY,
  type RetailVocabularyItem,
} from '../learning/scenarios/retail-membership-orders'
import type { OntologyView } from './view-model'

export const DEFAULT_PREFIXES: Readonly<Record<string, string>> = {
  'retail:': RETAIL_NS,
  'learning:': 'urn:ontolearn:learning:',
  'rdf:': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
  'rdfs:': 'http://www.w3.org/2000/01/rdf-schema#',
  'owl:': 'http://www.w3.org/2002/07/owl#',
  'xsd:': 'http://www.w3.org/2001/XMLSchema#',
}

const XSD_NS = 'http://www.w3.org/2001/XMLSchema#'
const DECIMAL_DATATYPE = `${XSD_NS}decimal`
const INTEGER_DATATYPE = `${XSD_NS}integer`
const BOOLEAN_DATATYPE = `${XSD_NS}boolean`

export type ZeroCodeObjectMode =
  'entity' | 'zhText' | 'string' | 'decimal' | 'integer' | 'boolean' | 'raw'

export type ZeroCodeObjectInput =
  | { mode: 'entity'; iri: string }
  | { mode: 'zhText'; text: string }
  | { mode: 'string'; text: string }
  | { mode: 'decimal'; text: string }
  | { mode: 'integer'; text: string }
  | { mode: 'boolean'; booleanValue: boolean }
  | { mode: 'raw'; rawValue: string }

export type ZeroCodeObjectValue = ZeroCodeObjectInput

export type ReadableDiffSummaryRow = {
  action: '新增' | '修改' | '移除'
  resourceLabel: string
  businessFactSummary: string
  impactNote: string
}

const IRI_SCHEME_RE = /^[A-Za-z][A-Za-z0-9+.-]*:\S+$/

function hasInvalidScalarChars(text: string): boolean {
  for (const ch of text) {
    const code = ch.codePointAt(0)!
    if (code === 0 || (code >= 0xd800 && code <= 0xdfff) || code === 0xfffe || code === 0xffff) {
      return true
    }
  }
  return false
}

export function isValidIri(iri: string): boolean {
  if (!iri || hasInvalidScalarChars(iri)) return false
  if (!IRI_SCHEME_RE.test(iri)) return false
  for (const ch of iri) {
    const code = ch.codePointAt(0)!
    if (code <= 0x20 || (code >= 0x7f && code <= 0x9f)) return false
    if ('<>"{}|^`\\'.includes(ch)) return false
  }
  return true
}

export function compactIri(
  iri: string,
  prefixes: Readonly<Record<string, string>> = DEFAULT_PREFIXES,
): string {
  for (const prefix of Object.keys(prefixes)) {
    if (iri.startsWith(prefix)) return iri
  }
  let bestPrefix = ''
  let bestNs = ''
  for (const [prefix, ns] of Object.entries(prefixes)) {
    if (iri.startsWith(ns) && ns.length > bestNs.length) {
      bestPrefix = prefix
      bestNs = ns
    }
  }
  return bestPrefix ? `${bestPrefix}${iri.slice(bestNs.length)}` : iri
}

export function expandCompactIri(
  value: string,
  prefixes: Readonly<Record<string, string>> = DEFAULT_PREFIXES,
): string {
  for (const [prefix, ns] of Object.entries(prefixes)) {
    if (value.startsWith(prefix)) {
      return `${ns}${value.slice(prefix.length)}`
    }
  }
  return value
}

function escapeLiteralBody(text: string): string {
  if (hasInvalidScalarChars(text)) {
    throw new Error('UNREPRESENTABLE_ZERO_CODE_LITERAL')
  }
  return text
    .replaceAll('\\', '\\\\')
    .replaceAll('"', '\\"')
    .replaceAll('\n', '\\n')
    .replaceAll('\r', '\\r')
    .replaceAll('\t', '\\t')
}

function unescapeLiteralBody(body: string): string | null {
  let out = ''
  for (let i = 0; i < body.length; i += 1) {
    const ch = body[i]!
    if (ch === '"' || ch === '\n' || ch === '\r' || ch === '\t') return null
    if (ch !== '\\') {
      out += ch
      continue
    }
    const next = body[i + 1]
    if (next === undefined) return null
    if (next === '\\') out += '\\'
    else if (next === '"') out += '"'
    else if (next === 'n') out += '\n'
    else if (next === 'r') out += '\r'
    else if (next === 't') out += '\t'
    else return null
    i += 1
  }
  return hasInvalidScalarChars(out) ? null : out
}

export function encodeZeroCodeObject(
  input: ZeroCodeObjectInput,
  prefixes: Readonly<Record<string, string>> = DEFAULT_PREFIXES,
): string {
  switch (input.mode) {
    case 'entity': {
      const expanded = expandCompactIri(input.iri.trim(), prefixes)
      if (!isValidIri(expanded)) throw new Error('INVALID_ZERO_CODE_IRI')
      return `<${expanded}>`
    }
    case 'zhText':
      return `"${escapeLiteralBody(input.text)}"@zh`
    case 'string':
      return `"${escapeLiteralBody(input.text)}"`
    case 'decimal': {
      const normalized = input.text.trim()
      if (!/^-?\d+(?:\.\d+)?$/.test(normalized)) {
        throw new Error('INVALID_ZERO_CODE_DECIMAL')
      }
      return `"${normalized}"^^<${DECIMAL_DATATYPE}>`
    }
    case 'integer': {
      const normalized = input.text.trim()
      if (!/^-?\d+$/.test(normalized)) {
        throw new Error('INVALID_ZERO_CODE_INTEGER')
      }
      return `"${normalized}"^^<${INTEGER_DATATYPE}>`
    }
    case 'boolean':
      return `"${input.booleanValue ? 'true' : 'false'}"^^<${BOOLEAN_DATATYPE}>`
    case 'raw': {
      if (!input.rawValue.trim() || hasInvalidScalarChars(input.rawValue)) {
        throw new Error('INVALID_ZERO_CODE_RAW')
      }
      return input.rawValue
    }
  }
}

export function decodeRdfObjectToZeroCode(n3Object: string): ZeroCodeObjectValue {
  if (n3Object.startsWith('<') && n3Object.endsWith('>')) {
    const iri = n3Object.slice(1, -1)
    if (isValidIri(iri)) return { mode: 'entity', iri }
    return { mode: 'raw', rawValue: n3Object }
  }

  const decimalSuffix = `"^^<${DECIMAL_DATATYPE}>`
  if (n3Object.startsWith('"') && n3Object.endsWith(decimalSuffix)) {
    const inner = n3Object.slice(1, -decimalSuffix.length)
    if (/^-?\d+(?:\.\d+)?$/.test(inner)) return { mode: 'decimal', text: inner }
    return { mode: 'raw', rawValue: n3Object }
  }

  const integerSuffix = `"^^<${INTEGER_DATATYPE}>`
  if (n3Object.startsWith('"') && n3Object.endsWith(integerSuffix)) {
    const inner = n3Object.slice(1, -integerSuffix.length)
    if (/^-?\d+$/.test(inner)) return { mode: 'integer', text: inner }
    return { mode: 'raw', rawValue: n3Object }
  }

  const booleanSuffix = `"^^<${BOOLEAN_DATATYPE}>`
  if (n3Object.startsWith('"') && n3Object.endsWith(booleanSuffix)) {
    const inner = n3Object.slice(1, -booleanSuffix.length)
    if (inner === 'true' || inner === 'false') {
      return { mode: 'boolean', booleanValue: inner === 'true' }
    }
    return { mode: 'raw', rawValue: n3Object }
  }

  if (n3Object.startsWith('"') && n3Object.endsWith('"@zh') && !n3Object.startsWith('"""')) {
    const decoded = unescapeLiteralBody(n3Object.slice(1, -4))
    if (decoded !== null) return { mode: 'zhText', text: decoded }
    return { mode: 'raw', rawValue: n3Object }
  }

  if (
    n3Object.startsWith('"') &&
    n3Object.endsWith('"') &&
    n3Object.length >= 2 &&
    !n3Object.startsWith('"""')
  ) {
    const decoded = unescapeLiteralBody(n3Object.slice(1, -1))
    if (decoded !== null) return { mode: 'string', text: decoded }
    return { mode: 'raw', rawValue: n3Object }
  }

  return { mode: 'raw', rawValue: n3Object }
}

const VOCAB_BY_IRI = new Map<string, RetailVocabularyItem>(
  RETAIL_VOCABULARY.map((item) => [item.iri, item]),
)

const WELL_KNOWN_LABELS: Readonly<Record<string, string>> = {
  'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': '属于类型',
  'http://www.w3.org/2000/01/rdf-schema#label': '中文/英文名称',
  'http://www.w3.org/2000/01/rdf-schema#comment': '业务定义说明',
  'http://www.w3.org/2000/01/rdf-schema#subClassOf': '上级概念类',
  'http://www.w3.org/2000/01/rdf-schema#domain': '适用主体类',
  'http://www.w3.org/2000/01/rdf-schema#range': '客体类或数值类型',
  'http://www.w3.org/2002/07/owl#Class': '本体概念类',
  'http://www.w3.org/2000/01/rdf-schema#Class': '本体概念类',
  'http://www.w3.org/2002/07/owl#ObjectProperty': '对象关系属性',
  'http://www.w3.org/2002/07/owl#DatatypeProperty': '数值/文字属性',
}

export function labelForIri(iri: string, ontologyView?: OntologyView): string {
  const fromProject = ontologyView?.objects.find((obj) => obj.iri === iri)
  if (fromProject) {
    const zh = fromProject.labels.find(([, lang]) => lang === 'zh')?.[0]
    if (zh) return `${zh} (${compactIri(iri)})`
    if (fromProject.identifier) return `${fromProject.identifier} (${compactIri(iri)})`
  }
  const fromVocab = VOCAB_BY_IRI.get(iri)
  if (fromVocab) return `${fromVocab.zhLabel} (${fromVocab.compactIri})`
  const known = WELL_KNOWN_LABELS[iri]
  if (known) return known
  return compactIri(iri)
}

export function formatObjectForDisplay(n3Object: string, ontologyView?: OntologyView): string {
  const decoded = decodeRdfObjectToZeroCode(n3Object)
  switch (decoded.mode) {
    case 'entity':
      return labelForIri(decoded.iri, ontologyView)
    case 'zhText':
      return `「${decoded.text}」`
    case 'string':
      return `「${decoded.text}」`
    case 'decimal':
    case 'integer':
      return decoded.text
    case 'boolean':
      return decoded.booleanValue ? '是 (true)' : '否 (false)'
    case 'raw':
      return decoded.rawValue
  }
}

type DiffTuplePayload = {
  subject?: unknown
  predicate?: unknown
  object?: unknown
  id?: unknown
  layer?: unknown
  payload?: unknown
}

function asDiffPayload(value: unknown): DiffTuplePayload | null {
  return value && typeof value === 'object' ? (value as DiffTuplePayload) : null
}

function summarizeDefinitionPayload(
  payloadText: unknown,
  ontologyView?: OntologyView,
): string | null {
  if (typeof payloadText !== 'string') return null
  try {
    const parsed = JSON.parse(payloadText) as {
      entityMetadata?: {
        entities?: Record<string, { identifier?: string; labels?: [string, string][] }>
      }
      triples?: Array<{ subject?: string; predicate?: string; object?: string }>
    }
    const entities = parsed.entityMetadata?.entities
    if (entities && Object.keys(entities).length > 0) {
      const entries = Object.entries(entities).map(([iri, meta]) => {
        const zh = meta.labels?.find(([, lang]) => lang === 'zh')?.[0]
        return zh ? `${zh} (${compactIri(iri)})` : `${meta.identifier || compactIri(iri)}`
      })
      return `概念定义：${entries.join('、')}`
    }
    if (Array.isArray(parsed.triples) && parsed.triples.length > 0) {
      const first = parsed.triples[0]!
      if (first.subject && first.predicate && first.object) {
        return `${labelForIri(first.subject, ontologyView)} 的 ${labelForIri(first.predicate, ontologyView)} 设为 ${formatObjectForDisplay(first.object, ontologyView)}`
      }
    }
  } catch {
    return null
  }
  return null
}

export function summarizePreparedDiffRows(
  rows: readonly unknown[],
  ontologyView?: OntologyView,
): ReadableDiffSummaryRow[] {
  return rows.map((entry, index) => {
    const item = (entry && typeof entry === 'object' ? entry : {}) as {
      resource?: unknown
      before?: unknown
      after?: unknown
    }
    const res = Array.isArray(item.resource) ? item.resource.map(String) : []
    const beforeObj = asDiffPayload(item.before)
    const afterObj = asDiffPayload(item.after)
    const action: '新增' | '修改' | '移除' =
      beforeObj === null && afterObj !== null
        ? '新增'
        : beforeObj !== null && afterObj === null
          ? '移除'
          : '修改'

    const active = afterObj ?? beforeObj
    const resourceKind = res[0] ?? 'change'
    const resourceId = res[1] ?? res[2] ?? `#${index + 1}`

    if (
      active &&
      typeof active.subject === 'string' &&
      typeof active.predicate === 'string' &&
      typeof active.object === 'string'
    ) {
      const subjLabel = labelForIri(active.subject, ontologyView)
      const predLabel = labelForIri(active.predicate, ontologyView)
      const objLabel = formatObjectForDisplay(active.object, ontologyView)
      const beforeObjLabel =
        beforeObj && typeof beforeObj.object === 'string' && action === '修改'
          ? formatObjectForDisplay(beforeObj.object, ontologyView)
          : null
      return {
        action,
        resourceLabel: `${subjLabel}`,
        businessFactSummary:
          action === '移除'
            ? `移除事实：${subjLabel} 的 ${predLabel}（原值 ${objLabel}）`
            : beforeObjLabel
              ? `${subjLabel} 的 ${predLabel} 从 ${beforeObjLabel} 改为 ${objLabel}`
              : `${subjLabel} 的 ${predLabel} 设为 ${objLabel}`,
        impactNote:
          action === '移除'
            ? '仅撤回该人工断言；受管映射与其它实例不受影响'
            : '写入待确认事务草稿；确认提交后才会更新项目版本与快照',
      }
    }

    const defSummary =
      summarizeDefinitionPayload(afterObj?.payload, ontologyView) ??
      summarizeDefinitionPayload(beforeObj?.payload, ontologyView)
    return {
      action,
      resourceLabel: `${resourceKind}:${compactIri(resourceId)}`,
      businessFactSummary:
        defSummary ?? `${action}结构定义 ${compactIri(res.slice(1).join(' / ') || resourceId)}`,
      impactNote: '结构或元数据定义变更；需人工核对完整差异后正式提交',
    }
  })
}
