# T02 R13 ZCode 独立完整候选工程审查报告

- 本方实际 SID：`f67a67e285d8e9a84fffd39e138e608e`（新会话，不同于原开发 `session_2c11bc85da8154ac74a7b7bec040bf13`，也不同于 R04–R12 各历史 ZCode/MiniMax SID）。
- 模型/思考等级：ZCode / GLM-5.3 / 最高 / 完全访问。
- 审查对象（实测复核）：W=`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`，branch=`feature/weekly-t02-fr200-fr201`，base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `b02a39b4cd7e8fdbe990e824b22e28b6d2be9d38`，tree `3284bc38e8206096e47c578724cc13548f1c5761`，sole parent `e9a114707e3aeeb4b34f819b77976fe3a9e1c139`，47 累计提交 / 150 差异路径 / 1425 tracked 文件，`git status` 仅 AGENTS.md overlay 与 round-01/02/03 未跟踪（与票面一致）。
- 输入一致性：粘贴 232 行文本与原件 `…/20261028_t02_candidate_freeze_review_095/zcode-complete-input.md`（22165B）`cmp` 逐字节相同，SHA256 均为 `f87a7579da8a42b24feda704c287a844bbc1c60aa867711de1e4dd1bec666fb5`，与票面声明一致。已读至 EOF（含原 160 项完整原文）。
- 本报告为 R13 全新独立审查：不继承 R12 为本轮通过，不读另一方本轮目录（minimax/ 未读、未列目录内容），未运行任何产品/测试/构建/打包/CI/probe，未修改候选源码，未 stage/commit/push。所有运行证据引用均为 O081/O092/O093/O094 既有回执，本人未复跑、不冒运行资格。

## 总判定：ConditionalPass（限定本地技术阶段）

- **当前 push 前源码阻断：0。** 本人对 base→head 全部 150 路径中的产品/测试实现面（约 70 个非归档路径）做了静态审查（含 4 个主进程文件全文、1 个新 Python 模块全文、其余关键差异逐块阅读），未发现新的、需要在本候选内修复的源码缺陷或与 PRD/ADR/M0 计划冲突的实现。
- 该判定**只覆盖本地技术阶段**。完整产品、CI、发布、合并均不放行，条件见 §3；全部原 HOLD 保留（HOLD 关闭数仍为 0）。整体已合并可用 FR 仍为 2/17（FR401/402），Goal/M0/release 未完成，T04 不推进。
- 本轮审查链完整性：12 路径最后增量的实现与 O084–O090 处置逐条对照一致（详见 §5 新增闭环核验）；47 提交累计范围未缩成诊断代码。

## 1. 实际阅读范围与缺口（披露）

**全文阅读**：输入 232 行；AGENTS.md 当前工作树版（含 overlay 与 HEAD diff 对照）；`docs/reviews/T02/status.md`、`docs/m0-checklist.md`；PRD FR-200/201 条款、附录 C/D/E/F/G 全文；M0 更新计划全文（docs/iterations/I01/inputs/ 下实际原件 207 行）；ADR-0001/0002/0003 全文；round-12 `disposition.md`、`owner-errata.json` 全文；O084–O090 七份控制文档全文；O095 `CANDIDATE-BINDING.json`（结构+关键断言）、`development/FREEZE-REPORT.json` 全文；O094 `DELIVERY-INDEX.json`；O092 FINAL-MANIFEST/O093 HANDOFF 关键键；`apps/desktop/src/main/engine-ledger.ts` 全文 769 行；`packages/engine/src/ontolearn_engine/project/mainline.py` 全文 1207 行。
**差异逐块阅读**：engine.ts、index.ts、desktop-ipc.ts、preload/index.ts、tests/e2e/isolated-desktop.ts、coordinator.py、domain_changesets.py、query_presentation.py、rdf_snapshot.py、storage.py、job_store.py、project_host.py、.github/workflows/ci.yml、renderer ontology 六文件、licenses/NOTICE、pyproject/uv.lock、contracts v2.ts（含手写 SHA-256 全函数）。
**结构化/摘要阅读**：round-12 `owner-effective-index.json`（738KB，经 JSON 结构化提取全部 175 位置、17 观察、160 清单行与分类计数，未逐条展开每条 limitRefs 全文）；`scripts/run-engine-tests.py`（528 行的关键 gating/owner/PID 段）、`scripts/engine-test-reporting.py`（头 40 行+插件钩子清单）；`tests/e2e/t02-fr200-fr201.spec.ts`（2180 行：结构、import、头部 80 行与全部 test 描述，未逐行读断言体）；三个关键单测文件读取测试名清单（engine-ledger.test.ts 40 项、t02-ownership-detail.test.ts 13 项、test_mainline_manual_input_rejection.py 17 个 test 函数）；contracts/v2/schema.json 仅定位 ownershipDetail* 定义。
**未读/不读**：另一方 minimax 本轮目录（按票）；R04–R12 双方历史原稿全文（zcode-glm53.md 93KB/minimax-m31flash.md 310KB 未逐字读，其结论经 round-12 effective-index 结构化数据获得，本人不沿用其判定）；vendor rdflib wheel 二进制成员；`tests/e2e/ui-observation.ts`、`OwnershipConflictDetailView.ts` 及其余 14 个 unit 测试正文；O092/O093/O094 的其余 authority JSON 细目。以上缺口不影响本报告的阻断判定，但影响范围见 §3"无法确认"标注。

## 2. Top 10 实际最重要风险（不足数不凑；每项含 stableID/严重性/触发/证据/影响/建议/是否 push 前源码阻断）

1. **完整三平台 CI 门禁未过，且当前 head 无任何新 CI**（承 R11-T01、R11-T02、Z11-R02、F-R09-02 及 status.md CI 节）。严重性：高。触发：push/PR/merge 时。证据：CI45 Quality 在原 15min apt 阶段取消、主 24 例未运行；当前 `b02a39b4` 未 push、无新 CI（本输入 §当前实际验证与证据边界；status.md R12 节）。影响：整候选无法合并；Windows/Mac 真实门禁状态未知残留。最小建议：由 ROOT 另发精确票 push 后跑完整 Quality 15min/Desktop 20min 三平台，要求全部必要 step 自然 green、packaged recovery 步骤自身 success，不加新门禁也不放宽原预算。**当前 push 前源码阻断：否（必要后继 CI/merge 门）。**
2. **Windows E2E 失败根因 UNKNOWN；transport ledger 只是观测不是修复**（承 Z09-02、F-R09-02/03、R11-T02、MM12-N7）。严重性：高。触发：Windows CI 运行。证据：旧 79F 逐例原因未知；CI41 同步 helper12 TypeError、CI43 异步 C1 新形态分列未合因；本轮新增 `engine-ledger.ts`+Windows 条件诊断 step（ci.yml 137–147）只产出首败证据。影响：Windows 平台资格长期悬置，误读"单步绿"为通过的风险。最小建议：保持 ledger/诊断为证据路径，等真实失败样本定因后处置；不得以诊断步骤通过冒充产品验收。**push 前源码阻断：否（后继 CI 门 + 独立 UNKNOWN）。**
3. **engine 与全部后代自然退出未证**（承 Z08-02/Z09-03/Z11-R01）。严重性：中高。触发：任意真实运行收尾。证据：O094 24 次 launch 23 exit0+1 预期 C1 SIGKILL；engine 自然退出与后代清理 UNKNOWN（DELIVERY-INDEX ownerFactualCorrections 第 3 条）。影响：长期驻留进程/资源泄漏不可排除，异常后状态对账依赖持久 marker 而非进程事实。最小建议：在后续真实 CI/桌面票中记录 engine PID 与后代退出码（原窗口）。**push 前源码阻断：否（独立 HOLD）。**
4. **签名/公证/组织/法律/IP/隐私/人类 bus-factor 未核**（承 LEGAL146、HUMAN147；checklist 145–147/154）。严重性：中高。触发：任何对外发布/分发。证据：包为未签名 mac-arm64 开发目录；`.pen`/PRD 归档产权、账户归属未核；全流程由 AI 会话承担，人类复核未发生。影响：发布即面临法律与安全信任缺口；单点故障。最小建议：发布前完成 Developer ID 签名+公证、组织归属核验与至少一次人类工程师接手评审（原 HOLD 窗口）。**push 前源码阻断：否（独立 HOLD）。**
5. **容量口径未定（Q5）、旧超限库恢复与坏 SQLite 物理保护未实现**（承 DATA57；checklist 19–21/156/158）。严重性：中。触发：大库/损坏库打开。证据：mainline.py READ_LIMITS/128MiB 为逻辑账本且自我声明"非 Q5/RSS/SQLite I/O 承诺"；存储保守保留全部快照无 GC；损坏库物理保护在 ADR-0002 与 status.md 反复列 HOLD。影响：真实规模下打开失败或资源失控且无恢复路径承诺。最小建议：Q5 决策后按 S1 两档口径扩测；损坏库"拒绝打开+明确报错"行为补故障注入（原窗口）。**push 前源码阻断：否（独立 HOLD）。**
6. **unknown parser/N3/Store/preview 失败仍为 UNKNOWN 面**（承 MM12-N2 撤回后边界、Z12-N1/Z12-OBS-a；F-R09 系）。严重性：中。触发：构造 RDF 输入命中未分类解析器分支。证据：`rdf_snapshot.py` 新增 `TermInputError` 只把 BadSyntax/Notation3InputError 等确定性输入拒绝分类为 INVALID_REQUEST（vendored fr201.3 patch 专为此）；其余异常仍 ValueError→UNKNOWN/HOLD（domain_changesets.py:455/462 与测试 `test_non_input_failures_keep_original_unknown_and_hold`）。影响：少量畸形输入会以 STORAGE/HOLD 收尾而非可行动错误；语义边界文档需持续维护。最小建议：维持现状不扩大捕获（原 owner 窗口：新增不经封装 parser 入口前复核 standalone EOF）。**push 前源码阻断：否（独立 HOLD/维护）。**
7. **本地 fork rdflib（7.6.0+ontolearn.fr201.3）供应链维护面**（承 MM12-N8、T03/vendor 观察及 checklist 38/39/136）。严重性：中。触发：上游 rdflib 安全更新或打包复核。证据：`packages/engine/vendor/rdflib/` 固定 fork wheel + notation3 补丁；PROVENANCE/NOTICE/锁文件三处一致（本人已核对 pyproject/uv.lock pin fr201.3）；包内物理路径核验留待未来制造票。影响：安全补丁响应依赖手动重打 fork；NOTICE 声明与包内实际路径可能出现偏差。最小建议：建立上游 diff 跟踪与升级窗口（原窗口），打包票内复核 NOTICE 物理路径。**push 前源码阻断：否（维护建议）。**
8. **contracts `v2.ts` 手写 SHA-256**（本轮本人复核确认；见 §4 N-R13-01）。严重性：低-中。触发：renderer 侧 ownership detail 分段校验。证据：`packages/contracts/src/v2.ts` `ownershipSha256`（约 60 行手写实现；无 node:crypto 依赖，因需在 renderer 语境运行）。本人静态核对：常数、σ/Σ/Ch/Maj、填充与 ≤32KiB 长度域全部正确，且有 exactly-1024B/临界边界测试与 Python 端 hashlib 交叉验证链。影响：非正确性缺陷，但手写加密原语长期维护易错（后续改动无库回归保护）。最小建议：增加固定 NIST 测试向量单测锚定实现；若未来迁移到 SubtleCrypto 或共享库需同版双端验证。**push 前源码阻断：否（维护建议）。**
9. **剩余 Undo/ownership 家族与 FR200 编辑后四具名下游（推导/保存查询/SHACL/报告）GUI 未验**（承 R08 收窄子集、status.md 各轮 OPEN 窗口）。严重性：中。触发：用户执行定义级 Undo 之外的操作或编辑后查看下游结果。证据：已验子集仅"定义 Undo/Undo-of-Undo/owned restart"（O056 18 例）；公共失效九行正负例在位但不替代四类下游实测。影响：编辑后过期/撤回语义在真实 UI 路径上未证实，可能误展示为当前。最小建议：在后续授权触及对应家族/下游接线时逐类补 GUI 验收（原具名窗口）。**push 前源码阻断：否（独立 HOLD）。**
10. **本地数据无静态加密：设备物理访问可直接读取项目库/快照**（checklist 45/51 的本地化等价；承既有"加密 at rest 部分适用"结论）。严重性：中低（单用户本地产品，威胁模型有限）。触发：设备丢失/共享。证据：SQLite 与快照明文存储（架构当前无加密层）；凭据未来走 safeStorage 属 S3（未接入，当前无凭据可泄）。影响：本地 ontology 数据可能含业务敏感内容，失窃即泄露。最小建议：发布前评估 SQLite 加密扩展或文档明示边界；不在本候选内新增。**push 前源码阻断：否（发布前评估项）。**

