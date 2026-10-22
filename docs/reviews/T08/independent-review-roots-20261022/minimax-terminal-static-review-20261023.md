# T08 MiniMax 终态归档静态复核（2026-10-23）

结论：归档字节、任务身份及封存终态关联核验通过；报告/metadata 的证据转述存在下述两项差异或限制，不能无保留称其全部准确。原报告保持 NotPass；官方 completed 只是执行终态，不是产品 Pass。1 P1 / 7 P2 / 3 P3 均为审方发现，尚未经过 owner 代码 triage，本复核不确认或驳回这些产品缺陷。

## 范围与身份

仅核本目录 `minimax-terminal-20261023/` 的归档报告、最终回复、终态收据、reviewer metadata、三份 raw 及其 manifest；对照 M 自有同名报告/metadata 和 metadata 明确引用的三份 raw。原生来源仅为既知精确文件 `/Users/kyle/.minimax/v2/sessions/2026/10/22/19-18-08-741-session_bXZzXzY4MzAxYWQ1MTk3ZDQ2ZWQ5MWJmOWFlZTdlYzM5ZjE5/messages.jsonl` 内原 turn 的必要验证 call/result 与最终回复。

- 37123 字节报告 SHA-256 为 `a707127833feff9b22291ffd5a3cb8fa0b944608950a172df424e104f75ea44c`，匹配 receipt，与 M 原报告逐字节一致；原件非符号链接。
- `reviewer-run-metadata.json` 与 M 自有 `metadata/minimax-m31flash-review-metadata.json` 逐字节一致，SHA-256 `586887cf0cf31a900aede597c53659a04ca083b20a567ef3505584bf2090a6e0`。
- 最终回复归档匹配原生第 157 行的 messageId、原始行 hash（含 LF）、text 与实际 model `MiniMax-M3.1-Flash`。SID 为 `mvs_68301ad5197d46ed91bf9aee7ec39f19`，原 turn 为 `eb566335-2a7c-40ad-bc6e-d0e5aff754c3`。
- 报告/metadata 所载 cwd 为 M 自有树，reviewHead 为 `5b64bfea538b638310cd3ce79e595c3b482e003d`，base/product 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3` / `93516fa8455cf4b195cbfb699aa7a6652d428b6f`，与既存输入身份相同；本轮不重做源码或树完整性审查。
- 终态 receipt 的精确 SID/原 turn 四标量记录为 completed，session 为 idle、cwd 匹配。此为 owner 封存查询结果；本复核未访问 DB 或重新执行查询。原报告生成时 turnId UNKNOWN 的历史表述保留，由后续原生链补足关联，不改写原件。

## 三份 raw

三份工作树 raw、主树复制品、manifest 与 reviewer metadata 的大小/hash 全部一致：

| raw 文件尾名（共同前缀 `minimax-m31flash-run-20261023-01-`） | 字节 | SHA-256                                                            | 内容                                                             |
| ------------------------------------------------------------ | ---: | ------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `npm-check.txt`                                              | 5286 | `93d9733dc3aa83bc6de0cc4b29d07c52bae286cfdbfcf4bf8207612032bc31f1` | 21 TS 文件、717 项；Python 1052 项、54.98s；直接记录 EXIT_CODE=0 |
| `vitest-t08.txt`                                             |  579 | `10022861d8d910d3ab72de55b11ebb4da4fdf8e9d14ec70b758a81299bf33f21` | 6 文件、87 项；直接记录 EXIT_CODE=0                              |
| `reviewer-probe.txt`                                         | 2695 | `0232a119e731a31fc5ddf95ab111b23fdad63e09873c0ce2a6016f2f4314dd88` | 修正后 10 项通过；EXIT_CODE=0；文件头注记首跑断言错误            |

原 turn 第 82/83 行关联 check 后台任务受理，第 87/88、102/103 行为其轮询；轮询仍标 running，不把包装命令的退出或任务受理当作原 turn completed。check 命令将 npm 退出值直接写入 raw 的 EXIT_CODE，raw 显示 0，并有完整检查链末尾结果。第 112/113 行定向测试 call/result 明确给出 87 项及 EXIT_CODE=0。第 123/124 行 probe 重跑 call/result 明确给出 10 项及 EXIT_CODE=0。

## 首跑失败的实际保全

在原生第 119/120 行找到首跑 probe 的精确 call/result。结果明确为 **1 failed | 8 passed (9)**、`EXIT_CODE=1`：错误断言是 body 不应含 reasoning_effort，实收值为 high。包装命令自身显示 wrapper=0、工具 execution exitCode=0，不能用其掩盖内部 Vitest 退出 1。

后续第 123/124 行使用同一 raw 路径重定向覆盖，最终为 **10 passed (10)**、EXIT_CODE=0。测试数从 9 变为 10，因此不称作完全不变的同一测试集仅重跑。现有 raw 的 header 只披露首失败事实，**不是首失败原始 stdout 的完整保存**。

本复核已按授权新增 `minimax-terminal-20261023/native-validation-results.json`，封存必要原生验证 call/result、精确 messageId、行号和含 LF 的源行 SHA-256，包括首失败可见完整 tool-result 文本与修正后结果。文件为 21204 字节，SHA-256 `5bc51b94cf749c7a07498680998423e5e35e8ffb0b3dc20069cc3cd91b4e8efd`。这补足原生结果证据；不将其冒充已不存在于该 raw 路径的首跑原文件，也不打开 background-tasks 额外输出路径。

## 两项转述差异/限制

1. **Ruff 格式文件数不符。** 报告第 69 行及 reviewer metadata 的 npm-check result 称 `ruff format --check 179 文件`；实际本次 raw 为 **224 files already formatted**。717 TS、1052 Python 及退出值不受影响。原文不改，后续摘要必须使用 224 或附注原文有误。
2. **verify:sources 的 npm 退出码未独立捕获。** 第 112 行对应 call 将 `npm run verify:sources` 接到 `tail -25`，未设置 pipefail；第 114 行结果确实包含“已核对 12 个归档源文件。”与 EXIT=0，但后者只证明 tail/管道包装退出，不能直接证明 npm 进程的退出值。metadata/report 的 exit 0 若被理解为 npm 独立退出码，证据不足。该 call/result 已有限封存于上述 JSON，支持实际调用与 12 源成功文案，不能提升为单独完整 raw 或独立 npm 退出码。结果前的 esbuild 可用性检查报错不混作 verify:sources 本身失败。

## 结论表述与未验边界

报告和最终 assistantText 均明确总体 NotPass，区分关键真实验收缺前置与审方代码发现；终态 receipt 也明确发现尚未 adjudicate。不能把 10 项行为探针通过当作严重度/责任归属成立的证明，不能把报告中的全部观察自动记为 owner 已确认缺陷或已修复。

原报告第 10 节保留真实模型、领域、Diff/事务/撤销、最终授权/安全存储、App 挂载、平台/真人/CI/远端等未验条件。历史运行读档与审方本次实际运行有区分；本复核读取归档与 native 结果仍然只是读档，没有重跑验证。metadata 另列的 postArtifactLintFormatCheck 不在本轮三 raw 读取面内，本复核未独立验证它。

本轮不读取或转发另一审方的意见/报告/状态，不访问 UI/DB，不导出 headers、system 全文或 thinking，不执行产品、测试、API 或 probe。仅新增本报告与获准的最小原生验证 JSON；双方原报告、metadata、raw 和产品文件均不修改。
