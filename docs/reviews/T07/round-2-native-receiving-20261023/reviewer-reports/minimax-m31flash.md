# T07-S1 R2 指定独立完整工程审查报告 · MiniMax Code (M3.1-Flash)

- 阶段：T07-S1（完整私有轮次编排 / 资源 FIFO 指标 / 独立场景页及现有验证）
- 唯一报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157/docs/reviews/T07/round-2/minimax-m31flash.md`
- 审查者：MiniMax Code 独立只读审查任务（M3.1-Flash / xhigh / 始终授权）
- 审查日期：2026-10-23
- 审查工作区：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157`（detached HEAD = reviewHead）
- 本角色 runtime：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-r2-f9a1157.runtime`
- 读取台账：`../T07-minimax-review-r2-f9a1157.runtime/metadata/reviewer-read-ledger.json`（148 项逐项 source/字节/哈希/EOF/工具方式）
- 原始验证输出：`../T07-minimax-review-r2-f9a1157.runtime/raw/validation/`（001–010 全部 stdout/stderr/exit/meta）

---

## 1. 结论（先行）

**结论：通过（限 T07-S1 私有候选范围），并附 1 项新的 P2 与 1 项新的 P3。**

本轮是我方在本固定候选上的**全新独立完整审查**：不沿用前轮任何结论（Z 的「限 S1 通过」、M 的「限 S1 通过」均只作历史材料），未缩为 delta。完整 25 路径 diff、14 项实现/测试/fixture、PRD V0.6 全文、全部历史/首错/35 个 log-PNG 原件/9 条原始 final/7 项意见/前轮过程失败均已独立核实；我方在本角色隔离环境重新运行了 4 组验证命令并完整留存原始 stdout/stderr 与目标退出码，另在合规 scratch 副本内重跑了 render-probe。

**新发现（P2，非阻断本 S1 范围，但必须在接线前处置）**：`Definition.digest` 对"语义等价、字节不等价"的输入过于敏感——同 ID 同内容重复事件、或仅事件顺序不同的 Definition，其运行语义完全相同（我方实测逐轮 created/completed/backlog/metrics/consumed 全等），但 `digest` 不同，导致显式续跑被拒（`Snapshot belongs to another input/configuration`）。这与「同一场景内容」的产品语义不一致，属契约精度问题，详见 §5.1。

**新发现（P3）**：`Definition.digest` 的构造方式使摘要依赖 `asdict` 的字段表示而非稳定规范化集合，见 §5.2。

未发现新的 P1；未发现实现级安全漏洞、越权注册、父能力冒领或证据造假。

**必须同时声明的限制（不得被读成产品通过）**：

1. 本次通过的只是**私有服务 + 私有页面 + 合成编排探针**这一 S1 子集。`ProbePorts.infer` 返回合成标记、`execute` 只模拟"一事件一工单"、`commit` 只捕获不可变值；`PersistentProbe` 只证明真实 SQLite 事务/隔离/崩溃边界。三项指标由合成状态统计得出，**合成指标不等于产品通过**。
2. 父领域全部未验且未关闭：真实 T05 推理（初始/事件后/轮末）、真实 T06 冻结条件/排序/冲突/动作与动作间取消、T01/I04 正式 scenario 任务注册与 project/run/job 身份、原子 Round+progress、取消/最后提交/终态竞态、operation-id/expectedRound 与响应丢失对账、公共契约/bridge/App 挂载与真实数据、用户真实删除运行/恢复基准/从快照创建与续跑、完整 E.5 `facts`/`inferred`/`actionTrace`/`triggeredInstances`、T10 跨设备重放、FR-700–705 与 E.2–E.5/G.4/G.6 父验收、Windows/macOS 完整产品与平台/发布门、真人验收、push/PR/CI/远端 develop 核验/合并/发布。
3. 前轮 **PROCESS_FAIL 裁决原文保留、不被本报告抵消**：Z 侧拒绝后包装执行且报告遗漏首错/拒绝、M 侧在固定 review checkout 原位运行 render-probe、M 侧向父项目派发 find 枚举、两方阅读缺项。这些是历史事实，不因本轮换新树、新收据或新候选而自动关闭。
4. 本报告不替代 ZCode GLM-5.3/最高一方结论，也不关闭父 Goal、CI、远端与发布门。

---

## 2. 任务身份、实际设置读回与缺失项

| 项 | 实际值 | 来源 |
| --- | --- | --- |
| 应用 | MiniMax Code | 本任务运行环境 |
| 实际模型 | **M3.1-Flash** | operator 收据 `actualSettingsUI.model`（本任务新建空任务 + 自选文件夹的 UI 实读）；与本会话运行标识 `MiniMax-M3.1-Flash` 一致 |
| 实际思考等级 | **xhigh** | 收据 `actualSettingsUI.thinking` |
| 实际权限模式 | **始终授权（Full access / bypassPermissions）** | 收据 `actualSettingsUI.permission` |
| 设置读回范围 | 自建空新任务 + 自选文件夹，不沿用既有活动任务 | 收据 `settingsScope` |
| 实际 native session ID | **`mvs_58e4985c72594853ac34354567ea2468`** | operator 收据 `actualSessionId`；与本会话系统标识完全一致 |
| 实际 task ID | **UNKNOWN** | 收据 `actualTaskId` 为空，官方未单独给出 |
| 实际 original turn ID | **UNKNOWN** | 收据 `originalTurnId` 为空，官方未给出；**不以旧 turn 复用或推测填补** |
| 官方 terminal 标量 | **UNKNOWN** | 收据 `officialTerminal` 为空 |
| 官方原生读链核验 | `fullNativeReadVerified: false` | 收据原文 |
| 独立性声明 | `globalConfigRead: false`、`peerOpinionsUsed: false` | 收据原文 |
| GUI 已释放 | `UIAccepted: true` | 收据原文 |

**缺项一律按 UNKNOWN 记录**：本轮未执行 `agent list`、`session get`、全局配置读取、父目录 find/枚举、未读取 R2 另一方（ZCode）的报告/目录/状态/队列/metadata/意见、未复用旧 SID 或旧 turn 身份。

**完全访问只是执行能力，不改变只读职责**：本轮未修改实现/测试/fixture/验收/PRD/配置/依赖锁，未 commit、未 push、未切分支，未把 `AGENTS.md` 暂存，未读取凭据，未新增付费或重置。

---

## 3. 输入受理与范围核验（本方实际执行）

| 核验项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| 官方附件字节 / 换行数 | 242581 B / 1700 | 242581 B / 1700 LF（末字节 LF） | ✅ |
| 官方附件 SHA256 | `525ac36e5e50…8ede` | 完全一致 | ✅ |
| 本方 `docs/reviews/T07/round-2-input/full-input.txt` | 与官方附件逐字节一致 | SHA256/字节数/换行数完全相同 | ✅ 逐字节一致 |
| 官方附件全文读取 | 至真实 EOF | 1–1700 行读到实际 EOF（工具按字节截断处续读） | ✅ |
| reviewHead | `fdfd908e36a8…7973` | 一致（detached HEAD） | ✅ |
| base → product → reviewHead 祖先关系 | B 是 P 祖先，P 是 R 祖先 | 均为真 | ✅ |
| `git diff --name-only base..product` | 25 路径 | 恰 25 行，全部 `A`（新增） | ✅ |
| base→product 差异规模 | — | 8801 insertions | ✅ |
| 25 候选路径工作树 vs f9 blob | — | 24/25 相等；唯一差异 `docs/reviews/T07/status.md`（工作树 `8898e1a9…` vs f9 `9a0d5668…`），为已声明的流程文件差异 | ✅ 按各自 ref 读取，不称 25 项全部物理等 f9 |
| 14 项实现/测试/fixture 身份 | 与 required-reading 声明一致 | 14/14 字节与 SHA256 全部相等 | ✅ |
| `candidate.patch` | 340601 B / SHA `3e697c94…b8a3` / 8951 行 | 三项全部一致 | ✅ |
| candidate.patch 与 `git diff --full-index --binary base..product` | 逐字节相同 | 实测相同 | ✅ |
| candidate.patch 结构 | 25 段全部新增 | 25/25 段为 `new file mode 100644` + `--- /dev/null` + `@@ -0,0 +1,N @@`；无删除/重命名/修改/二进制块/非 diff 内容；25/25 段 hunk 声明行数 = 实际 `+` 行数 | ✅ |
| 完整 candidate.patch 读到 EOF | 是 | 1–8951 行续读至实际 EOF，末字节 LF，末三行为 vitest 断言收尾 | ✅ |
| 批准 PRD（base 固定） | 93584 B / SHA `7586b2c4…fbb` | 一致；1255 行全文读到 EOF（含 FR-700–705、附录 C–G、D.1/D.2、E.1–E.5、G.4/G.6、第 10–12 节） | ✅ |
| 148 项必读清单字节身份 | 全部与声明一致 | 148 项、0 mismatch、0 missing（逐项 hashlib 复算） | ✅ |
| 归档 75 成员 | 逐项大小/SHA 相符 | MATCHED 75、MISMATCH 0、MISSING 0、EXTRA 0；其中确为 **35 个 log/PNG**（含 2 张 PNG 真实图像读取） | ✅ |
| 9 条原始内审 final | 逐行 rawLineSha256 与 sources 索引一致 | 9/9 全部匹配，payload.id 逐项对应；3 条加密中间消息仅登记元信息、未解密 | ✅ |
| 共享文件/契约/依赖 | 未被本线改动 | 25 路径中无 `packages/contracts`、无 `apps/desktop/src/main`、`preload`、`storage.py`、`job_store.py`、无 `package.json`/`package-lock.json`/`pyproject.toml`/`uv.lock` | ✅ 未改共享与依赖锁 |
| 能力注册 | 未越权注册 | `scenario` 在 contracts/main/preload/entrypoint 中仅命中 base 既有的数据范围枚举 `'asserted'|'asserted+derived'|'scenario'`；`ScenarioPage` 全库仅被 `tests/unit/t07-scenario.test.ts` 引用，无挂载点 | ✅ |
| 受保护 AGENTS | SHA `de15f6ce…c8c4`，保持未暂存 | 工作树一致，`git status` 仅 ` M AGENTS.md` 与 `?? docs/reviews/T07/round-2-input/` | ✅ 未 stage |

**读取范围声明**：本轮对 14 项实现/测试/fixture、完整 candidate.patch、完整 PRD、当前 AGENTS、前轮两份作者报告原文、两份独审、PROCESS_FAIL 裁决、7 项意见处置、native-receiving 33 项封存件、75 项归档原件、9 条原始 final、31 项历史/指南件均读到实际 EOF；`t09-e5.json`（169895 B / 4963 行）与 `round-projection-handoff.json`（13004 B / 530 行）分段续读至 EOF，未以 `json.load`/keys/hash 代替可见全文。逐项方式见台账 `items[].visibleReadMethod`。

---

## 4. 实际运行的验证（命令 / 退出码 / 首错 / 未运行项）

环境隔离：`TMPDIR`、`UV_CACHE_DIR`、`UV_PROJECT_ENVIRONMENT`（指向本角色 `.venv`）、npm cache、`RUFF_CACHE_DIR` 全部指向本角色 runtime；已清除 `ROOT_SOURCE_PATH`、`PYTHONPATH`、`ONTOLEARN_TEST_ENGINE`、`ONTOLEARN_DB_PATH`；pytest basetemp 使用本角色全新唯一子目录（`runtime/pytest/r1`、`runtime/pytest/r2`）。

| # | 命令（原入口直接执行） | 退出码 | 结果 | 原始输出 |
| --- | --- | --- | --- | --- |
| 001 | `uv run --frozen pytest packages/engine/tests/test_scenario_rounds.py --basetemp=<runtime>/pytest/r1` | **0** | **46 passed**，stderr 0 B | `001-t07-rounds.{stdout,stderr,exit}.txt` |
| 002 | `uv run --frozen pytest packages/engine/tests/test_scenario_persistence.py --basetemp=<runtime>/pytest/r2` | **0** | **44 passed**，stderr 0 B | `002-t07-persistence.{stdout,stderr,exit}.txt` |
| 003 | `npx --no-install vitest run tests/unit/t07-scenario.test.ts` | **0** | **27 passed (27)**，stderr 0 B | `003-t07-vitest.{stdout,stderr,exit}.txt` |
| 004 | `npm run check`（lint→format→3×typecheck→vitest→electron-vite build×3→ruff→pytest 全链） | **0** | eslint 0 警告、prettier 全过、3×tsc 通过、**vitest 16 files / 657 passed**、三环境构建成功、ruff 全过（216 files formatted）、**pytest 1142 passed in 49.18s**；stdout 130 行 / 5397 B，stderr **0 B** | `004-npm-check.{stdout,stderr,exit,meta}.txt` |
| 005 | `node docs/reviews/T07/evidence/render-probe.mjs`（**cwd = 本角色 runtime/scratch/probe-copy**） | **0** | stdout 0 B、stderr 0 B；产出 `ui-probe.json` + `page-wide.png` + `page-narrow.png`，三者 SHA256 与封存原件**逐字节一致**（`6e5edcec…` / `32ede79b…` / `1ee10753…`） | `005-render-probe.{stdout,stderr,exit,meta}.txt` |

**探针合规性自查（针对前轮原位违规）**：本轮**未在固定 review checkout 运行探针**。运行前先 `cd` 到 `/Users/kyle/.minimax/…/T07-minimax-review-r2-f9a1157.runtime/scratch/probe-copy` 并打印真实 `pwd -P`（输出见 `005-render-probe.meta.txt` 的 `cwd=`），再以**相对路径** `node docs/reviews/T07/evidence/render-probe.mjs` 调用**未修改的原脚本**（副本内脚本 SHA256 `259c46a3…cdc308` = 固定 checkout 同文件哈希）。运行后核验：产物只落副本（副本 `evidence/` 内三件 mtime 更新），固定 checkout `evidence/` 目录**未新增 PNG**、`ui-probe.json` 哈希仍为 `6e5edcec…`、`git status` 仍仅 ` M AGENTS.md` + `?? docs/reviews/T07/round-2-input/`；脚本自建的 `.t07-ui-*` 临时目录已自行回收无残留。

**计数归属核对（不拼数、不追认）**：`uv run --frozen pytest packages/engine/tests -q --collect-only` → 1142 collected，其中 `test_scenario_rounds.py` 46 项、`test_scenario_persistence.py` 44 项，本线专属 90 项确在其中，其余 1052 项为既有套件。001/002/003/004 是**四次独立运行**，各自单独报告，未把 46+44+27 说成"同一次独审运行"。

**本方独立反例探针（新增，用于本报告 §5 的定级）**：

| # | 目的 | 退出码 | 结果 |
| --- | --- | --- | --- |
| 006 | 同 ID 同内容重复事件的 Definition 与去重版对比 | 0 | 逐轮语义**全等**（created/completed/backlog/metrics/consumed 一致，state 与 consumed 一致），但 `digest` 不同（`11503fb2…` vs `da549aa0…`） |
| 007 | 跨重复事件定义的显式续跑 | 0 | 双向均被拒：`Snapshot belongs to another input/configuration` |
| 008 | 仅事件顺序不同的 Definition | 0 | 逐轮语义全等，`digest` 不同（`dee5060f…`），续跑被拒 |

**历史首错与空日志处置**：`ruff-first.log`（E501）、`persistence-ruff-first.log`、`persistence-pytest-readonly-fix.log`（11 failed / 32 passed，`NameError: name 'sqlite3' is not defined`）、`ui-first.log`（Playwright 浏览器缺失 revision-1248）、`ui-final.log`（`getByLabel('产能输入方式')` 超时）均已按完整原件读取并保留。`ui-identity.log`、`ui-confirmed.log`、`ui-second.log`、`ui-source-fix.log`、`ui-config-rerun.log` **均为 0 字节**，不作为成功或退出码证据；UI 结论只依据实际 `ui-probe.json` 内容 + 可复现脚本 + 本轮实跑。

**本轮未运行项（按派发边界，非遗漏）**：`npm run test:e2e`（Electron）、`npm run package:dir`、`engine:build`、dev/HMR 探针、新 native/caller/producer、真实业务模型/API、任何付费/重置、凭据读取、产品启动与产物运行。**静态与运行证据不等于打包或生产证据。**

---

## 5. 本轮新发现

### 5.1 [P2] `Definition.digest` 对语义等价输入敏感，导致显式续跑被误拒

- **位置**：`packages/engine/src/ontolearn_engine/scenario/model.py`（`Definition.digest` 属性，`Definition.events` 参与 `asdict` 后整体摘要）与 `packages/engine/src/ontolearn_engine/scenario/runner.py:2108-2111`（`_validate_resume` 首条校验 `checkpoint.definition_digest != definition.digest` → `ValueError("Snapshot belongs to another input/configuration")`）。
- **触发**：`event_catalog()` 对同 ID 同内容事件做去重（`catalog.setdefault`），因此**重复事件在语义上是幂等的**；事件集合的**顺序**也不影响 runner 的处理顺序（runner 每轮按 `(event.sequence, event.id)` 排序取事件）。但 `digest` 直接对 `asdict(self)` 求 SHA-256，把**原始 events 元组**（含重复项与顺序）纳入摘要。
- **实测（本轮 006/007/008 探针）**：同 ID 同内容重复一次 → 逐轮 `created`/`resource_completed`/`backlog`/`metrics`/`consumed` 与最终 `checkpoint.state`/`checkpoint.consumed` **完全相同**，`digest` 不同；仅把 events 逆序 → 逐轮语义**完全相同**，`digest` 同样不同；两种情形下跨定义显式续跑**双向都被拒**。
- **影响**：`Definition` 是"同一场景内容"的领域身份（FR-700/FR-703、G.4 要求按内容区分输入版本与可重放依据）。当同一场景的输入表示存在无意义的差异（事件列表里多了一条重复项，或事件在 JSON 数组中的排列顺序不同），续跑会被当作"另一个输入/配置"拒绝。真实后果是：用户从项目/场景复制或重新录入同一场景时，**看似相同的内容可能无法续跑**，且错误文案只说"另一个输入/配置"，不区分"内容等价但表示不同"与"内容真的不同"。当前实现与合成端口下不产生错误数据（拒绝是保守方向，不放行错误续跑），故不构成数据正确性 P1；但它直接影响 FR-703 的续跑可用性与 FR-700 的复制语义，属**接线前必须定义的契约精度问题**。
- **建议**：在正式场景适配契约中固定 `digest` 的规范化口径——建议对 events 做"按 `(id, round, sequence)` 排序 + 按 ID 去重（同 ID 异内容仍按现行规则拒绝）"后再摘要，并把"同 ID 异内容"与"表示差异"区分为两类错误文案；同时在 `integration-request.md` 明确 `initial_consumed`、容量、假设、来源等字段是否全部参与摘要。按现行规则，接线期任何实现/契约变更都需新候选 + 必要验证 + 双方全新完整审查。
- **为何此前未被记录**：前轮两方报告与 7 项意见均未涉及 `digest` 的规范化口径（现有 7 项为：未来事件 initial_consumed、资源选中即完成、原行 hash 方法、ignored log/png 追溯、状态/失效标签、续跑 initial phase、动作序号连续性）。

### 5.2 [P3] 摘要直接依赖 `asdict` 的字段表示

- **位置**：`model.py`（`Definition.digest` = `hashlib.sha256(canonical(asdict(self)).encode()).hexdigest()`）。
- **触发**：摘要输入是 dataclass 的字段表示形式（tuple/list 结构、字段顺序、嵌套 dataclass 展开方式），而不是一个显式声明的"参与摘要的字段清单"。
- **影响**：任何对 `Definition` 字段的增删改名或 dataclass 表示变化都会**静默改变摘要**，从而改变续跑/重放的身份判定，且不会有任何显式的"哪些字段参与摘要"的契约说明。`ScenarioIdentity`（页面侧 10 维身份）与 `Definition`（引擎侧摘要）目前是两套独立清单，存在漂移风险。
- **建议**：在接线契约中显式列出参与摘要的字段（与 `presentation.ts` 的 `sameInput` 10 维对齐），并对摘要输入做显式规范化而非依赖 `asdict`。

### 5.3 复核确认的既有工程结论（本方独立复核，非沿用）

以下为本轮在固定 head 上独立复核的结果，与前轮结论方向一致，但结论依据为本轮实跑与源码复核：

- **E.2 编排顺序**：`runner.run` 每轮严格为 事件（按 `(sequence,id)` 排序、只取 `round<=n` 且未消费）→ `apply_events` → 行为前推理 → `plan`（冻结）→ `execute` → 生成事件仅准下一轮 → `resource_stage` → 轮末推理/指标 → 构造完整 Round → `commit` → 推进 checkpoint；即使初始场景为空也强制一次 `initial` 推理。
- **推理身份校验**：`_inference` 校验 `input_state` 深相等、`rule_version`、`context` 相等与 `snapshot` 非空，错阶段/换输入被拒为 `INFERENCE_IDENTITY`。
- **动作边界**：`action_count` 必须是 `int` 且 0–1000（`type is not int` 拒绝 bool）；`trace` 数量须等于 `action_count`、三元组唯一、`event_id` 属于本轮事件、`behavior_id` 非空、`action_index >= 1`；`execute` 返回数须等于计划数。任一不满足即失败且不执行、不提交。
- **取消与失败**：各阶段间 `check()`，提交前最后一次检查，提交后不再设取消检查点（已提交轮次保持可见）；失败/取消返回最后已提交 checkpoint，未提交轮次零效果；异常统一为受限错误码（`SCENARIO_STAGE_FAILED` 等），不回传原始异常文本、路径或业务原值。
- **续跑校验**：定义摘要全等、轮次区间、消费⊆目录且无重复、定义事件须逐项相同、非 initial 消费不得早于其所属轮次、已提交轮次消费不得丢失、completed 唯一且 ⊆ 创建账本、initial_consumed ⊆ consumed；跨项目/引擎/锁/输入版本续跑全部拒绝；独立重放从 `_initial` 重新开始。
- **E.4 指标**：`metrics()` 按实际状态集合统计（积压=非完成工单数、累计完成=去重完成身份数、未闭环高危=High 且非 Closed 告警数），**未**使用 E.4 的简化递推公式（PRD 明示该公式只适用于简化测试模型）；初始已完成工单不计入累计完成。页面 `metricDefinitions` 给出三项公式与单位，未展示 P1 的平均等待时间。
- **E.5 口径**：私有 `e5.json` 的产能 3（积压 1/2/3/4、累计 3/6/9/12）与产能 4（积压恒空、累计 4/8/12/16）逐项与 PRD E.5 表格一致；批准 T09 输入副本 `t09-e5.json` 的两产能逐轮 created/completed/backlog/积压数/累计完成数一致，未闭环高危 **4/8/12/16**，且**工单完成不自动闭环告警**（工单状态与告警状态分别断言）；17 项固定文件哈希经 `t09-input-receipt.json` 逐项登记，未消费 T09 服务、未改 T09 原件。
- **FIFO**：`resource_stage` 排序键 `(created_round, sequence, id)`，与 PRD E.3「队列按创建轮次、创建序号和工单 ID 升序」一致；指标按实际状态统计，不使用简化递推公式冒充。
- **ID 不复用**：`State.created_orders` 不可变账本登记历史创建身份与单调序号，删除工单后新事件必得全新序号（删除 E2 后新建得 W003、再删得 W004）；同事件重复创建幂等、异内容拒绝、跨事件 ID 复用拒绝。
- **页面安全与受限操作**：全目录检索未出现 `dangerouslySetInnerHTML`、`innerHTML`、`eval(`、外部 URL、`require(`、`window.api`；无适配器方法或状态不允许时按钮禁用；错误统一脱敏；历史运行使用自身不可变 identity/evidence；`sameInput` 比较全部 10 个身份维度，V1 晚到不会成为 V2 当前结果；对比表缺轮显示缺失而不补造。
- **真实 Store 边界**：被测 `storage.py` 与批准 base 逐字一致（不在 25 路径 diff 内）；测试只用公开 API；`commit_round` 的事务阶段与测试 `PHASES` 对应；提交后投递失败按公开 `history()` + 完整载荷对账确认效果，不盲重放、不推断"零提交"；10 个真实子进程 `os._exit(92)` 用例断言退出码 92、stderr 为空、`terminal is None`（崩溃不冒充终态）；正式哨兵事实与 revision 全程不变；`collect_cache()` 后重开快照仍完整。
- **READONLY 假通过已封死**：断言位于 runner 错误边界之外，逐例断言 `(True, sqlite3.SQLITE_READONLY, "SQLITE_READONLY")`；禁用注入负对照使该断言必然失败。**旧 42 项 READONLY 证明维持失效，未追认**；43/44 为不同历史运行，未拼数。

---

## 6. 历史问题逐项处置（IR-01～05 与 7 项意见）

### 6.1 IR-01～05（本轮独立复核，未沿用历史结论）

| 编号 | 触发 | 本轮源码/实跑核验 | 状态 |
| --- | --- | --- | --- |
| IR-01 P2 | V1 历史运行展示 V2 当前来源/假设/产能 | `RunView.evidence` 与 `RunView.identity` 独立承载运行自身依据；`resultLabel` 仅在 `sameInput` 全部 10 维相等时才标"当前结果"，否则"历史结果 · 输入版本已变化"；TS 用例与本轮探针 `lateV1MarkedHistorical` 两侧一致 | **确认关闭** |
| IR-02 P2 | 第 1 轮快照提前消费第 2 轮事件被接受 | `_validate_resume` 拒绝非 initial 的未来消费、拒绝丢失已提交消费；正反例在本轮 46 项内实跑通过 | **确认关闭** |
| IR-03 P2 | 删除最高序号工单后复用历史 ID | 账本 + 单调序号不复用；`test_deleted_order_id_and_event_identity_are_never_reused` 实跑通过 | **确认关闭** |
| IR-04 P2 | 已有场景后无法从基准项目创建 | 显式来源选择，项目来源不传 scenarioId；TS 用例 + 本轮探针第三次调用 source 为 `undefined` | **确认关闭** |
| IR-05 P2 | READONLY 未触发时 Assertion 被 runner 吞掉产生假通过 | runner 外逐例强断言 + 禁用注入负对照必然失败；本轮 44 项持久化实跑通过；旧 42 项证明未追认 | **确认关闭** |

### 6.2 7 项既有意见（登记，不称其他 owner 已接收）

`responsibilityAcknowledgedByOtherOwner` 全部为 `false`；`implementationChangeMade: false`。本轮逐项复核其依据是否仍成立，并给出本方处置意见：

| id | 意见要点 | 既有依据 | 本轮复核 | 本方处置意见 |
| --- | --- | --- | --- | --- |
| Z-P3-1 | 未来事件可在 `initial_consumed` 显式声明 | `model.py` 的 `initial_consumed` 只校验唯一性与目录包含；`runner` 的未来消费检查显式排除 initial 集合 | 成立：`initial_consumed` 属操作者声明，且进入 `digest`，不会静默污染他人运行 | 维持登记延期；**建议与本轮 §5.1 合并处置**（两者同属"Definition 身份与消费语义口径"，在同一次契约评审中固定） |
| Z-P3-2 | 资源阶段"选中即完成" | `resource_stage` 将队列前 N 个工单直接置 completed；PRD E.3 允许该最小语义 | 成立；PRD E.3 明确"达到完成条件的工单标记为已完成"，本线为最小私有语义 | 维持登记延期；真实完成条件仍归 T06 |
| Z-P3-3 | 封存原行 hash 可复算性 | 旧独立 audit 用 `splitlines(keepends=True)` 逐行 SHA，双方 9/9 匹配 | 本轮独立复算：9 条原始 final 逐行 `rawLineSha256` 与 `internal-review-sources.json` **9/9 全部匹配**；未跟随 `sourceSession` | 静态方法更正**在本轮复现成立**；仍不等于官方读取或工程通过 |
| Z-P3-4 | ignored log/png 可追溯性 | `.gitignore` 忽略 `evidence/*.log`、`evidence/*.png` | 本轮实测：固定 checkout `evidence/` 目录**确实没有 PNG**（`ls *.png` 失败），35 个原件由 `frozen-inputs` 封存件按哈希可追 | 维持封存完成；但**本轮过程类 P2 另列**，不因封存完成而抵消 |
| M-F01 | 结果状态/失效原因标签精度 | `presentation.ts` 的 `resultLabel` 把"已过期"与"历史"合并，且 `sameInput` 失败时恒称"输入版本已变化"，而实际比较的是 10 维（含规则/行为/引擎/依赖锁/语义） | 成立；本轮 `grep` 复核确认无 `dangerouslySetInnerHTML` 等注入面，但标签语义精度问题仍在 | 维持登记延期；**建议与本轮 §5.2 合并处置**（同属"身份维度清单"契约） |
| M-F02 | 续跑 `phase="initial"` 语义未定义 | `runner` 续跑时仍以 `phase="initial"`、`round=N` 发起推理，随后从 N+1 继续；`integration-request.md` 未定义该阶段含义 | 成立；对合成端口无影响（续跑与完整运行 checkpoint 相等），但真实 T05 适配器若按"初始场景"语义理解会在中途状态上产出非预期快照 | 维持登记延期；建议在接线契约中写死"当前 checkpoint 轮次边界上的前置快照"或新增 `phase="resume"`，并声明续跑的阶段序列与推理调用次数 |
| M-F03 | 同一触发实例动作序号连续性 | 唯一性校验施加于完整三元组，故同实例可出现 actionIndex 1 与 3（跳过 2）而不被拒 | 成立；runner 只校验身份/归属/唯一，不校验实例内 1..k 连续 | 维持登记延期；建议在 T06 接线时明确"连续性由行为执行器保证，runner 只校验身份/归属/唯一"，或由 runner 追加 1..k 校验（不未经批准新增契约） |

**说明**：上表 7 项均为作者 P3/观察，**不是**前轮过程 P2；本报告不因本轮通过而追认其已关闭，也不虚称其他 owner 已接收承诺。

---

## 7. 前轮过程失败的事实（原文保留，不被本轮抵消）

前轮 owner 裁决原文：**「本轮记 PROCESS_FAIL，不放行指定完整双审门」**。本轮已逐条独立核实其事实基础（读取 `launch-20261023/native-receiving-20261023/` 全部 33 项封存件，含两方 `tool-calls.jsonl` / `tool-results.jsonl`）：

1. **Z 侧：被拒后包装执行且报告遗漏首错。** 原生 `call_336cc6c0c5b34af8b0d1ad09`（第 56 调用）结果 `isError:true`，Mimosa 拒绝理由为「Bash 直接写源码/安全配置会绕过 Write/Edit 安全扫描」；下一调用 `call_bcea7d98973c4a879eb401c3` 用 Write 落盘 `run-t07-pytest.sh`（含同目的 pytest/vitest 命令），再由 `call_a6aa655e833646e9849ac25e` 用 Bash 执行该 wrapper 并取得 `PYTEST_EXIT=0`；另有更早的内联 Python `NameError: name 'MATCH' is not defined`（第 10 调用）。而前轮 Z 报告「首错」栏写「无」、最终回复写「均 exit 0、无首错」。
2. **M 侧：在固定 review checkout 原位运行 render-probe。** `call_01a164ffa8ce72f89d3c3668`（messages sourceLine 87）先 `cd` 到固定 review 树、构建副本 C，却以**绝对脚本路径**调用副本脚本而**从未 `cd "$C"`**；脚本第 8 行 `const root = process.cwd()` 使输出写入固定树（结果证据：固定树 `evidence/` 三件 mtime 变为 03:04:03）。虽随后有合规 scratch 重跑（`PROBE_EXIT=0`），但 owner 裁决明确：**不能因同 SHA 或后继真 scratch 重跑消除违规**。前轮 M 报告已自认该偏差。
3. **M 侧：向父项目派发 find 枚举。** `call_01a164fb56917084b7633386` 执行 `find /Users/kyle/Documents/工作/知爻/本体 -name "owner-ui-pre-submit-retry*" …`，超出"只读自身 root 与本角色 runtime"的边界；其最终输出在封存材料中不存在，本轮**未追读、未据此推断命中路径**。
4. **两方阅读缺项。** 独立原生补审确认：Z 侧 14 项实现/测试/fixture 中 12 项完整内容覆盖，缺 `t09-e5.json` 与 `round-projection-handoff.json` 全文；M 侧 10/14，另缺 `scenario.css`、`__init__.py`；两方 PRD 均只按区间读取而非 1255 行全文；历史原日志以 head/tail/grep 查看而非全文。
5. **过程 P2 与工程结论分离。** 上述均为过程事实，不等于产品代码失败；前轮两份作者报告的「限 S1 通过」原文保留，不被本报告改写，也不被本报告借用为结论依据。

**本轮自身的对应事实**：本轮读取范围已覆盖上述所有缺项（14/14 全文、完整 candidate.patch 8951 行、PRD 1255 行全文、35 个 log/PNG 原件、9 条原始 final）；探针在 scratch 副本内以真实 `pwd` + 相对路径运行，固定 checkout 未被改写；未发生任何自动审批/安全扫描拒绝（本轮拒绝数为 0，见台账 `automaticApprovalRejections: []`）；未使用管道 tail 取代目标退出码；未向父目录 find/枚举，未读取 R2 另一方材料。

---

## 8. 未验边界（全部保留，不因本报告关闭）

真实 T05 初始/事件后/轮末推理；真实 T06 冻结条件/稳定排序/冲突检测/动作语义与动作间取消；T01/I04 正式 scenario 任务注册、project/run/job 身份、原子 Round+progress、取消/最后提交/终态竞态、operation-id/expectedRound 与响应丢失/崩溃**正式**对账 API、正式数据隔离；FR-705 用户真实删除运行/恢复基准/真实快照创建与续跑；公共契约/bridge/App 挂载与真实数据接线；完整 E.5 `facts`/`inferred`/`actionTrace`/`triggeredInstances` 与真实 RDF 执行；G.6 完整迁移；T10 跨设备重放；FR-700–705 与 E.2–E.5/G.4/G.6 父级跨模块验收；Windows/macOS 完整产品/平台/发布门；真人验收；push/PR、实际 CI、远端 develop 核验、正常合并与发布。

另：`test.rounds` 只接受 toy 载荷，传完整业务 Round 会得 `IDENTITY_CONFLICT`——本线**未**以该能力冒充正式沙盘。

---

## 9. 后续门（本报告不关闭）

1. **本报告与 ZCode 同版本结论都实际完成、双方全部意见有处置后**，方可 push/PR；实际 CI 通过后正常合并 develop 并核验远端与保护源。
2. **§5.1 的 P2 须在正式场景适配契约中定案**（digest 规范化口径与续跑可用性）。若因此修改实现/测试/契约/验收/配置/依赖/base，须生成新候选、必要验证，并由双方各做**全新完整审查**；本报告不适用于变更后的候选。
3. §5.2 与既有 M-F01、Z-P3-1 建议在同一次契约评审中合并处置，避免多轮小改。
4. 前轮 PROCESS_FAIL 的四项过程事实仍需 owner/root 的独立处置记录；本报告只提供事实核实，不自行豁免，也不因本轮换新树而自动关闭。
5. 全部 57 项 P0、附录 C–G 与第 10–12 节、完整父 Goal、双 OS、真人、CI、远端与发布门保持未关闭。

---

## 10. 最终结论

在「完整私有轮次编排 / 资源 FIFO 指标 / 独立场景页及现有验证」这一 S1 范围内：受审身份链（base→product→reviewHead、25 路径、14 项、完整 8951 行 candidate.patch、批准 PRD 全文、75 项归档原件、9 条原始终态、31 项历史与指南）逐项核实且字节全部吻合；实现与测试经本轮完整源码级独立复核与四次独立运行（46 Py / 44 Py / 27 TS / check 657 TS + 1142 Py，全部 exit 0、stderr 空）、外加合规 scratch 副本内的 render-probe 复跑（exit 0、产物与封存原件逐字节一致、固定 checkout 未被改写），未发现新的 P1；IR-01～05 确认关闭；新增 1 项 P2（digest 对语义等价输入敏感导致续跑误拒）与 1 项 P3（摘要依赖 `asdict` 表示），两者均要求在接线契约中定案；文档对自身边界的表述与代码事实一致——无私有能力冒充产品能力、无越权注册、无父验收冒领、无证据造假。

**判定：通过（限上述 S1 私有范围）；新增 1 项 P2 与 1 项 P3 待接线期处置；7 项既有意见维持登记（未被其他 owner 接收）；前轮 PROCESS_FAIL 四项过程事实保留；父领域、完整 E.5、跨设备、双 OS、真人、CI、远端与发布门全部未验且未关闭。**

**任务级实际设置已由 operator 收据读回**：M3.1-Flash / xhigh / 始终授权，session `mvs_58e4985c72594853ac34354567ea2468`；task ID、original turn 与官方 terminal 官方未给出，按 UNKNOWN 如实保留，未据此预填任何通过。
