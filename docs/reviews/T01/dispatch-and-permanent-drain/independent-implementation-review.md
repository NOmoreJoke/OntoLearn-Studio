# T01 dispatch / permanent drain 独立实现审查

结论：固定产品 `04ed06afca87ef8d21a71c68371bc19a849d98f8` 本轮不通过。独立真实 Node 专项发现 **P2-DI-01：跨 Session 的旧 ping、旧 completion 与新 hello 可使未结数量达到 131，超过批准的 130**。首次失败和补齐第二真实 child 原件的失败均保留；未修改产品或原测试，未将已有完整 check 通过改写为本轮独审通过。

## 身份、职责及证据范围

审查者为未参与本实现的独立 agent `/root/create_budget_review`。唯一仓库写入为本报告；没有 stage、commit、切分支或修改作者材料。工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-dispatch-permanent-drain`。base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；adoption `e79d9d4f2e2fbdfe29217be5e4cc03f8bcce82e1`；产品 `04ed06afca87ef8d21a71c68371bc19a849d98f8`，其 parent 为该 adoption；流程 HEAD 在专项前后均为 `4f270f0f5c648b730d4bdf13009f26da72909080`。开始时只有既有未暂存 AGENTS 修改；该规则文件保持原字节。

已全文读取实施授权、固定主方案及独审、根预审、AGENTS/common、三份受审源码/测试、实现文档及 review-input/checks/log-index/source-index/runtime-process-evidence；大输出中断处另行分段补读。依据为：

| 输入 | bytes | SHA-256 |
| --- | ---: | --- |
| 根控制 `T01-dispatch-permanent-drain-implementation-authorization.md` | 11686 | `4ea8dede0ad911a0715f907ce8216364847f9f18324c9309b88d3542b0c93a2e` |
| `506e15744e47fd36f43bdbd645f6e65526cf0bf4` 主方案，含 §12 | 46175 | `fc341d0c24ffb91ac170a0f393616e22551a8e22a53b35ac373346012e97b368` |
| 同固定 ref 方案独审 | 16878 | `a9244b2ef43731448451f58583c4d077f7c4f2afb1129d15e308e473f470fd5e` |
| 根 `T01-controller-dispatch-permanent-drain-plan-prereview.md` | 20090 | `4f77f1f779f0e71cd66c34a868384f043ce4f04397f27897ced4754a328c2161` |
| 本树 AGENTS | 15852 | `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759` |
| 根 developer-common-instructions | 17891 | `e437121a08053544c2a09151ac5183baf15b5fa67a3a604891aaa9e77ba971b0` |
| 本树 review-input.json | 3153 | `ea2c3e265f5c7a95612e01541d703e12bb5bbeb32734927aebdb8ba7a78a1742` |
| 本树 candidate-manifest.json | 26507 | `12b1621713981e3c8abdc06498cc333a28f57b2117163809beeca80f980a02f0` |

根控制文件均位于 `/Users/kyle/Documents/工作/知爻/本体/iteration-control/2026-10-21-weekly-release/`。固定方案通过真实 Git blob 读取，未把新建或缺失的工作区路径当原件。

## P2-DI-01：独立 hello 池令跨代未结总量达到 131

位置：`apps/desktop/src/main/engine-lifecycle.ts:380`、`:405–408`、`:489–493`；调用链为 `engine.ts:544–570`、`:609–705` 和新 Session 的 hello `#send`。批准政策及实现文档均给普通业务最多 128、heartbeat 1、completion 1，总计最多 130；文档进一步声称 hello 与 heartbeat 不会同时未结。

实现实际上把 `hello` 和 `ping` 作为两个独立的单额池。旧 ping 在逻辑超时导致 `#finish` 时不释放，这是正确的 unknown 保额；只有其真实 owner 结束才回收。然而旧 owner 尚未真实 close 时，第二 owner 可以开始，并取得另一份 hello 额度。若旧 completion 也尚未知，已释放原 Job 业务槽后同步进入的 128 个业务 reservation 加上这三份控制 reservation，实际为 `128 + 1 + 1 + 1 = 131`。

