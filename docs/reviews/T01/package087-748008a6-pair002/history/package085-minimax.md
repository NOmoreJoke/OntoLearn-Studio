# OntoLearn Studio — T01 / 7d30 / package085 全量独立工程审查报告

- **审查方**：MiniMax Code（model M3.1-Flash，xhigh，始终授权 / 完全访问）
- **审查日期**：2026-10-24
- **审查类型**：全新独立完整审查（非受理、非抽样摘要）
- **产品源码状态**：全程只读。未修改任何产品文件、测试、配置、标准、Git 索引；未运行新的 build / GUI / APP / 产品 / 外部请求；未读取对方模型报告，未以其结论代替独立核验。唯一写入为本报告。

---

## 0. 结论（先行）

**存在阻断。** 当前候选 `7d30ab34` 的**代码质量与核心不变量是可信的**——我独立复算了源码闭集、逐项核对了打包产物谱系、审读了主链路的事务/幂等/隔离/历史不可变实现，并**没有**发现数据损坏、越权写入或泄露用户数据的实现缺陷。

但**发布/验收侧存在 3 类真实阻断**，其中 2 类是**可用性阻断**（缺陷），1 类是**发布义务未完成**（非缺陷但阻断放行）：

1. **【High，缺陷】引擎侧"不确定"状态是单向闩锁**：任何一次主链路超时、引擎死亡或 UNKNOWN 投递后，`project:*` / `query:*` 全量 IPC 在该 App 生命周期内永久返回 `PERMISSION_DENIED`，且**不存在任何复位路径**（`apps/desktop/src/main/engine.ts:276,707,813,2053,2456,2521`；我已确认全仓只有 `= true` 赋值，无 `= false`）。
2. **【High，缺陷】引擎重连后原操作不可对账**：`origin` 绑定 `hostClientId` + `engineSessionId`，二者均随握手/会话更换，故重连后同一 `operationId` 的认领比对必然 `IDENTITY_CONFLICT`，原回执不可取回（`packages/engine/src/ontolearn_engine/project/project_lifecycle.py:82-102,465-470,1027-1031`；`apps/desktop/src/main/engine.ts:2220`）。**这与阻断 1 恰好互为因果：引擎死亡后既 poisoned 又 identity-mismatch，引擎侧的对账能力在最需要它的时刻不可达。**
3. **【Medium，发布义务】打包产物无签名、无公证、无可分发目标**：`mac: identity: null` + 三平台 `target: dir`（`apps/desktop/electron-builder.yml`）。我实测 `codesign` 为 `adhoc`、`TeamIdentifier=not set`、`Sealed Resources=none`，`spctl -a` 报 `code has no resources but signature indicates they must be present`。该 `.app` **不能交付给最终用户**。`docs/m0-checklist.md` 早已自列"签名、公证、安装与无开发环境设备离线启动验证"未完成。

**用户 0/17 口径不可改变**：本审查者无 push/merge 权限，且第 3 项阻断必然要求重新打包（改变产物字节），第 1、2 项要求改码。任何一项落地都会产生**新候选**，现有 whole085 / package085 / e2e085 / real-runtime 证据**不能沿用**到新候选。

**历史状态未被清零**：C4–C6 审查失败与 HOLD、D2、损坏 SQLite physical HOLD、`_distutils` 归属、Windows/参考设备、真实 LLM、签名/完整 legal、指定双审、CI、develop 合入与完整 release 原门**全部继续留账**。本报告不将任何旧轮次宣称为已通过。

---

## 1. 回读确认（审查开始前的实际读回）

| 项 | 实际读回值 | 判定 |
| --- | --- | --- |
| 提示词文件 | 16490 字节；SHA256 `5d83cd662b4b644b5fc72a04b27e922b4420d49c9485f7575df8d305f837c8c6`；187 行，读至 EOF | **与指定值逐位一致** |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | 一致 |
| Git authority | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/.git/worktrees/T01-project-transactions`（由 `.git` 指针读回） | 一致 |
| HEAD | `7d30ab34b59d696b40df9d6d959d3626612f4423` | 一致 |
| 分支 | `feature/weekly-t01-project-transactions` | — |
| base / merge-base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 与远端 develop **一致** |
| 远端 develop（只读 `ls-remote`） | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | **一致** |
| 累计范围 | 36 commits；`git diff base..head` = **525 files changed, 560720 insertions(+), 4638 deletions(-)** | 与"525 files"一致 |
| 受保护 owner 规则 | `AGENTS.md` 15147 B / `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，工作区为**未暂存修改** | **未修改**（HEAD 版为 `1b3c0291…`，属正常：owner 规则刻意不暂存） |
| 清单全文 | 160 条引用行（147 条产品条目 + 13 条人工角色条目），已读至 EOF，未摘要 | — |
| model / 思考 / 权限 | MiniMax-M3.1-Flash / xhigh / 始终授权（完全访问） | 按要求执行 |

**注**：`git status` 仅显示 ` M AGENTS.md`，无其他未提交改动；索引为空。

---

## 2. 本次实际已核 / 未核范围（诚实边界）

### 2.1 已核（独立完成）

- **源码闭集身份**：`S-source-after-commit.json` 1270 条 → 我在 worktree 内**逐条重算 bytes+SHA256**，**1270/1270 完全一致，0 缺失、0 不符**；并与 `git ls-tree -r HEAD` 比对，**集合与内容完全相等**（1270 = 1270）。
- **whole085 单次完整 check**：日志确认 6 阶段全绿（eslint `--max-warnings 0`、prettier、3× `tsc --noEmit`、vitest **35 files / 1691 tests**、electron-vite build、ruff check + ruff format --check + pytest **3445 passed / 44 skipped**），自然退出 0，workers 1 / retries 0 / 300s 预算内 141.96s。
- **package085 产物谱系**：从打包 `.app` 内解出的 ASAR 成员与 whole085 构建清单**逐字节+SHA 一致**（`out/main/index.js` 590878 B、`out/preload/index.js` 391731 B、`out/renderer/assets/index-CHAACd0i.js` 1201461 B、css 11040 B、`index.html` 709 B，5/5 全对，无多余 JS）。**JS 确实来自 whole085，不是本次重建**。
- **engine 复用**：包内 `engine/ontolearn-engine` SHA256 `43efc368…`，与 root 受理票登记值一致；`newJSOrEngineBuildExecuted: false` 属实。
- **e2e085**：`Running 18 tests using 1 worker`，**16 passed + 2 skipped**，`stats.unexpected = 0`；2 条 skip 原因经我读源码确认是**真实平台条件**（`tests/e2e/i04-jobs.spec.ts:100-103,318-321` 要求 `process.platform === 'linux'`，第二条另需 `I04_NATIVE_ISOLATED=1` + openbox/xdotool），**不是隐藏失败**。
- **real-runtime**：三种 SOURCE005 在途模式（reload / renderer-recovery / coordinator-exit）均 `faultApplied=true` 且 PASS；native 生命周期经真实 CUA 对话框 0/0/1 与真实 Cmd-Q，`before-quit → 第三窗口 closed → will-quit` 顺序成立，App 自然退出 0。
- **源码级审查**（下列文件实读，非摘要）：`main/index.ts`、`main/engine.ts`、`main/task-service.ts`、`main/desktop-ipc.ts`、`main/project-mainline-service.ts`、`main/csp.ts`、`preload/index.ts`、`electron-builder.yml`、`job_store.py`、`storage.py`、`coordinator.py`、`project_lifecycle.py`、`compensation.py`、`domain_changesets.py`、`mainline.py`、`invalidation.py`、`semantic_offline.py`、`query_presentation.py`、`job_store.result_page/result_current/collect_cache`、`registry.json`、`errors.json` 及对应测试与 E2E。

