# T11 原会话恢复窗口实际回读

本次获总控 GUI grant 后逐侧核对；发现两方均已有报告，**没有发送继续、重发全文、创建会话、重置、改设置或消费恢复权益；已释放 GUI**。临时粘贴用于核会话 ID 的文本均已清空，未发送。

- Z：原 session 精确匹配；当前 GLM-5.3/最高/完全访问，workspace 正确。原失败 turn 保留；原 session 此后已有正文为“重试”的 user 输入及新 turn `turn_1b2a8b28-1eab-4f29-ad08-6a8385491485`，末模型 `finishReason=stop`，官方 `turn.completed`（2026-10-22T14:33:25.728Z）。这次访问没有触发该重试，不推断是谁操作。UI 显示完成，报告实在、29056 bytes / SHA256 `6e82553c693678e2f6af95a905fc8f77c639d5caac28ccce5878e226064ee505`；报告自述工程范围通过，父发布门保留。
- M：原 session/cwd 精确匹配，M3.1-Flash/xhigh/始终授权。UI 显示模型服务不稳定和网络问题、继续执行按钮；无公开 quota/auth 提示。原 aborted 之外，后续 turn `turn_6746f565-e8f7-4911-bd3a-6bd587059bb9` 的最后 assistant 为 `toolUse`，**尚未核得正式 stop 完成终态**。报告已在约定路径、42053 bytes / SHA256 `d28405753dcc5644dd0b809f0c0eedbf0b1692ac12bd3d8c58970f128f3833a0`，自述工程不通过；不把报告自称终态替代客户端真实终态。按“已生成报告不盲排队”停在准确现状，未另发继续。

原完整输入逐行供给证据沿用此前 native-readback，不重发或改写。两审查树 HEAD 仍为原 b6e57a0534c94316dd07c3a87b4b8931d5a39501，冻结 product/base/scope 不变。最小原生链只含本会话 user 的 canonicalTextRange 所指正文、消息/turn/stop/模型/cwd 标量及报告哈希；M 的背景任务 user 输入 canonical 范围为空，不复制其应用上下文。未导出系统提示、thinking、headers 或其他会话内容，两个审者没有收到对方本轮意见。

本回执只完成恢复窗口和状态采集，全文报告接收/意见处置尚待单独完成，不将两方意见组合成双审通过；M 真实终态仍缺。固定报告的“322行由末行无换行解释”与既有逐行采证不符：真实是321正文行并有尾LF，UI322为空尾；报告原件不修改，供后续收件时明确校正。
