# T07-S1 指定双审 · MiniMax Code (M3.1-Flash) 完整工程独立审查报告

- 阶段：T07-S1（完整私有轮次编排 / 资源FIFO指标 / 独立场景页及现有验证）
- 报告文件：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-f9a1157/docs/reviews/T07/round-1/minimax-m31flash.md`
- 审查日期：2026-10-23（北京时间）
- 审查者角色：MiniMax Code 独立只读审查者（指定模型任务）

---

## 1. 结论（先行）

**结论：通过（限 T07-S1 本候选范围）。**

依据：25 路径完整 diff、14 项实现/测试/fixture 全部源码通读、PRD FR-700–705 与附录 D/E.1–E.5/G.4/G.6/第10–12节逐条比对、历史 IR-01～05 逐项核验、本方独立实跑（`npm run check` 退出 0 = 657 TS + 1142 Py；T07 专属 46+44 Py + 27 TS；合成 headless 页面探针退出 0 且复现字节一致），以及归档原件 75/75 成员与 9/9 原始终态的逐字节校验。

**本轮新发现 3 项 P3（均为接口契约/表述精度，不构成阻断）：** F-01 结果状态标签与附录 D.1/D.2 的"已过期"语义未分离；F-02 续跑时 `phase="initial"` 推理语义未在接线提案中定义；F-03 逐动作轨迹对同一触发实例的序号连续性未约束。三项均需在 T05/T06/T00 正式接线前由对应 owner 固定，本报告不要求改动已冻结候选。

**必须同时声明的限制（不得被读成产品通过）：**

1. 本次通过的是**私有服务 + 私有页面 + 合成编排探针**这一完整 S1 子集。`ProbePorts.infer` 返回合成标记、`execute` 只模拟"一事件一工单"、`commit` 只捕获不可变值，**三项指标由合成状态统计得出，合成三指标不等于产品通过**。
2. **父领域未验**：真实 T05 推理（初始/事件后/轮末）、真实 T06 冻结条件/排序/冲突/动作、真实 E.5 的 `facts`/`inferred`/`actionTrace`/`triggeredInstances`、T01/I04 正式 scenario 任务生命周期与取消/原子进度/终态/operation-id 响应丢失对账、公共契约/bridge/App 挂载、真实删除/恢复/快照创建/续跑、T10 跨设备重放、FR-700～705 与 E.2–E.5/G.4/G.6 父验收、Windows/macOS 完整产品与发布门，**全部未验且未关闭**。
3. 本报告不替代 ZCode GLM-5.3/最高一方结论，不关闭完整父 Goal、CI、远端核验与发布门。

---

## 2. 任务身份、实际设置读回与缺失项

| 项目 | 实际值 | 来源 |
| --- | --- | --- |
| 应用 | MiniMax Code | 本任务运行环境 |
| 实际模型 | **M3.1-Flash** | operator 收据 `actualSettingsUI.model`（本任务新任务 UI 读回）；本会话运行环境标识 `MiniMax-M3.1-Flash` 一致 |
| 实际思考等级 | **xhigh** | 同上 `actualSettingsUI.thinking` |
| 实际权限模式 | **始终授权（Full access / bypassPermissions）** | 同上 `actualSettingsUI.permission` |
| 设置读回范围 | 自建空新任务 + 自选文件夹，非沿用既有活动任务 | 收据 `settingsScope` |
| 实际 native session ID | **`mvs_bfa6c40659f6405391d5de2bbb8cbc0f`** | operator 经官方本任务 Session 菜单 "Copy session ID" → 粘贴到本任务草稿 → AX 读值取得（`.runtime/metadata/owner-ui-accepted-retry-20261023.json`）；**与本会话运行标识完全一致**，可据此把本报告绑定到该实际任务 |
| 实际 task ID | **UNKNOWN** | 收据 `actualTaskId: null`，官方未单独给出 task ID |
| 实际 turn ID | **UNKNOWN** | 收据 `officialTurnId: null` |
| 正文受理时间 | 2026-10-23 03:00:35（+08:00，官方提交并受理附件 `full-input.txt` TXT 139.7 KB） | `owner-ui-accepted-retry-20261023.json`（`shortLaunchSubmitted: true`、`UIAccepted: true`） |
| 本任务首个用户回合（附件到达） | 2026-10-23 02:59（+08:00） | 本会话 |
| 任务设置读回收据时间 | 2026-10-22T18:58:51.606039+00:00 = 2026-10-23 02:58:51（+08:00） | `.runtime/metadata/owner-ui-pre-submit-retry-20261023.json` |
| 官方原生读链核验 | `fullNativeReadChainVerified: false`（官方未从原生存储回读提交正文；正文身份以本方收到的附件 SHA256 核验为准） | 同上 |
| 独立性声明 | `globalConfigRead: false`、`peerOpinionsUsed: false` | 同上 |

**缺项按"未知"照实记录，不以用户默认、界面模型名或进程 ready 代替读回。** 收据路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T07-minimax-review-f9a1157.runtime/metadata/owner-ui-pre-submit-retry-20261023.json`（任务级设置读回，提交前）与 `owner-ui-accepted-retry-20261023.json`（官方提交受理与 native session ID）。task ID 与 turn ID 未由官方给出，按 UNKNOWN 记录；本任务未扫描 globalconfig、peer、本轮其他意见或全 session 自恢复身份。

