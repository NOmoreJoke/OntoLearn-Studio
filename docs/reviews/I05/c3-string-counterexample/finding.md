# I05-C3-STRING-1：plain / xsd:string 抽象 term 分裂

结论：固定 C3 有真实语义缺陷，建议P1阻断指定外审派发。相同词法的plain与显式xsd:string被部分入口当成两个term，导致真实query/Rule漏匹配、SHACL in误报和selected-derived数量约束误判。不是T05新比较政策，不是从设计报告推断运行缺陷；没有修改3289/bf2原件。总控已明确撤回条件派发，实际新任务0，待总控读反例后授原修复门。

## 固定来源与实际运行

冻结完整head `3289d67dbfb19545c7a3b3b26753cdd0065741bb`，产品69598f3/测试b045690；本次开始过程head49af70d。原candidate SHA edfc7a50…63b41e4、1197跟踪blob/204执行输入在本次前后全部一致。AGENTS78df、最新common ff5f9fd0…有效；原受审清单/双审输入不改。实际本线原Mac无窗口source venv，仅新增合成输入/临时DB及证据；没有全套重测、stdio Session、包/native/GUI或生产验证。

运行命令 `PYTHONPATH=packages/engine/src .venv/bin/python build/i05-plain-string-c3/probe.py`。driver实际exit0，现有DirectWorker/completed helper经真实Store.commit→semantic.start→coordinator独立worker→result.get/page→semantic_result鉴权读取，**12个不同job均succeeded**，全payload、元数据、请求/operation、原分页rows保全，项目事实/定义state前后不变。没有fake finish或把pure直接结果冒称worker。

## 规范目标与现有各层

