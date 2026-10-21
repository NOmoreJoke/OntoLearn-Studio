# 格式3：wire、matcher 与启动诊断小合同提案

2026-10-21。接收 owner 待冻结提案，**不是批准的 canonical、实现或运行证据**。只依据批准 `5f910b52c69d86a1076b2032e5d3c63e715947f3` 源码及总控 `format3-minimal-integration-handoff-review.md` 第5–6节（SHA-256 `cfc001d99f41c080d79346413b6431218fbacd2382f62a282553c55e4b6c34e8`）。本提案不向 T01 引入未批准的 I06 gateway、I05 或其他工作树实现。

完整固定值案例见 [format3-wire-fixtures-proposal.json](format3-wire-fixtures-proposal.json)。它有完整 request/response/notification 和本地错误对象，不是补丁片段；所有正反结论均为**未来合同预期**，本次仅 JSON/文档格式检查，未运行产品校验器、引擎或平台。当前没有协议3 catalog，固定测试 hash `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` 明标 `schema-fixture-only`，所有案例实际 ready/dispatch 预期均为 false；不是现 5f/e2c 的 hash，也不是合法协议3连接证据。

## 1. 最小版本与严格对象

建议保留一个 canonical 目录，暂保留现 `packages/contracts/v2/` 和适配器文件名，版本语义由同一资源描述；不复制 v3 目录维持第二真相。schemaVersion/registry/errors 元版本和 schema `$id` 的最终具体值由 T01 一次冻结，不能机械替换所有数字2。现有受限 schema 词汇及严格对象保持，不为本提案引入新依赖或宽松 catchall。

| 项目             | 提案约束                                                                                                                               |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| SQLite 实际格式  | 迁移与完整 Store/JobStore ready 后 Project.formatVersion 才为3；不能在未迁移库上预报3                                                  |
| bootstrap        | request/response 外层 protocolVersion=2，仅首次 hello；client 发 supportedVersions=[3]、engineSessionId=null                           |
| hello 成功       | selectedVersion=3，response 外层和 result 内的 engineSessionId 是同一新非 null UUID；id/method 精确对应；success 仅有 result，无 error |
| 后续业务         | request/response/notification 外层 protocolVersion=3；session 精确等于已协商 UUID，任何业务 error 也不例外                             |
| I06 私有网关状态 | I06 私有网关配置/凭据/授权及发送 ledger 不因本协议升级进入 Project/域 input hash/T01 checkpoint；不从 I06 未批准实现复制进接收候选     |

上述排除仅针对 I06 私有网关状态，**不排除 T01 自己的应用状态覆盖**；T01 完整 checkpoint 仍须包含 metadata、drafts、learningCurrent、assistanceAudit，并按其合同保存真实来源/版本。

通用 hello 参数 schema 可保留原1–8项、1–99整数的 supportedVersions 数组并要求唯一，以便服务端拒绝旧客户端；**本版 main 发出的列表只能是 [3]，无自动降级**。hello success 只能选择双方交集里的3，不能选2或先建会话再解释格式3。capabilities 必须唯一且逐项属于同版 registry 真实 runtime/已实现交集；fixture 的四项只是 schema 样例，不是生产能力清单。所有 limits 字段、整数/字节上限沿实际同版资源严格校验。

## 2. 五种完整握手对及错误边界

JSON 的 H01–H05 固定了全部字段和 UUID；不在 wire 对象内加入 provenance 标记，标记只在 fixture 外壳。

| 案例 | 请求 / 响应要点                                                                                                     | 普通 `matchesResponse`                     | 单独终止诊断        | 取得 ready                                |
| ---- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------- | ----------------------------------------- |
| H01  | outer2/[3]/null → outer2/selected3/两处相同 UUID/完整 limits/hash                                                   | 未来 shape/绑定应 true                     | 无                  | 本文件 false，缺实际协议3资源与 hash 核对 |
| H02  | outer2/[2]/null → null-session VERSION_INCOMPATIBLE，params.supportedVersions=[3]                                   | 请求和响应完整合法时 true，只终止          | 新端不兼容          | false                                     |
| H03  | 合法 hello 外壳，clientId 参数非法 → null-session INVALID_REQUEST/protocol.invalidRequest/{field:'params'}/false    | **false**：完整请求 schema 不合法          | 可识别固定终止诊断  | false                                     |
| H04  | 首次 hello 携非 null session → null-session SESSION_MISMATCH/protocol.sessionMismatch/{}/false                      | **false**：完整请求 schema 不合法          | 可识别固定终止诊断  | false                                     |
| H05  | 新 client 发 [3] → 旧端 outer2/null VERSION_INCOMPATIBLE/protocol.versionIncompatible/{supportedVersions:[2]}/false | **false**：不进入新端普通 response catalog | 仅 legacy2 终止诊断 | false                                     |

