# shape-entry 固定源码独立审查

结论：固定 `3bd19e347051627242197f15fce712c9c9dd6b8f` 在本窗口范围通过。未确认需修复的 P0/P1/P2 阻断。四个 consumer-C 原输入已通过真实 I05 前门并各执行一次真实 Validator，完整 conforms/结果行与未修改的固定 golden 一致；非法、date、illtyped 及邻例边界保持。

该结论来自本窗口固定源码和实际证据，不借前轮 producer/fullview 或方案审结论。它不接收整个 I05、T01 Job/selected、DAG/directsteps 或 OS/真人验收；后续采用仍须按真实新 ref 精确组合及现行门禁处理。

## 版本、授权与实际范围

- 唯一树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-shape-entry`；branch：`feature/weekly-i05-profile-shape-entry`。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；adoption：`6e64311957a43b725bfb3e5da88c8df29c000b87`；产品：`3bd19e347051627242197f15fce712c9c9dd6b8f`。
- 全文读取 `inputs/` 的窗口、最新 AGENTS、共用指导（含完整第九节及最新责任交接）；完整解析并逐条核固定输入与 candidate。窗口 3205B/SHA `721735d16c406b2b34b3192348bf5721c7a6d7c1c47a7629e25c7696bd36c3a9`；固定输入 58397B/SHA `c7b28fc8257ce1e31ba8ffdd4900d6f0c8dc48529a7b9e137e182d2d758cad59`。
- 142 控制项逐项核当前字节=固定 Git=manifest bytes/SHA；140 只读等 adoption；初始 141 项逐 sourceRef/Git/bytes/SHA 等 adoption。base→product 实际 133 项差异，9 项同 base；adoption→product 恰为下表两路径。
- 完整静态清单、授权原件 hash 和 AST 结果保存于 `static-input-manifest.json`。

| writer                                                       | 实际 bytes | SHA-256                                                            |
| ------------------------------------------------------------ | ---------: | ------------------------------------------------------------------ |
| `packages/engine/src/ontolearn_engine/semantic.py`           |      54174 | `24f3c57f7995a7f4b901599e6f7837eb328355459f151e811dce01f6b38a173d` |
| `packages/engine/tests/test_semantic_profile_shape_entry.py` |       7211 | `38bc7a4074e183205f55fdb0a74e6933a505f9ff021fe24f5895d296ab725324` |

固定输入原件未改：consumer-C-inputs.json 为 8505B/SHA `eeab821ccd71d55eed425a08b34d07648e623c0aa34eb2eabf66b839bbb426f6`，consumer-C-goldens.json 为 8163B/SHA `c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440`。

## 源码与 AST 证据

`semantic.py:1205–1294` 的 `_shapes` 仍先 `_terms(graph, shapes=True)`，保 NodeShape→PropertyShape、IRI、路径、列表、字段位置与单值结构检查。实际代码差异只有：

1. 第 1260 行，`sh:datatype` 的本地候选集合为原 `_DATATYPES | {RDF.langString}`。
2. 第 1269–1283 行，inclusive 参数的本地 Literal datatype 集合新增 `XSD.nonNegativeInteger` 与 `XSD.dateTime`；`not isinstance(o, Literal)` 和 `o.ill_typed` 门均保留。

独立静态脚本从两个固定 Git blob 解析 AST，逐顶层节点比对，唯一变化节点是 `_shapes`。再只向旧函数施加上述两处精确 AST 集合变化，所得完整函数 AST 与新函数相等。因此不是仅靠 grep：全局 `_DATATYPES`、`_terms`、query、rule/profile core、`check_shapes` 等所有其他代码 AST 相同。实际文本 diff 同样只有两处集合及其换行，无额外 import、delegate 或资源/公共错误码改动。

全局 `_DATATYPES` 虽原已含 `xsd:date`，inclusive 本地集合仍不含它。由此修复没有选择 date 运算扩展政策，也没有放宽 data 的 illtyped 前门。`_terms:83–92` 的词法、datatype 与非有限数门未变；原外联拒绝 `63–67` 未变。`check_shapes:1297–1342` 仍先复制有限内存图、重走 `_terms/_shapes`，再构造原 pySHACL Validator，options 仍为 inference none、advanced/use_js/iterate_rules/sparql_mode false；未绕过 `_shapes` 直喂 Validator，未用 rule Calendar 比较器或伪造 report。

## 四个原输入的实际完整结果

独立 `consumer-c-probe.py.raw` 只把原 fixture 的 dataTurtle/shapesTurtle 传入 `parse_turtle` 与 `check_shapes`。Validator.run observer 仅记录次数并调用保存的真实原方法，未供应任何结果。golden 在实际计算完成后读取并用于断言。完整原始 report 在 `03-consumer-c.stdout.txt`，含所有 13 个 consumer-C 原格的实际结果/入口错误。

| 原 ID                       | Validator.run 次数 | 实际完整结果                                                                               |
| --------------------------- | -----------------: | ------------------------------------------------------------------------------------------ |
| C-langString                |                  1 | conforms=true，violations=[]                                                               |
| C-inclusive-nni             |                  1 | conforms=true，violations=[]                                                               |
| C-inclusive-dateTime-equal  |                  1 | conforms=true，violations=[]；`01:00+01:00` 对 `00:00Z` 的上下闭界均成立                   |
| C-inclusive-dateTime-before |                  1 | conforms=false，恰一条 MinInclusive 结果，value 为原 `1999-12-31T23:59:59Z` typed dateTime |

最后一格精确核对整行：focusNode=`<urn:m1:s>`、resultPath=`<urn:m1:p>`、sourceShape=`<urn:m1:shape>`、component=`<http://www.w3.org/ns/shacl#MinInclusiveConstraintComponent>`、severity=`<http://www.w3.org/ns/shacl#Violation>`，以及完整 typed value。没有只检查 conforms 或结果条数，也没有把少一秒的输入补造为 offset 等值。

