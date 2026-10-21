# T06 事件源位置修复候选完整本地独立复核

审查者 `/root/behavior_independent_review`。结论：**通过本次私有行为算法完整本地只读复核**。全部历史问题关闭，未发现新的实质缺陷；此前不通过记录保留。

固定 HEAD `e81cfc973d251b76d8b9537adae150e8d2f930af`，分支 `feature/weekly-t06-behavior`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。审查前后 HEAD 一致，仅 AGENTS 既有保护改动。

已全范围重新覆盖 T06 实现、接口、私有 fixture、两份测试和历史问题，核对原 PRD：

- FR-600 定义唯一、独立实例、事件幂等正常；常量 create 历史 P1 未回归。
- FR-601 仅内部 create/set/add/notify，无外部入口；资源处理仍待集成。
- FR-602/E.1 冻结条件、全部意图后竞争检查、完整排序键、实例内部顺序、同值保留其他动作、单多值正确。
- FR-603 状态/轨迹/Diff/完整冲突证据比较保留；原缺测 P2 未回归。
- FR-604 检查的失败不改输入，无部分 candidate/consumption，丢弃模拟未标正式执行。
- G.3 私有反例符合原语义，手工推导未冒充完整轮次。

最新 P2 已关闭：`planner.py:307` 保留排序前 event_index；头/载荷、身份冲突、编辑失败均含正确源位置，合法字段才加入 ID/sequence。独立重跑原两种复现均修复；另确认 request 原始顺序保留，执行视图仍按 sequence/ID。

错误文本为安全结构常量；内部 evidence 与公共参数边界明确。完成前缀、partial_decision、discarded_actions 分别表达，无部分成功候选。

独立执行：两份行为测试 **83 passed**；5 个 Python 文件 ruff check/format（无缓存）通过；原问题内存复现及原始顺序/执行顺序探针通过。

未验证真实推理/RDF、Store 事务/回滚、资源、取消、公共接口、Agent/UI、完整 G.3、打包、CI、生产；新候选全仓检查由开发线另提供，旧结果未沿用。未写文件、推送或运行 GUI/e2e/native/HMR/CUA/指定应用。

本结论不替代指定双模型外审，不表示完整 T06 已验收。
