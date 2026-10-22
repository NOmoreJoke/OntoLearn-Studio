# 本轮物理树与执行补充（优先于下附冻结历史提示中的路径、安装及一律不运行段）

任务仍为本组全部固定工程与全部原依据的独立完整审查。只允许选择本物理树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5`。它是detached HEAD，必须保持HEAD `4fa5d62eb13269351384527b1f84761c08811e79`；产品候选 `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。旧提示中的原owner工作树/分支仅为历史来源，不是当前执行目录，不切去原树，不切分支，不拼装其他分支。原固定完整工程/历史输入清单及manifest继续用原只读共享地址与ref逐件核身份；过程追加的纯文档不改变产品。当前AGENTS15147B/SHAde15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4已在本树传播，保持未暂存，不修产品/测试/锁/配置/验收。

## 唯一本任务路径

```json
{
  "env-cache": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/env-cache",
  "tmp": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/tmp",
  "scratch": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/scratch",
  "raw": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/raw",
  "reports": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/reports",
  "metadata": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/metadata",
  "workingTree": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5",
  "nodeModules": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/node_modules",
  "pythonVenv": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/.venv",
  "environmentShell": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/environment.sh",
  "fullReport": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/reports/source-selection-minimax-full-report.md",
  "actualTaskMetadata": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/review-session/metadata/task-actual.json",
  "ordinaryBuildOutput": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/apps/desktop/out",
  "engineBuildOutput": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/build/engine",
  "packageOutput": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/release",
  "playwrightOutput": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection-minimax-review-8c904b5/test-results"
}
```

开始运行前source本树environment.sh（不是执行bootstrap.py）；它设置本树独立npm/uv/Electron/builder/XDG缓存与TMP，UV_LINK_MODE=copy，清除ROOT_SOURCE_PATH、旧engine/package/fixture/HMR目标。仅本树实体node_modules/.venv可用，不能借其他树、把.venv指向外部、用共享mutable inode或复制同伴运行库；系统Node/npm/uv/Python只读基础工具可以共用，`.venv/bin/python`基础解释器符号链接须如实披露。Hatchling正常editable安装只指本树源码，是setup，不是产品运行通过。

setup由原T03唯一owner完成，模型不得重装依赖、更新锁、运行本包bootstrap或make-prompts脚本；若依赖缺失，报告精确setup缺口给owner。setup收据记录`npm ci --ignore-scripts`、`uv sync --frozen --python /Users/kyle/.local/bin/python3.12 --no-managed-python --link-mode copy`及独立Electron install.js安装结果；跳过的可选lifecycle不等于跨平台工具均ready。不能用安装exit0冒充check/e2e/package通过。当前这份预备包制作阶段不运行产品；后续真实审查任务可按下列正常回归权限执行，不继承旧“一律不新运行”限制。

## 正常回归权限及资源

静态完整审读后，若必要验证对应受审内容，可在本树记录精确argv/原因/时间/exit/stdout/stderr后运行原未改入口：`npm run check`、`npm run verify:sources`、`npm run test:e2e`、`npm run package:dir`。无需因旧提示重复向用户申请权限。没有变化不强制重测；不因普通C1/I04测试含native路径就泛禁它们。check含真实Vitest/Python进程、coordinator/worker/SQLite和build，不是纯静态；sources读取原source-manifest所列资料；e2e显式安装Electron后启动真实可见应用；package构建unsigned mac目录，尚不等于包内样例验收。各命令具体调用、输出与平台条件见只读完整静态审计`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-physical-setup-20261022/static-command-audit.md`，此审计是Codex setup依据，不是另一指定模型本轮意见。

GUI/C1真实恢复、焦点、现有固定5173端口和默认应用数据目录须由总控内部排互斥运行lease；当前包不证明任何lease，当前T01独占GUI以总控交接为准。仅worktree/TMP隔离不能证明初始Electron userData隔离，启动前明确实际应用数据使用范围与自有PID，不改冻结源码来绕过，不清理用户/其他任务进程。资源未交接时继续完整静态审读，准确记录待运行项，不向用户索要桌面时段。

C1 `csp-lifecycle.spec.ts`默认包含无平台/I02_NATIVE启用开关的runNativeRecovery，Mac也执行；保留其真实crash/hang与既有hook局限，不宣传为全部原生提示人工验收。I04 reload需本轮独立fixture；coordinator additionally Linux；I04 real-native需Linux且I04_NATIVE_ISOLATED=1及其原display/window前提。正常独立fixture准备`uv run --frozen python scripts/prepare-i04-fixture.py <本树scratch下新的唯一目录>`属于产品运行，只有正常运行阶段且对应资源条件满足才执行，输出fixture绝对路径赋I04_TEST_FIXTURE；不得拿Mac skip冒称Linux门通过。I02_HMR=1会改源，冻结期禁止；不改测试以跳过native或换stub/禁hang-monitor冒充验收。

