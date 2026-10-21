# T04 查询状态

2026-10-21；owner：本聊天 `01a15bcd-fcba-7583-a307-56497cdde347`。

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-query`
- 分支：`feature/weekly-t04-query`
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 启动实查：HEAD=base；仅保护 AGENTS.md 未暂存；指南 SHA-256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`。
- Goal 已建立。当前阶段：独立实现进行中；未正式接线、未外审、未 push/PR/合并，父功能 FR-400–404 与完整发布验收保留。

独占新增：`packages/engine/src/ontolearn_engine/query_service/`、`packages/engine/tests/test_query_service_*.py`、`apps/desktop/src/renderer/src/query/`、`tests/unit/t04-*.test.ts`、`tests/fixtures/query/`、`docs/reviews/T04/`、`docs/iterations/T04/`。不改共享文件、根状态或任务。

下一交付：安全 RDF 项/可视条件编译、离线模板与 SPARQL 草稿、独立查询页面、分页结果身份/空结果解释、保存意图与必要边界测试；独立只读内审。正式执行只消费批准 I05 query.execute；项目保存只经 T01 事务，不新增可变源或假执行器。

验证：专属 pytest/vitest、`npm run check`；当前尚未运行。仅无窗口 CLI，不运行本机 Electron/e2e/native/HMR/凭据提示。外审 ZCode/MiniMax 资源由总控预约；指定同候选双新审、push/PR/CI/正常合并与远端核验均待实施。

已实际接收总控补发的第九节全文与无桌面段全文；未重建 Goal 或改写历史输入。第九节 SHA-256 `1f57a08e909e9d49a6e2c2d6e7012beec3e22b8e3c9e8eacad22c84dfb2d4b54`；无桌面段 `5215df2ead4745e7d74f137c4fa6ac837a54114590b5dee2d83cd16bb728551d`；共同指令补发 SHA `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`。本线未出现实际额度告警、未查询凭据/消费重置/新增付费，未运行 GUI。额度告警由唯一负责人核实；Codex 每次兑换仍需本人该次确认，阈值/幂等/读回要求保留。

本地恢复提交：`4c17a38195982164cf01541fd212c385e558ac7e`。对应完整 `npm run check` 已终态通过：TS 17 文件/640 项、Python 1080 项，lint/format/types/build/ruff 通过；原始失败与最终日志保留本线 ignored evidence，哈希在 verification-summary.json。内审 1 的实际终态不通过（两项 P2），已按 internal-review-1.md 修复保存定义身份、任务能力限定和旧结果标识，正在运行修复版 check 与独立复核。修复版定向 TS 12 项、静态 SSR 11 项已通过；未替代正式接线/父验收/指定双外审。

操作政策补充已实际读取 AGENTS 追加段及 external-review-permissions.md 全文：保护指南 SHA 现为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，共同指令透传 SHA `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`。ZCode 默认 yolo，MiniMax 默认 bypassPermissions；仍需实际任务读回，审查只读、无桌面/密钥/付费限制不变。未因政策重启 Goal 或重跑产品测试，AGENTS 保持未暂存，旧字节由总控保留。
