# T06-S1 独立对抗审查报告（MiniMax Code M3.1-Flash / xhigh）

审查者：MiniMax Code M3.1-Flash（xhigh），独立新任务，未读取同轮另一模型（ZCode GLM-5.3）的提示、会话、报告或意见。
结论：**此独立 S1 范围 —— 有条件通过（Pass with Conditions）**。语义层未发现 P1/P2 级缺陷；发现 2 项 P2（规模/健壮性）与 4 项 P3（契约与诊断粒度）。P2 需在父模块正式接线前解决或由总控明确接受为已知边界；本结论**不关闭** FR-600–604 父模块、完整 G.3 轮次或 T06 整体验收。

---

## 1. 任务来源与执行身份

| 项目 | 实际值 |
| --- | --- |
| 任务来源 | 2026-10-22 派发操作补充 + 下方原冻结正文（补充节优先） |
| 实际模型 | `minimax/MiniMax-M3.1-Flash`（`session get me` 读回 `effective_model`） |
| 思考等级 | `thinking.effort = xhigh`（同一读回） |
| 会话 ID | `mvs_a864253984c3453f982eeaa1cdfb43d8` |
| 任务实际权限 | `permissionMode = bypassPermissions`（始终授权 / Full access）；来源为任务冻结输入 `frozen-inputs.json` 记录的本次任务权限 + `/Users/kyle/.minimax/config.yaml:107` 的用户级默认值。用户级配置本身不作为当前会话证明，此处以任务记录为准 |
| 本任务 prompt SHA | `5096382b813ea6b12d2c6d14702631f43c4196b95b30ec52428d84453c2ded07`（与 `frozen-inputs.json` 记录一致） |
| 独立工作区 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-review-61396a5` |
| 分支状态 | detached HEAD（无分支，无切分支、无提交、无 push、无 PR） |
| 原开发树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior` —— **仅作只读字节比对来源，本次未写入任何字节** |

模型自身可核事实与 owner 外部读回已区分标注：上表模型、思考等级、会话 ID、权限来自任务输入与配置读回；本会话可独立核验的是工作区内容、Git 对象、测试与探针结果。

## 2. 固定 SHA 与范围核验（全部独立复核通过）

