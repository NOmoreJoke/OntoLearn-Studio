# I04 S2 常驻协调器与 ExecutionJob — 独立对抗性审查报告（MiniMax M3.1-Flash）

- 报告路径：`docs/reviews/I04/round-1/minimax-m31flash.md`
- 审查角色：独立只读对抗性审查者（非开发者、非总控、非另一方审查者）
- 报告写入时间：2026-10-20（本轮审查窗口内）

---

## 1. 评审任务、模型与思考设置的来源记录

| 项 | 值 | 来源与性质 |
| --- | --- | --- |
| 派发关联标签 | `I04-R1-MiniMax-M31Flash-C1-ce6fd54` | 派发文本声明为**关联标签，非原生 UUID**；本报告不据此虚构原生任务 ID |
| 指定模型 | MiniMax Code M3.1-Flash | 派发文本与总控第九节第 2 条声明 |
| 指定思考设置 | xhigh | **派发文本断言**（"经 MiniMax Code M3.1-Flash / xhigh"） |
| 我的实际上下文 | 模型标识为 `MiniMax-M3.1-Flash` | 运行时注入的 system 环境信息 |
| 独立记录 | 我的可见上下文**只暴露模型身份**，不暴露可验证的数值化 thinking/effort 设置 | 我无法自证 xhigh 已被宿主施加；既不声称"已验证 xhigh"，也不虚构 UI 截图或配置回读 |

处置：本项为**记录性说明**，不作为阻断项。模型与思考设置以总控派发记录为准；本报告的结论不依赖对思考强度的假设。

---

## 2. 项目路径、分支、base/head 与工作区状态

