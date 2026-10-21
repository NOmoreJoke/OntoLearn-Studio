# 项目宿主一致读取服务独立审查

**最终意见：固定a142d9实现/f27a53新测试/a27a4d实现文档无未解实质阻断，两项P2均已独立复现并在修后定点关闭；本候选完整check04及sources原件已读回，支持该私有一致读取服务阶段交总控冻结与指定双审。** 结论只覆盖现有可信Store3连接上的内部目录/工作区读取，不授文件位置能力/公开宿主接线、创建/resolution实现或父FR完成。以下保留授权、WIP/首read-ready和被替代运行历史，不把旧阶段通过贴到本候选。

## 正式授权与独立只读边界

新树`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-host-read-services`，分支`feature/weekly-t01-project-host-read-services`，实际HEAD/批准base均`5f910b52c69d86a1076b2032e5d3c63e715947f3`。原T01 Goal继续，不重建；原5de/427树冻结，历史task-runtime维护仍I05。

已实际全文读取并核原字节：

| 输入                                                               | bytes | SHA256                                                             |
| ------------------------------------------------------------------ | ----: | ------------------------------------------------------------------ |
| 根`T01-project-host-read-services-implementation-authorization.md` |  7435 | `0c96119b2038b1db0d74fc8466926f321c7ebee669cb8949876e417c9e580757` |
| 根`T01-project-host-services-fixed-foundation-inputs.json`         | 12166 | `d0c242de45aec840258b7b6f7f4ba4eb6fbdc35b8969a0cf69630d5b0123e1c6` |
| 新树AGENTS.md                                                      | 15852 | `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` |
| 根developer-common-instructions.md                                 | 17891 | `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` |

授权全文`e33830`、共同指南全文`cc2ff2`、独立AGENTS及48manifest全文`063b87`；`e5cee9`exit0独立逐48项取固定5de Git blob，核现场原字节、bytes/SHA全部一致，并核新树branch/HEAD。合并输出曾被工具截断时，不将缺失AGENTS段称已读，已用063b87单独完整读回。

本阶段主线唯一产品作者只新增`packages/engine/src/ontolearn_engine/project/project_host.py`与新测试`packages/engine/tests/test_project_host_read_services.py`。合同由另docs作者写；本agent唯一可写本报告，不改产品/旧测试/48输入/依赖/规则/其他报告或总控状态，不提交推送。模块只能消费可信host已持有的真实Store3连接，无路径/新连接/创建迁移/许可/RPC；创建/resolution只提交精确合同，不写DDL/实现。无GUI/Electron/e2e/native/HMR/凭证/外审应用。

## 实现前静态机制核读与具体建议

以下是既有48组合源码的分析，不是尚未交付新模块的缺陷或通过结论。已将同一具体建议直接发主线，避免作者在可复用接口上重复探索。

