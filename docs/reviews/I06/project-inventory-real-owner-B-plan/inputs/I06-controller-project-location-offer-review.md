# I06 项目位置与 cohort offer：总控独立静态复核

2026-10-21。结论：固定 docs 提案 `1f3b053d8a69d1f7ddb1e29c143f648d910fe689` 已关闭首审的两项 P2 与多链接建议。本次未发现阻断先行 **A：纯 inventory 与生命周期机制** 的新增实质矛盾；可供 root 另行批准四条新私有代码/测试路径。A 必须从批准5f自包含，不复制e2c/961产品，不接真实owner、持久退役恢复、native/VFS或生产首内容IO；这些缺失时生产准入仍保持 incomplete/unsupported。整份offer、B/C/D/E、目标OS和完整父功能未由本报告放行。

本审只运行Git、文件读取及stdlib JSON/hash/集合断言；未import或执行产品、测试、build/native/GUI、凭据或模型，没有对外发消息。唯一写入为本报告；未改产品、owner证据、共享state或Goal。平台条款作为**尚待实现和验证的合同**审查，本审没有重做其官方链接检索或目标OS实验，不把owner平台补核升级成本审实际OS证明。

## 1. 固定输入与真实范围

实际树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-model-gateway`，branch `feature/I06-model-gateway`，当前HEAD为上述固定ref，当前状态仅 ` M AGENTS.md`。docs起点 `660da44aa7ad1b3ba7dbfb3a90fef37e25763ec8`，自有历史产品e2c、guard961均是只读事实来源；批准产品基线仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。

已全文读取最新AGENTS 15852B/78df2825…759、common 17891B/e437121a…1b0（批量输出被截部分已单独补读）、根3994B/b62750…5b准备指令、7435B/0c9611…57读取服务授权，以及固定T01计划29575B/f7ee5b…4d全件。后者从I06封存原件读取并由固定427ba Git逐字绑定，没有据此采用5de或新host实现。

主offer `docs/iterations/I06/project-location-capability-and-cohort-offer.md` **46365B/SHA256 `561ec272c07f0c0f026c9aa17b717b99d3e110e31cb4ee45f0663254e9517443`** 已按1–100、101–190行完整分段读取。owner独立首审、followup、source-static、platform-static和disposition均全文读回。

独立逐项核验：

- inputs.json的31项，固定Git项以其ref:path取真实blob、本地政策项读实际文件；bytes/SHA全部相符。
- manifest的13记录全部当前=固定Git且bytes/SHA相符；加manifest自身恰为docs起点→固定head的14条实际diff，全在唯一offer和获准review目录。
- 31项输入包括封存T01计划、guard设计和准备指令，hash均与原件一致；主offer与两历史快照身份也相符。
- 本交付**没有ZIP**；原件以这14份docs/JSON封存，不能声称本审验证了不存在的ZIP。manifest本身不以自列hash认证自己，固定Git与实际delta对它作外部绑定。
- checks.json真实记录仅docs格式/Git/输入hash；初次格式check失败保留。没有产品、native或OS终态可供本轮提升为通过。

本审另只读核e2c的private-directory关键open/list/read/publish/PrivateOperations、model-service构造/select/close、stored-result-source底层RPC/abort/finally、main initialize/close、TaskService订阅/dispose、Supervisor finish/stop和局部health工厂、GatewayApplication active/close关键原文，与offer事实表和source-static修正相符；未读运行凭据/目录正文。

## 2. 首审修正已真正写入最终合同

| 原问题 | 最终合同及判断 |
| --- | --- |
| retired一概拒绝会永久阻止同库重开 | §2.1区分private-deny/profile-container/database-managed；DB `released-retained`保留记录，只凭旧组真实release、新可信用途和重新核原生锁/身份再取得精确DB组能力。private项无例外、unsettled不许重新取得，不凭同UUID恢复grant。原矛盾关闭。 |
| final占位与no-replace发布冲突 | §3用途表及§3.2统一为authority内名预留、OS独占staging、关闭/checkpoint/sync后一次native no-replace。外部抢占会失败保staging，不删占位或replace原文件；发布后sync失败记已发布/耐久unknown。原矛盾关闭。 |
| nlink闭合不足 | §2.1要求同观察边界内distinct目录项数=linkCount且全部受保护；nlink3只见final+pending两名是unknown，外部DB nlink>1有限拒绝，不假称扫描全盘。建议关闭。 |

其他源码纠正亦已落实：4096/10000是新增写/追加门而非恢复扫描上限；health临时Supervisor列为当前未接入；late initialize风险明确为未来重复初始化缺口，未捏造当前并发；credential factory成功与实际加密backend可用分开。followup1093B/07eafe9…bef确实绑定最终46365B/561ec272…443，不能把初审“不通过”倒写成初审已通过。

## 3. 首内容IO与真实文件能力的设计边界

§2–3与T01 H2明确一致：模型状态、picker结果、绝对路径、UUID/hash、metadata-eligible、T03来源broker均不授数据库内容访问。完整inventory/真实purpose/持有身份门必须在SQLite/header/catalog/Store/backup首次内容IO前成立。open-existing不创建、不mkdir、不迁移；create独占staging且不覆盖；migrate须精确备份和人类确认。三个目的分离，T01仍是Store/DB内容唯一owner，I06是metadata/lifecycle与拟原生broker供方。

主库/WAL/SHM/journal/writer-lock及备份是精确角色，不给目录任意写权。prospective项绑定受持父对象+单basename，首次创建登记实际身份再IO；alias/未知成员/超额不截断后complete。使用已持verified handle而非check后path reopen；跨await/连接/发布均须实际native fence。旧对象被持有不等于新目录项同一，撤销后旧namespace不再open/publish。SQLite备份不能裸拷main漏WAL，热恢复不能冒充只读open。语义闭合方向正确，当前均待原生实现。

原生路线明确为同build SQLite capability VFS，要求注册到Python sqlite3**实际同库实例**；不准默认VFS/URI/ATTACH/extension/temp逃逸或借第二SQLite/APSW证明原Store。若符号/静态链接不能共用则unsupported并向build唯一owner申请精确方案。版本字符串不等ABI；源/包实际_os调用/VFS/锁/SHM轨迹待证。此路线可保留为C阶段技术提案，但仅文档不足以判断它已可编译、部署或正确兼容SQLite。

macOS15 arm64的逐组件dirfd/NOFOLLOW、APFS no-replace与发布后耐久；Windows11 x64的逐组件RootDirectory HANDLE/reparse、完整128bit FileId+卷、角色share/delete策略及原HANDLE发布，均写为平台要求和待验限制。已发布后同步失败、Windows取消请求不等settled、main duplicate不能代child IO完成均未被忽略。**本审没有确认这些原语组合在实际目标构建中成立**；C须做真实OS/ABI小阶段，不能因本静态合同没有新矛盾就签发IO能力。Linux或Node mock不能代两目标OS。

## 4. inventory、cohort与责任边界

inventory先reserve再mkdir/publish；owner缺席、初始化/观察/close失败、超限、别名不明、跨revision拼接均不得complete+[]。模型不可用与metadata不完整分开；只有真实metadata complete且旧引用全部fence的disabled-model binding才可让将来本地确定性路径发布。完整userData容器的精确DB例外仍须root另冻结，不能在A靠后缀/字符串构造。

active/retired记录不因0句柄删保护。private残留永久保护，DB release保留历史且新open重新取权；跨重启缺持久退役记录不能当空。原进程退出与OS锁/句柄实证是未来受控恢复前置，不凭PID缺席推release。未settled picker/FS/init/network/child继续计槽，逻辑abort/UI超时/Promise包装reject均不腾真实槽。late成功只能收尾原epoch，不能恢复grant/装新cohort。

固定直接持engine者已列main全局、TaskService订阅、ModelGatewayService、StoredResultSource及当前未启用health临时工厂；Application/Projector/Core/Repository/transport作为间接资源链另外排空，不冒充直接engine owner。实际e2c source包装Promise可先拒而底层RPC未settled、Supervisor.stop清pending后child.close更晚，已由所读源码证实。关闭整组并以新Supervisor重建同UUID引用是合理必要设计；普通renderer刷新/同Supervisor瞬断不被无故扩大成所有重连清grant。

候选私建→旧组实际排空→新lease绑定实际child→该child唯一Store/Job/reconcile/hello两层ready→真实库选项目/scope→I06全部新引用或安全disabled binding→同步发布，顺序没有靠fixture/renderer UUID补授权。operation unknown依T01现claim/context只读对账，不建第二main账本、不换op重放。T03来源broker与build四文件责任没有被该offer挪用。

## 5. A可以独立实施的精确条件

建议root仅授权以下四个**新**路径；不是授权security目录、B旧模块或C native路径：

1. `apps/desktop/src/main/security/private-resource-inventory.ts`
2. `apps/desktop/src/main/security/project-cohort-lifecycle.ts`
3. `tests/unit/i06-private-resource-inventory.test.ts`
4. `tests/unit/i06-project-cohort-lifecycle.test.ts`

从实际批准5f独立worktree/feature开始，自包含TS纯机制即可；允许stdlib/原5f既有依赖，不复制e2c/961产品、私有仓库、环境或新native依赖。两个新模块之间的受限内部类型可共享于这两文件，无必要为A修改index/engine/task-service/Store/公共canonical/preload/App/build/锁/CI/旧测试。当前这些A代码尚不存在，实施正确性仍需独立审查。

A的输出只证明“经该核心接受的metadata/owner状态机一致”，**不是实际完整FS观察、生产HostIntent、可执行LocationLease或发布许可**。API应以当前实例registry和opaque对象身份约束owner/token/epoch，拒clone、他实例、旧profile、旧revision/ABA和旧已released票据；不导出通用FS callback、raw fd/path opener或生产首IO动作。合法数值/对象字段本身不认证真实OS/owner供方。没有B真实供方、持久退役恢复或T01实际release证据，真实bootstrap应停incomplete/unsupported；A单测可提供受控metadata证明机制，不能把合成complete当生产complete。

实施至少保留以下出口：

- 固定预期owner集合，未注册/未观察/failed init不因列表为空而complete；初始未知、确证fresh/确证不存在和损坏恢复须可区分，不能把ENOENT通配成empty。
- 同步reserve/mutation先失效旧issued状态；一个完整revision只由对应全部owner同epoch观察形成，bounds/条目/links等超额整体失败。复制输入并限定精确native字段；调用者后改数组/对象不能改变已发快照。
- private-deny/profile-container与database-managed分别处理；released-retained保记录，未settled release不得凭0计数/超时/abort伪签，reopen需新实例/epoch和当前原身份事实。
- picker/acquire/init/network/worker/child分类的逻辑取消和实际settle分开；重建不重置实际槽；重复settle、错owner receipt、晚init/旧close清新全局均有拒绝/隔离测试。A只是记录这些可信供方回执，不能自己制造真实child已退出事实。
- 同UUID主动重开走新transition，普通view refresh/同Supervisor瞬断有对照；candidate未满足各必要binding/ready前不能逻辑publish，失败不部分安装，晚回只归旧对象。生产主指针发布和所有真实持有者改造仍在D/B。
- 工程有限界/TTL/release先固定单位与安全失败、真实测试边界；只证状态和有限留存，不将unit或5秒写成CPU/RSS/OS取消能力。任何持久退役格式/新增数据写权限另批。

正常check/source及新专项由原owner在实施阶段实际执行，原raw失败保留；复杂实现独立审查。A通过也不关闭B真实metadata/资源追踪、C原生/VFS与两OS、D宿主/Store、E公开消费/真人、指定同版双模型/CI/正常develop合并与父I06/FR-002。

本次未发现必须先改主offer才能批准上述受限A的阻断；以上是将其现有边界落成准确施工范围，非追加产品范围或降低原门。下一步由root逐路径/基线正式授权，不能由本审报告自动开工或对生产首IO放行。
