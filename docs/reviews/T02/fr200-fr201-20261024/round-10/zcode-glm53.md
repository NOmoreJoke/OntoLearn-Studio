# T02 FR-200／FR-201 R10 全新整候选独立工程审查报告

- 本方：ZCode（GLM-5.3／最高思考等级／完全访问），全新任务，不续用 R04–R09 任何结论，独立形成判断。
- 受审候选：base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `67b7bcbd2d911b4a6898d837dbf20688d793e844`（tree `78a6b5d5ba4ff4e8e408e8f7da95c5c719be3996`，唯一 parent `b0c0e8d37954a3b8c2563b6068d6ca3d151a8dd1`），branch `feature/weekly-t02-fr200-fr201`。
- 本报告只读审查，未运行任何 check/vitest/pytest/build/package/formatter/HMR/GUI/SQL/探针，未改动任何源码/测试/依赖/配置/文档，未 git add/commit/push/切分支。运行事实全部来自标明身份的既有原件（O059–O069 及 rounds 归档），本人只做文本/JSON/hash/Git 只读比对。

---

## 0. 完整输入回执与身份核验（全部实测通过）

| 层 | 声明 | 本人实测 |
| --- | --- | --- |
| 外层原件 | 26579B、SHA256 `750cebb5…b8747`、222 个 LF | 粘贴附件 `pasted-text-20261027-041241-c148fb1d.txt` 实测 size=26579、SHA256 `750cebb5714380c482526300fd5b74632ade9b905164c3f7092169b2380b8747`、`tr -cd '\n' | wc -c` = 222 |
| 外层第二来源 | 与仓外完整输入一致 | 与 `outputs/20261027_t02_67b7_fresh_r10_070/zcode-complete-input.md` 逐字节 `cmp` IDENTICAL |
| 内嵌原160清单 | 11255B、SHA256 `1ca23def…f709c`、末字节非 LF | 取第 51–220 行、剥离 sed 补入的恰好 1 个尾 LF 后实测 bytes=11255、SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`；`od -c` 实核尾部为 `…someone who was there)` + `\n\n` + EOF 标记，末字节 `)` 非 LF，两个分隔 LF 未计入原清单 |
| Git 身份 | cwd/branch/base/head/tree/parent | shell pwd 实际即受审 worktree；HEAD=67b7bcbd、tree=78a6b5d5、`rev-list --parents -n1` 唯一 parent=b0c0e8d3、branch=feature/weekly-t02-fr200-fr201、base 为 HEAD 祖先 |
| 规模 | 40 提交、117 差异路径、1396 tracked | `rev-list --count` =40；`diff --name-only base head | wc -l` =117；`ls-files | wc -l` =1396 |
| 工作树脏项 | 仅既有保护项 | `git status --porcelain` 仅 `M AGENTS.md` + 未跟踪 round-01/02/03 目录，与声明一致 |

原清单 160 项嵌入完整性：第 60–206 行 147 项 + 第 208–220 行 13 项 = 160 项，第 207 行为过渡句不计项；两层边界分别核验，未把分隔 LF 算入原清单。回执结论：**输入原件与身份核验全部通过，按真实候选继续审查**。

补充事实核验（本人实测，非运行）：`git ls-remote origin` 只读核得 develop=`583c05c…`、feature=`b0c0e8d3…`，即 **67b7 未 push、无新 CI**，与输入及 O069 COMPLETION 声明一致。

---

## 1. 审查范围与真实覆盖声明

### 1.1 本人全文亲读（新增文件全文 / 修改文件完整累计差异）

- **67b7 最终提交四路径全文 diff**（本人 `git show 67b7bcbd` 逐行读，且 O069 `staged.diff` 与本人生成之 b0→67b7 diff `cmp` 逐字节 IDENTICAL）：`tests/e2e/mainline-consumer-first-ack-loss.spec.ts`、`tests/e2e/t02-fr200-fr201.spec.ts`、`tests/e2e/ui-observation.ts`（新）、`tests/unit/ui-observation.test.ts`（新）；四文件当前字节 SHA256 与 O069 两份独核所 pin 值逐一相同（`132c6b04…/3e69c4d9…/4c271fcc…/6dc201ba…`）。
- **主进程/preload 累计 diff 全文**：`desktop-ipc.ts`(+3)、`engine.ts`(±6)、`project-mainline-service.ts`(+24)、`preload/index.ts`(+1)。
- **renderer 层累计 diff 全文**：`OntologyMainlinePage.tsx`(±89)、`OntologyPage.tsx`(1 行)、`mainline-api.ts`(±9)、`mainline-facts.ts`(±50)、`mainline-session.ts`(±88)、新增 `mainline-ownership.ts`(78 行全文)、新增 `OwnershipConflictDetailView.ts`(105 行全文)。
- **契约层**：`packages/contracts/src/index.ts` 新增段全文（含 `reassembleOwnershipDetail` 逐行）、`src/v2.ts` 新增段全文（含手写 `ownershipSha256` 与 `matchesOwnershipDetail`）、`python/contract_v2.py` 新增 49 行全文、`registry.json` 全部差异；`schema.json` 中 ownership 相关 `$defs`（params/result/manifest/header/document 的边界：totalBytes≤16MiB、segmentCount≤512、pageSize≤64、startOrdinal≤511）逐一读出；`binding-regressions.json` 差异确认为 registryHash 全量一致更新。
- **引擎 Python**：`storage.py`(±114)、`project/domain_changesets.py`(±36)、`rdf_snapshot.py`(±32)、`coordinator.py`(±23)、`project/query_presentation.py`(±21)、`pyproject.toml` 累计 diff 全文；`project/mainline.py` 的 T02 全部增量 hunk（+417：_WriteAdmission/_WriteScope/_Budget/_MainlineReader/_OwnershipProof/ownership_proof/begin reserve/绑定期等，含 46–303、415–540、618–735 相关段亲读）；`job_store.py` 增量 hunk（+406：_transaction 写准入包裹、_application ownership_proof 分支、_persist_ownership_detail、_ownership_header/_ownership_segment、ownership_detail_page、三处 mark_controlled）亲读；`project_host.py` 增量（MaterialProfile/material_profile 抽取 + admit_terminal_growth）亲读。
- **vendor/配置**：`notation3-input-types.patch` 前 80 行（类型化输入拒绝错误 + 整数位限守卫）；`PROVENANCE.json` 键结构与状态；`licenses/NOTICE`、根 `package.json`、根 `pyproject.toml`、`uv.lock`、引擎 `pyproject.toml` 累计 diff 全文；`.github/workflows/ci.yml` 累计 diff 全文（JSON reporter/PLAYWRIGHT_JSON_OUTPUT_FILE、CI_ENGINE_TEST_SHARDS=2、Windows first-failure diagnostic `--maxfail=1 --full-trace`、artifact always 上传）。
- **治理文档**：worktree AGENTS.md（含 2026-10-22 桌面政策、2026-10-21 权限节）；PRD FR-200/FR-201 条款正文与附录 A–G 全文；ADR-0001 全文、ADR-0002 全文、ADR-0003 全文；`docs/m0-checklist.md` 全文；`docs/reviews/T02/status.md` 全文；round-09 `disposition.md` 全文（31/78/额外13/R09 Top 的稳定 ID 全部取得）、`version-map.json`/`artifact-manifest.json` 清单结构；M0 更新计划全文（见 1.4 路径失效说明）。

### 1.2 既有证据原件核对（pin 校验 + 内容阅读，未复跑）

- O069：`COMPLETION.json`（6941B/`6b9f8a52…` 实测相同）、`staged.diff`（36240B/`4716d937…` 实测相同且与 b0→67b7 diff 逐字节相同）、`FINAL-MANIFEST.json`（14072B/`711993fd…` 实测相同；70 针条目数本人用脚本复数为 70）；`INDEPENDENT-PRE-REGRESSION-REVIEW.json`（`da1cbfac…` 相同，含 IR069-01/02/03 三项初版阻断及修正记录）与 `INDEPENDENT-CANDIDATE-BINDING.json`（`fdb98ed2…` 相同，四路径五方一致性、1392 未改源、native24 readback）全文阅读；`NATIVE24-QUALIFICATION.json`（`3c30612c…` 相同；verdict PASS_LOCAL_NATIVE24_BOUNDED、checks=89 本人复数且 false=0、21P+3 原 I04 skip、事务组 7/7/7/7/22/7=57、拒绝 42 INVALID+1 OWNERSHIP=43）。
- O059–O068 历史证据按 R09 归档描述与 round-09 disposition §7 作为历史事实引用（标注身份，不继承判断）；CI41/CI42、b0 rerun 等远端事实以 O059/O067/O068 原件 + 本人对 ci.yml/driver 源码的只读核对为限。
- 一处披露性差异（信息级，非篡改）：O069 `COMPLETION.json` 内 `qualityRetryO068.handoff` 针为 1803B/`2f8fbe97…`，当前磁盘 `HANDOFF.json` 实测 1530B/`6f8b3a00…`；`FINAL-MANIFEST.json` scope 已明示 "self/laterHANDOFF/ROOTsendreceipt excluded"（HANDOFF 与 ROOT-SEND-RECEIPT 均在 70 针冻结范围外、写于封冻之后），属已披露的排除边界，建议 owner 留档知悉。

### 1.3 子代理 breadth sweep + 本人逐项复核

体量过大（约 9,000+ 行测试体）的 21 个测试/脚本文件由只读 Explore 子代理做可疑模式清点（A skip/弱断言、B 断言弱化、C 凭据、D 共享 oracle、E env/网络/外写、F 分片结算、G repack 行为），其全部结论中本人另行逐处复核了五项载重发现（run-engine-tests.py:340-365、test_mainline_read_work_budget.py:31-45、t02 spec canonical 副本 116-132、自指断言 314-331、两处 env 重定向写），原文亲读属实；其余结论（各文件 A 项为 0、无凭据、无网络、repack 无下载/无执行）与本人此前的抽样和 grep 一致。子代理原文全文在任务档案中，本报告仅采信经本人复核或与本人独立观察一致的条目。

### 1.4 真正未覆盖 / 读取受限（如实披露）

- 二进制 wheel（fr201.1/2/3、upstream）仅核存在、尺寸（fr201.3=2,379,774B 与 uv.lock 记载一致）与 PROVENANCE 三方哈希记录，未做 wheel 内部逐字节复算（只读审查下不可行，按既有 O036/O047 等运行证据有界接收）。
- `packages/contracts/v2/fixtures.json`（+446 行）与 `schema.json`（+525 行）为数据夹具/模式正文：ownership 相关 defs 亲读；其余新增夹具仅结构性抽查，不称全文亲读。
- `tests/e2e/t02-fr200-fr201.spec.ts` 全文 1942 行中，本人亲读其 67b7 增量全部 + 关键函数（read/diff/commit/拒绝矩阵段）+ 子代理全文清点；未逐行重读全部 1942 行。`native-driver.ts` 亲读累计 diff 前 200 行 + 子代理全文复核。
- `packages/engine/tests/test_mainline_dispatch.py` 等 6 个引擎测试（合计约 3,700 行）为子代理全文清点 + 本人抽样复核，不称本人全文亲读。
- R04–R08 各轮报告正文（zcode-glm53.md / minimax-m31flash.md 等）仅按 round-09 disposition 的索引与本人必要条目引用，未重读全部历史原稿。
- **失效引用路径**：AGENTS.md 指向的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 在本分支、base、develop、main、origin 均不存在（本人逐一 `cat-file -e` 核实），仅在主 checkout `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio/docs/architecture/` 下以**未跟踪文件**存在（主 checkout `git status` 显示 `??`）。本人已按真实同主题原件读取全文（35,812B，S1/S2/S3/C1/B1/U1 全文）并据此审查；该治理文档未入版本控制本身登记为观察 R10-09 的组成部分。ADR-0002 实际位于 `docs/iterations/I01/ADR-0002-storage.md`（AGENTS 映射正确），ADR-0003 位于 `docs/architecture/0003-resident-coordinator-and-jobs.md`，均已读。

---

## 2. 候选实现审查结论

### 2.1 67b7 相对 b0 的四路径修复（本轮唯一实现面 delta）

- delta 仅 4 个测试路径（631+/43-），产品、契约、CI、依赖、配置零改动——本人以 staged.diff 与 b0→67b7 diff 逐字节相同及最终提交 name-status 实证。
- `tests/e2e/ui-observation.ts`（新）：只观察"public getByRole exact"已选元素的同步 DOM 快照；不支持形态（shadow、script/style 内嵌、head、aria 覆盖原生 role/name）一律抛错 fail-closed；严格唯一（重复即抛）；nativeBUTTON enabled 按 Playwright 1.64.1 本地判据（disabled 属性 OR 最近 disabled FIELDSET 且首个直接 LEGEND 例外，再沿 parent/shadow-host 链取最近显式 aria-disabled true/false、小写不 trim）；文本归一化仅去 U+200B/U+00AD + trim + 折叠空白；`committedReceiptOperation` 只认**首段**操作 UUID + 精确提交版本 + 唯一"当前已读版本"+ pending=0；`updateObservationSlot` 单槽同步替换、诊断副本 16KiB 有界（超限走 base64 前缀截断副本），断言快照不截断。7 个纯合成 DOM 单测覆盖以上语义（含 4,301 字符原始值不归一、阴影 host 链、重复 fail-closed）。
- case7（ack-loss）：内层等待替换为一次非等待快照；按钮消失本身不再被当作成功（`reconciliationReady` 要求回执出现或 reconcile enabled===true）；原 5s/12 次上限、单提交、marker/getJob/getOperation/最终 Read 全链保留。
- FR201：同阶段 UI 观测批处理（`button.or(rejection)` 等），完整错误文案精确比对、raw input 值完整保留核验、`diff()` 要求唯一 `<pre>` 且确认段"全部 N 项…"精确出现一次；原首次 commit poll 与显式 reconcile 不改。
- 与 O069 叙述一致性：逐点核对无出入；IR069-01（遮蔽记录器）/02（重复匹配等待弱化）/03（后段搜索身份漂移）三项初版问题及修正均在独核原件中有记录，且本人验证修正后代码确实分别改为 recordObservation、立即抛 Duplicate、paragraphs[0] 严格身份。
- 本人对该 delta 的独立判断：**修复真实、方向正确、无断言弱化**；nativeBUTTON 判据与本地 Playwright 的等价性依赖"来源必须是 exact button role locator"这一前提（helper 已用拒绝 role/aria-label 覆盖来维持），属已注释声明的受限等价（见 R10-08）。

### 2.2 累计候选（base→head）核心实现

- **主进程/preload**：新增 `project.ownership.detail` 白名单方法，主进程引擎监督层维持方法白名单 + projectId 必须等于选中项目；`getOwnershipConflictDetailPage` 调用前后做 owner/selectionEpoch/projectId/engineSessionId 四重再校验（防跨选择发布）；preload 只增一个业务命名方法。符合"preload 仅业务命名、无通用 invoke"不变量。
- **renderer**：OWNERSHIP_CONFLICT 错误映射为完整中文指引（含"已输入内容保留"），冲突详情经 512 页有界、`requireCurrent()` 逐 await 再校验的分页读取；`newManualFactPlan` 改为 SHA-256(canonical JSON triple) 派生 ID 并拒绝 lone surrogate，`manualFactPlan` 的 AMBIGUOUS_FACT_SUPPORT 扩展覆盖 owner/source_row/managed_value/原值/编辑目标值重叠；`OntologySession.prepare` 全程 identity/stale/pending fence（`++this.#sequence` 使读请求本身使在途预览失效）；`OwnershipConflictDetailView` 纯 createElement 文本渲染，无 innerHTML，locator 仅 id/owner/sourceRow/slot（不含对象原值）。fact-ID 派生与 Python `Store.digest` 的跨语言一致性由 `t02-manual-fact-id.json`（声明并绑定真实 Python Store 生成的 golden vector，含 sourceStorageSha256 pin）+ 单测 spawn 真实 venv Python 交叉验证，不靠测试侧重实现哈希。
- **契约**：TS/Python 双端 `matchesOwnershipDetail` 数学一致（32768 段、ceil 计数、nextOrdinal/complete、逐段 SHA-256 + 严格 base64）；TS 侧 `reassembleOwnershipDetail` 在分配 `Uint8Array(totalBytes)` 前先 schema 验证声明总量（≤16MiB）并对输入做节点/深度/键数/字符串上限的结构化捕获（防预分配放大）；`ownershipSha256` 为手写同步 SHA-256（同步契约匹配器约束），实现经跨语言绑定夹具回归（binding-regressions 全量 registryHash 更新一致）。错误参数只传 detailRef 等白名单字段。
- **引擎**：storage 增 `ManualOwnershipConflict`/`SingleDeclarationConflict`（witness 只含定位符）；同计划内引入的单值声明与既有事实冲突时给出声明定位（同计划删除/覆盖不能再作为签发者）；`_check_slot` 对 manual incoming 分类 reservedIdentity/sameStatement/singleSlot；preview 前对 manual/edits 的 S/P 走 `iri()`、O 走 `term()` 且 `parsed.n3() != value` 拒绝非规范别名；rdf_snapshot 以 `TermInputError`（BadSyntax/Notation3InputError）与普通 ValueError 分流；`job_store` 写准入（_WriteAdmission）在 `_transaction` 边界做 before_commit 终检（material_profile + admit_terminal_growth）、未知异常保留 holding 不退款不重试；ownership detail 持久化为内容寻址分段 + fingerprint 去重 + 全量预算预留（estimate=6*chars+8192 ≤ MAX_DOCUMENT）；coordinator bootstrap 在 business3 + JobStore + 非 TEST_MODE + 无 ordinary/query_dispatch 时 `prepare_mainline_store`（native 恢复启动同步修复）；text_page 最终编码器预付（cb8c9b7a）消除搜索后预算不足窗口。
- **vendor/供应链**：rdflib 改为本地 vendored `7.6.0+ontolearn.fr201.3`（uv.sources 指向 wheel、uv.lock path 源 + 哈希），NOTICE 透明披露补丁内容与仓库引用；patch 本身为纯输入分类类型化（RelativeIRIBase/UnicodeCodePoint/UnterminatedString/MissingDatatype/InvalidLanguageTag/IntegerDigitLimit），未见行为外溢；repack 脚本无网络、无执行、三重 SHA pin、拒覆盖（子代理全文 + 本人结论一致）。**注意树内仍保留 fr201.1/fr201.2 两个历史 wheel**（见 R10-05）。
- **CI**：不改变 15/20 分钟预算；Windows first-failure diagnostic 明示"非验收"；artifact always 上传扩容。2b→240 与 240→67b7 均未再改 ci.yml（本人核）。
- **测试质量（子代理 sweep + 本人复核）**：21 文件无 skip/fixme/注释断言/凭据/网络；存在三类共享-oracle 式弱点（见 R10-06/R10-07），多数有独立 hashlib/golden 兜底缓解；`run-engine-tests.py` 分片结算 fail-closed（非零退出、JSON 解析失败、缺/多/重复节点均计错误），skip 不使 run 失败与 pytest 原生语义一致且计数可见（R10-04 详述）。

