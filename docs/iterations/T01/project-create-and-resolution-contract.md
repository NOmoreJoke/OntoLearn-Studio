# 项目创建与只读 resolution 合同

2026-10-21。本文冻结下一次精确实施审批的私有合同；当前只授权成文。创建、resolution、DDL、公共 DTO、RPC、宿主与位置 IO 均未因此获实施权。

## 1. 固定输入与范围

- 授权：根 `iteration-control/2026-10-21-weekly-release/T01-project-host-read-services-implementation-authorization.md`，7435B，SHA256 `0c96119b2038b1db0d74fc8466926f321c7ebee669cb8949876e417c9e580757`。
- 继承清单：同目录 `T01-project-host-services-fixed-foundation-inputs.json`，12166B，SHA256 `d0c242de45aec840258b7b6f7f4ba4eb6fbdc35b8969a0cf69630d5b0123e1c6`；48 路径只取 `5de3fff8aa02c5d6e577938660e9362936d90550` 的指定组合，不采用整个提交，不转移旧测试维护权。
- 本文树：`.worktrees/T01-project-host-contract-docs`，分支 `docs/weekly-t01-project-host-contract`，Git base 为批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。产品依据实际通过 `git show 5de3fff8:路径` 读取；本 docs 树工作目录的 5f 实现不是上述 48 新组合。
- 本轮全文核验 AGENTS SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、common SHA256 `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`。不重建 Goal，不 stage/commit，不运行产品、测试、构建或 GUI。

需求依据保留 PRD FR-001–006/804：空白创建是后续首个有限分支；示例/模板、复制、重命名、归档、导出、四入口、人类选择与完整恢复未由本合同替代。本文不把空白分支缩成完整 FR-002。

## 2. 实际已有证据与身份

固定 5de 的 `storage.py:259` 创建 `projects` 并 seed Store3 genesis；`job_store.py:489` 同事务建立公开映射；`public_project` 会写，`project_get` 会调用可写 snapshot，不是只读 resolution。`job_store.py` 的全局 `operation_claims` 已记录 Job 受理，queued 可有 claim/完整 context 而完全没有领域 marker。`operation_get` 只查 marker，返回 null 无法证明未受理。`_accepted_job` 校验原 claim、Job context、不可变 snapshot/参数/prepared 及确认；它不按当前 base 重建计划。`format3._history` 从 immutable origin 校验完整 checkpoint/receipt 链。

| 命名空间   | 精确含义与权限边界                                                                                                                                                                      |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 库         | 一份已获真实宿主许可且已由唯一 JobStore 打开的本地 SQLite 文件；一库多项目。服务不接受文件路径，不另开连接，不为检查打开、创建或迁移库。                                                |
| 库逻辑证据 | `libraryEvidenceRef = digest(['ontolearn.library-evidence',1,app_format.migration_id])`；只引用真实 immutable 行。它不是物理文件 ID、跨拷贝唯一 ID 或 FS capability；复制库可保留同值。 |
| 项目       | engine 生成的小写 UUIDv4，作为新项目的内部 `projects.id` 与公开 `public_projects.public`，公开映射 internal 相同。旧 internal/公开 UUID 原样保留，不重编号；名称不作身份，可重名。      |
| 操作       | UUIDv4，在当前物理库全部项目/Job/application 中共用 `operation_claims.operation` 主键。不能把 `projectId+operationId` 当独立可复用主键；跨库同 UUID 不证明同一操作。                    |
| Job        | 已存在的真实 `jobs.id`；由 claim 查出，不要求失响应方已收到 jobId。创建项目本身不伪造一个 Job。                                                                                         |
| 会话/来源  | 原成功 hello 的 hostClientId/engineSessionId；仅由可信调用链提供，不接受 renderer 的 actor/write/confirmed 自报。这些字段证明来源绑定，不证明真人点击。                                 |

**原 dispatch 物理绑定另为必要条件。** 将库 A 逐字复制为 B 后，上表逻辑证据、claim、request、origin 和所有 receipt 均可相同；当前获准读 B 不证明原请求曾发向 B。“当前许可”“原来源”“原 dispatch 物理绑定”是三个分别核验的条件。最后一项必须来自原请求真正 dispatch 时的 Store/位置能力/实例及 generation 事实，不能从当前 Store、migration_id、复制来的 SQL 行或 renderer 输入现场合成。

