# T01 下一阶段：可信项目宿主与 ChangeSet 接线方案

状态：依总控本轮精确指令新增的 **docs-only 待审方案**。产品固定 `5de3fff8aa02c5d6e577938660e9362936d90550`，批准集成基线仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；未取得下一实现、共享文件接线或默认生产3启用授权。仅新增本文件及 `docs/reviews/T01/project-host-integration-next-plan/`，不修改5de产品、旧报告、双模型同候选输入、测试或总控状态。

目标是接通真实用户选择项目、完整 Diff 和一次明确接受，继续完成原44项地图/FR-001–006/804。此方案不把fixture、renderer UUID、hostClientId、hash或页cursor当作人类授权；也不把服务阶段的typed子集改成父功能验收范围。

## 1. 固定证据与实际缺口

[输入清单](../../reviews/T01/project-host-integration-next-plan/inputs.json) 从固定Git逐字读取：14份5de源码/PRD/地图、5份5f对照和5份I06合同，共24项；5de与660合同另核现场同字节。下列3份I06合同固定 `660da44aa7ad1b3ba7dbfb3a90fef37e25763ec8`，只读参考而非采用其未批准网关代码：

- `main-integration-handoff.md`，10812B/SHA `3deb9558dd2d1ab13b7da680c9591259ab7a46c97a8fee2aad5c10896af61035`。
- `format3-consumer-integration-request.md`，24058B/SHA `1e55e54bd9f93d2ff8f8aef0c95b6f28495a1c0eb6ebb9f85802123056adac26`，全文读；尤其§3–6的同UUID生命周期、固定engine引用、C1–C6及消费路径。
- `source-selection-lifecycle-interface.md`，23391B/SHA `2495c4b371b6bf02519b62d1e3465422795703b4aaa110d2ac3f1dff52264a16`，本轮定点读§2/4/5；source scope、Job确认、模型grant分离，以及写帧前guard/真实未settled计数合同可复用其边界。它不是现成的项目数据库文件I/O能力。

另全文读固定 `b1283bce1daf7198fc6b0b62f8b0a6bbffa5a874` 的 `T01-owner-response-alignment-r1.md`（9168B/SHA `64f16ecce5164cc9bc6272add415b121a15c201f25805dc8cb2593eae74cb6c1`）及固定 `961ce77f26accd11bd1cd3ad4a9e560cd3565e37` 的 `transfer-guard-core-v1.md`（11155B/SHA `ad67e4e1837a6f630c3f5980f2add3e3bb8e9444a60071bb6c6e7e05e2b18879`）。前者明确真实metadata owner/受控I/O仍缺；后者仅metadata/token，contentIo恒unsupported，无真实FS lease或external atomic fence。不得把该实现的metadata-eligible兑换成本项目打开/创建能力，也不读取或采用其产品代码。

这些合同中的历史14/6文件ownership文字不能覆盖最新生效交接：T01已持 main/index、task-service、engine及canonical；I06仍持preload/index、renderer App/env/style和其私有网关。改哪条路径仍须根逐条登记窗口，不据文档推断新写权。

| 实际代码证据                                                       | 当前行为                                                                                                                                   | 下一阶段不能跳过的缺口                                                                                           |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `main/index.ts:91–139`                                             | 仅 I04 main launch fixture 提供 databasePath/projectId、allowedProjects，并调用selectProject；正常启动固定userData/engine.sqlite且未选项目 | 真实位置选择、项目目录/新建/打开、许可和可信选择来源均未接；不能把fixture去掉test字样转产品                      |
| `main/engine.ts:146–163,208–213`、`coordinator.py:160–164,846–852` | Supervisor复制构造期scope，normal allowedProjects=[]；Coordinator严格拒未许可项目                                                          | TaskService.selectProject本地绑定不授引擎权限；发现/创建UUID之后仍需真实库级许可到项目scope的窄合同              |
| `JobStore.create_project/public_project/_project:489–517`          | 一库多项目；域/app genesis+公开映射同事务；公开映射可写，UUID持久；无正式create幂等receipt                                                 | 不能假定“一个项目一个文件”、inventory时补映射或把随机UUID/INSERT当创建授权；新建须独立冻结完整请求/claim/receipt |
| `Store.__init__:80–94`、`serve:837–845`                            | 构造会创建库、迁移；serve还先mkdir；显式3有真实lease/备份/校验                                                                             | open-existing必须不创建、不mkdir、不静默迁移或降级；现dataPath/isAbsolute不证明路径授权或别名锁正确              |
| `DesktopBridge:157–169`、preload、App                              | 只有health和只读任务/结果桥；没有项目生命周期或ChangeSet专名桥；App明确编辑/自动保存未接                                                   | 新增确认按钮仍无真实项目/编辑/接受来源；不能借generic invoke或renderer自报refs填洞                               |
| `EngineSupervisor.request/#send:640–714`                           | await ensure后只核transport current Session，直接stdin.write                                                                               | 仅调用前/响应后检查TaskService generation不能阻止await期间失效的旧写帧；需真实发送前同步main-only guard          |
| `TaskService.restoreOnce/remembered`                               | remembered来自已有Job或subscribe；operation.get是nullable marker                                                                           | job.create受理但响应丢失时可能既无已知jobId又无marker；null不是无claim，恢复不能只遍历remembered或自动重放写请求 |