| 项 | 实际值（本人独立核对） |
| --- | --- |
| Git 根 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs` |
| 分支 | `feature/I04-resident-jobs` |
| base SHA | `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500` |
| head SHA | `ce6fd54fd51bb16a6eda5f45d2675506799710f5` |
| 变更规模 | 71 个文件，`+16087 / -235`，16 次提交（`7e833e6` … `ce6fd54`） |
| 保护文件 | `AGENTS.md` SHA-256 = `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`（与要求值**逐字符一致**），保持 dirty、未 stage |
| 审查开始时 `git status` | `M AGENTS.md`、`?? docs/reviews/I04/candidate-1.json`、`?? docs/reviews/I04/round-1/` |
| 审查结束时 `git status` | 上述三项 + `M docs/reviews/I04/status.md`（**追加式流程记录**，见 §3.3；由开发线在我审查窗口内追加，未触碰受审实现） |
| 候选冻结记录 | `docs/reviews/I04/candidate-1.json`：71 条文件 SHA-256、`protectedDirty: ["AGENTS.md"]`、`frozen: true`、base/head/branch/worktree 与实际一致 |

---

## 3. 已检查范围、验证命令与实际结果

### 3.1 已检查范围（本人阅读/核对的代码与证据）

**需求与治理**
`docs/iterations/I04/acceptance.md`（10 行原验收表 + F6 说明 + I03 继承处置 + 当前候选结果）、`docs/iterations/I04/implementation.md`、`docs/architecture/0003-resident-coordinator-and-jobs.md`、`docs/reviews/I04/status.md`、仓库外 `iteration-control/2026-10-19/goal-objective.md`（含第九节全文）、`docs/reviews/I04/candidate-1.json`。

**Python 引擎**
`protocol.py`、`coordinator.py`（588 行全文）、`job_store.py`（1528 行全文）、`worker.py`、`memory_guard.py`、`resources.py`、`process_environment.py`、`storage.py`（差异 + 关键区段）。

**契约**
`packages/contracts/src/v2.ts`、`packages/contracts/src/index.ts`、`packages/contracts/python/contract_v2.py`、`packages/contracts/v2/schema.json`（response/notification/params 定义）、`states.json`、`registry.json`、`errors.json`、`frame-fixtures.json`（51 例）。

**TypeScript 桌面**
`apps/desktop/src/main/engine.ts`、`jsonl.ts`、`task-service.ts`、`index.ts`、`view-navigation.ts`、`window-recovery.ts`（差异）、`preload/index.ts`、`renderer/src/App.tsx`、`renderer/src/task-presentation.ts`。

**构建/CI**
`.github/workflows/ci.yml`、`scripts/build-engine.mjs`、`apps/desktop/electron-builder.yml`、`packages/engine/entrypoint.py`、`__main__.py`（差异）。

**测试**
`packages/engine/tests/test_job_store.py`（矩阵区段）、`test_i04_round_faults.py`、`test_i04_lifecycle_boundaries.py`、`test_storage.py`、`test_contract_v2.py`。

**证据文件**
`local-verification.json`、`native-source-evidence.json`、`native-packaged-evidence.json`、`original-protection.json`、`preflight.json`、`legacy-scan-measurement.json`、`legacy-scan-attempt1.json`、`internal-runtime-review.json`、`round-1/source-provenance-note.json`、`round-1/dispatch.json`，以及 `build/I04-evidence/` 下的原始日志与 `source-final1-manifest.json`（722 条）。

### 3.2 本人实际执行的验证命令与结果

全部在唯一临时目录 `/tmp/i04-review-mm31/` 内进行；未写入 `out/build/release`，未运行 `npm run check/build/package`（该输出在本次任务中预约给 ZCode 线，开发线未在本任务内让出预约）。

| # | 命令 | 实际结果 | 退出码 |
| --- | --- | --- | --- |
| 1 | `shasum -a 256 AGENTS.md` | `db1fb184…29786`，与要求一致 | 0 |
| 2 | `git rev-parse HEAD` / `--abbrev-ref HEAD` | `ce6fd54f…` / `feature/I04-resident-jobs` | 0 |
| 3 | `git diff --stat base..head` | 71 files, 16087 insertions, 235 deletions | 0 |
| 4 | `.venv/bin/python -m pytest -p no:cacheprovider --basetemp=/tmp/i04-review-mm31/pt -q` | **992 passed in 17.51s** | **0** |
| 5 | `npx vitest run` | **12 test files passed / 593 tests passed** | **0** |
| 6 | `shasum -a 256 build/I04-evidence/next-candidate-memory-failure.log` | `182ef85f3c3599ed05505a00bff676e2f127497fe32957481d969123561d85d4`（与 JSON 声明一致） | 0 |
| 7 | 对 `next-candidate-memory-failure.json` 声明的 4 个文件逐个 `git show ce6fd54:<path> \| shasum -a 256` + 工作树哈希 | **4/4 与 ce6fd54 逐字节相同**（详见 §5 问题 3） | 0 |
| 8 | 探针 A（§5 问题 3）：在 C1 源码上重复真实 worker 内存超限场景 20 次 | **20/20 全部得到 `RESOURCE_LIMIT{memory}`，另一项目任务 20/20 `succeeded`** | 0 |
| 9 | 探针 B（§5 问题 3）：令 `resident_bytes` 抛 `MemoryGuardUnavailable` | **精确产出 `{INTERNAL_ERROR, engine.internal, {}}`**，与失败日志断言形状完全一致；且兄弟任务同时 `failed` | 0 |
| 10 | 重算 `source-final1-manifest.json` 全部 722 条对 `git show ce6fd54:<path>` | 38 处不一致：5 处为真实内容差异（`AGENTS.md` + 4 份文档），33 处为清单记录空文件而 head 树无该路径 | 0 |
| 11 | `git diff --stat ce6fd54 7e58f08f -- packages apps` | 仅 `engine.ts`、`task-service.ts`、`App.tsx`、`contracts/src/index.ts`、`test_job_store.py`；**无任何引擎运行时源码改动** | 0 |
| 12 | `git show cf6e1a8 -- packages/engine/tests/test_job_store.py` | 读出"96 格矩阵加固"提交的完整断言增量（§5 问题 2 依据） | 0 |
| 13 | `grep -rn "job.progress"` 全仓 | 生产端缺失：仅 `contract_v2.py:308`（校验）、`v2.ts:358`、`task-service.ts:584`（消费）、schema/fixtures（线例）；`coordinator.py:98-117` 只发 `job.state` | 0 |
| 14 | `grep -n pageSize packages/contracts/v2/schema.json` + `task-service.ts` | `params_result.page`/`cursorRecord` 上界 **200**；`params_job.list`/`jobListCursorRecord` 上界 **100**；TS `task-service.ts:396`=200、`:190`=100；引擎 `resources.py:43 maxPageItems=100` | 0 |

**工具性失败（如实保留，未掩盖）**
- `npx vitest run --reporter=basic` → `ERR_LOAD_URL` / `RunnerError`（vitest 5 无该 reporter 模块）。**属命令参数错误，非测试失败**；去掉该参数后重跑通过（退出码 0）。
- `bash` 读取兄弟 worktree 时被路径穿越防护拦截（`..`）；改用绝对路径经 `read` 工具读取，未绕过防护。

### 3.3 审查窗口内受审目录的新增材料（我据此更新判断）

1. `docs/reviews/I04/status.md` 追加 18 行流程记录：声明"协调器被杀后无视图重连/状态更新、首次手动恢复返回旧订阅 `NOT_FOUND`"为**已确认的下一候选 P2**，"不主张 C1 已修复"；声明 96 格矩阵"缺完整断言"，加固提交 `cf6e1a8` 在另一 worktree、尚未进入本 checkout；另记录下一候选 `d3a8070` 上复现的"project 修订号读竞态"。
2. `docs/reviews/I04/round-1/source-provenance-note.json`（新建）：解释 `local-verification.json` 的 `sourceManifest.differences=[]` 系**文档在清单采集后被修改**所致，并声明"实现/测试/配置/运行时资源与 ce6fd54 相同"。

处置：上述两项均为**追加式流程证据**，未改动受审实现、测试、配置或依赖，故不使本轮审查失效；但其内容**直接影响问题 1、2 的判定**，我已逐条独立复核（§5）。

### 3.4 未验证事项（明确记录为"未验证"，非"失败"）

| 事项 | 原因 |
| --- | --- |
| `npm run check` 聚合结果（lint/format/typecheck/vitest/build/ruff/pytest 串联）端到端复现 | `out/build/release` 在本任务中预约给 ZCode 线，开发线未让出预约。**我以等价的分项复现覆盖**：vitest 593、pytest 992 均本人独立通过；lint/format/typecheck/build/ruff 读取 `build/I04-evidence/logs/full-check-4.log` 证据（该日志记录 macOS arm64 下 593 TS + 992 Python 通过）。**"聚合命令本身未由我执行"这一点不隐瞒** |
| `npm run package:dir` 与包内同样例 | 同上（写 `out/`）。包内证据读取自 `build/I04-evidence/package-macos-final1/`（12 项 runtime 探针 exit 0） |
| Windows 内存守卫（JobObject）、Windows 打包探针 | 平台限定，本机不可得 |
| 真实最终三平台 CI、代码签名、干净设备安装、生产运行 | **双审后、合并前的强制门禁**，按派发要求不得声称本地已跑 |
| 原生窗口"可见/聚焦/真实提示框"的外部观察 | 属隔离 CI/独立桌面验收项；本机不得启动 Electron/e2e/native。现有证据中"聚焦"依赖 Electron 进程内 `isFocused()`，"原生提示框"仅由断言通过体现 |
| 领域业务语义（E.2 全阶段、E.5/G.4 工单集合、资源产能、FR-704 业务场景结果页） | 明确超出 I04 基础设施范围，仍为开放项，**本报告不代为完成** |
| `parallel-coordination.md`、`scope.md`、完整 `state.json`（1833 行） | 未逐行通读；I03 两份归档最终报告正文未在本会话打开，仅经 `status.md`/`acceptance.md` 引用定位其处置 |
| I03 R2-F1 "24 个差异反例"的逐条数量 | 反例族与严格 binding 校验存在并通过（见 §6），但"恰好 24 条"这一数字我未逐条清点 |

---

## 4. 结论先行

**C1（`e45e6038` → `ce6fd54`）不通过。**

判定依据（阻断级，3 项）：

1. 协调器进程被杀后**首次重建订阅失败**（`NOT_FOUND(subscription)`），UI 持续显示陈旧的 `running`，原始验收第 8 条不成立；**开发线自己在 status.md 中确认该缺陷在 C1 未修**。
2. **96 格故障对账矩阵的断言不完整**：C1 每格只断言 job 状态/marker/修订号，`after_commit` 仅断言"facts 非空"，未断言提交内容精确值、依赖向量与 versions 台账、失效（staleReason）重算、以及 job_blobs/job_plans/job_confirmations/operation_claims 不可变；`acceptance.md` 第 12/26 行对该矩阵的描述**强于 C1 测试实际断言的内容**。原始验收第 5、6 条证据不足。
3. **资源上界事件会被降级为通用 `INTERNAL_ERROR{}`**：Darwin RSS 采样只捕获 `OSError`，而 `resident_bytes` 抛 `MemoryGuardUnavailable(RuntimeError)`，逃逸后落入 `classify()` 兜底。我用探针**确定性复现出与实际失败日志完全相同的错误形状**；原始验收第 4、7、9 条的"资源上界分类"语义不稳健。

另有 3 项 P2（跨层分页上界不一致、`job.progress` 无生产端、`seen` 集合无回收）与 8 项 P3 证据/记录问题。全部问题的处理结论见 §5。

---

## 5. 问题清单（每项含位置、触发条件、影响、证据、修复建议、处理结论）

严重程度定义：**P1 = 阻断合并**；**P2 = 重要，须在下一候选修复，可与阻断项同批处理**；**P3 = 证据/记录/清理类，允许延期但须登记**。

### P1-1 协调器被杀后首次重建订阅失败，UI 状态陈旧

| 项 | 内容 |
| --- | --- |
| 位置 | `apps/desktop/src/main/task-service.ts:229-320`（`doSubscribe`：`watches.delete(jobId)` 后用**旧会话的** `subscriptionId` 调 `job.unsubscribe`，该调用失败会直接中断整个订阅流程，无 `NOT_FOUND` 容忍）；`apps/desktop/src/main/engine.ts`（子进程退出路径 `finish(session, exited())`，**无自动重启、不向 renderer 推送状态失效事件**） |
| 触发条件 | 常驻协调器进程被杀/崩溃 → `engineSessionId` 变化 → 旧 `subscriptionId` 在新会话中不存在 |
| 影响 | 违反原验收第 8 条（"按 project/job 查询持久权威状态与提交点、重建订阅，拒绝旧通知"）：首次 `restore()` 返回 `NOT_FOUND(resource=subscription)`，UI 保留 `running` 展示，而 job 实际已 `failed/ENGINE_EXITED`；需二次手动操作才恢复，期间 UI 与权威状态不一致 |
| 证据 | ①`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-bridge/test-results/i04-disconnect-probe.json`：`sourceCommit=ce6fd54…`，`afterIdle.updatesSinceKill=0`、`coordinatorRestarts=0`、`firstManualRestore.ok=false / NOT_FOUND{subscription}`、`finalRead` job `failed` + `ENGINE_EXITED`；②开发线 `status.md` 自述："confirmed next-candidate P2, not a claim that C1 was fixed"；③**本人代码级确认**：`doSubscribe` 中旧订阅 `unsubscribe` 的异常未被容忍，且 `watches` 已先 `delete`，故第二次调用不再发 unsubscribe 而成功——与探针"第一次失败、第二次成功"的轨迹完全吻合 |
| 修复建议 | 旧订阅 `unsubscribe` 需容忍 `NOT_FOUND{subscription}`（会话已切换属正常路径）；会话 ID 变化后强制重新查询权威状态再建立新订阅；引擎子进程退出时向 renderer 推送一次"状态需重新对账"事件，并明确重启/降级策略 |
| **处理结论** | **未关闭 — 阻断。** C1 不得合并；必须在下一候选修复并以同版新候选重新双审 |

### P1-2 96 格原子故障对账矩阵断言不完整，验收第 5/6 条证据不足

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/engine/tests/test_job_store.py:174-266`（`PHASES` 8 × mode 3 × failure 4 = 96） |
| 触发条件 | 每一格 |
| 影响 | C1 每格只断言：job `state`（succeeded/failed）、`operation_claims` marker 有无、修订号 ±1，以及失败格的整份项目状态相等；`after_commit` 格仅断言 `state(...)["facts"]` 非空。**未**断言：提交内容的精确值（事实集合、受管值 owner/source_row/managed_value、mappingState.generatedVersion）、依赖向量与 `versions` 台账、**失效（staleReason）重算结果**、job_blobs/job_plans/job_confirmations/operation_claims 的不可变性、jobs 行 `context/fingerprint/run` 冻结、`stateVersion`/`finishedAtMs` 一致性。原始验收第 6 条要求的"保留前后事实/所有权/版本/失效/marker/job"与第 5 条"同事务证据"未被逐格证明 |
| 证据 | ①C1 测试源码（本人阅读）；②`git show cf6e1a8`（另一 worktree 的加固提交）显示加固后才逐格断言上述性质（`expected_state`/`expected_vector`/`expected_ledger`/`expected_stale`、immutable tables 快照比对、frozen row 比对等），而 `ce6fd54` 树内无这些断言；③开发线 `status.md`："Controller audit identified missing complete assertions in the existing 96-cell atomic matrix" |
| 修复建议 | 将 `cf6e1a8` 等价加固纳入受审候选并重跑 96 格；同步修正 `acceptance.md` 第 12/26 行的表述，使其只声明测试真正断言的内容 |
| **处理结论** | **未关闭 — 阻断。**（注意：加固提交在另一 worktree，未进入本 checkout，故不能以"已修"计入 C1） |

