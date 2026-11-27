# T01 fde989ac / package088 全新独立完整累计工程复审报告（ZCode / GLM-5.3 / pair001）

- 审查者：ZCode，Start Plan 发起；model `account:bigmodel-start-plan/GLM-5.3`；最高思考档（slider2）；完全访问（本会话全程无权限拒绝）；官方 workspace memory 已 OFF（本次全新任务，未读/写任何 `.zcode`/`.minimax`/项目/用户 memory）。
- 候选：HEAD `fde989ac2cd2fc59dc396b7082307f09235019e1` + package088，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，累计 40 commits / 546 files。
- 只读边界：未修改任何产品源码、测试、配置、标准、Git 索引与既有证据；未运行新 build/安装/GUI/APP/engine/测试/打包/外部请求；所有 Git 读命令带 `--no-optional-locks`。唯一写入物为本 report.md。未读取另一模型本轮任务/报告（`../minimax/` 全程未打开）。
- 历史上下文：六份已完成历史报告（085 双方、087 pair001 双方、087 pair002 双方）与三份处置记录全文读毕并逐项回实码独立复核，可反驳处置，未把处置当指定 PASS。

---

## 0. 结论（先行）

1. **当前内部演示范围（无签名目录包，用户明确"非正式分发，仅限内部演示"，实际宿主 macOS 27.0.1）：PASS。** 依据（全部为本轮直接读证或亲读实码，非沿用旧结论）：累计 40 commits 内核心不变量经我在 fde 工作树逐行复核成立，未发现新的阻断级实现缺陷；clean-checkout-002（tracked-only fde、独立 npm ci/uv sync）单次完整 `uv run --frozen npm run check` 自然 0（147.099s；35 TS 文件 1694 测试、345 Ruff、Python collected 3510 = 3466 PASS + 44 SKIP + 1 个故意 duplicate-ZIP 负例 warning）；package088 机械身份/资源闭包通过（五 JS 直采 C002 新产物、engine 复用真实 888 组件、ASAR 819 文件、APP910/Resources290/engine266、ROOT 603 delivery leaves + 35 refs 物理受理）；本版 088 真实完整 E2E 18 collected = 16 PASS + 2 原平台条件 skip（91.04s，各层自然 0，T02 两例 5.1/5.0s，T04 实测 243 ordered rows 完整分页/CSV/history PASS）；三种在途真实故障（reload/renderer-recovery/coordinator-exit）各有 PASS 且原 queued/running 前提、faultApplied、Job/marker/noReplay 断言不变；native 首次 0-retry 真实 PASS（160.14s，三窗口，真实 responses 0/0/1，真实 Cmd-Q，beforequit→closed→willquit，APP/driver 自然 0）；renderer 产品三次尝试 FAIL/FAIL/PASS（第三次 24.84s 真实点击链完整 PASS）。
2. **上一对核心争议（retire 抛错泄漏）经我在当前 fde 源码逐链独立重建：自然可达反例仍不存在；"故障注入下产品无原 ACK 自动重试入口"作为实在限制保留。** 详见 §3。M1（uncertain 单向闩锁）、M2（跨 session 创建原回执不可对账）、M3（16 个未ACK/UNKNOWN 完整义务容量）未修复、如实保留，与处置口径一致；我本轮补充的边角搜索（重复 ACK、乱序 ACK、首次提交各失败分支、中途崩溃）未产生新反例。
3. **正式分发与其他平台：BLOCK/HOLD 全部保留，一项未清零。** 至少：签名/公证/身份（identity null、deep codesign exit 1）、wholeAPP legal/`_distutils`、Windows/参考设备、**目标 macOS 15 arm64 兼容性 UNVERIFIED（实际宿主为 macOS 27.0.1，旧报告"15 实测"为历史错误已更正、原件保留）**、真实 CI 三失败未在远端闭环（fde 未 push，PR6 remote head 仍 58419ec4）、损坏 SQLite 物理 HOLD（B/C 未授权）、D2 规模/索引、用户级备份/恢复实测、a11y、真实 LLM（S3 前不接入）、C4–C6/D8 历史轮次。
4. **0/17 口径不变。** push→PR→CI 全绿→squash develop→远端复核均未发生；本审查者无推送/合并权限；本地绿不得预告远端绿。
5. 两项任务中事实补充/勘误已按原件核验后采纳并单列（§5.6）：renderer 第 2 次 05:54:08Z 恢复对话框的人工输入已获用户可信确认（仅该时刻，native 05:58:48Z 第 1 个 0 仍 UNKNOWN）；package 回执"1790"为字节数（timeout=false 是直接字段，wrapper 原预算 300s）。一处证据哈希差异如实登记（§1.3）。

---

## 1. 受理与环境回读（全部本方实测）

### 1.1 附件与仓库身份

| 项 | 指定 | 实测 | 判定 |
| --- | --- | --- | --- |
| prompt.txt | 32525 B / SHA256 `283038a370d3958254632dd5b7442da0cac9e81a7427d0054cf7339575e4960c` | `wc -c`=32525；`shasum -a 256` 全匹配；官方 Read 工具读至 EOF（218 行） | ✅ |
| 原 11255B 清单 | 逐字保留、恰在 EOF 出现一次 | 第 49 行"你现在是我的软件工程审查员。"起至 EOF = **11255 B**；标记串全文恰出现 1 次；末行 `> remembering why it's built this way, a year from now (someone who was there)` 即文件末尾 | ✅ |
| 项目绝对路径（Unicode 规范、Copy Path 读回） | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | `pwd` 一致；与附件第 3 行逐字符相同 | ✅ |
| Git authority G | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | `.git` 指针读回一致 | ✅ |
| HEAD / 分支 | `fde989ac…19e1` | `rev-parse HEAD` 一致；分支 `feature/weekly-t01-project-transactions` | ✅ |
| base | `5f910b52…47f3` | `cat-file -t`=commit；`merge-base HEAD base`=base 自身 | ✅ |
| 累计范围 | 40 commits / 546 files | `rev-list --count`=40；`diff --name-only`=546 | ✅ |
| AGENTS.md overlay | 15147 B / `de15f6ce…56a5c8c4`，唯一未暂存工作修改，勿编辑/暂存 | 字节与 SHA 一致；`status --porcelain` 仅 ` M AGENTS.md`；全程未触碰 | ✅ |
| 索引 | 175620 B / `c2af8c61…1741b3`，cached diff 空 | G/index 实测一致；`diff --cached --name-only`=0 | ✅ |
| fde 树内 AGENTS | C002 已提交 1056 B / `1b3c0291…4a3a6fb` | `git show fde989ac:AGENTS.md` 实测 1056 B / SHA 一致——与 15147B overlay 不同，不混称全同 | ✅ |
| provider / model / 思考 / 权限 | Start Plan / GLM-5.3 / 最高 slider2 / 完全访问 | 本会话环境 `account:bigmodel-start-plan/GLM-5.3`；无权限拒绝 | ✅ |
| memory | workspace memory OFF，全新任务 | 未读写任何工具/项目/用户 memory | ✅ |

### 1.2 六报告 + 三处置 + 088 证据哈希（本方逐件重算）

