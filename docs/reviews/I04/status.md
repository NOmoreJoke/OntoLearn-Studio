# I04 常驻协调器与 ExecutionJob

同一 Goal；会话 01a15899-4318-7522-8035-353e88d34de4。2026-10-20 已实际接收完整 Goal 第九节与无桌面打扰约束。

当前阶段：C1 双指定模型均明确不通过，原报告完整保留于 round-1。修复候选 C2 已完成本地、隔离与包内验收并集成主线，准备冻结后提交新版双审；准确受审头与文件清单见 candidate-2.json。当前修复及新验证见 reconnect-verification.json；原 cf83e18 检查点保留在 Git 历史及本地 c2-history，不冒充最新验收。真实三平台 CI、推送、PR、合并与远端核验均未完成。

以下“范围与门禁”至“用户确认恢复后的检查点”为按执行顺序保留的历史快照，不是当前完成状态。后续 C1 派发/终审记录另有时间标题。

- worktree: /Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs
- branch: feature/I04-resident-jobs
- base: e45e6038b5e0f8f4adc69ed55aafccd75b3d3500
- origin: https://github.com/NOmoreJoke/OntoLearn-Studio.git；目标 develop
- 初始仅 AGENTS.md dirty，SHA256 db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786，禁止 stage。

## 范围与门禁

采用总控 I04-launch-prompt.md 的完整原验收及实际合并 I03；只做 S2 基础设施，不接 I05/I06 业务。主会话独占共享 contracts、入口、registry、build-engine；I03 R2-F1 必须在 Python 通知消费者接入前修复。I05 entry/build 交接已接收，后续整合保留其 probe/metadata/collect-all/inventory/license 行为，不提前复制未合并依赖。

原验收、静态/运行/包内/桌面证据、双指定模型同版明确 Pass、意见处置、真实 CI、正常 PR 合并和远端核验全部保留。启动时尚无开发/运行/审查/合并通过证据（历史启动快照）。

## 文件责任与集成顺序

模块子任务各自独立 worktree/feature 分支，从同一 base 开始；不得改他人所有文件，不 stage 保护指南，不共享可变依赖/DB/输出。

| 负责人 | 唯一文件范围 | 接口/依赖与集成 |
| --- | --- | --- |
| 主会话 | Python coordinator.py/worker.py/protocol.py/__main__.py/entrypoint.py、contracts 及资源、scripts/build-engine.mjs、I04 总验收文档与集成测试 | 消费 JobStore 服务；协调唯一规范与资源；统一 cherry-pick 后联验 |
| storage agent | storage.py、job_store.py、新 test_job_store.py | 同一 SQLite；JobStore(Store) 负责持久 DTO/claim/plan/blob/results/cursors、原子提交与 fence 后 reconcile；不得改共享规范 |
| supervisor agent | main/engine.ts、main/jsonl.ts、新 supervisor/jsonl unit tests | EngineSupervisor 持久进程、严格帧/hello/pending/路由/超时；调用 request(method,params) 仅限主进程；健康及停止接口 |
| bridge agent | main/index.ts、新 main/task-service.ts、preload/index.ts、renderer、contracts/src/index.ts、新 bridge unit tests/e2e I04 专用文件 | 窄业务 bridge；消费 EngineSupervisor.health/request/stop；主进程受信项目上下文，重建只查询/订阅，不重发任务；index.ts 契约文件临时单一责任属该 agent，其他 contracts 主会话 |

顺序：独立纯模块/真实存储验证并行→主会话审查接口并 cherry-pick→真实进程/worker/SQLite/bridge/隔离窗口/包内联验→独立只读 agent 检查→冻结→指定双审。内部通过不代替外部审查。

## 启动时待执行（历史）

启动时待办：完整实现、原矩阵验收、隔离环境准备、依赖安装、双审/推送/PR/CI/合并。协调器旧写者 fencing、完整终态证据、F6 真轮次结果链路和原生恢复均不得用替身抵扣。

## 2026-10-20 初始实现检查点

