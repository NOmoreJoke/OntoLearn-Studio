# T05 同一执行器扩展与真实 trace 适配合同草案

状态：**完整交接提案，待 I05/T01/T00 逐项接受；不是实施、公共格式或文件责任已生效**。依据原 FR-500–505、附录 C/D/G.2；父完整 P0、完整类型/取值支持矩阵、解释、生命周期和指定双审保持。

## 1. 已实际读回的来源与生效门

I05 `docs/reviews/I05/t05-semantic-ownership-release-proposal.json` 已全文读取，SHA256 `eb9ee33a7588dc902189c5a13a02741f40cab3b3611c1e5b393108ad84618229`，记录的 head 为 `3c0b3bafcdab86159962ff3331bb161c40d349bc`；其状态明确 proposed_future_owner_offer_not_effective。

| 未来拟交路径                                               | offer 固定 SHA256                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------------- |
| packages/engine/src/ontolearn_engine/semantic.py           | 7a83a1236c5262578256cc01ac6c57318a3688ab2df76fefaa61fb60a6b93033 |
| packages/engine/src/ontolearn_engine/semantic_scopes.py    | 5bec13ea42db3a9fbc04df3895fceb6945508b31e74e07b96fa98b56ac47fb5a |
| packages/engine/src/ontolearn_engine/semantic_execution.py | db9729f9f87ddb8fb7b6747d5ee3b1f371d041fdf6df28d78cd7b7268b246913 |
| packages/engine/src/ontolearn_engine/resources.py          | cfba5cc0b9b8dd83bc8023d0f090bc5db253e0c105a810394d61fce8b25e0268 |

T05 **有条件接受未来维护范围**：同一个执行器的 FR505 比较/多输出、选中结果认证、严格定义解析和执行身份版本。须原owner实际释放、T05实际核对、独立复核及root登记生效；目前只读报告，未读取/复制/导入/执行这四个未批准候选文件。三个semantic执行器文件为I05新增，resources.py在批准5f中已有，但其I05候选增量未批准；当前不作实验组合。

实际适配须先取得 I05 同版门禁合并，再更新批准基线并核对四文件身份；或取得root对独立实验来源隔离及完整组合新双审的明确授权。当前未有后者。I05 C2其余query/samples/tests继续原owner；任何临时回收必须逐文件协调。未提供 semantic_query/turtle/samples/error_adapter、既有tests、contracts、worker/protocol、锁/构建/入口/CI责任；遇到这些路径的新需求必须精确再交接。

## 2. 当前真实接口与本线差距

以下是offer及后续固定26负责人事实响应（见第11节），不是本线已消费/实测该代码：

- Rule(id, when[1..16 triples], then单triple)，id长1..128，scoped execution至多100条规则。Triple是三个URIRef/Literal/Variable项；精确位置限制与字面量白名单仍需批准源码/实测读回。
- reason(Graph, tuple[Rule,...])先有限RDFS，全部自定义规则读取同一个冻结闭包，输出不反馈规则/RDFS。
- evidence每项精确rule/result/inputs/basis；inputs保持when顺序，basis是该匹配inputs已记录proof的原始断言/公理并集再排序，不是全producer输入、全部路径或最小证明；rdfsEvidence单列。rules保留全部实例化输出，不等于新增知识差集。
- 保存定义严格enabled/when/then，references可选；未知compare/multi字段拒绝，不跳过。disabled不执行。
- semantic_scopes._selected_output按原规则和冻结输入检查已有selected evidence的内部一致性；它不单独认证授权/producer或全局完备性，权威Store另验证成功producer及payload/rows/身份。不重算替换历史。
- finite4载荷的implementation/version/snapshot hash及Store认证producer绑定必须准确；扩展须新语义版本和完整current/history/失败原子发布回归。

本线的schemaVersion/kind/id/revision/label/conditions/conclusions只是私有编辑payload，**不能直接喂当前严格when/then解析器**。T01须确定唯一持久化包装与references派生；T05后续仅在同一semantic_execution入口适配。T00协调接口设计；canonical/schema/注册表当前由T01唯一维护，剩余bridge由I06按第8节生效清单维护；不注册第二协议、Python入口或公共schema副本。