RDF1.1无语言simple literal是xsd:string的省略写法，同词法二者是同一抽象term；数值词法01与1仍是不同term。[RDF1.1 §3.3](https://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/#section-Graph-Literal)。SHACL in按term成员，数量按value-node集合，datatype另按SPARQL datatype检查，各自不能从规则value comparator推导。[SHACL2017](https://www.w3.org/TR/2017/REC-shacl-20170720/)。

S1 `rdf_snapshot.term`已有字符串规范写法：显式xsd:string转为plain，lang标签转小写；Store要求传入该canonical N3及content-derived ID。其手工事实入口并不是接受任意写法再自动转换，故不能强灌typed spelling后称存储bug。本见证显式按既有S1规范化/去重；原raw spellings与转换映射分开留存。

C3 `semantic_turtle.LexicalSink.newLiteral`保留datatype参数，plain为None、typed为XSD.string。`semantic_execution._term/_graph/_rules`沿此构造；query clone只处理numeric/unary，未统一String；RDFLib term equality/hash区分这两个内部表示。SHACL datatype有专门plain-string兼容分支，因此它正确，不能泛称“所有SHACL均错”。

## 最小见证与具体结果

完整driver输入11条只用于纯解析表示/数值对照。plain与typed重复同一s/p/x，纯parse实际11 triples、term-equal=false/value-eq=true；RDF1.1同term去重应10。`"01"^^integer`与`"1"^^integer`在这份纯解析对照仍term不等，没有用本问题合并数值。

真实Store输入另外明列：numeric01不进入手工事实，xsd:string按既有S1变plain后按term内容去重，最终**9条canonical事实**。三个对象主体plain/typed/both的p均为plain `"x"`；其中主体名typed只表示输入原写法，不能说数据库里仍是typed对象。下面精确query仅依赖所指s/p，不受其他控制事实影响；没有额外执行一个删减数据库来冒称更小运行。

| 消费者/原件                                                                   | 实际结果                                             | RDF1.1目标/解释                                                |
| ----------------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------- |
| Rule when `?s p "x"`                                                          | 3匹配                                                | 正确对照。                                                     |
| Rule when `?s p "x"^^xsd:string`                                              | 0匹配                                                | 应同样3匹配；不是数值比较问题。                                |
| ASK `plain p "x"^^xsd:string`                                                 | false                                                | 应true。见03-query原件，job27be0fb2…                           |
| ASK `typed p "x"`                                                             | true                                                 | 正确对照；typed主体在Store已canonical为plain。                 |
| VALUES绑定typed string与p变量join                                             | 空结果                                               | 应返回both/plain/typed三个主体。                               |
| SELECT projection含DATATYPE/LANG/sameTerm(typed)                              | 3行，DATATYPE全xsd:string，LANG空串，sameTerm全false | DATATYPE正确，sameTerm应全true；不以datatype投影证明join正确。 |
| asserted sh:datatype xsd:string                                               | conforms=true                                        | 正确对照。                                                     |
| asserted sh:in (plain)                                                        | conforms=true                                        | 正确对照。                                                     |
| asserted sh:in (typed string)                                                 | conforms=false，3条完整In违规                        | 应true；保留各focus/path/value/sourceShape。                   |
| asserted only both，maxCount1 / minCount2                                     | true / false                                         | 正确对照：只有一个抽象值。                                     |
| 真实reasoning输出plain+typed同词法head，选定该producer后maxCount1 / minCount2 | false / true                                         | 两个内部表示错误计成2值；应仍true / false。minCount2为假通过。 |

reasoning完整rules现有5个term输出/evidence（3 plain-matched加plain/typed两个emit），typed-matched全缺；按抽象term预期两个constant匹配各3＋同p/x head集合1＝7个term输出，成功匹配trace仍需分别保留。这是正确匹配和图集合去重两层要求，不能通过丢掉匹配/依据伪修。

实际derived两个任务引用真实reasoning result，不重算代替producer；selected认证和payload/rows hash均通过，故问题是经认证载荷中的term语义，而非Store授权绕过。末两job分别b5c1581e…和bd793e2e…，完整record含原producer/resultRef/原快照/implementation/参数/页。

## 语言标签控制及保留范围

新增的唯一language对照用同一原环境的pure真实parse/query/reason入口，无新增worker任务：`"x"@en`与`"x"@EN`当前term/hash相等、同图去重为1；大写模式query/sameTerm和Rule常量对小写数据均匹配，S1 canonical为en。LexicalSink内部仍保留EN原拼写，实际evidence.inputs显示EN而basis显示en，是表示层差别，不能据此说本轮已发现lang匹配或数量错误。

本问题需统一无语言string内部抽象身份；修复不能丢lang、把带lang当无lang字符串、合并en与en-US、或更改numeric/date词法和值政策。完整BCP47合法性、任意标签/排序/序列化往返及其他语言支持本轮未验，不用这个en/EN对照关闭其范围。若要统一所有lang序列化拼写，需明确独立采用和影响；本次最小修复不以“必须重写全部lang政策”为前提。

## 建议最小修复边界（未实施、待root授门）

在同一现有语义管线设一致string-term表示，优先沿用S1的plain内部约定以少改现有canonical持久输入；选typed内部表示也可，但需完整核对所有接受/输出端，不能只改一条比较。限定同词法、无language、datatypeNone或XSD.string这一个等价类，保留normalize=False及所有其他datatype词法；不改全局Literal/parser设置。

需要实际评估的I05-owned路径是semantic_turtle.py（数据/shape及常量构造）、semantic_query.py（query常量/BGP/VALUES/表达式）、semantic.py（接受Graph的frontdoor、Rule常量、SHACL data+shape一致表示）、semantic_execution.py（_term严格输入/Rule/图重建）、semantic_scopes.py（来源hash与选定既存结果的一致性/重建），以及resources.py版本、semantic_samples.py/相应既有和新增回归。应共享同一精确转换，不造第二执行器；是否拆新helper路径先给root具体范围。不是修改这些文件的当前授权。

query修复还须逐项评估现有允许表达式在运行时构造/绑定string的路径，不能仅把静态token换写后宣称所有query term一致。本轮没有运行该扩展矩阵，也不把这一风险外推成已复现的新缺陷；后续不能为方便修复而静默缩减原query支持。

不要改已转T01的worker/Store/canonical、协议、锁/依赖、build或CI来消除本反例；目前真实source worker/存储支持运送并认证该结果，未发现必须修改它们的证据。只改when比较不能修shape/list/query常量、图重复和selected-derived计数；只修datatype也不能修in/count。

## 版本、载荷与历史

这是原抽象term身份/结果含义的修正，需新semantic version（例如finite6仅作待定建议）及resources实施身份同步，形成新完整候选与对应验证/双方新全范围审查，不能在finite5原件下暗改。新版本会影响规范化输出、source asserted/ontology/selectedRules摘要、完整proof/rows/hash、canonical validation projection和selected内部一致性；必须在同一版本计算/认证，而不是单改展示N3或rows后不重算其来源。

优先保持现有payload结构，不添加公共字段；若要求原始显式datatype写法额外传到新公共DTO，则属于T01另行设计，不能用本修复越权。原definition/原输入仍不可变，按新语义解释，不重写历史或Store ID。

当前Store.semantic_result按原producer/meta/payload/rows/hash鉴权，未简单要求全局当前implementation；prepare_semantic_request的新selected却要求whole implementation相等。此处是静态核对的既有机制，不冒称本轮已运行未来版本。新候选必须再实测：旧finite5结果按原身份读取且字节不变（仍受schema/payload可用条件），作为新版本selected输入严格拒绝；同版本完整graph/shape/query/Rule/来源/分页及current-history通过。不要升级旧producer标签、用新parser重签旧证明或删除不理想旧载荷；历史可读不等于规范正确或获准消费。

## 原始失败及证据边界

两次预备Store.commit因noncanonical手工对象在worker前拒绝，各0worker任务，DB/原脚本/input/stdout/stderr/exit1均留本线ignored目录；第一轮将原因仅归numeric01的猜测不完整，实际typed spelling也违反S1 canonical。明确更正后最终driver沿真实已有canonical输入门，12任务exit0，不把这些准备失败当产品反例或抹掉。

随后证据整理一度用系统python导入JobStore，缺rdflib，已改回原.venv只读保存canonical state；未为此重跑产品。该整理异常原工具输出未单独重定向成raw文件，本说明不冒称有独立原stderr文件。最终保全的运行raw、两次driver原失败及language对照原stdout/stderr/数值exit均为实际原文件。

原始包排除合成SQLite/锁/WAL/SHM，保存脚本、全部12任务receipt/完整payload/rows、原输入/转换、parse/language见证、stdout/stderr/exit、绑定/环境和首次失败。没有用摘要/hash代替运行原件；固定Git＋204输入清单及原锁可重建源码环境，临时DB不作离线完整恢复承诺。独立只读审查另附原文，不作为指定模型外审。
