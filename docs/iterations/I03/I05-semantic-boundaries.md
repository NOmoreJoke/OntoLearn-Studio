# I05 语义错误与 SHACL 事实投影契约

依据为 PRD FR-006/203/401/500–505、附录 C/D，以及总控转交的 [I05 原始核对](../../reviews/I03/handoffs/I05-contract-handoff-20261020-source.md)。该输入声明 I05 纯模块检查点02a8c909；来源与逐字哈希见同目录 I05-contract-source.json。本次只修订有限 M0 契约，不采用 Q6 最终实现范围，不注册语义能力或新增方法。完成状态仍见 [status](../../reviews/I03/status.md)。旧6f35ffd候选保留，新契约必须验证并冻结新候选；未来指定双审不得沿用旧候选意见。

## 安全类别及其依据

`errors.json` 的 parameterMeanings 是有限类别的语义目录；键与 paramsSchema 枚举必须完全一致。新增类别仍只有一个有限枚举参数，无原值、URI、路径、查询、格式字符串、数量、堆栈或库异常。messageKey/retryable 固定，均为 false。需要行列定位或业务说明时另走已授权详情引用，不增加自由文本。

- `RESOURCE_LIMIT.resource=semanticInput`：真实语义文本/blob字节或输入三元组量；不是传输frame、数据类型错误或字节解码错误。
- `semanticResult`：总计算结果行、三元组、依据/证据载荷量；不是单页page，不能建议增加pageSize来解决。
- `semanticWork`：闭包累计工作、规则匹配或中间匹配集合预算；不是附录E行为actions/rounds，也不自动等同memory。
- `UNSUPPORTED_CONSTRUCT` 新增 rdfFormat/rdfConstruct/rdfsConstruct/datatype/literalValue/queryFunction/queryOrder/querySlice/ruleOutput/validationScope。原 shaclAdvanced 明确涵盖全部合法但非白名单的SHACL约束/特性；不能一律改称语法错误。sparqlForm只表达SELECT/ASK之外的合法查询形式，不吞并函数、排序或切片类别。

类别仅用于描述实际拒绝的原因，不表示相应构造已经支持或最终被产品淘汰。输入/结果/工作上限的实际数值由执行策略和真实测量另行记录，不将 I05 当前常量采用为 Q5 容量目标；查询文本LIMIT/OFFSET与服务稳定分页分别处理，不能静默移除查询切片。

## 当前 v3 细码的处置（优先于历史合码）

总控随后转交 I05 [typed-reasons-v3 原表快照](../../reviews/I03/handoffs/I05-typed-reasons-v3-source.md)，哈希见 I05-contract-source.json。该表声明真实来源分支已细分；I05 源码尚未冻结，仅报告123项定向回归，尚无本线核验的新检查点、全check或包内证据。本表明确公共契约，不将交接声明当成已冻结实现通过。未来检查点需对实际来源再次核对，当前不注册新公共方法。

