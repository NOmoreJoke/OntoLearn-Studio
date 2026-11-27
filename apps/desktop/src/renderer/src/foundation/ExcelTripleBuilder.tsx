import { useState } from 'react'
import {
  RETAIL_MICRO_10_ROWS,
  RETAIL_NS,
  RETAIL_SOURCE_TABLES,
  RETAIL_VOCABULARY,
  type FoundationMicroStepId,
  type RetailSourceTableId,
  type RetailTableRow,
} from '../learning/scenarios/retail-membership-orders'
import { DERIVED_CHURN_TRIPLE, type SandboxTriple } from './foundation-types'

export type ExcelTripleBuilderProps = {
  activeStep: FoundationMicroStepId
  defaultTable: RetailSourceTableId
  onAddTriple(triple: SandboxTriple): void
}

const SUBJECT_OPTIONS = RETAIL_VOCABULARY.filter((v) => v.kind === 'individual')
const PREDICATE_OPTIONS = [
  ...RETAIL_VOCABULARY.filter((v) => v.kind === 'objectProperty' || v.kind === 'dataProperty'),
  {
    iri: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    compactIri: 'rdf:type',
    zhLabel: '属于类型（类模具）',
    kind: 'objectProperty' as const,
    plainHint: '声明一个具体个体属于哪个业务类（如 BlackGoldMember）。',
  },
]
const OBJECT_ENTITY_OPTIONS = RETAIL_VOCABULARY.filter(
  (v) => v.kind === 'individual' || v.kind === 'class',
)

function stripPrefix(iri: string): string {
  return iri.startsWith(RETAIL_NS) ? iri.slice(RETAIL_NS.length) : iri
}

