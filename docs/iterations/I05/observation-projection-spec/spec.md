# I05 私有观察投影规范提案 v1

本提案给 37 个固定观察 ID 的精确目标值、严格 JSON schema、来源和有限关系。`cases.json` 保存完整值及全部独立 typed 数学侧车，不能用本文摘要替代。当前是待 owner 接收的私有 serializer/API 技术提案；没有执行 6891 产品或真实库，`wholeOracleComplete=false`。11 个 legacy 域 ID 实际为 **10 个正常、1 个 unbound-head 拒绝**；依固定输入、独立 oracle 和合同 L45 保留这个差异，不因设计窗简称“正常”而改写结果。

## 依据及交付面

- `pure-sources.json`：固定 0e42 两资产内的 37 个观察、19 个不同 dataset，以及 3d8f 已独立编写的逐 ID 数学预期。不是新 probe 输出或运行 golden。
- `cases.json`：37 项 `expectedProjection` 全字段精确值、`independentTypedMath`、API、参数、输入投影 hash、来源、前置条件、有限关系与 pending。
- `schema.json`：JSON Schema 2020-12；每个对象 required/exact keys，禁止 extra；term、triple、legacy、scope、来源、报告、错误都有完整定义。
- `model.py` / `selftest.py`：只构造本提案的 JSON 数学模型，不创建产品类、capture、allocation、Job 或成功产品对象。仅 stdlib，零产品导入。
- 同名 review 目录：原始限定行摘录、逐源字节/SHA、额外批准字面参考、实际验证记录及 manifest。

来源有四种不同权威：① ee2b 已批准合同与既有 I03 边界；② 6891 指定行的接口字面/旧预登记断言，只约束该局部场景；③ 3d8f 独立有限数学；④ 本文新增投影编码、精确前门与规范化 API 的提案。④ 不能追称 6891 已实现。固定输入只决定输入，constructor 默认、异常类集合和字面 key 集合均不能决定某 ID 的实际首错。来源账中旧完整文件只求字节 hash；只解码批准行，没有按关键字筛出邻近算法。

不读费用作者树或 WIP，不导入产品计算/解析/解码/投影模块，不取历史 actual/usage/golden，不运行 helper、新 probe/tests/generator。已批准的旧纯合同含有历史状态叙述，本文不将其用作任何 expected、预算或运行证据。

## 三个边界

| 层                 | 载荷与含义                                                                      | 不能推导什么                                                  |
| ------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| canonical 私有 API | 实际异常的有限声明字段；当前函数确实返回的全部结果                              | 默认字段不是实际发生字段；内容相等不证明同次发行              |
| harness 私有观察   | 本文版本化 JSON 投影、真实所在 harness 阶段、实际 hook 次数、完整已返回阶段原件 | 不是公共 DTO，也不授权 selected、Store、Job 或读取资源        |
| 公共 ErrorFrame    | 现行 strict 四字段 `code/messageKey/retryable/params`，由受信入口/责任归属适配  | 不加 stage、reason、路径、原值或自由 message；不修改 registry |

本文的 terminal `projection` 是完整终态投影，不是整份执行日志格式。harness 必须另完整保留每个已成功返回阶段的原件，按有序阶段 ordinal 关联，包括 producer 的完整 payload/rows/sidecars/typed 视图和原 source metadata。拒绝终态的 `partialView=null` 不意味着删除此前完整成功阶段，也不制造当前失败阶段的半个视图。整份 harness 的 fullview 编码/真实 capture/预算来源仍按原 owner 合同待接收；本 schema 不能冒充这些未闭字段已完整。

## RDF、N3 与集合/序列

typed term 精确为三种：`{kind:"iri",value}`；`{kind:"literal",lexical,datatype,language}`；`{kind:"blank",label}`。字面量 language 必须显式 null 或完整字符串，不能省略；datatype 保完整 IRI。三元组是长度恰为 3 的数组，subject/predicate/object 顺序固定。数据 BNode 仍拒；只有既有合法 shape-list 图允许 BNode。允许 BNode 不等于批准任意空白节点输入。

