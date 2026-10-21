# Ontology真实供方方案：独立实质审查

首审结论：55720B固定稿暂不通过，三项P2需具体处置；不是产品缺陷运行复现，也不否定S1→M→S2的总体方向。问题分别为旧opaque命名空间的历史兼容、原ownership失败外侧写，以及预算耗尽后的Job失败/取消收尾。另有正例成本数字和未定义成本项需明确。本报告唯一新写；未改作者稿、既有C1/C2/dispatch、产品/测试/依赖或其他报告。

## 1. 实际依据、读取与身份

全文读准备授权6217B / SHA256 `d55528dc65449c83cc5961578f17bedeb47b0b24e0a1080593ba765e8e45a2e9`，根T02独审15654B / `c8c048c9d799e54d5eb4ad34324238a2ba834dcb724a7b020af50199fcb9cadc`，工具 `000d99`；T02固定4406103主稿44243B / `6b88b1f7a8e9b7b08719f6b48dda16905a3eb800a7b8baef21f4b7a26b06983c` 实际184行分段全文 `fd1c6b`、`f8f23a`，身份由 `bfe176`核验。没有把T02供方请求当已有产品实现。

本轮首审对象及配套原件：

| 对象                       | bytes | SHA256                                                           |
| -------------------------- | ----: | ---------------------------------------------------------------- |
| 主方案                     | 55720 | 765515f50902b2c691d41bf85cd660df2afe3014ba38f4ae9753146aba20c0d2 |
| source-manifest.json       | 36527 | 1cdd225221bdd6731463bd9572073181b36ea196df47e6eb4845869a30c4113a |
| static-call-inventory.json | 64782 | f90847c090a385e1a983f2014f71b511691552433dc62e9eb1c7e01a8c785817 |
| investigation.md           |  5213 | 2a9c36b5bfc9e9e0a1a72c5aba727eec20cde08c6295fb291d50265c35f2073d |
| positive-fixture-spec.json |  3429 | 0f043263b691fb45c30c8e643ddeab81c44fdd18eea6ccd417d1fd1561bf8af4 |

主稿228行由 `bfe176`、`2cac1e`读；第二次工具输出包装在§8中部截断，已以 `fd1c6b`、`6b971f`精确补读对应段，没有把截断当全文。调查说明、静态正例数据全文在 `2cac1e`读取；JSON清单/库存由stdlib解析核查，未把64782B函数库存当实际调用次数证明。

69来源current bytes/SHA均与清单一致（`e9f913`）；本审未重复作者69项固定Git全核，不能把current匹配冒称本审再次证明全部Git/ref。T02四模块__init__/service/source_projection全文 `8896fd`，model全文 `50c905`；只读，不复制、不import、不执行或修改。四件实际身份：501B/dd89c568…；model7779B/26cb5c55…；service7896B/fa49220f…；source_projection7422B/919e6f05…，完整SHA见已核manifest。T01实际固定423b的相关Store/transactions/compensation/domain_changesets/Job/format3正文定点读，沿同一现文件原身份，不借C2新树或可变实现。

工具 `d6bec3`仅stdlib AST解析，库存9文件189个函数name/line/end与现源全部一致，不证明动态目标、rdflib内部成本或真实组数。`e9f913`最初把functions字典按数组索引触发KeyError；该静态调查错误已由 `b66494`正确枚举、`d6bec3`全核修正，不计产品失败或通过。没有数据库、产品/测试/构建、故障子进程、网络/模型/GUI/native运行，没有stage/commit或对T02其他聊天发消息。

## 2. P2-01：旧opaque namespace碰撞未有完整历史解释规则

位置：首稿§4“旧consumer安全/profile升级”、§5“_snapshot_state/load/reopen/profile历史严格namespace”。实际切点Store._definition1014、commit650–678、_snapshot_state1262及format3._validate493/_raw_checkpoint543。

