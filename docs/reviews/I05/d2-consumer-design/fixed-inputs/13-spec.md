# I05 私有观察投影规范提案 v2（R3 wire 门修订）

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

| ID/族                    | 本提案 exact 目标                                                                                             | 权威/未证边界                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| turtle/front-5           | SemanticError / INVALID_TURTLE；harness=parse-data；canonical stage=null                                      | F1：按 Turtle IRIREF 词法拒裸空格，再做合法 IRI 语义检查；旧竖线 IRI 断言不替代此输入，固定库实际分类待验                   |
| shape/front-2            | SemanticError / INVALID_LITERAL_LEXICAL；parse-shapes                                                         | F1：SHACL shape 中 typed nni `-1` 先过 datatype 词法/值域门，再约束模板门；旧 data-gate 断言不证明 shape 侧                 |
| integer/other-datatype-1 | 同码；parse-data                                                                                              | F1：只宽化 data object 的 exact xsd:integer ill_typed；xsd:int/nonNegativeInteger/decimal 与 shape 侧都不宽化；两侧独立登记 |
| scope/missing-source     | SemanticError / REASONING_SOURCE_REQUIRED；scope-provenance-gate                                              | F1 新明确 missing-source 私有码；不借三个别的 scope 码外推                                                                  |
| scope/wrong-source       | SemanticError / REASONING_SOURCE_MISMATCH；scope-provenance-gate                                              | 旧 L84–105 局部预登记该 code；此 ID 的完整上下文检查与 stage 待验                                                           |
| scope/missing-result     | SemanticError / REASONING_RESULT_INVALID；scope-provenance-gate                                               | 旧 L108–119 支持缺失/不完整 code；本 stage 为 F1 固定                                                                       |
| scope/unselected-result  | SemanticError / UNSELECTED_REASONING_PRESENT；scope-selection-gate                                            | 旧 L237–247 局部 code；F1 显式先核 include/asserted 组合，后核 source/result                                                |
| 14 restore 固定扰动      | RestoreFailure / RESTORE_EXPECTATION_MISMATCH / expectation / A1 / slot=null / domain=null；harness=restore   | R1：新增 receiver integrity preflight 的固定出口，**非 constructor 默认/旧测试证明 actual A1**                              |
| dag/turtle-entry         | DirectStepsFailure / DIRECT_STEPS_INVALID / input / entry / domain=null；harness=structured-material-required | D1 新 structured-only entry guard；旧 L556–568 只证明预登记有限拒绝和 reason0，未定 exact class/code                        |
| offline/implicit-jsonld  | OfflineAccessDenied / EXTERNAL_ACCESS_DENIED；implicit-loader-guard                                           | O1 新 typed denial 事件；现有 loader 没精确异常投影，仍 pending 真实边界/no-I/O 验证                                        |

F1 的 scope 先序为 exact include 类型→asserted 与 result/source/rules 组合→derived result 必需→source 必需→source 完整一致→result 完整一致→project→query/SHACL。不得以 source 缺失触发 fresh reason。坏空格前门需按 token grammar 识别 IRIREF，不能扫全文 regex 导致合法 literal 内同字串误拒。正常 literal、合法 `<urn:ok>`、nni `0/+0/01`、合法 shape-list 是后继 F1 必须保留的边界；本文不实现 parser、也不把这些扩展边界当已测产品。

R1 在原同次成功生产与独立资源准入已成立的前提下，进入 receiver-integrity stage A1，按 payload bytes/length/digest→rows bytes/length/digest→source→definitions→catalog 的固定顺序核原 held expectation；任何不一致统一 exact mismatch，不带具体输入字节/路径。只读接收副本，保原 allocation/expectation/物料。未获准重新绑定 expected，故 14 个 mutation 必须更改至少一个 held 字节身份；如果未来 mutation 实现只是 no-op 或重绑，该 observation 是 fixture/harness 失败，不能算预期拒绝通过。尚未到这个阶段的真实生产/准入/预算错误保首错并记 not-reached/pending，不能接受任意 RESOURCE_LIMIT 代 A1，也不为凑 A1 放宽原 cap、退款或更换 allocation。

这一 R1 最小 preflight 不证明深层 DAG 结构验证覆盖；若将来有**另获准**rebound 结构测试，它会通过字节门再测深层，须另 ID/独立 expected，不能偷换本 14 原输入。禁止把正常 restore 的真 wire 重新签成篡改 expected。新规范的资源收费由独立 fee owner 另给，本文不计算17L/planDigest/budgetUsage、实现阈值或准入，不借构造默认规则证明实际调用。

