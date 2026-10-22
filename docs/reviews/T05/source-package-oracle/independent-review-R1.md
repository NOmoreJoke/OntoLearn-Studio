# T05 source/package 外部 oracle 独立审查 R1

2026-10-22。审查者为全新独立 agent，未参与候选实现。审查对象为本地提交 `3d8f4ee912f41bd03388322d29a9bfc0e7defe85`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，分支 `feature/T05-source-package-oracle`。本报告是审查后的唯一新增文件；没有修改、提交或替换候选。

## 结论

**通过，限定为本候选的外部 oracle 实现、固定来源、可复现性与诚实保留 pending 的审查。未发现需要阻断该限定收件的 P1/P2。**

417 observations、320 datasets、三个有序 case-set 均完整保留；280 specified、137 pending，`wholeOracleComplete=false`。这些是规格状态，不能解释为 280 个产品通过、全 oracle 完成、source/package 等效、父 T05/原 Goal/正式 Job/selected/whole-H/S1/B1 或发布验收完成。本报告没有关闭任何 pending。

## 授权与审查范围

先全文读取主目录 `iteration-control/2026-10-21-weekly-release/T05-source-package-independent-oracle-window.md` 及受审树 `AGENTS.md`。随后审查两份脚本全文、五份生成 JSON 的完整结构/账本及逐项模型、字段政策、README、receipt、candidate manifest、author dispositions、命令记录与固定 inputs/guidance。

只使用普通 Git、文件读取、stdlib JSON/hash/AST/数学检查，以及获准的一次 oracle 自测和一次重建 check。没有 import 或执行产品/probe/RDFLib/pySHACL，没有读取新 I05 probe/new test/generator 或 source/package 运行输出作为依据，没有读取未来观察目录，没有产品 pytest/npm/package/DB/native/GUI/网络/安装/共享环境/模型外发/付费/push/PR/merge/Goal 操作，也没有重开被拒资源分析。产品恢复模块仅使用已获准的 literal-only JSON 声明；旧 date 测试仅使用获准 L275–313 摘录。

检查 Git 确认候选 HEAD/分支正确，候选相对 base 仅新增授权范围的 97 个文件；manifest 排除自身的 96 个成员与实际变更集合精确相等，每件 bytes/SHA 均吻合。审查开始及实际验证时仅 `AGENTS.md` 为受保护未暂存修改，15852 B / SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。没有切分支、提交或操作旧冻结树。

## 完整性、独立来源与业务核对

1. **全部输入绑定。** 独立逐项比较 417 项的 ID/顺序、family、operation、datasetId、projectionSha256、sourceRefs、contextStatus、parameters；独立重算每项投影摘要。实际引用覆盖全部 320 datasets。case-set 为 full-v1 的 417 项及两档 B1 各 1 项，有序成员与固定 descriptor 完全一致，子集没有冒充 full 覆盖。

2. **原字节与 expected 权威分开。** 用 Git 原 blob 对照六件获准纯输入/旧 golden 和六件规范文档，副本逐字相等。两输入确为 0e42 的 8205267 B / `47c66ffe18613eb8cc1af6365dcfc9d866821f22c48f96d9f44725f8f7c59eaa` 与 21202 B / `0b91c1a9366d170b5614d94c20006054a5a959be235e0f46cb150cf32335193a`。旧手选 expected 确为 525c 的 767826 B / `87220503f9983146c974fe3e35025d520cad70e54fdd994aebfa86fb1ff7259f`。每项另列 expectedSourceRefs；没有把输入 sourceRefs、历史采集成功或 source 输出当 expected 权威。

3. **原 83 数学上下文。** 除审查旧手选 graph/match/ruleDefinition/rdfsWitness 映射外，另用不 import builder/产品的 stdlib 脚本，从固定输入的原 records/when/comparisons/heads 构造 RDF 身份集合，用 subclass 可达性 BFS、domain/range 和 type 传播求有限闭包，再独立连接全部条件、计算比较及 heads。全部 83 个上下文、101 个匹配的 RDFS/custom/derivedUnion、绑定、accepted、比较真假及全部 head occurrences 与候选吻合。该验证是数学上下文核对，不执行 repair 或原产品操作。所有 82 eligible 仍有准入 pending；repair 的数学对象仅作 context，状态仍 not-executed。四个 E5 项只代表当前累计 event fragment，未升级完整事件/行为/事务链。

4. **RDF/query/SHACL/UTC/integer。** 核对有限 Turtle decoder 的适用语法与全部相关固定输入、IRI/literal/datatype/language、integer 原词法与 string/language 身份，原始文本/record 仍由固定摘要和来源保留。query 完整变量/rows/None/ASK、同值排序、COUNT、FILTER type error 及六个 string expression 的固定结果均有完整模型；Q01 只有 alarm 一列。SHACL 保留 conforms 及六字段多重集，Min/MaxCount 的 value=None 未伪造。C2–10 与旧 independent C golden 一致；date/offset、反向双界、无 target/value、minCount、共享 property、多值、严格/宽 integer 和 legacy/UTC policy 分立。拒绝保持零 Validator、无部分 report/view 的要求，不以普通违规或空报告代替前门失败。

5. **date 首错来源层级。** 12 个 lexical7/8/9/10/15/16 bound/value 只复用 root 明确允许的旧预登记断言；每项声明 `pre-registered legacy regression assertion` 及 `independentLibraryClassificationProven=false`，并保留摘录原件/摘要。它们不是本次独立证明的固定库分类或真实执行观察。未从新 probe 输出补期待。其他缺乏精确前门顺序的项仍明确 pending。

