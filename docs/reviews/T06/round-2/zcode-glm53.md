# T06-S1 独立只读对抗审查报告（round-2 / zcode-glm53）

- 审查者：ZCode GLM-5.3 / 最高思考（会话实际模型 `account:bigmodel-individual-coding-plan/GLM-5.3`，环境自证；思考等级为派发指定）。
- 任务权限：本任务 UI 读回 GLM-5.3 / 最高 / 完全访问（owner 派发声明）。完全访问不改变只读职责：本审查未使用任何写权限改动受审内容，未提交/推送/切分支。
- 任务来源：owner 官方粘贴文本附件 40359 B / SHA-256 `74a96e1460d6bb81be3f5697616b93bc6bdfadeb72078ef52cd0664c1697e426`，与 `out/environment-prep/own-frozen-input.md` 逐字节一致（`cmp` 相等）。按其原完整要求执行全新完整独立审查，非旧 613 任务补评。
- 报告位置：本工作区 `docs/reviews/T06/round-2/zcode-glm53.md`（即本文件）；过程证据在 `out/GLM53-r2-evidence/`。
- **总结论：通过（仅限本独立 S1 范围 = 私有行为计划算法 + T09 固定输入只读适配，产品候选 3be0397）。未发现新的 P1/P2/P3 代码缺陷。P2-1 我独立裁决为"定位机制已修复"；P2-2 我独立裁决为"风险保留、当前私有 S1 范围非阻断、容量门不关闭"。全部历史 local-review 与 round-1 外审意见经我自行核验后逐项关闭或维持原边界（第 7 节）。父 FR-600–604 模块与完整 B 用例验收保持未验开放（第 8 节）。**

## 1 精确版本与基线核验（全部实际执行）

| 项 | 值 | 核验结果 |
| --- | --- | --- |
| 唯一工作区 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-s1-zcode-review-3be0397` | `pwd` 一致；detached HEAD |
| 流程 HEAD = 产品候选 | `3be0397faf03de6520c47bf7d86f3dc2fd004287` | `git rev-parse HEAD` 一致；本审查树 HEAD 精确等于产品 3be |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 存在为 commit（Merge PR #5） |
| base→产品完整 binary diff | 6075356 B / SHA-256 `569b98c2b6f16a18593fc3c3c8b17580f8df21672d04188549d7946cda9c916f` | `git diff --binary base product \| wc -c / shasum -a 256` 独立重算一致（plain diff 为 1215620 B / `fa879b62…`，binary 口径与派发一致） |
| 工作区状态 | ` M AGENTS.md` | 唯一 dirty 为获授权政策追加，保持未暂存未还原；无其他改动 |
| 13 项受审来源 | 见第 2 节表 | 工作区 = Git HEAD(3be) blob = 派发 manifest SHA 三方逐一相等（脚本逐件重算，`ALL 13 SOURCES BYTE-IDENTICAL: True`） |
| T09 只读缓存 | `out/t09-approved-873c8c0` 19 文件 | 与 T09 固定 Git `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 对象逐字节一致；manifest SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` 重算一致；未读变化中 T09 HEAD，未导入其 Python |
| 主 PRD | `/Users/kyle/Documents/工作/知爻/本体/PRD-本体学习与落地Agent工作台.md` | SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` 与派发一致 |

## 2 完整读取范围（全文，非摘要；真实 Read 链）

