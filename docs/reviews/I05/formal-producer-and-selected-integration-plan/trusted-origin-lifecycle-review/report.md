# I05 正式 producer / selected 方案：真实来源与生命周期独立审查

结论：**固定候选不通过，1项P1方案缺陷（OL-1）**。selected 的选定 worker 角色合同遗漏 consumer 原Job自身的 asserted/ontology 输入；K=0 时没有任何 producer artifact 可以供应这两类图，无法执行所承诺的 asserted-only query/validation。其余查到的正式来源、Store、权限、role存储/GC、永久排空等缺失，方案已正确识别为尚待原owner实现/冻结的供应门，本审不把这些“未实施”重复算作当前方案漏洞。

本次完全静态：没有import产品、执行引擎/测试/SQL/组合探针、创建worker/环境或采用；没有GUI/native/HMR/模型/付费、其他聊天消息、Goal、提交或切分支操作。唯一写本目录报告与静态输入清单；主方案及旧160原件没有改动。

## 1. 固定对象、授权与方法

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/I05-profile-restore`
- 候选完整ref：`651c4c2d2dd498ebc572543d116f2cdddb678045`
- 主方案：`docs/iterations/I05/formal-producer-and-selected-integration-plan.md`，**59605B / SHA-256 `fe28f883c1db687b4c20da4f91046d66216fcb4322a43633306af159a9cb861f`**，完整读取213行。
- 受理/Store/worker基准：T01 C1 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`；I05计算/恢复基准 `3ef2f6952ed1a4f852da31c0bef7e8d8679752a5`；旧C4事实参考 `523c478d5f39671c4ac7c1ea6997e51d3047d58e` / `40c18ea1b9ce4fef9a5235718fd7e622e2d06cc4`。未用主树WIP替代这些版本。
- 已完整读取当前AGENTS、主checkout根授权 `iteration-control/2026-10-21-weekly-release/I05-formal-producer-and-selected-integration-plan-preparation.md`（**6107B / SHA `3d707e0844e4302f5bbdf62e51fdb790737df1e690127c451fc20f47feadfa42`**）、根strict closure及当前developer-common-instructions（含完整第九节、无桌面与维护权补充）。当前AGENTS为15852B / `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。

方法为固定Git全文/相关函数逐行读取、JSON字段/角色集合交叉核、哈希/字节核对和手工时序反例。`static-input-manifest.json` 列25个固定输入、5个当前未版本化权限快照的精确ref/path/bytes/SHA及实际readScope；另逐Git核135项拟闭包描述与七份旧C4源身份。135项只做身份核验，不等于全文功能审查、采用批准或可运行证明。轻量历史记忆仅用于定位“pure API不认证来源”的既有边界；本报告所有当前事实均按固定实际源码重新核查。

## 2. OL-1：必须先补的方案级反例

**[P1] 为所有K供应consumer原Job输入，而不能只供应producer artifacts。**

- 主位置：方案 **第130行**；相关承诺为 **第155、157、159、200行**。
- 选定合同：selected阶段parent→worker仅有“每个原结果”的origin/payload/rows/input/source五类角色，加本consumer的consumer-definition；同段禁止worker自行开库，并要求phase/role固定。第155行明确K=0为asserted-only，第159行要求用原immutable输入构建RDFLib图，第200行把K=0列为真实成功验收。
- 具体反例：真实T01接受query Job C，原snapshot S含断言 `urn:a urn:p "x"`、对应datatype property ontology定义，consumer-definition只保存实际SPARQL `SELECT ?s WHERE { ?s <urn:p> "x" }`。用户选择asserted，derivedResultIds=[]，即K=0。按第130行角色清单，没有任何producer result，也就没有input-preimage/source-preimage角色；worker只获得query定义及绑定摘要，得不到S的事实和本体内容。它不能从query文本或snapshot hash还原事实，也不能开第二Store。若返回空结果，则把非空真实输入变成了错误结论；若一直unsupported或失败，则不满足被明确承诺的正常K=0成功链。
- 实际源码依据：旧I05 `semantic_execution.py:376–384` 分别从request原snapshot的facts和ontology definitions构图；`semantic_scopes.py:52–70`、`:234–264` 同样要求调用方供应两类图，selected输出不会生成它们。T01 C1 `coordinator.py:607–613` 的现owned worker只拿capability/parameters/memoryBytes，不存在未列出的自动snapshot供应；`worker.py`也没有DB权限。当前缺供应本身不是发现，**选定的新穷举角色合同仍无法表达必需输入**才是方案缺陷。
- K>0也需分清：producer原input/source用于复核原推理，consumer原Job的asserted/ontology则用于确定本次查询/验证的基础scope；不能把若干producer输入任意并集当本consumer事实。T01现 `_dependencies:758–773` 已核同inputSnapshotId及重叠manifest一致，这些校验并不会替worker送来内容或规定分层；所有K都需同一明确物料规则。
- 修订建议：在第130行明确新增或明确内嵌的 **consumer原snapshot asserted/ontology input及source物料**，K=0..32均必需，受理前由T01原snapshot owner固定canonical内容、身份、长度、来源、版本与当前权限，再通过原owned通道送达；为其单独声明大小/总流/持有/解析预算并纳入T/S/H及role manifest。若选择把它放进consumer-definition，必须明确exact typed子字段、内容来源和边界，不能只靠名称让实现者自行塞整snapshot。实际producer的B/Q/P和消费者原图物料应明确各自身份与所有权。
- 回归/验收补充：K=0下分别对非空asserted-only query、SHACL断言违规/通过、空asserted图执行真实Job→新worker；另对K=1/2/32保持相同consumer snapshot和完整有序选择，故意错换consumer snapshot/ontology/source/role尾片，须在内容消费或发布前有限拒绝。新输入供应不能借重新reason或从expected/oracle构造图补洞。

以上是计划反例，未运行SPARQL或产品。父审已收到，修订尚未包含在651固定字节中，本报告不预先按拟修复关闭。

## 3. 实际可信链核对

| 面 | 已核实际源码与方案对应 | 审查判断及边界 |
| --- | --- | --- |
| 原Job及不可变输入 | 423b `create_job:854–1013` 在原事务里写queued/context/fingerprint/operation claim；context包含原snapshot、参数、input、implementation、limits、vector/manifests。`_accepted_job:1015–1078` 核原context和重试输入，不按当前base重造。 | 方案第30、45–48、86行正确复用真实基础，没有将test-only外部expected换个名字当正式捕获。新增semanticInput/原dispatch/source供应明确尚缺，属S1门。 |
| 一次capture切点 | 3ef `_execute_profile:626–738` 当前一次reason，随后同一projection完成result→source→definitions及rows；`semantic.py`原allocator创建每个L、实际Catalog在原计算内生成。方案第74–76行要求在实际发生点独立capture，非mechanismBatches反推L。 | 单一core/facade重构方向成立；前像须计算前固定、所有正常输出门完成后才发生产记录。实施仍须覆盖既有facade/测试/消费者；文档不是现成capture实现或预算证明。 |
| owned worker成功来源 | 423b dispatch只正式开放changeset，其他仅test分支；execute只传有限参数，已有complete+正常exit+cancel检查。 | 方案第32–33、86、111、128–132行承认真实新profile worker通道尚缺；不复制旧worker、不以success=True认领来源正确。新角色完整性仍受OL-1阻断。 |
| 同Store原子origin | 423b `finish_read_job:1274–1284` 已将result+succeeded放同事务；`_publish_job:1516–1604` 发布普通rows，当前没有B/Q/origin；jobs.context有immutable触发器。 | 方案第96–102行把新增origin放同Store typed details/private ref并要求迁移、同事务rollback，而不更新原context或建第二receipt账本，方向正确。供方必须实现实际transaction内部核对，不能把事务前缓存检查当最终cancel/权限fence。当前计划已有拒发布要求，本审不把尚未交付的事务实现重复算漏洞。 |
| 跨库/项目/锁及权限 | 现snapshot读取核internal project/hash；Job及selected要求完整implementation相同；当前source helper只证明同Store bytes完整性。 | 方案第52、86–94、155、174行完整记录原Job/operation/library public/internal/source/defs/lock/code manifest与current permission generation；未知physical/dispatch保持关闭。真实I06/native供应未到前内部临时库联验可推进，但不能登记正式用户来源成立。 |
| 内容身份与授权区分 | `source_content.intern_content:127–147` 明说不产生grant/Job/claim/receipt；read核完整manifest/chunks；source存入不可删job_blobs。 | 方案第35、61、92、98行没有用sourceRef/tableDigest/SHA替代权限，也保留原parser/options/row/column来源；正确。mapped source真实来源与typed规则确认还需原owner供应，不能仅从opaque定义JSON推断完成。 |
| selected完整K范围 | canonical jobInput为exact六字段，derivedResultIds 0..32且没有uniqueItems；现legacy request仍len=1，旧selected只收五键。 | 方案明确新adapter保序、重复/33拒绝、全部K/原N槽/同原L，不声称当前legacy已支持；OL-1需修。same snapshot、reasoning kind、payloadavailable、manifest一致、完整implementation相同的现T01前提也应在新S1/S4中保留为明确断言。 |

origin持久化中的完整source/definitions/Catalog/parameters与原L是必要数据，仍不构成自认证；方案没有把pure `formal_authority=False` 改成授权位。代码/锁三字段相同而实际实现漂移的负例已列producerCodeManifest供应与验收门。普通SHA不认证控制DB/安装代码的恶意主体，该威胁边界也已明确。

## 4. 复用、失败、退役、GC及重开

| 对象/时序 | 实际核对与判断 | 仍必须在供应/实现中验证 |
| --- | --- | --- |
| 原operation重试/响应丢失 | C1 `_accepted_job`读原claim和immutable context；`operation_get:1210–1225` 只查marker，readJob可null。方案第100、161、168行要求原claim对账、不新建operation绕过。 | C2真实claim发现接口仍是S5供方门。不能marker-null=notAccepted；同Job活跃handle复用不意味着可免费重开恢复池。 |
| 非terminal重开 | C1 `reconcile_jobs:1444–1471` 在lifetime writer lease后把queued/running/cancelling归失败/取消，不重跑。 | 方案正确要求原真实reconcile，禁止静默reason或用marker补成功。原输入可读不代表原Job可再次执行。 |
| active/retired | C1 coordinator kill后wait；engine `#finish:328–364`清当前session指针后发kill/延迟SIGKILL，`stop:366`为void。 | 方案第114、171行正确不把pending0、stop返回、kill请求当永久排空；完整退役cohort及pipe/timer/native终态为S5/I06门，不是本轮已存在能力。 |
| 取消/撤权/窗口切换 | 现cancel_job在原事务内queued→cancelled、running→cancelling；coordinator在提交前再次核状态。TaskService detach只换generation/视图，不等于后台结束。 | 方案第167–172行正确先fence，再等实际释放后解pin/名额；必须在最终实现精确规定同actor/事务线性化，按J04/J07覆盖撤权与commit、lease命中、worker退出的竞态。未提供实测不写通过。 |
| role cache/pin/GC | 现 `collect_cache`只清非pin/非current结果payload；job_blobs/Job/claim/details存在immutable trigger，不存在role-aware GC。 | 方案第98、113、167–170行已要求原owner迁移和新角色存储、active+retired pin及配额；没有擅改旧immutable source。payload evicted、source missing、损坏、permission拒绝需分别有限结果，不能填假页面或默重算。 |
| native/PV/view/traceback | pure 3ef已有限收口；新fullview及scope生命周期尚未实现。 | 方案第77、157、170行明确同时预留后转交、清所有新增native/Graph/traceback locals、全部K成功才发布。既有S2经验已纳入，未来必须对新view和多结果末项故障实测，145纯恢复测试不能跨用。 |
| 历史与current | 当前selected依赖相同inputSnapshotId；Store current仅在原snapshot revision和依赖仍有效时设置。 | 方案明示historical选择、缺origin旧结果普通历史可读但新profile selected有限拒绝、不倒填来源。不得将“historical”变成V1推导混入V2当前图的豁免；新adapter应冻结实际同snapshot约束，不能自行补答产品决定。 |

