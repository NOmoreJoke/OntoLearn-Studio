# OntoLearn Studio — T01 / 748008a6 / package087 全量独立工程审查报告（MiniMax M3.1-Flash / xhigh / 始终授权）

- **审查方**：MiniMax Code（provider `minimax`，model `MiniMax-M3.1-Flash`，variant `thinking`，effort `xhigh`，`permissionMode: bypassPermissions`）
- **审查日期**：2026-10-24
- **审查类型**：全新独立完整审查（非受理、非计划、非抽样摘要）
- **产品源码状态**：全程只读。未修改任何产品文件、测试、配置、标准、Git 索引；未运行新的 build / 安装 / GUI / APP / engine / 测试 / 外部请求；未读取另一模型本轮任务或本轮报告。**唯一写入物为本报告文件。**
- **历史上下文**：对称读取了上一候选 7d30/package085 的两份**已结束冻结**的历史报告与 `review-opinion-treatment.md`，并对 M1/M2/M3/M4 的处置逐项回到源码独立复核（结论见 §4、§9）。

---

## 0. 结论（先行）

**当前内部演示范围：BLOCK（存在 1 项新增的实现级阻断 + 3 项延续的实现级缺陷）。**
**正式分发 / 跨平台 / 其他门禁：HOLD 保持，一项未关闭。**

1. **【High｜新增缺陷】M4 的退役回调一旦抛错，主链路投递与 IPC 投递租约会永久泄漏，且产品路径没有重试入口。** `apps/desktop/src/main/engine.ts:964-972` 在 `consume()` 内循环执行退役回调，回调抛错即**中断整段清理**——`#mainlineDeliveries.delete(delivery)`（唯一删除点 `engine.ts:978`）、bytes/objects 退款、`#mainlineReceipts.delete`、`#mainlineConsumed.add` **全部不执行**；`apps/desktop/src/main/desktop-ipc.ts:135-141` 因 `consume()` 抛错而 `return permission()`，**跳过 `deliveries.delete(id)`**；`apps/desktop/src/preload/index.ts:36-43` 把该失败**静默吞掉**。新单测 `tests/unit/t01-mainline-reply-lifecycle.test.ts:541-583` 证明的是 `receiver.consume(receipt)` 这一**引擎级**接口可重试释放——但产品路径的 ACK 只发一次且失败被吞，**该重试在生产中不可达**。后果：每次退役失败永久占用 1 个主链路投递槽（上限 16，`engine.ts:771`）与 1 个 IPC 投递槽（上限 16，`desktop-ipc.ts:164`），并永不退还 128MiB/1048576objects 全局预算；累计 16 次后**整个 project/query 面永久 `PERMISSION_DENIED`**。详见 §4.1。
2. **【High｜延续】`uncertain` 单向闩锁仍在**（M1 未修复）：`engine.ts:822/2098/2501/2566` 全部只有 `= true`，全仓无复位。详见 §4.2。
3. **【Medium｜延续】未 ACK 主链路投递永不回收**（M3 未修复）：`desktop-ipc.ts:164` 上限 16 → 16 次后 project/query 面永久拒绝。详见 §4.3。
4. **【Medium｜延续】跨引擎会话后创建/示例的原回执永久不可对账**（M2 按窄范围保留）：`origin` 绑定 `engineSessionId`（`project_lifecycle.py:82-102`），新握手必然 `IDENTITY_CONFLICT`。详见 §4.4。
5. **【Medium｜发布义务】未签名 / 未公证 / 只有目录包**，不可对外分发。详见 §4.5。
6. **【Medium｜本轮新增发现】引擎内 8 个被 import 但不存在的模块**（`ontolearn_engine.quality.*` 与 `semantic_profile_*`，38 处 import 站点）。我独立做完可达性追踪后**下调了子代理给出的 Medium**：这些 import 全部位于 profile 专属分支，而 profile 分支在当前 runtime **不可达**（`reasoning.execute` 的 `implementation` 为 `design-only` 且不在 `v2Runtime`；`execute_profile*` 全仓无调用者）。因此是**死代码悬挂 import**，不是运行期故障，但属必须清理的落地雷。详见 §4.6。

**未发现数据损坏、越权写入、凭据泄露、注入或可利用的鉴权缺陷。** 事务、幂等、隔离、历史不可变、契约驱动等核心不变量在本轮独立复核中全部成立。

**0/17 口径不可改变。** 本审查者无 push/merge 权限，未做任何推送。§4.1 的修复必然改码 → 产生**新候选** → whole087 / package087 / e2e actual002 / real-runtime actual001 证据**不可沿用**到新候选。

**历史状态未被清零。** 086 首败、087 外部 guard 首败（0 产品用例）、C4–C6 失败与 HOLD、D2、损坏 SQLite physical HOLD、`_distutils` 归属、Windows/参考设备、真实 LLM、签名/完整 legal、指定双审积压、CI、develop 合入与完整 release 原门**全部继续留账**。

---

## 1. 回读确认（审查开始前的实际读回，全部由本方实测）

