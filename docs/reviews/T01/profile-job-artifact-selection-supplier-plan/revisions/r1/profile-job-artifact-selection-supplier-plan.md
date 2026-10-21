# I05真实Job、制品角色与完整选择租期的T01供方方案

建议供应同一条真实链：**原Job受理固定物料 → 同一owned worker一次I05计算 → 原Store一次事务保存来源/结果/终态 → 新owned worker逐原artifact严格恢复 → 同consumer U/D的完整selected查询或SHACL → 实际drain后释放**。先做内部真实临时JobStore3切片，正式位置/原dispatch/current_scope仍由I06唯一owner供应。本稿是合同准备，不授源码采用、schema迁移或运行权，不把缺供方改为永久unsupported。主线另派独立审查；作者不填写审查通过。

## 1. 固定输入、实际调查及职责

本次唯一写旧C1树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core` 下本主稿和 `docs/reviews/T01/profile-job-artifact-selection-supplier-plan/`。开始HEAD为7753666d2cfda48c76ce59fa1ad6f34802c48eed，只有受保护AGENTS修改，index为空；不stage、commit、创建产品树、改Goal或发其他聊天。原ontology/dispatch/C1/C2及全部产品/环境只读。AGENTS15852B/78df2825…与common17891B/e437121a…已读，包括完整第九节和无桌面约束。

根准备授权8800B/SHA256 `8957aa0a482d6ead8b7426d0ebf13b5d4faedf3f9ce156b17ad44d6997acdcad`、I05固定a3592837d854628948ef4c468b6c839f21763273主稿69523B/`23a4ae9f7974185db61664fb1db892586140ea20995f1bb5950943717bd0ed4c`全部219行、根独审35841B/`ac6934f2b2e842aad90cba252835629064ae4ee06452892f3f4f551a774c6909`全部168行和9754B/2517a322…实施授权均全文实读。原SB/CPS/OL方案问题关闭不等新代码运行通过。I05当前另树九writer/139候选尚未固定回供，本稿不读其WIP。

`source-manifest.json`逐135项对根固定清单38921B/bb2519d2…真实Git bytes/SHA核同，包含52个423b C1组件、3ef I05/T05、T03和基线依赖；不是wholecommit或产品采用。它明确旧C1当前不具有部分I05路径，不能把旧树current假称135已装。既有owner调用图41函数起止逐AST核同；新 `static-call-inventory.json` 对19固定源码、530函数记录词法调用位置，不import/执行产品，不把AST边数当动态全闭包/费用证明。初始错误路径和未匹配glob如实保留在工具原件，不计产品失败。

| 实际固定切点                                               | 已有事实及必要扩展                                                                                                                                       |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 423b JobStore.create_job854–1013 / _accepted_job1015–1078  | 原事务先全库claim，再snapshot/参数/依赖/implementation，写immutable context+queued+claim；需在同一原受理内加typed semanticInput，不在wrapper前后另签来源 |
| _dependencies742–774 / _definitions725                     | 已核reasoning kind、同snapshot、payloadavailable、重叠manifests；definition当前只提family/id/version/references，不是完整RuleSpec载体                    |
| finish_read_job1274–1284 / _publish_job1516–1604           | 原result+terminal同事务；rows先canonical再界，不足新制品写前费用；原Store.publish每次UUID，不用摘要代原Job                                               |
| result_get1610–1645 / _result_rows1720 / collect_cache1978 | get只17字段且展开`**projection`；page先读完整rows；原cache不认识role/pin。需显式白名单和私有reader，不能拼page当严格原bytes                              |
| coordinator.dispatch333–460 / execute551–754               | 非test正式仅changeset；stdin写一次即close、stderr DEVNULL、ready/complete后stop读者，不能承载新duplex/ack或证明尾流终态                                  |
| worker._execute211–255 / protocol                          | worker只test；原262144帧/32层/安全数及owner监测保持。新branch须真正调用I05新API，不搬旧C4语义worker                                                      |
| storage.snapshot1208 / _state / _project_snapshot1234      | 当前先完整组装/JSON解码；新source必须SQL前门先界，再调用/复制并付原深helper费用，不能先snapshot再收费                                                    |
| Store._definition1014 / domain_changesets.supported110     | 旧definition opaque，正式只ontology/manual；完整rule/query/constraint保存确认是必要writer，不能仅新profile_jobs包装                                      |
| job_blobs / job_details / jobs.context触发器               | 原输入、Job、claim、details历史不可改删；新可回收role不可塞旧blob后宣称能GC，也不改context补原L                                                          |

PRD FR006、400–505、附录C/D/G.2对应原文已读。原一阶段RDFS→独立规则、保存序无关、完整解释/SHACL真实报告、外联拒绝、历史不可变、完整FR/57P0/C–G/10–12、数学M1/原83和目标平台/真人/指定双模型/CI/develop门均沿I05固定合同，不在本供方切片降低。

## 2. 唯一版本序列、树及完整采用边界

未来拟新5f树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-profile-job-artifact-selection`，branch `feature/weekly-t01-profile-job-artifact-selection`，基线5f910b52c69d86a1076b2032e5d3c63e715947f3；本轮不创建。初始只读135与根I05清单一致，逐路径原Git采用后才可装独立环境。resources初始严格3ef2927B/2361c55d…版，仅多private semantic_identity；IMPLEMENTATION仍i04，LIMITS/resource_manifest不改，不转resources维护权。

拟接口版本固定为 `i05-profile-job-context/1`、`i05-owned-worker/1`、`i05-profile-origin/1`、`i05-profile-selection/1`、`t01-profile-owner-cost/1`、`t01-profile-cache/1`。I05 computation/fullview/input codec版本由其实际固定回供，不能用同名版本猜字段；代码/锁/profile/codec/schema/budget/cache有任一变化，重出整组合manifest及适配结论。原计算pure formal_authority/aggregate_recomputed不变false。

与ontology7753666统一维护：其entityMetadata profile2、ontology sourceBinding/v2 job_plans与新profile rule/roles进入**同一Store catalog演进表**，不各树改一次schema_hash、并造两个新迁移。建议顺序：固定C2及dispatch真实产品 → ontology profile-aware只读/共享深meter原语 → 根决定metadata profile与本S1–S4合成catalog → 根唯一迁移窗口 → 两类真实Job各自原namespace联验。若S1先交内部无metadata正例，可先固定单一合成profile的子集版本；以后功能增加另显式升级，不能在旧相同hash下静默加语义。

拟合成descriptor为 `T01-store-profile/3`，精确包含原app DDL/trigger、Job DDL/trigger、新role/cache DDL/trigger、`entityMetadata:1|absent`、`profileRule:1`、`semanticJob:1`、`profileOrigin:1`、`ontologyPreparedProof:2|absent`的已批准枚举及reader语义版本。descriptor完整内容及新hash在实现冻结时由唯一format3 writer给，不在方案伪填未知SHA。不是让caller选择任意feature位。app_format.schema_hash以该完整descriptor签名区分新profile，job_format.schema_hash也含实际Job+role schema；旧固定validator的严格hash比较因此拒绝新库。app原列/CP schema1和migration_id/source_format/backup_hash保持，不改C1 libraryEvidenceRef。是否保留app/schema_version原CHECK1并扩签名语义，须根与ontology既有提案一次批准；若要求catalog2，改成一份真实DDL/备份迁移而非两个方案各绕一版。user_version仍3只说明物理格式基础，不认证新语义。

