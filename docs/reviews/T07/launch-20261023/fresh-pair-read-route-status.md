# T07 fresh pair 后台取证状态（2026-10-23）

两份报告已收到并封存，作者均写明“限 T07-S1 私有范围通过”。此处仅记录作者结论，尚未接收为双审门通过。

- ZCode SID：`session_488117259b5e999c5321f8a1141cefd6`。
- MiniMax SID：`mvs_bfa6c40659f6405391d5de2bbb8cbc0f`。
- 两树 reviewHead：`24f3703ecf4fce75e0d0375f7291ed928f083c41`；产品：`f9a1157c2fff06c8bef17fa1ec44d8eb1ebacad3`。
- 两份完整报告、7 份元数据、10 份 ZCode 验证日志与 6 份 MiniMax 探针产物原字节保存在 `fresh-pair-snapshot/`；逐文件源路径、大小、SHA256、14 项候选身份与本地 git 状态见其 `snapshot-index.json`。此前提交失败/重试收据原样保留。

## 尚缺直接证据

1. 各自原始 native turn/main_turn ID。
2. 官方附件记录与从原始回合读出的全量 Read/tool 链，须能证明实际完整输入和连续读取；本地附件 SHA、作者声明、报告都不能替代。
3. 各自正式 terminal 事件及最终输出与报告的绑定。
4. MiniMax 测试命令完整 stdout/stderr、调用参数与退出事件；目前 runtime/raw/validation 只有原位与 scratch 两组三产物，测试通过和退出码仅有作者声明。
5. ZCode 虽有测试通过输出，仍需原生调用/退出事件核对，不能把日志尾部计数当作正式终态。

MiniMax 元数据中 reportBytes=29378，封存实际报告=30205 字节，原元数据已保留。其披露在固定 review checkout 原位运行 render-probe，随后再在 scratch 重跑；即使产物相同，流程偏差仍存在，待独立审查处置。未向任一外审方输入另一方意见，也未改写原报告。

## 官方只读入口边界

现有可用工具未提供 ZCode/MiniMax 既有会话读取绑定。本机 ZCode 官方 CLI 存在 app-server 与 session/read/messages/events 协议，但另起 app-server 的活动会话映射不等于桌面现有任务；因此未启动新服务、未 resume，也未借此恢复身份。MiniMax 随包 mcode-tools CLI 仅提供连接器功能，随包 mavis session handler 需要原生运行时上下文；未借用其他任务上下文、未读取全局配置或凭据、未自行调用私有 HTTP。

下一步只接受两个确切 SID 对应的、已有授权的官方只读客户端绑定或官方定向导出（保留原始 turn/main_turn、附件、完整消息/tool 事件及 terminal）。GUI 已释放，本轮不再 CUA。不能以“报告文件出现”填充未知值。

产品/测试未由 owner 重跑或修改；未 push/PR/CI/合并，未改 Goal。父功能、完整 E.5、平台和发布门保持原状态。
