# I05 独立费用规范 R2：独立复审

结论：**Fail，限于新提案规范及纯数学参考模型。** 固定 114 项已经有可重复的非空收费程序；本次两 seed 分别重算其全部 219815 个事件、结果字段及账本算术，均与冻结候选一致。R1 的“只有动作目录、114 金额均 null”已得到实质补充，F2/F3 的小模型修复也通过独立边界。但完整 reference 对真实词法/比较错误没有失败 invoice/H01，而且编译遗漏带变量 head 的常量受控引用及 predicate 结构预检，因此仍不能接收为覆盖所要求错误分支的完整收费规范。此结论不是产品缺陷、产品运行或现行 oracle 的结论。

## 固定对象与证据边界

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-independent-fee-spec`，分支 `docs/I05-independent-fee-spec`。base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；R1 candidate 为 `6bbea55f5134f95f715858f55c142fb8b760ccf1`；revision base 为 `ac6e0a91763ea18d5e17e162a275822e7caee8f4`；R2 candidate 为 `7554c5582619a2beddaa42bf08ffd1a8e1961214`；冻结 process/实际 HEAD 为 `b04f359a53fbce2c137d09f20a020facd8916231`。

独立核 111 个 manifest 成员、manifest 自身及 process receipt，共 113 件，全部 current bytes = 固定 Git bytes = 声明 SHA。manifest 为 29745B / `3ee69b02684a2934e01d67666eb10a11b2c0c328479cf9e95be2a44902ef3ced`；process receipt 为 20589B / `3453a574b4a0ca80d02e69b0f1e80892159a5b5bb14993d6fcef6c2b5043d132`。base、revision、process 的变更路径均只在原两 docs 前缀，process delta 仅该 receipt。R1、事故、来源和首失败原件未改。

先读 AGENTS、仓库外设计窗、实际 `.json` setup-proof、6146B 窄授权及 R1 全报告；全文读 R2 specification、handoff、hand-examples、1105 行 reference、全部新 driver/codec/primitive/retention 测试与审计脚本、采用 Q6 纯规范。114 行结构化表的所有继承字段与 R1 对比，所有新增 invoice 与完整程序对比，原输入/参数/projection SHA/独立数学 pointer 逐项核；没有用数量核对替代字段核对。

冻结时 AGENTS 15852B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 保留为历史。审查期间唯一规则 owner 按用户授权更新政策；已全文重读当前 15147B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。此为单列政策更新，没有被认作候选漂移，也未因此重跑或扩大本窗。

首作者事故仍为 not-independent；其 11526B / `bb9ef16b17408d7a87e56a7d8f3e3c8df6faffd44baf1b66f0657bdb05d959a7` 草稿仅 opaque bytes/hash/Git 比对，未解码、未读内容、未执行。2d5 只读批准的 `local-proof-excerpts.json` 三行，未读取原报告或邻行。没有读产品函数体、当前 probe/tests/generator、actual/usage、投影 WIP 或其它 worktree 产品代码。

## R2-F1 — [P1] 完整入口在语义错误时不产生失败收费程序，较早资源首拒也不能交付

位置：`charge-reference-v2/reference.py:384`、`:541`、`:724`、`:863`、`:1030`。依据：`specification-r2.md` 第 5、6 节及窄授权 B/D，要求错误前已费、首错、无成功前缀、完整 receipt/H01/终态；不能只给成功程序或手填 error 事件。

`make_program` 只在图/typed/capture/restore 全部枚举结束后调用 `finish_program`；H01 也只在该函数重放时插入。`parse_math`、`compare_math` 等真实数学错误直接抛 `ValueError`，没有将错误转换为有界失败事件并完成收费/receipt/cleanup。小模型 `Ledger` 对调用者手列 `error` 的处理不能补上完整入口的这一缺口。

独立反例均为审者新选的纯输入，没有更改原 114 项，也没有运行产品。完整输入、原异常 traceback 和已枚举收费 tape 在 `independent-r2-adversarial.json`：

1. `late-input-invalid-integer`：一个三元组，末 object 是 lexical `bad` 的 xsd:integer。枚举 25 个事件后抛 `INVALID_LITERAL_LEXICAL numeric`；没有返回 invoice，观察 tape 无 H01，仍有 control/material/workspace 的逻辑持有。
2. `false-then-type-error`：合法整数 binding，先 `1 gt 2` 为 false，再比较 N 与 S 的 `ne`。两个 comparison 都访问，185 个事件后抛 `mathematical domain mismatch`；仍无失败 invoice/H01/终态。没有把 false 当作跳过后错，但无法交付该路径的收费证明。
3. `resource-before-late-lexical`：两组三元组，各 term 的合法 SourceRecord.text 为 50000 字节，最后 integer lexical 为 `bad`。在生成 tape 第 48 个事件已先出现 ENTRY/input 首拒：已用 250824，请求 50202，合 301026 > 262144；随后第 49 个事件之后仍抛词法异常，最终既不返回该资源首拒，也不返回 paid prefix、失败清理或 receipt。这里的 48 是未插入 H01 的生成序号，不能冒充完整重放程序序号。

这不是宣称 Python 内存泄漏或产品 ledger 实际运行失败；它证明**新提案的完整数学程序对必需错误路径未定义完整输出**。固定 114 个正向数学输入两 seed 全量一致，不能覆盖这些路径。当前“发生真实错误立即整批失败”文字也不足以计算错误发生前应付多少、哪一个预算更早耗尽。

最小后继修订：让完整 reference 的每个规范错误出口均形成有界收费失败程序，先有完整静态生命周期/receipt 票，再给准确付费 prefix、稳定首错、有限 cleanup/终态；资源更早拒绝时不得被未执行尾的语义错误遮蔽。新增从完整纯输入触发这些分支的反例，不能仅在 `invoice_model` 手列一个 `error` 或填假现行 usage。原 R1 F1 因此仅部分解决，尚未关闭。

## R2-F2 — [P2] 带变量 head 的常量受控引用及 predicate 结构未在 compile 检查

位置：`charge-reference-v2/reference.py:584-605`。依据：固定 `author-v2-inputs/q6.md:13`、`:23`、`:50`，以及 `author-v2-inputs/integration.md:59`、`:63-64`；要求全部规则含 disabled、零匹配规则先完成常量/heads/RDF 位置/受控引用预检。新 profile 的 Triple.predicate 为 TermInput；head 不从常量或结果自行获得 Catalog 许可。

`check_definition` 只有当 head 三项**全都不是变量**时才调用 `check_head`。常见的 subject/object 变量因此跳过整个 compile head 校验，连已经固定的 predicate/类引用也未检查；when 中 predicate Variable 也没有结构门。若规则 disabled 或零匹配，evaluate 不会再补检查。

独立纯输入结果：

- `uncontrolled-head-zero-match`：when 的 predicate `urn:never-present` 无匹配，head 为 `(?s, urn:undeclared, ?v)`，Catalog 中只有另一属性。reference 返回 `fee-program-fits-declared-component-caps`，100 个事件，未报未声明输出。
- `uncontrolled-head-disabled`：同规则 disabled，仍返回 fits，92 个事件。
- `variable-predicate-disabled`：when 为 `(?s, ?predicate, ?o)`，规则 disabled，仍返回 fits，88 个事件；固定新 profile 的 predicate 结构在 compile 前就应拒绝。

这些反例没有从 heads 扩充 Catalog；问题是必要的前门根本没有运行。固定 114 正向数学集合核同只证明其实际枚举路径，不能证明所承诺的 compile 预检完整。缺少该预检还使“全部 compile 动作已经收费”的完整性声明没有成立，不能以真实 issuer pending 掩盖。

最小后继修订：分别静态检查每个 Triple 的位置与每个已知常量 head 的受控 predicate/类引用；变量只推迟其依赖具体 binding 的位置检查。disabled/零匹配同样完整编译，并为这些检查给明确收费事件和首错。此处只报告，不代作者改候选。

## R1 逐项处置与已经成立的证据

**R1 F1：部分解决，仍 open。** 新 binder 有明确 proposal namespace、原 raw/identity/SourceRecord 区分、确定构造文法、逐 field 状态、Catalog 声明来源；原 82+32 的完整程序/非空金额/receipt/H01 均已补。114 表全部原继承字段保持不变；没有改原 operation、参数、dataset/projection 或外部数学输入。baseline 实际是 **893** 个 fieldOrigins；全部程序累计状态统计见 machine proof。审者曾怀疑 typed pointer 使用数字索引，独立解析后 **0 个失效 supplied/None/empty pointer**，该疑点已排除，不作为发现。完整错误分支与 compile 前门仍因上述两项未完成。

**R1 F2：在本次受审纯状态机范围关闭。** control 不可普通 release/alias，保到 terminal；cap67 在 control64+receipt3 后拒新增 object，cap68 恰成功；release/重复 release/错误时点等静态拒绝。新完整 reference 也保 control64/各 D128 到 terminal，发布结果仍 live。

**R1 F3：在本次受审纯状态机范围关闭。** 全程序在开户前核 new handles/累计 slots，release 不返名额，不复用名称；BLOCK 的 work+scan+hash+临时+retained 一次预付。另选独立向量：control64、final(h3/s5) 为 work16，BLOCK work11/scan7/hash5、temp2/3+retained1/2，随后 release retained 再 HOLD2/1。objects69 在 BLOCK 原子拒，已付仍16、peak67、live0；objects70 成功，work27、peak70、累计 handles3/slots5，terminal 仅 receipt3/3。未借最终清理回流预算或 reopen。完整 reference 的异常输出问题另列 R2-F1，不与旧小模型修复混淆。

本次实际验证还包括：

- 原 8 方法/19 手列向量、生命周期 8 方法、新 typed 13 方法全部 exit0。九域×六算子 486 分类、六 numeric 的 648 实际真值均检查；Q6 通用 date/year0/24点与 SHACL finiteUTC 的不同消费者边界保持。
- baseline 全 2282 prefix 的独立算术审计、第二 input encoder、85953B 新输入及 782B receipt decoder 通过；literal totals C0=3215450、ENTRY=176580、G=185814、M0=140761，H01 work152782，累计 h8/s149538，最终 native+receipt 仍 live。审计不 import reference/invoice_model。
- 审者另两次有界纯重算，seed1/2 各 114 项、各 219815 个事件；逐项全部数学结果字段、完整费用、事件 SHA、hold/release、每 prefix used/live/peak、全 H 并持、首拒、h/slots 均核同，不只比较 counts。完整金额是新提案需求，超首拒尾仍 analytic-unexecuted-tail；例如 E.5 round4 的 input 更早耗尽不是任意 RESOURCE_LIMIT 通行证。
- 自选 11 个精确有理 IEEE 边界通过：32/64 最小 subnormal 半值与其上方、subnormal→normal 中点、max-finite 溢出中点及下方、直接 binary32 双舍入反例；没有宿主 float/Decimal 中转。原 rounding/limb/shift 先限位的有限测试通过，不宣称无限值域已穷尽。
- 固定 sorted rule_id divmod、原 ordinal、disabled 占槽/不回流、dummy 完整空 batch、同 child compile/eval、false 后继续/all-true 全 heads、重复 source/key/alias/cache hit 全字段复核、whole-J、重复 target/head/view 持有、restore/D/roots 各钱包和原 cap，在固定程序、全文静态审查及给定边界内核对。未把逻辑票解释为 heap/RSS/真实 owner quota。

## 来源、失败原件与未通过门

全部源副本及已声明 Git 来源字节匹配；Q6 纯规范为固定 `9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd:docs/iterations/T05/q6-adopted-profile-v1.md`，未拿当前算法作规范。原 R1 Fail、首作者隔离事故、首次 determinism 2240/2239 与比较 exit1、原两子命令各 exit0、13 票见 15 的 Q6 test exit1 及未知早期 exit 均保原记录；本审查不执行旧失败版本或修写其结论。

本审查首次按 `.md` 推定 setup-proof 文件名的 cat 为 exit1，随后窄枚举定位实际 `.json`，不是产品失败。最初五个只读命令的精确 combined 输出保在工具会话；当时尚未启用文件分流，proof 明示该边界，没有回造 stdout/stderr。此后命令 helper 完整保存 argv/cwd/实际 exit/分离双流、UTF8/base64、bytes/SHA；Git manifest 核验只存 opaque 输出摘要，禁读草稿未解码。新增文件只在 review 的 `independent-review-r2.md`、`independent-proof-r2.json`、`independent-r2-*`；index 空，无 stage/commit/push/分支切换。

真实现行 codec/native wire/planDigest/fingerprint、原同 issue17L/issuer/usage/权限/capture、真实 owner H/Job/source/Store 仍独立 pending；不能由本提案的数学值签发。未运行产品、pytest/npm check/build、RDFLib/pySHACL、native/DB/GUI、网络/安装/版本探针、417 产品 oracle，也未改 T05 或产品。原 57 项/六迭代、SQLite HOLD/whole-H/owner、正式 Job、指定同版双模型、CI、两 OS、真人及 develop 门均保留。后继应先封存本次 Fail，再新 revision 处置，不在冻结候选上修写。
