# T02 S1 同版完整独立审查 — 2026-10-22 实际桌面执行补充

本补充优先于下方冻结原文中的旧工作目录、输出目录和操作排程限制。原审查对象与全部验收保持，原文完整附后。

你的唯一审查工作目录：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-zcode-review-4932122`。HEAD固定 `ce1c3df41a233a07de4ef8fad54d5f201b222a23`，产品候选 `49321221733ea927484647352e05e7d833cebc86`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。不得 checkout/commit/stage/push，不得写产品/测试/fixture/锁/配置/验收。原文所有 T02-ontology 工作区相对路径，映射至本目录相同相对路径；不使用原owner运行环境，不访问另一审者会话或意见。

唯一正式报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-zcode-review-4932122/docs/reviews/T02/round-1/zcode-glm53.md`；你的原始stdout/stderr、首失败、exit code、临时复现和依赖准备流仅放 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-zcode-review-4932122/test-results/t02-s1-r1/`（tmp/streams等）。可在本树基于既有锁独立建立 node_modules/.venv、执行必要审查复现/边界/性能反例/完整check；不必再逐命令请求root批准。保留完整原始流及前后候选哈希；不修改锁/既有测试来掩盖失败。实现只读，发现问题完整列出原路径行号、触发/影响/严重度/建议/验证。验收不足、环境缺失或旧失败均如实报告，不能把未执行算通过。

直接human已撤销旧静默桌面要求并要求补齐指定双审。当前AGENTS已经阶段owner传播，本树AGENTS为当前政策（不提交）。完整阅读 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-zcode-review-4932122/docs/reviews/T02/round-1/launch-20261022` 中当前政策及执行补充；总控实际创建窗口说明优先于历史“无租约/T06独占/仅后台/不许GUI”的旧排程描述。当前前台仅用于本owner创建和设置两个独立任务，之后释放；需要后续可视化时协调本owner。不得触碰T06既有任务/session/stdio，不另启共享dataDir runtime，不改系统凭据/付费/其他项目，不运行已拒绝SQLite物理实验。

完整范围以input-manifest为准：19产品/测试/fixture、5验证harness以及全部58原始delta文件/过程证据/后续纯方案，不能截为UI或提示审查。原阶段语义不扩张：S1内部模型/手工编辑/源绑定为当前候选，父功能、实际Store写入/bridge等仍有明确缺口。旧C1/C2内部结论与历史失败仅作事实，不能替代你对当前同版完整审查。报告只写你自己的独立结论，中文，真实终态，所有P级问题都列出。

以下冻结原文UTF-8字节原样保留，SHA256 58a62654038514f80528b147e73631acb70ddeaaa7a607f920dfccc76f761f35：

<!-- BEGIN COMPLETE ORIGINAL PROMPT -->
# ZCode GLM-5.3 全范围独立审查冻结提示

准备日期：2026-10-22（Asia/Shanghai）。仅准备，尚无真实任务或lease，不得据此启动。

本方指定设置：GLM-5.3；最高思考等级 max；permission.mode=yolo。实际provider/model须从支持入口registry读取并逐任务核同；不可换用旧模型或仅凭默认配置。

