# I04 Round 2（C2）独立对抗性审查报告（ZCode / GLM-5.3）

## 1. 评审任务、模型及思考设置的来源记录

- 任务来源：总控派发的独立只读复审任务，派发关联标签 `I04-R2-ZCode-GLM53-C2-0462e08`（标签为关联标识，非原生 UUID）。完整审查提示词原文由派发方提供，附最新 AGENTS 无桌面打扰约束、Goal 第九节（效率/额度）、C1 两份不通过报告及 disposition/evidence-lineage 必读输入。
- 模型与思考设置：按派发声明为 ZCode GLM-5.3 / 最高思考，经派发 UI 新建任务核验；本人无法看见宿主 UI 配置，仅如实记录：本会话实际以独立只读审查身份执行，可见上下文为派发提示词 + 受审 worktree 实际文件 + C1 归档输入；不可见的设置不虚构、不自证。
- 审查纪律：未创建 Goal/线程、未实施、未提交、未推送、未切分支或合并；未在宿主 Mac 启动任何 Electron/e2e/native/HMR/产物 GUI，未自动操作审查 UI；未读取另一模型（MiniMax）本轮任何报告、进展或结论——本轮 `round-2/` 在我审查期间只存在两份派发 prompt 文件，MiniMax 报告尚不存在，其 prompt 我也未读取；未把开发者/内部 agent 判断当作通过依据（内部证据只作事实线索，全部独立复核）。
- 本报告为唯一指定输出；临时探针与日志仅在 gitignore 的 `build/I04-review-ZCode-GLM53-C2/`。

## 2. 项目路径、分支、base/head 与冻结保护核验

