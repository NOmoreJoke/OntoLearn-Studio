# OntoLearn Studio — T01 / 748008a6 / package087 全新独立完整累计工程审查报告（ZCode）

- 审查者：ZCode，Start Plan / GLM-5.3 / 最高思考 / 完全访问（回读自任务书第 25 行与本会话实际运行环境）。
- 候选：HEAD `748008a6a15091e8c5376b53a9348002eee7a207`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`（2026-10-24 本轮 parent 侧只读 ls-remote 已实核 origin/develop；本审查遵守"不运行外部请求"，未再次发起 ls-remote）。
- 范围：base→HEAD 全部 38 提交 / 525 文件累计变更（`git diff --stat` 实测 561,064 insertions / 4,638 deletions），非仅最后两提交；产品实现、源码、测试、配置、标准、Git 索引与既有证据只读核验；未运行新 build/安装/GUI/APP/engine/测试/外部请求，未修改任何产品文件。
- 唯一写入物：本 report.md。

## 0. 结论（先行）

1. **当前内部演示实现（macOS 15 arm64 无签名目录包，用户明确"非正式分发，仅限内部演示"）：PASS。** 依据：产品代码内未发现新的阻断级实现缺陷；whole087 单次完整 check 自然 0（35 TS 文件 1694 测试全过、332 Ruff、3445 pytest 过/44 原_skip、JS build 完成）；package087 机械包身份/资源闭包通过（ASAR 内 main 与 whole087 六处哈希一致，engine 复用真实 888ac577 组件未重建）；真实运行 18 例收集=16 PASS + 2 例原 macOS 平台条件 skip（i04 两例为 Linux 专属 fixture，源码条件非本轮回避），T02 两例完整 PASS（4.4s/4.3s）闭环了 086 的 UI 失败；SOURCE005 三例真实故障（reload/renderer-recovery/coordinator-exit）均 PASS 且无 NOT_EXERCISED；native 真实死循环/真实原生对话框 0/0/1/真实 Cmd-Q/beforequit4→windowclosed5→willquit6/engine exit0+close0 seq7/8 本次均获直接观测。上一轮 M4（第 17 个正常新 commit 被拒）已按批准方案正确修复并有 17 次真实提交回归。
2. **正式分发与其他平台：BLOCK（保留 HOLD，不因内部包清零）。** 至少：签名/公证/身份（deep codesign exit 1 ×9、signedReleaseGate=false）、wholeAPP legal/_distutils 来源闭包（ROOT acceptance 明示 `legalFullClosureAccepted:false`、`mechanicalClosureOnly:true`）、Windows/跨平台/参考设备/D2、损坏 SQLite 修复授权（B/C 未定）、用户级备份/恢复实测、a11y、D8 人工裁决。机械包身份通过不等于 formal 签名、法律或全平台发布通过。
3. **0/17 口径不变。** push→PR→CI→merge→远端复核均未发生，本审查者无推送/合并权限；本次双审通过与否由 parent 汇总，不由本报告自宣。
4. 历史失败全部保留：086 的 1 failed/6 notrun UI 失败、actual001 首次外部 guard 失败（globalHEAD 误留 dd21、0 产品用例）、C4–C6 三次配对失败、D8 决策书、旧 085 的 `UNKNOWN_NOT_OBSERVED`——均未被本轮绿证据"洗白"，仅按事实注明当前包新增的直接观测。

## 1. 受理回读核验（全部实测，非引用任务书）

| 项 | 声明 | 实测 | 结果 |
| --- | --- | --- | --- |
| prompt.txt | 20616B / SHA256 `76c7eeca…c6fec41c` | `wc -c`=20616，`shasum -a 256` 一致；全文读至 EOF，含 11255B 原清单 160 引用行（147 产品 + 13 人员角色口径与历史处置记录一致） | ✅ |
| 仓库绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | `pwd` 一致 | ✅ |
| HEAD | `748008a6…a207` | `git --no-optional-locks rev-parse HEAD` 一致 | ✅ |
| base | `5f910b52…47f3` | `cat-file -t` = commit 存在 | ✅ |
| Git authority | `本体/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `rev-parse --git-dir` 一致 | ✅ |
| 提交/文件数 | 38 commits / 525 files | `rev-list --count`=38；diff --stat=525 files | ✅ |
| AGENTS.md overlay | 15147B / `de15f6ce…a5c8c4` | 实测一致；未触碰（工作树唯一 M 项保持原样） | ✅ |
| 索引 | 173116B / `0bd0667b…7b119e`；cached diff 空 | 实测一致；`diff --cached --stat` 0 行 | ✅ |
| S-source 闭集 | 223577B / `ebf3328e…c252892` | 实测一致；1270 条；抽样 5 条（engine.ts、project-mainline-service.ts、storage.py、t02 spec、csp.ts）记录哈希与磁盘 `shasum` 全部吻合 | ✅ |
| 历史两报告（7d30/package085，允许读） | minimax 50711B/`8d6c72a6…`、zcode 33258B/`540dbaa4…` | 实测一致后阅读；未读取本轮 `minimax/` 任何内容 | ✅ |
| 意见处置 | `review-opinion-treatment.md` 10836B | 已读全文并独立复核 M1–M4 处置（见 §3.3） | ✅ |

