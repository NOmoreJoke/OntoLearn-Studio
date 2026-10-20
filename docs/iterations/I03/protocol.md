# I03 v2 协议设计

规范结构见 `packages/contracts/v2/schema.json`，各对象 `additionalProperties:false`；可变键字典仅允许版本向量/摘要键并限制属性数。TS 用 zod strict 对象，Python 用同一受限 JSON Schema 子集；适配器不识别的 schema 词汇拒绝，不能静默跳过。约束另含跨字段、字节和绑定关系校验。错误目录与规范 error 分支的一致性有测试锁定。完成度见 [status](../../reviews/I03/status.md)。

## 引导与帧

稳定 bootstrap 是 `protocolVersion:2, method:hello, engineSessionId:null`，params 为 `supportedVersions/clientId`，新进程只接受一次 hello。双方只选择明确共同支持版本，本版只支持 2；无交集返回 VERSION_INCOMPATIBLE 和 `[2]`，不隐式降级。v1 为内部骨架，无长期兼容承诺。握手成功响应的外层 session 必须等于 result.session，结果包含 selectedVersion/engineVersion/session/capabilities/limits/registryHash；能力必须来自实际实现/验证交集。当前 v2Runtime=[]，不能将设计条目发到生产声明。hello 后再 hello 为 INVALID_STATE，握手前其他方法为 HANDSHAKE_REQUIRED。失败 hello session 可为 null；成功必须是不复用的 UUID。

传输只使用本地 stdio，每行 UTF-8 JSON，行末 LF；stdout 不混日志，输出后 flush。CRLF 可去除单个 CR，空行、BOM、坏 UTF-8/JSON、重复对象键、非有限数字、超深对象均拒绝；不能将多个 JSON 作为一个对象解析。reader 按未完成单帧字节检查，追加前先检查上限，跨字符保存有限字节，不按 JS 字符数计大小。一次 chunk 含多帧时逐帧消费，不能把整个 chunk 字节数误当单帧。到达错误/退出终态后停止累积、清空所有 pending 与部分帧；后续 chunk 直接丢弃。

本版硬上界：请求与响应/通知单帧 262144 字节（不含 LF），对象嵌套不超过 32 层；error 紧凑 UTF-8 编码 2048 字节；单页完整结果 131072 字节、最多 200 行，每行 64 个单元格，每格最多 8192 Unicode 标量。错误参数条数由每码严格对象约束，最大为五项；row≤1048576/column≤16384。超量明细只用不透明 detailRef 分页，不能塞进错误。stderr 每会话最多 16384 字节、每条≤1024；只固定事件码/安全身份，不记录正文。I04 流读取需在解析前执行深度/原始帧大小/重复键约束；本迭代 validateV2 接受的是已经解码的 JSON 值，不声称验证原始帧。

`limits` 各字段独立且有硬上界：startup/handshake/request/heartbeat/cancelGrace 各≤60000ms；任务 total≤3600000ms；queue≤128、并发≤8、worker memory≤2GiB。profile 的提议默认：启动10s、握手5s、请求5s、心跳10s、取消收尾5s、任务2min、队列32、并发2、内存512MiB、分页100条。I04 必须通过实际测量再决定运行配置；不得把这些数值称为容量达标。协商只能降低，能力配置不能超过本版硬上界；心跳不延长总期限。超时按 phase 命名，控制请求仍可在计算忙碌时被处理。

## 方法与精确 schema

每个请求有 `kind/id/protocolVersion/engineSessionId/method/params`；响应有同 id/method/session，成功只有 result，失败只有 error。为避免无 pending 的错误响应，坏 JSON/无合法信封/未知方法属于会话级协议错误：主进程结束会话并以本地固定错误清理 pending；不反射未知 method、原始帧或路径。合法已知方法的 params 错误可用其 id/method 返回 INVALID_REQUEST。notification 无请求 id。稳定服务方法在 registry 中标记 owner、读写、范围和设计状态。