- 本树 AGENTS.md（工作区保护版）全文；官方粘贴附件 223 行全文受理并哈希核验。
- `docs/reviews/T06/`：review-readiness.md、status.md（均为 613 时代历史快照，按任务文本以当前事实优先）、local-review-1..6 全部原文。
- round-1 共同历史全文：zcode-glm53.md（19238B）、minimax-m31flash.md（25539B）、zcode-glm53-process-addendum-20261022.md、zcode-owner-audit-20261022.md、minimax-owner-audit-20261022.md、resource-remediation-plan-20261022.md、resource-remediation-independent-review-20261022.md。
- `out/review-common-history/`：local-review-7.md（22379B / SHA `b21c69b7…` 重算一致）、evidence/validation-3be0397.json 全文、baseline_613.py（SHA `9d2474a3…` 重算一致）、owner/独立两包及 unpacked 目录结构、owner 首败 `owner-first-failures/raw-tool-rows.jsonl`（40492B / SHA `8187b04d159b6e22fe2d2071cbb3216c9b95ad3857f722772f0f84066d4161db` 重算一致）与 README、独立首败 `measurement-wrapper-first-failure.json`。两包 tar.gz 字节数/SHA 重算与任务文本一致（62+61 regular 成员说明按 manifest 核对）。
- 13 源全文：behavior 三源码（planner.py 984 行、baseline_adapter.py 583 行、`__init__.py` 5 行）、五份行为测试（planner 489 / creation 161 / failures 327 / baseline_adapter 350 / resource_equivalence 317 行）、build_corpus.py 446 行、counterexamples.json 7863 行（结构化全量解析 9 例每字段 + 作者脚本内存重放 canonical 完全相等，作者脚本仅 import copy/hashlib/json/pathlib、不导入被测实现）、三个 iterations 文档（interface.md 56 行、t09-adaptation.md 35 行、probe_t09_baselines.py 223 行）。
- 完整 base→产品 diff：76 文件全部为新增（A）；其中 613→3be 的实现变化 diff 全文精读（planner.py ±319 行、interface.md、t09-adaptation.md、新增 test_behavior_resource_equivalence.py 317 行）；其余流程/UI 历史块只作流程证据核对类别，不执行归档脚本，不把 UI 或别线历史材料当本候选产品内容。
- 主 PRD 原条款：FR-600–604（7.7 节）、附录 C（能力矩阵）、E.1/E.2/E.3、G.0（固定基线）/G.3（B-01..B-11）、10.2 性能容量、Q5 原文（未替任何未决问题填默认值）。
- 未读本轮另一模型（MiniMax）round-2 的提示、会话、报告或意见；未读 UI 树当前材料。

## 3 实际验证命令与结果（全部无窗口，本树独立环境）

| # | 命令 | 结果 |
| --- | --- | --- |
| 1 | `uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q` | **exit 0，139 passed in 1.34s**（log：`out/GLM53-r2-evidence/pytest-behavior.log`） |
| 2 | `npm run check` | **exit 0**：lint/格式/类型/构建/ruff 通过，vitest 15 文件 630 测试，pytest **1191 passed**（含 139 行为；log：`npm-check.log`） |
| 3 | `uv run --frozen python docs/iterations/T06/probe_t09_baselines.py --source-root out/t09-approved-873c8c0 --manifest-sha aaaef2c0… --output out/GLM53-r2-evidence/T06-GLM53-3be0397-probe.json` | **exit 0**；9 例（B-01/02/03/04/05/06/09/10/11）完整 facts/orders/notifications/actionTrace/consumedEvents/triggeredInstances/conflict 比较通过；`product_runtime=not-executed`、`formal_acceptance=false`、manual gold 标注保留 |
| 4 | 自编探针一（stdin，零 .py 落盘）：`_first_conflict` 对直接 `combinations` 定义 oracle 的首冲突对等价 | 穷举二实例二值单槽序列长度 0..8：**510 例 0 失败**；穷举 typed 四值（0/False/1/1.0）长度 0..6：**299592 例 0 失败**；随机多槽/多实例/多值（含 create 多写、typed、多值槽）：**5000 例 0 失败** |
| 5 | 自编探针二（stdin）：旧 613（固定 baseline_613.py）vs 当前实现全管线差分，自有随机生成器 | **1500 例：473 plan / 1027 domain error，0 不匹配**；每例完整 plan 或 reason/location/evidence canonical 相等；相等输出滚动 SHA `13afccfa33fe22e79880a83a506f30b680880203f2edcbf8f6f998f4f7163aef`；无 unexpected exception |
| 6 | 自编探针三（stdin）：定向负例 | 先验证再索引（重复对象/重复事实/单值 false-0 与 1-1.0 矛盾均按原类拒绝）；notify↔create 身份碰撞两个方向均 `duplicate_identity`；事件删除/重建/入边清理正确；决定容器独立；输入跨调用不变、计划确定性且相互脱离——全部 OK |
| 7 | owner helper（unpacked 路径全文读后执行，SHA `25dfed41…`；仅读固定输入，输出写自有 out）`--mode equivalence --count 1000` | **exit 0**；1009 例：114 plan / 895 domain_error，全量输出/错误证据相等，rolling SHA `8fd07766b5e3bff41a07d0b0b4247c8f202dd120c216834712b7e6a6362cf160`，**与 owner 原记录逐字符一致**（独立复现） |
| 8 | 同 helper `--mode creates --size 800 --implementation current` | **exit 0**；wall **0.540088s**、800 决定/800 源动作；input SHA `400f6c00…`、完整 plan SHA `54644b52…` 均与 owner 配对记录一致（旧 613 同输入为 131.515803s） |
| 9 | 同 helper `--mode matrix --size 1000 --implementation current` | **exit 0**；wall **10.606399s**（tracemalloc 开启）、**100 万条完整决定/0 源动作**、**traced peak 340522343 B**（与 owner 及前次独立审三次完全相同字节）；input SHA `1a0a2c59…`、完整 plan SHA `0964fe0a…` 一致；测后逐条 decision 完整字段/顺序/独立容器（`id()` 去重数=总数）校验内含 |
| 10 | fixture 作者脚本内存重放（`exec`，`__file__` 重定向至自有 out 临时目录） | 与受审 counterexamples.json **canonical JSON 完全相等**；committed 原始字节 SHA `17de133b…`；作者脚本不导入计划器 |

