# I05 私有观察投影规范：独立 R1

结论：**Fail，需修订后按新 candidate 做 delta 独审**。固定 37 项的完整值、来源独立性、条件式 A1 提案和安全字段结构总体可追溯；存在 3 项 P2：安全回退仍可输出非白名单 harnessStage、BNode 小例比较与本规范 RDF language identity 相冲突，以及两个前门 ID 的实际 API/显式政策入口登记不完整。另须补足跨输出字段共用 BNode 双射的明确比较域。没有发现须把产品运行状态改绿的证据；本次没有产品运行。

这是对固定设计候选的审查，不能外推正式 I05/T05、whole-H、source/package、费用、capture、Store/Job、CI、两 OS 或指定双模型验收通过。未修作者文件、输入、schema、模型、自测或保护 AGENTS；未 stage/commit、切分支、push、操作其它树或外部应用。

## 固定对象、独立性与证据

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-observation-projection-spec`。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- candidate：`dd3e659e9214481700275afb3f3188891e42359d`，18 文件。
- process/实际审查 HEAD：`6b665455a4cb88a9744c1b8d67573c5adf0c95f6`，仅后加 candidate receipt，共 19 文件。
- 启动实际 `git status --short` 只有 ` M AGENTS.md`。AGENTS 为 15852B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，核对一致且未 stage。
- manifest 实核 3977B / `6900517c540f1d15b0d105cfe0cd48c32e71bc42e64f174ee12530cc5f578be2`；receipt 实核 5063B / `a7d221a2faa0dd2b1a924b4e9591c6c6e5165a2c978d0e68eb805765d691238d`。
- 19 文件 current=process Git bytes；manifest/receipt 所列 candidate 文件 current=candidate Git=bytes/SHA。base→process 只含两个授权 docs 前缀；manifest 排除自身/后加 receipt，不存在自哈希循环。

本审者为全新独立上下文，先全文读外控 design-window、setup-proof 和新树 AGENTS，再读完整 19 文件。大型 JSON 按完整值读取；重复对象用逐字段相等核验关联已读原值，未以摘要、数量或 schema 形状替代完整值。`pure-sources.json` 的 37 observations、19 datasets、37 externalIndependentOracle 条目另与固定 Git 纯 JSON **全字段递归 exact** 核验；原资产 inventory 为 417 observations/320 datasets。

来源账 25 项 bytes/SHA 独核通过。限制源全文 bytes 只用于 Git/hash；实际解释/展示仅获准行和声明片段，没有读取产品计算/解码/投影算法。`literal-excerpts.json` 全部行与固定 `6891a5842302859a531cf82767c5a482417bc274` 对应行一致；两份 `.raw` 的源文件 SHA、逐声明 fragment bytes/SHA 与 API 参数声明经限定片段 AST 核对一致。没有执行 AST 表达式、旧 helper/tests、新 probe/generator、产品或第三方库。

已核准的来源层级仍分开：`ee2b30a2dad35b2d395f9c735aff80371ab41110` 纯合同；`3d8f4ee912f41bd03388322d29a9bfc0e7defe85` 外部独立数学和 pending；6891 局部旧预登记断言/声明；本候选新增 serializer、F1/R1/D1/O1 技术提案。没有把 sourceRefs 当 expected 来源、constructor 默认当实际首错、异常集合当每 ID 可接受集合，也没有从原产品 actual 生成 golden。

证据在 `r1-proof.json`、`r1-check.py`、`r1-counterexamples.py` 和 `r1-*.stdout/stderr.txt`。命令分别记录 argv/cwd/实际 exit 和双流 SHA/bytes；自测及反例另保完整分离双流。只为核 byte 的固定 Git blob 不复制整份受限产品算法到报告目录，原件以完整 ref/path 加 byte SHA 定位。初始阅读工具个别大输出发生展示截断，随后用有界分段和精确重复值核对补读；没有把截断显示当完整命令原件。作者原两 KeyError 仅按已提交 tail/chunk/实际 exit1 记录审查，不追认其缺失 stdout 或产品运行。

## 需要修订的发现

### R1-01 [P2] Unknown 安全回退未封闭 harnessStage

位置：`model.py` L192–206；`spec.md` L78、L87、L91–93；`schema.json` 的 rejection.harnessStage。

`safe_projection` 会先用 schema 拒绝非法 stage，但 fallback 调 `unknown(harness_stage)` 时原样放回该值。独立输入为合法 detached diagnostic、`harness_stage="/private/r1-sensitive-path"`，实际返回的 Unknown 包含同一路径，`complete=false` 且 `validate(output,schema)=false`。这使被描述为安全回退的模型产生自身 schema 不接受、且带自由路径文本的终态；`unknown` 直接调用也有同一问题。反例保存在 `r1-proof.json` 的 `counterexampleUnsafeHarnessFallback` 及分离双流。

此处没有证据证明真实受信调度器会传错 stage，因此不是已发生的产品泄漏。但候选声称对未预登记字段/值安全回退，尚未将“stage 已经受信且在白名单”定义成被校验的函数前置条件；自测只使用合法 stage，未覆盖这个入口。

最小 delta：在 detached 模型与 adapter 合同中显式先校验 exact-string 白名单 stage；非法值不得复制进任何 JSON。可以发固定安全的采集失败信号，或采用 owner 接收的固定保留 stage，并同步 schema/version。若选择在序列化之前以固定字面异常拒绝非法调度状态，须明确 collector 的 incomplete 处置，且异常内容不得带输入值。加入非字符串、路径/URL、未知 stage 的反例；断言每个返回 JSON 均 schema 合法且不含该输入文本。无须修改公共 ErrorFrame 或 37 项已登记目标。

### R1-02 [P2] BNode 图同构小例错误地区分 language 大小写

位置：`model.py` L262–281，尤其 L274/L277–279；`spec.md` L31–33；`selftest.py` L217–230。

规范明确图身份中的 language 只 casefold，raw occurrence 保原文。`graph()` 确实如此；`graph_isomorphic()` 却直接 canonical 整个 typed term，未做同一身份归一。独立 shape-list 小例为 `_:a rdf:first "hello"@EN; rdf:rest rdf:nil`，另一图仅将空白节点改成 `_:p`、语言改为 `en`。两图按本规范 RDF identity 同构，模型实际返回 false。删除尾 rest 边仍应 false；仅改 BNode 且保 EN 时模型返回 true，故反例定位于语言身份处理，而非缺少映射或小例超过 8 节点。

最小 delta：只在图身份域把 literal language casefold 后做 BNode 双射比较；继续保留原输入/证据序列语言原文、typed datatype 和 numeric lexical。加入该正常图同构例及删除尾项、节点折叠、datatype/int-vs-integer、`01`/`1` 的反例。不能通过把 raw occurrence 全量 lowercase 修复。

另一个必须明确的边界：当前函数仅接收一张图，`matches()` L257–259 对终态做纯 exact；提案没有定义 typed graph、N3 evidence、query cells、SHACL sourceShape 等位置如何共享**同一** BNode 映射。独立检查确认：两个分别同构的图片段可以分别把同一个左节点映成右边 p/q，合并后不存在整体双射。后继比较器须先列完整身份域并在该域共享映射，再各自精确比较有序 occurrence；不能在每个 field/row 独立调用同构。当前 37 expected 没有 BNode，故不声称已发现其某项数值错误；这是窗口明示 BNode 边界未闭合。

### R1-03 [P2] 两个前门 ID 未登记批准的实际调用入口及政策映射

位置：`cases.json` L10474–10480、L10520–10529；`coverage.md` 对应两行；`spec.md` L102–103、L134。

`shape/front-2` 与 `integer/other-datatype-1` 都登记 `api="semantic.validate"`。但获准 `ee2b30a2dad35b2d395f9c735aff80371ab41110:docs/iterations/I05/source-package-parity/contract.md` L52–53 分开规定：shape 是 `parse_turtle(data)` + `parse_turtle(shape,shapes=True)` → `check_shapes`；integer-policy 是 `validate_shacl_text(...,data_policy=...,range_policy="legacy")`。后者固定原参数为 `dataPolicy="integer-illtyped-report-v1"`、`rangePolicy="legacy"`，当前文件没有从 input 参数到实际 Python 调用参数的精确映射，也未声明新 `semantic.validate` wrapper 的签名/版本/兼容与调用图。

因此完整 code/null 目标虽已写出，后继 consumer 仍可能调用旧默认 strict 入口或不同 shape 路径，在不同行为下“验证”同一个期望。这里不通过读未获准函数体来判断某个函数是否存在，也不把 F1 的新首序本身判为不允许；缺陷是设计没有给出其所声称的精确 API 目标。

最小 delta：保留原 input parameters 和 projection hash，另登记明确 invocation/stages：shape 的两个 parse 参数与 check_shapes，integer 的 `validate_shacl_text` 及 exact `data_policy/range_policy`。若确要引入新 wrapper，则明确其新版本签名、owner、与批准入口的分派关系和 pending，并在逐 ID 表及 coverage 同步。`spec.md` L103 的“integer 族”应收紧为已批准 **data object 的 exact xsd:integer ill_typed**；xsd:int/nonNegativeInteger/decimal 与 shape 侧均不随之宽化，不能借此修改 Q6。

## 完整 37 项审阅结果

以下“值核对”只表示独立数学、固定输入、提案目标和静态关系核对，绝不是运行通过。每项已核全部 keys/type/null、空数组/末项、排序、多重性、完整输入参数及 sourceRefs。legacy 数量栏按 `rdfs/rules/rdfsEvidence/evidence`；拒绝的 null 栏完整为 classification/stage/slot/domain/ruleId/location（有非 null 时明确列出），另 `partialView=report=null`。13 正常、24 拒绝：10 legacy 正常 + 3 scope 正常；1 unbound + 14 restore + 1 DAG text + 7 前门 + 1 implicit guard。

| ID（cases 起始行）                                    | 完整值/关系核对结论与依据                                                                                                                                                                                                                                                        |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| turtle/front-5（7）                                   | SemanticError/INVALID_TURTLE，parse-data，六诊断尾字段 null；坏空格 IRI 的 F1 新词法优先提案，原实际 parser/IRI 首错 pending，旧竖线断言没有外推。                                                                                                                               |
| rdfs/type（53）                                       | 1/0/1/0；x:B 的两叶为 x:type:A 与 A subclass B；原 typed/premises/depth1 全保。                                                                                                                                                                                                  |
| rdfs/domain-depth2（288）                             | 2/0/2/0；x:A 两叶，x:B 三叶，第二 witness 指向 ordinal0，depth2；没有只保直接两前件。                                                                                                                                                                                            |
| rdfs/range（688）                                     | 1/0/1/0；y:C，两叶包含 range 公理与 x p y，顺序完整。                                                                                                                                                                                                                            |
| rdfs/subclass（919）                                  | 1/0/1/0；A subclass C，两叶、两个有序直接 premise。                                                                                                                                                                                                                              |
| rdfs/cycle（1154）                                    | 8/0/8/0；六 subclass 新边含 A/A、B/B、C/C 与 x:B/x:C，两层 witness、所有 leaf union/ordinals 一致；没有新增一般自反公理。                                                                                                                                                        |
| rdfs/domain-first-witness（2512）                     | 1/1/1/1；u:C 选 p/domain/C 与 u p a，未偷换 u p b；observe 的 when 为 u:C，basis 回溯两叶。                                                                                                                                                                                      |
| rdfs/range-first-witness（2913）                      | 1/1/1/1；u:C 选 a p u 与 p/range/C；observe 完整 basis 一致。                                                                                                                                                                                                                    |
| legacy/no-rule-feedback（3314）                       | 0/1/0/1；仅 equipment/001 HighRiskEquipment；四位置 inputs、四叶 basis；完整 `RULE_CHAIN_UNSUPPORTED:R-next` 新格式接收提案，R-next 未反馈。                                                                                                                                     |
| legacy/multiple-matches（3933）                       | 0/1/0/2；A01/A04 两个完整四输入匹配，单 head 图而两条 evidence；没删重复结果 occurrence。                                                                                                                                                                                        |
| legacy/repeated-variable（4838）                      | 0/1/0/1；仅 c p c 满足 ?s 两位置，完整 c:Self evidence；a p b 不误收。                                                                                                                                                                                                           |
| legacy/unbound-head（5025）                           | SemanticError/UNBOUND_RULE_VARIABLE，rule-definition，六尾字段 null；独立 oracle/合同本来明确拒绝，不构造第11个正常五字段 DTO。                                                                                                                                                  |
| scope/asserted（5070）                                | facts6/ontology2，reasoning_result=null，reasoningSource=null；6条完整 asserted source、两个 view 摘要相同、query 两行，SHACL true/[]。                                                                                                                                          |
| scope/fresh（5753）                                   | facts9/ontology3；unit Pump/Equipment/HighRiskEquipment 与一条派生 subclass；完整五字段含3条 rdfs/3条 basis、1条四前件 custom evidence；9 selectedFacts、ruleIds、derivedAxioms、三内容摘要与两 view 摘要独立复算一致；query5行、两条 minCount 违规六字段均全，value 显式 null。 |
| scope/project（7534）                                 | 与 fresh 的完整 terminal value/query/shacl exact 相同；仍要求同次真实旧 metadata/结果复用、prepare1/project0 hooks 及输入不变，不能由 JSON 相等自证。                                                                                                                            |
| scope/missing-source（9315）                          | SemanticError/REASONING_SOURCE_REQUIRED，scope-provenance-gate，六尾字段 null；新 F1，不能靠别的三个 scope 码推实际。                                                                                                                                                            |
| scope/wrong-source（9363）                            | SemanticError/REASONING_SOURCE_MISMATCH，scope-provenance-gate；旧局部 code 有限支持，新 ID 全上下文与 stage 仍 pending。                                                                                                                                                        |
| scope/missing-result（9415）                          | SemanticError/REASONING_RESULT_INVALID，scope-provenance-gate；旧 absent/incomplete code 支持不等于全部首序已证。                                                                                                                                                                |
| scope/unselected-result（9467）                       | SemanticError/UNSELECTED_REASONING_PRESENT，scope-selection-gate；新 F1 显式 selection 先于 source gate，原 oracle phase 未被冒称旧 actual。                                                                                                                                     |
| restore/fullview/payload-unknown-key（9519）          | 条件式 R1：RestoreFailure/RESTORE_EXPECTATION_MISMATCH/expectation/A1；slot/domain/ruleId/location=null；explanation=false、固定 roots 与原 mutation 未改。                                                                                                                      |
| restore/fullview/tail-source-tamper（9583）           | 同一条件式 exact 终态；保原 source 字节身份与 held expected，不生成 source 值或 budget。                                                                                                                                                                                         |
| restore/fullview/tail-definition-tamper（9647）       | 同一条件式终态；definitions 完整原身份，不重绑 expected。                                                                                                                                                                                                                        |
| restore/fullview/tail-limits-tamper（9711）           | 同一条件式终态；limits 位于被绑定完整 bytes，未推深层原子性或新费用。                                                                                                                                                                                                            |
| restore/fullview/tail-child-tamper（9775）            | 同一条件式终态；末 child 未因比较摘要而豁免，原成功物料完整保留。                                                                                                                                                                                                                |
| restore/explanation/payload-unknown-key（9839）       | 同一条件式终态，explanation=true；不是旧 deep/rebound fixture 的错误 golden。                                                                                                                                                                                                    |
| restore/explanation/tail-source-tamper（9903）        | 同一条件式终态，源/roots/参数全保。                                                                                                                                                                                                                                              |
| restore/explanation/tail-definition-tamper（9967）    | 同一条件式终态，definitions/roots/参数全保。                                                                                                                                                                                                                                     |
| restore/explanation/tail-limits-tamper（10031）       | 同一条件式终态，不以资源错误代 mismatch。                                                                                                                                                                                                                                        |
| restore/explanation/tail-child-tamper（10095）        | 同一条件式终态，不把删尾视为可忽略差异。                                                                                                                                                                                                                                         |
| restore/explanation/dag-depth-plus-one（10159）       | 同一条件式终态；dag/domain-depth2、roots x:type:B 与原 mutation 全保；此 A1 不证明深层 depth 校验。                                                                                                                                                                              |
| restore/explanation/dag-last-premise-forward（10225） | 同一条件式终态；原 forward mutation 未改；未冒称实际深层首错。                                                                                                                                                                                                                   |
| restore/explanation/leaf-rename-all（10291）          | 同一条件式终态；原全链 leaf 改名仍须改变受绑定 bytes，不重签 held expected。                                                                                                                                                                                                     |
| restore/explanation/head-occurrence-1023-15（10357）  | 同一条件式终态；原 dataset/roots/enum 全保；不把当前小 dataset 名称当 mutation 实际到达末项的运行证据。                                                                                                                                                                          |
| dag/turtle-entry（10421）                             | DirectStepsFailure/DIRECT_STEPS_INVALID/input/entry，structured-material-required；其余 null；D1 新提案，旧只给有限拒绝类集合及 reason0，精确类/code 未证。                                                                                                                      |
| shape/front-2（10474）                                | SemanticError/INVALID_LITERAL_LEXICAL，parse-shapes，六尾字段 null；shape nni=-1 的 F1 新优先级，旧 data-gate 不证明 shape 侧；API 调用登记见 R1-03。                                                                                                                            |
| integer/other-datatype-1（10520）                     | SemanticError/INVALID_LITERAL_LEXICAL，parse-data；原 dataPolicy/rangePolicy 全保，nni 不应放宽；API/参数实际入口见 R1-03。                                                                                                                                                      |
| offline/implicit-jsonld（10569）                      | OfflineAccessDenied/EXTERNAL_ACCESS_DENIED，implicit-loader-guard，六尾字段 null；O1 新事件，不把库任意异常伪装 SemanticError；真实 loader/no-I/O 仍 pending。                                                                                                                   |

R1 的 14 项共同前提逐项存在：原生产已完成、真实 caller-held expectation/allocation 不变、独立资源准入成立、实际 mutation 改变至少一个被绑定字节序列。固定顺序 payload→rows→source→definitions→catalog；更早失败要保首错、记 not-reached/pending。本文没有运行 byte mutation dispatcher，故“每项实际改变 bytes”仍是须后继独审/实测的条件，不能拿 14 个相同目标 JSON 当它的证明。

## 20 个作者自测与独立补查

先静态读完两脚本，import 只含 stdlib 及本 detached model，确认不写既有候选；再以指定 Python 3.12、`PYTHONDONTWRITEBYTECODE=1` 实跑，20 方法实际通过。它们通过说明当前模型自洽到其覆盖范围，未覆盖的反例仍可失败。

| 自测方法                                               | 实际覆盖与审查边界                                                                                                                         |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| test_37_exact_ids_and_targets                          | 37 shape/self-exact 及 legacy/scope builder 对照；部分为实现与提案共同构造，单独不能证明独立 expected。R1 另对固定外部 oracle 全字段核验。 |
| test_hand_authored_type_example                        | 独立字面 type 正常五字段，含完整两叶。                                                                                                     |
| test_hand_depth_two_has_all_three_leaves               | 核末 basis 数量和 B；R1 再核全部 premises、leaf union、depth/ordinal。                                                                     |
| test_hand_multiple_matches_preserve_two_occurrences    | 核双 evidence/四 inputs；R1 再核 A01/A04 完整记录。                                                                                        |
| test_evidence_duplicate_occurrence_is_not_deduplicated | 重复 match 保 evidence occurrence。                                                                                                        |
| test_ordered_when_duplicate_positions_survive          | 重复 when 保两个位置。R1 另重复 head 本身。                                                                                                |
| test_normal_cannot_match_any_rejection_or_unknown      | 选定拒绝/Unknown/RESTORE_LIMIT 不能匹配正常。R1 扩为13正常×24已知拒绝=312组合。                                                            |
| test_known_rejections_do_not_all_match_each_other      | missing/wrong-source 与 restore 默认错替代；不接受任意已知拒绝。                                                                           |
| test_missing_and_extra_each_top_field_rejected         | 顶层缺键与 exceptionText extra；R1 扩到1031个嵌套必需字段缺失。                                                                            |
| test_every_nonempty_sequence_tail_is_observable        | 非空数组删尾。R1 独立计423个，另33个空→非空。                                                                                              |
| test_complete_five_fields_and_basis_tail               | 五字段缺失和末 basis 叶删除。                                                                                                              |
| test_when_reorder_changes_value                        | 四输入逆序仍 shape 合法、exact 拒绝。                                                                                                      |
| test_exact_warning_and_unbound_case                    | 完整 warning 与 unbound reason，未构造正常空对象。                                                                                         |
| test_scope_sources_and_four_fields                     | 6/2、9/3、9来源、1公理及 fresh/project value 相等；相等不证明身份。                                                                        |
| test_scope_shacl_null_and_multiplicity                 | 两条违规/value null 与缺省拒绝。                                                                                                           |
| test_bool_not_integer_and_no_untrusted_diagnostic      | slot bool、reason/stage/domain/location/ruleId/extra message 拒绝及合法 harness stage 下回退。没有覆盖 R1-01。                             |
| test_unknown_is_fixed_safe_incomplete                  | Unknown 完整固定字段、complete=false、不能 match；direct reason/class 错配拒绝。                                                           |
| test_strict_json_duplicate_and_nonfinite               | 重复 key、NaN、Infinity 拒绝；未运行第三方 JSON Schema validator。                                                                         |
| test_lexical_type_language_and_escape_preserved        | integer01/1、int/integer、转义、raw EN 与 null/空字符串摘要不同。未组合测试 BNode identity，所以漏 R1-02。                                 |
| test_global_blank_node_bijection_and_tail              | 一张图整体重命名通过，删尾/折叠拒绝；未测试跨输出字段共用映射或语言 identity。                                                             |

R1 独立补查实际结果：1031 个嵌套缺字段、423 个非空数组删尾、33 个空数组加项、229 个 null/bool/int 类型混淆均不能 match；312 个正常对已知拒绝替换均不能 match；37 个 Unknown 均不能 match。独立复制 head 和 premise 均保 occurrence。scope 重复同 head 的 source 仍为两条；selected 两 digest 篡改不能 match；往 content source 加 `authority` 被 schema 拒绝。所有 scope view/source 摘要以完整 typed 图/原有序 raw 规则独立复算一致。没有只比较 source=package。

JSON Schema 的定位需要继续保持：只形状与有限枚举，业务关系/逐 ID exact 在 schema 后。当前模型的 exact Python scalar type 比通常 JSON Schema 的数值数学域更窄；本轮未用真实第三方 validator 检验 `1.0` 等数字表示的互通，不能宣称跨实现 validator 已一致。后继若消费标准 JSON Schema，须明确 exact-int reader gate 作为额外谓词，不能仅凭 schema 合法推出 exact-type 合法。此项列为未验证兼容边界，不另计本轮产品缺陷。

## 完整文件与窗口逐项处置

| 固定文件                                              | 审查处置                                                                                                                                                      |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cases.json                                            | 全37完整目标、完整 math/null、参数/hash/sourceRefs、authority/pending/preconditions，逐值及独立来源核验；R1-03待改。                                          |
| coverage.md                                           | 37行、10+1 legacy、13正常/24拒绝计数正确；对应 API 行随R1-03改。                                                                                              |
| model.py                                              | 全文静态及有限执行，见R1-01/02；无产品/第三方导入。                                                                                                           |
| pure-sources.json                                     | 全37/19/37内容对固定0e42/3d8f完全一致，含完整值而非运行 golden。                                                                                              |
| schema.json                                           | 全定义/required/extras、term/graph/legacy/scope/query/SHACL/error whitelist；已登记目标全合法，Unknown与known complete分离；不能冒业务权限或完整runtime载体。 |
| selftest.py                                           | 全20方法静态和实跑；覆盖/缺口如上表。                                                                                                                         |
| spec.md                                               | 全文提案、独立性、字段/排序、F1/R1/D1/O1、owner/兼容/顺序审阅；三发现与BNode跨域边界待改。                                                                    |
| I05-canonical-profile-api-defaults-reference.json.raw | 原字节/hash及两 API 参数声明限定AST核验；rules默认不代表实际省略参数或capture。                                                                               |
| I05-observation-literal-enum-reference.json.raw       | 六声明片段及_DOMAINS依赖 tuple核验；compound initializer保表达式，不执行。                                                                                    |
| author-validation.md                                  | 冻结/首错/未执行边界与本候选一致。                                                                                                                            |
| candidate-receipt.json                                | 5063B/SHA独核、18项current/candidate bytes核验、后加process与自排除一致。                                                                                     |
| literal-excerpts.json                                 | 全限定行字符串对固定Git逐行核验；不执行其中任何 helper/assertion。                                                                                            |
| manifest.json                                         | 3977B/SHA独核；17成员加manifest成18，process另加receipt成19，当前=Git=SHA一致。                                                                               |
| preparation-errors.json                               | 两个实际纯JSON检查KeyError保留；原缺失完整stdout不补造，非产品失败。                                                                                          |
| prettier-check.txt                                    | 原66B/SHA核验，作者已有成功check记录；本轮仅check本R1报告md。                                                                                                 |
| prettier-write.txt                                    | 原326B/SHA核验；只是作者格式写记录，没有据此推产品行为。                                                                                                      |
| selftest-final.txt                                    | 原2405B/SHA核验；R1另跑且保分离stdout/stderr，不要求时间文本相同。                                                                                            |
| source-ledger.json                                    | 25项完整ref/path/bytes/SHA核验；限定片段与额外纯声明授权分开。                                                                                                |
| verification.json                                     | 20方法、实际argv/exit、作者输出SHA与文件一致；静态/纯模型范围未冒充运行。                                                                                     |

窗口要求1（逐ID完整值）：13正常和24拒绝均给出完整提案值，既有数学保持；R1-03使两项精确调用合同尚不完整。要求2（legacy/scope/RDF/N3/BNode）：五字段、完整证据/leaf union、scope四字段及来源完整；R1-02及跨域映射边界未闭。要求3（canonical/harness/public）：三层分开、公共strict四字段不改、Unknown不可match、既返完整阶段保留与无partial view明确；R1-01安全函数回退需封闭。要求4（首错权威）：每组新首序提案及旧待验明确，14项A1有真实准入前提；未外推旧默认、竖线IRI/data-gate/scope码。要求5（schema/模型/小例）：有严格形状、全值与有用自测，独立补查补足尾项/空→非空/多重性，两个可复现模型问题仍Fail。要求6（owner/版本/consumer/oracle delta）：各owner、私有/1、接收顺序、源载体与runtime门保持；R1-03须把必要API delta具体到批准入口/精确参数，不实施产品。

本窗未新增17L、planDigest、budgetUsage、allocation/capture/issuer身份；外部旧oracle中已有字段名仍仅为来源缺口记录，未据其补完整值。未修改Q6/date/外联拒绝、公共registry/authority、原数学或其它WIP。当前仍 `wholeOracleComplete=false`。未获得纯合同的旧source metadata完整编码、真实库首错、实际hook计数、mutation实现、完整上游阶段codec与真实预算/来源继续pending。

修订须保持原输入与既有数学，针对上述最小delta形成新候选并重新冻结；本报告的Fail保留，随后仅按实际变更做delta独审。通过本设计审查也只解除设计缺陷，不替代后继owner接收、隔离runtime票或原正式验收门。

R1 新报告的实际 Prettier `--check` 已通过；JSON 证据由 stdlib 严格解析及字段检查，未调用第三方 JSON Schema validator。最终冻结核验与报告 bytes/SHA 见 `r1-proof.json`，证据本身不写自哈希。