## 3. 同一 Rule 的扩展建议

推荐保持现有Rule与reason核心，单次三元组匹配后增加受限比较和多结论实例化；不引入第二推理器。为减少未移交samples调用受影响，可评估保留原三个构造参数、添加内部可选comparisons及additional_then；输出为原then加额外结论。该命名仅为内部候选，不是新公共JSON格式；最终由owner以同一版本化规范确定。

1. when只含类型/属性存在三元组模式；所有变量先由同一冻结断言+RDFS输入绑定，保持每个三元组条件原顺序。
2. 比较条件是合取，支持eq/ne/lt/le/gt/ge；左右可为已绑定变量或合法RDF常量。比较不绑定新变量，无代码、函数、聚合、否定或递归。
3. 同一次绑定评估全部比较；满足后一次实例化所有结论。类型结论和受控对象/数据属性结论保留同一规则/版本/绑定，不拆成多条规则。定义与实例化均校验变量闭合、IRI/字面量位置、引用和控制属性。
4. 任一结论或比较发生错误，整次任务失败且不发布部分current。输出仅推导图，不写断言/场景状态。重复事实集合去重，但全部独立有效触发依据保留。
5. 全部规则共享冻结闭包，输出不反馈到任何规则或RDFS。保存顺序、集合枚举顺序和hash seed不能改变完整事实/依据集合；展示排序另按获批规范。
6. 新定义/执行语义版本与旧finite4严格区分。不得靠列表长度猜测旧单triple/new多triple，不把未知字段忽略成旧规则。不支持版本明确拒绝，不伪造协议版本错误。

当前本线草稿上限128/文本4096不是I05实际when16/rules100/id128的能力声明；正式适配须消费唯一获批limits并在预览/任务入口一致校验。新comparisons/额外结论的实际预算需要测量后确定，不能默把旧caps当新业务容量通过线。

## 4. 完整类型支持矩阵提案

下表是**待采用的比较语义建议**，不是3c0b执行结果或Q6采用。原Q6-01历史报告列出常见类型，但本offer没有逐datatype实测；批准版本到位后要逐行读回真实支持/拒绝及精度/词法边界。不得以只跑小整数缩窄实际支持。

后续固定26事实响应明确：graph term门不等于FILTER政策；float/double都转Pythonfloat、date值转换剥时区，FILTER错误可False丢行。下表的精度/时区/失败建议因此更不能按现库已支持理解；须逐项接受第11节链接的D表。

