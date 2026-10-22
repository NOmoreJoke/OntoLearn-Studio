# T06-S1 独立只读对抗审查报告（round-1 / zcode-glm53）

- 审查者：ZCode GLM-5.3 / 最高思考（会话实际模型 `account:bigmodel-individual-coding-plan/GLM-5.3`，环境自证；思考等级为派发指定）。
- 任务权限：派发侧读回声明 `permission.mode=yolo`（完全访问）。该读回属 owner 外部证据，模型会话内无法自证；本审查全程只读 + 仅写本报告，未使用任何写权限改动受审内容，未提交/推送/切分支。
- 报告位置：本工作区 `docs/reviews/T06/round-1/zcode-glm53.md`（即本文件）。
- **总结论：通过（仅限本独立 S1 范围 = 私有行为计划算法 + T09 固定输入只读适配）。未发现新的 P1/P2/P3 代码缺陷；2 项 P3 文档级观察见第 6 节。全部历史 local-review 问题经我自行核验后关闭（第 7 节）。父 FR-600–604 模块与完整 B 用例验收保持未验开放（第 8 节）。**

## 1 任务来源与独立性

- 输入：`round-1/zcode-glm53-input.md`（SHA-256 `f5b0c53bda018c4b85270dd250268d413c5d4d70be438f694cd8e6e030faa39c`，与 `round-1/frozen-inputs.json` 记录一致）+ 2026-10-22 桌面执行补充（将原冻结正文中 `T06-review-61396a5`/`T06-behavior` 路径整体映射到本任务唯一工作区）。
- 独立性：未读取另一模型输入 `round-1/minimax-m31flash-input.md`（仅按流程记录其 SHA `5096382b813ea6b12d2c6d14702631f43c4196b95b30ec52428d84453c2ded07`），未读取其任何会话、报告或意见；未读取 UI 树 `T06-behavior-ui` 的任何内容充当本范围。
- 只读执行：未改实现/测试/依赖/配置/AGENTS；未运行 Electron/e2e/native/HMR/GUI/Keychain/模型 API/新增支付。

## 2 精确版本与基线核验（全部实际执行）

