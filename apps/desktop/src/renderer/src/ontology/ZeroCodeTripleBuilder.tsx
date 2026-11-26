import { useMemo, useState } from 'react'
import {
  RETAIL_NS,
  RETAIL_VOCABULARY,
  type RetailVocabularyItem,
} from '../learning/scenarios/retail-membership-orders'
import { REIFIED_SO101_TRIPLES, type SandboxTriple } from '../foundation/foundation-types'
import {
  compactIri,
  decodeRdfObjectToZeroCode,
  encodeZeroCodeObject,
  type ZeroCodeObjectMode,
} from './rdf-display-adapter'
import type { OntologyView, RdfRow } from './view-model'

export type ZeroCodeTripleBuilderProps = {
  ontologyView?: OntologyView
  foundationDraftTriples?: readonly SandboxTriple[]
  disabled: boolean
  onPreviewTriple(tuple: RdfRow): void
  onConsumeFoundationDraft?(): void
}

type OptionItem = {
  iri: string
  label: string
  kind: RetailVocabularyItem['kind']
  datatype?: RetailVocabularyItem['datatype']
}

const DEFAULT_RDF_TYPE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'

export function ZeroCodeTripleBuilder({
  ontologyView,
  foundationDraftTriples = [],
  disabled,
  onPreviewTriple,
  onConsumeFoundationDraft,
}: ZeroCodeTripleBuilderProps) {
  const { subjects, predicates, entityTargets } = useMemo(() => {
    const subjMap = new Map<string, OptionItem>()
    const predMap = new Map<string, OptionItem>()
    const entityMap = new Map<string, OptionItem>()

    for (const item of RETAIL_VOCABULARY) {
      const option: OptionItem = {
        iri: item.iri,
        label: `${item.zhLabel} (${item.compactIri})`,
        kind: item.kind,
        datatype: item.datatype,
      }
      if (item.kind === 'individual') {
        subjMap.set(item.iri, option)
        entityMap.set(item.iri, option)
      } else if (item.kind === 'class') {
        entityMap.set(item.iri, option)
      } else {
        predMap.set(item.iri, option)
      }
    }

    predMap.set(DEFAULT_RDF_TYPE, {
      iri: DEFAULT_RDF_TYPE,
      label: '属于类型 (rdf:type)',
      kind: 'objectProperty',
    })

    for (const obj of ontologyView?.objects ?? []) {
      const zh = obj.labels.find(([, lang]) => lang === 'zh')?.[0]
      const title = zh || obj.identifier || compactIri(obj.iri)
      const opt: OptionItem = {
        iri: obj.iri,
        label: `${title} (${compactIri(obj.iri)})`,
        kind: obj.kind,
      }
      if (obj.kind === 'individual') {
        subjMap.set(obj.iri, opt)
        entityMap.set(obj.iri, opt)
      } else if (obj.kind === 'class') {
        entityMap.set(obj.iri, opt)
      } else {
        predMap.set(obj.iri, opt)
      }
    }

    return {
      subjects: [...subjMap.values()],
      predicates: [...predMap.values()],
      entityTargets: [...entityMap.values()],
    }
  }, [ontologyView])

  const initialDraft = foundationDraftTriples[0] ?? REIFIED_SO101_TRIPLES[4]!
  const [subjectIri, setSubjectIri] = useState<string>(initialDraft.rdfSubject)
  const [predicateIri, setPredicateIri] = useState<string>(initialDraft.rdfPredicate)
  const initialDecoded = decodeRdfObjectToZeroCode(initialDraft.rdfObject)
  const [objectMode, setObjectMode] = useState<Exclude<ZeroCodeObjectMode, 'raw'>>(
    initialDecoded.mode === 'raw' ? 'decimal' : initialDecoded.mode,
  )
  const [objectEntityIri, setObjectEntityIri] = useState<string>(
    initialDecoded.mode === 'entity' ? initialDecoded.iri : `${RETAIL_NS}member/M-018`,
  )
  const [literalText, setLiteralText] = useState<string>(
    initialDecoded.mode === 'decimal' ||
      initialDecoded.mode === 'integer' ||
      initialDecoded.mode === 'zhText' ||
      initialDecoded.mode === 'string'
      ? initialDecoded.text
      : '36.00',
  )
  const [booleanVal, setBooleanVal] = useState<boolean>(
    initialDecoded.mode === 'boolean' ? initialDecoded.booleanValue : true,
  )
  const [hint, setHint] = useState<string>('')

  const activeSubject = subjects.find((s) => s.iri === subjectIri) ?? subjects[0]!
  const activePredicate = predicates.find((p) => p.iri === predicateIri) ?? predicates[0]!
  const activeEntityTarget =
    entityTargets.find((e) => e.iri === objectEntityIri) ?? entityTargets[0]!

  function loadDraftChip(draft: SandboxTriple) {
    setSubjectIri(draft.rdfSubject)
    setPredicateIri(draft.rdfPredicate)
    const decoded = decodeRdfObjectToZeroCode(draft.rdfObject)
    if (decoded.mode === 'entity') {
      setObjectMode('entity')
      setObjectEntityIri(decoded.iri)
    } else if (decoded.mode === 'boolean') {
      setObjectMode('boolean')
      setBooleanVal(decoded.booleanValue)
    } else if (decoded.mode !== 'raw') {
      setObjectMode(decoded.mode)
      setLiteralText(decoded.text)
    }
    setHint(
      `已从 00 沙盒草稿载入：${draft.subjectLabel} — ${draft.predicateLabel} → ${draft.objectLabel}`,
    )
  }

  function handlePreview() {
    try {
      const encodedObj = encodeZeroCodeObject(
        objectMode === 'entity'
          ? { mode: 'entity', iri: objectEntityIri }
          : objectMode === 'boolean'
            ? { mode: 'boolean', booleanValue: booleanVal }
            : { mode: objectMode, text: literalText },
      )
      setHint('已编译为标准 RDF 事实并填入下方预览事务，请在差异表核对后提交。')
      onConsumeFoundationDraft?.()
      onPreviewTriple({
        subject: subjectIri,
        predicate: predicateIri,
        object: encodedObj,
      })
    } catch (cause) {
      const code = cause instanceof Error ? cause.message : 'INVALID_INPUT'
      if (code === 'INVALID_ZERO_CODE_DECIMAL') {
        setHint('请输入合法数字（小数），例如 36.00。')
      } else if (code === 'INVALID_ZERO_CODE_INTEGER') {
        setHint('请输入合法整数，例如 25。')
      } else if (code === 'INVALID_ZERO_CODE_IRI') {
        setHint('请选择或输入有效的业务对象标识（如 retail:member/M-018）。')
      } else {
        setHint('请检查当前造句槽位内容后再预览。')
      }
    }
  }

  return (
    <div className="zero-code-builder-card" data-testid="zero-code-triple-builder">
      <div className="zero-code-builder-head">
        <div>
          <span className="zc-badge">零代码辅助轮 · 无需手写 &lt;urn:...&gt;</span>
          <h2>自然语言下拉造句器</h2>
        </div>
        <span className="zc-namespace-pill">业务命名空间：retail: (知味茶饮)</span>
      </div>

      {foundationDraftTriples.length > 0 && (
        <div className="zc-draft-strip" data-testid="foundation-draft-strip">
          <span>来自 00 沙盒的 #SO-101 重构草稿（点击一键填入）：</span>
          <div className="zc-draft-chips">
            {foundationDraftTriples.map((draft) => (
              <button
                key={draft.id}
                type="button"
                className="zc-draft-chip"
                data-testid="foundation-draft-chip"
                disabled={disabled}
                onClick={() => loadDraftChip(draft)}
              >
                {draft.subjectLabel} · {draft.predicateLabel} → {draft.objectLabel}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="zc-slots-grid">
        <div className="zc-slot-field">
          <span className="zc-slot-label">主体业务对象</span>
          <select
            data-testid="zc-subject-select"
            aria-label="零代码主体对象"
            value={subjectIri}
            disabled={disabled}
            onChange={(e) => {
              setSubjectIri(e.target.value)
              setHint('')
            }}
          >
            {subjects.map((item) => (
              <option key={item.iri} value={item.iri}>
                {item.label}
              </option>
            ))}
          </select>
        </div>

        <div className="zc-slot-field">
          <span className="zc-slot-label">业务关系或特征</span>
          <select
            data-testid="zc-predicate-select"
            aria-label="零代码业务关系或特征"
            value={predicateIri}
            disabled={disabled}
            onChange={(e) => {
              const nextIri = e.target.value
              const nextPred = predicates.find((p) => p.iri === nextIri)
              setPredicateIri(nextIri)
              setHint('')
              if (nextPred?.kind === 'dataProperty') {
                setObjectMode(nextPred.datatype ?? 'zhText')
              } else {
                setObjectMode('entity')
              }
            }}
          >
            {predicates.map((item) => (
              <option key={item.iri} value={item.iri}>
                {item.label}
              </option>
            ))}
          </select>
        </div>

        <div className="zc-slot-field">
          <span className="zc-slot-label">值类型</span>
          <select
            data-testid="zc-object-mode-select"
            aria-label="零代码客体值类型"
            value={objectMode}
            disabled={disabled}
            onChange={(e) => {
              setObjectMode(e.target.value as Exclude<ZeroCodeObjectMode, 'raw'>)
              setHint('')
            }}
          >
            <option value="entity">关联对象 / 所属类</option>
            <option value="zhText">中文文本</option>
            <option value="decimal">金额 / 小数 (decimal)</option>
            <option value="integer">数量 / 整数 (integer)</option>
            <option value="boolean">是 / 否 (boolean)</option>
            <option value="string">纯文本 (string)</option>
          </select>
        </div>

        <div className="zc-slot-field">
          <span className="zc-slot-label">目标对象或数值</span>
          {objectMode === 'entity' ? (
            <select
              data-testid="zc-object-entity-select"
              aria-label="零代码目标对象"
              value={objectEntityIri}
              disabled={disabled}
              onChange={(e) => {
                setObjectEntityIri(e.target.value)
                setHint('')
              }}
            >
              {entityTargets.map((item) => (
                <option key={item.iri} value={item.iri}>
                  {item.label}
                </option>
              ))}
            </select>
          ) : objectMode === 'boolean' ? (
            <select
              data-testid="zc-object-boolean-select"
              aria-label="零代码布尔值"
              value={booleanVal ? 'true' : 'false'}
              disabled={disabled}
              onChange={(e) => setBooleanVal(e.target.value === 'true')}
            >
              <option value="true">是 (true)</option>
              <option value="false">否 (false)</option>
            </select>
          ) : (
            <input
              data-testid="zc-object-literal-input"
              aria-label="零代码数值或文本输入"
              value={literalText}
              disabled={disabled}
              onChange={(e) => {
                setLiteralText(e.target.value)
                setHint('')
              }}
              placeholder="输入文本或数值，如 36.00"
            />
          )}
        </div>
      </div>

      <div className="zc-sentence-bar">
        <p data-testid="zc-live-sentence">
          业务语义预览：<strong>{activeSubject.label.split(' (')[0]}</strong> 的{' '}
          <strong>{activePredicate.label.split(' (')[0]}</strong> 设为{' '}
          <strong>
            {objectMode === 'entity'
              ? activeEntityTarget.label.split(' (')[0]
              : objectMode === 'boolean'
                ? booleanVal
                  ? '是 (true)'
                  : '否 (false)'
                : literalText || '（待输入）'}
          </strong>
        </p>
        <button
          type="button"
          className="zc-preview-btn"
          data-testid="zc-preview-add-fact"
          disabled={disabled}
          onClick={handlePreview}
        >
          填入并预览新增事实
        </button>
      </div>

      {hint && (
        <p role="status" className="zc-status-hint" data-testid="zc-status-hint">
          {hint}
        </p>
      )}
    </div>
  )
}