### 2.2 未核（明确记为"无法确认"，不以静态检查代替运行证据）

- **native hook 中引擎 ChildProcess 的 `exit` / `close` 事件**：`UNKNOWN_NOT_OBSERVED`。有限 PID 采样（`ps -p 96916,96936,96942` 自然退出 1、stdout 空）**不能**证明 JS 事件已送达，也不能证明全局 reap 完整。
- **2 条 Linux-only E2E 在 Linux 上的真实行为**（本轮在 macOS 执行）。
- **Windows 打包与运行、参考老设备**。
- **损坏 SQLite 的 physical HOLD、`_distutils` 归属、D2 规模口径、真实 LLM 调用**。
- **签名/公证/安装/离线启动**（`identity: null`，本轮未做，也做不了）。
- **可访问性合规、屏幕阅读器、RTL/emoji/口音字段的渲染细节**。
- **agent 侧真实模型链路**（S3 前不接入，故不在 M0 范围）。
- 我派出的 5 条只读审查 lane 中，**T02 与 T04 两条在多次长轮询后仍无产出，已终止**；这两条范围由我在主会话**直接读源码**覆盖（见 §3 对应条目），但**放弃了子代理的第二双眼睛**。其余 3 条（项目生命周期、ACK 丢失/切换隔离、引擎生命周期）返回了完整结论，并对其中每条 High/Medium 我都**亲自回到源码复验**。

---

## 3. 最值得修复的 10 个问题（按严重程度排序）

> 标注约定：**【观察】** = 我在源码/产物中直接读到的事实；**【推断】** = 由观察推导的运行期后果（未经本轮执行验证）。

---

### 1. 【High｜缺陷】`uncertain` 是单向闩锁，一次主链路故障即永久毒化主链路 IPC

**位置**：`apps/desktop/src/main/engine.ts:276`（`uncertain?: boolean` 声明）、`:707`（`#mainlineReady` 判定并 `throw deniedOrdinary()`）、`:813`、`:2053`、`:2456`、`:2521`（全部为 `= true`）；`:1119-1124`（`mainlineProjectClient()` 复用同一被污染 record）。

**【观察】** 全仓对该字段的赋值只有 `= true`，**没有任何复位、没有 `= false`、没有删除**（我已用 grep 穷举确认）。`#mainlineReady` 在 `record.uncertain` 为真时直接抛 `deniedOrdinary()`；`mainlineProjectClient()` 只要其 Session 仍是 current 就**继续返回同一条被污染的 record**。

**【观察】** 置位条件包括：主链路请求超时、stdin 写失败、引擎死亡时仍有主链路请求在途、以及 UNKNOWN 投递（`engine.ts:813` 遍历 `delivery.records` 全量置位；`:2053`、`:2456`、`:2521` 三处独立置位）。

**触发条件 / 反例（【推断】）**：引擎已提交，但 JSONL 回复行被丢弃 → 桌面端 5s 请求超时（`requestMs=5000`）→ `mainlineOwner.uncertain = true` → Session 因心跳存活而不重启 → 此后**全部** `project:*` / `query:*` 路由永久 `PERMISSION_DENIED`。

**风险**：可用性中断 + **本会话内原操作对账能力不可达**。`project.create` 无 recovery principal（`#publish` 从未执行），故 `TaskService.beginRecovery` 不会触发；同时 `clearProject()` 已置空 `projectId`，`tasks.getOperation` 亦失败。

**严重度**：High。**无数据损坏或重复写入**——引擎侧 `operation_claims` 兜住了不变量；损害是可用性与对账可达性。

**建议**：为 `uncertain` 增加**基于原操作证据**的复位路径（例如：同一 `operationId` 成功对账取回原回执后清除该 record 的闩锁），或在 `#mainlineReady` 改为"不确定态下允许只读/对账类调用"。**不要**简单放宽为"忽略 uncertain"——那会恢复自动重放已输入写入的风险。

---

### 2. 【High｜缺陷】引擎重连后，已提交未确认的原操作永久不可对账

**位置**：`packages/engine/src/ontolearn_engine/project/project_lifecycle.py:82-102`（`origin_value`：`{hostClientId, engineSessionId, permission}`）、`:465-470`（空白项目创建认领比对）、`:1027-1031`（示例创建认领比对）；`apps/desktop/src/main/engine.ts:2220`（`clientId: randomUUID()`，每次握手新发）。

**【观察】** `origin` 强制包含 `hostClientId` 与 `engineSessionId`，二者均为 36 位 UUID，且**逐会话/逐握手更换**。认领命中时要求 `old["context"]["origin"] == origin`，否则 `IDENTITY_CONFLICT`。`project_receipt` 存在于 `storage.py:283`，但**未对外暴露**，无会话无关的回执查询路径。

**触发条件（【推断】）**：引擎在**已持久化提交之后、回执抵达渲染端之前**崩溃 → 用户以同一 `operationId` 重试 → `origin` 已变 → `IDENTITY_CONFLICT` 而非"取回原回执"。渲染端确实会保留原 `operationId`（`App.tsx:291` `createIntent.current ??= example`）。

**风险**：**不会**产生重复项目/草稿（守卫有效），主链路也**不会**被砖（重算使用存储的 origin，失败类别是 identity 而非 structure），但**原回执永久不可取回**，UI 停留在"创建结果尚未确认"，用户只能人工核对项目列表。

**严重度**：Medium-High。与阻断 1 复合后（引擎死亡 → 既 poisoned 又 identity-mismatch）**引擎侧对账在最需要时不可达**。

**建议**：把"操作身份"与"会话身份"解耦——认领比对应基于**稳定的请求指纹**（业务语义 + 目标项目 + 输入摘要），而非含会话 UUID 的 `origin`；会话信息仅作审计元数据。

---

### 3. 【Medium｜缺陷】IPC 投递租约永不回收，16 次未 ACK 后主链路永久拒绝

