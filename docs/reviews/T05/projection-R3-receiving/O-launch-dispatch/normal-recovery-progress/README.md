# 原 M 正常恢复后的正式终态与终稿收件

**原会话新turn正式completed，终稿原样保全；技术结论仍NotPass，完整覆盖验收未通过。** 本批父过程为 `c00e10be2a9a778bd73d814ff9898f5dc6d5b617`。这是终态与报告的静态收件，不是产品修复或父门签署。

## 已观测事实

- 本人sid `mvs_8262fb931cf34f3dae99b85683d65fd7`，正常恢复turn `02d129f4-4010-43c2-8ad2-ba620086a3aa`，精确runtime row `completed`，updated `1792684537181`（2026-10-22 15:55:37.181Z/上海23:55:37.181）。15:56:27.851270Z读回，fallback空、session idle/cwd匹配。该row不替换旧c978 delivery failed或旧ad原turn UNKNOWN。
- 同turn末assistant `msg-9d8r4FYbBSvzfUEUjn0iKRl4op0_xTlWzQMDwD9T9r8`，timestamp `1792684525088`、stopReason stop。仅复制公开text 3479B/SHA `9dee2c7b16e43a3d5884890d2b99a6f0d9de36b4d9d4d3389c68507131c59668`，未复制system/thinking/tool output。
- `final-v2.md` 实际44941B/503行/SHA `9921ffe20f68b1bbf5c7938fa7d45c9b0059cd9c8ed5b0a4afcb5a6e23852df7`，非symlink；原样复制为 `minimax-final-v2-original.md`，来源二次读取字节相等。owner全文阅读；首组合输出中间截断已补读175–335行，没有将打印截断当全文已读。
- 本批保护快照逐字节复用已提交派发快照（15:55:45.601016Z），该快照晚于final已知mtime（15:55:06.346781573Z）及completed更新，**不是新增复测**。两模型各290保护来源/11冻结launch通过，index空、detached86df、tracked仅AGENTS；Z额外32/M40仅path/lstat、unknown、不读/hash内容，wholeFilesystemFreezePass false。

## 报告意见与覆盖的接收边界

原M自报O工具链Pass（引用旧47/47及build-check合并流，本次未重跑）；149件静态NotPass；运行/打包/生产无法验证，父门全不签。owner将F01–F15原文逐条登记为 `reported-open-awaiting-adjudication`，未采纳、驳回或修源。原11条全部仍有编号，但文本均有压缩/改写，已保原11全文及新旧section指纹对照，不用“保留编号”代替“逐字保留”。F12–F15为新增候选：历史verify-i01信封、stateVersion路径、Conflict诊断文本、平台内存保证。F12“确定性运行失败”是报告基于静态推理的定性，**本次未运行该脚本，不是owner运行复现证据**。

逐件表149唯一path与固定 `full-engineering-inventory.json` 的149项集合精确相等；L124/P20/S2/部分3计数确实闭合。**覆盖标签仍是reviewer自述，owner未复做逐件产品审查，且完整全文覆盖未达成：**

- PRD明确未逐行读1–395、1020–1255；两份allocation raw仅规范行72–80/103–109，其余正文未读。登记为部分，未用完整清单计数消账。
- package-lock.json/uv.lock仅统计，未作条目级依赖审查。
- 约55件产品缺口由本人补足、三个子审网络错误零产出是报告自述；owner没有读取子审原生流追验，不用该自述判旧c978 terminal根因，也不把子审启动当覆盖。

## 发现的报告准确性限制（原稿不改）

1. **严重度汇总不一致**：报告L20/L429写5中/5低-中/5低-信息；实际15标题为6中（F01–05/F12）、4低-中（F06/07/13/14）、3低（F08–10）及2低-信息（F11/15）。所有原文保留，机器寄存器按标题计数，不改写原汇总。
2. **F15父进程采样叙述自相矛盾**：L372及证据称父进程RSS采样仅Darwin，L373又称“Darwin下父进程侧不做采样兜底”。owner只登记文本矛盾，不据此裁技术真伪。
3. **owner对F02计数的初始误读已更正**：旧F02标题本来就是9/13个golden，与本稿L279相同；旧正文另称8条observation未被覆盖，属于不同计数单位。owner最初把8条未覆盖observation误读为旧覆盖数并通知总控，复读旧F02全文后已纠正，不能登记为报告8→9的矛盾。其余11项新旧文本差异仍全保，内容被压缩不等于编号缺失或技术处置。
4. §4.1标题称“三项复核后撤销”，其中锁文件行实际明确未作条目审查。owner不将该行当锁文件风险被排除。
5. 本树已知 `report.md` 当前第三版本60824B/SHA `78cdadc36894bcb52faceac5c22a98fb13a22becb4f0f3f7f22f7fae4f292b07`，已原样另存并保JSON编码完整unified diff；旧56586/58279保全副本不改。第三版相较58279主要记录产品子审失败/零交付及约束自述；改动actor/精确时间未归因，不采其“所有未知元数据归本任务/全无未知”自述为owner证据。

137 pending、26 allocation缺件、历史IRI/FR505/graph/date/E1–E4与全部父门继续未闭，另存历史处置原文，不把报告completed等同全工程双审通过。后续是否补全文覆盖、修报告或裁F01–F15由总控在原范围调度；owner本次未再发续接、未开新任务、未改受审源码/测试/fixture、未产品运行、未Goal/push/PR/merge。GUI已释放，之后仅获准的本人精确最小后台读回与已知报告收件。
