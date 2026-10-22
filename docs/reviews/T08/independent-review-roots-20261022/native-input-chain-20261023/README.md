# T08 原始 turn 完整输入链（2026-10-23）

两项原始任务已实际消费同版完整冻结派发输入；本批补足 native 输入证据，不是终态或 Pass。没有再操作 CUA，没有恢复或重建原 Goal，没有新执行产品验证。

| 项目 | ZCode | MiniMax |
| --- | --- | --- |
| SID | `session_cd996c3a9b47f03713b41eaae59a83b0` | `mvs_68301ad5197d46ed91bf9aee7ec39f19` |
| 原始 turn | `turn_cd14dccd-3356-41ea-acb6-1b8db45132c0` | `eb566335-2a7c-40ad-bc6e-d0e5aff754c3` |
| 独立 cwd | `.worktrees/T08-zcode-review-93516fa` | `.worktrees/T08-minimax-review-93516fa` |
| reviewHead | `5b64bfea538b638310cd3ce79e595c3b482e003d` | 同左 |
| 完整正文 | 373 行 / 59804 bytes | 373 行 / 59859 bytes |
| 正文 SHA256 | `8951b0e305e9326dbb41ff8a2f16c4de5f1c35dc0163d19601b2daa08683029d` | `65104b0ce095ed1c163d16645cc408c8798bf3bb7fd8fc5132494c82f8eea65f` |

base `5f910b52c69d86a1076b2032e5d3c63e715947f3`、产品 `93516fa8455cf4b195cbfb699aa7a6652d428b6f` 保持。完整原始提示前缀与执行补充均在 native 正文里；完整正文包含全部 25 实现/测试/fixture、44 产品差异、828 产品树及 PRD 原门。此处不重新评判实现。

## ZCode 精确原生证据

唯一源 `/Users/kyle/.zcode/cli/rollout/model-io-session_cd996c3a9b47f03713b41eaae59a83b0.jsonl`。逐条只接受本人 SID、原 turn、`querySource=main_turn`。首请求 `messages[4]` 的本人短启动单独保存；只从 `messages[5]` 中本人附件标题起提取连续编号 1..373，去数字 TAB 前缀、保留原末 LF，得到 `zcode-original-turn-attachment.txt`，与本人冻结正文逐字节相等。没有复制其余 system、headers、thinking 或私有上下文。首原生行 SHA、路径、时间、范围和设置见 `zcode-original-input-chain.json`。

首请求实际 `GLM-5.3`、thinking enabled、`request.body.output_config.effort=max`；完全访问来自前批官方新任务 UI。`zcode-native-identity-result.json` 保留原 call 与配对非错误 tool result，实测本人 cwd 和同一 reviewHead；不以本 owner shell 代模型自身检查。

官方终态仅查获准唯一 `/Users/kyle/.zcode/cli/log/zcode-2026-10-23.jsonl`，必须双匹配本人 SID+原 turn，再取 completed/failed 的最小事件。当前 `zcode-official-status.json` 为 0 匹配，UNKNOWN；不是失败或已完成。`progress-observation.json` 的 model_io 结束时间和 tool-calls 只描述单次模型调用。

## MiniMax 精确原生证据

只在 `2026/10/22` UTC 日期下按完整本人 SID 的 base64url 无填充后缀唯一过滤，没有列出父目录或其他会话。唯一目录 `/Users/kyle/.minimax/v2/sessions/2026/10/22/19-18-08-741-session_bXZzXzY4MzAxYWQ1MTk3ZDQ2ZWQ5MWJmOWFlZTdlYzM5ZjE5/`，manifest.sessionId 相等，仅消费其 paths.messages 指针。首 user 只保留 canonicalTextRange 4441:5277 的本人短启动，不导出客户端其余上下文。实际 assistant model 为 `MiniMax-M3.1-Flash`；xhigh/始终授权仍由前批本任务官方 UI 证明，不以全局配置替代。

首原 turn 对正式 asset 的三个 read call 及非错误 tool result：

| call ID | native 调用行/结果行 | 实际返回正文行 |
| --- | --- | --- |
| `call_WiUsYhjnCyovMri1HjYhBhmG` | 5 / 6 | 1–155 |
| `call_kYPDuRdwUVmffo3rvA3wVIPH` | 7 / 8 | 156–282 |
| `call_PwI5OcNbcx1viswycPgIgU7N` | 9 / 10 | 283–373 |

第一、二段客户端截断提示并未造成漏读，后续真实 offset 续读完整覆盖。`minimax-native-read-segments.json` 只存本人 read 调用、编号正文和来源行 SHA；去箭头编号、移除客户端截断包装、恢复源文件末 LF 后得到 `minimax-original-turn-attachment.txt`，实核与正式 asset 原字节和冻结正文三者完全一致。正式 asset 精确路径、原始 user 身份和完整重建说明见 `minimax-original-input-chain.json`。`minimax-native-identity-result.json` 是原 turn 首个 bash 的非错误返回，含实际本人 cwd、HEAD、附件字节/行/hash。

官方终态仅按已给出的两条四 scalar SQL 路由，用 `mode=ro`、`query_only=ON`、timeout=1；agent_state 带精确 SID+已核原 turn，sessions 带精确 SID。未探测 schema、其他表或会话，不启 runtime、不改 journal。`minimax-official-status.json` 的原 turn terminal 为 null、session status=started，真实 workspace_dir 为本人独立树，project_workspace_dir 为项目分组本体；这不是完成。

## 当前交付边界

03:25:13 北京时间观察时，双方精确约定报告路径均不存在。`progress-observation.json` 保留这一时点及来源；后续只在报告真实出现后 lstat 非 symlink、原字节封存、全文阅读并结合原 turn 官方终态判断。各方本轮意见互不转发。

本批完整输入和自身 cwd/ref 已有 native 直接证据，供根独立核验统计；不自行填写 rootverified 或指定 Pass。原 source/check/PRD 验收/父发布门保持，旧创建收据和它们当时的 UNKNOWN 不改写。