- 项目路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs`；分支 `feature/I04-resident-jobs`。
- base = `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`（与 `origin/develop` merge-base 核验一致）；head = `0462e0825f3bda2774ce5d43f4422327f2d5fbd9`（HEAD 实测）；完整区间 93 个文件（+33117/−236，66 新增/27 修改，41 次提交），非 last commit 或仅 C1 修复——与派发声明一致。
- `candidate-2.json` 与 Git 核验一致；对全部 93 个冻结文件重算 SHA256 **完全一致**；`runtimeInputs`（c2-runtime-inputs.json，122 文件）哈希一致。
- 保护文件：`AGENTS.md` 保持 dirty、未 stage，审查开始与结束时两次核验 SHA-256 均为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，与要求逐字符一致。
- 工作区状态：`M AGENTS.md` + 未跟踪 `docs/reviews/I04/candidate-2.json`、`round-2/`（派发明示允许）；哈希复核时 `status.md` 与冻结值一致，审查窗口内出现一次派发方追加（630 字节 C2 派发过程记录），经逐字节比对确认为对 HEAD 的**纯追加**，属明示允许的 append-only 流程证据，不改任何实现；其余全部冻结文件（含实现/测试/配置/依赖/验收）始终字节一致；原仓库 64 保护文件无差异（reconnect-verification.originalRepositoryProtection，未复跑但与本 worktree 无写路径冲突）。

## 3. 已检查范围、验证命令与实际结果、未验证事项

### 3.1 代码审查范围（实际读码）

- Python 全文：`coordinator.py`、`memory_guard.py`、`protocol.py`、`job_store.py`（1529 行）、`worker.py`、`process_environment.py`、`resources.py`、`__main__.py`（diff）、`entrypoint.py`（模式清单）、`contract_v2.py` 的 `accepts_job_event`。
- TS/桌面全文：`engine.ts`（EngineSupervisor）、`task-service.ts`（888 行）、`jsonl.ts`、`task-presentation.ts`、`task-progress.ts`、`preload/index.ts`、`view-navigation.ts`、`window-recovery.ts`；`App.tsx`、`main/index.ts` 关键区段（IPC sender/mainFrame/可信文档校验、tasks:update、render-process-gone 接线、阶段展示与卸载仅退订）。
- 测试精读：`test_job_store.py` 96 格矩阵区段（172–551 行，逐格断言全文）、`test_i04_lifecycle_boundaries.py` 全文（含 B1 竞态回归）、`test_session_page_limits.py`、`test_stdio_session_shutdown.py`、`test_memory_guard_exit.py`、`test_worker_parent.py`、`test_i04_round_faults.py` 参数化与子进程注入全文；`test_resident_runtime.py`/`test_coordinator_control.py`/`test_i04_progress.py` 测试名与职责清单；TS 测试以整包运行覆盖（未逐行读体）。
- 契约：`schema.json` 分页上界实测（result.page/cursorRecord=200、job.list/jobListCursorRecord=100）、`v2.ts` 与 `contract_v2.py` 的 `acceptsJobEvent` 逐条对等比对。
- 脚本/CI：`scripts/i04_matrix_evidence.py`（只读逐格 recorder 全头部与断言不变性声明）、`.github/workflows/ci.yml`（矩阵 recorder+source-revision、xvfb/openbox/xdotool 真原生、package 与包内恢复、artifact 上传）、`build-engine.mjs`/`verify-i04-package.py`/`entrypoint.py` 以 diff 范围与打包证据核对。
- 文档：`acceptance.md`、`implementation.md`、`ADR-0003`、`m0-checklist.md`（S2 仍未勾选）、`status.md` 尾部、`round-1-disposition.json`、`round-1-evidence-lineage.json`、C1 两份报告全文。

### 3.2 实际运行的验证命令与结果（本机无窗口）

**退出码记录方法更正（总控指出的执行记录缺陷）**：首轮运行采用 `命令 | tail -N; echo $?` 形式，所记录的 `PYTEST_EXIT` 等实为管道末尾 `tail` 的状态，不能证明被测命令退出码；输出摘要（passed 计数等）本身有效。已按指示在安全边界内**保留首轮原日志不改写**，并用完整输出重定向（`$?` 直接读自被测命令，无管道）重跑全部命令；两轮结果一致。退出码以重跑为准（`exitcode-rerun/summary.txt` + 各完整日志）。

| 命令 | 首轮输出摘要 | 重跑真实退出码（完整日志 `exitcode-rerun/`） |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q` | 1015 passed | **exitcode=0**（pytest.log：`1015 passed in 34.75s`，与冻结 macOS 记录一致） |
| `npx vitest run` | 630 passed / 15 files | **exitcode=0**（vitest.log：630/630） |
| `npm run lint` | 无告警输出 | **exitcode=0** |
| `.venv/bin/python -m ruff check .` | All checks passed | **exitcode=0** |
| `npm run typecheck`（三段） | 无错误输出 | **exitcode=0** |
| `npm run format:check` | All matched files use Prettier | **exitcode=0** |
| `npm run verify:sources` | 已核对 12 源 | **exitcode=0** |
| `npm run check`（聚合含 build） | 630 TS + 1015 Python | **exitcode=0**（check.log：`All checks passed!`、`1015 passed in 34.47s`） |
| 候选哈希复核 | 93/93 一致 + runtimeInputs 一致（§2） | —（非命令） |
| 证据哈希重算 | reconnect-verification 71 项 artifacts 全部字节一致；desktop-evidence 6 项 raw 引用全部一致；matrix `cases.jsonl`（144 行）SHA 一致 | —（非命令） |
| 矩阵证据结构核验 | 144/144 格 setup/call/teardown 全 passed；96+48 与参数化定义精确对应；终态分布符合设计（atomic：12 succeeded=after_commit×3 模式、84 failed；round：12 cancelled=cancel×6×2、36 failed）；pytestExitStatus=0、errors=[]、unexpectedTests=[] | —（非命令） |
| 分页上界三方核验 | schema 200/100/100/200 = 引擎 maxPageItems 200（可显式调小）= TS zod 200/100 | —（非命令） |
| **本人定向探针**（父侧轮询监测不可用） | 按 PID 注入 `MemoryGuardUnavailable`：目标任务 `failed/INTERNAL_ERROR/resultRef=None`（fail-closed），兄弟任务 `succeeded` —— 与实现声明一致；探针留存 `build/I04-review-ZCode-GLM53-C2/` | 探针退出码补正：原 `probe-guard-unavailable.log` 的 `PROBE_EXIT=0` 来自 grep 管道（不成立，两次探针失败时也为 0）。已对最终按 PID 探针单独补一次完整重定向运行，**真实 pytest returncode=0**（`exitcode-rerun/probe-guard-unavailable.log`：`1 passed in 0.19s`，含 FAILED_JOB/SURVIVED_JOB 输出；退出码另存 `exitcode-rerun/probe-exit.txt`，不并入八项 summary.txt）。原日志与两次探针自身失败记录保留不改写 |

