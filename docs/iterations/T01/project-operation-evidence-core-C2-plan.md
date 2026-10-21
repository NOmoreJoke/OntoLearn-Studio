# C2 原操作只读证据核心：实施申请方案

本方案申请完成正式 resolution 所需的**当前已打开库内证据核验核心**。它读取真实 claim、原受理材料和必要历史，不写数据库、不重新派发，也不认证原 dispatch、物理库或当前权限。最终正式服务仍须按固定 ff725 合同取得真实供方，再按全部条件返回 resolved；本阶段没有把最终目标改成永久 unknown。

当前仅有4190B方案准备授权，SHA256 `3a2fb6b04154bdc29fcda1d92c74cfe7c5e8438950ae55c7b49dd573d05d9195`。下列接口、代码路径、资源 guard 和测试均是具体申请，**未获得产品实施/运行授权**。C1 固定423b7e4和原59交付冻结，a33cc80仅新增根C1收口原字节。本方案不修改旧合同、C1说明/manifest/ZIP或任何产品/测试。

## 1. 已调查事实与明确缺口

依据固定 `379916267e5c36eebedb44d35a6636b9915ccd70` 的39602B合同 `ff725f2c0ee40cbdf61c9c4d27dfea1be3ccd2068df4399878b037976de4a5f3` 第3、6、7、8、9节，及固定 C1 `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 的实际源码。以下行号均为该ref：

| 真实切点                                                                                  | 已有行为及对本方案的约束                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| job_store.py:1015 `_accepted_job`                                                         | 核完整context fingerprint、原project/capability/input/confirmation/implementation/limits，读原snapshot、parameters、runConfig events/consumption、prepared，最后get_job。不能只收费claim/jobs后直接调用。 |
| job_store.py:1080 `get_job`                                                               | 核真实DTO/context对应及同版contract；不是terminal marker/result完整互证器。                                                                                                                               |
| job_store.py:776 `_job_prepared_plan`                                                     | 普通prepared与ChangeSet分派保严格namespace；普通actor仅是一项旧来源，不包含完整host/session。                                                                                                             |
| domain_changesets.py:842 `accepted_plan`、536 `_verify_plan`、678 `_receipt`              | 验完整prepared envelope、preview、segment blobs、参数、原确认回执。历史核验用host=None；传旧host会额外要求当前base/state仍相同，错误拒绝后续历史。origin须另从envelope和job_details原回执交叉对selector。 |
| project_lifecycle.py:214 `creation_context`，format3.py:587 `_history`、778 `receipt_for` | 创建必须核真实origin/seq1 application op/receipt；receipt_for实际跑到当前head的完整混合历史、当前域/app状态及完整集合，不能只读两个checkpoint。                                                           |
| storage.py:402 `_read`                                                                    | 会加入已有事务，故入口须先拒db.in_transaction；仅套该contextmanager不够。                                                                                                                                 |
| job_store.py:1444 `reconcile_jobs`、1978 `collect_cache`                                  | 前者真实写并改变非终态，严禁从本核心调用；后者可回收receipt结果payload，缺cache不否定原受理、也不能引发create/replay。                                                                                    |
| project_host.py:158 `_preflight`                                                          | 既有全库schema/表/列/raw行字节及重复history工作guard，不等于新的canonical UTF-8证据预算。                                                                                                                 |

已实读函数正文、相关DDL和传递调用；静态AST所列`_accepted_job→_project_snapshot/blob/_job_prepared_plan/get_job`及`state→_state→mapping_status→vector`形成需要查询门的实际闭包。源码bytes/SHA与完整52路径拟接收清单见本方案reviews目录 `fixed-foundation-inputs.json`（14521B，SHA `aef7b7c2d61cadb0eb8de73b5697f7ce78d384d217ff301bacd9038ff291f9cd`），不是从函数名推测。

现缺I06原dispatch物理绑定重新证明、当前库/项目read及catalog+creation-receipt-read能力、真实profile frame/page/envelope来源。普通Job context确实未记host/session；不能从actor、当前Session或UUID补归因。C2可信fixture与当前已开真实JobStore只能验证机制，不能消除上述缺口。正式适配缺原绑定时仍按合同 `unknown/physical-binding-unavailable`；当前权限不足先于内容返回。

## 2. 精确分支、采用与拟写范围

申请从批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 新建：

- 树：`.worktrees/T01-operation-evidence-core`。
- 分支：`feature/weekly-t01-operation-evidence-core`。
- 按上述清单逐52项从423b原Git bytes/SHA接收，单独adoption提交；不whole-commit、不开默认格式3、不复制旧docs/环境。52项全部只读，包括C1 lifecycle/job_store/storage/format3、reader、所有旧测试、canonical/main/worker/coordinator和I05 task-runtime。保AGENTS/common及64原保护文件原字节。
- 仅申请两个新writer：`packages/engine/src/ontolearn_engine/project/operation_evidence.py`、`packages/engine/tests/test_project_operation_evidence.py`。
- 实施时另列专属说明/原件目录经根冻结。本次只写主plan及 `docs/reviews/T01/project-operation-evidence-core-C2-plan/`，不提前创建新树、两个产品文件或fixture脚本。

未来相对5f产品/测试将为完整54项，而非只报两个新文件；初始52项维护权不转移。不需要改__init__、applications/domain_changesets、依赖、锁、协议/registry、主renderer/preload、build/CI。采用契约和查询门若实际不足，提交具体绕门SQL/调用栈与最小既有路径diff后另申；不能为了保两文件范围复制validator或写stub。潜在readhook涉及job_store `_accepted_job/get_job/_job_prepared_plan`，且storage snapshot/state/marker与format3 history也必须闭合，不能只改顶层三个方法自称充分；当前均未申请通用写权。

## 3. 私有输入与有限事实输出

拟唯一内部入口：

```text
read_operation_evidence(real_job_store, selector, *,
    maxEvidenceBytes, maxSelectorBytes, maxReturnBytes, readerLimits)