独立专项通过真实公共入口运行，不直接 reserve 人造 ticket。它仅在原 `DispatchAccounting.prototype.reserve` 外加只读记录 wrapper，原方法照常执行并返回同一 ticket；`bytes > 0` 是原实现尚未回收的 reservation。记录器不修改 ticket、accounting、child、timer、write 或 response。子进程为本机真实 Node，真实 stdio；source/producer 是明确的机制 fixture，不是生产 issuer，terminal 四字段只用于验证消费者路线。

实际触发顺序：

1. 第一个真实 child 完成同版 hello，接受 `job.create`。producer 的 CompletionPort 发真实 `job.get`，child 不回该 get；逻辑超时后 completion 仍计 1。
2. producer 发该原 Job 的终态来源，使原业务 ticket 释放。观察注销返回永不完成的 Promise，watch 保 unknown，不代签真实生产注销。
3. child 不回真实 `session.ping`，并忽略 SIGTERM。ping 超时结束逻辑 Session，但旧 child/pipe 尚未结束，因此旧 ping 仍计 1。
4. 通过真实 `engine.health()` 同步调用 128 次，全部在 ensure 微任务前预留业务槽。第二个真实 child 在批准 cap2 内启动，发送 hello，并延迟回复，以取得明确观察窗口。
5. 在第二个 hello 已实际发送、旧 owner 尚未真实排空时，原计账对象显示 `{business:128, completion:1, ping:1, hello:1}`，总 131。`expect(active.length).toBeLessThanOrEqual(130)` 实际失败。

首次运行工具 `e4ca5b` 真实 exit 1，完整日志保留为 `/tmp/t01-dispatch-independent-cap-01.log`。其旧实际 child PID 为 43941；观测点较早，原件只读到旧 marker。没有删除或改写该失败。

补证运行只增加 90ms 观察等待并另存原件，工具 `09c1fe` 真实 exit 1。该次原件明确记录 **旧 PID 44234** 的 `hello/job.create/job.get/session.ping`，以及 **新 PID 44258** 的 `hello`，同样总 131。两个子进程均非 mock，实际用 `process.execPath` 启动；两次 finally 均 await 原 `stopAndDrain().transportOwnershipLifetime` 完成后退出。没有按泛 PID 或进程组收尾。

影响：原 130 硬界和 hello/heartbeat 互斥前提均被突破。不是仅缺少生产 source 的待接线事项；即便 source/producer 正确提供真实许可，该消费者计数结构也容许上述组合。现有 42 项中分别覆盖满业务、completion、旧/新 child、heartbeat/退避，却缺少这四池跨 Session 的组合边界。

建议：让 hello/ping 共同使用实际有限控制额度，或在所有 reservation 前核总池；必须保留已未知旧 ping/completion，且保持业务 128 和总 130，不能提前解 unknown、增加到 131 或仅调整文字。若新 hello 暂不能取得额度，应有界拒绝/等待真实旧控制 owner 结束，并正确处理新候选 child/starting。补上跨代组合边界、真实迟到/owner 回收后再准入及永久 stop 的目标专项。具体实现和新候选由唯一作者及 root 调度；本报告没有代修产品。

该反例在首次实际失败后已立即发 root 和作者 `/root/dispatch_plan_review`；第二次真实 PID/hello 及只读脚本路径亦已发送。root 已接受为 P2，尚未给出新实现或复核，因此状态为 **未关闭**。

## 其他定点审查结果与边界

