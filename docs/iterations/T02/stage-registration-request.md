# T02-S1 独立服务/页面子阶段登记请求

状态：**仅请求总控登记与预约；尚未获子阶段批准、指定外审时段或正式消费授权。**不改写原T02 Goal，不缩减FR-200–204、附录C/F/G、12.1/12.4及完整父功能/发布门。本线不写root tasks/state或service-stage-register。

依据总控当前 `service-stage-register.md` 的独立服务登记制度，申请把已实做并内审通过的T02本线候选按下列精确范围单独安排审查/合并；子阶段通过不能关闭父功能，也不能把私有页面称为产品入口。

## 固定候选与文件范围

- 批准base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。C2实现`5ef86a1da88d86f2de7b55a7e3be38b1e0f986b4`；C3实现`49321221733ea927484647352e05e7d833cebc86`；当前流程head在status/实际Git读回。后续外审前须再核实际批准develop、同步必要依赖、处理冲突并固定最终base/head。
- Python：`ontology/{__init__,model,service,source_projection}.py`；`test_ontology_{editor,fixed_inputs,source_projection}.py`。
- Renderer：`ontology/{OntologyPage.tsx,view-model.ts,ontology.css}`；`tests/unit/t02-ontology-views.test.ts`。
- 固定输入：`tests/fixtures/ontology/`下5个Turtle正反样本、原manifest及获批T09固定873的manifest/G-base原字节；不采用T09服务。
- 流程/测试工具：`docs/iterations/T02/`、`docs/reviews/T02/`的全部当前tracked实物。原始日志与大幅截图保留本地；待推具体内容需与最终审查范围一致。AGENTS、node_modules/venv/out、数据库、凭据、其他模块与root控制文档均不入产品提交。
- 不包含公共contracts/registry、storage/Job/worker/protocol、main/preload/App、依赖锁/build/CI；不把未批准I05/I06/T01实现列为依赖。

## 子阶段完整有界验收

| 有界能力                        | 必须比较的实物与反例                                                                                                                                                                                            | 当前直接证据                                                                                    |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 私有本体定义与断言编辑计划      | 类/对象属性/数据属性/个体、层级/类型/domain/range、多语言名称/定义/同义词/示例；完整元数据before/after及全部增删RDF；复制/引用删除/错误类型/旧项目版本/同版本内容漂移                                           | 26条C2 Python，3条TS视图；C2内审通过                                                            |
| 批准Store2不可变源与RDF读取证明 | 完整G-base10定义/18断言的具体集合；原fact ID/owner/source_row/managed_value/人工覆盖/墓碑；重叠支持原下标、定义hash/显式引用、表单类型/名称定位原asserted来源；漏项/同数量错误替换/跨项目/旧源/坏源与读取零写入 | 新13条真实临时SQLite专项；C3内审通过。证明RDF覆盖，**不证明metadata授权、当前源选择或最终提交** |
| 独立页面呈现与状态隔离          | 表格/循环多父类树/一跳SVG图；多语言/多行真实按键编辑、定义与实例事实分开、完整Diff；旧草稿/旧影响/迟到/切项目/失败表达；双尺寸与截断提示                                                                        | 11项实际headless组件状态探针，仅合成callback，不计IPC/Store/模型运行                            |
| 正常仓库与来源保全              | 本线39 Python；全仓lint/format/type/vitest/build/ruff/pytest；固定批准source与输入/原失败hash、受保护AGENTS未暂存；未变旧UI不重复运行                                                                           | `verification-c2.json`、`verification-c3.json`及实际原日志；最新633TS/1091Py通过，12归档源保持  |

## 不随子阶段关闭的父功能验收

1. 由T01/T00正式发布同版投影、业务方法/注册表、严格边界/固定错误/分页，实际来源/项目/session/generation绑定；当前private DTO不是公共契约。
2. T01可信当前快照、non-RDF metadata/来源/引用、真实人类确认、唯一Store.commit、整批回滚/旧预览拒绝/提交对账/撤销；只读binding和合成callback不能替代。
3. 批准I05有限Turtle/RDFS/SHACL矩阵：完整导入支持检查、不支持构造拒绝、原文件/项目不变、允许列表/多语言与常见类型/基本事实的无损往返、标准工具互操作。当前Turtle样本存在和基本RDF探针只算准备。
4. I06剩余六文件的真实命名bridge、App路由、壳生命周期/草稿持久化/过期和失败完整交互；真实页面联验必须通过后才能称本体可用。
5. T08真实建模草稿进入同一版本化预览、不可自确认、失败准确表达；FR-200–204及12.1/12.4、跨模块与双平台/父发布验收继续。

## 最新共享owner路由（只读核验）

总控最新 `execution-state.json` 与生效协议表明：

- T01：storage.py；`packages/engine/src/ontolearn_engine/{job_store.py,coordinator.py,__main__.py}`、`packages/contracts/python/contract_v2.py` 四文件（协议SHA `18485767098d448a4fcce2fc7e59b5a325433826894b98111cab96926fdc2097`）；contracts/src两文件、v2五JSON、main/engine.ts八文件（协议SHA `add9884ab9a0cda3a8a562f26a3b7c515255919d65eb0487d6c254681ed4991d`）。具体格式3实现仍未批准供T02消费。
- I06：main/index.ts、main/task-service.ts、preload/index.ts、renderer/env.d.ts、App.tsx、style.css六文件及其本线模块。
- I05：未单独交接的语义/resources等；T03：已生效四个依赖/build文件。本请求不扩大任何共享写授权。

## 原质量门与预约

实际外审当前预约T06-S1，随后I05 C2，T02尚未登记时段。本请求不以其他任务活跃状态或配置文件替代预约。获批最终候选后仍须原开发聊天通过合规CUA为ZCode GLM-5.3/最高与MiniMax M3.1-Flash/xhigh各新建完整只读独立任务，核实实际路径/模型/思考/权限，两个真实终态全文读回及逐项处理；双方明确通过后才push/PR（attach），实际CI通过、正常merge、远端核验。新base或产品/测试/依赖/验收变化重新验证并双方新审。用户桌面/密钥/付费/外发及平台确认边界不变。
