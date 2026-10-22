# T04-S1 既有验证与历史意见处置索引

本索引是 2026-10-22 外审输入准备，不是新验证、指定任务、指定报告或父 Goal 恢复。固定 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，product `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`，准备前 process `e761d2962aa18c83885dde4cc0dcd15fd9aba322`。

## 当前候选对应的证据

所有相对路径相对于 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query`。

| 原件 | 适用范围与实际结果 | 不可替代的边界 |
| --- | --- | --- |
| `docs/reviews/T04/evidence/reader-service-verification.json` | 固定 554 最终 `npm run check` exit 0；TS 18 文件/666 项、Python 1083 项，lint/format/types/build/ruff 通过；相对批准基线新增 TS 36/Python 31 | 不是平台、真实执行或持久化联验 |
| 归档成员 `raw/check-reader-service-final.log` | 最终完整 check 原始输出，5276 字节，SHA `e65b5f2e5781b172a927d6161a25fd0ec301f5b45a7857108fa0a6d5cf13f772` | 不能用旧 640/642 TS 汇总替代 |
| `tests/unit/t04-query-reader.test.ts` 与对应原日志 | 24 个合成 transport 故障测试；代次、游标、排序、取消 ACK/真实终态及版本下限 | 没有真实 I05/IPC 请求 |
| `docs/iterations/T04/ssr-probe.mjs`、归档成员 `raw/reader-ssr-first.log` 和最终汇总 | 静态 SSR 14 项；423 字节，SHA `f730e85970c4fff87784f8d377da18f50da85de9487a4a0080fedc38a0f80874`；组件和探针从 `c3f771b1dbdbee18d53f629bd8c7dd79985b8883` 到 554 字节不变，按该范围继承 | 不验证浏览器事件、CSS/CSP、真实下载、原生或性能；旧 `ssr-review-fixes.log`/`ssr-save-identity.log` 是 11 项，不当最终 14 |
| `test_query_service_approved_baseline.py`、批准输入 provenance | 每次验证输入哈希；原/生成查询独立还原 G-base 都只返回 A01，A01 改 Closed 后空；显式语义错误 Closed/High 返回 A02，行数相同但完整答案错误 | 只是 RDFLib 编写互操作，不是正式 query.execute、规则/行为或 Store 运行 |
| `internal-review-8.md`，并完整读取 1–7 | 独立 Codex agent 对最终固定 554 完整范围复核通过，历史意见全部关闭 | 不是本轮指定 GLM/MiniMax 双审 |

本 S1 没有依赖、构建、锁、打包配置改动，未新增 package/native 验收。已有 build 不能证明 Windows/macOS 或实际安全存储通过。默认不重跑无变化产品测试；审查若发现需要新验证的具体疑点，应在报告列出触发、必要命令及未验边界，由开发线按实际授权安排。

## 原件恢复与版本归属

- `docs/reviews/T04/evidence/raw-logs-554ec89.tar.gz`：6081 字节，SHA `c17c2595d79900c539e4a0aa61bc1ad012e058af9e666282aa9c1f6079064865`。全部 37 原日志/61602 原始字节，包括首次失败、空日志和相同内容的不同文件名。
- `raw-logs-554ec89.index.json`：SHA `6d369a87a25fa5db8e88307e7032827f95778b8ba4415ee4b5371432af5dc811`，每成员大小/哈希和三份原汇总的固定 Git 来源；恢复说明 `raw-logs-recovery.md`。开发线和总控均已从 Git blob 完整读回，R1 实际关闭。
- 旧 `verification-summary.json` 是 `4c17a38195982164cf01541fd212c385e558ac7e` 的 640 TS/1080 Python/SSR8；旧 `final-verification.json` 是 `c4aa5f9c7508d8f439b547ff13f9334906e74744` 的 642 TS/1082 Python/SSR11。原件保留，不改写为 554 的结果。
- `reader-service-verification.json` SHA `ad4ddc21947462c6c4168a43448290fc5ad959e08e43b00254ed4adc2d0e1aac` 是最终 554 的终态依据。历史 internal-review 文件中“check 终态待开发线另记”按此后实际终态解释，不删历史文字。

## 历史意见及逐项关闭

每方必须完整读取原报告并独立复核修复，以下是导航，不能替代源码或原报告，也不能把旧内审通过自动改为本轮指定通过。

| 项目 | 原问题/原审查状态 | 已实施处置 | 实际独立关闭证据 |
| --- | --- | --- | --- |
| R1-01 | review-1：P2，复用保存丢失 definitionId；review-2：新建成功不返回 ID，第二次仍新建 | 私有 SavedQuery 带 ID；回调返回真实持久 ID，校验更新 ID 一致；request/document generation 隔离迟到，编辑 revision 保留未保存提示 | review-3 通过，6 项纯内存状态探针；review-4/5/7/8 继续完整复核 |
| R1-02 | review-1：P2，同项目非 query 任务被显示并可取消 | 使用批准 job validator，限定 active project + query.execute；当前 job 与结果不同持续标此前结果 | review-2 关闭；review-3/4/5/7/8 保持 |
| R5-01 | review-5：P2，ACK 后重读尚未完成就释放 cancelBusy，重复 cancel | 等待 refreshJob 完整生命周期，延迟重读反例 | review-6 关闭；review-7/8 保持 |
| R5-02 | review-5：P2，空页丢失最后非空排序锚，10→空→5 被接纳 | 仅保留 ordinal/rowId 有界锚，空页不清，新绑定/释放清理 | review-6 关闭，倒退/前进探针；review-7/8 保持 |
| R5-03 | review-5：P2，ACK version 下限在随后刷新/通知/取消前查中丢失 | 私有当前 job 版本下限跨路径保留；新绑定/job 正确清理 | review-6 关闭；review-7/8 保持 |
| R5-04 | review-5：P3，trim 改写实际 SPARQL 原文 | trim 只用于非空检查，输出保留原字符串 | review-6 关闭；review-7/8 保持 |
| R6-01 | review-6：新增 P2，INVALID_REQUEST params={} 不符合批准枚举，降成 internal | identity/params/cursor 归类并带 params.field；原始 bridge 异常固定 internal，不泄漏 | review-7 通过，4 项独立错误探针；review-8 保持 |
| 同版本/终态边界 | 开发线额外发现并修复；未假称审查原始发现 | 同版本状态矛盾、已观察终态重开拒绝；不以相邻状态转换限制合法跳跃观测 | review-6 独立探针复核，review-7/8 保持 |
| 同数量错义反例 | review-7 通过后依登记新增，不能冒充原候选已覆盖 | 固定 G-base 正确 A01 与错误 A02 都 1 行，检查完整答案 | review-8 固定 554 独立读/运行 3 项通过；最终 check 覆盖 |
| 总控 R1 原件可恢复性 | 首份总控审计发现 37 raw 仅 ignored，不能只保 hash | ae86 将原字节无损归档、索引和恢复说明纳入 Git，不改原日志/旧汇总 | 总控实际 Git blob 读回关闭；回执已记入 e761 的 status |

全部原报告路径：`docs/reviews/T04/internal-review-1.md` 至 `internal-review-8.md`。固定产品 554 含 1–7；review-8 为后追加流程证据，按输入清单固定其实际内容。没有本轮外审意见或外审结论可供引用。

## 完整父需求仍待验

FR-400–404、附录 C/D/G 的 Q-01/02/O-01、第 11–12 节及全部父 P0/跨模块门保持。真实 query.execute、项目内只读与外联拒绝、真实分页/取消/游标/历史、T01 preview/confirm/commit/保存恢复/撤销/过期、T08 模型草稿/工具闭环、真实 ASK/RDF 类型/执行文本与适用关系图、App、T10 跨设备和目标平台/真人/发布均未由本 S1 或本提示证明。指定审查、push/PR/实际 CI/正常 merge/远端也尚未完成。