### 3.3 证据文件审阅（读实际内容并独立复核）

- `reconnect-verification.json`：7 项 check 与派发声明一致（macOS 630/1015；隔离 Linux 630/1013+2 Darwin 跳过；源码/包内各 6 项桌面验收；双平台 package+12 runtime；双平台 144 格 recorder；sources 12）；limitations 六条如实（含"双审仍未完成、无 push/CI/合并、arm64≠x64/Windows、Darwin 非硬上限"）。
- `reconnect-desktop-evidence.json`：实读 coordinatorRecovery（真实 kill→sawUnconfirmed/actionsDisabled→reconnecting(attempt 0,1)→restored，已提交轮次保留、中断任务 failed=ENGINE_EXITED v4 不倒退）；healthDelivery（受控 IPC 顺序下迟到 success/error 均不能覆盖新连接状态，边界如实注明"不冒充实际引擎退出"，实际退出由 coordinator-kill 用例覆盖）；native（源码+包内，真实 crashed/unresponsive、inspectorClosed、hangMonitorEnabled、两个原生提示框 windowId/标题/可见性、外部 `xdotool/XGetInputFocus` 观察者）。
- `matrix-evidence.json`：见 3.2；negative 缺格运行 exit 1 的声明与 CI 独立 artifact 上传接线一致。
- `reconnect-internal-review.json`：自我标注"not the designated external dual-model gate"，仅作内部线索，我未将其结论当通过依据。
- 独立监督者 worktree `.tmp/review/memory-race/` 探针实读：旧码强制真实窗口 10/10 复现 `INTERNAL_ERROR`（B1 机制）；生产修复码 10/10 `RESOURCE_LIMIT(memory)` 且 `returncodeAtException=null`+errno ESRCH；monitor 故障子进程 exit 75 零输出。与我读到的在树回归互证。
- 历史 C1 证据（local-verification/native-source/native-packaged/internal-runtime-review）：经 `round-1-evidence-lineage.json` 绑定 ce6fd54（C1）来源并被 acceptance.md 指向 C2 摘要，未冒充 C2。
- **审查窗口内新增的独立握手证据**（`build/I04-evidence/handshake-independent-c2/`）：我独立读取 finding-summary.json 与 probe-default.json、审阅两个探针脚本源码确认无 clock/queue/limits/reader mock（真实生产 `__main__` + 真实 stdio/SQLite），并自行重算全部 6 项工件哈希、3 个源码哈希（对 candidate-2 与 `git show 0462e08` 双重比对）——**全部一致，反例运行在精确冻结字节上**。原始数据：44,401 个合法唯一握手前 health（5.300s 时刻抽样仍为 `HANDSHAKE_REQUIRED` 优雅拒绝）、hello 于 5.8098s 发出、5.8886s 成功协商（首响应 0.0823s ⇒ deadline ≤5.0823s ⇒ 迟到 ≥0.7275s，确定性非边界抖动）；空闲对照同源码父 stdin 开启 5.1261s 自然 exit 0；正例结尾显式 SIGTERM 收尾 exit 0，未冒充自然 deadline。结论见 R2-N2。

### 3.4 未验证事项（如实保留，不记为通过）

- 远端三平台真实 CI、push/PR/合并、Windows 真实运行、签名/干净设备/生产语义：按门禁属双审通过后的必经步骤，本轮不可得，不视为已验证。
- 本机未运行 `test:e2e`/Electron/打包产物启动（无桌面打扰约束）；其隔离 Linux 源码+包内证据已逐哈希核验并实读关键字段，但非本人复跑。
- `package:dir` 未由本人重跑：现有双平台包内证据哈希一致、打包管线自证据采集后无源变更（93 文件冻结核验），重跑无增量信息；如需可后续补跑。
- `test_resident_runtime.py`/`test_coordinator_control.py`/TS 测试体未逐行精读，以整包运行 + 名称/职责核对覆盖。
- B1 竞态的"自然发生"无法确定性重放（微秒级窗口）；本轮以在树真实窗口回归（test_actual_memory_worker_exit_precedes_asyncio_returncode_delivery）+ 独立探针 + 本人探针三重覆盖其机制。

