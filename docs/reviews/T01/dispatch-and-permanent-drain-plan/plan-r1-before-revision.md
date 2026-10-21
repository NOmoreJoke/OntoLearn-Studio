# T01 dispatch 与永久 child 排空：精确实施方案

本方案从固定真实 Supervisor 出发，申请一个 main-private 同步写前准入切点、有限 child 所有权账和永久停止排空来源。当前仅文档准备；没有修改或执行产品。正式 scope、原物理 dispatch、Store/worker/native 释放及生产接线仍须各 owner 的真实来源，不由本方案的对象形状、Promise 或 fixture 代替。

## 1. 授权、固定输入和拟施工范围

实际根授权 `T01-dispatch-and-permanent-drain-plan-preparation.md` 为5480B，SHA256 `c74eb72aa29fb6dce5e77cd48c22df69c2845e99b1c9be41074844fb1f016caa`。本线C1产品固定 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`；现过程HEAD `a33cc80e82475e54d74b4e48c1fd32f32979983a`只新增C1根收口，C1原59、C2及所有产品均保持原字节。AGENTS15852B/78df和common17891B/e437已全文读；首合并输出中common被包装截断，随后工具606e90单独补读全文。

engine唯一源码起点为423b的 `apps/desktop/src/main/engine.ts`，26260B/SHA `6d55774068ca27a49958daeea9f4b1fa15614c95563ca28b8a768265ecd4365e`，全文实际读完。I06固定ffb的B方案§4.1/6/8只作待供合同和调用图依据，未采用e2c旧网关、canonical或cohort实现。现有Node官方类型/注释离线读取，未联网或启动新子进程。

拟独立树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-dispatch-permanent-drain`，分支 `feature/weekly-t01-dispatch-permanent-drain`，基线批准5f `5f910b52c69d86a1076b2032e5d3c63e715947f3`。建议逐路径精确采用423b的52项已核产品/测试，单独adoption，不采用C1流程资料或整个commit；完整ref/path/bytes/SHA见本方案reviews目录的 fixed-foundation-inputs.json。

申请产品/测试 writer仅三项：

| 路径                                                 | 必要责任                                                                                               |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `apps/desktop/src/main/engine.ts`                    | 现Supervisor内唯一接入写前门、先占child槽后spawn、全旧/当前/starting持有、停止和来源投影；不改公共协议 |
| 新 `apps/desktop/src/main/engine-lifecycle.ts`       | 私有有限child/dispatch/observer槽与来源关联；没有路径、scope/OS authority工厂、第二Job或持久意图表     |
| 新 `tests/unit/t01-dispatch-permanent-drain.test.ts` | 专项状态反例及真实自有Node子进程/完整stdio证据；不修改旧测试                                           |

采用52中除engine外51项继续只读，完整相对5f产品/测试为54路径，不能只报最后三writer。main/index、task-service、所有I06/worker/Store/canonical/native/build/锁/CI及旧tests均不在这次最小实现申请。若实际实施证明需要其他文件，先出具体反例与最小diff申请，不能在此窗口接公开消费。现在不建新树或创建上述产品/测试。

## 2. 已实际确认的生命周期与缺口

| 固定切点                                   | 当前事实与影响                                                                                                    |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `#operation`                               | Promise微任务只认证逻辑错误来源；不是实际操作或OS资源完成                                                         |
| `#ensure/#start`                           | stopped入口/退避后复查、单#starting与每分钟5次start；spawn返回后才形成session。速率限制不能界跨分钟仍活的旧child  |
| `#send`                                    | 只验当前session、pending数、原schema/整帧；安装timer/pending后直接stdin.write。没有cohort/scope原来源同步核验     |
| `#receive`                                 | 校验真实pending与同版response后删pending并resolve；job.create回queued只是已受理，后台任务仍可执行                 |
| `#finish`                                  | terminal、parser.stop、reject/清pending、移除#session后kill；1000ms升级kill timer只等close清除，没有永久owned集合 |
| `stop()`                                   | stopped=true、generation++、只finish当前session、清listener；无await，无所有旧child/starting实际排空结论          |
| stdout/end、child/error/close、stdin/error | 可触发逻辑finish；单end/error、exitCode/signalCode或kill返回都不是三条自有pipe和全部child终态                     |