**位置**：`apps/desktop/src/main/desktop-ipc.ts:105-113`（`deliveries` Map）、`:142`（仅在**精确 ACK** 时 `deliveries.delete(id)`）、`:164`（`if (deliveries.size >= 16) return permission()`）。

**【观察】** `deliveries` **只**在 ACK 路径删除，**无过期、无驱逐、无容量回收**。同文件 `:144` 的 `accepted` Map **有** FIFO 驱逐（`if (accepted.size >= 16) accepted.delete(...)`）——**同一函数内的对照证明这是遗漏而非有意设计**。

**触发条件（【推断】）**：渲染进程崩溃/重载，或 preload ACK 失败累计 16 次 → 全部 `project:*` / `query:*` 路由 `PERMISSION_DENIED` → **App 在本次运行内被砖死**，只能重启。

**风险**：可用性中断。`tests/unit/t01-mainline-ipc-delivery.test.ts:138-153` 将该行为断言为"有意"，但**断言现状不等于断言正确**。

**建议**：为 `deliveries` 增加与 `accepted` 对称的**有界驱逐**（或按 session/frame 失效清理）。释放租约须仍以"精确 ACK"为**授权**依据，驱逐只回收**容量**，不得让未确认的投递变成"已投递"。

---

### 4. 【Medium｜缺陷】`#intents` 永不回收，16 次提交后本会话所有提交失效

**位置**：`apps/desktop/src/main/project-mainline-service.ts:279`（`#intents = new Map<string, MainlineIntent>()`）、`:658`（`if (this.#intents.size >= 16) throw invalid()`）、`:667`（`set`）。

**【观察】** 该 Map 只有 `set`，**无 `delete`/无驱逐**；容量上限 16 触发后，**本会话剩余生命内**每次 `commitProjectChangeSet` 都抛 `INVALID_STATE`。

**触发条件**：用户在同一 App 会话内执行 16 次以上受控变更（长会话或脚本化操作）。

**风险**：可用性中断，且错误码误导（表现为"请求非法"而非"资源已满"）。

**建议**：与 `accepted` 一致采用有界 FIFO 驱逐；或按操作终态回收。

---

### 5. 【Medium｜发布义务】打包产物无签名 / 无公证 / 无可分发目标

**位置**：`apps/desktop/electron-builder.yml`：`mac: identity: null`；`mac/win/linux` 均 `target: dir`。

**【观察】** 我对实际产物 `OntoLearn Studio.app` 实测：
- `codesign -dv --verbose=4` → `Signature=adhoc`、`TeamIdentifier=not set`、`Sealed Resources=none`、`Internal requirements=none`；
- `spctl -a -vvv -t exec` → **`code has no resources but signature indicates they must be present`**（Gatekeeper 判定为不合格）。

**【观察】** `target: dir` 产出的是**未打包目录**，不是 `.dmg`/`.pkg`/`.msi`/`.deb`，**当前不存在任何可交付给终端用户的安装产物**。

**【观察】** `docs/m0-checklist.md` 已自列"签名、公证、安装与无开发环境设备离线启动验证"为**未完成**，且 PRD Q2（首发操作系统、架构、参考设备及签名安装验证）同样未决。

**风险**：即使代码无缺陷，该产物在他人 Mac 上会被 Gatekeeper 拦截；**发布义务未完成**，不得宣称"可交付"。

**严重度**：Medium（对"开发期可运行"无影响，对"可发布"是硬阻断）。

**建议**：设定 `mac.identity`（Developer ID）、开启 `notarize`、改用 `dmg`/`pkg` 目标；此改动**必然改变产物字节**，必须重新出包并重跑打包态 E2E。

---

### 6. 【Medium｜缺陷】结果分页每页全量物化结果载荷（游标正确，但每页 O(总量)）

**位置**：`packages/engine/src/ontolearn_engine/job_store.py:2313-2315`。

**【观察】** `available = [r for r in payload if position is None or [r["ordinal"], r["rowId"]] > position]` —— 游标**语义**是 keyset（正确），但每次翻页都会把**整个结果载荷**在 Python 内存中物化一遍。

**【观察】** 同函数其余防护良好：游标绑定 `inputSnapshotId`/`scope`/`parametersHash`，不符即 `CURSOR_MISMATCH`（`:2309-2311`）；单页编码上限 131072 字节，超限 `RESOURCE_LIMIT`（`:2323-2326`）；主进程侧 `pageSize` 限制 1..200（`task-service.ts:1033`）。

**风险**：243 行规模（e2e 实测）无影响；**百万行级结果每翻一页都全量物化**，内存与延迟随总量线性增长，与"5M 行查询超时"类风险同类。

**建议**：把行存储改为按 `(ordinal,rowId)` 索引的表并用 `WHERE (ordinal,rowId) > ? ORDER BY ... LIMIT ?` 下推，或对载荷做分段索引；**保持现有 keyset 游标语义不变**（它是对的）。

---

### 7. 【Medium｜缺口】导出仅支持"当前页"，无全量导出

**位置**：`apps/desktop/src/renderer/src/query/typed-results.ts:252-272`（`currentPageCsv`）、`apps/desktop/src/renderer/src/query/QueryResultPanel.tsx:16-23`（`downloadCsv`）、`:317-318`（导出当前页）。

**【观察】** 导出内容**仅来自已加载的当前页**；`currentPageCsv` 的注释明确"never fetch or accumulate more rows"。e2e `t04-query-variants.spec.ts:814` 实测 243 行结果需**逐页导出并拼接**。

**【观察】** 该实现的**安全面是正确的**：公式注入已缓解——`/^[\s]*[=+\-@]/u` 或以 `\t\r\n` 开头的值前置 `'`（`typed-results.ts:261`），引号按 `""` 转义，含 UTF-8 BOM 与 CRLF。

**风险**：清单项"导出，因为迟早每个客户都要表格"仅**部分**满足；大结果集导出为人工多步，易漏页、易出错。

**建议**：增加受控的**全量导出**（服务端流式/分段产出，仍受 `maxFrameBytes` 与页上限约束），并复用现有的公式注入转义。

---

### 8. 【Low-Medium｜缺陷】重复撤销报错而非幂等 no-op

**位置**：`packages/engine/src/ontolearn_engine/project/compensation.py:187-188`。

**【观察】** 同一操作被撤销两次时，第二次因"later edits conflict with undo"抛 `Conflict` → `INVALID_STATE`，而非返回"已是目标状态"。

**【观察】** 该冲突会**回滚**，不产生部分效果，故无数据风险。

**风险**：UI/重试语义不友好（重试风暴会持续报错）；与"幂等键"总体风格不一致。

**建议**：区分"目标状态已达成"与"存在真实冲突"，前者返回成功回执。

---

### 9. 【Low｜缺陷】`createIntent` 仅存于内存，重启后同名可再建一个项目