| 项 | 值 | 核验方式与结果 |
| --- | --- | --- |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git cat-file -e` 存在 |
| 产品候选 | `61396a598b2dffc1d3d2fd4660f9af1d5c93d266` | 存在 |
| 流程 HEAD（审查工作区） | `10f1d8c33820d9a882a153590d8488f6d3fa7723` | `git rev-parse HEAD` 一致 |
| 冻结流程前置 | `11d66ea267c56e1436f1f916dd6319a1914d9a59` | 存在 |
| 完整 base→产品 binary diff SHA | `e1b08e5c89b72f4d8a0a7e1ca57feadd91ced235301d1096fdfd07d8e5d507dc` | 独立重算 `git diff --binary base product \| shasum -a 256` **一致** |
| diff 规模 | 23 files / 13961 insertions | 独立统计 |
| T09 唯一批准 Git | `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` | 存在 |
| T09 manifest SHA | `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` | 独立重算一致 |
| 主 PRD SHA | `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` | 与派发一致 |
| 保护 AGENTS SHA | `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` | 独立 `shasum` 一致；保持 dirty（`git status` 显示 ` M AGENTS.md`）、未还原、未暂存 |

### 2.1 12 项受审来源四路逐 byte 一致性

对每项执行 `git hash-object`，在**产品 commit / 流程 HEAD / 审查工作区 / 原开发树**四者比对，结果全部相同：

| 路径 | blob |
| --- | --- |
| `packages/engine/src/ontolearn_engine/behavior/__init__.py` | `55b8c37a…` |
| `packages/engine/src/ontolearn_engine/behavior/baseline_adapter.py` | `3469d13a…` |
| `packages/engine/src/ontolearn_engine/behavior/planner.py` | `78bbc9bc…` |
| `packages/engine/tests/test_behavior_baseline_adapter.py` | `a33ed06a…` |
| `packages/engine/tests/test_behavior_creation.py` | `05f765a7…` |
| `packages/engine/tests/test_behavior_failures.py` | `c2352426…` |
| `packages/engine/tests/test_behavior_planner.py` | `33ab70c4…` |
| `tests/fixtures/behavior/build_corpus.py` | `02c4f530…` |
| `tests/fixtures/behavior/counterexamples.json` | `dcf5e115…` |
| `docs/iterations/T06/interface.md` | `69700f09…` |
| `docs/iterations/T06/probe_t09_baselines.py` | `453d31e8…` |
| `docs/iterations/T06/t09-adaptation.md` | `652c3c96…` |

辅助确认：`git diff --name-status <product> <flowHEAD> -- <12 路径>` 输出为空，即流程 HEAD 相对产品 commit **未改动任何受审路径**（仅提示/哈希类流程证据提交）。
`docs/reviews/T06/evidence/validation-61396a5.json` 中 12 项 `source_sha256` 逐项重算，mismatches = 0。

### 2.2 T09 固定输入字节核验

`out/t09-approved-873c8c0` 共 19 个文件（17 个 manifest 文件 + `manifest.json` + PRD）与 Git `873c8c0` 对应 blob **逐字节一致**。仅使用该只读缓存，未读取变化中的 T09 HEAD，未导入其 Python 实现。

## 3. 完整读取范围（全文，非摘要）

- `AGENTS.md`（受保护 dirty 版本）
- `docs/reviews/T06/review-readiness.md`、`docs/reviews/T06/status.md`
- `docs/reviews/T06/evidence/validation-61396a5.json`
- `docs/reviews/T06/local-review-1.md` … `local-review-6.md`（全部 6 份）
- `docs/iterations/T06/interface.md`、`t09-adaptation.md`、`probe_t09_baselines.py`
- 3 份 behavior 源码全文（`__init__.py`、`planner.py`、`baseline_adapter.py`）
- 4 份行为测试全文
- `tests/fixtures/behavior/build_corpus.py`、`tests/fixtures/behavior/counterexamples.json`
- 完整 base→产品 diff（23 文件 / 13961 行新增）
- 主 PRD：FR-600–604、附录 C、E.1、E.2、E.3、E.4、E.5、G.3（B-10 / B-11）

## 4. 实际执行的命令与结果

全部为无窗口验证，串行执行，使用本树独立 `node_modules` / `.venv`。

```bash
cd /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-review-61396a5

# 固定 SHA 与 diff 哈希
git diff --binary 5f910b52c69d86a1076b2032e5d3c63e715947f3 \
  61396a598b2dffc1d3d2fd4660f9af1d5c93d266 | shasum -a 256
# -> e1b08e5c89b72f4d8a0a7e1ca57feadd91ced235301d1096fdfd07d8e5d507dc  ✅ 与派发一致

# 行为测试
uv run --frozen pytest packages/engine/tests/test_behavior_*.py -q
# -> 122 passed in 2.32s

# 全仓检查（无窗口）
npm run check
# -> exit 0（含 lint / format / typecheck / vitest / build / ruff / pytest）
npm test
# -> 15 files / 630 TS tests passed；Python 尾段 1174 passed in 45.41s

# T09 固定输入 probe
uv run --frozen python docs/iterations/T06/probe_t09_baselines.py \
  --source-root out/t09-approved-873c8c0 \
  --manifest-sha aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e \
  --output /tmp/T06-REVIEWER-61396a5-probe.json
