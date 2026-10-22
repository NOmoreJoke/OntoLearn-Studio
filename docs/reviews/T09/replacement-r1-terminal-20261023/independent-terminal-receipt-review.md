# T09 replacement-r1 最终收件限定独立核查

**限定收件范围通过，未发现收件结构或意见登记缺陷。绝非 Pair Pass、代码复审或产品通过。** 作者各自的 bounded Pass、Z 的总控过程 FAIL 与 Pair Pass=false 已明确分列。

2026-10-23（Asia/Shanghai），独立 Codex 子 agent `t09_prd_audit`。仅读取本目录指定八文件，唯一新增本报告；没有跟随其中路径或执行文内命令，没有读取 native/global/数据库/源码/peer、运行 GUI/产品/环境试验或 cleanup，也未重取旧源/输入证明。

## 四份原件身份

实际逐字节计算结果与 terminal receipt 相符：

| 原件                              | bytes / 行数 | SHA-256                                                            |
| --------------------------------- | ------------ | ------------------------------------------------------------------ |
| zcode-original-report.md          | 19358 / 114  | `5540beb29ab89baf5c72fd9fc3a2fcc9df213c376ad392171c7a291a5b727f79` |
| minimax-original-report.md        | 49469 / 353  | `92cfb9d6433710303355fd7be6754026e54846f24c2853e46a41df2a0f9766b0` |
| zcode-original-run-receipt.json   | 5815 / 94    | `af96feacf642ae0fbb80bb4b50135028987d63ad0682d1bf9e15c8ef821c8f0d` |
| minimax-original-run-receipt.json | 6065 / 124   | `9e15046fdbe959300aa28b7e1a923d460c365bfb6232659db067c3d409ef86d4` |

四份原件未由本审查格式化、补值或修改。Z 的报告 Write ID、路径、19358B/hash 及公开成功返回在 proof 与 terminal receipt 中一致；Write 正文未在派生 proof 重复提供，本次不独立读取 native 重新证明其采集来源。

M binding 记录初次 Write 48944B / `36cdc187a20a3e06994d0fe91c5bb6f0178be73ae8ba47146fab15b1391bf2cc`，随后五次同一路径 Edit 均记录成功。仅利用本包内终稿及 old/new 字符串，在内存反向应用五 Edit 精确恢复该初稿 bytes/hash，再正向应用得到最终 49469B/hash；每个被替换串出现次数均为 1。该检查证明记录链内部一致，不等于重新读取初始 native Write，也不独立证明操作者采集过程；`expectedDiskBytesUsedToFillContent=false` 按其来源声明保留。

## 正式终态与 UNKNOWN

Z SID `session_1d54a3bdcdcb436f5693f8a1f6c41544` / 原 turn `turn_9bfca954-5f33-42c8-ac6a-c38344f8c7e0` 在 receipt/proof 中一致，记录官方 `turn.completed` 为 `2026-10-22T21:21:46.823Z`。

M SID `mvs_4a0e67fa3d5949eb910022a5c96822fb` / 原 turn `12d877f3-1c57-46bb-ad32-a609bc2a0ba3` 一致，四列原 turn 行为 completed。`1792704167996` 对应 rowUpdatedUTC `2026-10-22T21:22:47.996Z`，材料明确它是表更新时间，不另造精确 completion event。

M 原稿早期 sessionId/turn/受理/SID菜单/草稿字段 UNKNOWN 与“未回填”表述原样保留，后继收据按时点和来源分列，没有替作者改写成已读取后来事实。Z 原稿的 UNKNOWN 及其后“证据齐备”等作者表述也未被本审查纠正或背书。正式终态绑定是操作员收件记录，不倒灌为作者当时已知事实。

## 意见与过程失败

两作者判关闭的 13 旧项均完整登记：CONTENT-01–05、INFRA-01、UI-01–05、DOC-01/02。三项既有 P3（M F-01/02/03）两方均接受延期，但未修、未关闭：导出三类断言仍须 T10 接线验收前补齐；提示区分度留后继内容候选；oracle 自动断言须相关内容/oracle 下次维护前补完整对象、顺序和双 replay 的直接比较。

PARENT-01/02/03 和领域、durable/跨 attempt、bridge/App、资源入包、T08/T10、平台/native/包、真人及 80% 原口径、CI/远端/发布/57P0 门均保留。没有用新收件关闭父门或拼入 N0/stage。

四个新增意见也已全部登记待总控决定：Z E-01/E-02 的环境/归因与清理建议未执行；M F-04 的合法 recordVersion=0 哨兵冲突、F-05 的历史验证摘要阶段标记缺失未独立复现、修复、升降级或自行认作可延期。M F-01–03 没有重复计入新增问题。

Z proof 保留明确拒绝、改工具/改同目标 argv 的后继及越写面全局记忆 Read/Edit 输入，过程结论 FAIL 不被作者的“误报”“非包装绕过”自述豁免。全局部分只含调用 ID/名称/路径及状态说明，没有 Read 返回正文、Edit old/new 实际内容或目标文件内容；实际全局读取执行/写入成功均保持 UNKNOWN。

真实树 verify=1、pytest 38 failed/4 passed 与后继 scratch HEAD 镜像 verify=0、pytest 42 passed 的替代关系未被合并美化。环境/hook 唯一因果及“非产品缺陷”仅属作者判断，材料明确总控未采为已证事实，镜像和清理未因此补票。作者 bounded Pass 完整保留，但不能抵消 Z 过程 FAIL 或形成同轮双审通过。

## 操作者早期扫描异常

当前 proof 明确记录：早期拒绝关键词扫描先遍历 `result.value` 字符串并匹配关键词，再限制调用 ID，未预先白名单，可能处理越界 global 返回字符串。两 known global input ID、既有 chat 工具输入代码范围及 UNKNOWN 曝光程度已列，不能说“从未处理返回”或“零曝光”。没有因本审查补读任何返回或目标文件。

精确扫描调用时间为 UNKNOWN；`21:22:13.412416Z—21:24:47.983209Z` 仅由既有 status 快照夹定的顺序窗口，不是精确时刻。`21:20:12.768Z` 是后来纠正提取所用的 native request 截断位置，不能覆盖早期异常或冒作操作者扫描时间。最终白名单提取和不再调查 global 返回/文件的范围与这些限制相容。

## 运行证据强度

两份 run receipt 只是作者原始产物，不是操作者或本审查的新运行。Z 的五组 returncode 声明为 1/0/1/0/0，保留真实树失败、镜像替代及 18 passed/16 skipped；其占位 argv/相对路径、部分逐流摘要缺失未被补齐。M runnerExit 与四个 child returncode 分列，后者均为 0，并列 stdout/stderr 路径/bytes/hash；本次没有跟随验证这些 raw 路径，也没有把 native 完成状态当独立整数 exit 字段。

两侧浏览器组件均为本轮 skip，不冒充实跑；缺 1248 的历史 exit1、未重跑全量 check/安装浏览器、领域/native/双 OS/真人/生产未验均保留。Z 关键抽查和 gzip 摘要核验、M 解压原件等不同覆盖强度没有拼成一份更强证明。操作者未做新源、产品、环境或 GUI 验证的边界按原收据保留。

本报告只核本包字节、重建链自洽和意见/来源登记。后续严重度、过程失效的调度及父验收仍由总控裁定；本轮 Pair Pass 为 false。
