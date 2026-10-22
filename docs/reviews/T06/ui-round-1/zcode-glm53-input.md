指定模型/设置：ZCode GLM-5.3 / 最高思考（max）。必须由owner提交前后读回当前新任务实际 permission.mode=yolo（完全访问）；全局设置不能证明本任务。只写独立报告 zcode-glm53.md。

# T06 UI 全新独立完整只读对抗审查

本轮只审未装配 App 的独立行为工作台组件。它是完整 FR-600–604 的一个已实现子阶段，不能用 UI 夹具或组件通过关闭真实 Store/推理/Agent/G.3、正式权限隔离、原生两 OS、包内验证、真人、CI、合并或发布。

## 派发前必须具备的实际操作补充

本文件是完整冻结输入，尚须 owner 在提交前另附“实际派发 addendum”。addendum 必须给出本审查者唯一独立 review worktree 的绝对路径、实际 detached/branch 与完整 HEAD、独立 node_modules/.venv/构建/日志/输出目录、源码/原件逐字节匹配回执，以及本模型唯一报告绝对路径。下文 [REVIEW_WORKTREE] 只是待映射符号；没有该 addendum 就报告无法验证并停止，不猜路径、不直接在开发树执行。owner 可只读从固定产品/流程 Git 创建独立审查树，不能修改冻结产品、原提示、旧报告或旧 manifest。两个模型各用独立环境，不共享可变依赖/输出，不互传本轮意见。创建/设置/读回按总控短时内部租约串行；后台模型推理不占整个应用。当前 UI 新任务尚未创建，不把静态准备当受理或通过。

## 固定身份与来源

- 原开发树：/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui；branch feature/T06-behavior-ui。只供固定来源核验，不在其中安装/测试/写报告。
- base：5f910b52c69d86a1076b2032e5d3c63e715947f3。产品候选：da37709dcf09e04ded767ab2d08c26bbd8df24f3。流程 HEAD：3b3af941c73b7a5d416fda50ec6fb8102992551f。
- 产品完整 binary diff SHA-256：0b2ebc607543cfbc0a02a2856c1fddbf4b4a92c6204cf186f3655d0b90f8a2b4；完整命令为 git diff --binary BASE PRODUCT，必须读完全部10文件，不能只看571→da的三修复 delta。
- 当前 AGENTS SHA-256：de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4，保护 dirty，禁止还原/暂存。产品之后的流程只改 behavior/status.md 与 verification.json，必须读两版本并分清源码与流程；7源码/测试/脚本均与产品字节一致。
- 主 PRD：/Users/kyle/Documents/工作/知爻/本体/PRD-本体学习与落地Agent工作台.md；SHA-256 7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb。原文 FR-600–604、附录 C/D/E.1/E.2 与 G.0/G-behavior/G.3；涉及 Agent/安全还读 F、G.5 和第10–12节相应原门。不要用本提示或历史审查摘要替代原条款。
- 本轮证据映射：本输入同目录 dispatch-preflight.json。只读自身派发输入，不读取同轮另一模型提示、会话、报告或意见；S1 正在外审，其当前提示/报告/输出/推理全部禁止读取。

## 全部受审10文件

- apps/desktop/src/renderer/src/behavior/BehaviorWorkspace.tsx
- apps/desktop/src/renderer/src/behavior/README.md
- apps/desktop/src/renderer/src/behavior/behavior.css
- apps/desktop/src/renderer/src/behavior/controller.ts
- apps/desktop/src/renderer/src/behavior/model.ts
- apps/desktop/src/renderer/src/behavior/presentation.ts
- apps/desktop/src/renderer/src/behavior/status.md
- apps/desktop/src/renderer/src/behavior/verification.json
- apps/desktop/src/renderer/src/behavior/verify-headless.mjs
- tests/unit/t06-behavior-ui.test.ts

必须全文读取上述文件、完整 base→product diff、product→流程HEAD的两份流程差异；对下列7项重算当前审查树/Git产品/流程三方 SHA，不以数量或文件摘要代替。

