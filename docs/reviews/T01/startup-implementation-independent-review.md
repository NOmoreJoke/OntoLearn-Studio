# T01 business3/startup 独立实现审查

**固定候选代码审查结论：未发现尚未解决的实质阻断，支持本内部显式business3/startup阶段冻结。** 本结论绑定下述17产品/8测试原字节，P2-S1、root嵌套guard P2及reader实际状态收证点均已关闭；最终全仓检查、unsigned打包及包引擎stdio原件已读回并绑定同候选。它是本阶段独立代码审查与所列验证结论，不是父FR/Goal完成、默认生产3、签名发布、真实Electron IPC/native或指定双模型/CI/远端/正常合并通过。

最终候选 `startup-final-17-products-8-tests`，基底 `79d6bc4998ef49f8401636166b7e9fa7193c6b21`：[逐路径manifest](evidence/startup-final-source.json)，4500B/SHA256 `6ef21895a7e2b370f87896bc4f79a04425de852751cef16272a1f124d798c5b4`；[完整源码ZIP](evidence/startup-final-source.zip)，175431B/SHA256 `d3927873679cb89bf28031023f89081301df70c3c63a655afc6d588b5ed6e86a`。独立实际读回exec `574d04`、`564fa7`均exit0：25路径逐项工作树bytes/长度/SHA与ZIP相同，26个唯一成员为25源码测试+完全相同manifest；AGENTS保护SHA仍78df…a759。未解包或修改产品。后文初组与修前hash均为历史，不覆盖此最终身份。