## 有限比较与手工小例

schema 后分别核 expected/observed 全部 graph 槽各自 wire 的完整 N3 升序、RDF identity 唯一性和既定表达限制，之后才按 `projection_layout` 确定唯一 RDF 身份域，再执行逐 ID 完整比较：RDF 图按集合；有序 RDF occurrence 保数组全长/每个末字段/重复与顺序；其余 keys/type/null/字段逐一 exact。正常项遇到任意已知拒绝、unknown 或 RESOURCE_LIMIT 都不匹配；拒绝项也只匹配对应 exact origin/reason/stage/class/slot/domain。source 与 package 相等只是独立结论；两者各自还要对独立 expected 及真实来源/完整阶段/计数关系核验。不得把 source 输出固化为 expected。

正常手工例：`x type A` 和 `A subclass B` 只新增 `x type B`；五字段中 rdfsEvidence 的 basis 恰为这两叶，rules/evidence/warnings 皆空。深度2 domain 例有 `p domain A`、`x p y`、`A subclass B` 三叶；x:B 的 basis 必须全三叶，不能因只看 direct premise 就删 p/x 输入。多匹配例 A01、A04 两个匹配产生同 head，图1条但 evidence2条，每条四个有序输入。

边界手工例：raw when `[t,t]` 投影仍两项；两个完全相同 accepted head occurrences 仍两条 evidence。integer01 与 integer1 的 N3 不等；int 与 integer datatype 不等；语言 raw `EN` 不被原件改成 en；shape-list BNode 只整体双射，删最后 rest 边必须不等。scope SHACL 的两条 minCount 违规的 value 都是显式 null，删除 null 或删最后 sourceShape 必须失败。

拒绝手工例：unbound-head 是真实独立数学定义错误，不构造空正常 DTO；missing-source 不能以 mismatch 或任何 resource reason 代；R1 的14项必须 exact proposed A1。raw exceptionText、路径 domain、bool slot、额外 message、未知 stage 均拒 schema；Unknown 固定安全字段且 complete=false，仅作 incomplete 记录。

20 个 stdlib 自测含手写 type/depth2/multiple-matches 断言，全部 37 exact shape/值核验，逐非空数组删除尾项的 mutation，误拒/任意已知拒绝替代、重复 occurrence、输入次序、null/省略、异常泄漏、BNode 全图反例。不把 schema 自测称库、产品、source/package 或生产验证。

## owner、版本、兼容与集成顺序

| owner                        | 最小后继 delta（本窗不实施）                                                                                                                                                                                                            | 兼容和前置                                                                                                                    |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| I05 canonical API owner      | F1 的显式语法/词法/选择首序、missing-source 私有码；D1 structured-only exact entry；R1 完整 receiver preflight；O1 typed offline denial                                                                                                 | 原公共 registry/Q6/date/外联拒绝/权限保持；API 若改变旧输出需新版本入口，不改旧契约来冒通过                                   |
| I05 serializer/harness owner | 新 `i05-observation-projection/2` 选择器；完整五字段/N3+typed 数学对应；新 scope display provenance/content source；exact canonical class 适配；安全 Unknown；完整先前返回阶段原件及实际 hooks                                          | 不按 key 猜版本，不截 /2 /3 成五key，不将新 contentSource 反喂旧 helper；旧原始 provenance 继续完整保存，未定编码保持 pending |
| T05 oracle owner             | 新 `observationProjectionVersion`、每个 ID 的完整 `expectedProjection`、`expectedProjectionSourceRefs`、`firstErrorAuthority`、`projectionPendingFields`、`finiteRelations`/`preconditions`；保旧 input sourceRefs 与数学 expected 分离 | 37 项逐一接收本文件实际 commit 和 hash；旧137 pending 不批量改绿。legacy11 是10正常+1拒绝；wholeOracleComplete 仍 false       |
| root/来源与预算 owner        | 接收明确组合、真实原 allocation/capture/issuer/完整预算准入、旧 source metadata 完整载体；后继隔离 runtime 票                                                                                                                           | 本设计的内容 hash/schema 不替代权限或发行凭据；API 默认 `rules=()` 不证明实际调用省略参数、实际 fee/capture                   |