本方唯一报告绝对路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology/docs/reviews/T02/round-1/zcode-glm53.md`。不得读取/写入另一方本轮报告。后续隔离映射若改变输出位置，须总控独立附录固定实际绝对路径和hash，不改本原提示。

你是本轮全新、独立的指定审查者。必须完整审查同一个T02-S1候选及其全部证据，不能把UI、C3来源绑定或后续方案单独当整轮范围。此提示只是冻结输入；实际执行仅在总控授予独占后台lease、创建真实任务并逐任务读回设置后生效。任务ID/模型显示/报告文件均不得预填或伪造。

## 精确身份与只读输入

- base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- product head：`49321221733ea927484647352e05e7d833cebc86`；C2历史`5ef86a1da88d86f2de7b55a7e3be38b1e0f986b4`；C1历史`438c6ade34795cb3b0111f0bca463d4fd091b393`。
- 冻结输入过程head：`d597b3c00980652042163d250c875d660d4d371e`。之后仅本round-1追加提示/索引/报告等过程证据，不改变产品。报告同时记录实际review工作树HEAD，不能拿新增过程commit假称产品变化。
- 原工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-ontology`；分支`feature/weekly-t02-ontology`。不得切分支、reset/clean/stash、提交、stage或修改任何原输入。
- 完整输入清单：`docs/reviews/T02/round-1/input-manifest.json`；逐path/ref/bytes/SHA核对，基线/产品diff与所有tracked流程docs均在范围。另读`scope-and-evidence.md`、`history-disposition-index.md`与`original-log-index.json`。
- AGENTS未暂存、SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，两个原PNG未跟踪，保持原字节。不能自动修复、暂存或清理这些保护项。现存截图原字节也在Git证据封存内。
- 如总控另给隔离review工作树，必须附独立冻结workspace/output mapping，逐项验证同base/product/全部输入hash，原提示保留；不得猜路径、借其它模块环境或自行建树。无映射时按原绝对路径只读，无法满足则准确报告不可验证。

## 完整S1实现与验收范围

原FR-200–204/附录C/F/G/12.1/12.4与父功能不缩减；这次独立外审对象是总控登记的完整有界T02-S1私有服务/独立页面阶段。请读原PRD对应条款、FR-804、相关附录和`docs/iterations/T02/acceptance.md`、`source-projection.md`、`stage-registration-request.md`、`interface-handoff.md`、`delivery.md`。历史文档含旧active/旧owner/旧预约句子，不覆盖最新真实Goal blocked/生效责任；以本提示及当前操作政策、固定source身份与实际证据分开判断。

1. 私有实体/事实模型：类、对象/数据属性、个体、层级/type/domain/range，中文/多语言/多行名称定义、英文标识、synonyms/examples；IRI为身份，不按显示identifier错误合并。完整增删RDF、metadata-only before/after、复制与删除影响；结构定义不伪造实例或必填关系；种类/字面量/引用/不可表示输入明确拒绝；旧project/revision/同版本内容守卫。
2. 批准Store2只读来源绑定：完整RDF集合相等，全部原factID、owner/source_row/managed_value、人工覆盖、墓碑、同RDF多重支持、definition payload hash/原triples下标与显式引用。读取不改库/输入；sourcehash不是metadata授权、当前源选择、人类确认或删除计划，不能用removed_sources直接删mapped/多支持。
3. 独立React页面及纯view-model：表格、循环/多父类树、一跳SVG图/完整列表及截断、完整语言/多行意图、Diff/删除影响、草稿独立版本、异项目/late/错误状态；无Node/通用IPC/模型外发/自动确认。五文件UI harness同样完整审查其真实探针覆盖与合成callback边界。
4. 全部专属Python/TS测试、完整fixed G-base/Turtle正反fixtures及输入来源。T09固定873只读manifest/G-base使用，不采用服务或expected冒充运行。核全部具体RDF/对象/来源，不只计数。Turtle corpus存在、RDFLib基础项可读不等于安全导入/完整模板/往返。
5. 证据与历史：C1不通过、C2/C3修复与内审、原失败日志、完整check、UI证据/归档与真实读回、任何未知或缺失记录均完整审查。不得把内部审查当指定模型通过，也不能仅看该模型名或已有报告标题直接通过。

19个产品/测试/fixture路径必须全覆盖：