## 3. 判定条件与阻断分类

- **当前源码阻断（本候选内必须修复）：无。**
- **必要后继 CI/merge 门（ConditionalPass 的条件，全部保留原口径）**：同交付实现/测试/CI/依赖下，完整发现集合（当前 3798 含新增 29）逐 node 自然 0 或原有据 skip、无失败/早停/取消/timeout/NOTRUN；Quality 15min/Desktop 20min 三平台全部必要 step 真实 success；packaged recovery 步骤自身 success；原 40/45/90 与 5/60/180 预算/断言/原 skip 不变；不加旧根因先证、near-full 余量阈值或故意失败门；远端 develop 实际 SHA/tree/功能复核与精确 merge 票。
- **独立 HOLD（不随 CI 绿自动关闭）**：engine/Windows 后代自然退出 UNKNOWN；签名/公证/wholeApp 法律与 _distutils；跨 OS（macOS15/Win11）与参考 8GB 设备；容量/旧超限库恢复/坏 SQLite 物理保护；unknown parser/N3Store/坏快照；其余 ownership 家族与剩余 Undo；四具名下游 GUI；sys.path 等价；旧 79F/CI40–45 各首败根因 UNKNOWN 不倒填；法律/IP/隐私/真实人类 bus-factor；供应链/license 全量核验。HOLD 关闭数仍 0。
- **无法完成/无法确认（本人未运行）**：一切运行时行为（check/GUI/打包/CI/性能）本人零复跑；FR201 编辑后四下游、A11Y、RTL/emoji 专项、五年前设备、NOTICE 包内物理路径、组织归属（checklist 146 唯一"无法确认"行）等均按既有证据边界标注。
- **维护建议（非门禁）**：见 Top10 #7/#8 及 §4。

## 4. 本轮新发现（单列；均非阻断）

- **N-R13-01 手写 SHA-256（contracts/src/v2.ts `ownershipSha256`）**：见 Top10 #8。本人逐行核对实现正确；因未读另一方本轮报告，无法确认是否与其本轮观察重叠，作为本轮本人独立记录。
- **N-R13-02 `_MainlineReader._preflight` 对 `owner.current` 的隐式非空依赖**：`mainline.py:469–474` 直接访问 `owner.current.method`；当前所有调用路径（budget 均由 current reply 构造）保证非空，但该不变量是隐式的。若未来新增无 current 的 preflight 调用将 AttributeError→非 JobFault→unknown+hold（保守失败，非安全问题）。维护观察。
- **N-R13-03 `MainlineHost.close()` 的 `_clean_close` 语义**：`mainline.py:1202–1206` 先置 `closed=True` 再 `reader.close()`，异常时 `_clean_close` 保持 False——后继 bind 因非 clean predecessor 拒绝。语义正确且保守，仅记录确认。
- **N-R13-04 coordinator bootstrap 别名 `_BOOTSTRAP_JOB_STORE = JobStore`**：coordinator.py:42 模块级别名用于 serve 内 isinstance 防重绑定，正确性 OK；属可读性观察。
- 以上均不构成 push 前源码阻断；未发现需运行证实的新的产品缺陷反例，故无需向 owner 提交最小验证建议。

## 5. 最后 12 路径增量与 O084–O090 处置对照（本人静态复核）

- `engine-ledger.ts` 769 行与 O087 六条修正逐条吻合：独占创建（`open(path,'ax')`）、短写即败不重试（`bytesWritten!==chunk.byteLength`→fail）、计数器饱和（`#saturate` 至 4096 且 saturated 强制 incomplete）、footer 前缀记账+1025B/1 条预留、ID 白名单单次读取（`readId` 128/模式限制）、job.create 顶层 result 字段与 project.create 无 Job、job.state 取 `data.state`。
- 接线满足 O084/O087 边界：`index.ts` 主进程侧 gate（win32+未打包+flag+launchId UUID+`--user-data-dir` 与实际 userData resolve 相等+`ontolearn-e2e-profile-` 前缀 6–48 位后缀）；Supervisor 独立再拒 packaged；`recordRequestPrepared` 只读已注册 strict clone 且位于 recovery-pin 之前（pin 与 write 之间零 observer）；`recordResponse` 在结算后以匹配 pending.request 的 method 记录；`recordNotification` 在原校验与会话匹配之后、listener 投递之前；close 监听为原 listener 原地扩展（fail 先行、不新增第二监听）；`requestStop` 只请求封账不等待。
- e2e 收集器实现 O088 R01/R02/R10 修正：footer 两标志必须为真 boolean 才计完整、缺尾 LF 即 incomplete、close 恰一次且收集失败不掩盖原错误（`closeAndCollectLedger` try/finally）、读取上限 524289 单次 open、外文件/过期文件只记元数据（foreign-or-stale）。
- 单测覆盖与 O089/O090 补齐项对应存在（engine-ledger.test.ts 40 项含 byte-cap-before-record-cap、exact-1024B、callback-error、no-callback 生产上界、预留字节临界含 flight/queue/overflow；supervisor 13 项含新 session 后旧 close、stop 后未全 close 无 footer；collector 21 项含 closeError 引用相等与顺序）。
- `coordinator.py` bootstrap（business3+JobStore+非 test+无 ordinary/query dispatch→`prepare_mainline_store`）与 `mainline.py` `_WriteAdmission`/`MainlineHost` 的授权链、`job_store.py` `_transaction` 写入接纳（before_commit 终态增长核对 `admit_terminal_growth`）、`_persist_ownership_detail`/`ownership_detail_page` 分段文档（指纹去重、双侧 admissions、页界 262144）、`storage.py` 墓碑/单值声明见证（`ManualOwnershipConflict`/`SingleDeclarationConflict` witness 含首阻断行定位）、IRI memo（16 别名+身份门+保守 disable）与 R12 Z12-N1..N4/MM12-N2/N3 处置一致。
- `rdf_snapshot.py`/vendored fr201.3 补丁与 MM12-N2 撤回后的正确边界一致：仅确定性输入拒绝分类，未分类失败保 UNKNOWN。
- CI workflow 差异与 MM12-N7/E06 一致：Windows 条件诊断 step（`--maxfail=1` 仅失败早停、locale 探针）、`CI_ENGINE_TEST_SHARDS=2`、逐 run JSON reporter+always 上传 test-results/engine-tests；`run-engine-tests.py` 无 flag mode1 与 mode2 保持原 `os.execv` 直跑（本人读关键段确认）。
- O095 冻结链完整性：FREEZE-REPORT 记录普通 12 路径 commit（e9a→b02a39b4，stat 12 files +3675/−24），票面 12 blob 与测试源字节绑定 passed=True；`atUTC` 含 `03:0x` 占位值（作者自述未核，原样保留不改写）；Mimosa `scanner_enobufs` 无 scanner 原件佐证（仅 hook timing），按作者自述保留，不当作安全扫描完成也不当作绕过。runtime HEAD（e9a+12WIP）与提交后 blob 相同字节，不把测试运行 HEAD 倒写为新 head——本人核对的 base/head/tree/47/150/1425 与票面一致。