I06 真实 project-open/create 位置能力尚未到达。`961ce77` 的 metadata/contentIo unsupported、picker 结果、路径字符串、`isAbsolute`、migration_id、库可读或 hello 成功均不授 catalog/create 权。未来宿主能力必须绑定实际 Store/库文件身份、用途、当前 generation/Session 和撤销状态；该不透明能力不落入 renderer JSON，不由本文虚构其可执行工厂。库级 catalog/create/read-receipt 与单项目 read/write 分开。

## 3. 私有接口与原完整业务请求

以下是未来 Python 私有接口合同，不是已注册协议名或第二份公共 schema。所有对象精确键；未来公共化由唯一 canonical owner 单独冻结同一版本。

```text
create_project_request(store, request, *, trusted_origin, dispatch_binding,
                       library_create_scope, reader_limits, limits, hook)
resolve_operation(store, selector, *, original_dispatch_binding, current_scope, limits)
```

两者仅接受已经 Store3+Job3 校验、对账且持同一 lifetime lease 的真实连接。不得把 Store-ready 当 Job-ready。`trusted_origin` 精确为 `{hostClientId,engineSessionId}`，来自当前可信会话；scope 是宿主的真实权限上下文，不是客户端参数。库未获准、ready 失败或 profile 不适用时，不进入服务。

`dispatch_binding` / `original_dispatch_binding` 是私有、不透明、不可由 JSON 重建的可信实证句柄，不放入下列 selector、context 或 receipt。其供方须证明原 operation/requestHash、原 host/Session/generation、原实际 Store 实例与经位置能力核验的物理库身份之间的真实 dispatch 关联；没有捕获过的 dispatch 不能补造。resolution 供方随后必须把原物理身份与当前已许可 Store 的真实文件身份重新对应，拒绝复制库、替换文件或无法证明的别名/迁移。原实例与当前实例不必相同，但实例转换的真实对应证据不能省略。

这不是预先声明已有 I06 句柄/工厂：原事实如何捕获、保留、撤销后验证及跨 Session 重新证明，必须由 I06 实际位置/生命周期合同交付并另获根批准。可以消费真实可信调用链仍持有的原绑定；本合同不为此建立 main 持久意图账本。若原绑定丢失或不能重新证明，resolution 返回 `unknown/physical-binding-unavailable`。当前权限、同正文/同 UUID/同来源或数据库内容完全一致都不能补足该条件。

创建请求精确为：

```json
{
  "requestVersion": 1,
  "operationId": "<UUIDv4>",
  "initialization": { "kind": "blank" },
  "name": "<原始非空名称>"
}
```

无 projectId、内部 ID、文件路径、actor、permission、confirmation、template 内容或客户端 plan。名称须含非空内容，并通过第 7 节完整编码及 reader 相容预检；持久化原始名称，不 trim/NFC/casefold；同名不合并。空白分支固定 `templateRef=null`、`archived=false`、`mode='guided'`、`origin='created'`，对应既有 Store3 创建默认值；其他初始化类型明确拒绝，后续模板/示例保留独立真实 producer 合同。

`requestHash=digest(request)`，使用现 Store canonical JSON/SHA256。传输 request id、timeout、重试次数不参与。新项目 UUID 由 engine 在原 claim 查无之后分配；它不混入调用方 requestHash。原 request/context 的全值必须持久化，不能只留一个无法重建的摘要。

创建返回精确为：

```text
{createResultVersion:1,operationId,projectId,requestHash,receipt}
```

receipt 是第 4 节真实 immutable receipt；没有 `jobId`、虚构 marker、当前假 snapshot 或许可对象。返回成功不自动改变当前项目、发写 scope 或人类确认状态。

只读 selector 分两种：

```text
{resolutionVersion:1,kind:'project.create',operationId,expectedRequest:<完整创建请求>,
 originalOrigin:{hostClientId,engineSessionId}}

{resolutionVersion:1,kind:'job',operationId,projectId,jobId:null|UUID,
 expectedRequest:{projectId,operationId,capability,input,confirmationRef},
 issuedImplementation:<原implementation>,issuedLimits:<原limits>,
 originalOrigin:{hostClientId,engineSessionId}}
```

重复出现的 operation/project 字段必须完全相同。Job `input` 是完整原 jobInput，包含 inputSnapshotId/scope/definitionId/parametersHash/derivedResultIds/preparedPlanRef；不能用当前 implementation、limits、base、重新生成参数或新 confirmation 代替原值。`jobId=null` 是未知实际 jobId，必须从该 operation 的真实 claim 完整发现；非 null 时与 claim 精确核对。上述原来源是待核验的归因条件，不是当前许可；伪造它不能绕过 current_scope。

selector 本身不携带物理归因权，必须另外取得上述 `original_dispatch_binding`；单有本 JSON 不足以关闭 unknown。

