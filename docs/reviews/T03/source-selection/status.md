# T03 来源选择独立子树状态

2026-10-21（Asia/Shanghai）。Owner：原T03聊天 `01a15bcd-f838-75a2-b2c3-692915cc91c3`；原Goal继续active，不新建Goal。

- 实际工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection`，分支 `feature/weekly-t03-source-selection`，批准base及创建时head `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 总控已明确批准新 `apps/desktop/src/main/mapping/` 唯一owner为原T03；配套仅 `tests/unit/t03-source-*.test.ts` 与T03私有docs。S1原树303候选source/tests/依赖/验收不改。
- 保护AGENTS携当前78df SHA、共同指令实际b24 SHA；未stage指南。环境独立，不复用S1可变node_modules/.venv/build。
- 已实现私有 `SourceSelectionBroker`：可信host选择回调、真实有界FS读取/hash、不透明句柄、安全元数据；项目/lifecycle/generation/编码/sheet绑定及重读指纹/源变拒绝；重选/取消/关闭/迟到、同步abort重入与受限内部错误。最多两个实际未终态操作，abort不提前释放槽位。
- 不新增公共契约/IPC/SQLite/写通道/网络。正式native dialog、canonical source运输、bridge/App和Job确认/提交仍待对应owner及实际联验；注入picker单测不是原生GUI通过。
- 当前运行验证：29项 `t03-source-selection` 专项通过（真实临时文件读取/hash、同长变更、删除/重建、超限、FIFO、旧证明、重入/迟到/并发上限，编码与sheet并发后发优先、配置期间证明失效/preview busy及cancel/new pick）。修复后 `npm run check` 完整通过：659 TS + 1052 Python、零skip，包含lint/格式/类型/构建；日志 `check-config-concurrency.txt`。
- 独立内审：[首轮](internal-review.md)发现并发配置先完成者生效P2；已按后发有效请求优先修复，[完整复核](internal-review-followup.md)关闭P2且未发现新增阻断，独立运行29项通过。复核时完整check尚未终态，此后开发线读取exit0及659/1052通过；不得把该终态归为独立agent重复执行。
- 历史保留：首次check因测试prefer-const失败，修复后24项候选check为654 TS + 1052 Python；21/22/24项中间专项日志及首次失败均保留，属于对应旧候选。原始文本总量不足16KiB，因尚无获准push/CI artifact，为审查可读回首跑失败与实际命令终态而暂存入本私有证据目录；后续由实际CI承接。
- 29项为可信picker注入测试，XLSX测试只验证选择/字节与sheet状态，不冒充真实工作簿解析。
- 设计及T01/I06交接：[design-and-handoff](../../../iterations/T03/source-selection/design-and-handoff.md)。主进程实际e2e/新模块正式接线在隔离环境待验，不在本机开Electron/e2e/HMR/native窗口。此子树未做打包或平台验收，无S1证据继承。

产品可恢复提交 `f2c7deb8139255bc11e44c5b4a958ecbdae6a373`；源码/测试SHA与独立复核报告一致。当前尚未push/PR/CI/合并，待总控登记及后续指定双审和接线资源。
