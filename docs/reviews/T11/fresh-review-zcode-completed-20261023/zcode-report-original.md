# T11 036 全新完整指定独立审查报告（ZCode / GLM-5.3）

日期：2026-10-23（Asia/Shanghai）。审查者：ZCode，指定模型 GLM-5.3，思考 最高(max)，权限完全访问（yolo）；只读审查职责不因完全访问扩大。

## 0. 终态结论（先行）

| 维度 | 结论 |
| --- | --- |
| **完整工程范围（原25产品路径按036现状 + 原8流程 + 本轮23变更 + 56个requiredFiles 全量，含 verify.ts/verify-release.mjs/三collector脚本/两测试/两fixture/全部T11文档与证据链）** | **通过** |
| 18项原意见（M 12 + Z 6） | 本方逐项处置见 §7：可在工程范围关闭的 12 项判定关闭；依赖真实目标环境的 6 项（Z-F4/F5/F6 运行面、M-F-H②真实同包、及对应真实验收）为**部分关闭/无法验证**，父门保留。原严重度与 M 对 7d28 的 NotPass 作为历史记录保留，不因此改写 |
| 真实平台/发布验收（双OS真机安装/native/凭据/恢复迁移、签名公证、真实API零伪造评估、五真人、Q5容量、指定双审合成、CI/push/PR/合并/远端、最终渠道下载实装） | **无法验证 / 未关闭**，全部按原门保留 |
| 核验器发布授权 | 恒 `releaseAuthorized:false`（类型层面固化 + 全部实测路径一致），本报告"通过"不构成发布授权 |

通过的含义：036 冻结字节与自身验收文档（acceptance.md/v3规范/README/user-study）一致；本方独立环境复现全部关键验证（探针 109/109 零 skip、默认 105|4 skip、缺873对象显式失败、全仓 check 0 退出、显式 lint/format、bash -n）；独立复核 873 固定基线、57 P0、G50、Q9 决议、两份 raw 归档全部成员字节/hash；未发现新的 P1–P3 阻断缺陷（仅 4 项信息级观察，见 §8）。本通过是新审独立结论，不继承 Z 对 7d28 的旧 Pass，也不被 M 对 7d28 的旧 NotPass 约束；M 的 12 项意见在 036 上的修复经本方逐项核实（§7）。

## 1. 任务来源、设置读回与 provenance

