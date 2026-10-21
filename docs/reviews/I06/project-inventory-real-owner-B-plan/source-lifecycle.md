# B 供方准备：固定源码生命周期与 underlying 排空事实

2026-10-21。仅静态研究和接口提案，不授权采用或修改旧产品。唯一输出为本文件。准备指令全文读回：4183B，SHA256 `869e9c9568a52776b212238506700735b58de3b15cd709941b99d294cd8264c9`。已读固定1f3 offer、根offer复核、A实施授权、A最终独立读回及收口；共同政策仍AGENTS78df/common e437。不执行产品/import、安装、测试/build、native/GUI、网络/凭据、Goal或push动作。

以下 `e2c269ad` 精确指 `e2c269ad78a78e1a042cadc93b1c81a874707153`；`6a38fcb8` 指 `6a38fcb8135343ba5e62a8a8effe57b18c3de00c`；批准消费base仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。所有引用为固定Git的 `ref:path:行`，不是工作树当前代码或已批准新T01 runtime事实。本文避免重复metadata/retired格式研究，只列其供方对生命周期闭合的必要关系。

## 1. 结论与最小采用闭包

原offer的八路径不是可直接从5f落地的完整gateway闭包，也不是B最小必采集合。B应先独立实现真实操作接纳、初始化/close及underlying追踪供方；完整模型gateway采用须另有逐路径授权和canonical前置。不得把为取得一个drain hook而复制整个旧gateway称为仅B供方接线。

- `e2c269ad:apps/desktop/src/main/model-gateway/model-service.ts:2–31` 依赖Model* DTO、modelGatewayError/modelInvalidRequestError和validateModelParams/Result/matchesModelResult；固定5f的contracts/index与v2没有这些model导出。整文件采用会引入未批准canonical依赖，不能以新空stub、第二契约或改T01路径绕过。
- `e2c269ad:apps/desktop/src/main/model-gateway/configuration-repository.ts:3–11` 运行时导入credentials schema、private-directory，以及stored-result-source的materialCanonical。该source又在 `e2c269ad:apps/desktop/src/main/model-gateway/stored-result-source.ts:3–7` 运行时导入contracts/v2 registry、error catalog和EngineError。因此仅取配置仓库也会静态拉入真实结果读取链。若B需拆独立私有canonical工具，必须单列新路径/原调用方delta并证明旧私有format1字节语义不变；本轮没有此改动授权。
- `e2c269ad:apps/desktop/src/main/model-gateway/gateway-application.ts:5–19,58–63` 组合core/source/projector；`gateway.ts:3–19` 组合credentials类型、policy、transport和await-boundary。后两者对实际排空至关重要，不能因原八路径未列而漏掉。
- `e2c269ad:apps/desktop/src/main/model-gateway/credentials.ts:2,28–33` 对Electron SafeStorage是type import；实际Electron构造入口在electron-safe-storage.ts。B独立供方不得为了测试生命周期触发该入口或真实加密后端。
- finite-fixture-policy属于原测试字段语义，不是B生命周期必要采用项；preload/UI/canonical/原平台测试均不因B自动进入写范围。

### 固定只读源表及建议责任

下表SHA全部由固定Git原始blob实际计算。`model-gateway/` 缩写仅用于列宽，完整前缀为 `apps/desktop/src/main/model-gateway/`。这些是输入身份，不是正式依赖批准或本轮产品写权。