- apps/desktop/src/renderer/src/behavior/BehaviorWorkspace.tsx：0e7012e1a5d2791fda1aafd5eea0a8248d78d7329e8513ea7ad2062ae39f671b
- apps/desktop/src/renderer/src/behavior/controller.ts：36d59ea11907fe44e73bb84849b20839944a02b8d538f602dc88ef82657217d3
- apps/desktop/src/renderer/src/behavior/model.ts：b246491a46387f4b33079266c10d2a41f36648875e240330191ff3ba8a09f90f
- apps/desktop/src/renderer/src/behavior/presentation.ts：5966010c9a052cc2bbd7524e759fe06d9806c698259e84039aae54fcb28fa1d2
- apps/desktop/src/renderer/src/behavior/behavior.css：869ebea1be9dcbfb839814c5c610bd7bc698420edc5f4c05e315ad37347c1465
- apps/desktop/src/renderer/src/behavior/verify-headless.mjs：a4573ccca0725aa1db18c4953ae213213493423927ca435401a7f9c152eba742
- tests/unit/t06-behavior-ui.test.ts：cad7082f2c0da281fd0256b09834dda2857e99da5bba47866c1619bc4480440c

README、status、verification 本身同样在全范围，只是7项源码清单不重复列流程字段。审查开始/结束记录真实 git status 与 HEAD，产品路径不得发生变更。共享 App/env/style/main/preload/contracts/Store/依赖/锁/CI不在本组件的写面；不得自行装配或采用任何未批准服务实现。

## 历史原件与完整证据映射

以下在 S1 开发树中存放的是本 UI 的指定历史文件，不是当前 S1 外审意见。须按这些精确绝对路径只读，owner 应将原字节复制为本 reviewer 独立只读证据目录并在 addendum 写清映射，防止依赖变化中的其他树；不要广泛扫描 S1 round-1/。

- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-integration-handoff.md；5145B；SHA b0403445b1fd3c368231fa233fd97edbc6c9bb77184727de412a6fc905cb715d
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-local-review-1.md；6356B；SHA 628f2370edb030f636fa671188b8e344f953b693918a404db70ae85734ec0292
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/ui-local-review-2.md；7552B；SHA 0ed80af74646509741dc0e7a40fb142713b0605c30dc97735b1eba8c1680c9b3
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/evidence/ui-validation-da37709.json；5569B；SHA a7cfcdb01cc1c2dff14a0503744c74dc1d982c27e86b1d154b7fdc3cc2419820
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/evidence/ui-archive-index-20261021.json；7428B；SHA a21315870ddc3726b73547a1920ab74b45c43c4cff85c6923424bf580314d231
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/evidence/ui-archive-20261021.md；2741B；SHA 33c33705d0f3f078f83a79769f574a373906b81f8e5d378a529c53a0045a7232
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/evidence/ui-571b4d6-negative-probes.mjs；2965B；SHA dc8b54956bbfda1f0b2d0548ca7a8eecaa6fdbbf07c54306d0ef4c65b69562ab

原失败产品 571b4d64120c8420d527f9fda2a3cb81bbd47d3f 的 Git 对象及 verification.json 也须读取。旧三项 P2 不能由开发者声明关闭替代你自己的核验：一，显式 always 无额外条件，不将空/缺组静默解释为真；二，单 sample candidate/completed/failed/cancelled 与 action/notification/committed/error 的矩阵，矛盾刷新保留上一有效结果；三，自有 __proto__/constructor/prototype（含转义）载荷被静默丢值，须拒绝并保留原文及普通键，不误写为已证原型污染。历史报告完整读取，逐项说明关闭或重开，并继续全范围找新问题。原不通过报告不得覆盖或改写。

两包原件来自固定 Git 归档：

- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/evidence/ui-original-artifacts-20261021.tar.gz；2232198B；SHA a51bfec8089f9a7db1578ebbfcc3570e1591beda51b956f2d8bf165a0cfab433；内部manifest SHA 42950c37fededf9175de2433f35f420a7e30fa4b147e29edcda2f1cb344b629d；34成员。
- /Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior/docs/reviews/T06/evidence/ui-session-tool-records-20261021.tar.gz；6698B；SHA 06d2e8636bbef29c6bb131bb3605c4f15e679d784137a2bffec5e58d472f5a3b；内部manifest SHA b35e8ae09fd445463dca559b1baa2390dbc3eb26060c0657840656b7315e2156；8成员。

