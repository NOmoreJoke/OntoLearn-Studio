# T05 最小纯profile/comparator阶段：一次授实施规格

**当前仅计划，待总控一次授阶段后实现。** Q6用户政策与规范pin已明确采用，不再申请Q6。继续同一T05工作树/分支/完整Goal，不重建；官方Goal仍因真实依赖/接线/平台门blocked，有限阶段不冒充全部恢复/完成。行为规范见[已采用profile v1](q6-adopted-profile-v1.md)。原已测产品2f与635 TS/1200 Python/18 synthetic DOM只是历史证据，本计划没有运行新机制。

## 1. 本阶段唯一实现范围与输入/输出

实现**可供未来唯一I05执行器调用的纯值/给定binding机制**，不实现图搜索、规则匹配、RDFS/SHACL、规则反馈、Job/Store/SQLite/HTTP/IPC/UI或公共schema。全部新模块只依赖标准库；IRI仅以标准库检查与批准5f相同的scheme/禁用字符最小结构约定，不import其RDF模块，不用Literal/Graph parser或value转换；完整IRI/RDF语法合法性是实际入口precondition与后续联验缺口。当前quality.__init__会import旧definitions→RDFLib/parser日志filter，因此拟在本阶段改为保持四个既有导出名称的lazy导出，让新机制import不安装旧parser副作用；原编辑/plan API和测试保持。

私有类型/API（不是公开JSON契约）：

- `TermInput`、`SourceRecord`、`InputLocation`、`ProfileLimits`为冻结数据；`Budget`为本次调用专属、只能扣减的私有可变计费器，不与其他调用共享；`ProfileFailure`仅暴露只读安全字段，异常运行时traceback不进入输出/日志。不通过任意对象str/repr获取输入，不执行用户callback。SourceRecord只记录实际有界来源，不认证actor/job；位置无依据则None，绝不猜0。
- `parse_value(term, location, budget)`→`ProfileValue`，含原term/source及精确Number/Calendar/String/Language/IRI/Boolean value。`compare_values(left,op,right,budget)`→bool；类型对/算子按已采用矩阵，失败抛私有ProfileFailure，不构造公开DTO。
- `compile_rules(definitions, catalog, budget)`→`CompiledPlan`：控制定义/变量闭合、全部常量/heads/RDF位置/合法引用预检，**成功后才允许处理任何binding**，即使caller最终给零匹配也要先编译。constants预检失败立即整批失败，不承诺返回多错误清单。
- `evaluate_bound_batch(plan, matches, budget)`→完整不可变`PreparedFiringBatch`；matches只能是有界list/tuple的冻结`BindingMatch`，包含实际变量term、按原位置排列when triples及其已有proof leaves。拒绝无限generator/任意用户代码。每组核绑定闭合及与给定when模式实例化一致，**不证明when在图中或caller已枚举全部匹配**。
- `check_firing_group(plan, group,budget)`复核给定完整组的comparisons/全heads/binding/when/basis内部一致；不调用reason，不认证producer或全局完备。未来I05 selected复用同一机制，T01另认证真实producer/快照/依赖/定义/payload/rows hash与权限。

## 2. 原子多head与真实位置

规则最多100条；when至多16、comparison至多32、heads至多16，变量名沿现私有语法`?[A-Za-z][A-Za-z0-9_]{0,63}`，最多64变量。它们是拟阶段预算，不是新公共语言或已测业务容量。RuleSpec保原rule id/实际revision或prepared-plan摘要、原定义digest、当时policy、原when/comparison/head位置；新增内部IR不直接灌I05旧exact-key payload。

给定每完整when binding：先核全部使用变量；按源comparison位置计算**全部comparison，不因前false短路**。发现真实错误可立即整个batch失败，不汇总所有错误；无错误且全true后才实例化所有heads到局部临时tuple，逐项核RDF位置/类与对象/数据属性受控引用。全部通过才向局部batch缓冲追加；整批所有binding/预算/完整序列化成功后一次return。任何后项head/后binding/最终输出超限都丢弃整个本次缓冲，不返partial。无匹配/全false是成功空批，不是UNBOUND；没有发布current能力。

head只允许rdf:type到已声明类，或已声明对象/数据属性；IRI subject/predicate、object/data属性的对象种类及禁止schema修改沿现有限规则合同，不新增domain/range强制、SHACL隐含校验或状态动作。定义引用错误/坏位置→INVALID_RULE；用户合法binding导致某head位置非法也整任务INVALID_RULE。合法RDF三元组但超受控输出（schema等）→UNSUPPORTED_RULE_OUTPUT；已可信闭合后内部缺binding/被改计划→Internal，不能假称用户未绑定。