- 同步入口：`request/health/requestWithDispatch` 在原 `#operation/#ensure` 微任务前拥有有限 JSON、校验同版 params、预留数量及 envelope 保守字节；job.create 同步预留本账 watch 并调用真实 producer reserve 合同。ownJson 对普通数据拒绝 accessor/cycle/nonfinite/坏 surrogate，深度、节点及转义 UTF8 有界。它并未证明 JS Proxy trap、key 反射、registry 先读取后计量或整个进程 RSS/CPU 有界，实现文档也没有作此承诺。
- scope/profile 消费：attach 仅一次且必须在接纳/starting/generation 前，附着失败不能退回裸业务；私有 invalidation epoch 仅否定能力。编码/hash/observer 注册/方法绑定均在最后 source consume 前；最终尾段直接核私有 epoch/source/current/stopped，先标 attempted 再调用已绑定 stdin.write，未再外调 source。同步 revoke/stop、非 undefined hook、错 Supervisor/child/host/session/generation/profile/hash/version/limits 在已有专项中有具体覆盖。fixture WeakMap 只证明消费机制，不证明真实全部 issuer 撤销路径，也不授首 IO 权限。
- child 寿命：owned reservation 在 spawn 前取得；cap2 包括旧 current/retiring/unknown，starting 共用一个实际启动 Promise。只因 stdout end、exit、kill 返回值或逻辑断线不会结 transport。真实 child.close、实际各条自有 stdio.closed、starting finally 和自有 kill timer 收尾共同控制释放。退避 stop 同时 clear timer/reject deferred，未发现只清 timer 留悬空 starting 的旧缺陷复现。真实后代延持管道、忽略 TERM、failed OS spawn 由已读专项和原 PID 原件支持；controlled fake close 仅是逻辑证据。
- completion/通知：原 ticket/project/job/当前 owner 与一次性当前 read dispatch 共门，completion 独立 1/262144；get/subscribe/unsubscribe 白名单及原 subscriptionId 检查存在，超时保槽、严格迟到才解 foreground。真实 server QUEUE_FULL 的 get 回退路线有专项。每原 ticket 的 producer observation 最多一份，terminal-cleanup-unknown 不由 fulfilled Promise 或本地 delete 冒充真实注销。terminal 四字段经原 producer 投影和额外 4096B 编码界及原 ticket 逐字段核同；frame/request 在真实 terminal 时清除。
- 未把 opaque 来源当作已验证内存：真实 producer 仍须保证 reservation/observation/subscription、其 WeakMap/闭包不暗留完整 payload，通知共享唯一有界 listener，并提供真实注销和未知 jobId 的唯一 claim 发现。消费者可见 ticket 清字段并不能证明未交生产供方内部也已满足 4096/524288B。清理 Promise 的回调仍捕获有限 ticket/producer/observation；生产供方完整可达引用和注销实现需要在真实 owner 交付时再审。本轮未把这一静态疑点单独升级为已证 P2，也未以其否定已证的 131 反例。
- Promise/FailureOrigin：`logicalOutcome` 使用原 `#request/#operation` 返回的 public Promise；没有额外 async 包装替代该来源。startup/legacy 投影保持原 originatingPromise 与私有错误来源核同；原 v2/v3 严格匹配、startupFailure 及未知 strict3 frame 终止行为保留。没有把 transport ended 推成 Job/Store/worker/VFS/LocationLease released。

这是本轮三 writer 全文实现审查及完整 54 输入/51 readonly 指纹核查；没有重复审改继承产品语义或运行其全套测试。对上述无新增已证阻断的观察，不应解读为生产 issuer/producer 或全平台排空已通过。

## 原检查证据与本轮独立执行

实际读回并 SHA 核同的作者原证据：

| 原件 | bytes | SHA-256 | 实际内容/终态来源 |
| --- | ---: | --- | --- |
| `/tmp/t01-dispatch-permanent-drain-check-06.log` | 8676 | `5d986475201092184d4b7f9c3db64d5899f223e2a3d4b3f64a05720c046ab59b` | lint/format/typecheck/build；23 TS 文件 1167 通过；Python 2969 通过/44 skip；原 checks 记录 c60b32 exit0 |
| `/tmp/t01-dispatch-permanent-drain-sources-02.log` | 111 | `1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536` | 12 归档源核同，原独立命令 0eddb7 exit0 |
| `/tmp/t01-dispatch-permanent-drain-focused-pids-01.log` | 218 | `ac01ddb5783d680ed4f3899beed32c40558dcc9423bcc9068440932ad64b0a29` | 42 原专项通过；只证明真实本地 Node/owner 机制 |
| `/tmp/t01-dispatch-permanent-drain-pid-evidence-01.json` | 395861 | `ebc0babee9c447d709eb8ce9ee09413804e7babfa1a39d070ec1c6a3ff6cbc7a` | 已核原件 SHA；runtime-process-evidence 明记 29 实际 PID/argv、28 marker 完整行前缀；不称每次最后写入全部捕获 |

