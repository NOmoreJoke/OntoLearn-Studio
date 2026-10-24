# T01 package087 @ 748008a6 全新独立累计工程复审报告（pair002 / ZCode / GLM-5.3）

- 审查者：ZCode（Start Plan 发起；model `account:bigmodel-start-plan/GLM-5.3`；最高思考档；完全访问——本会话全程无权限拒绝）。
- 候选：HEAD `748008a6a15091e8c5376b53a9348002eee7a207`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`（origin/develop 本地只读 ref 实核一致；本轮未发任何网络请求，含 ls-remote）。
- 范围：base→HEAD 完整 38 commits / 525 files 累计变更，非仅最后两叶。
- 只读承诺：未修改任何产品源码、测试、配置、标准、Git 索引与既有证据；未运行新 build/安装/GUI/APP/engine/测试/外部请求；所有 Git 读命令带 `--no-optional-locks`。唯一写入物为本 report.md。未读取另一模型本轮 `_002` 目录任何内容；未读写任何工具/项目/用户 memory。

---

## 0. 结论（先行）

1. **当前内部演示范围（macOS 15 arm64 无签名目录包，用户明确"非正式分发，仅限内部演示"）：PASS。** 依据见 §8，全部为本轮直接读证：源码闭集与仓库身份全对；whole087 单次完整 check 自然 0（35 TS 文件 1694 测试、332 Ruff、3445 pytest 过/44 原 skip、JS build 完成，receipt 实读）；package087 机械包身份/资源闭包通过（ASAR main 六处一致、engine 266 组件复用真实 888ac577、APP910/Resources290、593 物理针脚）；真实 e2e 18 collected = 16 PASS + 2 原平台条件 skip（T02 两例 4.4s/4.3s 原始 stdout 实读）；SOURCE005 三例真实故障 PASS 无 NOT_EXERCISED；native 真实 Cmd-Q 生命周期含 engine exit0/close0 直接观测（actual-native.json 11713B/`e152a346…` 原件时间线逐字段实读）。
2. **上一对（_001）双方结论分歧的核心——MiniMax §4.1"退役回调抛错→租约永久泄漏累计 16 次"——本轮逐链独立核验后判定：机制观察全部属实，但在当前代码不变量与产品入口下未找到自然可达触发条件，不成立为实现级 High 缺陷。** 残余真实限制（保留）：故障注入下该失败模式**无产品恢复入口**（preload 单次 ACK、失败静默保留租约），属未来不变量变化时的健壮性风险。详见 §3。
3. **M1（uncertain 单向闩锁）、M2（跨会话创建原回执不可对账）、M3（16 未ACK/UNKNOWN 责任容量）均未修复、如实保留**，与处置记录口径一致；本轮补充两条新独立观察（§3.5：#mainlineRecords 会话更替累积上限 16；scratch 预算为全局高水位摊销而非每投递 8MiB），均不构成内部演示阻断。
4. **正式分发与其他平台：HOLD 全部保留**（签名/公证/身份、wholeAPP legal/_distutils、Windows/参考设备/D2、损坏 SQLite HOLD（B/C 未授权）、用户级备份恢复实测、a11y、渗透测试、C4–C6/D8 历史轮次）。机械包身份通过不等于正式签名、法律或全平台发布通过。
5. **0/17 口径不变。** push→PR→CI→merge→远端复核均未发生；本审查者无推送/合并权限。历史失败（086 首败、087 guard 首败、first full001 首败、C4–C6）全部原样保留，未因本轮绿证据洗白。

---

## 1. 受理与环境回读（全部本方实测，非引用任务书）

| 项 | 指定 | 实测 | 判定 |
| --- | --- | --- | --- |
| prompt.txt | 25014B / SHA256 `fb7a26b3049dec04e823ac60a642b9cc0d73b49cb960d92e3c0a9e59d4cd5ec5` | 逐位一致；官方 Read 工具读至 EOF（214 行） | ✅ |
| 原清单全文 | 11255B 逐字 | 自"你现在是我的软件工程审查员。"起至 EOF 恰 11255B（SHA256 `1ca23def…f709c`，与 _001 MM 报告提取值一致） | ✅ |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | `pwd` 一致；Unicode NFC 规范形态验证通过 | ✅ |
| Git authority | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `rev-parse --git-dir` 一致 | ✅ |
| HEAD / base | `748008a6…a207` / `5f910b52…47f3` | `rev-parse` 一致；本地 origin/develop ref = base | ✅ |
| 累计范围 | 38 commits / 525 files | `rev-list --count`=38；`diff --name-only`=525 | ✅ |
| AGENTS.md overlay | 15147B / `de15f6ce…a5c8c4`，未暂存勿改 | 一致；`status --porcelain` 仅 ` M AGENTS.md`；全程未触碰 | ✅ |
| Git 索引 | 173116B / `0bd0667b…db7b119e`，cached diff 空 | 索引文件实测一致；`diff --cached --name-only` = 0 | ✅ |
| S-source 闭集 | 223577B / `ebf3328e…c252892`（1270 条） | 一致 | ✅ |
| 四份历史报告 | mm085 50711B/`8d6c72a6…`、zc085 33258B/`540dbaa4…`、mm001 103590B/`33ff3583…`、zc001 34597B/`12ffaff3…` | 全部实测一致后全文读毕（mm001 717 行分两段读至 EOF） | ✅ |
| 两份处置 | 10836B/`cc21f6b0…`、24902B/`bae9babb…` | 一致并全文读毕 | ✅ |
| 设置 | ZCode Start Plan / GLM-5.3 / 最高 / 完全访问 | 本会话实际环境一致 | ✅ |

memory 政策：官方工作区记忆已由用户关闭；本轮未读/写任何 `.zcode`、`.minimax`、项目或用户 memory。对方本轮目录（`…designated_dual_review_002/minimax/`）从未打开（连 listdir 也未做）。

## 2. 审查方式与覆盖

**亲读代码（748 工作树，行号均为本轮实读）**：`apps/desktop/src/main/engine.ts` 全文 2623 行（分段通读）；`project-mainline-service.ts` 全文 818 行；`desktop-ipc.ts` 全文 212 行；`preload/index.ts` 全文 87 行；`csp.ts` 全文；`electron.vite.config.ts`/`electron-builder.yml` 关键行；`packages/engine` 抽段：`project_lifecycle.py`（origin/认领幂等 82–102/458–472/1023–1033）、`job_store.py`（operation_get 1398–1413、reconcile_jobs 1924–1951）、`format3.py`（DDL/UNIQUE 70–90）；测试：`t01-mainline-reply-lifecycle.test.ts:528–587`、`t01-mainline-real-runtime.test.ts:505–634`、`tests/e2e/t02-ontology-mainline.spec.ts` 的 748 全 diff。
**穷举 grep**：`uncertain` 赋值全集、`#mainlineHoldingEntries`/`#mainlineRecords` 变异点、`releaseHolding/retainHolding/onReplyConsumed` 全部调用方、`commitProjectChangeSet` 产品调用链。
**525 文件分类**（`diff --name-only` 实测）：docs/reviews 307、packages/engine 66、docs/iterations 38、apps/desktop 35、tests/unit 22、tests/e2e 12、licenses 29、packages/contracts 8、fixtures/scripts/锁文件/配置 等约 8。产品代码为少数，docs/licenses/测试占多数——与 dirstat 一致；38 提交逐一列出核对（`git log --oneline` 38 行全读）。
**证据面**：whole087（ENTRY/check 日志回单/BUILD-NONCE-DIFF）、package087（ENTRY/package-readback 1.5MB 关键字段/ROOT 受理票 107285B/`41e81bd9…` 关键字段）、e2e002（ENTRY/MANIFEST 定位/test.stdout.raw 原文）、real-runtime actual001（ENTRY/ACTUAL-RUNTIME-RESULTS/native-lifecycle 原件含子进程 exit/close）、086 失败 trace（18686B/`216e2890…`）、INDEPENDENT-POSTPATCH-REVIEW、TRACE-REFERENCE-CORRECTION、ALL-GLOBAL-BINDING-READBACK（定位至 `…runner_adapters_001/e2e/head-binding-correction-001/`）。
**未核/无法确认**：Windows/Linux 参考设备与五龄设备实测；损坏 SQLite 物理 HOLD；D2 规模与执行计划；a11y 实测；RTL 渲染；第三方依赖 advisory（无网络）；docs/reviews 307 个过程文档逐字（仅台账级抽样）；锁文件全量传递依赖逐条复核（采信前两轮双方独立全量复核+S 闭集哈希一致）。

