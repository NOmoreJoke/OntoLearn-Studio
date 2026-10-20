# I04 S2 常驻协调器与 ExecutionJob — Round 2 独立对抗性复审报告（MiniMax Code · M3.1-Flash · xhigh）

> **报告修订记录**
> - **R0（初版）**：候选完整性核验、独立复现（1015/630/矩阵/ESRCH/progress/分页/kill/证据哈希）、历史问题逐项判定、十项验收逐项判断，结论为"通过 + 1 项 P2 非阻断新发现 `R2-P1`"（依据：本人单一 harness 实测进程存活超期 10.639s）。
> - **R1（本次修订）**：收到开发线自有只读探针产物 `build/I04-evidence/handshake-independent-c2/` 后，**以本人自写 harness 在本人隔离 export 上独立复现同一现象**（§3.2 第 15 行、§5 `R2-P1`），并独立核验其源码哈希、工件哈希、方法论与证据边界。**结论方向不变（仍为通过 + `R2-P1` P2 非阻断），但事实精度与影响描述收紧**：由"进程存活超出声明时限"精确为"**协商准入在声明预算之外仍被接受**"，并据此明确原验收 #4 的握手独立时间预算子项只能按弱形式记录。修订仅涉及本报告文字与流程记录，**未改动任何受审实现、测试、配置、依赖或验收文件**。

## 0. 结论先行

**结论：通过（Pass）**，附 1 项非阻断新发现 `R2-P1`（P2）需按 §5 登记修复或明确延期。

- 历史 C1 的 3 个阻断级问题（`P1-1`、`P1-2`、`P1-3`）与 `B1` 经**机制级读码 + 本人独立可复现运行**双重确认已关闭，不是依据 `round-1-disposition.json` 的 `status` 字段或开发者/内部 agent 判断。
- 十项原验收在本候选上均有实际证据支撑，其中原生可见/焦点一项只核验了既有隔离环境证据的真实性与哈希，未在宿主复现（遵守最新 AGENTS 的无桌面打扰约束），已在 §3.4 明确列为"未验证"边界。
- 远端三平台 CI、push、PR、合并、签名、干净设备、生产与领域业务（E.2/E.5/G.4/FR-704）**均未验证**，不在本次结论内，仍是双方通过后的必经门禁。
- 本轮新增 1 项非阻断缺陷 `R2-P1`（P2）：握手时限 `handshakeMs=5000` 仅在 inbox 瞬时为空时生效，持续请求下不成立。该结论现由**两条互相独立的 harness 互证**（本人自有探针 + 开发线自有只读探针，均针对 `0462e082` 冻结字节、无 clock/queue/limits mock），且由"进程存活超期"精确到"**协商在声明预算之外仍被接受**"。属 C1 遗留代码，C2 未引入回归、也未登记。原验收 #4 的**握手独立时间预算子项按弱形式（请求数上限）成立、按声明值不成立**，处置要求见 §9。

---

## 1. 评审任务、模型及思考设置的来源记录

| 项 | 记录 |
| --- | --- |
| 派发关联标签 | `I04-R2-MiniMax-M31Flash-C2-0462e08`（**派发关联标签，非原生 UUID**，不冒充原生任务 ID） |
| 任务性质 | Round 2 独立全范围**只读**对抗性复审；与 ZCode GLM-5.3 的本轮任务互不共享结论 |
| 模型 | M3.1-Flash。来源：派发侧 UI 核验并写入 `docs/reviews/I04/round-2/dispatch.json`（`MiniMax.model = "M3.1-Flash（订阅限免）"`）；我本人运行时上下文标注 `Model: MiniMax-M3.1-Flash`，二者一致 |
| 思考设置 | **xhigh**。来源：派发声明（`dispatch.json` → `MiniMax.thinking = "xhigh"`）。**如实说明**：思考级别本身不在我可读的运行时上下文中，我无法独立核验其生效，只能以派发声明为准；本报告不据此对"思考强度"作任何额外断言 |
| 实际可见上下文 | 我能读到的运行时上下文仅包含模型标识与通用代理契约；`dispatch.json`、两份 C1 报告、处置与证据血缘文件、I04 验收/实现/ADR-0003/状态文档、总控 Goal 第九节全文均由本轮提示词直接提供或由我实际读取文件获得 |
| 独立复核声明 | 未读取另一模型本轮 round-2 报告（`docs/reviews/I04/round-2/zcode-glm53.md` 存在但**未打开、未引用**）；未使用开发者或内部 agent 判断作为通过依据；未复用本会话之前的结论性表述作为证据 |
| 新增独立证据 | 复审期间收到开发线自有只读探针产物 `build/I04-evidence/handshake-independent-c2/`（`finding-summary.json` / `probe-default.json` / `probe-idle-control.json` 及脚本）。该产物**不含另一指定模型本轮报告或其结论**。我按要求**不采信其结论**：已逐文件核验哈希、用**本人自写 harness** 在本人隔离 export 上独立复现同一现象（§3.2 第 15 行、§5 `R2-P1`），并独立判断其证据强度与边界 |
| 只读边界 | 未修改任何实现/测试/配置/依赖/验收文件；未提交、未推送、未切分支、未合并；未新建 Goal/thread。**唯一写入为本报告**（另按候选允许范围对 `docs/reviews/I04/status.md` 追加一段流程记录） |
| 保护文件 | `AGENTS.md` 保持 dirty、未 stage，SHA-256 实测 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与要求逐字符一致 |
| 宿主 GUI | 未在用户 Mac 桌面启动 Electron/e2e/native/HMR/产物 GUI；未自动点击、聚焦或 Raise 任何应用 |
| 模型/思考 | 全程保持派发指定的 M3.1-Flash / xhigh，未更换模型、未降级思考、未触发任何额度受限处置 |

---

## 2. 项目路径、分支、base/head 与候选完整性