本轮只运行必要的新反例，两次共用本树自有 `node_modules`，未借旧树 env，未重复完整 check。命令为：

```text
node node_modules/vitest/vitest.mjs run --config /tmp/t01-dispatch-independent-vitest.config.mts
```

独立输入/原件身份：

| /tmp 原件 | bytes | SHA-256 |
| --- | ---: | --- |
| `t01-dispatch-independent-cap-01.test.ts.txt`（首跑脚本原字节） | 5687 | `d981eaa5cd0f6f93626fb248d2c6a216f78934f779d6f070547e17a0aa3f5102` |
| `t01-dispatch-independent-cap.test.ts`（补证脚本） | 5708 | `87b1d6ae59aaaa38c63316622843dd2f5826585d99e618b98403179cfa53f98e` |
| `t01-dispatch-independent-vitest.config.mts` | 332 | `bb225b123c4e7824645dd2f942f783bae1944a8f4f8012d969a3a79cd704ef6d` |
| `t01-dispatch-independent-cap-01.log` | 1717 | `c2cfac0fe6c666b1c2007f65bdf84137f52a246b72c6e0f45d26628abfe5aa70` |
| `t01-dispatch-independent-cap-02.log` | 1784 | `0cd45d2bd345c436b14fccf600cbc803e957002f01761138c1bc3d6c42acf590` |
| `t01-dispatch-independent-cap-evidence.json` | 419 | `a106b2cdfb7e3e5405894fcc168a5140234dd0285574ca94ad675c81a3596174` |
| `t01-dispatch-independent-cap-evidence-02.json` | 486 | `3215d204ca3360a86dc5206dd981f7b1f294372dfd9a82e7d90558f7671bcc57` |

首跑失败 e4ca5b 与补证失败 09c1fe 均是本轮实际工具终态 exit1；报告没有把预期失败说成通过。未运行 Electron/GUI/e2e/HMR/native、网络、正式模型、凭据、付费或全套重复测试；未提供生产签发来源、未联系 T02 或其他 chat，也不替代指定双外审。

## 末次产品保护核查

独立只读脚本 `df817f` 实际 exit0：逐 54 行核 current bytes/SHA = candidate-manifest = Git 产品 blob，实际 base→product 的产品/test 路径集也恰为同 54；51 readonly 逐字等原 `423b7e4c799f188cf2ce6e8e7121893ce85624cd`，无遗漏、无新增受审产品。三 writer 在审查前后保持：

| 路径 | bytes | SHA-256 |
| --- | ---: | --- |
| `apps/desktop/src/main/engine.ts` | 45410 | `1a0613bab6c88ccc194d01e58cba651f04757962115fafaa9e30e919d7b63946` |
| `apps/desktop/src/main/engine-lifecycle.ts` | 18536 | `e3f33a55938c89c344c203253522140326052e6cdddedbad7ca0dcd1fe12f31b` |
| `tests/unit/t01-dispatch-permanent-drain.test.ts` | 43765 | `66be70925677ab34e4d6aac82edc49ee34c878f067c226aa0e4cadf025f9692a` |

最终状态：本报告冻结于上述实际产品；P2-DI-01 待唯一作者按原 130 政策修复、生成新候选并由 root 安排定点复核。当前原产品不能接收为本轮独审通过；完整首版/生产装配和父验收门保持原责任边界。

---

## R2 定点复核：7dfa9c8，原报告前缀保留

本节为原独审者实际复核后的追加。前14062B仍为原报告，SHA256 `eec339c0d75b6877be39aee23918e9ca2bbe1e5068b6af93335fa3ab8ab3060d`；首轮不通过、两个真实131失败和原件全部保留，不把历史改成已通过。