### P1-3 资源上界事件被降级为通用 `INTERNAL_ERROR{}`（结合本轮提供的实际失败证据）

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/engine/src/ontolearn_engine/coordinator.py:381-386`（Darwin RSS 采样仅 `except OSError: pass`，而 `memory_guard.resident_bytes()` 抛的是 `MemoryGuardUnavailable(RuntimeError)`，**未被捕获**）；`coordinator.py:33-50`（`classify()` 对非域内异常统一兜底 `INTERNAL_ERROR{}`）；`coordinator.py:492-497`（`except Exception` → `fail_job(classify(error))`） |
| 触发条件 | 子进程在采样窗口内退出（`proc_pidinfo` 失败 → `MemoryGuardUnavailable`），或宿主负载导致 spawn 失败等任何非域内异常 |
| 影响 | 违反原始验收第 4 条（"内存故障隔离、资源上界"）、第 7 条（"SQLite/错误按真实类别分类，未知内部异常安全兜底"）、第 9 条（"资源上界与真实依赖"）。资源上界事件被呈现为"内部错误"，上层无法区分"被限流"与"引擎内部缺陷"，隔离语义与上界语义同时失真；且该次运行**未能证明**"一个 worker 故障不影响其他任务"（失败日志中兄弟任务状态未被断言） |
| 证据 | ①`build/I04-evidence/next-candidate-memory-failure.log`（SHA `182ef85f…`，与 `.json` 声明一致）：`test_memory_failure_isolated_from_other_project_real_worker` 得到 `INTERNAL_ERROR{params:{}}` 而非 `RESOURCE_LIMIT{memory}`；②**本人核对**：`.json` 声明的 4 个文件（`coordinator.py` `5ca0400f…`、`worker.py` `da98fad8…`、`memory_guard.py` `cf28e960…`、`test_i04_lifecycle_boundaries.py` `1eedf8e4…`）与 `git show ce6fd54:<path>` 及工作树哈希**逐一相同**；③`git diff --stat ce6fd54 7e58f08f` 显示该轮**未改动任何引擎运行时源码** → 观察到的失败与 C1 引擎逻辑无关、由运行环境触发；④**探针 A**：在 C1 源码上重复该场景 20 次，20/20 得到 `RESOURCE_LIMIT{memory}`，C1 全量 pytest 992 通过 → **C1 未复现该失败**；⑤**探针 B**：令 `resident_bytes` 抛 `MemoryGuardUnavailable`，C1 精确产出 `{code:INTERNAL_ERROR, messageKey:engine.internal, params:{}}`，与失败日志的断言差异逐字段一致，且兄弟任务同时 `failed` → **C1 中存在可确定复现的错误分类漏洞** |
| 修复建议 | 采样路径显式捕获 `MemoryGuardUnavailable` 并按 `RESOURCE_LIMIT{memory}`（或可区分的安全码）处理；`classify()` 增加"资源上界事件不得降级为 `INTERNAL_ERROR`"的不变式；worker 死亡原因按退出码分别映射（74→memory、75→guard 不可用、其余→`ENGINE_EXITED`）而非一律兜底；把该测试标注为平台相关（Darwin RSS 采样），并在 CI 中给出确定的断言边界 |
| **处理结论** | **未关闭 — 阻断。** 精确表述：**观察到的这一次失败不可归因于 C1 的改动**（引擎字节相同、C1 侧 20/20 通过）；**但 C1 含有可确定复现的降级漏洞**，正是它把"资源上界"事件变成了与日志完全相同的 `INTERNAL_ERROR{}`。修复必须落在 C1 代码路径上；不得以"此前全绿"覆盖，也不得降低期望 |

### P2-4 跨层分页上界不一致：`result.page` 契约/TS 允许 200，引擎只允许 100

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/contracts/v2/schema.json:2747-2751`（`params_result.page.pageSize` maximum **200**）、`:2218-2222`（`cursorRecord.pageSize` maximum 200）、`:2606-2610`（`params_job.list.pageSize` maximum **100**）、`:4421-4425`（`jobListCursorRecord` 100）；`apps/desktop/src/main/task-service.ts:396`（`result.page` ≤ **200**）、`:190`（`job.list` ≤ 100）；`packages/engine/src/ontolearn_engine/resources.py:43`（`maxPageItems: 100`）；`coordinator.py:254-255`（`job.list` 与 `result.page` 统一按 `maxPageItems` 拒绝） |
| 触发条件 | 调用方按契约/TS 合法取值请求 `result.page` 且 `pageSize ∈ [101,200]` |
| 影响 | 契约与实现对同一参数给出不同合法域：通过 schema 与 TS 校验的请求被引擎以 `RESOURCE_LIMIT{resource:page}` 拒绝。违反原始验收第 9 条（"与 U1 M0 身份/依赖/分页对齐"、"只开放已实现能力"），并使公共契约对调用方产生误导 |
| 证据 | 上列行号与上界值均为本人直接读取（命令 14） |
| 修复建议 | 统一到一个上界（建议 100，或将引擎 `maxPageItems` 提升至 200 并同步 schema/TS/游标记录类型）；因涉及公共契约与实现双方，需在下一候选同版重新双审 |
| **处理结论** | **未关闭 — P2**（允许与阻断项同批修复；不建议在无同步的情况下单独改动一侧） |