## 4. 唯一创建事务、claim 与 receipt

选定复用现表，不扩 kind、不增表、不建立 main 意图账本：

- `operation_claims.kind='application'`、`job IS NULL`、`context IS NOT NULL`，符合固定 `JOB3_CLAIMS` 的原 CHECK/FK。
- 新 context 用唯一 `projectCreateContextVersion:1` 命名空间；与旧 `applicationContextVersion:1` 严格互斥，不伪装成 metadata change。其语义操作是 `project.create`，不是复用一条 metadata claim 当创建结果。
- `app_operations.kind='application'` 使用已有合法值；`app_receipts.payload` 放独立版本 receipt。创建没有领域 `commits`/marker，不推动 domainRevision，不制造另一个 Job/第二 receipt。

新 context 精确字段：

```text
{projectCreateContextVersion:1,libraryEvidenceRef,projectId,project,
 operationId,request,requestHash,
 origin:{hostClientId,engineSessionId,permission:'library.create'},plan}
```

其中 project/projectId 均为同一真实新 UUID；`claim.fingerprint=digest(context)`。plan 精确字段：

```text
{projectCreatePlanVersion:1,projectId,domainRevision:0,
 inputSnapshotId,beforeCheckpointRef,
 beforeCAS:{metadataVersion:0,operationSequence:0},
 afterCAS:{metadataVersion:1,operationSequence:1},
 initialMetadata:{name,templateRef:null,archived:false,mode:'guided',origin:'created'}}
```

plan 必须从完整 request、真实空 genesis 与服务固定效果重新算出；不接受调用方 plan。requestHash、contextHash、planHash、checkpoint/snapshot 内容 hash 各按其原定义分别核对，不互换。

调用 Store 的 `creation` 参数是私有 intent，而不是尚未存在的持久 context：精确为 `{projectCreateIntentVersion:1,libraryEvidenceRef,projectId,operationId,request,requestHash,origin}`。intent 不带 plan/receipt/checkpoint；Store 分支在实际 genesis 已建立后，才据实构造上述 plan 和最终 context。不得先猜一个 checkpointRef，也不得在 Store 之外提前落 genesis 来凑 context。

一次外层 `BEGIN IMMEDIATE` 内的确定顺序：

1. 核当前真实 library.create scope、origin、真实 dispatch binding、输入和预算；按 operation 查全库 claim，先处理第 5 节的原请求。无 claim 时核 commits/rounds/app_operations/app_receipts 等全局占用证据，孤儿证据拒绝，不接管。此时尚不生成新 UUID。
2. engine 分配 UUID，核 projects/public_projects 中均未占用；碰撞安全失败，不把既有项目当新建，不用 INSERT OR IGNORE 吞冲突。按第 7 节在首次写入前计候选 genesis/context/receipt 的实际编码，以及加入此项目后的完整目录、工作区和 reader 验证预算；不相容整体拒绝。
3. 唯一 `Store.commit(...,creation=intent)` 新互斥分支承担正式创建写入。project 参数为该新 UUID，`job=None`、`base=None`；分支自身重核 intent/operation/项目身份及全局占用条件，不混 definitions/manual/mapping/compensate/application 等入口。原普通 domain/application 路径和哈希原样保持。正式服务不得直接在 Store 外写 genesis 或调用 metadata mutator 拼接成功。
4. Store 分支在同连接建立 projects revision0、空 domain snapshot、既有 seed_project(origin='created') 的 app genesis/origin/checkpoint，以及 public_projects 的真实映射。此未提交 genesis 的 metadataVersion/sequence 均为 0，名称为既有 null 默认；不得改写既有 origin 或把最终名称硬塞进旧 genesis 定义。
5. 同事务 INSERT 唯一 application claim（此时 public FK 已满足）；从真实 genesis 核 plan。用创建专属效果初始化最终名称及 metadataVersion1、operationSequence1；draft/learning/assistance 仍为空，domain snapshot/revision 保持不变。形成 after checkpoint。
6. INSERT 唯一 app_operations 序号1和 app_receipts，更新 app_projects 当前 head；逐行读回验证实际 immutable 内容/哈希/FK、完整 genesis→create 链和 CAS。已有同 hash 的坏行整体拒绝并回滚，不覆盖或“修复”。最后一次 COMMIT 后才发布结果。

创建 receipt 精确字段：

```text
{projectCreateReceiptVersion:1,libraryEvidenceRef,projectId,operationId,
 requestHash,contextHash,planHash,operationSequence:1,domainRevision:0,
 metadataVersion:1,inputSnapshotId,beforeCheckpointRef,afterCheckpointRef}
```

