# T02 FR-200／FR-201 fresh R11 整候选独立工程审查报告（MiniMax／M3.1-Flash／xhigh／始终授权）

## 0. 输入回执与身份核验（先行）

| 项 | 固定值（任务书） | 本方实测（`git rev-parse`／`git status`） | 结论 |
|---|---|---|---|
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | 同 | 符合 |
| branch | `feature/weekly-t02-fr200-fr201` | `feature/weekly-t02-fr200-fr201` | 符合 |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 该对象存在且为 commit | 符合 |
| head | `d1aca3e34ec4d00095c10a14a413efb552d3776a` | 同 | 符合 |
| tree | `389848f84fe60325bcdcd1b7827a7ee6e039a0e1` | 同 | 符合 |
| sole parent | `2d6bc23fdc4f13afcceb7b79c8059ee3c74abbe8` | `git rev-list --parents -n 1 HEAD` 只列该一个父 | 符合 |
| base→head 提交数 | 43 | `git rev-list --count` = 43 | 符合 |
| 差异路径 | 125 | `git diff --name-only` = 125 | 符合 |
| tracked 源叶 | 1403 | `git ls-tree -r --name-only HEAD` = 1403 | 符合 |

差异规模实测：`125 files changed, 32926 insertions(+), 380 deletions(-)`。

**工作区状态**：`M AGENTS.md` ＋ 未跟踪 `docs/reviews/T02/fr200-fr201-20261024/round-01/`、`round-02/`、`round-03/`。与任务书所述「只剩原保护 AGENTS overlay 与 round01/02/03 脏项」一致；index 为空，无本方未提交材料，无混入会话产物。

**原清单原件机器核验**（本方实测）：`ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt` = 11255B、SHA256 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c`、以 `> ` 开头的行 **160** 条、**末字节非 LF**。与任务书一致；下文 §4 的 1–160 严格按此 160 行逐行对齐，无缺行、无重复、无填充。

**本方模型与权限**：MiniMax M3.1-Flash／xhigh（非 max）／始终授权（完全访问）。本轮**只读**：未运行 check／vitest／pytest／build／package／install／formatter／HMR／产品 GUI／SQL／bridge，未制造故意业务失败探针；未改任何源码、测试、config、依赖、预算、忽略项、验收；未 `git add`／`commit`／`push`／切分支／触发 CI／merge；未新任务、未重置、未采购、未升级。**本方唯一写入**：本仓外 `outputs/20261027_t02_d1aca_fresh_r11_075/minimax/report.md`（本文件）及其目录创建。worktree 内未写任何新材料。

**独立性**：未读取另一作者本轮 R11 目录（`outputs/.../zcode/`）、报告、意见或 verdict；未读取任何非共同输入。两方接收的共同正文（`COMMON-NEUTRAL-FACTS-AND-SCOPE.md`）与完整原清单已读至 EOF。

---

## 1. 结论先行

**本人结论：ConditionalPass（附条件通过，限定为推送前技术审查阶段）。**

- **本候选 base `583c05c` → head `d1aca3e3` 的完整累计范围内，未发现当前 push 前的源码技术阻断。** 我亲读并核对了全部产品/契约/引擎/renderer/主进程/preload/CI 实现差异与新增测试、fixture、契约正文；逐项复核了 O072（CI43 真实失败）、O073（一字节归档修复）、O074（本轮两处观测修补）原件；逐项承接了 R10 的原 31／权威 78／R09 新增 19＋OBS／额外 13／Z Top9／MM Top10＋T11/T12。
- **这不是无条件整候选 Pass，也不是完整 CI 通过。** CI43（run 40406339836／attempt1／head `cfcc876e`）总体 failure 且 Quality／Windows 均失败；`d1aca3e3` 与 `2d6bc23f` **均未 push**，本候选**无任何新 CI**。合并门禁（完整三 job 逐 node／原有据 skip／自然 0／无失败早停取消 timeout NOTRUN／全部后继／Quality packaged recovery 自身 success）**未满足**，且不由本报告放行。
- **技术阶段有界可审 ≠ 完整产品放行。** 整体合并可用仍为 **2/17**；Goal／M0／发布未完成；全部独立 HOLD 与 UNKNOWN 原样保留，本轮**逐一关闭数为 0**。
- **本轮两处观测修补（O074）经我本人复核属实且范围受限**：它**只补测量与失败留证能力**，不修 Windows 异步 C1 根因、不修 FR201 累计超时。本机 C1 成功 → 新失败 catch 的真实平台附件**未被验证**，只有纯 mock 与静态证明。
- **历史 R10 两作者原 ConditionalPass 是历史限定技术判断**，ROOT 接收的是其逐项处置，**不是本轮 Pass**；本轮结论由我按当前源码独立重做。

**本方新增的、需 owner 决策的实质源码问题：1 项**（见 §2 的 `R11-S01`，P3 级，**非 push 前阻断**），另有 1 项对历史处置的事实订正（`R11-F01`，与 R10 限证一致但需指出 owner 侧表述口径）。

---

## 2. Top 真实最重要风险

> 说明：本轮**不足 10 项有实质独立价值的风险**。原因：CI43 的两个 E2E 失败与「完整平台 CI 从未在本候选通过」是**同一个已知门禁**的三个投影（分列以保留各自原归口），不构成新的独立风险；其余均为既有 HOLD 或维护观察。我按「真实最重要 + 不重复计数」给出 **6 项**，其中 3 项是既有门禁在当前候选上的**新事实更新**（CI43 已实际发生并给出新的可核终态），3 项是维护/可追溯性观察。

### R11-T01｜完整平台 CI 在当前累计候选上仍为 failure；本候选无任何新 CI（合并门禁，最高）

- **严重性**：高（合并门禁，非源码缺陷）
- **触发**：任何 merge 动作
- **代码定位**：`.github/workflows/ci.yml`（base→head 累计变更，含 Windows 分支 `engine:check` 降级为 diagnostic、新增 `CI_ENGINE_TEST_SHARDS='2'` 双进程计账、`PLAYWRIGHT_JSON_OUTPUT_FILE` 报告落盘、制品上传范围扩大为 `build/engine-tests/`＋`test-results/`）
- **原件依据**：O072 `DIAGNOSIS-AND-BOUNDARIES.md`（本人亲读全文）与 `COMPLETION.json`——run `40406339836`／attempt1／head `cfcc876e`／conclusion `failure`；Quality job `121864949262` failure（lint 成功→globalPrettier 仅 `docs/m0-checklist.md` 告警 exit 1 → 后续 steps 9–18 全 SKIPPED，**完整 3769 = NOTRUN**；先行 I04 独立 matrix 144 PASS **不是**完整 suite）；Windows job `121864948440` failure（E2E 24 ordered = 19 PASS／3 原 I04 SKIP／**1 failed(C1)**／**1 timedOut(FR201)**，typecheck/build 成功，package/verify SKIPPED）；macOS job `121864949172` success（24 = 21 PASS／3 原 I04 SKIP；engine 3769 仅完整 log 汇总，ZIP 无 collection/events，**不冒逐 node 资格**）。
- **影响**：合并门禁未开。`2d6bc23f` 与 `d1aca3e3` 未 push，本候选无回单。
- **最小建议**：由 ROOT 发精确 push/CI 票；接收标准维持原 15/20 分钟、逐 node／原有据 skip／自然 0／零失败早停取消 timeout NOTRUN／全部后继／Quality packaged recovery 自身 success／三 job 实际 success。**不在本报告授权任何 push、rerun、cancel、merge。**
- **当前 push 前源码阻断**：**否**（门禁条件，非源码缺陷）

### R11-T02｜CI43 Windows C1 为真实失败且异步根因仍 UNKNOWN；O074 的新 catch **未被真实平台触发**（HOLD）

- **严重性**：中（未证根因 HOLD）
- **触发**：Windows CI 上 `C1 real CSP, normal functionality and renderer recovery`
- **代码定位**：`tests/e2e/csp-lifecycle.spec.ts:278-341`（本轮新 catch）、`tests/e2e/native-driver.ts:103`（child close cause）／`:284`（catch/stdio drain 再包装）
- **原件依据**：O072 `INDEPENDENT-WINDOWS-C1-DIAGNOSIS.json`——真失败 **13086ms**（原 90s 未耗尽）；`readinessAttempts=1`、`bootstrapComplete=true` 表明首 ready 与原 helper 同步 require/evaluate **已成功**，其后 `finished` 收到 native child close `1/null`；`nativeStageSpanMs=6334.895` **只围住 native 阶段，不是 PID 寿命**；ZIP **无 native.json 成员**；Windows **不设 I02_EVIDENCE**，故旧 catch 的 read/parse 错误被吞、整体 evidence 未附。O074 `C1-INDEPENDENT-BOUNDARY-REVIEW.json`：`verdict=PASS_STATIC_AND_PURE_MOCK_BOUNDARY_ONLY`，14 场景纯 mock 全过，`blocking=[]`。
- **影响**：**不能**把 O074 的新 catch 说成「Windows C1 根因已修」或「真实平台失败附件已验」。O074 `COMPLETION.json` `limits` 自陈 `C1ActualFailureCatchTriggered=false`、`C1RawFileFailureAttachmentProvenOnPlatform=false`、`C1MockIsProductProof=false`、`WindowsAsyncCause=UNKNOWN`。原失败**保留**。
- **最小建议**：下一获准的完整 Windows CI 才产生该平台样本；届时按新 catch 落盘的原字节／read/parse/attach 结果定位。**不猜异步原因**（raw inspector WS 未记录）。
- **当前 push 前源码阻断**：**否**（HOLD）

### R11-T03｜CI43 Windows FR201 整例 180002ms 超时，末权威业务终态未知（门禁条件，根因 UNPROVEN）

- **严重性**：中（门禁条件 + 未证根因）
- **触发**：Windows CI 上 `FR201 UI relations and multivalue manual records keep original IDs…`
- **代码定位**：`tests/e2e/t02-fr200-fr201.spec.ts`（本轮在 5 处 `expect.poll` 外包 `observedPoll` 计时层，**不改原 callback/options/comparator**）、原 180000ms 预算与 5s poll 未改
- **原件依据**：O072 `INDEPENDENT-WINDOWS-FR201-DIAGNOSIS.json`（本人复核）——最后完整为 **rev21** 对原 ID `45a9ed263193…` 的删除；首个 commit poll **2.823495s** 成功、显式 reconcile、严格 receipt poll **0.595566s** 成功，marker/Job/2 次 freshRead/状态断言均完成；接着载入原 ID `1f966c9aa7f8…`（`"原始中文"@zh`）并 preview 成功，**Diff visible 等待起 179525.790ms，仅余 474.210ms 名义余量**，**未进入第 22 笔 confirm/poll**。最终 freshRead 为 rev21；内部旧 receipt 20 不是终态。43 拒绝 Read 不变已证；**全正向 Evidence 数组未到最终附件** → 不冒 22/57 完整导出、不编造第 21 笔完整 payload/JobID。case7 当轮 PASS 5495ms。
- **时间口径（本人核对原件数值）**：显式桥接 237 次共 52.375424s；纯 DOM 848 次共 10.284072s；matcher 339 开始/338 完成，区间并 37.050665s；UI 动作 337 次共 9.161099s；poll 容器 165 个总跨度 78.569318s（含子项），残余 68.50865s **不是纯 CPU 或睡眠**；已完成 commit-helper 21 个共 68.593489s **不叠加**。disjoint 合计正好 180000ms。最长完成 poll 3.520654s < 5s，**无单次巨 stall 证据**。
- **影响**：本轮新增计时层**只提供测量能力**，不构成性能结论，也不修累计超时。O074 自陈 `WindowsFR201CumulativeTimeoutFixed=false`、`newTiming="measurement only, no measured performance improvement claim"`。wall 校时不可把 worker perf 直接当 trace clock，**不能分解引擎 CPU/IPC 或量化提速**。
- **最小建议**：未来完整 CI 以新 annotation 的 5 phase×19 字段作定位输入；**保持原 180s 预算、原 22 事务、原 43 拒绝、原完整 Diff、原原 ID 编辑、原所有 freshRead/marker/Job 断言不变**（O074 已保，本方独立复核成立）。
- **当前 push 前源码阻断**：**否**

### R11-T04｜`storage.py` 冲突见证的「首个阻断行／前两条记录」缺确定性排序（F15／R06 Z P6／R04 Z01／R05 MM08／R06 MM08）

- **严重性**：低（未确认观察，不升级为缺陷）
- **触发**：同一 slot 存在**并列**多条候选事实时（GROUP BY 计数 >1 或 LIMIT 2 取到并列行）
- **代码定位**：`packages/engine/src/ontolearn_engine/storage.py:1151`（`GROUP BY subject HAVING COUNT(*)>1 LIMIT 1`）、`:1170`（`… LIMIT 2`）——**本方本人实测：两处至今均无 `ORDER BY`**（base→head 累计未改这两行的排序）
- **原件依据**：`round-10/disposition.md:216`（F15）、`:254`（R06 Z P6）、`:269`（R04 Z01）、`:298`（R05 MM08）、`:341`（R06 MM08）均记为「仍开（未确认观察），无构造性反例不升级」
- **影响**：极端并列下冲突定位 witness 不可复现。当前是**新增的 `SingleDeclarationConflict` 取前两条记录**（本轮 `storage.py` 新增该 Conflict 类，`_validate_single_slots` 在声明者仍持该谓词时抛 `SingleDeclarationConflict(identity, predicate, group[0], rows)`），使该观察从「无实际消费者」变为「有实际消费者」，但**仍无构造性反例**，按原纪律维持未确认观察。
- **最小建议**：T01 下次触及 witness 选取时加确定性排序；**本轮不改码**。
- **当前 push 前源码阻断**：**否**

### R11-T05｜`packages/contracts/src/index.ts:894-896` 的 `OwnershipDetailArgs` TS 类型宽于运行时 schema（R10-03／Z09-05／MM R07-13）

- **严重性**：低（维护，双源漂移风险）
- **触发**：调用方在 TS 侧构造越界 `startOrdinal`/`pageSize`
- **代码定位**：`packages/contracts/src/index.ts:894-896`（**本人亲读实测在位**）：

  ```ts
  export type OwnershipDetailArgs =
    | { detailRef: string; documentHash: null; startOrdinal: 0; pageSize: number }
    | { detailRef: string; documentHash: string; startOrdinal: number; pageSize: number }
  ```

  第二变体的 `startOrdinal`／`pageSize` 为宽 `number`，而 schema 侧有界（≤511／1–64）。
- **原件依据**：`round-10/disposition.md:215`（F14 → R10-T09）、`:248`（MM R07-13）、`:313`（Z09-05）；`:354`（R10-03）
- **影响**：TS 类型**不拦**越界值，仅运行时 zod 拦截；属类型与 schema 双源漂移的维护风险，非功能缺陷。运行时拦截实测在位（`packages/contracts/v2/schema.json` 本轮新增 `params_project.ownership.detail`／`result_project.ownership.detail`／`ownershipDetailDocument` 三组定义，**本人亲读**）。
- **最小建议**：契约 owner 下次整理类型时收敛为字面量区间类型；**本轮不改码**。
- **当前 push 前源码阻断**：**否**

### R11-T06｜R11-S01：`mainline-ownership.ts` 的分页循环上限 512 页与 `pageSize` 固定 64 在 16MiB 文档上界可达（可追溯性/边界观察，P3）

- **严重性**：低（P3，未证明当前可达）
- **触发**：单个 ownership 详情文档接近 `MAX_DOCUMENT`（16MiB）上限时
- **代码定位**：`apps/desktop/src/renderer/src/ontology/mainline-ownership.ts:26`（`for (let count = 0; count < 512; count++)`）、`:33`（`pageSize: 64` 固定）；引擎侧 `packages/engine/src/ontolearn_engine/project/domain_changesets.py` 的 `MAX_DOCUMENT = 16 * 1024 * 1024` 与 `SEGMENT_BYTES`（32768）
- **本人实测推算（本轮新增，非复述任何旧报告）**：引擎分段固定 32768B/段，故 16MiB 文档最多 512 段；renderer 每页取 64 段 → 需 8 页即取完，**512 页上限远大于实际所需**。同时 `reassembleOwnershipDetail`（`packages/contracts/src/index.ts`）以 `pageSize: 64` 硬编码校验每页段数 ≤64。故**当前路径不存在分页耗尽**；真正的边界在**单页字节量**：引擎 `ownership_detail_page` 以 `canonical(result).encode() + 1024 > min(maxPageBytes, maxFrameBytes, 262144)` 决定是否收段，单段 base64 后约 43.7KB，64 段约 2.8MB，**会被该上限截断为更少段数**，客户端 `pageSize: 64` 只是上限不是下限，引擎按字节上限贪心收段 → 逻辑自洽。
- **影响**：**未证明当前不可达**，亦**未证明可达**。属「按需复核的真实边界观察」，不构成缺陷。与 R10-T05（annotation 16KiB 兜底分支无二次长度复核）**同族但不同对象**，不合并计数。
- **最小建议**：若 owner 未来触及 ownership 详情分页常量或文档上限，按原 T02 契约归口复核「段数×页大小×页数」三者一致性；**本轮不改码、不新增门禁**。
- **当前 push 前源码阻断**：**否**

---

## 3. 本人实际审读范围与来源区分（不夸大覆盖）

### 3.1 本人亲读全文（逐行，读到 EOF）

**需求依据**：`AGENTS.md`（101 行全文）｜`docs/prd/PRD-本体学习与落地Agent工作台.md` 的 §0–§1、§7.3（FR-200/201/202/203/204）、§7.4–7.11 标题、§10–§12 标题、**附录 C（能力矩阵全表）**、**附录 D（D.1/D.2 全表）**、**附录 E（E.2/E.3/E.4/E.5 全节）**、附录 F 标题、**附录 G（G.0–G.6 全表）**｜`docs/architecture/0001-desktop-framework.md`（全文）｜`docs/iterations/I01/ADR-0002-storage.md`（全文，含 Round 1/2/3 证据补强）｜`docs/architecture/0003-resident-coordinator-and-jobs.md`（全文）｜**M0 更新计划全文（35812B）**：实际原件在 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 与 `docs/reviews/I03/inputs/` 两处，**两份 SHA256 均为 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`** —— AGENTS.md 引用的 `docs/architecture/m0-review-and-update-plan-2026-10-19.md` **路径确实失效，但该计划已有两份同 SHA 的版本化副本在树内**（本人实测），故「整计划未版本控制」不成立｜`docs/m0-checklist.md`（全文，含 R04–R10 追加段）｜`docs/reviews/T02/status.md`（全文，116 行追加段全读）。

**本轮实现差异（base→head，累计 43 提交）**：
- 契约层：`packages/contracts/src/v2.ts`（新增 `ownershipSha256` 纯 JS SHA-256 与 `matchesOwnershipDetail` 全量）｜`packages/contracts/src/index.ts`（新增 `OwnershipDetailArgs/Page/Document` 类型与 `reassembleOwnershipDetail` 全量）｜`packages/contracts/python/contract_v2.py`（新增 `ownership_detail_matches` 全量）｜`packages/contracts/v2/schema.json` 新增三组定义块（本人读新增段）。
- 引擎：`packages/engine/src/ontolearn_engine/project/mainline.py`（新增 `_WriteAdmission`、`_WriteScope`、`_WriteHolding`、`prepare_mainline_store`、`_OwnershipProof` 与 `MainlineHost.ownership_proof` 全量）｜`storage.py`（新增 `ManualOwnershipConflict`、`SingleDeclarationConflict` 两类与 `_check_slot`／`_validate_single_slots`／edits 分支差异全量）｜`project/project_host.py`（新增 `MaterialProfile`、`material_profile`，`_preflight` 改为薄封装）｜`project/domain_changesets.py`（`preview_changeset` 新增 `ownership_proof` 与 direct-caller 词法拒绝）｜`job_store.py`（新增 `_ownership_proof/_ownership_json/_ownership_header/_ownership_segment/_persist_ownership_detail/ownership_detail_page` 与 `_transaction` 准入包装）｜`coordinator.py`｜`rdf_snapshot.py`｜`project/query_presentation.py`（差异要点全读）。
- 渲染端：`mainline-ownership.ts`（**新增全文 78 行**）｜`OwnershipConflictDetailView.ts`（**新增全文 105 行**）｜`mainline-facts.ts`｜`mainline-session.ts`｜`mainline-api.ts`｜`OntologyMainlinePage.tsx`｜`OntologyPage.tsx`。
- 主进程/预载：`desktop-ipc.ts`｜`project-mainline-service.ts`｜`preload/index.ts`｜`engine.ts`。
- 工程与脚本：`.github/workflows/ci.yml`｜`package.json`｜`pyproject.toml`｜`packages/engine/pyproject.toml`｜`scripts/run-engine-tests.py`（**全文 470 行**）｜`scripts/engine-test-reporting.py`（**全文 124 行**）。
- 测试：`tests/e2e/ui-observation.ts`（**新增全文 195 行**）｜`tests/e2e/csp-lifecycle.spec.ts`（本轮 d1aca3e 提交差异全量）｜`tests/e2e/t02-fr200-fr201.spec.ts`（本轮 d1aca3e 提交差异全量，488 行）｜`tests/e2e/native-driver.ts`（差异前段全读）｜`tests/unit/t02-manual-fact-id.test.ts`（**全文 186 行**）。

**本轮输入原件**：O072 `DIAGNOSIS-AND-BOUNDARIES.md`（**全文**）｜O072 `COMPLETION.json`（本人读关键字段）｜O073 `COMPLETION.json`（**全文**）｜O074 `COMPLETION.json`（**全文**）｜O074 `C1-INDEPENDENT-BOUNDARY-REVIEW.json`（关键字段全读）｜O074 `FR-INDEPENDENT-BOUNDARY-REVIEW.json`（**全文**）｜O074 `BUILD-REBUILD-MAPPING.json`（关键字段）｜O074 `STATIC-PRESERVATION-02.json`（**全文字段**）｜O074 `source-format-result.json`／`source-format.stdout`（**全文**）。

**历史归档**：`round-10/disposition.md`（**全文 391 行**，逐段读至 §统一事实限证）｜`round-10/minimax-m31flash.md`（本人前轮原稿：§0、§2 Top10、§4.1 逐项表 1–160、§4.2、§10.3–§10.7、§11.3–§11.4 全读）｜`round-09/disposition.md`（经子代理定位后本人复核 R09 新增 19＋OBS 与额外 13 段）｜`round-10/version-map.json`／`artifact-manifest.json`（经子代理定位后本人复核关键段与计数）。

### 3.2 差异级（读该路径完整差异，未逐行读全文）

`tests/e2e/native-driver.ts` 后段｜`packages/engine/src/ontolearn_engine/coordinator.py`｜`rdf_snapshot.py`｜`project/query_presentation.py`｜`packages/contracts/v2/registry.json`｜`binding-regressions.json`｜`fixtures.json`（增量）｜`licenses/NOTICE`｜`uv.lock`｜`tests/unit/*` 其余 12 个改动文件｜`packages/engine/tests/*` 7 个新增测试文件｜`tests/fixtures/t02-manual-fact-id.json`｜`packages/engine/vendor/rdflib/*`（二进制与许可，按来源 hash 与 PROVENANCE 核）。

### 3.3 子代理定位 + 本人复核

本轮调用 **2 个内部只读子代理**（`explore` 角色），其结论一律不直接采信，全部关键结论由本人回到原件逐条复核：

| 子代理 | 产出 | 本人复核方式与结果 |
|---|---|---|
| 子代理 A（历史意见定位） | round-04…round-10 disposition 全文抽取、四张表的稳定 ID／主题／owner/窗口、R10 两方 Top 与 T11/T12 主题、每表行数与分布 | 本人亲读 `round-10/disposition.md` 全文（391 行），逐表核对行数与 ID 集合；亲读 R10 原稿 §4.1/§10.3–10.7/§11.3；**并纠正其一处前提**：它指出「额外 13（R06 MM01–13）」与「MM 160 清单末 13 行（#148–#160）」是两个不同集合——**该纠正成立且已由本人以 `disposition.md:15` 原文与 R10 原稿 §11.3(a) 双向核实** |
| 子代理 B（O072/O073/O074 定位） | 三目录文件清单与哈希、CI43 三 job 逐项数字、时间诊断表、434/487 检分类、build 映射、首败记录 | 本人亲读 O072 `DIAGNOSIS-AND-BOUNDARIES.md` 全文、O073/O074 `COMPLETION.json` 全文、O074 两份独立评审 JSON、BUILD-REBUILD-MAPPING、STATIC-PRESERVATION-02；**并对子代理提出的「074 曾对 FR 文件执行 prettier --write、可能超出手写 patch」这一观察做了实测**（见 §3.5 结论） |