每firing保留原binding、重复when位置、每comparison实际两operand/operator/value/profile/判定、全部head原index（重复term也保留）、when输入既有proof的basis并集及原source身份。阈值不进basis。两个不同firing同结论都保留；独立输出term集合按抽象term key去重，而非值eq。完全同rule/binding/ordered-when组重复从可信caller送入属内部输入不一致，不靠静默去重隐藏；group key不提供授权证明。输出排序用稳定term/规则/位置键，禁止Python hash seed决定可观察顺序。完整成功批才可交未来I05真实事务，未接线前不提供“成功Job”或写入。

InputLocation只为真实source中的`section=when|comparison|head,index=非负`及内部可选side/span；编译构造时由本例真实定义元素传入，不拿新排序位置冒充原索引。对binding operand保留原变量occurrence位置与图source来源的区别；原始row/字节span未知则不造。公开ruleId/诊断引用怎样呈现仍T01/I06批准路径；本阶段不回传原值/path/stack至公共错误或日志。

## 3. 失败reason、context与优先顺序

纯机制只产安全`ProfileFailure(reason,location,classification)`，不自行制造可信Origin/Producer、真实Job/source身份或DTO。下表是未来caller/adapter必须满足的**成对合同**，不是本阶段新增公共路由；M3/M8a/M9未在现adapter接线时不能直接发给它。

| failure                                                         | 真实可信用户规则入口的目标context／现有DTO                             | 触发与额外边界                                                                                                   |
| --------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| INVALID_RULE                                                    | REASON/RULE/VERIFIED_USER_INPUT→SEMANTIC_INPUT_INVALID `{field:rule}`  | 定义/operand形状、非法输出位置/引用；持久损坏不归此用户分支                                                      |
| UNBOUND_RULE_VARIABLE                                           | 同上                                                                   | 定义变量闭合不成立；合法join无解不是错，可信闭合后内部丢binding→Internal                                         |
| INVALID_LITERAL_LEXICAL                                         | 同上                                                                   | 已支持类型原lexical/值域/标签well-formed非法；资源限额不装词法错                                                 |
| UNSUPPORTED_LITERAL_DATATYPE                                    | 同R/R/U→UNSUPPORTED_CONSTRUCT `{construct:datatype}`                   | 合法但未支持的datatype；不能删已采用类型矩阵                                                                     |
| UNSUPPORTED_NONFINITE_LITERAL                                   | 同R/R/U→UNSUPPORTED_CONSTRUCT `{construct:literalValue}`               | 合法NaN/±INF/+INF或有限词法目标溢出；非法词法另错，合法下溢零不拒                                                |
| UNSUPPORTED_RULE_OUTPUT                                         | 同R/R/U→UNSUPPORTED_CONSTRUCT `{construct:ruleOutput}`                 | 合法RDF三元组但超受控输出（如schema）；坏定义/位置仍INVALID_RULE                                                 |
| RULE_COMPARISON_TYPE_MISMATCH                                   | 同context→SEMANTIC_INPUT_INVALID `{field:rule}`，**未来新路由**        | 已解析合法value域/算子不兼容，含ne；不返回false                                                                  |
| RULE_INPUT_BUDGET                                               | 同context→RESOURCE_LIMIT `{resource:semanticInput}`，**未来新路由**    | 预检字节/定义计数/位长；图/text原入口另有context，不复用假R/R分支                                                |
| WORK_LIMIT                                                      | REASON/RULE准确既有资源分支→RESOURCE_LIMIT `{resource:semanticWork}`   | 按实际消耗；UNKNOWN先拒，既有trusted-internal资源/network例外保留                                                |
| RULE_EVIDENCE_RESULT_LIMIT                                      | REASON/RULE准确既有资源分支→RESOURCE_LIMIT `{resource:semanticResult}` | 完整批条目/字节；最终公开行/载荷仍PROJECTION/PROJECTION的PROJECTION_RESULT_LIMIT，frame/page/worker memory另边界 |
| RULE_POLICY_UNSUPPORTED                                         | R/R/U→UNSUPPORTED_CAPABILITY `{}`仅未来M9提案，未批准接线              | 本阶段调用内部API的policy错误为本地安全失败；公共未知字段/坏结构先严格解析，非protocol版本错                     |
| unknown reason/context/UNKNOWN origin/可信持久损坏/意外内部异常 | INTERNAL_ERROR `{}`                                                    | 未列新组合不降用户错；已有其他合法route与资源/network优先顺序不变，原异常不外泄                                  |

