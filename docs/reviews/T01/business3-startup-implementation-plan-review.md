# T01 business3/startup 实施计划独立只读复核

结论：**修订计划已覆盖本轮具体路径和认证/清理缺口，未发现仍阻断提交审批的实质问题；支持 root 审批该精确阶段范围。** 本报告不是实施授权、实现验收或 root 并行预审通过记录，不代 root 关闭其 P1/P2。startup/schema/新码/runtime3-ready 仍须 root 明确授权后实施；原 r1–r3 已关闭设计不因本轮计划重审。

## 固定输入与实际边界

- 工作树 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`；实际 HEAD `27a0d17149ffdaf013233b4ac7fc861ccb0e38c2`。产品来源为纯材料提交 `bf04169d400378084e8fea87b6a8e3915135987d`，过程补证不变更其产品；本轮末读 engine/contracts/desktop 源码差异清单为空。
- 首次实际全文读计划稿 SHA256 `8893137b342c93caeb686b838a1cd8de057e46c1c2bc626c7c5b4e9887ac5140`；彼时16产品/5新增测试加2已有专属测试。该稿属于本次补充前历史输入，不作为最终可审批稿。
- 作者修订最终计划 `docs/iterations/T01/business3-startup-implementation-plan.md` **全文实际读取**，开始/结束 SHA256 为 `e9999d37a034fc365b8c5a345c3c135220e13c78b4f4907a763d81351d846b07`。本文按此稿的17产品/7测试范围判断。
- common `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` 及四文件生效记录已在前安全点全文实际接收；生效仅 future maintenance，`startupImplementationAuthorized:false`，无桌面约束不变。
- 只读当前实际 Store/JobStore构造、Coordinator request/serve/worker通道、Python main、canonical/index、supervisor/reader、task-service、main factory/catch、共享DTO过滤、preload/App与explainError的必要位置。未读或消费他线未批准实现。
- 本轮只新增本报告；未修改计划、产品、测试、旧报告、status或总控文件，未格式化其他文件、提交或运行产品/测试/GUI/Electron/e2e/native/HMR。

## 1. 必要路径与最小范围

17条产品路径均在已生效的T01责任内，角色与当前真实切点对应；数量增加来自原构造内部无法由serve替代的cleanup，不是扩张Job业务：

| 必要路径组 | 实际依据与计划用途 | 范围判断 |
| --- | --- | --- |
| contracts/v2/{schema,errors,registry,fixtures,binding-regressions}.json（5） | 独立startup schema/error、四有限分支/实际raw golden、同源registry状态及profile绑定反例 | 新格式码不进入普通codes/error2/error3；不增方法/能力；原2预期保留。 |
| contracts/src/{v2,index}.ts、contracts/python/contract_v2.py（3） | 严格独立helper、普通business3错误构造、展示DTO和有限sanitizer | 原默认validate/safeError/PROTOCOL_VERSION2保持；display union不用于实际选版。 |
| engine/{storage,job_store,coordinator,__main__}.py（4） | typed版本检查、父子构造cleanup、两层真实ready/reconcile、同版请求/错误/通知、最终stdout producer | 不改SQL/schema/commit/claim/D7；不因前门3改worker内部通道；resources不转。 |
| desktop main/{jsonl,engine,task-service,index}.ts（4） | 原reader长度metadata、私有profile/expectedHash/deferred/credential、各catch/connection/recovery门及可信工厂 | 不另造parser或generic IPC；sender/mainFrame/可信文档约束保留。 |
| renderer/src/task-presentation.ts（1） | 最后默认safeError门与固定文案 | 只允许已批准有限展示值，不显示原异常/路径/实际format。 |

上表前缀分别为 `packages/`、`packages/engine/src/ontolearn_engine/`、`apps/desktop/src/`，完整17路径已在计划§2逐条列出。本轮核四新生效路径及engine.ts实际SHA均与计划§1相符。`contracts/package.json`的`./v2`确实指向已有design-v2.ts，后者实际`export * from './v2'`，无需改出口文件。

精确测试为5新增（Python startup_contract/startup_stdio，TS startup_canonical/startup_supervisor/startup_presentation），另同步2份已有T01 business3专属测试的runtime profile状态断言；不是修改历史通用测试预期。I06保留的preload/index.ts与renderer env.d.ts/App.tsx/style.css不施工；可只读核实际过滤/展示与类型重建，确需改动再精确交接。protocol/resources/worker语义/build/entrypoint/锁/CI和project/format3.py未被默许改动。

## 2. 本轮具体补充与闭环核对

| 项目 | 当前实际触发/原稿不足 | 最终稿具体处置与独立判断 |
| --- | --- | --- |
| 根预审：JobStore构造清理 | JobStore.__init__ except连续db.close/format3 lease/legacy lease；第一个cleanup失败可改首因并跳后续，serve没有构造成功对象可补救 | §2第17路径及§4明确父构造前/后所有权，独立尝试各cleanup并保原typed首因；§7要求逐close故障、父失败/父成功子失败及不重复清理。已覆盖计划缺口，不代root变更其P1状态。 |
| 独立补充：Store内层先因覆盖 | Store.__init__ except也先db.close再lease.close。若先有UnsupportedProjectFormat而db.close再抛，进入JobStore之前首因就可能丢失；只修外层不够 | §2 storage条目和§4同步固定Store在成功返回前负责资源、失败逐项尝试/重抛原typed首因，成功才移交，父失败不凭遗留引用重复cleanup；新测试包含Store内层。设计层已覆盖，无需新增第18路径。 |
| 根预审：原attempt错误来源 | 当前EngineError是可公开构造对象，捕获时supervisor可能已换代；仅instanceof、当前profile/generation或形状不能认证原startup | §6私有WeakMap记录原Session/attempt/profile/preHello/startupPromise/requestPromise/operation与冻结安全错误；projectFailure必须同时接实际caught对象及内部登记的原调用promise。旧attempt可向原调用者返回原首错，但不更新新连接；clone/tag/公开类/跨实例/错误promise拒升级。已覆盖计划缺口，不代root变更其P2状态。 |
| 独立补充：逐listener clone会丢凭据 | engine.connectionState当前调用listener(structuredClone(state))；若只登记原state，真实TaskService收到clone后不能查原WeakMap | §6选择唯一每个交付clone由所属Supervisor先内部登记同原Session/attempt再交listener，保留逐listener隔离；projectConnectionFailure从冻结私有记录返回原generation/session用于fence，普通再次clone和跨实例不得补认证；§7真实交付链反例明确。设计层已覆盖。 |

上述均为真实代码支持的必要实施补充，首次发现已及时发主线。最终§10如实列作者处置且写明待root复核，没有将本报告或作者修稿变成根预审通过。

## 3. 启动身份、producer与错误全链路

**受信入口**：计划§3仅未打包main内部显式flag选择business3，默认legacy2；engine argv由该私有options签发，不从renderer/generic IPC/继承env/child自报选择。DB和allowedProjects沿现可信工厂；backup是同DB目录随机全新绝对目标，Store同lease决定是否需一致备份；main不先开PRAGMA或删除旧备份。实际entrypoint正常分支确实转发__main__.main，计划不需改该未交文件。

**expectedHash**：当前supervisor实际在spawn前读本地registry原bytes、严格解析并对照编译registry后SHA256；开发/包内路径与计划一致。新profile继续使用该可信起点，资源读失败不spawn。Python已从同资源加载CONTRACT/REGISTRY_HASH/完整锁，不能在resources导入失败时伪造合格startup。计划明确registry hash不替代schema/errors/helper/锁的完整包内资源验证。

**ready与普通错误**：Store3→JobStore3→真实reconcile_jobs→权限/limits/profile→成功hello的顺序明确；后续真实request/response/notification/result按固定profile严格校验，不将2/3作宽松OR。当前resources.safe_error确实仅校验error2；§2/§5用独立canonical startup_error构造新启动错误，business3_error处理普通3错误（特别[3]版本诊断），不改未交resources或默认2。Job/derived wholeimplementation/D7无新例外，health不把私有CAS或test Job标成新能力。

**typed与cleanup**：仅实际不支持user_version检查产生UnsupportedProjectFormat；leaseBusy/SQLite primary忙、有限存储错误、受控结构失败与普通配置/OSError分开。四有限投影、未知原因fallback、默认2无新格式码明确。serve从首个自有资源起登记清理，构造各自保首因，信号/reader/worker/store/temp的cleanup独立尝试，不把“已尝试”说成settled；最终实际bytes核1024、单LF/flush/非零退出，失败不泄漏异常文本。

**raw与首错**：原JsonlReader确实在去CR/清零后只交decoded值，增加同一reader来源的原payloadByteLength是必要最小变更。计划计LF外、去CR前/空白/转义/跨chunk实际累计，通用帧限不降1024、不加第二parser。Session deferred/expectedHash/profile/once必须在数据callback前就绪；合格或非法诊断同步terminal/stop/reject/清timer/终止，自有EOF/close/timeout不覆盖首错，同chunk后续不分派；ready后诊断不是startup。这沿用已关r3，未重开新设计。

**全部展示门**：实际TaskService的call/receive/connectionChanged、guard、recover、connectionUpdate，以及main/index health catch、共享taskUpdateSchema/preload isTaskUpdate和最后explainError各门均已对照。新计划逐个区分原错误凭据提取与有限展示副本；不先解包丢原promise，不从公开投影重授startup来源。真实App直接接已批准BridgeResult，explainError默认safeError门需改，I06四路径不机械扩权。最终固定格式文案和有限params不暴露实际format/path/异常，也不授权自动重放写入。

## 4. 最小验证及待验边界

计划§7已要求真实SQLite/Python CLI、Node监督真实子进程、四App/Engine组合、旧2保留/显式3成功/不兼容安全终止、实际project.get3、原Job/operation重试与恢复；producer raw golden保存完整stdout/stderr/returncode、完整库/PRAGMA/receipt/lease；真实故障与人为注入分别记录。专属反例含清理首因/所有权、假hash、错误profile/session、raw1023/1024/1025/2000spaces/转义/CRLF、同chunk、无pending、旧attempt与错误originatingPromise、逐listener真实clone及伪clone等，与新实现风险匹配。

main/index顶层导入Electron，计划不在本机执行它；将必要profile工厂/health投影保持最小可测调用，结合源码接线、共享真实helper、类型/构建只算无窗口机制证据，**不是实际Electron handler、IPC/sender或页面验收**。unsigned包内引擎CLI与资源manifest可无窗口运行，但不启动desktop产物；包内身份、Windows/macOS、原生可见/焦点/凭据/崩溃与最终UI仍按原门在隔离环境补齐。不用mock/隐藏窗口/禁hang monitor冒充原生通过。

本轮没有运行上述命令或审批新增生产故障后门；§7明确故障注入仅新专属受信harness，旧通用测试可只读执行不能改预期。§9列出的独立新码/helper/profile/backup/17+7精确范围及证据边界须由root接受；任何计划外阻断再追加精确审批。指定双模型全新同版独立审查、必要验收、CI、正常PR/合并/远端和父P0/发布门完整保留。

最终判断限于：**该修订计划可提交精确阶段审批，尚无新的实施授权或运行通过结论。** 后续代码审查须核上述所有权和不透明凭据确实实现，不能因本计划文档闭环而省略真实异常/旧attempt/全链路验证。
