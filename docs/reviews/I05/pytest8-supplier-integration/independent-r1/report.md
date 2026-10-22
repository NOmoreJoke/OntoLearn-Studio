# I05 首次 pytest 8 项失败：独立静态短归因

结论：日志证明一次共享 full_run 未完成、一次独立故障注入运行没有到达 restore 包装器，以及一个 roots 返回值与测试属性访问的类型不一致。现有日志不足以把前 7 项归为同一个具体代码缺陷，也不足以决定改测试还是改公共接口。本次没有运行产品或修改产品/测试。

## 范围与身份

- 审查者：独立子 agent `/root/independent_pytest8_static_triage`。
- 调用者声明的卫生候选：`e56eae1eeebcd845cf07a9ec5ce638cb0df953c7`；过程提交：`d1fb6d13ead01a10a5406a661d38f46108098663`。本次没有读取 Git 元数据去再次验证 ref。
- 只读取两个卫生候选源文件及 T03 原始 pytest 日志；三个文件的完整字节哈希已独立验证，见 read-receipt.json。源文件只渲染并审读相关窗口；并未把整文件哈希称为全文工程审查。
- T03 日志：15886 bytes，SHA-256 `62b3e3989a16dc19787686af7debc81d04aa05d8045577f3e4f28d4f927f139e`。全文 239 行已读，最后记录 1175 collected / 1167 passed / 8 failed / 204.47s。
- 日志来自 T03 运行时旧格式源文件，行号不同于本次卫生候选；下表同时给出日志断言旧行号及当前对应位置，不据此声称当前候选已经运行。
- 未读取共享生产算法、T03 环境、T03 WIP 或其他文件；未调用 pytest、canonical API、full-v1、B1、安装器、Ruff、格式化器或 GUI。

## 8 项逐项结论

| # | 测试 | 原日志断言行 / 当前测试行 | 日志直接证明 | 静态归因与未决边界 |
| --- | --- | --- | --- | --- |
| 1 | test_full_jsonl_is_complete_inventory_not_self_signed_equivalence | 833 / 950 | full_run 返回 status=1，stderr 为空 | 共享采集不成功；空 stderr 不代表没有诊断，采集器会写 JSONL observation/terminal。具体 firstFailure 没有出现在日志展开内容中。 |
| 2 | test_full_observations_keep_parameters_sources_counts_and_statuses | 904 / 1028 | 同一个 full_run 至少有一条 unexpected-failure | 不是第二次独立采集失败。日志没有展示该记录的 id、error.code、classification、stage 或 api。 |
| 3 | test_fragment_repair_shape_inputs_execute_without_upgrading_old_math77 | 929 / 1059 | 同一个 full_run 的索引没有 transfer-repair-before | 与采集不完整相容的连带断言失败；不能断定该 repair 自身执行后失败，也不能断定其业务语义错误。 |
| 4 | test_missing_mandatory_policy_keywords_are_actual_call_contract_rejections | 951 / 1085 | 同一个 full_run 中没有 shacl-policy/missing-both | 与早停导致未执行相容；不能由 KeyError 宣称缺少必填参数的拒绝规则错误。 |
| 5 | test_full_production_bytes_are_complete_and_restore_uses_actual_capture | 962 / 1098 | 同一个 full_run 没有 status=observed-return 的 fullview/dag 条目 | 只证明筛选结果为空；不能据此断定生产 API 执行并失败或产物字节错误。 |
| 6 | test_restore_negative_copies_bytes_but_keeps_same_caller_capture | 1067 / 1216 | 同一个 full_run 没有 status=observed-return 的 restore-negative 条目 | 只证明筛选结果为空；不能据此断定负例本身违反 capture/restore 保持规则。 |
| 7 | test_r1_real_producer_capture_survives_restore_unknown_failure | 1251 / 1415 | 另一次有故障注入的 full-v1 返回1；issued=received=0 | received=0 证明本测试 restore 包装器未进入。issued 在原 producer 成功返回后才 append，所以 issued=0 不能证明 producer 从未进入；原函数也可能在 append 前抛出。它不是前6项共享 fixture 的同一次运行，不能未经 JSONL 就认定同一根因。 |
| 8 | test_real_capture_restore_retains_original_expectation_on_bad_bytes[True] | 1657 / 1842 | roots[0] 在这次真实调用中是 dict，访问 .kind 抛 AttributeError；短路顺序也证明 len(roots)==1 已通过 | 测试假定返回项支持属性访问，与实际结果类型不符。公共返回契约未在许可窗口内核实，不能单凭实际 dict 就替换 expected，也不能单方把生产接口改为 RootRef。 |