初始facts/ontology _terms沿I05报告的REASON/SYNTAX/VERIFIED_USER_INPUT，即使后续query/validation：三个literal token分别映datatype/literalValue或SEMANTIC_INPUT_INVALID field:syntax；本阶段不改该入口。普通SHACL违规不入adapter。M12当前跨implementation新消费IDENTITY_CONFLICT不变，未来语义UNSUPPORTED adapter/受限诊断schema方法仍未批准实施。精确新caller正反context/golden要I05+T01联验，不能由纯helper自报U；可信绑定若坏literal/when/计划一致性应Internal而非用户规则词法错误。

本地确定错误顺序：输入计数/字节/结构护栏→定义顺序与原位置的闭合/常量/heads预检→每binding完整性→原comparison顺序左右operand解析/域/算子→all-true后原head顺序→完整batch输出预检。false不跳后项；一旦错误整批失败。预检先触发资源可覆盖未扫描词法；预算内非法词法与合法非有限分开。未知内部/取消由真实权威边界即失败，不伪造多诊断或重跑。多个真实错误仅保证以上稳定首错，无多错误汇总承诺。

## 4. 可冻结的阶段硬上限与计费

以下是**拟由本次阶段授权一次冻结的防护值**，不是测得的业务容量/性能、不是生产limit或Q6改写。所有限额是最大值；测试可用更小值验证±1，caller不能通过输入任意抬高。版本`mechanism-budget/1`，未来真实接口limits须再由owner测量/同版冻结，不能把本表覆盖Job frame/page/worker内存/timeout。

| 项                              | 硬上限／前置检查                                                                                                                                                                         |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 一次机制输入总UTF8字节          | 262144，含term/source/结构内容，对已解码受控输入先数长度、流式UTF8计数再复制/构造；真实上游解码/transport自身另限，纯函数不能追溯阻止caller先前分配；不是使用transport帧证明semantic容量 |
| 单term lexical／单source原文    | 分别16384／65536 UTF8字节；总额仍262144；空S/L文本按实际字节计，不用泛化非空text helper                                                                                                  |
| 数字组件长度                    | 整数/浮点significand/指数文本/年份/fraction分别≤4096 ASCII digits，处理前查限；float巨大指数先有界流式远界判定，不能先int全部指数或分配10幂                                              |
| 持久中间整数组件                | 每个p/q/日序等≤16384 bits；乘/移位/除法临时≤32768 bits，**运算前**以上界估算；不调全局int限制/Decimal context/RDFLib normalize                                                           |
| 定义/when/comparison/heads/变量 | 100 / 每规则16 / 32 / 16 / 64；原编辑128草稿不是运行容量，本阶段不改UI或公共limits                                                                                                       |
| 给定完整binding数               | 总计≤1024；只接有界序列，超限前不构造完整输出，不把1024称真实匹配容量                                                                                                                    |
| 输出                            | firing≤1024、head occurrence≤16384、trace逻辑项≤8192、完整安全私有载荷UTF8≤262144；同时限制，失败不截断成功                                                                              |
| 累计work                        | ≤16777216确定单位；每次昂贵操作前扣费，超限即失败；不按墙钟伪装semanticWork，不预填未测ms/MB容量                                                                                         |

确定计费：扫描/UTF8计数按字节；定义/绑定/比较/head/proof leaf/trace项各至少1；bigint以32-bit limb数L=max(1,ceil(abs.bit_length/32))，乘法预扣L(a)×L(b)，除法/余数/GCD每步按被除/除数limb乘积，shift/十进小段转换/有界幂每一步按输出/参与limb收费；交叉乘与GCD不免费，构造10^n前估bit上界。序列化按字段/UTF8字节在追加前计数，整数值内部若需证据采用有界hex numerator/denominator，不对大int无界decimal str；常量预解析只在compile收费，binding与每次comparison有实际事件，缓存不得绕过计费。sorting按比较/term字符检查计费，新增缓存/算法变更需同版更新成本约定与边界证据。

