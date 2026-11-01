# T02 FR-200／FR-201 全新 R06 整候选独立工程审查（MiniMax Code / M3.1-Flash）

本文件是本方（本轮独立审查方）在 R06 的唯一报告原稿。所有结论只针对 base→head 候选本身，不继承 R05 对 aff386f6 的任何判定。

---

## 0. 身份、设置与本轮边界

| 项 | 值 | 来源 |
|---|---|---|
| 审查方 | MiniMax Code（MiniMax Code CLI / MCode） | 本方运行时 |
| 模型 | MiniMax-M3.1-Flash（订阅既有权益） | 本方运行时 |
| 思考等级 | xhigh | 本方运行时 |
| 权限模式 | 始终授权 / Full access（permissionMode=bypassPermissions） | 本方运行时 |
| 会话 ID | `mvs_e7a25882036e477fa423cd4dd3a5eced` | 本方运行时上下文读回 |
| 任务 ID | **需由操作者从正式 UI 读回**；本方不自造、不代填 | 约定 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | `pwd` 实测 |
| 分支 | `feature/weekly-t02-fr200-fr201` | `git rev-parse --abbrev-ref HEAD` |
| 封存 prompt | 22602 B，SHA256 `d7691b26d307fd722a98cfec9b215f15f8babf000f74481e4062374a86e674de`，已读至 EOF（217 行，原 160 项清单恰一次在 EOF） | `shasum -a 256` + `wc -c` + 完整读取 |

**本轮未取得远端执行授权**：未 push、未创建 PR、未触发 CI、未 merge；未修改索引、分支、工作树实现。

---

## 1. 候选身份核验（实际执行，全部自测）

```
pwd                       = /Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes
branch                    = feature/weekly-t02-fr200-fr201
base  583c05c7870ba0f8f642e3eeea1d0590e5859ca2 → tree 133357a527a3967417189195b5c24e3f8a5752e8
head  831813c60a32155a579a69fc9e2cbc879b8139bb → tree 944724a8d0e2d03502de3cf6551e0cde97e5e2f4
git rev-list --count base..head = 31
git diff --name-status base..head = 79 叶
git ls-files | wc -l           = 1363
```

与封存 prompt 给定的 base/head/tree/31 提交/79 差异叶/1363 tracked 源**全部一致**。`git status` 仅见 `M AGENTS.md`（受保护现行政策 overlay，工作树未提交）与 `?? docs/reviews/T02/fr200-fr201-20261024/round-01..03/`（旧未跟踪历史报告），二者均**不属候选新增**，本方未混入、未改动。`round-04/`、`round-05/` 已入库为受审证据。

**远端真实状态（本方 `git ls-remote` 实测，与仓内文档矛盾，见 D-2）**

```
refs/heads/feature/weekly-t02-fr200-fr201 = 934bd14f2adfb7868a683a48d4e832e0aae2f6da
refs/heads/develop                        = 583c05c7870ba0f8f642e3eeea1d0590e5859ca2
```

即：分支**已被推送**，但只到 `934bd14f`；当前 head `831813c6` 未推送，因而**没有由本次 UTF-8 修复产生的任何 CI**。

**提交区间构成（自测，与封存 prompt 第 23／27 条一致）**

| 区间 | 实际内容 |
|---|---|
| `cb8c9b7a → aff386f6` | 13 文件、2517 insertions，纯文档 + 1 CI 文件；**产品/测试/依赖零改动** |
| `aff386f6 → 934bd14f` | 10 文件、1460 insertions，纯证据文档 |
| `934bd14f → 831813c6` | **恰 2 个测试文件**，+10/−6 行 |

---

## 2. 本轮实做与未做（读回证据与转述声明的区分）

**本人实际执行（全部只读或纯计算）**

1. `pwd`／`git rev-parse`／`git status`／`git worktree list`／`git log`／`git diff --stat/--name-status/--numstat`／`git show`／`git ls-files`／`git ls-remote`。
2. `shasum -a 256`：`AGENTS.md`（工作树 `de15f6ce…` vs HEAD `1b3c0291…`）、PRD、vendored rdflib 五个文件、O042 `report.json`。
3. **AST 等价独立复算**（纯计算，隔离目录 `/tmp/r06-9781/ast`，仅用 stdlib `ast`，**不导入产品、不执行任何测试**）：从 `934bd14f` 与 `831813c6` 分别 `git show` 两个测试文件 → 解析 → 只剥离新增的 `encoding="utf-8"` 关键字 → 比较 `ast.dump`。结果：**manual_input_rejection.py 5 处、read_work_budget.py 1 处，共 6 处；剥离后两文件完整 AST 与 `934bd14f` 完全相等**。封存 prompt 的「六处」成立。
4. **vendored rdflib 只读解包**（`unzip`／`zipfile`，未安装、未 import）：读 `rdflib/term.py`、`rdflib/plugins/parsers/notation3.py` 源码，定位 `_castLexicalToPython`、`Literal.__new__`、`_is_valid_langtag`；定位已发布 wheel 内 `notation3.py:931` 与 `:1609` 两处无守卫的 EOF 访问。
5. 逐份读取：PRD（FR-003/006/200/201/204/804、附录 C/D/E/G 原文）、`docs/iterations/I01/ADR-0002-storage.md`、`docs/architecture/0001`、`0003`、`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`、`docs/reviews/T02/status.md`、`docs/m0-checklist.md`、round-04／round-05 全部处置与两份独立核验、round-05 条款映射、`packages/engine/vendor/rdflib/PROVENANCE.json`、base→head 全部 79 叶差异中的产品/契约/主进程/preload/renderer/CI 部分。
6. 读回仓库外证据原件：`outputs/20261025_t02_windows_trace_utf8_repair_041/`（`fullcheck.stdout.log`、`fullcheck-start.json`、`CANDIDATE-QUALIFICATION.json`）、`outputs/20261025_t02_831813c6_original6_gui_042/`（`report.json`、`gui-exit.json`、`GUI-ACTUAL-QUALIFICATION.json`、`independent-actual-result-review.md`、`final-guards.json`）、`outputs/20261025_t02_934bd14f_remote_ci_040/`（`FINAL-CI-FACTS.json`、`FIRST-WINDOWS-FACTS.json`）。

**本人未做（不制造新口径）**

未运行 `npm run check`／vitest／pytest／ruff／build／package:dir／install／sync／HMR／GUI；未执行任何产品进程、SQL、probe；未读密钥、`.mimosa/`、无关 profile；**未读另一方本轮报告**（`round-06/` 若同时存在亦未读）。

**并行只读核验（两路 explore 子代理，结论均已由本人逐条复核后才采信）**

- 历史意见追踪（R04 Z01–Z07/M01–M07、R05 P-1–P-8/R05-01–R05-13 逐项出处与处置）。
- 证据目录核验（O041/O042/O040 原件）。
  本报告正文中标注「本人复核」的均为本人独立读回；标注「证据自述」的为原件内独立核验报告的结论，本轮**未逐笔复算**。

---

## 3. 需求依据（实际读取与哈希核验）

| 原件 | 实际值 | 本方动作 |
|---|---|---|
| `docs/prd/PRD-本体学习与落地Agent工作台.md` | 93584 B，SHA256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` | 哈希**独立复算一致**；读 FR-200/201 第 **307–318** 行、附录 C 第 959–979 行、附录 D 第 983–1015 行、附录 E 起始第 1016 行、附录 G 起始第 1115 行、FR-003/006/204/804 原文 |
| `docs/iterations/I01/ADR-0002-storage.md` | 存在（真实路径，**不在** `docs/architecture/`） | 读「决定及边界」「依赖与派生结果」「迁移与恢复」「测量与采用限制」全文 |
| `docs/architecture/0001-desktop-framework.md`、`0003-resident-coordinator-and-jobs.md` | 存在 | 读 |
| `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` | 存在（M0 更新计划真实归档路径） | 检索 T02/FR-200 命中 |
| 现行 `AGENTS.md`（工作树 overlay，未提交） | SHA256 `de15f6ce…`，HEAD 版 `1b3c0291…` | 全文按现行政策执行；**不属候选新增**，未混入 |
| 人类 D8 选择 A 原件 | `iteration-control/2026-10-21-weekly-release/user-grants/T02-D8-choice-A-20261025.json`（仓库外） | 按封存 prompt 记载采信；**本轮未直接打开该文件**，四禁止与「仅解除 T02 本功能 R4+ 限制、原 45f64 不合并、不扩功能/预算/付费」按 prompt 转述执行 |
| `licenses/NOTICE`、`packages/engine/vendor/rdflib/PROVENANCE.json` | 见 §4 验证 | 读 + 哈希复算 |

**不引用不存在的 FR-007/008**；不把 `staleReason` 之外的来源当失效规则；不改写 canonical 政策。

---

## 4. 整候选代码审查发现

### D-1 【合并阻断·门禁级】当前 head `831813c6` 从未在远端 Windows 上运行过；旧 head `934bd14f` 的 Windows job 是失败

- 读回 `outputs/20261025_t02_934bd14f_remote_ci_040/FINAL-CI-FACTS.json`：`run 40171564866`、`attempt 1`、`headSHA 934bd14f…`、`exactlyOnePushAndAutomaticRun true`、`noDispatchRerunOrCancellation true`、**`conclusion: "failure"`**、`mergeAllowed false`、`allOld79FCausesProved false`、`allWindowsAcceptanceProved false`。job：`Desktop (macos-latest)` **success 593.0s**；Quality **success 718.0s**（含 packaged application recovery success）；Windows **failure**，失败步骤为 `Windows engine first-failure diagnostic (not acceptance)`，其后 typecheck/build/e2e/package 全部 skipped。
- 读回 `FIRST-WINDOWS-FACTS.json`：Python `3.12.10`，`localeEncoding/preferredEncoding/defaultFileEncoding` 全为 **cp1252**，`utf8Mode 0`；首败用例 `packages/engine/tests/test_mainline_language_input_rejection.py::test_r03_same_owned_host_rejects_then_commits[language-first-digit-manual]`；`actualException: UnicodeEncodeError: 'charmap' codec can't encode characters in position 328-329`；`summary {failed 1, passed 980, skipped 3, seconds 258.55, stopAfterFirstFailure true, fullWindowsAcceptance false}`。
- **831813c6 是针对该首败的唯一改动**（本人 AST 复核：6 处 `encoding="utf-8"`，剥离后 AST 与父提交完全等价，产品/依赖/CI/cap 零改动）。但修复**从未被任何 Windows 运行覆盖**：`git ls-remote` 显示远端只到 `934bd14f`。
- 旧 CI36（run 40164456782 / head 58c9）的 macOS success、Quality 15 分钟取消、Windows 20 分钟取消前 79 个 F 标记，**不因本次修复而消失**；且 `allOld79FCausesProved false` 明确记录「旧 79 个失败并非全部定因」。
- 影响：Windows 完整验收为 0 证据；合并门禁未闭合。**这不是源码缺陷**，而是「修复未经平台验证」的证据缺口。

