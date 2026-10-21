# T01 下一实际功能阶段：正式 ChangeSet 领域事务服务计划

状态：依总控本轮指令准备的**待审计划**，尚未实施或取得新阶段授权。产品和测试固定 `fd3944a35aed05c279d7d0c2f9a077c84d99aaf2`，不修改已验17产品/8测试；此计划不将内部阶段改成父功能完成。原44项验收地图、FR-001–006/804、完整项目恢复、真实Agent/UI、指定双审及CI/合并范围全部保留。

## 1. 选择和具体结果

优先把现有 **`changeset.commit`** 从design-only接成真实领域Job，交付实际定义/引用与人工事实的预览、完整Diff、独立确认、唯一writer原子提交、选择性撤销、持久receipt及异常重开链。使用实际Store支持且可以验证的业务输入，不新增同义capability，不把test.atomic换名字，不给纯domain伪造metadata变更。

选择依据是当前真实代码：

| 已有基础                                            | 实际可复用与尚缺部分                                                                                                                                     |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ProjectTransactions.preview/commit/preview_undo`   | 实际Store.commit回滚预演、完整before/after/control、摘要与逐记录Diff、选择性补偿/ABA与引用冲突；纯私有，digest匹配不授人类权限。                         |
| `JobStore.prepare_plan`                             | 已有真实预验及同库prepared/confirmation表，但只返回两ref、准备时即签确认，普通计划未携带本线完整preview身份/control/intent，不能直接当本次人类确认入口。 |
| `create_job/_accepted_job/commit_job/operation_get` | 已把changeset.commit视为atomic写，已有全局kind=job claim、完整context与重试、Store提交+真实receipt结果+终态同事务；普通prepared检查不接compensate。      |
| Store3域操作记录                                    | 原Store.commit自动写operationSequence、完整checkpoint和域receipt；无需新claim种类、第二writer、业务表或DB格式迁移。                                      |
| canonical现capability                               | 现schema已枚举changeset.commit，registry/dependencyPolicy已有formal-write/confirmation/atomic定义；**实际仍design-only**。                               |
| Coordinator                                         | 当前只有test.*可执行，且仅test.atomic走commit_job；正式分支必须直接执行确定性Store事务，不能沿测试worker的ready rows制造业务结果。                       |

正式source链已有r4/完整表与纯材料合同，但尚缺批准parser三身份/真实Table/options、受信文件能力、proof/pin/受理撤销与持久生命周期。此时先做ChangeSet不依赖这些缺口；不复制未批准T03/I05实现。学习激活/辅助账本可在既有两表推进，但当前优先级低于真实领域写入。既有source/学习设计不重做。

## 2. 本阶段实际支持及完整父范围

本次typed业务输入支持人工asserted RDF事实增改删，以及ontology定义中Store已验证的`triples`、`singleValuedPredicates`与显式同项目`references`子集；同批引用闭包在最终状态校验。定义payload必须为精确已知结构，拒绝任意JSON、非object和未知字段，不把Store对其他opaque payload的宽容当产品支持。所触及记录的before与after都必须能以本typed子集完整表达；不得允许替换一个旧opaque定义成功、之后才说无法撤销。未触及的其他域定义仍保留且只按原引用/ownership规则校验，不冒称其语义已验证。撤销只受理本服务产生、具有完整正式证据且属于当前支持集合的目标ChangeSet。

这些输入会真正落入Store的definitions/facts、ownership检查、revision/vector与不可变历史。现Store结构/引用存在性保护不等于附录C完整本体、SHACL、规则、行为或查询语义；那些实际producer/codec仍由T02/T05等批准接口接入同一入口，不能另开写路。人工/Agent都应复用本服务；本阶段不用实际模型生成建议，故不能关闭T08真实路径或FR-804整项。

完整项目快照恢复仍须覆盖metadata/draft/learning/不可洗白辅助历史并独立确认覆盖清单。现私有`preview_restore`是**域快照**补偿，不能以“整个项目恢复”名义开放。本阶段交付撤销与失败后重开恢复，不注册全项目restore或用域restore缩减原需求；后续完整恢复计划仍依原地图S06/G01推进。

## 3. 唯一预览、完整Diff和真实确认边界

1. 新私有`project/domain_changesets.py`仅作为现单连接服务：规范化typed业务变更，经公开UUID→`JobStore._project`绑定，调用原`ProjectTransactions.preview`或`preview_undo`。同一预览冻结project/base/intent/target、完整before/after/control、原计划、summary与完整Diff；预验后正式域数据/marker/revision/历史不变。
2. prepared envelope采用明确版本化的普通ChangeSet命名空间，复用现`job_plans`，与旧test域plan/application plan严格分支。内容固定`preparedChangeSetVersion:1`、公开projectId、原hostClientId/engineSessionId和完整ChangePreview；ref为该完整canonical envelope的digest。原`ChangePreview.identity`、Store marker fingerprint、prepared ref与Job context fingerprint分别按各自定义核对，不能互换。只记录准备数据，**preview不签confirmation**。JobStore的create_job、_accepted_job、_validate_job3/reopen与commit_job均按明确capability+prepared版本分派，旧test/application分支原样保留，不只补首次create。
3. 不把完整Diff压成一行receipt或只回diffHash。完整Diff为一份canonical UTF-8 JSON bytes，以不可变manifest+有序分段存于既有同项目blob；manifest固定总bytes/hash/段数，每段固定ordinal、byteOffset、rawByteLength/hash。本阶段申请技术保护为完整Diff原bytes最多16777216、单段最多32768、至多512段；空Diff仍编码完整JSON空数组。**wire统一base64**，即使切在UTF-8字符内部也只按bytes重组，不得把半个字符decode成string。page实际base64+JSON全部开销同时服从maxPageItems/maxPageBytes和整个frame上限。分段/manifest各自先核既有put_blob整值262144B上限，总量/manifest/输出预算全部在保存prepared/segments前完整计算；超限明确RESOURCE_LIMIT、不留部分新准备记录、不签确认，不截断旧值。上述限额是本计划待批准的工程保护，不是Q5容量/内存/性能结论或永久产品能力承诺；不新增递归manifest/第二schema。
4. 页复用现同项目不可变cursor基础，绑定project、hostClientId/engineSessionId、preview/plan/diff/base、完整页口径与下一byteOffset。初页从0开始，下一位置只能用上一页已签cursor取得；最后页返回position=totalBytes的完成cursor，confirm必须核同绑定、未过期、确实到总长度的该cursor。复用现cursor TTL/记录上限/清理，不建第二授权账本；它只证明该受信连接取得完整分页链，不证明人类看过内容。重复同cursor幂等，错绑定/跳页拒绝。共享`src/index.ts`内实际Diff重组helper再核全部offset/长度/hash、最后整值UTF-8与JSON，拒绝漏段/乱序/改bytes；Node真实runtime测试必须调用该helper重组后再请求confirm。未来host只能在此helper通过且用户实际确认后调用confirm。有限单页输出不伪造read Job，不借result.page绕过Diff含义。
5. 确认是独立受信host动作：实际展示业务摘要和完整Diff后才可请求确认。renderer/Agent不传actor、permission、prepared/confirmation任意ref或`confirmed=true`。**当前Coordinator没有人类actor/write grant上下文，不把它说成现成接口**；本阶段只在当前专用stdio信任边界内，成功hello时保存该真实请求的clientId作为hostClientId，并以该值作为确认行的actor归因，现allowedProjects仍是项目许可来源。actor/clientId/session都不成为人类授权或外发授权证明。confirm不得接外部actor/write字段，必须与prepared内原hostClientId/engineSessionId相同，并核完整Diff完成cursor/previewHash；事务内再次校验base/前态/control及结构、引用、ownership。真正人类确认来源须由后续I06受信main/UI负责，不凭这些标识补造。
6. 本阶段的真实CLI/Node确认调用只证明**受信确认边界机制**。当前I06保留的preload/App尚无实际Diff/确认UI，原main也只在测试fixture中选择项目，不能据Node测试声称真人确认/正式新建打开已接通。需要总控向I06申请精确命名接线与trusted项目选择接口；本阶段不自行写其四文件，不新增generic invoke或自动点击确认。
7. confirm只有通过上述边界后才使用既有`job_confirmations`签发，绑定project/ref/base/planHash/actor/write；同原preview/host/Session的精确confirm重试返回原签发，不无限增加新凭据。新operation须重验当前host/Session/项目与原prepared确认来源，另一实例不能接管旧确认。已经claim的operation则**先**按原完整请求/context和持久凭据对账，不重新要求临时Session/cursor仍活；旧Job保持原actor归因，不能因换Session、当前版本推进而新建Job/换operation或重复写。重启后的新operation需要重新呈现/确认，不把持久ref存在当当前人类授权。

## 4. 有限正式契约与实际执行

仅在显式internal business3注册`changeset.preview`（change/undo两明确分支）、`changeset.diff.page`和`changeset.confirm`三个有限方法；提交复用`job.create`的既有`changeset.commit`，结果/订阅/取消/对账复用原Job接口。新方法只扩canonical中严格3分支和business3 methods；legacy2的旧defs/v2Runtime/default health/error与原test路径不放宽。registry使用明确profile级可用状态，不全局把design-only改成默认生产可用。

计划不落第二份JSON schema。实施时仅在唯一`v2/schema.json`定义精确DTO，TS/Python原helper加载同一份定义。preview参数明确project/base及typed edits或undo目标，返回公开projectId、previewHash/base/intent/target、summary、完整Diff manifest元数据；page只返回该冻结manifest的完整指定段；confirm不接客户端actor/permission，仅返回既有prepared/confirmation签发结果到可信host托管。新DTO的公共/宿主投影不得泄漏内部project字符串、DB路径或私有application receipt。

正式parameters由prepare服务对真实ChangeSet内容生成并存于同项目blob，不接受workMs/failRound/allocateBytes/rows等test控制参数；现inputSnapshot/definitionId/parametersHash/implementation按实际冻结内容与现changeset依赖policy绑定。提交采用已确认版本化prepared分支，完整保留intent/target/preview/control和允许的compensate。旧test/application两种命名空间及已保存hash精确兼容，新Job不能消费其凭据，反向亦然。

Coordinator在testMode=false且profile3时接受该正式capability，进入当前project writer调度和真实Job状态机，保留**两个线性化点**：create_job首先在受理事务持久化唯一claim+queued；后续commit_job另在一事务原子保存域状态/marker、Store3 sequence/checkpoint/receipt、Job receipt result与succeeded。受理后未提交可以保留真实failed/cancelled Job，不能承诺claim和最终domain commit在同一事务，也不删除原受理历史。

确定性ChangeSet分支不启动test worker：queued→running并实际通知，在commit闸前至少一次让出到正常请求dispatcher的await；取消线性化以Coordinator实际dispatch并持久接受cancel为准，**stdin读线程收到字节不等于cancel已受理**。随后检查cancelling/deadline并进入同步单连接事务，再验真实当前base/输入/引用/ownership和原Store提交；闸前已接受取消则零domain，commit完成后才接受的取消只返回succeeded事实，不追写失败。不得以固定睡眠或测试workMs人为延长生产确认，也不承诺同步SQLite中途能响应新取消。真实stdio测试需覆盖running通知后正常dispatcher先受理cancel并零domain，以及commit完成后cancel已终态两组；其调度控制如需机制fixture必须明确标记，不能把queued取消或hook注入冒称真实running取消。

业务receipt来自真实marker，完整核operation/job/planHash/revision/前后快照。queued受理、Job succeeded、receipt result与Store3私有receipt是不同证据；public operation.get继续输出既有公开commitMarker，不OR进私有格式。当前receipt绑定提交输入快照，不把它错误标成真实查询/推理结果或凭它证明所有consumer当前可用。

## 5. 精确申请路径与唯一writer

下列是**下一阶段申请**，不因本计划或未来维护权已经生效而提前修改：

| 产品路径（10条）                                                            | 必要修改                                                                                                                   |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py`（新增） | 真正typed业务规范化、既有preview/undo适配、完整Diff分段与重组身份；不持第二状态库。                                        |
| `packages/engine/src/ontolearn_engine/job_store.py`                         | 同库prepared/confirm/分段持久读取、capability精确plan分支、原actor/确认与全claim重试、正式commit完整preview/undo证据适配。 |
| `packages/engine/src/ontolearn_engine/coordinator.py`                       | 三有限3方法、原项目授权、正式changeset.commit调度与确定性atomic分支、取消/故障/恢复。                                      |
| `packages/contracts/v2/schema.json`                                         | 只在严格3增加上述DTO/分支，业务输入不使用任意JSON。                                                                        |
| `packages/contracts/v2/registry.json`                                       | profile级三个命名方法及既有changeset.commit实际可用状态。                                                                  |
| `packages/contracts/v2/fixtures.json`                                       | 完整跨端正反例/原bytes/page边界与registry同源更新，旧startup/sourceTable原值保留。                                         |
| `packages/contracts/v2/binding-regressions.json`                            | preview/page/confirm/Job/operation/错项目及命名空间绑定。                                                                  |
| `packages/contracts/src/v2.ts`                                              | 复用唯一canonical执行严格3新分支/匹配，不引入并行validator。                                                               |
| `packages/contracts/src/index.ts`                                           | 新有限DTO类型与实际Diff完整重组/校验helper，供Node验收与未来命名host接线。                                                 |
| `packages/contracts/python/contract_v2.py`                                  | 同canonical的严格3方法/资源绑定。                                                                                          |