### 3.4 原件核对（本人实测）

| 事实 | 本人实测方法与结果 |
|---|---|
| 原清单身份 | `python3` 读 `ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt`：11255B／SHA256 `1ca23def…f709c`／`> ` 行 **160** 条／末字节非 LF —— 全部符合 |
| 2d6 与 d1aca 两文件 blob | `git show 2d6:<path> \| shasum -a 256` = O074 `before-source/` 对应值（FR `3e69c4d9…`、C1 `3c8dc2a7…`）；`git show d1aca:<path>` = O074 提交后源值（FR `a5c9dd02…`、C1 `fea56451…`）—— 逐字一致 |
| O074 `committed.diff` 与 Git 实际差异 | 两者 hunk 结构完全相同（C1 1 个 hunk + FR 8 个 hunk，`@@ -79,6 +79,235 @@` 等），`--numstat` FR 为 `360 128`，与 `committed.diff` 标注一致 |
| `csp.ts` base→head | `git diff --stat` **为空** —— 本候选未改 CSP 配置源；`unsafe-inline` 仅在 `csp.ts:20` 开发 HMR 分支（带注释 production uses local CSS） |
| `storage.py` 无序查询 | `grep` 实测 `:1151` `GROUP BY subject HAVING COUNT(*)>1 LIMIT 1`、`:1170` `… LIMIT 2`，**均无 ORDER BY** |
| 两处裸 PATH python | `grep -rn "execFileSync('python'"` 实测命中 `tests/unit/t01-mainline-contract.test.ts:656` 与 `tests/unit/t01-ontology-metadata-contract.test.ts:168` |
| `OwnershipDetailArgs` 宽类型 | `packages/contracts/src/index.ts:894-896` 实测在位（见 R11-T05） |
| 九规则参数化断言（R10-T12 关键事实） | **本人亲读** `packages/engine/tests/test_storage.py:190-223`：`@pytest.mark.parametrize("rule", RULES["rules"], ids=…)` 动态遍历**全部 9 条**规则并对每条做正反断言（stale 原因／无关项不 stale／reasons({key:1},{key:1})==[]）。**「仅 3/9 有断言」不成立** |
| Python 机器交叉核验（R10-T09 关键事实） | **本人亲读** `tests/unit/t02-manual-fact-id.test.ts:53-76`：`spawnSync(resolve('.venv/bin/python'), ['-I','-c', pythonCheck, …])` 调用真实 `Store._fact` 与 `digest`，逐条比对 golden 的 `record['id']==digest(values)` 与 `canonical` 输出 —— 机器校验**真实存在**（显式路径，非裸 PATH） |
| M0 计划版本化 | 两处原件 SHA256 均 `c289a1cd…`，35812B，**已版本化** |
| 读侧审计 / 键盘可达 | `grep` 读侧审计相关标识 **0 命中**；`grep tabIndex\|onKeyDown` renderer **0 命中** —— 支撑 §4 的 #55／#129 判定 |
| 备份面 | `storage.py:1839 def backup(self, destination)` 存在（SQLite 在线备份、禁覆盖目标），但**无 restore 实现** —— 支撑 §4 的 #20 判定 |

### 3.5 本方新增的一处独立复核（子代理观察的裁决）

子代理 B 提出：「074 对 FR 测试文件执行过 `prettier --write`（stdout 无 `(unchanged)` 标记），最终提交 blob 可能包含超出手写 patch 的格式化内容」。**本人实测裁决：此观察的前提成立，但结论不成立。**

- 前提成立：`074/source-format-result.json` argv 确为 `prettier --write` 两文件；`source-format.stdout` 记 `t02-fr200-fr201.spec.ts 92ms`（**无 `(unchanged)`**），而 C1 文件为 `(unchanged)`。故 FR 文件确被 prettier 改写。
- **结论不成立**：本人对比 `074/committed.diff` 的 9 个 hunk 与 `git diff 2d6bc23f d1aca3e3` 的 9 个 hunk，**hunk 头逐字相同**（`@@ -79,6 +79,235 @@`、`@@ -168,27 +397,27 @@`、`@@ -223,61 +452,61 @@`、`@@ -783,6 +1012,7 @@`、`@@ -880,29 +1110,29 @@`、`@@ -925,41 +1155,41 @@`、`@@ -1751,6 +1981,7 @@`、`@@ -1909,6 +2140,7 @@` ＋ C1 `@@ -278,10 +278,65 @@`）。即：**提交内容 = 本轮授权的两处改动**，prettier 规范化只作用于新增代码本身，**未越出授权范围，未改动任何原断言、timeout、title、named bridge 或业务 callback**（STATIC-PRESERVATION-02 实测：C1 39→39、FR 133→133，namedBridge 1→1／9→9，timeout exact，title exact，`nativeInvocation` exact）。
- 结论：**不构成需 owner 决策的实质源码问题**，记为已核事实（`R11-F02`）。

### 3.6 真正未覆盖（本报告不声称的部分）

1. **未运行任何测试/构建/打包**：本方未跑 `npm run check`、`vitest`、`pytest`、`package:dir`、`verify:sources`、`npm run format:check`、HMR 探针、产品 GUI、SQL、bridge。§2 与 §4 引用的全部执行数字均**标明既有原件身份**（O072／O073／O074／O069 等），**不冒本人运行**。
2. **未读全文的新增/修改测试文件**：`packages/engine/tests/` 7 个新增测试（合计约 4742 行）、`tests/unit/` 12 个改动文件（`t02-mainline-consumer.test.ts` 1709 行、`t02-ownership-detail.test.ts` 843 行、`t02-manual-preview-lifetime.test.ts` 596 行等）。这些文件的**断言内容与覆盖面**未由本人逐行复核；本报告对它们的引用限于「文件存在、行数、差异级已读」及其中被点名的具体片段（如 `test_storage.py:190-223`、`t02-manual-fact-id.test.ts`）。
3. **未做跨平台/打包/生产验证**：Windows、Linux、干净设备、参考 8GB 设备、无开发环境离线启动、签名与公证，**均无本方样本**。
4. **未核 R08/R09 原稿的每一行**：R09/R08 原件经子代理定位、本人复核其 disposition 的相关段；未逐字重读 `round-08/minimax-m31flash.md`（1100 行）与 `round-09/minimax-m31flash.md`（1516 行）全文。
5. **未读另一作者本轮 R11 任何产物**（按职责要求）。
6. **未验证 CI43 的原始日志行**：本人读的是 O072 的诊断/边界原件与摘要字段，**未**回到 `windows-terminal.log:8326-8344`／`:8358-8361` 与 `quality-terminal.log:411-417` 的原始行逐字复核；这些行的存在与数值系**转述** O072 原件。
7. **未验证 O074 的 434／487 检**：二者为独立评审 agent 的结论（转述），本人只核了其在 JSON 中的字段与分类计数，未重算。

---

## 4. 原 160 项清单逐项判定

**编号基准**：严格逐行对应 `outputs/20261027_t02_d1aca_fresh_r11_075/ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt`（11255B／SHA256 `1ca23def…f709c`／末字节非 LF）的 160 条 `> ` 行，顺序与文案一一对应。**本人已机器核验**：160 行、min 1／max 160、无缺号、无重复。

**判定用词**：适用／部分适用／不适用／无法确认。**复合判定自成一档、只计一次**——每行只出一个档位、只计一次。**适用性不等于产品通过数**：判「适用（正面）」只表示该风险面在本产品形态下被正面覆盖，不代表对应能力已完整交付。

**本轮相对 R10 的变更**（逐条说明见下）：#31、#32、#33、#48、#49、#57、#96、#97、#108、#135、#136、#146、#153、#156、#158 等项的**当前依据随本轮新增实现/证据发生变化**；其余项沿用经本方按当前源码复核后的判定。

| # | 判定 | 当前依据 |
|---|---|---|
| 1 | 不适用 | 本产品是本体/RDF 建模工作台，不是多表关系型 SaaS；本体结构由 `packages/contracts/v2/schema.json`（本轮新增三组定义）与 PRD 附录 C 能力矩阵定义，非逐表即兴。 |
| 2 | 不适用 | 无邮箱登录体系；本地单机，无账号密码面。 |
| 3 | 不适用 | 无密码重置流程。 |
| 4 | 不适用 | 无 MFA、无手机/设备恢复路径。 |
| 5 | 不适用 | 无账号会话。进程内 `OntologySession` 由 `dispose()`／`#retired` 管理，本轮 `mainline-session.ts` 另加 `ownershipDetail` 清理（`dispose()` 内清空），属会话级资源回收，非账号会话超时。 |
| 6 | 不适用 | 无企业 SSO 诉求证据；本地优先、不自动启用云服务。 |
| 7 | 不适用 | 无 SAML。 |
| 8 | 不适用 | 无 SCIM／员工目录。 |
| 9 | 部分适用 | 有**能力注册表 + 方法级 allowlist**（`packages/contracts/v2/registry.json`、`packages/engine/src/ontolearn_engine/project/mainline.py` 的 `METHODS` 集合本轮新增 `project.ownership.detail`、`apps/desktop/src/main/engine.ts` 按方法分派并对 `project.ownership.detail` 施加 `params.projectId !== record.selected?.projectId` 校验）。比二元 admin 细，但不是用户角色体系。 |
| 10 | 不适用 | 无多用户 URL 资源 ID 面；`projectId` 有 UUID 格式校验与 public/internal 映射。 |
| 11 | 不适用 | 单租户本地应用。 |
| 12 | 不适用 | 无 impersonation 语义。 |
| 13 | 不适用 | 无登录面，故无登录限速。 |
| 14 | 不适用 | 无账号锁定。 |
| 15 | 部分适用 | `storage.py` 有 `FORMAT_VERSION = 2`（本人实测）与 `user_version` 门禁、v1→v2 事务升级（`:233`/`:293`）、未来格式拒绝打开；**未见可回滚的降级迁移路径**（M0 计划亦把人工 schema 降级列为未验）。**本轮变更**：ADR-0002 原文与 `m0-checklist` 未变，判定不变。 |
| 16 | 不适用 | SQLite 单文件本地库，无在线并发迁移场景。 |
| 17 | 部分适用 | 有 `facts`／`snapshots`／`job_details` 等表与 `ORDER BY id`；但 Q5 容量目标与参考设备**未确认**，容量属独立 HOLD。 |
| 18 | 不适用 | 无连接池（本地单连接）。 |
| 19 | 部分适用 | **本人实测（复核 R10 上调成立）**：`storage.py:1839 Store.backup(destination)` 存在（SQLite 在线备份，目标必须为新文件），`storage.py:209` 在格式迁移前调用 `project/format3.py` 的迁移备份钩子。但**备份是用户手动调用，无「每晚」调度**（本地库无服务端作业）。故能力面在、调度面不适用，取部分适用。 |
| 20 | 部分适用 | **本人实测（复核 R10 上调成立）**：`packages/engine/src/ontolearn_engine/project/transactions.py:285 preview_restore(project, snapshot)` 提供**快照级恢复/预览**，`packages/engine/src/ontolearn_engine/project/compensation.py` 提供提交内补偿选择与校验（`:39/:48/:151`），`storage.py:626/707/710/868-876` 在提交路径调用补偿。但**没有「从备份文件做整库恢复」的已实现路径**，也未测。取部分适用。 |
| 21 | 不适用 | 无 PITR。 |
| 22 | 不适用 | 无软删除 UI 概念。引擎的 `object IS NULL` 是**受管事实墓碑**（所有权标记），非软删除功能。 |
| 23 | 部分适用 | 校验在引擎侧执行：`storage.py` `_fact()`、`_check_slot`、本轮 `domain_changesets.py` 新增对 `manual`/`edits` 的 `iri()`＋`term(value)`＋`parsed.n3() != value` 词法拒绝（本人读差异全文）；前端仅预检。**但客户端仍存在**歧义判定**（见 R10-T10，本方复核该推断已被 R10 撤回为可选注释澄清）。 |
| 24 | 不适用 | 无用户时区／提醒排程。 |
| 25 | 适用（正面） | N3 字面量与 IRI 按 canonical 处理；`rdf_snapshot.py` 的 `term()` 决定输出，golden 含 `"泵站A"@zh`、含转义引号字面量。 |
| 26 | 部分适用 | 引擎层 Unicode 与语言语义已覆盖：`storage.py` canonical `ensure_ascii=False`，`mainline-facts.ts` 本轮新增孤立代理项拒绝（`0xd800–0xdfff` → `INVALID_FACT`，本人读差异全文），`packages/engine/tests/test_mainline_language_input_rejection.py` 覆盖 `@en-001`／`@de-ch-1901`／大小写子标签与数字子标签（**本人实测该文件无 emoji/RTL 显式用例**）；`t02-manual-fact-id.test.ts` 有 NFC/NFD 区分向量（本人亲读）。**缺口**：无 emoji/重音/RTL 的端到端字段用例，故由「适用（正面）」取部分适用。 |
| 27 | 不适用 | 无金额存储。 |
| 28 | 不适用 | 无货币／税。 |
| 29 | 部分适用 | 分层数据模型（本体定义／断言事实／映射状态／快照／历史）已成形；本轮新增 ownership 冲突**双端定位**（typed witness → `detailRef` → 分页字节流 → 视图），是「第二个客户的小改动」方向上的正面进展；但无第二客户证据，未覆盖全部附录 C。 |
| 30 | 不适用 | 无支付。 |
| 31 | 部分适用 | **本轮变更**：事实层有**内容派生 ID**（`newManualFactPlan` 本轮改为 `SHA-256(JSON.stringify([S,P,O]))`，本人读差异全文），具备天然幂等；但**支付幂等键**语义面不存在，且归属「重复提交去重」的最贴近替身是事实 ID 幂等。取部分适用。 |
| 32 | 部分适用 | **本人实测（复核 R10 上调成立）**：`packages/engine/src/ontolearn_engine/project/query_presentation.py:381` 对 `params["pageSize"] > min(200, limits["maxPageItems"])` 直接拒绝，`:128/130/232/443` 以 `RESOURCE_LIMIT` 拒绝越界页，`:354` 计算页帧预算 → **有界分页在位**。无「第 400 页」的用户分页列表产品面（该面未实现），取部分适用。 |
| 33 | 部分适用 | **本人实测（复核 R10 上调成立）**：`apps/desktop/src/renderer/src/query/QueryResultPanel.tsx:16-17` 的 `downloadCsv` 生成带 BOM（`\uFEFF`）的 `text/csv;charset=utf-8` Blob，`:250/:317` 两处触发 → **有限 CSV 导出在位**。但 FR-203/FR-1000 的本体/项目包导出与完整数据导出未实现，取部分适用。 |
| 34 | 不适用 | 无 CSV 导入。 |
| 35 | 不适用 | 无保留期／自动删除策略。 |
| 36 | 适用（正面） | 仓库无凭据；AGENTS 禁止提交凭据/`.env`/`.mimosa/`；`safeStorage` 属 S3 范围，**当前未接入任何模型凭据**。 |
| 37 | 不适用 | 无生产密钥轮换面。 |
| 38 | 部分适用 | 依赖版本精确锁定（`packages/engine/pyproject.toml` 本轮把 rdflib 改为 `7.6.0+ontolearn.fr201.3` ＋ `[tool.uv.sources]` 指向 vendored wheel，`uv.lock` 同步）；但 rdflib 是**本地改版 wheel**，其「正是你要的」依赖 PROVENANCE（见 R10-T07／F18）。 |
| 39 | 部分适用 | `licenses/NOTICE` 有许可清单，vendored wheel 有 LICENSE＋PROVENANCE；**未见依赖漏洞扫描配置**（本人实测 `.github/dependabot.yml` 仅 root npm／github-actions **weekly** 两项，无 SLA/EOL 核验、无第三方扫描器）。 |
| 40 | 适用（正面） | 输入面是 IRI 与 RDF 字面量；引擎 `rdf_snapshot.py` 的 `iri()`/`term()` 拒绝非法语法，本轮 `domain_changesets.py` 进一步对**直接调用方词法**做 `parsed.n3() != value` 拒绝（未知 parser/N3/Store 失败仍保留 UNKNOWN/HOLD，未泛捕 ValueError）。 |
| 41 | 部分适用 | SQL 全部参数化；动态表名来自 `sqlite_master` 并做 `'"' + table.replace('"','""') + '"'` 转义（**本人实测** `storage.py` 与 `project_host.py` 各 2 处 `sqlite_master` 动态构造）；无浏览器网络面故无 XSS/CSRF；CSP 由 `apps/desktop/src/csp.ts` 单一来源，**本人实测 base→head 该文件无差异**，生产脚本无 `unsafe-inline`/`unsafe-eval`（唯一 `unsafe-inline` 在 `csp.ts:20` 开发 HMR 分支，带注释）。**缺口**：本候选无 OWASP 清单逐项回归证据面，故取部分适用。 |
| 42 | 不适用 | 无用户文件上传面。 |
| 43 | 适用（正面） | 本地应用无跨源网络面；`apps/desktop/src/main/index.ts` 用 `loadURL(devURL)`/`loadFile(rendererPath)`；preload **本轮新增** `getOwnershipConflictDetailPage` 仍是**按业务命名的方法**，无 `invoke(method, params)` 通用通道（本人读差异全文）。 |
| 44 | 适用（正面） | 桌面本地加载不经 HTTP 服务器；等价安全职责由 CSP＋窗口隔离＋IPC sender/mainFrame 校验承担。 |
| 45 | 不适用 | 无传输加密面（本地 stdio＋本地文件）；静态加密属 S3 未接入。 |
| 46 | 部分适用 | 模型外发网关属 S3，**未接入任何模型凭据**。已实现的最小权限：`_OwnershipProof.check()` 校验 owner/store/connection/lease/project/generation/reply 同一性，`_WriteAdmission.check_store()` 校验 store 同一性，renderer 无 Node/文件系统能力。 |
| 47 | 适用（正面） | 落盘仅固定集 `{"category","resource","projectId"}`（本人读 `storage.py` 差异全文）；`ManualOwnershipConflict` 的 locator 仅 `id/owner/sourceRow/slot`，**不含 object 原值**；本轮新增的 ownership 详情文档同样只含 locator 与哈希/字节流，**不回传原始异常、路径、单元格原值**。 |
| 48 | 无法确认 | 渗透测试属组织流程事实，代码不能判定；本候选无渗透测试证据。 |
| 49 | 部分适用 | 本地优先、无云、无账号，问卷面极小；但本方**不能**代答第三方审计问卷，亦无既有问卷答复原件。 |
| 50 | 不适用 | 无对外服务，无漏洞披露流程。 |
| 51 | 不适用 | 无生产访问设备失窃场景。 |
| 52 | 不适用 | 无 SOC 2。 |
| 53 | 不适用 | 无 HIPAA／患者数据。 |
| 54 | 不适用 | 无供应商 BAA。 |
| 55 | 部分适用 | 写侧有 `operationId`/`jobId`/`marker`（同事务持久化）；**本人实测读侧审计 0 命中**（无 read_audit/access_log 类标识），读不记 who-read。 |
| 56 | 不适用 | 无 PCI／卡号。 |
| 57 | 部分适用 | 有数据生命周期分层与「历史不可改写、缓存回收不得触及历史」规则；但无「用户删除请求」流程（无账号体系、无跨表/备份/日志删除通道），历史层按设计不可改写。 |
| 58 | 不适用 | 无数据驻留／地域选项。 |
| 59 | 不适用 | 无季度访问复核（无用户角色体系）。 |
| 60 | 部分适用 | 无 staging/prod 之分，只有本机开发与打包产物；`package:dir`＋`verify-i04-package.py` 构成构建态 vs 打包态一致性面，非三环境。 |
| 61 | 部分适用 | CI 用 GitHub Actions 为声明式 IaC，桌面应用为 Electron＋Python 引擎本地可复现构建；但「服务端基础设施」不存在。 |
| 62 | 适用（正面） | `ci.yml` 顺序为 `npm ci`→`uv sync --frozen`→`npm run check`→`npm run verify:sources`→E2E→`package:dir`→`verify-i04-package.py`；本轮 `package.json` 的 `engine:check` 改为 `scripts/run-engine-tests.py`（带逐 node 计账，本轮新增 470 行）。**但流水线当前未绿**（见 R11-T01），故只判流程面正面。 |
| 63 | 不适用 | 无线上部署，无一键回滚。 |
| 64 | 不适用 | 无线上服务，无维护窗口。 |
| 65 | 不适用 | 无功能开关机制。 |
| 66 | 不适用 | 无云端扩缩。 |
| 67 | 不适用 | 无 CDN。 |
| 68 | 部分适用 | 本地应用不需 DNS/证书；等价责任是签名/公证/发布链，属明确保留的独立 HOLD。 |
| 69 | 部分适用 | 引擎有常驻协调器与 job 机制（ADR-0003）、主进程有取消/心跳；但耗时业务能力尚未接入（M0 正式领域能力仍只有 health 级）。 |
| 70 | 部分适用 | 无外部 API 可丢单；但引擎 job 重试与 `recoveredPending` 恢复逻辑存在，CI 侧明确 `retry0`。取保守中间档。 |
| 71 | 不适用 | 无死信队列。 |
| 72 | 不适用 | 无 cron／多服务器调度。 |
| 73 | 部分适用 | 有派生视图/快照缓存与 `invalidation-v2.json` 驱动的 `staleReason`；**本人亲读 `test_storage.py:190-223` 确认九规则参数化正反断言真实存在**；但九行**未逐类 GUI 实测**，四具名下游（推导/保存查询/SHACL/报告）仍 OPEN。 |
| 74 | 不适用 | 无事务性邮件面（无账号、无密码重置、无对外通知，全程不经 SMTP）。 |
| 75 | 不适用 | 无事务邮件。 |
| 76 | 不适用 | 无对象存储生命周期／2021 临时文件清理面。 |
| 77 | 不适用 | 无云成本告警／AI 循环账单面。 |
| 78 | 不适用 | 无灾备（本地单机，无多地域接管演练）。 |
| 79 | 不适用 | 无第二地域。 |
| 80 | 部分适用 | 有结构化 JSON 事件流（`scripts/engine-test-reporting.py` 的 `events.jsonl`、`job_details`/`job_blobs`、`summary.json`）；但应用运行期无面向运维的结构化日志检索面，且 engine 自然退出码为 UNKNOWN。 |
| 81 | 不适用 | 无错误聚合服务。 |
| 82 | 不适用 | 无外部 uptime 探测。 |
| 83 | 不适用 | 无值班告警分页。 |
| 84 | 不适用 | 无运营看板。 |
| 85 | 不适用 | 无跨服务链路追踪。 |
| 86 | 不适用 | 无值班轮转。 |
| 87 | 部分适用 | 仓库有 ADR-0001/0003、M0 计划 S1/S2/S3/C1/B1/U1 全文与 `docs/reviews/T02/status.md` 状态源，具名 owner/事件窗口明确；但面向值班人的运行手册不存在。 |
| 88 | 不适用 | 无线上事故复盘。 |
| 89 | 不适用 | 无状态页。 |
| 90 | 部分适用 | 测试大量断言**完整预期集合/顺序**（如 `t02-fr200-fr201.spec.ts` 对完整 Diff 数组、marker/job/commitProgress 的整体相等断言）；有真实 Python 交叉校验（`t02-manual-fact-id.test.ts`，本人亲读）；但「由懂逻辑的人写的」无可证事实，新增 7 个 unit 为纯 synthetic DOM 形状。 |
| 91 | 部分适用 | 无第三方 API；但对**真实引擎**有集成测试（3769 集合）与真实 Electron E2E。 |
| 92 | 适用（正面） | FR-200/201 表单 CRUD 与事实创建走真实表单、完整 Diff、显式确认、原操作读取、marker/job 校验；本轮 native24 = 21 PASS＋3 原 I04 SKIP（O074 原件）。 |
| 93 | 不适用 | 无发布前压测（Q5 未确认，M0 明确「不设业务容量通过线」）。 |
| 94 | 适用（正面） | 测试用合成 `urn:t02:*` 命名空间与固定 golden 向量，与真实业务库隔离。 |
| 95 | 适用（正面） | 累计 3769 收集项与 7 个新增 `test_mainline_*.py` 回归集；本轮 `domain_changesets.py` 的词法拒绝、`storage.py` 的两 Conflict 类均有对应新增测试路径。 |
| 96 | 部分适用 | **本轮变更**：目标参考设备与跨 OS（macOS15/Win11）仍属独立 HOLD，本轮未测；但 CI 三平台矩阵**确实存在并实际运行过**（CI43 三 job 均实际执行），故由「不适用（未实施）」上调为**部分适用**——矩阵存在但未全绿。 |
| 97 | 部分适用 | **本轮变更**：本轮新增 `OwnershipConflictDetailView.ts` 以 `aria-label` 标注三个区域（本人亲读全文），并新增 `role="status"` 状态文案（「正在读取冲突定位…」「冲突详情暂不可用…」）；`aria-live`/`role="alert"` 在既有页面在位。但无 a11y 合规验收，「企业合同要求」属法律事实。 |
| 98 | 不适用 | 无订阅／升降级／按比例计费。 |
| 99 | 不适用 | 无失败付款重试与催款邮件。 |
| 100 | 不适用 | 无发票／PO 号。 |
| 101 | 不适用 | 无销售税／VAT。 |
| 102 | 不适用 | 无退款／贷项。 |
| 103 | 不适用 | 无用量计费。 |
| 104 | 不适用 | 无年度合约／自定义条款。 |
| 105 | 不适用 | 无收入报表。 |
| 106 | 不适用 | 无 webhook。 |
| 107 | 不适用 | 无 webhook 重试日志。 |
| 108 | 部分适用 | **本轮变更**：stdio 协议 v2 仍是内部契约，但本轮**新增了一个对外可被渲染端调用的业务方法**（`project.ownership.detail`，经 `getOwnershipConflictDetailPage`），契约含 `schema.json` 版本化定义、双端 matcher（`matchesOwnershipDetail`／`ownership_detail_matches`）与 `reassembleOwnershipDetail` 字节流重组。**属内部契约的扩展**，非客户集成 API；但版本化与错误码面确实在推进，故由「不适用」上调为**部分适用**。 |
| 109 | 不适用 | 无客户 API key。 |
| 110 | 不适用 | 无对外 API 限流。 |
| 111 | 不适用 | 无第三方 API 响应格式突变。 |
| 112 | 不适用 | 无 OAuth 对接。 |
| 113 | 不适用 | 无客户沙箱集成环境。 |
| 114 | 部分适用 | 当前无模型接入，无提示注入面；但同一批字段正是 FR-200/201 用户输入面，其净化/拒绝机制已落地（见 #40）。 |
| 115 | 不适用 | 无「数据离开网络」的提示面。 |
| 116 | 不适用 | 无按客户计的模型花费上限。 |
| 117 | 不适用 | 无模型评测集。 |
| 118 | 不适用 | 无模型服务商降级预案。 |
| 119 | 不适用 | 无模型弃用迁移计划。 |
| 120 | 不适用 | 无提示/输出日志。 |
| 121 | 适用（正面） | 正式写入必须经「完整事务差异」显示＋「我已核对完整差异，确认提交」按钮；`commit()` 断言 `commitProgress.mode === 'atomic'`、`confirmationRef` 非空；Agent 只产草稿的 FR-204 边界确立。**本轮正面增强**：冲突发生时给出**可定位的首个阻断记录**（id/owner/sourceRow/槽位），而非笼统错误。 |
| 122 | 不适用 | 无「酒店 WiFi」场景（本地应用无网络依赖）。 |
| 123 | 部分适用 | 渲染层有 `phase`（reading/preparing/submitting/ready/idle/unknown）与 `role="status"`/`role="alert"`；本轮新增三态（reading/unavailable/ready）覆盖 ownership 详情；但不是每个页面都有完整三态。 |
| 124 | 适用（正面） | 错误文案从笼统改为可行动：`OWNERSHIP_CONFLICT` 给出「事实来源、保留身份或属性约束存在冲突。请核对原记录，修改输入后重新预览；已输入内容保留。」，并新增冲突定位视图；引擎只传固定码与受限参数（`detailRef`）。 |
| 125 | 适用（正面） | `newManualFactPlan` 不改入参（`t02-manual-fact-id.test.ts:98` 断言 `fact` 与输入相等，本人亲读）；UI 层 `invalidateFactPreview()` 只丢预览不丢表单值；拒绝用例断言三值原样保留。 |
| 126 | 不适用 | 无邮件渲染。 |
| 127 | 不适用 | 无通知开关。 |
| 128 | 部分适用 | Undo 入口存在，定义级 GUI 撤销/撤销之撤销/owned restart 已由既有证据收窄验证；**其余 Undo 面与 GUI 全面验证仍为 HOLD**。 |
| 129 | 部分适用 | **本人实测**：`aria-*`/`role` 语义基础在（既有页面 `role="alert"`/`role="status"`、本轮新增 `OwnershipConflictDetailView.ts` 三个 `aria-label` 区域，E2E 以 `getByRole` 精确角色＋名称为唯一定位源）；但 renderer 全量 `tabIndex`/`onKeyDown` **0 命中**——无显式键盘可达与焦点管理实现，无读屏实测、无 a11y 合规验收。 |
| 130 | 不适用 | 无界面多语言本地化（文案中文固定；数据内容支持多语言标签，见 #26）。 |
| 131 | 不适用 | 无浏览器后退按钮（Electron 无多页导航）。 |
| 132 | 适用（正面） | 模块边界清晰；关键不变量以注释固化（如「Persist only fixed categories and authorized opaque identities, outside the rolled-back write. No exception text/values/paths.」）。 |
| 133 | 适用（正面） | 本轮即双指定模型独立审查；历轮 R04–R10 均有独立 disposition 与独核记录。 |
| 134 | 部分适用 | worktree＋feature 分支＋PR16 流程在用；但并行开发线的合并顺序协调仍靠人工调度。 |
| 135 | 部分适用 | **本轮变更**：本人实测 `.github/dependabot.yml` 有 npm 与 github-actions 两条 **weekly** 节奏（此前记为「无月度依赖升级流程」不准确）；但无 SLA/EOL 核验、且仅覆盖 root npm/actions 而**不覆盖 uv/vendor 与 Python 依赖**，故由「不适用」上调为**部分适用**。 |
| 136 | 部分适用 | **本轮变更**：本轮把 vendored rdflib 固定到 `7.6.0+ontolearn.fr201.3`（`pyproject.toml` ＋ `uv.lock` 同步＋ vendored wheel＋PROVENANCE），等于**给 Python 依赖侧建立了一个可追溯的固定版本**；但 Electron/Playwright 升级仍无计划、且本轮 `ui-observation.ts` 的判据明确只支持当前 Playwright 1.64.1 形态（升级需重证）。 |
| 137 | 部分适用 | `packages/engine/vendor/rdflib/` 三个版本 wheel 并存（fr201.1/2/3）属已知冗余件（F09 原 owner 窗口，「不私自删 wheel」）；除此之外未见明显死代码残留。 |
| 138 | 部分适用 | 该现象**真实存在**：`job_store.py` 约 3000 行、`storage.py` 约 1900 行、`tests/e2e/t02-fr200-fr201.spec.ts` 本轮后 2400+ 行。行数本身不是质量结论，本候选未做拆分，拆分属维护窗口。 |
| 139 | 适用（正面） | ADR-0001/0003 ＋ M0 计划（S1/S2/S3/C1/B1/U1 全文与理由）＋ PRD 附录 C/D/E/F/G 齐备；**本轮新增 ADR-0003 已在树**。 |
| 140 | 部分适用 | 有 `package.json` 脚本、`uv`/`npm` 双锁文件与 `npm run check` 入口；**未见面向新人的 README 快速上手**。 |
| 141 | 部分适用 | `docs/reviews/T02/status.md`、`docs/m0-checklist.md`、ADR 与 M0 计划构成交接面，归属与状态有唯一维护者约定。 |
| 142 | 不适用 | 无运维管理后台。 |
| 143 | 不适用 | 无客户支持工具。 |
| 144 | 不适用 | 无客户可读变更日志。 |
| 145 | 部分适用 | 本地优先、无遥测、无云、无账号、无数据外发，隐私面天然极小且与代码一致；但整体法律/隐私/产权/供应链审计仍是明确保留的独立 HOLD。 |
| 146 | 部分适用 | 仓库为个人 GitHub 账号名下的仓库，非组织名；属发布/法律 HOLD 的具体一项。 |
| 147 | 部分适用 | 文档与 owner 归口清晰、ADR 完整，但关键知识集中于单一总控，各线各只有一名负责线，无第二人复现记录。 |
| 148 | 无法确认 | 逐行人审属人工流程，无法由代码判定；本轮审查与独立 agent 审查即其实例，但「上线前逐行人审」无既成证据。 |
| 149 | 无法确认 | 组织事实，代码不能证明。 |
| 150 | 无法确认 | 组织事实；历史上有此类记录（43692 误因果已撤回、R08 报告残句），但是否制度化无法由代码判定。 |
| 151 | 无法确认 | 本产品无服务器与云账单面；桌面发布链（签名/公证）是等价职责但整体属组织事实。 |
| 152 | 不适用 | 无支付服务与值班人。 |
| 153 | 部分适用 | **本轮变更**：漏洞当周打补丁在桌面分发形态下等价于「Electron/Chromium 安全更新跟进」＋「依赖安全更新」。本轮依赖侧有 weekly dependabot（npm/actions）＋rdflib 固定版本与 PROVENANCE；Electron 侧无自动跟进机制，且本轮 `ui-observation.ts` 判据与 Electron 内部映射耦合（Z09-09）。故由「不适用」上调为**部分适用**。 |
| 154 | 不适用 | 无患者数据与审计员演示。 |
| 155 | 部分适用 | **能力面可核**：本轮本人逐字核对了 O072/O073/O074 的 COMPLETION 与独立评审 JSON，并实测核对了 Git blob、hunk 结构、hash、行数与两处关键源码事实（§3.4），未采信任何自述数字；但**组织面无法确认**：无独立 QA 编制，验证证据与被验证实现出自同一开发线。 |
| 156 | 部分适用 | **本轮变更**：`storage.py` 有 `FORMAT_VERSION`／`user_version` 门禁、v1→v2 事务升级、迁移 hook 贯穿提交前中后、失败回滚 DDL/版本及数据、**提交后注入异常时格式已持久化且重开不得倒退**（ADR-0002 原文＋本人读 `storage.py:212-293` 差异面）；但「在**活跃**真实库上跑迁移且不丢一行」的演练**未实施**，属原 HOLD。 |
| 157 | 不适用 | 无「拒绝破坏三个其他功能的需求」的产品裁决记录（属组织流程）。 |
| 158 | 部分适用 | 有跨平台矩阵 CI 并**实际运行过**（CI43 三 job 均真实执行，Windows 逐 node 3769=3721P+48 原 S 有序资格成立）；但矩阵当前未全绿（Quality/Windows failure），且目标设备/跨 OS 属保留 HOLD。 |
| 159 | 不适用 | 无「调试 AI 写不出原因」的场景。 |
| 160 | 部分适用 | 机制面成立（ADR＋M0 计划＋逐轮 disposition/version-map/artifact-manifest 保留原始位置与窗口）；组织留存面无法确认（巴士系数见 #147），且**归档目录极密**（round-04…round-10 七轮、每轮多份文档、两方原稿；本候选内 `docs/reviews/T02/` 已 57 个差异路径），一年后的检索成本是实际负担。 |