## 3. 争议可达性独立核验（本轮核心增量）

> 任务书要求："retire 若抛错，其原 receipt/holding 保留，当前 preload 只有一次原 ACK 而无自动重试，这是实在限制……请实际查证这些排除链，若找到遗漏当前可达反例明确列出；不要仅从人为 throw 推出正常产品 16 次泄漏，也不要把引擎 handle 重试说成产品重试。"

### 3.1 机制事实（MiniMax §4.1 的观察部分——全部属实）

- `engine.ts:946-981` `consume()`：前置校验（OFFERED/callbackDone/computations=0/全部 wire terminal/无 uncertain record/session 仍 current）后，`:966-969` 循环 `retire(); consumptions.delete(entry)`——**retire 抛错即中断**，`:973-980` 的退款、aliases/wires/records 清空、`#mainlineDeliveries.delete`（全仓唯一删除点 `:978`）、`#mainlineReceipts.delete`、`#mainlineConsumed.add` 均不执行；`finally` 仅复位 `consuming`。已完成的清理项已删除、不重复退款（精确重试语义）。
- `desktop-ipc.ts:136-141`：ACK 处理器 `try { replies.consume(...) } catch { return permission() }`——consume 抛错则 `deliveries.delete(id)`（`:142`）被跳过，IPC 16 槽（`:164`）同样被占。
- `preload/index.ts:28-45`：收到业务信封后发起**恰好一次** `project:reply-received` ACK（与 5s 超时 race），任何失败（超时/拒绝/deliveryId 不符）被 `catch {}` 静默吞掉并照常返回 payload——**无重发逻辑**，注释明示"Main keeps the original unacknowledged lease; no retry/clear is fabricated"。
- `engine.ts:2090-2091`：引擎退出（#finish）对在途投递只调 `#unknownDelivery`（置 UNKNOWN + 相关 record `uncertain=true`），不删除、不退款。
- `#mainlineDeliveries` 上限 16（`engine.ts:771`）；`deliveries` Map 上限 16、除精确 ACK 外无回收（`desktop-ipc.ts:103-104` 设计注释 + `:164`）——M3 的有意不对称（`accepted` Map 有 FIFO，`:144`）。

**以上与 MM 报告一致，我全部独立复核属实。分歧仅在"自然可达性"。**

### 3.2 三个抛错条件的逐链排除（产品 retire 闭包 = `project-mainline-service.ts:640-657`）

