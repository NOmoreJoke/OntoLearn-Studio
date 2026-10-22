# T03 P2 新候选独立审查

结论：在本次两处产品增量与固定 17 case 证据范围内，未发现需要修改产品的阻断问题。新增六项确实进入同一个固定 probe invocation，旧 11 项实现与预期保持；交付原件、实际包和候选提交之间的绑定可复核。本结论不替代主控指定的两个全新外部审查，也不关闭原全量审查尚存的功能或覆盖问题。

## 审查对象与独立性

- base：`30319412daf8ae4745987babf7bbed93c53b6b42`。
- candidate：`da1795b20c3c0d47ae975fe3371e802092a4b429`，分支 `fix/T03-mapping-p2-boundaries`。
- 产品只审 `packages/engine/src/ontolearn_engine/mapping/probe.py` 与 `packages/engine/tests/test_mapping_entrypoint.py`；读取新 P2 docs、其引用的本树原件、旧 11 项固定期望及实际包的三模块 PYZ 内容。没有编辑产品、旧报告或 AGENTS。
- 本 reviewer 未参与该增量实现。执行的唯一审计程序是本目录 `audit.py`；它只做 Git/文件/JSON/AST/PYZ 读取和哈希校验，没有执行 source entrypoint、包内 code 或实际 engine，没有重跑 full check、打包或 GUI，没有网络操作。
- 实际调用：本树 `.venv/bin/python docs/reviews/T03/mapping-p2-boundaries-20261023/independent-review/audit.py`，本次 exit 0、stderr 0 B。执行 UTC、逐项结果见 `audit-result.json`，完整 stdout/stderr 另存；未发生审计失败后重写结果。

## 代码与验收核对

1. **旧 11 项保留。** 原 `run` 仅改名 `_legacy_cases`；独立 AST 比较确认其函数体逐节点相同。新 oracle 投影到 base 的 `project-probe-first.json`，全部原字段、四条 facts、三依赖版本与旧 11 个 case 完全相同。旧期望原字节 SHA-256 是 `5124b647c29d60bd1e4483ca6caf7d68c3a2f02eaff0241b06112ce902944203`。
2. **外部引用两个固定输入真实构造。** `probe.py:214–275` 写死最小 OOXML：一个 B2 `WEBSERVICE("https://example.invalid/ref")` 公式及字符串缓存，一个 B2 显示文本和 `TargetMode="External"` hyperlink 关系；无 caller URL/path。`284–295` 读取真实 parser 返回的两格内容，要求精确值并输出 sheet/row。成功输入的 column=2 是已知 B2 fixture 坐标，不是错误对象返回的列号；不能把这两个成功观察描述成六个 parser error 定位。
3. **CSV 四类错误定位严格。** `296–342` 以内置旧 caps 各生成 file/column/cell/row 超限输入，捕获实际 `SourceError.issue`，比较完整 `(code,sheet,row,column)`，并把实际 issue 四字段写出。无错误或位置不符均 fail closed。源码 caps 未改；观察分别为空/0/0、CSV/1/0、CSV/2/1、CSV/50002/0。新增位置负例故意将 file-limit 的 row 改为 1，可触发 `CSV_BOUNDARY_LOCATION_MISMATCH`；它不是仅校验预先写死的结果文案。
4. **socket 观察范围成立。** `191–211` 在尝试时先加计数、再抛异常，`finally` 恢复三个原对象；`346–364` 将所有固定输入构造及解析包在 guard 中，依赖 openpyxl import 明确在 guard 前。即使 parser 吞掉拒绝异常，随后的累计计数检查仍拒绝成功。对应新测试覆盖三个 API 故障、吞异常、成功/异常恢复。guard 对整个单次 invocation 共用计数，各新 case 保存当时快照；不属于 17 个隔离计数器。
5. **入口及预期没有放松。** 两产品增量中没有 entrypoint、source parser、plan、依赖、锁或 builder 改动。普通与 `-O` entrypoint 测试仍完整比较 serialized JSON 与静态 oracle；新增恢复测试仅比较它负责的 boundaryEvidence，避免 Python tuple 与 JSON array 的无关差异。此调整没有取消完整入口断言。`_require` 使用显式异常，优化模式不会移除验收断言。

## 原件及实际包复核

独立审计结果如下，均为 reviewer 重新读取/计算，不仅采信交付文案：