先核 archive/manifest 的字节与 SHA，再按 manifest 的 regular member 白名单只读恢复到本 reviewer 自己的 evidence 目录，拒绝绝对路径、..、链接；逐项核 bytes/SHA。不要执行归档中的 preview.js/index.html/旧脚本来替代当前产品运行，也不覆盖任何原件。需要核对全部33原文件及独立的六条工具原行，索引涵盖当前9、旧571的11、独立headless5、当时构建/脚本5、固定Git来源3；两包共42成员（含manifest/说明）。六条历史call/output是独立34单测exit0与旧两次装配失败exit1，按包内manifest核call_id、源行/offset/length/终态，不需要读任何全会话、凭据或人类/系统消息。原件保存意义是可恢复，不是新验收。旧浏览器binary SHA/完整argv未记录，不能拿现在的版本倒推。

## 完整对抗审查重点

- 元数据、行为ID唯一与编辑现有ID例外、单组 AND、显式 always/equals/exists/type、空/缺/未知字段/有限JSON边界；四类安全动作及重排、单值覆盖/多值追加拒绝、对象/类/属性/IRI已知性、同实例先创建后引用。界面类型是私有callback，exists/type不能默认为已与S1 has/always无损兼容。
- 有序事件、标量payload与显式add/remove/set事实变更、同ID重投保留源内容、重复ID/保留键/畸形JSON、草稿到服务callback传递保真；不能重做领域引擎、靠UI产生推导/竞争/消费真相或默认补Store权威。
- 逐条触发/未触发原因、动作真实顺序及状态、Diff增撤、通知、原request/runId/project/input/behavior/scope及断言/推导/语义版本；候选/提交/失败/取消、当前/过期/历史的组合与安全文本。单轮不得混入旧轮次已提交记录；schema严格拒unknown/evidence/矛盾状态，React不执行HTML-like通知。
- 异步绑定、epoch/卸载/能力连接改变、切项目/输入版本后迟到回包，草稿生命周期、同项目刷新与切行为key责任；refresh只读同runId不重发事件不覆盖草稿；cancel必须真实终态，ack不能当已取消，完成先赢与取消先赢的竞态。
- 缺省无服务禁用、固定错误枚举及本地说明，不直接渲染原始异常/堆栈/路径/密钥/业务原值；隔离scope标签不是权限/受信来源证明，onDraftChange不是持久保存或批准。
- 全部 UI 正常流、反例、Tab/可访问角色、1440/390布局与中文可读性。比较完整状态/文本/集合/顺序而非只验计数；60是4×5×3合成状态组合，不是60次真实引擎运行。

## 审查实际验证与证据分账

开发线历史结果是完整 npm run check exit0：664 TS（含34UI）/1052 Python；旧571仅651TS/21UI。修复后的内部独立 agent 实际运行34专项与真实 headless，全文核历史原件；它读取开发线全仓日志，没有独立再跑全仓。它们都不是你本次指定审查结果，也不是S1的1174Python或真实引擎联验。

本轮需在 owner 映射的独立 [REVIEW_WORKTREE] 验证：npx vitest run tests/unit/t06-behavior-ui.test.ts；npm run check；以及当前 verify-headless.mjs 的完整 headless 正反例。依次串行使用本树环境，保存命令、cwd、退出码、完整新日志/截图和首败，不能覆盖历史输出。headless 原脚本输出目录固定 test-results/t06-behavior-ui-r2，须在本 reviewer 自己的副本中仅重定位 component 到固定审查源码、output 到新唯一目录，保留临时脚本及其diff/hash；由当前脚本实际生成 fixture/构建输出，不运行归档旧preview。脚本使用只监听127.0.0.1的临时随机端口、headless浏览器且无HMR；核自有端口/PID并关闭自有资源，不共享可变cache/输出。需要浏览器依赖缺失时先准确记录，按owner既有授权准备官方依赖，不能跳过又称通过。实际查看新宽屏/手机截图并解释局限。可追加只读临时内存反例，不改冻结实现、测试、预期、依赖或配置。

