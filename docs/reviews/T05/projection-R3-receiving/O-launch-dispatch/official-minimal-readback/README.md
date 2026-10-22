# O 本人正式会话最小核回（首批收件）

本目录是已提交的初始 dispatch 八件记录的追加证据；不覆盖旧记录、不改两份冻结输入或审查原报告。GUI 短窗口已释放给总控。ZCode 已正式完成并全文收件；MiniMax 仍在原审查 turn 中，本目录当前不签双模型完整 Pass。

## 真实输入、设置与终态

- ZCode：`session_c76c854a8d2736fb809ce34b124f861b`。正式首 user 12896B / `477890e73a4b3ccecfa38b8a2a9e9d4de584d859206ea18482240b70a4d02f86`。与冻结 12897B 仅差末尾一个 LF，正文及全部空行未变。`GLM-5.3 / max / thinking enabled` 取自本人首次正式请求；本人 runtime_config 事件核 `yolo` 和独立 cwd。不是全局配置默认值。
- MiniMax：`mvs_8262fb931cf34f3dae99b85683d65fd7`。正式首 user 的本人正文 12945B / `9bb1f6e9aa635516a5ef9cd7a2df0e71a425d9ebf4cfd9739968746ebff88588`，与冻结 12946B 仅差末尾一个 LF。实际为 inline 全文；排除客户端追加 reminder 后比对，不需要虚构附件 Read 覆盖链。`MiniMax-M3.1-Flash / xhigh` 和精确 cwd 标量取自本人 llm-call；权限仍采用已核本人 UI 的“始终授权”回执，未读全局配置替代。
- Z 首 turn `turn_55ad22cc-1f42-4a54-9875-d68601efb179` 在 10:36:59Z 真实额度失败，错误 1308／重置原文 21:59:03 保留。后续 turn `turn_829965ac-a1f3-4a38-9992-67f71eb2995b` 首请求 10:38:16.009Z，末模型 10:49:40.143Z `finishReason=stop`，官方事件 10:49:40.361Z `turn.completed/status=completed`。恢复原因和操作者未知；owner 未 reset、重发、付款或升级。
- Z 原报告 `zcode-final-report.md`：18041B / `5545dd1e07ace009f690ace4e763245afcee0baa3691d1ebfe99cac06f2e95dc`，按正式终态收件、全文读取、字节原样保存。报告自身身份/effort 未核的旧表述不改，由本目录独立官方核回补证。
- MiniMax 的最新 `toolUse` 仅是执行中观察，不是正式终态；后续收件另加不可混淆的证据。

## 操作补充与独立性

总控授予的短 GUI 窗口只操作原 O 的 MiniMax 会话。官方复制会话 ID 后在本人临时 composer 核 ID，清除临时 ID，填入并核对同版 288B 操作补充，再点发送。UI 回执为“1 条排队中”且 composer 空；当前不把排队回执当模型消费。正文、SHA、原生匹配状态在 `operation-supplement-receipt.json`。Z 在窗口前已终态，未进入 Z 或为补充续任务。未操作 T02 草稿或另建任务。

补充只限制未知自动元数据为 path/lstat、归属 unknown，禁止 hash/parse 或再跑会读取未知内容的 observe；原源与输入不改。没有给任一模型发送对方本轮意见。

## 原报告结论及需保留的偏差

Z 自签有限 O 静态审查与两条授权正常 O 命令 Pass，无 P0/P1/P2；产品运行、生产、受限 actual、137 pending、父 T05/P0 等全部未闭。本目录只收件并准确引用该声明，不把字节核验当逐行完整审查，不把其静态结论升为 26 backlog 项或父级完整验收通过。

明确命名的正常命令原流已完整收读并原样复制：47 项测试 OK，`--check` 五件一致、280 specified／137 pending／false whole；七件源前后 hash 文件字节一致。命令 argv/exit 归属来自原报告，owner 未重新执行这些命令。

Z 报告披露：运行过旧 observe 并为新 `.mimosa` 元数据生成不透明 hash；对元数据归属的判断仅是 reviewer 声明，owner 未读取未知内容或确认归属。报告还披露一次不必要重复测试、stderr 弃流和 exit 未登记，以及静态脚本的三次探索失败。全部原文保留，不补造遗漏流，不为修改意见续任务。

独立收件复核指出原报告的 observe 表述不符冻结工具：该工具 `setupReady = phase == 'setup' and not unknown`，故 observe 阶段恒 false，不能归因为新增元数据；`return 0 if not unknown else 2`，故在报告所述有未知路径的前提下不能同时采信 exit 0。owner 采纳该准确性意见，报告原文保留，这两句列为未核／待处置，不纳入 owner 已证实事实。未为查这两句而读取旧 observe 产物或未知元数据，也未向 M 提供本轮 Z 意见。

采证自身有一次诊断投影过宽，工具输出了 MiniMax 首 user 中客户端追加 reminder；未将该上下文复制进本目录或转发给模型/总控，之后按本人正文起始标记提取。共享证据只含本人正文、必要标量与报告；不宣称这一次工具输出不存在。

## 冻结与共享边界

`check-protected-stat-only.py` 是 owner 独立标准库/Git 静态检查，不执行原 observe 或任何产品/oracle。两树分别 290 件保护来源与 11 件冻结 launch 成员 bytes/SHA 全同，HEAD 仍 detached `86df64a2`，index 空，仅当前受保护 AGENTS tracked 修改。未知额外路径仅 lstat，归属一律 unknown，不开、不 hash、不删、不忽略；因此不签全 filesystem 集合冻结 Pass。完整检查记录见 `protected-stat-readback.json`。

官方原始全流留在其私有原处；活动 JSONL 没有被复制成共享全上下文，也不以某时点 stat 或单行 SHA 冒充永久全流 hash。`initial-own-record-projection.json` 是最初时点记录，M `selectedOwnUser=[]` 缺口随后由正文核回补齐，未改写旧时点。

本批只追加 owner docs。未改源、fixture、AGENTS、审查报告或冻结提示，未 push/PR/merge/Goal。