`app_receipts.project` 使用内部 UUID；claim.project 使用同值的公开 UUID；receipt 三重互证真实 request/context/plan。beforeCheckpointRef 必须是该项目 immutable app_origins.checkpoint；真实 origin 必须 created、revision0、legacy_operations0；after 是该创建唯一序号1 checkpoint。没有别的早期 operation、领域 marker、draft 或辅助事件。不允许把已存在的 revision0 空项目补认成此次创建。此后 metadata/领域写与当前 head 可继续前进，原 receipt 不随之重算。

## 5. 精确重试与兼容

当前同一库新事务内：先查原 claim，再分配 UUID/构造 genesis。若为创建 namespace，则核 context 精确键/版本、request 全值及 requestHash、原 origin、context fingerprint、公开映射、完整 origin/序号1 receipt 和后续真实链；同时核原真实 dispatch 物理绑定与当前库相符。复制库里的原 claim 不能替代最后一项。

- 同完整业务请求、同原 host/Session 的精确重试返回原结果；不重新检查“项目仍空/名称仍相同”、不看临时 UI token/TTL、不补写第二记录。
- 任意 request 字段、kind、project、原 implementation/limits 或 origin 不同，拒绝身份冲突；UUID碰撞不覆盖。跨 kind 同 operation 不改签。
- 新 Session 的 create 调用即使正文相同也不重放；它只能用第 6 节只读 resolution 恢复已存在结果。若缺原请求或充分归因证据则保持 unknown，不能自动换 operation 再创建。
- COMMIT 后丢响应、flush 失败或取消等待，不把成功项目删掉/回滚成失败；receipt 是持久事实。COMMIT 前失败/真实退出不留项目、映射、claim、snapshot/checkpoint、receipt 的半组；未持久化的 UUID 不对外认作项目。

**DDL 最小决定：本合同不要求 DDL 变更。** `operation_claims` 当前允许 application+非 null context，app_operations 允许 application，app_receipts 为有 FK 的 JSON payload，均能承载以上精确语义。JOB3_SCHEMA/JOB3_HASH、app schema_hash、user_version=3、FORMAT_VERSION=2 不因加分派而撒谎改写。不得 IF NOT EXISTS 补坏库，也不得把已有 claim/context/receipt 转写成新格式。

但“无 DDL”不等于旧 reader 能读取新语义。固定 5de 的 `_validate_job3`/`applications.claim_context`/`format3._history` 会拒绝新 namespace。未来实现须显式扩**语义验证**：Job3 dispatcher 和 mixed-history dispatcher 识别精确新 tag 后交创建 validator；旧 applicationContextVersion1 仍调用原严格 validator，Job context/原指纹不改。新/旧 namespace 不能互带标签或回落为宽松 JSON。新创建记录写入后，旧格式3程序必须安全拒绝，不能静默忽略；默认格式2仍拒绝实际3。未来启用需同候选 reader/writer 与有限能力版本绑定，不能仅靠 schema hash 相同宣称兼容。发现必须改变任何 DDL/版本/能力范围时，保反例并重新申请，不能在实施中补一张表。

`JobStore.apply_application` 的既有原 claim 重试入口也必须显式辨别 namespace：遇相同 operation 的 `projectCreateContextVersion:1` 创建 claim，先返回 identity-conflict，不进入旧 `applications.claim_context`，不当成坏 metadata 输入或放宽回落。反向创建入口遇旧 application/Job claim 同样先 identity-conflict。此责任在已列 job_store.py 内，四条未来产品路径仍足够，不需改 applications.py。

## 6. 只读 resolution 的充分证据与 unknown

resolution 不调用 create_job/create_project/commit/reconcile_jobs/snapshot/public_project，不运行 worker，不接受路径，不触发迁移，不补 marker/映射/receipt，也不做“安全重试写”。在当前许可与原 dispatch 物理绑定分别核验后，使用一次全新只读事务读取真实 claim、完整 Job/context/参数/snapshot/prepared/confirmation/receipt 及必要链；拒绝加入调用方未知活动 writer 事务，避免未提交状态变成恢复事实。SQLite authorizer 禁全部写仍须能运行。启动期间 reconcile 是既有独立生命周期步骤，不由 resolution 暗中执行。

