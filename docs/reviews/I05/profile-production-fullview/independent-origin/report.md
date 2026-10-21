# f677 实际来源、完整 schema 与生命周期独立审查

结论：对固定 `f677d8a3a642ef7ac7bf389218d43564762bcd9a`，本审查范围有限通过；未确认新的来源、字段保真或受控 Exception 失败清理阻断。此结论不能接收整个候选：根已通知另一独立预算审查存在两项阻断，需修复、重新冻结并按实际 delta 复审。本报告不替预算审、指定双方审查、完整 check、CI 或正式集成验收结绿。

这是实际源码审查，不沿用前一轮方案审作为实现证据。未执行 T01 Job、owned worker、Store/origin 事务、权限、selected query/SHACL 或实际取消/退役/GC 租期链；本组件的成功不证明这些供应已存在。

## 固定输入与方法

- 唯一树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-formal-profile-integration`。
- 产品：`f677d8a3a642ef7ac7bf389218d43564762bcd9a`；adoption：`e4460763890cf9550f359395df83260d75fe2e0a`；base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 全文读取本过程 `inputs/` 的最新 AGENTS、common（含完整第九节与后续责任交接）、9754B 实施授权；对应 SHA 及完整 139 项核验结果见 `static-input-manifest.json`。授权 SHA 为 `2517a322ab2952c1a9444a6963fc790935240a158e0647ce7b2a706461e75031`。
- 139 项逐项以 `git show 固定ref:路径` 对照 candidate manifest 的 bytes/SHA 与当前字节；全部相同。130 非 writer 逐字等 adoption；base→product 实际差异 130 项，另 9 项同 base；adoption→product 恰为授权九 writer。
- 全文读取两个新模块、九 writer 的实际差异、原 parser/执行与恢复相关上下文，以及作者 `producer-implementation/source-and-retention-map.md` 全文（14912B，SHA `9fd73c163b4349520d128a8a42182448b175924c6bd5efadd9f835f49edade4a`）。作者说明仅作为待核主张，不能替代源码或本审运行。
- 使用 Git、stdlib AST/hash 与本树自有 `.venv` 的有界只读探针；未修改产品、测试、旧记录、AGENTS、依赖、环境、Goal 或分支，未 stage/commit。探针从创建即为 `origin-probe.py.raw`，保留诊断原件，不是新增 active `.py`。

| 授权 writer（省略共同 engine 前缀）                 | bytes | SHA-256                                                            |
| --------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| src/ontolearn_engine/semantic.py                    | 53978 | `5d7413e6ed09f3b62958c6840db499722f2ef7cf0ede1a22415bdce64572f68e` |
| src/ontolearn_engine/semantic_execution.py          | 34752 | `f38c39a9c151515cecc820b9ae0ff4bf954e4d61183ce1d5ff64af94d66755ba` |
| src/ontolearn_engine/semantic_profile_input.py      | 39562 | `dde83f0385096e3218632502743e6389ed292beefae477bc279c4683a4260c97` |
| src/ontolearn_engine/semantic_profile_production.py | 10827 | `b8ed430cd5e4c2a8abd31f503042ee5bd3c865b5a6eb9b606a57f1269c757247` |
| src/ontolearn_engine/semantic_profile_restore.py    | 56777 | `00a9c83359a563188f9e10fd871372c5934b1dbac15f7c6fa519deadfab9493a` |
| tests/test_semantic_profile_input.py                | 10986 | `9ae9c026a87d1cb216c93dc39c97592bd95f48b1f2c5d13e46a11dd0b5f65fec` |
| tests/test_semantic_profile_production.py           | 10565 | `4be5e2e780e4b8bb7148e7d2eb4bfa548ddf729ff069963cac3769a89329039a` |
| tests/test_semantic_profile_restore.py              | 38135 | `55fe7ed30642d2e1d75d7ffa4ac66a3144cb30f7fbf832b0762bf8e782f69c0b` |
| tests/test_semantic_profile_restore_limits.py       | 26399 | `1fbca337971be0d46cec100fd12343b2671f1c9cc5dce051c3809779229e44ed` |

所有源码行号均指上述固定产品 ref，源码共同前缀为 `packages/engine/src/ontolearn_engine/`，测试前缀为 `packages/engine/tests/`。

## 问题与具体反例处置

本审范围没有未关闭的已确认 P0/P1/P2 问题；不为凑问题把未供应的 T01 权威或另审预算问题重复登记为本组件逻辑缺陷。以下为实际尝试否证的主张及结果，而非把缺少反例等同于全域形式证明。

| 反例/风险                                                           | 实际核验与结论                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 从 payload/批次反推 allocation，或重跑 reason 后补上下文            | `semantic.py:891–897、913–925、929–943` 在原发生点留定义、disabled、Catalog、同一原 L 对象；`semantic_profile_production.py:210–216` 只把捕获槽转为 allocation。独立探针观察 core/defs/catalog=1/1/1、compile=2/evaluate=1（一个 disabled），每个捕获 L `is` compile 实际 Budget.limits。 |
| 扩展 capture 改写原匹配/数学语义                                    | 去掉新增 capture 参数与 observer 条件语句后，`_profile_reason` AST 与 adoption 逐节点相同。真实匹配、compile、evaluate、false match、head、basis 等计算仍为原体；没有复制第二份算法。                                                                                                     |
| 前像先被篡改，之后仍运行真实 core                                   | `production.py:152–195` 重建并核四组原前像及 native source，才到 `199–205` 执行。现有测试 `test_semantic_profile_production.py:178–189` 对四组 bytes 分别污染且断言 reason=0；parser fake/v999 也在 reason 前拒绝（217–224）。这验证数据一致性，不认证来源。                              |
| consumer K=0 没有自己的基图；语言、None、空串或 occurrence 顺序丢失 | `input.py:895–970` 独立承载 asserted/ontology 两层 U 与 typed D，不依赖 producer。独立探针非空 asserted+空 ontology、`language_raw='ZH-cn'`、四字段 source 的 None/空串精确往返成功；当前并未用它执行 selected。                                                                          |
| fullview 只从旧 RestoredChild 补字段，丢 planDigest 或 usage        | `restore.py:69–107、829–937、1083–1098、1213` 对完整 decoder-native 建只读视图；allocation 只校验独立原 L。独立探针对完整原 native 结构作 exact-type signature，外 7/reasoning 15/每 child 11 均一致，rows 保原 bytes；恢复期间禁止 reason 的 guard 未触发。                              |
| 新 fullview 冻结后，后续 child/结果构造失败却留下半结果             | 独立注入 freeze、projection、batch、result、usage、peaks、live 故障，以及第一槽真实 16c 完成后第二槽失败。均为安全错误、无 cause/context、failed；共享公开 operation frame 的八组新增/大局部全部 None。                                                                                   |
| producer 真实计算后收据/最终 record/转交失败保留 native             | 三处实际晚期 MemoryError 注入均已经过一次真实 core，返回有限 MATERIAL_INTERNAL，公开 producer frame 的 12 个被审局部全 None，ledger failed，无原异常链。                                                                                                                                  |

上述故障为明确受控注入，不是 OS OOM、进程强杀或真实 Job cancellation 的替身。root 转告的预算 hash/固定 bootstrap 顺序两项仍属于独立预算阻断，本审没有判断其关闭。

## 来源与 data-only 合同

`input.py:22–40、296–382` 固定六种 raw class，字段语法先 exact type 后递归；SourceRecord 四字段、TermInput 五字段、RuleSpec 八字段、Triple 三位置与 Comparison 三字段均直接读取原值。禁止 foreign class/metaclass 协议，不从 RDF set、N3、PV 或 saved payload 重造 raw syntax。规则与各成员 tuple 的顺序、disabled tuple 的原序均保存。`_definitions:454–498` 额外产生带 enabled 的固定 wrapper，同时保原 serializer 的独立 definitions_preimage；enabled 与 disabled 在严格 decode 后逐项核一致（621–657），并比较重编码 bytes。

`_prepare_profile_material:695–730` 对 Turtle 保存原 UTF8 bytes，source.digest 来自该 bytes，source.text 在原 65536B 门上取原字符串或 None；structured 保存原 tuple[tuple[TermInput×3]] 和逐 term.source occurrence tuple。reference/revision 的 None 和空串不归一化。producer parser identity 必须精确等实际 domain 对应的当前固定 parser 名/语义版本（703–714）；这仍只是内部 parser 身份数据，不是可信代码 manifest 或正式 capability。

consumer `input.py:797–823` 仅表达当前真实 `_request` 使用的 query `{text,references?}` 或 validation `{turtle,enabled,references?}`，不填默认 enabled/references。两层可各自 structured 或 Turtle；原 bytes 在独立层以 hex 编码，不拿 SourceRecord.text 代长原文（826–946）。strict decode 逐 input/source/definition bytes 再对照 canonical 重编码（948–962）。外部 owner 的 parser identity 和各层 identity 保留为数据，代码没有认证原 snapshot、权限、Job 或 owner 的能力。

这里存在明确的后续责任边界：人工构造同类型 records、重绑一致摘要或伪写 parser identity 不能凭本 data-only API 得到来源认证。当前没有 formal authority 位、Store 写口、自签 Job 或 selected cache；不能把缺少来源认证改称该 codec 已提供。未来 T01 必须从真实受理快照/owner 供应并绑定这些物料。

## 唯一计算与兼容

`semantic_execution.py:674–715` 仍调用原 parser/context 体；新分支只选择 exact 私有 `_ProductionCapture` 和同一个 `_profile_reason`。定义 tuple 从原 `_profile_definitions` 返回保留，包含原 ordinal；disabled 在原校验后捕获，Catalog 是实际 `_profile_catalog` 返回对象。每个原 ProfileLimits（包括 dummy 与 disabled 所占槽）在创建后、compile 前捕获，没有另做 divmod 或从已保存 payload 推算原 L。

`semantic_execution.py:716–755` 保持原 projection/UTF8/rows/hash，新增局部保存该次真实 source_encoded/defs_encoded/encoded/rows_encoded。`production.py:116–127` 还对同次 source/defs bytes 与预先固定前像作核验；`218–225` Catalog 额外编码实际捕获对象，而不是反解 saved JSON。`ProfileComputation` 仅在所有步骤成功后构造并 transfer（228–242）。

原 `reason` legacy 分支未变；profile facade 的既有异常适配移入共用 core，未另造新 matcher。原 `execute_profile`、`execute_profile_records` 参数与四键 wire 保留，rows 切片及受限错误 adapter 仍由原体提供。新 data-only 错误不加入 wire 契约。这里的 ProfileComputation 顶层是 frozen record，但它显式持有原 mutable native_result/wire 字典；它不是深只读输出，也不是不可篡改权威句柄。固定 bytes 与独立恢复核验不能被调用方后来修改 native 字典替代。新深只读能力由 restore fullview 提供。

## 完整 schema、恢复与持有

`restore.py:322–551` 固定 object keys、位置、标签、bool/int/hex/bytes、原 raw fields，并对 saved PV 的 term/domain/value/language 与 fresh canonical parse 逐项 exact 比较；这不是允许修补 saved value。`553–937` 保 comparisons、heads、proof、basis、source/revision/digest、Catalog、原 L、budgetLimits/Usage、planDigest、所有 ordered originalMatches，及顶层其他 reasoning 字段。原 shared decoder、预像/摘要、canonical payload/rows/source/catalog 校验保持。

冻结在 safe projection 已删除、原 A16 预付和新增 freeze 预留后才开始（1202–1213）。`_freeze_native:1032–1080` 将 dict/tuple/list 变为 frozen wrapper，序列显式保 native_kind；canonical 精确类的 immutable leaf 原样保留，没有重新 parse/reissue PV。`_freeze_projection:1083–1098` 输入完整 raw 外层与完整 native reasoning，不接受 allocation 或 RestoredChild 作为字段来源。

完整视图生成后，每个原槽仍且仅调用一次原 16c `check_firing_batch`，disabled 传原空 tuple 与 disabled=True，未禁用槽传原 ordered matches（1217–1240）；16c 本身的真实 compile/replay 是原校验语义，不是额外 reason。全部槽通过以后，才构造最终 RestoredBatchSet/RestoredProfileResult（1337–1361），旧 batches API 与新 result API 共用一次 operation。

`_restore_operation:1383–1398` 清 children/parse_usage/caps/projection/inner_batches/retention、失败 outcome，并 drop decoder/cache 后 cleanup/finish；终末清理若抛 BaseException，也清 outcome/decoder 后透传。producer `243–258` 重建有限错误、drop capture 并清新局部，再在 except 外 raise，所以原 helper traceback 不经 cause/context 留到公开错误。

`RestoredProfileResult.retention` 在 cleanup 前快照全部仍预留 live（1340–1346）。cleanup 后 ledger.live0 表示本 R 操作终结，返回视图仍持有原发行 PV/native/rows，不能理解为物理内存释放。C 的 retained/peaks 则是保守逻辑票，不是 RSS、真实 Python object 大小或 CPU。两类 receipt 都不授 H 租期或权限；接收 owner 须另承担真实持有/累计、退休、GC 与失败取消生命周期。此处没有声称证明全进程容量或 Q5 容量线。

## 测试真实性与证据范围

读取了新增 input/production 两个测试全文，以及两个旧 restore 测试的完整差异。`test-ast-comparison.json` 以固定 adoption/product 的 AST 对照证明：旧 restore 的 15 个 test 函数一个未删、既有 test AST 全部不变；旧 limits 的 21 个 test 函数一个未删，仅收据失败 test 修改为核真正共用 `_restore_operation` 并增加清理字段，没有放宽原输入/断言。capture_case 的输入和独立 witnesses 仍在真实生产前形成；旧夹具通过 observer 拿 native 再推导 allocation 的步骤，已改用真实发生点 capture API。observer 现在只计数并调用真实 core，没有供应替身结果。

新增测试以 wraps 观察真实 core/defs/catalog/compile/evaluate，不返回预制结果或 expected。完整 fullview signature 的 oracle 是同次真实 producer native，适用于字段无损恢复；它不是独立数学正确性 oracle，不能据该相等再宣布 T05 数学已全证。原 expected/hash 不随恶意 payload 污染而改写的拒绝断言仍保留。

本审实际运行 `01-origin-probe`：14 个有界案例，exit0、timeout=false、stderr0。完整 argv、cwd、起止、环境覆盖、139 项 sourcesBefore/After 及双流保存在同目录。probe 输入使用原真实 capture fixture；注入仅制造失败、wrap 仅计数，不供应计算/alloc/expected。首执行即成功，无被覆盖的失败运行。

其中 8 个 fullview 故障路径涵盖 freeze/projection/batch/result/usage/peaks/live 与第二槽；3 个 producer 晚期路径涵盖 receipt/record/transfer；其余 3 个为实际 capture、完整字段/持有、consumer raw 往返。探针不是 pytest 测试数，不能与 root 的 238 专项累加。

root 的完整 npm check 此时仍在处理新过程脚本格式问题，本审未把它记作通过；作者 83 probe/1024 回归和 root 238 专项也没有重命名为本审独立运行。未重跑所有旧145/23exec、不以其旧版证据充新成功。新过程文档/JSON 的显式 ignore 覆盖格式检查结果另存 `02-document-format.*`；不批量格式化作者文件或历史日志。

## 关闭边界

来源/schema/本轮受控 Exception 清理范围的有限通过，绑定本报告的精确 f677 与九文件 hash。预算阻断未关闭、实施输入改变后必须按新固定 ref 复核实际 delta。未来 T01 原受理/owned worker/同事务 origin、Job/store/permission/locks/version、所有 K selected、不可重置聚合账与 H、退役/取消/重开/GC，及 T03/I06 供应与指定双方/CI/最终整链验收均不能从此报告继承通过。
