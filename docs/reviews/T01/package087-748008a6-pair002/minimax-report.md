# OntoLearn Studio — T01 / 748008a6 / package087 全新独立完整累计工程复审报告（MiniMax M3.1-Flash / xhigh / 始终授权）

- **审查者**：MiniMax Code（provider `minimax`，model `MiniMax-M3.1-Flash`，variant `thinking`，effort `xhigh`，`permissionMode: bypassPermissions`）
- **审查日期**：2026-10-24
- **审查类型**：全新独立完整累计复审（非受理、非计划、非抽样摘要）
- **候选**：HEAD `748008a6a15091e8c5376b53a9348002eee7a207`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，38 commits / 525 files 累计变更
- **只读边界**：产品源码、测试、配置、标准、Git 索引与既有证据全程只读；**未运行任何新的 build / 安装 / GUI / APP / engine / 测试 / 外部请求**；未修改任何产品文件、测试、配置、索引；未读取另一模型本轮（pair002）任务或报告；未读取或写入任何工具/项目/用户记忆。
- **唯一写入物**：本文件 `…/20261024_t01_748008a6_package087_designated_dual_review_002/minimax/report.md`。

---

## 0. 结论（先行）

### 0.1 当前 748008a6 / package087 —— 内部演示范围（macOS 15 arm64 未签名目录包，用户明确"非正式分发，仅限内部演示"）

**判定：PASS（带 1 项单事件可达、需重启自愈的可用性闩锁，以及 3 项需多次事件累积的容量闩锁，全部不涉及数据损坏、越权写入、凭据泄露或注入）。**

### 0.2 正式分发 / 其他平台 / 保留 HOLD

**全部保持 HOLD，一项未关闭**（§9.2）。机械包身份通过 ≠ 正式签名、法律或全平台发布通过。

### 0.3 与上一轮结论的关系（不继承、不迎合）

上一轮（同一 748 候选）MiniMax 给 **BLOCK**，其唯一新增实现级阻断是 §4.1「M4 退役回调抛错 ⇒ 主链路投递与 IPC 租约永久泄漏且无产品重试入口」。**我不维持该 High/阻断定级**——理由不是我未查到反例，而是我**独立逐段复核后确认：该退役回调在当前产品路径下不可能自然抛错**（完整排除链见 §3）。该报告自己把触发条件标为【推断】，而本轮我把"自然可达性"这一前提本身做实了。

同时**我也没有维持上一轮 ZCode 的"未发现新的实现级阻断缺陷"这一无保留表述**：我在同一 M4 修复区域内找到两个**前两轮均未识别、且不需要故障注入即可到达**的容量闩锁（N1、N2，见 §4 第 2、3 项），二者比被否定的那一条更容易触发。

因此本轮结论不是"折中"，而是：**否证了上一轮 BLOCK 的具体依据，同时用两个真实可达的替代缺陷替换它，并按当前交付范围重新定级。**

### 0.4 0/17 口径

**不变。** 仅在实际指定双审通过且 push → PR → CI → merge → 远端复核后方可改变。本审查者**无推送/合并权限，未做任何推送、未建 PR、未触发 CI**。

### 0.5 历史状态未被清零

086 首败、087 外部 guard 首败（0 产品用例）、C4–C6 三次配对失败与 D8 人工裁决门、损坏 SQLite physical HOLD、`_distutils` 归属、真实 LLM、正式签名/完整 legal、Windows/参考设备/D2、静态盘上加密、渗透测试、a11y 合规、指定双审积压——**全部继续留账**，本轮无一项被本轮绿证据抵销。

---

## 1. 受理回读核验（本方实测，非引用任务书）

| 项 | 任务书指定 | 本方实测 | 判定 |
| --- | --- | --- | --- |
| 附件字节数 | 25000 B | `wc -c` = **25000** | ✅ |
| 附件 SHA256 | `e896810d33c72c401506d5d607929b658ca7e08ad092d5f2a128d07c15b89519` | `shasum -a 256` **完全一致** | ✅ |
| 清单全文 | 11255 B，逐字保留 | 附件第 45–214 行提取 = **11255** B，SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`；首行「你现在是我的软件工程审查员。」、末行「> remembering why it's built this way, a year from now (someone who was there)」 | ✅ |
| 清单结构 | 160 引用行 | 实测：产品条目 = 附件第 54–200 行（**147** 条），人员角色条目 = 第 202–214 行（**13** 条），合计 **160** | ✅ |
| 源码绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | `pwd` 的 Unicode 规范路径逐字符一致（`od -c` 复核无 NFC/NFD 偏差） | ✅ |
| Git authority | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `git rev-parse --git-dir` 一致 | ✅ |
| HEAD | `748008a6a15091e8c5376b53a9348002eee7a207` | `git --no-optional-locks rev-parse HEAD` 一致 | ✅ |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 本轮**亲自** `git --no-optional-locks ls-remote origin refs/heads/develop` = 同一 SHA（只读远端查询） | ✅ |
| 累计范围 | 38 commits / 525 files | `rev-list --count` = **38**；`diff --name-only` = **525**；`--shortstat` = **561064 insertions / 4638 deletions** | ✅ |
| 受保护 owner 规则 AGENTS.md | 15147 B / `de15f6ce…56a5c8c4`，未暂存，勿修改 | 工作树实测 **15147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`**；`status --porcelain` 唯一条目为 ` M AGENTS.md`；**全程未修改**（HEAD 内版本为 1056 B / `1b3c0291…`，差异属 owner 刻意不暂存） | ✅ |
| Git 索引 | 173116 B / `0bd0667b…7b119e`，cached diff 空 | worktree 索引实测 **173116 B / `0bd0667bf2c014a604601613a2cab4ab155794777813cf01460993f1db7b119e`**；`diff --cached --stat` = 0 行 | ✅ |
| S-source 闭集 | 223577 B / `ebf3328e…c252892` | 实测字节与 SHA 一致 | ✅ |
| **S-source 内容复算（本方亲自执行）** | 1270 条 | **1270/1270 逐条重算 bytes + SHA256 全部一致，0 缺失、0 不符**；再以 `git -c core.quotepath=false ls-tree -r --name-only HEAD` 与闭集做路径集比对 → **两侧路径集完全相等（均 1270）** | ✅（闭集记录的是**含未暂存 AGENTS overlay 的工作区闭集**，非纯 HEAD 树闭集 —— 引用时须说明） |
| provider / model / 思考 / 权限 | MiniMax M3.1-Flash / xhigh / 始终授权 | 会话环境：`minimax/MiniMax-M3.1-Flash`、variant `thinking`、effort `xhigh`、`bypassPermissions`（始终授权） | ✅ |
| 分支 | — | `feature/weekly-t01-project-transactions` | — |

所有 Git 读命令均带 `--no-optional-locks`。

**累计 diff 区域分布（本人统计）**：`docs/reviews` 307、`packages/engine` 66、`docs/iterations` 38、`apps/desktop` 35、`tests/unit` 22、`tests/e2e` 12、`licenses/*` 29、`packages/contracts` 8、根/`scripts`/`tests/fixtures` 7。**净增 561k 行中绝大部分是契约 fixture 与过程文档**，不是产品实现。

---

## 2. 本轮实际已核 / 未核范围（诚实边界）

### 2.1 已核（本方亲自读取或亲自执行只读复算）

- **Git 全量状态**（§1 全部实测项，含 1270 条闭集逐条重算）。
- **争议焦点代码逐行**：`apps/desktop/src/main/engine.ts`（643–809、820–883、896–1011、1012–1102、1150–1330、2082–2118、2470–2570）、`apps/desktop/src/main/project-mainline-service.ts`（284–285、405–525、575–660、661–800）、`apps/desktop/src/main/desktop-ipc.ts`（80–212 全文）、`apps/desktop/src/preload/index.ts`（20–50）。
- **M4 实现链路**：`#keepIntent` / `#offerIntent` / `#readAcceptedIntent` / `commitProjectChangeSet` 全段；`onReplyConsumed` / `retainHolding` / `releaseHolding` / `consume` 全段；17 次真实 commit 回归测试 `tests/unit/t01-mainline-real-runtime.test.ts:490–640` 全文；退役清理失败测试 `tests/unit/t01-mainline-reply-lifecycle.test.ts:541–583` 全文。
- **Python 引擎**：`project_lifecycle.py`（`origin_value` 与两处认领比对）、`format3.py`（UNIQUE 约束）、`job_store.py`（游标/快照绑定相关行）、`semantic*` 未逐字复核（继承前轮结论，见 §10）。
- **渲染端**：`ontology/mainline-session.ts`（提交与撤销路径）、`ontology/mainline-diff.ts`（Diff 权威读取）、`query/typed-results.ts`（CSV 导出）、`query/QueryResultPanel.tsx`（导出与 BOM）。
- **证据面**：whole087 `ENTRY.json` / `check-full-087-receipt.json`；package087 `.app` 实物目录（本人 `os.walk` 复算）；T11 `ENTRY.json`；e2e actual002 `ENTRY.json`；real-runtime actual001 `ENTRY.json` / `ACTUAL-RUNTIME-RESULTS.json` / `frozen-original/native-lifecycle/actual-native.json`；ROOT 受理票 `controller-t11-package087-final-root-acceptance-20261024.json`。
- **历史上下文**：上一轮 085 两份冻结报告 + `review-opinion-treatment.md`（10836 B）经**只读子代理**逐字提取后由本人复核；本轮 748/package087 的 MiniMax `_001`（103590 B）与 ZCode `_001`（34597 B）两份报告及 `review-opinion-treatment.md`（24902 B）**本人全文读至 EOF**。

### 2.2 未核 / 无法确认（如实记录，不以静态检查代替运行证据）

- **本轮未运行任何测试、构建、引擎、GUI 或网络。** 所有"绿"均指对**既有冻结证据的独立复核**，不构成新的运行证据。
- Windows 打包与运行、Linux 参考设备、五龄老设备实测；两条 Linux-only e2e 在 Linux 上的真实行为。
- 损坏 SQLite physical HOLD、`_distutils` 归属、**D2 规模/负载/索引执行计划口径**、真实 LLM（I06 网关未接入）。
- 签名 / 公证 / 安装 / 无开发环境设备离线启动。
- 可访问性合规（对比度、真实屏幕阅读器）、RTL 排版、emoji/口音渲染细节。
- `packages/contracts/v2/fixtures.json` 与 `binding-regressions.json` 的**内容**风险（随包分发，未逐字审其是否含业务数据）。
- Python 侧第三方依赖（rdflib 7.6.0 / pyparsing 3.3.3 / pyshacl 0.30.1 等）的 advisory 状态（本轮无网络，未做漏洞核验）。
- `docs/reviews` 下 307 个过程文档仅做台账抽样，未逐字通读。
- **我的第 4/5/6 项缺陷的运行期后果均为【推断】**——我未执行复现（§4 逐项标注）。

### 2.3 子代理使用与自我限制（如实披露）

本轮派出 **1 条只读子代理 lane**（`explore`），任务范围仅为**上一候选 085 的两份历史报告 + `intent_lifecycle_fix_001` 处置记录**的逐项提取，用于保护本人上下文用于真实代码核验。该 lane **成功完成**，其产物我已逐条与源码/本轮两份 `_001` 报告交叉比对后采纳事实部分（历史结论本身不作为本轮判定依据）。**该 lane 未读取产品源码、未写任何文件、未读写任何记忆。** 本轮**没有**其他 lane 失败或并发限制事件。

---

## 3. 争议焦点独立复核：退役回调抛错在当前产品路径下是否自然可达

这是上一轮 BLOCK 的唯一依据，也是本轮任务书要求"实际查证这些排除链，若找到遗漏当前可达反例明确列出"的焦点。**我逐段重建了排除链，结论是：这些排除链成立，当前产品路径下该回调不可能自然抛错。**

