# I05 → I03/I04 冻结草案兼容性核对

此记录只提出接口需要，不实现适配器、不采用未批准契约、不修改他线候选。I05 独立实现为 `02a8c90902788963206d7ef60fbeccc801e27c5c`；只读核对 I03 候选 `6f35ffd37d003b2aec1672891635009ebf79bb41` 的 protocol/shared-state/errors/dependencies。当前状态见 [status.md](status.md)。

I03 来源：`packages/contracts/v2/errors.json` SHA-256 `96b7e7cd08172a3fa30bd9bd6e5c57b4a43909eea7463f191e758e82b1068f44`；dependencies SHA-256 `dee118b368915df4172a77b875d31ce29ad8374cb5fce3915678f7f950cedad4`；registry SHA-256 `f1d8f00c2482cac44bea435a7f3549e63230afdb0f8bd96763b55dfa352b42a0`。路径均在 I03 唯一 worktree，只读访问；不拷贝一份可变契约。

## 30 个产品纯模块错误的逐码去向

“可表达”表示现草案有准确语义位置，仍需真实服务按调用阶段映射；不是已通过公开协议执行。messageKey/retryable 应从唯一目录生成，绝不透传内部异常、查询、URI、文件路径或原值。

| 内部 code | 当前草案可表达的安全去向 / 尚缺语义 |
| --- | --- |
| EXTERNAL_ACCESS_DENIED | NETWORK_FORBIDDEN，params={}。可表达；拒绝 SERVICE/FROM/imports 与执行期 I/O guard。 |
| INVALID_TURTLE | SEMANTIC_INPUT_INVALID，field=syntax。可表达。 |
| INVALID_UNICODE | SEMANTIC_INPUT_INVALID，field 按真实入口取 syntax/query；不能转发 surrogate 字符。可表达。 |
| ABSOLUTE_IRI_REQUIRED | SEMANTIC_INPUT_INVALID，field=syntax；若来自规则定义则 rule。可表达。 |
| INVALID_QUERY | SEMANTIC_INPUT_INVALID，field=query。可表达。 |
| INVALID_RULE | SEMANTIC_INPUT_INVALID，field=rule。可表达。 |
| UNBOUND_RULE_VARIABLE | SEMANTIC_INPUT_INVALID，field=rule。可表达。 |
| INVALID_SHAPE | SEMANTIC_INPUT_INVALID，field=constraint。可表达。 |
| INVALID_SHAPE_LIST | SEMANTIC_INPUT_INVALID，field=constraint。可表达。 |
| UNSUPPORTED_BLANK_NODE | UNSUPPORTED_CONSTRUCT，construct=rdfBlankNode。可表达。 |
| READ_ONLY_QUERY_REQUIRED | UNSUPPORTED_CONSTRUCT，construct=sparqlForm。可表达；拒绝合法的 CONSTRUCT/DESCRIBE 等形式，不冒称语法错误。 |
| UNSUPPORTED_OWL | UNSUPPORTED_CONSTRUCT，construct=owlExpression。可表达；不表示完成 OWL 支持。 |
| UNSUPPORTED_SHACL | UNSUPPORTED_CONSTRUCT，construct=shaclAdvanced。需目录明确该枚举也涵盖其他非白名单 SHACL 约束，不能把合法但不支持的约束称为语法错误。 |
| UNSUPPORTED_SHACL_PATH | UNSUPPORTED_CONSTRUCT，construct=shaclPath。可表达。 |
| UNSUPPORTED_FORMAT | 尚缺明确的 RDF 格式范围分类；现有 rdfBlankNode/owlExpression 均不准确。 |
| UNSUPPORTED_RDF | 先由真实来源区分非法事实形状与合法但超范围 RDF 构造，不能只凭本 code 编造具体构造。候选后续可细分内部码。 |
| UNSUPPORTED_RDFS | 尚缺非白名单 RDFS 构造（如 subPropertyOf）的准确分类，不能归为 owlExpression。 |
| UNSUPPORTED_DATATYPE | 尚缺有限 datatype 的不支持分类；它是形状模板所用合法但未支持的 datatype，不能直接当 syntax 错误。 |
| UNSUPPORTED_LITERAL | 当前纯模块将非法词法、未知 datatype 与不支持的非有限数值合用此 code。正式接线前须按事实细分或携带受限分类；不能凭码一律误报“非法输入”或“不支持”。不增加原值参数。 |
| UNSUPPORTED_QUERY_FUNCTION | 尚需明确查询函数/聚合范围分类；当前 construct=sparqlForm 是否涵盖它，应由唯一维护者决定并记录。 |
| UNSUPPORTED_QUERY_ORDER | 尚需明确排序表达式范围分类；不能把合法但候选不支持的表达式描述为语法错误。 |
| QUERY_SLICE_UNSUPPORTED | 尚需明确 LIMIT/OFFSET 候选范围分类；不可静默移除切片或取任意子集。服务分页与查询文本切片分开。 |
| UNSUPPORTED_RULE_OUTPUT | 尚缺规则输出构造分类。ruleChain/ruleRecursion 并不准确表达“规则试图生成本体公理/任意谓词”。 |
| ASSERTED_SCOPE_REQUIRED | 尚缺验证 scope 不受支持的分类；不能把它归为 shaclPath 或 memory。真实服务应先构造明确事实范围而不是删掉用户数据。 |
| INPUT_LIMIT | 语义文本/三元组输入量限制。现 RESOURCE_LIMIT 枚举只有 memory/actions/rounds/frame/page；输入内容寻址 blob 上限不是传输 frame 上限，不能直接混用。 |
| RESULT_LIMIT | 计算载荷三元组/证据量上限；不是单页 page 上限，不能谎称增加 pageSize 可以解决。 |
| WORK_LIMIT | 累计闭包/规则匹配工作量上限；不是附录 E 行为 actions/rounds 或 worker memory 上限。需准确的安全资源分类。 |
| IN_MEMORY_GRAPH_REQUIRED | 通常是可信服务/适配器违约；对外固定 INTERNAL_ERROR，而非反射 Python 类型。若公开输入引用不合法，应在 I03 参数/资源归属层提前拒绝。 |
| QUERY_FAILED | 当前为库求值失败兜底。已知可修复查询输入错误应在正式适配时细分；无法安全确定时 INTERNAL_ERROR，不猜测原始异常，不把所有库故障都当用户输入错误。 |
| VALIDATION_FAILED | 验证器未生成有效报告等内部故障：INTERNAL_ERROR。不能返回 conforms=true 或空违规成功。 |