新端三个 null 失败均严格为 outer2/method=hello/ok=false/id=当前 hello ID，只允许对应 code/messageKey/retryable/params，无 result、路径、实际值、异常或额外键。错误参数枚举不混入旧 [2]；旧端兼容是单独有限形状，不能放宽全局 error catalog、业务 response 或 null-session schema。

服务端先验证有界 JSONL 与精确 request 外壳/已知 method/id，再对首次 hello 依次检查 params、初始 session、版本交集；H03/H04/H02 分别给上述固定失败且不授予 session。外层不是2的 hello、未知 method/id、非法外壳、重复 hello 或握手前业务请求不进入应用 adapter；本小合同建议关闭该连接，不执行、不建 claim、不消费确认。不能反射未验证的 method/id/错误原文，具体关闭是否伴有限错误须由 owner 冻结，不能由本提案新增第四种通配 null 响应。

**单独诊断分类不是让非法请求通过 matcher。** main 仅构造并发送通过完整 request 校验的 hello；H03/H04 是接收端失败合同案例，不是 main 的正常发包路径。诊断读取器只在当前 generation 尚未成功握手、当前唯一 hello 等待中、id/method 精确关联时识别这些完整固定失败；非法请求对的普通 matcher 仍为 false。没有 pending/旧 generation/诊断额外字段一律不能接受，按固定协议失败关闭；分类只终止并给安全说明，不建立 session、放行后续帧或重放请求。不得为接收错误放宽合法 request schema。H05 也不能回到 protocol2 业务会话。

## 3. TS/Python matcher 与 main ready 顺序

以下是语义合同伪码，不是产品实现；两适配器必须采用同一判定顺序和同一份 fixture 预期：

```ts
function matchesResponse(q: unknown, r: unknown): boolean {
  if (!validateFullRequest(q) || !validateFullNewResponse(r)) return false
  if (q.id !== r.id || q.method !== r.method) return false
  if (q.method === 'hello') {
    if (q.protocolVersion !== 2 || q.engineSessionId !== null) return false
    if (!r.ok) return isStrictNewHelloFailure(r) // 只允许新端三种固定形状
    return (
      r.protocolVersion === 2 &&
      r.result.selectedVersion === 3 &&
      q.params.supportedVersions.includes(3) &&
      isUuid(r.engineSessionId) &&
      r.engineSessionId === r.result.engineSessionId &&
      capabilitiesAreUniqueAndImplemented(r.result.capabilities)
    )
  }
  if (
    q.protocolVersion !== 3 ||
    r.protocolVersion !== 3 ||
    !isUuid(q.engineSessionId) ||
    q.engineSessionId !== r.engineSessionId
  )
    return false
  return r.ok ? matchesAllExistingMethodBindings(q, r) : true
}
```

`matches_response` 同判，Python bool 不充当 integer，TS 数字须安全整数。此纯函数不替代 main 的 pending、阶段、hash 或实际项目读取权限检查。JSON 的 `pureMatchesResponse` 与 `preHashPendingMatch` 分开：后者仅包含完整 shape、pair、pending 和 phase，**排除 hash、实际候选 catalog 校验和 ready**。重复 hello、无 pending 的 N13/N14 可以是纯 pair 合法，但 preHashPendingMatch 必须 false。N05 的 shape/pair/pending/phase 均匹配，故 preHashPendingMatch=true；hash 比较失败后最终 pending 必须 reject、连接 terminal，绝不能 resolve 或 ready。H03/H04/H05 不能由普通 matcher 成功接纳；终止诊断另走上节有限分类器。旧2兼容不进入上述函数的业务/成功路径。

`matchesAllExistingMethodBindings` 保留批准5f既有约束：project/job/result/operation/subscription 的实际请求响应身份，job.create 的 operation/capability/完整 input/confirmationRef 与输入扁平引用，result.current 的 kind/definition/scope/parameters/implementation/current，session.ping nonce，result.page 完整 binding/页数上限，job.list 项目/filter/listSnapshotId/每项项目与 pageSize。新方法未冻结不注册 runtime，更不因 protocol3 自动获得写能力。