### 3.1 退役回调本体（`project-mainline-service.ts:640–657`）

```
intent.budget.onReplyConsumed(intent.payloadEntry, () => {
  if (!intent.pendingReplies.has(pending)) throw invalid()          // 条件 A
  if (intent.pendingReplies.size > 1) { intent.pendingReplies.delete(pending); return }
  if (intent.active !== 0 || intent.unknown || !intent.accepted) throw invalid()  // 条件 B
  const accepted = intent.accepted
  intent.accepted = undefined
  try { intent.budget.releaseHolding(intent.payloadEntry) }
  catch (cause) { intent.accepted = accepted; throw cause }          // 条件 C
  intent.pendingReplies.delete(pending)
  this.#fullIntents.delete(intent)
})
intent.pendingReplies.add(pending)
```

### 3.2 排除链逐条（本方独立推导）

**排除链 0（前置约束）：主链路 IPC 是单飞的。**
`engine.ts:771` `#newDelivery` 在 `#mainlineComputing` 非空时抛 `invalidStateOrdinary()`；`receive()` 在 `engine.ts:909` 置 `#mainlineComputing = delivery`，在 `941–943` 的 `finally` 清除；`desktop-ipc.ts:171` 把**每个**主链路 handler 包在 `replies.receive(...)` 内。⇒ **同一时刻只有一个主链路 handler 在执行**，并发第二次调用被硬拒（→ `permission()`）。
唯一能在主链路 handler 挂起期间插入执行的，是 ACK 通道 `project:reply-received`（`desktop-ipc.ts:122`），它**不经过** `receive()`。

**排除链 1：条件 B 的 `intent.active !== 0` 不可被退役回调观察到。**
`intent.active++` 在 `project-mainline-service.ts:752`，`intent.active--` 在 `796–798` 的 `finally`。`active > 0` 且跨越 `await` 只可能出现在两条分支：
- `:755` `await this.#readAcceptedIntent(...)`；
- `:773` `await operation`（`job.create`）。

两条分支的前置门是 `:751` `if (intent.unknown) throw denied()` 与 `:754` `if (intent.accepted) return this.#offerIntent(intent)` / `:755` `if (intent.jobId) return await this.#readAcceptedIntent(...)` ⇒ **两分支都只在 `intent.accepted === undefined` 时进入**。

由此得到本轮**独立推导的不变式**：
> **不变式 I：`accepted === undefined` ⇒ `pendingReplies` 为空 ⇒ 该 intent 不存在任何在册退役回调。**

不变式 I 的证明（全部在同步段内）：
1. intent 创建时 `accepted` 为 `undefined`、`pendingReplies` 为空集（`:736–746`）。
2. `accepted` 只由 `#keepIntent(intent, accepted)` 置位（`:633`，调用点 `:786`），其后**紧接同步**执行 `#offerIntent(intent)`（`:792`），后者在 `:640` 注册回调、`:658` 加入 pending 令牌。`:786 → :792` 之间无 `await`。
3. `accepted` 只在退役回调内被清空（`:648`）；该回调在同一同步段内于 `:655` 删除最后一个 pending 令牌；若 `releaseHolding` 抛错则在 `:652` **恢复** `accepted` 并向上抛。
⇒ `accepted` 为 `undefined` 时，pending 令牌集合必为空 ⇒ **没有退役回调可以在 `active > 0` 的 await 窗口内被触发**。
5. 在 `intent.accepted` 分支（`:754`）中，`active++ → #offerIntent → finally active--` 是**无 await 的同步段**，事件循环无法在其中抢占 ⇒ ACK 事件也无法插入。

⇒ **条件 B 的 `active` 分量在当前产品路径不可达。**

**排除链 2：条件 B 的 `intent.unknown` 分量不可达。**
`unknown = true` 只出现在 `:756`（新写分支，彼时 `accepted` 为 `undefined`）与 `:775`（同一分支的错误处理）；`unknown = false` 在 `:787`（offer 之前）。⇒ `unknown` 为真 ⇒ 无在册退役回调 ⇒ 不可达。

**排除链 3：条件 A（`!pendingReplies.has(pending)`）不可达。**
pending 令牌在 `:658` 加入，位于注册（`:640`）的**下一行**，两者之间无 `await`；令牌只被其自身回调删除（`:643` / `:655`）。⇒ 回调执行时令牌必在集合中。

**排除链 4：条件 C（`releaseHolding` 抛错）不可达。**
`engine.ts:872–883` 的**唯一**显式拒绝是「holding 不存在」或「`holding.record !== record`」——**没有 current-session 检查**（这一点我逐行确认，与处置记录的描述一致）。
- payloadEntry 的 holding 由 `#keepIntent(intent, accepted)` → `intent.budget.retainHolding(intent.payloadEntry, accepted)` 创建；`intent.budget` = `supervisor.queryReadBudget(current.owner)`，而 `intent.owner === current.owner` 在 `:730–732` 被强制 ⇒ 同一个 record。
- `#mainlineHoldingEntries` 是 WeakMap，全文件**只有 `get` 与 `set`**（grep 全部 5 处使用点确认，**无 `delete`**）⇒ 已释放条目在 `:875` 命中 `holding.bytes === 0` **提前 return，不抛错**。
- 已释放后再次调用仍是幂等成功。

⇒ **条件 C 在当前产品路径不可达。**

### 3.3 现有两条 throw 测试的真实性质（逐字核对）

| 测试 | 实际做法 | 是否代表产品路径 |
| --- | --- | --- |
| `tests/unit/t01-mainline-reply-lifecycle.test.ts:541–583`（`keeps the exact receipt after partial cache cleanup failure without double refund`） | 用 `vi.fn()` 人为让 `retried` 抛 `'cleanup remains owned'`，随后**直接再次调用 `s.receiver.consume(offered.receipt)`**（引擎级 API） | **否** —— 绕过 IPC 层与 preload；且回调是测试自造的，不是产品 `#offerIntent` 的真实回调 |
| `tests/unit/t01-mainline-real-runtime.test.ts:570–590` | `vi.spyOn(budget,'releaseHolding').mockImplementationOnce(() => { throw … })` 一次性注入，随后 `value.replies.consume(duplicate.receipt)` 重试 | **否** —— 同为故障注入 + 引擎级直调；产品路径没有对应的"自动再 ACK" |

两条测试证明的是**"释放失败后原 receipt/holding 保留、可按原 handle 重试、已完成项不重复退款"**（这是**已采用的安全合同**，实现正确），**不证明**自然触发，也不证明产品自动恢复。

### 3.4 仍然成立的真实限制（如实保留，不因上述结论而被淡化）

即便自然不可达，以下三点是**源码可证的客观事实**，本轮维持登记：

- **【观察】** `engine.ts:964–972`：`consume()` 的退役循环被 `retire()` 抛错中断 ⇒ `engine.ts:973–980` 的退款（bytes/objects）、`aliases.length=0`、`wires.clear()`、`records.clear()`、`#mainlineDeliveries.delete`、`#mainlineReceipts.delete`、`#mainlineConsumed.add` **全部不执行**；`finally` 只把 `delivery.consuming` 复位。
- **【观察】** `desktop-ipc.ts:136–142`：`consume()` 抛错 ⇒ `return permission()` ⇒ **`deliveries.delete(id)` 被跳过** ⇒ IPC 投递槽（上限 16，`:164`）被永久占用。
- **【观察】** `preload/index.ts:28–45`：ACK **只发一次**（`ipcRenderer.invoke('project:reply-received')` + 5s 超时），失败被 `catch {}` **静默吞掉**，渲染端**照样拿到正确业务结果**；代码注释自述「Main keeps the original unacknowledged lease; no retry/clear is fabricated.」⇒ **产品层没有任何自动重发原 ACK 的入口**。

⇒ **准确表述**：**若**退役回调真的抛错（故障注入、未来代码改动或未预见状态），原 receipt/holding 会**被正确保留**（fail-safe 成立，符合已采用合同），但**产品路径没有恢复入口**，两个 16 槽账本各泄漏 1 槽。**这是"保住了责任、却没有恢复通道"的潜伏脆弱性，不是当前可达的可用性中断。** 上一轮把"16 次正常操作即泄漏整条主链路"当作触发条件，与代码不符。

### 3.5 本轮在争议焦点附近发现的**真实可达**替代缺陷（不需要故障注入）

见 §4 第 2 项（N1）与第 3 项（N2）。它们比被否定的那一条**更容易**在正常使用中到达。

---

## 4. 最值得修复的 10 项（按严重程度排序）

> **【观察】** = 我在源码/产物中直接读到或亲自复算到的事实。
> **【推断】** = 由观察推导的运行期后果（**本轮未执行验证**）。

### 4.1 【High｜可用性｜观察+推断】`uncertain` 是单向闩锁：一次主链路请求超时即永久毒化该 owner 的整个 project/query 面

- **位置**：`apps/desktop/src/main/engine.ts:276`（`uncertain?: boolean` 声明）、`:714`（`#mainlineReady` 判定并 `throw deniedOrdinary()`）、`:822`（`#unknownDelivery` 全量置位）、`:957`（`consume()` 因 record 不确定而拒绝）、`:2098`（引擎死亡时在途请求置位）、**`:2500–2505`（请求超时置位 + `delivery` 转 UNKNOWN）**、`:2566`。
- **【观察】1**：本轮对 `engine.ts` 全文件穷举 `uncertain` 赋值：**只有 `= true`**，全仓**无 `= false`、无删除、无复位路径**（grep 全部 7 处出现点确认）。
- **【观察】2**：`engine.ts:2500–2505` 的超时处理**同时**做两件事：
  ```js
  const timer = setTimeout(() => {
    if (mainlineOwner) mainlineOwner.uncertain = true
    if (delivery) this.#unknownDelivery(delivery)
    session.pending.delete(request.id)
    rejectRequest(this.#sign(session, timeout(phase)))
  }, duration)
  ```
  ⇒ **一次 >5s 的主链路请求超时（`requestMs` 默认 5000，`engine.ts:705`；主链路取 `Math.min(requestMs, engineLimit)`）会一次性：(a) 毒化 owner record；(b) 把该 delivery 永久转为 UNKNOWN。**
- **【观察】3**：owner record 的逃逸条件是"**引擎会话更换**"，不是"应用重启"：`engine.ts:1164–1167` `mainlineProjectClient()` 仅在旧 record 的 session 已失效时才铸造新 record；会话仍存活时返回**同一个**被污染的 client。⇒ 引擎健康时**无任何自愈路径**。
- **【推断】触发/反例**：任何一次主链路请求超过 5 秒（大项目、冷/忙磁盘、引擎 GC 停顿）⇒ 此后该会话内**全部** `project:*`/`query:*` 永久 `PERMISSION_DENIED`；用户只看到一个固定错误码，无"重启会话"引导。
- **【推断】风险**：可用性中断 + 该会话内原操作对账能力不可达。**无数据损坏、无重复写入**——引擎侧 `operation_claims` 仍兜住不变量。
- **严重度**：**High**（单事件触发、无自愈、影响面是整个主链路面）。这与 §3 的退役回调不同：本条**不需要**任何故障注入，只需要一次慢操作。
- **建议**：为 `uncertain` 增加**基于原操作证据**的复位路径（例如同一 `operationId` 成功对账取回原回执后清除该 record 的闩锁），或在 `#mainlineReady` 改为"不确定态下允许只读/对账类调用"。**不要**简单放宽为"忽略 uncertain"——那会恢复自动重放已输入写入的风险。

### 4.2 【Medium–High｜可用性｜观察+推断】**新发现**：一次失败的 `changeset.commit` 永久占用 1 个 `#fullIntents` 槽；16 次失败后本会话所有提交被永久拒绝

