# I05 v3 内部安全细码交接

承接总控转交的 I03 `I05-semantic-boundaries.md` 草案。本记录是 I05 的实际来源分支，不修改公共目录、不直接消费传输 DTO、不把未冻结草案当批准接口。I04 仍需保留可信来源上下文：非法用户定义与服务生成的非法图不能只凭同一内部码归责用户。

| 实际分支 / 内部细码 | 当前真实含义 | 供 I03 唯一维护者判断的公共分类 |
| --- | --- | --- |
| `_text` / TEXT_TYPE_INVALID | 参数根本不是 str，未执行字节上限判断；测试含 None / 数字 / list / dict。 | 可信适配器违约→INTERNAL_ERROR；公开参数入口应提前 INVALID_REQUEST，绝不是 RESOURCE_LIMIT。 |
| `_text` / TEXT_INPUT_LIMIT | 合法字符串的实际 UTF-8 字节量超限。 | semanticInput。 |
| `_copy` 或 parse 完成 / GRAPH_INPUT_LIMIT | 实际输入图三元组量超限。 | semanticInput。 |
| 字面量 ill_typed / INVALID_LITERAL_LEXICAL | RDFLib 已确定非法词法；例如 integer 的非数值文本。上下文过滤原值诊断。 | 已确认用户输入时 SEMANTIC_INPUT_INVALID / 真实入口；可信生成项违约仍 INTERNAL_ERROR。 |
| 字面量 datatype / UNSUPPORTED_LITERAL_DATATYPE | 合法、未被 ill_typed 标记的字面量使用候选列表外 datatype。 | UNSUPPORTED_CONSTRUCT / datatype。 |
| 非有限值 / UNSUPPORTED_NONFINITE_LITERAL | datatype 已支持，但实际 float/Decimal 值非有限。大而有限 Decimal 使用 is_finite，不误称非有限。 | UNSUPPORTED_CONSTRUCT / literalValue。 |
| 形状 datatype URI 不在支持列表 / UNSUPPORTED_DATATYPE | 合法 datatype IRI，模板当前不支持。 | UNSUPPORTED_CONSTRUCT / datatype。 |
| `_terms` / RDF_TERM_INVALID | 主体或谓词不符合已知 RDF 项形状；不是合法但未支持的 rdfConstruct。 | 按真实生产者归 SEMANTIC_INPUT_INVALID 或 INTERNAL_ERROR。 |
| `_terms` / RDF_TYPE_OBJECT_INVALID | rdf:type 对象不是类 IRI。 | 同上，不冒称合法但未支持构造。 |
| `_terms` / RDFS_TERM_INVALID | subclass/domain/range 对象不是应有的 IRI。 | 同上；不等同合法但超范围 RDFS。 |
| `_terms` / UNSUPPORTED_RDFS | 合法 IRI 使用当前范围外的 RDFS 词汇，例如 subPropertyOf。 | UNSUPPORTED_CONSTRUCT / rdfsConstruct。 |
| 形状 targetClass / SHAPE_TARGET_CLASS_INVALID | 目标类对象非 URI；实际反例为匿名节点。 | 已确认用户模板时 SEMANTIC_INPUT_INVALID / constraint；可信模板生成错误则 INTERNAL_ERROR。 |
| 形状 datatype / SHAPE_DATATYPE_INVALID | datatype 对象非 URI；实际反例为字符串。 | 同上；不是 shaclPath。 |
| 形状 path / SHAPE_PATH_INVALID | 已确认非法的字面量路径。 | 同上，SEMANTIC_INPUT_INVALID / constraint；不是合法复杂路径。 |
| 形状 path / UNSUPPORTED_SHACL_PATH | 目前在该分类分支明确验证了“单一 inversePath 且对象为 URI”的合法范围外形式。 | UNSUPPORTED_CONSTRUCT / shaclPath。 |
| 形状 path / SHAPE_PATH_UNCLASSIFIED | 匿名路径未得到安全结构分类；不根据异常或节点字符串猜测合法性。 | INTERNAL_ERROR 安全兜底，不能归责用户或伪称已支持。候选仍停止检查，不返回通过；更丰富复杂路径分类待明确实现。 |
| 查询最终 rows / QUERY_RESULT_LIMIT | 最终查询行量超限，输入图本身可能完全合格；真实笛卡尔积样例覆盖。 | semanticResult，非 page。 |
| RDFS closure / RDFS_RESULT_LIMIT | 实际闭包图三元组量超限。 | semanticResult。 |
| 规则 next_matches / RULE_MATCH_WORK_LIMIT | 中间匹配集合量超限，尚未生成最终结果。 | semanticWork，不能机械归结果上限。 |
| 规则输出 / RULE_EVIDENCE_RESULT_LIMIT | 最终推导三元组与解释证据条目预算超限。 | semanticResult。 |
| 累计 charge / WORK_LIMIT | 累计闭包与匹配步骤预算，未声称是行为动作、内存或墙钟期限。 | semanticWork。 |
| check_shapes 或范围适配 / FACT_SCOPE_CONTAINS_AXIOMS | 事实层混入公理，不表示合法 asserted+derived 范围不支持；正确范围已有真实通过与违规证据。 | 可信服务投影违约→INTERNAL_ERROR，不要求用户删除数据或改合法 scope。 |
| 范围适配 / ONTOLOGY_SCOPE_CONTAINS_FACTS | 本体层被交付了领域断言，不静默丢掉它。 | 可信服务角色绑定违约→INTERNAL_ERROR。 |
| 范围适配 / SCOPE_SELECTION_TYPE_INVALID | 选择开关不是 bool，类型违约。 | 可信适配器 INTERNAL_ERROR；公开参数层提前 INVALID_REQUEST。 |
| 范围适配 / UNSELECTED_RULES_PRESENT | asserted-only 却附带要求执行的规则；不静默忽略该矛盾选择。 | 按来源在选择/参数层拒绝；可信服务组装错误→INTERNAL_ERROR。 |

原 `INPUT_LIMIT`、`RESULT_LIMIT`、`UNSUPPORTED_LITERAL`、`UNSUPPORTED_RDF`、`ASSERTED_SCOPE_REQUIRED` 不再从这些执行分支产生。其旧含义保留在 v2 历史交接和证据中；新候选不能沿用旧码映射或旧通过结论。其余原有细码按原三十码交接及真实来源处理，未知库故障保持 INTERNAL_ERROR 兜底。

真实分支回归位于 `test_semantic_error_reasons.py`，使用真实库 / 图 / 匹配和最终结果。资源测试只在测试上下文临时降低对应预算以触发同一实现分支，不伪造结果或任务，也不将测试值采用为业务容量。错误对象字符串只有固定 code；不携带原值、URL、路径或异常文本。

合法两范围的纯分图适配记录输入 / ontology / 所选规则摘要、每个事实的完整来源、独立公理视图与来源，并保留规则链警示。一个 constraints 图是该样例完整保存的模板图（含多个命名形状），不冒充多个公共 constraintDefinitionId 或新的集合协议。未来 I04 的真实 Store 引用、派生 resultId、授权和版本绑定仍须按唯一契约实现。