普通package内回归使用本次本树包内engine：`uv run --frozen python scripts/verify-i04-package.py <本树release/mac-arm64/OntoLearn Studio.app/Contents/Resources/engine/ontolearn-engine> <本树scratch下新建输出目录>`，不得借旧包。mapping已有--mapping-probe、profile已有固定semantic-profile CLI及其外部oracle属于各自原验收，若确需重跑先列其冻结合同原argv和当阶段精确运行界限交owner核对；本补充不凭“正常回归”扩成任意参数、任意文件、SDK/原生身份读取或新资源研究。profile历史probe/oracle真实exit1、83=78成功/4资源拒绝/1缺规则未执行保持原样，不把计数相同当全通过。

## 严格保留的界限与完整交付

不运行未签T03-N0 native/producer/caller及其局部函数、runner/reader、ABI/loader/drain、witness/descriptor/index身份payload或被拒资源研究；不借票、不抬guard、不导入它们做fixture/dry-run。普通已有C1/I04回归与这些专票研究分清。只读完整工程源码/全部原设计、失败、验收/历史原件仍在范围内；历史资料按原固定ref读，SDK/受限身份载荷继续按原明确权限，不自行解码。Caller停止现场不读不写；必要身份以原已固定manifest说明未验边界。

只向上述本任务raw/scratch/reports/metadata及原命令自有忽略输出写入。完整意见报告写唯一fullReport，真实task/session/turn/实际模型思考权限与来源写actualTaskMetadata；尚未实际创建则留空，不能用目标模型名称伪填实际值。MiniMax Code要求M3.1-Flash/xhigh/bypassPermissions，创建/读回由原owner按总控短lease执行，不自建第二任务。不创建Goal/新聊天，不提交/推送/PR，不stageAGENTS。

禁止发现、搜索、读取另一指定模型本轮任务、意见、进度、状态库、报告、raw或metadata；也不通过共享Git新日志、app runtime/configDB窥探同伴。可读原固定完整历史原件及本补充明确列出的setup收据。只审自己本轮独立任务，不削减原范围。所有首次失败完整保留；全部原门逐项判定，静态/运行/包/父业务/两OS/生产分别报告。终态完整全文读回及全部意见处置由owner后续封存，setup独审不算指定模型Pass。

下附当前三份共同规则全文和冻结dispatch-v2提示原字节。发生冲突时本补充仅覆盖本物理目录、独立写面、setup、正常回归执行与资源调度；原工程范围/历史/严格安全/模型/完整报告/发布门不缩减。共同指南中“建立Goal”等新开发入口不适用于本既有审查任务，不新建Goal。


---

# 当前共同原件：developer-common-instructions.md

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

# 当前共同原件：desktop-operation-policy-20261022.md

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

# 当前共同原件：external-review-permissions.md

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

# Frozen dispatch-v2 full original (exact bytes below)

# 不可变共享包入口（前向F1修复）

工程仍只读提示正文指定的本组工作树；完整发审包跨树只读，不复制、不拼装其它分支源码。共享包绝对根：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022`。包固定Git ref：`ed9cef968b17a1edefc0977b509906fb9f81a336`，其Git仓库读取位置为`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping`。原candidate-manifest绝对路径`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022/candidate-manifest.json`，固定Git地址`ed9cef968b17a1edefc0977b509906fb9f81a336:docs/reviews/T03/designated-review-backlog-20261022/candidate-manifest.json`，4301B，SHA256 `60c52bd13dac43bb9685b5233db817118dda10341357794d9f27500f07301e6c`。

本组完整输入绝对路径`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-mapping/docs/reviews/T03/designated-review-backlog-20261022/source-selection-fixed-inputs.json`，固定Git地址`ed9cef968b17a1edefc0977b509906fb9f81a336:docs/reviews/T03/designated-review-backlog-20261022/source-selection-fixed-inputs.json`，215883B，SHA256 `4a83eb9e2319b92299f3cd79967b15d5afe5f461cc30b2e657235ddcc873f0b4`。历史矩阵与覆盖关系为共享根下`historical-stage-inventory.md`、`coverage-matrix.json`、`coverage-summary.md`，均从上述同一fixed ref读取并逐件对原manifest核身份。可通过指定mapping仓库的只读Git show读取该ref:path；不能在本组工程猜相对路径、搜索一个未固定版本，或切分支。

下文旧“本包”均指上述**外部只读共享包**。当前新提示属于dispatch-v2前向定位修复，旧19原件及Fail报告保留，不用新提示覆盖旧candidate-manifest。实际任务ID、设置、终态及lease仍未发生。native当前仍禁止派发；三组现有工程可按真实短lease创建。操作政策在总控根目录使用最新原件；当前3160B/SHA2032bd9e1cdbf398a0d505e092e1a08b80ff15df26b1d06c7d7e1c2e0a5a8ec1说明T06已释放前台、仅创建/设置/读回短lease、后台推理不独占整个应用；不向用户索要桌面时段，不扩大native/static执行边界。

---

# T03 source-selection 完整独立审查提示：minimax

这是待实际创建的任务输入，实际task ID/逐任务设置/lease/终态均未发生。要求设置 **M3.1-Flash / xhigh / permissionMode=bypassPermissions**，必须从真实任务读回。只读审查，不修改实现/测试/依赖/配置/验收，不安装、提交、推送或创建PR。与另一模型独立，不传递本轮意见。

精确工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T03-source-selection`；分支 `feature/weekly-t03-source-selection`。批准base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；产品/验收候选 `8c904b57b7c5aac7b2b19273e679e7e36304dd1c`；完整证据固定ref `4fa5d62eb13269351384527b1f84761c08811e79`。本包 `source-selection-fixed-inputs.json` 列出完整工程全部tracked路径及blob身份、base delta，不只修复delta。必须审完整源码、工具、tests、fixtures、配置、依赖锁和全部原验收/失败/缺证。工具位于docs或扩展名.py.raw/.input.py.txt也不能漏。metadata清单不是作者已全文读所有载荷的声明。

