# T01 dispatch 与永久 child 排空：实现与供方边界

本实现交付私有准入消费机制、有限执行账和真实 child／stdio 排空。真实 I06/native dispatch issuer、完整 Coordinator Job terminal producer、Store／worker／VFS 来源仍待各唯一 owner 交付；本阶段不能发布正式生产 dispatch 或据此宣告库级 released。

## 固定输入与范围

实施授权为仓库外 `iteration-control/2026-10-21-weekly-release/T01-dispatch-permanent-drain-implementation-authorization.md`，11686B/SHA256 `4ea8dede0ad911a0715f907ce8216364847f9f18324c9309b88d3542b0c93a2e`；固定主方案为 `506e15744e47fd36f43bdbd645f6e65526cf0bf4` 的 `docs/iterations/T01/dispatch-and-permanent-drain-plan.md`，46175B/SHA256 `fc341d0c24ffb91ac170a0f393616e22551a8e22a53b35ac373346012e97b368`，包括独审处置后的 §12。

新树 `.worktrees/T01-dispatch-permanent-drain`，branch `feature/weekly-t01-dispatch-permanent-drain`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。单独 adoption `e79d9d4f2e2fbdfe29217be5e4cc03f8bcce82e1` 逐项从 `423b7e4c799f188cf2ce6e8e7121893ce85624cd` 采用原52项。原51项继续只读；三 writer 为 engine.ts、新 engine-lifecycle.ts、新专项 test。完整相对5f为54产品／test，不能只以最后三项描述候选。[采用回执](../../reviews/T01/dispatch-and-permanent-drain/adoption-receipt.json)保留逐项原 bytes／SHA。

AGENTS 为15852B/SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，保留 unstaged，不纳入采用或产品提交。common、原流程资料、所有旧tests、main/index、TaskService、canonical／registry、Python Coordinator／Store／worker、依赖／锁／build／CI 均未取得写权。

## 同步入口、原始材料与最终写前门

`request`、`health`、`requestWithDispatch` 在调用当下先有限检查／拥有输入、预留业务数量及完整 envelope 的保守字节额度，随后才进入原 `#operation` 微任务及 `#ensure`。初次 hello／退避的等待者同样计账。严格 schema 仍使用现同版 contracts；自有输入拒绝 getter、循环、非 JSON 类型、非法 surrogate、非有限数，并界深度32、节点262144、UTF8／转义后字节262144。节点反射会创建 key 列表，现 registry 仍先 read 后界；本实现没有证明进程所有临时分配或 RSS 已界住。

启动前没有 Session，因此 reservation 的 `originalRequest` 是入口真实冻结的 `{method,params}`，没有伪 Session UUID。字节预留为此材料的编码长度加192B envelope余量，只是数值占额，尚无可发送frame。hello 后构造一次冻结完整 `actualRequest`，复用同一已拥有 params，形成唯一 LF frame／hash。私有 `DispatchFacts` 同时带同一 `originalRequest`、完整 `actualRequest`、privateTicket、actualSupervisor／actualChildOwner、generation、原 hello hostClientId、engineSessionId、profile、registryHash、engineVersion、真实 limits、frameBytes 与 sourceEpoch。实际 encoded frame 必须落在原预留及协商预算内；预留可能略保守拒绝临界大帧。

`attachDispatchSource` 只能一次且须在任何业务接纳前；已starting或已有generation的对象也不能事后附着，以免在真实首IO后倒授权。失败的附着不能回退成裸业务旁路。附着后的所有业务包括裸request共门，缺原dispatch拒绝；内部旧 transport 回归接口没有生产 scope。来源缺失时 guarded 调用 write0。缺真实 producer 的 attached job.create 在启动前拒绝。真实首IO先于 hello，故附着的 `checkBeforeSpawnSync` 还必须由实际位置／lease issuer 核当前候选；缺它的真实权限不得启动生产候选。旧内部自有fixture可运行不等于正式原装配可用。

供方通过 `installInvalidationSink` 取得仅否定能力：其 scope／lease／cohort 撤销先同步推进此实际 source 的 epoch，再改其私有 registry，最后通知；安全整数耗尽封闭，不 wrap。不得从 sink、品牌、UUID、hash、DTO或成功 callback 生成 scope。

编码、hash、producer预登记／绑定、observer注册、方法读取、write绑定、pending／timer 全在最后消费前完成。`checkAndConsumeDispatchSync` 的真实实现必须在最后核同／consume到return之间只触自己的不可变事实／私有登记，禁止外调、getter、thenable、Promise及再入。返回值必须 undefined。T01 紧接着只核私有 source 同一附着／epoch未变／未封闭及 stopped／current session／generation，再标 write-attempted、调用预绑定的真实 stdin.write。同步撤销、stop或再入不会穿过该 fence。已消费但本地拒绝不得重发原 permit。