| 机制           | 实际源码与最小使用方式 / 反例                                                                                                                                                                                                                                                                                                                                                                                                                         |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 一致只读事务   | `Store._read`在无外层事务时BEGIN→finally ROLLBACK，可覆盖整次目录/工作区验证与捕获；不要用BEGIN IMMEDIATE的`_transaction`充当只读事务。若调用者已有未提交写事务，_read会直接join，读到的不是持久头；纯服务宜拒绝active transaction或明确可信只读外层合同，不能擅自rollback调用者事务。                                                                                                                                                                |
| 禁写接口       | `snapshot/_snapshot`会INSERT OR IGNORE；`JobStore.project_get`调用snapshot，`public_project`会补映射；`format3.checkpoint/seed_project`也写。不能因行通常已存在就称纯读，也不能新造placeholder弥补证据。                                                                                                                                                                                                                                              |
| 完整既有权威   | `format3.load_checkpoint`经_history核完整mixed ledger、receipts、起点、连续sequence/domain revision、当前头、实际application/state/vector，不只是payload hash。`_raw_checkpoint`仅结构读，不能单独授权；`format3.validate`还核schema/catalog/完整项目集合/integrity/foreign keys。可在同一_read中一次完整validate，再读取已被同txn验证的既有head；避免每目录行再次load_checkpoint重复全链。选哪种调用要写实，不能称验证旧值后另开事务读取现头仍一致。 |
| 验证本身的预算 | history/validate会物化snapshots、域state、所有draft/learning/audit，而返回DTO不含这些数组并不能证明内部工作有限。应在调用它们前用SQL count、typeof和UTF8存储bytes聚合检查项目/历史/域记录/文本总量，再受控完整验证；超限整体拒绝，不能仅最后序列化页时拒绝或默截断。工程界是私有技术限额，非Q5/CPU抢占/真实RSS承诺。                                                                                                                                  |
| 目录完整集合   | inner JOIN会静默隐藏缺mapping/app项目，故先核projects/public_projects/app_projects双向完整一一对应、真实public UUID及当前checkpoint metadata，再冻结稳定有序完整快照分页。不得调用public_project补写，不凭名称或路径推UUID，archived/同名如实保留。                                                                                                                                                                                                   |
| 工作区证据     | 同一读事务核public→internal、revision、既有正确domainSnapshot、metadata/version、sequence/checkpoint与指定editor。不能生成新snapshot；缺证据固定安全失败。完整history内部需要验证全部当前application，但输出只投影白名单metadata与指定draft，不外泄全部域/learning/audit。                                                                                                                                                                            |
| draft三种状态  | 未创建无持久header/generation，不伪造为0代墓碑；墓碑present0保留generation/bound_revision；JSON null是present1、payload='null'与真实hash。boundDomainRevision不是CAS，旧bound但合法稿应保留。严格UTF8、exact类型和内容hash，不能用truthiness把null/空JSON当删除。                                                                                                                                                                                     |
| 私有分页缓存   | 一次冻结完整目录，后页不持长SQLite事务、不混入随后metadata/新项目变化；缓存保存私有不可变值/编码值，返回拷贝不可反向改缓存。cursor只定位，绑定reader实例/snapshot/固定page size/position和deadline；明确single-use或精确同页重试语义，不能续TTL。页编码先计费再推进，初次/后页失败、末页释放、过期、取消、满额都有有限清理，不先释放再留下后台工作。                                                                                                  |
| 零写证明       | 完整DB逻辑dump前后等+SQLite authorizer真实拒INSERT/UPDATE/DELETE/DDL同时合法读取成功；只total_changes==0不足以证明没尝试INSERT OR IGNORE。测试允许读事务BEGIN/ROLLBACK，但不要为了通过authorizer临时切换到另一连接或关闭约束。                                                                                                                                                                                                                        |
| 安全错误       | 数据/JSON/hash/SQLite异常只投影有限安全reason，不返回原异常、路径、内容。内部缺证据与超预算应区分；只读拒绝不能被解释成不存在项目/无claim或授予新的scope。                                                                                                                                                                                                                                                                                            |

机制阅读工具：`d29915`、`cde661`、`e5cee9`均完整exec返回exit0，实际读取了现format3 application/history/checkpoint/validate、Store snapshot/state/vector/_read、应用claim_context/validate及DraftHead。仅源码读取与hash，没有执行产品、探针或旧/新测试。

## 待作者read-ready的独立审查切点

- 两新增代码/测试固定SHA、完整函数及精确私有DTO/预算/游标寿命；检查是否只消费同连接，零写、无新能力。
- 新服务合同与真实实现一致：catalog完整性/metadata/draft/no-header/tombstone/null，快照物化、失败/资源/取消与末页释放真实行为，不把计划阈值当测量通过。
- 真实SQLite/authorizer/整库dump、多项目一致分页、metadata/draft合法更新后的旧快照、受损/缺历史/缺mapping和跨reader/过期游标等；只按必要小型独立反例验证，不复制作者矩阵。
- 并行create/resolution合同单独标方案；必须基于实际claims/context充分投影，queued无marker、未知jobId、当前许可、跨Session仅对账不重放，不新增main账本，也不从无证据null断言未受理。
- 作者完成后本候选完整check/source核验及原始首失败/实际终态；不以新树继承48输入或旧5de跑过的测试自动认本候选验证。