### P2-5 `job.progress` 通知无生产端，UI 阶段分支生产不可达

| 项 | 内容 |
| --- | --- |
| 位置 | 生产端缺失：`packages/engine/src/ontolearn_engine/coordinator.py:98-117`（`_notify` 只发 `event:"job.state"`）；消费端：`packages/contracts/src/v2.ts:358`、`apps/desktop/src/main/task-service.ts:584`、`apps/desktop/src/renderer/src/App.tsx:219-235`（渲染"阶段"与百分比）；契约/线例：`packages/contracts/v2/schema.json:4286`、`packages/contracts/python/contract_v2.py:308`、`packages/contracts/v2/fixtures.json`（4 条正例） |
| 触发条件 | 任何运行期状态流转 |
| 影响 | 原始验收第 4 条要求"无总量只显示阶段"，但阶段数据在生产中永不可达，UI 该分支恒空；契约与线例给出 `job.progress` 正例，易被误读为已实现能力，违反"只开放已实现验证的能力"与"不捏造百分比" |
| 证据 | 全仓 `grep -rn "job.progress"`（命令 13）：无任何 Python 生产端发出该事件；`coordinator.py` 全文只出现 `job.state` |
| 修复建议 | 二选一：由协调器在真实可用的阶段边界发出 `job.progress`（仅阶段，无百分比），或从契约/线例/UI 分支中移除该事件并同步 TS/Python；任一改动须同版重新双审 |
| **处理结论** | **未关闭 — P2** |

