# directsteps 18908e4：来源、schema 与生命周期独立审查

结论：**不通过**。固定 `18908e4abca900a07a15a5d157d4022f2a11349a` 存在三项 P1：精确类型前门之前执行 foreign 协议；leaf ID 未按实际 TripleKey 的原算法核验；roots 信任未与 typed firing/head 绑定的 saved evidence，可返回不存在的 occurrence。另私有 closure 缺 exact sink 门并实际执行任意 callback，归入第一项修复范围。根已确认并开始修复，以下结论仅针对旧固定候选，不能视为对新 WIP 的判断。

通过依据和限制也完整保留：真实首次插入捕获、版本分派、四模板/seed identity/DP 的主要实现及定向正常/故障测试确实存在；这些不能抵消下列实际反例。预算充分性由另一独立审查判断，本报告不签预算通过，不将组件成功外推成正式 Job/selected/权限或整个 I05 成功。

## 输入、固定身份与方法

- 唯一树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-directsteps`。
- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`；adoption：`78e9cf7f26dc039e99ec6725d7de8a396d1298d2`；被审产品：`18908e4abca900a07a15a5d157d4022f2a11349a`。
- 完整读取本窗口 inputs 的窗口/指导/合同/预算及 source 请求，完整解析固定139和 candidate141；读取树外 `I05-directsteps-layered-closure-acceptance-correction.md`，其1535B/SHA `250c1a0f3ffe6d7a1c6a566eb81140d19d6eb24d564316ca7db448083174a85f`。更正的按轮闭包事实适用：真实后轮更短 height 不可达；不能为该测试制造另一推理次序。
- 合同34958B/SHA `c947430801e6b3cca113c15a856704c3d5bed418efa9083d67819830a6961fba`；窗口5942B/SHA `9e9091f4f5f565e437bc45ee74476cb5f77e19858fcef783892f54d4adf50f55`；139固定清单57687B/SHA `e5fe75cbf07436660fc475b5ac6c176c40fff35f00e1aad1250b7d967ef149d5`；2180B预算模型/SHA `74e03d64e7fb80b1d4340779f842232c46fd7a3333d959e663b4b6fc8f674d51`。
- 逐项独立核141当前字节=固定 Git=候选 bytes/SHA，139初始采用等各自固定 sourceRef/adoption；133只读逐字等 adoption，实际差异恰六旧 writer+两新件。完整清单及全部授权原件 hash 在 `static-input-manifest.json`。
- 阅读八个产品/测试 writer 的固定代码或完整实际 diff、相关原 parser/decoder/formatter、纯模块作者 handoff 和独立测试作者交付。作者 handoff 是待核主张，不是独审证据。新模块1192行、新测试922行已全文读。
- 三次独立产品运行均保存 argv/cwd/env/head/完整双流、141项 sourcesBefore/After 和实际完整 D 费用事件。`runtime-source-binding.json` 再次将三次前后来源逐项核同旧固定 manifest，均为189、exit0、timeout=false、stderr0；探针 exit0表示完成观察，不表示被观察的漏洞符合要求。

| writer（共同前缀 packages/engine/）                     | bytes | 固定 SHA-256                                                       |
| ------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| src/ontolearn_engine/resources.py                       |  3065 | `177f57db2c3e768b9fc17d0c9e0665677e6aab55c16003ac7f304254c10d2238` |
| src/ontolearn_engine/semantic.py                        | 55567 | `b86619ce20fb5ae861c32219900a4afff86a66c91675d15ae3cea46ec68a0b80` |
| src/ontolearn_engine/semantic_execution.py              | 35035 | `f9e7450d5825fc9e9264a2c5728b3a42baf31a275a3b265c68ff616636bf83cb` |
| src/ontolearn_engine/semantic_profile_production.py     | 17511 | `228c12686afcee65e1c0c3871a4aac168a5de5e54b7a459e594edd614775cf77` |
| src/ontolearn_engine/semantic_profile_restore.py        | 67018 | `31c87a98ecc1d4f8de9095ce159e2dfbb76449213b70f51be08454ab64f2b290` |
| src/ontolearn_engine/semantic_profile_restore_budget.py | 37889 | `ffde8fd243696ab4e8812e8994e6a8fc2b5832f411e5fdf1e4c7753fe19c93d0` |
| src/ontolearn_engine/semantic_profile_directsteps.py    | 46459 | `7927769077e363b23741f6dc78b7c0ec2ad00b7d3285f8403a190c0e00169b22` |
| tests/test_semantic_profile_directsteps.py              | 35520 | `030d29b25542d7f6f8224aa1c8a4399cb48360ba0e29209ea8abe77cff4b5ce4` |