## 4. 问题清单（本轮新发现）

### R2-N1（P3，非阻断，允许延期）：父侧 Darwin 轮询"监测不可用"分支缺在树确定性回归

- **位置**：`packages/engine/src/ontolearn_engine/coordinator.py:441-446`（轮询仅捕获 `ProcessLookupError`）、`packages/engine/src/ontolearn_engine/memory_guard.py:87-91`（短读/权限/无 errno → `MemoryGuardUnavailable`）。
- **触发条件**：darwin 轮询期间 `resident_bytes` 抛 `MemoryGuardUnavailable`（libproc 不可用、短读、权限），且 `process.returncode` 仍为 None。
- **行为与影响**：异常穿出到 `execute()` 的 `except Exception` → `fail_job(classify(...))` → 该任务 `failed/INTERNAL_ERROR`，不产生成功或 RESOURCE_LIMIT 误报（fail-closed，符合派发与 implementation.md"监测不可用不静默忽略"的设计）。数据安全、兄弟任务隔离均成立。**行为本身正确**；问题仅在树内没有一条确定性测试钉住该分支的公共结果形状（worker 自身监测故障有 exit-75 测试、真实 ESRCH 窗口有在树回归、`resident_bytes` 分类有单测，但"父侧轮询遇 MemoryGuardUnavailable → failed(INTERNAL_ERROR) + 隔离"无在树断言）。
- **证据**：本人探针（3.2 末行）首次以按 PID 注入验证该分支，passed；探针前两次失败的自身设计缺陷（全局 monkeypatch 误伤兄弟任务、任务过早完成）保留于日志，属探针问题非产品问题。
- **修复建议**：未来候选把本人探针（按 PID 注入）收编为在树回归；因涉及测试文件新增，须按冻结规则走新候选，不要求本轮处理。
- **处理结论**：**非阻断，允许延期**。设计语义已文档化且有独立证据，缺的只是防回归钉子。

### R2-N2（P2，重要，须在下一候选修复；非阻断本轮）：引擎侧握手时间预算是"流量条件性"的——持续前置请求可无限期推迟 5s 握手 deadline，迟到 hello 仍被接受

- **位置**：`packages/engine/src/ontolearn_engine/coordinator.py` `serve()` 主循环（冻结版 632–647 行）：`handshake_deadline` 仅在 `except queue.Empty` 分支内检查；`request()` 的 hello 路径无 deadline 检查。
- **触发条件**：父进程在握手前以满速率持续发送合法唯一请求（每个均得到优雅 `HANDSHAKE_REQUIRED` 错误响应，非会话致命），inbox 永不排空 → deadline 检查被饿死；一旦停止流量，下一次空闲 tick 即正常强制执行。
- **影响**：引擎侧的握手独立时间预算（`LIMITS.handshakeMs=5000`）在持续流量下不成立：未认证会话存活时间不再有独立墙上时钟上界，只受 65536 唯一请求预算（数量界，非时间界）与帧预算约束；期间引擎持有 DB writer lease、持续做有界拒绝工作。**无数据/完整性/安全影响**：握手前一切非 hello 方法均被 `HANDSHAKE_REQUIRED` 拒绝，无任何能力或项目数据访问；触发者只能是受信本地父进程（stdio）；空闲路径的 deadline 强制执行正常（5.1261s 自然退出）。**产品实际接线不受影响**：EngineSupervisor 预握手只发送 hello，且其 `startupTimer` 与 hello `send()` 超时均为绝对 setTimeout（不随子进程流量推移，我已自查 engine.ts 确认），系统级握手在实际交付链路中仍有绝对时间界——该洞只削弱引擎自身的纵深防御预算。
- **证据**：`build/I04-evidence/handshake-independent-c2/`（§3.3 末条：方法学、哈希、原始数据均经我独立复核）；代码路径在冻结字节上由我逐行确认。
- **修复建议（须新候选 + 按冻结规则重审该变更）**：在 serve 循环每次取出 inbox 项之前（与队列空否无关）评估握手前绝对 deadline；保留原 deadline 不因被拒请求续期；截止前合法安全回复、正常已协商会话与受控清理语义不变；补一条确定性 busy-inbox 回归（可用显式短限配置，标注区别于默认时长正例；断言迟到 hello 被拒/传输关闭、空闲 deadline 与及时 hello 仍正常）。
- **处理结论**：**未关闭——P2，须在下一候选修复并回归**；非阻断本轮（评级为我在独立核验方法学、代码路径与产品接线后自行作出，评级依据与 C1 先例一致：仅受信父进程可触发、无数据/完整性影响、冻结测试与 CI 不受影响、空闲语义正确、修复已按冻结规则排期另线新候选——严格于 C1 对 P2-4 的非阻断先例，后者当时存在真实产品可达路径）。