当前未审尚未read-ready的新源码，不预判通过。既有48只读保护、指定双审/CI/正常合并/远端、四入口/T09内容/位置能力/IPC/native/人类确认与父44/57P0保持原门；纯读取服务和本报告不改变完成度。

## 实现初读与实际头 P2（已定点关闭，最终冻结待交付）

主线交付初版新模块14242B/SHA `58a77b2caa7cfd2287fa5b3ed4d278693d5146842080331c307d0691070395a3`供进行中只读审查；新测试当时仍在作者编写，非冻结候选。独立`6f0aea`exit0完整读取模块并绑该次源hash，未修改产品/测试。

### P2：配置target不证明实际数据库仍为3

初版constructor仅核`JobStore._target_format==3`，而`_read/_validate`未核真实`PRAGMA user_version`。既有format3.validate为安装迁移提交前可复用，亦有意不以header==3作为内部条件；直接复用不能隐含这个入口约束。

独立`2dc34e`exit0在自有临时真实JobStore3建项目/reader后，离线header损坏fixture改`PRAGMA user_version=4`。catalog_start和workspace仍接受回数据，actual4/target3，完整dump不变；运行前后源SHA相同58a77b…。这是读取入口未拒未来/回拨格式的实质反例，不是普通API能把库升级4或当前模块偷偷写库的指控。原完整exec保留。

主线修订在fresh BEGIN之后、preflight/内容验证之前读真实user_version，非3则安全state拒绝。已建reader和新建reader的0/2/4由主线加测试。当前修后观察14377B/SHA `007e597059d20688ebd880172b245733f6aa3e4ca8e13c82bfba7ccb0e6bcc90`，仅是本次定点身份，不能提前套到尚未交付的最终源码。

独立修后`efa3f2`exit0：实际临时JobStore3的2项目两页目录及指定editor缺失workspace，在authorizer禁止DML/DDL/附库动作下成功，写尝试列表空、完整dump不变、事务释放；随后同一reader将离线header fixture改4，catalog/workspace均state拒绝、dump不变。前后源码SHA同007e…；该P2在当前修订上独立关闭。没有重复作者36项矩阵或全仓测试。

已缓存目录后页不触数据库，仅是原快照内存分页、不新增许可；真实Store/location生命周期失效须由可信owner close reader。此处是私有模块host合同，不声称当前I06生命周期已实现。后续最终文档须保留这一边界。

### 其余已核的实现机制与审查建议

- SQL预检当前确实覆盖所有表的行数/字段存储bytes与保守work，发生在format3.validate完整history之前；schema/table数和column数也有固定上限。未因DTO不输出大数组而省掉内部校验预算。
- 同fresh `_read`完整validate后读取head，无snapshot/project_get/public_project调用；集合核projects/app/public双向覆盖及UUID，实际draft缺失/墓碑/null分支独立。缓存是私有bytes tuple，页面解码给新值；single-use后页先删除原token再编码，失败不会遗留旧槽。
- clock作为唯一外部callback，目前调用发生在_read之外；已建议若支持注入，有限化异常/巨大数与明确单调假设、回退策略。若仅受信测试hook且生产固定monotonic，应写实，不能把任意host Python callback副作用当本模块产品威胁。此为边界建议，未虚列第二个实质P2。
- 新测试zero_write当时允许PRAGMA user_version不区分其second参数；同值/异值写header可能不被authorizer或iterdump捕获。已建议读取user_version必须无写参数并加负控；当前模块实际只读，不能把测试证明精度问题说成已发现模块写库。继承旧测试不需改。
- 未来resolution需要充分Job claim/context验证，不能把此format3.validate（Store/app权威）改称完整Job claim归因。当前只读catalog/workspace不提供resolution，不据此扩大本模块责任。

源码与新测试相关切点的读取`a96233`/`cbd059`/`351f3f`exit0；全部首失败/修前修后身份保留。后续将根据真实read-ready最终源码、测试及合同补绑并做最终全范围意见；本节不构成尚未冻结候选通过。

## 首Read-ready候选第二项P2：碰撞可复活已消费游标（历史待修，现已关闭）