- **位置**：`apps/desktop/src/main/project-mainline-service.ts:735`（`if (this.#fullIntents.size >= 16) throw invalid()`）、`:749`（`this.#fullIntents.add(intent)`）、`:656`（**全文件唯一的** `this.#fullIntents.delete(intent)`，位于退役回调内）、`:284–285`（两容器声明）、`:754`/`:792`（唯一两处 `#offerIntent` 调用点）。
- **【观察】1**：本轮 grep 确认 `#fullIntents` 的**全部** 5 处引用（284 声明、285 声明、735 判定、749 增加、656 删除）。**删除只发生在退役回调内**；而退役回调只在 `#offerIntent`（`:640`）注册，`#offerIntent` 只在 `:754`（已有 accepted）与 `:792`（首次成功后）被调用。
- **【观察】2**：intent 在**创建时**（`:749`、早于任何 payload 保留）就被加入 `#fullIntents`。因此**在到达 `#offerIntent` 之前失败**的提交，其 intent 会**永久驻留** `#fullIntents`：此时 `accepted === undefined`、`jobId === undefined`、`pendingReplies` 为空 ⇒ **永远不可能存在退役回调去删除它**。
- **【观察】3**：失败点具体为 `:774–777`（`job.create` 被引擎拒绝 ⇒ `intent.unknown = this.supervisor.queryWriteEntered(pin)` 后上抛）与 `:778–785`（返回的 accepted Job 校验失败 ⇒ `throw invalid()`）。
- **【观察】4**：渲染端每次尝试**铸造新的 operationId**：`apps/desktop/src/renderer/src/ontology/mainline-session.ts:479` `operationId: crypto.randomUUID()` ⇒ 用户重试**不会**复用同一 intent ⇒ 被占用的槽**不可通过重试回收**。
- **【观察】5**：`ProjectMainlineService` 在 `apps/desktop/src/main/index.ts:262` **只实例化一次**（应用级长生命周期单例）；`dispose()`（`:801–817`）**不清空** `#fullIntents` / `#intents`。
- **【推断】触发/反例**：任何引擎级拒绝的提交（如基线版本已变导致的 `REVISION_CONFLICT`、重复提交、undo 冲突、引擎不可达）都消耗 1 槽。累计 **16 次**后，`:735` 抛 `invalid()` ⇒ **此后任何新提交都被拒绝**，且该错误码是通用"请求非法"，UI 无任何"资源已满"提示 ⇒ **只能重启应用**。
- **【推断】风险**：可用性中断（长会话）。**无数据损坏**（引擎侧不变量未被破坏）。
- **【观察】6｜覆盖缺口**：17 次真实 commit 回归（`tests/unit/t01-mainline-real-runtime.test.ts:490–640`）使用 **17 个全新 operationId**，且每轮断言 `expect(value.replies.diagnostic().slots).toBe(0)`（即每轮都被 ACK 并成功退休）⇒ **该测试从未执行过一次"失败的提交"**，本泄漏完全未被覆盖。
- **严重度**：**Medium–High**。属上一轮 M4 修复（把上限从 `#intents.size` 移到 `#fullIntents.size`）相邻区域的回归缺口。
- **建议**：把 intent 加入 `#fullIntents` 的时机改为**真正持有完整 payload 之后**（或在任何失败路径上以原 operation 身份释放该槽），并补一条**产品路径级**测试：N 次失败提交后第 N+1 次提交仍可用；同时把 `:735` 的容量拒绝映射为可操作的错误码（当前 `invalid()` 与"请求非法"混同，见 MM 历史 §4.3 的同类观察）。

### 4.3 【Medium｜可用性｜观察+推断】**新发现**：UNKNOWN delivery 永不回收，引擎侧 16 槽账本单调劣化；8 次"提交期间切换项目"即可同时烧尽引擎槽与 IPC 槽

- **位置**：`engine.ts:978`（**唯一**的 `#mainlineDeliveries.delete(...)`）、`:771`（`#mainlineDeliveries.size >= 16` ⇒ 抛错）、`:820–823`（`#unknownDelivery`）、`:926`（`ok===false` + 已有 alias ⇒ 转 UNKNOWN）、`:939`（回调抛错 ⇒ 转 UNKNOWN）、`:2090–2091`（引擎退出 ⇒ 转 UNKNOWN）；`desktop-ipc.ts:142`（**唯一**的 `deliveries.delete(id)`）、`:164`（`deliveries.size >= 16`）。
- **【观察】1**：本轮 grep 列出 `#mainlineDeliveries` 的**全部 10 处**使用点 —— **不存在任何 `.clear()`，也不存在除 `:978` 之外的 `.delete()`**。而 `consume()` 要求 `delivery.state === 'OFFERED'`（`:953`）⇒ **UNKNOWN delivery 永远无法被消费、永远不会被删除、其 bytes/objects 永不退还**。
- **【观察】2**：`:771` 的容量门因此变成**单调劣化**的账本：**跨引擎重启也不清零**（引擎重启只换 session，不换这个 Set）。
- **【观察】3｜自然触发（不需要故障注入）**：`project-mainline-service.ts:788` `budget.handoff(accepted)` **先于** `:789` `if (this.source.current() !== current) throw denied()`。⇒ **用户在提交往返期间切换项目** ⇒ `#run` 捕获 ⇒ BridgeResult 为 `ok:false`，而 `delivery.aliases` **非空**（已 handoff）⇒ `engine.ts:926` `result?.ok === false` ⇒ **该 delivery 被转为 UNKNOWN 并永久保留**；随后渲染端 ACK 时 `consume()` 因 `state !== 'OFFERED'` 抛错 ⇒ `desktop-ipc.ts:142` 的 `deliveries.delete(id)` 被跳过 ⇒ **IPC 槽也永久占用**。
  ⇒ **一次切换竞态 = 烧掉 1 个引擎槽 + 1 个 IPC 槽。8 次即同时打满两个 16 槽账本 ⇒ 整个 project/query 面永久 `PERMISSION_DENIED`，且跨引擎重启不可恢复，只能重启应用。**
- **【观察】4**：其余 UNKNOWN 来源（`engine.ts:939` 回调抛错、`:2090` 引擎退出、`:2502` 请求超时）同样只进不出。
- **【推断】风险**：可用性中断 + 预算永久性收缩；**无数据损坏**。
- **严重度**：**Medium**（需 8 次竞态或 16 次故障；概率低于 §4.1，但完全无自愈）。
- **建议**：为 UNKNOWN delivery 引入**有界**回收（例如按 session/frame 失效事件释放容量，**不得**把未确认投递当作"已投递"），并把 `deliveries` 与 `#mainlineDeliveries` 的回收责任**唯一化且可达**；同时为 `ok:false` + alias 的 UNKNOWN 路径补测试。

### 4.4 【Medium｜延续未修｜观察+推断】跨引擎会话后创建/示例的原回执永久不可对账（M2）

- **位置**：`packages/engine/src/ontolearn_engine/project/project_lifecycle.py:82–102`（`origin_value` 强制 `hostClientId` 与 `engineSessionId` 均为 36 位 UUID）、`:465–470`（空白项目创建认领比对）、`:1027–1031`（示例创建认领比对）；`apps/desktop/src/main/engine.ts:1174–1181`（每次握手新铸 owner）、`:2220` 附近（`clientId: randomUUID()`）。
- **【观察】1**：本轮**亲自逐行**复核：`origin_value` 要求 `set(value) == {"hostClientId","engineSessionId","permission"}` 且前两者长度必须为 36 且为 UUID；两处认领命中均要求 `old["context"]["origin"] == origin` **全等**，否则 `"identity"` 故障（对应 `errors.json` 的 `IDENTITY_CONFLICT`）。
- **【观察】2**：引擎会话 id 逐握手更换 ⇒ **新会话重提同一创建操作必然冲突**。
- **【推断】触发**：引擎在已持久化提交之后、回执抵达渲染端之前崩溃 → 用户以同一 `operationId` 重试 → `IDENTITY_CONFLICT`，**原回执不可取回**，UI 停留在"创建结果尚未确认"。
- **【推断】风险**：**不会**产生重复项目/草稿（守卫有效），但原回执永久不可取回。与 §4.1 复合时（引擎死亡 ⇒ 既 poisoned 又 identity-mismatch），最需要时对账不可达。
- **严重度**：**Medium**。**限制未修复，不称闭合。** 与已采用合同一致：不得删 origin、不得新增持久意图账本。
- **建议**：把"操作身份"与"会话身份"解耦——认领比对基于**稳定的请求指纹**（业务语义 + 目标项目 + 输入摘要），会话信息仅作审计元数据。

### 4.5 【Medium｜延续未修｜观察+推断】未 ACK 的 IPC 投递永不回收，16 次后主链路永久拒绝（M3）

- **位置**：`desktop-ipc.ts:105–113`（`deliveries` Map）、`:142`（**唯一** `deliveries.delete`，位于精确 ACK 路径）、`:164`（`if (deliveries.size >= 16) return permission()`）、`:176–181`（投递写入）；`preload/index.ts:40–42`（5s ACK 超时被吞）。
- **【观察】**：`deliveries` **只**在 ACK 路径删除，**无过期、无驱逐、无容量回收**；**同一函数内**的 `accepted` Map **有** FIFO 驱逐（`:144`）⇒ 这是有意的不对称，设计注释亦明写「No timeout, navigation or new session deletes an unacknowledged receipt」。
- **【推断】触发**：渲染进程崩溃/重载/导航发生在主进程回复与 preload ACK 之间 ⇒ 槽位永久占用；累计 16 次 ⇒ 全部 `project:*`/`query:*` 永久 `PERMISSION_DENIED`。
- **风险**：可用性中断（应用被砖，需重启）。**无数据损坏。**
- **严重度**：**Medium**。**限制未修复，不称闭合。** 与 §4.3 共用同一 16 槽量级，但**不共用同一容器**（IPC 侧 vs 引擎侧）。
- **建议**：为 `deliveries` 增加与 `accepted` 对称的**有界驱逐**或按 `WebContents` `destroyed` 事件释放。**释放租约仍须以"精确 ACK"为授权依据；驱逐只回收容量，不得让未确认投递变成"已投递"。**

### 4.6 【Medium｜发布义务｜观察】打包产物无签名、无公证、无可分发目标

- **位置**：`apps/desktop/electron-builder.yml`（`mac.identity: null`、`mac/win/linux` 均 `target: dir`）；实物 `outputs/20261024_t11_package087_actual_001/frozen-artifacts/release/mac-arm64/OntoLearn Studio.app`。
- **【观察】1**：本方对 package087 实物目录**亲自 `os.walk` 复算**：`.app` 合计 **549 文件 + 361 目录 = 910 条目**；`Contents/Resources` 下 **290 个常规文件**；`Contents/Resources/engine` 下 **225 文件 + 41 目录 = 266 条目**；`app.asar` **19 014 603 B**。⇒ 与 ROOT 受理票数字**逐个吻合**（§7）。
- **【观察】2**：`identity: null` + `target: dir` ⇒ **无签名、无公证、无 .dmg/.pkg/.msi/.deb 安装产物**。
- **【推断】风险**：他人 Mac 上 Gatekeeper 拦截/降信；无安装/升级路径。**属既定发布义务（decision D5 明示本轮不签），不是代码缺陷**，但对"对外分发"是硬阻断。
- **严重度**：**Medium**（对内部演示无影响；对外分发是硬阻断）。
- **建议**：正式阶段设 `mac.identity`（Developer ID）、开 `notarize`、改 `dmg`/`pkg` 目标。**该改动必然改变产物字节 ⇒ 必须重新出包并重跑打包态 E2E。**