当前pending上限128、heartbeat额外1；starts上限5/60000ms，退避100..2000ms，request/startup/handshake/heartbeat可信上限60000ms；stderr仅计最多16384B而不保正文。listener集合目前没有显式上限。新方案保持原握手、帧和期限语义，另加下面的所有权与留存上限，不能把原速率/pending限当永久排空已实现。

Python实际切点也已读：coordinator的job.create持久受理并排queued后立即返回；异步worker任务后续进行。`Coordinator.stop()`取消tasks并gather，serve finally再调用store.close，reader可能仍有阻塞OS读，cleanup_failures另记。T01 engine没有现成wire可核这些全部终态，不能将child退出推广成该链已完整释放。

## 3. 三种不同来源，不互相代替

1. **logicalOutcome**：这次request Promise的结果/错误/超时/用户停止等待；仍由原错误品牌和originatingPromise关系投影。先超时不删除底层实际执行事实。
2. **operationExecution**：按真实方法语义区分foreground handler与其派生后台Job。匹配原frame的真实普通同步RPC response可证该次foreground handler已经返回；它不证明全部Store/OS资源已释放。job.create派生Job的queued/running/cancelling均未终结；已terminal亦须与原完整claim/context/receipt/round证据一致。job.create受理回复只结foreground、不结后台Job来源。缺供方保持 `unknown`，不合成完成、notAccepted或自动改operation重派。
3. **transportOwnershipLifetime**：整个实际Supervisor自构造起、经所有短session/重连直到永久stop后，所创建全部child与本对象自有三pipe、timer/listener/starting reservation的持有寿命。只有这组真实终态齐备才结内部transport所有权来源；不是Store、外部后代进程、VFS、SQLite锁、LocationLease或整个cohort释放证明。

三个来源都绑定同一个实际Supervisor对象身份、真实会话/代际和原请求；不接受caller填 `released:true`、`count:0`、UUID相同或Promise.resolve作为完成证明。生产I06聚合必须分别登记engine child、Store connection/worker/native及其真实寿命，不因transport已结束省略其余。

### 3.1 方法分类与准确占槽终态

分类不是caller布尔选项，必须固定为本ref同版registry的methods与coordinator真实dispatch实现；新增/未知方法fail closed，不能从effect=read猜没有副作用。实际serve循环是 `emit(request(value))` 之后才 `await tick()`；request同步调用dispatch并返回严格response。由此只有相同真实child/session、原request id/method/正文绑定、同版matchesResponse校验的response，才可证明该次同步foreground handler返回。

| 固定方法                                                                                               | foreground来源何时结算/释放对应槽                                                                                                                                   | 不能据此结算的内容                                                                                 |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| hello、health、session.ping                                                                            | 匹配真实response后结本次控制handler；仍沿原握手/健康期限                                                                                                            | child寿命、库ready、当前权限                                                                       |
| project.get、job.get/list、result.get/current/page、operation.get、changeset.preview/diff.page/confirm | 匹配真实成功或业务错误response后，释放该foreground槽；这些当前均同步handler，某些会生成snapshot/cursor/确认等持久或会话对象，不能统称纯读                           | 整个Store/其他任务/返回对象所引用资源的释放；operation.get的null不是notAccepted                    |
| job.cancel                                                                                             | 匹配真实response结该次取消请求handler                                                                                                                               | 原Job后台执行；响应cancelling/accepted并不取消其原ticket                                           |
| job.subscribe/unsubscribe                                                                              | 匹配真实response结本次注册/注销handler                                                                                                                              | 其他订阅/原Job和整个coordinator；订阅由原TaskService/Coordinator真实owner维持，不给此RPC捏后台完成 |
| job.create                                                                                             | 先占一个原operation ticket；response结foreground。返回queued等非terminal时该ticket改持后台Job真实关联，继续占全局未结算槽；即使错误response也不能只凭错误码认未受理 | Job终态、worker结束、Store/锁释放。handler尾部失败可能发生在受理后，需真实claim对账，不能安全重试  |

普通foreground timeout后不能立刻释放，但若同一current child稍后给出严格匹配的原response，可经独立有限retained lookup结其真实foreground，不能再次resolve已超时logical Promise。现#receive对缺pending的业务3响应会终止session，因此实施时须先查该本对象保留的原request关联，仅把已核同迟到response作为completion evidence；未知id/错frame继续原异常政策。若旧session已finish/parser stop，缺响应来源仍unknown，不能将其当正常晚回复。