## 6. 原 160 项清单逐项处置（本人独立判定；每行一个类别；合计 160=23 适用+66 部分适用+70 不适用+1 无法确认）

产品事实基准：本地优先 Electron 桌面应用（单用户、无服务器、无登录、无多租户、无支付、无邮件、无云）；当前正式能力 health+已合并 FR401/402；FR200/201 与存储/任务基础设施在候选内。分类不是产品通过数。

| # | 主题 | 类别 | 当前依据（本人检查） |
|---|---|---|---|
| 1 | 设计化 schema | 适用 | storage.py 固定 DDL+user_version+LAYERS 白名单+ADR-0002 版本化，非逐表即兴 |
| 2 | email+登录 | 不适用 | 无账户/登录体系（本地单用户） |
| 3 | 密码重置链接 | 不适用 | 同上 |
| 4 | MFA | 不适用 | 同上 |
| 5 | 会话超时/踢出 | 不适用 | 无用户会话；引擎会话 fence/预算是另一语义 |
| 6 | SSO | 不适用 | 无企业客户面 |
| 7 | SAML | 不适用 | 同上 |
| 8 | SCIM | 不适用 | 同上 |
| 9 | 深于 admin 的角色 | 部分适用 | 无 RBAC；有 capability/owner 授权链（mainline/_OwnershipProof/附录F 白名单设计） |
| 10 | 改 ID 越权读 | 部分适用 | 本地单用户威胁模型不同；projectId!==selected 拒绝、operation claims、proof.check 在位 |
| 11 | 租户隔离 | 不适用 | 无多租户；项目按库内隔离 |
| 12 | admin 代登录 | 不适用 | 无此面 |
| 13 | 登录限速 | 不适用 | 无登录 |
| 14 | 锁定保护 | 不适用 | 无登录 |
| 15 | 迁移前进/回滚 | 部分适用 | v0→v2→v3 前向迁移+故障回滚 hook 有测试（合成 424P+44S）；降级迁移/发布兼容无承诺 |
| 16 | 迁移不锁主表 | 部分适用 | BEGIN IMMEDIATE+迁移写锁防双 opener；本地单进程无"2pm 高峰"但锁窗口真实 |
| 17 | 索引 | 部分适用 | 固定主键/唯一约束；大表索引未按容量设计（Q5 未定） |
| 18 | 连接池 | 不适用 | 单进程本地 SQLite |
| 19 | 每晚备份 | 部分适用 | Store.backup 在线备份 API+测试；无自动夜间任务（本地产品语义） |
| 20 | 已测恢复 | 部分适用 | 备份恢复经测试；跨设备项目包恢复属 FR-1000 未实现 |
| 21 | PITR | 不适用 | 本地单库，快照/版本链替代 |
| 22 | 软删除 | 适用 | 受管事实墓碑、删除留痕、commit_evidence 前后快照；定义级 Undo 子集已验 |
| 23 | 服务端校验 | 适用 | zod strict+引擎 contract 双层、错误码白名单（AGENTS §7） |
| 24 | 时区存储 | 不适用 | 无定时提醒；时间戳为安全整数毫秒 |
| 25 | 撇号姓名 | 部分适用 | Unicode 字面量/引号全链路有（canonical N3、text002）；无姓名字段场景 |
| 26 | emoji/RTL | 部分适用 | UTF-8/多字节边界（4096 cap、续字节检查）有；RTL/emoji 专项未见显式测试 |
| 27 | 金额整数 | 不适用 | 无货币；xsd integer 词法（含 digit limit）在 fr201.3 处理 |
| 28 | 货币/税务 | 不适用 | 无交易 |
| 29 | 数据模型抗二客变更 | 部分适用 | definitions 规范 JSON+依赖向量+不可变快照；无真实第二客户压力 |
| 30 | 幂等键 | 适用 | 同 operation/job 重试返回原标记不重复写入；commit_round 同内容幂等 |
| 31 | 重复提交去重 | 适用 | 同上+case7 单 commit/0 replay 断言+delivery wires 绑定 |
| 32 | 第 400 页分页 | 部分适用 | 512 成功续页已证非固定 8；超大页深未逐页实测 |
| 33 | 导出 | 部分适用 | Turtle 导出属 FR-203 未实现；诊断/diff 附件导出在测试链 |
| 34 | 2009 CSV | 不适用 | CSV 解析属 FR-300 未实现（映射计划 API 非解析器） |
| 35 | 保留规则 | 部分适用 | collect_cache 只回收可重建载荷、pins 保留、历史不可清理；产品级保留策略不存在 |
| 36 | 密钥不入库 | 适用 | 当前无任何凭据；repo 未见密钥；S3 前凭据只在主进程（ADR-0004 计划） |
| 37 | 轮换 AI 贴的密钥 | 不适用 | 无已知贴入历史 |
| 38 | 确认安装的包 | 部分适用 | npm/uv 双锁精确 pin+vendored wheel PROVENANCE；完整供应链核验 HOLD |
| 39 | 依赖扫描 | 部分适用 | 锁文件+固定版本；无自动漏洞扫描/SBOM 全量（NOTICE 在库）；dependabot 配置存在未核 SLA |
| 40 | 输入消毒 | 适用 | 边界 zod strict、IRI/term 白名单、错误参数白名单不回传原值 |
| 41 | SQLi/XSS/CSRF/OWASP | 适用 | 全参数化 SQL（? 占位）；CSP 单源无 inline/eval、contextIsolation；无 HTTP 面 |
| 42 | 文件上传 | 不适用 | 无用户上传；example 资源是受信 bundle+SHA 绑定+O_NOFOLLOW/FIFO 拒绝 |
| 43 | CORS | 不适用 | 不开 HTTP 端口（架构不变量） |
| 44 | 安全响应头 | 部分适用 | CSP meta/header 双变体单源；HTTP"每响应"语义不存在 |
| 45 | 静态/传输加密 | 部分适用 | 本地文件明文（Top10 #10）；无传输面；模型 TLS 属 S3 |
| 46 | 最小权限 | 适用 | 渲染端无 Node、preload 白名单、引擎无凭据、Agent 白名单、_OwnershipProof 链 |
| 47 | 日志不记敏感 | 适用 | 最小日志、固定错误码、ledger 只记白名单 ID；无密码类数据 |
| 48 | 渗透测试 | 不适用 | 当前无对外暴露面 |
| 49 | 安全问卷 | 不适用 | 无企业买家 |
| 50 | 漏洞披露流程 | 不适用 | 未发布；发布前建立（维护建议） |
| 51 | 笔记本被盗 | 部分适用 | 本地明文库可被物理读取（Top10 #10）；无凭据可泄 |
| 52 | SOC2 | 不适用 | 无企业服务面 |
| 53 | HIPAA | 不适用 | 无医疗数据承诺 |
| 54 | BAA | 不适用 | 同上 |
| 55 | 查看审计 | 部分适用 | commits/commit_evidence 记录变更依据；"谁查看了"不存在（单用户） |
| 56 | PCI | 不适用 | 无支付 |
| 57 | GDPR 删除 | 不适用 | 本地单用户；无服务端残留面 |
| 58 | 数据驻留 | 不适用 | 完全本地 |
| 59 | 季度访问审查 | 不适用 | 无组织访问面 |
| 60 | dev/staging/prod 一致 | 部分适用 | 同一套 check/CI/打包；无 staging；CSP 单源双变体 |
| 61 | IaC | 部分适用 | CI workflow+锁文件+打包脚本可重建；无云设施 |
| 62 | 先测后发流水线 | 部分适用 | CI 门禁设计完整但未全绿；无客户可达面 |
| 63 | 一键回滚 | 部分适用 | Git+快照恢复+ChangeSet 撤销 API；部署回滚场景不存在 |
| 64 | 零停机 | 不适用 | 本地应用 |
| 65 | 特性开关 | 不适用 | 无远程特性发布（ledger 旗是 E2E 诊断不是产品开关） |
| 66 | 自动扩缩 | 不适用 | 无服务 |
| 67 | CDN | 不适用 | 无 web 分发 |
| 68 | DNS/SSL 续期 | 不适用 | 无域名服务面 |
| 69 | 后台任务队列 | 适用 | ExecutionJob 状态机+队列上限+取消+资源限额（ADR-0003/I04 实施） |
| 70 | 重试退避 | 部分适用 | 引擎有限退避重启+retryable 标志；无网络重试面 |
| 71 | 死信队列 | 部分适用 | failed 终态+持久记录+UNKNOWN 保留；无 DLQ 产品语义 |
| 72 | cron 不双跑 | 部分适用 | OS writer lease+旧写者隔离是进程级等价物；无 cron |
| 73 | 缓存与失效 | 适用 | invalidation-v2.json 唯一规则源+依赖向量+当前指针隔离；仅模型配置不失效已实现 |
| 74 | SPF/DKIM/DMARC | 不适用 | 不发邮件 |
| 75 | 退信处理 | 不适用 | 同上 |
| 76 | 存储清理 | 部分适用 | 有界回收+pins；无快照 GC（历史增长保留开放） |
| 77 | 成本告警 | 不适用 | 无云成本；FR-903 用量属 S3 后续 |
| 78 | DR 计划 | 部分适用 | 故障注入+恢复验收在 spike/CI；正式 DR 文档不适用 |
| 79 | 第二区域 | 不适用 | 本地产品 |
| 80 | 可搜索结构化日志 | 部分适用 | JSONL 事件流+固定码；无集中日志系统 |
| 81 | 错误聚合 | 不适用 | 无告警邮件场景；错误码目录存在 |
| 82 | 外部拨测 | 不适用 | 无服务 |
| 83 | 告警调优 | 不适用 | 同上 |
| 84 | 仪表盘 | 不适用 | 无服务；性能留原始测量值（S1/B1 口径） |
| 85 | 跨服务追踪 | 不适用 | 单进程+stdio；requestId/jobId 关联在位 |
| 86 | on-call | 不适用 | 无生产服务 |
| 87 | runbook | 不适用 | ADR/状态文档承担部分 |
| 88 | postmortem | 部分适用 | 评审轮次/处置记录实质是复盘且改变流程（O084–O090 链） |
| 89 | status page | 不适用 | 无客户面 |
| 90 | 懂逻辑者写的单测 | 适用 | 3798 引擎+1924 TS 断言真实预期集合/顺序（AGENTS §7 禁数量断言） |
| 91 | 三方 API 集成测试 | 不适用 | 无三方 API；rdflib/pyshacl 为库并有包内样例 |
| 92 | 核心流程 E2E | 部分适用 | 真实 Electron E2E 24 例+包内验收覆盖表单/查询；无 signup/checkout 场景 |
| 93 | 负载测试 | 不适用 | Q5 未定；S1 两档合成测量存在不冒业务基线 |
| 94 | 类生产测试数据 | 部分适用 | G-base/G-behavior 固定基线+fixtures；无生产数据 |
| 95 | 回归测试 | 适用 | 全量 suite 每轮跑+失败保留不覆盖（CI 全集门禁设计） |
| 96 | 旧设备 | 部分适用 | 参考 8GB 设备/低端硬件 HOLD 未测；mac-arm64 开发机已测 |
| 97 | 可访问性 | 部分适用 | PRD 8.9 要求在；键盘/屏幕读者验收未做（A11Y 限证） |
| 98 | 订阅升降级 | 不适用 | 无订阅 |
| 99 | 催缴邮件 | 不适用 | 无支付 |
| 100 | PO 发票 | 不适用 | 同上 |
| 101 | 销售税 VAT | 不适用 | 同上 |
| 102 | 退款 | 不适用 | 同上 |
| 103 | 用量对账 | 不适用 | 无计费 |
| 104 | 年度合同条款 | 不适用 | 同上 |
| 105 | 财务报表 | 不适用 | 同上 |
| 106 | webhook 验签 | 不适用 | 无 webhook |
| 107 | webhook 重试 | 不适用 | 同上 |
| 108 | 版本化 API | 部分适用 | v2/v3 协议版本化+能力声明+不兼容拒绝；无对外公共 API |
| 109 | 客户 API 密钥 | 不适用 | 无此面 |
| 110 | API 限速 | 部分适用 | 65,536 请求/会话+帧/队列/分页/内存限额矩阵是本地等价物 |
| 111 | 三方格式变化预案 | 部分适用 | vendor 锁版本+等价性测试+缓存隔离；预案文档化于 ADR |
| 112 | OAuth 刷新 | 不适用 | 无 OAuth |
| 113 | 客户沙箱 | 不适用 | 无集成面 |
| 114 | 提示注入防护 | 部分适用 | Agent 未接入（S3 前）；附录F/A-04"导入文本不改权限"设计在 |
| 115 | 数据不出网 | 适用 | 本地优先+无遥测+无模型调用+外联拒绝设计（FR-402、B1/I05 边界） |
| 116 | 每客户模型上限 | 不适用 | 单用户本地；FR-903/904 设计在 |
| 117 | evals | 部分适用 | 附录E/G 固定验收模型=产品等价 evals；模型 evals 不适用 |
| 118 | 模型降级 | 部分适用 | FR-806 设计在；未实现（S3 后续） |
| 119 | 模型弃用迁移 | 不适用 | 当前无模型 |
| 120 | 提示/输出日志 | 部分适用 | FR-904 最小外发记录设计在；当前无调用无日志面 |
| 121 | AI 不可逆操作人类审批 | 适用 | Agent 只产草稿不自动确认；preview/confirm 两步+proof 绑定人类会话（FR-804/架构不变量） |
| 122 | 弱网加载 | 不适用 | 本地应用；大页有 512 页/字节 cap 边界 |
| 123 | 空/加载/错误态 | 部分适用 | 四段式错误映射在；逐屏空/加载态验收未完成 |
| 124 | 可操作错误信息 | 适用 | 固定错误码+messageKey+受限定位参数，不回传原始异常（PRD 8.6） |
| 125 | 表单保留输入 | 部分适用 | draft.save generation CAS+表单状态在；逐字段失败保留未逐屏验 |
| 126 | 邮件渲染 | 不适用 | 不发邮件 |
| 127 | 通知可关闭 | 不适用 | 无通知系统 |
| 128 | undo | 部分适用 | 定义级 Undo/Undo-of-Undo/owned restart 已验；剩余家族 HOLD |
| 129 | 键盘导航/读屏 | 部分适用 | 同 97 |
| 130 | 翻译/本地化 | 部分适用 | 语言子标签 canonical 测试在；UI 本地化框架不存在（当前单语） |
| 131 | 后退按钮 | 部分适用 | 桌面导航语义不同；SPA 返回行为未见专项验收 |
| 132 | 人类可读代码 | 适用 | 严格 lint+约束注释+清晰命名（本轮样例确认） |
| 133 | 每次变更 code review | 适用 | 指定双模型独立审查+多轮处置实质覆盖 base→head 150 路径 |
| 134 | 分支策略 | 适用 | worktree+feature 分支+PR 门禁+冻结流程（AGENTS §5） |
| 135 | 月度依赖升级 | 部分适用 | dependabot 配置在（root npm/actions）；升级节奏未建立（项目早期） |
| 136 | 框架安全补丁升级 | 部分适用 | Electron 44.9.0/rdflib 7.6.0 fork 固定；升级流程未建立（Top10 #7） |
| 137 | 删除死代码 | 部分适用 | 本轮未见 AI 残留死代码；旧 wheel fr201.1/.2 已从 vendor 删除 |
| 138 | 拆分大文件 | 部分适用 | 模块化清晰；最大新文件为测试 1112 行；未见失控追加模式 |
| 139 | 架构决策记录 | 适用 | ADR-0001/0002/0003+M0 计划+状态/version-map 体系完整 |
| 140 | README 快速上手 | 部分适用 | README/贡献/架构说明在；"新工程师 1 小时"未实测 |
| 141 | 交接文档 | 部分适用 | AGENTS/状态/交接体系完善；人类继承人接手仍 HOLD |
| 142 | 运维面板 | 不适用 | 无运维面 |
| 143 | 客服工具 | 不适用 | 无客服面 |
| 144 | 客户 changelog | 部分适用 | 内部状态/round 记录完整；无客户面 |
| 145 | 条款/隐私匹配代码 | 部分适用 | PRD 隐私原则与设计一致；正式 ToS/隐私文本未发布 |
| 146 | 账户/域名/repo 归属 | 无法确认 | 组织/法务归属未核（LEGAL146 HOLD），代码审查无法认证 |
| 147 | bus factor>1 | 部分适用 | 多模型/多会话流程在但均 AI；人类 bus factor=1 风险真实（HUMAN147） |
| 148 | 高工逐行读 AI 代码 | 部分适用 | 指定双独立模型覆盖；人类工程师逐行阅读不存在（HOLD 语义） |
| 149 | 后端先设计数据模型 | 适用 | schema 设计化+版本向量+ADR（本人在 storage.py/mainline.py 确认） |
| 150 | 解释 AI 修一造二 | 部分适用 | 全量回归+失败保留对抗此风险；无人类 senior 复核 |
| 151 | DevOps 工程师 | 部分适用 | CI/打包脚本在；无生产服务器面 |
| 152 | 3am on-call | 不适用 | 无生产服务 |
| 153 | 安全补丁响应 | 部分适用 | 版本固定+扫描缺口同 136/39 |
| 154 | 审计陪同 | 不适用 | 无合规审计面 |
| 155 | QA 验证 AI 测试声明 | 适用 | 独立审查+O092–O094 实测复核链即该角色（ROOT 收件验证） |
| 156 | 活库迁移不丢行 | 部分适用 | 迁移故障矩阵+备份门禁（合成）已测；真实大规模活库未测（Q5） |
| 157 | tech lead 说不 | 部分适用 | 范围冻结+清单扩建禁止+PRD 非目标在；由总控流程承担 |
| 158 | architect 规模化 | 部分适用 | 预算/限额边界显式；规模化未验证（Q5） |
| 159 | senior 调试 | 部分适用 | 诊断基础设施（ledger/首败/报告）持续建设；AI 边界由独立审查制衡 |
| 160 | 一年后记得为什么 | 适用 | ADR/状态/version-map/PROVENANCE 是记忆机制；人类接手仍 HOLD |

