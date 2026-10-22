# minimax-m31flash : PREPARED ONLY / NOT DISPATCHED

Expected model: M3.1-Flash; effort: xhigh; permission: bypassPermissions. Actual per-task UI readback: null.

Candidate: e3c727dd90e22e7add5f0db94cefb57901af61f0. Evidence process: 0932268ddaaac29511bd57d26737ad48de1e8495.

Actual independent review cwd/process/input commit: PENDING ROOT SETUP. Actual task/session/turn: null. Planned report path within that independent tree: `docs/reviews/T08/round-2/minimax-m31flash.md`. Do not run this preparation against the developer checkout or old93516 review trees. No task creation/runtime/GUI authority is supplied by this file.

Shared complete body SHA256: `a49974c9aa06ee4dcf8b13c95e30f413d9f4a64fed6b215beb42dd6a2de7fa62`. Both designated reviewers receive this exact complete body and historical inputs; future peer opinions remain private.

<!-- COMPLETE SHARED BODY -->

# T08 下一轮完整同候选独立对抗审查

这是材料准备，不是已创建任务。新受审候选固定为 `e3c727dd90e22e7add5f0db94cefb57901af61f0`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；完整新运行／历史证据固定于过程提交 `0932268ddaaac29511bd57d26737ad48de1e8495`。原开发树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T08-agent-model`、branch `feature/weekly-t08-agent-model` 只是来源，**不是新独立审查树或已获执行票的证明**。新 review cwd、detached/process HEAD、task/session/turn、设置读回与报告输出根均待总控实际登记，不用旧93516审查树或任务冒充。

本文所有包内相对路径均相对 `docs/reviews/T08/dual-review-preparation-e3c727d/`；未来须从实际独立review tree下的该目录解析，不把它们当workspace根目录路径，也不读取原开发树的移动文件。角色报告路径则相对未来实际独立review tree根目录。

## 完整原范围与结论门

必须实质审查当前完整累计实现和全部原验收，不能只审修复差分、六组DOM、摘要或有限S1。全文读取原PRD V0.6，逐项覆盖FR-800–806、900–902、904，FR-204/302/400协作，附录C–G及F、G.5 A系列相关边界，第10–12节全文，尤其11.3全部九类、12.2全部七项及Q9真实服务。FR-903保持原P1；原57项P0、附录/需求/验收基线及原延期安排不改。清单与数量不等于产品验收，集成前置也不是完整验收条件。

整体关键验收缺失时结论须为“不通过”或“无法完成验证”；允许具体说明已实现代码中未发现哪些问题，不得把局部Pass当父功能Pass。缺前置不能成为不读源码、不完成可做审查的理由，也不能以合成端口、SSR、协议手工消息或静态清单代替真实运行。完整审查是本轮任务，不是预设必须通过。

## 精确输入与阅读顺序

1. 核 `input-manifest.json`、完整产品树与base→candidate全部差异清单，核全部28源／测试／fixture；以固定Git对象为准，不读取移动HEAD或别线未批准实现来补空。`inputs/current-product/`是本轮源，源码统一`.snapshot`数据后缀，字节不变；禁止执行或编译这些归档副本。`inputs/current-context/`含本轮完整PRD、M0计划、ADR、锁、真实App/main/preload/contracts上下文，M0实际归档路径是 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`。
2. 原101项输入成员全部原字节保留于 `inputs/history-original/`，包括原完整审查正文、需求/验收表、controller计划/决策、旧25源、完整PRD、内审1–8、首次失败gzip/元数据、固定输入/CSV观测、717项原check等。旧93516身份、旧25/44/828和旧运行只用于历史，不是本轮28源或新运行；不得漏读旧失败、压缩原件及其限制。原679/691/706仅有摘要/成功日志SHA，不虚称其完整成功日志已补齐。
3. 完整读两份历史指定NotPass：`inputs/evidence/docs/reviews/T08/independent-review-roots-20261022/zcode-terminal-20261023/zcode-glm53.report.md` 与对应 `minimax-terminal-20261023/minimax-m31flash.report.md`。它们是**上一轮共同历史输入**，不是本轮对方意见。原M的1P1/7P2/3P3、Z的3P3及双方整体NotPass均保留。历史Z未逐字段展开三gzip/两中间JSON、M的Ruff计数差异/管道npm真实exit未知/首探针失败后改断言等限定与原件一并核，不静默升级覆盖。
4. 完整读 `inputs/evidence/docs/reviews/T08/post-designated-review-20261023/` 的14项裁定/争议、bounded observations、独审分析、修复独审1 NotPass与2局部Pass、737/739历史check及各原始日志。owner的采纳/争议和局部通过不关闭指定问题，由你独立判断各原意见在当前固定源是否成立。
5. 完整读 `inputs/evidence/docs/reviews/T08/dispatch-boundary-20261023/` 的微任务/上下文修复、修前3失败、112纯TS及其限定、独审、7a33完整752/1052、真实验收计划；再读 `mounted-harness-preparation-20261023/` 的计划与实现首轮NotPass/纠正复核、mounted01失败、02成功但覆盖被指出不足、03最终六组真实DOM、symlink拒绝负例、最终e3完整check及各metadata/result/raw、Electron自动下载触发命令/文件SHA/来源说明、28源与9依赖前后身份和完整交接索引。
6. 按完整树及全部base差异追查调用链和遗漏；不能只读28文件或旧44差异。原设计/所有历史发现、原始失败与后继修复都进入判定。规则以 `inputs/current-policy/` 全文为准，历史launch旧GUI限制按时点解释，当前实际执行仍服从本轮精确资源票。

## 必须实质检查的当前累计代码