```

只接受可信owner已持有、完整启动Job-ready且target/actual3的真实JobStore及其同一已开连接，不接受path、connection factory、authority/scope布尔或复制JSON的物理绑定。没有JobStore薄公开服务、RPC路由或真实位置首IO。未知caller活动事务先拒，且不rollback caller事务。

selector**原样沿ff725第3节**，精确键/版本/重复operation与project一致；project.create带完整expectedRequest+originalOrigin，job还带projectId、已知UUID或null jobId、完整原expectedRequest及issuedImplementation/issuedLimits。复用当前同版contract对job.create/implementation/limits的严格校验，不另建schema或业务context；name、UUID、origin复用C1严格纯validator。原Implementation/Limits必须是原值，不能取当前默认值。

先迭代检查精确形状、标量/有限节点和安全整数、Unicode scalar，无NUL/surrogate/NaN/Infinity/bool冒整数；按严格schema只允许实际字段深度，并申请MAX_SELECTOR_DEPTH=32、节点数≤maxSelectorBytes作为独立有限guard。以有界迭代canonical编码累计selector长度，超限立即停止，不先deepcopy/一次性encode超大树。`maxEvidenceBytes`为可信调用者显式正safe integer≤67108864，无无限默认；maxSelectorBytes显式正值≤262144；maxReturnBytes显式正值≤131072。bool/零/负/无限/越界均invalid-input。readerLimits只读消费真实冻结ReadLimits实例，不另复制放宽。

内部输出申请精确临时union，名称刻意不等于正式resolution：

```text
{evidenceVersion:1,kind:'project.create',operationId,
 finding:'create-record',createResult:<C1真实原createResult>}
{evidenceVersion:1,kind:'job',operationId,
 finding:'job-record',job:<真实同版JobDTO>,originEvidence:'recorded'|'not-recorded'}
{evidenceVersion:1,kind:<selector.kind>,operationId,
 finding:'no-evidence'|'incomplete-evidence'}
