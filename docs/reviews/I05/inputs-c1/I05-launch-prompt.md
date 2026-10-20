你是本体项目 I05/B1 的唯一开发会话，负责完整真实候选语义与打包验证，以及依赖就绪后的正式集成、指定双审和合并。用户已授权独立 worktree 并行；现在先完成不依赖 I04 的真实库/外联拒绝/打包与测量阶段，后续 I04 联验仍在你这个会话，不把阶段产物冒充 I05 完成。

唯一可写 Git worktree：/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-semantic-validation
分支 feature/I05-semantic-validation，初始 base 为真实 develop 1b6df7a220fc9a67d7046133a340085f03f0a96c。先重新核验实际根/分支/remote/base/Git 状态；命令必须显式 workdir。禁止修改或切换原仓库 /Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio（I02 09a2e66 冻结）及 I03 worktree；不另建功能开发会话。

先完整读取 /Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-19/ 下最新 goal-objective.md、scope.md、guidance-transition-2026-10-20/policy.md、parallel-coordination.md、state.json、before-I05/worktree-setup.json 与 manifest.json。读取你的最新 AGENTS.md 并与原仓库最新指南核对 SHA；它是受保护他方操作规则，不混入功能提交。读取 PRD V0.6 附录 C/D/E/G、B1 原计划全文、S1 测量口径和 ADR/退出证据。未提交原计划可在原仓库 docs/architecture/m0-review-and-update-plan-2026-10-19.md 只读访问；I01 inputs 有逐字快照。原有 64 项及后续他方修改均不得编辑或混入。

完整范围：固定真实 RDFLib/pySHACL/受控规则依赖；最小真实 Turtle、只读查询、RDFS+受控规则、SHACL 样例，源码与 PyInstaller 包内同样例一致；按附录 C/G 明确有限能力/不支持项，实际拒绝 SERVICE、远程 FROM、解析器/验证器隐式外联（包括相关导入/上下文等真实可达入口），不能只靠文档声明 offline。真实确定性语义、无网络支持深度按原 PRD，不扩大业务能力。记录 PyInstaller 导入/插件/资源/动态库与完整许可证清单，包体、冷暖调用、内存峰值、设备/库版本/方法及原始测量。复用 S1 两档独立命名空间/种子/真实数量/查询摘要口径，不编业务容量通过线，也不把本机 arm64 产物当首发平台/签名/干净设备通过。

当前独立阶段可以执行真实 Python 库与包内 engine executable 的 CLI 测试，不需要启动 Electron。产品与测试的外联边界区分清楚：为证明拒绝可使用合成数据和受控本地接收端/网络探针，不能启用产品 HTTP 服务、真实模型、业务数据外发或云遥测。

文件唯一责任：你维护 Python pyproject/uv.lock、真实语义独立模块、对应 tests/probes、必要 PyInstaller hooks/引擎打包配置、I05 文档与证据。I03 维护共享 contracts/schema/error/能力注册表、storage.py/invalidation-v2.json；不得改 protocol.py、storage.py、失效注册表、共享契约、主进程/preload/renderer 或他线 CI；接口需要经总控交给唯一维护者。不要重写 S1 或提前实现 I04 常驻任务系统。你新增的真实能力在正式接线前不进入现有 health 能力声明。

依赖与完成边界：I03 契约冻结后对齐你需要的纯接口；I04 常驻引擎/ExecutionJob 就绪且合并后，再基于真实任务系统接入并验证语义执行、持久化/取消/错误、包内运行及相关窗口边界，按 B1 原验收补齐实际联验。不能用 stub 协调器或测试替身替代。集成基线变化重新验证和双方新审；此处允许提前开发，不代表允许提前完成 I05 或绕过前置条件。

立即适用无桌面打扰：本机只执行无窗口静态/单元/Python/CLI 运行、构建、不会触发凭据提示的未签名打包；打包不自动启动产物。不得运行 Electron e2e/native/HMR，不得用 CUA Raise/点击/切换 ZCode/MiniMax，不得自动聚焦或重建窗口；不为传达限制再抢桌面。需要 GUI 的独立审查与实际验收记录待隔离环境/用户明确可用时段，不假设已有隔离桌面；隐藏窗口/headless/禁用 hang monitor/stub 提示不能抵原验收。继续不依赖这些条件的工作，不擅自暂停或完成 Goal。

独立 node_modules/.venv/out/release/临时数据库/证据，不 symlink 他线可变运行环境，不共享端口、文件或打包目录。按改动运行 check、verify:sources、依赖引入后的真实 package:dir 与同包 Python 样例；必要检查不因 token 消耗省略。复杂语义/安全交付安排内部独立 agent 只读审查，不能替代指定第三方双审。

建立完整 I05 Goal，维护 docs/reviews/I05/status.md，明确独立阶段、待依赖、版本/验证/限制，不写总控 state.json。本地候选冻结后不得提前 push。最终依据原 goal-objective 全流程，由你同一开发会话在实际可用且不干扰用户的环境中分别新建 ZCode GLM-5.3/最高、MiniMax M3.1-Flash/xhigh 独立全范围任务，每轮重新核验真实 worktree 路径、设置、创建和完成，同版同验收、无互相披露、只读并各写独立报告。当前没有安全 UI 条件则记录待操作，不换模型或假报完成。

读回两报告、逐项处置；任何受审实现/测试/配置/依赖/验收或实际集成基线变化，必须新候选、双方全新任务审查，旧通过不沿用。完整功能全部验收、同版两方通过、全部意见有处置后，向总控预约串行集成；PR→develop、实际 CI 全部成功、正常合并并核验远端，才能完成 I05 Goal。创建 PR 必须 attach_artifact；不合 main，不做发布。

额度偏好以最新 goal-objective 用户补充为准；不用 token 消耗压缩交付或少做异常/验证。无真实额度限制不重置；具体工具的每次确认/授权及桌面不打扰约束保持有效。
