# I06 正式采用批准格式3：消费接口与集成请求

2026-10-21。仅有界设计请求，未改产品/契约/测试，未运行平台；不采用 T01 未批准实现，不把内部 Store-ready 或协议提案当正式通过。I06 消费源码固定 `e2c269ad78a78e1a042cadc93b1c81a874707153`，批准依赖仍为 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本次不重复 e2c 已完成回归或旧矩阵；未来正式格式3集成须针对实际批准候选重新界定必要验证。

已全文读取共同指南，实核 SHA-256 `b24c4c88404f422c5fae4bf6c01e231b678e46741250801e8100cc62a31fec39`；文首 db1 为初始快照，当前操作规则按新增权限节及根 AGENTS `78df2825…a759` 执行。旧冻结输入/hash原样保留。T01独占 storage.py、Python4、canonical7+main/engine.ts；T03独占构建4，均停止未来争写。I06原14仅余 main/index.ts、task-service.ts、preload/index.ts、renderer/env.d.ts、App.tsx、style.css 六文件；私有网关文件的后续改动仍须在本线原责任内按实际必要性提出。本文不扩大 tests/CI/resources 或外审权限。

## 1. 已读依据与证据归属

| 依据                                                                                 | 本次使用范围                                                                                                                                                                         |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| e2c `apps/desktop/src/main/task-service.ts`                                          | TaskEngine只读调用/事件接口，selectProject/projectContext，view generation、项目revision观察与重连                                                                                   |
| e2c `main/index.ts`、`model-gateway/model-service.ts`、`gateway-application.ts`      | main生命周期、项目回调、context生成/关闭、pending/来源关闭及既有私有配置边界                                                                                                         |
| e2c `model-gateway/stored-result-source.ts`、`main/engine.ts`                        | 严格共享校验、完整结果读取/同session复核，bootstrap/hash/ready处理；engine.ts今后由T01维护，本文只读                                                                                 |
| e2c `renderer/App.tsx`、`task-presentation.ts`、preload/index.ts、contracts/index.ts | UI查询/显示和具名桥的现有消费边界；不因读取取得额外修改权                                                                                                                            |
| T01 `format3-foundation-contract.md`                                                 | SHA `d435f2340ddda8d77e1f74c9291a7de64dfcac2fba1ba2d3834c6e24498c9855`：域/应用CAS分离、两层ready、checkpoint及业务3建议                                                             |
| T01 `format3-stage-a-contract.md`                                                    | SHA `46eaf700422dc339bd2e2754efa3ede8bdde4abef785570743534590ddbfefb0`：内部候选仍默认2/显式3、Store-ready不等于Job-ready/公共可用                                                   |
| T01 `interface-handoff.md`、`internal-service-contract.md`                           | SHA分别 `a06920c7450567ca0ab16203ce04aacb2e7ec9c8f9423347bc79d50c47eb64b8`、`f1035ee0f0edfd98c014ddee95cfd437b9279220c9c5ba2f1e5fa47f08a04e7b`；只识别提案范围，不直接调用内部SQL/类 |

T01文档中的早期“待交接”文字保留其生成时身份，当前文件责任由共同指南/实际生效交接覆盖。读取文档不表示采纳其中未批准实现或从内部类推导新RPC。I05真实语义、T10真实export/排除/保存边界由根的另行请求负责，本文不重复 X1–X6，也不替其验收。

## 2. 现有只读消费可满足的部分