所有 Git 读命令均带 `--no-optional-locks`。任务书要求的"先回读再执行"已完成，本轮直接进入完整审查。

## 2. 证据链独立核验（五链，全部只读）

### 2.1 whole087 单次完整 check（`outputs/20261024_t01_t02_receipt_observation_fix_001/whole087/`）

- ENTRY.json：HEAD=748008a6、parent=dd21ab12、changedPaths 仅 `tests/e2e/t02-ontology-mainline.spec.ts`；source1270 与 runtime1270 同为 223577B/`ebf3328e…`（N checkout 与提交源一致）；index/AGENTS 哈希与我实测一致。
- check-full-087.log（21634B）+ receipt（naturalExit 0，argv=`npm run check`，153.76s）：eslint `--max-warnings 0` 通过、prettier 全过、三级 typecheck 通过、**vitest 35 文件 / 1694 测试全过**（log 133–134 行）、JS build 完成、Ruff 332、**pytest 3445 passed / 44 skipped（133.63s）**。
- BUILD-NONCE-DIFF.json：oldMain 594342B/`847fa7e5…` → newMain 594342B/`83d82b19…`，唯一差异为既有构建配置 `randomBytes(18)` 开发 CSP nonce 的 24 字符字面替换（`electron.vite.config.ts:7`），`allOtherMainBytesEqual:true`、`remainingFourOutputsEqual:true`、`requiresFreshExactPackage:true`。**诚实性确认**：`buildTimeProvenance` 明示 JS 构建发生在 dd21+仅 T02 测试 WIP 时点、check 后 748 原样提交一叶——即不能声称 JS 在 748 重新 build；本报告按此口径表述。

### 2.2 package087 真实打包（`outputs/20261024_t11_package087_actual_001/` + ROOT acceptance）

- ENTRY：sourceHEAD=748008a6、四阶段（guard-before/PACKAGE/guard-after/POSTFLIGHT）全部 naturalExit 0、package:dir 2.05s、attempts 1 / retries 0。
- package-readback.json（1.5MB，errors:[]，staticMechanicalChecksPassed:true）：ASAR 866 条目（819 文件）；**ASAR 内 `out/main/index.js`=594342B/`83d82b19…` 与 whole087 六处（BUILD-NONCE-DIFF / actual-five-JS / frozenOutFive / ASAR / ROOT JS.main / ENTRY）完全一致**；`asarFiveEqualActualFrozenOutFive:true`；engine 组件 members 266 / regularFiles 225 / 37,723,215B，`completeReusedEngineComponent.matched:true`、embeddedPYZ 与 build081 冻结 PYZ 逐字节相等（`equalsFrozenPYZ:true`）、producerHEAD=888ac577、`newEngineBuild:false`——**engine 复用真实 888 组件、未重建；JS 直接采用 whole087 产物，无二次构建**。
- ROOT acceptance（107285B / `41e81bd9…` 实测吻合，accepted:true，status `…ONLY_RELEASED`）：APP910（members 910 / 545 regular / 383,005,197B）、Resources290（290 regular leaves 投影）、engine266（口径在 ENTRY 与 readback）、`rootActualPhysicalAPP910AndOut9Reconstructed:true`、deliveryPhysicalPinsMatched 593。**同时如实记录**：`signedReleaseGate:false`（basis: identity null、product signing skipped；deep codesign exit 1，9 个非 engine 二进制 verify exit 1，3 个 engine 必要签名 exit 0）、`legalFullClosureAccepted:false`、`mechanicalClosureOnly:true`、`dynamicCasesExecuted:false`（该文档为静态身份验收范围；动态证据由 2.3/2.4 单独承担）、`formalReleaseAccepted:false`、remainingGates 5 项。`asarDesktopPackageJSONRawSourceBytesEqual:false`（ASAR 内 292B vs 原始 491B）有 `reviewerReadOnlyAnalysisCorrection` 记录的解释（打包规范化 package.json，main 另行单独校验）——作为已记录的已知差异保留，不构成机械身份矛盾。

### 2.3 真实 e2e（`outputs/20261024_t01_full_e2e087_actual_002/`）