export function ExcelTripleBuilder({
  activeStep,
  defaultTable,
  onAddTriple,
}: ExcelTripleBuilderProps) {
  const [selectedTable, setSelectedTable] = useState<RetailSourceTableId>(defaultTable)
  const [selectedRowId, setSelectedRowId] = useState<string>('SO-101')
  const [subjectIri, setSubjectIri] = useState<string>(`${RETAIL_NS}order/SO-101`)
  const [predicateIri, setPredicateIri] = useState<string>(`${RETAIL_NS}paidAmount`)
  const [objectKindChoice, setObjectKindChoice] = useState<'entity' | 'literal'>('literal')
  const [objectEntityIri, setObjectEntityIri] = useState<string>(`${RETAIL_NS}store/S-01`)
  const [literalInput, setLiteralInput] = useState<string>('36.00')
  const [feedback, setFeedback] = useState<{ tone: 'ok' | 'error'; text: string }>()

  const tableMeta =
    RETAIL_SOURCE_TABLES.find((t) => t.id === selectedTable) ?? RETAIL_SOURCE_TABLES[0]!
  const rows = RETAIL_MICRO_10_ROWS.filter((r) => r.table === selectedTable)
  const selectedRow = RETAIL_MICRO_10_ROWS.find((r) => r.rowId === selectedRowId)

  const selectedPred =
    PREDICATE_OPTIONS.find((p) => p.iri === predicateIri) ?? PREDICATE_OPTIONS[0]!
  const selectedSubj = SUBJECT_OPTIONS.find((s) => s.iri === subjectIri) ?? SUBJECT_OPTIONS[0]!
  const selectedObjEntity =
    OBJECT_ENTITY_OPTIONS.find((o) => o.iri === objectEntityIri) ?? OBJECT_ENTITY_OPTIONS[0]!

  function applyRowToBuilder(row: RetailTableRow) {
    setSelectedRowId(row.rowId)
    setFeedback(undefined)
    if (row.table === 'members') {
      const mIri = `${RETAIL_NS}member/${row.rowId}`
      if (SUBJECT_OPTIONS.some((s) => s.iri === mIri)) setSubjectIri(mIri)
      if (activeStep === 'step-04') {
        setPredicateIri('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
        setObjectKindChoice('entity')
        setObjectEntityIri(
          row.cells.tier === '黑金会员'
            ? `${RETAIL_NS}BlackGoldMember`
            : `${RETAIL_NS}RegularMember`,
        )
      } else {
        setPredicateIri(`${RETAIL_NS}displayName`)
        setObjectKindChoice('literal')
        setLiteralInput(String(row.cells.displayName ?? ''))
      }
    } else if (row.table === 'stores_staff') {
      const sIri = `${RETAIL_NS}store/${row.rowId}`
      if (SUBJECT_OPTIONS.some((s) => s.iri === sIri)) setSubjectIri(sIri)
      setPredicateIri(`${RETAIL_NS}managedBy`)
      setObjectKindChoice('entity')
      setObjectEntityIri(`${RETAIL_NS}staff/EMP-07`)
    } else if (row.table === 'orders') {
      const oIri = `${RETAIL_NS}order/${row.rowId}`
      if (SUBJECT_OPTIONS.some((s) => s.iri === oIri)) setSubjectIri(oIri)
      if (activeStep === 'step-03') {
        setPredicateIri(`${RETAIL_NS}orderAtStore`)
        setObjectKindChoice('entity')
        setObjectEntityIri(`${RETAIL_NS}store/S-01`)
      } else {
        setPredicateIri(`${RETAIL_NS}paidAmount`)
        setObjectKindChoice('literal')
        setLiteralInput(String(row.cells.paidAmount ?? '36.00'))
      }
    } else if (row.table === 'complaints') {
      const cIri = `${RETAIL_NS}complaint/${row.rowId}`
      if (SUBJECT_OPTIONS.some((s) => s.iri === cIri)) setSubjectIri(cIri)
      setPredicateIri(`${RETAIL_NS}compensationStatus`)
      setObjectKindChoice('literal')
      setLiteralInput(String(row.cells.compensationStatus ?? '已赔付'))
    }
  }

  function handleBuildTriple() {
    if (selectedPred.kind === 'objectProperty' && objectKindChoice === 'literal') {
      setFeedback({
        tone: 'error',
        text: `校验拦截：「${selectedPred.zhLabel}」属于对象关系，宾语必须是可继续连线的圆节点对象，不能直接填文字/数字。`,
      })
      return
    }
    if (selectedPred.kind === 'dataProperty' && objectKindChoice === 'entity') {
      setFeedback({
        tone: 'error',
        text: `校验拦截：「${selectedPred.zhLabel}」属于数值/文字属性，宾语应填写方盒子字面量（如 36.00 或 "已赔付"）。`,
      })
      return
    }
    if (objectKindChoice === 'literal') {
      const trimmed = literalInput.trim()
      if (!trimmed) {
        setFeedback({ tone: 'error', text: '请填写属性值内容（例如 36.00 或 王敏）。' })
        return
      }
      if (
        'datatype' in selectedPred &&
        selectedPred.datatype === 'decimal' &&
        !/^-?\d+(?:\.\d+)?$/.test(trimmed)
      ) {
        setFeedback({
          tone: 'error',
          text: '实付金额必须为合法数字（例如 36.00），不可填入非数字字符。',
        })
        return
      }
      const rdfObj =
        'datatype' in selectedPred && selectedPred.datatype === 'decimal'
          ? `"${trimmed}"^^<http://www.w3.org/2001/XMLSchema#decimal>`
          : 'datatype' in selectedPred && selectedPred.datatype === 'integer'
            ? `"${trimmed}"^^<http://www.w3.org/2001/XMLSchema#integer>`
            : `"${trimmed.replaceAll('"', '\\"')}"@zh`
      onAddTriple({
        id: `excel-${stripPrefix(subjectIri)}-${stripPrefix(predicateIri)}-${trimmed}`,
        subjectId: stripPrefix(subjectIri),
        subjectLabel: selectedSubj.zhLabel,
        predicateId: stripPrefix(predicateIri),
        predicateLabel: selectedPred.zhLabel,
        objectValue: trimmed,
        objectLabel: trimmed,
        objectKind: 'literal',
        rdfSubject: subjectIri,
        rdfPredicate: predicateIri,
        rdfObject: rdfObj,
      })
      setFeedback({
        tone: 'ok',
        text: `已拆出方盒子属性三元组：${selectedSubj.zhLabel} — ${selectedPred.zhLabel} → ■ ${trimmed}`,
      })
      return
    }

    onAddTriple({
      id: `excel-${stripPrefix(subjectIri)}-${stripPrefix(predicateIri)}-${stripPrefix(objectEntityIri)}`,
      subjectId: stripPrefix(subjectIri),
      subjectLabel: selectedSubj.zhLabel,
      predicateId: stripPrefix(predicateIri),
      predicateLabel: selectedPred.zhLabel,
      objectValue: stripPrefix(objectEntityIri),
      objectLabel: selectedObjEntity.zhLabel,
      objectKind: 'entity',
      rdfSubject: subjectIri,
      rdfPredicate: predicateIri,
      rdfObject: `<${objectEntityIri}>`,
    })
    setFeedback({
      tone: 'ok',
      text: `已拆出圆节点关系三元组：${selectedSubj.zhLabel} — ${selectedPred.zhLabel} → ● ${selectedObjEntity.zhLabel}`,
    })
  }

  return (
    <div className="excel-builder-grid" data-testid="excel-triple-builder">
      <section className="excel-source-panel" aria-label="知味茶饮微缩 Excel 源表">
        <div className="excel-table-tabs" role="tablist" aria-label="切换仿真业务源表">
          {RETAIL_SOURCE_TABLES.map((tbl) => (
            <button
              key={tbl.id}
              type="button"
              role="tab"
              aria-selected={selectedTable === tbl.id}
              data-testid={`sandbox-table-tab-${tbl.id}`}
              onClick={() => setSelectedTable(tbl.id)}
            >
              {tbl.id}
            </button>
          ))}
        </div>
        <div className="excel-table-caption">
          <strong>{tableMeta.title}</strong>
          <small>{tableMeta.subtitle}（点击任意行自动填入右侧积木）</small>
        </div>
        <div className="excel-table-scroll">
          <table>
            <thead>
              <tr>
                {tableMeta.columns.map((col) => (
                  <th key={col.key}>{col.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr
                  key={row.rowId}
                  data-testid={`sandbox-row-${row.rowId}`}
                  className={selectedRowId === row.rowId ? 'is-selected' : undefined}
                  onClick={() => applyRowToBuilder(row)}
                >
                  {tableMeta.columns.map((col, colIndex) => (
                    <td key={col.key}>
                      {colIndex === 0 ? (
                        <button
                          type="button"
                          className="excel-row-pick-btn"
                          data-testid={`sandbox-pick-${row.rowId}`}
                          onClick={(e) => {
                            e.stopPropagation()
                            applyRowToBuilder(row)
                          }}
                        >
                          {String(row.cells[col.key] ?? '—')}
                        </button>
                      ) : (
                        String(row.cells[col.key] ?? '—')
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {(selectedRow?.anomalyTag === 'homonym' || activeStep === 'step-02') && (
          <aside className="sandbox-callout" data-testid="homonym-callout" role="status">
            <strong>同名碰撞对照：为什么“王敏”不能当唯一 ID？</strong>
            <p>
              <code>#M-018</code>（黑金会员·尾号 8818）与 <code>#M-209</code>（普通会员·尾号
              4309）中文显示名都是“王敏”。在本体中，<code>retail:displayName</code>{' '}
              只是方盒子标签，唯一身份由 <code>retail:member/M-018</code> 与{' '}
              <code>retail:member/M-209</code> 稳定承担。
            </p>
          </aside>
        )}

        {selectedRow?.anomalyTag === 'renamed_staff' && (
          <aside className="sandbox-callout" data-testid="renamed-staff-callout" role="status">
            <strong>改名不改号：店长花名从“阿杰”变为“Jie”</strong>
            <p>
              无论花名如何调整，店长 <code>#EMP-07</code> 关联的门店与历史客诉责任链不会断裂。
            </p>
          </aside>
        )}
      </section>

      <section className="excel-slots-panel" aria-label="零代码三元组积木拼接器">
        <h3>S–P–O 三元组积木槽位</h3>
        <p className="slots-hint">{selectedPred.plainHint}</p>

        <div className="sandbox-slot-stack">
          <label>
            1. 主体对象（Subject · 必须是圆节点个体）
            <select
              data-testid="sandbox-subject-select"
              value={subjectIri}
              onChange={(e) => setSubjectIri(e.target.value)}
            >
              {SUBJECT_OPTIONS.map((item) => (
                <option key={item.iri} value={item.iri}>
                  {item.zhLabel} ({item.compactIri})
                </option>
              ))}
            </select>
          </label>

          <label>
            2. 业务关系 / 特征（Predicate）
            <select
              data-testid="sandbox-predicate-select"
              value={predicateIri}
              onChange={(e) => {
                const next = PREDICATE_OPTIONS.find((p) => p.iri === e.target.value)
                setPredicateIri(e.target.value)
                setFeedback(undefined)
                if (next) {
                  setObjectKindChoice(next.kind === 'dataProperty' ? 'literal' : 'entity')
                }
              }}
            >
              {PREDICATE_OPTIONS.map((item) => (
                <option key={item.iri} value={item.iri}>
                  {item.zhLabel} ({item.kind === 'dataProperty' ? '属性→方盒子' : '关系→圆节点'})
                </option>
              ))}
            </select>
          </label>

          <label>
            3. 客体形态（圆节点对象 vs 方盒子数值）
            <select
              data-testid="sandbox-object-kind-select"
              value={objectKindChoice}
              onChange={(e) => {
                setObjectKindChoice(e.target.value as 'entity' | 'literal')
                setFeedback(undefined)
              }}
            >
              <option value="entity">● 业务对象 / 概念类（圆节点）</option>
              <option value="literal">■ 文字或数值字面量（方盒子）</option>
            </select>
          </label>

          {objectKindChoice === 'entity' ? (
            <label>
              4. 选择关联对象（Object）
              <select
                data-testid="sandbox-object-select"
                value={objectEntityIri}
                onChange={(e) => setObjectEntityIri(e.target.value)}
              >
                {OBJECT_ENTITY_OPTIONS.map((item) => (
                  <option key={item.iri} value={item.iri}>
                    {item.zhLabel} ({item.compactIri})
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <label>
              4. 填写文字或数值（Literal）
              <input
                data-testid="sandbox-literal-input"
                value={literalInput}
                onChange={(e) => setLiteralInput(e.target.value)}
                placeholder="例如 36.00 或 王敏"
              />
            </label>
          )}
        </div>

        <div className="sandbox-preview-sentence" data-testid="sandbox-preview-sentence">
          <span>预览句子：</span>
          <strong>
            {selectedSubj.zhLabel} — {selectedPred.zhLabel} →{' '}
            {objectKindChoice === 'entity'
              ? `● ${selectedObjEntity.zhLabel}`
              : `■ ${literalInput || '（待填写）'}`}
          </strong>
        </div>

        <div className="sandbox-actions">
          <button
            type="button"
            className="sandbox-primary-btn"
            data-testid="sandbox-add-triple"
            onClick={handleBuildTriple}
          >
            加入右侧知识图谱
          </button>
          {activeStep === 'step-06' && (
            <button
              type="button"
              className="sandbox-secondary-btn"
              data-testid="sandbox-demo-derive"
              onClick={() => {
                onAddTriple(DERIVED_CHURN_TRIPLE)
                setFeedback({
                  tone: 'ok',
                  text: '规则已触发：华东区黑金会员王敏 #M-018 因超时客诉被自动推导为「高流失风险待挽回会员」（虚线边）。',
                })
              }}
            >
              演练：触发规则推导虚线边
            </button>
          )}
        </div>

        {feedback && (
          <p
            role={feedback.tone === 'error' ? 'alert' : 'status'}
            data-testid={
              feedback.tone === 'error' ? 'sandbox-validation-error' : 'sandbox-validation-ok'
            }
            className={
              feedback.tone === 'error' ? 'sandbox-feedback is-error' : 'sandbox-feedback is-ok'
            }
          >
            {feedback.text}
          </p>
        )}
      </section>
    </div>
  )
}