### D-2 【阻断·文档事实错误】仓内状态文件称「尚未推送」，与远端真实状态相反

- `git ls-remote` 实测：远端分支已在 `934bd14f`，`develop` 仍在 `583c05c7`。
- `docs/reviews/T02/status.md:3` 仍写「**尚未推送、创建PR、运行本候选CI或合并**」；`docs/m0-checklist.md:41` 仍写「aff 尚未 push、无新 CI」。两处**已被 O040 的真实 CI 事实超越**，按唯一状态来源规则必须更新，否则任何以 status 为准的流程都会误判远端阶段。
- 同源过期：`round-05/artifact-manifest.json` 的 `trackedSourceCount 1355 / baseDiffLeaves 71 / cumulativeCommits 29 / tree 2d9b113b` 与「implementation/tests/config/dependencies/builds remain aff-equivalent」对当前 head 已失效（实测 1363／79／31／`944724a8`，且含 2 个 `.py` 测试文件差异）。
- 已披露为 P-8／R05-04「状态入口时效」；本轮确认其**具体失效内容**并给出正确值。

### D-3 【产品缺陷·中】`definitions[].value.triples[]` 的词法未在预览期受控拒绝；提交期以未分类 `ValueError` 逃逸并 HOLD 会话

- 新守卫只覆盖 `manual`/`edits`：`packages/engine/src/ontolearn_engine/project/domain_changesets.py:448-465`（`iri(subject)`、`iri(predicate)`、`term(object)`、`parsed.n3() != value` → `INVALID_REQUEST`）。
- `definitions` 的 triples 只在 `packages/engine/src/ontolearn_engine/storage.py:726 → _definition(definition["value"])` 处校验（`storage.py:1110-1135`，第 1128–1129 行 `raise ValueError("Canonical RDF object required in definition")`），且 `storage.py:1178-1181` 的 `_validate_references` 会对**项目全部定义**重复该校验。
- 该异常**不是 `Conflict`** → `packages/engine/src/ontolearn_engine/job_store.py` 的 `_application` 中 `except Conflict` 分支不捕获 → 逃出 `preview_changeset`/`apply_application` → `packages/engine/src/ontolearn_engine/coordinator.py` 归为内部错误 → `packages/engine/src/ontolearn_engine/project/mainline.py:1187-1200 observe_error` 置 `reply.unknown = True` 且 `self.hold = True` → 之后 `mainline.py:659-663 require_owner` 一律 `fault("STORAGE_FAILURE")`。
- 实际后果：**预览显示干净 Diff、确认提交才失败，且整个引擎会话被 HOLD（需重启进程/会话才恢复）**。属用户可触发的可用性事件，非纯文档问题。
- 状态：已披露为 Z-03／M-05／P-3／R05-06「OPEN 非阻断延期」。本轮**确认仍开放**，并把后果从「wire 面坏词法走 UNKNOWN」具体化为「预览/提交分歧 + 会话 HOLD」。

### D-4 【产品缺陷·中】裸 ownership 冲突仍无定位；`Conflict` 错误码映射无 `ownership` 键

- `packages/engine/src/ontolearn_engine/storage.py:57-64`：`Conflict.code` 的映射表 `.get(category, "INTERNAL_ERROR")` **没有 `"ownership"` 键**。
- `storage.py:1230`（无 `manual_incoming` 的路径）`raise Conflict(message, category="ownership")` → `job_store.py:627-634` 落旧三字段 `{"category","resource","projectId"}` detail → `job_store.py` `_ownership_header` 对该形状 `fault("INVALID_STATE")` → 渲染层 `mainline-session.ts` 走 `ownershipDetail.status === 'unavailable'` → 界面显示「冲突详情暂不可用」。
- 即：**有 witness 的两类冲突（`ManualOwnershipConflict`、`SingleDeclarationConflict`）可定位；其余 ownership 家族不可定位**，且其错误码在契约层映射为 `INTERNAL_ERROR`。
- 状态：已披露为 Z-04／P-4／R05-07「部分采纳」。本轮确认范围未变。

### D-5 【产品缺陷·中】「首个阻断行」顺序未定义：witness 选取依赖无序扫描

- `storage.py:1212-1215`：`SELECT * FROM facts WHERE project=? AND subject=? AND predicate=?` —— **无 `ORDER BY`**；`storage.py:1147-1157` `_validate_single_slots` 的 `GROUP BY subject … LIMIT 1` 与 `LIMIT 2` 同样无确定序。
- 而 `storage.py:67-86` 的 `ManualOwnershipConflict` 文档字符串明确声称 witness 是「**the actual first blocking row**」，`SingleDeclarationConflict` 声称是「**the actual first two blocking records**」，UI 标题为「首个阻断冲突定位」。
- 后果：跨运行／跨 SQLite 版本下 witness 记录不保证稳定，界面展示的「首个」不可复现，且不受回归测试约束。
- 状态：已披露为 Z-01／R05-08「未确认观察，不升级缺陷」。本轮把它从「未确认」推进为**可核对的源码事实（SQL 无 ORDER BY）**，仍不擅自升级为已证跨运行缺陷。

### D-6 【产品缺陷·中】已发布 vendored wheel 的 standalone EOF 残留未类型化 `IndexError`，可逃逸为未分类 `ValueError` → HOLD

- 本人用 `zipfile` 只读解出已发布 `packages/engine/vendor/rdflib/rdflib-7.6.0+ontolearn.fr201.3-py3-none-any.whl` 内 `rdflib/plugins/parsers/notation3.py`：第 **931** 行 `while argstr[j] in {"!", "^"}`、第 **1609** 行 `if argstr[j] == "@"` **无边界守卫**。
- `packages/engine/vendor/rdflib/notation3-input-types.patch` 只在 `elif ch == "\\"` 分支补了 `UnterminatedStringError`，**未覆盖 931／1609**。
- 逃逸链：未捕获 `IndexError` → `packages/engine/src/ontolearn_engine/rdf_snapshot.py:44-45` 的 broad `except Exception` → 变为**普通 `ValueError`（非 `TermInputError`）** → `domain_changesets.py:459-465` 只捕 `TermInputError` → 逃逸 → 与 D-3 同款 HOLD 后果。
- 状态：已披露为 M-04「保留既有 OPEN，不泛捕 IndexError」。本轮确认发布制品内仍存在该路径。

### D-7 【产品缺陷·低-中】渲染端错误码白名单缺 16 个契约码

- 本人实算：`packages/contracts/v2/errors.json` 共 **26** 码；`apps/desktop/src/renderer/src/ontology/mainline-session.ts:86-104` 白名单 **17** 码；交集 **10**；**缺 16**：`CURSOR_EXPIRED, CURSOR_MISMATCH, ENGINE_EXITED, HANDSHAKE_REQUIRED, MAPPING_VALUE_INVALID, METHOD_NOT_ALLOWED, NETWORK_FORBIDDEN, NOT_FOUND, PAYLOAD_EVICTED, QUEUE_FULL, SEMANTIC_INPUT_INVALID, SESSION_MISMATCH, TIMEOUT, UNSUPPORTED_CAPABILITY, UNSUPPORTED_CONSTRUCT, VERSION_INCOMPATIBLE`。
- 后果：这 16 码在 UI 落到通用「操作未能完成」文案，用户得不到可执行信息。
- 状态：已披露为 Z-05／P-5／R05-05。**集合事实成立，但本轮仍未证明这 16 码在当前所有错误路径均可达**；不擅自改白名单（共享契约维护者负责）。

### D-8 【测试脆弱·低】两个 TS 单测仍依赖 PATH 上的 `python`

- 本人实读：`tests/unit/t01-mainline-contract.test.ts:656` 与 `tests/unit/t01-ontology-metadata-contract.test.ts:168` 均为 `execFileSync('python', ['-I','-B','-c', script], …)`；对照 `tests/unit/t02-manual-fact-id.test.ts` 已改用固定 `.venv` 路径。
- 已知首败（O035 裸调用 Python ENOENT 两处）按 status.md 保留。Windows 当前不跑 vitest，故**不归为 79F 根因**。
- 状态：已披露为 R05-12「部分采纳非阻断维护」。**代码事实仍成立**：处置表称「作者已改正」指的是原报告表述更正，源码并未改。

