# I05 私有观察投影规范：独立 R2 delta 复审

结论：**Fail，新增 1 项 P2（R2-01）**。R1-01 的非法 stage 安全回退、R1-02 的 language identity 及同一已绑定 artifact 内共享 BNode 映射、R1-03 的两项入口/参数映射均已按各自限定范围修复。新 comparator 把所有图槽转成集合后再比较，却没有独立检查各端 wire 数组自身的稳定 N3 排序及 RDF identity 唯一性；实际固定 ID 的乱序输出因此可被匹配。需补 canonical wire gate，不能以集合等价代替该要求。

原 R1 Fail 报告、proof、双流、首错及原候选身份完整保留；本报告不覆盖它们。本次只审私有设计及 stdlib 有限数学模型，不表示真实库/API、source/package、来源/费用、正式 Job/Store/selected/whole-H、CI、两 OS、真人或指定双模型通过。未执行产品或第三方库。

## 固定候选与实际验证边界

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-observation-projection-spec`。
- revisionBase：`57c67631fab6a36f47963aca95b4036064e10777`。
- R2 candidate：`1e753a82b837fb53f0389dabf1c401d89809238c`，相对 revisionBase 为 18 文件 delta。
- 实际冻结 process/HEAD：`ce268c62cc33a5b85d9c663c87d8260d68ab9612`；candidate→process 仅新增 `candidate-receipt-r2.json`。
- 启动实际 status 只有保护 ` M AGENTS.md`；其 15852B / SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` 一致，index 为空。
- `manifest-r2.json` 实核 12948B / `3e8d9580a8174404a64dbba9a8a785f427fd7b8248a2c06a29d182e4e59f7ee2`。
- `candidate-receipt-r2.json` 实核 21764B / `759522fdb603fe2d2132bd28a6d6d704d7829d581a9619a84f96824162211344`。
- 两前缀完整 62 文件 current=process Git bytes；manifest 的 60 成员及 receipt 的 61 candidate 文件逐项 current=candidate Git=bytes/SHA。60 成员加 manifest 为61，后加 receipt 为62，无自哈希循环。
- 43 个 R1 不可变原件逐字对 revisionBase 核验不变。`selftest.py`、`pure-sources.json` 原字节不变；37 项的 id、parameters、datasetId、inputProjectionSha256、inputSourceRefs、independentTypedMath、expectedProjection 全字段不变。没有改原输入数学或从 actual 补值。

先全文读 `disposition-r2.md`、实际 delta、修改后的 model/schema/spec、两项 invocation/API、完整 coverage 及新 `selftest-r2.py`；未变部分以 R1 已读内容及固定 Git 保全核验承接。完整 18 文件 diff 另存 `r2-independent-full-diff.stdout.txt`，模型/schema/cases/spec 的语义差异逐项审阅，格式变化与语义变化分开。新增 manifest/receipt 全部清单行由独立脚本解析后逐项核实际 Git bytes，不只信作者布尔字段。作者两次 31/32 方法日志及 formatter 记录按实际内容保留，没有把31称为32或补造原始流。

静态确认待执行 model/selftest/selftest-r2 仅 stdlib 与 detached 设计模块，不导入产品/第三方，不写既有候选；再用指定 Python 3.12、`PYTHONDONTWRITEBYTECODE=1` 运行 `selftest-r2.py`，**原20+新12=32方法实际 exit0**。没有运行会覆写旧 proof 的 r1-check/r1-counterexamples 脚本。本审者新增检查分别保存 `r2-independent-*` 分离 stdout/stderr，argv/cwd/实际 exit、流字节/SHA 和核验详情见 `r2-proof.json`。

本轮命令没有 exit 非零。这里的 Fail 是验收反例成立的审查结论；首个失败的验收断言是 `rdfs/cycle` 的 rdfs 数组逆序后仍被 `matches` 接受，不是把检查脚本故障记成产品失败。

## R2-01 [P2] 集合身份比较绕过 wire 自身 canonical 校验

位置：`model.py` L274–276、L391–393、L411–419；`spec.md` L31 的稳定 N3 输出要求、legacy 字段表的完整排序要求，以及 R2 新 L120、L149–160 的集合比较规则。相关模型执行结果见 `r2-proof.json` 的 `stableSerializationCounterexamples`、`wireVersusIdentityChecks`、`sortedAliasDuplicates`。

