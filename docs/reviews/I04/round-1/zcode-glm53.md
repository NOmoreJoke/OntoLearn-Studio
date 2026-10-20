# I04 Round 1 独立对抗性审查报告（ZCode / GLM-5.3）

## 1. 评审任务、模型及思考设置的来源记录

- 任务来源：总控派发的独立只读审查任务，派发关联标签 `I04-R1-ZCode-GLM53-C1-ce6fd54`（标签为关联标识，非原生 UUID）。完整审查提示词原文由派发方提供，并附最新 AGENTS 无桌面打扰约束与 Goal 第九节（效率/额度）要求。
- 模型与思考设置：按派发声明为 ZCode GLM-5.3 / 最高思考，经 UI 新建本任务派发；dispatch 过程证据（UI 哈希、双任务创建记录）由开发会话保存在 `round-1/dispatch.json` 并在 `status.md` 追加段声明。本人无法看见不可见的 UI 配置，仅如实记录：本会话实际以只读审查身份执行，上下文为派发提示词 + 受审 worktree 实际文件；未读取另一模型（MiniMax）本轮任何报告或结论（写作本报告时 `round-1/` 下尚不存在该文件，本人也未读取 prompts/dispatch 等派发过程文件内容）。
- 审查纪律：未创建 Goal/线程、未实施、未合并、未以开发者身份行动；未运行任何宿主 Mac Electron/e2e/native/HMR 或审查 UI 自动化；未修改冻结文件；临时验证文件仅位于 `build/I04-review-ZCode-GLM53/` 与 `/tmp`。

## 2. 项目路径、分支、base/head

- 项目路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs`
- 分支：`feature/I04-resident-jobs`；HEAD = `ce6fd54fd51bb16a6eda5f45d2675506799710f5`；base = `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`（merge-base 核验一致）。
- 受审范围：完整区间 71 个文件（+16087/−235），非仅最后一个提交。`candidate-1.json` 记录 71 文件逐文件 SHA。
- 保护文件：`AGENTS.md` 保持 dirty 未 stage，SHA 复核为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`（审查开始与结束时两次核验一致，与派发要求相同）。
- 冻结完整性复核：对 `candidate-1.json` 全部 71 个文件重算 SHA256——70 个完全一致；唯一差异为 `docs/reviews/I04/status.md`，其工作区改动经逐字节比对确认为对 HEAD 版本的**纯追加**（候选派发记录），属派发方明示允许的 append-only 流程证据，不改任何实现。
- 工作区其余状态与审查开始时一致；本人探针/日志均在 gitignore 的 `build/I04-review-ZCode-GLM53/` 内。

## 3. 已检查范围、验证命令与实际结果、未验证事项

### 3.1 代码审查范围（全部实际读码）

- Python：`coordinator.py`、`worker.py`、`job_store.py`（1528 行全文）、`protocol.py`、`memory_guard.py`、`process_environment.py`、`resources.py`、`storage.py`（diff 全文）、`entrypoint.py`、`__main__.py`、`contract_v2.py`（R2-F1 修复）。
- TS/桌面：`engine.ts`（EngineSupervisor 全文）、`jsonl.ts`、`task-service.ts`（全文）、`view-navigation.ts`、`preload/index.ts`、`task-presentation.ts`、`App.tsx`（diff）、`main/index.ts`（IPC 接线 diff）、`window-recovery.ts`（diff）、`electron-builder.yml`、`electron.vite.config.ts`。
- 契约/资源：`schema.json`（含 null-session 响应分支逐分支比对）、`registry.json`（v2Runtime 14 方法与 test-only 能力登记）、`fixtures.json`（321 例含 I04 null-session 正反例）、`binding-regressions.json`（41 例）、`frame-fixtures.json`、`v2.ts`（acceptsJobEvent/matchesResponse）、`index.ts`、`design-v2.ts`。
- 测试：抽查 `test_i04_round_faults.py`（子进程真实注入 6 阶段×4 故障×2 前置轮）、`test_job_store.py`（3 计划×8 提交点×4 故障参数化）、`test_i04_lifecycle_boundaries.py`、`tests/unit/supervisor.test.ts`、`task-runtime.test.ts`、`binding-regressions.test.ts` 断言强度；全仓 skip 扫描（仅 3 处合法：Darwin 专用 RSS 探针按平台跳过、两个 e2e 需隔离环境/fixture，均在 CI 条件下真实执行）。
- 脚本/CI：`scripts/build-engine.mjs`（契约/uv.lock 打包）、`scripts/verify-i04-package.py`（临时 cwd 下包内资源 SHA+公共例+真实 runtime）、`scripts/prepare-i04-fixture.py` 存在性、`.github/workflows/ci.yml`（Linux openbox/xdotool 真原生显示、三平台包验证步骤）。
- 文档：`docs/iterations/I04/acceptance.md`、`implementation.md`、`docs/architecture/0003-*.md`、`docs/m0-checklist.md` diff（S2 条目改写但仍未勾选）、`docs/reviews/I03/round-2/processing.md`（继承处置）。