| 现有接口/消费点                                                                              | 可以继续的条件                                                                                                | 实际差异或最小请求 / owner                                                                                                                                                                                               |
| -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `EngineSupervisor.request(method,params)`、engineSessionId、onNotification/onConnectionState | 保留受信main内部接口及原参数/结果语义，业务3封装由唯一engine实现处理                                          | **T01**交付同版bootstrap/业务3发送和匹配、真实hash/ready、失败诊断；I06不在TaskService手工改外层version或复制协议                                                                                                        |
| `project.get` → ProjectView                                                                  | projectId/projectRevision/inputSnapshotId/dependencyVector仍为原领域含义，仅实际formatVersion=3               | **T01**提供严格Project3类型/运行校验/完整fixture；metadataVersion、draft generation、operationSequence不能塞进域revision/vector/hash。TaskService/StoredResultSource没有自行写死formatVersion=2，可复用动态canonical校验 |
| TaskService.activeProject/restoreTasks                                                       | 同项目权限、订阅和真实project.get重读，原job/result身份与恢复合同不变                                         | **I06/T01交界**：普通view刷新和引擎重连仍按现有只读恢复；受控DB/协议迁移的生命周期另见第3节，不将renderer generation当授权寿命                                                                                           |
| `job.get`、`result.get`、`result.page`                                                       | 保留当前请求参数、result/job字段、producer/implementation和完整分页binding；业务外层改3不等于载荷可以静默变形 | **T01**给真实格式3成功/失败与历史结果/分页fixture；如字段/schema名称确需破坏性变化，先给精确diff和迁移说明。不得用新Project DTO拼一个私有兼容契约                                                                        |
| StoredResultSource.load                                                                      | 共享 `validateV2`/registry/error导出及 `result_project.get/result/job/page` schema身份仍有明确消费方式        | 现有固定main项目、输入/参数/依赖/实现/全页顺序、读完重读、同session与预算检查可保留。若导出/目录改名，**T01**给唯一同源替换入口，再由I06只改实际import/callsite，不维护第二validator                                     |
| 领域材料与字段scope                                                                          | 格式3仍提供同一不可变领域输入，metadata/draft未被实际读作模型输入                                             | 不自动把DB格式号、应用CAS或checkpoint摘要塞入scope；不因改名/草稿制造领域staleReason。新增应用数据真正成为外发输入时才另定义真实来源/版本/用户授权；当前I06没有该读取入口                                                |
| `operation.get` 与现有任务对账                                                               | 保留原Job/operation/marker身份及不可变历史；新application receipt不冒充Job成功                                | **T01**说明同UUID跨kind拒绝与原只读结果兼容。I06既有解释链不需要先消费新operation.list/checkpoint/草稿写API，不猜它们的SQL签名或RPC名                                                                                    |
| `getModelAccessStatus`、其余模型具名桥                                                       | 原模型契约由实际批准I06版本在单一canonical内合法保留                                                          | **T01当前canonical owner + 根**须在批准依赖安全集成点交付合并后的完整类型/校验/模型main-only分类；T01的5f基础不含e2c新增12方法，不能整份替换后假设I06仍可编译，也不能现在强令T01复制未批准gateway                        |

因此，若正式采用仅是**应用冷启动到同版已批准格式3**，且上述只读载荷/导出保持，不必为了格式号改StoredResultSource算法、复制Project DTO、升私有网关格式或新增metadata/草稿桥。当前 `models=[]/runtime-only` 和包内finite策略拒绝保留；数据库3不是新的producer白名单或生产字段溯源批准。

## 3. 生命周期缺口：冷启动与受控升级分开

### 冷启动/整应用受控重启

新main天然没有旧内存grant、选择和调用ledger；当前应用关闭流程会先关闭模型/取消等待，再收尾任务/engine。若由外部受控流程排空旧应用/自有DB连接、以同一writer lease完成迁移，并只启动批准的新应用/engine，既有模型服务新context/local可复用。**T01仍需给生产受信的格式3打开/迁移选择及实际ready证明**；当前内部 `target_format=3` 设计、user_version或一句“Store-ready”不能替代正式入口。不用测试fixture/testMode暗启真实用户库升级。

### 同进程受控DB/协议迁移、项目替换或明确关闭后重开

e2c事实是：TaskService.selectProject仅在UUID变化时调用onProjectChanged；dispose调用null；connectionChanged只fence view/recover，不发模型项目撤销。ModelGatewayService.selectProject对相同UUID早返。故**同UUID重读/新engine ready/renderer generation增加不是可信升级屏障**。这不是已证实e2c越权：现有普通引擎重连/renderer重建不自行等同新project session，来源重读、字节和授权绑定仍在，不能为了未来升级一律清掉现有普通恢复授权。

受控升级若选同进程路径，最小可信顺序须明确由谁调用和确认：

1. 在关闭旧协调器/变更DB前停止模型新接纳；通过现有 `models.selectProject(null)` 或等价受信本线边界关闭旧GatewayApplication，撤销旧context/preview/grant/material并取消pending。不是仅隐藏UI或把selected project UUID再设一遍。
2. 同步使旧项目异步响应失效。已有source.close/active abort、core.closeProject和service跨await同context检查可复用；已进入网络的数据不能撤回，取消只承诺阻止之后的本地继续，不能宣称过去零外发。旧凭据录入可能产生未发布的私有密文，不得据晚回调发布新配置/恢复旧授权。
3. **T01**完成原任务/operation对账、worker fence、自有连接排空、同lease迁移、Store-ready+Job-ready及实际结构/身份验证；任何失败保留证据且不恢复旧context为可发送。全局活跃旧SQLite连接不会靠PRAGMA自动失效，边界由受控入口负责。
4. 新engine取得真实同源catalog并完成outer2/[3]/selected3/双session相等的hello，main同步核真实registryHash/限额再ready；再真实project.get确认项目/格式/领域状态。只收到connection.ready或迁移回执不够。
5. I06在该可信重开点对同UUID建立**新context且local**，要求重新选材料/预览/明确确认；旧grant/pending/outcome回调不回流为新会话结果。新context前后已保存的非秘密配置可保留，不把公开持久configurationVersion与core内部版本合并，也不迁私有vault/audit进项目。