过程记录（不影响产品）：一次 Bash 尝试将 build_corpus.py 复制到自有 out 时被 Mimosa PreToolUse 路径守卫拒绝（与 round-1 第 1 号拒绝同类）；未重试被拒操作，改用 stdin 内存 exec 完成同等验证，全程零 .py 落盘、仓库零接触。

## 4 语义核对（对照派发审查重点逐项，均给出代码依据）

- **事件顺序与原始源位置分别记录**：`planner.py:383-405` 预校验携带排序前 `event_index`（仅 id/sequence 字段本身合法才附入 identity），`planner.py:405` 执行视图按 `(sequence, id)` 排序，请求原始数组不改写；`test_behavior_failures.py:279-316` 证明源位置≠执行位置。
- **scope/内容消费身份**：消费账本 scope 必须 JSON 等于 request scope（`planner.py:363-364`）；事件 fingerprint=内容哈希且不含 sequence（`planner.py:410`）；同指纹重投→`duplicate_event` no-op；成功计划返回"旧账本+本轮新消费"（`planner.py:956-962`）。
- **同 ID 异内容拒绝**：投递内与跨轮账本均 `event_identity_conflict` 整批拒绝（`planner.py:411-425`）。
- **冻结事件后推导绑定与 current/version**：`plan_behaviors` 校验 binding/assertion_digest/ontology_version/rules_version 与 status=="current"（`planner.py:769-779`），冻结集=事件后断言∪推导（781-791）；推导不能引用不存在对象、单值矛盾经 `_state(frozen)` 拒绝（791）；B-04 陈旧绑定拒绝+伪造敏感性对照保留（planner 测试 115-134）。
- **条件组/四层实例排序/动作序**：条件合取（`_definitions` 543-552）；`(-priority, behavior_id, event_sequence, event_id)`（`planner.py:859-861`），实例内按 action_index；planner 测试 192-224 固定 12 步顺序且与存储顺序无关。
- **跨实例单值不同意图全轮拒绝（含 create.initial 隐含写）**：`_single_writes`（668-685）把 set 与 create.initial 单值字段全部纳入；`_first_conflict`（688-726）按槽分桶、去重仅限搜索索引、跨桶取全局最小 `(i,j)`——本轮以 30 万+穷举与 5000 随机例对直接 combinations oracle 验证首对完全一致（第 3 节 #4）；`test_behavior_creation.py:59-69` 与 resource_equivalence 测试 42-105 覆盖 create.initial 竞争、内部覆盖/重复写、跨槽全局首对。**实例内任一中间写与 peer 不同值仍拒绝**（同实例跳过仅对相同 instance 键）。
- **同值保留其他动作/通知**：`_Workspace._put` 同键返回 False（unchanged）不删除动作；B-11 同值双通知保留（fixture+测试）。
- **同实例内部顺序更新允许**：`_first_conflict` 桶内按 `(event_id, behavior_id)` 相同即同实例跳过；K1 类场景（A→B 内部覆盖成功）在差分与 resource 测试覆盖。
- **1000 按源动作计、create.initial 仍一项**：`action_count = sum(len(b["actions"]))`（`planner.py:862-863`）；501×create(initial 2 字段) 通过、1001 拒绝（creation 测试 47-56）；1000 边界通过（planner 测试 363-369）。
- **静态/动态对象、模板白名单单次替换、未知字段、有限 JSON、类型和 Unicode 异常**：`_static_references`（589-646）常量引用静态校验、动态实例期复验、peer 不得引用他实例 create；模板仅 `{eventId}/{behaviorId}` 白名单、residual 花括号拒绝（`_expression` 458-477）、`re.sub` 函数替换单遍不重解释（489-496）；未知字段 `_shape` 全层拒绝；`allow_nan=False`+有限 `_scalar`+入口 `encode("utf-8")` 校验（30-39）；lone surrogate 三处拒绝（failures 测试 222-232）；0/False、1/1.0 typed 差异参与条件与冲突（resource 测试 78-82）。
- **完整成功状态/Diff/轨迹/消费**：输出含 before/after_events/frozen/candidate/decisions/action_trace/diff/consumption，`committed=false`；diff 基线=before→candidate 总净变化（`planner.py:983`、interface.md:34）；fixture 九例全字段相等断言+确定性二跑（planner 测试 67-112）。
- **失败部分解释/initial_index、discarded 与正式执行区别、无 candidate/consumption/输入修改**：阶段化 evidence（event_validation/event_preparation/definition_validation/condition_evaluation/intent_limit/intent_validation/conflict_check/candidate_simulation）+ partial_decision 前缀 + discarded_event_edits/discarded_actions；`executed_actions` 恒空；failures 测试 61-72 断言无 candidate/consumption 且 `str(error)` 为纯 `reason: location`；动态 initial 失败携带准确 `initial_index`（creation 测试 127-161，evidence 全字典精确断言）；本轮全部负例输入前后不变（第 3 节 #6）。
- **错误安全文本与私有 evidence 不得公开**：`BehaviorError` 仅结构常量；`__init__.py` 只导出 4 符号（baseline_adapter 不在包出口）；interface.md:40 明确内部证据不外发。
- **固定输入加载/PRD/manifest/逐文件 hash/根路径边界/同一已验证 bytes 解析**：`load_bundle` 先核 manifest SHA、PRD source SHA、逐文件 SHA（baseline_adapter.py:69-103）；`_read` 绝对路径与越根拒绝（32-41）；解析使用已核验 buffer；篡改/越界负例单测（adapter 测试 284-302）。
- **有界 RDF Boolean/IRI/局部 ID/全部展开投影身份、notification 完整 facts、原动作粒度和顺序**：decode/encode 仅字符串/布尔/IRI 子集且 round-trip/负例齐备（adapter 测试 124-152）；投影复验全部 subject/predicate/通知 ID/事件 IRI/类型 IRI（`project_candidate` 487-523）；通知两条 RDF 陈述一次投影；actionTrace 1-based 源动作粒度（571-578）。
- **负例和完整集合断言而非只计数**：九例 probe 按完整集合+顺序比较（probe 脚本 104-119）；139 项行为测试以全字段相等/精确 evidence 为主；决定矩阵混合例逐条完整断言且容器独立（resource 测试 235-287）。