**结论：累计候选未发现新的源码安全或正确性缺陷；四路径 delta 是对真实观测弱点的正确修复，且无既有断言弱化。**

---

## 3. Top 风险（本人按当前重要性排序；实际 9 项，不足 10，不凑项）

| # | stableID | 严重性 | 触发与定位 | 依据/原件 | 影响 | 最小建议 | 是否本候选 push 前源码阻断 |
| --- | --- | --- | --- | --- |---|---|--- |
| 1 | R10-01（承 Z08-01/Z08-06/F02/R06 D1/R05 Z P1/R05 MM01/R06 MM01/Z F1） | 高（门禁） | 完整平台 CI 从未在本候选通过：CI41/CI42 Quality/Windows 失败或取消，67b7 未 push 无新 CI（本人 ls-remote 实测 remote feature=b0） | O059/O067/O068 原件；round-09 disposition §7 | merge 门禁未满足，不阻断 push 后重试 | ROOT 发精确 push/CI 票，按原 15/20 分钟与逐 node/原有据 skip/自然 0 标准接收 | 否（门禁，非源码缺陷） |
| 2 | R10-02（承 Z08-02/Z09-02/F-R09-02/03、OBS-R09） | 中（未证根因） | CI41 Quality C1 `native-recovery.cjs:12` `app.isPackaged` undefined TypeError；时序/解析/npm shim 具体原因 UNPROVEN | O059 原件；本人读 native-driver.ts:4-5 注释自认竞态未证 | 根因未知时 240/67b7 的 CI 结果不可倒填为已修复 | 真实 CI 归因窗口定因后处置；不为凑绿改预算 | 否（未证根因，HOLD） |
| 3 | R10-03（承 Z09-05/MM R07-13） | 低（维护） | `packages/contracts/src/index.ts:894-895` `OwnershipDetailArgs` 第二变体 `startOrdinal:number; pageSize:number` 宽于 schema（≤511/1-64） | 本人实测在位 | TS 类型不拦越界值，仅运行时 zod 拦截；双源漂移风险 | 契约 owner 下次整理时收敛为字面量区间类型 | 否 |
| 4 | R10-04（承 Z P6/R06 D5/R04 Z01/R05 MM08/F15 + F03 附带） | 低（未确认观察） | `storage.py:1151`（GROUP BY…LIMIT 1）与 `:1170`（…LIMIT 2）均无 ORDER BY，并列时"首个阻断行/前两条记录"不确定；另 `run-engine-tests.py:340-357` skip/xfailed/xpassed 不计失败（与 pytest 原生一致、计数可见） | 本人实测在位；子代理+本人双复核 | 冲突定位 witness 在极端并列时不可复现；CI 汇总不因新增 skip 变红（ROOT 接收标准已要求逐项列 skip） | T01 触及 witness 选取时加确定性排序；CI 维护票评估 skip 逐项对账强化 | 否 |
| 5 | R10-05（承 Z09-04/F09/MM R07-12） | 低（供应链卫生） | `vendor/rdflib/` 保留 fr201.1/fr201.2/fr201.3 三个 wheel + upstream，实际只用 fr201.3（uv.sources） | 本人核目录与 pyproject | 仓库体积与制品审计面增大；PROVENANCE 三方哈希一致但冗余件在树 | T11 merge 后受控清理历史 wheel，保留 PROVENANCE 记录 | 否 |
| 6 | R10-06（新，本人+子代理双复核） | 低（测试质量） | 共享 oracle：`test_mainline_read_work_budget.py:31-57` 用裸 SQL 重实现产品 read-admission 记账公式预测边界；两 e2e spec 各有一份手写 `canonical()` 副本（t02:116-132、ack-loss:46-62）作期望序列化；引擎多处用产品 `digest()` 现算期望 id | 本人亲读三处原文 | 公式/序列化与产品同源同错时边界测试双双"正确"（同错盲区） | 在这些位置补独立 hashlib/sha256 断言（language:156、text_budget:116、t02-manual-fact-id golden 已是好样板，逐步推广） | 否 |
| 7 | R10-07（新，本人复核） | 低（测试质量） | 自指断言：t02:316 `parametersHash: job.parametersHash`、:329 `planHash: marker.planHash`、ack-loss:468/472-478 与同源 accepted 快照自比较、stateVersion 仅 `>=` | 本人亲读 | 无独立期望值的字段回环恒真，掩盖字段错绑/漂移 | 为 planHash/parametersHash 补独立 digest 期望或交叉来源值 | 否 |
| 8 | R10-08（新） | 低（维护） | `ui-observation.ts` nativeBUTTON enabled 判据仅支持当前本地 light-DOM 形态（fail-closed），与 `native-driver.ts:244-269` 450×100ms 就绪轮询同为针对未证竞态的受限等价/同步补丁 | 本人读源码与注释 | Playwright/Electron 升级或形态变化时转为误报超时或需重证 | 升级/形态演进时重证判据；CI 归因时优先定因而非扩轮询 | 否 |
| 9 | R10-09（治理观察） | 低（流程） | AGENTS.md 引用的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 不在任何分支 Git 内，仅主 checkout 未跟踪文件（`??`） | 本人 `cat-file -e` 六 ref 核实 + 主 checkout status | 治理文档无版本控制/无哈希针，换机器或清理即丢失，评审依据不可复现 | 将 M0 计划正式提交入库或改指已入库等价文档并记哈希 | 否 |