- actualCollected=18，16 ACTUAL_PASS + 2 CONDITIONAL_SKIP；两 skip 为 i04 `coordinator exit reconciles…`（源码条件 `process.platform !== 'linux' || !fixturePath`）与 `native renderer crash…`（加 `I04_NATIVE_ISOLATED !== '1'`）——**原源码的 macOS 平台条件跳过，非本轮回避**。
- ROOT-EXECUTION-RECORD.json：完整 npm 入口 `--max-failures=1 --trace=on --reporter=list,json`、workers=1、retries=0、outer 300s、`perCaseTimeouts:"Original source/config30/60/90; no CLI timeout override"`；outer/wrapper/inner/npm 各层 naturalExit 0；observer 214 采样 0 错误。
- 16 个 `isolated-desktop-launch` 附件全部 `OWNED_PROFILE_BOUND`（同 run 内 owned profile、packaged appPath、`--user-data-dir` 指向该 profile）；`actualExecPathGetter:null`、`actualResourcesPath:null`、`NOT_RECORDED_BY_UNCHANGED_HELPER`——**缺失 getter 仍为 UNKNOWN，未冒充观测**；KNOWN-PIDS-AFTER：113 knownPIDs、psExit 1、`noSignals:true`、`globalReapClaim:false`——有限已知 PID 无匹配不被外推为全局 reap。
- T02 两例：`five fields, complete Diff, original receipt, Undo/Redo and owned restart` 4.4s PASS、`edit real example home…then query through T04 UI` 4.3s PASS，trace.zip 22019B/24471B 已固定。

### 2.4 真实运行时（`outputs/20261024_t01_package087_real_runtime_actual_001/`）

- SOURCE005 三例全 PASS：reload / renderer-recovery / coordinator-exit 的 preFaultJob.state 均 `running`（在途前提成立）、`faultApplied:true`、无 NOT_EXERCISED；finalJob.jobId 与 preFaultJobId 一致（**Job 不重建**）；baselineMarker 七字段、domain revision 1→2、noReplay 边界声明齐备。
- native-lifecycle：真实 `executeJavaScript` 无限循环（hangMonitorEnabled、visible/focused）；3 个真实原生"窗口恢复"对话框，CUA 实际响应 **0/0/1**；真实 Cmd-Q 退出（`successExitMethod:"real-user-app-quit; never app.exit(0)"`）；事件序 **before-quit(4) → window-closed(5) → will-quit(6)**；**本次直接观测 engine 子进程 exit 0 (seq7) / close 0 (seq8)**（pid 33058，observer 直接事件；RELEASE 明示"historical085 UNKNOWN unchanged, not inferred from PID absence"）；退出后同次 CUA AX 返回 procNotFound 的工具错误原文保留、未重新 getApp；APP/driver 全 natural 0。

### 2.5 086 历史失败与更正链（保留，不洗白）

- 失败 trace.zip 18686B/`216e2890…` 实测吻合；解包核验确为失败 trace：主错误 `Expected: not "waiting"`、Timeout 5000ms（spec confirmAndRead）；rpbm@1548 为原操作状态 region 的 count 查询、rpbm@1549 textContent 在 context 关闭后报 "Target page, context or browser has been closed"。**如实记录两个证据链细节**：(a) Playwright trace 不记录 count() 返回数值，"1548 pending.count 非零"的依据是 ENTRY 文字诊断与调用序列推断，correction basis 引用的原始诊断文件（reads8217a5/b5f5a7）在本次可读范围内未找到；(b) trace 中 Close context（1552）本身无错误，报错的是 1549 的 textContent。这不改变结论（测试在 5s 内未观测到终态即失败），但把"观察到的事实"与"归因表述"区分开。
- 086 入口分布：9 PASS / 1 fail（T02 主例）/ 2 条件 skip / 6 notrun（`1 failed / 2 skipped / 6 did not run / 9 passed` 原文）。失败 Job 在已结束 profile 复制 DB 中真实 `succeeded`、`projectRevision:1`（FAILED-T02-SQLITE-READBACK.json），但 `doesNotProveUIReceiptObserved:true`——**DB 成功不冒充 UI 通过**。
- TRACE-REFERENCE-CORRECTION.json 承认旧 ENTRY 曾用未过滤 glob 误指 passed trace，改为固定失败 trace（18686B/216e2890），`UIReceiptActualDOM:"UNKNOWN"`。
- INDEPENDENT-POSTPATCH-REVIEW.json（独立 agent）：one evaluateAll 同步读双 region 移除 count→textContent TOCTOU；重复 region 拒绝、原双谓词/5s/后续全部断言保留；`actualRuntimePassClaim:false`（当时未跑，运行证据由 actual002 补齐）。我独立读取 748 全 diff 证实该描述（见 §3.2）。
- actual001 首次外部 guard 失败保留：status `FIRST_ACTUAL_GUARD_FAILURE_PRESERVED_BEFORE_WRAPPER_PRODUCT`、naturalCoordinatorExit 1、0 产品用例；CORRECTION/ALL-GLOBAL-BINDING-READBACK：新 adapter 仅改全局 HEAD 一行字面量（after.py 81030B `96edff16…`→`e27a27e4…`）、14 个全局绑定 AST 核验、`allFunctionsAndObserverByteIdentical:true`；actual002 才执行真实产品入口。