实际 get_goal 已读回本会话独立 Goal active，覆盖开发至合并远端核验。三条子线已实际创建 /root/storage、/root/supervisor、/root/bridge，worktree 依次为同级 I04-storage / I04-supervisor / I04-bridge，branch 依次 feature/I04-storage / feature/I04-supervisor / feature/I04-bridge。监督子线 3066c16 已 cherry-pick 为 7e833e6；只含 engine.ts/jsonl.ts 与两份专用 unit tests。

- 主线独立 npm ci / uv sync --frozen 成功；未改依赖/锁。
- 可信 binding 单字段24历史差异+合法控制/更多畸形回归，共41例双端定向通过；修复为缺字段/类型/状态安全拒绝，不将公共wire误称权限漏洞。
- 共享 raw frame corpus 已生成并用于两端测试；TS reader/supervisor/binding131例通过，Python协议/契约定向502例通过。尚非完整check或全验收。
- schema修订原因：I03文档要求未握手其他方法返回HANDSHAKE_REQUIRED，但旧response仅hello允许session=null；新增严格bootstrap错误分支，仅非hello、null session、HANDSHAKE_REQUIRED或VERSION_INCOMPATIBLE，不放宽成功/已握手错误。本修订须在完整I04候选双方新审。
- Docker既有daemon创建本线容器 ontolearn-i04-isolated（ID933e69810dcd），arm64，独立容器文件系统、无宿主依赖挂载；准备Xvfb/openbox/xdotool/uv成功。尚未运行桌面验收，不等于CI架构/平台通过。未启动用户Mac Electron/native/HMR窗口。
- 原失效计划路径不在Git基线；已读I03 inputs内冻结原文。I05纯错误适配接口已建议由原线独立维护，实际Store/Job/bridge联验仍等待本线接口，不注册语义。

## 首次真实集成与独立审查修复

存储8a5b7fb/e1490c1/bde0937、bridge8f493969、内存守卫52883da及独立真实生命周期回归fd4b448均已串行集成；相应主线提交3ccb709/fc04801/0610c3f/94cc6bf/e387516/8256fa4。独立审查者提出的超时范围、输入drain阻塞、终态后round、401位整数、Darwin rlimit不可用、取消DTO非法字段/queued快照、round版本递增、通知去重均已按真实反例修复；额外可信异常类型/启动完成后接管/事件循环让出也已实现，尚待最终全量复核。

首轮真实runtime 1/6成功、5失败如实保留build/I04-evidence/logs/I04-runtime-initial.*；主要为Darwin guard不可用及取消DTO不符，不能称首轮全绿。修复后真实常驻进程/worker/SQLite六项已通过（含两种pending事件、正式原子完成后取消、杀协调器保留已提交轮次并fence恢复）。full-check-2真实exit0，570 TS、851 Python，但后续又有新review回归和来源修复，尚非冻结候选最终证据。12份归档源核验通过，原仓库64受保护文件实际SHA比对无差异。

Darwin守卫采用实际libproc RSS监控+受控基础设施分配前预算，明确不是硬AS限制，采样间可超出阈值；Linux RLIMIT_AS与Windows JobObject需各平台实际验证。当前仅有限测试工作负载，不据此批准I05/native语义库的任意内存行为。新增真实memory/生命周期测试结果仍需主线最终执行。

## 用户确认恢复后的检查点

上一 turn 实际 interrupted；get_goal 实际返回 paused，threadId=01a15899-4318-7522-8035-353e88d34de4，createdAt=1792487817。用户随后明确回答“恢复同一 Goal 继续执行”，依该指令续跑原目标。工具无 resume 字段，恢复时原记录仍显示 paused；记录接口限制，不重建 Goal、不编造 active。Git、原失败日志和容器现场保留。

- smoke2 的 canonical PERMISSION_DENIED 与旧字符串断言不匹配；旧日志和 trace 保留 linux-smoke2。仅更新断言后隔离 smoke3 实际 exit0，1 passed。preload 运行依赖已正确打包，旧缺失故障不当作当前故障。
- 独审发现宿主环境向 Python 继承潜在凭据；b5d2993 与 worker 显式最小环境修复，真实 worker 自造 sentinel 回归通过，未读取真实凭据。包内最小环境尚待当前候选验证。
- 9545195 集成 F6 多页 ledger、完整绑定、48 项轮次故障矩阵和回收后完整 claim 幂等。子线223项通过。主线12项真实 runtime 通过，包含跨页稳定重读、真实新结果替换后正常 GC、历史保留、回收安全拒绝及四种物理摘要损坏反例。第一次 GC 探针因旧结果仍受 current 保护未回收，修为真实新运行替换；未放宽保护。
- 0986f73 修复同文档锚点不解绑订阅；合法早到 atomic 通知与初次 restore 竞态正在闭环。候选尚未冻结，外部双审、推送、CI 和合并未开始。