（信息级另记：O069 COMPLETION 的 handoff 针与当前 HANDOFF.json 不一致属已披露排除边界，见 §1.2，不计风险项。）

**本候选（base→67b7）无 push 前源码技术阻断。** 以上 1–2 为既有门禁/未证根因，3–9 为维护/测试质量/治理项，均非阻断。

---

## 4. 原用户 160 项清单逐项判定（本人独立判定，依据为本轮亲读代码/配置/文档；判定档：适用／部分适用／不适用／无法确认；复合不拆档、只计一次）

统计：适用 26｜部分适用 48｜不适用 81｜无法确认 5｜合计 **160**。

| # | 判定 | 依据（要点） |
| --- | --- | --- |
| 1 | 适用 | `packages/contracts/v2/schema.json`+zod 双端 + SQLite 格式 v2 表结构均为先设计后实现（ADR-0002），非逐表即兴 |
| 2 | 不适用 | 单机本地产品，无账户/登录代码（grep renderer/main 无 login/password） |
| 3 | 不适用 | 无密码体系 |
| 4 | 不适用 | 无 MFA 面 |
| 5 | 部分适用 | stdio 会话 65,536 请求上限/会话关闭/重启隔离（ADR-0003）；无用户会话超时概念 |
| 6 | 不适用 | 无企业客户/SSO |
| 7 | 不适用 | 同上 |
| 8 | 不适用 | 无组织成员管理 |
| 9 | 部分适用 | 主进程方法白名单 + projectId 绑定 + `_OwnershipProof.check` 授权链（mainline.py:478-517）；无多用户角色 |
| 10 | 部分适用 | 单用户；跨项目/会话/owner 越权由 deniedOrdinary/proof.check/authorize 拦（engine.ts:1229-1245） |
| 11 | 不适用 | 无多租户；项目级隔离存在 |
| 12 | 不适用 | 无后台管理员 |
| 13 | 不适用 | 无登录接口 |
| 14 | 不适用 | 无登录锁定面 |
| 15 | 部分适用 | v0→v1→v2 前向迁移+失败回滚+未来格式拒绝打开（ADR-0002 迁移段）；无产品级反向迁移 |
| 16 | 部分适用 | 迁移取事务写锁后重读格式版本防双 opener；本地单进程锁窗口有界，未做并发负载测量 |
| 17 | 部分适用 | 表均含 (project,…) 复合主键；未见二级 CREATE INDEX；读路径靠行/字节准入限额（validation_rows/bytes）封顶，容量 Q5 未定 |
| 18 | 不适用 | 本地单连接 SQLite（BEGIN IMMEDIATE），无连接池需求 |
| 19 | 不适用 | 无服务器/夜间任务；本地 `backup(newPath)` 在线备份 API 存在但无调度 |
| 20 | 部分适用 | 备份/迁移恢复在 S1 spike 与引擎测试有真实验证（evidence/round-2/3、迁移 424P）；无产品级恢复演练 |
| 21 | 不适用 | 无服务端 WAL/PITR；对应机制为内容寻址快照+不可变历史 |
| 22 | 部分适用 | 受管事实删除留墓碑（ADR-0002 facts 表）；历史/已提交轮次不可改写 |
| 23 | 适用 | 服务端（引擎/主进程）二次校验：preview 的 iri/term/n3 规范拒绝、双端 strict schema |
| 24 | 部分适用 | 时间戳 ISO/safe-integer 存储；无跨时区调度功能；时区语义未展开（无 9am 提醒类需求） |
| 25 | 适用 | Unicode 输入全链（language tags、`泵站A`、text002 Unicode profile、lone surrogate 拒绝）有真实测试 |
| 26 | 部分适用 | UTF-8 显式编码贯穿（831813c6 六处 write_text、JSON 资源显式 UTF-8）；RTL 布局未支持未验 |
| 27 | 不适用 | 无货币金额概念 |
| 28 | 不适用 | 同上 |
| 29 | 部分适用 | definitions payload JSON+三类版本分层预留扩展；"第二客户"场景未验（Q5/Q6 未定） |
| 30 | 适用 | operationId/jobId 幂等：同 operation 重试返回原标记不重复写（ADR-0002；测试 singlecommit1/重试语义） |
| 31 | 适用 | preview→人工确认→提交链 + 单提交限制 + 幂等 marker（重复点击不产生第二事务，43 拒绝含重复面） |
| 32 | 部分适用 | 游标分页绑定项目/结果/范围并拒绝失配（diff-page/ownership-detail/text/rows page）；page 400 未测 |
| 33 | 不适用 | FR-203 Turtle 导出未实现（当前无导出功能） |
| 34 | 不适用 | FR-300 CSV/XLSX 导入未实现 |
| 35 | 部分适用 | collect_cache 仅回收可重建载荷、result_pins 固定、历史不可变；用户删除运行 FR-705 未实现 |
| 36 | 适用 | 无凭据入仓（无 token/key 字面量）；引擎不持密钥（S3 未建） |
| 37 | 不适用 | 尚无已发放密钥可轮换 |
| 38 | 部分适用 | uv.lock 固定+本地 wheel 哈希；树内 3 个冗余历史 wheel 待清（R10-05） |
| 39 | 部分适用 | `.github/dependabot.yml` 在树（本人核实存在）；扫描执行/SLA 未核（发布项） |
| 40 | 适用 | 输入经双端 strict schema + canonical term/iri；UI 渲染仅 createElement 文本节点 |
| 41 | 部分适用 | SQL 全参数化（唯一标识符拼接来自 sqlite_master 且引号转义）；XSS 由 CSP+无 innerHTML 覆盖；CSRF 不适用（无 HTTP） |
| 42 | 部分适用 | 无用户上传；内置示例资源读取 O_NOFOLLOW/FIFO 拒绝/大小上限/前后 fstat 一致（mainline.py `_example_resource_reader`） |
| 43 | 不适用 | 无 HTTP 服务；CSP connect-src 'none'（生产） |
| 44 | 部分适用 | CSP 唯一配置源 csp.ts（生产 meta/开发 header 两变体）；无其他 HTTP 头概念 |
| 45 | 部分适用 | 无网络传输；静态加密未实现（本地 SQLite 明文，safeStorage 属 S3 未建） |
| 46 | 适用 | Agent 只产草稿+白名单工具+不自动确认（架构不变量/附录 F）；Python 无凭据 |
| 47 | 部分适用 | operation/job 持久记录 who-did-what；跨边界仅错误码+白名单参数（无原值/堆栈/凭据）；运行时日志体系未成型 |
| 48 | 不适用 | 未做渗透测试；未发布（发布前安全审查属 HOLD） |
| 49 | 不适用 | 无企业买家问卷 |
| 50 | 不适用 | 未发布，无对外漏洞披露流程需求 |
| 51 | 部分适用 | 当前无生产凭据可泄露；设备被盗风险=本地数据暴露（无静态加密），发布前评估 |
| 52 | 不适用 | 无 SOC 2 承诺 |
| 53 | 不适用 | 不处理医疗记录 |
| 54 | 不适用 | 同上 |
| 55 | 部分适用 | 提交/运行/操作持久留痕（commits/commit_evidence/runs）；"查看"审计无（本地单用户） |
| 56 | 不适用 | 无支付，不触卡数据 |
| 57 | 不适用 | 无服务端个人数据；本地数据删除=文件级（未产品化） |
| 58 | 不适用 | 数据全本地 |
| 59 | 不适用 | 无组织访问体系 |
| 60 | 部分适用 | 开发/生产 CSP 同源生成（csp.ts 两变体）；无 staging/prod 部署差异面 |
| 61 | 部分适用 | CI workflow+构建/打包脚本全部版本化；无云基础设施 |
| 62 | 部分适用 | CI 按 check→e2e→package→verify 排序；但完整平台 CI 未绿（R10-01），门禁未过 |
| 63 | 不适用 | 无部署回滚面；存储层撤销依据已备（commit_evidence） |
| 64 | 不适用 | 无在线服务 |
| 65 | 不适用 | 无特性开关体系（进度由迭代门禁管理） |
| 66 | 不适用 | 本地单机 |
| 67 | 不适用 | 本地应用无 CDN |
| 68 | 不适用 | 无域名/证书（发布项） |
| 69 | 适用 | ExecutionJob/JobStore 队列、取消、心跳、崩溃对账（ADR-0003 已实施并有故障注入测试） |
| 70 | 部分适用 | 主进程三次有界只读恢复重建会话；写操作明确不自动重放（设计决定）；无通用退避框架 |
| 71 | 部分适用 | 失败任务终态+原因持久（run_terminal/failed），job.get 可重建；无 DLQ 概念 |
| 72 | 不适用 | 无 cron |
| 73 | 适用 | invalidation-v2.json 唯一规则源、staleReason、保守发布、缓存回收规则（S1 验收） |
| 74 | 不适用 | 无邮件 |
| 75 | 不适用 | 同上 |
| 76 | 部分适用 | 可回收载荷边界明确（collect_cache）；临时/派生数据全生命周期属 Q5 未定 |
| 77 | 不适用 | 无云成本/无模型调用（S3 未建） |
| 78 | 不适用 | 无正式 DR 计划文档（本地备份路径存在） |
| 79 | 不适用 | 单机产品 |
| 80 | 部分适用 | CI JSON 报告（report.json/engine-tests events.jsonl）可检索；运行时结构化日志有限 |
| 81 | 不适用 | 无错误跟踪服务 |
| 82 | 不适用 | 无在线服务可监控 |
| 83 | 不适用 | 同上 |
| 84 | 不适用 | 同上 |
| 85 | 部分适用 | operationId/jobId/revision/snapshot 绑定链路贯穿断言（trace 语义）；跨服务 tracing 不适用 |
| 86 | 不适用 | 无值班 |
| 87 | 部分适用 | AGENTS/ADR/验收文档链完整；运维 runbook 属发布前 |
| 88 | 部分适用 | T02 R01–R10 评审/处置/状态追加即复盘机制并落实改进 |
| 89 | 不适用 | 无在线状态页 |
| 90 | 适用 | 1912 TS 单测+3769 引擎测试，断言完整预期集合/顺序（非仅数量） |
| 91 | 不适用 | 无第三方网络 API 依赖（rdflib 为本地库且绑定回归覆盖） |
| 92 | 部分适用 | e2e 覆盖真实读写/恢复/拒绝流（六例+ack-loss+native24）；无商业变现流 |
| 93 | 不适用 | Q5 容量未定，无负载测试承诺（合成规模两档非负载） |
| 94 | 部分适用 | G-base/G-behavior 固定基线+Unicode 大文本；无生产数据（无生产环境） |
| 95 | 适用 | binding-regressions/黄金向量/每轮修复带回归（如 4299→4301 边界、UTF-8、canonical 拒绝） |
| 96 | 无法确认 | Q2 参考设备未定；参考 8GB/旧设备未测（HOLD） |
| 97 | 部分适用 | aria-label/role=alert/精确 getByRole 命名广泛使用；键盘可达（原生控件）；完整屏幕阅读器/合规未验（HOLD） |
| 98–105 | 不适用 | 无订阅/支付/发票/税/退款/计量/合同/收入报表（无商业化） |
| 106 | 不适用 | 无 webhooks |
| 107 | 不适用 | 同上 |
| 108 | 部分适用 | 内部 stdio 协议 v2 版本化+VERSION_INCOMPATIBLE（ADR-0003）；无对外 API |
| 109 | 不适用 | 无 API key 体系 |
| 110 | 部分适用 | 帧/队列/分页/内存/请求上限按能力有界（65,536 请求、MAX_REPLIES 16、16MiB 文档、页 262,144B） |
| 111 | 不适用 | 无第三方 API（依赖升级有引擎/依赖锁隔离规则） |
| 112 | 不适用 | 无 OAuth |
| 113 | 部分适用 | 隔离场景副本（E.2）+隔离 worker+测试 fixture；客户集成沙盒概念不适用 |
| 114 | 不适用 | 无模型调用/无 prompt 出口（S3 设计已预留外发检查与附录 F 规则） |
| 115 | 不适用 | 同上（无数据外发路径） |
| 116 | 不适用 | 无模型计费 |
| 117 | 不适用 | 无模型 |
| 118 | 不适用 | 同上（Q9 未定） |
| 119 | 不适用 | 同上 |
| 120 | 不适用 | 同上（S3 设计仅最小元数据日志） |
| 121 | 适用 | Agent 只草稿、人工显式确认 ChangeSet（附录 F/FR-804；确认按钮全链测试） |
| 122 | 不适用 | 本地应用与网络无关 |
| 123 | 适用 | role=alert 错误/reading/unavailable 冲突态/pending 回执等状态齐备并全量断言（含 67b7 完整状态快照） |
| 124 | 适用 | 四段式可操作中文错误（OWNERSHIP_CONFLICT 指引核对原记录/重新预览/输入保留） |
| 125 | 适用 | 拒绝后三个字段 raw 值完整保留并断言（含 4,301 字符不截断） |
| 126 | 不适用 | 无邮件 |
| 127 | 不适用 | 无通知系统 |
| 128 | 部分适用 | 存储层撤销依据完整（前后快照+edits 保 ID）；定义级 Undo/Undo-of-Undo/owned restart 子集已验（O056 第18例）；其余 Undo/ownership 家族 HOLD |
| 129 | 部分适用 | 原生表单控件键盘可达；屏幕阅读器支持未验 |
| 130 | 不适用 | zh-CN 单语产品（本地化框架未规划） |
| 131 | 不适用 | 桌面单窗口应用，导航/弹窗被禁（无历史栈） |
| 132 | 部分适用 | TS strict/Python ruff/注释解释约束；预算/准入类代码（mainline.py 写准入、job_store ownership 持久化）复杂度显著偏高，可读性有代价 |
| 133 | 适用 | R01–R10 指定双模型独立审查+ROOT 接收门禁（本报告即其中一环） |
| 134 | 适用 | AGENTS §5 worktree+feature 分支+文件责任制（当前 40 提交历史即按此执行） |
| 135 | 部分适用 | 锁文件精确固定；dependabot 配置在树；月度升级节奏未建立 |
| 136 | 部分适用 | Electron/rdflib 版本锁定并有升级隔离规则；EOL 跟踪未建立 |
| 137 | 部分适用 | 原型遗留三项已处理（m0-checklist）；vendor 冗余 wheel 未清（R10-05） |
| 138 | 部分适用 | 主要模块尺寸尚可；t02 spec 1,942 行/mainline.py 1,206 行偏大（测试/适配器性质） |
| 139 | 适用 | ADR-0001/0002/0003+M0 计划，决定/理由/未决项明确 |
| 140 | 无法确认 | README 在且快速开始清晰；"新工程师 1 小时内跑通"未实测 |
| 141 | 适用 | docs 树+AGENTS+状态/证据链完整可交接 |
| 142 | 不适用 | 无运营后台 |
| 143 | 不适用 | 无客服工具体系 |
| 144 | 不适用 | 未发布无面向客户 changelog |
| 145 | 无法确认 | 未发布无 ToS/隐私政策文本；本地处理事实由架构固定，文本一致性待发布时核 |
| 146 | 无法确认 | 账户/域名归属属组织事实，代码不可证 |
| 147 | 无法确认 | bus factor 属组织事实（当前单人 owner+AI 工作流） |
| 148 | 适用 | 指定双审逐轮全文覆盖+ROOT 接收（本人本轮亲读核心与 delta 全文） |
| 149 | 适用 | ADR-0002 数据责任分层先于存储实现 |
| 150 | 适用 | 评审轮次记录并处置"AI 修复引入新问题"（如 IR069-01..03 修正留痕） |
| 151 | 不适用 | 无部署/云账单（CI 由 ROOT 票管理） |
| 152 | 不适用 | 无值班支付 |
| 153 | 部分适用 | 依赖锁定+供应链 HOLD；漏洞应急补丁流程未演练 |
| 154 | 不适用 | 无审计接待 |
| 155 | 适用 | 独核/QUALIFICATION 89 项复核+本人本轮只读复核机制在位 |
| 156 | 部分适用 | Store 合成前向迁移 424P+44 条件 skip 已验（R08）；活库/大规模/损坏库物理保护 HOLD |
| 157 | 适用 | 范围冻结/不擅自增功能门禁（AGENTS、Q6 既有决定不重问） |
| 158 | 不适用 | 单机产品无并发客户；容量 Q5 HOLD |
| 159 | 部分适用 | 首败诊断脚本/结构化栈/受控诊断（Windows diagnostic）机制在位；根因能力仍受 UNPROVEN 限制 |
| 160 | 适用 | ADR 记录理由；状态文档历史字节前缀逐轮保全 |