### 3.2 实际运行的验证命令与结果（本机无窗口）

| 命令 | 结果 |
| --- | --- |
| `uv run --frozen pytest` | **992 passed，exit 0**（与冻结记录一致） |
| `npm test`（vitest） | **593 passed / 12 files，exit 0** |
| `npm run lint` | exit 0 |
| `npm run format:check` | exit 0 |
| `npm run typecheck`（三段） | exit 0 |
| `npm run verify:sources` | exit 0（12 源） |
| `uv run --frozen ruff check .` | exit 0 |
| TS/Python 原始帧解析差分探针（实际实现，14 个边界） | **全部一致**：转义 `\u0001` 双端接受；原始控制字符（0x09/0x01）、孤立代理、前导零、`+1`、`1e400`、`NaN`、重复键、深度 33 双端拒绝；`-0`/`1.0`/深度 32 双端接受。审查前怀疑的"TS 接受字符串内原始控制字符"分歧**被证伪**（JSON.parse 本身拒绝） |
| 候选哈希复核 | 见 §2 |
| `source-final1-manifest.json`（722 文件）重算 | 4 个文档与当前工作区不同（见 Z1），全部实现/测试/配置文件一致 |
| 内存隔离测试定向重跑 | 空载 30/30 通过、8 核忙负载 40/40 通过（见 B1 的复现性说明） |
| 新增失败证据核验 | `next-candidate-memory-failure.log` SHA=`182ef85f…` 与 JSON 声明一致；声明的 4 个"与 C1 相同"文件对 `ce6fd54` git blob 重算**全部匹配**；失败平台 darwin、失败断言为 `bad["error"]` 得 `INTERNAL_ERROR` 而非 `RESOURCE_LIMIT(memory)` |

### 3.3 证据文件审阅（未重跑、读实际内容）

- `local-verification.json`：结构完整，静态/隔离运行/打包三类分开，limitations 四条如实（无宿主 GUI、arm64 容器≠CI x64/Windows、Windows 探针待真实 CI、未验签名/生产语义）。
- 源应用 Linux 原生证据 JSON 实读：`result=PASS`、`inspectorClosed=true`、`hangMonitorEnabled=true`、事件 `[crashed, unresponsive]`、3 窗口、第 2 窗口真实 visible+focused；持久任务跨崩溃/无响应恢复 succeeded(v3) 不倒退、running 由 v2 推进到 v36、failed(v3) 不变，operation 证据保留——与声明一致。
- `internal-runtime-review.json`：环境继承 P1（I04-ENV-01）已由 `worker_environment()` 白名单与主进程 `getEngineEnvironment()` 白名单双端修复并有回归；未读取任何真实凭据。

### 3.4 未验证事项（如实保留，不记为通过）

- 本机未运行 `test:e2e`/Electron/打包产物启动（无桌面打扰约束）；其源与包内隔离 Linux 证据已审阅但非本人复跑。
- 未重跑 `package:dir`（现有双平台包内验证证据与脚本已核对，冻结后无打包相关改动；如需可后续补跑）。
- Windows 真实 CI 与三平台最终 CI、签名/干净设备/生产语义：按门禁在双审通过并 push 后、合并前执行，本轮不可得，不视为已通过。
- B1 竞态在本机 70 次定向重跑未复现（见下），复现依赖外部证据运行。