- codec对未知/截断/空/非法结构、单choice/非流式/JSON、thinking响应与历史、多轮tool ID/关联/重放/长度是否严格；enabled响应字段与无tools历史规则分开，不默默降模式。受测provider pin由宿主预先提供，响应model/fingerprint在工具前精确复验；请求别名不硬等返回版本，不TOFU/模糊后缀，不把字符串相等当真实权重、effort、能力或质量证明。
- 整批参数先验、全部TrustedContext字段（project/revision/snapshot/scope/module/mode/有序选择）、执行微任务紧邻端口前及回收／答案时的复验，authority异常净化、取消/超时/迟到、并发BUSY与预算/重复ID分类；模型不能注入项目/授权/确认，跨问题不能清空全会话ID/预算。只读、草稿、隔离运行边界及正式ChangeSet独立确认仍完整保留。
- P1的JSON参数形状检查不是SPARQL执行门。default无ports也不是已验证真实parsergate；必须由获批I05/T04唯一执行器及T00 composition保证SELECT/ASK范围、禁外联/写入与安全拒绝说明。不得造弱lexer/关键词黑名单，BASE不自动等于网络，CONSTRUCT不笼统叫写入但仍按原P0支持面判断。具体接口未交付的缺口必须留在完整结论。
- 请求输出ceiling与响应自报completion超限检查不同于输入/total usage或费用控制；缺usage仍未知，不是零。事后拒绝不能撤回费用，不改变Q5或默认费用政策。I06仍须最终发送前检查真实总量/预算/主体/当前配置和隐私。
- 收据完整呈现，失败/取消/过期/历史不能被自由文本或仅引用成功项隐藏；provider失败、预算尽、部分批取消仍保留已完成草稿和取消收据，快照不可反写；异常code/getter/proxy变异不能将原始异常/路径/单元格/凭据送入本地收据或provider投影。安全枚举外发仍须I06授权。
- 实际messages/tools/reasoning/摘要/历史/错误、字段来源、当前隐私/策略/端点/主体/配置版本及完全本地切换的最终字节授权、凭据与日志权威都在I06；T08投影只是最小化，不能从模型body、旧prop或构造快照授予外发，也不建立第二设置/公共注册表/Store writer。
- 真实AgentSidebar源码与事件：七模块/两模式、最多四动作、本地/模型未就绪/缺handler/旧context的发送、retry、Diff、取消；同context同步防重入，全部context轴隔离输入/锁/错误，迟到回调不污染新context或覆盖后续编辑；React文本节点不能变成HTML或资源加载。DOM六组必须核实际断言、非busy正反对照、原错误oracle与后续纠正，而非只看pass摘要。
- 两份新fixture只能证明真实ReactDOM与Node纯会话编排。Node原生Buffer留在Node SSR bundle；专用测试binding不进入公共App。Chrome显式exe/hash/实际版本、锁/9依赖前后hash、真实output归属、全新profile/offline/页面request abort与失败留档须真实。合成端口AbortSignal/late result不等于T00/I04持久job取消/ACK/终态，组件截图不等于全App/native视觉或两OS验收。
- 原v1合成case、v2真实RDFLib/CSV输入及完整oracle不可删：Q01/Q02阶段、同数量错义A02、001/002身份/名称/行号、SPARQL原文/哈希、错误/取消/旧快照等都逐项核。手工模型协议和有限库probe不是实际NL生成、正式query/reasoning/behavior/scenario能力或Q9/11.3评估。

## 已有证据与剩余真实缺口

e3自身完整check owner实报752TS/1052Python、exit0；mounted03六组包含14模块模式组合与七轴，28源/2输入/9依赖前后同、Chrome155.0.8059.85、页面requests/pageErrors空。方案、实现、DOM和完整check的Codex独立核验只作为历史证据，不是你的运行或指定Pass；总控接收也不是替你批准。mounted01真exit1、02虽exit0但覆盖被指出不足，原件均保留，不覆盖成最终成功。

总控有限收件原文在 `inputs/controller-intake/T08-e3-mounted-actual-controller-intake-20261023.md`，5032字节、SHA256 `9d363775591a262350b333c71ea1b99286d7d930a270f41131a69bf7789ee0d8`。该收件未重审原26算法、未关闭原NotPass/P1/P2；历史Node二进制SHA未记录，保持UNKNOWN，不拿当前文件反推历史。总控仅核三PNG哈希，未做视觉审查；owner曾查看隔离组件截图也不是全App验收。最新T01具体后端执行票已发、实现仍在进行，尚无固定可供T08消费的获批供方，不把授权、开工或未来方案记成真实接线通过。

尚无T08实际获批I05/T04 parsergate与composition、T04 QueryPage同页、T00/I04真实job取消/ACK/终态、I06实际当前隐私/最终授权/安全存储/provider/费用、T01真实Diff/真人confirm/原子/undo/restore、T09实际离线/学习记录、原11.3/12.2/平台/真人/CI/远端和发布证明。不得复制未批供方、造第二组件/执行器或要求花费API来填空。具体依赖未交付不等于要等整模块完工，也不关闭相应原P1/P2。

## 只读职责、执行票与报告

当前只准备材料：没有新任务、新review root、GUI/浏览器/Electron、测试或setup授权。总控未来派发须先登记两棵独立实际树与证据/输入提交，读回每任务模型/effort/权限，明确各自可执行原check/headless probe、环境和互斥资源。不能从本文件自行启动或沿用旧任务/旧运行票。实际派发后的普通必要验证不能因历史“无GUI/CLI前置”被泛禁，但不得擅自扩SQLite HOLD/native/固定端口/付费范围。

只读实现/测试/依赖/配置，不改或格式化源、不提交/切分支/push/merge，不改冻结prompt/manifest，不读取secret/.env/keychain或真实provider API，不新增付费，不新建/修改Goal。报告与scratch只写各自获准路径，独立venv/node_modules/cache/tmp/基线源；失败/原退出码/DB/journal保留，不删除或新ignore求绿，不宽泛kill。完整相同输入提供双方；不得读取或互传本轮新对方意见。