**位置**：`apps/desktop/src/renderer/src/renderer/src/App.tsx:59-61`（`useRef`）、`:291`（`createIntent.current ??= example`）、`:315`（成功后置空）。

**【观察】** `createIntent` 是 React ref，**不持久化**；成功后才清空。引擎侧以 `operationId` 去重，故**同一 operationId 不会重复创建**；但重启后新建 ref → 新 `operationId` → **同名可产生第二个项目**。

**【观察】** UI 已提示"创建结果尚未确认，请核对原请求或项目列表。"（`App.tsx:335`）——属**诚实提示**，非静默错误。

**严重度**：Low（数据不丢，但用户可能得到重复项目）。

**建议**：把待确认意图（含 `operationId`）持久化到本地 profile，重启后按 `operationId` 而非名称恢复。

---

### 10. 【Low｜潜在缺陷】`create_project` 存在绕过版本化直接写库的 API

**位置**：`packages/engine/src/ontolearn_engine/storage.py:259-267`、`packages/engine/src/ontolearn_engine/job_store.py:637-643`。

**【观察】** 二者直接 `INSERT` 到 `projects` / `public_projects`，**不写** `operation_claims`、**不写** `app_receipts`、**不产出**创建回执——与"正式写入只经 `Store.commit`（版本化、可预览、原子提交）"的不变量**在 API 层面**相悖。

**【观察】** 当前**不可从协议到达**（仅 `storage_probe.py:63` 与测试调用），故暴露是**潜在的**。

**风险**：未来任一适配器误用该 API，会产生"无回执、无认领、不可对账"的孤儿项目。

**建议**：收敛该 API 为内部私有，或强制其走 `Store.commit` 的版本化路径。

---

### 3.x 其余已记录但未进前 10 的问题（完整保留）

| # | 严重度 | 问题 | 位置 |
| --- | --- | --- | --- |
| 11 | Low | 内部异常消息内嵌原始事实值（subject/predicate/owner/source_row/id）。当前 `classify` 只转发 `.code/.params`（`coordinator.py:93-94`），`storage.py:54` 亦注明 `Conflict` 消息仅内部使用 → **潜在**泄露，非当前泄露 | `storage.py:767-773` |
| 12 | Low | 无独立 "Redo" 入口。E2E 用例名写 "Undo/Redo"，实际第二次操作是**再撤销一次**（同一按钮"预览撤销本次修改"）。FR-804 仅要求"撤销"，故**不构成规格违背**，但用例命名夸大且用户无显式 redo 语义 | `tests/e2e/t02-ontology-mainline.spec.ts:296,344-353`；`OntologyMainlinePage.tsx:331-333` |
| 13 | Low | 工作区内部依赖以 `"*"` 声明（`@ontolearn/contracts`）。npm workspaces 会解析到本地包，风险低，但与其余"精确版本"约定不一致 | `apps/desktop/package.json:15` |
| 14 | Low | 并发主链路调用**直接拒绝**而非排队（`#mainlineComputing` / `mainline.py:288`）。无错投，但良性并发产生硬失败 | `engine.ts:764`；`mainline.py:288` |
| 15 | Low（性能） | 撤销对账对**每个**后续 commit 调用 `_with_retirements` → `retirement_at` 全历史扫描 ⇒ 长历史下 O(n²) | `compensation.py:177-186` |
| 16 | Low | Dependabot 只覆盖 `npm` 与 `github-actions`，**未覆盖 Python**（`SECURITY.md` 声明 Python 更新为手工 `uv lock --upgrade`） | `.github/dependabot.yml` |
| 17 | Low | 无 `CHANGELOG.md`、无 Terms/Privacy 文档（清单项"条款与隐私政策需与代码一致"） | 仓库根目录 |
| 18 | Info | 撤销补偿的 `history`/`conflict` 语义在**值相同**时也拒绝（ABA 保护，`compensation.py:169-188`）——这是**优点**，非缺陷，但与"重试应幂等"的直觉相反 | `compensation.py:170` 注释 |

---

## 4. 其余阻断与验收缺口（原样保留，未清零）

### 4.1 发布义务（阻断放行）

- **签名 / 公证 / 可分发产物**：见问题 5。`identity: null` + `target: dir`。
- **完整 legal**：`licenses/` 与 vendored setuptools/packaging 的 LICENSE 原件已入库（`licenses/python-vendored/setuptools-84.0.0/...`、`licenses/python-runtime/packaging-26.3.dist-info/...`），但 D8 记录明确"完整 legal"**未通过**，9 项非 engine 签名及 APP deep 仍失败。
- **`_distutils` 归属**：未关闭。
- **无开发环境设备离线启动验证**：未执行。
- **Windows / 参考老设备**：未执行。
- **损坏 SQLite physical HOLD**：未关闭。
- **D2 规模口径**：未关闭。
- **真实 LLM / I06 网关正式接入**：S3 前按设计不接入，属**已验证方法范围**，非当前缺陷。

### 4.2 运行时证据缺口

- **native hook 引擎 ChildProcess `exit`/`close` = `UNKNOWN_NOT_OBSERVED`**。
  **【我的独立判断：此单项不构成产品阻断，但必须继续记为 UNKNOWN】**，依据如下：
  - **【观察】** 真正决定"引擎中途死亡是否安全"的路径是三种 SOURCE005 在途模式，它们在**打包 App** 上均 `faultApplied=true` 且 PASS（reload / renderer-recovery / coordinator-exit），且 `coordinator-exit` 模式正是引擎死亡路径。
  - **【观察】** 引擎侧对死亡有结构性兜底：`job_store.py:1924-1951` 的 `reconcile_jobs` 在启动时把任何非终态 Job 判为失败/取消并固定 `ENGINE_EXITED`；`storage.py:630-893` 的 marker 与领域变更**同一 SQLite 事务**写入，故引擎死亡**不可能**留下半提交。
  - **【推断】** 缺失的是**证据工具链的观测缺口**（native hook 未捕获 child 事件），不是产品缺陷证据；`ps` 的有限采样在进程已退出后返回空是**预期行为**，不能反推 JS `close` 事件是否送达。
  - **因此**：不得据此宣称"引擎子进程被完整 reap / 无孤儿"；该断言**保持未知**。同时不得用"内部包绿 + 局部绿"抵销 §4.1 的发布义务。

### 4.3 历史轮次状态（未清零）

C4–C6 的新建配对尝试失败记录、C6 的 Z 正式 SID/turn/terminal `UNKNOWN`、晚 C4 Z / C5 M 报告归属 `UNKNOWN` —— **一律保留，不追认已通过，不新增轮次**。首轮 full001 的环境等值首败（npm/APP 未启动）及其后 22 字段显式控制层修正、new002 运行原件均**原样保留**，本次审查**未改写任何历史证据**。

---