### D-9 【信息】Ruff 369／379／380／386 是四次不同真实运行；380／386 仓内无记录

- 369（O029）、379（O036）、380（O040 三个远端 job log）、386（O041 `fullcheck.stdout.log:107`「386 files already formatted」）均为**各自日志实测值**，互不相同。
- 仓内 `round-05/disposition.md:29` 与 `status.md` 只讨论 369/379；**380 与 386 无任何仓内记录**。按既有口径不推断任何差因。

### D-10 【覆盖缺口·中】附录 D／E／G 无条款映射

- `round-05/fr200-fr201-original-clause-evidence-map.md` 结构为：§1 身份与读回、§2 FR-200 第 309 行 12 行拆分、§3 FR-201 第 313–318 行 4 行、§4 附录 C 13 行（**每行「实际证据」栏均为「本次未执行」**）、§5 修订短补充。**附录 D（983–1015）、附录 E（1016–1095）、附录 G（1115+）无任何映射行**。
- 后果（点名）：附录 D.2 第 994–1000 行的失效联动义务**正是 FR-200 的编辑对象**（本体类/属性/层级/定义域/值域变化 → 必须标记过期：当前推导、保存查询结果、SHACL 结果、报告；不得删除断言事实）。本候选覆盖了这些定义的 CRUD，**却没有任何证据说明改了它们之后下游结果被正确标记过期**。`packages/engine/src/ontolearn_engine/invalidation-v2.json` 是否覆盖该四类下游，本轮**未核 → 无法确认**。
- 这不构成「实现缺失」的断言，只构成「本轮不可据此宣称 FR-200 整条及其失效联动已验」。

### D-11 【信息】4299／4300 应用层仍无断言

- 全仓仅见 `"9" * 4301`（`packages/engine/tests/test_mainline_language_input_rejection.py:36`、`tests/e2e/t02-fr200-fr201.spec.ts:831`）；`PROVENANCE.json:147-148` 的 `actualIntegerLimit: 4300` 与 `integerBoundary` 属**说明文字**，非断言。4300/4299 边界在应用层无回归。

### D-12 【可核对正面结论】

| 结论 | 证据 |
|---|---|
| 831813c6 的六处 `encoding="utf-8"` 剥离后与父提交**完整 AST 严格相等** | 本人隔离目录纯 `ast` 复算（§2.3）；O041 `CANDIDATE-QUALIFICATION.json` 的 `ASTAfterRemovingSixKeywordsEqualsOriginal: true` 旁证 |
| O041 本地全检真实自然 0 | `fullcheck.stdout.log:52-53` TS 39 文件/1892 通过；`:106` All checks passed；`:107` 386 files already formatted；`:113` 3769 collected；`:240` 3719 passed/50 skipped/1 warning/160.24s；`fullcheck-start.json` pid 55024、`headAtExecution = 934bd14f…`（**即：进程启动时 Git HEAD 是 934bd14f + 两处工作树测试修订，不是 8318**，与封存 prompt 的限定一致） |
| O042 GUI 真实 6 PASS | `report.json` 4001380 B、SHA256 `0cba6522ffb7874f20f0226531cd123d5b6f25b3a73cba86bba13361b5d54e6f`（**本人 shasum 复算一致**）；`stats {duration 108413.912, expected 6, skipped 0, unexpected 0, flaky 0}`；`gui-exit.json {exitCode 0, naturalProcessExit true, runnerPid 58606}`；`GUI-ACTUAL-QUALIFICATION.json` head 831813c6 / tree 944724a8；`final-guards.json` 1363 源 + 5 build + 旧 094 包 912 成员与 rootmode 前后/当前全等 |
| vendored rdflib 五个文件哈希**全部匹配** PROVENANCE | 本人 `shasum`：fr201.3 `99fab7bd…`（=PROVENANCE artifact）、upstream `30c0a3eb…`、LICENSE `53a705e5…`、patch `de5755d6…`；fr201.1 `13be2a17…`、fr201.2 `f30e6279…` 为历史留存 |
| 打包体积差因可解释 | upstream wheel 615416 B（142 成员 DEFLATED），fr201.3 2379774 B（142 成员 **ZIP_STORED**，PROVENANCE 明示），成员总数与未压缩总量一致（2358325 vs 2358909）→ 差异是**压缩方式**不是内容膨胀；`596328` 是压缩成员 payload 之和，非整 wheel 大小（R05-09 的计量纠正成立） |
| 依赖指向受控本地 wheel | `packages/engine/pyproject.toml`：`rdflib==7.6.0+ontolearn.fr201.3` + `[tool.uv.sources]` 指向 `vendor/rdflib/…fr201.3…whl`；`uv.lock` 同步改为本地 path source 并保留 hash/size |
| 无通用 IPC 通道 / renderer 无 Node 能力 | 新增 `project:ownership-detail` 为具名方法（`apps/desktop/src/main/desktop-ipc.ts:64-65,194`、`apps/desktop/src/preload/index.ts:56`）；`engine.ts:349,1232,1243-1247` 增白名单并强制 `params.projectId === selected` |
| SQL 注入面已防 | `project_host.py` 的 `material_profile` 与 `mainline.py:553-571` 对表名/列名一律 `'"' + name.replace('"','""') + '"'` 标识符转义，无拼接用户输入 |
| 渲染层无 XSS sink | `apps/desktop/src/renderer/src` 内 `dangerouslySetInnerHTML`／`new Function`／`eval(` 零命中（本轮 grep） |
| 仓库无 tracked 凭据 | `git ls-files` 中无 `.env`／key／secret 类文件（仅 `tokens.css` 命中前缀） |
| D8 四禁止在代码层成立 | `rdf_snapshot.py:13-14` `TermInputError` 精确分类；`domain_changesets.py:448-465` **只捕 `TermInputError`**（不泛捕 `ValueError`）、按异常类型而非文案分类、`parsed.n3() != value` 即拒绝（**不静默规范化**）、容量常量未上调（`READ_LIMITS` 相对 base 未放宽） |

---

## 5. 历史意见逐项追踪（R04／R05 全部 35 项）

**编号说明（本人核对后更正）**：R04 的 `Z-01…Z-07` = ZCode GLM53 的「问题 1–7」，`M-01…M-07` = MiniMax 的「T02-R04-01…07」；R05 的 `P-1…P-8` = ZCode R05 意见，`R05-01…R05-13` = MiniMax R05 意见（**并非「M01–M13」**）。以下处置结论均为**当前 head `831813c6` 上的复核结果**，不是 R04/R05 原文的自述。

### 5.1 R04 十四项

| 码 | 内容 | 原处置 | 本轮在 831813c6 上的复核 |
|---|---|---|---|
| Z-01 | 冲突查询无 `ORDER BY`，「首个阻断行」未确认 | 未确认观察 | **仍开放**，本轮升级为源码事实（D-5，`storage.py:1212-1215`／`:1147-1157`） |
| Z-02 | witness 字符串上限跨层不一致 → UI 详情恒不可用 | 作者撤回 | **撤回成立**（43692 确为 capture 分页信封长度）；但审计员要求单列的「整文档 262144／16 MiB 预算 + `index.ts` 注释」在处置表中**无独立行**，仍按 OPEN 保留 |
| Z-03 | `definitions[].value.triples[].object` 坏词法 → UNKNOWN/HOLD | OPEN 非阻断延期 | **仍开放**，并确认后果为「预览/提交分歧 + 会话 HOLD」（D-3） |
| Z-04 | 通用 ownership 冲突无定位 | 部分采纳 | **仍部分开放**（D-4）：有 witness 两类可定位，其余不可 |
| Z-05 | 渲染白名单 17 vs 契约 26，缺 16 | 非阻断延期 | **集合事实仍成立**（本人复算一致，D-7）；可达性仍未证 |
| Z-06 | `de-CH-1901` 拼写与 canonical 政策张力 | 现有政策继续 | **维持**：本轮从 vendored `term.py` 读到 `inst._language = lang`（**rdflib 不做小写化**），故 `rdf_snapshot.py:57` 的显式 `.lower()` 是唯一小写化点；`"x"@de-CH-1901` 被拒、`"x"@de-ch-1901` 可提交，与既有政策一致。**不为当前候选另设人类政策前置** |
| Z-07 | 核心文件规模 2993/1887/1748 | 信息级 | 本轮实测：`job_store.py 2993`、`storage.py 1887`、`tests/e2e/t02-fr200-fr201.spec.ts 1748`、`mainline.py 1206` —— 数值一致；仍为信息级，不据 LOC 推正确性 |
| M-01 | 仓内无状态来源记录 FR-200/201 | 采纳并完成 | **仍存在冲突**：归档版 `round-04/archive/all-opinions-disposition-original.md:14` 为「部分采纳…交 ROOT」，最终版 `round-04/disposition.md:14` 为「采纳…本次完成」，两版并存无差异说明 |
| M-02 | vendored wheel 冗余 3 版本 + 锁文件不约束内容哈希 | 核心前提不采 | 本轮补强：PROVENANCE 与 uv.lock 均含 hash/size，且**本人复算五文件哈希全部匹配**；三历史 wheel 保留属审计留存，不删 |
| M-03 | 整数边界应用层不可证 | 部分采纳 | **仍开放**：仓库内只有 4301，无 4299/4300 断言（D-11） |
| M-04 | vendored patch 未覆盖文档级 EOF | 保留 OPEN | **仍开放**，本轮在**已发布 wheel 内**定位 `:931`／`:1609`（D-6） |
| M-05 | `term()` broad 分支两条出口错误语义不同 | 部分观察 | **仍开放**：D-3／D-6 给出了两条具体逃逸链 |
| M-06 | `changeSetFact` 契约只约束 `id` 形状 | 维护建议 | 本轮确认 `changeSetFact` 已要求 `subject/predicate/object` 为非空字符串（`maxLength 262144`），`additionalProperties false`；该建议已部分被契约演进覆盖，不认定为缺陷 |
| M-07 | `@ontolearn/contracts/v2` 桶导出暴露三模块并集 | 信息级 | **仍开放**：`packages/contracts/package.json` 的 `exports` 仍是 `{".":"./src/index.ts","./v2":"./src/design-v2.ts"}` |