**条件 A：`!intent.pendingReplies.has(pending)`（:641）**——`pendingReplies` 仅在 `#offerIntent` 中添加各自闭包捕获的 pending（:658），仅由**各自**回调删除（:643/:655）；无任何跨删除路径。consume 对成功执行的回调先删后可能重入（重试仅重跑仍登记的失败项，且失败路径未删自身 pending——:649-654 抛错前 `accepted` 已还原、pending 仍在）。**未找到自然反例。**

**条件 B：`intent.active !== 0 || intent.unknown || !intent.accepted`（:646）**：
1. **同 intent 并发不存在（单飞串行）**：产品唯一入口 `project:changeset-commit` IPC（preload→desktop-ipc:70-71）经 `register()` 包装进 `replies.receive(work)`（:169-183）；`receive` 在整个 work 期间持有 `#mainlineComputing = delivery`（engine.ts:909），而 `#newDelivery` 在 `#mainlineComputing` 已设时直接 `invalidStateOrdinary`（engine.ts:771）⇒ **全部主链 IPC 调用端到端串行**，第二次同 operationId 提交在第一次完成（含 `finally { intent.active-- }` 同步执行完毕）前无法进入。
2. **已有 accepted 的再入分支全程同步无 await**（service:752-754）：`active++ → #offerIntent → active--` 为一个同步块，consume 只能发生在后续独立事件轮，ACK 事件不能插入。
3. **仅有的两个 active>0 的 await 窗口均无本 intent 的存活回调**：首次提交 `job.create` await（:766-777）时该 intent 刚创建、pendingReplies 为空、offer 尚未发生；`jobId` 分支 `#readAcceptedIntent` await（:755）仅在 payload 已成功退役后可达，而**退役当次回调必为最后 pending 且删除后集合为空**（size>1 分支只删自身不退役）⇒ 退役后不存在本 intent 的待执行 retire 回调。不同 intent 的在途 await 与本 intent 的 active 无关（active 为 per-intent 字段）。
4. **unknown 在 accepted 存在期间不可能再置位**：`unknown=true` 仅出现在首次提交分支（:756 进入时、:775 `job.create` 失败且 `queryWriteEntered(pin)` 为真时）；accepted 一旦建立，后续再入只走 accepted/jobId 分支。offer 前必为 false（:751 前置拒绝、:787 成功后置 false）。
5. `intent.accepted` 仅由 `#keepIntent`（:633）与回调本身（:647/:652）赋值；回调运行时 accepted 必在（条件 A 已过且此前未被并发清空）。
**未找到自然反例。**

**条件 C：`releaseHolding` 抛错**——引擎实现 `#releaseHolding`（engine.ts:872-883）仅检查 holding 存在（`#mainlineHoldingEntries` WeakMap，全文件仅 get/set、**无 delete**，grep 穷举）与 `holding.record !== record`，**无 current-session 检查**（注释明示允许旧 owner 在会话变化后清理自己的 holding）；`bytes===0` 时幂等返回。`payloadEntry` 为 `Object.freeze({})` 私有对象（service:742），仅 `#keepIntent`（:632，经 `intent.budget`——其在 intent 创建时固化绑定固定 mainline record 的 budget 实例，engine.ts:1012-1150 record.budget 缓存）retain、仅本回调 release（grep 全调用方：query-definition-service 用的是自己的 entry，selection fence 用 selectionEntry，退役 principal 用 token——均非 payloadEntry）。**未找到自然反例。**

### 3.3 两条 throw 测试的定性（确认处置描述）

- `t01-mainline-reply-lifecycle.test.ts:540-579`：手工 `onReplyConsumed(first/second, …)` 注册**人造回调**（`fail` 标志手抛 `'cleanup remains owned'`），直接调 `s.receiver.consume(...)`。证明中断语义、已完成项不重复退款、精确重试可释放——**引擎级接口性质，非产品自动恢复**。
- `t01-mainline-real-runtime.test.ts:570-595`：真实 17 次提交循环内，仅 index 0 处用 `vi.spyOn(budget,'releaseHolding').mockImplementationOnce(throw)` 一次性注入 + **直接** `value.replies.consume(duplicate.receipt)`；断言失败后 holdingCount/offered 不变，mockRestore 后再 consume 成功、holdingCount-1。同样为**注入+直连**。
- 17 次提交主体为真实产品路径：17 次 `job.create`、末次重取为 `job.get`（:618-619）、`projectRevision=17`、17 条 facts（:627-628）、每轮终态后 `slots===0`（:613）——**正常产品流 17 连提交零泄漏的运行证据**。

### 3.4 附加反例搜索（我主动尝试的边角，均未成立）

- ACK 乱序（D2 先 ACK、D1 后 ACK）：R2 见 size>1 删自身；R1 见 size==1 正常退役——无抛错。
- 重复 ACK 同一 deliveryId：IPC 层 pending 命中后转 `accepted` 记录，二次 ACK 走 accepted 分支直接返回，不重复 consume（desktop-ipc:127-151）；引擎层 `#mainlineConsumed` 幂等。
- 首次提交中途 `job.create` 失败：`unknown = queryWriteEntered(pin)`（:775）——写未入线（校验/QUEUE_FULL）则 unknown 保持 false 可重试；已入线则该 operationId 永久 `denied`（:751）且该 intent 永占一个 full 槽——**这是设计内的"已进入写入不自动重放"义务保留**（M3 族），非泄漏 bug。
- 首次提交成功后 `source.current() !== current` 抛 denied（:789）：work 异常 ⇒ receive 将 delivery 置 UNKNOWN、record.uncertain=true——落点为 M1 闩锁（已知），非 retire 泄漏（offer 未执行、无回调登记）。
- 渲染端中途崩溃：preload ACK 未发出 ⇒ 双方 16 槽各留一个未 ACK 责任——M3 设计内保留。