## 3. 累计代码审查

### 3.1 审查方式与覆盖

38 提交中 36 个为上一候选 7d30 已全量审过的基础（03376dfb…7d30ab34：私有事务、补偿、format3 契约、CAS、Job3 claims、business3 校验、ChangeSet/undo、b6edf213 主线集成 66.6k 行、888/bb9f 打包与许可等）。本轮作为全新累计审查，在 748 工作树**重新通读核心承载件全文**：`project-mainline-service.ts`（818 行）、`desktop-ipc.ts`（212 行）、`preload/index.ts`（87 行）、`csp.ts`、`mainline-session.ts`（819 行，T02 状态机）；并复核不变量：预算硬上限（engine.ts:735-736，134217728B/1048576 objects；单请求 8388608/263168）、生产 CSP 无 `unsafe-inline`/`unsafe-eval`（仅开发变体 style-src 有 HMR 例外并限定 127.0.0.1:5173 + nonce 校验）、preload 仅业务命名方法（无通用 invoke 通道；`receiveMainline` 封装带 zod 信封校验与 5s ACK 超时，ACK 失败保留原租约不伪造重试）、SQL 全参数化（storage.py 106 处 execute、185 个 `?` 占位符；唯一 4 处 f-string 为 SAVEPOINT 语句，标识符 `"s_"+uuid4().hex` 内部生成，无注入面）、IPC `trusted(event)` 前置 + sender/mainFrame/session 精确匹配（desktop-ipc.ts:129-135）、renderer 无 Node 能力。S-source 闭集抽样含两个本轮改动叶，工作树与提交源一致。

### 3.2 dd21ab12（M4 修复）与 748008a6（T02 测试快照）逐行审查

**dd21ab12**（engine.ts +47 / project-mainline-service.ts +166 / 两测试 +208）：
- 紧凑身份与完整载荷两层分离：`MainlineIntent` 增加 `jobId/payloadEntry/pendingReplies/active`；`#keepIntent` 将 `{operationId,request,engineSessionId,jobId}` 紧凑记录预付在 `intent` 本身的 holding 上（永驻 `#intents` Map，不 FIFO 遗忘，由既有 128MiB/1048576 全局硬预算约束生命周期）；accepted JobView 独立记在 `payloadEntry` holding（service:621-636）。
- ACK 后退休：`#offerIntent` 通过 `budget.onReplyConsumed(payloadEntry, retire)` 登记；仅当该 intent 的**全部** pendingReplies 都精确 consume 且 `active===0`、非 unknown、accepted 仍存时才 `releaseHolding(payloadEntry)` 并移出 `#fullIntents`；清理失败恢复 `intent.accepted` 并抛错——原 receipt/holding/完整责任保留、可按原 handle 重试（service:637-660；engine.ts:1059-1076 注册约束：holding 存在、同 session、单 delivery ≤16、预留 512B/8obj/4096 上限）。
- engine.consume（engine.ts:949-975）：仅 OFFERED+callbackDone+无计算中+同 session 的精确 receipt 可消费；逐项执行 retire、逐项删除（已完成项不重复退款）；`consuming` 防重入；UNKNOWN 投递永不执行回调（有专项单测）。
- 旧操作重放：`#readAcceptedIntent` 只经真实 `job.get`（`job.get` 加入 mainline 允许清单，engine.ts:1706），并校验 jobId/projectId/operationId/capability/confirmationRef/input 全等后才返回；**绝不 job.create 重放**；`if (intent.unknown) throw denied()` 保留"已进入写入不自动重放"边界（service:751）。
- 16 上限从 `#intents.size` 移到 `#fullIntents.size`（service:735）：退休后可继续新提交；17 次真实提交回归测试断言 `job.create` 恰 17 次、末次调用为 `job.get`、revision=17、错 confirmationRef 被拒且不产生新 job.create。
- 我的两个**独立边界观察**（均 fail-closed 方向，不构成阻断）：
  1. retire 回调在 `intent.active!==0`（并发同 operationId 调用进行中）时抛 invalid → consume 失败、receipt 保留、可稍后重试；此路径无显式单测。风险：极端时序下 ACK 需重试一次。严重度 Low。
  2. ACK 丢失（delivery 转 UNKNOWN）后该 intent 的首个 pending 永久残留于 `pendingReplies`；即使后续同 operationId 重试并 ACK，`size>1` 分支只删新 pending、payload 永不退休——即任何经历过一次 ACK 丢失的 intent 永久占用一个 full 槽。这与 owner 保留的 M3 语义（16 个 inflight/UNKNOWN/unACK 完整责任，不 FIFO、不假作 ACK）一致且已被处置记录接受；可达后果是 16 次 ACK 丢失后本会话提交容量耗尽需重启。观察事实，非新缺陷。

