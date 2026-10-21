# T03 来源选择独立子树状态

2026-10-21（Asia/Shanghai）。Owner：原T03聊天 `01a15bcd-f838-75a2-b2c3-692915cc91c3`；原Goal继续active，不新建Goal。

- 实际工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection`，分支 `feature/weekly-t03-source-selection`，批准base及创建时head `5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 总控已明确批准新 `apps/desktop/src/main/mapping/` 唯一owner为原T03；配套仅 `tests/unit/t03-source-*.test.ts` 与T03私有docs。S1原树303候选source/tests/依赖/验收不改。
- 保护AGENTS携当前78df SHA、共同指令实际b24 SHA；未stage指南。环境独立，不复用S1可变node_modules/.venv/build。
- 已实现私有 `SourceSelectionBroker`：可信host选择回调、真实有界FS读取/hash、不透明句柄、安全元数据；项目/lifecycle/generation/编码/sheet绑定及重读指纹/源变拒绝；重选/取消/关闭/迟到、同步abort重入与受限内部错误。最多两个实际未终态操作，abort不提前释放槽位。
- 不新增公共契约/IPC/SQLite/写通道/网络。正式native dialog、canonical source运输、bridge/App和Job确认/提交仍待对应owner及实际联验；注入picker单测不是原生GUI通过。
- 历史29项候选运行验证：29项 `t03-source-selection` 专项通过（真实临时文件读取/hash、同长变更、删除/重建、超限、FIFO、旧证明、重入/迟到/并发上限，编码与sheet并发后发优先、配置期间证明失效/preview busy及cancel/new pick）。修复后 `npm run check` 完整通过：659 TS + 1052 Python、零skip，包含lint/格式/类型/构建；日志 `check-config-concurrency.txt`。
- 独立内审：[首轮](internal-review.md)发现并发配置先完成者生效P2；已按后发有效请求优先修复，[完整复核](internal-review-followup.md)关闭P2且未发现新增阻断，独立运行29项通过。复核时完整check尚未终态，此后开发线读取exit0及659/1052通过；不得把该终态归为独立agent重复执行。
- 历史保留：首次check因测试prefer-const失败，修复后24项候选check为654 TS + 1052 Python；21/22/24项中间专项日志及首次失败均保留，属于对应旧候选。29项阶段原始文本总量不足16KiB，因尚无获准push/CI artifact，为审查可读回首跑失败与实际命令终态而暂存入本私有证据目录；后续由实际CI承接。
- 29项为可信picker注入测试，XLSX测试只验证选择/字节与sheet状态，不冒充真实工作簿解析。
- 设计及T01/I06交接：[design-and-handoff](../../../iterations/T03/source-selection/design-and-handoff.md)。主进程实际e2e/新模块正式接线在隔离环境待验，不在本机开Electron/e2e/HMR/native窗口。此子树未做打包或平台验收，无S1证据继承。

历史29项产品可恢复提交 `f2c7deb8139255bc11e44c5b4a958ecbdae6a373`（流程2f7）；其源码/测试SHA与当轮独立复核报告一致，已被下述检查入口候选替代。尚未push/PR/CI/合并。

## 选表前检查入口增量（当前候选）

已发现并补齐选表前真实枚举所需的main-only `readForInspection`：复用同一有界FS/源指纹与生命周期规则，只返回bytes/summary，不生成preview/commit proof，不放宽XLSX显式选表要求。新增3项实际临时文件回归，专项32项通过；新候选完整check exit0（662 TS / 1052 Python，零skip；`check-inspection.txt`）；[独立完整复核](internal-review-inspection.md)通过、独立32项专项通过，旧P2仍关闭。独立报告未读取全check终态，该终态由开发线此后读取。29项版本f2c/2f7保留为历史，不把其通过沿用于新候选。原S1冻结不改，尚无正式解析/IPC/Job接线。

当前检查入口产品提交 `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`，源码与测试hash均与本轮独立报告及git对象逐一一致。总控已核验旧f2c/2f7历史候选（readback SHA3354ca6…）；该核验不覆盖本次新入口。现等待总控读回新候选并协调T01/I06正式契约、隔离联验和指定双审资源。原Goal持续active，未push/PR/CI/merge。

总控派出的独立 inspection 增量审计已实际终态（turn `01a15c2b-0ff5-7ff0-a89f-f66f9af1b44a`），开发线全文读回报告 `T03-controller-source-inspection-delta-readback.md`，SHA `5538099b1895124bcafd9e9a5d37528b67cfc24e5809949fb2c3803f0f58a92b`。固定8c/b868字节与10raw对应，有界通过且无新增阻断；没有运行新测试。该报告不授公共接口消费/协议批准，也不替指定双审或正式联验。实际等待用同一live任务句柄续接至终态，不把一般资源排队当在跑任务。

## 当前Goal：blocked

已通过Goal工具实际标记blocked，完整原目标不变。相同外部条件连续三轮仍未满足：总控已全文读本次审计，但 `approvedForConsumption=false`，T01/I06唯一来源运输/确认/Job正式接口及接线依赖未就绪；指定双审仍无合规隔离入口/可用桌面时段与真实任务句柄。独立审计已终态，不再把它当运行中等待。现有授权内准备、代码、必要检查、内审和可恢复原件均已完成；需要实际依赖/资源状态变化才能继续。两树仅保护AGENTS未暂存；未push/PR/CI/merge，保留所有父功能/目标平台验收。待总控提供精确获批接线条件或合规外审资源后续接，不重复提出已pending的桌面问题。

## T01 r1设计交接（不恢复Goal）

按总控新消息全文核对T01固定f51dd38的§2及原件SHA0f3ab7…，保存 [精确设计答复](../../../iterations/T03/source-selection/t01-interface-response-r1.md) 与 [独立复核](t01-interface-response-r1-review.md)。接受唯一有界JSONL的64KiB原字节分块/seal方向；六个待冻结合同是完整帧/小帧预算、configure新代次引用、完整表及选项摘要、typed来源与总预算/pin回收、worker所有权及确认前只读执行/大结果、复验到最终确认提交的生命周期。复核的一项P3确认语义已关闭；seal完整性不等于人类写确认。仅文档/静态来源读回/格式检查，未运行新runtime测试或采用未批准代码，broker/source测试字节未改。原Goal仍blocked，公共schema/消费/接线尚未生效。