两位只读agent独立核到项目权限源、实际发送切点和未知claim发现缺口；未运行产品/测试/GUI。这些是下一合同的前置，而非5de已宣称具备的人类UI能力回退。

## 2. 推荐顺序与完整四入口

### H1：真实位置和项目目录，先解决许可来源

保留真实一库多项目模型，建议让用户选择/新建一个**库文件位置**，在库内目录选择项目。项目条目显示名称和所处位置；创建时可选已有库位置或新的库位置。不发明“一项目一文件”迁移或项目包格式。FR-002的逐项目复制、导出/导入、默认归档/删除确认另按原地图/T10接通；目录不是导出包。

建议冻结三个主进程行为，而非让renderer传路径：

1. `chooseProjectLocation()`：可信mainFrame明确用户动作后，main原生打开/保存位置选择器产生私有位置记录；renderer只收opaque location ticket、允许显示的位置摘要及catalog状态。取消候选位置选择不改原项目/文件，不沿用一次已撤销的预览。位置ticket不成为模型外发许可。
2. `listProjects({locationTicket,pageSize,cursor})`：main查私有位置记录；engine在该真实库级窄许可内只读枚举public_projects JOIN projects/app_projects，返回一致的有限目录页。缺公开映射或格式证据则拒绝，不调用public_project补写；同名项目以实际身份区分，不按名称猜UUID。renderer的目录行只有main签发selection ticket，回传UUID本身不能选入他库。
3. `createProject({locationTicket,name,templateSelection})` / `openProject({selectionTicket})`：main持有原位置/目录绑定；engine创建/解析真实公开UUID，main才安装该项目的有限scope并调用TaskService.selectProject。新建名称是受限内容，不是授权。模板必须指向T09批准且完整的真实内容与初始化合同；无实际模板不能用空库标示示例成功。

**必须先由根确认的合同实件**：位置模型与允许的本地文件形态；库级catalog/create权限的可信启动来源；公开UUID由engine解析/分配后如何形成单项目scope；完整create请求及持久幂等/receipt命名空间。建议库级权限仅属于实际main启动配置/服务对象，不通过renderer boolean、RPC自报permission或可任意复用的字符串授予；catalog与当前项目写scope分开，Agent不可调用picker/catalog create或选scope。不能为解开空allowset而让所有无projectId方法默认获库权限。

建议新内部3命名方法为 `project.catalog.page`、`project.create`、`project.select`、`project.workspace.read`，均是**待统一canonical的设计名**，不是现有API。catalog/create/select必须另有库级host gate；workspace.read仍要求当前项目许可。有限响应至少区分：

- 目录：冻结catalog身份/分页上界、公开项目身份、白名单metadata及metadataVersion，main重新签本窗口selection ticket；不返回任意表或自动开放所有项目写权。
- 创建回执：原完整业务请求、真实新projectId、创建receipt及最终项目视图；同operation精确重试返回原事实，异请求同ID拒绝，不借metadata operation冒充create。失败不能遗留可见半项目或覆盖已有库。
- 项目一致视图：同一读事务的domainRevision/inputSnapshot、metadataVersion/metadata、operationSequence/checkpointRef，以及指定editor的draft generation/present/boundDomainRevision/contentHash/完整有界内容。墓碑保generation；不把boundDomainRevision当CAS，不透传完整learning/audit无限数组。