job.create后台ticket只由真正的Coordinator/Job证据供方结算，不由caller `background:false` 或T01方法名猜测成功释放。相同operation重试不得造第二ticket/第二Job，须按本对象实际原关联和真实claim核同；持久归因不充分时仍unknown。全局128槽满于128个真实未结后台Job时允许有限拒新业务；这是明确工程背压，不把正常同步只读RPC的每次已收到response永久留槽，也不承诺有无限额外查询通道。

## 4. 提议main-private接口与生产消费前置

以下是待根冻结的本线私有签名，不是公共DTO、RPC或现成实授权接口：

```text
EngineSupervisor.attachDispatchSource(actualSource) -> void
EngineSupervisor.requestWithDispatch(method, params, originalDispatch) -> DispatchOperation
DispatchOperation.logicalOutcome -> 原Promise
DispatchOperation.dispatchObservation -> 本对象只读的 not-written | write-attempted
DispatchOperation.operationExecution -> 待真实owner核验的独立终态来源
EngineSupervisor.stopAndDrain() -> 同一永久TransportDrainOperation
TransportDrainOperation.transportOwnershipLifetime -> 实际所有自有终态来源
TransportDrainOperation.observe({waitMs}) -> 有限 ended | pending/unknown 快照
```

`actualSource`只可由可信main装配时从真实I06 owner取得并绑定；它不是renderer对象、JSON重建的权限、任意callable或引擎自己mint的scope。它需在自身私有登记中持有profile/cohort/process incarnation、实际Supervisor引用、原dispatch/库物理绑定、当前scope/lease、host/session/generation及request完整值/实际已知版本与限额。T01只核同本对象/帧/会话并同步消费来源，不能从字段相同推真实物理权限。当前hello只公开engineVersion/registryHash/limits，不公开完整issuedImplementation；job.create的该值须由真实Job DTO/原context取得后归到原请求，不能在写前猜测或从新Session补出。若生产需要写前版本实证，canonical/Coordinator owner须另交确切producer与同版字段，不在这三writer中擅加wire。

attach只能一次，必须在该生产cohort第一笔业务frame前；重复attach、换实际engine对象或来源撤销均不能复用旧登记。缺真实供方时 `requestWithDispatch`在任何业务write前unsupported/permission失败、write0。内部fixture只证明准入门工作，不使生产附着可用。现有裸request是已批准内部transport/旧回归接口，**不带当前scope权限**；最终生产装配必须令已attach的Supervisor上所有业务路径（包括裸request）共用本门，裸调用没有原dispatch即拒绝。不得把本内部阶段旧fixture仍能运行当生产raw bypass获准。若后续main/TaskService/model消费者未全部关闭旁路，正式生产能力保持不发布，不能只挑新方法测试取绿。

保留现有stop():void兼容“请求永久停止”，让它进入同一永久停止状态机；它自身返回不提供drain receipt。stopAndDrain重复调用返回同一永久操作，不重复建reaper或签多个寿命来源。对象身份和receipt的检查仅防误接线，任何下层释放事实仍要来自真正owner。

### 4.1 source实际接入次序

为避免用“将来有safe callback”跳过生产者，本方案申请供方的三个明确同步动作：`recordValidatedSession(facts)`、`checkAndConsumeDispatchSync(originalDispatch,facts)`、`recordSessionTerminal(facts)`。facts含实际Supervisor引用、其私有owned/session标识、generation、hostClientId、engineSessionId、profile、registryHash、原hello limits与engineVersion；写前facts再含已冻结原request/编码hash及实际有的业务operation/project。这些不是renderer可提交的对象schema，也不是T01给I06签实授权。

hostClientId在当前 `#start`发hello之前生成一次并加入该Session不可变登记；不是收到hello后重新randomUUID。`#receive`已严格核真实pending hello、registry及帧预算后，先调用recordValidatedSession，供方核它已attach的同一实际Supervisor/真实cohort，再允许本session进入业务准入；该动作不得从hello字段生成scope。供方失败时不对外发布可用生产ready。重连得到新generation/session同样重新登记，但不结整个Supervisor寿命或复用旧session的单次dispatch。