业务通知除严格 outer3/session，还绑定 project/job/subscription、精确 lastSeq+1、stateVersion 与合法状态转换；终态后拒绝迟到 progress/state，不因 session 相同忽略对象归属。JSON E01–E04 提供完整 progress 正反例；其他批准事件及原 binding-regressions 由 owner 同版本迁移和补全，不删旧验收。

main 必须在处理 hello 的**同步 onFrame 分支**完成：当前 generation/唯一 pending/阶段检查 → 全对象及 pair 匹配 → 实际 expected registryHash 比较 → 同步限制 maxFrameBytes → 安装 selected3/session → 才通知 ready/允许业务。不能只在 promise.then 检查 hash 或限制，这会放行同一 stdout chunk 的下一帧。失败先将 session terminal/stop reader/拒绝 pending；同 chunk 后帧不执行。单独 session.status/其他 notification 不能令连接 ready；ready 前通知丢弃或关闭，具体策略同版冻结。不得把 fixture hash 相等当实际候选校验。

## 4. 实际 registryHash 算法及最终 receipt

批准5f的 engine.ts:264–303 与 resources.py 使用：

```text
registryBytes = read exact candidate packages/contracts/v2/registry.json as bytes
registryHash = lowercase hex(SHA256(registryBytes))
```

**只 hash registry.json 原字节**，包含其空白/换行；不是 schema+registry+errors 拼接，不是 JSON 排序/重序列化，也不是目录 hash。main 还须保留有界读取（当前262144B）、fatal UTF-8/严格 JSON 与编译进 app 的 registry 同源比较；批准实现当前用 `JSON.stringify(parsed) === JSON.stringify(compiledRegistry)`。格式3若改比较策略须显式冻结并跨端同判，不能只看到 hash 形状64hex 就通过。

源码端输入为 `packages/contracts/v2/registry.json`；实际包 main 输入为 `resources/contracts/v2/registry.json`；frozen Python 由 `sys._MEIPASS/contracts/v2/registry.json` 读取。只有目录迁移获批准才改这些路径；各处实际字节必须同版。schema.json/errors.json/fixtures.json/binding-regressions.json、TS 编译模块、Python adapter 和 executable 另按实际候选清单逐文件 SHA-256/大小与来源验证，**这组同源证据不改变 wire registryHash 的算法，也不等于签名或全部代码证明**。

本阶段不生成协议3成功 hash。接收 owner 最终 receipt 至少要有：批准候选 base/head、版本/catalog `$id`、全部相关资源清单及 raw hash、编译 app 内同源 registry 核对、实际 source/packaged Python 读取路径及原字节 hash、完整 hello request/response 两 session、negotiated limits、同 chunk 失败/成功顺序实证、ready 前无业务/claim/确认副作用。之后才新增实际 runtime-positive fixture；不能将本文件 ready=false 改写为已通过或用现5f/e2c hash冒充协议3 catalog。

## 5. 有限退出码与本地启动错误

建议在同版 registry 的小型 `startupExitCodes` 冻结以下唯一非零映射（数值为提案，须 T01 与 Python owner 最终确认）：

| 固定初始化类别   | 拟退出码 | main 本地 SafeError                                                         |
| ---------------- | -------- | --------------------------------------------------------------------------- |
| projectFormat    | 80       | ENGINE_START_FAILED / engine.startFailed / {reason:'projectFormat'} / false |
| projectStructure | 81       | 同码/key，reason=projectStructure                                           |
| storageFailure   | 82       | 同码/key，reason=storageFailure                                             |
| jobReadyFailure  | 83       | 同码/key，reason=jobReadyFailure                                            |
| contractFailure  | 84       | 同码/key，reason=contractFailure                                            |
| storageBusy      | 85       | STORAGE_BUSY / storage.busy / {retryAfterMs:250} / true                     |

前五类完整 JSON 外壳均在 fixtures 的 startupLocalCases，例如：

```json
{
  "code": "ENGINE_START_FAILED",
  "messageKey": "engine.startFailed",
  "params": { "reason": "projectFormat" },
  "retryable": false
}
```

这是 main 本地安全错误，可经原 `BridgeResult` 错误路径返回；**不是无 pending 的 stdout 消息或 hello response**。ENGINE_START_FAILED 的 params 必须且只能有 reason，取前五项枚举，固定 key/false；错误编码仍受现有2048B保护，不含路径、原 SQLite 异常、业务内容或密钥。busy 沿原 catalog 形状，本地分类固定250ms；retryable 不授予重放任务/确认/迁移。最小展示模板可由 error code/reason 固定映射为“引擎未能启动：项目格式不兼容/项目结构不完整/存储不可用/任务存储未就绪/契约资源不兼容”，busy 为“存储正被占用，请稍后重试”；不能用原 stderr 文本替代。此处仅定义本地模板数据，不自授 renderer/新的 UI 路径；真正展示若现流程不足，另逐路径授权/验证。

