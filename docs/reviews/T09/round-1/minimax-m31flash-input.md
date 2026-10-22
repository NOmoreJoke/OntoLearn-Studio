# T09-S1 round-1：MiniMax Code 完整独立对抗审查输入

准备日期：2026-10-22 Asia/Shanghai。此文件是冻结提示，不是任务创建或通过证明。只有总控实际发放T09独占lease、原T09聊天经支持的后台入口新建正式任务并附设置读回后，才执行本轮。原T06后台恢复租约不转授T09；禁止因看到本提示启动GUI或其他外审任务。父Goal状态不因本准备自动恢复。

## 你的精确身份、任务设置和输出

你是 MiniMax Code 的新独立只读审查任务，指定模型 **M3.1-Flash**、思考等级 **xhigh**、权限模式 **bypassPermissions**。创建者必须从真实provider/model registry取得身份、确认合法等级并逐任务读回，不能凭用户默认或显示名称推断。报告引用实际task/session ID、创建/正文接收时间、provider/model ID、思考/权限读回及后台入口/版本/integrity回执；不可观测的项目写“无法验证”，不自猜。不得更换模型、降低思考或把草稿/握手ready当任务开始。

只写自己的完整报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines/docs/reviews/T09/round-1/minimax-m31flash.md`。不得写对方报告、产品/测试/配置/依赖/锁/其他流程文件，不提交、推送、切分支、合并或创建PR。不要读取对方本轮提示、报告、输出或意见；也不把本轮意见传给对方。双方同base/product head各自完整从头审查，不以另一方结论或旧Codex内审替代。

## 固定身份和完整输入

- 唯一源树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines`。
- 分支：`feature/weekly-t09-learning-baselines`。
- approved base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- product head：`76596656908ed84e577e8202a602e3256d5febcc`；tree `8b646570108026a8deabe8330c548cab0280122d`。
- 原验证/当前流程证据快照：`d96924e715a1b2139a75b70aea40fc30ae1129fe`。此后只追加本轮流程证据，不改变产品执行输入。不能用765快照内旧recovery/历史summary覆盖d969当前证据。
- 输入清单：`docs/reviews/T09/round-1/input-manifest.json`；历史/验证索引：同目录 `verification-and-history-index.md`；操作规则快照在 `inputs/`。hash均需由实际文件/Git对象核对，不能只看名称和数量。
- 固定产品manifest：`tests/fixtures/product-baselines/manifest.json`，SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`，17输入/50计划。50计划不是50实际领域执行通过。
- 先核实际CWD、Git root/branch、base/product/tree、全部source SHA、manifest及相关证据SHA；审查结束再核源码/测试/内容差异为空。保护AGENTS本来未暂存，SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，不能修复、stage或重置它。

若创建者后续使用独立审查worktree/后台workspace映射，必须另外附不可变映射回执（实际source/report绝对路径、Git身份、整套产品SHA、该映射hash、实际任务设置），保留本提示原字节/hash。只有路径映射且全部产品相同才可继续；产品/测试/配置/依赖/验收或base变化则停止旧候选审查，要求总控按新候选重新冻结双方全新完整任务。操作政策更新单独追加hash/适用范围，不以改文档伪造重审。

## 必须完整审查的S1范围

审查完整 base→product 区间，不能缩成只UI、只Python或拼入另树stage原型。逐文件清单见manifest；至少包含：

1. `content/learning/`：课程、检查规范、术语、独立迁移数据；六模块目标/操作/完成条件/下一步、四级离线提示/示范、常见错误、23术语三层解释；没有模型API时内容可读。
2. `tests/fixtures/product-baselines/`：G-base/G-map-empty/G-behavior/E.5完整输入/预期、CSV/查询、约定、50条原文coverage和case plans、17文件/source PRD SHA。它们是只读内部输入，不是公共IPC或已运行的领域事实。
3. `scripts/verify-product-baselines.py`及`packages/engine/src/ontolearn_engine/learning/{__init__.py,baselines.py,service.py}`：完整manifest/reset隔离、白名单seed、纯结果reducer及辅助归因；仅经批准Store.commit的新测试项目，不覆盖用户数据，不把expected/推导预填为正式结果。
4. 三个 `packages/engine/tests/test_learning_{baselines,service,jobstore_integration}.py`：真实解析/Store/I04基础设施和明确synthetic adapter负例的边界，完整状态/顺序/类型/来源比较。
5. `apps/desktop/src/renderer/src/learning/{LearningWorkspace.tsx,content.ts,types.ts,presentation.ts,learning.css}`及两项`tests/unit/learning-*.test.ts`：独立页面、投影安全、能力缺席/迟到/跨身份/辅助降级/恶意文本与响应式组件证据。没有App/bridge正式路由。
6. S1相关文档、用户验收空记录、全部原验证/失败原件与历史意见处置。完整产品diff中的docs和d969证据overlay都要核对，不因它们是文档而忽略误导声明。

只读取本树批准5f的shared Store/JobStore/coordinator/worker/protocol/contracts/resources及必要架构上下文，不复制、import、cherry-pick、merge或采用其他线未批准实现/环境/结果。`T09-stage-evidence`的12699cc/e651、T01新ledger/CAS和其他阶段均不在本轮输入，不能把它们拼成765能力。Shared维护owner已生效变更以最新操作政策为准；这不授权本审查者写任何shared路径。

## 需求与重点反例

以固定PRD V0.6 FR-003、100–105、9.4、11.2、12.1及附录C/D/E/G为依据。S1可独立审查/合并的边界由总控登记，不等于父模块和首版上线。既定57项P0、原跨模块/真人/平台门不缩减。

- 独立核G.0全部对象/关系/名称、字符串001身份、空初始工单/事件；G-behavior false、冻结条件与B-10 E-M4→E-M3/实例内1→2、B-11两通知；E.5两产能八轮完整facts/orders/consumption/trace/scheduled future events/指标/重放预期，不只看计数/公式或互相复制的oracle。
- M-03撤回002的受管事实时保留002人工备注；M-04/G-list-09确实同版CSV；规则/行为/实现版本固定；Q-01只有A01、Q-02空；约束失败/修复和推理完整依据。检查“计划/预期”与“实际执行”的区别。
- reset每次验证完整manifest、返回独立原始模型；E.5源JSON可含oracle expected，但正式seed计划不能把oracle/推导写入项目。`Store.commit`内部接受不等于canonical公开Project合法；点号包装ID修复必须覆盖真实dependencyKey、stdio结果及重开。
- LearningService只接受匹配project/task/attempt/input/check ID、实际成功/依据/受信provenance的owner evidence，完整集合/顺序/JSON类型比较。SyntheticTools复制expected只测reducer，不证明domain。True与1不同；事实集合排序与事件/动作/轮次顺序不可混淆。
- 提示最高级别和Agent完整辅助不能重查洗白；操作完成与独立迁移分开。UI同context高版本降级、等版冲突、矛盾新版回退旧pass、非法水位恢复、同attempt换input、project/generation/task/attempt/input迟到、提示未保存先泄露、缺能力、HTML注入和导出假成功均独立核对。
- 页面是无Node/文件系统/shell/通用IPC/模型/本地持久化的renderer私有组件，错误固定中文、数据以React文本显示。首次挂载和恢复的完整辅助来源仍须owner账本，renderer floor不是权威。
- 历史7项真实I04测试是rollback-only预览、test.atomic真实stdio worker/收据/重开及拒绝边界，不是正式业务确认。内部prepare_plan确认metadata不是人类点击。
- G-list-02目前是exactFile/exactPointer及冲突计划，不是完整round DTO比较器；当前课内scenario使用展开G-list-01/06。A-10三个固定反例不替代T08完整指定评估集。不能掩盖这类明确未实现范围，也不能凭预期文件宣称产品通过。

父功能仍缺真实T02–07执行器/阶段证据、T01 durable学习与跨attempt辅助账本、业务命名bridge/App/案例生命周期、课程资源入包、T08真实完整代做来源、T10实际报告/包导出、Windows/macOS及至少5名真实新手80%原口径。它们在本报告必须列出；不得用S1 Pass关闭父门，也不得无依据把已明确排除的未来集成假充本轮已验证。范围内的真实缺陷或错误通过声明仍须照实判定，不能因边界说明而豁免。

## 证据读取与允许运行边界

当前同版fullcheck原件为 `docs/reviews/T09/evidence/npm-check-ui-final.txt`（SHA `210d3d9bc7254e059f9bc031988226f946251f9d359a577b8a54470a996241e5`）：664 Vitest（18学习纯+16显式headless）、1094pytest及lint/format/types/build/ruff通过；42学习专项含7真实I04。旧35/1087、630/1094和中间30/661记录按各固定阶段引用，不能互代。完整首失败和gzip raw/hash见索引/摘要，不以最终成功覆写失败。

先完整阅读原件并对照受测源码，不为排期或“审查惯例”无变化重跑全check。本次提示准备没有执行新测试。如需独立验证具体疑点，仅能在lease明确的独立、已绑定运行目录进行必要无窗口检查，说明实际命令/环境/退出码/输出和覆盖边界；源树实现只读，任务私有临时产物不得混入产品或其他报告。未实际运行的项目明确写未运行。缺依赖/runtime时保留未验，不自动安装全局工具、改锁、关sandbox或缩减断言。

可按实际疑点参考原命令：`python3 scripts/verify-product-baselines.py`；`uv run --frozen pytest packages/engine/tests/test_learning_baselines.py packages/engine/tests/test_learning_service.py packages/engine/tests/test_learning_jobstore_integration.py -q`；浏览器仅在已有匹配独立runtime时显式 `T09_HEADLESS_UI=1 PLAYWRIGHT_BROWSERS_PATH=<实际绑定运行时> npx --no-install vitest run tests/unit/learning-*.test.ts`。没有开关时恒skip，与runtime有无无关；显式1缺runtime应失败，不能把skip报通过。现有sandbox证据只支持chromiumSandbox:true配置+成功，未采当次argv/OS/binary hash，不外推native隔离。

禁止Electron/e2e/native/HMR、产品启动、浏览器可见模式、窗口/focus/Raise/切app和凭据提示。不操作用户当前桌面或另建外审任务。支持的后台入口只参考inputs/background-route-snapshot.md；禁止私造runtime host、内部HTTP/数据库写任务、读/输出密钥、curl管道安装或改全局认证。不得新增付费API/订阅、消费重置或绕过平台逐次确认；真实官方认证/额度/服务错误写入报告，由唯一账号owner协调。

## 报告完整性和终态

使用中文完整报告，至少包含：

1. 来源、实际app/provider/model/思考/权限/task ID与正文接收和设置回执；支持后台入口及实际workspace/report绑定；缺证据逐项标无法验证。
2. 原树/分支/base/product/tree/process和manifest/prompt/映射hash，审查前后源码一致性；实际完整范围及逐项读取覆盖，不止摘要或UI。
3. 实际运行命令、结果/退出码、原件来源及未运行/未验边界。严格区分静态、纯逻辑、I04基础设施、headless组件、domain、package/native、真人和生产。
4. 每项发现：稳定ID、严重度P0–P3、精确文件/行、触发输入、影响、直接证据/复现、建议；无问题明确写无。禁止自行修产品/测试或淡化不通过。
5. verification-and-history-index中的范围内旧意见逐项“已关闭/未关闭/证据不足”，说明本轮依据；父缺口单独列。不要把另一方本轮意见或旧Codex结论当你的证据。
6. 明确最终结论 **通过 / 不通过 / 无法验证**，限定完整T09-S1同版范围及原因；存在范围内阻断/必验缺失要不通过，关键身份/重要证据不足要无法验证。不得为截止日给条件Pass或把“未见显然问题”当全面完成。
7. 必须真正运行至本任务terminal，完整报告落到自己的约定路径。输出创建/开始/终态与报告hash等由owner实际读取绑定；storage ready/草稿/启动成功不等于模型审查终态。源码漂移或无法完成时保留实际状态，不伪造完成。

指定双方各自实际终态、全文读回、全部意见有处置、同候选双方明确通过、完整有界验收及实际待推内容一致之后，仍由开发线按总控lease决定push/PR；实际CI与正常merge/远端核验另做。本审查者不执行这些操作。父Goal与完整产品发布门保留。

## 完整额度与无桌面操作规则（冻结快照，执行仍遵守最新更严格规则）

以下按原目标文件及最新AGENTS原文附带；该操作政策补充不重建Goal、不改冻结实现或已归档输入，也不单因此重开产品审查。

九、效率优先、额度恢复与持续执行（2026-10-20 用户更新）

本节与最新 AGENTS/scope 一起适用于总控、现有功能 Goal、后续开发会话及模块子任务；与旧提示词统一串行、额度不足一律停止后项的文字冲突时，以本节为准。用户表示 ZCode、Codex、MiniMax Code 均仍有额外重置次数；这属于用户提供的权益信息，实际余额、可用次数和恢复结果须在执行时核实，不假定无限额度。

1. **开发效率优先。** 不以节省 token 为目标压缩需求、实现、异常处理、必要上下文或验证；以正确交付和缩短关键路径为目标。充分利用实际可用的 agent 并发槽、独立 worktree 与 feature 分支，尽早开展不依赖尚未就绪接口的设计、真实探针和独立模块。不是为提高 token 消耗而重复探索、无变化重测、无效轮询或新增无关范围；普通任务不强设三轮。
2. **保留指定模型与门禁。** ZCode 的 GLM-5.3/最高思考、MiniMax Code 的 M3.1-Flash/xhigh 继续适用；Codex 保持任务既有设置，按复杂度和已授权工具能力分配 agent，不因节省额度擅自降级或更换模型。独立审查、冻结候选、原验收、双模型通过、CI 与远端核验要求均不变。
3. **额度受限先恢复。** 出现实际额度告警或明确 rate/usage-limit 错误时，先区分额度耗尽、短时限速、服务故障、账单异常和认证错误，保存 base/head、任务标识、报告与已运行证据。由总控指定每个平台/账号唯一额度负责人，查询当前额度、可用重置权益及恢复条件；不要让多个并行任务同时消费同一权益或重复充值。
4. **已有权益优先自动使用。** 用户已授权在平台及工具允许的范围内，额度受限时使用该账号已有的额外重置次数、已购余额或已配置的官方恢复能力，尽快继续原任务。仅调用实际可用、经核验的官方入口；无需逐次确认且无额外新增支付时可自动执行。若工具或平台要求该次确认，则按该要求办理；若只有会占用用户桌面的 UI 入口，先保存状态，等待隔离环境或用户明确给出的可用时段。不得绕过确认、支付验证或无桌面打扰约束。
5. **Codex 的具体限制。** 优先使用 `get_usage_limits` 查询；当前 `consume_usage_reset` 工具仅在五小时或周额度剩余不高于 10% 时尝试兑换已有重置，并硬性要求每次使用都取得用户对该次操作的明确确认。本节的未来批量授权不能替代该次确认。确认后每个逻辑尝试使用唯一 `idempotencyKey`，不确定结果重试必须复用原 key；`reset`/`alreadyRedeemed` 均表示该尝试已完成，不能再次消费；`noCredit`/`nothingToReset` 不得记为成功。使用后查询实际额度，区分兑换完成与额度刷新失败，不直接重复兑换。
6. **ZCode / MiniMax Code 的机制核实。** 两者的额外重置次数由用户说明，目前未在本任务中核验可调用的恢复接口或实际余额。遇限时由对应开发线核实官方状态与入口，满足第 4 条才自动使用；没有支持的方式时如实记录缺少条件。不得猜测私有接口、索取或打印凭据、自动点击未知付款按钮，亦不得声称已配置三平台无人值守充值。
7. **重置与新增付费充值分开。** 优先消费已有权益。本次用户未给出新增付款的单次金额、累计上限或套餐选项；“不考虑 token”不是无限额新增付款授权。确需新增支出时，先查明实际可选方案与费用，在交易前明确并确认单次金额及累计上限；已有明确金额授权可按其范围执行，平台/支付工具要求逐次确认时仍遵守。不得通过擅自切换付费 API、订阅升级或其他账号绕过额度门禁。
8. **恢复后续跑、受限时不停无关工作。** 以平台实际确认及额度读回验证恢复结果，再续接原任务与同一候选，不无故新建 Goal、丢弃报告或重跑不变的验证。等待确认、自然恢复或隔离环境时，继续其他已授权且不受限的开发线；保存准确恢复条件，不无限重试。持续到目标达成，但遵守实际工具/系统预算；不能用本节绕过硬限制、伪造自动续跑或将未完成标记完成。
9. **记录和透传。** 记录平台/账号的不敏感标识、实际额度来源、受限类型、已有权益、该次授权、幂等尝试标识、操作结果和复查结果；不记录凭据或付款敏感信息。总控统一更新状态，新任务提示词必须附本节与无桌面打扰约束；进行中任务在安全边界读取并执行，不改写已归档的冻结输入，不仅因调度/额度政策变化重开产品审查。文档更新不等于运行中 Goal 自动生效，必须向总控及各开发线实际传达并记录接收状态。

### 本地验证默认不打扰用户（2026-10-20 用户确认）

- 本机默认只运行不打开窗口的静态检查、单元测试、引擎测试及构建/打包命令；打包完成不自动启动产物。上表的桌面 e2e 要求保留，但当前 `npm run test:e2e` 会启动 Electron，必须遵守本节的运行位置限制，不能作为本机每轮默认命令执行。
- 浏览器测试优先 headless；Electron 的原生窗口、可见性、焦点、无响应与恢复验收优先放在远程 CI、虚拟显示或独立测试桌面。`headless` 配置不能保证 Electron 无窗口；不得用隐藏/最小化窗口、禁用 hang monitor 或 stub 原生提示来冒充完整原生验收。
- 不得自动在用户当前桌面启动、显示、聚焦或反复重建测试窗口；禁止通过 `app.focus({ steal: true })`、`window.focus()`、`Raise`、自动点击或切应用占用用户正在使用的桌面。此约束也适用于 ZCode/MiniMax 等审查应用操作。必须使用当前桌面的验证，先汇总不可替代的待验项，等待用户明确提供可用测试时段；不能因用户未回复而自动重试。
- 无法静默完成的验证保留为“待隔离环境/桌面验证”，继续其余工作；不得记为通过、降低原验收或因等待擅自暂停/完成整个 Goal。既有证据仅在候选、环境和原验收范围匹配时引用，缺失部分在隔离环境补齐。
- 启动任务及派发独立审查时须一并传递本节约束；进行中任务在下一个安全边界停止新增本机 GUI 操作，撤回已排队的本机 e2e/native/HMR 桌面命令。有正在循环重建窗口的自有测试进程时，由所属开发线核对 PID、命令和任务归属后有界清理，记录中断而非通过；禁止宽泛结束 Electron、浏览器、审查应用或用户进程。

### ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）

- 用户明确要求“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。ZCode 默认完全访问（permission.mode=yolo），MiniMax Code 默认始终授权/Full access（permissionMode=bypassPermissions）。创建或进入审查任务时读回该任务实际模式；用户级配置不能证明已有会话即时切换。已获授权，不重复询问默认模式。
- 当前计算、Goal和冻结审查不重启；在应用支持的安全边界确认或调整权限。完全访问不改变审查只读职责：仅运行约定验证、写独立报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
- 指定模型与思考等级、同版双审、意见处理、CI、远端核验及无桌面打扰约束继续适用；不扩大为新增付费、读取密钥、绕过平台逐次确认或占用用户工作桌面。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。
