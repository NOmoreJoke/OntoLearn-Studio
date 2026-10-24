# T01 正式 ChangeSet 业务服务计划独立审查

最终计划审查结论：固定计划 `39ebbf378386004eb9e8654bf9dbd7465e50d5215a87c55fde01cffc258d71e1` 无未解决的实质阻断，可按10产品/4新增测试的精确范围交root作阶段决定。下文初稿三项P2、首次修订关闭及根新增两项反例均保留为历史；最终两项定点关闭与新身份见尾段，不表示当前仍待补齐。本次未运行产品、测试或探针；计划意见不是实施授权，也不证明服务、真人UI或父FR已完成。

## 固定输入与实际审查边界

- 工作树HEAD实际为 `fd3944a35aed05c279d7d0c2f9a077c84d99aaf2`。
- 全文读取计划 `docs/iterations/T01/changeset-business-service-implementation-plan.md`，初读SHA256 `446c4dc9ffeae5b705ca7e0e0351c0c2cc5150aadf2d12f562bd5e3d3941a615`。下列行号指该输入；后续修订需另绑，不回写本初稿结论。
- 仅写本新报告，不修改产品、测试、作者计划或旧报告；没有执行产品/探针/GUI/Electron/native/e2e/HMR。旧task-runtime临时窗口已由根另行关闭、未来I05维护，本计划没有取得该路径新写权。
- 实际读回完整exec `a182c2`、`0fa626`、`50a4da`、`47140a`、`5f9633`、`5d9aa1`、`9bde39`、`cdf39f`均为只读命令。`cdf39f`输出包含已阅44项地图的重复长表并被工具截断，不将该输出称新一轮PRD全文复审；本轮只核本计划明确保留的父范围，不重开原设计/地图或扩大语义实现。

| 必要当前源码 | 实际SHA256 |
| --- | --- |
| engine/job_store.py | 541eececf30db5e2a0c6f60ca45e4ca10846c7d7cd3f29c5c2210c3a339ab30b |
| engine/coordinator.py | fbedf4bd10ec4eef0c3c4154eedb8cce5903498a46e8ffa3201dea245b18f23c |
| engine/storage.py | 2f8762aef48279f5d2e05fa8e27015e04a911f4fdc0748586570d194ff090776 |
| engine/project/transactions.py | 13a9f9a104e2f7d0d71ba4b7f66a7adfb40e32631d6d67a9dbd5835ae590a123 |
| engine/project/format3.py | 20f01692000f627586cb6d1eea0c09b3e2f0190705f779e511a41655d90ee0b1 |
| contracts/src/v2.ts | 2caea16b799e4af09ab74e27f84dad23da023d31ddf26b7ac2eb92c222a71073 |
| contracts/python/contract_v2.py | b33c865454ee3f1155466e9b62fdcbf6f0dbe6edc739e0c8c314760c02261e96 |
| contracts/v2/registry.json | 271800b8f3ca3946b71d9ca07da24c251a0842f66bf6f806b96ac1b1767ff9fa |
| contracts/v2/dependencies.json | dee118b368915df4172a77b875d31ce29ad8374cb5fce3915678f7f950cedad4 |

engine前缀为 `packages/engine/src/ontolearn_engine/`，contracts前缀为 `packages/`。

## 批准前需补清

### P2-P1：Diff字节传输、重组与确认的责任尚未闭合

位置：计划§3第3–5项（34–36行）、§4 DTO（44行）、C02（78行）。

计划规定raw段32768、UTF-8可跨段，页服从maxPageBytes/frame，但没有冻结wire编码。若半个多字节字符被当JSON string传送，不能无损重组；若采用base64，32768原bytes变为43692个编码字符，页/JSON封套开销也必须计入预算，不能按32768×pageSize估算。当前 `put_blob` 的整值canonical上限262144，cursor只保存绑定/位置，不自动替新Diff定义编码或完整manifest上限。