| 方法            | params 必须字段                                                      | 成功结果                                    | 责任与边界                                                                                          |
| --------------- | -------------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| hello           | supportedVersions, clientId                                          | 握手记录                                    | 仅 bootstrap                                                                                        |
| health          | 空对象                                                               | status=ok, engineVersion                    | 会话级短探针                                                                                        |
| session.ping    | nonce                                                                | 同 nonce                                    | 会话级心跳，不影响任务总时限                                                                        |
| project.get     | projectId                                                            | revision/snapshot/vector/formatVersion      | 不传文件路径，项目打开由主进程文件选择服务负责                                                      |
| job.create      | projectId, operationId, capability, input, confirmationRef           | 持久 job DTO                                | input 为 snapshot/scope/definition/参数摘要/派生结果引用/preparedPlanRef；不传自由方法/任意 payload |
| job.get         | projectId, jobId                                                     | 持久 job DTO                                | 恢复时先校验归属                                                                                    |
| job.cancel      | projectId, jobId                                                     | disposition/state/stateVersion              | accepted/alreadyRequested/alreadyTerminal；不把 accepted 当终态                                     |
| job.list        | projectId, filter, pageSize, listSnapshotId, cursor                  | 固定集合 job 页                             | 初次两个身份均 null，后续均非 null；最多100条                                                       |
| job.subscribe   | projectId, jobId                                                     | subscriptionId/project/job/stateVersion/seq | 主进程建立限权订阅，新序列起点；随后 job.get 补状态                                                 |
| job.unsubscribe | projectId, jobId, subscriptionId                                     | unsubscribed=true                           | 只停止投递，不取消任务                                                                              |
| result.get      | projectId, resultId                                                  | 不含大载荷的结果元数据                      | evicted 明示，不伪装空结果                                                                          |
| result.current  | projectId, kind, definitionId, scope, parametersHash, implementation | 结果元数据或 null                           | null 仅合法身份下确无当前结果                                                                       |
| result.page     | binding, pageSize, cursor                                            | binding/rows/nextCursor                     | 稳定键与限额见 shared-state                                                                         |
| operation.get   | projectId, operationId                                               | 原子提交标记或 null                         | 权威对账，不创建新写入                                                                              |

正式 job.create 不接受客户端 jobId/dependencyVector/集合摘要/limits/实现版本；服务从可信快照、参数仓库与运行配置解析。参数内容以内容寻址 immutable blob 保存；preparedPlanRef 只引用经结构/引用/领域检查和预览的计划。确认记录绑定项目、base、planHash、diffHash、权限与人类确认者，不能仅凭任意 UUID 视为确认；Agent 不能发放自己的 confirmationRef。只读任务不带确认或写计划，正式写任务两者必需。业务能力设计项不进入开放名单，任意或尚未实现 capability 返回 UNSUPPORTED_CAPABILITY。

## 身份、绑定与通知

公开 project/job/operation/request/session/subscription/result/run/detail/cursor 身份为小写 UUIDv4。job/operation 在全库持久唯一，跨项目与重启不得复用；request 仅在本 session 内唯一，不跨重连重用 pending。snapshot/参数/计划是小写64位 SHA-256。S1 内部历史短字符串 ID 不改写，I04 通过持久可迁移映射表分配公开 UUID，验证双向唯一，不能直接将任意内部字符串穿过公开 schema。

主进程先校验 sender/mainFrame/可信文档，再将调用绑定到已授权项目服务；引擎检查 session、project 与 job/result/operation 所属项目。UUID 不等于权限。pending 索引是 `(engineSessionId,requestId)`，保存 method 和输入归属；matchesResponse 是纯绑定检查，实际服务还须验证参数及结果归属，不能只看 schema。未知/重复/过时响应不结算新 pending；记固定诊断并有界关闭异常会话。超时清理 pending 后的迟到响应丢弃，不重发写请求。旧进程全部 pending 返回 ENGINE_EXITED，但这只是传输结果，任务终态通过持久 job.get/operation.get 恢复。

项目通知必须有 session/project/job/subscription/seq，event 仅 job.progress/job.state；session.status 采用单独 schema，不伪造 project/job。seq 是每会话每订阅严格递增正整数；session.status 另有独立序列。重连新 session/新订阅新序列，不能覆盖持久 stateVersion。接收同时匹配四个身份、seq>lastSeq、stateVersion≥已知版本；job.state 的 DTO project/job 必须与外层一致。seq 缺口触发 job.get，不能靠通知推算正式状态。解绑或切项目先撤销订阅能力与 generation，随后即便匹配旧 UUID 也丢弃。