| 对象 | 结果 |
| --- | --- |
| docs `manifest.json` | 19 个文件的 size/SHA 全相同 |
| `raw-evidence-manifest.json` | 74 个原件的 size/SHA 全相同 |
| `candidate-binding.json` | 11 个 source identities 全相同；除独立 AGENTS overlay 外均等于 candidate 提交；记录的受保护路径仍等于 base |
| 运行时 dirty 与提交 | 主要 check、sources、package、verify-package、source-O 的 command-at-start 两产品 SHA 均等于当前 candidate；未把运行时 HEAD303 写成已在提交后实测 |
| actual receipt | docs 副本与 raw receipt 字节相同，28825 B / `5ad2ea0f5dd16463cba097b60127188ba7d41eff5b5e2b4ca138d8c2d37a076f` |
| actual engine | 当前 4622464 B / `c4c8d80cb78323a0c7dc28978893197d477809764a0ac2a2c336734cfd1be031`，等于 raw receipt |
| engine inventory | 当前完整 440 项与原件、docs 副本逐项相同，文件实际 hash、目录种类、symlink target 均核对 |
| package PYZ | 独立读取真实 engine 的 probe/source/plan，源以 flags=0 / dont_inherit=True / optimize=0 编译，只递归替换 co_filename、marshal4，三者均与实际 PYZ 和原 receipt code SHA 相同 |
| lock / licenses | receipt 引用的 source lock、packaged lock 和四个 license 原件 size/SHA 全相同 |
| 5 个固定 subprocess 原件 | source/package JSON 完整等于 oracle，exit0 且 stderr 空；path/script/URL 三拒参 stdout 空、exit2、固定 32 B stderr |
| source `-O` | 独立读取已执行原始 stdout，完整等于 oracle；对应 command receipt exit0 |

17 条 `allCaseRecords` 都保留 `independentPerCaseProcessExit:null`，并明确记录同一 source/package invocation 的外层 exit0。旧 11 项 `boundaryObservation:null`，没有补造其原先未输出的位置；新六项实际 observation 与完整 oracle 一致。没有把内部 case status 当作独立进程退出。

本次还回读了 14 个 command receipt 与原双流，确认首次 Ruff 三长行/两文件格式失败和首次 targeted 1 failed / 11 passed 均保留。修正后的 targeted 为 12 passed；fresh check 原始日志含 638 TS、1116 Python（60.53s），sources 为 12 个归档源，package 原始日志显示本树独立 mac-arm64 输出。上述是对已运行证据的独立复核，不是 reviewer 重新执行这些命令。

oracle 冻结记录 UTC 为 2026-10-22T18:40:45.294885+00:00；各受控命令从 18:42:29 起均记录同一 oracle SHA `e7a8c0d3e0e9152d56da781a1705837e7987ac44cc4e450a8707293e2641eebc`，实际 verifier 于 18:47:19 启动。reviewer 核对了这些记录的一致性；没有用新 stdout 重建或调整 oracle。

## 未覆盖边界

- “零 socket”仅表示被替换的 `socket.socket`、`create_connection`、`getaddrinfo` 在固定解析期间计数为零；不涵盖依赖 import、预先保存的 API 别名、其他 OS 网络入口。交付报告与 receipt 已明确这些限制，本次没有将其扩成全系统断网证明。
- 两个固定引用形态只证明对应合成 WEBSERVICE 缓存和 hyperlink 显示文本行为，不是所有 externalLinks/公式/工作簿格式的穷举证明。
- code object 等价只对三模块成立；当前完整目录 inventory 是其余文件的实际身份记录，不把它升级成全部代码与所有依赖的语义等价证明。
- 私有 verifier 在 subprocess 前归档完整 inventory、结束时重查 executable，本次 reviewer 又在结束后独立核对当前完整 inventory。原运行中每一个时间点的所有数据文件均未变化，不是这里单凭快照能单独证明的结论；本交付也没有作该声明。
- 没有生产用户文件、GUI、目标平台、nativecaller、DB、I05 或注册业务能力验收。本候选不能继承旧候选外审结论，亦不消除旧全量外审中的未解决事项。

审查处置：本次无产品修改请求，可把 `da1795` 及其已绑定实际包交主控进入下一阶段。是否关闭 P2 和整体 gate，由主控结合指定外审原始结论决定。