以下源码行号均指189固定 ref，源码前缀为 `packages/engine/src/ontolearn_engine/`。

## DS-O1 / P1：新增路径在 exact 类型门之前执行 foreign 协议

位置：`semantic_profile_production.py:73–102、249–264`；`semantic_profile_restore.py:1051–1058`。附属私有 sink 门：`semantic.py:385–409`。

新解释入口在 `_prepare_profile_material` 与四组 exact bytes 门之前调用 `_direct_bound`，并在255行直接 `len(material.input_preimage)`、`len(material.definition_material)`。`_direct_bound` 第84行使用 `kind in (tuple, list)`，不是 identity 判断；foreign metaclass 的 equality 可以在拒绝之前执行。新 expectation 路径在1057行比较 `e.input_domain`，1058行才检查其 exact str。

实际最小反例见 `counterexample-probe.py.raw`、`01-counterexample-observations.json`：先通过真实 `prepare_profile_material(records=())` 得到 exact ProfileMaterial，再 dataclasses.replace 单字段。

| 污染位置                                              | 实际回调     | 最终结果                        |
| ----------------------------------------------------- | ------------ | ------------------------------- |
| input_preimage=Bomb（__len__记录并抛错）              | len一次      | DIRECT_STEPS_INTERNAL，reason=0 |
| definition_material=同类Bomb                          | len一次      | DIRECT_STEPS_INTERNAL，reason=0 |
| source=(ClassBomb(),)，metaclass.__eq__记录           | class-eq两次 | DIRECT_STEPS_INTERNAL，reason=0 |
| exact ExplanationRestoreExpectation.input_domain=Bomb | eq一次       | RESTORE_INPUT_INVALID           |

有限错误与无 cause/context 不能撤销已经发生的 foreign 协议执行。annotation/frozen dataclass 不保证嵌套字段符合类型，故新 wrapper 绕过了原 data-only 的零回调前门。

另按合同§2，私有 `_finite_closure` 也只应接受 exact `_DirectStepsCapture`。189没有该门：对真实 type/subclass 图传入带 candidate 方法的 ArbitraryCapture，该方法实际收到 `rdfs9-type-via-subclass` 并执行，随后原 RuntimeError 直接冒出。独立证据在 `03-roots-observations.json`；这是私有合同违规，未声称它暴露了公共 IPC。

建议：把所有传入字段 exact 类型/基本形状门置于首次 len/比较/递归/formatter 前；`_direct_bound` 使用 `is` 分派并拒 foreign 类。input_domain先 exact str 再比较；私有 closure 在任何候选动作前固定 exact sink、批准的模式。不为修门复制 matcher/PV/数学或放松旧语法。新增 public nested foreign/tuple subclass/metaclass、两组 preimage 与私有 sink 的零协议回归，不能仅断言最终异常。

## DS-O2 / P1：leaf ID 只查语法，未绑定原实际 TripleKey 算法

位置：`semantic_profile_directsteps.py:885–892、970–987`；`semantic_profile_restore.py:733–739 leaf 方法、1570–1607 _validate_explanation`。leaf 方法实际只解 reference string 与 triple key；`_leaf_id` 仅检查74字符、`i05-proof:`前缀及小写hex。

合同§3明确要求 leaf ID 对实际保存 TripleKey 按原算法核验。189的 `_validate_explanation` 校验完整输入 RDF identity/代表和 DAG，但没有补这一摘要关系；纯模块 docstring“caller already validated original leaf IDs”的假设在实际 caller 中不成立。

实际反例以真实 domain-depth2、rules=() 生产产物为输入，把第一条 proofLeaf.reference 从

`i05-proof:77222fa1fcdb5bf9db8db68a83c2e5e102fb6bdddab5461a6df385d6a11ade0b`