`INVALID_PROBE_CASE` 只属于 CLI 测试分派，不进入产品能力或错误目录。潜在链的 `RULE_CHAIN_UNSUPPORTED:<内部规则ID>` 是纯结果警示，需正式服务从有权限的定义身份映射为受限提示，不能把携带任意内部 ID 的文本直接塞入 error.params。规则本身仍可保存/启用，且不产生二阶推导。

上述缺口在公开服务接入前解决即可；当前纯模块未注册，不要求 I03 在双审期间擅自改冻结候选。若唯一维护者决定现在修订，须新候选并保留原完整双审门禁；I05 不自行增补共享枚举。

## 输入范围与结果承载的对齐

1. I03 使用服务派生的不可变 snapshot/parameters 引用、实际依赖向量与 definitionSetDigests，和 I05 纯模块不写 Store 的边界相容。传入图之前必须验证内容摘要、项目归属和 schema；不能让客户端指定 Store/parser/processor/pySHACL kwargs。
2. 查询和推理可使用已校验 ontology 与选定事实图；SHACL 的 ontology 依赖仍须保存，但不能把 ontology 公理直接混入验证事实范围。当前事实范围拒绝 subclass/domain/range，避免 Validator 即使 inference=none 仍扩大 targetClass。含推导范围须显式合入已校验的事实结果，不改变原始断言。
3. 规则定义的启用状态、完整规则/本体/映射集合及集合空→非空变化均由 I03/I04 的真实依赖算法跟踪。纯模块不伪造 facts 键或根据查询命中对象缩小真实依赖。
4. 查询 rows、完整 SHACL 违规和推理依据可能超过 262144 字节帧、131072 字节页、200 行、64 格或8192标量单格。worker 载荷应存为不可变结果，再按服务契约分页/详情引用；不能将整个返回 dict 塞进完成通知，也不能截断为成功空集。N3 字面量序列化的长度包含转义/语言/datatype，必须按最终编码检查。
5. 取消、崩溃、迟到发布、持久终态、总时限、内存和窗口重连只能用真实 I04 与 Store 联验；原纯语义回归和 CLI 超时不能替代。实现来源三键与锁哈希保留，正式接入需要更新基线与新同版全范围双审。

本记录完成静态接口核对，不表示 I03 设计已通过、I04 已实现或 I05 集成验收通过。