图是 RDF identity 集合；不做 integer `01→1`、date/offset、IRI/namespace、词法等重写。simple literal 和 xsd:string 按 RDF 1.1 同一身份；language 在**图身份**比较中仅 casefold。完整原文、raw TermInput/source/null、语言大小写、重复 raw record 的**有序 occurrence**留在固定输入/完整阶段原件，不因图去重消失。N3 是三字符串数组，不把它拼成不透明字符串：IRI 为 `<IRI>`；literal 为完整转义引号词法，非 string datatype 加 `^^<datatype>`，lang 加 `@原语言`；BNode 为 `_:label`。不调用任意对象 repr/str 来序列化。graph 的稳定输出按完整 N3 三元组字典序；语言身份归一后的图与原 occurrence 是不同比较域。

合法 shape-list BNode 的比较必须对**整张图**找一个双射，保每条边、list 尾项和结构。不能逐行独立换名、删 BNode、删尾或把一个节点映射到多个节点。`graph_isomorphic` 只用于最多 8 个 BNode 的独立小例；超过其小例域返回 false，不称产品实现或通用库性能证明。原输入/证据 occurrence 序列仍精确比较，不以图集合等价吞掉重复或顺序。

schema 定形状，另须满足本文有限关系及逐 ID exact 值。shape 合法不代表业务合法/匹配。严格 JSON reader 必须拒重复 key、NaN/Infinity；exact integer 排除 bool。字符串按 Unicode code point；UTF-8 无 BOM、无 Unicode normalization。摘要 preimage 用 `sort_keys=true, ensure_ascii=false, separators=(",",":")` 的 JSON UTF-8；文档格式化空白不进入这个数学 preimage。

## legacy 五字段和全部证据

| 字段         | 类型/省略/null                              | 完整值与顺序                                                                                                                  |
| ------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| rdfs         | N3 triple 数组；required，非 null           | 仅有限 RDFS 新增图集合，完整排序；不混入 seed                                                                                 |
| rules        | N3 triple 数组；required，非 null           | custom 输出图集合，重复 head 只在图集合去重                                                                                   |
| warnings     | string 数组；required，空时 `[]`            | code+`:`+原规则 ID 完整字符串；按字符串排序去重                                                                               |
| rdfsEvidence | `{result,basis}` 数组；required             | 每条 rdfs 结果恰一项，按 result；basis 是选中 witness 的完整原始叶集合，排序；不是只保直接前件                                |
| evidence     | `{rule,result,inputs,basis}` 数组；required | 每个 accepted match 的每个 head occurrence 恰一项；inputs 保 when 原定义位置、全尾项和重复；basis 为全部输入 witness 叶 union |

evidence 稳定键为 `(rule,result,inputs,basis)`，词典序；相同完整键 occurrence 仍保重复。这个顺序是本 serializer 的**新增明确提案**，不能由旧 `evidence=records` 推出现有全部规则迭代顺序。bindings、whenBasis、headIndex、全部 comparison、definitionOrdinal 和 orderedDirectInputTriples 在 `independentTypedMath` 全部保留，与五字段逐项关联；五字段没有相应键不意味着可丢弃数学侧车或运行原件。`rdfsEvidence` 的 basis 与 direct witness 的有序两前件分开。

有限规则仍只为 domain/range、type-via-subclass、subclass transitive；先闭包，再固定一次 custom matches，不反馈 custom 输出。每个 RDFS witness 保既定 stable-first 候选次序，不新增 shortest-depth。cycle 自反结果只来自环的实际传递，不引入普遍自反公理。完整 witness/premises/depth/leafUnion 数学在 cases 内，不能只核最终图数量。

`legacy/no-rule-feedback` 的 `RULE_CHAIN_UNSUPPORTED:R-next` 来自相同 rule-chain 条件及 6891 scope 局部预登记字符串，应用到此 ID 的稳定格式在本规范明确接收；没有改为公共错误。其余 9 个正常 legacy warnings 均 `[]`。`legacy/multiple-matches` 输出图只有一个 head，但 evidence 有 A01、A04 两条完整四输入记录。`legacy/unbound-head` 应 `UNBOUND_RULE_VARIABLE`，没有成功五字段对象。