还需覆盖真实开库前门：Store.__init__在_migrate/format3.validate内即可能扫描全部snapshot/history，JobStore.__init__随后_validate_job3又逐claim调用_accepted_job。不能等ProjectHostReader或profile adapter创建后才计费。新profile只在最小catalog探测识别后、任何全历史解码之前，于同连接建立一次有限startup admission（原schema/row/bytes/work界与本配置交集），向原两个validator传同owner深meter；失败关自有DB/lease保首因，不改旧格式打开路径。显式迁移备份原migration_backup含target.read_bytes整文件hash；新profile升级须在原位置权限下先核实际文件/备份硬界、按固定≤1MiB buffer流式hash并预付全文件扫描，不以逻辑16MiB cell估计整个SQLite物理文件或WAL。原备份成功/fsync/不覆盖/源变化拒绝合同保持，额外文件/备份费用与首IO权由真实位置owner另授。

新代码双分派：旧profile1/Job3按旧字节、opaque和旧context精确规则读；新profile按完整descriptor及真实origin解释。旧format2默认不自动升级、不启profile Job。原marker/snapshot/plan/context/claim canonical、JOB3_HASH/SCHEMA_HASH常量的**历史含义**不重算成新值，校验分支按实际catalog选择各自固定值，不用“兼容”放宽旧比较。

升级在真实位置/备份/原writer租约、所有profile/ontology active与retired清空后进行：先有限全历史预检和SQL/schema核同，再同一外层事务建新表、受控更替catalog immutable-update触发器、更新签名并恢复完整触发器，写后全验证，任何失败回滚DDL/catalog。保原历史和migration_id，不迁移倒填任何旧Job来源。备份仍由正式原位置供方提供；内部临时库未来可验证机制，不能造生产备份权。

## 3. S1：原事务受理与真实每能力身份

建议 `JobStore.create_profile_read_job(..., *, admitted_material, owner_scope, cost)` 是原create_job同一实现的精确私有分支。不是先create普通Job再UPDATE context，也不另建claim/receipt/intent表。拟`Coordinator.admit_profile_job`内部入口消费实际owner对象后调用原create_job并走原queued/execute调度；它在实际Coordinator初始化时与已开JobStore绑定的私有owner登记取用，不能由参数布尔/任意JSON构造。内部配置只选择已批有限工程profile，不签I06正式用户权限；原公开dispatch不因这一私有入口自动放开semantic capability。新增私有参数不能由JSON反序列化制造。旧六字段jobInput和原普通Job DTO保持exact，公开入口在I06真实原scope/dispatch/位置供方未到前不开放。`test_mode=True`不作语义准入开关。

实际安装provider resolver在 `project/profile_jobs.py` 维护：只允许静态名单的reasoning.execute/query.execute/validation.execute及固定I05 profile provider，读取真实已装模块/T03源包manifest与锁、检查完整相对path/size/SHA集合，再调用只读resources.semantic_identity(profile=True)并核三字段相同。resolved descriptor含代码manifest/包身份/锁/profile/codec/capture/fullview版本；不信child自报implementation，不动态import调用者路径，不把parser identity当whole engine identity。health/startup仍原i04，不能全局替换IMPLEMENTATION或复制常量。

原事务次序：

1. 校私有exact request与owner用途、当前权限和真实Store能力；未准先拒内容读。对已有operation先原claim→原Job/context互证及同一私有原semanticInput identity，精确重试只返回原状态，不向当前snapshot重发配额。
2. 新operation在同connection预扣schema/SQL/read/canonical/material准备费用，核目标原snapshot与完整参数/定义/来源，不能在此之前调用无界snapshot/load。源材料先有界，再codec，不执行matcher/compile/evaluate/PV。确认来源和policy不足时，任何新claim/Job/材料行均不留。
3. typed semanticInput与完整普通context一次canonical后成为原fingerprint；实际Job UUID分配、role manifest和Job角色chunks、queued DTO与claim同一原事务落库。全库occupied-operation和原create/application冲突检查不变。
4. 接收前预留后续start/cancel/fail/terminal独立控制份额和持久增量，注册不可重置consumer账户及owner pins；提交失败撤回内存预留和SQL新行，已经执行的读/扫描工作不退款。COMMIT后响应丢失沿同operation发现原Job，不二次计算。

semanticInput exact字段组：version、mode(producer|consumer)、providerDescriptor、原public/internal project/libraryLogicalId与catalog descriptor、原request/operation及普通input、原scope用途和实际ownerGeneration/dispatchRef（正式缺失明确not-recorded）、sourceDomain、snapshot identity/revision/vector/manifests、原parameters ref/bodyDigest、parser/options/table材料身份、role manifests、consumer分层U/D身份、完整ordered selected IDs和明确historical选择、feeProfile/quota配置身份。JobId在原row/DTO，role manifest同事务绑其实际ID；不可用hash循环自引用，context manifest不包含自身fingerprint，通道另携原已生成fingerprint。原L不在受理时猜，只有成功计算后capture进入origin。

旧 `_accepted_job/get_job/job_context/_validate_job3` 必须按精确新version验证该扩展和角色manifest完整关联，拒unknown版本、额外键、错project/request/参数/锁；旧context没有字段则沿旧路径，不能因旧opaque恰似新形状认证来源。丢失cache内容不抹已受理claim或原context真实性；重试可返回原failed/succeeded，若要内容另走有权限的availability判定，不重派已终态Job。

受理context还固定admissionCost：每原artifact的可信B/Q/N、Rcap矩阵及Σcap、C/T/S上限、隔离的start/cancel/finalize/retry份额、pin和持久增长预留。生产受理没有actual原L，不能预填；只可按真实typed定义数界槽数、按工程界留输出，selected才取原origin actual L。正常success origin保存实耗/peaks；失败若保存有限费用摘要，必须在同一原失败终态事务及F预留内写typed详情，不能另开侧交易。异常进程退出前未落盘usage明确unknown，不补零；原Job终态或reconcile禁止重发该Job账户，不能借丢内存免费重试。新合法Job另经claim/费用/历史/名额准入。

## 4. 所有K的U/D、原物料及RuleSpec完整写链

U是**本consumer原snapshot**的assertedRecords/ontologyRecords/input/source，不是producer Q，也不是D或derived图。K=0..32均独立固定U≤16MiB（input/source各8MiB），query/shape及相关definitions D≤8MiB。producer原input≤8MiB（Turtle原UTF8仍1MiB）、Q=input+source≤16MiB、其D≤8MiB。空图也用明确的非空canonical空分层body，不能把U=0作为缺物料的默认。

owner源前门采用两阶段：SQL先按完整真实行typed计量探测rowid/PK、原TEXT UTF8/BLOB长度、固定列数/数量，再预扣整行读取/JSON词法/depth/node/复制成本，最后读正文和精确decoder。snapshot原raw单行拟≤16MiB、深度32/节点≤1M；所有相关现有ReadLimits/schema/表列/全库bytes/work较紧者另交集。不能先SQLite提取巨大JSON value或fetchall全payload再计费；未知SQL模板/历史shape先有限拒，不让旧深helper无账运行。Python新字段先exact容器/标量和有限len，再预付Unicode scalar校验及UTF8最坏4×char、JSON转义最坏6×char和固定分隔，实际计入后归还未执行保留；禁止先整canonical/encode巨string后量长度。需要新当前snapshot时，先界_state各真实行及原canonical最坏输出，再在同原Store.snapshot路径执行；复读/规范化也另计。不是另造snapshot生产者或替换real._db。

