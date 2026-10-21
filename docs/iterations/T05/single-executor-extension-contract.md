# T05 同一执行器扩展与真实 trace 适配合同草案

状态：**完整交接提案，部分技术方向已获I05/T01回复，Q6、公共格式及实际交接仍未生效，原Goal仍blocked**。依据原 FR-500–505、附录 C/D/G.2；父完整 P0、完整类型/取值支持矩阵、解释、生命周期和指定双审保持。现行接受项/缺口以第11节当前决策表为准；旧来源/提案保留历史，不将回复等同实现。

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
6. 新定义/执行语义版本与旧finite4及C3 finite5严格区分；比较/多head需更新身份，不能沿用C3。不得靠列表长度猜测旧单triple/new多triple，不把未知字段忽略成旧规则。不支持版本按实际入口明确拒绝，不伪造协议版本错误；当前跨implementation新消费为IDENTITY_CONFLICT，未来语义adapter仍待批准。

当前本线草稿上限128/文本4096不是I05实际when16/rules100/id128的能力声明；正式适配须消费唯一获批limits并在预览/任务入口一致校验。新comparisons/额外结论的实际预算需要测量后确定，不能默把旧caps当新业务容量通过线。

## 4. 完整类型、六算子与消费者矩阵

现行具体表为[比较算子、跨域及消费者矩阵r2](comparison-operator-consumer-matrix-r1.md)，取代本节早期宽泛建议；旧412版本仍在Git。尤其早期“不同非numeric eq=false/ne=true”**已被I05明确否决**：除D3明确numeric混型，未定义跨域/操作在eq/ne/lt/le/gt/ge全部整任务M3失败，不当false/true或合法无匹配。

I05技术选择同一执行器内独立operand validator/comparator，不复用FILTER bool/Literal排序，不改变query/FILTER/cast。D3推荐严格词法精确有理数→直接binary32/64 nearest/ties-even→精确表示值比较；D4推荐独立Gregorian日序＋完整秒精度、显式offset/无TZ分域、date起点、date/dateTime不互cast。定义常量与闭合先验，每个完整binding的全部comparisons校验，不因先false隐藏后错。

上述是**技术答复，不是Q6采纳、规范pin或真实执行证据**。新矩阵补齐同域S/L/I/B六operator、全部有序跨域格及graph/query/SHACL用途；S/L算子、合法语言标签间的可比域、IRI/boolean仅eq/ne及具体消费者支持为T05待审政策；simple与显式xsd:string同一RDF1.1抽象term不是可选合域。SHACL须分别保留K数量/in、D精确datatype及适用词法、R自身SPARQL范围关系非true含type-error的违规结果，不能套D3/D4/E3，待具体审定。图门先于comparator且可能受宿主值范围限制，须同版reason/selected入口与消费者保真政策，不能全局关闭ill_typed/normalize，也不能靠窄拒绝关闭原FR505/SHACL范围。

真实验收须覆盖六numeric全部有序混型、2^24/2^53、0.1、巨大整数、ties奇偶、normal/subnormal、±0/溢出下溢，及年零/负年/大年份、闰日、24:00、完整秒/offset/有无TZ、原term与持久/selected一致性。每格提供真实结果或获批受限错误及成本证据；原22例只作输入oracle，不代表完整矩阵已通过。D8计费点已技术接受，阈值仍待测量，见当前决策表。

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

已在安全边界全文读取总控新版 developer-common-instructions.md（最新SHA `ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff`，原b24的15574B逐字保留为前缀）；AGENTS仍 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。第2节T00指接口设计/集成协调角色，**实际当前canonical与接线文件owner按下列生效清单，不据角色抢写**：

- T01：storage.py、worker.py；job_store.py、coordinator.py、`packages/engine/src/ontolearn_engine/__main__.py`、packages/contracts/python/contract_v2.py；contracts/src/index.ts、v2.ts及v2/schema、registry、errors、fixtures、binding-regressions.json；desktop/main/engine.ts。
- T03：packages/engine/pyproject.toml、uv.lock、scripts/build-engine.mjs、packages/engine/entrypoint.py。
- I06：main/index.ts、task-service.ts、preload/index.ts、renderer/env.d.ts、App.tsx、style.css。
- I05：其余未交路径；本合同四语义文件仍只是未来offer，未对T05生效。