统计：适用 23（1,22,23,30,31,36,40,41,46,47,69,73,90,95,115,121,124,132,133,134,139,149,155,160 去重后为 23 行）、部分适用 66、不适用 70、无法确认 1（#146），合计 160。

## 7. 历史 175 位置逐 stableID 处置（本人按四类：已闭/保留/未知/不采；"已闭"均指信息/流程状态闭合，不新增产品或发布 HOLD 关闭）

分组说明：current31=R08 当轮 19+12、authoritative78=R04–R07 权威位、R09New19PlusOBS、extra13=R06 MM 追加、R10ZTop9、R10MMTop10PlusT11T12、zNew3=R11 Z 新增、miniNew9=R11 MM 新增（含 S01→R11-T06 别名不增位；Z Top9 为别名映射不增位）。R12 的 111 行通用当前依据与各行原 owner/事件窗口继续作为历史承接；本表给 R13 当前判定。

**current31（31 项）**

| ID | 判定 | R13 当前依据 |
|---|---|---|
| Z08-01 | 保留 | 有界事实采纳；动作延期原窗口，本轮无新执行 |
| Z08-02 | 未知 | 退出码/后代 UNKNOWN 主题（Top10 #3），证据沿原窗口 |
| Z08-03 | 保留 | 同通用：观察采纳、延期 |
| Z08-04 | 保留 | 同上 |
| Z08-05 | 保留 | 同上 |
| Z08-06 | 保留 | 部分采纳；本地闭合资格维持，未闭部分延期 |
| Z08-07 | 保留 | 同通用 |
| Z08-08 | 保留 | 同上 |
| Z08-09 | 保留 | 同上 |
| Z08-10 | 保留 | 已证窄事实采纳，未穷尽推论不采 |
| Z08-11 | 保留 | 同通用 |
| Z08-TOP10-OLD79F | 未知 | 旧 79F 根因 UNKNOWN 不倒填（Top10 #2） |
| F01 | 已闭 | 本轮必要阅读/技术收件动作由本报告与 ROOT 收件履行；不关产品/CI 门 |
| F02 | 保留 | 同通用 |
| F03 | 保留 | 同上 |
| F04 | 不采 | 原强论断维持撤回，不复活 |
| F05 | 保留 | 登记缺口类；R13 状态追加由 owner 后续票履行，非产品闭合 |
| F06 | 保留 | 同通用 |
| F07 | 保留 | 同上 |
| F08 | 保留 | 部分采纳，HOLD 不关闭 |
| F09 | 保留 | 同通用 |
| F10 | 保留 | 同上 |
| F11 | 已闭 | 有界闭合/信息状态，仅继承原证据 |
| F12 | 保留 | 同通用 |
| F13 | 保留 | 同上 |
| F14 | 保留 | 公开入口拒空已证；算术冗余维护沿原窗口 |
| F15 | 保留 | 同通用 |
| F16 | 保留 | 同上 |
| F17 | 保留 | 同上 |
| F18 | 保留 | 同上 |
| F19 | 保留 | 同上 |

