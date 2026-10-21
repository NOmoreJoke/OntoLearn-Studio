# I05 directsteps + shape 最小组合独立增量审查

结论：**有限通过；没有发现本次组合新增阻断。** 被审产品为 `43d56317f0bfbdfeec05efc583b306615ae54a30`，continuation为 `fb99fbdc6d2630efe0c1107b93401667a808466d`。本审只核批准的两集合组合和三份精确采用原件，没有重做旧六问题或旧过程全审，也没有重跑产品测试。

## 输入和固定身份

全文读取根控制 `I05-directsteps-root-closure-and-shape-combination.md`，以及完整55581B固定输入JSON，解析其全部144行并逐项处理。固定输入SHA为 `1084ff2fa6874b6b6d9f940dc022b067c5e1108c8eb8c803c03083aa4edae115`；本树两份raw与根授权原件逐字相同。随后读取candidate、preflight、exact patch、prepare/run归档脚本和early-launch记录，并对frozen-process清单的1095项作身份保全核验。

`static-verification.json` 保存独立静态方法、全部144身份及输入指纹：当前144逐项等产品Git，143只读逐项等各自sourceRef Git、sourceTree当前原件和授权bytes/SHA。semantic是唯一writer：其sourceRef=8e8表示输入前像，更新后的56037B/SHA属于组合产品43d；不把组合输出伪称8e8原件。

| 组合成员                             | bytes | SHA-256                                                            |
| ------------------------------------ | ----: | ------------------------------------------------------------------ |
| semantic.py                          | 56037 | `c45fda962a3aa272490d683abbec96175e21ca32de94afb1d2de006b02a3c56e` |
| consumer-C-inputs.json               |  8505 | `eeab821ccd71d55eed425a08b34d07648e623c0aa34eb2eabf66b839bbb426f6` |
| consumer-C-goldens.json              |  8163 | `c25e7afcc593a7be09fc8b2ca29af9cff28a7a1e030a13b98aa5e7d88d596440` |
| test_semantic_profile_shape_entry.py |  7211 | `38bc7a4074e183205f55fdb0a74e6933a505f9ff021fe24f5895d296ab725324` |

三份新增成员逐项等 `3bd19e347051627242197f15fce712c9c9dd6b8f` 固定Git；其sourceTree亦仍等该原件。完整路径/角色和引用均见静态清单。

## 文本、AST与行为边界

独立Git差异恰一修改、三新增。`semantic.py:1296` 仅将sh:datatype的局部允许集扩大为原_DATATYPES并rdf:langString；`1305–1320` 的inclusive局部允许集仅增加nonNegativeInteger/dateTime。精确两次文本替换的结果逐字等43d semantic，且逐字等归档exact-shape.patch，不是整文件覆盖。

顶层AST只有 `_shapes` 变化；组合后的整个 `_shapes` 函数文本和AST都等3bd。函数外所有文本逻辑未变，包括全局_DATATYPES、_terms、query、rules、四append及原排序/首插入、原L收费、身份/leaf/D费用、schema/version和兼容逻辑。其余140个原受控文件逐8e8保持。故本次不会通过共享全局类型集把新政策带进DAG或规则运算。

date没有进入inclusive集合；ill_typed门仍在，原_terms拒绝也未动。min/maxCount、非literal边界、结构/路径及external-import门均不变。这是指定入口允许集的组合，不采用有限date提案、不接纳新的illtyped入口，也不扩待议spike。

独立逐1095个旧过程/主文核当前bytes/SHA和continuation Git全部相同。只做保全核验，不重新审其历史内容或覆盖旧报告。

## 采用测试与真实结果的判定

三份采用原件已全文读。测试模块在加载时读取inputs/goldens；实际observe只把data/shapes传入原parser和check_shapes，golden没有进入产品调用。测试在真实调用返回后才按id选择expected并核完整结果。Validator.run的observer调用原run，仅记录次数与返回报告；本审也没有供应结果或重跑该调用。

四个原C输入明确比较conforms及完整focusNode/resultPath/value/sourceShape/component/severity；不是只看一个布尔或错误消失。dateTime-before的期望是正常MinInclusive violation，equal是符合；没有把输入拒绝伪称Validator报告。邻例、独立非法边界、nni零/封闭上界、external imports、illtyped的数据入口也保留原断言。

本审消费根唯一 `01-combined-check` 的完整stdout、stderr、command和成员表，并逐144核sourcesBefore/After等固定产品。实际结果及26报告/全部D费用观察见 `existing-evidence-verification.json`；没有重复专项或全check。

根01实际exit0/no timeout/stderr0；lint、format、typecheck、build、ruff通过，TS1125通过，Python4990通过/44既有skip（141.56s）。77DAG和26shape由同一次完整check承载，不与旧专项累计。两个完成run的144项前后身份均逐项等43d固定候选。

实际26份shape观察中9次进入真实Validator、17次在Validator前拒绝。四修复C均恰调用一次；三个邻例和两个nni边界也各一次。所有诚实报告与原golden逐完整行核同，dateTime-before确有原完整violation。非法date边界和illtyped数据均为0次Validator，后者仍INVALID_LITERAL_LEXICAL。结构非法及external-import同样未触发Validator。

DAG费用观察读取本次真实全check所留66份JSONL、178个packet，来自66个有observer产出的DAG测试；事件均为实际12字段记录，共222170个累计历史副本，不能当作互不重复收费数。没有把没有observer文件的其余测试伪称有fee文件，也没有另造fee、结果或扩大预算结论。源码中D票额/阶段/上限不变，本审不替预算独审签字。

`03-verify-sources` 实际exit0/no timeout，stdout核12归档源；144前后等43d。早期02是runner文件尚未创建时launcher退出2，npm未执行；独立分离双流/准确时间缺口按early-verify-launch原记录保留，不拿03成功补作首跑。

## 交接限制

本结论只适用于精确43d组合与现有真实证据；不声称正式Job/Store/selected/HΣ、父I05/M1、两个pending消费者、同版双外审、CI、目标OS真人或develop门通过。

仅写本新independent-review目录。未改任何产品、测试、其他过程、AGENTS、环境或Goal，未stage/commit/branch，未运行GUI/native/e2e/HMR/网络/模型/服务/付费。过程脚本为.py.raw，只做stdlib静态或既有证据读取。报告、成员清单及写锁交付后停止写入。