完全访问仅是执行能力，不改变只读职责：本次未修改实现/测试/fixture/验收/依赖锁/配置，未 commit / push / 切分支，未读取凭据，未新增付费。

---

## 3. 输入受理与范围核验（本方实际执行）

| 核验项 | 期望 | 实测 | 结论 |
| --- | --- | --- | --- |
| 官方附件字节/行数 | 143054 B / 896 行 | 143054 B / 896 行 | ✅ |
| 官方附件 SHA256 | `153dc55dbae5e3b27b8ae65e0a74f14e1da01c36398cffa477691269f7e325dd` | 完全一致 | ✅ |
| 本方 `docs/reviews/T07/dispatch-20261022/full-input.txt` | 与官方附件全文一致 | `diff` 无差异，SHA256/字节数相同 | ✅ 逐字节一致 |
| 输入前缀 SHA256（94374 B） | `914a1c98…93d88` | 一致 | ✅ |
| 输入后缀 == 原 `minimax-frozen-prompt.md` 原字节 | byte-exact | True（原文件 SHA256 `650c9f85…4cb1d` 亦一致） | ✅ |
| cwd | `/Users/kyle/…/.worktrees/T07-minimax-review-f9a1157` | 一致 | ✅ |
| reviewHead | `24f3703ecf4fce75e0d0375f7291ed928f083c41` | 一致（detached） | ✅ |
| base → product 祖先关系 | base 是 product 祖先，product 是 reviewHead 祖先 | 均为真 | ✅ |
| base→product diff 路径数 | 25 | 25（全为 A 新增） | ✅ |
| 14 项实现/测试/fixture 在 product head 的 blob SHA256 | 全部匹配 manifest | 14/14 匹配 | ✅ |
| `candidate.patch` | 340601 B，SHA256 `3e697c94…b8a3` | 一致 | ✅ |
| `frozen-inputs.tar.gz` | 946863 B，SHA256 `880d4cc9…48e6`，75 成员 | 一致 | ✅ |
| 归档 75 成员逐项字节/SHA256 | 全匹配，无多余/缺失 | 75/75 匹配，extra 0、missing 0 | ✅ |
| 9 条原始内审终态 | 文件 SHA256 + 逐行 rawLineSha256 | `51f5746a…4361` 一致；9/9 行哈希与 messageId 全部匹配 | ✅ |
| 3 条加密中间消息 | 仅登记元信息、未解密 | `internal-review-sources.json` 仅列 messageId/行号/时间/availability | ✅ 未解密 |
| 15 份本地原始日志 hash（validation + persistence-validation 声明） | 全匹配 | 9/9 + 6/6 匹配 | ✅ |
| 共享文件未被本线改动 | storage/job_store/coordinator/worker/protocol/contracts/main/preload/pyproject/uv.lock/package.json 在 base→product→reviewHead 三点一致 | 全部 UNCHANGED | ✅ |
| storage.py / job_store.py 与批准 base 字节 | `4abf1082…842` / `42cd05b9…4f2` | 一致 | ✅ 未采用未批准 owner 代码 |
| 受保护 AGENTS | SHA256 `de15f6ce…c8c4`，保持 M 未 stage | 工作树 `de15f6ce…c8c4`，`git status` 仅 ` M AGENTS.md` | ✅ |
| `full-git-files.json` | 832 tracked / 831 exact / 唯一例外=受保护 AGENTS | 一致 | ✅ |
| 8 份 current-inputs 文件 hash | 全匹配 | 8/8 匹配 | ✅ |

