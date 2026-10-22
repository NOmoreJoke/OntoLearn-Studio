# I05 独立费用规范 R3：独立 delta 审查

结论：**Fail，限于提案规范及其纯数学参考入口。** 原六个 R2 完整反例现已返回有界 invoice/H01/paid prefix/failed 清理；原固定 114 项亦有完整新程序。逐 SourceRecord occurrence 的修复已由新的共享对象反例独立证实。但新选 `rule_id=7` 仍让错误封装的 receipt 路径二次抛异常，且变量 rdf:type object 被允许成功，违反固定新 profile 的静态位置要求。因此不能接收为全部规范错误入口和原语言边界均已完整处理。本报告不作产品运行、现行 invoice 或真实权威结论。

## 固定对象与只读边界

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-independent-fee-spec`，分支 `docs/I05-independent-fee-spec`。revision base `8d703858a9e7777e0086057032aea280316e49c1`，candidate `ebd3e009a9588e4019880a34a3e8096f6f61d025`，process/实际 HEAD `4699bd2b08178302beaf1660e7c0724d35ef8177`。

独立逐件核 manifest 的 187 members、manifest 自身和 author receipt，共 **189 件 current bytes=固定 Git bytes=声明 SHA**。manifest 为 38854B / `20814a8d82f8eeeb94699d92941ea7daa00b72c8220c5979227daeb90cf44519`；receipt 为 77971B / `be199aeb1a07ac72a4eb90911d5df8f0ae1126ebc23a5b07c1ab9b2ba34c9029`。revision base 的 130 件原文件全部逐字节保持；59 件 delta 全为两授权 docs 前缀内新增，candidate→process 仅新增该 receipt。原 R1/R2 Fail、原输入、旧 typed/golden、事故和原流均未改。

全文重读当前 AGENTS（15147B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`）、原设计窗与 amendment，重核 Q6 纯规范授权；新桌面政策没有扩大本次纯模型窗。全文读 R3 规范/手算/handoff/disposition/revision record、新 1258 行 reference、所有新驱动/测试/冻结/审计脚本和完整 v2→v3 core diff；所有候选 Python 静态 AST/import/write 面先核，再执行无写候选的模块。没有执行 mutating driver、旧 R2 reviewer/collector 或旧失败版本。

v1 隔离 raw、旧大 proof/流程原件只作 opaque bytes/hash/Git 验证，未读取隔离草稿正文；2d5 原报告与邻行、产品算法/actual、备包、D2/WIP、其它产品 worktree 均未读取。写面仅新 review 报告、proof 和 `independent-r3-*`。

## R3-F1 — [P1] 无效 rule_id 被带入 receipt，完整错误入口再次逸出异常

位置：`charge-reference-v3/reference.py:59` 的 `allocation`、`:809` allocator order、`:1095` 完整入口与 `:1197` receipt length。固定依据：`author-v2-inputs/integration.md:63` 要求所有 rule_id 的类型/有界字节/唯一性在排序、分配前完整校验；R3 第 2、3 节承诺 plain JSON 的实际规范错误统一返回完整失败账。

审者新反例 `nonstring-rule-id` 仅使用小型 plain JSON：一个合法 score 事实、已声明 DatatypeProperty 和一条 when/head 规则，唯独 `rule_id` 为整数 `7`。这不是任意 Python 对象，也不是生成器手工破坏生命周期。

实际结果见 `independent-r3-adversarial.json`：

1. `allocation` 只核条数与重复，允许单个整数 ID，context 保存含 `rule_id=7` 的 allocation。
2. `_enumerate_program` 对该 ID 调 `.encode()` 排序时抛 `AttributeError`；`make_program` 的确捕获它并将其分类为 INVALID_RULE。
3. 异常 handler 调 `finish_program`，receipt 长度公式再次对 `(a['rule_id'] or '').encode()` 求值，同一个整数再抛 `AttributeError`。该第二次异常逸出完整入口，未返回 invoice、H01/paid prefix/receipt 或终态对象。

原六个案例和作者 10 方法全部通过，只说明这些错误的输入元数据恰可安全编码；不能证明所有规范错误出口都闭合。这仍是 R2-F1 所要求完整入口的缺口，不应改标为产品错误或合法 RESOURCE_LIMIT。

最小后继修订：在任何排序/分配前对整次规则元数据作有界结构检查；无效 ID 不进入预测 child/receipt。完整失败 receipt 的构造只消费已验证字段，早期无效规则以明确未完成绑定表示，保准确原始输入指针，不将 ID 静默转字符串或伪造 dummy。为一个新无效外层字段补真实完整入口反例，不只追加这一个字面 ID 分支。