| e2c269ad路径 | bytes | SHA256 | B建议角色 |
| --- | ---: | --- | --- |
| model-gateway/model-service.ts | 22132 | `0bfd4360cbaf086b143fbc209e68994cc65496f3f9bce7d3a0bc4609c5a28395` | I06未来整组供方；完整采用受model canonical前置限制 |
| model-gateway/gateway-application.ts | 13777 | `2542730ba42406c1b2ab86c30f3bacfac2386be2f537b1f166a0a1da2d64f1d4` | I06未来context/调用/间接source聚合 |
| model-gateway/stored-result-source.ts | 10155 | `b77f2acf2e93af1e212fa7d3539b63f0090800a86dcb4587d347c3fde0d8e2d3` | I06未来包装结果与RPC underlying分开 |
| model-gateway/stored-field-projector.ts | 10374 | `73b1d5e0b1c16f3559259817c7f6a2bd1105c090cfb4abb5fc4c956dc63fce8c` | I06未来catalog/refresh异步操作登记 |
| model-gateway/gateway.ts | 13893 | `3f6005fe33dba7275c0e7a45a640cd94e17e62dc1609347f1c644dcf2f610126` | 原八路径之外，若采用需精确申请；追踪credential/audit/transport实际操作 |
| model-gateway/transport.ts | 3256 | `ec417eabbe25cf2340df0f0fc3b82b86740b961f3ef0f84adaa40f923b43aa99` | 原八路径之外，若采用需精确申请；result与request/response/socket终态分离 |
| model-gateway/await-boundary.ts | 971 | `e0dd898dd90e12b31b76df04a0907288eb14533bb8dd15e8ebb24ed9fc581382` | 逻辑等待工具；通常可只读保留，不把它的结算当资源settled |
| model-gateway/policy.ts | 2486 | `dd09203ebe7e7f655cee40e01c84149a8c121e48ece916fa816cbc2c320d1ced` | 有限私有错误/输入依赖；无生命周期理由自动修改 |
| model-gateway/credentials.ts | 3366 | `8a56addc33468467a733614a96ff4f24489d06144afe44f4dafe873dbc10482f` | 原八路径之外，若采用需精确申请；同步加密调用与repository操作起止 |
| model-gateway/electron-safe-storage.ts | 653 | `724462829544f8c51b0fe1c6ed5335c7b1168cb9379baa7daf69641cf11e9b0e` | 真实Electron适配只读前置；B独立临时目录阶段不采用/调用 |
| model-gateway/private-directory.ts | 15060 | `40a9a5d52488a25d3958c171ac3e5df4272eed5d42a97f51a76ee5baeb015a88` | 由metadata供方线另列精确delta；本报告只要求真实FS/handle close终态 |
| model-gateway/configuration-repository.ts | 5292 | `535c66d17ac5172eaee4a5c4781f7e84af1bcad64eb522baa33bb14ad199b19d` | 内容仓库操作与init/close登记；不是metadata-only观察器 |
| model-gateway/ciphertext-repository.ts | 4225 | `31e4bed54746529cecbdd1100db6ccb19840ef1d5367090a5334964a2f01e41d` | 同上；不读密文来建立inventory |
| model-gateway/persistent-audit.ts | 4665 | `62d77f33293770b3c72a0ede6ab796115ac10ebad8def1e534790015c562f5a8` | 同上；已登记调用的收尾audit仍需计入drain |
| apps/desktop/src/main/index.ts | 12088 | `d88c1df806dc913b85a719026640ee6502762153c82c148e57aa32d5dbd9c60b` | T01唯一owner，只提局部cohort prepare/publish/abort接口 |
| apps/desktop/src/main/engine.ts | 18609 | `d1e8a6a55b718861809570864745d49ef0e9bec3271f49cc2bc4945c8cfdf8ca` | T01唯一owner，只提RPC实际终态、全部child永久stopAndDrain |
| apps/desktop/src/main/task-service.ts | 33131 | `7ed65bd689a8cfa445b4d349a1a996750f67c190600d0f46b2dceb324ebd0a68` | T01唯一owner，只提订阅/恢复/晚unsubscribe排空及可信项目生命周期 |

## 2. 实际完成Promise与资源终态不是同一件事

