# T11 比较投影 v3

2026-10-23。此版只约束T11离线审计，不修改T01 Store或T10项目包。替代当前工具接受的v2；旧 [v2规范](selection-comparison-v2.md) 和历史提交保留，核验器拒绝旧格式，不自动升级。

每个投影必须有 `format=t11-comparison-v3`、`comparisonCase=current-state|g6-conflict`、projectId、sourceSnapshotId（SHA256）、非负projectRevision、executionVersions（semantics/engine/lock），以及selection/capabilities/dependencies。每层为唯一稳定 `{id,payload}` 数组，payload须完整非空且不能只是count摘要；事实值、来源、所有权、managed value、冲突及版本由领域adapter保留，T11不猜业务schema。前后完整规范字节内容比较，不按数量比较。

- 当前层：facts、definitions、ownership、mappingState、queries、results字段全必填。通用current-state允许合法空definitions/mappingState/queries/results，但不含当前事实或来源/ownership的包不得restoreCurrent=true；模板仅作为负向check。这保持PRD G.6拒恢复边界，不作F01新模板范围决定。
- G.6人工冲突：六当前层必须全部非空。正式Win→Mac与Mac→Win各自固定g6-conflict；恢复可另按实际冻结场景为current-state或g6-conflict。freeze的recoveryComparisonCase和migrationComparisonCases与投影一致；两迁移槽schema只接受g6-conflict，不能更新两边pin后降级。
- 可选携带层：derivedResults/history/rounds/rawSources/agentSessions/undo。selection分别为currentDerived/historicalRuns/rawSources/agentSessions/priorUndo；未选择的层必须空（historicalRuns控制history和rounds）。priorUndo仅审计选择，不新增产品UI。
- capabilities三项独立。restoreCurrent在成功恢复比较中必为true；rerunOriginalMapping仅在选择原文件、rawSources非空且mappingSources=embedded时true。replaySandbox仅在选择非空history、replayInputs和replayConfiguration齐全、replaySemantics=supported时true；rounds可为零，不能因首轮未提交拒绝完整初始输入重放。不支持/缺失必须false，不静默续跑。

独立freeze分别pin恢复源SHA与两方向源SHA，不能由待检manifest生成。所有22个MIGRATION_CHECKS保留，包括重关联同源重跑识别相同人工冲突、继续编辑/查询/撤销、模板拒恢复、无历史当前恢复、无原文件恢复、零提交重放等。比较相同投影只证明字节一致；来源真实性、业务语义与实际目标操作仍须原件和正式接口验证。