Calendar采用day+秒分数分离，避免大年份×fraction分母；float远界可直接∞/有符号零，但原词法扫描/长度预算照计。所有原始term/source字节保持，资源超限不是“此类型不支持”。阶段无合作cancel token；真实父进程取消/deadline仍T01/I05权威边界，未来若需callback先精确owner授信号路径，不造无驱动token。

## 5. 精确代码／测试／fixture路径（本次申请的一揽子私有范围）

仅下列路径，**待root授阶段，不在本轮创建代码/测试文件**；不给四semantic future路径写权，不触公共协议/worker/Store/入口/build/锁/旧I05 tests。

| 操作        | 精确路径／职责                                                                                                                                                                                                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 修改        | `packages/engine/src/ontolearn_engine/quality/__init__.py`：四既有导出lazy兼容，避免新纯模块import旧parser日志filter                                                                                                                                                                       |
| 新增        | `packages/engine/src/ontolearn_engine/quality/rule_profile.py`：profile/pins、冻结类型、source/真实位置、安全failure、immutable Limits/计费                                                                                                                                                |
| 新增        | `packages/engine/src/ontolearn_engine/quality/rule_terms.py`：结构化term、S/L/boolean/IRI门，完整ABNF、raw/source/term_key分层                                                                                                                                                             |
| 新增        | `packages/engine/src/ontolearn_engine/quality/rule_numbers.py`：严格整数/decimal/float lexical、bounded有理与直接binary舍入                                                                                                                                                                |
| 新增        | `packages/engine/src/ontolearn_engine/quality/rule_calendar.py`：精确年历/offset/秒分数、无宿主datetime                                                                                                                                                                                    |
| 新增        | `packages/engine/src/ontolearn_engine/quality/rule_comparator.py`：九域/六numeric有序对/六operator分派与精确比较，无FILTER                                                                                                                                                                 |
| 新增        | `packages/engine/src/ontolearn_engine/quality/rule_firing.py`：compile与给定binding全比较/all-head原子批、完整组内部复核，无图matcher或发布                                                                                                                                                |
| 新增测试    | `packages/engine/tests/test_quality_profile_terms.py`、`test_quality_profile_numbers.py`、`test_quality_profile_calendar.py`、`test_quality_profile_comparator.py`、`test_quality_profile_firing.py`、`test_quality_profile_limits.py`、`test_quality_profile_imports.py`（均同tests目录） |
| 新增fixture | `tests/fixtures/quality/profile-v1/lexical.json`、`numeric-oracles.json`、`calendar-oracles.json`、`comparison-matrix.json`、`firing-cases.json`、`manifest.json`（均同profile-v1目录）                                                                                                    |
| 文档证据    | `docs/iterations/T05/`本阶段两规格与原合同必要状态；`docs/reviews/T05/`独立review/实际日志/输入hash。新扩展文件先报精确路径，不泛化整个目录                                                                                                                                                |

现有definitions.py/rdf_terms.py/planning.py/comparison.py/renderer本阶段不修改、不用于新value转换；旧私有草稿不是获批执行schema，之后接线再决定唯一适配。无新增依赖（RFC grandfathered固定名单随rule_terms与fixture受审，不在线取registry）；不设置任何进程全局解析/数值策略。

## 6. 阶段实现后必要证据（现在全部未跑）

| 机制验收            | 必须真正执行与对照的内容                                                                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| lexical/type        | 每类型正反、ASCII/fullmatch、空串/空白、XML1.1 S与L差异、simple/string term、surrogate/NUL/FFFE边界、int越界/非负-0、decimal禁指数、合法+INF分类；原source不被规范化                                               |
| labels/IRI          | 全ABNF分支/privateuse/grandfathered、只well-formed不registry-valid/valid层筛选、大小写/raw保留/不同标签X6；IRI identity与已验证入口precondition，明确未证明完整RFC3987 parser                                      |
| numeric             | 6×6有序混型×6、1/2/3真值签名、2^24/2^53/decimal0.1、巨大整数、ties两侧/奇偶、normal/subnormal/最大有限/溢出/±0/远指数；固定IEEE hex位模式及独立有理构造oracle，杀死binary64→32双重舍入；不由被测helper生成expected |
| calendar            | 0000/-0000/-0001、负世纪/跨年闰日、>9999、全部秒精度/24点/月年进位、非法60/14:01、Z/±00:00/无TZ、date/dateTime跨域；day与分数独立oracle，杀死微秒截断/机器TZ/错误负年除法                                          |
| complete groups     | 零匹配坏常量仍失败；false后坏comparison；后一head坏/后一binding坏/最终输出预算坏都无partial；同输出两firing保留、重复head/when位置保留、阈值不入basis；缺head/换binding/丢比较/换policy/basis污染组复核失败        |
| limits/security     | 每类阈值±1，幂/乘/GCD/序列化前fail，极端指数只做有界判定，字符串/整数扫描有界；错误首位/真实source及无index不伪造；unknown/internal不降用户错误；不会读网络/Store/文件或改全局策略                                 |
| imports/regressions | 新机制import不触旧parserfilter，旧四导出行为兼容；独立子进程只用于import全局副作用核对，无GUI。既有quality输入/草稿测试保持                                                                                        |

