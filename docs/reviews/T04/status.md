# T04 查询状态

2026-10-21；owner/chat `01a15bcd-fcba-7583-a307-56497cdde347`。**独立实现已验证、独立内审通过；正式集成与原父功能尚未完成。Goal 保持 active。**

## 身份与恢复

- worktree：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query`
- branch：`feature/weekly-t04-query`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 通过内审/验证的实现候选：`c4aa5f9c7508d8f439b547ff13f9334906e74744`；之后仅追加流程证据。
- 启动时 HEAD=base，仅保护 AGENTS.md 未暂存，初始指南 SHA `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。总控追加权限政策后实际 SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；仍不暂存/提交 AGENTS。
- 实际独立 agent `/root/t04_private_review` 已完成固定候选审查。首两次不通过、逐项处置及最终通过见 internal-review-1/2/3/4.md，不替代指定外审。

独占新增仅 query_service/、test_query_service_*.py、renderer/src/query/、t04-*.test.ts、fixtures/query/、docs/{reviews,iterations}/T04/。未改共享契约、App/main/preload、Store/worker、锁/CI、总控 tasks/state；未消费未批准实现。

## 实现与验证

离线模板、对象/字段/条件构建、SPARQL 草稿与严格 RDF 项序列化；独立查询页面、显式当前/历史输入、范围/快照/实际查询显示、分页身份/表格/空结果方向/当前页 CSV；私有保存意图及真实保存 ID 回填，异步切换隔离。无真实执行器或第二存储，未接线时执行/保存禁用，无假结果。

- `npm run check` 最终 exit 0：TS 17 文件/642 项、Python 1082 项（新增 30 项），lint/format/typecheck/build/ruff 全部通过；原日志 `evidence/check-fixed-baseline.log`（本地 ignored）。
- 定向 TS 12 项通过；无窗口静态 SSR 11 项通过。独立 agent 的事件/状态探针另 6 项通过；这些不表示浏览器交互/CSP/下载/原生运行通过。
- 总控批准 T09 固定 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 输入。manifest `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`；17 项与 PRD 来源哈希全核验，选择的原字节保留。原始/生成查询各自独立还原 G-base，完整结果仅 A01；Closed 后均空。仅 RDFLib 编写互操作，未用 expected 预填 Store，不计 I05 联验。
- 原始首失败/后续修复日志保留；摘要与哈希见 evidence/verification-summary.json 和 final-verification.json。`git diff --check` 通过。

## 准确待验与下一交付

精确路径、字段、成功/失败和责任交接见 [integration-handoff.md](../../iterations/T04/integration-handoff.md)，逐 FR 命令/边界见 [acceptance.md](../../iterations/T04/acceptance.md)。

1. T00/I05：批准业务命名 draft→query.execute 接线，列/RDF term/ASK/实际执行文本元数据；真实项目/快照/推导身份、分页 cursor/任务时限/取消/只读与外联拒绝。当前 approved base 中 query.execute 仍 design-only。
2. T01：唯一 preview/confirm/commit、保存/读取/撤销/恢复与过期；保存成功返回真实 definitionId。无 renderer 发行 ID 或本地第二源真相。
3. T08 自然语言真实草稿/工具闭环、T09 真实完整案例、T10 保存查询迁移、适用局部关系图仍待共同接口；原 FR-400–404、C/D/G、11–12 和全部父 P0/跨模块验收保留。
4. 正式同版集成后刷新实际 develop 并重验；预约 ZCode GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh 各新完整任务、读回/全部处置/双方明确通过后才 push/PR（attach）；实际 CI 通过后正常合并/远端核验。**当前未指定双外审、未 push/PR/CI/合并、未上线。**

## 已接收操作政策

已实际全文读取第九节与无桌面段，并透传独立 agent：第九节 SHA `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`，无桌面段 `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d`；补发共同指令 `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`。后续权限政策共同指令 SHA `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4` 及 external-review-permissions.md 亦已全文读取/透传，agent 实际回执核验。

ZCode 默认 yolo、MiniMax 默认 bypassPermissions，仍需每个实际任务读回；只读审查、指定模型与无桌面限制不变。不重建 Goal/历史输入，不因纯操作政策重测。本线未遇额度告警、未消费重置/新增付费、未读取输出 secret、未调用模型/外发业务数据、未运行 GUI/Electron/e2e/native/HMR/凭据提示。Codex 每次兑换仍须本人该次确认/阈值/幂等/读回；审查资源由总控预约，平台证据不能由 CLI 代替。