| 固定引用 | 当前实际动作 | B需要保留的区别 |
| --- | --- | --- |
| `e2c269ad:apps/desktop/src/main/index.ts:90–129,310–314` | 启动一次modelInitialization；顺序开三仓库，构造service，再写models；仅检查quitting | 当前没有重复初始化已发生的证据；未来多cohort prepare必须局部持有资源，初始化Promise/失败清理归原owner，晚完成不得写新全局 |
| `e2c269ad:apps/desktop/src/main/index.ts:77–89` | closeModels先清models，吞service.close错误，再allSettled仓库close并清全局 | 返回不保留逐资源失败，不是全部释放receipt；未来旧close不得清新cohort全局 |
| `e2c269ad:apps/desktop/src/main/index.ts:37–66` | before-quit只等待5秒race，然后dispose/stop/quit | UI/退出等待上界不代表OS调用结束；不能把race完成当released |
| `e2c269ad:apps/desktop/src/main/model-gateway/model-service.ts:190–204,529–535` | serial队列最多32，close关context且等tail | 只覆盖进入该串行队列的操作，不覆盖所有source/network，也不能证明其下层资源已settled |
| `e2c269ad:apps/desktop/src/main/model-gateway/model-service.ts:329–354,397–408` | getCatalog和preview独立await，并在回来后same(context) | 不在serial tail中；same拒旧结果解决安装问题，不是底层排空登记 |
| `e2c269ad:apps/desktop/src/main/model-gateway/model-service.ts:478–504` | invocation.completion晚回只在相同context且未closed时更新结果表 | 有late-install防线，但completion可能仅表示包装业务完成；不能据invocations终态释放underlying槽 |
| `e2c269ad:apps/desktop/src/main/model-gateway/gateway-application.ts:305–323,359–383` | active仅start登记；completion.finally删active；cancel/close abort，close返回void | catalog/select/preview/refresh亦须独立登记；close/active清理均不等所有实际RPC、凭据、audit、socket完成 |
| `e2c269ad:apps/desktop/src/main/model-gateway/gateway-application.ts:227–274` | refresh有5秒abort及返回后对象/源指纹复核 | 保护原选择语义，但abort结束逻辑等待不证明下层请求结束；复核仍不是live-current lease |
| `e2c269ad:apps/desktop/src/main/model-gateway/stored-field-projector.ts:160–169,184–200,282–286` | catalog/fresh/select await source；close置closed并清catalog/scopes | 无自己的underlying聚合receipt；不能漏掉未通过application.start产生的source调用 |
| `e2c269ad:apps/desktop/src/main/model-gateway/stored-result-source.ts:58–105,249–252` | close abort controllers；abort可先reject外层Promise；finally移active | 原engine.request仍可在途。即使active=0，也不代表真实RPC或Python读取完成 |
| `e2c269ad:apps/desktop/src/main/model-gateway/await-boundary.ts:5–35` | 5秒/abort先reject返回的Promise，原operation继续.then | 只停止等待，不替代实际operation终态；普通native包装Promise也可以过A品牌门 |
| `e2c269ad:apps/desktop/src/main/model-gateway/gateway.ts:250–255,325–350` | credential.read与audit.append经boundedWait；guard在await后复核 | 外层失败可早于凭据仓库/OS调用/audit真正完成；B须在包装前登记原操作 |
| `e2c269ad:apps/desktop/src/main/model-gateway/gateway.ts:369–387` | 失败/取消后还可能追加blocked/attempt-failed audit，最后删core pending | 排空顺序必须允许原调用必要收尾audit完成，再关闭audit仓库；不能core pending=0就释放其晚到append |
| `e2c269ad:apps/desktop/src/main/model-gateway/credentials.ts:44–81` | store中同步encrypt后await write；read await repository再同步decrypt | backend/同步OS调用不能靠JS timer撤销；必须在进入同步调用前登记，在实际返回后结算。B临时目录阶段不触发这些调用 |
| `e2c269ad:apps/desktop/src/main/model-gateway/transport.ts:14–21,35–69,70–89` | finish可先resolve/reject；redirect/limit/timeout/guard失败随后destroy；response end也可先完成业务结果 | 没有聚合request/response/socket实际close的独立Promise。destroy调用或业务成功不能冒充资源关闭；DNS/TLS/迟到事件无法证明结束时必须保unsettled/unknown |
| `e2c269ad:apps/desktop/src/main/model-gateway/private-directory.ts:428–443` | PrivateOperations登记Promise最多32；close等这些Promise结算后关目录 | 有仓库级登记，但没有真实owner/cohort receipt；部分handle.close在其他finally中被catch吞掉，失败不能变成“句柄已释放” |