R2 将 `matches` 从完整 exact 改为 `projection_identity_equal`。其 graph 模式通过 set 和内部排序将输入数组归一，之后只比集合身份；schema 没有数组排序谓词，且 JSON `uniqueItems` 只拦完全相同的 JSON 值。模型没有另先证明收到的每个 graph wire 数组本身遵守 serializer 规定。

独立对**三个原固定 ID**仅逆序一处图数组，保留全部元素、其它字段、摘要和参数，结果均为 `schemaValid=true`、`matches=true`、`exactOriginal=false`：

| 固定 ID            | 仅修改的 wire 数组                   | 应核但未核的条件                   |
| ------------------ | ------------------------------------ | ---------------------------------- |
| rdfs/cycle         | value.rdfs，8项全部逆序              | 完整 N3 三元组稳定升序             |
| rdfs/domain-depth2 | value.rdfsEvidence[1].basis，3叶逆序 | 完整叶图的稳定 N3 升序             |
| scope/fresh        | value.facts，9项全部逆序             | typed 图按完整 N3 key 的稳定序列化 |

这三个例子没有 BNode，也没有不同库或随机标签因素，因此不需要放宽排序来容纳同构。全部37 expected 中实际85个 graph 槽本来都按规定 N3 排序；是新 matcher 放过不规范输出，不是要求修改独立 expected。

重复项须区分两种情况，避免误报：向非空 rdfs、rules、typed facts、basis 各插入**完全相同 JSON 项**时，identity helper 的确会去重，但 schema 的 `uniqueItems` 先拒绝，最终 `matches=false`。这四项 schema gate 有效，不能说所有重复都被最终 matcher 吞掉。

然而 `"hello"@EN` 与 `"hello"@en` 是两个不同 JSON 值、同一个 RDF identity。独立 N3 graph 小例以一条 `@en` 为 expected，把两条 `@EN/@en` 按本端 N3 顺序排好后作为 observed；schema 合法，最终仍 match。typed graph 的相同大小写别名小例也如此。它们是手写 detached serializer 边界，不是产品成功对象、新业务 fixture、capture 或实际产品观察。其意义是：即使先补普通排序，仍须按规定 RDF identity 检查 graph 数组唯一性；raw source/occurrence 的重复则应留在其原有序域，不能删。

最小 delta：在 schema 后、共享映射前，分别对 expected/observed 的全部 graph 槽验证本端 canonical wire 规律：完整 N3 排序、RDF identity 唯一，以及既定 typed/N3 表达限制。通过后再按同一 artifact 的全域双射比较图身份和序列字段。不要改37原值，不要把 when/heads/evidence/source occurrence 当集合，也不要把所有数组一概排序/去重。

合法 BNode 改名可能改变两端的相对 N3 排序：独立正例左端 `[a→x,b→y]`、右端 `[p→y,q→x]` 均已各自在本端升序，共享映射 `a→q,b→p` 后身份相等。本轮已确认它可以通过。因此修复应先证明各端自身 canonical，再比较映射后的身份；不能仅改回对两端图数组的逐下标 raw exact，也不能一般忽略排序。新增反例须包含这一个正常交叉改名例、上述三个实际ID乱序例、两类重复及 occurrence 尾项/重复的保留。

## R1 发现逐项闭合情况