### 3.5 本轮新增独立观察（处置与两报告均未列出）

1. **【Low-Medium｜观察】`#mainlineRecords` 随引擎会话更替单调累积**（engine.ts:624，仅 `set` 无 `delete`，:1167 上限 16）：引擎会话死亡后下一次 `mainlineProjectClient()` 会为同一逻辑 owner 新建 record；第 16 次会话更替后 `mainlineProjectClient()` 永久 `INVALID_STATE`，主链进程内不可恢复（重启恢复）。与 uncertain 闩锁同族（M1 族长会话限制），内部演示规模（引擎重启有 60s/5 次退避约束）极难触达；如实留账。
2. **【修正 MM §4.1 的预算外推】**`#scratchReserve` 是**全局高水位摊销**（engine.ts:758-769：`nextBytes = Math.max(scratch.bytes, bytes)` 只补差量），非每投递 8MiB；16 个未清投递的常驻成本 ≈ 每投递 4096B/128obj + 载荷 handoff，距 128MiB/1048576 全局预算两三个数量级。MM"可能在远早于 16 次时就使新持有申请失败"不成立；约束面就是 16 槽本身。
3. **【确认 ZCode-001 观察 2 并补充】**任何经历过一次 ACK 丢失的 intent，其 stale pending 永存 ⇒ payload 永不退役、永占一个 full 槽（退役要求 size==1）；叠加 unknown 首提 intent 永占槽，构成 M3"16 个完整未ACK/UNKNOWN 义务容量拒绝"的两个真实来源。与已采纳安全合同一致（不 FIFO、不无偿驱逐），非新缺陷。

### 3.6 判定

- **不采纳** MM §4.1 的"实现级 High——正常产品可累积 16 次泄漏"：三个抛错条件在当前产品入口与不变量下均无自然触发（§3.2 穷举 + §3.4 边角搜索）；17 次真实提交回归 `slots===0` 为运行佐证。
- **采纳并保留**：该失败模式一旦发生（未来重构破坏单飞/同步块/私有 entry 任一不变量，或内存态损坏），产品层无恢复入口（单次 ACK 被吞、IPC 返回 PERMISSION_DENIED、引擎级 `receiver.consume` 精确重试在产品路径不可达）——**"保留"语义正确但"保留后可被产品释放"未实现**，且每次发生占用 1 引擎槽 + 1 IPC 槽直至重启。加固方向（仍有效的原 frame/session 对同一 deliveryId 的有界私有 ACK 重试，不重发 commit/job.create）与处置建议一致，未实施，不为本轮要求。
- 不把引擎 handle 可重试说成产品重试；不以"测试注入可恢复"冒充"产品自动恢复"。

## 4. 历史意见处置复核（独立判断，不以处置为指定结论）

| 项 | 本轮独立复核结论 |
| --- | --- |
| M1 uncertain 闩锁 | **未修复**（engine.ts:822/2098/2501/2566 仅 `= true`，grep 穷举无复位）。影响范围为同 live engine session 的主 project/query 面（`#mainlineReady` :709-725）；health/tasks/job/result/operation 不经此门；引擎重启或新 owner 可恢复；处置"部分采纳、缩小表述"与代码一致——是表述修正非缺陷闭合。保留为 Top3。 |
| M2 跨会话创建/示例 | `origin_value` 强制 `{hostClientId, engineSessionId(36-UUID), permission:'library.create'}`（project_lifecycle.py:82-102），每次握手新 `clientId: randomUUID()`（engine.ts:2265）⇒ 新会话重提同 operationId 必 identity 冲突；`operation_get` 按当前许可读 marker（job_store.py:1398-1413）、恢复白名单含 job.get/operation.get——"全局不可对账"不成立，**创建/示例专属限制客观存在**。缺原物理绑定保持 UNKNOWN 是已采纳合同（不删 origin、不新增持久意图账本）。保留为 Top7。 |
| M3 16 未ACK | 事实与代码一致（desktop-ipc:103-104/142/164；engine:771/978）。"可达耗尽"为事实陈述非缓解；§3.5-3 补充其两个真实来源。保留为 Top4。 |
| M4 第17个 commit | **实现正确**（本轮全文精读）：紧凑身份（operationId/request/session/jobId）retain 在 intent 自身 holding、由原 128MiB/1048576 全局预算出资、不 FIFO 遗忘；`#fullIntents` 上限（service:735）与 payload 退休分离；旧 id 严格全等校验后仅 `job.get`（service:661-699，jobId/projectId/operationId/capability/confirmationRef/input 六项），绝不 `job.create` 重放（17 次回归 :618-625 实证）；释放失败保原 receipt/holding 可精确重试；无 public 协议/origin/CSP/preload 放宽，无新增持久账本。 |
| 085 M5–M18 / Z1–Z10 | 处置表"留账不洗绿、不自动扩功能"与我在 748 的复读一致。Z1（child exit/close）在 087 actual001 已获直接观测（§5）；其余各项维持原口径（见 §7）。 |
| 001 处置更正项 | native 时间线更正确认（03:39:00.131/143/185Z，原件实读）；086 count 值为推断非 trace 记录、旧 tool output ID 非文件路径——表述边界正确；format3 `UNIQUE(project,event_id)`/`UNIQUE(project,operation)` 隐式索引确认（format3.py:70-90），"仅主键隐式索引"过窄的更正成立。 |

## 5. 证据链独立核验（全部只读实测）