六份历史报告与三份处置共 9 件：**9/9 字节与 SHA256 全部一致**（085 MM 50711B/`8d6c72a6…`、085 Z 33258B/`540dbaa4…`、087-001 MM 103590B/`33ff3583…`、087-001 Z 34597B/`12ffaff3…`、087-002 MM 87337B/`7a844d10…`、087-002 Z 39904B/`7b802002…`、处置 10836B/`cc21f6b0…`、24902B/`bae9babb…`、20117B/`d6d783f7…`）。

088 证据面 30 件全部核验一致，含：source-map 226770B/`c4a3e3d3…`、check-source-map 226769B/`30055ab1…`、ENTRY 4080B/`817273c5…`、CLEAN-FULL-CHECK-002 606B/`dc8951aa…`、clean-full-check-002.log 12017B/`66df9fd4…`、actual-five-JS 775B/`6c909cb9…`、SOURCE-MAPPING 1749B/`d5807399…`、ACTUAL-PLATFORM 1178B/`0fd0ac41…`、ROOT 受理票 111553B/`5ae9bfad…`、package-readback 1521347B/`58eec2ac…`、full-e2e ENTRY 3515B/`403e5fb2…`/MANIFEST 13245B/`69d87918…`、FIRST/SECOND/THIRD 三组 JSON+MANIFEST+TIMELINE、NATIVE 三件、COORDINATOR 两件、086 失败 trace.zip 18686B/`216e2890…`；包内 `app.asar` 19014603B/`74304c2d…`、`engine/ontolearn-engine` 6223312B/`43efc368…` 实测吻合；T09 ZIP 1344035B/`b8717a53…` 在 4 处副本（t09 供给、mainline node-checkout、clean-checkout、clean-checkout-002）逐字节一致；CI-FIRST-{WINDOWS,QUALITY,MACOS}-FAILURE.log 三件在档（35539/53038/47548B）；THREE-FAULT-RESULTS.json 在档（600B，reload PASS 原件）。

### 1.3 一处声明哈希差异（如实登记，不改任何原件）

`…/20261024_t01_package088_real_runtime_actual_001/CUA-TOOL-TIMELINE.json`（第 1 次 renderer 失败时间线）：**实际 17590 B / SHA256 `49a2c19acd047f0ed7223e30dde80208b8b4c097037296c9f4b8a62f4264aada`；附件声明值为 `…b8b4c097037298c9f4…`**——单十六进制字符差异（`6` vs `8`），字节数一致，重复哈希结果稳定；全 outputs/iteration-control 范围内无其他文件引用该前缀（仅本 prompt/shared-prefix/minimax prompt 三份文本），判定为**任务书转录笔误**而非证据文件被改动。该文件内容本轮未采信任何未经验证的结论；此差异不影响其余 30+9 件全部一致的事实。

---

## 2. 本轮已核 / 未核范围

**已核（本方亲自执行）**：§1 全部实测；`project-mainline-service.ts` 全文 818 行、`desktop-ipc.ts` 全文 212 行、`preload/index.ts` 全文 86 行亲读；`engine.ts` 关键段亲读（590–1120、1120–1335、1660–1724、2070–2140、2440–2614）+ 穷举 grep（`uncertain`/`#mainlineHoldingEntries`/`#intents`/`#fullIntents`/`#mainlineDeliveries`/`#mainlineRecords`/`clientId` 全部出现点）；fde 15 叶全部 diff 亲读（ci.yml、两 package.json、八 Python 文件、prepare 脚本 183 行全文、ZIP/.sha256/README）；`scripts/prepare-fr003-bundle.py` 逐行；`test_prepare_fr003_bundle.py` 用例清单与参数化展开；`test_frame_corpus.py` 新 cp1252 回归与 fixture；渲染端 `mainline-session.ts` confirm/pending 门禁段（430–545）；SOURCE-MAPPING/ENTRY/ACTUAL-PLATFORM/CLEAN-FULL-CHECK-002/THREE-FAULT-RESULTS/actual-five-JS 全文读；package-readback 关键字段（292B/`5d32103d…` 出现 2 处、`"bytes": 292` 3 处）；40 commits 全列核对；748→fde 28 叶改动面确认（主进程源/引擎源/契约/根 tests 零改动）。

**未核 / 无法确认（不以静态检查代替运行证据）**：本轮未运行任何测试/构建/引擎/GUI/网络（含 ls-remote）——fresh002 的 0 退出是**对既有冻结回单的独立复核**；"先 7 红后 60 绿"为任务书声明的 red→green 过程（结构与参数化用例逻辑一致，但本轮无权复跑）；Windows/Linux 参考设备与五龄设备；目标 macOS 15 真机；损坏 SQLite 物理 HOLD；D2 规模/执行计划；a11y 实测；RTL；第三方依赖 advisory（无网络）；docs/reviews 300+ 过程文档逐字（台账级）；远端分支保护设置；CI run 40063929148 的原件只读复核至日志文件在档，未发起任何远端查询。

---

## 3. 核心争议逐链独立复核（在 fde 工作树亲读实码）

> 结论先行：任务书第 17 行列举的每一条实现声明，我都在当前源码找到并核实；三个抛错条件的自然可达排除链成立；未发现遗漏的当前可达反例。以下每条【观察】均为本轮实读。

### 3.1 任务书声明的逐条核实