## 4. 问题清单

### B1（P2，阻断，未关闭）：darwin 内存故障错误分类竞态——超限任务偶发返回 INTERNAL_ERROR 而非 RESOURCE_LIMIT(memory)

- **文件位置**：`packages/engine/src/ontolearn_engine/coordinator.py:381-386`（`execute()` 读循环的 darwin RSS 轮询）；关联 `packages/engine/src/ontolearn_engine/memory_guard.py:77-85`。
- **触发条件**：darwin 平台；worker 因内存预算被拒退出（如 `allocateBytes` 超过 `maxWorkerMemoryBytes`）；coordinator 的 20ms RSS 轮询恰落在"子进程已被 child watcher 线程 `waitpid` 收尸、但 `process.returncode` 尚未被事件循环回调置位"的窗口内执行 `resident_bytes(process.pid)`。
- **机制（本人已逐步证实）**：
  1. 测试场景中 worker 的 `check_allocation` 抛 `MemoryBudgetExceeded`（`MemoryError` 子类）→ worker `main()` 以 `MEMORY_LIMIT_EXIT=74` 干净退出，无任何输出；
  2. 设计路径是 EOF 后 `returncode == 74 → RESOURCE_LIMIT(memory)`；
  3. 但轮询处 `except OSError: pass`（注释明示意图"子进程退出经由真实退出状态对账"）——而 `resident_bytes` 对已收尸 pid 抛的是 `MemoryGuardUnavailable`（**RuntimeError 子类，经本人在本机以真实子进程实测 `isinstance(e, OSError) is False`**），`proc_pidinfo` 因 ESRCH 返回长度不符即触发；
  4. 该异常穿透到 `execute()` 的 `except Exception` → `fail_job(classify(...))` → 落入未知来源兜底 `INTERNAL_ERROR`，与设计分类相悖。
- **证据**：
  - 外部实际失败：`build/I04-evidence/next-candidate-memory-failure.log`（SHA 与元数据一致；`npm run check` 中 991 通过/1 失败；失败断言输出 `{'code': 'INTERNAL_ERROR','messageKey': 'engine.internal','params': {},'retryable': False}` vs 预期 RESOURCE_LIMIT/memory）；元数据 `next-candidate-memory-failure.json` 声明的 `coordinator.py`/`worker.py`/`memory_guard.py`/`test_i04_lifecycle_boundaries.py` 四文件对 `ce6fd54` blob 重算**字节一致**——失败可归因于 C1 冻结代码，非另一 checkout 的差异（该 checkout head=`7e58f08`、TS 测试数 619 与 C1 的 593 不同，但 Python 侧 992 项与 C1 完全同集，失败测试文件字节同 C1）。
  - 机制证明：reaped pid 上 `resident_bytes` 抛 `MemoryGuardUnavailable` 且不是 `OSError`（本机实测）；`coordinator.py` 全文仅此一处调用 `resident_bytes` 且仅捕获 `OSError`。
  - 复现性：本人在受审 checkout 空载重跑该测试 30 次、8 核忙负载 40 次，**全部通过**——竞态窗口为"轮询的 returncode 检查与 `proc_pidinfo` 系统调用之间/子进程收尸与 returncode 置位之间的微秒至毫秒级间隙"，概率低但非零；外部那次运行在全量 check 负载下命中。本人未能在 70 次内直接复现，如实记录。
- **影响**：
  - 违反原验收第 4 项的资源边界错误语义与第 7 项的分类要求（已知内存资源故障必须表现为有界 `RESOURCE_LIMIT(memory)`；`INTERNAL_ERROR` 仅保留给未知来源兜底）；
  - 冻结候选自身的必要验收测试 `test_memory_failure_isolated_from_other_project_real_worker` 在受支持平台（darwin 为当前开发平台）非确定性失败——CI `desktop` 矩阵（`macos-latest`, `windows-latest`）第 91 行直接运行 `npm run engine:check`，**强制 CI 可被该竞态非确定性打红**；按项目规则不得以无诊断重跑掩盖；
  - 数据安全不受影响：失败运行中隔离断言均成立（另一项目任务 succeeded、失败任务 `resultRef=None`、状态 failed），仅公共错误码错误。
