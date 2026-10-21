# I06 主进程命名接口与材料边界

2026-10-21；本文对齐开发分支固定实现 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6`，其中已含契约提交 `69dd44d`。批准依赖仍为 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`；不采用未批准 I05 候选。文件名保留以维护历史链接，原“待注册提案”已由本实现对齐稿取代。完成度由 [status.md](../../reviews/I06/status.md) 唯一维护。

当前真实定义来自 `packages/contracts/src/index.ts`、`src/v2.ts`、`v2/schema.json`、`registry.json`、`errors.json`；实现来自 `model-gateway/model-service.ts`、`GatewayApplication`、main index、preload 和 App。本文与 [合成案例](narrow-interface-examples.json) 不是第三份运行协议；案例校验范围与记录见 [对齐检查](../../reviews/I06/interface-alignment-review.md)。

## 公共调用与真实权限

12 个方法只注册在 `registry.mainRuntime/mainCapabilities`，owner 为 main、`agentEligible=false`，不进入 Python JSONL 方法表。preload 每项映射固定 IPC channel；renderer 不获得通用 method/URL/headers/body 转发、secret 读取、vault 或 audit 查询。main 先核验 sender/webContents、mainFrame、可信文档，再用实际校验器验证参数。可信 frame 不等于已同意外发，预览与明确确认是独立动作。

`contextId` 为 main 签发的当前项目 UUID。除 `getModelAccessStatus({})` 外均必填；请求不能自报 projectId。项目切换关闭旧 application，撤销旧 context、选择、预览、grant 和内存调用。异步读取/配置保存后复核 context，不把旧项目响应交给新 UI。同一 profile 由 `app.requestSingleInstanceLock()` 保证一个主进程 owner；窗口重建保留 main 服务，UI 仅读回状态及既有 invocation 结果，不确认、不重发。main 重启不恢复调用或授权，audit 恢复也不重放。

## 12 个已实现方法

所有对象严格拒绝额外键；无隐式转换或 undefined 占位。结果采用 `BridgeResult<T>`：`{ok:true,data:T}` 或 `{ok:false,error:SafeError}`。UUID、Hash、来源 result DTO 均复用当前契约定义；`validateModelParams/Result/Reply` 负责严格形状和语义，`matchesModelResult` 另核对本次请求与响应身份，真正的项目/目录/授权权限仍由 main 服务核验。

| 方法                         | 参数                                                                          | 成功结果与行为                                                                                                                                                                                                                                       |
| ---------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `getModelAccessStatus`       | `{}`                                                                          | `{availability,contextId,projectId,privacy,configurations,selections,invocations}`。无 context 时两身份均 null，unavailable/local、选择与调用为空；配置只含非秘密显示数据。                                                                          |
| `configureModel`             | `{contextId,configurationId,configurationVersion,displayName,endpoint,model}` | `ModelConfiguration`。新建必须两个 null，更新必须两个 UUID；version 是预期旧版本，不能省略或混合 null。main 检查真实旧版本并持久替换。                                                                                                               |
| `storeModelCredential`       | `{contextId,configurationId,configurationVersion,secret}`                     | `{configurationId,configurationVersion,credentialState:'configured'}`；返回新 version。写前和异步加密后核对预期配置版本，principal/ref/credential version 由 main 生成，不回显 secret。                                                              |
| `setModelPrivacy`            | `{contextId,privacy:'local'\|'minimal'\|'project'}`                           | `{privacy}`；实际模式改变清预览/grant，local 默认且拒绝外发。字段名为 privacy，不是旧稿 mode。                                                                                                                                                       |
| `selectModelResults`         | `{contextId,results:{resultId,selection:'current'\|'historical'}[]}`          | `{selections:ModelWholeResultSelection[]}`；0–64 个不同 resultId，空数组清空。逐份真实读取，批次成功才替换；失败释放临时材料并保留旧选择。替换/清空释放旧选择，定向取消依赖它的调用。                                                                |
| `getModelFieldCatalog`       | `{contextId,resultId,selection}`                                              | `{catalogId,metadata,selection,fields}`；从固定可信 main 模型及实际完整 Store 结果产生 1–16 个字段描述，无正文值。未知模型/shape 拒绝。                                                                                                              |
| `selectModelFields`          | `{contextId,catalogId,fieldIds}`                                              | `ModelFieldSelection`；1–16 个唯一目录 field ID，必须包含 requires 传递依赖闭包。真实重读后只投影选中字段，成功替换旧选择。                                                                                                                          |
| `previewModelExplanation`    | `{contextId,configurationId,selectionIds}`                                    | `{previewId,configurationId,configurationVersion,endpoint,model,principal,purpose:'explain',privacy,selections,authorization}`；1–64 个唯一选择，重读完整来源。authorization 为 `{state:'required'}` 或 `{state:'reusable',grantId}`，由 main 判断。 |
| `confirmModelAuthorization`  | `{contextId,previewId}`                                                       | `{grantId,configurationVersion}`；仅接受本 context 尚有效的一次预览，由用户明确确认触发；不自动确认 reusable 预览。                                                                                                                                  |
| `startModelExplanation`      | `{contextId,configurationId,grantId,selectionIds}`                            | `{invocationId,state:'running'}`；立即返回 main 生成 ID，后续来源/授权/网络失败从 outcome 读取；返回 running 不表示已发送。                                                                                                                          |
| `getModelExplanationOutcome` | `{contextId,invocationId}`                                                    | 独立状态 union，见下；仅查询 main 已登记调用，不新增发送。                                                                                                                                                                                           |
| `cancelModelExplanation`     | `{contextId,invocationId}`                                                    | cancelling 或既有 completed/cancelled/failed；没有 running 返回分支。取消只作用于该调用，不能承诺远端未收到。                                                                                                                                        |