| 当前内部细码                  | 公共去向与来源条件                                                                                                                |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| TEXT_TYPE_INVALID             | 可信适配器类型违约→INTERNAL_ERROR；公开参数入口已确认用户参数形状错→INVALID_REQUEST/field=params，绝不是资源超限                  |
| TEXT_INPUT_LIMIT              | 真实UTF-8字节量超限→RESOURCE_LIMIT/semanticInput                                                                                  |
| GRAPH_INPUT_LIMIT             | 实际输入三元组量超限→RESOURCE_LIMIT/semanticInput                                                                                 |
| INVALID_LITERAL_LEXICAL       | 已确认用户输入非法词法→SEMANTIC_INPUT_INVALID/真实入口；可信生成项违约→INTERNAL_ERROR                                             |
| UNSUPPORTED_LITERAL_DATATYPE  | 合法、未被ill_typed标记、候选列表外datatype→UNSUPPORTED_CONSTRUCT/datatype                                                        |
| UNSUPPORTED_NONFINITE_LITERAL | 已支持datatype但实际值非有限→UNSUPPORTED_CONSTRUCT/literalValue；不得把大而有限Decimal误归此类                                    |
| UNSUPPORTED_DATATYPE          | 模板中合法但当前不支持的datatype IRI→UNSUPPORTED_CONSTRUCT/datatype                                                               |
| RDF_TERM_INVALID              | 已知非法RDF主体/谓词形状；用户输入按真实入口SEMANTIC_INPUT_INVALID，可信生成项违约INTERNAL_ERROR，不借rdfConstruct                |
| RDF_TYPE_OBJECT_INVALID       | 当前领域事实形状要求rdf:type对象为类IRI；用户输入按真实入口SEMANTIC_INPUT_INVALID，可信生成项违约INTERNAL_ERROR                   |
| RDFS_TERM_INVALID             | 已知非法subclass/domain/range项形状；用户输入按真实入口SEMANTIC_INPUT_INVALID，可信生成项违约INTERNAL_ERROR，不借合法范围外类别   |
| UNSUPPORTED_RDFS              | 合法但范围外RDFS词汇→UNSUPPORTED_CONSTRUCT/rdfsConstruct                                                                          |
| SHAPE_TARGET_CLASS_INVALID    | 用户模板目标类非IRI→SEMANTIC_INPUT_INVALID/constraint；可信模板生成违约→INTERNAL_ERROR                                            |
| SHAPE_DATATYPE_INVALID        | 用户模板datatype对象非IRI→SEMANTIC_INPUT_INVALID/constraint；可信模板生成违约→INTERNAL_ERROR，不称shaclPath                       |
| SHAPE_PATH_INVALID            | 已确认用户模板非法字面量path→SEMANTIC_INPUT_INVALID/constraint；可信生成违约→INTERNAL_ERROR                                       |
| UNSUPPORTED_SHACL_PATH        | 新来源分支已确认合法单一inversePath且对象为IRI→UNSUPPORTED_CONSTRUCT/shaclPath；不能扩大为所有匿名路径均合法                      |
| SHAPE_PATH_UNCLASSIFIED       | 未安全分类的匿名路径→INTERNAL_ERROR/{}；不得归责用户、假称支持或返回检查通过                                                      |
| QUERY_RESULT_LIMIT            | 最终查询行量超限→RESOURCE_LIMIT/semanticResult，非page                                                                            |
| RDFS_RESULT_LIMIT             | 最终闭包三元组量超限→RESOURCE_LIMIT/semanticResult                                                                                |
| RULE_MATCH_WORK_LIMIT         | 中间匹配集合量超限→RESOURCE_LIMIT/semanticWork                                                                                    |
| RULE_EVIDENCE_RESULT_LIMIT    | 最终推导与解释证据条目预算超限→RESOURCE_LIMIT/semanticResult                                                                      |
| WORK_LIMIT                    | 累计闭包/匹配步骤预算→RESOURCE_LIMIT/semanticWork                                                                                 |
| FACT_SCOPE_CONTAINS_AXIOMS    | 可信事实投影混入公理→INTERNAL_ERROR；不能映射validationScope，不要求用户改合法scope或删除数据                                     |
| ONTOLOGY_SCOPE_CONTAINS_FACTS | 可信本体角色混入领域事实→INTERNAL_ERROR；不静默丢弃事实                                                                           |
| SCOPE_SELECTION_TYPE_INVALID  | 可信适配器类型违约→INTERNAL_ERROR；公开选择参数形状已知非法→INVALID_REQUEST/params                                                |
| UNSELECTED_RULES_PRESENT      | asserted选择却组装需执行规则；公开选择/参数组合已确认非法→INVALID_REQUEST/params；可信服务组装违约→INTERNAL_ERROR，不静默忽略规则 |

新表需要保留可信生产者/入口上下文；仅细码存在仍不能自动归责用户。原INPUT_LIMIT、RESULT_LIMIT、UNSUPPORTED_LITERAL、UNSUPPORTED_RDF、ASSERTED_SCOPE_REQUIRED不再从对应新执行分支产生，下一层适配器不得为新检查点继续依赖旧合码。未知库故障仍INTERNAL_ERROR。其余未替换代码沿用下表的真实来源条件；分类在来源分支产生，不解析异常文本、原查询或节点字符串。

