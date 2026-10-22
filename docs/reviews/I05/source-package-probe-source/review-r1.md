# I05 source/package probe：独立静态审查 R1

结论：**不通过**。固定候选有两项 P2 和一项 P3，需修复后冻结新候选并作 delta 复审。未发现输入结果污染或供应源码被改写；这不等于运行、业务、包或发布通过。

审查者为新的独立 agent source_package_static_review_r1，不是 probe、资产或测试作者。只写本报告和 review-r1-proof.json；未修改受审文件，未 import／exec 产品、probe、tests，也未运行生成器、pytest、npm、ruff、formatter、构建、安装、DB、native、网络或 GUI。

## 固定身份与实际范围

- base：5f910b52c69d86a1076b2032e5d3c63e715947f3。
- candidate：0e42a0fe349054a92817cb4d463bccdc15f6c042。
- 22 模块采用：01434e3f0f693de1cc3b560d04fdecd700d424a3；T01 四件采用：44f88a5cf45563a47ecf8df32cff35b7baaa95fa。
- immutable supplier：6891a5842302859a531cf82767c5a482417bc274；process：f79a29f596b2444cba542a906c91727869014886。
- probe：83335 B／cfdd263dd28db81af8852f957be92caa2c7047605b4097aba8b98b407a86b736。
- generator：59342 B／7b0499507d599b8061e02dca518cae6d5c1ffb7e07bcc1375c2791bac9173c9d。
- tests：63296 B／fd61df800d081ba28cc92515be9fd81c1280e522ed0e86f4c256aa7f29a490d6，66 个 test 函数；未作 pytest 收集，不能给展开例数或 passed 数。

按固定 Git 读取并核对 candidate-manifest 的72件，共13009828 B；逐项 current=Git=manifest。该清单明确排除自身和后续过程件，不误报为整个仓库的清单。另读取其自身及精确 window、limited closure、T01 增补、accepted-contract，分段审查完整新 probe／generator／tests，交叉读取 canonical supplier 的类型、入口、capture/restore 及 ledger 状态机。72件全部 bytes/SHA、核对步骤和限制见独立 proof。

AGENTS 实采15852 B／78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759；开始时唯一受保护 M，未暂存。源码／资产在本审查期间未变。

## R1-01 [P2] 每次真实调用前后缺少 deadline 边界

位置：probe run_fixed_suite L1545–1689，尤其 start 在 preflight/import 后、循环内只在整 observation 前检查；_b1_observation L1423–1494 的 timed 以及 _dispatch L1497–1532。

固定合同 §4.3 要求120秒 monotonic「调用前后／逐 case 采样」，并承认不能中断 opaque 调用。候选却只在整 observation 之前及整个循环末尾检查。一个 B1 observation 内 First/Warm 两遍的 Turtle parse、ontology parse、graph build、query、reason、shapes parse、SHACL、serialization 之间没有任何 deadline 检查；scope 和 production 的多阶段调用同样如此。首个 opaque parse 在deadline之后返回时，代码仍会继续启动后面的真实 query/reason/Validator 乃至 Warm，然后才发现超时。preflight/import 本身也全部在 start 之前。

这是控制流可直接证明的偏差，不是声称本机已经超时。精确反例：专用 b1-semantic-1x-v1，collection起点为0；First/turtleParse 返回时 monotonic 已是121。当前 timed 返回后直接启动 ontologyParse/fixedSelect 等调用，未观察121。现有 test_deadline_boundary 只让循环前钟跳121，不覆盖同项内部边界。

建议：在 probe 中保存同一次 monotonic 起点和安全边界控制，canonical 原函数每次调用前后显式检查；不 monkeypatch 业务函数。preflight耗时域应明确并在首个业务调用前纳入检查。中途超界保实际已完成阶段、callCounts 和 incomplete；不得以此宣称硬超时或实际 cancelled。补写调用返回后过界、不再启动下一真实阶段的测试源码，当前仍不执行。

## R1-02 [P2] 中途失败丢失已完成阶段，unknown 没有当前 stage/API

位置：_b1_observation L1423–1494 的 timed／passes；_production_observation L1183–1257；run_fixed_suite 的 except 分支 L1610附近。

合同 §4.2 要求 observation 的 stage/API、全部安全诊断；未知异常保 INTERNAL_ERROR、当前stage和incomplete。§7 要保每阶段及 First/Warm 的完整输出与失败原件。当前 unknown 只有 operation、classification、exceptionClass，不能定位究竟在 parse、query、reason、compute、restore 还是序列化。B1 的 phases 仅在 call 成功返回后更新，passes 仅在整轮成功后 append；如果 Warm/shacl 失败，First 的全部成功结果与 Warm 已完成阶段均滞留在局部变量并随异常退出，外层无 result/partialOutputs。真实 producer 已成功但正例 restore 或 observer serialization 失败时，本次已发行 bytes/expectation/allocation 也没有进入该 observation。

精确静态反例：同一 b1 observation 的 First 全成功，Warm/turtleParse、ontologyParse、graphBuild、fixedSelect、rdfsRules、shapesParse 已成功，Warm/shacl 抛未知 RuntimeError。外层只发 unexpected-failure，无 First 或 Warm 已得结果、无 stage=Warm/shacl；终态虽正确 incomplete，仍不能完整审计首失败。另一个反例是 production 成功后 restore 抛未知异常：外层没有同次 producer 接收 bytes，可恢复输入及见证，不能据此复核 source/package 的失败差异。