本子阶段没有主进程/preload/bridge/CSP改动，不需为此强行启动Electron/e2e/native/HMR/Keychain、产品正式数据或真实模型API；若发现原验收必须另验的门，准确列未验，由owner按总控资源与正式依赖补齐，不用隐藏窗口、stub提示或禁hang monitor冒充native。当前人类已允许computer use，不以旧无GUI/静默/CLI认证作为前置；具体任务写面与新模型创建仍按总控短lease，不能抢其他任务。

## 结论、报告与真正终态

只可写本模型的 [REVIEW_WORKTREE]/docs/reviews/T06/ui-round-1/zcode-glm53.md 和本reviewer唯一临时输出。不写原开发树、另一报告或根控制文件；不切分支、提交、push、PR、合并，不修受审代码。

最终中文完整报告必须含任务来源、实际app/模型/最高思考/当前任务权限与真实task/session/turn身份（owner外部读回与模型自身可核事实分开）、绝对工作区/branch或detached、base/product/processHEAD与源码hash核验、完整读取10文件/diff/PRD/历史原件范围、实际每条命令与结果和首败/限制。每发现严重度、具体源码行、最小有效触发输入、影响、证据、修复建议；逐项核历史三P2是否关闭，全部新意见都列出。只对“未装配独立UI组件完整范围”给明确通过/不通过/无法验证，原FR父模块和所有未验门继续列明；任何阻断或缺证不伪作Pass。不能自己改写另一模型结论。写好全文后在会话最终消息给完整报告绝对路径与明确结论，并真正结束。本轮需真实业务终态+持久最终消息+全文报告，accepted/正确设置/检查绿/摘要均不等于通过；owner会全文读回、原字节归档并处置所有意见，受审内容变化后双方新建同版完整审查。

## 当前操作政策全文（历史报告中的旧限制按原时点理解）

## 第九节与当前桌面操作政策

以下按原目标文件及最新AGENTS原文附带；该操作政策补充不重建Goal、不改冻结实现或已归档输入，也不单因此重开产品审查。

九、效率优先、额度恢复与持续执行（2026-10-20 用户更新）

本节与最新 AGENTS/scope 一起适用于总控、现有功能 Goal、后续开发会话及模块子任务；与旧提示词统一串行、额度不足一律停止后项的文字冲突时，以本节为准。用户表示 ZCode、Codex、MiniMax Code 均仍有额外重置次数；这属于用户提供的权益信息，实际余额、可用次数和恢复结果须在执行时核实，不假定无限额度。