Job 成功判据：claim 的 project/kind/job/fingerprint 与 jobs 行和 `digest(fullContext)` 一致；原 expectedRequest/issuedImplementation/issuedLimits 与完整 context 逐值相同；调用既有只读 `_accepted_job` 等完整校验，不能只比较摘要、DTO 或某个 JOIN。正式 ChangeSet 的 origin 必须由真实 immutable prepared envelope +确认原回执交叉核验，不能从当前 Session 补出原来源。旧普通 Job context 未记录 host/Session 时，不能补称原 Agent/原 host 已归因。

| 真实证据                                                                                 | resolution 结果与恢复动作                                                                                                                   |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| queued/running/cancelling Job 的 claim、完整 context、原请求及来源均足够，marker 为 null | `resolved-job`；返回该真实 Job，表示已受理，绝不解释为未提交所以再 job.create。running 是否能继续仅由已有 Coordinator 生命周期决定。        |
| 已 terminal 的完整 Job                                                                   | `resolved-job`，返回同 jobId/state/stateVersion/resultRef/error；成功 receipt/marker 必须互证；失败/取消可以无 marker。不得把失败自动再跑。 |
| 创建 context+序号1 receipt+完整历史充分，当前许可足够                                    | `resolved-create`，返回原 createResult 与 recoveryOnly=true；不再次创建，不自动选择项目/发 scope。                                          |
| claim 缺失或目标库不匹配，只有 null marker/客户端 remembered/同名项目                    | `unknown/no-evidence`，绝不返回 notAccepted，也不自动重放。                                                                                 |
| claim/context/Job/prepared/receipt 缺行、损坏或不完整，且 Store 仍可供读                 | `unknown/incomplete-evidence`；不拼接新证据、不补写。如果 Store 打开本身已因损坏失败，走既有启动/存储失败，不能声称仍可 resolution。        |
| 原来源未持久记录/无法充分对应 originalOrigin                                             | `unknown/origin-not-recorded`；可在已许可项目中另用真实 job.get/list 展示其受理状态，但不能据此关闭“这次原意图”的 unknown 或猜 Agent 归因。 |
| 真实完整正文与 expectedRequest 不同，或已知 jobId 不同                                   | 身份冲突；不返回其他操作内容，不把异请求认作原请求。                                                                                        |
| 当前库/项目 read 权不足或已撤销                                                          | 权限失败，先于内容返回；原 Session 曾有权限不沿用。不得通过猜 UUID/operation 探查另一项目。                                                 |

以上所有 resolved 行均以原 dispatch 物理绑定可重新证明为共同前提。缺失、伪造或无法对应当前 Store（包括 A→B 逐字复制）的绑定，返回 `unknown/physical-binding-unavailable`；即使 claim/request/origin/receipt 全相同，也不能用当前 B 的许可关闭原意图 unknown。此时在当前许可下展示 B 的真实历史仍是另一项只读行为。

有限返回 union：

```text
{resolutionVersion:1,status:'resolved-create',operationId,projectId,
 originalRequestHash,createResult,recoveryOnly:true}
{resolutionVersion:1,status:'resolved-job',operationId,projectId,job,
 originalRequestHash,recoveryOnly:true}
{resolutionVersion:1,status:'unknown',operationId,
 reason:'no-evidence'|'incomplete-evidence'|'origin-not-recorded'|'physical-binding-unavailable'}
```

返回 job 是按当前严格同版 canonical 校验的真实 DTO，不回整个 context/领域 before/after/原值/任意SQL文本。originalRequestHash 对 Job 为完整原 job.create 业务请求加原 issuedImplementation/issuedLimits 的 canonical 摘要；不是 Store plan fingerprint，也不是整个 Job context fingerprint。创建则是第 3 节 requestHash。

当前许可按真实查得 project 再核；对原项目未知的创建只读恢复，须有该实际库的 catalog+creation-receipt-read 窄能力，不能由 operationId 自行授予。恢复得到 projectId 后仍需真实项目选择/单项目 read/write scope。跨 Session 必须重新证明原 dispatch 物理绑定与当前实际库对应；若绑定已丢失或不可恢复，只能展示当前许可下的真实持久记录，不能返回 resolved 来关闭原意图 unknown。新 Session 的 current_scope、数据库内原 request/origin 或 migration_id 不充原物理事实。回应还须绑定此次 current_scope/原库/原操作，不改变新 generation 的选中项目。普通 Job 因缺原来源保持 unknown 是明确历史缺口；未来如要求其充分归因，必须另冻结新 Job context 版本、真正生产来源与迁移兼容，不改写旧 context/hashes。