（98–105、114–120、126–127 等区间项如上逐号归档：#98 订阅、#99 失败支付重试、#100 发票 PO、#101 销售税 VAT、#102 退款、#103 用量计量、#104 年度合同、#105 收入对账、#106 webhook 签名、#107 webhook 重试日志、#114 prompt 注入、#115 客户数据出网、#116 按客户花费上限、#117 evals、#118 供应商降级兜底、#119 模型弃用迁移、#120 prompt/output 日志、#126 邮件客户端渲染、#127 通知关闭——均不适用，依据同区间说明。）

---

## 5. 历史条目逐项承接（本人当前适用性；67b7 相对 R09 的 delta 仅 4 测试路径，产品/契约/CI 事实未变——凡"代码事实在位"均经本人本轮 grep/亲读在 67b7 复核）

### 5.1 原 31 稳定位置（R09 disposition §5 全量）

| ID | 本人当前处置 | 最小理由（本人复核依据） | 原 owner/窗口（保持） |
| --- | --- | --- | --- |
| Z08-01 | 仍开（合并门禁） | 本人 ls-remote：remote feature=b0，67b7 未 push 无新 CI | ROOT 精确 push/CI 票；merge 前逐项核 |
| Z08-02 | 仍开（未确认） | O069 engine 自然退出 UNKNOWN、Windows 后代 UNKNOWN 维持 | Windows CI 证据接收；新工具另票 |
| Z08-03 | 仍开（维护） | ci.yml 2b→240→67b7 均未改（本人核 name-status） | 未来制品回单/预算变化须新授权 |
| Z08-04 | 仍开（历史 FAIL 缺栈） | 旧 79F/CI40 首败无逐例栈，新绿不倒填 | 下次真实 CI 复发时定因 |
| Z08-05 | 仍开（双向因果限定） | `rdf_snapshot.py:57` term().lower 在位；language 小写事实未变 | T01 测试维护窗口 |
| Z08-06 | 承接（本地闭合资格） | O069 本机 fullcheck/native24 证据接收；远端 Windows/Quality 未验 | Windows/Quality 实际 CI |
| Z08-07 | 仍开（非阻断延期） | 方法错误码覆盖/裸 detail 文案窗口未至 | 原 T01/T02 方法接线窗口 |
| Z08-08 | 仍开（P2 供应链） | 树内 3 wheel+upstream 在位（本人核） | 发布/供应链 owner 另票 |
| Z08-09 | 仍开（卫生观察） | ci.yml artifact always 已在（本人核 diff），去重评估留维护票 | 未来 CI 维护票 |
| Z08-10 | 仍开（部分采纳维持） | dependabot.yml 在树（本人核存在），执行未核 | 发布/vendor owner 窗口 |
| Z08-11 | 仍开（HOLD 群＋Undo 子集收窄） | 67b7 未触及任何 HOLD 面（delta 仅 4 测试路径） | 各原 owner 对应验收前 |
| Z08-TOP10-OLD79F | 仍开（未知保原） | 历史残留无新证据 | ROOT 登记及复发证据 |
| F01 | 本轮已履行（R10 覆盖） | 本人对 67b7 delta 与核心实现全文必要覆盖（§1）；不预写 ROOT 接收 | ROOT 本票接收 |
| F02 | 仍开（合并门禁，数值更新 67b7） | 67b7 未 push；未来按原 15/20 分钟逐 node | ROOT 精确票后、merge 前 |
| F03 | 仍开+限定 | run-engine-tests.py 结算 fail-closed 语义在位（本人+子代理双复核 §3-R10-04）；"完整 sys.path 等价"不声称 | ROOT CI 控制层维护票 |
| F04 | 维持撤回（不复活） | O067 的 reconciliationReady 缺陷已由 67b7 修复式承接；旧口径不回填 | 本票内闭合 |
| F05 | 仍开（状态登记待履行） | status.md/m0-checklist 归档停在 b0（本人核末段）；67b7 待 ROOT 登记后续归档，本人不代登记 | ROOT 指定文档 owner |
| F06 | 仍开（维护） | CI_ENGINE_TEST_SHARDS/env 传递事实在位；13 身份字段≠sys.path 等价 | 原 T02 归口首个 CI 维护票 |
| F07 | 仍开 | 规则继续适用：无 head/tree 绑定的产出不予接收 | ROOT 证据控制层维护票 |
| F08 | 部分闭合、本体仍开 | 67b7 保留原异步 fence（requireCurrent 链本人亲读）；UX/异步预览维护窗口未至 | 原 T02 前端归口 |
| F09 | 仍开 | 同 Z08-08（冗余 wheel 在树） | T11 merge 后受控维护 |
| F10 | 仍开 | 根 pyproject：lint per-file-ignores（4 个 T01 脚本）≠ format exclude（4+round-NN 模式），覆盖面不等（本人核在位） | 下次含 Python 围栏归档前核 |
| F11 | 承接收窄维持 | fact-ID 与 operation 幂等为两事；golden fixture（真实 Python Store 生成）绑定 digest 一致性 | 原 MM 作者票内闭合 |
| F12 | 仍开 | ci.yml 无延时/重试/隐藏取消（本人核） | ROOT CI 结算/控制层维护票 |
| F13 | 仍开 | 无未实测提速量化声明面 | PR16 说明/CI 结算窗口 |
| F14 | 仍开 | ownership-detail 契约已落地（本人读 schema/双端 matcher）；后续维护归口不变 | 原 T02 契约归口维护票 |
| F15 | 仍开（未确认观察） | storage.py:1151/:1170 无 ORDER BY 在位；无构造性反例不升级 | 原归口 witness 选取维护窗口 |
| F16 | 仍开（容量维持） | READ_LIMITS/HELD_BYTES/128MiB book 未提高（本人读常量） | 原 T02 契约归口 |
| F17 | 维持（语义等价，无新动作） | 无变化 | 无 |
| F18 | 仍开 | NOTICE/PROVENANCE 透明披露在位；供应链核验留发布前 | T11+T02 依赖归口 |
| F19 | 仍开 | 旧 raw/标题保留；round-NN format 排除不触旧件 | ROOT 唯一归档归口 |

