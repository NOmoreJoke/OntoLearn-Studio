# Dispatch 与永久 child 排空方案：独立审查

当前结论：首轮 read-ready 方案有一项 P2 写前撤销联动缺口，以及两项应在实施前具体化的 P3 生命周期/供方建议；待作者修订后定点复核。本报告不预先写通过，也不把方案当产品、生产 scope、物理绑定或 OS 释放已完成。

本审仅写本文件。没有修改产品/测试、作者主稿/清单、C1/C2文件或根控制资料；没有 import/执行产品、数据库、测试、Node实验子进程、网络、模型、GUI/native，没有 stage、commit、切分支或新建产品树。仅做原文件/Git/hash/JSON静态读取与本报告格式检查。

## 1. 实际读取与固定身份

工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-create-core`，实际过程 HEAD `a33cc80e82475e54d74b4e48c1fd32f32979983a`，产品源 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`。本审实际全文读 AGENTS、common 和根5480B方案准备授权（工具 b9ca48，输出完整；637f18 再核 bytes/SHA）：

| 输入                                                 | bytes | SHA256                                                           |
| ---------------------------------------------------- | ----: | ---------------------------------------------------------------- |
| AGENTS.md                                            | 15852 | 78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759 |
| developer-common-instructions.md                     | 17891 | e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0 |
| T01-dispatch-and-permanent-drain-plan-preparation.md |  5480 | c74eb72aa29fb6dce5e77cd48c22df69c2845e99b1c9be41074844fb1f016caa |
| 首轮主方案                                           | 35460 | 7b1fc29a0314787a5c13e14da903b2c2c8f12394a4e88db73f2989cb4b15151c |
| fixed-foundation-inputs.json                         | 15031 | acd98954a826450dc016169a49508ed6bb1d2b758ba2683b6a5c4ecb1b77e940 |
| investigation-inputs.json                            |  6679 | a30a128fdb04ed8a1f764023aac541a8427e277a8fdd6d5e4b14afc9a265d7d4 |
| source-investigation.md                              |  4864 | e72a66f2bff50c63aa4123b7a64c5a4eca79a1c7961f2638f97c3de5ba4e9e9a |
| checks.json                                          |  1236 | 224e2f1097346963f3a3212838614a2b8f6082caf01b112eda22a08081b59587 |
| review-input-r1.json                                 |  1371 | 714e7f7178f19fe1d85d90859ac655571075c42e3104387507c8db191925c1a7 |

主方案全文读取637f18；五份配套材料全文/JSON读取80d960、3f4f1c、054212。3f4f1c逐52项实际核423b Git blob=current bytes/SHA，51 readonly、engine唯一继承未来writer；不是只信作者checks的布尔值。2b6824核新树及两新产品/test确实尚不存在。

本审实际全文读固定engine.ts（80d960、ba7025、3f4f1c尾部）；其26260B / SHA256 `6d55774068ca27a49958daeea9f4b1fa15614c95563ca28b8a768265ecd4365e`与423b Git核同。另读jsonl.ts全文4924B / `8426b2cc134cb2fed08667c87f0eb8a84a3544a13677197a1acddc7de00776c7`、Coordinator request/dispatch/tick与serve finally/stop切点，coordinator.py41168B / `6e057cbdd76c674813d9f90e231306cb9cf5611ef7fcbeb234de13d698afa18c`。registry15962B / `1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b`的v2Runtime与business3方法列表由bedc47/8c6715实际读取。

离线官方Node声明中killed/kill/PID复用风险、stream.closed/destroyed/writableEnded注释已读32e3a3；I06固定B方案§4.1/§6/§8作为供方计划而非已批准API，32e3a3大输出中§6被包装截断后，054212单独完整补读。未浏览网络，也没有把类型注释当本机真实子进程执行证据。

## 2. 与真实源相符的设计部分