## scope 四项与来源

投影外壳为 `{kind:"scope",complete:true,value,query,shacl}`。`value` 恰有 `facts/ontology/reasoning_result/provenance` 四项；前两项完整 typed 图；asserted 的 reasoning_result 显式 null；fresh/project 为完整五字段。不接受把 profile /2、DAG /3 截字段喂旧 legacy helper。

provenance 新版本 `i05-scope-observation-provenance/1` 恰有 `format/selectedFacts/selectedRuleIds/warnings/derivedAxioms/views/reasoningSource`。这是缺乏旧纯合同后的最小新编码提案，**不是**声明旧 6891 已有这些精确 keys、view hashes 或 source 编码。

| 字段                     | 有限关系                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| selectedFacts            | 按完整 triple N3 排序，每个 facts triple 一项；`sources` 是 occurrence 数组，不能只选第一项            |
| asserted source          | `{kind:"asserted",basis:[原 triple]}`；不冒称 ontology/rule 来源                                       |
| rdfs source              | `{kind:"rdfs",basis:完整叶图}`；domain/range 依据必须同时有 ontology 公理和事实                        |
| rule source              | `{kind:"rule",ruleId,inputs,basis}`；保每条对应 evidence occurrence，不因 head 相同合并来源            |
| derivedAxioms            | `{triple,source:{kind:"rdfs",basis}}` 数组，完整排序；只入 ontology，不污染 facts                      |
| selectedRuleIds/warnings | 全部实际选用规则 ID / 完整警告，精确字符串排序；asserted 为两个空数组                                  |
| views                    | asserted/selected 各 `{factsCount,ontologyCount,factsDigest,ontologyDigest}`；数量是摘要，完整图仍比较 |
| reasoningSource          | asserted 显式 null；derived 为新 `i05-scope-content-source/1` 内容摘要记录；不作为 authority           |

内容 source 的三个摘要精确为 canonical JSON：`{domain:"i05-scope-facts/1",graph:完整 typed asserted}`、ontology 类似、`{domain:"i05-scope-rules/1",rules:原有序全部 raw 规则定义}`。保留 definition/source/null/比较/heads 的原字段及顺序。完整预期摘要在 cases；不造实际实现来源、运行身份或 source-vs-package 代码 hash。

内容 source 不是 6891 原始 `provenance.reasoningSource` 的替代入参。已有 project 必须用同次 prepare 原样返回的**真实旧 metadata**及 reasoning_result；此 display 新版本只由新 serializer/API 导出。新 API 若引入 canonical source，应保另有受信同次 handle 与实际 producer provenance，按明确版本分派，不能拿本 JSON 自述替代。旧 metadata 完整编码尚未获纯合同，因此对当前实现的 full observation 仍 pending，不删除它凑 schema 通过。

固定 scope/asserted 为 facts6/ontology2、reasoning_result/source null、空派生；fresh/project 为 facts9/ontology3，增加 unit 的 Pump/Equipment/HighRiskEquipment，ontology 增 CriticalPump subclass Equipment。完整 selectedFacts 6/9 项、全部 basis、query 全 rows 和 SHACL 两条违规/sourceShape/null 在 cases。fresh prepare 实际 reason=1；project 投影 reason=0，且 source/result 同次、原事实/本体/保留 payload 不可变。这些是需要真实 hook/身份核验的关系，JSON 值相等不能自证。

## 安全错误字段表

每个 rejection 固定 `{kind,complete,harnessStage,diagnostic,partialView,report}`。partialView/report 均显式 null；没有自由错误文本。`harnessStage` 来自固定调度阶段白名单，独立于 canonical exception 的 stage。diagnostic 恰为 `origin/reason/classification/stage/slot/domain/ruleId/location`，全部 required；没有的字段必须 null，不能猜填或省略。