主线正式read-ready输入为：新模块14995B/SHA `6d009c8a00f9bb44c7e78af266fd7a11970db74b1a2ddb19ba2383d0bfb689dd`；新测试22971B/SHA `0e4829af9a1c35c290ace56e65484ae8912b1be67fc3fb31c6ee5ebe20f00a71`；实现文档12282B/SHA `10e75768f38b7292044f29a27fb12138cc1e43d4e37d56c9c4f3bb43595e56dc`。作者47专项与当前check并非本agent运行，本报告不提前改成最终通过。之后修订须另绑身份。

### 触发、影响与原件

`catalog_next`先删除旧token，再`_page`生成下一token；碰撞处理只看当前`_catalogs`，因此刚消费token已不在集合中。entropy若返回刚消费值，就被重新安装给下一位置。新测试只覆盖撞另一个仍活动的token，未覆盖这一单次语义反例。

独立`9eadff`exit0，真实自有临时JobStore3三项目/page_size1：只在本probe进程将`secrets.token_urlsafe`替为返回刚消费token（无文件改动），第二页`nextCursor`实际等于旧token；再重放原token成功取到第三页offset2。完整dump不变、源运行前后同6d009c8…89dd。这个机制fixture证明碰撞处理与“旧token不可重放”的合同不一致，**不声称攻击者能预测正常256bit随机或已发生领域写越权**；实质影响是已消费定位身份复活/错误前进及分页响应时序不可依赖。

最小修复不能只排除当前活动token；仅排除本次consumed值也未覆盖早先已消费/已完成目录旧token在后续重发。若保留单reader全生命周期不可重放且不保无限consumed日志，建议有界单调counter参与唯一token身份，到顶安全拒绝/close，或给可证明有限的等价唯一性方案与跨快照旧token策略。不能以清空active map让旧token重新可用。相关反例要覆盖刚消费、取消/末页后旧token及另一仍活动快照，且不改继承测试。

已即时发主线，要求当前check自然结束后再改源；本报告将保首候选原件与修后身份分别核，不把首check覆盖修后源码。

### Read-ready其他增量核读

主线已按建议有限化clock：异常/非有限/巨大整数转换/回退均state且清掉memory，可信clock非renderer输入；未宣称CPU隔离。新测试读回了47项包括真实完整目录/工作区/大稿、draft三态、缺mapping/app/head/snapshot/metadata/hash、真实重开、缓存/过期/资源与active外事务，损坏fixture按原SQL重建immutable trigger，未修改生产约束。

新authorizer已提取共享规则，user_version有写参数的同值3/异值4均拒，负控用同一authorizer而非另造拒绝函数；这关闭此前零写证明精度建议，不是模块写库P2。`f88b9f`读实现文档与clock增量，`b12052`、`c653dc`读新测试/碰撞处理与负控，均exit0。测试和最终合同仍按后续实际freeze收口。

## 最终代码候选及第二项P2关闭

| 最终输入                                                       | bytes | SHA256                                                             |
| -------------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| `packages/engine/src/ontolearn_engine/project/project_host.py` | 15777 | `a142d9dc9e3c56c51110fd21125c65cc72a19631743be92ccf2e8be98da4edeb` |
| `packages/engine/tests/test_project_host_read_services.py`     | 25403 | `f27a53c8f69398bd16ec7b40fadd2d03e28927a2f5aa3f9751569bc6583ede64` |
| `docs/iterations/T01/project-host-read-services.md`            | 12820 | `a27a4d0a8a26cb99558eae529e323b7310fd35b3edd24bf6ee57138ba317ed3f` |

独立`acc182`exit0核三输入原字节；`e61ad4`实际核counter/namespace及新测试/文档相关段，工具输出超预算部分截断不称其全文。此前模块/文档全文加最终实际delta已核，测试按各功能/新反例实际断言读取，不以52数量替代质量。root明确最后完整check启动前未再变这三输入。

