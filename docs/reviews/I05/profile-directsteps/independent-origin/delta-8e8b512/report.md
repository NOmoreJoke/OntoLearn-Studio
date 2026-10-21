# directsteps 最终兼容 delta 独立复核

结论：**有限通过**。固定 `8e8b5126c69534c6259d37b2d3e88f75ef935aa0` 关闭 cb 完整check暴露的六个旧production兼容失败；此前来源/schema/lifecycle的O1/O2/O3与exact sink关闭结论维持。此次没有新发现，不替预算审或正式Job/selected供应门签字。

旧189失败原件、cb有限通过报告和其首失败记录均未改。独立逐项复核两份原write-lock的全部成员字节/SHA，均不变。cb报告原先没有把进行中的完整check记为通过；现在明确补记其最终失败事实，不回写历史报告。

## 固定来源与最小差异

唯一树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-directsteps`。前版本为 `cb2662c2ea4014d3de06194442f462c17eabe23b`，被审版本为 `8e8b5126c69534c6259d37b2d3e88f75ef935aa0`。完整读取两文件实际Git差异及必要上下文，恰17行增加、5行删除，没有测试修改。

| 文件（packages/engine/src/ontolearn_engine/） | bytes | SHA-256                                                            |
| --------------------------------------------- | ----: | ------------------------------------------------------------------ |
| semantic_execution.py                         | 35220 | `3ac496383349e3ddefea1672c27c88bacaf99f4436c22e96e1592393bac102f3` |
| semantic_profile_production.py                | 19993 | `5c857470890bd810370ad877db930848ba08e80096c640037d39bea83c14a320` |

对 `candidate-final.json` 全141项独立核当前字节=固定Git=候选bytes/SHA；测试和其余源码与cb不变。运行前后再次逐141绑定8e8，完整身份清单、AST检查和diff原件存于本目录。

## 两项修复的实质判断

`semantic_execution.py:718–724` 只在存在direct_ledger的新解释分支先调用 `before_explanation_projection(result, source, tuple(rules))`，随后无参数调用原 `before_projection()`，然后执行原投影。`semantic_profile_production.py:223–245` 把原D预界/整流预票移入独立方法，恢复旧hook的 `self` 单参数签名。

独立AST对照确认：cb的before_projection首个D if语句与新helper的整个body精确相同；其后原C阶段6/hash/traversal/scan_copy/reserve语句与新before_projection的整个body精确相同。新分支仍在任何实际投影与摘要委托之前取得D预票；原C四MAX_BYTES hash票仍在原阶段6、首个摘要委托前，未改票额、stage、上限或receipt费用。旧分支不再传入三个新参数，旧monkeypatch(self)恢复兼容。

`semantic_profile_production.py:445–459` 的旧public facade保留十个显式None结果槽，并在finally以固定identity断言其为空；没有把真实结果暂存在这些槽。其实际对象仍由共同 `_execute_admitted_profile_job` 拥有和清理。独立AST证明该共同函数相对cb完整不变，包含capture.drop、各结果/编码局部清空、失败outcome清空和原ledger.failed路径。facade的新增断言只比较固定None identity，不执行foreign协议或放松异常。成功直接返回共同计算的原结果，未增第二次reason/compile/evaluate或改变wire。

此次差异未涉及restore/leaf/evidence/roots/reader/纯模块，未重新开启O1/O2/O3或改变旧/2、新/3字段与版本要求。新的hook命名不提供来源认证、Job或权限。

## 实际验证与失败历史

全文读取根18正常check stdout：TS1125与build通过、ruff通过，pytest最终为 **6 failed /4958 passed /44 skipped**。五个失败是旧C域精确边界测试访问旧facade原空locals时缺capture键；另一项是旧before_projection(self) monkeypatch被新三参数调用破坏。没有修改旧测试或将其删去。根19有界终止不能当作通过；本报告不把它补成成功证据。

本审在8e8只运行定向测试，使用本树 `.venv`、独占basetemp、`-p no:cacheprovider`、禁pyc：

- 原五个C域精确边界及one-less测试；
- 原projection hash ticket先于三摘要委托的monkeypatch测试；
- 新directsteps四个真实晚期fault测试。

实际 **10 passed /88 deselected /0.87s**，exit0/no timeout/stderr0。完整argv/cwd/environment overrides/head、141 sourcesBefore/After、stdout/stderr见 `01-compatibility-and-late-faults.*`；实际D完整事件在 `01-fee-events/`。原C边界费用和safe traceback locals断言、晚期fault对PV及结果引用的断言均实际通过。没有重跑full check，也未跑GUI/网络/模型/服务。

根20的98专项和21完整check由根维护；本报告以自身10项运行及固定差异为直接复核证据，不在21完成前宣称完整check通过。预算上界仍由预算独审判断。

## 交接边界

只新增 `docs/reviews/I05/profile-directsteps/independent-origin/delta-8e8b512/`。未改产品、旧测试、其他过程、AGENTS/环境/Goal，未stage/commit/branch。过程脚本从创建即 `.py.raw`，原始输出及metadata保留。新增报告与清单显式取消ignore做文档格式检查。成员清单及写锁完成后停止写入。