## 历史30码及兼容来源边界

下表保留原交接的完整依据，供旧检查点审计和未替换细码对照；被上述v3替换的来源不再按旧合码建立新映射。它不是已实现的公共适配器。

| I05内部码                  | 公共去向与必须成立的条件                                                                                                                                                                                                                                             |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| EXTERNAL_ACCESS_DENIED     | NETWORK_FORBIDDEN/{}；真实SERVICE/FROM/imports或执行期I/O拒绝，不能带目标URL                                                                                                                                                                                         |
| INVALID_TURTLE             | SEMANTIC_INPUT_INVALID/field=syntax；真实Turtle语法失败                                                                                                                                                                                                              |
| INVALID_UNICODE            | SEMANTIC_INPUT_INVALID；field按真实入口为syntax/query/rule/constraint，不带无效字符                                                                                                                                                                                  |
| ABSOLUTE_IRI_REQUIRED      | 已确认是用户提交项不合格时SEMANTIC_INPUT_INVALID，field按入口；可信适配器产生非法项则INTERNAL_ERROR                                                                                                                                                                  |
| INVALID_QUERY              | SEMANTIC_INPUT_INVALID/field=query                                                                                                                                                                                                                                   |
| INVALID_RULE               | SEMANTIC_INPUT_INVALID/field=rule                                                                                                                                                                                                                                    |
| UNBOUND_RULE_VARIABLE      | SEMANTIC_INPUT_INVALID/field=rule；实际未绑定的规则变量检查                                                                                                                                                                                                          |
| INVALID_SHAPE              | SEMANTIC_INPUT_INVALID/field=constraint                                                                                                                                                                                                                              |
| INVALID_SHAPE_LIST         | SEMANTIC_INPUT_INVALID/field=constraint；真实模板列表形状错误                                                                                                                                                                                                        |
| UNSUPPORTED_BLANK_NODE     | UNSUPPORTED_CONSTRUCT/rdfBlankNode；范围外空白节点，模板允许列表不被此规则误拒                                                                                                                                                                                       |
| READ_ONLY_QUERY_REQUIRED   | UNSUPPORTED_CONSTRUCT/sparqlForm；合法但不支持的查询形式，不是语法失败                                                                                                                                                                                               |
| UNSUPPORTED_OWL            | UNSUPPORTED_CONSTRUCT/owlExpression；真实范围外OWL构造                                                                                                                                                                                                               |
| UNSUPPORTED_SHACL          | UNSUPPORTED_CONSTRUCT/shaclAdvanced；合法但非白名单SHACL约束/特性，不限高级规则                                                                                                                                                                                      |
| UNSUPPORTED_SHACL_PATH     | 须按真实来源细分：合法但范围外路径→UNSUPPORTED_CONSTRUCT/shaclPath；已确认非法path或targetClass/datatype模板项→SEMANTIC_INPUT_INVALID/field=constraint；可信适配器违约或未能分类→INTERNAL_ERROR。现合码也用于targetClass/datatype对象非IRI，不能按码一律称路径不支持 |
| UNSUPPORTED_FORMAT         | UNSUPPORTED_CONSTRUCT/rdfFormat；不混入rdfBlankNode/owlExpression，不带原格式字符串                                                                                                                                                                                  |
| UNSUPPORTED_RDF            | 须细分：已确认用户输入的非法RDF项/事实形状→SEMANTIC_INPUT_INVALID/真实入口；合法但超候选范围→UNSUPPORTED_CONSTRUCT/rdfConstruct；可信图/适配器违约或无法分类→INTERNAL_ERROR                                                                                          |
| UNSUPPORTED_RDFS           | 须细分：合法但范围外RDFS构造→UNSUPPORTED_CONSTRUCT/rdfsConstruct；已确认非法输入形状按真实入口SEMANTIC_INPUT_INVALID；可信层违约或无法区分则INTERNAL_ERROR。不能借owlExpression                                                                                      |
| UNSUPPORTED_DATATYPE       | UNSUPPORTED_CONSTRUCT/datatype；合法但未支持的datatype，尤其模板类型；非法词法不归此类                                                                                                                                                                               |
| UNSUPPORTED_LITERAL        | 须细分：真实非法词法→SEMANTIC_INPUT_INVALID/入口；合法但未知datatype→datatype；合法但不支持的非有限等值类别→literalValue。缺来源分类→INTERNAL_ERROR，不携带原字面量                                                                                                  |
| UNSUPPORTED_QUERY_FUNCTION | UNSUPPORTED_CONSTRUCT/queryFunction；含不支持的合法函数或聚合                                                                                                                                                                                                        |
| UNSUPPORTED_QUERY_ORDER    | UNSUPPORTED_CONSTRUCT/queryOrder；合法但不支持的排序表达式                                                                                                                                                                                                           |
| QUERY_SLICE_UNSUPPORTED    | UNSUPPORTED_CONSTRUCT/querySlice；拒绝文本切片，不改变查询含义，不冒充服务分页限制                                                                                                                                                                                   |
| UNSUPPORTED_RULE_OUTPUT    | UNSUPPORTED_CONSTRUCT/ruleOutput；范围外规则头公理/任意谓词，不借ruleChain/ruleRecursion                                                                                                                                                                             |
| ASSERTED_SCOPE_REQUIRED    | 若实际实现明确不支持所请求的合法scope→UNSUPPORTED_CONSTRUCT/validationScope；若服务给Validator混入本体/派生公理或违反已选事实投影→INTERNAL_ERROR。现有合码不足以证明是哪一种，不能要求用户删数据或改scope以掩盖适配器错误                                            |
| INPUT_LIMIT                | 真实文本/blob字节或图量超限→RESOURCE_LIMIT/semanticInput；现_text()对非字符串同样使用此码，可信适配器类型违约→INTERNAL_ERROR；若在公开参数层已确定用户参数形状错误→INVALID_REQUEST/field=params。不能按合码一律声称超限                                              |
| RESULT_LIMIT               | 最终查询行/闭包三元组/输出和依据总量超限→RESOURCE_LIMIT/semanticResult；现len(next_matches)>MAX_RULE_MATCHES是中间匹配集合，应→semanticWork。须在来源分支分类，缺证据→INTERNAL_ERROR                                                                                 |
| WORK_LIMIT                 | RESOURCE_LIMIT/semanticWork；真实累计闭包或匹配预算，不借actions/rounds/page                                                                                                                                                                                         |
| IN_MEMORY_GRAPH_REQUIRED   | 可信服务/适配器违约→INTERNAL_ERROR；公开资源身份/归属错误在资源入口先拒绝，不反射Python类型                                                                                                                                                                          |
| QUERY_FAILED               | 已确定的用户查询输入问题应在来源细分；未知库求值失败→INTERNAL_ERROR，不凭异常文本编原因                                                                                                                                                                              |
| VALIDATION_FAILED          | 无有效验证报告等内部失败→INTERNAL_ERROR；不能包装conforms=true或空违规成功                                                                                                                                                                                           |