write进入前标 attempted；write false、抛错、callback错误、逻辑超时仍保持 write-attempted。没有自动 replay、改 operationId 或把未知变未发送。原 FailureOrigin／originatingPromise 品牌保留；派生操作没有替代原TaskService错误来源。

## 三种独立寿命与严格迟到回包

`logicalOutcome` 仅是原 public Promise。普通严格匹配 response 可以证明该次 foreground handler 已返回并结 `operationExecution:{kind:foreground-returned}`；先逻辑超时的帧保留原 ticket／child／session／完整frame绑定，仅同当前实际 session 的严格原回包才能结底层，不重新 resolve 已超时 Promise。旧 unmatched 诊断仍保留；未知 strict3 response 仍按原规则终止连接。

job.create queued／running／cancelling 仅是受理，不结后台。相同未结 operation 不创建第二 background ticket／Job；attached 原dispatch重复拒绝。旧内部无 source 的重复 create 若已知同完整 params／jobId，读取真实 job.get 当前结果，不重发原 create；这是回归兼容，不是许可重新标注或生产 completion 优先通道。job.cancel response 只证明 cancel handler 返回。

`transportOwnershipLifetime` 是该实际 Supervisor 自构造至永久 stop 的 child／自有三pipe／timer／listener／starting reservation 寿命。它既不结后台 Job，也不结 Store连接／事务、worker、外部后代、SQLite锁／SHM／映射、VFS、LocationLease或整个cohort。某真实 Job terminal 也不结这些独立 owner。没有实际供方的源保持 unknown 并占额，不以 TTL／空map／fulfilled Promise 消除。

## producer reservation、独立 completion 与观察清理

以下全部是消费机制合同，没有在这三 writer 中实现或 mint 生产 issuer。真实 owner 必须以实际 issuer incarnation、原dispatch／物理库绑定、原operation／request、privateTicket、原已知实现／限额／origin／claim／context／receipt／round材料，逐一核原件；未知原implementation不得取新 Session 值补出。

入口 job.create 先占本账128 watch之一，并同步调用 `ExecutionEvidenceProducer.reserveOperation` 占真实 producer 容量，只绑定当时实际已有的 Supervisor／privateTicket／原dispatch／同一 originalRequest／CompletionPort。reservation 不等于 bound、spawn许可或write许可。hello 后 `bindOperation(同一reservation,完整facts)` 核旧事实及新增真实Session，最多一个 observation，再 `observe` 注册一个终态回调。正常严格 create 回包才交 `bindAcceptedJob`；丢回包时 jobId 未知不能用 marker/null 发明受理／未受理。

`projectTerminal` 必须验证该真实 issuer 实际发出的 observation 与原 ticket，投影只允许 operationId／projectId／jobId／succeeded|failed|cancelled 四项，消费者另界4096B且逐原件核同。假对象、错 Job／ticket、错 incarnation 无解槽权。真实 terminal 释放原业务数量／frame；此时通知观察可能仍待清理。

`OwnedObservation.closeObservation()` 只是请求；其结果须由同一 producer 的 `projectObservationCleanup(issuedCleanup,原observation)` 认证真实注销／订阅结束来源。仅 Promise fulfilled／返回对象／删本地map无权解watch。失败保 terminal-cleanup-unknown；只留原ticket／Job／issuer／observation等有限身份，清掉完整原request／frame。每项消费者身份界4096B、全128即524288B；真实供方自己的闭包／WeakMap也必须同样界住，不能在其侧暗留原payload。对应通知owner的真实child+三pipe终态可回收该连接watch，但不会结原业务ticket；供方后来若仍持有原合法 terminal 来源，可独立投影原 Job 终态。

私有 `CompletionPort` 只供已登记 producer 为其当前已知 Job 发 job.get／job.subscribe／job.unsubscribe。每次都要当前真实 read dispatch，不能复用 create 的一次性permit或称health。只许原ticket／project／job，同一原ticket最多一个subscription，unsubscribe须核原subscriptionId；不能任意method／新job.create／cancel／renderer优先级。沿实际 schema、profile、frame与同步fence。当前连接不同于原通知owner时拒绝此通道；跨Session原物理重证明仍由后续真实resolution owner供给。

completion独立1个foreground／262144B预算，原业务满128也可取得真实对应观察结果；超时保inflight未知，严格迟到原回包前不再开第二poll。消费端不建poll timer（0≤1）；scheduler由真实供方在此上限内实现。server128订阅必须与真实TaskService共享；无余量应观察实际QUEUE_FULL并串行get，不能另假设新增128订阅。通知分派要求真实producer共用一个listener，内部最多128watch，不能每Job注册public listener；本实现没有通过fixture证明生产分派已接线。

## 所有旧／当前／starting child 与永久排空