### 4.7 【Medium｜数据韧性｜观察】无用户级备份/恢复入口；损坏 SQLite 物理 HOLD 未关闭

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:95–101`（legacy 损坏 kind 显式拒绝，注 "explicit repair required"）、`:148–168`（v2→v3 迁移备份）、`project/format3.py:158–187`（`migration_backup`：目标必须不存在、`PRAGMA integrity_check == ok`、源逻辑哈希在备份后**复查**）；数据文件为单文件 `userData/engine.sqlite`。
- **【观察】**：迁移备份是**强制且可验证**的（好的一面）；但**没有应用内项目导出/备份/恢复入口**，损坏库的唯一路径是拒绝启动并要求手工文件级操作。
- **【推断】风险**：磁盘故障或误删整库 ⇒ 用户数据不可自救。完整性方向设计强（原子提交 + 不可变证据 + 快照），风险集中在**可用性/数据所有权**。
- **严重度**：**Medium**。
- **建议**：正式阶段提供项目级导出/备份入口（可复用快照机制）+ README/应用内说明数据目录与备份位置。**注**：PRD **FR-002** 明确要求"新建、打开、复制、重命名、归档和**导出项目**"，**FR-203** 要求附录 C 范围内 Turtle 的导入与导出——**本体/项目级导出当前未见实现**，这是 P0 条款缺口而非增强项。

### 4.8 【Medium｜发布前置｜观察】跨平台 / 参考设备 / 规模口径（D2）未实测

- **【观察】**：本轮实测仅 macOS 15 arm64；e2e 的 2 条跳过是**真实平台条件**（`tests/e2e/i04-jobs.spec.ts` 源码条件 `process.platform !== 'linux' || !fixturePath`，另一条另需 `I04_NATIVE_ISOLATED === '1'` + openbox/xdotool）——**不是隐藏失败**。Windows 打包与运行、参考老设备、容量/负载基线均未执行。
- **【推断】风险**：**不得**以 18 条 e2e 充当负载测试；本报告的所有规模判断均不外推。
- **严重度**：**Medium**（发布前置，非代码缺陷）。

### 4.9 【Medium｜功能完整性｜观察】T02 无独立 redo；撤销仅能作用于当前回执；本体事实表整表传输

- **位置**：`apps/desktop/src/renderer/src/ontology/mainline-session.ts:382–390`（`prepareUndo()` 无参，固定取 `this.#state.receipt`，代码自述「Undo is a new operation with a freshly read base, never an inverted local diff.」）、`OntologyMainlinePage.tsx:330–333`（唯一入口"预览撤销本次修改"）；引擎 `project/transactions.py` 的 `preview_undo` 可作用于任何有证据操作（含 undo 自身）；本体侧 `OntologyMainlinePage.tsx:48–54,175`、`OntologyPage.tsx:108–115,247` 整表传输 + 渲染层切片。
- **【观察】**：撤销是**服务端补偿性新事务**（不是本地反向 diff）；UI **无操作历史选择器** ⇒ 连续误操作只能逐次撤销；e2e 用例名写 "Undo/Redo" 而实际第二次操作是**再撤销一次**。本体事实/定义表**不是服务端分页**。
- **【观察】｜对照 PRD**：**FR-804 只要求"撤销本次 ChangeSet"**（并要求冲突时说明影响并暂停），**未要求独立 redo 或历史选择器** ⇒ 这是**功能缺口，不是规格违背**。
- **严重度**：**Medium**。

### 4.10 【Low–Medium｜工程卫生｜观察】开发 nonce 编译进生产产物；测试夹具随包分发；工作区星号依赖；超大文件；错误码可行动性

- **【观察】1**：`apps/desktop/electron.vite.config.ts:7` `const devNonce = randomBytes(18).toString('base64')` 在**模块顶层**生成并注入 main bundle，**对所有构建生效** ⇒ 每次构建 main 字节都不同。生产不可达（打包态 `devURL` 为 undefined），**无生产影响**，但它是 `BUILD-NONCE-DIFF.json` 必须逐字解释"仅一处 24 ASCII 字面量差异"的根因——该披露经本方复核**诚实且可核**（§7）。建议改为**运行时**在主进程生成开发 nonce。
- **【观察】2**：`electron-builder.yml` 整体拷贝 `packages/contracts/v2`（约 2.3 MB），其中 `fixtures.json` / `binding-regressions.json` 为**测试语料**（运行时实际只需 `registry.json`/`schema.json`/`errors.json`/`states.json`/`dependencies.json`）。**本方未逐字审其内容是否含业务数据 ⇒ 该子项记为无法确认。**
- **【观察】3**：`apps/desktop/package.json` 的 `"@ontolearn/contracts": "*"` 违反仓库自身"JS 直接依赖写精确版本"约定（workspace 链接故无 registry 供应链暴露，但允许静默漂移）。
- **【观察】4**：`engine.ts` 2623 行、`job_store.py` 2589 行、`semantic.py` 1627 行、`workspace-controller.ts` 1531 行——多项已超"2000 行"清单线。
- **【观察】5**：`SafeError.messageKey` 携带但从不渲染（`typed-results.ts` 与面板直接拼固定码），错误可行动性弱于其设计意图；`task-presentation.ts` 对缺失/非数值参数直接 `Number(...)` 插值，可渲染"建议等待 **NaN** 毫秒"。
- **严重度**：**Low–Medium**（可维护性 + 少量 UX 瑕疵；不为本轮清理而扩建功能）。

---

## 5. 未进 Top 10 但保留的阻断 / 验收缺口（全部原样保留，不清零）

| # | 严重度 | 问题 | 位置（均为本方源码实读） |
| --- | --- | --- | --- |
| 11 | Medium | **引擎侧 16 槽账本与 IPC 侧 16 槽账本是两份独立容量**，且引擎侧跨引擎重启不清零（§4.3） | `engine.ts:771` / `desktop-ipc.ts:164` |
| 12 | Medium | **`#mainlineRecords` 永不清理**：16 次引擎死亡后 `mainlineProjectClient()` 永久抛错，项目选择/创建全死 | `engine.ts:1167`（仅 `.set`@1310，无 `.delete`） |
| 13 | Medium | **本体事实/定义表整表传输 + 渲染层切片**，非服务端分页 | `OntologyMainlinePage.tsx:48–54,175`；`OntologyPage.tsx:108–115,247` |
| 14 | Medium | **两处 Turtle 直连 `SinkParser` 未做字节上限**，绕过 `_parse_turtle` 的 1 MiB 限制（`_utf8_bound` 辅助已存在但未用） | `semantic_scopes.py:125–129`；`semantic_execution.py:279–283`（对照 `semantic_turtle.py:121–133`） |
| 15 | Medium | **撤销影响面板用渲染层投影计算**（`entityDeletionImpact`）而非引擎影响文档，具误导权威性 | `OntologyMainlinePage.tsx:129–136`；对照 `mainline-api.ts:91` |
| 16 | Medium | `workspace-controller.ts` 的 `finally { this.set({ busy:false }) }` **无条件清 busy**（即使已被围栏），可短暂在写操作在途时重新启用按钮 | `workspace-controller.ts:527,536` |
| 17 | Medium | **工作区/项目切换无焦点管理、无区域播报**；`<a href>` 置 `aria-disabled` 但仍可聚焦且仍带 `onClick` | `App.tsx:156–170,504,514,525` |
| 18 | Low–Medium | **CSV 导出的公式注入护栏在当前 N3 数据形态下不可触发**（真实单元格以 `"` 或 `<` 开头），且**导出字符串无显式字节上限** | `typed-results.ts:252–272` |
| 19 | Low–Medium | **查询历史列表用新页替换旧页**（非累积），且只有"下一页"无"上一页"，早先页从列表消失 | `workspace-controller.ts:1289`；`QueryWorkspacePage.tsx:652–657` |
| 20 | Low–Medium | **渲染层无 `AbortController`/请求取消**，陈旧响应只靠计数器抑制，底层 IPC/引擎工作仍跑到完成 | 渲染层全局 grep 无匹配 |
| 21 | Low–Medium | `App.tsx` 的 `queryControllers` Map **从不清理**，每个打开过的项目永久保留 controller/历史 jobs/冲突表 | `App.tsx:45,92–96` |
| 22 | Low | **`mainline-session.ts` 的用户主动 `read()` 若在 capture 与微任务之间序列号变化则被静默丢弃**（调用方得到已 resolve 的 Promise，无反馈） | `mainline-session.ts:328–334,430–432` |
| 23 | Low | **主体事实软删除（`object=NULL` 墓碑）与手工事实硬删除并存**，语义分层需文档说明 | `storage.py:729–737`；`rdf_snapshot.py:54` |
| 24 | Low | **`Coordinator.seen` 为整个 session 生命周期保留每个请求 id**（硬上限 65536，超限 session 致命） | `coordinator.py:155,282–284` |
| 25 | Low | **内部异常消息内嵌原始事实值**（subject/predicate/owner/source_row/id）。当前 `classify` 只转发 `.code/.params` ⇒ **潜在**泄露，非当前泄露 | `storage.py:767–773`；`coordinator.py:93–94` |
| 26 | Low | **重复撤销报 `INVALID_STATE` 而非幂等 no-op**。**保留原样**：原 operation 幂等与"以新 operation 再次撤销"语义不同；ABA/后续修改冲突必须保留（**这是优点**） | `compensation.py:187–188` |
| 27 | Low | **`createIntent` 仅存内存**（React ref），重启后同名可再建一个项目；引擎侧以 `operationId` 去重故不重复创建，UI 已给诚实提示 | `App.tsx` `createIntent` ref |
| 28 | Low | **`create_project` 存在绕过版本化直接写库的内部 API**（不写 `operation_claims`/`app_receipts`）。**当前不可从协议到达**（仅 probe 与测试调用）⇒ 潜在暴露 | `storage.py:259–267`；`job_store.py:637–643` |
| 29 | Low | `project/workspace.py` **仅被测试引用，无任何生产模块 import**；其易失草稿语义易被未来 UI 误当持久草稿 | `workspace.py:1–6` |
| 30 | Low | `OntologyPage.tsx` 的客户端重建 Diff 渲染器**无生产调用者**，一旦接线即暴露非权威 Diff | `OntologyPage.tsx:35,156,550–578` |
| 31 | Low | **墓碑/硬删除语义、`Coordinator.seen` 上限、e2e `mkdtemp` profile 目录从不删除**（测试卫生） | `tests/e2e/isolated-desktop.ts:13` |
| 32 | Low | **无 `CHANGELOG.md`、无 Terms/Privacy**；`appId: io.github.nomorejoke.ontolearnstudio` 仍为个人/项目名而非组织名 | 仓库根；`electron-builder.yml` |
| 33 | Low | **Dependabot 只覆盖 npm 与 github-actions，未覆盖 Python**（SECURITY.md 声明 Python 为手工 `uv lock --upgrade`） | `.github/dependabot.yml` |
| 34 | Low | **单元层存在弱断言模式**（`toHaveLength(0)`/`toBeDefined()`/`toBeTruthy()`/`toBeGreaterThan(0)`）；**e2e 层未发现仅断言数量或仅"按钮可点"的用例** | `tests/unit/**`（grep） |
| 35 | Low | **首次丢回复 e2e 的注入点在 IPC 回复层**，**不覆盖引擎→主进程这一腿的丢失**，也不覆盖"引擎已提交但主进程尚未持久化即崩溃" | `tests/e2e/mainline-consumer-first-ack-loss.spec.ts` |
| 36 | Low | 引擎内 **8 个被 import 但不存在的模块**（`ontolearn_engine.quality.*` 与 `semantic_profile_*`）——**死代码悬挂 import**，profile 分支当前不可达（`reasoning.execute` 的 `implementation` 为 `design-only`；`execute_profile*` 全仓无调用者）⇒ 运行期不是故障，但若将来接线会被 `except Exception` 吞成静默降级 | `semantic.py` / `semantic_execution.py` / `semantic_turtle.py` 多处 |
| 37 | Info | **并发主链路调用直接拒绝而非排队**（无错投，良性并发产生硬失败） | `engine.ts:771`；`mainline.py:288` |
| 38 | Info | **撤销对账对每个后续 commit 调 `_with_retirements` ⇒ 长历史下 O(n²)** | `compensation.py:177–186` |
| 39 | Info | 已退役项目的 session 会读写**另一项目**的全局 book 条目（局部状态写入仍受 `projectId` 门禁） | `mainline-session.ts:166,169` |