**748008a6**（仅 tests/e2e/t02-ontology-mainline.spec.ts，+15/−10）：poll 内改为单次 `receipt.or(pending).evaluateAll` 在一个 DOM turn 同步读取两 region；重复 region（>1）仍抛错；`提交版本 N。` / `succeeded` 判定值、`expect.poll` 原 5s、`needsReconciliation` 分类及后续全部断言未变——**纯观测方式修复 TOCTOU，无断言/预算放宽**，与 INDEPENDENT-POSTPATCH-REVIEW 描述一致；actual002 的 T02 两例 4.4s/4.3s PASS 为其运行闭环。

### 3.3 历史意见处置的独立复核（不预设立场）

- **M1（uncertain 单向闩锁）**：处置"部分采纳"与代码事实相符——闩锁仍在（同一 live engine session 一次 UNKNOWN 后主 project/query 走 `mainlineReady` 受拒），但"全 App 永久不可用"不成立：新 session 新 owner 可建，原可信 principal 路径支持真实 open 与只读恢复。我独立同意该缩小化定性；将可达的单会话主链不可用保留为本轮 Top 10 第 4 项。
- **M2（跨 session 原操作冲突）**：不采纳全局化、保留创建专属限制——与 `.worktrees/T01-project-host-read-services` 契约（origin 全等重取、缺物理绑定保持 UNKNOWN）及 `test_mainline_named_example_dispatch.py` 的显式断言一致；恢复白名单确含 job.get/operation.get。同意处置；限制留账。
- **M3（16 未 ACK 投递）**：保留 16+UNKNOWN 责任、不 FIFO——desktop-ipc.ts:104（无 timeout/navigation/new session 删除未 ACK receipt）、:164（16 槽上限）与 engine UNKNOWN 不回调均实证。可达耗尽事实保留（Top 10 第 3 项）。
- **M4**：实现正确（§3.2），处置所述"两层方案、不丢身份、job.get 只读、失败保 receipt"逐条与代码吻合；17 次真实提交测试为真实引擎+SQLite，非替身。
- 其余 M5–M18 / Z1–Z10：处置表的"不自动扩功能、留账不洗绿"与我在 748 的复读结果一致。其中 **Z1（child exit/close UNKNOWN_NOT_OBSERVED）在本轮出现实质新事实**：real_runtime native-lifecycle 首次由 observer 直接记录 engine exit0/close0（seq7/8）——旧 085 记录不改写，但"正常 Cmd-Q 路径引擎子进程退出可观测"已闭；剩余活体挂起→下次 `leaseBusy` 场景仍未演练（推断性风险）。

### 3.4 T02 / T04 / 恢复路径要点（748 现状复读）

- T02 undo：`prepareUndo` 固定取**当前回执**（mainline-session.ts:382-390），以新读 base 作为新操作进入（非本地反转 diff）；undo-of-undo 经引擎 `preview_undo` 语义可达（即事实 redo 路径），但无独立 redo/历史选择器 UI（M12/Z3 保留）。`if (!receipt || pending) return` 静默返回为轻微 UX 粗糙。
- 对账：`reconcile` 经 getOperation→marker 七字段校验（含 planHash 64-hex、revision>base）→ getJob succeeded+atomic marker 双确认才 terminal；无 operation 时 32 页×100 条有界扫描查原 Job，找不到保持 unknown——**不制造否定回执**（mainline-session.ts:275-314, 658-804）。
- 补偿/未提交清理：`clearUnsubmitted` 用新鲜 generation CAS 写 closedBookmark，防迟到原书签覆盖；ACK 丢失按原 save ID/args 精确重试；REVISION_CONFLICT/INVALID_STATE 触发 cleanupNeedsRefresh 重读。已核。
- T04：查询结果当前页 CSV 导出（QueryResultPanel.tsx:319 `query-current-page.csv`）与 ASK CSV（:252）；分页带 listSnapshotId 快照绑定校验 + seenCursors 环检测 + complete 语义（workspace-controller.ts:1241-1290 等）；**无全量导出**（M7/Z4 保留）。分页每页物化规模风险（M6）与撤销历史扫描（M15）未量化验证。
- 首次 ACK 丢失 e2e（mainline-consumer-first-ack-loss.spec.ts）：断言第二个信封复用原 accepted Job（同 operationId/同 acceptedJob、仅新 deliveryId）——零重放实证。项目切换隔离：selection fence + fingerprint 绑定（projectId 入指纹、owner/session 全等）+ draft 每项目 generation CAS；ontology-switch-preflight / query-draft-switch 两 e2e 在 16 PASS 内。

## 4. 最值得修复的 10 项（按严重程度；标注适用范围与观察/推断）

