# B1 同源包输入与完整覆盖调查

2026-10-22。**目前可制定同源包验收，不能用旧83数学投影或date三个输入代表完整B1。** 本件是独立只读调查和case建议，不是主合同、可执行probe、输入包或运行通过证明。仅新增本文件；没有运行产品、第三方库、测试、CLI、构建、安装、DB、GUI、native、模型或外部审查，也未创建树/Goal。root维护合同与JSON索引，本件不重复包装guard差异调查。

## 固定来源与原B1/S1要求

可写树为 `I05-source-package-contract`，分支 `docs/I05-source-package-contract`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。AGENTS是受保护未暂存操作副本，不参与本件写入。全文读本窗 preparation、setup、operating-AGENTS/common、I05 shape/整数/date收件、T05 date收件与T03 offer准备原件；另读T03固定 `4fa5d62eb13269351384527b1f84761c08811e79` 的 `docs/iterations/T03/I05-profile-build-dependency-offer.md`，以及T05固定 `525c91717c07dc4b386fcec00f897e1e6a75caf1` 的date README/receipt/独审。历史收件是引用证据，作者未重跑这些组件。

产品调用依据固定 `6891a5842302859a531cf82767c5a482417bc274`，供应树 `I05-shacl-date-policy` 当前纯过程 HEAD `f79a29f596b2444cba542a906c91727869014886`。下文产品行号均指6891 Git，不是新docs树的旧5f实现。只有必要命名小源、原83 JSON、C原件及原上下文输入作静态读取；没有展开493旧过程或旧大包。

PRD `docs/prd/PRD-本体学习与落地Agent工作台.md`：FR-500 L398–402要求明确验证数据范围/是否推导/版本，unsupported不能叫passed；FR-501 L404–415固定先RDFS再独立一阶段规则、无规则反馈；FR-502 L417–421要真实依据；FR-504 L427–431是有限SHACL模板；附录C L959–979限定IRI/字面量、四类有限RDFS、SELECT/ASK、直接path与inclusive子集；G验收要求完整结果，不是数量；PRD L744、827、835、875规定固定输入/输出、查询/约束及打包必要性。本文不据这些条款开放更多标准能力。

原架构 `m0-review-and-update-plan-2026-10-19.md` 的B1 L155–161要求：源环境真实Turtle、只读query、RDFS/受控规则、SHACL，随后包内运行同一样例；检查隐式导入/资源插件/动态库/许可证，以及SERVICE、FROM和解析/验证器隐式外联拒绝；记录包体/冷暖/峰值/规模/设备/版本。S1 L53要求至少两档、独立对象命名空间、稳定种子、真实数量/输入及查询摘要、冷暖/重复/方法，失败或中止也记录，不设未经Q5确认的容量线。

