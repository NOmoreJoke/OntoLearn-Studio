# Store 补偿与项目格式设计

## 无 schema 变化的下一阶段

在唯一 `Store.commit` 增加互斥 `compensate` selector，普通新增事实 ID 校验保持原样。两种形状严格固定：`{kind:"undo",operation:...}` 与 `{kind:"restore",snapshotRef:...}`。selector 及已确认预览身份一起进入 planHash；未传新参数时旧计划编码保持逐字兼容。

恢复来源必须为同项目正式历史：内容 hash、project shape 不足以证明可信；目标快照需能关联到 commit_evidence 的同 revision 后快照或下一 revision 前快照。revision 0 只接受完全空白的正式初态。undo 前后快照版本须与目标 marker 对齐；缺证据、未来版本、轮次证据和自造快照明确拒绝。

undo 根据原 before/after 计算受影响记录，并对当前及后续所有提交的前后证据复验；后续曾编辑同记录（包括 A→B→A）保守暂停。无关记录保留。完整 restore 列出目标之后到确认 base 的所有操作，独立确认，不能复用单次 undo 确认。

提交内应用目标定义成员/事实完整行，保留原 ID、owner/source_row/managed_value、人工值与墓碑；正式数据变更只作为 Store.commit 内部的一段实现，不能新增外部 SQL writer。最终复验引用、单值和有效语句所有权，保留已有故障 hook 和 marker/前后快照同事务。

根据实际 before/after 差异推进定义、事实和受影响映射版本；版本 ledger 不回拨，retirement 按成员变化追加/撤回。映射目标 current 绑定新的 mapping 版本；目标 stale 保持可解释的未知生成 `-1`，不能直接复制历史计数碰巧变 current。只重绑实际受影响 owner，无关映射保持后续状态。结果依赖调用原 `_invalidate`，不恢复旧 current 指针，不改历史运行。

内部 `operation_list` 在一致读事务捕获 throughRevision，稳定分页按 revision 升序，后续固定 upper bound。公开 DTO/游标/身份映射仍交 T00，不自行注册第二套协议。

## 项目元数据和草稿的格式门

现有 Store FORMAT_VERSION=2 被 JobStore/public schema 引用；schema/JobStore 不在当前写权限。需要新增权威 metadata/draft/学习记录及快照字段时，必须先确定显式升级和旧 reader 安全拒绝策略。不得静默保留 format=2 却让旧 reader 忽略新权威数据；不得在新库谎报旧格式。

项目名/模板/归档、显示模式、草稿 CAS 与学习记录需在同 SQLite，由 Store.commit 提交。草稿独立 generation，正式保存回调必须匹配其内容/代次和实际 marker；结果刷新不写草稿。快照恢复覆盖哪些用户状态必须明确，当前未提交编辑不得被隐式丢弃。具体迁移版本及跨端接线等待唯一负责人共同落实；易失 DraftWorkspace 只用于交互隔离，不计持久恢复通过。

## 验证矩阵

补偿新增完整反例：被删已编辑原 ID；首次/空映射；映射人工值/墓碑；target current/stale 重绑定；定义反复退休/恢复；同记录后续编辑与 ABA；无关后续编辑保留；后续引用/单值/语句所有权冲突；伪造但 hash 正确的快照；错项目/错 shape/未来快照；同 operation 异 selector；每故障边界异常和真进程退出；after_commit 丢响应对账；分页追加期间保持固定上界；旧 marker/hash 精确兼容。比较完整状态、版本、来源、marker、快照和历史，不只数量。