## 5 发现清单

**未发现 P1/P2/P3 代码缺陷。** 无新增文档级观察达到 round-1 两项 P3 的等级——round-1 的建议（fingerprint 点名排除 sequence、动作属性值原样 JSON 标量边界）已分别落实在 `interface.md:7` 与 `t09-adaptation.md:12`，且 `interface.md:28` 新增了索引/完整输出/Q5 边界声明。以下为一项信息级记录（不阻断、无需修改）：

1. **[信息] 三次独立测量的 matrix traced peak 字节数完全相同（340522343 B）**：owner 配对、前次独立审、本轮（第 3 节 #9）在各自进程里得到逐字节相同的峰值。这与实现为确定性分配（同一输入产生同一对象序列）相符，属合理现象；但它同时具体展示了 P2-2 成本的确定性下限——该 1000×1000 输入在此实现下的 traced 峰值不会因环境波动降低。无行为缺陷；仅作为容量裁决的输入事实。

## 6 两项资源 P2 的本轮独立裁决

### P2-1（原可避免的全对扫描/逐写全 facts 序列化/逐动作全状态比较）——机制已修复，我同意关闭定位机制

- 旧机制在固定 613 源码中静态可证：`combinations(writes, 2)` 全对（旧 804 行）、每次 `_put` 重建 `{_json(f) for f in state["facts"]}`（旧 178 行）、每动作 `prior = _json(candidate)`+`_normalize` 全量排序两次序列化（旧 840-858 行）、`prepared.reasoning_input`/`binding` 多次解析整个文档（旧 668-676 行）。
- 当前机制：`_Workspace` typed-key facts 字典 + `(subject, property)` 槽索引（planner.py:175-206）；`_first_conflict` 分桶且只保留最早 `(instance, value)` 搜索代表、完整 intents 不裁剪（688-726）；增量 effect（927-953）；binding/expected 单次计算（752、769-774）。
- 等价性证据：本轮 30 万+ 穷举 + 5000 随机 oracle 零失败（首冲突对与原 combinations 定义完全一致）；1500 例自有差分 + 1009 例 owner-helper 差分全部完整输出/错误证据相等且 rolling SHA 与 owner 原值一致；800-create 独立重测 wall 0.540s、input/完整 plan SHA 与 owner 记录一致（旧 613 同输入 131.5s）。
- 保留边界：per-instance scratch 仍按实例重建（成本非零）；测量区间为 prepare+plan、排除测后核验；非生产速度/容量承诺；1000 源动作本来就不是 facts/fields/bytes 配额，不存在"绕过"。