### 已验证为非问题的对抗性假设（记录证据边界，不编造问题）

- "ESRCH 修复过宽，把真内存超限吞成静默"——证伪：仅 `read<=0 且 errno==ESRCH` 转 `ProcessLookupError`；短读(>0)/EACCES/残留 errno 均仍 `MemoryGuardUnavailable`（在树参数化单测含"前次调用残留 ESRCH 不得误分类"）。
- "65536 预算把 hello/ping 排除或偷偷淘汰旧 ID"——证伪：`request()` 对所有方法统一计数、`seen` 只增不减；在树测试真实打满 65536（含 hello）后第 65537 帧会话致命、重复 ID 先于预算拒绝。
- "阶段通知可能携带伪造总量/百分比"——证伪：`_progress` 恒 `completed/total=None`；UI 仅在 `total!==null` 时显示计数（生产端永不触发）；早到缓冲按代次/项目/任务/输入/stateVersion 校验、终态清除。
- "旧会话订阅在新会话注销会再触发 C1 P1-1"——证伪：TS 仅在 `binding.engineSessionId === 当前会话` 时才发远端 `job.unsubscribe`，跨会话直接跳过（本地 fences）。
- "迟到 health 成功回复可覆盖新连接状态"——证伪：`health()` 在 resolve 后复查 `current(session)`，代次不匹配抛 `ENGINE_EXITED`；桌面证据（受控 IPC 顺序）双端一致。
- "矩阵 recorder 可能改测试/放宽断言"——证伪：插件声明+代码头核验不改任何测试/超时/重试；只读连接（mode=ro/query_only/authorizer）；缺格负例 exit 1。
- "源/包 health 证据同哈希系复制"——证伪：该 JSON 只含确定性 UI 字符串（1559 字节无 UUID/时间戳），内容合理；native/disconnect 等其余 raw 哈希源码/包各自不同。
- "R2-N2 使实际产品的握手失去时间界"——证伪：EngineSupervisor 预握手只发送 hello，其 `startupTimer` 与 hello `send()` 超时为绝对 setTimeout、不因子进程流量推移；系统级握手在实际交付接线中仍有绝对时间界，R2-N2 仅削弱引擎侧纵深防御预算。

## 5. 历史问题逐项关闭判断（C1 全部 18 项 + I03 继承）