网络已发送数据不可撤回。`e2c269ad:apps/desktop/src/main/model-gateway/gateway.ts:350–360` 与 `transport.ts:75–85` 有最终授权guard与request.end切点；B跟踪不能为了排空改变此发送规则、把取消等同未发送，或恢复旧grant。真实模型外发仍未获本阶段授权。

## 3. A track的先启动后登记缺口：必须先接纳再开始

精确固定A代码：`6a38fcb8:apps/desktop/src/main/security/project-cohort-lifecycle.ts:295–342` 接收一个已经存在的Promise，随后核owner/epoch/品牌/配额并登记。以下只是静态反例表达，不曾在本轮执行：

```ts
cohort.track(owner, 'network', sendOnce(endpoint, secret, body, signal, guard))
cohort.track(owner, 'initialize', ConfigurationRepository.open(location))
```

JavaScript先计算参数：sendOnce的Promise executor已在 `e2c269ad:apps/desktop/src/main/model-gateway/transport.ts:14–23` 创建request；仓库open的异步调用也已经开始执行，随后A才可能返回busy/stale/budget。A拒绝登记不能撤回刚开始的实际操作，也没有给它保留underlying槽。因此**不能直接用此调用写法证明先接纳/零IO**。

同样，`new Promise((resolve,reject)=>{ abort时reject; 原操作.then(resolve,reject) })` 本身是普通native Promise，可满足A的exact-prototype/own-keys门，却能先于原资源结束。`e2c269ad:apps/desktop/src/main/model-gateway/stored-result-source.ts:89–105` 正有这层包装。native品牌只防伪thenable/对象，不认证实际资源来源、完整登记或OS释放。

B必须在以下两个方案中明确冻结一个，不能静默假称A已支持：

1. **首选B本地pre-admission供方**：新的真实owner私有authority在启动任何命名操作前同步预留owner/epoch/kind/全厂及每owner预算，再由该模块自己的固定实现启动对应FS/RPC/transport/初始化动作；同一同步切点把实际underlying关联到预留项。没有消费者传入的任意IO/action callback。A只接该供方已认证的机制结算投影；B的实际槽不由A包装结果决定。所有真实操作入口均封装于同一供方，不允许另一路直接调用A绕预留。若启动/关联发生异常，保留原预留和已知真实操作为unknown，不能A.track失败后丢失它。
2. **另提A reservation修订**：若需要跨供方统一预留，可申请新增 `reserveOperation(owner, kind)` / `attachUnderlying(reservation, actualOperation)` 的受限内部合同；必须根精确授权新候选，6a38原字节不动。未attach的预留不因TTL/abort自动当作未启动/释放；取消与实际结算仍分离，不能靠任意调用者自报notStarted/count0。该方案不是本轮已批准API。

本地预留项不能用“立即可reject的deferred包装Promise”充当真实完成。可以另有operation/result promise，但真实underlying必须来自实际供方的固定操作及终态事件；native包装只表达等待状态。供方自身的未开始、已进入OS/已写帧、清理失败和真实settled均要有可核验来源。首阶段仍保 `mechanismOnly:true / productionAdmission:'unsupported'`，不签首内容IO能力。

## 4. 建议的精确供方接口与结果/释放分离

下面是待冻结私有接口，不是新增公共wire、已存在方法或本轮实施授权。对象只由可信main/供方工厂创建，并绑定实例、cohort、epoch；不接raw count、safe/ready布尔值、任意FS callback或伪造receipt。