`checkAndConsumeDispatchSync`只能以真实issuer已持有的原dispatch/current scope/lease/物理来源核同；无条件返回undefined的fixture只能证明机制路径，不能用于生产attach或宣称真实供方已交。它不返回通用permit/true授权；其真实实现/issuer构造与主装配调用链要由I06/T01各自独立审查。

`recordSessionTerminal`在引擎先同步撤本session新派发资格、固定逻辑首因后执行；失败不清内部unknown/owned entry，不能阻止本Supervisor停止接纳。它只失效该transport session的准入，不能充当永久cohort revoke或Store released。真正的operation completion为独立异步owner来源，须按§3.1/9交付，不复用这三个同步动作伪造完成。

## 5. 最后一个同步写前切点

**位置：** `#send`内，原严格校验、完整编码及字节预算、槽预留完成后，紧邻第一次真实 `session.child.stdin.write(encoded,...)`。不得在检查后插入await、Promise.then、用户listener/diagnostic或schema getter；使用已经冻结/自有的编码帧和解析原request，不能检查对象A后序列化已被改动的B。

按以下次序固定原事实：

1. 入口尚未永久stopped，未处于拒新接纳的quiescing；先界method/profile与完整输入/原帧、maxPending及全局dispatch字节/数量槽，拒绝不触write。只保唯一自有编码帧与原request绑定，禁止重新从renderer计算origin或scope。
2. 确认 `#session === session`、非terminal、generation等于Supervisor当前generation、hello.engineSessionId严格等于本session与原dispatch预期，真实child引用仍是该owned entry；不能以同UUID替新对象。原hostClientId取实际hello写入的clientId登记，不能另造当前字符串来认旧dispatch。
3. 对实际source调用一个精确的**同步核同/消费动作**。入参为实际Supervisor引用、owned child/session token、profile、generation、engineSessionId、完整原request及其固定编码hash/字节、实际存在的原业务operation/project、已真实取得的原profile版本/limits、原dispatch引用。供方在同同步动作内核其私有issuer登记、当前cohort/current scope/lease与原物理绑定；不存在的issuedImplementation或不适用的operation字段不补值，按上一节明确的供方缺口处理。成功仅消费这次原请求的一次permit，不能返回可复用授权或允许另帧。
4. 供方核验期间禁止引擎同步再入dispatch。它若触发stop/revoke/代际变化，返回后引擎立即重核stopped/current/owned entry，再决定write。critical段不运行任何外部通知；所有错误投影/diagnostic在未发送失败已固定之后进行。检查成功至stdin.write调用之间只有局部状态检查和一次私有写入，不再调用供方或其他可重入代码。
5. write前先把该entry标为 `write-attempted`；调用write抛错、callback报错、返回false、超时或断连均保“可能已部分/全部发出”，绝不降为not-written。只有写调用根本未发生的本地拒绝可取消未启动预留。write(false)表示backpressure，不能重写同frame；等待drain也不释放已发原operation。

这个临界段只约束可信main同事件循环中的顺序。外部OS撤权若不能由真实lease/fence在此边界兑现，供方必须拒绝/unsupported；不能声称JS同步本身原子覆盖OS文件替换、跨进程锁或实际内容IO。原dispatch捕获/重新证明由I06/native实际机制另交，不从migration_id/UUID/同正文补造。

**首IO不是hello之后才发生。** 当前#start spawn的business3引擎会在hello前打开/迁移Store，故本写前门不能倒授权该首位置IO。生产spawn须先由真实I06/native给足候选位置与lease准入；缺失时生产候选不spawn，不能先启动看hello再推位置安全。本内部三writer机制及受控临时child fixture只证明transport顺序，首内容IO供方另有精确批准窗口。

**控制frame单列：** hello只用于新child握手，依原startup/handshake/profile/registry期限，绑定真实owned child与新host client；session.ping是同会话心跳，占唯一control槽，不发业务权限。health只返回既有健康能力，不替scope或库ready；其他business读写均不得伪装ping/health绕门。protocol字段/hello固定2引导/selected2或3逻辑不改，不把permission/ready检查埋进未注册method。

## 6. child、starting和资源状态机