| 项 | 任务书指定 | 本方实测 | 判定 |
| --- | --- | --- | --- |
| prompt.txt 字节数 | 20609 B | `20609` | ✅ |
| prompt.txt SHA256 | `81741afe6c1bd89faea63d3ac3b660378f2d41c53a11ac111fc201c9d318544f` | 完全一致 | ✅ |
| 清单全文 | 11255 B，逐字保留 | 附件第 29 行至 EOF 提取 = `11255` B，SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`，与 `iteration-control/2026-10-21-weekly-release/review-policy-20261024/user-review-checklist.txt` **逐字节相同**（`cmp` 判定 IDENTICAL） | ✅ |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | `pwd` 与 `git rev-parse --show-toplevel` 均一致（Unicode 规范路径逐字符相同） | ✅ |
| Git authority | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `git rev-parse --git-dir` 一致 | ✅ |
| HEAD | `748008a6a15091e8c5376b53a9348002eee7a207` | `git rev-parse HEAD` 一致 | ✅ |
| base / merge-base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git merge-base HEAD <base>` = 同一 SHA；`git cat-file -t` = commit | ✅ |
| 远端 develop（只读 ls-remote） | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git ls-remote origin refs/heads/develop` = 同一 SHA | ✅ |
| 累计范围 | 38 commits / 525 files | `git rev-list --count` = **38**；`git diff --name-only` = **525**；`+561064 / −4638` | ✅ |
| 受保护 owner 规则 AGENTS.md | 15147 B / `de15f6ce…56a5c8c4`，未暂存，勿修改 | 工作区 ` M AGENTS.md`；实测 15147 B / SHA 一致；**全程未修改** | ✅ |
| Git 索引 | 173116 B / `0bd0667b…db7b119e`，cached diff 空 | 索引文件实测 173116 B / SHA 一致；`git diff --cached --quiet` → `CACHED_DIFF_EMPTY` | ✅ |
| 源码闭集 S1270 | 223577 B / `ebf3328e…c252892` | 实测字节与 SHA 一致 | ✅ |
| provider / model / 思考 / 权限 | MiniMax M3.1-Flash / xhigh / 始终授权 | 会话实测 `effective_model=minimax/MiniMax-M3.1-Flash`、`variant=thinking`、`thinking.effort=xhigh`；`~/.minimax/config.yaml` 实测 `permissionMode: bypassPermissions`、`defaultModel: minimax/MiniMax-M3.1-Flash`、`defaultModelVariant: thinking`、`defaultModelThinking.effort: xhigh` | ✅ |
| 分支 | — | `feature/weekly-t01-project-transactions` | — |

**独立闭集复算（本方亲自执行，非引用）**：在 worktree 内对 `S-source-after-commit.json` 的 **1270 条**逐条重算文件字节数与 SHA256 → **1270/1270 一致，0 缺失、0 不符**；再用 `git -c core.quotepath=false ls-tree -r HEAD` 与闭集做路径集比对 → **两侧路径集完全相等**（首轮因默认 quotepath 转义非 ASCII 路径曾显示不等，加 `-c core.quotepath=false` 后确认相等）。唯一内容差异是 `AGENTS.md`：闭集登记的是**未暂存 owner overlay**（15147 B / `de15f6ce…`），HEAD 提交的版本为 1056 B / `1b3c0291…`。**结论：闭集是"工作区状态闭集"而非纯 HEAD 树闭集**——这是 owner 规则刻意不暂存的正常结果，不构成篡改，但引用该闭集时必须说明这一点。

---

## 2. 本轮实际已核 / 未核范围（诚实边界）

### 2.1 已核（本方亲自读取或亲自执行只读复算）

- **仓库与 Git 全量状态**（§1 全部实测项）。
- **HEAD 两个新叶的全部 diff 逐行**：`dd21ab12`（M4 四叶：`engine.ts` +47/−、`project-mainline-service.ts` +166/−、两个单测）与 `748008a6`（仅 `tests/e2e/t02-ontology-mainline.spec.ts` +15/−10）。
- **M4 实现链路逐行**：`engine.ts:296-302/490-504/753-809/835-895/899-1011/1043-1099/1660-1712`、`project-mainline-service.ts:237-300/619-700/700-800`。
- **748008a6 断言强度判定**：前后逐行对比 + 渲染端标记核对（`OntologyMainlinePage.tsx:297/320` 为 `<section aria-label="原操作状态">` / `<section aria-label="已提交回执">`，与 `getByRole('region',{name})` 的可及名称来源等价）。
- **Python 引擎核心**：`project_lifecycle.py`（origin 绑定与创建幂等）、`job_store.py`（`operation_claims` / `_occupied_operation_evidence` / `_accepted_job` / `operation_get` / `commit_job` / `reconcile_jobs`）、`coordinator.py`（worker 启动、session、授权模型）、`storage.py`（`_migrate` / `_transaction` / `collect_cache` / 不可变触发器）、`semantic.py`（`reason()` 分支）、`semantic_execution.py`（`execute_request` vs `execute_profile`）、`semantic_turtle.py`（profile 专属解析器）、`semantic_offline.py`（audit hook）、`memory_guard.py`。
- **Electron 主链路**：`main/index.ts`、`main/engine.ts`、`main/task-service.ts`、`main/desktop-ipc.ts`、`main/project-mainline-service.ts`、`main/query-definition-service.ts`、`preload/index.ts`、`src/csp.ts`、`electron.vite.config.ts`、`electron-builder.yml`。
- **渲染层**：`renderer/src/ontology/**`、`renderer/src/query/**`、`App.tsx`、`task-presentation.ts`，以及 `tests/e2e/**` 与 `tests/unit/**` 变更集。
- **契约面**：`packages/contracts/v2/registry.json`（全量能力表）、`errors.json`（固定错误码 + `paramsSchema`）、`packages/contracts/src/v2.ts`。
- **需求依据**：`docs/prd/PRD-本体学习与落地Agent工作台.md` 的 FR-001…FR-006 / FR-203 / FR-204 / FR-402 / FR-403 / FR-404 / FR-804 / FR-900–902。
- **累计 diff 安全扫描（本人执行）**：`eval`/`new Function`/`exec`/`subprocess`/`spawn`/`os.system`；`dangerouslySetInnerHTML`/`innerHTML`/`document.write`；`execute(f"...")` 拼接 SQL。→ 渲染端 **0 处** `dangerouslySetInnerHTML`；引擎 src **0 处** 网络 import（socket/urllib/requests/httpx/http.client）；引擎唯一 `subprocess.Popen` 在 `storage_probe.py`（测量夹具，非协议可达），产品 worker 用 `asyncio.create_subprocess_exec` 且 argv 完全固定（`worker.py:85-99`）。
- **证据面**：whole087 `ENTRY.json`/`check-full-087.log`/`check-full-087-receipt.json`/`BUILD-NONCE-DIFF.json`/`actual-five-JS.json`；package087 `.app` 实物目录；root 受理票；e2e actual002 `ENTRY.json`/`frozen-original/test.stdout.raw`；real-runtime actual001 `ACTUAL-RUNTIME-RESULTS.json`/`frozen-original/coordinator-exit/actual-native.json`；086 失败 `trace.zip`；`TRACE-REFERENCE-CORRECTION.json`；`INDEPENDENT-POSTPATCH-REVIEW.json`；087 guard 首败 `actual_001/ENTRY.json`；runner adapter `CORRECTION.json` 与 `ALL-GLOBAL-BINDING-READBACK.json`。

### 2.2 未核 / 无法确认（如实记录，不以静态检查代替运行证据）

- **本轮未运行任何测试、构建、引擎、GUI 或网络**。所有"绿"均指对**既有证据的独立复核**，不构成新的运行证据。
- Windows 打包与运行、Linux 参考设备、五龄老设备实测；Linux-only 两条 e2e 在 Linux 上的真实行为。
- 损坏 SQLite 的 physical HOLD、`_distutils` 归属、D2 规模/负载口径、真实 LLM（I06 网关未接入）。
- 签名 / 公证 / 安装 / 无开发环境设备离线启动。
- 可访问性合规（对比度、真实屏幕阅读器）、RTL 排版、emoji/口音的渲染细节。
- `packages/contracts/v2/fixtures.json` 与 `binding-regressions.json` 的**内容**风险（随包分发，但未逐字审其是否含业务数据）。
- `docs/reviews` 下 307 个过程文档仅做台账抽样，未逐字通读。
- Python 侧第三方依赖（rdflib 7.6.0 / pyparsing 3.3.3 / pyshacl 0.30.1 等）在本机锁定树中的实际漏洞状态（本次无网络，未做 advisory 核验）。
- **子代理使用与自我限制**：本轮派出 4 条只读审查 lane（Python 引擎 / Electron 主进程 / 渲染层 / 证据面）。前三条返回完整结论；证据面 lane 长时间无产出后**由我终止**，其全部范围（§6 证据表）改由我在主会话**逐项亲自复算**。对前三条 lane 的每一条 High/Medium，**我均回到源码逐行复验并独立定级**（其中 1 条我**下调**了严重度，见 §4.6；1 条我**新增**了缺陷，见 §4.1）。

---

## 3. 累计范围与架构事实（本轮独立复算）

### 3.1 38 commits / 525 files 分布

| 区域 | 文件数 | 说明 |
| --- | --- | --- |
| `docs/reviews` | 307 | 过程证据文档，非产品代码 |
| `packages/engine` | 66 | Python 引擎 + 引擎测试 |
| `docs/iterations` | 38 | 迭代设计/验收文档 |
| `apps/desktop` | 35 | 主进程 / preload / 渲染层 / CSP / 打包配置 |
| `tests/unit` | 22 | TS 单测 |
| `tests/e2e` | 12 | Playwright 真实 Electron e2e |
| `licenses/*` | 29 | 分发许可闭包 |
| `packages/contracts` | 8 | 契约 schema / registry / fixtures |
| 其他 | 8 | `pyproject.toml`、`package.json`、`uv.lock`、构建脚本 |

产品代码净增约 561k 行，其中绝大部分是契约 fixture（`fixtures.json` 21 185 行、`binding-regressions.json` 12 330 行、`schema.json` 6 939 行）与文档。

### 3.2 核心不变量复核结果

| 不变量 | 本方独立判定 | 依据 |
| --- | --- | --- |
| 正式写入只经版本化提交路径 | **成立** | `Store.commit`（`storage.py:456-893`）是 `definitions`/`facts`/`mapping_state`/`versions`/`definition_retirements` 的唯一写者；创建/示例/应用三个分支均从 `Store.commit` 内部派发且互斥（`:482-541`）；每个提交都做 base 版本 CAS（`:638-643` → `REVISION_CONFLICT`）、版本递增、不可变 `commits` 标记与前后快照、不可变 `commit_evidence`，**同一 SQLite 事务**（`:630`） |
| RDF 图只从不可变快照重建 | **成立** | `rdf_snapshot.graph_from_snapshot`（`:51-66`）每次新建 `Graph()`，托管墓碑排除；`grep '_db.execute' semantic*.py` **无输出**，语义层零 SQL |
| 历史与已提交轮次不可改写 | **成立** | SQL 层触发器强制：`storage.py:1789-1795`（snapshots/commits/runs/rounds/run_terminal）、`:216-220`（commit_evidence）、`format3.py:108-124`、`job_store.py:2506-2531`（job 族 + `operation_claims` + `job_plans` + `job_confirmations` + `job_results` + `job_reports` + `job_details` + `job_context`）。补偿是**追加新提交**，不改旧标记 |
| 幂等与不重放 | **成立** | 三层键：`operation_claims.operation`（PK）、`commits(project,operation)`、`rounds.operation` UNIQUE。`job.create` 重放走 `job_store.py:1054-1060 → _accepted_job:1197-1266`，逐项复验冻结上下文摘要与调用方绑定；`_occupied_operation_evidence`（`:419-427`）拒绝跨项目/跨轮次采纳 |
| 失效规则唯一来源 | **成立** | `invalidation.py:19-28` 仅从 `invalidation-v2.json` 取 `staleReason`；`model` 与 `implementationCompatibility` 的 `staleReason` 为 `null` ⇒ **仅改模型配置不使领域结果过期**；`publicationPolicy.lateResult = preserve_as_historical`；失败/取消/历史是**生命周期状态**，不是过期原因 |
| 渲染端隔离 | **成立** | `window-security.ts:3-15`：`contextIsolation:true`、`nodeIntegration:false`、`sandbox:true`、`webviewTag:false`、`webSecurity:true`、`allowRunningInsecureContent:false`；`app.enableSandbox()`；preload 仅 `contextBridge.exposeInMainWorld('ontolearn', bridge)` 一个键、27 个**业务命名**方法，**无 `invoke(method, params)` 通用通道**；全部 28 个 IPC 处理器经 `register()`（`desktop-ipc.ts:153-184`）且首句即 `trusted(event)` |
| CSP 唯一来源 | **成立** | `csp.ts:2-26` 是唯一策略定义；生产变体**无** `unsafe-inline`/`unsafe-eval`（`unsafe-inline` 仅在 `if (development)` 分支的 `style-src`）；生产 `connect-src/object-src/base-uri/frame-src/form-action` 均 `'none'`；全仓无第二/第三份手写策略 |
| 跨边界只传固定错误码 | **成立** | `errors.json` 每码 `paramsSchema` 且 `additionalProperties:false`；`project-mainline-service.ts:413-425` 与 `query-definition-service.ts:333-357` 把非白名单错误一律降级为 `INTERNAL_ERROR`；引擎 stderr 不转发（`engine.ts:2246-2251`） |
| 不自动启用模型/遥测/云 | **成立** | 全仓无模型客户端、无遥测、无 HTTP 监听（唯一 HTTP 是 e2e 的**测试**探针与 Vite 开发服务器）；引擎 env 白名单只透传 `HOME/TMPDIR/TMP/TEMP/LANG/LC_ALL/LC_CTYPE/TZ`（+Windows 路径变量），**不继承** `PATH`/`PYTHONPATH`/代理/凭据 |
| 引擎不持密钥、只经 stdio | **成立** | `spawn(command, args, { shell:false })`，命令为绝对路径；`semantic_offline.py:24-32` 在语义作用域内以 `sys.addaudithook` 阻断 `socket.*`/`urllib.Request`/`subprocess.Popen`/`os.system`/`os.posix_spawn` |

---

## 4. 最值得修复的 10 项（按严重程度排序）

> **【观察】** = 我在源码/产物中直接读到或亲自复算到的事实。
> **【推断】** = 由观察推导的运行期后果（本轮未执行验证）。

---

### 4.1 【High｜新增缺陷】M4 退役回调抛错会永久泄漏主链路投递与 IPC 租约，产品路径无重试入口

**位置**
- `apps/desktop/src/main/engine.ts:946-981`（`consume()` 全段）
- `apps/desktop/src/main/engine.ts:964-972`（退役循环 + `finally { delivery.consuming = false }`）
- `apps/desktop/src/main/engine.ts:978`（**唯一**的 `#mainlineDeliveries.delete(delivery)`）
- `apps/desktop/src/main/engine.ts:771`（`if (this.#mainlineDeliveries.size >= 16 …) throw invalidStateOrdinary()`）
- `apps/desktop/src/main/engine.ts:1059-1079`（`onReplyConsumed`）
- `apps/desktop/src/main/project-mainline-service.ts:644-670`（`#offerIntent` 的退役回调，3 个抛错条件）
- `apps/desktop/src/main/desktop-ipc.ts:135-141`（`try { replies.consume(...) } catch { return permission() }`，随后 `deliveries.delete(id)`）
- `apps/desktop/src/main/desktop-ipc.ts:164`（`if (deliveries.size >= 16) return permission()`）
- `apps/desktop/src/preload/index.ts:28-45`（ACK 单次发送 + `catch {}` 静默吞掉）
- `apps/desktop/src/main/engine.ts:2090-2091`（引擎退出只把投递标 UNKNOWN，**不删除、不退款**）

**【观察】1**：M4 在 `delivery.consumptions` 中登记退役回调，`consume()` 在 `engine.ts:966-969` 逐个执行：
```js
for (const [entry, retire] of delivery.consumptions) { retire(); delivery.consumptions.delete(entry) }
```
回调抛错 ⇒ 循环中断 ⇒ `engine.ts:973-980` 的**退款（bytes/objects）、`aliases.length = 0`、`wires.clear()`、`records.clear()`、`#mainlineDeliveries.delete`、`#mainlineReceipts.delete`、`#mainlineConsumed.add` 全部不执行**。`finally` 只把 `delivery.consuming` 复位为 `false`。

**【观察】2**：`#mainlineDeliveries.delete(...)` 在整个仓库**只有 `engine.ts:978` 一处**。因此一次中断即让该投递**永久驻留**在 `#mainlineDeliveries` 中：占用 1/16 的投递槽，其 bytes/objects 永不退还给 128MiB/1048576objects 全局预算。`#finish`（引擎退出）只调用 `#unknownDelivery`（`:2090-2091`）把状态置 UNKNOWN，**同样不删除、不退款**。

**【观察】3**：退役回调 `project-mainline-service.ts:644-670` 有 3 个抛错条件：`!intent.pendingReplies.has(pending)`、`intent.active !== 0 || intent.unknown || !intent.accepted`、以及 `intent.budget.releaseHolding(...)` 抛错（失败时恢复 `intent.accepted` 并向上抛）。

**【观察】4**：IPC 层 `desktop-ipc.ts:135-141`：
```js
if (pending) {
  try { replies.consume(pending.receipt) } catch { return permission() }
  deliveries.delete(id)
  …
}
```
⇒ `consume()` 抛错 ⇒ **`deliveries.delete(id)` 被跳过** ⇒ IPC 投递槽（上限 16）也永久占用。

**【观察】5**：preload `index.ts:36-43` 对 ACK 结果只做一次校验，失败即 `throw new Error('delivery acknowledgment rejected')`，随即被外层 `catch {}` **静默吞掉**，并 `return delivery.data.payload`（渲染端**照样拿到正确结果**）。**没有任何重发 ACK 的逻辑。**

**【观察】6**：新单测 `tests/unit/t01-mainline-reply-lifecycle.test.ts:541-583`（`keeps the exact receipt after partial cache cleanup failure without double refund`）确实覆盖了"释放失败后重试可释放"：它先断言 `consume(offered.receipt)` 抛出 `cleanup remains owned`、`deliveryBytes` 未变、`offered` 仍为 1；随后把 `fail = false` 并**再次直接调用 `s.receiver.consume(offered.receipt)`**，断言 `slots` 归 0。**该重试调用的是引擎级 `receiver.consume()`，绕过了 IPC 层。** 产品路径中 ACK 只发一次且失败被吞 ⇒ **该恢复路径在生产中不可达**。

**【推断】触发/反例**：任何使退役回调抛错的时序（同一 operationId 的并发提交使 `intent.active !== 0`；`releaseHolding` 因会话/持有记录变化而失败；`pendingReplies` 状态异常）⇒ 一次泄漏。累积 **16 次**后：
- `engine.ts:771` 使**所有**新的主链路投递被拒 ⇒ `project:*`/`query:*` 全部 `PERMISSION_DENIED`；
- `desktop-ipc.ts:164` 同口径使 IPC 投递面同样封顶；
- 全局 128MiB/1048576objects 预算被已死投递**永久占用**，且 `#retainHolding` 的 `maximum` 计算（`engine.ts:853-857`）随之收缩，可能在远早于 16 次时就使新的持有申请失败。
- 用户侧**无任何可见错误**：渲染端收到的是**正确结果**，只有主进程静默泄漏。

**风险**：可用性中断（整条主链路永久失效）+ 资源预算永久性收缩；无数据损坏（引擎侧 `operation_claims` 仍兜底不变量）。

**严重度**：**High**。这是本轮 M4 修复**自身失败模式未被容器化**的直接后果，且 M4 的设计目标之一正是"释放失败留原 receipt/holding"——但实现只保证了"保留"，没有保证"保留后可被释放"。

**建议**（不要求扩大协议面）：
1. 把退役回调的失败与**投递生命周期解耦**：退役失败只标记该 entry（`delivery.consumptions` 保留 + 记录 `retireFailed`），**不中断** `consume()` 的其余清理（退款/清别名/删除投递/标记已消费）。这样"保留 receipt"语义不变，但**不留投递壳**。
2. 或：IPC 层在 `consume()` 抛错时**仍删除 `deliveries` 槽**并把 delivery 转入一个"待释放"集合，由后续成功 ACK 或会话结束统一回收，而不是永久占用 16 槽。
3. 补一条**产品路径级**测试（而非仅引擎级）：模拟退役失败 → 断言投递槽与 IPC 槽均被回收 → 断言第 17 次主链路调用仍可用。
4. 明确并记录：`#mainlineDeliveries` 与 `deliveries` 的回收责任必须**唯一且可达**，否则 16 这个上限实际是"泄漏计数"而非"并发计数"。

---

### 4.2 【High｜延续缺陷，M1 未修复】`uncertain` 是单向闩锁，一次主链路故障即永久毒化主链路 IPC

**位置**：`engine.ts:276`（声明）、`:714`（`#mainlineReady` 判定并 `throw deniedOrdinary()`）、`:822`（UNKNOWN 投递全量置位）、`:957`（消费判定）、`:2098`（引擎死亡）、`:2501`、`:2566`；`:1119-1124`（`mainlineProjectClient()` 复用同一 record）。

**【观察】** 本轮我对 `engine.ts` 全文件穷举 `uncertain` 赋值：**只有 `= true`，无 `= false`、无删除、无复位路径**。置位条件覆盖：主链路请求超时、stdin 写失败、引擎死亡时仍有主链路在途、UNKNOWN 投递。

**【推断】触发**：引擎已提交但 JSONL 回复行丢失 → 桌面端 5s 请求超时（`requestMs=5000`）→ `record.uncertain = true` → Session 因心跳存活而不重启 → 此后**全部** `project:*`/`query:*` 永久 `PERMISSION_DENIED`。

**风险**：可用性中断 + 本会话内原操作对账能力不可达。**无数据损坏、无重复写入**——引擎侧 `operation_claims` 兜住不变量。

**严重度**：High。

**关于 owner 处置的独立复核**：`review-opinion-treatment.md` M1 条目称"部分采纳，缩小影响范围"——**我核实的结论是：M1 的核心（单向闩锁）并未修复**，"缩小影响范围"指的是原报告"整个 App 永久不可用"的表述被修正为"仅主 project/query 受拒"，并指出 `TaskService` 325–435 的恢复路径与 1363–1472 的只读恢复通道仍可用。该表述与代码一致（`engine.ts:1124-1129` 确实创建新 owner），**但闩锁本身仍只置位不复位**。此处的处置是**表述修正**而非缺陷修复——不应被读作 M1 已闭合。

**建议**：为 `uncertain` 增加**基于原操作证据**的复位路径（例如同一 `operationId` 成功对账取回原回执后清除该 record 的闩锁），或在 `#mainlineReady` 改为"不确定态下允许只读/对账类调用"。**不要**简单放宽为"忽略 uncertain"——那会恢复自动重放已输入写入的风险。

---

### 4.3 【Medium｜延续缺陷，M3 未修复】未 ACK 主链路投递永不回收，16 次后主链路永久拒绝

**位置**：`desktop-ipc.ts:105-113`（`deliveries` Map）、`:142`（**唯一** `deliveries.delete`，位于精确 ACK 路径）、`:164`（`if (deliveries.size >= 16) return permission()`）、`:176-181`（投递写入）；`preload/index.ts:40-42`（5s ACK 超时被吞）。设计注释见 `desktop-ipc.ts:103-104`："No timeout, navigation or new session deletes an unacknowledged receipt"。

**【观察】** `deliveries` **只**在 ACK 路径删除，无过期、无驱逐、无容量回收；**同一函数内**的 `accepted` Map **有** FIFO 驱逐（`:144`）——对照证明这是有意的不对称。

**【推断】触发**：渲染进程崩溃/重载/导航发生在主进程回复与 preload ACK 之间 → 槽位永久占用。累计 16 次 ⇒ 全部 `project:*`/`query:*` 永久 `PERMISSION_DENIED`，**只能重启应用**。

**风险**：可用性中断（应用被砖）。

**严重度**：Medium。

**关于 owner 处置的独立复核**：treatment 文档 M3 称"部分采纳可达耗尽事实，不采纳 FIFO 修复"——我核实：代码未变（`:142` 仍是唯一删除点），M3 的事实陈述（可达耗尽）**成立**，但**"可达耗尽"是事实陈述而非缓解**。需要注意的是：M3 与本轮 §4.1 的退役失败泄漏**共用同一个 16 槽上限**，二者叠加会更快触发封顶。

**建议**：为 `deliveries` 增加与 `accepted` 对称的**有界驱逐**，或按 `sender`/`frame` 销毁事件（`WebContents` 的 `destroyed`）释放。释放租约仍须以"精确 ACK"为**授权**依据，驱逐只回收**容量**，不得让未确认投递变成"已投递"。

---

### 4.4 【Medium｜延续，M2 按窄范围保留】跨引擎会话后创建/示例的原回执永久不可对账

**位置**：`packages/engine/src/ontolearn_engine/project/project_lifecycle.py:82-102`（`origin_value`：`{hostClientId, engineSessionId, permission}`，后两者必须是 36 位 UUID 且 `permission == "library.create"`）、`:465-470`（空白项目创建认领比对）、`:1027-1031`（示例创建认领比对）；`apps/desktop/src/main/engine.ts:2220` 附近（每次握手新发 `clientId`）。

**【观察】** `origin` 强制包含 `hostClientId` 与 `engineSessionId`，二者**逐会话/逐握手更换**。认领命中时要求 `old["context"]["origin"] == origin`，否则 `"identity"` 故障（`project_lifecycle.py:466-468`）。我同时确认 `origin_value` 要求 `engineSessionId` 为 36 位 UUID ⇒ **新会话必然不同** ⇒ 必然 `IDENTITY_CONFLICT`，原回执不可取回。

**【推断】触发**：引擎在已持久化提交之后、回执抵达渲染端之前崩溃 → 用户以同一 `operationId` 重试 → `IDENTITY_CONFLICT` 而非"取回原回执"。渲染端保留原 `operationId`（`App.tsx` 的 `createIntent` ref）。

**风险**：**不会**产生重复项目/草稿（守卫有效），主链路也**不会**被砖；但**原回执永久不可取回**，UI 停留在"创建结果尚未确认"。与 §4.2 复合后（引擎死亡 → 既 poisoned 又 identity-mismatch），引擎侧对账在最需要时不可达。

**严重度**：Medium。

**关于 owner 处置的独立复核**：treatment 文档 M2 称"不采纳全局 High 结论，保留创建专属限制"——我核实：`job_store.py:1398-1413` 的 `operation_get` 确实按**当前许可 P/op** 读 marker，且恢复白名单含 `job.get`/`operation.get`，故"所有 Job/marker 都不可对账"的全局化结论**不成立**（该部分我认同）。但"创建/示例专属"这一限制**客观存在且未修复**，仍应按 Medium 记留，而非按"已处理"清零。

**建议**：把"操作身份"与"会话身份"解耦——认领比对基于**稳定的请求指纹**（业务语义 + 目标项目 + 输入摘要），会话信息仅作审计元数据。

---

### 4.5 【Medium｜发布义务】打包产物无签名、无公证、无可分发目标

**位置**：`apps/desktop/electron-builder.yml:24`（`mac.identity: null`）、`:25/27/29`（`mac/win/linux` 均 `target: dir`）；`package087` 实物目录 `outputs/20261024_t11_package087_actual_001/frozen-artifacts/release/mac-arm64/OntoLearn Studio.app`。

**【观察】** 本方对 package087 实物目录实测（标准库 `os.walk`）：
- `.app` 合计 **549 个文件 + 361 个目录 = 910 条目**（与 root 受理票的 "completeAPP910" 精确吻合）；
- `Contents/Resources` 下 **290 个常规文件**（与 "Resources290 regular" 吻合）；
- `Contents/Resources/engine` 下 **225 个文件 + 41 个目录 = 266 条目**（与 "engine266" 吻合）；
- `Contents/Resources/app.asar` 存在，19 014 603 B，ASAR 头解析出 **819 个文件成员**；
- `mac.identity: null` + `target: dir` ⇒ **无签名、无公证、无 .dmg/.pkg 安装产物**。

**【观察】** 该包确实**未签名**（`identity: null`，且 `target: dir` 不产出可分发安装件）。这与 `package-readback.json` 中 `allNativeSignaturesVerify=false`、`appDeepCodesign.exit=1` 的历史记录一致。

**风险**：在他人 Mac 上会被 Gatekeeper 拦截/降信。**属既定发布义务**（decision D5 明示本轮不签），不是代码缺陷，但对"对外分发"是硬阻断。

**严重度**：Medium（对内部演示无影响；对外部分发是硬阻断）。

**建议**：设定 `mac.identity`（Developer ID）、开启 `notarize`、改用 `dmg`/`pkg` 目标。**该改动必然改变产物字节 ⇒ 必须重新出包并重跑打包态 E2E。**

---

### 4.6 【Low–Medium｜本轮新增发现】引擎内 8 个被 import 但不存在的模块（死代码悬挂 import）

**位置**：`packages/engine/src/ontolearn_engine/semantic.py`（import 站点 433, 666-667, 689, 730-731, 830, 848, 871-873, 946-954, 957, 1217-1219, 1239, 1254）、`semantic_execution.py`（574-578, 697, 700-701, 761, 917-918）、`semantic_turtle.py`（237, 372, 675, 714, 765）。
缺失目标：`ontolearn_engine.quality.{rule_calendar,rule_firing,rule_numbers,rule_profile,rule_terms}` 与 `ontolearn_engine.semantic_profile_{directsteps,input,production}`。

**【观察】1**：本方以 `git ls-files packages/engine/src` 列举 tracked 模块——**无 `quality/` 目录、无 `semantic_profile_*` 文件**；`packages/engine/src/ontolearn_engine/` 实测同样不存在。

**【观察】2（可达性独立追踪）**：这些 import 全部位于 **profile 专属分支**：
- `semantic.reason()`（`semantic.py:1247-1258`）仅在 `profile is not None` 时才 `from ontolearn_engine.quality.rule_profile import PROFILE`（`:1254`）；`profile is None` 走 `_legacy_reason`（`:1253`）。
- 产品接线 `semantic_execution.py:461` 调 `semantic.reason(facts + ontology, rules)` —— **不带 profile** ⇒ 走 legacy 分支。
- `semantic.reason(..., profile=PROFILE, ...)` 只出现在 `semantic_execution.py:759`，位于 `_execute_profile`（`:678`）内。
- `execute_profile` / `execute_profile_records` / `_execute_profile_production`（`:874/:896/:915`）**全仓无调用者**（我已在 `packages/engine/src`、`packages/contracts`、`apps/` 三处穷举）。
- `semantic_turtle.py` 的 5 处 import 位于 `_term_input`（`:236`）、`_value_fields`（`:371`）、`_profile_source`（`:674`）、`parse_profile_graph`（`:692`）、`_profile_record_node`（`:764`）—— 我逐个追踪其调用者，全部收敛到 profile 专属类/函数（`ProfileTermContext`、`_ProfileSink`、`profile_context_for_graph`、`profile_graph_from_records`、`bind_profile_disabled_rules`、`decode_profile_term`）。

**【观察】3**：能力表中 `reasoning.execute` 的 `implementation` 为 **`design-only`**，且不在 `registry.json` 的 `v2Runtime`（19 个方法）清单内；`coordinator.py` 无 reasoning 派发。

**【推断】结论**：当前 **profile 路径不可达 ⇒ 运行期不是故障**。真实风险是**落地雷**：若将来接线 `execute_profile`，`ImportError` 会被 `semantic_execution.py:863-871` 的 `except Exception` 吞掉，降级为 `PROFILE_EXECUTION_FAILED`/`INTERNAL_ERROR`——一个**静默降级**，而不是确定性的"能力不支持"拒绝。

**严重度**：**Low–Medium**（我**下调**了子代理初判的 Medium，理由是可达性已被完整排除；维持非 Info 的理由是它一旦被接线就是静默错误而非显式拒绝）。

**建议**：删除这些悬挂 import 与 profile 死分支，或以固定的"能力不支持"错误码显式封门（对齐 `errors.json` 的 `UNSUPPORTED_CONSTRUCT` 口径），使未来调用得到确定性拒绝而不是被吞掉的 `ImportError`。

---

### 4.7 【Medium】无用户级备份/恢复入口；损坏 SQLite 物理 HOLD 未关闭

**位置**：`packages/engine/src/ontolearn_engine/storage.py:95-101`（legacy 损坏 kind 显式拒绝，注 "explicit repair required"）、`:148-168`（v2→v3 迁移备份）、`format3.py:158-187`（`migration_backup`：目标必须不存在、`PRAGMA integrity_check == ok`、源逻辑哈希在备份后**复查**）；数据文件为单文件 `userData/engine.sqlite`（`main/index.ts:256` 附近）。

**【观察】** 迁移备份是**强制且可验证**的（目标新路径 + integrity_check + 源变更即 abort），这是好的一面。**但**：没有应用内项目导出/备份/恢复入口；没有面向用户的"从备份恢复"流程；损坏库的唯一路径是拒绝启动并要求手工文件级操作。

**【推断】风险**：磁盘故障或误删整库 ⇒ 用户数据不可自救。**完整性方向的设计是强的**（原子提交 + 不可变证据 + 快照），风险集中在**可用性/数据所有权**。

**严重度**：Medium。

**建议**：项目级导出/备份入口（可复用快照机制）+ README/应用内说明数据目录与备份位置。注意 §4.9 所述：PRD **FR-002** 明确要求"系统必须支持新建、打开、复制、重命名、归档和**导出项目**"，**FR-203** 要求附录 C 范围内 Turtle 的导入与导出——当前**本体/项目级导出未见实现**，这已不只是"增强项"而是 P0 条款缺口。

---

### 4.8 【Medium｜发布前置】跨平台 / 参考设备 / 规模口径（D2）未实测

**【观察】** 本轮实测仅 macOS 15 arm64；e2e 的 2 条跳过是**真实平台条件**（`tests/e2e/i04-jobs.spec.ts:100-103` 要求 `process.platform === 'linux'` 且需 fixture；`:318-321` 另需 `I04_NATIVE_ISOLATED=1` + openbox/xdotool）——我已回源码逐行确认**不是隐藏失败**。Windows 打包与运行、参考老设备、容量/负载基线均未执行。

**【推断】风险**：不得以"243 行 E2E"充当负载测试；本报告的所有规模判断均不外推。

**严重度**：Medium（发布前置，非代码缺陷）。

---

### 4.9 【Medium｜功能完整性】T02 无独立 redo；撤销仅能作用于当前回执

**位置**：`apps/desktop/src/renderer/src/ontology/mainline-session.ts:382-390`（`prepareUndo()` 无参，固定取**当前回执**的 operationId）、`OntologyMainlinePage.tsx:330-333`（唯一入口"预览撤销本次修改"）；引擎侧 `packages/engine/src/ontolearn_engine/project/transactions.py:253-283`（`preview_undo` 可作用于任何有证据操作，含 undo 自身）。

**【观察】** 撤销是**服务端补偿性新事务**（`intent='undo'` + 全新 base 读取），不是本地反向 diff；冲突面逐资源比对并抛 `UNDO_CONFLICT`。但 UI 无操作历史选择器 ⇒ **连续误操作只能逐次撤销**，且 e2e 用例名写 "Undo/Redo" 而实际第二次操作是**再撤销一次**。

**风险**：功能完整性缺口。**注意**：PRD **FR-804** 只要求"撤销本次 ChangeSet"并要求"如与后续编辑冲突，必须说明影响并暂停"——**未要求独立 redo**。因此这是**功能缺口而非规格违背**；对照 §6 清单中"undo"一项已满足。

**严重度**：Medium。

---

### 4.10 【Low–Medium｜工程卫生，4 处合并】开发 nonce 编译进生产产物；~2 MB 测试夹具随包分发；工作区通配依赖；超大文件

**【观察】1（且是本轮证据链的直接成因）**：`apps/desktop/electron.vite.config.ts:7`
```js
const devNonce = randomBytes(18).toString('base64')
```
在**模块顶层**生成，且 `:11` 用 `define` 注入 **main** bundle，**对所有构建生效**（无 `command` 判断）⇒ 该 24 字符 base64 字面量**随生产产物出厂**。生产不可达（`index.ts:200` 仅当 `devURL` 存在时注入开发头；打包态 `app.isPackaged` 使 `devURL` 为 undefined），所以**无生产影响**；但它使**每次构建的 main bundle 字节都不同**，正是 `BUILD-NONCE-DIFF.json` 必须逐字解释"仅一处 24 ASCII 字面量差异"的原因。我实测该记录：`oldMain.sha256=847fa7e5…` vs `newMain.sha256=83d82b19…`，`allOtherMainBytesEqual=true`、`remainingFourOutputsEqual=true`、`soleDifference` 描述与 `electron.vite.config.ts:7` 一致——**该披露是诚实且可核的**。熵本身充足（18 字节 CSPRNG = 144 bit）。
**严重度**：Low（无生产影响），但建议改为**运行时**在主进程生成开发 nonce，消除构建不可复现性。

**【观察】2**：`electron-builder.yml:11-12` 整体拷贝 `packages/contracts/v2`（2.3 MB），其中 `fixtures.json` 1.4 MB、`binding-regressions.json` 608 KB、`frame-fixtures.json` 17 KB 是**测试语料**；运行时实际只需要 `registry.json`/`schema.json`/`errors.json`/`states.json`/`dependencies.json`（`engine.ts:2156-2160` 只读 `registry.json`）。同一目录还被 `scripts/build-engine.mjs:69` 重复打进 PyInstaller bundle。
**严重度**：Low（我**未**审其内容是否含业务数据 ⇒ 该子项记为**无法确认**）。

**【观察】3**：`apps/desktop/package.json:15` `"@ontolearn/contracts": "*"` —— 违反仓库自身"JS 直接依赖写精确版本"约定（AGENTS.md §7）。workspace 链接故无 registry 供应链暴露，但允许静默漂移。**严重度**：Low。

**【观察】4**：`job_store.py` 2589 行、`engine.ts` 2623 行、`semantic.py` 1627 行、`workspace-controller.ts` 1531 行——多项已超"2000 行"清单线。**严重度**：Low（可维护性）。

---

### 4.11 其余已记录但未进前 10 的问题（全部保留）

| # | 严重度 | 问题 | 位置（均为本方/子代理源码实读） |
| --- | --- | --- | --- |
| 11 | Low | **本体事实/定义表是"整表传输 + 渲染层切片"**，非服务端分页；`MainlineProjectReadDTO.domain.state.facts` 无分页字段，一次 IPC 传全部事实 | `OntologyMainlinePage.tsx:48-54,175`；`OntologyPage.tsx:108-115,247`；`api002-source-types.ts:398-404` |
| 12 | Medium | **两处 Turtle 直连 `SinkParser` 未做字节上限**（`text.encode("utf-8")` 的长度被丢弃），绕过 `_parse_turtle` 的 1 MiB 限制；`_utf8_bound` 辅助函数已存在但这两处未用 | `semantic_scopes.py:125-129`；`semantic_execution.py:279-283`；对照 `semantic_turtle.py:121-133` |
| 13 | Low | **Darwin 内存护栏仅为咨询式**：仅 10 ms RSS 采样，`native_hard_limit=False`（`RLIMIT_AS` 仅 Linux、Job Object 仅 Windows）；模块 docstring 已如实声明 | `memory_guard.py:1-8,164-169` |
| 14 | Low | **退出码 75（`MEMORY_GUARD_EXIT`，"护栏不可用"）未被区分**，一律报为 `ENGINE_EXITED`，与真实崩溃不可区分（仅 74 映射 `RESOURCE_LIMIT`） | `coordinator.py:788-789` vs `:790-791`、`:901-902`；`memory_guard.py:17-18` |
| 15 | Low | 内存护栏在**首帧解码之后**才安装（帧大小已有界，属纵深防御缺口） | `worker.py:214-215`；`protocol.py:6,28` |
| 16 | Low | `CREATE TABLE IF NOT EXISTS definition_retirements` 在**写事务内**、每次含删除的提交都执行（DDL 取 schema 锁） | `storage.py:704,922` |
| 17 | Low | `project/workspace.py` **仅被测试引用，无任何生产模块 import**；docstring 自述持久化"pending"，易被未来 UI 误当持久草稿 | `workspace.py:1-6`；`mainline.py` 有独立 `app_drafts` 持久草稿路径（`format3.py:52-60`、`draft_plan.py:117-177`） |
| 18 | Medium | **撤销影响面板用渲染层投影计算**（`entityDeletionImpact(projection, iri)`）而非引擎影响文档；具误导权威性（不参与提交路径），且与权威 `undo-impact` 文档并存 | `OntologyMainlinePage.tsx:129-136`；`mainline-ontology.ts:262-274`；对照 `mainline-api.ts:91` |
| 19 | Low | **查询历史列表用新页替换旧页**（非累积），且只有"下一页"无"上一页"，早先页从列表消失 | `workspace-controller.ts:1289`；`QueryWorkspacePage.tsx:652-657` |
| 20 | Low | **CSV 公式注入防护在当前数据形态下不可触发**（护栏作用于 N3 串，真实单元格以 `"` 或 `<` 开头）；无害但写法具误导性；且导出**无显式字节上限** | `typed-results.ts:252-272`（护栏 260-261，导出 259/267） |
| 21 | Medium | **`workspace-controller.ts:536` 的 `finally { this.set({ busy:false }) }` 无条件清 busy**，即使 `view !== this.view`（动作已被围栏），可短暂在写操作在途时重新启用按钮 | `workspace-controller.ts:527,536` |
| 22 | Low–Med | `App.tsx:45` 的 `queryControllers` Map **从不清理**，每个打开过的项目都永久保留其 controller/历史 jobs/冲突表 | `App.tsx:45,92-96` |
| 23 | Medium | **工作区/项目切换无焦点管理、无区域播报**，键盘与读屏用户无"上下文已切换"线索 | `App.tsx:156-170` |
| 24 | Low | `App.tsx:514,525` 对 `<a href>` 置 `aria-disabled` 但仍可聚焦且仍带 `onClick`；`App.tsx:504` 无条件 `aria-current="page"` | `App.tsx:504,514,525` |
| 25 | Low | `task-presentation.ts:78,84,111` 对缺失/非数值参数直接 `Number(...)` 插值，可渲染"建议等待 **NaN** 毫秒" | `task-presentation.ts:78,84,111` |
| 26 | Low | `mainline-session.ts:328-334` 用户主动 `read()` 若在 capture 与微任务之间序列号变化则**被静默丢弃**（调用方得到已 resolve 的 Promise，无反馈）；`:430-432` `#prepare` 失败同样可能不产生任何用户可见错误 | `mainline-session.ts:328-334,430-432` |
| 27 | Low | 渲染层**无 `AbortController`/请求取消**，陈旧响应只靠计数器抑制，底层 IPC/引擎工作仍跑到完成 | 渲染层全局 grep 无匹配 |
| 28 | Low | e2e 的 `mkdtemp` profile 目录**从不删除**，每次运行在系统临时目录留下完整 Electron profile + `engine.sqlite` + 备份 | `tests/e2e/isolated-desktop.ts:13` |
| 29 | Low | 主体事实的软删除（`object=NULL` 墓碑）与手工事实的硬删除并存，语义分层需文档说明 | `storage.py:729-737`；`rdf_snapshot.py:54` |
| 30 | Low | `Coordinator.seen` 为整个 session 生命周期保留每个请求 id（硬上限 65536，超限 session 致命） | `coordinator.py:155,282-284` |
| 31 | Low | 内部异常消息内嵌原始事实值（subject/predicate/owner/source_row/id）。当前 `classify` 只转发 `.code/.params`，属**潜在**泄露，非当前泄露 | `storage.py:767-773`；`coordinator.py:93-94` |
| 32 | Low | 重复撤销报 `INVALID_STATE` 而非幂等 no-op。**保留原样**：原 operation 幂等与"以新 operation 再次撤销"语义不同；ABA/后续修改冲突必须保留（`compensation.py:170-188`）。这是**优点**，不建议改成无条件 no-op | `compensation.py:187-188` |
| 33 | Low | `createIntent` 仅存内存（React ref），重启后同名可再建一个项目；引擎侧以 `operationId` 去重故不会重复创建，UI 已给诚实提示 | `App.tsx` `createIntent` ref |
| 34 | Low | `create_project` 存在绕过版本化直接写库的内部 API（不写 `operation_claims`/`app_receipts`）。**当前不可从协议到达**（仅 `storage_probe.py` 与测试调用），属**潜在**暴露 | `storage.py:259-267`；`job_store.py:637-643` |
| 35 | Info | `OntologyPage.tsx:550-578` 的客户端重建 Diff 渲染器**无生产调用者**（T02 走 `previewManagedEdit`），一旦被接线即暴露非权威 Diff | `OntologyPage.tsx:35,156`；`OntologyMainlinePage.tsx:119-128` |
| 36 | Info | `mainline-session.ts:166` 已退役项目的 session 会读取并写入**另一项目**的全局 book 条目（写的是 B 自己的 pending，局部状态写入受 `projectId` 门禁） | `mainline-session.ts:166,169` |
| 37 | Info | 并发主链路调用**直接拒绝**而非排队（无错投，良性并发产生硬失败） | `engine.ts:764`；`mainline.py:288` |
| 38 | Info | 撤销对账对每个后续 commit 调 `_with_retirements` → `retirement_at` 全历史扫描 ⇒ 长历史下 O(n²) | `compensation.py:177-186` |
| 39 | Info | 无 `CHANGELOG.md`、无 Terms/Privacy 文档；`appId: io.github.nomorejoke.ontolearnstudio` 仍为个人/项目名而非组织名 | 仓库根；`electron-builder.yml` |
| 40 | Info | Dependabot 只覆盖 npm 与 github-actions，**未覆盖 Python**（SECURITY.md 声明 Python 为手工 `uv lock --upgrade`） | `.github/dependabot.yml` |
| 41 | Info | 单元层存在 28 处弱断言模式（`toHaveLength(0)`/`toBeDefined()`/`toBeTruthy()`/`toBeGreaterThan(0)`），分布在 9 个变更单测文件；**e2e 层未发现仅断言数量或仅"按钮可点"的用例** | `tests/unit/**`（grep）；对照 e2e 断言强度见 §5 |
| 42 | Info | 存在名为 `mainline-consumer-first-ack-loss` 的 e2e，其"首次 ACK 丢失"注入在 **IPC 回复层**（真实 handler 先执行、随后抛错使渲染端 Promise reject）；**引擎→主进程**这一腿的丢失、以及"引擎已提交但主进程尚未持久化即崩溃"未被覆盖 | `tests/e2e/mainline-consumer-first-ack-loss.spec.ts:57-146` |

---

## 5. 证据链独立核验结果（本方逐项亲自复算）

| 证据 | 本方独立核验 | 判定 |
| --- | --- | --- |
| 附件 20609 B / `81741afe…854f` | 实测字节与 SHA256 | **一致** |
| 清单 11255 B | 附件第 29 行至 EOF 提取与 canonical `user-review-checklist.txt` **逐字节相同**（`cmp` IDENTICAL，SHA `1ca23def…f709c`） | **一致** |
| 远端 develop `5f910b52` | 只读 `ls-remote origin` 实测 | **一致** |
| HEAD `748008a6` / base `5f910b52` / merge-base | `rev-parse` / `merge-base` / `cat-file -t` 实测 | **一致** |
| 38 commits / 525 files | `rev-list --count` = 38；`diff --name-only` = 525；`+561064/−4638` | **一致** |
| AGENTS.md `15147B/de15f6ce…` | 实测字节与 SHA；工作区仅 ` M AGENTS.md`；**未修改** | **一致，未修改** |
| 索引 `173116B/0bd0667b…` + cached diff 空 | 索引文件实测字节与 SHA；`git diff --cached --quiet` → EMPTY | **一致** |
| S1270 闭集 `223577B/ebf3328e…` | 实测字节与 SHA | **一致** |
| **S1270 内容复算** | worktree 内逐条重算 1270 条 bytes+SHA256 → **1270/1270 一致，0 缺失 0 不符**；路径集与 `ls-tree -r HEAD` **完全相等** | **一致**（闭集含未暂存 AGENTS overlay，见 §1） |
| whole087 单次完整 check 自然 0 | 日志实读：`Test Files 35 passed (35)`、`Tests 1694 passed (1694)`、3 段 `✓ built in 33/20/60ms`、`ruff` "All checks passed!"、`pytest 3445 passed, 44 skipped in 133.63s`；`check-full-087-receipt.json` `naturalExit:0 / observedExit:0 / timeout:false / sourceUnchanged:true / changed:[]` | **一致** |
| main `594342B/83d82b19…` | `actual-out-after/main/index.js` 实测字节与 SHA；`actual-five-JS.json` 五件产物逐条登记 | **一致** |
| BUILD-NONCE-DIFF（仅一处 24 ASCII nonce 差异，其余全等） | 实测 `oldMain.sha256=847fa7e5…` vs `newMain.sha256=83d82b19…`，两文件均 594342 B；`allOtherMainBytesEqual=true`、`remainingFourOutputsEqual=true`；差异根因定位到 `electron.vite.config.ts:7` 的 `randomBytes(18)` | **一致**（与 §4.10-1 互相印证） |
| **"JS 未在 748 重建"** 的诚实性 | `buildTimeProvenance` 原文："dd21+exact1 E2E-test WIP -> check/build unchanged exact1 commit748008a6. **Not rebuilt at 748.** Product source unchanged; existing build-time dev CSP nonce differs." —— 且 check 的 `cwd` 为 `node-checkout`（N 侧），源码内容与 748 等价（因唯一变更只改测试文件） | **一致且诚实**：不可称"748 重新 build" |
| package087 实物闭包 | 本方 `os.walk` 实测：APP **910**（549 文件+361 目录）、Resources **290** 常规文件、engine **266**（225+41）、`app.asar` 19 014 603 B / **819** 文件成员 | **与受理票数字逐个吻合** |
| root 受理票 `107285B/41e81bd9…` | 实测字节与 SHA | **一致** |
| e2e actual002：18 collected / 16 PASS + 2 平台条件 skip | `frozen-original/test.stdout.raw` 实读："Running 18 tests using 1 worker"、逐条 ✓/− 明细、"2 skipped / 16 passed (1.3m)"；T02 两例 **4.4s / 4.3s**（与声称逐字吻合） | **一致** |
| 2 条 skip 是真实平台条件 | 回源码 `i04-jobs.spec.ts:100-103`（`process.platform !== 'linux' \|\| !fixturePath`）、`:318-321`（另需 `I04_NATIVE_ISOLATED==='1'` + openbox/xdotool） | **一致，非隐藏失败** |
| 入口/worker/retry/预算未改 + 全自然 0 | `ENTRY.json`：`naturalCoordinatorExit/naturalWrapperExit/naturalNPMTestExit = 0`、`timeout=false`、`retries=0`、`actualProductAttempt=1`、`durationSeconds=81.27` | **一致** |
| 缺 process getter 仍记未知 | `actualGettersMissingRemainUnknown=true`；`KNOWN-PIDS-AFTER.json` 与 `finitePSExit=1`、`globalDrainClaim=false` | **一致（未把有限 PID 采样洗成全局 reap）** |
| 三 SOURCE005 在途模式 `faultApplied=true` 且 PASS | `ACTUAL-RUNTIME-RESULTS.json` 实读：`reload.faultApplied=true/result=PASS`、`renderer-recovery.faultApplied=true/result=PASS`、`coordinator-exit.faultApplied=true/result=PASS` | **一致（无 NOT_EXERCISED）** |
| **引擎 exit/close 本轮直接观测到** | `frozen-original/coordinator-exit/actual-native.json`：`childProcesses[0]`（被故障杀死者）`exit={code:null,signal:'SIGKILL'}`、`close={code:null,signal:'SIGKILL'}`；`childProcesses[1]`（重启后的引擎）`exit={code:0,signal:null}`、`close={code:0,signal:null}`；`childSnapshotAfter[0].exit.code=0 / close.code=0` | **一致**：本轮是**新观测**，085 的 `UNKNOWN_NOT_OBSERVED` **未被改写**（属不同轮次） |
| 真实故障语义 | `readsAfterFault[0].job.error.code=ENGINE_EXITED`；`coordinatorReady.connection.update.error.code=ENGINE_EXITED`；`taskUpdatesAfterFault` 4 条 seq | **一致** |
| native 真实生命周期 | `native-lifecycle.result=NATIVE_RESTORE_DECLINE_NORMAL_QUIT_OBSERVED`；`testCleanupBeforeQuitAt=03:36:41.542Z` < `testCleanupWillQuitAt=03:36:41.650Z` | **一致** |
| 086 首败保留 | `actual002/ENTRY.json`：`original086TestFailurePreserved=true`；`original087FirstGuardFailurePreserved` 指向 `actual_001/ENTRY.json` | **一致** |
| **086 失败 trace 身份** | `trace.zip` 实测 **18686 B** / SHA256 `216e28909f149e7b5a564345f498244408fac14435548c2e560e0eb1231ed259`，zip 内 6 成员（含 `test.trace` 82645 B） | **一致（与声称逐字节吻合）** |
| 归档误指"passed trace"已更正 | `TRACE-REFERENCE-CORRECTION.json`（两份副本内容一致）：说明原 ENTRY 的 `savedTrace` 与首个 `ORIGINAL-TRACE-CALLS` 用了未过滤 glob 选中了通过件；登记正确失败 trace 与 `FAILED-T02-TRACE-CALLS.json`（9527 B / `632db975…`）；`verifiedCalls=[rpbm@1544,1545,1547,1548,1549,1543]` | **一致** |
| **旧 086 UI 未采样，不得称通过** | 同文件 `UIReceiptActualDOM: "UNKNOWN; no receipt saved in this trace. Durable DB success is independent evidence, not a UI acceptance pass."` | **一致（诚实限制保留）** |
| 748 只改 DOM 快照读取，未放宽断言 | 本方逐行比对 `git show 748008a6`：仅把 `count()`+`textContent()` 双 await 改为一次 `evaluateAll`；同一 `.not.toBe('waiting')`、同一两个谓词、同一 `needsReconciliation` 分支、`:215-218` 的后续断言**全部未改**；并**新增**重复区域拒绝（`:198-199`）。渲染端标记为 `<section aria-label>`，与 `getByRole('region',{name})` 等价 | **一致**（且较原实现**更严**；"重复region仍拒"实为**新增**而非保留） |
| 独立 postpatch 复核 | `INDEPENDENT-POSTPATCH-REVIEW.json`：`"One evaluateAll synchronously reads both original regions, removes observed count→textContent TOCTOU. Duplicate region rejection, original two predicates/5s and every later assertion remain."`、`actualRuntimePassClaim: false` | **与本方独立结论一致** |
| 087 外部 guard 首败保留 | `actual_001/ENTRY.json`：`status=FIRST_ACTUAL_GUARD_FAILURE_PRESERVED_BEFORE_WRAPPER_PRODUCT`、`naturalCoordinatorExit=1`、`productCaseAttempts=0`、`wrapperNpmAppStarted=false`、`actualGUISteps=0`、`globalDrainClaim=false`、`finitePSExit=1` | **一致**（0 产品用例，非产品失败） |
| adapter 只改一行全局 HEAD | 本方 `diff -U0` 实测：**仅第 30 行** `HEAD='dd21ab12…'` → `HEAD='748008a6…'`，两文件**均为 81030 B**，其余函数与 observer 逐字节相同 | **一致** |
| 14 个全局读回 | `ALL-GLOBAL-BINDING-READBACK.json` 列出 14 项（REPO/CANONICAL/RUN/RUNTIME/PHASE/LABEL/NODE/NPM/PYTHON/WRAPPER_SHA/HEAD/AUTHORITY/FIXED/RUN_SPEC），`HEAD` 与 `AUTHORITY` 均指向本候选 | **一致** |
| 085 两份历史报告 + 处置记录 | 双方历史报告与 `review-opinion-treatment.md` **对称读取**；M1/M2/M3/M4 处置逐项回源码复核（§4.2/4.3/4.4 与 §9） | **已复核，结论见 §9** |

---

## 6. 用户 11255B 清单逐项适用性判断（全部 160 条引用行逐条判定）

> 原则：**先判适用性**；不适用按**类别**简述依据；**适用但未核实写"无法确认"**；不为满足清单而给本产品扩建无关功能。
> 本产品形态：**本地优先、单用户、离线、无服务端、无网络端口、无账号体系、无计费、无模型接入**。因此清单中大部分条目属服务端/SaaS 形态，按类别不适用——但这是"当前形态不适用"，**不是"已具备"**。

### 6.1 整类不适用（按类别说明依据）

| 类别 | 清单条目 | 不适用依据 |
| --- | --- | --- |
| 账号与身份 | login（+号邮箱）、密码重置、MFA 及其恢复、会话超时与全量会话吊销、SSO、SAML、SCIM、深于 admin 的角色、按 URL 改号越权、租户隔离、管理员"登录为该用户"及审计、登录限流、防 CFO 误锁 | 无服务器、无登录、无多用户/多租户；IPC 侧以 sender/frame/文档三重校验替代（`index.ts:317-324`、`trusted-document.ts:2-12`）。**注：一旦引入"接收他人项目文件"或团队共享，该整类立即适用且当前为零基础** |
| 支付与计费 | 订阅/升级/降级/按比例、失败扣款与催缴、发票与 PO 号、销售税/VAT、退款/信用额度/部分退款、用量计量到分、年约定制条款、财务对账报表 | 无任何货币处理（无 money 字段，"money stored as integers"随之不适用） |
| 对外 API 生态 | 版本化对外 API、客户 API key 与吊销、API 限流、第三方 API 响应格式突变预案、OAuth token 刷新、集成沙箱、webhook 签名与重试日志 | 无对外 API/webhook；引擎协议是**私有 stdio 契约**（`registry.json` + `schema.json` 双端校验 + 固定错误码表），本身即"designed schema" |
| 邮件 | SPF/DKIM/DMARC、退信与投诉处理、邮件客户端渲染 | 不发邮件 |
| 云基础设施 | dev/staging/prod 对齐、IaC、零停机、一键回滚云语义、功能开关、自动扩缩、CDN、DNS/SSL 续期、第二区域、DR 年度演练、状态页、成本告警 | 无云服务、无网络端口（`connect-src 'none'` + 引擎 audit hook）。本地等价物已核：CI 完整门禁、回滚=上一目录包+git 还原（流程层） |
| 观测与值班 | 3am 可搜结构化日志、错误聚合、外部拨测、告警 paging、延迟/错误率/吞吐仪表盘、跨服务 tracing、on-call 轮值、runbook、postmortem、状态页 | 无运行服务可观测。产品以**零日志策略**为隐私设计（主进程零 console/零日志文件；错误只出固定码受限参）。**有意取舍，非缺失**；若接入模型网关需重评 |
| 合规套件 | SOC 2、HIPAA、BAA、PCI scope、GDPR 全表/备份/日志删除、数据驻留、季度权限复核、渗透测试、安全问卷证据包、企业买方尽调 | 不处理 PHI/卡号/第三方 PPI，无企业买方。`SECURITY.md` 已含私有披露约定。转为"首个企业客户前的义务" |
| 流量与规模 | 连接池、周一尖峰、负载测试、5M 行索引超时 | 本地 SQLite 单写者 + 独占租约；分页/导出边界已设硬顶。**容量与老设备口径属 Q5/D2 未执行项**（§4.8） |
| 队列与调度云侧 | cron 双跑、死信队列、存储生命周期规则 | 无定时任务、无队列服务、无按量云成本 |
| 通知 | "notifications people can turn off" | 应用无通知系统 |

### 6.2 适用且已核并有实现

| 清单条目 | 结论与依据 |
| --- | --- |
| a schema someone designed, instead of one the AI improvised table by table | ✅ 契约驱动：`packages/contracts/v2/schema.json` + `registry.json` + `errors.json` + 21 185 行契约 fixture；双端执行（TS zod `.strict()` + Python `contract_v2.py`）；canonical JSON 拒 NaN/代理对 |
| validation on the server, not just in the form | ✅ 等价已核（无服务端）：主进程 zod `.strict()` + 引擎契约校验双重；每错误码 `paramsSchema` 且 `additionalProperties:false`，`maxEncodedBytes:2048` |
| input sanitization everywhere a user can type | ✅ 边界数据一律 zod `.strict()`；引擎侧二次校验；标识符正则 `^[A-Za-z0-9_.-]{1,128}$`；自由文本走 RDF 字面量，UTF-8 全量支持 |
| protection against SQL injection | ✅ 全量参数化（`?` 绑定）；动态标识符仅来自硬编码表名元组或 `sqlite_master` 转义读取；累计 diff 中**新增行内无 `execute(f"...")` 拼接** |
| protection against XSS, CSRF and the rest of the OWASP list | ✅ React 默认转义 + 单一 CSP 源；渲染端累计 diff 内**0 处** `dangerouslySetInnerHTML`/`innerHTML`/`document.write`；无 HTTP 面故无 CSRF/CORS 面；`connect-src/object-src/base-uri/frame-src/form-action` 全 `'none'` |
| CORS rules that aren't "allow everything" | ✅ 不适用（无 HTTP 服务、不开端口），由 CSP + 引擎 audit hook 双重保证 |
| security headers on every response | ✅ 等价已核：本产品不产出 HTTP 响应；等价的"响应头"即 CSP meta/header（唯一源 `csp.ts`） |
| secrets out of the code, out of the repo and out of the AI chat history | ✅ 无密钥存在（无模型客户端）；`.gitignore` 排 env/key/pem/p12；无 `.env`、无 dotenv；引擎 env 白名单不继承 |
| rotating every key the AI pasted into a config file last month | ✅ 不适用（无物可轮） |
| confirming every package the AI installed exists and is the one you meant | ✅ 直接依赖精确 pin（`.npmrc save-exact`）；`uv.lock` 含 sha256；新增 Python 依赖（pyshacl 0.30.1 / pyparsing 3.3.3 及传递依赖 owlrl 7.6.2、prettytable 3.18.0、wcwidth 0.9.2、html5rdf 1.2.1）**带锁文件与 sha256**；新增 npm 依赖 = 0；许可闭包已入库（`licenses/NOTICE` 逐组件登记，版本与实际树一致） |
| dependency scanning, because the AI pulled in libraries nobody reviewed | ⚠️ **部分**。Dependabot 覆盖 npm + Actions（Python 为手工 `uv lock --upgrade`，见 §4.11-40）；**本次未做 `npm audit`/`pip-audit`**（无网络，只读）⇒ 第三方 advisory 状态**无法确认** |
| file uploads that get scanned, size-limited and stored where they can't execute | ✅ 无用户上传面（导入=打包内置示例资源，路径由主进程硬指定且经 `O_NOFOLLOW`/绝对路径/`S_ISREG`/TOCTOU 复查，见 `mainline.py:52-140`） |
| encryption at rest and in transit | ⚠️ **部分 / 无法确认**。传输=无网络（最强形态，`connect-src 'none'`）；**静态=SQLite 明文**（本地优先设计下的接受项，明示记录）。设备被盗场景无缓解 ⇒ 归入 §6.4 |
| least-privilege access for everyone, including the AI agent holding production credentials | ✅ 无模型客户端/无凭据；现有"代理"=渲染层，受沙箱 + 闭合 preload + `trusted()` 三重校验约束；引擎无密钥无外联；特权引擎参数（`--t01-internal-profile` / `--t11-internal-example-root` / `dataPath`）**仅由主进程构造**，渲染端不可控 |
| logs that record who did what, without recording passwords, tokens or card numbers | ✅ 等价已核。领域动作以不可变 `commits`/`commit_evidence`/`operation_claims`/`job_details` 记录（含 actor/origin/operation）；原始字面值不写入审计；引擎 stderr 不转发 |
| audit trails that show who viewed a record, not just who changed it | ⚠️ **部分**。"谁改变了什么"完整（不可变提交证据）；"谁查看过"仅在查询侧有 `job_details`/result 元数据，**未见逐次查看审计** ⇒ 该子项**无法确认** |
| a disclosure process for the day a stranger emails you a vulnerability | ✅ `SECURITY.md` 含私有渠道报告路径与"不要在公开讨论附凭据/业务数据/可利用细节"约定 |
| idempotency keys, so a retried payment doesn't charge the card twice | ✅ 等价（无支付）："重试不重复提交"已核。`operation_claims` 与副作用**同事务**写入，先于副作用落库；`job.create` 重放返回既有 job 且复验冻结上下文；e2e 实测首次 ACK 丢失零重放（§7） |
| deduplication for the user who clicks submit four times | ✅ 同一 `operationId` 命中认领即返回原回执；主进程**拒绝自动重放已输入写入**（`project-mainline-service.ts:751` `if (intent.unknown) throw denied()`） |
| pagination that still works on page 400 | ✅ **T04 查询路径**满足：服务端 UUID cursor + 绝对 startIndex，页大小固定 200；显示层 zod 校验 ordinal 连续、`end ≤ rowCount`、`nextCursor ⟺ 还有行`；e2e 实测 **243 行跨多页**读全。**⚠️ 但本体事实/定义表是"整表传输 + 渲染层切片"**（§4.11-11），该子路径不满足 |
| exports, because sooner or later every customer wants their data in a spreadsheet | ⚠️ **部分**。CSV 存在（CRLF、引号 `""` 转义、UTF-8 BOM）且公式注入已缓解，e2e 断言精确字节；但**仅当前页**（`typed-results.ts:259` 注释 "never fetch or accumulate more rows"），无全量/JSON/XLSX。**对照 PRD：FR-402 明确"大数据量导出不属于普通查询流程"⇒ 当前页导出与 FR-402 相容；但 FR-002 的"导出项目"与 FR-203 的 Turtle 导入导出未见实现（§4.7）** |
| imports that survive the CSV someone saved in 2009 | ✅ 不适用（无用户 CSV 导入面）。**⚠️ 但 PRD FR-300（P0 支持 UTF-8 CSV 与 XLSX）尚未实现**——属 P0 功能未开工，不是本轮审查的缺陷 |
| retention rules, and code that deletes what your contract says you'll delete | ⚠️ **部分**。有缓存回收（`collect_cache` 排除 `result_pins`/`current_results`/`job_current`，仅置空 payload 保留结果身份，`payloadStatus='evicted'`）与游标 TTL（`ReadLimits.ttl_seconds=60`）；**无按合同/用户策略的保留期规则** |
| a data model that survives your second customer asking for "one small change" | ✅ 版本化 schema + `migration_log` + 显式 v2→v3 迁移 + `PRAGMA user_version` 断言 + 启动期只读结构审计（`format3.validate` 逐表逐触发器比对 SQL 文本并校验 `schema_hash`） |
| database migrations that run forward and roll back | ⚠️ **单向向前**（`version > target` → `UnsupportedProjectFormat`，**无降级路径**）。回滚=保留的迁移备份（文件级）⇒ **"run forward and roll back" 仅半满足** |
| migrations that don't lock the main table at 2pm on a Tuesday | ✅ 等价适用（单机桌面）：启动期持 OS 独占写租约（`flock LOCK_EX|LOCK_NB`），`BEGIN IMMEDIATE` + `synchronous=FULL`；无在线迁移窗口 |
| a restore from those backups, tested | ❌ **未核 / 未建立**。有迁移备份机制（强制新目标 + `integrity_check` + 源哈希复查），**未见"从备份恢复"的实测证据**（§4.7） |
| backups every night | ✅ 不适用（无服务器）。本地迁移备份存在，但**非常态备份** |
| point-in-time recovery for the day someone runs a delete without a where clause | ✅ 等价已核。SQLite 快照 + 不可变提交证据 + 显式补偿/撤销 ⇒ 无 `DELETE ... WHERE` 式破坏面。**这不是 PITR**（无 WAL 归档） |
| soft deletes, so "I deleted it by accident" is a support ticket and not an incident | ✅ 等价已核。领域以"退役（retirement）"显式建模，从不可变历史重建隐藏成员（`compensation.py:73-133`），并有"退役影响预览"；本体事实墓碑（`object=NULL`）在快照中保留且不进入 RDF 图 |
| caching, and clearing that cache when the data changes | ✅ `invalidation-v2.json` 单一规则源；`collect_cache` 排除 current/pinned；结果身份保留、载荷可回收；`staleReason` 只由规则文件产生；**仅改模型配置不作废领域结果**；历史/失败/取消不计入过期原因 |
| undo | ✅ 已核。补偿为**服务端前向补偿新事务**（不改写历史），带 ABA 保护（值相同也需 later-edit 校验）；e2e 实测 Undo 与 Undo-of-Undo 通过。局限见 §4.9（无独立 redo/历史选择器）与 §4.11-32（重复撤销报冲突而非 no-op，**有意保留**） |
| a human approval step for anything the AI does that can't be undone | ✅ **结构性**已核。`registry.json` 逐能力声明 `agentEligible`/`requiresConfirmation`/`exposure`/`requiresChangeSet`；`changeset.preview`/`changeset.confirm` 为 `agentEligible=false`（仅 internal-business3-trusted-host）⇒ **Agent 无法自我确认**；UI 确认按钮在完整 Diff 全部行展示后才可用（`OntologyMainlinePage.tsx:281-290`） |
| code a human can read | ✅ TS `strict`；Python ruff（E/F/I/UP/B，line-length 100）；领域文件单一职责 + 模块级 docstring 说明"为什么"。**⚠️ 但多项已超 2000 行（§4.10-4）** |
| architecture decisions written down, with the reasons | ✅ `docs/architecture/0001-desktop-framework.md`、`0002-storage.md`、`0003-resident-coordinator-and-jobs.md` + `docs/iterations/**` |
| a README that gets a new engineer running locally in under an hour | ✅ 结构达标（`README.md` 快速开始 + `CONTRIBUTING.md` + `docs/development.md`）；**"一小时"未实测 ⇒ 无法确认** |
| documentation for whoever inherits this | ✅ `AGENTS.md`（owner 规则）+ `docs/prd|architecture|iterations|reviews` + `source-manifest` |
| a branching strategy, so two people can work without overwriting each other | ✅ 独立 worktree + `feature/<模块>-<子任务>` + PR 合回 develop；禁止共享 checkout 并行写；提交前缀规范 |
| code review on every change | ✅ 流程层面：指定双审 + CI + 远端核验门禁；本报告即其中一环 |
| monthly dependency upgrades, so you're never two major versions behind | ✅ Dependabot（npm + Actions，weekly）。**⚠️ Python 侧为手工**（§4.11-40） |
| framework upgrades before the old version stops getting security patches | ✅ 机制在（Dependabot + `uv lock --upgrade` 政策）。**⚠️ 实际补丁响应节奏无法确认（无既定 SLA）** |
| unit tests written by someone who knows what the logic should do | ✅ Python 侧 **60 文件 / 563 个 test 函数**（AST 计数），仅 2 个无直接 assert（但经 `diagnosis()` helper 间接断言返回码/空 stderr/单行 stdout/错误码/契约校验）；TS 侧 35 文件 / 1694 测试。断言多为**具体预期集合与顺序**。**⚠️ 单元层 28 处弱断言模式（§4.11-41）** |
| integration tests for every third-party API you depend on | ✅ 不适用（无第三方 API 依赖；仅 rdflib/pyparsing/pyshacl 三个固定版本库） |
| end-to-end tests for signup, checkout and the other flows that make you money | ✅ 等价：18 条**真实 Electron + 真实 Python 引擎** e2e（16 PASS + 2 真实平台条件 skip），断言真实领域语义（完整 Diff 文档逐字比对、marker 全字段相等、Job input/commitProgress、undo 后域状态、重启后同 profile 重读），**非"按钮可点"式冒烟** |
| regression tests, so fixing bug 41 doesn't bring back bug 12 | ✅ 专门回归集存在（`test_mainline_cleanup_regressions.py`、`binding-regressions.json`、`verify-frozen-review-sources.test.ts`、本次新增的 `t01-mainline-reply-lifecycle.test.ts` 清理失败重试用例） |
| test data that looks like production without being production data | ✅ `packages/contracts/v2/fixtures.json` 与 `tests/fixtures/T04/` 为合成夹具；`.sqlite`/`.db`/`.env` 不入库 |
| loading testing before the launch email goes out | ❌ **未执行**（D2 规模口径未关闭）。**不得以 243 行 E2E 充当负载测试** |
| testing on the five-year-old laptop your biggest customer's ops team still uses | ❌ **未核**（Windows/参考设备未执行，Q2 未决） |
| accessibility compliance, because the enterprise contract requires it | ⚠️ **部分**。被动 a11y 良好：`role=alert`/`role=status`/`aria-live`/`scope="col"`/`role=img`+`<title>`/原生 label 关联。**缺口**：本体事实表 `<th>` 无 `scope`、切换无焦点管理（§4.11-23/24）、本体模块 0 处自定义键盘导航、树形结构无 `aria-level/expanded` ⇒ 合规性**无法确认** |
| empty states, loading states and error states on every screen | ⚠️ **部分**。`OntologyMainlinePage` / `QueryWorkspacePage` / `QueryResultPanel` 三屏均有专门空/加载/错误分支；**全屏覆盖度未逐屏核验 ⇒ 其余屏幕无法确认** |
| error messages a customer can act on, instead of "something went wrong" | ✅ 固定错误码 + `messageKey` + 枚举化参数；`safeDisplayError` 在主进程做展示投影；**不返回原始异常/堆栈/路径**；四段式"发生了什么/为什么/如何修复/相关知识"有 e2e 断言。**⚠️ 局部瑕疵见 §4.11-25（NaN 插值）** |
| forms that keep what people typed when one field fails validation | ⚠️ **部分**。服务端保留 `preservedDraft`；选择操作不覆盖未保存草稿；错误文案明示"已输入内容保留"（`OntologyMainlinePage.tsx:267-272`）；**逐表单核验未完成 ⇒ 无法确认** |
| a back button that does what people expect | ❌ **无法确认**（未核导航历史模型）。桌面视图经菜单/链接切换（`installViewNavigation`），无浏览器历史栈语义 |
| keyboard navigation and screen reader support | ⚠️ **部分**，见"accessibility"条 |
| translations, with dates and numbers formatted for each locale | ⚠️ **部分**。无 i18n 层（全部硬编码简体中文，`index.html lang="zh-CN"`）；**正面**：renderer 内 `toLocale|Intl.` **0 处**，时间戳从不渲染为日期 ⇒ 无 locale 日期/数字错误，但也无人类可读时间。**注**：`SafeError.messageKey` 携带但从不渲染（`typed-results.ts`/Panel 直接拼 code）⇒ 可行动性靠固定中文模板而非 messageKey |
| notifications people can turn off | ✅ 不适用（无推送/邮件） |
| pages that load on hotel wifi | ✅ 不适用（离线本地应用，**无任何网络请求**；`connect-src 'none'`） |
| emails that render in every mail client | ✅ 不适用 |
| zero-downtime deploys | ✅ 不适用（单机桌面应用） |
| cron jobs that don't run twice the day you add a second server | ✅ 不适用（桌面单机无常驻调度） |
| background job queues, so slow work doesn't freeze the page | ✅ 已核。`JobStore`（`jobs`/`job_plans`/`job_confirmations`/`job_current`/`job_cursors`）+ 常驻协调器 + 取消 + 资源上限；查询/提交均走持久 Job + 订阅更新，UI 保持响应 |
| retries with backoff, so one flaky API call doesn't become a lost order | ✅ 已核。主进程侧三次尝试、250ms×2^(n-2) 退避、每次 15s 超时、attemptToken 使迟到回复无法授权下一次尝试；引擎侧 `reconcile_jobs` 重启后把非终态 Job 判失败/取消（`ENGINE_EXITED`）而非重跑 |
| a dead-letter queue for the jobs that fail every retry | ⚠️ **部分**。Job 有终态（succeeded/failed/cancelled）与 `job_details` 证据，但**无独立 DLQ 视图** ⇒ 该子项**无法确认** |
| structured logs you can search at 3am | ✅ 等价已核（JSONL 行协议严格 raw reader + 帧上限）。**注**：产品为隐私采用零日志策略，可检索性是取舍 |
| an admin panel for your ops team | ✅ 不适用（单用户本地应用，无运维角色） |
| support tooling | ✅ 不适用（同上） |
| a changelog customers can read | ❌ **未满足**（无 `CHANGELOG.md`）。当前无外部客户，影响低 |
| terms and a privacy policy that match what the code does | ❌ **未满足**（无 Terms/Privacy 文档）。**正面**：README/SECURITY 声明本地优先、无遥测、无外联、未签名仅内部——与代码实测一致（无网络客户端、无遥测代码） |
| every account, domain and repo in the company's name | ⚠️ **部分**。`appId: io.github.nomorejoke.ontolearnstudio` 用个人/项目名而非组织名 ⇒ 按本条**未满足** |
| a bus factor higher than one | ⚠️ **无法确认**（组织事实，不可从仓库证据判断）。**可核实的相关风险**：仓库与 `appId` 归属个人名下（见上条） |
| a disaster recovery plan, written down and tested once a year | ❌ **未核 / 未建立**（且损坏 SQLite physical HOLD 未关闭） |
| dev, staging and production environments that match each other | ⚠️ **部分**。CI 有 Linux/多形态矩阵（`ci.yml`）；但 dev（business3 无 fixture）/ packaged / fixture 三条路径的 profile 与示例根**不同**，一致性未系统核验 |
| infrastructure written as code | ⚠️ **部分 / 不适用**。CI 完整且冻结安装（`npm ci`、`uv sync --frozen`）；**IaC 不适用**（无云资源） |
| a deploy pipeline that runs the tests before anything reaches customers | ⚠️ **部分**。CI 有完整 `npm run check` + 打包验证脚本，**但正式发布流水线未建立**（无签名/公证/分发步骤） |
| one-click rollbacks, because Friday deploys happen | ⚠️ **部分**。有迁移前备份（`O_EXCL` + fsync）与显式 rollback-to-preview savepoint；**无产品级一键回滚** |
| feature flags, so you can ship the code without shipping the feature | ⚠️ **部分**。存在内部 profile 开关（`business3`/`legacy2`）与 `testMode`；**非产品级特性开关** |
| indexes, because the query that was instant on 50 test rows times out on 5 million real ones | ⚠️ **部分 / 无法确认**。已核键集分页与 `LIMIT` 边界；**索引与大数据量执行计划本次未核**（D2 未关闭）⇒ 真实规模下性能**无法确认** |
| a plan for the day a third-party API changes its response format | ✅ 不适用（无第三方 API 调用） |
| protection against prompt injection in every field that reaches the model | ✅ 不适用（S3 前无模型调用路径）。**但见 §6.3 的落地前义务清单** |
| customer and patient data kept out of prompts that leave your network | ✅ 不适用（同上） |
| a model spend cap per customer | ✅ 不适用（无计费、无模型调用）⇒ 属 I06 范围 |
| evals, so you find out when a model update makes your answers worse | ⚠️ **部分**。有契约/夹具/黄金集与 `verify-frozen-review-sources` 冻结校验；**模型质量 evals 不存在**（无模型） |
| a fallback for the afternoon your model provider goes down | ✅ 不适用（无模型依赖） |
| a migration plan for the day your model gets deprecated | ✅ 不适用（无模型依赖） |
| prompt and output logs for debugging, minus whatever you're not allowed to keep | ✅ 不适用（无模型调用） |
| GDPR deletion requests that reach every table, backup and log | ✅ 不适用（不收集个人数据、不联网）。**注**：本地用户数据的"彻底删除"未见产品化入口 ⇒ 语义上部分适用，**无法确认** |
| data residency for the customer whose contract says EU only | ✅ 不适用（数据 100% 本地，无区域存储） |
| HIPAA / a BAA with every vendor / PCI scope | ✅ 不适用（无 PHI、无支付卡、无受监管客户）；**一旦改为服务化即整体适用** |
| quarterly access reviews someone signs off on | ✅ 不适用（无账号/角色体系） |
| a penetration test before your enterprise customer's security team runs their own | ❌ **未执行**（发布义务） |
| answers to the security questionnaire every enterprise buyer sends, with evidence behind each one | ⚠️ **部分**。`SECURITY.md` 已声明边界与"当前健康检查通过不代表未实现业务安全能力通过"；**正式问卷证据包未建立 ⇒ 证据部分无法确认** |
| a plan for the day a laptop with production access gets stolen | ❌ **未核**（无静态加密、无密钥托管、无远程吊销——本地无账号体系）。发布义务项 |
| "reading every line the AI wrote before it ships (a senior engineer)" 等 13 条人工角色条目 | ⚠️ **无法确认**（人员稳定性与轮值不可从仓库证据判断）。**可核实的对标**：指定双审 + CI + 远端核验门禁在案运行（本报告即其中一环）；但 **bus factor=1 与个人名下仓库归属是真实组织风险** |

### 6.3 适用但**无法确认 / 未满足**（需后续里程碑处理）

1. 静态加密与设备失窃预案（本地 SQLite 明文）。
2. 正式发布流水线 + 分发产物（无签名/公证/安装件）。
3. Windows 与参考老设备（含五龄老设备）实测。
4. D2 规模/负载口径与索引验证。
5. 可访问性（键盘导航、屏幕阅读器、对比度、树形 aria、切换焦点管理）。
6. "谁查看过"审计。
7. 全屏空/加载/错误状态覆盖度。
8. 表单校验失败保留已输入内容的逐表单核验。
9. i18n / locale 日期与数字格式化 / RTL。
10. `CHANGELOG.md`、Terms/Privacy。
11. 组织化命名（`appId` 与仓库仍为个人/项目名）。
12. 超大文件拆分（`job_store.py` 2589、`engine.ts` 2623、`semantic.py` 1627）。
13. **备份恢复实测**（有备份机制，未见恢复演练证据）。
14. 可测试的 DLQ 视图。
15. "按合同删除"的保留期规则。
16. **本体/项目级导出与 Turtle 导入导出**（PRD FR-002 / FR-203，P0）。
17. **CSV/XLSX 数据源接入**（PRD FR-300，P0）。
18. 分支保护规则与 PR 模板强制（模板文件存在；**远端设置本次只读未核**）。
19. 第三方依赖 advisory 状态（无网络未核）。
20. 依赖扫描对 Python 的覆盖。

### 6.4 模型接入前的落地前义务（S3 之后整类适用）

以下条目当前"不适用"，但**一旦接入模型即整类适用**，属 I06 前必须建层的义务，本轮如实登记而非视作已完成：提示注入防护（每字段）、客户/患者数据不出网、每客户模型花费上限、模型质量 evals、模型商宕回退、模型弃用迁移、提示与输出日志（扣除不可保留部分）、密钥保护（FR-901 要求进 OS 安全存储或等效机制——**当前无密钥故未实现，不得记作已具备**）。

---

## 7. 任务书指定的五条边界 —— 本轮独立追踪结论

### 7.1 创建 / 示例复制 / 补偿 / owned draft / 重启
- **创建**：显式应用事务（`project_lifecycle.py:426-556`），严格 4 字段 request + 严格 3 字段 origin（`permission` 必须字面为 `library.create`）；项目 id 服务端 `uuid4()` 且多表 uuid 碰撞检查；**genesis 被验证而非断言**（`require(genesis == candidate["before"])`）并用**已验证的实际 genesis 重建 candidate** 后再落 claim；`library_evidence` 绑定 `app_format.migration_id`（绑定已安装 format3 目录，而非路径）。
- **示例复制**：两阶段、replay-first。认领命中则从**不可变上下文闭包**服务（不从后续可变 bundle 读），且要求 request **与 origin 全等** + 重算回执相等；否则从**显式安装、哈希钉死**的 bundle 根读取，含绝对路径、`O_DIRECTORY|O_NOFOLLOW`、`O_NOFOLLOW|O_NONBLOCK`、`S_ISREG`+尺寸、**前后 `fstat` dev/ino/size/mtime 比对（TOCTOU 防护）**、manifest SHA-256 必须等于 bootstrap pin。
- **补偿**：纯函数、零 SQL 写入（`compensation.py:143-201`，"never mutate current or any persisted record"）；ABA 防护显式（值相同也需 later-edit 校验）；`trusted_snapshot` 拒绝未来快照；`preview_restore` 拒绝 `target > base`；退役成员**从不可变历史重建**（`retirement_at` 重放 `commits`+`commit_evidence`），完整性缺口抛 `Conflict`。
- **owned draft**：两套机制需区分——**持久草稿**=`app_drafts` + 逐 `(project, editor)` 代际 CAS（`draft_plan.py:110-134`，同时校验 `expectedGeneration` 与 `boundDomainRevision`）；**`DraftWorkspace`（`workspace.py`）是易失编辑器会话，仅被测试引用、无生产 import**（§4.11-17）。
- **重启**：`reconcile_jobs` 在取得 OS 独占写租约**之后**把非终态 Job 判失败/取消（`ENGINE_EXITED`），注释明确"marker alone can never invent success"；`format3.validate` 启动期只读复核**每个项目的全部历史**；写租约在进程死亡（含 SIGKILL）时由 OS 自动释放。
- **判定：实现与证据一致，本轮未发现该边界的新缺陷。**（观察）

### 7.2 T02 完整 Diff / commit / undo / redo 与原操作回执
- **Diff 是引擎文档而非客户端重建**：`readFullDiff()` 按 cursor 重取冻结文档，逐段校验 byte offset/length/sha256 vs 引擎 manifest、重算每段 SHA-256、整档 SHA-256 vs `manifest.documentHash`、严格 UTF-8（`fatal:true`）、行形状校验；确认按钮仅在全部行展示后可用。**⚠️ 例外**：`OntologyPage.tsx:550-578` 存在一个客户端重建的"完整 RDF Diff"渲染器，**无生产调用者**（§4.11-35）。
- **commit 绑定单一原操作身份**：一次确认时刻铸造唯一 `operationId`，同时用于写入、对账与回执；回执**只**由真实引擎 marker 产生（校验 projectId/operationId/planHash(64 hex)/beforeSnapshotId/projectRevision>baseRevision/afterSnapshotId/jobId，且 Job 必须 `succeeded` + `commitProgress.mode==='atomic'` + marker 相等）；不匹配即 `INVALID_RECEIPT`。**重试不重铸身份**：查询侧恢复路径以**同一 operationId + 同一 confirmation** 重放。
- **undo 是服务端补偿性新事务**（`intent='undo'` + 全新 base 读取），冲突面逐资源比对。
- **redo 不存在**（§4.9）。
- **判定：与 e2e 一致；redo 为真实功能缺口（且不构成 FR-804 违背）。**（观察）

### 7.3 T04 分页 / 历史快照 / 导出
- **分页是服务端 cursor**，非客户端切片（针对 T04 查询路径）；行页与文本页均带游标连续性、UTF-8 字节区间与 EOF 一致性校验；历史列表用钉死的 `listSnapshotId` + 严格单调 `(createdAtMs, jobId)` 排序；结果身份（`resultId`/`payloadSha256`/`inputSnapshotId`/`inputProjectRevision`）在每页重验，不匹配即拒绝展示。
- **导出**：CSV、CRLF、引号转义、BOM、公式注入缓解、仅当前页、**无显式字节上限**；**护栏当前不可触发**（§4.11-20）。
- **⚠️ 本体事实/定义表是整表传输 + 渲染层切片**（§4.11-11），该子路径不满足"page 400"。
- **判定：T04 查询路径实现与验收一致；导出与本体表分页为真实缺口。**（观察）

### 7.4 首次 ACK 丢失 / 项目切换隔离
- **首次 ACK 丢失的注入点在 IPC 回复层**：真实 handler 先执行并断言返回了成功的投递信封，随后抛错使渲染端 Promise reject ⇒ **引擎真实执行，仅丢失回执投递**，无伪造回复、无 Job 抑制。断言为 **真实语义**：`commitCalls===1`、`executeCalls===0`、`lostAckCalls===0`、最终请求与首次请求逐字节相等（同一 operationId、同一 confirmation），并以**真实 `listJobs` 全量清点断言项目中恰好一个 Job**（唯一 rowKey、绑定与顺序均校验）；对账用真实 `getOperation`/`getJob`，marker 深度相等。查询变体：重发同一请求后引擎返回**同一 operationId 与同一 acceptedJob**（仅投递 id 不同），Job 清单仍恰好一个 ⇒ 证明是幂等重取而非重执行。
- **切换隔离**：逐个缓存核对了键——`OntologyOperationBook`（按 projectId）、查询 controller（按 projectId）、`QueryWorkspaceController.projectId`（构造期不可变）、草稿恢复（断言 `preview.projectId === source.projectId`）、`checkRead`（断言 `read.projectId === this.projectId`）、session↔project 绑定 ⇒ **均不跨项目**。e2e 以"持有真实 handler 之后的回复"证明切换后**未发出任何写 IPC**（`held.calls === []`）、diff 区域计数 0、释放后 B 的域/草稿逐字节不变，且保留的 A controller 仍持**原 operationId**、其显式重试只在 A 内落一次。
- **⚠️ 未覆盖**：`engine→主进程`这一腿的丢失、以及"引擎已提交但主进程尚未持久化即崩溃"；且该 e2e 自述未覆盖"选择与 React 清理之间的微任务窗口"（§4.11-42）。
- **判定：实现一致，边界质量高；覆盖边界已如实标注。**（观察）

### 7.5 main / task / engine session / epoch / 权限 / 持久 Job / marker / noReplay
- **三个不同的计数器**已分清：引擎 session id（引擎在 hello 中签发，每条通知须匹配）、引擎进程 generation（每次 spawn 自增，`#current()` 要求同代）、task view generation（`clearView` 自增）、主链路选择 epoch（每次重选项目自增，嵌入每个 recovery principal 并在 `current()` 复检）。
- **权限/信任模型**：桌面宿主是唯一 principal；线上协议**永不**提供 store/permission/scope/implementation/read ticket；`allows_owner` 要求 host/actor/store/session/ordinary/mainline **全部**同一；越权访问非当前项目 → `PERMISSION_DENIED`（仅 `project.open` 可命名未选中的目录 id）；`host_client_id` 明确是"受信 stdio 客户端的归属，**绝不是**人类同意的证明"——同意由显式确认摘要承载（`CONFIRMATION_MISMATCH`）。
- **持久 Job**：TS 侧**无**持久 Job store（"Durable job outcomes always come from SQLite queries"）；Job 结果恒从引擎重读（`job.get` / `operation.get`）。
- **marker / noReplay**：marker 与回执/终态**同事务**落库；`reconcile` 在 marker 缺失时返回 `uncommitted` 且**永不授权自动重试**；`operation_get` 纯从不可变 marker 解析；TS 侧 `reconcileMarkers` 交叉核对 `job.commitProgress.marker` 与 `operation.get`，不一致即 `invalid`。
- **引擎退出观测**：stdout end / stdin error / error / close **四条路径全部路由到 `#finish`**（标记终态、投递转 UNKNOWN、拒绝在途请求、SIGTERM→1s 后 SIGKILL 升级、发出 `EngineConnectionState`）；`TaskService` 与主链路 source 均消费该事件。**无独立"挂起杀进程"监视器**，只有心跳 + 每请求超时。
- **重启**：惰性（下次请求触发）、退避 100ms→2s、60s 内最多 5 次；新会话拿新 `engineSessionId` + 自增 generation，旧投递转 UNKNOWN、旧 principal 不可再采纳 ⇒ **epoch 权威被保持**。
- **判定：除 §4.1/§4.2/§4.4 的生命周期缺陷外，实现一致。**（观察）

---

## 8. 其余阻断与验收缺口（原样保留，未清零）

### 8.1 发布义务（五项独立 HOLD）
1. **签名 / 公证 / 可分发产物**：`identity: null` + `target: dir`（§4.5）。
2. **完整 legal 与 `_distutils` 归属**：`licenses/` 与 vendored setuptools/packaging 的 LICENSE 原件已入库（`licenses/python-vendored/setuptools-84.0.0/`、`licenses/python-runtime/packaging-26.3.dist-info/`），但 D8 决策书明确"完整 legal"**未通过**，9 项非 engine 签名与 APP deep 仍失败。
3. **跨平台 / 参考设备 / 无开发环境设备离线启动**：未执行。
4. **损坏 SQLite 物理保护 HOLD**：未关闭（§4.7）。
5. **D2 规模/负载口径**：未关闭（§4.8）。

### 8.2 流程与合并链
- **未推送、无 PR、无 CI 运行、未合并、未远端复核**；用户 **0/17 口径不变**；本审查者无推送/合并授权，未做任何推送。
- **指定双审体系**：47 阶段指定双审积压、0 个真实指定模型 Pass；C4→C5→C6 同一 subject 三次正式配对未通过，已达 D8 人工裁决门；`D8-mainchain-888ac-human-decision-20261024.md` 待用户选 A/B，未预填。
- **M0 退出项全部未勾**：Q2/Q3/Q5/Q6/Q7/Q8/Q9、四类基线、六项技术设计、S2/I04 合并门、签名公证离线启动；原型遗留 A-01/B-03/B-04 三项保留。
- **真实 LLM 验收**：阻塞并如实标注（代码无模型客户端，S3 前按设计不接入——已核现状与设计一致）。

### 8.3 历史轮次事实（一律保留、不追认）
- **086 首败**：完整入口原为 9 PASS / 1 T02 fail / 2 skip / 6 not run；失败 Job 在已结束 profile 复制 DB 中真实 succeeded/revision1，**但当时实际 UI 回执 DOM 无采样** ⇒ **不得称旧 086 UI 通过**。正确失败 trace 已更正登记（§5），`UIReceiptActualDOM: UNKNOWN` 保留。
- **087 外部 guard 首败**：`productCaseAttempts=0`、`wrapperNpmAppStarted=false`、`actualGUISteps=0` ⇒ 是**外部 guard/元数据错误，不是产品失败**，但同样不得洗成产品 Pass。adapter 仅改一行全局 HEAD、14 全局读回、ROOT 独立票声明同 freshphase/fixture 从未用于产品、库存全同，随后 actual002 才**真正执行一次**产品入口。
- **C4–C6 / D8 / HOLD / first full001 首败与其 22 字段修正史**：一律原样保留，本轮未改写任何历史证据文件。
- **085 的 `UNKNOWN_NOT_OBSERVED`**：本轮 coordinator-exit 的 observer **直接记到** SIGKILL（被故障杀死者）与 exit 0/close 0（重启后引擎）——这是**新观测**，**不改写 085 的结论**，也不从有限 PID absence 反推全局 reap。

---

## 9. 对上一候选（7d30 / package085）处置记录的独立复核

`review-opinion-treatment.md` 登记了 MiniMax 的 18 项建议与 ZCode 的 Top10。本方**逐项回源码复核**后的独立结论：

| 原项 | 处置登记 | 本方独立复核结论 |
| --- | --- | --- |
| **M1** uncertain 单向闩锁 | 部分采纳，缩小影响范围 | **闩锁未修复**（`engine.ts:822/2098/2501/2566` 仅置位，全仓无复位）。"缩小影响范围"指的是修正"整个 App 永久不可用"的**表述**（只读恢复通道确实存在）。**应记为 Medium–High 延续缺陷，不清零**（§4.2） |
| **M2** 跨 session 原操作必冲突 | 不采纳全局 High，保留创建专属限制 | **成立**。`operation_get` 按当前许可读 marker、恢复白名单含 `job.get`/`operation.get` ⇒ "所有 Job/marker 不可对账"的全局化不成立。**但创建/示例专属限制客观存在且未修复**（`origin` 含 `engineSessionId`，新握手必然冲突）⇒ Medium 延续（§4.4） |
| **M3** 16 未 ACK 投递 | 部分采纳可达耗尽事实，不采纳 FIFO | **事实成立、缺陷未修**（`desktop-ipc.ts:142` 仍是唯一删除点，`:164` 上限 16）。"可达耗尽"是事实陈述而非缓解。与本轮 §4.1 共用同一 16 槽上限，叠加更快封顶（§4.3） |
| **M4** 第 17 个正常新 commit 被拒 | **已实施**（四叶，HEAD dd21ab12） | **本轮独立验证：修复真实且正确。** 新增 `#fullIntents`（只统计"完整"意图）替代原 `#intents.size>=16`；退役经 `onReplyConsumed` 绑定到**原 reply 的 ACK**，并经引擎 `consume()` 的退役回调执行；原 operation 身份（operationId/request/owner/session/jobId）由紧凑 holding 保留并**继续计入原 128MiB/1048576objects 全局预算**，不 FIFO 遗忘；释放失败保留原 receipt/holding；旧 id 严格匹配后**只做 `job.get`**（`_readAcceptedIntent` 校验 jobId/projectId/operationId/capability/confirmationRef/input 全等），**绝不重放 `job.create`**；未放宽 public 协议、未改 origin、未新增持久 intent 账本。**但新引入 §4.1 的泄漏缺陷**（退役回调抛错 ⇒ 投递与 IPC 租约永久泄漏且生产无重试）⇒ **M4 的核心目标达成，但其失败模式未被容器化** |
| M5 签名/公证/dir | 采纳实际产物状态 | 成立，本方实测与之一致（§4.5） |
| M6 每页物化载荷 | 登记规模/性能风险 | 成立；本方确认游标语义为 keyset（正确），物化为 O(总量) |
| M7 全量导出 | 当前页 CSV 事实采纳 | 成立；并**补充**：FR-402 明确"大数据量导出不属于普通查询流程"⇒ 当前页导出与 PRD 相容；但 FR-002/FR-203 的**项目/本体导出**仍未实现（§4.7） |
| M8 重复撤销 no-op 建议 | 不自动采用 | **同意**。原 operation 幂等与"以新 operation 再次撤销"语义不同；ABA/后续修改冲突必须保留 |
| M9 重启 createIntent 持久化 | 记录限制 | 成立：原 resolution 合同禁止新增 main 意图账本，缺原物理绑定继续 UNKNOWN |
| M10 probe 内部直写 API | 记录潜在误用风险 | 成立：当前协议不可达，未证明当前越权路径 |
| M11 内部异常含原值 | 保留潜在风险 | 成立：`classify` 只转发 `.code/.params`，属潜在非当前泄露 |
| M12 独立 redo/用例命名 | 保留观察 | 成立（§4.9）；并补充 FR-804 只要求"撤销"，故是功能缺口非规格违背 |
| M13 workspace 星号 | 低风险维护项 | 成立（§4.10-3） |
| M14 并发主链拒绝 | 保留有界单飞 | 成立 |
| M15 撤销历史扫描 | 登记性能风险 | 成立（O(n²)） |
| M16 Python 更新策略 | 保留手工冻结政策与扫描缺口 | 成立 |
| M17 changelog/terms/privacy | 登记文档义务 | 成立 |
| M18 ABA 保护 | 保留为优点 | **同意**，不得与 M8 混同后移除 |
| Z1 child exit/close 观测及活体 leaseBusy | 观测 UNKNOWN 保留 | **本轮已被新观测部分推进**：coordinator-exit 的 observer 直接记到 SIGKILL 与 exit 0/close 0。但**活体挂起风险仍为推断**，不得以有限 PID absence 反推全局 reap；且本轮发现**新的**相关缺陷（§4.1 泄漏 ⇒ 更易触发容量封顶） |
| Z2–Z10 | 分别保留 | 成立（签名/公证、redo、全量导出、损坏 SQLite HOLD、备份恢复、a11y、i18n、大文件/死代码、跨平台/参考设备） |

**总评**：处置记录**本身诚实、逐项有据**，未发现"把 owner 处置当作模型 Pass"的情形，也未发现处置与代码不符之处；M4 是本轮唯一实质性的代码修复，且本方独立验证其目标达成。**唯一需要补正的是**：处置记录把 M1/M2/M3 表述为"已处理/部分采纳"，读者易误解为缺陷已闭合——**三者客观仍为未修复缺陷**，只是表述范围被收窄。

---

## 10. 最终判定

### 10.1 当前 748008a6 / package087 —— 内部演示范围（macOS 15 arm64 未签名目录包，"非正式分发，仅限内部演示"）

**判定：BLOCK。**

**真实依据（支持"接近可用"的正面事实）**：
- 38 commits / 525 files 的累计实现，**未发现数据损坏、越权写入、凭据泄露、注入或可利用的鉴权缺陷**。
- 核心不变量全部成立（§3.2）：版本化单一提交路径、不可变历史、幂等不重放、渲染端隔离、CSP 唯一来源、固定错误码边界、无模型/遥测/云自动启用、引擎无网络出口。
- 事务与隔离边界质量高：真实 ACK 丢失零重放（有真实 Job 清单佐证）、项目切换后无任何写 IPC 外泄、原操作回执绑定真实 marker。
- 证据纪律优秀且**我逐项复算全部吻合**：whole087 单次完整 check 自然 0（35 文件 / 1694 测试 / 332 Ruff / 3445 通过 44 skip / JS build）、package087 实物闭包 **910/290/266** 与受理票逐数吻合、e2e actual002 **18 collected / 16 PASS + 2 真实平台条件 skip**（T02 两例 4.4s/4.3s）、三 SOURCE005 `faultApplied=true` 且 PASS、引擎 exit/close **本轮直接观测到**、086 首败与 087 guard 首败**均原样保留**、`BUILD-NONCE-DIFF` 对"仅一处 nonce 字面量差异"的披露**诚实且可核**。
- 748008a6 的测试改动经本方逐行判定：**真实修复 TOCTOU，未放宽任何断言**，且较原实现**更严**（新增重复区域拒绝）；与独立 postpatch 复核结论一致。

**阻断依据（为什么是 BLOCK 而不是 PASS）**：
1. **§4.1（本轮新增，High）**：M4 退役回调抛错 ⇒ 主链路投递 + IPC 投递租约**永久泄漏**，且产品路径**无重试入口**（preload 单次 ACK + 静默吞错）；累计 16 次 ⇒ **整个 project/query 面永久 `PERMISSION_DENIED`**，且全局预算永不退还。修复它**必然改码 ⇒ 产生新候选 ⇒ 本轮全部证据不可沿用**。
2. **§4.2（High，延续）**：`uncertain` 单向闩锁未修复。
3. **§4.3（Medium，延续）**：未 ACK 投递永不回收；与第 1 项共用 16 槽上限，叠加更快封顶。
4. **§4.4（Medium，延续）**：跨引擎会话后创建/示例的原回执永久不可对账。

> **不洗绿也不升格**：以上 4 项均为**源码可证的可用性/资源生命周期缺陷**，不是"证据缺口"。同时，**不得**反过来用"历史失败保留 + 局部绿"抵销 §8 的发布义务，也**不得**把 §4.1 说成"只是理论风险"——它的触发条件恰是 M4 自己要处理的"释放失败"场景。

### 10.2 正式分发 / 其他平台 / 保留 HOLD（与上条**互不抵销**）

**全部保持 HOLD，一项未关闭**：
1. 签名 / 公证 / 可分发安装产物（§4.5）。
2. 完整 legal 与 `_distutils` 归属。
3. 跨平台（Windows）/ 参考设备 / 无开发环境设备离线启动。
4. 损坏 SQLite 物理保护 HOLD。
5. D2 规模 / 负载 / 索引口径。
6. 真实 LLM 与 I06 网关正式接入（S3 前按设计不接入）。
7. 静态加密与设备失窃预案、渗透测试、正式安全问卷证据包、可访问性合规。
8. 本体/项目级导出与 Turtle 导入导出（PRD FR-002/FR-203）、CSV/XLSX 接入（FR-300）。
9. 指定双审积压、C4–C6 失败与 D8 人工裁决、CI、develop 合入、完整 release 原门。

**机械包身份通过 ≠ 正式签名/法律/全平台发布通过。** 本报告**不以**内部未签名包的绿、也不以 243 行 E2E 的绿，代替上述任何一项。

### 10.3 0/17 口径

**不变。** 仅在实际指定双审通过且 push → PR → CI → merge → 远端复核后方可改变；本轮未获推送授权，且 §4.1 的修复会产生新候选，现有 whole087 / package087 / e2e actual002 / real-runtime actual001 证据**不可沿用**到新候选。

### 10.4 建议的下一轮最小动作（不扩大范围）

1. 修 §4.1：把退役失败与投递生命周期解耦（失败只标记、不中断清理），并补一条**产品路径级**（非仅引擎级）测试断言 16 槽不被泄漏占用。
2. 把 `deliveries` 与 `#mainlineDeliveries` 的**回收责任唯一化且可达**（顺带覆盖 §4.3），并在主进程把容量封顶映射为可操作的错误而非 `PERMISSION_DENIED`。
3. 修 §4.2：为 `uncertain` 增加基于原操作证据的复位路径（**不要**简单放宽为忽略 uncertain）。
4. 删除 §4.6 的 8 处悬挂 import 与 profile 死分支，或以固定"能力不支持"错误码显式封门。
5. 完成后**重新出完整 check → 新候选 HEAD/JS → T11 新包 → 对应真实运行 → 双方各新建全新独立复审**；不得沿用本轮证据，也不得复用终态任务改旧结论。

---

## 11. 本次审查的自我限制（如实记录）

- **只读**：未修改任何产品文件、测试、配置、标准或 Git 索引；未运行新的 build / 安装 / GUI / APP / engine / 测试 / 外部请求。**唯一写入为本报告文件**（`…/20261024_t01_748008a6_package087_designated_dual_review_001/minimax/report.md`）。
- **未运行测试**：本轮**没有**执行任何测试、构建或打包；所有"绿"均指对**既有证据的独立复核**，不构成新的运行证据。按仓库规约，静态检查不替代运行证据。
- **未读对方本轮产物**：`…/20261024_t01_748008a6_package087_designated_dual_review_001/zcode/` 全程未打开；仅读取了**上一候选**已结束冻结的 085 两份历史报告与处置记录（对称上下文）。
- **子代理的自我限制**：3 条 lane（Python 引擎 / Electron 主进程 / 渲染层）返回完整结论，我对其每一条 High/Medium **均回到源码逐行复验并独立定级**——其中 1 条（8 个缺失模块）我**下调**为 Low–Medium 并给出可达性证明（§4.6），1 条（退役回调泄漏）是我**在复验中新增**的 High 缺陷（§4.1）；第 4 条 lane（证据面）长时间无产出后终止，其范围**由我在主会话逐项亲自复算**（§5 整表）。
- **N 临时 checkout 非源码 authority**：我以 **worktree 实测内容**为准（S1270 与 HEAD 树路径集完全相等、内容 1270/1270 一致），未采信临时 checkout 的 UNBORN Git 状态。
- **对历史证据只读不改写**：未触碰任何历史证据文件。

---

*报告结束。审查者未修改任何产品文件；本报告为唯一产出。*
