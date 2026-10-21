# 格式 3：I06 八文件未来维护交接回执

2026-10-21。I06 选择释放八文件的未来维护，不在当前网关候选中代实施格式 3。八文件均 clean，且从 `9fcba663` 到 ARIA 产品修正 `e2c269ad` 内容未变；当前无正在修改这些路径的任务，也无在途指定外部冻结审查。I06 从本回执起停止这八文件的后续逻辑修改，待总控登记及 T01 接收逐项 ack 后转由 T01 唯一维护；不必等待整个 I06 完成。总控登记接收的实际生效时点。

## 精确输入和范围

已全文读取总控最小请求 `iteration-control/2026-10-21-weekly-release/format3-minimal-integration-handoff-review.md`，SHA-256 `cfc001d99f41c080d79346413b6431218fbacd2382f62a282553c55e4b6c34e8`。逐文件批准 base、旧平台 source、ARIA source、当前 HEAD 与工作树 SHA-256/dirty 见 [机读回执](format3-maintenance-handoff.json)。批准 base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，取证 HEAD 为 `2775ef02222ee667ee4c0a20cafd32887d0a27c7`，分支 `feature/I06-model-gateway`。

释放清单：

1. `packages/contracts/src/index.ts`
2. `packages/contracts/src/v2.ts`
3. `packages/contracts/v2/schema.json`
4. `packages/contracts/v2/registry.json`
5. `packages/contracts/v2/errors.json`
6. `packages/contracts/v2/fixtures.json`
7. `packages/contracts/v2/binding-regressions.json`
8. `apps/desktop/src/main/engine.ts`

T01 在其独立批准 `5f910b52` 基础候选实施有限格式适配，不 cherry-pick 或复制本回执中的未批准网关实现。八文件的批准 base 与当前 I06 内容均不同；此处当前 SHA 用于保全及冲突定位，不是 T01 的依赖来源。原 I06 worktree/提交/平台原件全部保留原字节；所有权交接不改动这棵树。

其余六个既有 I06 共享文件（main/index、task-service、preload/index、renderer/env.d.ts、App.tsx、style.css）、既有测试、I05 Python、build/锁/CI/CSP/window 文件均不在此次释放内。新增 TS 跨端测试路径若有需要，另报精确路径及 owner 后登记。

## 实施与再集成边界

版本升级的小合同须包含 bootstrap outer2 / supported[3] / selected3、两处新 session 相等、实际同源 registryHash、三个新 null 失败及旧 [2] 有限终止、业务 3 精确绑定和有限启动诊断。I06 提供独立文档提案供接收 owner 冻结；当前未生成协议 3 canonical，不把测试 hash 写成真实 ready 证据。协议/SQL/Job-ready 仍须三方同版冻结和独立核对，交接本身不批准公共协议。

本次所有权/文档动作不需要改 ARIA 或重跑当前 e2c 回归；既有证据仅覆盖其原 source。T01 实际产品改动后，按实际 delta 完成全量检查、TS/Python 绑定同判、真实源码/包内闭环、故障诊断和原窗口恢复回归。首次 source native 超时及一次定向复验通过的历史仍保留，不被新交接消除。

未来 I06 引入实际批准格式 3 时，先对接收 owner 冻结的 base/head/逐 hash 和实际 develop 合并核验，协调唯一维护及冲突处理；未经返还或新的精确登记，I06 不自行恢复这八文件写权。合并必须保留 main-only 模型方法拒绝进入 Engine 的 guard 和网关严格绑定，不能用任何一方文件机械覆盖。T01 返还或再分配前须停止相关修改，交付 clean/dirty 清单、实际合同和验证证据。最终 I06 整候选联验、指定双审、PR/实际 CI/远端合并要求仍保留。
