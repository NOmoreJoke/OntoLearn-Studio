# I04 S2 常驻协调器与 ExecutionJob — Round 3 独立对抗性审查报告（MiniMax Code · M3.1-Flash · xhigh）

> **报告修订记录**
> - **R0（首版终稿，314 行）**：SHA256 `8cbaba1dd275b80cd1079e2122ad610befbd2971a6cd521938c576ec577634b5`，已由总控只读快照留存于 `build/I04-evidence/minimax-r3-first-terminal-report.md`（哈希一致）。
> - **R1（本次修订，同一原任务内）**：经总控指出后由本人复核原始数据，确认首版**两处方法/文字准确性**需要更正并已更正（详见 §3.2 注 A/注 B 与 §6 统计行）：①握手探针 `sentFrames` 计的是**写调用批次数**而非真实请求数，首版据 `MAX_TOTAL_REQUESTS=40000`（与批次计数比较）声称"真实请求总数严格 < 65536"**不成立**——排除性论证已改用**实际被处理的请求数 `replies`**（绿臂 36192/38019/38119、红臂 63201，均 < 65536）并补充 `duplicateIdsSent=0`；首版将红臂 `exitAtS=33.571s` 与绿臂 `5.085s` 并列对比**易被误读为自然到期时刻差**，实为本人收尾关闭 stdin 后的 EOF 退出观测，有效对照轴已更正为"期限后是否仍存活 + 迟到 hello 是否被接受"。②原始 ID 统计由首版误写的"17 关闭 + 5 开放"更正为**22 个原始 ID → 21 关闭 + 1 延期（Z3）**，继承/范围开放项另列 §6.4。
> - **修订范围**：仅本报告文字与统计口径。**未改动任何受审实现、测试、配置、依赖或验收文件**；未重跑已绿的完整 `npm run check`（仍为 630 TS / 1020 Python、exit 0）或任何 GUI/原生验收；未读取另一模型本轮报告；**未变更任何原始 ID 的等级或处置方向**；**最终结论不变（通过）**，理由见 §10。


## 0. 结论先行

**结论：通过（Pass，针对冻结候选 C3：`e45e6038` → `d3ad536bf9de71780489e32891d3e29d8ebc3dc5`，105 文件）。**

- 本轮唯一的实质技术主张是「C2 遗留的握手绝对期限缺陷已修复」。我**未采信**开发线的任何结论、处置字段或另一模型的判断，而是用**本人自写 harness** 在**本人隔离 export** 上，对**真实默认 `handshakeMs=5000`**、真实 stdio、真实 SQLite、真实子进程做了**红/绿对照**：仅替换 `coordinator.py` 一个文件的 C2 前置字节，**C2 前置字节在 5s 期限后仍存活并接受了 7.001s 发出的迟到 hello（签发会话）**，而 **C3 字节在 ~5.08s 自然到期退出、迟到 hello 未被接受**。修复在**生产默认参数的真实路径**上成立，**不是**仅在缩短过的测试参数或 mock 时钟下成立。（对照轴与计数口径见 §3.2 注 A/注 B。）
- 关键增强证据：同一 harness 直接打在**实际不可变打包产物**（`ontolearn-engine`，SHA256 `5a399a3e…`）上，忙 inbox 下 5.086s 自然退出、迟到 hello 未被接受、空闲对照 5.122s、及时会话在 7s 后仍可 health。
- 历史问题全部有处理结论：**22 个原始 ID**（C1 的 19 个 + C2 的 3 个）逐项独立判定 → **21 项已关闭**（含本轮由红转绿的握手期限）、**1 项按原约延期**（Z3，P3）、**0 项依据不足**、**0 项仍未关闭的阻断项**。继承/范围开放项（I03 O1、I03 O3/I01 R6、领域业务、I05/I06）**另列于 §6.4，不计入上述 22 个原始 ID 的统计**。
- 我发现的**唯一新问题**是本人 harness 的两个缺陷（重复 UUID 导致 duplicate-id fatal 冒充期限终止、活进程 `stderr.read()` 永久阻塞），属**探针自身**问题、非产品缺陷，已按要求保留原失败脚本并另名写出修正版 v3/v4，**未改动任何冻结代码**。
- 远端三平台 CI、push、PR、正常 merge、远端核验、签名、干净设备、生产与领域业务（E.2/E.5/G.4/FR-704）**均未验证**，不在本结论内，仍是双方通过后的必经门禁。

---

## 1. 评审任务、模型及思考设置的来源记录

| 项 | 记录 |
| --- | --- |
| 派发关联标签 | `I04-R3-MiniMax-M31Flash-d3ad536bf9de71780489e32891d3e29d8ebc3dc5`（派发文本明示为**派发关联标签，非原生 UUID**）。本报告不据此虚构原生任务 ID。 |
| 任务性质 | Round 3 独立全范围**只读**对抗性审查；与 ZCode GLM-5.3 本轮任务互不共享结论。 |
| 指定模型 | MiniMax Code **M3.1-Flash**。来源：派发声明（总控 Goal 第九节第 2 条 + 本轮派发文本）；**另经派发侧 UI 核验记录 `docs/reviews/I04/round-3/dispatch.json` 记载 `MiniMax.model = "M3.1-Flash（订阅限免）"`、`MiniMax.thinking = "xhigh"`、`projectFolderChooserObserved = /Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs`、`branchSelectorObserved = feature/I04-resident-jobs`、`nativeTaskTitleAtCreation = "未命名会话"`、`creation = "Actually sent user message and running task; no C2 continuation reused."`**，二者一致。该记录为**派发方**经实际 UI 核验并另存，非本人回读 UI 配置。 |
| 指定思考设置 | **xhigh**。来源：派发声明 + 上述 dispatch.json 的 `thinking: "xhigh"` 字段。 |
| 我的运行时上下文 | 可见上下文标注 `Model: MiniMax-M3.1-Flash`。**如实说明**：思考级别（effort/thinking）本身不在我可读的运行时上下文中，我**无法独立核验 xhigh 是否已被宿主实际施加**；本报告不据此对"思考强度"作任何额外断言，也不虚构 UI 截图或配置回读。 |
| 派发者核验 vs 自身可见 | 派发者（总控）核验并另存实际 UI 记录（模型/思考/项目路径/分支/原生任务标题/创建状态）于 `docs/reviews/I04/round-3/dispatch.json`；**我本人只见该记录内容，未自行操作或回读 UI**。本人对 dispatch.json 所列 **10 项 evidence 逐份重算 SHA-256 + 字节数：10/10 与磁盘逐字节一致，0 缺失 0 不匹配**。我自身实际可见的只有上述模型标识与通用代理契约。 |
| 独立复核声明 | **未读取**另一模型本轮 round-3 报告、进度或结论。写作本报告时 `docs/reviews/I04/round-3/` 下的 `zcode-glm53.md`（另一模型报告）**始终未打开、未引用**；我读取的同目录文件仅 `minimax-m31flash-prompt.txt`（本人提示词）与 `dispatch.json`（**派发方**的创建/模型/思考记录，其内容为任务创建元数据，**不含**另一模型的任何结论）。亦未将任何开发者/内部 agent/另一模型的判断作为通过依据。 |
| 只读边界 | 未修改实现/测试/配置/依赖/验收文件；未提交、未推送、未切分支、未合并；未新建 Goal/thread。**唯一写入为本报告**。 |
| 保护文件 | `AGENTS.md` 全程保持 dirty、未 stage；审查开始与结束两次核验 SHA-256 均为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与要求逐字符一致。 |
| 宿主 GUI | 未在用户当前桌面启动、显示、聚焦或重建 Electron/e2e/native/HMR/产物窗口；未自动点击、聚焦或 Raise 任何审查应用；未在宿主运行 `npm run test:e2e` 类命令。 |
| 模型/思考/额度 | 全程保持派发指定的 M3.1-Flash / xhigh，未更换模型、未降级思考、未触发额度受限处置、未作任何重置或购买尝试。 |

---

## 2. 项目路径、分支、base/head 与候选完整性