| origin              | 私有声明允许值                                                                                                                                                                                       | 必须保留的类型                                                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| SemanticError       | 此套件安全理由：UNBOUND_RULE_VARIABLE、INVALID_TURTLE、INVALID_LITERAL_LEXICAL、REASONING_SOURCE_REQUIRED（新增）、REASONING_SOURCE_MISMATCH、REASONING_RESULT_INVALID、UNSELECTED_REASONING_PRESENT | 此声明无 classification/stage/slot/domain，均 null；harnessStage 另存                                                  |
| RestoreFailure      | reasons=RESTORE_INPUT_INVALID/EXPECTATION_MISSING/EXPECTATION_MISMATCH/LIMIT/INTERNAL/LEDGER_REUSED；classes=input/expectation/resource/internal                                                     | stage=entry 或 A1…A16；slot=null 或 exact int 0…99；domain=null 或获准 17 字面域                                       |
| DirectStepsFailure  | INVALID/LIMIT/REUSED/INTERNAL，均带 DIRECT_STEPS_ 前缀；分别 input/resource/expectation/internal                                                                                                     | stage=entry/capture/link/encode/restore/roots/receipt/cleanup；domain=null 或 work/scan_copy/objects/scalar；slot null |
| MaterialFailure     | MATERIAL_INVALID/LIMIT/MISMATCH/INTERNAL/LEDGER_REUSED                                                                                                                                               | classification null；stage exact int 0…8；domain=null 或 traversal/scan_copy/hash/scalar/objects；slot null            |
| OfflineAccessDenied | 新 O1 私有类型，固定 EXTERNAL_ACCESS_DENIED                                                                                                                                                          | 其他字段 null；不将任意库异常强称 SemanticError                                                                        |
| Unknown             | 固定 INTERNAL_ERROR                                                                                                                                                                                  | 其他 canonical 字段 null；complete=false；保安全的实际 harnessStage                                                    |

Restore domain 的完整白名单为 wire/schema/traversal/integer/copy/cache_query/cache_split/cache_alloc/rule/pv_compare/hash/scalar/objects/trie_nodes/trie_slots/opaque_scalar/opaque_objects。来自 root 新批准的纯声明依赖，不执行表达式。schema 允许整个安全 finite 集只为保诊断；**逐 ID exact 目标不允许任取一个已知理由**。DirectSteps reason/class 必须满足上表有限函数；RestoreFailure 的四分类是现有声明允许集，不能仅按 reason 自行重写实际分类。

本窗所涉三类 private failure 的声明没有 ruleId/location；两键固定 null。未来 ProfileExecutionFault 的 location/rule_id 不能凭此被删：需要该 API 的另一个明确 version/schema 与全部获准有限字段，当前套件不把未知该类当已匹配。完整返回阶段的所有已有安全诊断保持原件。未预登记 origin/字段/值、非 exact type、外来类或不受信描述符读取失败，都发安全 Unknown/incomplete，不能裁掉不认识的字段再宣称完整已知错误。不得通过 getattr 任意对象、字符串拆解、异常 args/text/堆栈/路径来认错误；受信 adapter 按 exact canonical class/显式字段出口读取。

Unknown 不打印原异常、URL、文件路径、节点、异常 class 自由名或堆栈。collector 的原 stderr/exit/signal 按原安全受控采集约束保存，不嵌到该 JSON。Unknown/incomplete/未开始/未到达均不能 oracle-match；collection exit0 不表示 original operation 成功。

## 首错与最小 deterministic delta

下面是精确**目标提案**，不是从允许异常集合猜测的旧实际值。每个字段的 null、origin、分类/阶段在 cases 中完整展开。

