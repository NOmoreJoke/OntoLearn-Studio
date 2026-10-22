# T09 私有多阶段证据原型完整独立审查 — ZCode

你是本轮独立外审者。要求模型设置：GLM-5.3 / 最高 max / permission.mode=yolo。这只是要求，不是实际设置证明；须由真实应用/任务读回provider、model完整标识、reasoning、permission、session/task ID、正文受理和最终终态。若身份不可观测，写无法验证，不把应用名或用户全局配置当本任务实际回执。

这是已有12699原型的完整指定补审，不是新S2、缩验收、新功能或只看摘要。只写你自己的完整报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-stage-evidence/docs/reviews/T09/stage-round-1/zcode-glm53.md`。产品、测试、配置、依赖、锁、共享文件和其他流程文件全部只读，不commit/push/切分支/PR。不得读取或接收另一方本轮prompt/报告/输出/意见，也不得传递你的当前意见给对方。双方相同固定base/product各自独立完整审查，不用历史Codex内审或另一方结果替代。

## 固定身份与输入角色

- 原树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-stage-evidence`；branch `feature/weekly-t09-stage-evidence`。
- approved shared base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；实现 `12699cc0f536f5875e8b021349b58c2c954145cc`，tree `813af592a58396bf0a90a7f9f22076a5e5862266`。
- 实际local continuation parent `74b17a43fd51b0fa89d810c664d185583a140e48`，继承S1产品 `76596656908ed84e577e8202a602e3256d5febcc`；local parent不能当shared批准base。
- 原验证/内审保存e6519932b0b20fd1862dcd6f038a621fce8177f5；固定流程ref `9a1baa74f2b6482106eb7c8090efef7f7ba065e2`，其后本轮仅追加准备材料。
- 清单 `docs/reviews/T09/stage-round-1/input-manifest.json`；原件映射 `validation-and-history-map.json`，可读索引 `verification-and-history-index.md`；当前操作政策快照在`inputs/`。先核实际CWD/Git root/branch、base/product/tree/parent、逐条Gitblob/bytes/SHA，审查结束再核实现/测试/内容未漂移。
- 当前protected AGENTS SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，原树本来未暂存，不修改、stage或reset。S1另树round-1的十一文件不改、不拿其Pass覆盖stage，本轮没有现成指定Pass。

manifest分role保留：完整sharedbase→126的77路径产品diff及34个运行源/内容/测试；localparent→126仅三增量；9a1流程overlay；批准base共享依赖上下文；本轮政策/提示/映射。相同path不同role/ref不可混淆，不能用变化物理HEAD冒充固定产品字节。所有review任务后来如使用独立worktree，必须另附不可变、独立hash的实际source/report绝对路径与各角色映射、Git树/产品hash及任务设置回执；保持本提示原字节。只是路径变化而产品同一才能继续；实现/测试/依赖/配置/验收或base变须新候选、必要验证、双方全新完整任务。

## 必须全文审查三文件及完整继承上下文

1. `packages/engine/src/ontolearn_engine/learning/stages.py` 全文。私有类型StagePlan/Slot/Ref/StoredStage/Completion/Receipt与StageReader/EvidenceView；完整bind_stages/require_current及所有守卫，不能只看最后两个函数或成功例。
2. `packages/engine/tests/test_learning_stages.py` 全文。完整80专项的参数化正反例、SyntheticReader/合成ledger、validation形态和两个真实批准I04探针的证据边界，不把测试给定rows说成领域查询。
3. `docs/iterations/T09/stage-evidence-contract.md` 全文。当前只读私有合同与owner信任/一致读/CAS/持久化前置，不是公共注册或已交付正式实现。
4. 完整继承S1源码/输入/课程/reducer/真实七项I04/独立UI及接口文档作为实际依赖和对比上下文，按manifest固定读取；本任务最终对应126原型，不能用另树765审查结果、后来T01未批准代码或d969/72aa流程文档补出产品能力。固定17输入/50案例计划不是50领域实跑。
5. 按manifest读取必要批准5f的唯一canonical schema/registry/errors/资源、Store/JobStore/result/page/依赖失效/测试helper和架构PRD，验证实际compatibility；不得复制第二公共schema、SQLite真相或Store写通道，不能采用其他线未批准实现/环境/结果。
6. 全部历史失败/最终日志与STAGE-01/02处置、设计对齐回执、blocked/等待/状态的历史时点。旧报告只作证据线索，不是你的结论；不忽略文档错误通过声明。

需求依据是固定PRD V0.6 FR-003/006/100–105、9.4、11.2、12.1及附录C/D/E/G。完整原文在approved base并由manifest绑定SHA7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb；必须保留原57P0及全部原验收，不因名为原型而缩减关键门。

## 重点反例与真实信任边界

