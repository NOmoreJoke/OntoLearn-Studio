# B 方案：逐意见处置与来源选择

2026-10-21。本轮只有 docs；起点为 A 固定 `6a38fcb8135343ba5e62a8a8effe57b18c3de00c`，批准产品基线仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。产品、原 A 的 68 条交付、e2c/961 原件及保护 AGENTS 不动；不执行产品/测试/真实运行 IO/网络/GUI，不改变 Goal，不 push/PR/merge。

## 首审与修订

首审候选 41058B/SHA `d6bf752aa945711867c8362fa9e332474b03cf81e3922486c81a125bc9fd2d10` 原字节保存在 `plan-before-independent-review.md`；`review-input-r1.json` 绑定当时四件。独立首审 `independent-review-r1.md` 7405B/SHA `1acdbd9d80b906aced55f35dae19a33b0f96d17e3c2b1d2f27e6cfd81001f25a` 原文暂不通过，不能倒写成首审已通过。

| 意见                             | 真实触发与原方案缺口                                                                                  | 修订位置及处置                                                                                                                                                                                                                                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P2-1 同址历史/current 不能映射 A | A payload locationKey 唯一且完整观察不能省略旧记录；仅新 incarnation id 不足以同时保旧 inode/新 inode | §4.2(8)、§7(4)明确原 A 遇此形态 unknown，保全部身份，不漏历史。精确最小 A inventory+专属测试两路径扩展为另批申请；只允许有限 absent-retired 历史与单 present 并存，负例继续拒绝。§9列未来真实替换及正反例，本轮不修或重测 A                                                                                  |
| P2-2 控制树自举/自身追加递归     | 首次写 intent 需要目录，目录又被旧条款要求先有 intent；journal自身写亦可能递归                        | §5冻结唯一 fixed-control bootstrap/self-append 例外；真实 trusted fresh、预reserve、固定目录/header、partial/close/sync/identity失败unknown，期间外部目标 IO0。自身固定协议追加不递归，其他目标仍须 durable intent+seal；bootstrap 来源/原语未到仍是 B-R 实施前置。§9列未来验收，不提供真实 fresh 或生产能力 |
| 小项 owner 数量                  | “其他六类”与实际四个 I06 子集角色不符                                                                 | §2改“不合成任何缺席 owner”，不因子集测试补 synthetic owner                                                                                                                                                                                                                                                   |

修订候选 44238B/SHA `b71667de836ee2bcf8f62107f170e808200a3b4f77c264ed06d7c21e9ceed605` 由 `review-input-followup.json` 绑定。最终独立定点复核结论以另存的 `independent-review-followup.md` 原文为准；首审与后续结论分别保留实际时点。所有反例均是静态代码推演，不伪称本轮运行失败或已有实现通过。

已实际全文收取最终复核 4459B/SHA `050bb29bbb07d93584f47c3b4b7d62ac14223c738f22625fed7384cddd86f851`：两项P2及owner小项关闭、修订方案静态审查通过、无新增阻断。它绑定上述最终候选；不授权产品实施或解除生产 unsupported。无需重跑无变化产品。

## 两份来源报告的采用

`source-metadata.md` 原31796B/SHA `78cdde9eeebceb1e9e1c8764c0873363f7b49ed665266d026122b8863bf3945d`、`source-lifecycle.md` 原23028B/SHA `6f0cb3bd6950af0ba588c7357025ae17c126a8d8b03ac0d23371e1149d1fdb4c` 保留原字节。其源事实、完整闭包、初始化/close/包装Promise缺口已采用；其候选 B1/B2/B3 顺序、文件名、控制位置均是各自建议，不并集为额外授权。

主方案统一选择 B-M/B-R/B-L；metadata 新路径为 private-resource-owner.ts，实际操作新路径为 private-operation-lifecycle.ts。先观察子集，再单独固定持久来源，模型/仓库适配逐路径后批；源报告中其他命名不创建。控制根选稳定 appData 候选而非跟随可变 userData，实际名称/源 identity/安装级 writer 与 fresh 仍待根/T01冻结。B-L选择供方自身唯一 pre-admission gate；A reservation 只是必要时另批替代方案，不当前实现、不开放 callback/scope factory。

配置仓库 canonical 运行时牵连、type-only 依赖仍需获批类型闭包、Model* 在5f不存在、network/credential/audit/全部旧当前 child 和 Store永久寿命，均按源报告保留；不能为编译或fixture成功复制 e2c canonical/T01源码或写 stub。当前只读来源共52项，均有 ref/路径/bytes/hash；不将hash核验称为全文研究每份代码。

## 验证、封存与未验边界

本轮仅文档格式与静态 Git/JSON/hash/范围核验，实际命令及退出记录在 `raw/` 和 `checks.json`；没有 B 产品运行结果，不贴 A 的700TS/1052Python为 B 通过。没有新 ZIP；原件以本次 docs Git ref/manifest 绑定，旧 A ZIP 未改。本轮无需通过重跑冻结产品来验证文案更正。

manifest不自列，checks不自列自身最终hash；Git实际delta提供外部绑定。复制入本review的五份外部授权/根报告保持原字节（可能保留末尾空行）；原独立报告不批量格式化。完整 Git whitespace 与仅新主方案/自写摘要检查分开记录，不能为洗绿改变原件。

生产仍 unsupported。真实全量owner/retired来源、目标OS/native/同build VFS、T01宿主/Store/worker/dispatch/永久排空、公开消费及57P0/父I06/FR-002均不由方案定稿通过。下一步仅供根批准最小B-M或先定具体缺口；本文/独审不自动授权任何后续产品。指定同base/head双方新审、CI、正常develop合并、远端、两OS和真人门保留。