| RDF值类别                        | eq/ne建议                                                                                       | lt/le/gt/ge建议                                                                  | 必测正反例/边界                                                                     |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| IRI                              | 完整IRI同一性；不隐式解引用/大小写折叠                                                          | 不提供语义大小顺序；明确类型不兼容                                               | 相同IRI、仅大小写/尾斜线差异、IRI与字符串不同                                       |
| plain / xsd:string               | 原始Unicode码点序列，区分大小写/空格，不trim或自动NFC                                           | 确定的Unicode码点词法序，绝不转数值或用locale                                    | 空串、中文、组合字符、字符串10与2不按数值比                                         |
| rdf:langString                   | 字面值加规范化语言标签；不同语言不相等                                                          | 同标签按码点词法序；不同标签需明确不兼容                                         | zh/zh-CN、标签大小写、同词不同语言                                                  |
| xsd:boolean                      | 仅布尔值域，true不隐式等于整数1                                                                 | 不提供业务大小顺序                                                               | true/false及合法词法、与数字1/0不串型                                               |
| xsd:integer                      | 精确整数值                                                                                      | 精确整数序                                                                       | 本22例中的18格、大整数/负数/0/资源上限                                              |
| xsd:int                          | 值语义；越界词法无效                                                                            | 值语义                                                                           | 32位边界及越界、负值                                                                |
| xsd:nonNegativeInteger           | 值语义；负词法无效                                                                              | 值语义                                                                           | 0、正值、负值拒绝                                                                   |
| xsd:decimal                      | 精确十进制值，避免二进制float中转                                                               | 精确十进制序                                                                     | 0.1、负小数、相同数值不同有效位、极大/极小指数或合法词法边界                        |
| xsd:float                        | 必须先明确按声明值域解释，不能默认Python double等于float32                                      | 有限值序                                                                         | 32位舍入、相邻值、±0、溢出/下溢、NaN/INF策略                                        |
| xsd:double                       | 按声明有限值语义                                                                                | 有限值序                                                                         | 相邻64位值、±0、大整数跨精度、NaN/INF策略                                           |
| xsd:date                         | 同型可确定日期值；时区语义明确                                                                  | 双方均有时区时比较规范化值，均无时区时比较同一局部日历域；混合时区信息不全不猜测 | 跨日时区、闰日、无时区/带时区混合、非法日期                                         |
| xsd:dateTime                     | 同型可确定时刻；不默认本机时区                                                                  | 均有时区规范化比较；均无时区用同一局部域；混合信息不全明确不兼容                 | 相同时刻不同offset、微秒/精度、夏令时文本不引入系统时区                             |
| 不同numeric datatype             | **待单一政策采用**：推荐比较各声明datatype实际表示的精确值，不隐式丢精度；integer/decimal须精确 | 同左，float/double的实际表示与跨型提升需owner明确                                | integer1/decimal1相等；decimal0.1与binary double0.1的政策；2^53附近；float32/64差异 |
| 不同非numeric值域                | 建议eq=false/ne=true，禁止字符串数字/布尔数字互转；时间可比域需单独判定                         | 明确不兼容，不默转字符串或跳过                                                   | 字符串1对整数1、boolean true对整数1、IRI对同文本字面量                              |
| 未支持datatype/无效词法/非有限数 | 区分合法但不支持与非法输入；不编造false通过                                                     | 同左                                                                             | 未知datatype、非法integer/date、NaN/INF/非有限转换                                  |

跨numeric精度是待采用的具体技术决定：若改选标准数值提升策略，必须列出精度丢失例的实际可观察含义并通过Q6，不能一面称精确一面悄悄舍入。上表的建议没有在本线执行或变成隐式默认。完整支持矩阵必须包括每格真实结果或明确受限错误及成本/范围处置，不得用“22例通过”关闭。

## 5. 真实 trace 与22例 oracle的适配

- 所有真实输入只来自批准Store认证的不可变producer快照、原始规则/版本、ontology和facts；不得从调用方自报context或T05 expected构建“真实依据”。
- 保留现有trace的rule/result/inputs/basis和rdfsEvidence来源含义，inputs的when顺序及匹配inputs既有proof并集的basis/排序原样承接；不能补无关producer事实，也不能改称全部可能证明或最小证明。固定26的该疑问已由负责人响应关闭；C3稳定witness和新trace仍须真正批准版本及逐项接受。
- 比较依据必须额外可见：实际绑定值、operator、阈值/右值、比较类型/语义版本、对应原规则条件位置。它们与when三元组输入区分，不能伪称阈值是输入图事实；公开形状由唯一owner确定。
- 多结论每条结果都关联同一个完整匹配和比较依据，不能把两个不同告警/两条规则拼成一次触发。相同输出多次触发必须完整保留各依据。可采用一个firing记录含全部结论、再按原result字段投影；也可每结果记录共同firing引用，但必须认证同一绑定及全部应有结果，不能只验其中一条。
- 新selected一致性检查须绑定**原producer的原规则/语义**，核对所给firing的全部when实例、比较判定、同binding全部heads及对应basis；不得据此冒称授权或全局匹配完备性。Store另认证真实producer及成功终态/原快照/完整implementation/依赖/定义与内容hash。不能调用reason重算替换历史或拿当前修订规则证明旧结果。原身份历史读取有schema/payload条件；新任务消费historical仍要求整个implementation相等（含lock），不等于读回后可自动跨版本消费，也不重签旧结果。
- 新22例只对照**全部自定义规则输出**。若执行器载荷包含断言/RDFS/规则组合图，需用真实来源分层明确抽取rule部分并核对trace覆盖，不能直接把expectedRuleOutputs说成全部闭包。RDFS单列另外核对原R-04等用例。
- 18比较格保持每次完整两条when输入及实际operator判定；多结论例两输出共享原四条when依据；JOIN例不允许跨alarm绑定；禁用与缺属性仍不能产生实际trace。没有结果时显示未记录，不能把合法join无解误作定义变量未绑定错误。
- T05显示模型只适配获批公共响应，T08只引用真正可验证的trace；没有凭据/模型外发权限因trace存在而扩大。