| 声明 | 实码核实 | 判定 |
| --- | --- | --- |
| 16 个完整未ACK/UNKNOWN 安全义务保留 | `desktop-ipc.ts:103-104`（"No timeout, navigation or new session deletes an unacknowledged receipt"）+ `:142`（唯一 `deliveries.delete`，精确 ACK 后）+ `:164`（16 槽上限）；`engine.ts:771`（`#mainlineDeliveries` 16 上限）+ `:978`（唯一 delete，consume 内）；UNKNOWN 态投递因 `consume` 前置 `state==='OFFERED'`（`:953`）永不可消费 | ✅ |
| consume 成功且无活跃使用才退完整 payload | `project-mainline-service.ts:637-660`：仅当最后一个 pending 令牌 ACK（size==1）、`active===0`、非 unknown、accepted 仍在时才 `releaseHolding(payloadEntry)` + `#fullIntents.delete`；多 pending 时各 ACK 只删自身令牌（`:642-644`） | ✅ |
| 紧凑原 operation 身份仍由原 128MiB/1048576 硬预算出资、不 FIFO 遗忘 | `service:621-630` `#keepIntent`：`retainHolding(intent, {operationId, request, engineSessionId, jobId})`，注释明示"prepaid separately and never FIFO-forgotten…hard budgets still bound its lifetime storage, including after payload retirement"；`#intents` Map 只 set（`:748`）无 delete；全局预算 `engine.ts:735-736`（134217728B/1048576 objects） | ✅ |
| 原 owner/request/session 匹配后旧操作只实际 job.get、不 job.create 重放 | `service:661-699` `#readAcceptedIntent`：`requestPinned('job.get', …)`（`:676`），六项全等校验（jobId/projectId/operationId/capability/confirmationRef/input，`:683-691`）；allowlist 确含 `job.get`（`engine.ts:1706`）；`intent.unknown` 前置 `denied()`（`:751`） | ✅ |
| 释放失败保留原 receipt/holding | 回调内 `releaseHolding` 抛错时先恢复 `intent.accepted` 再上抛（`:649-654`）；引擎侧 `consume` 的 retire 循环被中断时退款/删除全部不执行（`engine.ts:966-980`），已完成项已删、不重复退款；IPC 层 consume 抛错 `return permission()` 跳过 `deliveries.delete`（`desktop-ipc.ts:137-141`） | ✅ |
| 17 次 commit 单测覆盖正常预算退役 | 任务书声明 + 087-001 Z/MM 双方独立读证一致（17 次 `job.create`、末次 `job.get`、revision=17、每轮 `slots===0`）；本轮无权复跑，采信为既有冻结测试事实 | ✅（声明+历史双证） |
| retire 抛错后 preload 只有一次 ACK、无产品自动重试（实在限制） | `preload/index.ts:28-45`：恰好一次 `project:reply-received`（与 5s 超时 race），任何失败 `catch {}` 静默并照常返回 payload，注释"no retry/clear is fabricated"；无重发逻辑 | ✅ |
| 两条人为 throw 测试 + 直接 receiver.consume 不是产品自动恢复 | 两条测试（`t01-mainline-reply-lifecycle.test.ts:541-583` 人造回调抛错后直接 `s.receiver.consume`；`t01-mainline-real-runtime.test.ts` 一次性 spyOn `releaseHolding` 注入后直接 consume）均为注入+引擎级直调——087-001 双方逐字核对一致，本轮采信并独立同意该定性 | ✅ |
| 初次 await receiver 单飞 | `engine.ts:770-771` `#newDelivery` 在 `#mainlineComputing` 非空时 `invalidStateOrdinary`；`receive()` 全程持有 `#mainlineComputing`（`:908-909`，`finally :941-943` 清除）；`desktop-ipc.ts:171` 每个主链 handler 包在 `replies.receive` 内 ⇒ 主链 IPC 端到端串行 | ✅ |
| accepted 分支 active++→offer→finally active-- 无 await | `service:752-754` `active++` → `if (intent.accepted) return this.#offerIntent(intent)` 为同步段，`finally :796-798` `active--`；ACK 事件不能插入 | ✅ |
| 异步 job.get 只在最后成功 ACK 退役后、无旧 pending 回调 | `:755` jobId 分支仅在 `accepted===undefined` 时可达；accepted 仅由成功退役回调清空（`:648`），彼时最后一个 pending 已删、集合为空 ⇒ 无在册 retire 回调 | ✅ |
| pending token 仅由各自 callback 删 | 令牌在注册下一行同步加入集合（`:658`），仅自身回调删除（`:643/:655`）；无跨删除路径 | ✅ |
| unknown 仅首写阶段 | `unknown=true` 仅 `:756`（job.create 前）与 `:775`（job.create 失败且 `queryWriteEntered(pin)`）；`:787` offer 前置 false；`writeEntered` 仅在最终 pin 校验后、stdin.write 前置位（`engine.ts:2558`）——到 stdin 边界而非持久受理，QUEUE_FULL 两处（主进程容量拒在 write 之前 / Python 队列拒在已发送之后）语义不同，处置区分正确 | ✅ |
| releaseHolding 拒绝看 entry/record 而非 currentSession | `engine.ts:872-883`：唯一拒绝条件是 holding 不存在或 `holding.record !== record`，注释"Old owner cleanup may close its own logical holding after a session change"；`bytes===0` 幂等返回；`onReplyConsumed`（`:1059-1079`）另核同 entry/record/session + holding.bytes!==0 + 单 delivery ≤16 + 预留 512B/8obj/4096 | ✅ |
| payloadEntry 私有固定对象、budget 固定 record、holding WeakMap 无 delete | `payloadEntry: Object.freeze({})`（`service:742`，模块私有）；`budget` 在 intent 创建时取 `queryReadBudget(current.owner)` 固定绑定（`:741`）；`#mainlineHoldingEntries` 穷举 5 处仅 get/set（`engine.ts:646/838/869/873/892`），无 delete | ✅ |

### 3.2 M1/M2/M3 与相邻观察在 fde 的现状（均为【观察】）

- **M1 uncertain 单向闩锁**：穷举 7 处出现点——声明 `engine.ts:276`、读 `:714/:957`、赋值仅 `= true` 四处（`:822` UNKNOWN 投递、`:2098` #finish 在途、`:2501` 请求超时、`:2566` stdin 写抛错）。无复位、无删除。逃逸条件是引擎会话更换后 `mainlineProjectClient()` 铸新 record（`:1164-1167`），不是应用重启；health/tasks/job/result/operation 不经 `#mainlineReady`。**未修复、如实保留。**
- **M2 跨 session 创建/示例原回执不可对账**：hello 每次握手 `clientId: randomUUID()`（`:2265`）+ `engineSessionId` 逐会话更换 ⇒ 新会话重提同 operationId 必 `IDENTITY_CONFLICT`（引擎侧 origin 全等比对，085/087 双方已逐字核；本轮确认 TS 侧无变化）。恢复白名单确含 `job.get`/`operation.get`（`:1695-1711`）——全局化结论不成立，创建/示例专属限制保留。
- **M3 十六义务容量拒绝**：三个独立 16 容器（IPC `deliveries`、引擎 `#mainlineDeliveries`、service `#fullIntents`）+ `#mainlineRecords` 第四个 16（`:1167`，只 set `:1310`，初始 1 + 15 次会话更替可达上限）。可达耗尽事实保留，不 FIFO、不无偿退款。
- **N1（失败提交占 fullIntents 槽）**：`service:749` 在真正 payload 之前加入 `#fullIntents`，唯一 delete 在退役回调（`:656`）——**事实确认**；但渲染端 `confirm()` 有 pending 门禁（`mainline-session.ts:441-450` 已有 pending 即拒绝新确认），新 UUID 仅在确认链成功后铸造（`:479`），失败保 reserved pending 为 unknown（`:539+`）——"16 次任意 UI 失败即耗尽"的推广不成立；已入线（writeEntered）与未入线失败重试权限不同，处置的保守保留正确。
- **N2（提交往返期间 source 变化）**：`service:788` handoff 先于 `:789` `source.current()` 检查——`ok:false` + alias 非空 ⇒ `engine.ts:926` 转 UNKNOWN——**机制确认**；两容器各计 1 槽、不相加为"8 次满两 16"；receive 直接 reject 时不产生 IPC delivery（`desktop-ipc.ts:172-174` 在 deliveryId 生成前返回）——算术更正确认。
- **scratch 预算**：`engine.ts:758-769` 高水位摊销（`Math.max` 只补差量）确认；`#holdingSize`（`:824-833`）`32*UTF8bytes+4096` / `raw.length+128` 为**保守计费单位，不是实际 RSS/堆测量**——任务书口径（"预算是保守高水位工作预算，不冒称实际 RSS"）与代码一致，不提供固定耗尽数字。
- **本轮附加边角搜索（未产生新反例）**：重复 ACK 同 deliveryId（IPC `accepted` 幂等 `:127-151` + 引擎 `#mainlineConsumed` `:948`）；ACK 乱序（size>1 删自身/size==1 正常退役）；首次 `job.create` 各失败分支（writeEntered 决定 unknown/denied）；渲染端中途崩溃（preload ACK 未发 ⇒ 双 16 槽各留一个未 ACK 责任，M3 设计内）。