**authoritative78（78 项）**

| ID | 判定 | 依据 | ID | 判定 | 依据 |
|---|---|---|---|---|---|
| Z F1 | 保留 | 通用承接 | R06 D7 | 保留 | 通用承接 |
| Z F2 | 保留 | 同上 | R06 D8 | 保留 | 同上 |
| Z F3 | 保留 | 同上 | R06 D9 | 已闭 | 有界闭合信息状态 |
| Z F4 | 已闭 | 有界闭合 | R06 D10 | 保留 | 通用承接 |
| Z F5 | 保留 | 通用承接 | R06 D11 | 保留 | 同上 |
| Z F6 | 保留 | 同上 | R06 D12 | 保留 | 同上 |
| Z F7 | 保留 | 同上 | R04 Z01 | 保留 | 同上 |
| Z F8 | 保留 | 部分采纳 | R04 Z02 | 不采 | 已撤回强论断；有效更正保留 |
| Z F9 | 已闭 | 有界闭合 | R04 Z03 | 保留 | 通用承接 |
| Z F10 | 已闭 | 有界闭合 | R04 Z04 | 保留 | 部分采纳 |
| MM R07-01 | 已闭 | 有界闭合 | R04 Z05 | 保留 | 通用承接 |
| MM R07-02 | 保留 | 通用承接 | R04 Z06 | 已闭 | 有界闭合 |
| MM R07-03 | 保留 | 同上 | R04 Z07 | 已闭 | 有界闭合 |
| MM R07-04 | 保留 | 登记缺口（同 F05 类） | R04 M01 | 已闭 | 有界闭合 |
| MM R07-05 | 保留 | 通用承接 | R04 M02 | 已闭 | 有界闭合 |
| MM R07-06 | 已闭 | 有界闭合 | R04 M03 | 保留 | 通用承接 |
| MM R07-07 | 已闭 | 有界闭合 | R04 M04 | 保留 | 同上 |
| MM R07-08 | 已闭 | 有界闭合 | R04 M05 | 保留 | 同上 |
| MM R07-09 | 已闭 | 有界闭合 | R04 M06 | 保留 | 部分采纳 |
| MM R07-10 | 已闭 | 有界闭合 | R04 M07 | 保留 | 通用承接 |
| MM R07-11 | 保留 | 通用承接 | R05 Z P1 | 保留 | 同上 |
| MM R07-12 | 保留 | 同上 | R05 Z P2 | 已闭 | 有界闭合 |
| MM R07-13 | 保留 | 同上 | R05 Z P3 | 保留 | 通用承接 |
| R06 Z P1 | 保留 | 同上 | R05 Z P4 | 保留 | 部分采纳 |
| R06 Z P2 | 保留 | 同上 | R05 Z P5 | 保留 | 通用承接 |
| R06 Z P3 | 保留 | 同上 | R05 Z P6 | 已闭 | 有界闭合 |
| R06 Z P4 | 保留 | 部分采纳 | R05 Z P7 | 已闭 | 有界闭合 |
| R06 Z P5 | 保留 | 通用承接 | R05 Z P8 | 保留 | 通用承接 |
| R06 Z P6 | 保留 | 同上 | R05 MM01 | 保留 | 同上 |
| R06 Z P7 | 已闭 | 有界闭合 | R05 MM02 | 已闭 | 有界闭合 |
| R06 Z P8 | 保留 | 通用承接 | R05 MM03 | 保留 | 通用承接 |
| R06 D1 | 保留 | 同上 | R05 MM04 | 保留 | 同上 |
| R06 D2 | 保留 | 同上 | R05 MM05 | 保留 | 同上 |
| R06 D3 | 保留 | 同上 | R05 MM06 | 保留 | 同上 |
| R06 D4 | 保留 | 部分采纳 | R05 MM07 | 保留 | 部分采纳 |
| R06 D5 | 保留 | 通用承接 | R05 MM08 | 保留 | 通用承接 |
| R06 D6 | 保留 | 同上 | R05 MM09 | 已闭 | 有界闭合 |
|  |  |  | R05 MM10 | 已闭 | 有界闭合 |
|  |  |  | R05 MM11 | 已闭 | 有界闭合 |
|  |  |  | R05 MM12 | 保留 | 通用承接 |
|  |  |  | R05 MM13 | 已闭 | 有界闭合 |

**R09New19PlusOBS（19 项）**：Z09-01 保留；Z09-02 未知（CI41/CI43 分列不合因）；Z09-03 未知（退出码主题）；Z09-04 保留；Z09-05 保留；Z09-06 保留；Z09-07 保留；Z09-08 保留；Z09-09 保留；Z09-10 保留；F-R09-01 保留；F-R09-02 未知（同 Z09-02）；F-R09-03 不采（强论断维持撤回，readiness 表征保留）；F-R09-04 保留；F-R09-05 保留；F-R09-06 保留；F-R09-07 保留；F-R09-08 已闭（显式映射 F05 后继归档窗口）；OBS-R09-10 保留。

**extra13（R06 MM，13 项）**：MM01 保留；MM02 已闭；MM03 保留；MM04 保留（登记缺口）；MM05 不采（已撤回）；MM06 保留；MM07 保留（部分采纳）；MM08 保留；MM09 已闭；MM10 已闭；MM11 已闭；MM12 保留；MM13 已闭。

**R10ZTop9（9 项，别名承 Z08-01/Z08-06/F02 等，不增位）**：R10-01 保留（部分采纳）；R10-02 未知（CI41 helper 主题独立）；R10-03 保留；R10-04 保留（部分采纳）；R10-05 保留；R10-06 保留（窄事实）；R10-07 保留；R10-08 保留；R10-09 不采（强推论撤回收窄）。

**R10MMTop10PlusT11T12（12 项）**：T01 保留；T02 保留；T03 保留；T04 保留；T05 不采（强推论不采，fixture scope=generated 事实保留）；T06 不采（同上）；T07 保留；T08 保留；T09 保留（窄事实）；T10 不采；T11 保留（生成来源 hash 事实采纳）；T12 不采（仅 3/9 断言推论不采；九 rules 参数化正反断言在位为反证）。

**zNew3（3 项）**：Z11-OBS-01 已闭（公开入口 schema 拒空更正确认；不对称论断不采）；Z11-R01 保留（有界失败事实+测量建议，不设余量门禁）；Z11-R02 未知（CI43 新形态单列 UNKNOWN）。

**miniNew9（9 项，S01→R11-T06 为别名不增位）**：R11-T01 保留（完整 CI 门禁延期 ROOT 精确票）；R11-T02 未知（Windows 失败附件未采）；R11-T03 保留（计时仅测量）；R11-T04 不采（无 ORDER BY 事实保留、错误推论不采）；R11-T05 保留（TS 宽类型维护）；R11-T06 已闭（页数不变量更正；固定 8 缺陷论断不采）；R11-F01 已闭（M0 计划版本化事实，非阻断）；R11-F02 已闭（exact2 限证）；R11-F03 已闭（extra13 独立索引事实）。