| 编号 | 本轮判断 | 依据（独立复核，不引用开发者结论） |
| --- | --- | --- |
| B1（P2 阻断） | **已关闭** | `resident_bytes` 仅真实 `read<=0+errno ESRCH` → `ProcessLookupError`；coordinator 仅捕获它并交给真实退出码（74→RESOURCE_LIMIT(memory)）。在树确定性竞态回归：真实 libproc 采样观测 `(ESRCH, ESRCH, returncode=None)` 后最终按实际 exit 74 分类且兄弟任务成功；独立监督者探针旧码 10/10 INTERNAL_ERROR vs 修复码 10/10 RESOURCE_LIMIT；我的按 PID 探针验证监测不可用 fail-closed。本机 1015 全过含原失败测试 |
| P1-3（P1 阻断） | **已关闭**（与 B1 同根） | 同上；且未采用"宽泛吞掉 MemoryGuardUnavailable"或把监测故障误归内存超限，选择 fail-closed + 文档化（implementation.md §平台资源边界），符合"不机械映射未知来源"的 F5 要求 |
| P1-1（P1 阻断） | **已关闭** | 断连即时 fence（connectionChanged 校验 generation/session，disconnectedSession 去重）；`recover()` 最多 3 次只读恢复、250/500ms 间隔、单次 15s 竞速，超限 offline + 显式刷新重试；跨会话不发旧 unsubscribe；首次显式 restore 成功且无写重放（restored.count==7 断言）；marker revision 竞态由 `restoreOnce` 三读 + 受限 transition 交接处理（reconnect-internal-review revisionBefore/After 真实对账证据） |
| P1-2（P1 阻断） | **已关闭** | 96 格逐格断言：精确事实（owner/source_row/managed_value）、mappingState.generatedVersion、依赖向量与 versions 台账（含 definition-remove 计数保留）、staleReason 重算（expected_stale）、job_blobs/plans/confirmations/operation_claims 不可变表字节相等、jobs 冻结行、marker/receipt/commits/commit_evidence/snapshots 精确集合、二次 reconcile 幂等；48 逐轮格（0/1 已提交轮×6 点×4 故障）为真实子进程唯一写者 + 真实 SQLite READONLY（disk 分支）+ 持久取消；另测试明确"注入≠物理磁盘"并单列真实 READONLY 回归；144 格只读 recorder 双平台留证 |
| P2-4 | **已关闭** | 引擎 `maxPageItems=200` 与 schema/TS/游标一致（我实测四方）；job.list 维持 100；真实 210 行 200+10 分页、201 契约拒绝、显式预算 100 时 101→RESOURCE_LIMIT(page) 精确错误均有在树测试 |
| P2-5 | **已关闭** | coordinator 真实阶段生产端（loading/computing/committing/reconciling + 订阅时 queued 快照，seq=0 响应/seq=1 早到提示的设计有注释与测试）；恒 null 总量；TS 16 项有界早到缓冲（≤8 事件/≤1MB/代次与身份版本门控）；e2e 源码+包内真实"阶段：计算"断言 |
| P2-6 | **已关闭（按声明的有限会话策略）** | 65536 唯一 ID（含 hello/ping）、不淘汰、超限/重复会话致命；父 stdin 保持开启时 fatal 退出 0/stderr 空（os.read 原始 fd 读线程）；新会话保留 marker/receipt/历史、未提交在途任务对账为 ENGINE_EXITED、不重放写；ADR-0003 §决定显式记录该生命周期与不承诺无限会话；limitations 如实披露 |
| Z1 / P3-7 | **已关闭** | local-verification 增 provenanceClarification；round-1-evidence-lineage 原始 NUL 路径审计：0 缺失、5 差异（AGENTS+4 文档）；MiniMax 33-absent 原文保留并被事实性反驳，未改写其 Not-Pass |
| Z2 / P3-13 | **已关闭** | `reconcile_jobs` 死分支已删（`cancelled iff cancelling` else `failed`），恢复守卫独立在树 |
| Z3 | **按约延期（保留开放）** | 与 I03 O1 同批；本轮无 schema 词汇/预算扩张需求被违反 |
| P3-8 | **已关闭** | lineage 记录明确 observed_git_head 为分支尖端、8 文件哈希映射、整树不可重建的边界，未伪造主体 SHA，未以内部审查替代外部门禁 |
| P3-9 | **已关闭** | linux-native1..4 失败逐项登记（症状/原因边界/raw 哈希/trace 时间），laterSuccessDoesNotRewriteThisFailure=true |
| P3-10 | **已关闭** | status.md 现行段落明确 C1 双 Not Pass；历史段落标注时间点属性 |
| P3-11 | **已关闭** | matrix-evidence.json 144 格机器记录（含 per-cell 快照/表指纹/关键行）+ CI 独立运行上传 artifact；缺格负例 exit 1 |
| P3-12 | **已关闭** | e2e 用外部 `xdotool getwindowfocus/getwindowname/--onlyvisible` 校验第二个窗口真实可见+聚焦（不匹配即 throw）；原生提示框以外部可见窗口清单发现并记录 windowId/标题/可见性，crash+hang 两框断言；源码+包内隔离证据均有（本机未复跑，见 3.4） |
| P3-14 | **已关闭** | `commit_job_round` 显式守卫（仅 running+rounds，其余拒绝且库不变）+ 注释与 implementation.md §存储守卫说明论证"持久证据修订非状态名迁移"；合法轮次与回滚独立测试 |
| P3-15 | **已关闭** | 预查为 advisory 队列/幂等早判；权威创建在 BEGIN IMMEDIATE 内复验完整指纹并由 operation 主键强制唯一；绕过/指纹变更反例在树 |
| I03 R2-F1 | **保持关闭** | 双端 `accepts_job_event` 逐条对等（精确键集/身份/真整数范围/bool 拒绝/状态枚举/progress stateVersion 等值语义）；41 例共享语料 + 真实消费者（task-service receive→acceptsJobEvent→缺口对账）在整包运行中通过 |
| I03 O1 | 按约开放 | 本轮 schema 变更（null-session 分支、job.progress）为 C1 已审内容的延续，双端同源消费；未来词汇/默认上界演进仍须先统一再重审 |
| I03 O2 | 遵守 | `parameterMeanings` 零引用；UI 全部固定本地模板 + messageKey + 受限参数（`Number()` 收敛） |
| I03 O3 / I01 R6 | 按约开放 | 未夹带无依据优化；测量记录未做性能结论 |
| F5 | 保持满足 | producer 语义分类（ServiceFault/JobFault/Conflict/sqlite 主码）+ 未知兜底；B1 修复未引入机械映射 |
| F6 基础设施子项 | 范围内完成、边界如实 | 真实 worker/Job/Store/轮次/result.page 链路、`_check_summary` 强校验（run/terminal/consumption blob/快照/审计行）、摘要仅首页；E.2/E.5/G.4/FR-704 仍开放，文档不代完成 |
| I05/I06 边界 | 遵守 | `entrypoint.py` 保留 `--storage-probe` 并仅新增 worker/contract/protocol-resources；无 I05 semantic hooks、无网关接线；registry 中产品能力仍 design-only、`health()` 过滤只报 health |