先占 owned entry 再spawn，总2，starting单1。reader终止／逻辑拒绝／移除current不删除实际entry。每entry保实际ChildProcess和实际存在的stdin／stdout／stderr，child.close与各stream.closed全部满足，且starting finally实际结束、升级timer清理后，才回收。failed spawn亦等真实error／close；进入spawn后同步抛错而无实际handle，保unknown。只有尚未调用spawn且无child的取消才是never-created。

永久stop先撤新接纳／推进generation／封闭source，clear退避timer并同步reject该attempt自有deferred，让await／finally实际执行。重复stop幂等；晚continuation复查stopped。所有真实旧child均由同一集合持有；SIGTERM最多一次，1000ms后可SIGKILL一次，观察exit或close后不再kill。kill true／false／throw、exitCode、stdout end、destroy调用都不是排空证明。仅使用自有ChildProcess引用，不按泛PID或进程组收尾。

stopAndDrain重复返回同一永久operation。最多8个observe，waitMs正safe integer≤60000；observer超时只返回pending快照，不取消实际排空。永久transport receipt只由该本账真实终态形成，无无限历史child列表；短断线重连不结整个寿命。

工程拒绝界：业务≤实际maxPending≤128、预留／未结frame≤8388608B、单frame≤262144及协商上限、heartbeat1、completion1，hello与heartbeat不同时未结，普通+heartbeat+completion≤130；两public listener集合各64；owned2；starts5/60000ms，退避100..2000ms；原可信期限上限60000ms。没有新增CPU／性能／用户容量承诺。

## I06完整重建及后置生产闭环

I06 B-M四真实子集为private-root、credentials、configurations、audit，不能用engine空owner补profile／database／tasks／retirement。未来唯一T01装配须先登记实际Supervisor child来源及真实Store／worker，再初始化／ready；完整对象组为Supervisor、TaskService、ModelService、GatewayApplication、StoredResultSource、StoredFieldProjector、Core、LocalContext及真实grant／material。同UUID的新Supervisor必须整组新对象，重新context、同版hello、真实Store／Job／reconcile／目录／项目scope／LocationLease；不能复用旧source／projector／core／grant。候选失败只排空该候选，不关闭新active或共享profile仓库。

本三writer不修改上述消费者或I06实现。真实source／producer、未知JobId的唯一claim发现、跨Session物理重证明、Store／worker真实寿命、全main／TaskService／model生产旁路封闭、首IO、native／双目标OS真人、打包／指定双模型同版审查／CI／正常develop合并仍按原owner门禁后置。本阶段不把最终目标改成永久unknown；缺口须由各owner继续交具体真实来源。

## 验证记录

真实Node测试覆盖首次hello前129、逐次foreground超过128、逻辑超时／严格迟到、queued不结Job、满128下completion独立通路、清理未知watch保额、实际SIGTERM延迟／升级、后代延持stdio、旧current两child／第三spawn0、failed spawn、退避stop／starting finally、重复stop和有限observer。write false／throw／callback错误与缺stream close的controlled事件只计逻辑机制，不能代OS关闭证据。既有startup／TaskService真实Python回归保持原测试；来源与命令终态见本目录reviews中的checks及输入manifest，完整首失败日志保留独立临时路径与SHA。

未运行Electron／GUI／e2e／native／Keychain／正式模型／网络业务／付费／打包，也没有push／PR／merge。本文件没有把静态或fixture通过写成正式scope或全库released。

最终产品固定 `04ed06afca87ef8d21a71c68371bc19a849d98f8`（parent为上述adoption）。其完整 `npm run check` 工具ee810f／session20411，终态c60b32 exit0：23个Vitest文件、1167例通过（新专项42例）；ruff／构建／全部类型等同命令通过，pytest 2969通过／44既有skip。独立 `npm run verify:sources` 工具0eddb7 exit0，12归档源核同。原首失败与修复见 [checks.json](../../reviews/T01/dispatch-and-permanent-drain/checks.json)，54项现／Git相等指纹见 [candidate-manifest.json](../../reviews/T01/dispatch-and-permanent-drain/candidate-manifest.json)。独立agent审查尚待另行形成，作者不自行判Pass。

实际进程原件另以工具8c7cef exit0保全：冻结04ed产品／测试不变的42例专项全部通过，独立TMPDIR只读观察器保存29个真实Node PID、29份定向ps完整argv及28个marker文件的完整行前缀；一个marker可含多child incarnation。约386KiB原件留在独立/tmp路径，bytes／SHA与观察器源码身份见 [runtime-process-evidence.json](../../reviews/T01/dispatch-and-permanent-drain/runtime-process-evidence.json)。不把抽样前缀称全部最后写入，也不将逻辑fake计作真实进程。该证据补录不改产品或重跑无变化完整check。
