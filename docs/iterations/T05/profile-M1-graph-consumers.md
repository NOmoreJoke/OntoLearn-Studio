# M1 两规则图与13C实际消费者观察

本轮执行真实固定6c组件，未修改143项采用输入。最终测试候选`2ce39f011282b6fdce5e6870610529cff1458fdd`；完整检查前端1125 passed，Python4 failed/4899 passed/44既有skipped，整体exit1，不能收为全绿。15个实际场景为9项规范相符、4项确定规范差异、2项入口/政策pending；另1项纯输入完整性测试。新增专项没有skip/xfail，不以pytest通过数代替消费者规范状态。

新树`.worktrees/T05-profile-M1-graph-consumers`，branch `feature/weekly-t05-profile-m1-graph-consumers`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，143逐path采用为`8fccf64c99e42e03003f90d799a58db8ecc97df6`。139固定I05源与四个9333原件均核Git/current/bytes/SHA。受控145=143只读+2新增，实际base delta136（采用134，另9同base）；base AGENTS保原字节，最新操作15852B/78df与common17891B/e437携带全文核同。

唯一新源码为5962B纯输入fixture和`packages/engine/tests/test_profile_M1_graph_consumers.py`。fixture完整五图逐byte同9333；只执行前两规则图，另三direct图保留输入且等待真实新carrier，没有为三图加skip并声称覆盖。旧数学051ae4/e0ee、057d合同树与三ZIP未改、未重测；Goal状态不动。

## 真实规则链与保真

fixture binder仅在新test内按真实schemaVersion1输入构造原TermInput/RuleSpec，记录原condition/conclusion ordinal及pointer/hash。它不是T01保存定义binder，也不提供Job/issuer/origin。Catalog来自真实ontology，独立golden只在计算后断言。每项调用prepare_profile_material→execute_admitted_profile_job→restore_profile_result，RestoreExpectation/OriginalAllocation仅绑定该次实际产物及前像，没有手造17L或自签来源。

M1-complete-heads实际两个originalMatches、一个true firing、三个head occurrence与两个RDF结果均逐字段相符。完整when/bindings、true两侧原lexical/source及Number、ruleId/definitionOrdinal、原定义digest与每head实际source、全部basis/evidence/native/restored结构均核。外7/内15/child11完整类型结构相等，不只比hash；原L/预算usage与实际C/R receipts/费用事件、真实payload/rows/catalog/输入/source/definition前像归档。

M1-false-then-error真实执行两次比较：先false，再comparison/index1类型不匹配，原condition索引3。原私有diagnostic与四字段public adapter均严格断言；无payload/batch/heads或restore成功。测试透明观察器只调用原函数并记录真实Boolean/异常，不替换输出；其调试call记录不属于持久false ComparisonEvidence，也没有从golden回填false typed值。

返回物料的retention责任保留；逻辑live零不代表物理释放、H租约、容量或性能通过。query/SHACL原API没有C/R receipt，不编费用L；实际入口阶段、Validator.run次数和原报告独立记录。

## 13个C格实际分层

| 状态             | ID                          | 实际结果                                                                                                   |
| ---------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 规范相符         | C-query-numeric-promotion   | 原query真实numeric promotion返回s                                                                          |
| 规范相符         | C-query-type-error          | 原query FILTER错误剔行，正常空rows                                                                         |
| 规范相符         | C-datatype-exact            | 真正Datatype违规报告                                                                                       |
| 规范差异，测试红 | C-langString                | check-shapes前门UNSUPPORTED_DATATYPE；Validator.run=0，无正常report                                        |
| 规范相符         | C-count-term-identity       | 实际2个value node，MaxCount报告；未编可选value                                                             |
| 规范相符         | C-in-term-identity          | 原RDF term身份In违规报告                                                                                   |
| 规范相符         | C-inclusive-numeric         | 原Validator等界conforms                                                                                    |
| 规范差异，测试红 | C-inclusive-nni             | numeric-only inclusive名单INVALID_SHAPE；Validator.run=0                                                   |
| 规范差异，测试红 | C-inclusive-dateTime-equal  | 同上；不能把前门失败当conforms                                                                             |
| 规范差异，测试红 | C-inclusive-dateTime-before | 同上；不能声称MinInclusive report发生                                                                      |
| 规范相符         | C-inclusive-type-error      | 真正普通MinInclusive违规report                                                                             |
| pending          | C-inclusive-date-entry      | INVALID_SHAPE，Validator.run=0；原core-only与date extension两条件预期均保留，政策未采用                    |
| pending          | C-illtyped-entry            | parse-data INVALID_LITERAL_LEXICAL，Validator.run=0；规范Datatype报告与当前前门分开，未声称Validator已运行 |

