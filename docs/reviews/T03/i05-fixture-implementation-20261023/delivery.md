# I05 provenance fixture：唯一测试文件有限移交

已冻结测试候选 `27eaaafcfad0f53e287401c24f7dae991c8cea63`，父提交 `6202e3144405f7a718e5d3d1dde7f42ec45a3b65`。产品差异恰为 `packages/engine/tests/test_semantic_build_provenance.py`，74行新增；最终47627B，SHA-256 `216d92b0dae54c28bb9464cf854e39110b8010d73020b1d66cdd9cb4df92d4a2`。本移交不包含 I05 采用、完整检查通过或发布批准。

## 实际改动

`make_case` 入口使用同一个 MonkeyPatch 隔离八个固定 distribution 的精确根名及点分隔后代；退出时按逆序恢复原对象，包括 None。没有改 reader 对未登记 loaded 子模块的拒绝，也没有改 builder、entrypoint、合同、依赖或封存输入。

新增三个实际测试项：正常退出恢复、首次 fake_module 调用中抛错时的 setup 恢复、预置污染后通过 request.getfixturevalue 构造真实 case fixture。覆盖全八根、深层 child、None、近似前缀与 fake native sentinel，要求 keyset 和对象身份恢复。未知 child 负例先验证 clean positive；原 repeated loader-code verification 保持原意。

## 实际验证与首败

| 步骤                                     | 实际结果                                          | 精确边界                                                                                                                   |
| ---------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 完整 supplier 模块                       | 101 passed，exit0，JUnit101/0failure/0error/0skip | 实跑源码47649B / `76068ad0…c28f9a`；UTC/PID/argv/cwd/环境覆盖/四源前后/完整分离双流均在 owner/01-supplier-module           |
| 一次原 npm run check                     | exit1                                             | 在3份继承固定文件的 Prettier 阶段失败；未到 typecheck、vitest、build、Ruff、全套 pytest。首败完整保留在 owner/02-npm-check |
| 唯一测试文件 Ruff check                  | exit0                                             | 对76068源码；不是整个仓库 Ruff 通过                                                                                        |
| 唯一测试文件首次 format check            | exit1                                             | 仅提示 if any 条件换行；487B stdout原件保留                                                                                |
| 仅该文件格式化                           | exit0                                             | 76068→216d，仅一处换行，主与独审均确认完整 AST 去位置属性后相等                                                            |
| 最终 format check / test-path diff check | 均exit0                                           | 对216d源码；没有重复 supplier101或原全量检查                                                                               |
| verify:sources                           | 未执行                                            | 原全量首败后停止依赖步骤，不计通过                                                                                         |

所有运行均在本方 supplier tree，原命令和自然 child PID/UTC/exit 在各 start/receipt，原双流不合并。测试运行前后四源字节相同；格式化步骤有意只改变测试文件并正确记为四源不全同。101结果始终绑定76068，不能冒称216d实跑101。完整 AST等价只说明该换行未改代码结构，不替代未来目标树的真实检查。

三份 Prettier 首败文件为：`docs/iterations/I05/source-package-probe/implementation.md`、`probe_inputs/i05-source-package-parity-inputs.json`、`probe_inputs/i05-source-package-parity-manifest.json`。当前字节均等于6202和830cdd固定对象，身份见 owner/first-check-formatting-block.json。未格式化这些封存输入，未改 ignore/配置，未重跑原 check。

## 独立审查与过程归档

非作者对76068实际完整测试源及diff作 pre-run 静审后才开始运行；随后独立核原两次运行、101项 JUnit、首败、三个继承格式路径及四源身份。格式化后另追加完整 AST/文本 delta 审查；首报告与manifest保留。主已全文读三个最终报告并核各manifest。

根追加授权的过程改名 `static-audit.py`→`static-audit.py.raw` 保4335B / `17b9c228…6418f1`原字节。6202旧提交与旧manifest不变，新 sidecar绑定旧路径/旧hash/新路径；实际改名发生于首check自然exit之后，没有倒填成运行前已改名。旧manifest按其冻结6202解释，不宣称当前旧路径仍存在。这个改名不是本次三个Prettier失败的修复。

测试源码路径 diff check 为0；包含原字节 patch 的过程归档 staged diff check 为2，原因是 unified diff 的空白上下文行含一个前缀空格。完整输出保留在 owner/process-staged-diff-check 记录中，未清洗原件，不把它写成全部 diff 检查通过。

## 下游采用门

根已明确允许以“101有限通过、wholecheck仍NotPass”移交唯一测试blob；I05只能由根另票在实际集成源9d86的后继候选采用，然后执行真实目标完整原check。当前未跨写I05或mapping两棵c1e44受审树。原I05 1320/2、此前98、本次101及两次格式首败各保留原身份；实际first offending module名称仍UNKNOWN。未运行native、CLI、prepare、打包、GUI、全417或模型API，未push/PR/merge。
