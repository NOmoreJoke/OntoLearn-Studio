import { useState, type ReactNode } from 'react'
import { parsePreparedReport, type PreparedReport } from './report'

export function TransferPanel({
  projection,
  connected,
}: {
  projection?: unknown
  connected?: ReactNode
}) {
  const [include, setInclude] = useState({
    rawSources: false,
    derived: false,
    history: false,
    agentSessions: false,
  })
  let report: PreparedReport | undefined
  let invalid = false
  if (projection !== undefined) {
    try {
      report = parsePreparedReport(projection)
    } catch {
      invalid = true
    }
  }
  if (connected) {
    return (
      <section aria-labelledby="transfer-title">
        <h1 id="transfer-title">导出与迁移</h1>
        {connected}
      </section>
    )
  }
  return (
    <section aria-labelledby="transfer-title">
      <h1 id="transfer-title">导出与迁移</h1>
      <p role="status">准备阶段：正式项目接口尚未接入，当前不能导入或导出项目。</p>
      <p>
        完整包须包括当前断言、来源所有权、定义及必要配置版本。缺少当前断言或来源所有权只能标为模板包。
      </p>
      <p>
        无原始文件仍可恢复当前项目，但不能直接重跑映射；缺少运行输入不代表模板包，仅不承诺重放该运行。
      </p>
      <fieldset>
        <legend>导出范围（待实际项目清单复核）</legend>
        {(
          [
            ['rawSources', '原始数据文件'],
            ['derived', '当前推导结果'],
            ['history', '历史运行输入与结果'],
            ['agentSessions', 'Agent 会话'],
          ] as const
        ).map(([key, label]) => (
          <label key={key}>
            <input
              type="checkbox"
              checked={include[key]}
              onChange={(e) => setInclude({ ...include, [key]: e.currentTarget.checked })}
            />
            {label}
          </label>
        ))}
        <p>API Key、密码、令牌、私有审计及发送授权始终排除。</p>
      </fieldset>
      <dl>
        <dt>恢复当前项目</dt>
        <dd>未验证：等待完整 checkpoint 与原子导入接口。</dd>
        <dt>重跑原始映射</dt>
        <dd>未验证：原始文件与来源关系须完整；缺文件时需重新关联。</dd>
        <dt>重放沙盘</dt>
        <dd>未验证：须核对完整输入、配置、行为/规则版本及真实支持的执行语义。</dd>
      </dl>
      {invalid && <p role="alert">报告投影无效。请重新读取已提交的业务证据；未生成报告。</p>}
      {report && (
        <section aria-label="报告投影预览">
          <h2>{report.title}</h2>
          <p>项目版本：{report.projectRevision}</p>
          <p>这是尚未接线的投影预览。</p>
          <ul>
            {report.goals.map((goal, index) => (
              <li key={index}>{goal}</li>
            ))}
          </ul>
        </section>
      )}
      <button type="button" disabled>
        导出项目（接口未就绪）
      </button>
      <button type="button" disabled>
        导入项目（接口未就绪）
      </button>
    </section>
  )
}