- 现 `#finish` 会先terminal、stop reader、reject pending并移除当前session，再kill；旧child在实际close前可能仍活。`#starts`每分钟5次不能替代永久owned集合上界。方案用先占槽、current/starting一个加retiring一个的申请cap2，并在真实资源未终态时拒绝再spawn，方向与缺口相符。
- `#send`当前没有scope/current cohort来源，仅严格frame/pending与当前session；在真实stdin.write前增加同步门是正确切点。方案保预编码帧与原request，不让检查对象和发送对象不一致；write抛错/false/callback失败仍write-attempted，不假认未发送。
- Coordinator request同步dispatch后才emit，serve随后tick才调度后台。方案区分普通同步foreground回复与job.create queued受理，不把所有正常read回复永久占128槽；job.cancel回复不能结原后台Job。实际同版method表与上述来源相符。
- 同Supervisor短断线不结束永久transport ownership，新Supervisor即使UUID相同也需整组ModelService/Application/Source/Projector/Core及context重建；方案没有把同UUID、Promise、session/stop返回或child.close当完整cohort/Store/native释放。
- stream终态分别记录，end/finish/destroyed不当close；已exit/close不重复kill，unknown不按TTL腾槽。现readEngineHealth只stop的兼容边界未被伪称已永久排空。
- 原payload帧8MiB、数量128、owned2、listener64、observer8和有限timer均明确为新增申请政策，不把现速率/pending限说成已有永久guard。生产rawrequest旁路必须另阶段全部封闭，scope/native缺失时不发布正式生产能力；hello前已有Store首IO也已如实列为前置。

这些是方案静态可实施性观察，不是已实现/已运行通过。

## 3. 首轮意见

### [P2-DP-01] scope-only revoke不一定反映在三项本地重核

位置：主方案§5步骤3–4、§4.1同步source合同。首轮方案说source核验中若发生stop/revoke/代际变化，返回后只重核stopped/current/owned entry；但I06私有scope/lease撤销未必改变这三项Supervisor量。

静态具体反例：真实source先检查当前scope有效，在同一次同步动作中通过某个通知/回调撤销其registry scope（没有stop Supervisor、不换child/session/generation），随后正常返回。T01只检查原三量均仍真，即执行stdin.write。该反例不依赖await，也不需要renderer伪造权；因此“没有await”本身没有证明撤销可见。

最小处置：供方最后核验/consume到返回之间禁止任何外调/再入；同时给出真实issuer撤销到T01同步fence的精确联动，或T01可直接读并核同的source epoch。revoke必须先使该来源在T01不可再派发，再改变权限材料；返回后检查该fence/epoch，而不只是三项session状态。该fence只防接线竞态，不认证OS/native撤权。增加“只撤scope、不stop、不换session”的write0反例，并保校验失败后permit已消费的有限处理，不另frame重用。

本意见已先发主线及作者；没有运行产品或修改其主稿。

### [P3-DP-02] 异步operation结算供方还需最小具体签名

位置：§4的operationExecution、§9 T01/I05横向申请。三个同步source动作已具体，但后台operation完成只写为待真实owner核验的异步来源；尚未冻结如何登记原ticket、接收哪个实际issuer观测、怎样区分terminal Job事实与worker/Store寿命，以及订阅留存和清理上界。

建议在方案内给出最小bind/observe或attachActualCompletion合同，绑定实际Supervisor/ticket、原dispatch/JobId、可信producer incarnation及完整原受理/terminal材料。不能接受任意Promise/DTO形状或caller completed布尔；订阅数量包含在有限ticket/observer政策，缺供方保持pending/unknown。若当前wire没有生产者，明确标请求而非实现，并保持正式消费后置。这样未来三writer内部机制可拒缺来源，又不需要随意解释一个通用callback。

### [P3-DP-03] 清退避timer须同时结其deferred