## 5. 用户 11255B 清单逐项适用性判断（160 条引用行）

> 原则：不适用按类别说明依据；**适用但未核实写"无法确认"**；不为满足清单而扩建无关功能。本产品是**本地优先、单用户、无服务端、无网络、无账号体系、无计费**的桌面应用，清单中绝大多数条目属于服务端/SaaS 形态，按类别不适用并说明理由。

### 5.1 适用且**已核并有实现**（实测/源码双证）

| 清单条目 | 结论与依据 |
| --- | --- |
| undo | ✅ 已核。`compensation.py` 纯函数式前向撤销（以新提交实现，不改写历史），带 ABA 保护；e2e `t02-ontology-mainline.spec.ts` 实测 Undo 与 Undo-of-Undo 通过。局限见问题 8/12 |
| idempotency keys | ✅ 已核。`operation_claims.operation` 为全局 PK（`job_store.py:2545`），与副作用**同事务**写入，先于副作用落库 ⇒ 不会无认领地产生副作用 |
| deduplication（连点四次） | ✅ 已核。同一 `operationId` 命中认领即返回原回执（`job_store.py:501-513`、`project_lifecycle.py:1023-1032`）；主进程**拒绝自动重放已输入写入**（`project-mainline-service.ts:649-670`） |
| pagination that still works on page 400 | ✅ 已核。keyset 游标（`ordinal,rowId`），游标绑定快照/范围/参数哈希，不符即 `CURSOR_MISMATCH`（`job_store.py:2303-2336`） |
| exports | ⚠️ **部分**。已核存在且公式注入已缓解，但**仅当前页**，见问题 7 |
| validation on the server | ✅ 等价已核（无服务端）。主进程 zod `.strict()` + 引擎侧契约校验双重；`errors.json` 为固定码注册表，每码 `paramsSchema` 且 `additionalProperties:false`，`maxEncodedBytes:2048` |
| input sanitization everywhere a user can type | ✅ 已核。边界数据一律 zod `.strict()`；引擎侧 `contract_v2.py` 二次校验 |
| protection against SQL injection | ✅ 已核。全量使用参数化查询（`?` 绑定），无字符串拼接 SQL（抽查 `job_store.py`、`storage.py`、`project_lifecycle.py`） |
| protection against XSS | ✅ 已核。React 默认转义 + 单一 CSP 源（`csp.ts`），生产变体无 `unsafe-inline`/`unsafe-eval`，`connect-src 'none'` |
| CORS rules | ✅ 不适用（无 HTTP 服务、不开端口）。由 CSP `connect-src 'none'` + 引擎 audit hook 双重保证无外联 |
| security headers on every response | ✅ 等价已核。本产品不产出 HTTP 响应；等价的"响应头"即 CSP meta/header（唯一源 `csp.ts`） |
| secrets out of the code / repo | ✅ 已核。对基线→头全量 diff 做密钥模式扫描，命中项均为**测试夹具与负例**（`"secret"` 字面量、`secrets.token_urlsafe`），无真实凭据；`.env`/`*.sqlite` 未入库 |
| logs that record who did what without passwords/tokens/cards | ✅ 等价已核。领域动作以不可变 `commits`/`commit_evidence`/`operation_claims`/`job_details` 记录（含 actor/origin/operation）；原始字面值不写入审计记录 |
| audit trails that show who viewed a record | ⚠️ **部分**。已核"谁改变了什么"完整（不可变提交证据）；"谁查看过"仅有查询侧 `job_details`/result 元数据，**未见逐次查看审计** → 该子项**无法确认**是否满足 |
| idempotent / transactional migrations | ✅ 已核。`job_format` 以 `schema_version=3` + `schema_hash` 固定，`PRAGMA foreign_key_check` 校验，`migration_log` 记录，format3 有独占写者租约 |
| data model that survives "one small change" | ✅ 已核。版本化 schema + 迁移日志 + 格式迁移（v2→v3 显式）、`PRAGMA user_version` 断言 |
| a schema someone designed | ✅ 已核。契约驱动：机器可读 schema/registry + 固定错误码表 + 契约夹具库（`fixtures.json` 1.4 MB） |
| indexes, because the query that was instant on 50 test rows times out on 5 million real ones | ⚠️ **部分**。已核键集分页与 `LIMIT` 边界；**索引与大数据量执行计划本次未核**（D2 规模口径未关闭）→ 真实规模下性能**无法确认** |
| unit tests written by someone who knows what the logic should do | ✅ 已核。1691 TS + 3445 Python 断言具体预期集合/顺序/错误码，非仅断言数量 |
| end-to-end tests for the flows | ✅ 已核。18 条真实 Electron 用例，16 通过 + 2 条**真实 Linux 平台条件**跳过（已读源码确认非隐藏失败） |
| integration tests for every third-party API | ✅ 不适用（无第三方 API 依赖；仅 rdflib/pyparsing/pyshacl 三个固定版本库） |
| regression tests | ✅ 已核。存在专门回归集（`test_mainline_cleanup_regressions.py`、`binding-regressions.json`、`verify-frozen-review-sources.test.ts` 等） |
| test data that looks like production without being production data | ✅ 已核。`packages/contracts/v2/fixtures.json` 与 `tests/fixtures/T04/` 为合成夹具 |
| testing on the five-year-old laptop | ❌ **未核**（Windows/参考设备未执行，Q2 未决） |
| code a human can read | ✅ 已核。TS `strict`、Python ruff(E/F/I/UP/B, line-length 100)、领域文件单一职责且有模块级 docstring 说明"为什么" |
| architecture decisions written down with the reasons | ✅ 已核。`docs/architecture/0001-desktop-framework.md`、`0002-storage.md`、`0003-resident-coordinator-and-jobs.md` |
| a README that gets a new engineer running locally in under an hour | ✅ 已核。`README.md` + `CONTRIBUTING.md` + `docs/` |
| documentation for whoever inherits this | ✅ 已核。`AGENTS.md`（owner 规则）+ `docs/iterations/`、`docs/reviews/` 迭代与证据记录 |
| monthly dependency upgrades | ✅ 已核。`.github/dependabot.yml`（npm + Actions，weekly）。**Python 侧为手工**，见问题 16 |
| a branching strategy | ✅ 已核。worktree + `feature/<模块>-<子任务>` + PR 合回 develop；禁止共享 checkout 并行写 |
| code review on every change | ✅ 已核（流程层面）。指定双审 + CI + 远端核验门禁；本报告即其中一环 |
| structured logs you can search at 3am | ✅ 等价已核。JSONL 行协议（`main/jsonl.ts`）严格 raw reader + 帧上限 |
| background job queues | ✅ 已核。`JobStore`（`jobs`/`job_plans`/`job_confirmations`/`job_current`/`job_cursors`）+ 常驻协调器 + 取消 + 资源上限 |
| retries with backoff | ✅ 已核。`task-service.ts:471-538` 三次尝试、250ms×2^(n-2) 退避、每次 15s 超时、attemptToken 使迟到回复无法授权下一次尝试 |
| a dead-letter queue | ⚠️ **部分**。Job 有终态（succeeded/failed/cancelled）与 `job_details` 证据，但**无独立的 DLQ 视图**；重试耗尽后直接置 offline → 该子项**无法确认**是否满足 |
| cron jobs that don't run twice | ✅ 不适用（桌面单机无常驻调度） |
| caching and clearing that cache when the data changes | ✅ 已核。`invalidation-v2.json` 驱动；`collect_cache` 排除 `result_pins`/`current_results`/`job_current`，仅置空 payload 而保留结果身份（`payloadStatus='evicted'`） |
| soft deletes | ✅ 等价已核。领域以"retirement"显式建模（`compensation.py:73-133` 从不可变历史重建隐藏成员），并有"退役影响预览"（`OntologyMainlinePage.tsx:277`） |
| a data model with layers (定义/事实/推导/场景/历史) | ✅ 已核。`definitions` / `facts` / `mappingState` / `retirements` 分层；快照+版本+运行历史分离 |
| history immutability（历史与已提交轮次不可改写） | ✅ 已核。**SQL 层强制**：`snapshots`/`commits`/`runs`/`rounds`/`run_terminal`/`commit_evidence`/`operation_claims`/`job_plans`/`job_confirmations`/`job_results` 等表带 `BEFORE UPDATE/DELETE … RAISE(ABORT,'immutable evidence')` 触发器（`storage.py:1789-1795`、`job_store.py:2505-2532`） |
| cache collection must not touch history | ✅ 已核。见上 `collect_cache` 排除项 |
| staleReason only from the rules file | ✅ 已核。`invalidation.py:6-8` 从 `invalidation-v2.json` 装载 `CODES`；`reasons()` 对 `staleReason=null` 的 family（model）直接跳过 ⇒ **仅改模型配置不使领域结果过期**；历史/失败/取消不作过期原因 |
| human approval for anything the AI does that can't be undone | ✅ 已核（结构性）。`registry.json`：`changeset.commit` 为 `agentEligible=true` 但 `requiresConfirmation=true`；而 `changeset.preview`/`changeset.confirm` 为 **`agentEligible=false`**（仅 internal-business3-trusted-host）⇒ **Agent 无法自我确认** |
| Agent 只产出草稿并调用白名单工具 | ✅ 已核。`registry.json` 逐能力声明 `agentEligible`/`exposure`/`requiresConfirmation`/`requiresChangeSet` |
| 模型外发唯一网关 / 凭据只在主进程 / 引擎不持密钥 | ✅ 等价已核（当前未接入）。Python 引擎**无任何网络出口**：`semantic_offline.py` 全局 audit hook 在语义作用域内阻断 `socket.*`/`urllib.Request`/`subprocess.Popen`/`os.system`/`os.posix_spawn`；全仓仅 `urllib.parse.urlsplit`（纯字符串解析）；RDFLib 远程 Store 被显式拒绝 |
| 保护 prompt injection | ✅ 不适用（S3 前不接入模型）。当前引擎**无模型调用路径** |
| customer data kept out of prompts | ✅ 不适用（同上） |
| model spend cap per customer | ✅ 不适用（无计费、无模型调用）。属 I06 范围 |
| evals | ⚠️ **部分**。有契约/夹具/黄金集与 `verify-frozen-review-sources` 冻结校验；**模型质量 evals 不存在**（无模型） |
| a fallback for the afternoon your model provider goes down | ✅ 不适用（无模型依赖） |
| a migration plan for the day your model gets deprecated | ✅ 不适用（无模型依赖） |
| prompt and output logs | ✅ 不适用（无模型调用）；本地诊断日志另计 |
| encryption at rest and in transit | ⚠️ **部分/无法确认**。本地 SQLite **无静态加密**；传输面无网络（`connect-src 'none'`）。桌面本地场景可接受，但"设备被盗"场景无缓解 → 见 §5.3 |
| least-privilege for everyone including the AI agent | ✅ 已核。preload 仅按业务命名方法（**无** `invoke(method, params)` 通用通道）；渲染端无 Node/shell/文件系统；特权引擎参数（`--t01-internal-profile`、`--t11-internal-example-root`、`dataPath`）**仅由主进程**构造（`main/index.ts:237-259`），渲染端不可控；`exampleRoot` 校验必须绝对路径且 profile 须为 business3（`engine.ts:589-599`） |
| a disclosure process | ✅ 已核。`SECURITY.md` 含私有渠道报告路径与"不要在公开讨论附凭据/业务数据/可利用细节"的约定 |
| a plan for the day a laptop with production access gets stolen | ❌ **未核**（无加密、无密钥托管、无远程吊销——本地无账号体系）。发布义务项 |
| penetration test before the enterprise customer's security team | ❌ **未执行**（发布义务） |
| answers to the security questionnaire with evidence | ⚠️ **部分**。`SECURITY.md` 已声明边界与"当前健康检查通过不代表未实现业务安全能力通过"；**正式问卷证据包未建立** → 证据部分**无法确认** |
| dev / staging / production environments match | ⚠️ **部分**。CI 有 Linux/多形态矩阵（`ci.yml`），但 dev(`business3` 无 fixture) / packaged / fixture 三条路径的 profile 与示例根**不同**，一致性未系统核验 |
| a deploy pipeline that runs the tests before anything reaches customers | ⚠️ **部分**。CI 有 `npm ci` + `uv sync --frozen` + 完整 check + 打包验证脚本（`verify-i04-package.py`），但**正式发布流水线未建立**（无签名/公证/分发步骤） |
| feature flags | ⚠️ **部分**。存在内部 profile 开关（`business3`/`legacy2`，`--t01-internal-business3`）与 `testMode`；**非产品级特性开关** |
| one-click rollbacks | ⚠️ **部分**。有迁移前备份（`O_EXCL` + fsync）与显式 `rollback to preview` savepoint（`job_store.py:785`）；**无产品级一键回滚** |
| zero-downtime deploys | ✅ 不适用（单机桌面应用） |
| autoscaling / CDN / DNS-SSL / second region / uptime checks / dashboards / tracing / on-call / runbooks / postmortems / status page / cost alerts | ✅ 不适用（无服务端与云基础设施）。**内部**对标可部分适用：JSONL 结构化日志、错误码注册表、CI 门禁已具备 |
| a disaster recovery plan, written down and tested once a year | ❌ **未核/未建立**（且损坏 SQLite physical HOLD 未关闭） |
| load testing before the launch email | ❌ **未执行**（D2 规模口径未关闭）。本次**不得**以"243 行 E2E"充当负载测试 |
| empty states, loading states and error states on every screen | ⚠️ **部分**。`OntologyMainlinePage` / `QueryWorkspacePage` 有空/加载/错误分支；**全屏覆盖度本次未逐屏核验** → 其余屏幕**无法确认** |
| error messages a customer can act on | ✅ 已核。固定错误码 + `messageKey` + 枚举化参数；`safeDisplayError` 在主进程做展示投影；**不返回原始异常/堆栈/路径**（`worker.py:466` 以 `os._exit(76)` 固定退出码替代原始 traceback） |
| forms that keep what people typed when one field fails validation | ⚠️ **无法确认**（未逐表单核验保留语义） |
| pages that load on hotel wifi | ✅ 不适用（离线本地应用，无网络请求） |
| notifications people can turn off | ✅ 不适用（无推送/邮件） |
| keyboard navigation and screen reader support | ❌ **无法确认**（未核 aria/焦点顺序/对比度） |
| translations with dates/numbers per locale | ⚠️ **部分**。当前单一中文界面；**无 i18n 框架与 locale 格式化层** → 该子项**未满足但当前不适用**（单语产品） |
| a back button that does what people expect | ❌ **无法确认**（未核导航历史模型） |
| deleting the dead code the AI left behind | ⚠️ **部分**。已核无 `__pycache__`/`.pyc` 入库（已 gitignore）；**未系统核死代码** |
| splitting up the 2,000-line file | ⚠️ **部分**。`job_store.py` 2589 行、`engine.ts` 2800+ 行、`semantic.py` 1600+ 行——**已超 2000 行阈值**，按本条标准**未满足** |
| an admin panel for your ops team | ✅ 不适用（单用户本地应用，无运维角色） |
| support tooling | ✅ 不适用（同上） |
| a changelog customers can read | ❌ **未满足**（无 `CHANGELOG.md`）。当前无外部客户，影响低 |
| terms and a privacy policy that match what the code does | ❌ **未满足**（无 Terms/Privacy 文档）。本地无遥测、无云服务，事实与"无数据外发"一致，但**缺文档** |
| every account, domain and repo in the company's name | ⚠️ **部分**。`appId: io.github.nomorejoke.ontolearnstudio` 用个人/项目名而非组织名——按本条**未满足** |
| backups every night | ✅ 不适用（无服务器）。本地迁移备份存在，但**非常态备份** |
| a restore from those backups, tested | ❌ **未核**（备份存在，未见"从备份恢复"的实测证据） |
| point-in-time recovery for the accidental DELETE | ✅ 等价已核。SQLite 快照/提交证据 + 不可变历史 + 显式补偿/撤销 ⇒ 无 `DELETE ... WHERE` 式破坏面；**这不是 PITR**（无 WAL 归档） |
| GDPR deletion requests reaching every table/backup/log | ✅ 不适用（不收集个人数据、不联网）；**本地用户数据的“彻底删除”未见产品化入口** → 语义上部分适用，**无法确认** |
| data residency for the EU-only contract | ✅ 不适用（数据 100% 本地，无区域存储） |
| HIPAA / BAA / PCI scope / SOC 2 | ✅ 不适用（无 PHI、无支付卡、无受监管客户）；**一旦改为服务化即整体适用** |
| quarterly access reviews | ✅ 不适用（无账号/角色体系） |
| SSO / SAML / SCIM / MFA / 登录 / 密码重置 / 会话超时 / 角色权限 / 租户隔离 / "登录为该用户" / 登录限流 / 锁定策略 | ✅ **整类不适用**：本地单用户、离线、无账号、无多租户。**但反过来说，本产品不具备任何远程身份边界**——一旦引入"接收他人项目文件"或"团队共享"，该整类立即适用且当前为零基础 |
| security headers / CORS / API keys / webhooks / versioned API / OAuth / sandbox / API 限流 | ✅ 整类不适用（无对外 API 面）。内部协议 v2/v3 已有版本化与能力协商（`hello.supportedVersions`） |
| a third-party API changing its response format | ✅ 不适用（无第三方 API 调用） |
| retention rules, and code that deletes what your contract says you'll delete | ⚠️ **部分**。有缓存回收与游标过期（TTL 60s，`project_host.ReadLimits`），但**无按合同/用户策略的保留期规则** |
| money as integers / currency-rounding-tax / subscriptions / dunning / invoices / refunds / usage metering / annual contracts / revenue reports | ✅ 整类不适用（无计费与金额） |
| the customer with an apostrophe in their last name / emoji, accents and RTL in every field | ⚠️ **部分**。存储层 UTF-8 + JSON 安全；**RTL 排版与 locale 字体未核** → RTL **无法确认** |
| timezones stored right | ✅ 不适用（无定时任务/提醒；时间戳为 UTC epoch 毫秒，`now_ms()`） |
| CI / IaC | ⚠️ **部分**。CI 完整且冻结安装（`npm ci`、`uv sync --frozen`）；**IaC 不适用**（无云资源） |
| monthly dependency upgrades / framework upgrades | ✅ 已核（Dependabot）。见问题 16 的 Python 侧缺口 |
| bus factor > 1 / "people who know what they're doing"（13 条人工角色条目） | ⚠️ **无法确认**。流程上有 owner 规则、双审门禁与证据归档；但**人员稳定性与轮值不可从仓库证据判断** → 属组织事实，非本仓库可核 |