更实质的是C02声称漏页/乱序不能确认，但confirm只明确绑定previewHash，没有指定实际产品中的重组校验入口、读覆盖状态或确认完成凭据。单个完整Diff hash/持久ref不能证明本次host拿齐、按序重组了所有段；只有新测试内重组成功也不能当产品确认守卫。真正人类是否观看仍应留未来UI验收，不应让core伪证。

最小补齐：冻结raw UTF-8 canonical bytes、分段byte offset/index/总段数/各段与全值hash及wire编码；总量、manifest与最终页/response完整encoded预算在分配/写入前明确检查，超限不签确认。选定已申请路径内的真实重组机制/接口（可以是有限共享helper与受信host完成状态），明确引擎page/cursor验证、host完整重组验证和未来真人展示各自责任。C02把漏页、重排、重复、截断、假全hash分别落在实际负责的守卫上；不得由“confirm收到了预览hash”推导展示完成，也不需越权提前写main/UI。

### P2-P2：actor/write与Session确认来源的起点未具体定义

位置：计划§3第5、7项（36、38行）、C03（79行）。

当前Coordinator只有profile、allowed_projects及成功hello生成的Session；`_authorize`（158行）仅核项目白名单，没有actor/write grant字段。当前 `prepare_plan` 接受受信调用方提供actor/write，但它不是本计划所说“当前连接已建立main上下文”的现成实现。现 `job_confirmations` 七字段不含Session；create_job也没有caller actor参数。因此仅写“重验当前actor/确认来源”尚不足以产生可实施且能跨重开重试的合同。

触发反例：旧Session确认后进程退出，持久ref仍在；新Session使用它创建新operation，必须拒绝。与此同时，旧operation已受理/已提交时，同一原请求在新Session必须能按原claim/context读回，不能因旧Session死亡、base变化或当前actor换代而丢失原操作。若把当前Session/actor混进必须重新计算的稳定plan/Job fingerprint，或者在读取原claim之前统一做临时确认活性检查，两项要求会冲突。

最小补齐：明确内部受信actor及write权限从何现有可信配置/构造状态产生、在哪一步与项目/Session冻结（不是renderer字段，也不以clientId等同真人授权）；明确新operation使用的本实例/Session确认签发登记或不可伪来源检查及其生命周期。持久plan/confirmation与临时来源分别保存；既有claim分支先核当前项目权限、原完整请求和不可变context，再返回原Job/receipt，不重签/换ref/重算CAS；只有新operation分支要求本Session重新呈现与确认。可在已申请Coordinator/JobStore路径完成，不需修改main或发明真实用户身份系统。

### P2-P3：受理与提交两次线性化及无worker取消闸需明确

位置：计划§4执行段（48行）、C04/C05（80–81行）。

“claim、域状态/marker…与succeeded保持同事务”与当前实际边界不符：`create_job`（729行起）先在独立事务写claim+queued Job，`commit_job`（1074行起）才将领域变更、Store3历史/receipt、Job结果和succeeded放在另一个事务。既然queued可被查询/取消，不能再承诺claim与最终domain commit一起才持久。C05本已允许已受理Job终态，应把这两点明确对应，而非暗示零claim等于零领域提交。

无worker确定性分支也不能只去掉subprocess后连续start→同步commit：若之前没有实际调度让控制handler受理取消，就不能用queued取消或内部hook模拟，证明“running阶段取消先于commit闸”。stdin线程已读到取消bytes与Coordinator已dispatch并持久cancelling不是同一顺序。

最小补齐：明确受理事务=唯一claim+queued，提交事务=domain/marker/Store3 sequence/checkpoint/receipt+Job receipt result+succeeded；受理后失败允许保留该claim/失败或取消Job。写清确定性执行分支的真实可调度边界与提交闸，顺序以Coordinator已受理cancel/实际状态检查为准；同步SQLite事务中不承诺新请求可插入。C05用真实stdio分别证明queued取消、running但提交闸前已受理取消→零领域写、commit后取消→alreadyTerminal/既有成功事实，且异常/失响应重开不倒写失败。只需现Coordinator/JobStore和新增测试，不需worker或新的public测试控制参数。