### 3.3 判定

与 087-002 双方结论一致且经我独立重建：**retire 回调三个抛错条件在当前产品入口与不变量（单飞串行、同步块、私有冻结 entry、WeakMap 无 delete、固定 record）下无自然触发；一旦因故障注入或未来重构发生，产品层无恢复入口（单次 ACK 被吞 + IPC 返回 PERMISSION_DENIED + 引擎级精确重试在产品路径不可达）——"保留责任正确、保留后无产品释放通道"的潜伏脆弱性如实保留**，加固方向（仍有效原 frame/session 对同一 deliveryId 的有界私有 ACK 重试）登记未实施，本轮不要求。不把引擎 handle 可重试说成产品重试，不以人为 throw 推正常 16 次泄漏。

---

## 4. base→fde 累计代码审查（40 commits / 546 files）

### 4.1 结构与改动面

40 提交全列核对：产品实现集中在 `03376dfb…b6edf213`（私有事务/补偿/Job3 claims/format3 契约/CAS/ChangeSet/undo/主线集成）、`7d30ab34`（恢复权威与已完成 principal 退役）、`dd21ab12`（M4 两层退休）、`748008a6`（T02 单快照观测）、`58419ec4`（13 份归档文档）、`fde989ac`（CI 输入可复现，15 叶）；其余 24 个为 docs/契约冻结过程提交。748→fde 仅 28 叶（+3335/−8），**主进程源码、引擎源码、契约、根 tests 目录零改动**——087 两对双审精读的实现即当前 fde 实现，我本轮对关键承载件的全部亲读结果见 §3。58419ec4 为纯归档（package087 固定头双审证据 13 文件入 `docs/reviews/T01/package087-748008a6-pair002/`），不改产品。

### 4.2 五条任务书边界的累计复核结论

1. **创建/补偿/owned draft/重启**：创建为显式应用事务、幂等认领（operation_claims）、genesis 验证后重建 candidate；示例复制两阶段 replay-first、哈希钉死 bundle + TOCTOU 复查；补偿纯函数零 SQL 写入、ABA 保护、从不可变历史重建退役面；owned draft = `app_drafts` 逐 (project,editor) 代际 CAS；重启 `reconcile_jobs` 在取得 OS 写租约后把非终态 Job 判 `ENGINE_EXITED`（"marker alone can never invent success"）。（085/087 双方逐字核 + 本轮 TS 侧无变化确认。）**未发现缺陷。**
2. **T02 完整 Diff/commit/undo/redo 与原回执**：Diff 为引擎文档分页拉取 + 逐段/整档 SHA-256 + 严格 UTF-8；commit 三次 currency 检查 + 先 CAS 书签后域写 + marker 七字段回执；undo 为服务端补偿性新事务；无独立 redo UI（FR-804 未要求，功能缺口留账）。748 的单次 `evaluateAll` 同步快照 + 新增重复 region 拒绝（原断言全保留）。本版 088 真实 E2E T02 两例 PASS（5.1/5.0s）为运行闭环。
3. **T04 分页/历史快照/导出**：服务端 keyset cursor + 快照绑定 + 显示层严格校验；历史列表钉死 `listSnapshotId` 严格单调；导出当前页 CSV（BOM/CRLF/注入防护）——全量导出/JSON/XLSX 为留账缺口。本版 088 实测 243 ordered rows 跨页全读 + CSV + history PASS。
4. **首次 ACK 丢失/项目切换**：IPC 回复层注入的 e2e 断言 `commitCalls===1/executeCalls===0/lostAckCalls===0` + 真实 listJobs 恰一 Job；切换隔离（selection fence + fingerprint + per-project CAS）；N2 的 UNKNOWN 资源处置缺口见 §3.2。
5. **main/task/engine session/epoch/权限/持久 Job/marker/noReplay/资源 stage/干净 checkout**：四个 generation/epoch 已分清；权限面（owner/principal/budget/allowlist、trusted 三重校验、preload 闭合命名面）本轮在 desktop-ipc/preload 全文复读确认；持久 Job 结果恒从引擎重读；marker 与回执同事务；noReplay 只读恢复；资源 stage 见 §4.3；干净 checkout 可构建性由 fresh002 实证（§5.1）。

### 4.3 fde 最新 15 叶逐项复核（全部【观察】）

- **`.github/workflows/ci.yml` +4**：恰在两个 checkout（quality/mac 作业）补 `fetch-depth: 0`——对应真实 CI 中 shallow depth 缺固定 5f reader 的失败；windows 作业未动（其失败是 cp1252，由下一项修）。
- **六 Python 文件 8 处显式 UTF-8**：精确计数 `encoding="utf-8"` = binding_regressions 1 + ordinary_library 1 + project_source_table_material 1 + project_business3_contract 2 + query_definition_service 2 + query_presentation 1 = **8 处**，全部为模块级 fixture 装载点；`test_frame_corpus.py` 新增 `test_shared_corpus_modules_keep_utf8_under_cp1252` 参数化**恰 7 个 module/variable 对**（CASES/PROFILE/REGRESSIONS/CORPUS/FIXTURES/BINDINGS/DATA）在 cp1252 默认下 runpy 重载并断言语义相等——"7 真实 module cp1252 回归"确认。`cp1252_contract_default` fixture 只对三个 fixture 资源注入平台默认、不动全局编码，注入点在 `io.text_encoding` 解析之前——设计精确诚实。原有故意错误默认 cp1252 对照与所有旧 assert 保留；"先 7 红后 60 绿"为声明的过程事实（结构一致，本轮无权复跑）。
- **T09 ZIP 跟踪**：`resources/examples/equipment-maintenance-resource-source-v2.zip` 1344035B/`b8717a53…` + 同名 `.sha256` pin + README（22 件、解包 1338939B、provider 198B、load-input 10930B、来源与边界声明）。
- **`scripts/prepare-fr003-bundle.py`（183 行，逐行亲读）**：stdlib 严格 ZIP 校验——ZIP 整体字节+SHA256 恒等、恰 22 个唯一成员、前缀/绝对路径/`..`/反斜杠/目录项/符号链接/非常规文件全拒绝、manifest 7566B/`23de1c47…` 双 pin、manifest 成员集合与 ZIP 成员集合全等、逐成员 size+SHA256（`zipfile.read` 同时验证 CRC）、聚合 1338939B；staging：目录符号链接拒绝、协作锁 `O_CREAT|O_EXCL` 0o600 + 清理时 inode 归属核对、owned temp `mkdtemp` + `xb` 独占写、POSIX 文件 0444/目录 0555、改名前 `verify_tree` 复核、准备期间目的地出现即拒绝；**既有 stage 只复核、缺失/变更/额外成员拒绝不覆盖**（"Existing staged bundle changed; it will not be overwritten"）；注释明示"not a no-replace guarantee against unrelated concurrent writers"——不宣称防非合作外部写者竞态，与任务书口径一致。
- **`test_prepare_fr003_bundle.py`**：7 个测试函数、参数化展开恰 **14 例**（干净 stage 完整+幂等；坏 stage 3 变体拒绝不修复不改写；换 archive 拒绝；结构 4 变体 duplicate/escape/symlink/unknown；既有锁不删；链接 3 位置拒绝且不写目标；可写成员拒绝不 chmod 修复）——"14 资源负例/竞态测试"精确确认。
- **package.json/pre 钩子**：根新增 `prepare:examples`（`uv run --frozen python scripts/prepare-fr003-bundle.py`），挂 `predev`/`prebuild`/`pretest`；desktop 新增 `prepackage:dir` → 根 prepare——四个钩子**只做 prepare，不塞入新 build**，与任务书一致。
- **ASAR 内 package.json 292B**：package-readback 内 `"bytes": 292` 3 处（旧/新/实际）、`5d32103d76e4bcb57e9a9438fcb1453a4601ee0f2405dcd5d049a29dfab8e373` 2 处——workspace scripts 经原 builder transformer 剔除后三份一致，确认。