1. **开发效率优先。** 不以节省 token 为目标压缩需求、实现、异常处理、必要上下文或验证；以正确交付和缩短关键路径为目标。充分利用实际可用的 agent 并发槽、独立 worktree 与 feature 分支，尽早开展不依赖尚未就绪接口的设计、真实探针和独立模块。不是为提高 token 消耗而重复探索、无变化重测、无效轮询或新增无关范围；普通任务不强设三轮。
2. **保留指定模型与门禁。** ZCode 的 GLM-5.3/最高思考、MiniMax Code 的 M3.1-Flash/xhigh 继续适用；Codex 保持任务既有设置，按复杂度和已授权工具能力分配 agent，不因节省额度擅自降级或更换模型。独立审查、冻结候选、原验收、双模型通过、CI 与远端核验要求均不变。
3. **额度受限先恢复。** 出现实际额度告警或明确 rate/usage-limit 错误时，先区分额度耗尽、短时限速、服务故障、账单异常和认证错误，保存 base/head、任务标识、报告与已运行证据。由总控指定每个平台/账号唯一额度负责人，查询当前额度、可用重置权益及恢复条件；不要让多个并行任务同时消费同一权益或重复充值。
4. **已有权益优先自动使用。** 用户已授权在平台及工具允许的范围内，额度受限时使用该账号已有的额外重置次数、已购余额或已配置的官方恢复能力，尽快继续原任务。仅调用实际可用、经核验的官方入口；无需逐次确认且无额外新增支付时可自动执行。若工具或平台要求该次确认，按该要求办理；如需UI由唯一资源owner依2026-10-22当前政策直接computer use，不等待额外用户桌面时段。不得绕过确认或支付验证。
5. **Codex 的具体限制。** 优先使用 `get_usage_limits` 查询；当前 `consume_usage_reset` 工具仅在五小时或周额度剩余不高于 10% 时尝试兑换已有重置，并硬性要求每次使用都取得用户对该次操作的明确确认。本节的未来批量授权不能替代该次确认。确认后每个逻辑尝试使用唯一 `idempotencyKey`，不确定结果重试必须复用原 key；`reset`/`alreadyRedeemed` 均表示该尝试已完成，不能再次消费；`noCredit`/`nothingToReset` 不得记为成功。使用后查询实际额度，区分兑换完成与额度刷新失败，不直接重复兑换。
6. **ZCode / MiniMax Code 的机制核实。** 两者的额外重置次数由用户说明，目前未在本任务中核验可调用的恢复接口或实际余额。遇限时由对应开发线核实官方状态与入口，满足第 4 条才自动使用；没有支持的方式时如实记录缺少条件。不得猜测私有接口、索取或打印凭据、自动点击未知付款按钮，亦不得声称已配置三平台无人值守充值。
7. **重置与新增付费充值分开。** 优先消费已有权益。本次用户未给出新增付款的单次金额、累计上限或套餐选项；“不考虑 token”不是无限额新增付款授权。确需新增支出时，先查明实际可选方案与费用，在交易前明确并确认单次金额及累计上限；已有明确金额授权可按其范围执行，平台/支付工具要求逐次确认时仍遵守。不得通过擅自切换付费 API、订阅升级或其他账号绕过额度门禁。
8. **恢复后续跑、受限时不停无关工作。** 以平台实际确认及额度读回验证恢复结果，再续接原任务与同一候选，不无故新建 Goal、丢弃报告或重跑不变的验证。等待确认、自然恢复或隔离环境时，继续其他已授权且不受限的开发线；保存准确恢复条件，不无限重试。持续到目标达成，但遵守实际工具/系统预算；不能用本节绕过硬限制、伪造自动续跑或将未完成标记完成。
9. **记录和透传。** 记录平台/账号的不敏感标识、实际额度来源、受限类型、已有权益、该次授权、幂等尝试标识、操作结果和复查结果；不记录凭据或付款敏感信息。总控统一更新状态，新任务提示词必须附本节与当前桌面政策；进行中任务在安全边界读取并执行，不改写已归档的冻结输入，不仅因调度/额度政策变化重开产品审查。文档更新不等于运行中 Goal 自动生效，必须向总控及各开发线实际传达并记录接收状态。

### 当前桌面操作政策（2026-10-22 用户撤回静默限制）

2026-10-22人类已撤回静默桌面、不占用/聚焦/点击限制及先预约用户时段的偏好。已授权任务可直接computer use操作桌面端及按原验收运行本机原生测试；互斥资源由总控内部协调，不把CLI认证/后台/headless/隔离桌面作为前置。具体阶段源码/写面/运行票/被拒工作边界不随政策扩大；指定双审、冻结、必要验证、CI/平台/真人/远端和付款逐次确认门保持。当前详细政策见 /Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md。

### ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）

- 用户明确要求“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。ZCode 默认完全访问（permission.mode=yolo），MiniMax Code 默认始终授权/Full access（permissionMode=bypassPermissions）。创建或进入审查任务时读回该任务实际模式；用户级配置不能证明已有会话即时切换。已获授权，不重复询问默认模式。
- 当前计算、Goal和冻结审查不重启；在应用支持的安全边界确认或调整权限。完全访问不改变审查只读职责：仅运行约定验证、写独立报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
- 指定模型与思考等级、同版双审、意见处理、CI和远端核验保持；桌面按2026-10-22当前政策执行，不扩大为新增付费、读取密钥或绕过平台逐次确认。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。
