# C2 原操作只读证据核心：独立方案审查

结论：最终方案41960B/1724在本审内部事务、严格helper复用、证据闭包、状态与归因边界范围内已完成具体处置；两项P2和一项P3均在方案层面关闭，无本审未解决实质设计问题。预算算式与SQL计价另审。本文是静态方案审查，不是 C2 产品实现、运行、授权或正式 resolution 通过；没有运行数据库、产品 import、测试或故障子进程、GUI、网络或模型。

## 固定材料与权限

全文实读根 C2 准备授权4190B / SHA256 `3a2fb6b04154bdc29fcda1d92c74cfe7c5e8438950ae55c7b49dd573d05d9195`、C1根收口2650B / `001eceab453c30bd49b59e21d629ee1b4b88cfc5002f981fd0e84f8d61332fdd`（f0b74c）；独立hash核验3703fd exit0。固定379916合同39602B / `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3` 的第3、6、7、8、9节逐节全文读完（ec7d9b）。沿用已全文读新树 AGENTS15852B/78df与common17891B/e437，完整第九节与无桌面规则仍有效。

本轮唯一主草稿 `docs/iterations/T01/project-operation-evidence-core-C2-plan.md` **33663B / SHA256 `dcebb1e03baac485b06cc22f90611b24503e81c26978695188dcb4b9cf0e7835`**，190行在abb5aa与fa69a5全文实读；不把尚未实施的查询门或测试矩阵当实际验证。本审仅可写本新报告，不改主方案、C1产品/原59交付、其他报告或任何旧规则，不stage/commit/checkout。

新清单全文186a04：14521B / `aef7b7c2d61cadb0eb8de73b5697f7ce78d384d217ff301bacd9038ff291f9cd`。e5531f exit0逐52路径核source423b Git=current/bytes/SHA，全部唯一readonly；当前HEAD为纯过程a33cc80。计划C2树不存在，两新writer文件不存在。未来从5f建新树、逐52接收后全部只读、只新增 operation_evidence.py/test_project_operation_evidence.py 的范围是申请，不是已授权动作。预算SQL计价专项由另一agent负责，本审不重复其算式或替它下结论。

## [P2-C2-01] 旧 history wrapper 会把存储故障改成缺证

状态：已在修订稿§4与专项矩阵具体处置，方案层面关闭；以下保留首草稿§3、§4、§7原问题。

固定源码 `format3.receipt_for`（778行起）在内部 `_history` 调用外捕获 `sqlite3.DatabaseError`，统一改抛 `Format3Fault('structure')`；`load_checkpoint` 同样处理。`sqlite3.OperationalError` 是其子类，真实 locked/busy 和某些读取I/O故障都可能被归为结构坏。若门直接透传SQLite异常，外层即使列出storage-busy/storage-failure，也已经无法从structure恢复原失败类型。这会把存储暂不可用冒充正常incomplete-evidence，违反固定合同对资源/存储错误与缺证的区别。

具体静态反例：创建完整证据存在，receipt_for遍历后续checkpoint时实际conn.execute或cursor下一次fetch抛OperationalError；旧wrapper返回structure，核心把它当缺checkpoint而输出incomplete。相同问题适用于门抛出的控制异常若继承ValueError/KeyError/TypeError等旧捕获族，资源超限/未知SQL也可能被吞成坏证据。本轮未运行该故障，不声称有实际产品复现。

要求的最小处置：门在实际execute及所有fetch/iteration边界把SQLite busy/locked/I/O错误转成独立C2控制异常，安全携带有限reason；该异常不能属于既有validator捕获的sqlite3.Error、ValueError、KeyError、TypeError、OverflowError、RecursionError等族。资源/unsupported-profile控制异常同样须无损穿过旧helper。唯一入口负责finally释放自己开启的读事务，然后按固定安全reason映射；不改旧wrapper/52readonly，不展示原异常串。若ROLLBACK自身失败，应保留原首因并报告storage失败/cleanup，不能返回正常事实。