| 原发现                      | R2 独立复现与处置                                                                                                                                                                                                                                                                                                                                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| R1-01：Unknown stage 可泄漏 | **原根因闭合。** `safe_harness_stage` exact str 检查先于 membership，unknown/safe_projection 共用；非法 stage 不读 diagnostic。独立10种非法输入产生30个 schema 合法 Unknown/incomplete，全部固定 collection-failure，无路径/URL/原未知文本；Poison 的 attribute/str/repr/eq/hash/iter 调用为0。另11个合法 stage 各带 Poison diagnostic 也安全回退且零触碰。str子类不能冒 exact str。 |
| R1-01：版本与保留阶段       | **闭合在私有/2。** schema known 分支 stage 与 HARNESS_STAGES 一致；collection-failure 仅 Unknown/complete=false。37项 Unknown 均不匹配，已有完整目标不变；check-shapes 只新增合法链阶段。未改公共四字段/registry/归责。                                                                                                                                                              |
| R1-02：language casefold    | **原误拒闭合。** 独立合法 shape-list a/EN→p/en 正常同构；删最后 rest 边拒绝；lexical 中 `word@EN` 改成 `word@en` 仍拒绝。仅 language identity 归一，N3 原输出语言原文不同仍保留；数字01/1和int/integer区分由原方法及新增方法验证。                                                                                                                                                   |
| R1-02：跨输出共享双射       | **同一已绑定 artifact 的有限模型闭合，扩展引入R2-01。** 独立全域映射 a→q、b→p 覆盖typed facts/ontology、N3 rdfs/rules、rdfsEvidence、evidence result/inputs/basis、provenance triple/source/derivedAxiom、query、SHACL focus/sourceShape；schema合法的抽象对象全域正常映射通过，21个位置逐一改为相反映射均拒绝，即使全局节点数量不变。没有逐field重命名蒙混。                        |
| R1-03：shape入口            | **闭合。** 固定 ee2b 合同实际L51核为parse data→parse shapes(shapes=True)→check_shapes。case逐步登记datasetField、positional、format=turtle、shapes False/True、stageReturn和keywordArguments；新wrapper=null。F1目标在第二步，第一步完整dataGraph保留、末步未到达，签名/调用链不冒实际首错证据。                                                                                     |
| R1-03：integer入口          | **闭合。** 同合同实际L52为validate_shacl_text；原camel参数/hash不变，显式data_policy=integer-illtyped-report-v1/range_policy=legacy。只放宽data object的exact xsd:integer ill_typed，不宽化int/nni/decimal或shape，不回落默认strict，不改Q6/date/外联。                                                                                                                              |

本审者也纠正R1报告对相邻来源行号的偏差：批准shape链在 ee2b 原合同**L51**，integer行是**L52**。R2没有用错误行号充新权威；完整合同SHA已重新核为 `d2cdc2e6017ad0257f30611d2928a60a116f4dc389cacdfc977c17efe13e2a23`，仅读取获准纯合同，没有补读产品函数体。

## BNode 身份域、摘要与仍未关闭的边界

新layout覆盖整个terminal的明确RDF槽，非RDF/raw/source/规则ID/warnings/摘要保exact。独立检查证实quoted lexical含`@EN`不会被全量lowercase；raw language_raw=EN→en、source null→空串、raw `_:a`→`_:p`均拒绝；evidence inputs删尾或evidence外层增重复occurrence也拒绝。正常13项对24个已知拒绝的312组合全部拒配。

**一个域必须确为同一个artifact**。独立例中两个互不关联artifact都可各自用标签a；它们分别与p、q同构，分开比较均通过；错误合并成一个域会拒绝合法的两组映射。当前API没有多artifact域ID参数，其前置合同是调用者先提供真实artifact/graph→consumer绑定，不能把同字面label当跨producer身份。R2spec已明确不同图不入同域、关联缺件pending；本次只确认这个限定设计及反例，不宣称runtime绑定已经实现或允许把不同parse/producer合并。

**摘要不自动随双射忽略**。独立左右两图合法alpha等价，各自对自身完整preimage求SHA时可以得到不同digest；当前identity_domain_equal对digest exact，因此拒配。相反，复制旧digest再改label不能称右端自洽。本轮抽象terminal联合例沿用固定摘要，只检验布局与双射，明确不充合法scope、source/capture或准入证据。R2spec对此保留了显式owner版本/完整preimage关系pending；不能凭该小例或schema宣布真实带BNode的跨端摘要兼容已通过。

8个BNode是有限小例的比较域，不是产品容量线。超过它的实现/有界算法、更多artifact关联及真实摘要关系须另接收，不能分field各求同构来绕开。37固定expected本身没有BNode，原正常/拒绝值未因此修改。

## 32方法、新增文件及回归覆盖