### 5.2 R05 二十一项

| 码 | 内容 | 原处置 | 本轮复核 |
|---|---|---|---|
| P-1 | Windows 79F 根因未关闭 | 合并阻断 OPEN | **已部分超越但门禁未闭**：O040 取得**首个真实首败栈**（cp1252 `UnicodeEncodeError`）；但 `allOld79FCausesProved false`、`allWindowsAcceptanceProved false`，且**当前 head 无 CI**（D-1） |
| P-2 | Quality job 取消未复绿 | 合并阻断 OPEN | **在 934bd14f 上已实测绿（718s，含 packaged recovery success）**，处置表该行已过时（须更新，但**不得据此取消 Quality 门禁**——绿的是父提交） |
| P-3 | `definitions.triples` 词法 | OPEN | 仍开放（D-3） |
| P-4 | ownership 定位 | 部分采纳 | 仍部分开放（D-4） |
| P-5 | 白名单缺 16 | 非阻断延期 | 仍开放（D-7） |
| P-6 | canonical 语义边界 | 部分采纳，不新设人类前置 | 维持（D-12 末行、Z-06） |
| P-7 | 诊断步 `PYTEST_ADDOPTS` + 文件行数 | 信息项 | 仍开放：`.github/workflows/ci.yml` 仍以 `PYTEST_ADDOPTS: '-vv --maxfail=1 --tb=short'` 改写 Windows 有效 pytest 选项，**不得称「未改任何验收命令」**；行数已更新（含 `mainline.py 1206`） |
| P-8 | `status.md` 为 58 时点快照 | 时点披露 | **已具体化为实质错误**：status/m0-checklist/artifact-manifest 三处均称未推送，而远端已在 934bd14f（D-2） |
| R05-01 | Windows 无成功证据、79F 根因为高可信假设 | 部分采纳 | 部分超越（D-1）：首个首败栈已定因到 cp1252，**但旧 79F 全同因未被证明** |
| R05-02 | 三 job 两 cancelled、无远端全绿 | 采纳阶段事实 | **已过时**：934bd14f 的 macOS 与 Quality 均 success；Windows failure。**当前 head 仍无 CI** |
| R05-03 | 本候选无自产新包与包内运行 | 采纳 | **仍成立**：无 8318 新包制造/新包内运行；旧 094 包 912 成员与 rootmode 前后/当前全等（O042 `final-guards.json`） |
| R05-04 | 状态入口停在 58c9 | 部分采纳，不采计数差因果 | 仍开放且已具体化（D-2、D-9）；Ruff 差因**仍不推定** |
| R05-05 | 白名单仍缺 16 | 非阻断延期 | 仍开放（D-7） |
| R05-06 | definitions 早期坏词法 → UNKNOWN/HOLD | 采纳 OPEN | 仍开放（D-3） |
| R05-07 | 通用/受管 ownership 定位 | 部分采纳 | 仍部分开放（D-4）；`SingleDeclarationConflict` 确有真实 witness，标题应收窄——本轮同意该收窄 |
| R05-08 | 「首个阻断行」排序未规定 | 维持未确认 | 本轮给出来源码事实（D-5），仍不新设排序验收 |
| R05-09 | vendored 可复现 + 仓库体积 | 部分采纳，计量纠正 | **本轮复核支持该纠正**：615416 B vs 596328 的关系成立（D-12） |
| R05-10 | AGENTS 失效链接在未提交 overlay | 指南维护，不属 aff 缺陷 | **仍成立**：overlay SHA256 `de15f6ce…` ≠ HEAD `1b3c0291…`，未提交、未混入候选；**本轮不因此重开产品审查** |
| R05-11 | ownership 定位不含 object | 非缺陷信息边界 | **仍成立**：`storage.py:67-86` 的 `locator()` 只返回 `id/owner/sourceRow/slot`，无 object |
| R05-12 | 两 TS 单测依赖 PATH `python` | 部分采纳 | **代码事实仍在**（D-8）：`t01-mainline-contract.test.ts:656`、`t01-ontology-metadata-contract.test.ts:168` |
| R05-13 | 核心文件变大 | 信息级 | 仍信息级（D-12 末） |

### 5.3 处置表本身的三处事实性缺口

1. **无任何处置回执以 `831813c6` 为受审对象**：仓内 `round-04/disposition.md`、`round-05/disposition.md`、`round-05/artifact-manifest.json`、`docs/reviews/T02/status.md` 均停在 aff386f6/934bd14f 之前的时点。
2. **P-1／P-2／R05-01／R05-02 的处置已被 O040 新证据超越**，处置表未记录 run `40171564866` 与其 Windows 首败栈。
3. **审计员要求但处置表未单列的项**：Z-02 的「整文档 262144／16 MiB 边界 + `index.ts` 注释」需独立保持 OPEN；M-03 的「未做 mutation 实验故不得保证式宣称未来改动必失败」限定未写入处置；P-7 的「有效 pytest 选项已变」限定未写入处置。

---

## 6. 证据读回：旧证据 vs 本候选新证据（严格区分）

| 证据 | 归属候选 | 实测内容 | 是否覆盖 831813c6 |
|---|---|---|---|
| O040 `20261025_t02_934bd14f_remote_ci_040` | **934bd14f** | run 40171564866；macOS success 593s；Quality success 718s；**Windows failure**；首败 cp1252 `UnicodeEncodeError`；1 FAIL/980 PASS/3 SKIP/258.55s；`mergeAllowed false` | **否**（父提交） |
| O041 `20261025_t02_windows_trace_utf8_repair_041` | **931813c6 的物理内容**，但 `headAtExecution = 934bd14f` | focused 151 PASS/22.58s；fullcheck 自然 0/178.72s，TS 39/1892，Py 3769 收集/3719 PASS/50 SKIP/1 warning/160.24s，Ruff 386；`executedPhysicalSourceEqualsAll1363PostcommitPhysicalSource true`、`currentBuildsEqualActualFullcheck5 true`、`ASTAfterRemovingSixKeywordsEqualsOriginal true` | **是**（内容等价） |
| O042 `20261025_t02_831813c6_original6_gui_042` | **831813c6** | 6 PASS/0 skip/0 retry/0 flaky/108413.912ms；runner 58606 自然 0；report 4001380 B/`0cba6522…`（本人复算一致）；58 附件、57 事务（7/7/7/7/22/7）、43 拒绝（42 INVALID_REQUEST + 1 OWNERSHIP_CONFLICT）、6 fresh profiles、104 采样/33 已知 PID start、旧 094 包 912 成员与 rootmode 前后/当前全等 | **是**（开发 GUI，macOS） |
| 原 package094 包内 18 项 / named 24 / text0022 | **原 cb8 制品** | 16 PASS + 2 原 Linux 条件 skip 等 | **否**（旧制品，仅按旧包范围有界保留） |
| 旧 CI36 / run 40164456782 / head 58c9 | **58c9** | macOS success、Quality 15m 取消、Windows 20m 取消前 79 F | **否**，且**不因本次修复消失** |

**本人未复算、仅采信原件内独立核验报告的 O042 逐笔结论**：58 附件逐个解码一致、57 事务逐笔 before/after Read 连续性、FR200 28 笔与 FR201 22 笔逐笔语义、43 拒绝逐件 Read 相等、104 采样与 PID 表、main 606471 B/`6470899108e…` 与 builtHTML 绑定、8 环境实际缺席。原件明确写明：**FullRead 相等不等于物理 DB 零写；不覆盖 Undo GUI、全部 ownership 家族、签名/公证/法律/全平台/参考设备/容量/旧库恢复及 UNKNOWN/HOLD；不继承 R05 verdict；新 8318 的 Windows 完整 GREEN 仍缺。**

**本轮无任何新包装配、无包内运行、无新 CI、无新 probe**；旧失败（0e7 TIMEOUT、O027 三 FAIL、093 的 13PASS/1FAIL/2skip/2NOTRUN、text001 首败、R03 ZPass/MMFail、O022 被拒 probe）按既有规则保留，未重试被拒 probe、未开旧失败 DB/profile/SQL。

---

## 7. 独立 HOLD（全部保留，未被本轮任何证据抵消）

签名／公证／wholeApp 法律与 `_distutils` 来源；全平台／参考设备／macOS 15／Win11；性能容量 Q5／D2 与旧超限库恢复；损坏 SQLite 物理资源保护（用户明确保留）；unknown parser／N3／Store／坏快照；Undo GUI 与未实测 ownership 家族；上述未知退出码（native engine 与 named App 部分 exit 仍 UNKNOWN）。本轮新增的两项证据缺口亦不得被内部演示／本机绿冲抵：**831813c6 无 Windows 完整验收**、**远端分支已推送但仓内状态未更新**。

当前合并可用仍为 **2/17**（FR-401/402）；本轮**不新增 FR、不宣称 Goal／发布／M0 完成**。

---

## 8. 原始 160 项清单逐条（本方独立适用性判断）

> 说明：本节不是新增 160 项验收，而是对封存 prompt 原文 160 条的一次逐条适用性判定。判定基于本轮对**实际代码、配置、需求与证据**的阅读；未实际读到的一律写「无法确认」，不假装检查过。不为凑数新增无用功能。