### 5.2 权威 78 历史位置（R08 disposition §4 索引；逐 ID）

| 历史ID | 本人当前处置（67b7） | 本人复核要点 | 原窗口（保持） |
| --- | --- | --- | --- |
| Z F1 | 仍开（门禁）：67b7 未 push 无新 CI，O069 本机证据不替代回单 | ls-remote 实测 | ROOT 精确 CI 票；merge 前 |
| Z F2 | 仍开（维护）：本轮 round 归档外无新增 raw 命名入树 | name-status 核 | 未来新增 raw/改规则时 |
| Z F3 | 仍开（维护）：run-engine-tests/reporting 全部 JSON 写出显式 UTF-8（子代理+本人抽查）；历史 20 默认 encoding 窄结论维持 | 脚本亲读 | 原测试 owner 下次触及 |
| Z F4 | 关闭（口径）维持：双分母事实修订；62d4→67b7 无 dumps 调用面变化 | — | 无待办 |
| Z F5 | 仍开：两 TS PATH python 在位（t01-mainline-contract / t01-mainline-real-runtime，grep PATH 命中） | grep | T01 测试维护者下次授权 |
| Z F6 | 仍开（逐项集合）：definitions 早期 wire、裸 ownership、standalone EOF、缺码、无序、4299/4300 分见对应行，未被集合化关闭 | 各行复核 | 各接线/维护事件 |
| Z F7 | 仍开（发布 HOLD 群）全部保留 | delta 未触及 | 各 owner 对应验收前 |
| Z F8 | 仍开（部分）：rdf_snapshot.py TermInputError 分流在位（本人读 ：40-49），裸族两出口终码仍 OWNERSHIP_CONFLICT | 亲读 | 未知/新家族接线前按 HOLD |
| Z F9 | 承接（限本受审面闭合）：_OwnershipProof 授权链完整（本人读 mainline.py:478-517/677-700） | 亲读 | T01/T02 触及合同出口时再核 |
| Z F10 | 承接（既有证据接收）：O047/O069 native24 57 事务/43 拒绝不外推全 GUI | — | 无待办 |
| MM R07-01 | 关闭：排除面在（根 pyproject per-file-ignores 本人核）；覆盖面问题归 F10 | 亲读 | 本次静态接收 |
| MM R07-02 | 仍开（维护）：未发生的新 raw 非当前失败 | — | 未来确增 raw 名时 |
| MM R07-03 | 仍开：两覆盖面仍不等（同 F10 本人核） | 亲读 | 独立配置票 |
| MM R07-04 | b0 已履行（240 归档=O066）；67b7（R10 资料）再次处于待归档（同 F05） | status.md 核 | ROOT 文档 owner，本票归档后 |
| MM R07-05 | 仍开（overlay 维护）：AGENTS.md 未提交 overlay 在位（git status M） | 亲读 | ROOT/指南 owner 授权维护时 |
| MM R07-06 | 关闭（口径）维持 | — | 无待办 |
| MM R07-07 | 已闭合（口径）：20 默认 ASCII JSON 窄结论维持 | — | 载荷变化时 |
| MM R07-08 | 已闭合（口径）：28 笔 FR200 分层不扩维持 | — | 父 FR/具名下游另验 |
| MM R07-09 | 已闭合（口径）：本轮无新构建，沿用既有 nonce 证据（O069 同口径） | — | 既有证据限定 |
| MM R07-10 | 已闭合（口径，歧义见 F19）：Ruff 各时点计数对账维持；67b7 无 .py 变化 | name-status 核 | 无新复跑票 |
| MM R07-11 | 仍开（观察）：mainline-facts.ts edit 保原 ID/重叠拒绝扩展在位（本人读 diff） | 亲读 | T02/ROOT PR 说明可解释 |
| MM R07-12 | 仍开（HOLD）：PROVENANCE/patch/upstream 三方哈希记录在位；法律/供应链 HOLD 保留 | 亲读 | vendor/发布 owner 升级/发布前 |
| MM R07-13 | 仍开（维护）：index.ts:894-895 TS 宽于 schema 在位（本人核） | 亲读 | 契约 owner 下次整理 |
| R06 Z P1 | 仍开（门禁）：同 Z F1，数值 67b7 | — | 合并前真实 CI |
| R06 Z P2 | 仍开：诊断步与验收口径分离维持（F03） | — | 未来 CI 证据接收标准 |
| R06 Z P3 | 仍开：domain_changesets.py:157 `_definition(store, record)` 预览路径未分类 ValueError 在位（本人核） | 亲读 | T01 核心；原始 wire/Agent 接线前 |
| R06 Z P4 | 部分闭合维持：typed witness（Manual/SingleDeclaration 含 witness）已落地（本人读 storage.py:67-104）；裸族未全闭 | 亲读 | T01 详情合同＋T02 消费 |
| R06 Z P5 | 仍开：错误码集合差事实维持（OWNERSHIP_CONFLICT 参数仅 detailRef 等白名单），16 码可达性未证 | 亲读 | 对应方法接线前 |
| R06 Z P6 | 仍开（未确认观察）：:1151/:1170 无 ORDER BY（本人核） | 亲读 | T01 Store 维护触及选取时 |
| R06 Z P7 | 已闭合（沿既有决定）：domain_changesets.py:464 `parsed.n3() != value` 在位（本人核）；Q6 不重问 | 亲读 | 政策变更才新人类决定 |
| R06 Z P8 | 仍开（逐项承接）：7.2–7.6 各行分别承接，不以集合标题掩盖 | — | 各原归口 |
| R06 D1 | 仍开（门禁）：67b7 delta 仅 4 测试路径，无新源码缺陷；门禁待 CI | 亲读 | ROOT 正常票 |
| R06 D2 | b0 已履行 240 归档；67b7 待归档（同 F05） | status 核 | ROOT 文档 owner |
| R06 D3 | 仍开：同 R06 Z P3（同源事实本人核） | 亲读 | T01；接线前 |
| R06 D4 | 部分闭合维持：两出口终码均 OWNERSHIP_CONFLICT（storage.py:818-827/1174-1177 与 _application 分流本人读）；裸族定位未全闭 | 亲读 | 随家族接线处理 |
| R06 D5 | 仍开（未确认观察）：同 Z P6 | 亲读 | T01 下次触及选取时 |
| R06 D6 | 仍开：patch 含 `j==len_argstr`/digit-limit 类型化守卫（本人读 patch 头 80 行）；`n[-1]` 裸索引残余未证不可达 | 亲读 | 新解析入口前复核 |
| R06 D7 | 仍开：同 Z P5 | — | T01/T02 对应方法接线前 |
| R06 D8 | 仍开：同 Z F5（grep 在位） | grep | T01 测试维护者 |
| R06 D9 | 已闭合（口径）：Ruff 各时点原件保留；67b7 无 Python 变化 | name-status | 文档 owner |
| R06 D10 | 仍开：四具名下游（编辑→推导/保存查询/SHACL/报告）GUI 未逐类验；公共失效九例证据维持，两分不抹 | — | 父 FR/消费链验收前 |
| R06 D11 | 仍开：仅 4301 断言在位（本人 grep：ui-observation.test.ts:115、t02 spec:1010、language:36），4299/4300 应用断言缺 | grep | T02 整数守卫维护窗口 |
| R06 D12 | 保留（有界）维持：六 keyword AST/本地运行/旧包身份按原资格不外推 | — | 无待办 |
| R04 Z01 | 仍开（未确认观察）：同 Z P6/D5 | 亲读 | T01 触及选取时 |
| R04 Z02 | 撤回维持：43692 误因果不复活；262,144/16MiB 预算边界仍在（job_store 页上限 min(maxPageBytes,maxFrameBytes,262144) 本人读） | 亲读 | T01 详情预算维护 |
| R04 Z03 | 仍开：同 R06 Z P3/D3 | 亲读 | T01；接线前 |
| R04 Z04 | 仍开（部分闭合）：同 R06 Z P4 | 亲读 | 家族接线前 |
| R04 Z05 | 仍开：同 Z P5/D7 | — | 方法接线前 |
| R04 Z06 | 关闭：canonical 既有政策在位（:464 本人核） | 亲读 | 无待办 |
| R04 Z07 | 关闭：规模信息接收，不以 LOC 推正确性 | — | 无待办 |
| R04 M01 | 关闭（历史演进）：当前 head 状态源另见 F05 | — | ROOT 归档票 |
| R04 M02 | 关闭（维持）：PROVENANCE/审计件在树（本人核）；fr201.1/2 保留不删见 F09 | 亲读 | 无待办 |
| R04 M03 | 仍开：同 R06 D11（grep 本人核） | grep | T02 整数守卫时 |
| R04 M04 | 仍开：standalone EOF 残余未证当前 UI 可达 | — | 新解析入口前 |
| R04 M05 | 仍开：同 D3/Z P3 | — | T01 接线前 |
| R04 M06 | 关闭（维持分层）：双端 ID 校验/原 ID edit 在位（mainline-facts.ts 本人读）；不外推全产品安全认证 | 亲读 | 无待办 |
| R04 M07 | 仍开（维护窗口）：未证冲突，不缩导出面 | — | 契约 owner API 整理时 |
| R05 Z P1 | 仍开（门禁）：同 Z F1 | — | ROOT 合并门禁 |
| R05 Z P2 | 关闭（事实）维持：934 Quality packaged recovery 为历史证据，不迁移新 head | — | 无待办 |
| R05 Z P3 | 仍开：同 Z P3 | — | T01 接线前 |
| R05 Z P4 | 仍开（部分闭合）：同 Z P4 | — | 家族接线前 |
| R05 Z P5 | 仍开：同 Z P5 | — | 方法接线前 |
| R05 Z P6 | 关闭（口径）：canonical 政策不变（见 F03 关联） | — | 无待办 |
| R05 Z P7 | 关闭（口径）：诊断选项演变事实；F03 约束继续 | — | 无待办 |
| R05 Z P8 | 已闭合（维持）→ 在 b0 已履行归档；67b7（R10）待归档 | status 核 | ROOT 文档 owner |
| R05 MM01 | 仍开（门禁）：旧 79 全因未知 | — | 新 CI 后合并前 |
| R05 MM02 | 已闭合（事实）维持 | — | ROOT/新 CI 后 |
| R05 MM03 | 仍开（门禁）：67b7 未打包（O069 构建副本=旧 5+nonce 差，非新包制造，本人核 BUILD-REBUILD 映射声明） | 亲读 | 新包制造票 |
| R05 MM04 | b0 已履行 240 归档；67b7 待归档（同 F05） | status 核 | ROOT 文档 owner |
| R05 MM05 | 仍开：同 Z P5/D7 | — | 方法接线前 |
| R05 MM06 | 仍开：同 D3/Z P3 | — | T01 接线前 |
| R05 MM07 | 仍开（部分闭合）：typed witness 已实现；裸族延期 | 亲读 | 家族接线前 |
| R05 MM08 | 仍开（未确认观察）：同 Z P6（本人核无序在位） | 亲读 | T01 下次触及选取时 |
| R05 MM09 | 已闭合（维持）：wheel/payload/解压量分层；冗余件见 F09 | — | vendor/发布 owner |
| R05 MM10 | 关闭：AGENTS overlay 维持非候选缺陷（git status M 在位） | 亲读 | 无待办 |
| R05 MM11 | 关闭（信息）：locator 仍仅 id/owner/sourceRow/slot，无 object（storage.py locator 本人读） | 亲读 | 无待办 |
| R05 MM12 | 仍开：两 TS PATH python（grep 在位） | grep | T01 原测试维护者 |
| R05 MM13 | 关闭（信息）维持 | — | 无待办 |