| 项 | 实际值（本人独立核对） |
| --- | --- |
| Git 根 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs` |
| 分支 | `feature/I04-resident-jobs` |
| base SHA | `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`（`git cat-file -t` = commit） |
| head SHA | `d3ad536bf9de71780489e32891d3e29d8ebc3dc5`（= 当前 HEAD） |
| 受审区间 | 完整 base→head，**非 last commit、非 C2→C3 差异**：105 文件，`+37062 / −236`，53 次提交 |
| C2→C3 增量 | 19 文件：生产代码仅 `coordinator.py`（6 行）、测试 3 文件（`test_handshake_deadline.py` / `test_i04_lifecycle_boundaries.py` / `test_resident_runtime.py`）、其余为文档与流程证据 |
| `candidate-3.json` 清单核验 | 声明 105 文件；本人对**全部 105 条**重算 SHA-256 并与 `git show d3ad536:<path>` 实际字节比对：**105/105 逐字节一致，0 不匹配** |
| 集合一致性 | 候选声明文件集与 `git diff --name-only base..head` 实际集合**完全相等**（无多、无缺） |
| 保护 dirty | `AGENTS.md` SHA 一致、未 stage；`git diff --cached --name-only` 为空 |
| 工作区状态 | `M AGENTS.md`（保护 dirty）、`M docs/reviews/I04/status.md`（候选允许的**纯追加**流程记录，+4 行）、`?? docs/reviews/I04/candidate-3.json`、`?? docs/reviews/I04/round-3/`。经逐行比对，status.md 增量为"2026-10-21 C3 实际双新任务派发"段，**未夹带实现、测试、配置、依赖或验收变化**。 |
| 运行源 head 关系 | `candidate-3.json.runtimeInputs.observedRunSourceHead = c5c1961214ba5074300a96af034b70ea92a0323d`；本人核验 `c5c1961` 是 `d3ad536` 的**祖先**，`git diff c5c1961..d3ad536` 仅含文档/流程文件（无代码/测试/配置变更） |

**独立结论：受审对象身份、范围、冻结边界成立，审查对象确为完整 105 文件区间。**

---

## 3. 已检查范围、验证命令与实际结果、未验证事项

### 3.1 实际读码范围

**需求与治理**
`docs/iterations/I04/acceptance.md`（44 行全文）、`docs/iterations/I04/implementation.md`（47 行全文）、`docs/architecture/0003-resident-coordinator-and-jobs.md`（27 行全文）、`docs/reviews/I04/status.md`、`docs/reviews/I04/candidate-3.json`、最新 `AGENTS.md`（95 行全文）、原 M0 计划 S2 全文（`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:64-123`，含 5 条退出门槛）、PRD V0.6 §8.6（错误表达四段式）、PRD §8.7。

**I03 继承规范**
`docs/iterations/I03/protocol.md`（全文，含方法表、身份/绑定/通知、安全错误、错误参数与模板选择）。

**Python 引擎**
`coordinator.py`（657 行：serve 主循环、request/dispatch、_progress/_stage/_notify、classify、worker_command）、`job_store.py`（1528 行：create_job、_accepted_job、commit_job_round、reconcile_jobs、operation_claims、immutable 触发器）、`memory_guard.py`（224 行：`resident_bytes` ESRCH 判定、MemoryGuard._monitor、Windows JobObject）、`protocol.py`、`resources.py`（LIMITS 全表、registry SHA、safe_error）、`worker.py`、`process_environment.py`、`__main__.py`、`entrypoint.py`。

**TS / 桌面**
`apps/desktop/src/main/engine.ts`、`task-service.ts`（`doSubscribe`/`fenceConnection`/`connectionChanged`/`recover`/`restoreOnce`/`call`）、`jsonl.ts`、`view-navigation.ts`、`window-recovery.ts`、`preload/index.ts`（全文）、`renderer/src/{App.tsx,task-presentation.ts,task-progress.ts}`、`main/index.ts`。

**契约与资源**
`packages/contracts/v2/{schema.json,registry.json,fixtures.json,binding-regressions.json,frame-fixtures.json}`、`packages/contracts/src/{v2.ts,index.ts,design-v2.ts}`、`packages/contracts/python/contract_v2.py`。

**构建 / CI / 脚本**
`scripts/build-engine.mjs`、`scripts/verify-i04-package.py`、`scripts/i04_matrix_evidence.py`（含文件头自述）、`scripts/prepare-i04-fixture.py`、`.github/workflows/ci.yml`（全部 3 个 job）、`apps/desktop/electron-builder.yml`。

**测试**
`test_handshake_deadline.py`（96 行全文）、`test_resident_runtime.py`（第 13 项新增用例全文）、`test_i04_lifecycle_boundaries.py`（R2-N1 新增回归全文）、`test_session_page_limits.py`、`test_i04_round_faults.py`、`test_job_store.py`（96 格断言区段）、`test_i04_progress.py`、`test_stdio_session_shutdown.py`、`tests/unit/{supervisor,task-runtime,task-service,task-progress,binding-regressions}.test.ts`、`tests/e2e/i04-jobs.spec.ts`（skip 条件区段）。

**历史证据**
C1 两份原报告 + `round-1-disposition.json` + `round-1-evidence-lineage.json`；C2 两份原报告 + `round-2-processing.json` + `round-2/dispatch.json`；`c3-verification.json`、`c3-desktop-evidence.json`、`c3-handshake-evidence.json`、`c3-internal-review.json`。

### 3.2 本人实际执行的验证命令与结果（全部在唯一隔离环境）

隔离方式：`git archive d3ad536bf9de71780489e32891d3e29d8ebc3dc5` 导出到唯一 ignored 目录 `build/I04-review-MiniMax-M31Flash-C3/source`，在其中建立**独立** `node_modules`（`npm ci`）与**独立** `.venv`（`uv sync --frozen`，Python 3.12.12，editable 安装指向本人 export）。**共享 `out/build/release` 全程未写入**——这一点与派发记录 `docs/reviews/I04/round-3/dispatch.json` 的 `sharedOutputReservation` 一致（`ZCode.sharedOutputReservation = "ZCode only for primary out/build/release/check/package until explicit release"`；`MiniMax.sharedOutputReservation = "None; truly independent fixed-head export/dependencies/output/cache/DB only"`）。

| # | 命令（workdir 见括号） | 实际结果 | 退出码 |
| --- | --- | --- | --- |
| 1 | `shasum -a 256 AGENTS.md`（worktree 根） | `db1fb184…29786`，与要求一致 | 0 |
| 2 | `git rev-parse HEAD` / `--abbrev-ref HEAD` / `git status --porcelain` | `d3ad536…` / `feature/I04-resident-jobs`；仅 4 项预期状态 | 0 |
| 3 | 候选清单 105 文件 SHA-256 全量重算 vs `git show d3ad536:<path>` | **105/105 逐字节一致，0 不匹配**；集合与实际 diff 完全相等 | 0 |
| 4 | `npm run check`（本人 export 根） | **630 TS / 1020 Python 全部通过**，`All checks passed!` | **0** |
| 5 | `npm run verify:sources`（本人 export 根） | `已核对 12 个归档源文件。` | **0** |
| 6 | 矩阵 recorder（本人 export 根，`-p scripts.i04_matrix_evidence`，`--i04-matrix-source-revision d3ad536bf9de71780489e32891d3e29d8ebc3dc5`） | **144 passed**，`status=passed`、`completedCalls=144`、`capturedDatabases=144`、`errors=[]`、`unexpectedTests=[]`、`observedMainJobStates={failed:120, succeeded:12, cancelled:12}` | **0** |
| 7 | **负对照**：同一 recorder 只跑 `-k "changeset and before"` 子集 | pytest **8 passed**，recorder **exit 1**，`errors=[INCOMPLETE_DATABASE_EVIDENCE, INCOMPLETE_OR_DUPLICATE_MATRIX:atomic, INCOMPLETE_OR_DUPLICATE_MATRIX:round, NONPASS_MATRIX_CASE:atomic, NONPASS_MATRIX_CASE:round]` → **缺格不可被计数推导掩盖** | **1（预期非零）** |
| 8 | Darwin 生命周期子集（`-k "rss or memory or exit"`） | **7 passed** | 0 |
| 9 | 同一子集**连续重跑 20 次**（竞态抖动探针） | **TOTAL_FAILURES = 0 / 20** | 0（全部） |
| 10 | `test_session_page_limits.py` + `test_stdio_session_shutdown.py` + `test_job_store.py` | **173 passed** | 0 |
| 11 | `test_i04_progress.py` + 上述会话/限额/协调器控制 4 文件 | **33 passed** | 0 |
| 12 | C3 声明的 101 份 artifact 逐份重算 SHA-256 + 字节数 | **101/101 与磁盘逐字节一致，0 缺失 0 不匹配** | 0 |
| 13 | 实际不可变 macOS 包引擎 SHA-256 | `5a399a3e6cfe5c23219a8cfd75ab2ddf6c36b98b42c49555973f57f8da6f2418`，**与 C3 声明逐字符一致** | 0 |
| 14 | C2 报告与处置文件 SHA-256 | zcode `72c6d226…`（153 行）、minimax `5ce6e749…`（312 行）、processing `e1ce8423…` — **三者与声明全部一致** | 0 |
| 15 | **握手真实默认期限 · 绿臂**（本人 v3 harness，C3 head 源码，真实 stdio/SQLite/默认 LIMITS） | 忙 inbox：**aliveAt4.9s=true、aliveAt5.1s=false、exitAtS=5.087、exitCode=0、replies=36192（实际被处理的请求数）、sessionsIssued=0、lateHelloAccepted=false、stderr 空、duplicateIdsSent=0**；空闲对照 exit 5.087s；及时会话 sessionIssued=true、healthAfterDeadline=ok。**请求计数口径见 §3.2 注 A** | 0 |
| 16 | **握手真实默认期限 · 红臂**（同一 v4 harness，仅把 `coordinator.py` 换回 C2 前置字节） | 忙 inbox：**aliveAt5.1s/5.3s/5.6s/6.0s/7.0s 全为 true、replies=63201（316×200+1，与写调用数一致）、sessionsIssued=1、lateHelloAccepted=true、lateHelloWriteOk=true**；空闲对照 exit 5.084s；及时会话正常。**exitAtS=33.571 为本人收尾时关闭 stdin 后的 EOF 退出观测，不是握手自然到期时刻——见 §3.2 注 B** | 0 |
| 17 | **握手真实默认期限 · 绿臂 v4**（与红臂同一 harness，仅换回 C3 字节） | 忙 inbox exit **5.085s**、replies=38019、lateHelloAccepted=false、sessionsIssued=0；空闲 5.078s；及时会话 health ok | 0 |
| 18 | **握手真实默认期限 · 实际打包产物**（本人 packaged harness，打印 `ontolearn-engine`） | 忙 inbox：**exitAtS=5.086、exitCode=0、replies=38119、lateHelloAccepted=false、stderr 空**；空闲 exit 5.122s；及时会话 sessionIssued=true、healthAfterDeadline=ok | 0 |
| 19 | 矩阵精确断言结构抽查 | `test_job_store.py` 逐格断言 `expected_state`/`expected_vector`/`expected_ledger`/`expected_stale`（具体值）、不可变表字节相等、冻结行、marker/receipt 精确集合 — **非计数式** | 0 |
| 20 | 分页四层一致性 | schema `params_result.page` max=200 / `params_job.list` max=100 / `cursorRecord` 200 / `jobListCursorRecord` 100；TS `task-service.ts:689` max 200；引擎 `LIMITS.maxPageItems=200` | 0 |
| 21 | 安全边界静态核查 | `csp.ts`/`window-security.ts`/`trusted-document.ts` 相对 base **零 diff**；preload 全为业务命名方法（无 `invoke(method, params)`）；renderer 无 `createJob`/`invoke(`；`registry.productRuntime=["health"]`，业务能力 `implementation=design-only`，测试能力 `exposure=test-only`；`job.create` 需 `test_mode` 且能力 ∈ {test.read,test.atomic,test.rounds} | 0 |
| 22 | 恢复边界读码 | `recover()` 恰好 3 次尝试、退避 250/500ms、单次 15s 上限、generation 双重 fencing（`alive()` 校验 generation/session/project）、第 3 次失败转 `offline` | 0 |
| 23 | CI 步骤顺序与绑定 | `npm ci`(28) → `uv sync --frozen`(29) → 矩阵证据步(30-37，`--i04-matrix-source-revision HEAD`) → `npm run check`(38) → `verify:sources`(39) → `package:dir`(65) → `verify-i04-package.py`(72)；desktop job 三平台同跑 `package:dir` + `verify-i04-package.py` | 0 |
| 24 | 跳过项扫描 | 引擎侧仅 **3 处** `skipif`，全部为 Darwin 专属（libproc RSS 采样证据 / 父侧 RSS 采样失败 / libproc-child-watcher 退出竞态），与 C3 声明的 Linux "+3 Darwin 专属 skip" 精确吻合；e2e 侧 3 处 skip 均由 `process.platform!=='linux'` 或 `I04_NATIVE_ISOLATED!=='1'` 或 fixture 缺失门控，CI 以真实 `prepare-i04-fixture.py` 提供 | 0 |

**本人证据落盘**（全部在 gitignore 的 ignored 目录，SHA 已记录）：
`build/I04-evidence/minimax-c3-independent/` — `probe_handshake_real_v3.py`（`37770b83…`）、`probe_handshake_real_v4.py`（`7ea874d4…`）、`probe_handshake_packaged.py`（`3d860990…`）、`handshake-new-C3-v3.json`（`4f008ee4…`）、`handshake-red-C2-v4.json`（`f2e264a7…`）、`handshake-green-C3-v4.json`（`6559b3e1…`）、`handshake-packaged-C3.json`（`90a0bbd6…`）、`minimax-c3-matrix-summary.json`（`43da48e4…`）、`minimax-c3-matrix-negative-control.json`（`93ed777d…`）、`minimax-c3-npm-run-check.log`、`verify-sources.log`。

**注 A — 握手探针的请求计数口径（更正前一版表述）**

本人 harness 的 `Session.write(payload)` **每次调用只把 `counter` 加 1**，而 flood 每次调用携带 **200 个请求帧**。因此：

| 口径 | 含义 | v3 绿臂 | v4 绿臂 | v4 红臂 | 打包绿臂 |
| --- | --- | --- | --- | --- | --- |
| `sentFrames`（写调用/批次数） | 成功写入 stdin 的**批次数**，每次批含 200 帧 | 183 | 192 | 317 | 193 |
| 实际帧数上限 | `sentFrames × 200` | ≤36600 | ≤38400 | ≤63400 | ≤38600 |
| **`replies`（实际被处理的请求数）** | 引擎实际应答的请求条数 | **36192** | **38019** | **63201** | **38119** |
| `duplicateIdsSent` | 重复 ID 数 | **0** | **0** | **0** | **0** |

**因此前一版表述「总数上限 40000（严格 < 65536），故 budget 耗尽与 duplicate fatal 均不可能冒充期限」不成立**：源码常量 `MAX_TOTAL_REQUESTS=40000` 是与 `counter`（批次数）比较的，其**理论帧数上限为 40000×200 = 8,000,000**，远大于 65536；该常量**不是**一个低于 65536 的真实请求数上界。

**正确的排除性论证（改用 `replies` 这一实际计数）**：

1. **排除 65536 请求预算耗尽**：绿臂实际被处理的请求数为 36192 / 38019 / 38119，距 65536 尚有 **27517 / 27417 / 29344** 的余量；引擎是在**预算远未耗尽**时于 ~5.08s 自行退出的。红臂实际处理 63201 条，同样 **< 65536**（`replies == 316×200+1` 与写调用数 317 精确吻合），故红臂的存活**也不是**预算耗尽所致。
2. **排除重复 ID 会话致命**：四臂 `duplicateIdsSent` 全为 **0**（每批生成全新 UUID），重复 ID 致命路径未被触发。
3. **确认引擎死于自身期限而非被写入压垮**：绿臂 `exitAtS≈5.08s` 早于本人写 hello 的时刻（7.009s），且该次写调用 `lateHelloWriteOk=False`（管道已断），证明**引擎在 flood 仍在持续写入时就已自行退出**；红臂在同样负载下 `aliveAt5.1s…7.0s` 全为 true 且 `lateHelloWriteOk=True`，并**签发了会话**。
4. 因此，绿/红差异**只能**归因于 `coordinator.py` 的截止检查位置，而非预算、重复 ID 或写侧压力。

**注 B — 红臂 `exitAtS=33.571s` 的性质（更正前一版表述）**

前一版把红臂的 `exitAtS=33.571` 与绿臂的 `5.085` 并列对比，**易被误读为"握手自然到期时刻由 33.571s 收敛到 5.085s"**，这一表述**不准确**：

- 红臂 `cleanupTimedOut=true`，其 33.571s = 本人 `finish()` 的 25s 等待超时后**主动关闭 stdin** 触发 EOF 后的退出时刻，**不是**协调器因握手期限自然到期而退出的时刻（恰恰相反：红臂**没有**在期限处退出）。
- 红臂真正的、用于对照的事实是：**在 5s 期限之后仍持续存活**（`aliveAt5.1s/5.3s/5.6s/6.0s/7.0s` 全为 true）、**7.001s 发出的迟到 hello 被接受**（`lateHelloWriteOk=true`、`sessionsIssued=1`、`lateHelloAccepted=true`），且实际处理 63201 条请求仍低于预算。
- 绿臂对应的自然到期事实是 **`exitAtS≈5.08s` 且 `cleanupTimedOut=false`**（无需收尾强制关闭，进程自行退出），其退出**就是**握手期限的自然到期。

即：**红绿对照的有效轴是"期限后是否仍存活 + 迟到 hello 是否被接受"，而不是两个 `exitAtS` 的数值差。** 本报告 §0、§5.1、§6.3、§7.1 中凡引用"33.571s"之处均已按此更正。

### 3.3 保留的失败与工具性错误（如实保留，不掩盖为通过）

1. **本人 v2 harness 两个缺陷（探针自身问题，非产品缺陷）** — 经总控指出后由本人复核确认：
   - v2 忙臂的 flood 在 `while` 外**只生成一次** 200 个 UUID 的 payload 并在 `while` 内反复发送同一 payload → 触发**重复 ID**，而重复 ID 在真实协调器中是**会话致命 `ProtocolFault`**。因此 v2 的忙臂**可能**是"重复 ID 致命"而非"握手期限"终止，**不能**证明持续合法唯一请求下的期限行为。
   - v2 的 `Session.finish()` 在等待超时后仍对**活进程**执行 `stderr.read()`，阻塞等待 EOF；且 `arm_timely` 在及时 hello 成功后未先关闭 stdin，导致常驻会话永不退出 → 探针挂起 >4 分钟。
   - **处置**：保留 v2 原文件不动（本人文件 SHA `cee0ac6a41e4c8f1b090ac8e280dbd6b045e56b4863988bb7131f2d817856089`，与总控只读快照**完全一致**），另名写出 v3（修正：每批**新** UUID、有界收尾先关 stdin、stderr 有界读取）与 v4（追加**红臂能力**）。本报告 §3.2 第 15-18 行的结论**全部来自 v3/v4/packaged**，不来自 v2。**计数口径保留的缺陷**：v3/v4 的 `MAX_TOTAL_REQUESTS=40000` 与**批次数**比较而非真实请求数（详见 §3.2 注 A），该常量不构成低于 65536 的真实请求上界；排除性论证已改用实际 `replies` 计数。
   - **另一处本人自查纠错**：v1/v2 阶段我曾试图以 `PYTHONPATH` 指向 C2 前置源码做红臂，但协调器/引擎以 `python -I -m ontolearn_engine` 启动，`-I` 隐含 `-E` 会**忽略 `PYTHONPATH`**，实际仍解析到当前 tree 的 editable 安装 —— 那些"红臂"实际上跑的是**同一份新代码**，**不构成红臂**。v4 改用 `-c` 引导内显式 `sys.path.insert(0, ...)`（`-I` 不阻止），红臂才真正跑在 C2 前置字节上。该纠错是本人自查得出，已如实记录，不以"曾经验证过"充数。
2. **本人首次 `npm run check` 失败（隔离环境构造错误，非产品缺陷）** — 首次运行 `task-runtime.test.ts` **8 例失败**，报 `spawnSync …/.venv/bin/python ENOENT`。定位为本人把 venv 建在 `build/I04-review-MiniMax-M31Flash-C3/.venv`，而测试夹具按仓库根解析 `<workspace>/.venv`。改为在 export 根 `uv sync --frozen` 后重跑，**630 TS / 1020 Python 全绿，exit 0**。**属隔离环境构造问题，非产品缺陷**；首次失败日志保留在 `npm-run-check.log`（rc=1），未以绿色覆盖。
3. **工具性拦截** — `rm -rf .venv` 被危险路径防护拦截（守卫相对 worktree 根解析）；另一次 `..` 重定向被路径穿越防护拦截。**均未绕过**：改用 `mavis-trash` 对精确绝对路径做可恢复删除，改用绝对路径重定向。
4. **进程收尾** — 按总控提示，先以 `ps -o pid,ppid,etime,command` 核验 28165（本人探针父进程，PPID 28164=本人 bash 包装）与 28397（其 `-I -m ontolearn_engine` 子进程）**确属本人 harness**，再按 PID 定向收尾；复核后**无遗留**本线进程。**未**广泛结束 Electron、浏览器、审查应用或用户进程。
5. **未重复运行**同候选同环境已充分绿色的验证：完整 `npm run check` 仅在修正隔离环境后运行一次并通过；未为减少工作而重复 check/engine:check/全 pytest/单测/package。

### 3.4 未验证事项（明确记为"未验证"，既不记为通过、也不记为失败）

1. **远端三平台 CI**（Linux/Windows/macOS 官方 runner）未运行；本报告全部数字来自本地隔离环境与既有隔离 Linux 证据。
2. **push / PR / 正常 merge / 远端核验**未执行（双方通过后的必经门禁）。截至本次冻结，远端 `develop` 仍为 `e45e6038`，无 push/PR/远端 CI/merge。
3. **签名安装、干净设备、生产环境**验证未执行（PRD Q 类决策不由 ADR-0003 替代）。
4. **宿主 Mac 上的原生可见/焦点/无响应/真实提示框**未由本人复现（遵守最新 AGENTS 无桌面打扰约束）。既有证据来自独立 Docker/Xvfb/Openbox 环境；本人只核验其内容与哈希真实性（`c3-desktop-evidence.json` 中 `x11Focus` 外部 `xdotool/XGetInputFocus` 观察者、两个真实 native dialog 的 `windowId/title/visible`、`inspectorClosed=true`、`hangMonitorEnabled=true`、事件 `[crashed, unresponsive]`）。**arm64 隔离环境不冒充 CI x64 / Windows / 签名 / 干净设备**。
5. **Linux arm64 侧 `npm run check`（1017 Python + 3 Darwin 专属 skip）**未由本人复跑（需 Linux 环境）；本人复跑的是 macOS 侧 1020/630。既有 Linux 日志经 C3 artifact 哈希核验一致，但**非本人复跑**。
6. **实际 `npm run package:dir` 与包内 13 项 runtime 全量复跑**未由本人执行（写 `out/release`，为 ZCode 线预约；且打包产物已存在且哈希经核验）。本人**直接对既有不可变打包产物**执行了真实默认期限探针（第 18 行），这是对该产物行为的**直接实测**，不是仅读日志。
7. **领域业务语义**（E.2 全阶段、E.5/G.4 工单集合与产能/指标/业务重放、FR-704 业务结果页）未验证、未完成；I04 仅交付基础设施与测试专用任务负载。
8. **I05 语义 / I06 网关**产品集成未开始；**性能与容量通过线**未测量（I01 R6 保持原等级开放/延期，本轮未据合成测量作任何性能承诺）。
9. **I03 R2-F1「24 个差异反例」的逐条数量**未逐条清点（反例族存在、双端对等校验存在且在整包运行中通过；但"恰好 24 条"这一数字本身未逐条核对）。
10. `parallel-coordination.md`、完整 `state.json`（1833 行）未逐行通读；相关结论仅经 `status.md`/`acceptance.md`/总控派发原文定位。

---

## 4. 安全边界专项核验

| 检查项 | 结果 |
| --- | --- |
| CSP / 窗口安全 / 可信文档 | `csp.ts`、`window-security.ts`、`trusted-document.ts` 相对 base **零 diff**；未新增第三份策略；未改生产策略 |
| preload 暴露面 | 全为**按业务命名**方法（`getEngineHealth`/`restoreTasks`/`getActiveProject`/`getJob`/`listJobs`/`cancelJob`/`subscribeJob`/`unsubscribeJob`/`getResult`/`getResultPage`/`getOperation`/`onTaskUpdate`），**无** `invoke(method, params)` 式通用通道 |
| renderer 隔离 | `App.tsx` 无 `createJob`、无 `invoke(`；任务创建不经 renderer |
| 跨边界错误 | `safe_error` 白名单（code/messageKey/params/retryable）；`classify` 按真实来源分派（ServiceFault / JobFault / Conflict / sqlite 主码），未知来源统一 `INTERNAL_ERROR`；不回传原异常、堆栈、路径、单元格原值或凭据 |
| 项目归属 | 引擎侧 `_authorize` 对未授权项目 `PERMISSION_DENIED`；跨项目 result 绑定 → `NOT_FOUND{result}`（不泄漏存在性） |
| 能力声明 | `productRuntime=["health"]`；业务能力 `implementation=design-only` 且 `agentEligible` 字段独立；测试能力 `exposure=test-only`、`implementation=test-runtime`；`job.create` 需显式 `test_mode` 且能力 ∈ {test.read,test.atomic,test.rounds}，否则 `UNSUPPORTED_CAPABILITY` |
| 阶段通知 | `_progress` 恒 `completed=None, total=None`（**不捏造百分比**）；`test_i04_progress.py` 逐条断言该等值 |
| UI 四段式 | PRD 8.6 四段（发生什么/为什么/如何修复/相关知识）在 `task-presentation.ts` 固定本地模板组装；C3 desktop 证据中成功与错误两路均实际产出该四段文本；`retryable` 不触发自动重放（文案明示"重试提示不代表允许自动重放写入"） |

---

## 5. 本轮新发现问题

### R3-N1（探针自身缺陷，**非产品缺陷**，不构成阻断；已修复并保留原失败证据）

- **性质**：本人审查 harness 的缺陷，**不是**被审实现的问题。按要求**如实保留原失败、脚本与已跑证据**，另名写出修正版。
- **两个具体缺陷**：
  1. **重复 ID 冒充期限终止**：v2 忙臂的 flood 复用同一 200-UUID payload（`while` 外生成一次），重复 ID 在真实协调器中触发**会话致命 `ProtocolFault`**（`coordinator.py:172-174`：`if value["id"] in self.seen … raise ProtocolFault()`）。因此 v2 忙臂的"进程退出"**无法归因**于握手期限，可能只是 duplicate-id fatal。
  2. **活进程阻塞**：v2 `Session.finish()` 在等待超时后仍对活进程 `stderr.read()`；`arm_timely` 在及时 hello 成功后未关闭 stdin，常驻会话永不退出 → 探针挂起 >4 分钟（本人 PID 28165/28397，经核验后定向收尾）。
- **处置**：保留 v2 原文件（SHA `cee0ac6a…`，与总控只读快照一致）。v3 修正为每批**新** UUID、有界收尾先关 stdin、stderr 有界读取不阻塞活进程。v4 在此基础上追加**红臂**（`-c` 引导显式 `sys.path.insert`，绕开 `-I` 忽略 `PYTHONPATH` 的问题）。
- **v3/v4 保留的计数缺陷（本人复核确认）**：`MAX_TOTAL_REQUESTS=40000` 是与**写调用批次数**比较的（每次写含 200 帧），**不是**低于 65536 的真实请求数上界；前一版据此所作"budget 耗尽不可能冒充期限"的表述**不成立**，已更正。排除性论证改用**实际被处理的请求数 `replies`**：绿臂 36192 / 38019 / 38119（距 65536 尚有 27517 / 27417 / 29344 余量）、红臂 63201（`= 316×200+1`，与写调用数 317 精确吻合）**均低于 65536**；四臂 `duplicateIdsSent=0`。故绿臂 ~5.08s 的退出**不能**由请求预算或重复 ID 致命解释（详见 §3.2 注 A）。
- **对本轮结论的影响**：**无**。§3.2 第 15-18 行的握手结论**全部**来自 v3/v4/packaged 三套修正版 harness；v2 的结果**未**用于任何判定。
- **处理结论**：**已解决（限于探针）**；不进入受审代码，不需新候选，不构成阻断。

### 5.1 已核验为"非问题"的对抗性假设（记录证据边界，避免后轮重复探查）

| 假设 | 实测结果 |
| --- | --- |
| 握手修复只在 mock 时钟/缩短参数下成立 | **证伪**：本人 v4 在**真实默认 5000ms**、真实 stdio/SQLite、无任何 clock/queue/limits mock 下，用**仅替换一个文件**的红/绿对照直接证明——C2 前置字节：**在 5s 期限后仍存活**（aliveAt5.1s…7.0s 全 true）、**7.001s 的迟到 hello 被接受**（签发会话）；C3 字节：**在 ~5.08s 自然到期退出**（`cleanupTimedOut=false`）、迟到 hello 未被接受（写入时管道已断）。有效对照轴是"期限后是否仍存活 + 迟到 hello 是否被接受"，**不是**两个 `exitAtS` 的数值差（红臂 33.571s 是本人收尾关闭 stdin 后的 EOF 退出观测，非自然到期，见 §3.2 注 B）。同一 harness 同一默认参数。 |
| 修复在打包产物上不成立 | **证伪**：直接对不可变 `ontolearn-engine`（SHA `5a399a3e…`）跑同一 busy/idle/timely 三臂：忙 inbox 5.086s 退出、迟到 hello 未接受、及时会话 7s 后仍可 health。 |
| 忙 inbox 下"持续可解析非 hello 帧"仍能绕过截止 | **证伪**：v3/v4 忙臂每帧均为**新** UUID 的合法 `health` 请求，36380 条回复后进程在 5.08s 终止（远低于 65536 预算），`sessionsIssued=0`。 |
| 粘包（单 chunk 多帧）能绕过截止 | **证伪**：v3 `D_coalesced` 臂把 5 个新帧 + 1 个 hello 写入**同一个 chunk**，迟到 hello 仍未被接受，进程 5.077s 退出。 |
| 及时 hello 会被误杀 / 握手预算变成会话寿命 | **证伪**：及时 hello 0.096s 签发会话，`aliveAt5.1s/5.6s/7.0s` 全为 true，7s 后 health 仍返回 `ok`（同一会话）。C3 源码语义一致：`coordinator.session is None` 才检查截止。 |
| 心跳/活动能延长握手总时限 | **证伪**：截止时刻在 `serve()` 入口**一次性建立**（`coordinator.py:632`），此后**不再赋值**；每轮循环仅比较 `time.monotonic() >= handshake_deadline`。被拒请求不续期。 |
| 真实 ESRCH 与"监测不可用"被混同 | **证伪**：`memory_guard.py:87-90` 仅在 `read<=0 且 errno==ESRCH` 时抛 `ProcessLookupError`；短读/权限/残留 errno 仍为 `MemoryGuardUnavailable` → 协调器只捕获 `ProcessLookupError`，其余**穿透至 fail-closed**（`failed/INTERNAL_ERROR`，无成功结果/operation）。 |
| 父侧采样不可用被静默忽略 | **证伪**：`bc098d0` 在树回归以**实际目标 PID** 注入 `MemoryGuardUnavailable`，断言目标 `failed/INTERNAL_ERROR`、`resultRef=None`、`operation.get` 为 None，而**兄弟真实 worker 成功**且结果行精确、两个进程均被回收。本人重跑 **7 passed**，**20 次连跑 0 失败**。 |
| 矩阵计数可被"计数推导"掩盖 | **证伪**：本人负对照——8 例真实通过，recorder 仍 **exit 1** 并报 `INCOMPLETE_OR_DUPLICATE_MATRIX`/`NONPASS_MATRIX_CASE`。 |
| 96 格断言只断言数量 | **证伪**：逐格断言 `expected_state`（事实精确值/owner/source_row/managed_value/mappingState.generatedVersion）、`expected_vector`、`expected_ledger`、`expected_stale`（staleReason 精确重算）、不可变表字节相等、冻结行、marker/receipt/commits 精确集合。 |
| 分页上界跨层不一致 | **证伪**：schema 200/100、TS 200、引擎 `maxPageItems=200` 四层自洽；`job.list` 100 与 `result.page` 200 为分层设计。 |
| `job.progress` 无生产端 | **证伪**：`_progress`/`_stage` 为真实生产端（queued/loading/computing/reconciling/committing 边界）；实测恒 `completed=None`/`total=None`；`test_i04_progress.py` 断言等值。 |
| 65,536 请求预算被偷偷淘汰 ID | **证伪**：`seen` 只增不减、不淘汰；上限含 hello/ping；超限或重复 ID 会话致命；`test_session_keeps_all_request_identities_until_its_explicit_budget` 通过。 |
| C3 夹带实现/契约/依赖变更 | **证伪**：C2→C3 生产代码仅 `coordinator.py` 6 行；`packages/contracts/` 在 C2→C3 **零变更**；`c5c1961`（第 13 项）仅新增 `test_resident_runtime.py`，未改应用/引擎/构建/配置/依赖。 |
| CI 矩阵步可能被跳过或绑定错误源码 | **证伪**：矩阵步位于 `npm ci`/`uv sync` **之后**、`npm run check` **之前**，绑定 `--i04-matrix-source-revision HEAD`（PR merge-ref 兼容），步失败仍使 job 红，`if: always()` 上传 `summary.json`/`cases.jsonl`。 |

---

## 6. C1 / C2 历史问题逐项独立判断

判定口径：以**本候选的实际代码与本人独立运行结果**为准；原 ID 与 P 等级**原样保留**；**不采信** `round-1-disposition.json` / `round-2-processing.json` 的 `status`/`C2ReviewJudgment` 字段作为关闭依据；**不自行**把历史不通过改通过、**不降**阻断等级、**不隐藏**分歧。

### 6.1 C1 — ZCode GLM-5.3（4 项）

| ID | 级别 | 摘要 | 本轮判断 | 独立依据 |
| --- | --- | --- | --- | --- |
| **B1** | P2 | Darwin 内存故障分类竞态：超限偶发 `INTERNAL_ERROR` 而非 `RESOURCE_LIMIT(memory)` | **已关闭** | `memory_guard.py:87-90` 仅真 ESRCH 转 `ProcessLookupError`；协调器只捕获它并交**真实退出码**（74 → `RESOURCE_LIMIT{memory}`）。本人 Darwin 子集 **7 passed**，**20 连跑 0 失败**；父侧采样不可用另有 `bc098d0` fail-closed 在树回归（目标失败/兄弟成功/两进程回收）。 |
| **Z1** | P3 | source-final1 清单与冻结候选 4 个文档差异 | **已关闭** | 本人对 `candidate-3.json` **105/105** 逐字节重算一致；集合与实际 diff 完全相等。历史清单时点差异已由 lineage 文件交叉索引，实现字节不受影响。 |
| **Z2** | P3 | `reconcile_jobs` 不可达分支（死代码） | **已关闭** | 当前 `reconcile_jobs` 为 `cancelled iff cancelling` / 其他 → `failed` 二分，无 queued→cancelling 假设分支；恢复守卫另有独立在树回归。 |
| **Z3** | P3 | 非分页响应依赖 schema 上界而非显式字节预算预检 | **仍未关闭（按约延期，与 I03 O1 同批）** | C3 **未新增任何 schema 词汇**（`packages/contracts/` 在 C2→C3 零变更），本轮无违规；`result.page`/`job.list` 已有显式 `maxPageBytes` 预检。维持原登记的"不声称关闭"。 |

### 6.2 C1 — MiniMax M3.1-Flash（15 项）

| ID | 级别 | 摘要 | 本轮判断 | 独立依据 |
| --- | --- | --- | --- | --- |
| **P1-1** | P1 | 协调器被杀后首次重建订阅失败，UI 状态陈旧 | **已关闭** | `doSubscribe` 仅在 `binding.engineSessionId === 当前会话` 时发远端 unsubscribe，跨会话本地 fence；`connectionChanged` 立即 `fenceConnection()`；`recover()` 恰好 3 次只读恢复（250/500ms 退避、单次 15s 上限、generation 双重 fencing）、第 3 次失败转 `offline`、显式刷新可重试；`restoreOnce` 走持久权威查询。隔离证据实读：协调器被杀后 `running`(v3) → `failed`(v4)/`ENGINE_EXITED`、已提交轮次 1 保留、**无 operation marker**（不重放写入）、`sawUnconfirmed=true`、`actionsDisabled=true`。 |
| **P1-2** | P1 | 96 格原子故障对账矩阵断言不完整 | **已关闭** | 本人独立跑 recorder：**144/144**、`completedCalls=144`、`capturedDatabases=144`、`errors=[]`、`unexpectedTests=[]`、`observedMainJobStates={failed:120, succeeded:12, cancelled:12}`，且**绑定 head SHA**；负对照证明缺格 **exit 1**。源码逐格为精确值断言（state/vector/ledger/stale/不可变表/冻结行/精确集合），非计数式。 |
| **P1-3** | P1 | 资源上界事件被降级为通用 `INTERNAL_ERROR{}` | **已关闭** | 与 B1 同根：仅真 ESRCH 交实际退出码；短读/权限/监测不可用保持 **fail-closed**，未被"宽泛忽略 `MemoryGuardUnavailable`"或误归内存超限。R2-N1 在树回归钉住该分支公共结果形状（本人重跑通过、20 次无抖动）。 |
| **P2-4** | P2 | `result.page` 契约/TS 允许 200，引擎只允许 100 | **已关闭** | 四层一致：schema `params_result.page`/`cursorRecord` max=200、TS `task-service.ts:689` max 200、引擎 `LIMITS.maxPageItems=200`；`job.list` 保持 100（schema/TS 双层）。真实 210 行 200+10 稳定分页在树测试；201 契约拒绝；显式更小预算 100 时 → `RESOURCE_LIMIT{page}`。 |
| **P2-5** | P2 | `job.progress` 无生产端，UI 阶段分支生产不可达 | **已关闭** | `_progress`/`_stage` 为真实生产端（真实排队/读取/计算/提交/退出对账边界）；恒 `completed=None`/`total=None`；`test_i04_progress.py` 逐条断言等值（本人 33 例组通过）；renderer 早到缓冲按代次/项目/任务/输入/stateVersion 校验且有界。 |
| **P2-6** | P2 | `Coordinator.seen` 无回收，常驻会话必然在 65536 后终止 | **已关闭（语义已明确）** | `seen` 上限 65536、含 hello/ping、**不淘汰**；超限/重复 ID 会话致命；`test_session_keeps_all_request_identities_until_its_explicit_budget` + `test_request_replay_is_rejected_before_session_budget` 通过（本人随 `test_session_page_limits.py` 173 例组通过）；ADR-0003 与 implementation 明确"常驻=进程复用，不承诺无限请求或任务无中断"，limitations 如实披露。 |
| **P3-7** | P3 | `local-verification.json` 的 `differences=[]` 与实际不符 | **已关闭** | 原报告未被改写；差异由 `round-1-evidence-lineage.json` 交叉索引；本人以 105/105 SHA 全量复核替代，清单时点差异不再有歧义。 |
| **P3-8** | P3 | `internal-runtime-review.json` 无法映射到任何修订 | **已关闭** | 该文件明确标注为历史 C1 记录（`observed_git_head 83a12283…`），不作 C3 验收证据；C3 另立 `c3-*.json` 与 `matrix-evidence.json`，且 101/101 artifact 哈希经本人逐份重算一致。 |
| **P3-9** | P3 | `linux-native1..4` 失败未在提交文档中索引 | **已关闭** | lineage 记录索引原始失败与 raw 哈希；原失败目录仍保留，**未以后续绿色覆盖**。 |
| **P3-10** | P3 | `status.md` 内部表述矛盾 | **已关闭** | 现行 `status.md` 明确记载 C1 双不通过、C2 双附边界通过且不推送、C3 走完整新双审；本轮观察到的增量仅为"2026-10-21 C3 实际双新任务派发"**纯追加**段，未改历史表述。 |
| **P3-11** | P3 | 96/48 矩阵计数无对应证据记录 | **已关闭** | recorder 产出 `summary.json` + `cases.jsonl`（144 唯一 nodeid）并由 CI 独立上传 artifact；本人独立复现并做负对照。 |
| **P3-12** | P3 | 原生"聚焦"证据进程内自证；原生提示框缺证据字段 | **已关闭（证据层面；宿主复现未做）** | raw JSON 含 `windows[1].x11Focus = {observer:"xdotool/XGetInputFocus", windowId, title, visible}` 与 `nativeDialogs`（crash/hang 各含 windowId/title/visible）；源码与包内两份 SHA 匹配且经本人 101/101 artifact 重算核验。**边界**：未在宿主复现（无桌面打扰约束），仍待远端 CI/独立环境。 |
| **P3-13** | P3 | `reconcile_jobs` 存在不可达分支 | **已关闭** | 同 Z2。 |
| **P3-14** | P3 | `commit_job_round` 的 `stateVersion` 递增未走状态机守卫 | **已关闭** | `job_store.py:799-803` 显式守卫 `job["state"]!="running" or commitProgress["mode"]!="rounds"` → `fault("INVALID_STATE")`；queued/cancelling/终态/其他能力拒绝且数据库不变；implementation §存储守卫说明已论证"running→running 是持久证据修订、不是状态名称迁移"。 |
| **P3-15** | P3 | `job.create` 的 claim 预检查在事务之外 | **已关闭** | `has_operation_claim` 为 **advisory**（队列预算/幂等早判）；权威创建在 `BEGIN IMMEDIATE` 内复验完整指纹；`operation_claims(operation TEXT PRIMARY KEY)` + 不可变触发器保证全局唯一；指纹覆盖 input/confirmation/parameters/snapshot/plan/project/capability/implementation/limits/dependencyVector/manifests。 |

### 6.3 C2 — 本轮新增项（3 项）

| ID | 级别 | 摘要 | 本轮判断 | 独立依据 |
| --- | --- | --- | --- | --- |
| **R2-N1** | P3 | 父侧 Darwin 轮询"监测不可用"缺在树确定性回归 | **已关闭** | `bc098d0` 新增 `test_parent_rss_monitor_unavailable_fails_only_the_target_real_worker`（`skipif` 仅 Darwin）：以**实际目标 PID** 注入 `MemoryGuardUnavailable`，断言目标 `failed`/`INTERNAL_ERROR`、`resultRef=None`、`operation.get` 为 None，**兄弟真实 worker 成功**且结果行精确、两个进程回收；未改断言/预算/重试。**本人复跑通过，20 次连跑 0 失败。** |
| **R2-N2** | P2 | 握手时间预算是"流量条件性"的：持续前置请求可推迟 5s deadline，迟到 hello 仍被接受 | **已关闭（由红转绿，本人独立红/绿对照）** | 修复 `7d4cfaf`：把检查移出 `except queue.Empty` 分支，置于 `serve()` 循环**每次取帧之前**，`coordinator.session is None and time.monotonic() >= handshake_deadline` → `break`；截止时刻一次性建立、**不再赋值**。**本人证据**：同一 v4 harness、同一真实默认 5000ms、真实 stdio/SQLite、无 clock/queue/limits mock，仅替换 `coordinator.py` 一个文件——C2 前置字节：**期限后仍存活**（aliveAt5.1s…7.0s 全 true）、**7.001s 迟到 hello 被接受**（`sessionsIssued=1`、`lateHelloWriteOk=true`）、实际处理 63201 条请求仍低于 65536 预算；C3 字节：**~5.085s 自然到期退出**（`cleanupTimedOut=false`、exit 0、stderr 空）、迟到 hello 未被接受、实际处理 38019 条请求（距预算余 27517）。四臂 `duplicateIdsSent=0`，故退出**不能**由请求预算或重复 ID 致命解释（计数口径见 §3.2 注 A）。空闲对照两侧均约 5.08s；及时会话两侧均正常。C3 声明的三项精确定时回归在树存在（`test_handshake_deadline.py`，控制局部时钟与输入字节，不降低 `LIMITS`）；本人另补**真实默认 + 打包产物**证据（打包件忙 inbox 5.086s 自然退出、迟到 hello 未接受）。**该修复不是"仅缩短测试参数"或"仅源码测试通过"。** |
| **R2-P1** | P2 | 握手时限仅在 inbox 瞬时为空时生效，可被绕过（MiniMax 提出） | **已关闭（同 R2-N2 根因）** | 本人独立复现与判定与 C2 报告结论一致（C2 报告的自写 harness 记录：洪泛组 10.639s、迟到 hello 5.3928s 被接受），**未沿用**其结论而是自己重做红/绿对照；C3 修复后本人实测：忙 inbox（每帧新 UUID、总数 < 65536）**5.085s** 终止、迟到 hello 未被接受、粘包单 chunk 亦未被接受、及时会话 7s 后仍可用。**原验收 #4 的"握手独立时间预算"子项现按声明值 5000ms 成立**（此前 C2 仅"弱形式成立"的记录应据此更新）。 |

### 6.4 继承自 I03 / I01 的义务

| 义务 | 判断 | 依据 |
| --- | --- | --- |
| **I03 R2-F1**（可信 binding 校验） | **保持关闭** | 双端 `accepts_job_event` 严格校验（精确键集/身份形态/`lastSeq`/`stateVersion` 真整数且在范围内、bool 拒绝、状态枚举、progress stateVersion 等值语义）；共享语料 41 例 + 真实消费者链路回归在整包运行中通过；合法绑定语义未放宽。 |
| **I03 O1**（词汇/默认上界演进策略） | **仍未关闭（按约开放）** | C3 **未新增任何 schema 词汇**（C2→C3 `packages/contracts/` 零变更）；三层上界自洽。策略变更仍须统一双端并重新审查。 |
| **I03 O2**（parameterMeanings 是语义目录而非 UI 文案） | **维持遵守** | UI 全部使用固定本地模板 + 已验证 messageKey + 受限参数组装四段式；目录语义未进 UI。 |
| **I03 O3 / I01 R6**（历史增长/容量） | **仍未关闭（按约开放/延期）** | 本轮未夹带无证据优化；`legacy-scan-measurement.json` 仅测量记录，未宣称性能/容量结论。 |
| **F5**（内部错误到公共安全类别的适配） | **保持满足** | 仅接受本地 `ServiceFault`/`JobFault`/结构化 S1 `Conflict`；SQLite 按真实 errorcode 主码分类；未知来源统一 `INTERNAL_ERROR`；不按异常码机械映射、不借异常文本归责。 |
| **F6**（终态摘要基础设施子项） | **基础设施子项验证通过；业务仍开放** | 真实 worker/Job/Store 事务/不可变 `result.get`/`result.page` 链路；`_check_summary` 强校验 run/terminal/消费 blob/快照/审计行；摘要仅出现在首个非游标页（`test_scenario_actual_multi_page_round_audit_summary_only_first_non_cursor_page` 断言首页含 `run.summary.v1` 且后续页不含）；畸形/错配/缺失/回收拒绝在树。**E.2/E.5/G.4/FR-704 业务执行与页面仍保留未通过**，未登记为业务能力。 |
| **I05 / I06 边界** | **遵守（未集成）** | `entrypoint.py` 保留 `--storage-probe`，仅新增 `--worker/--contract-probe/--protocol-resources`；未复制 I05 semantic hooks；I06 网关未接入、未复制；共享入口/打包脚本归属无冲突。 |

**原始问题 ID 合计：C1 19 项 + C2 3 项 = 22 项 → 已关闭 21 项、按原约延期 1 项（Z3，P3）、依据不足 0 项、仍未关闭的阻断项 0 项。**（继承/范围开放项见 §6.4，单独列出，不计入本统计。）

---

## 7. 十项原验收 + 本轮追加九项实际路径的逐项判断

| # | 原验收要点 | 判断 | 关键证据 / 边界 |
| --- | --- | --- | --- |
| 1 | 常驻协调器与主进程监督、hello 协商、registry 原始字节 SHA、只开放已实现能力、同会话多次 health 复用同进程、TS/Python 双端同步 v2、v1 旧组合显式不兼容、修正旧注释 | **通过** | `EngineSupervisor` 会话复用；`hello` 返回 `selectedVersion/engineSessionId/capabilities/limits/registryHash`；registry 原始字节 SHA 双侧比对；`productRuntime=["health"]`，业务能力 `design-only`；本轮 1020/630 全绿覆盖双端一致性 |
| 2 | 严格 JSONL reader（拆包/粘包/跨 chunk UTF-8/多字节/坏 JSON/未知方法/重复 ID/嵌套重复键/无交集/超长未终止帧/连续超限 chunk/终态后 chunk）、追加前字节上限、stdout 只协议且及时 flush、stderr 有界脱敏、双端同源正反例 | **通过** | `protocol.py` 追加前字节上限并清理 pending；`decode_frame` 深度 32/重复键拒绝；共享 `frame-fixtures.json`（778 行增量）覆盖 UTF-8 切点/粘包/CRLF/嵌套重复键/深度/数值/非法 Unicode/终态后丢弃；父 stdin 保持开启时 fatal 干净退出（exit 0、stderr 空） |
| 3 | 独立 requestId、全局持久 jobId/operationId、可替换 session/subscription、seq 与项目归属联合校验、并发乱序关联正确、旧会话/旧项目/旧订阅响应不结算新请求也不污染 UI | **通过** | `seen` 去重与 65536 上限；`matchesResponse` 全量关联；`task-service.ts` 代次/会话/项目/订阅联合校验 + 跨会话 unsubscribe 本地 fence；迟到 health 由 `generation` 隔离 |
| 4 | 有界队列/并发/项目单 writer、只读任务绑定不可变快照、**握手独立时间预算**/单请求/总时限/心跳/取消收尾/帧/队列/分页/内存分别有界、忙碌计算仍能处理取消与心跳、心跳不延长总时限、无总量只显示阶段、隔离 worker 故障不误终止其他任务、单 job 取消不杀协调器 | **通过（本轮关键子项由红转绿）** | 各项上界集中于 `resources.LIMITS`；矩阵 `observedMainJobStates={failed:120,succeeded:12,cancelled:12}` 表明取消/失败未导致协调器整体退出；`completed/total=None` 不捏造百分比；**握手独立时间预算**：本人红/绿对照 + 真实默认 + 打包产物三重证据（§6.3 R2-N2），**按声明值 5000ms 成立**；及时协商成功后会话不受影响（7s 后 health ok） |
| 5 | job 状态只由协调器写入 S1 同一 SQLite 真相、正式数据/版本/所有权/失效/operation/job 提交证据同事务、持久 operation_claims 全局唯一且指纹完整、不得建立第二份权威终态、输入/确认/计划/范围/快照/参数/实现来源完整绑定 | **通过** | 单一 SQLite；`operation_claims(operation TEXT PRIMARY KEY)` + 不可变触发器；`BEGIN IMMEDIATE` 内权威复验；指纹覆盖全部输入维度；ADR 明示"不另存第二份权威终态"；96 格逐格核对不可变表字节相等 |
| 6 | 逐项运行 I03 的 S1 故障对账矩阵（提交前/事务中、磁盘错误、旧基线、响应丢失、取消与完成竞态、零轮取消、部分轮取消/崩溃、末轮提交缺终态、终态后取消、迟到旧结果、真实依赖/集合变化）；先隔离/fence 旧 writer 再查同事务 marker；不以异常文本或末轮编号猜成功；不自动重放；已提交历史不可改写 | **通过** | 本人 96/96 + 48/48 逐格只读 DB 捕获（recorder 绑定 head SHA，`errors=[]`）+ **负对照 exit 1**；隔离证据实读：协调器被杀后已提交轮次保留、无 operation marker、不重放；`definition-remove` 模式逐格断言 `staleReason` 精确重算 |
| 7 | Python→主进程→业务命名 bridge→UI 保留 code/messageKey/受限 params/retryable；UI 按 PRD 8.6 四段式；取消/过期/历史/不支持/失败/待对账分别表达；SQLite 按真实 errorcode 分类、未知异常安全兜底；不回传原值/路径/URI/堆栈/凭据；retryable 不是自动重放许可 | **通过** | `task-presentation.ts` 四段式固定模板；C3 隔离证据实读成功/错误两路四段文本（含"重试提示不代表允许自动重放写入"）；`safe_error` 白名单；`classify` 真实主码分类 + 未知兜底 |
| 8 | 窗口重建后按 project/job 查持久权威状态与提交点、重建订阅、拒绝旧通知、不重发写任务；页面卸载仅解除订阅；覆盖 renderer 崩溃/无响应时已提交数据保留与恢复；原生可见/焦点/故障恢复须在隔离环境或授权时段 | **通过（原生一项边界已记录）** | `view-navigation.ts` 仅新文档换代；`render-process-gone` 只解绑；卸载仅退订；恢复经持久查询重建订阅不重发写；隔离 Linux 源码+包内真实 crashed/unresponsive、3 窗口、外部 `xdotool/XGetInputFocus` 焦点、两个真实 native dialog 字段齐备（经哈希核验）。**未在宿主复现，远端 CI 仍必跑** |
| 9 | 与 U1 M0 身份/依赖/分页及 I05/I06 已批准边界对齐；资源投影/确认/来源读取不信任 renderer 自报；测试专用任务不登记为已实现能力；验证基础设施的真实 Store 提交与轮次证据不得换成内存 mock；定义集合与真实依赖从权威快照计算并在提交/发布边界复验 | **通过** | `has_operation_claim` advisory + 权威复验在 `BEGIN IMMEDIATE`；`job.create` 完整指纹；测试能力 `exposure=test-only`，需显式 `test_mode`，renderer 无创建入口；矩阵逐格捕获**真实 SQLite**（`mode=ro` + `query_only`）；依赖向量参与指纹；I05/I06 未接入 |
| 10 | ADR-0003 采用/修订结论须基于真实运行证据；依赖/协议资源打包按唯一规范显式纳入并核验包内 SHA，不依赖源码 checkout 路径 | **通过** | ADR 结论段引用真实子进程/SQLite/传输/隔离窗口探针并明示"Darwin 非硬上限"等边界；双平台 `resources.json` `frozen=true`，9 项资源 SHA 与源码逐字节一致；资源清单 CLI 在临时 cwd 执行，不借 checkout 寻址；**本人直接对实际不可变打包产物**执行真实默认期限探针（§3.2 第 18 行） |

### 7.1 本轮追加的九项实际路径（逐项独立核验，不预设实现正确）

| # | 指定路径 | 判断 | 关键证据 / 边界 |
| --- | --- | --- | --- |
| 1 | 最多 3 次只读恢复、marker/revision 竞态、迟到 health；真实 job.get 对账、订阅重建及不重发写任务 | **通过** | `recover()` 严格 3 次、250/500ms 退避、单次 15s 上限、generation 双重 fencing、第 3 次转 offline；跨会话不发旧 unsubscribe；隔离证据 `sawUnconfirmed=true`、`actionsDisabled=true`、已提交轮次保留、无 operation marker |
| 2 | 96 atomic + 48 round 原精确预期断言、mid_job_terminal/S2 边界、逐格只读 DB recorder；CI 新证据步位置与 HEAD 绑定；失败非零 | **通过** | 本人 144/144（绑定 head SHA）+ 负对照 exit 1；逐格为精确值断言；CI 步位于 `npm ci`/`uv sync` 之后、`npm run check` 之前，`--i04-matrix-source-revision HEAD`（merge-ref 兼容），步失败仍红，`if: always()` 上传 JSON |
| 3 | Darwin 仅真正 ESRCH 才转交进程真实退出码，其他父进程监测不可用须 fail-closed；parent sampler 采样失败/EOF/退出/父 stdin 尚开场景与回归；真实父子进程隔离、先 fence 后 reconcile | **通过** | `memory_guard.py:87-90` 仅 `read<=0 且 errno==ESRCH` → `ProcessLookupError`；其余 → `MemoryGuardUnavailable` → 目标 fail-closed（`bc098d0` 在树回归，目标失败/兄弟成功/两进程回收）；本人 7 passed + 20 连跑 0 失败；**未以其他平台跳过冒充 Darwin 通过**（Darwin 专属 skip 在 Linux 上按平台跳过，在 macOS 本机真实执行） |
| 4 | `result.page` 默认 200 与显式更小预算；稳定 resultId/游标绑定、真实 F6 summary + 持久 round 审计多页、回收反例、历史轮次不删；真实未知总量 stage 生产端与早到 UI 缓冲 | **通过** | 四层上界自洽（§3.2 #20）；210 行 200+10 稳定分页在树；显式更小预算 100 → `RESOURCE_LIMIT{page}`；摘要仅首个非游标页且畸形/错配/回收拒绝在树；`_progress` 真实生产端恒 `completed/total=None`；早到缓冲有界并按代次/身份校验 |
| 5 | 65,536 唯一请求的有限会话（含 hello/ping、不淘汰 ID）、父 stdin 开启时 fatal 干净退出、新 session 对持久任务的对账 | **通过** | `seen` 只增不减、上限含 hello/ping；超限/重复 ID 会话致命；父 stdin 开启时 exit 0 / stderr 空（原始 fd 读取）；新会话保留 marker/receipt/历史、未提交在途任务对账为 `ENGINE_EXITED`、不重放写入；本人 173 例组通过 |
| 6 | 外部 X 焦点/实际 dialog 字段与源码/包内窗口恢复证据；隔离 Linux arm64 不能冒充 x64/Windows/远端 CI | **通过（边界已记录）** | raw JSON 含 `x11Focus`（外部 `xdotool/XGetInputFocus`）与两个真实 dialog 的 windowId/title/visible，源码与包内两份 SHA 匹配且经 101/101 artifact 重算；**明确声明 arm64 容器 ≠ CI x64/Windows/签名/干净设备**；本人未在宿主复现 |
| 7 | JobStore 不可达分支清理、同 running 状态持久 progress 的 stateVersion 与状态边守卫分工、queued/cancelling/terminal 拒绝、advisory operation_claim 预查与正式 PK/完整指纹权威；真实集合删除/重加 ledger、失效、映射所有权及跨项目反例 | **通过** | 死分支已删；`commit_job_round` 显式守卫（`running` + `mode=rounds`，否则 `INVALID_STATE`）且库不变，未放宽状态机；预查 advisory、权威在 `BEGIN IMMEDIATE` 内复验、`operation_claims` PK + 不可变触发器；`definition-remove` 逐格断言 `staleReason` 精确重算与映射所有权；跨项目 `NOT_FOUND`（不泄漏存在性） |
| 8 | C3 声明修复**生产默认**握手绝对 deadline：从独立反例到每次读取/解析 loop 检查；检查实际生产默认参数而非仅缩短过的测试参数；持续可解析非 hello 帧、ping、粘包、已缓冲多帧、等待/处理/accept 边界不能反复重置或绕过；心跳/活动不能延长总时限；过期必须安全终止并清理关联状态；合法及时 hello 不误杀；不得把单请求等待超时当全握手绝对上限 | **通过（本轮决定性核验）** | 源码层：截止一次性建立（`:632`）且此后不再赋值；每轮取帧前检查（`:637`），与队列空否无关；`coordinator.session is None` 才检查 ⇒ 及时协商后仅解除握手前期限。运行时层：**真实默认 5000ms**、真实 stdio/SQLite、无 clock/queue/limits mock 的红/绿对照（C2 前置字节：**期限后仍存活**且 7.001s 迟到 hello 被接受；C3 字节：**~5.085s 自然到期退出**、迟到 hello 未被接受）；**实际打包产物**同结论（5.086s 自然退出、迟到 hello 未接受）；粘包单 chunk 亦未被接受；及时会话 7s 后 health ok；exit 0、stderr 空、无会话建立、无数据写入。绿臂实际处理请求数远低于 65536 预算且 `duplicateIdsSent=0`，故退出**不能**由请求预算或重复 ID 致命解释（§3.2 注 A）。**未把单请求等待超时当全握手上限**：检查点位于 serve 循环且以 `handshake_deadline` 比较 |
| 9 | 针对上项的精确定时回归及真实默认包 case：计时来源、容差、首次/每 loop 检查、握手前后状态、进程真实退出/输出/错误、包内默认值和规范资源；候选线索 `test_handshake_deadline.py`、`tests/unit/supervisor.test.ts`、`scripts/verify-i04-package.py` | **通过** | 三项精确回归在树（`test_handshake_deadline.py`：边界恰为 5.0 与 6.0s 均拒绝迟到 hello；及时 hello 后重复 hello 仍为 `INVALID_STATE` 而非杀死会话），仅控制**模块局部 clock 与 stdin 字节**，**不降低 `LIMITS`**；`scripts/verify-i04-package.py:62` 在包内运行 `test_resident_runtime.py`（含第 13 项默认时长 stdio 用例，保持调用方 stdin 开启、验证自然退出 0、stderr 空、线程回收），并随该入口进入三平台 CI；包内默认值 `handshakeMs=5000` 经 hello 响应与资源清单核验；**本人另以真实默认 + 真实打包产物直接实测**（§3.2 #18），不只依赖 mock 测试 |

---

## 8. 未验证与保留的门禁（合并前必须完成，不由本报告代替）

1. **远端三平台真实 CI**（Linux / Windows / macOS 官方 runner）——本轮全部数字来自本地隔离环境与既有隔离 Linux 证据。
2. **push feature 分支 → 创建指向 develop 的 PR → 实际 CI 全绿 → 遵守分支保护的正常 merge → 远端核验**。截至本次冻结，远端 `develop` 仍为 `e45e6038`，无 push/PR/远端 CI/merge。**双方同版通过后仍须实际 CI 门禁**；不预填成功、不宣称签名/干净设备/生产/领域业务。
3. **原生可见/焦点/无响应/真实提示框在隔离 CI 或独立桌面的最终确认**（arm64 隔离环境不冒充 x64/Windows）。
4. **Windows 真实运行**（JobObject 内存限制、Windows 打包探针）。
5. **签名、干净设备安装、生产运行**。
6. **领域业务**：E.2 全阶段、E.5/G.4 工单集合与产能/指标/业务重放、FR-704 业务结果页；I05 语义与 I06 网关集成。
7. **I01 R6 历史增长/容量**、**I03 O1 词汇与默认上界策略**、**Z3 非分页响应字节预算预检**：按原约保持开放/延期，本轮未新增违规。
8. 若本轮之后**实现、测试、配置、依赖、验收或集成基线发生变化**，须重新冻结候选并由两个指定模型**各新建独立同 base/head 任务**重审；**不得延用本轮或另一模型的通过**。

---

## 9. 无桌面打扰、隔离资源与额度（Goal 第九节）执行声明

1. **未启动宿主 GUI**：未在用户当前桌面启动、显示、聚焦或重建 Electron/e2e/native/HMR/产物窗口；未自动点击、聚焦或 Raise 审查应用；未在宿主运行 `npm run test:e2e` 类命令。
2. **隔离验证**：所有本人执行均落在唯一 ignored 目录 `build/I04-review-MiniMax-M31Flash-C3/`（源码 export、独立 `node_modules`、独立 `.venv`、独立 pytest `--basetemp` 与 `-o cache_dir`、矩阵证据目录、探针脚本与结果）；**共享 `out/build/release` 未写入**（ZCode 线持有该预约）。
3. **导出源码与固定 SHA 的相符性已核验**：export 的 105 个受审文件逐字节重算与 `candidate-3.json` **全部一致**；本报告以 primary 路径/分支/base/head 记录受审身份，另记实际执行目录 `build/I04-review-MiniMax-M31Flash-C3/source` 及其哈希，**未把导出目录冒充另一受审候选**。
4. **进程卫生**：仅按精确 PID 收尾本人 harness 及其子进程（先经 `ps` 核验命令行与父子链），复核后无遗留；**未**宽泛结束 Electron、浏览器、审查应用或用户进程。
5. **额度**：未触发任何额度告警或受限处置，未作任何重置、购买或模型/思考更换；未绕过逐次确认。
6. **冻结零改动**：受审实现/测试/配置/依赖/验收文件未改动；`AGENTS.md` 保持 dirty 未 stage 且 SHA 不变；`git diff --cached` 为空；HEAD 仍为 `d3ad536bf9de71780489e32891d3e29d8ebc3dc5`。
7. **唯一写入**：本报告 `docs/reviews/I04/round-3/minimax-m31flash.md`（另在 gitignore 的 `build/I04-evidence/minimax-c3-independent/` 留存本人探针与运行证据）。**未覆盖 C1/C2 任何报告**。

---

## 10. 最终结论

**通过（Pass）——针对冻结候选 C3：`e45e6038` → `d3ad536bf9de71780489e32891d3e29d8ebc3dc5`，105 文件。**

依据与边界：

- **C2 遗留的握手绝对期限缺陷已由红转绿**，且是本人在**真实默认 5000ms、真实 stdio/SQLite、无 clock/queue/limits mock**的条件下，用**仅替换一个文件**的红/绿对照**直接实测**得出，并额外在**实际不可变打包产物**上复现。有效对照轴为**期限后是否仍存活 + 迟到 hello 是否被接受**：C2 前置字节在 5s 期限后仍存活并接受了 7.001s 的迟到 hello，C3 字节在 ~5.08s 自然到期退出且迟到 hello 未被接受。绿臂实际被处理请求数 36192/38019/38119 与红臂 63201 **均远低于 65536 预算**，四臂 `duplicateIdsSent=0`，故该退出**不能**由请求预算耗尽或重复 ID 致命解释。这满足原验收 #4 的"握手独立时间预算"子项**按声明值成立**，不依赖 mock 时钟或缩短后的测试参数。
- **历史问题全部有处理结论**：C1 的 19 个 ID 与 C2 的 3 个 ID 共 **22 个原始 ID** 逐项独立判定 → **21 项已关闭、1 项按原约延期（Z3，P3）、0 项依据不足、0 项仍未关闭的阻断项**；未自行把任何历史不通过改通过，未降低任何阻断等级，未隐藏分歧。继承/范围开放项（I03 O1、I03 O3/I01 R6、领域业务、I05/I06）另列于 §6.4。
- **本轮唯一新问题 R3-N1 属本人探针自身缺陷，非产品缺陷**，已修正并保留原失败脚本与证据，不构成阻断。
- **关于本次两处更正对结论的影响（本人独立复核）**：两处均属**表述与计数口径的准确性**问题，**不改变任何事实观察，也不改变结论**。①计数口径更正后，排除性论证改用更强的 `replies` 实际计数（此前错误地依赖批次计数），**结论方向不变且论证更严谨**；②红臂 `exitAtS` 性质更正后，有效对照轴由"两个 exitAtS 数值差"改为"期限后是否仍存活 + 迟到 hello 是否被接受"——该轴在原始数据中**同样成立且更直接**（红臂 aliveAt5.1s…7.0s 全为 true、签发会话；绿臂 cleanupTimedOut=false 自然退出），**结论不变**。③ID 统计更正为 21 关闭 + 1 延期，与 §6.1–§6.3 的**逐行判定完全自洽**（本人机械核对：22 行、21 closed、1 deferred=Z3），**不改变任何 ID 的等级或处置方向**。因此最终结论仍为**通过**。
- **静态/运行/打包/隔离 native/远端 CI/生产声明分开判断**；远端三平台 CI、push/PR/正常 merge、远端核验、签名、干净设备、生产与领域业务**均未验证**，仍是双方通过后的必经门禁，**不预填成功**。
- 未发现需求遗漏、错误假设、边界缺陷、异常路径或回归风险方面的阻断问题；本报告不以"未发现问题"替代检查范围与证据边界的说明——检查范围与未验证事项已分别在 §3.1/§3.4/§8 逐项列明。