顺序：先独立审查本 candidate→owner 按项接收版本/首错与来源载体→唯一 I05 writer 提交新 API/serializer、独立 fee 规范接收并组成固定组合→T05 独立适配完整字段→后续获准 source 与 package 实测及独立比较。真实库分类没有证据前保 pending；旧首失败/unknown 不重写。再按原正式 Job/Store/selected/whole-H、CI、目标两 OS、真人与指定双模型门验收；不 push/merge，不替代 Goal。

本窗没有实施 packages/scripts/tests/共享契约/CI，没有使用业务编译、第三方库、build、native/DB/GUI/网络/安装或模型；不修改原数学、capture/原 allocation、调用权威、公共四字段错误边界或保护 AGENTS。

## R2 delta：采集安全、共享 BNode 域和明确调用链

R1 报告的 Fail 保留。v2 对私有 terminal schema 的唯一结构扩展是保留的安全 stage `collection-failure`，以及明确的合法链阶段 `check-shapes`；schema ID 为 `urn:ontolearn:private:i05-observation-projection:2`。case 容器仍 `/1`，另有明确 `projectionSpecVersion=i05-observation-projection/2`，37 个 `expectedProjection` 与独立数学保持原完整值，禁止靠新增 key 猜版本。后继 serializer owner 须显式选择 /2；旧 /1 只在固定旧 candidate 解释，不默默接收新 stage。

`unknown` 与 `safe_projection` 都先对 harnessStage 做 **exact str 类型且有限白名单**检查，再处理 diagnostic。正常集合为 reason/rule-definition/scope/restore/structured-material-required/parse-data/parse-shapes/scope-provenance-gate/scope-selection-gate/implicit-loader-guard/check-shapes。非 str、str 子类、路径、URL、未知字符串或外来对象均不得被复制、比较、hash、getattr、str 或 repr；只返回字面 `harnessStage="collection-failure"`、Unknown/INTERNAL_ERROR、complete=false。该保留 stage 只允许 Unknown/incomplete，不能出现在 complete=true 的已知拒绝，也不能匹配任一 37 项。合法阶段的 Unknown 保原有限阶段。collector 完整记录此安全 incomplete 终态和此前已返回的完整阶段原件；不能补回非法 stage 文本。这里不创建新的公共码或 ErrorFrame 字段。

`projection_layout` 明列整个 terminal artifact 的 RDF 位置；同一 terminal 内以下位置共享 **同一个** BNode 标签双射，不能逐字段、逐行或逐列表片段各自挑映射。身份域只在这一实际不可变 artifact 内；跨独立 parse/producer artifact 的节点不能凭相同字面 label 合并；若 query/SHACL 消费该图，其 term references 明确归此图所属同一 artifact。实际 harness 必须提供这一 graph→consumer 关联，未绑定的不同图不进入同域，仍 pending。

| 位置                                                                                             | 比较模式与域                                                                                                                   |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| scope facts/ontology typed 图                                                                    | 同一域、RDF 集合；仅 literal.language 身份 casefold                                                                            |
| legacy rdfs/rules；scope.reasoning_result 的同字段                                               | 同一域、N3 三元组集合                                                                                                          |
| rdfsEvidence.result/basis；evidence.result/inputs/basis                                          | 同域；result/inputs 是有序位置（inputs 的重复与全尾项保留）；basis 是完整图集合；evidence 外层 occurrence 数组仍有序且重复保留 |
| provenance.selectedFacts.triple、所有 sources 的 inputs/basis；derivedAxioms.triple/source.basis | 同域；triple/inputs 有序、basis 为集合，source 列表及其规则身份 exact                                                          |
| query.rows 的每个非 null typed cell                                                              | 同域、二维有序序列；变量名/列序、null 和重复 rows 保留                                                                         |
| SHACL violations 的 focus/path/value/sourceShape/constraint/severity                             | 全部 RDF term 引用同域；value=null 保留；当前已登记 terminal 的 violation 外层数组完整有序，本次不另放宽其排序                 |
| raw 输入/occurrence/source 原文、规则定义、ID、warnings、内容摘要及其他非 RDF 槽                 | 不做 alpha-renaming、不 casefold，完整 exact；raw JSON 的 `"_:a"` 字符串也不是自动发现的 node 引用                             |