## R3-F2 — [P2] rdf:type object 变量放宽了已冻结的新 profile 语言

位置：`reference.py:598` 的 `static_head`，尤其 `:604-606` 的 `object_known` 条件。固定依据：`author-v2-inputs/integration.md:59` 明确区分 legacy 与新 profile：新 profile 的 predicate 为 TermInput，**rdf:type object 必须为已声明类 TermInput**，差异由显式版本入口拒绝/定位。原窗口/amendment允许新收费 binder/primitive，不允许修改该语言政策。

审者新反例 `variable-rdf-type-object`：输入声明 `urn:C rdf:type owl:Class`，另有 `urn:s urn:classRef urn:C`；规则 when 为 `(?s, urn:classRef, ?v)`，head 为 `(?s, rdf:type, ?v)`。Catalog 确实含 C，故没有依靠伪造许可；问题是规则 head 的类位置本身是 Variable。

完整入口实际返回 `state=completed`、`firstError=null`，M0 work10581，保留 native+receipt；独立数学集合检查也一致。`static_head` 遇 object Variable 时跳过类常量要求，evaluate 再以 binding 值属于 Catalog 为由放行。R3 文字把这种位置描述为可延后检查，已经超出原纯收费补充的权限。

最小后继修订：新 profile 在 compile 对 rdf:type object 的 TermInput/已声明 Class 要求直接检查，enabled、disabled、零匹配同样收费和拒绝；仅对原语言确实允许依赖 binding 的位置延迟具体值检查。不能通过改 legacy、扩 Catalog 或改原已采用规范来使本例成功。

## R2 发现处置与已成立的修复

**R2-F1：原六例已解决，完整发现仍 open。** 两个词法/比较错、零匹配/disabled 不受控 head、variable predicate 以及较早资源首拒的原输入逐字段未改。原六 JSON source 对象图的区别被明示：旧 collector 复用两个 source，JSON 读回为六个独立对象；原 R2 dry48 仅为旧生成 tape，不冒新执行序号。当前六例均返回 H01Paid、有限 reason、分析/执行双 tape、paid prefix、IFR3、failed/live0/无 retained handles。资源例正确保留完整执行第 53 项 ENTRY/input 首拒，250824+50202>262144，未执行后的坏 lexical，不能被尾错误覆盖。新 R3-F1 说明封装还未覆盖所有规范错误。

**R2-F2：原静态缺项在其原反例范围已解决；新语言边界仍有 R3-F2。** when/head 位置有明确 3 work，固定 head predicate/已知 class/property kind 的 Catalog 扫描与许可检查，在零匹配/disabled 编译也执行；原非法 when Variable predicate 在 compile 拒绝，未进入 plan hash/join。这里不能把原反例修复外推为允许 rdf:type object Variable。

**逐 occurrence source：实际修复成立。** 独立第三种对象图：六个 term 共享 **一个** SourceRecord；JSON 读回六个独立 SourceRecord。两者不仅 amount 相同，而是整份 invoice（含分析/执行事件与两 hash、paid prefix、receipt）相同；C0 六次 source scan 合 864B、六次合成 text hash 合138B，ENTRY/key/fingerprint 仍逐出现收费。没有通过 Python id 省扫描票。固定 baseline 的 record-term source84+definition source1，85次扫描61420、85次合成 hash35383，相对原 source 小账分别增加40072 scan/22920 hash、合62992 work/112动作；原“只解释49→53就算修复”的不足已补，不改写旧证据。

这里 C0 source 新条款的核验口径明确是当前程序的 record-term.source 与 definition.source；定义常量内的 TermInput.source 另由 M0 编译/parse 的完整输入与复核计价。若后继采用“每个 term.source”作更宽的通用表述，应明确这两个动作域，避免从本次85次口径推导未规定的额外 C0 费用。

R1 F2/F3 的旧小 Ledger、19+8 字面程序未改，本轮没有重跑无关旧测试；原 R2 范围内关闭结论保留。本轮对新严格执行器另做资源与终态边界，未借旧小票证明 IFR3。

## 独立正反验证与适用范围

本轮重新执行作者新 10 个完整入口方法，以及不 import reference/Ledger 的审计器；均实际 exit0。13 个旧 typed 测试文件与字面 expected 逐字节不变；本轮没有为未改的 numeric/Q6 算法再跑无变化小测试，原有限分类/真值/IEEE 结论仍只保持其原范围。