未来专项应覆盖execute、fetchone/fetchall和iterator-next故障，以及history包裹内资源/未知模板控制异常，核结果不是incomplete、无内容泄露、无写、owner未知caller事务不受回滚。该要求是门闭合的一部分，不申请新的产品路径。

## [P2-C2-02] rounds 模式需明确无run和零轮的合法状态

状态：已在修订稿§8与专项矩阵具体处置，方案层面关闭；以下保留首草稿§6 rounds行与§8 mode rounds/failed/cancelled行原问题。

固定 `create_job`（955–1001）为所有Job写 `jobs.run=NULL`；rounds DTO的committedProgress也是None。`start_job`只变state，直到`start_job_run`才写runs。`_finish_unsuccessful`（1189）仅当run真实存在时写run_terminal。因此queued rounds、已start但尚无run的running/cancelling，以及无run的failed/cancelled，均可合法存在。已有run但零轮也合法，progress=None；固定旧测试test_cancel_preserves_rounds_zero_null_and_cancel_snapshot明确覆盖零轮取消。

草稿对mode rounds统一说核run归属、全部rounds和真实run_terminal，未冻结这些空阶段的条件。若按该段无条件要求runs/terminal，会把真实已受理Job误判incomplete；也可能为了“满足完整证据”人为推导空run。首草稿的一般queued无marker规定不足以给出run NULL的精确决策。

要求的最小处置：明确三层状态矩阵：(1) run=NULL、progress=None、非succeeded合法受理，不要求或合成run；若progress非空或succeeded则不完整。(2) run存在但0轮，非终态允许无terminal；failed/cancelled必须有对应terminal，committedProgress可None且与实际0轮核同。(3) succeeded必须有run、完整连续轮次达到真实maxRounds、对应terminal/末态/consumption/result；非终态反有terminal、错误状态或非空进度无run均拒绝。无run状态亦应拒绝与该Job关联的孤儿round/run绑定，不能仅忽略存在的矛盾材料。

未来专项需从真实create_job逐阶段构造queued/runNULL、running-before-start_run、cancelling/runNULL、failed/cancelled/runNULL、run存在0轮取消，再加伪progress/succeeded无run/坏terminal反例；只读判定不续跑、不补证据。这里只规定未来验收，本轮没有运行这些路径。

## [P3-C2-03] terminal结果全行核验关系宜逐字段冻结

状态：修订稿§8已采纳，方案层面关闭。首草稿§6/8明确resultRef、job/project/snapshot/implementation/投影互证，但其“完整严格”还应列出固定writer的其他关系，避免只对归属而忽略全行内已读字段。固定Store.publish将results.dependencies保存为原snapshot中选定dependencyVector，cache_key按project/kind/snapshot/dependencies/implementation摘要；_publish_job保存context.manifests、definition/scope/parameters投影及capability对应kind。

建议明确results.dependencies与原受理vector、job_results.manifests与原context.manifests、results.kind与原capability、cache_key与原公式逐值核同；payload尚在时逐同版row schema、rowId/ordinal唯一性及receipt/summary专用关系核验。反例是只改结果manifests/dependencies/kind仍满足id/job/project，不能因这些表行已计费就默认语义完整。当前stale/current是可变cache，不当原受理身份。此为设计精确化，不是运行发现或额外writer申请。

## 其余关键切点的静态判断

直接读固定源码b575f9、8d4ba8、863c26、1d99b7、22c22e、9dfd39、6ca591、17bcdb；静态AST ca4631列所选原方法的self/cls调用边。没有通过产品import取得这些结果。

