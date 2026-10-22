# I05 观察投影规范 R3 独立 delta 审查

结论：**Pass，限定于本轮冻结的私有投影设计模型 delta。** R2-01 的 wire 顺序与 RDF identity 唯一性缺口已闭合；未发现本轮需退回作者的新增问题。R1、R2 两份正式 Fail 及原始证据保持原结论和原字节，不被这次 Pass 覆盖。本结论不关闭 `wholeOracleComplete=false`、真实库分类、真实来源/发行/准入/预算、runtime、417 或父门。

历史全量 `git diff --check` **仍为 exit 2**，只指向指定不可变的 R2 raw diff 原件；不能称全 check 绿。精确只排除该单件的范围检查和本轮 revision delta 检查均为 exit 0。此证据保全例外与本次设计缺陷验收分别陈述，详见下文。

## 1. 固定身份与独立性

本审查为原独立 R1/R2 审者对 R3 的最小 delta 复审。承接已读设计窗、setup-proof、当前树 AGENTS、R1/R2 正式报告、纯合同/固定输入及获准字面来源边界；本轮全文读 R3 disposition、当前 model/spec、新 selftest-r3、实际完整 delta、验证、manifest/receipt。机器证据逐项核所有清单字段及对应 Git/current 字节，未靠作者验证结论替代独立运行。