- 任务来源：用户消息所附 full-prompt.md。本方 `.t11-review-runtime/input/full-prompt.md` 实测 **26496 bytes / SHA-256 `b5676374b24ac30a2c9cca0e25ba6c65c6c01b2fff675d1717df6d8a4e0f3c22`**，与用户给定值一致；已完整读取全文（157行）并执行，未只读预览、未降为18项delta。
- 实际设置读回：仅读本方 `metadata/operator-ui-settings-before-send-20261023.json`（未读 global config、agent list、peer 任何文件）：modelUI=**GLM-5.3**（菜单选中）、effortUI=**最高**（slider 2）、permissionUI=**完全访问**（任务切换模式实读），workspace/HEAD/guide（15147B/de15f6ce…）均与本树一致。该收据 `sessionId:null`、`actualBackendScalarUntilOwnNativeReadback:"UNKNOWN"`。
- 本报告 provenance 如实登记：模型=GLM-5.3（本会话系统声明 account:bigmodel-individual-coding-plan/GLM-5.3，与本方收据一致）；effort=最高；permission=完全访问(yolo)。**sessionId/taskId/turnId 及后端实际标量：UNKNOWN**（本方 metadata 未记录原生读回，不以默认配置冒充实际设置）。
- cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-zcode-review-036d7172`（实测一致）；HEAD=`036d7172ddba8502fe81e6e7ce375ce09ef7fa1c`（detached，实测一致）。工作树差异仅 ` M AGENTS.md`（15147B，SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，最新政策差异，保持未暂存）与未跟踪 `.t11-review-runtime/`——与 source-setup.json（892受控文件、onlyPolicyDifference=["AGENTS.md"]、approvedFixed873ObjectPresent:true）声明一致，本方逐项复核成立。
- 身份链：原工程base `5f910b52…`、原产品 `7d28fdb2…`、修复base `692077da…`、受验实现/测试 `33894063…`（Git对象均在）。实测 `692..338` 恰 15 路径（实现/测试/文档），`338..036` 恰 9 路径（owned-fixes 8件 + status.md，全流程件），合计与本方 handoff-manifest `ownedRepairAndProcessChanges23` 的 23 条完全一致；338→036 的 14 条实现/验收路径（5脚本+2测试+comparison fixture+acceptance/v3/README/migration-recovery/user-study/q9）逐 blob 比对**全部 SAME**，"036 仅本轮独审和流程收尾"成立。
- 独立性：未读取任何 peer 本轮 prompt/receipt/report/state/metadata（即使路径可推断也未尝试）；未访问父 `.worktrees`、总控队列或全局应用日志；仅阅读显式列为历史的两份完整报告、18矩阵、triage 全套与旧 raw 归档。未 stage/commit/push/PR/切分支，未修改任何受审实现/测试/依赖/配置；仅在自己 runtime 写 raw/metadata/本报告。

## 2. 输入完整性与受控文件核验（全部通过）

1. **56 个 requiredFiles**（handoff-manifest 逐条 bytes+SHA256）：本方逐一实测，**56/56 全部字节级一致，0 缺失 0 漂移**；覆盖原25产品路径、8流程件、23变更件、历史两报告/18矩阵/triage/raw 全套。
2. **两个二进制归档**（tar 成员不解包流式核验）：
   - `owned-fixes-20261023/raw-logs.tar.gz`（2825B，归档 SHA `2e714950…` = index 登记）：14/14 成员字节+SHA 与 raw-logs-index 全等；已读全部失败日志（§5）。
   - `round-1/raw-logs.tar.gz`（7208B，SHA `c1f34bd3…`）：48/48 成员与 index 全等（entryCount=48、sourceRecord 指向 verification.json `0cb03592…`）；已读关键失败原件（unit-third-run 40 failed、check-first-run、check-second-run ENOENT、fixed-baseline 全链等）。
   - **首跑 38 失败无独立完整 raw**：实测归档内确无含 "38 failed" 的日志，仅 `first-failure.json` 摘录（`digest is not a function` + 旧 usage 行）与 transcript 线索；status.md"历史失败保留范围更正"段与 history-archive-verification.json（48/48）如实登记，既未声称齐全也未声称永久不可得。本方不重跑补造。
3. **873 固定基线独立复核**（只读 `git show`，本树对象存在且为 commit）：manifest SHA 实测=`aaaef2c023320038bc155640566bdc69e0c358e7c380` 后接 `23…ac39e`（下同，与批准值全等）；source=PRD SHA=`7586b2c4…f60fbb`（**当前树 PRD 同 hash，逐字节等同冻结版**）；`files` 恰 17 路径，逐一 `git show` 后 SHA 全部吻合（content/learning 4件 + tests/fixtures/product-baselines 13件）。
4. **57 P0 / G50 独立解析**：按核验器同款正则解析 873 版与当前版 PRD：P0=57 且唯一（两版一致）；G.1 表行 37（M-01…A-10）+ `### G.4` 起顶层 `- ` 列表 13（实测 6 条来自 G.4、7 条来自 G.6，G.5 无顶层列表）= 50；873 `coverage.json` 恰 50 条，id 集合与 PRD 推导全等、逐条 source 与 PRD 原文全等；`cases.json` 50 条 id 与 coverage 全等；指针用例恰 3 条（G-list-01 exact `/expected`、G-list-02 exact `/expected/3`、G-list-06 replayExact `/expected/3`），E.5 基线文件含基准/对比两场景完整期望。
5. **Q9 决议绑定**：`q9-decision-source-20261023.json`（批准来源 `iteration-control/…/decisions.md`，SHA `def9817dc35c11514335fce5ecf859878e00cdfccc259659edb7925fee9d84a7`，2026-10-21，§首选真实模型服务 L21–29）与 verify.ts `APPROVED_MODEL`（endpoint `https://api.deepseek.com/chat/completions`、requestedModel `deepseek-v4-pro`、decisionSha256 同上）及 README §Q9 三方一致；"endpoint 指具体路由、Base URL 是 `https://api.deepseek.com`"的语义在文档与代码一致，Base URL 冒充 endpoint 有专门拒绝测试。
6. 环境隔离：本树独立 `node_modules`（node v24.15.0/npm 11.12.1）与 `.venv`（uv 0.11.12），均非符号链接；setup 两日志实测 bytes/SHA 与 setup.json 登记全等（npm-ci 631B/`82595a73…`，uv-sync 900B/`c5336a7e…`）；本轮全部命令 TMPDIR/TMP/TEMP 指向本方 `.t11-review-runtime/tmp`，日志新名落本方 raw，未覆盖任何失败。

## 3. 12 条审查标准逐项结论（共同正文§全范围审查标准）

