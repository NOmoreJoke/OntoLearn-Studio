# T05 接口与语义交接提案

状态：本线私有领域 payload/显示模型草案，**尚未获得共享 owner 接受**。不定义第二套 IPC/公共错误/Store 写入通道；不改现有注册表。目标范围仍为原 FR-500–505、C/D/G.2 全部 P0。

## 已批准基线与真实缺口

base `5f910b52c69d86a1076b2032e5d3c63e715947f3` 的 `packages/contracts/v2/registry.json` 将 `reasoning.execute` 和 `validation.execute` 登记为 design-only；前者 scope 为 asserted（表示计算输入），后者 asserted / asserted+derived。基线没有领域执行器，不能用 `test.*` 或计划结果代替。

I05 未批准候选不作为本线正式依赖，不复制其实现。需 I05/总控给出可读取的固定语义候选报告及逐项支持证据；其有限 B1 pending 不视为削减以下产品要求。

| 原要求            | 正例与完整结果期望                                                                      | 反例/不得发生                                                  | 当前正式执行状态与提案                                                                 |
| ----------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 类型/存在/合取    | Equipment + 同一告警 High/Open → 仅 001 风险                                            | A02 Closed、A03 Low 不得触发；跨不同告警拼接不得触发           | 未接入；变量 join 绑定同一告警                                                         |
| 属性值比较        | eq/ne 与 lt/le/gt/ge，数值整数/decimal/double 对应值语义；语言/字符串 equality 单独记录 | 字符串 10/2 不作数值顺序；布尔不作数字；不合法类型不得悄悄比较 | 未接入；I05 给出 RDF datatype 比较矩阵与受限不支持错误；不擅自规定跨类型隐式转换       |
| 多结论/受控属性   | 一规则输出类成员和已声明对象/数据属性，所有输出保持完整                                 | 不允许 schema 变更、任意代码、场景状态动作                     | 本线 plan 根据本体目录检查引用，拒绝 RDF/RDFS/OWL/SHACL schema 属性输出；I05执行时复验 |
| 五类 SHACL 模板   | required/datatype/maxCount/in/numericRange，目标类及直接路径                            | 逆向/替代路径、SPARQL/高级规则必须拒绝                         | 本线校验已实现；真实报告/模板编译归 I05                                                |
| RDFS → 单阶段规则 | R-04 的 P001 经子类先成为 Equipment，再成为风险                                         | 自定义规则输出不再触发规则或 RDFS                              | plan 固定阶段；真实计算及测试归批准执行器                                              |
| 链/顺序           | R-05/R-06 两规则保持保存并启用，提示规则链；两种保存顺序完整结果相等                    | 不允许依序改变结果，不以禁用/删掉 R-next 伪造单阶段            | plan 排序稳定，静态潜在链保守提示；本体闭包精确依赖诊断待实际执行器                    |
| 撤回/多依据       | R-02 先 stale 后撤回；R-03 保留输出且依据改到 A04                                       | 不删断言、不覆盖历史；一个依据移除不得误撤回仍有支持的结论     | 私有比较算法已实现；真实结果发布/失效需 I05/T01                                        |
| V-01 范围         | 当前断言 Equipment，删 003 名称仅 003 的 C-name 违规；补回空集合                        | 不将 domain/range 当必填、不偷偷包含推导类型                   | 明确 scope/includesDerived/constraintVersion/inputVersion；未运行                      |
| 真实依据          | 规则完整事实→规则→结果 DAG，保留多次触发；RDFS 公理与直接输入                           | 缺叶/断链/循环不显示为完整依据；T08 不补写                     | 结构校验与显示已实现；真实性必须对实际 snapshot/规则版本核对                           |
| 开放世界          | O-01 缺失关联显示“未记录”                                                               | 不显示“已证明不存在告警”                                       | 私有显示帮助函数已实现；正式查询/导航待接入                                            |

## 精确共享需求

### T01：唯一持久化/版本/确认

需要正式项目服务提供：读取当前不可变项目身份/快照/依赖向量、已声明类和对象/数据属性目录、已保存 constraint/rule 定义；新建/编辑/启停/删除进入同一 ChangeSet 预览、用户确认、`Store.commit` 和撤销。草稿中的 revision 不当作权威版本；服务复验 base/定义版本、引用、依赖失效。删除仍被引用概念须有影响预览；保存失败不清空用户草稿。

本线 `quality/definitions.py::validate_definition(value)` 仅返回不可变校验 payload，`build_plan` 无 Store/SQLite 写入。JSON 成功输入见 `tests/fixtures/quality/g-base.json` 的 definitions；拒绝输入含 extra `script`、无绑定变量、不支持模板、非法范围，返回本地 `DefinitionError(code,path)`，由 T00 转换唯一受限公共错误。path 不自动可外发。

需要 T01 确认 `definitions` 层 `constraint/rule` 的正式存储格式与删除/引用规范；当前仅提案，未创建数据库或直接提交调用。

### I05：执行器及真实结果适配

