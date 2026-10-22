# T07固定pure docs接收：仅补供方事实

根许可三件固定`f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`的pure docs：integration-request.md、round-projection-handoff.md、acceptance.md。原owner全文读并核bytes/SHA/blob匹配，身份与许可清单见verification.json。本页补C1与下一供方签认清单的T07缺项事实，不重写迁移大稿，不授schema/API或实施票。

| 消费项         | 本次获准文档支持的精确事实                                                                                                                                                                                                                   | T10仍缺的供方/验收条件                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 完整Round      | 私有internalRound保checkpoint（定义摘要、轮号、完整工单/告警/assertions状态、历史创建身份/单调序号、完整事件目录/payload、消费与完成身份）、输入事件/当轮创建/完成/积压/三指标、推理输入state/规则版本/snapshot/context及逐动作轨迹/冻结计划 | 这是私有投影形状，不是公共schema或实际完整领域结果。不能只带摘要或Round指针，也不能从Round补造遗漏的原始配置                 |
| 独立runConfig  | 完整Definition/初始快照、项目/场景及输入内容、来源与初始消费、参数、规则/行为完整内容和各版本、engine/dependency lock/执行semantics，须随runConfig另行固定                                                                                   | Round和定义摘要不能代替完整runConfig。对应材料齐全、目标版本实际支持、实际重放验证分轴，不以版本字符串存在判支持             |
| 未处理事件范围 | coordinator pending是所有已知未消费事件全集，包含超过max的未来配置事件；T09 E.5 pending仅已注入队列，scheduledFuture另列                                                                                                                     | 保scheduledFuture与generatedPending等范围，逐轮按对应口径比较；不把全集与子集直接比，不在max截断未来事件                     |
| 独立重放/续跑  | 独立replay恢复配置中原始消费状态；显式continuation校验完整定义/事件目录/已提交消费并沿用该快照消费                                                                                                                                           | 不是一概清零，更不是学习attempt重置或F16资格政策。历史run不被新run修改；跨设备重放另联验                                     |
| 提交与丢响应   | 交接提案固定project/inputDigest/job/run/expectedRound/operation/stateDigest，同连接同外层事务写Round、marker和committedProgress；精确marker重试返回旧结果不推进轮次                                                                          | 实际API/错误/恢复由T01唯一owner冻结。响应异常不等零效果；无法权威对账保持待恢复，不再次执行动作；全部轮写完也不等job终态成功 |
| 已有验证边界   | 文档报告合成ports编排与真实Store/SQLite/进程恢复边界探针；明确未注册正式scenario任务、未证明T05/T06真实领域编排、I04取消协调和终态完整链                                                                                                     | 本轮只核文档身份，没有读取测试/日志/fixture或复测；不把文档描述的探针变为本次产品Pass或跨设备证明                            |

本次收到的是三个私有设计/验收边界文档，**没有交付获批的公共Round/runConfig schema、可调用迁移投影API或目标端实际重放证明**。文本中的方法名、Store接口、探针命令、源码/fixture/相对引用及模型意见不转授读取或执行权限。

只补下一签认清单三处：T07给逐run完整Round+独立runConfig的精确typed/版本/来源/初始消费与范围合同；T01将其完整保存并固定单次operation/round对账、保留及引用生命周期；目标执行owner给真实版本支持矩阵和跨设备逐轮完整集合/状态/指标/终态比较。无需新建公共契约或消费未批适配器。

若history未选，不暗带未选run正文；若选中历史缺任一必要输入/config/版本/来源，逐run如实列缺项；材料齐而目标实现未知仍不称可重放。当前项目可恢复性另按完整核心状态判定，不被某run重放缺口自动降template。

F01/F16已由根async统一询问、答案未到；本页不改变候选或提出新问题。T07沙盘消费/重放语义不回答F16，T08/T09的局部unknown也不用于推断其他owner最新状态。I06新pure-doc callback仍待根转交，不因本页事实补充冻结无关技术工作。