---

## 6. 任务书指定的五条边界 —— 本轮独立追踪结论

### 6.1 创建 / 示例复制 / 补偿 / owned draft / 重启
- **创建**：严格 4 字段 request + 严格 3 字段 origin（`permission` 必须是字面量 `library.create`，`project_lifecycle.py:82–102` 逐字复核）；认领命中要求 `request` 与 `origin` **双双全等**（`:465–470`）；否则走 `_occupied_operation_evidence` 拒绝跨项目/跨轮次采纳。
- **示例复制**：两阶段、replay-first；认领命中从不可变上下文闭包服务，且要求 origin 全等 + 重算回执相等；否则从哈希钉死的 bundle 根读取（绝对路径 + `O_NOFOLLOW` + `S_ISREG` + 尺寸 + 前后 `fstat` dev/ino/size/mtime 比对 + manifest SHA-256 等于 bootstrap pin）。
- **补偿**：纯函数、零 SQL 写入；ABA 防护显式；`trusted_snapshot` 拒绝未来快照；退役成员从不可变历史重建。
- **owned draft**：**两套机制需区分**——持久草稿 = `app_drafts` + 逐 `(project, editor)` 代际 CAS（同时校验 `expectedGeneration` 与 `boundDomainRevision`）；`DraftWorkspace`（`workspace.py`）是**易失编辑器会话，仅被测试引用、无生产 import**（§5 #29）。
- **重启**：`reconcile_jobs` 在取得 OS 独占写租约**之后**把非终态 Job 判失败/取消（`ENGINE_EXITED`），注释明确 "marker alone can never invent success"；`format3.validate` 启动期只读复核**每个项目的全部历史**；写租约在进程死亡（含 SIGKILL）时由 OS 自动释放。
- **判定：实现与证据一致，本轮未发现该边界的新缺陷。（观察）**

### 6.2 T02 完整 Diff / commit / undo / redo 与原操作回执
- **Diff 是引擎文档而非客户端重建**（本轮逐行复核 `mainline-diff.ts`）：manifest 边界（`totalBytes ≤ 16 MiB`、`segmentCount ≤ 512`、段数与声明一致）、**字节偏移连续性**（逐段 `byteOffset` 与累计长度核对）、**逐段 SHA-256 重算比对**、`documentHash` 一致性、严格 UTF-8 解码；确认按钮仅在全部行展示后可用。**例外**：`OntologyPage.tsx:550–578` 存在客户端重建的 Diff 渲染器，**无生产调用者**（§5 #30）。
- **commit 绑定单一原操作身份**：一次确认时刻铸造唯一 `operationId`，同时用于写入、对账与回执；回执**只**由真实引擎 marker 产生（校验 projectId / operationId / planHash(64 hex) / beforeSnapshotId / projectRevision > baseRevision / afterSnapshotId / jobId，且 Job 必须 `succeeded` + `commitProgress.mode === 'atomic'` + marker 相等），不匹配即 `INVALID_RECEIPT`。
- **重试不重铸身份**：查询侧恢复路径以**同一 operationId + 同一 confirmation** 重放。
- **undo 是服务端补偿性新事务**（`intent='undo'` + 全新 base 读取），冲突面逐资源比对；**固定作用于当前回执**，无操作历史选择器、无独立 redo（§4.9）。
- **判定：与 e2e 一致；redo 与历史选择器为真实功能缺口（且不构成 FR-804 违背）。（观察）**

### 6.3 T04 分页 / 历史快照 / 导出
- **分页是服务端 cursor**（keyset），非客户端切片；行页与文本页均带游标连续性、UTF-8 字节区间与 EOF 一致性校验；历史列表用钉死的 `listSnapshotId` + 严格单调 `(createdAtMs, jobId)` 排序；结果身份（`resultId`/`payloadSha256`/`inputSnapshotId`/`inputProjectRevision`）在每页重验，不匹配即拒绝展示（`job_store.py` 多处 `inputSnapshotId` 不等即拒绝）。
- **导出**（本轮逐行复核 `typed-results.ts:252–272`）：CSV、CRLF、`""` 转义、公式注入缓解（`/^[\s]*[=+\-@]/u` 或以 `\t\r\n` 开头前置 `'`）、**仅当前页**（代码自述 "never fetch or accumulate more rows"）；**UTF-8 BOM 由调用方添加**（`QueryResultPanel.tsx:17` `new Blob(['\uFEFF', csv])`）；**导出字符串无显式字节上限**。
- **本体事实/定义表整表传输 + 渲染层切片**，该子路径不满足"page 400"（§5 #13）。
- **判定：T04 查询路径实现与验收一致；全量导出与本体表分页为真实缺口。（观察）**

### 6.4 首次 ACK 丢失 / 项目切换隔离
- **首次 ACK 丢失的注入点在 IPC 回复层**：真实 handler 先执行并断言返回了成功的投递信封，随后抛错使渲染端 Promise reject ⇒ **引擎真实执行，仅丢失回执投递**，无伪造回复、无 Job 抑制。断言为**真实语义**：`commitCalls === 1`、`executeCalls === 0`、`lostAckCalls === 0`、最终请求与首次请求逐字节相等（同一 operationId、同一 confirmation），并以**真实 `listJobs` 全量清点**断言项目中恰好一个 Job；对账用真实 `getOperation`/`getJob`，marker 深度相等。查询变体：重发同一请求后引擎返回**同一 operationId 与同一 acceptedJob**（仅投递 id 不同）⇒ 证明是幂等重取而非重执行。
- **切换隔离**：逐个缓存核对了键——本体操作簿（按 projectId）、查询 controller（按 projectId）、`QueryWorkspaceController.projectId`（构造期不可变）、草稿恢复（`preview.projectId === source.projectId`）、`checkRead`（`read.projectId === this.projectId`）、session↔project 绑定 ⇒ **均不跨项目**。
- **⚠️ 本轮发现的切换侧缺口（新增，§4.3）**：隔离本身成立，但**"提交往返期间切换项目"会把该次投递永久转为 UNKNOWN**，同时毒化 owner record 并烧掉两个 16 槽容量。⇒ 隔离的**正确性**无问题，**失败时的资源处置**有缺口。
- **⚠️ 未覆盖**：`engine→主进程`这一腿的丢失、以及"引擎已提交但主进程尚未持久化即崩溃"（§5 #35）。
- **判定：隔离语义正确且有真实证据；失败路径的资源回收有缺口。（观察 + 推断）**

### 6.5 main / task / engine session / epoch / 权限 / 持久 Job / marker / noReplay
- **四个不同的计数器已分清**：引擎 session id（引擎在 hello 中签发，每条通知须匹配）、引擎进程 generation（每次 spawn 自增，`#current()` 要求同代）、task view generation（`clearView` 自增）、主链路选择 epoch（每次重选项目自增，嵌入每个 recovery principal 并在 `current()` 复检）。
- **权限/信任模型**：桌面宿主是唯一 principal；线上协议**永不**提供 store/permission/scope/implementation/read ticket；`allows_owner` 要求 host/actor/store/session/ordinary/mainline **全部**同一；越权访问非当前项目 → `PERMISSION_DENIED`（仅 `project.open` 可命名未选中的目录 id）；`host_client_id` 明确是"受信 stdio 客户端的归属，**绝不是**人类同意的证明"——同意由显式确认摘要承载（`CONFIRMATION_MISMATCH`）。
- **持久 Job**：TS 侧**无**持久 Job store（"Durable job outcomes always come from SQLite queries"）；Job 结果恒从引擎重读（`job.get` / `operation.get`）。
- **marker / noReplay**：marker 与回执/终态**同事务**落库；`reconcile` 在 marker 缺失时返回 `uncommitted` 且**永不授权自动重试**；`operation_get` 纯从不可变 marker 解析；TS 侧 `reconcileMarkers` 交叉核对 `job.commitProgress.marker` 与 `operation.get`，不一致即 `invalid`。
- **引擎退出观测**：stdout end / stdin error / error / close **四条路径全部路由到 `#finish`**（`engine.ts:2085–2118`：标记终态、投递转 UNKNOWN、拒绝在途请求、SIGTERM → 1s 后 SIGKILL 升级、发出 `EngineConnectionState`）。
- **重启**：惰性（下次请求触发）、退避 100ms→2s、60s 内最多 5 次；新会话拿新 `engineSessionId` + 自增 generation，旧投递转 UNKNOWN、旧 principal 不可再采纳 ⇒ **epoch 权威被保持**；**新 owner record 会在旧会话失效时被铸造**（`engine.ts:1164–1167`）⇒ 这是 `uncertain` 闩锁（§4.1）与跨会话创建限制（§4.4）的**共同逃逸条件**。
- **判定：除 §4.1–§4.4 的生命周期/容量缺陷外，实现与证据一致。（观察）**

---

## 7. 证据链独立复核（本方逐项亲自复算）

