# T07 → T01：轮次投影与提交对账固定提案

此文与 `tests/fixtures/scenario/round-projection-handoff.json` 为私有业务适配提案，不是第二公共schema，也不是正式scenario接线通过。样例由已验证私有runner实际输出生成，推理/行为明确为合成端口；无expected预填Store、无新增产品写入通道。样例用例会核对完整Round及摘要，防止交接材料漂移。

现已生效的JobStore唯一owner为T01，依据总控 `I05-T01-format3-ownership-handoff.md`；本线只修改授权私有文档/fixture/test，四共享Python文件不改。默认2/显式内部3及公共合同批准门保留。

## 已生成的完整形状

样例包含完整 `internalRound`，对应 `dataclasses.asdict(Round)` 的JSON规范化值，不省略状态：

- checkpoint：定义摘要、轮号、完整场景state（工单/告警/assertions、历史创建身份和递增序号）、完整事件目录和payload、consumed与completed身份。
- 输入事件、当轮创建/资源完成/积压集合、三项指标。
- 行为前与轮末推理的输入state、规则版本、snapshot和Context（round/phase）。
- 逐动作三元轨迹(eventId/behaviorId/actionIndex)及冻结计划JSON。

完整Definition/初始快照、输入/规则/行为内容与版本、引擎/锁/执行语义还需随runConfig固定；Round不能单独证明可重放。

## 给coordinator的状态投影提案

样例 `proposedCoordinatorState` 保留整个 `scenarioRound`，同时投影已有消费者需要的 `inputEvents`、`consumedEvents`、`pendingEvents`。身份与payload摘要必须与同一job/run/输入版本绑定，由唯一owner最后确定字段和严格校验。

注意两个不同范围：

1. 终态“未处理事件”必须包含所有已知未消费事件，包括超过max仍配置在未来轮次的事件。样例的coordinator `pendingEvents`为此全集。
2. 批准T09 E.5的 `expected.pendingEvents`是已注入待处理队列，不含另列的`scheduledFutureEvents`。逐轮基线比较必须分别核对，不把上面的全集直接和此子集比，也不能在达到max时丢掉未来事件。

样例显式给出scheduledFuture与generatedPending集合以说明范围。执行器实际生成的事件仍只能进入下一轮。最终合同可换字段名，但须保留这两个统计范围和完整payload。

## 单次提交与响应丢失

建议内部adapter在提交前固定 `(projectId, inputDigest, jobId, runId, expectedRound, operationId, stateDigest)`。operation分配一次，不能每次观察/重试生成新值；示例UUID仅说明身份形状，不是实际持久运行记录。

- 提交前验证项目/run/job归属、输入摘要、expectedRound、当前取消/租约与完整状态；轮次、operation标记、job committedProgress同连接同外层事务提交。
- 原marker已存在时，先核对同operation/job/run/round及完整载荷，准确返回原snapshot/receipt；不推进下一轮或重复增加stateVersion，不用旧CAS拒绝已经精确成功的同次重试。
- 响应丢失后用权威history/marker核对完整身份及载荷。匹配则保留已提交效果，随后按当前真实取消/任务状态收尾；不得返回“本轮零效果”，不得再次执行动作。
- marker不存在且确认事务回滚，才能按真实取消/失败边界保留上一轮。无法读回或身份不匹配时保持对账失败/待恢复，不假定零效果或成功；由I04恢复规则确定终态。
- 轮次全部写完不自动等于任务终态成功：取消、最后提交和终态持久化的竞态仍由T01/I04统一处理。worker不打开Store、不自己发布结果/终态。

批准5f的 `commit_job_round` 当前内部生成operation并按progress+1推断轮次；`test.rounds`又只允许toy状态。以上需要由T01冻结具体内部API/错误与恢复fixture，正式能力由T00/对应owner统一启用。本线测试专用PersistentProbe只展示真实Store的完整记录对账路径，不可作为产品adapter直接发布。