| 项目                      | 固定身份                                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------------- |
| worktree/cwd              | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-observation-projection-spec`                   |
| 原 base                   | `5f910b52c69d86a1076b2032e5d3c63e715947f3`                                                          |
| revisionBase              | `755326a26306f5bce0f36c172bd4994c7340f235`                                                          |
| candidate                 | `49e55cfdc68adca7f04faaf4f2335d1072553045`                                                          |
| process/审查 HEAD         | `fb7dfbb676cd1f09030ab508a3625284bfd6d9e4`                                                          |
| manifest-r3.json          | 25501 bytes；SHA256 `f8aac6b92326cfa094db7f2deadc498cd0bcfb96ba6948013bd2fe6f458c70f6`              |
| candidate-receipt-r3.json | 47004 bytes；SHA256 `91055f397914c55a735aed645084c542d342d644595998be22f744f648776e66`              |
| 保护 AGENTS.md            | 15852 bytes；SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，原有 M 保留 |

独立核 candidate delta 恰为 21 件：两个既有 tracked 修改 `model.py/spec.md`；新增 `selftest-r3.py`；review 前缀新增 delta/disposition/manifest、validation、两次 selftest 的四流、作者 formatter 的四流、三种 diffcheck 的六个 JSON 载体，共 18 件。process 相对 candidate 只增加 `candidate-receipt-r3.json`。完整 diff 不截短，另以 lossless UTF-8 JSON-string 载体保存，不新建原样 raw diff 文本。

manifest 的 119 条成员记录、receipt 的 120 条 candidate inventory 记录逐字段独核；manifest 自排后构成 candidate 120 件，再加 receipt 得 process 121 件。121 件每件 current bytes 均等于 process 的 Git blob，逐件 bytes/SHA 在 `r3-proof.json.results.fullInventory`。`delta-r3.json` 的 99 旧不可变件逐件对 revisionBase 的 Git blob、声明 bytes/SHA 核同；没有用新清单覆盖旧原件。

整个 `cases.json` 与 revisionBase 的完整解析对象相等，37 项输入/parameters/hash/expected/独立数学及源引用都未改变；`schema.json/pure-sources.json/selftest.py/selftest-r2.py` 原字节不变。99 件不变性同时保护旧 source-ledger、literal excerpts、获准 source/defaults/enum 裁剪及各轮报告/原件。来源承接的是此前已批准的纯合同、固定 0e42 输入、3d8f 独立 expected/coverage 和局部字面/数学；没有重新读取未授权产品函数体、原算法、actual、日志、费用 WIP 或调用产品。

## 2. R2-01 闭合：先验本端 wire，再比数学身份

关键实现为 `model.py:274` 的 `matches`：expected schema → observed schema → expected 本端全部 graph 槽 → observed 本端全部 graph 槽 → 全 terminal 共享身份关系。独立包装当前纯模型入口观察调用次序，正常路径恰为这五步；observed 图 wire 非法时止于第四步，没有进入会集合化的 identity helper。此包装只存在于独立进程内，finally 恢复函数，没有改候选文件。

`model.py:353` 的 `canonical_graph_wire` 在任何集合归一之前检查原 rows 的完整三元组：表达合法、subject/predicate 位置正确、原 N3 三元组 key 升序、RDF identity 唯一。排序 key 保本端原 BNode 标签和原语言拼法；identity key 仅对语言身份 casefold。`model.py:379` 的槽门逐端按各自 layout 找所有 typed-graph/n3-graph。它不排序、去重或修复输入，也没有把 ordered occurrence 当 graph。`spec.md:180–196` 与该顺序及有限表达域一致。

审者按字段独立枚举图槽，未用模型 layout 生成预期枚举：legacy rdfs/rules、rdfsEvidence/evidence 的全部 basis、scope facts/ontology/reasoning_result 及 selectedFacts 每个 source/derivedAxioms 的全部 basis。37 项共 **85 槽**，与实际 layout 的 graph 子集逐路径相等，原 complete expected 全部通过，原 golden 无需改值。

| 独立反例           | 核验与结果                                                                                                                                                                             |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 三个指定 ID        | `rdfs/cycle` 的 8 条 rdfs、`rdfs/domain-depth2` 的 3 叶 basis、`scope/fresh` 的 9 条 facts 逆序，schema 仍合法、identity-only 仍相同，expected 或 observed 任一端篡改均被 matches 拒绝 |
| 扩展到全部可逆图槽 | 46 槽各反转两端，共 92 次拒绝；完整对象不被修复/变更                                                                                                                                   |
| 相同 JSON 重复     | 77 个非空图槽各插入原成员，两端共 154 次拒绝；schema 的 uniqueItems 先拒，原有效门保留                                                                                                 |
| 空到非空           | 8 个空 graph 槽插入一条本身合法且 canonical 的新三元组，两端共 16 次拒绝；门合法仍不等于完整目标相等                                                                                   |
| 已排序语言别名     | typed 与 N3 图各含 `hello@EN` 和 `hello@en`，两成员 JSON 不同、schema 合法且本端已排序；observed 坏、expected 坏、双方同坏均拒，不能被 set 吞掉                                        |
| 单个语言拼法       | 单个合法 EN 和 en 仍能按 RDF identity 对应，不把 casefold 扩到词法或 source                                                                                                            |

R2 所需最小 delta 已具可执行入口及测试，没有改 schema/golden 来避免原反例。数学 helper 继续允许同一图集合的不同枚举，这一行为本身不再用作 wire 放行证据。

## 3. 有限表示门及合法改名正例

`model.py:284` 校 typed exact term keys/type、UTF-8、有限绝对 IRI/blank label、language 与 rdf:langString 关系；`model.py:318` 只读取既定 serializer 的单个 N3 token，并要求 `n3(decoded)==原 token`。这不是 Turtle parser、完整 RDF 库或 datatype 值验证。数值/date 词法政策没有重算。

独立构造 15 个 schema 放行的 N3 坏 token：显式 xsd:string、`\u0068` 替代普通 h、非规范 `\/`、未转义 LF/TAB/CR、含竖线/插入符/花括号/反斜线的 IRIREF、relative IRI、空语言、不完整 language、langString 无 language、越出本有限 blank label 域。完整入口对坏 expected、坏 observed、双方同坏均拒。另有 7 个 schema 放行的 typed 坏图：非法 IRI、literal subject、blank predicate、string datatype 配 language、langString 配 null、非法 datatype IRI、孤立 surrogate。补充独立命令对这 7 项三种端配置分别核验，共 21 次拒绝。没有通过修改 schema 或调用第三方来得出这些结果。

合法正例使用每端自身 canonical 的交叉 BNode 改名：左图 a→x、b→y；右图 p→y、q→x；统一映射 a→q、b→p。typed 与 N3 两种图的完整 matches 均通过，N3 反向比较亦通过。独立 N3 正例同时有 distinct rule evidence、跨节点引用和重复 inputs，映射在图与所有 evidence 槽一致；只改某条 evidence.result 指向冲突节点即拒，删输入尾或加 evidence occurrence 也拒。不是按数组下标 raw exact，也不是逐片段各求一个映射。

合法 `word@EN` 词法、integer `01`、int `1`、正确转义 LF、Unicode é 自身匹配通过；将 quoted lexical 的 EN 改 en、integer 01 改 1、integer datatype 改 int 均拒。语言归一仅作用于 RDF 身份后缀/typed language，未改引号内文本、数值词法、datatype、raw/source 原文。

这些带 BNode 的构造是 detached serializer 数学正反例；不将临时改 facts 后仍保原 digest 的抽象外壳冒称有效业务 scope，不证明真实 BNode 摘要或来源绑定。合法双方本端 canonical 与业务源关系必须分别验收。

## 4. 既有修复及完整值回归

原 20 + R2 新 12 + R3 新 9 = **41 个方法**实际运行 exit 0，完整 stdout/stderr 分开保留。作者首轮 40 和次轮 41 的旧双流都全文读回且保留；审者运行是新的独立 argv/双流，不覆写它们，不运行会覆写 R1/R2 proof 的旧审查脚本。

| 原发现/边界               | 本轮核验                                                                                                                                                                                                                                                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1-01 不可信 stage 泄漏   | 模型 `23–26/206–223` 保 exact str 先行；独立对路径、URL、未知/空字符串、None/bool/int/list/dict、str 子类、危险对象共 11 输入，分别调用 unknown/safe_projection 共 22 次，全部仅返回固定 collection-failure/Unknown/INTERNAL_ERROR/incomplete，schema 合法；危险 diagnostic 与外来对象的属性、eq/hash/str/repr 均未被触碰 |
| R1-02 语言及 BNode 联合域 | 原 12 方法含 typed/N3、provenance、query、SHACL sourceShape 的全域矛盾反例；本轮全通过。额外 canonical 交叉正例与 evidence 冲突反例通过预期；不退回片段同构，不折叠不同节点                                                                                                                                               |
| R1-03 API/参数            | 原固定 cases 与调用记录不变；shape/front-2 保 ee2b L51 的 data parse(shapes=False) → shape parse(shapes=True) → check_shapes；integer 保 L52 的 validate_shacl_text，data_policy=integer-illtyped-report-v1/range_policy=legacy，原 camelCase parameters/hash 不变；对应旧方法通过。没有把批准签名当真实首错实测          |
| 非 RDF/source/摘要 exact  | 原联合域测试验证 raw/source/null 不参与改名；布局仍仅声明 RDF 槽，未声明字段完整 exact。模型 `467–542` 全域映射、keys/type/null/数组长度仍保留；摘要字段没有被忽略或重写                                                                                                                                                  |
| ordered occurrence        | 原20/12及新9继续测 when 顺序/重复、多个 head、inputs/evidence 尾及 occurrence 数、source/SHACL 全尾。新门只碰 graph 槽，序列在原完整 identity 比较中保全                                                                                                                                                                  |
| 正常误拒/Unknown          | 37 个固定 expected 均匹配自身；37 个 Unknown 均不能匹配任何固定目标；13 个正常 × 24 个已知拒绝 = 312 个替代全部拒绝；没有任意 known error 或 RESOURCE_LIMIT 通行                                                                                                                                                          |

完整 37 ID 的分类仍为 11 legacy 域（10 正常 + unbound-head 拒绝）、3 scope、14 restore、1 DAG text、7 前门、1 implicit-jsonld，共 13 正常/24 拒绝。旧独立 expected、五字段全图/证据/basis、scope 四项及 source/digest/null、14 项 held expectation 与 A1 preflight 的新提案前置关系全保持原值。wrong/missing result/source、unselected、implicit-jsonld 不被宽化成任意首错。上述旧内容的数学/合同审查承接原轮结论，本轮以完整对象/字节不变性和旧方法回归核保护，没有声称重跑产品证明全部首错。

## 5. 入口、schema 与 pending 的边界

`projection_identity_equal`（model.py:545）现明确标注为数学身份关系，wire 调用者必须用 matches；`identity_domain_equal/graph_isomorphic` 的集合化只发生在关系 helper 内。R3 新实际完整比较入口已先 gate，独立轨迹证实坏 wire 无旁路进入 identity。当前有限设计没有产品 harness consumer 实现，本结论不能证明后继集成已调用正确入口；serializer/oracle owner 后续必须保持 spec.md:192 的唯一完整入口要求，不能以 helper=true 作为 oracle-match。

schema 仍只承担既定严格 JSON shape/type/null/required/extra/完全相同 JSON uniqueItems；语义 canonical 门补充 schema 放行的表示与 RDF 别名，不让两者互相替代。非 graph 的 RDF occurrence 按原完整序列/身份关系比较，本轮没有把所有数组统一排序，也没有扩成全 RDF 表达接收器。固定37均通过说明有限门与现有完整目标自洽；抽象图正例只证明有限 comparator 行为。

最多 8 BNode 是独立小例/枚举模型的界，不是产品容量、性能或准入额度。跨独立 parse/producer artifact 的真实身份绑定仍 pending，不能仅凭相同 label 合域；图到 query/SHACL 的真实所属关系也需实际 harness 提供。内容 source 是提案 display 摘要，不是公共 DTO、旧 metadata 替代入参或 authority。真实 BNode preimage/hash 标签差异没有被全域映射消除，实际 digest 兼容需 owner 单独接收版本和关系。

F1/A1/O1/D1 新精确首错仍是待 owner 接收的技术目标；原14 held bytes 与真实准入前提必须同时成立，未到达保 not-reached/pending。integer 例外只限 data object 的 exact xsd:integer ill_typed，不扩到 int/nni/decimal/shape。公共 strict 四字段 ErrorFrame、registry、Q6/date/外联/权限、真实 issuer/capture/预算、旧 metadata 完整载体均未改变或关闭。没有制造 17L/planDigest/usage/sourcecapture，也没有新 T03 外部票。

## 6. 命令、证据与已知非零

所有设计运行使用指定 `/Users/kyle/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`，`PYTHONDONTWRITEBYTECODE=1`。先静态读/AST 核四个候选脚本及独立脚本的 stdlib imports 和写入范围，再执行有限 detached 模型。没有产品/第三方 import、网络、安装、版本探针、旧 helper/tests、probe、pytest、npm/build、native/DB/GUI 或外部模型。

| 实际命令范围                             | exit | 意义                                                                           |
| ---------------------------------------- | ---- | ------------------------------------------------------------------------------ |
| 独立固定树/清单/完整值检查 runner        | 0    | 121/99、清单 bytes/SHA/Git、完整37、原件、实际 diff 范围；内部首个非零命令另保 |
| selftest-r3.py                           | 0    | 原32 + 新9，41方法；独立双流                                                   |
| r3-independent-boundaries.py             | 0    | 85槽、双方篡改/别名/有限表达、合法 alpha、词法及拒绝替代                       |
| r3-independent-regressions.py            | 0    | 不可信stage 22次、typed 表达两端补核21次、空图插入两端16次                     |
| 全 base→process `git diff --check`       | 2    | 唯一指定历史 raw 原件的28条 trailing-whitespace 诊断；stderr为空               |
| 同全范围仅精确排除该单件                 | 0    | 不排整个 review 前缀，不排其他证据                                             |
| revisionBase→process `git diff --check`  | 0    | 本轮实际新增/修改范围                                                          |
| 新独立报告 Prettier --check              | 0    | 只检查新报告，实际 argv/分离双流见独立 proof；未格式化任何候选/历史原件        |
| 最终 frozen bytes/HEAD/index/status 复核 | 0    | 候选121件、保护AGENTS保持；仅本审新增允许文件                                  |

唯一历史 raw 为 `r2-independent-full-diff.stdout.txt`：128276 bytes，SHA256 `13c4471bc5518f354b8315220c14b8fbd5f722c722075ed93c1fc29183b01477`。审者重新计算其原固定 57c67631fab6a36f47963aca95b4036064e10777→1e753a82b837fb53f0389dabf1c401d89809238c 的 Git diff bytes，与原件完全相同。原上下文空格不得 trim/formatter 来换绿。root 原先未等待依赖检查便提交的顺序失误说明在旧 receipt 中保留；当前两种局部 exit0 不抹掉 full exit2，这不是产品失败。

本轮完整 diff、失败流及独立模型运行流用 UTF-8 JSON-string 载体保原 bytes、SHA、text；反编码 roundtrip 核同，载体自身另有 bytes/SHA。重复只读 Git blob 输出以已逐字节核同的固定 ref/当前原件引用保存，空 stderr 显式保空；不重复复制原件。没有再生成会携带原 diff 上下文空白的新 raw 文本。`r3-proof.json` 保实际 argv/cwd/独立 exit、双流 identities/内容引用、首个非零命令、121清单及独立结果；不把工具首 stdout 截断当原件。

两条额外只读定位误差单独披露：恢复上下文后误用不存在的 `docs/specs/.../model.py` 执行 sed，exit1；随后 rg 带不存在的 `docs/specs` 根，虽列出 review 匹配但 exit2。已改用真实 `docs/iterations/I05/...` 路径全文读取；它们未写任何文件，不是模型/产品失败，也没有冒称所有探索命令 exit0。正式可重放验证命令与分离流均另存证据。

## 7. 审查处置

本轮无新增需要作者修改的发现，R2-01 在冻结设计范围内闭合；原 R1 三项修复未见回归。保留所有原 pending 与历史 Fail，本 Pass 仅允许 root 接收这份设计 delta，不能直接转换为产品、真实来源/费用/runtime 或父门通过。

审者只新增本报告、独立 proof 与 `r3-independent-*` 命令/JSON载体；未 stage/commit/切分支/push，未改 candidate/旧报告/旧证据/schema/tests/AGENTS。报告与 proof 的最终 bytes/SHA 由本轮最终保全记录及交接消息给出；proof 不自含自身 hash，避免循环声明。