| ID/族                    | 本提案 exact 目标                                                                                             | 权威/未证边界                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| turtle/front-5           | SemanticError / INVALID_TURTLE；harness=parse-data；canonical stage=null                                      | F1：按 Turtle IRIREF 词法拒裸空格，再做合法 IRI 语义检查；旧竖线 IRI 断言不替代此输入，固定库实际分类待验   |
| shape/front-2            | SemanticError / INVALID_LITERAL_LEXICAL；parse-shapes                                                         | F1：SHACL shape 中 typed nni `-1` 先过 datatype 词法/值域门，再约束模板门；旧 data-gate 断言不证明 shape 侧 |
| integer/other-datatype-1 | 同码；parse-data                                                                                              | F1：wide integer 政策只宽化已批准 integer 族，不使非法 nni 负值合法；两侧独立登记                           |
| scope/missing-source     | SemanticError / REASONING_SOURCE_REQUIRED；scope-provenance-gate                                              | F1 新明确 missing-source 私有码；不借三个别的 scope 码外推                                                  |
| scope/wrong-source       | SemanticError / REASONING_SOURCE_MISMATCH；scope-provenance-gate                                              | 旧 L84–105 局部预登记该 code；此 ID 的完整上下文检查与 stage 待验                                           |
| scope/missing-result     | SemanticError / REASONING_RESULT_INVALID；scope-provenance-gate                                               | 旧 L108–119 支持缺失/不完整 code；本 stage 为 F1 固定                                                       |
| scope/unselected-result  | SemanticError / UNSELECTED_REASONING_PRESENT；scope-selection-gate                                            | 旧 L237–247 局部 code；F1 显式先核 include/asserted 组合，后核 source/result                                |
| 14 restore 固定扰动      | RestoreFailure / RESTORE_EXPECTATION_MISMATCH / expectation / A1 / slot=null / domain=null；harness=restore   | R1：新增 receiver integrity preflight 的固定出口，**非 constructor 默认/旧测试证明 actual A1**              |
| dag/turtle-entry         | DirectStepsFailure / DIRECT_STEPS_INVALID / input / entry / domain=null；harness=structured-material-required | D1 新 structured-only entry guard；旧 L556–568 只证明预登记有限拒绝和 reason0，未定 exact class/code        |
| offline/implicit-jsonld  | OfflineAccessDenied / EXTERNAL_ACCESS_DENIED；implicit-loader-guard                                           | O1 新 typed denial 事件；现有 loader 没精确异常投影，仍 pending 真实边界/no-I/O 验证                        |

F1 的 scope 先序为 exact include 类型→asserted 与 result/source/rules 组合→derived result 必需→source 必需→source 完整一致→result 完整一致→project→query/SHACL。不得以 source 缺失触发 fresh reason。坏空格前门需按 token grammar 识别 IRIREF，不能扫全文 regex 导致合法 literal 内同字串误拒。正常 literal、合法 `<urn:ok>`、nni `0/+0/01`、合法 shape-list 是后继 F1 必须保留的边界；本文不实现 parser、也不把这些扩展边界当已测产品。

R1 在原同次成功生产与独立资源准入已成立的前提下，进入 receiver-integrity stage A1，按 payload bytes/length/digest→rows bytes/length/digest→source→definitions→catalog 的固定顺序核原 held expectation；任何不一致统一 exact mismatch，不带具体输入字节/路径。只读接收副本，保原 allocation/expectation/物料。未获准重新绑定 expected，故 14 个 mutation 必须更改至少一个 held 字节身份；如果未来 mutation 实现只是 no-op 或重绑，该 observation 是 fixture/harness 失败，不能算预期拒绝通过。尚未到这个阶段的真实生产/准入/预算错误保首错并记 not-reached/pending，不能接受任意 RESOURCE_LIMIT 代 A1，也不为凑 A1 放宽原 cap、退款或更换 allocation。

这一 R1 最小 preflight 不证明深层 DAG 结构验证覆盖；若将来有**另获准**rebound 结构测试，它会通过字节门再测深层，须另 ID/独立 expected，不能偷换本 14 原输入。禁止把正常 restore 的真 wire 重新签成篡改 expected。新规范的资源收费由独立 fee owner 另给，本文不计算17L/planDigest/budgetUsage、实现阈值或准入，不借构造默认规则证明实际调用。

## 有限比较与手工小例

schema 后再执行逐 ID `exact`：递归 keys/type/null/数组全长/每个末字段/重复与顺序。正常项遇到任意已知拒绝、unknown 或 RESOURCE_LIMIT 都不匹配；拒绝项也只匹配对应 exact origin/reason/stage/class/slot/domain。source 与 package 相等只是独立结论；两者各自还要对独立 expected 及真实来源/完整阶段/计数关系核验。不得把 source 输出固化为 expected。