固定423b源码有重要语言边界：rdf_snapshot.term会lower language并重建Literal，Store._fact要求object等于该term的n3；因此不能声称从旧N3恢复用户原输入大小写/数值词法。选两个明确源域：

- **snapshot-records/1**：真实Store原持久行，按照其原顺序id/definition顺序取全部实际asserted与ontology记录，data-only扫描原N3语法产生TermInput，保留该原持久文本中的词法/语言拼写，不经Graph/rdflib.normalize重建。SourceRecord是新明确snapshot ID+JSON-pointer locator、原行digest/revision和原文本；它说明当前原持久记录，不冒称历史用户文件或单元格。None/空串保原材料语义，不填伪span。重复support仍逐原行保存，不先set去重。
- **utf8-turtle / mapped原文件**：须实际源owner供应原UTF8、已接纳scope、内容/row-column/transform/options及parser实现身份；Turtle原source.digest绑原raw且text遵原65536门。新profile不能把source_content ref/tableDigest当权限/原parser证明；旧历史源或原语言已失时明确source-missing/coverage材料。完整源接线列真正I06/T03/T04供方门，不能永久用缺失返回替代目标。新材料一经供应，其五/四字段及原序必须不再损失。

新 `project/profile_material.py` 只管Store前门、真实locator/source映射和strict codec编排；TermInput/SourceRecord/RuleSpec canonical格式复用I05实际固定data-only codec。N3扫描若I05最终codec没有该入口，T01只写所需有限原Store语法adapter，不复制quality数值/规则parser，不用Graph反造；精确语法/代码费用须独审后固定。映射owner/source_row不能作为已有完整原文件proof，缺列位置必须如实标明。

规则选择现有definitions层唯一home：family=rule的payload为strict `profile-rule-definition/1`，字段enabled(bool)、rule_id、when/ comparisons/heads原tuple序、source四字段或None、revision、definition_digest、policy及references；Variable/Triple/TermInput各位置exact。enabled不塞进原RuleSpec假字段，作为定义启停记录供应原allocator disabled集合；原policy只能已采用固定profile，不收任意Python/callback。rule ID与definition ID明确互证，不排序改原when/head/comparison顺序；新definition_digest以固定`profile-rule-content/1`域对除definition_digest本身之外的exact payload字段（含enabled/source/policy/revision）canonical求SHA256，不造自引用hash。revision由原Store该home真实下一版本在原预演固定并在commit后逐值核同；旧任意revision不冒认为该Store版本，历史保原值。实际规范化/ordinal/disabled仍由I05一次计算捕获。

真实创建/编辑/启停/复制/删除经原typed ChangeSet preview→完整Diff与全部页→明确confirm→原changeset Job→Store.commit；无需用户再次确认单纯只读reasoning，但定义改动不能从语义Job参数偷偷保存。必须扩展Store._definition、domain_changesets.supported/_definition、transactions/state_diff、compensation全量before/after及应用combined path，触及rule/query/constraint strict union与完整references/失效vector/manifest。查询保存含真实text/scope，constraint保原有限模板；现unsupported family不是可以只靠opaque Store写绕过的门。所有入口包含删除/载体替换/undo均核新profile和真实已确认plan scope，不另建rule plan/确认账本。

为防与ontology的已审v2命名空间混接，新profile定义计划申请原job_plans中的严格 `preparedChangeSetVersion3`，domain固定profile-definitions、`profileDefinitionSourceVersion1`真实sourceBinding，包含原project/revision/snapshot/vector/manifests/CP、完整定义/原材料身份及cost版本。previewHash另用`profile-definition-preview/1`域，原storePreviewIdentity与marker fingerprint不改；parameters/confirmation分别严格version3、cursor kind为changeset-document-v3-profile，并绑planRef/sourceBinding/host/session/完整Diff manifest。v1普通domain和v2 ontology保持各自exact历史结构，v3不能通过v2 validator或v2 completion游标，所有分派在同一accepted_plan/confirmation/history入口完成，不复制第二套宽松validator。新confirm/新Job接收/首次commit都在各自原外层事务内复验current source，已受理重试/已提交receipt只验证原historical来源；undo为新当前source的新v3预演。v3第一窗口只允许rule/query/constraint与明确manual样本事实，不混改ontology metadata；跨此集合的原子编辑另需root组合proof审批。Store低层写gate、combined/application与补偿路径也必须核同该真实原plan scope，不能只在支持表放行。该v3是本供方请求，须根在唯一canonical窗口与ontology实际v2实现一起批准；不得按本稿改掉冻结ontology方案。

旧 `{enabled,when,then}`/opaque rule按显式旧版本读取，不猜comparisons/multihead，不能冒认为新RuleSpec；新profile第一批定义从真实用户/Store确认材料建立。升级前全历史schema定位扫描新的保留namespace、Job语义context、projection/private origin discriminant碰撞，与ontology entityMetadata碰撞策略合并：旧opaque保真、碰撞/未知覆盖则拒本次升级，原件不改。确需保真迁移另交根批准，不静默删键或认证形似值。

## 5. S2：同一owned worker的lowercase hex角色通道

在原worker.py的私有profile branch调用唯一新I05生产/selected API；原test.* request/ready/rounds分支行为保留。新增 `profile_worker.py` 管严格通道和同次数据转交，不开Store/路径/网络，不复制matcher或另开toy进程。coordinator维持同一owned child/owner monitor/memory guard，120s/512MiB、原queue/concurrency/phase较紧门不升。

parent的stdin改为此branch全阶段保留的duplex控制流；stdout是role/ack/control数据，stderr改为受限且不泄露原输入的独立drain（允许仅计数丢弃，无无限日志缓存）。不是仍close stdin后幻想child收ack；三流的实际关闭及读任务终态均登记owner。root先固定dispatch实际drain接口后再接父engine cohort，不能借旧stop(void)证明已放行。

每raw chunk≤32768、lowercase hex≤65536；固定exact header canonical≤4096B（包含完整JSON键/引号/分隔/data字段开闭），LF另1，frame≤69633≤min(实际maxFrameBytes,262144)。header字段为固定type/version/phase/role、原Job/op/context fingerprint、dispatch owner generation、producerResultId/index或null、ordinal/byteOffset/chunkBytes/totalBytes/chunkDigest及data。安全整数先exact-type/范围；原L/大精确数按I05声明canonical unsigned hex传递，不先JSON大int解码。digest与ID先固定长度/Unicode scalar，unknown/extra字段拒绝，不让foreign len/iter/hash进入。header若实际较大先拒，不分配完整角色再发现帧超限。

生产parent→worker：input-preimage/source-preimage/definitions-material；worker→parent：payload-json/rows-json/capture。selected parent→worker始终有consumer-input-preimage/consumer-source-preimage/consumer-definition；再逐有序producer送origin/payload-json/rows-json/input-preimage/source-preimage；worker→parent为consumer-output。role=origin是原Store reader的完整typed P，不能让child capture覆盖。生产6 roles；selected 5K+4 roles，逐role-begin传manifest，不将K32全部清单塞一帧。

phase/role方向固定，只有一个未ack raw块。receiver在任何JSON/hex decode、append/copy/hash前从自己actor T/H预付；逐原chunk长度/ordinal/offset增量hash，sender仅在匹配ack后发送下一块，最后role-end核完整长度/SHA；空role零data块而有begin/end。错phase/role/Job/producer/index、重复/失序/截断/不规范hex、非0pad概念替换、end后data均有限失败，不重发双扣或静默去重。ack丢失按同deadline失败，不reset totalMs。完成后仍读到真正stdout EOF、无尾字节或未完成frame，不能调用旧reader.stop忽略同一chunk尾部；必须complete一次、全部预定role结束、正常child exit0，才可能进入成功保存。