| 证据 | 本轮核验 | 判定 |
| --- | --- | --- |
| whole087 check 回单 | `naturalExit:0`、argv=`npm run check`、153.76s、sourceUnchanged、changed:[]；日志 21634B/`faa92c9f…` | ✅ |
| whole087 ENTRY | HEAD=748、parent=dd21、`buildTimeProvenance` 明示"Not rebuilt at 748"（诚实）；0/17 unchanged | ✅ |
| BUILD-NONCE-DIFF | old 594342B/`847fa7e5…` → new 594342B/`83d82b19…`，唯一差异 24-ASCII nonce（electron.vite.config.ts:7），`allOtherMainBytesEqual`/`remainingFourOutputsEqual`=true | ✅ |
| package087 ENTRY | attempts 1/retries 0、`newWholeCheckJSOrEngineBuildExecuted:false`、sourceHEAD=748、formalReleaseAccepted:false | ✅ |
| ROOT 受理票 | 107285B/`41e81bd9…`；accepted=true、`ACCEPTED_STATIC_PACKAGE_IDENTITIES_RESOURCES_ONLY_RELEASED`、`legalFullClosureAccepted:false`、`mechanicalClosureOnly:true`、`dynamicCasesExecuted:false`、deliveryPhysicalPinsMatched=593、APP910 物理重建=true、remainingGates 5 项原文 | ✅ |
| e2e actual002 | ENTRY：18 collected、16 PASS+2 CONDITIONAL_SKIP、各层 natural 0、81.27s、observer 214 采样 0 错、`actualGettersMissingRemainUnknown:true`；`test.stdout.raw` 原文：`Running 18 tests using 1 worker`、T02 两例 `4.4s`/`4.3s` ✓、`2 skipped / 16 passed (1.3m)`、两条 skip 为 i04 Linux 平台条件（:98/:317） | ✅ |
| SOURCE005 三例 | reload/renderer-recovery 均 `result:PASS`、`faultApplied:true`、`preFaultState:running`、finalState succeeded（coordinator-exit 同构，字段截断前已见同型结构；_001 双方与处置一致读证） | ✅ |
| native 生命周期 | actual-native.json 11713B/`e152a346…`；before-quit seq4 `03:39:00.131Z` → closed seq5 `03:39:00.143Z` → will-quit seq6 `03:39:00.143Z` → engine pid33058 exit0 seq7 / close0 seq8 `03:39:00.185Z`——与处置更正逐字段一致 | ✅ |
| 086 失败 trace | 18686B/`216e2890…`；TRACE-REFERENCE-CORRECTION 登记 correctFailedTrace 同哈希、`originalEntriesPreserved:true` | ✅ |
| 748 一叶 | `git show` 全 diff：仅 t02 spec +15/−10；单次 `evaluateAll` 同步读双 region + **新增**重复 region 拒绝；原双谓词/`needsReconciliation` 分类/poll 5s 未动 | ✅ |
| INDEPENDENT-POSTPATCH-REVIEW | "One evaluateAll…TOCTOU removed. Duplicate region rejection, original two predicates/5s and every later assertion remain."、`actualRuntimePassClaim:false`（运行闭环由 actual002 补齐） | ✅ |
| ALL-GLOBAL-BINDING-READBACK | 定位于 `…runner_adapters_001/e2e/head-binding-correction-001/`（与 CORRECTION.json/after.py 同目录）；guard 首败与一行 HEAD 改绑记录链在案（actual002 ENTRY 引用） | ✅ |
| 087 guard 首败 | actual_001 ENTRY 保留（0 产品用例、status 前缀 `FIRST_ACTUAL_GUARD_FAILURE_PRESERVED…`）；未被洗绿 | ✅ |

## 6. 最值得修复的 10 项（按严重度；每项区分观察/推断）

> 本产品无资金/多租户/网络面，无"数据泄露/资金损失"级项；最接近"服务中断"的是 3/4（会话内主链不可用，重启可恢复，无数据损坏）。

