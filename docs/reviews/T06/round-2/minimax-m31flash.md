# T06-S1 R2 全新完整独立对抗审查（MiniMax Code M3.1-Flash / xhigh）

审查者：MiniMax Code M3.1-Flash（xhigh，bypassPermissions 始终授权），2026-10-23 全新独立只读任务。

## 0. 结论（先行）

**本独立 S1 范围（私有行为计划算法 + T09 固定输入只读适配）：通过（Pass）。**

未发现 P1 或 P2 级实现缺陷。发现 **4 项 P3**：1 项可达性受限的实现前置条件缺口（`_edit` 兼容包装器不自行校验传入状态，重复事实被静默去重）、2 项失败证据粒度问题、1 项接口文档措辞缺口。均为不改变当前可观察语义、可在本候选之外择机修正的项，不阻断本范围。

**两项历史资源 P2 我给出与共同历史一致但独立作出的实质裁决：**
- **P2-1 关闭的是"本次指向的可避免机制"**：我独立穷举 271,453 例单槽 + 14,425 例双槽 + 40,000 例随机 create.initial 首次冲突序列，并用我自己独立重写的旧 `combinations` 语义作 oracle，**首次冲突对 0 不一致**；又以 1,500 例随机请求做全管线差分（802 plan / 698 domain error），与冻结 613 基线**完整输出或完整 reason/location/evidence 逐字节相等**；独立复测 creates 规模已由旧 8.675/33.185/131.516 秒的近二次变为 0.122/0.248/0.565 秒的近线性。**P2-1 的严重度事实保留，成本未被"优化掉"的表述不采用。**
- **P2-2 不关闭**：完整 B×E 决定输出的 Ω(BE) 成本仍在。我独立实测 1000×1000 零动作矩阵为 1,000,000 条决定、1,000,000 个独立 conditions 容器、traced peak **340,522,087 B**、wall **10.184 s**（owner 同口径 340,522,343 B / 11.710 s；旧 613 为 345,860,759 B / 11.622 s）。该成本与旧候选同量级、**本候选未使其变差**，但也**未被消除**。就本"显式调用的私有纯函数、无公共/Store/真实运行注册"范围，我判定**当前非阻断**；**这是工程容量风险与 Q5 未关闭项，不是"容量问题已解决"的结论**，不授权任何生产规模/响应时间/RSS 适用性主张。

**本结论不关闭** FR-600–604 父模块、完整 G.3 轮次、B-07/B-08、T06 整体验收，也不替代另一指定模型的本轮审查。

---

## 1. 任务来源、身份与权限

| 项 | 实际值 | 来源与自证边界 |
|---|---|---|
| 任务来源 | 2026-10-23 官方附件 `own-frozen-input.md`（223 行 / 40372 B / SHA-256 `38096163d2278fca1def97411d91bd16bfd0813cb5d6f312a56cd3f1f422fac9`）+ 本条会话指令 | 附件路径 `/Users/kyle/.minimax/v2/assets/2026/10/23/03-23-51-824-asset_20261023-032351-824_38096163d227_3c69da82-own-frozen-input.md`；本树 `out/environment-prep/own-frozen-input.md` 与之 `diff` 全等、字节数与 SHA-256 完全一致 |
| 指定模型 / 思考等级 | MiniMax M3.1-Flash / xhigh | 由 owner 在**本任务 UI 读回**告知；模型侧自报身份与运行上下文一致。用户级配置文件不作会话证明 |
| 任务权限 | 始终授权 / Full access（`bypassPermissions`） | 同上，由 owner 在本任务 UI 读回；本轮全程只读，仅写本报告与本方 out 证据 |
| 冻结输入中的历史快照 | 正文旧"账号等待"句按历史快照保留 | 该句属冻结输入原文快照；账号已由总控观察恢复，当前根已明确本线仅此 S1 双任务窗口。本轮不重述、不据旧快照阻断 |
| 同轮另一模型 | **未读取**其提示、会话、报告或意见 | `docs/reviews/T06/round-2/` 在本轮开始时不存在；本轮未创建、未读取任何同轮他方材料 |
| UI 树 / 其他开发线 | **未读取** `T06-behavior-ui` 及任何他线当前意见 | 不在本候选范围 |

## 2. 精确版本与隔离核验（本方独立重算）

| 项 | 值 | 核验方式与结果 |
|---|---|---|
| 唯一工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-s1-minimax-review-3be0397` | `pwd` 实测一致 |
| 分支状态 | detached HEAD（`## HEAD (no branch)`） | `git status --porcelain=v1 -b` 实测 |
| 产品候选 / 流程 HEAD | `3be0397faf03de6520c47bf7d86f3dc2fd004287` | `git rev-parse HEAD` 精确相等 |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git rev-parse` 存在且为 commit |
| 完整 base→产品 binary diff | **6075356 B / SHA-256 `569b98c2b6f16a18593fc3c3c8b17580f8df21672d04188549d7946cda9c916f`** | 独立重算 `git diff --binary <base> <product> \| shasum -a 256` **一致**（普通 diff 口径为 `fa879b62…`，与派发口径不同属正常：派发口径为 `--binary`） |
| diff 规模 | 76 文件 / 23585 insertions | 独立 `git diff --stat` |
| 主 PRD | SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` | 独立 `shasum` 与派发一致 |
| 保护 AGENTS | SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 独立 `shasum`；保持 ` M AGENTS.md` 未暂存、未还原（授权政策追加，非受审产品变更） |
| 结束状态 | `git status --porcelain=v1` 仍仅 ` M AGENTS.md`；受审 13 路径 `git diff HEAD -- <13路径>` **为空** | 本轮未改实现/测试/依赖/配置/AGENTS，未切分支、未提交、未 push、未 PR |