数据暂存固定为owner有界内存；child不能开DB、HTTP或另个Store。每阶段一role、一个inflight frame、一次只恢复一个原artifact，但完整K已转交Graph/view及parent原材料继续H计持有；最终bytes(bytearray)的双buffer提前同时留票。跨actor不借同一份票。大物料在实际H/时间内不能完成则资源失败，不能放宽原帧/内存/时间门。

## 6. S3：唯一Store的typed origin和角色schema

新增schema只有派生cache及其可用性状态，不另建receipt/Job/claim真相：

| 表/原位置                                                                                                                   | 精确用途与生命周期                                                                                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 新profile_job_payloads(job FK jobs, role固定enum, ordinal safe nonnegative, raw BLOB NOT NULL；PK(job,role,ordinal))        | producer input/source/definitions或consumer input/source/definition实际原bytes；受理与Job/claim同事务写。UPDATE拒，DELETE仅terminal+无active/retired pin的原GC；queued/running不得回收 |
| 新profile_result_payloads(result FK results, role enum(payload-json,rows-json,consumer-output), ordinal, raw BLOB；PK(...)) | 同成功事务写原B或consumer O；UPDATE拒，GC同owner全role原子删除，不能留下冒充完整的前缀                                                                                                 |
| 新profile_cache_state(owner_kind enum(job,result), owner_id, status enum(available,evicted), manifest_digest；PK(kind,id))  | status只available→evicted，拒恢复/覆写manifest；原rows缺失或manifest行缺失不自动认evicted，需实际成功GC状态互证。多态owner必须代码与schema约束核真实jobs/results，迁移不能把孤儿合法化 |
| 原job_details                                                                                                               | immutable typed i05-profile-origin/1，含原完整L/defs/Catalog/capture与来源metadata，永久历史；不是cache，不能因空间紧删除                                                              |
| 原job_results.projection                                                                                                    | 新profile严格3个原projection字段+唯一versioned origin ref union；旧projection仍严格原3字段。不能把unknown键当旧私有扩展                                                                |
| 原results/result_state/job_current                                                                                          | 原普通rows及失效/current公式保持，payload cache可回收；新profile结果GC同步普通rows和其result roles，原source roles另有明确状态                                                         |

新增BLOB也是实际消费delta：原host全库guard按CAST BLOB长度可先界，但固定C2完整typed-row canonical计价未定义bytes值，不能直接调用旧canonical(bytes)。新catalog的C2/reader适配申请对BLOB使用固定计价投影`{sqliteType:'blob',byteLength:n,lowerHex:<exact hex>}`；SQL先长度/行数并预付2n+固定envelope上界，正文取出后才有界hex并核原digest。只在已知四表/已批准列用此编码，旧TEXT/INTEGER/NULL计价完全不变、证据每row一次而重复work照计。maxEvidence/read-work/frame总门不升。该计价对象只是本次内存证据费用，不持久化、更不改变原context/hash；C2旧版本遇新profile安全拒绝，须root另授其原两readonly模块消费适配后才能组合。

raw分块与角色manifest的ord/count/length/SHA一一相符，块默认32768；完整manifest在immutable context/origin，不把cache_state自报digest当原manifest。SQLite UNIQUE/PK、FK、CHECK、immutable-update和status单向触发器的实际完整SQL须新实现逐字冻结；cache_state owner外键若SQL不能安全表达多态，选两个明确job/result state表，而不是弱化引用。本方案首选**两个state表** `profile_job_cache_state(job FK jobs,...)` / `profile_result_cache_state(result FK results,...)`，因此新增总四表，拒孤儿/unknown owner；前表的kind通用描述只是语义，不再另建第五张多态表。

原job_blobs参数/source_content等继续immutable且算history；不能挪到可删表洗旧引用。新profile的受理大角色用新job payload表，context只保存严格manifest/ref及完整原snapshot/参数的原字段；snapshot或原参数本已含同一内容的真实持久副本照算，不为GC删旧历史。source角色回收后，origin/L仍真但strict selected返回source-evicted；不自动从snapshot或当前定义重建缺失前像。

origin字段按固定I05§6全部保存：version/mode、result/producer或consumer Job/op/project/library logical/catalog、原context fingerprint/真实dispatch或not-recorded、输入snapshot/revision/vector/manifests/参数/明确scope与选择、真实provider完整三字段/代码清单/锁/包/全部版本、source/parser/options/定义和ontology材料身份、各role原owner/length/SHA/chunk manifest、B/Q/P/N/F、actual rule_ids/disabled_ids原tuple/各child(rule_id,definition_ordinal,完整17L)、actual normalized definitions及Catalog、成功stateVersion、complete+exit的原owner通道关联。None/空tuple/disabled dummy None不归一化；原17L来自一次capture不从payload或divmod反推。P≤16MiB，内部分块若需要保存job_details多个typed永久段，原ref必须manifest闭合且所有段同事务，不能把单字段巨大string留到最后收费。

## 7. 成功保存、失败与终态控制

`finish_profile_read_job(jobId, owned_capture, scope_fence, cost)`只接该原active owner实际拿到的不可重建handle；caller bool/success/dict/worker自报proof不足。接收前确认全体角色和真实child终态；SQLite外层事务内再核原Job仍running/mode none/run NULL、cancel/deadline/current权限generation、原snapshot/来源/完整implementation和已受理内容全部相等，再一次写result UUID、完整rows、job_results/origin、cache roles、current/stale和Job.succeeded/resultRef。receipt/commit marker不用于读Job，mode none没有伪domain commit。producer reasoning origin可供strict选择；consumer query/validation只保存其原U/D、ordered selection及输出来源，不伪装成reasoning fullview artifact。

任何扫描、实际SQL写和原Store.publish深helper先预扣；依原_publish_job kind映射、rows校验/唯一rowId与ordinal/排序、Store.publish原cache_key公式、manifests/current规则，原语义不另抄一套。必须改原入口让已付scope穿透，不在外wrapper调用原无账canonical/snapshot。prepared ontology/rule写Job仍走原changeset commit，不共用读Job成功adapter。

避免“先留最坏16MiB P而history仅8MiB，导致所有正常producer必拒”的矛盾：受理时实际Q/D已有原始长度；未知B/P/O输出由可信owner在原最大8/16/8MiB之内发行本Job明确lower-only effectiveBcap/effectivePcap/effectiveOcap，同时不超过剩余cache/history/终态headroom及C2较紧上限，写入admissionCost和worker角色约束。不是提高原17L或改I05机制池，超该工程输出界真实资源失败；无足够有限非零余量先拒新受理。首个小正例明确申请Bcap65536/Pcap32768/Ocap8192，随后连续32 producer须按真实持久增长核余量。需要更大artifact的配置须根批准并取不变pure hard bound/全库guard交集；不承诺语法最大输出都能入16MiB工程库。接收前为选定effective cap和真实输入增长封存；成功只释放未发生容量，不返已执行work，不能等末态发现没有终态空间。