## 6. 失败原子语义、错误和生命周期

全解析/类型与引用/预算校验后再计算；任何未绑定变量、无效结论、非法词法、比较类型不兼容、预算/取消/执行错误都不得发布部分成功current。中间集合只在worker内存，正式断言永不修改。失败/取消保留已有明确已提交数据与历史，不把旧stale结果恢复成current，也不删除原断言或历史。

发布前复验项目/快照/规则/约束依赖和执行身份，迟到只保历史；成功结果与持久终态/真实resultId经现有Store/Job边界。响应丢失先按实际持久marker/result/job对账，不自动重跑正式写入。T01保存规则/启停/修订即失效，重算只替换当前推导；唯一依据删除撤回，多依据仍在保留。

现有批准错误目录可承载部分边界：SEMANTIC_INPUT_INVALID(field=rule)、UNSUPPORTED_CAPABILITY、UNSUPPORTED_CONSTRUCT(datatype/literalValue/ruleOutput)、RESOURCE_LIMIT(semanticInput/semanticWork/semanticResult)。目录另有ruleChain/ruleRecursion枚举，但固定26的adapter没有对应reason映射，链当前是warning；不得据枚举存在声称已接通。新增比较/多head的精确reason×producer×stage×origin→现有DTO建议与额外路径见第11节M/P表，须原adapter owner与T01 canonical接受。不借protocol VERSION_INCOMPATIBLE表达语义版本，不发明ruleComparison；未知/不可信故障维持Internal，不向错误参数加原值/路径/堆栈。

## 7. 实施与同候选验收顺序

1. owner逐项接受本合同或给出具体差异，确认类型/预算/trace/错误及T01唯一包装；不把四路径offer当生效。
2. I05批准版本合并、根实际生效交接后，更新本线基线，读取真实源码，确认四路径足够；必要共享/既有test改动另逐文件释放。
3. 在同一执行器内实现扩展，更新语义版本与严格解析/selected认证，不增新进程/入口/公开schema副本；全部模型与工具仍共用真实领域服务。
4. 实跑22 oracle全部输出/每条真实依据、完整类型矩阵、R-01–06/V-01/O-01、保存即失效/禁用撤回/多依据/历史/迟到/错误原子性及预算取消。旧有限语义与包内/外联拒绝/当前历史选择回归不得丢。
5. 引入新依赖/包内范围按原AGENTS实测，当前桌面禁GUI保持；最终刷新实际develop、固定base/head、指定双新模型全审、意见处理、push/PR/真实CI/正常合并/远端及完整父验收。局部合同/数据/测试不能关闭本任务。

## 8. 当前已生效责任补记（操作政策）

已在安全边界全文读取总控新版 developer-common-instructions.md（SHA `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`）；AGENTS仍 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。第2节T00指接口设计/集成协调角色，**实际当前canonical与接线文件owner按下列生效清单，不据角色抢写**：

- T01：storage.py；job_store.py、coordinator.py、`packages/engine/src/ontolearn_engine/__main__.py`、packages/contracts/python/contract_v2.py；contracts/src/index.ts、v2.ts及v2/schema、registry、errors、fixtures、binding-regressions.json；desktop/main/engine.ts。
- T03：packages/engine/pyproject.toml、uv.lock、scripts/build-engine.mjs、packages/engine/entrypoint.py。
- I06：main/index.ts、task-service.ts、preload/index.ts、renderer/env.d.ts、App.tsx、style.css。
- I05：其余未交路径；本合同四语义文件仍只是未来offer，未对T05生效。

这次责任政策更新不代表未批代码/格式已批准；未改产品、未重建Goal，不仅因此重跑无变化测试/重开外审。必要修改仍逐精确路径交接，旧冻结树/输入保留原字节。

## 9. 标准值域参考与仍待采用的应用政策

