# I05 triage R1 补充：M06 未应用提案

结论：该精确补丁的静态意图与最小防御范围合理，可作为等待根源文件范围交接后的候选修改提案；不构成已应用修复、回归通过或产品验收。没有新增阻断意见。

窄读 `m06-unapplied-proposal.patch`（1258B / e06a73161d258f063e53aea9f1686c8ab9d5b6844c2347512e9cec8201a8b840）与其 JSON。独立解析新增 guard 与测试语法，未读额外产品源码，未应用 patch。

- `_scope_observation` 的 `counter is None` 检查置于 modules/dataset 查找及 canonical 调用之前，以 `ProbeFault("INTERNAL_ERROR")` 拒绝缺失 instrumentation；没有业务成功替身、新公开错误码、fallback counter 或放行分支。正常 non-None 路径在 diff 层面保持原序。
- 空 modules/dataset 输入要求准确 ProbeFault 与 INTERNAL_ERROR，能够暴露原先抢先 KeyError 的反例，并约束失败发生在真实业务输入访问之前；这个负例有意义。它不替代合法 full-v1/B1/canonical 回归。
- 这是 patch-only 检查；新增代码片段可被 AST 解析，不表示完整拟源码/fixture/ProbeFault 构造及调用者行为已由本审查复核。既有安全错误出口的实际签名、完整拟文本 hash 与合法路径回归仍需获授权后核对，不由本补充假称通过。

六个固定输入不变，未重跑已经通过的 checker。没有执行 pytest、import、产品、安装、构建或运行。独立有限 proof 见 `independent-triage-r1-m06-proof.json`。