1. **【High｜正式发布阻断｜观察】签名/公证/身份缺失。** ROOT acceptance remainingGates[0]、`signedReleaseGate:false`、deep codesign exit 1、9 个非 engine 二进制 verify exit 1（package-readback `appDeepCodesign`）。触发：任何正式分发/他人设备运行。风险：无法分发、Gatekeeper 拦截、供应链无身份锚。建议：正式阶段采购证书并重签+公证后再开分发门（内部演示已获用户授权范围，不擅改 builder）。
2. **【High｜正式发布阻断｜观察】wholeAPP legal/_distutils 来源闭包未接受。** `legalFullClosureAccepted:false`、`mechanicalClosureOnly:true`；另有 ASAR 内 package.json 292B vs 原始 491B 的已记录差异。风险：正式分发法律义务未闭。建议：正式阶段逐组件复核上游来源与许可（含 _distutils、setuptools vendored 原件）并出具接受记录。
3. **【Medium｜长会话可用性｜观察】ACK 丢失→intent payload 永不退休，16 次后本会话提交容量耗尽。** 位置：desktop-ipc.ts:164（16 投递槽）、project-mainline-service.ts:637-660（pendingReplies 残留语义）+ :735（16 full intents）。触发：连续 16 次投递 ACK 丢失/UNKNOWN（如渲染进程反复在中途崩溃）。风险：需重启 App 才能继续提交。这是 owner 明确保留的 M3 安全语义，非缺陷；建议增加恢复入口或 UI 明示（现 UI 仅 unknown 态）。
4. **【Medium｜可用性｜观察】uncertain 单向闩锁（M1 处置后保留部分）。** 位置：engine.ts `mainlineReady`/uncertain record 复用路径。触发：同 live engine session 主 project/query 链一次 timeout/UNKNOWN。风险：该 session 内主链 IPC 拒绝直至引擎重启（新 session/新 owner 可恢复；创建前清空 P 场景恢复更窄）。建议：文档化用户自救路径（重启会话）或在恢复白名单内扩只读对账入口。
5. **【Medium｜性能/规模｜推断】无显式二级索引 + 每页物化 + 撤销历史扫描。** 事实：引擎包 0 处 `CREATE INDEX`（仅 TEXT 主键隐式索引）；jobs/history 列表按 `ORDER BY created,id`/`ORDER BY revision` 等查询（job_store.py:2179 等）；M6 每页物化、M15 撤销扫描未量化。触发：单项目数据增长至数万~百万行级（当前演示规模无故障）。风险：分页/对账变慢。建议：在 D2/规模口径验证时补关键查询 EXPLAIN QUERY PLAN 与索引；不提前优化。
6. **【Medium｜数据韧性｜观察】用户级备份/恢复缺失 + 损坏 SQLite 修复 HOLD。** 迁移时备份存在（storage `_migrate(backup_path=…)`）但非用户级定期备份；restore 从备份实测未做；损坏库显式修复要求人工（`Invalid legacy result kind; explicit repair required`）且 B/C 方案未授权。风险：用户误删/磁盘损坏无自助恢复。建议：正式阶段设计用户备份/恢复入口并实测一次恢复（"没恢复过的备份只是希望"）。
7. **【Medium｜验收｜观察】跨平台/参考设备/D2/Windows 未测。** 包与全部真实运行证据仅 macOS 15 arm64 本机形态；Windows 无构建；LSMinimumSystemVersion 13.0 的更低版本 macOS 未验。属用户明确的独立保留门。
8. **【Medium｜合规/UX｜观察】a11y 未测（Z7）+ 错误 messageKey 可行动性（Z8）。** 键盘导航/读屏（清单 129 行）无合同事实不虚称合规；错误显示为固定码白名单（mainline-session.ts:81-99），部分码对终端用户可行动性有限。建议：正式/企业阶段按合同引入 a11y 验收；错误文案分级。
9. **【Low-Medium｜功能缺口｜观察】T04 无全量导出（仅当前页 CSV，QueryResultPanel.tsx:319）+ T02 无独立 redo（undo-of-undo 引擎可达但 UI 固定当前回执）。** 与 FR-804/T04 原范围核对后按需立项，不由清单自动扩权（M7/M12/Z3/Z4 处置一致）。
10. **【Low｜维护｜观察】超大文件与依赖/文档节奏。** engine.ts 2623 行、workspace-controller.ts 1531 行（清单 138 行）；依赖升级与扫描为手工冻结政策、无自动扫描（M16）；changelog/terms/privacy 未建立（M17）；bundle id `io.github.nomorejoke` 为个人命名空间（正式化前决策）。建议按维护迭代处理，不混入当前发布线。