**fde 15 叶定性：纯 CI 输入可复现性 + 资源 stage 加固，不改产品源码、不放宽任何断言、严格增量验证；无新增实现缺陷。**

---

## 5. 088 证据链独立核验

### 5.1 干净 checkout（fresh001 真败保留 / fresh002 全量 0）

fresh001 自身 npmci/uvsync 0 但直接 `npm check` 无 python 导致 1692 PASS / 2 FAIL（spawn python ENOENT）、完整 check 1——**真败保留，不洗绿**。fresh002：独立 clean-checkout-002（实际分支 `refs/heads/feature/weekly-t01-project-transactions` @ fde989ac，非 detached；旧 clone001 才 detached）、独立依赖、原入口 `uv run --frozen npm run check` **自然 0 / 147.099s**（ENTRY counts：TS 35 文件 1694 PASS、Ruff 345、Python 3466 PASS + 44 SKIP = collected 3510、1 个故意 duplicate ZIP warning）；tracked 1288 源 before/after 相同（BEFORE/AFTER 同哈希 `0d7c24c9…`）；`initialBuildReleaseOutAbsent:true`、`ownFreshDependencies:true`。SOURCE-MAPPING 严格映射：S 实际（含 15147B overlay AGENTS）与 check（含 1056B 已提交 AGENTS）**唯一差异叶 AGENTS.md，其余 1287 叶逐字节相同**——两份 AGENTS 不同、不混称全同。ENTRY 的 `goal:"paused"` 与 pending 状态为**原历史字段保留**（本轮按任务书注明当前 ROOT Goal 为 active/inProgress、用户已授权继续本 pipeline，不以该历史字段宣称当前暂停）；`remotePush:false`、`CI:"old584 first three jobs all FAILED; no new CI claimed"`、`mergedUsableFRs:"0/17 unchanged"` 原样。

### 5.2 package088 唯一实际包

T11 `package:dir` 一次自然 0；直采 C002 新 JS（五 JS 与 actual-five-JS-fde989ac.json 逐件一致，main 594342B/`f8fd1490…` 仅开发 nonce 字面量与 087 不同、其余四输出同）、不 build JS/engine、复用真实 888 engine（`43efc368…` 实测吻合）。fresh002 npmci 首次准备因 Electron dist/path 缺失失败（metadata 9 但 dist 缺）——**真败保留**；ROOT 授权复制 N 已存在同版本 Electron dist（595 members + path.txt 36B）逐叶核、无下载/备用版本/源码变化，saved-binding 保留完整失败与供应记录。APP910 叶/Resources290 regular/engine266（225+41）/ASAR819 文件/五 JS 完整实读；stage 原 22 文件/11 只读目录（0555/0444）逐叶同；根包 builder dirs 0755 与原 stage 0555 分别记录。ROOT 受理票 111553B 哈希一致，603 delivery leaves + 35 refs 物理接受。**helper timeout=false 仅为 child.wait 自然 0 + driver 完成的推断；package 回执 1790 字节（ROOT acceptance `raw1790receipt` 原文核验）、`timeout:false` 为该 JSON 直接字段、wrapper 原预算 300 秒——按用户勘误更正表述，"1790"不是秒**，两类证据不混同。

### 5.3 完整 E2E + 三故障 + coordinator + native

full_e2e088：18 collected = 16 PASS + 2 原平台条件 skip（原 npm 入口/worker1/retry0/300s 与 30/60/90 未改；91.04s；outer/NPM/driver/APP 自然 0；T02 两例 5.1/5.0s；T04 243 ordered rows 完整分页/CSV/history PASS；16 附件实际新 app.asar/argv 绑定 owned profile；process direct resourcesPath/execPath getters 仍 null UNKNOWN 不回填；observer 216 采样 errors[]；有限 113 knownPIDs absence 不等全局 reap；relative label 无前缀导致 `exactReportedRelativeLabelsMatch=false`、collector normalize 后 18 全同 missing/unknown=[] 不隐瞒；原 full18 不因后续 renderer 操作错误重跑）。三在途故障各有 PASS（reload/renderer-recovery/coordinator-exit，原 queued/running 前提/faultApplied/Job/marker/noReplay 断言不变；coordinator 首次 PASS 5.47s，原 Job 身份读回 failed/ENGINE_EXITED/validationPASSED，全自然 0）；绝不说整个产品流程 0-retry。native 首次 0-retry PASS：160.14s（180/190s 预算内）、三窗口、真实 responses 0/0/1、真实 Cmd-Q、beforequit 22.666Z→thirdclosed→willquit 22.677Z、APP 22.735Z 自然 0、无 forcedFailure、有限 knownPIDs absence；**第 1 个 0（05:58:48.623Z）早于 T01 任何 CUA 输入，来源 UNKNOWN、是否人工输入未确认——保持 UNKNOWN，不称全自动、不归因用户/产品，且不属 05:54:08Z 人工确认范围**。三 fault/native 原串行顺序因独立 profile 允许先 coordinator/native 再补 renderer，ROOT 各有新直接真票；不是接受 renderer FAIL 或改断言。

### 5.4 renderer 三次（FAIL/FAIL/PASS，如实保留）