## Candidate 1 external review dispatch

Frozen base e45e6038b5e0f8f4adc69ed55aafccd75b3d3500 -> head ce6fd54fd51bb16a6eda5f45d2675506799710f5; 71 files. candidate-1.json records exact hashes and protected dirty AGENTS. Both new tasks were actually created through CUA: ZCode GLM-5.3/highest and MiniMax M3.1-Flash/xhigh, exact I04 folder and feature branch verified. Dispatch labels are correlation labels, not invented native UUIDs. Full prompt and UI evidence hashes are in round-1/dispatch.json. Both were observed running; no Pass or report-complete claim. Shared out/build/release reservation belongs only to ZCode until actual release; candidate code remains frozen.

## Next-candidate preparation, outside the frozen checkout

C1 ce6fd54 remains frozen and both external tasks remain running. Controller audit identified missing complete assertions in the existing 96-cell atomic matrix; storage commit cf6e1a8 strengthens only that test, independently reviewed and 96/96 passed. It is not yet in this checkout.

An independent actual coordinator-kill probe at pending=0 also demonstrated no view reconnection/status update and an old-subscription NOT_FOUND on the first manual restore. Probe and synthetic evidence remain in I04-bridge/test-results/i04-disconnect-probe.{cjs,json}. This is a confirmed next-candidate P2, not a claim that C1 was fixed.

Preparation worktree: /Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-reconnect (see exact path below). Root-owned contracts/App/isolated-e2e responsibility is at sibling I04-reconnect, branch feature/I04-reconnect, base ce6fd54, with independent npm/uv environments and outputs. Actual path is the same parent .worktrees/I04-reconnect. Supervisor owns engine.ts lifecycle event commit 9fe17f7; bridge owns TaskService/tests bounded read-only reconciliation. Root contracts commit 0ba6840, App e7a39d3, matrix integration 5caeb1d, UI fault-test 910fcdb/04657f6 are only in that separate worktree. TaskService integration, full verification, new freeze and both fresh full external reviews remain required. No source/config/test/acceptance in the C1 checkout has changed.

## Next-candidate validation checkpoint (C1 still frozen)

Root's separate I04-reconnect checkout integrated bridge e78b41a as d3a8070. Its no-window full check passed 609 TS / 992 Python; macOS arm64 package and packaged CLI/common-example plus 12 runtime probes passed. Independent Linux arm64 check passed 609 TS / 991 Python with one Darwin-specific skip. Actual isolated source coordinator-kill recovery, reload/safe errors, native crash/visible focused unresponsive and generic desktop/CSP tests passed. Linux package/common examples/runtime probe passed; packaged GUI tests are in flight. The first cloned-container check failed by scanning previously packaged dependency trees before Git metadata existed; full raw log is preserved, a fresh `git init` restored normal ignore discovery and the full check passed. No product source or test exclusion was changed for that failure.

Independent review then reproduced a project/commit-marker read race in d3a8070 with real Python/worker/SQLite: a delayed actual project.get revision 0 response followed by actual atomic completion could return project revision 0 with succeeded job marker revision 1. Bridge is fixing all restore paths in its own worktree, with the initially failing real regression retained. This next-candidate issue is open; current results are intermediate evidence, not final candidate acceptance. Both C1 external reviews remain running and their source checkout remains unchanged.

## Additional real failure preserved before C1 review completion