| 证据 | 本方独立核验 | 判定 |
| --- | --- | --- |
| 附件 25000 B / `e896810d…` | 实测字节与 SHA256 | **一致** |
| 清单 11255 B | 附件第 45–214 行提取实测 11255 B，SHA `1ca23def…f709c` | **一致** |
| 远端 develop `5f910b52` | 本轮**亲自**只读 `ls-remote origin refs/heads/develop` | **一致** |
| HEAD `748008a6` / base / merge-base | `rev-parse` / `cat-file -t` / `merge-base` | **一致** |
| 38 commits / 525 files | `rev-list --count` = 38；`diff --name-only` = 525；`+561064 / −4638` | **一致** |
| AGENTS.md `15147B/de15f6ce…` | 实测字节与 SHA；工作区唯一 M 项；**未修改** | **一致，未修改** |
| 索引 `173116B/0bd0667b…` + cached diff 空 | 索引文件实测字节与 SHA；`diff --cached` 0 行 | **一致** |
| S1270 闭集 `223577B/ebf3328e…` | 实测字节与 SHA | **一致** |
| **S1270 内容复算** | worktree 内逐条重算 **1270/1270 一致，0 缺失 0 不符**；与 `ls-tree -r HEAD` 路径集**完全相等**（均 1270） | **一致**（闭集含未暂存 AGENTS overlay，见 §1） |
| whole087 单次完整 check 自然 0 | `check-full-087-receipt.json` 实读：`argv = npm run check`、`naturalExit: 0`、`observedExit: 0`、`timeout: false`、`sourceUnchanged: true`、`changed: []`、`logBytes: 21634`；`cwd` 为 N 侧 `node-checkout` | **一致** |
| **"JS 未在 748 重建"的诚实性** | `BUILD-NONCE-DIFF.json` 实读：`oldMain.sha256 = 847fa7e5…` vs `newMain.sha256 = 83d82b19…`（两文件均 594342 B）、`allOtherMainBytesEqual: true`、`remainingFourOutputsEqual: true`；根因定位到 `electron.vite.config.ts:7` 的 `randomBytes(18)`（本方逐行复核该行，**确认其为模块顶层、对所有构建生效**） | **一致且诚实**：不可称"748 重新 build" |
| package087 实物闭包 | 本方 `os.walk` 亲自复算：APP **910**（549 文件 + 361 目录）、Resources **290** 常规文件、engine **266**（225 + 41）、`app.asar` **19 014 603 B** | **与受理票数字逐个吻合** |
| ROOT 受理票 | `107285 B / 41e81bd99baa82079c97e0653efbd0f481a07f1b04f1eb75b54280036d48e7f5` 实测吻合；`signedReleaseGate: false`、`legalFullClosureAccepted: false`、`mechanicalClosureOnly: true`、`formalReleaseAccepted: false` | **一致**（正式门仍未闭） |
| e2e actual002 | `ENTRY.json` 实读：`sourceHEAD = 748008a6…`、`status = ORIGINAL18_COLLECTED_16PASS_2_ORIGINAL_PLATFORM_SKIPS_NATURAL0`、`naturalCoordinatorExit/naturalWrapperExit/naturalNPMTestExit = 0`、`timeout: false`、`actualCollected: 18`、`ACTUAL_PASS: 16`、`CONDITIONAL_SKIP: 2`、`profileBindings: 16`、`allOwnedProfileBound: true`、`actualGettersMissingRemainUnknown: true`、`observerSamples: 214`、`observerErrors: []` | **一致**（缺 getter 仍记未知，未洗成观测） |
| 2 条 skip 是真实平台条件 | 回源码 `tests/e2e/i04-jobs.spec.ts` 平台条件 | **一致，非隐藏失败** |
| 三 SOURCE005 在途模式 | `ACTUAL-RUNTIME-RESULTS.json` 实读：`reload` / `renderer-recovery` / `coordinator-exit` 均 `faultApplied: true`、`result: PASS`，**无 NOT_EXERCISED** | **一致** |
| **native 原件与时间戳（本轮纠正核对）** | `frozen-original/native-lifecycle/actual-native.json` 实测 **11713 B / `e152a3462ac10b24eb34607015d86ed7fa9b40f7b12778897b438fb27fc611e9`**；实测事件：`before-quit` seq **4** @ `2026-10-24T03:39:00.131Z`、第三窗口 `closed` seq **5** @ `03:39:00.143Z`、`will-quit` seq **6** @ `03:39:00.143Z` ⇒ **与任务书的补充事实更正完全一致**；上一轮 MiniMax `_001` §5 使用的 `03:36:41.542Z/03:36:41.650Z` 确为 coordinator 清理时间，**不是 native** | **一致；上一轮该处时间混用确认存在** |
| 086 首败保留 | `actual002/ENTRY.json` 的 `original086TestFailurePreserved: true`；失败 trace `18686 B / 216e2890…` | **一致（旧失败未被洗白）** |
| 087 外部 guard 首败保留 | `actual_001/ENTRY.json`：`productCaseAttempts: 0`、`wrapperNpmAppStarted: false`、`actualGUISteps: 0` ⇒ **外部 guard/元数据错误，不是产品失败** | **一致** |
| "无显式 CREATE INDEX" | 引擎 `packages/engine/src` 全量 grep `CREATE INDEX` = **0 处**；但 `format3.py:76` `UNIQUE(project,event_id)`、`:86` `PRIMARY KEY(project,sequence),UNIQUE(project,operation)` ⇒ SQLite 会为 UNIQUE 约束建隐式索引 ⇒ **"仅主键隐式索引"的表述过窄，不能据此断言全部查询无索引** | **与任务书补充更正一致** |
| 历史四份报告与处置 | 085 两份 + `intent_lifecycle_fix_001` 处置经只读子代理逐字提取并由本方交叉复核；748/package087 的 MiniMax `_001` / ZCode `_001` / 处置记录由**本方本人全文读至 EOF** | **已读，结论见 §3、§9** |

---

## 8. 用户 11255B 清单逐项适用性判断（160 引用行；147 产品 + 13 人员）

> 原则：**先判适用性**；不适用按**类别**简述依据；**适用但未核实写"无法确认"**；不为满足清单给本产品扩建无关功能。
> 本产品形态：**本地优先、单用户、离线、无服务端、无网络端口、无账号体系、无计费、无模型接入**。因此清单大部分条目属服务端/SaaS 形态，按类别不适用——但这是"当前形态不适用"，**不是"已具备"**。

### 8.1 整类不适用（按类别简述依据）

| 类别 | 覆盖的清单条目（按清单原文顺序） | 不适用依据 |
| --- | --- | --- |
| 账号与身份 | login（+号邮箱）、密码重置链接、MFA 及其恢复、会话超时与全量会话吊销、SSO、SAML、SCIM、深于 admin 的角色、按 URL 改号越权、租户隔离、管理员"登录为该用户"及审计、登录限流、防 CFO 误锁 | 无服务器、无登录、无多用户/多租户。IPC 侧以 sender/frame/文档三重校验替代。**注：一旦引入"接收他人项目文件"或团队共享，该整类立即适用且当前为零基础** |
| 支付与计费 | 订阅/升级/降级/按比例、失败扣款与催缴、发票与 PO 号、销售税/VAT、退款/信用额度/部分退款、用量计量到分、年约定制条款、财务对账报表 | 无任何货币处理（"money stored as integers"随之不适用） |
| 对外 API 生态 | 版本化对外 API、客户 API key 与吊销、API 限流、第三方 API 响应格式突变预案、OAuth token 刷新、集成沙箱、webhooks 签名与重试日志 | 无对外 API/webhook；引擎协议是**私有 stdio 契约**（`registry.json` + `schema.json` 双端校验 + 固定错误码表），本身即"designed schema" |
| 邮件 | SPF/DKIM/DMARC、退信与投诉处理、邮件客户端渲染 | 不发邮件 |
| 云基础设施 | dev/staging/prod 对齐、IaC、零停机、一键回滚云语义、功能开关、自动扩缩、CDN、DNS/SSL 续期、第二区域、DR 年度演练、状态页、成本告警 | 无云服务、无网络端口（`connect-src 'none'` + 引擎 audit hook）。本地等价物已核：CI 完整门禁；回滚 = 上一目录包 + git 还原（流程层） |
| 观测与值班 | 3am 可搜结构化日志、错误聚合、外部拨测、告警 paging、延迟/错误率/吞吐仪表盘、跨服务 tracing、on-call 轮值、runbook、postmortem、状态页 | 无运行服务可观测。产品以**零日志策略**为隐私设计（主进程零 console/零日志文件；错误只出固定码受限参）。**有意取舍，非缺失**；若接入模型网关需重评 |
| 合规套件 | SOC 2、HIPAA、BAA、PCI scope、GDPR 全表/备份/日志删除、数据驻留、季度权限复核、渗透测试、安全问卷证据包、企业买方尽调 | 不处理 PHI/卡号/第三方 PPI，无企业买方。`SECURITY.md` 已含私有披露约定。转为"首个企业客户前的义务" |
| 流量与规模 | 连接池、周一尖峰、负载测试、5M 行索引超时 | 本地 SQLite 单写者 + 独占租约；分页/导出边界已设硬顶。**容量与老设备口径属 D2 未执行项**（§4.8） |
| 队列与调度云侧 | cron 双跑、死信队列、存储生命周期规则 | 无定时任务、无队列服务、无按量云成本 |
| 通知 | "notifications people can turn off" | 应用无通知系统 |

### 8.2 适用且本轮已核（有实现与证据）

