# d643 完整双审准备包独立审查

结论：当前纯准备收件范围通过，未发现阻断问题。本报告是非作者静态准备核查，不是指定模型审查、环境就绪证明、setup/运行许可、GUI START、Pair Pass 或父验收通过。

## 实际阅读和核验边界

两份 `full-input.md` 已分别分段完整阅读，无未补读的截断：ZCode 为 1–95、96–190、191–285、286–380、381–475、476–568 行；MiniMax 为 1–115、116–230、231–345、346–460、461–568 行。包含当前完整执行约定和全部六块历史原文，没有只读头尾、delta 或摘要。两份当前约定均逐字包含中央 `review-contract.md`；根有限收件全文亦由内嵌块读取，并与中央 `controller-intake.md` 字节核对。

实际核对中央 manifest、source/evidence 索引、tracked 索引、两方 mapping、setup proposal、operator 模板和 AGENTS 固定身份，以及两个新 ownroot 的本次九件副本、AGENTS、Git 身份/status、32 源文件的字节/hash。源只作身份核验，没有产品代码语义复审、import 或执行。99 个 evidence 项只核固定 Git blob ID/字节及索引角色，不重新读其历史正文或独立重算全部 99 项 SHA-256；983 项只核 tracked 元数据，不声称逐文件语义阅读。未跟随历史路径到旧实际根或外部 `.private` 原件。

没有模型消息、任务发现/创建、GUI/CUA、浏览器探针、Chrome 实体读取、global/native/未知 metadata 读取、setup、依赖安装、产品测试、构建、服务、API、push 或 Goal 操作。只新增本报告，并仅对本报告执行本树显式 Prettier 格式/check。

## 固定输入身份

| 材料                                | 字节数 | SHA-256                                                            |
| ----------------------------------- | -----: | ------------------------------------------------------------------ |
| `preparation-manifest.json`         |  16942 | `72efeafc9f8c44bc05ddb6e24b9a471b8c3f0d4b972d23843f3557fbf0df39be` |
| `source-and-evidence-manifest.json` |  62519 | `5f697dcba77a52e5c3109219d2a81a63bfb22290e3947413dff4baf442b30146` |
| `tracked-review-head.json`          | 167985 | `a619d1ef9bc6d5474cc5890ec4efb24fb7095ec04f5072fd7093ec37e1995d87` |
| `review-contract.md`                |  20507 | `6ec12c82fdcd086aa0cf0558be4bd197bf85387194c0592df9dd875078b95d30` |
| `controller-intake.md`              |  11242 | `1c711134b2c7c526c72b0a46b0ba093579efd9d4839fe909b638b368c4d48d48` |
| `agents-current.txt`                |  15147 | `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` |
| `zcode/full-input.md`，568 行       |  96990 | `fc7c6270f0a2fc6745b506af5e3a85f385caa2f4f62519a93d628cb54eb7aa0b` |
| `minimax/full-input.md`，568 行     |  97059 | `e7065252cf88c3e14c2a709675fa2ef8bfde3c42679bc52795740794027ac2e8` |

