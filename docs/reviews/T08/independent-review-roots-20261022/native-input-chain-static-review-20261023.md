# T08 原生输入链静态复核（2026-10-23）

结论：指定输入链核验通过。两份重建附件均与各自冻结完整 dispatch 逐字节一致；已核原 turn 的附件行块、身份工具结果及模型设置证据。此结论仅针对输入证据，不是审查完成、产品通过或指定模型 Pass。

## 实际核对

读取 `native-input-chain-20261023/` 中指定输入链元数据、附件重建文本、行块及身份结果和封存状态。原生来源严格限于以下两个已知精确文件：

- Z：`/Users/kyle/.zcode/cli/rollout/model-io-session_cd996c3a9b47f03713b41eaae59a83b0.jsonl`，只处理第 1、2 行中的精确身份标量、自有附件编号行和首个身份工具 call/result。
- M：`/Users/kyle/.minimax/v2/sessions/2026/10/22/19-18-08-741-session_bXZzXzY4MzAxYWQ1MTk3ZDQ2ZWQ5MWJmOWFlZTdlYzM5ZjE5/messages.jsonl`，只处理前 10 行内指定原 turn 的附件 read call/result、模型身份及身份工具结果。

未遍历其他 session，未读取模型报告或意见，未复制 headers、完整 system 或模型 thinking 正文；未访问 CUA、DB、源码或运行产品验证。只新增本报告。

## 附件字节与原 turn 关联

| 角色 | 重建附件与冻结 full dispatch | 字节 | SHA-256 |
| --- | --- | ---: | --- |
| Z | 逐字节相同 | 59804 | `8951b0e305e9326dbb41ff8a2f16c4de5f1c35dc0163d19601b2daa08683029d` |
| M | 逐字节相同 | 59859 | `65104b0ce095ed1c163d16645cc408c8798bf3bb7fd8fc5132494c82f8eea65f` |

Z 第 1 条原生记录的 `sessionId` 为 `session_cd996c3a9b47f03713b41eaae59a83b0`，`turnId` 为 `turn_cd14dccd-3356-41ea-acb6-1b8db45132c0`，`querySource` 为 `main_turn`。首请求 `request.messages[5]` 内自有附件编号 1..373 去除编号、恢复源末尾 LF 后，字节等于归档重建附件和冻结 full dispatch。编号 374 是终止空行，未作为额外正文。第 1 行含 LF 的原始字节 hash 匹配输入链元数据。

M 的三组 read call/result 均属于原 turn `eb566335-2a7c-40ad-bc6e-d0e5aff754c3`，均读取同一官方附件精确路径，结果 `isError=false`：

| 原生 call/result 行号 | call ID | 连续覆盖附件行 |
| --- | --- | --- |
| 5 / 6 | `call_WiUsYhjnCyovMri1HjYhBhmG` | 1..155 |
| 7 / 8 | `call_kYPDuRdwUVmffo3rvA3wVIPH` | 156..282 |
| 9 / 10 | `call_PwI5OcNbcx1viswycPgIgU7N` | 283..373 |

逐组核对 `minimax-native-read-segments.json` 的 call 对象、message ID、result 的 toolCallId、原 turn、原始行 hash（含 LF）、编号正文及 coveredLines，均匹配原生精确行。三组连续覆盖 1..373，无缺行、重复或跨 turn 拼接；由原生编号行独立重建的字节同样匹配归档附件和冻结 full dispatch。客户端截断提示不计入附件正文。

## cwd/ref 与模型设置

Z `zcode-native-identity-result.json` 与原生第 2 行首请求中的对应 tool result 完全匹配；其 call 与第 1 行响应中的首个身份工具 call 相同，toolCallId 为 `call_7f39455092ee40ff9136ea32`，结果非错误。M 身份结果匹配原生第 3 行，message ID、toolCallId、原 turn、原始行 hash 和文本均相同，并关联第 2 行对应身份工具 call。两结果分别明确返回自有 `T08-zcode-review-93516fa` / `T08-minimax-review-93516fa` cwd 及 `5b64bfea538b638310cd3ce79e595c3b482e003d`。

Z 原请求记录实际模型标量为 `GLM-5.3`，`request.body.output_config.effort=max`，`thinking.type=enabled`；这里只核设置，不读取推理正文。M 三个原附件 read 调用的原生模型标量均为 `MiniMax-M3.1-Flash`。M 的 xhigh 与始终授权仍来自既有 owner 官方任务 UI 读回，不能用提示文本或原生 model 字段补证实际 effort；本轮未扩大到全局配置或应用 UI。

## 状态边界

封存 `zcode-official-status.json` 对精确 SID/原 turn 的 terminalEventMatches 为空，officialTerminal 为 UNKNOWN；`minimax-official-status.json` 的对应原 turn agentState 为 null，session 状态为 started。这里只核封存 JSON 的表述，未再次查询日志或数据库。无 Z 事件或 M null 均不能推出 completed、成功、失败或取消；model_io 单次调用的 completedAt/finishReason 也不是原 turn 官方终态。

本次只固定并验证输入证据链，不等待或读取双方报告，不核验审查覆盖、发现处置或最终结论。产品93516fa、原完整验收与后续指定双审门保持，输入链通过不能替代这些门禁。