| # | 标准 | 本方结论与证据 |
| --- | --- | --- |
| 1 | 严格 schema、身份/预期 hash、独立 freeze、不自证 | **符合**。manifestSchema/expectedSchema 及全部子 schema `.strict()`（verify.ts:10-246）；source/candidate/reviewedSha==freeze.candidateSha（:518）；releaseAuthorized 为返回类型字面量 false（:212-217,1074）；freeze 由 CLI 独立注入且强制覆盖 now（verify-release.mjs:12-15）；expectedResults 逐 `${label}:${id}` pin（:706）；两端同填假数据仍被 APPROVED 常量与 baseline 唯一 manifest 拒绝（测试 refuses arbitrary service tuples / unapproved production profiles） |
| 2 | CLI manifest/freeze 16MiB、大文件 8GiB、先限额后 parse、同 fd、增长/短读/非regular/读错误关闭、TOCTOU 不虚称 | **符合**。withFile：O_RDONLY\|O_NOFOLLOW\|O_NONBLOCK 打开后 fstat（非regular/空/超限→FILE_BOUNDS）→ 限额后 alloc/parse → 同 fd 完整读取/hash/PE/koly → 尾部再读1字节检增长（FILE_CHANGED）→ fstat 比对 size/ino/dev/mtime/ctime → finally close（:363-403）；readJsonFile 16MiB 先限后 parse（:404-407）；verifyLargeFile 8GiB、1MiB 分块流式 hash（:434-451）；叶 symlink 经 realpath 解析后出根即拒（boundPath :346-359）；注释明示"不保护并发替换的祖先"、README:43 同口径，未宣称消除全部 TOCTOU；IO 专项 9 例含限额前拒绝/增长/短读/读异常关闭/非regular/叶替换/外部symlink 全过（本方亲跑） |
| 3 | 双目标、结构标记≠签名链、native 证据保持 | **符合（结构级）**。artifacts 恰2且目标互斥；dmg/koly 与 NSIS PE(MZ→PE→machine 0x14c/0x8664) 仅结构判别（:417-433）；Mac 另强制 hardenedRuntime/notarized/stapled + 4项签名报告，Win authenticode+时间戳+3项报告；组件 inventory 与 licenses 多重集等价；下载 URL https/无凭据/无query/hash==候选/installed。README:45 明示结构标记不证明 NSIS/DMG 实质与签名可信；metadata valid 不能证明签名可信——README§核验的实际边界明示 |
| 4 | 57 P0、G50、T09 唯一 manifest 17 文件、E.5 指针、生产 profile | **符合**。§2.3/2.4 独立复核全等；evidence 模式显式固定 873 manifest SHA/prd-v0.6-learning-1/PRD SHA/17 精确路径集合（:562-576，多余键比较为排序多重集）；内容 hash 仍从唯一 manifest 逐文件读取（:579-580），无第二基线；探针测试实测 17/17 文件 hash 联验（本方亲跑 109/109） |
| 5 | RDF SPO 无序保重、其余保序、1000轮等原要求不用模拟冒充 | **符合**。compareProductComplete 仅对 {facts,assertedFacts,inferred,addedTriples,inputs} 且全部元素为完整三字符串键 SPO 时排序多重集（保重复），其余数组严格保序（:467-492；单测直接断言重复数与 events/trace/rounds 保序）；1000轮/每轮1000/已提交不可变/取消/响应丢失属 PRODUCT(57 P0)与 DEVICE_CHECKS 报告覆盖（:248-292），全部 actual 为合成/oracle 构造，acceptance.md/README/status 一致声明"不代表50项产品用例通过"——无模拟冒充 |
| 6 | v3 投影、current-state 空层、PRD模板边界、G.6 双向固定、22迁移check、旧v2拒绝、零提交重放、模板负向 | **符合**。snapshotSchema v3（:914-996）：current-state 允许 definitions/mappingState/queries/results 合法空；facts/ownership 为空即 TEMPLATE_NOT_RESTORABLE（对应 PRD G.6/FR-1000 模板边界，未代答 F01）；g6-conflict 六层非空；两迁移槽 freeze literal g6-conflict（:233-239）不可双边改写降级（测试 MIGRATION_BEFORE_CASE/EXPECTED_IDENTITY）；MIGRATION_CHECKS 恰 22（:318-341）含 relink-rerun-conflict/continue-edit-query-undo/replay-zero-commit-inputs 等；UNSELECTED_CONTENT 五类未选必空；MAPPING/REPLAY_CAPABILITY 布尔严格等于依赖推导；v1/v2 拒绝不转换（测试）；零提交 rounds=[] 可重放正例（zero-commit-replay）与完整初始输入重放边界保留；T11 未另造 Store/项目包/恢复器（migration-recovery.md:3 明示） |
| 7 | 旧资产独立 pin、两项回退 check、原 check 保留 | **符合**。previousAssets 恰2（target/version/sourceSha/sha256）独立 pin；回退资产禁等于当前资产、禁同版本/同候选、结构+签名+公证链检查（:1013-1054）；`rollback-retain-new-version-copy`、`rollback-refuse-incompatible-format` 在 RECOVERY_CHECKS（:308-317）与每个旧资产报告必检 id（:1041-1053）中双落；具名 check 不证明真实操作——README:31/migration-recovery.md:23 明示 |
| 8 | 两 collector 完整审 | **符合（静态+合成；真实运行未验）**。Mac：全部已知系统命令绝对路径（/usr/bin/uname、/usr/bin/sw_vers、/bin/mkdir、/bin/mv、/usr/sbin/sysctl、/usr/bin/shasum、/usr/bin/plutil、/usr/bin/file、/usr/bin/codesign、/usr/sbin/spctl、/usr/bin/xcrun），最前 OS/arch 门（arm64+15.*），pending/step 全程、失败 failed+有限exit、首raw与半成品保留、新目录防覆盖（`! -e`）、成功末尾才 complete、EXIT/INT/TERM trap；Windows：--ApprovedIsolatedSession 强制、Win11+X64 门、输入叶子文件、新目录、首 raw signature-i.json 先落再验、pe-machine.ps1 受控 DOS 长度(≥64)/offset(64≤o≤len-6)/PE签名/machine/size-changed/finally dispose/PE_INVALID 固定错误不回显原异常。核验器侧：collectorStatus 严格 `{complete,complete,0}`，缺/pending/failed/malformed 拒（4态测试）；collector-complete actual 与 status 文件 hash 绑定；installed-components-match-package 严格 `{packageSha256,inventory,app,engine,method,provenance}` 且 packageSha256==候选包 hash，inventory/provenance 读核、app/engine 大文件 hash；代码注释明示"绑定声明字节，不证明安装/解包 transcript 真实性"，README:31 同口径——marker≠native/签名/同包，真实 T03 唯一包内成员与原件对照仍为独立门 |
| 9 | Q9 批准 tuple 双向 pin | **符合**。§2.5 三方一致；manifest 与 freeze 任一漂移、Base URL 冒充路由、任意同 tuple 服务均拒绝（MODEL_PROFILE_DRIFT + 测试）；返回模型/服务版本/模式/评估 hash/零伪造继续独立冻结（MODEL_CHECKS 13 项含 endpoint-change/prompt-injection/offline-fallback）；不授 API 资源或消费 |
| 10 | ≥5真人/80%、4/5与3/5、core/transfer 矛盾、独立分记、反例、原件核验 | **符合（结构级）**。users≥5 唯一；human/非developer/ontologyNovice/资产绑定/blockers空；成功=coreCompleted&&transferCompleted&&assistance∈{independent,product-hints}，4/5=0.8 恰过、3/5 拒（实测）；core=true/transfer=false 专门矛盾错误；transferIndependent 不能由操作完成推得；每人 agentFullCounterexample 必真、agentMarkedIndependent 必假；产品提示完成与独立迁移分记（user-study.md:25 口径与代码一致，对应 FR-105"分别记录"、11.2、12.1 第8步含迁移+HTML）；F16 跨尝试资格待决不由工具恢复（user-study.md:27 明示）；record 只 hash 不解析，主持人/独立验收人核原件职责成文（user-study.md:29），无自证布尔 |
| 11 | CLI 语法/错误码、synthetic 永不放行、freeze.now 覆盖、时钟外部核验、18项/内部发现有证据处置 | **符合**。参数≠3→usage exit2；读不了/格式错→固定 `MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID` exit2、stdout空、不回显内容（测试实测）；synthetic 一致也 exit1（releaseAuthorized 恒 false）；CLI 用当前墙钟覆盖 freeze.now（伪造2099 now 测试→USER_STALE），README:45 明示工具不认证时钟、由操作者核时间来源/偏差。18项与旧内部发现逐项处置见 §7/§8（owner 未自动关闭/降级，closedByOwner=0，M NotPass 保留——本方为首个出处置意见的指定新审） |
| 12 | 状态/历史标签、双值不混淆、T03 GUI/T05 等焦点不动 | **符合**。status.md 置顶"2026-10-23 owned修复窗"精确入口（日期/工作树/分支/base/SHA/取代关系），历史段落原文保留并标注"仅描述各段当时状态"；同 updatedAt 不同来源 hash（blocked-audit `0b41a993…` vs format-python `cf21df89…`）两份原件并存未归并；本方未触碰 GUI/Goal/队列，未改任何原状态记录 |