## 6. 十项原验收的检查结论（摘要）

1. **常驻/协商/registry SHA/v1 不兼容**：通过。同 PID 多次 health（`ensure()` 会话复用）、registry 原始字节 SHA 双侧比对（主进程重读文件+hello 返回值+包内资源）、`PROTOCOL_VERSION=2`、无 v1 回退与旧组合显式拒绝、旧"M1 再设计"注释已由常驻实现替换。
2. **严格 JSONL**：通过。双端同源 frame-fixtures；两 reader 均追加前预检上限、CRLF、终态丢弃、深度/重复键/孤立代理/大数拒绝；冻结记录的 14 边界双端差分探针结论与代码一致。
3. **身份归属与关联**：通过。`matchesResponse` 全量关联、`seen` 去重、代次/会话/项目/订阅联合校验、乱序并发与旧订阅拒绝（NOT_FOUND 容忍语义正确化）、完整指纹反例在树。
4. **有界与资源**：通过（附 R2-N2 边界修正）。队列计入总时限、忙碌期 20ms 轮询可取消/心跳、心跳不延长总时限、stdin 阻塞/退出等待有界、单 job 取消不杀协调器、worker 故障隔离、父死亡守卫（真实 kill 探针）；内存项 B1 关闭（见 §5）；**引擎侧握手预算为流量条件性**（持续前置请求可推迟 5s deadline、迟到 hello 仍被接受，确定性反例在冻结字节上复现，见 R2-N2，P2 非阻断、须下一候选修复）——系统级握手在实际产品接线中仍由 supervisor 的绝对定时器保证有界，空闲路径的引擎侧 deadline 亦正常。
5. **唯一 SQLite/同事务证据/完整绑定**：通过。operation_claims 全局唯一、context 完整指纹、marker/receipt/终态同事务、immutable_* 触发器、receipt 不入 current、输入/确认/计划/依赖/实现来源完整绑定。
6. **S1 故障矩阵**：通过（按 3.4 边界）。96+48 逐格精确断言 + 真实 READONLY/持久取消/真实退出分支；lease→BEGIN IMMEDIATE→marker 对账、不猜成功不重放、已提交历史不可改写。
7. **安全错误到 UI 四段式**：通过。真实 errorcode 主码分类、未知兜底、无原值/路径/堆栈外传、固定模板四段式、retryable 不自动重放（文案明示）。
8. **窗口重建/崩溃/无响应**：通过（以隔离 Linux 源码+包内真实证据 + 哈希核验为准，本机未复跑）。仅新文档换代、卸载仅退订、持久查询重建订阅不重发写、外部 X 焦点与真实提示框字段齐备。
9. **U1/未来边界**：通过。分页预算四方一致、固定集合+持久游标（TTL/尺寸/绑定复验、回收不返回成功空页）、身份映射持久、确认只经可信侧 actor/permission、测试任务不登记产品能力（renderer 无创建入口）。
10. **ADR 采用与包内资源**：通过。ADR-0003 基于真实运行证据修订并保留边界（Darwin 非硬上限、不批准未来原生库）；PyInstaller 显式打包契约+锁、双平台包内 SHA 与源一致、临时 cwd 寻址。