**其余未进 Top 10 的阻断/缺口（完整保留，不清零）**：C4–C6 三次配对失败历史与熔断门记录、D8 人工裁决（888ac 决策书待用户选 A/B）、0/17 发布流程（push→PR→CI→merge→远端复核未发生）、静态盘上加密未启用（SQLite 明文，依赖 OS 全盘加密的决策留账）、正式渗透测试未做、模型网关 S3 前不得接入（当前不适用）、actual001 guard 失败与 086 失败永久留档。

## 5. 用户 11255B 清单逐项适用性（160 引用行；147 产品 + 13 人员）

### 5.1 适用且本轮已核（有实现与证据）

- schema 预先设计（format3/before3 契约+zod business3 `.strict()` 全边界校验；PRD/ADR 驱动，非 AI 逐表即兴）。
- 权限深于 admin/everyone：owner/principal/budget/allowlist 能力模型（engine.ts 权限面 + mainline 允许清单 :1706）。
- 越权改数字读他人数据：projectId 绑定 + owner/session/current 三重校验（service `#current`/fingerprint）、IPC trusted+sender/frame/session 精确匹配（desktop-ipc.ts:129-135）——无跨项目越权路径。
- 服务端校验（主进程+引擎双侧，非仅表单）；参数化 SQL（106 execute/185 占位符；savepoint=uuid4hex）。
- 幂等键（operationId/operation_claims/marker；17 次真实提交恰 17 次 job.create）；重复提交去重（同 operationId 复用 accepted Job；draft generation CAS）。
- 分页在深处仍正确（快照绑定+游标环检测+complete；400 页未实测性能→§4.5）。
- 导出=当前页 CSV+ASK CSV（全量导出为缺口，§4.9）。
- 保留规则/软删的等价更强形态：不可变提交轮次/历史/快照（before/after snapshotId 链）；缓存回收不触历史（AGENTS 不变量+budget 边界实证）。
- 秘密不入库不入仓（无凭据；S3 前模型网关不接入；引擎无密钥不外呼）。
- 输入消毒（zod strict 全 IPC 边界）；XSS（React+CSP 生产无 unsafe-inline/eval）；CSRF/CORS 不适用（无 HTTP 面，connect-src 'none'）。
- AI 代理最小权限与人工审批（Agent 仅草稿+白名单工具+不得自确认；人工确认按钮是唯一写入口）。
- 日志不记敏感（跨边界固定错误码+受限参数，无原始异常/堆栈/路径外传）。
- 后台任务队列（持久 Job/claims/恢复/有界 worker；失败/取消为持久终态记录，本地形态 DLQ 等价）。
- 缓存与失效（RDFLib 图仅从不可变快照重建；staleReason 只来自 invalidation-v2.json；本轮 M4 的 payload 退休即受控缓存清理）。
- 不可变时点证据（逐操作快照链 = point-in-time 等价能力，本地单用户形态）。
- 单测有人懂逻辑（1694 例断言预期全集/顺序而非计数）、回归测试（086 失败→748 修复+回归即实例）、测试数据非生产数据（隔离 profile/fixture+真实引擎）。
- e2e 核心流（创建/示例/Diff/commit/undo/重启/查询/切换/ACK 丢失 18 例）。
- 每变更代码审查（指定双审+固定 SHA+独立复核，本轮即实例）；分支策略（worktree+feature 分支规范）；ADR（0001/0002+迭代目录）；继承者文档（docs 树+状态文件+证据链）。
- 事后复盘改变些什么（C4-C6/086/actual001 失败记录、更正与独立复核留档——postmortem 文化实际运作）。
- 空态/加载态/错误态（session phase 状态机 8 态+错误显示；未逐屏穷尽验证→部分）。
- undo（T02 补偿式撤销+不可变 marker）。
- 迁移前进+不锁表（本地单进程 BEGIN IMMEDIATE 短事务；forward user_version+显式修复策略，无自动回滚是有意决定）。

### 5.2 整类不适用（本地优先单用户桌面，无对应面；不为此加功能）

