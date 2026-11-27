import {
  FOUNDATION_MICRO_STEPS,
  RETAIL_SOURCE_TABLES,
  type FoundationMicroStepId,
} from './scenarios/retail-membership-orders'

export type LearningTrackId = 'retail' | 'equipment'

export type DualTrackRoadmapHeaderProps = {
  selectedTrack: LearningTrackId
  onSelectTrack(track: LearningTrackId): void
  onOpenFoundationStep(stepId: FoundationMicroStepId): void
}

export function DualTrackRoadmapHeader({
  selectedTrack,
  onSelectTrack,
  onOpenFoundationStep,
}: DualTrackRoadmapHeaderProps) {
  return (
    <section
      className="w7-dual-track-roadmap"
      data-testid="w7-dual-track-roadmap"
      aria-label="阶梯案例库与底层本体概念路线"
    >
      <div className="w7-track-selector" role="group" aria-label="案例阶梯选择">
        <button
          type="button"
          className="w7-track-card"
          data-testid="learning-track-retail"
          aria-pressed={selectedTrack === 'retail'}
          onClick={() => onSelectTrack('retail')}
        >
          <span className="w7-track-badges">
            <span className="w7-track-pill is-accent">Lv.1 零代码入门推荐</span>
            <span className="w7-track-pill">微观沙盒 10 条 ↔ 压力集 80 条</span>
          </span>
          <strong>知味茶饮 · 全渠道会员与门店订单履约</strong>
          <small>
            面向完全零代码的 BA / PM：从 Excel 拆三元组与 PRD 圈词起步，走通 4 表建模与 80
            行脏数据体检。
          </small>
          <span className="w7-track-tables">
            {RETAIL_SOURCE_TABLES.map((tbl) => (
              <span key={tbl.id} className="w7-table-chip">
                {tbl.id}
              </span>
            ))}
          </span>
        </button>

        <button
          type="button"
          className="w7-track-card"
          data-testid="learning-track-equipment"
          aria-pressed={selectedTrack === 'equipment'}
          onClick={() => onSelectTrack('equipment')}
        >
          <span className="w7-track-badges">
            <span className="w7-track-pill">Lv.2 工程进阶迁移</span>
            <span className="w7-track-pill">9 步标准实操路线</span>
          </span>
          <strong>智能工厂 · 设备运维与告警闭环</strong>
          <small>完整保留工业设备运维知识图谱、SHACL 约束修复、派生查询与独立迁移考核。</small>
        </button>
      </div>

      {selectedTrack === 'retail' && (
        <div className="w7-foundation-steps-panel" data-testid="w7-foundation-steps-panel">
          <div className="w7-foundation-steps-head">
            <h3>Lv.1 底层本体元概念六步阶梯（00 三元组与概念沙盒）</h3>
            <span>无需编程基础 · 点击任意微关卡直达沙盒</span>
          </div>
          <ol className="w7-foundation-steps-grid" aria-label="六步底层概念微关卡">
            {FOUNDATION_MICRO_STEPS.map((step) => (
              <li key={step.id}>
                <button
                  type="button"
                  className="w7-foundation-step-btn"
                  data-testid="w7-foundation-step-card"
                  data-step-id={step.id}
                  onClick={() => onOpenFoundationStep(step.id)}
                >
                  <span className="w7-foundation-step-top">
                    <span className="w7-step-mono">{step.num}</span>
                    <span className="w7-step-mode-badge">
                      {step.recommendedMode === 'clinic' ? 'PRD 坏模型诊所' : 'Excel 拆积木'}
                    </span>
                  </span>
                  <strong>{step.title}</strong>
                  <small>{step.conceptSummary}</small>
                </button>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}