真正5项SHACL report的conforms及完整focus/path/value/sourceShape/component/severity，均同时比原API输出和原Validator RDF报告；原report.nt/report-text、data/shapes物料完整保存。report blank-node ID保实际原件，断言按结构匹配，不制造固定ID或可选value。两个query核完整type/variables/rows。规则比较器没有替代query/SHACL，消费者没有额外reason。

四项确定规范expected保持原只读golden，不因6c前门失败放宽。已回交root路由原I05：`semantic.py::_shapes`的datatype whitelist及inclusive whitelist。143仍只读；需原owner给新获准供方后组合验证，不能在本树改产品或改goldens取绿。date/illtyped仍按根明确政策等待，并不是永久unsupported通过。

## 首失败与验证原件

首次6b0d5f测试因独占basetemp父目录尚未建立而15 setup errors/1passed，0实际场景；完整双流、argv/cwd/env/exit及0观察ZIP保留。随后5155ab首实际运行完整15观察，但新test观察器错挂不存在的CaptureLedger.finish，使两规则图停binder；同版其余13C实际完成。改为真实transferred/failed方法，仅新test修正；a1b85f专项4failed/12passed、两规则图通过。随后加强raw Validator完整字段/真实2value nodes/每head source/定义digest，固定499658，仍仅原四产品入口红。

独立agent发现两处测试覆盖缺口：bindings转dict后没有断言顺序；错误location未完整核side/span与标量类型。实际原件正确，但原断言不足。499658完整检查结束并封存后，仅修改新增test：显式断言bindings tuple顺序，完整诊断/public error经plain严格比较，核两次实际call的完整InputLocation与operator；加真实测试/输入源码SHA元信息。固定2ce39，局部两规则测试2 passed；独审复核diff及21成员原件，确认两P2关闭，无新增P1/P2。记录由T05依据agent回复整理，不冒称外部双审。

首次lint、lint fix、后续长行失败及其修正均保双流，不倒写历史。最终lint/格式已通过；12个归档源核验通过。499658完整normal-isolated为前端1125 passed/22 files，Python4 failed/4899 passed/44既有skipped（142.69s），仅上述四产品入口红；lint/format/types/build通过。首次normal-check因补显式basetemp在Python前停止，仅终止验证归属的本次子树，exit -15，不报通过。最终2ce39完整检查另行保存final-normal，不用499658证据冒充补强后候选。每run独占artifact/basetemp，结束即ZIP冻结，包含原command双流和全部逐操作原件，逐member byte/SHA/CRC验证；不轮转覆盖。具体actual index与失败处置见本轮reviews目录。

所有检查限无窗口组件；无GUI/Electron/e2e/native/HMR、凭据、模型、网络服务或付费。正式Job/Store/worker/selected、directsteps、原83/E5/repair及父M1/指定双外审/CI/目标OS真人/合并门继续原边界。本轮完整测试实现和失败证据已可审查，产品四入口待原owner修复后才能收绿。

## 最终交付指纹

2ce39的final-normal完整检查为前端1125 passed/22 files，Python4 failed/4899 passed/44既有skipped（142.51s）；lint/format/types/build通过，四个失败ID与前版相同。新test 28706B / SHA `3ee46c9c633cdb611cf75a6fae3148b6abad8828ebf55327138549ad7cb8811c`；纯输入fixture 5962B / SHA `dc57792093204d85c2e54471c271965c40b7ccd7e5cd6f4614173e1497c332f6`。

最终原件`final-normal-originals.zip` 1307902B / SHA `06eb119efb8e6ec44b903723c1a4f7d6f3fc25d657b9f14b5f0b35ec51321124`，79成员/15观察。独审逐member byte/SHA/CRC复核，绑定2ce39源码摘要；最终限定接受本轮测试与证据交付，两P2关闭，无新增P1/P2或测试证据阻断。4产品问题与2pending保持开放。

完整145项指纹见`controlled145.json`；旧499658版本另存。所有命令双流及退出码见`command-ledger.json`，历次ZIP逐member验证见`archive-ledger.json`，四个完整反例见`product-counterexamples.json`，首失败与修正履历见`failure-dispositions.json`。`delivery-manifest.json`仅排除其自身精确路径，覆盖本轮全部过程文档、日志和ZIP；receipt绑定测试候选，最终过程commit另在总控交接消息给出，避免自引用hash。
