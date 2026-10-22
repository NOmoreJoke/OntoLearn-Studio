# I05 外审首轮与续审意见的最小修复准备

结论：进入正常缺陷处理。旧 2cf 与旧 packet、两方首报告及续审终稿全部保留，不再为凑齐旧覆盖反复续接。当前只有静态 triage 与修复设计，没有产品改动或运行结果。新候选必须重新完成同版双方全范围独立审查，不能只审补丁。

本准备 tree 为 `.worktrees/I05-retained-source-review-triage`，分支 `fix/I05-retained-source-review-triage`，固定起点 `2cf0c3328de464e15a3fa9cdbfdf6aa88d0b4a64`；原批准产品基线仍为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。这里从受审固定对象复制，是隔离修复准备，不宣称已经同步当前 develop 或取得集成许可。AGENTS 采用现行 15147B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，仅工作区指南修改，不提交。

## 已核事实与共享责任

`m08-static-facts.json` 对固定 2cf/6891 的引擎 manifest、锁和两模块顶层 import 作独立静态解析。候选引擎只声明 `rdflib==7.6.0`；`semantic.py:13` 直接导入 `pyshacl.validator.Validator`，而候选锁没有 pyshacl 及其四个所需传递 distribution。核心依赖缺口成立。`pyparsing==3.3.3` 已由 RDFLib 传递带入；缺少直接声明不等于该包本身缺失，不照抄外审更强措辞。

`m08-static-closure-correction-r2.json` 完整处理 dependency edge 激活的 extras：供应 pySHACL → RDFLib[html] → html5rdf，八个要求的 distribution 在供应锁闭包内可达。首版枚举漏 optional edge 的结果保留，后出记录只更正闭包字段。该解析没有安装包、解析网络、调用 resolver 或 import 产品；锁内存在也不证明实际安装或可运行。Python 3.12 是有条件的准入要求，不能登记为已观测到实际解释器错误。

`packages/engine/pyproject.toml`、`uv.lock`、打包 writer 和入口属于 T03 唯一维护面。I05 不抢改。由根协调 T03 提供同一固定供应组合，直接依赖精确声明与锁同时对应；旧 6891 两文件是可核输入，不自动等于当前正式依赖合同，更不把旧 23 包与新的整锁/运行/许可集合混为同一集合。打包还需真正的 build provenance、probe_inputs 布置、隐式导入与许可清单。

M09 的 `storage.py` 与 `job_store.py` 均与 5f 完全同字节。缺 ownership 的 code 映射、四个抛点、JobStore 包装另外铸造 detailRef 和契约要求 detailRef 已静态核实，详见 `m09-shared-owner-routing-facts.json`。这些事实尚不能证明某个绕过包装的正式跨边界路径可达。不能只加入错误码却遗漏必填 detailRef。交根唯一路由到 T01，不由 I05 修改 Store、JobStore、错误目录或存储测试；损坏 SQLite 输入与物理保护 HOLD 保留。

## 按依赖执行的修复单

| 项目              | 精确负责面                                                                             | 最小动作与完成依据                                                                                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M08 / M02 / Z F-1 | T03 经根协调                                                                           | 固定引擎直接依赖、锁、build provenance 与实际打包输入的同版本交接；静态确认包及 extras 闭包，不以单独换锁或存在于锁替代实际环境验证。                                              |
| M09               | T01 经根协调                                                                           | 判断正式边界、detailRef 发行责任与错误映射；若需修复，由唯一 owner 提供固定新候选和自己的契约验证，I05 只后置集成。                                                                |
| M01 与政策登记    | I05 新文档；正式状态由根/原状态 owner                                                  | 新候选明确 I05 验收与 Q6/date 的权威来源、已经采用的政策及仍未完成的实现/样例/验收；原 PRD、历史报告和旧状态不回写。                                                               |
| M07 与三指纹差    | I05 新 packet 元数据                                                                   | 新版本显式给 payload、候选、过程与根 seal 的有向关系和逐件身份。旧 R1 清单仅标历史，不再冒充新候选清单；一字节政策差保持未解直至独立实证。                                         |
| M06               | I05 自有 `semantic_source_package_probe.py` 与 `test_semantic_source_package_probe.py` | 在获源文件修改范围后，为意外无 counter 的 scope 路径加既有安全错误出口的明确前置；保持当前合法 full-v1、B1 和 canonical 调用语义。新增有意义的失败边界断言，实际执行另待运行窗口。 |
| M03               | I05 probe 与 canonical owner                                                           | 当前硬编码值相同。先取得精确 canonical 身份出口；有已批准出口再派生，缺出口不凭猜测造属性。不改冻结版本或把源码 SHA、语义版本串、代码指纹混成一种身份。                            |
| M04 / M05 / Z O-1 | 各原模块、T01/T05 owner，经根协调                                                      | 明确互斥版本、缺失 helpers、回归集和 fixture 的逐路径采用/保留/继承关系。新 70 函数不替代旧测试。只凭相同名字、日期或祖先关系不能关闭意见。                                        |
| Z F-2 / Z O-2     | I05 指纹验证与 T03 打包                                                                | 指纹跨 loader/cache 稳定性待真实验证；probe_inputs 必须由实际打包 writer 放入批准位置。当前无证据，不写通过。                                                                      |