1. 不适用 —— 本地单机桌面应用，无多租户表结构设计；本体/定义/事实模型由 PRD 附录 C 主定义固定（`docs/prd/…:959-979`），非"表级临时设计"。
2. 不适用 —— 无账号体系、无邮箱输入、无登录流程；`engine.ts` 无任何 auth 方法。
3. 不适用 —— 无密码重置；本地项目不经服务端。
4. 不适用 —— 无 MFA 与用户身份体系。
5. 部分适用 —— 会话概念存在但语义不同：引擎会话由 `mainline.py:602-654 MainlineHost` 的 owner/lease 模型约束（`owner_id`、`session`、`host_client_id` 三元绑定），非登录会话 TTL；无"用户级会话"概念，故"kill one user's sessions"不适用。
6. 不适用 —— 无 SSO；本地优先，无云身份。
7. 不适用 —— 无 SAML；同上。
8. 不适用 —— 无 SCIM、无企业目录。
9. 不适用 —— 无"用户角色"；权限是**方法级白名单**（`engine.ts:1228-1247`、`coordinator.py:436-443`）与**对象级所有权**（`_OwnershipProof`），属工程隔离而非 RBAC。
10. 适用且通过 —— 越权读取按真实所有者拦截：`_OwnershipProof.check`（`mainline.py:492-507`）校验 store/lease/project/generation/method/reply；`engine.ts:1243-1247` 强制 `params.projectId === record.selected?.projectId`；preload 不暴露通用 invoke。
11. 适用且通过 —— 单租户本地应用，无跨客户数据路径；`authorize()`（`mainline.py:668-675`）拒绝非选中项目。
12. 不适用 —— 无"登录为他人"按钮；无支持人员代理身份。
13. 不适用 —— 无登录面，故无口令爆破面；引擎侧有 `RESOURCE_LIMIT`／`QUEUE_FULL` 限流（`coordinator.py:99,521`）。
14. 不适用 —— 无锁定策略可致 CFO 被锁。
15. 部分适用 —— 有格式迁移且**可回滚**：`coordinator.py:1124-1136` 目标格式 3、`storage.py` v1→v2→v3 迁移；ADR-0002「迁移与恢复」载明「失败回滚 DDL/版本及数据，重开可重试」「未来格式拒绝打开，不静默改写」。未验：真实旧库迁移的端到端运行证据。
16. 部分适用 —— 迁移取事务写锁后**重读**格式版本以防两个 opener 重复 DDL（ADR-0002）；但按既往处置（ZCode#16），**单写者/启动期迁移不等同在线无锁证明**，本轮未验在线并发迁移。
17. 部分适用 —— 索引与查询面有界：`job_store.py:52-66` 的 `cursor_ttl_ms ≤ 60000`、`max_cursor_records ≤ 4096`、`job_store.py:2561` 上限即拒绝；`project_host.py` 的 `material_profile` 以行数/字节/工作量三聚合做准入（超出即 `RESOURCE_LIMIT`）。缺口：Q5 容量未定，未验 500 万行量级。
18. 不适用 —— 单进程 SQLite，无连接池；`store._db` 为独占句柄（ADR-0002「同一 lifetime lease」）。
19. 部分适用 —— 有快照与备份原语：`ADR-0002` 载明 `backup(newPath)` 使用 SQLite 在线备份、禁止覆盖目标、可恢复全部当前数据与所有权；FR-004 自动保存与可恢复快照。缺口：**无定时夜间备份策略**（桌面应用无守护进程），且本候选未新增。
20. 部分适用 —— 恢复路径存在（快照恢复、项目包 FR-1000 方向），但**"从备份实际恢复"未在本候选实测**；旧 094 包内恢复属旧制品范围，不外推。
21. 不适用 —— 无数据库删除事故场景的运维需求；不可变历史与墓碑删除是主设计（ADR-0002）。
22. 适用且通过 —— 删除为可审计 no-op（ADR-0002「移除未知事实当前为可审计 no-op，终态不可改写」）；UI 删除前展示影响范围（`mainline-ontology.ts` 262-296 收集 S/P/IRI 命中，`OntologyPage.tsx:346-366` 先读并列出影响，有引用则拒绝计划）。
23. 适用且通过 —— 校验在引擎侧而非仅表单：`domain_changesets.py:448-465`（服务端受控词法拒绝）、`storage.py:1110-1135 _definition`、`job_store.py` 契约校验；schema 侧 `changeSetFact` 强制 subject/predicate/object 非空字符串。
24. 不适用 —— 无跨时区提醒/日程；本地单机无时区业务语义。缺口未涉及。
25. 适用且通过 —— 撇号等字符在字符串字面量内不受影响；`term()` 走 Turtle 解析并要求 `parsed.n3() == value` 精确往返（`rdf_snapshot.py:30-58`）。
26. 部分适用 —— **本轮的真实痛点**：Windows cp1252 下 `write_text` 无 encoding → `UnicodeEncodeError`（O040 首败栈）；候选用 `encoding="utf-8"` 修复测试落盘。产品侧 Unicode 处理：渲染层显式拒绝孤立代理项（`mainline-facts.ts:56-62`）。缺口：**RTL 未覆盖**；产品侧在 Windows cp1252 默认编码下的实际写入路径（本轮无 Windows 实跑）。
27. 不适用 —— 无金额/货币计算。
28. 不适用 —— 无货币、税务规则。
29. 适用且通过 —— 数据模型有版本化契约与单一真源：`packages/contracts/v2/schema.json`（141 个 `$defs`）、`registry.json` 记录方法与实现、`uv.lock`/`package.json` 锁精确版本；Store 格式版本化迁移（ADR-0002）。本候选新增 `project.ownership.detail` 同步登记于 `registry.json` 与 `schema.json`。
30. 适用且通过 —— 幂等键即 `operationId`：`storage.py` `operation_claims` 表 + `has_operation_claim` + `apply_application` 幂等认领；`mainline.py:968-1003` 明确"已接受操作按原始请求/actor 认证"，重复提交不再取新 CAS。
31. 部分适用 —— 四次点击去重由 UI 侧 `mainline-session.ts` 单飞（`#queuedRead` 合并 + `this.#sequence` 递增围栏）与引擎侧 `begin()` 拒绝并发 current（`mainline.py:707-710`）共同保证。**按既往限定（ZCode#31），受控输入拒绝本身不独自证明"四次点击去重"**；本轮读到的围栏代码是实现证据，未构造四连点反例。
32. 适用且通过 —— 分页有游标语义：`cursor_ttl_ms`、`max_cursor_records`、游标内含原 page_size 并校验（`mainline.py:844-847`）；ownership 详情分段读取 `startOrdinal/pageSize ≤ 64`、`segmentCount ≤ 512`（schema）。缺口：未验"第 400 页"量级。
33. 不适用（本候选范围）—— 导出属 FR-203（`docs/prd/…:324-328`），本候选只做 FR-200/201；不得据此称 FR-203 完成。
34. 不适用（本候选范围）—— CSV 导入属 FR-300 映射域。
35. 部分适用 —— 有明确"历史不可改写、缓存回收不得触及历史"的规则（ADR-0002「`collect_cache` 只置空未被报告 pin、未作为当前结果的可重建载荷…快照、状态、定义、来源、输入快照仍保留」）。缺口：无"按合同自动删除"的商业规则（无合同体系）。
36. 适用且通过 —— `git ls-files` 无 `.env`/key/secret；AGENTS 禁止提交凭据与 `.mimosa/`；错误面只传固定错误码与受限参数（`mainline.py:762-774` 只映射 7 个 reason→固定码），不回传原始异常/路径/单元格原值。
37. 不适用 —— 无运行时密钥；模型凭据属 S3 之后且凭据只在主进程（AGENTS「模型外发」不变量），当前尚未接入。
38. 适用且通过 —— **本轮直接验证**：vendored rdflib 五文件哈希全部与 `PROVENANCE.json` 一致；`pyproject.toml` + `uv.lock` 指向本地固定 wheel 并带 hash/size；`NOTICE` 记录上游许可与透明本地补丁位置；上游整 wheel 与补丁 wheel 成员数一致、差异仅压缩方式（D-12）。
39. 部分适用 —— 依赖固定到精确版本且有 lock（`npm`/`uv` 双锁 + CI `npm ci`/`uv sync --frozen`）；**未配置自动依赖漏洞扫描**（无 Dependabot/Renovate/OSV 任务）。缺口明确。
40. 部分适用 —— FR-200/201 的输入面已有受控词法守卫（`domain_changesets.py:448-465` 覆盖 manual/edits），**但 `definitions[].value.triples[]` 未覆盖**（D-3），且 standalone EOF 路径未类型化（D-6）。
41. 适用且通过（SQLi/XSS/CSRF 局部）—— SQL：标识符正确转义、值参数化（`project_host.py`、`mainline.py:553-571`）；XSS：renderer 无 `dangerouslySetInnerHTML`/`eval`；CSRF：Electron IPC 靠 contextIsolation + sender/mainFrame/可信文档校验，不适用传统 CSRF；OWASP 其余项（SSRF/XXE 等）在无网络、无 XML 导入面下不适用。
42. 适用且通过 —— 内置示例包是"文件读取"的唯一外部资源面：`mainline.py:304-342` 用 `O_NOFOLLOW`+`O_DIRECTORY`+`O_NONBLOCK`+`fstat` 拒绝 FIFO/超限/被替换文件；`:366-404` 校验 manifest SHA256、字节数与 canonical 内容；无"用户上传"面。
43. 不适用 —— 不开 HTTP 端口（AGENTS 架构不变量）；无 CORS 面。
44. 部分适用 —— 无 HTTP 响应；替代面为 Electron CSP（唯一配置源 `apps/desktop/src/csp.ts`，本候选未改动）与窗口/导航安全策略。缺口：CSP 的生产/开发两变体本轮未逐项复核。
45. 部分适用 —— 传输：无网络链路，N/A；静态：本地 SQLite 未加密（N/A 于单用户本地，但仍是真实边界）；模型凭据按 AGENTS 只在主进程。缺口：明确记录"本地库不加密"。
46. 适用且通过 —— **本候选的核心设计**：`_WriteAdmission`（`mainline.py:66-286`）确保写权限只来自进程拥有的 reply/operation，不来自 wire；`prepare_mainline_store` 只加限制不加权限；`MainlineHost.bind` 要求 owner 是真实 `Coordinator`+`business3`+非 test_mode；`ownership_proof` 为栈内签发、wire 不可构造（`_OwnershipProof` 为 frozen dataclass，仅内部生成）。
47. 适用且通过 —— 记录 origin（`ownerId/hostClientId/engineSessionId`）、job/operation/marker、参数 hash；跨边界只传固定错误码与受限参数（`mainline.py:510-515`、`:762-774`）；不回传密码/token/单元格原值。
48. 不适用（尚无外部企业客户）—— 独立渗透测试未做；已保留为发布前门禁事项，未宣称完成。
49. 不适用 —— 无企业销售与问卷流程；`licenses/NOTICE` 已具备可支撑问卷的事实基础。
50. 不适用 —— 未公开发布，无外部漏洞报告入口。
51. 部分适用 —— 无生产服务凭据；但本地项目库被拷走即数据泄露，**未做本地库加密或导出审计**（见 45）。
52. 不适用 —— 无 SOC 2 义务客户；**不得据此取消法律/签名/公证等独立 HOLD**。
53. 不适用 —— 无患者数据；产品域是本体建模，非医疗。
54. 不适用 —— 无 BAA 场景（无 PHI、无外部模型）。
55. 不适用 —— 单用户本地应用无"谁查看过"的概念；候选的 ownership witness 是**变更时定位**，不是查看审计。
56. 不适用 —— 无支付、无卡号数据。
57. 不适用 —— 无个人数据主体、无云端副本或备份删除链路；本地库中的人名仅作为业务概念字符串。
58. 不适用 —— 无服务端，数据不出本机，天然满足居住地要求（这是本地优先的直接收益）。
59. 不适用 —— 无多用户、无季度访问评审对象。
60. 部分适用 —— CI 有 macOS/Windows 矩阵（`.github/workflows/ci.yml`）作等价环境；**当前 Windows 门禁未绿**（D-1）；无生产环境。
61. 部分适用 —— 无云基础设施可写为代码；CI 工作流是本项目实际的"编排即代码"，但**无 IaC（无 Terraform/Ansible）**，因为没有服务器。
62. 适用且部分通过 —— 有 CI 先测试后合（lint/格式/类型/vitest/构建/ruff/pytest + e2e + package）；**当前 Windows job 失败**（D-1），故"测试先于客户"目前**未被证明**。
63. 部分适用 —— 无部署回滚；有"撤销一次 ChangeSet"与快照恢复（FR-004、ADR-0002），但**Undo GUI 未实测**（独立 HOLD 保留）。
64. 不适用 —— 桌面应用无停机窗口概念；升级靠安装包替换。
65. 部分适用 —— 无通用 feature flag 框架；但业务能力按 profile 门控（`profile == "business3"`，`coordinator.py:436-443`、`mainline.py:102-106`），等价于编译期开关。
66. 不适用 —— 本地单机，无弹性伸缩。
67. 不适用 —— 无 CDN；本地资源。
68. 不适用 —— 无域名/证书；桌面应用离线运行。
69. 适用且通过 —— 有常驻作业体系：`Coordinator` + `JobStore` + job 状态机（succeeded/failed/cancelled），`ADR-0003` 覆盖常驻协调器与作业。
70. 部分适用 —— 面向第三方的重试退避不适用（无第三方 API）；引擎对可重试错误给 `STORAGE_BUSY` + `retryAfterMs`（`coordinator.py:99`、`job_store.py:295`），作业幂等重入靠 `operation_claims`。缺口：无通用指数退避。
71. 部分适用 —— 无 DLQ 概念；但**失败诊断被持久化在回滚事务之外**（`job_store.py` 的 ownership detail 走独立提交），使失败可事后取证。缺口：作业终态失败的集中重试队列未实现。
72. 不适用 —— 无 cron；但重复投递幂等由 `operationId`/`operation_claims` 保证（见 30）。
73. 部分适用 —— 无缓存层；有"当前推导"与失效语义（`invalidation-v2.json` 为唯一机器规则源）。**缺口：本候选改类层级/domain/range 后的下游失效联动未被证据覆盖**（D-10，附录 D.2 未映射）。
74. 不适用 —— 不发事务邮件。
75. 不适用 —— 无邮件发送。
76. 不适用 —— 无云存储计费；本地磁盘占用无清理策略（见 78）。
77. 不适用 —— 无模型调用，故无跑飞账单；模型外发属 S3 之后。**不得据此取消模型网关/预算 HOLD**。
78. 部分适用 —— 有 ADR-0002 迁移与恢复条款、`backup(newPath)` 原语、FR-1000 项目包方向；但**无书面且年度演练的灾备计划**，本候选未新增。
79. 不适用 —— 单机本地产品，无区域承诺。
80. 部分适用 —— 引擎侧有结构化协议帧与固定错误码（`coordinator.py` 协议层）、请求 id 与 origin 绑定；**无集中式可检索日志平台**（无服务器）。缺口：3am 检索能力依赖本机 stdout。
81. 部分适用 —— 无错误聚合平台；有固定错误码目录（`packages/contracts/v2/errors.json` 26 码）天然可分组。缺口：渲染端白名单缺 16 码（D-7），分组视图不完整。
82. 部分适用 —— 产品唯一正式能力是 health（ADR-0002「当前产品正式能力仍仅 health」）；无外部探活。缺口：无第三方 uptime 监控。
83. 不适用 —— 无 7×24 值班体系。
84. 不适用 —— 无在线服务指标面板；仅有运行期日志。
85. 部分适用 —— 单请求可追踪：`requestId`/`engineSessionId`/`hostClientId`、job marker 与参数 hash 串联"一次请求经过的每个服务"（本候选只有一进程一引擎）；缺口：无跨服务 tracing。
86. 不适用（组织角色）—— 无值班轮转；**不消解本轮对代码、模型声明与因果调试的实际责任**。
87. 部分适用 —— 有 runbook 性质文档（AGENTS.md、`docs/reviews/T02/status.md`、ADR-0001/0002/0003、处置表与首败记录）；缺口：未覆盖"队列深度临界"式运维术语体系。
88. 适用且通过 —— 保留首败而非覆盖是本项目明确纪律：status.md 与 disposition.md 逐条保留 0e7 TIMEOUT、O027 三 FAIL、093 的 13PASS/1FAIL/2skip/2NOTRUN、text001、R03 ZPass/MMFail、O022 被拒 probe、CI36 取消与 79F；本轮亦未覆盖任何历史失败。
89. 不适用 —— 未公开发布，无状态页。
90. 适用且通过 —— 断言真实需求与错误边界而非数量：例如 `packages/engine/tests/test_mainline_manual_input_rejection.py` 的完整 Read 相等/Diff 0/确认 0 断言、`test_mainline_postwrite_*.py` 的分页与预付边界；PRD 附录 G 固定基线（G-base）作为"知道逻辑应该是什么"的外部锚点。
91. 适用且通过（按第三方依赖改写）—— 无外部 API；但**唯一的第三方深度依赖 rdflib 被本地补丁化**，其自带回归（PROVENANCE：newCases 172 + inherited 158，边界 4299/4300/4301、en-001/de-CH-1901）并留有 `reviewFindingDisposition`（初稿 167 绿漏掉空 lang，被复核发现后补正为 5 例）。缺口：应用套件未在该供应商轮运行（`applicationSuiteNotRun: true`）。
92. 适用（按本产品关键流改写）—— 无 signup/checkout；对应关键流是"本体事实 CRUD → 预览 Diff → 确认提交"，由 `tests/e2e/t02-fr200-fr201.spec.ts`（1748 行）真实驱动 O042 的 6 例全绿。
93. 部分适用 —— 容量口径 Q5/D2 未定，**独立 HOLD 保留**；本地全量 check 有规模证据（TS 1892、Py 3719），但无压力/并发负载测试证据。
94. 适用且通过 —— 固定样例与内置示例（G-base、`tests/fixtures/t02-manual-fact-id.json`、内置示例包带 manifest SHA256）均为合成/固定数据，不含真实业务数据。
95. 适用且通过 —— 本候选新增 6 个回归模块（`test_mainline_dispatch/language_input_rejection/manual_input_rejection/postwrite_admission/postwrite_rows_budget/postwrite_text_budget/read_work_budget`），修复 bug 41 不带回 bug 12 由模块化回归承担。
96. 不适用/保留 HOLD —— 低端设备与参考设备验证未做，**独立 HOLD 保留**；本候选无低端硬件实测。
97. 部分适用 —— 语义化与 ARIA 已用：`OwnershipConflictDetailView.ts` 用 `dl/ol`+`aria-label`，`OntologyMainlinePage.tsx` 用 `role="alert"`/`role="status"`。缺口：无正式无障碍审计与合规报告。
98. 不适用 —— 无订阅计费。
99. 不适用 —— 无扣款失败重试与催缴。
100. 不适用 —— 无发票。
101. 不适用 —— 无销售税/VAT 逻辑。
102. 不适用 —— 无退款/贷项。
103. 不适用 —— 无用量计费。
104. 不适用 —— 无年度合同。
105. 不适用 —— 无收入报表。
106. 不适用 —— 无 webhook 出站。
107. 不适用 —— 无 webhook 重试；缺省不适用。
108. 适用且通过 —— 契约显式版本化：`schema.json` 的 `draftSaveVersion/readVersion/detailReadVersion/ownershipDetailVersion`、契约 `registry.json` 登记方法集合、`packages/contracts/src/v2.ts` 与 `contract_v2.py` 双端一致；新增方法同步登记（`registry.json` 增 `project.ownership.detail`）。
109. 不适用 —— 无对外 API key。
110. 部分适用 —— 无对外 API 限流；引擎侧有 admission 限流（`RESOURCE_LIMIT`、游标记录数、保留字节 128 MiB、对象 1 Mi）。缺口：未做"真实整合不被误挡"的体验证据。
111. 适用且通过（第三方改版风险）—— 唯一被改写的第三方依赖 rdflib 采用"固定版本 + 透明本地补丁 + 来源证明 + 保留上游原件 + 可复现 repack（`scripts/repack-rdflib-input-types.py`）"策略，且 `PROVENANCE.json` 记录 `officialUpstreamUnchanged: false` 与 `transparentLocalVersion: true`——即上游改版不会静默进入。缺口：本地分叉增加后续升级成本（见 135/136）。
112. 不适用 —— 无 OAuth。
113. 不适用 —— 无对外集成沙盘；开发态真实 GUI 即内部验收面。
114. 不适用（模型未接入）—— 无模型调用面；AGENTS 规定 S3 前唯一网关在主进程、Python 引擎不持有密钥。**不得据此取消模型外发 HOLD**。
115. 不适用（同上）—— 无 prompts 出网。
116. 不适用（同上）—— 无模型账单。
117. 部分适用 —— 无模型评估；有**能力基线式**固定验收（附录 G 的 G-base/G-map-empty/G-behavior 与候选自身的固定用例集），可作为将来模型接入的对照底座。缺口：模型更新漂移检测未存在。
118. 不适用（同上）—— 无模型供应商。
119. 不适用（同上）—— 无模型生命周期管理；未来需另决。
120. 不适用（同上）—— 无 prompt/输出日志留存。
121. 适用且通过 —— 人在环路是本候选硬设计：预览 → 完整 Diff → 显式确认按钮才提交（`mainline-session.ts` 的 `confirm()` 注释"Called only by the explicit human confirmation button after displaying all rows"；`packages/engine/src/ontolearn_engine/project/mainline.py` 无自动确认路径）；PRD FR-204/FR-804 要求版本化 Diff + 原子提交 + 撤销。
122. 不适用 —— 本地应用无"酒店 WiFi"加载面；无远程资源依赖。
123. 适用且部分通过 —— 有明确空/读/错三态：读取中（`ownershipDetail.status === 'reading'` → "正在读取冲突定位…"）、不可用（"冲突详情暂不可用…"）、错误（`role="alert"`）；缺口：并非每个屏幕都有空态（本候选只覆盖本体构建页）。
124. 适用且通过 —— 错误文案可执行且区分场景：`OntologyMainlinePage.tsx` 对 `OWNERSHIP_CONFLICT` 给专门解释并保留输入；表单级错误码有中文映射（FACT_NOT_FOUND / MANAGED_FACT_REQUIRES_OWNER / AMBIGUOUS_FACT_SUPPORT 等）。
125. 适用且通过 —— 失败保留已输入内容（界面明写"已输入内容保留"）；`OntologyMainlinePage.tsx` 的围栏（`factLifetime` + `sequence`）在失败/失效时也不清空表单。
126. 不适用 —— 不发邮件。
127. 不适用 —— 无推送通知。
128. 适用但未实测（独立 HOLD）—— 有"撤销一次 ChangeSet"的存储语义（ADR-0002）与快照（FR-004），但 **Undo GUI 未实测，保留 HOLD**；`OwnershipConflictDetailView` 也不是 Undo。
129. 部分适用 —— 语义 HTML 与 `aria-label`/`role` 已用（见 97）；焦点管理与完整键盘导航未做审计。
130. 部分适用 —— 无 i18n 框架，UI 文案硬编码中文；但**数据层 Unicode 正确性被本轮真实缺陷覆盖**（cp1252，26/25/6 相关）；日期/数字按 locale 格式化未存在（无日期业务）。
131. 不适用 —— 桌面应用无浏览器历史；但等价诉求"上下文过期须显式失效"已实现（`sourceIdentity` 绑定 + `STALE_CONTEXT` + `discardPreview`）。
132. 部分适用 —— 注释密度高且解释非显然不变量（预算、持有、围栏）；但核心文件规模偏大（2993/1887/1206/1748，见 138）。
133. 适用且通过 —— 变更门禁即本流程：双模型独立审查 + 逐条处置 + 冻结候选 + 指定双审；本轮 R06 即该机制的一次执行。
134. 适用且通过 —— 并行开发线各自独立 worktree + feature 分支 + base SHA（`git worktree list` 实证 80+ worktree），禁止多 agent 同 checkout 切分支。
135. 部分适用 —— 依赖锁定到精确版本，但**无月度升级节奏**；rdflib 为本地分叉，升级需重做补丁与回归（见 111/136）。
136. 不适用（无外部服务）—— 本地桌面应用不依赖服务端框架停服；但 Electron/React/Python 的安全补丁策略未成文。
137. 适用且有意不做 —— 历史 wheel（fr201.1/.2/.3 + upstream）与旧证据按审计留存保留（R05-09/M-02 处置明确不删审计件）；残留"死代码"判定需逐项确认，不能按体量直接删。
138. 适用且仅信息级 —— 实测 `job_store.py 2993`、`storage.py 1887`、`mainline.py 1206`、`t02-fr200-fr201.spec.ts 1748`；按既有处置（M-07/R05-13）不据 LOC 推正确性，也不新增重构。
139. 适用且通过 —— ADR-0001（桌面框架）、ADR-0002（事务源真相）、ADR-0003（常驻协调器与作业）均记录决定、理由与保留限制；M0 更新计划归档在 `docs/iterations/I01/inputs/`。
140. 适用且通过 —— `README.md` 给出 clone/switch/npm ci/uv sync/npm run dev 与"检查本地引擎"验证路径，并明确标注"当前为 M0 开发骨架、六模块业务/项目保存/模型调用尚未实现"——与实际状态一致，未夸大。
141. 适用且通过 —— 交接材料完整：PRD V0.6、ADR×3、M0 计划归档、`docs/reviews/T02/status.md`（含快照分节与未关闭边界）、round-04/05 处置与独立核验、本轮 R06。
142. 不适用 —— 无运营后台；无远程运维面。
143. 不适用 —— 无客户成功流程。
144. 部分适用 —— 未发布，故无面向客户的 changelog；内部变更以提交前缀（`feat:`/`fix:`/`docs:`/`test:`/`chore:`）与处置表可追溯。缺口：无产品级变更记录文件。
145. 部分适用 —— 未发布，无对外条款/隐私政策；仓库内 `licenses/NOTICE` 已记录第三方许可与本地补丁事实。**不得据此取消法律/wholeApp/_distutils HOLD**。
146. 不适用（尚未发布）—— 仓库与远端名为 `NOmoreJoke/OntoLearn-Studio`（个人身份），对外命名需在发布前决策；本轮不代为命名。
147. 部分适用 —— 工程侧抗单点：双模型审查 + 多 worktree 并行 + 契约单一维护者 + 逐意见处置；**但真实 bus factor 仍受限于人力与单一知识持有人**，组织层面本轮无法确认。
148. 适用（以独立审查流程承担）—— 本轮 R06 即"逐行读 AI 产物再放行"的一次执行；O042 的独立核验（58 附件逐个解码、57 事务逐笔差分、43 拒绝逐件重算）为该实践的实例。
149. 适用且部分通过 —— 数据模型先于第二客户设计：`packages/contracts/v2/schema.json` 141 定义、`registry.json`、`ADR-0002` 分层与不可变快照；缺口：尚无第二客户/多领域压力检验。
150. 适用（因果调试责任，不因"组织角色"而消解）—— 本候选确有"修一处引另一处"的具体形态：`_WriteAdmission` 为修分页预算而引入预付与持有模型、`query_presentation.py` 为修终末编码而引入 `_RowsPrepaid` 二次付费、831813c6 为修 cp1252 而只改测试编码；本轮逐条追到调用点并确认无副作用扩散（D-12、AST 复核）。缺口：预付/持有模型的**跨路径回归**仍依赖既有套件，未新增针对性 mutation 证明。
151. 部分适用（组织角色）—— 无服务器与云账单，故无生产运维面；实际职责落在 CI 门禁与打包产物（`package:dir`）上。**不消解本轮对 CI 失败与打包证据的责任判定**。
152. 不适用（组织角色）—— 无支付停止的 3am 页面；本地应用无值班。
153. 部分适用（组织角色）—— 无服务端框架停服；真实可行动作是本地分叉 rdflib 的补丁维护（见 111）。**不消解本轮对依赖可复现性的核验责任**。
154. 不适用 —— 无患者数据流动可审计。
155. 适用且通过 —— "测试 AI 声称测过的"：本轮不采信任何报告自述，改为自行复算 AST 等价、自行 shasum 五文件哈希、自行读回 CI/GUI 原件；O042 亦由独立核验逐笔重算而非沿用汇总。
156. 适用且部分通过 —— 迁移在事务写锁内、可回滚、未来格式拒绝（ADR-0002）；**但真实旧库迁移未在本候选端到端实测**，且旧超限库恢复属独立 HOLD。
157. 适用且通过 —— "说不"被制度化：多个意见被明确判为"不采/部分采纳/OPEN 非阻断延期"而非强行收口（如 Z-02 撤回、M-02 不删审计件、R05-04 不采计数差因果）；本轮亦未把 D-1～D-11 降级为信息项。
158. 部分适用 —— 单机本地即"一次为所有客户"的最强形态之一（无跨租户偏差）；但**跨平台（Windows/macOS 15/Win11）与参考设备未覆盖**，且当前 Windows 门禁未绿（D-1）。
159. 适用（因果调试责任，不因"组织角色"而消解）—— 本轮对 cp1252 首败的定位是独立完成的（读 `FIRST-WINDOWS-FACTS.json` 原始栈 + 复核 `encoding="utf-8"` AST 等价），未依赖其他模型的"AI 写的代码"无法调试这一前提。
160. 适用且通过 —— 记忆在仓：ADR 记录决定与理由、处置表记录每条意见及其限制、状态文档分节保留历史快照、PROVENANCE 记录制品来源与已知缺口、AGENTS 记录现行政策。

