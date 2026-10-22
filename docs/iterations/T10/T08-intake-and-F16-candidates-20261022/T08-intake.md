# T08事实边界与消费要求

唯一新供方输入为根转交的6576B纯事实文档，固定ref/path/bytes/SHA见verification.json。表内五源码身份、PRD及旧T02接口只作溯源，本轮没有读取其内容。该摘要描述其固定93516fa候选边界，不代表T08或其他owner最新移动状态。

| 类别           | 固定摘要支持                                                                                                  | T10消费限制                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 私有UI动作     | hint/check/demonstrate/explain是动作名；私有demonstrate或project模式产生full-assistance标记，侧栏交onAction   | 是动作/回调，不等实际学习check、受信辅助事件或报告分类；不能将UI标记直接落学习真相                       |
| 对话/工具      | 内存会话；exchangeId、tool callId与私有本地收据存在；beginUserTurn清当前问题收据并保会话历史/已用tool ID/预算 | 不等attempt/task/check身份；新会话/问题不清已发生辅助，不定义学习attempt转换                             |
| 项目引用/codec | project/revision/snapshot/scope/module/mode/selected refs及可有result/status/trace/fields；codec有版本        | 项目引用和codec版本不等learning provenance版本；不能合成actor身份或覆盖完整性                            |
| 学习事实投影   | 此固定摘要未提供学习attempt/task/check/actor、逐attempt提示水位、持久provenance或T10正式投影API               | 不将state().localReceipts/inputContext本地克隆或模型工具消息最小化函数当T10 provider、外发授权或持久账本 |
| 实际链证据     | 未给实际provider/领域工具/T09学习记录/公共接线的本线完整联验证据                                              | 未采集不等零次辅助/无attempt/完整覆盖；合成收据、SSR、CSV/RDFLib探针不能代替真实学习来源                 |

T09七件固定设计另要求同project/task/attempt跨input单调水位、owner创建新attempt、提示先保存再展示和真实非空依据；T08摘要不证明这些持久链已经实现。C1保留实际owner schema槽/真实证据要求，不用私有UI callback或空数组把缺provider填成真空学习状态。

F15既有展示分类仍按T09固定设计：1–3部分提示、4完整示范、Agent完整修改单列。T08私有动作标签不自动满足这些分类的真实来源门槛。能确认足以完成任务的Agent完整修改确已被接受时，该次不能计独立迁移成功；只有UI标签或记录缺失时，应保未验证/来源缺口，不能伪造无辅助，也不伪造实际已代做。

可继续的不依赖供应技术工作：报告按真实来源/版本/过期/历史分层，结构上分操作完成与独立迁移；typed引用和origin保真，缺记录状态显式；实际provider/持久reader/CAS由唯一owner同版交付。这里不发布新的DTO、公共方法、schema或第二provenance writer。