1. 第 1 次真实 FAIL（original case inner deadline）：65s prompt 05:46:23.997Z、失败 05:47:27.793Z、APP 74021 清理 exit0 于 28.126Z；CUA 精确 getApp 输出 27.507Z 已只剩 286ms、click 调用 32.940Z 晚于 exit 4.814s——不能当活跃 dialog 的 API 签名 bug；随后 bundleID 歧义 displayName fallback 误开旧 `/OntoLearn-Studio/release/mac-arm64` 包并于 05:48:07.183Z 发 CmdQ、无当时物理 exit 证明。最初记录"时刻未录"后从本 chat 正式 session 恢复为更正时间线，旧原件不改。
2. 第 2 次新 namespace 真实 FAIL：prompt 05:54:01.521Z、**response1 于 05:54:08.290Z 早于本轮 CUA getState/getApp/freshAX 调用（12.283Z）**；CUA 只见 blank window/截图、无 click/键盘。**来源补充（用户可信确认）：该 05:54:08Z 时刻存在人工点击或键盘输入；具体按钮/按键未确认，不据此推断具体输入机制，也不归因产品或本轮 CUA；原 response1 与真实 FAIL 保留，先前 UNKNOWN 原始记录不覆盖，由本补充更新输入来源；仅对应 13:54:08（05:54:08Z）renderer 第 2 次，不涵盖 05:58:48Z native 第 1 个 0。**终态 outer/driver 1、APP cleanup 0 不洗 FAIL。
3. 第 3 次真实 PASS：新 namespace、原 7 源逐字节同、65/75s/全部 assert 不变；prompt 06:04:20.054Z、T01 精确 path + 显式 freshAX 唯一 button4 真实 click、response0 于 40.122Z；window2 新建/load、原 Job `6686f607…` 原 job.get succeeded validationPASSED、domain/marker/noReplay 全 PASS；24.84s、outer/dispatcher/driver/APP 全自然 0；click+getAX 批次末"App quit"为验收通过后 cleanup 的工具读回失败、未再 getApp；06:05:18Z knownPIDs scoped 无匹配仅有限样本。

### 5.5 真实 CI 三失败保留

PR6 当前 remote head 58419ec4（**fde 尚未 push**）；run 40063929148 三 job 真实 FAILED：Windows cp1252 读取、quality 干净 checkout 缺忽略 T09/T11 bundle、mac shallow depth 缺固定 5f reader；原 stdout 三件在档。fde 的 15 叶正是针对此三失败的修复，但**不得以本地绿说远程已绿**；三失败原样保留至远端真实全绿。

### 5.6 平台事实更正

实际宿主 **macOS 27.0.1 / Darwin 27.0.0 arm64**（ACTUAL-PLATFORM-AND-C002-BRANCH.json 实读：`sw_vers`→27.0.1、`uname`→Darwin 27.0.0 arm64、C002 分支/HEAD 读回）；**macOS 15 arm64 仍为批准的目标兼容平台、UNVERIFIED**。旧 087 报告/旧 prompt 中"15 actual"文本为历史错误，原件保留、本轮不沿用。本报告所有"内部演示 PASS"的平台依据是实际宿主 27.0.1，**目标 15 兼容性属 formal/平台 HOLD**。

---

## 6. 最值得修复的 10 项（按严重度；每项区分【观察】/【推断】）

1. **【High｜发布流程｜观察】真实 CI 三失败未在远端闭环，fde 未 push。** PR6 remote head 仍 58419ec4；run 40063929148 Windows/quality/mac 三 job FAILED；fde 15 叶为针对性修复且 fresh002 本地全量 0，但 0/17 要求 push→PR→CI 真实全绿→squash develop→远端复核。风险：流程阻断，本地绿不能预告远端绿（clean checkout 的平台差异正是本轮三失败来源）。建议：推送 fde、观察三作业真实结果；任一失败即新候选重走。
2. **【Medium-High｜可用性｜观察+推断】M1 uncertain 单向闩锁（含 records16 同族）。** `engine.ts:822/2098/2501/2566` 仅置位无复位 + `#mainlineRecords` 只 set（`:1167` 上限 16）。触发：同 live engine session 任一主链超时（>5s）/UNKNOWN/引擎死亡在途；或会话更替累计。后果：该 session 主 project/query 全拒（health/tasks/job/result 不受影响），极端长会话后主链进程内不可恢复。建议：文档化"重启会话/应用"自救；未来按原操作对账证据设计复位（不得简单忽略 uncertain）；把容量/闩锁拒绝映射为可操作错误码而非 PERMISSION_DENIED。
3. **【Medium｜长会话容量｜观察】M3 十六义务容量拒绝（两个真实来源）。** IPC `deliveries` 16 / 引擎 `#mainlineDeliveries` 16 / service `#fullIntents` 16；来源一：ACK 丢失（preload 静默）→ stale pending 令牌永存 → payload 永不退役永占 full 槽；来源二：已入线（writeEntered）写失败的 unknown intent 永占槽。触发：单会话累计 16 次投递 ACK 丢失/UNKNOWN。后果：主链容量拒绝直至重启。这是 owner 明确保留的安全语义（不 FIFO、不假作 ACK），非缺陷；建议 UI 明示容量状态与自救路径。
4. **【Medium｜健壮性｜观察】故障注入下 retire/consume 失败无产品恢复入口。** §3.3：机制属实、自然触发未证成；一旦发生（未来不变量被破坏）每次泄漏 1 引擎槽 + 1 IPC 槽且产品单次 ACK 被吞。建议（未来候选）：对仍有效原 frame/session 的同一 deliveryId 做有界私有 ACK 重试（保原记录/载荷/计费，不重发 commit/job.create）；当前不要求为未证成的自然故障实施。
5. **【Medium｜对账｜观察】M2 跨 session 创建/示例原回执不可对账。** origin 绑定逐握手 `clientId: randomUUID()`（`engine.ts:2265`）+ engineSessionId。触发：引擎在"已持久化提交后、回执抵达前"死亡后重试。后果：无重复项目（守卫有效），UI 停留"创建结果尚未确认"需人工核对。建议：长期按原合同以"重新证明原 dispatch 物理绑定"设计 resolution；不删 origin、不新增持久意图账本。
6. **【High｜正式发布｜观察】签名/公证/身份缺失 + 仅目录包。** `identity: null`、三平台 `target: dir`；ROOT 受理票 `signedReleaseGate:false`、deep codesign exit 1。对外分发硬阻断（内部演示已授权范围）。
7. **【High｜正式发布｜观察】wholeAPP legal/`_distutils` 来源闭包未接受。** `legalFullClosureAccepted:false`、`mechanicalClosureOnly:true`；ASAR 内 package.json 292B vs 原始的差异为已记录的打包规范化。
8. **【Medium｜数据韧性｜观察】用户级备份/恢复实测缺失 + 损坏 SQLite 物理 HOLD（B/C 未授权）。** 迁移备份强制可验（integrity_check + 源哈希复查），但无应用内项目级备份/恢复入口、无恢复演练；损坏库唯一路径是拒绝启动。另 PRD FR-002 项目导出、FR-203 Turtle 导入导出、FR-300 CSV/XLSX 接入为未完成 P0 条款，本内部子链 PASS 不冒称完整 MVP。
9. **【Medium｜平台/规模｜观察】跨平台/参考设备/D2 未实测，目标 macOS 15 UNVERIFIED。** 全部真实运行证据在实际宿主 macOS 27.0.1；目标 15 兼容、Windows、五龄设备、负载/索引执行计划（无显式 CREATE INDEX，有 UNIQUE 隐式索引）均未验。
10. **【Low-Medium｜合规/UX/卫生｜观察】a11y 未核 + i18n 单语 + 工程卫生。** 键盘导航/读屏/对比度无合同事实；全部文案硬编码 zh、messageKey 携带不渲染、局部 NaN 插值；`job_store.py` 2589 / `engine.ts` 2623 / `semantic.py` 1627 行超 2000 行线；无 CHANGELOG/Terms/Privacy；appId 个人命名空间；Dependabot 不覆盖 Python；8 个悬挂 import 的 profile 死分支（不可达，落地雷）。