# -> exit 0；case_count=9；product_runtime=not-executed；formal_acceptance=false
#    输出 canonical sha256 = 0e6d1a210b593c9689612eb56b58ae3ff98a1d4a84ee83dec97fb42c451dbd66
#    与 evidence/validation-61396a5.json 记录完全一致
```

补充只读探针（全部位于 `/tmp/T06-review-61396a5/`，未改动任何受审文件）：

- **语序/排序**：优先级降序 → 行为 ID 升序 → 事件 sequence 升序 → 事件 ID 升序，四层键逐项验证通过。
- **跨实例单值竞争**：不同值 → `competing_write`（含 `conflict_slot`），跨不同行为与跨不同事件均命中；同值 → 保留全部其他动作与通知。
- **同实例内部顺序覆盖**：允许；与 peer 不同值仍 `competing_write`。
- **`create.initial` 隐含单值写入**：参与跨实例竞争（`conflict_slot = {subject, property}`）；`create` 计为一个源动作，初始字段不额外计数（1000×50 → `action_count = 1000`）；1000 通过 / 1001 `action_limit`。
- **冻结快照**：条件对 post-event 冻结快照求值；reasoning facts 并入冻结快照并可被条件看见；reasoning 单值矛盾 → `cardinality_violation`；stale status / binding / ontology_version → `stale_reasoning`。
- **事件身份**：同 ID 同内容 → no-op `duplicate_event`；同 ID 异内容 → `event_identity_conflict`（含原始 event_index）；消费台账重复事件重投 → no-op，不报 `duplicate_identity`。
- **失败路径**：文本仅为 `reason: location` 结构常量；含 `initial_index`；含 `committed=false`；无 candidate；失败后输入 request 不被修改。
- **边界拒绝**：未知字段 → `invalid_shape`；NaN → `invalid_json`；孤立代理项 → `invalid_json`；消费 scope 不符 → `consumption_scope_mismatch`；静态未知 subject → `invalid_object definition.subject`；动态未知 subject → `invalid_object fact.subject`（stage=`intent_validation`）；peer 创建对象不可引用、同实例自有 create 可引用；单值属性用 add → `cardinality_action_mismatch`；非白名单模板占位符 → `invalid_expression`。
- **模板**：单次替换不重解释插入文本；事件模板残留 `{}` 被拒。
- **投影侧**：独立复现 local-review-5 P2#1 的四类非法展开身份（fact subject / predicate / notification id / notification event），均在 `project_candidate` 被 `invalid_fixture_iri/baseline.iri` 拒绝。
- **公共暴露面**：`ontolearn_engine/__init__.py` 不导出 behavior；worker / protocol / storage 无 behavior 执行注册；`apps/desktop` 无 behavior 引用 —— 符合私有范围声明。

### 4.1 fixture 生成脚本独立重放

`build_corpus.py` 独立重跑后与 `counterexamples.json` 语义 **deep-equal = True**。committed 文件的 byte 差异仅为数组展开/收拢的 prettier 排版（committed 文件 `prettier --check` 通过；脚本仅 import `copy`/`hashlib`/`json`/`pathlib`，不导入被测实现）。**判定为排版差异，不作为缺陷。**

## 5. 发现

严重度定义：P1 = 语义/正确性错误或安全边界破坏；P2 = 规模/健壮性显著缺陷或契约与实现不一致，会在父模块正式规模下造成不可接受的行为；P3 = 契约粒度/诊断完整性/边界歧义，需澄清或改进。

### P2-1　写意图冲突扫描与事实写入为二次复杂度，大规模输入下耗时失控

**源码位置**
- `packages/engine/src/ontolearn_engine/behavior/planner.py:804` — `for a, b in combinations(writes, 2):`（跨实例单值写意图两两配对扫描，无提前退出、无按 subject/property 分桶）
- `packages/engine/src/ontolearn_engine/behavior/planner.py:178` — `if _json(fact) not in {_json(f) for f in state["facts"]}:`（每次写入对**全部**事实做一次全量 `_json` 序列化重扫）
- `packages/engine/src/ontolearn_engine/behavior/planner.py:856` — 候选模拟中每个动作后调用 `_normalize(candidate)`（重排全量候选）

**触发输入**
1000 个行为，每个行为一个 `create` 动作且带 50 个单值 `initial` 字段（总 1000 个源动作，**未触发** 1000 动作限额）。

**实测证据**（本轮复跑，可复现）

```
# 隔离：combinations 配对扫描成本（planner.py:804）
writes=2000 pairs=1999000  -> 0.15s
writes=4000 pairs=7998000  -> 0.61s
writes=8000 pairs=31996000 -> 2.42s      # 规模翻倍 → 耗时约 4 倍，二次增长