修复在每reader保存独立UUID namespace和从1到既有MAX_VERSION的有界递增counter；token编码32hex.namespace + 点 +16hex.counter + 点 +43字符随机后缀，共93ASCII。counter在entropy调用/页面编码之前消耗，包括失败页不回退；不保无限consumed日志。exact str/len93/完整格式和当前reader namespace先验后才查私有map，suffix也exact str/len43/字符集，异常有限state。reader counter到顶只拒还需产生cursor的目录/页，不wrap，也不阻止不需要cursor的单页读取。消费后页失败释放其整份快照，其它目录不被覆盖。

独立`a7f1d5`exit0在最终a142d9源的真实3项目Store3上，把entropy固定为'A'×43：连续页的93字节token不同，原已消费token重放拒绝；末页结束后新catalog仍拒旧token；两reader同固定suffix产生不同namespace/token，交叉token拒绝。counter置MAX后需cursor的后页limit、已消费快照被释放，单页读取仍成功；整个逻辑dump不变，运行前后源SHA同a142d9。该项P2闭合，未把这是正常随机可预测的攻击，也不宣称任意OS entropy源完全失陷仍有无限身份保证。

### 最终全范围意见

1. **权限/零写/事务**：消费真实已持有JobStore3，fresh read transaction内核实际header3后预算/完整权威/投影；active外事务拒绝且不rollback调用者。无路径/new connection/创建迁移/持久cursor/新RPC或grant。后页是原冻结内存，host真实能力失效必须close reader，这项真实main/I06 hook仍未交付。
2. **权威而非只hash**：先聚合预检，后同txn完整format3.validate与双向项目集合校验，再读既有checkpoint/snapshot；真实当前domain/app及receipt链互证，不补mapping/snapshot/placeholder，不调用已知写helper。该权威是本模块要求的Store/app历史，不冒充完整Job context resolution。
3. **预算/缓存**：只可收紧默认值；schema、所有表行/列CAST BLOB字节及重复decode work预检在物化validator之前，catalog worst-case留存预付费在capture前。snapshot/row/page/workspace/draft完整编码有界；页先编码再安装，后页消费/失败/到期/末页/取消/close释放；epoch/counter不无限积累日志。限额是工程拒绝线，不是Q5/RSS/CPU或跨reader全局容量实测。
4. **DTO/一致性**：public UUID真实映射与稳定顺序、同名/archived完整metadata；workspace同txn拿真实base/snapshot/metadata/version/sequence/checkpoint与指定editor，未创建/墓碑/null不混、旧bound内容不假冒当前CAS、不输出整domain/learning/audit。返回副本不回写缓存。
5. **测试真实覆盖及限制**：新测试用实际Store应用CAS/域写构建合法证据，不自造成功checkpoint；真实authorizer和dump/事务trace、不可变表损坏fixture按原SQL恢复触发器、真实close/reopen UUID、多页/metadata更新/大稿/draft三态、缺mapping/缺证据/坏header、预算/TTL/active外事务、clock/entropy/counter等逐断言。模拟坏数据、受控时钟与entropy是机制fixture，不是磁盘断电/真实并发writer或位置许可证明。无新schema/依赖/旧测试维护。
6. **兼容/范围**：48输入只读继承，不改task-runtime；本阶段两条新code/test与必要文档。不实施创建/resolution/DDL或公开协议，相关精确合同由另独审负责；本报告只核读取服务及其实现文档，不替代另一合同审查。默认2、原完整首版/四入口/位置/I06生命周期/T09/编辑/Agent/全restore/learning/44及57P0和指定双审/CI/正常合并/远端门不变。

当前未发现修后新实质代码阻断。不会为已关闭反例或无变化继承项再跑矩阵；最终只核原件真实终态和输入无漂移。

## 最终运行字段初始登记（历史，实际终态见下）

- 主线最终`npm run check`：exec aba62e、session5551，日志`/tmp/t01-project-host-full-check-04.log`。**仍在运行，exit/count/hash待实际结束后补入，不提前记pass。**
- 作者pytest05为52pass、ruff06为pass属于作者已通知的专属证据；待原log/终态读回，不写成独审运行。
- check02为当时45项候选、check03为修前47项候选，虽主线实际报告自然exit0，也不能覆盖最终a142d9/f27a53；它们是历史/被替代验证。首fixture碰immutable trigger失败及修前9eadff均保留，不用最终通过抹去。
- 本独审实际运行仅2dc34e修前头反例、efa3f2修后头+零写基线、9eadff修前token复活、a7f1d5修后counter/namespace闭环；均完整exec对象已emit。没有执行全仓/52专项、GUI、引擎包、IPC/native或产品窗口。