**完整发现：**已知 operation、未知 jobId 时按唯一 claim 发现实际 jobId，再完整验证，不能只找最近16个 Job或只找有 marker 的 Job。operation 也丢失时，既有全量有界项目目录/Job 列表可展示真实持久记录供用户查找，但名字/时间/最后一条不是原意图归因。库有多个候选时全部明确展示或整体资源失败，不静默选一个；没有充分选择/原请求继续 unknown。不新增 main localStorage/JSON/SQLite 意图账本，也不把内存“已发送”当持久受理证据。

## 7. 预算、错误、取消与退出

此处为下一机制的有限工程 guard，不是 Q5 容量或性能结论。单位全部为 canonical UTF-8 bytes；字符串须为合法 Unicode scalar，无 surrogate/NUL；不改原名称字符序列。先计形状/标量/编码预算，再复制/持久化，不用先深 clone 一个超预算对象。

| 对象/操作             | 固定预算与超限行为                                                                                                                                                                                                                                                                                        |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 创建 name             | 1–4096 UTF-8 bytes，至少一非空白字符；仅工程 guard，不决定名称唯一性。                                                                                                                                                                                                                                    |
| 完整新 create request | ≤16384 bytes；context/plan 合计 ≤65536；receipt ≤16384；成功返回 ≤32768。超限在写前整体拒绝。                                                                                                                                                                                                             |
| resolution selector   | ≤262144 bytes，与实际 profile frame 更小值取小；拒 unknown keys/宽松 coercion/NaN/非 safe integer。                                                                                                                                                                                                       |
| resolution 证据读取   | trusted caller 显式给 maxEvidenceBytes，有限正 safe integer且≤67108864，无无限默认。SQL先计每个将读的唯一实际行的 UTF-8 byte长度，包含完整 context及引用的snapshot/参数/prepared/确认/必要checkpoint链；总预算不足时整体资源失败，host保持 unknown，不截断后宣称充分。旧历史不强行迁移/删字段以适配预算。 |
| resolution 返回       | ≤min(131072,真实maxPageBytes,真实maxFrameBytes减实际envelope预算)。本单 operation 接口不分页一个 Job/context，不截断字段；过大明确资源失败。                                                                                                                                                              |
| 留存                  | 服务不保留新持久/内存意图账本，不新增游标或跨请求长事务。每次只读 transaction 后释放临时证据；不回收真实 immutable历史。                                                                                                                                                                                  |

**创建名称初筛不是充分接受条件。** 4096 个 ASCII `x` 满足上述原 name 字节界，但完整 `initialMetadata` 按现相同 canonical 规则是 4178B，已超过当前 `ReadLimits.metadata_bytes=4096`；引号、反斜杠及控制字符的 JSON 转义还会扩大编码。因此 writer 必须在首次写入前核验下面全部持久投影相容条件，失败整体 resource-limit，不截名、不归一化、不先创建再让 reader 拒绝，也不修改或提高本阶段读取服务限额。

`reader_limits` 必须来自可信宿主选定的实际 `ReadLimits` 策略，不能由 renderer 放大。未来 creator 只读消费其既有定义/数值：完整 `canonical(initialMetadata)` 的 UTF-8 长度必须 ≤实际 metadata_bytes（当前默认4096）；真实 UUID、revision0、metadataVersion1、sequence1和实际 afterCheckpointRef 组成的完整目录行必须 ≤catalog_row_bytes（默认8192）；用同项目真实 inputSnapshotId、指定合法 editor 的 missing draft 组成初始 workspace，须满足 identity_bytes（默认512）和 workspace_bytes（默认278528）等相关字段/整体编码界。不得只验 name 自身或减去一个未证明的固定余量；完整 JSON 转义、字段名和标点都计入。

还须在同一创建外层事务、任何 INSERT 之前，对加入候选项目后的**完整库集合**计算 reader 的结构/持久预算：现有项目数加1 ≤projects（默认256）；真实已有行加候选全部 genesis/public/claim/context/checkpoint/operation/receipt 行，按 reader 同一 SQL 字节口径累计 ≤validation_rows（默认16384）和 validation_bytes（默认33554432）；按其既有 `total_bytes*(1+app_operations行数+snapshots行数)` 工作 guard ≤validation_work（默认536870912）；schema/table/column 界不变。完整新目录所有实际编码行及分隔符的快照预算须 ≤snapshot_bytes（默认1048576），新目录行/整页须能在实际 page_bytes（默认131072）和有效 page_items 下完整交付，单目录 reserve `768+项目数*(catalog_row_bytes+64)` 须能放入 retained_bytes（默认8388608）。候选编码/行集合在写前构造并计费，Store 实际写后逐值验证与候选相符；任何差异回滚。不得为预检调用会拒活动 writer 事务的 `ProjectHostReader.catalog_start/workspace`，也不额外打开读连接或补 snapshot。