### 2.1 13 项受审来源：Git / manifest / 磁盘三方字节一致

13/13 项的磁盘 SHA-256、`git show <product>:<path>` blob SHA-256 与 `out/review-common-history/evidence/validation-3be0397.json` 的 `source_sha256` **三方全等**（我逐项 `hashlib` + `subprocess git show` 重算，非采信清单）：

| 受审来源 | SHA-256 | B |
|---|---|---|
| `docs/iterations/T06/interface.md` | `47fcdd948f838779f8c921ae7fcc48b586c8d24325e68f5a775b6b8670e4e2a0` | 10072 |
| `docs/iterations/T06/probe_t09_baselines.py` | `d960d1c95e34d40398bb9a280745bdf690020e47b6730d8f59d45e6efba16565` | 8446 |
| `docs/iterations/T06/t09-adaptation.md` | `0a48144fa3324c406af52848676c2f2e14840bf79747891d07f7a1709c7eb477` | 3907 |
| `packages/engine/src/ontolearn_engine/behavior/__init__.py` | `0519496083ecaf23ad3a606c8be5f461b21bfb1507f313678083d212cec676d9` | 255 |
| `packages/engine/src/ontolearn_engine/behavior/baseline_adapter.py` | `18f6eb0133b12db950d07dfffe881fb38192af4b14d0b67003c47b67af5a32af` | 22551 |
| `packages/engine/src/ontolearn_engine/behavior/planner.py` | `525caeb1aafadc9856dc912e50fec95dfbcaea568e64b911f783d0d7f42a95d0` | 39977 |
| `packages/engine/tests/test_behavior_baseline_adapter.py` | `59a07e8b8d7f0caba8cca1d4f31f684fefafc295473f10ee0dd165439ed50859` | 11995 |
| `packages/engine/tests/test_behavior_creation.py` | `96e99469d2057e56fd702d43bc3c0373e90809e6f624e49a5a19f675222d999c` | 6151 |
| `packages/engine/tests/test_behavior_failures.py` | `02f9698299f224019e9aed01617d108a06cd4a16a591c5ec08624b2c9c96839e` | 11355 |
| `packages/engine/tests/test_behavior_planner.py` | `940e54c1a94ec1b0ac9a8baec0bf7d98270fcaff2a476818033571a78db3285d` | 18557 |
| `packages/engine/tests/test_behavior_resource_equivalence.py` | `9bb385e714156ee41b1cbf113063dda52c7fe007e240c58df08459d66d861e8f` | 11658 |
| `tests/fixtures/behavior/build_corpus.py` | `9bbe4db97895c5ead7588acf22a25fa21e5358743b83755a9549141f5b66c5b4` | 16153 |
| `tests/fixtures/behavior/counterexamples.json` | `17de133b6a13efd14197b4d7dc09a51c7df097db5161b9acb6f7b92e5f9796f9` | 213042 |

### 2.2 T09 唯一批准输入字节核验