## 兼容性与路径可行性

未发现必须先扩大10条产品路径的结构障碍：

- `ProjectTransactions.commit`（201行）已有完整preview identity/control前后核对、真实Store补偿与对账，`Store.commit`已有compensate/preview身份/控制参数，Store3域历史按实际marker fingerprint记录；可在JobStore的新prepared分支调用，不必改其底层。
- `job_plans`/`job_confirmations`可持久新版本化命名空间，`job_blobs`可存分段，`job_cursors`可绑定新kind。需要在JobStore明确按capability+版本分派：create_job、_accepted_job、_job_prepared_plan、_validate_job3重开、commit_job都必须识别同一新分支；不能只在新建路径放宽后导致重开拒绝。旧普通plan和application prepared envelope必须继续精确验证、双向不能互用。
- 新prepared envelope hash、ChangePreview.identity、Store marker fingerprint、Job context fingerprint是四类不同绑定。现commit_job直接把plan字典转Store kwargs，新分支需提取并验证真正preview/plan后走ProjectTransactions.commit；不能把envelope直接展开或把prepared hash当marker的planHash。public operation.get仍保留原commitMarker，私有Store3 receipt不并入公开DTO。
- 新3方法需在TS/Python专用匹配中直接绑定其返回/页/确认。当前matchesBusiness3Response在严格3验证后投影旧2并调用旧matchesResponse；未知3专属method会被旧2拒绝，不能只加schema/method枚举就宣称pending匹配已接通。此修改已在申请TS/Python路径内，不必放宽旧2。
- typed支持集合还应明确before/after闭包：若允许把旧opaque ontology payload替换为本阶段typed值，而undo因旧值不在支持集合被拒，便出现本服务能提交A却不能正式撤销A。最小做法是在preview阶段明确拒不具可逆证据/支持集合的触及前态，或在本typed子集内保证旧值完整无损还原；不要求现在实现附录C其他producer语义。

这些是实施时必须验证的具体交接点，不是声称它们已经实现或已实际测试。

## 父范围与验收判断

计划清楚保留原44项地图、FR-001–006/804、完整项目restore与学习/辅助缺口；把当前域snapshot补偿与整个项目恢复分开，没有把P1完整专业模式提前。四个新增测试应覆盖真实业务输入/Store领域写/正式undo及新Job路径，不能用改名test.atomic、假metadata变化或合成测试rows冒充业务结果。C01–C08总体覆盖预览/失效/正式提交/故障/撤销/依赖传播/包，补上三项合同后可作为本内部阶段的实施验收范围。

本阶段仍只证明受信host确认机制，不关闭实际人类Diff展示、I06命名bridge/项目选择、真实Agent A-01/A-02、完整项目恢复、真实消费者联验或native验收。指定GLM-5.3最高、MiniMax M3.1-Flash/xhigh、CI/正常合并/远端等原门保留。本审没有运行产品/探针或将fd启动通过迁移成新业务阶段通过。

## 修订版定点复核与关闭

本次只核作者对上述三P2及兼容提醒的实际修订，没有重开无变化设计或增加固定轮次。全文读回修订计划的完整exec `cc9874` exit0，计划SHA实际 `5eb576f029bdf652ff2f52c82a335cf977afeb57cdf8db807d82d323832271e8`，HEAD仍fd3944…aaf2；作者第一次因表格空格匹配失败的apply_patch未改文件，随后修订是文档变化，不算产品失败或实现证据。