当前 reader 按固定 page_size 取整组行，不能假定它会因 byte预算自动少给行。页预检须覆盖 `1..page_items` 所有有效 page_size 的实际分组/offset，计完整 page 的字段、93字节非末页cursor、snapshotId、total、offset、JSON转义和分隔符，或使用经证明不小于这些页的编码上界。初始 workspace 对所有合法 editor 的 identity_bytes 最坏编码界预留 missing-draft开销，不能只用一个短测试editor证明。写前候选及hash计算只用于预算，不充当真实已存在的checkpoint证明；最终context/receipt仍按第4节从Store实际genesis及写后记录构造、读回并逐值核对。

这些条件保证新增持久内容与同版现 reader 的实际读取政策相容；旧库已超该预算时创建也整体拒绝，不自动修库。目录增长本身仍有明确工程界。暂存槽位被占满、已有快照剩余留存、TTL、取消等当前 reader 运行资源保持原有限失败语义，不能把持久预算相容宣称为任何占用状态下目录永不失败。未来 reader 政策或 workspace 形状若变化，应重新核相容再授 writer，不复制第二套可独立漂移的 ReadLimits；本修订不改当前 reader、冻结实现文档或新增产品路径。

证据计费应避免同一行反复扣费，但不能漏掉需要解析的引用。既有 Store/Job 启动校验与完整 ChangePreview 已有分配风险不能由本 guard 倒称已解决；将来实现和当前宿主性能须据实测量。

私有有限失败 reason：invalid-input、permission-denied、identity-conflict、resource-limit、storage-busy、storage-failure、unsupported-profile。unknown 是上述正常有限 union，不能替代权限/明显异请求错误。本合同不注册新错误码；未来公开适配由 canonical owner 使用既有安全 code/params 或单独申请。路径、异常字符串、SQLite文本、原名称和完整 context 不进入展示错误。初始化前失败沿已有 startup 类型/首因/逐资源 cleanup 链；ready 后失败用正常严格 profile 业务错误，不能伪造 startupFailure。

取消只影响尚未进入服务的调度或当前等待。同步 SQLite commit 内不承诺接受新 cancel；既已接受的事务必须按真实 commit/rollback 结果收口，不依据 stdin 到达时间决定。UI取消等待/超时不等于数据库取消；进入 unknown 后只能只读 resolution。COMMIT 后取消不会删除新项目或倒写失败。真实进程退出前未 commit 全组回滚；commit 后失响应恢复原 receipt。单独读 resolution 被取消/断连只丢本次返回，不改变 Job/claim/项目。不得新增生产 fault env，故障 fixture 和真实 OS 退出证据分开。

## 8. 最小将来路径与审批门

当前授权的只读 `project/project_host.py` 和其新测试不需为本合同改动。将来精确实施的最小私有集合为以下四条产品路径，另两条新专属测试；本阶段全未授权实施：

| 路径                                                                   | 必要责任                                                                                                                                                         |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 新 `packages/engine/src/ontolearn_engine/project/project_lifecycle.py` | 创建 request/context/plan/receipt 的唯一 validator与 Store委托效果；只读 resolution/预算/归因，复用真实 Store/claim/Job校验。无路径IO或第二writer。              |
| `packages/engine/src/ontolearn_engine/storage.py`                      | Store.commit互斥creation分支、唯一外层事务内genesis初始化；原方法默认/format2/旧写hash不改。                                                                     |
| `packages/engine/src/ontolearn_engine/job_store.py`                    | 受信创建薄适配/原claim优先；新namespace的Job-ready分派；旧apply_application原claim重试先拒创建namespace为identity-conflict；只读resolution复用完整accepted校验。 |
| `packages/engine/src/ontolearn_engine/project/format3.py`              | origin→创建seq1→后续完整链的专属效果/receipt验证及单CP load，旧origin和旧application逻辑不变，不改DDL。                                                          |
| 新 `packages/engine/tests/test_project_create_contract.py`             | 原子创建、兼容、幂等、逐边界异常/真实退出重开证据。                                                                                                              |
| 新 `packages/engine/tests/test_project_operation_resolution.py`        | 真queued无marker、来源/当前许可、完整发现、损坏/资源/零写证据。                                                                                                  |