- **修复建议（须新候选 + 完整重验证 + 双模型重审，不得倒改 C1）**：将轮询的捕获扩大为 `except (OSError, MemoryGuardUnavailable): pass`（保持"探针不可用即交给真实退出状态对账"的原意图），并补一条确定性回归：monkeypatch `resident_bytes` 在 returncode 仍为 None 时抛 `MemoryGuardUnavailable`，断言仍走退出状态路径产出 `RESOURCE_LIMIT(memory)`；顺带覆盖"轮询时 pid 已收尸"的时序反例。修复后按冻结规则生成候选 2 全范围复审。
- **处理结论**：**未关闭（阻断）**。在修复并经新候选双审通过前，C1 不得通过。

### Z1（P3，非阻断）：source-final1 清单与冻结候选存在 4 个文档差异（记录时点差异，实现字节不受影响）

- **位置**：`build/I04-evidence/source-final1-manifest.json`（722 条）vs 当前冻结状态；差异文件为 `docs/architecture/0003-*.md`、`docs/iterations/I04/acceptance.md`、`implementation.md`（三者为验证轮之后、冻结提交之前的文档定稿）与 `status.md`（追加式派发记录）。
- **影响**：`local-verification.json` 的 `sourceManifest.differences: []` 是记录时点为真；但今日比对清单会看到 4 个文档差异，读者若只看清单可能误判冻结后实现有变。实现/测试/配置文件经本人对 `candidate-1.json` 逐文件重算**全部一致**，故验证结论所覆盖的实现字节与冻结候选相同，无实质影响。
- **建议**：后续证据追加时重录清单或在 local-verification 中注明"清单时点早于文档定稿"；可在候选 2 一并处理。允许延期。

### Z2（P3，非阻断）：`reconcile_jobs` 存在不可达分支（死代码）

- **位置**：`packages/engine/src/ontolearn_engine/job_store.py:940-941`（`if state == "cancelled" and job["state"] == "queued"`）。
- **触发条件/证据**：`cancel_job` 对 queued 任务直接迁移到终态 `cancelled`（`job_store.py:651`），`cancelling` 只可能来自 `running`；故 `state=="cancelled"`（要求现态为 `cancelling`）与 `job["state"]=="queued"` 永不同时成立，该分支不可达。
- **影响**：无行为影响，仅为冗余分支，可能误导后续维护者以为存在 queued→cancelling 中间态。
- **建议**：候选 2 中简化为单一 `elif state == "cancelled"` 路径。允许延期。

### Z3（P3，观察项）：非分页响应依赖 schema 上界而非显式字节预算预检

- **位置**：`coordinator.py:170-174` 仅对 `result.page`/`job.list` 施加 `maxPageBytes` 预检；`result.get`/`job.get` 等依赖 schema 上界（如 `vector.maxProperties=4096`，估算上限远低于 `maxFrameBytes`）与 `_emit` 的最终 `ProtocolFault` 兜底（会话致命而非优雅错误）。
- **影响**：当前词汇与上界下不可达；若未来扩词汇（正是 I03 O1 延期项）可能某响应无显式预算。与 O1 同属"schema 演进前先统一双端行为"的既有承诺范围。
- **建议**：随 O1 的未来 schema 演进一并统一处理；当前不要求改动。

### 已验证为非问题的对抗性假设（记录证据边界）