## 实际授权与起点

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`，原功能/Goal保持；授权读取时HEAD为 `79d6bc4998ef49f8401636166b7e9fa7193c6b21`，当时仅AGENTS既有工作树差异。
- 总控 `T01-startup-implementation-phase-authorization.md` 已全文实际读取并实算SHA256 `3054a5ca2393ce6178e537c150f31b8fc0c63f3d28527a61b53cadeebfd6f334`，为最终严格五字段封套版；采用计划SHA `e9999d37a034fc365b8c5a345c3c135220e13c78b4f4907a763d81351d846b07`。common `e437121a…971b0` 和无桌面约束保持。
- 起始精确批准17产品/7测试（5新增、2已有T01专属状态同步）；后经根唯一临时窗口明确新增1条旧task-runtime测试，当前最终17产品/8测试，授权详见后文。I06余四、protocol/resources/worker/project-format3、design-v2/package/entrypoint/build/锁/CI及其他旧通用测试不改；新必要范围先精确报根。
- 默认生产2、packaged入口2；内部显式3和新启动诊断按真实profile、同源hash、Store→Job→reconcile、一次prehello/raw1024与原Session opaque凭据实施。不增source/learning/完整恢复业务，不改D7或取得新producer授权。
- 独立审查仅写本报告；不会改作者产品/测试或在其WIP中修单，不运行GUI/Electron/e2e/native/HMR。收到read-ready/冻结后才记录对应源码hash及必要小型真实探针，完整exec返回对象与首失败保留；不复制大矩阵。

## 固定候选审查覆盖与当前证据边界

| 分组 / 实际作者 | 独立审查切点 | 当前证据状态 |
| --- | --- | --- |
| 4 Python runtime + 2新增Python测试 / recovery_design_review | Store/Job父子所有权与每close失败首因；typed actual format；CLI有限argv/backup；两层及reconcile失败不hello；完整stdio原bytes/退出/lease；普通3 error不经过legacy吞值 | 最终字节已统一绑定；reader状态增量独立1例通过、真实CLI future/lease探针通过，52机制/26stdio包含于最终2706Py通过；包引擎真实stdio原件另核。 |
| 8 canonical + 1新增TS及2专属状态测试 / startup_canonical | 独立五字段startup封套/四安全error；默认error2/error3和原validator不变；normal3错误helper；展示union只展示；同源hash及原长接口 | 最终字节已统一绑定；新增转义pair独立raw1024/1025探针通过，原schema/sourceTable兼容核对完成；不代表producer业务全功能ready。 |
| 5 desktop + 2新增TS测试 / 主线 | ES #private/closure WeakMap；原attempt/startup/request/health promise及operation；每listener交付clone登记；raw reader→首错→TaskService/main catch→共享filter→固定文案；真实Electron待隔离 | 最终字节已统一绑定；P2-S1与root嵌套guard P2定点关闭，真实listener隔离探针通过；真实IPC/native仍待隔离门。 |
| 1旧task-runtime测试 / T01唯一临时窗口 | 测试自持真实child、完整同版wire匹配与半帧为零、原SIGKILL/exit73/offline/恢复与持久证据 | 授权r2实际字节一致；原8项/期限/断言保留，主线39TS实际通过；窗口关闭及后续owner仍由根另定。 |

本轮提前发出的两项有源码依据的实施风险提醒，均不是已证明的新代码缺陷：

1. 旧 `tests/unit/task-service.test.ts:21` fake及`task-runtime.test.ts:162–210/341–348` transport只实现旧TaskEngine接口，且async wrapper会更换promise。新增接口不能以改旧tests或按shape重授startup来兼容；应保留严格legacy2兼容范围，真实business3必须走实际Supervisor opaque API。新专属测试需真实Supervisor→TaskService原promise正例及错promise/包装分支不晋升。
2. 旧Coordinator.ServiceFault构造立即legacy safe_error，单独在classify末尾换3 formatter会丢失原[3]版本诊断。已通知Python作者，其回执将保留受控原code/params，默认.error维持legacy兼容，business3分类从原受控值构造，不复用已吞值的legacy投影；实际实现/反例待read-ready核对。

上述两项保留为实施期协作记录，后文记载其实际实现与验证。以下按原发生顺序保留初组、修前失败及各版本关闭，不回写旧输入；最终代码意见以上述固定候选为准。

## canonical 分组初次 read-ready 增量

本组是作者声明read-ready后的初次实现阅读，**不是整阶段冻结或通过**。8条canonical产品开始/结束hash一致，且与作者逐项回执相符：

| 路径 | 初组 SHA256 |
| --- | --- |
| packages/contracts/v2/schema.json | a4850496c250103ea260558d23d4a75e8ba0e514b943e7c34fa34f2985b1a375 |
| packages/contracts/v2/errors.json | ad242d93ced7a0c8a463b708b7a1f3105e65f03c3980e0a0c6c4309f8c26544c |
| packages/contracts/v2/registry.json | 363df6234f9b87f6512017d52e1d10ed6babc512e7fb5c7f2b150513c9f5d239 |
| packages/contracts/v2/fixtures.json | 4b17575ad643a916bcc6b7f51c88b0e8c7a179ef7951fc39d29b083a78b851a6 |
| packages/contracts/v2/binding-regressions.json | bf54ff5d65225ca88d7d3368aa0006bfbdb0b67ec294138c708fc6e69bf82dfa |
| packages/contracts/src/v2.ts | 2caea16b799e4af09ab74e27f84dad23da023d31ddf26b7ac2eb92c222a71073 |
| packages/contracts/src/index.ts | 621b9c42f53656108ff3a0b3787330ffbd242f43f6cf3f5692d98b60f3734463 |
| packages/contracts/python/contract_v2.py | b33c865454ee3f1155466e9b62fdcbf6f0dbe6edc739e0c8c314760c02261e96 |

`tests/unit/t01-startup-canonical.test.ts`全文初读hash为 `7c4edbc5ccf62637eea6c140b7a623c8ecaea79d385fd184016a30f58a4a5335`；随后作者通知仅补schema/catalog每分支完整params/key/retryable逐值断言，末读hash为 `e1cea6f92b4f917c86e4f7fce2167c0b1b7dc8ac311ab69208fa07069c511279`，不把前者称最终测试身份。profile状态此时仍validator-only，按作者说明待真实runtime接通后与两条已有专属测试同步；后续状态/hash刷新须另绑。

已核：新增$defs仅startupFailure/error_startup，严格五字段封套/四有限错误与授权相符；全部旧$defs、原sourceTable及旧errors/registry顶层值机器比较均不变。PROJECT_FORMAT_UNSUPPORTED没有进入普通codes/error2/error3/普通response；normal3错误构造对[3]版本诊断不用legacy safe_error。新增displayHealth/ProjectView/error展示union只供有限DTO，不选实际runtime；默认healthSchema/PROTOCOL_VERSION2/safeError保持。未发现本初分组新增阻断，尚未核完整真实producer或Session凭据链。

独立小型机制probe（未重复作者241TS/195Py或45新case矩阵）：用实际TS编译器在内存加载当前canonical/index及实际新JsonlReader，完整合法格式诊断逐**单字节chunk**送入：实际payload1024接受；同一JSON加CR实际1025拒绝；前加2000空格实际2291拒绝。metadata为frozen且计数准确；额外封套字段/假hash拒绝，普通2/3错误sanitize拒新格式码，display仅有限接受。Python子进程直接导入当前contract，四startup构造全等、normal3[3]保留、普通business3新格式码返回INTERNAL_ERROR。结果不证明supervisor的profile/prehello/once/raw来源认证已实现。

完整exec返回对象已emit，chunk `f208e0`，exit_code0、wall_time_seconds0.200055041；stdout完整包含上述三个计数/接受结果，errorIsolation=true、fakeHashAndExtraEnvelopeRejected=true，以及Python status0/signalnull/完整stdout/stderr空。Python没有运行engine或parser。该probe用到的reader末读hash为 `8426b2cc134cb2fed08667c87f0eb8a84a3544a13677197a1acddc7de00776c7`；不是最终desktop组冻结身份。

源码开始读回完整结果chunk `85d073`、旧区域机器比较 `2d81f6`、结束hash `f0d9d3` 均exit_code0。作者随后测试/状态变化与其他组WIP继续进行，最终候选须统一核hash；本轮不提前将整阶段或其他组标通过。

## desktop 与构造清理初组（尚未冻结）

初次 desktop 读回的7路径身份如下；未重复主线83项矩阵，以下不称最终候选：

| 路径 | 初读 SHA256 |
| --- | --- |
| apps/desktop/src/main/jsonl.ts | 8426b2cc134cb2fed08667c87f0eb8a84a3544a13677197a1acddc7de00776c7 |
| apps/desktop/src/main/engine.ts | 3896bd68d1f65ee0384a6687ec77b038d3f9058c2633df1715d64d059590dbee |
| apps/desktop/src/main/task-service.ts | 3daebc473d6811a6bf8bacc8378eb3da98f08af8e656a9acdd57a5cdc92fe6cb |
| apps/desktop/src/main/index.ts | 8578e7461d82bcde08bdaf115990630f3fae12ec1fd1bb8154c84132441e3bf1 |
| apps/desktop/src/renderer/src/task-presentation.ts | 45fc0f9195979be7d0b172d2500d1a96395156bc423dbc1299fcdaf6ce272fd2 |
| tests/unit/t01-startup-supervisor.test.ts | 60f7f0f68647642da1b2ec43dddba95adb6e7be022f1b6557016867060de1ab2 |
| tests/unit/t01-startup-presentation.test.ts | 4334b6ea52d85167c374bff1aa477b93fd5300df0bff5f95134b514dbe1a260d |

ES #字段及#内部方法承载Session/attempt/startupPromise/request外层operation和真实cause绑定；公开投影读取私有副本。TaskService实际Supervisor品牌选择3，旧mock/wrapper保持legacy2；call近端catch保存原promise，经#caught私有token传到guard；main health保留原operation。每listener实际交付clone先注册，后续普通clone/跨实例不登记。上述为源码与初组新测试阅读，没有实际运行Electron或IPC。

### P2-S1：business3通知错误Session未同步终止

初读engine.ts的#receive通知分支，在严格合法notification但prehello/错误engineSessionId时直接return，后续同chunk帧仍可分派。与计划§4.5/§4.6严格Session同步终态不符。已向主线发出具体分支及建议：business3条件内同步#finish(invalid())，legacy2保留原行为，并补同chunk后续不分派。主线已实际改入，修后read-ready SHA `6d55774068ca27a49958daeea9f4b1fa15614c95563ca28b8a768265ecd4365e`；待独立定点闭环与最终候选绑定。

独立探针失败原记录保留：exec `e77150` exit1因为探针child误把main追加profile也作JSON.parse，实际ENGINE_EXITED，**不是产品问题复现证据**。修正slice范围后exec `2b517d` exit1收到产品INVALID_REQUEST；此时源码已由主线修改（读回 `8e1ee4`），探针仍期待旧接受行为，故不能倒称修前机制复现成功或最终关闭。完整exec对象均已emit。后续报告追加的首写命令 `cc4719` exit1为报告工具脚本编码失败，未修改报告或产品；改用apply_patch。

其余连续读回 `319589`、`e69dc0`、`cbb829`、`17fc21`、`ef151a`、`e4a968`均exit0。主线更多测试仍在补强，后续单独绑定最终身份。

### Store / JobStore 父子清理初组

作者声明read-ready后，两路径diff全文及机制反例阅读，末hash与交接一致：storage.py `2f8762aef48279f5d2e05fa8e27015e04a911f4fdc0748586570d194ff090776`；job_store.py `541eececf30db5e2a0c6f60ca45e4ca10846c7d7cd3f29c5c2210c3a339ab30b`。

实际future-version两处改typed UnsupportedProjectFormat；配置target非法仍ValueError。Store构造内每close独立尝试后原raise；Job parent_ready只在父成功返回后转移db/format3资源，父失败不重复close，legacy lease仍由Job收尾。公开close尝试全部资源后抛首个cleanup异常。已核新机制测试逐close调用次序/父失败不重复/首因对象不变，不把注入机制称真实OS故障；此初组暂未发现新增阻断。Coordinator/CLI完整stdio仍待read-ready，不用此结论提前宣称整个ready门通过。

### P2-S1 修后定点关闭

主线声明该engine增量read-ready后，独立实际Node子进程向真实Supervisor发送：合法hello3；接着同一stdout chunk为严格合法3但错Session的job.progress通知、正确Session通知、原health成功响应。exec `ab02c8` exit_code0 / wall_time_seconds0.323181666，stdout记录engine源SHA仍为 `6d55774068ca27a49958daeea9f4b1fa15614c95563ca28b8a768265ecd4365e`；实际投影INVALID_REQUEST，事件严格为ready→disconnected，通知递送0、current Session已清。补丁同步terminal/reader.stop使同chunk后续帧不消费，当前修正版关闭P2-S1。不会把初读SHA或原两失败探针视为最终版本通过；完整冻结仍须再绑定。

## Python runtime 全组 read-ready 增量

4产品/2新增测试开始与末读身份与作者交接一致；完整exec `577a73`、`aef377`、`41d097`、`ff95e9`、`abbe91`均exit0。storage/job_store身份沿上节，另四条如下：

| 路径 | SHA256 |
| --- | --- |
| packages/engine/src/ontolearn_engine/coordinator.py | 06e18bef3847ac3aa08e3bcf64dee865ec1a2631908b0b3a5973f4d050095d98 |
| packages/engine/src/ontolearn_engine/__main__.py | dae8f978a8cadc22dcc9f57b1e8a5e46cc760636192e45a2822aa47ab13b4684 |
| packages/engine/tests/test_project_startup_contract.py | b977e5be1ff1ba5f2afc76eedc71559703b1d485a1c0910bb0bf956c8288f421 |
| packages/engine/tests/test_project_startup_stdio.py | f42126f2e3f854a8aeb1e23759d47bcdca0cb20265dc856a1439be2a185cfd0c |

已核真实serve先Store/Job3构造与validate，再reconcile，随后allowed/Coordinator/信号和reader线程，最后接受hello。成功bootstrap仍外层2/selected3，正式request/response/notification按实例profile3校验，重复hello或错版本/Session在本连接同步结束；worker内部协议保持2。ServiceFault保留内部code/params，普通3分类从其原值构造，解决提前legacy投影吞掉[3]风险。默认2构造/启动仍未翻转；裸Store3或缺私有ready门无法构造3 Coordinator。

CLI只从有限显式argv取profile/绝对backup，资源未加载不发可信hash诊断。初始化逐资源独立清理后通过StartupInitializationFailure保留第一cause，main只据typed actual format/有限SQLite及Format3Fault分类；不解析异常文本，主动取消/正常退出不捏造格式错，ready后失败不回到startup。最终producer对实际将写bytes核预算，完整write+flush，写失败不伪称成功。新测试清楚区分真实SQLite/CLI、受控机制注入和OS故障；作者77项为作者证据，本审未重复其矩阵。

独立真实CLI小探针exec `c9d6f7` exit_code0 / wall_time_seconds0.038051333：临时真实SQLite设user_version=2147483647，显式business3真实子进程实际退出1，stdout单行完整291B格式诊断、stderr空、hash与资源相同；原版本值不变。子进程后直接重开得到UnsupportedProjectFormat而非busy，验证其自有lease释放。stdout原完整封套与进程状态已emit；未运行GUI或产品窗口，不把此单例称完整故障矩阵。

该Python分组未发现新增阻断。仍待完整候选冻结、最终canonical状态/hash、desktop补强测试及整个交叉链路审查；本报告保持进行中，不代指定双模型/CI/远端/隔离native门。

## 最终冻结前补核：来源隔离、真实恢复与同源状态

desktop末读 `fd637b` 与 `b0ba2d` 均exit0：5产品与P2-S1修后身份一致；presentation测试仍4334…260d；supervisor测试扩充为 `54abbe1737c5e2f83ca53d1a0fd1d6eb550c18080492bb4781792b65b340a2d5`。新增反例包括无hello pending的受控数据/EOF/close、项目在原promise catch前切换、真实3原子Job通知/结果/operation精确重试/单claim/revision+1，以及只对本测试刚启动的Coordinator PID发SIGTERM，实际签发listener clone→TaskService恢复到新Session且旧Job不重写。已核测试确实要求订阅时queued/running与真实事件，workMs500明确为调度控制，没有删减原断言。作者曾有Job零事件首失败，主线保留原日志，本审不覆盖该历史或重复其30项矩阵。

独立追加来源隔离小探针 `302fbc` exit_code0 / wall_time_seconds0.61812325：真实无窗口Node子进程ready后发非法startup记录触发正常断开。首个实际listener篡改其交付对象的state/generation/session/error并抛错，第二listener仍收到独立原始INVALID_REQUEST断开值；两实际交付对象均可从私有记录提取相同原Session/generation1/错误。普通structuredClone、跨Supervisor事件和公开EngineError构造均拒绝晋升。完整stdout含最终registryHash2718…ff9fa及实际投影，不依赖公开标签或当前profile；没有运行完整测试矩阵。

最终canonical状态增量实际读回 `1a9abb` exit0，与作者交接完全一致：

| 路径 | 最终增量 SHA256 |
| --- | --- |
| packages/contracts/v2/registry.json | 271800b8f3ca3946b71d9ca07da24c251a0842f66bf6f806b96ac1b1767ff9fa |
| packages/contracts/v2/fixtures.json | 848f08c1f02a98bb269e5b4114f7906db32ea3615eaea65c3ee1c0a4a8d54503 |
| packages/contracts/v2/binding-regressions.json | 8b6556d163a4c08c954bc3972fbb666b5ba3843110566a24e6183a0ce8f41f76 |
| tests/unit/t01-business3-contract.test.ts | ad3a0177523aed860d0f2cd72ae2296af9b6e6ad9dfe297240387615ce1901d7 |
| packages/engine/tests/test_project_business3_contract.py | d7c75036fc81ae7a380ccc0da1a5896fb2a4a1be66938e2431bccf85a14625ed |

其余canonical 5产品及新增canonical测试仍上文末读身份。实际两旧测试只同步profile状态与标题，不放宽旧2预期。状态是explicit-internal-opt-in-default2；sourceTable及旧fixture其他顶层值保持。registry实际完整bytes hash用于同源golden和startup/binding，不混用初组363d…d239；更早独立探针按其当时候选保存，不追写为新hash通过。作者最终241TS/195Py为作者证据，本审未重复矩阵。

只读必要共享链路 `06e16e` exit0；preload/App读取 `e7ba18`、`796c97`中末尾rg无匹配故exec exit1，读取内容正常、不是测试/产品失败：preload原有限命名bridge和isTaskUpdate过滤复用共享有限DTO，App实际health/error入口调用固定explainError，没有新runtime选择或通用invoke。本审没有修改I06余四路径或运行Electron；真实IPC/native链仍待隔离环境，不以静态阅读替代。

当前新增待收证的精确清理点：serve停止时stopped.set是reader停止请求，read线程可能仍阻塞os.read，reader.stop只在其finally发生；不能将serve返回/进程退出等同线程已settled。仅未join不是自动P2，也不应关闭用户stdin、无限等待或跨线程直接操作reader.buffer。已建议作者按批准计划最小记录实际start成功/stop请求/有界观察未settled状态并给机制证据；是否需要实现delta待其回执，暂不扩为新功能。

### reader 状态证据收口

作者read-ready最小增量实际开始与末读一致，exec `c50a2d`、`fe707a`均exit0：coordinator `fbedf4bd10ec4eef0c3c4154eedb8cce5903498a46e8ffa3201dea245b18f23c`，新增contract测试 `9138aa334445445311220928d62e5ba33a6dc70a3ea7f5d7b9bfe31e4232edb6`，取代本报告前次06e1…5d98/b977…f421。main只置stopRequested并以is_alive有限观察，原owner读线程独占reader.stop；内部记录thread创建/start尝试/成功、reader创建/stop尝试/实际停止及threadFinished，保守settled。start失败可通过实际ident补观察，观察异常明确记录未知而非已停；不join、不关闭stdin、不跨线程清reader buffer、不新增parser。内部返回dict或初始化carrier快照不进入wire/Job/receipt。可能仍阻塞的daemon明确保持未settled，不把正常进程边界转写成资源释放证明。

独立只运行新增定点 `test_started_blocked_reader_is_requested_not_falsely_settled`，完整exec `8b6f90` exit_code0 / wall_time_seconds0.382632417，实际1 passed in0.27s。真实daemon线程调用测试受控阻塞read：serve返回时线程alive、stop已请求但reader尚未stop且settled=false；测试只释放自己的伪read后，owner线程执行EOF/stop并结束；原快照保持较早未停状态。它是线程机制证据，不是对真实用户stdin或OS故障的模拟成功。未重复52/77矩阵。作者52项日志实际SHA `0d508c3131ab2532e2c9e07ad1a9fed2de628eea329e6fb5b63fcca5d17c3c84`，stdio因serve变化由作者另重验。

该精确状态收证点已关闭，当前独立代码审查未发现新的实质阻断，支持主线继续全仓check与unsigned打包验证。desktop supervisor测试随后只因lint prefer-const改为const recoverySession对象，末读SHA `94468b409057add8c120278c506dbea011f5a3292b53f647ce7d6c0ac60c158c`；产品5路径不变。最终统一候选身份、stdio终态及全仓/包结果仍须另绑，不能把旧77/30日志自动算在新候选，也不能由本结论代替指定双模型/CI/远端或隔离native验收。

## 未应用旧测试迁移补丁的独立范围核对

全仓首跑由主线实际报告：lint/format/type通过，1024TS通过、3旧task-runtime测试因反射internal.session.pending失败，后续build/Python未运行；不登记全仓通过。ES #private为必要生产边界，不通过重新开放Session修测试。根正在协调唯一旧测试写权，本审只读申请补丁，不应用、不运行未授权旧测试。

实际全文读取 `7c3802` exit0：原文件SHA `2f8f8c1fd34cc449b2cca6ff2a05dcbed43b47560f97fcc039810233f2dfee50`；申请补丁 `cba8eaf5ee10753e1ed0e9c0df3256d9452ff08934ff185226a1d6e7825e5baa`；说明 `55eba07c181d6b51bd8a96bec51583784b5964c88c6acb91705c65d3b16985f7`。读原断言及git apply --check完整exec `7df561` exit0，后者只核补丁可应用，没有写文件。

保持的真实语义：包装实际actual.spawn并保留真实OS child；故障重启仍真实Python退出73；旧child仍SIGKILL且等close；PID/session换代、恢复2次/失败3次累计4/手动成功累计5次真实spawn、rounds[1]、原子成功Job不降级/receipt revision1、operation.get恢复、无job.create/cancel重放、唯一Job/claim、恢复view绑定均保留。独立内存应用补丁 `e5cfe4` exit0确认原8个测试名完全相同，8项20秒期限全部不变，无skip；虚拟候选SHA `5449f3df49b9078c5e2cf1cc78c669d78043d1cae1ef63d9d5df66bf3a8c551f`。原文件末读仍原SHA，无测试运行或生产API变动。作者CompilerHost类型检查是静态证据，不能当8项运行通过。

精确观测边界已反馈主线：新Set证明wire中写出的请求ID得到完整JSON响应，并不直接读取ES内部pending Map。当前仅按response同id删除，尚未核schema/method/session；且reader未end，framingFailed=false不排除残留半帧，缺LF的尚未登记ID也可能令Set为空。建议最小增强为保存真实request并验证匹配合法response才删除，kill前同时断言两方向bufferedBytes为0。这是测试观测强度说明，非已复现生产错误；不因root尚未授权而自行修改旧测试。修订补丁及批准后的真实8项结果待另绑。

### 旧测试r2授权及实际应用读回

安全边界实际全文读取root唯一窗口授权与effective JSON，完整exec `3035fc` exit0：授权SHA `6764ab1fd75458dce7cbe9c7fdd3edea9825b91ae6997fceac8f42801949eb14`，JSON `a29d2f34ee2c5ed4d78b6c77c0303b39939450eb9eeaf8688452a749f2367fe5`。仅T01临时writer，I05只读，非永久移交；待根核实际冻结HEAD/SHA/diff/8项及必要全check终态后另定关闭/后续owner。本审不登记窗口关闭，不改旧测试或外推其他旧路径；实际阶段范围随此精确授权为17产品/8测试。

主线实际应用的r2补丁SHA `ef49df07c0798a9946cc17e38e9018b29d8d49cfdb351baa4f36d034637b68bc`，原旧测试末读SHA `5a190b3ccde080b3e5b1059e2da944d56397d04e53b1a659c1bbdbeb4ae5ec99`，与授权内存预计一致。只读exec `fbb6ce`、`79895f`均exit0：真实request先validateV2，保存完整request；response须matchesResponse完整绑定才删除；杀进程前新增双reader.bufferedBytes之和0。先前r1观测不足已关闭，不再称直接证明ES私有Map本体；本8项仍是默认2，不推广作显式3证明。原8项及新增desktop两文件39TS通过为主线实际session45685/chunk564884证据，本审未重复39项。

## root P2：嵌套guard丢失已认证business3错误

根独立指出并由主线真实复现：受控真实Coordinator的job.get抛VERSION_INCOMPATIBLE/[3]，走合法同版响应与原Supervisor pending；doSubscribe.guard已提取合法3错误，但restoreJobs重建公开{error}，restoreOnce.guard再以默认safeError处理，最终错误地降为INTERNAL_ERROR。修前实际session48888/chunk6cdf6b exit1。原日志已全文读取，SHA `b5396517f3ba5c9f9a2313dc9ce2e20df60247badbb8a7a462cfc43d34e46f27`；修前精确两输入ZIP SHA `ed7543875935ef673a3edcc5640db29455522f007016ec8da4b05402def376e2`，不把该失败改写成仅静态提醒或修后通过。

修后TaskService SHA `4a14a1171e2562c4b61f3ad48484d2e1ffec22ce41865023b876440efb829b70`；supervisor测试SHA `1a6090196479d1bb25be0f4c522c9953a8a1c2a6cc6c7d77cfc2cf195458ce61`。开始/末读完整exec `859e2c`、`6a0ea2`、`fbb6ce`、`756638`一致：#caught保存私有投影+原项目/代次；guard返回实际promise，并仅为真正auth结果在#outcomes绑定原promise。subscribe的finally只内部link其实际wrapper promise，回调登记先于调用方await继续；restoreJobs必须原结果对象+已登记promise+当前项目/代次，才转成私有token。公开DTO/结构clone/原结果配新promise不重新授予来源，私有投影也不读取被改写的公开error字段。其他17产品身份不因该补丁外推变化，旧包不得替新TaskService验证。

独立仅运行新nested机制用例，完整exec `76a579` exit_code0 / wall_time_seconds0.996006833：1 passed、19因-t筛选未运行（非产品skip），实际真实Python→合法3响应→原Supervisor pending→嵌套两guard保留完整VERSION_INCOMPATIBLE/[3]；相同用例还验证clone公开结果与原结果配新promise均INTERNAL_ERROR。不重复39项或全仓矩阵。此固定修正版关闭root P2，未发现新增来源晋升问题；最终全仓/重新打包、统一身份及指定双审等门仍未由本定点代替。

### 原r3转义预算证据pair补齐

canonical作者仅补原raw13后两条完整raw及新增专属断言；实际读回 `93f9bd` exit0，fixtures新SHA `ba4d6aa6757c8ba0cf95aef11fdb653a1cb30a1d4b75ea32697a11324c6bb8ae`，newcanonical TS `68f89588117dbbc438e0f99287b4937a55cce19cf35e6506194e5d9be077905a`，registry仍2718…ff9fa，其余产品不变。新增两条各140个实际\\uXXXX与4个chunk；compact值291B，两条解码完整值均等原格式诊断golden。实际payload分别1024/1025，原长接受/拒绝，补齐同decoded不同escaped byte预算，不替换原13raw。Python交叉断言也独立decode全部raw并计140转义。作者首个全转义生成1426越预算的assert失败仍保留，不虚称首稿通过。

独立机制probe首exec `23d0aa` exit1：两个raw计数/预算结果已符合预期，但本审Node assert.deepStrictEqual额外比较了严格reader的null prototype与JSON.parse普通对象原型；这不是JSON值或产品错误。随后仅改完整JSON值比较口径，实际exec `f3a247` exit_code0 / wall_time_seconds0.222029334，两个完整golden等值、4chunk/140转义、1024 true/1025 false全部通过。首失败完整对象保留，不删改、不作为产品失败或倒称成功。未重复作者243TS矩阵。

## 最终运行原件与固定候选绑定

最终25源码/测试仍与manifest/ZIP逐字节一致，独立末验exec `d01ecc` exit0；没有因验证后修改产品而沿用旧结果。本报告只写自身并格式化，不修改受审实现、测试或其他报告；最终候选身份始终为本页开头6ef218…c5b4 / d39278…e86a。

最终主线终态与本审实际全文原件读回分别登记：

| 事项 | 原执行终态（主线提供） | 本审读回的原件及实际范围 |
| --- | --- | --- |
| npm run check | session20694 / chunk1a3ca0 / exit0 | `/tmp/t01-startup-fullcheck-final.log`，8029B，SHA `f33b8aba4a42afa4e0d9eb12d354bcdeebfdd0c4f1d918d9cb24d9d4c460cf24`。lint/format/三层TS类型/build/ruff通过；20个TS文件1030项通过；2750Py收集，2706通过、44原有skip。旧迁移8项包含于TS全集，新52机制/26stdio包含于Py全集。 |
| npm run package:dir | session95246 / chunk80910e / exit0 | `/tmp/t01-startup-package-final.log`，14324B，SHA `b1fac97983ca7f34a5694c73e5833bf94cfc6d469fb71471a4dd3d9c779ca184`。重新build+PyInstaller+electron-builder --dir --publish never，Darwin arm64；identity明确null，跳过macOS代码签名，不算签名/公证/发布。 |
| 实际包引擎harness | session63701 / chunk2a9c3b / exit0 | `/tmp/t01-startup-packaged-probe-final.json`，58234B，SHA `2dbb6ccd116c769852853b2424aa843e5497c4abfe539fac70ef994643265e5f`。5个实际引擎session、9资源manifest与完整stdin/stdout/stderr base64；没有执行Electron/desktop。 |
| 静态asar/资源/registry AST | chunkfdfdb9 / exit0 | `/tmp/t01-startup-package-resource-bindings-final.json`，1950B，SHA `0e275620f8cd69a3cdf0cb084f120c9f578278003c2a070f8280b0a436ff2124`。actualmain388655B，SHA `46e6b7908b29dc71b20f6c0e25081285ce258f3ba0c41983202413092a06b9f3`；仅静态数据AST与资源相等，不执行bundle/handler。 |

本审不是重新运行上述完整命令：独立读回完整exec `ded4b8`、`387c4f`、`23c244`、`03bd23`、`d01ecc`均exit0，明确区别其read命令退出0与原执行session/chunk。第一完整check中旧反射失败和后来fullcheck-fixed仅说明文档Prettier失败均为保留历史；最终全check才覆盖此25路径，不把文档格式错误称产品失效或删除首失败。

包引擎原始记录逐条独立decode并核bytes/SHA、严格envelope及每条原请求绑定：legacy2-health为hello/health两响应，selected2；business3-health同为两响应，selected3；future-format唯一291B startupFailure、code PROJECT_FORMAT_UNSUPPORTED、退出1/stderr0；真实包Coordinator+worker原子session有13个严格响应及5通知（含succeeded），退出0；重开有hello/operation.get/job.create三响应、退出0。所有成功session请求均配对、stderr0；三个create响应绑定原同一Job/operation，重开operation.projectRevision1，真实projectRevision由0至1，记录claims1。原始记录的成功状态没有被连接失败覆盖，不以重开重放新操作。

实际packaged executable SHA `e815d4aa7ee6fce29aba4f18531bc07bac6392fcf45895c9943cdeaed923df25`已独立读当前文件与build副本核同字节；其manifest九资源（含Python helper）与当前canonical对应hash相同，registry2718…ff9fa、新fixtures ba4d…b8ae保持。独立读取包两处8份JSON资源与canonical逐字节相等，helper/uv.lock亦等；实际asar抽取main与out/main完全相等。原AST脚本已全文只读检查：只解析有限数据literal并完整比较registry值，不eval bundle；没有重复运行该脚本或启动任何Electron handler。

上述证据足以支持本内部阶段固定候选的独立审查结论，尚未证明真实Electron IPC、窗口/焦点/无响应/native平台或签名发布；不替代指定双模型、CI、PR、正常develop合并与远端核验。旧测试临时窗口仍须root回交核验并明确登记关闭/后续owner，本审不自行关闭；metadata/draft持久化、来源授权接线、learning、完整产品恢复及父FR全功能验收仍按原范围推进，不由本startup子阶段判完成。