1. **【High｜发布义务｜观察】签名/公证/身份缺失。** `electron-builder.yml:24-29`（identity null、三平台 target dir）；ROOT 受理票 `signedReleaseGate:false`、9 项非 engine 二进制 deep verify exit 1。触发：任何正式分发/他人设备。风险：Gatekeeper 拦截、供应链无身份锚。建议：正式阶段采购 Developer ID、重签+公证、产 dmg/pkg 后重跑打包态验收（必然新候选）。
2. **【High｜发布义务｜观察】wholeAPP legal/_distutils 来源闭包未闭。** `legalFullClosureAccepted:false`、`mechanicalClosureOnly:true`；ASAR 内 package.json 292B vs 原始 491B 为已记录的打包规范化差异。建议：正式阶段逐组件（含 setuptools vendored、packaging.dist-info、_distutils）复核上游来源与许可并出具接受记录。
3. **【Medium｜可用性｜观察】M1 uncertain 单向闩锁 +（新观察）#mainlineRecords 累积。** engine.ts:822/2098/2501/2566（仅置位）+ :624/:1167（records 无 delete、上限 16）。触发：同 live session 任一主链超时/UNKNOWN/引擎死亡在途；或引擎会话更替 16 次。风险：该 session 内主 project/query 全拒（health/tasks/job/result 不受影响），极端长会话后主链进程内不可恢复。建议：文档化"重启会话/应用"自救路径；未来考虑基于原操作对账证据的复位（不得简单忽略 uncertain）。
4. **【Medium｜可用性/资源｜观察】M3 未ACK/UNKNOWN 16 槽容量拒绝（含两个真实来源）。** desktop-ipc.ts:164 + engine.ts:771；来源一：渲染端 ACK 丢失（preload:40-45 静默）导致 stale pending ⇒ intent payload 永不退役永占 full 槽；来源二：已入线写失败的 unknown intent 永占槽。触发：单会话累计 16 次投递 ACK 丢失/UNKNOWN。风险：主 project/query 面拒绝直至重启。建议：UI 明示容量状态与自救（重启）；维持"不 FIFO、不假作 ACK"边界。
5. **【Medium｜健壮性｜观察】故障注入下 retire/consume 失败无产品恢复入口。** §3 全链：机制属实、自然触发未证成；一旦发生（未来不变量被破坏）每次泄漏 1 引擎槽+1 IPC 槽且产品单次 ACK 被吞。建议（未来候选）：对仍有效原 frame/session 的同一 deliveryId 做有界私有 ACK 重试（保原记录/载荷/计费，不重发 commit/job.create）；当前不要求为未证成的自然故障实施。
6. **【Medium｜数据韧性｜观察】用户级备份/恢复实测缺失 + 损坏 SQLite HOLD。** 迁移备份强制且可验（integrity_check+源哈希复查），但无应用内项目级备份/恢复入口、无恢复演练；损坏库显式拒绝启动（B/C 未授权）。风险：磁盘故障/误删整库时用户无自助。建议：正式阶段设计备份/恢复入口并实测一次恢复。
7. **【Medium｜对账｜观察】M2 跨会话创建/示例原回执不可对账。** origin 绑定逐会话 UUID（project_lifecycle.py:82-102 + engine.ts:2265）。触发：引擎在"已持久化提交后、回执抵达前"死亡，用户重试。风险：无重复项目（守卫有效），UI 停留"创建结果尚未确认"需人工核对。建议：长期按原合同以"重新证明原 dispatch 物理绑定"设计 resolution，不删 origin。
8. **【Medium｜性能/规模｜推断】索引/每页物化/撤销历史扫描未量化。** 无显式 CREATE INDEX（有 UNIQUE 隐式索引，format3.py:76/86）；T04 每页 O(总量) 物化；撤销 `_with_retirements` 全历史扫描。触发：数据增长至数万行以上（当前演示规模无故障）。建议：D2 口径内补 EXPLAIN QUERY PLAN 与关键索引，不提前优化。
9. **【Medium｜合规/UX｜观察】a11y 未核 + 错误可行动性局部瑕疵 + i18n 单语。** 键盘/读屏/对比度无合同事实；局部 NaN 插值（task-presentation）、错误为固定码白名单；全部文案硬编码 zh。建议：正式/企业阶段引入 a11y 验收与文案分级；先抽文案常量层。
10. **【Low-Medium｜功能/卫生｜观察】T04 无全量导出 + T02 无独立 redo + 工程卫生。** 导出仅当前页 CSV（有公式注入防护）；undo-of-undo 引擎可达但 UI 固定当前回执；job_store.py 2589 行/engine.ts 2623 行超线；无 CHANGELOG/Terms/Privacy；appId 个人命名空间；Dependabot 不覆盖 Python。建议：按 FR 范围核对后立项；卫生项按维护迭代处理。

## 7. 其余阻断与验收缺口（保留，不清零）

- 合并链未走：未 push/无 PR/无 CI/无 merge/无远端复核；0/17 不变。
- 指定双审体系：47 阶段积压、C4→C5→C6 三次配对失败与 D8 人工裁决门、HOLD 原记录保留。
- M0 退出项未勾（Q2/Q3/Q5/Q6/Q7/Q8/Q9、四类基线、S2/I04 合并门、签名公证离线启动）。
- 跨平台/参考设备/无开发环境设备、D2、损坏 SQLite 物理 HOLD、真实 LLM（S3 前按设计不接入）、静态盘上加密决策、渗透测试、安全问卷证据包、086 首败与 087 guard 首败永久留档。
- PRD 未完成 P0 条款（FR-002 项目导出、FR-203 Turtle 导入导出、FR-300 CSV/XLSX）——本轮内部子链审查不冒称完整 MVP。

## 8. 内部演示范围最终判定

**PASS。** 真实依据（均为本轮直接读证）：

1. 仓库身份与闭集全对（§1）；cached diff 空，唯一未暂存项为受保护 AGENTS overlay。
2. whole087 单次完整 check 自然 0；748 相对 check 时源仅一叶测试改动且原样提交（BUILD-NONCE-DIFF 诚实链）；package087 机械身份/资源闭包通过、engine 复用真实 888 组件未重建。
3. 真实运行：18=16 PASS+2 原平台条件 skip（各层 natural 0）；T02 两例 PASS 闭环 086 UI 失败；SOURCE005 三例真实故障 PASS；native 真实 Cmd-Q 与 engine exit/close 直接观测。
4. M4 修复实现正确并有 17 次真实提交回归（slots=0）；无协议/origin/CSP/preload/权限面放宽。
5. **本报告与 _001 MiniMax BLOCK 的分歧点已逐链核验**：其唯一新增实现级 High（§4.1）自然触发不成立（§3），其余三项（M1/M2/M3）为双方共识的"保留限制"，按"缺陷已闭合"口径不成立、按"当前内部演示是否阻断"口径不成立（可达后果均为会话内可用性降级且重启可恢复，无数据损坏/重复写入/越权/泄露——引擎侧 operation_claims/marker/不可变历史兜底本轮再次独立确认）。
6. 历史失败全部保留未清洗（§5）。