### 5.3 R09 新条目与 Top（stableID 原样承接，本人当前适用性）

| ID | 本人当前处置 | 本人复核要点 | 原 owner/窗口 |
| --- | --- | --- | --- |
| Z09-01 | 仍开：67b7 无新 CI，完整平台 CI 待办、merge 门禁 | ls-remote | ROOT；精确 CI 票/merge 前 |
| Z09-02 | 仍开：CI41 根因 UNPROVEN，前置同步不冒证因 | ci/driver 只读核 | ROOT；真实 CI 归因 |
| Z09-03 | 仍开：engine/Windows 后代退出 UNKNOWN | O069 边界声明 | ROOT；CI 证据接收 |
| Z09-04 | 仍开：3 冗余 wheel 在树（本人核） | 目录核 | T11；merge 后受控维护 |
| Z09-05 | 仍开：TS 类型宽于 schema/常量双源（index.ts:894 本人核） | 亲读 | 契约 owner；下次整理 |
| Z09-06 | 仍开（不升级缺陷）：无 ORDER BY 观察在位 | 亲读 | T01；触及 witness 选取时 |
| Z09-07 | 仍开：仅 4301 断言、4299/4300 消费断言缺（grep 本人核） | grep | T02；原整数守卫维护窗口 |
| Z09-08 | 仍开：制品卫生/always 取消限制（artifact always 已在，去重评估留票） | ci.yml 亲读 | ROOT；下次回单/CI 维护票 |
| Z09-09 | 仍开：native-driver 与 Electron 内部映射耦合（CDP 就绪探测本人读 217-242） | 亲读 | 原 T02 native 线+ROOT；升级/证据维护 |
| Z09-10 | 仍开：裸 ownership 详情 HOLD 家族（67b7 未触及） | delta 核 | T01/T02；对应家族接线前 |
| F-R09-01 | maintain：67b7 无新 CI；累计引擎/spec 执行证据已有（O069），CI41 平台失败保留 | 亲读 | ROOT/原 T02；下一精确 push 后 |
| F-R09-02 | maintain：根因 UNPROVEN 为 HOLD 与主张纪律，非新"必须证因"门禁 | — | 原 T02/ROOT；真实 CI 归因 |
| F-R09-03 | maintain：readiness-helper 断言与 app?.isPackaged 建议已撤回；根因 HOLD 保留 | — | 原 T02 测试/打包；真实 CI 归因 |
| F-R09-04 | maintain：145.101s 非轮询耗时为有界观察，不作新门禁 | — | 原 T02 测试；真实 Windows 运行后 |
| F-R09-05 | maintain：仅失败 annotation 核查；成功 CI 无需失败样本 | — | 原 T02；真实失败样本存在时 |
| F-R09-06 | maintain：证据绑定接收限制；脚本 A 在 base→240、240→67b7 未改 | name-status | ROOT；证据接收拦截 |
| F-R09-07 | maintain：sys.path 等价限制不解除 | — | 原 T02 |
| F-R09-08 | maintain：指定文档 owner 的状态归档义务——67b7 待登记（同 F05） | status 核 | ROOT 指定 owner；本票归档/状态追加 |
| F-R09-09 | maintain：完整 CI/制品接收纪律；ci.yml 在 base→240 累计内、其后未改 | name-status | ROOT；每次 CI 完整回单 |
| OBS-R09-10 | maintain（P3）：整数上限测试环境前提记录，4299/4300 不因此关闭 | — | 沿原 T02 测试窗口 |

### 5.4 MM 额外 13 行（不充作原 78，独立列示）

R06 MM01 仍开（门禁，数值 67b7）；R06 MM02 已闭合（事实）；R06 MM03 仍开（门禁，67b7 未打包）；R06 MM04 b0 已履行→67b7 待归档重新变开；R06 MM05 仍开（同错误码集合差）；R06 MM06 仍开（同 definitions wire）；R06 MM07 部分闭合（typed witness 已落地、裸族延期，本人读 storage.py 两 Conflict 类）；R06 MM08 仍开（未确认观察，无序在位本人核）；R06 MM09 已闭合（维持，冗余件见 F09/Z09-04）；R06 MM10 已闭合（overlay 在位本人核）；R06 MM11 已闭合（locator 字段面本人核）；R06 MM12 仍开（维护，两 TS PATH python grep 在位）；R06 MM13 已闭合（信息）。

---

## 6. 门禁、未验项与 HOLD（不因本报告改变）

- **远端与合并**：PR16 open/unmerged，remote develop=583、feature=b0（本人只读 ls-remote）；67b7 未 push、无新 CI、无新包。整体合并可用仍 2/17（FR401/402），不推进 T04。
- **未来 merge 前仍须**：同交付实现/测试/CI/依赖下 Windows 3769 全集逐 node 通过或原有据条件 skip、自然 0、无失败/早停/取消/timeout/NOTRUN、全部后继（typecheck/build/E2E/package/verify）、Quality 专项与 packaged recovery 步骤自身 success、三 job 实际 success，原 15/20 分钟不变；case7 若复发须定因处置；作者 CI 后条件确认、精确 merge 票与 remote SHA/tree/功能复核另验。
- **独立 HOLD 全部保留**：签名/公证/wholeApp 法律/_distutils/隐私产权与供应链；跨 OS（macOS15/Win11）与参考 8GB 设备；Q5/D2 容量、旧超限库恢复、损坏 SQLite 物理保护；unknown parser/N3/Store/坏快照/standalone EOF；其余 Undo/ownership 未验家族；具名下游四类 GUI；native engine 与 named App 及 Windows 后代未知退出码；测试专用 env 重定向写路径（R10 维护观察）等。
- **O068 部分 C1 PASS** 只补该旧内容实际子集，不给 CI41 根因或完整 C1 放行；旧 R09 ConditionalPass 不继承至本候选（本报告为 R10 独立结论）。

---

## 7. 总体判定

**ConditionalPass。**

理由（本人独立形成）：

1. 实现与修复质量：base→67b7 累计候选在存储、契约、引擎、渲染各层保持既定架构不变量（本地优先、渲染端隔离、CSP 单源、确定性/Agent 解耦、SQLite 唯一真相、错误面受限）；67b7 delta 是对 R09 已识别观测弱点的正确修复，未发现断言弱化或产品面改动。
2. 未发现 push 前源码技术阻断：本人全文/差异级审查 + 子代理 sweep + 本人复核未发现新的安全或正确性缺陷；Top 风险 9 项均为门禁、未证根因、维护、测试质量或治理项。
3. 条件（非本报告新增，均为既有门禁）：完整平台 CI 三 job 实际 success 与逐 node/原有据 skip/自然 0 接收；case7 复发定因；状态文档对 67b7 的登记与归档（F05/F-R09-08）；全部 §6 HOLD 在对应验收前保留。
4. 本判定不授权 push/PR 修改/新 CI/merge/打包/任何远端或预算动作；上述仍由 ROOT 按既有门禁另行决定。

---

## 8. 证据与路径清单