# 隔离：_put 单次写入的全量 facts 重扫成本（planner.py:178）
facts=5000  one put -> 0.007s
facts=10000 one put -> 0.014s
facts=20000 one put -> 0.027s
facts=40000 one put -> 0.061s            # 单次 put 随 facts 线性增长

# 端到端：N creates × 50 单值 initial
creates=200 -> 8.1s
creates=400 -> 30.0s
creates=800 -> 119.4s                   # 翻倍约 4 倍，整体呈二次增长
```

400×50 的 cProfile 归因显示热点集中在 `_json` 序列化（约 484 万次调用）。

**影响**
在 1000 源动作的上限内，行为数量 × 初始字段数一旦接近实际业务量（例如数百个行为各带数十个初始字段），单次计划可能达到**数十秒至分钟级**。由于 `create.initial` 字段数不计入 1000 动作限额（限额只计源动作），此开销**不在限额保护范围内** —— 限额保护被绕过。这属于可用性/资源边界缺陷，但**不影响正确性**：结果语义在所有规模上均正确。

**建议**
1. `planner.py:804` 改为按 `(subject, property)` 分桶后再在桶内两两比较，复杂度降为 O(n + Σk²)；同桶同值可直接跳过。
2. `planner.py:178` 的重复检测改为维护 `(subject, property)` → 规范化值集合的索引，写入时增量更新，避免每次全量 `_json`。
3. `planner.py:856` 的 `_normalize` 改为仅在受影响区间重排，或在规模超过阈值时切换为增量归并。
4. 明确 `create.initial` 字段总数是否需要独立上限（当前无限额），并在 `interface.md:26` 的「每轮动作上限 1000」条款旁写明该上限**仅计源动作**这一事实（当前 `t09-adaptation.md:7` 有此说明，但 `interface.md` 未写，接口文档与实现的口径存在文档缺口）。

### P2-2　behaviors × events 决策矩阵无上限，内存随乘积线性膨胀

**源码位置**
`packages/engine/src/ontolearn_engine/behavior/planner.py:698–751` —— 对**每个** behavior × **每个** accepted event 生成一条 `decision` 记录并全部保留在 `decisions` 列表中；`planner.py:756` 的 `action_count` 限额只统计**已触发实例**的动作数，未触发组合不受任何上限约束。

**触发输入**
1000 个行为（trigger 类型与事件类型不匹配，故无实例触发、绕过动作限额）× 1000 个 accepted events。

**实测证据**
```
behaviors=200  events=400  -> decisions=80000   peak=30MB  wall=0.9s
behaviors=1000 events=1000 -> decisions=1000000 peak=346MB wall=10.7s
```

**影响**
`decisions` 是成功输出的必备字段（`interface.md:32` 要求完整条件决定集合）。行为数与事件数相乘，无任何上限或分页。1000×1000 即产生 100 万条决策、峰值 346 MB，**在一个未触发任何动作的轮次中**。本模块的输出需与完整轮次快照同事务保存（`interface.md:30`），因此这份内存占用会传导到正式事务路径。这是资源边界缺口，不影响正确性。

**建议**
1. 为 `decisions` 引入显式上限或分页/流式契约（例如超限时按行为 ID 游标分批返回），并在 `interface.md` 写明；
2. 或对「完全不匹配的 behavior × event」组合做短路 —— 不匹配的 decision 只记录 `reason=event_mismatch`，可不保留完整 condition 结构；
3. 与 P2-1 合并评估：两者共同决定了该模块在正式规模下的资源画像，建议在 T07 资源预约（B-07）联验前给出实测数字。

### P3-1　单个 `create.initial` 内重复同一单值属性时静默后者覆盖

**源码位置**
`packages/engine/src/ontolearn_engine/behavior/planner.py:170–179`（`_put` 的单值分支：`if not many:` 先按 `(subject, property)` 剔除旧值再追加新值）配合 `planner.py:196–204`（`_edit` 的 `create` 分支对 `initial` 逐项调用 `_put`，**未检测同一 `initial` 列表内重复的单值属性**）。

**触发输入**
```json
{"kind": "create", "object": "O1",
 "initial": [{"property": "status", "value": "FIRST"},
             {"property": "status", "value": "SECOND"}]}