固定423b `_definition`只验证它认识的triples/references/singleValuedPredicates，不拒未知dict键；旧commit把整个value canonical持久化，旧快照也完整保留payload。故以下旧profile1载体是当前源码允许的opaque材料：

```json
{ "triples": [], "entityMetadata": "legacy-note" }
```

还包括恰好长得像新entityMetadataVersion1的旧opaque对象。首稿仅说“旧快照profile1没字段按旧版本解释”，不足覆盖已占名的历史。若新strict invariant在load/reopen/history一律把同名字段解释为新业务metadata，升级后会拒绝原合法历史；若只看新形状则可能把旧opaque误认证为真实五字段。旧history没有metadata语义激活位置，改catalog当前hash本身不能补这份历史来源。

必要处置：profile1按原语义保全部opaque、S1不冒认namespace且给coverage-unavailable；显式升级前扫描全部真实当前/历史相关payload做碰撞预检，有任意未经授权占名就有限拒绝升级、原库/历史不改，或另交真实可审的版本激活/逐历史解释材料。不能删除旧字段或重写marker/hash来适配。应补当前及仅历史占名、无效值和恰似v1值、拒绝前后完整dump、仍可旧语义读与重开矩阵。

这是兼容设计遗漏，不是本审运行旧库；首选schema_hash语义profile的总体必要性仍成立。旧Store可直接替换同id仅triples payload而丢未知metadata、旧RDF consumer只取triples，足以说明“加未知键无需升级”不是安全替代。

## 3. P2-02：原ownership失败会在回滚外另写job_details

位置：首稿§7准确hook、§8增长表、§10零部分artifact矩阵；真实job_store.py427 `_application`。

实际分支在原_application事务内出现`Conflict(category='ownership')`时，先让原事务回滚，再开启第二个_transaction，INSERT job_details保存category/resource/projectId，最后以OWNERSHIP_CONFLICT/detailRef报错。mapped、删除、undo等原ownership分支可触发；它不是在原失败事务内回滚的临时artifact。

首稿只列preview/conflict impact/确认/Job/commit等正常artifact增长，没有列该错误后侧写；因此“该次失败完整dump不变/无第二写交易”和“首写前全增长预算”不能由当前原机制成立。它还可能发生在失败phase保留池已释放或成本耗尽之后。

必要处置：对新ontology成本scope明确禁该回滚外持久详情侧写，安全返回有限冲突，不生成悬空detailRef；原非ontology调用保持旧默认，精确列job_store._application必要delta和ownership专属回归。若要保留失败artifact，须根另改交易/增长合同并预扣该独立副作用，不能仍宣称零部分artifact。预算耗尽本身不得经这条旧错误路由获得额外未计价写入。

## 4. P2-03：Job已受理后的失败/取消控制容量未冻结

位置：首稿§7session失效后由Coordinator fail_job收尾、§8Job接收/成功commit终态；真实JobStore.cancel_job1151、fail_job1174、cancelled_job1182、_finish_unsuccessful1189、_transition1131/_save1126及reconcile_jobs1444。

这些是原独立状态交易。受理时只计queued DTO并让validation_bytes恰到限，随后失败error/finishedAt或取消状态会扩张同一jobs.dto；rounds收尾还可能产生run_terminal。若成本session已过期/耗尽，仍用旧默认fail_job写会绕过新增长/工作guard；若全部受同一耗尽guard拦截，又不能据此声称“正常收尾可闭合”。成功commit/undo表里的terminal DTO不能自动证明这些失败路径已预留。

独立stdlib反例 `d6bec3`：只取实际DTO中会变的state/stateVersion/resultRef/error/finishedAtMs/updatedAtMs字段，queued canonical101B，按原reconcile合法ENGINE_EXITED结构变failed后176B，净增75B。其余真实字段不变，UTF8数据库jobs.dto会有同样正增量；若受理后raw全库恰达上限，该失败状态也会越界。此为静态最小投影算式，不是经contract验证/数据库实测的完整Job。