`identity_domain_equal` 收集所有明确槽中的 BNode 标签，求一次全域双射并应用到**全部**槽；图模式比较完整集合，序列模式递归保 keys/类型/null/顺序/重复，未声明位置 exact。N3 槽只识别完整 `_:label` token 和完整生成字面量 token 的 language 后缀；不对 IRI、datatype、lexical、source 或含 `@EN` 的普通文本全量 lower。`projection_identity_equal` 将上述 layout 应用于整个 terminal，`matches` 在严格 schema 后调用它。单图 `graph_isomorphic` 与图函数使用相同 language identity。两者均为最多 8 个 BNode 的有限数学模型；超过小例域拒比较并保 pending，不能称产品限额或推导容量。后继实际 comparator 若支持更大域须另获准有界实现，不得以每字段各求同构绕过全域限制。

独立数学联合例同时含 typed 图、N3 evidence、重复有序 inputs、query cells、SHACL sourceShape：a→p、b→q 在所有位置一致才通过；只将 query/evidence/sourceShape 任一处的 a 指向 q 即不通过，即使各片段分别同构、两端全局节点数量相同。另有合法 `_:a first "hello"@EN; rest nil` 对 `_:p ...@en` 正常例，删 rest 尾、折叠节点、lexical01/1、int/integer 都不等。raw EN/source/null 不被修改或宽化。这些是纯数学边界，不能作为产品接收带 BNode 数据事实的批准。

所有实际 payload/rows/sidecar/source 摘要仍必须分别核各自完整原始 preimage，不能因 BNode 比较放弃 hash。此模型对摘要字段仍 exact；若将来合法运行域的 digest 因各端生成 BNode label 而不同，需要 owner 单独接收明确 preimage 关系与新版本，不得一般忽略摘要或用本双射伪造发行凭据。本窗不关闭这一 pending，也不创建虚假成功 capture。

两项调用的 `invocation` 在 cases 中逐步登记：

- `shape/front-2`：按固定 ee2b 合同实际 L51，`semantic.parse_turtle(dataset.dataText,format="turtle",shapes=False)` 得 dataGraph；随后 `semantic.parse_turtle(dataset.shapesText,format="turtle",shapes=True)` 得 shapesGraph；只有两者完成才 `semantic.check_shapes(dataGraph,shapesGraph)`。原 input parameters 仍 `{}`，没有额外 input policy。F1 精确目标在第二步 parse-shapes 拒绝，因此 check_shapes 未到达；所有已成功返回的第一步 dataGraph 全量保留。L52 是相邻 integer 行，不能混用行号当 source 权威。
- `integer/other-datatype-1`：按同合同 L52，`semantic.validate_shacl_text(dataset.dataText,dataset.shapesText,data_policy="integer-illtyped-report-v1",range_policy="legacy")`；完整映射 `parameters.dataPolicy→data_policy`、`parameters.rangePolicy→range_policy`，值逐字保留，无默认 strict fallback。F1 目标仍 parse-data / INVALID_LITERAL_LEXICAL；真实库分类未证。

这两项不新设 `semantic.validate` wrapper；批准入口名称、阶段、参数及新 F1 首序分开。其 owner 均为 I05 canonical API/serializer owner，接收和实际实现/调用验证继续 pending；没有读实际函数体来补签名或执行链。`integer-illtyped-report-v1` **仅**放宽 data object 的 exact xsd:integer ill_typed，交真实 Datatype 报告；xsd:int、nonNegativeInteger、decimal 及 shape 侧都不随之宽化，旧 parse/query/reason/check 的 strict 不变。未改 Q6/date/外联/公共 registry/权限。

新 `selftest-r2.py` 保留原20方法的独立名称，并新增针对 R1 三发现及联合域的测试。旧 selftest/双流/20通过只属于 R1 的覆盖，未改写为包含这些新反例。R2 的实际命令/分离双流与结果另存新证据，仍是 stdlib 设计验证，独立审查结论由 root 另派 R2 审者给出。

## R3 delta：各端 wire canonical 门先于集合身份

R2 的 Fail 与所有原件保留。R3 兑现 v2 已规定的 canonical 输出约束，没有改变37个完整目标、输入/hash/source/math、JSON字段或私有 `/2` 格式，也未修改公共schema/registry、Q6/date、错误政策或权限。新候选仍需 owner 按实际 ref 接收，不把此修订称已实现产品行为。

完整 wire 比较入口是 `matches`，顺序固定为：

