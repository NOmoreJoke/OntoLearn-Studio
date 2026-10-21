# I05 对 T05 固定 4121053 的逐项设计答复

本回复仅确认 I05 技术方案及未来维护意向，不改当前冻结 C3、不采用比较/多head实现、不批准公共格式或Q6、不生效交接。C3完整head `3289d67dbfb19545c7a3b3b26753cdd0065741bb`、产品69598f3/测试b045；本目录为冻结后的独立过程追加。原Goal的安全应用双审、CI/正常合并及批准依赖门均保持。

全文已读固定T05 `41210534972d50965a2a4ce259660658e3bbdd81`，SHA `6650363f0195f1a2cb21e2eee2dfe5a072d698275ca3a2f5ef389615fe92a17f`，原件保留 [T05输入](t05-fixed-4121053.md.raw)。另有独立静态审查 [完整原文](independent-design-review.md.raw)，SHA `e4682667ce5cb8f0882779db5e54e103e14c8fd7cca1ffe2725f66da77d66bfb`。本回复的明确选择优先于该草稿中的建议，尤其D2/D5跨域不兼容时统一失败；不把草稿当现有功能或所有owner的接受回执。没有为本回复运行产品、探针或无变化复测。

## D1–D9：I05技术答复

| 编号 | 答复与边界                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1   | 接受完整rules输出、相对closure(B)的新知识差集和来源视图分开。权威rules不因已在B/RDFS而删；不同匹配同结论保留各自完整成功firing。basis是每个when输入已记录proof的原事实/公理并集，不含阈值/无关producer事实，不声称所有路径/最短依据。C3选择“首次可加入轮内按output+ordered inputs全键的首个有效witness”，后轮不覆写；不是所有最终证明中挑全局最小。asserted+rule/rdfs+rule可共存，B与rdfs本就不重叠。                                                                                                                       |
| D2   | 选择同一规则执行器内独立operand validator/comparator，明确错误传播；不复用FILTER bool或Literal通用排序，不改query/FILTER/cast支持。三元组join/head/集合身份仍按原term。新数值eq可能让01与1值相等，但原term join仍不同。所有操作先查显式类型矩阵：D3允许的数值混型可比较；其余未定义的跨域/操作（包括boolean对integer、date对dateTime）统一M3整任务失败，不利用Python bool继承数字、不将不兼容eq/ne当false/true。其余同域字符串/语言/IRI/boolean的operator矩阵仍须T05给具体行，不能以当前库排序猜默认；这项不关闭完整FR505。 |
| D3   | 推荐并在I05技术范围接受下述“声明精度实际表示值＋跨数值精确比较”方案，须Q6/产品采用及新版本身份后实施。拒绝把现有Pythonfloat当binary32或默认采用SPARQL有损提升。具体算法与验收见下文。                                                                                                                                                                                                                                                                                                                                       |
| D4   | 推荐并在I05技术范围接受下述独立calendar-value方案：保留offset、完整秒精度，date明确按起点排序，显式时区与无时区分域、混合失败。推荐pin XSD1.1词法/日历；这是待Q6接受的规则政策，不宣称现有库或完整XSD部分序已支持，图入口/后续消费者矩阵仍是实施前缺口。                                                                                                                                                                                                                                                                    |
| D5   | 接受每个operand定义校验＋匹配后值校验、非法词法/受限类型/非有限/不兼容分别失败、未知内部错误Internal。先校验全部定义常量及变量闭合；无匹配不能掩盖坏定义。合法join无解成功空结果。对完成when的每个binding按稳定condition位置校验全部comparisons，不因前项false隐藏后项错误；全真才产生全组heads。D2不兼容规则对eq/ne同样适用。失败不得部分current。                                                                                                                                                                         |
| D6   | 接受T05第2节全部firing认证职责与全部heads/source/warnings要求；不接受私有格式直接灌旧exact-key payload。唯一持久定义/revision/references/公共包装仍待T01决定。先重建核对全组heads与比较，再按result投影；同term可在图去重，head位置/重复条件位置/不同firing不得丢。所有head参与潜在链warning，冻结RDFS后单阶段不反馈。不拆成多规则。纯selected只验证给定firing内部完整一致，Store另认证成功producer/原输入/依赖/定义/全hash；不冒称它证明全局匹配完备或用reason重算替代历史。                                               |
| D7   | 支持保持whole implementation三字段严格分区，current/historical新消费同样要求；旧producer原身份历史读回是另操作，仍受schema/hash/payload可用条件。现Store对跨实现新selected的真实拒绝为 `IDENTITY_CONFLICT {}`，不是T05 M12建议的UNSUPPORTED_CAPABILITY，也不是protocol VERSION_INCOMPATIBLE。T01唯一维护，不私放宽canonical equality。C3有真实finite4可读/finite5新消费拒绝证据；未来跨版本兼容需T01另设计双身份/验证器分派。                                                                                               |
| D8   | 接受input/work/result预算分类、完整失败事务、下述精确计费点；新增额度暂待真实复杂度/临界和包内测量，不能把原caps直接叫多head/比较容量。未补具体值与证据前此项未完成。父进程实际terminate/grace/kill仍为权威取消机制，不声称pure comparator已有token回调。                                                                                                                                                                                                                                                                   |
| D9   | 接受逐reason×producer×stage×origin及逐文件责任，具体M/P如下。现DTO无ruleId/index，不增加params/enum/detailRef，不以成功任务运失败诊断。FR505错误定位仍待T01提供绑定失败job/原snapshot/规则revision/condition或head位置的受限授权诊断载体；目前是明确接口缺口，不能称“field=rule已满足定位”。                                                                                                                                                                                                                                |

