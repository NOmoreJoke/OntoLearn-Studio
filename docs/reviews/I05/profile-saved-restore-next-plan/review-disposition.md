# 独审意见处置与本轮交付边界

最终主方案：`docs/iterations/I05/profile-saved-restore-next-plan.md`，45463B，SHA256 `3f72f07ba535983ca324226be769de2c157303b35b723aa107bf4e6252a1f41b`。独立审查原初意见、修订delta与有限结论均保留在 `independent-final-review.md`；首版37213B/214e原样另存 `plan-before-review-fixes.md.raw`。本轮仅文档，未修改或运行产品/测试。

| 意见 | 主开发处置 | 独审最终读回 |
| --- | --- | --- |
| R1 [P1] R整次常数来源不完整 | 新增A1–A16固定阶段、六次wire与hash调度、累计节点/copy上限、live集合；区分新代码逐操作扣与不可改canonical调用前整体预付。另列opaque逻辑持有预留，不伪称新增内部hook。JSON转义chunk由B/Q buffer付款，不误套64KiB小槽界。 | 已关闭于静态方案与debit合同；未来实现仍须逐循环/调用/共存集合核，不能当实现或CPU/RSS通过。 |
| R2 [P2] 三字符串native容器含糊 | rdfs/rules、evidence与rdfsEvidence内层三元值全部明确exact tuple，外list、basis/proof tuple分别冻结。 | 已关闭，与实际meter.key/生产组装一致。 |
| R3 [P2] key header未固定导致64B界有歧义 | 精确8B binary header、source位、8字段marker/4B UTF8长度/None编码，最大framing49B；审计SHA separator精确32B。 | 已关闭，S≤B+64M条件成立，hash仍不作cache等价。 |
| 辅助静态表漏计vararg | AST census补计vararg/kwarg；check_ints由2改3，全表最大仍30。 | 独审自有重算diff=[]；不影响预算合同。 |

额外精确化：恢复测试必须subprocess exec全新Python解释器，不能用继承父发行注册表的fork快照冒跨child恢复。没有新增第五个代码路径或selected测试。

本轮根只接受“方案准备”：实际16c新API只读，未复制/采用；未来70项只是63继承+3待采用+4新私有文件的精确申请。T01正式producer/Store/worker终态、项目快照与权限、保存窗口/撤回GC、selected第六测试、长期字段/公共消费、T03 D2实际组合及父出口没有关闭。旧Goal状态未改。

仅做Git/文件/标准库AST/JSON/hash/整数运算与文档独审；未import产品、未pytest/probe/npm check/verify:sources、未安装/build/package，无GUI/native/e2e/HMR/Keychain/付费/push/PR/merge。固定0475的118项bytes/SHA零漂移，AGENTS dirty原字节保护且不提交；具体静态读回见final-static-audit.json。最终文档集合由artifact-manifest.json逐项固定，manifest自身以Git提交ref固定，不循环自引用。