当前不修改任何上述产品文件。先由根确定新 source 修复中 I05 的独占文件与 T03/T01 交接边界，再在此隔离 tree 写实质新候选；涉及其他共享路径须根唯一路由。无需等待 F01/F16/Q5 才完成依赖及错误事实 triage，也不能因此默认这些产品决定。

## 新候选输入、范围和验证

1. `opinion-association-matrix.json` 保留两方首/续原意见、历史意见状态、身份更正、政策 context 不对称和全部未闭项；13 个本轮意见行只作关联，互相关联不合并严重度、不自动关闭。旧 M 的 NotPass、旧 Z 静态 Pass 的未读范围继续有效。
2. `next-full-review-coverage-inventory.json` 固定旧主树全 856 件、16 namespace 和 251 组精确 path/blob/bytes/SHA 代码字节。它是 metadata 预览，不是新候选清单或已完成审查证明。新候选产生后刷新实际成员差异；两方各审完整工程及原 retained 范围。可以共享同一精确字节的实际已读代表证据，仍需核别名上下文和采用关系，不能把分组计数当通读。
3. 明确补入旧 Z 未逐行的 semantic.py 550–1203、四 profile 内部、contract_v2 和桌面大文件；保留 namespace 业务源码、八 queued diff 正文及历史依据均按原范围逐件审清或由原 owner 给明确后继处置，不能静默移除。26 个未冻结项仍 opaque，不作为可执行产品。
4. 下个双方完整输入对称包含四份正式政策的完整副本及相同 SHA。1510B M 补注仍 prepared、未投递；不为它独自再续旧任务。Q2/Q3/Q7/Q6 比较与规范 pins/date 政策、Q9 方向已定，与资源/实现/验收分开；Q5/F01/F16、Q8 及未明确细项不默认。
5. 新 packet 在 payload 冻结后记录实际 candidate Git；后出 process 引用 candidate 与成员清单，根 seal 再引用过程。wrapper 的独立输入 manifest 明确绑定各实际固定对象及复制成员；不要求被散列文件嵌入未来自己的 hash/commit。分清受审 payload 与后出过程文件，逐件验证，不复用旧 R1 成员清单来声称新 lineage。
6. 纯文档准备只作格式、身份、结构与独立审查。本轮不执行产品、安装、resolver、pytest、npm check、package、网络、DB、native、417 或 SQLite 物理操作。后续代码改动按实际改动跑有意义验证；依赖/打包还需完整 check、实际 package:dir 及包内同样例。只有根明确释放相应运行范围后才执行并留真实双流/exit。
7. 新候选冻结后在两应用各建全新真实独立任务，模型/思考/权限/实际 cwd、原生 session ID 和完整输入 Read 链逐项读回。两方全范围审查与所有旧意见处置、必要运行验收、原 CI/发布门分别完成；有限静态设计通过不顶替任何一门。

## 本准备的证据限制

固定字节读解析与 TOML/AST/JSON/哈希均为 stdlib 静态操作，没有执行受审源码。初次闭包忽略 extras 已独立后出更正；根目录无 AGENTS 的 cat exit1、只读路径枚举不存在的 review 目录 exit2、D2 元数据展示 len(int) exit1 均为实际工具转录，未作为产品缺陷，未伪造早期分流。本次工作不修改原 source tree、旧 packet、旧报告，也未推送、建 PR 或合并。
