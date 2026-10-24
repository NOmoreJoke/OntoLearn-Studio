# T01 business3 / startup 唯一下一阶段实施计划

本页是提交总控审批的精确实施计划，不是实施授权。沿用已闭合的 [r1](business3-ready-startup-contract-r1.md)、[r2](business3-ready-startup-contract-r2.md)、[r3](business3-ready-startup-contract-r3.md)，不重开原 R1–R4 / P2-RAW-1024。四文件未来维护虽已生效，startup、独立新码/schema、显式 runtime3 与 ready 仍未获准实施；本次仅新增此文档，没有运行产品或测试。

## 1. 实际输入、责任与实施目标

入口核对基于材料提交 `bf04169d400378084e8fea87b6a8e3915135987d`；交稿时实际 HEAD 已为纯证据补封 `27a0d17149ffdaf013233b4ac7fc861ccb0e38c2`。主线材料及其证据不属于本计划改动。已只读核对真实 Store / JobStore、Coordinator.request/serve、Python main、canonical TS/Python/schema/registry/errors、main supervisor/reader/factory/task-service 和固定呈现函数。未消费未批准 I05/I06 实现。

实际核验四条新生效路径仍分别为：

| T01 唯一未来维护路径                                 | 读取时 SHA256                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------------ |
| `apps/desktop/src/main/jsonl.ts`                     | `12c0437f66b73b0aa88617b551394f6771529d2e5f307a5ab2765feb1fc05357` |
| `apps/desktop/src/renderer/src/task-presentation.ts` | `5ddcd33a9e00e367597d20d8d2449062df577a1f3cdb53dfae2318a173858751` |
| `apps/desktop/src/main/task-service.ts`              | `8d513fe5a25a4dc82839cdc6200ae1972b7743620175bc7e309834a712655122` |
| `apps/desktop/src/main/index.ts`                     | `7df36c6d51a63de4ba6a302cb5063affffeb2dd6a1d9598bec29da8b09ea6bc9` |

`apps/desktop/src/main/engine.ts` 已有 T01 责任，读取时 SHA256 为 `f7aee77b0bf558dd8e6a375d5524d3cc55817689bdde8ae07556f1e2456633b4`。操作 common 已实际全文读取，SHA256 `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0`；生效记录明确 `startupImplementationAuthorized:false`。

待批准的唯一目标：默认生产2完整保留；仅受信内部显式入口选择3，在真实 Store3 + JobStore3 + reconcile 完成后协商业务3，并把限定启动失败从原 stdout bytes 一直传到既有命名 bridge 和固定文案。仅原已实现能力，不新增 source/learning 方法，不把测试 Job 或私有应用 CAS 宣称为新产品能力。

## 2. 精确改动清单与出口

以下为申请的产品改动集合，未列路径不施工。符号名是本阶段拟冻结的内部接口名称，不是已经存在的实现。