- 本报告唯一写入路径：`outputs/20261027_t02_67b7_fresh_r10_070/zcode/report.md`（未在 worktree 内写任何文件）。
- 输入原件：`~/.zcode/tmp/paste-attachments/2026-10-27/pasted-text-20261027-041241-c148fb1d.txt`（= 仓外 `zcode-complete-input.md`，cmp 逐字节相同）。
- 受审对象：worktree `T02-s1-review-fixes` @ 67b7bcbd（冻结 SHA 读取；AGENTS.md overlay 与 round-01/02/03 未跟踪 WIP 为既有保护项，未触碰）。
- O069 证据：`outputs/20261027_t02_minimal_observation_repair_069/`（COMPLETION/staged.diff/FINAL-MANIFEST/两独核/NATIVE24 哈希均本人实测相同；HANDOFF/ROOT-SEND-RECEIPT 属 70 针外已披露排除件）。
- 历史证据：O059–O068 按仓外 outputs 目录与 round-09 disposition/artifact-manifest/version-map 索引引用；round-04…round-09 归档在 `docs/reviews/T02/fr200-fr201-20261024/`。
- 子代理：单个只读 Explore（21 文件 breadth sweep），其五项载重发现均经本人原文复核后采信；原文留存于任务档案。
- 本报告不内嵌自身终态 bytes/SHA；由 owner 另存原件实测。

---

# 追加处置（同任务追加稿；前缀保全声明）

本节为本人 R10 同任务必要覆盖／事实／位置处置补充。首自然稿 57671B（SHA256 `66dd65a4b06345fa1645b78d551a3151c254e5f53eb175f72722d6ab4486fb52`）全部原文保留为前缀、未改动任何旧句；以下全部为追加内容，凡与首稿表述不一致处，以本节"有效替代"行准，旧句保留不删除。本追加稿未重开审查、未运行任何测试/构建/安装/formatter/Git 写、未读另一作者本轮任何输出；代码发现仅回 ROOT，不在本报告内改源。

## A. Z10-AUDIT-02：必要覆盖补齐与 F01 有效替代（覆盖三层如实闭合）

追加稿本人直读补齐（此前首稿仅 pattern 清点/抽样，与 §5.1 F01 旧句不一致——该不一致属实，本节以补读与替代句闭合）：

**本人直读（追加稿新增消耗，范围与语义结论）**

1. `packages/engine/tests/test_mainline_language_input_rejection.py` 1–326 全文：独立 stdio 子进程三族拒收（@1/@zh1/4301 位整数）+物理库文件字节（main/-wal/-shm/-journal SHA256）拒收前后不变；同会话后续合法提交、数字子标签合法提交、大写子标签维持 canonical 拒绝；委托 `owned_rejection` 复用其全部断言（含内部 HOLD 标志与连接/租约/选择身份）。
2. `test_mainline_manual_input_rejection.py` 1–1034 全文：非规范别名拒收后 iterdump 全库不变、无调用方归一化、宿主身份保持；原 ID 编辑+Undo 后 ID 保持；四类非输入故障（term/preview/sqlite-integrity/snapshot-integrity）→INTERNAL_ERROR+hold+unknown 结算+后续 STORAGE_FAILURE；parser/urlsplit/IRI 预检的未知故障不按消息文本分类（同文本异常亦 UNKNOWN）；vendor 版本 pin（`7.6.0+ontolearn.fr201.3`）与 `TermInputError` 专属类型；reservedIdentity 完整 ownership detail 分页读取（独立 hashlib 逐段+全量 SHA）+诊断行外无库变更；singleDeclaration 同计划签发者判定（removed-first 保留原 UNKNOWN 不弱化守卫）；同 host 拒收后合法后继全链提交。
3. `test_mainline_postwrite_admission.py` 1–860 全文：终态增长边界轴参化（rows/bytes/work × −1/0/+1）；2742B 终端尾部证明常量独立 pin；真实草稿增长受控拒绝（物理文件字节不变、无 operation claim）后小草稿同 host 继续；排队 commit 终检（cancel/fail/commit-limit 三果、仅 jobs DTO 行变化、重放返回原 job 不新增行）；双项目全局余量；前台/后台作用域不可借用/退款；after_commit 重入拒绝；清理失败保留原始因与 holding；结算失败保持精确 unknown；bootstrap 未决 writer 不可被后继领养（unfinished/retained/8 态矩阵）；干净交接后真实后继可用而旧 proof 失效；后继不可接管排队/活动 job；真实 stdio 增长拒绝+同 host 合法提交；bootstrap 重启后已接受 job 结算 failed/ENGINE_EXITED、marker None、read 可用。
4. `test_mainline_postwrite_rows_budget.py` 1–395 全文：243 行五列真实查询的完整行枚举（itertools.product 独立期望）+逐页边界/费用记账观察（reserve/before_commit 计费钉 1114112/8192/134217728，before==after 无扣减）；终检费用拒绝原子（无退款）后同 host 继续；页作用域不可借出/退回预付费用（unknown/replacement）；预付物不能二次消费。rowKey 用产品 digest 复算（共享 oracle，见 C 节 R10-06 精化）。
5. `test_mainline_postwrite_text_budget.py` 1–320 全文：56,309 字符文本（ASCII/多字节）冷历史真实执行；executedText 独立 `hashlib.sha256` 校验（好样板）；UTF-8 字节游标恒等、页字节/帧上限断言；final prepaid 费用 528384/256/1052672 与每页一次；拒绝原子后同 host 继续；游标回调吊销在最终编码器之前拒绝、job_cursors 行数不变。
6. `test_mainline_read_work_budget.py` 1–559 全文：44 op/22 快照真实历史 + 不透明 blob 至工作界；同 host core 读通过而默认全表面 reader 仍拒绝（两公式分开验证）；最后 remove 提交/marker/after read 全链；64MiB 工作界在 lower/authorized-plan 两阶段先于校验拒绝——**用 SQL trace 回调独立证明 json_extract 是否执行**（独立于公式副本的证据渠道）；重复解码界先于 plan 选择器；六类损坏（context/plan/snapshot/checkpoint/repeated-ref/cross-project）仍跑完整认证并 STORAGE_FAILURE+hold、iterdump 不变、health 可用；authorized-plan SQL 失败无零兜底（authorizer 拒绝 json_extract → STORAGE_FAILURE+hold）。
7. `test_mainline_dispatch.py` 累计新增块（新行 56–585，+523 行）+ 必要既有 fixture/dispatch 上下文：`ownership_fixture`/`ownership_pages` 助手 + 12 个测试——大定位符（manual/managed×40k 字符）完整分页纯读有界、错 documentHash→IDENTITY_CONFLICT、末页非全文权威、跨项目 NOT_FOUND、诊断后同 host 合法提交；损坏矩阵（missing-version/empty-header/bad-json/bad-segment）→STORAGE_FAILURE+hold；分段失败全诊断行回滚且无 detailRef；诊断不能污染已准入全量 reader（早/晚）；私有准入保留 core-only 向量（admissions==(True,False)、旧 proof 失效、公开 preview 原全目的预检不变）；坏既有 blob 在 intern 复用前有界拒绝；原始段预算拒绝先于 JSON 解码；行上限处去重复用回滚新上下文；精确历史三字段 detail →INVALID_STATE；引用不跨后继会话（NOT_FOUND+新 preview 新 ref）。
8. `packages/contracts/v2/fixtures.json` 全部变更（350+/96− 共 446 changed，非 446 added；U2 diff 全 hunk 亲读）：新增 3 个 request 模式用例（named ownership request valid；no null continuation invalid——documentHash null 时 startOrdinal 必须 0；wire issuer forbidden invalid——多余 ownerId 键拒绝）与 4 个 request/response 绑定用例（named ownership page valid；wrong ref invalid；corrupted segment SHA invalid；premature next invalid）；其余全部变更为 registryHash `058ed1be…`→`5e097b7e…` 的传播（含 26367/26621 起 127 行 golden startupFailure wire 的 wireUtf8/wireBase64/chunksBase64 同义重编码，仅内嵌 registryHash 变化）。无其他语义变更。
9. `packages/contracts/v2/schema.json` 新增三块全文（6877–6901 request 变体、8698–8761 response ok/error 变体、11449–11884 `$defs`：ownershipDetailDocument 双 kind 全边界（existing id/owner/sourceRow/slot、incoming id=hash/owner null/sourceRow null、single-declaration declaration/slot/existing[2]）、manifest（totalBytes 2..16,777,216、segmentCount 1..512）、header（origin 三元组、requestHash/fingerprint、segmentBlobRefs 1..512）、params 双变体（null+startOrdinal 0 / hash+startOrdinal 1..511、pageSize 1..64）、result（segments 1..64、nextOrdinal 1..511|null、complete）。
10. `tests/e2e/native-driver.ts` 完整累计 diff（246+/58−；首稿仅前 200 行）：`waitFor` 统一取消集、发送边界再校验、45s 绝对截止不重置、就绪探测显式校验 Electron 映射（`resolve('electron')==='electron'`、process.type browser、app/dialog/BrowserWindow API 形状、whenReady/isReady 一致）、helper 只发送一次不重试、子进程先退时同预算内 drain stdio、finally 全量清理监听。450×100ms 就绪轮询确为未证竞态的同步补丁（R10-08 维持）。
11. `tests/e2e/t02-fr200-fr201.spec.ts` 全文 1–1942（首稿已消费 67-delta 与关键函数，本稿补齐全部剩余正文）：FR200 四类 CRUD/复制/删除矩阵的完整 M/RDF 期望（独立手写 N3 期望，非产品适配器生成）；FR201 多值/原 ID 编辑链/11 类受控拒收输入（datatypes/quote/language/authority/4301 整数/别名）×add/edit×字段隔离；OWNERSHIP_CONFLICT reservedIdentity 可见定位（列表/标题/字段逐项断言+页面附件）；失败 catch 的有界诊断（2s/262KiB/只读桥查询/DOM 先于读后于读、诊断失败不覆盖原始失败）；数字子标签独立 cohort 自证 fixture 隔离非容量修复。全文确认无 skip/TODO/注释断言。
12. `packages/engine/vendor/rdflib/notation3-input-types.patch` 全文 1–136（首稿前 80 行）：余部为 `j < 0`→MissingDatatypeError、assert→UnterminatedStringError、`j == len_argstr`→UnterminatedStringError、UnicodeCodePointError 精确捕获、`_is_valid_langtag` 复用 Literal 校验器→InvalidLanguageTagError。patch 全部为输入分类类型化，无行为外溢；R06 D6 的 `n[-1]` 裸索引残余在本 patch 段之外、未证不可达（维持原判）。

**子代理真全文 + 本人核对层**：`tests/unit/` 各文件（native-driver.test.ts、t02-manual-fact-id、t02-manual-preview-lifetime、t02-ownership-detail(-view)、t02-mainline-consumer、t02-mainline-metadata、t01-mainline-real-runtime 等）及 `scripts/run-engine-tests.py`/`engine-test-reporting.py`/`repack-rdflib-input-types.py` 的全文清点（首稿 §1.3 已述），其中五处载重发现经本人原文复核（首稿 §3 R10-04/06/07 与 §1.3），本追加稿对 run-engine-tests 结算语义的 grep 复核维持。

**真正未读（如实保留）**：`fixtures.json`/`schema.json` 未变约三万行；`test_mainline_dispatch.py` 未变旧段（首稿与子代理覆盖其调用面）；三个 wheel 与 upstream wheel 的内部字节（仅哈希/尺寸/PROVENANCE 有界核）；R04–R08 历史报告全文（按 round-09 索引必要引用）。