`out/t09-approved-873c8c0` 共 **19 个文件**，逐件与 Git `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 对应 blob 比对，**19/19 逐字节相等**（含 17 个 manifest 文件、manifest 本身、PRD 副本）；manifest SHA-256 = `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` 与派发一致。未读取变化中的 T09 HEAD，未导入其 Python，未把 expected 当实际结果。证据：`out/reviewer-verify/t09-byte-audit.json`。

## 3. 完整读取范围（全文，非摘要）

- 本树 `AGENTS.md`（保护 dirty 全文）、`docs/reviews/T06/review-readiness.md`、`status.md`、`out/review-common-history/evidence/validation-3be0397.json`（全键遍历 + 全部 `pairedMeasurements`）。
- **共同历史全文**：`docs/reviews/T06/local-review-1..6.md`、`out/review-common-history/local-review-7.md`、`round-1/minimax-m31flash.md`、`round-1/zcode-glm53.md`、`round-1/zcode-glm53-process-addendum-20261022.md`、`round-1/minimax-owner-audit-20261022.md`、`round-1/zcode-owner-audit-20261022.md`、`round-1/resource-remediation-plan-20261022.md`、`round-1/resource-remediation-independent-review-20261022.md`。
- **两个已解包证据包**：`resource-fix-3be0397-owner-validation-20261022-unpacked/`（含 26 份 receipt/stdout/stderr、`owner-first-failures/` 10 条原工具行 + `raw-tool-rows.jsonl` 40492 B、`run_cost_matrix.py`、`verify_equivalence_and_cost.py`、`run_evidence.py`、完整 base→产品 patch）与 `resource-fix-3be0397-independent-validation-20261022-unpacked/`（`adversarial.py`、两个 receipt、`extra_cases.py`、`measure_original_inputs.py`、`source-and-diff-audit.json`、`t09-byte-audit.json`、`final-evidence-manifest.json` 等）。
- **13 项受审来源全文**（含 `counterexamples.json` 全量解析：9 个 case 的全部 request/expected/reasoning_facts 逐字段解析，非显示截断）。
- **完整 base→产品 diff**：我独立生成 `out/reviewer-verify/planner-613-vs-3be0397.diff`（旧 613 planner 与当前 planner 的逐行差分，207 插入 / 112 删除），并完整读取；另核 76 文件 diff 统计。
- **主 PRD**：第 7.7 节 FR-600–604 原文、附录 C 能力矩阵、E.1/E.2/E.3/E.4/E.5、G.0（G-base/G-behavior）、G.3、10.2、第 16 节 Q5。
- **owner 新 helper 全文**：`run_cost_matrix.py`、`verify_equivalence_and_cost.py`、`run_evidence.py`（执行前通读，确认其对树只读、仅失败路径写 `mismatch.json`）。

## 4. 实际执行的命令与结果（本方真实 exit）

全部无窗口；使用本树独立 `node_modules`/`.venv`；未运行 Electron/e2e/native/HMR/GUI/Keychain/模型 API/密钥/付费。

| 验证 | 命令 | 实际结果 |
|---|---|---|
| 行为专项 | `uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q` | **exit 0，139 passed in 1.16s**（`out/pytest-behavior-reviewer.log`） |
| 全仓检查 | `npm run check` | **exit 0**：eslint/prettier/3×tsc/vitest **15 文件 630 测试全过**/electron-vite build/ruff+format/pytest **1191 passed in 54.74s**；`All checks passed!`（`out/npm-check-reviewer.log`，含真实 `EXIT=0`） |
| 九例 T09 probe | `uv run --frozen python docs/iterations/T06/probe_t09_baselines.py --source-root out/t09-approved-873c8c0 --manifest-sha aaaef2c0… --output out/T06-REVIEWER-3be0397-probe.json` | **exit 0**，`case_count=9`，`product_runtime=not-executed`，`formal_acceptance=false`，`reasoning_source=manual gold test input`；输出 SHA-256 `d18e5059394b11f6f783d4247c8e4f074a102a58d5ef3d48c3272fc248339c9e`，**与 owner/round-1 记录逐字节一致** |
| 作者脚本复现 | 复制 `build_corpus.py` 到本方 `out/reviewer-verify/` 重跑 | 生成件与受审 `counterexamples.json` **规范 JSON 完全相等**（`f84c378881ab56646e1e3cf88c7ca7c2b6e8a3e18e486b8841c657057390d20d`），仅数组展开/收拢的 prettier 排版不同；作者脚本不导入被测实现 |
| **本方独立对抗脚本** | `uv run --frozen python out/reviewer-verify/adversarial.py` | **exit 0，34/34 全过**（A 段穷举/随机 oracle、B 段全管线差分、C 段定向负例），证据 `out/reviewer-verify/adversarial-result.json` |
| **本方独立复测** | `uv run --frozen python out/reviewer-verify/measure_current.py` | **exit 0**：creates 200/400/800 与 1000×1000 矩阵的 **input SHA 与完整 plan SHA 与 owner 配对记录全部一致**（`out/reviewer-verify/measure-current.json`） |
| 独立变体规模 | `uv run --frozen python out/reviewer-verify/scaling_distinct_props.py` | 800 create × **10 个不同单值属性** → 0.199 s（近线性），非针对"重复同槽"形状的特调 |

### 4.1 本方独立对抗脚本要点（A/B/C 三段，共 34 项）

**A 段：首次冲突对等价性（自写 oracle，不复用既往脚本）**
- A1 单槽穷举长度 0–5、实例 {E1/E2}×{BA/BB}、值 {v1,v2,v3}：**271,453 例，不一致 0**。
- A2 双槽穷举长度 0–3、槽 {status, other}：**14,425 例，不一致 0**（跨桶全局最小 (i,j) 保持）。
- A3 随机 40,000 例，含 `create.initial` 多写（一条 intent 贡献多写、全局写序号推进）：**不一致 0**。
- A4 退化用例：`[(A,x),(A,y),(B,x)]` → 报 (1,2)；"X 槽 (0,3) 与 Y 槽 (1,2) 同时冲突" → 报 (0,3)；重复 `(instance,value)` 代表压缩只影响搜索索引。均与 oracle 一致。
- 我的 oracle 是**按旧 `combinations` 契约独立重写**的：全量写展开 → 按写序两两配对 → 同实例跳过 → 同槽且 typed 值不同 → 取最小 (i,j)。

**B 段：全管线差分（当前 vs 冻结 613 基线）**
- 1,500 例随机请求（随机 set/add/create/notify、随机 typed 值含 `False/0/1/1.0/"x"/"雪"`、随机 trigger/priority/enabled/conditions、随机事件编辑 set/add/remove/delete_object/declare/create、含重复事件投递）：**802 plan + 698 domain error，无 unexpected exception**；每例比对**完整 plan JSON** 或**完整 reason/location/evidence**，**0 处不一致**；并断言调用方请求未被修改。

**C 段：定向负例（23 项，含我在本轮新增的自建用例）**
typed 竞争（1 vs 1.0 / 1 vs True / False vs 0 / "1" vs 1）· 同值跨实例保留双方通知且事实唯一 · 实例内部中间写仍参与跨实例竞争且冲突对与旧全局首对一致 · delete_object 删除出边与关系入边、declare 不复原事实 · notify id 与对象 id 双向碰撞 · 每条 decision 独立 conditions 容器 · 跨调用无共享可变工作区 · 1000 源动作（每个 create 5 个 initial）通过 / 1001 拒绝 · 未知字段 / NaN / 孤立代理项拒绝 · 模板白名单单次替换且插入文本不被重解释 · 事件失败保留原 `event_index`+`event_sequence`（源位置≠执行顺序） · 推导单值矛盾 → `cardinality_violation` · 条件基于动作前冻结快照 · diff 基线为 before→candidate（含事件阶段与通知） · consumption scope 不符拒绝 · peer 不可引用他实例 create · 推导事实参与条件求值。

## 5. 发现

严重度定义：**P1** = 语义/正确性错误或安全边界破坏；**P2** = 规模/健壮性显著缺陷或契约与实现不一致；**P3** = 契约粒度/诊断完整性/边界歧义，需澄清或改进。

### P3-1（实现，前置条件未强制）`_edit` 兼容包装器对未校验状态会静默去重重复事实

- **源码位置**：`packages/engine/src/ontolearn_engine/behavior/planner.py:280–288`（`_edit`）、`planner.py:175–183`（`_Workspace.__init__`，其中 `planner.py:178` 为 `self.facts = {_json(fact): dict(fact) for fact in state["facts"]}`）。
- **触发输入**：以 `_edit(state, …)` 传入含两条相同事实的状态：`{"objects":["X"],"facts":[{"subject":"X","property":"status","value":"v"},{"subject":"X","property":"status","value":"v"}],"notifications":[]}`。
- **实测证据**（`out/reviewer-verify/probe-edit-unvalidated.stdout.log`，本方实际输出）：同一状态经 `_state()` 校验 → `duplicate_fact / state.facts`（被正确拒绝）；经 `_edit(…, {"kind":"declare","object":"Y"}, …)` → **被接受，事实数由 2 静默变为 1**。即 `_Workspace` 的字典键索引把 `_state()` 原本会拒绝的非法输入"修好"了。
- **影响**：当前**不可达**——唯一调用方是 `baseline_adapter.adapt_case`，其状态来自 `model_state()`，已由 `_state()` 校验（`baseline_adapter.py:211`）。但本轮冻结输入的对抗检查项明确包含"先 `_state` 验证后索引**不静默去重非法输入**"，而该保证目前只由调用方自觉维持、包装器自身不强制。将来任何新增调用方或适配器改动一旦传入未校验状态，重复事实会被静默丢弃而非按 `duplicate_fact` 拒绝，属于"验证先于索引"不变量的潜在回归入口。
- **建议**：在 `_edit` 内先调用 `_state(state, schema, classes)`（成本是每次适配器 setup 一次 O(facts)，可忽略），或至少在 docstring 中把"传入状态必须已通过 `_state`"写成可执行断言而非散文约定。不要改变其他任何行为。

### P3-2（诊断粒度）失败的 `create` 编辑已部分写入的效果未列入 `discarded_event_edits`

- **源码位置**：`planner.py:218–225`（`create` 分支：`self.objects.add(obj)` 先于 initial 循环；`planner.py:219` 的 `_explain(initial_index=index)`）、`planner.py:441`（`discarded_edits.append(...)` 只在 `workspace.edit(edit)` **成功返回后**追加）。
- **触发输入**：事件编辑 `{"kind":"create","object":"NEW","initial":[{"property":"status","value":"ok"},{"property":"nope","value":"bad"}]}`（`nope` 不在 schema）。
- **实测证据**（`out/reviewer-verify/probe-partial-create.stdout.log`）：`reason=invalid_property`、`location=fact.property`；evidence = `{stage: event_preparation, edit_index: 0, initial_index: 1, event_id: E1, event_index: 0, event_sequence: 0, discarded_event_edits: [], event_trace: [], committed: false}`。即该 create 已把对象 `NEW` 与 `status=ok` 写入工作区后失败，这些**已丢弃的部分效果没有出现在 `discarded_event_edits`**（该列表只收录"先前成功编辑"）。
- **影响**：读者可由 `edit_index=0` + `initial_index=1` 定位失败点，但无法从证据看出"失败前已临时创建了对象 NEW 并写入一条事实"。`interface.md:50` 的现措辞是"事件准备失败的**先前编辑**标为 discarded_event_edits"，字面上未被违反；这属"失败部分解释"的可读性缺口，而非语义错误。全部此类编辑仍被整体丢弃、无 candidate/新 consumption、输入未变（本次实测 `input unchanged: True`）。
- **建议**：在事件准备失败时，把**失败编辑本身**及其部分效果摘要（对象已登记、已应用的 initial 序号）一并记入失败证据（例如 `discarded_event_edits` 增加一条带 `partial_effect` 的记录，或新增独立字段），以便"丢弃模拟"与"正式执行"的区别可被完整重建。属诊断增强，不改语义。

### P3-3（接口措辞）`before` 是规范化后的前事件状态，不是调用方提交状态的字节副本

- **源码位置**：`planner.py:358`（`_state(request["state"], …)` 会对 `objects`/`facts` 就地排序规范化）、`planner.py:975`（`"before": request["state"]`）。
- **触发输入**：调用方提交 `state.facts` 未按规范序排列（受审测试的等价断言 `result["before"] == req["state"]` 只因私有 fixture 本身已排序而成立）。
- **影响**：调用方若以"提交状态的字节副本"理解 `before`，在未排序输入下会观察到列表顺序差异。规范化本身是既有既定行为（`interface.md:28` 要求输出保持规范排序），diff 基线也建立在同一规范化状态上，因此**无正确性影响**；仅接口文档未把这一点写明。
- **建议**：在 `interface.md:34` 对 `before` 补一句"为规范化后的行为前状态（对象与事实按规范序），不是提交状态的字节副本"。

### P3-4（接口措辞）整请求级形状/有限 JSON 失败没有 stage，仅 `location=input` 且 evidence 为空

- **源码位置**：`planner.py:319`（`request = json.loads(_json(request))` → 有限 JSON 门）、`planner.py:320–338`（`_shape(request, (…), location="input")`）。
- **触发输入**：请求顶层出现未知字段 → `invalid_shape / input`；事件载荷含 `NaN` → `invalid_json / input`；事件 ID 含孤立代理项 → `invalid_json / input`。
- **实测证据**：本方 C9a/C9b/C9c 三项实测均为上述 reason/location，evidence 为空字典（无 `stage`、无 `committed`）。`interface.md:48/54` 列举的阶段集合（`event_preparation`、`definition_validation`、`condition_evaluation`、`intent_limit`、`intent_validation`、`conflict_check`、`candidate_simulation`、`event_validation`）中**不含整请求级门**。
- **影响**：整请求被拒是安全的（无输入修改、无部分状态），但诊断上无法区分"请求形状错误"与"某个具体字段错误"，且 `committed=false` 不出现在该层证据中。属阶段枚举的文档/契约粒度问题。
- **建议**：或在 `interface.md` 补一句整请求级门的位置约定（`location=input`、无阶段），或在实现中给该层一个固定阶段名与 `committed=false`；两者取其一即可，不必改动现有错误码语义。

### 5.1 本轮未发现的问题（已独立核对并排除）

以下均为我在本轮亲自核对、结论为**符合当前合同**的项，记录以免被误当作未验：

- **首次冲突对**：`_first_conflict`（`planner.py:688–726`）按槽分桶、去重仅用于搜索索引、跨桶取全局最小 (i,j)。**穷举 + 随机 + 退化用例与旧 `combinations` 语义 0 不一致**（见 4.1 A 段），并满足冻结输入"首冲突必须等价旧全局 combinations 的最小 (i,j)，不是最早闭合 slot，索引去重只减搜索不删 intents"。
- **同值保留**：跨实例同值单值写入不冲突、双方通知与其他动作全部保留（实测）。
- **实例内部顺序覆盖**：允许；实例内中间写仍参加跨实例竞争（实测冲突对与旧全局首对一致）。
- **`create.initial` 隐含写**：按一个源动作计数（1000 个 create 各 5 个 initial → 1000 源动作通过；1001 → `action_limit`），全部 initial 单值写参加竞争。
- **冻结与绑定**：`binding/assertion_digest/ontology_version/rules_version` + `status=current` 校验；推导并集只读；单值矛盾拒绝；陈旧绑定拒绝；`PreparedRound` 保留原请求数组顺序。
- **事件身份**：同 ID 同内容 no-op；同 ID 异内容整批拒绝并带原 `event_index`。
- **typed JSON**：值键用 `_json` 保留 JSON 类型差异（`false/0`、`1/1.0` 均为不同值）。
- **模板白名单**：仅 `{eventId}/{behaviorId}`，一次替换，插入文本不被再解释；残留花括号拒绝。
- **未知字段 / 有限 JSON / Unicode**：各层 `_shape` 严格；`allow_nan=False`；入口 UTF-8 编码校验拒绝孤立代理项。
- **失败语义**：staged evidence、`initial_index`、`partial_decision`、`discarded_event_edits/discarded_actions`、`executed_actions` 恒空、`committed=false`、无 candidate/新 consumption、输入不变（实测）。
- **固定输入适配**：`load_bundle` 核 manifest SHA、PRD source SHA、逐文件 SHA，越根拒绝，解析使用已核验 buffer；`project_candidate`（`baseline_adapter.py:490–583`）复验全部展开 subject/predicate、通知 ID/事件/生成类型 IRI；通知两条 RDF 陈述只投影一次；`actionTrace` 保持 1-based 源动作粒度。
- **公共暴露面**：`behavior/__init__.py` 仅导出 4 个符号；`baseline_adapter` 不在包出口；本候选未在 worker/protocol/storage/`apps/desktop` 注册行为执行入口 —— **符合"私有范围"声明，但这不等于公共链路已验收**。

## 6. 历史问题逐项自行处置（不沿用任何既往 Pass）

| 来源 / 级别 | 问题 | 本轮独立处置 | 核验依据 |
|---|---|---|---|
| LR1 P1 | 静态 create 破坏重复事件幂等并阻断空轮次 | **关闭，未回归** | 常量 create 仅在 `_static_references` 登记供本行为引用，实际碰撞仍由触发实例的 `_edit(create)` 拒绝；重复/空轮/disabled/不匹配/新事件碰撞五项回归随 139 专项全过 |
| LR1 P2 | 冲突证据与非空 Diff 缺完整预期断言 | **关闭，未回归** | B-05/B-09 完整 conflict/intents/event_trace 与成功例完整非空 diff 全字段断言；我另以 1,500 例全管线差分覆盖 |
| LR3 P2 | 事件预校验缺阶段与原始源位置 | **关闭，未回归** | 本方 C11/C11b 实测：`event_index=0`（原数组下标）+ `event_sequence=10`，与执行顺序（sequence 0 的 E1 先执行）分离 |
| LR5 P2#1 | 展开身份未过 IRI 验证可投影非法 RDF | **关闭，未回归** | `project_candidate` 对全部事实 subject/predicate、通知 ID、关联事件、生成类型逐项 `_iri`；四类非法展开身份负例随 139 专项通过。注：`iri()` 实现在 `packages/engine/src/ontolearn_engine/rdf_snapshot.py`（要求 scheme、拒绝空白与 `<>"{}|^\``），**该文件不在本候选 diff 内**，属 base 既有代码 |
| LR5 P2#2 | `create.initial` 动态解析漏 `initial_index` | **关闭，未回归** | 本方 `probe-partial-create` 实测 `initial_index=1` 精确；既有 creation 测试逐字断言完整 evidence |
| LR2 / LR4 / LR6 / local-review-7 | 整轮"通过"结论 | **不作为本轮依据** | 本轮重读当前完整实现、重跑 139 专项、npm check、九例 probe，并自建 34 项对抗与 1,500 例差分；旧结论仍只属于各原候选 |
| Round-1 MiniMax P2-1 | 写意图二次复杂度 | **机制关闭，容量事实保留** | 见第 7 节；旧"限额被 initial 绕过"的表述不成立（1000 是源动作限额，E.2 与 `t09-adaptation.md:7` 一致），不采纳该措辞 |
| Round-1 MiniMax P2-2 | B×E 决定矩阵无上限 | **不关闭，保持 P2 容量风险**；本私有范围当前非阻断 | 见第 7 节 |
| Round-1 MiniMax P3-1 | 单个 `create.initial` 内重复单值属性静默覆盖 | **关闭（合同已明确）** | `interface.md:26` 明确"initial 按列表顺序应用，单值同槽后项覆盖，轨迹保留完整原列表，任何中间单值写入仍参加跨实例竞争"；实现实测符合，且中间写仍触发竞争。改为 `cardinality_violation` 属新语义决定，不在本候选擅改 |
| Round-1 MiniMax P3-2 | 跨实例同对象 create 碰撞整轮拒绝 | **关闭（合同已明确）** | `t09-adaptation.md:9`"原 create 碰撞仍拒绝"；E.1 的同值幂等通则指单值**属性写入**，不等于对象创建合并；declare 是独立的幂等节点登记。实测两个碰撞方向均拒绝 |
| Round-1 MiniMax P3-3 | 成功路径不保留事件原始源位置 | **关闭（非现合同违约），保留为可选诊断观察** | `interface.md:54` 只承诺**错误**路径源位置；`PreparedRound.document.request.events` 保留原数组。若把 `event_index` 加入 `consumption.events` 会被 `_shape` 严格拒绝，且会使消费身份依赖投递位置，破坏"同 ID 同内容即 no-op"规则 —— 不擅自扩合同 |
| Round-1 MiniMax P3-4 | diff 基线含事件阶段效果 | **关闭（合同已明确）** | `interface.md:34` 定义 diff 为 before→candidate 总净变化；本方 C14 实测含事件阶段与通知。**同意**不得改用 frozen→candidate（frozen 含只读推导事实，会把"推导未持久化"误报为行为删除） |
| Round-1 ZCode P3-1 | fingerprint 未点名排除 sequence | **关闭（本候选已实施）** | `interface.md:7` 现文已写"事件 fingerprint 包含类型、版本、载荷和 edits，明确排除 `sequence`" |
| Round-1 ZCode P3-2 | 适配动作属性值原样 JSON 标量边界 | **关闭（本候选已实施）** | `t09-adaptation.md:12` 现文已写"动作中的属性值按已声明动作的原样 JSON 标量保留……不冒充附录 C 的完整值语义" |
| Round-1 ZCode 信息项 | `rdf:type` 保持集合基数 | **确认属有意行为，无需修改** | `baseline_adapter.py:182` 将 `rdf:type` 初始化为 `cardinality: "many"`，`singleValuedPredicates` 仅做存在性校验（`:196–201`） |
| 指定过程门 | ZCode 4 次 PreToolUse 拒绝、首 stdin 20PASS/2FAIL/exit1、修正 5PASS、合计 27 条结果；MiniMax 的 probe/argv 缺口 | **仍归总控/指定流程裁定，本轮不重跑、不执行任何归档被拒脚本** | 我已读回 owner 包 `owner-first-failures/` 10 条原工具行（5853/5857/5861/5865/5876/5880/5892/5896/5900/5904）：5853/5857 ruff exit 1；5861/5865 format exit 0 但 pytest exit 2（adapter 仍 import 已删 `_edit`）；5876/5880 恢复兼容 wrapper 后 122 passed exit 0；5892/5896 新测试 E501 且 1 fail/16 pass exit 1；5900/5904 改 `sort_keys` 后 139 passed exit 0 —— **首败链真实存在且未被抹平** |
| UI 线 / 其他开发线 | 不在本候选 | **不读取、不冒充** | 未读 `T06-behavior-ui` 任何内容 |