## 7. 最终结论

**通过（针对冻结候选 C2：`e45e6038` → `0462e08`，93 文件）。**

- C1 的三项阻断（B1/P1-3 同根、P1-1、P1-2）**全部关闭**，且每项均有在树确定性回归与独立证据，我逐一独立复核（含本人定向探针）；P2-4/5/6 按声明关闭；Z1–Z3、P3-7…P3-15 关闭或按约延期；I03 继承义务（R2-F1/O1/O2/O3、F5/F6 基础设施子项、I05/I06 边界）满足或按约开放。
- 本轮新发现两项，均非阻断：**R2-N1（P3，允许延期）**——为父侧轮询监测不可用分支补一条在树确定性回归；**R2-N2（P2，重要，须在下一候选修复并回归）**——审查窗口内新增的独立实际证据（我已独立复核方法学/哈希/原始数据/代码路径）证明引擎侧握手 5s 时间预算是流量条件性的：持续合法前置请求可饿死 deadline 检查，迟到 ≥0.73s 的 hello 仍成功协商。非阻断依据：仅受信本地父进程可触发、握手前一切能力访问均被拒绝、无数据/完整性影响、扩展受 65536 请求预算约束、空闲路径与产品实际接线（supervisor 绝对定时器）的时间界均成立、冻结测试与 CI 不受影响；该评级为我对照 C1 P2-4/5/6 先例自行作出，不采用证据提供方的结论。
- **通过的含义边界**：仅指本冻结候选在本轮可执行的验证范围内满足原验收与继承义务。以下仍为后续必备门禁、未验证不视为通过：远端三平台真实 CI、push/PR/正常合并、Windows 真实运行、签名/干净设备/生产语义；本轮未在宿主启动任何 GUI。
- 上述结论独立作出，未参考、也未等待另一模型本轮任何报告或结论。

## 8. 资源与约束声明

- 本 ZCode C2 任务对共享 out/build/release 的 check/build/package 预约：首轮用毕后曾声明释放；应总控的退出码记录方法指正，为重跑验证**有界重新占用**（`exitcode-rerun.sh` 一次，含聚合 `npm run check` 与 build，全部真实退出码 0），**至此再次显式释放**，MiniMax 可按其独立输出环境使用。
- 全程未启动宿主 Electron/native/HMR/产物 GUI，未操作审查应用 UI，未读取另一模型本轮报告/进展/结论；探针与日志留存 `build/I04-review-ZCode-GLM53-C2/`（gitignore 内），含 guard-unavailable 探针源码与三次运行日志（含两次探针自身失败的原始记录）。
- 冻结文件零改动；`AGENTS.md` 保持 dirty 且 SHA 未变；本报告为唯一指定输出 `docs/reviews/I04/round-2/zcode-glm53.md`。