分类前提是当前 generation 的受控 engine 初始化边界产生已定义的结构化异常，尚无成功 hello；storage.py/job_store.py/coordinator 的固定类型与 sqlite_errorcode 是来源，`__main__.py` 仅作明确映射。不能把所有 ValueError/任意进程 sys.exit(80) 当真实格式故障。stderr 保留丢弃/有界计数，不解析文字。到不了固定分类阶段的资源加载错误、未知退出码、信号、未启动成功或无法确定来源仍为原 ENGINE_EXITED/engine.exited/{}/true 安全兜底；启动后任何退出不再解释为这张表的格式诊断，按原任务/operation 对账。

原 schema/hash/timeout 等首个终止失败优先，随后的 close(code) 不能覆盖它或复活 generation。确定性 ENGINE_START_FAILED 不自动重启/迁移，不把下一轮 UI 只读轮询变成重试循环；须显式修复条件/用户重试后新 generation。busy 可提示重试，但不自动 replay，受原总预算/退避/5次每60秒启动界限约束。未获有效 hello 不能发 ready；启动失败不能吞成空项目。具体 sticky failure 清除与取消策略列入最终冻结项。

## 6. 精确路径与 T01 最终冻结项

I06 八文件释放回执已单独提交（`24b224f`）；本文不修改或替代该回执及其安全生效条件。最小八文件是 canonical7（src/index.ts、src/v2.ts 及 v2/schema.json/registry.json/errors.json/fixtures.json/binding-regressions.json）+ `apps/desktop/src/main/engine.ts`；接收与集成只消费批准5f基础及明确格式3 patch，不顺带采用 I06 gateway。其余 main/task-service/preload/env/App/style 不随这八文件移交；worker/protocol reader/resources/入口build/锁/CI及旧测试也未由本文新增授权。

Python 四路径 `packages/contracts/python/contract_v2.py`、`packages/engine/src/ontolearn_engine/coordinator.py`、`packages/engine/src/ontolearn_engine/__main__.py`、`packages/engine/src/ontolearn_engine/job_store.py` 已按总控 `I05-T01-format3-ownership-handoff.md` 正式转原 T01 唯一维护（SHA-256 `18485767098d448a4fcce2fc7e59b5a325433826894b98111cab96926fdc2097`）。默认格式2、显式内部3隔离，只基于批准5f，不复制 I05 未批准语义；worker/protocol/resources/既有测试未随之转交。Store3内部由 T01 承接；T03构建四文件为独立交接，不混入本合同。canonical/main 八文件仍须独立总控登记与 T01 ack 才生效，不因 Python 四文件转交而自动生效。TS与Python必须合成同一个已定义候选：任一端未同步，不能对外打开数据库3。新增跨端 TS 测试路径须单独登记 owner，不能修改原测试消除失败。

T01 实施前须一次冻结：

1. canonical 元版本/目录/`$id`，bootstrap 成功/失败 schema 与 runtime 列表的最终字段名；不得同时留两套可漂移协议。
2. 本文 H01–H05 的普通 matcher/独立终止诊断边界及优先顺序；非法 params/non-null initial session 不放宽为合法请求，旧[2]只终止。
3. TS/Python 所有业务/事件/页 binding 同判、重复/无 pending/旧 session/同 chunk/资源限额及关闭策略的完整新增 fixture 与测试路径。
4. 实际协议3 catalog/registryHash 及 source/包内 receipt；本 fixture 的 a64、engineVersion/capabilities/limits 不能直接当运行身份。
5. 五类结构化初始化异常、busy 的真实来源、退出数字/同源表、ENGINE_START_FAILED catalog 配对和 main 首错优先/sticky 重试策略。
6. Store/JobStore 两层 ready 与真实 Project.formatVersion=3 的成功边界；与启动失败、迁移回滚/对账同步，不能先 hello 再补必需表。
7. 所有额外源码/旧测试/资源路径若确有需要，逐文件 diff、owner ack、source/package/mixed-version 直接证据及最后完整同候选门禁。

本文件与 JSON 仅提供可审的小合同；不执行 T01、不批准格式3，不把静态检查或 schema-fixture 预期当成产品测试通过。