## 7. 两项历史资源 P2 的本轮独立实质裁决

### 7.1 P2-1 —— 本次指向的可避免机制：**已修复**（我独立确认）

原报告指向三处可避免的重复工作，在当前候选对应 `planner.py:167–288`（编辑索引）、`planner.py:688–726`（按槽冲突搜索）、`planner.py:781–789`（推导事实键集一次生成）、`planner.py:927–955`（增量 effect 与边界排序）。我的独立证据：

1. **语义等价**（比"没变快"更强）：A 段 271,453 + 14,425 + 40,000 例首次冲突对与旧 `combinations` oracle **0 不一致**；B 段 1,500 例全管线（802 plan / 698 error）与冻结 613 基线**完整输出/证据逐字节相等**。即"分桶 + 去重 + 增量 effect + 边界排序"**没有改变任何可观察语义**，包括首冲突对、错误阶段与证据。
2. **机制确已消除**：creates 家族（每个 create 50 个重复同槽 initial）我实测 **0.122 / 0.248 / 0.565 s**（200/400/800），旧 613 为 **8.675 / 33.185 / 131.516 s**；旧为每翻倍约 4×（近二次），新为每翻倍约 2.0–2.3×（近线性）。
3. **不是只对"重复同槽"特调**：另以 **800 create × 10 个不同单值属性**（8000 条事实）实测 0.199 s，近线性。
4. **未引入规避输出的取巧**：百万级矩阵仍产出 1,000,000 条决定、1,000,000 个独立 conditions 容器，且完整 plan SHA 与 owner 记录一致；未分页、未删 disabled/mismatch、未共用可变 conditions、未暗设配额或拒绝。

