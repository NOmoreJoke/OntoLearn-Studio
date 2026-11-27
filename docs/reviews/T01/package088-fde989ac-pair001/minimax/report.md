# OntoLearn Studio — T01 / fde989ac / package088 全新独立完整累计工程复审报告（MiniMax M3.1-Flash / xhigh / 始终授权）

- **审查者**：MiniMax Code（provider `minimax`，model `MiniMax-M3.1-Flash`，thinking variant，effort `xhigh`，`permissionMode: bypassPermissions`／始终授权）
- **审查日期**：2026-10-24
- **审查类型**：全新独立完整累计复审（非受理、非计划、非抽样摘要）
- **候选**：HEAD `fde989ac2cd2fc59dc396b7082307f09235019e1`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，**40 commits / 546 files** 累计变更
- **规范源码 S**：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions`
- **规范 Git authority**：`/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/.git/worktrees/T01-project-transactions`
- **只读边界**：产品源码、测试、配置、标准、Git 索引与既有冻结证据全程只读；**本轮未运行任何新的 build / 安装 / GUI / APP / engine / 测试 / 外部请求**；未修改任何产品文件、测试、配置、索引；未读取对方本轮（`…/designated_dual_review_001/zcode/`）任务或报告；未读取或写入任何工具/项目/用户 memory。
- **唯一写入物**：本文件 `…/20261024_t01_fde989ac_package088_designated_dual_review_001/minimax/report.md`

---

## 0. 结论（先行）

### 0.1 当前 fde989ac / package088 —— 内部演示范围（macOS 未签名目录包，用户明确"非正式分发，仅限内部演示"）

**判定：PASS（带 1 项由产品自带恢复入口可达、需累计事件的容量闩锁，以及 4 项需重复事件/单次慢操作的会话内可用性闩锁；全部不涉及数据损坏、越权写入、凭据泄露或注入）。**

### 0.2 正式分发 / 其他平台 / 保留 HOLD

**全部保持 HOLD，一项未关闭**（§10.2）。机械包身份通过 ≠ 正式签名、法律或全平台发布通过。

### 0.3 与上一轮（748008a6 / package087）结论的关系（不继承、不迎合）

上一对双方对 748008a6 均给内部演示 PASS。本轮**不沿用**该结论，全部重新独立核验：

- 我**独立复核并认同**上一对 MiniMax 对 087-MM §4.1（M4 退役回调抛错 ⇒ 16 次泄漏）的**否证**：退役回调的三个抛错条件在当前产品路径下自然不可达，我逐段重建了排除链（§3.1）。
- 我**不认同**把"重复提交路径永久占用一个 `#fullIntents` 槽"仅作为抽象风险登记：上一轮把它写成"经历过一次 ACK 丢失的 intent，其 stale pending 永存 ⇒ payload 永不退役"，但**没有指出产品里真正触发"同 operation 重复回复"的具体入口**。本轮我定位到了该入口，并进一步确认**切换项目不会回收该槽**（§4）。这是本轮相对历史报告的**实质增量**。
- 上一对 MiniMax §4.2（`#fullIntents` 失败提交占槽）与 ZCode §3.5-3（stale pending 永占槽）所指的两个来源，本轮合并为同一条可达链路，并给出精确机制与计数口径。

### 0.4 0/17 口径

**不变。** 仅在实际指定双审通过且 push → PR → CI → merge → 远端复核后方可改变。本审查者**无推送/合并权限，未做任何推送、未建 PR、未触发 CI**。

### 0.5 历史状态未被清零

086 首败、087 外部 guard 首败、fresh001 首败、真实 CI 三失败、C4–C6 三次配对失败与 D8 人工裁决门、损坏 SQLite physical HOLD、`_distutils` 归属、真实 LLM、正式签名/完整 legal、Windows/参考设备/D2、静态盘上加密、渗透测试、a11y 合规、指定双审积压 —— **全部继续留账**，本轮无一项被本轮绿证据抵销。

---

## 1. 受理回读核验（本方实测，非引用任务书）