一致改为 `i05-proof:` 加64个0，并在该 payload 的 directSteps leaf refs / rdfsEvidence.proofLeaves 中同步替换。raw input/source/definitions/Catalog/原L与实际 leaf TripleKey 均不变。

- **原 expected 保持不变**：实际拒绝 RESTORE_INPUT_INVALID；外层摘要 gate 没有放松。
- **只重绑定新 payload/rows 两摘要**：189新 restorer 实际接受；sameInputSourceWitnesses=true，D ledger completed。错误ID并不等于原实际TripleKey的leaf摘要。

这不是要求摘要提供来源认证，也不是发现绕过原 expected。这里明确审的是合同要求的局部语义一致性：一个满足格式/一致引用、但不满足原 ID 算法的给定 artifact 不应获得新 DAG 校验通过。测试409–460的 last-ref 只改一处，能因悬空被拒，不能覆盖所有引用一致重命名的反例。

建议：在新解释接收链，对每条实际 saved leaf TripleKey 计算既有 `i05-profile-proof-leaf/1\0` + NUL连接三key 的 UTF8 SHA-256，精确核 reference；不要按任意 raw alias 的另一拼写算ID，不重写 raw/语言/source，不二次 reason，不重新签发 leaf。实际构造/hash/扫描应先取得本窗口新D票，由预算审核费用。新增一致重命名反例，保留原 expected 不变的独立拒绝断言。

## DS-O3 / P1：roots 可返回不存在的 rule firing/head occurrence

位置：`semantic_profile_restore.py:1646–1670`；其 `_Decoder.evidence` 只有各字段 schema/上界检查（`firingIndex<=1023`、`headIndex<=15`），未与已由16c核过的 firingGroups/heads 逐项对应。

roots 将 `reason['evidence']` 直接当作真实 head occurrence 表。新16c只验证原 typed firing/batch，并不替额外 aggregate evidence 认证其 occurrence。因而新 roots 的“只定位已有节点、全部真实head occurrence”承诺不成立。

实际反例见 `roots-probe.py.raw`、`03-roots-observations.json`：真实一个规则firing、两个重复head，实际合法索引为 `(0,0)`、`(0,1)`。仅将 saved evidence 第一行 firingIndex 改1023、headIndex改15，原 typed firingGroups、PreparedFiring.heads、batch、目标 triple 不动。

- 原 expected不变时拒绝，维持外层 gate。
- 仅重绑定 payload/rows 摘要后，restore接受。恢复期间禁止reason的guard未触发。
- 对原真实目标调用 roots，实际返回 `ruleHead(1023,15)` 和 `ruleHead(0,1)`；第一个不存在，真实 `(0,0)` 反而丢失。

因此这也不是要求 roots 认证 Job/权限，而是它未能履行最小只读定位合同。现有707–743行正例只证明诚实 producer 的 aggregate evidence 正确，不能覆盖字段间不一致的给定输入。

建议：新解释恢复中将 saved evidence 与实际 typed firing/head、目标 triple、全局 firingIndex/HeadEvidence.index 完整核对应，或使 roots 只从已核真实 firing/head 建索引而不信任未绑定的 aggregate 行；确保不返回不存在的ref、不丢同目标的其他真实occurrence。保持原fullview全部字段、旧/2行为及禁止二次reason；所需formatter/全量核对按实际新D费用复审。新增恶意索引、错误target、缺/多/重排occurrence与原多head正例。

## 已确认存在的实现与有限通过依据

窄 writer 权限：独立 AST 对照证明 resources.py 唯一改变顶层函数为 semantic_identity；旧 IMPLEMENTATION、registry/锁/全局 LIMITS未变。restore_budget.py只改变 `_Reader.__init__/fixed_key` 与 read_json schema分派；JSON_KEYS原表、默认schema1、R caps/TermCache及其版本 AST未变，新schema2只增directSteps/steps/premises/depth四key。证据为 `narrow-writer-ast.json`。

真实首次插入：`semantic.py:385–471` 保原排序键 `(key(result), ordered input keys)`；四生成点只附固定tag。第459–460行在原 MAX_TRIPLES、meter debit/union后，实际 closure.add前捕获当前key、ordered前件与tag。已有候选都先通知D池，未入选和后轮重复未被免除；原 L 调用及旧 union 路径未被新池替代。`_profile_reason:980–995` 仅一次 closure，原 leaf ID 建立后才 link；1158–1161行 finish 全量 resolve 后才发布。接收只检查四模板、前向引用、depth及集合/DP，不全图枚举或补全闭包。