**当前结论：新固定产品 `7dfa9c8008727d469935181fc20beebb5ba4419a` 的本次定点独审通过，P2-DI-01关闭；根补充的reserve同步stop后返回真实reservation取消缺口亦关闭。** 没有发现本次修订新增的已证P2。范围限已批准三writer的消费者/计账/实际child机制，不是指定GLM/MiniMax双外审、真实生产issuer/producer或全库released证明。

### R2实际输入与身份

树及base/adoption同原报告。开始/结束流程HEAD `009e947bfb8a769b18defc299fe6018281be483c`。修复产品 `cd506d5bd978a5b0c7e4faaf0e509ee2a48a8ba2` 的parent是原流程4f270；新固定产品7dfa的parent为该修复产品，新产品后继仅修正新增测试的批量延迟假设。已读实际产品diff、全部新增8case、当前实现文档、处置、checks、runtime和输入清单；未重跑不变全套。

13输入绑定为 `review-input-r2.json` 4060B/`9e1e4ddb9a65c3d103dca93feb875e7173254ce671db43739cd4fdadd31f18f8`。逐current bytes/SHA全核同，包含原14062B独审本体。主要固定输入：

| R2路径/角色                          | bytes | SHA-256                                                            |
| ------------------------------------ | ----: | ------------------------------------------------------------------ |
| engine.ts                            | 46221 | `8948ef7f9b2a581e712da259e7ad6d9188840c1e71d01c67dcfa6896ed15d900` |
| engine-lifecycle.ts                  | 18826 | `35665d40f436032cf4b68a54061ccb65508a1d8b54430d810837013d05b8ebe4` |
| t01-dispatch-permanent-drain.test.ts | 56494 | `bb4c23c51cc63383f62263d0617555fba613141928c4f04808065aa4973fecc6` |
| 当前实现文档                         | 16906 | `f92afae840df00c8af5afaec4efd7b1231559144c91ace8b7e43e6ba512abc17` |
| disposition-r2.md                    |  4185 | `90aa8bc166eb1e1fc3df47c330ab9d4c572ebeced67105fb3aac3c9780aa0cd8` |
| candidate-manifest-r2.json           | 27389 | `00eb25982e8a81788038af4fa1387a9ac001775e17c16f401266fecc5c9af37f` |
| checks-r2.json                       |  5561 | `875f24f96614714894035579a099d158a89174a9ef4e0ef9683d972c58845c26` |
| runtime-process-evidence-r2.json     |  6367 | `b2418404a27d6175e8973de2fca565c9574eddbb3b5082a99a98e9432612a8fd` |
| log-index-r2.json                    |  9422 | `d45c8b9018f1489ab96181094f6aa9c2fa83a06c2ff6c8745860dc7090b62763` |

代码/测试路径仍为本报告前文三个绝对位置的同树路径；docs均同dispatch review前缀或原实现文档。R1 engine45410/1a0613、helper18536/e3f33a、test43765/66be709作为历史输入保留；本次不能拿其指纹描述R2当前源。新源的相对变化仅三writer，51采用只读仍等原423b。

### DI-01实际关闭依据

helper真实reserve新增 `hello+ping<=1`，保原业务128、completion1；没有把总量改131或提前释放旧unknown。engine在退避之后、spawn之前预留hello ticket和hostClientId，spawn回调只发送这份同一reservation。缺额返回QUEUE_FULL，尚未真实spawn的candidate经never-created+starting finally释放；已发送旧控制仍只由严格原response或实际owner终态回收。新#start错误映射保原EngineError对象，LifecycleFault转固定安全错误，没有改变FailureOrigin来源的原对象语义。

本审**独立复跑原131反例**：只复制原5708B脚本并改输出文件名，原脚本SHA仍为 `87b1d6ae59aaaa38c63316622843dd2f5826585d99e618b98403179cfa53f98e`。工具 `57fdd6` 实际exit0、1test pass。实际旧PID **60117** 完成hello/create/get/ping；末观察 `{business:0,completion:1,ping:1,hello:0}`，总2，无第二spawn。该末快照表示128新入口已因共享control缺额被撤回，不是把128视为从未reserve，也不代表旧unknown清掉。