`xsd:float`与`xsd:double`的声明值域分别基于32位与64位浮点；这解释了矩阵中的精度边界，不证明当前库已按这两个声明精度执行。[W3C XSD 1.1 Datatypes](https://www.w3.org/TR/xmlschema11-2/#float)

RDF term equality与值相等不同，因此即使比较判定两值相等，也不能据此合并原RDF term、重写snapshot事实/身份或改变输出三元组去重语义。[RDF 1.1 Literals](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal)

SPARQL有自己的数值提升、操作数匹配和字符串码点比较规范。本合同的受控规则比较尚未采用该整套政策；IRI/布尔排序和跨numeric精度建议可能与SPARQL不同。owner需明确是否要求规则与查询FILTER同语义；如采用SPARQL路径，应同步精度/类型错误和跨入口正反例，不允许声称“标准兼容”却混用另一值比较政策。[SPARQL 1.1 Operator Mapping](https://www.w3.org/TR/sparql11-query/#OperatorMapping)

负责人后续已确认：rules未扣除断言/RDFS，图去重仍保留不同匹配evidence；同term可有asserted+rule或rdfs+rule来源，RDFS本身与原始输入不重叠。正式显示须分开完整规则输出、新知识差集和trace，不把同事实写回断言或改称全新知识；具体投影/字段仍待采用。

## 10. C2 依据不确定性的新依赖事实

总控随后实际通知并由T05只读核对I05报告：固定实现 `26eb632f0e1210b03ac3aef4cfd71fdc4a0c5222`、冻结C2 `2e337854838191fab09c7a584f5aa73d0939557a` / 输入manifest `31bd67f0a006d3423ed3fa0494e2b36a4c9963be8d7ba6cc7ab7f124aa7e55ef` 的6个新进程seed1/2/3/5/7/11，在相同源码/锁/输入下结论集合相同，但domain/range的rdfsEvidence及下游rule basis可出现两种有效support。原B1要求完整可观察结果确定，故C2停止派发/推送；没有创建C2指定外审任务，不能把未创建说成审查通过或不通过。

证据来源为I05 `docs/reviews/I05/evidence/c2-basis-counterexample/{manifest.json,finding.json.raw}` 及 `round-2/observed-outcome.json`；T05实际只读这三份报告，未读/解包/导入/执行其中列出的产品或probe脚本。报告源和哈希、有限验证范围见本线 `docs/reviews/T05/semantic-dependency-c2-receipt.json`。这是I05独立probe的事实，不是T05重跑证明，也不是新类型/trace政策已采用。

I05正准备C3最小确定性witness修复及新语义身份，当前尚无可由T05采用的批准C3。第1节offer及四个hash仅保留为历史固定来源，**未来交接须重新核对真正批准候选的源码hash、语义身份和selected认证**；不得将旧首次witness行为或旧hash固定成最新不变约束。四路径仍未生效，责任不因本记录转移；原C2、报告和本线既有UI输入保留。

确定性修复必须保留原解释范围，不自动等于枚举全部RDFS可能证明。RDFS代表依据如何稳定选择须由owner按新候选精确回应，与同规则独立匹配/多结论的真实依据要求分别处理。T05不能通过只比较结论集合、忽略依据差异或补写依据来隐藏该缺陷；正式联验应核对同版完整输出/真实依据稳定性、历史producer语义隔离及源变后的真实变化，不把跨进程选证差异误记成上游数据变更。当前不因依赖消息重跑未变化的UI/输入测试。

## 11. 收到固定接口事实后的最小待决表

总控已实际转交固定26负责人响应及独立事实审计，本线全文核对三份报告及其hash；此前basis、规则输出和selected/Store职责的事实疑问按第2/5/9节更正，不等于采用新方案。完整来源收据见`docs/reviews/T05/owner-interface-facts-receipt.json`。

后续只接受[负责人逐项决策表](owner-decisions-after-interface-facts.md)的D1–D9、M1–M16和P1–P10明确答复：精度/时区/非有限/失败、同binding完整heads与比较trace、producer/consumer版本分区、现有DTO及精确额外路径。所有提案仍待接受，未变更公共协议/代码/责任，未读或运行未批准C3，原Goal仍blocked，旧固定609及原报告不改。