这次责任政策更新不代表未批代码/格式已批准；未改产品、未重建Goal，不仅因此重跑无变化测试/重开外审。必要修改仍逐精确路径交接，旧冻结树/输入保留原字节。

## 9. 标准值域参考与仍待采用的应用政策

`xsd:float`与`xsd:double`的声明值域分别基于32位与64位浮点；这解释了矩阵中的精度边界，不证明当前库已按这两个声明精度执行。[W3C XSD 1.1 Datatypes](https://www.w3.org/TR/xmlschema11-2/#float)

RDF term equality与值相等不同，因此即使比较判定两值相等，也不能据此合并原RDF term、重写snapshot事实/身份或改变输出三元组去重语义。[RDF 1.1 Literals](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal)

SPARQL有自己的数值提升、操作数匹配和字符串码点比较规范。I05本轮已明确选择规则独立operand/comparator，不采用FILTER bool或Literal通用排序，也不改query/FILTER/cast。本规则方案不宣称整套SPARQL同义，精确数值和日历仍待Q6/norm pin；未来若要求统一，须另接受消费者政策/路径及跨入口证据。[SPARQL 1.1 Operator Mapping](https://www.w3.org/TR/sparql11-query/#OperatorMapping)

负责人后续已确认：rules未扣除断言/RDFS，图去重仍保留不同匹配evidence；同term可有asserted+rule或rdfs+rule来源，RDFS本身与原始输入不重叠。正式显示须分开完整规则输出、新知识差集和trace，不把同事实写回断言或改称全新知识；具体投影/字段仍待采用。

## 10. C2 依据不确定性的新依赖事实

总控随后实际通知并由T05只读核对I05报告：固定实现 `26eb632f0e1210b03ac3aef4cfd71fdc4a0c5222`、冻结C2 `2e337854838191fab09c7a584f5aa73d0939557a` / 输入manifest `31bd67f0a006d3423ed3fa0494e2b36a4c9963be8d7ba6cc7ab7f124aa7e55ef` 的6个新进程seed1/2/3/5/7/11，在相同源码/锁/输入下结论集合相同，但domain/range的rdfsEvidence及下游rule basis可出现两种有效support。原B1要求完整可观察结果确定，故C2停止派发/推送；没有创建C2指定外审任务，不能把未创建说成审查通过或不通过。

证据来源为I05 `docs/reviews/I05/evidence/c2-basis-counterexample/{manifest.json,finding.json.raw}` 及 `round-2/observed-outcome.json`；T05实际只读这三份报告，未读/解包/导入/执行其中列出的产品或probe脚本。报告源和哈希、有限验证范围见本线 `docs/reviews/T05/semantic-dependency-c2-receipt.json`。这是I05独立probe的事实，不是T05重跑证明，也不是新类型/trace政策已采用。

C2通知时I05正准备C3最小确定性witness修复；后续已报告冻结C3及新语义身份，但当前仍无可由T05采用的批准C3（最新答复见第11节）。第1节offer及四个hash仅保留为历史固定来源，**未来交接须重新核对真正批准候选的源码hash、语义身份和selected认证**；不得将旧首次witness行为或旧hash固定成最新不变约束。四路径仍未生效，责任不因本记录转移；原C2、报告和本线既有UI输入保留。

确定性修复必须保留原解释范围，不自动等于枚举全部RDFS可能证明。RDFS代表依据如何稳定选择须由owner按新候选精确回应，与同规则独立匹配/多结论的真实依据要求分别处理。T05不能通过只比较结论集合、忽略依据差异或补写依据来隐藏该缺陷；正式联验应核对同版完整输出/真实依据稳定性、历史producer语义隔离及源变后的真实变化，不把跨进程选证差异误记成上游数据变更。当前不因依赖消息重跑未变化的UI/输入测试。

## 11. 负责人新回复后的接受项与缺口

固定26事实及独立审计来源仍见`docs/reviews/T05/owner-interface-facts-receipt.json`。新固定I05 ffc462b与T01 f51dd38文档已全文读回/验hash，当前来源与有限范围见`docs/reviews/T05/owner-design-responses-r2-receipt.json`；只用T01§1，不采用其余模块建议。本线没有读取文档指向的未批准C3实现/库/测试或运行候选。

[当前决策表](owner-decisions-after-interface-facts.md)逐项登记D1–D9、M1–M16及P1–P10：I05接受独立比较器、未定义跨域六操作失败、完整firing/单阶段、精确数值/日历技术方向及预算计费点；T01接受全组认证职责和严格三字段，澄清当前IDENTITY_CONFLICT、result_get/rows逐出与Coordinator授权边界。M4–7/M8b/c复用准确现有reason；M3/M8a/M9是未接线新reason，M10保留UNKNOWN优先及既有资源/network分支，不能用目录存在代替真实路由。

仍待：Q6采用及规范pin、矩阵新增S/L/I/B和graph/query/SHACL消费者格、真实全类型/精度/时区矩阵、D8阈值、新多head持久/public包装与M9分类。T01独立受限诊断`semantic.diagnostic.get`/`diagnosticRef`仅技术提案，未批准未实施，不加到现protocol2 params或成功rows，也不存在由此获批的protocol3。定位缺口保持明确。

四语义路径仍future/not-effective，P2/P3/P5/P6为I05未来代改、不移交，query不因D2扩大；P7/P8归T01，P9归T03，P10归I06。I05报告冻结C3 head3289d67（产品69598f3/测试b045）；总控此前报precheck ready，后续因I05报告term/selected反例已撤回条件外审派发，冻结输入保留；固定反例待总控/独立读回，未合并，不能作为批准依赖。未来比较/多head要新于C3 finite5身份，并重新核对真正批准候选hash/selected认证。原Goal仍blocked，本轮是明确授权的有限设计更新；原产品、输入、证据及全部实际验收门不变。

## 12. R1/R2修正与具体决定请求

总控独立设计复核17603B/SHA70909867a8786f181639810c3c40d188f92c2849311dd148f6bf55fce044705a指出旧383b96c矩阵的SHACL datatype/range混列及simple/xsd:string可选合域歧义。现矩阵§4分别给K/D/R合同与shape/data双侧手工见证，§2/3明确RDF1.1抽象term和source拼写分层；query/SHACL以自身合同正确为目标，不要求等同规则值政策，不以拒绝全部难值关闭FR504五模板/双范围/真实违规定位。

[技术接受请求与Q6决定单](q6-policy-decision-request-r1.md)给出TA-S/L/I/B/X/C及保留D3/D4接受项，Q-SLIBX/NUM/CAL/REC/CONS/LIFE逐项可采用/改写的具体组合、候选有日期REC及勘误登记、政策见证和真实未验门。仍待owner技术答复/Q6采用/实际公共包装与运行；这是有限文档修正，不是当前I05缺陷认定或指定双审Pass。原Goal仍blocked，不读取未批C3或重复产品测试。

## 13. T01已接受包装合同，仍缺I05逐格真实契约

固定b35cb4e T01回复（SHA3d300cf1070adf54f97fec45d060273f78d0e29fba9bbef502403466084b8d09）已全文读回，保留f51原接受，详见当前决策表§8/矩阵§6及Q6单补记。T01接受各consumer自己的profile、SHACL正常违规不改整Job E3、真实Job/result上下文/分页/hash/当前授权；完整implementation只分区不证明同义。D5/D8执行证据、唯一Store/原operation claim、全context幂等与原子性方向接受，阈值未测。M12当前IDENTITY_CONFLICT、未来UNSUPPORTED和诊断资源未批准未实施的界限不变。

I05须逐C格给实际入口、原输入/definition source、输出形状/新producer身份、有限预算/实际异常安全reason和完整成功失败golden，T01才按真实context接持久绑定；T01不猜通用异常、不决定执行器Q6。定位仅真实source有限section/index/reason，原值/路径不外泄；main呈现/公共诊断尚待共同冻结和真实接线。未改变公共协议/路由/路径所有权，未读未批实现或重测，原Goal仍blocked；FR504/505及全部原完成门继续保留。