The next worktree's second full check (7e58f08) passed 619 TS and 991 Python but failed test_memory_failure_isolated_from_other_project_real_worker: expected RESOURCE_LIMIT(memory), actual INTERNAL_ERROR. Its coordinator.py/worker.py/memory_guard.py/lifecycle-test bytes were independently hashed equal to C1 ce6fd54. The original full raw log and exact hash proof were copied into build/I04-evidence/next-candidate-memory-failure.{log,json}, and the same observation was actually sent through CUA to both still-running C1 tasks; both visibly received it before terminal report completion. No other model's conclusions were disclosed.

Independent actual libproc/worker/SQLite probes confirmed the Darwin child-exit sampling window: kernel ESRCH while asyncio returncode was temporarily None, then actual child exit 74. Natural repetition first reproduced on iteration 69; holding only parent delivery in the real sample reproduced 10/10. Formal next-worktree commit cf83e18 distinguishes only actual nonpositive libproc read+ESRCH, lets the parent reconcile the owned child's real exit, narrows the parent's catch to ProcessLookupError, and keeps worker monitoring faults fail-closed. Its targeted 20 tests passed, an independent production-source probe passed 10/10 with the other project succeeding, and real monitor-fault subprocesses exited 75 without diagnostics. Final full check/package revalidation is in flight. C1 itself remains unfixed/frozen and neither external review has completed.

## C1 ZCode terminal report received

ZCode GLM-5.3/highest actually completed; full 145-line report was read and terminal UI captured. Final conclusion 不通过: B1 P2 Darwin RSS child-exit classification race is the sole blocker; Z1 manifest timing/Z2 unreachable reconcile branch/Z3 future non-paged response budget are P3 explicitly deferrable. Report SHA and terminal AX SHA are in round-1/dispatch.json. Its suggested broad MemoryGuardUnavailable catch is not automatically adopted: next-worktree cf83e18 instead distinguishes only actual kernel ESRCH and preserves fail-closed monitoring, to be judged by both new reviews. ZCode explicitly released shared outputs. MiniMax remains running; C1 is still frozen.

A further independent original-requirement audit confirmed no actual job.progress/stage producer despite launch acceptance 4/S2 exit 2 requiring phases without invented totals. Real Python/worker/SQLite probe observed zero progress events for test.read/test.atomic/test.rounds. This is a new P2 next-candidate gap; bridge temporarily exclusively owns coordinator/new progress tests in its own worktree, preserving formal ESRCH precondition. Root next-worktree 7d3529a adds a compact 16-entry UI progress cache admitted only after matching authority generation/project/job/input/stateVersion, with 11 policy tests passing and real desktop stage assertions prepared. Producer integration and renewed validation remain outstanding.

Eight leftover CPU-load loop children from ZCode's completed 40-run probe were individually reidentified by exact PID/parent/command/checkout and terminated with bounded SIGTERM; all eight gone, no other processes touched. Raw identity hashes and result in build/I04-evidence/zcode-load-cleanup.json.

## Both C1 reports completed and read; next candidate still required

MiniMax M3.1-Flash/xhigh also actually completed, terminal UI and all 325 report lines read. C1 final conclusion 不通过: P1-1 reconnection/P1-2 matrix evidence/P1-3 resource category; additional P2 page limit/stage producer/session request lifecycle and P3-7..P3-15 evidence/cleanup/guard-rationale items. All fifteen IDs plus ZCode B1/Z1–Z3 must have dispositions; the report's narrative P3 count is not used to omit its ninth numbered P3 item. Native model settings remain verified through CUA. Report/terminal AX hashes recorded in dispatch.json. Neither old report will be overwritten or reinterpreted as Pass.

All 70 non-process files in candidate-1.json were rehashed unchanged after both terminal reports. C1 source freeze remained intact. A direct raw-path audit also resolved all 722 source-manifest entries in ce6fd54 with zero absent files; the five byte differences are approved dirty AGENTS plus the four documented docs. MiniMax's 33 absent-path claim is preserved in its report and factually challenged in source-provenance-note.json for both next reviews, without changing its Not-Pass.

New next-candidate findings are being resolved in independent worktrees: progress producer/UI early delivery (bridge/root), default result page support 200 (root, actual SQLite page 200+remaining 10 proven), safe input-reader exit at the 65536 session budget (supervisor actual stdio found SIGABRT from buffered daemon reader; fix in progress), and JobStore unreachable branch/rationale (storage). Matrix per-cell machine evidence is assigned only to storage's new script; native external X focus/dialog evidence only to root. The finite session budget must preserve all prior IDs for anti-replay and explicitly disclose possible in-flight failure; it is not an unlimited same-session guarantee. No push/PR/CI/merge yet.