**保留 HOLD（正式分发/其他平台，独立判定，与上互不抵销）**：签名/公证/身份；wholeAPP legal/_distutils；Windows/跨平台/参考设备/无开发环境设备；D2 规模；损坏 SQLite HOLD（B/C）；用户级备份/恢复实测；a11y；渗透测试；静态加密与设备失窃预案；PRD P0 缺口；C4–C6/D8/双审积压；0/17 发布流程（本审查者无推送/合并权限）。

## 9. 用户 11255B 清单逐项适用性（160 引用行：147 产品 + 13 人员）

> 原则：先判适用性；不适用按类别说明依据；适用未核实写"无法确认"；不为清单扩建无关功能。产品形态：本地优先、单用户、离线、无服务端、无网络端口、无账号、无计费、无模型接入（S3 前）。

### 9.1 整类不适用（按类别）

| 类别 | 条目 | 依据 |
| --- | --- | --- |
| 账号/身份 | login+/邮箱、密码重置、MFA 及恢复、会话超时/全踢、SSO、SAML、SCIM、登录限流、防误锁 | 无服务器、无登录、无多用户；IPC 以 sender/frame/文档三重校验替代。一旦引入共享/接收他人文件即整类适用且零基础 |
| 多租户/企业合规 | 租户隔离、admin 代登录+审计、SOC 2、HIPAA、BAA、PCI、GDPR 全表删除、数据驻留、季度访问复核 | 单用户本地数据、无 PHI/卡号/第三方 PII；转为"首个企业客户前义务" |
| 支付/计费 | money 整数、汇率/税、订阅/按比例、催缴、PO 发票、VAT、退款/信用、计量对账、年约、收入报表 | 无任何货币处理 |
| 对外 API | 版本化对外 API、API key、API 限流、第三方变更预案、OAuth 刷新、集成沙箱、webhook 签名/重试 | 无对外 API/webhook；内部 stdio 协议为设计契约（schema+registry 双端校验） |
| 云基础设施 | dev/staging/prod 云语义、IaC、零停机、一键回滚、功能开关、自动扩缩、CDN、DNS/SSL、二区域、DR 年度演练、状态页、成本告警 | 无云、无端口（CSP connect-src 'none' + 引擎 audit hook 断网）；本地等价：CI 门禁、目录包回滚 |
| 观测/值班 | 3am 可搜日志、错误聚合、外部拨测、告警、仪表盘、tracing、on-call、runbook、状态页 | 无运行服务；产品零日志策略为隐私取舍（固定错误码+受限参数） |
| 邮件 | SPF/DKIM/DMARC、退信/投诉、邮件渲染 | 不发邮件 |
| 流量/规模云侧 | 连接池、负载测试、5M 行超时、cron 防重、死信队列云语义、存储生命周期 | 嵌入式 SQLite 单写者；无定时/队列服务；规模口径归 D2 |
| AI 服务 | 提示注入、数据出提示词、每客户花费上限、模型 evals、降级、弃用迁移、提示/输出日志 | S3 前无模型调用路径（已核"不存在"）；I06 接入后整类适用 |
| 其他 | 文件上传扫描、CSV 2009 导入、通知开关、酒店 wifi 加载 | 无上传面（导入=内置示例，主进程硬指定路径）；无通知系统；离线 |

### 9.2 适用且本轮已核（有实现与证据）

