import type { QualityRuleTestResultDTO } from '@ontolearn/contracts'
import {
  RETAIL_NS,
  summarizeRetailDataset,
  type RetailDatasetScale,
} from '../learning/scenarios/retail-membership-orders'
import { compactIri, formatObjectForDisplay } from '../ontology/rdf-display-adapter'

export type RetailSimulationBannerProps = {
  scale: RetailDatasetScale
  disabled: boolean
  running: boolean
  result: QualityRuleTestResultDTO | null | undefined
  onSelectScale(scale: RetailDatasetScale): void
  onRunSimulation(scale: RetailDatasetScale): void
}

function formatSubjectName(iri: string): string {
  const short = compactIri(iri)
  if (iri === `${RETAIL_NS}member/M-018`) return '王敏 #M-018 (黑金会员)'
  if (iri === `${RETAIL_NS}member/M-031`) return '陈晨 #M-031 (黑金会员)'
  if (iri === `${RETAIL_NS}member/M-042`) return '林悦 #M-042 (黑金会员)'
  if (iri === `${RETAIL_NS}member/M-056`) return '周航 #M-056 (黑金会员)'
  return short
}

export function RetailSimulationBanner({
  scale,
  disabled,
  running,
  result,
  onSelectScale,
  onRunSimulation,
}: RetailSimulationBannerProps) {
  const summary = summarizeRetailDataset(scale)
  const derivedCount = result?.valid
    ? result.actualOutputs.length
    : scale === 'micro10'
      ? 2
      : summary.churnTargetCount

  return (
    <section
      className="retail-simulation-banner"
      data-testid="retail-simulation-banner"
      aria-label="知味茶饮双规模仿真体检与推导"
    >
      <div className="retail-sim-head">
        <div>
          <span className="retail-sim-badge">Lv.1 知味茶饮 · 零代码仿真验收台</span>
          <h3>
            {scale === 'micro10'
              ? '微缩沙盒集（10 行精选流水）'
              : '压力仿真集（80 行含脏数据流水）'}
          </h3>
        </div>
        <div className="retail-scale-toggle" role="group" aria-label="仿真数据集规模切换">
          <button
            type="button"
            data-testid="retail-scale-micro10"
            aria-pressed={scale === 'micro10'}
            disabled={disabled || running}
            onClick={() => onSelectScale('micro10')}
          >
            微缩沙盒 10行
          </button>
          <button
            type="button"
            data-testid="retail-scale-stress80"
            aria-pressed={scale === 'stress80'}
            disabled={disabled || running}
            onClick={() => onSelectScale('stress80')}
          >
            压力仿真 80行含脏数据
          </button>
        </div>
      </div>

      <div className="retail-kpi-grid" data-testid="retail-anomaly-summary">
        <article className="retail-kpi-card is-warn">
          <span className="kpi-label">必填缺失拦截（SHACL）</span>
          <strong>{summary.missingStoreCount} 笔订单缺门店</strong>
          <small>
            {summary.missingStoreCount > 0
              ? `订单 ${summary.missingStoreIds.join('、')} 缺失 storeId`
              : '微缩集已补齐门店'}
          </small>
        </article>
        <article className="retail-kpi-card is-danger">
          <span className="kpi-label">数值越界拦截（SHACL）</span>
          <strong>{summary.negativeAmountCount} 笔实付金额为负</strong>
          <small>
            {summary.negativeAmountCount > 0
              ? `订单 ${summary.negativeAmountIds.join('、')} 违反 >= 0`
              : '微缩集金额均 >= 0'}
          </small>
        </article>
        <article className="retail-kpi-card is-warn">
          <span className="kpi-label">悬空引用检测</span>
          <strong>{summary.danglingManagerCount} 家门店悬空店长</strong>
          <small>
            {summary.danglingManagerCount > 0
              ? `门店 ${summary.danglingManagerStoreIds.join('、')} 指向未登记 #EMP-999`
              : '微缩集店长全关联'}
          </small>
        </article>
        <article className="retail-kpi-card is-accent">
          <span className="kpi-label">规则自动推导名单</span>
          <strong>{derivedCount} 名高流失风险待挽回会员</strong>
          <small>黑金会员 + 华东门店 + 关联超时客诉</small>
        </article>
      </div>

      <div className="retail-sim-actions">
        <button
          type="button"
          className="retail-run-btn"
          data-testid="retail-run-simulation"
          disabled={disabled || running}
          onClick={() => onRunSimulation(scale)}
        >
          {running ? '正在执行真实引擎推导…' : '一键运行茶饮仿真体检与推导'}
        </button>
        <span className="retail-sim-note">
          通过真实引擎只读样本评估执行：零破坏当前正式项目，输出结构化证据链。
        </span>
      </div>

      {result && (
        <div className="retail-evidence-panel" data-testid="retail-evidence-chains">
          <div className="retail-evidence-verdict">
            <strong>
              引擎实测结论：{result.valid ? '结构有效' : '存在校验错误'} ·{' '}
              {result.matchesExpected ? '预期一致' : '与预期存在差异'}
            </strong>
            <span>
              规则推导 {result.actualOutputs.length} 条 · RDFS 继承推导 {result.rdfsOutputs.length}{' '}
              条
            </span>
          </div>
          {result.ruleTraces.length > 0 && (
            <ul className="retail-trace-cards" aria-label="白话推导证据链">
              {result.ruleTraces.map((trace, idx) => (
                <li key={idx} className="retail-trace-card">
                  <div className="trace-card-head">
                    <span className="trace-rule-pill">{trace.rule ?? '业务规则'}</span>
                    <strong>
                      结论：
                      {trace.output
                        ? `${formatSubjectName(trace.output[0])} → 归入「高流失风险待挽回会员」`
                        : '推导完成'}
                    </strong>
                  </div>
                  <p className="trace-premises">
                    白话前提链：
                    {trace.inputs
                      .map(
                        ([s, p, o]) =>
                          `${formatSubjectName(s)} 的 ${compactIri(p)} = ${formatObjectForDisplay(o)}`,
                      )
                      .join(' 且 ')}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  )
}
