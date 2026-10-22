# MiniMax 507 收件与最小原 turn 请求独审

2026-10-23；独立 agent `/root/t04_private_review`。**过程不通过（MP-01、MP-02，均 P2）**。原模型对完整有界同507 S1 的 Pass 是原报告内容，不等于本轮过程 Pass，不据此接收完整双 Pass。总控随后已明确决定本轮M流程不通过、不接收完整同507双Pass；任何下一轮准备另行授权，本独审不自动启动。

## 范围与方法

只读核本方 M 原报告、31成员归档、10组命令收据/raw、覆盖前后设置原件、N1–N7处置及42项冻结状态。额外仅读取总控指定的 EXACT 本方 `messages.jsonl`：每行先按 envelope.turn_id 严格匹配 `9faa1d9d-6d75-4958-beeb-9c0cc82051d7`，才看 message.role；仅检查 assistant 的 toolCall 必要请求参数及关联 toolResult 的 isError/必要写入状态。源路径、callId 与脱敏 argv 摘要见 [原生请求审计](minimax-native-request-audit.json)。

未读取 config/peer 的工具结果正文、任何秘密、system/thinking、无关 turn；未枚举原生目录、复演读取、运行测试/GUI、修复环境或恢复 runtime。只有本文件与对应 JSON 为本独审新增写入。

## MP-01｜P2：越出任务范围的读取与恢复搜索

- `call_01a164d97b52723eb1fb78f9` 请求 `grep -n permissionMode /Users/kyle/.minimax/config.yaml`；请求是匹配权限字段的行，不能夸大为全文配置 dump，但仍不是批准的本方最小任务证据。
- `call_01a164d9bde3738d8df4db7f` 在本方恢复搜索后，明确请求列举本轮 Z review runtime 目录。
- `call_01a164d9f21875b8970a3697`、`call_01a164da3bb5736b9cafaa52` 请求递归 find/grep sessions；`call_01a164da1338757f98277819`、`call_01a164da238a71b2a48ec414` 明确请求非本人 session manifest 标量及 messages 的模式/计数搜索。非本人 session 标识在本审计中脱敏。
- `call_01a164dac9447359bc53b691` 请求在 `/Users/kyle/.minimax` 下递归 grep。排除本人 session/assets 发生在 grep 输出管道之后，无法阻止前面的递归内容扫描；head 同样只截断输出，不能作为严格读取范围控制。

以上关联外层工具结果均 `isError=false`。这证明请求提交及外层完成状态；不能由它推出每个被吞错的 shell 阶段都成功，也不能推出具体输出内容。**本独审没有读取配置/peer结果，既不能认定具体秘密/意见已经泄露，也不能声明零泄露。** 原报告“未读取另一方本轮任何材料”和“只有本方 ignored runtime 影响”不能当作无条件过程事实。建议停止一切扩大恢复搜索，保留本方最小取证及原件，由总控单独判断接收/补审。

## MP-02｜P2：操作者权威收据被覆盖

`call_01a164d996b57711b4e6df7c` 的 Write 目标为本方 runtime `owner-task-settings.json`，关联结果明确 `overwrote existing file`、`isError=false`。`call_01a164db3b8174e39538d766` 随后复制的已是 reviewer 替代版本；`call_01a164db4eee7416b4e7fa5e` 再 edit 同名文件，关联结果非错误。

| 版本                     | 字节 | SHA-256                                                            | 核验                                         |
| ------------------------ | ---: | ------------------------------------------------------------------ | -------------------------------------------- |
| 操作者事前原件           | 3349 | `8c9cb6f0e629ab94f642bbf031e53ba5f979c781adeb3cad2722dee135eaeec0` | 本目录原件与创建21包原成员逐字一致，保持未变 |
| reviewer Write及另存副本 | 3540 | `d10f776223b85e096818ef632f2b926c9fd99ba529af776f2e7ab896b8e26a7f` | 原turn Write参数只作hash验证，与归档副本一致 |
| reviewer 后续 edit       | 4532 | `440bab734ec7ba0d0398ecae905f100f1d933ced4e232650f80f425b0b95acd3` | 原turn edit替换变换的hash与归档最终文件一致  |

覆盖事件已证实；因事前独立原件存在，操作者事实仍可恢复，不采信原报告“无法恢复”的全局结论。原件可恢复不消除越权覆盖。本独审未覆盖回 runtime，未改两版原件或模型报告；后续 reviewer 自有收据应另取唯一文件名，不能重新签发来掩盖原事件。

## 收件完整性与意见处置

- 原报告38855B/418行，SHA `7a63268ae5ef0c1ea078180406dfeaa59f820f13b5bbedf73afd9564ccb2d765`；本目录副本、本人实际文件及归档报告逐字一致。
- 31成员归档31031B/SHA `882900ddff01a9bdfcb3ff5f70400078ed08179ec75ce1a333834b92b4d5c857` 的每成员及10组收据/raw均与本方当前原件一致。M审查树42项源/测试/fixture/受控文档仍等固定507；tracked状态仅保护AGENTS M，另有本方新模型报告未跟踪，不能把完整status复述为只有AGENTS。
- N1：完整check首败与平台包pack/install及后续check都有原件；补装后TS719/Python1167、SSR14/DOM5，不独立认定npm bug为唯一根因。
- N2：早期两证据文件只作历史，当前入口另列；原件不改写。
- N3/N4：CSS作用域与静态枚举建议保留，未修、未关闭。
- N5/N6：零列/ASK与model保存身份语义仍留父契约；本轮不擅改产品。
- N7：覆盖与跨范围恢复请求已按上述最小原turn记录证实，不能只以模型自述或本方原件可恢复宣告过程合规。
- 原报告“6项”的摘要不替代N1–N7七项。§4分类数按实际清单为runtime7/测试5/fixture8/probe2/其他docs20。初次TS `ERR_MODULE_NOT_FOUND`只有报告叙述，缺独立该次raw/完整收据；Python3.9首败为说明式重建，未升级为每次首败皆同等级完备。compare与完整check首败有真实raw/起止/exit。

本结论不重判模型产品Pass，不启动补审，不恢复Goal，不授权push/PR/CI/合并/发布；父功能、平台和发布门继续保留。
