# I04 常驻协调器与 ExecutionJob

同一 Goal；会话 01a15899-4318-7522-8035-353e88d34de4。2026-10-20 已实际接收完整 Goal 第九节与无桌面打扰约束。

当前阶段：实现及本地/隔离/包内验收通过，准备冻结；外部双审、真实三平台 CI、正常合并与远端核验未完成。验证详情见 local-verification.json 和两份 native-*-evidence.json；下文初始记录按其时间保留。

- worktree: /Users/kyle/Documents/工作/知爻/本体/.worktrees/I04-resident-jobs
- branch: feature/I04-resident-jobs
- base: e45e6038b5e0f8f4adc69ed55aafccd75b3d3500
- origin: https://github.com/NOmoreJoke/OntoLearn-Studio.git；目标 develop
- 初始仅 AGENTS.md dirty，SHA256 db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786，禁止 stage。

## 范围与门禁

采用总控 I04-launch-prompt.md 的完整原验收及实际合并 I03；只做 S2 基础设施，不接 I05/I06 业务。主会话独占共享 contracts、入口、registry、build-engine；I03 R2-F1 必须在 Python 通知消费者接入前修复。I05 entry/build 交接已接收，后续整合保留其 probe/metadata/collect-all/inventory/license 行为，不提前复制未合并依赖。

原验收、静态/运行/包内/桌面证据、双指定模型同版明确 Pass、意见处置、真实 CI、正常 PR 合并和远端核验全部保留。当前无开发/运行/审查/合并通过证据。

## 文件责任与集成顺序

模块子任务各自独立 worktree/feature 分支，从同一 base 开始；不得改他人所有文件，不 stage 保护指南，不共享可变依赖/DB/输出。

| 负责人 | 唯一文件范围 | 接口/依赖与集成 |
| --- | --- | --- |
| 主会话 | Python coordinator.py/worker.py/protocol.py/__main__.py/entrypoint.py、contracts 及资源、scripts/build-engine.mjs、I04 总验收文档与集成测试 | 消费 JobStore 服务；协调唯一规范与资源；统一 cherry-pick 后联验 |
| storage agent | storage.py、job_store.py、新 test_job_store.py | 同一 SQLite；JobStore(Store) 负责持久 DTO/claim/plan/blob/results/cursors、原子提交与 fence 后 reconcile；不得改共享规范 |
| supervisor agent | main/engine.ts、main/jsonl.ts、新 supervisor/jsonl unit tests | EngineSupervisor 持久进程、严格帧/hello/pending/路由/超时；调用 request(method,params) 仅限主进程；健康及停止接口 |
| bridge agent | main/index.ts、新 main/task-service.ts、preload/index.ts、renderer、contracts/src/index.ts、新 bridge unit tests/e2e I04 专用文件 | 窄业务 bridge；消费 EngineSupervisor.health/request/stop；主进程受信项目上下文，重建只查询/订阅，不重发任务；index.ts 契约文件临时单一责任属该 agent，其他 contracts 主会话 |

顺序：独立纯模块/真实存储验证并行→主会话审查接口并 cherry-pick→真实进程/worker/SQLite/bridge/隔离窗口/包内联验→独立只读 agent 检查→冻结→指定双审。内部通过不代替外部审查。

## 待执行

完整实现、原矩阵验收、隔离环境准备、依赖安装、双审/推送/PR/CI/合并。协调器旧写者 fencing、完整终态证据、F6 真轮次结果链路和原生恢复均不得用替身抵扣。

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