目录/创建请求预算、页上界、库级scope寿命、create claim类型及作用域、错误值须由根/唯一owner先冻结完整schema和正反例，再实施。若现全局claim/receipt不能表达创建前项目身份，不得新建第二可变幂等账本凑实现；提交最小DDL/命名空间方案并独立审查后再授权。

### H2：打开模式与切换屏障，不能在选择前写库

在任何Store构造/迁移前，可信host intent必须明确区分 `open-existing`、`create-new` 和显式获确认的旧库迁移。open-existing缺失、空文件、目录、非DB、未来格式都明确失败，不创建父目录、空库或降为2；create-new独占发布且不覆盖。旧库迁移先显示准确动作/备份位置与影响，取消不迁移；备份不能覆盖/与源别名相同，保留原件和已发生失败证据。打开/迁移的实际文件授权不等于ChangeSet修改确认，不能用一次“打开文件”许可签任意领域修改。

`str(path)+'.writer-lock'`现有锁不能独自证明不同路径别名指同库的仲裁。正式任意位置选择须冻结受信路径/真实OS文件身份、符号/硬链接/重解析点策略及TOCTOU边界，确保同库不会因别名拿两把锁；主库/WAL/SHM/备份/锁的身份和不覆盖规则同列。需要拒绝不支持形态时给有限错误，不透原路径/SQLite异常；不得删除未知文件或unlink旧锁“解忙”。T03来源文件broker、metadata-eligible检查或hash不授数据库读写权。各目标平台只认实际证据，不将POSIX探针当Windows文件行为通过。

I06须实际提供私有profile整根/凭据/audit/pending的完整保护inventory及真实受控FS能力合同；模型初始化失败不能当私有根为空。该策略必须按project-open/create用途设计：现transfer guard只有import/export descriptor，且将数据库根列为转移禁止范围，不能拿它既禁止真实选定数据库又声称已可打开。需要在保留私有根保护和同库单writer仲裁下，明确允许本次获准数据库连接的最小用途/身份，而非放开通用FS。metadata owner、OS adapter和新purpose契约未到时，先只做不依赖其IO的目录投影/原子创建设计与独立服务；任意路径真实接线保持硬前置，不以固定userData替代FR-002的可选存储位置。

**强制切点在首次内容I/O之前**：picker返回仅登记候选，必须先取得上述真实location owner签发、用途限定的可执行能力，并核完整保护inventory、active/retired别名及退役闭合性；随后才允许SQLite/header格式探测、catalog读页、Store构造、备份或迁移。能力缺失/unsupported、inventory incomplete/unknown或平台未证明时，固定拒绝该路径内容I/O，不能以用户选过、绝对路径、metadata-eligible、hash或T03 broker降级。跨await及连接/发布前按该实际能力的fence复验；check后另行按path reopen不是能力闭合证明。当前961ce77不能满足该gate。

建议同进程切换采用**整组项目服务关闭/重建**，不修改现永久stop的Supervisor去假装restart，也不仅替换TaskService后让I06继续持旧engine。最小顺序：

1. 主线程串行标记transition、阻止新项目写请求；先使旧preview/未dispatch资格失效，记录待对账operation。候选位置选择取消保留原项目，但不能复活已撤销票据。
2. 调I06冻结的可信lifecycle关闭钩子：先停止模型新接纳、关闭旧GatewayApplication/来源scope，撤销旧grant/material、取消pending。普通renderer刷新/引擎瞬断不一律等同主动项目替换；不要顺带改I06已有恢复授权政策。
3. 旧写Job按其真实取消/提交边界对账，停止/排空自有worker与SQLite连接后释放lease；实际未settled picker/FS操作仍计槽，不靠abort/rebuild清零。已发送网络数据不承诺撤回。
4. 先在main私下构造候选Supervisor/TaskService，保持initializing且不发布为当前可操作项目；由该实际child的唯一engine/Store执行获准的打开/创建/迁移，同lease做Store校验→Job校验→reconcile→真实同源hello。不能main先开另一个writer制备数据再启动child，也不能等ready以后才“构造”用来取得ready的Supervisor。
5. 候选组真实project读取与当前许可核验后，完成所有固定持有engine的I06服务重建/安全绑定，再发布该候选组；给相同UUID也建立新项目lifecycle/context且local。配置可按原I06政策读非秘密记录，不恢复旧grant、source proof或待发送写意图。
6. 安装新view generation后才显示可操作项目。失败状态明确“项目未打开/待恢复”，保留最后提交和原意图供只读对账；不能用空TaskView/新UUID表示成功，也不能静默重新启用旧模型scope。

