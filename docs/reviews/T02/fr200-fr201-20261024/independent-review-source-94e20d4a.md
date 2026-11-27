# T02 FR200/FR201 多值事实修复与验收定义独立审查

结论：**Pass（本域最小修复、两专项及新 UI 测试定义的静态层）**。未发现本次四叶新增的 P1/P2 阻断。真实 UI/Electron 用例没有运行；不据此结整 FR200/201、不登记 2-of-17 完成或解除 HOLD，不替指定双审与父验收。

## 固定身份与审查范围

- 固定候选：`94e20d4a4a654ebcf735be74902ecfa7595ce356`，已实际 rev-parse。
- 基准：`583c05c7870ba0f8f642e3eeea1d0590e5859ca2`；分支 `feature/weekly-t02-fr200-fr201`。与基准差异恰四叶，1285 插入、5 删除；唯一产品改动为 `mainline-facts.ts` 的20行差异，其余为测试。旧分支/旧报告不改。
- 完整核四叶差异，全文读生产 planner 与新922行 spec，读两 unit 新增全部矩阵及必要既有 fixture/断言上下文。只读实际 `storage.py` 的 remove/edit/manual 与 `_check_slot`、快照所有权校验切片，`project/domain_changesets.py` 的 supported/preview 与真实 Store preview 入口；未 import、执行 Store/SQL/产品或全仓测试。
- 读 PRD V0.6 FR200/201（307–320）及附录 C（959–979）相关全文：四类、类层级、五字段 M、删除影响、结构定义与实例断言分离、RDFS domain/range 非值校验语义保持。本次未借此扩大为 Turtle、SHACL、规则或整个父功能通过。
- 实际 AGENTS 15147B，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，与此前全文读过的版本相同；没有改指南或公共源。

| 四叶（相对工作树） | 字节 | SHA-256 |
| --- | ---: | --- |
| `apps/desktop/src/renderer/src/ontology/mainline-facts.ts` | 2994 | `b981e7e9eb464cd20e94c57a303f45d788c63a661e9adbc8f7acc2b2a13c6837` |
| `tests/unit/t02-mainline-consumer.test.ts` | 61899 | `1e61715a1e7ae3c29c07e0714926a6f53dad96f8eaf75d6ccbe82b2b91584474` |
| `tests/unit/t02-mainline-metadata.test.ts` | 19432 | `ab3c2a91b354353ea25340c6deac495e3e837cf9835ca2325c18a5715fbdc54a` |
| `tests/e2e/t02-fr200-fr201.spec.ts` | 36101 | `61ad7e8749cdeac0ef1d43f94a278907803b500ac95a48ed335f803d0d4e6579` |

本人运行之前、之后均逐四叶核 **current bytes = fixed Git bytes = owner before SHA**，两次均4/4相符。before清单 `/tmp/t02-fr200-fr201-check-01-before.json` 为468B，SHA-256 `783c1b972b73e84551477c28bdca9fe202431ff62da57b4c4c444f3a290fa0b0`。

## 产品修复与存储语义

1. `mainline-facts.ts:16–19` 仍要求选中原 ID 存在且非墓碑，且 owner/source_row/managed_value 均 null。改动没有把映射记录转换为 manual。
2. 22–40 行取消“同 S/P 只能一条活记录”的过宽门，允许独立 manual 的不同 O。仍拒同 S/P 任意 active mapped 贡献（三所有权字段任一非 null），以及其他记录精确支持原 SPO 或编辑目标 SPO。用的是完整词项字符串精确相等，没有 N3 解析、语言/类型字面量归并或语义等价猜测。墓碑及其他 S/P 不被写入或当活支持合并。
3. 41–52 行 ontology definition 的精确原/新 SPO 重叠门未变；remove 返回 `[fact.id]`，edit 只返回 `{[fact.id]:newO}`。无批量按 S/P 写、删除 sibling、重建全 facts、生成新 ID 或重写 M/definition payload。未改 `newManualFactPlan`。
4. 实际 `storage.py:724–759` 对 manual remove 按 project/id 删除，对 edit 按原 ID 只更新 object，并核 `term(value).n3()==value`；`_check_slot:1114–1140` 继续施加真实 single-valued/精确重复及 reserved-ID 冲突。planner 放行不等于服务必接受，未解除这些权威检查。`project/domain_changesets.py:135–165` 对实际 touched before/after 拒映射字段，`preview_changeset:434–444` 经 merge_plan→真实 transactions.preview→supported；本次没有将只读形状或 planner 结果当提交权限。
5. 新14事实实例覆盖：四个按两原 ID 编辑/删除的正例、三个不同 RDF 拼写不归并例、三个 ownership 字段的选中/同槽拒绝、两个事实原/目标精确重叠、两个定义原/目标精确重叠。包含墓碑、其他槽 mapped、M/opaque定义/mappingState 不变断言。`"01"^^xsd:integer` 等 fixture 只用于证明 planner 不做词项语义折叠，不能由此声称非 canonical 拼写会获真实服务接受。

## 新测试定义的范围与完整性

两 unit 新增10个结构矩阵实例：rdfs/OWL class、objectProperty、dataProperty、individual 共5种变体的 create/edit/copy/delete 与 exact五字段M/RDF，另5种外部引用影响/删除拒绝。独立 expected triples 明确声明及 parent/domain/range/type；结构变更不生成实例事实。它们是纯映射/拒绝形状测试，没有新 backend/Job 运行证明。

