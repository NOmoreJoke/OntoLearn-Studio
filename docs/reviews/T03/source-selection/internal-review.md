# T03 来源选择子任务独立内审

2026-10-21（Asia/Shanghai）。只读实现与测试；不沿用 T03-S1 通过结论，不替代指定双模型外审。

## 受审身份与规则

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection`；分支 `feature/weekly-t03-source-selection`。
- base/HEAD：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；实现与测试为未提交候选。
- `source-selection.ts` SHA-256：`bf4ef7a1eeb74090d067b283fa140cd26c1441f5e3f18d4c1af77d332b8f1b28`。
- `t03-source-selection.test.ts` SHA-256：`406567e2ef8100f312aa6e9522a3b11b8a54d494e5cbcfd90f9c799fc44c5891`。
- 已全文读取并核对 AGENTS：`78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；共同指令：`b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，遵守完整第九节、只读及无桌面打扰规则。
- 需求依据：FR-300–304；本轮重点是可信来源选择与旧上下文拒绝，不是完整映射业务验收。

## 结论：存在一项 P2，待修复复核

### P2：并发 configure 由先完成者生效，后发配置可被旧请求抢先淘汰

位置：`apps/desktop/src/main/mapping/source-selection.ts:185–190`。

两次 `configure` 都在相同 generation 下开始异步文件复验，直到某次读取完成后才 invalidate。因此先发请求先完成时会使最新请求报 `stale-context`，并把先发的编码/工作表保留为当前值。它与 `pick` 的后发有效请求优先策略不一致，现有专项测试未覆盖并发配置。

实际证据：在真实临时 CSV 文件上顺序发起 `configure(...encoding='utf-8')` 与 `configure(...encoding='big5')`，再 `Promise.allSettled`，得到前者 fulfilled（utf-8）、后者 rejected（stale-context）。探针以 TypeScript ES2022 编译当前源码，在 Node 24 中运行；仅创建/清理本任务临时文件，未修改受审文件。

建议：明确配置并发策略。可以在有效配置请求开始时建立新代次，让晚到的旧配置和旧 proof 失效；或在入口对重叠配置明确拒绝 busy 并记录串行约束，避免异步完成时争抢。补充编码和工作表并发、配置期间旧 proof、取消/新 pick 交错的回归。

## 验证与已确认边界

- 独立执行 `npx vitest run tests/unit/t03-source-selection.test.ts`：24 passed。
- 已读取 `check-second.txt`：654 项 TS、1052 项 Python 测试通过；未重复全套。首跑失败原件保留。
- 实际文件字节和 SHA、等长修改复验、删除/增长、目录/FIFO拒绝、固定错误、opaque scope/proof 对象身份、项目关闭/切换/重开、取消与 dispose、迟到 picker、abort 重入、两槽并发限制有对应测试。
- 文件路径仅来自可信 host picker，未接受 renderer 路径；摘要不含路径。读前/读后 fstat 与字节数受限，正式读取重新核对 SHA；返回字节为独立副本，proof 为主进程对象身份。
- 不含原生 picker、真实 XLSX 工作表枚举/解析、IPC/公共契约、引擎传输、Store 写入、正式 App 接线、原生窗口/e2e 或目标平台验收。注入 picker 的真实临时文件单测不能证明这些项通过。

本轮未运行 GUI、Electron、e2e、native、HMR、外联或付费操作；未提交、推送、切分支或修改实现/测试/依赖/配置。仅新增本报告。
