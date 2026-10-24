# T01 第一阶段独立内审

审查者：独立只读 agent `/root/store_interface_audit`。base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。范围：私有 project 包、两份 test_project 测试、Store 可选 preview_identity 及接口边界；不替代 ZCode/MiniMax 指定双审。

首轮发现两项 P2，均有独立临时探针复现：

1. 已提交 marker 分支仅比较 plan/base/job，修改预览 before/after/意图/目标/覆盖清单仍返回旧成功。修复：完整 preview.identity 作为新可选 Store plan 字段持久化，对账复核真实前后快照。新参数未传或 None 不进入旧计划；保留旧 hash。五种已提交篡改反例均拒绝且整库不变。
2. 仅按 projectRevision 排序结果，无法区分同版本新旧查询，也会把 stale 回退 current。修复：每结果槽独立刷新 generation，每次请求/失效推进；旧 generation 拒绝，同 generation 只接受相同结果的幂等重放。完整草稿不被更新。

复核结论：**两项关闭，当前私有阶段无新阻断，可以阶段提交并继续实现。** 独立运行 T01/Store/JobStore 416 passed；ruff check/format 六文件通过；git diff --check 通过。无 GUI、原生窗口或外部审查应用操作，无文件修改。

受审实现 SHA-256：

| 源码 | SHA-256 |
| --- | --- |
| storage.py | 38aabe4355f9cd6e7a145495ac5d896f6b512135754f83771759b8e3da249cab |
| project/transactions.py | b3c6ca33d68737c47981319c99ae91b5c148cfc5c563fe0aee67612e0d65125c |
| project/workspace.py | 07963e2c662b71eac1c380ca311035852c3a6d2cb77ac1dc516b82ca039bd369 |

保留边界：完整恢复仍受限，草稿仍易失，未接公开 protocol/worker/main/UI。旧 JobStore 不携带新预览身份，不能将旧 marker 当作 T01 预览对账依据；正式接线需其唯一维护者统一处理。指定双审、实际 CI、集成和父功能验收均开放。

另由 `/root/recovery_design_review` 只读复核下一阶段：支持不改 schema 的 compensate/operation_list；metadata/draft 权威持久化须协调显式格式升级、旧 reader 拒绝和 JobStore/canonical，不能保留格式 2 偷加权威表。恢复需正式 commit_evidence 追溯、后续冲突/所有权/retirement/动态失效、旧 hash 兼容和真实故障验证，详见 compensation-design.md；此为设计意见，不计下一阶段运行通过。