## 2026-10-20 C2 修复与完整验证检查点

C1 原不通过及全部 P 等级保留；处置见 round-1-disposition.json。实际修复自动只读恢复、投影提交竞态、迟到健康回复、Darwin ESRCH 退出竞态、分页默认 200、真实未知总量阶段、65536 有限会话及父 stdin 开启时干净退出；补齐 144 格精确断言/逐格证据、外部 X 焦点与原生提示框字段、死分支清理和存储守卫说明。独立内部审查证据不替代指定双审。

macOS 无窗口 check 为 630 TS/1015 Python；隔离 Linux arm64 为 630 TS/1013 Python+2 Darwin 专属跳过。源码及包内各六项桌面/健康/CSP/reload/协调器退出/native 验收通过；两个平台 package、公共例及各12项真实包内runtime通过；矩阵两平台各144格通过。驱动 sandbox 前置失败及早期真实故障保留于索引，不记作当次通过。最终冻结/完整新双审、远端三平台 CI 与正常合并仍待执行。

## C2 冻结前集成核验

feature/I04-reconnect 已正常合入 feature/I04-resident-jobs。主线 122 份非文档输入逐文件 SHA 与实际验证输入一致，原仓库64保护文件与 AGENTS 均未变。最新 macOS/Linux 完整 check 覆盖新增 recorder 与 CI 接线后源码；来源核验12份通过。独立 bridge/supervisor/storage 检查已分别留证；最后归属表述与历史时点文案已校正，无运行源码变化。冻结后仅追加派发/报告流程记录，不修改实现、测试、配置、依赖或验收。

## 2026-10-20 C2 实际双审派发

冻结完整 e45e6038→0462e0825f3bda2774ce5d43f4422327f2d5fbd9，共93文件，candidate-2.json逐文件SHA。通过实际CUA各新建ZCode GLM-5.3/最高、MiniMax Code M3.1-Flash/xhigh独立任务，精确primary目录/feature分支及模型思考均核验，完整原验收/Goal第九节/无宿主GUI/旧C1报告处置已透传。两任务实际运行中，均尚无最终结论。共享out/build/release仅ZCode预约；MiniMax无冲突验证使用独立目录，禁止本轮相互读对方报告。派发证据见round-2/dispatch.json。受审93路径冻结；仅追加流程证据。

## 2026-10-20 C2 Round-2 MiniMax 复审结论（MiniMax Code · M3.1-Flash / xhigh）

独立只读复审完成，报告见 docs/reviews/I04/round-2/minimax-m31flash.md。候选完整性由本人逐文件重算核验：candidate-2.json 声明93文件与 git show HEAD:<path> 逐字节93/93一致，声明集合与 base→head 实际 diff 集合完全相等（43提交，+33117/−236）。隔离 export 环境（build/I04-review-MiniMax-M31Flash-C2，未写共享 out/build/release、未启动宿主 GUI）独立复现：Python 1015 passed、TS 630 passed/15 files、typecheck exit 0、矩阵 recorder 144 passed（atomic 96/96、round 48/48、逐格只读DB捕获144）且负对照5例通过时 recorder exit 1 证明缺格不被计数掩盖、CI 同款 --i04-matrix-source-revision HEAD 144 passed；另实测 ESRCH fail-closed 语义与10/10竞态用例、job.progress 真实5阶段且 completed/total=null、result.page 三层上界200与 job.list 100、越权 NOT_FOUND/PERMISSION_DENIED、协调器 kill 后已提交轮次保留且不重放、reconnect-verification.json 71/71 artifact SHA 全匹配。

历史条目逐项判断：P1-1/P1-2/P1-3/B1 四个阻断级问题确认关闭；P2-4/P2-5/P2-6/P3-7/P3-8/P3-9/P3-10/P3-11/P3-12/P3-13/P3-14/P3-15 及 Z1/Z2 确认关闭；Z3 与 I03 O1/O3、I01 R6 维持原延期/开放登记未上调。

