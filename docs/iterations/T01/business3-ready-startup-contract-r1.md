# T01 业务3两层ready及安全启动诊断草案 r1

纯文档，供固定b35校验层审计后的下一合同审查；未启用runtime3、修改公共schema或执行启动测试。当前 [status](../../reviews/T01/status.md) 保持。方案只使用已交T01 canonical/index、coordinator/**main**/storage/main-engine责任；I06余六、protocol/resources、旧tests/build/锁/CI不扩大。

## 现状与必要改变

实际入口__main__把全部启动异常输出固定stderr ENGINE_SESSION_FAILED后exit1；main丢弃stderr内容、child退出只给ENGINE_EXITED。这是安全的通用失败，但无法精确表示不支持项目格式。Store未来格式目前抛ValueError字符串，不能让main解析异常文本推断类型。Coordinator构造仍明确拒Store3，serve实际默认JobStore2；现阶段严格3 JSON不能越过此门。

建议采用**受限单帧stdout启动失败记录**，保留stderr永不解析。它不是业务响应、通知或hello，不授予session/权限。只在受信spawn的当前generation、hello尚未成功时接收一次，随后同步使整个连接失效、拒全部pending并终止进程。已经ready后或错误hash/形状的记录一律作为无效帧关闭；不能覆盖已接受的Job结论。

## 精确记录与错误边界（待canonical接受）

固定字段：kind=startupFailure、diagnosticVersion=1、engineSessionId=null、registryHash=实际同buildhash、error=有限严格分支；无requestId/projectId/路径/原值/异常/堆栈。它没有protocolVersion，因为尚未协商且不属于业务版本2/3信封；独立定义不扩展原envelope2/3或null-session业务错误集合。原generic JSONL reader只负责raw严格解析/帧限，不需修改protocol.py。

允许四类：

| code                       | messageKey                | 精确params             | retryable | 受信来源                                                                               |
| -------------------------- | ------------------------- | ---------------------- | --------- | -------------------------------------------------------------------------------------- |
| PROJECT_FORMAT_UNSUPPORTED | project.formatUnsupported | {supportedFormats:[3]} | false     | Store迁移受信typed异常，仅实际数据库format>3或明确无法支持的格式；不解析ValueError文本 |
| STORAGE_BUSY               | storage.busy              | {retryAfterMs:250}     | true      | 原writer lease busy或SQLite BUSY/LOCKED typed分类                                      |
| STORAGE_FAILURE            | storage.failure           | {}                     | false     | 已确认SQLite IOERR/FULL/READONLY/CORRUPT或备份/完整性校验的受控typed失败               |
| INTERNAL_ERROR             | engine.internal           | {}                     | false     | 其余异常，禁止自报具体存储/版本原因                                                    |

messageKey/retryable最终必须逐项核对已有catalog原件；若原值不同使用原catalog值，此表不能私自重命名现有错误。只有PROJECT_FORMAT_UNSUPPORTED为待新增有限业务3/local-safe错误；旧error2不扩展此码。对应index.safeError/taskUpdate错误接收须显式识别批准3分支，不能被旧validateV2错误门改写成INTERNAL_ERROR，亦不能接受任意code或额外params。PROJECT_FORMAT_UNSUPPORTED不借protocol.VERSION_INCOMPATIBLE表达数据库格式。

记录须在资源模块已成功完整加载后才可发出，并绑定main预先从受信本地资源核验的实际hash；资源缺失/加载失败/未知异常无法取得可信hash时保持固定stderr+exit，main给通用ENGINE_EXITED。诊断写失败或进程退出不伪造成功记录。记录最多1024实际UTF8字节且仍受原262144帧限，单行无额外字段；main不从child输出生成expectedHash。

## Store3与Job-ready顺序

受信format3 profile显式选择target_format=3；数据库路径/项目allowlist只由main传入现有受信环境，renderer不得指定格式、路径或启动参数。默认生产2保留，先用独立明确opt-in内部入口联验3；无[2]fallback。

1. 取得唯一writer lease，按既有受控一致backup/结构hash/迁移事务建立或验证Store3。失败时constructor关闭自有连接/lease，不允许hello成功。
2. 同lease完成JobStore3结构/claim kind验证、真实旧Job完整对账；不得复制schema或“只看PRAGMA=3”跳过。第二阶段失败可保留有效Store3，进程关闭后重开显式恢复，不降user_version或修坏3结构。
3. 校验真实allowed project配置与同一canonical资源可用，建立Coordinator3 profile；初始化与signal/thread安装全部进入try/finally，Job构造后任何后续失败均关闭store、恢复信号并清理自有temporary资源。现serve构造后、主循环try前有额外步骤，不能沿用该清理窗口。
4. 此后才处理有效bootstrap2 hello并选择3/session；真实业务请求/结果/通知都是3。未交的source/learning方法仍不存在，health仅按原真实能力投影，裸Store3/空pending都不是ready依据。