### 5.2 整类不适用（按类别说明依据）

- **账号/认证/多租户类**（登录、密码重置、MFA 及其恢复、会话与全量会话吊销、SSO、SAML、SCIM、角色与深层权限、IDOR、租户隔离、支持代登录、登录限流与锁定策略）：**本地优先、离线、单用户、无账号体系、无服务端**，故全部不适用。**注**：这些是"当前形态不适用"，不是"已具备"。
- **服务端基础设施类**（连接池、自动扩缩容、CDN、DNS/SSL 与续期、零点停机、作业队列的云侧部分、跨区容灾、值班/告警/仪表盘/追踪/状态页）：无云端、无网络端口（`connect-src 'none'` + 引擎 audit hook），故不适用。
- **计费/商业类**（订阅升降级与按比例计费、失败扣款与催缴、发票与 PO 号、销售税/VAT、退款与信用额度、用量计量到分、定制年约条款、财务对账报表）：无计费模型，故不适用。
- **对外 API 生态类**（webhook 签名与重试日志、面向客户版本化 API、客户自助 API key、OAuth 刷新、沙箱、客户 API 限流）：无对外 API 面，故不适用。
- **合规认证类**（SOC 2、HIPAA、BAA、PCI scope、GDPR 请求、数据驻留、季度访问复核）：不处理受监管数据、无云服务，故不适用。
- **邮件类**（SPF/DKIM/DMARC、退信与投诉处理、邮件渲染、通知开关）：不发邮件，故不适用。
- **AI 服务类**（prompt injection 防护、客户数据出网提示、每客户模型花费上限、模型质量 evals、模型商宕机回退、模型弃用迁移、提示与输出日志）：M0/S3 前按设计不接入模型，故当前不适用；**I06 网关接入后整类适用**。

