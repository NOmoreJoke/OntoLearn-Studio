# R3 投影规范：T05 只读收件与差距

本轮接收 `50317c791eca95e82dfbfaa2ef71c0dfc95a9302` 的固定 R3 设计作为后续规划输入，设计 candidate 为 `49e55cfdc68adca7f04faaf4f2335d1072553045`。T05 原冻结交付仍为 `77852d27a3c4e84867a42f243e0f4e0f32b8df67`，280 specified／137 pending，wholeOracleComplete=false。本轮只新增本 receiving 前缀及对应 review 前缀文档；不实施 serializer／comparator，不改变旧 oracle／golden／脚本／运行证据。

六件固定源的 bytes/SHA/行数和 root 限定收件记录身份在 `docs/reviews/T05/projection-R3-receiving/source-receipt.json`。已全文读取 closure、spec、model、coverage、R3 报告，完整解析 schema/cases 并逐字段绑定原输入；AST 只静态解析 model，没有 import／执行模型、其 selftest、产品、新 oracle 或生成 actual。R3 报告中的41方法、92次逆序／154次重复等来自其独立审者，T05 本轮没有重跑。源历史 full diff check 的 exit2 和旧R1/R2 Fail保持，不宣称源历史全部检查绿。

## 逐项范围

37项精确覆盖13正常／24拒绝：10个正常legacy、3个正常scope、1个unbound-head、14个restore、7个前门、1个DAG text、1个implicit loader。与本线137 pending交集只有36；`legacy/unbound-head` 已是旧 specified 拒绝，不能当新增关闭。其余101 pending为82 profile完整费用／准入、18其他生产／DAG／fullview、1个 `rdfs/ten-ontology-suite` 正常legacy。R3未登记该第11个正常legacy的完整target，不能把“legacy域11个ID”写成11个正常DTO，或由通用schema外推通过。

- `37-receiving-matrix.json`：每ID的固定case指针／完整子树hash、旧字段缺口、API/参数/阶段、拟定diagnostic、前置／来源／remaining requirements和不关闭标志。
- `137-gap-ledger.json`：原137项完整有序字段缺口逐项保留；36项标本轮有设计输入，101项明确无R3完整target，全部仍pending。
- `85-graph-slot-index.json`：独立静态JSON字段枚举85个graph槽；含逐case路径、模式、行数与子树hash，仅作结构登记，不是执行model.projection_layout或canonical/matches的验证。
- `gap-table.md`：37项人读对照与整体后继责任。机器账不以摘要代替完整源target；不把文档子树hash当真实payload/issuer摘要。

10个legacy `independentTypedMath` 完整对象与旧oracle.math精确相等。3个scope数学侧车与旧业务数学相等，但不包括旧 `semanticState/reasoningReceipt`：asserted的receipt仍null，fresh/project仍要求同次prepare原样result/source对象。该真实关系必须单独保留，不能因新display DTO不带此字段而删除。其他24拒绝侧车为null；restore的旧完整businessMath与真实前阶段原件要求也未被这些拒绝terminal取代。

## 接收设计与明确实施差距