## 安全错误

`error={code,messageKey,params,retryable}` 全部由白名单决定；不允许 free-text message、堆栈、路径、单元格值、原查询/IRI 或凭据。worksheetId/detailRef 是服务分配的不透明 ID，field 为有限枚举；显示标签需要主进程授权的资源读取，不能塞回 params。errors.json 与 schema 完整对照有测试，码与 messageKey/retryable 必须成对，不允许客户端改变含义。

错误分层：协议失败清 pending；业务任务失败持久 job.error；取消是 state=cancelled；过期是 staleReason；不支持为 UNSUPPORTED_CAPABILITY，不混入失败推理结论。bridge 必须原样保留这四个安全字段；UI 依 messageKey 在本地组装 PRD8.6 的“发生什么/原因/如何修复/相关知识”，技术详情也只显示安全枚举与引用，不展示原始业务异常。映射定位错误可打开授权详情，但仍不能自动进入模型上下文。

SQLite 例外映射规则、锁与幂等见 [jobs-and-storage](jobs-and-storage.md)。主进程凭据/授权/网关仍由 I06 独立拥有，不为统一能力表而塞入 Python；读权限与模型外发授权始终分开。

I03 纯值校验使用两端相同的保守编码预算：所有数值 token 按32字节计，其余按紧凑 JSON 的 UTF-8 转义成本，拒绝未配对 surrogate；数值限定 JS 安全整数范围内（小数可用），避免两种浮点打印格式改变边界判断。该预算保证返回编码可装入帧/页，可能提前拒绝临界大页；I04 原始帧仍按真实字节在追加前检查。正则采用全串匹配，Unicode 长度按标量而非 UTF-16 单元。

事件应用比身份接收更严格：连续 seq、job.state 严格下一 stateVersion、合法前状态或同一非终态的新持久版本；同版矛盾状态、已知终态后的更新、序号/版本缺口均拒绝应用并 job.get 重建。job.progress 仅接受当前已知非终态同一版本。cancelling→succeeded 需要持久完成对账，通知本身不提供此证明，因此先通过 job.get/operation.get 核对；纯路由函数不以一个完成通知自行推断这个竞态成立。

I05 内部错误固定映射为 SEMANTIC_INPUT_INVALID（syntax/query/rule/constraint）、NETWORK_FORBIDDEN、UNSUPPORTED_CONSTRUCT（有限枚举）或 RESOURCE_LIMIT（memory/actions/rounds/frame/page）。这些只是安全解释码，不宣称语义能力已实现或扩展附录 C。输入文本、查询、原值、库异常和 URL 不进入 params；尚不能安全归类者 INTERNAL_ERROR。

registryHash 定义为实际随引擎分发的 registry.json 原始 UTF-8 字节 SHA-256，主进程必须与同版构建预期核验；失配不开放调用。已采用协议的破坏性 schema/错误语义变化必须提高协商版本，不能在相同已发布版本内静默替换。I04 与 I05 打包负责人协调，将同源 schema/registry/dependencies/states 和校验适配器作为明确资源纳入包内并核对哈希；不依赖源码 checkout 路径，也不维护另抄一份协议真相。

retryable 表示条件修复后用户可显式重新发起的提示，不是自动重放授权，也不证明没有提交/发送。写任务先对账 operation/job；读取重试也需当前授权与新请求身份。主进程网关的内部重试另由唯一网关控制，bridge不能叠加。I06的11类需求与下一版安全映射见 ../../reviews/I03/handoffs/I06-error-disposition.md，当前未注册S3方法或私有错误穿透。

I05后续真实接口核对触发的有限错误类别与逐码判据见 [语义边界](I05-semantic-boundaries.md)。semanticInput/semanticResult/semanticWork分别与frame/page/附录E行为预算分开；旧合码在来源未细分前不能直接映射。SHACL参数使用版本化validationProjection与可信资源关联，不能转发任意混合图或验证器选项。此项修订生成新候选，原6f35ffd未外审记录保留，不开放新能力。