现 `EngineSupervisor.stop()` 是永久停止并清listeners，不能把同一实例stop后当可restart。若选择整套engine/TaskService重建，要明确旧实例dispose/新实例绑定与待恢复项目/Job引用的来源；若选择新内部生命周期hook，由**T01 engine owner**与**I06 main owner**先冻结最小受信信号/回调及错误顺序，本文不发明新RPC或要求所有普通重连触发升级。另一个必须对齐的实际引用是：ModelGatewayService构造时持有只读engine引用，StoredResultSource也固定该engine。若更换EngineSupervisor对象，仅重建TaskService并对旧models再selectProject同UUID仍会沿旧engine读取；必须一并关闭/重建关联模型服务（可复用index既有closeModels/initializeModels的私有资源加载边界），或先由owner定义可审的安全重绑。重开加载原非秘密配置不恢复旧grant。两种路线选定后才确认具体diff，不能只说“等T01”。

## 4. main启动与诊断必须由owner交付的实件

| 请求               | 必须交付的可核内容                                                                                                            | owner / 当前未定事实                                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| C1 正式候选        | 批准base/head、Store/Job/canonical/TS/Python/engine同版源与包内资源清单、实际format3启用范围                                  | **T01+根**；当前提案/Stage A内部候选均非批准生产依赖，不以其“ready”代通过                                                                    |
| C2 wire与hash      | 完整hello成功/三新null失败/旧[2]仅终止、业务3和session/pending/项目绑定；实际候选registry原bytes SHA256及编译registry同源检查 | **T01**；延续 `SHA256(registry.json原字节)`，不是多文件拼接或排序JSON。schema/errors/adapter另按manifest核同源；fixture a64不是实际ready凭据 |
| C3 升级前后边界    | 冷重启还是同进程、生产受信激活方式、同lease/排空/两层ready的调用顺序、失败/取消返回条件、项目重开实际读取                     | **T01 engine/DB + I06 main/index**；未经选择/冻结不预写CLI/env参数，不自行加入升级器                                                         |
| C4 读模型兼容      | Project3及原job/result/page/operation完整正反例、历史域输入hash不变、应用-only CAS不改domain/current的真实来源                | **T01**；任何导出/字段变更给确切映射，I06不猜新SQL/API                                                                                       |
| C5 准确启动失败    | 同源有限退出码/固定结构化异常来源、ENGINE_START_FAILED五reason与busy、首错优先、启动后exit不误归启动、确定性失败不反复起进程  | **T01 canonical/Python/engine**；还须证明TaskService有限重连请求不会越过sticky失败重新迁移，不能只靠retryable=false字段假定实现已停          |
| C6 单canonical集成 | 批准I06模型专名契约与格式3契约同版保留，原IPC权限/模型Python禁入不弱化；新类型/import/诊断消费者清单                          | **T01当前owner+根/I06**；不将T01的5f合同直接覆盖e2c新增模型合同，不要求当前采用未批准I06内容                                                 |

已有安全错误经EngineError→safeError→TaskService guard/main具名bridge传播可以复用；无需为了新本地启动错误造无pending stdout消息。准确**UI**诊断另有一个具体条件：e2c App.ErrorDetails调用 `apps/desktop/src/renderer/src/task-presentation.ts:explainError`，该switch没有engine.startFailed，会显示含错误code的通用模板。若要求该UI明确区分“不支持项目格式/结构”等，必须由根确认此**余6之外**精确路径的实际owner并代改或授权，使用冻结reason有限模板；本文不自行增加第7共享文件、不复制另一套展示器，也不把现通用安全展示说成泄漏或已完成准确诊断。

## 5. I06余六路径：是否真的要改

