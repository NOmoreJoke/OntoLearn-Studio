# I06 最小命名窄接口草案

2026-10-21；文档分支 base `4ace4c4ce054edd1037d32df1bef48732075702e`。正式批准运行基线为 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`，不依赖未合并 I05 候选。本文件是待唯一公共 owner 审查的接口提案，不是 schema、注册决定、实现报告或验收通过。对应合成样例见 [narrow-interface-examples.json](narrow-interface-examples.json)，既有私有实现约束见 [main-integration-handoff.md](main-integration-handoff.md)。

## 已批准读取、私有服务和必要扩展

| 层                     | 可使用的事实与边界                                                                                                                                                                                                                                           | 本草案的处理                                                                                                                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| I04 已批准只读接口     | `project.get({projectId})`、`job.get({projectId,jobId})`、`result.get({projectId,resultId})`、`result.page({binding,pageSize,cursor})`；现有窄 bridge 的 `getActiveProject/getJob/getResult/getResultPage`。schema/registry 以 `packages/contracts/v2/` 为准 | 复用现有校验器，main 决定 projectId 和完整 page binding；不是让 renderer 选引擎 method。pageSize 1–200、排序 `ordinal+rowId:asc`、完整读至 nextCursor=null，不把一页当整份结果                                              |
| I04 身份不足           | result DTO 没有整 payload hash、字段级 provenance、S3 外发许可或 current lease。`asserted/asserted+derived/scenario` 是图作用域，不是外发权限                                                                                                                | main 对完整 rows+metadata 计算实际 hash；不能从 DTO 的 scope、parametersHash、inputSnapshotId 或自报 hash 推导外发许可                                                                                                      |
| 已有未冻结私有来源初稿 | `StoredResultSource(engine:EngineSupervisor, mainProjectId, producerPolicy='runtime-only')`；`load({resultId,selection:'current'                                                                                                                             | 'historical'},signal?)`→ 复制的`{metadata,bodyText,bodyHash,sourceFingerprint}`；rows 包含在规范化 bodyText 内，不作为独立返回字段                                                                                          | 固定实际 supervisor/项目，复用 `validateV2`；逐项核对 producer/job/input/实现版本/current-history/payloadStatus、全页结果与完整重读一致性。初稿存在不表示运行、独立审查或正式接线已通过 |
| 已有未冻结私有应用初稿 | `GatewayApplication(core,source)`，项目来自固定 source.projectId；`selectStoredResult`、异步 `preview`、`confirm`、`start` → main 生成 invocationId+completion、`cancel(invocationId)`、`releaseSelection`                                                   | 下述公共 adapter 只做命名参数校验、可信 context 绑定和固定结果投影，不公开 core 的 register/derive/configure/invoke 或私有 completion 枚举。批量选择、rowCount/byteCount 投影、持久设置和有限终态 ledger 仍为此草案所需扩展 |
| 必要公共扩展           | 下表所有 S3 方法、contextId、展示 DTO、独立取消结果、精确网关公共错误                                                                                                                                                                                        | 当前 registry 没有这些方法。需新版本、唯一 owner、公共正反例及指定双审后，才可接 main/preload/UI；不能把这份 JSON 直接作为第三份运行协议                                                                                    |
| I05 后置语义           | 当前已批准 producer 仅 `test.*`；业务 query/reasoning/validation 仍 design-only                                                                                                                                                                              | 默认 runtime-only 拒绝未实现 producer。私有 synthetic-test-runtime 仅用于 I04 合成真实 Store/worker 链，绝不由公共 params 开启。字段级/真实业务 provenance、工具生成材料在 I05 实际合并后另验                               |

Q9 的真实 provider 协议未决，不自动阻塞合成 S3 主进程/授权/存储/窗口链的正式实现与验证；合成链也不能证明某真实 provider 协议已获选择。macOS/Windows safeStorage、Windows ACL、签名/升级/干净设备缺口仍属于完整平台验收待办，不能因接口草案或 Linux 结果将其宣布为非阻断。

## 可信调用者与状态 owner

只有经 main 核验 sender/webContents、mainFrame、可信文档及当前项目上下文的本地 UI 可调用。Python、模型、导入数据、Agent 工具与任意 iframe 不获得这些方法。可信 frame 不等于用户已经同意外发：main 读取权、设置意图、预览后的确认动作分别验证。

`contextId` 是 main 为当前项目服务签发的 UUID，用于拒绝过期 UI 动作，不是 renderer 自报 projectId 或权限。除状态读取外所有方法必须携带当前 contextId；main 按调用者与实际项目绑定核对，并在跨 await 后再次核对。项目切换/关闭使旧 context、选择、预览、grant 及调用失效；不得把旧 handle 迁移到新项目。窗口重建保留实际 main 项目服务，重新校验新 sender，只读状态/结果，禁止自动确认或重发。

main 项目服务持有隐私模式、selected result handles、预览、授权、活动 invocation 和有限终态；app 设置 owner 持有配置身份/凭据绑定。平台密文仓库和审计位于真实 app 私有目录，初始化失败只禁用模型功能，不阻断 Store 启动、保存或历史读取。UI 不持有解密 secret、凭据引用/version、审计查询权限或完整仓库；录入 secret 仅在用户输入控件短暂存在，经专名方法送 main，不进入状态管理、URL、日志、遥测、项目/导出或响应。JavaScript 字符串不能承诺内存物理清零。

## 拟定公共数据形状

以下为待批准的精确 TypeScript 记法；每个对象及每个 union 分支均 additionalProperties=false，不接受隐式转换、额外字段或 undefined 占位。UUID 使用现有 id 格式；Hash 为 64 位小写 hex；所有字节上限均按 UTF-8 检查，计数为0..MAX_SAFE_INTEGER的整数且还须满足逐项上限。endpoint 输入及规范化输出均最多2048字符。全部方法采用现有 `BridgeResult<T>` 的 ok/data 或 ok/error 外壳；执行取消位于成功读取的独立状态分支。

```ts
type Privacy = 'local' | 'minimal' | 'project'
type ResultChoice = { resultId: UUID; selection: 'current' | 'historical' }
type WholeResultSelection = {
  kind: 'whole-result'
  selectionId: UUID
  metadata: ExistingV2Result // 原 result.get 严格 DTO，不扩写 provenance 字段
  selection: 'current' | 'historical'
  bodyHash: Hash // main 对实际完整复制内容计算，只有一致性作用
  rowCount: number // 0..MAX_SAFE_INTEGER；仍受下文字节上限约束
  byteCount: number // 0..65536
}
type FieldSelection = {
  kind: 'fields'
  selectionId: UUID
  metadata: ExistingV2Result
  selection: 'current' | 'historical'
  catalogId: UUID
  fieldIds: UUID[] // 1..256，唯一，均由可信 catalog 解释
  projectionHash: Hash
  rowCount: number // 0..MAX_SAFE_INTEGER
  byteCount: number // 0..65536
}
type Selection = WholeResultSelection | FieldSelection
type Configuration = {
  configurationId: UUID
  configurationVersion: UUID
  displayName: string // 1..128 字符，纯文本显示
  endpoint: string // main 规范化 HTTPS 目标；无账号/密码/query/fragment
  model: string // ^[A-Za-z0-9._:/-]{1,128}$
  credentialState: 'missing' | 'configured' | 'unavailable'
}
type InvocationState = 'running' | 'cancelling' | 'completed' | 'failed' | 'cancelled'
type InvocationSummary = { invocationId: UUID; state: InvocationState }
type Outcome =
  | { invocationId: UUID; state: 'running' }
  | { invocationId: UUID; state: 'cancelling' }
  | { invocationId: UUID; state: 'completed'; text: string } // <=1MiB UTF-8；只作文本
  | { invocationId: UUID; state: 'cancelled'; externalEffect: 'unknown' }
  | { invocationId: UUID; state: 'failed'; error: ApprovedSourceOrPendingGatewayError }