**归档与原始终态的处置**：压缩包只提取到本角色独占 `.runtime/scratch/frozen`，未覆盖固定 review 路径；9 条原始终态只读本树封存副本，未跟随 `sourceSession` 链接到正在增长的原会话；未枚举其他 worktree/refs/controller 队列/peer 报告/另一模型本轮意见。

---

## 4. 完整读取范围（本方实际通读源码，非摘要）

**25 路径**：全部读取。其中 14 项实现/测试/fixture 逐字通读源码：

- `packages/engine/src/ontolearn_engine/scenario/{__init__.py, model.py, runner.py}`
- `packages/engine/tests/test_scenario_rounds.py`、`test_scenario_persistence.py`
- `apps/desktop/src/renderer/src/scenario/{ScenarioPage.tsx, presentation.ts, scenario.css}`
- `tests/unit/t07-scenario.test.ts`
- `tests/fixtures/scenario/{e5.json, round-projection-handoff.json, t09-e5.json, t09-manifest.json}`
- `docs/reviews/T07/evidence/render-probe.mjs`

其余 11 项（`docs/iterations/T07/{acceptance,integration-request,round-projection-handoff}.md`、`docs/reviews/T07/{.gitignore,internal-review.md,status.md}`、`docs/reviews/T07/evidence/{candidate-files,persistence-validation,t09-input-receipt,ui-probe,validation}.json`）全文读取。