**裁决**：P2-1 **所指的本次可避免机制关闭**；原 P2 的严重度事实与"create.initial 字段数不是动作限额、限额未被绕过"的正确表述一并保留。**不据此宣称任何生产速度、容量或倍数承诺**——我的测量是本机（macOS-27.0.1-arm64、Python 3.12.12）上该精确合成输入的一次测量，未控制其他桌面负载，不是生产指标。

### 7.2 P2-2 —— 完整 B×E 决定输出：**不关闭，保持 P2 容量风险**

- **合法反例仍成立**：1000 个不匹配行为 × 1000 个接受事件 = **零动作**、**1,000,000 条完整决定**。源动作上限不限制这些记录（`interface.md:28` 明写"源动作 1000 不是事实量、字段量或字节量上限"），未触发组合**不能**被称为绕过动作限额。
- **本方独立实测**（`out/reviewer-verify/measure-current.json`）：traced peak **340,522,087 B**、wall **10.184 s**；owner 同口径 340,522,343 B / 11.710 s；旧 613 为 345,860,759 B / 11.622 s。**成本与旧候选同量级，本候选使其峰值略降约 5.3 MB（1.5%）、墙钟略降，但 Ω(BE) 下界未变。**traced peak 是 **tracemalloc 跟踪的 Python 分配峰值，不是 RSS**；墙钟测量开启了跟踪，**不是**无跟踪常规耗时。
- **本候选没有把成本"优化掉"**：340 MB 不是"已解决"，本报告不这样表述。
- **是否阻断本范围（我自己的判断，不照抄）**：**当前私有 S1 范围内不阻断**，理由是——(a) 现合同要求完整决定集合且明写"不截断或分页"（`interface.md:28`，输出字段见 `:34`），PRD **Q5/10.2 未批准任何规模、参考设备、时间、内存或磁盘阈值**，因此不存在被违反的已批准验收线；(b) 成本来自输出合同本身的 Ω(BE) 材料化，**不是本候选引入的实现缺陷**，本候选也未使其变差；(c) 该模块目前只是显式调用的私有纯函数，无公共注册、无 Store、无真实运行、无并发与端到端持久化路径，实际容量主张尚不存在可被违反的正式对象。
- **同时明确不成立的**：不能据此宣称"适合生产规模"、"取消可响应"、"内存/RSS 预算合格"、"同事务序列化/持久化可靠"。**Q5 的规模/设备/时间/内存线仍未批准**，正式容量门与父模块验收**保持开放**，需要 Q5/对应 owner 形成可测指标后由父模块联验裁定。我**没有**替 Q5 填任何默认答案，也**没有**用"装配前再说"代替本轮判断。