结论：通过。新增1项P2非阻断发现 R2-P1：handshakeMs=5000 仅在 coordinator.serve() 的 except queue.Empty 分支检查（coordinator.py:632-640），inbox 恒非空时时限不成立——本人实测控制组5.155s退出 vs 洪泛组10.639s/65536响应后退出（exit 0，stderr 空）；属 C1 遗留（与 ce6fd54 逻辑一致，C2 仅改 read1→os.read），影响有界、不涉数据一致性与权限边界。要求开发线在合并前给出“修复并重审”或“明确延期并登记”的处置，处置前不得声称握手时限已验证成立。

未验证并保留：远端三平台CI、push/PR/合并、签名、干净设备、生产，以及领域业务 E.2/E.5/G.4/FR-704；原生可见/焦点仅核验既有独立Docker/Xvfb/Openbox证据的内容与哈希，未在宿主复现。受审实现/测试/配置/依赖/验收未改动，AGENTS.md 保护SHA未变未stage。

## 2026-10-20 C2 Round-2 MiniMax 复审报告修订 R1（握手独立时间预算）

收到开发线自有只读探针产物 build/I04-evidence/handshake-independent-c2/（不含另一指定模型本轮报告或结论）。MiniMax 复审未采信其结论：先独立重算其 3 个源码 SHA-256 与 6 个工件哈希（全部匹配，与 git show 0462e082:<path> 逐字节相同），再用本人自写 harness（build/I04-review-MiniMax-M31Flash-C2/probe_late_hello.py→probe_late_hello.json，本人隔离 export 冻结字节、真实 stdio 与真实 SQLite、无 clock/queue/limits mock）独立复现：空闲对照臂 5.1117s 自然退出 exit 0（证明 5000ms 预算本应生效），迟延 hello 臂在 40561 条合法唯一 pre-handshake health 持续占用 inbox 时，hello 于 5.3121s 发出、5.3928s 仍被接受（ok=true、签发 engineSessionId、limits.handshakeMs=5000 照常回传），最晚可能截止 5.0704s，即协商准入越出声明预算至少 0.3224s。

据此修订报告：R2-P1 事实精度由“进程存活超期”收紧为“协商准入越出声明预算”，两条独立证据线互证（本人超期 0.32s / 开发线 0.73s，自然到期 5.11s / 5.13s）。严重程度维持 P2 非阻断（该阶段仍有 65536 请求身份硬上界、不涉数据一致性/授权/凭据/跨信任边界、C1 遗留非 C2 回归），但对原验收 #4 的影响明确化：握手独立时间预算子项按声明值不成立、只以请求数上限弱形式成立，其余子项不受影响。处置要求：修复 coordinator.py 握手时限检查点（移出 except queue.Empty 分支、绝对截止不因被拒请求续期、补迟到 hello 必须被拒且空闲期限仍生效的回归用例），生成新候选并重走双方全范围复审，或明确延期并登记理由；闭环前不得声称握手独立时间预算已验证成立，不得沿用本轮通过结论。证据保留说明：两份 .log 与对应 .json 字节完全相同，属同一内容副本，按 JSON 报告计，不作为独立原始日志。受审实现/测试/配置/依赖/验收未改动，AGENTS.md 保护 SHA 未变未 stage。

## 2026-10-21 C2 双方实际终态与完整读回

ZCode GLM-5.3/最高完整报告153行、MiniMax M3.1-Flash/xhigh最终修订报告312行均已实际完成并读回；双方结论均为通过，原P等级与附带边界原样保留。Z新增R2-N1(P3)及R2-N2(P2)，MM新增R2-P1(P2，握手同根)。原C1全部19 ID与延期项逐项保留。两原任务均含同任务必要方法修正/独立事实补证，终态已核验，未换模型、未重建Goal、无真实额度故障/重置。

本线不以附条件通过抵扣原验收#4：C2独立握手期限仍不成立，故不推送C2。修复和测试在独立C3分支完成、受审primary一直冻结；C3需全范围冻结及双方各新建完整审查，不沿用C2批准。详见round-2-processing.json；无push/PR/远端CI/合并。
