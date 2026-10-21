# T01 真实供应接口静态调查

结论：选 **C1 固定 `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 的完整52路径组合**作为下一阶段拟只读 T01 基础；按路径采用，不 wholecommit。它已经包含 a816 的只读宿主和5de的真实 typed ChangeSet/Job3。真实 Job/claim、不可变快照/参数、单连接 result+terminal 与重开对账有现成实现；I05语义 Job准入、同次捕获、完整制品运输、独立持久来源及selected reader/pin生命周期仍是具体未实现供应，不能说等完整T01或native才可设计，也不能将基础链当已接I05。

本次仅静态 Git/文本/JSON/AST/hash，不 import/执行产品、SQL/数据库、fixture、测试、worker、构建、GUI/native/HMR、网络或模型。没有采用源码、创建产品树/环境、提交/切分支、修改Goal或向其他聊天派任务。唯一新写本目录。产品事实均取固定Git；root closure只作固定版本索引，不代源码。

## 1. 固定输入和边界

`future-readonly-T01-52.json` 给52个精确 path/ref/bytes/SHA。原C1 `source-manifest.json` 的 `productsAndTests` 52项已逐固定423b Git核同；其 header `sourceRef=a816` 是原采用来源，不是最终五writer的版本。`fixed-interface-inputs.json` 另列10个同5f的既有依赖与41个实际函数位置；未来全采用闭包要与I05/T03逐路径合成，不能仅复制这52项就称完整运行树。

重要组件（下列完整SHA在JSON中；只读事实，不授实施）：

| 组件                | 固定产品/路径                                                                          | 当前可用及不得扩大                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Store/Job3/C1       | 423b：storage.py 76042B；job_store.py 87227B；project_lifecycle.py 20932B              | Store3+Job3、一库多项目、唯一claim及事务、内部空白创建；不认证原物理库/dispatch/current permission。            |
| readonly host       | a816继承于423b：project/project_host.py 15777B/a142d9dc…                               | 真实现有JobStore3连接完整catalog/workspace读取；不创建scope/快照或打开路径。                                    |
| ChangeSet           | 5de继承于423b：project/domain_changesets.py 34728B、transactions.py 11924B             | 真预演/完整Diff/确认/同一Store提交；当前仅受支持ontology与手工facts，非全部规则编辑。                           |
| startup/coordinator | fd阶段后5de继承于423b：coordinator.py 41168B、**main**.py 3469B、main/engine.ts 26260B | 显式business3、默认2；真实owned child、状态/取消/重开基础；仅正式ChangeSet和test专用worker，语义仍design-only。 |
| source内容          | ff98761后继承于423b：project/source_content.py 6844B/d3e660b7…                         | 同Store的8MiB/128×65536 chunk内容缓存与全字节复验，不是source接纳/授权/pin/GC。                                 |
| source table        | bf04169后继承于423b：canonical Python/TS helper                                        | 完整data-only table/options/implementation先界材料与摘要；不是实际parser身份或完整source供应。                  |
| 原owned worker      | 423b与5f相同：worker.py 9314B/2fa848aa…                                                | 生存owner监测、测试计算/ready rows；没有semantic capture。                                                      |
| immutable依赖       | resources/protocol/memory_guard/process_environment/rdf_snapshot/invalidation等10项    | 同5f原字节。T01 resources 当前 IMPLEMENTATION=`i04-infrastructure-v1`，不能拿它给finite7 Job冒充同版身份。      |

C1精确52路径属于组件候选，不把所有52路径维护权转I05。T01唯一维护 Store/job_store/coordinator/worker/**main**、canonical、engine.ts/main/index/task-service/jsonl及task-presentation；I05原task-runtime维护权已返还，但本次也不授修改。T03四build/依赖文件仍其唯一owner；T05机制API仍T05。未来请求由根路由，不由本调查派其他聊天。

## 2. 当前真实持久链

以下行号按423b，完整位置见JSON。

1. `JobStore.create_job:854–1013` 先验证 canonical params_job.create/implementation/limits，按public project映射internal；同一次 `_transaction` 中先查全库唯一operation claim。新受理时 `Store._project_snapshot` 从原不可变snap ID读完整 `{project,projectRevision,dependencyVector,state}`，state包含mappingState/definitions/facts，且核实际project/hash/shape；参数从同project `job_blobs`按hash读回核真字节。
2. 原context存在 `jobs.context TEXT`，指纹同时在jobs和 `operation_claims.fingerprint`。完整内容为 `{input,confirmationRef,parameters,snapshot,plan,projectId,capability,implementation,limits,dependencyVector,manifests}`；rounds另有实际runConfig。并非只留当前base或摘要。`jobs`原id/project/operation/context/fingerprint不可变trigger保护；`operation_claims`不可UPDATE/DELETE。Job DTO在 `jobs.dto`，stateVersion/terminal随后在同Store更新。
3. `create_job` 写queued DTO、完整context和claim在同事务。`_accepted_job:1015–1078` 重试先核原claim/project/kind、Job关联和完整context指纹； supplied project/capability/input/confirmation/implementation/limits逐canonical等原值，再核原snapshot/原参数/prepared/确认。旧context绝不能就地改hash来“补来源”。
4. `get_job:1080–1106` 反核DTO与原context；`job_context:1108–1118` 仅在fingerprint匹配后取完整原context。`finish_read_job:1274–1284` 在一次事务要求running+mode none，发布result后更新succeeded+resultRef，两者同COMMIT；已有terminal只返回原Job，不能由late结果覆写failed/cancelled/succeeded。
5. `cancel_job:1151–1172` queued直接持久cancelled、running→cancelling；response保决定时快照。coordinator在提交前再核cancelling和deadline，异常/取消先收自有child后调同Store失败终态；重开 `reconcile_jobs:1444–1471` 在取得实际writer lease后把原非terminal标failed/cancelled，不重新执行计算，也不凭marker捏造成功。
6. 实际formal `Coordinator.dispatch:333–460` 只有business3 changeset.commit例外通过；其余若非test_mode或非test.*就UNSUPPORTED_CAPABILITY。`execute_changeset` 在唯一writer直接提交，不用伪rows。旧worker路径 `execute:551–754` 只把capability/parameters/memoryBytes给child。`worker._execute:211–255` 只做test rounds/read；这条路径不是I05 producer。

这可支持下一授权中“真实临时JobStore3 + 真实owned worker”的内部联验基础，不必先有用户目录。但permission/current_scope/物理绑定尚缺时，正式用户入口仍关闭；内部真实受理不能被改写为正式用户来源已认证。

## 3. source/definition/Catalog供应的实际缺口

- public `jobInput` exact六字段：`inputSnapshotId/scope/definitionId/parametersHash/derivedResultIds/preparedPlanRef`。已允许asserted/derived范围、参数和snapshot/definitions引用；**没有sourceProof/source raw ref、parser identity/options/tableDigest、original allocator、payload/rows digests或host/Session/generation/physical-binding**字段。不得绕additionalProperties=false塞字段。可由canonical唯一owner定义私有context typed extension及其未来公开适配，而非renderer传true/任意JSON。
- `JobStore._definitions` 仅从snapshot产生family/id/version/references供dependency选择；完整定义payload仍在snapshot中。但原Store `_definition` 对其他payload多为opaque JSON校验，`domain_changesets.supported:110–127` 对触碰definition只放ontology的triples/singleValuedPredicates/references，拒绝rule等其他family。故全finite7 RuleSpec/实际Catalog的可信编辑/入库/版本producer是实际缺口，不能把ontology服务等同全部规则已入库。
- source_content 的内容地址只证明同project完整bytes、canonical chunk和manifest；没有broker/current scope/当前reader、原operation/Job、parser执行、TTL/pin/配额/GC。sourceRef不是rawSHA也不是authorization。CSV/XLSX table helper只证明受控材料/encoding词汇/有序cells；Turtle的同次source witness以及semantic structured records须由真实I05 adapter与受理owner固定，不能拿tableDigest当SourceRecord或同次计算证明。
- T01资源的implementation是i04基础身份。正式语义准入必须从实际已装I05 producer取得完整finite7 engine/semantics/实际锁身份，并纳原context；不能让worker自己上报新锁后默认与Job原身份相同，也不能把parser三字段身份替whole semantic implementation。
- 新实际原L仅可由一次真实producer的allocator/capture切点输出；不能从保存payload L字段反推为独立L，更不能selected子集再分池。post-success capture metadata必须在原结果事务独立持久关联原Job，而非改变已经immutable的原context。

## 4. 当前result/selected可读接口的完整结构

`_publish_job:1516–1604` 只接受canonical普通rows list：最多10000行，`canonical(rows).encode()`≤8388608B；每row exact `{rowId,ordinal,cells}`，rowId UUID、ordinal非负safe int、cells最多64、每string最多8192字符，其他cell仅null/bool/有限safe数。核rowId/ordinal各自唯一后按 `(ordinal,rowId)` 排序。此8MiB是**整rows**门，不是strict restore的payload_json+rows_json合计B，也不含Q或source/retention票据；现函数会先完整canonical分配再检查，不能当已具新R分配前门。

Store.results持久 `{id,project,snapshot,kind,dependencies,implementation,cache_key,payload}`；payload在此路径是普通rows数组。job_results另存 `{id,job,manifests,projection,created}`，projection精确原 `{definitionId,scope,parametersHash}`；result_state保存stale，job_current按完整query key保当前指针。

`result_get:1610–1645` / canonical result_result.get **仅返回17字段metadata**：

```text
resultId, projectId, jobId, kind, definitionId, inputSnapshotId,
inputProjectRevision, dependencyVector, definitionSetDigests, implementation,
scope, parametersHash, state(current|stale|historical), staleReason,
payloadStatus(available|evicted), createdAtMs, historicalSelectionRequired
```

没有payload、source、同次原L、proof或完整strict bytes。metadata也必须受真实262144B输出frame约束，不能仅因DTO语义shape合法就宣称任意dependency量都可传。

`result_current:1647–1670` 以完整 `[project,kind,definitionId,scope,parametersHash,implementation]` 查询，payload evicted则null。`result_page:1821–1854` 是有写游标的普通投影分页，不是strict reader：

```text
binding={projectId,resultId,inputSnapshotId,scope,parametersHash,
         order:'ordinal+rowId:asc'}
