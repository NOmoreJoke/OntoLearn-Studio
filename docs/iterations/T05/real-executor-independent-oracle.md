# T05 真实执行输入的独立完整预期

本件与 `tests/fixtures/quality/real-executor-acceptance-inputs.json` 是独立预期，未执行 I05/T05 引擎、matcher、wrapper、比较器或真实 E1。仅新增本次授权的 fixture、本推导及 `docs/reviews/T05/real-executor-oracle/`。原完整 Goal、指定双审/CI/正常合并等门保留。政策采用和私有机制收口不构成实际执行证明。

## 固定输入、作者与方法

授权原件6389B、SHA `6346b48f7d69219f2e5b574732d7a6198a11746732d69b70aa7cdc5e876c9682`；接口事实固定400259f、22096B、SHA `502d7c70f670a6cc9c20e8683f0141468edaf45c1acc825fdcc6e3c71999fcae`，均全文读取并原字节封存。接口末尾临时task-runtime窗口是历史观察，未来维护已返I05；本件不改窗口或任何产品。

批准T09 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的17原输入共1307284B，每份均核原manifest及固定Git字节；另外固定原22扩展、profile/spec与PRD。输入清单 `inputs.json` 提供路径、ref、bytes、SHA；旧输入全部不改。原22扩展的 unresolvedComparisonDecisions 是历史元数据，由已采用profile覆盖，不再问Q6。`PRD-V0.6-E` 只是源输入标签，不是新执行器身份。

T05为唯一预期作者。先从输入的事实、本体、规则、事件和操作手工列举图集合、alarm分区、整数真值表、每个绑定及head，再用 `assemble-explicit-oracle.py` 进行标准库JSON编码/引用装配。该脚本无RDF库、推理闭包、通用模式匹配、值比较或行为调度器；不会读取原expected/actual来填本预期。显式表中的True/False、匹配tuple、RDFS结果及工单完成ID均是人工分析决定；循环只展开已声明表和输入子树。原case.expected只在另行结构核同/交叉审阅时读取，绝不作为新预期生成源。审查者只读，不平行编写第二份oracle。

读取大文件采用完整JSON解码、唯一源内容审阅及重复子树核同。50个product cases不等于54个learning checks；48个同ID expected结构和确定性JSON字节相同，G-list-01/06则展开E.5的capacity/replay/resume。`source-relations.json`记录精确pointer和hash；原缩进文本不宣称字节相同。四个额外check和Agent全辅助反例另列。课程9任务/15个check引用不是全范围替代。覆盖表50/54/22也不等于57 P0完成。

## 完整集合、来源和阶段的读法

fixture的 `triples` 是完整三元组字典；`graphs` 每图列完整 asserted、ontology、有限RDFS新增、自定义输出及合并派生集合的ID数组，ID解引用即可得到每个完整N3三元组。集合逐项相等，计数或包含关系不足。`matches`列每个完整正向三元组匹配、比较结果、接受与否、按原定义顺序的when、每个head序号和proof leaves；`graph.matchRefs`保留同输出多匹配，不因集合去重而丢依据。比较为false的完整when匹配仍记录，输出head为空；停用或缺属性的规则没有实际完整匹配。

`productCases`逐案保留原setup/steps并列阶段图、阶段输入摘要及源ref/hash；`extensions`逐案独立reset；E.5各轮细阶段在 `e5Rounds/e5RunPlans`；导入后的独立子例在 `importedSubcases`。本地 `oracleInputSha256`绑定解引用后的asserted/ontology/规则输入，**不是**真实producer/Store认证或已提交版本。

图的数学预期与已发布结果分开：非推理操作的完整图可以描述“若对此图推理”的数学全集，但原案例未要求运行时不产生一个current结果。R02/03保存后旧依据仅属原输入的stale/history；当前新图的预期不能回填到未重算结果。冲突/取消的工作图不是已提交asserted；历史快照不可按新图偷偷重算。源JSON已经提供的IRI/N3编码完整保留，可绑定实际文件SHA和JSON pointer；原导入前Turtle token、quote/escape、标签写法和byte span未提供时均为unavailable/null，不从输出逆造。生成的行为/规则预期term是推导结论，不冒充原始source。