```

**实测证据**
```
single-value repeated -> facts: [{"subject": "O1", "property": "status", "value": "SECOND"}]
trace: [{"event_id": "E1", "behavior_id": "BA", "action_index": 0,
         "action": {"initial": [{"property": "status", "value": "FIRST"},
                                {"property": "status", "value": "SECOND"}], ...},
         "effect": "changed"}]
```
对照（同模块多值属性 `rdf:type`）：
```
rdf:type repeated -> [{"subject":"O1","property":"rdf:type","value":"Equipment"},
                      {"subject":"O1","property":"rdf:type","value":"HighRiskEquipment"}]
```
多值重复**两条都保留**；单值重复**只保留最后一条**，且 trace 仍标 `effect=changed`，不报 `cardinality_violation`，也不在任何输出中提示 `FIRST` 被丢弃。

**影响**
同一动作内的矛盾初始状态被静默解决。`interface.md:24` 只规定了「同值单值写入及相同多值追加保持状态幂等」和「实例内顺序覆盖允许」，**未规定单个动作内 `create.initial` 重复单值属性的语义**。从 E.1「单值属性只允许一个值」看，更一致的做法应是报 `cardinality_violation` 而非静默取后者。属契约缺口 + 语义不一致。

**建议**
在 `_edit` 的 `create` 分支内，对 `initial` 列表做同 `(property)` 的单值重复预检：值相同 → 幂等保留；值不同 → 报 `cardinality_violation`（附 `initial_index`）。并在 `interface.md` 补写该条语义。

### P3-2　跨实例同值 create 同一对象标识 → 整轮 `duplicate_identity`

**源码位置** `planner.py:190`（`create` 分支）、`planner.py:210`（`declare` 分支）

**触发输入**
两个不同实例（BA / BB）各以 `create` 创建同一对象 `SHARED`，初始值**相同**（`status=S1`）。

**实测证据**
```
same-value same-object create -> duplicate_identity edit.object
```

**影响**
`interface.md:24` 规定「同值单值写入及相同多值追加保持状态幂等」，但对象标识碰撞不走该幂等路径，而是整轮拒绝。`t09-adaptation.md:9` 明确「原 create 碰撞仍拒绝」，故**与本线既有设计一致**；但与 E.1「同值幂等去重」存在张力。这是**上层需确认的设计问题**，非实现与自身契约不符。

**建议**
请总控 / PRD 责任人确认：跨实例同值 create 同一对象标识，应为「幂等去重（同值保留）」还是「整轮拒绝（现有行为）」。若维持现状，建议在 `interface.md` 明确写出该例外，避免上层误按 E.1 幂等通则理解。

### P3-3　成功路径不保留事件原始源位置

**源码位置**
- `planner.py:371` — `event_trace.append({"event_id": event["id"], "reason": "duplicate_event"})`
- `planner.py:387` — `accepted.append({"event": event, "fingerprint": fingerprint})`

**实测证据**（输入数组顺序为 E2(seq=5) 在前、E1(seq=1) 在后）
```
event_trace: [{"event_id": "E1", "reason": "event_applied"},
              {"event_id": "E2", "reason": "event_applied"}]