`ModelConfiguration={configurationId,configurationVersion,displayName,endpoint,model,credentialState}`；credentialState 为 missing/configured/unavailable。displayName 1–128 字符；model 匹配 `^[A-Za-z0-9._:/-]{1,128}$`。公开 endpoint 必须 HTTPS、最长 2048 字符，不含 userinfo、query、fragment、空白/反斜杠/控制字符；输出必须是 main 规范化 URL。私有 loopback policy 不由公开参数开启。

`ModelWholeResultSelection={kind:'whole-result',selectionId,metadata,selection,bodyHash,rowCount,byteCount}`。`ModelFieldSelection={kind:'fields',selectionId,metadata,selection,catalogId,fieldIds,fields,projectionHash,rowCount,byteCount}`。两类均返回实际材料行数 0–1024 和 UTF-8 字节数 0–65536；超过上限整体拒绝，不截断。Hash 仅作实际副本一致性检查，不是外发许可。metadata 为当前 result DTO，含所选 result/input/implementation、读取时 state、staleReason、payloadStatus 与 historicalSelectionRequired，不增加自报 provenance。

字段描述为 `{fieldId,label,type:'string'|'number'|'boolean',nullable,requires:UUID[]}`，label 1–128 字符；requires 是该字段的传递依赖 field IDs。目录及选择结果均校验唯一 ID、引用存在、无环；字段选择结果的 fields 必须对应全部 fieldIds 并包含依赖。UI 展示描述/依赖，main 验证实际闭包，不能仅靠 UI checkbox。

```ts
type Outcome =
  | { invocationId: UUID; state: 'running' }
  | { invocationId: UUID; state: 'cancelling' }
  | { invocationId: UUID; state: 'completed'; text: string }
  | { invocationId: UUID; state: 'cancelled'; externalEffect: 'unknown' }
  | { invocationId: UUID; state: 'failed'; error: SafeError }
```

completed 文本最多 1MiB 实际 UTF-8 字节，renderer 以文本节点展示。transport 使用 fatal UTF-8 解码，非法字节拒绝，不以替换字符伪造成功；公共校验也拒绝非法字符串。取消不使用公共 CANCELLED 错误；cancelled 分支没有 error/text 字段。

## 配置、凭据、缓存与错误

endpoint 改变生成新 configurationVersion、清除旧凭据 binding，旧 endpoint 的 key 不随目标迁移，需重新录入。model 改变也更新配置版本并撤销授权，但同 endpoint 可保留凭据；纯 displayName 改变保留同一身份/version。凭据轮换生成新主体/ref/version 和配置版本，清预览/grant。全局配置最多 32 项，使用串行 owner 与持久 CAS；不确定写入失败使模型服务 unavailable，关闭旧 context/core 配置，不能继续用旧内存授权掩盖持久更新。不可变旧密文受内部 admission 上限保护，不自动回收，产品回收策略另行设计。

main 项目 context 持有选择、目录、预览、grant 与 invocation ledger。目录缓存保护当前选择、淘汰未使用目录；当前选择替换时释放完整祖先引用，依赖调用取消。ledger 只保留 4 个活动和最多 64 个终态；终态按调用登记（启动）顺序在终态集合中淘汰，旧 ID 不重建。UI outcome cache 仅用于同 context 的结果显示，项目切换清理，恢复不触发确认/发送。设置与 grant 缓存均以真实规范配置、范围、privacy、purpose 绑定，renderer 不能请求 reusable。

当前 10 个精确公共网关错误均为 `GATEWAY_` 加内部名，messageKey 以 errors.json 为准、params 严格 `{}`、retryable=false：