**其余阻断/缺口完整保留（不清零）**：C4–C6 三次配对失败与 D8 人工裁决、47 阶段指定双审积压、真实 LLM（S3 前不接入）、静态加密与设备失窃预案、渗透测试、安全问卷证据包、"谁查看过"审计、全屏状态/表单保留/后退语义逐项、依赖 advisory（无网络未核）、分支保护远端设置、086 首败/087 guard 首败/first full001 首败/renderer 前两次 FAIL 原件。

---

## 7. 用户 11255B 清单逐项适用性（160 引用行：147 产品 + 13 人员）

> 原则：先判适用性；不适用按类别说明依据；适用未核实写"无法确认"；不为满足清单扩建无关功能。产品形态：本地优先、单用户、离线、无服务端、无网络端口（CSP `connect-src 'none'` + 引擎 audit hook 断网）、无账号体系、无计费、S3 前无模型接入。

### 7.1 整类不适用（按类别）

| 类别 | 覆盖条目 | 依据 |
| --- | --- | --- |
| 账号/身份 | login+/邮箱、密码重置、MFA 及恢复、会话超时/全踢、SSO、SAML、SCIM、登录限流、防误锁、按 URL 改号越权、租户隔离、admin 代登录+审计 | 无服务器/登录/多用户多租户；IPC 以 sender/frame/文档三重校验替代。一旦引入共享即整类适用且零基础 |
| 支付/计费 | money 整数、汇率/税、订阅/按比例、催缴、PO 发票、VAT、退款、计量对账、年约、收入报表 | 无任何货币处理 |
| 对外 API | 版本化对外 API、API key、API 限流、第三方变更预案、OAuth 刷新、集成沙箱、webhook 签名/重试 | 无对外 API/webhook；私有 stdio 协议为设计契约（schema+registry 双端校验） |
| 邮件 | SPF/DKIM/DMARC、退信/投诉、邮件渲染 | 不发邮件 |
| 云基础设施 | dev/staging/prod 云语义、IaC、零停机、一键回滚云语义、功能开关、自动扩缩、CDN、DNS/SSL、二区域、DR 年度演练、状态页、成本告警 | 无云无端口；本地等价：CI 门禁、目录包回滚 |
| 观测/值班 | 3am 可搜日志、错误聚合、外部拨测、告警、仪表盘、tracing、on-call、runbook、postmortem（云语义）、状态页 | 无运行服务；产品零日志策略为隐私取舍（固定错误码+受限参数）；postmortem 文化以本地形态实际运作（C4-C6/086/actual001 记录→更正→实现改变） |
| 合规套件 | SOC 2、HIPAA、BAA、PCI、GDPR 全表删除、数据驻留、季度访问复核、渗透测试、安全问卷 | 不处理 PHI/卡号/第三方 PII；转为"首个企业客户前义务"；SECURITY.md 已有私有披露约定 |
| 流量/规模云侧 | 连接池、周一尖峰、负载测试、5M 行超时、cron 防重、死信队列云语义、存储生命周期 | 嵌入式 SQLite 单写者 + 独占租约；无定时/队列服务；规模口径归 D2 |
| 通知/其他 | 通知开关、酒店 wifi 加载、文件上传扫描、CSV 2009 导入 | 无通知系统；离线；无上传面（导入=内置示例，主进程硬指定路径 + 严格 ZIP/stage 校验——fde 新增加固为本条本地等价物） |

### 7.2 适用且本轮已核（有实现与证据）

- **designed schema**：contracts/v2 schema+registry+errors 单一契约源，TS zod `.strict()` 与 Python 校验器双端执行。
- **深于 admin 的角色/权限**：owner/principal/budget/能力白名单（本轮 `engine.ts:1695-1711`、desktop-ipc/preload 全文亲读）。
- **服务端校验/输入消毒**：主进程+引擎双侧（等价形态）；标识符 schema 锁定、自由文本 UTF-8。
- **SQL 注入**：参数化 `?` 绑定全量（抽查 job_store/storage/lifecycle；唯一动态为 SAVEPOINT uuid4hex 内部生成）。
- **XSS/CSRF/CORS/安全头**：React 转义 + CSP 唯一源（生产无 unsafe-inline/eval、connect/object/base-uri/frame-src/form-action 'none'）；无 HTTP 面。
- **秘密出库/轮换**：无密钥存在（无模型客户端）；env 白名单不继承凭据；轮换随之不适用。
- **包确认/依赖扫描**：直接依赖精确 pin + uv.lock sha256 + licenses 闭包；Dependabot npm+Actions（Python 手工为留账缺口）；advisory 状态无法确认（无网络）。
- **最小权限（含 AI agent）**：preload 闭合命名面（本轮全文复读）、特权引擎参数仅主进程构造、Agent 未接入且 registry 声明不得自确认。
- **日志不记敏感/审计**：零日志 + 固定错误码 + paramsSchema 受限；"谁改变"完整不可变（commits/commit_evidence/operation_claims），"谁查看"仅查询侧元数据——部分。
- **幂等键/重复点击去重**：operation_claims 同事务、marker 幂等、17 次恰 17 次 job.create、ACK 丢失零重放 e2e；已入线写拒绝自动重放（`service:751`）。
- **分页 page 400**：T04 路径 keyset cursor + 快照绑定 + 严格显示校验（性能未量化归 D2）；本体事实/定义表为整表传输+渲染切片——该子路径不满足（留账）。
- **导出**：当前页 CSV（BOM/CRLF/注入防护）；全量/JSON/XLSX 缺（FR-402 相容、FR-002/203 缺口留账）。
- **软删除/保留规则**：retirement 显式建模 + 不可变历史 + 快照链（更强等价形态）；缓存回收不触历史；"按合同删除"保留期规则不存在（部分）。
- **时区**：epoch 毫秒/单调钟，无 naive 本地时间。
- **撇号/emoji/重音**：字面量层 strict UTF-8 全链 + 代理对拒绝；标识符层有意限 `[A-Za-z0-9_.-]`；RTL 无法确认。
- **数据模型抗变化/迁移**：版本化 schema + migration_log + v2→v3 显式迁移 + user_version 断言 + 启动结构审计；**单向向前**（无降级），回滚=迁移备份（文件级）——"forward and roll back"半满足；启动期独占租约短事务（单机无 2pm 锁表问题）。
- **备份/恢复**：迁移备份强制可验；**恢复实测未做**；夜间备份/PITR 云语义不适用（快照链+补偿为本地等价能力，非 WAL PITR）。
- **缓存与失效**：invalidation-v2.json 唯一规则源；仅改模型配置不作废领域结果；历史/失败/取消不计过期。
- **后台任务/带退避重试/DLQ**：持久 Job + claims + 恢复 + 有界 worker；主进程三次/指数退避/attemptToken；引擎重启对账不重跑；DLQ 无独立视图（部分）。
- **undo**：服务端补偿性新事务 + ABA 保护；本版 088 e2e T02 Undo/Undo-of-Undo PASS；独立 redo 无（FR-804 未要求，留账）。
- **AI 人工批准**：结构性成立——registry `requiresConfirmation`、confirm 仅 trusted-host、Agent `agentEligible=false`、确认按钮在完整 Diff 全部行展示后可用；其余 AI 条目（提示注入/数据出提示/花费上限/evals/降级/弃用/提示日志）S3 前不适用，接入后整类适用。
- **单测/集成/e2e/回归/测试数据**：1694 TS + 3466 Py（fresh002 回单实读）断言具体预期集合/顺序；18 例真实 Electron e2e；专项回归集 + fde 新增 14 例资源负例/竞态 + 7 例 cp1252 回归；fixtures 合成、.sqlite/.env 禁入。
- **空/加载/错误态、可行动错误**：主链/查询两模块专门分支；固定码+受限参数不回传堆栈；全屏覆盖/逐表单保留/NaN 插值——部分。
- **代码可读/ADR/README/继承者文档/分支策略/每变更评审**：strict+ruff；ADR 0001-0003；README/CONTRIBUTING/docs 树（"一小时"无法确认）；worktree+feature 分支+指定双审（本报告即一环）；分支保护远端设置未核。
- **事后复盘改变些什么**：C4-C6/086/actual001/renderer FAIL 记录→更正→实现实际改变（dd21/748/fde 为实例）。
- **披露流程**：SECURITY.md 私有渠道约定。
- **加密**：传输=无网络（最强形态）；静态=SQLite 明文（本地优先取舍、明示记录；设备失窃预案未建立）。