在入事务之前构建有界全部候选并预留持久增长、临时SQL增长峰值及原终态最大DTO；写后读回候选核同，任一chunk/details/result/terminal失败整体rollback。最终fence必须在原事务内，不能await权限后隔一交易落库。COMMIT之前cancel赢则无artifact；COMMIT后cancel已terminal返回原结果，响应丢失不另写origin或重算。

已有Job失败/取消是单独原状态交易，不能声称所有失败完整DB dump均不变。正确断言为无新可selected artifact/半origin，已受理Job/claim和真实失败/cancel终态允许按原合同改变。ownership Conflict在原_application会回滚后另txn写job_details；新profile/rule/ontology cost scope身份即使过期也不回落此旧侧写路径，改为私有有限冲突，不能用假detailRef或预算耗尽错误绕写。旧无scope分支保默认。

复用ontology已审TailReservation理念并为本read模式另冻结：受理前分别封存一次start、一次cancel和唯一owner finalize的不可侵占terminal floor，包含get_job/context/marker探测、全部原state helper、完整最大error/finishedAt/safe时间戳/版本和控制SQL。重复start/cancel/失败重试先走独立至多8次有限read份额或入口拒，不吃F_terminal；业务过期或额度耗尽不释放F。finalize票不是公共API重新发行，真实SQL已花不返，I/O失败不假terminal。profile read严格run=NULL，不借rounds/run_terminal支路；异常非NULL是结构失败。重开queued/running/cancelling由原reconcile在新有限control admission内标failed/cancelled，不恢复内存ledger自动重派计算。

每层原_transaction入层前保外层最多3控制execute、内层最多4（SAVEPOINT/RELEASE尝试/失败ROLLBACK TO/最终RELEASE）；最大depth8、每phase总入层16、phase封存63控制槽/16128work，计总65536，不仅预留BEGIN/外ROLLBACK。业务耗尽/未知SQL/过期不阻合法owner栈LIFO清理；未知外caller事务先拒。清理失败保首因并尽力外ROLLBACK，健康SQLite预算故障须in_transaction=False，真实I/O失败不能伪证明已清理。Tail三份的控制已计其64槽，不在每份上另叠63扩大总额。

## 8. 公开结果、分页与历史兼容

所有公开投影显式白名单：job DTO原字段、result.get原17字段、result.current同17或null、result.page的binding/普通rows/nextCursor、job.list/subscription及operation.get的原固定形状。job_details/detailRef路由只允许原已注册类型，不透传新origin ref/P/角色表/源权限材料；错误与通知不带raw/path/SQL/traceback。get_job/job_context内部新增semanticInput仅私有，不能通过notification或`**context/projection`展开。

result_get新profile仍逐名取definitionId/scope/parametersHash；不复制旧`**projection`。旧普通rows/page/cursor的200项/131072B/262144帧和完整binding/TTL/顺序保持。新私有reader不调用page拼payload；普通page全payload读也要在新profile source scope下先计，不把display分页免成免费正文通道。

结果普通payloadStatus继续指display rows存在，source缓存另有私有availability；source角色evicted可仍看原有普通rows，但不能selected。清result roles时与ordinary rows同txn清、状态和current指针一致；损坏、原manifest缺行、无合法evicted状态不能映成正常evicted。旧结果无origin仍可看旧metadata/普通历史页，新strict选择给origin-not-recorded；不倒填来源或把旧finite6当finite7。

私有fault区分unsupported-version/origin-not-recorded/source-missing/source-evicted/payload-evicted/corrupt/permission/identity/resource/busy/storage/late/cancel。公开适配只用原canonical已允许code/params：permission→PERMISSION_DENIED，artifact evicted→PAYLOAD_EVICTED(resultId)，缺来源/损坏→INVALID_STATE或STORAGE_FAILURE，身份→IDENTITY_CONFLICT，资源→RESOURCE_LIMIT固定semanticInput/semanticResult/semanticWork，busy按原retryAfterMs。NOT_FOUND.resource原enum没有source，不能塞`resource:'source'`；诊断细类只在受限内部结果/测试证据保留。确需面向用户独立错误码再单路径申请errors/schema/fixture，不临时放宽extra字段。

## 9. S4：完整selection、reader及同Store pin/GC

接口为 `open_profile_selection(consumerJobId, *, owner_scope, cost)` / `close_profile_selection(handle, actual_drain)`。有序IDs只来自原consumer context，不收caller expected/L/任意子集；exact0..32且重复拒、33拒。K0照核原U/D和本consumer权限，非空asserted及ontology基底都能走真实query/SHACL，不伪造一个空producer。

新operation受理时，对完整选择先逐metadata闭包核原producer→result→Job→operation claim→context→snapshot/params/manifests/implementation/origin/actual capture和cache availability；先权限再内容。保423b现门：kind reasoning、producer inputSnapshotId严格等consumer inputSnapshotId、payload available、重叠definition manifests相同、完整implementation三字段相同；再加本profile代码/锁/材料/版本/真实binding相等。historical必须明确consumer选相应历史snapshot，不能把旧V1结果混入当前V2；policy变化另版本审批。

pin在同一原Store owner线程与一致读事务中获取，先完整校验并为全部K/consumer U/D预留pin，再一次登记handle，任何项失败不发布前缀。GC与open由同owner同步串行，无await窗口；所用只读事务不造新DB/Store或回写domain。pins为不可JSON重建的owner内存映射，K32先pin全部必需角色，实际reader一次只打开一个producer。旧pin_report排序/去重/永久report语义不用于新ordered active selection；原result_pins/current/job_current仍是GC额外保护，不能忽略。

同consumer Job只有一份账户/一个handle（queued也占已预留selection名额）；重复open只复用尚活跃的同一handle并付有限核查费，closed/failed/retired的原Job不能新开R重新算。新的合法consumer operation重新受理、自己的U/D/Σcap/usage/pins，不免费继承旧Job已付或跨JobGraph/PV缓存。严格恢复每原artifact一次，每child同原L一次16c；K32原N_total可3200，但绝不塞进单pure N≤100池。不同实际N/disabled/dummy在独立原snapshot/Job矩阵验证；若同选择现政策不能产生不同N，不能伪造allocation制造这种正例。

每原artifact R_j读全B/Q/P并从**原origin独立**形成expected/allocation，最后一个原child/result失败清整选择；S用本consumer U一次构图，再按选择及原when/comparison/head/basis/source顺序加入已验证derived。producer Q仅核恢复不作为consumer asserted底图。native/fullview/Graph按I05严格schema/TermInput词法保真转换，不重reason、不偷偷二次JSON解析，无RDFS direct-step时不把leaf union说成直接链。

GC只删已terminal且所有active/retired pin释放的角色；job和result状态分别available→evicted、完整角色集合原子清，metadata/origin/L/Job/claim/receipt不删。source job roles被多个reader依赖时按实际owner集合保护；current和report所保护结果及其required source依赖同样保护，不能只pin result B丢Q。预算不足时先有限GC无pin cache，仍不足拒新受理，不删历史；恢复被回收artifact须新合法Job重新计算原明确输入，不“修复”旧origin。

close先fence新读/Graph使用，再停止owner工作并等待真实child/pipe/native/view/reader/retired终态，之后解除pins/H。TTL仅停止新用，不是自动释放。强引用仍在异常traceback/任务closure/返回view里不能降live；转交前接收owner同时预留，释放方真drop后才转票。关闭重开后原nonterminal Job只reconcile；旧活跃process/drain证据不足时owner租期保持retired/quarantine占额，不能仅因DBwriter lease重获、PID消失或ledger live0自认全部native已释放。