| 内部名                 | messageKey                    |
| ---------------------- | ----------------------------- |
| INVALID_INPUT          | gateway.invalidInput          |
| LOCAL_ONLY             | gateway.localOnly             |
| AUTHORIZATION_REQUIRED | gateway.authorizationRequired |
| SCOPE_EXCEEDED         | gateway.scopeExceeded         |
| CONFIGURATION_CHANGED  | gateway.configurationChanged  |
| CREDENTIAL_UNAVAILABLE | gateway.credentialUnavailable |
| AUDIT_UNAVAILABLE      | gateway.auditUnavailable      |
| REDIRECT_REJECTED      | gateway.redirectRejected      |
| MODEL_UNAVAILABLE      | gateway.modelUnavailable      |
| RESPONSE_LIMIT         | gateway.responseLimit         |

格式错误用固定 `INVALID_REQUEST/protocol.invalidRequest/{field:'params'}/false`；合法但失效的 context 在当前 service 中为 GATEWAY_AUTHORIZATION_REQUIRED。实际 EngineError 经 safeError 保留已注册来源错误及其受限参数；未知/非法错误降为 INTERNAL_ERROR。不透传 upstream body、路径、单元格、堆栈或凭据。结构校验接受某个错误形状不证明该运行分支已触发。任何 retryable 均不授权 bridge/重连自动重发；core 仅对 429/503 最多一次内部重试，每次重新检查并先持久审计，拒绝重定向。

## 来源、字段证明及发送窗口

`StoredResultSource` 固定 main 项目与 EngineSupervisor，只调用批准的 project.get/result.get/job.get/result.page；完整分页、producer/job/input/参数/实现版本与重读一致性缺一即拒绝，不开第二个 SQLite writer。默认 runtime-only；当前批准基线业务 producer 仍 design-only。有限字段模型只能由 main 注入，普通生产 `fieldModels=[]`。index 的有限策略仅在既有绝对 fixture path 与同值 env、可信 main 启动夹具、unpackaged/test runtime 条件下启用 `i06-finite-probe-v1`，不是 renderer 数据或标签选策略。它绑定已批准 test.read echo worker 的精确 implementation/uv.lock；静态 dependsOn 为合成 policy，不是通用生产列溯源，更不是 I05 未批准执行语义。

投影器验证平坦 scalar/tag/精确宽度、唯一模型及完整字段配置。catalog 绑定具体 result/job/正文副本供重新读取；授权 scope 另绑定模型完整 digest、项目/producer/定义/输入/参数/执行版本、字段与依赖及有序实际值/行身份，允许同源且选中字段不变的新真实 worker 结果复用原 grant。最终正文只带允许的来源摘要、选中字段描述和值，行位置改用投影内密集 ordinal，不外发原 rowId/ordinal、未选列及其派生值、完整参数/输入 hash。任意 text 加来源标签不能证明字段来源；field/tool/history/summary/error 仅从已允许结构化投影重建，无法证明的任意文本拒绝。

A-03 原要求是授权选中字段后触发真实工具，其其他列不能进入下一次请求；有限真实 Store/worker 输出、可信 main 模型/目录/投影和实际 receiver 字节可以证明 M0 有限范围。whole-result、hash、random UUID 或自报 provenance 不能替代。无需完整 M1 CSV 单元格溯源、恰好两个新 API 或 I05 编号前置；本实现选择这两个字段方法是接口决定，不是原需求加码。I05 特定真实业务材料须在其新执行语义实际批准合并后另绑定和重验，不能固定未批准 `i05-finite-3` 为生产来源。

明确历史选择是 PRD D/F 已有语义；展示实际版本、读取时状态和历史身份，current 不能静默降为 historical。检测到内容或来源身份变化保守拒绝，evicted 内容不重算冒充旧结果。最后完整异步读回到 socket 之间仍存在跨 Store 变化观察窗口；只承诺发送用户所选版本的已核验副本及其读取时状态，不声称发送瞬间仍 current。core 在实际发送边界重检授权、配置、凭据及材料范围。所有 Store writer/socket 原子 live-current lease 不是原 S3 自动前置，只在新增持续 current 保证时另审。

## 验证归属

本对齐只实际执行同版四个 contract 校验器及文档格式/ID 保全，不启动服务或平台。已有有限私有链证据按 [字段 manifest](../../reviews/I06/evidence/finite-fields-20261021.json) 原 source hash 引用；该阶段完整正文有代码断言和执行 receipt，但独立 probe 未归档成功 HTTP 原正文，不能声称独立重扫过归档 body。新正式链应在忽略测试证据中保存仅合成 receiver 完整 body 并 hash，不保存 headers/真实 secret/业务数据，也不进入产品日志。

完整 main/preload/UI/safeStorage/Linux 新运行、其他平台、实际可用保存/日志/窗口联验及完整 S3 指定双方新审、PR/CI/远端合并以 status 为准；本文件不将开发分支实现或历史私有平台结果写成这些已通过。当前无导出入口是能力事实，不能虚构导出器或导出测试。Q9 provider 协议未决不阻塞既定合成链，也不因合成 wire payload 就选定真实 provider。