| 供方 | 建议接口 | 最小事实要求 |
| --- | --- | --- |
| I06操作owner | `beginOwnedOperation(owner, epoch, finiteKind)`（模块内部） | 启动前预留；只允许该模块固定命名实现进入实际IO；返回真实operation身份而非生产lease |
| I06模型整组 | `prepareModelOwner(engineBinding, profileBinding)`、`quiesceModelOwner(owner)`、`waitModelOwnerReleased(owner, deadline)`、`abortPreparedModelOwner(owner)` | prepare资源局部持有；quiesce同步止新接纳、逻辑abort；等待分为result已结束/仍underlying/close失败；晚初始化只收尾原组，不写新全局 |
| I06source | `beginStoredRead(owner, binding, method, params)`；method严格限project.get/result.get/job.get/result.page | 返回分离的结果与实际RPC终态关联；source包装abort只影响结果等待；底层超时未知交T01处理，不自行证明Python工作已结束 |
| I06transport | `beginModelAttempt(owner, fixedRequest)`（内部） | 业务result与resourceClosed分别表达；原request/response/socket及相关迟到回调由实际供方聚合；只有真实终态才减network槽。cancel仅请求销毁 |
| I06credential/audit | 命名read/store/append的供方操作及 `drainOwnedOperations(owner)` | 在同步加密或仓库调用前登记；audit收尾属于原调用链；不导出secret、endpoint正文或OS错误。B无Keychain/真实模型验证，不假造已释放 |

不要只新增一个 `settled: Promise<void>` 字段而无其生产者闭合规则。每种settled均须列清所等的真实终态、异常和缺证据结果；拒绝/超时不自动等价释放。owner收到close错误后仍需保留资源身份/retired关联及未settled计数，不能清引用掩盖unknown。

同UUID主动重开/新Supervisor/迁移必须重建service→application→source/projector及其engine引用；依据为 `e2c269ad:apps/desktop/src/main/model-gateway/model-service.ts:72,152–171` 同UUID早返、engine只读。普通renderer刷新及同Supervisor短session恢复不触发上述全量重建或清grant；真实session ready/业务恢复由T01提供，B不消费A synthetic ready冒充实际就绪。

## 5. T01及native前置：B不能自己补造

| 固定引用/责任路径 | 当前缺口 | 请求T01/native准确交付 |
| --- | --- | --- |
| `e2c269ad:apps/desktop/src/main/engine.ts:472–488` | request超时删pending并reject，已写stdin仍可能在engine执行 | 私有受信请求attempt身份、派发切点及实际终态/未知状态；超时后仍可关联原响应或以该child真实close闭合，不能pending=0即完成 |
| `e2c269ad:apps/desktop/src/main/engine.ts:201–245` | finish先清session/pending并kill，child close更晚；stop只处理当前session | 永久 `stopAndDrain` 聚合该Supervisor所有实际旧/当前/正在spawn的child，不漏已经finish脱离this.session但未close的child；明确不可撤回写帧、停止新spawn、所有自有流/回调与真实close结果 |
| `e2c269ad:apps/desktop/src/main/task-service.ts:122–155,292–309` | dispose为void，unsubscribe可fire-and-forget；晚subscribe结果可再发unsubscribe | T01的受信项目epoch/普通view epoch分开；quiesce止新接纳并聚合subscription/recovery/late-unsubscribe；不据view缓存或dispose返回证明engine已排空 |
| `e2c269ad:apps/desktop/src/main/index.ts:77–129,223–231` | 全局资源初始化/关闭与多个固定引用没有candidate发布事务 | T01宿主局部prepare→真实位置/Store/Job/协议/项目scope→I06绑定或安全disabled→同步发布；旧close只清旧组。B不改已交index/task-service/engine |
| T01 Store/worker/coordinator | 本报告不读未批准新runtime，也没有其实际排空回执 | 唯一Store/worker所有连接、事务、writer lease及native资源的真实关闭/unknown证明；不是一条RPC终态或fulfilled包装Promise；Job/operation结论仍走原claim/context只读对账 |
| native/目标OS及未来C | Node目录复验、destroy/kill发出、main持有duplicate handle均不证明实际OS释放或首IO原子性 | 实际句柄/IO完成、原生锁/SQLite VFS与两个目标OS验证另批；B不能通过新通用callback/LocationLease工厂解除productionAdmission |

A的child/store-connection仅表示**整个cohort永久拥有关系寿命**，由未来T01供方在永久stopAndDrain时聚合全部实际child/连接终态。不能把每个可重启transport session的退出Promise直接接这两个kind；否则会把普通瞬断误升为全组quiesce。短session尝试仅按相应资源操作追踪，真正恢复由T01负责；原A注释和四个寿命反例不改。