## 10. 不可重置C/T/R/三池/S/H与具体有限quanta

所有数字为建议的工程准入，不是Q5默认、性能或OS内存承诺，须根明确批准配置身份后实施。配套 `budget-quanta.json`保逐式算值；未配置生产准入关闭，内部真实Job未来显式使用该有限配置。原17L/原W/I/O/F/head/trace/binding及N≤100不扩大。

C沿I05已批算法：A=Q+D+8MiB+16MiB≤48MiB，consumer准备Q=U/N=0；traversal128A+65536N、scan/copy64A+65536N、hash16A+65536N、scalar16A+131072N、objects8A+2048N+4096，原8个准备阶段逐操作有来源。Store SQL/原始读取和N3 adapter另在T01 owner前门付，不借C漏掉持久读取。第九遍或新delegate无来源先拒/申请，不能照旧加cap。

T按每actor收发实际raw总X、roles r、h=Σceil(roleBytes/32768)，n≤2h+2r+8，E=2X+4097n；wire/scan6E、copy16E、hash8E、objects64(n+r)+4096、scalar live=8X_live+262144。production X≤48MiB；selected X≤U+Σ(B+Q+P)+D+O≤1312MiB，K0≤32MiB，均为累计量而非同时内存。每phase两侧分别付，header/ack/stderr read/discard/control均有封存票，不能只付hex data。额外控制或role超式先拒，deadline不刷新。

R_j直接复用固定restore_budget.begin(B_j,Q_j,N_j)的17域cap公式，来源blob37478B/593b2a83…，原MAX_PV_OCCURRENCES131072/MAX_FIRINGS1024不变。受理先Σ_j cap按域核consumer quota；运行累计Σactual_usage、slot(j,i)唯一、失败工作不退。R live/peak向S/H真实转交，不能以max单R_j或纯ledger.cleanup清零当全部对象已释放。只按固定预算公式静态求cap，不运行matcher或从payload反推L。若I05新fullview实证需要预算delta，须其实际最终新版本及root批准后重新固定本cap来源，不暗改只读budget模块。

三池每child同原L一次：work≤3W_i+k_i，input≤2I_i，output≤2O_i，k_i=1+33F_i+4O_i+128+70+4。总和按每原(j,i)，disabled占原槽、空规则dummy有真实N1；selected不重新divmod，不借C/T/S。consumer K0没有R/16c，但其U/D的C/T/S/H不为零。

S令V=U+Σ(B+Q)，N_total=ΣN_j；traversal128V+65536N_total、scan/copy64V+65536N_total、scalar16V+131072N_total、objects8V+2048N_total+4096。实际图t先界≤100000，Graph.add/哈希/碰撞等opaque委托另预付32(V+1)(t+1)，普通term/值/词法/解释保留另按实际长度；不是把巨大逻辑上界说成CPU实测。query/SHACL计算原预算独立，不能被S覆盖成免费算法。

建议固定有限外层额度如下：

| 项              | 建议值与交集                                                                                                                                                                                                               |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R聚合17域quota  | 各域≤32×Rcap(B=8MiB,Q=16MiB,N=100)，JSON列完整向量；实际Σcap按trusted较小B/Q/N算，live cap许可与实际H限制分开                                                                                                              |
| C/T/S累计quota  | 由实际可信材料上述公式一次发行，另不超各公式按K32和原raw最大值的固定向量；new phase不能重新发行；计数internal exact int/通道canonical hex                                                                                  |
| owner SQL       | 每Job总65536（含全部probe/body/control），read-work536870912；原ReadLimits/schema/row/byte/work另交集，不放宽C2全库门                                                                                                      |
| selection/pin   | 每library最多2份已受理活跃+retired selection、每consumer1 handle、合计64 producer pins；拒新读不逐出未释放者。profile queued可能较原32队列更早资源拒，须根批准启用影响                                                     |
| retries/control | 每Job至多8个独立有限重读份额；start/cancel各一次与F_terminal隔离；控制cleanup不受业务耗尽挡                                                                                                                                |
| history/count   | 每library保留profile Job≤256、可选reasoning artifacts≤128；原不可变历史不删，达到后有限拒新受理                                                                                                                            |
| persistent      | profile immutable历史cell≤8MiB、可回收cache cell≤8MiB、两者及新profile副本合计≤16MiB；所有旧blob/context重复照计；原ReadLimits全库SQL cell bytes≤32MiB及其work门、C2 canonical证据≤64MiB另取较紧交集                       |
| H真实持有       | parent scalar≤512MiB、每worker≤1GiB、library active+retired≤1.5GiB逻辑票；每actor objects≤8388608、合计≤16777216，所有raw/encoded/view/Graph/pipe/native/退休引用入账；原worker物理512MiB及120s仍独立更紧，不把逻辑票当RSS |

persistent cell费用定义为实际TEXT UTF8+BLOB raw+每行256固定管理项，逐新/扩行/GC候选先算；原C2的完整typed SQL行canonical费用独立，TEXT转义及BLOB表示费用不能混为raw。全库bytes/work/表≤64/列≤32仍逐新完整schema复核；新增四表不能使旧guard暗放行。达到历史额度时诚实拒新Job；未来安全归档/容量调整另批，不删immutable history洗额度。

同一Store所有启用profile期间的writer都必须尊重active Tail/pins/持久headroom，未知旧writer先拒，不能通过普通put_blob抢走terminal空间。这与ontology的单一cost_scope admission注册表合并，两个profile不各算一份同库余量；未启新feature的旧默认行为保留，启用期间未知writer拒绝是明确待根批准的功能约束。

## 11. 非空正常正例与算式可执行性门

未来用真实Store确认：ontology声明Equipment/HighRisk、数值property/value和输出flag；asserted有设备a/b的数值20/5及原source，query/constraint有真实保存/版本。完整三条rule中R_true读value≥10产生type HighRisk和flag true两head，R_false比较9999为false，R_disabled启停记录为disabled。实际source/RuleSpec/definitions/Catalog/原17L全部由原计算capture，方案不提供fake batch、expected或L。最小完整链必须真实test_mode=False受理、同owned worker一次producer、同Store成功、关闭重开、新worker fullview/R/16c、真实query与SHACL通过/违规、普通分页及undo定义失效读回。

预算接受目标：每producer B≤65536、Q≤65536、P≤32768，consumer U≤16384（input/source各8192）、D≤4096、O≤8192，实际N3；K32全部32个真实成功结果，即使derived去重也逐原全恢复。role细分在JSON：每producer origin32768/payload61440/rows4096/input32768/source32768；consumer四role8192/8192/4096/8192。此是上界规格，实际B/Q/P/原L仍须真实API计算，不按这些数手填content或自签capture。

K32静态X5271552、r164、h196、n≤728、E≤13525720；S的V4210688、N_total96，按示例t≤128时opaque工作17381724192。R_j逐固定公式并Σ32，三池总上界逐式JSON。K0有X28672、U16384与非零C/T/S/H，K1/K2另列，不由空producer代图。示例cache cell不含row附加费为4325376、immutable P/context估2129920，连同原snapshot/参数/行及typed转义须实际核余量后才接收；未计项不能拿这两个小计冒充16MiB/32MiB总库证明。

