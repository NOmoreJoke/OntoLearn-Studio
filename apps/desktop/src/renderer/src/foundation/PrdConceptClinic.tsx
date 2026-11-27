import { useState } from 'react'
import {
  PRD_ORDER_STORY_SEGMENTS,
  REIFIED_SO101_TRIPLES,
  type PrdSegmentRole,
  type SandboxTriple,
} from './foundation-types'

export type PrdConceptClinicProps = {
  hasProject: boolean
  reified: boolean
  onReifyOrderModel(): void
  onApplyDraftToOntology(triples: readonly SandboxTriple[]): void
}

const ROLE_CSS: Record<PrdSegmentRole, string> = {
  class: 'prd-token is-class',
  objectProperty: 'prd-token is-object',
  dataProperty: 'prd-token is-data',
  rule: 'prd-token is-rule',
}

export function PrdConceptClinic({
  hasProject,
  reified,
  onReifyOrderModel,
  onApplyDraftToOntology,
}: PrdConceptClinicProps) {
  const [selectedSegmentId, setSelectedSegmentId] = useState<string>(
    PRD_ORDER_STORY_SEGMENTS[2]!.id,
  )
  const activeSegment =
    PRD_ORDER_STORY_SEGMENTS.find((s) => s.id === selectedSegmentId) ?? PRD_ORDER_STORY_SEGMENTS[0]!

  return (
    <div className="clinic-grid" data-testid="prd-concept-clinic">
      <section className="clinic-prd-panel" aria-label="PRD 业务原文四色圈词">
        <div className="clinic-panel-head">
          <h3>业务 PRD 原文四色圈词</h3>
          <span>点击下方标注词段，查看它属于哪类本体元素</span>
        </div>

        <div className="clinic-legend" aria-label="四色圈词图例">
          <span className="prd-legend is-class">[实体类] 紫标</span>
          <span className="prd-legend is-object">[对象关系/事件] 蓝标</span>
          <span className="prd-legend is-data">[属性数值] 绿标</span>
          <span className="prd-legend is-rule">[规则推导] 橙标</span>
        </div>

        <div className="clinic-story-box">
          {PRD_ORDER_STORY_SEGMENTS.map((seg, idx) => (
            <span key={seg.id}>
              {idx > 0 && '，'}
              <button
                type="button"
                className={`${ROLE_CSS[seg.role]}${selectedSegmentId === seg.id ? ' is-active' : ''}`}
                data-testid={`clinic-segment-${seg.id}`}
                aria-pressed={selectedSegmentId === seg.id}
                onClick={() => setSelectedSegmentId(seg.id)}
              >
                <span className="prd-role-tag">[{seg.roleLabel}]</span> {seg.text}
              </button>
            </span>
          ))}
          。
        </div>

        <article className="clinic-segment-detail" data-testid="clinic-segment-detail">
          <div className="clinic-detail-head">
            <span className={ROLE_CSS[activeSegment.role]}>{activeSegment.roleLabel}</span>
            <code>{activeSegment.mappedTarget}</code>
          </div>
          <p>{activeSegment.explanation}</p>
        </article>
      </section>

      <section className="clinic-diagnosis-panel" aria-label="坏模型诊所与事件实体化重构">
        <article className="clinic-card is-bad" data-testid="clinic-bad-model">
          <div className="clinic-card-badge is-bad">❌ 常见坏模型：二元直接连线</div>
          <p className="clinic-formula">王敏 #M-018 —[购买了]→ 杨枝甘露</p>
          <ul>
            <li>无法在同一笔购买中挂载“杨枝甘露 + 茉莉奶绿”两杯商品明细；</li>
            <li>实付金额 36.00 元、外卖超时 25 分钟无独立节点可挂，只能错误写到会员或商品上；</li>
            <li>复购多次后，客诉单 #CP-301 无法精确定位究竟针对哪一次下单。</li>
          </ul>
        </article>

        <article
          className={`clinic-card is-good${reified ? ' is-reified' : ''}`}
          data-testid="clinic-reified-model"
        >
          <div className="clinic-card-badge is-good">✅ 标准重构：事件实体化（订单 #SO-101）</div>
          <p className="clinic-formula">
            门店订单 #SO-101 作为中间事件圆节点，同时挂接会员、门店、多杯商品与实付金额
          </p>
          <ul>
            {REIFIED_SO101_TRIPLES.map((t) => (
              <li key={t.id}>
                <code>{t.subjectLabel}</code> — {t.predicateLabel} →{' '}
                <strong>{t.objectLabel}</strong>
              </li>
            ))}
          </ul>

          <div className="clinic-actions">
            <button
              type="button"
              className="sandbox-primary-btn"
              data-testid="clinic-reify-btn"
              onClick={onReifyOrderModel}
            >
              {reified
                ? '✓ 已重构为标准订单实体模型 (#SO-101)'
                : '一键重构为标准订单实体模型 (#SO-101)'}
            </button>

            <button
              type="button"
              className="sandbox-secondary-btn"
              data-testid={
                hasProject ? 'foundation-apply-to-ontology' : 'foundation-create-and-apply'
              }
              disabled={!reified}
              onClick={() => onApplyDraftToOntology(REIFIED_SO101_TRIPLES)}
            >
              {hasProject
                ? '将 #SO-101 重构三元组带入 01 本体构建草稿'
                : '新建茶饮练习项目并带入 01 本体构建草稿'}
            </button>
          </div>
        </article>
      </section>
    </div>
  )
}