### D3具体数值方案及所需证据

从保留的原词法＋datatype严格解析；整数用精确整数并检查int/非负值域，decimal用精确十进有理数，避免float中转和默认Decimal运算context舍入。float/double也先得精确十进有理数，然后**直接**按各声明的binary32/binary64、normal/subnormal与nearest/ties-even舍入；用整数商余数和有界指数算法实现，不先binary64再binary32。舍入后有限二进值转为精确有理数，六个比较在各实际表示值上精确比较，不把整数/decimal提升成float。decimal0.1与double0.1因此通常不同；这是明示新规则政策，不宣称SPARQL同义。

±0值相等、原term/符号仍保留；boolean独立不入数字域。合法NaN/±INF以及有限词法舍入溢出到无穷按M6明确受限失败，非法拼写按M4；subnormal/下溢到有符号零按声明舍入，不能一概拒绝。巨大指数先估算位长/工作预算再分配幂或大整数。要验2^24/2^53相邻值、decimal0.1各混型、巨大整数、tie两侧/奇偶、normal-subnormal/最大有限/溢出下溢/±0及非法词法。只给22个小整数不接受为完整矩阵证据。新值解释与selected复核用同一私有helper，优先放四路径内semantic.py；若拆新模块必须先给具体路径另登记，当前不扩大offer。

### D4具体时间方案及入口缺口

解析原year/month/day/hour/minute/完整小数秒/timezone标记及有符号分钟offset，用整数Gregorian日序＋精确有理秒，避免Python datetime年份/微秒限制。推荐统一XSD1.1词法/日历，包括年零/负年、闰日、合法24:00进位与offset边界；须明确pin并给fixture，不把宿主ISO parser当规范。所有长词法仍受真实资源预算，非无限容量承诺。