新纯模块仅import dataclasses和原TermInput，没有reasoner/Graph/PV/Job/网络。seed identity编码与原formatter链区分 IRI/literal、plain/explicit string alias、lower-language identity、integer01/1不同lexical；实际全部seed组和允许代表、唯一leaf、rdfs/evidence结果唯一完整覆盖、step连续序号、恰两个前件/无前向引用、四模板、depth和叶DP/basis都存在校验。DS-O2指出的是其中缺少ID摘要关系，不否认这些其他检查。

版本与原字段：旧默认仍 /2 + finite7 + schema1、内15；新入口显式 /3 + finite8 + schema2/direct1，外7/内16/child11。新 expectation 是独立exact class。执行来源仍由实际结构化 parser/material/defs/Catalog/原L捕获点提供，首入口拒Turtle，不从termSources拼seed。原typed fields/PV四字段fresh parse对照、source与input witness、payload/rows核验以及每槽原16c保留。fullview新readonly载体在整次校验后发布，未从RestoredChild补造原字段。

独立定向 pytest 实际 **12 passed / 53 deselected / 0.56s**，exit0/no timeout/stderr0；本树自有.venv、独占basetemp、`-p no:cacheprovider`、完整fee JSONL在 `02-targeted-fee-events/`。内容包括四模板/depth2/完整字段签名、同轮多个witness原sort首选、旧默认/新reader拒混版、多head roots诚实正例、四个实际晚期故障。

故障覆盖的真实生产receipt/新record、恢复新record和最后child注入都保持有限error、cause/context=None、无新native结果在公开traceback、PV发行表无新增残留；logical retained/live不因此宣称物理GC或免除H。未模拟OS OOM、进程强杀或正式Job取消。三个已确认反例恰说明正例/故障通过并不足以完整接收schema与前门。

## 测试与原始证据审计

新测试原35520B/SHA `030d…` 与独立test-agent交付完全相同，没有改expected/输入/assert求绿。四模板数学expected、同轮排序向量与sort-vs-generation反例由纯输入构建，并未从actual反生；observer只是wrap真实调用。受控duplicate helper明确标注非真实later-shorter图；树外更正保留原不可达要求历史，未修改实际闭包去配测试。原五T05图不被冒称覆盖所有这些新增向量。

根 `03-direct-special` 原10 failed/55 passed保留；`08-frozen-special` 在189上实际65 passed/1.21s、exit0/no timeout，根原fee事件和双流未被本审改写。作者早期uv/ruff部分原始环境/双流缺口已在handoff诚实注明，本审不补造。65项没有包含上述一致leaf重命名或不存在head引用，也没有public foreign字段回调断言；故不能覆盖这三项。

本审三个运行的完整记录是 `01-counterexamples.*`、`02-targeted.*`、`03-roots.*`；两探针观察结果另保存JSON，含全部相关D actor的实际events/usage/live/peaks/caps。旧C/R没有同样的D事件接口，不将D receipt冒作其费用；没有独立签预算上界。原expected污染拒绝与重绑定后局部缺陷分别留有原件，未放松外层预期来伪称认证漏洞。

根已告知09正常check在源不变情况下因采用作者的过程 `verify_static.py` 被ruff纳入而失败，正在按原字节归档为.py.raw；本报告不把它记作通过，不改原日志、不重复全仓check。后续根运行及任何新产品修复均须新版本证据。

## 限制与写锁

本审只写 `docs/reviews/I05/profile-directsteps/independent-origin/`，新增脚本从创建即 `.py.raw`。未改产品、测试、其他过程、AGENTS/依赖/环境/Goal，未提交、stage、切分支，未GUI/服务/模型/网络/付费。文档/JSON显式Prettier `--ignore-path /dev/null` 结果另存格式记录。

根开始修复后，本审停止全部产品运行与working源码读取，只读取固定189 Git和已保原件；三次运行的141前后hash再核均属于189。首审失败结论/反例不可被后续delta覆盖。新固定ref到达后，仅对实际修复和必要上下文复核，不沿用本报告宣告任何新候选通过。