- `apps/desktop/src/renderer/src/ontology/OntologyPage.tsx`
- `apps/desktop/src/renderer/src/ontology/ontology.css`
- `apps/desktop/src/renderer/src/ontology/view-model.ts`
- `packages/engine/src/ontolearn_engine/ontology/__init__.py`
- `packages/engine/src/ontolearn_engine/ontology/model.py`
- `packages/engine/src/ontolearn_engine/ontology/service.py`
- `packages/engine/src/ontolearn_engine/ontology/source_projection.py`
- `packages/engine/tests/test_ontology_editor.py`
- `packages/engine/tests/test_ontology_fixed_inputs.py`
- `packages/engine/tests/test_ontology_source_projection.py`
- `tests/fixtures/ontology/invalid-turtle.ttl`
- `tests/fixtures/ontology/manifest.json`
- `tests/fixtures/ontology/manual-supported.ttl`
- `tests/fixtures/ontology/supported-shacl-template.ttl`
- `tests/fixtures/ontology/t09-fixed-inputs/G-base.json`
- `tests/fixtures/ontology/t09-fixed-inputs/manifest.json`
- `tests/fixtures/ontology/unsupported-owl.ttl`
- `tests/fixtures/ontology/unsupported-shacl-path.ttl`
- `tests/unit/t02-ontology-views.test.ts`

另完整阅读`docs/iterations/T02/ui-probe/`的build/check/fixture/harness/index五文件及清单中全部S1证据。`typed-changeset-integration-plan*`后续十docs是onlydocs准备，不是本轮S1产品实现，不导入T01未获准runtime；其中内审P2已在方案层关闭，不能冒充实际commit/metadata/meter已实现。

## 原有验证与未验边界

- C3 `verification-c3.json`：原完整`npm run check` exit0，633 TS/1091 Python，其中39本线Python；新source_projection专项13条exit0。C3固定后无产品/测试/依赖/配置/验收变化。
- C2 `verification-c2.json`：原check633TS/1078Py、26本线Python/3TS；11项实际headless组件探针，合成callback，无Store/IPC/产品/e2e。C3页面/脚本原字节未变，沿用有据，不误称C3再跑。
- 原`verification.json`为C1历史；sources-first原12归档源exit0，未改source资料，不能混计C2/C3最新结果。C1/C2首失败均保留。
- 原32索引日志全部在`original-log-index.json`，Git内归档共41日志+2当前截图+4索引+内嵌manifest，48成员，548417B，SHA `43d9e20533885828a03c34392e8ae42ada23663c1cc338986c795c236f2a6b86`。读原`evidence-archive/manifest.json/readback.json/git-readback.json`与独审；如需解码只在内存或另外授权的私有临时位置安全读取，不覆盖原文件。旧C1两图已被覆盖，只有原hash，不能补造或拿C2图替原图。
- 本轮无依赖/锁/build改动，无新增必要package探针；从未执行Electron/e2e/native/HMR/包内/目标双平台安装生产验证，不得补记为通过。
- 完整父缺口：T01可信当前domain与metadata/来源/引用投影、正式canonical/named桥/session/scope、人类确认、唯一原子commit/receipt/undo；I05批准Turtle/SHACL列表与全部支持检查/无损往返；I06正式App/桥和壳生命周期；T08真实草稿与模型；FR200–204完整跨模块、两目标平台/真人、指定双审/CI/正常合并/远端/上线均仍待。S1结论不能关闭上述门。

## 审查执行纪律

- 实现、测试、fixture、依赖、配置、验收、原日志与本轮另一方提示/报告均只读；不调用或读取另一方本轮输出，不交换意见。两方都必须新建完整独立真实任务，不能复用已有会话/答案，不能以Codex内审替代指定模型。
- 当前只读源、Git/hash与原证据是默认方式。无变化不重复全仓测试/旧UI探针、不npm/uv安装或下载、不改锁。若新的必要独立复现不可替代，先在报告列明精确命令/隔离与未验原因，由总控另授；不得自行执行产品/测试、修改测试或自动修复。
- 唯一持久写权限是本提示指定的本方最终报告。无GUI/Electron/e2e/native/HMR、产品启动/聚焦/浏览器界面操作，无监听HTTP端口、Keychain/凭据提示；不新增模型API/付费/订阅，不读取输出密钥、不重置额度或私写任务数据库。后台路线须由lease owner使用实际支持官方入口，启动协议进程/草稿不算真实审查。
- 不创建Goal/用户线程、跨聊天发任务，不commit/stage/push/PR/merge/强推或动root控制记录。真实认证/额度/服务错误记录具体官方原因与恢复条件，保候选，不泛称无桌面或自行换模型。
- 启动前和终态后核全部冻结source/输入hash，任何产品/测试/依赖/配置/验收或base变化立即标明本任务失效/待新候选，不继承Pass；纯追加本轮过程证据须说明对应关系，不误称源码变化。