helper私有持有 `Map<ownedId,OwnedChild>`；ownedId只作本进程本对象定位，不作物理身份。entry在调用spawn前先占槽、状态reserved，登记真实generation候选和starting来源。spawn同步抛出且能证明没有ChildProcess返回时可结为never-created并释放该预留；spawn返回真实对象后立即登记child、三条实际stream及终态listener，再发布为session。不能先调用spawn再登记或只登记#session。

entry覆盖reserved/starting/current/retiring/unknown直到**真实关闭**；逻辑terminal与#session移除不删entry。#starting退避timer由同一永久所有权集合持有，永久stop同步取消可取消的未spawn等待并阻止其continuation；已过spawn调用的entry保留。即使启动失败、hello超时、旧session断开、晚spawn回调或stop与start交错，也必须留在同一集合。

每entry分别记录：child spawn/error/exit/close是否实际观察；stdin/stdout/stderr各自存在、error、end/finish、close；JSONL reader已stop、data listener已解绑/惰性丢弃、startup/heartbeat/kill timer清理。只有child close实际观察且所有实际存在自有stream close/可核closed，才允许该entry结本地transport终态；end/finish/destroyed不是close。缺stream只在失败spawn实际对象返回的null/undefined与对应失败/close事实一致时记not-created，不能补true。丢事件或不可观察保持unknown，不用exitCode猜close。

离线官方依据：@types/node child_process.d.ts明确killed不表示进程终止、kill信号可能不终止且PID复用有危险，失败spawn的stdin/stdout/stderr可为空；stream.d.ts明确destroyed只是destroy调用、closed在close事件之后成立、writableEnded不表示已flush。本方案不依赖未在本轮核验的“child close自动等于全部pipe关闭”概括，三pipe实际终态分别记录。未来真实子进程测试验证事件顺序/不遗漏；不由mock emit close充当OS证据。

退役请求只作用本Supervisor实际持有的child引用，不按用户PID或通用kill进程组。先禁止新写，按原策略请求SIGTERM，最多一个1000ms升级timer；已观察child exit/close的不再kill，避免把PID复用风险扩张为“再杀一次”；exit但pipe仍开则保留entry/unknown等待pipe真实终态，不因timer到自动released。kill失败保留真实持有与有限失败，不反复周期性重试。

永久stop的线性点先设stopped并递增generation，随后取消未开始的starting/retreat timer，撤销所有现/旧session继续dispatch资格，再遍历整个owned集合请求收尾。新ensure/start/request/attach全部同步拒绝。任何late continuation在spawn前重核stopped和预留epoch；若spawn已发生只能登记并排空，不能把产生的child遗忘。普通#finish/重连没有永久停止线性点，不能结ownershipLifetime或永久清I06grant。

## 7. 精确有限guard和清理

以下是申请冻结的工程拒绝界，尚非实测容量/性能结论：

| 集合/资源                         | 上界与先界顺序                                                            | 终态/失败策略                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| owned child与spawn预留            | 2（最多当前/starting一个+退役一个）；先占后spawn                          | 旧child不close时拒再spawn，不删unknown腾槽；原5starts/60000ms仍同时适用                                           |
| #starting                         | 1，含可取消退避等待及已reserved待发布                                     | stop先取消timer；continuation复查；不会因Promise早reject丢child                                                   |
| 跨所有session业务dispatch未结算槽 | ≤原可信maxPending（最多128），不是每session重新给128                      | 普通同步真实response释放foreground；job.create queued只转后台ticket不释放；timeout/abort无充分终态时保unknown占槽 |
| 保留原frame总字节                 | ≤8388608，单frame沿真实hello maxFrameBytes≤262144                         | 先界总额再retain，数量和字节均满足；不截断原request/context来腾槽                                                 |
| logical pending                   | 原每session≤128；唯一heartbeat控制额外1                                   | timeout只结logical pending，未结算来源另占有限槽；不重放frame                                                     |
| control frame                     | hello与ping分别最多1，不挤掉旧unknown业务来源                             | 沿原期限/会话，控制正文不当业务内容或实授权限                                                                     |
| listener                          | notification、connection各≤64；每owned child固定一组内部terminal listener | 超额在add前有限拒绝；不移除尚需终态的listener来通过停止                                                           |
| timer                             | starting退避1；每child startup1+heartbeat1+kill升级1；每logical pending1  | clear只取消本对象持有timer；kill升级只一次，无无界reaper interval                                                 |
| drain observer                    | 最多8个并发有限等待，waitMs正safe integer≤60000；永久操作自身仅1          | observer超时返回pending/unknown，不能settle真正寿命或删除资源                                                     |
| 已结来源保留                      | 已核终态且无订阅者后只留有限最终计数/同一永久receipt；未结槽不GC          | receipt固定版本与本对象WeakMap关联，无逐child无限历史列表                                                         |

