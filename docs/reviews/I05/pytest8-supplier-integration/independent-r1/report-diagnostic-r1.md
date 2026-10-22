# I05 diagnostic-r1 独立静态审查

结论：Limited Pass，仅针对两处诊断落盘改动；未发现新增 P1/P2。新增代码保留原调用与断言，仅在调用返回后、解析/断言前保存两个原始 BytesIO 的字节。另经固定 2cf 的 explanation_roots 单函数只读核对，原测试将结果项当成 RootRef 属性对象的假定确实不符合该函数返回结构。

## 已核验改动

候选目录：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-pytest8-supplier-integration`。比较基线：`d1fb6d13ead01a10a5406a661d38f46108098663`。

测试文件当前 75647B，SHA-256 `4fdc5c954c7784ca17298da4e23cbe77d7a618cfeb93add29cd074a13285a39e`；基线 75277B，SHA-256 `920883c27b6390a2f38aa71bbb399d3b588fe819b1298282da60e6217f11694b`。实际完整 diff 已保存为 diff-diagnostic-r1.stdout.raw，Git stderr 原字节另存，exit0。

- module-scope full_run 仅新增 tmp_path_factory 参数，以及调用后的 mktemp、stdout.write_bytes、stderr.write_bytes 三条语句；原 selector/full-v1 调用、返回值解析和返回元组保留。
- producer-fault 测试仅新增 tmp_path 参数，以及调用后的 stdout.write_bytes、stderr.write_bytes 两条语句；两个已有 monkeypatch 包装器、full-v1 调用、失败定位与全部断言保留。
- 精确移除这两个新增参数和五条诊断语句后，整个测试文件 AST（不含位置）与基线相同。该检验不只比较局部断言。
- probe 文件与该基线字节完全相同：102669B，SHA-256 `05f4ac85f883f40142782e9ee3943b8df9593ddf5a35e318ca35bbd6781a6dd4`。因此该 diagnostic patch 未改 selector、guard、identity、公共错误、产品调用流程或产品实现。

## 无隐藏 bypass 的静态判断

新增代码没有捕获/压制异常、替换 returned code、重绑 stdout/stderr、筛选/改写 JSONL、修改 expected 或移除断言。write_bytes 接收的都是原 BytesIO.getvalue()，包括零字节 stderr，未创建人工拆分流。文件系统写失败会作为额外测试错误暴露，不会把原失败转成通过。

新增 tmp fixture 与文件写入确实增加测试 I/O；本审查不声称执行时序完全不变，也不证明磁盘一定可写、pytest 临时目录一定被长期保留。原调用若未返回，这两处诊断语句不会执行。本改动没有提供 hard-stop、readerJoin 或崩溃前落盘保证。主 agent 应按既定证据流程保留原始临时文件及实际运行身份。

## explanation_roots 的固定返回结构

本次新增窗口只通过 Git/AST 抽取固定 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64` 的 `packages/engine/src/ontolearn_engine/semantic_profile_restore.py::explanation_roots` 单函数（1696–1767），没有 import/执行产品，也没有跟随其他算法。

其签名为 `explanation_roots(view, target_keys, *, direct_ledger)`。1743–1750 行显式构建 tuple：leaf 项为 `{kind, reference}`；step 项为 `{kind, ordinal}`；其余分支为 `{kind, firingIndex, headIndex}`；1767 行返回该 result。内部使用 RootRef 不等于公开返回 RootRef 实例。固定函数实际把内部 ref 字段投影成普通 dict。

因此，原测试 `roots[0].kind`、`.ordinal`、后续 `root.kind`/`root.reference` 属性假定是错误的消费方式。此结论现在有固定实现的结构证据，不再仅依赖一次 AttributeError。它不授权改变该公共返回结构，也不证明原测试期望的 kind/ordinal/引用值都正确；修复应保留原业务期望并按当前映射形状读取，再由主 agent 运行验证。

该单函数投影不构成前 7 项采集根因的证据；先前报告对缺少首次 firstFailure 的限制继续有效。父 agent 告知首次 BytesIO 未落盘，此事实在本审查中仅作为父 agent 提供的运行背景，没有独立读取新的运行数据来确认。

## 检查记录与限制

第一次自编 AST 辅助检查错误地假定 full_run body 长度为9，实际该假定不成立，检查器 exit1；这不是 pytest/产品失败。随后改为按 diagnostic 赋值和 write_bytes AST 节点定位，精确删除诊断节点后进行整文件 AST 比较，exit0。失败未记为产品回归，也未从记录抹去。

仅执行 Git、文件读取、哈希和 Python stdlib AST 操作，未运行 pytest/full-v1/B1/canonical、Ruff、formatter、安装器或 GUI。供应商三路径的采纳、依赖闭包、环境和下一次实际运行均不在本独立审查的验收范围内。此前 report.md 与所有既有产物保持原样；本轮只新增 diagnostic-r1 后缀文件。