---

## 9. Top 10（按严重程度；不省略其他阻断）

1. **【门禁级·阻断合并】当前 head `831813c6` 无任何远端 CI 证据，唯一针对 Windows cp1252 首败的修复从未在 Windows 上运行。** 远端只到 `934bd14f`，其 Windows job 失败（O040 `FINAL-CI-FACTS.json`：conclusion failure / `allWindowsAcceptanceProved false`；`FIRST-WINDOWS-FACTS.json`：cp1252 `UnicodeEncodeError`，1 FAIL/980 PASS/3 SKIP/258.55s）。旧 CI36 的取消与 79F 未被关闭。
2. **【门禁级·阻断合并】仓内唯一状态来源与远端事实相反。** `git ls-remote` 显示分支已在 `934bd14f`、`develop` 在 `583c05c7`，而 `docs/reviews/T02/status.md:3`、`docs/m0-checklist.md:41` 仍写"尚未推送/无新 CI"；`round-05/artifact-manifest.json` 的 1355/71/29/`2d9b113b` 对当前 head 已过期。
3. **【中·产品】`definitions[].value.triples[]` 词法不在预览期受控拒绝，提交期以未分类 `ValueError` 逃逸并 HOLD 整个引擎会话**（`domain_changesets.py:448-465` 只覆盖 manual/edits；`storage.py:726,1110-1135`；`mainline.py:1187-1200,659-663`）。预览显示干净 Diff、确认才失败。
4. **【中·产品】裸 ownership 冲突仍无定位，且 `Conflict` 码表无 `ownership` 键**（`storage.py:57-64,1230`；`job_store.py` `_ownership_header` → `INVALID_STATE`）→ 界面只能显示"冲突详情暂不可用"，且错误码落为 `INTERNAL_ERROR`。
5. **【中·产品】"首个阻断行"无确定序。** `storage.py:1212-1215` 与 `:1147-1157` 的 SQL 均无 `ORDER BY`，而 witness 文档字符串与 UI 标题都声称"首个/前两条"。
6. **【中·产品】已发布 vendored wheel 仍有未类型化 EOF 访问**（`rdflib/plugins/parsers/notation3.py:931`、`:1609`，本人从已发布 wheel 解出定位），经 `rdf_snapshot.py:44-45` 变成普通 `ValueError` 后逃逸为同一 HOLD 后果。
7. **【低-中·产品/UX】渲染端错误码白名单缺 16 个契约码**（契约 26 / UI 17 / 交集 10），这 16 码在 UI 退化为通用文案。
8. **【中·覆盖】附录 D/E/G 无条款映射**；尤其附录 D.2 第 994–1000 行正是 FR-200 编辑对象对应的失效联动义务，本候选无证据。
9. **【低·测试】两个 TS 单测仍依赖 PATH `python`**（`t01-mainline-contract.test.ts:656`、`t01-ontology-metadata-contract.test.ts:168`），无 Python 的机器上 ENOENT（O035 首败保留）。
10. **【信息·记录】Ruff 369/379/380/386 为四次不同真实运行，380 与 386 仓内无记录**；4299/4300 应用层无断言；`PROVENANCE.json` 的 `applicationSuiteNotRun: true` 未被任何文档承接。