位置：§6永久stop与§7 #starting。实际engine `#start`在退避时await一个setTimeout Promise，`#ensure`依其finally清#starting。若仅clearTimeout，Promise不会自己settle，#starting及未spawn预留可能永久留存，虽然实际没有child。

建议明确stop的退避取消同时resolve/reject该自有deferred，使continuation或finally按真实never-created路径结算，spawn前仍复核stopped/epoch；timer清除不是settlement证明。增加stop发生退避期、spawn次数0、#starting最终settle且transport drain不因无child悬挂的专项。若已经进入spawn，必须转owned child真实close路径，不从该取消分支删除。

## 4. 复核与剩余门

待作者给出修订主方案bytes/SHA后，本审只对实际变动、相关来源合同及验收条目复核，保留以上首轮身份与意见，不重跑无变化产品。主线与作者各自文件责任不变，C2审查不受本报告影响。

最终方案即使通过，也只申请精确三writer/52采用/51readonly的新独立5f树；不能自动成为实施授权。真实scope/原物理绑定、首IO/native、Store/worker终态、完整生产旁路封闭及全57P0、双OS/真人、指定GLM-5.3最高和M3.1-Flash/xhigh双方同版新审、CI/正常develop合并仍保留。

## 5. r2 定点复核与本次最终结论

本节取代首轮开头“当前结论”的待修状态；前9173B首审原文保持不变，并已有作者另存的同字节快照。**对下列固定r2方案，P2-DP-01与两项P3意见均已在方案层具体关闭，无本审未解决实质问题，本次独立静态方案审查通过。** 这是实施申请的设计结论，不是产品、真实producer、scope/native或运行验收通过。

### 5.1 实际修订输入和核验

工具17e939独立核下表当前bytes/SHA，并全文读处置、r2检查和r2输入；550789读取实际变更时大输出被包装截断，随后6f5ff7单独全文读新增§12、009e24独立读主稿§1–11的完整实际diff，没有用截断片段代替全文。r1全文已在637f18实读且其余未改，新增及实际修改段据此完整覆盖。

| r2对象                                      | bytes | SHA256                                                           |
| ------------------------------------------- | ----: | ---------------------------------------------------------------- |
| 主方案 dispatch-and-permanent-drain-plan.md | 46175 | fc341d0c24ffb91ac170a0f393616e22551a8e22a53b35ac373346012e97b368 |
| disposition-r2.md                           |  3716 | 2e6520dbf8ac28eeaa4e71750865f8fce0d84ac9ec68bcae6236d2adfe41c920 |
| checks-r2.json                              |  2675 | 4869cd66ae0f757115131aecb15491d0e2bcfcbd1d4f0f326dda1e480a7d0840 |
| review-input-r2.json                        |  2596 | cd6601717ac4e1863bb953bd3ecd1ba71f41755c4a5ec9aecf5d1555c449afd1 |
| plan-r1-before-revision.md                  | 35460 | 7b1fc29a0314787a5c13e14da903b2c2c8f12394a4e88db73f2989cb4b15151c |
| independent-review-r1-before-r2.md          |  9173 | a6bce6c54fb66b812b2971a539775de18c216cd72843eebcdfbfe7becec12a26 |

主方案相对docs/iterations/T01，其余相对本reviews目录。73b1dc actual exit0独立按r2输入逐10项重新读bytes/SHA，与清单一致；r1检查/输入及前述历史快照均未倒改。同行工具再核52拟采用项每一项Git423b=current/bytes/SHA、C1原59项Git/current、root-closure原字节、C2固定0a03539的9项过程文档Git/current均相同；不是采用作者checks里的布尔值。HEAD为`0a03539a44c43fafb2f890953bbb59a77ea33a05`；拟新树与两新产品/test仍不存在，AGENTS保护字节仍相同。本审没有stage/commit或修改这些输入。

### 5.2 逐项处置