## 8. 未验事项（本轮一律未验证，不得据本报告视为通过）

真实推理服务接线与真实推导（当前全部推导为 **MANUAL GOLD**，`product_runtime=not-executed`、`formal_acceptance=false`，`expected` 不代表实际 Store payload）· 通用 RDF codec 与附录 C 完整 literal 语义（当前为 JSON 标量，非完整 RDF literal 编解码器）· Store 原子轮次提交、回滚、取消、迟到投递与恢复（`Store.commit` 未接入）· 完整 E.2/G.3 轮次正式验收、资源 B-07 与轮末推理/指标 · Agent B-08 真实工具失败表达 · 公共业务方法/受限错误映射/权限/取消/分页与轨迹交接（`BehaviorError` 与私有 evidence 不可直接转发 renderer/Agent）· UI 正式接线（另树 `T06-behavior-ui`，本轮未读取）· 公共注册 / IPC 暴露（本轮静态确认未暴露，不等于公共链路已验收）· 设备规模、并发、RSS、端到端持久化容量与 **Q5** · GUI / native 两 OS / Electron / e2e / HMR / Keychain / 模型 API / 密钥 / 新增支付（**本轮一律未执行**）· 打包（`package:dir`）、CI、远端核验、push/PR/正常合并/生产 · 指定审查过程门（ZCode 四拒绝/首败/27 条计数等）仍归总控裁定。