H必须至少支付原R opaque_scalar541065216（这是纯预算实际封存量，不是OS实测），所以不能把外层H默认设512MiB而令所有合法恢复必拒。本建议worker逻辑1GiB让该已知预留有空间；小正例剩余native/view/Graph/新freeze的源码峰值必须实证在余量内，若不能必须在root批准新guard/必要源码优化后重审，不能只展示全拒绝测试。实际raw/source/全L/完整7/15/11字段、组数、查询/GC/失败累计、最后字段及±1都需实现后原件。静态JSON和上述算式不证明真实链已运行、120s可达或512MiB足够。

不同N矩阵另用真实仅一规则snapshot(N1)、无规则dummy(N1)、三规则含disabled(N3)、100槽含disabled(N100)各自真实consumer相同snapshot联验；不把不同snapshot的结果混进同selection来强造不同N。实际跨producer不同N若canonical原policy确实允许，才另给真实材料正例。

## 12. S5：claim对账、真实权限及drain接口

当前可引用的固定文档是C2 0a03539a44c43fafb2f890953bbb59a77ea33a05（42685B/e7db89cb…）及dispatch 506e15744e47fd36f43bdbd645f6e65526cf0bf4；它们不是本轮可采用的新产品。主线C2/dispatch在另树实现，只有其最终实际product ref/完整路径/bytes/SHA/验证经root回供后，才能替换closure受影响路径；不读或复制WIP，不凭方案名字宣称已有函数。

所需固定接口：

| owner                 | 最小版本化接口/输入输出                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T01 C2                | 固定方案原名`read_operation_evidence(real_job_store, selector, *, maxEvidenceBytes, maxSelectorBytes, maxReturnBytes, readerLimits)`保原新readonly txn/同conn严格原helper门、claim→Job/context/完整snapshot/参数/plan/terminal/result互证；新增profile origin/role/current-head完整schema适配时另精确授权。返回原evidenceVersion1 bounded finding及originEvidence，profile仍not-recorded直到真实原来源合同另批；不得把新origin表存在自动改recorded，更不能生成resolve authority |
| T01 dispatch owner    | 原真实call关联handle含ownerGeneration/engineSessionId/dispatch ordinal、request/Job/op/context、settled response或lost/unknown、可观察实际child/三流/starting/timer/listener terminal facts；签发来源是原调用，不收caller reconstruct JSON                                                                                                                                                                                                                                      |
| T01 cohort            | `retire_profile_owner(handle, reason)`先fence；`drain_profile_owner_v1(handle)`等待所有active+retired/starting spawn、engine/worker实际process及stdin/stdout/stderr、timer/listener/tasks/native/reader/view终态，返回bounded drain facts或still-pending；无success默认                                                                                                                                                                                                         |
| I06唯一权限/位置owner | `ProfileScopeUse/1`不可重建borrow：真实physical+logical library binding、public/internal project、原dispatch/current permission generation、用途/expiry/fence及同事务最后复核；`drainNativeOwnership/1`真实原native owner终态。不从read facts/布尔/复制DB生成                                                                                                                                                                                                                   |

实际接口名以相应owner固定回供为准，映射表必须逐字段/版本冻结；不能为了本稿名词对WIP补wrapper假供应。C2发现原claim即证明库内受理事实，operation marker null不能说未受理；响应丢失/重开仍查原Job/context，不换operation自动重跑。普通读Job没有domain marker正常；成功result/origin是真实终态闭包，缺cache不抹原受理。复制A到B即便逻辑UUID/hash全同也不认证A原physical/dispatch；正式resolve仍unknown或binding-unavailable。

内部临时库链用真实Coordinator/JobStore lease/owner实际来源及明确内部配置，不伪造I06正式scope。origin正式字段缺失如实not-recorded；可以验证原Job/同worker/SQLite机制，不能签公开用户来源。最小内部链不等待完整用户目录UI，但正式权限、首IO/备份/物理binding未供仍不得对外开放。

## 13. 每种终态的所有权转移

| 事件                         | 允许持久变化                                               | 实际持有/释放与可读证据                                                                                     |
| ---------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| 新受理前缺源/拒权限/预算不足 | 无新Job/claim/角色行                                       | 已执行读work不退；未转交buffer实际drop，权限先于内容证据                                                    |
| queued取消                   | 原Job cancelled+claim/history保留                          | 无producer；先drop尚未交worker物料/新读票，原source cache仅按terminal+无pin GC                              |
| running成功                  | 原一事务artifact/origin/result/succeeded                   | complete+正常exit+全部三流EOF/关闭任务/最终fence；只向一个handle转交，接收预留在先                          |
| running取消/异常/timeout     | 无半artifact；原失败/cancel终态按F预留                     | 先fence，terminate/kill只是请求；等待真实exit/三流/native/任务，期间retired占H/pin/selection名额            |
| complete后exit1/尾流/late    | 拒成功，保原失败事实                                       | 不以complete替exit、不忽略剩余frame；收尾失败不能报告已drained                                              |
| COMMIT后响应丢失             | 既有唯一success/origin不再写                               | 原operation/Job对账；无二次reason/新claim，内容可能之后GC但终态仍真                                         |
| engine关闭/重开              | 原reconcile非terminal；无自动重派                          | main permanent cohort仍记旧engine/worker所有者，缺真实drain先quarantine占额；已terminal历史可只读核证       |
| 旧artifact退役/GC            | metadata/L/Job/claim/receipt保留；缓存status及完整角色删除 | 无active/retired/report/current依赖才能GC，source依赖也受保护；evicted/损坏/缺源/权限各有事实，绝不默reason |
| 新Job复用相同source/result   | 新原受理及新不可重置账户                                   | 不免费借旧pure ledger/Graph票；完整key/权限重核，旧退休owner真实结束前不得偷降合计H                         |

永久drain的完成谓词是上述每个已登记所有者集合均实际terminal且没有待转交引用/starting spawn；timeout/TTL/pending0/PID不可见/kill返回/RPC promise settled都不是充分条件。bounded error保首因，不把未完成drain改成功；主线drain最终产品的完整反例/资源事实仍须同候选独审。

## 14. 精确writer申请、依赖与阶段顺序

以下是后续申请，当前只docs；唯一本T01 writer串行维护共享文件，不把135清单变目录写权。

| 既有路径（统一engine源码前缀packages/engine/src/ontolearn_engine/）                                                                       | 最小必要delta                                                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| storage.py                                                                                                                                | profile-aware原definition/快照/历史/写scope、metered原state/load/publish/事务/GC/持久增长与Tail headroom；保旧fingerprint和default2                                    |
| job_store.py                                                                                                                              | 原create/_accepted/get/context/Job3 reopen分派、同txn语义受理/成功/失败、origin ref白名单、source依赖pin/GC、原details侧写门、start/cancel/reconcile独立控制           |
| coordinator.py / worker.py                                                                                                                | 真provider内部准入、原Job材料编排、单owned child双向roles、全部EOF/exit/fence和尾流、取消/退役/费用/原test分支兼容                                                     |
| **main**.py                                                                                                                               | 仅安装实际冻结私有provider/owner配置和版本路由；不开放额外RPC或健康身份                                                                                                |
| project/format3.py                                                                                                                        | 唯一合成catalog/migration及历史/profile语义、四role状态表完整DDL/hash/trigger/FK和原C1身份保留                                                                         |
| project/domain_changesets.py / transactions.py / compensation.py / applications.py                                                        | 完整typed rule/query/constraint/ontology sourceBinding同namespace确认/接受/commit及所有Diff/undo/combined路径、同session深meter；不造第二plan                          |
| project/source_content.py / project_host.py                                                                                               | 仅新scope调用的原blob读/前门费用与新catalog/ReadLimits schema适配；旧8MiB source格式和host cache本义不改                                                               |
| packages/contracts/python/contract_v2.py、src/v2.ts、src/index.ts、v2/schema.json、registry.json、fixtures.json、binding-regressions.json | canonical唯一strict私有version/adapter/数据材料union、所需typed定义plan、hash/正反例同步；旧六字段/17字段和公开原methods保持。不私自改errors/states                    |
| apps/desktop/src/main/engine.ts、task-service.ts、index.ts、jsonl.ts；renderer/src/task-presentation.ts                                   | 只在root冻结dispatch实际产品后串行做真实original call/scope/drain及有限错误展示适配；本profile不传raw材料到renderer、不放开通用IPC。不认为旧四文件交接等于本次产品授权 |