- 账户/身份类：login 加号邮箱、密码重置链接、MFA、会话超时/全踢、SSO、SAML、SCIM、登录限流、锁定vs误锁（无账户体系；存在的是 engine session/epoch，性质不同且已核）。
- 多租户/企业合规：租户隔离（项目间隔离已核，跨客户租户不存在）、admin 代登录、安全问卷、披露流程与被盗笔记本预案（正式阶段再立）、SOC 2、HIPAA、BAA、PCI、GDPR 删除、数据驻留、季度访问复核、查看型审计（单用户无"他人查看"）。
- 支付/计费全部：货币整数、汇率/税、订阅/按比例、催付、发票 PO、VAT、退款、计量对账、年约、收入报表。
- Web/API 面：webhooks 签名与重试、对外版本化 API（内部协议版本字段已核：deliveryVersion/draftSaveVersion）、API key、API 限流（内部预算限流已核）、第三方 API 变更预案、OAuth 刷新、集成沙箱。
- 云运维全部：连接池（嵌入式 SQLite 单连接）、CDN、DNS/SSL、自动伸缩、二区域、零停机/一键回滚部署、功能开关（单版本桌面）、cron 防重（无 cron；flock 单实例）、负载测试（单用户；规模验证归 D2/§4.5）、外部拨测/告警/值班/runbook/状态页/可搜索集中日志（本地 JSONL 固定字段为对应形态）、错误聚合遥测（无遥测出网）。
- 邮件：SPF/DKIM/DMARC、退信处理、邮件客户端渲染。
- LLM 当前不适用（S3 前不接入，接入后逐项转适用并有网关/白名单/花费上限设计位）：提示注入防护、客户数据出提示词、按客户花费上限、evals、模型降级、模型弃用迁移、提示/输出日志。
- 文件上传扫描、CSV 2009 导入、通知开关（无对应功能）；酒店 wifi 加载（本地）。

### 5.3 适用但无法确认 / 未满足（如实登记，不以静态绿冒充）

- 备份每夜+恢复实测（§4.6）；索引与百万行规模（§4.5）；渗透测试；依赖自动扫描（M16）；框架/Electron/Python 升级节奏（手工政策）；五年级旧设备（目标明确 macOS13+ arm64，参考设备归 D2）；a11y（Z7）；i18n/RTL/本地化格式（单语 zh 现状）；表单失败保留输入的全覆盖；浏览器式后退预期（桌面导航存在、行为未全测）；README 一小时上手；2000 行文件拆分与死代码清理（Z9）；changelog/terms/privacy（M17）；公司名下账户/域名/repo（个人命名空间观察）；bus factor>1 与 13 项人员角色（人员事实无法从代码确认——流程上由指定双审/独立复核/总控记录部分承担，本轮实际运作有证据）；正式部署流水线（check 全绿才打包的当前流程已核，但 push→PR→CI→merge 未发生）；dev/staging/prod 一致性（当前 dev/CI/打包同套 check 已核，"prod"=本地包形态）。

## 6. 内部演示范围最终判定

**PASS。** 真实依据（均为本轮直接读证，非沿用旧结论）：

1. 源码闭集完整一致（S-source 1270 抽样+索引/overlay 哈希全对），无未提交产品改动混入（cached diff 空，唯一 M 为受保护 AGENTS.md）。
2. whole087 单次完整 check 自然 0（全量数字见 §2.1）；748 相对 check 时源仅一叶测试改动且原样提交（BUILD-NONCE-DIFF/ENTRY 诚实记录链）。
3. package087 机械身份/资源闭包通过：ASAR main=whole087 main（六处一致）、五 JS 全匹配、engine 266 组件复用真实 888 产物、APP910/Resources290 物理重建一致。
4. 真实运行：18 例=16 PASS+2 原平台条件 skip，各层 natural 0；T02 两例 PASS（含 748 修复叶的运行闭环）；SOURCE005 三例真实故障 PASS 无 NOT_EXERCISED；native 真实循环/对话框 0/0/1/Cmd-Q/事件序/engine exit+close 直接观测。
5. M4 修复实现正确且 17 次真实提交回归；无 public 协议、origin、CSP、preload、权限面的放宽；无新增持久 intent 账本。
6. 历史失败与 guard 失败均保留未清洗（§2.5）。

**保留 HOLD（正式分发/其他平台，独立于内部演示判定）**：签名/公证/身份；legal/_distutils 全闭包；Windows/跨平台/参考设备/D2；损坏 SQLite 修复授权（B/C）；用户级备份/恢复实测；a11y；渗透测试；静态盘上加密决策；D8 人工裁决；C4–C6 历史轮次记录；0/17 发布流程（本审查者无推送/合并权限，push→PR→CI→merge→远端复核待 parent 执行）。

## 7. 本次审查的自我限制（观察与推断区分）

- 未运行任何新 build/GUI/打包/测试/外部请求；所有运行证据均为对既有冻结产物的只读核验（含 trace.zip 解包到 /tmp 只读分析）。
- "1548 pending.count 非零"为 ENTRY 文字+调用序列的推断（trace 不记 count 值；原始诊断文件未找到），已在 §2.5 区分表述。
- 引擎活体挂起→`leaseBusy`、百万行分页性能、RTL/a11y、README 上手时长、人员配置类：均为推断或无法确认，不写成已验证事实。
- MiniMax/另一模型本轮任务与报告未读取；本报告结论独立形成后与之对照的流程由 parent 承担。
- 证据目录中的 JSON/哈希核验不能证明其生成过程之外的事实（如"未来不会损坏"）；机械包身份通过不等于 formal 签名/法律/全平台通过。

— 审查完成于 2026-10-24，ZCode（Start Plan / GLM-5.3 / 最高 / 完全访问）。
