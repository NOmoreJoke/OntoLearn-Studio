# T01 正式 ChangeSet 业务服务独立实现审查

**最终意见：固定14输入无未解实质代码阻断；两项P2已独立复现并在最终版本定点关闭，支持将本内部ChangeSet业务服务阶段交总控冻结与指定双审。** 已独立读回本候选完整check、新unsigned包CLI及实际资源绑定原件；下文保留初始接收、修前和中间候选历史。结论仅适用于显式internal3 typed ChangeSet/undo，不代表父FR、真实人类确认、Electron/native验收或指定双审/CI/合并完成。

## 实际授权与固定起点

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`；过程HEAD实际 `f51a9e10647d75cd07fe28007ab73c0e65451f63`，产品/测试起点为 `fd3944a35aed05c279d7d0c2f9a077c84d99aaf2`。授权接收时packages/apps/tests/scripts与依赖锁工作区差异清单为空。
- 已全文实际读取根 `iteration-control/2026-10-21-weekly-release/T01-changeset-business-service-implementation-authorization.md`，SHA256 `421f974c43975886d280386316b34b5f1e284712d68d38f338d8083beb217467`，对应固定计划27888B/SHA `39ebbf378386004eb9e8654bf9dbd7465e50d5215a87c55fde01cffc258d71e1`。授权属于原T01/原Goal，不重建任务，不将f51当远端批准基线；原集成基线仍5f910b52c69d86a1076b2032e5d3c63e715947f3。
- 最新共同指令已全文实际读回，SHA `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`；本树AGENTS实际保护SHA `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`。原第九节/无桌面/默认完全访问仍适用，不因政策重开旧产品审查。
- 旧计划独审固定SHA `d4869249d713abd168a352e5ac0fe5996bcbe972ddad6ab99725f3b255aeb6a0`，不修改该报告；本轮只写本新实现独审。根指定双模型/CI/正常合并/远端及父FR/真实UI门保留，不由本独立agent替代。
- 上述完整工具返回对象已emit：授权全文/hash `651a2d`、共同指令全文/hash `1d32cb`、HEAD/保护规则/计划/旧报告hash及空产品工作区差异 `0050d2`，均exit_code0。没有在此接收阶段执行产品、测试、探针、GUI/Electron/e2e/native/HMR或桌面审查应用。

## 精确施工与独立只读边界

获准产品10条：

1. `packages/engine/src/ontolearn_engine/project/domain_changesets.py`（新增）。
2. `packages/engine/src/ontolearn_engine/job_store.py`。
3. `packages/engine/src/ontolearn_engine/coordinator.py`。
4. `packages/contracts/v2/schema.json`。
5. `packages/contracts/v2/registry.json`。
6. `packages/contracts/v2/fixtures.json`。
7. `packages/contracts/v2/binding-regressions.json`。
8. `packages/contracts/src/v2.ts`。
9. `packages/contracts/src/index.ts`。
10. `packages/contracts/python/contract_v2.py`。

获准新增测试仅 `packages/engine/tests/test_project_changeset_service.py`、`packages/engine/tests/test_project_changeset_stdio.py`、`tests/unit/t01-changeset-canonical.test.ts`、`tests/unit/t01-changeset-runtime.test.ts`。私有新报告/阶段证据可按根授权增加，不覆盖历史。

不改transactions/storage/format3/applications/worker/protocol/resources、dependencies/errors、任何desktop main/preload/renderer、build/依赖锁/CI或已有测试。旧task-runtime窗口已关闭，未来I05维护，T01只读。必要额外路径须先给实际反例/首失败和最小申请，不能借报告证据或helper另造服务、writer/schema/authority。

本独审不参与产品实现或修作者源码。只在作者实际read-ready后绑定完整路径/SHA与当时验证身份，独立阅读相应实现/新反例；必要小型真实probe无窗口执行，emit完整exec返回对象并保留首失败，明确机制注入/真实OS、源码/包、静态/运行/真人UI范围。不重复作者大矩阵，不提前测试不完整WIP。

## 初始分组交接与待收read-ready切点（历史）

| 分组 / 作者                                                           | 未来独立审查切点                                                                                                                                                                     | 当前实际状态                                                            |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| 7 canonical产品+新增TS canonical / startup_canonical                  | 新strict3方法/pending/result直接绑定；ready/conflict有限union、diff/undo-impact文档隔离；raw/base64/页预算与真实重组helper；正常2/旧startup/sourceTable值和语义兼容                  | 已请求read-ready路径/SHA/实际终态与首失败原件，尚未收到实现；不判通过。 |
| 新domain_changesets+job_store+新增Py service / recovery_design_review | typed触及前后可逆、真实Store回滚预览、四hash/prepared版本分派；完整Diff/impact持久分页；首次confirm与typed原回执、TTL/GC/newRPCid、Session与新op/旧claim；重开及receipt/terminal原子 | 已请求实际分组read-ready及范围，不读取/执行WIP作为验收；不判通过。      |
| coordinator+新增Py stdio/TS runtime / 主线                            | 仅internal3/testMode=false正式cap；实际host/Session/project许可；无worker确定性分支；受理与提交两个线性化点、正常dispatcher取消闸；真实CLI/Node重组→confirm→Job/undo/operation/重开  | 待主线实际read-ready，后核跨组三段真实链；不以纯schema或服务单测替代。  |

## 必须逐项保留的独审与验收口径

- C01：真实typed事实/ontology两关联定义及references；触及before/after可逆，未触及opaque保留。实际rollback preview不改变正式域/marker/历史；ownership、单值、悬空引用与结构反例不靠假metadata或test参数。
- C02：canonical UTF-8 raw完整Diff/impact，16MiB总量、32768段、最多512段及原262144 blob/manifest上限；base64加完整JSON/page/frame先计费再原子保存。实际helper核顺序/offset/长度/段hash/整值hash、UTF-8与JSON，真实Node调用；漏页/乱序、跨项目/Session/文档kind或未完成cursor不能凭摘要放行。
- C03：preview无确认；首次签发核活完整链、当前base/前态/control/结构/引用/ownership。同一确认事务写实际confirmation行与严格job_details原业务请求/hash/响应互证；同host/Session精确重试先原回执，原cursor TTL/GC/base推进不重签。RPC id/timeout/retry计数不是业务幂等身份；缺失/不一致fail-closed，不补造。新Session/新op来源重新验证，与已claim原operation精确跨重启对账分别测试。
- C04：新版本prepared与旧test/application双向隔离；ChangePreview.identity、prepared ref、Store marker fingerprint及Job context fingerprint分别核验，create/retry/validate-reopen/commit同分支。真实严格3正式Job而非test.atomic改名/worker rows，实际implementation/input/依赖及public marker/私有Store3 receipt不混。
- C05：claim+queued受理事务与domain/marker/Store3 sequence/checkpoint/receipt+Job receipt result+succeeded提交事务分别线性化。running后真实让dispatcher受理cancel，先闸取消零域写、提交后alreadyTerminal，不承诺同步SQLite途中可收新取消。逐相关持久边界异常/模拟存储失败/取消/实际子进程退出与重开，完整持久状态/允许已受理Job终态分开，A-02无半批，丢响应先原operation对账。
- C06：正式undo保留不相交B、同资源/ABA/后续引用/ownership/单值阻断。impact来自实际目标前后/control及至固定base完整历史、当前refs/owner/slot；缺证据impactComplete=false并暂停、预算不足整体拒绝，不从异常文本/单个错误码冒充全清单。冲突结果没有提交凭据，Store预演仍唯一可提交判断。
- C07：真实Store发布结果的依赖失效与无关结果保留、版本前向；不把合成结果/机制测试称真实T04/T05领域producer联验。
- C08：实际受影响专项、独立代码审查、完整npm check/verify:sources，新同候选unsigned包实际正式提交/undo/重开及canonical同源。原fd启动通过不能迁移为本业务阶段通过；首失败、源码/资源/包hash、Git与实际session终态保留。

完整44项地图、FR-001–006/804、57P0/原附录和发布门保留：本阶段不是实际人类Diff观看/点击、main项目选择/命名bridge、真实Agent完整A-01/A-02、metadata/draft/learning/辅助账本完整项目恢复、完整消费者或平台/native验收。受信host机制不得自称人类授权，原Goal不自行暂停/完成，也不提前push。

以上为授权接收时的切点登记；实际实现、修前反例与最终候选读回见以下追加。

## 最终14输入固定与独立复核

实际全文读最终manifest，独立逐条读取工作树原字节，核全部10产品/4新测试的bytes/SHA，并核ZIP14个唯一成员逐字节等于工作树；manifest为ZIP外独立文件，不声称ZIP内有manifest。`d3ecd5`完整exec返回exit0：manifest2573B/SHA `21ce587382ed854b29c1b38ad2646a573e01273b3efd4950709e0786e8518b21`；ZIP146725B/SHA `64d03db87de4523dd4c2d5e547e3e98ba0431ade82f1ebde760a747916a35d68`。

| 实际路径                                                            |   bytes | SHA256                                                             |
| ------------------------------------------------------------------- | ------: | ------------------------------------------------------------------ |
| `packages/engine/src/ontolearn_engine/project/domain_changesets.py` |   34728 | `e38f9d58a31f3bb38dc7b2da58f3da26811d3a6cfcc2a5f43a5a10f9b71dfb9a` |
| `packages/engine/src/ontolearn_engine/job_store.py`                 |   86648 | `e40e75f28cb238575a122a35e38d108a264bddebe507cbd6d5010cb113385ad4` |
| `packages/engine/src/ontolearn_engine/coordinator.py`               |   41168 | `6e057cbdd76c674813d9f90e231306cb9cf5611ef7fcbeb234de13d698afa18c` |
| `packages/contracts/v2/schema.json`                                 |  207256 | `e913138e6f3ac632268ae7f8c2461577022e8298d1c03e0668416a0d654eaabf` |
| `packages/contracts/v2/registry.json`                               |   15962 | `1f2e298209e238433c02864a05c70b24482e4c1fd00e7309f63eac84a1f3706b` |
| `packages/contracts/v2/fixtures.json`                               | 1179996 | `b6edba394693d98dea613fb9dcc128d3d8eb0f2f6ee0268b0c5a2e8af8cedd5f` |
| `packages/contracts/v2/binding-regressions.json`                    |  304069 | `352b95dbb17eb7f359ac9cd7a16fc6bab3b92a361d9b77488f5668c151895e1c` |
| `packages/contracts/src/v2.ts`                                      |   36693 | `4dd0b43206bb97f223386b07e67dea0af18a651de9e930a94a877986bf7b7535` |
| `packages/contracts/src/index.ts`                                   |   15088 | `fc140c935238c4900d724562774a43e5ae1c9da2fb39bd367e8154b08409626d` |
| `packages/contracts/python/contract_v2.py`                          |   34608 | `17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7` |
| `packages/engine/tests/test_project_changeset_service.py`           |   38107 | `486f841318f2856332f887e41c843688e154fc98b839b601f3fa6a5085200aed` |
| `packages/engine/tests/test_project_changeset_stdio.py`             |   22010 | `2d3ab4f1eb010444b01c31b6eb2e215d41785ad369dc94c35b6f1f8fcca64c52` |
| `tests/unit/t01-changeset-canonical.test.ts`                        |   15464 | `d6e9eba166ffe82f55895efeaf50c94340e32f793a8ddf2ee865db4b8cacf32a` |
| `tests/unit/t01-changeset-runtime.test.ts`                          |   13415 | `da5e9ca35e345cfcd5db4b568b08ae8f25f887bb6966da63a796b274a75d382a` |

`git diff --name-only f51a9e1 -- packages/apps/tests/scripts及依赖路径`列9个已跟踪产品变化；新增domain/test由上表直接核原字节和ZIP，不把git diff未显示的未跟踪文件当作不存在。最终候选不修改storage/transactions/format3/applications/worker/protocol/resources、desktop、构建、依赖锁或已有测试。

初次归档校对`514dde`误沿用上一startup封套“源+manifest共15成员”的假设，Python AssertionError实际发生；该调用随后只读命令使shell最终返回0，不能将其记为归档核验通过。已保留原返回，修正仅审计假设后用独立单Python调用`d3ecd5`真实exit0，核本封套14源成员、外置manifest。没有改任何产品/测试/归档。

## P2-01：同步getter突破重组前预算，已关闭

**修前身份与触发。** `packages/contracts/src/index.ts`11703B/SHA `9570dd4f62371ac0d1e6fb507d26b62eeb91706b4afaaddea039d11c541a08c6`，原重组函数245–269附近多次读取caller `expected.manifest`、之后structuredClone，再用克隆的totalBytes分配。自持getter前5次给合法655B manifest，第6次给16777217；单线程同步变更即可绕过先前验证，不需要await。独立真实源码内存编译probe `50b9cb` exit0，getter读取6次，确实尝试16777217长度分配。探针以自持Uint8Array Proxy在真实分配之前抛`AUDIT_BLOCKED_OVERBUDGET_ALLOCATION`，没有实际分配超预算数组；完整返回保留，不将“被测试拦截”误称产品原本安全。

**修复与最终复核。** 最终helper SHA `fc140c935238c4900d724562774a43e5ae1c9da2fb39bd367e8154b08409626d`：先以own descriptor投影必需三个字段，拒绝accessor；对该投影与pages做一次有节点/深度/数组/字段/字符串预算的data-only capture，只接受own数据描述符与普通/null原型，不调用getter/toJSON/自定义实例。schema、aggregate、Uint8Array和所有异步digest之后均只读私有副本。无关DTO额外字段不进入capture，因此真实11字段ready仍能结构传入，不因对象8key预算被误拒。

独立修后`5a7042` exit0，实际在同一最终源内存编译：原getter切换反例现在`INVALID_CHANGESET_DOCUMENT`、getter读取0、数值分配列表空；实际完整11字段ready再加一个抛错extra getter也成功重组，extra getter读取0，结果与原完整JSON结构deepEqual。前一闭环probe `1ee018` exit1是审查器使用JSON.stringify比较对象键插入次序而误报；只把独立断言改成deepEqual后成功，产品未改，原失败保留。作者最初capture修版曾max8直接接收ready11字段的兼容问题由主线静态发现，最终三字段descriptor projection关闭；不冒称该中间版通过真实ready集成。

边界：JS反射对恶意Proxy不能提供绝对“零回调”保证，代码和既定data-only owner输入合同明确保留此限制；本项证明普通own accessors被拒、私有捕获之后不二读caller，不声称任意敌对Proxy可在原CPU内安全执行。

## P2-02：同ref坏缓存行被INSERT OR IGNORE接受，已关闭

**修前身份与触发。** domain初版SHA `c5571173213d3e314323210e8bea12a1f26625100b40687c23fff95b8139e39b`、JobStore `e40e75f28cb238575a122a35e38d108a264bddebe507cbd6d5010cb113385ad4`。新预览对segment/parameters调用既有put_blob，只获得由请求计算的ref，却未核该ref真实已存payload。独立`060359` exit0在实际临时JobStore3中，离线构造该segment ref对应损坏payload后再正式preview：返回ready、增加1 prepared，整库相对损坏基线发生变化，随后第一页才INVALID_STATE，域revision0。该探针明确是离线损坏fixture，不是普通API可直接篡改不可变表；实质要求是遇坏库不得发布不可消费preview/继续污染应用历史。

**修复与最终复核。** domain最终SHA `e38f9d58a31f3bb38dc7b2da58f3da26811d3a6cfcc2a5f43a5a10f9b71dfb9a`：同事务`_intern_blob`写后读真实blob并同时核digest/fullvalue，segments和parameters都经该入口。job_plans写后核真实project/payload并调用完整`_verify_plan`，包括base/planHash/diffHash/preview/snapshot/parameters/document；conflict detail写后核实际project/payload及完整document。不修坏行。

独立`3bea51` exit0，在最终实际源码的两个自有临时库分别复现segment与parameters同ref坏行：均INVALID_STATE、整库dump等于损坏基线、prepared行0、域revision0。静态逐行核prepared/impact写后验证使用同事务且不是校验请求变量后就返回。作者新增3反例的首候选3FAIL与修后78pass日志被通知保留，属于作者证据；本独审只独立运行上述两例，不重跑78矩阵。

## 全范围实现语义审查结果

| 范围                         | 实际代码及验收评估                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C01 typed可逆子集            | `supported`按真实before/after state_diff校验触及的ontology定义、manual/edits/remove事实；不把未触及opaque排除为整项目拒绝，也不把managed/owner/source_row事实冒充手工事实。预览实际ProjectTransactions rollback，Store仍唯一结构、引用、单值、ownership裁决者。旧opaque触及前态也拒，未触及保留；不靠假metadata或test.atomic输出。                                                                                       |
| C02 全文Diff/impact与预算    | canonical raw UTF8完整文档切段，raw16MiB/32768/512、manifest/blob262144；preview先逐段检查base64页/frame预算再写段/plan。page按绑定/原size/实际编码选择段，完成cursor非null。helper逐段、全值hash/长度/顺序/offset/UTF8/JSON及complete收尾，未将“取完整链”写成人类已看过。上述两P2补强零分配前捕获与真实坏行拒绝。                                                                                                       |
| C03 首次confirm vs原持久签发 | `_envelope`核原host/Session和完整冻结plan；已有confirmation先核同UUID receipt与签发行逐值互证、原完整业务params/hash/响应，之后直接回原结果，先于cursor TTL/GC与current base。首次才遍历live完整cursor chain并核当前base与真实重新preview；改cursor/换Session或孤立receipt拒。wire RPC id不进持久业务request，因此新RPC id合法精确重试不冲突。hostClientId只是成功hello归因，allowedProjects仍许可来源，不能称真人授权。 |
| C04 四hash/namespace/重开    | preview.identity、版本化envelope ref、Store plan fingerprint、Job context fingerprint有独立作用。新namespace在`_job_prepared_plan`正式cap分派，create/retry/reopen/commit均通过完整验证；旧普通test plan精确shape分支仍保留，双向不可拿凭据互换。新op核当前host/Session/base/state/control；原已claim先验证原context返回原Job，不依赖今天临时Session/cursor仍存活。                                                      |
| C05 两事务/取消/原子         | JobStore先持久claim+queued；正式execute分支不spawn worker，start running后实际`await asyncio.sleep(0)`让dispatcher处理取消，再核持久cancelling与total deadline。Store提交/marker/Store3历史/receipt/结果/succeeded同提交事务；hook失败全滚，after_commit异常先查真实terminal避免重写成功。SQLite同步提交期间新读到stdin不等于dispatch取消已线性化，测试scheduler机制明确，不承诺中途可新受理cancel。                     |
| C06 完整undo阻断             | impact以实际target Job/claim/committed reconcile+可信前后snapshot/control、至base连续所有revision的immutable证据投影；value变化/后续编辑含ABA、真实引用/owner/slot合并分别列出，不依赖ProjectFault异常文本或单个码。missing history/unsupported target明确completefalse并不给写凭据，conflict cursor不能升级confirm。真正preview_undo与Store仍最终判断，服务投影不代裁决。                                               |
| C07 结果失效                 | 正式发布沿现Store实际invalidation与Job receipt路径，测试核真实依赖结果与无关结果current保留；不是接通T04/T05真实producer，也不把机制结果当领域消费者实测。                                                                                                                                                                                                                                                               |
| C08 strict3/实际链/旧2       | 成功hello新cap完整strict3先验证后直接匹配；正式preview/page/confirm直接pending匹配，没有旧2投影漏字段。旧2/schema原分支、registry旧cap及sourceTable逐值保护独立比较见下。实际Node/stdio链与故障矩阵已读源码和作者证据，最后完整check/新包待原件绑定。                                                                                                                                                                    |

本独审实际全文核domain/Job新增分派/coordinator正式分支、新canonical/相关新测试。代码支持有限typed ontology/manual ChangeSet与正式undo的内部3路径；未发现修后新的实质代码阻断。C05测试中的SQLite authorizer/机制异常/受控scheduler不能称真实磁盘断电或自然取消时序；真实os._exit要逐实际原件单列。本审查没有重复作者故障矩阵/全仓测试，也没有执行GUI/原生验收。

兼容性独立比较`31a0ff` exit0：旧strict2 definitions保持原parsed值；旧request3/response3的原oneOf前缀保持，只有这两个原def追加分支；所有旧capability entries、旧registry非foundation/capabilities项及sourceTable原值不变。旧startup/business3仅按同版完整registry hash刷新，不把旧字节hash复用为新同源证据。已知实际Node17cap hello首失败与修复由主线/作者发现处理：初TS `63890b…`/Py `0e1166…`经strict3后错误投影至旧cap白名单；最终TS `4dd0b4…`/Py `17aa68…`仅在完整成功hello strict3验证后直接true。该修复与首失败日志保留，本独审不重复已被明确分配的同一探针。

## 运行证据待读回登记（历史）

主线已通知最终同候选完整check及新包harness正在运行；在收到真实终态、原log、包/实际资源绑定前，本报告仅给最终代码候选审查意见。作者报告的新78服务、93canonical、stdio5等均不冒充本独审运行，也不据此把父FR/完整产品/真实UI通过。最后只需核实际原件与最终输入无漂移，不重跑大矩阵。

## 最终运行原件读回与证据边界

所有以下运行由主线实际执行，本独审逐原件读回并作独立纯读取交叉验证，不把主线执行冒称本agent跑过，也不重复完整测试或打包。

| 运行 / 实际终态                                              | 独立读取原件及范围                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 完整`npm run check`，主线session73730/chunk e2ee33，exit0    | `/tmp/t01-changeset-fullcheck-01.log`8269B/SHA `30fbb987d484118dd70a1cd9975d76862244e5b6e1bede2174323c21a96c8888`，全文读回：lint/format/三类型检查、22文件1125TS、build、ruff及format、2789Py通过/44既有skip，实际收集2833。新业务4测试实际包含其中；未把44skip称通过或缩去原门。                                           |
| 串行新`npm run package:dir`，session79110/chunk219fea，exit0 | `/tmp/t01-changeset-package-02.log`14323B/SHA `f5ea2a89a04617e3208ea20aba2387c8ea4932c739ed0cad75ba404c86994fb9`，全文读回build→PyInstaller→electron-builder --dir --publish never；identity null，macOS正式签名跳过，未启动产物。                                                                                           |
| 新实际包CLI正式业务probe，session2986/chunk e651b4，exit0    | `/tmp/t01-changeset-packaged-probe-02.json`10988B/SHA `5565d6f9462a396b8839d5a42d0034e36cce11fe12a896169569f2e4dd7ebce1`；真实frozen executable/testMode=false，包资源9项；首提交A、不相交B、正式undo A、重开原operation对账，3formal claims/3receipt、domainRevision3/sequence3，最终只保留B。                              |
| 新实际asar/resource静态绑定，chunk616324，exit0              | `/tmp/t01-changeset-package-bindings-03.json`1951B/SHA `7d9d5de09ac003618e79db3446807b4ee0ba49e1b267c2d542d6377bebf4512b`；编译main404503B/SHA `fcdd498ce6084b10369648512a11fba931306f3164d88448caf7ef841776b850`与实际asar逐字节相等，完整registry AST数据值等canonical、8JSON双副本、Python helper、lock和实际engine同源。 |

上述log/JSON身份由独立`0abc6d` exit0核原字节；全文读取`dcc82a`末尾仅`rg --files`在部分/tmp目录返回2，前面cat原件已完整输出，不能把该工具整体exit2误报为运行原件失败。后续`403359`真实exit0读包log、probe/binding summary及静态harness源码。每个运行的session/chunk/exit属于主线实际返回，日志文本本身不虚构退出码。

### 独立原始wire交叉核对

`b7c6d4`完整exec exit0：从stdio-traces选出本次包project的两个真实Session，逐stdin/stdout/stderr严格base64 decode、核bytes/SHA，命令必须等于实际包exe且testMode=false/returncode0；全部response对原request id与method，hello成功selected3且两个Session身份不同。

- `/tmp/t01-changeset-stdio-traces/6ace55d7-43d8-479a-a45a-59baf7bfee3a.json`54276B/SHA `2f916f5ba819ef75f878be55087a823332c2b4393bd73b1afbe94da2b9483f74`：实际hello、project、三轮preview→page→confirm→job.create→job.get，全部响应无错误。
- `/tmp/t01-changeset-stdio-traces/ca6926f7-bf7b-4176-95f8-0cfa3e5beff3.json`20440B/SHA `3e65dee795e4900cfe5db97c2e7d8dd9cdb101fb7bb2a1250069eaf734e70154`：新Session对三原operation精确job.create+operation.get，对另新operation复用旧Session确认得到IDENTITY_CONFLICT，没有把老claim重试误判为新授权。

本独审据实际probe状态核3claims/3receipt/domainRevision3/sequence3，undo后definitions空、唯一事实subject=`urn:asset:B`。这些是包引擎CLI持久行为；没有调用Electron handler、真实IPC、用户Diff观看/点击或主线程项目选择。

### 独立当前包静态读回

`399005`完整exec exit0只读实际当前文件：重新核main与asar提取字节相等；8JSON在外部contracts与engine内部contracts两处都等最终canonical；helper SHA `17aa68bc2271b45ffb70a023b9db9e441bb1b4e79fc9a42bb6932f60631be7b7`，uv.lock SHA `d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e`，实际包exe SHA `10dea9b2e9f104707935fc4b418131d91b423548b07ed8f0598086f5783c95a4`并逐字节等build产物；该命令未执行任何Electron或引擎。

静态harness源码已读：只允许固定AST数据literal及严格`JSON.parse(单个静态字符串)`，不eval应用bundle。首绑定01实际asar/目录不等由主线并发check build与package改写nonce引起，原断言失败保留；不能沿用其包01原件作为最终同目录绑定。主线待check结束后串行新包02。随后绑定02旧AST harness遇Vite静态JSON.parse CallExpression拒绝的首失败也保留，仅补harness受限数据语法后03通过，未修改产品/依赖以“过测试”。独立`89131b`已读两首失败原log。

### 原源文件核验

独立`6f0183`exit0全文读`/tmp/t01-changeset-verify-sources-01.log`和`-02.log`，均为`npm run verify:sources`实际输出“已核对12个归档源文件”，两份SHA均 `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`。主线补回实际完整工具返回：02为chunk5122ec/exit0，01为chunk1cd109/exit0（前者先核manifest、以verify:sources为末命令），与上述实际log一致。 这只核既有12归档原源，不能代替本次14输入核验或功能验收；本次14原字节与ZIP另由`d3ecd5`确认。

## 最终范围与停止点

当前无未解实质代码阻断，支持固定本内部阶段并交总控/指定双审继续。独审完成的两项P2关闭、实际输入、首失败和修后探针均保留。默认2没有翻转，业务3仍显式内部profile；正式typed子集与undo已经真实Store/Job/receipt，不泛化到所有ontology/学习/Agent变更。

以下继续待原Goal/对应owner：完整44项地图/FR001–006及804，真人独立确认与host UI完整展示、项目四入口与创建/复制/导出等桥、完整Agent A-01/A-02、metadata/draft/learning/audit完整恢复与真实消费者、端到端取消用户体验、Q5物理内存/磁盘容量、真实Electron/native/IPC/平台体验、签名/公证/指定双模型/CI/远端核验与正常合并。没有因本候选测试数或checkpoint元数据存在就登记这些功能完成。

仅本新报告被本独审写入和格式化；产品/测试/旧报告/依赖/配置未改，没有GUI/Electron/e2e/native/HMR或桌面审查操作。最终报告封存后停止写，后续只对明确新候选/新问题接续，不重跑无变化矩阵。