| 清单条目 | 结论与依据 |
| --- | --- |
| a schema someone designed, instead of one the AI improvised table by table | ✅ 契约驱动：`packages/contracts/v2/schema.json` + `registry.json` + `errors.json` + 契约 fixture；双端执行（TS zod `.strict()` + Python `contract_v2.py`）；canonical JSON 拒 NaN/代理对 |
| validation on the server, not just in the form | ✅ 等价已核（无服务端）：主进程 zod `.strict()` + 引擎契约校验双重；每错误码 `paramsSchema` 且 `additionalProperties:false`，`maxEncodedBytes: 2048` |
| input sanitization everywhere a user can type | ✅ 边界数据一律 zod `.strict()`；引擎侧二次校验；标识符正则 `^[A-Za-z0-9_.-]{1,128}$`；自由文本走 RDF 字面量 |
| protection against SQL injection | ✅ 全量参数化（`?` 绑定）；动态标识符仅来自硬编码表名元组或 `sqlite_master` 转义读取；累计 diff 中**新增行内无 `execute(f"...")` 拼接** |
| protection against XSS, CSRF and the rest of the OWASP list | ✅ React 默认转义 + 单一 CSP 源；渲染端累计 diff 内 **0 处** `dangerouslySetInnerHTML`/`innerHTML`/`document.write`；无 HTTP 面故无 CSRF/CORS 面；`connect-src/object-src/base-uri/frame-src/form-action` 全 `'none'` |
| CORS rules that aren't "allow everything" | ✅ 不适用（无 HTTP 服务、不开端口），由 CSP + 引擎 audit hook 双重保证 |
| security headers on every response | ✅ 等价已核：本产品不产出 HTTP 响应；等价的"响应头"即 CSP meta/header（唯一源 `csp.ts`） |
| secrets out of the code, out of the repo and out of the AI chat history | ✅ 无密钥存在（无模型客户端）；`.gitignore` 排 env/key/pem/p12；引擎 env 白名单不继承 `PATH`/`PYTHONPATH`/代理/凭据 |
| rotating every key the AI pasted into a config file last month | ✅ 不适用（无物可轮） |
| confirming every package the AI installed exists and is the one you meant | ✅ 直接依赖精确 pin；`uv.lock` 含 sha256；新增 Python 依赖（pyshacl 0.30.1 / pyparsing 3.3.3 及传递依赖 owlrl 7.6.2、prettytable 3.18.0、wcwidth 0.9.2、html5rdf 1.2.1）**带锁文件与 sha256**；新增 npm 依赖 = 0；许可闭包已入库 |
| dependency scanning, because the AI pulled in libraries nobody reviewed | ⚠️ **部分**。Dependabot 覆盖 npm + Actions（Python 为手工 `uv lock --upgrade`）；**本轮未做 `npm audit`/`pip-audit`**（无网络）⇒ 第三方 advisory 状态**无法确认** |
| file uploads that get scanned, size-limited and stored where they can't execute | ✅ 无用户上传面（导入 = 打包内置示例资源，路径由主进程硬指定并经 `O_NOFOLLOW`/绝对路径/`S_ISREG`/TOCTOU 复查） |
| encryption at rest and in transit | ⚠️ **部分 / 无法确认**。传输 = 无网络（最强形态）；**静态 = SQLite 明文**（本地优先设计下的接受项，明示记录）。设备被盗场景无缓解 ⇒ 归入 §8.3 |
| least-privilege access for everyone, including the AI agent holding production credentials | ✅ 无模型客户端/无凭据；现有"代理" = 渲染层，受沙箱 + 闭合 preload + `trusted()` 三重校验约束；引擎无密钥无外联；特权引擎参数**仅由主进程构造** |
| logs that record who did what, without recording passwords, tokens or card numbers | ✅ 等价已核。领域动作以不可变 `commits`/`commit_evidence`/`operation_claims`/`job_details` 记录；原始字面值不写入审计；引擎 stderr 不转发 |
| a disclosure process for the day a stranger emails you a vulnerability | ✅ `SECURITY.md` 含私有渠道报告路径与"不要在公开讨论附凭据/业务数据/可利用细节"约定 |
| idempotency keys, so a retried payment doesn't charge the card twice | ✅ 等价（无支付）："重试不重复提交"已核。`operation_claims` 与副作用**同事务**写入，先于副作用落库；`job.create` 重放返回既有 job 且复验冻结上下文；e2e 实测首次 ACK 丢失零重放（§6.4） |
| deduplication for the user who clicks submit four times | ✅ 同一 `operationId` 命中认领即返回原回执；主进程**拒绝自动重放已输入写入**（`project-mainline-service.ts:751` `if (intent.unknown) throw denied()`） |
| pagination that still works on page 400 | ✅ **T04 查询路径**满足：服务端 keyset cursor + 绝对 startIndex、每页重验结果身份；⚠️ **本体事实/定义表是整表传输 + 渲染层切片**，该子路径不满足（§5 #13） |
| exports, because sooner or later every customer wants their data in a spreadsheet | ⚠️ **部分**。CSV 存在（CRLF、`""` 转义、UTF-8 BOM、公式注入缓解）且仅当前页（`typed-results.ts` 代码自述 "never fetch or accumulate more rows"），**无全量/JSON/XLSX**；导出字符串无显式字节上限。**对照 PRD**：FR-402 明确"大数据量导出不属于普通查询流程"⇒ 当前页导出与 FR-402 相容；但 **FR-002 的"导出项目"与 FR-203 的 Turtle 导入导出未见实现**（§4.7） |
| imports that survive the CSV someone saved in 2009 | ✅ 不适用（无用户 CSV 导入面）。**⚠️ 但 PRD FR-300（P0 支持 UTF-8 CSV 与 XLSX）尚未实现**——属 P0 功能未开工，不是本轮审查的缺陷 |
| retention rules, and code that deletes what your contract says you'll delete | ⚠️ **部分**。有缓存回收（`collect_cache` 排除 `result_pins`/`current_results`/`job_current`，仅置空 payload 保留结果身份）与游标 TTL（`ReadLimits.ttl_seconds = 60`）；**无按合同/用户策略的保留期规则** |
| a data model that survives your second customer asking for "one small change" | ✅ 版本化 schema + `migration_log` + 显式 v2→v3 迁移 + `PRAGMA user_version` 断言 + 启动期只读结构审计（逐表逐触发器比对并校验 `schema_hash`） |
| database migrations that run forward and roll back | ⚠️ **单向向前**（`version > target` → `UnsupportedProjectFormat`，**无降级路径**）。回滚 = 保留的迁移备份（文件级）⇒ **"run forward and roll back" 仅半满足** |
| migrations that don't lock the main table at 2pm on a Tuesday | ✅ 等价适用（单机桌面）：启动期持 OS 独占写租约（`flock LOCK_EX|LOCK_NB`）、`BEGIN IMMEDIATE` + `synchronous = FULL`；无在线迁移窗口 |
| a restore from those backups, tested | ❌ **未核 / 未建立**。迁移备份机制（强制新目标 + `integrity_check` + 源哈希复查）已核，但**未见"从备份恢复"的实测证据**（§4.7） |
| backups every night | ✅ 不适用（无服务器）。本地迁移备份存在，但**非常态备份** |
| point-in-time recovery for the day someone runs a delete without a where clause | ✅ 等价已核。SQLite 快照 + 不可变提交证据 + 显式补偿/撤销 ⇒ 无 `DELETE ... WHERE` 式破坏面。**这不是 PITR**（无 WAL 归档） |
| soft deletes, so "I deleted it by accident" is a support ticket and not an incident | ✅ 等价已核。领域以"退役（retirement）"显式建模，从不可变历史重建隐藏成员，并有"退役影响预览"；本体事实墓碑在快照中保留且不进入 RDF 图 |
| caching, and clearing that cache when the data changes | ✅ `invalidation-v2.json` 单一规则源；`collect_cache` 排除 current/pinned；结果身份保留、载荷可回收；`staleReason` 只由规则文件产生；**仅改模型配置不作废领域结果**；历史/失败/取消不计入过期原因 |
| undo | ✅ 已核。补偿为**服务端前向补偿新事务**（不改写历史），带 ABA 保护；e2e 实测 Undo 与 Undo-of-Undo 通过。局限见 §4.9 与 §5 #26 |
| a human approval step for anything the AI does that can't be undone | ✅ **结构性**已核。`registry.json` 逐能力声明 `agentEligible`/`requiresConfirmation`/`exposure`/`requiresChangeSet`；`changeset.preview`/`changeset.confirm` 为 `agentEligible = false` ⇒ **Agent 无法自我确认**；UI 确认按钮在完整 Diff 全部行展示后才可用 |
| code a human can read | ✅ TS `strict`；Python ruff（E/F/I/UP/B，line-length 100）；领域文件单一职责 + 模块级 docstring。**⚠️ 但多项已超 2000 行**（§4.10-4） |
| architecture decisions written down, with the reasons | ✅ `docs/architecture/0001-desktop-framework.md`、`0002-storage.md`、`0003-resident-coordinator-and-jobs.md` + `docs/iterations/**` |
| a README that gets a new engineer running locally in under an hour | ✅ 结构达标（`README.md` + `CONTRIBUTING.md` + `docs/development.md`）；**"一小时"未实测 ⇒ 无法确认** |
| documentation for whoever inherits this | ✅ `AGENTS.md`（owner 规则）+ `docs/prd|architecture|iterations|reviews` + `source-manifest` |
| a branching strategy, so two people can work without overwriting each other | ✅ 独立 worktree + `feature/<模块>-<子任务>` + PR 合回 develop；禁止共享 checkout 并行写；提交前缀规范 |
| code review on every change | ✅ 流程层面：指定双审 + CI + 远端核验门禁；**本报告即其中一环** |
| monthly dependency upgrades, so you're never two major versions behind | ✅ Dependabot（npm + Actions，weekly）。**⚠️ Python 侧为手工**（§5 #33） |
| framework upgrades before the old version stops getting security patches | ✅ 机制在（Dependabot + `uv lock --upgrade` 政策）。**⚠️ 实际补丁响应节奏无法确认** |
| unit tests written by someone who knows what the logic should do | ✅ Python 侧 60 文件 / 563 个 test 函数（AST 计数，前轮核）；TS 侧 35 文件 / 1694 测试。断言多为**具体预期集合与顺序**（本轮复核 17 次 commit 回归即断言 `job.create` **恰 17 次**、末次为 `job.get`、`final.domain.projectRevision === 17`）。**⚠️ 单元层弱断言模式**（§5 #34） |
| integration tests for every third-party API you depend on | ✅ 不适用（无第三方 API 依赖；仅 rdflib/pyparsing/pyshacl 三个固定版本库） |
| end-to-end tests for signup, checkout and the other flows that make money | ✅ 等价：18 条**真实 Electron + 真实 Python 引擎** e2e（16 PASS + 2 真实平台条件 skip），断言真实领域语义（完整 Diff 文档、marker 全字段相等、Job input/commitProgress、undo 后域状态、重启后同 profile 重读），**非"按钮可点"式冒烟** |
| regression tests, so fixing bug 41 doesn't bring back bug 12 | ✅ 专门回归集存在（`test_mainline_cleanup_regressions.py`、`binding-regressions.json`、`verify-frozen-review-sources.test.ts`、本次新增的 `t01-mainline-reply-lifecycle.test.ts` 清理失败重试用例） |
| test data that looks like production without being production data | ✅ 契约 fixture 与 `tests/fixtures/T04/` 为合成夹具；`.sqlite`/`.db`/`.env` 不入库 |
| empty states, loading states and error states on every screen | ⚠️ **部分**。`OntologyMainlinePage` / `QueryWorkspacePage` / `QueryResultPanel` 三屏均有专门空/加载/错误分支；**全屏覆盖度未逐屏核验 ⇒ 其余屏幕无法确认** |
| error messages a customer can act on, instead of "something went wrong" | ✅ 固定错误码 + `messageKey` + 枚举化参数；`safeDisplayError` 在主进程做展示投影；**不返回原始异常/堆栈/路径**。**⚠️ `messageKey` 携带但从不渲染**（§4.10-5） |
| background job queues, so slow work doesn't freeze the page | ✅ 已核。`JobStore` + 常驻协调器 + 取消 + 资源上限；查询/提交均走持久 Job + 订阅更新，UI 保持响应 |
| retries with backoff, so one flaky API call doesn't become a lost order | ✅ 已核。主进程侧三次尝试、250ms×2^(n-2) 退避、每次 15s 超时、attemptToken 使迟到回复无法授权下一次尝试；引擎侧 `reconcile_jobs` 重启后把非终态 Job 判失败/取消（`ENGINE_EXITED`）而非重跑 |
| a dead-letter queue for the jobs that fail every retry | ⚠️ **部分**。Job 有终态（succeeded/failed/cancelled）与 `job_details` 证据，但**无独立 DLQ 视图** ⇒ 该子项**无法确认** |
| structured logs you can search at 3am | ✅ 等价已核（JSONL 行协议严格 raw reader + 帧上限）。**注**：产品为隐私采用零日志策略，可检索性是取舍 |
| an admin panel for your ops team | ✅ 不适用（单用户本地应用，无运维角色） |
| support tooling, so customer success can answer questions without pinging engineering | ✅ 不适用（同上） |
| a plan for the day a third-party API changes its response format without telling you | ✅ 不适用（无第三方 API 调用） |
| protection against prompt injection in every field that reaches the model | ✅ 不适用（S3 前无模型调用路径）。**但见 §8.4 的落地前义务清单** |
| customer and patient data kept out of prompts that leave your network | ✅ 不适用（同上） |
| a model spend cap per customer | ✅ 不适用（无计费、无模型调用）⇒ 属 I06 范围 |
| evals, so you find out when a model update makes your answers worse | ⚠️ **部分**。有契约/夹具/黄金集与冻结校验；**模型质量 evals 不存在**（无模型） |
| a fallback for the afternoon your model provider goes down | ✅ 不适用（无模型依赖） |
| a migration plan for the day your model gets deprecated | ✅ 不适用（无模型依赖） |
| prompt and output logs for debugging, minus whatever you're not allowed to keep | ✅ 不适用（无模型调用） |
| GDPR deletion requests that reach every table, backup and log | ✅ 不适用（不收集个人数据、不联网）。**注**：本地用户数据的"彻底删除"未见产品化入口 ⇒ 语义上部分适用，**无法确认** |
| data residency for the customer whose contract says EU only | ✅ 不适用（数据 100% 本地，无区域存储） |
| HIPAA / a BAA with every vendor / PCI scope | ✅ 不适用（无 PHI、无支付卡、无受监管客户）；**一旦改为服务化即整体适用** |
| quarterly access reviews someone signs off on | ✅ 不适用（无账号/角色体系） |
| a disaster recovery plan, written down and tested once a year | ❌ **未核 / 未建立**（且损坏 SQLite physical HOLD 未关闭） |
| zero-downtime deploys | ✅ 不适用（单机桌面应用） |
| cron jobs that don't run twice the day you add a second server | ✅ 不适用（桌面单机无常驻调度） |
| pages that load on hotel wifi | ✅ 不适用（离线本地应用，**无任何网络请求**；`connect-src 'none'`） |
| emails that render in every mail client your customers use | ✅ 不适用 |
| notifications people can turn off | ✅ 不适用（无推送/邮件） |

### 8.3 适用但**无法确认 / 未满足**（需后续里程碑处理，如实登记，不以静态绿冒充）