独立两 seed 对 **114+6** 项各重新从固定纯输入调用新 reference，逐字段比较冻结完整结果；自行重放全部分析与执行 tape，按全九累计域+两 live 域重建 atomic reject、holds/releases、峰、全 H 并持、首错后仅清理、累计 h/slots 和终态。另自行解全部120个 IFR3：LP/固定宽度/全部17L/状态reason/首错ordinal/已付域与峰、执行 hash、零 footer hash、F/R/H01向量均核，未将分析需求写入 receipt。完整表的原现行/数学字段与 R2 一一保持，未改原 ID/dataset/operation/parameters/projection/外部数学。

固定114每 seed分析231960、执行231899项，所有完整字段/双 hash/receipt与冻结表一致。113项在原分池内；仅 E.5 round4 在 event13687 的 M0/input 拒绝：255390+12342=267732>262144，拒绝向量整体不扣，此前 binding16/firing15/head15/trace15不退款、整任务不发布前缀。分析13755项与执行13694项含清理严格分开，没有以分析尾冒已执行。

完整 baseline 独立核2410项、792B receipt、85953B fee material。C0work3278484/scan2275119/hash823438；ENTRY176580、G185814、M0141562；H01work152824/scan3168/hash810、h8/s149538；全峰149697/6819815，终态 native+receipt12016/272442。原 component caps 未抬，真实 owner H 不从这些逻辑票推导。

审者新有界边界不是作者六例的改名：

- `last-head-bound-literal-subject`：第一 head 合法，第二 head 的 subject 是 binding 的 literal，真实 evaluate:head 在第166项拒绝；M0 head occurrence2、trace1、firing0/output0，已付保留而返回引用全部清零。
- 新小型成功程序 M0完整 work10368。仅下调数学测试钱包到10367，在最终 batch digest 前已有8548，请求1820，整向量拒绝、hash不部分扣、failed/live0；10368恰成功，10369同额成功，不靠 blanket reject。没有改候选原 cap。
- 仅下调该小程序 C0 work 至H01需求19166的差1，即19165，第2项H01整向量拒绝，H01Paid=false、所有累计0、没有data/receipt持有，control终态清除。它是开户前拒绝边界，不能标成“已支付H01”的失败路径，也不能把静态分析票当已付。
- `nonstring-rule-id` 的未闭合异常与 `variable-rdf-type-object` 的错误成功均保实际原流/完整新输入；其它探索值仅作为证据保留，不无依据增列政策结论。

## 首失败、流程及未通过门

从本轮第一个 shell 命令起已启用新分流 helper，记录每实际 argv/cwd/exit/stdout/stderr、UTF8/base64、bytes/SHA；大件/隔离原件的 Git 比对输出只作明确 opaque 摘要。`git diff --no-index` 的实际 exit1 是“存在 v2→v3 差异”的正常返回，保 lossless diff，未包装为测试失败或0。新 verifier 捕获的模型异常不等于其外层诊断命令非零；报告分别陈述两者。

作者本轮 event49→53 test exit1、audit01 map顺序和 audit04 未开户M错误的 exit1、查询exit2、补丁工具 exitunknown、首次manifest数字误写及早期版本的有限成功均保原件；本审查不执行旧失败版本，不补造未知 exit。根初次按旧 `artifacts` 字段读 R3 manifest 的 KeyError/exit1 仅为根只读过程事实，后按 `members` 核189件成功，不算候选失败。旧 R2 交接“17件新review”是将 status17行含AGENTS误说为文件数，实际16件；根已保留该数量断言失败，不改旧报告/流。

最终 HEAD 不变、index空，只有保护AGENTS M与本轮明确新增 review 文件；准确新文件数由最终 `git ls-files --others` 实测，不能用 status 行数替代。没有 stage/commit/push/切分支、改环境/Goal或外部聊天。

现行 native/wire/typed/planDigest/fingerprint codec、真实同issue17L/issuer/usage/capture/权限、owner H/Job/Store仍独立 pending。未执行产品、pytest/npm/build、RDFLib/pySHACL、native/GUI/DB、网络/安装/版本/model、417产品oracle或T05受审候选。原57/六迭代、SQLite HOLD/whole-H/owner、正式Job、指定同版双模型/CI/两OS/真人/develop门均保留。后继应封存本Fail，再新revision修订，不能在本冻结候选上代修。
