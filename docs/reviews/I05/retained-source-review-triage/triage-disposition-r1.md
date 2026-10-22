# 首次独审意见处置

独立审查确认本次六件静态 triage 与修复计划可继续，保留 P3 `R1-P3-01`。本文件是后出精度更正；六个封审输入及其 SHA 不变。

`opinion-association-matrix.json` 中 M08 的 `2cf lacks pyshacl and5 required distributions` 应按以下两个不同集合理解：

- 候选 `uv.lock` 缺五个要求成员，**其中包含 pyshacl**：`html5rdf`、`owlrl`、`prettytable`、`pyshacl`、`wcwidth`。
- 从 `ontolearn-engine` 出发并传播激活 extras 的 runtime 闭包缺六个：上述五个及 `packaging`。`packaging==26.3` 虽在整锁内存在，但在候选 engine 闭包不可达。
- `pyparsing==3.3.3` 已由 RDFLib 传递可达；直接声明缺失不等于该包缺失。供应闭包包含全部八个要求 distribution，仍不代表实际安装、import 或运行通过。

该更正关闭本次文档措辞歧义，不关闭旧外审 M08 的实际依赖缺口或 M02 的运行前置条件。独立证据为 `independent-triage-r1-report.md` 与 `independent-triage-r1-proof.json`，不是产品运行结果。

独立补充审查也确认未应用的 M06 提案静态范围合理，无阻断。根随后明确授权在本树应用指定两个自有文件并准备同锁独立环境，只运行新增精确失败边界 case 与两源静态、格式检查。其实际应用、首次测试失败、修复后结果由后出的 M06 执行收据记录；原 `m06-unapplied-proposal.*` 保留未应用时点陈述，不回写成已应用或已测试。

T03 的 manifest/锁/build 与 T01 的 Store/JobStore 仍由根唯一路由，I05 无共享源修改授权。完整语义、417/B1、打包、native、SQLite 物理保护和发布门不由此打开。
