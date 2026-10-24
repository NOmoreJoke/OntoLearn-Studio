# T01 内部服务交接面

本文件描述当前私有 Python 实现，正式状态见 [status](../../reviews/T01/status.md)。它不是新公共协议或授权来源；不注册 runtime capability，不向 renderer/Agent 直接开放 Store。

## ChangeSet 与补偿

`ProjectTransactions(store)` 接收当前唯一 Store/受信协调器持有的连接，使用内部 project ID。T00 适配公开 UUID 时须先通过现有 JobStore 身份绑定，保留 writer lease/operation claim/资源/取消闸，不再新开第二个可变 Store。

- `preview(project, base, plan)`：调用同一个真实 `Store.commit` 后全部回滚，返回冻结 `ChangePreview`。属性包括 `identity/base/intent/target/overwritten_operations`、完整 before/after JSON、定义撤回控制集、业务摘要与逐记录 Diff。仅控制状态变化也进入 Diff 和预览身份。预览不生成正式 marker、snapshot 或权限。
- `preview_undo(project, operation)`：读取原 marker 前后快照，暂停冲突；由 Store 的 `compensate={kind:"undo",operation:...}` 真实预验。只逆转该次差异，后续曾改同记录（含 ABA）也暂停；引用、单值与语句所有权最终检查仍保留。
- `preview_restore(project, snapshot)`：`compensate={kind:"restore",snapshotRef:...}`；目标须有同项目正式历史来源或精确等于当前快照。列出目标之后到 base 的全部 operation，意图/目标/覆盖清单进入预览身份。与 undo 分开确认。
- `commit(preview, operation, job, confirmed_preview=preview.identity)`：这是受信应用层调用约定；摘要匹配仅绑定用户实际确认内容，不自行证明用户已授权。Store.commit 再验 base、数据和引用，`preview_identity`、`preview_control` 与 selector 进入原子持久 planHash；控制证据在事务内与真实前后状态核对。完整结果与原预览不符则回滚。
- `reconcile(preview, operation, job)`：只读相同 planHash/job 和真实前后快照；已提交返回原 marker，不重复 writer。无 marker 只表示当前未查到提交，不能授权未 fence 的自动重试。正式 job 终态仍以 I04 持久 job/operation 证据为准。

`Store.commit` 增加可选 `preview_identity`、`preview_control` 和 `compensate`；均为 None/未传时不进入旧 plan，旧 hash 精确兼容。补偿参数与普通 definitions/remove_definitions/manual/edits/remove/mapping 互斥。快照选择器不可上传替代 state。普通 `_fact` 内容 ID 守卫不放宽；受信恢复通过正式历史恢复旧 ID。

补偿是新 operation/revision，版本 ledger 向前。定义退休从完整不可变提交历史重建目标成员（含原补偿操作），缺证据明确拒绝；版本 ledger 保留向前，vector 只投影当前实际成员。不复制旧计数。映射目标 current 绑定新 mapping 版本，stale 保守重绑为 `generatedVersion=-1` 并给真实过期码；只处理受影响 owner，无关映射保留。恢复不重新指向旧领域 current、不改写历史运行/提交/快照。原子故障点保留原七个，并增加 `mid_restore`（删旧事实后重插前）、`mid_generation`（映射计数重绑后）。

## 操作列表

内部 `Store.operation_list(project, after_revision=0, through_revision=None, limit=100)` 返回 `throughRevision/operations/nextAfterRevision`。第一页一致读取时捕获 upper，后续页传同 upper 和上页 last revision；追加提交不会进入旧列表。limit 范围 1–200 是内部投影边界，不表示 Q5 容量已测。operations 返回原 marker 全字段，公开分页/权限/帧预算须由 T00 统一约束。该列表当前只覆盖域提交；格式3应用CAS不推进域revision时，须另用同项目operationSequence统一历史，不能把此方法冒充完整应用历史。

## 草稿和结果刷新

`DraftWorkspace(project)` 仍是易失交互会话，**未实现持久草稿恢复**。独立 draft generation 提供 CAS，保存回调只可接受精确 generation；模式只有 guided/assisted。`begin_refresh(slot)` 在每次请求或失效时推进结果槽 generation；`refresh_result(slot,generation,view)` 拒绝旧回调，同代次只接受同结果幂等回放，刷新不会改草稿。

持久 metadata/draft/学习记录的迁移须与显式格式版本、JobStore/public schema 和旧 opener 拒绝同步；当前没有创建权威扩展表，不用格式 2 掩盖不兼容状态。

## 接线待办

JobStore `_plan/prepare_plan/create_job/commit_job/operation_get` 仍由原 owner 维护，未接 compensate/preview_identity/preview_control；必须同版统一，并将可信人类确认和预览分开。protocol/contracts/registry/main/preload/UI/实际 Agent 入口仍待批准接线。当前旧 JobStore marker 不携带本预览身份和控制证据，不能拿来冒充本私有预览的成功凭据。T09 案例模板来源与重置还需固定 manifest 和受信创建事务；T10 项目包迁移必须携带来源与历史证据，缺项不能声称可恢复/撤销。

普通新操作通过自己原子保存的控制证据独立对账，不要求先重建旧库缺失的更早历史。新的真实 before/after capture 可证明该次基线；没有证据的更早目标仍明确拒绝补偿，不倒填历史。