`INVALID_PROBE_CASE`不进入产品错误；`RULE_CHAIN_UNSUPPORTED:<内部ID>`为结果警示，不能作为自由字符串error参数。正式警示详情须从获授权定义身份生成受限引用，规则保存/启用与执行不支持链分别表达。本次不添加公共警示方法。

## 分层投影与关联校验

版本化 `schema.validationProjection` 描述未来 parametersHash 所指的不可变验证配置：project/snapshot/revision、实现来源、constraintDefinitionId/constraintsRef、assertedFactsRef、ontologyAxiomsRef、scope、inputSelection、projectionPolicy。asserted必须derived=null；asserted+derived必须有真实推理resultId及独立factsRef/axiomsRef，其project/snapshot/实现必须与根一致。两种scope均保留ontology来源及依赖。该描述符不是任意图、parser/processor/pySHACL选项通道。

`validationResourceBinding`是可信Store读取的元数据投影，不由renderer或Agent自报。纯函数validationProjectionMatchesResources要求每个已选层恰好一个匹配角色、hash、project和snapshot；派生层须绑定同一真实reasoning结果、同一实现、available载荷、一致resultState。current选择只接受当次权威读取的current；显式historical选择仍须保留快照标识，可读取可用历史/过期依据，不能伪装成当前。asserted选择不能悄悄附带派生层。公共反例覆盖错误hash/层角色/项目/快照/结果/实现、缺层、非推理结果、回收载荷及未显式选择的历史。