| 项 | 值 |
| --- | --- |
| 项目路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs` |
| 分支 | `feature/I04-resident-jobs` |
| base SHA | `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`（merge-base 与声明一致） |
| head SHA | `0462e0825f3bda2774ce5d43f4422327f2d5fbd9`（= 当前 HEAD） |
| 受审区间 | 完整 base→head，**非 last commit、非仅 C1 修复**：`git diff --name-only base..head` = 93 个文件，`+33117 / −236` |
| 提交数 | 43（其中非合并 41、merge 2、首父链 19） |
| 工作区状态 | `M AGENTS.md`（保护 dirty）、`M docs/reviews/I04/status.md`（候选允许的追加式流程记录，+4 行）、`?? docs/reviews/I04/candidate-2.json`、`?? docs/reviews/I04/round-2/` |
| 候选清单核验 | `docs/reviews/I04/candidate-2.json` 声明 93 个文件；本人逐文件重算 SHA-256 并与 `git show HEAD:<path>` 实际字节比对：**93/93 全部逐字节一致，0 不匹配** |
| 集合一致性 | 候选声明文件集与 `git diff --name-only base..head` 实际集合**完全相等**（无多、无缺） |
| 运行时输入清单 | `candidate-2.json.runtimeInputs` → `build/I04-evidence/c2-runtime-inputs.json`（122 文件，SHA `74f9d234…`） |

> 结论：受审对象的完整性、范围与冻结边界成立，审查对象确为完整 93 文件区间。

---

## 3. 已检查范围、验证命令与实际结果、未验证事项

### 3.1 实际读码范围

**引擎侧（Python）**
- `packages/engine/src/ontolearn_engine/coordinator.py`（655 行）：`serve()` 主循环、握手时限、请求/响应、订阅与通知、进度生产端、Dispatch 分页上界。
- `packages/engine/src/ontolearn_engine/memory_guard.py`：`resident_bytes` 的 ESRCH 判定与 `MemoryGuard._monitor` 的失败退出路径。
- `packages/engine/src/ontolearn_engine/job_store.py`：`create_job`、`_transition`、`fail_job`/`cancelled_job`/`_finish_unsuccessful`、`commit_job_round`、`reconcile_jobs`、`has_operation_claim`、`operation_claims` 表与不可变触发器、`_check_summary`。
- `packages/engine/src/ontolearn_engine/protocol.py`：`JsonlReader` 追加前字节上限、`decode_frame`（深度 32 / 重复键拒绝）。
- `packages/engine/src/ontolearn_engine/resources.py`：`LIMITS`（`handshakeMs=5000` 等）与 registry 原始字节 SHA。

**契约侧**
- `packages/contracts/python/contract_v2.py`：`validate`、`semantic`、`accepts_job_event`；`packages/contracts/src/v2.ts` 对等 `acceptsJobEvent`。

**主进程 / 桥接 / UI**
- `apps/desktop/src/main/task-service.ts`（887 行）：`doSubscribe`、`clearView`/`fenceConnection`、`connectionChanged`、`beginRecovery`/`recover`、`restoreOnce`、`reconcileMarkers`、`receive` 早到事件缓冲。
- `apps/desktop/src/main/engine.ts`（537 行）：`EngineSupervisor` 会话复用、registry 原始字节 SHA、心跳、`getEngineEnvironment` 白名单。
- `apps/desktop/src/preload/index.ts`（业务命名通道面）、`apps/desktop/src/renderer/src/{App.tsx,task-presentation.ts,task-progress.ts}`。

**安全边界与打包**
- `apps/desktop/src/csp.ts`、`apps/desktop/src/main/window-security.ts`、`apps/desktop/src/main/trusted-document.ts`（相对 base **零 diff**）。
- `apps/desktop/electron-builder.yml`、`scripts/build-engine.mjs`、`scripts/verify-i04-package.py`、`scripts/i04_matrix_evidence.py`、`.github/workflows/ci.yml`。

**文档**
- `docs/iterations/I04/acceptance.md`、`docs/iterations/I04/implementation.md`、`docs/architecture/0003-resident-coordinator-and-jobs.md`、`docs/reviews/I04/status.md`、最新 `AGENTS.md`、`docs/reviews/I04/round-1/{minimax-m31flash.md,zcode-glm53.md}`、`round-1-disposition.json`、`round-1-evidence-lineage.json`、`round-2/dispatch.json`。

### 3.2 本人实际执行的验证命令与结果

隔离方式：`git archive 0462e0825f3bda2774ce5d43f4422327f2d5fbd9` 导出冻结字节到唯一 ignored 目录 `build/I04-review-MiniMax-M31Flash-C2/src`，在导出副本内建立独立依赖（`node_modules`/`.venv` 为 APFS clone，venv 的 editable 安装路径重指向导出源码）。**共享 `out/build/release` 未写入**。

| # | 命令 | 实际结果 |
| --- | --- | --- |
| 1 | `src/.venv/bin/python -m pytest packages/engine/tests -q --basetemp=build/I04-review-MiniMax-M31Flash-C2/pt -o cache_dir=build/I04-review-MiniMax-M31Flash-C2/cache` | **1015 passed**（34.77s） |
| 2 | `npx vitest run`（导出副本内） | **630 passed / 15 files**（6.93s） |
| 3 | `npm run typecheck`（contracts / unit / desktop 三段） | exit **0** |
| 4 | 矩阵 recorder（仓库根，`-p scripts.i04_matrix_evidence --i04-matrix-evidence …/mx`） | **144 passed**，exit 0；`atomic {expected 96, collected 96, passed 96}`、`round {expected 48, collected 48, passed 48}`；`completedCalls=144`、`capturedDatabases=144`、`observedMainJobStates={failed:120, succeeded:12, cancelled:12}`、`errors=[]`、`unexpectedTests=[]`、`cases.jsonl` 144 条唯一 nodeid |
| 5 | **负对照**：只选 5 个真实通过用例重跑同一 recorder | pytest **5 passed**，但 recorder **exit 1**，`errors=[INCOMPLETE_DATABASE_EVIDENCE, INCOMPLETE_OR_DUPLICATE_MATRIX:atomic, INCOMPLETE_OR_DUPLICATE_MATRIX:round, NONPASS_MATRIX_CASE:atomic, NONPASS_MATRIX_CASE:round]` → 证明缺格**不会**被计数推导掩盖 |
| 6 | CI 同款调用（仓库根 + `--i04-matrix-source-revision HEAD`） | **144 passed**、exit 0、`status=passed`、`errors=[]`、`sourceRevision=HEAD` |
| 7 | Darwin ESRCH 竞态用例 `test_actual_memory_worker_exit_precedes_asyncio_returncode_delivery` 连续重跑 | **10/10 通过**；与 `test_memory_failure_isolated_from_other_project_real_worker` 同批 2 passed |
| 8 | 语义探针：真实 ESRCH → 非 ESRCH 监测不可用 | 真实 ESRCH → `ProcessLookupError` → 交实际退出码 → job **succeeded**；监测不可用 → job **failed / INTERNAL_ERROR**（fail-closed，未被静默忽略） |
| 9 | `job.progress` 生产端探针 | 订阅后收到 **5 条 progress**（queued/loading/computing/reconciling/committing），`completed=None`、`total=None`（**无捏造百分比**）；通知 seq 严格 +1 递增，subscribe 响应 seq=0 不变 |
| 10 | 分页三层探针 | schema `params_result.page` max=200 / `params_job.list` max=100；引擎 `maxPageItems=200`；`result.page` 201 → `INVALID_REQUEST`；显式更小预算 100 → `RESOURCE_LIMIT{page}`；真实 200 行页通过（42420 字节 < `maxPageBytes=131072`） |
| 11 | 对抗探针（越权/越界） | 跨项目 result 绑定 → `NOT_FOUND{result}`；`job.list` pageSize=150 → `INVALID_REQUEST`；`result.page` 201 → `INVALID_REQUEST`；未授权项目 → `PERMISSION_DENIED` |
| 12 | 协调器 kill 探针 | 杀前 running、`lastCommittedRound=6` → 杀后 `reconcile_jobs` 恢复 1 个，state=**failed**、error=`ENGINE_EXITED`、**已提交轮次 6 保留**、**无 operation marker**（不重放写入） |
| 13 | 握手时限探针（见 §5 `R2-P1`） | 控制组（空闲 stdin）**5.155s** 退出；洪泛组（inbox 恒非空）**10.639s** 才退出、返回 **65536** 个响应、exit 0、stderr 空 |
| 14 | 证据哈希核验 | `reconnect-verification.json` 71/71 artifact SHA 全部匹配、无缺失；`cases.jsonl` SHA 与声明一致；native source/packaged 两份 raw JSON SHA 匹配；`matrix-evidence.json` 144 条唯一 nodeid 无重复 |
| 15 | **超时后 hello 探针（自写 harness，收到开发线证据后独立复现）**：`build/I04-review-MiniMax-M31Flash-C2/probe_late_hello.py` → `probe_late_hello.json` | 空闲对照臂：自然退出 **5.1117s**、exit 0、stdout/stderr 均 0 字节（声明的 5000ms 预算在 inbox 空闲时**确实生效**）；迟延 hello 臂：持续发送 **40561** 条合法唯一 pre-handshake `health`（inbox 恒非空），首 reply **0.0704s** ⇒ 最晚可能截止 **5.0704s**；hello 于 **5.3121s** 发出、**5.3928s 仍被接受**（`ok=true`、签发 `engineSessionId`、`limits.handshakeMs=5000` 照常回传）⇒ **协商在声明预算之外至少 0.3224s 成立**；cleanup 前进程存活，stderr 0 字节 |

**保留的失败与工具性错误（不掩盖、不掩盖为通过）**
- vitest 首次 5 例失败：根因为导出副本的 venv editable 安装仍指向原 checkout（`worker.py` 路径断言）；定位并重指向 `src/.venv/…/_editable_impl_ontolearn_engine.pth` 后全绿。**属隔离环境构造问题，非产品缺陷**。
- `pytest` 报 `-o cache_dir` 为未知配置项警告（无害，不影响结果）。
- 矩阵 recorder 首次报 `ImportError: No module named 'scripts'`：插件须从**仓库根**以 `-p scripts.i04_matrix_evidence` 加载（脚本头部已注明该要求）。**属调用方式问题，非产品缺陷**。
- 本人 `test.rounds` 探针首次因缺 `confirmationRef` 触发 `INVALID_REQUEST`：**探针构造错误，非产品缺陷**。

### 3.3 证据文件审阅（读实际内容 + 哈希核验，不只看汇总数字）

- **C2 验收证据**：`reconnect-verification.json`（71/71 artifact SHA 逐个匹配）、`reconnect-desktop-evidence.json`、`reconnect-internal-review.json`、`matrix-evidence.json`（144 条唯一 nodeid）。
- **历史 C1 记录（明确标注来源，不冒充 C2 验收）**：`local-verification.json`、`native-source-evidence.json`、`native-packaged-evidence.json`、`internal-runtime-review.json`（`observed_git_head = 83a12283…`，早于本候选）。
- **raw 产物**：macOS `c2-final-check.log` = 630 TS + 1015 Python；隔离 Linux arm64 `check-complete.log` = 630 TS + **1013 passed + 2 skipped**，两项 skipped 均定位为 Darwin 专属 `skipif`（`packages/engine/tests/test_i04_lifecycle_boundaries.py:234` 与 `:294`），非缺测。
- **原生证据**：raw JSON 中 `windows[1].x11Focus = {observer:"xdotool/XGetInputFocus", windowId, title, visible}` 与 `nativeDialogs`（crash/hang 各含 windowId/title/visible）确实存在 → C1 `P3-12` 要求的"外部 X 焦点 + 实际 dialog 字段"已补齐。
- **包内资源**：macOS / Linux 两平台 `resources.json` 均 `frozen=true`，9 项资源 SHA 与源码**逐字节一致**；两平台包内 12 项 runtime probe 均 exit 0。
- **开发线自有握手探针（`build/I04-evidence/handshake-independent-c2/`）**：本人逐项核验——(a) 声明的 3 个源码 SHA-256 与 `git show 0462e082:<path>` **逐字节相同**（`coordinator.py` `8f2ab2ac…`、`protocol.py` `34f85a35…`、`resources.py` `8bba36a3…`），工作区同字节；(b) `finding-summary.json` 所列 6 个工件的 SHA-256 与字节数**全部匹配**；(c) 探针脚本自身 `assert raw == git show PIN:path`，确实把运行绑定到冻结提交；(d) 使用真实 stdio、真实 SQLite 临时库、默认 `LIMITS`，**未对 clock/queue/reader/limits 做任何 monkeypatch**，符合"无 mock"要求；(e) 阴性对照（空闲、父 stdin 开启）自然退出 5.1261s/exit 0/无输出；(f) 收尾为显式 SIGTERM，报告已声明最终 exit 0 **不冒充自然到期退出**。**证据强度评价：方法论成立、上界推导（首 reply 之后才可能观察到 deadline ⇒ 最晚 5.0823s）成立、未夸大（明确声明不主张无限寿命或资源耗尽测量）。** **两点保留**：(i) `probe-default.log` 与 `probe-default.json`、`probe-idle-control.log` 与 `probe-idle-control.json` **字节完全相同**（分别为同一内容的副本），故该目录中的"log"并非独立的原始 stdout/stderr 日志，而是报告 JSON 的同内容拷贝，证据链上应按 JSON 报告计；(ii) 其结论（"P2 confirmed"）属开发线判断，我未直接采信，已用本人 harness 独立复现（§3.2 第 15 行）。

### 3.4 未验证事项（明确记录为"未验证"，不记为通过、不记为失败）

1. **远端三平台 CI**（Linux / Windows / macOS 官方 runner）未运行；本轮所有数字均来自本地隔离环境。
2. **push / PR / 合并 / 远端核验**未执行（双方通过后的必经门禁）。
3. **签名安装、干净设备、生产环境**验证未执行（PRD Q 类决策未由本 ADR 替代）。
4. **领域业务**（E.2 全阶段、E.5/G.4 工单集合与产能/指标/业务重放、FR-704 业务结果页）未验证、未完成；I04 仅交付基础设施与测试专用任务负载。
5. **宿主 Mac 上的原生可见/焦点/无响应**未由本人复现（遵守最新 AGENTS 无桌面打扰约束）；既有原生证据来自独立 Docker/Xvfb/Openbox 环境，本人只核验其内容与哈希真实性，**arm64 隔离环境不冒充 CI x64/Windows**。
6. **I05 语义、I06 网关**的产品集成未开始（I05 hooks 未提前复制、I06 未接入）。
7. **性能与容量通过线**未测量（I01 R6 历史增长保持原等级开放/延期，本轮未据合成测量作任何性能承诺）。
8. §3.2 中第 8–12 项为**内联对抗探针**，未落盘脚本文件（握手反例的 2 份脚本与 3 份矩阵摘要已落盘）；其断言与观测结果完整记录于本报告，可按记录在隔离 export 中复现。
9. **开发线自有的握手探针属旁证**：它证明该现象在本地隔离环境可复现，但**不能替代**远端 CI、独立第三方复现或跨平台确认；本报告对该现象的判定同样只覆盖本地隔离环境（arm64 macOS），不主张跨架构一致，也不主张该现象构成安全边界突破。

---

## 4. 安全边界专项核验

| 检查项 | 结果 |
| --- | --- |
| `csp.ts` / `window-security.ts` / `trusted-document.ts` 相对 base 的 diff | **零差异**（未新增第三份策略，未改生产策略） |
| 生产脚本 `unsafe-inline` / `unsafe-eval` | 新增代码中**不存在** |
| preload 暴露面 | 全为**按业务命名**的方法（读取/取消/订阅），无 `invoke(method, params)` 式通用通道 |
| renderer 能力 | 无创建任务/指定路径/通用 IPC 路径；e2e 断言 `'createJob' in window.ontolearn === false` |
| 跨边界错误 | 仅固定错误码 + 受限参数；不回传原异常、堆栈、路径、单元格原值或凭据；未知来源异常统一 `INTERNAL_ERROR` |
| 项目归属 | 跨项目 result 绑定 → `NOT_FOUND{result}`（不泄漏存在性）；未授权项目 → `PERMISSION_DENIED` |

---

## 5. 本轮新发现问题

### R2-P1（P2，非阻断）：握手时限 `handshakeMs` 在持续请求下不成立，可被绕过

- **编号**：R2-P1
- **严重程度**：**P2（非阻断）**
- **文件位置**：`packages/engine/src/ontolearn_engine/coordinator.py:632–640`（`serve()` 主循环）；上限定义 `packages/engine/src/ontolearn_engine/resources.py:35`（`"handshakeMs": 5000`）；文档承诺 `docs/iterations/I04/implementation.md:13`（"…请求/总量/启动/握手/心跳/取消收尾…分别有界"）与 `docs/architecture/0003-resident-coordinator-and-jobs.md`（"每个 stdio 会话最多接受 65,536 个唯一请求"）。

- **触发条件**：客户端在完成 `hello` 之前持续向协调器 stdin 写入请求，使 `inbox` **恒不为空**。此时 `serve()` 永远不会进入 `except queue.Empty:` 分支，而握手时限检查**恰好只写在该分支内**：

  ```python
  handshake_deadline = time.monotonic() + LIMITS["handshakeMs"] / 1000
  ...
      try:
          value = inbox.get_nowait()
      except queue.Empty:
          if coordinator.session is None and time.monotonic() > handshake_deadline:
              break
  ```
  （`coordinator.py:632` 设定时限；`:638` 是唯一检查点）

- **影响**：
  1. 对外声明的 `handshakeMs=5000` 上限在持续流量下**不成立**；进程存活时间由"5 秒"退化为"65536 次请求预算耗尽"（本人实测 10.639s）。
  2. **握手准入本身越出声明预算**（比"进程活得久"更实质）：在 inbox 持续非空时，**晚于截止时刻发出的 `hello` 仍被接受并签发会话**（本人实测超出最晚可能截止 0.3224s；开发线自有探针在其环境超出 0.7275s）。也就是说，"未完成握手的协调器"可以在声明预算之外完成协商并进入正式会话状态，而 `hello` 响应中回传的 `limits.handshakeMs` 仍宣称 5000ms —— **声明值与实际行为不一致**。
  3. 未握手期间所有非 hello 请求均被安全拒绝（`HANDSHAKE_REQUIRED`），**不写入任何数据、不绕过项目授权**；握手成功后一切权限校验照常生效（能力集、registryHash、项目授权均在 hello/后续请求中逐项校验）。总体仍被 65536 身份预算硬性封顶，故影响**有界**。
  4. 实际后果是：主进程侧若长时间未完成握手但持续占用 stdin（异常重连、错误的 pre-handshake 心跳循环），协调器不会在 5 秒内退出以暴露"未握手"故障，监督方的快速失败判定被推迟；且可能出现"超时后补握手成功"的情形，使启动时序判定与实际状态不一致。
  5. 因 stdio 管道只连接 Electron 主进程，可"攻击"者限于本机父进程，**不构成跨信任边界的安全问题**；无外部攻击面、无凭据/数据/授权影响。
  6. 对原验收 #4 的直接影响：**"握手独立时间预算"按声明值不成立**，该子项目前只以"请求数上限（65536）"这一弱形式成立。原验收 #4 其余子项（队列/并发/单 writer/不可变快照/单请求与总时限/心跳不延长总时限/取消收尾/帧/队列/分页/内存有界、无总量只显示阶段、worker 故障隔离、单 job 取消不杀协调器）不受影响。

- **证据**（本人实跑，落盘于唯一 ignored 目录 `build/I04-review-MiniMax-M31Flash-C2/`）：
  - 探针脚本：`probe_handshake.py`；结果：`probe_handshake.json`
  - 控制组（写 1 条请求后 stdin 保持开启且空闲）：`sent=1, responses=1, elapsedSeconds=5.155, exitCode=0, stderr=""` → 时限**生效**。
  - 洪泛组（无间隔持续写入，inbox 恒非空）：`sent=66033, responses=65536, elapsedSeconds=10.639, exitCode=0, stderr=""` → 时限**被绕过**，进程越过 5 秒存活至 65536 身份预算耗尽才退出（exit 0，stderr 空）。
  - 归属核查：`git show ce6fd54:packages/engine/src/ontolearn_engine/coordinator.py` 的同一分支逻辑与 HEAD **完全相同**；C2 对该文件的唯一相关改动是 `read1` → `os.read`（`2e94c03` 修复父进程仍持有 stdin 时的退出争用）。→ **属 C1 遗留缺口，C2 未引入回归**。
  - 覆盖缺口：`packages/engine/tests/` 中与 handshake 相关的用例为 `test_handshake_health_reuse_and_exact_registry_hash` 与 `test_prehandshake_gate_precedes_method_params`，**均不覆盖"未握手且请求持续到达"下的时限行为**。

- **第二条独立证据线（本人自写 harness，独立复现）**：`build/I04-review-MiniMax-M31Flash-C2/probe_late_hello.py` → `probe_late_hello.json`（本人隔离 export 的冻结字节，真实 stdio + 真实 SQLite，无 clock/queue/limits mock）：
  - 空闲对照臂：自然退出 **5.1117s**、exit 0、stdout/stderr 0 字节 → 声明的 5000ms 预算在 inbox 空闲时**确实生效**（排除"该上限本就不存在/从未生效"的解释）。
  - 迟延 hello 臂：连续发送 **40561** 条合法唯一 pre-handshake `health`（inbox 恒非空）；首 reply **0.0704s** ⇒ 最晚可能截止 **5.0704s**；`hello` 于 **5.3121s** 发出、**5.3928s 被接受**（`ok=true`、签发 `engineSessionId`、`limits.handshakeMs=5000` 照常回传）⇒ **协商越出声明预算至少 0.3224s 仍成立**；cleanup 前进程存活；stderr 0 字节。
  - 结论：**我本人独立得出与首轮相同的判定**（`R2-P1` 成立），并把事实精度从"进程存活超期"提高到"**协商准入越出声明预算**"。该复现与开发线自有探针**相互独立**（不同 harness、不同请求数、不同源码绑定方式：一侧绑定本人 export，一侧以 `assert raw == git show PIN:path` 绑定冻结提交）。

- **与开发线自有探针的交叉核验**（见 §3.3）：`build/I04-evidence/handshake-independent-c2/` 的 3 个源码哈希与 6 个工件哈希经本人独立重算**全部匹配**，其方法论（真实 stdio/真实 SQLite/默认 LIMITS/无 monkeypatch、空闲阴性对照、显式 SIGTERM 不冒充自然到期、上界推导）成立；我对其**结论文字不采信**，仅将其作为交叉印证的旁证。两条证据线在关键数值上互相独立地落在同一量级（超期 0.32s vs 0.73s，自然到期 5.11s vs 5.13s），互不依赖。

- **处置责任**：非 C2 回归，但修复必然触及受审路径 `coordinator.py`，须由处置方在**新候选**中完成，并重新走双方全范围复审。
- **修复建议**（供开发线选择，均为低风险局部改动）：
  1. 把时限检查移出 `except queue.Empty` 分支，改为在**每次请求处理前后**无条件检查 `time.monotonic() > handshake_deadline`（会话已建立则不适用），使时限与 inbox 状态解耦；**截止时刻必须保持为绝对时刻**，不得因被拒绝的请求而续期（否则等价于"只要有流量就永不超时"）。
  2. 或将"未握手期允许处理的请求数"单独设上限并计数，超限即结束会话，使"握手前"路径有独立的硬上界（可与时间预算并存）。
  3. 补回归用例（建议以默认 `handshakeMs` 保留本次反例为证据，另设**单独标注**的短上限确定性用例做回归，避免用短上限冒充默认预算证明）：持续 pre-handshake 洪泛下，进程仍在 `handshakeMs` 附近退出、**迟到的 `hello` 必须被拒绝或传输关闭**，同时断言空闲期限仍生效、正常及时 `hello` 仍可成功、stderr 有界、无会话建立、无数据写入。
  4. 修复涉及 `coordinator.py`（受审路径），须**生成新候选并重新走双方全范围复审**，不得在本候选上直接改。

- **处理结论**：**登记为非阻断缺陷（P2），但须在新候选中修复**。理由：① 该阶段仍有硬上界（65536 请求身份预算），不存在无限寿命；② 不涉及数据一致性、授权、项目归属、凭据或跨信任边界；③ 可"触发"者限于本机父进程；④ 属 C1 遗留而非 C2 回归；⑤ 实测超期量为 0.32s（本人）/0.73s（开发线），量级有限。**不据此推翻本轮候选结论**。
  **强制处置要求（合并前必须闭环）**：
  1. 修复 `coordinator.py` 的握手时限检查点，生成**新候选**并**重新走双方全范围复审**（开发线已计划在另线新候选开展修复，本报告不预判其结果、不接受"在新候选上继续沿用本轮通过"的做法）；
  2. 或由处置方**明确延期并登记理由**（含为何不影响启动失败判定与后续合规验收）；
  3. **在闭环前，任何文档、状态或发布说明不得声称"握手独立时间预算已验证成立"**；原验收 #4 的握手时限子项应按"弱形式成立（请求数上限）"表述，不得按声明值 5000ms 表述。

### 5.1 已核验为"非问题"的对抗性假设（记录证据边界，避免后轮重复探查）

| 假设 | 实测结果 |
| --- | --- |
| 跨项目可读取他人结果 | `NOT_FOUND{result}`（不区分"不存在"与"无权限"，未泄漏存在性） |
| `job.list` / `result.page` 越界 | `pageSize=150` → `INVALID_REQUEST`（schema 层）；`result.page` 201 → `INVALID_REQUEST`；引擎 `maxPageItems=200` 与契约一致 |
| 内存监测不可用被静默忽略 | 监测不可用 → job **failed / INTERNAL_ERROR**（fail-closed，未吞掉） |
| 协调器被杀后自动重放写操作 | 无 operation marker，已提交轮次保留，未重放 |
| 新增代码削弱 CSP / 放开 preload | CSP/窗口安全零 diff；preload 全业务命名；renderer 无 createJob 路径 |
| 父进程仍持有 stdin 时 fatal 退出受阻 | 干净退出（exit 0、stderr 空） |
| `job.list` 100 与 `result.page` 200 不一致属矛盾 | 属分层设计（集合列表 vs 分页结果），三层各自自洽，非缺陷 |

---

## 6. 历史问题逐项关闭判断（Round 1 全部条目 + 继承义务）

判定口径：以**当前候选的实际代码与本人独立运行结果**为准；原 ID 与 P 等级原样保留；不采信 `round-1-disposition.json` 的 `status` 字段。

### 6.1 ZCode GLM-5.3 条目

| ID | 级别 | 摘要 | 关闭判断 | 依据 |
| --- | --- | --- | --- | --- |
| **B1** | P2 | Darwin 内存故障分类竞态：超限任务偶发返回 `INTERNAL_ERROR` 而非 `RESOURCE_LIMIT(memory)` | **已关闭** | `memory_guard.py:87–90` 仅在 `read<=0 且 errno==ESRCH` 时抛 `ProcessLookupError`，其余抛 `MemoryGuardUnavailable`；`coordinator.py` 只捕获 `ProcessLookupError`；worker 自身监测故障 `os._exit(75)`。本人实测：真实 ESRCH → 交实际退出码 → job succeeded；非 ESRCH → fail-closed failed；Darwin 竞态用例 **10/10** 通过 |
| **Z1** | P3 | source-final1 清单与冻结候选存在 4 个文档差异 | **已关闭** | 本人 93/93 文件 SHA 与 `git show HEAD:<path>` 逐字节一致；4 处差异均为**记录时点文档差异**，实现字节不受影响，已由 lineage 文件交叉索引 |
| **Z2** | P3 | `reconcile_jobs` 存在不可达分支（死代码） | **已关闭** | 死分支已删除，现按 `cancelling` / 其他二分；取消与恢复守卫经独立探针验证 |
| **Z3** | P3 | 非分页响应依赖 schema 上界而非显式字节预算预检 | **仍未关闭（延期）** | 保持现有 schema 上界与致命帧保护；未来词汇/默认上界变更须统一 TS/Python 双端并重新审查。原登记的"不声称关闭"维持有效，不因本轮而上调 |

### 6.2 MiniMax M3.1-Flash 条目

| ID | 级别 | 摘要 | 关闭判断 | 依据 |
| --- | --- | --- | --- | --- |
| **P1-1** | P1 | 协调器被杀后首次重建订阅失败，UI 状态陈旧 | **已关闭** | `task-service.ts`：`doSubscribe` 对旧会话 unsubscribe 以 `previous.binding.engineSessionId === this.engine.engineSessionId` 守卫；`clearView`/`fenceConnection` 分层；`connectionChanged` + `beginRecovery`/`recover` **三次有界只读恢复**（250/500ms 退避、15s 上限）；`App.tsx` 以 `connectionEpoch` 隔离迟到 health；`restoreOnce`/`reconcileMarkers` 走持久权威查询 |
| **P1-2** | P1 | 96 格原子故障对账矩阵断言不完整，验收 5/6 条证据不足 | **已关闭** | 本人独立运行：atomic **96/96**、round **48/48**、`completedCalls=144`、`capturedDatabases=144`、144 条唯一 nodeid、`errors=[]`；**负对照**证明缺格会 exit 1（见 §3.2 第 5 行），计数不可被推导掩盖 |
| **P1-3** | P1 | 资源上界事件被降级为通用 `INTERNAL_ERROR{}` | **已关闭** | 与 B1 同源缺陷：仅真正 ESRCH 交实际退出码；短读/权限/监测不可用保持 fail-closed，**不再把"进程已消失"降级为通用错误**；未以"广泛忽略 `MemoryGuardUnavailable`"或"未知监测错误当作内存耗尽"的方式修复 |
| **P2-4** | P2 | `result.page` 契约/TS 允许 200，引擎只允许 100 | **已关闭** | 三层一致：schema max=200 / TS 对等 / 引擎 `maxPageItems=200`；`job.list` 保持 100；201 → `INVALID_REQUEST`；显式更小预算 100 → `RESOURCE_LIMIT{page}`；真实 200 行页通过（42420 B < 131072 B） |
| **P2-5** | P2 | `job.progress` 通知无生产端，UI 阶段分支生产不可达 | **已关闭** | `coordinator.py` 的 `_progress`/`_stage` 为**真实生产端**（仅在真实排队/读取/计算/提交/退出对账边界发阶段）；实测 5 条 progress、`completed=None`/`total=None`、无捏造百分比；通知 seq 严格 +1；renderer 早期缓冲 ≤16 条、身份/代次/stateVersion 校验 |
| **P2-6** | P2 | `Coordinator.seen` 无回收，常驻会话必然在 65536 请求后终止 | **已关闭（语义已明确）** | `seen` 上限 65536、含 hello/ping、**不淘汰 ID**；`test_session_keeps_all_request_identities_until_its_explicit_budget` 通过；超限即关会话（exit 0、stderr 空）；ADR/implementation 明确"常驻=进程复用，不承诺无限请求或任务无中断"。本人洪泛实测同为 65536 响应后关闭，行为与文档一致 |
| **P3-7** | P3 | `local-verification.json` 的 `differences=[]` 与实际不符 | **已关闭** | 原报告未被改写；差异由 `round-1-evidence-lineage.json` 显式交叉索引；原"33 条缺失路径"主张保留为**争议项**未被静默接受；本人以 93/93 SHA 复核替代 |
| **P3-8** | P3 | `internal-runtime-review.json` 无法映射到任何修订 | **已关闭** | 该文件明确标注为**历史 C1 记录**（`observed_git_head 83a12283…`），不作 C2 验收证据；C2 证据另立 `reconnect-*.json` 与 `matrix-evidence.json` |
| **P3-9** | P3 | `linux-native1..4` 失败未在提交文档中索引 | **已关闭** | lineage 文件索引原始失败与 raw 哈希；raw 目录仍保留原失败，**未以后续绿色覆盖** |
| **P3-10** | P3 | `status.md` 内部表述矛盾 | **已关闭** | 现行 `status.md` 明确记载 C1 双不通过与待办；本轮仅追加派发/结论记录，未改历史表述 |
| **P3-11** | P3 | 96/48 矩阵计数无对应证据记录 | **已关闭** | recorder 产出 `summary.json` + `cases.jsonl`（144 唯一 nodeid）并由 CI 上传独立 artifact；本人独立复现并做负对照 |
| **P3-12** | P3 | 原生"聚焦"证据进程内自证；原生提示框缺证据字段 | **已关闭（证据层面；宿主复现未做）** | raw JSON 含 `windows[1].x11Focus = {observer:"xdotool/XGetInputFocus", windowId, title, visible}` 与 `nativeDialogs`（crash/hang 各含 windowId/title/visible）；源码与包内两份 SHA 匹配。**边界**：未在宿主复现（无桌面打扰约束），仍待远端 CI/独立环境 |
| **P3-13** | P3 | `reconcile_jobs` 存在不可达分支 | **已关闭** | 同 Z2 |
| **P3-14** | P3 | `commit_job_round` 的 `stateVersion` 递增未走状态机守卫 | **已关闭** | 以 `state=="running" and mode=="rounds"` 守卫 + `stateVersion += 1` 持久化 revision；`implementation.md` 有专门说明（"原 running→running 不属于状态名称边，不能为复用函数而放宽状态机"）；queued/cancelling/终态/其他能力拒绝且数据库不变 |
| **P3-15** | P3 | `job.create` 的 claim 预检查在事务之外 | **已关闭** | `has_operation_claim` 为 **advisory**（队列预算/幂等早判）；权威创建在 `BEGIN IMMEDIATE` 内复验完整指纹；`operation_claims(operation TEXT PRIMARY KEY)` + 不可变触发器保证全局唯一；指纹覆盖 input/confirmation/parameters/snapshot/plan/project/capability/implementation/limits/dependencyVector/manifests |

### 6.3 继承自 I03 / I01 的义务

| 义务 | 判断 | 依据 |
| --- | --- | --- |
| **I03 R2-F1**（可信 binding 校验） | **已闭环** | `contract_v2.accepts_job_event` 严格校验 7 字段集合、id 形态、`lastSeq`/`stateVersion` 为真整数且在范围内、state 枚举；TS `acceptsJobEvent` 对等；语料 41 例（1 合法 + 40 拒绝）；不外传原异常；合法绑定语义保留 |
| **I03 O1**（词汇/默认上界策略） | **仍未关闭（延期）** | 本轮三层上界（`result.page` 200 / `job.list` 100 / 帧字节上限）自洽，未引入新分歧；策略变更须统一双端并重新审查 |
| **I03 O2**（parameterMeanings 是语义目录而非 UI 文案） | **维持原判定** | UI 使用固定本地模板（`task-presentation.ts` 四段式）组装"发生什么/原因/修复/相关知识"，未直接渲染 `parameterMeanings` |
| **I03 O3 / I01 R6**（历史增长/性能） | **仍未关闭（开放/延期）** | 保持原等级；本轮未据合成测量作性能或容量承诺，未夹带无证据优化 |
| **F5**（内部错误到公共安全类别的适配） | **维持并收紧** | 仅接受本地 `ServiceFault`/`JobFault`/结构化 S1 Conflict；SQLite 按真实 errorcode 主码分类；未知来源统一 `INTERNAL_ERROR`，不按异常码机械映射、不借异常文本归责 |
| **F6**（终态摘要基础设施子项） | **基础设施子项已验证；业务仍开放** | 测试专用逐轮负载经真实 worker/Job/Store 事务/不可变 `result.get`/`result.page` 执行；摘要仅出现在首个非游标页；**E.2/E.5/G.4/FR-704 业务执行与页面仍保留未通过**，未登记为业务能力 |
| **I05 / I06** | **维持（未集成）** | I05 hooks 未提前复制，入口/打包脚本归属未冲突；I06 网关未接入、未复制 |

---

## 7. 十项原验收逐项判断

| # | 原验收要点 | 判断 | 关键证据 / 边界 |
| --- | --- | --- | --- |
| 1 | 常驻协调器与主进程监督、hello 协商、registry 原始字节 SHA、只开放已实现能力、同一会话多次 health 复用同进程、TS/Python 双端同步 v2、v1 骨架与旧组合显式不兼容、修正旧注释 | **通过** | `EngineSupervisor` 会话复用 + registry 原始字节 SHA 核验；`hello` 协商返回 `selectedVersion/engineSessionId/capabilities/limits/registryHash`；`capabilities` 仅含 `v2Runtime` 已实现方法（测试任务不登记为产品能力）；`productRuntime` 不宣称测试任务；1015 + 630 全绿覆盖双端一致性 |
| 2 | 严格 JSONL reader（拆包/粘包/跨 chunk UTF-8、多字节、坏 JSON、未知方法、重复 ID、嵌套重复键、无交集、超长未终止帧、连续超限 chunk、终态后 chunk）、追加前字节上限、stdout 只协议且及时 flush、stderr 有界脱敏、双端消费同一规范与公共正反例 | **通过** | `protocol.py`：`JsonlReader` 追加前按字节上限拒绝并清理 pending；`decode_frame` 深度 32、重复键拒绝；共享原始帧语料覆盖 UTF-8 每个拆分点、粘包/CRLF、嵌套重复/转义同名键、深度、数值、非法 Unicode、终止后丢弃；`__main__.py` 仅在初始化失败时输出固定 `ENGINE_SESSION_FAILED`；父 stdin 保持开启时 fatal 干净退出（exit 0、stderr 空） |
| 3 | 独立 requestId、全局持久 jobId/operationId、可替换 session/subscription、seq 与项目归属联合校验、并发与乱序关联、未知/重复/旧会话/旧项目/旧订阅响应不结算新请求也不污染 UI | **通过** | `coordinator.request` 校验 id/方法/信封字段集；`jobId`/`operationId` 由 `job_store` 持久化；订阅可替换且绑定 `engineSessionId`；`_notify` 以 `stateVersion` 单调推进 + `seq` 递增；旧会话 unsubscribe 守卫；renderer 以代次/项目/任务/输入/stateVersion 校验早到事件 |
| 4 | 有界队列/全局并发/项目单 writer、只读任务绑定不可变快照、启动/**握手独立时间预算**/单请求/总时限/心跳/取消收尾/帧/队列/分页/内存分别有界、忙碌计算仍能处理取消与心跳、心跳不延长总时限、无总量只显示阶段、隔离 worker 故障不误终止其他任务、单 job 取消不杀协调器 | **通过（含 `R2-P1` 登记）**；其中**"握手独立时间预算"子项按弱形式成立、按声明值不成立** | 各项上界在 `resources.LIMITS` 集中声明；矩阵观测 `observedMainJobStates={failed:120, succeeded:12, cancelled:12}` 表明取消与失败未导致协调器整体退出；进度实测 `completed/total=None`；worker 故障隔离用例通过。**唯一例外**：`handshakeMs=5000` 仅在 inbox 瞬时为空时生效（`coordinator.py:638` 是唯一检查点，且写在 `except queue.Empty` 分支内）——空闲对照臂 5.1117s 自然退出证明该预算**确实存在且本应生效**；而持续 pre-handshake 流量下迟到的 `hello` 仍在 5.3928s 被接受（本人探针）、5.8886s 被接受（开发线探针），两者最晚可能截止分别为 5.0704s / 5.0823s ⇒ **该子项不得按"已验证成立"记录**；其余子项（队列/并发/单 writer/不可变快照/单请求与总时限/心跳不延长总时限/取消收尾/帧/队列/分页/内存有界、无总量只显示阶段、worker 故障隔离、单 job 取消不杀协调器）均成立 |
| 5 | job 状态只由协调器写入 S1 同一 SQLite 真相、正式数据/版本/所有权/失效/operation/job 提交证据同事务、持久 `operation_claims` 全局唯一且指纹完整、不得建立第二份权威终态、job 输入/确认/计划/范围/快照/参数/实现来源完整绑定 | **通过** | `job_store.py` 单一 SQLite；`operation_claims(operation TEXT PRIMARY KEY)` + 不可变触发器；`BEGIN IMMEDIATE` 内权威复验；claim 指纹覆盖全部输入维度；ADR 明示"不另存第二份权威终态"；矩阵 96 格逐格核对表哈希/状态/提交点 |
| 6 | 逐项运行 I03 的 S1 故障对账矩阵（提交前/事务中、磁盘错误、旧基线、响应丢失、取消与完成竞态、零轮取消、部分轮次取消/崩溃、末轮提交缺终态、终态后取消、迟到旧结果、真实依赖/集合变化）；先隔离/fence 旧 writer 再查同事务 marker；不以异常文本或最后轮编号猜成功；不自动重放；已提交历史不可改写 | **通过** | atomic 96/96、round 48/48 逐格只读 DB 捕获（本人独立复现 + 负对照）；kill 探针：已提交轮次 6 保留、无 operation marker、不重放；`reconcile_jobs` 死分支已删 |
| 7 | Python→主进程→业务命名 bridge→UI 保留 code/messageKey/受限 params/retryable；UI 按 PRD 8.6 给四段式；取消/过期/历史/不支持/失败/待对账分别表达；SQLite 按真实 errorcode 分类、未知异常安全兜底；不回传原值/路径/URI/堆栈/凭据；retryable 不是自动重放许可 | **通过** | `task-presentation.ts` 四段式固定模板；`task-progress.ts` 有界缓存；错误目录经 `errors.json` 统一；`safe_error` 限定参数；`retryable` 不触发自动重放 |
| 8 | 窗口重建后按 project/job 查持久权威状态与提交点、重建订阅、拒绝旧通知、不重发写任务；页面卸载仅解除订阅；覆盖 renderer 崩溃/无响应时已提交数据保留与恢复；原生可见/焦点/故障恢复须在隔离环境或授权时段 | **通过（原生一项边界已记录）** | `window-recovery.ts`/`task-service.ts` 的 `restoreOnce`/`reconcileMarkers` 走持久权威查询并重建订阅；早到事件有界缓冲 ≤8 条/≤1MiB；原生证据（独立 Docker/Xvfb/Openbox）含外部 `xdotool/XGetInputFocus` 焦点与真实 dialog 字段，源码与包内两份 SHA 匹配。**未在宿主复现，远端 CI 仍必跑** |
| 9 | 与 U1 M0 身份/依赖/分页及 I05/I06 已批准边界对齐；资源投影/确认/来源读取不信任 renderer 自报；测试专用任务不登记为已实现能力；验证基础设施的真实 Store 提交与轮次证据不得换成内存 mock；定义集合与真实依赖从权威快照计算并在提交/发布边界复验 | **通过** | `has_operation_claim` 为 advisory、权威复验在 `BEGIN IMMEDIATE` 内；`job.create` 输入绑定完整指纹；测试任务仅在显式可信测试启动下创建、标 `I04-test-rounds-v1`；矩阵逐格捕获真实 SQLite（`mode=ro` + `query_only`）；依赖向量参与指纹；I05/I06 未接入 |
| 10 | ADR-0003 采用/修订结论须基于真实运行证据；依赖/协议资源打包按唯一规范显式纳入并核验包内 SHA，不依赖源码 checkout 路径 | **通过** | ADR 结论段引用真实子进程/SQLite/传输/隔离窗口探针，并明示"Linux RLIMIT_AS、Windows JobObject、Darwin RSS 采样分别验证；Darwin 不是硬上限"等边界；macOS/Linux 两平台 `resources.json` `frozen=true`，9 项资源 SHA 与源码逐字节一致；两平台包内 12 项 runtime probe exit 0；资源清单 CLI 在临时工作目录执行，不借源码 checkout 找回资源 |

---

## 8. 无桌面打扰、隔离资源与额度（Goal 第九节）执行声明

1. **未启动宿主 GUI**：未在用户当前桌面启动、显示、聚焦或重建 Electron/e2e/native/HMR/产物窗口；未自动点击或 Raise 审查应用；未在宿主运行 `npm run test:e2e` 类命令。
2. **隔离验证**：所有本人执行均落在唯一 ignored 目录 `build/I04-review-MiniMax-M31Flash-C2/`（源码 export、pytest `--basetemp`、`-o cache_dir`、矩阵证据目录、探针脚本与结果）；**共享 `out/build/release` 未写入**，符合 ZCode 的共享输出预约。
3. **无失败掩盖**：所有失败与工具性错误原样保留（见 §3.2 末段），未降低断言、未替换测试、未跳过原要求、未因结果不符而换模型。
4. **模型与思考**：全程保持派发指定的 M3.1-Flash / xhigh，未因效率或额度更换模型或降低思考设置。
5. **额度**：本轮**未出现额度告警、rate/usage-limit 错误或服务故障**，因此未触发任何重置、购买或额度恢复流程；未绕过逐次确认（本次无 `consume_usage_reset` 类操作）；未把"未观察到底额错误"解释为可任意消费。
6. **未新建 Goal/thread**：本轮为既有审查任务的续接，未新建 Goal、未创建子会话、未把未完成审查记为通过。
7. **证据完整性**：新反例（`R2-P1`）保留了原始脚本、原始 JSON 结果与退出码；矩阵证据保留了 `summary.json`/`cases.jsonl` 三组（正对照/负对照/CI 同款）；迟延握手复现保留 `probe_late_hello.py` + `probe_late_hello.json`；开发线自有探针的 7 个文件原样保留在受审目录 `build/I04-evidence/handshake-independent-c2/`（本人只读，未修改、未删除）。
8. **收到新增独立证据后的行为**：未因此更换模型或降低思考设置、未放宽任何断言、未把开发线结论当作通过依据；本人以自写 harness 独立复现后才更新报告，并在报告修订记录中标明 R0→R1 的变化点。

---

## 9. 最终结论

**结论：通过（Pass）** — 针对候选 `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500 → 0462e0825f3bda2774ce5d43f4422327f2d5fbd9`（93 文件，完整性经本人逐字节复核）。

判定依据：

1. 历史 C1 的全部阻断级问题（`P1-1`、`P1-2`、`P1-3`、`B1`）经机制级读码与本人独立可复现运行双重确认关闭；其余 15 项已关闭，`Z3` 与 I03 `O1`/`O3`、I01 `R6` 维持原"延期/开放"登记，未被上调也未被略过。
2. 十项原验收在本候选上均有实际证据支撑；无占位界面、测试替身或 spike 被当作已实现产品能力。
3. 本轮新增 1 项 **P2 非阻断** 发现 `R2-P1`（握手独立时间预算在持续 pre-handshake 流量下不成立，C1 遗留、非 C2 回归、影响有界、无数据/权限/授权影响）。该发现现已由**两条互相独立的 harness 互证**：本人自有探针（迟延 `hello` 于 5.3928s 被接受，超出最晚可能截止 5.0704s 至少 0.3224s；空闲对照 5.1117s 自然退出）与开发线自有探针（5.8886s 被接受，超出 5.0823s 至少 0.7275s；空闲对照 5.1261s 自然退出）。已附修复建议（含"截止时刻不得因被拒请求续期"与回归用例要求），要求在新候选中修复并重走双方全范围复审，或明确延期并登记理由；**在闭环前，不得声称"握手独立时间预算已验证成立"，原验收 #4 该子项只能按弱形式（请求数上限）表述**。该项不构成阻断，不影响本轮通过判定。
4. 本结论**仅覆盖候选在本地隔离环境中的可复现范围**。以下仍未验证、且仍是双方通过后 push 与正常合并前的必经门禁：远端三平台 CI、实际 push、PR、CI 全绿、正常合并、远端核验、签名安装、干净设备、生产环境，以及领域业务 E.2/E.5/G.4/FR-704。

**给开发线的必办项（合并前）**

1. **闭环 `R2-P1`（最高优先的合并前必办项）**：在**新候选**中修复 `coordinator.py` 的握手时限检查点（时限检查移出 `except queue.Empty` 分支、保持绝对截止时刻不因被拒请求续期、补"迟到 `hello` 必须被拒绝且空闲期限仍生效"的回归用例），并**重新走双方全范围复审**；或由处置方**明确延期并登记理由**。**不得沿用本轮通过结论**；在新候选通过前，也不得在任何状态或发布说明中声称握手独立时间预算已验证成立。
2. 保持受审实现/测试/配置/依赖/验收冻结；任何改动生成新候选并重新双方复审，不沿用本轮通过。
3. 推送前按仓库规则执行 `npm run check`、`npm run verify:sources`、`npm run test:e2e`（隔离/远程环境）与 `npm run package:dir` 包内同样例，并保留失败与限界。
4. 远端三平台 CI 与合并后远端核验的真实结果须单独记录，不得以本地数字替代。

---

*本报告由 MiniMax Code（M3.1-Flash / xhigh）独立只读复审产出；唯一写入为本文件。报告中所有"已验证"结论均可由 §3.2 的隔离环境命令复现，所有"未验证"事项均已在 §3.4 显式保留。*
