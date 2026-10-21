# I06 主进程来源生命周期：T03 r1 对齐补充

2026-10-21。接受 T03 六项接口缺口并纳入本线主进程设计，当前仍不可装配；只保留明确设计选择与实际权属更新，不注册 source.*、修改产品或恢复原 blocked Goal。原 source-snapshot-transport-decision.md、source-selection-lifecycle-interface.md 及 T01-owner-response-alignment-r1.md 的固定字节作为历史输入保留，本补充更新其中 worker 交接状态并收紧以下消费条件。

## 实际读回与责任生效

- 完整读取 T03 固定 1e8ef97dbca174390a81b3ef8aef86c064564600 的 docs/iterations/T03/source-selection/t01-interface-response-r1.md，9846 bytes，实际 SHA256 7376353f6230d35a1fc931e096dab8310eae38de015f75a333e3998ec6df761b。其 broker/S1 候选仍非本线批准依赖；本轮未读或复制新实现。
- 完整读回 I05-T01-worker-ownership-handoff.md，最终格式化版本2885 bytes、SHA256 63c194efc64dae0b7e5b36911027cf69be04df709e9c5152d107baed265450da；execution-state.json 对应项 status/effective=true、effectiveAt=2026-10-21T10:21:19.636646+08:00，协议 SHA 一致。先读到的2706B/bdacff8a版本随后格式化，本轮已重新全文读取当前版本，不把旧 SHA 当现值。
- 共同指南实际 SHA256 ff5f9fd0a4913cc6c2fa612ec565bdf40d67db4a6640e5293d4ca1e7d02cfaff，16317 bytes；前15574 bytes实际 SHA256仍为原 b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39。旧条款完整保留，已读新增责任及原第九节、默认审查模式/只读、无桌面约束。AGENTS仍78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759，未修改或暂存。

worker.py 未来唯一维护已交 T01，只从批准5f的9314B/2fa848aa3a2148e59a24f01c9333701f0f03eed95cffe55a0a78b74f1d06f2f0实施必要来源接收。I05未批C3的13638B/3d934e79aff65288e1f249e2763f46b4eb86f50bd05ccc7628643951f4d4f99d保持冻结，不复制采用。I05若需修先由总控精确返还、T01停写保存SHA/差异；语义四路径 futureoffer 仍未生效。protocol/resources/语义/旧tests/build/CI没有随转；I06六共享与原专属私有职责不变。交接只消除 worker 唯一owner缺口，未消除首帧接收、wire/限额/ready/运行验证缺口。

## 六项主进程设计决定