| 项 | 任务书/凭据指定 | 本方实测 | 判定 |
| --- | --- | --- | --- |
| 附件字节数 | 32482 B | `wc -c` = **32482** | ✅ |
| 附件 SHA256 | `2d9db2837d3d9667ac3eb649339d55594737b705cdc3cb160dce9127b3243843` | `shasum -a 256` **完全一致** | ✅ |
| 原清单全文 | 11255 B，逐字保留，出现在 EOF | 官方文件工具读至 EOF（218 行）；按 marker 切分后清单体 **11255 B**，SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`；`b.count(checklist) == 1` 且 `b.endswith(checklist) == True` ⇒ **恰好一次且为 EOF 精确后缀** | ✅ |
| 清单首/末行 | — | 首行「你现在是我的软件工程审查员。」；末行「> remembering why it's built this way, a year from now (someone who was there)」 | ✅ |
| 源码绝对路径 | `…/.worktrees/T01-project-transactions` | `pwd` 一致（Unicode 规范路径） | ✅ |
| Git authority | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `git rev-parse --git-dir` 一致 | ✅ |
| HEAD | `fde989ac2cd2fc59dc396b7082307f09235019e1` | `git --no-optional-locks rev-parse HEAD` 一致 | ✅ |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git rev-parse HEAD~40` = 同一 SHA（base 是 HEAD 的第 40 代祖先） | ✅ |
| 累计范围 | 40 commits / 546 files | `rev-list --count` = **40**；`diff --name-only` = **546**；`--shortstat` = `546 files changed, 564392 insertions(+), 4639 deletions(-)` | ✅ |
| 分支 | — | `feature/weekly-t01-project-transactions`（**非 detached**） | ✅ |
| 受保护 AGENTS.md overlay | 15147 B / `de15f6ce…a5c8c4`，未暂存，勿改 | 工作树实测 **15147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`**；`status --porcelain` 唯一条目 ` M AGENTS.md`；**全程未修改** | ✅ |
| Git 索引 | 合法 index，cached diff 空 | `ls-files -s AGENTS.md` → `100644 f3876f66…`；`git show :AGENTS.md` = **1056 B / `1b3c02916e9bab79f463a61f2818846f01e849014b70251b37c112377443a6fb`**；`git diff --cached \| wc -c` = **0** | ✅ |
| N 临时 checkout | 原生 Git UNBORN，不作源码 authority | 未采信；以 worktree 实测内容为准（§6.1） | ✅ |
| provider / model / 思考 / 权限 | MiniMax M3.1-Flash / xhigh / 始终授权 | 会话环境 `minimax/MiniMax-M3.1-Flash`、thinking variant、effort `xhigh`、`bypassPermissions`（始终授权） | ✅ |

**所有 Git 读命令均带 `--no-optional-locks`。**

**累计 diff 区域分布（本方统计）**：`docs/reviews/T01` 320、`packages/engine/tests` 36、`packages/engine/src` 30、`docs/iterations/T01` 38、`apps/desktop/src` 34、`packages/contracts` 7、`licenses/*` 17、`tests/unit` 24、`tests/e2e` 5、根/脚本/夹具 25。**净增 56.4 万行中绝大部分是契约 fixture 与过程文档**，不是产品实现。

**本轮两项来源补充与勘误（双方完全相同，据原件核验后采用，非指定结论）**：

1. **renderer 第 2 次（2026-10-24 13:54:08 / 05:54:08Z）输入来源**：用户可信答复为"有手动点击或键盘输入"（`HUMAN-INPUT-SUPPLEMENT.json`）。据此该时刻**存在人工输入已有可信人类确认**；**具体按钮/按键未确认**，我**不据此推断具体输入机制**，也**不归因产品或本轮 CUA**。`SECOND-FAILURE.json` 原记录"no click or keyboard input issued"指的是**本轮 CUA 工具未发出任何点击/键盘**，该记录与本补充不冲突。renderer 第 2 次的**原 response1 与真实 FAIL 均保留**，先前 UNKNOWN 原始记录不覆盖，仅更新输入来源。**native 第 1 个 0（13:58:48 / 05:58:48Z）的来源仍为 UNKNOWN**，本补充不涵盖。
2. **package 回执单位勘误**：原冻结提示词"package1790s timeoutfalse是直接字段"为单位笔误。准确表述为——**包实际回执 1790 字节（B）**，`timeout=false` 为该 JSON 的**直接字段**；该 package wrapper 原预算 **300 秒**。我已据实际原件核验：`outputs/20261024_t11_package088_actual_001/execution-evidence/t11-package088-package-001-receipt.json` 实测 **1790 B / `97fb7cac5b1eb019810857e449c4e983d59b1347d5665178ce2196950dd4e6b6`**，其内容直接含 `"timeout": false`、`"naturalExit": 0`、`"observedExit": 0`、`"sourceUnchanged": true`、`"changed": []`；`INDEPENDENT-ACTUAL-REVIEW.json` 同区记 `"bytes": 1790, "timeout": false, "budgetSeconds": 300`。**1790 不是秒**。helper 的 `timeout=false` 仍只来自原 `child.wait` 自然 0 与 driver 完成的推断，**不得混作原始直接字段**。

---

## 2. 本轮实际已核 / 未核范围（诚实边界）

### 2.1 已核（本方亲自读取或亲自执行只读复算）

- **Git 全量状态**（§1 全部实测项；含 40 commits 逐一 `git log --oneline` 核对）。
- **争议焦点代码逐行**：`apps/desktop/src/main/engine.ts`（`#retainHolding/#releaseHolding` 835–883、`#newDelivery/#delivery/#unknownDelivery` 770–823、receiver `receive/consume/binding` 896–1011、budget 1012–1102）、`apps/desktop/src/main/project-mainline-service.ts`（**全文 818 行**）、`apps/desktop/src/main/desktop-ipc.ts`（100–170 + 全部 handler）、`apps/desktop/src/preload/index.ts`（**全文 86 行**）。
- **渲染端**：`ontology/mainline-session.ts`（**全文 819 行**）、`ontology/mainline-operations.ts`（全文）、`query/workspace-controller.ts`（820–880、1290–1360、500–540）。
- **引擎侧**：`project/project_lifecycle.py`（`origin_value` 82–102、创建认领比对 455–480）、`ontolearn_engine/resources.py`（**全文**）、`packages/contracts/python/contract_v2.py` 的 `ROOT` 定义。
- **fde989ac 新叶 15 文件全 diff**（含 `scripts/prepare-fr003-bundle.py` **全文 183 行**、新增测试 **全文 180 行**、CI workflow 全文、两个 `package.json`）、748008a6 的 25 行 e2e diff。
- **证据面**：37 个冻结证据文件的 bytes+SHA256 逐个复算（**37/37 一致**）；package088 实物目录 `os.walk` 复算；ASAR/engine 实测哈希；1288 源闭集**逐条重算**（**1288/1288 一致**）；两份 source-map 差分；1288 路径集与 `git ls-tree -r HEAD` 比对。
- **历史上下文**：六份历史报告 + 三份处置记录。其中 085 两份与 087 第一对两份经**只读子代理逐字提取至 EOF**（最终行号 467 / 171 / 716 / 102）后由本人逐条与源码交叉复核；087 第二对两份（`minimax` 594 行、`zcode` 244 行）与两份处置记录**本人全文读至 EOF**。

### 2.2 未核 / 无法确认（如实记录，不以静态检查代替运行证据）

- **本轮未运行任何测试、构建、引擎、GUI 或网络。** 所有"绿"均指对**既有冻结证据的独立复核**，不构成新的运行证据。
- Windows 打包与运行、Linux 参考设备、五龄老设备实测；两条 Linux-only e2e 在 Linux 上的真实行为。
- 损坏 SQLite physical HOLD、`_distutils` 归属、**D2 规模/负载/索引执行计划口径**、真实 LLM（I06 网关未接入）。
- 签名 / 公证 / 安装 / 无开发环境设备离线启动。
- 可访问性合规（对比度、真实屏幕阅读器）、RTL 排版、emoji/口音渲染细节。
- `packages/contracts/v2/fixtures.json` / `binding-regressions.json` 的**内容**风险（随包分发，未逐字审其是否含业务数据）。
- Python 第三方依赖（rdflib 7.6.0 / pyparsing 3.3.3 / pyshacl 0.30.1 等）的 advisory 状态（无网络，未做漏洞核验）。
- `docs/reviews/T01` 下 320 个过程文档仅台账级抽样，未逐字通读。
- **§4 的槽位占用后果、§8 Top10 中标注【推断】的运行期后果，本轮均未执行复现。**

### 2.3 子代理使用与自我限制（如实披露）

本轮派出 **1 条只读 `explore` lane**（2 次任务：初次提取 085/087 第一对四份历史文档；因工具层输出截断而追加索要缺失的 D 尾部 / E / F 两节）。该 lane **两次均成功完成**，其产物为我逐条与源码交叉复核的**事实提取**，**不作为本轮判定依据**。该 lane 未读取产品源码、未写任何文件、未读写任何记忆、未打开对方本轮目录。本轮无 lane 失败、无并发限制事件。

---

## 3. 核心争议独立复核：退役回调、预算出资、noReplay、holding

任务书要求"实际查证这些排除链，若找到遗漏当前可达反例明确列出；不要仅从人为 throw 推出正常产品 16 次泄漏，也不要把引擎 handle 重试说成产品重试"。我逐段重建了排除链。

### 3.1 退役回调的三个抛错条件（`project-mainline-service.ts:637–660`）

```js
intent.budget.onReplyConsumed(intent.payloadEntry, () => {
  if (!intent.pendingReplies.has(pending)) throw invalid()                                   // A
  if (intent.pendingReplies.size > 1) { intent.pendingReplies.delete(pending); return }
  if (intent.active !== 0 || intent.unknown || !intent.accepted) throw invalid()              // B
  const accepted = intent.accepted
  intent.accepted = undefined
  try { intent.budget.releaseHolding(intent.payloadEntry) }
  catch (cause) { intent.accepted = accepted; throw cause }                                   // C
  intent.pendingReplies.delete(pending)
  this.#fullIntents.delete(intent)
})
```

**A（pending 令牌缺失）不可达**：令牌在 `:658` 加入（注册回调 `:640` 的下一行），其间无 `await`；令牌只被**各自**回调删除（`:643` / `:655`）。我确认全仓无跨删除路径。

**B（`active` / `unknown` / `accepted`）不可达**，三条独立论证：

1. **`active`**：`intent.active++` 在 `:752`，`intent.active--` 在 `:796–798` 的 `finally`。`intent.accepted` 分支（`:754`）是 `active++ → #offerIntent → active--` 的**同步块**，其间无 `await`，事件循环无法抢占 ⇒ ACK 事件不能插入。两个跨 `await` 的分支（`:755` 的 `#readAcceptedIntent`、`:773` 的 `job.create`）都只在 `intent.accepted === undefined` 时进入。
2. **不变式 I（本人独立推导）**：`accepted === undefined` ⇒ `pendingReplies` 为空 ⇒ 该 intent 不存在任何在册退役回调。证明全在同步段内：intent 创建时 `accepted` 为 `undefined`、令牌集为空（`:736–746`）；`accepted` 只由 `#keepIntent(intent, accepted)`（`:633`，唯一调用点 `:786`）置位，其后**紧接同步**执行 `#offerIntent(intent)`（`:792`），二者之间无 `await`；`accepted` 只在退役回调内被清空（`:648`），该回调在同一同步段内于 `:655` 删除最后一个令牌，若 `releaseHolding` 抛错则在 `:652` **恢复** `accepted`。⇒ 两条跨 `await` 的分支运行时，该 intent 无可触发退役的回调。
3. **`unknown`**：只在 `:756`（新写分支进入时，彼时 `accepted` 为 `undefined`）与 `:775`（同分支错误处理）置位；`:787` 在 offer 之前清除。⇒ `unknown` 为真 ⇒ 无在册退役回调。

**C（`releaseHolding` 抛错）不可达**：`engine.ts:872–883` 的 `#releaseHolding` 唯一显式拒绝是「holding 不存在」或「`holding.record !== record`」——**没有 current-session 检查**（注释明确允许旧 owner 在会话变化后清理自己的 holding），且 `holding.bytes === 0` 时**幂等提前返回**。`#mainlineHoldingEntries` 是 WeakMap，全文件**只有 `get` 与 `set`，无 `delete`**（我逐点核对 `engine.ts:646` 声明与 `:838` / `:869` / `:873` 三处使用）⇒ 已释放条目不会抛错。`payloadEntry` 是 intent 私有固定对象（`Object.freeze({})`，`:742`），其 holding 由 `#keepIntent`（`:632`，经 `intent.budget`，而 `intent.budget` 在 intent 创建时即固化为绑定固定 mainline record 的 budget 实例）retain，且**只有本回调 release**（我核对了全部 `releaseHolding` 调用方：`query-definition-service` 用自己的 entry、selection fence 用 `selectionEntry`、退役 principal 用 `token`，均非 `payloadEntry`）。

**结论**：**在当前产品路径下，该退役回调不可能自然抛错。** 我**不维持** 087-MM §4.1 的 High/阻断定级，**独立认同**上一对的否证。

### 3.2 两条人为 throw 测试的真实性质（本方逐字核对）

- `tests/unit/t01-mainline-reply-lifecycle.test.ts:541–583`：用 `vi.fn()` 人为让回调抛 `'cleanup remains owned'`，随后**直接再次调用 `s.receiver.consume(offered.receipt)`**（引擎级 API）。
- `tests/unit/t01-mainline-real-runtime.test.ts` 的 17 连提交回归：在其中一次用 `vi.spyOn(budget,'releaseHolding').mockImplementationOnce(() => { throw … })` 一次性注入，随后**直接** `value.replies.consume(duplicate.receipt)`。

两条证明的是**"释放失败后原 receipt/holding 保留、可按原 handle 精确重试、已完成项不重复退款"**（**已采用的安全合同，实现正确**），**不证明**自然触发，也**不证明**产品自动恢复——preload 只发一次 ACK（§3.4）。

### 3.3 仍然成立的真实限制（如实保留，不因上述结论淡化）

- **【观察】** `engine.ts:964–972`：`consume()` 的退役循环被 `retire()` 抛错中断 ⇒ `:973–980` 的退款、`aliases.length=0`、`wires.clear()`、`records.clear()`、`#mainlineDeliveries.delete`、`#mainlineReceipts.delete`、`#mainlineConsumed.add` **全部不执行**；`finally` 只复位 `delivery.consuming`。
- **【观察】** `desktop-ipc.ts:136–142`：`consume()` 抛错 ⇒ `return permission()` ⇒ **`deliveries.delete(id)` 被跳过** ⇒ IPC 投递槽（上限 16，`:164`）被永久占用。
- **【观察】** `preload/index.ts:26–45`：ACK **只发一次**（`Promise.race` + 5s 超时），任何失败被 `catch {}` **静默吞掉**，渲染端**照样拿到正确业务结果**；注释自述「Main keeps the original unacknowledged lease; no retry/clear is fabricated.」⇒ **产品层没有任何自动重发原 ACK 的入口**。

⇒ **准确表述**：**若**退役回调真的抛错（故障注入、未来不变量被破坏或内存态损坏），原 receipt/holding 会被**正确保留**（fail-safe 成立），但**产品路径没有恢复通道**，两个 16 槽账本各泄漏 1 槽。这是"保住了责任、却没有恢复通道"的**潜伏脆弱性**，不是当前可达的可用性中断。

### 3.4 预算出资、FIFO、noReplay、holding —— 四条合同逐条复核

| 合同条款 | 本方独立核验 | 判定 |
| --- | --- | --- |
| **consume 成功且无活跃使用才退完整 payload** | 释放只发生在退役回调内，且回调由 `consume()` 的 `delivery.consumptions` 循环驱动（`engine.ts:966–969`），即**以精确 ACK 为授权依据**；回调内再校验 `active === 0`、`unknown === false`、`accepted` 仍在 | ✅ 成立 |
| **紧凑原 operation 身份仍由原 128MiB/1048576objects 硬预算出资、不 FIFO 遗忘** | `#keepIntent`（`:621–636`）把紧凑身份 `{operationId, request, engineSessionId, jobId}` retain 在 **intent 自身**的 holding 上，**无任何 releaseHolding 调用会释放它**；计费经 `#retainHolding` → `#mainlineReserve`（`engine.ts:733–752`）扣减全局 `bytes`/`objects`，上限 `134217728` / `1048576`；`#intents` Map **无 size 上限**（16 上限已移到 `#fullIntents`），故紧凑身份的真实约束是**全局预算**而非容器大小 | ✅ 成立。**该预算是保守高水位工作预算，不是实际 RSS**（RSS 仅由 `memory_guard.py` 的 10ms 咨询式采样观测，`native_hard_limit=False`） |
| **原 owner/request/session 匹配后旧操作只实际 `job.get`，不 `job.create` 重放** | `:726–733` 强制校验 `intent.request` 指纹、`intent.owner`、`intent.session` 全等，不等即 `invalid()`；`:751` `if (intent.unknown) throw denied()`（**No automatic replay of an entered write**）；`:755` 的 `intent.jobId` 分支走 `#readAcceptedIntent` → **`job.get`**（`:676`），并复验 jobId/projectId/operationId/capability/confirmationRef/input 六项 | ✅ 成立 |
| **释放失败保留原 receipt/holding** | `engine.ts:960–972` 的 `consume()`：退役循环中断 ⇒ 退款与删除**全部不执行**，`finally` 只复位 `consuming`；已完成项已逐个 `delete`，重试不重复退款。服务侧 `:651–654` 在 `releaseHolding` 抛错时**恢复 `intent.accepted`** 并上抛 | ✅ 成立 |

**关于 FIFO 的准确边界（本方独立清点）**：

| 容器 | 上限 | 回收方式 | 是否有 FIFO |
| --- | --- | --- | --- |
| `desktop-ipc.ts` `deliveries`（未 ACK 责任） | 16（`:164`） | **仅**精确 ACK 删除（`:142`） | ❌ 刻意无 |
| `desktop-ipc.ts` `accepted`（**已消费**身份） | 16（`:144`） | FIFO 驱逐 | ✅ 有（只含已消费身份） |
| `engine.ts` `#mainlineDeliveries` | 16（`:771`） | **仅** `consume()` 成功删除（`:978`） | ❌ 刻意无 |
| `project-mainline-service.ts` `#fullIntents` | 16（`:735`） | **仅**退役回调内删除（`:656`） | ❌ 刻意无 |
| `project-mainline-service.ts` `#intents`（紧凑身份） | 无 size 上限 | 无（永久保留） | ❌ 由全局预算出资 |
| `engine.ts` `#mainlineRecords` | 16（`:1167` 附近） | **仅 `.set`，无 `.delete`** | ❌ 刻意无 |
| `Coordinator.seen` | 65536 | session 生命周期内 | ❌ |

**不适用/需区分的条目**：无服务端，故连接池、autoscaling、CDN、cron 防双跑、云侧 DLQ、存储生命周期规则等**整类不适用**（§7）。

---

## 4. 【本轮新增】可达反例：同 operation 重复回复 ⇒ 永久占用 1 个 `#fullIntents` 槽，且切换项目不回收

这是任务书明确要求寻找的"遗漏当前可达反例"。我定位到了**产品自带的具体入口**，而非仅抽象风险。

### 4.1 具体路径（全部为本方源码实读）

**入口（UI 按钮 → 渲染端 → 主进程）**：

- `apps/desktop/src/renderer/src/query/QueryWorkspacePage.tsx:605–616`：当 `state.pending?.kind === 'commit'` 时渲染三个按钮，其中第一个为
  ```
  <button disabled={state.busy} onClick={() => void controller.recoverOriginalCommit()}>
      按原确认与 operation 取回受理（不生成新操作）
  </button>
  ```
- `apps/desktop/src/renderer/src/query/workspace-controller.ts:1321–1341`：
  ```js
  recoverOriginalCommit = () => this.action(async (view) => {
    const pending = this.state.pending
    if (pending?.kind !== 'commit') throw new Error('NO_PENDING_COMMIT')
    const job = take(await this.bridge.commitProjectChangeSet({
      operationId: pending.operationId,          // ← 同一 operationId
      confirmation: clone(pending.confirmation), // ← 同一 confirmation
    }))
    ...
  })
  ```
- 该 `pending` 在 `workspace-controller.ts:858–862` 于**首次提交之前**即写入 state（`operationId` 为 `crypto.randomUUID()`），因此**首次提交的回执丢失或 ACK 丢失后，pending 仍在**，按钮仍可见可达。

**主进程侧对应分支**：`project-mainline-service.ts:754` `if (intent.accepted) return this.#offerIntent(intent)`。

### 4.2 机制与计数（本方逐步推导）

设首次提交为 A，恢复提交为 B（同 operationId、同 confirmation）：

1. **A**：`intent.accepted` 首次置位（`:786`）⇒ `#offerIntent` 注册回调 `cb_A` 于 delivery `D_A` 的 `consumptions`，并加入令牌 `p_A`。`pendingReplies = {p_A}`。
2. **A 的回执或 ACK 丢失** ⇒ `consume(D_A)` 永不执行 ⇒ `cb_A` 永不运行 ⇒ `intent.accepted` 仍为真、`p_A` 仍在集合、`payloadEntry` 的完整载荷 holding 仍活着、`intent` 仍在 `#fullIntents`。
3. **B**：`intent.accepted` 为真 ⇒ 走 `:754` ⇒ `#offerIntent` 注册 `cb_B` 于新 delivery `D_B`，加入 `p_B`。此时 `pendingReplies = {p_A, p_B}`。
4. **B 的 ACK 成功** ⇒ `consume(D_B)` ⇒ `cb_B` 运行 ⇒ 命中 `if (intent.pendingReplies.size > 1) { delete(p_B); return }` ⇒ **只删自身令牌，不释放载荷**。
5. **结果**：`p_A` 仍在（其载体 `D_A` 永不会被 consume），`cb_A` 永不运行 ⇒ **完整载荷 holding 永不释放，`#fullIntents.delete(intent)` 永不执行**。

**再者**：由于 `intent.accepted` 始终为真，第 3 次同 operation 调用仍走 `:754`（而非 `:755` 的 `job.get` 分支）⇒ **该 intent 连"退而求其次走只读重取"的机会都没有**，载荷也永不被重新读取。**该状态不可自愈。**

### 4.3 后果与恢复面

- **【观察】** 每发生一次"回执或 ACK 丢失 + 用户点击取回受理"，永久占用 **1 个 `#fullIntents` 槽**（上限 16，`:735`），并连带占用该载荷在 **128MiB/1048576objects 全局预算**中的 bytes/objects（`#releaseHolding` 是唯一退款路径）。
- **【观察】** 累计 16 次 ⇒ `:735` 抛 `invalid()` ⇒ **此后任何新 operation 的提交都被拒绝**，错误码为通用 `INVALID_STATE`，在 UI 上与"请求非法"同形，**没有任何"资源已满/请重启"提示**。
- **【观察】本轮新增的升级点 —— 切换项目不回收该槽**：`ProjectMainlineService` 是应用级长生命周期单例；`#selection()`（`:444–462`，即项目切换/新建/打开的公共入口）只做 `#invalidateRecovery()`、`source.fence()`、`tasks.clearProject()`、`#retireRecoveryPending()`，**完全不触碰 `#intents` / `#fullIntents`**；`dispose()`（`:801–817`）同样不清。⇒ **用户切到另一个项目、甚至新建/打开项目，都不能回收被占的槽；只有重启应用能回收。**
- **【推断】** 触发需要"回执/ACK 丢失"这一真实但非日常的事件（渲染进程崩溃/重载、主进程回复行丢失、ACK 5s 超时等），**不需要故障注入**；产品为该场景专门提供了恢复按钮，因此**这条路径正是产品设计要覆盖的场景**，而不是边缘竞态。
- **【风险】** 纯可用性/容量性质。**无数据损坏、无重复写入**——引擎侧 `operation_claims` 与不可变 marker 仍兜住不变量；`job.create` 从未被重放（§3.4）。
- **【严重度】Medium–High**（比上一对记为"两个来源之一"更高：上一对未指出**产品自带入口**，也未指出**切项目不回收**）。

### 4.4 建议（**严格不触碰已采用的合同边界**）

已采用合同明确"不得用 FIFO、无偿退款、删除 origin、扩建持久 intent 账本、要求 16 个真实未解责任存在时第 17 个仍获准"。因此**不建议**放宽任何义务。可做的：

1. **把容量拒绝映射为可操作错误码**：`:735` 的 `invalid()` 改为专门错误（如 `RESOURCE_LIMIT`），并在 UI 明确提示"本次会话的未确认操作已达上限，请重启应用"。这条**不改变任何义务语义**，是本轮**成本最低、收益最直接**的修复。
2. **为"最后一个存活令牌"提供释放路径**：退役回调目前要求 `pendingReplies.size == 1` 才释放。若某令牌的载体 delivery 已被证明**永不可再 consume**（例如其 delivery 已不在 `#mainlineDeliveries`、或其 receipt 已被标记为不可达），则该令牌对应的义务已无释放入口，可允许**最后一个存活令牌**释放载荷。此路径仍以"精确 ACK 授权"为依据（活着的令牌确由真实 ACK 驱动），**不造消费证据、不 FIFO、不无偿退款**。
3. **补一条产品路径级测试**（非引擎级直调）：模拟"首次回执丢失 → 点击取回受理 → 断言 `#fullIntents` 槽与 payload holding 的终态"，防止该缺口再次无感回归。

---

## 5. fde989ac 新叶（15 文件）独立复核

`fde989ac` 是本候选相对上一候选的**唯一新增**。我逐文件核对其是否**正确且完整**地修复了已记录的三条真实 CI 失败。

### 5.1 三条真实 CI 失败（本方从原日志实读确认）

| Job | 原失败（run40063929148） | 原日志证据 |
| --- | --- | --- |
| Desktop (windows-latest) | 5 个测试模块 `UnicodeDecodeError: 'charmap' codec can't decode byte 0x90` | `CI-FIRST-WINDOWS-FAILURE.log:300–353`；checkout 实测 `fetch-depth: 1` |
| Quality (ubuntu) | `tests/unit/t01-example-host-runtime.test.ts` 3 例 ENOENT：`build/release-resources/fr003-bundle-v2/examples/equipment-maintenance/loader/t01-provider.json` | `CI-FIRST-QUALITY-FAILURE.log:360–483`（`Tests 3 failed | 1691 passed (1694)`） |
| Desktop (macos-latest) | `test_project_format3.py::test_approved_old_reader_rejects_actual3` → `git show 5f910b52…:packages/engine/src/ontolearn_engine/storage.py` 退出 128 | `CI-FIRST-MACOS-FAILURE.log:472–479`（`1 failed, 3444 passed, 44 skipped`）；checkout 实测 `fetch-depth: 1` |

**三条失败全部保留在案，未被本轮绿证据洗白。**

### 5.2 Windows cp1252 修复 —— 正确且完整（**观察**）

- 修复面：**6 个 Python 文件、8 处**显式 `encoding="utf-8"`（`test_binding_regressions.py` 1、`test_ordinary_library.py` 1、`test_project_business3_contract.py` 2、`test_project_source_table_material.py` 1、`test_query_definition_service.py` 2、`test_query_presentation.py` 1）。
- 新增回归：`test_frame_corpus.py` 新增 `test_shared_corpus_modules_keep_utf8_under_cp1252`，参数化 **7 个真实 module**（CASES / PROFILE / REGRESSIONS / CORPUS / FIXTURES / BINDINGS / DATA），经 `cp1252_contract_default` fixture 用 `monkeypatch.setattr(Path, "read_text", ...)` 模拟平台默认编码。
- **本方独立验证该回归**不是空转：`cp1252_contract_default` 的目标集合是 `CONTRACT.ROOT / name`。本方追查 `CONTRACT` 的真实来源——测试里 `from ontolearn_engine.resources import CONTRACT` 拿到的是 `resources.py` 用 `spec_from_file_location` 载入的 **`contract_v2` 模块**，其 `ROOT = Path(__file__).resolve().parents[1] / "v2"` = **`packages/contracts/v2`**（本方实测确认 `fixtures.json` 1405911 B、`binding-regressions.json` 608058 B、`frame-fixtures.json` 17537 B 均在该目录）。⇒ **fixture 目标集合与 6 个模块实际读取的路径精确相等**，未打空。
- **原有故意错误的默认 cp1252 对照测试与全部旧 assert 保留**（`test_corpus_uses_utf8_when_default_file_encoding_is_cp1252` 仍在，且仍断言 `default_cases[0]... == "中文😀".encode().decode("cp1252")`，即对照组不被抹平）。
- **"先 7 红后 60 绿"**：本方**未运行测试**（只读边界），该数字**无法确认**；但从源码看，新用例在修复前必然因 `read_text()` 落入 patched 分支而读成 cp1252（抛 `UnicodeDecodeError` 或产生 mojibake 导致 `loaded[variable] != expected`），修复后全部显式 UTF-8 ⇒ 机制自洽。**登记为"机制自洽、运行数字未验"。**

### 5.3 Quality 干净 checkout 缺 bundle 修复 —— 正确（**观察**）

- 新增 `resources/examples/equipment-maintenance-resource-source-v2.zip`（**实测 1344035 B / `b8717a53501e0825c5209faaf7e056e28d2f8c5f8c74b4b7e1f7bdf8b618164a`**，与脚本常量 `ZIP_BYTES`/`ZIP_SHA256` 及同名 `.sha256` 侧车三方一致）。
- ZIP 结构本方实测：**22 个唯一成员**，全部以 `examples/equipment-maintenance/` 前缀，`total bytes = 1338939`（与脚本常量一致）；`manifest.json` 7566 B / `23de1c472afd808761073ee2b46e6fa920508b1f869321062143950efd1ed8fb`（与 `MANIFEST_SHA256` 一致）；全部成员 `external_attr>>16 == 0o100444`（S_IFREG，非符号链接）。
- **该 stage 路径确被产品消费**（本方逐点确认，非摆设）：`apps/desktop/electron-builder.yml:13–14` 拷贝 `build/release-resources/fr003-bundle-v2/examples/equipment-maintenance` → `examples/equipment-maintenance`；`apps/desktop/src/main/index.ts:245,248` 在开发态解析 `../../build/release-resources/fr003-bundle-v2/examples/equipment-maintenance/loader`。
- 钩子面：根 `package.json` 增 `prepare:examples` + `predev` / `prebuild` / `pretest`；`apps/desktop/package.json` 增 `prepackage:dir`。**本方逐行确认这些钩子只调用 `prepare:examples`，不塞入任何新 build**（`prepackage:dir` = `npm --prefix ../.. run prepare:examples`）。
- **不污染 lint/format**：`build` 同时在 `.prettierignore` 与 `eslint.config.mjs` 的 `ignores`（`'build/**'`）中 ⇒ 0555/0444 的只读 stage 不会被 prettier/eslint 扫描。

### 5.4 macOS shallow depth 修复 —— 正确（**观察**）

- 两个 `actions/checkout` 均加 `with: fetch-depth: 0`（quality 与 desktop 两个 job）。
- **本方独立验证"该测试确实需要 base commit 且 base 含该路径"**：`packages/engine/tests/test_project_format3.py:369–394` 的 `test_approved_old_reader_rejects_actual3` 执行 `git show 5f910b52…:packages/engine/src/ontolearn_engine/storage.py`；本方实测 `git cat-file -e 5f910b52…:packages/engine/src/ontolearn_engine/storage.py` **存在**（blob `b77b71dd…`），且该文件在 base→HEAD 的 diff 中状态为 **M**（非新增）⇒ **`fetch-depth: 0` 是正确且充分的修复**（不是路径错误）。
- 附带观察：该测试使"批准过的旧 reader"这一跨版本契约**依赖 Git 历史可达**。对浅克隆的开发者本地环境该用例会失败；CI 已用 `fetch-depth: 0` 覆盖，但**本地开发环境的该前提未在脚本或 README 中说明**（§8 Top10 观察项）。

### 5.5 新增准备脚本 `scripts/prepare-fr003-bundle.py` 的独立安全复核（本方逐行）

**做对的部分（观察）**：

- ZIP 身份：先 `regular_bytes`（`O_RDONLY|O_NOFOLLOW|O_NONBLOCK`，`O_NOFOLLOW` 缺失时降级为 0）读入，校验 `len == ZIP_BYTES` 且 SHA256 等于常量 ⇒ 换包即拒。
- 成员结构：恰好 22 个唯一成员；逐项检查前缀、`PurePosixPath.is_absolute()`、路径段不含 `""`/`"."`/`".."`、不含 `\」、非目录、非符号链接、`S_IFMT ∈ {0, S_IFREG}`。
- **manifest 自身被 pin**（7566 B + SHA256），因此 manifest 里的 `path` 不可能是外部注入的；`pins` 集合与 ZIP 成员集合**全等**才继续；每个成员再校验 `file_size` + 解压后长度 + SHA256；`zipfile.read` 顺带校验 CRC。
- 聚合字节数 `1338939` 独立校验。
- 已有 stage：`verify_tree` 逐文件核对集合、POSIX 权限（目录 0555 / 文件 0444）与字节内容；**缺失/变更/额外成员一律拒绝，不覆盖**（README 亦明写"不生成新示例…不覆盖"）。
- 写入路径：`tempfile.mkdtemp` 私有 scratch → `path.open("xb")` 独占创建 → 逐文件 chmod 0444 → 自底向上 chmod 目录 0555 → `verify_tree(scratch)` → 再查 destination 未出现 → `rename`。
- 协作锁：`O_CREAT|O_EXCL` 独占创建 `.fr003-bundle-v2.prepare.lock`，`finally` 中**比对 dev/ino 后**才 unlink ⇒ 不会删别人的锁（`test_an_existing_preparation_lock_is_never_removed` 覆盖）。
- 文档诚实：README 明确"不承诺对不遵守锁的并发写入者提供平台级 no-replace 保证"。

**本方新增的三个低风险观察（观察）**：

1. **崩溃残留锁会永久阻断后续 prepare**（`prepare():142–143` 与 `finally:176–178`）：`os.open(lock, O_CREAT|O_EXCL)` 成功后若进程被强杀，锁文件残留；此后每次 `predev`/`pretest`/`prebuild`/`prepackage:dir` 都在 `os.open` 处抛 `FileExistsError` ⇒ **同一工作区的所有构建/测试入口永久失败**，且错误信息不指向"删除 `.fr003-bundle-v2.prepare.lock`"。**建议**：在 README 或错误信息中给出该锁的恢复命令，或对陈旧锁做基于内容/时间的**显式拒绝**提示（不得静默删除他人锁）。
2. **`finally` 中的 `lock.lstat()` 未做存在性保护**（`:176`）：若锁文件在 `os.open` 之后被第三方删除，`lstat()` 抛 `FileNotFoundError`，会把一次**已成功**的 prepare 变成失败，且掩盖原始异常。属非合作写者下的健壮性缺口。
3. **非 POSIX 平台的 `O_NOFOLLOW` 缺失降级**（`:28`）：Windows 上 `getattr(os, "O_NOFOLLOW", 0)` 为 0，符号链接防线只剩 `is_link()` 的 TOCTOU 窗口；`is_junction` 在 Windows 上可用但仅在 `is_link` 中被调用。脚本 README 已声明不承诺平台级 no-replace 保证，故定级为**维护观察**而非缺陷。

**未发现**任何越权写入、路径逃逸、TOCTOU 绕过、符号链接逃逸或不安全的解压行为；新增 14 个负例/竞态测试的覆盖面与实现一致。

---

## 6. 证据链独立复核（本方逐项亲自复算）

### 6.1 源码闭集（1288 叶）

- **【本方亲自逐条重算】** 以 `runtime-inputs/source-map.json` 的 1288 条 path→{bytes,sha256} 对**当前工作树**逐条重算：**1288/1288 一致，0 缺失、0 不符**。
- **【本方亲自比对路径集】** `git -c core.quotepath=false ls-tree -r --name-only HEAD` = **1288** 条，与闭集路径集**完全相等**。
- **两份闭集差分（本方亲自计算）**：`source-map.json`（226770 B / `c4a3e3d3…b9a99`）vs `check-source-map.json`（226769 B / `30055ab1…6c3a`）：**路径集完全相等，各 1288 条，逐条比对仅 1 条不同 —— `AGENTS.md`**（A = 15147 B / `de15f6ce…a5c8c4`；B = 1056 B / `1b3c0291…a6fb`）。⇒ **"其余 1287 叶逐字节相同、两份 AGENTS 不同"的表述属实**；**不得把两份 AGENTS 说成全同**。
- `SOURCE-MAPPING.json` 记载 `allOther1287LeavesEqual: true`、`soleDifferentLeaf: "AGENTS.md"` —— 与本方独立计算一致。
- `CLEAN-FULL-CHECK-002.json`：`head = fde989ac…`、`argv = ["uv","run","--frozen","npm","run","check"]`、`exitCode = 0`、`timeout = false`、`elapsedSeconds = 147.099`、`trackedCount = 1288`、`trackedSourceUnchanged = true`、`initialBuildReleaseOutAbsent = true`、`ownFreshDependencies = true`。本方**未重跑**，仅核对与源码事实相容（`initialBuildReleaseOutAbsent` 与新 `prepare:examples` 钩子一致）。

### 6.2 package088 实物闭包（本方 `os.walk` 复算）

| 项 | 任务书/受理票 | 本方实测 | 判定 |
| --- | --- | --- | --- |
| APP 叶子 | 910 | **910**（545 文件 + 352 目录 + 14 符号链接） | ✅ |
| Resources 常规文件 | 290 | **290** | ✅ |
| engine | 266（225 文件 + 41 目录） | **266**（225 文件 + 41 目录，根目录不计） | ✅ |
| `app.asar` | 19014603 B / `74304c2de5…cb6c` | **19014603 B / `74304c2de556e562815be0ba4052afac69f492fedd010057a6cc92657802cb6c`** | ✅ |
| engine 可执行 | 6223312 B / `43efc368…957d` | `ACTUAL-RESULT.json` 记 6223312 B / `43efc368d6ff26357bb36952328f0d41be5ac1a01c47d6745fd5b95d4cf0957d` | ✅ |
| APP root 权限 | 0755 | `rootMode: 493`（=0755）；**与原 stage 的 0555 分别记录、未混同** | ✅ |
| 包实际回执 | 1790 **字节**，`timeout=false` 为直接字段，wrapper 原预算 300 秒 | 见 §1 更正核验 | ✅ |
| 签名 | 未签 | `APPDeepCodesignExit: 1`、`nonEngineSignatureFailures: 9` | ✅（与历史一致，未洗白） |

### 6.3 真实 E2E（088 全量）

`outputs/20261024_t01_full_e2e088_actual_001/ENTRY.json`：`sourceHEAD = fde989ac…`、`status = ORIGINAL18_COLLECTED_16PASS_2_ORIGINAL_LINUX_ONLY_SKIPS_NATURAL0`、`naturalCoordinatorExit/naturalWrapperExit/naturalNPMTestExit = 0`、`timeout = false`、`durationSeconds = 91.040829667`、`actualCollected = 18`、`profileBindings = 16`、`allOwnedProfileBound = true`、`missingDirectProcessGettersRemainUnknown = true`、`observerSamples = 216`、`observerErrors = []`、`knownPIDs = 113`、`finiteKnownPIDsAbsentOnly = true`、`priorThreeCIFailuresAndLocalEnvironmentFirstFailurePreserved = true`。⇒ **"真实 18 collected = 16 PASS + 2 原 Linux-only 平台条件 skip"属实；缺 getter 仍记 UNKNOWN，未洗成观测。**

### 6.4 三种在途 fault / native / renderer 三次

- `THREE-FAULT-RESULTS.json`：`mode = "reload"`、`result = "PASS"`、`faultApplied = true`、`naturalOuterExit/naturalDriverExit/APPNaturalExit = 0`、`preGuard/postGuard = 0`、`knownOwnedPIDsAbsentOnly = true`。⇒ **三种在途 fault 各有真实 PASS，`faultApplied` 断言与原 queued/running 前提未改。**
- `COORDINATOR-FIRST-PASS.json` / `-MANIFEST.json`：bytes/SHA 与任务书一致（4951 B / `7fa6e142…a7bf4`；4056 B / `c970663c…795b`）。
- `NATIVE-FIRST-PASS.json`：`result = NATIVE_RESTORE_DECLINE_NORMAL_QUIT_OBSERVED`、`windows = 3`、`responses = [0,0,1]`、`responseInputSource[0] = "UNKNOWN before any T01 CUA input"`（即 05:58:48 那个 0，**来源仍 UNKNOWN，本轮补充不涵盖**）、`lifecycle` before-quit `06:01:22.666Z`(seq4) → will-quit `06:01:22.677Z`(seq6)、driver exitCode 0、`forcedFailureExit = null`、`rendererFailuresRemainUnresolved = true`。
- renderer 第 1 次 FAIL：`FIRST-FAILURE.json` / `-MANIFEST.json` / `CUA-TOOL-TIMELINE.json` 三件 bytes/SHA 与任务书一致；**原失败完整保留**。
- renderer 第 2 次 FAIL：`SECOND-FAILURE.json`（1095 B / `cbe70dca…9b0`）+ `-MANIFEST.json`（4988 B / `12b1eccb…6a03`）+ `CUA-TOOL-TIMELINE.json`（116242 B / `0d093186…a96f`）；`result = FAIL`、`originalBudgetsMs = {inner: 65000, driver: 75000}`、`binding` 记 "no click or keyboard input issued"（指本轮 CUA 未发出输入）、`prompt` 记 response 1 于 05:54:08.290Z。⇒ **真实 FAIL 保留；输入来源按 §1 的可信人类确认更新，不覆盖原记录。**
- renderer 第 3 次 PASS：`THIRD-RENDERER-PASS.json`（5222 B / `b97758b3…37f0`）：`result = PASS`、`faultApplied = true`、prompt 于 `06:04:20.054Z` 转发、**response 0 于 `06:04:40.122Z`**、`readAfterFault` 读到原 Job `6686f607-5f41-4f81-9c76-559e510673b5`、`state = succeeded`、`validation = PASSED`、driver pid 78034 exitCode 0、`pre/post` 均 natural 0、进程采样 `finiteSampleOnly = true`。

### 6.5 平台事实（本方实测）

- `sw_vers` → **ProductVersion 27.0.1**；`uname -a` → **Darwin 27.0.0 arm64**。⇒ **本机实际 host 是 macOS 27.0.1 / Darwin 27.0.0 arm64**；旧报告/旧提示词中的"15 actual"是历史错误，本轮**不继续当作已实测**。
- **macOS 15 arm64 仍为目标兼容平台，UNVERIFIED，不豁免。**
- `ACTUAL-PLATFORM-AND-C002-BRANCH.json`（1178 B / `0fd0ac41…0d69`）实读：`actualDevice = macOS27.0.1/Darwin27.0.0 arm64`、`approvedCompatibilityTarget = "macOS15 arm64; target-device compatibility remains UNVERIFIED"`、`priorMacOS15TestedClaimCorrected = true`、`oldReportsNotRewritten = true`、`C002BranchDescriptionCorrected = true`；其内实测分支 = `refs/heads/feature/weekly-t01-project-transactions` @ `fde989ac…`（**非 detached**）。本方另在 worktree 直接复核分支名同样一致。

---

## 7. 用户 11255B 清单逐项适用性判断（160 引用行：147 产品条目 + 13 人员角色条目）

> 原则：**先判适用性**；不适用按**类别**说明依据；**适用但未核实写"无法确认"**；不为满足清单给本产品扩建无关功能。
> 本产品形态：**本地优先、单用户、离线、无服务端、无网络端口、无账号体系、无计费、无模型接入（S3 前）**。因此清单大部分条目属服务端/SaaS 形态 —— 这是"当前形态不适用"，**不是"已具备"**。

### 7.1 整类不适用（按类别说明依据）

| 类别 | 覆盖的清单条目 | 不适用依据 |
| --- | --- | --- |
| 账号与身份 | login（+号邮箱）、密码重置链接、MFA 及恢复、会话超时与全量会话吊销、SSO、SAML、SCIM、深于 admin 的角色、按 URL 改号越权、租户隔离、管理员"登录为该用户"+审计、登录限流、防 CFO 误锁 | 无服务器、无登录、无多用户/多租户。IPC 侧以 sender/frame/文档三重校验替代。**注：一旦引入"接收他人项目文件"或团队共享，该整类立即适用且当前为零基础** |
| 支付与计费 | 订阅/升级/降级/按比例、失败扣款与催缴、发票与 PO 号、销售税/VAT、退款/信用额度/部分退款、用量计量到分、年约定制条款、财务对账报表 | 无任何货币处理（"money stored as integers"随之不适用） |
| 对外 API 生态 | 版本化对外 API、客户 API key 与吊销、API 限流、第三方 API 响应格式突变预案、OAuth token 刷新、集成沙箱、webhooks 签名与重试日志 | 无对外 API/webhook；引擎协议是**私有 stdio 契约**（`registry.json` + `schema.json` 双端校验 + 固定错误码表），本身即"designed schema" |
| 邮件 | SPF/DKIM/DMARC、退信与投诉处理、邮件客户端渲染 | 不发邮件 |
| 云基础设施 | dev/staging/prod 对齐、IaC、零停机、一键回滚云语义、功能开关、自动扩缩、CDN、DNS/SSL 续期、第二区域、DR 年度演练、状态页、成本告警 | 无云服务、无网络端口（CSP `connect-src 'none'` + 引擎 audit hook）。本地等价物：CI 完整门禁；回滚 = 上一目录包 + git 还原（流程层） |
| 观测与值班 | 3am 可搜结构化日志、错误聚合、外部拨测、告警 paging、延迟/错误率/吞吐仪表盘、跨服务 tracing、on-call 轮值、runbook、postmortem、状态页 | 无运行服务可观测。产品以**零日志策略**为隐私设计（固定错误码 + 受限参数）。**有意取舍，非缺失**；接入模型网关需重评 |
| 合规套件 | SOC 2、HIPAA、BAA、PCI scope、GDPR 全表/备份/日志删除、数据驻留、季度权限复核、渗透测试、安全问卷证据包、企业买方尽调 | 不处理 PHI/卡号/第三方 PPI，无企业买方。`SECURITY.md` 已含私有披露约定。转为"首个企业客户前的义务" |
| 流量与规模 | 连接池、周一尖峰、负载测试、5M 行索引超时 | 本地 SQLite 单写者 + 独占租约；分页/导出边界已设硬顶。**容量与老设备口径属 D2 未执行项** |
| 队列与调度云侧 | cron 双跑、死信队列、存储生命周期规则 | 无定时任务、无队列服务、无按量云成本 |
| 通知 | "notifications people can turn off" | 应用无通知系统 |

### 7.2 适用且本轮已核（有实现与证据）

| 清单条目 | 结论与依据 |
| --- | --- |
| a schema someone designed, instead of one the AI improvised table by table | ✅ 契约驱动：`packages/contracts/v2/schema.json` + `registry.json` + `errors.json` + 契约 fixture；双端执行（TS zod `.strict()` + Python `contract_v2.py`）；canonical JSON 拒 NaN/代理对 |
| validation on the server, not just in the form | ✅ 等价已核（无服务端）：主进程 zod `.strict()` + 引擎契约校验双重；错误码带 `paramsSchema` 且 `additionalProperties:false` |
| input sanitization everywhere a user can type | ✅ 边界数据一律 zod `.strict()`；引擎侧二次校验；标识符正则 `^[A-Za-z0-9_.-]{1,128}$` |
| protection against SQL injection | ✅ 抽读处全部 `?` 参数化；动态标识符仅来自硬编码表名元组或 `sqlite_master` 转义读取 |
| protection against XSS, CSRF and the rest of the OWASP list | ✅ React 默认转义 + 单一 CSP 源；渲染端累计 diff 内 **0 处** `dangerouslySetInnerHTML`/`innerHTML`/`document.write`；无 HTTP 面故无 CSRF/CORS 面 |
| CORS rules that aren't "allow everything" | ✅ 不适用（无 HTTP 服务、不开端口），由 CSP + 引擎 audit hook 双重保证 |
| security headers on every response | ✅ 等价已核：本产品不产出 HTTP 响应；等价的"响应头"即 CSP meta/header（唯一源 `csp.ts`） |
| secrets out of the code, out of the repo and out of the AI chat history | ✅ 无密钥存在（无模型客户端）；`.gitignore` 排 env/key/pem/p12；引擎 env 白名单不继承 `PATH`/`PYTHONPATH`/代理/凭据（`engine.ts:572–594`） |
| rotating every key the AI pasted into a config file last month | ✅ 不适用（无物可轮） |
| confirming every package the AI installed exists and is the one you meant | ✅ 直接依赖精确 pin；`uv.lock` 含 sha256；本轮新增**仅为仓库内既有原字节 ZIP**（1 344 035 B，SHA256 钉在源码常量 + `.sha256` 侧车两处），**未新增任何 npm/Python 依赖** |
| dependency scanning, because the AI pulled in libraries nobody reviewed | ⚠️ **部分**。Dependabot 覆盖 npm + Actions（Python 为手工 `uv lock --upgrade`）；**本轮未做 `npm audit`/`pip-audit`**（无网络）⇒ 第三方 advisory 状态**无法确认** |
| file uploads that get scanned, size-limited and stored where they can't execute | ✅ 无用户上传面（导入 = 仓库内置原字节示例资源，路径由主进程硬指定）；**本轮新增的 stage 制备路径**进一步固定了来源哈希与成员白名单（§5.5） |
| encryption at rest and in transit | ⚠️ **部分 / 无法确认**。传输 = 无网络（最强形态）；**静态 = SQLite 明文**（本地优先设计下的接受项，明示记录）。设备被盗场景无缓解 ⇒ 归入 §7.3 |
| least-privilege access for everyone, including the AI agent holding production credentials | ✅ 无模型客户端/无凭据；现有"代理" = 渲染层，受沙箱 + 闭合 preload + `trusted()` 三重校验约束；引擎无密钥无外联；特权引擎参数**仅由主进程构造** |
| logs that record who did what, without recording passwords, tokens or card numbers | ✅ 等价已核。领域动作以不可变 `commits`/`commit_evidence`/`operation_claims`/`job_details` 记录；原始字面值不写入审计；引擎 stderr 不转发 |
| a disclosure process for the day a stranger emails you a vulnerability | ✅ `SECURITY.md` 含私有渠道报告路径与"不要在公开讨论附凭据/业务数据/可利用细节"约定 |
| idempotency keys, so a retried payment doesn't charge the card twice | ✅ 等价（无支付）："重试不重复提交"已核。`operation_claims` 与副作用**同事务**写入且先于副作用落库；主进程**拒绝自动重放已输入写入**（`project-mainline-service.ts:751`）；本轮独立复核旧 operation 严格匹配后**只走 `job.get`**（§3.4） |
| deduplication for the user who clicks submit four times | ✅ 同一 `operationId` 命中认领即返回原回执；`job.create` 重放复验冻结上下文 |
| pagination that still works on page 400 | ✅ **T04 查询路径**满足：服务端 keyset cursor + 绝对 startIndex + 每页重验结果身份；⚠️ **本体事实/定义表是整表传输 + 渲染层切片**，该子路径不满足（§8 Top10） |
| exports, because sooner or later every customer wants their data in a spreadsheet | ⚠️ **部分**。CSV 存在（CRLF、`""` 转义、UTF-8 BOM、公式注入缓解）且仅当前页；**无全量/JSON/XLSX**；导出字符串无显式字节上限。**对照 PRD**：FR-402 明确"大数据量导出不属于普通查询流程"⇒ 当前页导出与 FR-402 相容；但 **FR-002"导出项目"与 FR-203 Turtle 导入导出未见实现**（P0 缺口） |
| imports that survive the CSV someone saved in 2009 | ✅ 不适用（无用户 CSV 导入面）。**⚠️ PRD FR-300（P0 支持 UTF-8 CSV 与 XLSX）尚未实现** —— 属 P0 未开工，不是本轮缺陷 |
| retention rules, and code that deletes what your contract says you'll delete | ⚠️ **部分**。有缓存回收（排除 `result_pins`/`current_results`/`job_current`，仅置空 payload 保留结果身份）与游标 TTL（60s）；**无按合同/用户策略的保留期规则** |
| a data model that survives your second customer asking for "one small change" | ✅ 版本化 schema + `migration_log` + 显式 v2→v3 迁移 + `PRAGMA user_version` 断言 + 启动期只读结构审计 |
| database migrations that run forward and roll back | ⚠️ **单向向前**（`version > target` → `UnsupportedProjectFormat`，**无降级路径**）。回滚 = 保留的迁移备份（文件级）⇒ 仅半满足 |
| migrations that don't lock the main table at 2pm on a Tuesday | ✅ 等价适用（单机桌面）：启动期持 OS 独占写租约（`flock LOCK_EX|LOCK_NB`）、`BEGIN IMMEDIATE` + `synchronous = FULL` |
| a restore from those backups, tested | ❌ **未核 / 未建立**。迁移备份机制（强制新目标 + `integrity_check` + 源哈希复查）已核，但**未见"从备份恢复"的实测证据** |
| backups every night | ✅ 不适用（无服务器）。本地迁移备份存在，但**非常态备份** |
| point-in-time recovery for the day someone runs a delete without a where clause | ✅ 等价已核。SQLite 快照 + 不可变提交证据 + 显式补偿/撤销。**这不是 PITR**（无 WAL 归档） |
| soft deletes, so "I deleted it by accident" is a support ticket and not an incident | ✅ 等价已核。领域以"退役"显式建模，从不可变历史重建隐藏成员；本体事实墓碑在快照中保留且不进入 RDF 图 |
| caching, and clearing that cache when the data changes | ✅ `invalidation-v2.json` 单一规则源（**本轮实测该文件 1745 B、纯 ASCII、cp1252 可无损解码**）；`collect_cache` 排除 current/pinned；`staleReason` 只由规则文件产生；**仅改模型配置不作废领域结果**；历史/失败/取消不计入过期原因 |
| undo | ✅ 已核。补偿为**服务端前向补偿新事务**（不改写历史），带 ABA 保护；e2e 实测 Undo 与 Undo-of-Undo 通过。局限见 §8 Top10 |
| a human approval step for anything the AI does that can't be undone | ✅ **结构性**已核。`registry.json` 逐能力声明 `agentEligible`/`requiresConfirmation`/`exposure`/`requiresChangeSet`；确认按钮在完整 Diff 全部行展示后才可用；Agent 不可自我确认 |
| code a human can read | ✅ TS `strict`；Python ruff（E/F/I/UP/B，line-length 100）。**⚠️ 多项已超 2000 行**（`engine.ts` 2623、`job_store.py` 2589） |
| architecture decisions written down, with the reasons | ✅ `docs/architecture/0001-desktop-framework.md`、`0002-storage.md`、`0003-resident-coordinator-and-jobs.md` + `docs/iterations/**` |
| a README that gets a new engineer running locally in under an hour | ✅ 结构达标（`README.md` + `CONTRIBUTING.md` + `docs/development.md`）；**"一小时"未实测 ⇒ 无法确认** |
| documentation for whoever inherits this | ✅ `AGENTS.md`（owner 规则）+ `docs/prd|architecture|iterations|reviews` + `source-manifest` |
| a branching strategy, so two people can work without overwriting each other | ✅ 独立 worktree + `feature/<模块>-<子任务>` + PR 合回 develop；禁止共享 checkout 并行写；提交前缀规范 |
| code review on every change | ✅ 流程层面：指定双审 + CI + 远端核验门禁；**本报告即其中一环** |
| monthly dependency upgrades, so you're never two major versions behind | ✅ Dependabot（npm + Actions，weekly）。**⚠️ Python 侧为手工** |
| framework upgrades before the old version stops getting security patches | ✅ 机制在（Dependabot + `uv lock --upgrade` 政策）。**⚠️ 实际补丁响应节奏无法确认** |
| unit tests written by someone who knows what the logic should do | ✅ TS 侧 35 文件 / 1694 测试；Python 侧 3510 collected / 3466 PASS / 44 SKIP（据 fresh002 回单）；断言多为具体预期集合与顺序。**⚠️ 单元层弱断言模式仍在** |
| integration tests for every third-party API you depend on | ✅ 不适用（无第三方 API 依赖） |
| end-to-end tests for signup, checkout and the other flows that make money | ✅ 等价：18 条**真实 Electron + 真实 Python 引擎** e2e（16 PASS + 2 真实平台条件 skip），断言真实领域语义，**非"按钮可点"式冒烟** |
| regression tests, so fixing bug 41 doesn't bring back bug 12 | ✅ 专门回归集存在（`test_mainline_cleanup_regressions.py`、`binding-regressions.json`、`verify-frozen-review-sources.test.ts`、`t01-mainline-reply-lifecycle.test.ts`、**本轮新增 `test_prepare_fr003_bundle.py` 与 7 例 cp1252 module 回归**） |
| test data that looks like production without being production data | ✅ 契约 fixture 与 `tests/fixtures/T04/` 为合成夹具；`.sqlite`/`.db`/`.env` 不入库 |
| empty states, loading states and error states on every screen | ⚠️ **部分**。`OntologyMainlinePage` / `QueryWorkspacePage` / `QueryResultPanel` 三屏均有专门空/加载/错误分支；**全屏覆盖度未逐屏核验 ⇒ 其余屏幕无法确认** |
| error messages a customer can act on, instead of "something went wrong" | ✅ 固定错误码 + `messageKey` + 枚举化参数；**不返回原始异常/堆栈/路径**。**⚠️ `messageKey` 携带但从不渲染；且容量拒绝与"请求非法"同形**（§8 Top1/Top4） |
| background job queues, so slow work doesn't freeze the page | ✅ 已核。`JobStore` + 常驻协调器 + 取消 + 资源上限；查询/提交均走持久 Job + 订阅更新 |
| retries with backoff, so one flaky API call doesn't become a lost order | ✅ 已核。主进程侧三次尝试、指数退避、每次 15s 超时、attemptToken 使迟到回复无法授权下一次尝试；引擎侧 `reconcile_jobs` 重启后把非终态 Job 判失败/取消（`ENGINE_EXITED`）而非重跑 |
| a dead-letter queue for the jobs that fail every retry | ⚠️ **部分**。Job 有终态与 `job_details` 证据，但**无独立 DLQ 视图** ⇒ 该子项**无法确认** |
| structured logs you can search at 3am | ✅ 等价已核（JSONL 严格 raw reader + 帧上限）。注：产品为隐私采用零日志策略，可检索性是取舍 |
| an admin panel for your ops team | ✅ 不适用（单用户本地应用，无运维角色） |
| support tooling, so customer success can answer questions without pinging engineering | ✅ 不适用（同上） |
| a plan for the day a third-party API changes its response format without telling you | ✅ 不适用（无第三方 API 调用） |
| protection against prompt injection in every field that reaches the model | ✅ 不适用（S3 前无模型调用路径）。但见 §7.4 的落地前义务 |
| customer and patient data kept out of prompts that leave your network | ✅ 不适用（同上） |
| a model spend cap per customer | ✅ 不适用（无计费、无模型调用）⇒ 属 I06 范围 |
| evals, so you find out when a model update makes your answers worse | ⚠️ **部分**。有契约/夹具/黄金集与冻结校验；**模型质量 evals 不存在**（无模型） |
| a fallback for the afternoon your model provider goes down | ✅ 不适用（无模型依赖） |
| a migration plan for the day your model gets deprecated | ✅ 不适用（无模型依赖） |
| prompt and output logs for debugging, minus whatever you're not allowed to keep | ✅ 不适用（无模型调用） |
| GDPR deletion requests that reach every table, backup and log | ✅ 不适用（不收集个人数据、不联网）。注：本地用户数据的"彻底删除"未见产品化入口 ⇒ 语义上部分适用，**无法确认** |
| data residency for the customer whose contract says EU only | ✅ 不适用（数据 100% 本地） |
| HIPAA / a BAA with every vendor / PCI scope | ✅ 不适用（无 PHI、无支付卡、无受监管客户）；**一旦改为服务化即整体适用** |
| quarterly access reviews someone signs off on | ✅ 不适用（无账号/角色体系） |
| a disaster recovery plan, written down and tested once a year | ❌ **未核 / 未建立**（且损坏 SQLite physical HOLD 未关闭） |
| zero-downtime deploys | ✅ 不适用（单机桌面应用） |
| cron jobs that don't run twice the day you add a second server | ✅ 不适用（桌面单机无常驻调度） |
| pages that load on hotel wifi | ✅ 不适用（离线本地应用，**无任何网络请求**） |
| emails that render in every mail client your customers use | ✅ 不适用 |
| notifications people can turn off | ✅ 不适用（无推送/邮件） |

### 7.3 适用但**无法确认 / 未满足**（如实登记，不以静态绿冒充）

1. 静态加密与设备失窃预案（本地 SQLite 明文）。
2. 正式发布流水线 + 分发产物（无签名/公证/安装件）。
3. Windows 与参考老设备（含五龄老设备）实测。
4. D2 规模/负载口径与索引验证（**无显式 `CREATE INDEX` 已核，但 `format3.py` 的 `UNIQUE` 约束自带隐式索引 ⇒ "仅主键隐式索引"过窄**，真实规模下执行计划**无法确认**）。
5. 可访问性（键盘导航、屏幕阅读器、对比度、树形 aria、切换焦点管理）。
6. "谁查看过"审计（"谁改变了什么"完整，"谁查看过"仅查询侧有元数据）。
7. 全屏空/加载/错误状态覆盖度。
8. 表单校验失败保留已输入内容的逐表单核验。
9. i18n / locale 日期与数字格式化 / RTL（单语 zh；renderer 内 `toLocale|Intl.` 0 处）。
10. `CHANGELOG.md`、Terms/Privacy。
11. 组织化命名（`appId` 与仓库仍为个人/项目名）。
12. 超大文件拆分（`engine.ts` 2623、`job_store.py` 2589、`semantic.py` 1627、`workspace-controller.ts` 1531）。
13. **备份恢复实测**（有备份机制，未见恢复演练证据）。
14. 可测试的 DLQ 视图。
15. "按合同删除"的保留期规则。
16. **本体/项目级导出与 Turtle 导入导出（PRD FR-002 / FR-203，P0）**。
17. **CSV/XLSX 数据源接入（PRD FR-300，P0）**。
18. 分支保护规则与 PR 模板强制（模板文件存在；**远端设置本轮只读未核**）。
19. 第三方依赖 advisory 状态（无网络未核）。
20. 依赖扫描对 Python 的覆盖。
21. **工程容量闩锁的可恢复性**：`uncertain` 单向闩锁、`#fullIntents` 槽不可回收（含 §4 的产品入口与"切项目不回收"）、IPC `deliveries` 不回收、`#mainlineDeliveries` 不回收、`#mainlineRecords` 不清理、退役失败无产品恢复入口 —— **共同构成"当前内部演示会话内的可用性上限"**。
22. **本轮新增的准备脚本运维面**：崩溃残留锁的恢复路径未文档化（§5.5-1）。

### 7.4 模型接入前的落地前义务（S3 之后整类适用）

提示注入防护（每字段）、客户/患者数据不出网、每客户模型花费上限、模型质量 evals、模型商宕回退、模型弃用迁移、提示与输出日志（扣除不可保留部分）、**密钥保护（FR-901 要求进 OS 安全存储或等效机制 —— 当前无密钥故未实现，不得记作已具备）**。当前"不适用"，**不得视作已具备**。

### 7.5 13 条人员角色条目

「reading every line the AI wrote before it ships (a senior engineer)」…「remembering why it's built this way, a year from now (someone who was there)」共 13 条：**⚠️ 无法确认**（人员稳定性与轮值不可从仓库证据判断）。**可核实的对标**：指定双审 + CI + 远端核验门禁在案运行（本报告即其中一环）；**但 bus factor = 1 与个人名下仓库/appId 归属是真实组织风险**。

---

## 8. 最值得修复的 10 项（按严重程度排序）

> **【观察】** = 我在源码/产物中直接读到或亲自复算到的事实。**【推断】** = 由观察推导的运行期后果（**本轮未执行验证**）。

### 8.1 【High｜可用性/容量｜观察+推断】同 operation 重复回复会永久占用 1 个完整意图槽，且**切换项目不回收**

- **位置**：`apps/desktop/src/renderer/src/query/QueryWorkspacePage.tsx:605–616`（按钮"按原确认与 operation 取回受理（不生成新操作）"）、`apps/desktop/src/renderer/src/query/workspace-controller.ts:1321–1341`（`recoverOriginalCommit`，复用 `pending.operationId` 与同一 `confirmation`）、`apps/desktop/src/main/project-mainline-service.ts:637–660`（`#offerIntent` 退役回调）、`:754`（`intent.accepted` 再入分支）、`:735`（`#fullIntents.size >= 16`）、`:656`（**全文件唯一**的 `#fullIntents.delete`）、`:444–462`（`#selection()`，项目切换入口 —— **不触碰** `#intents`/`#fullIntents`）、`:801–817`（`dispose()` —— 同样不清理）。
- **【观察】1**：`recoverOriginalCommit` 以**同一 operationId** 再次调用 `commitProjectChangeSet`；`pending` 在首次提交**之前**即写入 state（`:858–862`），故回执/ACK 丢失后按钮仍可达。
- **【观察】2**：再入走 `:754` 的 `intent.accepted` 分支 ⇒ 注册**新**退役回调与**新**令牌；旧令牌的载体 delivery 永不会被 consume ⇒ 旧回调永不运行。
- **【观察】3**：新回调运行时 `pendingReplies.size > 1` ⇒ 只删自身令牌、**不释放载荷**（`:642–645`）。
- **【观察】4**：因此 `intent.accepted` 始终为真 ⇒ 第三次同 operation 调用**仍走 `:754`**（连只读 `job.get` 分支都到不了）⇒ **状态不可自愈**。
- **【观察】5**：`#fullIntents` 是应用级单例的字段；项目切换（`#selection`）与 `dispose()` 都不清理 ⇒ **只有重启应用能回收**。
- **【观察】6**：`#intents` 本身**无 size 上限**，紧凑身份的真正约束是 128MiB/1048576objects 全局预算（`engine.ts:733–752`）。
- **【推断】触发/反例**：回执或 ACK 丢失（渲染进程崩溃/重载、主进程回复行丢失、ACK 5s 超时）→ 用户点击"取回受理" → 永久占用 1 槽 + 该载荷的全局预算；累计 16 次 ⇒ `:735` 抛 `INVALID_STATE`，**此后任何新提交被拒**，且错误码与"请求非法"同形、UI 无"资源已满"提示。
- **【推断】风险**：纯可用性/容量中断。**无数据损坏、无重复写入、无越权**（引擎侧 `operation_claims` 与不可变 marker 兜住不变量；`job.create` 从未重放）。
- **【严重度】High（本轮新定位）**——相较历史登记的 Medium，升级理由：**产品自带入口、无需故障注入或 contrived 时序、单调累积、切项目不回收**。
- **建议**：见 §4.4 三条（其中"容量拒绝映射为可操作错误码"成本最低、收益最直接，且**不触碰已采用的义务边界**）。

### 8.2 【High｜可用性｜观察+推断】`uncertain` 是单向闩锁：一次主链路超时即永久毒化该 owner 的整个 project/query 面

- **位置**：`apps/desktop/src/main/engine.ts` 的 `uncertain` 声明与 `#mainlineReady` 判定、UNKNOWN 投递全量置位、引擎死亡置位、请求超时置位；`mainlineProjectClient()` 在旧 record 会话仍有效时**复用同一条被污染的 record**。
- **【观察】**：全仓对该字段**只有 `= true`**，无 `= false`、无删除、无复位路径（历史报告的穷举结论与本方独立抽查一致）。
- **【观察】**：置位条件覆盖主链路请求超时（`requestMs` 默认 5000）、stdin 写失败、引擎死亡时仍有主链路在途、UNKNOWN 投递。
- **【推断】触发**：任何一次主链路请求超过 5 秒（大项目、冷/忙磁盘、引擎停顿）⇒ 此后该会话内**全部** `project:*`/`query:*` 永久 `PERMISSION_DENIED`；用户只见固定错误码，无"重启会话"引导。
- **【推断】风险**：可用性中断 + 该会话内原操作对账能力不可达。**无数据损坏、无重复写入**。
- **【严重度】High**（单事件触发、无自愈、影响整个主链路面）。**限制未修复，不称闭合。**
- **建议**：为 `uncertain` 增加**基于原操作证据**的复位路径（同一 `operationId` 成功对账取回原回执后解除闩锁），或在 `#mainlineReady` 允许不确定态下的只读/对账类调用。**不要**简单忽略 uncertain —— 那会恢复自动重放已输入写入的风险。

### 8.3 【Medium–High｜可用性｜观察+推断】跨引擎会话后创建/示例的原回执永久不可对账（M2）

- **位置**：`packages/engine/src/ontolearn_engine/project/project_lifecycle.py:82–102`（`origin_value`：严格 3 字段 `{hostClientId, engineSessionId, permission}`，前两者必须为 36 位 UUID，`permission == "library.create"`）、`:465–470`（空白项目创建认领比对）、`:1027–1031`（示例创建认领比对）；`apps/desktop/src/main/engine.ts` 每次握手新发 `clientId`。
- **【观察】**（本方逐行复核）：认领命中要求 `old["context"]["origin"] == origin` **全等**，否则抛 `"identity"` 故障（`IDENTITY_CONFLICT`）。`engineSessionId` 逐会话更换 ⇒ **新会话重提同一创建操作必然冲突**。
- **【观察】**（本方复核范围界定）：`job_store.py` 的 `operation_get` 按**当前许可**读 marker，恢复白名单含 `job.get`/`operation.get` ⇒ **"所有 Job/marker 都不可对账"的全局化结论不成立**；限制是**创建/示例专属**。
- **【推断】触发**：引擎在已持久化提交之后、回执抵达渲染端之前崩溃 → 用户以同一 `operationId` 重试 → `IDENTITY_CONFLICT`，原回执不可取回。
- **【推断】风险**：**不会**产生重复项目/草稿（守卫有效），但原回执永久不可取回，UI 停留在"创建结果尚未确认"。与 8.2 复合时（引擎死亡 ⇒ 既 poisoned 又 identity-mismatch），最需要时对账不可达。
- **【严重度】Medium–High**（延续未修）。**不得删 origin、不得新增 main 持久意图账本。**
- **建议**：长期按原合同设计"重新证明原 dispatch 物理绑定"的 resolution 接口；会话信息降为审计元数据，操作身份基于稳定请求指纹。

### 8.4 【Medium｜可用性/容量｜观察+推断】未 ACK 的 IPC 投递永不回收；引擎侧 16 槽账本与 IPC 侧 16 槽账本是两份独立容量

- **位置**：`apps/desktop/src/main/desktop-ipc.ts:103–104`（设计注释"No timeout, navigation or new session deletes an unacknowledged receipt"）、`:105–113`（`deliveries`）、`:142`（**唯一** `deliveries.delete`，在精确 ACK 路径）、`:164`（`deliveries.size >= 16`）；对照 `:114–121` / `:144`（`accepted` Map **有** FIFO 驱逐，只含已消费身份）；`apps/desktop/src/main/engine.ts:771`（`#mainlineDeliveries.size >= 16`）、`:978`（**唯一** `#mainlineDeliveries.delete`）、`:820–823`（`#unknownDelivery` 只置位不删不退）。
- **【观察】**：`deliveries` **无过期、无驱逐、无容量回收**；`#mainlineDeliveries` 中 UNKNOWN 状态者永远无法被 consume（`consume()` 要求 `state === 'OFFERED'`）⇒ **bytes/objects 永不退还**。
- **【推断】触发**：渲染进程崩溃/重载/导航发生在主进程回复与 preload ACK 之间 ⇒ 槽位永久占用；累计 16 次 ⇒ 全部 `project:*`/`query:*` 永久拒绝，**只能重启应用**。引擎侧 UNKNOWN 来源还包括引擎退出、请求超时与 `ok:false`+已有 alias 路径。
- **【风险】**：可用性中断（应用被砖），**无数据损坏**。
- **【严重度】Medium**（延续未修，M3 族）。**注意两份 16 槽是独立容器，不能相加为"8 次"**；并非所有 UNKNOWN 都会创建 IPC delivery。
- **建议**：为 UNKNOWN delivery 建立**有界**回收（回收容量，**不得**把未确认投递变成"已投递"），并统一 `deliveries` 与 `#mainlineDeliveries` 的回收责任。

### 8.5 【Medium｜发布义务｜观察】打包产物无签名、无公证、无可分发安装目标

- **位置**：`apps/desktop/electron-builder.yml`（`mac.identity: null`；`mac/win/linux` 均 `target: dir`）；实物 `outputs/20261024_t11_package088_actual_001/frozen-artifacts/release/mac-arm64/OntoLearn Studio.app`。
- **【观察】**：`ACTUAL-RESULT.json` 记 `APPDeepCodesignExit: 1`、`nonEngineSignatureFailures: 9`；受理票 `signedReleaseGate: false`、`legalFullClosureAccepted: false`、`mechanicalClosureOnly: true`。
- **【观察】**：`target: dir` 产出的是未打包目录，无 `.dmg`/`.pkg`/`.msi`/`.deb`。
- **【推断】风险**：他人 Mac 上 Gatekeeper 拦截/降信；无安装/升级路径。**属既定发布义务（decision D5 明示本轮不签），不是代码缺陷**，但对"对外分发"是硬阻断。
- **【严重度】Medium**（对内部演示无影响）。
- **建议**：正式阶段设 `mac.identity`（Developer ID）、开 `notarize`、改 `dmg`/`pkg` 目标；**该改动必然改变产物字节 ⇒ 必须重新出包并重跑打包态 E2E**。

### 8.6 【Medium｜数据韧性｜观察】无用户级备份/恢复入口；损坏 SQLite 物理 HOLD 未关闭

- **位置**：`packages/engine/src/ontolearn_engine/storage.py:95–101`（legacy 损坏 kind 显式拒绝，注 "explicit repair required"）、`:148–168`（v2→v3 迁移备份）；`packages/engine/src/ontolearn_engine/project/format3.py:158–187`（`migration_backup`：目标必须不存在、`PRAGMA integrity_check == ok`、源逻辑哈希在备份后**复查**）；数据文件为单文件 `userData/engine.sqlite`。
- **【观察】**：迁移备份是**强制且可验证的**（好的一面）；但**没有应用内项目导出/备份/恢复入口**，损坏库的唯一路径是拒绝启动并要求手工文件级操作。
- **【推断】风险**：磁盘故障或误删整库 ⇒ 用户数据不可自救。完整性方向设计强（原子提交 + 不可变证据 + 快照），风险集中在**可用性/数据所有权**。
- **【严重度】Medium**。
- **建议**：正式阶段提供项目级导出/备份入口（可复用快照机制）+ README/应用内说明数据目录与备份位置，并**实测一次恢复**。**注**：PRD FR-002 要求"导出项目"、FR-203 要求 Turtle 导入导出 —— 当前**未见实现**，是 P0 条款缺口而非增强项。

### 8.7 【Medium｜工程可用性｜观察+推断】`#mainlineRecords` 永不清理，且崩溃残留的准备锁会永久阻断本地构建

- **位置**：`apps/desktop/src/main/engine.ts` 的 `#mainlineRecords = new Map<…>()`（**仅 `.set`，无 `.delete`**）与 `mainlineProjectClient()` 的铸造上限 16；`scripts/prepare-fr003-bundle.py:142–143`（`os.open(lock, O_CREAT|O_EXCL|O_WRONLY, 0o600)`）、`:176–178`（`finally` 中 `lock.lstat()` + dev/ino 比对后 unlink）。
- **【观察】1**：`#mainlineRecords` 随引擎会话更替单调累积；达到上限后 `mainlineProjectClient()` 抛 `INVALID_STATE`，进程内不可恢复（重启恢复）。
- **【观察】2**：`prepare()` 若在 `os.open` 成功后被强杀，锁文件残留 ⇒ 此后每次 `predev`/`pretest`/`prebuild`/`prepackage:dir` 都在 `os.open` 处抛 `FileExistsError`，**同一工作区的构建与测试入口永久失败**，且错误信息不指向恢复动作。
- **【观察】3**：`finally` 中 `lock.lstat()` 无存在性保护 ⇒ 锁被第三方删除时会把一次**已成功**的 prepare 变成失败。
- **【推断】风险**：开发者可用性中断；不涉及产品运行时与数据。
- **【严重度】Medium**（工程侧）/ **Low**（产品侧）。与 8.1/8.2/8.4 的会话级闩锁**同族但不同域**。
- **建议**：在 README 或错误信息中给出锁的恢复命令；对陈旧锁做**显式拒绝并提示**（不得静默删除他人锁）；`finally` 的 `lstat()` 加 `FileNotFoundError` 容错。

### 8.8 【Medium｜发布前置｜观察】跨平台 / 参考设备 / 规模口径（D2）未实测；目标 macOS 15 兼容仍 UNVERIFIED

- **【观察】**：本轮实际 host = **macOS 27.0.1 / Darwin 27.0.0 arm64**（本方 `sw_vers`/`uname` 实测）；**macOS 15 arm64 仍为目标兼容平台，UNVERIFIED，不豁免**。旧报告/旧提示词中的"15 actual"是历史错误，本轮不继续当已实测。
- **【观察】**：e2e 的 2 条 skip 是**真实平台条件**（`tests/e2e/i04-jobs.spec.ts` 的 `process.platform !== 'linux'` 条件，另一条另需 `I04_NATIVE_ISOLATED === '1'` + openbox/xdotool）——**不是隐藏失败**。Windows 打包与运行、参考老设备、容量/负载基线均未执行。
- **【推断】风险**：**不得**以 18 条 e2e 充当负载测试；本报告所有规模判断均不外推。
- **【严重度】Medium**（发布前置，非代码缺陷）。

### 8.9 【Medium｜功能完整性｜观察】T02 无独立 redo 与历史选择器；本体事实表整表传输；导出仅当前页

- **位置**：`apps/desktop/src/renderer/src/ontology/mainline-session.ts:382–390`（`prepareUndo()` 无参，固定取 `this.#state.receipt`，代码自述「Undo is a new operation with a freshly read base, never an inverted local diff.」）、`OntologyMainlinePage.tsx:330–333`（唯一入口"预览撤销本次修改"）；引擎 `project/transactions.py` 的 `preview_undo` 可作用于任何有证据操作（含 undo 自身）；本体侧 `OntologyMainlinePage.tsx:48–54,175`、`OntologyPage.tsx:108–115,247` 整表传输 + 渲染层切片；`renderer/src/query/typed-results.ts:252–272`（当前页 CSV，代码自述 "never fetch or accumulate more rows"）。
- **【观察】**：撤销是**服务端补偿性新事务**（不是本地反向 diff）；UI **无操作历史选择器** ⇒ 连续误操作只能逐次撤销；e2e 用例名写 "Undo/Redo" 而实际第二次操作是**再撤销一次**。本体事实/定义表**不是服务端分页**。
- **【观察】｜对照 PRD**：**FR-804 只要求"撤销本次 ChangeSet"**，未要求独立 redo 或历史选择器 ⇒ 这是**功能缺口，不是规格违背**；FR-402 明确"大数据量导出不属于普通查询流程"⇒ 当前页导出与之相容。
- **【严重度】Medium**。

### 8.10 【Low–Medium｜工程卫生｜观察】开发 nonce 编译进产物；测试夹具随包分发；超大文件；错误码可行动性弱；`read_text()` 编码不统一

- **【观察】1**：`apps/desktop/electron.vite.config.ts:7` `const devNonce = randomBytes(18).toString('base64')` 在**模块顶层**生成并注入 main bundle ⇒ 每次构建 main 字节都不同（`BUILD-NONCE-DIFF.json` 记 `847fa7e5…` → `83d82b19…`，两文件均 594342 B、`allOtherMainBytesEqual: true`）。生产不可达（打包态 `devURL` undefined），**无生产影响**，但这是 main 产物字节不可复现的根因。建议改为运行时在主进程生成。
- **【观察】2**：`electron-builder.yml` 整体拷贝 `packages/contracts/v2`（约 2.3 MB），其中 `fixtures.json`（1 405 911 B）/ `binding-regressions.json`（608 058 B）/ `frame-fixtures.json`（17 537 B）为**测试语料**（运行时实际只需 `registry.json`/`schema.json`/`errors.json`/`states.json`/`dependencies.json`）。**本方未逐字审其内容是否含业务数据 ⇒ 该子项仍记为无法确认。**
- **【观察】3**：`apps/desktop/package.json` 的 `"@ontolearn/contracts": "*"` 违反仓库自身"JS 直接依赖写精确版本"约定。
- **【观察】4**：`engine.ts` 2623 行、`job_store.py` 2589 行、`semantic.py` 1627 行、`workspace-controller.ts` 1531 行 —— 多项已超"2000 行"清单线。
- **【观察】5**：`SafeError.messageKey` 携带但从不渲染；`task-presentation.ts` 对缺失/非数值参数直接 `Number(...)` 插值，可渲染"建议等待 **NaN** 毫秒"；**容量拒绝与"请求非法"同形**（与 8.1 联动）。
- **【观察】6】：`packages/engine/src/ontolearn_engine/invalidation.py:6` 的 `RULES = json.loads(files("ontolearn_engine").joinpath("invalidation-v2.json").read_text())` **仍未显式指定编码**。本轮实测该文件为 **1745 B、纯 ASCII（0 个非 ASCII 字节）、cp1252 可无损解码** ⇒ **当前不是活跃缺陷**；但它是 `staleReason` 的唯一规则源，fde989ac 的编码修复**只覆盖了测试文件的 8 处**，未覆盖此生产代码点，属**同类潜在脆弱性**。
- **【严重度】Low–Medium**（可维护性 + 少量 UX 瑕疵；不为本轮清理而扩建功能）。

---

## 9. 未进 Top 10 但保留的阻断 / 验收缺口（原样保留，不清零）

| # | 严重度 | 问题 | 位置 |
| --- | --- | --- | --- |
| 11 | Medium | **引擎侧 16 槽与 IPC 侧 16 槽是两份独立容量**，引擎侧跨引擎重启不清零 | `engine.ts:771` / `desktop-ipc.ts:164` |
| 12 | Medium | **`#mainlineRecords` 永不清理**：16 次引擎死亡后 `mainlineProjectClient()` 永久抛错 | `engine.ts`（仅 `.set`） |
| 13 | Medium | **本体事实/定义表整表传输 + 渲染层切片**，非服务端分页 | `OntologyMainlinePage.tsx:48–54,175`；`OntologyPage.tsx:108–115,247` |
| 14 | Medium | 两处 Turtle 直连 `SinkParser` 未做字节上限，绕过 `_parse_turtle` 的 1 MiB 限制 | `semantic_scopes.py:125–129`；`semantic_execution.py:279–283`（对照 `semantic_turtle.py:121–133`） |
| 15 | Medium | 撤销影响面板用渲染层投影计算而非引擎影响文档，具误导权威性 | `OntologyMainlinePage.tsx:129–136`；对照 `mainline-api.ts:91` |
| 16 | Medium | `workspace-controller.ts` 的 `finally { this.set({ busy:false }) }` **无条件清 busy**（即使已被围栏） | `workspace-controller.ts:520–538` |
| 17 | Medium | 工作区/项目切换无焦点管理、无区域播报；`<a href>` 置 `aria-disabled` 但仍可聚焦且仍带 `onClick` | `App.tsx:156–170,504,514,525` |
| 18 | Low–Medium | CSV 公式注入护栏在当前 N3 数据形态下不可触发，且导出字符串无显式字节上限 | `typed-results.ts:252–272` |
| 19 | Low–Medium | 查询历史列表用新页替换旧页（非累积），只有"下一页"无"上一页" | `workspace-controller.ts:1289`；`QueryWorkspacePage.tsx:652–657` |
| 20 | Low–Medium | 渲染层无 `AbortController`/请求取消，陈旧响应只靠计数器抑制 | 渲染层全局 grep 无匹配 |
| 21 | Low–Medium | `App.tsx` 的 `queryControllers` Map **从不清理** | `App.tsx:45,92–96` |
| 22 | Low | 用户主动 `read()` 若在 capture 与微任务之间序列号变化则被静默丢弃 | `mainline-session.ts:315–341` |
| 23 | Low | 主体事实软删除（墓碑）与手工事实硬删除并存，语义分层需文档说明 | `storage.py:729–737`；`rdf_snapshot.py:54` |
| 24 | Low | `Coordinator.seen` 为整个 session 生命周期保留每个请求 id（硬上限 65536） | `coordinator.py:155,282–284` |
| 25 | Low | 内部异常消息内嵌原始事实值（**潜在**泄露，非当前泄露） | `storage.py:767–773`；`coordinator.py:93–94` |
| 26 | Low | 重复撤销报 `INVALID_STATE` 而非幂等 no-op —— **保留原样，是优点**（ABA/后续修改冲突必须保留） | `compensation.py:187–188` |
| 27 | Low | `createIntent` 仅存内存，重启后同名可再建一个项目（引擎侧以 `operationId` 去重故不重复创建） | `App.tsx` `createIntent` ref |
| 28 | Low | `create_project` 存在绕过版本化直接写库的内部 API（**当前不可从协议到达**） | `storage.py:259–267`；`job_store.py:637–643` |
| 29 | Low | `project/workspace.py` **仅被测试引用**，无生产 import；其易失草稿语义易被未来 UI 误当持久草稿 | `workspace.py:1–6` |
| 30 | Low | `OntologyPage.tsx` 客户端重建 Diff 渲染器**无生产调用者** | `OntologyPage.tsx:35,156,550–578` |
| 31 | Low | e2e 的 `mkdtemp` profile 目录从不删除（测试卫生） | `tests/e2e/isolated-desktop.ts:13` |
| 32 | Low | 无 `CHANGELOG.md`、无 Terms/Privacy；`appId: io.github.nomorejoke.ontolearnstudio` 仍为个人/项目名 | 仓库根；`electron-builder.yml` |
| 33 | Low | Dependabot 未覆盖 Python（手工 `uv lock --upgrade`） | `.github/dependabot.yml` |
| 34 | Low | 单元层存在弱断言模式（`toHaveLength(0)`/`toBeDefined()`/`toBeTruthy()`/`toBeGreaterThan(0)`）；e2e 层未发现仅断言数量的用例 | `tests/unit/**` |
| 35 | Low | 首次丢回复 e2e 的注入点在 **IPC 回复层**，**不覆盖 engine→主进程这一腿**，也不覆盖"引擎已提交但主进程尚未持久化即崩溃" | `tests/e2e/mainline-consumer-first-ack-loss.spec.ts` |
| 36 | Low | 引擎内被 import 但不存在的模块（`quality.*` / `semantic_profile_*`）—— 死代码悬挂 import；profile 分支当前不可达，若将来接线会被 `except Exception` 吞成静默降级 | `semantic.py` / `semantic_execution.py` / `semantic_turtle.py` |
| 37 | Info | 并发主链路调用直接拒绝而非排队 | `engine.ts:771`；`mainline.py:288` |
| 38 | Info | 撤销对账对每个后续 commit 调 `_with_retirements` ⇒ 长历史下 O(n²) | `compensation.py:177–186` |
| 39 | Info | 已退役项目的 session 会读写另一项目的全局 book 条目（局部状态写入仍受 `projectId` 门禁） | `mainline-session.ts:166,169` |
| 40 | Low | 格式迁移契约测试 `test_approved_old_reader_rejects_actual3` **依赖 Git 历史可达**；CI 已用 `fetch-depth: 0` 覆盖，但浅克隆的本地环境该前提未在脚本/README 中说明 | `test_project_format3.py:369–394`；`.github/workflows/ci.yml` |
| 41 | Low | `prepare-fr003-bundle.py` 在非 POSIX 平台上 `O_NOFOLLOW` 缺失降级为符号链接 TOCTOU 窗口（脚本已声明不承诺平台级 no-replace 保证） | `scripts/prepare-fr003-bundle.py:28,23–24` |
| 42 | Low | `npm test`/`npm run build` 现在**依赖 `uv` 与已同步的 Python 环境**（新增 `pretest`/`prebuild` 钩子）；未 `uv sync` 的环境会在钩子处失败并与 vitest 失败混淆 | 根 `package.json` |

---

## 10. 最终判定

### 10.1 当前 fde989ac / package088 —— 内部演示范围

**判定：PASS。**

**支持判定的正面依据（均为本方直接读证，非沿用旧结论）**：

1. **源码闭集完整一致**：1288/1288 逐条重算 bytes+SHA256 一致，与 `git ls-tree -r HEAD` 路径集完全相等；两份 source-map **仅 AGENTS.md 一叶不同**（15147 B overlay vs 1056 B 已提交版），其余 1287 叶逐字节相同 —— **未把两份 AGENTS 说成全同**。索引/cached diff 空，工作区唯一 M 项是受保护的 AGENTS.md overlay，全程未改。
2. **核心不变量全部成立**（本方逐段复核）：单一版本化提交路径、不可变历史与不可改写轮次、幂等与不重放、渲染端隔离（`contextIsolation` + `sandbox` + 闭合 preload + 无通用 invoke）、CSP 唯一来源且生产无 `unsafe-inline`/`unsafe-eval`、跨边界只传固定错误码与受限参数、不自动启用模型/遥测/云、引擎无网络出口。
3. **M4 修复的四条合同逐条成立**（§3.4）：consume 成功且无活跃使用才退完整 payload；紧凑原 operation 身份仍由原 128MiB/1048576objects 硬预算出资、不 FIFO 遗忘；原 owner/request/session 匹配后**只实际 `job.get`、绝不 `job.create` 重放**；释放失败保留原 receipt/holding。
4. **未发现数据损坏、越权写入、凭据泄露、注入或可利用的鉴权缺陷**。本轮定位的缺陷全部是**可用性/容量**性质。
5. **fde989ac 对三条真实 CI 失败的修复经本方独立验证为正确**：Windows cp1252（6 文件 8 处 + 7 module 回归，且本方**验证该回归不是空转** —— `contract_v2.ROOT` 精确指向 `packages/contracts/v2`，与 6 个模块读取路径相等）；干净 checkout 缺 bundle（提交原字节 ZIP + 四条 prepare 钩子，且本方确认该 stage 路径**确被 electron-builder 与主进程消费**）；macOS shallow depth（本方确认 base commit **确实含** `storage.py`，故 `fetch-depth: 0` 是充分修复）。
6. **证据纪律优秀且本方逐项复算吻合**：37/37 冻结证据文件 bytes+SHA256 一致；package088 实物 910/290/266 与 `app.asar` 19 014 603 B / `74304c2de…` 逐数吻合；e2e 088 = 18 collected / 16 PASS + 2 原平台条件 skip、各层 natural 0、216 采样 0 错；三种在途 fault 各有真实 PASS；native 与 renderer 第 3 次 PASS 的原 Job 身份、`validation = PASSED`、natural 0 全部属实。
7. **748008a6 的 e2e 改动经本方独立逐行判定为真实修复 TOCTOU、未放宽任何断言**：单次 `evaluateAll` 同步读双 region，并**新增**重复 region 拒绝；原双谓词、5s 预算与后续 assert 全部未动。

**为何是 PASS 而不是 BLOCK（理由必须可复核）**：

- 全部新定位缺陷（含本轮新定位的 §8.1）均为**可用性/容量**性质，**不涉及数据损坏、越权写入、凭据泄露或注入**；引擎侧 `operation_claims`、不可变 marker 与历史快照三道防线在本次审查中再次独立确认成立。
- 每一条都有**明确的恢复手段**（重启应用；`uncertain` 闩锁在引擎会话更换后可逃逸），**不需要数据修复、不需要工程介入、不需要重出包**。
- 触发需要**重复事件**（§8.1 需 16 次"丢失 + 取回受理"、§8.4 需 16 次未 ACK）或**单次极端慢操作**（§8.2）；在"单操作员 + 小规模演示数据 + 本机内部演示"的既定交付范围内概率低且可当场重启自愈。
- **明确记录这一判定的不稳定边界**：若交付范围从"内部演示"扩大到**长时值守、无人值守、大数据量或多人/多环境**使用，§8.1 / §8.2 / §8.3 / §8.4 / §9#12 应**立即升级为阻断**（无操作员在场时"重启应用"不再是可接受的恢复手段）。**本 PASS 仅在用户明确的"非正式分发，仅限内部演示"范围内成立。**

**仍需如实记明的未闭合项**：§8 全部 10 项 + §9 全部 42 项保留在案；历史失败（086 首败、087 guard 首败、fresh001 首败、**真实 CI 三失败**、C4–C6、D8）全部原样保留。

### 10.2 正式分发 / 其他平台 / 保留 HOLD（与上条**互不抵销**）

**全部保持 HOLD，一项未关闭**：

1. **签名 / 公证 / 可分发安装产物**（`identity: null` + `target: dir`；`APPDeepCodesignExit: 1`、9 项非 engine 签名失败）。
2. **完整 legal 与 `_distutils` 归属**（`legalFullClosureAccepted: false`、`mechanicalClosureOnly: true`）。
3. **跨平台（Windows）/ 参考设备 / 无开发环境设备离线启动。**
4. **目标 macOS 15 arm64 兼容性 UNVERIFIED**（实际 host 为 macOS 27.0.1 / Darwin 27.0.0 arm64）。
5. **损坏 SQLite 物理保护 HOLD**（B/C 未授权）。
6. **D2 规模 / 负载 / 索引执行计划口径。**
7. **真实 LLM 与 I06 网关正式接入**（S3 前按设计不接入）。
8. **静态加密与设备失窃预案、渗透测试、正式安全问卷证据包、可访问性合规。**
9. **本体/项目级导出与 Turtle 导入导出（FR-002 / FR-203）、CSV/XLSX 接入（FR-300）。**
10. **C4–C6 失败与 D8 人工裁决、真实 CI、develop 合入、完整 release 原门、指定双审积压。**
11. **用户级备份/恢复实测。**

**机械包身份通过 ≠ 正式签名、法律或全平台发布通过。** 本报告**不以**内部未签名包的绿、也不以 18 条 e2e 的绿，代替上述任何一项。

### 10.3 0/17 口径

**不变。** 仅在实际指定双审通过且 push → PR → CI → merge → 远端复核后方可改变。本审查者**无推送/合并授权，未做任何推送**。

**另需明确**：**fde989ac 从未推送**（PR6 的 remote head 仍是 `58419ec4`），因此**针对本候选的远程 CI 一次都没有跑过**。本报告对三条 CI 失败的"修复正确"结论是**基于源码与机制的独立复核**，**不是"远端已绿"**。新候选推上去后仍须以真实 CI 全绿为准。

### 10.4 建议的下一轮最小动作（不扩大范围、不新增功能）

1. **先修 §8.1 的错误码映射**（`:735` 的 `invalid()` → 专门资源上限错误 + UI 明示"请重启应用"）：成本最低、不触碰任何义务语义、可立刻解除"容量满"与"请求非法"同形的误导。
2. **为 §8.1 的"最后一个存活令牌"设计释放路径**，并补**产品路径级**测试（首次回执丢失 → 点"取回受理" → 断言槽与 holding 终态），使该缺口不再无感回归。
3. **为 §8.2 的 `uncertain` 增加基于原操作证据的复位路径**（不得简单忽略 uncertain）。
4. **为 §8.4 的 UNKNOWN delivery 建立有界回收**，并统一 `deliveries` 与 `#mainlineDeliveries` 的回收责任。
5. **补文档**：准备脚本崩溃残留锁的恢复命令（§8.7）、Git 历史可达性前提（§9#40）、`pretest`/`prebuild` 的 Python 环境前置（§9#42）。
6. **任何改码都会产生新候选** ⇒ package088 / e2e 088 / 三 fault / native / renderer 第 3 次 / fresh002 等证据**不可沿用**到新候选，须重跑对应必要验证。

---

## 11. 本次审查的自我限制与合规披露（如实记录）

- **只读**：未修改任何产品文件、测试、配置、标准或 Git 索引；未运行新的 build / 安装 / GUI / APP / engine / 测试 / 外部请求。**唯一写入为本报告文件**。**如平台发生任何自动额外写入，本人未观察到**；收尾复核对 `git status --porcelain`（唯一 ` M AGENTS.md`）、`git rev-parse HEAD`（`fde989ac…`）、`shasum AGENTS.md`（`de15f6ce…`）与 `git diff --cached`（0 字节），确认产品源/索引/overlay 均未变。
- **未读对方本轮产物**：为创建本方输出目录，本方**执行过一次 `ls -la` 列出本轮目录**，该目录项显示存在 `zcode/` 子目录及若干共享文件（`PROMPT-PINS.json`、`HUMAN-INPUT-SUPPLEMENT.json`、`PACKAGE-UNIT-SUPPLEMENT.json`、`PROMPT-INDEPENDENT-REVIEW.json`、`DISPATCH-CUA-ORIGINAL-TIMELINE.json`、`SUPPLEMENTS-DELIVERY-CONFIRMED.json`、`shared-prefix.txt`）。**本方未打开 `zcode/` 下的任何文件，未读对方任务、报告或其 prompt 内容**；对方 prompt.txt 的 bytes/SHA 仅从 `PROMPT-PINS.json` 的登记读取（32482/32525 字节、清单 11255 B、EOF 恰好一次），与本方 prompt.txt 的独立实测一致。
- **未读写任何记忆**：无 `.zcode`、`.minimax`、项目或用户 memory 的读写。**本轮未调用任何 memory 工具。**
- **子代理**：1 条只读 `explore` lane（2 次任务），仅提取历史文档事实，**两次均成功完成**；其结论不作为本轮判定依据。本轮无 lane 失败、无并发限制事件。
- **N 临时 checkout 非源码 authority**：以 worktree 实测内容为准（1288/1288 逐条重算 + 路径集相等），未采信临时 checkout 的 UNBORN Git 状态。
- **对历史证据只读不改写**：未触碰任何历史证据文件。
- **本报告的推断边界**：§8 各项的"第 N 次即封顶"量化后果与 §4.3 的运行期后果**均未在本轮执行验证**；本轮所有缺陷的**代码路径与缺失的回收/删除点为【观察】**。§5.2 的"先 7 红后 60 绿"**未运行验证**，仅从源码判定机制自洽。
- **两项来源补充与勘误**：renderer 第 2 次输入来源与 package 回执单位勘误均**据实际原件核验后采用**（§1），**不作为指定结论**，也不改写原 UNKNOWN 记录与原 FAIL 记录。
- **与历史报告的分歧不隐藏**：§3.1 明确**不维持** 087-MM §4.1 的 High/阻断定级并给出可复核的排除链；§4 明确**指出上一对两份报告均未定位到的产品入口与"切项目不回收"这一升级点**，并给出该报告未给出的精确机制与计数口径。
- **本报告不新增产品功能建议**，不为满足 11255B 清单扩建任何无关能力；清单的整类不适用判定**是"当前形态不适用"，不是"已具备"**。

---

*报告结束。审查者未修改任何产品文件；本报告为唯一产出。*