正常手工例：`x type A` 和 `A subclass B` 只新增 `x type B`；五字段中 rdfsEvidence 的 basis 恰为这两叶，rules/evidence/warnings 皆空。深度2 domain 例有 `p domain A`、`x p y`、`A subclass B` 三叶；x:B 的 basis 必须全三叶，不能因只看 direct premise 就删 p/x 输入。多匹配例 A01、A04 两个匹配产生同 head，图1条但 evidence2条，每条四个有序输入。

边界手工例：raw when `[t,t]` 投影仍两项；两个完全相同 accepted head occurrences 仍两条 evidence。integer01 与 integer1 的 N3 不等；int 与 integer datatype 不等；语言 raw `EN` 不被原件改成 en；shape-list BNode 只整体双射，删最后 rest 边必须不等。scope SHACL 的两条 minCount 违规的 value 都是显式 null，删除 null 或删最后 sourceShape 必须失败。

拒绝手工例：unbound-head 是真实独立数学定义错误，不构造空正常 DTO；missing-source 不能以 mismatch 或任何 resource reason 代；R1 的14项必须 exact proposed A1。raw exceptionText、路径 domain、bool slot、额外 message、未知 stage 均拒 schema；Unknown 固定安全字段且 complete=false，仅作 incomplete 记录。

20 个 stdlib 自测含手写 type/depth2/multiple-matches 断言，全部 37 exact shape/值核验，逐非空数组删除尾项的 mutation，误拒/任意已知拒绝替代、重复 occurrence、输入次序、null/省略、异常泄漏、BNode 全图反例。不把 schema 自测称库、产品、source/package 或生产验证。

## owner、版本、兼容与集成顺序

| owner                        | 最小后继 delta（本窗不实施）                                                                                                                                                                                                            | 兼容和前置                                                                                                                    |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| I05 canonical API owner      | F1 的显式语法/词法/选择首序、missing-source 私有码；D1 structured-only exact entry；R1 完整 receiver preflight；O1 typed offline denial                                                                                                 | 原公共 registry/Q6/date/外联拒绝/权限保持；API 若改变旧输出需新版本入口，不改旧契约来冒通过                                   |
| I05 serializer/harness owner | 新 `i05-observation-projection/1` 选择器；完整五字段/N3+typed 数学对应；新 scope display provenance/content source；exact canonical class 适配；安全 Unknown；完整先前返回阶段原件及实际 hooks                                          | 不按 key 猜版本，不截 /2 /3 成五key，不将新 contentSource 反喂旧 helper；旧原始 provenance 继续完整保存，未定编码保持 pending |
| T05 oracle owner             | 新 `observationProjectionVersion`、每个 ID 的完整 `expectedProjection`、`expectedProjectionSourceRefs`、`firstErrorAuthority`、`projectionPendingFields`、`finiteRelations`/`preconditions`；保旧 input sourceRefs 与数学 expected 分离 | 37 项逐一接收本文件实际 commit 和 hash；旧137 pending 不批量改绿。legacy11 是10正常+1拒绝；wholeOracleComplete 仍 false       |
| root/来源与预算 owner        | 接收明确组合、真实原 allocation/capture/issuer/完整预算准入、旧 source metadata 完整载体；后继隔离 runtime 票                                                                                                                           | 本设计的内容 hash/schema 不替代权限或发行凭据；API 默认 `rules=()` 不证明实际调用省略参数、实际 fee/capture                   |

顺序：先独立审查本 candidate→owner 按项接收版本/首错与来源载体→唯一 I05 writer 提交新 API/serializer、独立 fee 规范接收并组成固定组合→T05 独立适配完整字段→后续获准 source 与 package 实测及独立比较。真实库分类没有证据前保 pending；旧首失败/unknown 不重写。再按原正式 Job/Store/selected/whole-H、CI、目标两 OS、真人与指定双模型门验收；不 push/merge，不替代 Goal。

本窗没有实施 packages/scripts/tests/共享契约/CI，没有使用业务编译、第三方库、build、native/DB/GUI/网络/安装或模型；不修改原数学、capture/原 allocation、调用权威、公共四字段错误边界或保护 AGENTS。