## 采集早停证据与因果边界

当前测试 939–944 行将 full_run 声明为 module-scope fixture，并只调用一次 run_fixed_suite("full-v1")。前6项测试消费这个同一个结果，因此 6 个失败不能当作 6 次独立运行失败。

当前采集器 2518–2566 行会把 BoundaryStop 或未知异常记录为 unexpected-failure。BoundaryStop 可设置 deadline/stopping，未知异常设置 failed；2576–2580 行写出 observation 后按 code 退出循环；2590–2602 行写 completedIds、unstartedIds 和 firstFailure。因此当前实现提供了明确的早停传播路径。但原始日志里的 full_run repr 被 pytest 缩略，没有真实展开 firstFailure。不能从 204.47s 总 pytest 时间反推某次 120s deadline 触发，也不能把 unknown/internal、deadline、资源上限或某个 API 指认为已证实原因。

第7项当前测试 1398–1415 行另行调用完整采集并安装两个包装器：producer 包装器先调用原函数再 append；restore 包装器进入即 append 再抛 RuntimeError。原日志没有展开本次 failed observation，因此只能得出上表边界。尤其不能把 issued=0 写成“没有任何 producer 调用”。

## roots 类型不一致的精确范围

第8项在失败前已完成当前测试 1820–1836 对应流程：真实生产、真实 restore、原字节一致性、载荷/行尾加空格拒绝以及 expectation/allocation 保持断言。日志只证明这条参数化用例在此之前没有失败，不覆盖其他输入或整个生产契约。

当前 1842 行使用 roots[0].kind 和 .ordinal；后续 1864–1865 行还有 root.kind、root.reference。它们属于相同的属性访问假定，但后两处未执行，不能记为新增实际失败。原日志没有打印 dict 的键和值，不能预填 kind、ordinal 或 reference 的实际内容。

当前 collector 在 1780–1788 行接收 explanation_roots 返回值后交给 _typed_value；_typed_value 的 969–975 行显式支持 str-key dict。因此“roots 实际是 dict”本身不直接证明 full_run 的 collector 会因此失败，更不能把第8项当作前7项根因。

## 最小后续证据

1. 优先取得这次首次 pytest 中共享 full_run 已产生的原始 JSONL，至少包含第一个 unexpected-failure 的完整记录及 terminal（firstFailure、completedIds、unstartedIds）；保留其实际字节/hash/来源，不重构截断 repr。
2. 单独取得第7项故障注入运行的完整 failed observation、stageAttempts、partialOutputs 和 terminal，区分 producer 未开始、开始未返回、较早 observation 失败等路径。若原始 BytesIO 未被保留，应明确记录不可恢复，不能把重新运行的产物冒充首次运行。
3. 通过根协调者限定窗口核对 explanation_roots 的正式返回契约/原有 canonical 合同测试；然后由唯一负责人裁定测试假定还是公共接口不符合契约。先核对契约，不改 expected 凑通过。
4. 后续真正运行需由根协调者明确供应商三路径、候选身份和 runtime 授权；本独立短审没有补跑来消除缺失证据。

本报告是静态归因，未给出验收通过或整体完成结论。