```

`ApprovedSourceOrPendingGatewayError` 不是新 catalog：来源错误复用实际获批白名单并校验；网关精确映射仍待公共 owner 批准。私有 `CANCELLED` 只投影到 cancelled 分支，不能成为公共 error、Job failed 或领域 staleReason。completed 文本不执行 HTML/脚本，不把模型建议当确定性结果、确认修改或工具权限。

## 命名方法、精确输入/输出及错误子集

表中 `G(...)` 仅引用 [I03 disposition 与 11 类需求](public-error-requirements.md) 中的内部语义标签，**不是已批准公共 code**。`S` 为下一节明确列出的现有来源错误。全部方法还允许固定的 INVALID_REQUEST(field=params)、PERMISSION_DENIED 和 INTERNAL_ERROR 安全兜底；不得透传校验 issues 或异常。

| 拟定方法                     | 严格 params                                                                 | `ok:true` 的 data                                                                                                                                      | 行为与专属错误子集                                                                                                                                                                                                                                                                                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `getModelAccessStatus`       | `{}`                                                                        | `{contextId:UUID, privacy:Privacy, configurations:Configuration[], invocations:InvocationSummary[]}`                                                   | 只投影 main 状态，配置<=32、调用摘要<=68。credentialState 不是远程 key 有效性证明，不触发模型调用/平台提示；只显示实际已初始化状态。不通过读取 secret 探测状态                                                                                                                                                                                                     |
| `updateModelConfiguration`   | `{contextId:UUID, configurationId:UUID                                      | null, displayName:string, endpoint:string, model:string}`                                                                                              | `Configuration`                                                                                                                                                                                                                                                                                                                                                    | null 仅表示创建，ID/version 由 main 签发；已有 ID 必须属于受信设置 owner。HTTPS 规范化与核心相同，拒绝用户信息、query、fragment、无效编码、任何 loopback/test-policy 参数；不是任意 URL/headers/body 转发。G(INVALID_INPUT,CONFIGURATION_CHANGED,CREDENTIAL_UNAVAILABLE)；配置持久化失败公共语义仍待批准，不能伪称成功 |
| `storeModelCredential`       | `{contextId:UUID, configurationId:UUID, secret:string}`                     | `{configurationId:UUID, configurationVersion:UUID, credentialState:'configured'}`                                                                      | secret 为 1–4096 位可打印 ASCII；只送 main 平台加密。首次录入和轮换由 main 生成 opaque principal/ref/version，禁止自报主体/version；响应不含 secret/ref/principal/credentialVersion。G(INVALID_INPUT,CONFIGURATION_CHANGED,CREDENTIAL_UNAVAILABLE)                                                                                                                 |
| `setModelPrivacy`            | `{contextId:UUID, mode:Privacy}`                                            | `{privacy:Privacy}`                                                                                                                                    | 默认 local；改变 mode 撤销旧预览/grant。local 同时取消关联等待，已发送内容不能撤回，不改变领域 staleReason。G(INVALID_INPUT)                                                                                                                                                                                                                                       |
| `selectModelResults`         | `{contextId:UUID, results:ResultChoice[]}`                                  | `{selections:WholeResultSelection[]}`                                                                                                                  | 0–64 个唯一 resultId；空数组清空选择。main 逐份真实读取整份结果，批次成功后原子替换选择集；失败保持旧选择并释放新临时句柄。selectionId 由 main 签发；未完成 invocation 继续持有自己的已复制材料直到终态。S，及 G(INVALID_INPUT,SCOPE_EXCEEDED)                                                                                                                     |
| `previewModelExplanation`    | `{contextId:UUID, configurationId:UUID, selectionIds:UUID[]}`               | `{previewId:UUID, configurationId:UUID, configurationVersion:UUID, endpoint:string, model:string, principal:UUID, purpose:'explain', privacy:'minimal' | 'project', selections:Selection[], authorization:{state:'required'}                                                                                                                                                                                                                                                                                                | {state:'reusable',grantId:UUID}}`                                                                                                                                                                                                                                                                                      | 1–64 唯一句柄，必须为 main 当前选择集；异步重读完整来源一致后，由服务内部生成外发 scopes 并调用 core.preview。UI 展示真实目标、主体、隐私档、整份结果身份/数量/字节，不能省略后自动确认。S；G(INVALID_INPUT,LOCAL_ONLY,CONFIGURATION_CHANGED,SCOPE_EXCEEDED,CREDENTIAL_UNAVAILABLE,AUTHORIZATION_REQUIRED) |
| `confirmModelAuthorization`  | `{contextId:UUID, previewId:UUID}`                                          | `{grantId:UUID, configurationVersion:UUID}`                                                                                                            | 仅对已展示、仍有效的 main 预览执行明确用户确认；不得模型/恢复自动调用。确认后预览不能再次确认。范围/用途/规范接收配置/主体/凭据版本/隐私 epoch 全相同的既有授权可由 main 在 preview 返回 reusable；renderer 不能指定是否复用。G(INVALID_INPUT,LOCAL_ONLY,AUTHORIZATION_REQUIRED,CONFIGURATION_CHANGED,SCOPE_EXCEEDED)                                              |
| `startModelExplanation`      | `{contextId:UUID, configurationId:UUID, grantId:UUID, selectionIds:UUID[]}` | `{invocationId:UUID, state:'running'}`                                                                                                                 | 固定用途 explain；1–64 唯一当前句柄。main 生成 ID、登记 completion、返回，不 await 长模型调用；来源重读、持久审计和发送在受控异步任务继续。返回 running 只表示已接纳，不能说明已发送/完成。S 或网关失败若在接纳后发生，进入 getOutcome 的 failed；接纳前 G(INVALID_INPUT,LOCAL_ONLY,AUTHORIZATION_REQUIRED,CONFIGURATION_CHANGED,SCOPE_EXCEEDED,MODEL_UNAVAILABLE) |
| `getModelExplanationOutcome` | `{contextId:UUID, invocationId:UUID}`                                       | `Outcome`                                                                                                                                              | 只查询当前 main 服务实际已登记调用。窗口重连仅此方法/状态读取，不调用 start。未知/跨项目/被回收 ID 固定 G(AUTHORIZATION_REQUIRED) 待批语义，不泄露是否曾存在；所有执行 S/G 失败只出现于失败分支                                                                                                                                                                    |
| `cancelModelExplanation`     | `{contextId:UUID, invocationId:UUID}`                                       | `Outcome`                                                                                                                                              | 只取消该 invocation，先返回 cancelling 或已终态；清理结束才 cancelled。重复取消不创建调用，已终态保持原结果。未知/跨项目 ID 与 getOutcome 相同；不能取消其他 grant 下所有用户任务来冒充单调用取消                                                                                                                                                                  |

这是初始“解释明确选中整份结果”的公共面；不把 suggest/review、任意材料派生或 Agent 工具转发挤入同一个通用方法。现有核心的其他安全规则/测试及完整 S3 验收仍保留，后续用途需要自己的业务语义和命名契约。

## 配置生命周期、错误与限额

配置编辑方法是**必要新提案**，当前 core 无 displayName/配置持久化公共 owner。需实现应用私有非秘密配置的原子存储、恢复及并发串行化：先成功发布新凭据密文，再安装相应新身份/version；任何失败不能返回 configured，不能覆盖旧有效配置。规范 endpoint 改变时不复用旧 endpoint 的凭据，目标进入 missing，必须新录入；model/凭据主体/version/配置身份变化撤销对应授权、预览及关联请求。纯 displayName 变化不改变接收身份，不冒充 core 已支持的字段；如公共 owner 选更保守全部撤销，须写进批准契约。旧不可变密文的安全回收/可达性/上限仍需设计，不能无限积累或从项目导出回收。

S 只可来自真实已批准请求并按当前 `errors.json` 校验：NOT_FOUND(resource限 project/job/result/snapshot)、PAYLOAD_EVICTED(resultId)、CURSOR_MISMATCH、CURSOR_EXPIRED、INVALID_STATE、UNSUPPORTED_CAPABILITY、RESOURCE_LIMIT(resource限 memory/page/frame)、TIMEOUT(实际批准 phase，当前私有 source 总预算使用 total)、SESSION_MISMATCH、ENGINE_EXITED、STORAGE_BUSY、STORAGE_FAILURE，以及 PERMISSION_DENIED/INTERNAL_ERROR。不得按异常文本猜来源、把模型配置失效冒充 REVISION_CONFLICT、把重定向错误冒充 NETWORK_FORBIDDEN。来源字段缺失/伪造/额外键只降级固定 INTERNAL_ERROR，不输出原文。具体 subset 仍由实际 source 实现及公共 owner 对齐，不能仅因列在这里制造新来源。

G 继续采用 I03 的新版本待批策略，不复制 catalog；必要最终字段为固定 code/messageKey、严格 params、retryable=false。现有 INVALID_REQUEST 例外固定 `{field:'params'}`；现有来源错误保持其获批参数和 retryable，不擅自改写已批准 schema。**任何 retryable 均不授权桥接/重连自动重发。**网关掌握的 429/503 至多一次内部重试每次重新授权/审计，外层不得叠加；网络/审计失败不证明此前没有发送，写任务仍先 operation/job 对账。

内部现有资源界限：配置32、预览128、grants128、材料512、每份64KiB、每次<=64材料且总scope并集<=256、最终请求<=256KiB、响应<=1MiB、并发发送4、网络单次5s。下列公共 adapter 限额是**待批准提案**：当前选择<=64、选择批次每项目至多1项正在加载；main invocation ledger 4个活动+64个终态，终态按 main 完成序淘汰，已淘汰 ID 不恢复/重放；每份整结果超过64KiB则整体拒绝，不截断 rows/来源。数值是内部保护，不是 Q5 产品容量/性能承诺。main 重启后内存调用/选择/授权失效，持久审计恢复不重放，也不伪造已丢失的模型响应；UI 明示结果不可恢复，用户必须重新选择/预览，不能按旧 ID 自动续发。

## 最后读取与发送之间的真实缺口

StoredResultSource 计划做完整 rows+metadata hash 与前后完整重读；它只能证明**读取时**内容一致，不是许可、字段 provenance 或 live-current lease。明确选中不可变结果快照不等于发送时仍 current；historical 选择必须是用户显式操作，evicted 不能重算冒充。core 的配置/授权最终 socket guard 不能自动观察另一个 Store 进程在最后读取后提交的变化。

若正式语义要求“发送那一刻仍 current”，需要唯一 Store owner 提供可审查的 snapshot/epoch lease：main 在选择/预览/start 绑定实际项目/结果版本，最后 socket 边界核对真实被持有的 lease。所有能改变受保护当前性/回收的写入路径必须实际经过同一仲裁并与发送边界安全释放协调，证明跨进程原子性；仅靠异步撤销通知、主进程 epoch 镜像或先比对后无锁发送仍有同一竞态。不能用 renderer 回传 hash、轮询、最后一次异步读或内存布尔值冒充原子保证。具体 lease/进程故障释放/历史结果切换接口尚未批准，此处保留阻断验收项。若产品允许解释明确选择的不可变历史快照，也必须先批准该语义并完整展示身份，不能静默降为旧快照解释。

## A-03 字段选择与来源绑定：正式 S3 必须补齐

PRD G.5 原 A-03 是“仅授权选中字段后触发工具调用”，工具返回的其他列不得进入下一次模型请求。当前 whole-result 初稿只能证明整份已选结果链，**不能替代 A-03**，也不能通过把所有列都声明成同一 scope 来算通过。I04 row/result DTO 没有可信列名/单元格 provenance、字段级读取/投影或“某个值来自哪个原始列”的证明；body hash、graph scope、random scope UUID 和 derived 输入并集均不能补出这些事实。上面的公共 whole-result 方法只能用于明确授权整份结果的场景，不能成为 A-03 尚未实现时的正式 S3 完成依据。

唯一 contracts/Store/语义 owner 需要追加并审查两项命名读取/投影面，以下是具体待批接口需求，不是假定已存在的 schema：

- `getModelFieldCatalog({contextId,resultId,selection})` → `{catalogId:UUID, resultId:UUID, fields:{fieldId:UUID,label:string}[]}`。main 验证实际读取许可；字段数量上限256、label最多128字符并按文本展示。catalogId/fieldId 均由可信 owner 签发，绑定固定项目、producer/job/input/实现版本、结果/源数据身份和实际列/单元格来源映射。renderer 只能选择服务提供的 fieldId，不能上传列名、原始值或 provenance。实际原始列身份如何由 Store/真实 worker 提供，仍须 owner 扩展并以真实 I05 来源证明。
- `selectModelFields({contextId,catalogId,fieldIds:UUID[]})` → `FieldSelection`，字段严格按上文带 kind=fields 的分支。fieldIds 为1–256唯一已获读权限的 catalog 字段；main/可信投影服务读取并组装实际选中字段字节，不能先允许任意工具文本进入再贴 scope 标签。projectionHash 由实际投影字节计算，只作一致性，不作许可；行/字段变化使 catalog/selection 失效，超64KiB整体拒绝。新 field selection 进入同一 preview/confirm/start 生命周期，但与 whole-result scope 严格不同，字段 grant 不可复用到 whole-result handle。此方法仍受当前 context/实际读取许可门，来源错误使用 S，参数或范围问题使用 G(INVALID_INPUT,SCOPE_EXCEEDED) 待批映射；不得以读取成功自动确认外发。具体投影类型及 scope/source binding 须新公共版本批准，不在此复制引擎协议。

工具结果/历史/摘要/错误进入网关时，可信 assembler 必须从真实来源映射重建允许字段投影，剔除未授权其他列及由其派生的值；`deriveFromMaterials({inputs,kind,text})` 的输入 scope 并集本身并不证明 text 没有混入其他列。最终实际发送边界同时检查 grant、配置身份、字段 projection 与可信来源链。必要反例是实际工具返回选中列与未选列两种不同合成标记，capture receiver 对下一次请求完整 bytes 断言未选列标记零出现；包括工具正文、历史、摘要、错误、重试/重定向路径，不能只测 params 拒绝 renderer.scopes。缺少真实字段映射/投影接口时，A-03 保持未验收，不以 whole-result probe 替代。

编号按原文保留：A-04 是导入文本要求忽略隐私，工具与隐私权限必须不变；A-05 是同一配置 Base URL 从 X 改 Y 后旧授权失效，而只改显示名可保留。A-03/A-04/A-05 的要求互不替代，均需真实 main/材料/发送链证据。

## 唯一 owner 的后续共享修改清单与验收

| 共享面                                                                                                                                         | 必要改动及验收                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/contracts/src/index.ts`、`src/v2.ts`、`v2/schema.json`、`registry.json`、`errors.json`、fixtures/binding-regressions、Python镜像定义 | 唯一公共 owner 批准精确方法/DTO/错误/取消与正反例。S3 owner为main、agentEligible=false；Python协议不得因此得到secret/模型调用能力。不是将 main IPC 中转为引擎通用请求 |
| `apps/desktop/src/main/index.ts`、`task-service.ts`、可信文档/sender、实际项目服务、`EngineSupervisor`                                         | 固定上下文与来源读取、私有实例生命周期、设置原子提交、invocation登记/取消/有限终态、最终guard和可信实际Store联验。所有后台失败不得阻断本地保存                        |
| `apps/desktop/src/preload/index.ts`、renderer env/`App.tsx`及必要展示                                                                          | 仅表中命名方法；设置/短暂录入、目标/范围预览、明确确认、独立取消、只读恢复、纯文本输出；不暴露通用 method/URL/headers/body，也不公开 private test policy              |
| Store/结果当前性或回收 owner、I05真实语义实现                                                                                                  | 补 lease/epoch 选择及结果producer/历史/evicted/全页完整性真实证据；当前合成Store/worker链与后续I05真实provenance分开记录                                              |
| 构建、打包、平台CI及实际可用项目/导出入口                                                                                                      | 唯一网关实际入包；平台safeStorage与私有仓库、实际普通日志/导出排除、真实保存/重连失败隔离。不存在的导出器不能用mock记通过                                             |

公共样例须迁入批准 schema 的同版 fixture 并实际执行，才能证明严格拒绝/接受；本文件仅做 JSON/格式/diff 校验。正式 main→bridge→UI、真实平台缺口、同一冻结候选指定双审、CI 与 develop 合并远端核验全部保留，不因草案形成而完成 I06。