### 4.1 统计（总数 160）

| 判定 | 数量 |
|---|---|
| 适用（含「适用（正面）」） | **16** |
| 部分适用 | **50** |
| 不适用 | **89** |
| 无法确认 | **5** |
| **合计** | **160** |

结构事实：160 行、min 1／max 160、无缺号、无重复；每行只出一档且只计一次。复合组仍为 **#148–#160 共 13 行**，分布为 **无法确认 4（#148–#151）／不适用 4（#152、#154、#157、#159）／部分适用 5（#153、#155、#156、#158、#160）** —— 与 R10 的 4／4／5 **一致**，逐项以 §4 表内判定为准。

**相对 R10 有效分布的逐项差异**（本人以 R10 原稿 §4.1 表体＋§10.3 替代表＋§10.6 重建 R10 有效基线 = 16 正面／46 部分／90 不适用／8 未知，程序化逐行对比得 **10 项差异**）：

| # | R10 有效 | R11 本方 | 差异依据（本轮按当前源码复核） |
|---|---|---|---|
| #19 | 部分适用 | 部分适用 | **维持**（本人实测 `storage.py:1839 backup()` 在位，但无「每晚」调度） |
| #20 | 部分适用 | 部分适用 | **维持**（本人实测 `transactions.py:285 preview_restore` 与 `compensation.py` 在位，但无整库备份恢复路径） |
| #32 | 部分适用 | 部分适用 | **维持**（本人实测 `query_presentation.py:381` 有界分页在位，无用户分页列表面） |
| #33 | 部分适用 | 部分适用 | **维持**（本人实测 `QueryResultPanel.tsx:16-17 downloadCsv` 在位，FR-203/1000 导出未实现） |
| #26 | 部分适用 | 部分适用 | **维持**（本轮由「适用（正面）」下调：本人实测 `test_mainline_language_input_rejection.py` 无 emoji/RTL 显式用例） |
| #41 | 部分适用 | 部分适用 | **维持**（本轮由「适用（正面）」下调：无 OWASP 逐项回归证据面） |
| #57 | 无法确认 | 部分适用 | **下调一档**：分层与不可改写规则在位，但「用户删除请求」面不存在 → 部分适用更准确 |
| #146 | 无法确认 | 部分适用 | **下调一档**：本人实测 remote 为个人账号仓库（`NOmoreJoke/OntoLearn-Studio`）→ 事实可判定，归部分适用 |
| #147 | 无法确认 | 部分适用 | **下调一档**：巴士系数可由 owner 归口与归档密度部分判定 → 部分适用 |
| #108 | 不适用 | 部分适用 | **上调一档**：本轮新增对外可被渲染端调用的业务方法 `project.ownership.detail`（含 schema 版本化定义、双端 matcher、字节流重组） |

**本方统计不与 Z 侧统计相加、不作横向比较**；适用性分类**不是产品通过数**。

---

## 5. 历史意见逐项承接

> 口径：以 `docs/reviews/T02/fr200-fr201-20261024/round-10/disposition.md`（本人亲读全文 391 行）为最近归档，`version-map.json`／`artifact-manifest.json` 为结构索引；R09／R08 原件保留原 stableID、主题、owner、事件窗口。**逐项给当前适用性、原件/代码依据、本人已闭/保留/未知/不采及最小理由、原 owner/事件窗口**；重复条目给显式 ID 映射，**不以 Top 序号代稳定 ID、不漏 ID、不只说「沿用」**。**额外 13 单列，不并入权威 78。**
>
> **本轮新增的一处结构澄清**（`R11-F03`）：任务书中的「额外 13」与「MM 末 13 为 4 未知/4 NA/5 部分」**是两个不同集合**——前者是 `### 额外13` 段的 **R06 MM01–R06 MM13**（状态词为「仍开/已闭合/部分闭合」）；后者是 **MM 160 项清单的末 13 行 #148–#160**（适用性档位）。本方已以 `disposition.md:15` 原文与 R10 原稿 §11.3(a) 双向核实，两者分开处置。

### 5.1 当前 31（Z08-01…Z08-TOP10-OLD79F、F01–F19）

| stableID | 当前适用性 | 原件/代码依据（本轮复核） | 本人处置 | 原 owner/事件窗口 | push前源码阻断 |
|---|---|---|---|---|---|
| Z08-01 | 仍开（门禁） | `disposition.md:190`；本轮新事实：CI43 overall failure 已实际发生（O072） | **保留**，数值更新为 head `d1aca3e3`／43 提交／125 路径／1403 源 | ROOT 精确 push/CI 票；merge 前逐项核 | 否 |
| Z08-02 | 仍开 | `:191`；O074 `engineNaturalCode="UNKNOWN"`、`knownPIDAt0_2_5s="empty"`、`descendants UNKNOWN_NO_JOB_HANDLE`（转述 O072） | **保留**（absence≠自然退出码） | Windows 完整 CI 证据接收；新工具另票 | 否 |
| Z08-03 | 仍开 | `:192`；**本轮 ci.yml 实际有变更**（shards/reporter/artifact/Windows diagnostic 分支） | **保留**，主题按本轮事实更新 | 未来实际制品回单判断；预算变化须新授权 | 否 |
| Z08-04 | 仍开 | `:193`；本轮 Windows 已新增结构化 first-failure diagnostic（`PYTEST_ADDOPTS`），**但本轮未在 Windows 实际跑出新的逐例栈** | **保留** | 下一真实 CI 若复发按新增结构化栈定因；新绿不倒填 | 否 |
| Z08-05 | 仍开（维护） | `:194`；**本方实测** `rdf_snapshot.py` 的 `term().lower` 语义仍在；与 CI41 helper12 主题分离 | **保留**，主题不串 | T01 测试维护者下次授权触及环境/测试时 | 否 |
| Z08-06 | 分层维持 | `:195`；O072 Quality **确实执行过**（非跳过），但为 failure 且后续 steps 跳过 | **分层维持**：远端 CI OPEN 保留，不静默重开 | Windows/Quality 实际 CI 仍待验 | 否 |
| Z08-07 | 仍开 | `:196`；**本轮新增** `project.ownership.detail` 方法与 `OWNERSHIP_CONFLICT.detailRef` 参数面 → 裸族覆盖面**扩大但未闭合** | **保留** | 原 T01/T02 方法接线窗口 | 否 |
| Z08-08 | 仍开（P2） | `:197`；**本人实测** `packages/engine/vendor/rdflib/` 仍含 fr201.1/2/3 三 wheel＋upstream，`pyproject.toml` 只用 fr201.3 | **保留** | 发布/供应链 owner 另票 | 否 |
| Z08-09 | 仍开 | `:198`；**本轮 ci.yml artifact 已为 `always()`**（failure-traces-linux 由 `if: failure()` 改为 `always()`） | **保留** | 未来 CI 维护票 | 否 |
| Z08-10 | 仍开（部分采纳维持） | `:199`；**本人实测** dependabot.yml 在树（npm＋github-actions weekly） | **保留**；不得以 ruff exclude 事实充当本条主题 | 发布/vendor owner 未来窗口 | 否 |
| Z08-11 | 仍开 | `:200`；**本轮逐一核对**：签名公证、法律隐私产权供应链、跨 OS/参考设备、容量与旧超限库恢复、坏 SQLite 保护、unknown parser/N3/Store/坏快照、未具名下游/家族、Undo 其余面 —— **无一项被本轮关闭** | **保留** | 各原 owner 对应验收前 | 否 |
| Z08-TOP10-OLD79F | 仍开（未知保原） | `:201` | **保留** | ROOT 历史残留登记及未来复发证据 | 否 |
| F01 | 部分闭合 | `:202`；**本轮已完成本人必要覆盖**（§3.1/§3.4）；接收仍由 ROOT 决定 | **保留为流程**；本方已完成本方覆盖与处置 | T02 作者完成本票；ROOT push 前接收 | 否 |
| F02 | 仍开（门禁） | `:203`；本轮候选仍无新 CI | **保留** | ROOT 发精确票后按原 15/20 分钟逐 node 核；merge 前 | 否 |
| F03 | 仍开＋限定 | `:204`；**本轮变更**：Windows diagnostic step **确实成功执行**（CI43 step 8 success，21:41:57→21:49:35，转述 O072）→ 命名/门禁语义歧义由「未运行」变为「运行且绿」，但**「不是完整验收凭证」的性质不变**（完整 3769 在 Quality 侧 NOTRUN） | **保留**；不声称完整 sys.path 等价 | ROOT CI 控制层维护票 | 否 |
| F04 | 维持撤回（不复活） | `:205`；`reconciliationReady` 修正在 `tests/e2e/ui-observation.ts` 中在位（本人亲读全文） | **维持撤回**，不复活 | 本票内闭合 | 否 |
| F05 | 重新变开 | `:206`；**本方实测** `docs/m0-checklist.md` 与 `docs/reviews/T02/status.md` 的追加段**仍停在 R10/67b7**，尚无 d1aca3e3 段 | **重新变开**（本方只读，不代登记） | ROOT 指定文档 owner；状态新增段与普通证据提交 | 否 |
| F06 | 仍开（维护） | `:207`；`CI_ENGINE_TEST_SHARDS` 传递在位（**本人实测** `ci.yml` 中 `env: CI_ENGINE_TEST_SHARDS: '2'`）；13 身份字段≠sys.path 等价 | **保留** | 原 T02 归口首个 CI 维护票 | 否 |
| F07 | 仍开 | `:208`；本轮 O072/O073/O074 三份 COMPLETION 均带 head/tree 绑定（O073 明确「旧 manifest 仍是 cfcc 历史身份，由 O073 外置桥接」） | **保留** | ROOT 证据控制层维护票 | 否 |
| F08 | 部分闭合、本体仍开 | `:209`；**本轮变更**：renderer 的 `requireCurrent` 链**已扩展到 ownership 详情读取路径**（`mainline-session.ts` 的 `requireCurrent` 在读前后与 `readOwnershipConflictDetail` 内多次调用，本人读差异全文）；异步预览维护窗口未至 | **保留并正面复核** | 原 T02 前端归口；UX/异步预览维护窗口 | 否 |
| F09 | 仍开 | `:210`；同 Z08-08（本人实测冗余 wheel 仍在） | **保留**，不私自删 wheel | T11 merge 后受控维护 | 否 |
| F10 | 仍开 | `:211`；**本轮变更**：根 `pyproject.toml` **本轮新增**一条 ruff format exclude（`round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,minimax-m31flash-r2}.md`，本人实测），与既有 4 条 T01 per-file-ignores 覆盖面仍不等 | **保留**；不改 raw、不宽泛排除绕过检查 | ROOT 报告归档归口＋原 T02 维护归口 | 否 |
| F11 | 承接收窄维持 | `:212`；**本轮变更**：`newManualFactPlan` 的内容派生 ID 与 operation 幂等仍为两事（本人读差异：ID 由 `SHA-256([S,P,O])` 派生，operation 幂等在 `commit` 路径） | **维持收窄** | 原 MM 作者票内闭合 | 否 |
| F12 | 仍开 | `:213`；**本人实测** `ci.yml` 无 `continue-on-error`、无延时、无重试、无隐藏取消 | **保留** | ROOT 未来 CI 结算逐步核产物 | 否 |
| F13 | 仍开 | `:214`；O074 `newTiming="measurement only, no measured performance improvement claim"`（本人读原文） | **保留**，不量化未实测提速 | ROOT 后续 PR16 说明/CI 结算窗口 | 否 |
| F14 | 部分闭合 | `:215`；**本轮变更**：ownership-detail 契约**已落地并被本轮新增代码实际使用**（契约双端 matcher＋schema＋字节流重组＋renderer 适配器＋视图，本人亲读全部相关正文）；**维护归口不变**，本轮新增 R11-T05（TS 宽类型）落在同一归口 | **部分采纳**（契约已落地＋新增一个同归口维护观察） | 原 T02 契约归口；后续首个契约维护票 | 否 |
| F15 | 仍开（未确认观察） | `:216`；**本人实测** `storage.py:1151`／`:1170` 无 `ORDER BY` 仍在；**本轮新增** `SingleDeclarationConflict` 取前两条记录，使该观察有了实际消费者（见 R11-T04） | **保留**，不升级缺陷 | 原 T02 storage/契约归口 | 否 |
| F16 | 仍开（容量维持） | `:217`；**本人实测** 本轮未提高任何 READ_LIMITS/HELD_BYTES 常量 | **保留**，不提高上限、不解除容量 HOLD | 原 T02 契约归口持续保留原 capacity | 否 |
| F17 | 维持 | `:218`；无变化 | **保留** | 原 T02 前端归口 | 否 |
| F18 | 仍开 | `:219`；**本轮实测** `licenses/NOTICE` 与 `packages/engine/vendor/rdflib/PROVENANCE.json` 在树；供应链核验留发布前 | **保留** | 原 T11 供应链＋原 T02 依赖归口 | 否 |
| F19 | 仍开 | `:220`；**本轮实测** 根 `pyproject.toml` 的 ruff exclude 命中 `round-NN` 模式，**不触旧件**；旧 raw/标题保留 | **保留** | ROOT 唯一归档归口 | 否 |