### P2-2（零动作 1000×1000 仍是完整 100 万决定）——风险保留，当前私有 S1 非阻断，容量门不关闭

- 本轮独立重测：100 万条决定逐条完整字段/顺序、独立 conditions 容器（helper 断言独立 `id()` 计数=总数）；traced peak **340522343 B**、wall 10.606s（tracemalloc 开启口径，非 RSS、非无跟踪时延）；与 owner、前次独立审数值一致。
- 裁决理由（我自己的，非照抄）：interface.md:11/24/32 与 PRD FR-603 要求完整条件决定集合，该材料化输出本身有 Ω(B×E) 下界，成本是合同的必要组成而非可避免缺陷；PRD Q5/10.2 未批准任何规模/设备/内存/时间阈值，因此不能以未存在的阈值判其违约，同样不能宣称生产容量合格；实现未分页、未删 mismatch/disabled 决定、未共用可变 conditions、未暗设配额——这些恰恰是被禁止的"用语义换通过"。
- 保留不关闭的部分：正式设备/并发/RSS/序列化持久化容量、取消可响应性、"同事务保存完整候选"的传导成本（interface.md:32）均未验证；若未来要改变输出合同或新增配额/分页，须 Q5 与对应 owner 决定。不以"装配前再说"代替本判断——本判断就是：**当前私有 S1 范围内不阻断，容量风险登记为真实存在且开放**。

## 7 历史问题逐项处置（自行核验，不沿用任何旧 Pass）