ontology-model只固定四条新增，未固定原项目全图：只列四条增量的图投影，不凭空继承G-base；learning-report未提供固定RDF图，明确图阶段不适用，仍须T10实际验收。transfer-repair独立数据未给规则定义，ruleVersion标签不授权继承R-risk；transfer-classify才给独立R-risk。缺失输入上下文不写成全项目成功空集。

## 有限RDFS及单稳定witness

按批准接口事实和PRD附录C的有限子集，只采用subclass传递、type沿subclass、domain、range；range仅对IRI对象产生类型。没有subProperty、全套RDFS公理/反身闭包或OWL扩张，label/comment不参与匹配或推导。自定义结果不会反馈任何规则或末轮RDFS。

逐原ontology扫描：G-base/G-map-empty/E.5/transfer及22扩展只有类/属性声明，没有上述可触发公理。G-behavior唯一额外公理是 `P rdfs:range xsd:boolean`，P的对象为literal false/true，不能产生以literal为主语的type三元组。课程的domain/range术语例子不是新增公理。因此这些图的完整RDFS新增集合为空。

R-04新增唯一边 `CriticalPump subClassOf Equipment`，唯一CriticalPump实例为P001。故唯一新增为 `P001 rdf:type Equipment`：

- 公理原三元组：`CriticalPump rdfs:subClassOf Equipment`。
- 直接前提：`P001 rdf:type CriticalPump` 与该公理。
- 有限规则/依据：type沿subclass；固定PRD FR501、附录C及G.2 R04。
- 层次1；源pointer精确绑定R04的两个输入操作与整个cases文件SHA。

Equipment无后续subclass边，没有domain/range；新type也不增加其他公理，故到此穷尽。该图公理先加入但实例未加入的阶段没有新增。fixture `rdfsWitnesses.R04-equipment`给出唯一稳定witness、原公理、直接前提、叶集合和输入引用。因候选只有一对，无替代路径选择歧义；若未来输入增加多路径，必须新版本冻结选择，不声称此输入穷尽所有形式证明。C4现返回的叶basis不被本预期假称已有直接步骤载体。

## 规则匹配与每个head的独立穷尽依据

R-risk原顺序为Equipment类型→该设备alarm关联→同一alarm High→同一alarm Open。主变量绝不能拼接不同告警。没有告警的Equipment不形成完整匹配；名称、工单状态和通知不参与条件。类/属性声明本身不等于实例或规则条件。每个正向绑定只有一个风险type head；同设备多个告警仍各自保留绑定与全部依据。

| 图/案例阶段                     | 完整匹配与输出推导                                                                                                                                                         |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G-base；名称改动；V01；O01去A03 | 001/A01 High+Open唯一；002/A02 Closed、003/A03 Low。完整custom仅001风险，RDFS为空。删名称/删A03不影响A01                                                                   |
| Q02关A01；R02删A01；B04删A01后  | 无完整High/Open，custom为空；不得使用旧A01依据。Q02空查询、O01未记录与否定事实分开                                                                                         |
| R03加A04中间图                  | 001/A01及001/A04两个绑定，一个去重风险term、两个head出现与依据。原case未要求中间infer，不能宣称运行过                                                                      |
| R03删A01后                      | 仅001/A04，风险term不变、依据改变；A01任何前提不属于新依据                                                                                                                 |
| R04                             | 001/A01和P001/A-P001恰两绑定；P001 when用RDFS Equipment，叶依据展开CriticalPump原断言及subclass公理，再加实际告警关联/High/Open。risk001与riskP001两custom，另一个RDFS新增 |
| R05/R06                         | R-risk唯一A01；R-next保存启用但冻结输入无HighRiskEquipment，零匹配。提示unsupported-rule-chain，绝不输出NeedsInspection；正反保存序列全集相同                              |
| B01/B07新增A04                  | A01/A04两个匹配；创建或完成工单不改变这些依据。B01重提同event不能增加事件、工单或匹配来源                                                                                  |
| B02新增低危A05                  | 仍仅A01；新A05 Low，不触发风险或工单                                                                                                                                       |
| B03先删A01再加A06               | 先零匹配，事件后仅A06；不能用初始风险快照代替行为前推理                                                                                                                    |
| G-behavior其余                  | 除B04删除A01外，名称/布尔/通知/工单变动均不改变A01唯一匹配。B05/B09冲突回滚，工作意图不成提交事实；B06 Y看冻结false仍通知；B10/B11各实例其他动作保留                       |
| 映射M01–06/导入数据             | 没有alarm/High/Open，custom为空；手工note不因源撤回删除。M03源删002只撤受管两条，保留002手工note                                                                           |
| transfer-classify               | 201/T-A1唯一，名称是asserted，risk201是该绑定输出；初始派生视图为空，直到实际推理后才可判来源                                                                              |
| E.5                             | 初始无告警。到第1/2/3/4轮，恰AE001–004/008/012/016共4/8/12/16个完整绑定，都指向risk001；逐个when/head/叶依据显式保留。未来事件未注入，工单完成不改变告警Open               |