**别名不增位确认**：Z Top9（承 R10-01/R10-02/Z11-R01/Z08-06/R10-08/R10-07/R10-03/R10-04/R10-05）与 S01→R11-T06 均为映射引用，175 位置总数不变；未把 Top 序号充 stableID。

## 8. 17 观察处置（R12 newOpinions17 的 R13 承接）

| ID | 判定 | 当前依据 |
|---|---|---|
| Z12-N1 | 保留 | 身份门不枚举插件全局态；无产品路径改全局态的反例（本轮 storage.py memo 复核确认门仍在） |
| Z12-N2 | 已闭 | 有界取舍（16 环/饱和/4096）确认；requiredBytes 错误已撤回 |
| Z12-N3 | 已闭 | 满后保守 disable 行为正确（本人读 `_SnapshotIRIObjects` 确认） |
| Z12-N4 | 保留 | 非生产注入装配观察；本轮无变化 |
| MM12-N1 | 已闭 | dc6 状态归档缺口已由 R12 归档票+本轮 b02a39b4 候选冻结流程收口（原"非阻断"定性不变） |
| MM12-N2 | 已闭 | 撤回前提+两改码建议不采；TermInputError 边界本轮复核成立（Top10 #6） |
| MM12-N3 | 已闭 | 原串键/单次调用边界确认（memo 实现一致） |
| MM12-N4 | 已闭 | 安全降级与未测性能边界确认 |
| MM12-N5 | 已闭 | UNKNOWN/ACK 解释边界确认（与 O084 #receive 结论一致） |
| MM12-N6 | 未知 | 仅 error 捕获；真实平台失败捕获仍未证（CI 后继） |
| MM12-N7 | 已闭 | Windows 条件 step 窄事实；本轮 ci.yml 复核一致，不放宽全量门禁 |
| MM12-N8 | 保留 | NOTICE 物理路径复核留制造票（Top10 #7） |
| MM12-N9 | 已闭 | AGENTS overlay 唯一例外确认（本轮 status/diff 复核一致） |
| MM12-N10 | 保留 | 归档体积观察；不采本轮删减动作 |
| MM12-OBS-a | 保留 | 解析上下文假设无反例 |
| MM12-OBS-b | 已闭 | 共享局部池正确事实确认 |
| MM12-OBS-c | 已闭 | 新增脚本必要静态审查本轮已履行（run-engine-tests/reporting 关键段已读）；CI 仍需真实 node 资格 |

## 9. 后继 R01–R10 / D01–D05 / O088–O090 R 编号映射处置

- **O084 A/C/D**：A（产品埋点写权）暂不授予——本轮 12 路径只落地 W-Mac 守卫与 Windows transport ledger（A 的八路径经 O087–O090 有界实现），未新增产品埋点；C（CI 日志分析）保留只读窗口；D（engine CI 报告）已按 O086 固定针落地 ci.yml/runner/plugin（本人复核无 flag 时 mode1/mode2 原样）。映射：A→engine-ledger 五路径+tests 三文件；C→R11-T01/T02；D→`scripts/run-engine-tests.py`+`scripts/engine-test-reporting.py`+ci.yml 三行 env。
- **O085 两文件 W-Mac**：helper（ui-observation.ts）+unit——已接收（7 reason 断言+短路/调用次数），本轮复核测试名在位。映射→Z12-OBS-c/OBS5 类观察承接。
- **O086 严格验证**：ci.yml 8932B/runner 21362B/r6 fixture 固定针——本轮工作树与 O095 绑定 12 blob 一致（CANDIDATE-BINDING exact12CommitBlobs passed=True）。已闭（该子步骤）。
- **O088 R01–R10 → O089/O090**：R01（双标志 bool）、R02（尾 LF）、R03（短写字节完成量）、R04（计数饱和）、R06（1024B 精确关联）、R07（callback error+无回调生产上界）已于 O089 关闭；R05（字节 cap 临界账）、R08（stop 后未全 close 无 footer）、R09（真实 pending 上 wire 后注坏帧）、R10（closeError 引用相等/顺序/优先级）已由 O090 关闭。**D01–D05（writer 交付差）**：O089 记录已闭合。本人本轮静态复核上述实现与测试名全部在位（§5），判定：**全部已闭（有界子步骤，不等于 Windows 根因修复或完整 T02 验收）**。
- **O090 回交边界**：完整候选=四旧 WIP+八路径=当前 b02a39b4 的 12 路径增量+既有 135 路径累计；本报告即该完整候选的指定 ZCode 新 SID 独立审查；MiniMax 第二审由另一方承担（本方未读）。

## 10. 结论重申

本候选（base583→b02a39b4）在本轮只读独立审查下：**push 前源码技术阻断 0，判定 ConditionalPass（限定本地技术阶段）**。全部条件：§3 所列完整同交付三平台 CI 门禁+远端复核+精确 merge 票；全部独立 HOLD 保留且关闭数为 0；维护建议（手写 SHA 测试向量、rdflib 升级窗口、NOTICE 物理路径、本地加密评估）不构成门禁。本报告不授权 push/PR/CI/merge/T04 推进；原件与既有 raw 不可改写；owner 收本原稿及必要事实补正后一次汇总 ROOT。

（本报告不内嵌自身最终 bytes/hash。）

---

# 补读附录（R13 同 SID 续作：必要漏项补读、实际影响与当前判定）

本附录由同一 SID `f67a67e285d8e9a84fffd39e138e608e`（GLM-5.3／最高／完全访问）在同 base583c→b02a39b4/tree3284bc38 候选上按 ROOT 指令完成，属完成原 R13 范围内必要漏项，不是新任务/新轮；不预设 Pass，未读另一方本轮任何材料。以上全部原前缀、原表格与原判逐字保留；本附录只追加，不回写初判。全部补读为本人分批实读至 EOF/全部 hunk，未使用任何 agent 摘要；除只读 Git/文本/哈希外未运行任何仓库代码、测试、构建、探针或 SQL。

## A. 补读清单与实际核对结果

**1）两个新增实现全文**：`tests/e2e/ui-observation.ts`（198 行）——七理由守卫链（disconnected→aria-labelledby→head-ancestor→special-self→special-descendant→shadow-self→shadow-descendant）保持原谓词/顺序/短路，`tagName` 前置；Playwright 1.64.1 native BUTTON 禁用语义（fieldset/legend 豁免＋最近显式 aria true/false 穿 shadow host）；`committedReceiptOperation` 只认首段身份与唯一"当前已读版本"段；`updateObservationSlot` 4096 UTF-16/16384B 有界槽且声明"非权威终态"。与 O085 验证一致，无缺陷。`OwnershipConflictDetailView.ts`（105 行）——纯 createElement 展示组件，值全部经 React 文本节点渲染（转义由框架保证），aria-label/语义列表完整，无任何写入面。

**2）两个脚本全文**：`scripts/run-engine-tests.py`（529 行）——mode1 无 flag 时原样 `os.execv` 直跑 pytest（行为不变）；`CI_ENGINE_TEST_REPORT_SINGLE=1` 时独占 run 目录＋launch-manifest（mode/optIn/owner/pid/parentPid/argv/execArgv/cwd/HEAD/tree/两脚本 controlHashes），exec 前 git 身份失败即非零返回，execv 保证 manifest PID 即 pytest PID——满足 O084-D"exec 前 owner/PID/PPID/完整 cmd/HEAD/tree 针"要求。mode2：先 `--collect-only` 收集器，按 CI40 实测跨度种子的贪心双桶分片（种子自我声明非单测时长/提速承诺），workers 用 files.json 整文件指派；`account()` 对 events.jsonl 做完整状态机核对（session_start/session_finish 各恰一次且 exitstatus=0、每 node start/finish 各一次、setup→call→teardown 相序、call 仅在 setup passed 后、outcome 映射含 unsettled/teardown-skipped/xfail/xpass、跨片重复节点检测、与全量收集清单精确对账、缺失补 unsettled）；信号/子进程退出失败路径显式记入 errors 并使 exit 非零；POSIX 新会话组 SIGINT→SIGTERM→SIGKILL＋`groupStillPresent` 核对，Windows CTRL_BREAK_EVENT→taskkill /T /F 并诚实记 `descendants: UNKNOWN after launcher exit; no job handle`（与 Windows 后代 UNKNOWN HOLD 口径一致）。`scripts/engine-test-reporting.py`（125 行）——独占 `"x"` 打开 events.jsonl；session_start 带 pid/parentPid/owner；logstart/report（失败/跳过才带 longrepr）/logfinish/session_finish；collection.json（临时文件原子替换）含身份（rootpath/inipath+SHA/testpaths/pythonpath/addopts/解释器/pytest 版本/平台/utf8/三处编码）与 nodeid/file 清单；shard 收集与全量清单或身份不一致即 `UsageError`；过滤只整文件 deselect、保持原生顺序。两脚本无 SQL、无产品运行面。