- 调用者只能给Context和有序StageRef，Plan/结果/job/页/completion/祖先/当前输入必须来自owner受信视图；renderer passed、客户端完整自洽假ledger、仅resultId/createdAt/revision大小均不能证明当时成功。
- planId/root_input_version必须非空非空白str；plan_version/epoch/ledger序号严格类型，True不能别名1。project/task/attempt/currentinput/epoch/root/stage/输入与完成序号完整绑定，不允许跨尝试/项目/输入、遗漏/未知/重复/重排stage或result重用。
- job必须实际succeeded且resultRef/jobId/project/snapshot/输入/能力精确相同；同快照另一query/validation/definition/scope/参数/依赖/实现/版本不能顶替。quality必须canonical validation形态，query不能替代。
- completion必须阶段真实成功且当时current时原子持久保存，独立读取不可变UUID回执，与今日结果除state/staleReason/historicalSelectionRequired三运行态字段外全部核心JSON相等。不从今日stale补造当时current。原型本身无法证明owner真的持久或不说谎，这是关键缺口。
- 批准I04修改事实后的旧结果真实stale必须原样保留；历史slot返回旧stale和原current完成证据，不改称historical/current。终态必须今日仍current、无stale、payload可用并绑定真实当前尝试输入；完整结果正确性仍待领域checker。
- 分页必须从null完整链到null，binding/project/result/snapshot/scope/parameters精确匹配、顺序正确、无重复游标/rowId/换绑/缺页/驱逐；completion不代丢失payload。root→每阶段→terminal及相邻阶段真实祖先，不按revision猜。同快照须plan明示；输入选择与完成序号交替。
- 一致读结束再次核完整当前plan；require_current只消费前重核，跨事务真正CAS由T01实现。重开/多窗口/复制/新attempt/输入切换及迟到结果不洗辅助、不把旧receipt登记当前完成。
- StageReceipt只表绑定，不能生成领域passed、operationComplete或independentTransferSuccess。绑定合法而payload错仍应由完整领域比较拒绝；S1辅助reducer/UI floor不代持久来源。
- 两真实I04探针真实read发布、事实编辑、stale/page/再次编辑拒绝；test.read回显给定rows，Plan/完成ledger/祖先仍测试内存，非SPARQL/SHACL/持久账本或产品重开CAS。canonical validation正例也是私有绑定测试，不是SHACL实跑。

## 原件、运行限制和结论门

最终原件80专项exit0与fullcheck exit0（648 Vitest通过/16 headless明确skip/1174 Py，静态/类型/构建/ruff通过）均绑定126。两个明文SHA及9份gzip raw/archive/bytes见映射。首49通过3失败、后续fixture55通过1失败/marker67通过2失败等完整原件保留，53/57/69及1163中间态不能代最终80/1174。STAGE-01独立修前纯探针及修后拒绝、STAGE-02修前静态/修后canonical测试逐项复判，不伪造修前运行。S1旧664/1094只归765，其browser成功不代stage或正式native。

本轮准备只做静态Git/JSON/hash/gzip，不执行产品命令。外审先全文读取原件并对照源码，不为审查惯例无变化复测；没有实际运行的命令写“本轮未运行，引用固定原件”。准备授权不授产品/额外服务/GUI运行权；未来如确需具体疑点的新验证，先保留疑点并由总控另给精确运行票，不能自装依赖、改配置/锁、启动服务/产品/浏览器/Electron/native/HMR或认证流程。静态只读Git/JSON/gzip核对与自己的报告写入可做。

当前产品原件明确formalDomainRuntime=false、durableLearningLedger=false、未公共注册/未接LearningService/UI/Store，且无包/native/双OS/真人验收。必须把以下作为未关闭关键门实际审查，不得删成“未来集成所以不影响整体Pass”：T01受信attempt/最高辅助与跨attempt来源、完成时不可变持久ledger/实际root-input-epoch-祖先/一致读/消费CAS；T00批准唯一公共合同；实际领域adapter、正式App/bridge/生命周期；课程入包/无模型离线；T08完整代做/T10实际报告；双OS/包/native/至少五名非开发新手80%；同版指定双审/全部意见/CI/develop正常合并/远端及原57P0。

**关键验收缺失不得给整体通过。** 若确认缺少必要实现/验证或存在阻断，最终写“不通过”；若关键身份/来源/原件无法核实，最终写“无法验证”。可以分项记录私有纯函数/基础设施已验证，但不接受以“有界原型通过”“有条件通过”覆盖整个当前原型关键验收缺口。不得预设为了排期的Pass，也不得伪造指定模型意见；报告须是你的真实完整评判，开发线将保留你的NotPass/无法验证原文和终态后补齐，再依变更冻结新候选。

## 完整报告与实际任务终态