## 必须交回的完整报告

报告必须含：实际平台/真实taskID/创建及正文接收时间/最终任务状态，指定provider/model与版本、思考等级和权限的逐任务实际读回来源；原/实际工作树绝对路径、branch、base/product/input-process/实际HEAD及prompt/manifest hash；逐19产品路径+5harness和必要依赖/全证据覆盖；实际执行的只读命令/结果/exit与沿用原运行证据分列，未执行不能写通过；各历史意见逐项依据；每个新发现按P0–P3给准确固定文件行/触发/影响/证据/建议；无问题也明确覆盖与未验边界。

最终必须对完整S1给明确“通过／不通过／无法验证”之一及理由，不能只条件Pass、部分UI通过、阶段拼接或空模板。只在实际任务真实终态后交付完整全文报告；由本线/root全文读回处理所有意见，同候选双方明确通过且其余门满足才可能push/PR/CI/正常merge。无权自行批准父功能或发布。来源/设置证据缺失时写无法验证，不伪造。

## 随任务附带的完整共同操作指令

以下是固定17891B共同指令原文，其中历史初始owner/旧AGENTS SHA须按上面的实际78df与后续生效通知理解；操作政策及完整第九节/无桌面/逐任务默认权限完整保留。后台创建route补充以`T06-supported-background-external-review-window.md`和`external-review-permissions.md`最新后台条款为准，本提示冻结准备时没有本线lease，只有准备文件许可；实际启动必须另附总控有效独占lease与逐任务设置回执。

# 完整首版功能开发共同指令

用户已在规划聊天 `01a15bad-ceeb-7103-b611-fff95e1f31ee` 明确要求 OntoLearn-Studio 全部原定首版功能于北京时间2026-10-25前开发上线、质量不降，并授权“发送并落实到现有总控”。总控实际读取原始用户消息确认了授权。本指令用于新功能开发聊天；截止日是目标，不是保质按期保证。

先读取本目录 controller-handoff.md、plan.md、tasks.json 中自己的任务、requirements.csv、acceptance-baselines.csv、review.md，以及实际工作树最新版AGENTS和对应PRD原条款/附录。57项P0、附录C–G及第10–12节保留；P1/P2原延期安排不变。T编号不覆盖I01–I06历史；纯服务完成不等于父模块P0完成，integration_prerequisites不是全部验收条件。

