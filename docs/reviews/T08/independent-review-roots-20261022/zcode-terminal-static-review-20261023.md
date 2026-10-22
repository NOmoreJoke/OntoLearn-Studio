# T08 ZCode 终态归档静态复核（2026-10-23）

结论：ZCode 报告归档、身份关联与结论表述核验通过。ZCode 的报告结论为 **NotPass**，官方执行 completed 不等于验收 Pass。本次只核指定材料及运行证据，不是重新产品审查，也不将报告自述的阅读范围升级为完整无遗漏验收。

## 归档与身份

- `zcode-terminal-20261023/zcode-glm53.report.md` 为 27221 字节，SHA-256 `d97250234022978231d34430ecd7914ce13d5b65c7cb34cf096d7879b4d3e4c8`，与 receipt 声明及 Z 自有报告原件逐字节相同；原件不是符号链接。本复核全文读取归档报告。
- `original-main-turn-final-response.json` 的 assistantText 与已知精确 model-io 文件第 41 行 `response.text` 完全一致，原始行含 LF 的 SHA-256 匹配 `6dcbdff297e98dcfeb472831de727b9b1945dcd54f7175dc7d908428cde92496`。
- 该原生记录为 SID `session_cd996c3a9b47f03713b41eaae59a83b0`、原 turn `turn_cd14dccd-3356-41ea-acb6-1b8db45132c0`、`querySource=main_turn`，与既存输入链一致。固定 reviewHead 为 `5b64bfea538b638310cd3ce79e595c3b482e003d`，base/product 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3` / `93516fa8455cf4b195cbfb699aa7a6652d428b6f`；本轮未重做此前输入链或源码核验。
- terminal receipt 导出的官方事件标量为同一 SID/turn 的 `turn.completed`、`status=completed`，时间 `2026-10-22T19:27:15.851Z`。本轮仅核这一封存事件收据的身份与语义，未获新授权去读取官方日志原始第 10204 行，故其行 hash 未独立回源。第 41 条 model_io 的 stop/completedAt 自身不作为官方 turn 终态证据。
- 原报告保留其生成时 turnId UNKNOWN 的历史表述；后续原生输入链和终态收据提供精确关联，不改写原报告。

## 三份 raw 与实际运行证据

逐份读取报告明确引用的 Z 自有三个 raw，并核对主树 `validation-raw/` 复制品，均逐字节相同：

| raw | 字节 | SHA-256 | 可核结果 |
| --- | ---: | --- | --- |
| `run-001-check.txt` | 7458 | `c201ad0455f5e74ddbc0f77b9839667c2752f7c8ffb2783d61e531b844e2fc5d` | check 完整链输出；21 TS 文件、717 项；Python 1052 项、56.94s |
| `run-002-probe-direct.txt` | 3737 | `577f88e8ee4198004158513a8435ba45d113c0aabd827e09d0e473b6ced5d553` | 五例，每例明确 `exit=0` |
| `run-003-t08-targeted.txt` | 561 | `2ca5972feb761e29d2f6fdd2e10af44de457da756e7ffe6e58fa8952fa0fcf15` | 6 文件、87 项 |

只从已知 Z 精确 model-io 文件筛选同 SID、原 turn、main_turn 的必要验证 call/result：

- 第 31 行 call `call_225c79686b774e69867463a2` 在本树以隔离环境运行 check，raw 重定向路径吻合；第 32 行对应 tool result 非错误，明确 `exit=0`。随后原生摘要结果给出的 raw SHA 与本次实测一致。
- 第 33 行 call `call_663f26fefb7848f29a5024c0` 运行五个有限 probe；第 34 行对应结果非错误、`done=0`，且五例分别有 `exit=0`，不单以循环最终退出推断每例成功。
- 第 34 行 call `call_ce17181929a24d7aba9fcde8` 运行六个 T08 定向测试；第 35 行对应结果非错误，明确 `exit=0`、6 文件与 87 项。

raw 的五例内容支持报告所述：Q-01 仅 A01；Q-02 空且 inputSha256 改变；同数量语义错得到 A02 且 querySha256 不同；语法错返回 QUERY_SYNTAX；CSV 身份为字符串 001/002、行 2/3、名称泵站A/泵站B。这里只核既有运行产物，不执行 probe，也不把手工协议/有限固定输入当真实模型或正式领域能力。

以上是 **Z 已执行验证的原生证据及 raw 读档**。owner 复制归档与本复核读取都不是重跑；本轮没有运行安装、产品、测试、API 或 GUI。

## 结论与覆盖限制

报告第 7 节称已实现纯模块中无新 P0/P1/P2，只列三条 P3：并发 executeCalls 的错误码语义、重复 ID 与参数错误的归因顺序、returnedModel 漂移的保守评估观察。它们是 Z 的观察项，本复核不重新裁定产品问题，也不将其记为已修复。

报告第 8–11 节及最终 assistantText 均明确：NotPass 主要因为完整关键验收缺失，包括真实 I06 最终授权/传输/安全存储、T01 Diff/真人确认/事务/撤销、真实领域工具与 App 接线、真实模型主体和消费上限、11.3/12.2/A 系列真实路径、平台/真人/发布门。局部单测或静态未发现新阻断不能替代整体通过。终态 receipt 也保留这一口径，未把 completed 改成 Pass。

以下限制必须随报告一起传递，不能只摘“全文”或“全部通过”摘要：

- 原报告第 3.5 节（第 46 行）明确：三份 gzip 原始内容未展开，两份中间 verification 未逐字段全文展开；只核其元数据和关键声明，并作交叉核验。报告整体“全文”表述受此具体例外限制。本复核未自行补读或抹去该限制。
- source-git-bytes 的 941 项清单读取与 **257 项 blob 抽查**不同；不能转述成 Z 独立逐项重核全部 941 个 blob。25 项产品快照核对、44 差异和 828 树计数也是各自不同证据，不能据此声称全文审过全部 828 项实现。
- 未实际验证的真实 provider/domain/App/平台等门仍未验；报告的局部“真实通过”仅指其受控单测、SSR 或有限输入运行，不是生产闭环。

本复核没有读取 MiniMax 本轮任何报告、状态或发现，没有访问 UI/DB，也未导出 headers、system 全文或 thinking。除新增本报告外，未修改双方审查树或冻结材料。后续是否满足指定双审完整交付及发布条件须另行核验，不能由本次归档核验代替。