| T03缺口                | I06明确选择与接线前条件                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. 较小协商帧          | 保留固定65536 raw/最多128块的候选 profile。begin前分别证明 main→coordinator、coordinator→worker 两段能容下严格完整 UTF-8 envelope（含转义/字段上限），均不提高 MAX。不足则拒绝该 source profile；本线当前不自行启用更小块。T01若选择正式小块profile，须版本化重定块数/总量/两段背压与同版fixture，本线同步后才能采用，不能沿用128块覆盖8MiB。                                                                                                                                                                                                                                                                                                    |
| 2. configure后的新ref  | inspection枚举结果绑定原project/lifecycle/selectionId/generation/format/SHA/长度。configure即使字节/选项相同也撤销旧proof并换selectionId/generation，main须丢旧预览/确认和迟到枚举。选择重新封存并取得新绑定引用，完整包含新上下文、encoding/sheet；不得修改旧immutable seal或将inspection ref升级为preview。底层可按批准策略去重bytes，但须由可信owner对当前输入核验并签新权威引用，不仅凭同hash字符串。                                                                                                                                                                                                                                        |
| 3. 完整tableDigest     | preview/确认账本须绑定由唯一canonical冻结的版本化完整摘要：实际source_hash、明确encoding/sheet、完整有序fields及全体有序rows的row.number/cell.text/kind。parser implementation与摘要规范身份另入完整计划绑定。现snapshot_hash/source_hash/definition_hash不冒充该摘要；不hash样本/describe/生成事实替代全表。TS/Python共享golden与UTF-8/转义/数值等规范先冻结，本线不复制第二份schema或自造摘要实现。                                                                                                                                                                                                                                            |
| 4. 实际消费者pin与回收 | broker两FS槽、上传两lease/16MiB候选配额、worker资源和持久blob quota分别计账。每个inspection/preview/Job实际消费者在开始读前，须由同一owner原子校验并取得有效受理/读保护，避免验证ref后被回收；读保护不等于正式写Job授权。TTL/取消先撤销未来未受理资格，已受理消费按其只读取消/资源合同停止并释放，不能先删仍在读取的块。最终写Job的durable pin与原claim/CAS准入、release/admit竞争仍需T01冻结原子排序；unknown先对账，不先unlink。                                                                                                                                                                                                               |
| 5. 确认前只读枚举/预览 | 真实inspection→枚举、正式preview计算须在最终映射写确认前，以独立受限只读执行语义运行。只允许批准的capability/来源/取消/有界结果读取；不得借测试Job或提前伪造写确认推进，也不由seal签发写授权。是否采用专用只读Job及其状态由唯一canonical/worker owner决定，本线不另建执行通道。完整表/plan/result超帧须按正式有界分页/分块完整保存与消费；UI样本可明确标受限，正式确认/提交不能消费截断计划。                                                                                                                                                                                                                                                    |
| 6. 复验到写受理        | main持有实际proof；readForCommit成功仅证明本次复验字节，随后磁盘仍可变。完整确认绑定sourceRef/options/table/map/project/domain/operation。复验后在main任一await/排队期间scope或generation失效，最终实际写帧guard或等价fence须拒绝未dispatch写入；只有调用前检查不足。已dispatch但尚未获ack时，main不能仅凭本地失效断言零Job：T01须冻结同owner受理/撤销的原子线性化与可信代次登记，撤销先完成则拒未受理请求，受理先完成则按真实Job/receipt处理。不能把本地wall-clock取消时间冒充跨进程排序证明；具体该保证仍缺合同和实件。原operation保留对账，不换身份重放。正式受理后仅消费已确认固定快照，后续重选/源变不篡改其输入，取消遵循正式Job/receipt。 |

新绑定引用与确认均为main/受信owner权威；renderer只显示安全摘要及发送明确动作，不传path/bytes/proof、任意RPC、tableDigest自证或 confirmed=true。旧未接纳lease跨session不复活；已accepted持久输入按原Job/operation恢复。来源proof、只读消费许可、正式映射确认和模型外发grant四种边界独立，source选择或Job受理不改变模型local/授权。

T03“复验至受理失效”的目标在以上第6项拆开实现：main最终写帧fence只解决dispatch前窗口，已发出的请求还需T01真实受理/撤销排序。该项不因worker交接或设计接受而关闭；不得以一个本地generation检查冒称已满足跨进程保证。

## 对接与验证边界

上述数值仍是I06提案；T03只接受方向，T01尚需统一严格字段、错误、状态、预算、帧profile、输入/输出/取消及pin合同。既有主进程宿主/测试精确路径申请保留，不从交接推导新增共享写权。本线待同版canonical与实际implementation ready后，在六共享及已登记专属范围接线；真实parser、XLSX枚举/CSV、预览确认、Job/Store与源包平台联验不因本补充通过。

本轮仅文档格式/diff及独立静态复核；没有因纯操作通知重测产品，没有本机GUI、容器或凭据操作，不改总控状态。空文件传输允许0块与真实CSV EMPTY_SOURCE业务拒绝分开；小帧、配置同值新代次/旧ref拒绝、完整tableDigest跨语言fixture、读消费者pin与回收、复验到受理失效和跨帧完整结果，均保留为同版实际验收项。

## 独立静态复核收口

/root/i06_design_review已实际全文读回新指南/worker生效协议和T03固定回应；六项对照无新增静态阻断。第6项初稿将未受理写入与未dispatch拒发混用，已明确拆开并定点复核关闭，收口前正文SHA4477326e0e29132e247c419e6897a9a7b22c16c84c25bd0a42256dba2baec189一致。未读取未批准实现、运行测试或修改文件，不替代T01正式合同和运行验收。