**其余未列入 Top10 但仍开放且不降级**：D-3～D-11 各条本身、§7 全部独立 HOLD、R05-09/M-07/M-01 的处置缺口（Z-02 整文档 262144/16 MiB 无独立行、M-03 mutation 限定未写入、P-7 有效 pytest 选项已变未写入）。

---

## 10. 整候选结论

**结论：无法完成验证（Conditional, verification-incomplete）——不通过整候选合并放行；本候选的实现与本地验收在 macOS 上通过，但存在明确的推送前/合并前技术阻断，且当前 head 的关键平台验收缺证。**

分开说明：

- **本地实现与本地验收：通过（限于 macOS dev 面）。** 831813c6 的六处编码修复经本人独立 AST 复算，确认剥离后与 `934bd14f` 完整 AST 严格相等，产品/依赖/CI/cap 零改动；O041 本地全检自然 0（TS 1892、Py 3719/50 SKIP、Ruff 386）；O042 在 head 831813c6 上真实六例 GUI 全绿（6 PASS/0 skip/0 retry/0 flaky、runner 自然 0），旧 094 包 912 成员与 rootmode 前后/当前全等。**这些是他人已执行并留存的运行原件，不是本轮新执行。**
- **推送前技术阻断：无（就源码本身）。** 本轮未发现需要在 push 之前必须修改代码的新增缺陷；D-1～D-11 均不需要改代码才能推送（除第 2 条的文档失真需在状态文件层面更正，且那属于流程/文档归口，不由本轮单方决定）。
- **合并前条件（必须满足，均非本轮可自行关闭）**：
  1. 在**同一候选 `831813c6`** 上取得远端 CI 的**完整 Windows 绿灯**（不得以 `934bd14f` 的 macOS/Quality 绿替代，也不得以本机 macOS 绿替代）；并对旧 CI36 的 79F 与取消做出"全部定因或明确残留清单"的处置结论。
  2. 按现行规则更新 `docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 的**当前时点**（远端已推送到 `934bd14f`、run 40171564866 的真实结论、当前 head 无 CI），并使 `round-05/artifact-manifest.json` 一类清单不再以 aff386f6 数值冒充当前候选。
  3. 对 D-3、D-4、D-5、D-6、D-7、D-8 给出**明确处置**（修复或正式延期到具名负责人与时点）；其中 D-3/D-6 属"用户可触发会话 HOLD"的可用性事件，建议在合并前给出可执行结论。
  4. 附录 D（尤其 D.2 失效联动）补映射或明确列入未验证范围，避免"类层级/domain/range CRUD 已验"被读成"这些变更的下游失效已验"。
- **推后 CI / 合并前条件（不属本轮判定）**：签名、公证、wholeApp 法律与 `_distutils`、全平台/参考设备/macOS 15/Win11、容量 Q5/D2 与旧超限库恢复、损坏 SQLite 物理保护、unknown parser/N3/Store/坏快照、Undo GUI 与未实测 ownership 家族、未知退出码——全部保持 HOLD，本轮未抵消任何一项。
- **不因本报告增加任何 FR 或宣称 Goal/发布/M0 完成**：合并可用仍为 **2/17**（FR-401/402）。

**关于"新 8318 Windows 完整验收仍缺"如何影响结论**：该缺口本身**不是源码缺陷**（修复内容与父提交在 AST 上完全等价，语义上只把测试落盘显式为 UTF-8），也**不能**被虚构成"修复必然失败"或"修复必然成功"。它只意味着——在同候选的 Windows 完整验收拿到之前，**整候选不能被判为通过**；本报告据此给出"无法完成验证"而非"通过"或"不通过"，并把它列为第一合并前条件。同理，旧 CI36 的失败与取消**不因**本次修复而消失，也不因本次修复而被归因。

---

## 11. 本报告的未验与自限

1. 本轮**未运行**任何产品、测试、GUI、构建、打包、probe 或 SQL；所有运行数据来自既有原件。
2. O042 中 58 附件逐个解码、57 事务逐笔差分、43 拒绝逐件重算、104 采样/PID 表、main 606471 B 与 builtHTML 绑定、8 环境缺席等**逐笔结论采信原件内独立核验报告**，本轮**未逐笔复算**；本人只复算了 report 字节/SHA、stats、gui-exit 与 GUI-ACTUAL-QUALIFICATION 的 head/tree。
3. **PR16 的 open/未合并状态未通过 API 核验**（本轮只核远端分支 SHA）→ 无法确认。
4. 人类 D8 选择 A 原件位于仓库外 `iteration-control/`，本轮**未直接打开**，相关约束按封存 prompt 转述执行。
5. `packages/engine/src/ontolearn_engine/invalidation-v2.json` 是否覆盖附录 D.2 首行的四类下游失效结果，本轮**未核** → 无法确认。
6. 另一方本轮报告**未读**；`round-01`～`round-03` 未跟踪历史目录**未读未改**。
7. 本方任务 ID 由操作者从正式 UI 读回后再登记；本报告不代填、不自造。

---

*本报告为 R06 原稿，事实修订只在同原任务、原代码未变时另封每版本；不改写历史原件，不通过诱导获取一致。*