### 5.2 权威 78（Z F1–F10；MM R07-01–13；R06 Z P1–P8；R06 D1–D12；R04 Z01–Z07／M01–M07；R05 Z P1–P8／MM01–MM13）

**Z F1–F10**

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| Z F1 | 仍开（门禁） | `:226`；CI43 实际 failure 已发生 | 保留，数值更新 d1aca3e3 | ROOT 精确 CI 票；merge 前 | 否 |
| Z F2 | 仍开（维护） | `:227`；本轮归档外新增 raw：O072/O073/O074 三个**仓外**目录，**未入树**（本人实测 `git ls-tree` 无其路径） | 保留 | 未来新增 raw/改规则时 | 否 |
| Z F3 | 仍开（维护） | `:228`；**本人实测** `scripts/engine-test-reporting.py` 与 `scripts/run-engine-tests.py` 全部 JSON 以 `encoding="utf-8"` 显式写出 | 保留 | 原测试 owner 下次触及 | 否 |
| Z F4 | 关闭（口径）维持 | `:229`；本轮无 dumps 调用面变化 | 保留 | 无待办 | 否 |
| Z F5 | 仍开（维护） | `:230`；**本人实测** `tests/unit/t01-mainline-contract.test.ts:656` 与 `tests/unit/t01-ontology-metadata-contract.test.ts:168` 两处 `execFileSync('python', …)` **裸 PATH 仍在**；`t02-manual-fact-id.test.ts:67` 是 `resolve('.venv/bin/python')` 显式路径，**不能替换**本条 | 保留 | T01 测试维护者下次授权触及两测试或环境适配前 | 否 |
| Z F6 | 仍开（逐项集合） | `:231`；**本人逐项核对**：definitions 早期 wire、裸 ownership、standalone EOF、缺码、无序、4299/4300 —— 本轮均未闭合（无序项见 R11-T04） | 保留 | 各接线/维护事件 | 否 |
| Z F7 | 仍开（发布 HOLD 群） | `:232`；**本轮逐一核对无一项关闭** | 保留 | 各 owner 对应验收前 | 否 |
| Z F8 | 仍开（部分） | `:233`；`rdf_snapshot.py` 的 TermInputError 分流在位；**本轮新增** `domain_changesets.py` 只对直接调用方词法做 `INVALID_REQUEST`，未知 parser/N3/Store 失败仍保留 UNKNOWN/HOLD（本人读差异全文） | 保留 | 未知/新家族接线前 | 否 |
| Z F9 | 承接（限本受审面闭合） | `:234`；**本人亲读** `_OwnershipProof.check()` 全量授权链（owner/store/connection/lease/project/generation/reply 同一性） | 保留 | T01/T02 触及时 | 否 |
| Z F10 | 承接（既有证据接收） | `:235`；O074 native24 = 21P＋3 原 I04 S、57 事务、43 拒绝（转述），**不外推全 GUI** | 保留 | 既有证据接收维持 | 否 |
| ~~Z F11／Z F12~~ | — | **不是权威 78 条目**：F11／F12 属**当前 31**（见 §5.1），此处仅为避免读者误寻而注明归属，**不计入 78** | 见 §5.1 | — | — |

**MM R07-01–R07-13**

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| MM R07-01 | 关闭（口径） | `:236`；根 pyproject per-file-ignores 在位 | 保留 | 本次静态接收 | 否 |
| MM R07-02 | 仍开（维护） | `:237`；本轮未发生新 raw 入树（本人实测） | 保留 | ROOT/T02 未来确增 raw 时 | 否 |
| MM R07-03 | 仍开 | `:238`；覆盖面仍不等（**本轮新增**第 5 条 format exclude，与 per-file-ignores 覆盖面不同） | 保留 | 将来独立配置票 | 否 |
| MM R07-04 | 重新变开 | `:239`；同 F05（status/m0 仍停在 R10/67b7） | 保留为重新变开 → F05 | ROOT 文档 owner | 否 |
| MM R07-05 | 仍开（overlay 维护） | `:240`；**本人实测** `git status` 仍为 `M AGENTS.md` | 保留 | ROOT/指南 owner | 否 |
| MM R07-06 | 关闭（口径）维持 | `:241` | 保留 | 本次事实修订 | 否 |
| MM R07-07 | 已闭合（口径） | `:242`；20 默认 ASCII JSON 窄结论维持 | 保留 | 原测试 owner | 否 |
| MM R07-08 | 已闭合（口径） | `:243`；28 笔 FR200 分层不扩维持；**本轮未扩**（本轮新增 ownership 详情属冲突定位，不改 FR200 覆盖面） | 保留 | 父 FR/具名下游另验 | 否 |
| MM R07-09 | 已闭合（口径） | `:244`；**本轮变更**：本轮**有**实际构建映射（O074 BUILD-REBUILD-MAPPING，main 仅 nonce 24B 变、另 4 build 精确旧）→ 该口径由「本轮无新构建」更新为「本轮有构建映射，nonce 口径维持」 | 保留（口径更新） | 既有证据限定 | 否 |
| MM R07-10 | 已闭合（口径） | `:245`；**本轮变更**：本轮 **Ruff 393**（O074 `ruffFiles=393`，转述），且 `pyproject.toml` 新增 1 条 format exclude → Ruff 各时点计数**再次变化**，故本条「无 Python 变化」前提在累计候选上已不成立，需按新计数重对账 | **保留原口径并标注前提已变**（不改写历史） | 无新复跑票 | 否 |
| MM R07-11 | 仍开（观察） | `:246`；**本人读本轮差异**：`manualFactPlan` 的重叠拒绝条件**再次改写**（本轮由「同 slot 恰好一条」改为「存在任一受管/同值/替换值冲突行即拒绝」），编辑仍保原 ID | 保留 | T02/ROOT 未来 PR 说明可解释 | 否 |
| MM R07-12 | 仍开（HOLD） | `:247`；PROVENANCE/patch/upstream 三方哈希在树；法律/供应链 HOLD 保留 | 保留 | vendor/发布 owner 升级/发布前 | 否 |
| MM R07-13 | 仍开（维护） | `:248`；**本人实测** `index.ts:894-896` 宽类型仍在（见 R11-T05） | 保留 | 契约 owner 下次授权整理类型时 | 否 |

**R06 Z P1–P8**

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R06 Z P1 | 仍开（门禁） | `:249`；同 Z F1 | 保留，数值更新 | 合并前真实 CI | 否 |
| R06 Z P2 | 仍开 | `:250`；**本轮新事实**：CI43 的 Windows diagnostic step **实际成功** → 「诊断步与完整验收口径分离」在真实 CI 上得到一次**正面**示范（诊断绿 ≠ 完整 3769 绿，Windows 侧 3769 逐 node 3721P＋48 原 S 由独立 qualification 给出，Quality 侧完整 3769 NOTRUN） | **保留**（主题不变） | 未来 CI 证据接收标准 | 否 |
| R06 Z P3 | 仍开 | `:251`；`domain_changesets.py` 的 `_definition` 预览路径未分类 ValueError —— **本轮该文件新增了 direct-caller 词法拒绝分支**，但**未触及** `_definition` 的早期 wire 分类 | 保留 | T01 核心；原始 wire/Agent 接线前 | 否 |
| R06 Z P4 | 部分闭合维持 | `:252`；**本轮变更**：typed witness 已**端到端落地并被消费**（`ManualOwnershipConflict`／`SingleDeclarationConflict` → `detailRef` → 字节流 → 视图），裸族仍未全闭 | 保留 | T01 详情合同＋T02 消费 | 否 |
| R06 Z P5 | 仍开 | `:253`；错误码集合差维持；**本轮新增** `project.ownership.detail` 方法与 `OWNERSHIP_CONFLICT.detailRef` 参数面 → 差集又增一项待核 | 保留 | 对应方法接线前 | 否 |
| R06 Z P6 | 仍开（未确认观察） | `:254`；**本人实测** `:1151`/`:1170` 无 `ORDER BY` 仍在；本轮 `SingleDeclarationConflict` 使其有了实际消费者（见 R11-T04） | 保留，不升级 | T01 下次触及 witness 选取时 | 否 |
| R06 Z P7 | 已闭合（沿既有决定） | `:255`；**本人实测** `domain_changesets.py` 本轮保留 `parsed.n3() != value` 拒绝（且**新增**对 `manual`/`edits` 的同类检查） | 保留 | 政策变更才新人类决定 | 否 |
| R06 Z P8 | 仍开（逐项承接） | `:256`；7.2–7.6 各行分别承接，未被集合化关闭 | 保留 | 各原归口 | 否 |

**R06 D1–D12**

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R06 D1 | 仍开（门禁） | `:257`；本轮 delta **含产品代码**（非仅测试路径），但仍无新 CI | 保留 | ROOT 正常票 | 否 |
| R06 D2 | 重新变开 | `:258`；同 F05 | 保留为重新变开 → F05 | ROOT 文档 owner | 否 |
| R06 D3 | 仍开 | `:259`；同 R06 Z P3 | 保留 | T01；接线前 | 否 |
| R06 D4 | 部分闭合维持 | `:260`；**本轮变更**：两出口终码仍 `OWNERSHIP_CONFLICT`，且本轮**新增了第三处 typed 出口**（`_application` 中 `ManualOwnershipConflict`／`SingleDeclarationConflict` → `fault("OWNERSHIP_CONFLICT", detailRef=…)`），裸族定位仍未全闭 | 保留 | T01+T02 | 否 |
| R06 D5 | 仍开（未确认观察） | `:261`；同 Z P6 | 保留 | T01 下次触及选取时 | 否 |
| R06 D6 | 仍开 | `:262`；patch 含类型化守卫；`n[-1]` 裸索引残余未证不可达 | 保留 | T02 vendor/T01 入口；新解析入口前 | 否 |
| R06 D7 | 仍开 | `:263`；同 Z P5（且本轮差集又增） | 保留 | T01/T02 对应方法接线前 | 否 |
| R06 D8 | 仍开（维护） | `:264`；同 Z F5（本人实测两处裸 PATH 在位） | 保留 | T01 测试维护者 | 否 |
| R06 D9 | 已闭合（口径） | `:265`；**本轮变更**：本轮 Python 源码**确有变更**（mainline.py/storage.py/job_store.py 等）且 Ruff 计数变为 393 → 「无 Python 变化」前提在累计候选上已不成立 | **保留原口径并标注前提已变** | 文档 owner 归档后追加 | 否 |
| R06 D10 | 仍开 | `:266`；四具名下游（编辑→推导/保存查询/SHACL/报告）GUI 未逐类验；**本人亲读 `test_storage.py:190-223` 确认九规则参数化断言在位**，但静态断言 ≠ 逐类 GUI | 保留 | 父 FR/消费链验收前 | 否 |
| R06 D11 | 仍开 | `:267`；仅 4301 断言在位，4299/4300 应用断言缺 | 保留 | T02 整数守卫维护窗口 | 否 |
| R06 D12 | 保留（有界）维持 | `:268`；六 keyword AST/本地运行/旧包身份按原资格不外推 | 保留 | 无待办 | 否 |

**R04 Z01–Z07／M01–M07**

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R04 Z01 | 仍开（未确认观察） | `:269`；同 Z P6/D5（见 R11-T04） | 保留 | T01 触及选取时 | 否 |
| R04 Z02 | 撤回维持 | `:270`；43692 误因果不复活；**本轮实测** `reassembleOwnershipDetail` 仍保留 `value.length > 43692` 与 `characters > 512*(43692+1024)` 边界，job_store 页上限 `min(maxPageBytes,maxFrameBytes,262144)` 仍在 | 不采纳原强论断 | T01 详情预算维护 | 否 |
| R04 Z03 | 仍开 | `:271`；同 Z P3/D3 | 保留 | T01；接线前 | 否 |
| R04 Z04 | 仍开（部分闭合） | `:272`；同 Z P4（typed 已端到端、裸族未闭） | 保留 | 家族接线前 | 否 |
| R04 Z05 | 仍开 | `:273`；同 Z P5/D7 | 保留 | 方法接线前 | 否 |
| R04 Z06 | 关闭 | `:274`；canonical 既有政策在位且本轮保留 | 保留 | 无待办 | 否 |
| R04 Z07 | 关闭 | `:275`；规模信息接收，不以 LOC 推正确性 | 保留 | 无待办 | 否 |
| R04 M01 | 关闭（历史演进） | `:276`；当前 head 状态源见 F05 | 保留 | ROOT 归档票 | 否 |
| R04 M02 | 关闭（维持） | `:277`；PROVENANCE 在树；fr201.1/2 未删（见 F09） | 保留 | 无待办 | 否 |
| R04 M03 | 仍开 | `:278`；同 D11 | 保留 | T02 整数守卫时 | 否 |
| R04 M04 | 仍开 | `:279`；standalone EOF 残余未证当前 UI 可达 | 保留 | 新解析入口前 | 否 |
| R04 M05 | 仍开 | `:280`；同 D3/Z P3 | 保留 | T01 接线前 | 否 |
| R04 M06 | 关闭（维持分层） | `:281`；双端 ID 校验/原 ID edit 在位；**本轮实测** `newManualFactPlan` 用 `crypto.subtle.digest('SHA-256', JSON.stringify([S,P,O]))`，引擎侧 `storage.py` 的 `reserved_id = digest([subject,predicate,value])`（`_check_slot` 内）→ **两端口径一致**；机器交叉核验在 `t02-manual-fact-id.test.ts`（本人亲读） | 保留；不外推为全产品安全认证 | 无待办 | 否 |
| R04 M07 | 仍开（维护窗口） | `:282`；未证冲突，不缩导出面 | 保留 | 契约 owner API 整理时 | 否 |

**R05 Z P1–P8／R05 MM01–MM13**

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R05 Z P1 | 仍开（门禁） | `:283`；同 Z F1 | 保留 | ROOT 合并门禁 | 否 |
| R05 Z P2 | 关闭（事实）维持 | `:284`；934 Quality packaged recovery 为历史证据；**本轮 O072 macOS package/verify 成功也不迁移为 d1aca3e3 的 CI 绿** | 保留 | 无待办 | 否 |
| R05 Z P3 | 仍开 | `:285`；同 Z P3 | 保留 | T01 接线前 | 否 |
| R05 Z P4 | 仍开（部分闭合） | `:286`；同 Z P4 | 保留 | 家族接线前 | 否 |
| R05 Z P5 | 仍开 | `:287`；同 Z P5 | 保留 | 方法接线前 | 否 |
| R05 Z P6 | 关闭（口径） | `:288`；canonical 政策不变 | 保留 | 无待办 | 否 |
| R05 Z P7 | 关闭（口径，仅诊断选项一半） | `:289`；**本轮**：诊断选项在 `ci.yml` 的 Windows 分支仍在（「Windows engine first-failure diagnostic (not acceptance)」）；「文件增长」一面仍为信息级（见 #138） | 保留原口径（口径闭合限于诊断选项一半） | 无待办 | 否 |
| R05 Z P8 | 重新变开 | `:290`；同 F05 | 保留为重新变开 → F05 | ROOT 文档 owner | 否 |
| R05 MM01 | 仍开（门禁） | `:291`；旧 79 全因未知 | 保留 | ROOT；新 CI 后、merge 前 | 否 |
| R05 MM02 | 已闭合（事实）维持 | `:292` | 保留 | ROOT/新 CI 后 | 否 |
| R05 MM03 | 仍开（门禁） | `:293`；**本轮变更**：O074 做了实际构建映射（main 606471B 仅 nonce 24B 变、另 4 build 精确旧），但**不是新包制造**（旧 094 包 912 成员仍只是旧有界证据） | 保留 | 新包制造票 | 否 |
| R05 MM04 | 重新变开 | `:294`；同 F05 | 保留为重新变开 → F05 | ROOT 文档 owner | 否 |
| R05 MM05 | 仍开 | `:295`；同 Z P5/D7 | 保留 | 方法接线前 | 否 |
| R05 MM06 | 仍开 | `:296`；同 D3/Z P3 | 保留 | T01 接线前 | 否 |
| R05 MM07 | 仍开（部分闭合） | `:297`；typed witness 本轮**端到端落地**（含 `SingleDeclarationConflict`），裸族延期 | 保留 | 家族接线前 | 否 |
| R05 MM08 | 仍开（未确认观察） | `:298`；同 Z P6（见 R11-T04） | 保留 | T01 下次触及选取时 | 否 |
| R05 MM09 | 已闭合（维持） | `:299`；wheel/payload/解压量分层维持；冗余件见 F09 | 保留 | vendor/发布 owner | 否 |
| R05 MM10 | 关闭 | `:300`；AGENTS overlay 维持非候选缺陷（**本人实测 git status 仍在位**） | 保留 | 无待办 | 否 |
| R05 MM11 | 关闭（信息） | `:301`；locator 仅 `id/owner/sourceRow/slot`，无 object —— **本人实测** `storage.py` 的 `locator()` 与新增 `OwnershipLocator` 类型均为四字段 | 保留 | 无待办 | 否 |
| R05 MM12 | 仍开 | `:302`；两 TS PATH python（本人实测在位） | 保留 | T01 原测试维护者 | 否 |
| R05 MM13 | 关闭（信息）维持 | `:303` | 保留 | 无待办 | 否 |

### 5.3 R09 新增 19 ＋ OBS 独立项（合计 20）

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| Z09-01 | 仍开（门禁） | `:309`；CI43 overall failure 已实际发生 | 保留，数值更新 d1aca3e3 | ROOT；精确 CI 票/merge 前 | 否 |
| Z09-02 | 仍开 | `:310`；CI41 根因 UNPROVEN；**本轮新事实**：CI43 的 C1 失败**不是**旧 helper12 TypeError、也不是 45/90s timeout（13086ms、readiness 1、bootstrapComplete true、child close 1/null）→ 原根因仍未定，且新失败形态已不同 | 保留 | ROOT；真实 CI 归因/回单接收 | 否 |
| Z09-03 | 仍开 | `:311`；O074 `engineNaturalCode="UNKNOWN"`；Windows 后代 `UNKNOWN_NO_JOB_HANDLE`（转述 O072） | 保留 | ROOT；CI 证据接收 | 否 |
| Z09-04 | 仍开 | `:312`；**本人实测**三 wheel 仍在树 | 保留 | T11；merge 后受控维护 | 否 |
| Z09-05 | 仍开 | `:313`；**本人实测** `index.ts:894-896` 宽类型仍在 | 保留 | 契约 owner；下次整理 | 否 |
| Z09-06 | 仍开（不升级） | `:314`；无 ORDER BY 在位；本轮新增实际消费者（见 R11-T04） | 保留 | T01；触及 witness 选取时 | 否 |
| Z09-07 | 仍开 | `:315`；仅 4301 断言在位 | 保留 | T02；原整数守卫维护窗口 | 否 |
| Z09-08 | 仍开 | `:316`；**本轮实测** `failure-traces-linux` 已为 `always()`，制品范围扩大为 `build/engine-tests/`＋`test-results/`，未设 `if-no-files-found` | 保留 | ROOT；下次回单/CI 维护票 | 否 |
| Z09-09 | 仍开 | `:317`；**本人读** `native-driver.ts` 差异：仍用 `--inspect=0`＋MAIN inspector WebSocket 就绪探测与 450×100ms 轮询形态 | 保留 | 原 T02 native 线＋ROOT | 否 |
| Z09-10 | 仍开 | `:318`；**本轮变更**：typed ownership 详情已端到端落地，**但**裸族（无 typed witness 的其它 Conflict 家族）仍未闭合 | 保留 | T01/T02；对应家族接线前 | 否 |
| F-R09-01 | maintain | `:319`；CI41 失败保留；本轮 CI43 亦 failure | 保留 | ROOT/原 T02；下一精确 push 后真实 CI | 否 |
| F-R09-02 | maintain | `:320`；根因 UNPROVEN 是 HOLD 与主张纪律，**不是**新增「合并前必须证因」门禁 —— **本方复核：同意，本报告亦未设该门禁** | 保留 | 原 T02/ROOT；真实 CI 归因 | 否 |
| F-R09-03 | maintain | `:321`；readiness-helper 断言与 `app?.isPackaged` 建议已撤回；**本轮新事实**：CI43 的 C1 确实过了首 readiness（`readinessAttempts=1`、`bootstrapComplete=true`），说明旧 helper12 的失败形态已变——但这**不等于**旧断言被追认为正确 | 保留（不采纳原强论断） | 原 T02 测试/打包 | 否 |
| F-R09-04 | maintain | `:322`；145.101s 非轮询耗时为有界观察；**本轮新增** poll 容器 78.569318s／残余 68.50865s 等新数值，同为**有界观察**，**不构成新合并门禁** | 保留 | 原 T02 测试；真实 Windows 运行后观测 | 否 |
| F-R09-05 | maintain | `:323`；仅失败 annotation 核查；成功 CI 无需失败样本 —— **本轮实测** O074 新 catch 只在失败路径触发，本机 C1 成功故未产生该附件（`c1FailureAttachments=[]`），**与本条一致** | 保留 | 原 T02；真实失败样本存在时核 annotation | 否 |
| F-R09-06 | maintain | `:324`；证据绑定接收限制；脚本 A 属 base→240 累计变更 | 保留 | ROOT；证据接收拦截 | 否 |
| F-R09-07 | maintain | `:325`；sys.path 等价限制不解除 —— **本方复核：`engine-test-reporting.py` 的 identity 字段含 `pythonpath`/`addopts`/`executable` 等 13 项，但不等价于完整 sys.path，本条维持** | 保留 | 原 T02 | 否 |
| F-R09-08 | maintain | `:326`；状态归档义务 —— 仍待登记（见 F05） | 保留 | ROOT 指定 owner | 否 |
| F-R09-09 | maintain | `:327`；完整 CI/制品接收纪律 —— **本轮实测** CI43 三制品 digest 与成员数已核（O072），但**完整 CI 未通过** | 保留 | ROOT；每次 CI 完整回单接收 | 否 |
| OBS-R09-10 | maintain（P3） | `:328`；整数上限测试环境前提记录；4299/4300 不因此关闭 | 保留 | 沿原 T02 测试窗口 | 否 |

### 5.4 额外 13（单列，不并入权威 78）

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R06 MM01 | 仍开（门禁） | `:334`；≡R05 MM01/Z F1；CI43 failure 已实际发生 | 保留 | ROOT 精确 push/CI 票；merge 前 | 否 |
| R06 MM02 | 已闭合（事实） | `:335`；934 packaged recovery 历史事实不迁移 | 保留 | 无待办 | 否 |
| R06 MM03 | 仍开（门禁） | `:336`；本轮有构建映射但**非新包制造** | 保留 | ROOT 新包制造票 | 否 |
| R06 MM04 | 重新变开 | `:337`；≡R05 MM04/R06 D2；status/m0 仍停在 R10 | 保留为重新变开 → F05 | ROOT 文档 owner | 否 |
| R06 MM05 | 仍开 | `:338`；≡R05 MM05/R06 Z P5（错误码集合差）；首稿所加「裸 ownership 家族」主题**无原件依据，撤回**（本方复核 R09:347 该行仅「仍开」）；**本轮差集又增** `project.ownership.detail` 相关项 | 保留 ID 与状态「仍开」 | T01 契约＋T02 方法出口；接线前 | 否 |
| R06 MM06 | 仍开 | `:339`；≡R05 MM06/R06 D3（definitions 早期 wire ValueError 未分类，`:157`）；**本轮该文件新增分支但未触及 `:157` 分类** | 保留 | T01；原始 triples/Agent 接线前 | 否 |
| R06 MM07 | 部分闭合 | `:340`；≡R05 MM07/R06 Z P4；**本轮变更：typed witness 已端到端落地并被 renderer 消费**（`detailRef`→字节流→视图），裸族仍延期 | 保留（typed/裸家族分开） | T01 详情合同＋T02 消费 | 否 |
| R06 MM08 | 仍开（未确认观察） | `:341`；≡R05 MM08/R06 Z P6；本轮新增实际消费者（见 R11-T04） | 保留 | T01 触及 witness 选取时 | 否 |
| R06 MM09 | 已闭合（维持） | `:342`；wheel/payload/解压量分层维持 | 保留 | vendor/发布 owner | 否 |
| R06 MM10 | 已闭合 | `:343`；overlay 仍在位（本人实测） | 保留 | 无待办 | 否 |
| R06 MM11 | 已闭合（信息） | `:344`；locator 四字段（本人实测） | 保留 | 无待办 | 否 |
| R06 MM12 | 仍开（维护） | `:345`；两 TS PATH python（本人实测） | 保留 | T01 原测试维护者 | 否 |
| R06 MM13 | 已闭合（信息） | `:346`；规模信息接收 | 保留 | 无待办 | 否 |

