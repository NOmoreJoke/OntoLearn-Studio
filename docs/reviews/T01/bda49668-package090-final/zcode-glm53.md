# T01 candidate bda49668 / package090 全新独立完整累计工程复审报告（ZCode / GLM-5.3 / pair001）

- 审查者：ZCode，Start Plan 发起；model `account:bigmodel-start-plan/GLM-5.3`；最高思考档（slider2）；完全访问（本会话全程无权限拒绝）；本任务为新建任务（`session_af837300f9c5a3411cfa984d7c5389f3`，与本方 `actual-task-receipt.json:5` 一致）、workspace memory OFF，未读/写任何 `.zcode`/`.minimax`/项目/用户 memory。
- 候选：HEAD `bda4966818f8af55b7726045aa65e52863317604` + 同一物理 package090（经 ROOT 接受的精准连续性，§4），parent `212625b2440c66c9d4034cd384013d6bf6034116`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，累计 **44 commits / 573 changed paths / 1314 tracked files**。本报告为对 base→bda 同一完整最终工程的全量只读累计独立复审，非仅 fixture 一行；不沿用 212 期任何一方的 PASS（ROOT 准入票明示 `newPairOldPassMustNotCarry=true`，本方判定全部由本轮亲读证据独立得出）。
- 只读边界：未运行任何 build/安装/测试/GUI/APP/engine/打包/网络（含 ls-remote；远端状态以派发时静态 snapshot 原件为准）；未修改任何产品源码、测试、配置、依赖、标准、Git 索引与既有证据；未打开活跃可变 DB；Git 读命令全部 `--no-optional-locks`；本轮唯一写入物为本 report.md。未读取对方本轮（`../minimax/`）任何目录/任务/报告内容（连列目录也未做）；上一轮 212 期两份完整报告与全部处置/审计按附件要求全文实读（§6），不误当本轮对手。

---

## 0. 结论（先行）

1. **当前内部演示范围（未签名目录包，授权文案"非正式分发，仅限内部演示"，实际宿主 macOS 27.0.1 / Darwin 27.0.0 arm64）：PASS。** 依据全部为本轮直接读证/亲读实码：身份与证据链全对（§1–§2）；212→bda 唯一改动经本方 Git diff + stdlib AST 双重复核确为单一显式 fixture 导入、其余 AST 全等（§3）；红→绿 collection probe 原件逐项核验为真实 pytest `--collect-only`、六原 nodeid、参数化 1+2+3=6 未动（§3）；精确 bda 单次完整 check 自然 0（139.336s，35 TS 文件 1694 PASS、Ruff 352、Python 3545 collected = 3495 PASS + 50 skip + 1 故意 duplicate-ZIP warning，`ssssss` 六 Windows skip 形态不变）（§3）；核心工程不变量在 bda 源码四层（preload/IPC/service/engine）与 Python 引擎关键链逐项亲读复核成立（§5）；同一物理 package090 产品连续性的五根支撑柱（唯一测试叶差分、66 生产构建输入逐字节不变、新 check 五 JS 中四件全同 + main 仅 24 字符既有 dev CSP nonce 字面量不同——本方亲自做了新旧 main.js 逐字节差分、APP090 910 成员/ASAR/engine 身份不变、旧 raw 未改标）由本方独立验证成立，且该精准桥接已获 ROOT 票接受（§4）。未发现数据损坏、越权写入、凭据泄露、注入或可利用鉴权缺陷；未发现本轮改动引入任何新产品缺陷。
2. **上一轮 Z 发现的 P2/Top2（Windows native 六例 `bundle` fixture 不可见）在本候选已按处置预订的最小方案真实修复：结构缺口消除、collection 层真实红→绿。但六例 native 测试体仍从未在真实 Windows 上执行，Windows 侧全部验证目标依旧 UNVERIFIED**（§3/§8）；本修复不回改上一轮两份原报告对 212 的事实发现。
3. **正式分发/其他平台：独立 HOLD 全部保留，一项未关闭。** bda 尚未 push（派发时 PR6 snapshot：open / merged=false / head_sha 仍 `8be6f08a…` / base develop 仍 `5f910b52…`）；CI29（run40071234771/head 8be）Quality FAILED / macOS FAILED / Windows CANCELLED 三终态未在远端闭环；签名/公证/wholeAPP legal/_distutils、Windows6 与目标 macOS 15、损坏 SQLite 物理（B/C 未授权）、D2/D8、真实 LLM/S3、用户恢复/FR-002/203/300、a11y/组织等既有门全部保留；后继仍须 fresh 双审（本报告为其中一半）→ROOT 完整接收→正常 push→真实新 CI 全绿→squash develop→远端复核。**0/17 不变，FR003 仍 partial，不预结 FR401/402。**
4. 历史身份与失败全部按原样保留（§7）：085 MM BLOCK/Z 内部 PASS、087 第一对 MM BLOCK/Z 内部 PASS、第二对双方内部 PASS/formal HOLD、088 双方内部 PASS/formal HOLD、089 首次制造真败（engine/package wrappers 自然 0、postflight 自然 1、恰缺两个 Electron license 输入 30/32）、CI29 三终态与 Windows 20 分钟门、086 首败 9PASS/1T02FAIL/2SKIP/6未跑、旧 087 guard 首败、旧 088 renderer FAIL/FAIL/PASS（第二次人工输入可信确认但按键/因果未知）与 native 首个 0 来源 UNKNOWN、旧 1790 为 package 回执字节非秒——均未被本轮任何绿证据洗白。

---

## 1. 受理与环境回读（全部本方实测）