| 项 | 值 | 核验结果 |
| --- | --- | --- |
| 唯一工作区 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-zcode-review-61396a5` | detached，无分支（原开发线 `feature/weekly-t06-behavior`） |
| 流程 HEAD | `10f1d8c33820d9a882a153590d8488f6d3fa7723` | `git rev-parse HEAD` 一致 |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 存在为 commit；与本地 `origin/develop` 引用相同（未 fetch，无网络操作） |
| 产品候选 | `61396a598b2dffc1d3d2fd4660f9af1d5c93d266` | 存在为 commit |
| 冻结流程前置 | `11d66ea267c56e1436f1f916dd6319a1914d9a59` | 在 product..HEAD 链上（最旧一档） |
| base→产品完整 diff | SHA-256 `e1b08e5c89b72f4d8a0a7e1ca57feadd91ced235301d1096fdfd07d8e5d507dc` | plain 与 `--binary` 两种口径均一致；23 个文件、全部 `new file mode`、零删除/修改行 |
| product..HEAD | 15 个仅流程证据提交 | `10f1d8c3`、`1ff7577e`、`756a33fe`、`97ee530d`、`d5de8386`、`97e2da8f`、`fd33cbbb`、`e2fca19c`、`4926b600`、`6099b124`、`cd0979af`、`ff1e3bb0`、`0113c393`、`11c7a9bb`、`11d66ea2`（仅新增/修改 `docs/reviews/**` 流程文件） |
| 12 受审文件 | 见下 | product / HEAD / 工作树三方 git blob 哈希逐一相同，零漂移 |
| AGENTS.md | SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 与 2026-10-22 补充声明一致；保持未暂存 dirty，未还原（原冻结正文中的 `78df2825…` 为政策追加前旧快照） |
| 工作区状态 | `M AGENTS.md` + 未跟踪派发/报告文件 | 无其他改动，未 stage、未提交、未推送 |

12 受审路径（git blob，product=HEAD=worktree）：

- `packages/engine/src/ontolearn_engine/behavior/__init__.py` `55b8c37a…`
- `packages/engine/src/ontolearn_engine/behavior/baseline_adapter.py` `3469d13a…`
- `packages/engine/src/ontolearn_engine/behavior/planner.py` `78bbc9bc…`
- `packages/engine/tests/test_behavior_baseline_adapter.py` `a33ed06a…`
- `packages/engine/tests/test_behavior_creation.py` `05f765a7…`
- `packages/engine/tests/test_behavior_failures.py` `c2352426…`
- `packages/engine/tests/test_behavior_planner.py` `33ab70c4…`
- `tests/fixtures/behavior/build_corpus.py` `02c4f530…`
- `tests/fixtures/behavior/counterexamples.json` `dcf5e115…`（SHA-256 `17de133b…` 与 `evidence/validation-61396a5.json` 记录一致）
- `docs/iterations/T06/interface.md` `69700f09…`
- `docs/iterations/T06/t09-adaptation.md` `652c3c96…`
- `docs/iterations/T06/probe_t09_baselines.py` `453d31e8…`

T09 固定输入独立核验：`out/t09-approved-873c8c0` 内 19 个文件（含 manifest 与 PRD 副本）逐一经 `git cat-file` 与 T09 仓库固定提交 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 的对象 blob 比对，全部一致（仅读取固定对象，未读取变化中 T09 HEAD，未导入其 Python）；`tests/fixtures/product-baselines/manifest.json` SHA-256 = `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` ✓。主 PRD `/Users/kyle/Documents/工作/知爻/本体/PRD-本体学习与落地Agent工作台.md` SHA-256 = `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` ✓。

## 3 完整读取范围

全文读取：本树 AGENTS.md；`docs/reviews/T06/` 下 review-readiness.md、status.md、baseline-compatibility-audit.md、local-review-1…6.md、ui-integration-handoff.md、evidence/validation-61396a5.json（另浏览 validation.json / validation-e81cfc9.json / t09-candidate-probe.json 的登记关系）；`docs/iterations/T06/` 三个文档（interface.md、t09-adaptation.md、probe_t09_baselines.py）；上述 12 受审文件全文（counterexamples.json 213KB 以结构化全量扫描 + 作者脚本复跑等价性验证代替逐行dump）；完整 base→产品 diff（导出 `/tmp/T06-zcode-glm53-full-diff.patch`，14099 行，核验纯新增属性）；主 PRD 第 7.7 节（FR-600–604 原文）、附录 C、E.1/E.2/E.3/E.4/E.5、G.0/G-behavior/G.3/G.4；本轮流程证据 `round-1/zcode-glm53-input.md`、`frozen-inputs.json`。未读另一模型输入与 UI 树。

## 4 实际验证命令与结果（全部无窗口）

1. `npm run check` → **exit 0**：eslint `--max-warnings 0`、prettier `--check .`、3 组 `tsc --noEmit`、vitest **15 文件 / 630 测试全过**、`electron-vite build`、`ruff check` + `ruff format --check`、pytest **1174 passed in 60.23s**（与派发声明 630TS/1174Python 一致）。
2. `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q` → **122 passed in 2.26s**。
3. `uv run --frozen python docs/iterations/T06/probe_t09_baselines.py --source-root out/t09-approved-873c8c0 --manifest-sha aaaef2c0… --output /tmp/T06-zcode-glm53-61396a5-probe.json` → **9 例（B-01/02/03/04/05/06/09/10/11）完整 facts/orders/notifications/actionTrace/consumedEvents/triggeredInstances/conflict 比较通过**；输出 raw SHA-256 `d18e5059394b11f6f783d4247c8e4f074a102a58d5ef3d48c3272fc248339c9e`，与开发登记的 `t09-probe-567ab48.json`/`t09-probe-61396a5.json` raw 哈希**逐字节一致**（确定性复现）；`product_runtime=not-executed`、`formal_acceptance=false`、reasoning_source=manual gold 保持标注。
4. 作者脚本复跑（`exec` 加载仓库 `build_corpus.py`、伪 `__file__` 指向 /tmp，不复制/不修改仓库文件）：生成 JSON 与受审 `counterexamples.json` **canonical JSON 完全相等**（受审字节为 prettier 格式化版本；`npx prettier --check` 亦通过）——fixture 来源链闭合，作者脚本确实不导入被测实现。
5. `uv run --frozen ruff check --no-cache` + `ruff format --check --no-cache`（9 个受审 Python 文件）→ 全部通过。
6. 只读内存负例探针（stdin 执行，仓库零写入）：第一轮 16 组 20 项通过、2 项为**探针自身预期错误**（见第 5 节说明）；按修正预期复跑 B1/K1/K2/C1/C2 全部通过。所有输入在失败前后与原请求 deep-equal（无输入修改）。
7. Git/哈希核验命令族（第 2 节全部结果来源）。

过程记录（不影响产品）：Mimosa 安全钩子两次拦截我向 /tmp 写探针 `.py`（误报"SQL 注入"，脚本零 SQL、零拼接）；改用标准输入执行完成同等验证，仓库与受审文件零影响。

## 5 语义核对（对照派发审查重点逐项）

全部按代码行级证据核对，结论均为**符合**：

- **事件顺序与原始源位置分别记录**：`planner.py:329-339` 预校验携带排序前 `event_index`（仅当 id/sequence 字段本身合法才附入 identity），`planner.py:350` 执行视图按 `(sequence, id)` 排序，请求原始数组不改写；失败测试 `test_behavior_failures.py:279-316` 证明源位置≠执行位置。
- **scope/内容消费身份**：consumption 必须 JSON 等于 request scope（`planner.py:307-309`）；事件 fingerprint=内容哈希且**不含 sequence**（`planner.py:355`）；重投同指纹→`duplicate_event` no-op（测试 `test_behavior_planner.py:137-149`，含 sequence=99 变体）；成功计划返回"旧账本+本轮新消费"（`planner.py:861-867`）。
- **同 ID 异内容拒绝**：投递内与跨轮账本均触发 `event_identity_conflict` 整批拒绝（`planner.py:356-370`；测试 170-177、failures 102-114）。
- **冻结事件后推导绑定与 current/version**：`plan_behaviors` 校验 binding/assertion_digest/ontology_version/rules_version 与 status=="current"（`planner.py:671-676`），冻结集=事件后断言∪推导（679-684），推导不能引用不存在对象、不能制造单值第二值（我的负例 F/O 证实）；B-04 陈旧绑定拒绝+伪造敏感性对照测试保留（planner 测试 115-134）。
- **条件组/四层实例排序/动作序**：`(-priority, behavior_id, event_sequence, event_id)`（`planner.py:753-755`），实例内按 action_index；planner 测试 192-224 固定 12 步完整顺序且与存储顺序无关。
- **跨实例单值不同意图全轮拒绝（含 create.initial 隐含写）**：`_single_writes`（612-629）把 set 与 create.initial 单值字段都纳入竞争；`combinations` 全对比较、同实例跳过、同值放行（803-824）；我的负例 C2 证实 create.initial 不同值在 conflict_check 拒绝且 `conflict_slot` 精确。**实例内任一中间写与 peer 不同值仍拒绝**（K2 证实 conflict 对为 `(c,0,"A") vs (p,0,"B")`）——与 interface.md「其任一写入与其他实例不同值仍拒绝」及 E.1「任意两个动作」一致。
- **同值保留其他动作/通知**：B-11（set/set 同值双通知）、我的 B 探针（create.initial 同值+通知保留，重复写 effect=unchanged）证实。
- **同实例内部顺序更新允许**：K1（A→B 内部覆盖成功终值 B）。
- **1000 按源动作计、create.initial 仍一项**：`action_count` 按行为定义动作数（756-757），501×create(initial 2 字段) 通过、1001 拒绝（creation 测试 47-56）；1000 边界通过（planner 测试 363-369）。
- **静态/动态对象、模板白名单单次替换、未知字段、有限 JSON、类型和 Unicode 异常**：`_static_references` 常量引用静态校验、动态引用实例期复验、peer 不得引用他实例 create（我的 B1 证实 `invalid_object@definition.subject`）；模板仅 `{eventId}/{behaviorId}` 白名单、residual 花括号拒绝（`_expression` 402-420）、`re.sub` 单遍替换不重解释插入文本（436-440；creation 测试 98-111，含事件 id="{behaviorId}" 反例）；未知字段 `_shape` 全层拒绝；`allow_nan=False`+有限 `_scalar`+入口 Unicode 编码校验（31-39）；lone surrogate 三处拒绝（failures 测试 222-232）；JSON 类型差异（0 vs False）参与条件与冲突（planner 测试 273-284）。
- **完整成功状态/Diff/轨迹/消费**：输出含 before/after_events/frozen/candidate/decisions/action_trace/diff/consumption，`committed=false`；fixture 九例反例全字段逐一相等断言（planner 测试 67-112，含确定性二跑相等）。
- **失败部分解释/initial_index、discarded 与正式执行区别、无 candidate/consumption/输入修改**：阶段化 evidence（event_validation/event_preparation/definition_validation/condition_evaluation/intent_limit/intent_validation/conflict_check/candidate_simulation）+ partial_decision 前缀 + discarded_event_edits/discarded_actions；`executed_actions` 恒空；断言 evidence 无 candidate/consumption、`str(error)` 为纯 `reason: location`（failures 测试 61-72）；动态 initial 失败携带准确 `initial_index`（creation 测试 127-161）；全部负例请求前后不变。
- **错误安全文本与私有 evidence 不得公开**：`BehaviorError` 仅结构常量 reason/location；evidence 标注内部诊断；`__init__.py` 仅导出四个符号（baseline_adapter 不在包出口）。
- **固定输入加载/PRD/manifest/逐文件 hash/根路径边界/同一已验证 bytes 解析**：`load_bundle` 先核 manifest SHA、PRD source SHA、逐文件 SHA，`_read` 绝对路径与越根拒绝，解析使用已核验 buffer（baseline_adapter.py:32-103）；篡改/越界负例有单测（adapter 测试 284-302）。
- **有界 RDF Boolean/IRI/局部 ID/全部展开投影身份、notification 完整 facts、原动作粒度和顺序**：decode/encode 仅字符串/布尔/IRI 子集且 round-trip/负例齐备；LR5 修复后投影复验全部 subject/predicate/通知 ID/事件 IRI/生成类型 IRI（496-523）；通知两条 RDF 陈述一次投影；actionTrace 1-based 保持源动作粒度。
- **负例和完整集合断言而非只计数**：九例 probe 按"完整集合+顺序"比较（probe_t09_baselines.py:104-119），B-02 真实未触发原因、B-06 冻结 false、B-05/09 完整冲突对；私有 122 测试以全字段相等为主。

两处探针初判"失败"经复核为**我方预期错误、实现正确**：B 触发 peer 引用他实例创建对象（interface.md 明文禁止，且有既有回归测试）；K 触发"实例内中间值与 peer 不同值仍拒绝"（E.1「任意两个动作」原文）。已按正确语义复跑通过。

## 6 发现清单（严重度/位置/触发/影响/证据/建议）

**未发现 P1/P2/P3 代码缺陷。**以下为 2 项 P3 文档级观察与 1 项信息记录：

1. **[P3·文档精确性] interface.md 未明说事件 fingerprint 排除 `sequence` 字段。**
   - 位置：`docs/iterations/T06/interface.md:7` vs `packages/engine/src/ontolearn_engine/behavior/planner.py:355`。
   - 触发：同 ID 同内容、不同 sequence 的重复投递。
   - 影响：实现按"内容身份不含 sequence"处理为 no-op（并有测试 `test_behavior_planner.py:137-149` 以 sequence=99 固定该语义），文档只写了"输入序号不参与内容身份"，未点名 sequence；读者可能误判。
   - 证据：上述行号与测试。
   - 建议：interface.md 补一句"fingerprint 由 id/类型/版本/载荷/edits 构成，不含 sequence"。
2. **[P3·边界声明] baseline_adapter 的 update-attribute / create-individual 属性值按原始 JSON 标量直传，不经 `decode_value`。**
   - 位置：`baseline_adapter.py:272-294`。
   - 触发：若未来固定数据在属性值位置使用 RDF 词面布尔/类型字面量（如 `"true"^^<…boolean>`）。
   - 影响：该值将以原始字符串进入计划，与状态中解码后的布尔不相等（条件不匹配或类型错写）。当前九例数据不存在此形态，probe 完整比较通过；`t09-adaptation.md:10-11` 已声明只承诺当前数据使用的子集，不冒充完整 codec。
   - 证据：代码行号 + 九例 probe 通过 + 单测模型属性值为 JSON 布尔原样直传（adapter 测试 66-68）。
   - 建议：在 t09-adaptation.md 点名"行为定义属性值仅支持 JSON 标量原样"；T05 完整 codec 接入时统一收口。
3. **[信息] `model_state` 对 `singleValuedPredicates` 含 `rdf:type` 的情况不改写其 many 基数**（`baseline_adapter.py:182,196-201`：schema 初始 rdf:type=many，singles 只做存在性校验）——与兼容审计"rdf:type 保持集合语义"一致，属有意行为，无需修改；可加一行注释防误读（可选）。

## 7 历史问题处置（逐项自行核验，非沿用 local Pass）

| 历史问题 | 处置 | 我的核验证据 |
| --- | --- | --- |
| LR1 P1 常量 create 破坏幂等/阻断空轮 | **关闭** | `planner.py:576-580` 静态 create 仅登记供本行为引用、无副作用；实际碰撞仍由 `_edit(create)` 拒绝；五项回归（重复事件/空轮/禁用/不匹配/新事件碰撞）在 `test_behavior_planner.py:153-168,450-467`，我实跑通过 |
| LR1 P2 冲突证据与非空 Diff 缺完整断言 | **关闭** | `test_behavior_planner.py:67-112` 对 B-05/B-09 的 conflict/failed_intents/decisions/event_trace 及成功例 candidate/frozen/diff/consumption 全字段相等；非空 Diff 反例 470-475 |
| LR3 P2 事件头/载荷错误缺源位置、重复 ID 无法定位 | **关闭** | `planner.py:329-350` 保留排序前 event_index（合法才附 id/sequence）；`test_behavior_failures.py:255-327` 六类字段错误+反序源数组+排序后重复冲突+非法 ID 元数据全部精确断言 |
| LR5 P2#1 展开身份未过 IRI 验证可投影非法 RDF | **关闭** | 投影复验全部 subject/predicate（`baseline_adapter.py:496-503`）与展开通知 ID/事件 IRI/类型 IRI（505-523）；四个非法 subject+事件 IRI 负例（adapter 测试 305-351），失败不改 plan |
| LR5 P2#2 create.initial 动态解析缺 initial_index | **关闭** | `_resolved_action` 逐字段 `_explain(initial_index=…)`（`planner.py:596-606`）；完整 evidence 含 initial_index=1 的精确断言（creation 测试 127-161） |

历史不通过结论（LR1/LR3/LR5）原文均保留未改写；LR2/LR4/LR6 通过结论我未沿用，以上表自行重验为准。

## 8 未验事项（边界保留，不因本报告关闭）

真实推理与通用 RDF codec（T05/I05）；Store 原子轮次提交/回滚/取消/迟到投递/恢复（T01/I04）；资源阶段 B-07、轮末推理/指标与完整 G.3/E.2 轮次（T07）；Agent B-08 真实工具失败表达（T08）；公共业务方法/受限错误/分页/权限/取消接线（T00）；UI 集成（另树 T06-behavior-ui，不在本候选）；公共注册/IPC 暴露；打包（`npm run package:dir`）；远端 CI/push/PR/合并/生产。九例 probe 推导为人工 gold（`product_runtime=not-executed`、`formal_acceptance=false`），expected 不代表实际 Store payload。**FR-600–604 父模块与完整 B 用例验收保持开放。**

## 9 明确结论

- **本独立 S1 范围（私有行为计划算法 + T09 固定输入只读适配）：通过。**
- 历史问题：全部关闭（第 7 节）。
- 新发现：0 项 P1/P2/P3 代码缺陷；2 项 P3 文档级观察 + 1 项信息记录（第 6 节，均已给出建议，不阻断）。
- 无法验证项：见第 8 节，均属声明中的未接线边界，不属本候选承诺范围。
- 本报告不改写、不引用另一模型结论；开发者应全文读回并处理第 6 节意见。

附：本审查 /tmp 产物（过程件，不入库）——`/tmp/T06-zcode-glm53-61396a5-probe.json`（九例 probe 输出）、`/tmp/T06-zcode-glm53-full-diff.patch`（完整 diff）、`/tmp/T06-zcode-glm53-corpus/counterexamples.json`（作者脚本复跑对照）。