| 初稿项 | 实际修订与关闭依据 | 仍保留的验收边界 |
| --- | --- | --- |
| P2-P1 Diff传输/重组/确认 | §3.3冻结canonical UTF-8 raw bytes，单段32768/总16777216/最多512段、byteOffset/ordinal/各段与整值hash；wire统一base64，含全部JSON/编码开销计page/frame预算，manifest与每blob先核262144上限；prepared/segments保存前预算，超限无部分新准备记录。§3.4由连续cursor链到totalBytes签完成cursor，confirm核同project/host/Session/preview/base及未过期完成链；真正的src/index产品helper核offset/缺段/乱序/长度/hash/最终UTF-8 JSON，Node真实runtime实际调用后才confirm。C02已分别列引擎链验证与consumer重组负例。 | 16MiB/32768/512是本计划待root批准的技术guard，非Q5/性能/永久能力承诺。完成cursor只证明本连接取得完整链，helper成功不证明人类看过；未来host/UI展示与真人确认另验。 |
| P2-P2 actor/Session与旧operation重试 | §3.2、3.5、3.7明确不声称已有actor/write grant：成功hello实际clientId仅作为hostClientId与确认actor归因，allowedProjects为现许可来源；prepared版本1明文绑定原project/host/engineSession和完整preview，confirm不收外部actor/write，核完成cursor与前态。新operation核本Session签发来源；已claim则先按原请求/context/持久凭据对账，不再要求临时Session/cursor存活，不换Job/ref或原actor。精确confirm重试返原签发。 | clientId/Session不是人类授权、跨进程凭据或实际UI证明。重启后新operation仍重呈现/确认，旧operation不得借重试变更完整请求；实施时需真实两分支反例与权限检查，不以持久ref存在代替当前来源。 |
| P2-P3 两线性化点/取消 | §4明确受理事务claim+queued与后续domain/marker/Store3历史/receipt/Job result+succeeded提交事务分开，受理后未提交可保留原failed/cancelled Job。无worker执行在running通知后、commit闸前实际await让正常dispatcher处理控制；以cancel真正dispatch/持久接受定顺序，不以stdin字节到达定顺序。运行中先受理cancel零domain与提交后alreadyTerminal两组列为真实stdio验收。 | 不承诺同步SQLite事务中响应新取消，不以固定sleep/test参数延长生产，不用queued取消或hook伪称running取消。需要机制fixture时明确它控制的调度范围；失响应仍原operation对账，不倒写成功为失败。 |

兼容提醒亦已在§2、§3.2及§4落明：触及before/after均在typed子集完整可逆，不支持的旧opaque前态在preview阶段拒绝；JobStore按capability+prepared版本覆盖create、accepted重试、重开validator与commit，不只放宽首次create。四种hash不互换；TS/Python新严格3方法/匹配仍在现申请路径，不通过放宽旧2解决。原test/application历史hash及新旧凭据隔离、无新schema/新writer、完整44项/FR/恢复/学习等父范围保持。

本轮未发现还需扩大产品路径的具体证据，也未执行任何产品或测试。计划层面可交root一次精确决定；后续真实实现仍须独立代码审查、各C01–C08实际证据、同候选原门及必要范围授权，不能将本最终计划意见写成服务已可用。

## 根新增两项反例的定点复核

本节保留首次计划闭合 `5eb576…271e8` 及上文初稿历史，不倒写为当时已经覆盖下列两项。根后续指出确认落盘但丢响应遇cursor过期/GC，以及撤销ABA/引用冲突无法从现异常直接取得完整影响；本轮只核这两项实际文档delta和必要当前接口，不重开其余已核设计，不执行产品/测试/探针。

实际读回exec `eb0263`、`0f21d6`均exit0，对应中间计划SHA `f1f12beec4a1fee4c553d99bda60bf4189118a9a28b4b9a20760e54133945389`；当前文档HEAD为 `dafe409bcc7ef5dc71d282678871bba9e66b4dfb`，相对fd3944基线的packages/apps/tests/scripts与依赖锁实际差异为空，不能误写文档HEAD仍是fd。另只读核原compensation.resolve历史交叠路径，源码SHA `99ecf0bb4383753accdc0df75f3564d058cfe9945203bc844b9739e0c51ea4cb`；没有修改底层补偿或将其执行作为探针。