| 路径                                      | 判断与证据                                                                                                                                                                                                                                                                                                             |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apps/desktop/src/main/index.ts`          | **同进程升级/项目替换时需最小接线**：这里实际构造engine/TaskService、连接项目回调与models初始化。需可信升级开始停发、真实重开后新context；若仅冷启动且T01保持既有构造接口，不能仅因格式号断言必须改。生产新selector若确需参数，先由C3给精确签名                                                                        |
| `apps/desktop/src/main/task-service.ts`   | **条件变更**：若复用同实例做受控关闭/重开，需明确与真实升级事件关联的项目fence/旧view回调处理；也可在index dispose旧实例并重建，避免无必要改这里。不得把selectProject相同UUID的普通刷新改为一律撤销模型；view generation不变成授权epoch。确定性启动失败是否需提前offline以实测C5决定，不先扩大重试逻辑                 |
| `apps/desktop/src/preload/index.ts`       | **格式3本身不要求改**：仍是既有具名读桥，业务外层version由main engine处理。仅未来实际批准新增应用业务入口才逐方法另接，不加通用invoke                                                                                                                                                                                  |
| `apps/desktop/src/renderer/src/env.d.ts`  | **通常不改**：继承唯一DesktopBridge类型；公共类型由T01统一，不手写Project3/错误镜像                                                                                                                                                                                                                                    |
| `apps/desktop/src/renderer/src/App.tsx`   | **只在实际同进程升级UI仍存活时确认必要diff**：现轮询按context变化清preview/grant、无context清outcomeCache，但等待中的旧status/outcome IPC仍需以实际context/升级周期防晚响应显示为新会话。冷重启/真实卸载可自然清空；不把这个未来测试条件认定为已复现e2c越权。准确错误文案优先走既有presentation owner，不默认复制到App |
| `apps/desktop/src/renderer/src/style.css` | **无现证据要求改**：没有新布局需求；不因协议升级做无关视觉改动                                                                                                                                                                                                                                                         |

私有 `StoredResultSource`/`GatewayApplication`/`ModelGatewayService` 优先保留现有严格读取与关闭机制。只有C4证实载荷/导出变更或C3选定的生命周期无法由现有关闭/重建完成时，才提本线精确适配diff；不升级私有配置journal/密文/audit格式，不增加原子live-current lease或默认Q9。本请求的migration writer lease是现有Store/Job生产连接仲裁，与socket持续current承诺分离。

## 6. 必要验证范围与精确待授权测试路径

下列是**集成前申请范围**，尚未创建、未授权写测试；原测试不修改，不按计划数量计通过。T01负责其canonical/迁移/两层ready/启动分类真实反例及实际包内来源，I06负责消费接线；共同固定最终批准candidate，保留首跑失败。

| 拟新增路径（待根登记owner）                                                         | 必要断言                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/unit/i06-format3-consumer.test.ts`（拟I06）                                  | 用批准同源Project3/job/result/page验证现adapter；完整分页/历史/evicted/跨项目与错误安全传播；两次实际应用-only CAS后domainSnapshot/vector/current不变，source重读不混入metadata/checkpoint；若共享导出改名则实际import/typecheck对应    |
| `tests/unit/i06-format3-lifecycle.test.ts`（拟I06）                                 | 可信受控升级开始→旧context/grant/选择/pending关闭；凭据/audit/source读取等待中晚回调失效；同UUID重开在真实ready+project.get后才新context/local。普通engine重连/renderer恢复作为对照，不被误标升级；若App存活，旧IPC回包不覆盖新会话显示 |
| `tests/i06-main-platform/format3-consumer-probe.mjs`（拟本线平台owner，需精确协调） | 隔离环境实际批准source及真正包内engine/同源catalog，outer2选3/真实hash/业务3/Project3；受控关闭/同lease/两层ready证据对应、错误格式库安全诊断；重开前无新POST/重开后明确新授权，原网络已发送部分单列而非宣称可撤回                      |

上述单元路径中的真实应用CAS fixture必须由T01已批准受信adapter制备；不在I06私开SQLite writer、直接SQL造状态或假造receipt。若正式采用暂不提供应用mutator，则只验证现已获批的只读边界，应用CAS相关项明确待该实际接口交付，不能用stage A默认状态冒充已测CAS。

必要运行收口还包括：新协议/假hash/旧session/同chunk失败不能ready或执行业务；失败generation全部pending结束且不复活；新context前后本地Store/Job对账与失败隔离。准确错误展示若获授权，另列有限模板/未知reason降级/无原异常路径泄漏检查。I06消费接线变更后做对应typecheck/静态/构建及实际批准候选的必要联验；不因为纯所有权/文档变化重复e2c已过回归，不把旧e2c/9fc平台事实贴成格式3通过。新的baseline或受审实现变化仍按原完整同版指定双方新审、CI/PR/正常合并/远端核验门禁。

下一可执行交付是根/T01冻结C1–C6及选择冷重启或同进程路线，登记实际必要的余6 diff与新测试owner；I06据批准可消费的只读合同实施最小适配。本文交付不是格式3接线、迁移、ready或完整I06通过。