新 e2e spec 仅5个测试定义：4类 UI CRUD + 1个 FR201 多值事实/删除影响。已全文核对：

- 使用原 `launchIsolatedDesktop`，按 UI 建空项目；create/edit/copy/delete 与事实 mutation 均用可见表单、完整 Diff 和明确确认按钮，未调用 bridge 写入/种 DB/替换 authority。此 helper 的实际 launch 只在测试体内，`--list` 未执行它。
- RDF与M期望由 spec 独立写出，不导入生产 mapper；读取 Diff 只提取新随机 home/fact ID，结构和 before/after 全记录仍对独立预期逐项比较。校验预览未改 domain/snapshot、提交后的完整 state、sibling/M/定义保留，以及原 operation/Job/marker、before/after snapshot 和新 revision。没有令 marker.planHash 等于 preparedPlanRef。
- 复制用新 IRI/identifier，保多语言和同义词/示例原文；修改结构分别核 subclass/domain/range/type；事实用同 S/P 多 O 原 ID 编辑/删除，并保其余字面量与定义。被引用 property 的影响列表与完整事实精确对应，预览拒绝后核项目未变。
- readProject/getOperation/getJob 仅作真实具名只读观察，没有借读回生成业务预期。仍须在真实运行时验证 UI selector、时序、Diff 顺序及 canonical 服务实际接受，而不是把静态定义当已发生。
- 空 UI 项目的 mappingState/墓碑初始为空；spec 已明确不将空集合保留断言报成非空 mapped/tombstone 覆盖。真实 active mapped 及非空墓碑来源/状态仍只有本次 unit shape/拒绝边界，未用 runtime 声称补齐。

## 红绿证据及本人运行

红件实际目录为 `outputs/20261024_t02_fr200_fr201_006/red-source/`（2叶，“source2”是件数），两件字节/SHA逐项匹配 receipt；原 planner 为基准的2742B旧实现，patch只加原反例测试。原始日志明确 **7 failed/8 passed/71 skipped**，失败均来自旧 `live.length!==1` 的 AMBIGUOUS_FACT_SUPPORT；receipt记录 exitCode=1。本人静态读回，未重跑/覆盖红证据。

| 红件 | 字节 | SHA-256 |
| --- | ---: | --- |
| red.patch | 4090 | `a41973ceca2dfa7b891d32a1a5f8c6e98cc7941e7686d6ccedbc4d72f7c62bd5` |
| red-test-01.log | 4228 | `f5851967ea9eac6ac15ddfb5b2c1632f278c3ff09e3bbde8850c123891088e58` |
| red-receipt.json | 918 | `309ea2f3bc6e25707422399fe3cb29e45933b83956df1e12dfdb3d882b5a6006` |

本人实际运行，以下四项分别观察退出码0：

```text
./node_modules/.bin/vitest run tests/unit/t02-mainline-consumer.test.ts tests/unit/t02-mainline-metadata.test.ts
2 files / 109 tests passed; Start 18:48:04; Duration 410ms

./node_modules/.bin/tsc --noEmit --strict --target ES2022 --module ESNext --moduleResolution Bundler --lib ES2022,DOM --types node --skipLibCheck --esModuleInterop --resolveJsonModule tests/e2e/t02-fr200-fr201.spec.ts apps/desktop/src/renderer/src/env.d.ts

./node_modules/.bin/eslint tests/e2e/t02-fr200-fr201.spec.ts --max-warnings 0

./node_modules/.bin/playwright test tests/e2e/t02-fr200-fr201.spec.ts --list
Total: 5 tests in 1 file
```

`--list` 是收集/定义核验，不运行测试体、Electron 或 GUI。本人未重跑全 check、native/package、产品、SQL或任一新 e2e。实际 Store 切片读取时最初误用了不含 project 子目录的路径，随后按真实路径读取；首次查询还尝试不存在的 tsconfig.e2e.json，后采用上列独立严格 tsc 命令，未写配置或改产品。

owner 七种 typed literal 实际 RDFLib `.n3()` 保原文的探针仅有其会话 stdout，未独立封存原始文件；本次未读该 stdout、未重跑探针，故只记 owner 报告，不能写为本人已验证或已运行 UI 数据覆盖。

## 全 check 静态读回与未验边界

本人全文读 `/tmp/t02-fr200-fr201-check-01-20261024.log`（3060B，SHA-256 `8b67dc1708d1b8f34ddea8c27c42b0663fc9f0e7f71a833e1e957dfb1bd3ffac`）：两个既有 T01 Python parity 测试报 `spawnSync python ENOENT`，1716 passed/2 failed，原失败保留；不是被本次 planner 断言触发的红例。随后全文读 check02日志（12106B，SHA-256 `04d852c3b3e9b1fc0116e3f7d4b654e106a8a2a9641c8427de8a643581678eae`），文本记录1718 TS、3495 Python passed/50 skipped/1 warning及其余check阶段成功。warning为刻意duplicate ZIP member用例的UserWarning。owner报告通过 frozen uv 环境恢复 python 可执行文件；本人未改 parity/锁，亦未独立观察该全检进程退出，不能把日志读回当本人重跑全检。

本次通过仅覆盖修复与测试定义：真实表单操作、完整 Diff/真人确认/Job/原子提交回执实际组合仍未执行；语言子集、正式 RDF parser/SHACL、导入往返、物理来源和父功能完整范围不在本次证明内。现有 HOLD 与根登记门继续保留，后继真实 UI 应按这5例运行并保首失败，不得以109 unit或5例list替代实际业务验收。