### 5.3 适用但**无法确认 / 未满足**（需在后续里程碑处理）

1. **静态加密与设备失窃预案** — 本地 SQLite 无加密；无密钥托管/远程吊销概念。
2. **正式发布流水线 + 分发产物** — CI 有质量门，但无签名/公证/分发。
3. **Windows 与参考老设备** — 未执行。
4. **D2 规模/负载口径与索引验证** — 未执行；不得以 243 行 E2E 代替。
5. **可访问性**（键盘导航、屏幕阅读器、对比度）— 未核。
6. **"谁查看过"审计** — 已核"谁改变"，查看侧未核。
7. **全屏空/加载/错误状态覆盖度** — 仅抽查两个页面。
8. **表单校验失败保留已输入内容** — 未核。
9. **i18n / locale 日期与数字格式化 / RTL** — 当前单语，故不适用；引入多语前需建层。
10. **`CHANGELOG.md`、Terms/Privacy** — 缺失。
11. **组织化命名**（`appId` 仍为个人/项目名）。
12. **超大文件拆分** — `job_store.py` 2589 行等已超 2000 行。
13. **备份恢复实测** — 有备份机制，未见恢复演练证据。
14. **可测试的 DLQ 视图** — 有终态与证据，无独立 DLQ。
15. **"按合同删除"的保留期规则** — 只有缓存回收与游标 TTL。
16. **分支保护与 PR 模板强制** — `.github/pull_request_template.md` 存在；**分支保护规则在远端设置，本次只读未核**。