## 最终真实运行原件与输入封口

本独审没有再次执行全仓/52专项。以下由主线运行，独立读取完整原log、核原字节身份，并区分主线exec退出元数据与stdout文本；不把log末尾passed自行当新运行退出证明。

| 最终原件                                      | 主线实际终态 / 独立读回                                                                                                                                                                                                                                                                               |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/tmp/t01-project-host-full-check-04.log`     | 8441B/SHA `f396e35b42e4dbcd264aec18055e4716ede138ccec870b211a511ae768a19524`。start exec aba62e/session5551，write_stdin70ca9d exit0；lint、format、三类型、22文件1125TS、三段build、ruff及195文件format、Python实收集2885=2841pass+44既有skip/79.08s。52条新read-service实含其中；不把44skip算pass。 |
| `/tmp/t01-project-host-verify-sources-01.log` | 111B/SHA `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`。主线exec60f3c4 exit0；12归档源核验，不等于本次48输入或新功能通过。                                                                                                                                                       |
| `/tmp/t01-project-host-target-pytest-05.log`  | 99B/SHA `4520a68c2ccd9a0c9c1e19032dc195cd011702b1dd9642f388f0b39c451b84ef`，52pass/0.92s；作者通知真实exit0。其后最后精确length guard等小收尾以最终check04覆盖，不把这个较早目标日志冒称已绑最终全部字节。                                                                                            |
| `/tmp/t01-project-host-target-ruff-06.log`    | 19B/SHA `82b3e6a6c090a57601d22943bd23fca9218d1031dbe5a7b754092f9a156b4f18`，All checks passed；作者通知真实exit0，最终同字节静态由check04再覆盖。                                                                                                                                                     |

完整check正文读取`6fdf21`已输出全部8441B log；该调用尾部`rg --files /tmp`遇部分不可读目录返回2，是文件发现命令的整体exit2，不是主线check失败，也不能写成该读取工具exit0。随后`47f6b6`exit0完整读取sources/目标logs并核上述4原件bytes/SHA，与主线通知一致。首fixture不可变trigger失败与旧check02/03保留；旧check02/03自然通过不覆盖最终counter/namespace修后源码，最终只采用check04。

独立`c1c448`exit0再次核48继承输入原字节与根manifest相符，最终新增模块/测试/实现文档三SHA均未漂移；48项尤其task-runtime未改，未扩写维护权。该核验只读，不执行/复制继承测试。AGENTS/common仍按首实际回执保护，原5de/427树和其报告不被本阶段改写。

最终代码及新增52测试、实现文档的机制边界与实测结果相符。两个实际P2关闭，零写/完整历史权威/有限预检/目录快照/指定editor三态/资源释放与游标单次语义没有未解实质阻断。支持交总控冻结本内部阶段，再履行指定同版双模型、CI和正常合并/远端门。**本独审不替代指定双外审**，也不替另独审的create/resolution合同作通过结论。

未执行或未证明：实际任意位置picker/首次DB I/O能力、I06 inventory/OS adapter及生命周期hook、main/preload/renderer/IPC/人类选择或完整Diff接受、公开3启用、创建/只读resolution实现、真实并发writer/磁盘故障/包内新read服务、native/目标平台与Q5性能容量、四入口/T09完整示例、编辑/Agent/全restore/learning及父44/57P0。当前只是私有读取服务，没有根据测试数量/metadata存在缩去原范围。

本agent只写本新独审报告；所有产品/测试/继承项/依赖/其他报告未改，无GUI/Electron/e2e/native/HMR/凭证或外审应用。最终以本树formatter显式`--ignore-path /dev/null --write`与同选项`--check`实际完成格式核验，报最终bytes/SHA后停止写；无变化不复测。
