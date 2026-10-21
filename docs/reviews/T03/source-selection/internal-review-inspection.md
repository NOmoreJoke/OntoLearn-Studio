# T03 来源检查字节入口独立内审

2026-10-21（Asia/Shanghai）。新候选独立复核，不沿用先前 29 项版本通过。

## 受审身份与规则

- 树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection`；分支 `feature/weekly-t03-source-selection`。
- HEAD：`2f7a4daf7cd32408b4ea6e87b93f3298c0c2569e`；本次源码及测试仍有未提交增量。
- `source-selection.ts` SHA-256：`700337e055974708fe848edf58187fe161c2af2a0feb908bd41241abfea9e989`。
- `t03-source-selection.test.ts` SHA-256：`734ec4fb10ac617a5c5659b40f9366ae35838eacd820539d759bc432a6ef247e`。
- 已重新核对规则文件哈希：AGENTS `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`；共同指令 `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`，与首轮全文读取版本相同。完整第九节、只读和无桌面打扰约束继续适用。

## 结论：本次私有实现内审通过，无新增明确阻断

完整读取当前来源选择实现并复核本次测试增量，旧 P2 保持关闭：有效 configure 入口撤销 proofs/旧代次，后发配置优先，配置期间检查或预览返回 busy，晚到旧请求不能覆盖或撤销新选择。

`readForInspection` 只提供已由可信 picker 选中来源的检查字节，不是预览或提交权限：

- 入口复用 `current` 检查 scope 对象身份、selectionId 和 configuring 状态；没有新增任意文件路径参数。
- 复用 `readVerified` 的两槽限制、有界真实文件读取和字节 SHA 复验；读取返回后再次检查 generation，取消/配置/项目生命周期变化不能返回迟到检查结果。
- 返回独立字节副本及冻结摘要，不登记 WeakMap proof；把 inspection 对象冒充 proof 仍被 readForCommit 拒绝。
- XLSX 的 sheet=null 仅可读取检查字节；readForPreview 仍要求显式工作表。未增加 parser、IPC、transport、Store 写入或网络调用。
- 同长度源文件变化在 inspection 复验中被拒绝并撤销已有 proofs；恢复原字节不能恢复旧 proof。

## 验证与边界

- 独立实际运行 `npx vitest run tests/unit/t03-source-selection.test.ts`：32 passed。
- `git diff --check` 无问题。
- 新增三项测试覆盖无 proof/副本、配置期间 busy/迟到/旧 selection、同长度变更及旧 proof 永久失效；既有生命周期、并发配置、abort 重入、文件限制及安全错误测试同时通过。
- 测试使用真实临时文件系统；`.xlsx` 文件内容是明确标注的未验证候选字节，不能据此宣称真实工作簿解析、工作表枚举或与 Python `xlsx_sheets` 接线通过。
- 新候选全量 check 在本轮日志读取时仍运行中，未在本报告记为通过，未重复执行全套。

未验范围保持：原生 picker、实际工作表枚举/解析联验、公共契约/IPC、引擎传输、Store 事务、正式 App、原生 e2e 和目标平台。此次内审不替代指定双新外审。未运行 GUI/Electron/e2e/native/HMR、凭据或付费/外发操作，未提交、推送、切分支或修改实现/测试/依赖/配置；仅新增本报告。