**3）`tests/e2e/t02-fr200-fr201.spec.ts` 全文（2180 行）**：三例均经 `launchIsolatedDesktop(launchOptions(), { observeTransport: true })`（即 Windows ledger 的三个真实启动点）。helper 链为真实 UI 流：`commit()` 在点击确认前先断言完整 Diff 与预期逐项相等、未提交读取等于 before（revision/snapshotId 不变）、点击后轮询回执/待处理（`pollText` 4096 UTF-16 有界）、pending 显示 succeeded 时走真实"核对原操作"按钮、回执身份用 `committedReceiptOperation` 首段严格匹配、再经真实 `getOperation`/`getJob` bridge 调用断言 marker 完整形状（beforeSnapshotId/afterSnapshotId/planHash/jobId/operationSequence）与 job 形状（capability=changeset.commit/state=succeeded/input/confirmationRef/commitProgress mode atomic）、evidence 操作去重、mappingState 与墓碑集合不变、刷新按钮再读相等。四类 CRUD 矩阵使用独立撰写的 N3 预期（含编辑/复制时语句位置保持语义）；FR201 例 12 笔请求三元组（多值关系、plain/中文/typed-alias/integer/boolean/decimal/double/date/dateTime），`"typed string"^^<xsd:string>` 别名被拒且输入原样保留、无 Diff/确认钮；`rejectCallerObject` 覆盖约 30 个坏输入（未闭合引号 ASCII/中文/三引号、缺 datatype、相对/越界 Unicode datatype、数字首位语言子标签、非规范大小写 de-CH-1901、4301 位裸整数、三种坏 IPv6 authority、全角斜杠），每个都验证三个字段输入保留、错误文案精确、before/after Read 相等、活动项目身份、附件落盘，并对 subject/predicate 做字段隔离；保留身份冲突路径断言可见冲突面板（现有/传入记录 id/owner=null/sourceRow=null/S/P、预览基准修订），冲突后未保存修正输入不产生 Diff；关系删除被引用阻断显示精确 fact 引用。错误屏障：2s 诊断预算（179s 案限内留 250ms 持久化余量）、先 DOM 快照并先存原始附件、仅既有只读 bridge 查询且任一超时即停后续、`clip()` 按 UTF-8 续字节回退不撕裂多字节、有界打包（262144B/512·0.75 base64 前缀）、原错误最后重抛、诊断绝不覆盖原失败。第三例（数字子标签独立 cohort）自我声明 `fixtureIsolationIsNotCapacityRepair: true`，不关闭保留的 rev-24 失败。断言为完整预期集合/顺序，非数量断言；未发现缺陷。

**4）九个新增单测全文**（engine-ledger.test.ts 1112、engine-ledger-supervisor.test.ts 805、isolated-desktop.test.ts 525、ui-observation.test.ts 269、native-recovery-observer.test.ts 326、t02-manual-fact-id.test.ts 186、t02-manual-preview-lifetime.test.ts 596、t02-ownership-detail-view.test.ts 138、t02-ownership-detail.test.ts 843）与**八个修改单测全部变动 hunk**（native-driver、t01-business3-contract、t01-mainline-contract、t01-mainline-ipc-delivery、t01-mainline-project-service、t01-mainline-real-runtime、t02-mainline-consumer、t02-mainline-metadata）。关键实证：O090 R05/R06/R07 的控制体（字节 cap 临界账含 held flight/queue/真实 overflow 替代/精确 1025B footer 预留、恰 1024B 全关联记录＋超一字节对照、直接 callback error 与无回调生产上界）与 R08/R09/R10 控制体（新 session 建立后旧 child 迟到 close 保 generation、stop 后真 child 未 close 无 footer、真 held ping 上 wire 后注坏帧且错误身份/线上序数与无 ledger 完全相等、closeError 引用相等＋close→info→attach 顺序＋收集失败不掩盖原错）全部在位——即 O088–O090 的闭合不再仅凭处置文档，本人已读测试正文直接确认。supervisor 源序测试（pin→write 直线 <800 字符无 ledger、prepared 在窗前、settled 在 write 后）在位。`t01-business3-contract.test.ts` 新增段对手写 SHA-256 对 Node `createHash` 做 8 个长度（2/55/56/63/64/65/32767/32768，覆盖填充边界与分段上界）差分验证并含三个负例。`t02-manual-preview-lifetime.test.ts` 把真实 `OntologyMainlinePage.tsx` 转译后在 VM 内以仪器化 hooks 驱动，覆盖 13 种变更下拒绝迟到哈希、ABA/取代/分离附件/同步 discard 订阅者。`t01-mainline-real-runtime.test.ts` 新增例经真实 preload/命名 IPC/服务/stdio（真实引擎子进程、单会话保持、replies diagnostic 0/0/0、子进程 exit 0）打通四冲突家族＋large（40000 字符主体多页）。native-driver 测试重写为完整 inspector 协议仿真（映射等待不装 shim、wrongMapping/missingAPI 即败、whenReady 停滞入原 deadline、exit/close/error 取消、绝对截止重查、invalid-json/send-throw/unknown-state/helper-error）。

**5）七个新增 Python 测试全文**（test_mainline_manual_input_rejection.py 1034、test_mainline_postwrite_admission.py 860、test_mainline_read_work_budget.py 559、test_mainline_postwrite_rows_budget.py 395、test_mainline_postwrite_text_budget.py 320、test_mainline_language_input_rejection.py 326、test_storage_snapshot_iri_memo.py 380）与 `test_mainline_dispatch.py` 全部 523 行变动。关键实证：`TermInputError` 边界两侧都被钉住——确定输入拒绝（R02 词法、urlsplit 契约内坏值、语言子标签、4301 整数、fr201.3 vendored 类型）经真实 stdio 子进程读回并同宿主继续完整提交（exit 0 无强杀）；未分类失败（parser-value/exception/config/assertion/index、n3、urlsplit 非契约异常、`iri` 预检异常、vendored 内部 join/int/unicodeEscape 故障）一律 INTERNAL_ERROR＋hold＋后续 STORAGE_FAILURE，且库转储逐行不变、同文不归类（"Even identical text must not classify an exception by its message"）；vendored 版本被测试显式钉住 `7.6.0+ontolearn.fr201.3`。postwrite admission：终态余量三轴 ±1 边界、2742B 尾部证明、draft 增长拒读不丢、queued 提交三结局（commit-limit/cancel/fail）非 jobs 行集不变、双项目全局余量、前后台 scope 不可互借、after_commit 重入拒、清理失败保原异常与持有、同一 Store DTO 不能 bind、bootstrap 未决写者不可被后继当 clean（8 状态）、clean close 真实交接、后继不能夺队列/活动 job、真实 stdio 增长拒绝＋同宿主完整提交、真实 stdio bootstrap 对账把已接受 job 记 ENGINE_EXITED failed。rows/text 预算：真实 243 行五列有序组合与 56309 字节转义/多字节文本全文分页（512/64 页上限内），固定终材费恰一次、预付拒绝对原子、cursor 回吊撤销在终编码器前拒。iri memo：16 别名上限、容量第 17 值重解析不驱逐首 16、非 IRI 分支整次调用禁用、别名不跨调用/异常不外溢、子类回调/字典子类/容量超限走原路径、自定义 `_definition` 单参 hook 且整次禁用、literal 转换器变化不留旧命中、未知 parser/n3 失败绝不转成功。dispatch 新增：large 定位器（含 managed 40KB 源行）纯读且库转储不变（含无新 cursor 行）、错 documentHash→IDENTITY_CONFLICT、末段非全文权威、跨项目 NOT_FOUND、损坏 header/segment→STORAGE_FAILURE＋hold、段失败回滚全部诊断行、诊断写入不毒化已准入全量读、旧三字段 detail 不发明定位器（INVALID_STATE）、引用不跨真实后继会话（新会话须新 preview 才有新 ref）。

**6）contracts 闭包**：实测 `registry.json` SHA256=`5e097b7e6ef0aa04da913820dffd0fbba33458f3204125e519105d87f2566740`，与 binding-regressions.json 13 处更新值一致；registry 仅在 business3 两处方法清单增加 `project.ownership.detail`。schema.json 新增 ownershipDetail*（id/owner/sourceRow 字符串界 1–16777216、manifest totalBytes 2–16777216/segmentCount 1–512、segment ordinal≤511/rawByteLength 1–32768/base64≤43692 且严格 pattern、document 双 kind oneOf、header 含 origin 三 ID＋requestHash/fingerprint/manifest/segmentBlobRefs）、params/result_project.ownership.detail wire 定义及 request/response envelope const；这些界与渲染端 512 页循环、32768B 分段、Python `SEGMENT_BYTES` 精确对应。fixtures.json 新增 7 个命名 case（named ownership request/page、no null continuation、wire issuer forbidden、wrong ref、corrupted segment SHA、premature next——含正负例）。`packages/contracts/python/contract_v2.py` 新增 `ownership_detail_matches`：与 TS 镜像的完整关联校验（projectId/detailRef/startOrdinal/segmentCount/页大小/nextOrdinal/complete/ordinal/byteOffset/rawByteLength＋base64 validate=True＋hashlib SHA-256），并接入 `matches_business3_response` 的 project.ownership.detail 分支（错误响应只需 engineSessionId 相等）。

**范围外自愿补读**（同属 150 路径产品面、本轮清单未列）：`tests/e2e/native-recovery.cjs` 与 `tests/e2e/native-driver.ts` 变动 hunk——被动失败观察（16 记录/4096B/saturated UNKNOWN、每码计数饱和、读失败不减量）与 helper 重写（绝对截止同步、映射等待不装 shim、exit/close/error 即取消、stdio 排空受原 deadline 约束、迟就绪不触发后续 helper），与 O059/O060/O062 及 native-driver/native-recovery-observer 两测试文件所述控制一致。

## B. 机械重数勘误（160 表）

原表 160 行每行单一标签、无缺号无冲突，逐字保留。首稿表下统计句自报"适用 23／部分适用 66／不适用 70／无法确认 1"为**汇总算术错误**（所列"适用"集合本身即含 24 项却写作 23 行）。按实际标签机械重数（脚本核对）：**适用 24／部分适用 64／不适用 71／无法确认 1，合计 160**。适用=1,22,23,30,31,36,40,41,46,47,69,73,90,95,115,121,124,132,133,134,139,149,155,160；无法确认=146；其余见原表。不回改原句、不凑首稿自报数字，以本节为准。