H2需要I06真实提供关闭/重新初始化/持旧engine对象清单和可完成/不可取消边界。源broker排空不等于Job排空，模型取消不等于过去零外发；这三条各按原合同验证。

### H3：实际四入口与持久编辑，然后完整Diff接受

四入口保持FR-001原文：内置示例、空白项目、打开已有、快速介绍，均不以前置API配置为条件。H1/H2可先独立实施空白/打开与目录，T09并行交真实模板/初始化/快速介绍内容；**不能因此把四入口验收改成两入口，或把禁用示例按钮/空JSON载入计为完整离线示例**。至少一个完整离线示例仍须真实六模块、G固定输入/输出/失败/重置和学习消费者闭环。

metadata/draft公共读写是编辑/模式恢复前置：复用真实app CAS，guided/assisted只改披露而不改domain格式；draft generation/迟到保存和结果刷新隔离按原M02实际联验。未经批准不接完整learning/restore动作；UI可以在真实缺来源处说明未就绪，但相应FR不登记完成。四类快照及全项目restore保持独立服务/人类确认/throughSequence完整覆盖，不用域undo替代。

ChangeSet建议有限named bridge：`previewChangeSet({draftTicket})`、`previewUndoChangeSet({operationSelectionTicket})`、`readChangeSetDiff({previewTicket,pageSize,cursor})`、`acceptChangeSet({previewTicket})`、`discardChangeSet({previewTicket})`。draftTicket须绑定真实T02/其他批准编辑器或T08建议来源及已接收的内容代次，不凭测试预填计划成为正式producer。人工typed编辑与Agent建议来源分开归因，最终都走唯一引擎服务。

main注入真实project/base/host来源；renderer不提交actor/write/engineSessionId、prepared/confirmationRef、完成cursor、inputSnapshotId/parametersHash或自由jobInput。不开放通用invoke、通用job.create、changeset.confirm，主进程有限routes继续验sender/mainFrame/trusted document并用唯一canonical严格参数/结果校验。

## 3. 完整Diff、人类确认和票据寿命

main私有preview记录至少绑定：当前真实窗口/frame/document、项目lifecycle和TaskService generation、Supervisor对象及真实engineSessionId、公开projectId、domain base、实际编辑CAS/content代次、typed计划digest、engine完整preview/manifest与原分页链。renderer只拿opaque previewTicket、展示generation、summary/intent/documentKind及去权只读文档；prepared/confirmation及engine completion cursor不透出。

main按真实分段链读全并调用5de实际共享reassemble helper，校验成功后才标document-ready；本地UI分页也必须提供整份原文，不能截断旧值、仅给receipt/摘要或只加载第一页。若主进程缓存整文档/renderer分页，先冻结总字节/票据数/并发/实际编码页预算并实测，不能把engine 16MiB自动解释为Electron IPC单帧预算或RSS承诺。换页不重签preview，不让UI自报“已读完”升级权限。

一个实际trusted UI明确接受动作是最终人类确认步骤；不额外叠第二次强制确认，不以page/hash“证明真人读完”。UI须显示业务摘要、完整Diff入口和实际冲突/范围，再允许用户接受；main仍独立验票据和来源。conflict/undo-impact永不可accept，impactComplete=false明确暂停。人类取消零confirm/零create；引擎首次confirm前若已变base/控制/来源须重预览，不能沿旧票据再算一个Diff悄悄提交。

编辑变化、重新预览、导航/刷新/窗口重建、项目切换/重开、换Session、base推进或来源CAS变化均使旧待接受票据失效。App自己的draft/fetch epoch与现latestGeneration/connectionEpoch联合防迟到显示；main也检查实际记录，不靠disabled按钮。编辑代次必须来自实际host接收/持久CAS链：仅renderer自报editToken或旧按钮回传generation不构成可信当前性。具体编辑更新、票据撤销与点击接受的main串行顺序须与T02/I06先冻结，不凭通知可能已发出就断言已生效。

## 4. 实际写帧前的闸与未知状态