重复hello（无论新旧session）、成功hello假hash、未知session或业务错误版本均同步关闭当前会话；不只增加3次anomalies再继续。main必须在同stdout chunk后续帧到达前完成hash/session/限额/终止状态更新，不等待promise回调。应用/Job请求结果仍按全局claim和真实receipt对账，连接失效不是durable失败。

## 必要同版验证计划（未运行）

新增专属test_project_*和t01-*用例，不改旧测试掩盖2行为。固定独立临时DB、原真实SQLite、无窗口真实Python子进程；测试主进程监督用Node/Vitest不启动Electron。

- 2App/2Engine现有回归保持；3App/3Engine真实Store3+Job-ready后hello成功，project.get格式3及原Job/input/results绑定成立；3App/2Engine完整旧[2]error终止；2App/3Engine仅[3]error终止。无混写或降级。
- 空库/合法旧0/1/2迁移与既有3重开；持锁、未来4、损坏3、备份失败、Job初始化/对账失败、授权配置错误、资源缺失各无成功hello。typed分类/完整固定JSON或通用退出逐个给实际oracle；重开验证原事务、lease释放与Job结论保留。
- 诊断wrong/额外字段、假hash、ready后记录、双记录、同chunk失败记录后成功hello、无pending旧generation；统一无ready、清pending且不覆盖durable状态。无原异常/路径/单元格进入stdout/stderr/bridge。
- 新业务同chunk假hash成功hello后通知/响应、重复hello、旧session、版本2业务、超时/退出/重启与真实operation重试；记录完整原输入/输出/退出poll、registry/schema/helper原字节hash、库/receipt前后状态。
- 主进程公开Bridge的ProjectView/health/error三处需同版消费3且继续严格拒未知字段；涉及实际renderer/preload/UI文件先由其owner精确接线，不把只改Project literal说前门完成。

实际代码前先关闭上述catalog值、startup schema/有限新码与受信profile入口的合同问题；此草案不自授新公共协议，不替代指定双审、CI、真实包/native和父验收。

## 完整记录示例与生成边界

以下四个完整JSON是受限新schema的拟定值，hash使用固定b35实际registry字节作可核验文档示例；不是曾输出的运行记录或未来新candidate hash。新registry变化时必须重新生成实际same-build golden，并由两端独立实算核对，不能保留此示例hash当新构建期望。

```json
{
  "kind": "startupFailure",
  "diagnosticVersion": 1,
  "engineSessionId": null,
  "registryHash": "04642f84124bc29ba3ee4092376e6c82d98c2e87a8353616734d0f419670dbc5",
  "error": {
    "code": "PROJECT_FORMAT_UNSUPPORTED",
    "messageKey": "project.formatUnsupported",
    "params": { "supportedFormats": [3] },
    "retryable": false
  }
}
```

```json
{
  "kind": "startupFailure",
  "diagnosticVersion": 1,
  "engineSessionId": null,
  "registryHash": "04642f84124bc29ba3ee4092376e6c82d98c2e87a8353616734d0f419670dbc5",
  "error": {
    "code": "STORAGE_BUSY",
    "messageKey": "storage.busy",
    "params": { "retryAfterMs": 250 },
    "retryable": true
  }
}
```

```json
{
  "kind": "startupFailure",
  "diagnosticVersion": 1,
  "engineSessionId": null,
  "registryHash": "04642f84124bc29ba3ee4092376e6c82d98c2e87a8353616734d0f419670dbc5",
  "error": {
    "code": "STORAGE_FAILURE",
    "messageKey": "storage.failure",
    "params": {},
    "retryable": false
  }
}
```

```json
{
  "kind": "startupFailure",
  "diagnosticVersion": 1,
  "engineSessionId": null,
  "registryHash": "04642f84124bc29ba3ee4092376e6c82d98c2e87a8353616734d0f419670dbc5",
  "error": {
    "code": "INTERNAL_ERROR",
    "messageKey": "engine.internal",
    "params": {},
    "retryable": false
  }
}
```

生产者须完成自有初始化失败清理后才生成、flush这一条记录并退出非零；不能先诊断再留下初始化线程/子进程或未关闭自有连接。清理失败不得声称资源已结算，未能安全分类仍给INTERNAL_ERROR或通用退出。main收到诊断后立即finish，后到EOF/close不能将已交给pending的具体安全错误覆盖为ENGINE_EXITED；该竞态在同版真实进程测试中验证。