- 全新只读事务：先拒真实db.in_transaction，再BEGIN、同连接完成、成功/失败ROLLBACK；不借Store._read默默加入未知writer事务。已有view中的state/_read只在该新事务内加入。规范禁止覆盖owner authorizer/progress callback，authorizer不冒充逐行费用证明。
- EvidenceView不继承/构造Store，不改真实_db，只把冻结原实现绑定到view；_accepted_job调用的_project_snapshot/blob/_job_prepared_plan/get_job均继续走view。_plan/_definition须保staticmethod，_snapshot_state须保Store原classmethod纯校验。无真实boundmethod透传、__getattr__回退或空stub。所列方法的静态调用闭包目前可用两新文件实现；未知模板fail closed，真正缺切点须另申，不据计划承诺实际已闭合。
- 实际行门：定位rowid先界、整条查询预算足够才投影、所有传递SQL再经门，是避免“先parse后补账”的具体设计。JOIN的commits/commit_evidence分别实际行去重，UNION不把来源相同值当同一材料；当前chain-end state/vector/application_state虽不返回也不能漏读。SQL精确计价/UTF16工作上界由预算独审另核。
- 全库与目标：不再调用全库format3.validate/_validate_job3而只收费目标。schema/catalog及全库aggregate guard与目标完整语义闭包分别存在；初始Job-ready是可信owner前置。方案明确现有启动校验先于C2预算的分配风险未解决，且没有把raw bytes/work冒充canonical证据预算。
- 创建：复用C1 creation_context对实际origin/seq1 op/receipt逐typed行核同，再用receipt_for核到当前head的完整混合链。修前伪创建claim借domain receipt反例应拒。不得只取genesis与seq1，后续CP/旧app claim/confirmation/draft.restore/current state均纳入闭包；后续名称/base变化不重做原请求。
- Job受理：未知jobId沿唯一claim完整发现，不从last16/marker查找；queued的null marker不等于未受理。原expectedRequest/issuedImplementation/issuedLimits与持久完整context比较，不取当前值。明显project/kind/knownJob/原请求错配是identity-conflict，不返回异操作内容。
- 来源：ChangeSet用accepted_plan(host=None)复用真实immutable envelope+确认job_details receipt，另核selector host/session；不能传原host触发当前base要求。普通Job缺session保持not-recorded，actor/当前Session不补来源。copy A→B仅能说明B持久事实，任何hash/UUID/migration_id都不是原dispatch物理绑定。
- 终态：_accepted_job/get_job不证明全部提交；atomic须实际marker+immutable app receipt/history与DTO互证，结果payload尚在须核receipt cells。可回收payload=NULL不等于未受理，不调用_result_rows的PAYLOAD_EVICTED来否定原终态。rounds严格链另受P2-C2-02处置约束；history.replayable=false不作充分性证明。
- 未来正式边界：临时事实union不含resolved/permission/scope/recoveryOnly，不把普通Job DTO塞正式unknown。真实current_scope、I06原dispatch绑定/跨Session物理对应、实际frame/page/envelope供方仍未到；正式适配无原绑定必须unknown/physical-binding-unavailable，权限失败先于内容可见。两新writer不构造真capability、不改协议/Host/main/UI。

## 修订复核与最终限定结论

第一修订主方案 **40363B / SHA256 `ff93f5017fefa71630a3c15e6d2f44ab2cebb867e75afbb47f005bcd652e2cbc`**，196行已在bb691e/f347bf重新全文实读并独立核bytes/SHA；不是只接受主线转述。52项清单仍14521B/aef7，9d111a exit0逐项再核source423b Git/current/bytes/SHA不变、计划树和两新writer继续不存在。

- P2-C2-01：§4明确EvidenceControl直接继承Exception，不属旧helper捕获族；真实connection的execute/fetchone/fetchmany/fetchall/iterator错误先安全转换，BUSY/LOCKED按主码为storage-busy、I/O等为storage-failure，资源/未知模板也穿透。入口finally保首因并记录有限cleanup状态，避免旧receipt_for把它们吞为structure。§10增加各边界故障和首因专项。9d111a另静态核旧捕获子句，未发现该独立异常仍会被所复用只读闭包吞掉。因此此设计缺口关闭，运行证据仍待另授权实施。
- P2-C2-02：§8明确run=NULL+progress=None的所有非成功状态合法，未开run不要求runs/terminal；已有run但零轮的running/cancelling合法，failed/cancelled的terminal允许committedProgress=None；成功要求真实run及完整轮次/terminal/末态/consumption链，实际last progress与DTO核同。§10增加runNULL/零轮状态反例。保留真实底层矛盾材料不得忽略、缺证不得补写的约束，因此原统一要求run所致误拒缺口关闭。未来实现仍须以精确状态矩阵逐项实际证伪，不把这里的静态结论当运行通过。
- P3-C2-03：§8逐字段冻结dependencies、manifests、projection、capability→kind、原cache_key公式、rowId/ordinal唯一性和完整receipt/summary/audit关系，当前stale/current不冒充原身份；§10加入对应损坏反例，精确化已完成。