**架构原件定位边界：** 该架构路径不在6891或本docs树5f的Git中。本轮实际读的是 `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/architecture/m0-review-and-update-plan-2026-10-19.md`，35812B，SHA256 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`；其头部自述核查基线e628f5e。不能伪造6891文件ref，主合同宜将该原件字节作为历史需求绑定，或由总控补准确归档ref。本文只使用上述明确B1/S1条款。

## 1. 原83输入：实际能表示什么

固定 `docs/iterations/I05/profile-probe-inputs.json` 为1839011B/SHA `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de`，格式 `i05-profile-input-projection/1`，`fixedOriginalRef=f9af899fad31ea19c7540e9624c437a189b8b5bf`，`expectedIncluded=false`。全文JSON解码并核结构：

| 指针 | 实际数量/意义 | 不能据此宣称 |
| --- | --- | --- |
| `/mathInputs` | 83份输入，索引0–82 | 83个原操作或83个全业务通过 |
| `/mathInputs/*/eligibleStandaloneMathInput` | true82/false1 | 82份都具备完整原场景 |
| `/mathInputs/*/input/fullOriginalInputContext` | true79/false4；与eligible交集78 | full标志等于Job、source认证或已提交快照 |
| `/productCases` | 50个原产品案例引用 | 50案例已执行 |
| `/learningChecks` | 54个学习check引用，checkExecuted全部false | 课程任务数或全57P0 |
| `/originalOperations` | 106个setup/step操作引用，originalOperationExecuted和lifecycleExecuted全部false | 查询、验证、映射、回滚、行为、重放等已发生 |
| `/sourceFiles`、`/decodedInputJsonFiles` | 22份来源描述、9份输入JSON描述 | 应把22文件连expected整份喂probe |
| 每个math input的三个状态位 | lifecycleExecuted/originalRequestedOperationPassed/sourceAuthorityAuthenticated全false | 数学成功能修改这些原权威边界 |

83的索引分区可直接给主索引定位：0–3是G-base/G-behavior/G-map-empty/E.5 baseline；4–54是原案例操作的文字事实/规则折叠；55–76是22扩展（18格integer比较与JOIN/MULTI/DISABLED/MISSING四格）；77是transfer:repair；78是transfer:classification；79–82是四轮E.5事件片段。

旧canonical probe `semantic_profile_probe.py:167–245` 只将 `input.asserted/ontology` 的triple、`definitions`的when/comparisons/heads/revision/definitionJsonValueSha256、disabled_rule_ids解成真实TermInput/RuleSpec，再在L295调用 `execute_profile_records`。新SourceRecord指向该固定投影asset的JSON字段（L178–194），不是原CSV/Turtle token/byte span或已认证Store来源。

旧probe L289–291对索引77作not-executed/ORIGINAL_INPUT_CONTEXT_INCOMPLETE并设置failed；L303–305保留真实ProfileExecutionFault.error及diagnostic；末尾 `return 1 if failed else 0`。因此即使另外82份计算全成功，原probe也会因repair未执行返回1；这不是可以改写成exit0的旧结论，也不能把非零退出一律当新包库崩溃。本文只静态核上述控制流，不声称本轮观察到82次成功。

### 完整原操作上下文仍须保留

`originalOperations`不是完整step正文：它只有caseId/group/ordinal/op/source pointer、mathInputId、decision及状态。完整setup/steps要从批准 `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/cases.json` 的 `/cases/i/setup`、`/steps`原字段取；不读取 `/expected`来生成图。50个product case的独立baseline、reset、scope、版本、定义/behavior/event/capacity以及操作顺序必须留在审计上下文，不能只保留一个终态图摘要。

例如：Q01 `/cases/41/steps/0`、Q02 `/cases/42/setup/0`及`steps/0`；V01 `/cases/49/steps/0..3`；R04 `/cases/46/steps/0..2`。旧83对Q01/Q02/V01的对应项仍只reason，并没有执行其query或validate。R02/03的stale/history与R05/06保存顺序同样不是reason两次就完成原操作验收。新包的有限语义调用可验证折叠后输入数学结果，但要明确原发布/事务/历史未执行。

### 具体缺件/不适用项

| 原上下文 | 固定指针/事实 | 可做的组件部分与缺口 |
| --- | --- | --- |
| transfer-repair | `/mathInputs/77`；transfer-inputs.json `/repair`给5事实、10本体、name-required约束、referenceCatalogue，没有rules | 用实际SHACL消费缺名设备102，再用referenceCatalogue唯一给出的名称构造独立after-repair输入。不能从ruleVersion继承R-risk，也不能将组件before/after叫真实repair工具提交完成 |
| ontology-model | `/unresolvedInputContexts/0`；course.json `/tasks/0`只给4条新增 | 可核4条增量的有限计算；完整原项目未给，不能擅自继承G-base |
| learning-report | unresolved索引2；checks.json `/checks/learning-report` | 无固定RDF项目，需T10真实输出/生命周期输入，不能按空图true代替 |
| G-list-13 edit-and-undo | unresolved索引3；cases.json `/cases/33/steps/3`无selected subject | 不能指定001/002生成中间编辑图；导入后完整状态、设备B操作与undo须真实owner供方 |
| G-list-05 late-V1 | unresolved索引4；cases.json `/cases/25`无V1完成轮次/载荷 | 不能从V2或oracle反造V1历史结果，保留not-executed/pending上下文 |
| E.5四事件片段 | `/mathInputs/79..82`，fullOriginalInputContext=false | 分别有18/34/50/66 asserted、各10 ontology、1规则，可作明确event-fragment数学计算；缺前序behavior/resource/order图，不是四个完整场景快照，更不证明capacity/replay/resume/reset |
| 其他生命周期/非图操作 | 全106原操作的状态仍false | 模型授权、HTML、导入导出、来源所有权、ChangeSet、行为/资源/事件消费、取消/崩溃、history/reset等另有owner/正式链；私有probe不得模拟权威状态 |

五条unresolved列表不等于只有五条未执行操作。其余原行为/生命周期可能输入文字齐全，但当前语义组件不是对应executor；应区分missing-input、unsupported-by-this-component与not-executed，不能统一叫pass。

## 2. 原consumer-C：13格的完整映射

两个固定原件分别为consumer-C-inputs.json的13个cases与consumer-C-goldens.json同ID预期。**2 query+11 SHACL；“原C/cases11”既可能指索引11，也可能在旧记录指11个shape，不能写成13个SHACL或总共11例。** 原件、历史currentEntryGap和两个date条件golden均不改。

| `/cases/i` | ID | 源包同canonical调用及完整外部oracle |
| --- | --- | --- |
| 0 | C-query-numeric-promotion | parse_turtle(dataTurtle)→query(graph,query)，完整SELECT variables/rows；integer16777217与float词法的query promotion选中s，不用规则精确比较false代替 |
| 1 | C-query-type-error | 同query入口，FILTER错误剔行，正常空rows；不是执行Job失败 |
| 2 | C-datatype-exact | shape/check或显式strict文本入口；false，完整Datatype六字段，value精确xsd:int的1，不把int当integer |
| 3 | C-langString | true/空报告，datatype rdf:langString支持；原gap文本仅历史 |
| 4 | C-count-term-identity | false，MaxCount完整六字段，01与1两个RDF词法term都保留，value若实际缺失为None |
| 5 | C-in-term-identity | false，In完整六字段，value为integer01，不能numeric equality归一成1 |
| 6 | C-inclusive-numeric | min=max integer2，true/空 |
| 7 | C-inclusive-nni | nonNegativeInteger2与同型bound，true/空；非法负数/坏词法另走前门 |
| 8 | C-inclusive-dateTime-equal | 两个不同offset代表同时间，非date路径，true/空 |
| 9 | C-inclusive-dateTime-before | false，完整MinInclusive六字段，保留原1999-12-31T23:59:59Z value |
| 10 | C-inclusive-type-error | 字符串a与integer bound，正常false/MinInclusive完整行；非date类型错不能被UTC分支新前门吞掉 |
| 11 | C-inclusive-date-entry | legacy仍INVALID_SHAPE/Validator0；显式utc-date-range-v1、两种data_policy均true/真实空；选原golden的已存在extension条件分支，不用core false分支，也不改历史文本 |
| 12 | C-illtyped-entry | strict仍INVALID_LITERAL_LEXICAL/Validator0；integer-illtyped-report-v1进入真实Datatype false，value为原not-an-int^^xsd:integer；参数报告身份不能混用 |

源JSON的requiredResultRows在外部转为实际API六字段对照：focusNode→focus，resultPath→path，sourceConstraintComponent→constraint，resultSeverity→severity，sourceShape/value不变；`valueExpectation`只属于外部说明，不传生产。SELECT golden的字典行依variables映射核实际二维rows；不能只比包含s或数量。

额外两date衍生来自T05固定107208858229ef518c458aec96a29d4d2b366c46/运行8e6f469ac7a64a1b3ec43edb13a8dc976ee8c4c4/过程525c91717c07dc4b386fcec00f897e1e6a75caf1：仅将原case11 data唯一日期改为1999-12-31Z或2000-01-01+00:00，shape完全不变。前者是真实MinInclusive false六字段，后者date-value/RDF_TERM_INVALID/Validator0。该消费闭环是3输入/7stage/3真实报告（原C调用0/1/1/0/0），不是7个规范输入或本轮已取得包内证据。

## 3. B1必要语义族、真实入口及失败边界

以下是完整case选择面建议，不是把现有整份test打入包。只提取表中命名位置的纯输入字面量/真实定义，给独立ID/原指针；test中的expected、monkeypatch、fake对象、原结果与pytest helper不随输入采用。

| 族与固定源码入口 | 至少保留的真实正向输入/输出 | 拒绝/负向与观察边界 |
| --- | --- | --- |
| Turtle：semantic.py L111–133 `parse_turtle` | 合法IRI、unicode、原literal lexical/datatype/lang；plain/explicit xsd:string、语言大小写同identity及integer01/1不同term；完整图集合 | 非Turtle格式、坏文本/Unicode、1MiB/图100000原限额、blank node、未知datatype、illtyped、nonfinite、owl:imports。拒绝不能静默删构造后“解析成功” |
| Query：L160–237 `query` | SELECT完整variables/二维rows/None未绑定、ASK精确bool；COUNT、稳定ORDER BY及值相等term tie；C0/1及原Q01/Q02查询 | SERVICE含SILENT/变量/嵌套、FROM/NAMED/relative/file拒外联；非SELECT/ASK、RAND/NOW/UUID/自定义函数、非COUNT聚合、Slice/LIMIT、named Graph、非法Order各保原固定码。不将literal中SERVICE/FROM文字误拒 |
| 有限RDFS+legacy规则：L1234 `reason` | subclass transitive、type-via-subclass、domain、IRI range；cycle终止；原R04先闭包再R-risk；多匹配同输出仍全部evidence；完整rdfs/rules/warnings/evidence | range literal不造literal主语；不扩subProperty/完整RDFS/OWL；annotations不参与推理；规则不反馈规则/RDFS；unbound head/非法rule即使空图也拒绝 |
| Profile实际text/records：semantic_execution.py L822/844 | `execute_profile`或`execute_profile_records`，原83的82 eligible逐完整typed when/comparisons/heads/basis/source与payload/rows/implementation；false不等于类型错误；22扩展的18integer格及JOIN/MULTI/DISABLED/MISSING | profile/词法/比较类型/资源有限失败必须保error+diagnostic，不能把0head等同所有前门通过。actual P1不能用给定binding、fakeCatalog或oracle.matches驱动 |
| 实际producer/fullview | material.py实际路径是semantic_profile_input.py L786 `prepare_profile_material`；production.py L445 `execute_admitted_profile_job`；restore.py L1569 `restore_profile_result` | /2 finite7 schema1，外7/内15/child11全字段、原L/C/R；接收完整payload/rows，不删未知字段迁就；末child/source/definition/limits/opaque错误无部分视图 |
| DAG/fullview | 新producer L459 `execute_profile_explanation`→restore L1677 `restore_profile_explanation_result`→L1696 `explanation_roots`；新 /3 finite8 schema2，7/16/11完整签名、ordered two-premise、depth、叶union/source全部保留 | 只真实structured material；Turtle新解释明确拒绝。roots只定位完整view已有leaf/step/all head occurrence，不是权限过滤、selected或正式Job。旧reader拒新字段、版本不猜测 |
| SHACL通用shape：L1528 `check_shapes` | 显式facts graph+named NodeShape/property/直接path；required/datatype/maxCount/in/inclusive；C2–10；真实报告conforms+完整六字段 | unsupported复杂path/SHACL、重复/缺target/path、非法bound、data混公理分别原门；没有target/没有value不伪造范围violation；minCount另由真实Validator判断 |
| B整数：L1533 `validate_shacl_text` | 两个keyword必填；strict与integer-illtyped-report-v1精确区分；原C12、坏integer其他词法、合法+01、无target/无constraint、optional value报告 | 只放宽data对象exact xsd:integer/ill_typed，shape侧和int/nni/decimal等不放宽。UTC成功后旧parse/query/reason/check仍严格。未知/非exact policy先于解析拒绝 |
| UTC date：同L1533入口 | policy=utc-date-range-v1→entry2；原C11、before/equal/after min/max、0001/9999/2000闰年、反向双bound、无target/无value/minCount、多值/共享property/不相关非Z date | 两侧exact xsd:date、ASCII11位YYYY-MM-DDZ；合法非Z/offset拒绝，不转UTC；date与非date pair双向拒绝，shape混bound无target仍INVALID_SHAPE；illtyped原parse门优先；exclusive仍unsupported |
| 新逻辑资源门 | 固定date公共1M恰界、公开超界、D1早/晚错误不同、同RDF三序费用/阶段相同；DAG四域有限资源 | 票数是政策work，不是native/CPU/H/RSS证明。private少一票/MemoryError/foreign metaclass/duplicate sink属于受控单测，不伪装可由JSON给出的真实图输入或实际OSOOM |
| Offline真实路径 | semantic_offline.py L22–35的实际scope与拒绝；必要SERVICE/FROM/import data/ontology/shape正反 | 配置“关闭”不足；将来源与包分别留拒绝原件。不同scope外任务不受影响，字面量网络词可用。不得在本docs窗口启动网络探针 |

### DAG新增纯输入建议

固定 `test_semantic_profile_directsteps.py:130–181` 有四个输入图及断言；未来只提取records：type二seed、domain→type三seed depth2、range二seed、subclass传递二seed。该文件L315的A/B竞争和L864的type先生成/domain后生成但排序先插入两个真实向量，补首见证与后轮重复；L707两相同head保全部occurrence。L358 raw alias/source保留及integer01/1也是独立族。

不可把L656受控helper“late-shorter”序列当真实图：完整分轮成功closure中首发现轮次等于最小proof-height，后轮更短不可达；此边界已在原独立报告中证明。L938起foreign bytes/metaclass、L991 foreign expectation domain，及受控MemoryError同属native边界单测，不是探针可接受的Python对象输入。包内可验证真实producer/restore调用的这些类被收集，但不要通过JSON开放任意对象构造。

末step/premise/depth/source、伪叶全链改名、伪firing1023/head15等恢复拒绝，可由**本次真实producer产生的接收副本**做已冻结的有限扰动，再仅重绑payload/rows外层摘要；原输入/source/实际allocation仍来自本次生产。不能让输入包直接携带“成功native_reason”“原L/PV”“restore expected/allocation”替代真实发行；不能给恢复端第二reason补齐DAG。

## 4. probe可读的纯输入与外部oracle分离

可以作为未来纯输入的数据：原text（含format/shapes角色）、query全文、逐原record的IRI/literal原lexical/datatype/language_raw/source、真实RuleSpec定义投影（id/revision/definition digest/when/comparisons/heads/disabled ids）、两个显式SHACL policies、范围选择及与其绑定的真实事实/约束文本、只读target key、固定有限扰动描述。来源ref/path/bytesSHA/JSON pointer、case ID、输入摘要与“片段/缺上下文/未执行”说明用于审计；不作能力/来源认证。

原83里这些输入位于 `/mathInputs/i/input/{asserted,ontology,definitions,disabled_rule_ids}`；旧`purpose`、scopeNotes、原操作引用与false权限标志可保为报告上下文，但不能据它们计算结论或自行升级认证。原case setup/steps的事实/规则/事件文字可作独立投影，必须保来源与scope；它们不因放入JSON而成为已提交状态。

以下只能在**外部**的独立oracle/验收层：consumer-C-goldens；T05 `real-executor-acceptance-inputs.json` 的triples/graphs/rdfsWitnesses/matches及各case expected；expectedReport/core/extension分支、接受绑定、推导heads/basis/闭包、实际旧结果/原成功payload、CompiledPlan/ProfileValue/seal/token。文件名叫inputs不证明其内容是输入——该T05 767826B文件明确是independent expected，包含248个三元组、89个expected图、40个匹配，不能喂业务。

外部比较应先按**纯输入的身份与scope**匹配独立oracle的图，再解引用triples/when/head/witness全部字段；不用“生成input hash后给expected lookup”驱动引擎。原83的E.5片段不与完整oracle轮图直接等同。source与frozen包的本次producer各自实际发行allocation/typed值，不能跨进程复制原opaque对象；比较完整wire/输入来源/typed字段和恢复一致性，而不是比较对象地址或伪造class别名。

原完整Turtle token/quote/escape/byte span在原JSON/N3输入未给时为缺件。把record投影另序列化成Turtle可以定义一个新纯输入ID，但它是生成文本的来源，不是原导入Turtle或CSV来源，不能借此填补原span。原CSV/source ownership与实际映射提交另有owner，不由此组件推断。

## 5. B1/S1的尺度、同输入和观测边界

已定位现有稳定S1纯输入定义：`storage_probe.py:35–57`，SEED=20261019，schema/predicate命名空间`urn:ontolearn:`；对象为`urn:case:{i}:equipment/...`与`alarm/...`，每scale恰18事实、六对象。固定QUERY在L36–37，是High/Open alarm查询及ORDER BY；它不等于原Q01包含Equipment/alarm关联的162B查询。`semantic_samples.py:4,15,153`明确复用该fixture/seed。

因此至少1×/10×应保这份18/180事实的输入结构/namespace/种子，若语义样例另加共享ONTOLOGY的10三元组则明确为28/190图；快照事实数与合并图数分列，不以同ID复制冒扩容。原83使用`urn:ontolearn:learning:`、C使用`urn:m1:`，不能用字符串替换把三个输入身份抹平。新输入展开/生成器仍需下一窗口；本文没有生成可执行器或运行输入包。

S1 `storage_probe.measure`会进入Store与临时DB；本次没有调用，也不建议拿新的语义probe去执行/绕过SQLite HOLD。B1可先设计同固定纯输入在源/包的解析/建图/query/语义输出等效；snapshot加载阶段必须绑定实际获准来源、owner和方法，尚未授权者记待验，不用虚构的“零秒加载”填表。两档都应保存实际输入字节/三元组/查询摘要、源与包身份、Python/依赖/OS/CPU架构/设备、冷启动与热调用定义、次数及每次原始耗时/峰值/包体；不沿用C4数字，不因均值或相同count省掉失败/超时/中止。

未来包内验证要运行新产物中的同canonical组件和同纯输入，不能让打包失败回退checkout/系统Python；包内模块/资源完整不以.py与pyc同SHA判断。指定双外审、目标Windows/macOS干净设备/无系统Python/断网/签名安装、CI/真人/正式Job/Store/worker/selected均是独立门。这里只记录必要验收面，不另授构建/计量/原生操作或被拒的SQLite/heap/OS分析。

## 6. case索引的具体建议与剩余输入需求

root JSON索引宜分别保留：原83逐项（含唯一not-executed及4片段）、106操作来源引用、50案例/54学习check索引；C13逐项及policy/stage变体；原Q01/Q02/V01独立真实query/shape输入；22扩展与R04原有顺序、原S1两档；新增有限RDFS四分支/DAG/raw alias/head occurrence/真实恢复拒绝；shape四修复/整数B/date全部已收支持与前门；外联与不支持构造。不要把117date观察、78整数观察、77DAG/26shape参数实例或23个T05测试数混为原规范case数。

已足够从原纯输入建立的组件项无需等正式Job：C13、Q01/Q02、V01 before/after、repair缺名的SHACL before/after、四有限RDFS与DAG、整数/date。仍缺的具体上下文见第1节；S1原fixture和query已命名，但未来展开后精确输入字节/hash与观测方法必须另固定。原查询/约束的结构化定义若需转换为Turtle，必须有唯一可审计的模板映射与source pointer，不由expectedReport倒推shape。

外部oracle的维护/解释仍归T05；若新增图无既有独立完整oracle，先另授纯输入与独立手工预期，不能用源输出当唯一黄金后只核包等于源。源包相同错误可能同时错；同输入等效与数学正确性要分别判定。受支持且完整的case、按合约拒绝、unsupported、not-executed、缺上下文、意外失败均分别留状态，任何一类都不能静默删出总清单。

本文完成的是可用于编写主合同和索引的调查；下一实施/输入asset/probe/四文件writer/运行/包测试仍由总控精确授予。未创建或消费任何新的执行输入包。

## 命名来源字节索引

下表仅本调查引用的命名来源，不是完整包guard或自动采用面；root另负责完整依赖/收集guard差异。除另列ref外均为6891 Git读取。

| 路径 | 字节 | SHA256 |
| --- | ---: | --- |
| `docs/prd/PRD-本体学习与落地Agent工作台.md` | 93584 | `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` |
| `docs/iterations/I05/profile-probe-inputs.json` | 1839011 | `6c6ffc3a1a57d1817583c0a71d24e2847cc5d2d673848878c6e6e72dfe6c39de` |
| `docs/reviews/T05/profile-M1-math-explanation-input-contract/consumer-C-inputs.json` | 8505 | `eeab821ccd71d55eed425a08b34d07648e623c0aa34eb2eabf66b839bbb426f6` |
| `docs/reviews/T05/profile-M1-math-explanation-input-contract/consumer-C-goldens.json` | 8163 | `c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440` |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/G-base.json` | 8219 | `306d41b332d223b47929eb90f196c71e4965a0e9ff81100c9469ed32612e8845` |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/cases.json` | 188023 | `a774a8d9615fd6fcacf81b567dff96c5cb202b6c35ef2d74a2943fe12b3e9baa` |
| `tests/fixtures/quality/approved-T09-873c8c0/content/learning/transfer-inputs.json` | 9091 | `3ae8b7fd952680283b9e2b2573afee94ba88357efa4849da4e4b3e0d7e681aa6` |
| `tests/fixtures/quality/approved-T09-873c8c0/tests/fixtures/product-baselines/unclosed-high.rq` | 162 | `8efbacd589c42ac40abbb55475cdd088e407a88a23e0db61dc8375e04e4dd386` |
| `tests/fixtures/quality/real-executor-acceptance-inputs.json` | 767826 | `87220503f9983146c974fe3e35025d520cad70e54fdd994aebfa86fb1ff7259f` |
| `docs/iterations/T05/real-executor-independent-oracle.md` | 17382 | `82d8c3976c2f5e47388e44fd44462c5ceddb58c26919b8cf58d22f3e90468f7b` |
| `packages/engine/src/ontolearn_engine/semantic.py` | 65749 | `60008130fe0db368ea87948c2c8f079b1161f2aa951693b69635558ed1f56a07` |
| `packages/engine/src/ontolearn_engine/semantic_profile_probe.py` | 13391 | `2b2dabd91745b4b4c2a3fad39b6386e4edd985189336bf029d9b07a638fc7bf6` |
| `packages/engine/src/ontolearn_engine/semantic_execution.py` | 35220 | `3ac496383349e3ddefea1672c27c88bacaf99f4436c22e96e1592393bac102f3` |
| `packages/engine/src/ontolearn_engine/semantic_profile_input.py` | 40378 | `f4d76b68e6bd5f27d4e1c0ee7b26435117b1dd762a4b2a16503d41afd1841f74` |
| `packages/engine/src/ontolearn_engine/semantic_profile_production.py` | 19993 | `5c857470890bd810370ad877db930848ba08e80096c640037d39bea83c14a320` |
| `packages/engine/src/ontolearn_engine/semantic_profile_restore.py` | 70203 | `1607d2968d2ba76ad0711be446fea7965641fb845226d0e683ac35e5d0f57243` |
| `packages/engine/src/ontolearn_engine/semantic_samples.py` | 33858 | `387278fa37006c9cdb3b08f1c7e7d6b8c3f0d5fbdaecb554fe02f310ec93cdb9` |
| `packages/engine/src/ontolearn_engine/storage_probe.py` | 5611 | `01415c8c904ad75bf8f6e2bf48430bd04211e0899bee81c490cee9dfe42f90f2` |
| `packages/engine/tests/test_semantic_profile_directsteps.py` | 42828 | `7bd1b63fbdcaf70d0a78efa4432c1b6091f91d96758988a86b5764b5c5d4b708` |
| `packages/engine/tests/test_semantic_profile_shape_entry.py` | 7211 | `38bc7a4074e183205f55fdb0a74e6933a505f9ff021fe24f5895d296ab725324` |
| `packages/engine/tests/test_semantic_shacl_entry.py` | 14604 | `61a3e92c298fa37483d203a8ad59dcafc9ec0ff61cf6d30b043267b7ca048c98` |
| `packages/engine/tests/test_semantic_shacl_date_policy.py` | 26924 | `bd8e332a1b55ebdf183f1effdd37126a61233931edaa8d2239e0a20d9179b765` |

配套 `case-catalog.json` 是本轮后续精确授权的**仅metadata**清单：逐83 index/ID/sourceRefs/inputProjectionJsonSha/eligible/full及原false状态，C13指针/ID/字段指针，106操作、54checks、50产品case的原引用与未执行状态，五项上下文缺件；没有dataTurtle、triple、规则正文、expected或已有计算结果，不是运行asset。JSON总数与本文计数用标准库静态核同；未调用产品。