这张表是穷尽论证；完整三元组与每个绑定/head不只在 prose 概括，全部在fixture可解引用。阈值、规则文本或ontology类声明不混入实际when proof leaves；RDFS生成的前提通过其witness展开到真实公理和断言叶。

## 22扩展的手工真值及独立reset

每案只含共享ontologyTriples、本案inputTriples及本案rules，**不继承**R-risk或前案输出。18个比较输入均为唯一score在001上的integer1/2/3，对固定integer2；只001形成type+score完整when。手工整数序为1＜2＜3：

| 操作 | score1 | score2 | score3 |
| ---- | ------ | ------ | ------ |
| eq   | false  | true   | false  |
| ne   | true   | false  | true   |
| lt   | true   | false  | false  |
| le   | true   | true   | false  |
| gt   | false  | false  | true   |
| ge   | false  | true   | true   |

fixture逐个原ID绑定这18格；true恰输出001 Matched一个head，false仍有一个完整when匹配及比较false，但零被接受firing/head/custom。阈值2不是图前提。没有RDFS公理，因此完整RDFS新增为空。

其余四案：JOIN中001的A04 High/Closed和A05 Low/Open、002的A02 Closed、003的A03 Low，全无单一High/Open匹配；MULTI只有A01一个绑定、head0 risk001与head1 derivedLabel needs-review全部保留；DISABLED唯一规则revision2关闭，零匹配/产物；MISSING无score，零匹配，缺记录不推出否定。不能因为零输出就跳过合法定义/常量预检。

本22案没有覆盖profile九域、六numeric有序对、词法失败或资源±1等无限/更广边界。它们仍对应采用profile §§2–6和既有六机制fixture所述范围，真实解码映射待I05新候选固定；本oracle不添未授权新输入，也不将机制旧绿当新图golden通过。B域出现的布尔是场景输入，不是新boolean比较案例；本次integer18格不能宣称覆盖其他numeric五型。

## 阶段、reset、恢复与不应出现的产物

50个主案例各自恢复原baseline。A类非图隐私/HTML/模型/导出步骤不擅自写入项目；A01仅手工提交名称有效，旧Diff拒绝；A02中途失败/重开仍原集合。M类列出空图、首映射、手工改动、拒绝或撤回后的每个图；M05空键/重复键各独立reset，整批不提交。

R02先初推理、删除、stale、重算；R03先初推理、A04添加、A01删除、重算；V01两次验证分开。R06独立重建已保存启用两规则前提，并记录两个序列，不依赖先前实际运行。B01/02/03/07分事件、行为前推理/冻结、动作、资源、轮末；B04明确prime-current后删除再探测；B05/09失败回滚，不发布半组动作；B06冻结与动作后区分。