必要处置：在新Job受理前对有限合法失败/取消终态预留真实持久增量和最小控制工作，或给每个原状态入口明确同事务预算/容量拒绝与诚实失败规则；必须覆盖cancel_job/fail_job/cancelled_job/_finish_unsuccessful/_transition/_save，以及重开后的reconcile职责边界。控制余量不授予新domain/plan写，不改旧context/hash；scope失效或资源耗尽时不能从旧默认路由绕过。若重开生命周期仍是未解决原风险，明确保门，别称内存session已证明跨退出收尾。

## 5. 成本正例及实现申请需更精确的说明

正例source实际canonical2365B，具三Entity五字段和九声明/label/comment支持加一人工fact；来源是真实数据规格，不是已经Store/T02运行。按正文已列公式与B4096、H+P24576、Q8、N8、S12、L2048、T64，`Helper`为2581248，非JSON的2593536；8个Rdf组各203264加32768余量、20Helper合计53283840，非53529600。原数值较大是安全保守方向，但应明确额外预留项或更正，不称同一公式精确核同。

`SourceBind=SnapshotShape+...`中的SnapshotShape尚无独立固定成本式/调用计数；20Helper/8Rdf组也明确只是待实现接受目标。库存189函数的位置核同不证明“组内全部旧重复已包含”。需把每个组合成本的明确变量/式子与全链共享账户、失败工作不退款、真实保留释放分开列，说明SQL probe工作是否独立额度或同币纳入，避免正例遗漏某类费用。首完整正例真实运行及实际组数仍是实施后必须过的门，当前不把该JSON当真实body已受限的证据。

整体方向正确：先于T02 Snapshot/Triple/validate/bind/change_preview及旧T01深helper执行收费，跨页/失败共享有限session；旧plan/detail/blob和完整历史重复不免工作；预算不足不猴补旧函数/事后追账。S1两个新writer可用只读view的全phase可证明预扣先行；M/S2明确需要storage/format3/transactions/compensation/domain_changesets/job_store/applications等精确hook，不再假称两个wrapper足够。

## 6. 其余实质核对与完整目标

- metadata首选有明确唯一home(project,ontology definition ID,IRI)、五字段与IRI/definition ID分离、同IRI多home即使同值也拒；修改identifier不改IRI。labels/definitions保存所有语言和值，RDF集合交叉核同；manual/definition多支持保源，不以RDF去重抹支持。中文单值显示无唯一zh时给选择材料，不把排序第一当主名称。
- legacy L1/L2/L3的取舍明确：默认不擅用v_IRIhex为英文标识；缺metadata和真实空值分开，未知opaque不默认缺失。根尚需选legacy与identifier唯一性范围；这不是作者自授业务决策。S1先保真读+缺失报告与M在完整编辑前的顺序保留。
- profile升级确有旧consumer丢未知metadata的源码必要delta；同user_version3新语义签名、安全拒旧consumer、保migration_id避免破C1逻辑引用是可审方向。但P2-01的旧namespace碰撞必须先解决；生产备份/位置供方未到不被fixture代替。
- S2 sourceBinding在唯一v2 job_plans内，previewHash独立命名，原storePreviewIdentity/marker域不混；preview/confirm/新Job接收/首次commit四个真实原外层事务各自复验，非wrapper跨await。页/cursor/proof歧义、旧v1和v2严格分派、historical/current分离、已提交后当前metadata变化不抹真实receipt均明确。
- growth表完整涉及原preview/页/confirm/Job/domain/app历史/result及SQL试算峰值，immutable plans/details/blobs无安全GC则有限库增长后拒绝，未声称TTL删历史。仍需P2-02/03的失败/取消例外和控制容量。
- FR-200四类创建编辑复制删除、五字段/metadata-only、实体子资源不相交undo/ABA、所有支持选择与完整引用影响都有必要具体delta。T10包/metadata伴随文件不能被Turtle单独往返替代；跨层IRI引用供方、T10真实版本、FR202实际三视图/分页、FR203合法列表/Turtle、FR204 T08草稿/实际App/人类/双OS与正式scope仍依T02固定完整表及root供方门，不能以本内部供方宣称完成。
- 当前writer申请的S1/M/S2分阶段和root序列解锁合理；canonical严格字段/registry/TS/Py helper/fixture同版集合明确，T02冻四模块只读，必要新树consumer meter另申。_application及状态收尾delta须在精确表补齐，不把已列job_store通用路径视为可随意改任何分支。