批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`、产品源 `d643c5a41f42d4d5395ab7d6c457c6e002cf481f` / tree `fbbe968e500d98eed8277588a0a535036260f12d`、物理 review HEAD `60b0672c91d2fa4b87f2481b40f24bbbf22b3d2d` / tree `a5070a7e47c6e7170a384382f483e2d94963ceb1` 分列。实核中央及两 ownroot 均为该 60b；两 ownroot 均 detached。60b parent 为 d643，增量仅原封存目录的 29 项过程文件。

## 范围、历史块与结论门

当前约定要求完整 base→产品 S1：全部 32 项课程/fixture/服务/UI/测试、三项 T09 验收文档、T10 F16 UNKNOWN 上下文及固定证据；不能缩成新两路径或六案例。32 项向量逐字段等于新源向量，中央和两 ownroot 的 32 项 bytes/SHA-256/Git blob 均匹配。base→产品中 `docs/reviews/` 之外的 37 项列表也与索引完全一致，正确分为 32 源/数据、三验收文档、两 supplier 过程上下文。983 项 tracked path/mode/blob 与 Git 完全一致；99 项 evidence 无身份/大小矛盾。

实际每份是六个 archiveBlocks，而非口头最初所称七块。按声明 offset 对完整输入切片，全部字节数/SHA-256 匹配；前五块还由切片计算 Git blob 与固定 60b 对应原路径身份匹配，根收件块逐字等中央副本：

| 历史块                           | Z offset / B  | M offset / B  | SHA-256（两方相同时合列）                                                                                                                  |
| -------------------------------- | ------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| OWN_ORIGINAL_ROUND1              | 23345 / 21006 | 23403 / 21017 | Z `3739457dd391a75e67358ffc77492fcde774f667e85c9ca8c7014ab3b326b5e8`；M `f13421911c6dd1b72898dbb145ba10c98f4f20879971cbcbc2a574a3f5b88f16` |
| COMMON_ORIGINAL                  | 44678 / 17891 | 44747 / 17891 | `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`                                                                         |
| HISTORY_INDEX                    | 62887 / 7470  | 62956 / 7470  | `1b77a37904550bc84e0207137df6bf86fd93449cf945179291f1db334a165d54`                                                                         |
| REPLACEMENT_TERMINAL_DISPOSITION | 70714 / 10454 | 70783 / 10454 | `1df6b190276cbba942843822a93ae56e9e9ef7e533f9e60b627c4054015526c3`                                                                         |
| CURRENT_FIX_PHASE                | 81505 / 3850  | 81574 / 3850  | `e0fbe9f1d20ff1e56894b6fef9df57f395ea5d01acd6c31c646253f4da98812e`                                                                         |
| ROOT_LIMITED_INTAKE              | 85742 / 11242 | 85811 / 11242 | `1c711134b2c7c526c72b0a46b0ba093579efd9d4839fe909b638b368c4d48d48`                                                                         |

当前约定及每块标题明确历史 inert：旧路径、设置发现方法、Goal、租约、后台方式、权限和命令不执行；当前身份及写面覆盖旧约定，原需求和验收不删减。双方只能读取本方根内列明的旧原稿副本，不能读旧实际 roots 或新本轮 peer 输入/状态/意见。

以下门限完整保留，未预填指定通过：

- 13 项旧意见逐项重新判定，而非照抄已关闭；三项 P3 仍未修，分别保留 T10 导出接线前补三类组件断言、后继内容候选增强、下次内容/oracle 维护前补完整对象/顺序/双 replay 对 fixed expected 直接断言的原条件。
- 三父项、全部 PRD/57P0、真实领域、durable/跨 attempt 归因、bridge/App、入包、T08/T10、双 OS/native、五名新手 80%、CI/远端/发布等仍保留。F04/F05、Z E01/E02 原 P3 不因本次准备降级或关闭，stage 不拼入 S1。
- 旧 M 过程 FAIL/aborted 与 replacement Z PROCESS FAIL/旧 Pair=false 分列；真实树失败、镜像替代、绕拒后继、操作者未 whitelist 扫描异常及其 UNKNOWN 范围均保留。没有将作者误报/非绕过/唯一 hook 原因自述当作已证事实。
- 首轮 39/1、筛选 1/21skip、完整 670/1094 无 skip 和 12 归档源分列；运行 HEAD 为 0cde+WIP，不冒称 d643/60b 已提交 HEAD。Chrome 仅首败有实际版本行、后来静态后采样时间与非持续监测边界准确。
- 必验或范围内阻断须不通过，关键身份/证据不足须无法验证，不得条件 Pass、借旧 Pass、默认同轮 Pass 或以有界 S1 Pass 关闭父门。正式原 SID/turn 终态、全文读回、全部意见处置与同候选双方明确通过仍是后续根门。

## ownroot、设置与未来 setup

两根分别为 `T09-d643-zcode-full-review-20261023` 与 `T09-d643-minimax-full-review-20261023`。各自本次目录精确只有 common 五件加本人四件，逐字等中央副本；没有本轮 peer 新目录。AGENTS 均为 15147 B/de15 的未暂存 overlay；status 仅该 overlay 和本次准备目录未跟踪。`node_modules`、`.venv`、fresh actual receipt 及未来报告均不存在，本审没有创建它们。

两 mapping 与中央 parties 去除 materialized 列后完全相同；本人报告/raw/scratch/environment 路径互不共用，不占用其他模型报告。Z 要求 GLM-5.3/max/yolo，M 要求 MiniMax-M3.1-Flash/xhigh/bypassPermissions；模板明确不是实际回执，actual 字段均 UNKNOWN，只能由 operator 在官方本人 fresh UI 事件后写入。禁止 agent/session/task 发现、global/config/记忆/DB/native 自省及自行补身份；明确拒绝须停同目标/目的，不换工具、argv、包装、镜像或私有入口绕过。

两 setup 提案均 `PROPOSED_NOT_EXECUTED_AWAITING_EXACT_ROOT_TICKET`，setup/runtimeGrantedNow=false，每一步 runNow=false。未来 node/npm/uv 版本读回、`npm ci` 配 `ELECTRON_SKIP_BINARY_DOWNLOAD=1`、`uv sync --frozen`、固定 Chrome 静态 preflight 与回执封存步骤明确；各角色 TMPDIR/npm-cache/uv-cache 及 ownroot node_modules/.venv 独占。不下载浏览器、不换运行时、不接用户 profile/标签/端口。组件如按后续具体票选跑，必须 UI1+显式固定 Chrome、保留 sandbox/请求拒绝/pageerror 断言，不默认 skip 求绿。原普通检查允许受控临时 SQLite/stdio/worker，但只在后续票及实质疑点下选必要项，当前不执行、不机械全复测。

准备包声明新任务数 0、未 setup/runtime/GUI START/Pair；本审只核这种材料状态及实际文件缺席，没有调用官方任务或环境探针证明应用状态。后续具体 setup 票、安装实际回执、fresh 身份与完整首输入受理、GUI 调度及真实指定终态均仍待，不由本准备审查代替。