### P2-6 `Coordinator.seen` 集合无回收，常驻会话必然在 65536 请求后终止

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/engine/src/ontolearn_engine/coordinator.py:76`（`self.seen = set()`）、`:126-128`（`if value["id"] in self.seen or len(self.seen) >= 65536: raise ProtocolFault()`）；`serve()` 的 `inbox = queue.Queue(maxsize=64)`（`:511`） |
| 触发条件 | 单会话累计请求数达到 65536 |
| 影响 | `ProtocolFault` 为**会话致命**错误：常驻协调器在此之后不可用，与"常驻协调器"目标（第 1 条）存在结构性张力；集合只增不减、无有界淘汰或滑动窗口策略，长会话运行无任何证据支撑 |
| 证据 | 源码位置与语义为本人直接核对；未见任何覆盖长会话/淘汰策略的测试或文档说明 |
| 修复建议 | 明确会话生命周期策略：有界淘汰（如仅保留最近 N 个 id 或按会话轮换）并在契约中说明；补充长会话与重复 id 的边界测试；若判定"会话按请求量轮换"为设计意图，需在 ADR-0003/实现文档中显式写明并给出证据 |
| **处理结论** | **未关闭 — P2** |

### P3-7 `local-verification.json` 的 `sourceManifest.differences=[]` 与实际不符（已被事后说明，但主记录未更新）

| 项 | 内容 |
| --- | --- |
| 位置 | `docs/reviews/I04/local-verification.json`（`sourceManifest.differences`）、`build/I04-evidence/source-final1-manifest.json`（722 条）、`docs/reviews/I04/round-1/source-provenance-note.json` |
| 触发条件 | 以清单对 `ce6fd54` 逐文件重算 |
| 影响 | 本人重算 722 条得 38 处不一致：5 处为真实内容差异（`AGENTS.md` + `0003-resident-coordinator-and-jobs.md` + `acceptance.md` + `implementation.md` + `status.md`），33 处为清单记空文件而 head 树无该路径。**实现/测试/配置/运行时资源与 `ce6fd54` 一致**，差异仅在文档；但提交内的验证记录与实际不一致，削弱证据链自洽性 |
| 证据 | 命令 10（本人重算）；开发线事后新增的 `source-provenance-note.json` 说明了成因并给出逐文件 SHA 对照，与我的重算结论一致 |
| 修复建议 | 在 `local-verification.json` 中更新 `differences` 或加入指向 `source-provenance-note.json` 的交叉引用，避免"记录为空差异"与"实际 5 处文档差异"并存 |
| **处理结论** | **降级为 P3，已被说明**：成因已由开发线书面说明且与我的独立重算一致 → **接受该说明**；仍建议下一候选补齐主记录的交叉引用（可延期） |

### P3-8 `internal-runtime-review.json` 无法映射到任何修订

| 项 | 内容 |
| --- | --- |
| 位置 | `docs/reviews/I04/internal-runtime-review.json:3`（`observed_git_head: 83a1228…`） |
| 触发条件 | 与 `ce6fd54` 的文件哈希比对 |
| 影响 | 该内部审查声明的 head 为 `83a1228…`，但其 8 个文件哈希中有 2 个（`protocol.py`、`worker.py`）属于 `ce6fd54`，且 `worker.py` 在 `83a1228` 并不存在 → 该审查记录自相矛盾，无法确定它实际审查了哪个修订 |
| 证据 | 本人对 `ce6fd54` 的逐文件哈希核对（`protocol.py=34f85a35…`、`worker.py=da98fad8…`） |
| 修复建议 | 重新生成该记录并写入实际被审 head；或显式标注它对应的修订与生成方式 |
| **处理结论** | **未关闭 — P3**（证据可追溯性，允许延期但须在下一候选修正） |

### P3-9 `build/I04-evidence/linux-native1..4` 的失败未在提交文档中索引

| 项 | 内容 |
| --- | --- |
| 位置 | `build/I04-evidence/linux-native1..4/native.log`（未索引）；`docs/reviews/I04/status.md:59` 仅提及 `linux-smoke2` |
| 触发条件 | 阅读提交内证据链 |
| 影响 | 提交记录呈现的运行历史比磁盘实际更干净；`build/` 被 gitignore，`clean`/克隆后无任何原始日志留存，失败上下文不可追溯 |
| 证据 | 本人列举 `build/I04-evidence/` 各目录并读取 `native.log` 失败片段（早期 openbox/xdotool 环境问题）；`build/` 不在版本控制内 |
| 修复建议 | 在 `docs/reviews/I04/` 登记各失败目录、失败原因与处置（摘要即可），并说明哪些失败属于环境前置未就绪而非产品缺陷 |
| **处理结论** | **未关闭 — P3**（可延期，但下一候选应补登记） |

### P3-10 `status.md` 内部表述矛盾

| 项 | 内容 |
| --- | --- |
| 位置 | `docs/reviews/I04/status.md:5`（"实现/本地/隔离/打包验收通过"）与 `:17`（"当前无开发/运行/审查/合并通过证据"） |
| 触发条件 | 通读文档 |
| 影响 | 同一文档对"是否已通过"给出两种结论；第 5 行附有"下段为时间点初始记录"的说明，但第 17 行本身无时间标注，读者无法区分当前状态与历史快照 |
| 证据 | 本人直接阅读（审查窗口内追加的 18 行未改动这两行） |
| 修复建议 | 为历史段落统一加时间戳/状态标签，或将初始记录移入归档段落 |
| **处理结论** | **未关闭 — P3**（措辞类，限期修正） |

### P3-11 96/48 矩阵计数无对应证据记录

| 项 | 内容 |
| --- | --- |
| 位置 | `docs/iterations/I04/acceptance.md:26`（"3×8×4=96"、"48"） |
| 触发条件 | 核对证据文件 |
| 影响 | 96/48 可由 `test_job_store.py:171-180` 与 `test_i04_round_faults.py:16,64-66` 推导，但无任何证据 JSON/日志记录 96/48 的逐格实测结果（pytest 按文件报告 165 与 58），"完整矩阵已跑"只能间接推断 |
| 证据 | 本人核对测试参数化定义与 pytest 报告口径 |
| 修复建议 | 在 `local-verification.json` 增加 96/48 逐格结果的机器可读摘要（含每格终态与证据字段） |
| **处理结论** | **未关闭 — P3**（与 P1-2 同批解决为宜） |

### P3-12 原生"聚焦"证据依赖进程内自证；原生提示框缺证据字段

| 项 | 内容 |
| --- | --- |
| 位置 | `docs/reviews/I04/native-source-evidence.json`、`native-packaged-evidence.json`；`tests/e2e/i04-jobs.spec.ts:99` |
| 触发条件 | 审阅原生证据 |
| 影响 | "第二个窗口已聚焦"依赖 Electron 自身 `isFocused()`（且此前已执行 `app.focus({steal:true})`），不是外部 X 级观察者；原生提示框仅由断言通过体现，证据 JSON 中没有对应字段。两者都不能替代隔离环境中的外部原生可见性验收 |
| 证据 | 本人阅读两份原生证据 JSON 与 e2e 断言；`acceptance.md:28` 以"实际聚焦"表述该结论 |
| 修复建议 | 在证据 JSON 中显式记录原生提示框的判据字段；原生可见/聚焦的最终验收保留在隔离 CI/独立桌面执行并单独归档 |
| **处理结论** | **未关闭 — P3 且属"待隔离环境验证"项**（不得以本机证据替代） |

### P3-13 `reconcile_jobs` 存在不可达分支

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/engine/src/ontolearn_engine/job_store.py:939-943`（`state == "cancelled" and job["state"] == "queued"`） |
| 触发条件 | 静态审阅 |
| 影响 | 该分支条件不可达（终态 `cancelled` 与 `queued` 互斥），属死代码，会误导后续维护者以为覆盖了"取消与排队竞态" |
| 证据 | 源码直读 |
| 修复建议 | 删除死分支，或改为真实可达的取消/排队竞态断言 |
| **处理结论** | **未关闭 — P3**（清理项） |