request={binding,pageSize:1..200,cursor:null|UUID}
response={binding,rows:[普通row],nextCursor:null|UUID}
```

同事务逐snapshot/scope/parameters对metadata；按ordinal+rowId升序。page schema最多200行，候选encoded_size≤131072B，Coordinator再按实际maxPageItems/maxPageBytes和262144 frame限制。cursor绑定完整binding+page_size+position，TTL默认60000ms、最多256（构造可收紧或至4096），未过期同请求复用同页token。

`_result_rows:1720–1730` 先从SQLite完整读取并json解析全payload，再分页；其后available与候选rows还有临时副本。它没有提供strict payload/rows两份原byte、input/source前像、capturedOriginalAllocation，亦无恢复R/源缓存pin。**当前 selectedResult 不能据现result.get/page供应完整恢复输入**。未来需要私有完整artifact reader，保持外部普通分页兼容；不能把display rows拼出的payload临时expected包装当trusted provenance。

## 5. 活跃、退役与回收：谁当前真正拥有

| 资源                         | 实际owner/当前账本                                                                                                                                     | 当前缺失与最小后续条件                                                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DB/Store/原Job/claim/history | Coordinator持唯一JobStore和lifetime OS writer lease；真实SQLite唯一可变源                                                                              | 不另开worker DB/第二Store。物理位置/current permission仍需真实host/I06供应，libraryEvidenceRef/migration_id只逻辑证据。                                                                                  |
| 活动worker                   | Coordinator.active + tasks + process对象；cancel/failure kill后await wait，finally从active移除                                                         | 现无semantic artifact完整阶段、role累计传输/pin/restore强引用账本；不能把pending清零当child/stdio/native已结束。                                                                                         |
| main session/child           | EngineSupervisor当前#session/#starting/每session pending、listener/timer；#finish删当前指针后kill并安排SIGKILL/close cleanup                           | 没有覆盖所有已退役child的永久bounded cohort/stopAndDrain；stop():void。T01永久排空尚为方案，不能当实物supplier。                                                                                         |
| renderer视图                 | TaskService.selectProject只由trusted main调；detachView递增generation/清watch/早到通知/订阅，dispose释放listener                                       | 视图卸载不是后台Job取消/结束，也不是缓存source释放。selected语义raw/PV的owner及撤权后drop尚未建立。                                                                                                      |
| 结果cache                    | results.payload可NULL；collect_cache清非result_pins/非current_results/非job_current；metadata/Job/claim保留。pin_report原子pin完整explicit结果manifest | 当前历史receipt metadata不删，但receipt的cache payload亦可回收；不能把cache不在当原受理/终态不成立。需要明确selected-source保留/缺失有限结果，不默重算。                                                 |
| source/parameters blobs      | job_blobs immutable UPDATE/DELETE trigger、payload NOT NULL；source_content复用该表                                                                    | 当前无source GC，亦无可回收role/active/retired/account/pin schema。不能通过collect_cache清source，也不能直接破坏参数/原context引用。未来T01同唯一Store的role-aware保留/回收接口需要精确schema/迁移批准。 |
| readonly host快照            | ProjectHostReader私有catalog缓存：≤4 snapshots、8MiB逻辑retained、绝对TTL60s、close清掉                                                                | owner必须在权限/Store能力失效前关reader；close不关Store。该账本不能借来支付semantic sidecar或PV。                                                                                                        |

所有“待真实释放”的资源继续占原owner名额，失败/取消/窗口关闭/权限撤销只先禁止新消费；实际流/child/读者/raw副本/PV强引用终态确认后才降live。历史claim/Job/receipt/capture身份及其必要原metadata不按缓存额度回收；payload/source若可回收，明确PAYLOAD_EVICTED/source-unavailable，permission失败先拒内容可见。cache key须完整库/项目/原Job/source/定义/参数/implementation/锁/profile/capture版本/原L/selected绑定；hash仅地址和完整性，不作为业务相等或授权。

## 6. 最小T01供应请求（供根路由，均未获代码窗口）

选定一条扩展既有真实链，不造第二Store/Job/receipt/意图账本。下列**私有接口名和typed版本是本方案请求**，不是当前存在的公开DTO；T01唯一owner须按同版canonical/worker合同冻结后I05才能逐路径消费。

### T01-S1：真实语义受理与完整原context

拟 `create_profile_read_job(project,operation,input,*,trusted_admission,implementation,limits)`。复用原create_job/claim事务，原JobDTO和六字段jobInput先不扩公开；增加typed私有 `jobs.context.semanticInput`，版本 `i05-profile-job-context/1`，完整冻结：原原request（含operation/capability/六字段input/confirmation）、public/internal project、实际Store logical identity、原host/Session/generation与真实dispatch引用、当前origin profile、原snapshot ID+revision+dependencyVector+完整definition-set manifests、参数原body/ref、source/raw-content refs+实际length/SHA+options/domain、input/source原byte-preimage refs、完整definition/Catalog canonical材料refs、实际producer implementation/锁、original input availability与scope用途。

trusted_admission必须由T01真实owner消费实际I06/source/definition供应后产生，不能renderer JSON重建或外部bool“confirmed”。实际源前像在调用I05前固定；Job accepted时若source不满足或预算不足，不发claim。原operation精确重试先读原context/claim，错来源/参数/锁/limits/Job绑定拒绝，不能以当前base重造。内部可信临时库/真实owner可单独联验，但物理位置/native未到时正式入口仍关闭。旧unversioned Job原字节/hash不改，仅此新profile分支需新typed context；缺版本的旧结果普通历史仍可读，strict消费返回unsupported-profile/缺来源而不补造。

### T01-S2：同真实owned worker的versioned有界制品通道

当前protocol.decode_frame与LIMITS.maxFrameBytes均262144，不能整帧塞B≤8MiB/Q≤16MiB、也不能把8MiB rows门当实际worker可传。选择**保持帧硬界，扩一个私有worker profile** `i05-owned-worker/1`，T01唯一维护worker/coordinator；不启公共3新能力、不复制matcher。原test.* request/ready/rounds保持旧分支完整兼容。

新请求头绑定真实jobId/operationId/dispatch实例关联、immutable context fingerprint、snapshot/source/definition/Catalog/参数/implementation/原编码role manifest以及本次实际limits；数据role为 input-preimage、source-preimage、payload-json、rows-json、original-allocation/capture（收发方向由phase限定）。chunk exact字段至少 `profileVersion,jobId,operationId,phase,role,ordinal,totalBytes,chunkBytes,sha256,data`；base64每块原bytes≤65536，按 `4*ceil(n/3)` 加完整envelope先界，encoded frame仍≤实际maxFrameBytes。source_content的128块是单role 8MiB缓存门；Q总16MiB应是两个各有界role，不把它错当单role16MiB或放大旧缓存。

严格连续ordinal/expected role与phase；重放、错child/Job/operation/context/长度/截断/duplicate/end后数据拒绝。parent先完整接收并复验所有role长度/SHA/原metadata，原计算成功complete+正常exit且原Job仍running、期限有效才可提交；不按ready前缀发布。不能让worker打开Store/传数据库路径，不能由引用强迫其从第二连接拿source。发送/接收JSON/base64/哈希/拼装/暂存、inflight pipe/raw副本/retired child均另设先计费预算，不归pure restore R或旧16c三池；原L只能来自一次实际I05 allocator切点，非新worker的默认重新分配。

### T01-S3：同事务保存真实capture身份和结果终态

拟 `finish_profile_read_job(jobId,*,owned_capture)`，只从本Job真实owned通道消费一次成功capture；T01对原Job/context/implementation/source/defs/Catalog/参数及实际L交叉绑定。完整post-compute provenance选择保在**既有唯一Store**的不可变metadata中：`job_details` typed `i05-profile-result-provenance/1` + `job_results.projection` 私有ref，避免改旧immutable jobs.context；public result_get改为显式白名单原三projection字段，不能把私有ref通过现 `**projection`直接泄入strict17字段DTO。大metadata分块只可走同Store现blob机制并永久标history-evidence，不新增平行receipt权威。

provenance完整字段至少 version、真实Job/operation/public/internal/library logical identity、原context fingerprint和dispatch关联、实际成功producer身份/锁、源/定义/Catalog/参数/输入域及原前像 refs/lengths/digests、payload/rows原bytes refs/lengths/digests、actual original rule IDs/disabled IDs/ordinal/各child完整17L（或永久metadata ref）、N/F、capture/schema/budget/cache versions、实际resultId与成功stateVersion。SHA仅完整性；authority来自唯一真实owner事务/claim/context/capture通道，不由同处可改payload或来源布尔签发。

所有artifact intern/readback/provenance/result/job_results/current更新/Job.succeeded必须同外层事务。取消先到、失败、exit非0、截断、超限或late/撤权不能留可供selected的半结果；终态成功后响应丢失只能读原Job/原结果，不重算。SQLite结果payload可回收但metadata/capture原L/Job/claim/receipt不可回收；若现job_blobs不可删除不能直接实现source GC，T01须另给同Store role-aware lifecycle/schema最小变更，不把此推荐误称已实现。

### T01-S4：完整selected恢复输入供应与租期

拟 `open_profile_result(result_binding,*,current_scope,limits)` / `close_profile_result(handle)`，只读已实际succeeded且原resultRef/claim/provenance闭包一致的历史/当前结果；原版本锁不匹配、来源不全/回收、撤权、cross-library/project/operation/result、无原capture皆有限拒绝。caller不能传expected/actualL来覆盖真实记录。

T01返回真实owner持有的私有租期句柄及完整data-only provenance与四role原bytes（或受控流），I05从该独立原记录建立pure RestoreExpectation/OriginalAllocation；原definitions/Catalog/source/false-true载体与版本都应由同次capture对应，不能从当前定义或payload反推。它不同于display result.page；返回的artifact不会注册第二public schema或颁formal authority。当前权限门在内容读取前；historicalSelectionRequired保持明确历史选择。新worker恢复原batch、逐原L调用16c后才供selected只读投影，不重新执行reason。

同事务获取必要source/artifact read pin，读者保留全部完整bytes/PV/缓存并入唯一T01 owner资源账；撤销/窗口关闭同步fence新读，实际在途/退役资源终态后才释放。缓存key含完整原来源/Job/capture/impl/参数/全部原L和selected identity，按完整结构核相等，不只hash。配额满可有限拒新读，不能逐出历史receipt或活跃/未释放的原源。

### T01-S5：原操作只读对账和永久排空

当前operation_get仅marker（1210–1225），queued/readJob即使已有claim也可null；不得当notAccepted。已有固定 `0a03539…` C2只是42685B方案，尚无operation_evidence.py产品。请求复用其“从唯一claim发现Job、原完整request/implementation/limits、snapshot/blob/prepared/confirmation/terminal互证、同conn只读预算”的拟接口；原host/Session没有持久时返回not-recorded，不补归因。正式resolve仍须真实原dispatch物理绑定/current_scope，否则unknown/physical-binding-unavailable。

main/engine.ts完整cohort/permanent stopAndDrain仍是T01在准备的独立方案；请求具体给真实Supervisor generation/session原dispatch、所有新/旧/待spawn child与stdio/timer终态，不能用stop():void、RPC promise、pending=0或kill返回作释放来源。I05只消费其未来真实owner接口，不抢写engine.ts/worker。

## 7. 有限错误、兼容与真实验收

沿现canonical已有ID/request/state/resource/cursor/payload有限错误；新profile需要区分并由T01唯一schema冻结：`unsupported-profile`、`origin-not-recorded`、`source-unavailable/evicted`、`implementation-mismatch`、`capture-incomplete`、`identity-conflict`、`permission-denied`、`resource-limit`、`storage-failure/busy`、`cancelled/late`，不是本调查新注册的wire码。corrupt不可映正常evicted，缺source不可伪success，逻辑库内有claim不可当物理dispatch已证。错误不含SQL、raw路径/文本/traceback。

未来验收必须由原实际Job→唯一worker真实计算一次→原capture→同Store事务成功→新解释器从原Store供应恢复→selected完整读回，不能手填batch/expected作链输入。正向至少完整false/true/disabled槽、全部原L、跨child排序/完整source、合法空batch/大源和原规则定义；两次计算或替代原L应使测试失败。

负向覆盖原claim/capture/ref/锁/版本/全源最后字段错配、复制库/跨项目/operation/phase/late chunk、源/结果回收、响应丢失后原operation对账、重开不重算、取消/失败/超限前后各事务断点无可见半成功、权限先拒内容、真实低预算±1、退役child/stdIO/pin未释放仍占账、窗口切换旧generation不可再投影。现145/23exec保持原证据，不重跑充新链；新组合预算/协议/来源变化后按新候选验证，再由T03唯一build owner包内运行同一真实Job样例，目标平台/真实UI/指定双方/CI/合并门另外保留。

本调查没有对这些新矩阵运行任何产品；所有供应请求仍须根批准精确writer与T01相应交付后才能施工。
