# M1 directsteps 与真实消费者最小实施合同（申请稿 V1）

本稿申请新增一个 **finite RDFS 直接 witness 载体**；不重做规则解释、数学值、来源载体或推理器。6c 已有 `PreparedFiring.when/comparisons/heads/basis/source` 足够表达规则的真实输入—规则—结果；缺失的是 `_finite_closure` 首次插入时真实选中的 finite rule、ordered premises 与 depth。不能从 `rdfsEvidence.basis/proofLeaves` 倒推这三项。后续实现由原 I05 writer 负责，T05 只供应外部独立断言与消费者测试；本轮仅文档，未授源码。

本稿基于当前树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T05-profile-M1-math`、branch `feature/weekly-t05-profile-m1-math`、起点 `e0ee604ae5e63b4dfdda5db984c0eec8b59a65f5`。已收件产品 `051ae4cb9b5e58560c8e45cdc56fd98522777b5c` 与数学原件不动、不重测。全部下述新名字、上限和接口均为待根批准的具体申请，不是假定已经采用。

## 1. 精确输入与实际缺口

- 固定 T05 `9333e69234a6f54a0dfc1485f49d8fdeb4b69cfd`：数学/解释输入合同30594B，`supplemental-graph-inputs.json` 5962B/SHA `dc57792093204d85c2e54471c271965c40b7ccd7e5cd6f4614173e1497c332f6`；同版 explanation、consumer C goldens 只读。
- 固定 I05 `6c1eec41091a997f898cb448bfc7d4000c154307`：实际 producer/material/fullview/预算、原 finite closure、旧 scope 与 identity 源。原文件、精确 bytes/SHA 和行号均绑定本轮 `fixed-inputs.json` / `inputs/`，不采用当前他树 WIP。
- 对应 PRD FR501–505、附录 C/D/E/G 只读：一阶段 RDFS→独立规则，不把规则结果反馈给规则/RDFS；RDFS 最低解释为相关公理与直接输入，规则为完整依据链。原83、父M1及发布门沿原状态。

| 6c 实际位置 | 已经具备 | 本轮所需增量 |
| --- | --- | --- |
| `semantic.py:385–448 _finite_closure` | 唯一闭包；候选按 `(result key, ordered input keys)` 排序；`if triple not in closure` 只选首次 witness | 在四处实际候选产生点带 finite rule tag；在该插入分支捕获有序的两直接输入、实际结果、序号/深度 |
| `semantic.py:958–973,1073–1087` | 真实 asserted/ontology 合并图的 leaf ID/三元组，以及每个新 RDFS result 的叶 union | leaf 是 depth0 的旧引用；union 继续沿旧路径，不冒充直接边 |
| `semantic.py:1023–1057`，`quality/rule_firing.py:129–145` | firing 的完整 typed when、comparisons、head occurrences、原 source/revision/definition_digest；evidence 有 firingIndex/headIndex | 不增第二个 rule firing DTO；只在读视图中按真实 firing/head 定位，depth由其 when 的真实直接节点读取 |
| `semantic_profile_restore.py:65–113,890–943` | strict 外7/内15/child11，RDFS evidence 严格只有 result/basis/proofLeaves | 新格式显式内16，新增一字段，child11及全部数学字段不变；旧 reader 仍拒绝未知字段 |
| `semantic_scopes.py:86–98,155–172` | legacy selected 只接受五 key 且 RDFS evidence只有 result/basis | 不可塞入 profile 15/16 或新字段；另开明确 profile 消费入口，旧函数不自动转换/丢字段 |
| `resources.py:40–53 semantic_identity` | profile=True 精确返回 i05-finite-7；运行时 infrastructure 身份另存 | 新解释模式必须显式选择新身份，不能只改 payload.format 或沿旧7标签发布 |

现有 `proofLeaves` 记录没有 source actor/原 token 认证。`termSources`/`RestoreExpectation.input_preimage/source_preimage` 已保留真实 occurrence/source；不为 directsteps 再复制来源文本或生成新认证字段。结构化记录可由实际三元组记录关联三项 TermInput source；Turtle occurrence 缺三元组级精确 token 时，只能显示已有实际 source/可得 span，关联未供应就标 unavailable，不从 N3 展示串编 token、byteSpan 或 ontology/asserted 所有权。

## 2. 唯一发生点、首插入与有序规则

保持 `_finite_closure(asserted, charge, meter=None)` 的默认返回 `(closure, proofs)` 和全部旧分支。新私有参数只接受本模块批准的 exact `_DirectStepsCapture`，默认 None；不允许任意 callback。只有新增解释 API 可以提供它。旧 legacy、旧 profile、旧 capture 默认路径不创建新 ledger/数组/候选 tag，不改变 L、错误顺序或输出版本。

新解释路径的候选临时记录为 `(triple, ordered_inputs, finite_rule)`；现有排序 key **完全保持** `(key(triple), tuple(key(t) for t in ordered_inputs))`，不把 rule/depth/source 加进 tie-break，不重排两输入。相同 key 的稳定性沿原生成顺序；不是 shortest path、最小 depth、全部证明或新规范排序。

| finite_rule 精确字符串 | 现有 append 产生处 | 有序直接前件 → result |
| --- | --- | --- |
| `rdfs9-type-via-subclass` | type propagation | `[(x rdf:type A),(A rdfs:subClassOf B)] → (x rdf:type B)` |
| `rdfs11-subclass-transitive` | subclass transitive | `[(A rdfs:subClassOf B),(B rdfs:subClassOf C)] → (A rdfs:subClassOf C)` |
| `rdfs2-domain` | domain branch | `[(p rdfs:domain A),(x p y)] → (x rdf:type A)` |
| `rdfs3-range` | range branch | `[(p rdfs:range A),(x p y)] → (y rdf:type A)`；实际代码已有 URIRef subject 门 |

每次 `append` 的新增 tag/额外 tuple slot 均先计新池；**重复/已存在结果、最终未入选的候选也计费**。在原 `if triple not in closure` 内，先通过旧 MAX_TRIPLES、旧 debit/union，再在任何新增容器构造前预留新池；保存当前两个输入的临时`SeedKey(真实canonical TripleKey)`或`StepOrdinal`引用、tag、result、`ordinal=len(steps)`、`depth=1+max(d0,d1)`，然后随该次实际成功插入一起确立。此时leaf ID尚不存在：6c的leaf_ids/leaf_records在闭包返回后的958–973才创建。新sink不得提前再hash leaf、从expected拿ID或增加另一来源表。由该唯一既有leaf发生点在原ID确立时执行`link_seed(actual_key, existing_leaf_id)`；wire编码前必须全量resolve为§3的最终DirectRef，悬空即整任务失败，native公开结果与wire都不得残留SeedKey。link的每次索引查找/键扫描/引用或字符串复制/临时释放都先计D池；临时SeedKey/索引与最终carrier并持峰值不相互抵扣，resolve完成再释放临时票。发生任意后续错误，整次生产不返回 carrier，不发布 partial steps。不得把失败后短暂留存的数组当成功观察。

seed leaf depth=0；每个 result 只登记一次。引用前件来自生成该批候选时已经存在的 closure，故只能是 seed leaf 或此前实际 step；保存全局首插入序号，不按最终 result 排序重编号。即使某条后续更短 witness 被发现，保第一次选择及实际 depth，不覆写。原 `proofs[result]` 的叶 union 仍由原代码产生。

**不用再次 reason/replay 整图来生成解释**，也不扫描叶 union 搜索一套“看起来合理”的直接边。接收端对给定两前件做四模板局部一致性检查，不枚举候选、不补结果、不评估 false 比较，因而不是第二推理器。

## 3. 最小完整新 wire 合同

申请在新的 reasoning 对象只增加 `directSteps` 一个字段；旧15字段原值原形保留。外 payload 仍七字段，mechanismBatches 每 child 仍十一字段。`directSteps` 的 exact key set：

```text
DirectSteps = { format: "i05-direct-rdfs-steps/1", steps: tuple[DirectStep,...] }
DirectStep  = { ordinal: int, rule: enum4, result: TripleKey,
                premises: tuple[DirectRef, DirectRef], depth: int }