fixture manifest列原输入、手工/独立oracle推导来源、profile/pin、bytes/hash，不取被测输出回填expected。阶段实际运行定向7组测试后`npm run check`（代码/测试变更必须全check），失败原件保留；只有新修改/失败/未解风险才复测。代码/测试/预算同候选独立agent复核；后续指定两模型资源预约、双方新完整审查、push/PR/CI/正常合并及远端证据仍按原门，不以私有阶段单测替代。

## 7. 原完整FR验收仍未证的格与后续接线

| 原范围           | 本阶段最多建立什么                             | 尚未证明／真实owner接线                                                                                                                         |
| ---------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| FR500 检查项目   | 纯机制返回/安全失败                            | 真parse/SHACL/规则聚合、Job状态/保存版本/公共分页，I05/T01/T01-main/I06真实入口                                                                 |
| FR501、R01–06    | 给定binding比较/多head原子及组内差异           | 真RDFS→单阶段匹配、无反馈、保存顺序、撤回/多依据、source变后实际重算与历史，I05唯一执行器/T01失效发布                                           |
| FR502            | 给定完整组的when/comparison/head/basis内部一致 | 真图成员/全部触发/真实producer授权与全source/proof/hash认证、T08引用，I05/T01/T08                                                               |
| FR503            | 真source位置的私有安全类型                     | 实际概念/数据/规则跳转、失效后定位、新受限诊断及当前授权，T01与I06/main；不在旧params塞字段                                                     |
| FR504、V01       | 不更改K/D/R消费者policy                        | 五模板空白项目创建编辑/启停/版本/真实违规→修复→复验、asserted/选定derived双范围，日期/langString shape未支持和其他C格真实合同/证据，I05/T01/I06 |
| FR505            | 全类型值比较与给定绑定多结论机制               | 真测试输入/预期/actual/错误位置、真实join同告警、全部完整输出/trace，原22例/T09批准873数据真实执行；不以纯夹具证明actual                        |
| D/FR006 生命周期 | 无Store写入、整批返回                          | 保存即失效、启停/删除依赖、迟到保历史/不current、取消/deadline/重试/原operation幂等、undo/重开/崩溃与payload逐出/历史隔离                       |
| O01及跨模块      | 不做闭世界反推                                 | 真实缺失显示未记录，T06消费新鲜结果、T08真实trace、T09迁移/真人、T10传输重跑                                                                    |
| 包/平台/发布     | 标准库纯模块与本机无窗口check                  | 实际包依赖收集/T03、原生Windows/macOS/隔离平台与凭据安全/I06，指定双审/CI/远端/完整父验收；新模块可打包不等于产物已运行                         |

I05真实批准版本及精确移交后，唯一执行器将调用这套机制；未来semantic.py/scopes/execution/resources、query/turtle/adapter/旧tests/samples仍按root登记原owner/代改，不复制第二比较器或偷偷合并C4。T01负责canonical/Store/worker及已新交main基础四文件，I06保留preload/env/App/style；公共定义/references/revision/source/诊断方法、main业务呈现、包/限额/最终新implementation均须同版正式对接。

## 8. root一次授阶段需固定的对象

以本计划与profile的固定commit/hash、上列7代码路径/7测试路径/6fixture路径、mechanism-budget/1护栏和私有无入口边界为一次申请。明确授予后直接完成代码、真实必要检查、独立内审和可恢复证据；不再问Q6、不取得future4、不开GUI、不改协议/依赖/公共路由或宣称FR完成。预算是拟防护上限需本次一并冻结，未测容量不量化；若实现发现需要新路径/预算突破或共享接口，先完成其他独立部分再报具体差异，不能通过扩目录/抬全局限制绕过。