原20个selftest方法的源字节完全不变，本轮同新model实际复跑；不能把它们写回为R1已覆盖这些新例。12个新方法分别覆盖：非法stage零触碰、合法/保留stage白名单、语言/图尾、数字词法/datatype/节点折叠、同域正常及raw exact、query/evidence/sourceShape矛盾、ordered序列/重复/lexical、terminal布局、provenance basis及N3数字、shape精确调用链、integer精确参数映射、37固定字段保全。实际32方法exit0，完整方法名及分离双流见 `r2-independent-selftest-32.stderr.txt`。

独立新增检查没有照抄作者fixture：采用交叉BNode映射、21个跨域矛盾位置、合法/非法stage与带更多危险方法的对象、各端摘要自洽而不同的边界、四类非空图重复、三项固定ID逆序及已排序RDF别名重复。85个已登记expected图槽的本端N3排序全部通过，说明修复可以保持独立golden。现有32方法只测有序inputs反序/尾项，不测graph wire反序及language alias graph重复，所以没有发现R2-01。

| 实际 delta 文件/组                              | 独立核对                                                                                                    |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| cases.json（M）                                 | 只两API改名/新增invocation及容器projectionSpecVersion；37完整expected/math/输入字段不变。                   |
| coverage.md（M）                                | 完整37行；两API同步，其他差异为表格格式，计数13正常/24拒绝不变。                                            |
| model.py（M）                                   | stage安全门、单图language归一、全terminal layout及共享映射；R2-01定位于新增graph归一入口。                  |
| schema.json（M）                                | /2 ID、check-shapes及Unknown专用collection-failure；旧字段/安全白名单不扩成自由文本。                       |
| spec.md（M）                                    | 私有/2、explicit invocation、单artifact映射/摘要pending；保留的canonical稳定输出约束需由R2-01新增gate兑现。 |
| selftest-r2.py（A）                             | 全文静态后实跑，32方法，无产品/第三方import或候选写入。                                                     |
| delta-r2.json（A）                              | 43个原件逐项对revisionBase bytes/SHA，含R1 Fail和root receipt；作者声明与独核一致。                         |
| disposition-r2.md（A）                          | 全文处置/范围、31→32实际记录、仍待独审，未作者自定Pass。                                                    |
| manifest-r2.json（A）                           | 60个成员逐项核Git/current/hash，自排除与完整有限清单一致。                                                  |
| r2-validation.json（A）                         | 每条实际argv/exit/双流引用及31/32方法记录核对；不是产品运行。                                               |
| r2-selftest-attempt-1.stdout/stderr.txt（2个A） | stdout空；stderr原31方法exit0完整，保留首次记录。                                                           |
| r2-selftest-attempt-2.stdout/stderr.txt（2个A） | stdout空；stderr原32方法exit0完整，不覆盖首次记录。                                                         |
| r2-prettier-write.stdout/stderr.txt（2个A）     | 原作者formatter记录保留；未把formatter作为语义验证。                                                        |
| r2-prettier-check.stdout/stderr.txt（2个A）     | 原check成功记录；本轮只check新增独立报告。                                                                  |
| candidate-receipt-r2.json（后加process的1个A）  | 61项candidate current=Git=SHA；字节/hash、只加receipt的process关系正确。                                    |

以上为candidate的18文件delta及process后加1件；其它43件全部不变，合计62件。新receipt是实际candidate提交后过程记录，原manifest/receipt仍只代表旧历史身份，没有倒填或循环自hash。审查只新增 `r2-review.md`、`r2-proof.json` 和 `r2-independent-*`；没有改作者r2-validation/streams或任何冻结文件，没有stage/commit/切分支/push。

14个restore的新A1 mismatch目标、原准入/同次held expectation/allocation、payload→rows→source→definitions→catalog顺序、末项/无partial view及更早首错not-reached/pending全部保留；两front API明确化没有宣称首错已经实测。scope来源不是公共DTO或selected权限；旧metadata完整编码、真实producer/caller/capture、费用、hook、无I/O、库分类、完整上游codec/source/package及原正式验收继续pending，`wholeOracleComplete=false`。

下一步只需针对R2-01补每端canonical gate与独立正常/反例，保持共享映射和所有旧输入/数学，生成新candidate后做delta独审。R1和本R2 Fail均保留，不边审边改。