为核真实峰值及恢复，本审另加一份必要独立边界专项，工具 `acb720` 实际exit0、4test pass，其中真实跨代1项记录每次原reserve成功后的实际账：**maximumTotal=130、maximumControl=1**；旧PID **60856** 的hello/create/get/ping尚unknown时仅一个实际child。等待旧owner实际结束后，旧ping.bytes才为0；旧completion.bytes仍>0，然后新实际PID **60887** 的hello/health正常完成。两份实际Node专项finally均await原永久stopAndDrain完成，没有mock child/pipe，不按泛PID收尾。这不是生产source证明。

### reserve同步stop的独立关闭依据

R2分离 `cancelRequested` 与 `attemptedCancellation` 原对象身份：stop发生在reserveOperation尚未return时只能请求取消；真实token回来后#prepare重核stopped/ticket状态，在进入ensure之前针对该原token实际cancel一次。先记录该token再外调cancel，防cancel自身重入。原成功且无observation才解watch；throw/async-looking依旧保unknown。

本审没有拿“最后consume不能外调”排除reserve阶段合法同步重入。另三个独立新case均调用实际EngineSupervisor入口/原DispatchAccounting，不借作者测试实现其断言：reserveOperation内同步engine.stop后return该真实fixture token；cancel内部再stop。分别验证：

| cancel结果                    |   真cancel调用 | spawn前检查/实际write | payload                           | 末watch |
| ----------------------------- | -------------: | --------------------- | --------------------------------- | ------: |
| success，返回undefined        | 同一原token1次 | 0/0                   | request/reservedRequest/frame清除 |       0 |
| throw                         | 同一原token1次 | 0/0                   | 清除，业务/frame额0               |       1 |
| async-looking Promise.resolve | 同一原token1次 | 0/0                   | 清除，业务/frame额0               |       1 |

随后直接重复原账cancelUnwritten及stop/drain，三项仍cancel仅1；失败两项保相同producerReservation/attemptedCancellation身份，transport无child结束也没有冒充producer清理成功。logicalOutcome固定ENGINE_EXITED，dispatchObservation仍not-written；bind/accept/observe/validated session/consume均设为不应到达，未被调用。异步样fulfilled不是清理authority，不解watch。本组是机制fixture，不提供真实生产许可。

### 独立运行原件

仅使用本树自有node_modules。两个实际命令如下，均无GUI/native：

```text
node node_modules/vitest/vitest.mjs run --config /tmp/t01-dispatch-independent-r2-vitest.config.mts
node node_modules/vitest/vitest.mjs run --config /tmp/t01-dispatch-independent-boundaries-r2-vitest.config.mts
```

| /tmp原件                                                 | bytes | SHA-256                                                            |
| -------------------------------------------------------- | ----: | ------------------------------------------------------------------ |
| t01-dispatch-independent-cap-r2.test.ts                  |  5708 | `d9a5c49239d51c6ca618c7a7b0ea44b085eb4878716029f67f68d407533017f4` |
| t01-dispatch-independent-r2-vitest.config.mts            |   371 | `e84d085d01adedd86d043f912aef679f0ed8103988c323879f81383a6649eb90` |
| t01-dispatch-independent-cap-r2-01.log                   |   230 | `fc81cdf2ca43aeaaf50196992f1a4a789ed89586a70916135cf83462e36ffb2f` |
| t01-dispatch-independent-cap-r2-evidence.json            |   415 | `584928f6b803bf584a585831e2acff1e5a07c382510b6992671086e3cb973777` |
| t01-dispatch-independent-boundaries-r2.test.ts           |  9437 | `c5f4675b036589a103a3ece3c85deea40f8f026d5e510e9f33267285a67dc9c9` |
| t01-dispatch-independent-boundaries-r2-vitest.config.mts |   378 | `bd5c84c8a69b4b70d47d552f09a23823c93370441573d55d87302ba913faf95e` |
| t01-dispatch-independent-boundaries-r2-01.log            |   230 | `cfac79fa3e433d32394786f3c09d386386caff0ed78767e6554f54d4cd1ef4f7` |
| t01-dispatch-independent-boundaries-r2-evidence.json     |   815 | `256129592ce28bfb77dc73bdd276f80a6d34f4241d31e18c3298623e27d36102` |
| t01-dispatch-independent-cancel-r2-evidence.jsonl        |   485 | `1798ea1eea03197548c3b79dac10843e64d1aedd2a123a54226e238c5418712f` |