这些是已在方案内明确存在的待实现门，不是本报告新增“等待整个T01/I06”的笼统阻断。内部真实临时JobStore3/owned worker可在获具体代码窗口后验真实链；正式public/native来源仍单独保留门禁。

## 5. 旧C4事实与供应路径准确性

已静态核523旧coordinator确有semantic.start/semanticRequest处理、worker实际进入语义执行且无DB权；旧request检查原snapshot和selected身份。资源/semantic/execution/query/samples/scopes/turtle七源在40c与523逐字相同，完整字节/SHA在本审manifest。这支持“旧finite6真实链存在”，不能把旧代码说成从未有过真实Job/Store/selected。

旧根C4 readback对Session(test_mode=False)、10×19=190完整结果、selected query/SHACL及关闭重开有明确有界证据，也明确没有完整DB离线重开原资源表证明。本审读取该根报告的相关原证据边界并核实际源码，没有重跑driver或重验1254成员归档。方案第16行没有把旧C4扩大成finite7成功，未继承其指定双审/发布通过；这一定位准确。

T01 S1–S5、T05机制/数学/解释、T03四build/lock及I06权限/native的owner与请求方向总体准确。现typed ChangeSet仅ontology/手工facts，不等于profile规则已可确认入库；当前worker也只test基础。拟52组件和135闭包不是写权转交或直接可跑组合，方案保留resources冲突、每能力implementation、未来精确supplier ref/完整closure重新冻结的门。此处不因新模块名称或数量完整便给采用授权。

## 6. 结论出口与未运行边界

先按OL-1补全所有K的consumer原图/source供应角色、身份与预算，补K=0正常成功/非空/违规及错物料负例，再生成新的固定docs/ref供必要delta复核。现651不宜作为“完整集成方案已审过”进入代码窗口。

没有其他已证实的来源/生命周期方案阻断；这不证明尚不存在的S1–S5实现、C/T/S/H费用、真实source确认、role GC/lease、跨库/权限/native或生产链已通过。目标平台、真人、全I05/57P0/FR/10–12、指定GLM/MiniMax双方新审、CI/正常合并和远端门保持。不得把此次静态审查、旧C4或3ef纯恢复结果计作新正式集成验收。
