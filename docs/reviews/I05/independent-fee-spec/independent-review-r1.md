# I05 独立费用规范：独立 R1

结论：**Fail，限于本窗完整设计交付及纯数学模型；不作产品缺陷或产品运行结论。** 当前候选可以保留为来源清楚的局部公式、缺项清单和数学小账，但还不能接收为已补完五 operation、82+32 输入的独立收费方案。发现 1 项设计完整性问题和 2 项可重复的纯模型问题。114 项现行 invoice 全部 pending 的诚实标注是正确边界，不应改成假精确值；同样不能把仍待别人供应的关键提案称为完整设计已给。

## 固定对象、隔离与审查范围

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-independent-fee-spec`。
- branch：`docs/I05-independent-fee-spec`；base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- candidate/实际 HEAD：`6bbea55f5134f95f715858f55c142fb8b760ccf1`。
- candidate manifest SHA256：`4aba269a56b297b55d27ec01bb55606e508cb129531cadadddbcdd122f6535b4`。
- 启动核验仅保护 `AGENTS.md M`、index 空；AGENTS 为 15852 bytes / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。此次仅新增本报告、`r1-proof.json` 和独立命令原件 `independent-r1-command.py`，没有修改、stage 或 commit 候选。

先全文读仓库外设计窗、setup-proof、当前树 AGENTS；全文读主规范、operation schedule、handoff、hand examples、model、tests、fee contract、bound formulas、16 组 structured claims、114 行 Markdown 表及结构化 JSON、19 个手列向量。逐 ID 的完整重复字段由独立只读代码逐项核对，并记录全部 114 个 ID。没有执行作者的 collect/inventory/validate/seal 写入脚本。唯一执行的新候选代码是先读/静态检查后的纯 `invoice_model.py`、其 8 方法数学测试；独立命令只使用 stdlib、该纯模型、固定 JSON/Git/hash 和已授权 formatter。

首作者事故仍为 not-independent：读了 incident 描述；旧 draft 仅作 opaque bytes/SHA 与 Git 比对，未解码内容、未复用。其 11526 bytes / `bb9ef16b17408d7a87e56a7d8f3e3c8df6faffd44baf1b66f0657bdb05d959a7` 完整。对 2d5 只读允许的三条裁剪证明，没有读取原报告邻行或历史 actual。fresh v2 作者过程按 root 的隔离派发事实及冻结 process/incident 记录接收；字节封存本身不独立证明一个作者从未看过其它上下文。

## F1 — [P1] 新提案仍缺决定费用的动作程序、字节合同和操作前置票

位置：`specification.md:55`、`:69`、`:73-79`；`operation-schedule.md:14-28`；`handoff.md:23-28`；`per-id.json:108-112`（同形缺项覆盖全部 114 行）；`process.md:11`。

收费单位表已经给出，但动作次数及被收费 bytes 仍不能从此提案唯一推出：

1. G02–G09 仅列“每次插入/查询/索引/候选/join 等付费”；没有独立候选/索引/匹配 traversal 程序。`:69` 明确还要 owner 供应纯动作清单。相同图和相同首 witness，可以全表配对后筛 predicate，也可以先建索引只枚举匹配项；两者满足表中“每次动作收费”，而 ITEM/SCAN 数不同。独立 insertion-sort 片段只解决已给数组的排序收费，不决定这些数组和候选的枚举量。
2. E08/M02/M04 没有完整 typed input/output/fingerprint 字节文法和 primitive schedule。`:73` 要求未来提交 ArithmeticWitness，`:75` 保留 typedByteExact=null。Horner/GCD 的局部提案足以解释两个小账；尚不能唯一计算 binary rounding、Calendar、IRI/lang/regex、全部字段/指纹的事件和 temporary_bits 前门。新的 TLV 是 proposalPlanDigest 的另一个域，无法给这些既有 typed 字节收费补值。
3. 五个 operation 没有 `:55` 自己要求的 receipt 精确大小、最大 handles/slots 与完整 finalization 静态 vector。原文明确“否则该条 pending”，但没有填入。小账 TT 换行的 3B receipt 只代表小账，不能移用作五 operation 的票。BLOCK 的 live 也未由模型表示：`invoice_model.py:150-155` 对 block 只返回累计 charges 和 None，无法作为一个向量原子核对委托临时 retention。
4. 每 ID 的 proposalInvoice 仅有组名、amount=null；requiredScheduleGroups 全部漏 H01。真实 issuer/usage 当然必须等待实际 owner，但其缺失不妨碍本窗先补纯数学的收费程序与保留公式。当前把这两类缺口放在一起推给后继，尚未完成本窗要求的最小具体提案。

**具体影响：** 即便为 `profile-83/baseline:G-base` 假设已取得完全真实的同次 L/issuer，当前规范仍无独立方法计算其图候选/join 次数、typed 流 bytes、receipt/cleanup 票，不能区分预算足够时误拒与正确拒绝。对 32 链也相同，只有分支组名不能给出首耗尽点。它不因诚实 pending 而成为错误 oracle，却仍是未完成的方案。

**最小修复：** 在当前授权 docs 面补版本化的纯 action schedule、逐种 typed 字节/算术规范、每 operation 的有限前置/finalization 向量及 retention 转移公式；或逐缺项明确列出需 root 接收的窄纯规范请求，同时将本候选降为“局部费用设计/未完成”，不声明完整方案已给。获准采用的提案须有至少一个从完整纯输入到逐 prefix 费用的独立完整示范，并把每 ID 的可计算提案/剩余真正权威缺口分开，补 H01 依赖。不能读取产品算法或历史 actual 来填这些数，也不能升 cap。

## F2 — [P2] control bootstrap 可提前 RELEASE，导致并持额度误成功

位置：`invoice_model.py:227-231`；应遵守 `specification.md:53-55` 及允许局部证明中的固定控制表示生命周期。

RELEASE 只禁止 receipt，允许把仍在使用的 control 票全部释放。独立反例（`r1-proof.json` 的 `control-ticket-released-before-data`）在 objects cap67 下：

```text
HOLD control64
F(handles=1,slots=1,fields=2,bytes=3,domain_bytes=1)  # reserve receipt objects3
RELEASE control
HOLD x(objects=1,scalar=2)
finish
```

模型实际 completed，peak.objects=67，work=10。control64 对应 caps/used/live/peak/stage 等仍在用的固定表示，不是可反复利用的数据票；普通事件阶段需要 control64+receipt3+x1=68，应在 x 前拒或把提前 release 判为无效程序。此反例没有假设 Python heap/RSS，也没有执行产品。

**最小修复：** 将 control 注册为生命周期特殊 handle，只允许在 terminal cleanup 内解除；其它提前 RELEASE 拒绝，并确保失败清引用/不退累计费用。增加 cap67/68 和重复/提前 control-release 的独立字面边界。当前 19 向量没有 release 事件，因此原 8 方法绿测未覆盖此问题。

## F3 — [P2] finalization 证明不足在保留变更之后才发现，异常未清理终态

位置：`invoice_model.py:214-226`；合同位置为 `specification.md:53-55`。

模型先写 held/live/peak，随后才检查累计 handles/slots 是否超过已预付 cleanup 的证明。独立反例 F(handles=0,slots=0,fields=2,bytes=3,domain_bytes=1) 后执行 HOLD x(objects1,scalar2)，实际抛 `ValueError('finalization proof insufficient; incomplete model')`，但留下：

```text
state=running
used.work=8, scan_copy=6, hash_bytes=4
held={receipt:(3,3), x:(1,2)}
live=peak={objects:4, scalar:5}
```

这不是 resource 预算失败后的正常 live0 结果，也不是在产生数据引用前就拒绝了不完整数学程序。它恰在证明已不足以覆盖清理后保留 x，并使账本停在 running。再次 run 虽被拒，仍不能补上本次 terminal/cleanup 证据。

**最小修复：** 在任何 held/live/peak mutation 前核对新增 handle/slot 的 finalization 证明；无效事件若属于静态程序错误，先全程序校验再开户，或在已开户路径统一以有限失败终态清引用、保留既付费。添加 h=0、s=0、最后允许 handle、差一个 slot、曾 release 后累计新 handle 仍不回流的字面测试。不得事后增大 finalization 票或重开 ledger。

## 已通过的限定验证

`r1-proof.json` 保存 82 个独立 verification subprocess 的 argv/cwd/各自 exit、stdout/stderr 或 opaque 输出 bytes/SHA；全部 exit0。独立 runner 的工具实际 exit0 另记。初步读文件时把 bound-formulas 路径写到 reviews 下，wc 工具 exit1 已单列保留，随后全文读正确 iterations 路径；不伪造 shell 展开后每个 argv 的独立 exit。作者原三次 early failure 继续为 exact exit unknown，作者旧 115→121 修订和旧绿测有限范围完整保留。

| 验证面 | 本次结果与边界 |
| --- | --- |
| 冻结与 manifest | base→candidate 恰 53 个新增文件；52 项+manifest 自身与 diff 集合相等；每个 current bytes=Git bytes=SHA；manifest 自排除可复现 |
| 来源 | 22 输入 bytes/SHA 全匹配，其中 19 个完整 Git ref/path 与冻结副本逐字节一致；另外为当前 AGENTS、裁剪 local proof、外控 API 声明；16 组 excerpt/逐行文本/bytes/SHA 全匹配 |
| 114 输入与逐 ID | 82+32 ID 恰覆盖、无重复；dataset pointer、声明 projection SHA、独立 JSON byte/hash/节点/字符串计数、定义/record/targets 数、disabled、114 外部 expected pointer/value SHA 全逐项核对 |
| allocator | 113 行完整 17L 与独立字面常量及 divmod 公式一致；原 ordinal 与 sorted 槽保留，disabled 仍占槽；1 行 Turtle 只保明确 canonical API 省略参数时的 dummy 条件值，未推为真实 invocation/capture |
| 16c/R_parse | Σk=203N+33×1024+4×262144，N3 总 work51414625、N1 总51414219、input/output各524288；cap 不当 usage，R/R_parse/16c 分账；R_parse 仅同版完整原成功下的子集蕴含 |
| 数学真值 | 18 个整数比较均独立核 1/2/3 对 2 的运算真值，并核纯输入 score lexical、operator、阈值；不因此证明匹配或准入 |
| 手列事件 | 全部 19 向量与字面 expected 一致；8 个作者测试方法实际通过。人工复核 F14、成功23/差1时已付21、false16/17、双比较全heads32/末head前29、alias34、cache269/尾前259、restore28×2=56、roots32/尾前30、并持7/15、D121、GCD17、Horner20。它们是给定程序的小账，不能证明事件程序没有遗漏 |
| 独立新边界 | 自行选 L(2^64)=3、L(2^32)=2：F10+MUL6+SCAN2=18，cap17 在 SCAN 前已有16而拒；另自行构造 F2/F3，实际复现上面两处模型问题 |
| 现行 exact/下界/上界 | 七池/49B key framing/32B audit separator/limb 乘除单位可核；“至少1”继续仅下界；R 分域、C 八 stage、T/S/H 为带前提的既有拟界；D139417856为固定 traversal 子界、通用 cap581671040，18work/2scan 的 index 字节是新提案，不能当旧 exact 全账 |
| authority 与决策 | 114 行原 capture/planDigest/usage/issuer 均 null 并列 missing；现行完整 invoice=0、提案完整 invoice=0、全部 admission pending；没有自动允许任意 RESOURCE_LIMIT，没有预测 L 代发点 |
| 格式与修改边界 | 已授权现有 Prettier --check 检查候选自写 md/json，通过；冻结 raw 副本及保全原件不格式化。git diff --check 通过；候选无变化 |

## 覆盖判断与后继门

false 后继续比较、all-true 全 heads、后项错误无 success prefix、Catalog/source 重复 occurrence、cache hit 仍逐值核、same-child compile/eval 不重开、disabled None 与 dummy 真空 batch、未用不回流、重复 restore 分账、roots 重复 target 不去重、篡改原摘要不重签、完整 7/15/11 与新 7/16/11、whole-J/C/R/D 与 H 转移、Job/owner/retired 责任均已有明确行为约束；本次未发现这些文字把图语义或授权身份偷换成数值相等。F1 涉及的是这些约束尚未形成完整可计算程序，F2/F3 涉及其纯模型违反自己的 retention/预付承诺。

proposalPlanDigest 的字段顺序、TLV tag/framing、原 17L 顺序和独立 domain 已列；它没有冒充现行 planDigest。未知原前像、typed 编码与原图动作仍未补齐；TLV 通用编码器/Record 不等于严格业务 schema validator，亦不发行 PV/receipt/producer 身份。Q6/Q5 等业务默认、原 cap 与数学/版本没有被擅自改动；API defaults 声明不能证明调用发生。

本次不读取/执行产品函数体、probe/generator、历史 actual/usage/日志，不 import 产品或第三方，不跑 pytest/npm check/build/RDFLib/pyshacl/native/DB/GUI/网络/安装。产品真实性、417 完整 oracle、预算运行、正式 Job、whole-H/SQLite HOLD/owner、指定同版双模型、CI、两 OS、真人和 develop 门均未因此通过。后继应逐项处置 F1–F3，产生新固定候选再独立审；此报告不会代作者修改冻结规范。