### 原checks、首失败和PID证据读回

独立读取final同版 `/tmp/t01-dispatch-permanent-drain-r2-check-02.log`（8677B/`3cd3df5901cf527d69a32115c0797e9df694327f7a9b95c368643f2cfc0e0b7d`）：lint/format/全部type/build、1175TS、2969Py/44既有skip；checks绑定原d5fb00/session9376→ede6da exit0。独立sources02原件111B/`1439dca3a0fd2dbc3702b336e9accceedc93893d0d65264c69da1aa175c45536`对应e928ed exit0/12；本审没有重跑这两个不变全量命令。

作者冻结新8例实际原件 `/tmp/t01-dispatch-permanent-drain-r2-focused-pids-03.log` 230B/`d37b6b10024cfd38fc7cb6905c2d1625c3365554182e45e7e0f394f416789399` 读回8pass/42仅专项过滤skip，不把它当全量50通过；同版全量check已给50专项全部成功。作者4d52de原probe副本日志230B/`a19d48c8450bbd62abe8a2e5ca058da7c96a65ccaa1327f21b2969d648de740e`亦读回；本审结论另有自己的上述实跑，不仅继承作者成功。

已读首focused01/02和observer01失败原流，确认分别有原局部fault未canonical映射、批量TIMEOUT；新增测试改为允许合法TIMEOUT但等待严格迟到回包结清所有foreground，再做正常health，计数界/旧unknown/旧42条断言未删或放宽。observer对-t当源码path的实际失败及后续修复在原处置/原件保留，没有洗成首次通过。

历史PID措辞需明确更正：本首报告前缀引用了作者当时“29份完整argv”的过度表述。原395861B/ebc0 JSON本身未改，本次实际定位PID37879记录确为ps exit0但stdout仅 `37879 37862 Thu Oct 22 00:25:50 2026     (node)`。正确是29个marker PID/29次成功定向ps，**28份完整fixture argv+1仅进程名**，另28个marker文件；不重跑旧进程凑数，不用新5个PID倒补旧29份证据。原报告历史文字保留，由本追加澄清替代该数量解释。

### 最终保护、限制与当前状态

只读独立核验 `791ee9` 实际exit0：13输入全同；54行current bytes/SHA=R2 manifest=7dfa Git blob；base→product产品/test实际集合恰同54；51只读逐字等原423b；log-index34个/tmp原件全部bytes/SHA核同，首失败没有覆盖；末HEAD仍009e，status仅既有AGENTS与本独审文件。三writer在本轮执行前后均为本节固定46221/18826/56494及其列示SHA。

R2只追加本报告，原14,062B按hash逐字核保，不更改作者docs/产品/tests或原日志，不stage/commit。第一次读取处置时猜错 `revision-disposition-r2.md` 路径，真实工具648501 exit1；随后依据manifest读取真实 `disposition-r2.md`，不是产品/测试失败，也没有将该次组合读取冒称全成功。

本次通过只关闭DI-01和该同步reservation取消缺口，不扩大原三writer授权或父完整产品验收。真实I06位置/原dispatch/current_scope/全部撤销、生产Job terminal producer、完整引用/opaque供方内存、未知jobId发现、Store/worker/native/VFS/cohort释放、全生产旁路、目标OS/真人/指定双外审/CI/正常develop及原父门仍按唯一owner后续供应。本审未执行或宣称这些通过。