### 根反例一：confirm已签发丢响应、cursor过期后的精确重试

计划§3.7–9明确首次签发与原签发回执分支，先核当前项目许可/原prepared类型和完整hash/原host与Session，再查持久回执。新typed回执复用现job_details三列表，以实际confirmation UUID为id，同一确认事务保存严格命名空间version1、原完整业务请求/hash和实际原签发响应，并与job_confirmations逐值互证；不混用ownership detail、不覆盖、不随cursor GC清除、不增新表/claim/generic detail接口。现JobStore路径有此写入与验证空间，不需要改Store/format3或新增第四方法。

原签发已存在且完整业务请求相同，直接只读返回原结果，cursor TTL/GC或后来base推进都不触发重签/新确认；缺失/不一致fail-closed，不能用当前cursor重建旧事实。仅首次签发检查live完成cursor、当前base/前态/control及结构约束。新Session仍先被来源绑定拒绝；新operation的当前base/来源检查与旧claim原请求重试继续独立。C03追加真实签发后丢响应、推进测试时钟并GC、同一confirmation/原库计数不变、新业务请求/新Session拒绝与旧operation跨重启对照，足以作为此机制实施验收。

随后实际定点读回exec `88c852` exit0，最终计划27888B/SHA `39ebbf378386004eb9e8654bf9dbd7465e50d5215a87c55fde01cffc258d71e1`：§3.4已将live cursor限定首次签发并显式让原回执优先；§3.7把完整原请求定义为canonical全部业务params+project/prepared/host/Session（含原完成cursor），排除每次变化的RPC id/timeout/retry计数。这样新RPC id的同业务重试不误拒，原业务字段/完成cursor变化才冲突。本项计划层关闭，尚待真实实现/故障反例，不声称其持久化已经运行通过。

### 根反例二：撤销冲突的完整实际影响与有限分页

当前ProjectTransactions.preview_undo的ProjectFault.resources只覆盖部分当前值差异；compensation.resolve还会因后续交叠（含ABA）、缺证据等抛Conflict(state)，Store的引用/ownership/单值检查同样不能从异常类别本身推导完整清单。原classify不识别ProjectFault，现有detail_get也不是公开命名方法；根反例成立，不能只回INTERNAL_ERROR/冲突码或解析异常文本冒称已列影响。

修订§3.1与§4明确preview ready/conflict有限成功union；conflict只用于真实同项目undo目标，返回冻结base/target、summary、impactComplete与完整impact manifest，没有prepared/confirmation写凭据。原diff.page以documentKind=diff|undo-impact分隔绑定和cursor；完成undo-impact分页不授confirm。实际影响从校验过的marker/目标前后快照/control、至冻结base的完整后续commit/evidence、当前references与受影响owner/slot只读构造，分别列全value-changed、later-edit含ABA、reference-block及ownership/single-value阻断；未知原因/不完整证据明确impactComplete=false并暂停，资源预算不足整体拒绝，不截尾后称complete。Store真实预演仍是唯一可提交判定，此投影不能授权绕过拒绝。

C06追加实际A→B改→C改回的全部B/C历史影响、后续引用、全页重组与原证据逐项全等、混文档cursor/冲突求confirm/job.create拒绝、缺证据不装完整与零领域写入，覆盖根的具体反例。该有限DTO/投影与分页可留在原10产品/4测试路径，不需公开generic detail.get、扩大错误catalog或修改底层补偿。本项计划层关闭；分类完整性、实际数据读回和分页预算仍须在实现阶段按新反例实测，不能由本只读文档意见提前登记产品完成。

最终仅更新本独立报告，既有三P2及44项父范围/双审/CI/native/真实UI等边界保持。最终当前意见以上述39ebbf固定计划为准，未发现新增需阻断root阶段决定的具体问题。