6. **有限 RDFS/DAG/occurrences。** 另用独立 stdlib 检查 37 个 record/legacy 数学模型中的 29 个 direct steps：四模板实例、结果完整覆盖、seed 与前序引用、ordinal、depth、原叶 union 全部吻合。首 witness 采用已批准 directsteps §2 的 result+ordered-premises 候选 key；没有采用 shortest proof。raw aliases 保留 24 个原 term occurrences 与六个 RDF 身份；两个绑定各两个重复 heads 保留四个 occurrence，不能用两个去重结果替代。模型内短规则符号属于数学模型；未来 wire 适配仍须按已批准合同的精确 enum/版本字段映射，不能直接以模型符号代 wire 标签。

7. **scope/B1/restore。** asserted 与 derived facts、ontology 中派生 axiom、query/SHACL 消费结果及 prepare/project 调用关系分立。scope 的真实 same-issue provenance 仍 pending。B1 两档保四 ontology、18k 原事实/改型事实、18k+4 merged、8k+1 RDFS、k matches/六叶 basis、完整 query 和原事实 SHACL；First/Warm 的业务等值要求没有变成预填时间或物理性能成绩。snapshotLoad 为 not-executed。14 restore observations 对应九个 enum，仅在真实同次接收 bytes 扰动且保原 expectation/allocation 的条件下要求 A1 拒绝；保无部分 view、原成功物料不变、reason0，不冒充深 DAG 或最后 child 原子性已经覆盖。

8. **字段、动态关系与上下文。** exact type/key/tail/multiplicity 政策、SHACL 六字段、完整 wire/rows/sidecars 摘要与长度、同次 opaque object、native/children 全投影对应均已列明；finiteRelations 自测并不自证实际 caller capture。7/15/11 顶层名来自获准 literal 声明，/3 显式加 directSteps，不按 key 猜版本。完整 typed/nested 值与真实费用仍 pending。原 106 operations/54 learningChecks/50 productCases 全 not-executed，保原正文/完整 setup、steps 与来源；没有把 collection exit0、数学图或元数据完整升级成生命周期、来源认证或原操作通过。

## 未决项处置

137 pending 的逐项字段/gap/required 与 coverage 对应，未发现用粗粒度 unknown 或历史结果计数替代精确期待：

- 82 个 profile：数学期待完整，完整累计 producer/copy/projection/action invoice、真实 caller-issued child allocation 与首错误准入仍缺。
- 32 个生产/DAG/restore：完整 graphBudget/budgetUsage/typed nested projection、实际同次发行和预算准入仍缺；其中 14 个否例另缺 A1 精确安全错误投影。
- 11 个 legacy 正常项：完整五字段 DTO/evidence 与警告字符串排序；3 个正常 scope 的精确 provenance 编码。
- 1 个 structured-only DAG text 拒绝细码；7 个前门码/阶段；1 个 implicit loader guard 的真实异常投影。

budget-gaps.json 的 82 项逐 operation、重复 copy/occurrence、formula 缺口、allocation 与首错误入口，以及 32 条真实生产/恢复链均存在。已知规范上限/子算式没有被当成实际 full invoice/usage，也未用历史 78/4/1、输入尺寸低于 cap 或 collection0 判准入。新的规范定位尚未纳入本固定候选；即使后续可细化声明分配公式，也不能据此填造实际 capture/usage，本报告不预先审查该后继 delta。

## 实际验证与可复现性

本审查实际各执行一次，工具保留原输出；没有往已有 commands 目录补写或伪造审查命令原件：

| 命令 | 本次实际结果 |
| --- | --- |
| `python3 -B scripts/test-i05-source-package-oracle.py` | exit0；37 tests passed，`Ran 37 tests in 3.394s` |
| `python3 -B scripts/build-i05-source-package-oracle.py --check` | exit0；417/320，specified280/pending137，wholeOracleComplete=false；五件完整重建字节一致 |
| 独立 stdlib/Git 核对 | 全部 417 绑定、320 dataset 覆盖、97 路径/96 manifest 成员、AGENTS、固定 Git 输入/规范副本、保存命令 argv/streams 的 bytes/SHA 均通过 |
| 独立数学核对 | 83 profile contexts/101 matches；37 finite models/29 direct steps 均通过，不 import builder/产品 |

五件 check 输出身份：

| 文件 | bytes | SHA-256 |
| --- | ---: | --- |
| oracle.json | 5651115 | d8a91a9a1dc99def3187b3f77d9f88e5d2a95def08287fc672c8e5aa0fd5a9ab |
| coverage.json | 126099 | 6a8ba37ee119769f0493622ff7328a348ed03f04c749d8c9622c5987ae814b0a |
| sources.json | 7115 | 5c8d2203706254f000e90fa4d397a9b0873e4cb73720b778791436df22397c3c |
| schema.json | 7350 | ddfbbb7f622115ee7698831e1f27333f6e14d8b2d35a5d70ea2aed301cbb012c |
| budget-gaps.json | 327726 | 4a0e72d103a156117e461810d1e0f27a4e96c8f69a56d405111cab34b99300e6 |

初次 KeyError 的精确 WIP builder、工具结果转录及 initial output 副本均保留；转录明确不是原双流，build-02 也明确非冻结源码候选。后续有 invocation/result 的保存命令，其 argv 对应且所有 stdout/stderr 原 bytes/SHA 与记录一致；最终候选 build/test/check 对应当前脚本摘要。不存在用后续成功覆盖首失败的报告声明。

上述验证证明本 oracle 的构造、固定数学规格与记录可复现；未证明固定第三方库/真实产品执行、source/package 观测、动态捕获来源或运行预算。最终比较器/JSONL 适配、费用与来源门、完整 oracle 及产品运行验收仍须后续明确授权、固定候选与新审查。