独立原13格探针同时核：

- C-inclusive-date-entry 仍为 `INVALID_SHAPE`、Validator=0；不采用 golden 中两个条件 date 分支中的任何一个作为实际成功。
- C-illtyped-entry 仍为 `INVALID_LITERAL_LEXICAL`、Validator=0；不冒称发生了普通 SHACL Datatype 结果。
- C-datatype-exact 仍因 int/所需 integer 的 datatype IRI 不同给完整 Datatype 结果；C-count-term-identity 保不同原 lexical term 的计数结果和 value=None；C-in-term-identity 保原 `"01"^^integer` 的 In 结果。
- C-inclusive-numeric 仍 conforms=true；C-inclusive-type-error 仍为普通完整 MinInclusive 结果，value 保原字符串。query numeric-promotion 和 FILTER type-error 的原 rows 也一致，二者没有执行 Validator。

这些结果区分了 shape 入口、query 行选择和 SHACL 普通验证结果，没有将 rule 私有数学语义替换进去。

## 新测试真实性与边界反例

全文读新增 183 行测试。测试模块读取独立 input 与 golden 原件，但 `observe` 的生产参数只有 input 的原 Turtle 字符串；expected lookup/比较发生在真实调用后，golden 没有进入 parser、Validator、输入改写或结果构造。第 32–44 行的 observer 委托原 Validator.run，未 monkeypatch `_shapes` 或 `check_shapes` 返回值。第 65–76 行只是六字段名称映射；第 79–103 行比较 conforms 与完整有序结果行，没有丢 value/sourceShape/component/severity 或容忍额外结果行。golden 的 valueExpectation/reason/currentEntryGap 属解释元数据，不是伪造产品输出。