### 7.3 适用但无法确认 / 未满足（如实登记）

五龄设备/Windows/Linux 参考设备/**目标 macOS 15**（实际宿主 27.0.1）；渗透测试；安全问卷证据包；"谁查看过"审计；a11y 合规（键盘/读屏/对比度/树形 aria/切换焦点）；i18n/locale 格式化/RTL；全屏空/加载/错误覆盖；表单失败保留输入全覆盖；后退按钮语义；README 一小时实测；2000 行拆分与死代码清理（含 8 个悬挂 import 死分支）；changelog/terms/privacy；公司名下账户/域名/repo（appId 个人命名空间）；按合同删除的保留期；依赖 advisory；Python 依赖自动扫描；DLQ 视图；正式发布流水线（check→打包已核，push→PR→CI→merge 未发生）；dev/staging/prod 一致性系统核验。

### 7.4 13 条人员角色条目

无法从仓库证据确认人员配置与轮值（组织事实）。可核实对标：指定双审+独立复核+CI+总控记录本轮实际运作；单人创始人 + 个人名下仓库的 bus factor=1 为真实组织风险，与代码判定分开记录。

---

## 8. 内部演示范围最终判定

**PASS。** 直接依据（均为本轮读证/亲读实码）：

1. 仓库身份与状态全对（§1）；cached diff 空，唯一未暂存项为受保护 AGENTS overlay；1288 源严格映射唯一差异叶即该 overlay。
2. 核心不变量在 fde 实码逐项成立（§3/§4）：版本化单一提交路径、不可变历史、幂等不重放、渲染端隔离、CSP 唯一源、固定错误码边界、无模型/遥测/云、引擎无网络出口；未发现数据损坏、越权写入、凭据泄露、注入或可利用鉴权缺陷；全部保留限制为会话内可用性/容量性质且重启可恢复。
3. fde 15 叶为 CI 可复现性 + 资源 stage 加固（8 处 UTF-8 + 7 回归、fetch-depth×2、T09 ZIP + 183 行严格 prepare + 14 负例、四个 pre 钩子只 prepare、292B package.json 三份一致），无产品源码变化、无断言放宽。
4. 088 运行证据：fresh002 全量 check 自然 0；package088 机械身份/资源闭包/ROOT 物理受理；完整 E2E 16 PASS + 2 原平台条件 skip；三在途故障各 PASS；coordinator 首次 PASS；native 首次 0-retry PASS（第 1 个 response 来源 UNKNOWN 如实保留）；renderer 第 3 次真实 PASS（前两次 FAIL 原样保留，第 2 次输入来源已获用户人工输入确认、仅限 05:54:08Z）。
5. 历史失败与限制全部保留未清洗：086 首败、087 guard 首败、first full001/fresh001 真败、CI 三失败、renderer FAIL×2、native first0 UNKNOWN、C4–C6/D8。
6. 两项任务中事实补充/勘误（renderer 05:54:08Z 人工输入确认；1790B 回执/300s 预算）经原件核验采纳，未据此变更任何产品/验收结论。

**保留 HOLD（正式分发/其他平台，独立判定，与上互不抵销）**：签名/公证/身份；wholeAPP legal/`_distutils`；Windows/跨平台/参考设备/**目标 macOS 15（UNVERIFIED，实际宿主 27.0.1）**；真实 CI 三失败远端闭环（fde 未 push）；损坏 SQLite 物理 HOLD（B/C）；用户级备份/恢复实测；D2 规模/索引；a11y；静态加密与设备失窃预案；渗透测试与安全问卷；PRD P0 缺口（FR-002/203/300）；真实 LLM（S3 前不接入）；C4–C6/D8/双审积压；**0/17 发布流程（push→PR→CI 全绿→squash develop→远端复核，本审查者无权限且未发生）**。

**内部演示 PASS 的不稳定边界（明示）**：若范围扩大到长时值守、无人值守、大数据量或多人/多环境，§6 第 2/3/4/5 项应立即升级为阻断（重启不再是可接受的无人值守恢复手段）；本 PASS 仅在用户明确的"非正式分发，仅限内部演示"范围内、在实际宿主 macOS 27.0.1 上成立。

---

## 9. 自我限制与合规披露（如实记录）

- **只读**：未修改任何产品文件/测试/配置/标准/索引/证据；未运行新 build/安装/GUI/APP/engine/测试/打包/网络（含 ls-remote）；所有 Git 命令带 `--no-optional-locks`。**唯一写入物为本 report.md。**
- **memory**：未读/写任何工具/项目/用户 memory（ZCode 官方 workspace memory 已 OFF，本次全新任务）；对方本轮目录（`…package088_designated_dual_review_001/minimax/`）从未打开。
- **无子代理**：本轮未派出任何子代理；全部工作由主会话完成。
- **运行证据边界**：所有"绿/0/PASS"均为对既有冻结证据（哈希先核后读）的独立复核，不构成新的运行证据；静态检查不替代运行证据。
- **观察与推断区分**：§3 可达性结论是对固定 fde 源码的静态控制流穷举，其"自然不可达"仅在当前不变量内成立；§6 各【推断】项未在本轮执行验证；"先 7 红后 60 绿"为声明的过程事实。
- **哈希差异披露**：§1.3 一处任务书声明哈希与实际单字符差异（17590B 时间线文件），如实登记，不改原件，不影响其余全部一致。
- **证据文件哈希核验不能证明其生成过程之外的事实**；机械包身份通过 ≠ 正式签名/法律/全平台通过；本地绿 ≠ 远端绿。

— 2026-10-24，ZCode（Start Plan / GLM-5.3 / 最高思考 slider2 / 完全访问 / workspace memory OFF），T01 fde989ac + package088 指定独立完整累计复审 pair001。