DirectRef   = { kind: "leaf", reference: existing_i05_proof_leaf_id }
           | { kind: "step", ordinal: int }
TripleKey   = tuple[str,str,str]  # 与原 rdfs/rdfsEvidence 同一真实 N3 key，不是输入 token
```

这是 **native 精确类型**；wire 仍唯一 `_ProfileProjection` 和 canonical JSON：tuple投影array，所有int（包括ordinal/depth、step引用）投影为既有 `{"integerHex":"0x0"}` 形式，不能引入另一套JSON数字、宿主float或宽松int。kind/rule/format为 exact str，bool不是int；缺/多/重复 key、未知 enum、None 与空数组不能互代。`steps=()` 合法（原图无新增RDFS）；缺 `directSteps` 不等于空步骤。

完整性与严格校验顺序：

1. 全局格式/identity/预算/期望前像及 payload/rows 原 gate；新步骤不得绕过 strict Reader 的白名单、重复键、深度、总字节门。
2. leaf IDs沿原算法，引用必须唯一命中同一 fullview 的 `proofLeaves`，leaf集合等于该生产的原 seed graph，不从 expected补 leaf。step ordinals精确为0…S−1，结果唯一、非seed，step结果集合精确等于现有 `rdfs` 与 `rdfsEvidence.result` 集合；不是只比数量。
3. 每步 premises 恰2；leaf必须存在；step ref必须 `< 当前 ordinal`，不能负数、自指、前指或悬空。逐行建立有界索引，核相应四模板及result；用已验证前件depth核本行depth。不能按结果词典序推拓扑。
4. 对每一步实际展开直接DAG叶引用，与该 result 的原 `rdfsEvidence.proofLeaves` 逐集合核对、无重复；并核原basis三元组一一对应。展开实际访问及 union/比较全部计新池，允许 DAG 多次重复访问但不得不收费；不用“每边一次”假装指数路径免费。使用逐step去重叶集合的有界动态规划，按每个实际引用拷贝/并集收费，超限整体拒绝，不递归展开路径。
5. 所有原 typed批次/definitions/source/原L及 check_firing_batch仍走现有同版完整校验；新增directsteps不替代原流程。最后一个step/最后一个premise/depth/source尾字段失败同样无成功prefix或部分selected。

第2项“seed相等”须依真实输入已生成的 seed key/来源核验，不能仅信payload自述。结构化源用已验证input_preimage三元组；Turtle fullview当前只验证occurrence与source，未提供“已验证seed三元组表”。因此最小解释入口先限定 **records非None 的真实 structured material**；Turtle 原入口继续旧格式。新restorer已校验的TermInput三元组，逐项复用`semantic._profile_term`与`_key`作相同lexical-preserving N3格式化（不是Graph闭包/parse_value）；调用前按各field UTF8最坏4倍、N3转义最坏6倍加32固定字节预扣新池scalar/copy/work，原/新临时同时保票，累计进入K门。formatter由现有restorer调用，directsteps纯模块只接收已核canonical key，不import reasoner、不造Graph或伪GraphBudget。然后逐键核seed/proofLeaves exact集合与原leaf ID算法。新增Turtle解释要由I05另供实际parser三元组绑定、分配与预算，不用termSources拼接推断。这样不把一项缺源隐含扩大为新parser权限。

这些检查证明给定DAG局部一致与覆盖，不在接收端证明“没有未枚举的更早 witness”或全闭包全局完备。首次选择来自真实发生点和绑定该次实际输出的来源链；hash本身不是认证，正式来源仍由T01未来真实Job/Store供给。

### 3.1 无必要新增的字段

不在step重复存 `basis/source/termSources`，避免两份可漂移真相；叶basis沿原evidence，来源沿原preimages/occurrences。原规则的真实名称是 `PreparedFiring.rule_id`，结果是每个 `heads[i].triple`，ordered premises是其 `when`。引用每个when对应的leaf/step，规则head的读视图depth为 `1+max(when depths)`；不写回PreparedFiring，不再发一个rule-step carrier。全局 `firingIndex + HeadEvidence.index` 标识 **occurrence**，相同triple的head0/1仍为两个。规则输出不进入finite步骤/规则when索引，禁止产生规则链。

缺原saved rule JSON→RuleSpec binder属于独立依赖；不把现有golden Catalog/typedexpected或手造Job当binder。内部组件可从纯输入按真实语法生成实际TermInput/RuleSpec，来源标记为fixture material；只有T01供正式快照后才能称保存定义/真实产品流程。

## 4. 版本分派与组件 API 申请

以下精确版本名申请整体采用，非本轮擅自改常量：

| 层 | 现有固定6c路径 | 申请的新解释路径 |
| --- | --- | --- |
| input material / rule profile / child L | material/1、已采用PROFILE与原ProfileLimits | 完全相同；首窗口仅structured records |
| computation wrapper | `i05-profile-computation/1` | `i05-profile-explanation-computation/1`，exact新class，含真实DirectStepsReceipt |
| payload.format & reasoning.formatVersion | `i05-reasoning-result/2` | `i05-reasoning-result/3` |
| reasoning + implementation executionSemanticsVersion | `i05-finite-7` | `i05-finite-8`，只版本化新增可观察解释，不改变Q6值域/算子政策 |
| directSteps.format | 不存在 | `i05-direct-rdfs-steps/1` |
| restore schema / full result / projection | schema/1、result-restored/1、projection/1 | `i05-profile-restore-schema/2`、`i05-profile-explanation-restored/1`、`i05-profile-explanation-projection/1` |
| 原R、term-key缓存及原batch revalidation | 现有/1与原batch版本 | 版本/预算原分支不变；扩展专用ledger另为 `i05-direct-steps-budget/1` |

新API只在精确内部模块使用，不注册公共capability、不改IPC/Store/Job：

```text
execute_profile_explanation(material: ProfileMaterial, *,
    error_catalog, error_schema, ledger: CaptureLedger,
    direct_ledger: DirectStepsLedger) -> ProfileExplanationComputation