1. 对 expected 和 observed 各自执行严格 schema。完全相同 JSON 图成员重复已有 `uniqueItems` 拒绝，这个有效门保留。
2. 对每端独立用其自身 `projection_layout` 找到**全部** typed-graph/n3-graph 槽，执行 `canonical_graph_slots`。先核表达，再核该端原标签/原语言拼法下的完整三元组 N3 key 升序，并核完整 RDF identity 唯一性。不改输入数组，不先排序/去重来修复它。
3. 两端各自 canonical 后，才调用 `projection_identity_equal` 作同 artifact 的共享全域 BNode 双射及其余完整值比较。映射后的图可以按集合比较；不能把映射后的顺序倒推成原 wire 合法，也不能逐下标 raw exact 拒掉合法交叉改名。

typed graph 的本端 key 为 `(n3(subject),n3(predicate),n3(object))`，N3 graph 的 key 为三项已验证的原 token。按 Unicode code point 比较完整 key，不只比主语或前缀。identity key 保完整 IRI/lexical/datatype及本端BNode标签，只对 language 身份 casefold，plain string为xsd:string身份。两个不同 JSON 成员 `"hello"@EN`、`"hello"@en` 即使本端已排序，仍是同一 RDF 成员，必须拒绝；不能靠 `uniqueItems` 或集合化吞掉别名。单独一个 EN 拼法仍可以和 en 作身份比较，原文/source 不被改写。

有限 typed/N3 表达门也独立于 identity：typed term 必须是既定 exact keys/type、合法 UTF-8 字符串；IRI/ datatype 为完整绝对 IRI，N3 IRIREF 禁用字符不接受；blank label 保既定有限字符域；lang literal 要完整 language tag 与 rdf:langString 对应，无 language 则不是 rdf:langString；subject不得literal，predicate必须IRI。**不计算** numeric/date datatype 值，不改变 ill_typed、Q6、date或前门业务政策。

N3 门只读取本 serializer 已定义的**单个生成 token**，不是 Turtle parser 或完整 RDF 库。literal 的 quoted lexical 使用原规定的 JSON double-quote/escape 生成规则；`n3(decoded_token)==原token` 必须成立。simple/xsd:string 输出为 plain string，因此显式 `^^xsd:string` 虽可能 RDF 等价，仍不符合本 wire 拼法；非规范 `\u0068ello` 代 `hello`、未转义控制字符、坏 IRIREF/label、空language等同样拒绝。schema 的 string 形状若仍放行这些值，不能替代此门。source原文里的escape、typed词法、语言大小写和重复occurrence完全保留，此门不对它们进行修复或重编码。

`projection_identity_equal`、`identity_domain_equal`、`graph_isomorphic` 是**数学身份关系**，可以处理一个集合的不同枚举方式；它们不是完整 wire 接收器，不能直接用于 harness/oracle-match。R2已有抽象同构/布局测试继续只证明该身份关系。所有 consumer 必须使用 `matches` 的 schema→两端wire→共享映射顺序；不把 identity-only=true 当成 wire 通过。

新手写反例对 rdfs/cycle 的8条rdfs、rdfs/domain-depth2的3叶basis、scope/fresh的9条facts分别逆序：schema仍合法，数学identity仍可相同，完整入口必须拒绝；expected端同样逆序也拒绝。37个原目标的85个graph槽本来均canonical，无需改golden。另有已排序的typed/N3 EN/en别名、完全相同JSON重复和schema仍放行的显式xsd:string/escape/控制符表示反例。

合法交叉改名正常例为左 `[a→x,b→y]`、右 `[p→y,q→x]`：各端分别按原标签升序，统一双射 a→q/b→p 后相等，完整入口必须通过（typed和N3均有小例）。when/heads/evidence/source等有序occurrence不被新门排序/去重；重复inputs和evidence可保留，删除任何尾项仍拒绝。raw/source和quoted lexical仍exact。小例只证明有限serializer/comparator边界，不证明合法产品scope、摘要绑定、capture/来源或资源准入。

R3不改旧32方法与其双流，新 `selftest-r3.py` 承接32回归并增加独立字面测试；实际次数、结果、首失败及分离双流另见新R3证据。R1安全stage、精确API映射、language identity与共享双射保持；所有库/费用/runtime/来源/旧metadata pending不变。独立R3结论由root另派审者给出，作者不自定Pass。