新增测试仅四条：`packages/engine/tests/test_project_changeset_service.py`、`test_project_changeset_stdio.py`；`tests/unit/t01-changeset-canonical.test.ts`、`t01-changeset-runtime.test.ts`。不预列修改现有测试；若真实原检查暴露必要兼容迁移，先保首失败再精确申请唯一窗。

既有`transactions.py`、`storage.py`、`project/format3.py`、`applications.py`、`worker.py`、`protocol.py/resources.py`、dependencies/errors、所有main/preload/renderer/build/依赖/锁/CI本阶段不改。若实际复用无法保持必需不变量，先给具体反例和最小路径申请，不能无授权扩写；也不能通过砍掉完整Diff/撤销/失败原子验收来回避。未来main命名服务/项目选择+I06的Diff/确认交互另有精确接线阶段，本次未假称已批准。

## 6. 同候选真实验收

| ID                     | 必须实际证明                                                                                                                                                                                                                                                                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C01 实际输入与完整预览 | 临时真实Store3中新增两关联ontology定义及人工RDF事实，预览调用真实Store逻辑但完整库域状态/marker/历史不变；逐条before/after/control/summary与实际基线/预演全等。非object/未知定义、悬空引用、单值冲突和映射所有权冲突拒绝。                                                                                                                      |
| C02 完整Diff/预算      | 正常、多页、单条旧值大于一frame、UTF-8跨byte段、精确32768±1、16777216±1总预算、base64+JSON后page/frame边界；实际共享helper重组与原完整值/hash等。换project/preview/Session/cursor、跳页或未完成链不能通过engine confirm；漏段/乱序/改bytes不能通过consumer重组。后者不冒称engine知道UI实际展示，不能只用摘要或结果计数。                        |
| C03 真实确认与失效     | preview未签confirmation且不能提交；伪actor/permission/公开ref替换/跨项目拒绝；实际受信确认边界后签发唯一绑定。预览后同属性编辑A-01、仅retirement控制变化、base推进、确认前/提交前竞态均拒绝旧Diff且域零变更。真正人类UI是否展示完仍留未来隔离验收，不由CLI伪证。                                                                                |
| C04 正式Job与版本      | 真实Python CLI、testMode=false、profile3经命名preview/page/confirm→原job.create changeset.commit→subscribe/get/result.page/operation.get；实际definitions/facts、revision/vector、marker、sequence/checkpoint/receipt、Job/result完整相符。旧2/无显式3仍拒绝；无test worker或test参数，实际implementation为本引擎/lock身份。                    |
| C05 逐边界失败与重开   | 对prepared/confirm持久化、claim受理、正式提交中Store既有每个相关边界、sequence/checkpoint/receipt/result/terminal及外层commit前后，分别异常/模拟写失败/取消与真实子进程退出。事务内失败比较完整持久状态，允许的已受理Job终态独立列出；A-02零半批。commit后丢响应先原operation对账，不造新operation，旧marker/单claim/单receipt/版本只推进一次。 |
| C06 撤销与恢复         | 真正提交A后提交不相交B，再通过正式undo预览/确认/Job只补偿A并保留B；同记录后改、ABA、后续引用/所有权冲突则列影响并暂停，零域写入。undo本身为新operation/revision并保历史，不回拨计数。真实CLI重启后原Job/operation/receipt仍相符；缺早期正式证据拒绝，不补造。                                                                                   |
| C07 版本传播           | 实际定义/事实版本、当前依赖闭包和受影响缓存stale变化与完整before/after一致，无关定义/结果保留；undo仍前向推进。用真实Store已发布结果核失效机制，但不冒称T04查询/T05推理producer已联验。                                                                                                                                                         |
| C08 回归与包           | 受影响专项、独立代码审查、完整npm check及verify:sources；新同候选unsigned包/CLI正式ChangeSet+撤销/重开与canonical资源同源验证。当前宿主不启动Electron/native/e2e/HMR/审查应用。产品/测试/依赖变化后按实际影响重验，不沿用fd启动通过当新阶段通过。                                                                                               |

## 7. 审查、交接和后续

本计划先独立只读审查，关闭具体缺口后交总控作一次精确阶段决定。实施后记录完整输入/首失败/执行终态、固定Git与独立结论，不依赖总控亲自重跑所有矩阵。指定GLM-5.3最高与MiniMax M3.1-Flash/xhigh同最终候选全新双审、PR/CI/正常develop合并/远端验证不由本内部阶段替代；仍不提前push。

父功能继续：P01–P09项目生命周期/离线案例，S01–S06四触发与完整项目恢复，M02编辑器草稿/刷新，D01–D13真实领域consumer，L01真实学习检查/辅助，R01–R05正式host/Agent/native/真人验收。该步骤先把最少外部依赖的真实领域事务接到现Job链，不把其余项删除，也不以一个尚缺producer等待所有模块完工。