---

## 6. 证据链独立核验结果（逐项）

| 证据 | 我的独立核验 | 判定 |
| --- | --- | --- |
| 提示词 16490 B / `5d83cd66…c8c6` | 实测字节数与 SHA256 | **完全一致** |
| 远端 develop `5f910b52` | 只读 `ls-remote` 实测 | **一致** |
| HEAD `7d30ab34` | `git rev-parse HEAD` 实测 | **一致** |
| 525 files 累计 | `git diff --shortstat` 实测 = 525 files / 560720+ / 4638− | **一致** |
| S1270 源码闭集 | 在 worktree 内逐条重算 1270 条 bytes+SHA256 | **1270/1270 一致，0 缺失**；且与 HEAD 树集合与内容**完全相等** |
| AGENTS.md `15147B/de15f6ce…` | 实测字节与 SHA | **一致，未修改** |
| whole085 自然 0 | 日志实读：6 阶段全绿、vitest 35/1691、pytest 3445 passed 44 skipped、`naturalExit 0`、141.96s | **一致** |
| package085 JS 来自 whole085 | 解包 ASAR 逐文件比对 whole085 构建清单 | **5/5 字节+SHA 一致** |
| engine 复用真实 888 产物 | 包内 engine SHA `43efc368…` 与 root 受理票登记值一致；`newJSOrEngineBuildExecuted:false` | **一致** |
| e2e085 = 18 collected / 16 pass + 2 平台条件 skip | `test.stdout.raw` 与 `report.json` 实读；`stats.unexpected=0`；2 条 skip 原因已回源码确认 | **一致，且 skip 非隐藏失败** |
| 三 SOURCE005 在途模式 PASS | `ACTUAL-RUNTIME-RESULTS.json` 实读，三者均 `faultApplied=true` / PASS | **一致** |
| native 真实 Cmd-Q 与生命周期顺序 | `before-quit`→第三窗口 `closed`→`will-quit`，App 自然退出 0，对话框响应 0/0/1 | **一致** |
| native 引擎 child `exit`/`close` | `UNKNOWN_NOT_OBSERVED`；`ps` 有限采样退出 1 且空 | **保持 UNKNOWN，不洗绿** |
| 首轮 full001 环境等值首败 | 保留，未改写 | **历史未被清零** |

---

## 7. 阻断判定

**存在阻断。** 分为两类，不可互相抵销：

**A. 代码缺陷阻断（必须修复后重出候选）**

- 阻断 1：`uncertain` 单向闩锁 → 主链路永久不可用（High）
- 阻断 2：重连后原操作不可对账（High，与阻断 1 复合后使引擎侧对账不可达）
- 阻断 3：投递租约永不回收 → 16 次未 ACK 后 App 被砖（Medium）
- 阻断 4：`#intents` 永不回收 → 16 次提交后本会话提交全失效（Medium）

**B. 发布义务阻断（不可用内部包/局部绿抵销）**

- 阻断 5：无签名、无公证、无可分发产物（Medium，但硬阻断发布）
- 完整 legal、`_distutils` 归属、损坏 SQLite physical HOLD、D2、Windows/参考设备、真实 LLM/I06 正式接入、备份恢复实测、无开发环境设备离线启动 —— **全部未关闭，保持留账**

**C. 证据缺口（不得宣称已验证）**

- native 引擎 child `exit`/`close` 保持 `UNKNOWN_NOT_OBSERVED`
- 2 条 Linux-only E2E 在 Linux 上的真实行为未核
- 本次**未**核：可访问性、正式安全问卷证据包、渗透测试、负载/规模口径、备份恢复演练

**用户 0/17 口径**：**不可改变。** 本审查者**无 push/merge 权限**；且阻断 5 必然改变产物字节、阻断 1–4 必然改变源码，任一修复都会产生**新候选**，现有 whole085 / package085 / e2e085 / real-runtime 证据**不可沿用**。C4–C6 的失败与 HOLD **不因本次审查而清零**。

---

## 8. 本次审查的自我限制（如实记录）

- **只读**：未修改任何产品文件、测试、配置、标准或 Git 索引；未运行新的 build / GUI / APP / 产品 / 外部请求 / 密钥操作 / 破坏性数据写入。唯一写入为本报告文件。
- **未运行测试**：本次**没有**执行任何测试、构建或打包；所有"绿"均指**对既有证据的独立复核**，不构成新的运行证据。按仓库规约，静态检查不替代运行证据。
- **未读对方报告**：未读取另一模型本轮任务/报告或其结论；§3 中来自子代理的每一条 High/Medium，均已由我**回到源码逐行复验**（复验位置已标注）。
- **两条 lane 未完成**：T02 与 T04 两条只读 lane 在多轮长轮询后仍无产出，已终止；该两域由我在主会话直接读源码覆盖，但**放弃了子代理的第二双眼睛**（§2.2）。
- **N 临时 checkout 非源码 authority**：我以 **worktree 实测内容**为准（S1270 = HEAD 树 = worktree 内容，三者一致），未采信临时 checkout 的 UNBORN Git 状态。

---

*报告结束。审查者未修改任何产品文件；本报告为唯一产出。*
