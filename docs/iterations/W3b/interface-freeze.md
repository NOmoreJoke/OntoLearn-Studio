# W3b-S2-1 接口冻结

本切片交付共享 DTO、校验、命名 preload 桥和主进程薄透传。S2-2 接入 Agent 宿主，S2-3 实现引擎语义，S2-4 接入工作台。普通公开快照仍由 `project.checkpoint.create` 铸造 `manual`，I06 继续使用原有 12 条 `model:*` 路由。

## 共享词表

- `AgentScope` 为 `asserted | asserted+derived`。
- `AgentMode` 为 `tutor | project`。
- `AgentPrivacy` 为 `local | minimal | project`。
- `AgentModule` 为 `learn | ontology | mapping | query | quality | behavior | scenario`。
- Agent 草稿收据使用 `purpose: 'suggest'`。证据和失败收据使用已有的 `explain | suggest | review`。

`agentScopeToQueryScope(value, inputSnapshotId)` 是工具范围到查询范围的唯一转换。历史 ID 由宿主注入。函数拒绝缺失或空白 ID，并原样保留有效 ID，例如 `001`。

| 工具范围               | 查询范围           | 查询选择                                            |
| ---------------------- | ------------------ | --------------------------------------------------- |
| `asserted`             | `asserted`         | `{kind: 'current'}`                                 |
| `asserted-and-derived` | `asserted+derived` | `{kind: 'current'}`                                 |
| `selected-history`     | `asserted`         | `{kind: 'historical', snapshotId: inputSnapshotId}` |

## Agent 与模型配置 IPC

| 通道                      | DesktopBridge 方法             | 未安装宿主时                                     |
| ------------------------- | ------------------------------ | ------------------------------------------------ |
| `agent:context`           | `getAgentContext`              | 本地导师模式，项目和快照为空，能力均为 `not-run` |
| `agent:set-mode`          | `setAgentMode`                 | `TOOL_UNAVAILABLE`                               |
| `agent:dispatch`          | `dispatchAgentQuestion`        | `MODEL_UNAVAILABLE`                              |
| `agent:state`             | `getAgentState`                | `idle`，空收据                                   |
| `agent:cancel`            | `cancelAgentExchange`          | `TOOL_UNAVAILABLE`                               |
| `agent:draft-plan`        | `buildAgentDraftPlan`          | `TOOL_UNAVAILABLE`                               |
| `agent:commit-draft`      | `commitAgentDraft`             | `TOOL_UNAVAILABLE`                               |
| `agent:audit`             | `listAgentAudit`               | 空列表                                           |
| `agent-model:set-enabled` | `setModelConfigurationEnabled` | `MODEL_UNAVAILABLE`                              |
| `agent-model:remove`      | `removeModelConfiguration`     | `MODEL_UNAVAILABLE`                              |
| `agent-model:probe`       | `probeModelCapabilities`       | `MODEL_UNAVAILABLE`                              |

主进程先校验窗口和 frame 信任，再校验参数，最后调用可选的 `getAgent`。切库阶段拒绝所有 Agent 调用，项目管理或恢复阻塞期间拒绝派发、草稿提交、模式持久化、配置启停与删除，以及能力探测。调用方提供的项目 UUID 仅用于绑定及复核，项目选择、数据范围和外发授权由宿主确定。模型配置和审计 DTO 只提供公开摘要。能力分别报告连接、结构化输出和工具往返，并标明验证来源。

## Turtle 与内部快照

| 通道                            | 方法                                                                             | 冻结结果                                                                                                                            |
| ------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `project:ontology-export`       | `exportProjectOntology` → `project.ontology.export`                              | `ok` 带已提交态的 Turtle、三元组数量、快照与版本。超出支持范围返回 `rejected` 和原因，整批拒绝。                                    |
| `project:ontology-import-check` | `checkProjectOntologyImport` → `project.ontology.import.check`                   | `ok` 带摘要和可提交给既有 ChangeSet 流程的计划。超出能力范围返回 `rejected`，语法或格式错误返回 `invalid`。两类失败均带原因。       |
| 主进程内部                      | `ProjectMainlineService.recordAgentBeforeCommit` → `project.agent.before_commit` | 输入绑定选中项目、操作、基准版本、完整辅导开关、可选任务 ID 和可空标签。结果带 `before-agent` 快照引用、域版本和实际更新的任务 ID。 |

导入成功摘要为 `{baseRevision, inputSnapshotId, tripleCount, definitionCount, manualFactCount}`。计划使用既有 ChangeSet 的 `definitions`（本体及约束）和 `manual`（手工事实），字段可省略。后续流程以摘要中的版本进行预览、查看差异、确认和提交。每条拒绝项含 `code`、`field` 和 `detail`。主进程 IPC 缺省使用 `turtle`，business3 可接收其他格式标识以返回 `UNSUPPORTED_FORMAT`。两条 Turtle IPC 沿用 mainline 投递和确认协议。

`project.agent.before_commit` 在 business3 的 `methods` 注册，标记 `agentEligible: false` 和 `exposure: 'main-process-only'`。仅 MainlineProjectService 内部调用，preload、DesktopBridge、`mainlineProjectMethods` 和普通任务读取通道均无此入口。S2-2 接线时用实际确认和提交身份触发快照，S2-3 提供写入和实际收据。

## 后续切片互斥写面

| 切片 | 独占写面                                                                                                                 | 依赖                                                                             |
| ---- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| S2-2 | `apps/desktop/src/main/agent/**` 新接线、`main/model-gateway/**` 受控请求入口、`main/index.ts` 组合根及主进程 Agent 测试 | 实现 `AgentBridge` 后注入 `getAgent`，内部调用快照方法，复用确认过的 ChangeSet。 |
| S2-3 | `packages/engine/src/**` 对应的 Turtle、business3 分发、快照/学习记录协同及引擎测试                                      | 实现三条已冻结的 Python JSONL 方法，保持公开 checkpoint 仅限 `manual`。          |
| S2-4 | `apps/desktop/src/renderer/**` 及其专属 UI 测试                                                                          | 消费命名桥和共享 DTO，使用导入检查结果进入既有预览、差异、确认、提交链。         |

接口和注册表继续由契约单 owner 维护。S2-2、S2-3 和 S2-4 共享本冻结版本；接口调整统一由总控协调。