JSON与元数据关联通过仍不能证明blob存在、内容摘要正确、用户明确选了历史或数据权限成立。I04/I05真实接入必须先完成授权/内容寻址读取与摘要校验，在一致的权威读取中解析结果元数据，核对projection与完整job.input的snapshot/scope/definition/parametersHash一致，再执行以下投影：

1. 从已验证项目分层读取本体定义与断言事实，不根据一份来源不明混合图猜层次。
2. 将选定真实推理结果的完整输出保留为不可变载荷；按经过验证的领域语义及来源分成派生事实和派生公理，记录两份内容引用与依据。不修改原始断言或完整结果，不静默删除输出。
3. SHACL数据视图为所选断言事实，加上仅在asserted+derived选择下的派生事实。必须保留领域个体的全部合法派生rdf:type及其他被选事实；不能直接删除所有rdf:type，也不能按谓词盲筛来隐藏不支持构造。无法可信分类时停止并报安全错误。
4. 本体公理和派生subClassOf/domain/range等公理留在独立引用/来源/依赖中，不作为Validator数据图或隐式ont_graph输入；约束模板也使用独立constraints图。禁止验证器再自行扩展目标或隐式推理。
5. 正确投影后再调用I05检查接口。现check_shapes对混合公理图的guard可防适配器误用，但不能把合法含推导选择整图拒绝，或为了绕过guard丢掉派生类型。I05负责内部真实分层/投影，I04负责权威引用解析、持久任务和正式接线；I03不修改这些实现。
6. 即使本体公理未进入SHACL数据图，ontology/rule/mapping集合及真实输入依赖仍全部保留；只改变scope或projectionPolicy会改变参数身份，不能复用另一范围的结果或分页游标。来源/实现不兼容仍默认隔离，不增加领域staleReason。

### 固定范围反例与证据边界

独立测试输入：ontology含`C subClassOf Mid`、`Mid subClassOf Equipment`；断言仅`x rdf:type C`且x无名称；约束是Equipment名称必填。真实推理应能提供`x rdf:type Mid`、`x rdf:type Equipment`及派生公理`C subClassOf Equipment`（仅在相应候选语义实际支持并验证后）。

- asserted视图不含本体路径，不得暗中把x扩为Equipment目标；该固定范围下x不产生名称违规。
- asserted+derived事实视图必须保留x的派生Equipment类型，使x成为目标并恰好产生x名称必填违规；不能因同一推理输出含subClassOf公理而整图拒绝，或过滤掉类型后假报通过。
- 原ontology及派生公理仍可按各自引用追溯，原断言不变；完整目标集合、违规对象/约束/路径与依据均须比较，不能只比数量。

公共样例验证的是描述符/元数据关系接受拒绝；本迭代没有执行RDFS、pySHACL或实际图投影。上述真实混合公理/派生类型案例由I05和I04接入联验提供证据。它约束范围透明与不丢事实，不提前采用最终Q6路线，也不把尚未实现的含推导scope标为检查通过。

约束资源在本版必须携带与根一致的constraintDefinitionId；constraintsRef关联的是该已保存定义的完整命名模板图（可含该定义内部子形状），其他层不得冒充约束定义。共享引用若要承载多个独立定义，必须另设固定成员清单与选择协议，不能仅修改根ID就使用原资源。I04读取时还须校验该定义与blob清单、实际命名模板及job.input.definitionId一致；纯metadata校验不证明图内成员真实。