### P3-14 `commit_job_round` 的 `stateVersion` 递增未走状态机守卫

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/engine/src/ontolearn_engine/job_store.py:834`（递增 `stateVersion`）与 `_transition`（校验 `permits_transition`）不一致 |
| 触发条件 | 静态审阅 |
| 影响 | 逐轮提交路径的状态版本推进未复用统一的状态迁移守卫，可能绕过既定的迁移合法性判定；当前未见被利用的证据，属一致性风险 |
| 证据 | 源码直读 |
| 修复建议 | 说明该路径为何可绕过迁移守卫；否则统一走 `_transition` |
| **处理结论** | **未关闭 — P3**（需论证，可延期） |

### P3-15 `job.create` 的 claim 预检查在事务之外

| 项 | 内容 |
| --- | --- |
| 位置 | `packages/engine/src/ontolearn_engine/coordinator.py:512`（`has_operation_claim`）、`packages/engine/src/ontolearn_engine/job_store.py:121-127`、`:480`、`:1488`（`operation TEXT PRIMARY KEY`） |
| 触发条件 | 并发同 operationId 提交 |
| 影响 | 预检查与写入之间存在时间窗；但唯一性最终由 SQLite 主键强制，库内路径在冲突时正确抛 `IDENTITY_CONFLICT`（`job_store.py:328/335/371/391`）→ 实际影响很小 |
| 证据 | 本人核对表定义与冲突分支 |
| 修复建议 | 明确预检查仅为早期友好拒绝，文档化唯一性由主键保证 |
| **处理结论** | **未关闭 — P3**（不构成缺陷，登记说明即可） |

---

## 6. 历史问题逐项关闭状态（复审口径）

来源：`docs/iterations/I04/acceptance.md:20`（I03 历史处置）、`:18`（F6）、以及原验收第 10 条对继承边界的表述。

| 编号 | 历史要求 | 本轮判断 | 依据 |
| --- | --- | --- | --- |
| **R2-F1** | 受信 binding 的 `lastSeq/stateVersion/state` 及身份字段须由可信侧构造并校验；缺字段、字符串数值、非法状态安全拒绝；不让 KeyError/TypeError 逃逸；沿用 24 个差异反例并增加合法绑定接受、错形状拒绝与真实接入链路回归；修复/回归纳入本候选新双审 | **已关闭** | `packages/contracts/python/contract_v2.py:263-300` 的 `accepts_job_event` 增加了严格 binding 形状/类型/状态校验并安全拒绝；消费端 `packages/contracts/src/v2.ts:330-370` 与 `apps/desktop/src/main/task-service.ts` 真实接入；回归覆盖于契约测试与 frame/notification 夹具；本人 pytest 992 全通过。**边界说明**："恰好 24 条反例"的数字我未逐条清点；本轮双审即为该修复要求的"同版新双审"载体 |
| **O1** | 不擅自扩展公共 schema 词汇/缺省数组上界；未来扩展须先统一 TS/Python 行为并重新审查 | **已关闭（附条件）** | 本候选的契约扩展有两处且均已同步双端并进入本轮审查：`response` 分支新增 `engineSessionId:null`（仅 `ok:false` 的非 hello 方法）——本人逐分支枚举 29 个 response 分支确认；`notification` 新增 `job.progress` 分支——但该分支**无生产端**，见 P2-5。行为一致性成立，能力实现缺失另计 |
| **O2** | 英文 `parameterMeanings` 是语义目录，不得直接作 UI 文案 | **已关闭** | 全仓检索显示 `parameterMeanings` 在应用/契约代码中**零引用**，仅在 `apps/desktop/src/renderer/src/task-presentation.ts:10` 以注释形式声明"目录与异常文本永不成为 UI 文案"；UI 文案由 `messageKey` + 受限参数组织 |
| **O3 / R6** | 保留开放状态及真实测量边界；扫描只承接实际负载测量与修复策略，不预设性能缺陷 | **保持开放（符合约定）** | `legacy-scan-measurement.json` 明确 `coldCacheControlled:false` 且未作性能结论；`legacy-scan-attempt1.json` 保留失败记录。**本轮未发现其被错误地宣称关闭**；按原约定延续开放 |
| **F5** | 内部错误到公共安全类别的适配须在实际 producer/入口/可信上下文确定后实现，不得按异常码机械映射未知来源 | **部分关闭** | 机制已就位且基于真实 producer：`classify()` 区分 `ServiceFault`/`JobFault`/`Conflict`/`sqlite3` 主码（BUSY/LOCKED→`STORAGE_BUSY`、IOERR/FULL/READONLY/CORRUPT→`STORAGE_FAILURE`）、未知→`INTERNAL_ERROR`。**但存在一条已证实的降级路径**（P1-3）：资源上界事件会被兜底为 `INTERNAL_ERROR{}`，且该路径的来源判定依赖运行时异常而非 producer 语义 → 仍需按 P1-3 修复后方可视为完全关闭 |
| **F6** | 终态摘要的**基础设施子项**：真实逐轮工作负载经真实 worker/Job/Store 事务与不可变 `result.get`/`result.page` 链路；摘要仅出现在首个非游标页面；不可用时不展示"全部处理完成" | **基础设施子项已关闭；业务子项保持开放** | `test_f6_summary_real_rounds_terminal_result_page` 经真实 worker 轮次与 Store 事务断言摘要单元格、`commitProgress`、快照与分页绑定；`acceptance.md:18` 明确仅关闭基础设施子项。**未主张** E.2 全阶段、E.5/G.4 工单集合、资源产能、FR-704 业务场景结果页——这些仍为开放项，本报告同样不代为完成 |
| **I03 继承的 I04 前置（协议/作业/存储/共享状态/验收）** | 以已双审批准并合并的 I03 版本为基线 | **基线一致，但受 P1-2 影响** | 基线树为 `e45e6038`（= I03 合并后的 develop）；但 C1 的 96 格矩阵断言弱于 I03 继承义务所要求的"保留前后事实/所有权/版本/失效/marker/job"完整性（见 P1-2），故该继承义务**在 C1 未完全满足** |
| **I05 / I06 边界** | 不夹带业务语义与网关 | **已遵守** | C1 侧未引入 I05 语义模块或 I06 网关目录；`registry.json` 中产品能力标 `design-only`、测试能力标 `test-only`；本报告不代为完成 I05/I06 验收 |

---

## 7. 最终结论

**不通过（针对冻结候选 C1：`e45e6038` → `ce6fd54`）。**

理由：

1. **存在 3 项阻断级未关闭问题**（P1-1、P1-2、P1-3）。其中 P1-1、P1-2 由开发线在 `status.md` 中自认"在 C1 未修"；P1-3 由本人在 C1 代码上确定性复现出与实际失败日志逐字段一致的错误降级形状。按审查规则，阻断问题未关闭即不得出具通过。
2. **关键验收仍无法验证**：原验收第 5、6 条（原子提交证据与故障矩阵逐项对账）因 P1-2 证据不足；第 4、7、9 条（资源上界分类与错误保真）因 P1-3 不稳健；第 8 条（进程/窗口重建后的状态查询与重建订阅）因 P1-1 直接不成立。
3. **边界声明**：本结论只针对 C1 这一冻结候选，**不否定 I04 迭代整体方向，也不代为判定下一候选**。下一候选修复上述阻断项后须**重新冻结、重新双审**，旧版本通过不沿用。

**同时明确记录以下"未验证"事实（既不记为通过，也不记为失败）**：Windows 内存守卫与打包探针、真实最终三平台 CI、代码签名、干净设备安装、生产运行、原生可见/聚焦的外部观察、领域业务语义（E.2/E.5/G.4/FR-704）。这些是双审后、合并前的强制门禁，**不得因本报告而出具任何已完成的暗示**。

**审查过程合规声明**：全程只读——未修改受审实现代码、未提交、未推送、未切换分支；唯一写入为本报告文件（`docs/reviews/I04/round-1/minimax-m31flash.md`，位于已存在的未跟踪 `round-1/` 目录内）。`AGENTS.md` 保持 dirty 且 SHA 未变；`out/build/release` 未被写入；未在本机启动任何 Electron/e2e/native/HMR 窗口或产物；未读取另一方模型的报告或结论（`round-1/` 在我列举时仅有派发与提示文件，后续出现的 `source-provenance-note.json` 为流程说明而非他方报告）。所有失败、退出码与工具性错误均如实保留。