## 9. 本轮只读性声明与首败记录

- 未修改实现、测试、依赖、锁文件、配置、公共文件或 AGENTS；未切分支、未提交、未推送、未开 PR；未写入原开发树 `.worktrees/T06-behavior`（仅作只读来源）；未读取另一模型本轮提示/会话/报告/意见；未读取 UI 树。
- 本轮写入仅两处：本报告 `docs/reviews/T06/round-2/minimax-m31flash.md`，以及本人 `out/` 证据（`out/pytest-behavior-reviewer.log`、`out/npm-check-reviewer.log`、`out/T06-REVIEWER-3be0397-probe.json`、`out/reviewer-verify/` 下对抗脚本与结果、测量脚本与结果、T09 字节审计、planner 差分、作者脚本复现件、两个边界探针）。
- **本轮我自己的首败（如实保留，不写成首轮全绿）**：
  1. `out/reviewer-verify/adversarial.py` 第一次运行真实 **exit 1**（`IndexError`），原因是我的穷举组合维度写错（`itertools.product` 未分块），**是我的脚本缺陷**；第二次运行因 A2 组合空间达 72⁶ 被我主动停止并重新限定规模，**该次中止不是产品失败**。
  2. 首次完整跑出 **7 项 FAIL**：A4a/A4b/C9a/C9b/C9c/C12/C14 —— 逐条复核后确认**全部是我方预期错误**：A4a 我误判 `(A,x),(A,y),(B,x)` 应报 (0,2)，实际旧语义报 (1,2)（同值 x 不构成竞争）；A4b 我设计的用例根本不含实际竞争对；C9a/b/c 我对"整请求级门"的错误无 `stage/committed` 证据却仍套用计划阶段断言；C12 我未真正传入矛盾的推导事实；C14 我漏算了通知记录进入 diff。修正预期后 **34/34 全过**。实现本身在这些点均与旧语义及现合同一致。
  3. 我的 `expect_error` 辅助函数最初对整请求级错误误判为失败（严格性错误，非实现问题），已按证据字段是否含 `stage` 区分。
- 全部验证命令的完整 stdout/stderr 与真实 child exit 均保存在本方 `out/`；未用展示用 `tail` 或管道状态替代真实退出码。

## 10. 明确结论

- **本独立 S1 范围（私有行为计划算法 + T09 固定输入只读适配）：通过。**
- **历史问题**：LR1/LR3/LR5 全部 P1/P2 关闭且未回归；Round-1 MiniMax 2×P2 按第 7 节分别裁决（P2-1 机制关闭、P2-2 保持 P2 容量风险），4×P3 关闭为合同已明确；Round-1 ZCode 2×P3 已在本候选实施、关闭；1×信息项确认为有意行为。
- **新发现**：**0 项 P1、0 项 P2、4 项 P3**（P3-1 实现前置条件未强制；P3-2 失败编辑部分效果未入 discarded 列表；P3-3 `before` 为规范化状态未写明；P3-4 整请求级门无 stage）。
- **无法验证项**：见第 8 节。
- **本报告不改写、不引用另一模型的结论**；开发者应全文读回并处理第 5 节意见。**不关闭 FR-600–604 父模块、完整 G.3 轮次、B-07/B-08、Q5 容量门或 T06 整体验收。**