| 路径                                                  | 唯一必要改动                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/contracts/v2/schema.json`                   | 新增独立 `$defs/startupFailure` 与 `$defs/error_startup`：仅 kind/diagnosticVersion/engineSessionId:null/registryHash/error，严格字段；四个有限错误分支，精确 params。与已有 error2/error3、envelope2/3、null-session hello 错误集合分离。已有业务3请求/结果定义复用，不重新复制 schema。                                                                                       |
| `packages/contracts/v2/errors.json`                   | 在独立 startup 说明/有限定义中登记拟批准的 `PROJECT_FORMAT_UNSUPPORTED/project.formatUnsupported/false/{supportedFormats:[3]}` 与现三码的启动收窄值；不加入普通 `codes` 可用业务错误集合，不放宽 error2/error3。规范值仍由这一 canonical 文件提供，禁止另写 Python/TS catalog。                                                                                                 |
| `packages/contracts/v2/registry.json`                 | 登记独立 startupFailure 的 version1、profile3-only、1024 payload 口径及 schema 引用；原 methods/capabilities 不扩。获准并完成内部入口后，将 business3 原 `validator-only-runtime-disabled` 状态准确同步为 `explicit-internal-opt-in-default2`；不声明默认生产3或全模块 ready。                                                                                                  |
| `packages/contracts/v2/fixtures.json`                 | 增加四分支完整单行 UTF8 golden、原 bytes/长度与反例及实际 registryHash；同步 business3.profile 上述状态。原2案例保留，b35 示例不冒充新构建 hash。                                                                                                                                                                                                                               |
| `packages/contracts/v2/binding-regressions.json`      | 仅追加本阶段 profile3 的 pending/hash/session/版本/重复 hello 绑定回归，与 startup 原字节反例区别记录；不改旧2预期来掩盖回归。                                                                                                                                                                                                                                                  |
| `packages/contracts/src/v2.ts`                        | 增加精确 startup 值/安全错误 helper：`validateStartupFailure(value, payloadByteLength, expectedRegistryHash)`、`validateStartupError(value)`；profile/generation/once 由 supervisor 私有状态控制。复用已有 validateBusiness3 / matchesBusiness3Response / business3HelloOutcome / acceptsBusiness3JobEvent，保留 validateV2 默认语义；派生或保守 decoded 预算不能代替实际1024。 |
| `packages/contracts/python/contract_v2.py`            | 对同一 canonical 定义提供 `validate_startup_failure`、`startup_error`；后者只从独立 startup 分支构造/校验。另以原 catalog 的 code/key/retryable 和 error3 定义提供 `business3_error`，供真实3普通错误（含 supportedVersions:[3]）使用；不改 resources.safe_error 或默认 validate。                                                                                              |
| `packages/contracts/src/index.ts`                     | 保留 `PROTOCOL_VERSION=2`、旧 healthSchema 和默认 safeError。新增显式3/启动安全分支与只供展示的有限 sanitizer；EngineHealth、ProjectView、Job/TaskView、isTaskUpdate 的有限2/3展示 DTO 同步。不得把展示 union 当作运行时选版。                                                                                                                                                  |
| `packages/engine/src/ontolearn_engine/storage.py`     | 在实际 user_version 不受当前 target 支持的检查点抛受控 `UnsupportedProjectFormat(ValueError)`，保留 ValueError 兼容及旧默认目标2；覆盖 lease 后两次真实版本检查；同时将本构造失败的 db/format3 lease 清理改成逐项保首因，避免 db.close 异常覆盖 typed 原因并跳过 lease。不改迁移/备份/commit 权威。                                                                             |
| `packages/engine/src/ontolearn_engine/job_store.py`   | 仅修构造失败清理：现 except 连续 db.close→format3 lease.close→legacy lease.close 会覆盖首因并跳后续。按下述父/子资源实际所有权逐项尝试、保原 typed 异常；不改 Job/schema/迁移/事务/claim/D7。                                                                                                                                                                                   |
| `packages/engine/src/ontolearn_engine/coordinator.py` | 显式有限 profile、Store/Job/reconcile ready 门、请求/hello/response/notification/result 的严格同版选择、初始化逐资源收尾和 pre-hello 原因封存；维护原 worker 内部通道，不将前门3机械改成 worker 协议3。                                                                                                                                                                         |
| `packages/engine/src/ontolearn_engine/__main__.py`    | 内部有限启动参数解析、资源完整加载后的 canonical startup helper、真实收尾后单行 UTF8/LF/flush/非零退出；导入/资源缺失保持固定 stderr + 通用退出，不泄漏异常。                                                                                                                                                                                                                   |
| `apps/desktop/src/main/jsonl.ts`                      | 仅在原回调增加只读 `payloadByteLength` metadata，来自每帧 size 清零/去 CR 前实际累计；原严格 parser、通用帧限与 stop 行为保持。                                                                                                                                                                                                                                                 |
| `apps/desktop/src/main/engine.ts`                     | 受信 profile/备份路径签发、expectedHash、启动 deferred/首错、原字节预算优先分派、同步终态与同版 pending 匹配、health 实际协议投影。                                                                                                                                                                                                                                             |
| `apps/desktop/src/main/task-service.ts`               | 按 engine 的 main 私有 profile 对 request params/result/notification/error 选严格分支；修 connectionChanged 先验 validateV2 门、guard/catch/recovery/connectionUpdate 的二次 sanitizer，保留 generation/session/项目权限及 durable 对账。                                                                                                                                       |
| `apps/desktop/src/main/index.ts`                      | 内部受信 profile 工厂与现命名 `engine:health` catch 的第二次 safeError 门；既有任务 handler 的最终有限投影同源。原 sender/mainFrame/文档校验保留。                                                                                                                                                                                                                              |
| `apps/desktop/src/renderer/src/task-presentation.ts`  | explainError 当前首先调用默认 safeError；明确改用展示专属严格有限 sanitizer，使已获主进程认证的新固定 messageKey 不被洗成 INTERNAL_ERROR，新增固定格式不支持文案，不显示路径/实际format/异常。                                                                                                                                                                                  |

出口已核实：`packages/contracts/package.json` 的 `./v2` 指向 `src/design-v2.ts`，该文件已有 `export * from './v2'`。新 helper 在现有 v2.ts 导出即可到实际入口；**不修改 design-v2.ts、package.json 或复制第二出口**。index.ts 新展示 helper 由现有 `.` 出口直接导出。

JobStore 已支持显式 target_format3、同 Store lifetime lease、第二层 schema 验证及 reconcile；这些机制直接复用。job_store.py 仅新增本阶段构造失败 cleanup 修正，project/format3.py 不预列改动。若还有计划外必要路径，先给根具体触发/依据，不能以本计划默许扩张。

## 3. 受信 profile、路径与 expectedHash 起点

拟冻结内部 profile 为 `legacy2 | business3`，SupervisorOptions 的默认值为 legacy2。main/index 的内部开发启动参数 `--t01-internal-business3` 是唯一显式3工厂入口，本阶段仅未打包 main 可选；packaged desktop 默认2，不从 renderer、generic IPC、任意继承环境或 child 自报选择。这个具体入口须随本计划获根批准，当前尚未启用。无[2] fallback。

main 已有 getEngineEnvironment 白名单继续忽略来源环境中的 profile/DB/allowlist 等授权变量。profile 通过由该 options 生成的固定引擎 argv `--t01-internal-profile=business3` 传给真实 CLI；默认不加参数。该参数由 `__main__.py` 有限解析，未知/冲突参数安全失败，不能按任意文本执行。现冻结 entrypoint 的正常分支已转发到 `__main__.main`，不需改 entrypoint.py；测试直接用真实 CLI 显式参数，测试入口不开放 renderer。

显式3为既有库迁移提供 main 生成的可信绝对 backupPath：位于同 DB 目录、含随机唯一后缀的全新目标，通过专用内部 argv 传入；Store 在同 lease 下判断是否需要备份，并以 xb/一致 backup/fsync/原逻辑 hash 验证防覆盖和竞态。main 不先开库猜 PRAGMA 决定可否省备份，不自动删除历史 backup；已经3重开可不使用本次预留目标。格式2路径不传此参数。数据库及 allowedProjects 仍由原 main 工厂签发，renderer 不能提交路径。

expectedHash 起点仍为 main 在 spawn **之前**读取受信本地 registry 原 bytes：开发路径 `packages/contracts/v2/registry.json`；包内 `resources/contracts/v2/registry.json`。继续原严格解码/内容对照编译 registry，再 SHA256 原 bytes；测试用 options.registryPath 只在可信 harness 内提供。资源加载失败不 spawn/不信 child hash。引擎现 resources 加载同候选 canonical 和完整锁，`__main__.py` 仅在资源成功加载后使用其中 CONTRACT/REGISTRY_HASH；不改 resources.py。registryHash 不替代 schema/errors/helper/锁的包内全量 hash 验证。

## 4. 真实 Store→Job→reconcile 与严格同版链

1. `__main__.py` 取得有限 profile，完整加载可信 resources/canonical；resources 导入未完成时不能生成合格诊断。serve 从第一个自有资源取得开始建立逐资源清理记录。
2. legacy2 原样 JobStore 默认2；business3 显式 JobStore(target_format=3, backup_path=可信新目标)。复用既有唯一 lifetime writer lease，Store3 第一层迁移/完整性校验，JobStore3 第二层结构/claim-kind校验，不二次取同锁。
3. 在该 lease 下执行真实 reconcile_jobs，按 Job/claim/receipt 对账旧任务，不能仅看 schema marker 或空 pending。Store3 成功而第二层/对账失败：不 hello、不回拨格式，关闭连接/lease；重开按既有真实证据恢复，不修坏库来伪成功。
4. 校验 allowedProjects、同源 canonical、limits、Coordinator 显式 profile，然后安装 signal、reader/任务；构造内尚未移交的资源由构造方负责。每个失败点与各 cleanup 点都独立有界收尾，不让第一次 cleanup 异常阻断其余释放；锁第一真实原因，不伪 settled。
5. 所有前置满足才接收 bootstrap2 hello。legacy2 选2；business3 仅实际支持3，成功外层仍2、selectedVersion3、新非空 session、真实同源 hash；之后正式 request/response/notification 为3。复用已批准三种 null-session hello 错误和完整 legacy[2] incompatible 诊断；非法/重复hello、错误版本/session/hash同步关闭，不靠三次 anomalies 容忍3。
6. Coordinator 不止移除 constructor guard：request 的 envelope/version/method/params、hello offer/选择、emit/progress/notification、dispatch result/response 校验全部按实例可信 profile；business3 project.get 必须真实 formatVersion3。JobStore 中无协议字面量的既有 Job/结果结构复用，不改身份/claim/D7。health 只声明实际已开放能力，不能新增 source/learning。
7. main 同样按每个 Session 固定 profile 构造 hello/正式请求，并用该 profile 的严格 response/notification/pending/matches helper。3成功后不能用 validateV2 宽容消费2；合法 hello 的 hash/session/限额更新与 ready 发出同步完成，然后才 resolve promise。未知旧 generation 不能伤及新 child。

Store/JobStore 构造失败必须落实实际所有权，而非靠 hasattr 顺序close：Store 在成功返回前负责其 db/format3 lease，各资源独立尝试 cleanup，原 typed 首因重新抛出；JobStore 只有在父构造成功返回后才接管这些资源，若父构造失败不得再以遗留引用重复cleanup。JobStore 在调用父构造前取得的 legacy2 lease 始终由其自己负责；父成功而后续Job3层失败时，由JobStore逐项收尾其已接管资源。明确移交/已尝试状态，防重复close及“清理第二错覆盖第一错”；某项清理失败不能截断其余项，不能伪称已settled。serve没有成功对象时不能补构造内部清理，因此两构造均属本阶段必要路径。

## 5. typed 格式原因与 startup 终态

完整链路固定为：Store 实际版本检查 → UnsupportedProjectFormat → serve 收尾后封存的 pre-hello 初始化失败 → `__main__` canonical 专属 startup_error / startupFailure → 原 bytes → reader metadata → main 严格有限 startup 分派。不能解析 ValueError 文本、stderr、退出码，也不将 Format3Fault("format") 或任意 structure/config 失败统统称未来格式。

| 真实来源                                                                                                        | startup 精确投影                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| business3 的 UnsupportedProjectFormat，来自实际不支持的 DB 版本检查                                             | PROJECT_FORMAT_UNSUPPORTED / project.formatUnsupported / false / `{supportedFormats:[3]}`；实际版本数不输出。默认2遇到3仍原通用启动失败，不发此新码或[3]。 |
| 已有 writer lease busy（包括 Format3Fault.category=leaseBusy）或 SQLite primary BUSY/LOCKED                     | STORAGE_BUSY / storage.busy / true / `{retryAfterMs:250}`。                                                                                                |
| SQLite primary IOERR/FULL/READONLY/CORRUPT，或明确受控完整性/结构校验失败                                       | STORAGE_FAILURE / storage.failure / false / `{}`。普通业务 STORAGE_FAILURE 原 optional operationId 不收窄。                                                |
| 未列出的异常、非法配置/参数、未证实分类的 OSError；backupRequired/backupExists/sourceChanged 等不冒充格式未来值 | 有可信资源则 INTERNAL_ERROR / engine.internal / false / `{}`；无可信资源则固定 stderr + 通用退出。不把任意 OSError 映成存储损坏。                          |

resources.py.safe_error 实际只调用 CONTRACT.validate('error')，新格式码不能通过它。producer 必须由 coordinator / `__main__.py` 调用独立 canonical startup helper；普通业务错误仍走原 catalog/严格所选业务错误：2继续 resources.safe_error；显式3的 ServiceFault/classify 使用 canonical business3_error，尤其 VERSION_INCOMPATIBLE/{supportedVersions:[3]} 不能交给仅验error2的 resources.safe_error，否则会被吞成 INTERNAL_ERROR。业务3错误也不加入格式新码，不持久化该诊断为 Job 失败或提交结论。

仅初始化/pre-hello 阶段可以产生一条合格记录。成功 ready 后发生错误按真实断开/任务对账，不退回 startup；主动取消/正常退出无首错时不捏造故障。先完成所有收尾尝试，后写最终单行 UTF8 payload、LF、flush、非零退出；写失败仍安全退出。

原 reader 的 metadata 为每帧只读 payloadByteLength：不含 LF、含去 CR 前全部 payload、空白/转义按实际 bytes、跨 chunk 累计。`__main__.py` 对最终写出 bytes 核1024；main 仅以 reader 原长核1024，不使用 stringify、重编码、bufferedBytes、child 字段或第二 parser。通用262144及正常 hello/业务帧限不降低。

每个 Session 在安装 child 数据回调前持有 startup deferred、expectedHash、profile、once/terminal 和首错状态。仅当前 generation、pre-hello、business3、严格 shape/hash/有限码/实际原长≤1024全部成立才接纳一次；任何不合格记录同步 terminal+reader.stop，拒启动 promise/全部pending、清timer并停止新发送/终止自有child。首错一经锁定，EOF/close/stdin-error/timeout/cleanup不能覆盖；同 chunk后续帧不分派。ready 后的 startupFailure 为无效帧，保留真实 ready→disconnected 历史和 accepted/committed。

## 6. 命名 bridge 到固定文案的全部错误门

必须分别落实以下两条真实路径，不能伪造带旧session的初次 disconnected：

- 未曾 ready：engine startup promise 拒绝 → TaskService guard/recovery catch 或 main/index `engine:health` catch → 命名 BridgeResult → explainError。
- 已 ready 后断开：engine finish → 绑定当前 generation/session 的 connection event → task-service connectionChanged 先验门 → 原恢复/查询对账和 connectionUpdate → 共享 taskUpdateSchema / preload isTaskUpdate → App task/health入口 → explainError。

main/index 的 health catch **当前再次调用 safeError**；task-service 的 connectionChanged **当前先 validateV2('error')**，call 结果、receive 通知、guard/recovery/connectionUpdate 亦有独立门。逐个改用下述不可伪造的原 Session 认证投影，不能仅改 engine receive 或只改共享 safeError。来自普通业务响应的新格式码仍拒绝，不因对象恰好匹配有限启动形状而获得 startup 来源。

可信私有凭据的实际接口拟固定在 engine.ts：每个 EngineSupervisor 实例持有私有 WeakMap，只有内部验证成功的分派分支能登记原始 EngineError 对象及真实 connection event 对象；记录冻结的 `{原Session引用, attempt, generation, profile, preHello, 原startupPromise引用, 原requestPromise/operation绑定, provenance, validatedSafeError}`，provenance 仅为该分支实际验证的 startup3/business3/business2/local。startup3 记录只能在全部 raw/hash/profile/pre-hello/once 守卫通过后生成，先登记再拒绝原 startup promise；对应外层request/health返回promise的关联由supervisor内部登记，不能靠消费者补写tag。公开 EngineError 构造器、可变 error 属性、结构克隆、child payload 或 renderer 参数都不能创建该凭据。正常业务错误只有实际 pending 匹配及本 Session 严格同版错误验证成功才能登记 business 来源。

Supervisor 暴露只读内部方法 `projectFailure(cause: unknown, originatingPromise: Promise<unknown>): SafeError`：查询**本实例** WeakMap，并要求 originatingPromise 是该实例内部登记的原调用promise（真实共享startupPromise关联或真实pending request/operation关联），按记录的原 Session/profile/provenance 对冻结副本选对应严格 sanitizer；不查“现在选的profile”来升级旧错误，不读取调用方附带的 phase/profile/source。无凭据、跨实例、伪造构造器或克隆对象最多走默认 error2 sanitizer/INTERNAL_ERROR，绝不按 instanceof、公开tag、shape 或当前 business3 profile/代次晋升为 startup3。合法原始错误在 child 退出或新 generation 启动后仍能向它原来的调用者投影同一首错；投影本身不修改新 Session，不给旧错误新写权限。

TaskService guard/recovery catch 和 main/index health catch 都在最靠近engine调用的catch保存原request/health promise，再把实际 caught 对象及该promise交给所属 supervisor.projectFailure，不能先解包成 `{error}` 后丢凭据。后续guard若需转交已认证投影，只能沿TaskService私有的本调用catch记录传递，不能根据公开对象重新授予startup来源。engine.connectionState 当前会为每个listener执行 structuredClone(state)，因此选择唯一方案：**每个实际交付clone都先在所属Supervisor私有WeakMap绑定同一原Session/attempt认证记录，再交付该listener**；不能只登记原state，也不取消现有逐listener隔离。`projectConnectionFailure(event)`只接受该实例实际交付并登记的对象，返回从私有冻结记录提取的有限error及原generation/session用于fence；后续普通structuredClone、跨Supervisor事件、公开tag/shape均不能补认证。不能仅信 event.error 或调用方重写的来源字段。TaskService 先保留原 generation/session、项目/调用代次与 alive fence，再对仍属该调用/恢复的对象使用投影；旧调用的错误不能更新新任务恢复状态。recover/connectionUpdate 对已认证投影只做有限展示校验，不重授来源或从当前 profile 重建认证。最终发送到 bridge 的是允许的 SafeError 副本，不发送私有凭据或原 Session。

共享 index 默认 safeError / healthSchema / PROTOCOL_VERSION2 保留。新增显式 `safeBusiness3Error`、`safeStartupError` 和展示专用 `safeDisplayError` / `displayHealthSchema`；具体公开符号需随精确合同获批准。health/ProjectView 的展示类型可为有限2|3，Job/TaskView/isTaskUpdate 只接纳完整已批准DTO，startup错误仅有限展示union。展示 helper 不选择 runtime，也不为请求提供权限。正式 param/result/notification/error 始终由 actual profile 决定，不能全局 OR 2/3 宽松透传。

task-presentation 的 explainError 改用 safeDisplayError 后，才新增固定 what/why/fix/detail；格式不支持文案建议为“项目格式暂不受支持／当前内部引擎不能打开此项目格式／保留项目文件并使用兼容版本后重新检查”。只输出固定 code、有限支持列表等允许值，不回显实际 format、路径、异常；不承诺迁移完成，不自动重放写入。

I06 的 `apps/desktop/src/preload/index.ts`、`apps/desktop/src/renderer/src/{env.d.ts,App.tsx,style.css}` 本阶段不改。共享导出/严格类型重建若足够，实际原命名调用及过滤器应直接消费新有限DTO；仍须以真实传递值验证最终门，不以“没改源码”当通过。若确实需四路径之一的源码变更，先交根具体阻断与原owner，不在本计划中扩权或写旁路。

## 7. 最小专属测试路径与实际验证顺序

申请新增以下五条专属测试，不改通用历史 tests：

| 新路径                                                   | 精确覆盖                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `packages/engine/tests/test_project_startup_contract.py` | 同 canonical 四分支/未知字段/普通error2和error3拒新码、typed原因分类、默认2/显式3参数边界与逐资源初始化/cleanup故障单测；覆盖Store及JobStore构造内每个close抛错、父失败/父成功子失败的移交及不重复cleanup、原typed首因保留和其他资源仍被收尾尝试；明确注入与真实OS故障的证据差异。                                                                                                                                                                                                                                       |
| `packages/engine/tests/test_project_startup_stdio.py`    | 临时真实 SQLite + 真实 `python -I -m ontolearn_engine`；0/1/2→3、已有3重开、两层/对账失败不hello、lease重取、真实未来版本/busy/结构坏/配置错/资源缺失、default2遇3、严格hello及真实退出。                                                                                                                                                                                                                                                                                                                                |
| `tests/unit/t01-startup-canonical.test.ts`               | TS/Python共享完整 golden、raw1023/1024/1025、2000spaces、同decoded不同转义、CRLF/跨chunk/UTF8、原hello通用帧限、metadata真实性/一帧一值；不重写 parser。                                                                                                                                                                                                                                                                                                                                                                 |
| `tests/unit/t01-startup-supervisor.test.ts`              | 无窗口 Node 监督真实Python子进程，从DB/CLI到startup promise和TaskService；无pending、首错close竞态、旧generation/一次/终态、同chunk先失败/先ready、pending匹配、2/3不兼容、真实Job/operation重试不重复写；主进程 health catch 的真实helper投影；伪造/克隆EngineError、篡改error属性、跨Supervisor、旧attempt延迟catch遇新generation/profile、错误originatingPromise、ready后同形新码均不得洗成startup来源或更新新连接状态；真实onConnectionState→TaskService交付clone可用，调用方再次structuredClone及跨实例事件拒认证。 |
| `tests/unit/t01-startup-presentation.test.ts`            | 最终 BridgeResult/TaskUpdate完整值经过共享过滤与真实 explainError，固定文案不被第二safeError吞掉、不泄漏原文；display DTO union不能用于runtime选择。                                                                                                                                                                                                                                                                                                                                                                     |

另有两条**已属T01的专属测试**需与声明同步修改必要断言/描述：`packages/engine/tests/test_project_business3_contract.py`、`tests/unit/t01-business3-contract.test.ts` 当前硬断言 fixtures.business3.profile 为 validator-only-runtime-disabled。新阶段若批准启用内部opt-in，需同步成准确新状态；不能让 registry/fixtures 继续宣称“runtime disabled”或删断言逃避。这两条纳入本阶段精确审批，不据此取得其他旧测试写权。

执行顺序固定：

1. 先冻结候选及完整 canonical/golden，TS/Python对同源完整值双向验证；新格式码仅独立 startup，原2 corpus原预期通过。raw实际 bytes矩阵按r3完整保存，不只比较decoded或compact长度。
2. Python真实CLI/SQLite验证：空/旧0/1/2/已有3、lease、backup/Job/reconcile、初始化与cleanup；每例保留stdin/stdout/stderr原字节、returncode、前后PRAGMA/逻辑hash/receipt/Job及可重取lease。真实CORRUPT与人为注入errorcode分开，不把注入写成实际磁盘满验收。
3. Node无窗口真实子进程接上engine→task-service→共享DTO→explainError，验证complete SafeError原值逐门一致；2App/2Engine保留，显式3成功，3App/2Engine和2App/3Engine完整不兼容终止，不发送降级业务。posthello读取真实project.get为3，并完成原已实现Job/input/result/operation绑定、恢复与幂等查询。
4. main/index 顶层实际导入依赖Electron，不能在本机启动它。把其必要profile工厂和health最终错误投影写成可从既有共享/engine helper直接验证的最小调用；结合只读接线核对和同版类型/构建检查，明确这是无窗口机制证据，**不宣称实际Electron handler已运行**。真实IPC/sender/页面与UI集成留隔离环境原验收，不能用mock Electron冒充。
5. 运行本阶段五专属测试、必要既有T01/Store/Job/契约/reader/task回归与仓库现有 check / verify:sources；只读执行旧测试，不修改其预期。首跑失败留原件，修后冻结新candidate；通过后无变化不重复全面测试。

建议执行入口使用现有 `uv run --frozen pytest <上述Python路径>`、`npx vitest run <上述TS路径>` 及现有 check/source命令；这只是计划，本次没有执行。故障注入仅在新专属测试的受信harness内对真实函数/进程入口施加，不新增生产环境“任意异常/任意结果”后门。

## 8. 同 candidate 打包与无桌面边界

构建前冻结base/head、批准依赖、所有实际改动/新增测试及canonical原 bytes/hash。用现有 unsigned目录打包流程，不改 build/entrypoint/依赖/锁：现构建已将 contract_v2.py、整个 contracts/v2 和 uv.lock 收入引擎资源；desktop extraResources 已携带同 v2 目录。读取源码、compiled main/imported registry、Python实际resources及frozen资源manifest，逐项核 registry/schema/errors/fixtures/binding-regressions/helper/完整锁与本candidate一致；registryHash必须两端对同一原字节独立实算。

包内既有 `--protocol-resources` 只读CLI可核真实frozen资源；现有CLI正常入口可在无窗口条件运行包内引擎stdio验证opt-in3及default2。**不启动desktop产物**，不运行Electron/e2e/native/HMR，不抢焦点、提示凭据或操作审查应用；缺平台/原生/真实IPC证据据实保留待验。若当前打包脚本无法收集新增需要的模块/资源，先精确报根/T03，不擅改build或复制另一打包链。

原指定双模型对同一最终candidate全新完整独立审查、全部意见处置、必要隔离验收、CI/实际远端/正常合并门保留；内部helper/设计/无窗口机制通过均不关闭父模块P0或发布。resources/implementation身份仍真实原来源，不以业务协议3冒充parser或语义producer升级，不改D7。

## 9. 根批准前必须明确接受的具体点

本计划已经选择唯一边界，以下是**尚未获准的申请项**，不是暗中留给实现自行切换的选项：

1. 接受独立 startupFailure/error_startup、有限local-startup新码、上述helper符号及同源四分支golden；默认error2/error3/PROTOCOL_VERSION2/safeError保持。接受只供展示的有限DTO分支与实际runtime按profile严格选择的分工。
2. 接受仅未打包main内部 `--t01-internal-business3` 工厂、签发的有限engine profile argv、新绝对backup目标及default2不动；packaged desktop仍不启3。包内独立CLI仅属机制验证，不自动开放产品入口。
3. 接受本页列明的17条产品文件范围、5条新增专属测试及两条已有T01专属状态断言同步（共7条测试路径）；四条I06保留路径、protocol/resources/build/锁/旧通用tests等仍排除。若计划外阻断出现，先追加精确审批而非临时旁路。
4. 接受从真实SQLite/CLI到最终固定文案的无窗口证据范围，以及真实Electron IPC/UI/native尚待隔离环境这一明确缺口；不要求为本地通过降低原验收。

审批未到之前，不实施本计划。下一独立复核应重点核：canonical新码不穿普通error2/3、全部二次错误门、bootstrap/业务3同步分派、原长metadata预算与终态、backup和typed分类来源、有限展示union不变成runtime OR，以及上述路径/测试范围是否与真实责任完全相符。

## 10. 根阶段预审的本稿处置（待根复核）

已全文读取本体根 `iteration-control/2026-10-21-weekly-release/T01-controller-startup-implementation-phase-review.md`，实际 SHA256 `cb52ba37111d778c696a534cf34d4dda092eac98071bcc75930f42ad5904c5b8`。其原预览 f7cbc45b…198c 保留为历史，不冒充本修订稿。

- P1 构造清理：§2新增第17条job_store.py限定路径；§4固定Store/JobStore父子取得/移交/失败清理责任，专属测试逐close故障和首因保留；不改SQL、迁移、事务或D7。
- P2 原attempt来源：§6固定Supervisor私有WeakMap、原Session/attempt/prehello/promise/operation及提取接口；每listener实际交付clone先登记，来源认证不可经公开类/tag/shape/当前profile重建；§7列延迟catch、伪造/clone、真实交付链及ready后同形新码反例。
- 计数/固定输入：17产品路径、5新增+2既有T01专属测试共7路径；bf04169为初读历史，实际源码起点为27a0d171。本文尚未提交/获准，最终Git提交、全文SHA和root授权由实际流程登记，不能把private草稿当已批准。

以上是作者的文档处置申请，不代根关闭预审意见或授予实施。交叉复核仅核本轮实质delta，不重做无变化r1–r3设计。
