# directsteps 来源、schema 与生命周期修复复核

结论：**有限通过；DS-O1、DS-O2、DS-O3 和 exact private sink 门已关闭。** 被审最终产品为 `cb2662c2ea4014d3de06194442f462c17eabe23b`，其七个产品源码与修复版本 `ff90092e39c95f0195eb175f46538a8a822dfeb2` 逐字相同。此次没有发现新的来源/schema/生命周期阻断。本结论不替预算审签字，也不把这个组件成功称为正式 T01 Job、selected、权限或整个 I05 成功。

旧 `18908e4` 首审失败报告、三个原反例及完整运行原件均保持原字节；已逐项验证原 write-lock 全部成员。旧失败事实不被本报告覆盖。

## 固定输入与实际差异

唯一树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-directsteps`。base 为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，adoption 为 `78e9cf7f26dc039e99ec6725d7de8a396d1298d2`。

全文读取 `18908e4…ff90092` 的四文件实际差异和所需上下文：157 行增加、26 行删除；未改 resources、restore_budget、directsteps 纯模块或旧测试。随后全文读取 `ff90092…cb2662c` 的测试追加173行，确认仅一个测试文件变化、原35520B为精确前缀、新42828B与独立测试作者 `3404e1ef300a65f155fdb71cafc34b4261fa3ad9` 的 Git 原件逐字一致。旧输入、断言、expected、skip/xfail均未借此次追加修改。

对 `candidate-cb2662c.json` 全141项独立执行固定 Git、当前文件、bytes/SHA 三方核验；与本审先按 ff 路径清单派生的 cb 清单一致。每次产品运行都再次前后逐141核同 cb。完整清单、运行双流成员、旧原件保全记录在 `static-input-manifest.json`。

| 产品源码（packages/engine/src/ontolearn_engine/） | bytes | SHA-256                                                            |
| ------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| semantic.py                                       | 55841 | `d9f246fd169abaad3b0ea6917ac4f0b4f149a7592aa36caa97bc7914524a2d1a` |
| semantic_execution.py                             | 35112 | `26fe08ea57c5c1c5a22d877ed193e052e40f439293ed61fe850fd9806a40f2df` |
| semantic_profile_production.py                    | 19484 | `16bfa048566bcf5c5680bb848871ba3820db166e8c074bccdef1a7e94fb7a3aa` |
| semantic_profile_restore.py                       | 70203 | `1607d2968d2ba76ad0711be446fea7965641fb845226d0e683ac35e5d0f57243` |

新测试 SHA 为 `7bd1b63fbdcaf70d0a78efa4432c1b6091f91d96758988a86b5764b5c5d4b708`。其余受控源码/测试身份见完整清单。下述源码行号适用 ff 与 cb。

## DS-O1 和 exact sink：关闭

`semantic_profile_production.py:305–321` 先核 exact ProfileMaterial、version、四个 exact bytes及上限、exact rules tuple/数量，才做新的 D 递归预界和 bytes 长度累计。`_direct_bound:84` 改为 `kind is tuple or kind is list`，其批准类分派也使用 identity；拒绝 foreign 对象无需执行 metaclass equality。`semantic_profile_restore.py:1057–1060` 在 domain 比较前先核 exact str。

独立原反例复测 `04-counterexample-observations.json`：input_preimage Bomb、definition_material Bomb、nested source hostile metaclass、expectation foreign domain 全部回调列表为空。前三项 reason 实际调用0；均有限拒绝，原生产异常无 cause/context。新增测试的八种材料污染还覆盖另外两个preimage、bytes subclass和TermInput.source内嵌foreign，均独立实测通过。

`semantic.py:385–392` 在任何 closure 工作之前核 `_DirectStepsCapture` exact class。原 ArbitraryCapture 在真实 type/subclass 图上的 candidate 回调为0，抛有限 ProfileReasonError；未借新入口调用 arbitrary sink。固定纯模块未引入新callback接口。

## DS-O2：关闭

`semantic_profile_restore.py:1623–1636` 对每条实际 decoded proof leaf 的三个 saved TripleKey，按原 `i05-profile-proof-leaf/1\0` 加 NUL 连接 TripleKey 的 UTF8 SHA-256公式重新核其 reference；不是按任意 raw alias 改写代表，也不重发 leaf。构造与hash前有明确 D debit/reserve，费用充分性由预算审判断。

原 domain-depth2 一致改名反例再次真实生产：把一个 leaf ID及其全部引用一致改成64个0。**原 expected 不变时拒绝；仅重绑定 payload/rows 摘要后也拒绝 DIRECT_STEPS_INVALID。** 原 input/source witness不变。见 `04-counterexample-observations.json`，含完整生产与接收 D 事件。

这里关闭的是原公式与给定 TripleKey 的局部一致性缺口；hash不是来源认证，本审没有声称重绑定摘要可绕过原expected。

## DS-O3：关闭

`semantic_profile_restore.py:1637–1660` 从已经恢复且经过原16c的 typed firingGroups 遍历全部实际 firing/head：使用全局 firing ordinal、head.index、实际 rule_id、实际 typed when/head经原formatter得到的key，以及原 firing.basis，构造完整 expected evidence。先核总数量，再按既定顺序逐行核六字段 `rule/firingIndex/headIndex/result/inputs/basis`。roots仍只定位通过完整验证后发布的 readonly fullview，没有重reason或补造rule链。

独立 `05-roots-observations.json` 包含八类污染：不存在的1023/15 occurrence、错误target、rule、inputs、basis、缺一行、多一行、重排行。每类分别保持原expected和只重绑定payload/rows摘要，共16次，全部拒绝 RESTORE_INPUT_INVALID。接收中把 `_profile_reason` 设为禁止调用；没有触发。所有这些失败的公开 `_restore_operation` frame，decoder、children、parse_usage、caps、projection、inner_batches、retention、outcome、direct_receipt九项均为None。

诚实产物的两个重复head仍恢复成功；对同一真实目标，roots恰返回 `(firingIndex=0, headIndex=0)` 与 `(0,1)`，完整保留两次真实 occurrence。

## 生命周期、字段和版本的必要回归

`semantic.py:476` 轮末同时清 additions、item、inputs、triple、basis以及捕获 additions 的 append/addition_key 函数引用，之后才结束candidate计数和释放其票。未改变原候选排序键、首插入位置、原L收费顺序或四生成模板。

新增 `_direct_json_size` 只遍历已批准的 exact投影JSON值，不构造另一份wire/tree；生产在 `semantic_execution.py:722–723` 实际投影后核 directSteps carrier，接收在 `semantic_profile_restore.py:1256–1263` 对实际 parsed carrier做同类计数。Reader的D独立预界在 `_restore_operation:1446–1460`、原R begin/parse前；这不替代原R容量。相关预算公式与上界未由本报告签字。

四源码差异没有改变原外7/新内16/child11字段、旧/2与新/3版本派发、旧facade/wire/error、structured-only、PV fresh parse对照或每槽一次原16c。新增evidence核对读取原typed结果，不从allocation/RestoredChild补造原字段，不再reason/compile/evaluate。完整正常投影、四模板/depth2、实际sort首选、旧版本以及roots正例均在定向正常测试中通过。

原实际晚期fault回归仍保留并独立通过，覆盖生产receipt/record与接收record/末child失败，有限异常、PV发行表与公开frame断言没有放松。新 `_validate_explanation` finally也清新建evidence/leaf/hash局部；公开错误从outer handler之后抛出，未把内部formatter/验证异常链公开。没有模拟OS OOM、进程强杀或正式Job取消。

D.failed只改变终态，保守live票可能继续非零；它不等于公开native对象仍保留，也不声称物理GC/RSS/H或authority。原C/R清理合同与D保守计账须分别理解。

## 实际运行与首失败记录

本目录所有成功/失败产品运行均使用本树自有 `.venv`，无网络/服务/GUI/model。pytest用独占basetemp、`-p no:cacheprovider`、禁pyc；完整argv/cwd/env overrides/head和141前后SHA、双流保存在对应JSON/文本。全部相关D ledger完整事件保存在 observations JSON及两个 fee-events目录，没有按摘要替代原事件。

- `04-counterexamples`：exit0/no timeout/stderr0；原O1/O2反例全部按上述预期关闭。
- `05-roots`：exit0/no timeout/stderr0；8污染×2门拒绝，诚实双head和exact sink通过。
- `06-targeted`：**12 passed /65 deselected，0.53s**；原四模板、同轮排序、旧默认、roots完整、晚期故障回归。
- `07-adopted-regressions`：**12 passed /65 deselected，0.18s**；新追加12回归。追加项用纯输入和原leaf公式构造expected，无actual反生；守原外层expected拒绝另由本审独立探针覆盖。

保留两个审计首失败，不将其算成产品成功：最初请求ff时，stdlib运行器在首次产品import前发现test已变，`00-ff-preflight.json`记载前置拒绝，未运行产品、也未冒称ff证据；产品运行随后全部绑定cb。`03-roots`真实失败双流与metadata保留：产品已拒绝污染，但本审误加D.live必须为0断言而失败。修正该探针断言后另存05成功记录，没有覆盖首失败。01早期O1/O2成功记录同样保留；脚本首版另存，不把后改探针冒充原运行源码。

全文读根16正常check双流：TS1125、build通过，随后因独立测试作者过程verify_static.py的ruff13项失败而停止。它不构成产品全check通过。根后续正常check由根执行，本审不重复运行，不以进行中的全check代替本文独立证据。

## 边界和交接

仅新增本独审prefix下delta目录；首189 write-lock全部成员字节不变。没有产品/测试/其他过程/AGENTS/环境/Goal写入，没有stage/commit/branch/模型/服务/GUI。过程脚本从创建即 `.py.raw`，不会作为active产品源被全仓ruff扫描；原始双流和实际metadata保持原样。新增交付文档使用显式取消ignore的Prettier检查，记录另存。

本结论只关闭本来源/schema/lifecycle分工的三项实际缺陷及必要delta。预算独审、根完整check、正式供应/采用/Job/selected等门仍由各自证据决定。完整成员SHA和写锁随报告交付后停止写入。