| 面 | 本轮接收的固定设计要求 | 当前差距及后继责任 |
| --- | --- | --- |
| 完整入口 | `matches`：expected schema→observed schema→expected本端全部graph wire→observed本端全部graph wire→全terminal身份比较 | 旧T05只有自身语义关系／类型检查，没有该完整投影consumer。未来适配必须显式调用完整入口或另获批准的等价有界实现；本轮不复制或调用模型函数 |
| 85图槽 | typed facts/ontology、N3 rdfs/rules及全部rdfs/evidence/provenance basis；schema required/exact type/keys/null只是第一门 | 后继consumer要保完整布局和每端原wire独立检查，不能只测一个顶层图或schema通过 |
| 本端wire | 原N3完整三元组key Unicode升序；RDF identity唯一；不预排序／去重修复。EN/en两成员JSON不同仍重复 | 旧独立业务图集合不等于新serializer wire。未来新增版本／字段，不能重排旧golden来绕过bad wire；expected端同样须验 |
| 有限表示 | typed exact keys/UTF8/IRI/位置；N3单生成token严格roundtrip，xsd:string用plain，非法escape/空language等拒绝 | 不是Turtle parser或数值/date值验证，不扩大Q6/date/ill_typed范围，也不是完整RDF表达／产品容量证明 |
| 统一BNode域 | 同一不可变terminal/artifact的typed图、N3证据、query cells、SHACL六term槽共享一次双射；图集合与有序occurrence分开 | 实际graph→query/SHACL归属绑定仍缺，跨parse/producer不能凭label并域；不逐字段各求同构。最多8BNode只是模型界，更大域须另批有界比较器 |
| 原文/source/摘要 | raw TermInput/source/null、规则定义、ID、warning、内容摘要及未声明槽全部exact；仅明确RDF身份language casefold | 不alpha-renaming raw `_:`字符串或lower lexical/IRI/datatype/source。所有实际preimage仍核原完整bytes；BNode合法改名造成digest差异的兼容仍需单独版本／关系，不能忽略hash |
| legacy DTO | 五键完整；rdfs/rules图，rdfsEvidence完整leaf basis；accepted每head occurrence各evidence，inputs保原顺序重复 | 新N3/evidence排序属于私有serializer提案；需I05明确版本/实现、T05完整target/数学侧车关联和实测。10正常不包括未登记ten-ontology-suite；原所有when/comparison/head/basis/source不丢 |
| scope display | 新provenance/content-source /1、完整facts/ontology/query/SHACL及selectedFacts所有sources/derivedAxioms | contentSource非旧reasoningSource入参／authority；旧metadata完整编码与真实同次handle/issuer还缺，fresh1/project0真实hook待验。SHACL旧业务多重集政策不能被新terminal有序数组悄改 |
| API/defaults | shape双parse→check的3步和integer显式validate_shacl_text映射已逐字登记 | cases仅这2项带完整invocation对象；其他35项虽有API名称/参数和合同依据，未来实际caller仍需完整已批准参数／返回／阶段关联。签名默认rules=()不证明本次省略，不猜wrapper／strict fallback |
| 拒绝字段 | 私有origin/reason/classification/stage/slot/domain/ruleId/location全部required；canonical stage与harnessStage分开 | 需I05 exact受信class字段出口；构造器默认／允许枚举不证明首错。未登记ProfileExecutionFault另需版本，不能裁安全字段强称已知 |
| 安全Unknown | exact str stage前门；非法stage仅collection-failure/Unknown/INTERNAL_ERROR/complete=false；不摸外来eq/hash/getattr/str/repr | collector安全完整阶段保留与实际adapter还未实现；Unknown/incomplete/未达与collection0都无oracle-match许可。公共ErrorFrame四键不增加私有字段 |
| F1/D1/O1 | 7前门、structured-only、typed no-I/O denial的逐ID exact目标 | 是新的确定先序/API技术目标；旧库分类／实际调用未证，不能靠旧邻近断言或库异常文本填码。需I05唯一owner实施并获准实测 |
| held A1 | 14项用原held expectation逐payload→rows→source→definitions→catalog核bytes/length/digest；统一expectation/A1/slot/domain null | 先要原生产成功、真实allocation/expectation、完整阶段原件与资源准入。任一早错保首错/not-reached；实际mutation必须改绑定bytes且不得rebind。不借A1声称深DAG结构覆盖 |
| 完整阶段 | 拒绝terminal partialView/report=null；此前已成功返回阶段原件仍全量保留 | 旧生产payload/rows/sidecars/typed图/metadata carrier等完整codec、实际issuer/捕获/全账单仍缺。本terminal schema不代表整份harness日志完整 |
| 137/417与费用 | 本规范37targets/19datasets设计输入；原417独立数学和原操作未执行权威保持 | 82profile费用、32生产typed/capture/费用、26声明metadata等旧字段仍各自pending；无feeWIP、17L/planDigest/usage造值，无运行票/父门关闭 |

## 两项已登记调用及版本边界

`shape/front-2` 保原parameters={}。先parse data（format=turtle, shapes=False）完整返回dataGraph，再parse shapes（shapes=True）拟定在parse-shapes拒绝；check_shapes未到达，但第0步完整图保留。`integer/other-datatype-1` 对dataText/shapesText调用validate_shacl_text，显式data_policy=integer-illtyped-report-v1、range_policy=legacy，保camelCase源参数映射；不fallback strict。宽化只限data object exact xsd:integer ill_typed，不扩int/nni/decimal/shape。签名、固定调度和真实首错是三层证据。

源case容器`i05-observation-projection-cases/1`与显式`projectionSpecVersion=i05-observation-projection/2`同时保留，schema ID为`urn:ontolearn:private:i05-observation-projection:2`。未来T05新字段可包括observationProjectionVersion、expectedProjection、expectedProjectionSourceRefs、firstErrorAuthority、projectionPendingFields、finiteRelations/preconditions；本轮只登记需接收内容，不把这些字段写进旧oracle或JSONL契约。input sourceRefs、独立数学与新增设计权威必须分列。

图hash有独立域：固定资产投影仍按旧ASCII canonical；本提案display/content-source preimage按ensure_ascii=false/sorted compact UTF8及指定domain；真实payload/rows/sidecar按各自原bytes。不能用一种canonical替代所有域，也不能拿source code SHA填bundle代码证明。

后继顺序为root明确owner/API/serializer/来源与费用组合→唯一I05 writer实施和完整调用验证→授权T05版本化字段适配及完整入口验证→获准source/package实际观察和独立对expected比较。单纯设计Pass不关闭任何137、正式Job/selected/wholeH/SQLiteHOLD/S1/B1、指定双审/CI/两OS/真人/develop门。本线没有桌面短lease，不创建指定任务；全线指定审查积压另以真实证据登记。