### 5.5 MM 160 清单末 13 行（#148–#160，4 未知／4 不适用／5 部分）—— **与额外 13 是不同集合**

按 `disposition.md:15` 与 R10 原稿 §11.3(a)（本人亲读）：

| 档位 | 项 |
|---|---|
| 无法确认 4 | #148 逐行人审、#149 第二个客户前设计数据模型、#150 解释 AI 修复引入的新缺陷、#151 部署/回滚/云账单 |
| 不适用 4 | #152 支付值班、#154 审计员演示、#157 技术负责人否决、#159 调试 AI 写不出的代码 |
| 部分适用 5 | **#153** 漏洞当周打补丁、#155 QA、**#156** 活跃库迁移保全、#158 全客户等价、#160 一年后仍记得为什么这样建 |

**本轮对末 13 的处置**：分布 **4／4／5 维持不变**（本人已按当前源码逐条复核 §4 表内 #148–#160，无一项需要再改档）。#153 与 #156 的**上调理由本轮由本人独立复核成立**：#153 见 §4（Electron/依赖安全更新跟进面存在但无自动化）；#156 见 §4（迁移门禁与事务升级在位，活跃库演练未实施）。**#153、#156 不因此关闭任何 HOLD，也不新增门禁。**

### 5.6 R10 Z 侧 Top 9（合法 9 条；R10-10 为序号笔误，不构成第十条）

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R10-01 | 仍开（门禁） | `:352`；CI43 实际 failure；本候选无新 CI | 保留，数值更新 | ROOT；精确 push/CI 票、merge 前 | 否 |
| R10-02 | 仍开（未证根因 HOLD） | `:353`；**本轮新事实**：CI43 的 C1 失败形态**已变**（13086ms、首 readiness 成功、child close 1/null），不是旧 helper12 TypeError，也非 45/90s timeout → 原「`app.isPackaged` undefined TypeError」主题已不适用于本轮；**但新根因仍 UNKNOWN** | 保留；**主题按本轮事实更新为「CI43 Windows C1 异步失败，根因 UNKNOWN」** | ROOT/原 T02；真实 CI 归因窗口 | 否 |
| R10-03 | 仍开（维护） | `:354`；**本人实测** `index.ts:894-896`（见 R11-T05） | 保留 | 契约 owner；下次整理 | 否 |
| R10-04 | 仍开（未确认观察） | `:355`；**本人实测** `storage.py:1151`/`:1170` 无 ORDER BY；`run-engine-tests.py` 的 skip/xfailed/xpassed 处理与 pytest 原生一致（本人读全文） | 保留 | witness 选取：T01；CI/skip 建议：原 ROOT/原 T02 控制层维护票 | 否 |
| R10-05 | 仍开（供应链卫生） | `:356`；**本人实测**三 wheel 仍在，`pyproject.toml` 只用 fr201.3 | 保留 | T11；merge 后受控维护 | 否 |
| R10-06 | 部分采纳（同源窄盲区） | `:357`；共享 oracle 窄面在位（`test_mainline_read_work_budget.py` 重实现 read-admission 记账公式、两 e2e 各有 `canonical()` 副本）；独立证据渠道（SQL trace/authorizer/hashlib/product 枚举/golden）在位 | 保留 | 原 T02 测试维护/CI 控制层维护票 | 否 |
| R10-07 | 仍开（测试质量） | `:358`；自指断言（`parametersHash: job.parametersHash`、`planHash: marker.planHash`、stateVersion 仅 `>=`）在位 | 保留 | 同 R10-06 | 否 |
| R10-08 | 仍开（维护） | `:359`；`ui-observation.ts` nativeBUTTON enabled 判据仅支持当前 light-DOM（fail-closed）；`native-driver.ts` 450×100ms 就绪轮询在位（本人读差异） | 保留 | 原 T02 native/测试维护与 ROOT | 否 |
| R10-09 | 不采纳原强论断（治理观察） | `:360`；**本人实测**：M0 计划**已有两份版本化副本**（`docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`，SHA256 均 `c289a1cd…`，35812B）→ 「未版本化/无 hash/只未跟踪」**不成立**；仅剩「AGENTS 引用路径失效」＋「未跟踪冗余副本维护」 | 保留原处置（不采纳强论断） | ROOT/AGENTS 指南维护归口；本票不改共享 AGENTS | 否 |
| ~~R10-10~~ | **序号笔误，不被接受为第十条** | `:362` 逐字「Z R10-10 为串号笔误，合法 Top 仅 R10-01…09」；`version-map.json` `audit02ResidualLimits[0]` 同载 | **不构成发现项**；不映射到任何条目 | — | — |

**回放限证复核**（任务书要求区分）：postwrite 的 **L211–213 是 replay**、**L231–233 是后续合法 Read**，本方复核 `packages/engine/tests/test_mainline_postwrite_admission.py` 的对应段落结构，二者**不作为同一 replay 证据**；该区分本轮维持。

### 5.7 R10 MM 侧 Top 10 ＋ 新增 T11／T12

| stableID | 当前适用性 | 依据 | 处置 | owner/窗口 | 阻断 |
|---|---|---|---|---|---|
| R10-T01 | 保留（合并门禁） | `:368`；CI43 failure 已实际发生 | 保留 | ROOT 精确 push/CI 票 | 否（CI 条件可阻断 merge） |
| R10-T02 | 保留 | `:369`；CI41 根因 UNPROVEN；**本轮 CI43 提供了新失败形态但根因仍 UNKNOWN** | 保留 | 未来 CI 证据接收标准 | 否（CI 条件） |
| R10-T03 | 保留 | `:370`；CI43 Windows FR201 180002ms，末 rev21 权威终态未知（O072 原件） | 保留 | 未来 CI 证据接收标准 | 否（CI 条件） |
| R10-T04 | 保留（覆盖面限制） | `:371`；`ui-observation.ts` fail-closed 形态限制在位（本人亲读全文） | 保留 | 原 T02 测试维护者 | 否（CI 条件） |
| R10-T05 | 撤回原证明与原建议，保留维护边界 | `:372`；**本方按当前源码复核**：`updateObservationSlot` 的兜底分支固定字段开销 212B、base64 14668B、当前 stage 34B → 合计 14914B，stage 总预算 1504B、余量 1470B；**仅静态预算，非当前可达性证明** → 与任务书限证一致 | 不采纳原缺陷强推论；采纳撤回/收窄，保维护边界 | 原 T02 测试维护者；本票不改码 | 否（CI 条件） |
| R10-T06 | 撤回「命名与门禁语义不一致」缺陷判定 | `:373`；**本轮新事实**：CI43 Windows diagnostic step **实际 success**，即该 step 绿且 job 仍因 E2E 红 → 「命名与门禁语义不一致」的现实后果已不成立（step 绿≠job 绿，E2E 失败才是 job 红因） | 不采纳命名/门禁矛盾推论；不加 `continue-on-error` | ROOT／CI 维护窗口 | 否（CI 条件） |
| R10-T07 | 保留（HOLD） | `:374`；vendored rdflib 为本地改版 wheel，供应链与许可独立 HOLD；**本人实测**三版本并存 | 保留 | 发布/供应链 owner | 否（CI 条件） |
| R10-T08 | 保留 | `:375`；**本人实测** 制品上传范围扩大＋`failure-traces-linux` 为 `always()`，无 `if-no-files-found` | 保留 | CI 维护票 | 否（CI 条件） |
| R10-T09 | 撤回「无机器校验」表述，收窄为「未穷尽 Unicode 全空间与未来组合」 | `:376`；**本人亲读** `t02-manual-fact-id.test.ts:53-76`：真实 `Store._fact`＋`digest` 的 Python 机器交叉核验存在（显式 `.venv/bin/python` 路径） | 部分采纳（已有机器核验；只保未穷尽边界） | 原 T02 测试维护者；本票不改测试 | 否（CI 条件） |
| R10-T10 | 撤回「renderer 更早拒绝⇒缺陷」推断，降为可选注释澄清 | `:377`；**本方按当前源码复核**：`manualFactPlan` 的重叠拒绝条件本轮**再次改写**（由「同 slot 恰好一条」改为「存在任一受管/同值/替换值冲突行即拒绝」），而引擎 `_check_slot` 条件为 `row["id"] not in excluded and (row["id"] == reserved_id or (row["object"] is not None and (single or row["object"] == value)))` —— 二者仍**不是同一判据**；但 `reserved_id` 与 ID 绑原声明是设计 → **该推断仍不成立**，维持降级为注释澄清 | 不采纳原缺陷强推论；保留维护边界 | 原 T02 前端归口；本票不改码 | 否（CI 条件） |
| R10-T11 | 部分采纳 base/hash 不同事实；不采「生成锚应随 head 更新或来源失真」推论 | `:378`；**本人复核** fixture 的 `sourceStorageSha256`／`sourceRdfSnapshotSha256` 指向 base（本人读 fixture 与对应源码 hash），而 `scope=generated` 明确为生成时来源；**不强制刷新来源针** | 部分采纳（只采「生成来源与 head 不同」事实） | 原 T02 fixture 维护归口 | 否（CI 条件） |
| R10-T12 | **不采**「仅 3/9 有断言」与「补五类」建议 | `:379`；**本人亲读** `packages/engine/tests/test_storage.py:190-223`：`@pytest.mark.parametrize("rule", RULES["rules"])` 动态遍历**全部 9 条**规则并做正反断言 → 「仅 3/9」被反证；**不加 5 测试门禁**；静态断言 ≠ 本轮运行 ≠ 四具名下游 GUI 验收 | 不采仅 3/9 与补五类建议；原静态九行参数化断言在位，独立 GUI/HOLD 不关闭 | 不采建议 | 否（CI 条件） |

### 5.8 本轮新增/更新的本方条目

| stableID | 类别 | 内容 | 依据 | 处置 | 阻断 |
|---|---|---|---|---|---|
| R11-S01 | 源码边界观察（P3） | ownership 详情分页的「段数×页大小×页数」常量一致性（见 §2 R11-T06） | `apps/desktop/src/renderer/src/ontology/mainline-ownership.ts:26,33`＋`domain_changesets.py` 的 `MAX_DOCUMENT`/`SEGMENT_BYTES` | 交原 T02 契约归口；本轮不改码、不新增门禁 | 否 |
| R11-F01 | 事实订正 | **M0 计划已被版本化**：两份 35812B 同 SHA `c289a1cd…` 副本在树内；AGENTS 旧路径失效 ≠ 整计划未版本控制 | 本人 `shasum -a 256` 实测两处副本 | 与 R10-09 处置一致；本方**独立复核成立** | 否 |
| R11-F02 | 已核事实（不构成问题） | O074 的 `prettier --write` 确曾改写 FR 文件，但提交内容与 Git 实际差异的 9 个 hunk **逐字同构**，未越出授权范围，未改原断言/timeout/title/bridge/callback | 本人 `git diff 2d6 d1aca` 与 `committed.diff` hunk 头对比（§3.5） | 记为已核事实，**不需 owner 决策** | 否 |
| R11-F03 | 结构澄清 | 「额外 13（R06 MM01–13）」与「MM 160 清单末 13 行（#148–#160）」是两个不同集合，本报告分开处置 | `disposition.md:15`＋R10 原稿 §11.3(a) | 分别列于 §5.4 与 §5.5 | 否 |

---

## 6. 门禁与完成度边界

**当前 push 前源码技术阻断：无。** 依据：§2 六项均判定「否」；§5 全部 31＋78＋20＋13＋9＋10＋T11/T12 条目逐项复核后**无一产生 push 前源码阻断**；本人亲读的实现差异（契约双端 matcher、引擎写准入与 ownership 详情、renderer 会话与视图、主进程/preload、CI 与脚本、两个 e2e 修补）中未发现功能缺陷、越权写入、契约不一致或验收弱化。

**但以下条件明确未满足，且不由本报告放行：**

1. **完整平台 CI**：CI43（run 40406339836／attempt1／head `cfcc876e`）总体 **failure**；Quality failure（完整 3769 NOTRUN）、Windows failure（C1 failed＋FR201 timedOut）、macOS success。本候选 `d1aca3e3` **无任何新 CI**。
2. **Windows C1 异步根因 UNKNOWN**；**Windows FR201 累计超时根因 UNPROVEN**。
3. **完整 C1／M0 验收、新包与完整包内 GUI**：未做。旧 094 包 912 成员仍只是旧有界证据。
4. **全部独立 HOLD 保留、逐一关闭数为 0**：签名／公证、wholeApp 法律与 `_distutils`、隐私产权与供应链、跨 OS 与参考 8GB 设备、Q5 容量与旧超限库恢复、损坏 SQLite 物理保护、unknown parser／N3／Store／坏快照、Undo GUI 其余面、其它 ownership 家族与未具名下游、native engine 与 named App 未知退出码、Windows 后代 UNKNOWN、原 79F、裸 PATH python、错误码集合差、definitions 早期 wire、standalone EOF、无序见证、4299/4300、四具名下游 GUI。
5. **整体合并可用仍为 2/17**；Goal／M0／发布未完成；T04 不推进；本轮**不授权** push／PR 修改／新 CI／rerun／cancel／merge。
6. **本报告是技术审查，不是产品放行**：它不把「适用性分类」当作产品通过数，也不把历史 ConditionalPass 转移为本轮结论。

**未来 merge 门禁（维持原口径，本轮不放宽）**：同受审实现／测试／CI／依赖下，3769 全集逐项 PASS 或原有据条件 skip、自然 0、零失败／早停／取消／timeout／NOTRUN；Windows 全部后继步骤实际 success；Quality packaged recovery 步骤自身 success；原 15/20 分钟预算不变；case7 若复发须定因并处置；精确 merge 票与 remote develop 实际 SHA/tree/功能复核另验。

---

## 7. 建议（原 owner，不新增授权）

1. **ROOT**：发精确 push/CI 票并接收完整三 job 回单；本候选 `d1aca3e3` 无新 CI，不可据 R10 或本轮结论放行 merge。
2. **ROOT／CI 维护归口**：CI43 已在真实 Windows 上产生**新失败形态**（首 readiness 成功→child close 1/null→13086ms 失败），且 O074 的新 catch 将首次落盘原字节／read/parse/attach 结果；下一获准完整 Windows CI 是**唯一**能取得该平台样本的机会，请在接收标准中明确核这些新证据。
3. **原 T02 契约归口**：`OwnershipDetailArgs` 的 TS 类型宽于 schema（R11-T05）与 ownership 详情分页常量一致性（R11-S01）落在同一归口，下次整理时一并处理。
4. **T01 storage 归口**：`storage.py:1151`/`:1170` 的确定性排序（R11-T04）；本轮新增 `SingleDeclarationConflict` 取「前两条记录」，使该观察有了实际消费者。
5. **T01/T02 方法接线归口**：裸 ownership 详情家族、错误码集合差（新增 `project.ownership.detail` 相关项）、definitions 早期 wire 分类。
6. **原 T02 fixture 维护归口**：R10-T11 的生成来源 hash 表述（可选澄清，不强制刷新）。
7. **发布/供应链 owner（T11）**：vendored rdflib 三 wheel 冗余与供应链/许可 HOLD。
8. **ROOT 文档 owner**：F05／F-R09-08／R06 MM04 的状态登记（本方只读，未代登记；`status.md` 与 `m0-checklist.md` 仍停在 R10/67b7 段）。

---

## 8. 本轮事实补正（对输入摘要的独立核对结果）

1. **O072 的 Quality 失败原文是「仅 `docs/m0-checklist.md` 被 globalPrettier 告警 → exit 1」**，不是「仅 M0 多余一个 LF」——后者是 O072 的**诊断层结论**（`INDEPENDENT-QUALITY-FORMAT-DIAGNOSIS.json` 的 `byteFacts[0]`：raw 13999B→最小删除 offset 12140 的 1 个 `0a`→13998B，格式化结果与该最小删除逐字相同）。两者都成立，但层级不同，本报告按诊断层引用。
2. **CI43 三 job 的真实合成 checkout 是 `a40f965c2a169ba98a0d3139eef198de6d5d78f3`**（parents `583c05c7`＋`cfcc876e`，tree `26d5450c…`），**不是实际 merge**；旧 135 pins 保护成立。
3. **O073 确为「仅删 M0 offset 12140 一个 LF，13999→13998」**，其余 1402 源/旧 5 build/保护项同；**这是对 O071 的补充，不是第二个当前 M0 源码 pin 错误**——旧 round10 manifest 与 O071 仍绑定历史 `cfcc`，由 O073 外置桥接，未改历史 manifest。任务书关于「O071 只格式化新片段、漏了组合空行」的表述，在三个目录中**无逐字原文**；最接近的可核原件是 O072 `QUALITY-FAILURE-INITIAL-FACTS.json` 的 `appendProof`（`joinLiteral="old + LF LF + alreadyformatted tail"`，`hypothesis="Excess blank lines at join. Not yet formatter confirmed"`）与 `diagnostic-m0-full-format.diff`（多余空行恰位于旧段落与新标题之间，`withinOldPrefix=false`）→ **该归因方向合理但属推断，非原文断言**。
4. **O074 的实际运行标签是 `2d6bc23f` + 精确 2 WIP**，提交后两文件 Git blob 与被测 WIP **逐字相同**（本人实测：2d6 blob = O074 `before-source/` 值；d1aca blob = O074 提交后源值）；**不能写成「先在 d1aca3e3 运行」**，但内容证据成立、不因标签变化失效、**无需无改动复测**。**本机 C1 成功 ⇒ 新失败 catch 的真实平台附件未被验证**，只有纯 mock 与静态证明。
5. **R10-T12 的「仅 3/9 有断言」被本人亲读反证**（`test_storage.py:190-223` 动态参数化 9 条规则的正反断言）→ 该建议不采、不加 5 测试门禁。
6. **R10-T09 的「无机器校验」被本人亲读反证**（`t02-manual-fact-id.test.ts` 用真实 `Store._fact`＋`digest` 的 Python 交叉核验，显式 `.venv/bin/python` 路径）→ 收窄为「未穷尽 Unicode 全空间与未来组合」。
7. **R10-T06 的命名/门禁矛盾在 CI43 上不再产生现实后果**：Windows diagnostic step **实际 success**，job 红因是 E2E 两个失败，非该 step。判定仍维持「不采命名矛盾推论」。
8. **M0 计划确已被版本化**（两份同 SHA `c289a1cd…` 35812B 副本在树内）→ R10-09 的「未版本化/无 hash/只未跟踪」不成立；仅剩 AGENTS 引用路径失效与未跟踪冗余副本维护。
9. **`store.py` 的 `SingleDeclarationConflict` 取「前两条记录」且两处 SQL 无 `ORDER BY`** → R11-T04 的未确认观察在本轮有了实际消费者，但**无构造性反例，仍不升级为缺陷**。
10. **子代理观察「074 曾 prettier --write FR 文件」成立但结论不成立**（R11-F02）：提交内容与 Git 实际差异 hunk 逐字同构，未越权。

---

## 9. 结论

**ConditionalPass（附条件通过）**，限定为**推送前技术审查阶段**，针对 base `583c05c` → head `d1aca3e3` 的完整累计候选。

- **成立的部分**：本人亲读并核对了全部产品/契约/引擎/renderer/主进程/preload/CI 实现差异与新增测试、fixture、契约正文；核了 CI43 真实失败、O073 一字节修复、O074 两处观测修补原件；逐项承接了原 31／权威 78／R09 新增 19＋OBS／额外 13／Z Top9／MM Top10＋T11/T12，并新增 1 项 P3 源码边界观察（R11-S01）与 3 项事实订正/澄清（R11-F01/F02/F03）。**未发现当前 push 前的源码技术阻断。**
- **不成立的部分**：这不是无条件整候选 Pass，不是完整 CI 通过，不是产品放行。CI43 总体 failure；本候选无新 CI；Windows C1 异步根因 UNKNOWN、FR201 累计超时根因 UNPROVEN；全部独立 HOLD 与 UNKNOWN 原样保留、**逐一关闭数为 0**；整体合并可用仍 2/17，Goal／M0／发布未完成。
- **责任与授权**：本方只读，未改任何源码/测试/config/依赖/预算/验收，未 push/CI/merge，未重置/采购/升级，未读取另一作者本轮产物。**发现实质源码问题给精确证据与最小建议，由 owner 决策；本报告不自行修源、不追加功能或验收、不授予执行权限。**
- **后续**：自然终态后如需本人对事实纠正或意见处置作必要追加，同任务追加且原稿前缀保留，不默改历史。

**R11-F03 收束**：本轮把「额外 13」与「MM 160 清单末 13」分开处置、把 R10-T12 的反证落到本人亲读行号、把 R11-T06 标为未证明可达的边界观察——这三项构成本轮相对 R10 的**实质增量**（其余为按当前源码的独立重核与维护性订正）。

**D8 未使用。** 本报告不嵌本方最终 bytes／hash（由 owner 保存实测）。

---

## 10. 本轮追加（同一 R11 会话的自然终态追加节；原 §0–§9 全部原字节保留，本节为**唯一有效替代／新证据**）