不需要先改 applications.py、worker.py、protocol.py、resources.py、旧tests或build/依赖。若实现证明上述最小集合不足，先留反例/具体路径再申请。正式 RPC/DTO将来另列 canonical `schema/registry/fixtures/binding-regressions`、Py/TS helper/消费导出及coordinator必要路由；本合同不提前注册。真实位置和宿主生命周期将来涉及 I06 能力供方、main/index/engine/task-service，以及实际需要的preload/UI原owner，须另获明确合同/阶段权，不把本内部服务许可扩成对任意文件的首次IO。

审批前必须确认 I06真实库用途能力已交付且由根批准消费、当前库/项目scope如何签发撤销、原dispatch物理绑定捕获与跨Session重新证明、创建/选择的真实人类触发与generation绑定。该前置未到时，本合同可被独审，不能发明实授capability、把新库/空库开库迁移当用户已批准或直接启用默认生产3。

## 9. 将来必须实际验收

1. 真实新建空白项目原子出现域/app genesis、公开UUID、名称、唯一claim/receipt；domainRevision0、metadataVersion1、sequence1；无Job/领域marker。重开UUID/receipt稳定，同名两个项目不混。
2. 创建每个持久边界前后分别异常、实际SQLite写失败、真实子进程退出；完整dump/行集合证明回滚或完整commit，无半项目。commit后丢响应/再次同业务请求只返回原结果；UUID/operation跨kind碰撞、孤儿证据、同hash坏旧行均拒绝且不修库。
3. 旧format2默认路径和旧Job/application哈希不变；固定旧格式3 reader遇新创建namespace安全拒绝，新reader读取旧完整/legacy-partial origin不重写历史。对schema hash不变但语义reader不兼容给真实反例，不伪称双向兼容。
4. 真 queued claim无marker、running/cancelling/三终态、未知jobId的claim完整发现、原receipt失响应/当前base推进/结果cache回收均如实投影；跨项目/库/Session/正文/implementation/limits/来源错配，当前许可撤销，缺行/坏context/伪receipt/无origin分别有限失败或unknown。
5. resolution 在 SQLite authorizer禁止所有写和dump完全相同下完成；不得调用补snapshot/映射或对账写。预算边界±1、旧大context、所有必要引用累计、无截断/无默认无限；失败和取消不改任何持久状态。创建另验4096 ASCII名称→完整metadata4178B必须写前拒绝、含引号/反斜杠/控制字符的转义扩张，以及完整metadata4096B边界、目录行/快照/页/workspace和全库validation预算边界；合法创建在相同reader政策及可用资源下完整catalog/workspace可读，非法候选完整dump不变。旧apply_application以创建operation重试精确报identity-conflict，不进入旧claim_context。
6. 新generation不得被旧Session迟到结果切换项目；跨Session只有原dispatch物理绑定可重新证明才允许关闭原意图unknown，否则只展示真实持久记录且零自动重放。逐字复制库A→B后同claim/request/origin/receipt不能靠当前B许可误认；丢失、伪造或拿当前Store重新合成原绑定、generation/operation/requestHash错配均unknown。operation也丢失的完整目录/Job发现不得冒认归因。scope fixture只证明机制，真实FS/人类点击/平台和公开链仍需对应owner独立证据。

以上均为待实施验收，本轮没有运行或宣称通过；当前只读服务的独立实现与全check另有自己的候选/证据，不由本文代替。完成文档后交另一agent独立审查，再由根决定下一次精确授权。

## 10. 本次独审意见处置

输入为主线独立报告 `docs/reviews/T01/project-host-read-services/creation-resolution-independent-review.md`，10182B，SHA256 `402c0010938b41692d981d2630eac5aa76a3901259a94e1f77118233e3238724`，已全文实读；初稿30208B/SHA256 `d2d469acdc401f01fec3269647fcdeefb66dc0ca2ddfbf0717f663508f410675` 保存在 `/tmp/t01-project-create-and-resolution-contract-d2d469ac.md`，字节哈希核验相同。

- P2-CR-01：§2/3/5/6/9添加与当前许可分离的真实原 dispatch 物理绑定，明确复制库反例、跨Session失证unknown和I06真实供方前置；不建main持久意图账本。
- P2-CR-02：§3/4/7/9添加完整 metadata/目录行/workspace及reader全部相关持久预算的写前相容预检，保留4178B反例；不改reader或扩大路径。
- 原报告最小路径提醒：§5明确旧 apply_application 原claim重试遇创建namespace先identity-conflict；§8的 job_store.py 责任须包含此项，仍仅四条未来产品路径。

本节记录合同修订，不替独立审查人关闭意见，也不授创建/resolution或位置能力实施权；修稿身份交主线逐字复制后再独审读回。
