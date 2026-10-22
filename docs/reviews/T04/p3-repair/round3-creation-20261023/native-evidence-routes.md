# R3已授权本人原轮次最小取证路由

GUI已在2026-10-22T20:15:03.300Z明确RELEASE，总控已ack并交T06；后续禁止CUA，仅下列已知本人SID/原turn精确后台，不重新全局查路由。此文件供owner续接，不给审查模型自行查身份或恢复授权。

| 本人任务 | SID | 固定原turn |
| --- | --- | --- |
| ZCode R3 | session_56788899c99e13a8d348bb21b2d62289 | turn_dee9efbf-58dc-473e-8f12-b9be14ed1a72 |
| MiniMax R3 | mvs_4e9f4b2b7bdd47348293cdbb41f60109 | 659fd77a-9a0b-49c5-b39f-48aeb928d9f1 |

Z官方终态只读精确`/Users/kyle/.zcode/cli/log/zcode-2026-10-23.jsonl`，先以本人SID+原turn原行过滤，JSON后严格同值，只取turn.started/completed/failed/cancelled/canceled/interrupted与timestamp/status及必要错误scalar；SDK stopped/文件存在不代替官方turn terminal。已知original turn后不得SID-only发现current fallback。

Z输入源只读`/Users/kyle/.zcode/cli/rollout/model-io-session_56788899c99e13a8d348bb21b2d62289.jsonl`，严格同SID+原turn，首requestId `c4f95e04-13cd-4341-80c9-0a942b9b1e53`。只提取已知冻结full-zcode-input正文编号TAB块1–148，最后空编号行承担尾LF，精确重建29675B。不得导出role/header/system/context/reminder/thinking等其余内容。

M只读SQLite URI `file:/Users/kyle/.minimax/v2/sqlite/runtime-state.sqlite?mode=ro`，timeout1、query_only ON，不immutable（要见WAL）。唯一后续SQL：

```sql
SELECT session_id,turn_id,terminal_outcome,updated_at_ms
FROM local_runtime_session_agent_state
WHERE session_id=? AND turn_id=?
```

固定params为上述本人SID+原turn。原turn首次定位已按已授权runbook做过一次本人SID-only四scalar查询并保存在创建归档；禁止再次SID-only、其他表/列/schema或其他会话查询。

M本人唯一native目录已按已知UTC日期2026/10/22下单层精确本人base64url SID后缀定位，未读/输出未匹配目录。后续直接只读：`/Users/kyle/.minimax/v2/sessions/2026/10/22/20-13-45-206-session_bXZzXzRlOWY0YjJiN2JkZDQ3MzQ4MjkzY2RiYjQxZjYwMTA5/messages.jsonl`。逐行先严格envelope.turn_id过滤再看必要工具，不能导出全轮角色/头/上下文/思考。

已核完整输入Read为`call_01a1653fa8b973348ab42383`行1–98及`call_01a1653fb1777661b258699a`行99–147，toolResult均isError=false。只抽其已知输入编号内容，147行连续；尾LF另从实际Read参数指向的唯一附件asset读取，精确重建29715B，不冒充模型额外读148行。asset精确路径与toolResult messageId见minimax-input-read-proof.json，不枚举assets。

M最初附件哈希失败只核了已知两call `call_01a1653f943e7160be41828e`和`call_01a1653f9ebd77e7917fd969`必要argv/error：前者cd到文件而非目录exit1，后者直接核文件成功。不是工具审批拒绝；失败原件在归档，不重跑补造。若后续真实审批拒绝，保存本方必要错误并报总控，不包装/脚本绕过。

模型报告仅各自审查树`docs/reviews/T04/round-3/zcode-glm53.md`与`minimax-m31flash.md`；原报告存在后全文读回、保持原字节、核每项发现与运行收据。不得代判另一方或父验收。操作者设置/受理在各树本方runtime/operator目录，原记录不原位改写；新增native原turn/输入证明单独文件。未知保持UNKNOWN，旧R2 Fail不转Pass。
