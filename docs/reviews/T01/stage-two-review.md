# T01 第二阶段独立内审记录

范围为第一阶段提交 `03376dfb873a67260fd6ef426c603f3ffbe3feb1` 后的 Store 补偿、历史列表、project 私有服务及对应测试。所有审查只读，禁止本机 GUI/Electron/e2e/native/HMR。此内审不替代两指定模型。

## 发现与实际处置

| 来源 | 问题与触发 | 实际修复及反例 |
| --- | --- | --- |
| `/root/store_interface_audit` P2；`/root/recovery_design_review` 定点评为 P1 | undo 合并仅检查重复有效三元组，漏掉普通 writer 的保留 ID/墓碑占位；恢复旧编辑 ID 会侵占后来保留的内容 ID | 最终每条有效事实复用 `_check_slot`、排除自身。活动保留 ID 和映射墓碑两种反例都拒绝且完整 DB dump 不变。两审均已复核原问题关闭 |
| `/root/store_interface_audit` P2 | mapping 无定义的历史目标恢复后残留后来 retirement，使原本允许的同源重跑被禁止 | 从完整不可变提交前后状态和补偿 selector 重建目标退休成员，缺证据拒绝；不改旧 snapshot/schema/hash，ledger 向前。原本已退休/未退休分别恢复后实际重跑拒绝/成功；二次恢复和 undo 纳入同一历史规则。已复核关闭 |
| `/root/store_interface_audit` 后续 P2 | 空映射撤销后历史计数被 vector 隐藏，首次重跑错误取0，刚生成即 stale | 普通 mapping 从真实计数 ledger 取 generatedVersion；undo/restore 至缺席后的首次与再次空映射重跑都立即 current。待最终复核 |
| `/root/store_interface_audit` 后续 P2 | 仅 retirement 控制变化没有可见 Diff，零变更摘要却改变未来重跑权限 | 预览单独捕获控制前后集，在详细 Diff 展示 definition-status/已撤回，摘要与 identity/Store plan/提交复验/对账全部绑定。仅控制变化的 restore/undo 及实际重跑拒绝都有测试。待最终复核 |

## 已完成的独立验证

首候选：全范围 T01/Store/JobStore 480 passed，发现前两项额外探针遗漏；修后候选 485 passed，原两项关闭但新增后两项。定点审查原 P1 关闭，68 个专用补偿用例通过，另三组内存 SQLite 序列分别成功提交 47/51/42 次并核对 retirement 历史重建、计数向前和有效定义不同时退休；它没有验证后续两项，不能拼成最终全范围通过。

开发侧最终修正版已有 T01/Store/JobStore **488 passed**；最终全仓与独立全范围复核进行中。各轮原始日志本地保留，最终 hash 清单单列，不能拿前版通过替代修后验证。

## 保留门禁

无 schema 迁移/metadata/draft/学习持久化，无公开 JobStore/协议/UI/Agent 接线，无指定外审、push、PR、CI 或合并。格式3及应用 operationSequence 继续由唯一 owner 协作；当前 operation_list 仅域提交范围。恢复依赖完整正规历史，旧缺证据记录保留可查看，不能猜测恢复。

## 最终复核通过

后续发现第五项第二阶段 P2：合法 v1 迁移项目缺早期历史，普通提交可成功却在丢响应后因强制 retirement_at 全历史而无法对账。修复为本次 `preview_control` 的真实前后控制证据在 Store.commit 事务内严格复验、与 identity 同 planHash 原子持久化；普通操作只凭自己的 marker/控制/前后快照对账。新精确 capture 可证明对应基线，不倒填更早缺史。实际 v1→普通提交→after_commit丢响应→重开对账/幂等重试/新操作撤销已通过；新增控制形状/排序/重复/伪造after拒绝反例。

`/root/store_interface_audit` 已最终全范围复核：**累计7项历史意见（第一阶段2项、第二阶段5项）全部关闭，当前内部范围没有新阻断，支持本地冻结提交。** 独立 496 passed，ruff check/format 八文件及 diff check 通过。此前表中后两项“待最终复核”在此次全部关闭。开发侧新完整 `npm run check` 实际退出0：630 TS、1196 Python，lint/格式/typecheck/构建/ruff均通过。

最终受审核心 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| storage.py | 8f4c32648d084ba143e031be48762b1324892f4090c79f3c5fb44628bba4f46f |
| project/transactions.py | 13a9f9a104e2f7d0d71ba4b7f66a7adfb40e32631d6d67a9dbd5835ae590a123 |
| project/compensation.py | 99ecf0bb4383753accdc0df75f3564d058cfe9945203bc844b9739e0c51ea4cb |

指定模型/正式集成和前述未验边界继续保留。本次仅新增格式3基础合同设计文档，尚未启用，不将其作为已实作/验收内容；后续独立挑战及T00统一合同另记。