## 7. 意见传递与待复审状态

上述具体反例已先发送主线/root及作者create_core_review，没有等报告写完才告知。作者回复已保55720/765515首稿，将分别补profile1全历史碰撞预检、禁止新scope ownership外侧写、失败/取消控制容量与入口、数字/成本项；作者没有自判关闭。本审尚未读取修订稿，故三P2当前保持未关闭，后续只在实际read-ready新身份和具体处置核对后追加结论。

本轮结论限静态方案，不运行任何产品或数据库，不授S1/M/S2/T02代码窗口，不改变C1/C2/dispatch保护、完整FR200–204/57P0/C–G/PRD10–12、指定同版双外审、CI/正常develop/远端与原Goal边界。

## 8. r2实际定点复核：原三P2处置与两项控制边界

作者r2主稿71515B / SHA256 `21c163a971b512b55b8a62c25143461ac5be79d91e3e9305f7b99802a1a29700`，处置说明5056B / `9caa48464f15fb4defb99274bea994eb5e854ece0a2342d5b26b769557e1b70f`，正例4102B / `fdbbb90dfce9df6515b54a61b1947260fbe287c87a824ddb40aede32b959dfcf`，工具 `14e455`实际核身份并全文读处置说明；其检索输出包装截断部分以 `b34da4`精确补读§5/§7及完整正例，不把截断当全文。原r1五件逐snapshot-manifest实际bytes/SHA均同，`58649f`；原55720意见与配套没有倒改。

P2-01在方案层已具体处置：profile1任何形态的同名字段都仍是旧opaque、S1给coverage-unavailable不认证；显式升级前于真实同事务先界/计费扫描所有schema定位的当前/历史definition payload，任一顶层占名或覆盖不足即拒升级原件不变，不去文本里猜字段。可升级源全部旧历史确证无该namespace后，新profile才允许新写。_snapshot_state纯旧shape保留，profile/provenance在owner读/历史/写入口明确传入，包来源也不能省。碰撞另需根批准保真迁移，未假称支持已到。该处置关闭原兼容设计遗漏；真实升级/重开/包证明仍待实施矩阵。

P2-02在方案层已具体处置：新ontology scope即使过期/耗尽也保持其身份，在_application ownership except任何uuid/新_transaction前转独立私有有限冲突，不写job_details、不伪造detailRef；公开OWNERSHIP_CONFLICT严格schema没有被塞假值。旧无scope路径保原默认；已有Job tail另列真实状态交易，不能混称preview失败dump不变。准确writer和矩阵补齐，关闭原失败侧写遗漏。

P2-03在方案层已有具体admission：原create_job首写前按完整合法DTO候选算最大SQL/canonical行增量、最坏safe-int时间戳/版本/有限错误catalog；Wtail按真实3个状态交易全probe/read/parse/校验/marker/清理计，最低262144不是任意Job充分证明，上限8MiB，64槽计入主总额、buffer占原池。S2严格只atomic changeset/runNULL，不借额度写run_terminal。真实状态入口、TTL不释放未收尾tail、active tail时所有Store写需尊重headroom、未知writer先拒以及重开reconcile另做control admission均明确；真实I/O/full仍可收尾失败，不虚构terminal。其对旧业务启用期间的调度影响已明示待root批准，不伪称完全零行为差异。

新metadata写gate还明确对namespace增加/改变/删除/载体删除都需同事务真实prepared ontology scope，普通合法payload替换也不能抹metadata；M真实开放依赖S2同版proof，不用内部fixture token假完成。这是对唯一home安全的必要补全。

