# I05 strict restore 必要 delta 独立复核：1316050

结论：**S1 已关闭；本候选不通过，新增 1 项 P2（S2）：receipt 构造失败后，公开异常帧仍保留已恢复的 children。** 首轮 `report.md`、`audit.json` 及原探针原件均保留，不改写 bbd 的失败结论。

本轮仅复核 bbd→131 的实际 delta 及必要上下文；测试差异以先前实际受审测试 b301→131 对照。没有重做整份方案审查，没有使用共享 Python 环境、修改四个产品/测试文件、68 项只读输入、AGENTS 或 Goal。仅写本目录 `delta-*` 证据。

## 固定版本与运行绑定

- 新代码/测试 ref：`1316050a895a787b7b94bbe18e99efcb3cd141d2`
- 原受审代码 ref：`bbd79c3cff88e8fef348a9c4dcb6981ab5e3cb47`
- 原受审测试 ref：`b301c3cdb348c08c6d10f1ac4e11666ec9bbd39b`
- base 仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| `semantic_profile_restore.py` | 49854 | `ce157068bbcf5695606cf918d405e633a330f16046420dc7e68d201516bd311f` |
| `semantic_profile_restore_budget.py` | 37478 | `593b2a832dd510063bb60d7b3d5526fbd6cf4dcba53ad9c513e82dbfdd77ef7f` |
| `test_semantic_profile_restore.py` | 33681 | `d3726f6170d126f7a6b495f53b951093faf0b3caa935b3d87a06c18c25619aac` |
| `test_semantic_profile_restore_limits.py` | 19794 | `7409ac4b72ca352b14f6d3ec6d4cb3dc5246060ec16231bcff86e7224e105ed9` |

`delta-audit.json` 逐项核对 `candidate.json` 的全部 **72 项**：新 fixed Git blob、当前字节、runs/06 的 sourcesBefore/sourcesAfter 与 manifest 均完全一致，含 68 项保护输入。四个恢复源码/测试的 AST parse 通过。

已读回 runs/06：实际专项 **142 passed，exit=0，timedOut=false，stderr 为空**。记录中的运行时 Git HEAD 仍为 bbd，本报告不把它写成当时已在新 HEAD 上执行；其全部72项前后源哈希逐字等于 131 固定候选，所以该次专项可按真实执行字节绑定新候选。本子 agent 没有重跑这142例。

## S1 关闭依据

新 `semantic_profile_restore.py:905–923` 在 `_check_expectation()` 最前面完成：

- `rule_ids` 和 `disabled_rule_ids` 先 exact tuple，随后才 len/iterate；tuple 派生类也不能进入。
- 原规则上限100、disabled 数量、children 槽数均先核；children exact tuple 已在公开入口 `:1204–1206` 先完成，因此本段 `len(allocation.children)` 不引入新的先用后验型路径。
- 两组 ID 成员先 `decoder.string()` exact str 后才 `bool()`；每 child 先 exact ChildAllocation / ProfileLimits，rule_id 先 optional_string 核型，ordinal 先 exact int 后数值操作。
- 后续原排序/唯一性、disabled 成员核对、ordinal、divmod、saved L / budgetLimits 对照均仍保留，没有以转换 foreign iterable 或改变原 L 消除失败。

新增 `test_semantic_profile_restore_limits.py:237–269` 对三个字段分别放 foreign 对象、tuple 派生类、tuple 内 foreign 成员，另污染 child.rule_id，保持原 expected/hash 不变，断言全部拒绝且协议计数为零。该测试包含在上述真实142例中。

本 agent 的 `delta-audit.py.raw` 另执行新固定原入口与 `_check_expectation()` AST 分支，使用原 canonical RestoreLedger，替代完整引擎依赖；foreign rule_ids 得到 `RESTORE_INPUT_INVALID`、ledger failed、**callbacks=[]**。此为独立分支证据，不冒充完整引擎运行。

## 新问题 S2

**[P2] receipt 构造异常后，已恢复 children 留在公开错误 traceback 帧。**