兼容 `e2c269ad:apps/desktop/src/main/engine.ts:530–535` 的readEngineHealth会局部建Supervisor并finally stop，固定desktop未调用；将来若启用也须经过同一供方/stopAndDrain，不能绕整组registry。当前5f/e2c基础层均不证明新的B接口已交付。

## 6. 可独立准备的最小实施子阶段与验证申请

建议新B实现树从实际重新核验的批准5f创建，按明确清单采用固定6a38两产品/两专项原字节作为A机制输入，**不整commit采用64件流程材料或复制e2c实现**；是否允许该采用仍须root逐hash授权。A四项身份已由最终独立读回给出：

| 6a38fcb8路径 | SHA256 | B使用边界 |
| --- | --- | --- |
| apps/desktop/src/main/security/private-resource-inventory.ts | `0f6a2125d5dea53b5e5badde99401086284d4fd776b0cefadad324e408c786e5` | 纯接收metadata一致性机制，不能认证B真实观察 |
| apps/desktop/src/main/security/project-cohort-lifecycle.ts | `bcbb73449395757b0cb6260b1299366e1a25de5bcc16c161f145a1f7674fcdb9` | 纯owner/Promise机制，B须补pre-admission与实际终态 |
| tests/unit/i06-private-resource-inventory.test.ts | `7d82c1012bbe7fc35c5faf6eaf167b82d93a357e0b1060db6256ba809a118f49` | 原机制回归原样，B新反例另写，不删原限制 |
| tests/unit/i06-project-cohort-lifecycle.test.ts | `f90dd23b6f30e4e641197db6cb93a0fae4786948e489d4985b38f37ec0bf2fea` | 同上，不将原synthetic通过提升成真实供方通过 |

本报告建议生命周期供方新增候选仅 `apps/desktop/src/main/security/private-resource-operation-owner.ts`；若需要整组组合再单列 `apps/desktop/src/main/model-gateway/model-cohort-owner.ts`。这些只是准确路径申请，不授security或model-gateway目录写权。metadata-only观察、持久retired/失败记录格式和实际私有目录mutation由另一供方研究汇入主方案，不在这里另建第二权威。完整gateway旧路径的采用/修改依第1节逐项评估，不能由这两个新路径间接解锁。

验证路径均仅提案、未创建/未授权/未运行：

- `tests/unit/i06-real-operation-owner.test.ts`：命名实际临时目录操作启动前配额拒绝时IO计数0；操作已启动后attach异常保持unknown/实际槽；abort/5秒timeout不释放真实在途，旧epoch晚完成不影响新组。新B本地pre-admission不是A.track后补登记。
- `tests/unit/i06-model-cohort-underlying-drain.test.ts`：init失败逐资源清理、catalog/preview/serial与必要收尾audit全部计入；业务结果完成而底层未结束仍unsettled；同UUID主动新engine与普通同Supervisor瞬断对照；安全disabled不掩盖未释放旧引用。
- `tests/unit/i06-source-request-underlying-lifetime.test.ts`：包装abort、request超时、迟到响应/child-close分开；实际T01 adapter未交时只能做协议/机制反例，不假称Python工作已排空。
- `tests/unit/i06-transport-resource-lifetime.test.ts`：result先结算、request/response/socket后close及destroy后迟到事件；合成Emitter只证状态机。真实Node网络释放需要另行授权的隔离本地测试，不在当前无网络准备阶段执行，更不能用它代真实外部模型/Keychain。

B1可先证明实际受控临时目录FS操作的启动/终态追踪与有限pre-admission；无Keychain、用户内容、HTTP/模型、Electron/native。B2整组source/credential/audit/network组合必须等相应固定闭包/供方/接口精确批准；T01永久child/Store排空、真实session/两层ready及native释放缺失时，继续明确unsettled/unsupported，不用自报count0或fixture ready补齐。所有后续实际验证由owner在获批新树运行，捕获argv/cwd/分离stdout/stderr/exit/输入SHA，保首失败和新候选原件；本文件没有任何运行通过结论。