| 条目 | 结论与依据 |
| --- | --- |
| 预先设计的 schema | ✅ contracts/v2 schema+registry+errors 单一契约源，TS zod `.strict()` 与 Python 校验器双端执行；PRD/ADR 驱动 |
| 深于 admin 的角色/权限 | ✅ owner/principal/budget/能力白名单模型（engine.ts 权限面+mainline 允许清单 :1695-1711 本轮实读） |
| 改号越权读他人数据 | ✅ projectId 绑定+owner/session/current 三重校验；IPC trusted+sender/frame/session 精确匹配（desktop-ipc:129-135 实读）；项目切换隔离有专项 e2e |
| 服务端校验 | ✅ 主进程+引擎双侧（无服务端形态下的等价物）；本轮抽读 job_store/lifecycle 全参数化 |
| SQL 注入 | ✅ 抽读处全部 `?` 参数化；动态部分仅静态表名元组 |
| XSS/CSRF/CORS/安全头 | ✅ CSP 唯一源 csp.ts 本轮全文实读：生产无 unsafe-inline/eval、connect/object/base-uri/frame-src/form-action 全 'none'；无 HTTP 面 |
| 秘密出库/轮换 | ✅ 无密钥存在（无模型客户端）；env 白名单不继承凭据（engine.ts:572-594 实读）；轮换随之不适用 |
| 包确认/来源 | ✅ 直接依赖精确 pin；licenses/ 29 文件闭包入库；uv.lock 带 sha256 |
| 最小权限（含 AI agent） | ✅ preload 闭合命名面 28 方法（本轮全文实读，无通用 invoke）；特权引擎参数仅主进程构造；Agent 未接入且 registry 声明不得自确认 |
| 日志不记敏感 | ✅ 零日志+固定错误码+paramsSchema 受限；引擎 stderr 不转发（engine.ts:2246-2251 实读） |
| 幂等键 | ✅ operationId/operation_claims 同事务；17 次提交恰 17 次 job.create、重取走 job.get（本轮测试实读） |
| 重复提交去重 | ✅ 同 operationId 复用 accepted Job；已入线写拒绝自动重放（service:751） |
| 深分页正确性 | ✅（T04 路径）cursor+快照绑定+严格显示校验；性能未量化归 §6.8 |
| 导出 | ⚠️ 部分：当前页 CSV（BOM/CRLF/注入防护）；全量导出缺（§6.10） |
| 软删除 | ✅ 等价更强形态：retirement 显式建模+不可变历史+快照链 |
| 时区 | ✅ epoch 毫秒/单调钟，无 naive 本地时间 |
| 撇号/emoji/重音 | ✅（字面量层）strict UTF-8 全链+代理对拒绝；标识符层有意限 `[A-Za-z0-9_.-]`；RTL 渲染无法确认 |
| 数据模型抗"一个小改动" | ✅ 版本化 schema+迁移日志+user_version 断言+启动结构审计 |
| 迁移前进/不锁表 | ⚠️ 单向前向+文件级备份回滚；启动期短事务+独占租约（单机形态无 2pm 锁表问题） |
| 缓存与失效 | ✅ invalidation-v2.json 唯一规则源；仅改模型配置不作废领域结果；历史/失败/取消不计过期 |
| 后台任务队列 | ✅ 持久 Job/claims/恢复/有界 worker（本轮 reconcile_jobs 实读） |
| 带退避重试 | ✅ 主进程三次/指数退避/attemptToken；引擎侧重启对账不重跑（"marker alone can never invent success" 实读） |
| 死信队列 | ⚠️ 部分：终态+job_details 证据，无独立 DLQ 视图 |
| 结构化日志 | ✅（等价）JSONL 严格 reader+帧上限；产品侧零日志为取舍 |
| 单测/集成/e2e/回归 | ✅ 1694 TS + 3445 Py（回单实读）；18 例真实 Electron e2e（16 PASS+2 平台 skip）；专项回归集+本轮 17 连提交回归；断言具体预期集合/顺序 |
| 测试数据非生产 | ✅ fixtures 合成；.sqlite/.db/.env 禁入 |
| 空态/加载/错误态 | ⚠️ 部分：主链/查询两模块有专门分支；全屏覆盖未逐屏核验 |
| 可行动错误信息 | ⚠️ 部分：固定码+受限参数不回传堆栈；局部 NaN 插值等瑕疵留账 |
| 表单失败保留输入 | ⚠️ 部分：preservedDraft/选择不覆盖草稿；逐表单未核 |
| undo | ✅ 服务端补偿性新事务+ABA 保护；e2e Undo/Undo-of-Undo PASS（4.4s 原行实读） |
| AI 不可撤销操作人工批准 | ✅（结构性）registry `requiresConfirmation`、confirm 仅 trusted-host、Agent `agentEligible=false`；确认按钮在完整 Diff 展示后可用 |
| 披露流程 | ✅ SECURITY.md 私有渠道约定 |
| 代码可读/ADR/README/继承者文档 | ✅ strict+ruff；ADR-0001/0003（+0002 于迭代目录）；README/CONTRIBUTING/docs 树——"一小时上手"无法确认 |
| 分支策略/每变更评审 | ✅ worktree+feature 分支+指定双审+CI+远端核验（本轮即其中一环）；分支保护远端设置未核 |
| 依赖升级节奏 | ⚠️ Dependabot npm+Actions；Python 手工（缺口留账） |
| 框架升级 | ⚠️ 机制在、无既定 SLA——无法确认 |
| 事后复盘改变些什么 | ✅ C4–C6/086/actual001 失败记录、更正与独立复核留档且实际改变了实现（M4/748） |

### 9.3 适用但无法确认/未满足（如实登记）

静态加密与设备失窃预案；备份恢复实测；五龄设备/Windows/参考设备；渗透测试；安全问卷证据包；"谁查看过"审计；a11y 合规；i18n/RTL/locale 格式化；全屏状态覆盖；后退按钮语义；README 一小时实测；2000 行拆分与死代码清理（job_store 2589/engine 2623/semantic 1627）；changelog/terms/privacy；公司名下账户/域名/repo（appId 个人命名空间）；按合同删除的保留期规则；依赖 advisory 状态（无网络未核）；Python 依赖自动扫描；分支保护远端设置；DLQ 视图。

### 9.4 13 条人员角色条目

无法从仓库证据确认人员配置与轮值（组织事实）。可核实的对标：指定双审+独立复核+CI+总控记录在本轮实际运作（本报告即一环）；单人创始人 + 个人名下仓库的 bus factor=1 为真实组织风险，与代码质量判定分开记录。

## 10. 自我限制与合规披露

- **只读**：未修改任何产品文件/测试/配置/标准/索引/证据；未运行新 build/安装/GUI/APP/engine/测试/网络（含 ls-remote）；所有 Git 命令带 `--no-optional-locks`。
- **子代理/失败 lane**：本轮未使用任何子代理（无失败 lane 可披露；全部工作由主会话完成）。
- **memory**：未读/写任何工具、项目或用户 memory；对方 `_002` 目录未打开。
- **唯一写入物**：本 report.md（zcode 目录在写入前仅含 prompt.txt 与 actual-task-receipt.json，无覆盖）。
- **观察与推断区分**：§3 的可达性结论是对固定 748 源码的静态控制流穷举（观察+逻辑推导），其"自然不可达"仅在当前代码不变量（单飞串行、同步块、私有 entry、WeakMap 无 delete、预算记录固定）内成立，不保证未来重构后仍成立；§6.8/§9.3 的规模/合规项为推断或无法确认，未写成已验证事实；运行证据均为对既有冻结产物的只读复核，不构成新的运行证据。
- 证据 JSON 的哈希核验不能证明其生成过程之外的事实；机械包身份通过不等于正式签名/法律/全平台通过。

— 2026-10-24，ZCode（Start Plan / GLM-5.3 / 最高 / 完全访问），T01 package087 748008a6 pair002 独立累计复审。