frame字节界是已编码留存额，不能倒称所有旧Zod/JSON stringify临时分配已解决。新增入口应在复制/深clone前按固定schema、标量/深度和wire预算先界，再冻结一次编码；既有启动readFileSync(registry)先读后界262144、旧caller对象序列化分配风险需另列，未由本账自动解决。新child上限2改变高故障下的拒绝行为，必须在未来真实延迟close反例与完整回归实测，不承诺原来能不断重启时仍继续spawn。

未发出来源可确定撤销；普通已发foreground按§3.1匹配真实response结算，派生后台Job或缺充分结果的unknown仍须真实operation owner补齐终态或永久全链owner提供受审退出事实。不得用TTL/最后16个job/当前base/transport close自己清槽。如果跨Session原物理dispatch无法重证明，正式resolution保unknown；本机制不能增加持久localStorage/JSON/SQLite意图账本补归因。长期unknown可导致本Supervisor拒新业务，这是有限拒绝；不能为可用性遗忘未知执行。

## 8. I06四角色及完整重建握手

I06 B-M本轮只覆盖private-root、credentials、configurations、audit四个真实子集；profile/database/tasks/retirement缺席仍incomplete。engine不是给这四角色填一个假的空owner，它提供实际child transport来源，Store/worker/profile由各owner另给。I06 B-L目前仍是方案，不能把其拟签名当已消费API。

未来唯一装配者T01 main应先登记候选Supervisor永久child来源及真实Store/worker来源，再执行初始化/实际ready；I06 registry在动作前reserve实际cohort/profile引用。完整绑定对象组必须为：实际Supervisor、TaskService、ModelService、GatewayApplication、StoredResultSource、StoredFieldProjector、Core、LocalContext及其真实grant/material。名称只是e2c调用图职责，不复制未批Model DTO/canonical/网关代码。

同UUID但新的Supervisor引用必须创建整组新对象，重新本地context与同版hello/实际Store/Job/reconcile/目录/项目scope和真实LocationLease验证；旧readonly engine、source、projector/core及grant不得复用。候选初始化失败只排空该候选实际对象，不关闭新active或profile共享仓库。主指针交换、ready及权限仍由唯一T01 owner同步发布，I06不修改T01源码。

短断线与同Supervisor重连沿原TaskService generation恢复；不因此结永久寿命、清整个model grant。永久stop或永久所有权结束则I06应quiesce整组、撤grant/material并排空各实际底层链。profile共享根/仓库只有其全部实际旧/当前引用终态后才可迁移；零本地child不移除持久路径deny。

## 9. 必须实际交付的横向接口申请

| 供方/责任                                              | 精确需要的真实内容                                                                                                                                                           | 缺失结果                                                                |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| I06/native dispatch source                             | 原request/operation及issued版本/限额→实际Supervisor/host/session/generation/profile/cohort/current scope/lease/物理库的私有登记、撤销和同步消费动作；复制库/替换文件不能通用 | guarded业务write0、unsupported/permission failure；不能caller bool替代  |
| T01 Python coordinator/Store + I05剩余runtime协议owner | 每原operation持久claim与Job的受理/全部terminal、worker实际退出/任务清空、Store事务/连接close失败及原资源持有的来源；准确本对象/本child关联                                   | job.create queued只证明受理；C2只读facts可辅助，不当后台完成/OS release |
| T01/C2后续正式resolution                               | 完整原request/issuedImplementation/issuedLimits/原origin、唯一claim发现、不限last16、完整receipt/rounds；再加真实原physical binding/当前许可                                 | 当前C2方案不输出resolved；no marker/缺cache不推未受理，不自动replay     |
| I06 B-L repositories/model/transport                   | pre-admission、实际FS/credential/audit/socket终态和整个对象组的实际ownership；不能只等serial tail/包装abort                                                                  | 未结底层保持unknown，不以transport-owner receipt解除全cohort            |
| native/VFS + T03 build                                 | 同build实际SQLite VFS锁/SHM/映射/lease、跨进程/真实目标OS释放证据；依赖/打包精确delta                                                                                        | child/pipe已结束也不宣布库级released或生产首IO可用                      |
| T01 main/TaskService + canonical owner                 | 实际生产消费者全部走准入、主指针/ready/权限发布、现业务profile帧与原request绑定、必要同版协议新任务                                                                          | 不以新增helper可编译当生产路径已封闭，无共享额外写权                    |