- 位置：`semantic_profile_restore.py:1221–1231`，清理路径 `:1253–1261`。
- 触发：原真实生产和恢复校验成功，全部16c调用完成后，最终 `RestoredBatchSet` 构造或 usage/peaks 快照发生 `MemoryError` 等普通异常。
- 实际机制：`:1221` 将 `children, parse_usage, caps` 绑定在公开 `restore_profile_batches` 的局部帧；`:1222` 构造失败后，异常虽转为新的有限 `RESTORE_INTERNAL`，finally 只清 decoder、cache 和逻辑 live。最终 `raise error` 的 traceback 必然包含该公开函数帧，其中 `children` 仍引用完整 RestoredChild/native batch；`parse_usage/caps` 也仍保留。构造失败时 outcome=None 并不能清掉这些独立局部引用。
- 实际入口证据：父审已从真实 `capture_case()` 完整成功开始，在最终结果构造器注入 `MemoryError`，得到 ledger.failed / live=0 / decoder=None，同时公开 traceback frame 的 children tuple 仍保留1个真实重建 RestoredChild/batch。原件 `runs/07-receipt-failure-probe.json` 绑定本候选 main SHA，本 agent已全文读回。
- 独立分支证据：本 agent执行固定131原公开入口 AST，使用原 canonical RestoreLedger，模拟私有 `_restore()` 返回 children sentinel 并在 final constructor 注入 `MemoryError`。结果为 RESTORE_INTERNAL、ledger failed/live零、decoder已清，但 `error_public_frame_retains_children=true`，见 `delta-audit.json`。这里只验证异常帧的实际控制流，不把模拟 child 当引擎成功证据。
- 影响与边界：失败异常对象继续持有已发行的 native 结果及其 child fact，不能认为所有临时已丢弃或 transferred；账本 live=0 与真实持有不一致。失败调用者还能通过公开 traceback 的 f_locals 取得本应只在整体成功时返回的 children。本问题不是最后 API 正常失败路径失效，也不声称 Python 内存调用者因此获得正式 producer/Store 权限。
- 依据：本阶段合同要求异常安全、终止临时持有、全部成功后才一次发布不可变结果；新 receipt 时序本身是为了将构造也纳入 running/异常边界，因而必须覆盖其构造失败路径。
- 建议：在失败清理分支显式清 `children/parse_usage/caps`，失败时也置 outcome=None；或将这些构造保持在可被丢弃的私有帧，只将最终 outcome 带回公开入口。须保留成功结果转移与最终 usage/peaks 快照准确性，不重新引入 snapshot 后未计费操作。
- 必要回归：真实 capture→实际 restore，对最终 `RestoredBatchSet` 构造注入 MemoryError，断言安全有限错误、failed、live零，且公开异常帧不持有 native children/outcome。再核普通末 child checker 失败和成功返回，确保清理不破坏原子成功结果。

## 其余 delta 对 schema / 行为的影响

1. `graph_budget` / allocation parse pool 提前对象 reservation、`_project` 增加 scalar reservation 和 BaseException 释放、canonical writer 的 8×bound+64 保留块均未修改 native 字段、值、tuple/list、PV parse 或比较规则。它们会新增正确的资源拒绝点；实际上界是否覆盖所有同时活跃数据归预算独审，不由本报告越界宣布通过。
2. A16 receipt 构造前先预付，再完成所有16c，最后构造 frozen outcome。schema/rows/witness/PV/canonical 对照仍在 API 之前，唯一check调用仍按slot一次、同原 captured L；disabled/dummy/空 batch 路径不变。
3. usage/peaks 在 `:1227–1228` 读取后，finally 只有 drop/release、cleanup、finish，没有新增 work debit 或 peak reservation；因此未发现 snapshot 后再计费造成 receipt 过时的影子变化。S2 是失败引用清理问题，不以其否定这一时序修正本身。
4. 原 expected/payload/rows/source 绑定、原 false/true 顺序、全部 comparison/head/basis/source 字段及 fresh PV 逐项比较没有变化。原 main 测试完全不变；limits 测试仅增加 foreign 协议和 encoder exact/差1 两组检查，未削弱原断言。

## 验证与限制

- 本 agent运行标准库 `delta-audit.py.raw`：72项 fixed/current/run06 前后哈希绑定、四文件AST、S1零回调与S2异常帧保留探针；结果记录 `delta-audit.json`。第一次探针脚本因 AST harness 未注入 dataclasses.fields 失败，补齐 harness 后执行成功；这是本目录探针依赖缺口，不是产品测试失败，未改产品源码。
- 父审真实142例与真实 receipt 故障注入分别作为读回的运行证据；没有冒称本子 agent 独立重跑完整引擎。
- 没有调用 GUI/Electron/e2e/native/HMR/CUA/Keychain/模型/付费/push/PR/merge；没有操作 Goal。
- 整次R费用/保留证明、最终 check/source、指定双方/CI及正式集成门仍由各自 owner 完成。此处有限“不通过”仅针对131的新失败清理问题；S1关闭不自动关闭其他门。

本轮到此停止扩展探索。待修S2的新固定候选，再只做必要 delta 复核。
