# T08 → T10 学习事实供方摘要

本次许可给T10的读取面仅为本纯文档，由总控核后转交。下列源码身份只用于溯源，不构成读取供方源码、移动HEAD、运行库或本轮模型意见的授权；无需跟进读取源码才能使用本摘要。本文不定义schema、不新增实现，也不表示投影API或父验收通过。

repo：OntoLearn-Studio；供方worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`。代码事实固定ref为`93516fa8455cf4b195cbfb699aa7a6652d428b6f`。以下均为T08本人此前已核验的固定材料，不引用当前审查意见。

| 事实项           | 实际支持及界限                                                                                                                                                                                                                                                     |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| attempt          | 不支持：没有学习attempt身份、持久状态或生命周期API。会话exchangeId不是attemptId。                                                                                                                                                                                  |
| task/check       | 不支持正式学习记录：hint/check/demonstrate/explain是UI动作名；工具callId不是学习task/check身份。私有工具收据不证明真实质量检查通过。                                                                                                                               |
| hint             | 仅支持UI动作与有限教育提示文本；没有逐attempt提示层级、步骤或持久使用记录。                                                                                                                                                                                        |
| assistance       | 已实现私有纯函数：demonstrate动作或project模式返回full-assistance，其余返回hint；侧栏把标记交给onAction回调。未持久化、未接入T09学习记录，不能独立判定学习报告类别。                                                                                               |
| actor            | 不支持：上述上下文/收据没有学习actor身份或认证绑定。projectId、mode和tool callId均不能替代actor。                                                                                                                                                                  |
| provenance/版本  | 仅有项目/运行引用：上下文含projectId、projectRevision、inputSnapshotId、scopeRef、module、mode、selectedObjectIds；evidence可含resultId、status、traceRefs、fields。没有学习provenance版本/逐attempt事实流；codec版本deepseek-chat-text-v1不是学习provenance版本。 |
| 持久事实/投影API | 不支持：本线会话数据在内存，未提供学习持久写入或T10正式报告/迁移投影API。state().localReceipts是收据，同级inputContext是上下文，均为本地克隆；projectToolMessage只做模型工具消息最小化，不是T10投影或外发授权。                                                    |
| 真实来源         | 实际provider、领域工具、T09记录与公共接线仍无本线完整联验证据。合成收据、SSR及固定RDFLib/CSV探针不等于真实模型质量或learning事实。未采集不能当作零次辅助、无attempt或完整覆盖。                                                                                    |

## 跨attempt及F16

已知原产品约束：PRD FR-104/105及11.2要求区分操作完成和独立迁移成功；接受足以完成迁移任务的Agent完整修改时，该次尝试不得计入独立迁移成功，并须反映Agent辅助。这是原需求，不是T08已实现的记录或投影。

**F16跨attempt决定的供方证据状态为unknown。** 在本人现有固定候选/文档内，没有可提供的F16决定版本、身份或完整规则；这不表示其他owner没有该决定。不能默认一次辅助永久影响所有后续attempt，也不能把清UI、新会话或新问题当作清除既有辅助事实而改判独立成功的依据。

代码中的beginUserTurn只清当前问题收据，保留会话历史、已用tool ID与预算；它是对话轮次边界，不是学习attempt转换或辅助分类政策。跨attempt的继承、重新独立尝试与既有辅助事实处理须以已有真实产品决定及学习事实owner交接为准；本摘要不补造默认规则。

## 固定材料身份（不授源码读取权）

以下路径均相对上述repo，ref为93516fa8455cf4b195cbfb699aa7a6652d428b6f：

| path                                                   | bytes | SHA256                                                           |
| ------------------------------------------------------ | ----: | ---------------------------------------------------------------- |
| apps/desktop/src/main/agent/agent-service.ts           | 13142 | 1d85c1f85f1a81e48f960405950240cafb55123e0823682d42edc927a0f9d659 |
| apps/desktop/src/main/agent/conversation.ts            |  8476 | dca459044105cbb119179d10313c6634ff7c624f4bed29ae7e69371ebbf1918a |
| apps/desktop/src/main/agent/deepseek-codec.ts          |  6659 | 399ed11640b9c0433ac3627e83fec39b28cd05bc26b9a999895481d36dc21074 |
| apps/desktop/src/renderer/src/agent/context-actions.ts |  1536 | c4b743dc94869ecf088ae892b7996b50f25da225e1235e0d9456f0b61696a1d0 |
| apps/desktop/src/renderer/src/agent/AgentSidebar.tsx   | 10355 | 6eef997da2f2fb20da58219332b272e57b0002f12a6a764ad99711248f7e949a |
| docs/prd/PRD-本体学习与落地Agent工作台.md              | 93584 | 7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb |

先前T02接口回报为纯设计/审查引用：ref `f36384fb911a74e9e4ca1254ff3aee348c54f77f`，path `docs/iterations/T08/T02-request-B-draft-interface-response-20261022.md`，8545 bytes，SHA256 `155b0355b4ac0cb6f01f6942dc20712b9e352a1f26977e26c4883030692bc8df`；本次摘要已承接需要的边界，不额外授予该文件或源码读取权。

原冻结审查输入、候选和父验收均未改。本次仅纯事实摘要，无产品执行、schema、替身或新的学习政策。