## 4. 56 个 requiredFiles 覆盖表（全部完整阅读/核验）

56/56 逐条实测 bytes+SHA256 全等（§2.1），并全部通读。分组结论：

| 分组 | 文件 | 结论 |
| --- | --- | --- |
| 实现5 | verify.ts(38220B,1076行全文)、verify-release.mjs、collect-macos.sh、collect-windows.ps1、pe-machine.ps1 | §3 全项符合；Z-F1/F3、M-F-A/B/C/F/H①③ 修复落实 |
| 测试2+fixtures2 | t11-release.test.ts(45714B,1209行全文)、t11-release-io.test.ts、comparison.json、synthetic-profile.json | 断言到具体错误码/语义边界；全部 fixture 自标 synthetic；探针仅固定873输入物化，actual 为 oracle 构造，边界如实 |
| 迭代文档4 | acceptance.md、selection-comparison-v2/v3.md、shared-file-handoff.md | 验收命令/边界与实现一致；v3 与 snapshotSchema 逐条对应；v2 作为历史保留不追改；共享交接仅提案未越权 |
| 发布文档5 | README、migration-recovery、target-device-runbook、user-study、user-observation-template.csv | README freeze 字段/exit 语义/RDF边界/信任边界与代码全等；runbook 11步+collector 只读边界；user-study 与 participant 字段逐项对应；空表未预填 |
| 原25产品路径中评审/证据12 | approved-fixed-baseline-probe、blocked-audit、completion-audit、external-review-permissions-receipt、first-failure、format-public/python-ownership-receipt、internal-review、operating-policy-receipt、selection-v2-review、status、t09-readonly-alignment、verification.json | 登记/计数/边界与实测吻合（65/695 为 7d28 历史，109/739 为 338 当前，已分层标注）；失败保留与缺口声明如实 |
| 历史2报告+矩阵/计划/子分析 | minimax-report-original.md(50693B 全文)、zcode-report-original.md(29056B 全文)、triage matrix/repair-plan/evidence-index/independent-plan-review/collector-and-io-analysis/index、两 owner-reception、两 received index.json、round-1 history-disposition、round-1 raw-logs-index | 18项源意见（M12+Z6）逐条与 triage 静态核对一致；两收件记录与报告字节/结论（M NotPass、Z scoped Pass）不冲突；历史归档/索引互证成立 |
| owned-fixes 8件 | handoff、verification、disposition、independent-implementation-review、index、raw-logs-index、raw-logs.tar.gz、history-archive-verification | verification 所记命令/计数/失败保留与归档互证；disposition 18项全 open（owner 不自行关闭）；内审 R1 已在338 delta 复核关闭并如实记录 |
| 其余 | q9-decision-source、recovery.json、shared-file-handoff（流程版） | 与上述交叉一致 |