本树自有 `.venv` 定向 pytest 实际 26 passed / 0.10s，exit0、timeout=false、stderr0。独占 basetemp 且 `-p no:cacheprovider`；环境和完整 argv/双流/142 项 sourcesBefore/After 保存在 `02-pytest.json` 及双流；逐例实际输出还在 `02-pytest-reports/`。

被实际否证的边界包括新测试第 118–137 行的非法 nni（负数/坏词法）、非法 dateTime（月/词法）、无类型 inclusive、date inclusive、未知 datatype、非 IRI datatype、非法 count、非 Literal bound；第 140–154 行的重复 path、重复 target、未知约束；第 157–176 行的 nni 零/闭上界与 data/shape 两侧 external import。非法路径均在 Validator 前拒绝。新增测试没有改旧输入/旧 assertions；140 只读中所有旧测试逐字保全。

独立13格脚本也是本次真实运行，exit0、timeout=false、stderr0，前后142项源码 hash 均保持。它与26个 pytest 有重叠，不把它们相加成39项独立验收，也不把定向结果代替全仓回归。

## 首失败与根运行证据

读取作者原四红的四份逐格 report：langString 为 UNSUPPORTED_DATATYPE，nni/两个 dateTime 为 INVALID_SHAPE，四格 Validator 均0。核原 run 的142来源 before=after，唯一不同于新候选的是 semantic.py 的旧53978B/SHA `5d7413e6ed09f3b62958c6840db499722f2ef7cf0ede1a22415bdce64572f68e`。原 exit1、原 stdout/stderr 与原报告未改写。

作者的 `02-shape-special` 虽执行时 Git HEAD 仍为 adoption，其142实际源字节均匹配最终产品，exit0/26 passed。没有仅凭 HEAD 把它误判成旧版通过；对应来源核验保存在 `author-source-binding.json`。

根的 `04-normal-check` 已实际完成，本审全文读其12987B stdout 和元数据：lint/Prettier/typecheck、22文件1125 Vitest、vite build、ruff check及239文件格式检查、pytest **4913 passed / 44 skipped**，exit0、timeout=false、stderr0。其142项 sourcesBefore/After 逐项等固定候选。44 skips 如实保留，不宣称全4957项均通过。`05-verify-sources` 亦 exit0、timeout=false、stderr0，实际核12归档源，142来源核同。未重复根的这两个正常命令，也不将它们标为本审独立执行。

本审自身的首次静态辅助命令使用系统 Python3.9，遇 `zip(strict=True)` 不支持的 TypeError；未执行产品、未写 static manifest。已保留工具返回完整 stderr 为 `00-static-first-failure.stderr.txt`，并在 `01-static.json` 明确记录初次 argv/原因；改用本树 Python3.12 执行保留的 static-review.py.raw 后成功。没有为消除辅助环境失败而修改产品或测试。两次实际产品定向运行均首执行成功。

## 限制与交接

本审只写 `docs/reviews/I05/profile-shape-entry/independent-review/`，脚本从创建即 `.py.raw`，不增加被全仓 ruff 当作产品源的 active `.py`。无产品/测试/旧过程/AGENTS/依赖/环境/Goal 修改，无 GUI/native/模型/网络服务、stage/commit。新增文档和 JSON 使用 existing Prettier 显式 `--ignore-path /dev/null` 检查；`04-document-format.*` 保留首次 exit1（仅01-static.json元数据格式），其原字节保存在 `01-static.json.raw`，同名 `.json` 是格式化派生，不声称原始运行日志被重新生成。最终显式检查保存在 `05-document-format.*`，实际结果据该记录。

通过绑定精确产品 ref、semantic.py 与新测试 hash、完整142来源，以及上述真实运行。没有穷举全部 SHACL 或 datetime 词法域、没有测量容量/性能提升，也没有接入 Job/worker/selected 或消费未批准跨树 WIP。完成本报告与证据 manifest 后停止写入；任何实际候选变化须按新固定 ref 评估必要复核。