本会话只负责指定的一项功能，建立自己的Goal（不存在时），不继承总控Goal。先核验并回执绝对worktree、分支、base、实际git状态、指南SHA、唯一文件责任、验收与下一交付。总控已创建独立worktree，切勿改主checkout或其他树；AGENTS是总控复制的受保护操作规则，SHA应为 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`，保持未暂存，不混入产品提交。不得重建原I05/I06 Goal或继续写其树。

当前批准develop为 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。I01–I04已合并；I05 C1在指定双审冻结，已发现词法语义阻断，I06在自己的14文件接线与隔离平台联验。不得采用未批准I05/I06实现、环境或测试结果为正式依赖。只读取已批准基线接口开展独立工作，具体接口缺口/共享改动向总控提供精确路径和依据。

初始共享责任（历史，已被下述逐项生效交接更新）：I06原独占 contracts/src/{index.ts,v2.ts}、contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json，desktop/main/{index.ts,task-service.ts,engine.ts}、preload/index.ts、renderer/src/{env.d.ts,App.tsx,style.css}；I05原保留其他Python Store/coordinator/worker/protocol、语义/resources、entrypoint/build/锁/CI/窗口安全恢复。这些逻辑文件在任何树中均不得抢写。新增私有路径可按本任务授权实施；现有共享文件、迁移和依赖锁一律先做具体交接。不得复制第二套公共契约、SQLite可变权威或Store写入通道来绕过交接。子任务独立worktree/feature和文件责任，复杂交付独立agent审查；核验真实并发槽，不将创建目录当作已启动agent。

后续责任变更补充：I05/T01双方实际接受、独立复核及总控登记后，只有 `packages/engine/src/ontolearn_engine/storage.py` 后续维护已交T01生效，详见 I05-T01-storage-ownership-handoff.md 和 execution-state.json。I05冻结树保持原字节，其余共享/14文件不变。不得将这个单文件交接扩张为其他文件授权；当前具体责任以总控实际生效记录为准。

2026-10-21新增已生效交接：T01除原storage.py外，已唯一接管Python四个 `packages/engine/src/ontolearn_engine/{job_store.py,coordinator.py,__main__.py}`、`packages/contracts/python/contract_v2.py`，及原I06 canonical七个 `packages/contracts/src/{index.ts,v2.ts}`、`packages/contracts/v2/{schema,registry,errors,fixtures,binding-regressions}.json` 和 `apps/desktop/src/main/engine.ts`，仅从批准5f独立实施格式基础。T03已唯一接管 `packages/engine/pyproject.toml`、`uv.lock`、`scripts/build-engine.mjs`、`packages/engine/entrypoint.py`，仅做XLSX最小依赖/收集/受限probe。原I05/I06树原字节保留，可读/构建但不得继续维护已交逻辑文件；必要修复先精确返还。I06仍维护其余六个main/index、task-service、preload/index、env.d.ts、App.tsx、style.css，I05仍维护其他未交路径；既有测试、CI、resources等不自动扩权。三份新handoff协议及独立报告/实际接受/生效通知见本目录 I05-T01-format3-ownership-handoff.md、I06-T01-format3-ownership-handoff.md、I05-T03-build-ownership-handoff.md 和execution-state.json；这不是未批准代码采用、公共格式启用或运行通过。

本机只允许无窗口静态、单测、Python、构建、unsigned目录打包；不得运行Electron/e2e/native/HMR、自动产物启动、抢焦点或凭据提示。原生可见/焦点/真实崩溃与无响应/实际安全存储在各自隔离Linux Docker/Xvfb/Openbox或远程CI准备；不关闭sandbox/hang monitor，不用隐藏窗口或stub原生提示冒充通过。Windows/macOS首发证据仍需实测；Linux不替代。ZCode/MiniMax审查应用当前资源预约属于I05，新线须先向总控预约，不自行抢用。CUA对Codex app已明确拒绝，禁止绕过。

开发至完整可审查结果，必要异常路径/事务/撤销/历史隔离均保留。AGENTS所需 check/sources/e2e/package 按实际改动执行，隔离项真实待验，首跑失败原件保留。文档/纯模块/静态检查不能冒充正式接线或生产。没有变化不重复测试。依赖资源缺失只阻塞相关部分，先完成独立工作，不擅自结束或暂停整个Goal。

最终完整验收前刷新实际批准依赖及develop、集成冲突并验证；冻结真实base/head。由同一开发聊天通过CUA在ZCode选择本精确工作树、GLM-5.3/最高，MiniMax Code选择本精确工作树、M3.1-Flash/xhigh；每轮双方各新建独立只读完整范围任务，不互传本轮意见。报告按 docs/reviews/Txx/round-N/{zcode-glm53,minimax-m31flash}.md，逐项含任务来源/模型设置/路径分支/base/head/检查命令结果/未验边界/问题严重度位置触发影响证据建议/历史逐项关闭/明确通过或不通过或无法验证。两个任务必须实际终态，全文读回、全部意见处置；不能自己把指定模型不通过改成通过。所有实现/测试/配置/依赖/验收或基线变化后重新验证并双方全新完整审查。纯追加流程证据记录对应关系，不自动触发无变化重审。

同版双方明确通过、验收和必要验证通过、全部意见有处置、实际推送内容与受审实现一致后才push/PR；实际CI通过后正常合并develop、核验远端与保护源。必须attach创建PR；无强推、绕过分支保护或双审前push。集成/外审按总控预约，减少前方候选基线失效。纯服务可单独冻结合并，但原父任务P0跨模块验收与完整发布门不关闭。

额度：效率和完整交付优先，不因token删减；真实告警由账号唯一负责人核实。Codex重置每次需本人明确确认/阈值/幂等，不能UI绕过；不新增付费、订阅、API消费或扩张授权。只读服务/身份元数据不含读取或输出密钥。真人非开发用户验收不能agent替代，向外招募/消息仍需用户明确授权。

各线只维护自己的 docs/reviews/Txx/status.md 及证据，不写根 state.json、tasks.json 或其他总控文件。及时保留可恢复SHA/原件和准确下一步；实际独立实现与验收证据成熟后向总控给出可读交付，不用反复询问常规实施许可。不能将配置/脚本存在、目录/模型名称或数量相同当作验收。完成后父模块/远端/上线分别据实记录。


## 原第九节及无桌面打扰约束全文

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


2026-10-21单文件补充生效：在既有T01十二共享及storage责任之外，`packages/engine/src/ontolearn_engine/worker.py`未来维护唯一交T01；只从批准5f的9314B/2fa848aa…06f2f0施工，不复制消费I05未批准C3的13638B/3d934e79…4f99d语义worker。原I05 C3受审字节继续冻结；若审查需修先由root精确返还、T01停写保存SHA/差异，执行输入变重新验证/双新审。protocol/resources/语义模块/旧tests/build/CI等不随此转，其他owners不变；source wire/限额/格式3/ready并未获批。原offer/接收/独立复核与唯一责任/返还门见本目录I05-T01-worker-ownership-handoff.md及execution-state.json。此补充不改变前文完整第九节/无桌面规则。


## 四文件基础层未来维护交接生效（2026-10-21T11:40:05.102755+08:00）

I05原owner分别释放并由T01逐项明确接收 apps/desktop/src/main/jsonl.ts、apps/desktop/src/renderer/src/task-presentation.ts；I06原owner仅释放并由T01逐项明确接收 apps/desktop/src/main/task-service.ts、apps/desktop/src/main/index.ts。独立复核eeb221ea…0562、原接收01fa5ce5…2731/2124ef6c…3fae均由总控全文读回，四接收路径实际clean且逐字等批准develop5f；生效登记见 foundation-four-file-handoff-effective.json，原协议bad9716a…2965及全部原件保全。自此四路径唯一未来维护者T01，原I05/I06停止所有checkout未来逻辑编辑，固定C4/e2c/961只读审查/构建保留。T01仅沿自己批准5f，不复制未批gateway/语义实现；I06保留preload/index.ts、renderer/src/env.d.ts、App.tsx、style.css及私有模块。其余协议/resources/旧tests/依赖/build/CI/语义路径不转移。

此项仅维护责任生效；当前纯表材料阶段授权不变，startup/schema/新码/runtime3/ready仍须总控精确阶段授权。返还任一路径须root精确路径/原因/基线/窗口/验证、T01先停写并保全HEAD/文件SHA/WIP diff/测试状态，再明确唯一接手者和生效点；旧owner不得自动回收。受审执行输入变化仍新候选/必要验证/指定双方全新完整审查，不继承旧Pass。原第九节、无桌面干扰、安全应用入口/实际租约、指定双审及push/PR/CI/正常合并门全部保留；历史文字不覆盖本新生效责任。

<!-- END COMPLETE ORIGINAL PROMPT -->