**F01 有效替代句（替代首稿 §5.1 F01 行"本轮已履行（R10 覆盖）"句）**：F01 = 本票（首稿+本追加稿）必要覆盖已按上述三层如实闭合：本人直读覆盖 67b7 delta 四路径全文、累计候选全部产品/契约/引擎/vendor/CI 变更、6 个引擎测试文件全文、dispatch 新增块、fixtures/schema 全部变更、T02 spec 与 native-driver 全文、治理文档与 R09 处置全文；子代理真全文+本人复核覆盖其余 tests/scripts；未读清单如上、不以摘要冒全文。旧句保留、由本段替代。

## B. Z10-AUDIT-01：HANDOFF 比较对象错位更正（撤回不一致事实与错误解释）

本人实测：`outputs/20261027_t02_b0_quality_retry_068/HANDOFF.json` 存在，1803B、SHA256 `2f8fbe97ba775027991fb90347a3db4764f9bf61690df50cf15e0aaec2457ed7`，与 O069 `COMPLETION.json` 的 `qualityRetryO068.handoff` 针**精确一致**——该针本就指 O068 目录的 HANDOFF.json。O069 自身 `HANDOFF.json`（1530B/`6f8b3a00…`）是另一文件，两者各自正确。首稿 §1.2 末段及 §3 表下注、§8 中"O069 COMPLETION 的 handoff 针与当前磁盘 HANDOFF.json 不一致……属已披露排除边界（FINAL-MANIFEST scope 排除）"的**事实陈述与因果解释均撤回**（是我把跨目录同名文件误当同一对象比较；FINAL-MANIFEST 的 self/laterHANDOFF 排除范围声明本身仍为真，但不是也不需要是对该"不一致"的解释）。保留维护建议：跨目录证据针应携带目录限定路径（该针字段仅给 basename `HANDOFF.json`，需读目录语境 `qualityRetryO068` 才能定位正确对象——本次误读的根因）；不改任何原件。

## C. Z10-AUDIT-07 与 Top 风险更正（R10-06 精化、R10-09 重写、归属标注）

**R10-06 精化（有效替代首稿 §3 R10-06 行的表述与范围）**：全文直读后收窄——共享 oracle 事实仍在（`scalar_profile`（read_work_budget:31-57）以裸 SQL 重实现产品记账公式并预测边界；两 e2e spec 的 `canonical()` 副本；多处用产品 `digest()` 现算期望 id/rowKey），但同文件存在**独立于公式副本的证据渠道**：SQL trace 回调证明 json_extract 是否执行、authorizer 拒绝证明无零兜底、损坏注入走真实触发器机制并配 iterdump/digest 不变量、text_budget 的独立 `hashlib.sha256`、itertools.product 独立全枚举、t02-manual-fact-id 的真实 Python Store golden。故盲区限于"边界预测值与产品公式同源同错"的窄面，多数行为断言（真实 RESOURCE_LIMIT 响应、SQL 面、不变量）仍为产品侧独立事实。严重性维持低（P3 测试质量），原归属：本候选测试为 T02 开发线产物；建议窗口：T02 下次测试维护/CI 控制层维护票；原文未规定专门 owner——**待 ROOT 归口**，不造授权。

**R10-09 重写（有效替代首稿 §3 R10-09 行与 §1.4 末段解释）**：首稿"治理文档无版本控制/无哈希针、仅主 checkout 未跟踪件"**事实错误，撤回**。本人亲核（O069 之外、本轮新实测）：`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 与 `docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md` 均已在 67 版本化（`git cat-file -e 67b7…:<path>` 通过，两路径同一 Git blob `3672867e50ecc2f359c1dcd7a81db1ae8f9b1d26`），工作树文件均 35812B、SHA256 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`，且与本人首稿所读主 checkout 未跟踪件 `cmp` 逐字节相同——即首稿阅读的就是版本化原件的同内容文件，S1/S2/S3/C1/B1/U1 全文阅读有效不变。owner 侧同目录证据 `M0-VERSIONED-PRIMARY-FACTS-01.json`（793B，SHA256 `6a3f0af399c7a9668fdc914374a94dff28dc151f62b19a381326a3adcfdd5b9e`）本人已读，其记载与本人实测一致。**保留的真实观察（收窄为低/路径维护）**：AGENTS.md 所指 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 在任何分支不存在（六 ref 亲核），属失效引用路径；主 checkout 另有一份未跟踪副本（`??`）构成冗余。建议：AGENTS 指向已入库受控副本（I01/I03 inputs 之一）并注明 blob/SHA；归属：指南 owner（ROOT/AGENTS 维护票）；不新增门禁。首稿 §1.4 对 M0 计划的"按真实同主题原件读取"处置本身不受影响，仅其推论句被本段替代。

**R10-07**：归属同 R10-06（T02 测试维护/CI 控制层维护票，待 ROOT 归口）；**R10-08**：native-driver 部分承 Z09-09（原 T02 native 开发线+ROOT，升级/证据维护窗口），ui-observation 判据部分属 67b7 新增测试件（T02 测试维护/Playwright 升级时重证，待 ROOT 归口）；R10-01..05、R10-10 之外首稿 Top 表维持原归属。

**MM 额外 13 行逐 ID 原位映射与窗口（补 Z10-AUDIT-07；集合与状态首稿 §5.4 已正确，此处补 owner/窗口/依据，不与原 78 混计）**：

| 额外ID | 无歧义原位映射 | 原 owner／事件窗口 |
| --- | --- | --- |
| R06 MM01 | ≡R05 MM01/Z F1（完整平台 CI 门禁；67b7 未 push 无新 CI，本人 ls-remote） | ROOT 精确 push/CI 票；merge 前 |
| R06 MM02 | ≡R05 MM02（934 Quality packaged recovery 历史事实，不迁移新 head） | 无待办（已闭合事实） |
| R06 MM03 | ≡R05 MM03（本 head 未打包；O069 构建副本=旧5+nonce 差非新包） | ROOT 新包制造票 |
| R06 MM04 | ≡R05 MM04/R06 D2（240 归档已由 b0 履行；R10 资料归档前再次待归档，同 F05） | ROOT 指定文档 owner；本票归档后 |
| R06 MM05 | ≡R05 MM05/R06 Z P5（错误码集合差；16 码可达性未证） | T01 契约+T02 方法出口；接线前 |
| R06 MM06 | ≡R05 MM06/R06 D3（definitions 早期 wire ValueError 未分类，:157 本人核在位） | T01；原始 triples/Agent 接线前 |
| R06 MM07 | ≡R05 MM07/R06 Z P4（typed witness 已落地、裸族延期，storage.py 两 Conflict 类本人读） | T01 详情合同+T02 消费；家族接线前 |
| R06 MM08 | ≡R05 MM08/R06 Z P6（无 ORDER BY 未确认观察，:1151/:1170 本人核） | T01 触及 witness 选取时 |
| R06 MM09 | ≡R05 MM09（wheel/payload/解压量分层维持） | vendor/发布 owner；升级/发布前另票 |
| R06 MM10 | ≡R05 MM10（AGENTS overlay 维持非候选缺陷，git status M 在位） | 无待办；ROOT/指南 owner 授权维护时 |
| R06 MM11 | ≡R05 MM11（locator 仅 id/owner/sourceRow/slot，storage.py locator 本人读） | 无待办（信息闭合） |
| R06 MM12 | ≡R05 MM12/Z F5（两 TS PATH python，grep 在位） | T01 原测试维护者；下次授权/环境适配前 |
| R06 MM13 | ≡R05 MM13（规模信息接收） | 无待办（信息闭合） |

## D. 160 项清单四处重判（Z10-AUDIT-03/04/05/06；唯一有效新统计）

下列四项由本人据实重判，**替代**首稿 §4 对应行（旧行保留）；其余 156 项判定不变。新统计为唯一有效统计，首稿 26/48/81/5 由本行替代、不并计：

**适用 24｜部分适用 50｜不适用 79｜无法确认 7｜合计 160**

| # | 旧判→新判 | 依据（本人实证） |
| --- | --- | --- |
| 31 | 适用→部分适用 | 43 拒绝构成更正：NATIVE24 `negativeCodeCounts` 为 42 INVALID_REQUEST + 1 OWNERSHIP_CONFLICT，全部是受控非法输入/冲突拒绝，**不是**四次连点/重复提交实验（首稿"43 拒绝含重复面"表述错误，撤回）。真实独立证据：operationId 幂等（同 operation 重放 `job.create` 返回原 job 不新增行——postwrite_admission:211-213/231-233 本人读）、丢 ACK 恢复不重放（case7 singleCommitCalls=1/execute0/replay0）、preview→人工确认单提交链。字面"用户连点四次提交"行为未实跑——保留未实跑边界，判部分适用 |
| 33 | 不适用→部分适用 | 本人核 `tests/e2e/t04-query-variants.spec.ts`（41,525B）真实 UI ASK/SELECT 查询结果 CSV 导出（`导出 ASK 结果 CSV`→query-ask.csv，精确内容断言 `"ASK"\r\n"true"\r\n` 等）；NATIVE24 attachmentPins 含 t04-actual-query-variant×4、t04-reopened-history-ui.csv、t04-real-ui-query-chain、t02-existing-home-to-t04-query——具名 CSV 导出子集已验在案。FR-203 Turtle/项目包导出未实现/未验。首稿"当前无导出功能"表述错误，撤回 |
| 57 | 不适用→无法确认 | Z10-AUDIT-06：不给法律结论。代码事实保留：无服务端、无网络外发、数据全本地（本人核 CSP connect-src 'none'、无 HTTP 端口）；但"本地/无服务端"不能凭架构证明 GDPR 类法律义务不适用或不存在个人数据（用户可录入真实业务/个人性质内容）。组织/法律适用与履行未知，原 privacy/legal HOLD 保留；不新增 SaaS 功能 |
| 148 | 适用→无法确认 | Z10-AUDIT-03：指定双模型审查+ROOT 接收是**机制事实**（归 #133，维持适用）；"每行 AI 代码由资深人类工程师在发布前读过"是组织/人员义务，当前无证据其已履行——原项目保留 senior human 逐行签字/组织事实 HOLD。两项分开计档，#148 判无法确认；不因此新增合并门禁 |

## E. 判定维持（本人独立复核后）

补充核验与全文补读后：**维持 ConditionalPass**。理由更新：(1) 必要覆盖按三层如实闭合（A 节），补读未发现新的产品源码缺陷——6A/.dispatch 全文的写准入、终检、损坏 HOLD、跨会话与预算语义与首稿对产品代码的判读一致；(2) 四处清单重判均为判定/依据修正，不产生新的 push 前源码阻断；(3) R10-09 更正后仅余失效路径引用的维护观察；(4) 全部既有条件与 HOLD（完整平台 CI 三 job、case7 复发定因、67b7 状态登记归档 F05/F-R09-08、签名公证/法律供应链/跨 OS/容量/损坏库/未验家族等）原样保留；CI/merge 仍由 ROOT 另票，本报告不授权任何远端/预算动作。

（追加稿完；report 正文不内嵌自身终态 bytes/SHA，由 owner 另存实测。）