在engine.ts增加**仅main服务可调用**的受限dispatch guard/等价接口，覆盖首次confirm与job.create；必要的项目创建/选择授权变更也遵守相同原则。guard捕获host私有scope/ticket，不能由renderer传函数、布尔权限或回调；在await ensure完成后、真正stdin.write之前同步核当前Supervisor/Session/项目lifecycle/文档与编辑代次、原preview资格。各await后复核仍保留，但不能用响应后generation检查代替这道闸。guard拒绝明确未dispatch；已dispatch则后续选择取消/关闭不能声称零Job。

main在受理前固定一次operationId和完整原业务请求/确认身份。确认请求响应丢失，同host/Session按原完整params读回持久confirmation回执，不换cursor重签；换Session不能用旧未受理确认新建operation。job.create响应丢失进入unknown，先只读找原claim：现operation.get=null仅表示无marker，可能queued/running。最小可用方案是冻结同项目all job.list完整分页→按原operation筛选→job.get/operation.get及完整可核context核对；列表不全/驱逐/身份不足时保持unknown。若现DTO不足以核原请求，不在main猜成功，改向根申请精确只读operation-resolution DTO，不改旧nullable marker含义。

main崩溃后的“原请求在哪里、如何恢复其可信来源”也必须交付：不能只保内存ticket或remembered Job；建议由现同库受信基础保存有限不可变host提交意图/operation归属，或用足够完整的既有claim只读投影恢复。两者须选一并冻结唯一权威、寿命、预算与敏感字段；不得临时另建未审的main可变账本或把session授权持久化成自动重放许可。只恢复待对账意图，不恢复人类确认权。

accepted原operation跨Session仅恢复原Job/receipt，不自动job.create、换operation、重签或重放。已知jobId复用现订阅/取消/restore/reconcile；未claim但原请求已dispatch且ack未知不能凭一次null就新建。真正受理/取消/提交先后以Coordinator/持久Job为准，不以stdin线程已读或renderer收到状态为准。

## 5. 唯一owner、最小路径与交接窗口

以下为**申请/候选路径**，不是新增写权；根须以实际chosen方案删去不必要路径并逐一授权。未列的protocol/worker/resources/build/锁/CI、旧测试、CSP/window安全/恢复均不写。新测试路径在阶段实施前另给固定清单，不能泛授权整个tests目录。

| owner与阶段             | 最小候选产品路径                                                                                                                      | 理由/前置                                                                                                                                                               |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T01 canonical H1/H3及§4 | contracts `src/index.ts`、`src/v2.ts`、`python/contract_v2.py`、`v2/schema.json/registry.json/fixtures.json/binding-regressions.json` | 唯一库级/项目只读/创建/Host DTO及方法分类；旧2不放宽。`errors.json`仅旧有限码不能准确表达实际分支时单列申请，不能预先扩无限路径参数                                     |
| T01 engine H1/H2        | `job_store.py`、`coordinator.py`、新`project/project_host.py`                                                                         | 一致目录/metadata/draft投影、库级host gate、真实公开UUID与scope；创建claim/receipt/API须先审                                                                            |
| T01 Store条件路径 H1/H2 | `storage.py`、`project/format3.py`、`project/applications.py`及必要入口`__main__.py`                                                  | 仅实际open-existing/exclusive-create/alias lease/原子genesis或选定claim需要才授权；不把项目路径塞普通RPC/新startup stdout。若涉及DDL/启动分类须完整新合同和真实故障矩阵 |
| T01 main H1–H3及§4      | `main/index.ts`、`main/engine.ts`、`main/task-service.ts`；建议新`main/project-host.ts`、`main/changeset-host.ts`                     | 位置/目录/服务cohort、真实scope、ticket、同步dispatchguard/原promise认证和unknown发现；新私有模块必须精确登记                                                           |
| I06消费 H2/H3           | `preload/index.ts`、`renderer/src/App.tsx`                                                                                            | 命名桥、四入口/目录/编辑来源、完整Diff/一次明确接受、冲突/撤销/unknown呈现；I06须给当前实际起点SHA并停写交接或由其独立树按冻结DTO实现                                   |
| I06条件/私有生命周期    | `renderer/src/env.d.ts`通常不改；`style.css`仅实际布局需要；私有ModelGatewayService/StoredResultSource等具体路径由I06列               | env继承唯一DesktopBridge；不复制schema。若整组关闭/重建可复用现私有close/initialize，不先改网关实现；固定engine引用不能遗漏                                             |
| T02/T08/T09/T10供方     | 各自精确合同/固定输入，由原owner写                                                                                                    | 真实编辑/建议来源、模板/快速介绍/检查、辅助归因/导出项目闭包；不以本计划取得其文件或采用未批准候选                                                                      |