没有现成Python wire提供全链operation完成；本方案不临时注册job.finished新通知、不造第二Job/intent表、不根据session死亡合成terminal。后续由唯一owner提出精确canonical/consumer producer变更另审。内存原frame/槽只作本进程有限在途关联，不是新持久业务权威。

## 10. 获批后必须实际运行的验收

当前全部是计划，未运行。未来专属测试要保完整命令/exit/stdout/stderr和真实自有进程身份，优先无GUI、专属临时脚本与stdio，不接用户进程或宽泛kill。

1. 写前guard对原完整request/hash、operation/project、actual Supervisor/child、host/session/generation、cohort/scope撤销/替换逐项错配：stdin write计数0；检查成功后同步stop/再入反例亦write0。已write callback失败/false/超时不变回not-written，同frame不重复写。
2. 真实Node child忽略SIGTERM、延迟退出或由其自有后代延持stdio；logical reject与kill先发生而close更晚，stopAndDrain真实寿命保持pending。按测试自有真实归属关闭后才观察child与三pipe全部终态；不以mock close替这一证据。
3. 多旧child/当前child、失败spawn、spawn返回后error/close、null stream、退避待spawn与stop竞态、晚spawn continuation、重复stop，均覆盖预留和实际entry；最大2时第三个spawn0，原5/min速率同时不放宽。
4. 单child exit但stream未close、stdout end但child仍活、stdin error、destroy调用未close、kill返回true/false均不提前settle。close以后不再kill；原handle未知不靠timer或TTL清理。
5. maxPending/全局dispatch128、8MiB retained、listener64、observer8、每项±1；正常同步RPC连续超过128次均由真实匹配response释放foreground，不累积耗尽；timeout先占、严格迟到response后可结foreground，queued回复不释后台operation槽。job.cancel回复不结原Job，同operation不造重复ticket；真实owner完成后仅释放对应原来源。所有guard在动作/留存前发生，拒绝不启动额外child或写frame。
6. hello/health/heartbeat同版/期限/registry hash/相同stdout chunk限制保留；hello/ping不能夹带业务授权。两旧profile回归继续，生产attached路径禁止裸request旁路；内部fixture通过不记真实scope/native生产证明。
7. 同Supervisor短断线后可按原政策重连，永久寿命未结；永久stop后request/ensure/spawn/attach均拒绝。新Supervisor复用旧UUID不能取旧operation、failure或drain来源，I06对象组需整组重建。
8. queued/running/cancelling/failed/cancelled/succeeded和原失响应：分别比实际claim/Job/receipt/rounds；Python后台还在时logical response不得结operation。缺物理绑定或必要owner时保持unknown，零重派。
9. 真实结果只证明本机自有Node child/pipe与机制，不能代macOS/Windows首发native、VFS/两OS真人、正式模型/位置切换或父57P0。实际集成后再跑对应完整check、source核验、隔离桌面/打包及指定双方同版全新审查、CI/正常合并。

## 11. 本轮交付与后续批准点

本轮只交主方案、52项精确输入清单、静态调查/固定引用与格式/hash原件；另由独立agent审查方案并逐项处置。没有新产品树、产品/tests/import/子进程/网络/模型/GUI/native运行，无push/PR/CI/merge。原Goal、完整FR/57P0、指定GLM-5.3最高与M3.1-Flash/xhigh同版新审门不变。

根下一次应分别冻结：三writer及52采用/51只读、上述工程上界和具体gate接口，内部child来源可验证范围；实际source/canonical/Store/worker/生产装配另列供方与消费窗口。只实现可独立验证的transport机制不会使最终目标变成永久unknown；正式来源和完整接线仍是同一完整目标的必要工作。
