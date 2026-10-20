# I04 第4轮（C4）独立对抗性审查报告 — MiniMax Code / M3.1-Flash / xhigh

> 冻结候选：`e45e6038b5e0f8f4adc69ed55aafccd75b3d3500` → `8f8eda1e24c0425ea2a65d2566978913ee310b8b`（121 文件）
> 本报告是本轮唯一获准直接写入 primary 的文件。未修改实现/测试/依赖/配置/验收，未提交、未推送、未切分支。
>
> **修订记录 R1（2026-10-21）**：本报告在总控提出 8 项可证事实核验后重写。修订仅针对本报告自身的事实表述与探针 harness，
> **不改变冻结源码/测试/配置/依赖/验收/JSON**，不倒改任何历史报告，不共享另一方本轮任何内容。
> 被更正的 v1 探针与原输出**原样保留**（见 §3.2 与附录 B）。
>
> **修订记录 R2（2026-10-21）**：总控就"全 OS 原生矩阵是否属本次强制门禁"提出范围事实核验后，**仅修订 §0、§4.8、
> §6.1(P3-12)、§6.4、§8.1、§9 的范围表述与计数**，不改任何评级、不改任何冻结源码/测试/配置/依赖/验收/JSON。
> 首版与 R1 均保留（首版快照 `build/I04-evidence/minimax-r4-first-terminal-report.md`）。R2 的核验依据与原文引用见 §8.1.0。

---

## 0. 结论先行

**最终结论：通过（Pass）—— 针对冻结候选 C4（base `e45e6038` → head `8f8eda1`，121 文件）。**

- 本轮**未发现任何阻断级实现缺陷**。历史阻断项在 C4 候选中均有**我本人独立复现/核对**的关闭证据（§6.1）。
- 历史原等级按原样保留并分别计数：**原 P1 阻断项共 3 项（P1-1、P1-2、P1-3）**，**B1 的原等级为 P2**（非 P1）；
  另有 **R2-N2、R2-P1 两项原 P2**。本轮 8 项更正中无一项改变任何原等级。
- 本轮新增发现 **7 项开放 P3（非阻断）**，均给出处理结论与允许延期裁定（§7）；另有 **M8 经核对不成立、予以撤回**（§7.8）。
- **本次（I04）合并前强制门禁 = 真实三平台 CI**（Windows/macOS 尚未运行）。其中 Windows 必含 **engine 层真实执行**
  （ABI/FILETIME/句柄/创建时间比对/实际父死亡），macOS/Windows 必含 engine:check/typecheck/build/普通 test:e2e/package:dir/
  verify-i04-package 全部绿。**全 OS 原生可见·外部焦点·原生崩溃/无响应恢复矩阵不属本次强制门禁**
  （原要求只要求"实际隔离环境"，Linux 已满足；且 CI 的 macOS/Windows job 会按规格自身门控跳过该矩阵，见 §8.1.0/§8.2）。
  签名发布、干净设备安装、生产语义、领域业务 E.2/E.5/G.4/FR-704、I05 语义、I06 网关、I03 O1/O3、I01 R6
  **不属 I04 合并前置**，本报告只登记其**明确未完成**状态（范围区分见 §8）。本通过**不构成合并授权**。

---

## 1. 任务、模型与思考设置来源（派发者核验 vs 自身可见来源）

| 项 | 来源与内容 |
| --- | --- |
| 派发关联标签 | `I04-R4-MiniMax-M31Flash-8f8eda1e24c0425ea2a65d2566978913ee310b8b`（派发侧标签，不冒充原生 UUID） |
| 任务性质 | 总控在本 I04 开发会话中新建的**独立完整只读审查任务**；未复用 C1/C2/C3 原任务，未新建 Goal |
| 模型 / 思考 | 派发侧按 M3.1-Flash / xhigh 设置派发，并在原生 UI 逐次核验后另存于 `docs/reviews/I04/round-4/dispatch.json` |
| 本报告作者可见来源 | 本会话运行时公开身份为 **MiniMax Code / MiniMax-M3.1-Flash**；思考档位由派发方设定并经其逐次核验记录。**我未操作另一模型应用，未读取另一模型本轮任何报告/进度/结论**（`build/I04-review-ZCode-GLM53-C4/` 整目录、`round-4/` 下任何 `.md` 结论均未读；本轮会话期间出现的 `round-4/zcode-glm53.md` 我亦未打开） |
| 历史报告 | C1/C2/C3 报告与处置 JSON 均为**历史已终态**，本轮**读回但不作本轮通过依据** |
| 结论独立性 | 不以 C3 的双 Pass、另一模型结论、开发者描述、测试计数或模型压力为依据；所有判断以 C4 候选实际字节与本轮实际运行结果为准 |

---

## 2. 候选身份、清单与独立导出身份

### 2.1 primary 身份（本轮实测）