consumption.events: [{"event_id": "E1", "fingerprint": "4280e3e..."},
                     {"event_id": "E2", "fingerprint": "0a55e10..."}]
consumption.instances: [{"event_id": "E1", "behavior_id": "BA"},
                        {"event_id": "E2", "behavior_id": "BA"}]
```
成功输出中**不含** `event_index`；事件源位置仅出现在失败路径的证据中（`interface.md:52` 的措辞恰只约束错误路径：「事件预校验、身份冲突和编辑失败均保留排序前的 event_index」）。

**影响**
需求「事件顺序与原始源位置分别记录」在**失败路径**已满足，在**成功路径**未满足：成功计划的 `event_trace` / `consumption` 无法把事件映射回请求数组下标。对「同一 ID 在多次投递中的具体哪一项」这类审计场景，成功轮次缺少定位信息。

**建议**
在 `event_trace` 与 `consumption.events` 的每条记录上追加 `event_index`（请求数组下标），与既有失败路径语义对齐；并在 `interface.md:52` 把该契约扩展到成功路径。

### P3-4　`diff` 基线为 pre-event 状态，含事件阶段效果

**源码位置** `planner.py:888` — `"diff": _difference(request["state"], candidate)`

**实测证据**
输出同时暴露 `before` / `after_events` / `frozen` / `candidate` 四态（顶层键：`action_trace, after_events, assertion_version, base_revision, before, behavior_version, binding, candidate, committed, consumption, decisions, diff, event_trace, frozen, kind, reasoning_version, round, run_id, scope, semantics_version`）。`diff` 的基线是 `request["state"]`（事件前），因此 diff 同时包含**事件阶段效果**与**行为阶段效果**，二者未分离。

**影响**
`interface.md:32` 要求「完整 Diff」，未定义 diff 应覆盖哪一段。消费者若把 diff 当作「行为造成的变更」理解，会把事件编辑效果误计为行为效果。属契约歧义，非错误。

**建议**
在 `interface.md:32` 明确 `diff` 的基线与覆盖范围；如需区分，可额外提供 `behavior_diff`（`frozen` → `candidate`）或明确 diff = `before` → `candidate` 的全集。

## 6. 历史问题逐项处置（自行核验，不采信既往结论）

| 来源 | 问题 | 我的独立复核结果 | 处置 |
| --- | --- | --- | --- |
| local-review-1 | P1 静态 create 检查破坏重复事件幂等 | 已修：静态 create 仅登记可引用对象，实际触发实例仍经 `_edit(create)` 拒绝碰撞。**独立复现**：首轮成功后以 candidate/consumption 作下一轮重投同事件 → 无 `duplicate_identity`（消费台账重投为 no-op） | **关闭** |
| local-review-1 | P2 缺测：冲突证据与 Diff 缺完整预期 | 已补。**独立复现**跨实例冲突：`reason=competing_write`、`location=behavior.intents`、`conflict_slot={subject,property}`、`decisions` 含全部 2 条、含 `intents`/`conflict` 完整证据、无 `candidate`、`committed=false`、`action_trace` 为空 | **关闭** |
| local-review-2 | （整轮「通过」结论） | 该轮通过结论**不作为本次依据**；相关项已按上两行独立重放 | 不采纳为结论 |
| local-review-3 | P2 事件前置校验缺阶段与源位置 | 已修。**独立复现**：同 ID 异内容 → `event_identity_conflict` 且含原始 event_index；非法 sequence/payload → 失败证据含 stage 与 event_index | **关闭** |
| local-review-4 | （整轮「通过」结论） | 同上，不作为依据 | 不采纳为结论 |
| local-review-5 | P2#1 展开身份未验 IRI，可投影非法 RDF | 已修。**独立复现**四类非法展开身份（fact subject / predicate / notification id / notification event）均在 `project_candidate` 被 `invalid_fixture_iri/baseline.iri` 拒绝 | **关闭** |
| local-review-5 | P2#2 `create.initial` 漏 `initial_index` | 已修。**独立复现**：动态 initial 字段失败 → 证据含 `initial_index` | **关闭** |
| local-review-6 | （整轮「通过」结论） | 同上，不作为依据 | 不采纳为结论 |

历史 local-review-1/3/5 的「不通过」原始结论保留，本报告不删改既往结论，只就其问题项给出本次独立处置。

## 7. 未验证事项（明确保留父模块边界）

以下均**不在**本次可验证范围，**不得**据本报告视为已通过：

- 真实推理服务接线与真实推导（当前全部推导为 **MANUAL GOLD**；`product_runtime = not-executed`、`formal_acceptance = false`；`expected` 不代表实际 Store payload）
- 通用 RDF 编解码与附录 C 完整 literal 语义（当前 JSON 标量非完整 RDF literal 编解码器）
- Store 原子提交、回滚、取消、投影身份与正式轮次事务（`Store.commit` 未接入）
- 完整 G.3 轮次正式验收、B-07 资源预约与产能、B-08 Agent 接入
- 公共注册与 IPC/UI 暴露（本次确认**未**暴露，符合私有范围）
- 父模块 FR-600–604 的整体验收、T06 整体验收
- Electron / e2e / native / HMR / GUI / Keychain / 模型 API / 密钥 / 新增支付：**本轮一律未执行**（无窗口验证约束）
- 打包（`package:dir`）、CI、远端核验、生产验证
- UI 树 `T06-behavior-ui`：**未读取**，不在本候选范围
- 同轮另一模型（ZCode GLM-5.3）的输入 / 报告 / 会话：**未读取**，未复用其推理结论

## 8. 结论

**此独立 S1 范围：有条件通过（Pass with Conditions）。**

- 语义正确性（E.1 / E.2 / FR-600–604 的私有范围）：**未发现 P1 / P2 级语义缺陷**。四层排序键、冻结快照求值、跨实例单值竞争、跨实例同值保留、源动作计数、失败解释与隔离、消费身份、模板白名单与单次替换、投影身份复验，全部经独立探针复核符合契约。
- 阻断项：**无 P1**。P2-1 与 P2-2 为规模/资源边界缺陷，**不改变结果正确性**，但会在父模块正式规模下造成数十秒级单轮耗时与数百 MB 级峰值内存，且 P2-1 中限额保护被 `create.initial` 字段数绕过。**建议在 T07 资源预约（B-07）正式联验前解决，或由总控明确接受为已知边界并写入文档。**
- P3-1 / P3-2 / P3-3 / P3-4 均为契约粒度与诊断完整性问题，需澄清或补充文档，不阻断本 S1 范围。
- **本结论仅覆盖「此独立 S1 范围」（纯计划 + 固定输入适配）。** 不关闭 FR-600–604 父模块、不关闭完整 G.3 轮次、不代表 T06 整体验收，也不替代指定的另一模型审查。

## 9. 本次操作的只读性声明

- 未修改实现、测试、依赖、配置、公共文件、AGENTS；未切分支、未提交、未 push、未开 PR。
- 未写入原开发树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior`（仅作只读字节比对）。
- 唯一写入：本审查树 `docs/reviews/T06/round-1/minimax-m31flash.md`（本文件）。原字节由 owner 归档回原开发树。
- 所有探针脚本与输出位于 `/tmp/T06-review-61396a5/`、`/tmp/T06-REVIEWER-61396a5-probe.json`。
- 结束时 `git status` 仍为：` M AGENTS.md` + 两份 dispatch 未跟踪文件，与审查前一致。
- 未运行 Electron / e2e / native / HMR / GUI / Keychain / 审查应用；未调用模型 API；未涉密钥、额度或付费。