| 来源 | 问题 | 本轮处置 | 我的核验证据 |
| --- | --- | --- | --- |
| LR1 P1 | 静态 create 破坏重复/空轮幂等 | **关闭，未回归** | `_static_references` 仅登记常量（planner.py:612-646）；重复/空/disabled/mismatch/新事件碰撞回归（planner 测试 153-168、450-467）实跑通过；差分含续轮场景 |
| LR1 P2 | 冲突证据/非空 Diff 缺完整断言 | **关闭，未回归** | fixture 全字段相等（planner 测试 67-112）+ 本轮 oracle/差分完整 evidence 相等 |
| LR3 P2 | 事件校验缺阶段/源位置 | **关闭，未回归** | planner.py:383-405 源位置视图；failures 测试 255-327 六类错误+反序+冲突后定位实跑 |
| LR5 P2#1 | 展开身份未验 IRI 可投影非法 RDF | **关闭，未回归** | 投影复验（adapter 487-523）+ 四非法身份负例（adapter 测试 305-351） |
| LR5 P2#2 | dynamic initial 缺 initial_index | **关闭，未回归** | `_resolved_action` 逐字段 `_explain(initial_index)`（planner.py:649-665）；creation 测试 127-161 evidence 全字典断言 |
| LR2/LR4/LR6 Pass | 旧候选通过结论 | **不沿用** | 本轮对 3be 全量重验（第 3/4 节） |
| round-1 ZCode P3-1 | fingerprint 未点名排除 sequence | **已实施并核验** | interface.md:7 现明确"明确排除 `sequence`" |
| round-1 ZCode P3-2 | 动作属性值原样 JSON 标量边界 | **已实施并核验** | t09-adaptation.md:12 新增该条 |
| round-1 ZCode 信息 | rdf:type 保持 many 基数 | **维持，无需修改** | adapter model_state:182 不改写（182-201） |
| round-1 MiniMax P2-1 | 全对/全扫/逐动作全量比较 | **本轮裁决：机制已修复**（第 6 节） | 独立重测+oracle+双差分 |
| round-1 MiniMax P2-2 | B×E 无上限 | **本轮裁决：风险保留、私有 S1 非阻断、容量门开放**（第 6 节） | 独立重测 100 万决定 |
| round-1 MiniMax P3-1 | initial 内重复单值静默覆盖 | **按现合同澄清，不改语义** | interface.md:26 明确有序覆盖+中间写竞争；resource 测试 164-181；不新增 cardinality 拒绝（会改合法行为） |
| round-1 MiniMax P3-2 | 跨实例同值 create 同对象拒绝 | **按现合同澄清** | interface.md:26 明确"create 对象标识碰撞仍拒绝"；两方向碰撞负例本轮实跑通过 |
| round-1 MiniMax P3-3 | 成功路径无源位置 | **维持现合同边界** | interface.md:52 仅承诺错误源位置；消费 schema 不新增字段（新增属接口扩展须批准） |
| round-1 MiniMax P3-4 | Diff 含事件效果 | **已澄清** | interface.md:34 明确 before→candidate 及 frozen 推导不可误记为删除 |
| round-1 过程门 | ZCode 4 拒绝/27 条结果、MiniMax tail 缺口等 | **过程事实保留，不重开代码问题** | 过程补正+两 owner audit 已全文读回；首败原件 SHA 本轮重算一致；该门归总控流程裁定，非本候选代码缺陷 |

## 8 未验事项（边界保留，不因本报告关闭）

真实推理与通用 RDF codec（T05/I05）；真实 Store 原子轮次提交/回滚/取消/迟到投递/恢复（T01/I04）；资源队列/产能 B-07、轮末推理/指标与完整 E.2/G.3 轮次（T07）；Agent 工具真实失败 B-08（T08）；公共业务方法/受限错误映射/分页/权限/取消接线（T00）；UI 正式接线（另树，不在本候选）；公共注册/IPC 暴露（当前确未暴露）；打包（`package:dir`）、远端 CI/push/PR/合并/生产、native 两 OS、真人操作；正式规模容量/RSS/Q5 指标（P2-2 风险门）。九例 probe 推导为人工 gold（`product_runtime=not-executed`、`formal_acceptance=false`），expected 不代表实际 Store payload。**FR-600–604 父模块与完整 B 用例验收保持开放，本报告不关闭。**

## 9 明确结论

- **本独立 S1 范围（私有行为计划算法 + T09 固定输入只读适配，产品 3be0397）：通过。**
- 新发现：0 项 P1/P2/P3 代码缺陷；1 项信息级记录（第 5 节）。
- P2-1：机制修复（我独立测量与等价验证支持）。P2-2：风险保留、当前范围非阻断、容量门不关闭（第 6 节，非照抄内部意见）。
- 历史问题：第 7 节逐项处置，旧 Pass 均未沿用。
- 无法验证项：见第 8 节，均属声明中的未接线边界，不属本候选承诺范围。
- 本报告不改写、不引用本轮另一模型结论；开发者应全文读回并处理全部意见。