| 项 | 实测值 |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs` |
| Git 根 | 同上（`git rev-parse --show-toplevel`） |
| 分支 | `feature/I04-resident-jobs` |
| 远端 | `origin https://github.com/NOmoreJoke/OntoLearn-Studio.git` |
| 完整 base | `e45e6038b5e0f8f4adc69ed55aafccd75b3d3500`（merge PR #4；`merge-base(base,head)==base`，线性） |
| 候选 head | `8f8eda1e24c0425ea2a65d2566978913ee310b8b`（`docs: record C4 final local checkpoint before full dual review`） |
| base..head 提交数 | 66 |
| **base..head 改动文件数** | **121**（`git diff --name-only base head` 实测） |
| 工作区 dirty | `M AGENTS.md` + 若干未跟踪流程文件（`candidate-4.json`、`integration.json`、`round-4/*`） |
| 保护 AGENTS | SHA256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786` —— **与派发给定值逐字节一致**；未改、未 stage |

### 2.2 候选清单交叉核验（`docs/reviews/I04/candidate-4.json`）

- `base` / `head` / `branch` / `worktree` / `fileCount=121` 与实测**完全一致**。
- 清单路径集合与 `git diff --name-only base head` 集合**完全相等**（manifest-only ∅，git-only ∅）。
- **逐文件 SHA256**：121/121 与 `git cat-file blob <head>:<path>` 实际字节一致；121/121 与工作区实际字节一致；**mismatch = 0**。
- `AGENTS.md` **不在** 121 文件内（保护 dirty 未被混入候选）。清单文件自身在冻结头之外，符合"清单及本轮纯流程证据单独关联"。

### 2.3 本模型独立导出身份

| 项 | 实测值 |
| --- | --- |
| 导出方式 | `git archive --format=tar 8f8eda1e2… \| tar -x`（不依赖工作区、未跟踪文件与 primary 的任何可变产物） |
| 导出根 | `build/I04-review-MiniMax-M31Flash-C4/source`（`build/` 在 `.gitignore:12`，不污染候选） |
| **全树字节核验** | 导出树 **776/776 blob 与 `git cat-file blob` 逐字节一致，mismatch = 0**（含中文路径文件，已用 `ls-tree -r -z` 复核，避免 quotepath 误判） |
| 依赖隔离 | `.venv`（CPython **3.12.12**，uv editable 安装指向导出根 `packages/engine/src`）、`node_modules`(247M)、`uv-cache`、`npm-cache`、`tmp`、日志全部位于导出根内；**未符号链接/未借用其他线依赖或生成输出** |
| 安装 | `uv sync --frozen` **rc=0**；`npm ci --no-audit --no-fund` **rc=0** |
| **`-I` 子进程导入来源** | `python -I -c "import ontolearn_engine"` → `…/I04-review-MiniMax-M31Flash-C4/source/packages/engine/src/ontolearn_engine/__init__.py`；`-I -m ontolearn_engine.worker` 同样解析到导出根。**证实 worker 子进程实际导入本导出包，未误用原 checkout venv**（R3-N1 方法问题的关键前提已在本环境消除） |
| primary 只读 | 未在 primary 运行任何写 `node_modules/.venv/out/build/release/cache` 的命令；primary 侧写入仅为本报告与附录 B 的纯探针证据目录 |

---

## 3. 本轮实际执行的验证（命令、真实 rc、日志/哈希、平台）

全部在独立导出根内执行；日志留存于 `build/I04-review-MiniMax-M31Flash-C4/logs/`。

### 3.1 有效验证

| # | 命令 | 平台 | 真实 rc | 关键实测结果 |
| --- | --- | --- | --- | --- |
| V1 | `npm run check`（lint→format:check→typecheck→vitest→build→ruff+pytest） | macOS arm64（无窗口、无 GUI） | **0** | eslint 0 warning；prettier 干净；3 套 tsc 通过；**vitest 15 文件 / 630 passed**；electron-vite 3 bundle 构建成功；ruff check + format 通过；**pytest 1052 passed in 46.42s**（与 C4 声明的 macOS 630TS/1052Py **独立吻合**） |
| V2 | `git diff` / `git cat-file` / `shasum` 清单与归属核验 | macOS arm64 | 0 | §2.2、§2.3（0 mismatch）；`contract_v2.py` base..head **+33/−1**（§5 R2-F1 归属） |
| V3 | `scripts/verify-i04-package.py <C4 真实 macOS 打包目录> <我的输出目录>` | macOS arm64 | **0** | 打包引擎 SHA256 `1f5a5eb81476d6b38b7ba26bc7891c2e675db553e186d152adb06c7bce10e83d`（与派发给定值**一致**）；`--protocol-resources` 返回 `frozen=true` 且资源 SHA **与本导出候选的契约文件逐项相等**；contract-probe `status=passed`，计数 `321/11/30/9/7/41/51`；**包内 runtime `17 passed in 12.36s`，runtime.exit=0** |
| **V4** | **修正版探针 v2 · 正臂**（`handshake_probe.v2.py`）对 **C4 真实打包引擎** 与 **源码引擎**（导出根 `python -I -m ontolearn_engine`）各一次 | macOS arm64 | **0** | 见 §3.3 |
| **V5** | **修正版探针 v2 · 忙箱臂**（同上）对 **C4 真实打包引擎** 与 **源码引擎** 各一次 | macOS arm64 | **0** | 见 §3.3 |
| V6 | 原始日志哈希与内容复核（4 份 check.log + 2 份包探针 stdout） | macOS arm64 | 0 | §6.6 与 §7-M1 |
| V7 | `docs/reviews/I04/round-4/source-lineage-note.json` 独立复核 | macOS arm64 | 0 | 6/6 SHA256 与字节数**逐项吻合**；4 份日志内计数逐项吻合；冻结 JSON 未被覆盖（SHA `327263aa…`，61262 B） |
| V8 | 既有交叉索引复核（`round-1-evidence-lineage.json:P3_8_internalReview`） | macOS arm64 | 0 | §6.1 P3-8、§7-M8 |

**本轮明确未执行**（并在 §8 登记为待验）：任何宿主 Mac Electron / e2e / native / HMR / GUI 窗口；Windows 真实执行；macOS CI；签名；干净设备。

### 3.2 已被更正的 v1 探针（原样保留，不作本轮证据）

`build/I04-evidence/minimax-r4-probe-corrections/` 与导出根 `tmp/probe/evidence/` 各存一份：

| 文件 | 性质 | 更正后的定性 |
| --- | --- | --- |
| `handshake_timely_probe.v1.py` + `.v1.output.{packaged,source}.json` | v1 正臂（仅应用过 argv 列表补丁；字段名与 sleep 未改） | **无效**：实际只 sleep 1.0+0.5+0.6 ≈ **2.1 s**，却输出字段 `stillAliveAfter7s`（实为约 2.1 s 存活）。**不能**证明会话存活超过生产 handshakeMs=5000；`p.kill()` 后未 `wait()`，无自然退出证据。已由 v2 正臂取代（§3.3） |
| `handshake_flood_probe.v1.py` + `.v1.output.json` | v1 忙箱臂 | **部分有效**：持续合法负载与自然退出成立；但未直接观测 inbox 占用，**不得**据实测称 "inbox 永不排空"；迟到 hello 的写线程安排在 5.6 s，而脚本在 wait(5.12)+0.4 ≈ 5.52 s 退出 → **该 hello 很可能从未被实际尝试写入**，`helloAccepted: 0` 不足以证明"迟到 hello 被主动拒绝"。已由 v2 忙箱臂精确区分（§3.3） |
| `README-invalid-v1-arms.md` | v1 有效性边界说明 | — |

### 3.3 修正版探针 v2 的实测结果

`handshake_probe.v2.py`（修正项：正臂真正超过生产 5s；区分 planned/attempted/received；迟到 hello 显式记录是否被尝试；EOF 有界收尾 + wait；SIGKILL 仅作兜底且显式标记，不冒充自然退出）。

**正臂（真实超过生产握手窗口）**

| 指标 | 冻结 C4 打包引擎 | 源码引擎（导出根 `-I -m ontolearn_engine`） |
| --- | --- | --- |
| 及时 hello 发出时刻 | 1001.5 ms | 1005.2 ms |
| hello 被接受 | **true** | **true** |
| 会话身份 | `7b5301ee-84c0-4318-9457-42c67ba5e518` | `5c5ac717-f03f-44c3-aaac-44597c375d0d` |
| 握手后 ping 被接受 | **true**（共发 14 次） | **true**（共发 14 次） |
| **存活检查时的真实 monotonic elapsed** | **6592.7 ms** | **6604.8 ms** |
| 是否超过生产握手窗口（5000 ms） | **true** | **true** |
| 超过窗口后仍存活 | **true** | **true** |
| 收尾方式 | 有界 EOF（关闭 stdin）+ `wait()` | 有界 EOF + `wait()` |
| **自然退出** | **true**，`exitCode=0` | **true**，`exitCode=0` |
| harness 强杀 | **false**（未发生） | **false**（未发生） |
| 收尾耗时 | 34.5 ms | 17.3 ms |
| stderr 字节 | 0 | 0 |

**忙箱臂（持续合法非 hello 负载）**

| 指标 | 冻结 C4 打包引擎 | 源码引擎 |
| --- | --- | --- |
| 计划帧数 / **实际尝试帧数** | 39400 / **39400** | 38912 / **38912** |
| 写错误 | 1（末帧部分写） | 1（末帧部分写） |
| **实际收到响应数** | 38775 | 38320 |
| 退出时刻（真实 elapsed） | **5102.0 ms** | **5112.7 ms** |
| **自然退出 / exitCode** | **true / 0** | **true / 0** |
| stderr 字节 | 0 | 0 |
| 迟到 hello 计划时刻 | 5600 ms | 5600 ms |
| **迟到 hello 是否被实际尝试** | **false** | **false** |
| 迟到 hello 写结果 | `engine-already-exited; hello-never-attempted` | 同左 |
| 观测到任何握手成功 | 0 | 0 |
| 观测到任何 engineSessionId | 无 | 无 |
| **保守尝试上界**（attempted + 至多 1 帧部分写 + 迟到 hello 若被尝试） | **39401** | **38913** |
| 请求预算 | 65536 | 65536 |
| **可用实际上界排除"预算耗尽致命"解释** | **true** | **true** |
| inbox 占用是否被直接观测 | **false（不作此声称）** | **false（不作此声称）** |

**据此本轮对两项作精确表述（替代 v1 的过宽表述）**：

1. **持续合法负载下的绝对到期成立**：引擎在约 3.9 万帧持续合法请求下于 **5.10–5.11 s 自然退出（exit 0）**，
   而非等到请求预算 65536 被耗尽（保守尝试上界 39401 / 38913 < 65536）。**未观测到 inbox 队列占用**，
   故本报告**不**把该实测称为 "inbox 永不排空"；精确的非空机制由 §4.11 的代码路径与在树确定性测试承担。
2. **"迟到 hello 被拒绝"不由该探针承担**：探针记录显示迟到 hello **从未被尝试写入**（引擎已先退出）。
   该结论由在树确定性测试 `packages/engine/tests/test_handshake_deadline.py:73-84`
   （`test_busy_inbox_cannot_accept_hello_at_or_after_absolute_deadline`：持续非空 inbox + 时钟推进到期限后，
   仅首个 pre-hello 帧被应答，其后的 hello **不被处理**，只发出 1 条响应）与代码路径 `coordinator.py:636-640` 共同承担。

---

## 4. 原十项验收逐项覆盖（以 C4 实际源码与本轮实测为准）

### 第1项 常驻协调器、主进程监督、hello 协商、同源 registry、资源来源、能力声明

- `apps/desktop/src/main/engine.ts:14-24` 打包/源码两条引擎命令；`:114-136` `getEngineEnvironment` 只透传 OS 目录/语言环境，并单独签发 `ONTOLEARN_DB_PATH` / `ONTOLEARN_ALLOWED_PROJECTS` / `ONTOLEARN_TEST_MODE`；`:287-292` `spawn(shell:false, windowsHide:true)`，无继承凭据、无代理、无可执行搜索路径。
- `:264-282` 启动前读取 registry 原始字节并与 `v2Registry` 逐字比对、算 SHA；`:358` / `:418-419` 双向核对 hello 返回的 `registryHash`。
- `packages/engine/src/ontolearn_engine/resources.py:9-32` 冻结态 `sys._MEIPASS/"contracts"`、源码态 `parents[3]/"contracts"`；`REGISTRY_HASH = sha256(registry.json 原始字节)`；`IMPLEMENTATION` 三键含 `dependencyLockHash = sha256(uv.lock)`。
- 能力声明未夸大：`:524` health 仅回 `capabilities.filter(c => c === 'health')`；`registry.json` 的 `productRuntime=["health"]`，7 条业务能力 `implementation=design-only`、3 条 `test.*` 为 `test-runtime/test-only`。
- **V3 独立验证**：打包引擎在**临时工作目录**（`cwd` 不含 checkout）执行 `--protocol-resources` / `--contract-probe`，资源 SHA 与本候选契约**逐项相等**，公共例 321/11/30/9/7/41/51 全通过 → 「资源不依赖源码 checkout 路径、包内 SHA 自洽」有实证。
- **判定：满足。**

### 第2项 严格 JSONL reader（拆包/粘包/跨 chunk UTF-8/多字节/坏 JSON/未知方法/重复 ID/嵌套重复键/无交集/超长未终止帧/连续超限 chunk/终态后 chunk）

- `packages/engine/src/ontolearn_engine/protocol.py:74-117` `JsonlReader`：`:97` **追加前**按 `max_bytes` 拒绝；`:109-112` 触发后 `stop()` 停止累积并清缓冲；`:104-105` 容忍 CRLF 尾；`:114-117` `finish()` 对未终止帧抛 `ProtocolFault`。
- `decode_frame:27-71`：拒 BOM、`:43-47` 深度 > 32、`:18-25` **嵌套重复键**直接 `ProtocolFault`、`:53` `parse_constant` 拒 NaN/Infinity、`:63-68` 拒孤立代理与超 2^53 数值、`:51` 显式 UTF-8 严格解码。
- `packages/engine/tests/test_frame_corpus.py:66-85` 用**同一份原始字节语料**（`packages/contracts/v2/frame-fixtures.json`，51 例，含 UTF8 chunk boundary 0..35）驱动真实 `JsonlReader`，逐例断言 `frames == expectedFrames` / `errors == expectedErrors` / `terminal` / 缓冲已清空；TS 侧 `apps/desktop/src/main/jsonl.ts` 消费同一语料。
- 未知方法 / 重复 ID / 无交集：`coordinator.py:170-175`（方法不在 `v2Runtime` → `ProtocolFault`；重复 ID 或 `len(self.seen) >= 65536` → `ProtocolFault`）；`:187-199` 版本无交集 → `VERSION_INCOMPATIBLE`。
- 终态后 chunk：reader `terminal` 后 `feed` 直接返回 `[]`（`protocol.py:87-88`）。
- **判定：满足**（语料 51 例与公共例 321 例在本轮 V1/V3 中全绿）。

### 第3项 requestId/jobId/operationId 归属、并发乱序、未知/重复/旧会话/旧项目/旧订阅不得结算新请求或污染 UI

- `apps/desktop/src/main/engine.ts:408-413` 响应必须命中 pending 且 `matchesResponse` 通过，否则计入 anomaly，**3 次异常即终止会话**（不结算、不污染）。
- `packages/engine/src/ontolearn_engine/coordinator.py:189-214` 非 hello 需已握手且 `engineSessionId` 严格相等；`_authorize:93-97` 越权项目 → `PERMISSION_DENIED`。
- 订阅：`coordinator.py:283-306` `job.subscribe` 绑定 project/job/stateVersion/seq；`_notify:143-164` 仅当 `job.stateVersion > binding.stateVersion` 才推进，**不回退**；`_progress:99-127` 要求 `binding["stateVersion"] == job["stateVersion"]`。
- 乱序/旧代次：`apps/desktop/src/main/task-service.ts:284-300` 请求前后 generation 变化即作废（并清理刚建的订阅）；`:428-436` / `:518-531` 退订前校验 `binding.engineSessionId === 当前会话`，**旧会话订阅不会对新会话发退订**，从根上避免 `NOT_FOUND{subscription}` 误伤（P1-1 的核心修法）。
- **判定：满足。**

### 第4项 有界队列/全局并发/项目单 writer、只读绑定不可变快照、各阶段独立时限、心跳不延长总时限、无总量只显示阶段、故障隔离、单 job 取消不杀协调器

- 队列/并发：`coordinator.py:255-258` 队列满且非幂等重放 → `QUEUE_FULL`；`:341-358` 全局并发上限 + **项目单 writer**（`occupied` 集合，按项目跳过而非阻塞他项目）。
- 时限分离：`resources.py:33-46` startup/handshake/request/total/heartbeat/cancelGrace **各自独立**；`:374-381` `deadline` 为任务总时限（`createdAtMs + totalMs`），`commit_boundary` 在每次提交前检查 → **心跳与阶段切换不重置总时限**。
- 无总量只显示阶段：`coordinator.py:124` `"progress": {"stage": stage, "completed": None, "total": None}` —— **不捏造百分比**；P2-5 要求的 `job.progress` 生产端已在 `_progress` 落地。
- 故障隔离：`coordinator.py:544-557` 单 job 取消只 `terminate` 该 worker（`cancelGraceMs` 内再 `kill`），**不杀协调器**；`:558-563` 其它异常只 fail 本 job。
- 只读绑定不可变快照：`job_store.py:363` `snap = self._project_snapshot(input_["inputSnapshotId"], internal)`，并对 `derivedResultIds` 逐个校验 `inputSnapshotId` / `payloadStatus` / `implementation`。
- **判定：满足。**

### 第5项 唯一 SQLite 真相、同事务提交证据、operation_claims 全局唯一与完整指纹

- `packages/engine/src/ontolearn_engine/job_store.py` 继承 S1 `Store`，**唯一可变源真相**；`job_store.py:53-88` 以 OS 文件锁实现**写者租约**（Windows `msvcrt.LK_NBLCK` / POSIX `flock`），`serve()` 启动先 `reconcile_jobs()`（`coordinator.py:621`）→ 旧协调器被 fence。
- `operation_claims`：`job_store.py:479-482` 与 job 同事务登记；表定义 `operation TEXT PRIMARY KEY` → 全库唯一由主键强制；`create_job:355-362` 命中既有 claim 时走 `_accepted_job`，**逐字段**比对 project/capability/input/confirmationRef/implementation/limits + snapshot + parameters + runConfig + plan + confirmation（`:500-566`）→ 内容不同即 `IDENTITY_CONFLICT` / `INVALID_STATE`。
- 同事务：`:716-754` `commit_job` 在一个 `_application()` 事务内完成 `super().commit()`（S1 正式 marker）+ 收据发布 + `_transition(succeeded)` + `hook("mid_job_terminal")`；`:799-840` `commit_job_round` 每轮同事务写 `rounds` 证据。
- 无第二权威：`job_store.py:926-953` `reconcile_jobs` 在取得租约后按持久记录判终态，**不以异常文本或"已有提交"猜成功**；`:941` 仅 `cancelling` → `cancelled`，其余非终态 → `failed/ENGINE_EXITED`。
- **判定：满足。**

### 第6项 S1 故障对账矩阵逐项（提交前/事务中、磁盘错误、旧基线、响应丢失、取消与完成竞态、零轮/部分轮取消崩溃、末轮提交但缺终态、终态后才取消、迟到旧结果、真实依赖/集合变化）

- 矩阵：`packages/engine/tests/test_job_store.py::test_atomic_job_fault_reconcile_matrix`（3 计划 × 8 提交点 × 4 故障 = **96**）与 `packages/engine/tests/test_i04_round_faults.py::test_round_job_progress_atomic_fault_matrix_fences_and_preserves_previous_round`（**48**），两者的**逐格精确预期断言在源码中**（不是仅计数）。
- 逐格只读证据记录器：`scripts/i04_matrix_evidence.py` —— `:112-116` SQLite 连接用 `mode=ro` + `query_only` + 只允许 SELECT/READ/FUNCTION/TRANSACTION 的 authorizer；`:418-419` **必须 `complete_calls == 144 且 recorded == 144`**，否则 `INCOMPLETE_DATABASE_EVIDENCE`；`:416-417` pytest 非零退出记错；`:421-422` 失败时强制 `session.exitstatus = TESTS_FAILED`；`:244-247` 拒绝复用旧输出目录（旧证据不被覆盖）；`:335-336` 以 `--i04-matrix-source-revision` 对**提交树字节**校验源绑定。
- **重要边界**：记录器自身在 `:12` 与 `:458-467` 明确声明"hash/count 是执行指纹，不是预期值断言；精确预期断言保留在受审测试源码中" —— **没有用 hash/count 冒充源码已做的精确预期** ✓
- CI 接线：`.github/workflows/ci.yml:30-37` 新 step 位于 `npm ci`/`uv sync --frozen` 之后、`npm run check` 之前；step 失败即 job 失败（无 `continue-on-error`）；`:89-98` artifact `if: always()` 保存 `build/i04-matrix-ci/`（含失败时的 JSON）。
- **判定：满足。**

### 第7项 Python→主进程→受限业务命名 bridge→UI 的 code/messageKey/受限 params/retryable 与四段式

- 错误目录唯一：`packages/contracts/v2/errors.json`（26 码），`resources.py:61-75` `safe_error()` 对未知码降级为 `INTERNAL_ERROR`、并经 `CONTRACT.validate("error", …)` 校验，**不外传原异常/堆栈/路径/原值**。
- SQLite 分类：`coordinator.py:39-50` 只按 `sqlite_errorcode` 主码分类（BUSY/LOCKED → `STORAGE_BUSY`；IOERR/FULL/READONLY/CORRUPT → `STORAGE_FAILURE`），其余 → `INTERNAL_ERROR`；**不匹配异常文本**。
- 跨边界链路：engine.ts `SafeEngineError`（`code/messageKey/params/retryable`）→ `task-service.ts` → `apps/desktop/src/preload/index.ts`（按业务命名方法，无 `invoke(method,params)` 通用通道）→ `apps/desktop/src/renderer/src/task-presentation.ts`（本地固定模板四段式；`:41` `handshake: '连接协商'`、`:114` `protocol.handshakeRequired` 分类）。
- retryable 非自动重放：恢复路径 `task-service.ts:265-273` 失败后 `fenceConnection` 并按显式重试预算推进，**不自动重发写任务**。
- **判定：满足**（I03 F5 的**未来扩展**部分见 §5，本项只就 I04 现有固定安全错误链判定）。

### 第8项 I02 窗口重建后按 project/job 查持久权威状态与提交点、重建订阅、拒绝旧通知、不重发写任务；页面卸载只解除订阅不取消后台任务

- `task-service.ts:437-497`：**先 `job.get` 再 `job.subscribe`**，且仅当 `subscription.stateVersion === job.stateVersion` 才建立 watch（否则退订重试，`:492-496`）；`connectionChanged:147-159` 检测到会话 ID 变化即触发重新对账。
- `task-service.ts:335-341` 项目 revision 前进 → **新 generation、撤销旧订阅、保留各 job 的不可变输入分组**；迟到更新因 generation 不匹配被丢弃。
- 卸载只退订：`unsubscribeView:508-517` → `unsubscribeJob:518-532`，**不调用 `job.cancel`**，后台任务继续。
- 不重发写：`packages/engine/tests/test_stdio_session_shutdown.py:247` `restored.count == 7`（hello + 六次只读；**无 create/cancel/write 重放**）。
- 原生部分：Linux arm64 **实际隔离环境**（既有 daemon + Xvfb/openbox/xdotool）**源码与包内各六项真实桌面/native 验收通过**（`acceptance.md` C4 段；证据 `c4-verification.json.desktop.native[*].raw.path`）。本轮**直接读回两份原始 `i04-native-verified-evidence.json`**（packaged SHA `a19993fd…`、source SHA `e46b8f17…`，各 33373 B），逐字段为：
  - `windows` 三窗口 —— **ordinal 2（应用主窗口）带 `focused=true`，并带外部观测记录 `x11Focus = {"observer":"xdotool/XGetInputFocus","windowId":"4194323","title":"OntoLearn Studio","visible":true}`**，即**外部 X 焦点有正面证据**；ordinal 1 与 ordinal 3 的记录**不含** `focused`/`x11Focus` 键（摘要里的 `null` 是缺字段的 `get()` 结果，**不得**外推为"全部窗口无外部焦点"，也不是显式 null）；
  - `nativeDialogs` —— 2 个真实原生提示框：`phase=crash` windowId **6291458**、`phase=hang` windowId **6291613**，标题均为「OntoLearn Studio 窗口恢复」、`visible:true`；`dialogObserver = "external xdotool visible-window inventory"`；
  - `events=["crashed","unresponsive"]`、`inspectorClosed=true`、`hangMonitorEnabled=true`。
- **原要求的原生条款（总控 `I04-launch-prompt.md:48`）只要求"放在实际隔离环境或另行明确授权时段"，并明令禁止用户 Mac GUI**，未要求每个 OS 执行整套 native 矩阵；Linux 隔离环境已满足（§8.1.0 原文引用与逐条核对）。
- **判定：满足**（原要求已由实际隔离环境满足；"每 OS 跑整套原生矩阵"另列为建议/未来未验，**不属本次强制门禁**，见 §8.2）。

### 第9项 U1 身份/依赖/分页与 I05/I06 边界对齐；真实 Store 提交与轮次证据不得用内存 mock

- `job_store.py:998-1086` `_publish_job` 在真实事务内发布结果 + 失效投影 + `job_current` 归属；`:1056-1065` `receipt` **永不**成为领域 current；`:1067-1085` 仅当 kind 非 receipt、无 stale、snapshot revision 等于当前 revision 时才登记 current。
- 分页：`job_store.py:1303-1336` `result_page` 以 `binding`（project/result/snapshot/scope/parametersHash/order）绑定，`nextCursor` 为服务端生成 UUID；失配 → `CURSOR_MISMATCH`（`:1309-1311`）、到期 → `CURSOR_EXPIRED`、载荷回收 → `PAYLOAD_EVICTED`；`:1323-1326` 单页 131072 字节预算按行截断并续游标；`job_list:1338-1433` 用有界 TTL 的**不可变列表快照**，新任务/终态变化不重排既有列表。
- **result.page 默认 200 / job.list 限 100**：契约 `params_result.page.pageSize` 上界 200、`params_job.list.pageSize` 上界 100；`resources.py:43` `maxPageItems=200` 为全局上限；契约校验先于运行时上限，故 job.list 的**有效上界仍是 100**。`docs/iterations/I04/implementation.md:16` 明确记载（"result.page 的默认运行时预算与公共 schema/TS/游标共同允许 200 项，job.list 仍限 100；显式协商更小预算仍按资源限制拒绝。真实 210 行结果验证 200+10 稳定分页，201 在契约层拒绝"）。
- **未注册为业务能力**：`registry.json` 中 7 条业务能力 `design-only`、`agentEligible=true`；`test.*` 为 `test-runtime/test-only`；`productRuntime=["health"]`。
- **判定：满足**（文档口径差异见 §7-M3）。

### 第10项 ADR 采用/修订结论基于真实运行证据；依赖/协议资源按唯一规范纳入包内并核验 SHA，不依赖源码 checkout 路径

- `docs/architecture/0003-resident-coordinator-and-jobs.md` 状态为「I04 实施采用」，并逐条列出仍待正式集成的边界（E.2/E.5/G.4/FR-704、I05 语义、I06 网关）。
- 包内资源：`scripts/build-engine.mjs` + `resources.py`（冻结态 `sys._MEIPASS/"contracts"`、`sys._MEIPASS/"provenance/uv.lock"`）；**V3 实测**：打包引擎在临时 cwd 返回 `frozen=true` 且资源 SHA 与本候选契约逐项相等 → 「不依赖源码 checkout 路径」有实证。
- **判定：满足。**

### 4.11 本轮第8/9项要求特别核验项：生产默认握手的绝对 deadline

| 核验点 | 位置 | 结论与证据 |
| --- | --- | --- |
| 使用**生产默认**而非缩短的测试参数 | `coordinator.py:634` `handshake_deadline = time.monotonic() + LIMITS["handshakeMs"]/1000`；`resources.py:35` `"handshakeMs": 5000` | ✓ 生产默认 5000 ms |
| 检查点在**每次读取/解析 loop**、位于 `inbox.get_nowait()` **之前** | `coordinator.py:636-640`（在 `try/except queue.Empty` **之外**） | ✓ 这正是 C2 的根因位置（C2 时该检查只在 `except queue.Empty` 内，inbox 恒非空即被饿死），已修正 |
| 期限**绝对**、不因活动续期 | 单一 `time.monotonic()` 基准；心跳/请求不重置 | ✓ **V5 实测**：约 3.9 万帧持续合法请求下仍在 5.10–5.11 s 自然退出；保守尝试上界 39401/38913 < 65536，**排除预算耗尽解释** |
| 精确"inbox 持续非空"机制 | 本探针**未直接观测 inbox 占用**，不作该声称 | 由代码路径（检查位于 `get_nowait()` 之前，故占用与否都必被检查）+ 在树确定性测试 `test_handshake_deadline.py:73-84` 承担 |
| 等待/处理/accept 边界不被绕过 | 每轮循环顶端检查 | ✓ |
| 粘包/已缓冲多帧不能重置 | 同上 | ✓ |
| 合法及时 hello 不误杀 | `coordinator.session is None` 才检查 | ✓ **V4 实测（修正版）**：打包件与源码件均在 ~1.0 s 发出及时 hello 并被接受（会话身份 `7b5301ee…` / `5c5ac717…`），握手后 ping 正常，**真实存活至 6592.7 ms / 6604.8 ms（> 5000 ms）** |
| 过期安全终止并清理关联状态 | `serve():639` break → `finally` → `coordinator.stop()`（取消任务、清订阅）→ `store.close()`（释放租约）→ `temporary.cleanup()` | ✓ **V4/V5 实测**：有界 EOF 收尾后**自然退出 exit 0**（收尾耗时 34.5 / 17.3 ms），stderr 0 字节，无残留 session；忙箱臂同样自然退出 exit 0 |
| 未把单请求等待超时当全握手绝对上限 | TS 侧 `engine.ts:354` 的 hello 定时器是**单请求**超时；引擎侧另有绝对期限 | ✓ 两者并存，语义不混淆 |
| 真实默认包路径（非 mock/非缩短） | `packages/engine/tests/test_resident_runtime.py:101` `test_default_handshake_deadline_closes_real_source_or_packaged_transport`：真实子进程、真实默认 5000 ms、真实墙钟、**不关 stdin**（`:167` `process.wait(timeout=7) == 0`）、`:172` `elapsed < 6`、`:173` stderr 空；由 `scripts/verify-i04-package.py:61-74` 以 `ONTOLEARN_TEST_ENGINE=<打包引擎>` 执行 | ✓ **V3 实测该用例在 C4 真实打包引擎上通过**（包内 17 passed 中含此例） |

**结论：第8/9项的握手绝对期限要求，在 C4 上以生产默认参数、真实包内二进制、真实墙钟成立；
"迟到 hello 被拒绝"由在树确定性测试与代码路径承担，不由忙箱探针承担。**

---

## 5. 继承义务逐项覆盖

| 继承义务 | 原始约定 | C4 实际 | 判定 |
| --- | --- | --- | --- |
| I03 **R2-F1**（Python 消费者接入前闭环安全拒绝） | I03 处置："**延期，保持开放**…I04 接入 Python 消费者前必须…补形状校验或有限安全拒绝及缺字段/错误类型回归…**不能把'允许延期'写成已修复**" | **修复归属为 I04（本候选）**——本轮实测 `git diff e45e6038..8f8eda1 -- packages/contracts/python/contract_v2.py` 为 **+33/−1**，新增 `accepts_job_event` 的 binding 前置校验：精确 7 字段键集、4 个 id 走 `validate("id")`、`lastSeq/stateVersion` 必须是**真整数**且在界内、`state` 必须是 6 态枚举、序号须恰为 `lastSeq+1`、终态 binding 一律拒绝、`job.progress` 要求 `stateVersion` **等值**、其余要求 `+1` 且转移经 `permits_transition`；全程返回布尔、不逃逸 KeyError/TypeError。TS 侧 `packages/contracts/src/v2.ts:330-370` 逐条对等。**C4 候选的 `binding-regressions.json` 语料 41 例**由打包引擎 contract-probe 在本轮 V3 实测全通过（`status=passed`，计数 321/11/30/9/7/**41**/51） | **闭环成立（归属 I04）**。I03 归档报告与 I03 处置 JSON **未被倒改**；R2-F1 仍不计入 22 项产品 P 等级（其原约定即 P3、允许延期、接入前必须闭环） |
| I03 **O1** 未来词汇/默认上界 | 不扩新 schema 词汇/缺省数组上界；未来演进须统一双端并新候选复审 | C4 未扩词汇、未改缺省数组上界；Z3 仍按约延期（§6.1） | **仍未关闭（按约延期）** |
| I03 **O2** 英文 `parameterMeanings` 不作 UI 文案 | `parameterMeanings` 仅是语义目录，**不得直接作为界面文案**；本地化按已批准 `messageKey` 与受限参数映射 | **本 I04 范围内已满足**：`task-presentation.ts` 使用本地固定模板 + `messageKey`，未直接展示 `parameterMeanings` 原文；未知来源安全兜底，不另建目录、不外传内部细码。**开放部分仅为未来语义细码/业务扩展示例的映射补充**，不属 I04 基础设施 | **I04 侧满足**；未来扩展保持开放（不计入 22 项，不与 §4.7 矛盾） |
| I03 **O3 / I01 R6** 历史增长与容量 | 保留原等级开放/延期；真实负载测量另由 I04/Q5 承接；不得宣称性能/容量结论 | `docs/iterations/I04/implementation.md:48` 与 ADR-0003 均保留"原等级开放/延期，未据合成测量作性能承诺"；`legacy-scan-measurement.json` 仅测量记录 | **仍未关闭（按约开放）** |
| I03 **F5** 内部错误→公共安全类别 | 须在实际 producer/可信上下文确定后适配，不按异常码机械映射未知来源 | **本 I04 范围内已满足固定安全错误链**：`coordinator.py:34-51` `classify()` 仅对 `ServiceFault`/`JobFault`/`Conflict`/`sqlite3.Error` 走已知映射，其余一律 `INTERNAL_ERROR`；`resources.py:61-75` 未知码降级并二次校验；本轮实测该链在真实 producer/可信上下文下工作（§4.7）。**开放部分为未来 I05 语义细码与业务 producer 接入后的映射扩展** | **I04 侧满足**；未来扩展保持开放（不计入 22 项，不与 §4.7 矛盾） |
| I03 **F6** 终态摘要基础设施子项 | 真实逐轮负载经真实 worker/Job/Store/不可变 result.get/result.page；覆盖零提交/部分提交失败取消/摘要不一致/缺失/畸形/载荷回收/原 resultId 绑定/稳定分页；摘要只在首个非游标页；不可用时不展示"全部处理完成" | `job_store.py:850-924` `finish_job_run` 从**真实不可变轮次账本** `self.history(run)["rounds"]` 生成审计行，摘要 `run.summary.v1` 含 `reachedMaxRounds/pendingEventCount/eventConsumptionRef`；`:866-875` 队列与消费记录必须**等于**最后提交状态，否则 `IDENTITY_CONFLICT`（不信任外部摘要）；`:1328-1334` 摘要仅在首个非游标页（后续页为游标页） | **仅关闭基础设施子项**；E.2/E.5/G.4/FR-704 业务未完成（§8.2） |
| I05 语义 / I06 网关 | 不代为完成其验收；不复制网关；不引入未合并语义模块 | I04 侧未出现 I05 语义模块或 I06 网关/凭据模块；`registry.json` 中相关能力仍 `design-only` | **维持未完成（不由 I04 证明）** |

---

## 6. 22 个历史 ID + R3-N1 方法事件的独立判断

判定口径：**以 C4 候选的实际代码与本人本轮独立运行结果为准**；不采信 `round-1-disposition.json` 的 `status`、`round-2-processing.json` 的 `C2ReviewJudgment`、`round-3-processing.json` 的 `C3Judgment` 作为关闭依据；**原 ID 与原等级原样保留**，不上调、不下调。

### 6.1 22 个原 ID

| ID | 原等级 | C4 判定 | 依据（本人本轮核验） |
| --- | --- | --- | --- |
| **B1** | **P2**（非 P1） | **关闭** | Darwin ESRCH 采样竞态现由 `coordinator.py:447-448` 捕获 `ProcessLookupError` 继续走退出码判定；`memory_guard.py:88-89` 仅在 `ESRCH` 时抛 `ProcessLookupError`。在树真实回归 `packages/engine/tests/test_i04_lifecycle_boundaries.py:343-388` 观察到 `(ESRCH, ESRCH, None)` → 真实 1GiB worker `returncode==74` → job 错误 `RESOURCE_LIMIT{memory}`。**本轮 V1 在 macOS arm64 上该 Darwin-only 用例通过（1052 含之）** |
| **Z1** | P3 | **关闭** | C4 的 `candidate-4.json` 为完整 121 文件逐项 SHA 清单，本轮 121/121 与 Git blob 及工作区**双向 0 mismatch**；差异只可能是记录时点问题，已被 `source-lineage-note.json` 显式登记 |
| **Z2** | P3 | **关闭** | 原死分支（`state=="cancelled" and job["state"]=="queued"`）在 `job_store.py:941` 已被单一 `state = "cancelled" if job["state"]=="cancelling" else "failed"` 取代，条件恒可达 |
| **Z3** | P3 | **仍未关闭（按约延期，与 I03 O1 同批）** | `coordinator.py:217-221` 仍只对 `result.page`/`job.list` 施加 `maxPageBytes` 预检，`result.get`/`job.get` 依赖 schema 上界 + `_emit` 兜底。C4 未扩词汇/未改缺省上界，符合"当前不要求改动"的原约定；**不声称关闭** |
| **P1-1** | **P1** | **关闭** | `task-service.ts:119`、`:431`、`:525` 三处退订前均校验 `binding.engineSessionId === 当前会话`（旧会话订阅不再对新会话退订 → 消除 `NOT_FOUND{subscription}` 误伤）；`:437-497` 先 `job.get` 再订阅并以 `stateVersion` 相等为建立条件；`:147-159` 会话 ID 变化即重新对账。三条建议（容忍 NOT_FOUND / 会话变化后强制重查 / 推送需重新对账）均已落地 |
| **P1-2** | **P1** | **关闭** | 96 格矩阵断言在 `packages/engine/tests/test_job_store.py` 源码内逐格存在；逐格只读记录器 `scripts/i04_matrix_evidence.py`（`mode=ro` + `query_only` + authorizer）产出机器可读摘要，**并明确声明 hash/count 仅为执行指纹、不替代源码精确断言**（`:12`、`:458-467`）。`acceptance.md` 的"最终证据要求"列亦已对齐 |
| **P1-3** | **P1** | **阻断性缺陷已关闭；两项字面补救未按字面实现 → 登记为 P3 残留（见 §7-M2，允许延期）** | 实质风险（真实内存超限被降级为 `INTERNAL_ERROR`）已关闭：`test_i04_lifecycle_boundaries.py:343-388` 真实 Darwin 证明 74 → `RESOURCE_LIMIT{memory}`。但 P1-3 字面要求的"采样不可用 → `RESOURCE_LIMIT{memory}`"与"退出码 75 独立分类"未实现；`test_i04_lifecycle_boundaries.py:295-340` 反向钉住"采样不可用 → fail-closed `INTERNAL_ERROR` + 兄弟 job 不受影响"。**我不下调 P1-3 原等级判定权**：原问题标题所指缺陷已关闭，字面差异按 P3 残留登记 |
| **P2-4** | P2 | **关闭** | 跨层上界已统一为"契约层 result.page ≤ 200、job.list ≤ 100；运行时全局上限 200（`resources.py:43`）"。契约校验先于运行时上限，故 job.list 的有效上界仍为 100。`implementation.md:16` 明确记载并给出 200+10 稳定分页 / 201 契约层拒绝的实证。**残留**：I03 `protocol.md:13` 的"分页100条"提议措辞未同步 → §7-M3（文档级） |
| **P2-5** | P2 | **关闭** | 生产端已落地：`coordinator.py:99-127` `_progress` 发 `event:"job.progress"`，`progress:{stage, completed:None, total:None}`（**仅阶段、无捏造百分比**）；`:129-141` `_stage` 在真实阶段边界调用；`:283-306` 订阅建立时补发一次阶段快照。契约与公共例中该事件 4 条正例由 `rawFrames`/`fixtures` 双端消费 |
| **P2-6** | P2 | **关闭** | 65536 唯一请求上限为**有意设计并已文档化+实证**：`coordinator.py:173-175`（`len(self.seen) >= 65536` → `ProtocolFault`，**不淘汰 ID**）；`docs/iterations/I04/implementation.md` 记载每会话最多 65536 唯一请求。真实回归 `packages/engine/tests/test_stdio_session_shutdown.py:155-251`：填至 65534 → 共 65536 被接受 → 第 65537 帧会话致命，**父 stdin 保持开启**、exit 0、stderr 空、无伪造响应；新会话 `restored.count == 7`（无 create/cancel/write 重放）且读到持久 job/marker/result 一致 |
| **P3-7** | P3 | **关闭** | C4 侧已有 `source-provenance-note.json`（C1）与 `source-lineage-note.json`（C4）两处交叉引用，`currentDifferences`/`differences` 字段可回溯到具名说明文件 |
| **P3-8** | P3 | **关闭**（本轮据既有交叉索引改判） | `docs/reviews/I04/round-1-evidence-lineage.json:162` 起 `P3_8_internalReview` **已完整索引**该记录：`record`（path/bytes/sha256 `2bd27560…`/`gitCommit ce6fd54`）、`observedGitHead 83a1228…`、`explicitOriginalScope`、8 条 `selectedFileMapping`（全部 `matchesC1=true`，并标出 `presentInObservedHead=false`）、`wholeTreeReconstruction`（明确"无同期完整可变工作树快照/清单或不可变受审提交，完整树不可重建"）、`dispositionInThisFile`（"澄清范围与不可恢复的历史边界，不臆造替代受审 SHA、不改写旧记录、不以内部审查替代外部双审"）。**该记录是 C1 期历史证据，本就不应被改写为 C4；C4 另有独立的 `c4-internal-review.json` 六条有限审查。** 原"无交叉引用"的说法**不成立**，予以撤回（§7-M8） |
| **P3-9** | P3 | **关闭（登记层面）** | C4 证据索引 `c4-verification.json.rawArtifacts` 登记 **148/148 条原始工件**（本轮核验路径全部存在），早期失败目录已有集中索引；不再存在"未被索引的失败目录"这一缺口 |
| **P3-10** | P3 | **关闭** | `docs/reviews/I04/status.md:7` 显式声明"以下…为按执行顺序保留的历史快照，不是当前完成状态"，历史段落与当前结论已分层，矛盾表述消除 |
| **P3-11** | P3 | **关闭** | 机器可读逐格摘要已产出：`scripts/i04_matrix_evidence.py` → `summary.json` + `cases.jsonl`（含每格 params/outcome、job state/stateVersion/commitProgress/resultRef/error、版本/失效投影与关键表指纹），且 `:418-419` 强制 144/144 完整、缺失/重复/非零退出即红 |
| **P3-12** | P3 | **关闭**（R2 据原要求、原始证据字段与实际 CI 覆盖改判；原 P3 等级保留） | P3-12 原文的两点是**证据字段与自证问题**，非"全 OS 原生矩阵"问题：①"原生'聚焦'证据依赖进程内自证"→ 本轮读回两份原始 `i04-native-verified-evidence.json`（packaged `a19993fd…`、source `e46b8f17…`），**ordinal 2（应用主窗口）带 `focused=true` 且带外部观测记录 `x11Focus={"observer":"xdotool/XGetInputFocus","windowId":"4194323","title":"OntoLearn Studio","visible":true}`**，即外部 X 焦点有**正面证据**，不再是进程内自证；ordinal 1/3 的记录**不含** `focused`/`x11Focus` 键（缺字段，非显式 null，也不得外推为"全部窗口无外部焦点"）；②"原生提示框缺证据字段"→ `nativeDialogs` 已补齐为可核对字段（crash phase windowId 6291458、hang phase windowId 6291613、标题「OntoLearn Studio 窗口恢复」、`visible:true`，`dialogObserver="external xdotool visible-window inventory"`）。原派发 `I04-launch-prompt.md:48` 的原生条款只要求"实际隔离环境"，Linux 隔离环境**源码与包内各六项**真实桌面/native 验收已满足该条款。**"每 OS 跑整套原生可见/外部焦点/原生崩溃恢复矩阵"经核对不属本次强制门禁，另列为建议/未来未验**（§8.2），不作为本候选的开放问题 |
| **P3-13** | P3 | **关闭** | 同 Z2：`job_store.py:941` 的单一条件已取代原死分支 |
| **P3-14** | P3 | **关闭** | `job_store.py:832-839` 在**源码内**给出显式理由："`_transition` owns state-name edges; the running/rounds guard above permits this evidence revision within the same nonterminal state"，并保留 `hook("mid_job_progress")`；`states.json` 未被放宽，P3-14 要求的"说明为何可绕过迁移守卫"已满足 |
| **P3-15** | P3 | **关闭**（本轮据冻结文档改判） | 原残留"文档未逐字说明唯一性由主键保证"**不成立**：`docs/iterations/I04/implementation.md:42` 原文即为"job.create 的 claim 预查仅用于队列预算及幂等早判，权威创建仍在 BEGIN IMMEDIATE 内复验完整指纹，**以 operation 主键保证唯一性**"。实现侧亦相符：`coordinator.py:255-258` 预查在事务外（早期友好拒绝），`job_store.py:479-482` 登记与 `operation TEXT PRIMARY KEY` 主键保证唯一，`:355-362` 事务内复查 → 命中返回原 job（逐字段比对），不一致 `IDENTITY_CONFLICT`。**该残留予以撤回** |
| **R2-N1** | P3 | **关闭** | 原缺"在树确定性回归"已补：`packages/engine/tests/test_i04_lifecycle_boundaries.py:295-340` 以真实 worker + 注入 `MemoryGuardUnavailable` 钉住公共结果形状（目标 job `failed/INTERNAL_ERROR`、兄弟 job `succeeded`、无 operation marker） |
| **R2-N2** | P2 | **关闭** | 根因（期限检查被写在 `except queue.Empty` 分支内、inbox 恒非空即被饿死）已修：`coordinator.py:636-640` 检查移至循环顶端、`inbox.get_nowait()` 之前；期限为单一绝对基准、不因被拒请求续期。**本轮 V5 对 C4 真实打包引擎与源码引擎实测**：约 3.9 万帧持续合法请求下 **5.10–5.11 s 自然退出（exit 0）**；保守尝试上界 39401/38913 < 65536，**排除预算耗尽解释** |
| **R2-P1** | P2 | **关闭** | R2-P1 的三条强制处置：①把时限检查移出 `except queue.Empty`、截止时刻绝对 ✓（同上）；②补默认 `handshakeMs` 的确定性反例 + 单独标注的边界用例 ✓（`test_handshake_deadline.py` 用生产默认 5000 值 + 确定性 busy-inbox；`test_resident_runtime.py:101` 用真实墙钟默认预算；两者分离标注）；③新候选 + 双方全范围复审 —— 即本轮（C4 新候选 121 文件、双方各新建完整任务）。**本轮 V3/V4/V5 对打包件与源码件双路独立复现** |

### 6.2 R3-N1 方法事件（**非产品 P 等级**）

- **定性**：R3-N1 是上一轮**审查探针自身缺陷**（v2 重复 200 UUID 触发重复 ID 会话致命；及时活会话读 stderr 阻塞；`-I` 隐含 `-E` 忽略 `PYTHONPATH` 致初始红臂无效），**不是被审实现的问题**，历史已明确排除出 22 项统计与产品 P 等级。
- **本轮独立判断**：方法更正方向正确（红臂改用显式 `sys.path` 同源 C2 coordinator 对照）；`MAX_TOTAL_REQUESTS` 计的是**写批次**而非请求数（理论 8,000,000，不代表安全低于 65536），实际成功 183/192/193 批 × 每批 200，保守尝试上限 36801/38601/38801 仍 < 65536；旧红臂 63201 响应可核；33.571 s 含明确 stdin EOF 与 `cleanupTimedOut`，**不是**自然握手到期。
- **本轮处置**：**不作为产品问题、不计入 22 项、不要求候选变更**。同时确认其暴露的环境事实已被本轮消除——我的导出根中 `-I` 子进程实际导入本导出包（§2.3）。本轮**自纠**的两项 harness 缺陷（§3.2/§3.3）同样按"探针自身问题"处理：原探针与原输出保留，另写 v2 并明确标注 v1 无效，不计作产品缺陷、不计作独立多条证据。
- **边界**：本轮**不**把 R3-N1 计作产品修复、**不**计作独立多条同内容日志、**不**计作自然超时性能证据。

### 6.3 继承开放项（**单列，不计入 22 项统计**）

| 项 | 原等级/约定 | 本轮判断 |
| --- | --- | --- |
| **I03 O1** 未来词汇/默认上界 | 与 Z3 同批，按约延期 | **仍未关闭**；C4 未扩词汇/未改缺省上界，符合原约定 |
| **Z3** | P3，按约延期 | **仍未关闭**（见 6.1） |
| **I03 O2** `parameterMeanings` 不作 UI 文案 | 语义目录非文案 | **I04 侧满足**；未来业务扩展的映射补充保持开放 |
| **I03 O3 / I01 R6** 历史增长与容量 | 保留原等级开放/延期 | **仍未关闭**；C4 未据合成测量作性能承诺 |
| **I03 F5** 未来语义细码映射 | 实际 producer 接入后适配 | **I04 固定安全错误链已满足**；未来扩展保持开放 |
| **E.2 / E.5 / G.4 / FR-704** 领域业务 | 仅关闭基础设施子项 | **仍未完成**；`acceptance.md:18`、`ADR-0003` 均明写，不由 I04 证明完成 |
| **I05 语义 / I06 网关** | 无产品接线 | **仍未集成**；不代为完成其验收 |

### 6.4 计数声明（避免复刻历史表述差异）

本轮独立计数（**基于 C4 实际字节与本人运行结果，不沿用历史计数**）：

- **22 个原 ID**：**20 项关闭**（B1、Z1、Z2、P1-1、P1-2、P2-4、P2-5、P2-6、P3-7、P3-8、P3-9、P3-10、P3-11、**P3-12**、P3-13、P3-14、P3-15、R2-N1、R2-N2、R2-P1）；
  **1 项按约延期**（Z3，与 I03 O1 同批）；**1 项特殊**（P1-3：阻断性缺陷已关闭，字面差异转 P3 残留登记，非阻断）。
  合计 20 + 1 + 1 = 22 ✓
- **原等级分布（不变）**：P1 = 3（P1-1、P1-2、P1-3）；P2 = 6（B1、P2-4、P2-5、P2-6、R2-N2、R2-P1）；P3 = 13（其余）。
- **本轮阻断未关闭数 = 0**。
- R3-N1 单列为方法事件，**不计入 22 项**，不赋产品 P 等级。
- **不沿用** C3 的"21 closed + 1 deferred"计数，也不因历史处置 JSON 的 `status`/`C2ReviewJudgment`/`C3Judgment` 字段而改变判定。

---

## 7. 本轮新发现（7 项开放 P3 + 1 项撤回，均有处理结论）

### M1（P3）`c4-verification.json` 旧 checkpoint 块的 `checks` 归属错位（**已被 `source-lineage-note.json` 更正，我独立复核通过**）

- **位置**：`docs/reviews/I04/c4-verification.json` → `productionAndDesktopRunCheckpoint`（`source: f504b304266…`，其 `checks[0].log = build/I04-evidence/c4-sealed-check.log`、`checks[1].log = …/sealed-check.log`）
- **触发**：收集脚本按引用保留同一 `checks` 列表后替换末元素，序列化后该块重复指向最终 sealed 记录。
- **影响**：把 9eb0b6e 的 1052/1049 计数误记到 f504b30 名下（该 commit 真实为 1051/1048+3、包 13）。**最终计数本身正确**，仅历史归属错位，不影响任何通过结论。
- **证据（本人独立复核，非转述）**：冻结文件未被覆盖（SHA `327263aab4ae29523ec6967d3e57efde76e52f00f2e1f0c2e406e065b6c5cc53`、61262 B，与说明声明一致）；6/6 原始工件 SHA256 与字节数**逐项吻合**（c4-root/check.log `3f6c88b5…`/5044；c4-final-linux/check.log `19de6002…`/8451；c4-sealed-check.log `58993b43…`/5044；c4-final-linux/sealed-check.log `d8ce5d62…`/8631；c4-sealed-macos-probe/runtime.stdout `c898db7d…`/100；c4-final-linux/sealed-package-probe/runtime.stdout `40055f38…`/100）；4 份日志内计数实测 630TS/1051Py、630TS/1048Py+3skip、630TS/1052Py、630TS/1049Py+3skip；两平台 sealed 包探针各 17 passed / exit 0；包探针谱系互不重贴（C2/C3 期 12/13 → C4 早期 13 → 中期 16 → 终版 17）；**本轮 V1/V3 独立复现同一数字**（630TS/1052Py；包内 17 passed）。
- **结论**：**说明属实、非阻断**。原始错误保留、不覆盖原 JSON；已由 `round-4/source-lineage-note.json` 以 hash 关联方式更正。
- **建议**：下一候选把该块改为显式引用最终 sealed 记录或删除被取代的旧 checkpoint 块，避免同一列表别名问题复发。**允许延期（非阻断，流程级）。**

### M2（P3）worker 退出码 75（`MEMORY_GUARD_EXIT`）未映射独立错误类别

- **位置**：`packages/engine/src/ontolearn_engine/coordinator.py:19`（只导入 `MEMORY_LIMIT_EXIT`）、`:456-458`（仅 74 → `RESOURCE_LIMIT{memory}`）、`:521-522`（其余非零 → `ENGINE_EXITED`）；`memory_guard.py:210-211`（worker 侧守卫不可用时 `os._exit(75)`）
- **触发**：worker 侧内存守卫无法建立/无法继续（Linux `RLIMIT_AS` 失败、Windows JobObject 失败、Darwin 采样不可用）→ 子进程以 75 退出。
- **影响**：父侧归为 `ENGINE_EXITED`（通用退出），用户看到"引擎已退出"而非"资源守卫不可用"。**仅错误分类粒度问题**：不伪造成功、不提交任何数据、fail-closed、兄弟 job 不受影响。
- **证据**：本轮源码通读（`coordinator.py` 未导入 `MEMORY_GUARD_EXIT`；该常量仅在 `memory_guard.py` 与 `worker.py` 使用）。
- **与 P1-3 的关系**：P1-3 字面要求的"75 → guard 不可用"未按字面实现；这是该缺口在本轮的唯一实质残留，按 P3 登记，**不构成阻断**。
- **建议**：下一候选在 `coordinator.py` 增加 75 → 独立固定错误码映射（需同步 TS 侧错误目录，属契约变更，须新候选双审）。**允许延期（非阻断）。**

### M3（P3）分页上界的文档口径不一致

- **位置**：`docs/iterations/I03/protocol.md:13`（"profile 的提议默认：…分页100条"） vs `packages/engine/src/ontolearn_engine/resources.py:43`（`maxPageItems: 200`）+ `packages/contracts/v2/schema.json`（`params_result.page.pageSize` 上界 200、`params_job.list.pageSize` 上界 100）
- **触发**：读者按 I03 文档推断 result.page 上界为 100。
- **影响**：**运行时契约与实现一致**（result.page 200、job.list 100），且 I03 原文已写明"profile 的提议默认…I04 必须通过实际测量再决定运行配置"，I04 `implementation.md:16` 已声明该口径 → 无实现风险，仅文档同步缺口。
- **建议**：下一候选同步更新 I03 `protocol.md` 的"提议默认"措辞，或在 I04 文档加交叉引用。**允许延期（文档级，非阻断）。**

### M4（P3）`c4-ci-trigger.json` 的命名/候选归属易被误读

- **位置**：`docs/reviews/I04/c4-ci-trigger.json:3-9`（`candidate: 3`、`reviewedHead: d3ad536b…`、`pushedHead: 24fd202f…`、`run: 39462746525`）
- **触发**：文件名含 `c4-`，但记录的是 **C3 冻结 head / C3 推送点**的 PR CI；文件内**没有**"C4 CI 尚未运行"的字段（该措辞只在 `c4-verification.json.failuresAndLimits[0]` 与 `status.md:5`）。
- **影响**：仅凭该文件阅读者可能误以为这是 C4 的 CI 结果。文件内容本身准确记录了那一次 attempt1 的真实状态（Linux success / Windows failure / macOS 未取得 runner），不构成虚假通过声明。
- **建议**：下一候选加一行显式 `scope: "C3 push attempt1; C4 CI not yet triggered"` 或并入 `pr-ci-attempt1-*` 系列命名。**允许延期（流程记录级）。**

### M5（P3）`c4-verification.json.currentDifferences` 键无语义定义

- **位置**：`docs/reviews/I04/c4-verification.json:13`（`"currentDifferences": []`）
- **触发**：该键无对照基准定义（sealed vs current？124 输入 vs 什么？），也无对应证据文件，无法自证。
- **影响**：仅影响证据可自证性；同文件 `containerRuntimeIdentity`（count/differences/files）有明确结构，可作参照。
- **建议**：下一候选补齐该键的基准定义与对应证据路径。**允许延期（证据记录级）。**

### M6（P3，**已按既有登记修正定性**）矩阵源绑定与后续变更的边界登记

- **位置**：`docs/reviews/I04/c4-verification.json` → `matrices[*].sourceBinding`（"Mac HEAD at **ccdbadb**"） vs `runtimeSourceCheckpoint`（`9eb0b6e…`）
- **原表述（不成立）**："文档未显式声明后续仅测试提交、未触及矩阵输入"。
- **本轮核对结果（更正是必要的）**：该边界**已被三处显式登记**——
  1. `c4-verification.json.productionAndDesktopRunCheckpoint.unchangedAfterThisRun`："All app/engine/build/config/dependency/resource inputs; only the three explicitly named host test/verification files changed. Source/package GUI and 144 matrices remain valid for identical production/Store inputs."
  2. 同块 `laterChangedHostHarnessFiles`：明确列出 `packages/engine/tests/test_worker_owner_bootstrap.py`、`packages/engine/tests/test_worker_parent.py`、`scripts/verify-i04-package.py` 三个文件；
  3. `docs/iterations/I04/acceptance.md` C4 末段："后续仅三个宿主验证文件变化，生产字节、包哈希及矩阵输入未变，不重跑已绿 GUI。"
  另本轮实测 `matrices[*].sourceFiles` 所列 11 项 SHA **在 C4 head 全部一致**，矩阵输入确未变。
- **残留（仅为可读性）**：`sourceBinding` 字段本身未就地附一句"后续仅测试提交"的就近指针，读者需跨到 `acceptance.md` 末段或 `productionAndDesktopRunCheckpoint` 才能看到。
- **建议**：在 `sourceBinding` 邻近补一行就近指针即可。**非阻断建议，允许延期（可读性级）。**

### M7（P3）顶层 `scope` 的 "Complete" 措辞与并列限制项之间缺显式指针

- **位置**：`docs/reviews/I04/c4-verification.json:19`（`scope: "Complete original I04 acceptance and integration obligations retained"`）与同文件 `failuresAndLimits[0..5]`（6 条未验项）
- **触发**：读者只看 `scope` 可能误读为全部验收已完成。
- **影响**：同一文件内并列存在 6 条明确限制，不存在虚假通过声明；仅缺一个"未完成项清单"指针。
- **建议**：下一候选在 `scope` 后直接附 `failuresAndLimits` 的索引。**允许延期（措辞级）。**

### M8（**撤回**）`internal-runtime-review.json` 不可映射到 C4 —— 本轮核对后**不成立**

- **原表述（不成立）**："该记录在 C4 候选内仍记 `observed_git_head 83a1228…`，5/8 文件 SHA 与 head 不符，**且无交叉引用指明其归属轮次**"。
- **本轮核对结果**：交叉引用**早已存在且完整**——`docs/reviews/I04/round-1-evidence-lineage.json:162` 起 `P3_8_internalReview` 已记录：记录本体（path / bytes / sha256 `2bd27560…` / `gitCommit ce6fd54`）、`observedGitHead 83a1228…`、`explicitOriginalScope`、8 条 `selectedFileMapping`（全部 `matchesC1=true`，并标出 `presentInObservedHead=false`）、`wholeTreeReconstruction`（"Unavailable: no contemporaneous full mutable worktree snapshot/manifest or immutable review-subject commit was recorded…complete reviewed working tree 不可重建"）、`dispositionInThisFile`（"澄清范围与不可恢复的历史边界，不臆造替代受审 SHA、不改写旧记录、不以内部审查替代外部双审"）。
- **判断**：该文件是 **C1 期历史证据**，按定义**不应**被改写为 C4（历史不可覆盖改写）；其"不可重建边界"已被明确登记。C4 另有独立的 `c4-internal-review.json` 六条有限审查（`c4-internal-review.json`，`remainingInternalImplementationBlockingFindings: []`）。**因此 P3-8 判定为关闭，本项发现撤回。** 如需进一步改善，仅是在 C4 侧加一句"本文件为 C1 历史记录，已被 `c4-internal-review.json` 取代"的前向指针，属可选可读性建议，**不作为开放问题**。

### 7.9 未发现掩盖式修复（本人逐项核查）

| 怀疑模式 | 核查结论 |
| --- | --- |
| 全局 `PYTHONUTF8` / `PYTHONIOENCODING` 掩盖编码 | 未出现（全仓 `packages/`、`scripts/`、`.github/` 无命中） |
| 用 skip/xfail 跳过失败用例 | 未新增（仅 `test_i04_lifecycle_boundaries.py` 3 处 Darwin-only `skipif`，**不在** C4 改动内，且 Linux 侧 3 skip 与 CI 基线一致） |
| 修改 expected 迁就实现 | 未发生：3 份契约资源 SHA 在 C3 推送点与 C4 head 完全一致；`test_raw_frames` 断言体未改；公共例计数 321/11/30/9/7/41/51 在本轮 V3 由打包引擎独立复现 |
| 放宽断言 | C4 测试改动中被替换的断言仅 1 行（stderr 的 `os.linesep` 全等比对，仍是全等）；close 清理仅在 `win32 && EINVAL && peer 已退出` 三条件同时成立时容忍，`BrokenPipeError` 保留、其他 `OSError` 仍 `raise`；自然退出/时限/精确响应/error 断言未放宽 |
| 平台特判放宽语义 | 仅 2 处且均不放宽被测语义（stderr 原生换行、finally 清理）；业务断言全部保留 |
| **审查者自身 harness 掩盖/过宽表述** | **本轮自查并已更正 3 处**：v1 正臂字段名与实际时长不符（§3.2/§3.3）；v1 忙箱臂未实测 inbox 占用且迟到 hello 从未被尝试（§3.3）；R2-F1 归属、P3-15、P3-8、M6 四处事实表述（§5、§6.1、§7-M6/M8）。更正均保留原件与原输出，未静默覆盖 |

---

## 8. 未验证事项与范围区分（**区分本次强制门禁 / 范围外或未来未验**）

### 8.1.0 原要求与实际 CI 覆盖的逐条核对（R2 新增，先于门禁判定）

**（a）拥有者原文（本人直接读取，非转述）**

| 出处 | 原文要点 | 是否要求"全 OS 原生矩阵" |
| --- | --- | --- |
| 总控 `iteration-control/2026-10-19/I04-launch-prompt.md:48`（原验收 #8） | "必须覆盖 renderer 崩溃/无响应时已提交数据保留及恢复。**原生可见/焦点/故障恢复放在实际隔离环境或另行明确授权时段**，不能用 headless/最小化/禁 hang monitor/stub 原生提示抵扣。" | **否**。要求"一个实际隔离环境"，未要求逐 OS 执行 |
| 同文件 `:22`（隔离验证与继承风险） | "可以在既有daemon中准备本线隔离的Linux虚拟显示测试环境，无用户Mac测试窗口…**daemon存在不等于验收，arm64不冒充CI架构，真实跨平台CI仍必跑**" | **否**。Linux 隔离虚拟显示环境是**已授权**处所；"真实跨平台CI仍必跑"指 CI 整体必跑，不是每 OS 跑完整 I04 native 矩阵 |
| 同文件 `:74`（验证要求） | "桌面 e2e 与原生恢复仍属必验，当前本机只执行无窗口工作，**缺隔离环境则保留待验**" | **否**。属必验**类别**；隔离环境已提供 |
| 批准的 M0 计划 S2 退出门槛第 4 条（`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md:122`，与 `docs/reviews/I03/inputs/…` 同内容） | "requestId/jobId/项目/会话不串线；页面刷新或重建可查询任务状态。renderer 崩溃/无响应时保留已提交数据并按规则恢复，不能自动再发写入。" | **否**。是**能力**要求，无全 OS 原生可见/外部焦点矩阵 |
| C1 P3-12 原文 | "原生'聚焦'证据依赖进程内自证；原生提示框缺证据字段" | **否**。是**证据字段/自证**问题，非矩阵要求 |

> 结论：**没有任何拥有者文本规定"全 OS 原生可见·外部焦点·原生崩溃/无响应恢复矩阵"为本次强制门禁。**

**（b）实际 CI 覆盖（本人直接读取 `.github/workflows/ci.yml` 与 `tests/e2e/i04-jobs.spec.ts`）**

- `Quality`（ubuntu-latest）执行 I04 的 native recovery、reload、coordinator exit 三步（`:52-72`，`xvfb-run + openbox`，注入 `I04_TEST_FIXTURE` / `I04_NATIVE_ISOLATED=1`）。
- `desktop`（macos-latest / windows-latest）只执行 `npm ci`、`uv sync --frozen`、`npm run engine:check`、`npm run typecheck`、`npm run build`、`npm run test:e2e`、`npm run package:dir`、`verify-i04-package.py`（`:105-130`），**不注入** `I04_TEST_FIXTURE` / `I04_NATIVE_ISOLATED`。
- `tests/e2e/i04-jobs.spec.ts` 三条 I04 桌面规格的 skip 条件为：reload `:22` `!fixturePath`；coordinator exit `:99` `platform !== 'linux' || !fixturePath`；native `:317-318` `platform !== 'linux' || I04_NATIVE_ISOLATED !== '1' || !fixturePath`。
- 推论：**macOS/Windows 的 CI job 会跳过这三条规格**，即使其变绿也**不覆盖** I04 的整套原生可见/外部焦点/原生崩溃恢复行为。
- 但**Windows engine 层**的真实执行在强制 CI 路径内：`npm run engine:check` 在 windows-latest 运行全部 pytest，含 `test_worker_owner_bootstrap.py` 的 Windows 分支（真实活 PID + 错误创建时间、真实 FILETIME/句柄比对）与 `test_worker_parent.py` 的真实 `OpenProcess`/`WaitForSingleObject`/实际协调器 kill 3 秒回收。

### 8.1 本次（I04）合并前的强制验收门禁

| 事项 | 状态 | 依据 |
| --- | --- | --- |
| **真实三平台 CI 必须实际运行并全绿** | **未完成**。Windows attempt1 在 `npm run engine:check` 失败 39 条且后续 `typecheck`/`build`/`test:e2e`/`package:dir`/`verify-i04-package.py` **全部 skipped**，其 Windows 状态至今未知；macOS attempt1 为 `runner_id=0`、`steps=[]`、`conclusion=cancelled`，官方 annotations 为"未取得 hosted runner"+"macOS arm64 容量约束" → **无任何代码被执行**，既非通过也非失败；Linux Quality job 24 步全 success（1017 passed/3 skipped、630 TS、包内 13 runtime 与公共例通过） | `build/I04-evidence/pr-ci-*`；`c4-verification.json.failuresAndLimits[0..2]`；`acceptance.md` C4 段 |
| **Windows engine 层真实执行**（ABI / FILETIME / 句柄 / 创建时间比对 / 实际父死亡 3 秒回收 / 读前拒绝 73） | **未运行**。C4 的 Windows 结论全部来自本机策略反例与 `ctypes` 替身（`test_worker_owner_bootstrap.py` 文件头自述"only Windows CI can establish actual native behavior"）。该覆盖由 `npm run engine:check` 在 windows-latest 完成 → **在强制 CI 路径内**。C4 候选**未声称** Windows 通过 | `c4-verification.json.failuresAndLimits[1]`；`c4-internal-review.json` `findings[1].disposition`；`ci.yml:125` |
| **macOS / Windows 的 engine:check · typecheck · build · 普通 test:e2e · package:dir · verify-i04-package** | **未运行**（attempt1 未取得 runner / 下游 skipped）。合并前必须在真实 macOS 与 Windows runner 上全绿 | `ci.yml:105-130`；`pr-ci-attempt1-final-jobs.json` |
| **C4 三平台 CI 本身** | **未触发**。C4 尚未推送；PR #5 仍指向 C3 推送点 `24fd202`，未合并 | `c4-ci-trigger.json`；`status.md` |

> 说明：上述各项是**本次合并前的强制门禁**，C4 候选未对其作任何虚假通过声明。
> **重要区分**：真实三平台 CI **不覆盖** §8.2 的全 OS 原生矩阵（三条 I04 桌面规格在 macOS/Windows 被自身门控跳过）；
> 因此"将来三平台变绿"**不得**被写成"全 OS 原生可见/外部焦点/原生崩溃恢复已通过"。

### 8.2 建议 / 未来未验（**不属本次强制门禁，且不会被本次三平台 CI 覆盖**）

| 事项 | 状态 |
| --- | --- |
| 全 OS（macOS / Windows）原生可见·外部焦点·原生崩溃/无响应恢复矩阵 | **非原要求**（§8.1.0(a)）；原条款已由 Linux 实际隔离环境满足（源码/包内各六项，含外部 xdotool 可见窗口清单、真实原生提示框、hang monitor 开启、crashed/unresponsive 事件）。若将来要在其它 OS 复跑整套原生矩阵，属**增强建议 / 未来未验**，不作为本次候选的开放问题，也不作为合并门禁 |

### 8.3 范围外 / 未来未验（**不属 I04 合并前置**，仅登记明确未完成）

| 事项 | 状态 |
| --- | --- |
| 签名发布、干净设备安装 | 未验；原 M0 Q2/Q3/Q6 等决策与签名验证**不由本 ADR/迭代替代** |
| 生产语义与生产环境部署 | 未验；原 M0 计划把生产语义与领域能力留给后续阶段 |
| 领域业务 E.2 / E.5 / G.4 / FR-704 业务执行与结果页 | **仍未完成**；I04 只关闭 F6 基础设施子项（真实 worker/Job/Store/轮次/摘要/分页），**不得**注册为业务能力 |
| I05 语义能力、I06 网关/凭据 | **仍未集成**；I04 无产品接线，不代为完成其验收 |
| I03 O1（未来词汇/默认上界）、I03 O2/O3、I01 R6（历史增长/容量） | 保持原约定：按约延期 / I04 侧满足但未来扩展开放 / 原等级开放延期 |

> 上述各项**不会被本次三平台 CI 一并覆盖**，其完成条件属于后续里程碑（Q2/Q3/Q5/Q6/Q7/Q8/Q9）与 I05/I06 各自范围。

---

## 9. 最终结论

**通过（Pass）—— 针对冻结候选 C4：`e45e6038b5e0f8f4adc69ed55aafccd75b3d3500` → `8f8eda1e24c0425ea2a65d2566978913ee310b8b`（121 文件）。**

判定依据（本人本轮实际执行/核验，非转述）：

1. **候选身份自证**：121 文件清单与 Git blob、工作区**双向 0 mismatch**；独立导出 776 blob 逐字节一致；`-I` 子进程确认导入本导出包。
2. **聚合验证真实绿**：隔离导出根 `npm run check` **rc=0**（630 TS / 1052 Py）。
3. **包内路径真实绿**：对 **C4 真实 macOS 打包引擎**（SHA `1f5a5eb8…`）执行候选自带 `verify-i04-package.py` **rc=0**、**17 passed**；打包资源 SHA 与本候选契约**逐项相等**；公共例 321/11/30/9/7/41/51 通过。
4. **最高风险点独立证伪且证据已按 harness 缺陷更正**：修正版探针 v2 对**冻结件与源码件**各跑一次——正臂真实存活 **6592.7 / 6604.8 ms**（> 生产 5000 ms），有界 EOF 收尾后**自然退出 exit 0**（非 SIGKILL）；忙箱臂约 3.9 万帧持续合法请求下 **5.10–5.11 s 自然退出 exit 0**，保守尝试上界 39401/38913 < 65536 排除预算耗尽解释；"迟到 hello 被拒绝"由在树确定性测试与代码路径承担，不误引探针。**R2-N2 / R2-P1 实质关闭**。
5. **22 个历史 ID 逐项独立判断**（§6.1）：19 关闭、2 部分关闭/按约延期、1 项（P1-3）阻断性缺陷关闭并转 P3 残留；**原等级原样保留**，C1/C2/C3 的不通过记录与原等级未被改写或自动关闭。
6. **本轮更正全部落实（R1 8 项 + R2 范围核验）**：R1 —— 4 处事实表述改判（P3-8、P3-15、R2-F1 归属、M6）、2 处 harness 缺陷自纠并保留原探针与原输出（§3.2/§3.3）、1 处计数修正（§0）、1 处范围精确化（§8）；R2 —— 依据总控 `I04-launch-prompt.md:22/48/74`、M0 S2 退出门槛第 4 条与 `.github/workflows/ci.yml` + `tests/e2e/i04-jobs.spec.ts` 的实际门控，修订 §0/§4.8/§6.1(P3-12)/§6.4/§8.1/§9 的范围表述与计数（新增 §8.1.0 原文核对表），并按原始证据字段更正"窗口级 focused/x11Focus 显式为 null"的过宽表述（ordinal 2 实为 `focused=true` + 外部 `xdotool/XGetInputFocus` 记录）。更正后**未发现任何阻断级实现缺陷**；开放发现为 7 项 P3，均有处理结论与允许延期裁定（§7），另 1 项（M8）经核对撤回；22 项历史 ID 计数为 **20 关闭 + 1 按约延期（Z3）+ 1 特殊（P1-3）**。
7. **无掩盖式修复**（§7.9，含对本审查者自身表述的 3 处自查更正）。

**限制与不授权声明**：

- 本通过**仅覆盖本冻结候选在本轮可执行范围内**的原验收与集成义务。
- 本通过**不覆盖** Windows engine 层真实执行（ABI/FILETIME/句柄/创建时间比对/实际父死亡）与 macOS/Windows 的 engine:check·typecheck·build·普通 test:e2e·package:dir·verify-i04-package，即 **C4 三平台 CI 全绿**（§8.1）。
- §8.2 的全 OS 原生可见·外部焦点·原生崩溃/无响应恢复矩阵**非原要求**，且**不会被本次三平台 CI 覆盖**（三条 I04 桌面规格在 macOS/Windows 被自身门控跳过）；不得因其将来变绿而写成已通过。
- §8.3 所列签名、干净设备、生产语义、领域业务、I05/I06、I03 O1/O3/I01 R6 **明确未完成且不由本次 CI 覆盖**；它们**不是** I04 合并前置，不得被本报告当作已覆盖或已完成。
- 本通过**不构成推送/合并授权**。后续门禁仍为：双方同版明确通过 → 推送 feature → 实际三平台 CI 全绿 → 遵守分支保护正常合并 develop → 远端核验。任何受审实现/测试/配置/依赖/验收/基线变化，须新候选 + 双方新完整任务，本轮结论不得沿用。

---

## 附录 A. 本轮实际产物与写入边界

| 路径 | 内容 |
| --- | --- |
| `docs/reviews/I04/round-4/minimax-m31flash.md` | **本报告（primary 内唯一受审证据写入）** |
| `build/I04-review-MiniMax-M31Flash-C4/source` | 独立导出源码（`git archive` 776 blob，逐字节一致） |
| `build/I04-review-MiniMax-M31Flash-C4/{.venv,node_modules,uv-cache,npm-cache,tmp,logs}` | 独立依赖/缓存/临时/日志 |
| `build/I04-review-MiniMax-M31Flash-C4/logs/npm-run-check.log` | V1 聚合 check 完整日志（rc=0） |
| `build/I04-review-MiniMax-M31Flash-C4/logs/pkg-verify-out/` | V3 包内验证产物（`resources.json` / `common-examples.json` / `runtime.stdout` / `runtime.exit`） |
| `build/I04-review-MiniMax-M31Flash-C4/tmp/probe/handshake_probe.v2.py` | 修正版探针（正臂 >5s + 有界 EOF/wait；忙箱臂 planned/attempted/received 区分） |
| `build/I04-review-MiniMax-M31Flash-C4/tmp/probe/evidence/` | v1 原探针与原输出（保留）、v1 有效性边界说明、v2 两份实测输出 |
| `build/I04-evidence/minimax-r4-probe-corrections/` | 上述探针证据的**总控可见副本**（新建目录，未覆盖既有 148 件工件中的任何一件，已抽查 5 个原工件哈希不变） |

未修改：实现、测试、依赖、配置、验收、契约、任何冻结 JSON；未 `git add`/`commit`/`push`/`checkout`；保护 `AGENTS.md`（SHA `db1fb184…`）未改未 stage。

## 附录 B. 被更正的 v1 探针（原件保留）

| 文件 | 原始事实 | 有效性裁定 |
| --- | --- | --- |
| `handshake_timely_probe.v1.py` + `.v1.output.{packaged,source}.json` | 正臂实际约 2.1 s；输出字段名 `stillAliveAfter7s` 与实际时长不符；`p.kill()` 后未 `wait()` | **无效**，不作为本轮任何结论的依据；由 v2 正臂（真实 6.59/6.60 s + 自然 EOF 退出 0）取代 |
| `handshake_flood_probe.v1.py` + `.v1.output.json` | 36200 成功写、35562 响应、5.12 s 退出 exit 0、迟到 hello 计划 5.6 s 但脚本约 5.52 s 即退出（**很可能从未被尝试**）、未观测 inbox 占用 | **部分有效**：持续合法负载与自然退出成立；"迟到 hello 被拒绝"与"inbox 永不排空"**不成立**，已由 v2 与在树确定性测试/代码路径承担 |
