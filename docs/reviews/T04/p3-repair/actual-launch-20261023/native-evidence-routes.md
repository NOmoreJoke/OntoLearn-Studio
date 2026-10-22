# T04 507 本方后台最小取证路线

2026-10-23；总控实际逐项给出并已在本轮使用。仅限本方已创建任务；不开放全局/他方日志、schema、模型 header、系统 context、thinking、安装包研究或 GUI。以下是可恢复路线，不是新模型结论。

## ZCode

- 实际 SID：`session_17ab107de1b57d5bb5eaa88a997731d0`；唯一原 turn：`turn_aadae121-702d-4abc-9abb-e8adc94aaf43`。
- 正式终态源：`/Users/kyle/.zcode/cli/log/zcode-2026-10-23.jsonl`。先按这两个精确标识过滤，再只取 `turn.started` / `turn.completed` / `turn.failed` / `turn.cancelled` / `turn.canceled` / `turn.interrupted` 的时间、状态、受限错误标量。模型 request/stream stop 不能当原 turn 终态；无事件保持 UNKNOWN。当前原 turn started 为 `2026-10-22T18:05:20.711Z`。
- 原生正文源：`/Users/kyle/.zcode/cli/rollout/model-io-session_17ab107de1b57d5bb5eaa88a997731d0.jsonl`。先限制本方 SID＋原 turn；首 launch request `47ff7638-5425-42b3-9634-204ba30f4207`、`2026-10-22T18:05:22.121Z`。官方文件附件正文位于该请求的 system-message 编号块；只导出已知 `full-zcode-input.md` 的 1–137 编号行，不导出系统 header/context/thinking/HTTP headers 或其他文件。
- 实际编号前缀是数字＋TAB（首行码点 `[49,9]`），首提取器误作 literal backslash-t 失败后已纠正，工具首失败保留。137 包括 136 正文行及尾空行，重建 26203B，与固定输入 SHA `c9a2892dec9cccebaba784a10a6a9050a9e02a0fe2eebb74fd1d7316d32c7eb3` 逐字一致。只另保必要 native model/provider 标量。

## MiniMax Code

- 实际 SID：`mvs_be9afd3ec94f4d05935086be63c127b7`；唯一原 turn：`9faa1d9d-6d75-4958-beeb-9c0cc82051d7`。
- 正式终态库：`file:/Users/kyle/.minimax/v2/sqlite/runtime-state.sqlite?mode=ro`，`sqlite3.connect(..., uri=True, timeout=1)` 后执行 `PRAGMA query_only=ON`。不用 `immutable=1`（库有 WAL）；不查 schema、其他表、全局配置或其他 SID。

```sql
SELECT session_id,turn_id,terminal_outcome,updated_at_ms
FROM local_runtime_session_agent_state
WHERE session_id=? AND turn_id=?
```

参数仅上述本方 SID＋唯一原 turn。总控曾明确授权未知 turn 时仅一次已知 SID 的 current 四标量定位，本轮已完成并保存 `first-own-turn-discovery.json`；从此仅 strict 查询，不重复 SID-only、不用后续 current turn 回填原 turn。无行、null 或非终态保持 UNKNOWN。

- 原生消息目录映射：只在已知 UTC 创建日期父目录 `/Users/kyle/.minimax/v2/sessions/2026/10/22/` 一层，将 basename 的结尾与 `base64.urlsafe_b64encode(本方SID字节).decode().rstrip('=')` 精确匹配。未匹配项不输出、不读取、不递归，不跨日期；无唯一匹配保持 UNKNOWN。
- 本轮唯一实际目录为 `/Users/kyle/.minimax/v2/sessions/2026/10/22/18-11-15-844-session_bXZzX2JlOWFmZDNlYzk0ZjRkMDU5MzUwODZiZTYzYzEyN2I3`。先列本层文件名/类型，已实际发现 `manifest.json`、`messages.jsonl`；manifest 的 sessionId 与本方一致。只在该 messages 文件按本方原 turn 筛选正式 `read` 调用及结果，且仅处理 full-minimax-input.md 的实际编号正文与必要 native model/provider 标量，不导出其余 context/系统/thinking/peer。
- 实际 Read 源附件：`/Users/kyle/.minimax/v2/assets/2026/10/23/02-11-16-116-asset_20261023-021116-116_e35e6fd38c5a_4cdbab23-full-minimax-input.md`，由本方真实 read 参数取得，并非遍历 assets。原 turn 两次 read 为 1–112、113–136；136 内容行全覆盖。末尾 LF 从实际官方 asset 另核，重建26243B与实际asset及固定输入 SHA `e35e6fd38c5ae8808bad1f8bb9d8a67b5fd4333b039d0088d3bba9b527647cb2` 一致。

## 保存与边界

两方各自 `test-results/t04-review-runtime/{zcode,minimax}/metadata/input-read-proof.json` 保存真实调用标识、范围和必要来源；只编号正文另成文本。创建/UI21成员包冻结不覆盖，补充原生证据另包。正文完整到达不等于完成完整 S1 审查；正式原 turn 终态、完整原报告和全部意见处置另行核验。GUI 已于原 owner 实际 callback 后释放，总控已交 T05，本路线不重新获得前台权。