## C. 补读对原判的影响

- **总判定维持不变：ConditionalPass（限定本地技术阶段），当前 push 前源码阻断仍为 0。** 约 1.2 万行补读正文未发现任何新的产品缺陷、需要运行证实的反例或与 PRD/ADR/M0 计划的冲突；相反，原输入中"当前12叶只是最近增量"的判断进一步被证实——12 路径之外累计实现/测试链经本人正文级阅读后成立。
- **N-R13-01（手写 SHA-256）修正**：首稿建议"增加 NIST 测试向量锚定"已**实质满足**——`t01-business3-contract.test.ts` 对 Node `createHash` 的 8 长度差分测试（覆盖填充边界 55/56/63/64/65 与分段上界 32767/32768）＋三个负例＋Python `ownership_detail_matches` 独立实现交叉＋fixtures 负例已锚定正确性。剩余建议收窄为"可选：追加官方 NIST 标准向量"（纯可选项）；Top10 第 8 项严重性由"低-中"降为"低"。原判文字保留，以本节修正为准。
- **证据补强（不改任何行标签）**：#41 XSS 获得 SSR hostile 转义直接测试证据（8 处转义、无 script/img/a/href/src/onerror）；#90/#95 断言质量经全部测试正文直接确认（完整预期集合/顺序，非数量断言）；#26 56309 字节转义/多字节 UTF-8 分页实测用例在位（RTL 仍无专项，维持部分适用）；#148/#155 审查-实测复核链（真实 stdio/真实 preload-IPC 集成）正文级确认。
- **新观察（均非缺陷，编号续 N-R13-05 起）**：N-R13-05 run-engine-tests.py 信号中断 worker 启动循环时经 `len(workers)!=len(groups)`＋覆盖对账显式失败，路径正确；N-R13-06 e2e `clip()` 按 UTF-8 续字节回退避免在代理对中间截断，边界处理正确；N-R13-07 isolated-desktop 收集器 cap+1 检测字节边界（恰 524288 收集、+1 即 oversized）与单测精确对应。均为正确性确认记录，不构成行动项。
- **原 Top10、§3 条件与 HOLD 集合不变**：三平台完整 CI/远端/merge 门、engine 与 Windows 后代自然退出 UNKNOWN、签名公证/法律/bus-factor、容量/坏库、unknown parser 边界、rdflib fork 供应链（NOTICE 物理路径留制造票）、剩余 Undo/四下游等全部保留；本轮补读未产生任何缩小或扩大这些边界的证据。

## D. 补读后仍未读披露

fixtures.json 除 7 个新 case 名与其被测引用外的完整新增正文（350 行 diff 细目）；schema.json 除 ownershipDetail*/wire envelope 外的其余新增定义只抽样未逐条；O092/O093/O094 authority 细目 JSON、vendor wheel 二进制成员、双方 R04–R12 历史原稿全文（经 round-12 effective-index 结构化承接）维持首稿披露；另一方 minimax 本轮目录按票未读。以上不影响本附录的阻断结论。本次为同 SID 原审查续作，未 push/CI/merge，未改任何受审源，不新增产品运行。（本附录同样不内嵌自身最终 bytes/hash。）

---

# 补读附录二（R13 同 SID 续作：contracts 剩余正文与 F-R09-09 单一位置补齐）

同 SID `f67a67e285d8e9a84fffd39e138e608e`（GLM-5.3／最高／完全访问），同 base583c→b02a39b4/tree3284bc38。以上 61421B 前缀（含首稿与附录一）逐字保留；本附录只追加。仍为纯只读（文本/JSON/哈希/只读 Git），未运行产品、依赖模块、tests/collection/probes、SQL、GUI/RPC，未改任何受审内容。

## A2-1. 实际补读的剩余正文

**fixtures.json（base→head 全部变动，951 行差异）**：逐行读毕并机械分类，全部变动仅两类——
1. **7 个新增 ownership fixture case**（此前仅读名称，现已逐字段读全）：请求侧 `named ownership request`（valid：documentHash=null＋startOrdinal=0）、`ownership no null continuation`（invalid：startOrdinal=1 配 documentHash=null，精确对应 schema params oneOf 反例）、`ownership wire issuer forbidden`（invalid：额外 `ownerId` 字段，对应 additionalProperties:false 与"wire 不能携带签发者身份"）；响应侧 `named ownership page`（valid：`dataBase64:"e30="` 即 2 字节 `{}`，manifest totalBytes=2/segmentCount=1/nextOrdinal=null/complete=true）、`ownership wrong ref`（invalid：result.detailRef 与请求不一致）、`ownership corrupted segment SHA`（invalid：segment sha256 全 f）、`ownership premature next`（invalid：complete=true 却 nextOrdinal=1）。本人独立重算 `sha256(b"{}")=44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`，与 fixture 中 documentHash/segment sha256 一致。
2. **registryHash 传导**：旧 `058ed1be…`→新 `5e097b7e…` 在 business3 cases、hello outcome、startup 诊断样例及 raw golden wire 段（wireUtf8 与 wireBase64 成对，含 chunk 内以 \uXXXX 转义出现哈希的分裂帧样例）的全量成对替换；与已实测的 registry.json SHA256 完全一致，无第三种值、无孤立替换。

**schema.json（base→head 全部 550 行差异＝3 个 hunk）**：逐行读毕。hunk1（@6874）：request envelope 新增 project.ownership.detail oneOf 分支（protocolVersion const 3、params 引用、additionalProperties:false）。hunk2（@8695）：response envelope 新增 ok:true（result_project.ownership.detail）与 ok:false（error3）两分支。hunk3（@11446，+442）：五个新 `$defs` 完整定义——`ownershipDetailDocument`（oneOf：manual 型 existing/incoming 各含 id/owner/sourceRow/slot；single-declaration 型含 declaration（layer const "ontology"）＋slot＋existing 恰 2 项 minItems=maxItems=2；全部字段 1–16777216 字符界）、`ownershipDetailManifest`（totalBytes 2–16777216、segmentCount 1–512）、`ownershipDetailHeader`（origin 三 ID、requestHash/fingerprint、segmentBlobRefs 1–512）、`params_project.ownership.detail`（oneOf：首页 documentHash const null＋startOrdinal const 0 vs 续页 documentHash hash＋startOrdinal 1–511；pageSize 1–64）、`result_project.ownership.detail`（startOrdinal 0–511、segments 1–64 引 changeSetSegment、nextOrdinal 1–511|null、complete bool；additionalProperties:false）。此前"抽样"阅读至此补全为全量。

交叉一致性确认：params oneOf 两态＝fixtures 反例与渲染端 `mainline-ownership.ts` 首页/续页调用形状；pageSize≤64/segments≤64＝渲染端 pageSize:64；ordinal/segmentCount ≤511/512＝渲染端 512 页循环上限；error3＝t01-business3-contract 中 NOT_FOUND ownership 错误样例；全部 additionalProperties:false 与 AGENTS §7 严格边界一致。

## A2-2. 新发现与对原判的影响

**无新发现，无缺陷。** 两文件补读仅把附录一的"抽样/名称级"阅读补成全量；所有边界、正负例与哈希传导经交叉核对自洽，且正例分段哈希经本人独立重算吻合。**原判不变：ConditionalPass（限定本地技术阶段），push 前源码阻断仍为 0**；Top10、§3 条件、HOLD 集合与附录一 C 节修正均维持。

## A2-3. F-R09-09 当前处置（单一历史位置补齐）

首稿 §7 R09New19PlusOBS 组枚举为 19 项且组名标注"（19 项）"，经与 canonical 索引机械比对（归一化短名后），175 位置中唯一真实遗漏即本条，且该组 canonical 共 20 位（19 新＋1 OBS）；extra13（MM01–13）、R10MM（T01–T12）短名齐全、17 观察齐全，无其他缺漏。现补：

- **F-R09-09：保留（maintain）。** 主题："每次 CI 完整回单接收要求不变"（双作者原状态均为保留）。原 owner/事件窗口：**ROOT；每次 CI 完整回单接收**（R12 索引 stable163/R09New19PlusOBS 行，Z 原 R10 承接、MM 原 563 行，limitRefs=BASE）。本候选当前依据：b02a39b4 未 push、无新 CI、本人未取得任何新远端完整回单——与该位置建立时点（dc6 未 push、O081 本地 check 自然 0 不冒 CI 回单）同构；最低理由：**"每次 CI 完整回单接收"未执行**。本报告 §2 Top10 第 1 项与 §3 后继 CI 门即同一主题的门禁表达，不重复编号、不并入 Top、不代 owner 定性；该位置在未来每次真实 CI 完整回单接收时仍归 ROOT 处置。

## A2-4. 当前结论与仍真实存在的阅读缺口

结论不变：**ConditionalPass（限定本地技术阶段），当前 push 前源码技术阻断 0**；全部后继 CI/merge 门、独立 HOLD 与维护建议按首稿 §2/§3 与附录一 C 节原样保留。至此，附录一 D 节所列两项"上次原 completion 第 6 项必要漏项"（fixtures.json 全部变动正文、schema.json 其余新增 hunk）已补齐清零。仍真实存在的阅读缺口（与附录一 D 节一致，无新增）：O092/O093/O094 authority 细目 JSON、vendor rdflib wheel 二进制成员、R04–R12 双方历史原稿全文（经 round-12 effective-index 结构化承接）、另一方 minimax 本轮目录（按票未读）；以上不影响本附录结论。本次仍为同 SID 原审查续作，非新轮/新审查，未 push/CI/merge，不新增产品运行。（本附录不内嵌自身最终 bytes/hash。）