修订同时加入预算agent要求的两阶段工作先扣、probe/query/read-work分离、scalar先界与编码chunk反例；本审仅确认它们没有放宽本审事务/零写/旧helper/正式授权边界，不替另一agent证明SQL算式。两个新文件承载EvidenceView/固定SQL门、必要事实关系与新专项，从已读静态闭包看未发现必须立即修改52只读文件的切点；实现一旦出现绕门SQL/无法复用/额外方法依赖，仍先给具体反例另申，不能凭本结论默扩维护权。

最终冻结方案为 **41960B / SHA256 `1724a6e6c9fd315a7065696720ce221bc68631aaf6b1d690479d70635eafba56`**。3fad78独立发现版本漂移后先告主线，没有拿40363身份当最终。新增§5及对应矩阵已实读e73960，其余段又按21f49f/5a62ab全文核对；主线确认仅控制槽及对应矩阵变化。新规范在65536总query内为BEGIN/ROLLBACK各预留1、业务SELECT最多65534；finally释放走独立控制路径，不被已耗尽的业务/证据/probe/read-work额度阻止，BEGIN未开始不伪rollback，cleanup失败保首因并标存储失败。该处置避免预算耗尽后遗留本次读事务，与本审只读生命周期要求一致；矩阵包含耗尽与±1后实际in_transaction=False的未来验收。没有新增本审实质设计缺口。此为方案限定结论，不是已实际执行清理故障或预算边界测试。

本审方案范围通过，交根与预算独审一并决定是否精确授权。尚未批准产品写入/新树采用/测试或DB运行；所有矩阵均待授权后真实验证。正式create/resolution、原dispatch物理绑定/current_scope/真实frame及Host/首IO供方、copy A→B正式unknown、普通Job来源缺失、指定双外审/CI/父FR及完整目标均保原边界；本报告不关闭这些门。

## 最后闭包补充与新冻结身份（追加）

主线最终读回指出P2-C2-02原意见中的“run=NULL亦拒与Job关联孤儿round”尚未在41960稿的实际集合中明确表达。本审确认补充必要：`jobs.run=NULL`并不排除损坏库中已有`rounds.job=实际JobId`，仅沿jobs.run读取会漏掉有结构关联的矛盾。非NULL时也可能同Job有另一run的轮次，仅顺单run同样会漏掉。

主方案最新冻结 **42685B / SHA256 `e7db89cb52cc75707d0e7a00e637e97701bea7e7d49f623ef464cb1baf44b96b`**；f52949独立核bytes/SHA并实读§6新增完整段。该段明确无论run是否NULL，先按`rounds WHERE job=实际JobId`定位、完整收费、逐核run=jobs.run；NULL时集合须空，非NULL再按所指run读全部rounds反核job一致。无新索引仍由全库raw guard和query/read工作界约束。run_terminal没有job列，限定沿真实run主键与结构化round.job关联，不扫同项目terminal JSON猜关联、不把别Job run当本Job。§10亦补runNULL带孤儿round、同Job跨run反例，已定点实读；原§8全部rounds核job约束继续。

该明确双向闭包满足原P2-C2-02处置要求，不扩大到无结构关联JSON全库语义扫描。仅追加本说明与新身份，前述首稿意见及41960审查过程保留。当前本审无未解决实质设计问题；仍为方案范围结论，未来产品/DB/专项、预算另审、根授权、正式物理绑定/scope与父门均不由此放行。本审没有运行产品或数据库。
