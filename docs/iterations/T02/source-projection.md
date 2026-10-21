# T02 只读 RDF 来源绑定

适用代码：`ontology/source_projection.py`。依赖仅为当前批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 `storage.py` / `invalidation.py` 和本线私有领域模型。不消费 T01 格式3或未批准 I05/I06，不改任何共享文件。

## 解决的具体接线问题

编辑器把个体类型、名称、注释放在专用字段，而批准 Store 的原记录可能来自手工/映射事实或 ontology definition 的 triples。提交适配器若只看表单字段，可能错误地重建事实 ID、丢弃映射基线或在错误层删除声明。

`bind_rdf_projection(source_ref, source, editor)` 对 owning service 取得的真实不可变源与已构建编辑投影核对：

- 使用批准 Store 的 `_snapshot_state` 复验记录、来源和显式引用形状，`digest` 核对完整内容地址；project/revision 必须一致。
- 逐条读取当前断言与 ontology definition 的三元组，要求与编辑器编译的**完整 RDF 集合**相等。漏项、同数量错误替换或新增虚构声明均拒绝。
- `FactSource` 保存原 id/subject/predicate/current_object/owner/source_row/managed_value；object 为 null 的映射墓碑保留为来源，不能成为事实。
- `StatementSource` 保存每条当前语句的事实 ID 或 definition ID/原 triples 下标；一条语句由多处支持时全部保留，不按 RDF 去重丢失来源。
- `DefinitionSource` 保存所有原 definition 的身份及完整 payload digest；`DefinitionReference` 保存原定义间显式引用边。完整 opaque payload 仍在源快照，不复制为另一可变权威。

`removed_sources(preview)` 只将本基准的 RDF 移除项定位到全部原支持。`require_source(ref, source)` 只检查调用者提供的新源是否仍等于绑定源。两者都不是 Store 计划、权限凭据或用户确认。

## 真实证明范围与仍待 owning source 的部分

生产模块不实例化 Store、不接收文件路径、不执行 SQL、不写项目、不注册能力；其结果均不可变。测试中才创建独立临时 Store，经真实 commit 准备案例输入，再证明读取本身没有增加 SQL 写入或改变 state/vector/revision。

这是 RDF 覆盖与来源对应证明，不是公共格式、通用 parser 或元数据授权器。identifier/synonyms/examples、单值策略、映射状态等非 RDF 内容仍由 T01/T00 owning adapter 读取和验证；本 API 不猜它们。定义间 reference 也不被猜成实体 IRI 引用。源 hash 是完整性证据，不能证明传入源来自受信项目服务或代表当前项目。

正式确认时 T01/T00 必须重新从可信项目身份取得当前源，复验版本/来源/metadata/引用，并将明确的人类动作绑定到一次 Store.commit。旧完整源可以继续用于历史浏览，但不能仅因其 hash 正确就获准提交。多支持、映射人工覆盖和墓碑的写入处置由 owning Store 决定，不能把 `removed_sources` 列表直接当删除计划。

SHACL 模板、Turtle 支持检查、完整交换格式与 T08 草稿仍按原 owner/批准依赖联验；当前模块不扩大语义矩阵，也不把快照读取证明换名为这些能力完成。

## 必要验证

`test_ontology_source_projection.py` 实际覆盖批准 Store2 的完整 G-base、人工覆盖、墓碑、完整集合错配、metadata 证明边界、重叠支持原下标、异项目/旧版本/源篡改、五类坏源固定诊断，以及表单类型/名称修改定位原 asserted record。无 Electron/GUI/真实模型/正式桥接或生产验证。
