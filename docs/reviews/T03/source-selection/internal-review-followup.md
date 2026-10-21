# T03 来源选择子任务修复复核

2026-10-21（Asia/Shanghai）。首轮报告 `internal-review.md` 保留；本报告对应新的源码/测试候选，不沿用旧候选通过。

## 受审身份

- 树、分支及 base/HEAD 与首轮相同：`feature/weekly-t03-source-selection`，`5f910b52c69d86a1076b2032e5d3c63e715947f3`；实现/测试为未提交候选。
- `apps/desktop/src/main/mapping/source-selection.ts` SHA-256：`25a340ce7d8e0f2f3cdd4659c06c0a5ae3139cb3b44fde7812b1e782122f2fa3`。
- `tests/unit/t03-source-selection.test.ts` SHA-256：`c992984ece21c463f9ae55245996c1a63891bfac120fcb18962b509e9fad38c5`。
- 适用首轮已全文核验的 AGENTS/共同指令及无桌面打扰约束；未运行 GUI、Electron、e2e、native、HMR、外联或付费操作。

## 结论

首轮 P2 已关闭；本次完整读取来源选择实现及专项测试，未发现新的明确阻断。结论限于私有 broker，不替代指定双模型审查或后续正式集成验收。

有效 configure 现在入口即更新 generation 并撤销旧 proofs；选中来源暂留只供后发 configure 使用，配置期间 preview 返回 busy。旧请求成功/失败收尾必须匹配原 ticket，不能覆盖或撤销新请求；配置失败不恢复旧选项。cancel/pick/close/open/dispose 均会清理 configuring 状态和来源。

## 独立验证

- 实际运行 `npx vitest run tests/unit/t03-source-selection.test.ts`：29 passed。
- 在真实临时 CSV 上重复首轮无等待并发探针：先发 utf-8 返回 stale-context，后发 big5 fulfilled，旧 proof 返回 stale-proof。未修改受审源码/测试。
- 新测试覆盖 CSV/XLSX 后发配置、旧 proof 立即撤销、配置中 preview busy、configure 与 cancel/new pick 交错，以及两次真实读取占满资源槽时 configure busy 后不恢复旧来源。
- 原有 scope/proof 对象身份、源字节/哈希复验、资源上限、迟到 picker、同步 abort 重入及取消/项目生命周期测试仍全部通过。
- 开发线正在运行新候选全量 check；本报告未将运行中任务记为通过，也未重复全套。首轮全量日志只属于首轮候选。

## 未验边界

可信 host 注入 picker 与真实临时文件测试不等于原生文件对话框验收；本模块没有工作表解析、IPC/公共契约、引擎传输、Store 写入或正式 App 接线。原生 e2e、目标平台及完整父功能保持待验。本轮仅新增本报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