建议消费经 T01 正式确认定义和不可变 snapshot，计算前解析/校验；执行器复验，不信任 UI 的计划。必须记录 engineVersion / dependencyLockHash / executionSemanticsVersion、输入快照、规则/约束版本及实际数据范围。测试采用本线 G.2 全部输入/负例并与 T09 对齐身份；附带完整 actual 集合及真实 trace，不能用 fixture expected 填充 actual。

真实 DAG 节点必须可回溯 snapshot 原始事实/公理或经批准规则的具体触发；多个支持单独保留。`comparison.py` 只校验结构/比较传入观察，不负责证明真实性，不能由其返回宣称推理执行成功。

### T00/I06：唯一公共契约/接线

请求现有 `reasoning.execute` / `validation.execute` 对接实际实现及 job/result 分页/取消，不新增通用 invoke。约束/规则读取/预览/保存复用 T01 正式业务方法；输入状态、失败、不支持、未执行与结果 current/stale/historical 明确区分。

`renderer/src/quality/QualityWorkspace.tsx` 尚未挂到 App；只生成待校验草稿，检查按钮禁用。`presentation.ts` 是内部显示模型，不供 IPC 传输；T00 对唯一公共响应严格 zod 校验后映射。观察需 projectId/输入快照/版本/约束与规则版本/执行语义/范围/是否含推导、逐检查状态、定位、预期/实际/差异、真实依据。当前页面不读取 window/Node、不自行假造任务状态。

公共响应分页未接入前，本线比较/显示只处理有界完整样例（最多 128 项），不得把截断页当完整集合。生产多页结果需由 owner 提供完整集合比较/分页显示语义。

## 验收与待确认项

本线局部测试仅证明定义/计划/比较算法；最终必须在批准同版执行器/项目/接线下运行 V-01/R-01–06/O-01 和 FR 全部路径（包括空白项目创建、失败修复、编辑启停版本化、取消/迟到/失效/撤回/历史隔离、真实依据定位与 T08/T06 联验）。指定双新模型审查、CI/正常合并、远端核验照旧。

Q6 的值比较具体 datatype 兼容、真实 pySHACL/RDFS 输出投影/trace 清单需 I05 owner 逐例回应；不因本提案把未支持项变成既定范围删减。真实完整 inference 输出基线及 T09 身份对齐尚缺，fixture 明确只冻结当前质量领域预期，不假装全 RDFS 闭包 oracle。

## I05 原候选差距实查补充

只读读取 I05 自有差异报告：`../I05-semantic-execution/docs/iterations/I05/q6-candidate-differences.md`，该树 HEAD `19101c8b606652064eb853efadf2721bdb3c95f1`；报告最后提交 `4447a35652ec55ed6c455826d704b0ee3bbee45c`，文件 SHA256 `67ef73574dd7c5a6cb0f60447f63ffca3028775e5a49e336534d37ab5c84a54d`。仅核对报告，不导入/复制/运行未批准实现。I05 原主线状态同时记录本轮 C1 已做真实 Store/worker/Job 联验，但仍未双审/推送/合并；因此不改变本线批准依赖结论。

- **Q6-08 明确未覆盖**：原候选规则是合取三元组模式、等值常量匹配、每规则单结论；无通用大小比较和同规则多结论。必须保留 FR-505，通过 I05 修订表达层与真实正反例补齐；不能靠拆成多条规则假装已经支持原编辑语义/版本/完整依据。
- **Q6-09 执行候选已有证据**：先 RDFS、规则统一读断言＋RDFS、一阶段输出不反馈、换保存顺序相同；产品编辑提示/版本保存/发布仍待接入。本线 plan/UI承接该原语义，不擅自实现另一套执行器。
- **Q6-10/11 候选已有模板与两范围证据**：有限 SHACL 目标类、直接路径、min/maxCount、datatype/in/min/maxInclusive；断言与“断言＋选定已有推导”均有实际报告。正式产品需要绑定实际选中的 immutable resultId/生产版本，不能以“本次计划的当前推导”替代指定历史结果。当前私有 UI 的范围草稿尚不提供选定推导结果的权威绑定，此项保留接线缺口。
- **Q6-01 具体 datatype 候选表**：string/langString、boolean、integer/int/nonNegativeInteger、decimal/double/float、date/dateTime，拒绝非有限数。T05 datatype 表单文本并非获准矩阵；本地模板校验已补齐 int/nonNegativeInteger/float/langString 等常见类型，避免编辑表达层自行缩减；这只校验类型 IRI，**不是执行器支持或 Q6 采用结论**。最终须在真实批准语义与 Q6 采用后统一。
- **Q6-02/03/12**：命名 Shape 与仅 sh:in 列表、有限子类/domain/range 闭包、完整导入/编辑/解释/导出各列均须承接原边界；探针/有限闭包不证明产品全部能力。

上述均为候选报告的事实与待补差距，未将其引用为正式执行通过。完整原需求与最终正反例/同版外审仍保持。

## 批准固定输入更新

总控随后批准 T09 固定873输入，本线manifest/17文件/PRD源已逐项核验，记录见 `approved-inputs.md`。正式后续G.2使用固定bundle的 `urn:ontolearn:learning:` 与 `name-required`/`alarm`，不再把私有样例命名空间作为待确认公共身份。完整真实执行/trace及原FR505语义补齐仍然开放；没有消费未批准服务/Store helper。