```

`originEvidence='recorded'`只表示数据库内ChangeSet两份原材料与selector来源相同；不是权限/原物理dispatch认证。普通Job返回实际受理DTO但标not-recorded，供未来已授权适配决定unknown/origin-not-recorded；正式resolution的unknown分支不夹带这份DTO。创建的origin原值须完全相同，不同为身份冲突。该union是私有临时事实投影，不是新增公共DTO或另一意图账本，不含resolved/recoveryOnly/permissionGranted/true授权字段、路径、context正文或SQL。

真实充分记录与明显expectedRequest/knownJob/implementation/limits/来源不一致时identity-conflict，不返回他操作内容；缺claim只报no-evidence，不报notAccepted。损坏/缺引用但已开Store仍能读则incomplete-evidence；不能把SQLbusy/磁盘故障或预算超限伪装缺证。有限异常申请invalid-input、state、identity-conflict、resource-limit、unsupported-profile、storage-busy、storage-failure，外层只映射既有安全code/params，不展示原异常串。

## 4. 一次全新只读快照与真实查询门

入口检查后明确 `BEGIN`，同一connection内完成结构guard、所有费用探测、严格事实核验与有限结果构造，最后 `ROLLBACK` 释放读事务；成功也不COMMIT写。所有异常/BaseException/断连取消均finally释放本次事务与临时seen/缓存，不关闭owner Store/lease。没有SAVEPOINT、第二连接、临时表、snapshot/public_project/project_get/reconcile/create/commit或worker。

不覆盖连接owner现有authorizer或progress callback。C2自身通过私有门只允许固定读模板；专项额外在外部SQLite authorizer禁止所有INSERT/UPDATE/DELETE/DDL/ATTACH/DETACH/写PRAGMA下运行，允许BEGIN/ROLLBACK及明确只读PRAGMA。该authorizer不是计费器，无法看每行PK，prepare缓存也不提供逐次收费证明。

申请模块内私有`EvidenceView`和`MeteredGate`，**不继承/构造Store、不替换real_store.\_db、不提供capability工厂**。view只绑定下列原实现到自身；所有能查SQL的方法self必须为view，不能透传`getattr(real_store,name)`的真实boundmethod，否则会绕门。其_db门调用同一个实际connection，没有合成库/行、修改真实Store属性或第二validator。

| 只读方法组          | 具体绑定/调用方式                                                                                                                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Job                 | JobStore原 `_project/_valid/blob/_plan/_job_prepared_plan/_accepted_job/get_job`；_plan保staticmethod语义。                                                                                                              |
| Domain              | Store原 `revision/vector/_has_retirements/_read/state/_state/mapping_status/marker/load_snapshot/_project_snapshot/_snapshot_state/_definition`；classmethod沿原Store类纯校验，不把classmethod错误绑定view类导致缺方法。 |
| Run                 | 如需要其读投影，Store原 `_run/progress/_history`均经view；但history里的replayable=false不是损坏证据的通过证明，C2仍严格核具体round关系。                                                                                 |
| Existing validators | `creation_context/format3.receipt_for/_history`、applications原claim/confirmation/plan、domain_changesets原accepted_plan及内部verify/receipt均传view；静态纯canonical/hash/contract函数沿原实现。                        |

门在实际connection的execute、fetchone/fetchmany/fetchall和cursor迭代处先捕获SQLite错误，转换为独立`EvidenceControl(Exception)`，不能继承sqlite3.Error或ValueError/KeyError/TypeError/OverflowError等旧helper捕获族。按sqlite_errorcode主码把BUSY/LOCKED映射storage-busy，I/O等映射storage-failure；未知模板和资源超限也使用该穿透控制异常。原因是固定format3.receipt_for会把sqlite3.DatabaseError含busy/I/O转成Format3Fault结构错误；若等外层再区分已太迟。实际SQL错误先在门处安全分类，入口finally释放后才映射；普通真实格式/关系损坏才是incomplete。cleanup失败保首因并记录有限cleanup状态，不泄露原SQL/异常字符串。

门声明精确SQL模板、来源表/列/完整PK、参数谓词、排序和投影。没有任意SQL passthrough/`__getattr__`回退；未知模板或不可审计传递调用unsupported-profile，不继续返回充分事实。VIEW只能读冻结class字段/contract/actual3；不暴露构造器、_transaction或写方法。class/property/staticmethod绑定需要专测，禁止空集/true stub。

每条实际SELECT先定位命中实际行并探费用，新增行预算累计通过后才把任何完整TEXT/blob投影交原validator。固定schema均普通rowid表；定位先只取整数rowid，不先fetchall可能超大的PK。批量先SQL count与行数界，再按有限locator批次探各完整行费用，整条查询预算足够才读正文，不能把LIMIT截断当完整history。`marker` JOIN按commits与commit_evidence分别计真实行；UNION/project过滤按各实际来源去重，投影仍由同conn原SQL生成，保持sqlite.Row索引/keys/dict语义。

原validator的后续引用由门继续收费，故可以逐层“预探该行→扣费→读/解析→发现新引用”，不要求在未读context前猜所有引用；没有任何完整行先被原helper读取再补扣。当前事务内按(table,rowid)去重，同时读回完整PK核条件；行id不持久化、不充业务身份或物理库标识。去重只免重复费用，不省关系校验。

## 5. canonical UTF-8证据额度与SQL先界

冻结新额度口径：每个实际表行按**固定全部列名→原SQL typed值**组成的canonical对象UTF-8字节计一次。TEXT payload/context/dto保原SQL字符串（含JSON空白、引号和转义），不先parse成另一对象才收费；NULL=4B，INTEGER按真实十进制含负号，TEXT按JSON字符串编码。该计价对象只在本次内存中，不是新持久context。

对m列完整行：`2 + max(m-1,0) + m + Σlen(canonical(columnName).utf8) + ΣL(value)`。JSON payload在context内嵌、又在snapshot/blob独立实际行存在，是两处材料，分别收费；同一实际snapshot被多次引用只扣一次。不能按内容hash合并不同表/PK，也不能按访问次数重复扣。

严格分四阶段，所有编码分支都相同：A.廉价SQL仅返回rowid/typeof、TEXT字符数n/存储字节数u/NUL存在和有限行数，不能在同一SELECT顺便执行完整replace/scanner费用；B.先按下述明确算式累计预扣工作guard；通过后才发精确canonical费用SQL；C.完整行费用与本次seen去重累计通过maxEvidence后；D.才允许原完整TEXT/body SELECT投影。不得让SQL先完成计价再由Python查工作界。预探本身也计查询和下述工作额。整个过程不返回未收费TEXT正文，不用接收整TEXT的Python UDF计价。固定schema对类型逐列检查，未批准BLOB/REAL或非法编码有限结构失败，不隐式coerce。已读完整行后再用原canonical独立核费用相同，不同整次失败，不能以写回修正。

精确TEXT探测拟两路，并申请额外固定工作guard：

1. 实核PRAGMA encoding=UTF-8。令u为`length(CAST(t AS BLOB))`，N(c)=`length(t)-length(replace(t,char(c),''))`，先拒NUL。`L(t)=2+u+N(34)+N(92)+Σ{8,9,10,12,13}N(c)+5Σ其余1..31 N(c)`。固定次数SQL内建扫描，准确覆盖引号/反斜杠/控制字符；不依赖JSON1或数据库默认编码猜测。
2. UTF-16LE/BE不能套CAST长度充UTF-8，也不凭方便永久拒绝同schema旧库。拟SQL `unicode(substr(t,i,1))` 按scalar计1/2/3/4或JSON转义2/6字节。该路径可能O(n²)，先只取字符数n，以`Σ(n+1)²`保守预扣工作量，未通过前不运行逐字符scanner。

申请独立固定`MAX_PROBE_WORK=536870912`抽象扫描工作单位。每首次探测的TEXT明确收费：UTF8为`256 + 160*(u+1)`，portable为`256 + 16*(n+1)^2`；NULL/INTEGER每字段64，每行固定128。UTF8的33项replace计数各按扫描/拷贝/结果length等最多4次原字节规模预留132u，再为metadata/NUL/UTF8验证等预留到160u，常数256覆盖标量操作。这里是明确工程收费单位，不假称严格SQLite opcode或CPU/RSS上界；portable的16倍平方同样是保守拒绝政策，非耗时换算。全局基础SQL metadata的每个候选TEXT也按其编码路径预探额计，schema字段不免收费；现reader aggregate工作guard另计。重复行可复用已核精确费用免再次运行探测，但每次真实读取工作仍按下一段计。20MiB ASCII即使证据尚不足64MiB也在33次replace前拒绝，百万portable scalar在scanner前拒绝。

另申请`MAX_QUERY_COUNT=65536`，包括schema/aggregate、metadata、费用、正文及原helper全部实际SQL执行；开事务前为BEGIN和最终ROLLBACK各保留1控制槽，业务/探测SELECT最多65534次且每次execute前预扣1。finally的ROLLBACK直接走独立控制路径，不能被已耗尽的业务门、证据/probe/read-work额度或未知模板guard阻止；这两个控制槽计入总额，不另造无限控制通道。若BEGIN未成功且无本次活动事务不做伪ROLLBACK；本次已开始则所有失败/取消都尝试实际释放，cleanup异常保首因并向owner标清存储失败，不能伪称已关闭。`MAX_READ_WORK=536870912`独立累计：每query固定128，加本次将物化的每实际行完整canonical费用（重复读取照计，不与seen免证据费用混淆）；批量先界行数/费用并预扣后再发正文SELECT，metadata/probe只返回int/null/固定枚举值；每次执行前按`128 + 128*固定返回列数*已界命中行数`预留其读取工作上界，不先读结果再决定够不够，整数须可安全表示且列数≤32；SQL聚合单行同理。若多个helpers反复load同一snapshot或mapping_status每owner再vector，证据每行只扣一次，查询次数和读取工作每次照扣。无SQL缓存回调冒充逐调用计数；有限cursor每次交付也不能绕过此前整查询预扣。三个固定上界均为本方案待批准的新内部工程guard，不能静默取同值reader字段当同一政策；任何一个超限均穿透resource-limit，不截断。

不新增/覆盖未知progress callback；如owner已有可信组合opcode/cancel guard可外层保留。本方案不以尚未到位的callback自称SQL执行时间保证；现固定schema/raw guard和预扣工作量只是有限工程界。若portable probe无法静态证明精确/有限或实现需额外owner hook，先交具体反例和切点申请；不以Python UDF先读整TEXT凑“先界”。未来专项须验证UTF8/UTF16、scalar边界/控制字符/非法TEXT和工作±1，不在本方案声称已运行。

selector、结果编码先逐scalar按字符预计canonical UTF8长度，累计通过后才分块escape/encode并拼有限结构；节点≤maxSelectorBytes、深度≤32。不能直接用JSONEncoder.iterencode的chunk作预算充分保证：它对20万个U+0001可先产生1200002B的单chunk；超大scalar先被完整转义后才len(chunk.encode())已经违反先界。对象key与值都走同一标量先界，canonical排序只在已界定有限keys后进行，不先构造超额完整编码再比较。结果≤maxReturnBytes，未来正式caller负责计算其≤min(131072,真实maxPageBytes,实际frame减实际envelope)；selector同理≤min(262144,实际frame可用)。C2只接显式有限数值，fixture数值不是已经交付真实profile/许可。

## 6. 完整实际行与引用闭包

所有表名为固定schema，列为该表全列；下表描述选择范围，完整PK/列从实际DDL固定进门，不接renderer表名。

| 分支              | 必须先收费后物化的实际行集合                                                                                                                                                                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 公共              | app_format/job_format实际单行；public_projects真实public→internal映射、projects；operation唯一operation_claims。读取schema SQL正文同样先界并收费；只返回count/length的guard不是payload物化。                                                                                         |
| Job受理           | claim→唯一jobs完整行(dto/context/fingerprint/run)；context.input.inputSnapshotId→snapshots；parametersHash→job_blobs(project,ref)；runConfig.eventsRef和eventConsumptionRef→实际blob。claimed jobId非null时精确核knownJob，跨project/kind先冲突。                                    |
| 普通prepared      | job_plans(ref)完整行、job_confirmations(id)完整行，原snapshot/base/plan_hash/diff_hash/ref/actor/permission核同；不给其actor补engineSessionId。                                                                                                                                      |
| ChangeSet         | 原envelope/preview完整before/after/control/manifest，全部segmentBlobRefs的job_blobs，envelope参数及input snapshot；confirmationRef的job_confirmations+job_details原确认回执。不是只核digest/头字段或最后一段。                                                                       |
| 创建              | C1 claim完整context、app_format逻辑证据、真实public映射、origin、seq1 app operation、immutable创建receipt；调用C1三immutable行核同及完整混合history。                                                                                                                                |
| 全必要混合history | 目标项目app_projects/head、app_origins、全部app_operations、其app_receipts、genesis和所有app_checkpoints，各domainSnapshotRef的snapshots；commits+commit_evidence全部对应行，旧application claim及其prepared/confirmation、draft.restore目标CP。链一直核到当前head，后续操作不能省。 |
| 当前链末端        | projects、versions、definitions、facts、mapping_state、definition_retirements和app_projects/app_drafts/app_learning/app_assistance实际目标project行；state/vector/application_state虽不返回仍是validator输入。mapping_status会再读vector，去重但不漏。                               |
| terminal结果      | resultRef→job_results和results完整实际行，核job/project/snapshot/implementation/投影和resultId关系；payload若存在完整收费后严格校验，若已回收为NULL不补cache。当前stale/current缓存不作为原受理身份，不调用result_get/_result_rows的当前性/载荷可用要求来替代事实核证。              |
| rounds            | jobs.run→runs、该run全部rounds、run_terminal、初始正式snapshot及每轮不同类型的round snapshot；terminal evidence所引eventConsumption blob。见第8节逐状态互证，不把round snapshot按正式project snapshot拒绝。                                                                          |

rounds另有一条不能省的反向实际集合：无论jobs.run是否NULL，都先按`rounds WHERE job=实际JobId`定位、完整收费后读，逐行要求其run精确等于jobs.run；run=NULL时该集合必须空，非NULL时也不能存在同Job混到其他run的round。再按所指run读取全部rounds，反向核每行job=实际JobId，避免只沿jobs.run漏掉有结构关联的孤儿轮次。此无新增索引查询仍受原全库raw guard和新query/read工作界。run_terminal没有job列，不能扫同项目所有terminal JSON猜本Job关联，也不能将别Job的run当本Job；这里只沿真实run主键或结构化round.job关联核证，不承诺遍历全库任意未关联JSON损坏。

跨项目恶意引用若helper会先读实际行再核归属，也必须由门先收费后读，再有限拒绝；不把不存在行虚扣一份材料。全局唯一claim从operation等值查询完整发现，绝不走最近16个Job/当前Job列表/有marker集合。超过有限行/字节界整体拒绝，不截断。operation也丢失属于合同另项目录/Job发现，不纳入此单operation入口，不凭名字/最后一次时间认领原意图。

## 7. 原受理、来源和创建的核验顺序

1. 参数安全界与未知caller事务拒绝；新读BEGIN。核实际header3、固定Store/Job3 schema/catalog和全库有限raw guard，不迁移/修复。
2. 按唯一operation claim定位；无claim只报no-evidence。有claim先查namespace、public project和knownJob条件，明显冲突在任何内容返回前失败。
3. Job严格调用经view的`_accepted_job`，完整比expectedRequest、issuedImplementation/Limits；原context hash既与claim也与jobs行相同。不是重新derive当前依赖或拿新base重做plan。
4. ChangeSet调用原accepted_plan(host=None)，从真实envelope及确认detail receipt交叉核原host/session，再逐值对selector.originalOrigin；普通Job没有两项持久来源则not-recorded，不补造也不猜actor。
5. 创建调用C1creation_context(view,internal,operation)及format3.receipt_for(view,...)，核实际严格原receipt而非仅自洽模型；expectedRequest/origin全值不同拒冲突。后续metadata/domain推进不重算原createResult，也不要求项目仍空或仍同名。
6. 加上第8节实际状态/结果互证，构造第3节有限事实投影；不足证据与存储错误分开。结果预算通过后释放读事务；未来正式adapter还须在内容可见前完成当前scope与原物理dispatch核验。

不调用全库format3.validate或_validate_job3后声称只收费目标闭包：它们分别读取全部snapshot/所有项目history、全部claim/jobs及prepared。初始ready是可信owner前置；本次保固定schema/catalog+全库SQLaggregate硬guard，并严格核目标完整闭包。若将来实际必须再全库语义验证，所有实际读也须经门收费，并明确申请相应范围；不能用ready免掉目标材料校验。

## 8. 各Job状态、真实提交与cache

| 实际情况                  | 核验与内部事实                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| queued/running/cancelling | 完整claim/context/DTO即已受理事实；不要求marker。marker存在时按真实关联验证，不能null→notAccepted/重派；正在运行不由本核心等待/续跑。                                                                                                                                                                                                                                                                                                                                              |
| failed/cancelled          | 允许无atomic marker；有marker或round进度必须验证相应真实证据，不能清除它们或把已有部分提交当成功全部完成。stateVersion/error/resultRef沿真实DTO。                                                                                                                                                                                                                                                                                                                                  |
| succeeded、mode none      | 核真实results/job_results关系与可用payload，不强求领域marker；cache回收不抹掉真实终态。                                                                                                                                                                                                                                                                                                                                                                                            |
| succeeded、mode atomic    | 必须真实commits+commit_evidence、DTO marker、同operation/job/project、snapshot/plan hash与format3 app receipt/完整history相符。若结果payload尚在，核唯一commit.receipt.v1行六项cells对应marker；坏receipt/incomplete不得只凭DTO放行。                                                                                                                                                                                                                                              |
| mode rounds               | run=NULL且committedProgress=None、state非succeeded是合法已受理，包括queued、尚未start_job_run的running/cancelling和未开run便failed/cancelled；不要求虚构runs/terminal。run存在而0轮、progress=None时running/cancelling合法，failed/cancelled有run_terminal且其committedProgress可None。run存在后核其归属/原snapshot/config/implementation与受理材料，全部已提交round连续/operation/job及对应project/run/number/state，last progress与DTO一致；不能因无round或null marker否定受理。 |
| rounds成功                | 在前项上核run_terminal.status=succeeded、evidence.jobId/progress/reachedMaxRounds、末snapshot的pending/consumed与eventConsumptionRef完整原blob；若result payload存在，核run.summary.v1及round audit实际对应。history.replayable=false仅是不可重放，不代替这些严格关系校验。                                                                                                                                                                                                        |
| cache evicted             | results.payload=NULL可合法发生，包括receipt；仍核immutable app receipt/history+marker及result/job_results归属来证明原受理/真实提交。没有必要immutable证据则incomplete；不生成receipt、不回填cache、不承诺重建结果正文。                                                                                                                                                                                                                                                            |

结果完整字段再冻结：results.dependencies按原受理snapshot/Job依赖vector核同、job_results.manifests等于原context.manifests、projection精确为原definitionId/scope/parametersHash；kind沿真实_publish_job capability→expected_kind映射，不根据当前UI猜。cache_key必须等于Store.publish原公式digest({project:internal,kind,snapshot:原inputSnapshotId,dependencies:真实vector,implementation:原implementation})。payload存在时每row走同版row validator、rowId及ordinal各自唯一、原排序/完整receipt或run summary/audit规则；不只核归属而漏掉已读全行字段损坏。当前result_state/current_results/job_current不是原受理身份，缺cache不得恢复或补造。

成功/失败/取消以及DTO markers的相互约束复用原contract，再加真实底层互证；不接受客户端状态或仅schema通过。普通Job可能完成全部这些事实核验却仍not-recorded，正式归因缺口继续存在。复制A到B后C2只说明当前B内事实；所有origin/UUID/hash相同也不能换成A原dispatch证明。

## 9. 有限资源、当前未解决风险与供方请求

全库guard只读消费同版ReadLimits的schema对象/SQL字节、表≤64/列≤32、所有raw rows/bytes及`bytes*(1+app_operations+snapshots)`；保持其原SQL编码口径，不与maxEvidenceBytes混淆。canonical证据累加、rowid/PK去重/查询次数/临时解析都在本次事务有限集合内，异常即释放，无cursor/长期内存意图。结果不附全部context/before/after或任意错误正文；不得以截断藏预算问题。

现有启动Store/Job3校验可能在C2入口前物化全snapshot/claims/context/prepared，没有C2预算保护；原ChangePreview构造完整before/after/diff也有既有分配风险。此方案不修改启动、迁移或preview，不宣称解决RSS/耗时或Q5容量；字节与工作guard是拒绝界，必须后续实际测量，不能量化未实测收益。

具体后续供方请求（不是已到接口）：

- I06：原dispatch→原真实库位置身份捕获及跨Session/撤销后可重新证明的不可JSON重造能力；当前库/项目read与catalog+creation-receipt-read窄scope、真实lease/首IO边界。A→B复制不能通用。
- T01 engine与I05：可信持有的原request、issuedImplementation/Limits、原host/session/generation/operation与真实dispatch关联；当前profile maxFrame/maxPage及实际envelope预算。不能从当前默认/renderer字段补旧值。
- canonical owner：正式注册/安全错误映射与严格同版公开selector/result、真实Host路由。C2不为编译提前复制未批准schema或建第二协议。
- 普通Job来源若未来要求充分：必须另冻结真正生产origin的Job context新版本/兼容/迁移政策，保旧hash；C2如实not-recorded，不自行加字段。

缺以上供方不阻本内部证据核验方案与未来自有临时库机制实施，但阻正式resolved/位置和权限放行。另并行dispatch永久排空方案由根独立授权、独立新docs负责，不与本C2产品范围混写。

## 10. 待批准的真实验收矩阵与命令

当前未运行以下任一产品/DB/子进程测试。未来只在新C2树、其独立环境、真实临时SQLite执行；每次保实际命令终态exit和完整stdout/stderr/首fail，不用后续shell成功遮退出码。

| 组              | 必须真实构造与反例                                                                                                                                                                                                                                                                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 受理发现        | queued无marker，running/cancelling/三terminal；unknown jobId从唯一claim找到第17条以前Job；knownJob冲突、跨project/kind、缺claim/孤儿不被收编。                                                                                                                                                                                                                |
| 精确身份        | 原完整request、input每字段、confirmation、issuedImplementation/Limits逐字段错配；bool/NaN/未知字段/巨大标量在深复制/正文查询前拒绝。                                                                                                                                                                                                                          |
| 来源            | 普通Job/not-recorded，普通actor不是host+session；ChangeSet真实preview→完整paged确认→accepted Job，原envelope/detail任何host/session/requestHash/引用错配均拒；后续base推进仍读原确认。                                                                                                                                                                        |
| 创建/历史       | 真C1创建、原回执丢失、后续metadata/domain/draft.restore仍恢复原事实；修前伪创建claim借domain receipt反例必须拒，缺genesis/seq1/后续CP/claim坏hash不修。                                                                                                                                                                                                       |
| terminal/cache  | atomic/read/rounds各状态、run=NULL与已开run零轮合法非成功状态、runNULL反有rounds.job=本Job或同Job跨run的结构矛盾、receipt cells/marker/resultRef/归属/dependencies/manifests/kind/cache_key/row唯一错配；cache回收后受理/immutable提交事实保留且不补payload；failed/cancelled部分round及坏terminal/consumption拒绝。                                          |
| 精确证据费用    | 独立SQLite实际全列canonical参考额做-1/0/+1；共享snapshot/同row三次读取只扣一次，不同PK同payload各扣，JOIN两行及context内嵌材料和实际行均计。最后segment/detail/当前draft/后续CP超限在正文物化前拒。                                                                                                                                                           |
| SQL编码/工作    | UTF8和真实UTF16LE/BE同schema库，ASCII/汉字/emoji/引号/斜线/所有控制字符；NUL/非法TEXT有限拒。完整行NULL/负整数收费；probe、query count、重复read work三界各-1/0/+1；20MiB UTF8在费用SQL前拒、百万portable scalar在scanner前拒，iterencode巨scalar先界反例。                                                                                                   |
| 全局guard/输出  | 原ReadLimits每相关结构/row/byte/work界，selector/frame较小值、output/page/envelope较小值及-1/0/+1；无默认无限、无截断充分证据。fixture frame只证有限机制。                                                                                                                                                                                                    |
| 真零写/生命周期 | 外部authorizer禁全写、完整dump前后相同，trace恰BEGIN→读→ROLLBACK；unknown caller事务不回滚、第二连接/写helper调用断言未发生；execute/fetch/iterator各阶段实际SQLITE_BUSY/LOCKED/I/O经门穿透旧helper不误报incomplete；业务SELECT在query上限恰耗尽及±1资源失败仍执行保留ROLLBACK并核in_transaction=False；故障、取消、cleanup首因及真实关库重开保持原持久事实。 |
| 查询门闭合      | 原helper全部传递SQL经门；模拟未知模板fail closed；classmethod/staticmethod正确绑定；真实read值/PK/费用核同，不能因stub通过。                                                                                                                                                                                                                                  |
| 复制库边界      | 真实A→B逐字复制，内部B事实相同不声称A物理归因；未来正式adapter缺真实binding必须unknown。C2不造scope工厂去假测生产归因。                                                                                                                                                                                                                                       |

授权实施后拟运行：新增 `test_project_operation_evidence.py`、受影响既有Job/ChangeSet/应用/format3/reader/创建专项；随后完整 `npm run check` 和独立 `npm run verify:sources`，保44原skip，不开GUI/Electron/e2e/native/网络/模型。若只文档变更通过格式/Git/hash即可，不重复C1。复杂core独立agent审固定最终54候选与实际反例；指定GLM-5.3最高/M3.1-Flash xhigh真实同版双外审及CI/PR/develop合并仍是后续必要门。

## 11. 本方案交付与审批点

申请根先审本方案的两个新writer、52精确只读采用、EvidenceView全传递查询门、完整typed行计价、UTF16工作guard和有限事实union；有任何切点无法严格闭合则先交实际反例另批，不在实施中默扩。

本轮须完成独立方案审查与预算定点审、逐项意见处置、固定纯docs候选/ref、逐项bytes/SHA manifest及原始工具来源包。只执行文档格式/AST/Git/hash，不将计划测试写为Pass。当前C1、正式create/resolution、原physicalbinding/current_scope/首IO、全Host、双OS/真人、FR-001–006/804/44/57P0、指定双外审和CI/正常develop集成均保原边界；原完整Goal继续。
