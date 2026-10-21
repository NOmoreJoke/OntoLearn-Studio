# T02 独立候选交付与接线缺口

Owner 聊天 `01a15bcd-f40b-7c91-81fa-7c481d2030d5`；独立 Goal active。Worktree `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`，分支 `feature/weekly-t02-ontology`。批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；当前受内审实现固定为 `5ef86a1da88d86f2de7b55a7e3be38b1e0f986b4`。后续流程证据提交不改变该实现。

## 已实际交付

- `ontology/model.py/service.py`：不可变定义/事实输入、创建/编辑/复制/删除、引用种类校验和完整删除影响、元数据 before/after、精确 RDF 增删、旧 project/revision/content 拒绝守卫。保留 rdfs/OWL 类声明，RDFS domain/range 不当必填约束。无 Store、网关或公共能力注册。
- `renderer/src/ontology/OntologyPage.tsx`：独立可渲染页面、表格/类树/一跳SVG图、多语言/多行表单、定义/实例事实分开、Diff/旧草稿/失败/迟到状态。尚无正式 App 路由或业务桥。没有“已保存”或自动确认入口。
- 私有 API：`change_preview(Snapshot, tuple[Put|Delete|Copy], add_facts=(), remove_facts=()) -> Preview`；`deletion_impact(Snapshot, iri)`；`rdf_triples(Snapshot)`；`Preview.require_current(Snapshot)` 只是守卫，不是确认授权。
- 633 TS/1078 Python 全仓通过；26专属Python/3专属TS；11项headless合成callback呈现核验。固定T09输入逐项hash通过、G-base完整RDF集合回归通过。C2独立内审通过，报告见 reviews/T02；C1失败及原始日志保留。

## 可落实的下一交接

| Owner / 精确 owning 路径                                   | 待提供或实施                                                                                                                                | 本线可交给联验的实物                                                                   |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| T01 `storage.py` 与其项目事务服务                          | 从同一快照读取定义/断言/外部引用，保留fact ID/owner/source_row/managed_value/墓碑；基线复验后一次Store.commit及可撤销；不得把预览当人类确认 | 纯Preview/完整RDF与metadata Diff；外部constraint/rule/behavior引用负例；固定G-base输入 |
| T00 / I06 canonical contracts与registry、main/preload、App | 发布严格schema/错误映射与按业务命名读取/预览；真实项目/session/generation/分页；路由挂载独立页面及T01人类确认                               | 私有呈现props、EditIntent/Preview样例与旧版本/异项目/迟到状态探针；这些尚非公共契约    |
| 批准 I05 语义/resources                                    | 受限文本的有限Turtle parser/支持检查、SHACL模板列表、未知构造明确拒绝、规范无损往返；不接URL/隐式外联                                       | 手工生成基本RDF真实RDFLib探针和支持/不支持/语法错误corpus；完整导入产品验收未执行      |
| T08 真实建模草稿                                           | 绑定明确输入版本/来源，进入同一预览，不能自确认或提升权限                                                                                   | 相同编辑预览服务与失败/旧版守卫                                                        |
| 总控指定外审队列                                           | 在实际批准基线上联验后预约双方各新只读完整任务；读回模型/思考/默认权限实际会话，再按原门禁push→PR→CI→正常merge→远端                         | 当前候选/完整测试及内审证据，不消费未批准依赖，不自行抢用审查应用                      |

正式公共投影、导入/往返、完整Store提交与原FR-200–204父功能验收均仍待。详细限制见 interface-handoff/acceptance 与唯一 status；本地候选不表示模块验收或上线。未写任何root tasks/state或其他共享文件；保护AGENTS仍未暂存。
