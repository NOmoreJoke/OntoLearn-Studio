# T09 私有多阶段证据绑定提案

这是独立父任务工作树 `T09-stage-evidence` 中的只读 Python 原型，未批准为公共契约，也未接入 `LearningService.check`、UI、IPC、registry 或 Store。T09-S1 的 `7659665`/`74b17a4` 原树整套冻结，当前共享批准基线仍为 `5f910b5`，此树只延续本线私有实现。正式持久账本与跨端合同由 T01/T00 唯一维护；本文件给出可评审的最小具体输入与反例，不授予第二写通道。

## 为什么不能只检查终态标签

课程 query 需要 Open 时的 Q-01 和修改 A01 后 Closed 时的 Q-02；quality/transfer-repair 需要删除与修复前后结果。每阶段的实际输入版本、快照、参数和结果必须保留。附录 G 各用例独立重置与课程连续路径分别建计划，不能把独立项目串成同一祖先链。

批准 I04 `JobStore.result_get` 在事实或依赖改变后会把旧结果返回为 `stale`。因此合法前置阶段不能靠把旧结果改称 `historical/current` 通过。该原型保留当前 canonical 结果原值，并要求 owner 在阶段真正成功、当时结果 current 时即持久保存不可变完成回执。检查时只读取既有回执，不从今天的结果补造“当时 current”。仅有 resultId、createdAt 或 revision 大小不够。

## 受信输入与职责

调用者只提交 Context 和有序 `StageRef(stage_id,result_id)`。`StageReader.view` 必须由 owner 提供一致读视图；它从持久任务定义/尝试账本读取 `StagePlan`，读取 result/job 的真实 canonical DTO、完整分页和已存在的 `StageCompletion`，并从同项目不可变提交链核验祖先。不能把 renderer 字段当作这些受信数据。

| 私有对象        | 绑定内容                                                                                                                                                                                                                      |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| StagePlan       | planId/version，聚合终态 project/task/attempt/inputVersion，attemptEpoch，root 输入版本/快照，terminal 快照，有序 slots                                                                                                       |
| StageSlot       | stageId，输入选择账本序号、完成账本序号，实际 inputVersion/snapshot/revision，精确 kind/definitionId/scope/parametersHash/dependencyVector/definitionSetDigests/implementation，expected capability，显式历史选择及同快照许可 |
| StoredStage     | owner 持久 join 的 plan/version/context/epoch/root/stage/完成序号，completionReceiptId，实际 job/result，全量 FetchedPage                                                                                                     |
| StageCompletion | 可定位 UUID receiptId，以及相同 plan/context/epoch/root/stage、实际输入选择/完成序号、当时持久保存的 canonical 完成结果                                                                                                       |
| StageReceipt    | plan、每阶段当前原始结果、原始完成回执、实际分页 rows；只表示绑定成立，没有 operationComplete、independentTransferSuccess 或领域 passed                                                                                       |

job/result/page 复用本树批准的唯一 `CONTRACT` 校验，不复制公共 schema。实际 job 必须 succeeded，resultRef/jobId/project/snapshot/输入定义等精确匹配；每 slot 还限定真实能力与全部结果选择字段，避免同快照的另一查询/约束/范围/参数顶替。

完成结果必须当时 current、无 staleReason、payload available；它和当前结果除 `state/staleReason/historicalSelectionRequired` 外所有字段逐字 JSON 相等，包括 createdAtMs、jobId、实现和版本。历史 slot 可保留今天真实的 stale 状态，但不能据此声称当前有效。终态 slot 必须今天仍 current、无 stale，且对应实际当前尝试输入。此收窄约定只覆盖连续课程，不自动覆盖事后选择旧快照重新执行的所有学习路径。

实际页从 null cursor 开始，逐页绑定同一 project/result/snapshot/scope/参数，游标链完整到 null，行顺序与 rowId 唯一，缺页、驱逐、重复和换绑拒绝。完成回执不能替代已驱逐的载荷，也不替代后续完整领域结果比较；绑定正确但 payload 错误仍可能被领域检查拒绝。

root→各阶段→terminal 与相邻阶段都必须有真实祖先关系；同快照要 Plan 明示。输入选择/完成账本序号严格交替递增，防止把后补回执当作前置阶段；它们必须来自 owner 真正持久的账本，不接受客户端计数。这个原型不能证明说谎的 resolver，正式 owner 的不可变持久性和原子 join 仍是必验前置。

## 并发、恢复与正式接线前置

`current_plan` 必须核对实际当前输入和 attemptEpoch，不能原样回显旧 Plan。读取后再核同一完整 Plan；receipt 消费前使用 `require_current` 重核，真正学习记录写入须在 T01 自己的 CAS 事务中与此核验原子完成。输入变化、尝试换代或计划变化后旧 receipt 不再可用。此模块不持有 SQLite、不写账本、不创建尝试、不清辅助历史。

正式接线还须由 T01/T00 审定：完成时原子保存 receipt 与结果引用/输入选择的事务；重开/复制/跨窗口时 epoch 与完整账本恢复；允许历史证据的真实只读选择；回收/pin 生命周期；固定错误映射；签名/版本与 runtime 能力。缺任一受信来源就不能用合成对象登记产品完成。T01/T08 的最高提示、完整示范与跨尝试辅助来源仍独立受信，StageReceipt 不授予独立迁移成功。

## 当前验证范围

纯测试使用明确 synthetic owner/ledger，核查精确选择、归属/顺序/祖先、分页、终态变化、原始完成证明和负例。另有真实批准 I04 JobStore 的 read 发布、事实编辑、失效及分页探针；test.read 只保存测试给定 rows，不执行 SPARQL/SHACL，学习完成账本仍为测试内存对象。因此它证明当前真实 stale 元数据可被原样保留并正确绑定，不证明真实领域工具、T01 持久 ledger、包内或平台验收。