成本小项已核：工具 `85ea93`独立stdlib逐式重算Helper2745088、Validate280320、Rdf537088、SnapshotShape200576、SourceBind额外99136；20Helper+8Rdf+SnapshotShape+SourceBind额外+4194304 tail+32768合计63725248，与JSON逐项相同。修订明确这是staticAccountedSubtotal而不是已证真实body上界，20/8组数、H/P/Q、tail与首完整正例仍是实际实施/激活门，没有把JSON当产品通过。

本审新增两项收尾边界已立即发作者与root，尚待实际修订：

1. **tail terminal floor不能被重试侵占。** 当前start/cancel/terminal扣同一剩余TailReservation；原cancel_job对已cancelling重复请求仍读完整Job并返回alreadyRequested。重复无UPDATE调用也能耗64查询/Wtail，导致最终terminal没有控制余量。应隔离一次start/一次cancel与不可侵占的terminal最坏份额；幂等/无效重试走独立有限只读预算或入口先拒，不能吃掉唯一收尾余额。按真实全部helper/probe算，超过控制上界接收前拒；补重复cancel/start/失败重试后terminal仍保留矩阵。
2. **嵌套SAVEPOINT的cleanup也需先留。** 原_application→ProjectTransactions.preview→Store.commit至少两层_transaction savepoint；内层错误可能需要ROLLBACK TO+RELEASE两组，再外层ROLLBACK。仅给每阶段BEGIN/最终COMMIT或ROLLBACK各1槽不覆盖实际序列。必须在入层前预留BEGIN/SAVEPOINT/RELEASE/ROLLBACK TO/COMMIT/ROLLBACK的有限最大成功/失败控制路径，cleanup不被业务耗尽/未知模板guard挡，仍计总65536并界嵌套深度；补真实preview试算内层耗尽后的dump/in_transaction=False。未知caller事务继续拒，合法owner token嵌套不是外部caller权限。

r2原三问题已获得明确设计修复，但最终审查仍等以上两控制边界在实际新身份中落实。没有执行产品、DB或测试，原受保护路径未改，本审仍仅追加本报告。

## 9. r3最终定点复核与方案阶段结论

实际主稿81538B / SHA256 `c752d7bdebe1b60ab5ecaae3dcf87a6a5829d21d45313c2f3d2c04b034205db5`。主线最初通报处置说明6625B，读取时作者已追加独审调度失败/待真实触发事实，实际为6954B / `45643aba73ba01130490c428c161a2e219409cfceada568eab368c16ecb4b09d`；本审以实际读取身份为准，已向root说明。工具 `a46fbf`核两身份并全文读处置说明，检索长输出包装截断未当全文；`b56c9a`逐r2四快照核原bytes/SHA，并用stdlib实际diff读取r2→r3全部新增；`a2c996`补读完整失败/tail/嵌套控制段及原Store._transaction120–145，重核69current来源与manifest全同。

### 9.1 原剩余两控制意见已在方案层关闭

**terminal floor：** r3把TailReservation分为互不借用的F_terminal/S_start/C_cancel，按真实helper/probe/控制序列在Job接收首写前分别算足，合计仍受Wtail/64槽及主64MiB/65536约束。一次start/cancel不借F，queued直接cancelled须读回后释放F，running→cancelling只消C。重复/非法状态调用先消独立有限retry/read份额（至多8次）或在入口前拒，不进入原写交易；不能先裸读Job再发现没额度。

唯一owner finalize票在admission封存，独立于普通重试入门，故retry份额耗尽或业务过期不阻一次真实收尾读核/合法terminal写。重复API拿不到此票；真实terminal SQL/I/O已开始后花费不退、不自动重领F，保原事实与首因；若需另一尝试要另有有限恢复admission，未声称无限重试或必terminal。这补齐了“既要先核角色又不能让角色判断吃掉F”的交互，不用renderer布尔或伪权限补洞。