| 项 | 指定 | 本方实测 | 判定 |
| --- | --- | --- | --- |
| prompt.txt | 48093 B / SHA256 `07a20af3…6b94` | `wc -c`=48093；`shasum -a 256` 全匹配；官方 Read 工具读至 EOF（313 行） | ✅ |
| 原 11255B 清单 | 逐字保留、恰一次、在 EOF | 第 144 行至 EOF 恰 11255 字节；`sed -n '143p'` 为引出行；特征串 `a schema someone designed` 与 `someone who was there` 全文各恰 1 次；末行即 `> remembering why it's built this way, a year from now (someone who was there)`，无尾随字节 | ✅ |
| 规范源码路径 S（Unicode） | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T01-project-transactions` | 会话 cwd `pwd` 逐字符相等（NFC 规范形态）；与附件、DELIVERY、probe 路径一致 | ✅ |
| Git authority G | `…/OntoLearn-Studio/.git/worktrees/T01-project-transactions` | 本方对该 index 物理读回并重哈希（下行）；`rev-parse` 一致 | ✅ |
| HEAD / parent / base | `bda49668…` / `212625b2…` / `5f910b52…` | `rev-parse HEAD` 与 `log -1 '%H %P'` 三者一致；分支 `feature/weekly-t01-project-transactions` | ✅ |
| 累计范围 | 44 commits / 573 paths / 1314 tracked | `rev-list --count base..HEAD`=44；`diff --name-only base..HEAD`=573；`ls-files`=1314 | ✅ |
| 工作区状态 | 仅受保护 AGENTS overlay，cached/untracked 空 | `status --porcelain` 仅 ` M AGENTS.md`；staged 0；untracked 0 | ✅ |
| AGENTS.md | overlay 15147 B / `de15f6ce…5c8c4`（非产品改动，不编辑/不 stage） | 字节与 SHA 一致；C 内 committed 版 1056 B / `1b3c0291…3a6fb`，两者不同不混称 | ✅ |
| Git 索引 | 179247 B / `3e9e222d…a42d` | G/…/worktrees/T01-project-transactions/index 实测一致；cached diff 空 | ✅ |
| C clean-checkout | HEAD 同 bda / clean / AGENTS committed | `rev-parse`=bda；porcelain 空；AGENTS 1056 B / `1b3c0291…` | ✅ |
| provider / model / 思考 / 权限 / memory | Start Plan / GLM-5.3 / 最高 slider2 / 完全访问 Value1 / Memory OFF | 会话环境 `account:bigmodel-start-plan/GLM-5.3`；本方 `actual-task-receipt.json:15` 同文；全程无权限拒绝；未触碰任何 memory | ✅ |
| 宿主 | macOS 27.0.1 / Darwin 27.0.0 arm64 | 与 ROOT 已接收的当前主机范围一致（目标 macOS 15 仍 UNVERIFIED，不从 macos-latest 推 15） | ✅ |

本方派发目录仅含 prompt.txt / launch.txt / actual-task-receipt.json；`report.md` 为本方新建，未覆盖任何文件。对方目录 `…/minimax/` 全程未打开。

## 2. 证据完整性（本方逐件重算）

**全部 pin 首件重哈希 0 不符**：

- 历史七件：212 期 MM 报告 100734B/`c7556ecb…`（776 行全文读毕）、Z 报告 48376B/`77709332…`（193 行全文读毕）、统一处置 `review-opinion-treatment.md` 119606B/`84cda011…`（486 行全文读毕）、MM 独审 31464B/`8b7cc8e4…`（187 行全文读毕）、Z 独审 29311B/`f2d9407c…`（151 行全文读毕）、ROOT-MM 事实校正 19131B/`59a001be…`（全文读毕）、PRIMARY-OPINION-DISPOSITION-CHECK 1345B/`f3d798ae…`（全文读毕）。终态回执四件（MM/Z COMPLETION 与 FORMAL-TERMINAL-SOURCE）按问题回查使用，未重复全读门。
- A 组 fixture-fix 全件：附件所列 19 件 + FULL-CHECK-START + ROOT 准入票 7268B/`02a87482…` 逐件 `wc -c`+`shasum` 相符；另对 DELIVERY 内部登记的全部 40 个 evidence/authorization/continuity 针程序化重哈希，**40/40 相符（0 bad）**；BUILD-INPUTS-212625b2.json 12261B/`1414f96a…` 相符并全文读毕（66 个生产构建输入 + 212 期 actualFiveJS）。
- B 组 090 运行链：ENTRY 8592B/`95eeb5f4…`、INDEPENDENT-ACTUAL-REVIEW.md 8751B/`f707390f…`、ROOT-INDEPENDENT-FAULT-NATIVE-REVIEW.json 20985B/`a4f57f5e…`、controller-t01-package090-full-runtime-actual-root-acceptance 12682B/`f74794ab…` 四件全文读毕；EVIDENCE-FILES.json 402309B/`9b7f5418…` 结构化核验（**1380 条目、字节数合计 187,733,739 B，与 ROOT 票机械重哈希值精确一致**，并抽查首条目）；package-readback.json 1526621B/`ac0c833f…` 结构化核验（schema/authorizationTicket/licenseTargets32/runtimeOriginals11/nativeMembers17/appDeepCodesign/errors=0 等键齐全）；controller-t11-package090-final-root-acceptance 111353B/`02680784…` 结构化核验（qualificationScope="Successful frozen090 for212625b2 only; old089 failed/not a runtime candidate…"、mergedUsableFRs="0/17"）。
- 大件按"全文/结构逐项"原则：≤25KB 全文读；三个大 JSON 做结构+关键值+计数核验；争议相关 actualraw（三 fault 的 Job 终态/SIGKILL/PID 序列/native 事件序）直接读自 ROOT-INDEPENDENT-FAULT-NATIVE-REVIEW 与 INDEPENDENT-ACTUAL-REVIEW 原件，未以摘要替代。
- 派发时远端 snapshot 两件（本方目录内）：PR6 open / merged=false / head_sha `8be6f08a…` / base_sha `5f910b52…`；DEVELOP fetch_commit 实返 `5f910b52…`（base 未漂移）。仅 snapshot，不称永久当前。

## 3. 212→bda 唯一改动与红→绿独立复核

**唯一改动（本方 Git diff + AST 双重复核）**：`git diff 212625b2..bda` 恰 1 文件 1 插入：`packages/engine/tests/test_windows_example_resource.py` 新增 `from test_mainline_example_provider import bundle as bundle`（插入于既有 `from test_mainline_example_provider import load` 之前）；文件 10529B/`5273b28b…`→10589B/`a11455af…`（S 与 C 工作树实测均为后者）。本方用 stdlib `ast.dump` 对固定 Git 对象独立比较：**从 bda 模块 AST 删除该唯一 ImportFrom 后与 212 AST 完全相等**；212 侧无任何 bundle 导入；三处 map 独立差分：212 source-map→bda source-after 恰一叶变化（该测试文件），clean-check before→after **零变化**（check 未改 clean checkout 任何 tracked 字节），bda source vs clean 仅 AGENTS.md 一叶差异。与 AST-DELTA.json 声明一致且为本方独立再现。

**当前模块全文亲读（10589B）**：六例 native 用例（:157 held-bundle 拒 rename/delete/preexisting writer、:209 junction×{intermediate,root}、:232 API 失败×{info,read,open}）的参数化、skipif(`os.name != "nt"`，全文仅 1 处 `skipif`)、真实 ctypes `WinDLL("kernel32")` / `CreateFileW`（DELETE 访问、share 7、断言 `ERROR_SHARING_VIOLATION`=32）/真实 `cmd /d /c mklink /J`/Unicode 根改名 `中文😀资源`/monkeypatch 真实 `_Api` 追踪 open-close——全部原样，无 skip 扩张、无 mock 冒充、无 os.name 伪置。fixture 提供者 `test_mainline_example_provider.py:15-33`（`@pytest.fixture def bundle(tmp_path)` 返回 `(root, manifest_sha256)`）与 `load` 助手全文读毕；`git ls-files '*conftest*'` 仍为空（本方复认），故同仓显式 `as` 别名导入（与 `test_mainline_draft_dispatch.py:17` 的 `owned as owned` 惯例一致）是正确最小修法，与统一处置 §3 预订边界一致：不挪/缩六例、不改 skip/参数/断言、不加 conftest。

**红→绿原件逐项核验**：probe（2305B 全文读毕）为真实 `pytest.main(["--collect-only","-q",…,"-k","test_native_","packages/engine/tests/test_windows_example_resource.py"], plugins=[Probe()])`，仅在 collection finish 读 `item._fixtureinfo.name2fixturedefs`，**不执行任何测试体**（`nativeBodiesExecuted:false` 两份一致）。red（212 侧 C，09:12:24，0.2664617089s，自然 exit 1=probe 断言未达）：六 nodeid 恰为原六例（含参数化后缀），`bundle`/`tmp_path` fixturedefs 均空；green（bda 侧 C，09:13:01，0.2579019579s，自然 exit 0）：六例 `bundle` 全部解析到 `test_mainline_example_provider.bundle`（C 内真实文件路径）、`tmp_path` 解析到 `_pytest.tmpdir`，`platformOrSkipChanged:false`。**判定：collection 层 fixture 依赖闭包真实修复（红→绿成立）；但六 native 测试体、NTFS/HANDLE 真调用仍零执行，Windows native 依旧 UNVERIFIED**——与 DELIVERY `nativeBodiesExecuted:false` 及 ROOT 票 `Windows6NativeVerified:false` 一致。

**完整 check（精确 bda 单次）**：FULL-CHECK.json + 12176B stdout 全文读毕：`uv run --frozen npm run check`，cwd=C，HEAD=bda，attempt 1，09:13:17.542954Z→09:15:36.879428Z，139.33603262493853s，自然 exit 0；eslint `--max-warnings 0`→prettier 全过→三路 typecheck→vitest 35 文件/1694 PASS（8.57s）→electron-vite build（main 594.34kB）→verify-frozen-review-sources 4 件→Ruff `All checks passed!`/352 formatted→pytest（Python 3.12.12/pytest 9.1.1，rootdir=C，configfile pyproject.toml，testpaths=packages/engine/tests）**collected 3545 = 3495 passed + 50 skipped + 1 warning**（唯一 warning 为 `test_prepare_fr003_bundle.py` 故意 duplicate ZIP member），`test_windows_example_resource.py` 行内 `....ssssss.....` 六 skip 形态不变（50=原 44+Windows 6，与 212 期同构）；`alteredTestBudgets:false`；source/clean tracked 字节前后不变（map 差分零变化，本方独立复核）。**BEFORE-READER-CORRECTION**：首个 preflight 元数据 reader 把 `ls-files -z` 终末 NUL 切出空项致 `len(paths)==1314` 断言失败，发生于任何源码/测试/索引改动之前，属证据工具更正保留项，非 pytest 首败、无重试（`testsOrAppExecuted:false`）。

## 4. 同一物理 package090 产品连续性独立评估（判定：充分，附明确边界）

本方对"212/090 的既有产品运行证据可否精准承接 bda"独立核验五根支撑柱，全部成立：

1. **源差分柱**：base→bda 相对 212 仅一测试叶（§3 AST+diff+map 三重），生产/依赖/配置与 66 个构建输入（BUILD-INPUTS 全 66 项含 electron-builder.yml、两锁文件、engine/contracts 全源）逐字节不变——66 输入集合不含任何 tests 路径，本方核对集合成员确认。
2. **构建输出柱**：新 check 五 JS 与 212 期 actualFiveJS 逐针对照：preload/index.js、renderer CSS/JS/index.html **四件 SHA 逐字相同**；main/index.js 两边均 594342B，**本方亲自逐字节 diff：唯一差异为 offset 590253–590276 的 24 字符连续区**，即既有 devURL CSP nonce 字面量 `2hH2ltkJ…`→`mSj5sG2O…`（`csp.ts:16` 的 `[\w+/=-]+` 24 字符 nonce），归一化后逐字全等——与 PRODUCT-CONTINUITY `normalizedBytesExactlyEqual:true` 一致并为本方独立再现。此差分同时再次实证 MM-O36（构建 nonce 致 main 字节不可复现）仍在。
3. **实物身份柱**：APP090 910 成员 wholePath/kind/mode/hash/linkTarget 与原 package-readback 及修前快照全同（app090-before/after 同 SHA `0fbd6760…`，本方重哈希）；ASAR 19014603B/`fbf5741e…`、engine 6232272B/`c6d12ac5…` 不变；旧 engine producer 与 runtime source HEAD 仍为 212，N（node-checkout）保旧 1314 源与原五 JS、Git UNBORN 非源码 authority——不称 N 为新 bda、不称 bda 跑过 GUI。
4. **不改写柱**：`oldRuntimeRawNotRetagged:true`、新 main 未 restore 旧 nonce、未采入旧 N/APP、`newEngineOrPackageOrMacRuntimeExecuted:false`——旧 PASS raw 保持 212 身分，无涂改。
5. **授权柱**：ROOT 票（7268B 全文读毕）`acceptedFixtureOnlyChange/acceptedFullCheck/acceptedSamePhysicalPackage090ProductContinuity/sameProductRuntimeEvidenceAcceptedForCurrentCandidate` 均 true，40 针重哈希 0 差异，S/C/N 三态与 AGENTS 例外明示。

**边界（明示，不以连续性外推）**：bda 自身零新 engine/打包/运行；若未来任何生产源/构建输入改变即此桥作废、须按真实影响重定资格；真实新 CI 仍是必要发布门（本地绿≠远端绿）；"四件全同+main 仅 nonce 差"证明构建输入等价下的可复现性，不等于新五 hash 全同旧包（main 确实不同，本方如实分列）；full18/三 fault/native 的既有运行事实按其原件边界承接（16 PASS+2 Linux 条件 skip 非 18 PASS；coordinator 目标 Job 终态 failed/ENGINE_EXITED、原 engine 91072 真实 SIGKILL、新 91074 自然 0；三 fault 均测试收尾 quit 非真实 Cmd-Q；native 真实 0/0/1+真实 super+q、before-quit4→closed5→will-quit6→engine7/8、CUA 11 对 call/output 非 11 次点击；三 fault raw 实际含 appPath/resourcesPath、full18 helper 未供 getter 与 execPath 仍 UNKNOWN；9 已知 PID 有限采样不作全局 drain）。本方不接受"任何一行变更即全盘重跑历史"（MM-O47 全盘禁止承接已被处置驳回），也不接受跳过新身份双审/CI。

## 5. 现码第一手复核（bda 四层 + Python 引擎关键链；行号为当前工作树实测）

桌面四层（preload/IPC/service/engine.ts 自 fde 后零改动，本方本轮全部亲读关键完整链，非沿用旧结论）：

- **preload/index.ts（86 行全文）**：`receiveMainline` 恰一次 `project:reply-received` ACK 与 5s 超时竞速（:26-45），任何失败 `catch {}` 静默仍返回业务 payload（:40-46 注释自述"Main keeps the original unacknowledged lease; no retry/clear is fabricated"）——单 ACK、无产品自动重试在真实调用方确认。bridge 仅按业务命名方法暴露。
- **desktop-ipc.ts（212 行全文）**：`deliveries.size>=16` 在 `replies.receive` 之前（:164）；唯一 `deliveries.delete(id)` 在 consume 成功之后（:142）；consume 抛错 `return permission()` 跳过删除（:136-141）；ACK 通道 sender/senderFrame/engineSessionId 三重精确匹配（:129-135）；`accepted` FIFO 仅含已消费身份、上限 16（:144）；设计注释"No timeout, navigation or new session deletes an unacknowledged receipt"（:103-104）原文在案；receive 直接 reject 时在 deliveryId 生成前返回（:172-174）。
- **project-mainline-service.ts（600-819 全区）**：`#keepIntent`（:621-636）紧凑身份 retainHolding、注释明示 never FIFO-forgotten、由全局硬预算约束寿命；`#offerIntent`（:637-660）退役回调 size>1 只删自身令牌、释放失败恢复 `intent.accepted` 再上抛、**全文件唯一 `#fullIntents.delete` 在退役回调内**（:656）；`#readAcceptedIntent`（:661-699）仅 `job.get` 且 jobId/projectId/operationId/capability/confirmationRef/稳定 input 六项全等校验；`commitProjectChangeSet`（:700-800）`#fullIntents.size>=16` 拒（:735）、`intent.unknown→denied()`（:751"No automatic replay of an entered write"）、`active++→offer/read/job.create→finally active--` 同步围栏、job.create 失败按 `queryWriteEntered(pin)` 区分已入线 unknown（:775）、受理成功置 unknown=false（:787）。
- **engine.ts（关键区亲读：180-274/700-774/774-1023）**：`mainlineHoldingMeasure`（:191-267）返回 `bytes=32b+4096, objects=b+128, work=8b`（:266），b 含真实 JSON 遍历计费（键名/引号/转义），263168 节点/栈上限（:224/248/261）——MM-T2 的 1183 固定阈值被驳回的算术基础本方独立复认（首次 delivery 预付 scratch 8388608B/**263168 objects** 于 :791，`maximum<1`（:858）并非唯一容量出口，measure 超额/:mainlineReserve（:726-752，134217728B/1048576 对象/536870912 work/delivery UNKNOWN 拒新支出/OFFERED 拒）亦可先拒）；`#newDelivery`（:770-771）16 槽与 `#mainlineComputing` 单飞；`#unknownDelivery`（:820-823）置 UNKNOWN 并把 records 全部 `uncertain=true`——**全文件 uncertain 写入仅 `= true`（:822/:2098/:2501/:2566，本方穷举），无任何复位（M1 未修）**；`#mainlineRecords` 仅 `set`（:1310）无 delete、上限 16（:1167）、先前有效 client 复用（:1164）——初始 1+15 继任口径成立；`#retainHolding/#releaseHolding`（:835-883）：WeakMap 仅 get/set、release 唯一拒绝是 holding 不存在或 record 不匹配（**无 session 检查**，:874）、bytes===0 幂等、替换语义先退旧值再入新；receive（:903-945）单飞、aliases 校验、失败置 UNKNOWN；consume（:946-981）前置 OFFERED+callbackDone+computations=0+全部 wire terminal+无 uncertain record+session current，逐项 retire 成功才逐项删除、退款与全部 delete 在最后（释放失败保原 receipt 可精确重试）、`#mainlineConsumed` 防重复退款。
- **csp.ts（26 行全文）**：唯一 CSP 源；生产 `script-src 'self'` 无 unsafe-inline/eval、`connect-src/object-src/base-uri/frame-src/form-action` 均 `'none'`；dev 变体注入 24 字符 nonce+unsafe-inline style+本机 origin/ws——与 §4 的 main.js nonce 差分互证。

Python 引擎侧关键链（亲读）：

- **mainline.py**：`_example_resource_reader`（:52-90）nt 分派 `_windows_resource.windows_resource`；POSIX 路径 O_DIRECTORY|O_NOFOLLOW 根、成员 O_NOFOLLOW|O_NONBLOCK|dir_fd、S_ISREG、maximum+1 短读、前后 (dev,ino,size,mtime_ns) 全等、finally close——逐语义等价确认。`BuiltinExampleProvider`（:93-157）：Path+64 位小写 hex pin、绝对路径、example_id/input_digest 双白名单、manifest SHA pin + canonical 全等后才开 input、input 长度+SHA、一切出界仅 `ExampleResourceFault("EXAMPLE_RESOURCE_UNAVAILABLE")`（OSError/ValueError/UnicodeError/RecursionError 收口 `from None`，路径/OS 错误不进 RPC）。READ_LIMITS/HELD 128MiB/1048576/MAX_REPLIES=16（:41-45）。`project.example.create`（:466-529）：origin 恰三字段、`operation_claims` **replay-first**（既有 claim 只从已认证不可变回执闭包重放，request/origin 任一不等即 IDENTITY_CONFLICT、回执不等即 INVALID_STATE），仅新 claim 才读 provider，再经 `store.commit` 单一版本化路径。
- **project_lifecycle.py:82-102**：`origin_value` 强制恰 {hostClientId, engineSessionId, permission}、两 UUID v4 36 字符、permission=="library.create"——M2 跨 session 原回执不可对账的结构根源确认未修。
- **format3.py:158-187**：`migration_backup` xb 独占创建→SQLite backup+integrity_check+logical_hash→close→**nt 以 `r+b` fsync 自有 fresh 备份/POSIX `rb`**→仅 POSIX 目录 fsync（`if os.name != "nt"` 旧条件，本方核对 501→212 diff 仅一行 r+b，**目录项不对称为既有平台差异，非本候选引入**）→proof=read_bytes→after_backup，次序与吞错边界原样。
- **_windows_resource.py（333 行全文）**：盘符白名单/拒 UNC、`\\?\`、相对、`..`、ADS、非法字符/控制符、尾点空格、保留设备名（含 COM/LPT ¹²³ 变体）、>510 UTF-16 组件；`GetDriveTypeW==DRIVE_FIXED`+`QueryDosDeviceW` 须 `\Device\HarddiskVolumeN`+卷 GUID 根句柄经 `GetFinalPathNameByHandleW` 回比+`GetVolumeInformationByHandleW=="NTFS"`；逐组件以已持父 HANDLE `NtCreateFile`（SYNCHRONIZE|FILE_READ_ATTRIBUTES|dir?FILE_EXECUTE:FILE_READ_DATA，share=0x1 拒 WRITE/DELETE，FILE_OPEN_REPARSE_POINT|FILE_SYNCHRONOUS_IO_NONALERT|成员 FILE_NON_DIRECTORY_FILE，IOSB 须 FILE_OPENED）、同句柄 Tag/Standard/Id/Basic 四信息类核无 reparse/类型一致/DeletePending/卷一致；两固定成员名+限额、max+1 短读、前后全元组全等、链复检；意外完成也先关自有句柄；`__exit__` 逆序关闭、close 失败且无先在异常才另报（保首因语义）；外层收口仅 ResourceUnavailable。结构定宽 ABI（_Standard 24B/Directory offset 21、_Id 24B、_Basic 40B）与测试断言互证。**真实 Windows 执行为零**；残余边界如实保留：两次采样不证持有期间始终无 reparse、share 不阻断全部 FSCTL 元数据操作、maximum+1 为字节界非墙钟界——最终防线是 manifest/input SHA pin（内容逃逸无法过 hash 校验）。
- **job_store.py:2303-2336**：`result_page` 全量 load 后 `available=[r for r in payload if position is None or [ordinal,rowId]>position]`——每页 O(总量) 物化确认仍在（D2 留账）；CURSOR_MISMATCH 绑定三键、页字节上限 131072。
- **compensation.py:168-192**：undo 对账对 marker 之后每个 commit 重建 `_with_retirements` 快照比对（later 编辑/ABA 检测），重复历史重建成本确认仍在；ABA/后续冲突报 state 类 Conflict（保护性保留，不改无条件 no-op）。
- **定点穷举**：coordinator `seen` 65536 硬界（:282-284）；memory_guard `MEMORY_GUARD_EXIT=75`、Darwin `native_hard_limit=False`（咨询式）；registry 3 处 `requiresConfirmation:true`、25 处 `agentEligible:false`；semantic 三文件悬挂 import **36 条**（20+11+5）指向不存在的 quality/semantic_profile 目标（本方 grep 计数复认 38 为误、目标 8 个）；engine.ts 2623 行/job_store.py 2589 行超 2000（semantic.py 1627、workspace-controller.ts 1531 未超）；electron-builder.yml `identity:null`、三平台 `target:dir`、两条 license `from: ../../node_modules/electron/dist/…`（:15-17，MM-O52 不同源脆弱点原样）。

## 6. 上一轮全部意见独立处置（全文读后自判，不盲采）

两份 212 报告、119606B 统一处置、两份独审、ROOT-MM 事实校正均已全文读毕；以下为本方对 bda 现码/现证的独立处置。源级事实因 bda 仅改一测试叶而机械承袭，但关键项均经 §5 亲读复认。

### 6.1 MM Top10（原分级保留，本方处置）

| ID | 本方独立处置（bda 实测依据） |
| --- | --- |
| MM-T1 uncertain 单向闩锁 | **confirmed+qualified（M1 未修）**。本方穷举 :822/:2098/:2501/:2566 仅置 true；只闩同 owner 主链接权（`#mainlineReady`:714），不等于 health/TaskService/全 App 停止；新 session 不退旧 UNKNOWN。 |
| MM-T2 约 1183 次全局冻结 | **有限容量 confirmed；固定阈值/全 App 永久 refuted（维持 ROOT 校正）**。公式（:266）与 scratch 263168 预付（:791）本方亲读复认；b=758 为无完整见证的假设、1183 为忽略 scratch 的理论商（仅扣 scratch 亦只 886）、`maximum<1` 非唯一出口；同一 Supervisor 实例寿命内有限安全拒绝成立，跨进程/全功能外推不成立。专属可行动错误码+ADR 为未来候选建议。 |
| MM-T3 未 ACK 双 16 槽+fullIntents 占位 | **confirmed+qualified（M3 未修）**。四个独立 16（IPC deliveries:164、engine #mainlineDeliveries:771、#mainlineRecords:1167、#fullIntents:735）不相加为 8；未入线且 unknown=false 的同指纹/owner/session 原 intent 可按原参数重试完成（:775 区分）；已入线 UNKNOWN 不清。 |
| MM-T4 跨 session 原回执不可对账 | **confirmed+qualified（M2 未修）**。origin 三字段强约束（project_lifecycle:82-102）+示例 claims replay 全等校验（mainline:487-501）亲读复认；守卫防重复创建有效；不删 origin、不新建持久账本、"只读按 operationId 查回执"仍是新增授权面须单独范围。 |
| MM-T5 Windows6/mac15 零运行 | **confirmed，平台 HOLD；本候选已修 collection 层前置（§3），native 体仍零执行**。 |
| MM-T6 Windows 目录项未持久化 | **缺口 qualified、'本次引入' refuted（维持）**。501→212 仅 rb→r+b 一行；nt 跳父目录 fsync 旧已存在（format3:179 本方亲读）；实际掉电/目录 durability 未验，不未证先采 BACKUP_SEMANTICS 方案也不降原不变量。 |
| MM-T7 无用户备份/恢复；损坏库拒启 | **confirmed，FR/恢复 HOLD**。FR-002/203/300 分开留账；页 CSV/内置示例不替代。 |
| MM-T8 prepare 残留锁 | **confirmed 工程可用性风险**。O_EXCL/lstat 语义不变；不按年龄删锁。 |
| MM-T9 38 处悬挂 import | **缺失 confirmed；38/全吞 refuted（维持）**。本方 grep 复认 36 条/8 目标、部分在 try 外；profile 分支当前不可达，不盲删不假启。 |
| MM-T10 每页全量物化 | **confirmed+qualified，D2 HOLD**。:2313-2315 亲读复认；generic result.page 与 typed rows 分路；10000rows/8MiB 生产上限在；不拿 500 万当已证反例，也不删安全核验求快。 |

### 6.2 MM §5 其余 52 项（O01–O52）

全部经统一处置/独审逐项承接，本方抽查关键项并复认：O01（非 engine 独立签名失败 **9** 非 17；identity:null/target:dir 亲读）、O02（whole legal/_distutils HOLD）、O07（UI 撤销当前回执≠通用 redo；FR804 不要求）、O12（records 初始 1+15 继任）、O16（retire/consume 失败保原 receipt/首因；preload 静默单 ACK 亲读 :40-46）、O17（ACK 失败仍返 payload、成功 accept 清 pending；按钮链前提保留，不说 16 次必成）、O31（createIntent 内存 ref 同 session 复用原 ID，App `??=`）、O35（workspace `"*"` 由 lock 锁定，非已证漂移）、O36（nonce 不可复现——本方 §4 亲测再现）、O38（行数纠偏）、O47（**全盘禁止承接 refuted**；按影响/原身份严格桥接，本候选正是被接受的具体例）、O48（212/bda 未推，不擅推）、O49（CI29 余 F/20min 总因 UNKNOWN 边界）、O50（8 短 ID/9 超限 nodeid）、O52（**license 闭集 exit-0 且仓内无断言 confirmed，采纳为未来工程改进未实施**；electron-builder:15-17 亲读；机械 32 非 whole legal）。其余按统一处置口径承接，无本方异议。

### 6.3 Z Top10 与 Z §10/§11

Z-T1（远端/CI 流程门）**confirmed**（派发 snapshot 头仍 8be/base 5f，CI29 三终态固定记录）；Z-T2（fixture P2/High）**本轮已修且不回改原发现**；Z-T3（Windows UNVERIFIED）confirmed；Z-T4/Z-T5（M1+records/M3）confirmed+qualified 如上；Z-T6（retire/consume 无恢复入口）confirmed 潜伏限制（自然触发未证，preload 静默单 ACK 亲读）；Z-T7（M2）confirmed；Z-T8（备份/FR）confirmed+qualified；Z-T9（签名/legal；17 与 9 字段口径分层）confirmed；Z-T10（mac15/D2/卫生）confirmed+qualified。Z §10 的 H1–H15 与 §11 九类实现/未完簇经两独审完整承接（含 Z 累计口径、"所有限制仅容量可恢复"两处过宽总结的驳回、page400 不得记 PASS、W16 未新增 ZIP、云不适用≠本地义务豁免、CSV2009 不能整体不适用、hash 不替路径资格、close 保首因限定等），本方复核无异议并逐项保留；Z §11.3 未完簇与 §11.4 组织 UNKNOWN 全部承接。Z 报告自身过程披露（首稿头读补齐、provider busy 无 fallback、26 项转录笔误、额外写 .zcode memory note 的执行偏离）保留不改。

### 6.4 160 项共同清单

MM 原 29✅/49⚠️/28❌/42➖/12❓=160 计数与逐项符号、统一处置 D1–D5 基础处置与 C01–C22 纠偏键本方全文读毕并复核无缺项；Z 分类承接同步有效。本方在 §10 给出独立适用性结论（与该表一致处不重复造表，差异处明示）。

## 7. 历史失败与 HOLD 全量保留（不清洗、不回写）

085（MM BLOCK/Z 内部 PASS）、087 pair001（MM BLOCK/Z 内部 PASS）、pair002（双方内部 PASS/formal HOLD）、088（双方内部 PASS/formal HOLD；renderer FAIL/FAIL/PASS 与 native 首个 0 来源 UNKNOWN 保留，090 首轮 PASS 不回写）、089 首次制造真败（engine-wrapper 9.54s/package-wrapper 2.60s 自然 0、postflight 1.13s 自然 1、恰缺 LICENSE 1096B 与 LICENSES.chromium.html 20115518B、30/32、真实输入遗漏非比对器误判；090 仅 +1 目录+2 文件+20116614B 精确补齐、复用 089 资格化同版本 engine、无二次构建/JS 重建/下载/新树；089 保持 FAIL）、086（9PASS/1T02FAIL/2SKIP/6 未跑）、旧 087 guard 首败（0 产品用例）、first full001/fresh001、CI29（run40071234771/head 8be：Quality 1693PASS/1FAIL、mac15 FAIL/3SKIP、Windows cancelled/20m annotation；348 DOM 行 100%@06:56:47、最早 draft 四组超长 PYTEST_CURRENT_TEST>32767 原栈；raw 404/runZIP 无 Windows，其余 F/20min 总因不全知，不泛归 nodeid/locale/fsync/resource）、更早 CI 三失败（cp1252/ignored bundle/shallow Git）、旧 1790=字节非秒、300s 原预算与 JSON 直接 timeout 字段/推断分开、501 合法 UUIDv4 ping+realpath 修窄点、C4–C6 三次配对失败、D8 人工裁决、47 阶段双审积压、W16 未新增 ZIP。以上全部原样保留；本轮 fixture 修复与 check 绿不洗任何一项；历史八份原件按争议回溯（本轮无争议需回原件重读的运行事实；本方未实际全文重读八件，不宣称读过）。

## 8. 本轮最值得修复的 10 项（按严重度；区分【观察】/【推断】；不为凑数虚列）

1. **【High｜发布流程｜观察】远端链完全未走**：bda 未 push；派发 snapshot PR6 open/head_sha 仍 `8be6f08a…`（指向 fde 期内容，不覆盖 44/573）/base develop `5f910b52…`；CI29 三终态未闭环。本地 check 自然 0 与 090 当前主机承接不能对冲远端。0/17 解除须 push→真实新 CI 全绿→squash→远端复核；任一失败即新候选。若 base 漂移须 ROOT 处理，不擅自 rebase/强推。
2. **【High｜平台｜观察】Windows 真实平台仍 UNVERIFIED**：fixture 注册仅修复 collection 层；六 native 体（真实 HANDLE/share/junction/Unicode/句柄关闭）与 format3 nt 分支、storage_probe Windows 能力在真实 NTFS 上零执行；mac 六 skip+fake API 是策略覆盖非实测。修后须真实 Windows runner 全套+保留首败原栈。
3. **【Medium-High｜可用性｜观察+推断】M1 uncertain 单向闩锁 + records 会话更替累积（1+15=16）未修**：同 owner 主链一次超时/UNKNOWN/引擎死亡在途即会话内持续 PERMISSION_DENIED，无进程内自愈（health/tasks/job/result/operation 不受该 owner 门约束）。自救指引缺失；未来复位须按原操作对账证据设计，不得简单清除。
4. **【Medium-High｜可用性/容量｜观察+推断】M3 四独立 16 容器 + 紧凑身份寿命预算**：未 ACK stale 投递、已入线 unknown intent、失败提交占位均可耗尽且错误与"参数非法"同形（INVALID_STATE），用户/支持无法区分。义务语义（不 FIFO、不代 ACK、不退款）是已采纳合同不得动；改进方向是专属错误码+UI 自救文案+ADR 记录寿命权衡。
5. **【Medium｜对账｜观察+推断】M2 跨 session 创建/示例原回执不可对账**：引擎在"已持久化后、回执抵达前"死亡→同 operationId 重试必 IDENTITY_CONFLICT，UI 停留"创建结果尚未确认"。无数据损失（守卫有效），但用户无法自证；长期需原 dispatch 物理绑定的 resolution 设计。
6. **【Medium｜健壮性｜观察】retire/consume 故障注入下无产品恢复入口；preload 单次 ACK 失败静默**：每次潜在泄漏 1 引擎槽+1 IPC 槽且吞一次私有确认（业务 payload 仍达）。自然触发在现不变量下未证成；同 deliveryId 有界私有 ACK 重试可作未来设计（保全部原责任/首因）。
7. **【Medium｜数据韧性/功能缺口｜观察】无用户级备份/恢复入口与恢复实测；损坏 SQLite 物理 HOLD；FR-002/203/300 P0 缺口**：迁移备份≠用户恢复；当前页 CSV/示例链不替代三条 FR。
8. **【Medium｜发布义务｜观察】签名/公证/身份缺失 + wholeAPP legal/_distutils 闭包 + 仓内打包 license 闭集断言缺位（MM-O52）**：`identity:null`+三平台 `target:dir` 未变；builder 两条 license `from` 绑死自身 node_modules 与 `--config.electronDist` 可不同源（089 真败实证该窗口），`package:dir` 在闭集不满足时仍 exit 0 且仓内无断言。未来候选应把实际 electronDist 同源校验与产物闭包断言纳入仓内 package 链（须新身份+验证，机械 32≠whole legal）。
9. **【Medium｜平台/规模/卫生｜观察】目标 macOS 15 UNVERIFIED；D2 规模未量化（result_page 每页 O(总量) 物化 :2313、undo later 全历史重建 compensation:171-186、本体表整传+渲染切片）；a11y/i18n 单语未核；engine.ts 2623/job_store 2589 超 2000 行；36 条悬挂 import/8 目标；dev nonce 致 main 构建字节不可复现（本方 §4 实测再现）**。
10. **【Medium｜工程可用性/正确性｜观察】prepare-fr003-bundle O_EXCL 残留锁阻断后续构建链；退出码 75（MEMORY_GUARD_EXIT）与真实 ENGINE_EXITED 不作区分；busy-finally 无条件清 busy（重叠写未证、维护风险）；渲染层无 AbortController；queryControllers Map 不清理（不得 LRU 删）**。均为既有登记，bda 未改。

## 9. 其余阻断/缺口（原样保留，不清零）

静态加密与设备失窃预案、渗透测试与安全问卷证据包、"谁查看过"审计、全屏空/加载/错误与表单保留/后退语义逐项、依赖 advisory（无网络未核）、Python 依赖自动扫描（Dependabot 不覆盖）、DLQ 视图、远端分支保护未核、changelog/Terms/Privacy、组织归属与 bus factor（组织事实，不从源码认证）、internal exception 消息含原值的潜在面、`project/workspace.py` 测试易失模型、内部 create_project 协议不可达、e2e 首丢注入点仅 IPC 业务回复层、mkdtemp profile 不清理、旧 reader 测试依赖 Git 历史可达、无 O_NOFOLLOW 平台 TOCTOU、真实 LLM（S3 前不接入；接入后 prompt 注入/花费上限/evals/密钥整类适用）。以上与 §8 不重复展开项一并保留。

## 10. 原用户 11255B 清单逐项适用性（本方独立结论）

产品形态（本方直核）：本地优先、单用户、离线、无服务端、无网络端口（CSP `connect-src 'none'`+引擎无网络出口+`semantic_offline` 审计钩）、无账号体系、无计费、S3 前无模型接入。先判适用性，不适用按类别说明且**不等于已具备**；适用未核写"无法确认"；不为清单扩建无关功能。MM 160 项逐项表（29✅/49⚠️/28❌/42➖/12❓）与 C01–C22 纠偏本方复核有效，此处给类别结论并注明本方亲证增量：

- **整类不适用（本地单用户桌面形态；新增对应面即整类重审）**：账号/身份（login+/邮箱、重置、MFA、会话超时/全踢、SSO/SAML/SCIM、登录限流/防误锁、租户隔离、admin 代登录）——无服务器/多用户，IPC 三重身份校验为本地等价物；支付/计费全套（money 整数、税、订阅、催缴、PO、VAT、退款、计量、年约、收入报表）；对外 API（API key、OAuth 刷新、webhook 签名/重试、集成沙箱）；邮件（SPF/DKIM/DMARC、退信）；云基础设施（IaC、零停机、CDN、DNS/SSL、二区域、状态页、成本告警、自动扩缩、外部拨测）；合规套件中 HIPAA/BAA/PCI（无 PHI/卡号）。**注意统一处置纠偏：云不适用不免本地恢复/隐私/规模义务；无支付勿强加其专门义务。**
- **适用且本方本轮亲证/复核成立**：designed schema（单一契约 schema+registry+errors、双端 zod `.strict()`/contract_v2）；改号越权（projectId/owner/session 绑定+IPC 三重匹配）；服务端校验（主进程+引擎双侧）；SQL 注入（关键路径参数化亲读）；XSS/CSP（csp.ts 唯一源、生产无 unsafe-inline/eval、React 转义）；秘密（无密钥存在、引擎不持凭据）；包确认（精确 pin+两锁+`uv sync --frozen`）；最小权限（registry 3 处 requiresConfirmation/25 处 agentEligible=false 亲数）；幂等/去重（operation_claims/commits/rounds 三键、job.get-only 恢复）；软删除（retirement+不可变历史触发器）；时区（epoch/单调钟）；Unicode（字面量层全链+代理对拒绝；RTL 无法确认）；缓存失效（invalidation-v2 唯一规则源）；后台 Job+有界退避（真实持久 Job/claims 恢复）；undo（补偿性新事务+ABA 保护，e2e Undo/Undo-of-Undo）；AI 人工批准（结构性成立：确认仅在完整 Diff 全行展示后、agentEligible=false）；分支策略/ADR/评审（worktree+feature+指定双审+CI 门禁实际运作）；披露（SECURITY.md 私有渠道）。
- **适用但部分满足/留账（与 MM ⚠️/❌ 及 C 键一致，本方无新证据推翻）**：分页 page400（机制已核、243 行跨页实测，**page400 未验**——C07）；导出（仅当前页 CSV；全量/JSON/XLSX/项目级缺）；导入（FR-300 未实现，不以内置示例替代——统一处置纠偏采纳）；迁移（前向完整、回滚=文件级备份、恢复实测未做——C04）；备份/夜间/PITR（无用户级）；日志（零日志取舍+不可变 who-changed 账本，who-viewed 缺——C09）；静态加密（明文 SQLite 为本地优先明示取舍、失窃预案缺）；依赖扫描（npm/actions 覆盖、Python 不覆盖、advisory 无法确认）；错误可行动（固定码+中文模板，容量拒绝与参数非法同形为瑕疵）；空/加载/错误态（主链两模块已核、全屏未逐页）；表单保留/后退/键盘读屏/a11y/i18n（未核/未做）；死代码/长文件（36 悬挂 import、两文件超 2000）；README 一小时/继承者文档（无法确认）；changelog/Terms/Privacy（无）；公司名下账户/域名/repo（appId 个人命名空间，产权为组织事实）；正式发布流水线（未走）。
- **13 条人员条目**：无法从仓库证据确认（组织事实）；可核实对标为指定双审+独立复核+CI+总控记录的本轮实际运作；bus factor=1 与公司产权属组织事实，本报告不从源码认证。

## 11. 最终判定

### 11.1 当前宿主内部演示范围（bda49668 + 同一物理 package090，macOS 27.0.1 / Darwin 27.0.0 arm64）

**PASS。** 独立依据（均为本轮亲证）：

1. 身份与证据链全对（§1/§2）：prompt/清单/HEAD/base/44/573/1314/AGENTS/index/C 全部相符；A 组 40 针与 B 组全部 pin 重哈希 0 差异；大 JSON 结构化核验与 ROOT 票机械值精确一致。
2. 唯一改动真实且最小（§3）：Git diff+独立 AST 双确认仅一显式 fixture 导入；六 native 用例/参数/skip/断言原样；无 conftest 复制/fixture 重定义/mock/skip 扩张。
3. 红→绿真实（§3）：真实 pytest collection，red fixturedefs 空/自然 1，green 六例解析原提供者 bundle+真实 tmp_path/自然 0；Windows native 体仍零执行如实分列。
4. 精确 bda 单次完整 check 自然 0（139.336s 全量、计数逐项核对、预算未改、source/clean 前后字节不变）。
5. 核心不变量在 bda 四层+引擎关键链亲读逐项成立（§5）：版本化单一提交路径、不可变历史、幂等不重放、渲染端隔离、CSP 唯一源、固定错误码边界、无模型/遥测/云、128MiB/1048576 硬预算与 16 义务语义、UNKNOWN 不退款不驱逐、示例资源双平台 fail-closed 读取+SHA pin 兜底。未发现数据损坏、越权写入、凭据泄露、注入或可利用鉴权缺陷。
6. 同一物理 090 产品连续性五柱独立成立且经 ROOT 接受（§4）；上一轮唯一确定性测试缺陷已闭合并经真实红绿证明。

**不稳定边界（明示）**：本 PASS 仅在"非正式分发，仅限内部演示"范围、当前宿主 macOS 27.0.1、且产品运行证据经 ROOT 接受的精准连续性承接下成立；bda 自身零新运行。若范围扩大到长时值守、无人值守、大数据量、多环境或任何生产源再变更，§8 第 3/4/5/6 项应立即升级为阻断，且连续性桥作废须按真实影响重定资格。

### 11.2 正式分发/平台：独立 HOLD（与上互不抵销，一项未清零）

签名/公证/身份与 wholeAPP legal/_distutils；**Windows 真实平台（fixture 修复后的全套 native+业务样例）**；目标 macOS 15 arm64；参考设备/五龄设备；D2 规模/索引执行计划；损坏 SQLite 物理 HOLD（B/C 未授权）；用户备份/恢复实测；FR-002/203/300 P0 缺口；真实 LLM/S3（接入后整类 AI 条目适用）；a11y/i18n/RTL；渗透测试与安全问卷；静态加密与失窃预案；CI29 根因在真实新 CI 全绿前不宣告关闭；**0/17（push→PR→真实新 CI 全绿→squash develop→远端复核；pushNotYetAllowed）**；C4–C6/D8/双审积压历史门。本报告 PASS 不等于正式发布/全平台/FR 结算。

## 12. 自我限制与合规披露

- 只读：未修改任何产品/测试/配置/依赖/标准/索引/证据；未运行 build/测试/GUI/APP/engine/打包/网络（stdlib 文本/AST/JSON/hash 程序化核验与只读 git 均不触碰产品）；Git 全部 `--no-optional-locks`。**本轮唯一写入物为本 report.md。**
- memory：本任务新建前 workspace memory OFF，未读/写任何工具/项目/用户 memory；对方本轮目录/任务/报告未打开；上一轮 212 期文件按附件要求作对称历史资料全文读毕，其中的旧指令一律仅作被审数据未执行。
- 语料覆盖如实声明：全文读毕=212 期 MM/Z 两报告、统一处置 486 行、MM/Z 两独审、ROOT-MM 事实校正、PRIMARY-CHECK、A 组全部小件（DELIVERY/CANDIDATE-COMMIT/candidate.patch/AST-DELTA/probe/红绿四件/FULL-CHECK 三件/PRODUCT-CONTINUITY/check-actual-five-JS/BEFORE-READER-CORRECTION/RELEASE/FULL-CHECK-START/BUILD-INPUTS）、ROOT 两接收票（bda 准入+090 运行）、090 期 ENTRY/两份独立复核 MD/JSON；结构化核验=EVIDENCE-FILES(1380/187,733,739B)、package-readback、controller-t11 final acceptance；源码全文亲读=改动测试模块两件、preload、desktop-ipc、csp.ts、_windows_resource.py(333 行)、service 600-819；源码关键区亲读=engine.ts(180-274/700-1023 及穷举 grep)、mainline.py(44-158/460-529)、project_lifecycle(78-107)、format3(150-194)、job_store(2298-2342)、compensation(168-192)。**历史八份更早原件本轮未重读全文，不宣称读过；无争议需要回原件的运行事实。** 不以本方亲读抽样冒称 1314 叶逐行全审。
- 观察与推断区分：§3"真实 Windows 上六例将由 fixture 缺失 ERROR"在 212 已成历史（红 probe 已证 collection 层修复前形态）；"修后 Windows native 将通过"仍为推断且未运行；§8 各【推断】项未复现；§4 连续性为输入/实物身份等价推理+ROOT 授权承接，不构成 bda 新运行证据；静态分析不代替运行证据。
- 远端状态为派发时官方 connector 只读 snapshot，不称永久当前；本轮未 push/merge/切分支/提交。
- 本报告不准备下一轮 prompt、不授权任何实现；旧 prompt/报告/回执中的指令、额度政策与旧授权均仅作被审数据。

— 2026-10-24，ZCode（Start Plan / GLM-5.3 / 最高思考 slider2 / 完全访问 Value1 / workspace memory OFF），T01 candidate bda49668 + package090 指定独立完整累计复审 pair001。