E.5事件只当轮输入；fixture每capacity四轮都列事件图、行为前推理/条件冻结图、行为后图、资源/轮末/提交图。工单顺序由原E.5固定：cap3累计完成W001–003/006/009/012，cap4累计完成W001–004/008/012/016，剩余具体ID也逐项列明；不是只用积压公式或计数。G1 cap3/4各两独立replay，G2 cap3单独reset，G6两次独立cap3重放另加round2显式续跑；后者保留E001–008消费，仅继续轮3/4，无W001–008重复创建。每轮的已提交快照、消费记录和原非图指标/action顺序仍须真实案例验证。

嵌套关系：G3→B09，G9→M04，G11→M01。G13先G9恢复进口项目，每个A01/M04/M06/A02子例独立恢复该进口状态，执行后不污染主查询/undo基点；note与来源/所有权保留。G13/M06输入的手工名称在进口图已存在，但原验收仍要求旧preview不得覆盖且重查冲突，不添加“no-op可通过”的新分支；具体版本推进/拒绝机制由T01实现，不能在预期里降低门。G13的edit-and-undo没有给selected subject；不固定编辑001或002，不构造完整中间缓冲图，也不以空图代替。只固定该整体操作完成后恢复imported的完整集合。撤销只恢复最后设备B编辑，不当成恢复整个项目快照。

G4的最大轮数与取消分独立branch，取消只保留round1、工作round2/W2不可发布；显式订单记录可投影类型/状态，缺少来源event就不造eventOrder。G5未固定V1实际完成到第几轮，本件只固定初图与“V1晚结果归历史、无V2当前”的选择规则，不猜其完成载荷。G7三个崩溃边界、G8存储失败后重开只见最后提交；G10三个缺省包变体仅模板，不能由原始图宣称恢复当前项目；G12完整及五缺字段变体分别保留可重放性要求，缺字段不重算补造。

完整集合已排除但尤其应检查：002/003错误风险、跨alarm组合、任何NeedsInspection二阶结果、P range产生literal主语、未来事件、重复工单、失败/取消的半提交、从stale/历史借来的当前依据、source撤回误删手工note、普通空结果推导否定、报告缺上下文被当全图成功。source/provenance和无模型/第三方授权等原非图门并未被这些排除表取代。

## 验证、原件与退出范围

`structure-check.py`只做JSON/ref/hash、集合去重、所有when/basis属于相应输入闭包、head与custom显式集合一致、witness指向和阶段/reset清单覆盖等结构一致性检查，不重新求闭包或匹配。原17输入/22扩展及已收口20路径须保持字节；不创建E1测试，不出假actual/run.log。首结构失败/修订和独审反例在独立证据目录保留，不覆盖失败为通过。候选oracle/推导/装配与检查输入固定后交独立agent全面审查，修具体问题后本地提交。

本阶段完成仅表示这组固定输入的独立预期准备。真实解码/执行器接入、生产source/producer认证、Store/Job/worker发布、生命周期/定位/平台、完整原验收、指定同候选双模型及CI/合并仍按原门另行推进。

## 独立审查R1–R3的修订

candidate2独审未通过三项P2，原报告及ZIP保持不变。R1删除G13无依据指定001的中间编辑图及无用途便利图/term，显式记录subject/完整中间缓冲未给，不降低整体undo恢复集合的验收。R2映射图改绑G-map-empty实际rule/ontology来源，CSV四条预期逐条绑定物理行2/3、原key/cell及mapping规则；字典中相同G-base occurrence不再被当作CSV来源。R06的新增类/R-next另绑本例实际pointer，以结构和确定性JSON值hash证明共享表示等值，不把不同输入来源当成同一认证。R3为Q02、A01、M04/M06和两条手工note补原操作/事实的精确pointer，结构门逐term核对；rawImportUnavailable只指未提供的导入前Turtle，不掩盖已知JSON/N3操作token。

首结构失败是Python3.9.6不支持zip(strict)，修checker后通过；首版与candidate2的fixture JSON值相同但格式字节不同，文档亦有边界补充，不能概称整版仅checker变。R1–R3编辑装配时还发生一次文本插入锚点未命中导致变量未定义，写出新fixture前即失败；原错误与当时脚本另存ZIP，原candidate2未覆盖。上述均非产品运行。本次修订另封新候选，独审只复核实际delta及集合不变范围。