**嵌套cleanup：** r3申请MAX_TXN_DEPTH8、每phase总入层16（含顺序进入，非只数最大深度），phase先封存3+4×15=63控制query与256×63 work。各层在BEGIN/SAVEPOINT之前拿票，外层最多BEGIN/COMMIT尝试/必要ROLLBACK三槽，内层最多SAVEPOINT/RELEASE尝试/必要ROLLBACK TO/最终RELEASE四槽。该序列覆盖固定原helper中成功RELEASE失败再进入except清理的额外尝试；每层真实结束才还未用保留，已执行query/work不返。

控制SQL只允许实际owner栈登记的内部name/LIFO及固定语句；业务query/work耗尽、过期、未知业务模板不阻清理，未知caller事务仍拒。祖先层在后续入层失败时保完整票；savepoint未建立不伪ROLLBACK TO，清理失败仍尽力剩余合法路径和外层ROLLBACK，保首因与有限cleanup状态。健康SQL下的业务耗尽专项核dump不变/in_transaction=False；真实I/O失败不假称已清理。tail三份控制已在64槽内，不再额外叠63以扩大总额度。这些规则明确落入storage._transaction及JobStore状态票传播的原writer申请，不靠新wrapper猴补。

### 9.2 与原风险/预算的交互核对

r3实际diff没有撤销profile1 opaque保真/全历史碰撞拒升级、profile-aware历史解释、同事务metadata写gate、ontology scope禁止ownership详情侧写或active-tail headroom准入。升级先排空tail/独占writer，旧profile/hash/metadata声明不能在已受理Job中间替换。tail仍只覆盖atomic changeset/runNULL；不把异常run写进未预算的run_terminal；reconcile重开有独立control admission，不恢复丢失的内存预算后自动domain重派。

现正例为4304B / SHA256 `53094f8b90033e138d0716e15522c60a5e7dbade65050a47dccaad6023aa984f`，`a2c996`实际读取并核字段。独立算式63控制槽/phase、16128work/phase，8个业务phase额外129024，原63725248加该项为63854272，低于67108864；tail示例4194304中已有的控制不双加。这仍是staticAccountedSubtotal，未证明实际20Helper/8Rdf/8phase/每phase入层数及H/P/Q/Tail候选充分性。新版明确真实组数不符必须在新phase/子调用前重算拒绝/修profile，至少完整五字段正例实际跑完并逐hook核费后才能关闭可执行性门；不能只测全拒绝，也不把本静态余量称性能收益。

### 9.3 最终结论与仍有的明确门

**对上述81538B固定主稿，方案阶段独立审查通过，无未解决实质P2；技术路线可实施，可交root决定分阶段精确授权。**本结论不是产品已实现、测试Pass或直接开启全部writer。原三P2及r2两控制补充已按实际新身份核对关闭，首稿/旧意见与真实证据保持历史，不倒写通过。

应保留的实施/决策门：root仍须选择legacy/identifier冲突范围和metadata语义profile方案；S1先供保真只读源，M实际写开放依赖S2同版本持久proof与原确认链。碰撞旧库仍按旧语义可读，保真迁移需另批，不静默认证或删旧字段。原scope、位置/备份、跨层完整引用、T10包版本与实际T02消费供方未到不靠fixture补齐。active tail对同Store未知旧writer的资源拒绝是需root批准的功能启用约束，不能宣传无条件零旧行为变化。

实现后必须按固定同版源码交实际cost inventory和全部深hook、首写增长/临时峰值/失败tail/嵌套cleanup证明，再跑真实全字段正例及±1/失败累计/重开/旧reader拒新profile/完整undo矩阵；生产App/真人/双OS、完整FR200–204及指定双外审/CI/正常develop/远端门保留。本轮仍只docs与静态文件/AST/算式/格式核验，没有产品import、DB、测试、故障子进程、网络/模型/GUI/native或stage/commit。