- "TS 接受字符串内原始控制字符导致双端分歧"——差分探针证伪（JSON.parse 拒绝，14/14 边界双端一致）。
- "hello 前错误响应与 schema null 分支矛盾"——逐分支比对：非 hello 的 null-session 错误仅 `VERSION_INCOMPATIBLE`/`HANDSHAKE_REQUIRED`，coordinator 门序（protocolVersion→handshake→params）保证其余错误均在会话建立后发生；hello 的任意错误允许 null；321 例共享语料含 `I04 pre-handshake *` 正反例与 `null session cannot succeed`。
- "队列满时幂等重放被拒"——`QUEUE_FULL` 检查带 `has_operation_claim` 豁免，重放不受限。
- "分页摘要可能出现在游标页"——游标 position 由服务端从上页末行生成，ordinal 0 的摘要行只可能在首个非游标页。

## 5. 历史问题与继承处置逐项判断

| 历史项 | 本轮判断 | 依据 |
| --- | --- | --- |
| I03 R2-F1（P3，要求 I04 接入 Python 消费者前闭环） | **已关闭（限 C1 代码层面）** | `contract_v2.py` 的 `accepts_job_event` 先做 binding 形状校验：精确键集、4 身份字段 id 校验、`lastSeq/stateVersion` 真整数+范围（bool 被 `type() is not int` 拒绝）、state 合法枚举；缺字段/错类型返回 False，不再逃逸 KeyError/TypeError；与 TS `acceptsJobEvent` 逐条对等。语料 41 例（原 24 差异变异 + 合法绑定接受 + 错形状拒绝 + 真实接入链路），双端同语料测试通过；合法绑定语义未变（合法控制组保持接受）。真实消费者（task-service `receive`→`acceptsJobEvent`）已接入并有丢通知对账/早到事件/atomic fence 竞态回归 |
| I03 O1（schema 词汇/默认上界演进前先统一双端） | **仍未关闭（按约延期，本轮无违规）** | C1 的 null-session 响应分支属 schema 演进，但走了既定统一路径：TS/Python 消费同一 `schema.json` 字节，共享语料补 I04 正反例，并纳入本候选完整审查。原"未来扩词汇/默认数组上界"仍开放 |
| I03 O2（parameterMeanings 英文散文不作 UI 文案） | **继续遵守** | `task-presentation.ts` 用固定本地模板按已验证 messageKey + 受限参数（`Number()` 收敛）组四段式；目录语义未进 UI |
| I03 O3 / I01 R6（legacy 扫描与历史增长，延期至真实负载） | **仍未关闭（按约延期）** | C1 未夹带无依据优化；`legacy-scan-measurement.json` 仅测量记录，未宣称性能结论或关闭 |
| 派发条件项：I05 交接边界 | **遵守** | `entrypoint.py` 保留 `--storage-probe`，仅新增 `--worker/--contract-probe/--protocol-resources`；未复制 I05 semantic-probe/collect-all hooks；`build-engine.mjs` 打包契约与 uv.lock，I05 hooks 合并留待其同步时唯一负责人处理 |
| 派发条件项：测试任务不登记业务能力 | **遵守** | registry 中 `test.*` 三能力 `exposure=test-only`、`implementation=test-runtime`；`productRuntime` 仍仅 `health`；`health()` 过滤 capabilities 只回 `health`；fixture 仅经主进程启动参数+环境变量双门，renderer 无创建入口（e2e 断言 `'createJob' in window.ontolearn === false`） |
| F6 基础设施子项边界 | **范围内完成、边界声明如实** | 真实 worker/Job/Store/轮次快照/消费证据/result.get/page 链路、`_check_summary` 对 run/terminal/消费 blob/快照的强校验、队列为空仍跑满 maxRounds、零轮/部分轮失败取消不造成功摘要、回收/畸形/矛盾拒绝、摘要仅首页；文档明确不关闭 E.2/E.5/G.4/FR-704 |

## 6. 十项原验收的检查结论（摘要）