用中文完整报告：实际app/provider/model/reasoning/permission/task-session与正文/设置受理证据；原树/分支/sharedbase/localparent/product/tree/process/manifest/prompt/未来映射hash；逐文件全文覆盖；实际静态命令/结果/退出码、所引固定原件与本轮未跑项；分清纯逻辑、合成ledger、I04基础设施、domain、durable、包/native、真人和生产。每发现给稳定ID/P0–P3/精确路径行/触发输入/影响/直接证据或复现/建议，禁止自行修产品。STAGE-01/02和历史失败逐项已关闭/未关闭/证据不足；全部父门和关键缺失单列。最终明确通过/不通过/无法验证与原因，不弱化关键缺失。

任务必须实际运行至自己的terminal并保存完整全文报告，仅正文受理/草稿/开始不算审查完成；创建/设置/终态/全文/hash由原owner真实读回绑定。源码漂移/环境不可用/无法完成据实保留，不伪造任务或终态。审查者不push/PR/合并；同版双方真实通过、全部验收和意见关闭后仍由原owner按总控gate执行CI/正常合并/远端。父Goal不因本任务启动或结束自动完成/恢复。

## 当前操作、额度和权限政策（逐字快照）

以下不改冻结产品；当前人类已撤回静默桌面偏好，桌面创建/设置/读回仅由总控内部短lease串行，后台推理不独占应用。当前本包没有T09创建lease，不创建模型/重复既有任务/authflow。完全访问不扩审查写面；禁止新增付费/API/订阅、读/输出密钥、重置确认绕过、宽泛结束用户进程。

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

# 当前桌面操作政策：撤回静默限制

总控已正式read_thread核验人类最新原文：“直接使用computer use调用桌面端的工具就行，删除我之前要求的静默桌面操作”。来源chat `01a1628e-1220-7fb1-9135-97cbea4a3ed5`，turn `01a162ce-e65a-7753-84ab-47db9975c1d3`，human message `01a162cf-5a30-7e13-95ee-24d468007ce5`。这条在“现在可以登录”答复之后，当前执行以其为准。

## 立即生效

- 撤回此前静默、不占当前桌面、禁止聚焦/点击、须先预约用户时段的偏好。已授权任务可直接computer use操作桌面端审查工具及按既有验收运行本机浏览器/Electron/native；不为常规桌面操作重复询问，不把CLI认证、后台、headless或隔离桌面作为前置。
- 同一桌面应用、原生故障测试与其他互斥资源由总控内部调度。本轮最先创建ZCode/MiniMax任务的负责人是原T06聊天 `01a15bba-0c8a-7dc2-b612-5b5c4ec4a4b9`；直接创建ZCode GLM-5.3/max/yolo完整新审，保留现有MiniMax真实session/turn/stream，不重复任务、不互泄本轮意见。其自有OAuth等待已实际收尾，不再给本人CLI登录前置。T06创建已完成并释放前台；后台任务保持，不独占整个应用推理时长。当前短时创建/核验lease以execution-state.json为准，现交T02。
- 尚在排队的T02/T03/T04/T07/T09/T10/T11不自行抢同一桌面；总控按实际资源交接。内部协调不是向用户重新申请桌面时段。完整必要验证可以按任务授权执行，不以“静默不了”一律停工；原native/窗口验收条件保留，不用隐藏/stub/禁hang monitor代真实结果。
- 操作政策撤回不扩大具体阶段写面/运行权：纯文档、源码静态准备、未签native caller、尚未获运行票的构建/探针，以及已被自动审批拒绝的工作仍按各自原界限；不得把桌面可用当ABI/loader/drain、SQLite损坏HOLD/whole-H/owner或其他产品验收通过。
- 指定模型/思考/逐任务权限、同版双审、必要验证、完整终态/全文报告/全部意见、CI/两OS/真人/develop远端及全部57P0保持。无新增付费、密钥读取/搬运、重置逐次确认绕过或宽泛结束用户进程授权。

## 规则传播与历史

阶段主聊天唯一修改主repo AGENTS及注册worktree政策副本；总控唯一修改common、active scope/goal-objective、permissions、state/队列。当前主AGENTS15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，传播收据 `outputs/20261022_desktop_policy_update/propagation.json`；异版仅按原操作政策段更新，其余不覆盖。

历史冻结prompt、原始审查输入、历史报告与旧原件不改。新任务附当前政策，已有任务由原owner在安全边界透传；单纯guidance变化不是产品/测试/依赖/验收或base变化，不重建Goal、不因本政策重审现有MiniMax。旧“无GUI许可”“待桌面时段”“必须先CLI登录”只能按历史时点解读，不能继续成为当前阻断理由。实际派发/任务ID/设置与终态另记，不把policy落地当任务已完成。