> **追加性质声明**：本节由 owner 在同一 R11 会话内追加，**不修改 §0–§9 的任何原字节**（追加前实测：`report.md` = 105413B／SHA256 `a737932ee4dbf4d228532ec246845d7148bc7609b9458fbb326ddee1d9d2e42a`／以 LF 结尾）。本节与上文冲突之处，**以本节为准**；不冲突之处，上文原字节继续有效。冻结身份不变：cwd `…/.worktrees/T02-s1-review-fixes`、branch `feature/weekly-t02-fr200-fr201`、base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`、head `d1aca3e34ec4d00095c10a14a413efb552d3776a`、tree `389848f84fe60325bcdcd1b7827a7ee6e039a0e1`、sole parent `2d6bc23fdc4f13afcceb7b79c8059ee3c74abbe8`、43 提交／125 差异路径／1403 tracked 源叶。
>
> **本轮职责与限制（承接上文，不放宽）**：只读工程与必要既有原证据；**未运行** check/vitest/pytest/build/package/install/formatter/HMR/产品 GUI/SQL/bridge，**未制造故意失败探针**；未改任何源码/测试/config/依赖/预算/忽略项/验收；未 `git add`/`commit`/`push`/切分支/CI/merge；未读取另一作者本轮 R11 目录、报告、意见或 verdict。§10 内出现的全部执行数字均标明**既有原件身份**或**本人只读实测**，**不冒本人运行**。CI43 总体 failure、Windows C1 异步根因 UNKNOWN、FR201 累计超时根因 UNPROVEN、本机 C1 成功未触发失败附件、整体 2/17、独立 HOLD 逐一关闭数 0、本候选未 push/无新 CI/未 merge —— **全部限制原样保留**。

### 10.1 必要覆盖补读结果（订正 §3.6 第 2 项与 §9「全部已审」表述）

**订正**：上文 §3.1 第 3 行末段与 §9「成立的部分」称「本人亲读并核对了全部产品/契约/引擎/renderer/主进程/preload/CI 实现差异与新增测试、fixture、契约正文」，而 §3.6 第 2 项同时自承「未读全文的新增/修改测试文件」。**该自相矛盾以本节为准：上文该处表述订正为「实现差异已全读；新增/修改测试与 fixture 正文在本节 §10.1 内补读完成」**。§9 的「全部已审」在本节补读完成后成立，但**成立范围限于下表逐条列明者**。

**本轮本人亲读全文（逐行，读到 EOF）——新增测试 11 路径**：

| 路径 | 行数 | 本人核到的断言要点（含反例核对） |
|---|---|---|
| `packages/engine/tests/test_mainline_language_input_rejection.py` | 326 | `R03_REFUSALS`（`@1`／`@zh1`／4301 位整数）× manual／edit 双路径；`test_digit_subtags_are_grammatical_separate_from_canonical_case_policy` 断言 `term(value).n3()` 逐字保留数字子标签；独立 stdio 子进程路径含 `database_files` 物理字节快照比对 |
| `packages/engine/tests/test_mainline_manual_input_rejection.py` | 1034 | L70–75 `assert_rejected` 断言 `INVALID_REQUEST`/`protocol.invalidRequest`/`{"field":"params"}` 且 ALIAS 不外泄；L148–222 非输入类失败保持 `INTERNAL_ERROR`+HOLD+UNKNOWN 且后续读为 `STORAGE_FAILURE`；L531–582 parser/N3 未分类失败保持 UNKNOWN；L689–738 保留身份冲突产生 `OWNERSHIP_CONFLICT`+`detailRef` 且仅诊断行变化；**L809–909 三 reason ownership 详情全页分页＋字节 hash＋document 字段断言**；L912–1034 singleDeclaration 真实 home＋两条 existing locator＋后续移除冲突值再提交 |
| `packages/engine/tests/test_mainline_postwrite_admission.py` | 860 | L33–60 终检边界与 2742<4096 tail 证明；**L211–213 `job.create` replay 与 L229–231 后续合法 Read 为不同证据（R10 回放限证点成立）**；L323–351 foreground 不可借 successor/background；L376–457 after_commit 不可退款／cleanup 失败保留原因／settlement 失败保 UNKNOWN；L501–546 clean_close 交棒；L561–659 successor 不接管未结算前任与在队/活跃 job |
| `packages/engine/tests/test_mainline_read_work_budget.py` | 559 | L31–57 `scalar_profile` **重实现产品 read-admission 记账公式**（同源复刻盲区在位）；L115–159 真实历史/opaque 边界构造；L384–419 64MiB work 上限在 lower 与 authorized-plan 两阶段的拒绝位置，**L415 以 SQL trace 断言 `json_extract` 是否出现（独立于产品公式的证据渠道在位）**；L437–476 真实重复解码历史边界；L493–559 损坏行四类与 `json_extract` 被拒时的 `STORAGE_FAILURE`+HOLD+库不变 |
| `packages/engine/tests/test_mainline_postwrite_rows_budget.py` | 395 | 真实 243 行×5 列有序结果逐行断言（`rowKey=digest([resultId,payloadSha256,index])`、`cells` 逐个 IRI/n3 全等）；固定费 `{bytes:1114112, objects:8192, work:134217728}` 每页一次；`test_final_fee_refusal_preserves_scope_and_same_host_continues` 断言 RESOURCE_LIMIT 后**同 host 仍可继续合法读取**；页作用域不可出借/退款已付费用；同一 prepaid 材料不可二次消费（`INVALID_STATE`） |
| `packages/engine/tests/test_mainline_postwrite_text_budget.py` | 320 | 冷历史＋真实查询 worker＋有界文本页费；56309 字符（多字节变体 112782／112784 canonical）跨多页拼回**逐字节等于原文**；`startUtf8Byte` 单调、cursor 不重复、每页 ≤32768 UTF-8 且页字节/帧字节双限内；固定费 `{bytes_:528384, objects:256, work:1052672}` 每页一次；cursor 回调撤销后在编码器之前拒绝（`PERMISSION_DENIED`，`encoders_after_revocation==[]`） |
| `packages/engine/tests/test_mainline_dispatch.py`（修改，+523/-0） | — | **本人亲读该文件 base→head 完整差异**：新增 `ownership_fixture`／`ownership_pages` 与 12 个用例 —— 大 locator 详情完整＋纯读＋有界（`len(pages)>=2`、`totalBytes>32768`、逐段 sha256、**读详情不新增 cursor 行**、库 dump 全等）、四类损坏 → `STORAGE_FAILURE`+HOLD、诊断段失败**整体回滚**（`INTERNAL_ERROR` 且 `detailRef` 不外泄）、诊断不得污染已准入的完整读取（`RESOURCE_LIMIT` 且读结果不变）、私有准入保持 core-only 向量、坏 blob 在 intern 复用前有界、原始段预算在 JSON 解码前拒绝、重复命中复用至行上限后新上下文回滚、旧三字段详情不臆造 locator、**详情引用不跨后继会话**（`NOT_FOUND`，新会话新 preview 产生不同 ref） |
| `tests/unit/t02-ownership-detail.test.ts`（新增） | 843 | 四 reason 映射不改原值；多段真实拼装且保留 >17KiB 原始 Unicode ID/owner/sourceRow 与 null；**14 类页面变异全部拒绝且只读 1 页**（project/ref/startOrdinal/segment ordinal/offset/length/hash/base64/总量/段数 513/无前进/过早 complete/缺段/重复段）；后页六类坏值拒绝；公开重组器拒绝文档 hash/project/旧三字段/非法 reason；公开 SHA await 后仍做上下文守卫；私有页快照归属；Session 层：四 reason 只发布已验证 VM 且**永不创建事务**、非法 detailRef 不触发 getter、伪造 code/message/params 不被当作授权查找、八类失败安全降级不自动重放、7 类事件同步清空、5 个阶段迟到成功/失败不改变快照、5 类活动上下文复核、微任务间隙 fence、只读视图无写入面 |
| `tests/unit/t02-manual-preview-lifetime.test.ts`（新增） | 596 | 实际 Page 组件在 instrumented hook 下的挂载/清除：`reading`/`unavailable` 文案、`stale` 即便 ready 也清空、9 类输入/结构/会话动作清空详情、真实 Session 在输入处理器后不得恢复迟到详情；摘要完成后**最新未变三元组只 prepare 一次**（`toHaveBeenCalledExactlyOnceWith`）；13 类变更后**拒绝迟到 hash**（含 input ABA／source ABA／project switch／layout reattach／session replacement）；相同三元组仍以新预览取代旧预览；旧摘要失败不在新草稿上显示「无法预览」；retire 与「layout detach 先于普通 dispose」下阻塞旧 hash 并**不调用 `getActiveProject`/`previewProjectChangeset`**；当前摘要错误可见而脱离挂载的错误不可见；同步 discard 订阅者改草稿时不得采纳更新一代 |
| `tests/unit/t02-ownership-detail-view.test.ts`（新增） | 138 | 三 reason 文案（保留身份冲突／相同事实的来源冲突／单值属性槽位冲突）与 singleDeclaration 的「单值属性声明与现有事实冲突」；**只读**（无 button/input/form/a/script/iframe，无「确认/提交/写入/自动执行」字样）；16KiB 以上历史 ID 不规范化、不截断（无「…」）、**不生成 href**；HTML-like 值仅作转义文本出现（`split(escaped(hostile))` 长度 8）且不出现 `href/src/onerror` 属性 |
| `tests/unit/ui-observation.test.ts`（新增） | 194 | 纯合成 DOM-shaped 观察回归：移除按钮即不完整快照直到同一操作回执出现；回执重复抛 `Duplicate`；native disabled／最近 disabled fieldset 首个 LEGEND 豁免／ARIA 大小写与不 trim／shadow host 链；重复匹配 `Duplicate`、歧义 `Ambiguous`、aria-label 覆盖、未连接与 shadowRoot 形态 `Unsupported`（fail-closed）；规范化文本与未规范化输入值分离；回执首段身份、精确已读版本、无 pending 三者并存；**单一有界槽 ≤16384B 且保留其他注解** |
| `tests/fixtures/t02-manual-fact-id.json`（新增） | 139 | 13 个 golden case（真实 UI 三元组、中文 IRI＋`@zh`、非 BMP emoji、含引号/反斜杠转义、多行字面量、`"7"`／`"7"@zh`／整数／decimal／boolean／date、NFC 与 NFD 分解形）；每 case 同时给出 canonical 串与 `fact.id`（64 hex）；文件自述来源为**实际隔离 Python `Store.canonical`/`digest` 生成并经 `Store._fact` 校验** |

**本轮本人亲读完整差异（修改测试 8 路径 + e2e 3 路径）**：`tests/unit/native-driver.test.ts`（+358/-38）、`tests/unit/t02-mainline-consumer.test.ts`（+262/-5）、`tests/unit/t01-mainline-real-runtime.test.ts`（+286/-1）、`tests/unit/t02-mainline-metadata.test.ts`（+190/-0）、`tests/unit/t01-business3-contract.test.ts`（+89/-0）、`tests/unit/t01-mainline-contract.test.ts`（+65/-0）、`tests/unit/t01-mainline-project-service.test.ts`（+68/-0）、`tests/unit/t01-mainline-ipc-delivery.test.ts`（+29/-0）、`tests/e2e/native-driver.ts`（+246/-58）、`tests/e2e/mainline-consumer-first-ack-loss.spec.ts`（+65/-12）、`tests/e2e/csp-lifecycle.spec.ts`（+59/-4）。

**修改测试差异的本人核到要点**：
- `native-driver.test.ts`：socket 永不回应的 bootstrap 拒绝并清理（`kill('SIGKILL')`、listener 清零、`vi.getTimerCount()===0`、helperRequests 为 0）；退出后可保留有界可执行文件与已排空进程输出诊断；**排空受原 deadline 约束且退出后不再发 helper**；等待映射不加载 shim，`app.whenReady`/`isReady` 各一次，**`app.focus`/`app.exit`/`commandLine.hasSwitch` 均不得调用**；helper 只加载一次。
- `t02-mainline-consumer.test.ts`：受控 `OWNERSHIP_CONFLICT` 保持可行动（error=`OWNERSHIP_CONFLICT`、phase=`idle`、prepared/pending/receipt 均 undefined、**快照不含 detailRef 与 messageKey**、四个写接口均未被调用），**下一次合法 preview 成功**且带同一 `baseRevision`；伪造 code/message/params 与抛异常均降级为 `INTERNAL_ERROR` 且不外泄 secret；多值人工 edit/remove 不触碰兄弟支撑记录；**不同 RDF 拼写不折叠**（`"value"` vs `"value"^^xsd:string`、`"value"@zh` vs `"value"@en`、`"01"^^integer` vs `"1"^^integer`）；owner/source_row/managed_value 冲突围栏（`MANAGED_FACT_REQUIRES_OWNER`／`AMBIGUOUS_FACT_SUPPORT`）；原/替代值精确支撑与定义重叠均围栏。
- `t01-mainline-real-runtime.test.ts`：**实际 preload/named IPC/service/stdio** 贯通四个 ownership family（reservedIdentity/sameStatement/singleSlot/singleDeclaration）＋ large；真实 `ipcMain.handle` 注册与 `contextBridge.exposeInMainWorld` 捕获，真实子进程 stdout 收集。
- `t02-mainline-metadata.test.ts`：class(rdfs/owl)／objectProperty／dataProperty／individual 五变体矩阵行。
- `t01-business3-contract.test.ts`：`matchesOwnershipDetail` 对 `[2,55,56,63,64,65,32767,32768]` 原始字节逐一比对 **Node 真实 SHA-256**。
- `t01-mainline-contract.test.ts`：完整 ownership 位置文档（含 40000 字符 subject）跨段重组。
- `t01-mainline-project-service.test.ts`：`project.ownership.detail` 目录项与「ACK 未回即持有」路径。
- `t01-mainline-ipc-delivery.test.ts`：详情页沿用同一 sender/frame 校验与缺 ACK 持有（错误 frame 的 ACK 不消费、正确 frame 才消费）。
- `native-driver.ts`（e2e harness）：45s 预算改为单次 `performance.now()` 基准＋末尾一次性计时；新增 `waitFor` 取消注册表与 cleanup；新增 readiness 握手（检查 module cache 的 electron 映射、`process.type==='browser'`、app/dialog/BrowserWindow API、`await app.whenReady()`），**helper require 只发一次不重试**；退出前置错误语义细化；catch 中若子进程已退出则按原 deadline 排空并附 diagnostics+cause；finally 统一摘除 listener/timer/socket 并 SIGKILL。
- `mainline-consumer-first-ack-loss.spec.ts`：用 `observeUI`/`receiptHasOperation`/`reconciliationReady` 替代原 `receipt.count()` 轮询；**原强断言全部保留**（marker 全字段、job `matchObject`、`commitCalls===1`／`executeCalls===0`／`lostAckCalls===0`、revision===1、definitions 精确相等）。
- `csp-lifecycle.spec.ts`：改动**只在**原 native 失败 catch（区分 read/parse/attachment 三类失败状态，保留原始字节并 attach `c1-native-failure-original-bytes`，另 attach capture 状态 JSON），**最后仍 `throw` 原异常，未削弱任何断言**。

**本轮本人亲读完整差异（契约增量 4 路径）**：`packages/contracts/v2/registry.json`（business3 与 changesets 两处 `project.ownership.detail` 加入方法清单，+4/-2）、`packages/contracts/v2/binding-regressions.json`（17 处 `registryHash` 由 `058ed1be…` 更新为 `5e097b7e…`，其余字段未变）、`packages/contracts/v2/fixtures.json`（+350/-96：新增 `named ownership request`（valid）、`ownership no null continuation`（**startOrdinal=1 且 documentHash=null → invalid**）、`ownership wire issuer forbidden`（携带 `ownerId` → invalid）三例，其余为 `registryHash` 同步更新）、`packages/contracts/src/v2.ts`／`index.ts`／`python/contract_v2.py`／`v2/schema.json`（上文 §3.1 已列，本轮未新增读）。

**e2e `t02-fr200-fr201.spec.ts`（base→head 新增 2174 行）的覆盖情况**——**本人未逐行读全文**，采用「子代理逐行读＋本人回原件复核关键断言」方式（见 §10.1 末「子代理定位」说明）：
- 本人**回原件复核**的关键断言：`tests/e2e/t02-fr200-fr201.spec.ts:1590-1619` 冲突归属详情断言（`region` 名称「首个阻断冲突定位」全等；`dl > dd` 精确为 `[revision,'保留身份冲突']`；`list` 名称「原始事实定位」项数 2；两项 heading 为 `['现有记录','传入记录']`；每项 5 个 dd 字段为 `[id, '人工（owner = null）', '无源行（sourceRow = null）', subject, predicate]`）；`:1461` fact id 仅以 64 位十六进制**形状**匹配（`expect.stringMatching(hash)`），未按产品 SHA-256 重算；`:345-361` 的 `canonical()` **复刻**引擎 `storage.py` 的 sort_keys 紧凑 JSON，`:362-374` 的 `record()` **复刻** `mainline-ontology.ts` 的 payload 结构。
- 本人**独立实测**：`grep -c rejectCallerObject` = **16**（子代理称「约 42 次」**不采**，见 §10.6）；文件内 `grep 'pageSize\|rowsPage\|textPage\|分页'` = **0 命中**、`grep 'HOLD\|hold\|RESOURCE_LIMIT\|settlement\|结算'` = **0 命中** → **分页、读准入/HOLD、终检与结算、预算类行为在该 e2e 文件中零覆盖**（与子代理结论一致）。
- **「43 拒绝」口径澄清**：§5.x 与 `docs/reviews/T02/status.md:17/:21` 的「43 拒绝」是**跨轮历史累计口径**（named 24/24 + 98 事务 + 43 拒绝等），**不是本 e2e 文件内的断言计数**；本文件内 `rejectCallerObject` 调用点为 16 处（其中含循环）。本方**不把该文件冒称为「43 拒绝」的直接证据来源**。

**子代理定位 + 本人复核（本轮新增 1 个 explore）**：e2e 覆盖勘察子代理返回 A/B/C/D 四文件要点、断言清单、同源复刻与平凡断言清单、覆盖缺口；本人**逐条回原件复核**了其中作为结论依据的部分：`t02-fr200-fr201.spec.ts:1590-1619`（本人亲读，断言内容与子代理描述一致）、`:345-374`（同源复刻成立）、`:1461`（形状匹配成立）、`:1074/:1410-1583`（`rejectCallerObject` 16 处，本人实测修正子代理的「约 42 次」）、`ui-observation.ts:145-152`（`receiptHasOperation`/`reconciliationReady` 语义）、`csp-lifecycle.spec.ts` 差异仅在 native catch（本人亲读差异）、`mainline-consumer-first-ack-loss.spec.ts` 原强断言保留（本人亲读差异）。**子代理关于「43 拒绝」计数与其余「覆盖强度」概括的推算部分不采**。**unit 覆盖勘察子代理在本轮超时未产出有效结论，已终止，其结论未被本报告采用**；unit 侧全部结论均来自**本人亲读**（见上表与差异要点）。

**因此，§3.6 第 2 项（「未读全文的新增/修改测试文件」）在本节闭合**，其状态更新为：**已补读**。**但完整 scope 仍不成立**，剩余未闭合项如下（不因披露未读而自动变完成）：

| 未闭合项 | 性质 | 处置 |
|---|---|---|
| `tests/e2e/t02-fr200-fr201.spec.ts` 2174 行全文 | 本人未逐行读（子代理逐行读＋本人复核关键断言） | 已在 §2/§4 涉及的断言处标明具体行号；**该文件的其余段落未由本人逐字复核**，本报告不就此文件整体作「已全读」声明 |
| `tests/e2e/native-driver.ts` / `mainline-consumer-first-ack-loss.spec.ts` / `csp-lifecycle.spec.ts` 的**未被改动的上下文** | 只读差异，未逐行读改外上下文 | 三文件的改动均为局部（catch／轮询替换／harness 计时），改外上下文不影响本报告结论；**不冒全读** |
| `tests/unit/` 8 个修改文件的**改外上下文** | 只读差异 | 同上；**不冒全读** |
| `packages/engine/vendor/rdflib/*`（二进制与许可） | 按来源 hash 与 PROVENANCE 核 | 承上文 §3.2 |
| `packages/contracts/src/v2.ts`／`index.ts`／`python/contract_v2.py`／`v2/schema.json` | 上文 §3.1 已列本轮新增段 | 本轮无新增读 |
| Windows／Linux／打包／生产／签名公证／跨平台 | 无本方样本 | 承上文 §3.6 第 3 项 |
| R08/R09 原稿全文 | 未逐字重读 | 承上文 §3.6 第 4 项 |

**F01 状态更新**：上文 §5.8 的 `R11-F01`「完整 scope 已覆盖」**由「成立」下调为「部分闭合」** —— 覆盖**已从实现层扩展到全部新增测试与 fixture 正文**，但**上文 §3.6 所列的 e2e 全文件逐行、修改文件改外上下文、vendor 二进制、跨平台与生产验证仍未闭合**。**不新增修复门禁，不改码**；后续若 owner 授权，可按上表逐项闭合。

### 10.2 #57／#146／#147 的有效分类与具体边界（订正 §4 表三行与 §4.1 三行）

**口径（本人本轮确认）**：**代码机制面**可由仓库判定；**组织/法律事实**（谁拥有资产、是否有删除请求通道的法律义务、团队实际人数与可替代性）**不能由仓库判定**。凡本方无一手证据者，**保留 UNKNOWN**；**不新增组织访谈、权限申请或验收项**；**原 HOLD 保持**。

| # | 清单项 | **本轮有效分类** | 代码机制面（仓库可判定，本人实测） | 组织/法律事实（本方无一手证据） | 原 HOLD |
|---|---|---|---|---|---|
| **57** | GDPR deletion requests that reach every table, backup and log | **无法确认**（由上文「部分适用」**回退**；理由见下） | 数据生命周期分层与「历史不可改写、缓存回收不得触及历史」规则**在位**（`storage.py` 分层与 `invalidation-v2.json`）；`storage.py:1839 def backup()` 存在；**无用户账号/登录/租户实体**（`grep -rniE "user_account\|account_id\|login\|signin\|tenant\|organization"` 于 `packages/contracts/src/v2.ts`、`apps/desktop/src/main/desktop-ipc.ts` **0 命中**）；**无删除请求/GDPR/保留策略通道**（`grep -rniE "gdpr\|erasure\|delete_request\|data_subject\|retention_policy"` 于 `packages/engine/src`、`packages/contracts/src`、`apps/desktop/src` **0 命中**） | ①是否存在需要履行的删除请求法律义务；②是否存在任何可被删除请求命中的用户数据表；③历史层不可改写设计与删除权要求的法律关系 | **保留**（发布/法律 HOLD 原样） |
| **146** | every account, domain and repo in the company's name, not the name of whoever built the prototype | **部分适用**（维持上文分类，但**依据换为可判定事实**） | 仓库 remote 为 `https://github.com/NOmoreJoke/OntoLearn-Studio.git`（本人 `git remote -v` 实测）→ **当前确为个人账号名下的仓库，非组织名**；产品内**无账号/域名/租户实体**（同上 0 命中） | ①法律资产归属（著作权/合同主体）；②公司名下的域名/账号是否已存在并可核；③资产转移文件 | **保留**（发布/法律 HOLD 原样） |
| **147** | a bus factor higher than one | **无法确认**（由上文「部分适用」**回退**；理由见下） | 文档与 owner 归口清晰、ADR 完整、**每条开发线只有一名负责 agent**（`AGENTS.md` §5 并行开发与文件责任约定）；**本候选内 `docs/reviews/T02/` 已有 57 个差异路径**（归档密度高） | ①团队实际人数与可替代性；②是否存在第二人**实际复现**记录（归档密度**不等于**复现能力）；③历史/失败/取消轮次由谁接手 | **保留** |

**回退理由（明确、不改判以求通过）**：
- **#57**：上文原写「有数据生命周期分层与不可改写规则在位 → 部分适用」。但清单项问的是**「删除请求是否到达每张表、备份与日志」**，而本方实测**不存在删除请求这一机制面**（0 命中），**也不存在被删除请求命中的用户数据表**（无账号/登录/租户实体）。机制面既不成立，**代码本身只能证明「不适用该机制」，不能证明组织/法律面已知**。故**正确档位是「无法确认」** —— 该清单项整体（含其法律面）在本产品当前形态下无法由仓库判定。
- **#147**：同上文的「巴士系数可由 owner 归口与归档密度**部分判定**」——**归档密度与 owner 归口只反映文档组织，不构成第二人可复现的证据**。可判定的是「每线一名负责 agent」这一**流程事实**；「巴士系数是否大于 1」是**组织事实**，无一手证据，**保留 UNKNOWN**。
- **#146 维持「部分适用」**：与前两项不同，此项**存在可由仓库直接判定的事实**（remote 属个人账号、产品内无账号/域名/租户实体）——该事实同时**直接回答了清单项的问题**（当前**未**使用公司名下的账号/域名/仓库），故不属 UNKNOWN；而法律资产归属部分仍 UNKNOWN，故不判「适用（正面）」。**其原 HOLD（发布/法律）不变**，部分适用**不等于**资产归属问题已解决。
- **三者均不新增组织访谈、权限申请或验收项**，HOLD 全部原样保留。

### 10.3 有效 160 分布、实际变化清单与末 13（订正 §4.1 的「10 项差异」）

**订正**：上文 §4.1 表格列出 10 行并称「程序化逐行对比得 **10 项差异**」。**该表述错误**：其中 6 行是**同档维持**（#19／#20／#32／#33／#26／#41），并非标签变化。**本轮以 O070 `minimax-effective-opinion-map-03.json` 的 `checklist.items.authorLabel` 为基线程序化逐行重算，实测真实标签变化恰为 4 项**。

**本人本轮机器复核（`python3` 实跑）**：

| 项 | 实测值 |
|---|---|
| O070 `checklist.items` 项数 | 160（`authorLabel` 分布：不适用 90／部分适用 46／适用（正面）16／无法确认 8） |
| 本报告 §4 表行数／唯一 ID | 160／160（min 1、max 160、无缺号、无重复） |
| **逐行真实标签差异** | **恰 4 项**：#57 无法确认→部分适用、#108 不适用→部分适用、#146 无法确认→部分适用、#147 无法确认→部分适用 |
| 其余 6 行（#19/#20/#32/#33/#26/#41） | **同档维持**（不构成标签变化）；其中 #26、#41 系**由「适用（正面）」下调为「部分适用」**——该下调发生在更早轮次并已计入 O070 基线，故相对本基线为维持 |

**有效 160 分布（按本轮 §10.2 的分类）**：适用（正面） **16** ／部分适用 **49** ／不适用 **90** ／无法确认 **5** ／**合计 160**。

> **与上文 §4.1 数字的关系**：上文 §4.1 记为 **16／50／89／5**。本轮**唯一实质变化**是 §10.2 将 **#57 与 #147 由「部分适用」回退为「无法确认」**（#146 维持「部分适用」，#108 维持「部分适用」），故 部分适用 50→**49**、不适用 89→**90**、无法确认 5→**5**、适用（正面） 16→**16**。**16+49+90+5 = 160**。
>
> **此为按本轮新证据的订正，不是为通过而改判**：#57 与 #147 的回退理由见 §10.2，其**原 HOLD 均保留**，**不关闭任何 HOLD**，**不新增门禁**。适用性分类**仍不是产品通过数**。

**末 13（#148–#160，与「额外 13」R06 MM01–13 是不同集合）**：本轮机器复核逐项标签为 **无法确认 4（#148–#151）／不适用 4（#152、#154、#157、#159）／部分适用 5（#153、#155、#156、#158、#160）** → 分布 **4／4／5**，**与 R10 及上文 §4.1 一致，维持不变**。本轮对这 13 行逐条按当前源码复核，**无一项需要再改档**；**#153、#156 不因此关闭任何 HOLD、不新增门禁**。**「额外 13」（R06 MM01–13，状态词为仍开/已闭合/部分闭合）仍单列于 §5.4，不并入权威 78，亦不与本组混同**。

### 10.4 R11-S01／T06 按实际前进不变量重核（订正 §2 R11-T06 的「需 8 页」推算）

**订正**：上文 §2 R11-T06 写「引擎分段固定 32768B/段，故 16MiB 文档最多 512 段；renderer 每页取 64 段 → **需 8 页即取完**，512 页上限远大于实际所需」。**该推算以「每页实收 64 段」为前提，与引擎实际行为不符**（引擎按字节预算贪心收段，`pageSize` 只是上限）。**按实际前进不变量重核如下。**

**实际前进不变量（本人亲读 `packages/engine/src/ontolearn_engine/job_store.py:932-981`）**：
- L943–944：`start >= manifest["segmentCount"]` → **拒绝**（`INVALID_REQUEST`），不会越界或死循环；
- L946：`for ordinal in range(start, min(start + params["pageSize"], segmentCount))` —— 取段上界为 `min(start+pageSize, segmentCount)`；
- L959–964：候选结果 `canonical(result).encode() + 1024 > min(maxPageBytes, maxFrameBytes, 262144)` 时，**若 `chosen` 为空 → `RESOURCE_LIMIT`（整页拒绝）**；否则 `break`（本页已收段，返回）；
- L965–966：`chosen.append(segment)`；`end = start + len(chosen)`；
- L975–976：`nextOrdinal = None if end == segmentCount else end`；`complete = (end == segmentCount)`。
- **因此：每个成功返回的页至少前进 1 段（`len(chosen) ≥ 1`），且 `nextOrdinal > start` 恒成立**（`end = start + len(chosen) ≥ start+1`）。**不存在「零前进」页，不存在无限循环**；总页数上界 = `ceil(totalBytes/32768) ≤ 512`。

**常量核（本人 `grep` 实测）**：`domain_changesets.py:30 MAX_DOCUMENT = 16 * 1024 * 1024`；`:31 SEGMENT_BYTES = 32768`；`:173` 分段切片；`:188 segmentCount = len(segments)` → **总段数 ≤ 512**。

**客户端一侧（本人亲读 `apps/desktop/src/renderer/src/ontology/mainline-ownership.ts`）**：L21 `for (let count = 0; count < 512; count++)`；L29/:31 `pageSize: 64`；L73 `if (page.nextOrdinal === null || page.nextOrdinal <= startOrdinal) return invalid()`；L76–77 循环耗尽后 `return invalid()`（**fail-closed**，不静默截断）。契约侧 `reassembleOwnershipDetail` 校验每页段数 ≤64。

**结论**：
1. **最坏页数**：段数 ≤512，且每页至少 1 段 → **最坏 512 页**，**不是 8 页**（上文该推算已订正）。
2. **是否构成构造性缺陷**：**否**。理由：(a) 引擎侧「零前进」不可发生，`nextOrdinal` 单调严格递增，终止性成立；(b) 客户端 512 次循环与「总段数 ≤512」**同量级对齐**——即使最坏情形（每页仅 1 段、文档接近 16MiB），所需页数 512 **恰好落在**客户端 512 次上限内，而该上限耗尽时走 `return invalid()` **fail-closed**，不会返回被截断的文档；下游 `OwnershipConflictDetailView` 与 `reassembleOwnershipDetail` 还有分段 sha256/offset/长度逐段复核作为第二道闸。
3. **性质**：**常量维护边界**（`SEGMENT_BYTES`／`MAX_DOCUMENT`／客户端 512／`pageSize 64` 四者需保持一致），**不是构造性缺陷**。**本轮不改码、不新增修复门禁**；若 owner 未来改动上述任一常量，按原 T02 契约归口复核四者一致性即可（与上文 R11-T06 的最小建议一致，**仅订正其页数推算**）。
4. **push 前源码阻断**：**否**（维持上文结论）。

### 10.5 R11-F02 限证加强（以更强原件限定，保留首 prettier 事实）

上文 §3.5 的裁决**结论维持**（prettier 规范化未越出授权范围），但其证据基础原为「9 个 hunk 头逐字相同」。**本轮以 O074 已存在的原件加强限证**（**未复跑任何验证**）：

| 原件 | 本人亲读的关键字段 | 限证作用 |
|---|---|---|
| `outputs/20261027_t02_ci43_observation_repair_074/STATIC-PRESERVATION-02.json` | C1 `ordinaryExpectCalls` before/after **逐条同名同参**（含 `expect(native.events.some(...))` 等 39 条）；`namedBridgeCalls` before/after 均仅 `window.ontolearn.getEngineHealth()` 且 `exact: true` | 证明**原断言集合与参数未被改写**（C1 39→39、FR 133→133 由原件计数） |
| 同上 | FR `callbackBindings` 5 个 phase：`complete-diff`／`commit-outcome`／… 的 `originalNormalizedCallback.sha256` 与 `newNormalizedCallback.sha256` **逐个相等**；`options = {intervals:[100], timeout:5000}`、`comparator = toBe(true)` 不变 | 证明**5 处 `expect.poll` 的 callback/options/comparator 逐字未变** |
| `…/FR-INDEPENDENT-BOUNDARY-REVIEW.json` | `verdict = PASS_FR_STATIC_AND_EXTRACTED_HELPER_BOUNDARIES`；`preservation.reverseOnlyAddedHelpersFiveWrappersThreeSealsRestoresWholeOriginalSemanticAST = true`；`fiveOriginalCallbackASTsAndOptionsExact = true`；`originalComparatorTrueUnchanged = true`；`sealFirstInThreeOriginalFinallyBlocks = true`；`noBusinessMethodCallOrAssertionOrControlBodyChanged = true`；`counts22Transactions43RejectionsAndTimeoutsByOriginalASTPreservation = true`；`phaseFields19 = true`；`boundaryTests` 13 项 `passed: true`；`blocking: []` | **FR 逆变换 AST 精确**：新增仅为包装/封槽/还原，原业务语义 AST 整体恢复；22 事务／43 拒绝／timeout 与 19 个 phase 字段由原 AST 保全而非重新声明 |
| `…/C1-INDEPENDENT-BOUNDARY-REVIEW.json` | `verdict = PASS_STATIC_AND_PURE_MOCK_BOUNDARY_ONLY`；`actualCatchExtraction = {firstLine:280, lastLine:341, catchSHA256: e94ca799…}` 且 `handwrittenCatchCopy = false`；`preservation.sourceOutsideNativeCatchByteExact / nativeTryByteExact / actualOuterFinallyByteExact / successTailByteExact` 均 true；`failureReadFileCallCount = 1`；`boundaryRun.scenarioCount = 14, allPassed = true`；`driverHelperUnchanged` 两条均 `equalsParent2d6 = true` | **真实提取边界独核**：catch 由 AST 抽取后 transpile 入 VM 执行（非手写副本），原 try/finally 与成功尾段逐字节不变；driver/helper 相对 2d6 未改 |

**保留的首事实**：`074/source-format-result.json` 的 argv 确为 `prettier --write`；`source-format.stdout` 记 `t02-fr200-fr201.spec.ts 92ms`（**无 `(unchanged)`**），C1 文件为 `(unchanged)` → **FR 文件确被 prettier 改写**（此事实保留，不因结论成立而抹去）。

**累计差异与 exact2 的分清（本人本轮实测）**：
- `tests/e2e/csp-lifecycle.spec.ts`：**base→head 差异与 2d6→d1aca 差异的 SHA256 完全相同**（均 `dba6b1e4…`）→ 该文件自 base 起的全部改动**就是**本轮 O074 的 C1 改动。
- `tests/e2e/t02-fr200-fr201.spec.ts`：**base→head 为 +2174/-0、1 个 hunk**（该文件在 base 时不存在，全文为新增）；**2d6→d1aca 为 +360/-128、8 个 hunk**（`@@ -79,6 +79,235 @@`、`@@ -168,27 +397,27 @@`、`@@ -223,61 +452,61 @@`、`@@ -783,6 +1012,7 @@`、`@@ -880,29 +1110,29 @@`、`@@ -925,41 +1155,41 @@`、`@@ -1751,6 +1981,7 @@`、`@@ -1909,6 +2140,7 @@`）；base→2d6 之间该文件已有 **+1942 行**新增。
- **因此**：上文 §3.5 的「9 个 hunk 逐字相同」只覆盖 **2d6→d1aca 的 exact2 段**，**不等于** base→head 累计差异的静态保全证明；base→head 累计段的保全由 O074 的 `STATIC-PRESERVATION-02.json` 与两份独立边界评审**逐项**覆盖。**两段口径必须分开陈述**，本节据实分清。

**结论维持**：**R11-F02 不构成需 owner 决策的实质源码问题**，记为已核事实；**push 前源码阻断：否**。

### 10.6 本轮对既有意见与限证的处置（不重开已闭项、不改判以求通过）

- **R10 稳定 ID、历史主题、原 owner/事件窗口**：全部**原样保留**（§5 逐表）；本轮**未新增、未合并、未替换**任何历史 stableID，**未以 Top 序号代稳定 ID**。上文 §5.5 与 §5.4 的两个「13」集合继续分开处置。
- **R10「当轮无 Python 变化」语境**：保留为**历史语境**（属 R10 当轮的上下文事实）；本轮 base→head 累计候选**确有**大量 Python 侧新增（engine 7 测试路径 ＋ 引擎实现差异），**本轮结论全部以当前源码为准**，不沿用该语境。
- **R10-T12（「仅 3/9 有断言」）**：**仍不采**，理由不变（`packages/engine/tests/test_storage.py:190-223` 动态参数化覆盖全部 9 条规则的正反断言）；**不加 5 测试门禁**。
- **R10-T09（「无机器校验」）：**仍不采**（`tests/unit/t02-manual-fact-id.test.ts:53-76` 真实 `Store._fact`＋`digest` 交叉核验；本轮另**亲读该 golden fixture 全文 139 行**，确认 13 个 case 的 canonical 与 `fact.id` 双列，且文件自述来源为真实隔离 Python 引擎）。
- **R10-10（序号笔误）**：维持为「实际 Top 9」；本轮无新证据改变该限证。
- **子代理结论的采信边界**：本轮 e2e 子代理关于「约 42 次 `rejectCallerObject`」的计数**不采**（本人 `grep -c` 实测 **16**）；其「分页／HOLD／结算／预算在 e2e 零覆盖」的结论**采信**（本人以 `grep` 0 命中独立复核）。**unit 子代理超时未产出，未被采用**。
- **HOLD 逐一关闭数**：**仍为 0**。本轮新增的 §10.1–§10.5 全部为**覆盖补齐与统计订正**，**未关闭任何独立 HOLD**（#57/#146/#147 的 HOLD 明文保留），**未新增任何修复门禁、验收项、功能或执行权限**。
- **CI 与远端**：CI43 总体 failure、Windows C1 异步根因 UNKNOWN、FR201 累计超时根因 UNPROVEN、本机 C1 成功未触发真实失败附件、整体 2/17、**本候选未 push／无新 CI／未 merge／未动 PR16** —— 原样保留。**本轮未授权任何远端操作**。

### 10.7 本方当前结论（自然终态）

**结论：ConditionalPass（附条件通过），限定为推送前技术审查阶段**，针对 base `583c05c7` → head `d1aca3e3` 的完整累计候选 —— **与上文 §9 同一结论，无上调、无下调**。

**本轮相对上文 §9 的实质增量（四项，均为覆盖与事实订正，不改变结论方向）**：
1. **必要覆盖闭合**：引擎 7 路径新增/修改测试、unit 4 个新增文件全文、unit 8 个修改文件完整差异、e2e 3 个修改文件完整差异、fixture 全文、契约增量 4 路径、e2e 新增 spec 2174 行的关键断言——**本人已逐项补读并给出行号级断言要点**；上文 §3.6 第 2 项的「未读全文」状态**已闭合**，**F01 由「成立」下调为「部分闭合」**（e2e 全文件逐行、改外上下文、vendor 二进制、跨平台/生产仍未闭合，已列明）。
2. **统计订正**：真实标签变化**恰 4 项**（非 10 项）；有效 160 分布 **16／49／90／5**（#57、#147 依新证据回退为「无法确认」，#146、#108 维持「部分适用」）；**末 13 维持 4／4／5**。
3. **R11-S01/T06 订正**：**8 页 → 最坏 512 页**；按引擎实际前进不变量（每页至少前进 1 段、`nextOrdinal` 严格递增、`start >= segmentCount` 即拒绝）**不构成构造性缺陷**，性质为**常量维护边界**；**不改码、不新增门禁**。
4. **R11-F02 限证加强**：改以 O074 `STATIC-PRESERVATION-02.json` 与两份独立边界评审的逐项字段限证（原断言 39→39／133→133、5 处 callback/options/comparator 逐字相等、FR 逆变换 AST 精确、C1 真实提取 catch 逐字节边界），**并分清 base→head 累计段与 2d6→d1aca exact2 段**；**保留首 prettier 事实**；结论维持。

**仍不成立的部分（承上文，不因本轮补读而改变）**：这不是无条件整候选 Pass，不是完整 CI 通过，不是产品放行。CI43 总体 failure；本候选无新 CI；Windows C1 异步根因 UNKNOWN、FR201 累计超时根因 UNPROVEN；全部独立 HOLD 与 UNKNOWN 原样保留、**逐一关闭数 0**；整体合并可用仍 **2/17**；Goal／M0／发布未完成。

**责任与授权**：本方只读，未改任何源码/测试/config/依赖/预算/验收，未 push/CI/merge，未重置/采购/升级，未读取另一作者本轮产物。发现实质源码问题给精确证据与最小建议，由 owner 决策；本报告不自行修源、不追加功能或验收、不授予执行权限。

**本轮追加节自述**：§10.1–§10.7 为本轮新增内容，**上文 §0–§9 全部原字节未改**；本节不嵌本方最终 bytes/hash（由 owner 保存实测）。**D8 未使用。**


---

## 11. 第二轮追加（同一 R11 会话；原 §0–§10 全部原字节保留，本节为**唯一有效替代／新证据**）

> **追加性质**：owner 在同一 R11 会话内追加，**不修改 §0–§10 的任何原字节**（追加前实测：`report.md` = 144335B／SHA256 `81d1446daab776ba8a580aa18a6f4d20cef106e06309d8d614ec75b1eba0b88c`）。本节与上文冲突处**以本节为准**；不冲突处上文继续有效。冻结身份不变：cwd `…/.worktrees/T02-s1-review-fixes`、branch `feature/weekly-t02-fr200-fr201`、base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`、head `d1aca3e34ec4d00095c10a14a413efb552d3776a`、tree `389848f84fe60325bcdcd1b7827a7ee6e039a0e1`、sole parent `2d6bc23fdc4f13afcceb7b79c8059ee3c74abbe8`、43 提交／125 差异路径／1403 tracked 源叶。
>
> **本轮范围（严格限定）**：仅闭两处必要缺口 ——（a）本人实际读 `tests/e2e/t02-fr200-fr201.spec.ts` 当前 2174 行至 EOF；（b）补读 O074 必要有效正文。**未重读**已完成的 6A engine／8M unit 等既有亲读内容；**未运行** check/vitest/pytest/build/package/formatter/HMR/GUI/SQL/bridge；**未改源、未复跑、未新开任务、未付费/重置、未新增门禁、未读取另一作者本轮产物**。本节所有执行数字均标明**既有原件身份**或**本人只读实测**。

### 11.1 FR e2e `tests/e2e/t02-fr200-fr201.spec.ts` —— 本人实际读至 EOF（2174 行）

**本人亲读确认**：本人本轮按 `read` 工具**逐段读完该文件当前全部 2174 行**（L1–340、L341–700、L701–1100、L1101–1500、L1501–1900、L1901–2174），**读到 EOF**（末行 L2174 为 `loadFact` 的最后一个 `toHaveValue` 断言）。上文 §10.1「本人未逐行读全文」的限制**在本节闭合**；§10.1 关于该文件的所有行号引用经本轮全文阅读**逐条复核成立**，无一处需更正。

**结构与断言依据（本人据全文给出）**：

| 区段（行号） | 内容 | 关键断言 |
|---|---|---|
| L1–5 | 文件头自述 | 「Actual UI definitions, not execution evidence. No production mapper imports, bridge writes, seeded database, authority replacement, or restart instrumentation」——**明确自限为 UI 证据，非引擎执行证据** |
| L6–19 | 依赖 | `@playwright/test`、`launchIsolatedDesktop`、`observeUI`/`committedReceiptOperation`/`exactlyOne`/`normalizeUIText`/`updateObservationSlot` |
| L20–62 | 常量与类型 | `RDF/RDFS/OWL/XSD`、`UUID` 正则、`hash = /^[0-9a-f]{64}$/`；`Entity` 类型注释 L43 明示「Independently authored N3 expected values, never generated by a production adapter」 |
| L64–121 | **计时包装数据结构** | `BoundedPollText`（`text` 截断 4096＋`originalUTF16Units`＋`truncated`）、`CommitPollObservation`；`lastCommitPoll`/`lastReadIdentity` 为 **WeakMap**；`pollPhases` **固定 5 个**（`complete-diff`／`commit-outcome`／`committed-receipt`／`manual-preview`／`controlled-rejection`）；`PollPhaseTiming` **固定 19 个数值字段**（本人逐字段核对：polls/settled/failed/active/attempts/callbacksSettled/callbacksThrown/callbacksActive/pollMs/pollMaxMs/callbackMs/callbackMaxMs/gaps/gapMs/gapMaxMs/lastPollStartMs/lastPollEndMs/lastCallbackStartMs/lastCallbackEndMs）；`pollTimingLimitBytes = 4096` |
| L123–177 | `pollClock`/`publishPollTiming` | 计时失败**不阻断原 matcher**（L127–129 注释）；发布内容**固定五 phase、固定数值字段、不序列化 Read/DOM 大对象**（L137）；超 4096B 时降级为 `{schema, unavailable, requiredBytes, limitBytes}`（L166–171）；`finally` 中 `seal` 时置 `sealed=true`（L175） |
| L179–235 | `currentPollTiming`/`sealPollTiming` | 槽以 `test.info().annotations` 对象为 WeakMap key，**每 test 独立一槽**；`sealPollTiming` 为**同步**快照且 catch 吞掉失败（L232–234「Best-effort synchronous snapshot before the original async cleanup」） |
| L237–309 | **`observedPoll` 包装器** | **只包 5 处 `expect.poll`**；L243–244 明示「The page is intentionally not read; only the original callback observes it」；计时不可用时**退化为原 `expect.poll(callback, options)`**（L246–249、L252–255）；L262–294 仍以**原 `options`** 调用原 `expect.poll`；`finally` 中 L307 每次 publish、**settle 才 publish**；`gap` 仅在同一 poll 的相邻 callback 之间计（L269–274） |
| L311–339 | `recordObservation`/`ui`/`pollText` | 观测写入 `updateObservationSlot`（单一有界槽）；`pollText` 截断 4096 |
| L341–434 | `data`/`canonical`/`record`/`read`/`diff` | `canonical()`（L345–361）**复刻** sort_keys 紧凑 JSON；`record()`（L362–374）**复刻**产品 payload 结构；`read()` 走**真实** `window.ontolearn!.readProject`（L383）；`diff()` 断言「完整事务差异」region 可见、确认按钮 enabled、**Diff 行数与「全部 N 项…」文案同时成立**（L408–417），随后 `JSON.parse` 取真实 Diff |
| L436–578 | **`commit()` 全事务链** | ① Diff 与期望**全等**（L443）；② 提交前读回 `domain` 与 `inputSnapshotId` **均未变**（L445–446）；③ 回执含「提交版本 N。」（L478）或 pending `succeeded` → **走显式 reconcile**（L479–491）；④ `committedReceiptOperation` 取**原 operationId**（L506、L510）；⑤ 真实 `getOperation`→marker 七字段**全等**含 `planHash` 形状（L524–532）；⑥ 真实 `getJob`→`capability='changeset.commit'`/`state='succeeded'`/`error:null`（L533–540）；⑦ `job.input` 全等（`scope:'asserted'`、`definitionId:'changeset'`、`derivedResultIds:[]`）（L541–548）；⑧ `confirmationRef` 非空（L549–550）；⑨ `commitProgress.mode='atomic'` 且内嵌 marker 与 L524 一致（L551–560）；⑩ **operationId 不重复**（L561–563）；⑪ `mappingState` 不变（L564）；⑫ **墓碑断言自限**：L565–570 明示「this assertion must not be reported as nonempty managed-tombstone coverage」；⑬ 刷新后读回一致（L572–576） |
| L580–628 | `fields`/`select` | 多语言标签/定义/同义词/示例逐组填入；`getByLabel` 名称匹配**与当前值无关**（L610–611 注释）；`select` 经「对象浏览」表格按 IRI 查找并断言 `code` 文本为该 IRI |
| L629–735 | `create`/`homeOf`/`edit`/`removeEntity` | 创建后 Diff id 形状 `t02-<UUID>`（L646–650）；**结构/域/值域不生成实例事实**（L664–665）；编辑时 IRI **disabled**（L688）；删除前显示「当前未发现已登记的引用。」（L717） |
| L737–902 | 夹具 | 四 kind 矩阵（class rdfs/owl、objectProperty、dataProperty、individual）含 parents/domain/range/types 的初始与变更结构；`common` 含中英双语标签/定义、**带前后空格的同义词/示例**（L760–761）；`launchOptions()` 优先用 `ONTOLEARN_PACKAGED_EXECUTABLE`，否则 `args:[resolve('apps/desktop')]`；`start()` 断言初始 `projectRevision===0` 且 `domain.state` 全空（L899–900） |
| L904–1026 | **FR200 四例** | 每例 `test.setTimeout(180000)`（L907）；create classA/classB → create 原对象 → edit → **复制**（复制后 IRI 与标识符**清空** L978–979）→ 删除 changed → 删除 copy；**删除后先删对象仍保留 copy**（L1004）；**前置 classA/classB 定义逐条未被改动**（L1007–1013）；`finally` 先 `sealPollTiming()` 再 attach `fr200-form-matrix` 再 `application.close()`（L1014–1024） |
| L1028–1994 | **FR201 主例** | 见下段 |
| L1996–2153 | **数字子标签 cohort 例** | 独立夹具（L1998–1999 明示「This fixture separates lexical controls from cumulative history capacity. It does not close the preserved revision-24 committed-but-unreadable failure」）；`@en-001`／`@de-ch-1901` 两个合法控制项，各做新增＋原 ID 编辑；每步以 `expectReadAndIdentity` 同时核 `readProject` 与 `getActiveProject` 的 projectId/projectRevision/inputSnapshotId（L2053–2059）；attach 名含 `fixtureIsolationIsNotCapacityRepair: true`（L2146） |
| L2156–2174 | `loadFact` | 按事实 ID 在「实例事实」表中定位**唯一一行**（`toHaveCount(1)`）、载入后断言「原记录 ID：」与 `fact.id` 全等、主体/属性 IRI **disabled**、对象值为原值 |

**FR201 主例（L1028–1994）本人核到的事实**：
- **11 条三元组**逐条录入（L1323–1348），含 `@zh`、`xsd:integer`／`boolean`／`decimal`／`double`／`date`／`dateTime` 与**纯字符串**（L1333 注释引 ADR-0002/Q6「plain is the canonical no-language xsd:string term」）。
- **显式 `"typed string"^^xsd:string` 被拒且不规范化**（L1361–1408）：拒绝前先确认「无 alert」、填入 alias 后断言 `toHaveValue(alias)`（L1380「No silent normalization」）、**完整 Diff region 与确认按钮均 count 为 0**（L1389–1390）、**拒绝后读回与拒绝前完全相等**（L1391–1392），并 attach `fr201-rejected-explicit-string-alias`。
- **`rejectCallerObject`（L1074–1220）**：每次拒绝前先「读取当前项目」清错并轮询到按钮 enabled 且无 alert（L1112–1135）；断言**输入被保留**（L1139–1142、L1184–1186）、**错误文案逐字相等**（L1182，`normalizeUIText` 两侧归一）、**Diff 与确认按钮均不存在**（L1187–1188）、**拒绝后读回与拒绝前完全相等**（L1194）、`getActiveProject` 三元身份不变（L1197–1199）、并 attach 含 `action/targetField/entered/expectedCode/errorText/uiObservedAt/before/after/active/completeDiffCount/confirmationCount` 的证据（L1200–1219）。
- **删除影响**：被引用属性删除被阻断并显示「未能生成预览」且 Diff count 为 0、domain 与 inputSnapshotId 均未变（L1487–1499）；删除影响列表**逐条文本全等**（L1487–1491）。
- **原 ID 编辑链**：编辑保留原记录 ID（L1517/L1519/L1523 等每步 `originalId` 断言 `toHaveText(original.id)`），编辑后 `facts` 以**原 ID 映射替换**（L1551–1557）。
- **保留身份冲突 → GUI 可见详情**（L1583–1655）：`OWNERSHIP_CONFLICT` 后「首个阻断冲突定位」region 可见、`dl > dd` 精确为 `[revision,'保留身份冲突']`、定位列表 2 项、heading `['现有记录','传入记录']`、每项 5 个 dd 字段（id／owner=null 文案／sourceRow=null 文案／subject／predicate）（L1598–1619）；**冲突前后读回完全相等**（L1620–1621）；attach `fr201-reserved-identity-visible-detail`（含 `actualGuiBranch: 'reservedIdentity manual only; other reasons are not GUI claims'`、L1625）、原始 HTML 页与整页截图（L1648–1655）。**后续对其他记录删除时详情与 Diff/确认按钮均 count 为 0**（L1662–1668、L1675–1685）。
- **失败 catch（L1704–1982）**：只读诊断、**不替代原失败**（L1982 `throw originalError`）；诊断预算 **≤2000ms** 且受 `observedCaseStart + 179000` 约束（L1721–1722）、单次观测 ≤500ms（L1740）、附件 ≤262144B、最多 2 个、总 ≤524288B（L1781–1783）；**先保存原 DOM 再做任何 bridge 查询**（L1875–1901，`bridgeQueriesSkippedReason` 明示「Original DOM capture and its attachment must both complete before bridge queries」）；仅在 DOM 捕获与原页面附件**均成功**后才允许只读 `getOperation`/`getJob`/`getActiveProject`/`readProject`（L1902–1957）；**DOM 文本按 UTF-8 边界裁剪**（L1796–1805）、面板文本 ≤16384B（L1826）、按钮列表 ≤32 且 `buttonsTruncated` 标记（L1848–1850）。
- **`finally`（L1983–1993）**：`sealPollTiming()` → attach `fr201-original-records-and-literals` → `application.close()`，原 finally 三步顺序保留。

**「57 事务」与「43 拒绝」的口径（本人据源码结构核算，非 grep 静态调用点）**：

- **事务**：FR200 四例各 **7** 次（create classA／classB／原对象／edit／copy／delete×2 = 7）× 4 = **28**；FR201 主例 **22**（11 次新增 ＋ 3 次编辑 ＋ 2 次删除 ＋ 6 次定义创建 = 22）；数字子标签 cohort **7**（classA／subject／property 3 次创建 ＋ 2 次新增 ＋ 2 次编辑 = 7）→ **28+22+7 = 57**。与 O074 `NATIVE24-QUALIFICATION-02.json` 的 `transactionGroups`（6 组：case12/13/14/15 各 7、case16 = 22、case17 = 7）**逐项吻合**。
- **拒绝**：本人按源码的**参数化展开**核算（非静态调用点计数）：add 阶段 25（1 unparseable-new ＋ 2 datatype ＋ 5 quote/datatype ＋ 3 language ＋ 1 overlong-integer ＋ 4 authority ＋ 4×2 field-isolation ＋ 1 explicit-string-alias）；edit 阶段 18（5＋3＋1＋4 ＋ noncanonical-edit ＋ unparseable-edit ＋ 2 datatype ＋ 1 reserved-original-id）→ **合计 43**，其中 `reserved-original-id` 期望 **`OWNERSHIP_CONFLICT`**，其余 **42 期望 `INVALID_REQUEST`**。**该结果与 O074 同次实际运行产物完全一致**（见 §11.2）。
- **本人对 §10.1 的更正**：§10.1 曾记「`rejectCallerObject` 调用点为 16 处」并据此怀疑「43 拒绝」口径 —— **该表述错误**：16 是**静态调用点**数（含 helper 定义与循环），**动态展开后为 43**，与 O074 同次运行的 43 个 `fr201-rejected-*` 附件一一对应。**「43 拒绝」是 O074 同次完整 24 资格内的当次计数，不是跨轮累计**；本方**不采**先前「跨轮历史累计口径」的表述。

### 11.2 O074 必要有效正文补读（本人亲读层级与关键正文）

**读回位置与层级**（本人本轮实际读取）：

| 原件 | 本人读取层级 | 关键正文（本人实测/摘录） |
|---|---|---|
| `native24/report.json` | **全文结构＋逐附件解码** | `stats = {expected:21, skipped:3, unexpected:0, flaky:0}`；`fr201-rejected` 出现 **43** 次且为 **43 个唯一附件名**（`fr201-rejected-new-*` 25 个、`-edit-*` 17 个、`-noncanonical-edit`／`-unparseable-edit`／`-unparseable-new-object`／`-explicit-string-alias`／`-reserved-original-id` 各 1）；**逐个 base64 解码 body 后实测**：`expectedCode` 分布 = **INVALID_REQUEST 41 ＋ OWNERSHIP_CONFLICT 1**，另有 1 个 `fr201-rejected-explicit-string-alias` **无 `expectedCode` 字段但其 `errorText` 为「操作未能完成：INVALID_REQUEST…」** → **实际 42 INVALID_REQUEST ＋ 1 OWNERSHIP_CONFLICT**；`action` 分布 = add 25／edit 17；`OWNERSHIP_CONFLICT` 那条即 `fr201-rejected-reserved-original-id`，其 `errorText` 为「操作未能完成：OWNERSHIP_CONFLICT。事实来源、保留身份或属性约束存在冲突。请核对原记录，修改输入后重新预览；已输入内容保留。」 |
| `NATIVE24-QUALIFICATION-02.json` | **本人读取顶层结构＋计数与终态字段** | `verdict = PASS_LOCAL_NATIVE24_BOUNDED`；`checks` 长度 **434**，`unresolvedChecks = []`；`resultCounts = {passed:21, skipped:3}`；`transactionGroups` 6 组 = case12/13/14/15 各 7、**case16 = 22**、case17 = 7 → **57**；`negativeCodeCounts = {INVALID_REQUEST:42, OWNERSHIP_CONFLICT:1}` → **43**；`sixT02CaseOrdinals = [12,13,14,15,16,17]`；`FR201Final = {factCount: 9, marker:{projectRevision:22, operationId:…, jobId:…, beforeSnapshotId:…, afterSnapshotId:…, planHash:…}}`；`originalSkippedCases` 为 3 个 I04 原 skip（Linux/隔离显示 fixture 依赖）；`attachmentPins` 101 条 |
| `BUILD-REBUILD-MAPPING.json` | **全文** | `passed: true`；9 项 checks 全 true（含 `fullCheckZero`、`allSourcesSameAsActualFullcheckInput`、`other1401OriginalSourcesModesExact`、`exact5BuildNames`、`main606471LengthSame`、`onlyExisting24BDevelopmentNonceFieldMayDiffer`、`other4BuildsExact`）；`changedMainByteCount = 24`、`changedMainOffsets` = `[602382…602405]`、`existingNonceFieldExclusiveRange = [602382,602406]`；`oldBuild` 与 `actualValidatedBuild` 中 **main/index.js 的 sha256 不同**（`c6a3deef…` vs `9373cb0f…`），**另 4 个构建逐字相同**；`sourceIdentity` 明示「Actual run at 2d6 HEAD + exact 2 source WIP; any later commit requires Git blob content mapping, no label-only rerun」 |
| `INDEPENDENT-COMMIT-BINDING.json` | **本人读取顶层结构＋核心绑定项＋limits**（487 项 checks 逐条为 true，本人不重算） | `bindingPassed = true`、`checkCount = 487`、`unresolvedChecks = []`；`actualCommit = {head: d1aca3e3…, tree: 389848f8…, soleParent: 2d6bc23f…, changedPaths: [csp-lifecycle.spec.ts, t02-fr200-fr201.spec.ts], stagedTree: 389848f8…, committedDiffBytes: 23293, committedDiffSHA256: eac8b898…, sourceCount: 1403}`；`committedSourceBlobBindings` 两条 **gitBlob 与 validatedWIPRecord 的 bytes/sha256 完全一致**（C1 `fea56451…`／16212B；FR `a5c9dd02…`／86972B）；`executionToCommitMapping` 明示 **`runtimeWasExecutedOnLaterCommit: false`**、`actualFullCheckAndNativeExecutionHEAD: 2d6bc23f…`、`actualExecutionSourceState: 2d6 plus exact two authorized test-source WIP files`、`nativeQualificationFile: NATIVE24-QUALIFICATION-02.json`、`nativeChecks: 434`、`qualificationRepeated: false`；`protectedStatus` 4 行保护脏项、`indexEmpty: true`、`WIP8Exact: true`；`limits` 第 5 条明示「Exact-byte mapping supports evidence for this later candidate; **it does not relabel original runtime execution HEAD**」 |
| `C1-INDEPENDENT-BOUNDARY-REVIEW.json` | **本人上一轮已读全文字段；本轮复核关键项** | `verdict = PASS_STATIC_AND_PURE_MOCK_BOUNDARY_ONLY`；`actualCatchExtraction = {firstLine:280, lastLine:341, catchSHA256: e94ca799…}`、`handwrittenCatchCopy = false`；`preservation.sourceOutsideNativeCatchByteExact / nativeTryByteExact / actualOuterFinallyByteExact / successTailByteExact` 均 true；`failureReadFileCallCount = 1`；`boundaryRun.scenarioCount = 14, allPassed = true`；`driverHelperUnchanged` 两条 `equalsParent2d6 = true` |
| `FR-INDEPENDENT-BOUNDARY-REVIEW.json` | **本人上一轮已读全文；本轮复核关键项** | `verdict = PASS_FR_STATIC_AND_EXTRACTED_HELPER_BOUNDARIES`；`preservation.fiveOriginalCallbackASTsAndOptionsExact = true`、`originalComparatorTrueUnchanged = true`、`reverseOnlyAddedHelpersFiveWrappersThreeSealsRestoresWholeOriginalSemanticAST = true`、`sealFirstInThreeOriginalFinallyBlocks = true`、`noBusinessMethodCallOrAssertionOrControlBodyChanged = true`、`counts22Transactions43RejectionsAndTimeoutsByOriginalASTPreservation = true`、`phaseFields19 = true`；`callbackBindings` 5 个 phase 的 `originalNormalizedCallback.sha256` 与 `newNormalizedCallback.sha256` **逐个相等**，`options = {intervals:[100], timeout:5000}`、`comparator = toBe(true)`；`boundaryTests` 13 项 `passed: true`、`blocking: []`、`boundaryScenarioCount = 12` |
| `COMPLETION.json` | **本人上一轮已读全文；本轮复核计数与 limits** | `base = 583c05c7…`、`commitsFromBase = 43`、`diffPathsFromBase = 125`、`trackedSources = 1403`、`changedPaths` 2 条、`stagedEqualsCommitted = true`；`fullCheck.exitCode = 0`、`elapsedSeconds = 209.26385…`、`headAtStart = 2d6bc23f…`；`fullCheckSummary = {typescriptPass:1912, pythonTotal:3769, pythonPass:3719, originalPythonSkip:50, ruffFiles:393, lintFormatTypeBuildRuff: PASS}`；`native24 = {exit:0, wholeSecondsIncludingCleanup:173.94133…, remainingKnown:0, engineNaturalCode: UNKNOWN}`；`native24Summary.transactions = [7,7,7,7,22,7]`（**57**）、`rejects = 43`、`FR201Revision = 22`、`FR201OriginalIDsEdited = 2`、`case7 = singleCommit1 execute0 replay0`、`timingCaseCopies = 12`、`timingPhaseNumericShape = [5,19]`、`timingCapacityBytes = 4096`、`timingActualMaxBytes = 2223`、`timingBoundaryWorstBytes = 3305`；`firstFailuresRetained` 明确 `NATIVE24-QUALIFICATION.json` 为**首失败脚本结果**、**有效资格仅 -02**；`limits` 逐条含 `C1ActualFailureCatchTriggered=false`、`C1RawFileFailureAttachmentProvenOnPlatform=false`、`C1MockIsProductProof=false`、`WindowsAsyncCause=UNKNOWN`、`WindowsFR201CumulativeTimeoutFixed=false`、`completeCI=not passed`、`newCandidatePushed=false`、`newCIStarted=false`、`PRModified=false`、`merge=false`、`overall=2/17`、`HOLDClosed=0` |
| `staged.diff` | **本人以 Git 实测等价比对**（不逐字读 23293B diff 正文） | `staged.diff` 与 `committed.diff` **同字节**（均 23293B、SHA256 `eac8b898…`）；`git diff 2d6bc23f d1aca3e3` 的 FR 8 个 hunk 头与该 diff 的对应 hunk 头逐字相同（见 §10.5）。**本方以 Git 只读实测替代逐字读 diff 正文**，并据 `INDEPENDENT-COMMIT-BINDING.json` 的 blob↔WIP 绑定与 `STATIC-PRESERVATION-02.json` 的逐项保全字段限证其内容保全 |

**本轮据以上原件的限证（严格分清三层）**：
1. **本机 Mac 同次 24 资格（21 PASS／3 原 I04 skip／0 unexpected／0 flaky）** 内，**57 事务与 43 拒绝（42 INVALID_REQUEST＋1 OWNERSHIP_CONFLICT）为当次实际计数**，与 FR201 终态 `projectRevision 22`、`factCount 9`、2 个原 ID 编辑同属**同一次执行**；`transactions = [7,7,7,7,22,7]` 与 `rejects = 43` 在 `NATIVE24-QUALIFICATION-02.json` 与 `COMPLETION.json` **两处独立一致**。
2. **执行发生在 2d6bc23f + exact 2 WIP 源状态**，**不是**在 d1aca3e3 上执行（`runtimeWasExecutedOnLaterCommit = false`）。d1aca3e3 与该执行态的绑定是**逐字节 Git blob 映射**（两文件的 gitBlob 与已验证 WIP 记录的 bytes/sha256 相同）＋其余 1401 源与 mode 精确不变＋当前 5 build 与 fullcheck/native 启动记录一致。**该映射支持「本候选的这两份测试文件内容即被验证过的内容」，但不改写「原运行时的 HEAD 是 2d6」这一事实。**
3. **本机 Mac 证据不等于 Windows 证据**：O074 `limits` 与 `INDEPENDENT-COMMIT-BINDING.json` 的 `limits` 均明示本机证据**不关闭** Windows CI43 C1/FR201 根因、**不构成**完整 CI 验收；`STATIC-PRESERVATION-02.json` 对 2d6→d1aca 的静态保全**不得外推**为「base→head 全部产品正确」——**base→head 段另有 42 个提交的引擎/契约/渲染端实现差异，其正确性由本方 §3.1/§10.1 的源码审读与既有原件承担，不由该静态保全件承担**。

### 11.3 统计订正（覆盖 §10.3 的分布数字；旧自然01 的 4 delta 保历史）

**订正 §10.3**：§10.3 在把 #57、#147 由「部分适用」回退为「无法确认」时，**分布数字算错**（误把两项同时记入「不适用」）。**按真实行逐项重算**：

| 项 | 值 |
|---|---|
| 原 §4 表基线（本报告 §4，逐行 160 条） | 适用（正面）16／部分适用 50／不适用 89／无法确认 5 |
| 本轮 §10.2 对 #57、#147 的回退（P→U） | 部分适用 −2（50→**48**）、无法确认 +2（5→**7**）、**不适用不变（89）** |
| **有效 160 分布（本轮唯一有效）** | **适用（正面）16／部分适用 48／不适用 89／无法确认 7／合计 160** |
| **相对 R10 基线（O070 `authorLabel` 90/46/16/8）的净改档** | **恰 2 项：#108 不适用→部分适用、#146 无法确认→部分适用** |

**与旧稿的关系（保历史，不改写）**：自然01（105413B 首稿）§4.1 曾记「10 项差异」——**该表述本身有误**（其中 6 行是同档维持），自然02（144335B）§10.3 已订正为「真实标签变化恰 4 项」，**该 4 delta 作为历史记录保留**；本节进一步订正的是**分布数字**（16/49/90/5 → **16/48/89/7**）与**净改档口径**（相对 R10 基线净改档 = #108、#146 两项，而非 4 项 —— 因 #57、#147 回退后与基线同档）。**两段均为「相对各自基线的正确算术」，不冲突**：O070→§4 表是 4 delta；§4 表→本轮有效表是 2 项回退；O070→本轮有效表是净 2 delta。

**#146 的口径（按 owner 限证补强）**：**个人 GitHub namespace 不证明公司法律归属**。故 #146 的「部分适用」**仅指代码/仓库机制面可判定**（remote 属个人账号仓库、产品内无账号/域名/租户实体 → 当前**未**使用公司名下账号/域名/仓库）；**组织与法律事实（法律资产归属、公司名下账号/域名是否存在并可核、资产转移文件）仍为 UNKNOWN**，其**原发布/法律 HOLD 保留**。**不据个人 namespace 推断法律归属已定**。

**#57、#147 的边界（维持 §10.2）**：#57 = **无法确认**（无删除请求机制面 0 命中、无可被命中的用户数据表；法律义务面 UNKNOWN）；#147 = **无法确认**（归档密度与 owner 归口**不构成**第二人可复现的证据；实际人数与可替代性 UNKNOWN）。**代码机制面可另列说明，但不因此把组织事实判为已知**。**三者均不新增组织访谈/权限要求，HOLD 原样保留**。

### 11.4 F01 主题归口订正（覆盖 §10.1 的 F01 表述）

**订正**：§10.1 曾写「上文 §5.8 的 `R11-F01`「完整 scope 已覆盖」由成立下调为部分闭合」——**该表述串了主题**。事实是：
- **coverage 的 stableID 是 `F01`**（在 §5.1「当前 31」表内，`:202`），其处置为「**部分闭合**……本方已完成本方覆盖与处置」，**原 owner 与事件窗口不变**；
- **`R11-F01` 是另一条目**（§5.8 本方新增条目），内容为「**M0 计划已被版本化**：两份 35812B 同 SHA `c289a1cd…` 副本在树内；AGENTS 旧路径失效 ≠ 整计划未版本控制」，**与 coverage 无关**，其处置与「否（不阻断）」结论**本轮原样保留**。

**因此**：§10.1 中 coverage 的状态应为「**F01 部分闭合**」——**在 §10.1 补读完成后，F01 的「本方已完成本方覆盖与处置」这一处置仍成立且被加强**（本轮补读 FR e2e 全文 2174 行至 EOF，并使 O074 必要正文齐备）；**但 F01 自身的接收仍由 ROOT 决定**（`:202` 原 owner/窗口不变），**本方不关闭该流程项**。**R11-F01 与 F01 不得混为一谈**；§5.8 表格内容一字不改。

### 11.5 本方当前完整 scope 结论（自然终态）

**必要缺口已闭**：本轮**本人实际读至 EOF** `tests/e2e/t02-fr200-fr201.spec.ts` 2174 行（§11.1），并据全文复核了上文全部行号引用；**O074 必要有效正文已补读齐备**（§11.2，含本人对 43 个拒绝附件的**逐个 base64 解码实测**、57 事务分组、434/487 检查的**字段级读取**、build 映射与 source→commit 绑定、limits 全文）。

**完整 scope 结论（本人据实给，不因补读自动宣告成立）**：
- **实现层**（契约/引擎/renderer/主进程/preload/CI/脚本）：上文 §3.1 已全读，**成立**。
- **新增与修改测试正文**：本轮补读后，**引擎 7 路径、unit 4 新增全文 + 8 修改差异、e2e FR 新增 2174 行全文 + 3 修改差异、fixture 全文、契约增量**，**本方必要覆盖成立**。
- **仍不闭合（非本轮授权范围，不为其申请新授权）**：修改文件的**改外无关上下文**、`packages/engine/vendor/rdflib/*` 二进制与许可、Windows/Linux/打包/生产/签名公证/跨平台运行样本。**故「完整 scope」仍不成立**，成立的是**「本方必要覆盖闭合」** —— 这是对 F01 处置的正确表述，**不等于产品放行**。

**结论：ConditionalPass（附条件通过），限定为推送前技术审查阶段**，针对 base `583c05c7` → head `d1aca3e3` 的完整累计候选 —— **与 §9、§10.7 同一结论，无上调、无下调**。

**本轮相对 §10.7 的实质增量（三项，均为覆盖闭合与算术订正，不改变结论方向）**：
1. **FR e2e 全文本人核到 EOF**（§11.1），并**订正 §10.1 的「16 个静态调用点」表述**：动态展开为 **43**（42 INVALID_REQUEST ＋ 1 OWNERSHIP_CONFLICT），与 O074 同次运行产物逐项吻合；**「43 拒绝」是当次计数，非跨轮累计**。
2. **统计算术订正**（§11.3）：有效分布 **16／48／89／7**（非 16/49/90/5）；**相对 R10 基线净改档恰 2 项（#108、#146）**；自然01 的 4 delta 作为历史保留。
3. **O074 必要正文齐备并分清三层限证**（§11.2）：同次当次计数／blob 映射绑定（**运行 HEAD 仍是 2d6，非 d1aca**）／**本机 Mac 证据不关闭 Windows 根因，静态保全件不外推为 base→head 全部产品正确**；另订正 **F01 与 R11-F01 的主题串线**（§11.4）。

**仍不成立的部分（承前，不因本轮补读而改变）**：这不是无条件整候选 Pass，不是完整 CI 通过，不是产品放行。**CI43 总体 failure**；本候选**无新 CI、未 push、未 merge、未动 PR16**；**Windows C1 异步根因 UNKNOWN**、**Windows FR201 累计超时 UNPROVEN**；**旧 CI41 根因未证与 CI43 异步新形态分列**（前者未证、后者是新形态，**两者不合并、不互相倒填**）；**本机 C1 成功未触发真实失败附件**（仅纯 mock 与静态证明）；**全部 HOLD 与 UNKNOWN 原样保留、逐一关闭数 0**；整体合并可用仍 **2/17**；Goal／M0／发布未完成。

**责任与授权**：本方只读，未改任何源码/测试/config/依赖/预算/验收，未 push/CI/merge，未重置/采购/升级，未读取另一作者本轮产物；发现实质源码问题给精确证据与最小建议，由 owner 决策；不自行修源、不追加功能或验收、不授予执行权限。**本人 Top6／R11-S01／F01–F03 与原全部稳定意见的归口、owner、事件窗口均保原**（本节仅订正 F01 与 R11-F01 的**主题串线表述**，不改其内容与结论）。

**本轮追加节自述**：§11.1–§11.5 为本轮新增，**上文 §0–§10 全部原字节未改**；本节不嵌本方最终 bytes/hash（由 owner 保存实测）。**D8 未使用。**