当前packaged仍默认2，unpackaged仅显式内部flag选3。真实host业务3启用必须由根单独冻结受信激活范围、同版资源/两层ready/兼容与回退政策；renderer不选version，不能借UI接线顺带全局翻转生产。5de已提供的有限启动失败和sticky行为复用，不无变化重开旧startup；新增open模式/错误确有实现影响才验证其实际delta。

跨owner接线建议先锁DTO/库级与项目scope/生命周期/dispatch cut，再让I06消费批准合同；强依赖串行，独立的目录一致读、create原子性、UI只读展示、T09内容/真实producer和测试夹具可在各独立树并行。不在冻结5de树混入他线代码或更新总控JSON。

## 6. 新阶段必须实际验收

| 范围                | 必须交付的真实证明；当前均未执行                                                                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 位置/open/create    | 用户真实选位置；取消零创建/迁移；open缺失/空/目录/非DB/未来格式不创建或降级；exclusive create不覆盖；alias双开正确busy；备份不覆盖/同源别名拒；目标平台实际文件行为与TOCTOU边界                                           |
| catalog/许可        | 原UUID重开稳定、inventory零写/不补映射；有限完整分页与同名项目；跨库/他项目/旧ticket不能授权；真实新建请求每持久边界异常/写失败/取消/真实退出，完整前后库和单claim/单receipt、丢响应原请求对账                            |
| metadata/draft/模式 | 同事务domain/app/current视图一致；墓碑CAS/JSON null/内容hash与实际编辑一致；迟到保存/结果刷新不覆盖新稿；引导/辅助切换与重开不变domain格式，自动保存真实用户动作不依赖模型                                                |
| I06生命周期         | 同UUID主动重开/迁移与普通瞬断/刷新分开对照；旧scope/grant/pending关闭，所有持旧engine者重建；晚IPC/密文/来源响应不装新context；未settled操作不假释放，不能承诺已发送网络撤回                                              |
| Diff/确认/闸        | 实际main/preload/renderer/IPC与可信sender/frame/document；详细旧值跨页完整，非摘要替代；冲突不可接受；仅一次实际人类确认；ensure等待期间切项目/关页/改稿/换Session时guard零dispatch，已dispatch对照必须unknown/真实cancel |
| 未知与重开          | confirm丢响应TTL/GC原回执；job.create已queued却无marker/未知jobId；进程/窗口重启恢复原operation；完整分页发现/身份不足保持unknown；绝不自动重放/换op/从null猜未受理；afterCOMMIT保成功                                    |
| 四入口与父范围      | 无API可用四真实入口；至少一个T09完整离线示例及真实领域/学习检查；完整快照/全应用恢复/四触发器/FR-006及其余44行逐项保留；不能用本次目录/typed编辑取代父要求                                                                |
| 同候选交付          | 新源码/完整原件、受影响专项、完整check/sources、实际新unsigned包及包内业务；真实IPC/native/目标OS/真人在获批隔离环境完成；GLM-5.3最高与M3.1-Flash/xhigh同版全范围新审、CI/正常合并/远端，不能承接旧Pass                   |

测试设计先将未dispatch/已dispatch、native逻辑abort/实际settled、源码mock/真实进程/包/真人证据分开；保存首失败和实际终态。当前Mac不启动Electron/native/e2e/HMR、凭据或审查应用，隔离资源未到不伪称验收通过。

## 7. 交给根的最小阶段决定

先确认H1/H2的真实位置模型、库级host前门/单项目scope、create幂等与read projection、open/create/migrate和alias lease合同，以及I06整组生命周期hook；据此锁最小路径/测试owner与实际输入。再授权内部服务和可信host基础，随后接真实编辑/完整Diff/四入口及人类验收。需要新只读operation-resolution或持久host意图时明确选择，而不是用null marker/内存remembered掩盖。

原5de ChangeSet内部阶段和其外审候选保持冻结。总控后续收口3483B/SHA `ebffe4122a18665048c930fe00b1a9ac1d052de9a4c2dc03cfcd87ae1b30f333` 已在本轮实际全文读回并核hash，确认内部typed阶段成立；未授本下一阶段实现或父功能通过。此方案只推进准确接口准备，不启用新能力、不缩减原完整Goal、不把等待资源当父功能完成。
