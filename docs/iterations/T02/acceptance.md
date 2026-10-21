# T02 本地服务候选验收范围

## 直接证据

基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，独立 worktree/分支见 [状态](../../reviews/T02/status.md)。本候选不改变依赖、锁、共享存储、契约或桥接。

| 原要求                      | 当前可运行部分                                                                                              | 验证                                                                                    | 剩余正式联验                                                                                                                    |
| --------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| FR-200 类/属性/个体及元数据 | 不可变定义创建/编辑/复制/删除预览；完整语言集合、层级/定义域/值域/类型引用；删除精确语句和外部定义影响      | `test_ontology_editor.py` 完整预期与异常；页面多语言/草稿探针                           | owning Store 投影/来源保留、正式提交与撤销、真实人类入口                                                                        |
| FR-201 区分结构和事实       | 编译真实 RDF 项；结构定义不产生实例关系或必填约束；对象/数据事实分别校验                                    | 精确 RDF 增删集合、主体/谓词/客体种类与语言/类型负例                                    | T00/批准 I05 同版公共方法与业务执行器                                                                                           |
| FR-202 表格/树/局部图       | 表格每页20项、类树循环/多父引用、SVG 一跳图与完整可读列表（最多12条，显示截断）                             | 纯视图模型完整集合/顺序，headless 组件表格/树/图，1440与390宽截图                       | 真实服务分页/快照与集成壳路由                                                                                                   |
| FR-203 Turtle               | 受控手工定义编译成规范 RDF，真实 RDFLib 解析所生成基本三元组的集合探针；正反导入 corpus/hash                | `test_complete_rdf_inspection_is_valid_turtle_with_all_terms` 只证明生成的基础 RDF 可读 | 完整有限 parser/SHACL 模板列表/不支持构造拒绝/原件保留/整批预览/最终提交/无损往返均待批准 I05/T01/T00，不能把 corpus 存在算通过 |
| FR-204 Diff/草稿            | before/after 全元数据 + RDF 精确增删 + 删除影响；project/revision/content digest 守卫；页面草稿绑定独立基准 | 旧版本/异项目/同版本内容不同拒绝；迟到回复与版本变化组件探针                            | T08 真实草稿、T01 人类确认/Store.commit/undo，绝不由预览充当确认                                                                |

`Entity` / `OntologyView` 是本线私有输入和呈现投影，不是第二公共 schema、存储格式或可变权威。`Preview.candidate` 保持输入 revision，只是候选，不意味着已提交。标识以 IRI 为准；metadata-only 变化仍保留 before/after。不把 RDFS domain/range 当闭世界验证，不执行推理，不混入推导或历史数据。

## 命令与证据位置

- `npm ci --ignore-scripts`、`uv sync --frozen`：本树独立环境，未改锁。
- `npm run check`：ESLint/Prettier/TS/vitest/构建/ruff/pytest；首失败与后续日志保留在 `docs/reviews/T02/*-first.log` 等本地忽略文件，不覆盖。完整结果以状态中最后同候选记录为准。
- `npm run verify:sources`：归档12源保持，未改资料原件。
- `node docs/iterations/T02/ui-probe/check.mjs`：专用 headless Chromium 呈现探针。默认使用 Playwright 自带 browser；可用 `T02_HEADLESS_EXECUTABLE` 明确指定既有无窗口执行器。当前实测 Chromium `151.0.7922.34`，不是锁定 Electron 44 的产品兼容证据。
- UI probe 仅通过 route.fulfill 提供本地静态产物，无 HTTP server/端口/外联；合成 callback 仅用于 React 状态负例，fixture 来自本线纯领域样本。严禁计为 IPC、Store、e2e、真实模型、平台或生产验收。截图与原始日志保留本地，关键 JSON 和哈希入库。

当前无依赖/打包配置改动，未执行新包内探针。未启动 Electron、e2e、native、HMR、审查应用或凭据提示。平台安装、生产与父功能验收均见本线状态和总控后续正式证据。
