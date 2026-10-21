# 规则批次复核：纯私有模块

已实现按可信原 child 限额重放和复核保存批次的纯模块。固定代码候选为 `16c58c6d0ca56491c7134c4866f9bed5e0f722c5`；实施与独审收据见 [证据目录](../../reviews/T05/rule-batch-revalidation-implementation/)。I05 正式消费尚未授权。

## 接口与边界

`rule_revalidation.check_firing_batch(definitions, catalog, original_matches, saved, *, limits, disabled)` 返回 `batch-consistent` 或 `definition-only`；其他情况抛安全 `ProfileFailure`。新复核预算标识为 `mechanism-revalidation-budget/2`，既有 profile/1、mechanism-budget/1、七模块和旧 API 不变。

`limits` 必须是 exact `ProfileLimits`，各字段 exact int、非 bool、非负且不超过固定默认值，入口复制为新冻结值。数值合法不认证它来自原 producer/分池账本。调用方须提供同一原 definitions/Catalog、完整原有序 false/true matches、binding/when/proof/source 和原限额；恢复、保留、外层调用次数及来源绑定不由本函数实现。

复核先用原限额 fresh compile 一次、evaluate 一次，再对保存 firings/facts 作一次完整 typed 编码；预扣后检查 fresh→canonical saved→saved payload 的两条连接边，以及 digest/profile。最后唯一一次组/比较遍历，对每个保存 operand 调 canonical `check_value`，即使别名相同也逐出现收费。字节相同的直接构造、篡改、pickle 恢复或模块别名对象不能冒充真实签发。

disabled 必须无原 matches、无 batch，只作有界 compile；空定义且原来无 batch 同理，返回 definition-only。实际存在的空 batch、全部 false 的批次仍完整重放复核；非空 enabled 且缺 batch 失败。原 disabled 若未曾成功编译，不能仅因生产跳过执行就承诺新 compile 成功。

## 逐操作预算

三个互不借用的现有 `Budget` 分别负责 replay、保存编码和保存 operand 签发检查，均使用原 child 限额副本。合法完整结果分别对应原执行、原输出编码片段和 true comparison 检查子集。入口控制单位在限额复制前支付，随后只绑定一次控制上限，组/比较和完整字节比较均在操作前支付。

对 child i，`C=32, H=64, P=len(PROFILE)`：

```text
K_i = 1 + F_i + F_i*C + 4*O_i + 2*H + 2*P + 4
work_i <= 3*W_i + K_i; input_i <= 2*I_i; output_i <= 2*O_i
whole <= 3*sum(W_i)+sum(K_i), 2*sum(I_i), 2*sum(O_i)
```

整次界以可信 N/分配/失败重试账本为前提；未证明 sum(F_i) 时不换成整次 F。源码不创建 I05 allocator，也不从参数认证原 limits 或原 matches。恢复/重新 parse、缓存键/哈希、完整 JSON 投影、原输入保留和跨 child 生命周期费用须另证，不能藏进三池。此处是 debit/编码字节界，没有 CPU、时间或进程峰值内存承诺。

## 实际验证与固定来源

source40000 见证已使用真实 canonical API 执行：原 compile+evaluate 成功（input 182041、output 82902）；fresh compile 后旧逐组复核实际 `RULE_INPUT_BUDGET/resource`；新 API 在相同原限额成功。完整手工输入、语义预期、实际 payload、三池/control usage、原 stdout/stderr 和 exit 保留于证据目录。该见证无 comparison，issuance 使用量为零；比较子集另由专项和独立预算探针覆盖。

新增专项覆盖紧原限额、多规则/组/多头及重复 occurrence、source/proof、false 后项运行时类型错、Unicode 同 dbb 生产重验、所有保存连接边/篡改与发行身份、disabled/空定义/真实空 batch、类型/资源和安全错误。合法等值结果的 issuance/control 不会自然超出已证明上界；其耗尽传播测试明确标为依赖故障注入，不编造同限额合法生产成功后被预算误拒的反例。synthetic N100 仅验算式。

新 Git 树从批准 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3` 开出。`cf93fe88258cda11308c627ee7f47c1c9e0ffae3` 先逐项采用批准清单的 21 份 dbb 原件。随后仅按单独 2178B/d8d9 授权适配一个导入测试：保无副作用/完整 **all**/unknown 断言，实际确认未批准 definitions/planning 缺失及四 lazy 名字不缓存；第二个 fixture manifest 测试原样。原导入失败 1 failed/1 passed 与旧测试原件保留，不复制缺失模块。

相对 develop 的产品范围为 **20 精确采用 + 1 采用测试适配 + 3 新路径**，共 24 路径；不能写成整个 diff 仅三路径。新三路径为 rule_revalidation.py、专项 test 和独立手工 cases.json。正常 check、受影响回归、归档源核验及两份独立审查的最终实际结果以 [最终收据](../../reviews/T05/rule-batch-revalidation-implementation/final-receipt.json) 为准；收据生成前不预报通过。

## 后续门

本模块仅源码可用；I05 同输入组合/正式消费、严格保存恢复与独立整次 R、T01 producer/不可变来源/权限/窗口/撤回 GC、T03 D2 包及父验收须分别完成。没有恢复器、Store/Job/worker/公共接口或包内可用性变更。原 Goal 保持 blocked，原两树与历史证据冻结；没有 GUI/native、推送、PR 或合并。指定同版外审、CI 与正常 develop 合并门保留。