建议：只读记录当前 stage/API 与阶段开始／结束，及时保留真实返回及同次发行的安全 bytes/receipts；失败时输出明确的 partial observation（collectionComplete=false），不编造未返回值，也不发布 partial restored view。未知异常仍只给安全 INTERNAL_ERROR，不能 stringify 原异常。调用边界、阶段保留和最终 JSONL item cap 应一起核对，超限仍走不截断失败。测试源码需覆盖「成功 First 后 Warm 故障」及「真实 producer 后 restore 故障」并验前项未被抹掉，不能 fake 业务成功结果。

## R1-03 [P3] 静态 diff 检查漏了候选新增文件，当前还有 EOF 格式失败

位置：docs/reviews/I05/source-package-probe-source/static-verify.py L86附近；input-generation-report.md L497；generator main 的报告构造结尾。

static-verify 只运行无 ref 的 git diff --check；它不检查 untracked，也不检查已经 staged／committed 的新候选。报告当时给 gitDiffCheckExit=0是真实命令返回，但不能覆盖本候选新增文件。独立实际执行 git diff --check 5f910b52c69d86a1076b2032e5d3c63e715947f3 0e42a0fe349054a92817cb4d463bccdc15f6c042 返回2：

~~~text
docs/reviews/I05/source-package-probe-source/input-generation-report.md:497: new blank line at EOF.
~~~

这与 root 首次 cached check 的同一失败一致，不能被旧工作区 check 的0覆盖。报告由 generator 可复现产出；只手改说明会使 --check 再次不一致。建议修 generator 的报告尾部 LF，重建说明及其来源清单/候选清单；静态验证明确对比 base→固定候选，并独立核当前工作区/暂存区，拒未覆盖的新文件。保本轮失败及旧候选，不覆写为pass。

## 静态核对通过的范围

- 22份供应 Python 与四资源逐件 current=固定Git=采用清单；probe imports 只含已列 canonical 闭包、stdlib、rdflib 和 pyshacl；未见 resource_manifest/build_request/execute_request/derive_dependencies/permits_transition 的调用，也没有 Store/worker/旧 probe helper 导入。T01 采用没有扩大到 states/dependencies 或公共业务接口。
- input 8205267 B／47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa；manifest 21202 B／0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a。417项、320 datasets、22份固定原件；所有投影 SHA、manifest size/SHA、全部 case-set 顺序与三个selector一致。
- 对原83逐字段重做独立 JSON 白名单对照：asserted/ontology只取triple+source，definitions只取原输入字段，disabled保留；contexts中的原106/54/50/unresolved/nonClaims与原件完全一致。82 eligible、79 full、交集78；repair77只禁原profile，before/after shape仍独立调用；四E5保fragment。C13的原 data/query/shapes 文本逐项一致，2 query/11 SHACL及显式policy变体都在。
- datasets递归未见 computed expected/matches/closure/native/restore前提等字段；71个合法 definition.heads 保留。原源路径／hash与运行新资产投影分开；审计 corpus 可含原测试expected，但没有把它们投影成运行输入。
- 真实 API 参数与 canonical 签名相符；结构化 TermInput/RuleSpec 构造没有替代 matcher／比较器。material prepare 与 production使用新CaptureLedger；_restore同次原expected/original_allocation，负例不重绑外层摘要，且先保成功view。九mutation按固定enum只复制接收bytes，不能将A1拒绝升级成深层DAG/末槽证明。DAG text入口真实走生产拒绝，旧fullview text入口分开。
- JSONL逐条完整编码后再写，partial integer write继续，传输半行时 broken 禁再append terminal；logical item/report cap与terminal reserve原值保持。当前固定 full terminal 的独立静态编码34755 B、B1子集terminal约11918 B；仅核当前字面schema/ID的尺寸，不是产品运行或未来schema空间证明。
- hook以code对象身份计数，已有hook拒绝，finally恢复；B1子集不挂hook，First/Warm与full instrumentation区分。图数由实际len取得，coldClaim/freshProcessExternallyVerified没有自签；内存、RSS、startup与S1 snapshot保持unknown/not-executed。未重开被拒heap/OS/SQLite话题。

## 保留的限制与下轮门

当前锁仍是未采用的5f，八distribution未实测；frozen没有T03外部build provenance而前置拒绝，是有意限制，不是本轮新增缺陷。source/package实际运行、native、12个B1 fresh、原12个S1 snapshot、全量oracle、父包、许可、指定双模型、check/package、CI、目标OS、真人和develop/远端全部开放。

marshal-filename-normalized code fingerprint是独立代码对象编码域；本轮只审其源码，没有运行 loader/compile比较，不能静态认定跨loader／缓存／optimization必然稳定或未来必然失败。后续同版实际验证应明确该域，或另用已审可复现的结构投影并补稳定性测试；不能用目前source SHA替代包code证据。

应先处理R1-01/02/03、保存逐项处置和新candidate；对实际变化作独立delta审查。本报告不改写首轮不通过，也不授予执行权限。
