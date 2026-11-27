# 独立接口核验

审查者：独立只读 agent `/root/store_interface_audit`。基线：`5f910b52c69d86a1076b2032e5d3c63e715947f3`，工作树/分支/AGENTS SHA 一致。只读原 Store/JobStore 与 PRD，没有运行测试，没有修改文件，没有使用 GUI。

结论：现有单次 Store.commit 可完成受限补偿撤销；不能普遍表达完整快照恢复。复用真实 writer、版本前进和不可变历史；不能剥离来源近似恢复。

逐项意见及当前处置：

| 意见 | 实现/交接处置 |
| --- | --- |
| 已编辑后删除的手工事实，原 ID 不等于当前内容摘要 | 私有恢复明确 RESTORE_REQUIRES_STORE_SUPPORT；需受信快照恢复扩展，普通新增 ID 闸门不放宽 |
| 映射人工漂移或墓碑不能由单次 mapping+edits/remove 还原 | 明确拒绝，交唯一 Store 维护者实现来源保留的补偿计划 |
| 首次映射用空 rows 撤销仍留下 mapping_state | 专用真实库反例，明确拒绝，不伪称完全撤销 |
| marker 缺少按 revision 的公开完整清单 | 私有只读原 commits 表；正式分页列表交接，锁定 throughRevision |
| 快照不含隐藏退休/版本账本 | 恢复推进新版本，不回拨 ledger；后续元数据迁移需兼容旧快照 |
| JobStore 已有正式真实回滚预览/可信 actor 确认 | 私有服务不注册协议，正式接线必须复用 prepare_plan；私有确认 hash 不等于人类授权 |

需注意：外层事务组合多次 commit 并读取原始历史，可克服部分“单次计划”限制；不将其表述为数据库本身绝对无法实现。本报告是接口分析，后续实现须另行独立内审与指定双审。