新增T01源六件：`project/profile_jobs.py`（原受理/provider）、`project/profile_material.py`（来源前门/codec）、`project/profile_artifacts.py`（同Store origin/role）、`project/profile_selection.py`（完整lease/pin）、`project/profile_budget.py`（原owner累计费用/H）、`profile_worker.py`（仅owned数据通道）。它们不自开Store/事务权威，不可替代上表真实旧writer hook。新增engine tests六件同名 `test_profile_jobs.py/test_profile_material.py/test_profile_artifacts.py/test_profile_selection.py/test_profile_budget.py/test_profile_worker.py`；新增TS测试 `tests/unit/t01-profile-canonical.test.ts`、`t01-profile-lifecycle.test.ts`。旧test不改，必要旧fixture变更须具体反例和单路径申请。

readonly：resources.py、protocol.py、rdf_snapshot.py、memory_guard/process_environment、I05 semantic/restore/budget/new codec/provider、T05七机制、T03四build/锁及CI均由各原owner。I05 new input/production/fullview的九writer139候选由其实际新产品ref另批准采用，后续selected/scopes/集成新三文件仍其独占；T01不复制matcher、改cap或代做fullview。若profile私有worker新依赖导致协议/budget/API必须变，给精确前后hash/循环/门反例另申，不能凭这张表抢写。

候选计数不伪闭：135初始+I05新增4=139；T01新增六源/六Py test/两TS test=153最小候选；I05后续selected及两测试新增三件则至少156。旧writer中若某path不在135或C2/dispatch实际新增路径另有delta，必须补入完整最终manifest，不能沿156当最终全闭包。新产品每次采用做actual branch/ref/path/current/Git/bytes/SHA、冲突表及独立receipt；所有未列路径仍5f，build/资源/schema版本不一致先停相关接线。当前source-manifest的135只证明真实固定输入，没有把未存在supplier当可采用。

实施顺序：root先分别精确授权I05三个真模块和T01 S1–S3原语/新profile schema设计；共享format3/storage/job_store/canonical与ontology只在一个root窗口合并维护，不能两树同时写。待真正provider和C2/dispatch固定后，root按path批准组合closure；T01完成一个真实nonempty producer→原origin→重开→K0/K1 consumer，然后K2/K32与全部失败/±1/pin/GC/drain，I05自己的selected API/新fullview预算实际证明同步关闭。T03唯一owner随后对同组合源码/最终包同真实Job全值验证。正式I06权限/位置/原dispatch和native资源回供后接公开UI，不以内部SQLite通过提前认证；指定双模型、CI/正常develop与远端及完整父门按原要求完成。本轮不执行任何这一步。

## 15. 实施验收矩阵、独审与本轮出口

| 组          | 未来必须真实驱动的断言                                                                                                                                                                                                              |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 正向        | 真实确认rule/ontology/query/constraint→原Job claim/context→一次owned producer/actual defs/Catalog/L→同txn保存→关闭重开→新worker fullview全部7/15/11字段/payload/rows/原序→selected实际query/SHACL通过及违规、分页/undo失效          |
| K与槽       | K0非空asserted/ontology/空图均U/D非免费；K1/K2/K32完整restore后才发布，重复/33拒；实际N1/N3/N100、disabled/dummy/空batch/全false/多head；原选择序与R_j/slot(j,i)一次，不拿K*N开大pure池                                             |
| 真实源      | 原snapshot/public-internal/project/op/Job/parameters/manifests/lock/codec/context/definition/source最后字段错换；consumer大于producer旧input、不同语言原拼写/None/空串/最后Unicode及TermInput精确类型；源文件缺失不伪locator        |
| 原版本/冲突 | 旧普通Job/page/6字段/17字段/finite6/opaque定义、旧profile1 namespace碰撞仅历史也拒升级且原dump不变；新旧reader严格分派、旧reader拒新库、migration_id/C1创建receipt/旧hash全保持；ontology与profile同时变更唯一migration/plan writer |
| wire        | 32768/65536/4096/LF/69633及实际262144差1、空role/全部164roles、ack/backpressure、uppercase/奇数hex、错role/index/ordinal/hash/end、complete后尾流/非0exit/迟到/三管道挂起；不得依stop/kill返回放行                                  |
| 费用        | C/T/每R_j/Σcap/Σusage/三池/S/H及SQL/GC/持久候选/临时峰值exact/-1/+1；重读/失败/切第二artifact不退款、同Jobclosed重开不能reset；新合法Job自己收费；实际loop/delegate/并持/source pin与retired逐owner映射                             |
| 事务        | 原受理任一写点/roles/details/result/current/terminal前后故障，最后chunk/child/result失败，无可selected前缀；已受理失败允许原终态变化；owner ownership侧写禁、未知外txn拒、内层SAVEPOINT耗尽完整cleanup/in_transaction=False         |
| tail        | 多次cancel/start/幂等/失败重试后F_terminal不被侵占；业务过期/读额度耗尽仍有一次合法owner finalize，真实SQL失败不假收尾；run NULL门与原rounds回归；重开原reconcile不重派                                                             |
| pin/GC      | 撤权先拒内容，全部K pin原子/GC串行、current/report依赖包含source、oldblob不可GC、status合法evicted与缺行损坏分清；实际native/view/Graph/pipe/traceback未drop继续占H，TTL/live0不代释放                                              |
| 对账/drain  | queued/running/cancelling/success/失败/cancel/COMMIT后响应丢失；marker null不能未受理，copy A/B不成resolve；starting/timer/listener/旧新retired/三流/native未终态不能释放；内部真实owner与正式I06 authority分开                     |
| 全范围      | 原83/89/40/M1所有原失败与缺状态、真实RDFS直接层次/SHACL C格、原17L数学来源、T03新源/包同链、外联/目标OS/真人/指定同版双模型/CI/正常develop/远端原门不由本切片关闭                                                                   |

独审重点为来源先界与权限、完整旧writer/真实事务、typed schema及历史碰撞、全部R/C/T/S/H真实持有和不可重置、正常非空正例是否在有限guard内可执行。任何实质反例先报根并保旧稿/处置，新稿实际bytes/SHA后请原独审复核；本作者不代审、不自签通过。源码/API未供的费用峰值/实际可执行性明确是实施门，但不能用这句话掩盖本方案的空材料/零额度/漏writer等具体设计矛盾。

本轮read-ready出口是主方案、source-manifest（135逐Git及全部固定文档身份）、静态调用库存、budget-quanta及调查原件；仅Git/文件/JSON/AST/算式/文档格式验证。之后待根安排实质独审；未获进一步授权不stage/commit/归档最终Pass，不运行产品import/DB/tests/故障child/native/build/GUI/网络/模型/付费，不改原Goal。