**规范**：`docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6 —— FR-700～705（477–501 行）、附录 D.1/D.2（983–1015）、附录 E.1–E.5（1016 起，含 E.2 固定轮次状态机、E.3 工单语义、E.4 指标公式、E.5 固定验收模型）、附录 G.4/G.6、第 10 章非功能需求、11 章指标、12 章 MVP 端到端验收，全部逐条读取比对。

**过程材料**：`round-1/README.md`、`frozen-manifest.json`、`archive-manifest.json`、`historical-issues.md`、`internal-review-sources.json`、`internal-review-original-finals.jsonl`（9 条）、`internal-review.md`（开发者摘要，识别为非原始报告）、`dispatch-20261022/input-manifest.json` 及 8 份 current-inputs。

**历史原件**：`frozen-inputs.tar.gz` 内 `local-originals/` 全部 32 个原始 log/PNG 原件（含首错与空日志）。

---

## 5. 实际运行的验证（命令 / 退出码 / 首错 / 未运行项）

环境隔离按派发指定：`TMPDIR`、`UV_CACHE_DIR`、`UV_PROJECT_ENVIRONMENT`、npm cache、`RUFF_CACHE_DIR` 全部指向本角色 `.runtime` 路径；已清除 `ROOT_SOURCE_PATH`、`PYTHONPATH`、`ONTOLEARN_TEST_ENGINE`、`ONTOLEARN_DB_PATH`；pytest basetemp 使用本角色全新唯一子目录。

| 命令 | 结果 | 退出码 |
| --- | --- | --- |
| `uv run --frozen pytest packages/engine/tests/test_scenario_rounds.py` | **46 passed in 0.12s** | 0 |
| `uv run --frozen pytest packages/engine/tests/test_scenario_persistence.py` | **44 passed in 2.30s** | 0 |
| `npx --no-install vitest run tests/unit/t07-scenario.test.ts` | **27 passed (27)** | 0 |
| `npx --no-install vitest run`（全量） | **16 files / 657 passed** | 0 |
| `npm run check`（lint→format→typecheck→vitest→electron-vite build→ruff→pytest 全链） | **1142 passed in 48.91s**，全段通过 | 0 |
| `node docs/reviews/T07/evidence/render-probe.mjs`（独占 scratch 副本，cwd=副本根） | 退出 0；产出 `ui-probe.json` + 2 PNG，**与封存原件逐字节一致** | 0 |

**独立复现的关键点**：`npm run check` 在本树独立跑出 657 TS / 1142 Py，与 `check-persistence-confirmed.log` 声明一致；本方未把 46+44+27 拼成"同一次独审运行"，三类证据分别报告。

**本方未运行项（按派发边界，非遗漏）**：`npm run test:e2e`（Electron）、`engine:build`、`package:dir`、HMR 探针、dev 模式、新 native/caller/producer、真实业务模型/API、任何付费/重置、凭据读取、产品启动与产物运行。静态/运行证据不等于打包或生产证据。

**首错与空日志处置**：历史首错原件全部保留未改——`ruff-first.log`（E501 line-too-long）、`persistence-ruff-first.log`、`persistence-pytest-readonly-fix.log`（11 failed / 32 passed，`NameError: name 'sqlite3' is not defined`）、`ui-first.log`（Playwright 浏览器缺失）、`ui-final.log`（`getByLabel('产能输入方式')` 超时 → 改显式 `aria-label` 后通过）。`ui-identity.log`、`ui-confirmed.log`、`ui-second.log`、`ui-source-fix.log`、`ui-config-rerun.log` **均为 0 字节**，不作为成功/退出码证据；UI 成功结论只依据 `ui-probe.json` 实际内容 + 可复现脚本 + 本方实跑。

---

## 6. 逐条审查结论

### 6.1 FR-700 场景创建
- `Definition`（`model.py:177-228`）持有 projectId/projectVersion、engineVersion、dependencyLockHash、scenarioId/inputVersion、ruleVersion、behaviorVersion、`max_rounds`、`semantics`、events、rules/behaviors/parameters、source、assumptions；`digest` 由 `asdict`+`canonical` 生成。
- `copy_scenario`（`model.py:240-243`）显式换 scenarioId 与 inputVersion → 摘要改变，源不被修改；`test_copy_is_explicit_and_does_not_change_source` 覆盖。
- 页面 `ScenarioPage.tsx:34/41/96-97/104/190` 提供"基准项目 / 选中场景"显式来源选择；选择基准项目时 `copySource === undefined`，`actions.create(draft, undefined)`。**IR-04 在源码与实跑探针两侧均已闭合**（探针 `calls[2][2] === undefined`）。
- 保留未验：真实项目/已有场景快照创建、T05 初始推理与规则支持校验。

### 6.2 FR-701 / E.2 固定轮次状态机
- `runner.py:218-326` 顺序与 E.2 六阶段**逐项一致**：事件输入 → 行为前推理 → 冻结计划/冲突检查 → 行为执行 → 资源处理 → 轮末推理/指标/提交。
- `Context(round, phase)` 显式贯穿 `initial/events/before/behavior/end`；`_inference`（`runner.py:134-144`）校验输入状态、规则版本、阶段上下文与非空快照，错阶段即 `INFERENCE_IDENTITY`。
- 上限：最大轮数 1–1000（`model.py:200-202`）、每轮动作 0–1000（`runner.py:253-254` → `ACTION_LIMIT`）。
- 轨迹：`runner.py:256-265` 拒绝数量不符、重复三元组、事件不属于本轮、behaviorId 为空、序号 < 1；冻结计划 JSON 随轮保存（`Round.frozen_plan`）。
- 失败/取消保留上轮：`run()` 在 commit 之前异常不回写 checkpoint，`test_failure_retains_previous_round_and_redacts_exception` 覆盖 5 个阶段，错误码统一为受限码（`SCENARIO_STAGE_FAILED` 等），不回传原始异常文本（探针以 `restore` 抛错验证页面只显示通用提示）。
- 新事件只进下一轮：`runner.py:271-273` 校验 `event.round == number + 1`，否则 `GENERATED_EVENT_ROUND`。
- 保留未验：真实 T06 冻结条件/稳定排序/冲突/动作语义；T05 真实推理；T01/I04 逐轮事务、取消竞态与错误；动作间取消与超时/硬终止（派发文件已声明由正式适配器承担）。

### 6.3 FR-702 / E.4 指标
- `metrics()`（`model.py:169-174`）按**实际状态集合**统计：积压 = 提交时非"已完成"工单数；累计完成 = `len(set(checkpoint.completed))`；未闭环高危 = High 且非 Closed 的告警数。**未使用 E.4 的简化递推公式**，符合 E.4 "不替代完整状态统计"。
- 初始已完成的工单不计入累计完成（`runner.py:283-295` 仅累计"本次变为已完成"者），`test_metrics_count_actual_state_not_recurrence_and_exclude_initial_completed` 覆盖。
- 页面 `metricDefinitions`（`presentation.ts:116-120`）给出三项公式与单位；**未展示平均等待时间等 P1 指标**，符合 FR-702 "未定义前不得展示"。
- 对比：`compareRuns`（`presentation.ts:179-188`）缺轮显示 `null` → 页面渲染"无该轮记录"，不补造缺失轮次；仅 `succeeded` 运行可进入对比。
- 保留未验：两个**真实**场景运行结果、真实告警数据口径。

### 6.4 FR-703 / G.4 后 2 条
- 输入身份隔离：`sameInput`（`presentation.ts:122-135`）比对全部 10 个身份维度（TS 测试逐字段参数化）；`Definition.digest` 覆盖全部版本与内容；跨 project/engine/lock 变化拒绝续跑（`test_resume_and_replay_isolate_project_and_implementation_identity`）。
- 消费重置 / 显式续跑：`_validate_resume`（`runner.py:158-190`）校验定义摘要、轮次范围、事件目录逐项一致、**拒绝提前消费未来事件**、**拒绝丢失已提交事件消费**、拒绝重复完成身份、拒绝未知完成工单、拒绝丢失初始消费；正反例齐备。
- 历史依据：IR-01 已闭合——`RunView.evidence`（`presentation.ts:39-45`）与 `RunView.identity` 独立携带运行自身来源/假设/参数/容量/轮数，`RunDetails`（`ScenarioPage.tsx:453-462`）渲染 `run.evidence.*` 而非当前场景值；V1 晚到与 V2 按完整身份区分。
- 保留未验：完整持久运行依据、重放包/执行语义校验、T10 跨设备重放。

### 6.5 FR-704 假设提示 / 附录 D
- 页面展示主要假设、数据来源、三项指标定义、未处理事件状态（`ScenarioPage.tsx:453-462, 465-470, 411-418`），全部以 React 文本节点渲染，**无 `dangerouslySetInnerHTML`、无外部资源引用**。
- 保留未验：实际业务记录进入页面、Agent 只按真实依据解释（T08）。

### 6.6 FR-705 / G.6 沙盘隔离、取消与恢复
- **不污染正式项目**：`test_scenario_persistence.py` 用真实 SQLite 写入 runner 实际生成的完整 Round，并断言 `store.state("project-1") == formal` 且 `revision` 不变（真实哨兵事实 `urn:t07:formal-equipment` 始终保持）；`store.collect_cache()` 后重开快照仍完整（缓存回收不触及已提交轮次）。
- **取消**：`cancel` 故障在 5 个事务阶段 × 前轮 0/1 组合下验证"当前未提交轮次不生效、前轮保留、已提交轮次保留在已取消运行中"。
- **提交响应丢失对账**：`PersistentProbe.commit` 在 `after_commit` 抛异常后，按 `operation` + `number` + `job` 从公开 `history()` 读回并逐字段比对 payload，仅在**确认恰好一条匹配记录且快照一致**时才视为已提交；不盲重放、不推断"零提交"、不重复执行动作。
- **真实崩溃**：10 个真实子进程 `os._exit(92)` 用例（2 前轮 × 5 阶段），断言退出码 92、stderr 为空、重开后只恢复已提交轮次、`terminal is None`（崩溃不冒充终态成功/取消）、正式数据与 revision 不变。
- **真实 READONLY**：见 6.8 IR-05。
- 保留未验：用户删除运行、恢复基准、真实快照续跑（FR-705 明确需 T01 生命周期 API，本线**未绕过**现有不可变 SQL 触发器）；完整 G.6 迁移/跨设备条目。

### 6.7 E.5 固定验收模型（逐项核对）
- 私有 fixture `e5.json`（SHA256 `84c299fa…53b`）：产能 3 四轮创建/完成/积压 = E.5 表 **逐项一致**（积压 1/2/3/4，累计 3/6/9/12）；产能 4 逐轮完成 W001–W004 / W005–W008 / W009–W012 / W013–W016、积压均空、累计 4/8/12/16 —— **一致**。
- 批准 T09 固定提交 `873c8c0…c380` 输入副本 `t09-e5.json`（SHA256 `e81b0d02…a5e5`，与 manifest 中 `tests/fixtures/product-baselines/E.5.json` 哈希相同）：两产能逐轮 created/completed/backlog/积压数/累计完成数 **全部逐项一致**；**未闭环高危 = 4/8/12/16**，且**工单完成不自动闭环告警**（工单状态与告警状态分别断言）—— 与公共 E.5 口径一致。
- manifest 17 项固定文件哈希经 `t09-input-receipt.json` 逐项登记为 matched；本线仅保存 manifest 与 E.5 原字节副本，**未消费 T09 服务或 Store helper、未改 T09 原件**。
- 私有 `e5.json` 的 0 值高危来自另一个**无告警**合成探针，文档已明确区分，未冒充公共 E.5。
- 保留未验：`facts`/`inferred`/`actionTrace`/`triggeredInstances` 的真实领域结果。

### 6.8 历史 IR-01～05 逐项核验（本方独立复核，不沿用历史结论）

| 编号 | 触发 | 当前源码核验 | 状态 |
| --- | --- | --- | --- |
| IR-01 P2 | V1 历史运行展示 V2 当前来源/假设/产能 | `RunView.evidence` 独立承载运行自身依据；`RunDetails` 渲染 `run.evidence.*`；`sameInput` 10 维身份比对 → V1 晚到不成为 V2 当前结果 | **确认关闭**（未重开） |
| IR-02 P2 | 第 1 轮快照提前消费第 2 轮事件被接受 | `runner.py:171-176` 对非 `initial_consumed` 的已消费事件校验所属轮次 ≤ checkpoint.round，否则 "Snapshot consumed a future event"；`runner.py:177-181` 反向校验已提交消费未丢失；正反例 `test_resume_rejects_future_consumption_and_lost_committed_consumption` | **确认关闭** |
| IR-03 P2 | 删除最高序号工单后复用历史 ID | `State.created_orders` 历史创建身份登记 + `order_sequence` 单调不回收（`model.py:97-130`）；`create_order` 事件级幂等且身份不复用（`model.py:133-143`）；反例断言删除 E2 后新建得 **W003**、再删得 **W004** | **确认关闭** |
| IR-04 P2 | 已有场景后无法从基准项目创建 | 显式来源选择；项目来源传 `undefined`；TS + headless 实跑双向验证 | **确认关闭** |
| IR-05 P2 | READONLY 未触发时 AssertionError 被 runner 吞掉，产生假通过 | READONLY 断言**位于 runner 错误边界之外**（`test_scenario_persistence.py:239-241`），逐例断言 `(True, sqlite3.SQLITE_READONLY, "SQLITE_READONLY")`；注入失效时 `disk_errors == [(False, None, None)]` → 断言失败；另有**禁用注入负对照**（`:244-267`）证明统一失败状态不能冒充 READONLY 证据 | **确认关闭**，且早期 42 项 READONLY 证明**未被追认** |

IR-05 的修复路径经原始首错 `persistence-pytest-readonly-fix.log`（11 failed，`NameError: sqlite3`）→ 修复 → 43 项 → 44 项交接样例的独立历史链，**三次为不同运行，未拼成同一次验证**。

---

## 7. 本轮新发现（P3，非阻断）

### F-01 [P3] 结果状态标签未按附录 D.1/D.2 区分"已过期"，且把当前失败/取消运行标为"历史运行"

- **位置**：`apps/desktop/src/renderer/src/scenario/presentation.ts:137-148`（`resultLabel`）；`ScenarioPage.tsx:441`（最新运行的标题）、`ScenarioPage.tsx:328-341`（历史运行折叠区）。
- **触发**：① `statuses` 对 `cancelled`/`failed` 一律返回 `已取消 · 历史运行` / `失败 · 历史运行`；而最新运行在页面中渲染于"历史运行（N）"折叠区**之外**（`ScenarioPage.tsx:317-327`），标题却写着"历史运行"。② `sameInput` 失败时统一返回 `历史结果 · 输入版本已变化`，但 `sameInput` 比较的是 **10 个维度**（projectVersion、ruleVersion、behaviorVersion、engineVersion、dependencyLockHash、semantics…），标签文字却恒定声明"输入版本已变化"。
- **影响**：附录 D.1 定义四态（当前/已过期/历史/失败·已取消），D.1 对"已过期"要求"必须显示原因和重跑入口"，D.2 要求"行为定义…变化 → 原运行保留为历史"并区分失效来源。当前实现把"已过期"与"历史"合并为同一标签，且该标签在**规则版本/行为版本/引擎版本/依赖锁**任一变化时都断言"输入版本已变化"——文字与事实不符；用户刚启动并失败的运行也被标为"历史运行"。不影响任何架构不变量、不影响 FR-700～705 可独立验证范围，也不产生"已通过产品能力"的虚假声明（页面明确为私有视图）。正式失效来源 `staleReason`（`invalidation-v2.json`）属正式适配器责任，故不判为 P2。
- **证据**：本方实跑 `tests/unit/t07-scenario.test.ts` 断言 `resultLabel({...run, status:'failed'}, identity) === '失败 · 历史运行'` 与 `'已取消 · 历史运行'`（该行为已被固化，见 `t07-scenario.test.ts:61-65`）。
- **建议**：由 T00 契约 owner 随公共接线一次性确定：① 拆出独立 `已过期` 状态并按 `sameInput` 的**具体差异维度**给出原因文案（至少区分输入/规则/行为/引擎/锁/项目版本）；② 为"已过期"运行提供"用当前输入重跑"入口；③ 当前（最新）运行的失败/取消标签去掉"历史运行"后缀，历史折叠区内的运行保留该后缀。属接线期修订，按规则需新候选与双方新完整审查。

### F-02 [P3] 续跑时以 `phase="initial"` 发起推理，该语义未在接线提案中定义

- **位置**：`packages/engine/src/ontolearn_engine/scenario/runner.py:221-227`（`initial_context = Context(checkpoint.round, "initial")`）。
- **触发**：`run(resume=...)` 时 `checkpoint.round = N`，runner 仍以 `phase="initial"`、`round=N` 调用 `ports.infer`，随后从 `N+1` 轮继续。E.1 的"初始场景也必须先形成行为前推导快照"针对**初始场景**；续跑时该状态是中途轮次状态。
- **影响**：对当前合成端口无影响（三次独立运行结果一致、续跑与完整运行 checkpoint 相等）。但 `integration-request.md:20` 把 `initial/events/before/behavior/end` 列为对 T05 的阶段契约，未定义"续跑时 initial 表示什么"。真实 T05 适配器若把 `phase="initial"` 理解为"本次运行的首次推导"并按初始场景语义生成，会在**中途状态**上产出非预期快照；且续跑比正常轮次多一次推理调用，调用次数语义亦未声明。
- **证据**：`test_context_is_explicit_and_inference_phase_cannot_be_reused` 断言全新运行为 `[Context(0,'initial'), Context(1,'before'), Context(1,'end')]`；续跑路径未对该阶段做独立断言。
- **建议**：在 T05/T00 接线前把 `phase="initial"` 的语义写死为"当前 checkpoint 轮次边界上的前置快照"，或新增独立 `phase="resume"`；同时在 `integration-request.md` 明确续跑的阶段序列与推理调用次数。属接线契约项，不要求改动已冻结候选。

### F-03 [P3] 逐动作轨迹未约束同一触发实例内的序号连续性

- **位置**：`packages/engine/src/ontolearn_engine/scenario/runner.py:256-265`。
- **触发**：唯一性校验施加于**完整三元组** `(eventId, behaviorId, actionIndex)`。因此同一触发实例可出现 `actionIndex` 为 1 与 3（跳过 2）而不被拒绝；反之不同触发实例可各自使用 `actionIndex=1`（后者符合 E.1"同一触发实例内动作按动作序号执行"，非缺陷）。
- **影响**：E.1 定义触发实例身份为 `(eventId, behaviorId)`，G.3 B-10 期望"每个实例内部仍按动作一、动作二执行"。当前 runner 只校验身份/形状/归属，不校验实例内序号连续性。真实执行器 T06 负责生成轨迹并承担 1000 上限，故本线未越权判定动作语义；但私有形状校验比 E.1 弱一档，接线时若依赖 runner 兜底会漏检。
- **证据**：现有断言 `len(set(plan.trace)) != len(plan.trace)`（`runner.py:256`）与逐项 `action_index < 1` 检查（`:262-263`）不覆盖实例内连续性。
- **建议**：在 T06 接线时明确"轨迹连续性由行为执行器保证，runner 只校验身份/归属/唯一"，或在 runner 追加"同一 `(eventId, behaviorId)` 的 actionIndex 集合为 1..k"的校验。属契约边界澄清。

**未发现 P1 / P2。** 以上三项均不要求改动已冻结候选实现、测试、fixture、验收、依赖锁或配置；按现行规则，接线期任何实现/测试/契约变更都需生成新候选并由双方各做全新完整审查。

---

## 8. 未验边界（必须保留，不得因本报告关闭）

真实 T05 初始/事件后/轮末推理；真实 T06 冻结条件/稳定排序/冲突检测/动作语义/动作间取消；T01/I04 正式 scenario 任务注册、project/run/job 身份、原子 Round+progress、取消/最后提交/终态竞态、operation-id/expectedRound 与 ack-loss/崩溃对账、正式数据隔离；FR-705 真实删除运行/恢复基准/真实快照续跑；公共契约/bridge/App 挂载与真实页面；完整 E.5 `facts`/`inferred`/`actionTrace`/`triggeredInstances`；G.6 完整迁移与 T10 跨设备；FR-700～705 与 E.2–E.5/G.4/G.6 父验收；Windows/macOS 完整产品、平台与发布门；ZCode GLM-5.3/最高一方结论；实际 CI、远端 develop 核验、PR/合并/发布。

另：`test.rounds` 只接受 toy 载荷（`integration-request.md:26`），传完整业务 Round 会得 `IDENTITY_CONFLICT`——本线**未**以该能力冒充正式沙盘。

---

## 9. 本审者执行过程偏差记录（如实披露）

派发文件规定：`evidence/render-probe.mjs` **禁止在固定 review checkout 原位执行**（避免覆盖旧证据），须在独占 scratch 建立固定 reviewHead 的 Git 文件副本后以副本为 cwd 调用。

- **偏差**：首次调用时我以 review checkout 为 cwd 执行了原脚本（脚本内 `const root = process.cwd()`），导致 `docs/reviews/T07/evidence/ui-probe.json` 与两张 ignored PNG 在 checkout 内被原位重写（mtime 2026-10-23 03:04:03）。
- **实际影响核对**：重写后的 `ui-probe.json` SHA256 `6e5edcec…1ba8` 与 `reviewHead` 内的 blob **完全一致**；`page-wide.png` `32ede79b…616e`、`page-narrow.png` `1ee10753…3aec` 与封存原件**逐字节一致**；`git diff HEAD -- docs/reviews/T07/evidence/` 为空，`git status` 仍仅 ` M AGENTS.md` 与 `?? docs/reviews/T07/dispatch-20261022/`；实现/测试/fixture/验收/依赖锁/配置/旧输入/归档原件**均未被修改**；脚本自建的 `.t07-ui-*` scratch 已自行回收，无残留。
- **纠正**：随后按规则在独占 scratch 副本（`git archive 24f3703` 展开，25 路径逐项核 hash，其中 `status.md` 与 manifest 记录不同属已知过程文件差异，manifest 自身标记 `physicalMatches:false`）以副本为 cwd 重跑，退出 0，产出与封存原件逐字节一致。两次运行产物分别留存于 `.runtime/raw/validation/inplace-run/` 与 `.runtime/raw/validation/scratch-run/`。
- **结论**：偏差为执行位置错误，未改变任何受审内容或证据字节，但按派发规则必须如实记录，不作淡化。

---

## 10. 后续门（本报告不关闭）

双方同版本**明确通过**、必要验收通过、全部意见有处置后，方可 push/PR；实际 CI 通过后正常合并 develop 并核验远端与保护源。实现/测试/配置/依赖/验收/base 变化后须新候选、必要验证及双方全新完整审查，不沿用本结论。全部 57 项 P0、附录 C–G 与第 10–12 节、完整父 Goal、平台与发布门保留。

**最终结论：通过（限 T07-S1 私有候选范围）；3 项 P3 记录待接线期处置；父领域、完整 E.5、跨设备、双 OS 与发布门未验且未关闭。**
