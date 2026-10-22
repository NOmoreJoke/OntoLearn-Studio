# 单测试文件实际 delta 独立 pre-run 审查

结论：**未发现静态阻断，可进入已签 START 票所列的必要自有验证。** 本次认可的是实际 patch 的范围、隔离逻辑及回归断言设计；尚未运行 Ruff、pytest 或 check，不宣称修复已通过全套，也不给 CLI/native/打包等新增执行权。

## 固定实际输入

根票为 `T03-I05-fixture-one-test-file-implementation-ticket-20261023.json`，实际 4233 B / SHA-256 `20f1dd81021ccf590bb1ad0e1737722e0384e3dc1b8bc1b595790801f914fe92`，已全文读。票明确要求非作者 actual-delta 静审在 runtime 前完成，之后无需另等一轮泛化 root 批准；本报告满足该静审步骤，不修改票。

实际 HEAD/base 为 `6202e3144405f7a718e5d3d1dde7f42ec45a3b65`。本 agent 全文读当前测试源码 1–1290 行及完整 diff：

- 唯一变更源码 `packages/engine/tests/test_semantic_build_provenance.py`：**47649 B / SHA `76068ad0853dabef7d99d97445f1a3da7b8ec52f2615524856f99c9655c28f9a`**。
- 相对 base 为 76 行新增、0 行删除；完整 diff 4511 B / SHA `4009a3f2b1ebf7c5c7d081bed679895af651b2f0f3ec5410d25194d18c0d6b5f`。
- base 测试文件为 44315 B / SHA `0def6d7da0bdc2353c6f524fe8d86d40ab18936b58d58d1cc06bae713f7a3ec8`。当前 tracked delta 除受保护 AGENTS 外仅该测试路径。

独立字节核对：builder 8437 B / `738f55ef056c3326f812ab9e4ed272a11a332a21a23a78c72fd07b510d31a8ff`；entrypoint 976 B / `aaf9f85b59f115ae0646fd31f5305ee588c2bd58a0fbb28d9714c707c9035ef3`；reader 46602 B / `c96f0630b97c02049b9ee2f62f0b44946962b14c0a2ab5c9094eaaa3fa3b7b0c`；合同 36587 B / `9d97a6a233b47abc23064a9a8f8330080d62f39b3db981de14a148880e202a04`，均与 base 相同。reader 对 loaded prefix 的严格扫描、路径/loader/代码/native guard 无改动。

## 实际隔离入口

make_case 最前端（54–58）遍历 tuple(sys.modules)，对固定八根的精确名或“根 + 点”后代执行同一 MonkeyPatch 的 delitem。位于 filesystem/fake module 构造之前，且既有 case fixture 与 finalize 单元中的直接 make_case 都经此路径。没有真实 target import、全局 clear 或任意库名猜测；没有把旧实际 offender 命名为 rdflib.*。

固定八 namespace 的 children（含深层/None/native 名称）都会隔离；prefix_neighbor 和 outside_prefix 不匹配。后续 synthetic 模块也经传入的同一 MonkeyPatch setitem，逆序 undo 的顺序为撤 synthetic、还原此前删除的值，包括 None。没有提前退出 scope 或手动 undo 全测试共享 patch。

## 新增断言的实际意义

`seed_inherited_distributions`（231–242）对全部八根分别 seed 根、child、child.deep、unavailable=None，并保存两种近似名 sentinel；额外 seed wcwidth._wcwidth_c。snapshot 收集完整匹配 namespace 的当前条目，因而既包括 seeded 项，也包括当时其他已存在 child；并非只记少数指定哨兵。

`assert_synthetic_distribution_baseline`（245–256）要求整个 prefix keyset 恰为八根、值为 exact ModuleType、近似名原对象不变，随后执行现有 verify，要求八 distribution 集合及24 supplier/private；native 仍需 NATIVE_UNAVAILABLE。故不能靠只替换 root、遗留 child、清掉近似名或仅模块数量相等而通过。native sentinel 是 fake ModuleType，测试不构成实际 extension 导入证明。

正常/异常参数化测试（260–283）使用外层 monkeypatch seed，inner context 执行实际 make_case。正常路径构造并核 baseline，然后退出 context；setup failure 路径把本测试模块的 fake_module 换成在**首次调用**即断言八 namespace 已清空、近似名仍在，并抛专用 RuntimeError 的函数。它发生在隔离完成且 make_case 未返回时，能真正检查 setup 中途失败，不只是成功后人为抛错。若隔离循环被删，异常路径会先得到 AssertionError 而非预期 RuntimeError，不能形成伪通过。

两个路径退出 context 后都要求 prefix keyset 与 before 完全相同、每个对象 `is` 同原值，近似名仍为原对象。None、深层 child 及 fake native sentinel 均属于 before 集合，已进入恢复断言。外层 seed 由外层 pytest monkeypatch 管理，测试结束后还会恢复整个 suite 此前真实条目；没有永久改库。

## 真实 fixture 顺序与原负例

新增 `test_case_fixture_isolates_inherited_distribution_names`（286–290）的测试参数没有 case。它先用 monkeypatch seed，再调用 `request.getfixturevalue("case")`，因此真实 case fixture 在污染环境中才构造，并使用同一个 pytest monkeypatch fixture 实例；不是 pytest 在测试体前已经构造一个干净 case 后再 seed。该路径核同一严格 baseline，补足仅 direct make_case 测试不能覆盖的 fixture 调度路径。其恢复依赖标准 fixture teardown；直接入口的 inner context 测试已显式断言同一隔离逻辑的恢复。

原 unknown-child negative 只增加一次 clean verify，之后在同一 evidence 上注入 pyshacl.unrecorded，保持 MODULE_MISMATCH 预期。这消除由无关 inherited child 提前触发同码而假绿的主要风险，没有删负例或放松 reader。

原 repeated code verification 函数 AST 与 base **完全相同**：第一次 verify 成功后改 loader.code，第二次期待 LOADER_MISMATCH。其原意没有降标。AST 对照还确认 imports 完全相同、原函数无删除，原有函数只有 make_case 与 unknown-child 两处发生语义增量；原 normalization、__file__/origin/loader、native、opaque evidence 等检查与 embedded Node stub 单元保持原文。

## 验证入口与限制

可按票继续用自有锁定环境，先执行完整 supplier 测试模块，再依票安排一次原 npm run check 及 sources/diff 等必要验证；实际新增测试计数应从运行结果记录，不从本静审预填。首次失败须保原件、停依赖步骤，若需具体纠正再按票做精确 delta 独审。此结论不保证整套 collection/插件运行必绿，也不把 namespace 的受控 key/对象恢复扩成任意并发 import 或模块内部状态回滚。

本 agent 仅执行 stdlib 字节/哈希/AST/Git 静态核对，未 import 产品/pytest、运行测试、格式化测试或修改 source，未 commit。独占目录保存 actual-test-source.py.raw、actual-delta.patch.raw 与 static audit 源码/原始输出。当前测试 hash 如因后续必要格式/修正发生变化，应明确新身份与差异；不能把本报告对76068的审查冒称另一个版本已审。

原 I05 fullcheck03 的1320/2、此前98有限通过及具体首 offender UNKNOWN 均保持。I05 采用新测试候选另需 root 交接；mapping 两棵 c1e44、真实 prepare/build-engine/CLI、native/ABI/loader、打包/Electron/GUI 等不由本票或本报告扩权。