1. 静态加密与设备失窃预案（本地 SQLite 明文）。
2. 正式发布流水线 + 分发产物（无签名/公证/安装件）。
3. Windows 与参考老设备（含五龄老设备）实测。
4. D2 规模/负载口径与索引验证（**无显式 CREATE INDEX 已核，但"仅主键隐式索引"的表述过窄**，`format3.py:76,86` 的 UNIQUE 约束自带隐式索引 ⇒ 真实规模下执行计划**无法确认**）。
5. 可访问性（键盘导航、屏幕阅读器、对比度、树形 aria、切换焦点管理）——本轮确认无自定义键盘导航、切换无焦点管理（§5 #17）。
6. "谁查看过"审计（"谁改变了什么"完整，"谁查看过"仅查询侧有元数据）。
7. 全屏空/加载/错误状态覆盖度。
8. 表单校验失败保留已输入内容的逐表单核验。
9. i18n / locale 日期与数字格式化 / RTL（单语 zh 现状；正面：renderer 内 `toLocale|Intl.` 0 处，时间戳从不渲染为日期）。
10. `CHANGELOG.md`、Terms/Privacy。
11. 组织化命名（`appId` 与仓库仍为个人/项目名）。
12. 超大文件拆分（`job_store.py` 2589、`engine.ts` 2623、`semantic.py` 1627）。
13. **备份恢复实测**（有备份机制，未见恢复演练证据）。
14. 可测试的 DLQ 视图。
15. "按合同删除"的保留期规则。
16. **本体/项目级导出与 Turtle 导入导出**（PRD FR-002 / FR-203，P0）。
17. **CSV/XLSX 数据源接入**（PRD FR-300，P0）。
18. 分支保护规则与 PR 模板强制（模板文件存在；**远端设置本轮只读未核**）。
19. 第三方依赖 advisory 状态（无网络未核）。
20. 依赖扫描对 Python 的覆盖。
21. **工程容量闩锁的可恢复性**：`uncertain` 单向闩锁（§4.1）、`#fullIntents` 失败提交占槽（§4.2）、UNKNOWN delivery 不回收（§4.3）、`#mainlineRecords` 不清理（§5 #12）、IPC `deliveries` 不回收（§4.5）——**这五项共同构成"当前内部演示会话内的可用性上限"，清单未直接覆盖，但属"empty/loading/error states on every screen"与"retries with backoff"背后的同一类可靠性缺口**。

### 8.4 模型接入前的落地前义务（S3 之后整类适用）

以下条目当前"不适用"，但**一旦接入模型即整类适用**，属 I06 前必须建层的义务，本轮如实登记而非视作已完成：提示注入防护（每字段）、客户/患者数据不出网、每客户模型花费上限、模型质量 evals、模型商宕回退、模型弃用迁移、提示与输出日志（扣除不可保留部分）、密钥保护（FR-901 要求进 OS 安全存储或等效机制——**当前无密钥故未实现，不得记作已具备**）。

### 8.5 13 条人员角色条目

「reading every line the AI wrote before it ships (a senior engineer)」…「remembering why it's built this way, a year from now (someone who was there)」共 13 条：**⚠️ 无法确认**（人员稳定性与轮值不可从仓库证据判断）。**可核实的对标**：指定双审 + CI + 远端核验门禁在案运行（本报告即其中一环）；**但 bus factor = 1 与个人名下仓库/appId 归属是真实组织风险**（§5 #32）。

---

## 9. 最终判定

### 9.1 当前 748008a6 / package087 —— 内部演示范围（macOS 15 arm64 未签名目录包，"非正式分发，仅限内部演示"）

**判定：PASS。**

**支持"可接受"的正面依据（均为本方直接读证，非沿用旧结论）**：

1. **源码闭集完整一致**：S-source 1270 条逐条重算 bytes+SHA256 **1270/1270 一致**，与 `git ls-tree -r HEAD` 路径集**完全相等**；索引/overlay 哈希全对；cached diff 空，工作区唯一 M 项是受保护的 AGENTS.md overlay。**无未提交产品改动混入。**
2. **核心不变量全部成立**（本方逐段复核）：版本化单一提交路径（`Store.commit`）、不可变历史与不可改写轮次、幂等与不重放、渲染端隔离（`contextIsolation` + `sandbox` + 闭合 preload + 无通用 invoke 通道）、CSP 唯一来源且生产无 `unsafe-inline`/`unsafe-eval`、跨边界只传固定错误码与受限参数、不自动启用模型/遥测/云、引擎无网络出口。
3. **未发现数据损坏、越权写入、凭据泄露、注入或可利用的鉴权缺陷。** 所有本轮定位的缺陷均为**可用性/容量**性质，且**无一构成数据损坏或静默写入失真**。
4. **M4 修复经本方独立复核成立**：紧凑身份与完整载荷两层分离；退休仅在全部 pending 精确 consume 且 `active === 0`、非 unknown、accepted 仍在时发生；紧凑身份继续计入原 128MiB/1048576objects 全局硬预算且**不 FIFO 遗忘**；旧操作严格匹配后**只做 `job.get`**、**绝不重放 `job.create`**；释放失败**保留原 receipt/holding**；未放宽 public 协议、未改 origin、未新增持久 intent 账本。
5. **证据纪律优秀且本方逐项复算吻合**：whole087 单次完整 check 自然 0（`naturalExit: 0`、`sourceUnchanged: true`、`changed: []`）；package087 实物闭包 **910/290/266** 与 `app.asar` 19 014 603 B 与受理票逐数吻合；e2e actual002 **18 collected / 16 PASS + 2 原平台条件 skip**，各层 natural 0；SOURCE005 三例真实故障 `faultApplied: true` 且 PASS；native 原件与时序经本方逐条读出并**确认任务书的更正正确**。
6. **748008a6 的测试改动经本方逐行判定为真实修复 TOCTOU、未放宽任何断言**（单次 `evaluateAll` 同步读双 region，并新增重复 region 拒绝）；与独立 postpatch 复核结论一致。

**为何是 PASS 而不是 BLOCK（与上一轮 MiniMax 的分歧点，理由必须可复核）**：

- 上一轮的**唯一**新增实现级阻断依赖"退役回调抛错"这一触发条件。**本轮独立逐段重建排除链后确认：在当前产品路径下该回调不可能自然抛错**（§3）。因此"16 次正常操作即烧尽主链路"这一后果**不成立**；MM 报告自身也把触发条件标为【推断】。**该阻断的触发前提被证伪，其定级不能维持。**
- 本轮**没有**用"内部演示"这一范围去回避缺陷：我把三个**真实可达**的替代缺陷（§4.1/§4.2/§4.3）排在 Top 10 前三，并给出代码位置、触发条件与修复方向。
- 这些替代缺陷**不构成内部演示范围的阻断**，理由：① 全部为**可用性/容量**性质，**不涉及数据损坏、越权写入、凭据泄露或注入**；② 全部有**明确的恢复手段**（重启应用；`uncertain` 闩锁在引擎会话更换后可逃逸），**不需要数据修复、不需要工程介入、不需要重出包**；③ 触发需要**重复事件**（§4.3 需 8 次切换竞态、§4.2 需 16 次失败提交）或**单次极端慢操作**（§4.1），在"单操作员 + 小规模演示数据 + macOS 15 arm64 本机"的既定交付范围内概率低且可当场重启自愈。
- **明确记录这一判定的不稳定边界**：若交付范围从"内部演示"扩大到**长时值守、无人值守、大数据量或多人/多环境**使用，§4.1/§4.2/§4.3/§4.5/§5#12 应**立即升级为阻断**（无操作员在场时"重启应用"不再是可接受的恢复手段）。**本 PASS 仅在用户明确的"非正式分发，仅限内部演示"范围内成立。**

**仍需如实记明的未闭合项（不因 PASS 而清零）**：§4.1–§4.10 全部 10 项 + §5 的 29 项全部保留在案；历史失败（086 首败、087 guard 首败、C4–C6、D8）全部原样保留。

### 9.2 正式分发 / 其他平台 / 保留 HOLD（与上条**互不抵销**）

**全部保持 HOLD，一项未关闭**：

1. **签名 / 公证 / 可分发安装产物**（`identity: null` + `target: dir`；§4.6）。
2. **完整 legal 与 `_distutils` 归属**（`legalFullClosureAccepted: false`、`mechanicalClosureOnly: true`）。
3. **跨平台（Windows）/ 参考设备 / 无开发环境设备离线启动。**
4. **损坏 SQLite 物理保护 HOLD**（B/C 未授权；§4.7）。
5. **D2 规模 / 负载 / 索引执行计划口径。**
6. **真实 LLM 与 I06 网关正式接入**（S3 前按设计不接入）。
7. **静态加密与设备失窃预案、渗透测试、正式安全问卷证据包、可访问性合规。**
8. **本体/项目级导出与 Turtle 导入导出（FR-002 / FR-203）、CSV/XLSX 接入（FR-300）。**
9. **C4–C6 失败与 D8 人工裁决、CI、develop 合入、完整 release 原门、指定双审积压。**

**机械包身份通过 ≠ 正式签名、法律或全平台发布通过。** 本报告**不以**内部未签名包的绿、也不以 18 条 e2e 的绿，代替上述任何一项。

### 9.3 0/17 口径

**不变。** 仅在实际指定双审通过且 push → PR → CI → merge → 远端复核后方可改变。本审查者**无推送/合并授权，未做任何推送**。

### 9.4 建议的下一轮最小动作（不扩大范围、不新增功能）

1. **先修 §4.2（`#fullIntents` 失败提交占槽）** —— 它是上一轮 M4 修复区域内最容易被真实使用触发的缺口，且修法最小（调整加入时机或在失败路径释放该槽），不必改协议面。
2. **给 §4.1 的 `uncertain` 增加基于原操作证据的复位路径**（不要简单忽略 uncertain），并把主链路的容量封顶/闩锁映射为**可操作的错误文案**而非 `PERMISSION_DENIED` / `invalid()`。
3. **为 §4.3 的 UNKNOWN delivery 建立有界回收**（回收容量，不制造"已投递"证据），并统一 `deliveries` 与 `#mainlineDeliveries` 的回收责任。
4. 补一条**产品路径级**（非仅引擎级）测试：退役失败后投递槽与 IPC 槽均可回收、第 17 次提交仍可用、失败提交不占 `#fullIntents` 槽。
5. 上述任何改码都会产生**新候选** ⇒ whole087 / package087 / e2e actual002 / real-runtime actual001 证据**不可沿用**到新候选，须重跑对应必要验证。

---

## 10. 本次审查的自我限制（如实记录）

- **只读**：未修改任何产品文件、测试、配置、标准或 Git 索引；未运行新的 build / 安装 / GUI / APP / engine / 测试 / 外部请求。**唯一写入为本报告文件**（`…/20261024_t01_748008a6_package087_designated_dual_review_002/minimax/report.md`）。**如平台发生任何自动额外写入，本人未观察到**；收尾复核对 `git status --porcelain` 与索引哈希，确认产品源/索引/overlay 均未变。
- **未运行测试**：本轮**没有**执行任何测试、构建、打包或产品运行；所有"绿"均指对**既有冻结产物的只读复核**，不构成新的运行证据。按仓库规约，静态检查不替代运行证据。
- **未读对方本轮产物**：`…/20261024_t01_748008a6_package087_designated_dual_review_002/zcode/` 全程未打开；仅读取了**上一轮已结束冻结**的 `_001` 双方报告与处置记录，以及更早的 085 两份历史报告与处置记录。
- **子代理**：派出 **1 条只读 `explore` lane**，仅提取 085 历史报告与处置记录的事实条目，**成功完成**；其结论不作为本轮判定依据，仅用于保护本人上下文以完成真实代码核验。本轮无 lane 失败、无并发限制事件。
- **N 临时 checkout 非源码 authority**：本人以 **worktree 实测内容**为准（S1270 逐条重算 1270/1270 一致且路径集与 HEAD 树完全相等），未采信临时 checkout 的 UNBORN Git 状态。
- **对历史证据只读不改写**：未触碰任何历史证据文件；未执行"保存结论到记忆"，未读写任何工具/项目/用户记忆。
- **本报告的推断边界**：§4.1–§4.10 与 §5 中标注【推断】的运行期后果**均未在本轮执行验证**；本轮所有新增缺陷的**代码路径与缺失的回收/删除点为【观察】**，其"第 N 次即封顶"的量化后果为【推断】。
- **与历史报告的分歧不隐藏**：本报告在 §3 明确**不维持**上一轮 MiniMax 的 High/阻断定级，并给出可复核的排除链与理由；在 §4.2/§4.3 明确**指出两份 `_001` 报告均未识别**的两个真实可达缺陷。

---

*报告结束。审查者未修改任何产品文件；本报告为唯一产出。*