中文报告必须记录实际任务/session/turn、模型/effort/权限与读回来源、cwd/branch/base/candidate/process/input SHA、全文阅读覆盖及未读项、每个实际命令/退出码/原日志、历史运行/自行运行/静态推断/未验分别说明。逐项处理历史内审1–8、两原指定报告与14行裁定/争议，原严重度保留历史；新问题给固定文件/行号、触发、影响、证据、建议，缺前置与可修代码分别列出但都进入完整结论。

后附政策原文中有通用开发职责及历史排期；它们不把开发写权、建Goal、运行票或旧状态转移给本只读reviewer。controller的review.md仅为排期覆盖核验历史，不能当产品审查通过。

结尾明确“通过／不通过／无法完成验证”及完整原验收是否满足。实际终态、完整报告读回与意见处置才是完成，不以已创建/设置名称/流式片段/局部Pass代替。原两NotPass和P1/P2只由新指定审查依实际证据裁定，owner不先填关闭。



---

# Full policy/reference: AGENTS.md

SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`

# OntoLearn Studio Agent 指南

默认中文，结论先行，简洁。先读需求依据再动手；不确定就问，不猜产品决定。

## 1. 先读什么

| 场景              | 必读                                                                                                                                                                                                                 |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 任何业务语义改动  | [PRD V0.6](docs/prd/PRD-本体学习与落地Agent工作台.md) 对应 FR 条款 + 附录 C/D/E/G                                                                                                                                    |
| 工程/架构改动     | [M0 更新计划](docs/architecture/m0-review-and-update-plan-2026-10-19.md)（S1/S2/S3/C1/B1/U1 验收全文）、[ADR-0001](docs/architecture/0001-desktop-framework.md)、[ADR-0002](docs/iterations/I01/ADR-0002-storage.md) |
| 当前状态与待办    | [M0 清单](docs/m0-checklist.md)；进行中迭代见 `docs/reviews/Ixx/status.md`                                                                                                                                           |
| 迭代 I01–I06 执行 | 仓库外总控 `../iteration-control/2026-10-19/scope.md` 与 `state.json`                                                                                                                                                |

状态快照（2026-10-20，以上述文件为准）：I01/S1 存储 spike 已合并 develop；I02/C1 CSP 与窗口恢复处于 CI 修复门禁；I03–I06 未开始。产品正式能力仍只有 health；存储是 Python 内部 API，未暴露给 IPC、UI 或 Agent。禁止把占位界面、测试替身或 spike 说成已实现的产品能力。

## 2. 仓库地图

```text
apps/desktop/src/main/      Electron 主进程：窗口安全、来源校验、引擎监督、恢复
apps/desktop/src/preload/   唯一桥接（按业务命名的方法）
apps/desktop/src/renderer/  React UI（无 Node 能力）
apps/desktop/src/csp.ts     CSP 唯一配置源（生产 meta / 开发 header 两个变体）
packages/contracts/         TS 边界类型与 zod 运行时校验
packages/engine/            Python stdio 引擎：protocol.py、storage.py、invalidation-v2.json
tests/unit, tests/e2e       vitest 单测；Playwright 驱动真实 Electron
docs/iterations/Ixx/        迭代设计、验收、证据；docs/reviews/Ixx/ 评审与流程记录
```

## 3. 架构不变量（违反即阻断）

- **本地优先**：不自动启用模型、遥测或云服务；不开 HTTP 端口；不引入云数据库或未经测量的图数据库。
- **渲染端隔离**：renderer 不得直接使用 Node、文件系统、shell 或通用 IPC；preload 只暴露按业务命名的方法，禁止 `invoke(method, params)` 式通道。IPC 处理器保持 sender/mainFrame/可信文档校验。
- **CSP**：只改 `csp.ts` 一处；生产脚本不得出现 `unsafe-inline`/`unsafe-eval`；不手写第三份策略。
- **确定性与 Agent 解耦**：确定性结果只能来自真实引擎；Agent 只产出草稿并调用白名单工具，不得自动确认自己的修改。
- **存储**：SQLite 是唯一可变源真相，正式写入只经 `Store.commit`（版本化、可预览、原子提交、旧基线拒绝）；RDFLib 图只从不可变快照重建，不能写回。
- **数据层次**：本体定义、断言事实、当前推导、场景副本、历史运行分层；历史与已提交轮次不可改写，缓存回收不得触及历史。
- **失效规则**：`staleReason` 只来自 `invalidation-v2.json`；仅改模型配置不使领域结果过期；历史/失败/取消不计为过期原因。
- **模型外发**（S3 前不得接入）：唯一网关在主进程，凭据只在主进程；Python 引擎不持有密钥，也不调用模型。
- **错误**：跨边界只传固定错误码和受限参数，不回传原始异常、堆栈、路径、单元格原值或凭据。

## 4. 改动类型 → 必跑验证

| 改动                                       | 命令                                                               |
| ------------------------------------------ | ------------------------------------------------------------------ |
| 任意代码或配置                             | `npm run check`（lint/格式/类型/vitest/构建/ruff/pytest）          |
| 涉及归档资料或 `docs/source-manifest.json` | `npm run verify:sources`                                           |
| 主进程、preload、bridge、CSP、窗口         | 另跑 `npm run test:e2e`（Linux 用 `xvfb-run -a`）                  |
| 引擎依赖、打包配置                         | 另跑 `npm run package:dir`，并在包内运行同一样例                   |
| 仅文档                                     | `npx prettier --check <文件>`；不批量格式化归档 PRD、审查和 `.pen` |

`I02_HMR=1` 的 HMR 探针会临时改写源文件，评审冻结期间禁止运行。结果须分开报告静态、运行、打包、生产四类证据，不以静态检查代替运行证据。

### 桌面工具与本地验证（2026-10-22 用户更新）

- 用户明确要求“直接使用 computer use 调用桌面端的工具，删除之前要求的静默桌面操作”。此前静默、不占用当前桌面、禁止聚焦或自动点击、须先取得桌面时段的偏好已撤回，不再作为现行限制。
- 已授权任务可按需直接使用 computer use 操作 ZCode、MiniMax Code 等桌面工具，也可运行本机浏览器、Electron、原生窗口与恢复验收；不为常规桌面操作重复询问或把后台、headless、隔离桌面作为前置。
- 多条开发线操作同一桌面应用或使用互斥测试资源时，由总控内部协调，避免互相改动任务或干扰测试；无需额外向用户预约桌面时段。清理进程仍须核对自有 PID 和任务归属，不得宽泛结束用户或其他任务的进程。
- 验证仍须覆盖原验收条件，区分静态、运行、打包与生产证据；不得用隐藏窗口、禁用 hang monitor 或 stub 原生提示冒充真实原生验收。操作政策更新不改变冻结候选、指定双审与发布门禁。

## 5. 分支、迭代与评审门禁

- **并行开发为默认执行要求（2026-10-20 用户确认）**：适用于当前 M0、后续里程碑、不同功能模块，以及单个模块内可独立开发的具体子任务。先识别真实接口、数据和集成依赖；可独立验收的工作须拆分并行推进，不得仅因迭代编号或模块顺序而全量串行。强依赖保留前置条件，不为增加并行数而重复实现或提前假定未冻结契约。
- **独立 worktree + feature 分支**：每条并行开发线使用自己的 Git worktree、feature 分支和负责 agent，禁止多个开发 agent 在同一 checkout 切分支或同时写文件。迭代使用 `feature/Ixx-<主题>`，模块子任务使用 `feature/<模块>-<子任务>`；其他改动使用 `feat/`、`fix/`、`docs/`、`chore/`。从核验过的 `develop` 提交切出并记录 base SHA，经 PR 合回；不强推共享分支。提交前缀使用 `feat:`、`fix:`、`docs:`、`test:`、`chore:`。
- **拆分与文件责任**：启动前记录各子任务的范围、前置依赖、接口约定、文件负责人、验收和集成顺序，再分配独立 agent。共享契约、存储迁移、能力注册表、依赖清单与锁文件指定唯一维护者；其他开发线提出接口需求，由维护者统一修改。依赖尚未就绪时，可先做独立设计、纯模块、真实库探针及对应测试，后置正式接线与联验；替身通过不得计作集成完成。
- **M0 的并行拆分**：I02 继续当前候选评审；I03 可基于已完成的 I01 并行设计；I05 可先做真实候选语义、外联拒绝、依赖与打包验证；I06 可先做网关 ADR、独立授权与凭据模块。I04 实施须等待 I03 同版本设计审查通过并合并；I05/I06 的正式接入及最终验收须等待各自实际依赖就绪，并补齐与存储、任务和窗口生命周期的联验。引入真实依赖时即做相应打包验证，不全部推迟到最终集成。
- **运行资源隔离**：各 worktree 独立依赖环境、构建输出、临时数据、日志及测试证据，开发端口和应用测试数据目录分别配置；不得共享可变运行库。桌面焦点、原生故障恢复、系统凭据存储及外部审查应用的 UI 操作由总控内部协调串行使用，避免运行互扰，不以向用户申请桌面时段为前置；已有固定端口或未隔离资源的测试须排队。
- **并行开发、按依赖串行集成**：每条开发线独立验证并履行现行评审门禁；合并前同步目标基线、处理冲突并验证实际集成结果。目标基线或受审内容变化时，按现行规则重新验证及独立审查，不沿用旧版本通过。保留双指定模型、CI 和远端核验要求；子任务完成不等于父模块或里程碑验收完成。
- **冻结与调度记录**：候选冻结后不得修改受审路径，任何实现、测试、配置、依赖或验收改动都要生成新候选，并按现行门禁重新独立审查。其他工作在独立 worktree 推进，不干扰冻结候选。总控记录并行任务、worktree/分支、base/head、文件责任、依赖和资源预约；仅按实际进展更新状态，不把获准并行登记为已启动或完成。
- **与旧计划的关系**：本节取代旧 `scope.md` 中“所有迭代必须前项合并后才启动后项”的统一串行调度要求；执行时总控须同步相关范围与调度记录，保留原需求、真实技术依赖、验收及评审门禁。后续功能模块和子任务同样执行本节，无需为常规并行拆分重复征求授权。
- **进行中开发与 Goal 的过渡**：按最新桌面操作政策执行；并行策略在安全边界用于新任务/新开发线，不强行迁移正在冻结审查的 checkout、不改写其候选、不重建已有 Goal、不丢弃报告或重跑无变化的验证。用户授权的 AGENTS/调度文档变化单独记录前后哈希与适用范围；若未改变受审实现、测试、依赖、CI、验收或集成基线，不将其误判为受审产品变更，不单因此重开整轮审查。若实际受审内容或基线确有变化，仍执行原重新审查规则。审查代码读取固定 SHA，实际执行遵守最新操作约束。新 worktree 须携带并核对最新指南，不能只读取旧基线中的 AGENTS；总控负责同步规则，开发会话各自维护状态，避免共同改写 `state.json`。
- 不混入其他会话的未提交改动；禁止 `git add -A` 或整体 stage。只 stage 本任务文件。
- 复杂或高风险交付使用独立 agent 审查，避免并发修改共享契约文件；不得替换指定审查模型或降低门禁。

### 效率与额度恢复（2026-10-20 用户确认）

- 以正确交付和开发效率为优先，不因 token 消耗缩减实现、异常处理、上下文或必要验证。充分使用实际可用的并行 agent/worktree；避免重复探索、无变化重测和无效轮询，不擅自更换指定模型或降低审查门禁。
- 用户说明 ZCode、Codex、MiniMax Code 均有额外重置次数；遇实际额度限制时由账号唯一负责人核实状态，优先通过经核验的官方方式使用已有权益恢复，成功后续接原任务。其他开发线保存现场并继续无关工作，不重复消费同一权益；短时限速、服务/认证/账单故障不能当作额度耗尽盲目充值。
- 自动恢复受实际工具/平台约束：Codex `consume_usage_reset` 每次必须取得用户对该次操作的明确确认，未来批量授权不能替代；只在工具的额度条件满足时使用，同次不确定重试复用幂等 key，完成后核验额度，不因刷新失败重复消费。ZCode/MiniMax Code 的可用恢复机制尚待核实，不虚称已实现无人值守充值；禁止通过 UI 绕过工具确认。
- 已有重置/余额与新增付费分开：本次未提供新增付款的单次金额及累计上限，实际购买前须明确这些条件及授权；不将“不考虑 token”扩大为无限付款、自动订阅升级或切换付费 API。完整执行与透传规则见仓库外 `../iteration-control/2026-10-19/goal-objective.md` 第九节；运行中 Goal 须实际同步，旧冻结输入保留。

## 6. 文档与证据规范

- **唯一状态来源**：完成度只在 `docs/m0-checklist.md` 和对应 `status.md` 中维护；其他文档链接过去，不重复“不代表 M0 完成”之类的声明。
- ADR 采用后放到 `docs/architecture/000N-<主题>.md`；迭代目录只保留设计、验收和证据。
- 证据只提交摘要、关键 JSON 和哈希；大段原始日志、截图、runtime dump 优先放 CI artifact。确需入库时写明理由。
- 文档写决定、理由、未决项，每份 ADR 控制在 1–2 屏；不编造性能数字、容量通过线、日期或人员承诺。
- 不提交凭据、业务数据、`.sqlite`/`.db` 运行库、`.env`、`.mimosa/`。

## 7. 编码约定

- TypeScript `strict`；边界数据一律经 zod `.strict()` 解析。Python 3.12 + ruff（line-length 100，E/F/I/UP/B）。
- JS 直接依赖写精确版本；npm 与 uv 两份锁文件随改动一起提交，CI 使用 `npm ci` 和 `uv sync --frozen`。
- 测试断言真实需求和错误边界（完整预期集合/顺序），不只断言数量或按钮可点击。
- 不设 PRD Q2/Q3/Q5/Q6/Q7/Q8/Q9 的默认答案；遇到这些决定时停下来询问。

### ZCode / MiniMax Code 默认执行权限（2026-10-21 用户确认）

- 用户明确要求“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。ZCode 默认完全访问（permission.mode=yolo），MiniMax Code 默认始终授权/Full access（permissionMode=bypassPermissions）。创建或进入审查任务时读回该任务实际模式；用户级配置不能证明已有会话即时切换。已获授权，不重复询问默认模式。
- 当前计算、Goal和冻结审查不重启；在应用支持的安全边界确认或调整权限。完全访问不改变审查只读职责：仅运行约定验证、写独立报告，不修改实现/测试/依赖/配置，不提交、推送或切分支。
- 指定模型与思考等级、同版双审、意见处理、CI 和远端核验继续适用；桌面操作按本指南最新政策执行，不扩大为新增付费、读取密钥或绕过平台逐次确认。
- 详见仓库外 `../iteration-control/2026-10-21-weekly-release/external-review-permissions.md`（worktree中从本体根目录定位）；新任务附上本节，旧冻结输入保留，单纯操作政策更新不触发无变化实现重审。



---

# Full policy/reference: developer-common-instructions.md

SHA256 `567b6e7064bf123dac46742aefa57e06f6ed2fe87ceec5225c395049be888fc1`

# 完整首版功能开发共同指令

用户已在规划聊天 `01a15bad-ceeb-7103-b611-fff95e1f31ee` 明确要求 OntoLearn-Studio 全部原定首版功能于北京时间2026-10-25前开发上线、质量不降，并授权“发送并落实到现有总控”。总控实际读取原始用户消息确认了授权。本指令用于新功能开发聊天；截止日是目标，不是保质按期保证。

先读取本目录 controller-handoff.md、plan.md、tasks.json 中自己的任务、requirements.csv、acceptance-baselines.csv、review.md，以及实际工作树最新版AGENTS和对应PRD原条款/附录。57项P0、附录C–G及第10–12节保留；P1/P2原延期安排不变。T编号不覆盖I01–I06历史；纯服务完成不等于父模块P0完成，integration_prerequisites不是全部验收条件。

本会话只负责指定的一项功能，建立自己的Goal（不存在时），不继承总控Goal。先核验并回执绝对worktree、分支、base、实际git状态、指南SHA、唯一文件责任、验收与下一交付。总控已创建独立worktree，切勿改主checkout或其他树；AGENTS是总控复制的受保护操作规则，SHA应为 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持未暂存，不混入产品提交。不得重建原I05/I06 Goal或继续写其树。

当前批准develop为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。I01–I04已合并；I05 C1在指定双审冻结，已发现词法语义阻断，I06在自己的14文件接线与隔离平台联验。不得采用未批准I05/I06实现、环境或测试结果为正式依赖。只读取已批准基线接口开展独立工作，具体接口缺口/共享改动向总控提供精确路径和依据。

初始共享责任（历史，已被下述逐项生效交接更新）：I06原独占 contracts/src/{index.ts,v2.ts}、contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json，desktop/main/{index.ts,task-service.ts,engine.ts}、preload/index.ts、renderer/src/{env.d.ts,App.tsx,style.css}；I05原保留其他Python Store/coordinator/worker/protocol、语义/resources、entrypoint/build/锁/CI/窗口安全恢复。这些逻辑文件在任何树中均不得抢写。新增私有路径可按本任务授权实施；现有共享文件、迁移和依赖锁一律先做具体交接。不得复制第二套公共契约、SQLite可变权威或Store写入通道来绕过交接。子任务独立worktree/feature和文件责任，复杂交付独立agent审查；核验真实并发槽，不将创建目录当作已启动agent。

后续责任变更补充：I05/T01双方实际接受、独立复核及总控登记后，只有 `packages/engine/src/ontolearn_engine/storage.py` 后续维护已交T01生效，详见 I05-T01-storage-ownership-handoff.md 和 execution-state.json。I05冻结树保持原字节，其余共享/14文件不变。不得将这个单文件交接扩张为其他文件授权；当前具体责任以总控实际生效记录为准。

2026-10-21新增已生效交接：T01除原storage.py外，已唯一接管Python四个 `packages/engine/src/ontolearn_engine/{job_store.py,coordinator.py,__main__.py}`、`packages/contracts/python/contract_v2.py`，及原I06 canonical七个 `packages/contracts/src/{index.ts,v2.ts}`、`packages/contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json` 和 `apps/desktop/src/main/engine.ts`，仅从批准5f独立实施格式基础。T03已唯一接管 `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`，仅做XLSX最小依赖/收集/受限probe。原I05/I06树原字节保留，可读/构建但不得继续维护已交逻辑文件；必要修复先精确返还。I06仍维护其余六个main/index、task-service、preload/index、env.d.ts、App.tsx、style.css，I05仍维护其他未交路径；既有测试、CI、resources等不自动扩权。三份新handoff协议及独立报告/实际接受/生效通知见本目录 I05-T01-format3-ownership-handoff.md、I06-T01-format3-ownership-handoff.md、I05-T03-build-ownership-handoff.md 和execution-state.json；这不是未批准代码采用、公共格式启用或运行通过。

2026-10-22人类已撤回静默桌面、不占用/聚焦/点击限制及先预约用户时段的偏好。已授权任务可直接computer use操作桌面端及按原验收运行本机原生测试；互斥资源由总控内部协调，不把CLI认证/后台/headless/隔离桌面作为前置。具体阶段源码/写面/运行票/被拒工作边界不随政策扩大；指定双审、冻结、必要验证、CI/平台/真人/远端和付款逐次确认门保持。当前详细政策见 /Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/desktop-operation-policy-20261022.md。 桌面仅在创建/设置/读回阶段按execution-state当前短lease串行，原任务后台推理不独占整个应用；CUA对Codex app的工具拒绝仍不得绕过。

开发至完整可审查结果，必要异常路径/事务/撤销/历史隔离均保留。AGENTS所需 check/sources/e2e/package 按实际改动执行，隔离项真实待验，首跑失败原件保留。文档/纯模块/静态检查不能冒充正式接线或生产。没有变化不重复测试。依赖资源缺失只阻塞相关部分，先完成独立工作，不擅自结束或暂停整个Goal。

最终完整验收前刷新实际批准依赖及develop、集成冲突并验证；冻结真实base/head。由同一开发聊天通过CUA在ZCode选择本精确工作树、GLM-5.3/最高，MiniMax Code选择本精确工作树、M3.1-Flash/xhigh；每轮双方各新建独立只读完整范围任务，不互传本轮意见。报告按 docs/reviews/Txx/round-N/{zcode-glm53,minimax-m31flash}.md，逐项含任务来源/模型设置/路径分支/base/head/检查命令结果/未验边界/问题严重度位置触发影响证据建议/历史逐项关闭/明确通过或不通过或无法验证。两个任务必须实际终态，全文读回、全部意见处置；不能自己把指定模型不通过改成通过。所有实现/测试/配置/依赖/验收或基线变化后重新验证并双方全新完整审查。纯追加流程证据记录对应关系，不自动触发无变化重审。

同版双方明确通过、验收和必要验证通过、全部意见有处置、实际推送内容与受审实现一致后才push/PR；实际CI通过后正常合并develop、核验远端与保护源。必须attach创建PR；无强推、绕过分支保护或双审前push。集成/外审按总控预约，减少前方候选基线失效。纯服务可单独冻结合并，但原父任务P0跨模块验收与完整发布门不关闭。

额度：效率和完整交付优先，不因token删减；真实告警由账号唯一负责人核实。Codex重置每次需本人明确确认/阈值/幂等，不能UI绕过；不新增付费、订阅、API消费或扩张授权。只读服务/身份元数据不含读取或输出密钥。真人非开发用户验收不能agent替代，向外招募/消息仍需用户明确授权。

各线只维护自己的 docs/reviews/Txx/status.md 及证据，不写根 state.json、tasks.json 或其他总控文件。及时保留可恢复SHA/原件和准确下一步；实际独立实现与验收证据成熟后向总控给出可读交付，不用反复询问常规实施许可。不能将配置/脚本存在、目录/模型名称或数量相同当作验收。完成后父模块/远端/上线分别据实记录。

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

2026-10-21单文件补充生效：在既有T01十二共享及storage责任之外，`packages/engine/src/ontolearn_engine/worker.py`未来维护唯一交T01；只从批准5f的9314B/2fa848aa…06f2f0施工，不复制消费I05未批准C3的13638B/3d934e79…4f99d语义worker。原I05 C3受审字节继续冻结；若审查需修先由root精确返还、T01停写保存SHA/差异，执行输入变重新验证/双新审。protocol/resources/语义模块/旧tests/build/CI等不随此转，其他owners不变；source wire/限额/格式3/ready并未获批。原offer/接收/独立复核与唯一责任/返还门见本目录I05-T01-worker-ownership-handoff.md及execution-state.json。此补充不改变前文完整第九节/最新桌面规则。

## 四文件基础层未来维护交接生效（2026-10-21T11:40:05.102755+08:00）

I05原owner分别释放并由T01逐项明确接收 apps/desktop/src/main/jsonl.ts、apps/desktop/src/renderer/src/task-presentation.ts；I06原owner仅释放并由T01逐项明确接收 apps/desktop/src/main/task-service.ts、apps/desktop/src/main/index.ts。独立复核eeb221ea…0562、原接收01fa5ce5…2731/2124ef6c…3fae均由总控全文读回，四接收路径实际clean且逐字等批准develop5f；生效登记见 foundation-four-file-handoff-effective.json，原协议bad9716a…2965及全部原件保全。自此四路径唯一未来维护者T01，原I05/I06停止所有checkout未来逻辑编辑，固定C4/e2c/961只读审查/构建保留。T01仅沿自己批准5f，不复制未批gateway/语义实现；I06保留preload/index.ts、renderer/src/env.d.ts、App.tsx、style.css及私有模块。其余协议/resources/旧tests/依赖/build/CI/语义路径不转移。

此项仅维护责任生效；当前纯表材料阶段授权不变，startup/schema/新码/runtime3/ready仍须总控精确阶段授权。返还任一路径须root精确路径/原因/基线/窗口/验证、T01先停写并保全HEAD/文件SHA/WIP diff/测试状态，再明确唯一接手者和生效点；旧owner不得自动回收。受审执行输入变化仍新候选/必要验证/指定双方全新完整审查，不继承旧Pass。原第九节、最新桌面政策、安全应用入口/内部资源租约、指定双审及push/PR/CI/正常合并门全部保留；历史文字不覆盖本新生效责任。



---

# Full policy/reference: desktop-operation-policy-20261022.md

SHA256 `2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1`

# 当前桌面操作政策：撤回静默限制

总控已正式read_thread核验人类最新原文：“直接使用computer use调用桌面端的工具就行，删除我之前要求的静默桌面操作”。来源chat `01a1628e-1220-7fb1-9135-97cbea4a3ed5`，turn `01a162ce-e65a-7753-84ab-47db9975c1d3`，human message `01a162cf-5a30-7e13-95ee-24d468007ce5`。这条在“现在可以登录”答复之后，当前执行以其为准。

## 立即生效

- 撤回此前静默、不占当前桌面、禁止聚焦/点击、须先预约用户时段的偏好。已授权任务可直接computer use操作桌面端审查工具及按既有验收运行本机浏览器/Electron/native；不为常规桌面操作重复询问，不把CLI认证、后台、headless或隔离桌面作为前置。
- 同一桌面应用、原生故障测试与其他互斥资源由总控内部调度。本轮最先创建ZCode/MiniMax任务的负责人是原T06聊天 `01a15bba-0c8a-7dc2-b612-5b5c4ec4a4b9`；直接创建ZCode GLM-5.3/max/yolo完整新审，保留现有MiniMax真实session/turn/stream，不重复任务、不互泄本轮意见。其自有OAuth等待已实际收尾，不再给本人CLI登录前置。T06创建已完成并释放前台；后台任务保持，不独占整个应用推理时长。当前短时创建/核验lease以execution-state.json为准，
- 尚在排队的T02/T03/T04/T07/T09/T10/T11不自行抢同一桌面；总控按实际资源交接。内部协调不是向用户重新申请桌面时段。完整必要验证可以按任务授权执行，不以“静默不了”一律停工；原native/窗口验收条件保留，不用隐藏/stub/禁hang monitor代真实结果。
- 操作政策撤回不扩大具体阶段写面/运行权：纯文档、源码静态准备、未签native caller、尚未获运行票的构建/探针，以及已被自动审批拒绝的工作仍按各自原界限；不得把桌面可用当ABI/loader/drain、SQLite损坏HOLD/whole-H/owner或其他产品验收通过。
- 指定模型/思考/逐任务权限、同版双审、必要验证、完整终态/全文报告/全部意见、CI/两OS/真人/develop远端及全部57P0保持。无新增付费、密钥读取/搬运、重置逐次确认绕过或宽泛结束用户进程授权。

## 规则传播与历史

阶段主聊天唯一修改主repo AGENTS及注册worktree政策副本；总控唯一修改common、active scope/goal-objective、permissions、state/队列。当前主AGENTS15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，传播收据 `outputs/20261022_desktop_policy_update/propagation.json`；异版仅按原操作政策段更新，其余不覆盖。

历史冻结prompt、原始审查输入、历史报告与旧原件不改。新任务附当前政策，已有任务由原owner在安全边界透传；单纯guidance变化不是产品/测试/依赖/验收或base变化，不重建Goal、不因本政策重审现有MiniMax。旧“无GUI许可”“待桌面时段”“必须先CLI登录”只能按历史时点解读，不能继续成为当前阻断理由。实际派发/任务ID/设置与终态另记，不把policy落地当任务已完成。



---

# Full policy/reference: external-review-permissions.md

SHA256 `feea1595894b347ff1151e5526bc21e2055911f2ba744670f08ba85765f8b53a`

# ZCode / MiniMax Code 默认执行权限

2026-10-21 用户明确指令：“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。适用于本项目现有和后续对这两个应用的调用；应用权限模式不改变具体任务的职责与验收。

## 默认与实际持久化

| 应用         | 默认模式               | 本机实际配置                                                             | 本次结果                                 |
| ------------ | ---------------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| ZCode        | 完全访问               | `/Users/kyle/.zcode/cli/config.json` → `permission.mode = "yolo"`        | 原子写入并读回；其他配置与原权限子项保留 |
| MiniMax Code | 始终授权 / Full access | `/Users/kyle/.minimax/config.yaml` → `permissionMode: bypassPermissions` | 原配置已经满足，核对后保留               |

ZCode 的默认配置路径、合法模式及 yolo 跳过权限提示的语义，来自已安装应用 `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs` 的实际配置加载器、schema 和权限判定实现。修改前备份为 `/Users/kyle/.zcode/cli/config.json.before-permission-20261021-084806.bak`，仅在需要恢复时本机读取，不复制进仓库或输出其他配置内容。

MiniMax 的配置和界面映射由已安装 `@mavis/local-runtime` 实际代码独立核验：`bypassPermissions` 对应中文“始终授权”和英文“Full access”。`config.chatPermissions` 不是已证实的全局默认入口，未手造或修改。运行时官方配置更新入口会清缓存并广播变更；本轮没有启动/连接运行时、修改其桌面 store 或重启应用。

## 调用时的执行要求

1. 新任务默认使用上述模式；创建/进入实际任务时读回其显示或实际配置，不只依赖用户级文件。项目覆盖值、显式请求参数和既有会话状态可能优先于用户默认。
2. 当前计算、冻结候选和审查任务不重启、不丢弃；在安全边界确认权限，必要时通过应用支持的会话设置切换。不能仅凭配置文件改动声称所有在途会话已经即时切换。
3. 用户已授权上述默认应用权限，常规调用不因旧提示词中的默认模式重复询问。应用硬限制、系统权限和平台工具自己的确认机制仍以实际支持为准。
4. 对抗审查仍只读实现；只允许约定验证和独立报告写入，禁止修改受审实现或自行提交/推送。完全访问是执行能力，不把审查任务改为开发任务。
5. 指定模型、思考等级、同版双审、意见处理、CI与远端核验保持。2026-10-22静默桌面偏好已撤回，可由原功能owner直接computer use，互斥桌面资源由总控内部协调；不必再申请用户时段。
6. 新任务提示词和共同开发指南附上本要求；历史冻结输入保留原样，文档权限规则更新本身不触发无变化的实现重审。

## 证据与接收

- ZCode 写前 SHA-256：`c7f88256c49fbae707d57bfcd294dfa4becee03169ded1f14f9ab7b8aa47bb5f`。
- ZCode 写后 SHA-256：`67f26b9702a009fa8353b77f9f9b6d44658bd9fc41f55b31e924d872cb2124`。
- 已逐项比较非权限配置及权限中其他字段，结构相同；未修改任务数据库、应用安装包、模型或思考设置。
- MiniMax 的本轮独立只读核验确认默认已符合；没有把静态文件核验当作每个运行会话的权限回执。
- 由现有执行总控维护调用指南与派发状态，在安全边界透传进行中开发线；实际发送/回执另行记录，不假定写文件即自动生效。

## 2026-10-22 后台恢复补充

当前人类已撤回静默桌面偏好，原功能owner可直接computer use；已启动的官方CLI/app-server任务继续。原指定模型、思考等级、逐任务权限读回、同版独立审查和全文终态门不变。T06两项真实任务已启动，桌面创建动作已结束；其他线由总控内部安排资源，不自行抢建任务。

历史：昨日短时答复曾被误记未答、随后又被误作本轮新答复，原件及16:01停止记录保留。当前人类已经撤回整个静默桌面偏好，原T06直接CUA创建ZCode审查，不再以旧时段/CLI认证阻塞；现有MiniMax任务保持。详见desktop-operation-policy-20261022.md。



---

# Full policy/reference: review.md

SHA256 `377053321db84c993a5461f1d13371b7c1627e59bab5aa59dfda50859229f347`

# 计划验证与独立审查

日期：2026-10-21（Asia/Shanghai）。审查对象为本目录的排期、任务依赖与需求/验收覆盖文档，未审查尚不存在的完整产品实现。

## 实际验证

- 59 个 FR 的编号、标题、优先级与 PRD V0.6 逐项一致；57 个含 P0，纯 P1 两项，FR-005 的混合边界保留。
- 附录 G：37 个命名用例与 G.4/G.6 的 13 条列表，共 50 条。每条原文都在 PRD 中存在。该结果证明清单覆盖，不证明已生成可运行 fixture 或产品通过。
- 12 个任务均有跨功能验收关系；核心接入依赖图无环。当前新任务为 `planned_not_dispatched`，未填真实 agent、worktree 或完成证据。
- 5 份本地需求/指南来源哈希匹配；独立审查另核对 4 个固定远端源码哈希匹配。原总控状态和远端 develop 的时间边界保留。
- 文档与 JSON 经本仓库现有 Prettier 格式检查通过。未改业务代码，未运行 Electron/原生测试，不以此次文档验证作为运行/生产证据。

## 独立 agent 复核

按用户 AGENTS.md 的复杂交付独立审查要求，由 `/root/release_scope_audit` 只读审查。

发现并实际修复、读回关闭：

1. 初版提取器把 G.5 当作与其他表同样列数，漏掉 A-01–10。改为按用例 ID 保留完整原表行；现共 50 条。
2. 初版 T00 依赖整项 I05/I06，造成无关工作等待。改为已批准 I03/I04 加共享文件逐项安全交接；语义/网关方法分别等待真实批准实现。
3. 初版任务前置表被描述为完整验收条件，实际跨功能自然语言、真实工具、B-08 和学习报告可能遗漏。改为核心接入前置、跨功能验收关系和阶段约束分别记录；模块完成仍以全部原验收与完整候选证据为准。
4. 交接明确验收覆盖表与可运行 G.0/E.5 基线不同，要求实际 fixture、重置、输入/预期哈希和验收命令位置。

最终复核结论：此前问题全部关闭，未发现计划文档新的阻断，可交执行总控接收。该结论不替代产品的 ZCode GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh 指定审查，不证明其他聊天已执行，不保证如期上线。