从固定Git原件读取。过程ref全部非docs工程字节已逐blob等于产品；process中后来追加或修改的证据工具另列laterEvidenceHelperDifferences，亦须按本次完整process审查，不能因位于docs漏审。后续本包纯流程commit不改变产品。若实际工程/测试/配置/依赖/验收或base变化，报告归属差异，不沿用旧Pass。禁止切分支、checkout/reset/fetch/cherry-pick或把不同树互斥共享文件拼成一个运行候选。

完整原依据包括本树PRD `docs/prd/PRD-本体学习与落地Agent工作台.md` 的全部FR-300–304、附录C–G（D/G.1 M-01–06）及§10–12；M0架构S1/S2/S3/C1/B1/U1及当前实际AGENTS；父I05/native相关完整原合同/57P0继续保留。每个局部、父业务、平台与发布门分别判断，不能排除未验部分后给整体Pass。历史阶段和后继见本包historical-stage-inventory.md、精确覆盖见coverage-matrix.json。首读入口（不是范围排除清单）：

- `docs/reviews/T03/source-selection/status.md`
- `docs/reviews/T03/source-selection/validation.json`
- `docs/reviews/T03/source-selection/internal-review-inspection.md`
- `docs/iterations/T03/source-selection/design-and-handoff.md`

现有证据：32专项、完整check 662 TS/1052 Python/0 skip，exit0。真实有界FS与注入picker不等于原生picker/合法XLSX解析/正式IPC、Job、Store；无新包/两OS/原生e2e。

当前完整共同指南/操作政策/权限及第九节在 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release` 的developer-common-instructions.md、desktop-operation-policy-20261022.md、external-review-permissions.md，须全文读。当前AGENTS为15147B/de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4受保护未暂存。用户已撤回静默桌面要求；旧待用户桌面时段/先CLI登录不是现行阻点。实际CUA短lease由总控内部交接，提示存在不证明lease。

本轮先审完整固定工程与既存运行原件，不新运行产品或验证命令；没有变更不强制重测。若完整判断确需新运行，报告精确命令/原因/所缺执行权，由原owner按实际阶段权限处理。尤其旧HOLD/自动拒绝/native未签票、caller及其局部函数、runner/reader、dry-run/fixture/模拟、编译/ABI/loader/drain不得由模型代跑。完整仓库源码和工具源码在本次静态审查范围；未获当前读取授权的SDK、工具安装/二进制身份载荷、原witness/descriptor/index身份payload及归档载荷不重读/解码，按原fixed manifest逐项明确未验证，不能谎称已全文审读。父runtime缺证不永久排除其余已有源码审查；需要该缺证才能判定的门明确不通过或无法验证。既有票不借/退/自提高guard，不读密钥，不新增付费或模型API。

首失败、历史HOLD、全部报告原件保留。内审不算指定Pass；源码、运行、打包、目标平台、生产/父业务分别给结论。未实测性能不量化，不能只看最后success、数量或作者摘要。完整报告含真实应用task/session/turn及实际设置、工作树/分支/base/product/process、全文读取覆盖、实际命令和结果或未运行原因、全部意见严重度/文件行/触发/影响/证据/建议、历史逐项处置、全部原验收矩阵、未验边界及明确通过/不通过/无法完成验证。真实终态后必须全文读回，不能只报阶段摘要，不能强行把任何模型不通过改为通过。

报告建议路径为本树 `docs/reviews/T03/designated-backlog/source-selection/round-1/minimax-m31flash.md`，须原owner实际调度确认唯一报告写面；尚未确认时返回完整原文供owner封存，不擅写别处。实际模型设置和task ID留给真实派发收据，不在本提示伪填。

本阶段状态：PREPARED_NO_ACTUAL_TASK。可在短lease交接后创建新独立完整任务，不因父runtime缺证无限等待。