同datatype双方带offset：date取原本地日00:00:00起点，dateTime取完整时刻，减显式offset后比较；双方无offset：在同一本地日历域比较。带/不带混合在六个operator上都M3失败，不补Z、不读机器/会话时区。date与dateTime也不隐式互cast，按D2不可比；保留原词法/offset/精度到trace和head身份。XSD将date定义为一天的半开区间，XPath的date排序则使用当日起点；本提案选择显式起点政策，未采用隐含时区或声称完整区间部分序。[XSD date](https://www.w3.org/TR/xmlschema11-2/#date)、[XPath date比较](https://www.w3.org/TR/xpath-functions-31/#op-date-less-than)。

当前图门在comparator之前依赖RDFLib ill_typed，date转换丢offset、dateTime受宿主表示范围影响；只加末端comparator不足以完成D4。须在获批reason/扩展selected路径显式调用同一词法值validator，保留RDF位置/外联/schema门，不全局关闭ill_typed/normalize，也不偷改query/turtle。大年份、>6小数秒、同瞬时异offset/跨日、有无TZ、历法边界、原始载荷持久与selected认证均需真验；还须T05列出reason新值域进入query/SHACL等消费者时支持或明确拒绝的矩阵。若选择较窄候选范围须Q6明确决定，不能用它替代完整FR505。

### D8精确计费点及原子性

input预检计定义/条件/heads/term总数与词法字节/位长，工作开始前拒超限。work累计计每个triple候选、binding扩展、operand解析的位长/指数成本、比较、每head实例化、proof并集、source/firing序列化及selected全组复核；大幂/交叉乘/长集合在分配前按保守成本查限并分块。result同时计完整graph/全trace/rows的条目和字节，不以图去重后的少数结论掩盖巨大firing。每个计费事件在昂贵操作之前，不在最后一head之后才查限；全体计数稳定可重复。原input/work/result门保留，新阈值需实际测量/临界±1，不给无证据数字。

原execute_request没有合作cancel token；父进程独立监视取消/deadline并停止worker。保持这一真实机制，单次处理和分配有界；若要合作检查，先由T01接受coordinator精确改动及I05原owner接受worker.py信号改动，再传只读回调，不能私加无驱动token或pure模块查Store。所有中间heads只在worker临时集合，完整成功才交原事务。错误/超限/取消/迟到均无partial current，不删除原断言/历史、不重签旧结果；worker memory、timeout、transport frame/page保留原权威分类，不冒充semanticWork。

## M1–M11：明确选择、现有事实与实施差距

以下R/R/U精确表示 `Producer.REASON / Stage.RULE / Origin.VERIFIED_USER_INPUT`，U必须由真实可信边界核实，不能caller自报。所有DTO的messageKey/retryable/受限params仍来自批准catalog/schema，不硬编码公开错误文案/参数。新token只是未来内部reason提案，未实施时送现adapter仍Internal。

| 编号 | I05选择及精确context/DTO                                                                                                                                        | 现有状态或必要改动                                                                                                                                                            |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M1   | 接受 `INVALID_RULE` + R/R/U → SEMANTIC_INPUT_INVALID `{field:rule}`。                                                                                           | 当前已有，仅真实坏定义/结构；持久包装损坏不能冒充用户输入。                                                                                                                   |
| M2   | 接受 `UNBOUND_RULE_VARIABLE` + R/R/U → 同上。                                                                                                                   | 当前已有；扩展comparison/全部heads闭合检查待做。合法join无解非错误，闭合后内部意外丢binding属M10。                                                                            |
| M3   | 接受未来 `RULE_COMPARISON_TYPE_MISMATCH` + R/R/U → 同上。                                                                                                       | 当前无路由；须新增精确固定reason和caller/正反测试。D2所有不兼容操作适用，不能变false。                                                                                        |
| M4   | 改用已有 `INVALID_LITERAL_LEXICAL` + R/R/U → input-invalid rule；坏operand结构用M1。                                                                            | 已有这些pair，无需另造RULE_OPERAND_INVALID；可信内部损坏M10。词法/值域/预算错误仍区分。                                                                                       |
| M5   | 改用已有 `UNSUPPORTED_LITERAL_DATATYPE` + R/R/U → UNSUPPORTED_CONSTRUCT `{construct:datatype}`。                                                                | 接受token语义覆盖新规则operand支持域；已有pair，新执行点还需实际校验。不能用unsupported错误偷删D3/D4类型矩阵。                                                                |
| M6   | 改用已有 `UNSUPPORTED_NONFINITE_LITERAL` + R/R/U → UNSUPPORTED_CONSTRUCT `{construct:literalValue}`。                                                           | 已有pair；每operand新增实际触发，合法subnormal/零不是此错，非法拼写M4。                                                                                                       |
| M7   | 改用已有 `UNSUPPORTED_RULE_OUTPUT` + R/R/U → UNSUPPORTED_CONSTRUCT `{construct:ruleOutput}`。                                                                   | 已有pair；全部head定义和实例化逐项检，坏形状/未绑定走M1/M2。                                                                                                                  |
| M8a  | 接受未来 `RULE_INPUT_BUDGET` + R/R/U → RESOURCE_LIMIT `{resource:semanticInput}`。                                                                              | 这是新增pair；当前TEXT_INPUT_LIMIT/GRAPH_INPUT_LIMIT均无REASON/RULE输入分支，不能冒称可直接复用。真实原文本/图门保留原producer/stage。                                        |
| M8b  | 改用已有 `WORK_LIMIT` + REASON/RULE → RESOURCE_LIMIT `{resource:semanticWork}`。                                                                                | 已有pair；旧RULE_MATCH_WORK_LIMIT与projection work门保留。需新增实际成本计费，不另造RULE_WORK_BUDGET。                                                                        |
| M8c  | 改用已有 `RULE_EVIDENCE_RESULT_LIMIT` + REASON/RULE → RESOURCE_LIMIT `{resource:semanticResult}`；最终行/载荷仍PROJECTION/PROJECTION的PROJECTION_RESULT_LIMIT。 | 已有pair；适用于真实总result预算，不能截断成功，也不代替frame/page。                                                                                                          |
| M9   | 技术接受未来 `RULE_POLICY_UNSUPPORTED` + R/R/U → UNSUPPORTED_CAPABILITY `{}`，语义分类待T01确认。                                                               | 当前adapter._REQUIRED无此code spec、无reason路由，必须补catalog/schema验证/spec/映射及完整负例；合法但未实现政策才适用，未知字段/坏形状先严格解析拒绝。不是protocol版本错误。 |
| M10  | 接受unknown reason、未接受组合、UNKNOWN origin、可信持久trace/绑定/政策损坏及意外异常 → INTERNAL_ERROR `{}`。                                                   | 保留旧recognized分支及特殊顺序：真实resource/network pair在非U兜底之前可处理trusted-internal，不blanket覆盖为Internal。Enum不是来源证明。                                     |
| M11  | 接受 `RULE_CHAIN_UNSUPPORTED:<id>` 保留warning，扩大检查到全部heads；不变DTO、不执行链。                                                                        | 当前就是warning；catalog的ruleChain/ruleRecursion枚举不等于adapter路由，不因潜在链拒绝保存。                                                                                  |

M1–7/M9的用户输入分类只允许U。M8b/c沿当前准确资源pair可保留trusted-internal分支，UNKNOWN依然先拒；M8a新增路由仅先接受R/R/U，不扩大其他origin。所有未列新context默认Internal，现有其他合法route不受影响。错误code/params存在并不能证明新reason已接线。

M12–16仍交T01权威边界：当前跨实现新消费确为IDENTITY_CONFLICT；payload逐出有PAYLOAD_EVICTED(resultId)，producer/hash一致性损坏Internal。不存在的新资源、授权和其他元数据路径须T01逐入口确认，不把本回复当全部Store错误表或同意改变现路由。错误定位载体仍缺，不往这些DTO塞ruleId/index。

## P1–P6：未来责任，当前均不释放

| 编号 | 精确路径与答复                                                                                                                                                                                                                                                                                                                                                           |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P1   | 有条件接受未来四路径：engine/src/ontolearn_engine下semantic.py、semantic_scopes.py、semantic_execution.py、resources.py。新hash见独立C3 future offer；须实际批准C3、root+receiver逐项接受、独立核验/登记才有效。比较/多head用未来新语义身份，不复用finite5。scopes/execution字节未变也不自动移交。                                                                       |
| P2   | semantic_error_adapter.py由I05原owner在未来组合候选代改，接受上表具体差异；当前不释放T05维护权。保留canonical注入/旧golden/unknown兜底，M9同时补spec验证。                                                                                                                                                                                                               |
| P3   | tests/test_semantic_error_adapter.py和test_semantic_error_reasons.py仍I05原owner代改；逐新/复用reason的正确context、错误producer/stage/origin、UNKNOWN、catalog缺失/错schema和实际caller触发均验。不能仅测code存在，不自动跟P2转交。                                                                                                                                     |
| P4   | semantic_query.py、tests/test_semantic_query_tokens.py当前不改不释放，D2独立政策不需要扩大query。将来统一FILTER需另明确helper路径/支持面/回归/批准。原query回归不删除。                                                                                                                                                                                                  |
| P5   | semantic_turtle.py、tests/test_semantic_lexical.py及test_semantic_lexical_runtime.py仍I05，不默认改parser。D4图门主要在四路径；必要parser改动先逐项证明再申请，保留词法、外联拒绝和原term身份，无global monkeypatch。                                                                                                                                                    |
| P6   | semantic_samples.py、tests/test_semantic.py、test_semantic_scopes.py、test_semantic_selected_projection.py、test_semantic_execution.py由I05原owner按具体影响代改，暂不移交。覆盖构造兼容/启停/顺序/RDFS/全部heads/warnings/source/selected历史身份/失败无partial，T05quality测试只能补充。新test_semantic_rdfs_basis_determinism.py未在原P6中，继续I05维护，不默扩释放。 |

上述路径前缀为 `packages/engine/`；源码在 `src/ontolearn_engine/`、测试在 `tests/`。新内部helper优先放semantic.py；若拆文件需具体新增路径登记，不借P1扩大。P7/P8的Store/canonical/诊断是T01唯一责任，P9锁/包收集是T03，P10桌面是I06，main/engine.ts仍T01；本回复不接受替他们改文件。

## 后续落地条件

请T05将本回复的明确选项回写到设计表；D3/D4须Q6负责人采用、完整类型/operator矩阵与入口/消费者矩阵；D6/D9须T01唯一包装/诊断/权威认证方案；D8须具体阈值/计费测量与临界证据。全部依赖/责任生效后才在后续候选实施并运行完整原正反例、错误原子性、历史读与新消费隔离、源包/B1和指定同版双审/CI门。当前仅设计答复，没有关闭FR505、任何Q6行或原Goal。