| 意见                         | r2具体处置与静态关闭理由                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P2-DP-01 scope-only revoke   | §5.4及§12.1要求真实issuer在撤scope/lease/cohort登记前同步推进T01私有epoch/封闭来源；sink只有否定能力，不能授scope或caller设epoch。T01捕获E，供方最后check/consume/return禁任何外调、getter、Promise或再入，返回后直接读本地source附着/epoch=E/未封闭再紧邻write。原三量不替source fence；consume后本地拒绝不重发旧permit，epoch耗尽永久拒。§10.1含不stop/不换session仅scope撤销write0反例。该合同已消除首稿局部重核漏撤销的设计缺口；真实issuer全撤销路径与native兑现仍须独立实证，未由本审证明。 |
| P3-DP-02 completion producer | §12.2冻结bindOperation、bindAcceptedJob、observe、projectTerminal、closeObservation签名及真实issuer incarnation、原Supervisor/child/privateTicket/dispatch/request/Job完整材料关联。每ticket一个watch/全128、仅一个总通知listener；terminal事实不结worker/Store/native寿命。清理失败保watch槽，终态待清理identity4096B/件、总524288B，不在闭包暗留原frame。原implementation未知不能用新Session补。现无真实producer明确为后续供方，不收任意Promise/形状或caller bool作为完成。                     |
| P3-DP-03 退避deferred        | §6/7及§12.4明确clear自有timer同时同步reject delay deferred，让await拒绝并执行该attempt的finally；finally完成后才可结never-created。spawnEntered=false且无child才可走取消释放，已进spawn仍等真实child/pipe，不能“没返回对象”自证无资源。§10.3列退避期stop、starting真正settle、spawn0和已spawn相邻反例。                                                                                                                                                                                           |

### 5.3 主线补充的满槽观察闭环

主线另指出：若128个后台ticket占满业务槽，completion producer只用同Supervisor普通job.get轮询，将无法得到释放ticket的观察。本审将此作为P3-DP-04纳入复核，而非冒称是本审首轮独立发现。

r2 §12.3提出明确补救：受理前先预留真实观察，现Coordinator128订阅总额须与TaskService等真实owner共用；另申请最多1个completion foreground RPC、独立262144B帧池/一个scheduler timer，仅注册producer为现ticket使用job.get/subscribe/unsubscribe。仍走真实profile/frame、current scope与同步fence，不开放任意method、job.create/cancel或renderer优先级，不伪装health/ping。普通128+heartbeat1+completion1最多130是新的待批准政策，不是当前已实现行为。

poll超时不释放其实际在途槽，unknown时暂停再poll；严格迟到response或真实owner终态才结算，不能每超时一轮再开并行查询。满额闭环已进入§10.8待验矩阵。现wire没有完整producer、原JobId未知的受理发现和完整原物理对应仍需真实供方，三writer也不授权Coordinator/canonical/TaskService产品变更。因此本设计只在真实producer兑现后可成为生产可闭合通路；缺供方时unknown/拒新是当前有限失败，不得写成完整生产已经可用，也不把最终目标缩成永久unknown。

这项方案边界与根授权一致，本审未发现需在当前三writer申请外先偷偷修改共享文件的理由；实施如发现必须扩路径，仍须具体反例/最小diff另批。

### 5.4 最终边界

首轮一项P2、两项P3及主线补充的观察自锁风险均已有明确设计处置和未来反例，r2当前主稿身份固定，无本审待修事项。保留原52只读采用申请、engine唯一继承writer与两个新增路径、完整54产品/test范围；未新建树或产品。

本审只对设计作静态通过结论，没有执行未来write0/真实child close/128满额/退避取消fixture，没有产品、DB、测试、网络、模型、GUI/native运行。本报告不授实施窗口，也不认证真实scope/dispatch physical binding、Store/worker/native释放、生产原request旁路封闭、双OS/真人、57P0、指定同版双外审、CI/PR/develop集成或整个Goal完成。
