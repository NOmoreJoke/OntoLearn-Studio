# O15 新完整双审：实际创建与原生输入核回

两个新任务均正式受理，GUI 已于 2026-10-22 18:29:54Z 明确释放给总控。当前只确认派发和输入身份，尚未收到两项正式终态及完整报告；原 15 条外部意见仍 open。源候选 b88be226、受审过程 HEAD 0f87f2c2，冻结输入不改。

## 精确本方路由

- ZCode：`session_b89ca579bc1862a94909bd1503bafbc6`；原 turn `turn_a4a74b36-8465-458a-a385-cdfd22c33d3c`。
- Z 原生模型流唯一已核路径：`/Users/kyle/.zcode/cli/rollout/model-io-session_b89ca579bc1862a94909bd1503bafbc6.jsonl`。只提取本人 session/turn 的公开输入、指定设置、工具正常验证与末响应标量；不复制 headers、凭据、thinking 或整个 system 容器。正式日期事件源已由总控核准为 `/Users/kyle/.zcode/cli/log/zcode-2026-10-23.jsonl`。读取该唯一确切文件，先双匹配本人 SID 和原 turn，再只提取 turn.completed/failed 的 time/status 及必要 error（最多2KiB）；不导出其他 context/header/thinking/peer，不换日期遍历。无匹配即 UNKNOWN，最后一次 tool-calls 或 model-io stop 不能替代官方完成。
- Z 首请求实际 GLM-5.3、thinking enabled、effort max；权限以本人任务 UI 完全访问为证。首请求 messages[4] 是本方短启动，messages[5] 的 system 容器含客户端正式附件。仅从本方已知标题起提取 21 行，去数字 TAB 前缀，重建 7231B / `1c51fb3284ed83158e304d689cbe686154d64f6c207926939dbda706d3f9f94f`，与冻结全文逐字节相等，保留最后 LF。其余 system 内容没有复制。
- MiniMax：`mvs_c28510d4b96a4ecbaea7be3f838c5110`；原 turn `677c3d52-3d00-45ec-96af-2005b0a71d58`。
- M 原生目录由精确 SID 的 URL-safe base64 文件名元数据定位，且 manifest.sessionId 相等：`/Users/kyle/.minimax/v2/sessions/2026/10/22/18-25-30-343-session_bXZzX2MyODUxMGQ0Yjk2YTRlY2JhZWE3YmUzZjgzOGM1MTEw/`。只读其已核 `manifest.json` 必要 path/sessionId 及 `messages.jsonl` 中本方指定 turn；不扫其他会话。
- M 首 user message id `msg-user-v1-teeJN5NqgfI2BIc_GKx-qooJqSMMHSxCN9bp_m-I00o`，只取 canonicalTextRange 4393:4758 的本人短启动；客户端追加上下文不复制。首 read 调用 `call_01a164dc795f71e6906f58db` 读取正式 asset，和同 turn 非错误 toolResult 配对。去行号箭头、仅规范客户端额外末尾空行，重建 7279B / `c31f1b5d44bb008becdadb21b4ea156058548c809cbcbf9d5db80e47e6629ddd`，等冻结全文；正式 asset 原字节也另核完全相等。
- M 正式 asset：`/Users/kyle/.minimax/v2/assets/2026/10/23/02-25-30-603-asset_20261023-022530-603_c31f1b5d44bb_7dbe04ab-launch-prompt.md`。只因本方已核正式 read 路径而读取，不枚举其他 asset。
- M actual UI M3.1-Flash（订阅限免）/ xhigh / 始终授权；原生 assistant 的实际 model 为 MiniMax-M3.1-Flash。未用用户全局配置代替本任务设置。

## M 正式终态最小 SQL

数据库 `/Users/kyle/.minimax/v2/sqlite/runtime-state.sqlite`，URI `mode=ro`，timeout=1，`PRAGMA query_only=ON`；不设 immutable，不改 journal，不启 runtime，不扫表。所有参数必须是上述本人 SID 和已核原 turn：

```sql
SELECT session_id,turn_id,terminal_outcome,updated_at_ms
FROM local_runtime_session_agent_state WHERE session_id=? AND turn_id=?;
SELECT session_id,status,workspace_dir,project_workspace_dir
FROM local_runtime_sessions WHERE session_id=?;
```

首次未知 turn 定位已使用相同 agent_state 四字段、精确本人 SID，无其他 SID。之后有原 turn 必须带 turn_id，不用子任务/投递 turn 的完成替代原审查。

## 已知输出与边界

报告只从两树各自 `docs/reviews/T05/projection-R3-receiving/launch-O15/report.md` 收件。实际出现后先 lstat 非 symlink、原样复制到本 owner 新过程目录、核字节/SHA、全文读，再结合原 turn 正式终态判断；任务自述不是 owner 已复做的全 150 审查。各自 raw 正常验证只在报告明确列出路径后读取。禁止互传本轮意见，不借旧 Z Pass 或续接旧 M。

现阶段 UI 已观察 M observe exit0、450 保护输入一致；这只支持输入保护，不能替代150项全文审查。owner 不重跑 observe、不覆盖模型记录，不安装额外依赖，不再 CUA，不改变源码/fixture/验收，不做 Goal/push/PR/merge。

本批原生公开本方输入片段入库，是为独立验证正式附件消费链；完整活动 JSONL、system、thinking 与私有上下文留在官方原处。首批采证在成功保存输入后尝试列本方 manifest 声明的 reports 子目录，目录不存在，报 FileNotFoundError；没有创建该目录、没有因此扩大扫描，也不把该错误归为模型审查失败。GUI 导航两次可恢复问题同样只属操作记录：原生路径框首次未输入成功（未点错误目录打开）；一次缓存 AX 字符串为空造成读取失败。两者均在正式发送前按新鲜状态恢复，不影响上述实际受理证明。