restore_profile_explanation_result(payload_json: bytes, rows_json: bytes, *,
    expected: ExplanationRestoreExpectation, allocation: OriginalAllocation,
    ledger: RestoreLedger, direct_ledger: DirectStepsLedger) -> RestoredExplanationResult

explanation_roots(view: RestoredExplanationResult, target_keys: tuple[TripleKey,...], *,
    direct_ledger: DirectStepsLedger) -> tuple[RootRef,...]
```

`ExplanationRestoreExpectation`是独立exact class：包含与旧RestoreExpectation相同的实际digest/implementation/input/source前像字段，加固定schema2/direct-budget1标识，不继承旧class伪装为schema1。`OriginalAllocation`仍仅来自这次producer实际L，新增direct limits/usage/retained独立进入DirectStepsReceipt，不改原allocation子表或原L。

roots仅返回已有节点的引用：leaf、finite-step，或 `{kind:"ruleHead",firingIndex,headIndex}`；相同目标匹配的所有真实head occurrence都保留。无目标返回空tuple，不推理补齐。它是已获准完整artifact的**内部只读定位API**，不是过滤权限、单目标传输DTO或正式selected入口；持有view本身已经持有完整结果，不用“只返root”冒充安全裁剪。

旧 `execute_admitted_profile_job`、`restore_profile_batches`、`restore_profile_result` 继续精确 /2 + finite7 + schema1；旧 private `reason` 不默认产生新字段。新API只接受 /3 + finite8 + schema2 + directsteps1；未知/混配版本立即有限拒绝，**不靠key存在猜版本、不删字段降级、不重签历史**。历史/legacy五key selected沿原函数；schema1解码不扩全局JSON_KEYS来容忍新字段。新Reader以显式schema模式选择固定新增key集，仍严格拒unknown/duplicate。

`resources.semantic_identity`申请唯一owner增加 exact bool `explanation=False`（旧参数默认不变）；explanation=True仅允许profile=True，只有新真实计算分支调用，返回finite8；`IMPLEMENTATION`的infrastructure身份、engineVersion、lock hash及公共registry不改。所有相同version必须从这一个函数取得，不在T05/test临时改字典冒充新producer身份。

新私有 `DirectStepsFailure` 仅含固定reason/classification/stage/domain，无输入值/路径/trace；invalid/limit/reused/internal四类，失败不退累计工作。旧图/规则错误仍保原diagnostic/public adapter。此内部API不新增公共error code；将它接入真实Job前由I05错误适配与T01边界另固定现有公共错误映射，未授前不得跨边界原样抛异常。

## 5. 有限费用增量：所有候选、DAG展开、整流与并持

原L/原图work/旧C/R不能提高或用新池抵扣。申请新 `DirectStepsLedger` 分池记录capture与每个restore/roots操作；lower-only override、一次使用、成功转移retention、失败清引用但累计费不退。额外池可使新解释模式更早有限失败，不宣称原最大图现在可解释。

固定物理上界沿6c：`MAX_TRIPLES=100000`、`MAX_WORK=1000000`、payload+rows联合`M=8388608`字节。新capture只走profile meter路径：每候选原有charge1+append debit3，因此被接受的全程候选数A≤250000；失败attempt仍先对本次新动作计费/限额。步S≤100000−N（N为真实seed去重三元组数），E=2S、depth≤S；不是A=S。新池另限制累计新索引key字节K≤M、carrier编码字节B≤M，整payload+rows仍≤M。所有限额均为提案，不是容量验收。构造计数器/容器前先开固定128-unit控制票；不足128不初始化池容器。

**索引实现约束**：不另 reason，不对每步扫描全图。新增TripleKey→leaf/step索引采用有限二叉byte trie（UTF8、三段显式长度前缀），每字节8次边访问；node至多 `1+8K_unique`、每node固定2槽，所有构造/边访问/原字节复制预扣。key encode先按原str字符长度预扣UTF8最坏4倍，再分段写入有界buffer，实际每次重复编码/比较计入K；累计K而非仅unique长度限额。候选只增加固定tag/slot，不重新生成key或排序；借用原已生成真实key，索引所需新拷贝另计。禁止把native dict/hash lookup、全串比较或sort当无成本无限操作；若owner复用另一已证有界索引，须给相同精确计费证据后改本实现申请。

| 发生阶段 | 每次实际新增工作的计费规则（逻辑单位，不是CPU/RSS） | 同时持有内容 |
| --- | --- | --- |
| 候选产生/首插入 C_D | 每候选8 traversal、4 objects峰值票；每step32 traversal、12 objects；每索引字节16 traversal、2 scan/copy；每新byte复制1 scan/copy | 本批候选A_live、临时SeedKey、全steps、索引、原closure/proofs和既有key同持；借用新增引用也预留D票，原物料实际保留责任另列，不能由旧L推断物理字节已收费或释放 |
| leaf linkage/全result coverage | 每实际表项/边/字段访问1 traversal，str比较按访问字节，union每输入leaf occurrence与每输出leaf引用各1 traversal并各预留slot | 原proofLeaves/evidence仍活；新DAG临时与其核对表同持，完成核对才释放临时票 |
| 新 JSON 投影/冻结 | 遍历字段/数组槽每项1，复制str/bytes每byte1；新carrier B字节编码/解码buffer各先预留；int仍走原bounded codec | native carrier、projected tree、encoding buffer、payload/rows buffers与原字节同时计峰；不得仅保最后一份B |
| R_D 每次接收 | schema/type/ref/template/depth逐项计；leaf-union DP逐实际输入/输出收费；canonical key索引创建/查找逐byte计；完整冻结/receipt计 | incoming payload/rows/preimages、raw解析树、typed view、索引、leaf-DP暂存、原恢复batch、opaque revalidation同时保票；每R_j新池，不能缓存跳过最后字段 |
| roots/S | 目标与全结果索引实际访问计费；一旦输出完整selected物料，输入J、扫描字段V、输出J_S与所有重编码/复制均按全量计，不只新字段B | root结果若借view，则H保整个view/bytes/indices；不能按root数量计retention |
| T/持久化复制 | 每次真实serialize、hash、拼帧、copy、parse按实际完整J=payload+rows+必要前像计；已有C/R的whole-stream预算也必须用实际新J | 发送缓冲、接收缓冲、Store bytes和解码对象同时保票；不得把Δcarrier B当成每次全流复制的收费量 |
| H/退役 | 接收之前reserve实际转移票；旧current变history/retired仍按实际引用承担，drop引用后才归还live票 | source/原件、视图、steps、所有共享返回引用的真实责任，不因R.cleanup/live0免H |

新ledger累计域精确为work/scan_copy，live域为objects/scalar；表中的traversal统一记入work，所有copy/encode/compare扫描同时计work和scan_copy，不能只减live。stage为entry/capture/link/encode/restore/roots/receipt/cleanup，new→running→completed或failed；复用拒绝，不改前次票。费用上界用“有限池+实际动作扣费”确保失败终止，不预言运行耗时。capture固定项目的分析子界为 work `128+8A_cap+32S_cap+16K_cap`、objects `128+4A_cap+12S_cap+4(1+8K_cap)`、scalar `128+2K_cap+4B_cap`；这些是分析子界，不再开一个可重复借用的work钱包；所有项目合并计入同一work/scan_copy通用上限，leaf-union/coverage等也扣同一池，不能漏记。work/scan_copy各设lower-only `64M+128(A_cap+S_cap+1)`，objects/scalar仍按实际reservation受本池与8MiB总流门双约束；若所有项目之和超限即有限失败，不得额外借原L。预算模型JSON列整数展开，属于静态算式，不是实跑usage。

接收端叶DP最坏复制可达N×S；实际扣费且被通用池截断，不能仅以2S直接边承诺线性整体空间。每步leafset用有界索引/bitset，输入/输出/排序均收费；若使用bitset，每次读写的全部machine word和零初始化也收费。不同时构造不收费的全路径树。

现C0预扣基于M覆盖整树投影/编码；R0原读流/strict child遍历按实际新J执行。新增模式的generic整流动作不因此免费；在对应原C/R记录后，新增D池可保守重复覆盖其新字段部分，但两池都不得事后退款或假称互相替代。T/S/H尚无本窗口正式实现/配额，必须由T01受理时独立保留各R_j与聚合Σ；K0…32每artifact的全部原费用/新费用累加，H跨current/retired保留。新JSON大于旧帧时保持真实分页/行上限，不能偷偷加frame或锁文件。

## 6. 原writer与精确源码申请（本轮全为只读）

所有现有路径旧ref/字节/SHA见 `source-window-request.json`；新路径oldSHA=null且本树不存在。根须逐路径授写，不把本申请当整commit/全树授权。原I05在独立实施树一次集成共享writer，T05不抢写。规则七quality模块、原restore_budget逻辑、material语法、Turtle parser、Store/worker/公共contracts/锁/构建默认delta=0。

| 唯一负责方 / 路径 | 最小申请delta |
| --- | --- |
| I05 `semantic.py` | optional exact private capture；四append tag与首次插入；新解释分支/version只传sink；原L与旧默认不变 |
| I05 新 `semantic_profile_directsteps.py` | exact record/有限ledger/index/局部DAG检查及内部roots；不import reasoner、不产输入/Job/expected |
| I05 `semantic_profile_production.py` | 新exact computation/API；真实occurrence capture与新receipt；仅records路径；失败全清理 |
| I05 `semantic_execution.py` | 新exact sink白名单入口和/3+finite8编码；旧私有入口保持默认；真实payload/rows联合8MiB门 |
| 根指定共享身份writer，建议仍I05；`resources.py`仅semantic_identity | explicit explanation bool分派；旧IMPLEMENTATION/registry/engine/lock不动；不是T01/S1/C2采用 |
| I05 `semantic_profile_restore.py` | schema2 exact expectation/decoder/fullview/局部图校验；原/1兼容分支完整保留；原child11不变 |
| I05 `semantic_profile_restore_budget.py` | **确需根新增窄写权**：read_json显式选择新增directSteps/steps/premises/depth四个fixed key的新表、原schema1表/默认/caps/TermCache版本不动；所有新D计费在新模块。不能把新增JSON_KEYS无条件放入旧全局表 |
| I05 新 `test_semantic_profile_directsteps.py` | 四finite规则/depth2/首witness/late-shorter/重复候选、有序前件、整流尾字段、全D池exact/差1、旧版本拒新key/旧输出不变；未来真实验证，非本轮执行 |
| T05 新两路径（后续另授） | `tests/fixtures/quality/profile-M1-graph-consumer-inputs.json`、`packages/engine/tests/test_profile_M1_graph_consumers.py`：只复制既有纯graph输入，外部goldens断言；不修改数学测试或原goldens |

`semantic_scopes.py`当前legacy selected不是profile实现；directSteps编码本身不需要改它。请将新profile scope消费列成后继精确窗口：由I05新增函数接受已经严格恢复的fullview及真实输入，直接取已有rdfs/rules生成scope，source由真实T01已绑定上下文供应；不得调用旧prepare_validation_scope（它会reason）或删字段喂五key函数。原T04查询、T05检查、T01权限/选定版本各归原owner。单对象安全裁剪/正式selected carrier不是roots API的能力，须单独冻结对象/支持依据可见性、完整selected schema、Σ/S/H与版本分派后再授，不能用本稿隐含补齐。

## 7. 实际消费者与可并行切片

各切片先保相同固定输入、expected物理分离。I05共享writer单一owner串行集成；独立fixture/断言/规范对照/补源可以并行，不等待所有FR整体完成。消费者状态只按后续实际观察记，原数学已收件结果不重跑来凑覆盖。

### A. 五个完整补充graph

| 原5962B的case/pointer | 最小真实链与断言 | 前置依赖 |
| --- | --- | --- |
| `/cases/0` M1-complete-heads | actual source→typed RuleSpec/Catalog→producer→strictfullview；2个originalMatches（s1 true/s2 false），3个head occurrence但2个RDF结果；01与1 term/source分开，typed值相等；完整when/bindings/comparisons/basis/定义ordinal/source逐项核 | 内部fixture binder可按实际语法完成并显式标fixture来源；正式保存JSON binder/T01物料供应另列，不能从golden取catalog。此图**不依赖directsteps**，可与I05 DAG开发并行 |
| `/cases/1` M1-false-then-error | 同实际when绑定v integer0、w string1；按定义顺序先false再类型错误；整体失败，无payload/heads/batch/restore成功，核实际diagnostic/原adapter；不能只看无head | 已有真实compare循环逐项执行后才all，原质量机制无需变更；测试输入可并行准备。它补本图顺序，不冒充完整false后错误/资源矩阵或持久false trace |
| `/cases/2` M1-direct-step | domain得x:A depth1，原有序ref为[domain公理, x-p-y]；再type-via-subclass得x:B depth2，[step0, A-subclass-B]；三leaf union与两条直接边分开 | 新DAG carrier/API；纯图规则为空且无需declared Catalog，不补规则 |
| `/cases/3` M1-direct-range | [range公理, x-p-y]得y:C depth1 | 同上 |
| `/cases/4` M1-direct-subclass-transitive | [A-subclass-B, B-subclass-C]得A-subclass-C depth1 | 同上 |

预期的l0/d1是9333文档符号，**不是新producer ID**。未来断言按真实leaf triple/ordinal关联映射符号，不把l0或d1喂生产。原R04 oracle t0117/t0116→t0063 depth1继续只读，不用新depth2替换。新first-witness/late-shorter反例输入必须T05独立另写并经根授新fixture，不从actual反生expected；既有五图不包含这些覆盖，不能声称已覆盖。

### B. 原83及E5/repair补源

E5真实源为既有 `tests/fixtures/product-baselines/E.5.json` 的initialFacts/rules/16 events（原供源169895B/SHA见9333manifest），由T06/T07执行每轮事件→行为前推理→冻结条件→行为→capacity→轮末推理/原子commit；T01供真实version/Job/消费队列/历史与选定快照。原I05四累计片段不是完整原产品流：r1/r2为RULE_INPUT_BUDGET，r3/r4为WORK_LIMIT，原失败保留。新的directsteps费用不修复这些旧L错误，也不能提高L、缩事件或假称性能改善。

16个event match应分别保同一Equipment和各自alarm的High/Open/link，alarm rdf:type不是R-risk直接前件；同一个输出head不能替代16次真实操作。T06/T07可并行准备完整snapshot/event/source包，I05独立定位旧debit；须新授权后真实消费，不先把预期metric当actual graph。

repair由T09（学习迁移源）、T02（实际定义/事实与ChangeSet）和T05（真实检查）确认missing rules是本来无规则还是缺档，补真实shape、修复前后asserted graph、rule定义/启停及版本；`ruleVersion`不能推出R-risk，空rules不能把未执行改绿。先Validator失败报告→真实受理修复ChangeSet→确认/commit→同scope重新check，再由真实新版本reason观察撤回/保留依据。T01负责基准冲突/undo/快照；T10报告消费另供真实版本。补源可与DAG并行，产品联验依赖上述真实提交链，不采用其WIP实现。

G-list-13 selected object/最后确认edit/undo、迟到V1/取消/历史及其它原source gaps继续沿9333原pointer供源；不造equipment001或用整库reset代单次undo。原83依然逐ID列78成功/4失败/1未执行，只有新的真实原链通过才能更新，本文不写状态表。

### C. query/SHACL的13个独立消费者格

下列为9333固定输入/golden已有合同与6c静态入口证据，**本轮不查网络、不重新解释标准、不运行库**。每格未来先报告入口是否接收，再报告实际query rows或真实SHACL report；不把规则profile结果移植过去。

| ID | 实际入口 / 最小核验 | 与DAG的依赖 |
| --- | --- | --- |
| C-query-numeric-promotion | 原T04→I05真实query：16777217 integer与float同词法在query numeric promotion选中s；保完整bindings/term，不取rule exact false替代 | 直接asserted图，无DAG依赖，可并行 |
| C-query-type-error | string a < integer1 FILTER错误剔行，rows空，正常query结果 | 同上 |
| C-datatype-exact | SHACL datatype精确IRI，int数据与integer要求产生完整Datatype违规 | 直接graph，无DAG依赖 |
| C-langString | 6c `_shapes` datatype whitelist仍拒rdf:langString；需I05窄shape入口修复后实际conforms，保前门失败原件 | 可独立shape切片，不先称Validator已通过 |
| C-count-term-identity | 01和1两RDF term计2，MaxCount违规；可选value字段据实际report，不填假node | 无DAG依赖 |
| C-in-term-identity | allowed integer1不包括integer01，In违规；完整focus/path/value/shape/component/severity | 无DAG依赖 |
| C-inclusive-numeric | min/max等界integer2，conforms | 无DAG依赖 |
| C-inclusive-nni | 6c inclusive whitelist无nni，当前INVALID_SHAPE；窄入口修复后实际Validator自身比较 | 同独立shape切片 |
| C-inclusive-dateTime-equal | 显式offset等值双inclusive；6c当前numeric-only参数门拒，修复后期待conforms | 同上；不调用rule Calendar comparator |
| C-inclusive-dateTime-before | 比min早1秒，修复后完整MinInclusive违规 | 同上 |
| C-inclusive-type-error | 合法string数据与numeric界产生普通MinInclusive违规；入口失败与正常report分开 | 无DAG依赖 |
| C-inclusive-date-entry | date合法界6c INVALID_SHAPE；root/I05须先冻结date extension政策，两分支保留，不能用profile Dz通过定政策 | 独立政策前置，不能阻塞其它12格 |
| C-illtyped-entry | `_terms`先拒illtyped integer；SHACL规范预期Datatype违规另存，未到Validator不能算正常report已证明 | root/I05决定保前门还是新增Validator专用入口；本稿不要求放宽通用_terms或吞错 |

source shape均为原输入真实 NodeShape→PropertyShape；不重写为unsupported单节点。query/SHACL只在选“包含推导”scope时才依赖真实selected/fullview投影；直接asserted C格不依赖新DAG，也不必等待T01正式Job才能在获准组件窗口观察真实库入口。正式UI/受理/保存报告/权限则仍依赖T01/T04/T05。date政策未定格准确pending，其余格先做实际观察。

独立shape修复窗口由原I05唯一writer改 `semantic.py::_shapes` 的精确名单及对应tests；与DAG同文件不能多人并写。不得借directsteps申请默授该delta；本稿只列独立可授切片。`semantic_query.py`当前无证据需改，delta=0；不替换query/SHACL比较器或增加reason调用。

## 8. 根可直接派发的顺序与验收

1. 根先批准 §3–5 新版本/structured-only API/有限新池与 §6 精确writer清单；I05在新实施树固定采用6c，禁止改本已收件数学树源。T05内部graph fixture/断言及T06/T07/T09真实补源可并行，无共享文件写。
2. I05实现四规则真实首次插入+新codec/fullview/ledger，先新入口组件验证，再独立审查固定候选。所有原旧版本拒绝/行为回归、实际producer/restore 7/16/11与尾字段/差1必须执行并留首失败；当前数学7/15/11结果仅作旧已收件证据，不当新候选运行。
3. T05在根后续指定组合树消费五纯图，外部goldens逐字段断言；两规则图可在新carrier前独立完成。额外firstwitness/late-shorter/false后词法与预算错误/空词法null/尾篡改等必须另供明确输入，不夸大既有五图覆盖。
4. query/SHACL直接图组件切片可并行；包含推导scope、单对象selected、真实保存/跨worker/Σ/S/H另等T01提供真实来源/权限/资源与I05专门profile scope，不用roots或旧五key替身填平。
5. 每个新候选在实际授权窗口验证对应delta并独审，指定同版双外审/CI/目标OS/真人/合并门保持。新文档的静态检查不属于执行证据，不关闭父M1、原Goal或原83。

本轮精确输入、字段/算式静态检查、一次独立合同审查、首失败原件与最终manifest/receipt都位于 `docs/reviews/T05/profile-M1-directsteps-contract/`。仅使用Git/标准库读回，未运行产品、第三方库、测试、GUI或网络；因此未跑Prettier/npm/pytest，不伪报格式或运行通过。本文提交后返回root申请实际源码窗口。