1. 常驻健康/协商/注册表 SHA/v1 不兼容：supervisor 同 PID 复用（专测）、registry 原始字节 SHA 双侧比对、`__main__` 常驻化并修正旧注释、`PROTOCOL_VERSION=2`、v1 旧组合不再被接受——通过（B1 不影响本项）。
2. 严格 JSONL：双端同语料 + 本人 14 边界差分探针全部一致；追加前字节上限、终态后丢弃、CRLF 跨 chunk、限内恰好边界均正确——通过。
3. requestId/jobId/operationId/session/subscription/seq 归属：`seen` 去重与上限、`matchesResponse` 全量关联（含 job.create 输入回显）、task-service 代次/会话/项目/订阅联合校验、乱序并发专测——通过。
4. 有界队列/并发/单 writer/超时/心跳/取消/内存：排队计入总时限、忙碌期取消可达（轮询 20ms）、心跳不延长总时限、stdin 写/退出等待/提交前复验入 deadline、单 job 取消不杀协调器、worker 故障隔离——**内存项因 B1 存在错误分类竞态，本项不通过**。
5. 唯一 SQLite/同事务证据/完整指纹：`operation_claims` 全局唯一、完整 context 指纹、同事务 marker/receipt/终态、`immutable_*` 触发器、receipt 不入 current——通过。
6. S1 故障矩阵：3×8×4=96 原子 + 48 逐轮，真实子进程 + 真实 READONLY 注入（断言 errorcode）+ 崩溃/取消；lease→BEGIN IMMEDIATE→marker 对账，不猜成功不重放——通过（本机全套 992 含全部矩阵项通过）。
7. 安全错误到 UI 四段式：`classify` 按真实 sqlite 主码、未知兜底 INTERNAL_ERROR、无原值/路径/堆栈外传、四段式固定模板、retryable 不自动重放——通过（B1 恰是该分类语义的违例，归入第 4/7 项的阻断）。
8. 窗口重建/崩溃/无响应：`view-navigation` 仅新文档换代、render-process-gone 只解绑、卸载仅退订、恢复经持久查询重建订阅不重发写任务；隔离 Linux 源+包内真实 crashed/unresponsive+真实对话框键盘导航证据实读一致——通过（以隔离证据为准，本机未复跑）。
9. U1/未来边界对齐：资源投影/确认/来源全部可信侧构造（`prepare_plan` actor/permission）、定义集合与依赖从权威快照派生、不可变稳定分页（同请求同 token、TTL/尺寸/绑定校验、回收不返回成功空页）——通过。
10. ADR 采用与包内资源：采用结论基于真实运行证据并保留边界声明（Darwin 非硬上限、未批准未来原生库）；PyInstaller 显式打包契约+锁、包内 SHA 与源一致、临时 cwd 不依赖 checkout——通过（以既有双平台包证据+脚本审阅为准，未重打包）。

## 7. 最终结论

**不通过。**

- 唯一阻断项为 **B1（P2）**：darwin 平台 coordinator 内存轮询的异常类型缺口，使内存超限故障非确定性误分类为 `INTERNAL_ERROR`。该失败已在 C1 字节一致的另一 checkout 实际发生（证据哈希与文件一致性经本人核验），机制经本机实测证实，且 macOS 强制 CI lane 直接暴露于此风险；未修复前不得以既有绿灯覆盖，也不得降低测试期望。
- 其余全部检查范围（含 R2-F1 关闭、十项原验收中的其余各项、继承处置、冻结完整性、双端一致性）均通过或按约延期，无其他阻断。
- 路径：在**新候选**中修复 B1（附确定性回归），按冻结规则完整重验证并交双指定模型对新候选全范围复审；Z1–Z3 为非阻断，可随候选 2 处置或明示延期。
- 待验保留：Windows 真实 CI、三平台最终 CI、签名/干净设备/生产语义——按门禁在双审通过并 push 后、合并前完成，本轮不视为已验证。

## 8. 资源与约束声明

- 本审查必要的无窗口 check/test 命令已全部完成（§3.2）；未运行打包（现有证据已核，无增量价值）。**本 ZCode 任务对共享 out/build/release 验证预约到此显式释放**，MiniMax 可按其独立输出环境使用。
- 全程未启动任何宿主 GUI/Electron/HMR，未操作审查应用 UI；未读取另一模型本轮报告或结论。
- 冻结文件零改动；本报告为唯一指定输出 `docs/reviews/I04/round-1/zcode-glm53.md`；探针与日志留存于 `build/I04-review-ZCode-GLM53/`（gitignore 内）。