## 5. 本方亲跑命令（既有证据之外的新运行证据；cwd 均为本 worktree 根；TMPDIR/TMP/TEMP→本方 tmp；日志均落 `.t11-review-runtime/raw/` 新名）

| # | 命令 | 结果 | 日志 |
| --- | --- | --- | --- |
| R1 | `npx vitest run tests/unit/t11-release.test.ts tests/unit/t11-release-io.test.ts`（默认） | exit 0；**105 passed \| 4 skipped (109)** | review-default-unit-20261023.log |
| R2 | `T11_FIXED_BASELINE_PROBE=1 npx vitest run …（同两文件）` | exit 0；**109 passed (109)，0 skipped**（四探针执行，17文件/50预期/指针联验） | review-probe-unit-20261023.log |
| R3 | `GIT_DIR=<空git仓> T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-release.test.ts` | exit 1；**4 failed \| 96 passed**，失败均为 `git show 873…` 显式报错——缺 Git 对象显式失败，**无 live HEAD 回退** | review-missing873-probe-20261023.log |
| R4 | `bash -n scripts/release/collect-macos.sh` | exit 0 | （stdout 空） |
| R5 | `command -v pwsh` | 无输出——本机无 pwsh，与 owned verification "PowerShell syntax/runtime (pwsh unavailable)" 一致，PowerShell 静态审阅保持 | — |
| R6 | `npx eslint --no-ignore --ignore-pattern '!scripts/release/**' <4个TS/测试文件>` | exit 0 | review-explicit-lint-20261023.log |
| R7 | `npx prettier --ignore-path /dev/null --check <acceptance 清单：5脚本中2+2测试+2fixture json+docs/release/*.md+docs/iterations/T11/*.md>` | exit 0，All matched | review-explicit-format-20261023.log（首次误带 CSV 报 no-parser 为本方调用错误，acceptance 清单本不含 CSV，已按原命令重跑通过） |
| R8 | `npm run check`（lint→format→typecheck×3→vitest→build→ruff+pytest） | **exit 0**：TS 17文件/**735 passed \| 4 skipped (739)**（4 skip 即默认跳过的探针）、构建3段、ruff All checks passed/207 files formatted、**pytest 1052 passed in 54.53s** | review-full-check-20261023.log |
| R9 | 静态核验脚本（python3/git）：56文件hash、两归档62成员、873基线17文件+P0/G50/coverage/cases/指针、Q9、692→338→036 路径与blob、setup日志hash | 全部通过（§2 详列） | 交互执行，结果载本报告 |

既有证据与本方亲跑严格分列：owner 的 109/739/1052、显式 lint/format、bash-n（cli-assertion-repaired-*、final-* 日志）为 owner 运行，本方仅在归档内核 hash 并读内容；本节 R1–R9 为本方独立新运行。两方结果互相印证，无矛盾。

## 6. 实现细节复核要点（非抽样）

- **M-F-A 修复核心**：v3 snapshotSchema `comparisonCase` + superRefine——`g6-conflict` 才强制六层非空（:964-970）；current-state 空定义/映射/查询正例、模板（facts/ownership 空）负例、六层逐空负例、case 降级（含双边改 freeze）负例全部在测并通过；恢复 case 由 freeze 独立 pin（recoveryComparisonCase 可 current-state/g6-conflict），两迁移槽 literal g6-conflict。
- **Z-F3 修复**：`if (!dest) { fail('MIGRATION_DESTINATION'); continue }`（:1067-1071），不再以 undefined 略过资产 pin；专项测试断言 TARGET_MATRIX+MIGRATION_DESTINATION 并现。
- **Z-F1 修复**：expectedSchema 仅一次 safeParse（:509-515），`Number.isFinite(now)` 保留（:516-517）。
- **CLI 断言修复史**：final-expanded-unit/final-full-check 保留 107过/2败 首败（Node MODULE_TYPELESS_PACKAGE_JSON 警告先于固定错误码污染 stderr，exit2 行为本身正确）；修复为断言 stderr **最后一行**等于固定错误码（t11-release.test.ts:1190），未删警告未改共享配置，后继 109/739 通过记录在档。属工程取舍而非放宽错误面（exit2/stdout空/固定尾行三点仍钉死）。
- **collector 状态机**：Mac `finish` 中 `set +e` 保写 failed marker，写失败保旧 pending/malformed 标记与 raw 文件（两者均不过核验器）；Windows catch 同构（COLLECTOR_STATUS_WRITE_FAILED 分支）。
- **fresh() 时间窗**：所有报告 testedAt∈[frozen, now]；CLI 覆盖 now 后伪造未来 testedAt 被拒（实测 USER_STALE）。
- **evidence() 多余 check 也必须被 freeze pin**（expectedResults 缺键即 EXPECTATION_PIN），防止夹带未审检查。

## 7. 18 项原意见逐项处置（原严重度保留；本方处置为指定新审一方意见，最终关闭需双审收口）

| 原项 | 原级别 | 036 修复核实 | 本方处置 |
| --- | --- | --- | --- |
| M-F-A 六层非空口径冲突 | 高 | v3 case 拆分+独立 pin+模板负向；六层仅限 G.6；双向 literal g6-conflict 不可降级；文档（README:25/v3:7-8/migration-recovery:21）与实现一致；测试正负例齐全并经本方探针亲跑 | **关闭**（工程范围）。原缺陷（文档承诺 v2 放宽而实现全局强制）已不存在 |
| M-F-B 端点/模型硬编码无依据 | 中 | q9-decision-source（dated+SHA def9817d…）入库；APPROVED_MODEL 常量+freeze 双向 pin；单边漂移/任意同 tuple/Base URL 拒绝 | **关闭**（工程范围）。仅固化既有选型，不接 API/网关，授权边界成文 |
| M-F-C 17文件全集未内建约束 | 中 | evidence 模式显式核 manifest SHA/版本/PRD SHA/17路径集合（缺/多/改版本即使双边同改也拒，探针实测）；内容 hash 仍唯一 manifest | **关闭**（工程范围） |
| M-F-D 80%分子口径偏严/迁移不单列 | 中(原列低见注)* | PRD 12.1 第8步含迁移任务→coreCompleted=完整八步含 transferCompleted；core/transfer 矛盾专门拒绝；transferIndependent/assistance 独立分记（FR-105"分别记录"）；不设额外迁移百分比门；user-study.md:25 与代码同步 | **关闭**（工程范围；口径已同步且有 PRD 依据） |
| M-F-E "最终检查"措辞 | 低 | acceptance/status 以命令+日期+候选精确标注；默认4skip与显式探针边界成文 | **关闭**（文档项） |
| M-F-F 回退两项无具名 check | 低 | rollback-retain-new-version-copy / rollback-refuse-incompatible-format 双落于 RECOVERY_CHECKS 与每旧资产报告必检 id，缺任一拒（测试实测） | **关闭**（工程范围） |
| M-F-G 同意/逐段记录无字段承载 | 低 | user-study.md:29 明确主持人/独立验收人核原件清单与工具只 hash record 的边界；不添自证布尔 | **关闭**（文档项；真实原件核验属父门） |
| M-F-H collector 三子项 | 低 | ①半成品：pending/step/failed/complete+首raw保留+核验器拒无complete（合成4态实测）②同包：installed-components-match-package 严格结构+packageSha256==候选+引用字节全核 ③PE：pe-machine.ps1 受控界限+固定错误 | **①③关闭（静态/合成）；②工具侧关闭、真实 T03 唯一包内成员与安装/解包原件对照仍 open（无法在无真实包环境验证，父门保留）** |
| M-F-I 结构/声明≠签名链 | 低 | README:45/migration-recovery/collector scope.txt 明示不解析签名链、不判安装器实质、来源须原件 | **关闭**（文档项） |
| M-F-J 墙钟不认证 | 低 | README:45 时间来源/偏差由操作者外部核验；无任意 --now；CLI 覆盖伪 now 有回归 | **关闭**（文档项；时钟真实性不可由工具证，边界如实） |
| M-F-K 状态双值并存 | 低 | status.md 置顶 dated 入口+取代关系；旧 JSON/报告/双值 SHA 原样保留未归并 | **关闭**（文档项） |
| M-F-L "失败原件保留"强于事实 | 中 | status.md"历史失败保留范围更正"分列首38仅摘录/transcript 与其后48归档；history-archive-verification 48/48（本方独立复核同） | **关闭**（文档项；首38缺口如实保留，不补造） |
| Z-F1 重复 safeParse | P4 | 已删第二次 parse，finite(now) 保留 | **关闭** |
| Z-F2 stat/open 与先读后限 | P4 | 同 fd/fstat/限额后分配/同fd读取hash结构/尾读检增长/finally close；CLI 复用 16MiB 边界；IO 9例实测 | **关闭**（工程范围；祖先目录可信稳定前提明示，未虚称消除 TOCTOU） |
| Z-F3 dest 缺失静默跳过 | P4 | 显式 fail+continue（:1067-1071）+专门测试 | **关闭** |
| Z-F4 Mac PATH 依赖 | P4 | 全部已知系统命令绝对路径（含最前 OS/arch 门与 xcrun）；bash -n 通过（本方亲跑） | **静态关闭；目标机真实运行为父门，未验证** |
| Z-F5 PE 越界读取 | P4 | pe-machine.ps1 DOS长度/offset/PE签名/machine/size 全界限+finally+固定错误；TS 侧小PE边界测试通过；pwsh 本机缺位（本方实测） | **静态关闭；真实 Windows 运行无法验证，父门保留** |
| Z-F6 半成品目录 | P4 | 状态标记+失败原件保留+核验器拒无 complete（合成实测）；重跑新目录 | **静态/合成关闭；目标机真实运行未验证，父门保留** |

\* M-F-D 原报告为【低】，triage matrix 登记低；repair-plan 引述时未改级。原级别一律以 matrix.json 为准保留。

**M 对 7d28 的 NotPass**：历史记录保留（其唯一硬因 F-A 及并行项已在 036 修复并经本方核实）；本方对 036 的工程范围结论为通过，二者不矛盾（不同候选）。**不成立双 Pass**：本报告仅为 ZCode 一方，M3.1-Flash/xhigh 一方全新同版审查及双方意见处理仍待完成。

## 8. 旧内部发现处置复核（internal-review/selection-v2-review/history-disposition 12+2 项）

逐项与代码/测试对照：P1 数量自证（EXPECTATION_PIN+PRODUCT_EXPECTATION_BASELINE+count-only/FR伪造负例）、P1 空壳快照（snapshotSchema+SOURCE_PIN+任意等值行负例）、P1 冻结时间回填（FREEZE_IDENTITY/FUTURE_FREEZE/CLI 强制 now）、P1 文本冒充旧版（结构+previousAssets pin+禁当前资产）、P2 core/迁移矛盾（USER_* 规则）、E.5 指针回归、v2 undo 泄漏（priorUndo+UNSELECTED_CONTENT）、v2 零提交误拒（canRerun/canReplay 推导，rounds 非空不再是前提）、固定873/SPO 续审（本方亲跑复现）、首38失败（缺口如实）、声明误删失败（unit-third-run 40 failed/check-first-run 原件在档）、Python ENOENT（check-second-run 原件在档）——**全部保持关闭且证据在档，无重开依据**；owned 内审 R1（status 入口未同步）已在 338 delta 修复并复核，本方核 status.md 置顶段确认。

## 9. 本轮新发现（无 P1–P3；4 项信息级观察）

| # | 级别 | 位置 | 观察 | 建议 |
| --- | --- | --- | --- | --- |
| O1 | 信息 | tests/unit/t11-release.test.ts:1190 | CLI 超限断言采用"stderr 最后一行==固定错误码"，容忍前置 Node 模块警告。失败史与取舍已完整存档（verification.json failuresPreserved），exit2/stdout空/固定尾行仍钉死错误面 | 未来候选可将 wrapper 改为 `--disable-warning` 或子进程过滤以恢复"整段 stderr"口径；非阻断 |
| O2 | 信息 | scripts/release/verify.ts:600-617 | coverage 的 G-list 提取从 `### G.4` 起扫描全部顶层 `- ` 列表，实际含 G.4(6)+G.6(7)=13 条（G.5 无顶层列表）；代码/注释概称"G.4 lists"。工具、测试与 873 冻结 coverage.json 三方同源一致（本方独立验证 id/source 全等），非缺陷 | 未来候选在注释中写明实际跨度，避免读者误以为仅 G.4 段 |
| O3 | 信息 | scripts/release/collect-macos.sh:19-38 | 参数校验失败（目录未建）走 EXIT trap 时 failed marker 落盘失败在 `set +e` 下静默，仅 stderr COLLECTION_FAILED；核验器侧无 marker 即拒，无错误放行 | 可选：finish 内检测目录存在性再写；非阻断 |
| O4 | 信息（环境） | 本树 packages/engine/tests、storage.py、tests/unit/engine-environment.test.ts | 本方运行临时空仓 `git commit` 时触发 Mimosa pre-commit 钩子，报出本树**既有**静态扫描发现（测试内 SQL 拼接样例、测试内硬编码凭据样例等，标注 high）。这些文件不在 T11 25/56 受审范围、非本轮改动，本方按只读职责未处置未修改，仅如实登记 | 转交相应 owner（T01/engine 线）按其流程处置；不属 T11 工程范围结论 |

## 10. 无法验证边界（不假设通过，不删验收）

1. 两 collector 真实目标机运行（Mac15 arm64 / Win11 x64 的成功、首步/中途失败、防覆盖、真实 codesign/spctl/stapler/Get-AuthenticodeSignature 输出）；PowerShell 语法/运行（本机无 pwsh，本方实测确认）。
2. 真实签名/公证/时间戳链、双 OS 安装/native/凭据/崩溃恢复/双向迁移、真实下载渠道与实装。
3. 真实模型 API 版本化评估与零伪造、五真人研究、Q5 容量口径与测量。
4. 指定双审合成（本报告为 ZCode 一方）、CI/push/PR/正常合并/远端核验、发布分发。
5. 工具固有边界：不能证明 freeze 独立性、报告签发者/真人资格/现实操作真实性；`consistent` 不等于发布授权（README 已声明，本报告维持）。
6. 首跑 38 失败独立完整 raw 缺口（永久性未知，仅摘录/transcript，未补造）。

## 11. 操作边界遵守声明

本轮零修改受审实现/测试/依赖/配置；未 stage/commit/push/PR/切分支（detached 保持 036）；未运行 e2e/install-electron/package:dir、真实 collector/平台 native/窗口/凭据/签名公证/API/网络/新增付费；未导出或查找密钥；未读 peer 任何本轮材料、父 .worktrees、总控队列或全局日志；AGENTS.md 保持未暂存政策差异。产物仅 `.t11-review-runtime/`（raw 6 份新日志、本报告、既有 metadata）。

## 12. 结论重述

- **完整工程范围（T11 离线发布证据核验工具及全部配套，036 冻结字节）：通过。** 无 P1–P3 新发现；4 项信息级观察；12 条审查标准逐项符合；既有披露经逐条核实为准确；关键验证在本方独立环境全部复现（R1–R9）。
- 18 项原意见：12 项工程范围关闭、3 项静态关闭（Z-F4/F5/F6，真实运行属父门）、M-F-H②工具侧关闭但真实同包原件对照 open、M-F-G/I/J/K/L 文档边界类关闭——原严重度与 M NotPass 历史记录保留。
- 真实平台与发布验收：**无法验证/未关闭**；`releaseAuthorized:false` 恒成立；本报告不构成发布授权，不关闭任何父 T11 发布门；同版另一指定审查（M3.1-Flash/xhigh）与双方意见处理、CI/合并/远端门按原规则继续。
