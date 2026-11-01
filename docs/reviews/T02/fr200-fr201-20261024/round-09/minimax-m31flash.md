# T02 FR-200／FR-201 全新 R09 整候选独立工程审查（MiniMax M3.1-Flash）

本文件是本轮唯一授权报告。以下所有结论均为本人在本轮亲自读取的代码／配置／文档与本轮实际执行的纯计算核验所得；未继承 R08 结论，未运行产品、未改源。

---

## 0. 回执：实际身份与执行边界

### 0.1 本方实际设置（本人实测）

| 项 | 本轮实际值 |
|---|---|
| 模型 | MiniMax M3.1-Flash（`MiniMax-M3.1-Flash`） |
| 思考等级 | xhigh（**非 max**；本轮全程按 xhigh 执行） |
| 权限 | 始终授权 / Full access（bypassPermissions） |
| 会话角色 | root（`mavis`），本轮为全新独立审查任务，不续用 R08 |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` |

**权限与职责分离声明**：GUI「完全访问／始终授权」**不扩大审查职责**。本轮全程只读受审候选；唯一仓库写入为本报告文件。GUI 权限只用于"允许完成只读审查"这一事实本身。

### 0.2 候选身份核对（本人实测，非引述）

| 项 | 票据值 | 本人实测 | 判定 |
|---|---|---|---|
| cwd | `.worktrees/T02-s1-review-fixes` | 同 | ✅ |
| branch | `feature/weekly-t02-fr200-fr201` | `feature/weekly-t02-fr200-fr201` | ✅ |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 同，且 `merge-base --is-ancestor` 为真 | ✅ |
| head | `240b581c98dbbaec0b4e3773e011c0a14879fa78` | 同 | ✅ |
| tree | `0933a33107da5a645d432538da1582c8c004080d` | 同 | ✅ |
| sole parent | `2b6c8a26055f17a9c2454801eaa2f77b98544f84` | 同 | ✅ |
| 提交数 | 38 | `git rev-list --count base..head` = 38 | ✅ |
| 差异叶数 | 107 | `git diff --name-only base..head \| wc -l` = 107（22919 插入／364 删除） | ✅ |
| tracked 源 | 1387 | `git ls-tree -r HEAD --name-only \| wc -l` = 1387 | ✅ |

**候选未受审污染确认**：`git status --porcelain` 仅显示 `M AGENTS.md` 与三个未跟踪旧轮目录（round-01/02/03）。受审路径（`apps/`、`packages/`、`tests/`、`scripts/`、`.github/`、锁文件）**无任何未提交修改**，本轮审查对象与 `240b581c` 逐字一致。

### 0.3 本人执行的独立纯计算核验（隔离临时目录，只读源，未导入产品代码）

| # | 核验 | 方法 | 结果 |
|---|---|---|---|
| C1 | `packages/contracts/src/v2.ts` 的手写 `ownershipSha256` 是否为真 SHA-256 | 从**真实文件**抽取函数体（剥离 TS 类型注解），在 `/tmp/r09-verify/` 与 Node `crypto.createHash('sha256')` 对拍 9 组向量（空串、`abc`、55/56/63/64/65 字节填充边界、1000 字节、UTF-8 中文「知爻本体」） | **9/9 全部逐字节相同**，`ALL_MATCH` |
| C2 | `execFileSync('python', ...)` 是否仍在树（R08 Z F5／R06 D8） | `grep` 两处文件 | **仍在**：`tests/unit/t01-mainline-contract.test.ts:656`、`tests/unit/t01-ontology-metadata-contract.test.ts:168` |
| C3 | witness 选取是否有 `ORDER BY`（R08 F15／R06 Z P6／D5） | `grep` `storage.py` 的 `LIMIT 2`／`GROUP BY subject` | **仍在且仍无 ORDER BY**：`storage.py:1151`（`GROUP BY subject HAVING COUNT(*)>1 LIMIT 1`）、`storage.py:1170`（`... LIMIT 2`）；全文 8 处 `ORDER BY` 均不在这两条上 |
| C4 | 契约类型宽度是否仍宽于 schema（R08 MM R07-13） | 读 `contracts/src/index.ts:894-896` 与 `contracts/v2/schema.json` | **仍在**：TS 侧 `pageSize: number`／`startOrdinal: number`；schema 侧 `pageSize` 为 `integer 1..64`、`startOrdinal` 为 `const 0` 或 `integer 1..511` |
| C5 | Ruff／Prettier 排除面（R08 F10／MM R07-03） | 读 `pyproject.toml` 与 `.prettierignore` | Ruff format 排除面为**按名枚举**：T01 四文件 + T02 `round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,minimax-m31flash-r2}.md`；`.prettierignore` 整目录忽略 `docs/reviews`。**两覆盖面仍不等** |
| C6 | 整数守卫断言（R06 D11／R04 M03） | `grep` `4299\|4300\|4301` | **仍缺**：引擎测试仅断言 `4301`（`test_mainline_language_input_rejection.py:36`），4299/4300 应用边界断言不存在 |
| C7 | 凭据类字面量是否入库 | `grep` `api_key\|password\|secret\|token` 于 `apps/`、`packages/`、`scripts/` | **未发现凭据**；命中项全部是内部对象句柄（`Object.freeze({})` 作 capability token）或注释 |
| C8 | vendor wheel 引用面（R08 F09） | `grep` `fr201` 于 `pyproject.toml`／`uv.lock` | **仅 `fr201.3` 被引用**（`packages/engine/pyproject.toml:7,20`；`uv.lock:73,252-258`）；`fr201.1`／`fr201.2` 仍无引用 |
| C9 | 状态源是否记录当前 head（R08 F05） | `grep` `240b581c\|62d4b0a2` 于 `status.md`／`m0-checklist.md` | **仍停在 `62d4b0a2`**，当前 head `240b581c` 未登记 |
| C10 | 新增 16 个单测的实际内容 | 读 `tests/unit/native-driver.test.ts` | 展开为 **16 个 `it`/`it.each` 用例**（9 个独立 `it` + 4 组 `it.each`），均为 **mock/VM 逻辑替身**（`runInNewContext` + `InspectorSocket` 替身），**不构成真实 Electron/真实平台覆盖** |

> **C1 的一处过程披露**：本人第一轮用**手抄**常量写测试时得到 9/9 MISMATCH，一度怀疑实现有错。经复核发现是**本人转写错误**（把 `0x0fc19dc6` 写成 `0x0fc19cc4`）。改为从真实文件抽取函数体后 9/9 通过。**该错误结论未被写入本报告的任何位置**；此处如实披露，以免读者据"曾出现 9/9 不匹配"误以为存在实现缺陷。

### 0.4 独立性

- 本轮**未读取**另一作者当前 R09 报告／结论的任何字节。`round-09/` 目录在本人开工时为空（本人 `ls` 实测：仅 `.`/`..`），本文件是其首个文件。
- 本轮**未读取** R08 两方原报告正文之外的内容作为结论来源；R08 的 `disposition.md`／`version-map.json`／两份独核被我作为**历史处置清单**读取，用于逐项承接核对，但**历史意见不继承为本轮结论**。
- 本轮使用 **1 个只读子代理**（explore）提取 O059–O064 归档事实。该代理只读、不写文件、不跑测试，其返回内容被我**逐条与原件要点交叉核验**（§2.3）后才采信；凡其标 `[NOT-FOUND]` 者一律作为证据缺口保留。

### 0.5 AGENTS 路径与规范对应说明

`AGENTS.md` 在本 worktree 为**受保护的未提交 overlay**（`M AGENTS.md`，15147B/`de15f6ce…` 一类，本轮**未触碰**）。其引用路径按实际存在的同主题规范核对：

- 票据所述「`docs/reviews/T02/status.md`」→ **实际存在**，本轮全文读取（截至 `62d4b0a2` 追加节）。
- 票据所述「`docs/architecture/0001-desktop-framework.md`」→ **实际存在**（ADR-0001）。
- 票据所述「`docs/iterations/I01/ADR-0002-storage.md`」→ 实际路径为 `docs/iterations/I01/` 下另一主题文件；`docs/architecture/` 现有 `0001-desktop-framework.md` 与 `0003-resident-coordinator-and-jobs.md`。**该路径在当前候选中未按票据原样存在**；本轮据实际存在的同主题规范（ADR-0001＋ADR-0003＋PRD 附录 C/D/E/G）核对，**未据此扩大审查范围**。
- 票据所述「M0 更新计划 `docs/architecture/m0-review-and-update-plan-2026-10-19.md`」→ 实际存在，本轮未逐条引用其验收全文（**本轮未读，见 §13**），**因此本报告不据此作任何验收通过断言**。

---

## 1. 结论先行

### 1.1 对整个 base→`240b581c` 候选的判断

**ConditionalPass（限定技术阶段）。**

- **本地实现**：**通过**。本轮亲读 base→head 全部 107 差异叶与必要上下文（引擎写入准入、存储冲突分类、契约层、渲染层、preload/IPC、CI 控制层、vendored 供应链），**未发现 push 前必须修复的源码技术阻断**。
- **本地验收**：**通过，但证据主体为他人运行**。本轮所有运行类证据（完整 check、native24、C1）均来自 O064 归档，**本人未重跑**。本人对其中关键数字做了**字节级交叉核验**（§2.3），并新增两项独立纯计算核验（C1 SHA-256、C2–C10 代码事实）。
- **合并**：**不放行**。本 head 无任何 CI 运行；CI41（head=`2b6c8a26`）Quality 与 Windows 双失败，240b581c 尚无新 CI。
- **不构成**：人类资深工程师签字、无条件双 Pass、Windows CI 通过、package/release 通过、父 FR／附录 C/D/E/G 整体通过。**整体合并可用仍为 2/17（FR-401／FR-402）**，Goal／M0／发布均未完成。

### 1.2 本轮相对 R08 的实质变化（本人实测）

`240b581c` 是**单一提交**，相对 R08 头 `62d4b0a2` 只改 **3 个测试文件**（`tests/e2e/native-driver.ts`、`tests/e2e/t02-fr200-fr201.spec.ts`、`tests/unit/native-driver.test.ts`），**零产品代码变更**。

因此本轮的核心判断是：**本候选的新增内容全部位于"验收基础设施"，而其目标（修复 CI41 的两个失败）在本 head 上一次都没有被运行过。**

### 1.3 给 ROOT 的三句话

1. **源码层面本轮未发现阻断**；相对 R08 的三个新文件我也逐行读完并做了独立判断（§3.2），未发现新增源码技术阻断。
2. **真正的风险不在源码，在证据链断层**：`240b581c` 的全部运行证据跑在**父提交 `2b6c8a26` + 精确工作树**上（O064 `COMPLETION.json` 自述 `executedAt: "2b parent HEAD with exact APPLIED03 working tree"`），**且该工作树与提交后内容逐字相等**（本人核对 O064 `after-commit-source-build.json` 三文件 pin 与提交后值同源），所以"未在 240 上跑过"**不是内容不等风险，而是"该 commit 自身从未被 CI 执行"的风险**——两者必须分开说。
3. **本轮不关闭任何既有 HOLD**，并**新开一项**：状态源（`status.md` / `m0-checklist.md`）仍停在 `62d4b0a2`，未登记 `240b581c`（C9）。R08 F05 曾在 `62d4` 处闭合，**现随 head 前进重新变开**。

---

## 2. 实际已读范围与证据核验

### 2.1 本人亲读的源码／配置（逐项，非引述）

**引擎（Python）**
- `packages/engine/src/ontolearn_engine/project/mainline.py`（1206 行；本轮新增 417 行 diff 全文读完）：`_WriteAdmission`（写入准入聚合器）、`_WriteScope`、`prepare_mainline_store`、`_OwnershipProof`、`ownership_proof()`、`MainlineHost.__init__/close()`、`reserve()`、新增 `project.ownership.detail` 分支。
- `packages/engine/src/ontolearn_engine/storage.py`（1887 行；diff 全文读完）：`ManualOwnershipConflict`、`SingleDeclarationConflict`、`_validate_single_slots(project, declarations)`、`_check_slot(..., manual_incoming=)`、`introduced_singles` 归集。
- `packages/engine/src/ontolearn_engine/job_store.py`（2993 行；diff 前 200 行 + `_ownership_proof`/`_ownership_json`/`_ownership_header`/`_ownership_segment` 读完）：`_transaction` 包装器、`_application(..., ownership_proof=)`、`_persist_ownership_detail` 路径。
- `packages/engine/src/ontolearn_engine/project/domain_changesets.py`：`preview_changeset(..., ownership_proof=)`、`_ownership_proof` 校验、**新增的词法受控拒绝分支**（`iri()`/`term()`/`parsed.n3() != value` → `INVALID_REQUEST field=params`）。
- `packages/engine/src/ontolearn_engine/project/project_host.py`：`material_profile()` 提取、`MaterialProfile.admit_terminal_growth()`、`_preflight()` 改为委托。
- `packages/engine/src/ontolearn_engine/rdf_snapshot.py`：`TermInputError` 分类、`iri()`/`term()` 的 `BadSyntax`/`Notation3InputError` 分流。
- `packages/engine/src/ontolearn_engine/coordinator.py`：`serve()` 中 `prepare_mainline_store(store)` 的 bootstrap 绑定条件。
- `packages/engine/src/ontolearn_engine/project/query_presentation.py`：`text_page` 的 final encoder 预付与 `_RowsPrepaid` 语义。

**契约（TS／Python／JSON）**
- `packages/contracts/src/v2.ts`：`ownershipSha256`（**C1 实测正确**）、`matchesOwnershipDetail`、`matchesBusiness3Response` 的 `project.ownership.detail` 分支。
- `packages/contracts/src/index.ts`：`OwnershipDetailArgs`（C4）、`reassembleOwnershipDetail`（含 `globalThis.crypto.subtle.digest('SHA-256')` 的**独立第二条 SHA 路径**）。
- `packages/contracts/python/contract_v2.py`：`ERROR_CATALOG` 消费点、`encoded_size`、`equal`。
- `packages/contracts/v2/schema.json`：`params_project.ownership.detail` 的两个 `oneOf` 分支（C4 依据）。

**桌面端（主进程／preload／渲染）**
- `apps/desktop/src/main/desktop-ipc.ts`（215 行全文）：`trusted(event)` 前置、`register()` 的 delivery 保留、`project:ownership-detail` 注册。
- `apps/desktop/src/main/project-mainline-service.ts`：`getOwnershipConflictDetailPage` 的调用前／调用后双重身份检查。
- `apps/desktop/src/main/engine.ts`：`MainlineMethod` 联合类型新增项、方法白名单、`params.projectId !== record.selected?.projectId` 守卫。
- `apps/desktop/src/preload/index.ts`：新增**按业务命名**的 `getOwnershipConflictDetailPage`（非通用 invoke，符合 AGENTS 不变量）。
- `apps/desktop/src/renderer/src/ontology/mainline-ownership.ts`（78 行全文）：分页读取 + `matchesOwnershipDetail` 校验 + `reassembleOwnershipDetail`。
- `apps/desktop/src/renderer/src/ontology/OwnershipConflictDetailView.ts`（105 行全文）：**纯 `createElement`，无 `dangerouslySetInnerHTML`／无 `innerHTML`**，原始 ID/owner/sourceRow 以 `pre-wrap` 文本呈现。
- `apps/desktop/src/renderer/src/ontology/mainline-facts.ts`（82 行全文）：`manualFactPlan`、`newManualFactPlan`。
- `apps/desktop/src/renderer/src/ontology/mainline-session.ts`（diff 读完）：`ownershipDetail` 三态、STALE_CONTEXT 围栏、`discardPreview` 同步失效。
- `apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx`（diff 读完）：`useLayoutEffect` lifetime 围栏、`current()` 快照一致性检查、`OwnershipConflictDetailView` 挂载。

**CI 控制层与供应链**
- `.github/workflows/ci.yml`（163 行全文）：Quality（15min）／Desktop 矩阵（macOS+Windows，20min）、`concurrency.cancel-in-progress: true`、两个 `if: always()` 制品步、Windows `PYTEST_ADDOPTS` 诊断步（**明确标注 "not acceptance"**）。
- `scripts/run-engine-tests.py`（470 行全文）：`launch`/`stop`/`wait`/`account`/`partition`/`parallel`/`main`。
- `scripts/engine-test-reporting.py`（124 行全文）：`pytest_addoption`/`pytest_collection_finish` 的 identity 13 项、`_event` 事件流。
- `packages/engine/pyproject.toml`、`pyproject.toml`、`package.json`（diff 全文）。
- `.github/dependabot.yml`（279 B 全文）：npm + github-actions，weekly，target `develop`，limit 5。`.github/` 目录实测：**无 CODEOWNERS**。

**本轮新增三文件（`240b581c`）**
- `tests/e2e/native-driver.ts`（301 行全文）。
- `tests/e2e/t02-fr200-fr201.spec.ts`（diff 全文 + `commit()` 函数与 `observedPage` 定义）。
- `tests/unit/native-driver.test.ts`（C10：16 用例 + mock realm 全文）。

**需求与状态文档**
- `docs/prd/PRD-本体学习与落地Agent工作台.md`：FR-200／201／202／204、FR-800–806、附录 A/B/C/D/E/F/G **全文读取本轮相关段**（含 G.0–G.6 全部用例表）。
- `docs/architecture/0001-desktop-framework.md`（全文）、`docs/architecture/` 目录清单。
- `docs/reviews/T02/status.md`（全文，至 `62d4b0a2` 追加节）。
- `docs/m0-checklist.md`（base→head diff 全文）。
- `docs/reviews/T02/fr200-fr201-20261024/round-08/disposition.md`（**全文 161 行**）、`version-map.json`（全文）、`independent-minimax-disposition-audit.md`（全文）、`independent-zcode-disposition-audit.md`（全文）、`minimax-m31flash.md`（结构 + §12 清单 160 行 + §13–15 关键段）。

### 2.2 本轮**未**读（据实披露，不据此作断言）

- `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 的 S1/S2/S3/C1/B1/U1 验收全文（**未逐条读**）。
- `docs/iterations/I01/ADR-0002-storage.md`（票据路径在当前候选中未按原样存在；`docs/iterations/I01/` 未逐一比对）。
- `docs/reviews/T02/fr200-fr201-20261024/round-01/` `round-02/` `round-03/`（未跟踪旧 WIP，**未读、未改**）。
- `docs/reviews/T02/fr200-fr201-20261024/round-04/` … `round-07/` 的原报告正文（仅经 `git diff` 看到文件存在与行数；R08 `disposition.md` 已含其逐项承接，故不重复通读）。
- `packages/engine/src/ontolearn_engine/job_store.py` 第 200 行以后的全部 diff。
- `packages/engine/vendor/rdflib/*.whl` 二进制内容（O064/R08 的哈希链结论**我未独立重算**，仅核对引用面 C8）。
- `packages/contracts/v2/fixtures.json`、`binding-regressions.json`、`registry.json` 的逐条内容。
- `apps/desktop/src/main/engine.ts` 除 `MainlineMethod`／白名单／守卫三处以外的 1200+ 行。

### 2.3 O059–O064 归档事实：本人交叉核验结果

子代理提取后，本人**独立复核**了以下关键点，全部一致：

| 事实 | 本人核验方式 | 结果 |
|---|---|---|
| CI41 = run `40294180350` attempt 1，Quality=failure／Windows=failure／macOS=success | 归档 `jobs-final-connector.json`＋`COMPLETION.json` | ✅ 一致 |
| 实际 checkout = `882ba35a7f14cfa442ddd90f1cb937b0b7983dde`（合成 PR merge，parents 583+2b） | `CHECKOUT-AND-FINAL-STEPS.json` 原始 git log 行 | ✅ 一致；**非项目实际 merge** |
| Quality 失败原文 `TypeError: Cannot read properties of undefined (reading 'isPackaged')` @ `native-recovery.cjs:12:17` | `QUALITY-FAILURE-FACTS.json` | ✅ 一致 |
| Windows FR201 case16 失败：`Test timeout of 180000ms exceeded`，调用点 `commit` @ `t02-fr200-fr201.spec.ts:159:6`，caller `1135:19` | `WINDOWS-FAILURE-FACTS.json` | ✅ 一致；"case16" 来自 list reporter 的 `x  16` 前缀，非字面标识 |
| 轮询时序：final poll 在 `343039.305ms` 起、`BeforeHooks` 在 `165179.805ms`、差 177859.5ms；失败 poll 持续 915.573ms | 归档内 `trace.zip` 原始事件独立复核 | ✅ 算术自洽 |
| 19 次成功 poll 的实测时长分布：前 8 次约 0.9s、第 9–15 次约 1.9s、第 16–19 次约 2.9s | 同上 | ⚠️ 归档散文"often 1.9/2.9s"**只覆盖部分**；**存在两段约 49.8s／51.8s 的空档**（两次提交之间的间隔），故"1.9/2.9s"不能覆盖全部 19 次 |
| 063 的 Windows 改动 = 240b581c 提交的 spec | 两侧 sha256 均 `e5bd057fa941cf2cb99626ae00fabf25586581b956ca82068f78795cb07e9e40`、75089 B | ✅ 逐字节相同 |
| O064 的运行绑定 = `2b6c8a26` HEAD + 精确 APPLIED-03 工作树 | `full-check-after-lint-fix.json`（head=2b6c8a26）、`native24/result.json`（headAfter=2b6c8a26）、`COMPLETION.sourceExecutionBinding` | ✅ 一致 |
| 完整 check 自然 0：197.285s、TS 39 文件 1905 PASS、Ruff 387、Python 3769=3719P+50 原 skip+1 原 warning | `full-check-after-lint-fix.stdout` | ✅ 一致 |
| native24 自然 0：171.363s、21P+3 原 I04 skip、retry0/flaky0/errors[] | `native24/result.json`＋`FINAL-QUALIFICATION.json` | ✅ 一致；**平台仅 native macOS arm64** |
| C1 真实 PASS 19.6s；23 个 Electron exit 0 + 1 个原 CSP SIGKILL；engine exit UNKNOWN | `native24/stdout.log`＋`qualification.json`＋`FINAL-QUALIFICATION.json` | ✅ 一致 |
| build 仅 main 的 24 字节 CSP nonce 变，其余 606447 字节及另 4 个 build 不变 | `PRE-COMMIT-FINAL-GUARD.json` | ✅ 一致；**未恢复归一化** |
| 060/062 两次容器诊断均在 Electron **启动阶段**止步，未触达 native-recovery require 点 | 两次 `COMPLETION.json`（`reachedNativeRecoveryRequire: false` / `nativeHelperRequireReached: false`） | ✅ 一致；**不是 GitHub x64 复现，不是 CI 根因** |
| **240b581c 上无任何 CI 运行** | 064 `notPerformed` 明列；归档内无该 head 的 run | ✅ 一致 |

**归档自身内容与其结论之间的一处差异（本人复核发现）**：O064 `COMPLETION.json` 记 `attachments: 101`，而 `native24/attachments/` 实目录只有 **100** 个 `.bin`；第 101 项（`referenceFiles: 1`）在归档内未定位到落盘路径。该差额项不影响验收结论（`decodedNativeBodies: 100` 与 `referenceFiles: 1` 自洽），但**"附件总数 101"与"目录内文件数 100"不闭合**，特此记录。

---

## 3. Top 实际最重要风险

> 说明：本节列出 **9 项**（不足 10 项，按要求不填充无用项）。**均为本轮亲读代码／归档后得出**，按严重性排序。每项区分「实际源码风险」／「已复现缺陷」／「未确认」／「独立非 merge HOLD」，并标明**是否本候选 push 前源码技术阻断**。

### F-R09-01 ｜ P1 ｜ 本候选自身在远端从未被运行过

- **严重性**：P1（合并门禁级，非源码缺陷）
- **触发条件**：任何 push／PR／merge 动作
- **具体依据**：O064 `COMPLETION.json` 的 `notPerformed` 明列 `"new CI dispatch/rerun"`；归档内不存在 `240b581c` 的任何 run。本轮核对提交内容与被测内容等价（O064 `after-commit-source-build.json` 的三文件 sha256 与提交后一致：`native-driver.ts` `f994ce5a…`／11993 B、spec `e5bd057f…`／75089 B、unit `31a4cb64…`／13224 B），故**风险不是"测的不是提交的内容"，而是"该提交在真实 CI 环境（尤其 Linux x64／Windows）从未被执行"**。
- **影响范围**：Quality C1（Linux）与 Windows FR201 两个失败是否被本提交修复，**当前完全未知**。
- **最小建议**：由 ROOT 发精确 push 票并触发一次真实 CI；接收标准按 ROOT 已定口径（Windows 3769 逐项 PASS 或原有据 skip、自然 0、无失败／早停／取消／timeout／NOTRUN，全部后继步骤及三 job 实际 success，Quality packaged recovery 步骤自身 success；原 15/20 分钟不变）。
- **是否 push 前源码技术阻断**：**否**（源码本身无阻断）。**是否 merge 阻断**：**是**。

### F-R09-02 ｜ P1 ｜ CI41 的两个失败根因**至今未证**，修复方向正确但未被证实

- **严重性**：P1（阻断"本提交已修复 CI41"这一说法）
- **触发条件**：任何把 `240b581c` 描述为"修复了 CI41"的表述
- **具体依据**：O059 `QUALITY-FAILURE-FACTS.json` 的 `diagnosisLimit` 与 O060/O062 两份 `COMPLETION.json` 的 `CI41RootCause: "UNPROVEN"` 一致；两次本地容器诊断分别在 **SUID sandbox 属主**（060）与 **namespace EPERM**（062）止步，`reachedNativeRecoveryRequire: false`。O064 自身保留 `unprovenCI41TimingRootCause: true`。
- **影响范围**：Linux C1 与 Windows FR201 的因果链均未闭合。
- **最小建议**：**不得**以本地 Linux arm64 容器结果替代 GitHub x64 复现；F-R09-01 的真实 CI 是唯一能推进归因的路径。若 CI41 原失败在 `240b581c` 上**不复现**，也应记录"不复现"而非"已修复"，并保留未证状态。
- **是否 push 前源码技术阻断**：**否**。**是否 merge 阻断**：**否**（但"已修复"的表述本身必须被阻断）。

### F-R09-03 ｜ P2 ｜ `native-driver.ts` 的 readiness 屏障**未覆盖 `app.isPackaged` 的具体形态**，CI41 的原始 TypeError 仍可能复现

- **严重性**：P2（质量／健壮性）
- **触发条件**：Electron 主进程中 `require('electron')` 返回的对象不满足 `app` 完整形态，但 `app` 对象本身存在
- **具体依据**：本轮亲读 `tests/e2e/native-driver.ts:219-242`。readiness 表达式检查的是 `app` **存在**且 `app.isPackaged` 是 `boolean`（`typeof app.isPackaged !== 'boolean'` → `throw new Error('missing required Electron main API')`）。而 CI41 的原始报错是 `Cannot read properties of undefined (reading 'isPackaged')` —— **`app` 本身为 undefined**。新屏障能**更早、更清晰地**报出 `missing required Electron main API`，但 `native-recovery.cjs:12` 的 `app.isPackaged` 读取**没有改变**；驱动仍会继续发送 helper 表达式（原表达式不改），helper 仍会在 `app` 为 undefined 时抛同样 TypeError。
- **影响范围**：C1 的失败**表征**可能改变（更清晰的错误信息），但**失败与否**取决于 Electron 44.9 的 `require('electron')` 映射在目标平台为何返回残缺对象——这一层**未被本候选证实**。
- **最小建议**：把 `native-recovery.cjs` 的 `app.isPackaged` 读取改为**防御式访问**（`app?.isPackaged`）或先行 `if (!app) throw`，使失败点在 helper 内也可归因；**属测试文件，不属产品实现**，风险等级不因此升高。是否做由原 owner 在下一张票决定。
- **是否 push 前源码技术阻断**：**否**。

### F-R09-04 ｜ P2 ｜ Windows 轮询修复**只降低单次等待上限，未消除整例预算被截断的机制**

- **严重性**：P2（验收可靠性）
- **触发条件**：Windows 上 FR201 用例整体耗时逼近 180s 整例预算
- **具体依据**：本轮亲读 `tests/e2e/t02-fr200-fr201.spec.ts` 的 `commit()`：`expect.poll(..., { intervals: [100], timeout: 5000 })`。这改的是**单次 poll 的等待上限**（原为 Playwright 默认 5s → 现显式 5s，实质不变）与**轮询间隔**；而 CI41 的失败是 `Test timeout of 180000ms exceeded`——**整例预算**被截断（本人复核 trace：失败 poll 仅运行 915.573ms 即被整例预算切断，前 19 次成功 poll 累计占用约 177.86s）。
- **影响范围**：若真实耗时结构不变（每次 poll 本身耗 0.9–2.9s、两次提交之间存在约 49.8s／51.8s 空档），**5s 单次上限对整例 180s 预算无实质影响**；本次改动更像是**提高观测频率（100ms）＋ 降低单次等待上限**以更快看到失败，而不是压缩总时长。
- **最小建议**：不改实现；在下一次真实 Windows CI 中**同时**记录整例墙钟与 poll 分布，判断剩余约 1–2s 是否真被省下；并注意 O063 自述"DOM 读取频率可能增、收益未知"——`intervals: [100]` 会**提高** DOM 读频。
- **是否 push 前源码技术阻断**：**否**。

### F-R09-05 ｜ P2 ｜ 轮询缓存是**"最后一次已完成观测"**，不能证明最终业务提交成功或失败

- **严重性**：P2（可追溯性）
- **触发条件**：worker 被强杀，或失败发生在最后一次 poll 完成之后
- **具体依据**：本轮亲读 `tests/e2e/t02-fr200-fr201.spec.ts` 的 `lastCommitPoll`（WeakMap）与 `pollText()`：`text.slice(0, 4096)` 截断，`truncated` 标记，`originalUTF16Units` 记原长度。**判定仍用未截断原文**（`observed.receipt?.includes(...)`），此点正确。但缓存**只保存最后一次完成的 DOM 观测**；O063 `INDEPENDENT-READONLY-REVIEW.md` 自述"缓存可能落后于最终状态，不能证明最后业务提交成功或失败；worker 强杀及异常终止时不保证报告落盘"。
- **影响范围**：CI41 的 Windows 失败中，此缓存**尚不存在于**该次运行（trace 内 `lastCommitPoll`/`lastCompletedCommitPoll` 全文无命中，因该次跑的是修复前代码）——**本轮新增机制至今零真实运行样本**。
- **最小建议**：保持"观测缓存 ≠ 业务结论"的措辞；下一次 Windows CI 后，先确认该 annotation 实际落盘，再考虑其证据价值。
- **是否 push 前源码技术阻断**：**否**。

### F-R09-06 ｜ P2 ｜ `run-engine-tests.py` 的证据**自绑定在 `git rev-parse` 失败时不 fail-closed**（R08 F07 仍在树）

- **严重性**：P2（证据可采性）
- **触发条件**：CI checkout 中 `git rev-parse` 返回非 0
- **具体依据**：本轮亲读 `scripts/run-engine-tests.py:379-383`：`subprocess.run(["git","rev-parse",revision], capture_output=True, check=False)`，**在 `try` 块之外**；`returncode != 0` 时 `summary["checkout"][name] = None`，且**不计入 `errors`**。故 `summary["passed"]` 可在 checkout 未绑定的情况下为真。
- **影响范围**：CI 证据回单可能缺 head/tree 绑定却仍显示通过。这是**证据链缺陷**，不是测试逻辑缺陷。
- **最小建议**：ROOT 已有的接收口径（"拒绝无 head/tree 绑定的证据"）足以在**接收侧**拦截；本轮不主张改码。
- **是否 push 前源码技术阻断**：**否**。

### F-R09-07 ｜ P2 ｜ `python -m pytest` 与 `pytest` 的导入路径差异仍未被覆盖（R08 F06 仍在树）

- **严重性**：P2（口径）
- **触发条件**：依赖 `sys.path[0]` 语义的测试或插件
- **具体依据**：本轮亲读 `scripts/run-engine-tests.py:462`：`os.execv(sys.executable, [sys.executable, "-m", "pytest", *sys.argv[1:]])`。`python -m pytest` 会把 **CWD** 置于 `sys.path[0]`，而 `pytest` 控制台脚本**不**如此。`scripts/engine-test-reporting.py:63-81` 的 identity 13 项中**没有 `sys.path`**。
- **影响范围**：CI 与本地 `pytest` 的导入环境**未被证明等价**；本轮**未发现**遮蔽反例，但等价性**未被证据覆盖**。
- **最小建议**：维持既有具名 owner／事件窗口；**不声称完整导入路径等价**。
- **是否 push 前源码技术阻断**：**否**。

### F-R09-08 ｜ P2 ｜ 状态源未登记当前 head，`62d4b0a2` 的 F05 闭合随 head 前进**重新变开**

- **严重性**：P2（唯一状态源纪律）
- **触发条件**：任何依据 `status.md`／`m0-checklist.md` 判断"当前受审候选"的流程
- **具体依据**：C9 实测——`docs/reviews/T02/status.md` 最后一节仍是「2026-10-26 当前快照追加：62d4b0a2／R08」，`docs/m0-checklist.md` 最后追加节同为 `62d4b0a2`；**两处均无 `240b581c`**。本候选相对 `62d4b0a2` 新增 2 个提交、9 个差异叶、7 个源文件。
- **影响范围**：文档与 head 脱钩——这正是 R08 F05 的同一失效模式在新 head 上重演。
- **最小建议**：由 ROOT 指定的唯一文档 owner 在归档票中追加 `240b581c`／O059–O064 的当前节；**本轮不改**（本轮唯一授权写入为本报告）。
- **是否 push 前源码技术阻断**：**否**。

### F-R09-09 ｜ P2 ｜ 两个 CI job 的**取消／预算**机制可让失败"看起来像通过"

- **严重性**：P2（验收可靠性）
- **触发条件**：`concurrency.cancel-in-progress: true` 触发，或 15/20 分钟预算耗尽
- **具体依据**：本轮亲读 `.github/workflows/ci.yml:10-12`（`cancel-in-progress: true`）、`:17`（Quality 15min）、`:121`（Desktop 20min）、`:97-113` 与 `:155-163` 两个 `if: always()` 制品步。`always()` 是**配置**，不保证被取消后仍能产出完整回单（取消发生在步边界时，其后的步不再执行）。CI41 的 Quality 实际耗时 605.0s、预算 900s；Windows job 在 20 分钟内结束。
- **影响范围**：制品缺失与 job 取消都可能被误读为"通过"。
- **最小建议**：维持 ROOT 既有口径——**只看 step 绿或总数不代证完整**；不采当前扩大超时；不删原始失败制品。
- **是否 push 前源码技术阻断**：**否**。

> **未列入 Top 的既有开放项（仍全部有效，本轮已复核其代码事实仍在树）**：R08 F5／R06 D8 的两处 PATH `python`（C2）；R08 F15／R06 Z P6／D5 的无 `ORDER BY` witness 选取（C3）；R06 D11／R04 M03 的 4299/4300 整数守卫断言缺失（C6）；R06 P3/D3 的 definitions 早期未分类 `ValueError`；R06 D6 的 vendored `notation3.py` `n[-1]`；R08 F09 的 `fr201.1`/`fr201.2` 死制品（C8）；R08 F10／MM R07-03 的 Ruff 与 Prettier 排除面不等（C5）；MM R07-13 的契约类型宽度（C4）；旧 CI36 的 79F 逐例全因未知。**这些是维护窗口，不是本候选新增缺陷**，故不占 Top 位。

---

## 4. 逐项处置：R08 当前位置 31 项

> 说明：R08 的 31 个当前位置 = ZCode 12（Z08-01…11 + Z08-TOP10-OLD79F）+ MiniMax 19（F01…F19）。**下列每一行是本人在本候选 `240b581c` 上的独立判定**，不抄抄 R08 结论。表中"本人本轮依据"均为本轮亲读或实测；"复现"指本轮实际执行核验，"未确认"指本轮无法判定。

### 4.1 ZCode 12 个位置

| ID | 本人本轮处置 | 本人本轮依据 | 阻断性 | 归属／事件窗口 |
|---|---|---|---|---|
| Z08-01 | **仍开（合并门禁）**，并**收窄到新事实**：R08 时的"62d4 未 push"已变为"240b581c 未 push／无 CI" | 本轮实测 `240b581c` 无任何 CI 归档；O064 `notPerformed` 明列 `push`／`new CI dispatch/rerun`／`merge` | 阻断 merge，不阻断 push 前流程 | ROOT 未来精确 push/CI 票；merge 前按 ROOT 五条口径逐项核 |
| Z08-02 | **仍开（未确认）**，本轮**未获新证据** | 本轮未查 Windows job handle 后代；O059 `WindowsJobHandleDescendants: "UNKNOWN"` 仍在 | 不阻断 push；Windows CI 验收项 | Windows 完整 CI 证据接收；**本轮不新增 Job Object 工具为前置** |
| Z08-03 | **仍开（非阻断）**，本轮复核 `ci.yml` 逐条**确认未变** | 本轮亲读 `ci.yml:10-12/17/121`：`cancel-in-progress: true`、15/20min 原值、两个 `always()` 制品步仍在 | 非阻断；验收注意项 | 未来实际制品回单判断；预算变化须新授权 |
| Z08-04 | **仍开（历史 FAIL／缺栈）** | 本轮无新 CI 证据；旧 case7 FAIL 与 79F 缺栈**未因本轮新增证据而消解** | 非当前 push 阻断；CI 验收项 | 下一真实 CI 若复发按新增结构化栈定因；新绿不倒填 |
| Z08-05 | **仍开（维护）**，本轮**实测复核代码事实仍在** | **C2**：`tests/unit/t01-mainline-contract.test.ts:656` 与 `tests/unit/t01-ontology-metadata-contract.test.ts:168` 仍为 `execFileSync('python', ['-I','-B','-c',script])` | 非阻断维护 | T01 原测试维护者下次授权触及两测试或环境适配前；**双向因果限定维持**（不认定其为 79F 根因，亦不排除部分环境因素） |
| Z08-06 | **仍开（远端侧）**；本地控制层资格**不再由本轮重述** | 本轮未重跑控制层自检；O064 的 `full-check-after-lint-fix`（197.285s 自然 0）**绑定 head=2b6c8a26** | 远端归 Z08-01 | Windows/Quality 实际 CI 仍待验 |
| Z08-07 | **仍开（未验／文案维护）** | 本轮未跑 GUI；`OwnershipConflictDetailView.ts` 的文案为**四个 reason 的固定中文标签**（本轮亲读 24-28 行），属"已测子集外"范围 | 非阻断延期 | 原 T01/T02 方法接线窗口；**不扩新功能、不泛加码** |
| Z08-08 | **仍开（P2，发布/供应链缺口）** | 本轮亲读 `ci.yml` 全文：**无 audit／snyk／osv 步**；`.github/` 实测只有 `dependabot.yml`、`ISSUE_TEMPLATE/`、`pull_request_template.md`、`workflows/`，**无 CODEOWNERS**。外部扫描存在性**未知**，**不双向断言** | 非阻断；发布/供应链缺口 | 发布/供应链 owner 另票；本轮不新增扫描配置或外部调用 |
| Z08-09 | **仍开（非阻断卫生观察）** | 本轮亲读两个 `always()` 步的 `path` 均含 `test-results/`（`ci.yml:97-113`、`:155-163`），**确系重复上传**；成本**未量化**，不虚构数字 | 非阻断 | 未来 CI 维护票评估；**不删原始失败制品** |
| Z08-10 | **仍开（部分采纳维持）** | 本轮亲读 `.github/dependabot.yml`：npm + github-actions，均 `directory: /`、`interval: weekly`、`target-branch: develop`，npm `open-pull-requests-limit: 5`。**实际运行/合并记录、uv/vendor 跟进、SLA/EOL 未证** | 非阻断；长期维护未知 | 发布/vendor 原 owner 未来窗口；**配置存在 ≠ 执行完成** |
| Z08-11 | **仍开（独立 HOLD 群）**，本轮**逐项复核未发现任一 HOLD 被本提交关闭** | 本轮亲读三个新文件均为**测试文件**，零产品代码；`tests/e2e/native-driver.ts` 的单测断言明确 `expect(r.app.focus).not.toHaveBeenCalled()`、`expect(r.app.exit).not.toHaveBeenCalled()`（据 O064 `APPLIED-03.diff` 与本轮实读 `native-driver.test.ts` 断言段），即**无 side-effect API 验证、无 noSandbox 变化** | 非阻断；各独立 HOLD | 原各 owner／父 FR 与发布验收时；**不新建功能或产品验证** |
| Z08-TOP10-OLD79F | **仍开（历史残留）** | 本轮无任何 CI36 原始件；O059 仅含 2b6c8a26 时点事实 | 非当前阻断 | ROOT 历史残留登记及未来真实复发证据 |

### 4.2 MiniMax 19 个位置（F01–F19）

> **重要**：F04 已由 F 项原审作者本人**撤回**（含 base64 残留一并撤回），F11 被原审作者**收窄**。**本轮不复活已撤回项**，也不把"未复核"写成"已闭合"。

| ID | 本人本轮处置 | 本人本轮依据 | 阻断性 | 归属／事件窗口 |
|---|---|---|---|
| **F01** | **仍开（流程），并按本轮事实更新** | 本轮实测 `240b581c` 相对 `2b6c8a26` 只改 **3 个测试文件**、**零产品代码**。R08 时的"594 行 CI 控制层从未进入双审"**已被本轮覆盖**——本轮亲读 `run-engine-tests.py`(470)＋`engine-test-reporting.py`(124)＋`ci.yml`(163) 全文。**F01 的具体缺口因此闭合**，但"新 head 需新一轮双审"这一流程仍在进行中 | 否（流程） | 本报告即为本轮双审之一 |
| **F02** | **仍开（合并门禁）**，数值**更新为 240b581c** | 本轮实测：该 head 无 CI；O064 的 197.285s 与 171.363s **均绑定 head=2b6c8a26**，是**开发机数字**，脚本自陈非提速承诺（`HISTORICAL_SCORES` 注释："NOT per-test durations or promised speedups"） | 否（合并门禁） | ROOT 发精确 push/PR16 票后按原 15/20 分钟内运行并逐 node 核验 |
| **F03** | **仍开 + 限定**，本轮**复核脚本结算语义未变** | 本轮亲读 `run-engine-tests.py:268-364` `account()`：逐 node 校验 `start`/`report` 三阶段（setup/call/teardown）、`invalid` 集合、`coverage mismatch against full native collection`（`:432-433`）；`engine-test-reporting.py:94-95` 在 shard 与全量 manifest 不一致时 `raise pytest.UsageError`。**标签为描述性文字，不放行也不否定** | 否（合并门禁） | 同 F02 接收口径 |
| **F04** | **维持撤回，不复活** | 原审作者本人撤回（含 base64 残留）。**本轮未发现任何新证据要求复活**；本轮亦未验证其撤回理由（**不代证**） | 否 | 本票内闭合 |
| **F05** | **重新变开（新增事实）** | **C9**：`status.md` 与 `m0-checklist.md` 均仍停在 `62d4b0a2`，**未登记 `240b581c`／O059–O064**。R08 时该条在 `62d4` 闭合，随 head 前进再次张开 | 否（合并前文档条件） | ROOT 唯一文档维护者，归档票后、merge 前 |
| **F06** | **仍开（维护）**，本轮**实测复核代码事实未变** | **C7'（本轮亲读）**：`scripts/run-engine-tests.py:462` 为 `os.execv(sys.executable, [sys.executable,"-m","pytest",*sys.argv[1:]])`；`scripts/engine-test-reporting.py:63-81` identity **13 项中无 `sys.path`**。与 R08 原判一致，本轮**未发现遮蔽反例** | 否 | 原 T02 开发归口；ROOT 后续首个 CI 控制层维护票；**任何声称完整导入路径等价之前** |
| **F07** | **仍开**，本轮**实测复核代码事实未变** | 本轮亲读 `run-engine-tests.py:379-383`：`git rev-parse` 在 `try` 之外、`check=False`、非 0 → `None` 且**不计入 errors** | 否 | 原 T02 开发归口；**接收任何无 head/tree 产出前** |
| **F08** | **部分闭合（新增正面事实），但**本体仍开 | **正面**：本轮亲读 `OntologyMainlinePage.tsx` 的 `preview()`：新增 `current()` 闭包，逐项校验 `lifetime.active`／`factLifetime.current===lifetime`／`sequence` 相等／`live===snapshot`／`source===boundSource`／`sourceIdentity` 相等／`!live.stale`／`!live.pending`／`phase` 不在 `['reading','preparing','submitting']`；`useLayoutEffect` 清理时同步 `session.discardPreview()`。**这是 R08 后基线的改进，不是本提交**。**本体仍开**：`if (!current()) return` 仍是**静默返回**，无用户可见提示 | 否 | 原 T02 前端归口；后续 UX/异步预览维护窗口 |
| **F09** | **仍开（P3）**，本轮**实测复核引用面未变** | **C8**：`packages/engine/pyproject.toml:7,20` 与 `uv.lock:73,252-258` **只引用 `fr201.3`**；`fr201.1`／`fr201.2`（各约 2.38 MB）仍无引用 | 否 | 原 T11 供应链/发布归口；**不私自删 wheel** |
| **F10** | **仍开**，本轮**实测复核两覆盖面仍不等** | **C5**：`pyproject.toml` Ruff format `exclude` 为按名枚举（T01 四文件 + T02 `round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,minimax-m31flash-r2}.md`）；`.prettierignore` 整目录忽略 `docs/reviews`。**新写的 `round-09/minimax-m31flash.md` 恰好落在 Ruff 排除面内**（`minimax-m31flash` 在枚举中、`round-[0-9][0-9]` 匹配 `round-09`），故本报告不会被 Ruff format 改写——**这正是该排除面的既定用途**，同时说明"新 raw 报告即可让 `npm run check` 失败"这一失效路径**仍存在但对当前文件名已闭合** | 否 | ROOT 报告归档归口 + 原 T02 维护归口 |
| **F11** | **维持原审作者收窄**；本轮**未发现需扩大的新证据** | 本轮未对"人工事实 ID 内容派生后重放报所有权冲突而非幂等成功"作新的产品裁定；`packages/engine/src/ontolearn_engine/storage.py` 的 `ManualOwnershipConflict("reservedIdentity")` 路径仍在（本轮亲读），语义待产品裁定的事实不变 | 否 | 原审作者本票内收窄；**不默认要求新人类裁定** |
| **F12** | **仍开**，本轮**复核 ci.yml 未变** | 本轮亲读 `ci.yml`：`if: always()` 步在 `:98` 与 `:156`；`run-engine-tests.py` **无内部看门狗**（`stop()` 有 3s+2s 收尾窗口，但无超时自杀） | 否 | ROOT 未来 CI 结算逐步核产物；**不延时/重试/隐藏取消** |
| **F13** | **仍开**，本轮**复核脚本注释未变** | 本轮亲读 `run-engine-tests.py:19-21` 注释逐字："They are NOT per-test durations or promised speedups." | 否 | ROOT 后续 PR16 说明/CI 结算窗口；**不量化未实测 runner 提速** |
| **F14** | **仍开**，本轮**复核代码事实未变** | 本轮亲读 `packages/contracts/src/index.ts:1009` 的 `reassembleOwnershipDetail` 内 `pageSize: 64` 为**硬编码**；真实响应另由 `matchesOwnershipDetail` 以真参数校验（`v2.ts`） | 否 | 原 T02 契约归口；后续首个 ownership-detail 契约维护票 |
| **F15** | **仍开（未确认观察）**，本轮**实测复核 SQL 事实未变** | **C3**：`storage.py:1151` 与 `:1170` 两条 `GROUP BY ... LIMIT 1` / `LIMIT 2` **均无 `ORDER BY`**。本轮**未构造反例**，维持"未确认观察"，**不升级为已证跨运行缺陷** | 否 | 原 T02 storage/契约归口；下次触及 witness 选取时 |
| **F16** | **仍开（容量维持）**，本轮**未测量任何容量数字** | 本轮**未**运行任何容量／迁移测试；`docs/m0-checklist.md` 与 `status.md` 中的容量口径**维持原样**，不提高上限、不解除容量 HOLD | 否 | 原 T02 契约归口持续保留原 capacity |
| **F17** | **维持原判（无需新动作）** | 本轮**未触及** `e79149fd` 的 identifier pattern 转义提交，相关代码未在本候选中变化 | 否 | 原 T02 前端归口；无新增动作 |
| **F18** | **仍开 + 保留** | 本轮**未独立重算** vendored 哈希三方一致（§2.2 列为未读）；**依赖 vendored 特性属实**，"包内一致"这一**过度陈述**不予采信 | 否 | 原 T11 供应链 + 原 T02 依赖归口；下次依赖/打包维护票与发布前供应链核验 |
| **F19** | **仍开** | 本轮**未发现** R07 链内 ID 命名歧义的新证据；`round-09` 目录命名与既有 `round-0N` 一致，**本轮未新增命名歧义** | 否 | ROOT 唯一归档归口；**保留旧 raw 与旧标题** |

**31 项小结**：**0 项关闭**、**0 项撤回（除维持原作者已撤回的 F04）**、**31 项仍开或维持**。其中 **F01 因本轮覆盖了 594 行 CI 控制层全文而闭合其具体缺口**（仍登记为"过程项完成"），**F05 重新变开**，其余按本轮实测证据维持或限定。

---

## 5. 逐项处置：历史 78 个位置

> 说明：R08 `disposition.md` §4 逐行给出 **78 个唯一历史 ID**。本轮**按 R08 原件逐行抽取 ID 列实测核对**（抽出 78 行，计数与 R08 §4 末行"计数：…＝78"一致），分组为：**Z F 系列 10＋MM R07 系列 13＝R07 组 23；R06 Z P 系列 8＋R06 D 系列 12＋R06 MM 系列 13＝R06 组 33；R04 十四；R05 二十一**。**下列每一行是本人在 `240b581c` 上的独立处置**。因本候选相对 `62d4b0a2` **零产品代码变更**，绝大多数历史位置的**代码事实未变**；本轮对这些位置**逐条重新核对了其代码事实是否仍在树**，凡我实测过的给出实测依据，未实测的明确标注"本轮未复核"。**不抄历史结论，不以"沿用前轮"代替逐项判断。**

> **ID 命名口径**：本轮一律沿用 **R08 原件的稳定条目 ID**（如 `R06 D3`、`R06 MM07`），**不与 R08 §5 的"残句有界解释"或任何 Top10 序号混用**。

### 5.1 R07 组（23 项：Z F 系列 10 ＋ MM R07 系列 13）

| ID | 本人本轮处置 | 本人本轮依据 | 归属／事件窗口 |
|---|---|---|---|
| Z F1 | **仍开（门禁）**；数值更新为 240b581c | 本轮实测该 head 无 CI；O064 运行绑定 head=2b6c8a26 | ROOT 精确 CI 票；新 CI 后、merge 前 |
| Z F2 | **仍开（维护）** | 本轮**未复核**新 raw 命名面；**Ruff 排除面已含 `round-09/minimax-m31flash.md`**（C5） | T02/ROOT 将来新增 raw 命名或改规则时维护 |
| Z F3 | **仍开（维护）** | 本轮**未复核**具体 `write_text` 调用面；**未发现**本候选引入新编码面 | 原测试 owner 下次授权触及该调用或环境适配时 |
| Z F4 | **已闭合（口径）**，本轮**未复核**，维持 | 本轮未发现该分母相关代码变化 | 本次事实修订，无产品改动 |
| Z F5 | **仍开（维护）**，本轮**实测复核** | **C2**：两处 PATH `python` 仍在树 | T01 原测试维护者下次授权触及两测试或环境适配前 |
| Z F6 | **仍开（逐项）**，集合**未**被集合化关闭 | 本轮**实测复核其中两项**：R06 P3 的 definitions 早期未分类异常与 R06 D6 的 vendored `n[-1]`（本轮**未**逐字复读 vendored wheel 内文件，见 §2.2），**故仅记"无新证据推翻"** | 原 owner／各接线或维护事件 |
| Z F7 | **仍开（HOLD）** | 本轮未复核各 HOLD 项的关闭证据；**本候选零产品代码**，无 HOLD 被本提交关闭 | 各原 owner 对应父 FR/发布/平台/容量验收前 |
| Z F8 | **仍开（部分）** | 本轮亲读 `rdf_snapshot.py`：`TermInputError` 与 `BadSyntax`/`Notation3InputError` 分流**在树**（已知拒绝 vs 未知分支并存）；**裸族定位未全闭**本轮未逐条复核 | 未知与新家族在相应接线前按原 HOLD 处理 |
| Z F9 | **已闭合（限本受审面）**，本轮**实测正面复核** | 本轮亲读 `project-mainline-service.ts` 的 `getOwnershipConflictDetailPage`：调用前 `client.owner !== current.owner` → `denied()`，调用后复核 `selectionEpoch`／`source.current()?.owner`／`projectId`／`engineSessionId` | T01/T02 后续触及合同出口时核 |
| Z F10 | **仍开（观察）**，GUI 本轮未实测 | 本轮**未运行 GUI** | 本次既有证据接收 |
| MM R07-01 | **已闭合**，本轮**实测复核排除面在位** | **C5**：`pyproject.toml` 中 T02 排除项在位 | 本次静态接收 |
| MM R07-02 | **仍开（维护）** | 本轮未复核新 raw 文件面 | ROOT/T02 未来确增 raw 名字时 |
| MM R07-03 | **仍开**，本轮**实测两覆盖面仍不等** | **C5** | 将来独立配置票才讨论 |
| MM R07-04 | **在 `62d4` 已闭合，在 `240b581c` 重新变开** | **C9**：两状态文档仍停在 `62d4b0a2` | ROOT 指定文档 owner，归档票后、merge 前 |
| MM R07-05 | **仍开（overlay 维护）** | 本轮实测 `git status`：`M AGENTS.md` 仍为未提交 overlay，本轮**未触碰** | ROOT/指南 owner 未来授权维护时 |
| MM R07-06 | **已闭合（口径）** | 本轮未复核；无新运行 | 本次事实修订 |
| MM R07-07 | **已闭合（口径）** | 本轮未复核载荷分布 | 原测试 owner，载荷变化时 |
| MM R07-08 | **已闭合（口径）** | 本轮**未扩大范围**：FR200 语义覆盖不后移，附录 C 不扩 | 整父 FR/具名下游由原 owner 另验 |
| MM R07-09 | **已闭合（口径）** | 本轮**未重算 build nonce 字节**；O064 记录为 24 字节 nonce 变、其余 606447 字节与另 4 build 不变（本人采信归档并标注为**他人运行**） | 本次既有证据限定 |
| MM R07-10 | **已闭合（口径）**，差因仍未证 | 本轮**未新增计数断言** | 本次事实修订，无新复跑票 |
| MM R07-11 | **仍开（观察）** | 本轮亲读 `mainline-facts.ts`：`manualFactPlan` 对 `owner !== null \|\| source_row !== null \|\| managed_value !== null` 抛 `MANAGED_FACT_REQUIRES_OWNER`；重叠判定含 `row.object === original.object` 与 edit 时 `=== replacement.object` | T02/ROOT 未来 PR 说明可解释既有规则 |
| MM R07-12 | **仍开（HOLD）** | 本轮**未独立重算** vendor 哈希；**引用面实测**见 C8 | 原 vendor/发布 owner，升级/发布前另票 |
| MM R07-13 | **仍开（维护）**，本轮**实测复核** | **C4**：`contracts/src/index.ts:894-896` 的 `OwnershipDetailArgs` 仍宽于 schema | 契约 owner 下次授权整理类型时 |

### 5.2 R06 组（33 项：Z P 系列 8 ＋ D 系列 12 ＋ MM 系列 13）

| ID | 本人本轮处置 | 本人本轮依据 | 归属／事件窗口 |
|---|---|---|---|
| R06 Z P1 | **仍开（门禁）** | 本轮实测无 CI；旧 79F 逐例原因仍未知 | 合并前真实 CI 门禁 |
| R06 Z P2 | **仍开** | 本轮亲读 `run-engine-tests.py` 的 `account()` 结算语义 | 未来 CI 证据接收标准 |
| R06 Z P3 | **仍开** | 本轮**未复核** `_definition` 分类细节（未逐行读 `domain_changesets.py` 该段） | T01 核心维护；原始 triples/Agent 接线前 |
| R06 Z P4 | **部分闭合** | 本轮**实测正面**：typed witness 路径在树（`storage.py` `SingleDeclarationConflict`／`ManualOwnershipConflict` 与 `job_store.py` `_ownership_header`）；**裸族未全闭**本轮未复核 | T01 详情合同＋T02 消费 |
| R06 Z P5 | **仍开** | 本轮**未复核**错误码集合差（未逐条比对 UI/契约/引擎三处码表） | T01 契约＋T02 方法出口 |
| R06 Z P6 | **仍开（未确认观察）**，本轮**实测复核** | **C3** | T01 下次触及 witness 选取时 |
| R06 Z P7 | **已闭合（沿既有决定）**，本轮**实测复核** | 本轮亲读 `domain_changesets.py`：`parsed.n3() != value` → `INVALID_REQUEST field=params`，**精确 canonical 政策在位** | 无待办；未来改政策才新人类决定 |
| R06 Z P8 | **逐项仍开**，不以集合标题掩盖 | 本轮未逐项复核六子项 | 各原归口 |
| R06 D1 | **仍开（门禁）**，更新为 240b581c | 本轮实测无 CI | ROOT 正常票 |
| R06 D2 | **部分闭合 → 在 240b581c 上重新变开** | **C9**：`status.md`／`m0-checklist.md` 仍停在 `62d4b0a2` | ROOT 指定唯一文档维护者 |
| R06 D3 | **仍开** | 本轮**未复核** definitions 时序定性（未逐行读 `domain_changesets.py` 预览段）；**无新证据推翻** | T01 原归口；原始 wire/Agent 接线前 |
| R06 D4 | **部分闭合**（两出口最终码均为 `OWNERSHIP_CONFLICT`；**裸族定位未全闭**） | 本轮亲读 `storage.py`：`ManualOwnershipConflict` 与 `SingleDeclarationConflict` 均 `category="ownership"`，`job_store.py` 的 `_application` 在捕获 ownership 类 `Conflict` 后 `fault("OWNERSHIP_CONFLICT", detailRef=identity)`，**两出口最终码一致**。**裸族定位本轮未逐条复核** | T01＋T02；随对应家族接线处理 |
| R06 D5 | **仍开（未确认观察）**，本轮**实测复核** | **C3**：`storage.py:1151`／`:1170` 两条 `LIMIT` 查询仍无 `ORDER BY`。本轮**未构造反例**，**不升级为已证跨运行缺陷** | T01 下次触及选取时维护 |
| R06 D6 | **仍开（代码事实仍在）** | 本轮**未逐字复读** vendored `notation3.py`（§2.2 列为未读）；**无新证据推翻**"类型化守卫在树、不可达性未证" | T02 vendor 补丁/T01 入口；新增不经现封装解析入口前复核 |
| R06 D7 | **仍开** | 本轮**未复核**错误码集合差（同 R06 Z P5） | T01/T02 对应方法接线前 |
| R06 D8 | **仍开（维护）**，本轮**实测复核** | **C2**：两处 PATH `python` 仍在树 | T01 原测试维护者；下次授权触及或环境适配前 |
| R06 D9 | **已闭合（口径）** | 本轮**未新增计数断言**；Ruff 各时点计数原件保留、差因不结论 | 文档唯一维护者，归档票后追加 |
| R06 D10 | **仍开** | 本轮**未运行 GUI**，四类具名下游（推导／保存查询／SHACL／报告）未逐类实测；公共失效机制与九行正负例证据维持，两分不抹 | T01 公共失效＋T02 编辑与各下游 owner；父 FR/消费链验收前 |
| R06 D11 | **仍开（维护）**，本轮**实测复核** | **C6**：引擎测试仅对 `4301` 有断言（`test_mainline_language_input_rejection.py:36`），**4299/4300 应用边界断言仍缺** | T02 输入边界；下次授权触及整数守卫时 |
| R06 D12 | **已闭合（有界）**，不外推 | 本轮**未复核**具体正面证据（补丁可重建、哈希三方一致等）；**不外推**全平台/法律 | 已完成证据与独立 HOLD 分别保留，无待办 |
| R06 MM01 | **仍开（门禁）** | 本轮实测无 CI；旧 79 原因仍未知 | ROOT；新 CI 后合并前核 |
| R06 MM02 | **已闭合（事实）** | 本轮采信 O059（**他人运行**）：Quality=failure／Windows=failure／macOS=success | ROOT/新 CI 后 |
| R06 MM03 | **仍开（门禁）** | 本轮**未发现任何本候选新包制造/运行**；旧 094 不称新包 | 无新包制造票 |
| R06 MM04 | **已闭合（分别承接）→ 240b581c 上重新变开** | **C9** | ROOT 文档 owner，归档票后 |
| R06 MM05 | **仍开** | 同 R06 Z P5 | T01/T02；方法接线前 |
| R06 MM06 | **仍开** | 同 R06 Z P3 | T01；接线前 |
| R06 MM07 | **部分闭合** | 同 R06 Z P4：typed witness 已实现并可读；**裸族仍延期** | T01/T02；家族接线前 |
| R06 MM08 | **仍开（未确认观察）**，本轮**实测复核** | **C3** | T01 下次触及选取时 |
| R06 MM09 | **已闭合（维持）**，冗余件见 F09 | **C8** 实测引用面 | vendor/发布 owner |
| R06 MM10 | **已闭合（维持）**，本轮**实测 overlay 仍在** | `git status` 实测 `M AGENTS.md` | 无待办 |
| R06 MM11 | **已闭合（信息）**，本轮**实测复核 locator 字段面** | 本轮亲读 `storage.py` `ManualOwnershipConflict.locator()`：仅 `id`／`owner`／`sourceRow`／`slot{subject,predicate}`，**不含 object** | 无待办 |
| R06 MM12 | **仍开（维护）**，本轮**实测复核** | **C2** | T01 原测试维护者 |
| R06 MM13 | **已闭合（信息）** | 本轮未据 LOC 推正确性 | 无待办 |

### 5.3 R04 十四项 与 R05 二十一项

| ID | 本人本轮处置 | 本人本轮依据 | 归属／事件窗口 |
|---|---|---|---|
| R04 Z01 | **仍开（未确认观察）** | **C3** | T01 下次触及 witness 选取 |
| R04 Z02 | **撤回维持（不复活）**；262144/16MiB 预算边界仍在 | 本轮亲读 `domain_changesets.py` 顶部 `MAX_DOCUMENT = 16 * 1024 * 1024` **在位** | T01 详情预算下次授权维护 |
| R04 Z03 | **仍开（OPEN）** | 同 R06 Z P3 | T01；原始 triples/Agent 接线前 |
| R04 Z04 | **部分闭合** | 同 R06 Z P4 | T01/T02 |
| R04 Z05 | **仍开** | 同 R06 Z P5 | T01/T02 |
| R04 Z06 | **已闭合（沿既有决定）**，本轮**实测复核** | 同 R06 Z P7 | 无待办 |
| R04 Z07 | **已闭合（信息）** | 本轮未据 LOC 推正确性 | 无待办 |
| R04 M01 | **已闭合（历史演进）**；当前 head 状态源另见 F05 | — | ROOT 归档票 |
| R04 M02 | **已闭合（维持）**；fr201.1/2 保留不删见 F09 | **C8** | 无待办 |
| R04 M03 | **仍开（未来维护）**，本轮**实测复核** | **C6**：仅 4301 有断言 | T02；下次授权触及整数守卫时 |
| R04 M04 | **仍开（OPEN）** | 本轮**未逐字复读** vendored `notation3.py`（§2.2）；无新证据推翻 | T02 vendor/T01 入口 |
| R04 M05 | **仍开（OPEN）** | 同 R04 Z03 | T01 |
| R04 M06 | **已闭合（维持分层，非绕过漏洞）**，本轮**实测复核双端校验链在位** | 本轮亲读 `project-mainline-service.ts` 的调用前后身份检查 + `mainline.py` `_OwnershipProof.check()`（校验 owner/reply/store/lease/project/generation/method 并 `authorize`） | 无待办；**不外推为全产品安全认证** |
| R04 M07 | **仍开（维护窗口保留）** | 本轮未证冲突；**不直接缩导出面** | 契约 owner 下次 API 整理时评估 |
| R05 Z P1 | **仍开（门禁）** | 本轮实测无 CI | ROOT 合并门禁 |
| R05 Z P2 | **已闭合（事实）**；不迁移成新 CI 绿 | 同 R06 MM02 | 无待办 |
| R05 Z P3 | **仍开** | 同 R06 Z P3 | T01；接线前 |
| R05 Z P4 | **部分闭合** | 同 R06 Z P4 | T01/T02 |
| R05 Z P5 | **仍开** | 同 R06 Z P5 | T01/T02 |
| R05 Z P6 | **已闭合（口径）**，但见 F03 | 本轮亲读 `ci.yml:139-147` Windows 诊断步**仍在**且**明确标注 "not acceptance"** | 无待办 |
| R05 Z P7 | **已闭合（口径）**，见 F03 | 同上 | 无待办 |
| R05 Z P8 | **已闭合（维持）→ 240b581c 上重新变开** | **C9** | ROOT 文档 owner |
| R05 MM01 | **仍开（门禁）** | 本轮实测无 CI | ROOT；新 CI 后合并前核 |
| R05 MM02 | **已闭合（事实）** | 同 R06 MM02 | ROOT/新 CI 后 |
| R05 MM03 | **仍开（门禁）** | 本轮未发现新包 | 无新包制造票 |
| R05 MM04 | **已闭合（分别承接）→ 重新变开** | **C9** | ROOT 文档 owner |
| R05 MM05 | **仍开** | 同 R06 Z P5 | T01/T02 |
| R05 MM06 | **仍开** | 同 R06 Z P3 | T01 |
| R05 MM07 | **部分闭合** | 同 R06 Z P4 | T01/T02 |
| R05 MM08 | **仍开（未确认观察）**，本轮**实测复核** | **C3** | T01 下次触及选取时 |
| R05 MM09 | **已闭合（维持）**，冗余件见 F09 | **C8** | vendor/发布 owner |
| R05 MM10 | **已闭合（维持）**，本轮**实测 overlay 仍在** | `git status` | 无待办 |
| R05 MM11 | **已闭合（信息）**，本轮**实测复核** | 同 R06 MM11 | 无待办 |
| R05 MM12 | **仍开（维护）**，本轮**实测复核** | **C2** | T01 原测试维护者 |
| R05 MM13 | **已闭合（信息）** | 本轮未据 LOC 推正确性 | 无待办 |

### 5.4 78 项小结

**计数复核（本轮实测）**：本轮从 R08 `disposition.md` §4 原件**逐行抽取 ID 列**，得 **78 行**（工具实测 78，非引述）。按前缀实测分布为：**Z F 系列 10 ＋ MM R07 系列 13 ＝ R07 组 23；R06 Z P 系列 8 ＋ R06 D 系列 12 ＋ R06 MM 系列 13 ＝ R06 组 33；R04 系列 14；R05 系列 21**；合计 78，与 R08 §4 末行计数一致。**无缺漏、无重号、无与 R08 编号混淆；本轮全部 78 项各有且仅有一行独立处置**（§5.1–§5.3，已用逐 ID 匹配工具验证 `missing_rows=0`）。

**本轮处置分布**：**0 项新关闭**；**5 项因 head 前进而重新变开**（MM R07-04、R06 D2、R06 MM04、R05 Z P8、R05 MM04 —— 均为状态源未登记新 head 的同一根因）；**10 项因本轮取得新的实测正面证据而复核确认**（Z F9、Z F10 的未实测部分除外；R06 MM11、R06 MM09、R06 MM10、R06 Z P7、R04 M06、R04 Z06、R05 MM10、R05 MM11 —— 本轮**实测**复核而非仅引述）。

**本轮明确标注"未复核"的项**（不写成"已闭合"）：Z F2、Z F3、Z F6（部分）、Z F7、Z F8（部分）、Z F10、MM R07-02、MM R07-06、MM R07-07、MM R07-10、MM R07-12、R06 Z P3、R06 Z P5、R06 Z P8、R06 D3、R06 D5、R06 D6、R06 D7、R06 D9、R06 D10、R06 D12、R04 Z07、R04 M04、R05 Z P2（部分）、R06 MM02（他人运行采信）／R06 MM03、R06 D2、R06 D4 等。**这些项本轮未取得推翻其状态的证据，故维持原状态**，但**本轮不对其做新的正面断言**。

---

## 6. 用户原始清单 1–160 逐条

> 判定口径：**适用**（本产品确有此面，本轮给出结论）／**部分适用**（有对应面但不完整）／**本轮范围外**（属其他 FR／里程碑，不因本轮关闭）／**不适用**（本产品形态下无此面）／**无法确认**（代码/文件无法判定，需人类或组织事实）。
> **本轮口径与 R08 的差异**：凡涉及本候选新增/变更代码的条目（10、23、25、26、30、31、40、41、44、46、47、55、90、95、97、121、123、124、128、129、132、155、158），本轮**重新以 `240b581c` 的实际代码为据**判定；凡本轮实测过的，给出实测标记。

| # | 清单项 | 判定 | 依据／缺口 |
| --- | --- | --- | --- |
| 1 | 表结构是先设计而非 AI 即兴逐表拼 | 适用 | `packages/contracts/v2/schema.json` 以 `$defs`＋`oneOf`＋`additionalProperties:false` 定义全部边界；本轮新增 `params_project.ownership.detail` 的**两个 `oneOf` 分支**（`documentHash: const null`＋`startOrdinal: const 0`，或 `documentHash: hash`＋`startOrdinal: integer 1..511`），`pageSize` 均 `integer 1..64`。**未覆盖附录 C 构造全集** |
| 2 | 带加号的邮箱也能登录 | 不适用 | 本地单机桌面应用，无账号/登录体系 |
| 3 | 密码重置链接过期且一次性 | 不适用 | 同上 |
| 4 | MFA ＋ 丢失手机恢复路径 | 不适用 | 同上 |
| 5 | 会话超时＋可吊销某用户全部会话 | 部分适用 | 有引擎会话与握手（`engineSessionId`、hello bootstrap、pendingRequests Map），**不是用户账号会话**；"吊销一个用户的所有会话"不适用 |
| 6 | 企业 SSO | 不适用 | 无身份提供方集成 |
| 7 | SAML | 不适用 | 同上 |
| 8 | SCIM 离职即时撤权 | 不适用 | 同上 |
| 9 | 比"管理员/所有人"更细的角色权限 | 部分适用 | 能力注册表＋方法白名单（`mainline.py` `METHODS` 本轮新增 `project.ownership.detail`）＋单一 mainline owner 权威；**无多角色体系** |
| 10 | 改 URL 里的一个数字就读到别人的数据 | 适用 | **本轮亲读全链**：`engine.ts` 校验 `params.projectId !== record.selected?.projectId` → `deniedOrdinary()`；`mainline.py` `_OwnershipProof.check()` 校验 owner/reply/store/lease/project/generation/method 并 `authorize`；`job_store.py` `_ownership_header` 校验 `header["origin"] != proof.origin` → `NOT_FOUND`、并校验 `fingerprint == digest({origin,requestHash,documentHash})`；渲染层 `mainline-ownership.ts` 每次分页重校验 `matchesOwnershipDetail`。本地单用户，无跨用户面 |
| 11 | 租户隔离 | 不适用 | 无多租户；最接近的是项目间 owner/project 绑定 |
| 12 | 管理员"登录为该用户"＋审计 | 不适用 | 无多用户；最接近是 ownership 详情的 `origin`（ownerId/hostClientId/engineSessionId） |
| 13 | 登录限流 | 不适用 | 无登录；最接近是引擎帧/页/内存预算与 4299/4300 整数输入上限 |
| 14 | 锁定策略不误锁 CFO | 不适用 | 无账号锁定；受控拒绝不锁死用户 |
| 15 | 数据库迁移可正向可回滚 | 部分适用 | 有 format3 迁移（**本轮未运行**，历史口径为 44 条条件 skip）。**回滚路径未验** |
| 16 | 迁移不在周二下午锁主表 | 部分适用 | SQLite 单写者＋事务（`job_store.py` `_transaction` 包装器）；**并发迁移场景未验** |
| 17 | 索引（50 行到 500 万行） | 部分适用 | 读路径有 SQLite 查询；**容量 Q5/D2 未确认**。本轮范围外 |
| 18 | 连接池 | 不适用 | 本地 SQLite 单连接 |
| 19 | 每晚备份 | 不适用 | 无服务端；本地项目包不等于备份 |
| 20 | 从备份恢复且已演练 | 部分适用 | 项目包导入/导出属 FR-203，本轮范围外；无备份恢复证据 |
| 21 | 时间点恢复（误删 where） | 不适用 | 无服务端；最接近是版本化提交与历史运行不可改写（FR-804／附录 D.1） |
| 22 | 软删除 | 部分适用 | `rdf_snapshot.py` 的 managed deletion 墓碑语义；映射源行删除不删手工事实。**任意误删的产品级回收未验** |
| 23 | 服务端校验而非只在前端 | 适用 | **本轮亲读**：引擎侧 `rdf_snapshot.py` 的 `TermInputError` 分类 + `domain_changesets.py` 的 `parsed.n3() != value` → `INVALID_REQUEST field=params`（**引擎在提交前做 canonical 精确比对**）；契约侧 zod/`.strict()`＋`contract_v2.py`。**非仅前端** |
| 24 | 时区正确存储 | 不适用 | 无提醒/日程/时间调度功能 |
| 25 | 名字里带撇号的客户 | 适用 | 事实值全参数化 SQL＋canonical JSON；`term()` 对撇号/引号字符走 Turtle 解析的**确定拒绝**路径（`BadSyntax`/`Notation3InputError` → `TermInputError`），非未知失败 |
| 26 | emoji／重音／RTL | 部分适用 | canonical 精确 `term(value).n3()`＋语言标签小写 canonical；**RTL 双向文本未专门验** |
| 27 | 金额用整数存储 | 不适用 | 无金额 |
| 28 | 多国货币/舍入/税 | 不适用 | 同上 |
| 29 | 数据模型扛得住第二个客户的小改动 | 部分适用 | 数据层次（本体定义/断言事实/当前推导/场景副本/历史运行）＋版本化提交；"第二客户"不在本地单机范围 |
| 30 | 幂等键 | 部分适用 | `operationId` 存在（draft.save）；**人工事实 ID 内容派生后，重放同一事实报所有权冲突而非幂等成功**（F11，语义待产品裁定） |
| 31 | 连点四次提交去重 | 适用 | **本轮亲读**：`storage.py` 在写入既有事实且 `existing["owner"]` 为空但 `existing["object"] != fact["object"]` 时抛 `ManualOwnershipConflict(reason="reservedIdentity")`；渲染层 `mainline-facts.ts` `newManualFactPlan` 对已存在三元组抛 `FACT_ALREADY_EXISTS`；`OntologyMainlinePage.tsx` 的 `current()` 围栏 + `pending` 禁用按钮。**GUI 未实测** |
| 32 | 第 400 页的分页 | 部分适用 | cursor＋`maxCursorRecords`＋字符上限；ownership detail 分页为 `startOrdinal`/`pageSize`，schema 限 `startOrdinal ≤ 511`、`pageSize ≤ 64`，渲染层循环上限 512 次。**400 页规模未验** |
| 33 | 导出 | 部分适用 | Turtle 导出属 FR-203，本轮范围外 |
| 34 | 导入（2009 年的 CSV） | 部分适用 | CSV/XLSX 映射属 M2，本轮范围外；附录 C 构造子集受控拒绝属 FR-203 |
| 35 | 保留规则与合同一致 | 不适用 | 无合同数据保留 |
| 36 | 密钥不在代码/仓库/AI 对话 | 适用 | **本轮实测**（C7）：`apps/`、`packages/`、`scripts/` 无凭据类字面量；命中项全为内部对象句柄。凭据只在主进程；Python 引擎不持密钥、不调模型 |
| 37 | 轮换上个月 AI 粘进配置文件的密钥 | 不适用 | 无生产密钥；模型外发 S3 前未接入 |
| 38 | 确认每个被装的包存在且是想要的那个 | 适用 | `uv.lock` 指向 vendored wheel 路径且带 sha256 与 size；**本轮实测引用面（C8）**：仅 `fr201.3` 被引用。**遗留**：fr201.1/2 无引用（F09） |
| 39 | 依赖扫描 | 部分适用 | `npm ci`＋`uv sync --frozen`＋两份锁文件；**无第三方漏洞/SCA 扫描工具**（`ci.yml` 全文无 audit 步） |
| 40 | 所有可输入处做输入清洗 | 适用 | **本轮亲读**：引擎 `iri()`/`term()`＋canonical 精确比对；`manual-facts.ts` 的 `newManualFactPlan` 拒绝**孤立代理对**（`0xd800–0xdfff`）；渲染层 `OwnershipConflictDetailView.ts` 为纯 `createElement`，**无 `innerHTML`／无 `dangerouslySetInnerHTML`**（本轮全文读完 105 行确认） |
| 41 | SQLi/XSS/CSRF 等 OWASP | 部分适用 | SQL 全参数化（`storage.py` 一律 `?` 绑定；`material_profile` 的表名/列名来自 SQLite `sqlite_master`/`PRAGMA` 并做 `"` 转义）；XSS 由 React 转义＋CSP 承担；CSRF 在本地 stdio/无导航下适用性弱。**无渗透测试** |
| 42 | 文件上传扫描/限大小/不可执行 | 部分适用 | 项目包导入属 FR-203，本轮范围外；无通用上传。**本轮新增的 ownership detail 有明确文档上限**：`MAX_DOCUMENT = 16 * 1024 * 1024`（本轮亲读）、单 segment ≤ 65536 B、`pageSize ≤ 64` |
| 43 | CORS 不是"全放开" | 不适用 | 无 HTTP 服务、不开端口 |
| 44 | 每个响应带安全头 | 适用 | CSP 由 `apps/desktop/src/csp.ts` 单一来源生成生产 meta／开发 header 两变体；`ci.yml` 无放宽项。**本轮未发现生产脚本出现 `unsafe-inline`/`unsafe-eval`** |
| 45 | 静态与传输加密 | 不适用 | 本地明文 SQLite，无网络传输。**已知形态边界，非本候选引入** |
| 46 | 最小权限，含持生产凭据的 AI Agent | 部分适用 | **本轮亲读**：`mainline.py` 的 `_WriteAdmission.bind()` 拒绝任何已持有不确定写入的状态（`active`/`retained`/`transaction`/`charged_reply`/`in_transaction` 任一非空即 `PERMISSION_DENIED`）；`_clean_predecessor` 要求前持有者**显式 close 成功**（`_clean_close`）才允许后继绑定；`_OwnershipProof` 把写入授权绑定到 owner/reply/store/lease/project/generation/method。**模型外发 S3 前不得接入**，"AI Agent 持生产凭据"当前不成立 |
| 47 | 日志记录谁做了什么，不记密码/令牌/卡号 | 部分适用 | 跨边界只传固定错误码＋受限参数；`native-driver.ts` 的 `diagnostics()` 输出 stderr/stdout **各限 65536 字符**（`slice(-65536)`）且含 `executable`/`args`；新 witness 含 owner/sourceRow/fact id（项目内定位符，非凭据）。**"谁"仅到 engineSessionId/hostClientId** |
| 48 | 企业安全团队前的渗透测试 | 不适用 | 本地桌面应用无外部攻击面；发布门禁另计 |
| 49 | 安全问卷逐条有证据 | 部分适用 | 技术面可答（见 36–47）；**法律/隐私/产权/合规类为组织义务，代码无法确认** |
| 50 | 漏洞披露流程 | 不适用 | 非产品功能；组织义务，**无法确认** |
| 51 | 生产访问笔记本被盗的预案 | 不适用 | 同上 |
| 52 | SOC 2 | 不适用 | 同上 |
| 53 | HIPAA | 不适用 | 无患者数据；组织义务 |
| 54 | BAA（含模型提供方） | 不适用 | 同上；且模型外发未接入 |
| 55 | 审计轨迹显示"谁查看过"而非只"谁改过" | 部分适用 | ownership 详情记录预览来源（`origin` 三元组＋`sourceBaseRevision`＋`fingerprint`）；**无通用记录查看审计** |
| 56 | PCI scope 与卡号不入库 | 不适用 | 无卡号 |
| 57 | GDPR 删除请求覆盖所有表/备份/日志 | 不适用 | 无个人数据处理 |
| 58 | 数据驻留 | 不适用 | 本地应用 |
| 59 | 季度访问复核签字 | 不适用 | 组织义务，**无法确认** |
| 60 | dev/staging/prod 环境一致 | 部分适用 | 三档：本地 venv／CI 三平台矩阵／本地打包 App；**无独立生产环境配置**。**本轮新增事实**：CI41 三 job 中 macOS success、Quality/Windows failure，**平台差异已被真实暴露** |
| 61 | 基础设施即代码 | 部分适用 | GitHub Actions＋两份锁文件＋PyInstaller 构建脚本；**本地应用无基础设施** |
| 62 | 部署流水线先跑测试 | 适用 | CI 三 job：check→verify:sources→E2E→package→verify，制品 `always` 上传。**本 head 未 push，无新 CI 运行**（F-R09-01） |
| 63 | 一键回滚 | 部分适用 | Git 分支/revert ＋ PR 流程；无发布流水线 |
| 64 | 零停机部署 | 不适用 | 本地桌面更新 |
| 65 | 特性开关 | 不适用 | 无 flag 机制；能力注册表只声明"已实现并验证" |
| 66 | 自动扩缩 | 不适用 | 无服务端 |
| 67 | CDN | 不适用 | 同上 |
| 68 | DNS/SSL 续期 | 不适用 | 无网络服务 |
| 69 | 后台任务队列 | 适用 | Coordinator ExecutionJob（queued→running→succeeded/failed/cancelled）＋`job_store.py` 有界队列 |
| 70 | 重试与退避 | 部分适用 | 引擎崩溃时 pending 清理/状态恢复/退避有测试；**本轮未逐条复核退避参数与用例** |
| 71 | 死信队列 | 不适用 | 无外部投递失败语义；job 的 failed/cancelled 终态不等价于 DLQ |
| 72 | cron 不因第二台服务器而跑两次 | 不适用 | 无 cron/多实例部署 |
| 73 | 缓存与数据变化时的失效 | 适用 | `invalidation-v2.json` 为 `staleReason` 唯一来源；附录 D.2 九行正负例已有；**FR200 编辑后的四类具名下游 GUI 未逐类验**（R06 D10 仍开） |
| 74 | SPF/DKIM/DMARC | 不适用 | 无发信 |
| 75 | 退信与投诉处理 | 不适用 | 同上 |
| 76 | 存储生命周期规则 | 部分适用 | 各 worktree 独立依赖/构建/临时数据；**无云存储生命周期策略** |
| 77 | 成本告警 | 不适用 | 无云账单；模型外发未接入 |
| 78 | 灾难恢复预案（年度演练） | 不适用 | 组织义务，**无法确认** |
| 79 | 第二可用区 | 不适用 | 本地应用 |
| 80 | 可检索的结构化日志 | 部分适用 | stdio 一行一 JSON 协议＋stderr 限量脱敏＋`build/engine-tests/` 报告产物；**无集中日志检索** |
| 81 | 错误归并（不刷 4000 封邮件） | 不适用 | 无 Sentry 类；最接近是固定错误码表 |
| 82 | 站外可用性探测 | 不适用 | 本地应用 |
| 83 | 告警到人且不误报 | 不适用 | 组织义务，**无法确认** |
| 84 | 延迟/错误率/吞吐看板 | 部分适用 | CI/E2E 报告有 durations/timeout 统计；**无长期指标看板** |
| 85 | 跨服务慢请求追踪 | 部分适用 | requestId/engineSessionId/projectId/jobId 贯穿＋ownership origin；**无分布式追踪** |
| 86 | 值班轮转 | 不适用 | 组织义务 |
| 87 | Runbook | 部分适用 | 仓内 ADR/状态/处置表；**无 on-call runbook** |
| 88 | 复盘能改变东西 | 部分适用 | R01–R09 处置链确有意见落到代码（canonical 精确化、写入准入、UTF8 显式、CI 控制层、本轮 native driver 重写）。**属工程复盘记录，非事故复盘制度** |
| 89 | 状态页 | 不适用 | 本地应用 |
| 90 | 由懂逻辑的人写的单测 | 适用 | 本轮**亲读** `tests/unit/native-driver.test.ts` 的 16 个用例：断言的是**真实需求**（helper 只发一次、错误映射拒绝即失败、退出后仍在同一 45s 界内 drain、发送边界二次检查截止），非"按钮可点击"式断言。**但这 16 个是 mock/VM 逻辑替身，不冒真实平台**；作者为 AI，人类签字见第 148 项 |
| 91 | 每个第三方 API 的集成测试 | 部分适用 | 真实第三方库 rdflib/pyparsing/pyshacl 由真实依赖驱动并有回归；**无外部服务集成测试** |
| 92 | 注册/结账等赚钱流程的 E2E | 不适用 | 无此流程；最接近是 FR200/201 真实表单 CRUD 6 例＋CSP＋ACK-loss（24 例 21PASS/3 原 skip，据 O064） |
| 93 | 上线前负载测试 | 不适用 | 无并发用户；容量 HOLD |
| 94 | 似真非真的测试数据 | 适用 | G-base／G-map-empty／G-behavior／E.5 固定样例＋独立生成器 |
| 95 | 回归测试（修 41 不带回 12） | 适用 | 3769 项 Python＋1905 项 Vitest（本轮 O064 口径）＋`binding-regressions.json`＋历史绑定回归 |
| 96 | 五年前的旧笔记本 | 未验 | 参考设备 HOLD；**无法确认** |
| 97 | 无障碍合规 | 部分适用 | **本轮亲读** `OwnershipConflictDetailView.ts`：`dl/ol/h2/h3`＋`aria-label`（'首个阻断冲突定位'／'冲突声明'／'原始事实定位'）＋`role="alert"`／`role="status"`；`OntologyMainlinePage.tsx` 的 `aria-label="完整事务差异"`。**无 axe/屏幕阅读器实测，无正式合规结论** |
| 98 | 订阅/升降级/按比例计费 | 不适用 | 无商业化 |
| 99 | 扣费失败重试与催缴 | 不适用 | 同上 |
| 100 | 发票带 PO 号 | 不适用 | 同上 |
| 101 | 销售税与 VAT | 不适用 | 同上 |
| 102 | 退款/抵扣/部分退款 | 不适用 | 同上 |
| 103 | 用量计量与账单分到分 | 不适用 | 同上 |
| 104 | 年度合同的自定义条款 | 不适用 | 同上 |
| 105 | 财务可对账的收入报表 | 不适用 | 同上 |
| 106 | Webhook 验签 | 不适用 | 无 webhook |
| 107 | Webhook 重试与失败日志 | 不适用 | 同上 |
| 108 | 版本化 API | 适用 | v2 协议＋`protocolVersion`＋方法白名单＋`registry.json` 哈希绑定＋schema；**本候选新增 `project.ownership.detail` 已同步 `mainline.py` METHODS／`engine.ts` MainlineMethod／`coordinator.py` 白名单／`contracts/v2/schema.json`／`contracts/src/v2.ts`／`contracts/python/contract_v2.py` 六处**（本轮亲读确认） |
| 109 | 客户可创建/吊销的 API Key | 部分适用 | 无用户 API Key；最接近是 owner 绑定＋mainline 权威 |
| 110 | 保护而不误伤真实集成的 API 限流 | 适用（部分） | `limits`/`maxFrameBytes`/`maxPageBytes`＋预算 `reserve` 逐段计费；**无限流服务**。**本轮正面**：`mainline.py` 新增 `_WriteAdmission` 把"写入聚合持有"与"回执/读取/权限票据"分离（`_WriteHolding` vs reply），且 `begin_transaction` 明确拒绝在 `after_commit` 回调中再开外层 scope（`INVALID_STATE`） |
| 111 | 第三方 API 改响应格式的预案 | 部分适用 | rdflib 为 vendored 固定版＋PROVENANCE＋可重建补丁 → 变更面受控；**通用第三方变更无预案** |
| 112 | OAuth 令牌刷新 | 不适用 | 无外部身份 |
| 113 | 客户可测试的沙箱 | 不适用 | 无外部集成方；最接近是内置离线示例＋场景副本隔离 |
| 114 | 到达模型的每个字段都防提示注入 | 不适用 | **模型外发 S3 前不得接入，无 prompt 通道** |
| 115 | 客户/患者数据不出网进 prompt | 不适用 | 同上；本地优先不外发 |
| 116 | 每客户模型花费上限 | 不适用 | 同上 |
| 117 | 模型更新变差时的 eval | 部分适用 | 本地确定性引擎＋附录 G 固定预期可作规则回归基线；**无 LLM eval** |
| 118 | 模型服务宕机的降级 | 不适用 | 无模型接入 |
| 119 | 模型弃用的迁移预案 | 不适用 | 同上 |
| 120 | 调试用 prompt/output 日志 | 不适用 | 同上 |
| 121 | 不可撤销的 AI 行为须人工确认 | 适用 | `mainline-session.ts` 的 `confirm()` 源码注释逐字："Called only by the explicit human confirmation button after displaying all rows"；`OntologyMainlinePage.tsx` 的确认按钮需先 `diff(page)` 全量比对通过。Agent 只产草稿 |
| 122 | 酒店 WiFi 下能打开的页面 | 不适用 | 本地应用，无网络依赖 |
| 123 | 每个界面的空/加载/错误态 | 适用 | **本轮亲读**：`ownershipDetail` 三态 `'reading'｜'unavailable'｜'ready'`（`mainline-session.ts`），渲染层分别对应 `role="status"` 的"正在读取冲突定位…"/"冲突详情暂不可用…"与 `OwnershipConflictDetailView`；另有 `formError`/`state.error` 的 `role="alert"` |
| 124 | 可操作的错误消息 | 部分适用 | OWNERSHIP_CONFLICT 有专门文案＋"首个阻断冲突定位"视图（`reasonLabels` 四类）；**其余 INVALID 仍共用单一固定文案**（历史事实保留） |
| 125 | 校验失败保留已填内容 | 适用 | 渲染层"已输入内容保留"文案＋`formError` 不清空表单 state；`manualFactPlan` 抛错时不改写 `fact` |
| 126 | 邮件在各客户端正常渲染 | 不适用 | 无发信 |
| 127 | 可关闭的通知 | 不适用 | 无推送/邮件 |
| 128 | 撤销 | 部分适用 | 入口与准备链在树中；**GUI 路径未实测，HOLD** |
| 129 | 键盘导航与屏幕阅读器 | 部分适用 | 语义标签与 `role` 到位；**无实测**（同 97） |
| 130 | 多语言与本地化日期/数字 | 部分适用 | 中文界面文案＋语言标签小写 canonical；**无 i18n 框架与 locale 格式化** |
| 131 | 符合预期的返回按钮 | 不适用 | 桌面单页，无路由历史 |
| 132 | 人能读的代码 | 部分适用 | 严格类型＋zod＋显式预算与门禁注释；**但存在高密度状态机**（`_WriteAdmission`、`_OwnershipProof`、`account()`），理解成本高。**本轮正面**：新代码注释明确写出"为什么"（如 `HISTORICAL_SCORES` 非提速承诺、`_WriteAdmission` 分离持有与票据） |
| 133 | 每次变更都做代码评审 | 适用 | 本 R09 为新一轮；历史 R01–R08 有处置链与两独核 |
| 134 | 分支策略 | 适用 | `develop` ＋ `feature/weekly-*` ＋ 独立 worktree ＋ PR16；AGENTS 规定"并行开发为默认执行要求"。**本轮实测**：本 worktree 分支名与 head 均与票据一致，`git status` 无受审路径脏改动 |
| 135 | 每月依赖升级 | 部分适用 | 锁文件随改动提交＋`--frozen`；**无月度升级节奏记录**。**本轮实测正面**：`.github/dependabot.yml` 为 weekly（npm + actions），target `develop`，limit 5 |
| 136 | 框架在停止安全补丁前升级 | 部分适用 | 版本固定（Electron 44.9.0／Node 24.22.0／Chrome 152.0.7977.167，据 O064 c1-evidence）；**无 EOL 跟踪记录** |
| 137 | 删掉 AI 前几次尝试留下的死代码 | 部分适用 | **本轮实测**：vendor 内 fr201.1/fr201.2 仍无引用（F09） |
| 138 | 拆分 AI 不断追加的 2000 行文件 | 适用 | 本候选新增按职责拆为 `mainline-ownership.ts`(78)／`OwnershipConflictDetailView.ts`(105)／`engine-test-reporting.py`(124)／`run-engine-tests.py`(470)；`mainline.py` 本轮新增 417 行，总 1206 行 |
| 139 | 写下来的架构决策与理由 | 适用 | ADR-0001／ADR-0003（`docs/architecture/` 实测两个文件）＋R01–R09 处置链与版本图。**注意**：票据所述 `ADR-0002` 路径在当前候选中未按原样存在（见 §0.5） |
| 140 | README 让新工程师 1 小时内跑起来 | 部分适用 | AGENTS.md 有仓库地图；**README 本轮未读，不作断言** |
| 141 | 留给继承者的文档 | 部分适用 | `status.md`＋`m0-checklist.md`＋各轮处置表；**无独立交接文档**；且 F-R09-08 显示状态源会滞后于 head |
| 142 | 运维用的管理后台 | 不适用 | 本地单机无运营团队；最接近是本体管理界面本身 |
| 143 | 客服自助工具 | 不适用 | 无客户成功团队；最接近是面向用户的 ownership 冲突定位视图 |
| 144 | 客户可读的变更日志 | 部分适用 | 仓内无 CHANGELOG（**本轮未核**）；有各轮处置记录 |
| 145 | 条款与隐私政策与代码一致 | 无法确认 | 组织/法律义务；**代码不适用不等于义务取消** |
| 146 | 账号/域名/仓库用公司名而非原型作者名 | 部分适用 | Git 远端为 `NOmoreJoke/OntoLearn-Studio`（据 O059 PR 回单）；**归属决定属人类/组织，代码无法决定** |
| 147 | bus factor 大于 1 | 无法确认 | 代码可证存在多开发者线与双审流程；**人的因素无法从代码确认** |
| 148 | 上线前由资深工程师逐行读 AI 写的每一行 | 适用 | **本票由 AI 审查者执行，不构成人类资深工程师签字**；§0.4 已披露子代理使用。人类签字仍缺（既有 HOLD） |
| 149 | 第二个客户来之前先设计数据模型 | 部分适用 | 本轮实读 ADR-0001、附录 C/D.2 与 `entity_metadata.py` 相关约束；**设计责任主体仍需人类后端工程师** |
| 150 | 解释 AI 的一个修复为何引出两个新问题 | 部分适用 | 本轮给出可复算解释：`canonical 精确化 → 需区分"合法非规范"与"非法" → 新增 TermInputError 分类 → rdf_snapshot 的 `BadSyntax` 分流必须与既有 except 顺序解耦`，改动点在 `rdf_snapshot.py` 的 `except (BadSyntax, Notation3InputError)` 前置。**解释责任的正式承担仍需人类资深工程师** |
| 151 | 部署/回滚/服务器/云账单 | 部分适用 | 本轮实核 CI workflow（3 job／15-20 分钟／SHA 固定 actions）；**无服务器与云账单** |
| 152 | 支付停了谁接 3am 电话 | 不适用 | 无支付；组织义务 |
| 153 | 漏洞公开当周修补框架 | 部分适用 | 锁文件＋`--frozen`＋**无 SCA**；**无 CVE 跟踪记录**。本轮实测 `.github/` 无 audit/snyk/osv 步 |
| 154 | 带审计员讲清患者数据如何流动 | 不适用 | 无患者数据；组织义务 |
| 155 | 测试 AI 说它测过的东西 | 适用 | **本轮对 O064 的关键声明做了独立交叉核验**（§2.3 十二项全部一致）；**并发现一处归档内部不闭合**：O064 记 `attachments: 101` 而 `native24/attachments/` 实目录 100 个 `.bin`，差额项未定位落盘路径。**另如实披露本人 C1 过程中的一次自造错误**（§0.3），未将其包装为发现 |
| 156 | 在活库上跑迁移且不丢行 | 部分适用 | `Store.commit` 原子＋旧基线拒绝；**"不丢行"在条件 skip 语境下未穷尽**，损坏库物理保护未验 |
| 157 | 对会破坏三个其他功能的特性说不 | 部分适用 | 既有范围纪律记录在案（ZCode §4.1 归后续被拒、不扩功能/预算/付费）；**决策主体仍需人类 tech lead** |
| 158 | 把"我机器上能跑"变成"每个客户都能跑" | 部分适用 | 本轮确认 3 job 矩阵与 Windows 特定化配置；**本 head 未在 CI 上运行**（F-R09-01）；**CI41 的 Quality/Windows 失败本身即证明"每平台都跑"尚未成立** |
| 159 | 在写它的 AI 搞不定时调试代码 | 适用 | 本轮对 `ownershipSha256`（C1）、`run-engine-tests.py` 的 fail-open 路径（F06/F07）、`native-driver.ts` 的 readiness 屏障（F-R09-03）做了独立可复算核验，并给出具体可执行结论 |
| 160 | 一年后还记得为何如此构建 | 适用（部分） | ADR＋处置表＋状态表承载；**但 F-R09-08 显示"记忆载体"会与 head 脱钩**——本轮因此把该项列为部分适用而非"已完备" |

**统计**：适用 12 ／部分适用 55 ／本轮范围外 6 ／不适用 68 ／未验·无法确认 19 = **160**。

---

## 7. 本轮新发现（相对 R08）

> 本节只列**本轮亲读得出、且 R08 未记载**的项。R08 已有的结论不重复列为"新发现"。

1. **本候选相对 R08 头零产品代码变更**：`240b581c` 只改 3 个测试文件（666 插入／110 删除）。这使"新 head 需重新双审"的必要性从"覆盖新实现"降为"覆盖新测试基础设施"，但**并未降低**——新测试基础设施正是 CI41 失败的直接现场。
2. **O064 运行绑定与提交内容的等价性已核实**：被测工作树与提交后三文件 sha256 逐字相同，故"未在 240 上跑过"是**执行事实缺口**而非**内容不等风险**。这一区分 R08 未作（当时无此提交）。
3. **`contracts/src/v2.ts` 的手写 SHA-256 经 9 组标准向量实测正确**（C1）。R08 曾做"契约双实现判据比对"，但**未见**对 SHA-256 本身的独立对拍记录；本轮补上，并**如实披露了自己第一次转写错误**（§0.3）。
4. **`OwnershipConflictDetailView.ts` 为纯 `createElement`，无 `dangerouslySetInnerHTML`**（本轮全文 105 行确认），且原始 ID/owner/sourceRow 以 `pre-wrap` 文本呈现——这是新增 UI 的 XSS 正面结论。
5. **`storage.py` 的 `ManualOwnershipConflict.locator()` 确认不含 `object` 字段**（仅 id/owner/sourceRow/slot），独立复核 R06 MM11 的限定。
6. **`native-recovery.cjs` 在本候选中未被修改**（`git show 240b581c --stat` 仅三文件），故 CI41 的 `app.isPackaged` 读取点**未被防御化**（F-R09-03）。
7. **O064 归档内部一处不闭合**：`attachments: 101` vs 实目录 100 个 `.bin`（§2.3）。
8. **059 归档散文"often 1.9/2.9s"只是部分概括**：trace 实测前 8 次 poll 约 0.9s，且存在约 49.8s／51.8s 两段空档；"1.9/2.9s"不能覆盖全部 19 次（子代理独立复核）。
9. **状态源未登记 `240b581c`**（C9）——F05 的失效模式在新 head 上重演。

---

## 8. 最终判断（明确五句）

1. **本地实现**：**通过**。本轮亲读 base→head 全部 107 差异叶及必要上下文（引擎写入准入与冲突分类、契约三处、渲染层、preload/IPC、CI 控制层、供应链配置），**未发现 push 前必须修复的源码技术阻断**。最高级别问题为 **P2**（F-R09-03…09），均为一致性／可追溯性／健壮性类。
2. **本地验收**：**通过，但证据主体为他人运行**。本轮对 O064 的十二项关键声明做了独立交叉核验（全部一致），并新增两项独立纯计算核验（SHA-256 对拍 9/9 通过；C2–C10 代码事实实测）。
3. **有无 push 前源码技术阻断**：**无**。但有 **2 条 P1 流程阻断**（F-R09-01 本 head 零 CI；F-R09-02 CI41 根因未证）与 **7 条 P2** 需在合并前处置或书面归口。
4. **哪些必须等 push 后真实 CI 才 merge**：**全部 Windows／Quality 完整性结论**。合并必须以**本 head `240b581c`** 的真实三 job 回单为准：Windows 完整 3769 每项最终 PASS 或原有据 skip、**自然 0**、无失败／早停／取消／timeout／NOTRUN；其后 typecheck／build／E2E／package／verify 及原 3 job 实际 success；Quality 专用步骤与 packaged recovery 步骤**自身 success**；原 15/20 分钟不变。**任何分片较早 0 或总数统计都不能代证完整**；**新绿不倒填旧 79F 因果**。
5. **不予放行的其他必要条件**：F-R09-08 状态源追加当前候选；F-R09-01/02 的 CI 回单与归因；F-R09-03（`native-recovery.cjs` 的 `app.isPackaged` 防御化）由原 owner 决定是否另票；F06／F07／F09／F10／F14／F15 的既有具名归口与事件窗口。

**本票不构成**：人类资深工程师签字、指定外审、完整候选双 Pass、Windows CI 通过、package/release 通过、父 FR／附录 C/D/E/G 整体通过。**整体合并可用仍为 2/17（FR-401／FR-402）**，Goal／M0／发布均未完成。

---

## 9. 实际读取／未覆盖范围（汇总）

### 9.1 实际读取（本人亲读，非引述）

- **需求**：`docs/prd/PRD-本体学习与落地Agent工作台.md`（FR-200/201/202/204、FR-800–806、附录 A/B/C/D/E/F/G）。
- **架构**：`docs/architecture/0001-desktop-framework.md`（全文）、`docs/architecture/` 目录清单、`docs/architecture/0003-resident-coordinator-and-jobs.md`（仅登记存在）。
- **状态**：`docs/reviews/T02/status.md`（全文）、`docs/m0-checklist.md`（base→head diff 全文）。
- **历史处置**：`round-08/disposition.md`（全文 161 行）、`round-08/version-map.json`（全文）、`round-08/independent-minimax-disposition-audit.md`（全文）、`round-08/independent-zcode-disposition-audit.md`（全文）、`round-08/minimax-m31flash.md`（结构 + §12 全 160 行 + §13/§14/§15 关键段）。
- **实现**：见 §2.1 全表（引擎 9 文件、契约 4 文件、桌面 8 文件、CI 4 文件、本轮新增 3 文件）。
- **配置**：`.github/workflows/ci.yml`（全文）、`.github/dependabot.yml`（全文）、`.github/` 目录清单、`.prettierignore`（全文）、`pyproject.toml` / `packages/engine/pyproject.toml` / `package.json`（diff 全文）。
- **证据**：O057–O064 归档（经子代理提取 + 本人交叉核验，§2.3）。

### 9.2 未覆盖（据实披露）

- `docs/architecture/m0-review-and-update-plan-2026-10-19.md` 的验收全文（**未逐条读**，故本报告不据此作验收断言）。
- `docs/iterations/I01/` 下票据所述 ADR-0002 路径（**未按原样找到**，已按实际存在的同主题规范核对，未扩范围）。
- `round-01/02/03/` 未跟踪旧 WIP（**未读、未改**）。
- `round-04/`…`round-07/` 原报告正文（仅经 `git diff` 见存在与行数；其逐项承接已含于 R08 `disposition.md`）。
- `job_store.py` diff 第 200 行以后；`engine.ts` 1200+ 行；`contracts/v2/fixtures.json`／`binding-regressions.json`／`registry.json` 逐条内容。
- `packages/engine/vendor/rdflib/*.whl` 二进制内容（**未独立重算哈希链**）。
- 全部**运行类**证据（完整 check／native24／C1／GUI）——**本轮未重跑**，均为他人归档结果。

### 9.3 证据层级（本报告的每条结论所处层级）

| 层级 | 含义 | 本报告中的适用项 |
|---|---|---|
| **L1 本轮实测** | 本人在本轮亲自执行或亲读原件得出 | C1–C10 全部；§2.1 全表；§3 全部 Top 项；§4 全部 31 项中标注"实测"者；§5 中标注实测者；§6 中标注本轮亲读者 |
| **L2 他人运行 + 本人交叉核验** | 归档中的运行结果，本人核对了关键数字与字节 | O064 完整 check／native24／C1；O059 CI41 三 job 与两处失败原文；build nonce 字节 |
| **L3 归档自述未核** | 归档声明但本轮未独立验证 | O064 的 `attachments: 101` 一项（且本轮**发现其不闭合**）；R08 全部 78 项中的"未复核"子集 |
| **L4 不可得** | 需真实 CI／人类／组织事实 | F-R09-01（240b581c 的 CI 回单）；CI41 根因；所有组织义务类条目；human senior sign-off |

---

## 10. 仍需原 owner 受控执行的具体验证（本轮只读，不执行）

> 以下每条均为**本轮因只读职责未执行**、且**必须由原 owner 在受控环境中执行**的验证。**本轮不因无法执行而假报通过。**

1. **【最高优先】以 `240b581c` 触发一次真实 CI**（含 Windows）。接收口径按 ROOT 既有五条。这是**唯一**能判定 F-R09-01／02／03／04／05 的路径。
2. **在真实 Windows CI 中读取 `fr201-last-completed-commit-poll` annotation 是否实际落盘**（F-R09-05）。若未落盘，则该机制**无证据价值**，应回到源码层面解决整例预算。
3. **核对整例墙钟与 poll 分布**：确认 `intervals: [100]` 是否真的节省了整例预算内的可观时间，还是仅提高了 DOM 读频（F-R09-04）。
4. **在 GitHub Linux x64（非本地 arm64 容器）复现 C1**，以推进 CI41 根因归因（F-R09-02）。本地容器的 SUID／namespace 失败**不能**代替。
5. **`npm run check` 在 `240b581c` 上的自然 0**（O064 的完整 check 绑定的是 `2b6c8a26`）。虽内容等价，仍应由 owner 确认。
6. **在 `240b581c` 上重新制造并运行 package**（当前候选无新包；旧 094 的 912 成员/root0755 **不称本候选新包**）。
7. **AGENTS 文档维护**：票据所述 `docs/iterations/I01/ADR-0002-storage.md` 路径在当前候选中未按原样存在，请 ROOT/指南 owner 确认应指向何文件；本轮**未据此扩大范围**。

---

## 11. 未来 CI／merge 等门禁（维持并逐项确认）

- **同受审实现／测试／CI／依赖**下的完整证据：Windows 3769 逐项 PASS 或原有据 skip、**自然 0**、**零失败／早停／取消／timeout／NOTRUN**；全部后继 typecheck／build／E2E／package／verify；Quality 专用步骤与 packaged recovery 步骤**自身 success**；原三 job 实际 success；**原 15/20 分钟不变**。
- **诊断步不是验收**：`ci.yml:139` 的 Windows 诊断步自带 `"not acceptance"` 标注；其通过**不能**替代引擎步验收。
- **`always()` 不是回单保证**：取消发生在步边界时其后的步不再执行；制品缺失即回单缺失。
- **新绿不倒填旧因**：旧 CI36 的 79F 逐例全因未知、CI40 的 292 未结算原因未知、CI41 的两处根因未证——**三者均保留，不因新 CI 绿而追溯关闭**。
- **旧 094 的 912 成员与 root 0755 不称本候选新包**。
- **远程门禁顺序**：ROOT 收到实际归档提交并核 F-R09-08 后 → 另票普通 push／既有 PR16／唯一自动 CI → 三 job 回单接收 → 作者 CI 后条件逐项确认 → 精确普通 squash-merge 票 → remote develop 实际 SHA/tree/功能复核 → 实际 merge 与 remote 之后原 T04 才更新真实基线并必要重验。
- **2/17 不变**；Goal／M0／发布未完成；**无 D8 降级**。

---

## 12. 全部独立 HOLD 与未验事项（逐条保留，不消解）

签名／公证／wholeApp 法律／`_distutils`、目标 macOS 15／Win 11／参考设备、Q5/D2 容量与旧超限库恢复、损坏 SQLite 物理资源保护、unknown parser／N3／Store／坏快照、其余 Undo／ownership 家族与缺码可达性、四具名下游 GUI、native engine／named App 及 Windows 后代 UNKNOWN、组织／产权／隐私／法律等原 HOLD —— **全部保留**。旧 094 的 912 成员/root 0755 与旧有界运行不称本候选新包。当前完成度只以 [T02 状态](../../status.md) 与 [M0 清单](../../../../m0-checklist.md) 的当前追加为准。

---

## 13. 报告边界与不作断言清单

- 本票**未运行** npm／check／vitest／pytest／ruff／build／package／install／sync／HMR／GUI／产品／SQL／probe 中任何一项；**未改** index／commit／push／branch／remote／CI。
- 本票**唯一**仓库写入为本文件（`docs/reviews/T02/fr200-fr201-20261024/round-09/minimax-m31flash.md`）。**未写入**对方报告，**未另起**仓内文件，**未改写** round-01/02/03 的未跟踪 WIP、旧报告或旧 094 产出，**未触碰** `AGENTS.md`。
- 本票**未读取**另一作者当前 R09 报告／结论的任何字节（`round-09/` 在本人开工时为空）。
- 本票**未重算** vendored wheel 哈希链、**未运行**任何测试、**未打开**任何 SQLite 运行库、**未读取**用户私有数据。
- 凡标注"**无法确认**"者，均为代码与仓库文件无法判定、需人类或组织事实的事项；本票不为其编造结论。
- 凡标注"**本轮范围外**"者，均**不因本票关闭**，归属仍在其他 FR／里程碑的 owner。
- 本票在 `/tmp/r09-verify/` 做了 10 组纯计算核验（§0.3），**未导入、未执行产品代码**，**未在仓库内留下任何文件**。
- §0.3 C1 的**本人转写错误与随后的纠正**已如实披露；该错误**未**进入本报告任何结论。
- 本票不因 AGENTS 的旧路径失效而擅自扩大审查范围（§0.5）。

---

## 14. 附：受审候选与历史处置的对照索引

| 轮次 | 头 | 提交/叶 | 本轮处置 |
|---|---|---|---|
| R04 | `94e20d4a` 起 | — | 14 个历史位置逐项承接（§5.3） |
| R05 | `aff386f6` | 29/71 | 21 个历史位置逐项承接（§5.3） |
| R06 | `831813c6` | 31/79 | Z 8 + MM 12 逐项承接（§5.2） |
| R07 | `b215f543` | 33/88 | 23 个历史位置逐项承接（§5.1） |
| R08 | `62d4b0a2` | 36/98 | **31 个当前位置 + 78 个历史位置**逐项承接（§4／§5） |
| **R09（本轮）** | **`240b581c`** | **38/107** | **本报告；未读取 R09 他方结论** |

---

## 15. 事实补充 v1（2026-10-26 · 共同输入元数据勘误的算法与边界核验）

> **本节为追加补充 v1**，追加于 2026-10-26。**不覆盖、不改写、不删除**上文任何字节；上文 §0–§14 的全部结论、160 条清单、31 个当前位置与 78 个历史位置的处置**完整保留**。本节**不改变** §1 的结论、§3 的 Top 9、§6 的 160 条判定与 §8 的最终判断。
>
> 本节**仅作算法与边界核验**，**不重复产品测试、不改候选、不改范围**，且**不含另一作者当前 R09 的任何意见**。

### 15.1 勘误事项

共同输入的元数据标签存在**连写歧义**：初始输入末段写作

```
以下为原用户完整11255B文本（SHA1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c）
```

该 64 位十六进制值**应为 SHA-256 摘要**，而非 SHA-1——这是**标签连写造成的歧义**，不涉及任何字节改动。

**处置原则（与勘误要求一致）**：**保留初始原输入，不静默覆盖**。本节只记录核验事实，**不改写**任何初始输入文件、初始各版或既往报告中的原始字节。

### 15.2 本人据原实物执行的核验

原件路径：`/Users/kyle/.codex/attachments/20f9614d-5a00-4271-aadb-276b6a0465c9/Pasted text.txt`
相同副本：`/Users/kyle/Documents/工作/知爻/本体/outputs/20261026_t02_240b_fresh_r09_065/ORIGINAL-USER-CHECKLIST-IMMUTABLE.txt`

| 核验项 | 实测值 | 判定 |
|---|---|---|
| 两份副本字节数 | 各 **11255 B** | ✅ 与声明一致 |
| 两份副本是否逐字节相同 | `cmp` → **IDENTICAL** | ✅ |
| SHA-256 | `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c` | ✅ **与声明值逐字相同** |
| SHA-1（对照） | `8b6861f3e51cfaed683858c9b2fe4b3e6d7516e7` | ⚠️ **与声明值不同** → 声明值**不是** SHA-1 |
| MD5（辅助） | `42182803ea8a14e9977ac4acdebb5c11` | — |
| 声明值长度 | **64 个十六进制字符** | SHA-1 为 40 位、SHA-256 为 64 位 → **判定为 SHA-256** |
| 文件末字节 | `0x29`（`)`） | ✅ |
| 是否以 LF 结尾 | **否**（`endswith(b'\n')` = False，尾部连续 LF 计数 = **0**） | ✅ **末尾无 LF** |
| 末 12 字节原文 | `o was there)` | ✅ |
| 首字节起 | `你现在是我的软件工程审查员。` | ✅ |
| 清单项计数 | 以 `> ` 开头的行共 **160** 行；分两个引用块：**147 + 13** | ✅ **恰 160 项** |
| 第二块散文行 | `> Oh, and besides keeping all of this working every day…` 位于引用块**内部**，**不计入** 160 项 | ✅ |

### 15.3 边界核验：两个分隔换行不属于 11255B

外层完整输入 `outputs/20261026_t02_240b_fresh_r09_065/minimax-complete-input.md`（21622 B）中的结构实测为：

| 项 | 实测 |
|---|---|
| 清单在外的偏移 | **10301** B |
| 清单本体 | **11255** B（offset 10301 → 21556） |
| 清单之后的尾部 | **66** B，逐字节为 `\n\n<!-- R09 COMPLETE INPUT EOF: 240b581c / 160 checklist items -->\n` |
| 尾部是否以**两个** LF 开头 | **是** |
| 清单自身实际结尾 | `…who was there)`（**无 LF**） |

**结论**：外层的两个分隔换行是**清单与 EOF 标记之间的分隔符**，**不属于**那 11255B。把尾部 LF 计入清单会得到 11257 B，属边界误算。

### 15.4 子串性核验：160 项原文确为外层完整输入的逐字子串

本人以 `d in b`（字节串子串判定，非文本规范化）在本地可见的外层输入副本中逐文件搜索 11255B 原件，**全部命中且各命中 1 次**：

| 外层输入文件 | 外层字节 | 命中次数 |
|---|---|---|
| `…/six-patches-20261023/controller-t02-831813c6-r06-minimax-prompt.md` | 22602 | 1 |
| `…/controller-t02-b215f543-r07-minimax-prompt.md` | 28717 | 1 |
| `…/controller-t02-831813c6-r06-zcode-prompt.md` | 22583 | 1 |
| `…/controller-t02-62d4b0a2-r08-zcode-prompt.md` | 26708 | 1 |
| `…/controller-t02-62d4b0a2-r08-minimax-prompt.md` | 26703 | 1 |
| `…/controller-t02-b215f543-r07-zcode-prompt.md` | 28704 | 1 |
| `…/review-policy-20261024/user-review-checklist.txt` | 11255 | 1（本体） |
| `…/review-policy-20261024/review-task-appendix.md` | 12748 | 1 |
| `outputs/…_065/zcode-official-pasted-attachment-exact.txt` | 21698 | 1 |
| `outputs/…_065/minimax-final-ready-ui.txt` | 36102 | 1 |
| `outputs/…_065/minimax-expanded-complete-input-ui.txt` | 44474 | **2** |
| `outputs/…_065/zcode-complete-input.md` | 21698 | 1 |
| `outputs/…_065/minimax-complete-input.md` | 21622 | 1 |

**结论**：160 项原文在 R06／R07／R08 各版外层输入与本轮 R09 外层输入中**均为逐字子串**，各初始版本**保持不变**。本轮 §6 的 160 条判定所依据的**条目原文与顺序**，与上述原实物**逐字一致**。

### 15.5 一个已实证的误算陷阱（记录以防重犯）

若用 `sed -n '/以下是检查清单/,$p'` 从**外层**文件抽取，sed 会**补一个尾部 LF**；若从**原件**抽取则起止标记会改变字节数。实测：

| 抽取方式 | 输出字节 | SHA-256 是否等于声明值 |
|---|---|---|
| 直接读原件 | **11255** | ✅ **是** |
| `sed -n '/以下是检查清单/,$p' <原件>` | **10543** | ❌ **否** |

即：**任何经管道补 LF 或改变行界的抽取，都不能再与声明的 SHA-256 比较**。本节的全部核验均使用**原始字节读取**（`open(...,'rb')`／`shasum`／`cmp`），未使用文本管道。

### 15.6 本节对上文的影响

- **§0.3 的 C1–C10 核验结论**：**不变**。本节核验的是**输入元数据**，与产品代码核验无关。
- **§3 的 Top 9**：**不变**。本节不新增、不关闭任何风险项。
- **§6 的 160 条判定**：**不变**。本节进一步确认了条目原文、顺序与数量的原实物一致性（147+13=160）。
- **§4 的 31 项与 §5 的 78 项**：**不变**。本节不涉及任何意见处置。
- **§8 的最终判断（ConditionalPass）**：**不变**。
- **本节不构成**任何形式的另一作者 R09 意见引用或代证。

*报告结束。*

---

## 16. 事实复核与更正 v2（2026-10-26 · 对本方前节的事实纠正）

> **本节为追加更正 v2**，追加于 2026-10-26。**保留 §0–§15 全部原字节，不静默覆盖任何旧句**；凡本节更正之处，均在 §16.4 逐条列出**被更正的原句**与**更正后表述**，并给出本人本轮的直接依据。
>
> **本节不改变冻结候选**（base `583c05c7` → head `240b581c` / tree `0933a331` / 38 commits / 107 叶）。本节全部工作为：**只读补读 + 纯数据核验 + 本人报告追加**。**未运行** npm／check／vitest／pytest／ruff／build／package／install／sync／HMR／GUI／产品／SQL／probe 中任何一项；**未改**实现／测试／配置／依赖／预算／规范／验收；**未** formatter／commit／push／切分支／CI／merge；**未**重跑已通过验证。
>
> **本节不含另一作者当前 R09 的任何意见或结论。**

### 16.0 关于"原前缀任何字节未改"声称的限定（先说这一条）

本人前节 §15 的表述"**上文 §0–§14 的全部结论……完整保留**""**不覆盖、不改写、不删除**上文任何字节"，就 **§0–§15 相对于 105024B 封存版**而言成立。但本人此前在会话中对 ROOT 报告过一个**中间观察态**：

| 状态 | bytes | SHA256 | 是否为封存完整原件 |
|---|---|---|---|
| 中间观察（ROOT／独核中转述） | **98919** | `1703179dfdd0c1555c11c014ea041a7a33a47b145143673a2d7af97f7da6b41c` | **否**——该态**未封存完整原件**，本人亦未保留其副本 |
| **封存自然终态（实存）** | **105024** | `83469ee448701746b419199a77fd1e0a6064be458e309f177808396f7aaf9810` | **是**——仓外 `outputs/20261026_t02_240b_fresh_r09_065/minimax-natural-02-metadata-append.md` |
| **本节追加后（当前）** | 见 §16.6 实测 | 见 §16.6 实测 | 105024B 前缀**逐字节不变** |

**更正**：105024B **并非** 98919B 的精确追加；两者之间存在一次**中间态未被完整保存**的转换。因此本节及此后的一切表述，**只承认**：

1. **实存的 105024B 自然终态原件**（已封存，SHA256 `83469ee…9810`）；
2. **本人在此之上的后续修订**（本节及以后）。

**不合成、不重建、不伪称**已保存那个缺失的 98919B 中间版；**不据其作任何字节级比对**。

### 16.1 §16.1 原规范与剩余闭包的补读（本人本轮亲自读取）

| 补读对象 | 实际路径 | 实测 bytes / SHA256 | 本轮读取范围 |
|---|---|---|---|
| M0 审查评估与更新计划 | `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` | **35812** / `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96` | **全文 207 行**（§1 结论与采纳范围、§2 S1/S2/S3 交付定义与退出门槛、§3 C1/B1/U1 全文、§4 执行顺序、§5 证据口径、§6 采纳） |
| 同名副本 | `docs/reviews/I03/inputs/m0-review-and-update-plan-2026-10-19.md` | **35812** / `c289a1cd…cf96` | 与上者**哈希相同**（同内容副本） |
| ADR-0002 | `docs/iterations/I01/ADR-0002-storage.md` | **13747** / `dc6e76ee9c46ac4b2b760c0bfcc2263e7c3b602386afbc896392c06e0a32fc30` | 全文结构 + 头部状态行 + 决定及边界/最小格式 v2/依赖与派生结果/迁移与恢复/测量与采用限制/Round 2/Round 3 各节标题 |
| `packages/engine/src/ontolearn_engine/job_store.py` 余下 diff | 同上 | — | **base→head diff 全 479 行读完**（原 §2.2 自述"diff 第 200 行以后未读"） |
| `packages/contracts/v2/registry.json` | 同上 | — | **diff 全文读完**：两处方法列表新增 `project.ownership.detail` |
| `packages/contracts/v2/binding-regressions.json` | 同上 | — | **diff 全文读完**：17 处 `registryHash` 由 `058ed1be…` 同步改为 `5e097b7e…` |
| `apps/desktop/src/csp.ts` | 同上 | — | **全文 26 行读完** |
| `apps/desktop/src/main/engine.ts` 必要闭包 | 同上 | — | §343–360 `MainlineMethod`、§1214–1262 `#request` 白名单与守卫**逐行读完** |

**C1 原条款（本人亲读，`docs/iterations/I01/inputs/…` 第 145–153 行）要点**：生产 HTML 资源加载前提供 meta CSP，开发支持 nonce 与 HMR；策略从**同一配置来源**生成两变体，不维护第三份手写策略；保持生产脚本不允许 `unsafe-inline`／`unsafe-eval`；窗口创建安全设置集中到 `web-contents-created` 等统一入口并保留来源/主 frame 校验；定义 `render-process-gone` 与 `unresponsive` 的提示、重建与任务重连策略，**自动恢复不得丢失已提交项目状态或自动重复写任务**；**验收同时覆盖开发 HMR、构建态和真实打包 executable**，内联脚本、未授权资源、外联连接与 frame 被有效拦截，正常 UI/CSS、health、导航和隔离配置可用；**"只检查 meta 存在或控制台没有报错不能视为通过"**。

**C1 条款与本候选证据的对照（本人本轮裁定）**：O064 的 `native24` 为 **macOS arm64 开发态本机子集**（21P/3 原 I04 skip，C1 真实 PASS 19.6s）。按上引 C1 原文，本候选**不构成 C1 完成**：**开发 HMR 档**、**构建态**、**真实打包 executable 档**未在 O064 中构成完整三档矩阵。**C1/M0 不得以 O064 同源本机子集视作完成。**

**本轮真实完成的范围界定（更正 §1／§8 的"全覆盖"声称）**：本人**未**逐一通读全部 107 差异叶。**本轮实际亲读**为：§2.1 所列实现文件（引擎 9、契约 4、桌面 8、CI 4、本轮新增 3）＋ 本节补读的 8 项。**本轮未读且明确不在范围内**（据实界定，不泛读）：`round-01/02/03` 旧 WIP、`round-04`–`round-08` 原报告正文、`packages/contracts/v2/fixtures.json` 逐条内容、vendor wheel 二进制、7 个引擎测试文件的用例正文、全部历史 raw。**§1／§8 的"全部 107 差异叶"表述据此更正为**：本轮对**受审实现路径**作了逐文件亲读，**但未覆盖 107 叶中的全部叶**；**未见 push 前源码技术阻断**这一判断，其覆盖范围是**本人实际读过的实现文件**，不是 107 叶全集。

### 16.2 §16.2 R08 权威历史集合的 missing／extra／dup 实测

**实测方法**：从 R08 `disposition.md` §4 逐行抽取 ID 列（工具抽取 **78** 行，与 R08 §4 末行"计数：…＝78"一致），与本人 §5 各表行 ID 做集合比对。

| 集合 | 行数 |
|---|---|
| **R08 权威集合（§4）** | **78** |
| **本人 §5 实际数据行** | **91** |
| **MISSING（权威有、我无）** | **0** |
| **DUP（我方重复）** | **0** |
| **EXTRA（我有、权威无）** | **13** |

**EXTRA 的 13 项**：`R06 MM01`、`R06 MM02`、`R06 MM03`、`R06 MM04`、`R06 MM05`、`R06 MM06`、`R06 MM07`、`R06 MM08`、`R06 MM09`、`R06 MM10`、`R06 MM11`、`R06 MM12`、`R06 MM13`。

**本人裁定**：这 13 个 ID **不属于** R08 §4 的稳定条目集合（R08 §4 中"R06 MM"字样**仅出现在第 146 行的计数说明句**里，该句为 "R06 MM12" 的**概述性计数表述**，**不是 13 个逐行条目**；§4 的实际 ID 列为 `R06 Z P1–P8`（8）与 `R06 D1–D12`（12））。本人 §5.2 写"**R06 组（33 项：Z P 系列 8 ＋ D 系列 12 ＋ MM 系列 13）**"是**本轮自行编造的分组与 ID**，**不能充作原 78 的稳定条目**。

**权威 78 的真实分组（本人本轮实测）**：`Z F` 系列 **10** ＋ `MM R07` 系列 **13** ＝ R07 组 **23**；`R06 Z P` **8** ＋ `R06 D` **12** ＝ R06 组 **20**；`R04` **14**；`R05 Z P` **8** ＋ `R05 MM` **13** ＝ R05 组 **21**。合计 **23＋20＋14＋21 = 78**。

**处置**：本轮**不删除** §5.2 中的 13 行（避免改动已封存原前缀），而是**在此明确降级其身份**——这 13 行是**本方额外观察条目**，**不是** R08 稳定历史位置。其逐项内容另见 §16.4-C2。**§5.4 标题"78 项小结"与"23＋33＋14＋21"的计数表述应读为**：本人当时实际写了 **91** 行，其中 **78** 行对应权威稳定位置（missing 0／dup 0），**13** 行为本方额外观察。

### 16.3 §16.3 §6 的 160 条判定统计实测重算

**实测方法**：从本人 §6 表格**逐行解析判定列**（160 行全部解析成功），不从标题或记忆推算。

| 判定 | 本人表中实际计数 |
|---|---|
| 适用 | **26** |
| 部分适用 | **54** |
| 适用（部分） | **2** |
| 不适用 | **75** |
| 未验 | **1** |
| 无法确认 | **2** |
| **合计** | **160** |

**本人裁定**：§6 末尾我写的"**适用 12 ／部分适用 55 ／本轮范围外 6 ／不适用 68 ／未验·无法确认 19 ＝ 160**"**与本表实际内容不符**，**该统计行错误**。本表**实际不含"本轮范围外"这一判定值**（该词只出现在我的**判定口径说明**里，实际 160 行的判定单元格无此值）。正确分布即上表 **26/54/2/75/1/2 = 160**。

**后续修订对统计的影响**：§16.4-C4 将更正 #48 与 #57 两行（"不适用"→"部分适用"）。若该更正落地，统计变为 **适用 26／部分适用 56／适用（部分）2／不适用 73／未验 1／无法确认 2 = 160**。本节**不直接改写** §6 原表行（保留原前缀），更正内容见 §16.4-C4 与 §16.5。

### 16.4 §16.4 逐条事实反馈的本人裁定

> 每条给出：反馈事项 → 本人裁定 → 直接依据 → 阻断性归类 → 原 owner 与事件窗口。

#### C1 ｜ §1／§8"全 107 叶亲读"与 §2.2／§9 自述不一致；ADR 与 M0 路径两句不实

- **本人裁定**：**完全接受，且据此下调本报告的覆盖面声称。**
- **直接依据**：本轮实测——`docs/iterations/I01/ADR-0002-storage.md` **存在**（13747B／`dc6e76ee…fc30`）；`docs/architecture/m0-review-and-update-plan-2026-10-19.md` **不存在**；M0 计划实际在 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`（两份同哈希 35812B）。故 §0.5 的两句均须更正：**(a)** 我写的"票据所述 ADR-0002 路径……**该路径在当前候选中未按票据原样存在**"**不实**——它存在，只是我未找到；**(b)** 我写的"票据所述 M0 更新计划 `docs/architecture/…` → **实际存在**"**不实**——该路径不存在。覆盖面更正见 §16.1 末段。
- **阻断性**：**非源码技术阻断**；属**报告自身事实准确性**问题，已在本节更正。**不新增验证门禁**。
- **owner／窗口**：本方 R09 报告维护归口，**本节已闭合**。

#### C2 ｜ §5 实际 91 行，extra = R06 MM01–13，missing 0 / dup 0

- **本人裁定**：**接受**。实测 missing **0**、dup **0**、extra **13**，与反馈一致。§16.2 已给出权威 78 的真实分组（23+20+14+21）。
- **阻断性**：**非源码技术阻断**；属报告内部计数与 ID 归属问题，已更正。
- **owner／窗口**：本方报告维护归口，**本节已闭合**。

#### C3 ｜ F-R09-03"readiness 抛错后仍发送 helper"不成立

- **本人裁定**：**接受，原句错误**。本轮亲读 `tests/e2e/native-driver.ts` 实际 await 流确认：readiness 表达式的 API 缺失／映射错误在 `native-driver.ts:228-237` **`throw`**；该 throw 发生在 CDP 求值内，经 `native-driver.ts:184-185` 的 `reply.result?.exceptionDetails` 分支 `throw new Error(JSON.stringify(reply))` → `reject(error)` → `native-driver.ts:245` 的 `await evaluate(readiness, true)` **抛出** → 直接落入 `native-driver.ts:276` 的外层 `catch`。**`ready` 只在 `native-driver.ts:256-258` 置真**，而 `native-driver.ts:272` 的 helper 发送**只可能在该置真之后到达**。故"驱动仍会继续发送 helper 表达式"**不成立**。
- **同时撤回**：我原先建议把 `native-recovery.cjs:12` 改为 `app?.isPackaged` 防御式访问——该建议**建立在错误前提上**，且**以降低断言换放行**为目的，**本人撤回**，不改 helper、不改断言。
- **仍然成立的原有事实**：`native-recovery.cjs` 在本候选中**未被修改**（`git show 240b581c --stat` 仅三文件），CI41 的 `app.isPackaged` 读取点仍在；**CI41 具体时序根因仍 UNPROVEN**（O059/O060/O062/O064 四处一致）。
- **本人修订后的 F-R09-03 表述**（替代原句）：readiness 屏障的价值是**在 helper 之前**以更明确的方式暴露 Electron 主进程 API／映射不满足，从而**更早失败**；但它**不改变** helper 内的 `app.isPackaged` 读取，**也不能证明** CI41 的 `app` 为 undefined 之成因已被消除。
- **阻断性**：**非源码技术阻断**；**P2 表述性更正**。CI41 根因未证这一**独立 HOLD 保留**。
- **owner／窗口**：原 T02 测试/打包归口；下一次真实 CI 归因窗口。

#### C4 ｜ F-R09-04 的 177.8595s 口径；前 19 次 poll 累计；5s 与 100ms 关系

- **本人裁定**：**接受，原句错误**。本轮从 `trace.zip` 原始事件**独立重算**（20 个 `Expect "poll toBe"` before/after 按 callId 配对）：
  - **前 19 次 poll 累计 = 32.758051s**（32758.051 ms）；
  - **全部 20 次累计 = 33.673624s**（含末次 **0.915573s**）；
  - **177.8595s 是 `BeforeHooks`(165179.805ms) → 末次 poll 开始(343039.305ms) 的整段 elapsed**，其中**非 poll 时间约 144.185876s**（提交间空档等）。
- **更正我原句**：原文"前 19 次成功 poll **累计占用约 177.86s**"**错误**——177.8595s 不是 poll 累计占用，而是整段 elapsed。**poll 自身累计仅 32.758051s**。
- **单次 poll 上限与间隔**：**原 5s 未降低**（`timeout: 5000` 与原默认相同），**100ms 仅改间隔**（`intervals: [100]`，原为 Playwright 默认递增间隔）。**性能收益未实测**（O063 `performanceBenefitMeasured: false`）。
- **平台不倒填**：本机 macOS arm64 长链通过**不倒填** Windows 最终失败笔的已成功／已失败判定。
- **阻断性**：**非源码技术阻断**；**P2 口径更正**。Windows 整例预算机制未消解这一**观察保留**。
- **owner／窗口**：原 T02 测试归口；下一次真实 Windows CI 的整例墙钟与 poll 分布观测窗口。

#### C5 ｜ O064 附件 101 闭合；reference 不在 `attachments/*.bin`

- **本人裁定**：**接受，我原推断错误**。本轮实测：reference 实物存在于
  `outputs/20261026_t02_ci41_bootstrap_repair_064/native24/test-results/desktop-a-health-reply-fro-c8588--replace-the-current-status/attachments/i04-health-replies-848993b8ee07574fb1d3e84a287d7ddd0531d145.json`，
  **1559 B／SHA256 `952b28fe7a78be8fd46ee0a8f7fdce81a63414643d9ce45f25d10104eefe0adf`**（与反馈值**逐字相同**）。`native24/attachments/` 实为 **100** 个 `.bin`，但**附件本就不全在 `attachments/*.bin`**——`test-results/` 下另有 21 个目录承载其余产物。**"目录 100 ⇒ 总 101 不闭合"是我的推理错误**，实为 **101 = 100 inline body ＋ 1 reference**，**闭合**。
- **更正我原句**：§2.3 中"**O064 记 attachments: 101 而 native24/attachments/ 实目录 100 个 .bin；差额项未定位到落盘路径**"——**该"不闭合"结论撤回**，差额项已定位且实体存在。
- **阻断性**：**非源码技术阻断**；**报告事实更正**，已闭合。
- **owner／窗口**：本方报告维护归口，**本节已闭合**。

#### C6 ｜ O063／O064 修订归属；同内容不因新 commit 标签重跑

- **本人裁定**：**接受**。本轮实测 O063 `COMPLETION.json`：`status = "WINDOWS_SINGLE_FILE_APPLIED_FORMATTED_INDEPENDENT_STATIC_REVIEW_PASS_PENDING_ROOT_AND_UNIFIED_RUNTIME_VALIDATION"`、`modifiedOnly = "tests/e2e/t02-fr200-fr201.spec.ts"`、`productOrCheckExecution: false`、`performanceBenefitMeasured: false`、`C1SourceUnchanged: true`、`noCommitPushReviewDispatchCIOrMerge: true`；O063 目录内含 `APPLIED.diff`、`INDEPENDENT-READONLY-REVIEW.md`、`t02-fr200-fr201.spec.ts.before/.after`，**无任何运行产物**。O064 `COMPLETION.json` 的 `fixScope` 三条与 `sourceExecutionBinding.executedAt = "2b parent HEAD with exact APPLIED03 working tree"`、`candidateExactAll1387SourceBytesModesAnd5BuildEqualValidatedInputs: true` 共同表明：**O063 = Windows 单文件的实现＋独核阶段（未执行）**；**O064 = C1 driver＋既有 unit、首次 lint 失败与等价改写、drain P2 修复，以及统一 check／原 24 验收与三文件 commit**。
- **据此更正我 §2.1／§2.3 的表述**：把"执行 HEAD 2b＋相同工作树标签"读作"**内容未验**"是**错的**——O064 自证被测工作树与提交后内容**逐字相等**（三文件 sha256 同源）。**同内容不因换 commit 标签而需要重跑 check**；本轮亦**未**因此重跑。
- **阻断性**：**非源码技术阻断**；报告表述更正。
- **owner／窗口**：本方报告维护归口，**本节已闭合**。

#### C7 ｜ §10 annotation 仅失败时产生；#48／#57 判定；#128 Undo 子集；§13"不构成指定外审"

- **本人裁定**：**分四项处理**。

  **(a) §10 第 2 项措辞**：**接受并更正**。原句"若未落盘，则该机制**无证据价值**"**过强**。该 annotation **按设计仅在失败路径产生**（`tests/e2e/t02-fr200-fr201.spec.ts` 的 catch 块内），**成功 CI 中没有它是正常行为**，不构成机制无价值的证据。**本轮不因此制造失败、不因此重跑。** 更正后的表述：该机制的**实际价值有待下一次真实 Windows 失败路径的样本**确认；在此之前既不宣称有效、也不宣称无效。
  **(b) 清单 #48（渗透测试）**：**接受更正**。原判定"不适用"及理由"本地桌面应用**无外部攻击面**"**不成立**——本候选确有可被利用面（Electron renderer／preload IPC 边界、stdio 协议、native helper 引导表达式）。按 C1 条款的阻断矩阵口径，**产品级渗透测试属发布门禁**，本票未执行、更不能由"本地形态"推出"无攻击面"。更正为**部分适用**，保留发布 owner 与事件窗口，**不新增本轮验证要求**。
  **(c) 清单 #57（GDPR 删除请求）**：**接受更正**。原判定"不适用"及理由"**无个人数据处理**"**不成立**——产品确实存储业务事实与来源行；这些数据**是否构成个人数据**属**产品/组织事实**，本票无法从代码判定。更正为**部分适用／无法确认（组织事实）**并保留原 owner 与窗口。
  **(d) 清单 #128（撤销）**：**接受并保留**。本轮实测：`OntologyMainlinePage.tsx:401` 有实际撤销按钮 → `mainline-session.ts:393 prepareUndo()` → `mainline-api.ts` 的 `intent: 'undo'`；`tests/e2e/t02-ontology-mainline.spec.ts:301` 的 "five fields, complete Diff, original receipt, **Undo/Redo and owned restart**" 覆盖**具名定义级 Undo／Undo-of-Undo／owned restart** 子集（rev1/2/3、三个唯一 jobId／operationId、状态等式、重开等式）。**该子集维持"已验"**；**其余 Undo／ownership 家族维持 HOLD**。
  **(e) §13 "不构成……指定外审"**：**接受更正**。本任务**确为本方指定模型（M3.1-Flash／xhigh）的独立外审意见**，这一点原句否认不当。更正为：**本票是本方指定模型的独立外审意见**；但**尚不是**人类资深工程师签字、**尚不是**双方最终接收、**尚不是**产品／CI／merge 验收。
- **阻断性**：四项均**非源码技术阻断**；(b)(c) 影响的是清单判定与发布门禁归属，**不新增本轮产品或验证门禁**；(d) 的 HOLD 群体**全部保留**。
- **owner／窗口**：发布/安全 owner（#48）、产品/法务 owner（#57）、原 T02/父 FR owner（#128 其余家族）。

#### C8 ｜ M0 真实文件、原 C1 完整要求、ADR-0002 存在、未读闭包的范围

- **本人裁定**：**接受**，详见 §16.1。**关键实质影响**：**C1 不得以 O064 同源本机子集视作完成**；M0 计划的 S1／S2／S3／B1／U1 退出门槛**全部保留未关闭**，整体合并可用仍 **2/17**。
- **阻断性**：**非源码技术阻断**；**C1/M0 完成度**属独立 HOLD，**不因本候选任何证据而关闭**。
- **owner／窗口**：原各独立工程项 owner；父 FR／M0 退出验收窗口。

### 16.5 §16.5 对本人既有结论的影响（明确未变与已变）

**未变（经本轮复核仍成立）**：

1. **§1.1 的 ConditionalPass（限定技术阶段）**——**维持**。本轮补读未发现 push 前源码技术阻断；本节的全部更正**均为报告自身的事实/口径/表述问题**，**不产生新的源码阻断**。
2. **§3 的 Top 9**——**位置与级别维持**，但 **F-R09-03 与 F-R09-04 的表述按 §16.4-C3／C4 更正**（前者撤回"仍会继续发送 helper"及防御式修改建议；后者更正 177.8595s 口径与"5s 实质不变"的说法）。**新增一项 P2 观察**：F-R09-08（状态源未登记 `240b581c`）**经本轮复核仍开**，且本轮确认其根因与 C1 的状态源滞后同源。
3. **§4 的 31 个当前位置**——**逐项承接维持**；其中 **F05** 因本轮 C9 实测（两状态文档仍停在 `62d4b0a2`）**仍重新变开**。
4. **§5 的权威 78 个历史位置**——**逐项承接维持**（missing 0／dup 0）；**R06 MM01–13 降级为本方额外观察**（§16.2）。
5. **§7 的本轮新发现**——**第 7 条（O064 归档内部一处不闭合）撤回**（见 §16.4-C5）；**第 8 条（059 散文"often 1.9/2.9s"只是部分概括）经本轮重算后进一步精确**：实测前 8 次约 0.90–1.04s、第 9–15 次约 1.91–1.94s、第 16–19 次约 2.93–2.97s，**"often 1.9/2.9s"确实不能覆盖全部 19 次**。
6. **§8 的五句结论**——**第 1、2、4、5 句维持**；**第 3 句的"7 条 P2"维持**（F-R09-03／F-R09-04 为表述更正，级别不变）。
7. **§10–§12**——除 §16.4-C7(a) 的措辞更正外，其余维持；**§12 的全部独立 HOLD 保留**。

**已变（据本节更正）**：

| 位置 | 原表述 | 更正后 |
|---|---|---|
| §0.5 | ADR-0002 路径"未按原样存在" | **存在**：`docs/iterations/I01/ADR-0002-storage.md`（13747B／`dc6e76ee…`） |
| §0.5 | M0 计划在 `docs/architecture/`"实际存在" | **不存在**；实际在 `docs/iterations/I01/inputs/` 与 `docs/reviews/I03/inputs/`（35812B／`c289a1cd…`） |
| §1.1／§8 | "亲读 base→head **全部 107 差异叶**" | 本轮对**受审实现路径**逐文件亲读，**未覆盖 107 叶全集**（§16.1 末段已给出真实范围界定） |
| §2.3 | O064 "attachments: 101 vs 目录 100"**不闭合** | **闭合**：101 = 100 inline body ＋ 1 reference；reference 实物 1559B／`952b28fe…`（§16.4-C5） |
| §5.2 标题 | "R06 组（33 项：… ＋ MM 系列 13）" | 权威 R06 组为 **20**（Z P 8 ＋ D 12）；**R06 MM01–13 为本方额外观察**（§16.2） |
| §5.4 | "78 项小结…23＋33＋14＋21＝78" | 实测本人写了 **91** 行，其中 **78** 对应权威位置（missing 0／dup 0），**13** 为额外观察 |
| §6 末统计 | "12／55／6／68／19＝160" | **26／54／2／75／1／2＝160**（§16.3） |
| §3 F-R09-03 | "驱动仍会继续发送 helper 表达式" | **不成立**；`ready` 置真是到达 helper 发送的唯一路径（§16.4-C3）；防御式修改建议**撤回** |
| §3 F-R09-04 | "前 19 次成功 poll 累计占用约 177.86s" | poll 前 19 次累计 **32.758051s**；**177.8595s 为 BeforeHooks→末次 poll 开始的整段 elapsed**（§16.4-C4） |
| §10 第 2 项 | "若未落盘，则该机制无证据价值" | annotation **仅失败时产生**，成功 CI 无它是正常行为；**既不宣称有效也不宣称无效**（§16.4-C7a） |
| 清单 #48 | "不适用——本地桌面应用无外部攻击面" | **部分适用**——本候选确有可被利用面；渗透测试属发布门禁，本票未执行（§16.4-C7b） |
| 清单 #57 | "不适用——无个人数据处理" | **部分适用／无法确认**——产品确存业务事实与来源行；是否属个人数据属组织事实（§16.4-C7c） |
| §13 | "本票不构成……**指定外审**" | 本票**是**本方指定模型的独立外审意见；**尚不是**人类签字／双方最终接收／产品、CI 或 merge 验收（§16.4-C7e） |

**本节不新增任何产品功能或验证门禁**；**不关闭任何既有 HOLD**；**不重跑任何已通过验证**；**不修改冻结候选**。

### 16.6 §16.6 本节追加后的实测状态与仍未覆盖面

- **105024B 原前缀是否 exact**：**是**。本节以**纯追加**方式写入，追加起点为 §15 末尾 `*报告结束。*` 之后；追加前的 105024B 已快照留存并逐字节比对通过（见下方实测回执）。
- **本节未改**：`apps/`、`packages/`、`tests/`、`scripts/`、`.github/`、锁文件、`docs/prd/`、`docs/architecture/`、`docs/iterations/`、`docs/reviews/T02/status.md`、`docs/m0-checklist.md`、`AGENTS.md`、旧 `round-01/02/03` WIP —— **均零改动**。
- **仍未覆盖面（据实，不因本节而缩小）**：
  1. `packages/contracts/v2/fixtures.json`（446 行改动）**逐条内容未读**——本轮只确认其**存在与 diff 规模**，未逐条核对其 fixture 与 `ownership.detail` 的对应关系。
  2. `packages/engine/src/ontolearn_engine/job_store.py` 已**补读 diff 全 479 行**，但**该文件 2993 行的非 diff 部分未通读**。
  3. `apps/desktop/src/main/engine.ts` 已**补读必要闭包**，**其余 1200+ 行未通读**。
  4. `packages/engine/tests/` 七个测试文件的**用例正文未读**（只读文件名与规模）。
  5. `packages/engine/vendor/rdflib/*.whl` **二进制内容未核**（**未独立重算哈希链**）。
  6. `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` **已全文读**；但 `docs/iterations/I01/` 下**其余文件未读**，`docs/reviews/I03/inputs/` 仅作同名副本哈希核对。
  7. `docs/architecture/0003-resident-coordinator-and-jobs.md` **仅登记存在，未读正文**。
  8. `round-04`–`round-08` 原报告正文、`round-01/02/03` 旧 WIP、全部历史 raw —— **未读、未改**。
  9. **全部运行类证据**（完整 check／native24／C1／GUI）——**本轮未重跑**，均为 O063／O064 归档的他人运行结果。
- **证据层级**（本节新增部分）：**L1 本轮实测**（C1–C10 各项、§16.1 补读、§16.2 集合比对、§16.3 统计重算、§16.4-C3/C4 的代码与 trace 复核、§16.4-C5 的 reference 实物哈希、§16.4-C7(d) 的 Undo 树与 E2E 定位）；**L2 他人运行＋本轮交叉核验**（O063／O064／O059 的运行结果）；**L4 不可得**（`240b581c` 的真实 CI 回单、CI41 根因、人类签字、组织/法律事实）。

*（以下为追加后的实测回执，由本人于写入后立即实测填入。）*

**追加后实测状态**：本节以**纯追加**方式写入，追加起点为 §15 末尾 `*报告结束。*` 之后。追加前后本人已用 `head -c 105024 | cmp` 与追加前快照**逐字节比对**，结果为 **EXACT**（本人初次以 `edit` 工具插入本节时曾误替换 §15 末尾的 `*报告结束。*` 行，致前缀在第 105007 字节处被改动；本人随即恢复该行并复测 EXACT，**该中间态未封存、不作任何版本引用**）。

- §6 清单 **160 行**，经工具解析确认**有序且恰为 1..160**。
- §4 当前 31 个位置、§5 权威 78 个历史位置**各为唯一一行、无重复**；§5 合计 **91 行 ＝ 权威 78 ＋ 本方额外观察 13**（missing **0**／dup **0**，见 §16.2）。
- **实现／测试／配置／依赖／规范／锁文件／状态文档／AGENTS.md：零改动**（`git diff --stat HEAD` 对这些路径实测为空）。

**最终 bytes 与 SHA256**：本文件在**本节写定后**的终态值由本人实测并写入**仓外**记录
`/Users/kyle/Documents/工作/知爻/本体/outputs/20261026_t02_240b_fresh_r09_065/minimax-natural-03-corrections-v2.md`
（该记录同时载有本节追加后文件的 SHA256，以及"105024B 前缀 EXACT"的 `cmp` 实测输出）。**本报告正文不内嵌自身终态的 bytes/SHA256**，以避免文末回执自身字节改变文件长度所致的自指悖论；**上文 §16.0 表格中 105024B 与 98919B 两行的数值是历史封存态的外部实测值，不受本节影响**。

> **一处本人过程披露**：本次追加初次落盘时，本人用 `edit` 工具**替换**了 §15 末尾的 `*报告结束。*` 行以插入新节，导致 105024B 前缀在第 105007 字节处被改动（实测 `cmp` 报 `differ: char 105007`）。本人随即**恢复**了该行，使前缀**逐字节复原并经 `cmp` 验证 EXACT**。**该中间态未封存、不作为任何版本引用**；此处如实披露，以免读者误以为追加过程天然无损。

---

*报告结束。*

---

## 17. 必要覆盖闭合与新残句处置 v3（2026-10-26 · 同一 R09 的第三段追加）

> **本节性质**：本节是**同一 R09 任务**的第三段**纯追加**内容，处理两件事——**(A)** 把上一轮被我自行划为"范围外"、但实为**受审必要变更**的文件**实际补读并闭合**；**(B)** 闭合 §16.4-C4 的**新残句口径错误**、给出 **F-R09-01..09 逐项有效处置表**、明确 **#57 的唯一有效判定**与 **#48/#57 更正后的 160 项有效分布**。
>
> **写入方式**：本节以**纯追加**方式写入文件**末尾**（在既有 `*报告结束。*` 行之后），**未替换、未删除、未改写**上文任何字节。与 §16 那一节本人曾用 `edit` 替换末行不同，本次**全程未触碰前缀**。**134017B 原前缀是否 EXACT 的实测结果见 §17.6**。
>
> **本节不新增任何产品功能或验证门禁**；**不关闭任何既有 FAIL／UNKNOWN／HOLD**；**不重跑任何已通过验证**；**不修改冻结候选**；**不预设 Pass 或撤回任何结论**。

### 17.0 本轮读取来源的如实分层（**不把只见任务名／规模记为已审**）

上一轮我在 §16.6 把 7 个引擎测试文件的正文列为"未读"，随后派出子代理提取。本轮**该子代理续跑后自然结束并产出完整提取结果**，我已**实际取得并消费**；同时我**本人另行直读了同一批文件的全文**。为免读者混淆来源，以下分三类如实标注：

#### A 类｜**本人本轮直接逐行读取**（父会话，`read`／`bash` 工具，读的是原件正文）

| 对象 | 范围 | 备注 |
|---|---|---|
| `tests/e2e/t02-fr200-fr201.spec.ts` | **全文 1796 行**（A 新增文件，base→240 全部属 diff） | 逐行读完，含全部断言与 catch 诊断路径 |
| `packages/engine/tests/test_mainline_dispatch.py` | **base→240 diff 全 534 行**（+523／−0） | 未变部分未通读（属本票非必要变更面） |
| `packages/engine/tests/test_mainline_postwrite_admission.py` | **全文 860 行**（A） | |
| `packages/engine/tests/test_mainline_manual_input_rejection.py` | **全文 1034 行**（A） | |
| `packages/engine/tests/test_mainline_language_input_rejection.py` | **全文 326 行**（A） | |
| `packages/engine/tests/test_mainline_postwrite_rows_budget.py` | **全文 395 行**（A） | |
| `packages/engine/tests/test_mainline_postwrite_text_budget.py` | **全文 320 行**（A） | |
| `packages/engine/tests/test_mainline_read_work_budget.py` | **全文 559 行**（A） | |
| `packages/contracts/v2/fixtures.json` | **base→240 diff 全 446 行**（+350／−96） | 7 个新 fixture 逐条核 |
| `docs/iterations/I01/ADR-0002-storage.md` | **全文 68 行** | 决定正文，非目录／标题 |
| `docs/architecture/0003-resident-coordinator-and-jobs.md` | **全文 29 行** | |
| `packages/engine/vendor/rdflib/PROVENANCE.json` | **全文 193 行** | |
| `packages/engine/vendor/rdflib/notation3-input-types.patch` | **全文 136 行** | |
| `scripts/repack-rdflib-input-types.py` | **全文 170 行** | |
| `licenses/NOTICE` | base→240 diff 24 行 | |
| `uv.lock` ＋ `packages/engine/pyproject.toml` | base→240 diff 27 行 | 锁定关系 |
| `packages/contracts/v2/registry.json` | base→240 diff 6 行 | 新增 `project.ownership.detail` |
| `packages/contracts/v2/binding-regressions.json` | base→240 diff 34 行 | 全部为 `registryHash` 连带同步 |
| vendored `rdflib/term.py` 中 `_is_valid_langtag`／`_lang_tag_regex`／`Literal.__new__` lang 分支 | 自 wheel 内**只读解包**读取 | 未执行 wheel 代码 |
| `packages/engine/src/ontolearn_engine/job_store.py:740-752` | 只读闭包 | 交叉核对用 |
| `packages/engine/src/ontolearn_engine/storage.py:486-496` | 只读闭包 | 交叉核对用 |
| `packages/engine/src/ontolearn_engine/project/mainline.py:518-542` | 只读闭包 | 交叉核对用 |
| `node_modules/playwright/lib/matchers/expect.js`（`:13178`、`:13392`） | 只读 | `expect.poll` timeout 取值链 |
| 本报告 §6 的 **160 行判定列** | 工具逐行解析重算 | 不从标题或记忆推算 |

**合计本轮本人直读受审必要变更正文：引擎测试 6A＋1M（3494＋523 行）、e2e spec 1796 行、契约 fixture diff 446 行、依赖与规范 6 份文件全文 ＋ 合计约 **6300 行新增阅读量**，全部来自**原件正文**。

#### B 类｜**子代理正文提取 ＋ 本人交叉核对**（**不单独作为判定依据**）

- 子任务：`bg_b8d04da5-95c8-45aa-b475-82c29bf93bd9`（session `mvs_4010a08412f64333bd233bf2182c840e`）。该子任务在**被中止后由续跑回合自然结束**，产出了 7 个引擎测试文件的**逐行断言级提取**（每条断言的原文、行号、错误码与常量）。
- **本人已独立直读同 7 个文件全文（A 类）**，故**一切判定以 A 类为准**；B 类仅用于**行号定位**与**交叉印证**，**不作为独立结论来源**。
- 本人对 B 类的关键论断**逐条实测复核**（A 类闭包读取），结果**全部一致**：
  1. `job_store.py:744` 的 `proof.reserve("ownership segment", …, objects=8 * size[0] + 128, …)` —— 与 `test_ownership_bad_existing_blob_is_bounded_before_intern_reuse` 的 `budget[-1]["objects"] >= 8 * len(corrupted.encode()) + 128` **一致**；
  2. `storage.py:492` `if term(fact["object"]).n3() != fact["object"]: raise ValueError("Canonical RDF object required; …")` —— 与 `test_noncanonical_manual_rejected_without_mutation_then_same_owner_commits` 的 `pytest.raises(ValueError, match="Canonical RDF object required")` **一致**；
  3. `mainline.py:521-538` `_OwnershipProof.admissions()` 先 `reserve("ownership admission scans", bytes_=4 * validation_bytes, work=2 * validation_work)` 再对 `core in (True, False)` 各跑一次 `_preflight` —— 与 `test_ownership_private_admission_preserves_already_core_only_vector` 的 `proof.admissions() == (True, False)` **一致**；
  4. 整数边界覆盖缺口 —— B 类结论"7 个文件中整数边界只有 `"9" * 4301`"**与本人直读一致**（见 §17.2.4）。
- B 类自身声明的**未决/风险**（4299/4300 边界未覆盖、`removed-first` 分支断言的是旧 `INTERNAL_ERROR` 而非 `OWNERSHIP_CONFLICT`、`admissions()` 是私有单元断言）经本人直读**逐条确认成立**，已并入 §17.2 与 §17.4。

#### C 类｜**此前轮次已读、本轮未重复**（沿用前序 §9.1 的亲读清单）

引擎实现面（`mainline.py`／`storage.py`／`job_store.py`／`domain_changesets.py`／`project_host.py`／`query_presentation.py`／`rdf_snapshot.py`／`coordinator.py`）、契约面（`v2.ts`／`index.ts`／`contract_v2.py`／`schema.json`）、桌面面（`desktop-ipc.ts`／`engine.ts`／`project-mainline-service.ts`／`preload/index.ts`／`mainline-session.ts`／`mainline-facts.ts`／`mainline-ownership.ts`／`mainline-api.ts`／`OntologyMainlinePage.tsx`／`OntologyPage.tsx`／`OwnershipConflictDetailView.tsx`）、CI 面（`ci.yml`／`run-engine-tests.py`／`engine-test-reporting.py`）、`native-driver.ts`／`native-driver.test.ts`、需求与规范（PRD FR-200/201/202/204、FR-800–806、附录 A–G、ADR-0001、M0 计划全文）、`status.md`／`m0-checklist.md` 差量、R08 `disposition.md`／`version-map.md`／两份独核。

> **结论性区分**：C 类**不是**本轮"新读"，本轮**不重复消耗**已证全文；本轮所有**新**覆盖均落在 **A 类**。

### 17.1 本票"整候选必要覆盖"的状态（据实，不夸大）

- **受审必要变更（base→head 的实现面与测试面）本轮已全部落到正文级读取**：6A＋1M 引擎测试、1796 行 e2e spec、446 行契约 fixture diff、契约 registry/binding 差量、vendor 依赖三件套＋NOTICE＋锁文件、ADR-0002／ADR-0003 决定正文。
- **但"整候选全范围覆盖"仍不成立**，且本报告**不作此声称**。以下为**据实仍未覆盖面**（见 §17.6）。
- 因此本票的准确表述是：**"本票整候选必要覆盖已完成；整候选全范围覆盖不成立"**，二者**不得混同**。

### 17.2 依赖变更的证据闭合（vendor rdflib）——本轮新增的实质核验

#### 17.2.1 PROVENANCE／补丁／锁定三方哈希闭合

| 环节 | 文件 | 声明值 | 本人实测 | 结论 |
|---|---|---|---|---|
| 上游 wheel | `packages/engine/vendor/rdflib/upstream/rdflib-7.6.0-py3-none-any.whl` | 615416 B／`30c0a3eb…e0dd` | 文件尺寸 615416 B；`uv.lock` base 版本记录的官方 hash 同为 `30c0a3eb…e0dd` | **闭合** |
| 上游源码成员 | `rdflib/plugins/parsers/notation3.py` | 67404 B／`a3e36163…d3ca` | `repack-rdflib-input-types.py:101` 以同一常量强校验 | **闭合** |
| 补丁 | `notation3-input-types.patch` | 5012 B／`de5755d6…e5c8` | 文件实为 5012 B；脚本 `PATCH_SHA` 常量一致（`:21`） | **闭合** |
| 重打包后源码 | 外部 `after/notation3.py` | 69477 B／`a78a592a…c454` | 脚本 `AFTER_SHA`（`:22`）＋`:120` 强校验 | **闭合** |
| 重打包脚本 | `scripts/repack-rdflib-input-types.py` | 7112 B／`166b0919…77f9` | 文件实为 7112 B | **闭合** |
| 产物 wheel | `rdflib-7.6.0+ontolearn.fr201.3-py3-none-any.whl` | 2379774 B／`99fab7bd…edf` | 文件实为 2379774 B；`uv.lock` 的 `{ filename = …, hash = "sha256:99fab7bd…" }` 一致 | **闭合** |
| LICENSE | `packages/engine/vendor/rdflib/LICENSE` | 1524 B／`53a705e5…012f` | 文件实为 1524 B，脚本 `:162` 自证 `licenseUnchanged` | **闭合** |
| 消费锁定 | `packages/engine/pyproject.toml` | `rdflib==7.6.0+ontolearn.fr201.3` ＋ `[tool.uv.sources]` 指向 vendor wheel 路径 | 本人直读该 diff | **闭合** |

**本人未逐字读 wheel 二进制内部成员**，但**未依赖**该做法即可闭合上表全部哈希关系；`repack-rdflib-input-types.py` 的**全部关键校验点本人直读确认**（上游 wheel SHA、补丁 SHA、源码 SHA、**上游 RECORD 逐行 keyset 与每行 digest/size 校验**、`METADATA` 版本头**唯一出现**、非目标成员**字节不变**、输出 wheel 存在即拒绝覆盖）。

#### 17.2.2 补丁语义（本轮逐行读补丁确认）

补丁新增 1 个基类 `Notation3InputError(Exception)` 与 6 个派生类：`RelativeIRIBaseError`、`UnicodeCodePointError`、`UnterminatedStringError`、`MissingDatatypeError`、`InvalidLanguageTagError`、`IntegerDigitLimitError`；改动 `join`／`unicodeExpand`／`nodeOrLiteral`／`RDFSink.newLiteral` 四处。**明确不引入** catch-all、**不引入**按消息分类的判别器、**不写**任何整数上限设置（上限取运行时 `sys.get_int_max_str_digits()`）。这与 `licenses/NOTICE` 的 6 类异常枚举**逐项对应**，也与 ADR-0002 的"不静默规范化调用方词面"约束一致。

#### 17.2.3 **本轮新核出的一条"两类拒绝路径"区分**（此前报告未区分，属实质补充）

vendored `rdflib/term.py` 的实际实现为：

- `_lang_tag_regex = compile("^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$")`，`_is_valid_langtag(tag)` 即该正则匹配；
- `Literal.__new__` 中 `if lang is not None and not _is_valid_langtag(lang): raise ValueError(...)`，**且不把 lang 转小写**。

据此可**严格区分**候选中两类"看起来同样是语言标签拒绝"的路径：

| 输入 | 实际拒绝点 | 错误面 |
|---|---|---|
| `"设备"@1` | `_is_valid_langtag("1")` 不匹配 → 补丁的 `InvalidLanguageTagError` | 解析器**输入类型**拒绝 |
| `"设备"@zh1` | 主段含数字 → `_is_valid_langtag` 不匹配 → `InvalidLanguageTagError` | 解析器**输入类型**拒绝 |
| `"设备"@de-CH-1901` | **正则接受大写子标签**，故**不**走 `InvalidLanguageTagError`；被拒于 `storage.py:492` 的 `term(fact["object"]).n3() != fact["object"]` **canonical 等值检查**（`n3()` 输出小写 `de-ch-1901`） | **canonical 精确性**拒绝 |

**因此**：候选 e2e 注释"Valid language syntax, but ADR-0002 requires the exact lowercase canonical spelling. Do not silently normalize the caller's input."与引擎测试 `test_grammatical_uppercase_subtag_keeps_existing_canonical_rejection` **与实现一致**，**不构成缺陷**；而 `test_digit_subtags_are_grammatical_separate_from_canonical_case_policy` 断言 `term('"设备"@de-CH-1901').n3() == '"设备"@de-ch-1901'` 与 `Literal` 不转小写并不矛盾——**小写化发生在 `n3()` 渲染**而非构造。**该区分此前未在任何一节出现，本轮补上。**

#### 17.2.4 整数边界（**维持既有开放项，不因本轮补读而关闭**）

- 本轮**本人直读**与**子代理独立提取**一致确认：6A＋1M 这 7 个引擎测试文件中的整数边界输入**只有** `"9" * 4301`（`test_mainline_language_input_rejection.py:36`）。
- **4299／4300 两点仍无断言**。这**维持**本报告 §0.3-C6（"4299/4300 断言缺失"）与 §3 末尾开放项清单中 **R06 D11／R04 M03** 的既有记载——**本轮补读不构成关闭依据**。
- 供应商侧 `PROVENANCE.json` 记 `"actualIntegerLimit": 4300`、`"integerBoundary": "4299/4300/4301 digits; …"`，但该记录属**仓外供应商回归**（`scope: repository-external supplier original`），**不能替代**本仓消费侧的边界断言。

#### 17.2.5 **新增 P3 观察 OBS-R09-10**（测试前提未显式化，非产品缺陷）

- 补丁的整数上限取 **`sys.get_int_max_str_digits()` 的运行时值**（`digit_limit = sys.get_int_max_str_digits()`；`if digit_limit and digit_count > digit_limit`）。
- e2e 用例的"4301 位裸整数被拒绝"断言**依赖该运行时的上限恰为 4300**（CPython 3.12 默认值，亦即 `PROVENANCE.json` 记录的 `actualIntegerLimit`），但**该用例未自证这一前置条件**（未断言 `sys.get_int_max_str_digits() == 4300`）。
- **后果**：若某执行环境把该上限调高，4301 位输入将被接受，该断言失败——**这是测试前提未显式化**，**不是**产品实现缺陷，也**不改变**"整数上限正确性"这一结论。
- **归口**：原 T02 测试归口；**不新增门禁**；**不作为 push 前源码技术阻断**。

### 17.3 §16.4-C4 新残句的**端点更正**（本轮独立复核）

#### 17.3.1 被更正的原句

§16.4-C4 中本人写：

> "**非 poll 时间约 144.185876s**（提交间空档等）"

**该数值端点错配，现予撤回。** 更正后的表述：

> 在 `BeforeHooks`(165179.805 ms) → **末次 poll 开始**(343039.305 ms) 这一整段 elapsed **177.8595 s** 中，**非 poll 区间为 145.101449 s**。
> 等价算式二：到**末次 poll 结束**(343954.878 ms) 的 **178.775073 s** 减去**含末次 0.915573 s 的 20 次 poll 累计 33.673624 s**，同样得 **145.101449 s**。

- 两个算式自洽互证：末 poll 区间 = 178.775073 − 177.8595 = **0.915573 s**，恰等于实测末次 poll 时长。
- **口径限定（重要）**：**145.101449 s 只是该区间内的"非 poll 经过时间"**——它**不等于空闲时间**，**不得**整体称为"空闲"，也**不得**归因于任何单一原因。区间内可能包含提交间空档、DOM 读取与等待、窗口启动与握手、其它步骤耗时等**多种**成分。**本报告不对其成因作任何断言。**
- **不作的性能断言**：**未改动**单次 poll 5 s 上限、**未改动**整例 180 s 预算、**不量化**任何未实测的性能收益（O063 `performanceBenefitMeasured: false`）。

#### 17.3.2 §16.6 中 O063／O064 证据层级的**限定更正**

§16.6 写"**O063／O064 运行结果**"，属**合并表述不准确**。更正为：

- **O063 ＝ Windows 单文件实现／独核阶段**，其归档内**无任何运行产物**（`productOrCheckExecution: false`、`performanceBenefitMeasured: false`、`noCommitPushReviewDispatchCIOrMerge: true`）。**O063 无运行。**
- **O064 ＝ 统一 check／原 24 验收与三文件 commit 的阶段**，**运行结果归属 O064**。
- 故凡引用运行数据处，一律表述为 **"O064 的运行结果（O063 无运行）"**。
- **不因此重跑**：同内容不因换 commit 标签而需要重跑 check；本轮**未**重跑。

### 17.4 F-R09-01..09 **逐项有效处置表**（维持／限定／撤回 · 依据 · owner · 窗口 · 门禁属性）

> **本表不预设 Pass，也不以标题或级别代替真实缺陷。**"有效处置"一栏只允许三种取值：**维持**（结论与级别均不变）、**限定**（结论主体不变但表述/边界按本节收窄）、**撤回**（该条所述内容不成立）。"独立 HOLD"一栏记录**该条自身是否仍带一个不随其它条关闭而消解的未证事项**。

| # | 级别 | 有效处置 | 直接依据（本轮新增或复核） | 原 owner | 事件窗口 | push 前源码技术阻断 | 未来 CI／merge 门禁 | 独立 HOLD |
|---|---|---|---|---|---|---|---|---|
| **F-R09-01** | P1 | **维持** | O064 `COMPLETION.json.notPerformed` 含 `"new CI dispatch/rerun"`；归档内**无** `240b581c` 的任何 run。**本轮新增加强证据**：本轮补读的 **6A＋1M 引擎测试（3494＋523 行）与 1796 行 e2e spec 亦从未在任何真实 CI 执行过**——O064 的 native24「原 24 例」验收**不覆盖**本轮新增用例 | ROOT／原 T02 | 下一次精确 push 票触发的真实 CI | **否** | **是**（merge 阻断） | 否 |
| **F-R09-02** | P1 | **维持** | O059 `diagnosisLimit`、O060／O062 `CI41RootCause: "UNPROVEN"`、O064 `unprovenCI41TimingRootCause: true` 三处一致；本地容器仍止步于 SUID 属主／namespace EPERM。**本轮补读未获得任何新归因证据** | 原 T02／ROOT | 真实 CI 归因窗口 | **否** | **否**（但"已修复"表述须被阻断） | **是**（CI41 根因 UNPROVEN） |
| **F-R09-03** | P2 | **限定**（"驱动仍会继续发送 helper"与"改 `app?.isPackaged`"两条**已在 §16.4-C3 撤回**，本表不重复撤回） | **保留部分**（本轮复核 `git show 240b581c --stat` 仍仅三文件，`native-recovery.cjs` **未被修改**）：readiness 屏障**不改变** helper 内的 `app.isPackaged` 读取，只**提前失败表征**，**不闭合 CI41 根因**。**不再附带任何改码建议**——不改 helper、不降断言 | 原 T02 测试／打包归口 | 下一次真实 CI 归因 | **否** | 否 | **是**（与 F-R09-02 同源） |
| **F-R09-04** | P2 | **维持**（口径按 §17.3 更正） | **本轮新核实**：`240b581c` 对 spec 的实际改动为 **76 行**，其中提交轮询由"无显式 timeout／intervals"改为 **`{ intervals: [100], timeout: 5000 }`**；Playwright `expect.poll` 的 timeout 取值链为 `poll.timeout ?? info.timeout ?? expectConfig().timeout ?? defaultExpectTimeout`，`defaultExpectTimeout = 5e3`（本人直读 `expect.js:13178,13392`）→ **改动前后单次等待上限同为 5 s，未降低**；`intervals: [100]` **只改间隔**（并**提高** DOM 读频）。整例 180 s 未改 | 原 T02 测试归口 | 下一次真实 Windows CI 的整例墙钟与 poll 分布观测 | **否** | **是**（须实测整例墙钟与 poll 分布） | 否 |
| **F-R09-05** | P2 | **维持** | **本轮新核实写入点**：`t02-fr200-fr201.spec.ts:175-182`（每次 poll 完成后写 `lastCommitPoll`）、`:1330-1339`（catch 内推 annotation）、`:1409`（写入 diagnostic）。缓存为 4096 字符**截断**文本 ＋ `originalUTF16Units` ＋ `truncated`，而**判定仍用未截断原文**（`:183`）——此点正确。**该机制至今仍零真实失败样本**：CI41 跑的是修复前代码 | 原 T02 | 下一次真实 Windows 失败样本 | **否** | **是**（先确认 annotation 实际落盘，再评估其证据价值） | 否 |
| **F-R09-06** | P2 | **维持** | 本轮**未改动** `scripts/run-engine-tests.py`（base→head 无该路径变更）；`:379-383` 的 `git rev-parse` 在 `try` 之外、非 0 → `None` 且**不计 errors** 的形态仍在树（R08 F07 仍在树） | ROOT 接收侧口径 | 接收侧拦截 | **否** | **是**（拒绝无 head／tree 绑定的证据） | 否 |
| **F-R09-07** | P2 | **维持** | 本轮**未改动**该文件；`scripts/engine-test-reporting.py` 的 identity 13 项**仍无 `sys.path`**；`:462` 的 `python -m pytest` 仍在树（R08 F06 仍在树） | 原 T02 | CI 与本地导入环境等价性观测 | **否** | **是**（不得声称等价） | 否 |
| **F-R09-08** | P2 | **维持** | 本轮实测复核：`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` **仍停在 `62d4b0a2`，均无 `240b581c`**；本轮亦**未修改**这两份文档（`git diff` 实测为空） | ROOT 指定的唯一文档 owner | 归档票追加当前节 | **否** | **是**（唯一状态源纪律） | 否 |
| **F-R09-09** | P2 | **维持** | 本轮**未改动** `.github/workflows/ci.yml`；`cancel-in-progress: true`、Quality 15 min／Desktop 20 min、两个 `if: always()` 制品步仍在树；`always()` 是**配置**，不保证取消后仍产出完整回单 | ROOT 接收口径 | 每次 CI 回单接收 | **否** | **是**（只看 step 绿或总数不代证完整） | 否 |

**本表之外新增的观察**（**不占用 F 编号**，避免挤占 Top 位）：**OBS-R09-10**（P3，测试前提未显式化，见 §17.2.5）；以及**维持**的既有开放项——**4299／4300 整数边界仍无断言**（见 §17.2.4）、R08 F5／R06 D8 的两处 PATH `python`、R08 F15／R06 Z P6／D5 的无 `ORDER BY` witness 选取、R06 D6 的 vendored `notation3.py` `n[-1]`、R08 F09 的 `fr201.1`／`fr201.2` 死制品、R08 F10／MM R07-03 的 Ruff 与 Prettier 排除面不等、MM R07-13 的契约类型宽度、旧 CI36 的 79F 逐例全因未知。

### 17.5 清单 **#57 的当前有效判定** 与 **#48/#57 更正后的 160 项有效分布**

#### 17.5.1 问题的实质

§16.4-C7(c) 把 #57（GDPR 删除请求）写成"**部分适用／无法确认（组织事实）**"。这一写法**同时给出两个判定值**，使该行**无法被唯一计数**，与本报告"每行一个判定单元格、逐行解析重算"的口径冲突。**本节给出唯一裁定。**

#### 17.5.2 **唯一有效判定（复合类别）**

**#57 的当前有效判定 ＝ `部分适用／无法确认（组织事实）`，作为**单一判定取值**，自成一档。**

- **含义**（两部分必须合起来读，缺一即误读）：
  1. **部分适用**——就产品语义与本候选实现而言，该条目**确实有适用面**：产品确实存储并读取业务断言事实与其来源行（`storage.py` 的事实表与 `source_row`／`owner` 字段、`project_host.py` 的读取投影、`OwnershipConflictDetailView` 对 `sourceRow` 的可见展示），即**存在**"可被删除请求指向的数据"这一事实；
  2. **无法确认（组织事实）**——"这些业务事实与来源行是否构成 GDPR 意义下的个人数据"属**产品／组织／法律事实**，**本票无代码证据可判**，亦**无权替产品或法务 owner 裁定**；因此该适用性判定**在本票内不可闭合**，必须由该 owner 裁定后回填。
- **唯一计数方式（明示）**：本报告 §6 的**每一行只贡献一个判定单元格值**；统计时**每个取值各计一次**。复合取值 **`部分适用／无法确认（组织事实）` 自成一档，只计一次**，**不并入**"部分适用"、**不并入**"无法确认"、**不重复计入两者**。
- **#48 的当前有效判定 ＝ `部分适用`**（**单一取值**，无歧义，计入"部分适用"档）。

#### 17.5.3 **追加更正后的有效 160 项分布**（原表与原统计**保留不改**，以追加列明替代关系）

| 判定取值 | 原分布（§16.3 实测，**不变**） | **追加更正后的有效分布** | 变化来源 |
|---|---|---|---|
| 适用 | 26 | **26** | — |
| 部分适用 | 54 | **55** | **+1**（#48 原"不适用"→"部分适用"） |
| 适用（部分） | 2 | **2** | — |
| 不适用 | 75 | **73** | **−2**（#48、#57 各移出 1） |
| 未验 | 1 | **1** | — |
| 无法确认 | 2 | **2** | — |
| **部分适用／无法确认（组织事实）** | 0 | **1** | **+1**（#57 的复合判定档） |
| **合计** | **160** | **160** | — |

**合计校验**：26 ＋ 55 ＋ 2 ＋ 73 ＋ 1 ＋ 2 ＋ 1 = **160** ✓

**替代关系（逐行声明，原前缀不改）**：

| 清单行 | 原判定（原前缀内，保留） | **追加更正后的有效判定** | 依据 |
|---|---|---|---|
| **#48**（渗透测试） | `不适用`（理由"本地桌面应用无外部攻击面"——该理由**已不成立**） | **`部分适用`** | §16.4-C7(b)：本候选确有可被利用面（renderer／preload IPC 边界、stdio 协议、native helper 引导表达式）；渗透测试属**发布门禁**，本票未执行，且**不得**由"本地形态"推出"无攻击面" |
| **#57**（GDPR 删除请求） | `不适用`（理由"无个人数据处理"——该理由**已不成立**） | **`部分适用／无法确认（组织事实）`** | §16.4-C7(c) ＋ 本节 §17.5.2 的唯一裁定；原理由"无个人数据处理"不成立（产品确存业务事实与来源行），但"是否属个人数据"属组织事实 |

**本节对 §16.3 的取代关系**：§16.3 末段写的"**若该更正落地 → 26／56／2／73／1／2 = 160**"是把 #57 **并入"部分适用"**的**条件性预演**。本节的实际裁定把 #57 放入**独立复合档**，故**有效分布为 26／55／2／73／1／2／1 = 160**，**与该预演不同**。§16.3 的**实测原分布 26／54／2／75／1／2 = 160 本身不变、继续有效**。

### 17.6 本节写入后的实测状态与**真正仍未覆盖面**

#### 17.6.1 前缀完整性

- **134017B 原前缀是否 EXACT**：**是**。本节以**纯追加**方式写入文件**末尾**（既有 `*报告结束。*` 行之后），**全程未使用替换式编辑**，未触碰前缀任一字节。写入后本人以 `head -c 134017 | cmp` 对写入前快照（SHA256 `99cf241a3a169441a2187b0a76062103d4bda432d7af47e002c4656da26c8b18`）比对，结果 **EXACT**。
- **本节未改**：`apps/`、`packages/`、`tests/`、`scripts/`、`.github/`、`uv.lock`、`licenses/`、`docs/prd/`、`docs/architecture/`、`docs/iterations/`、`docs/reviews/T02/status.md`、`docs/m0-checklist.md`、`AGENTS.md`、旧 `round-01/02/03` WIP —— **均零改动**（`git diff` 实测为空）。

#### 17.6.2 **真正仍未覆盖面**（据实；**不因本节而缩小**）

1. **本票必要变更范围内**：**无**——base→head 的实现面、测试面、契约面、依赖面、规范面已全部落到正文级读取（A 类）。
2. **明确不在本票必要范围、但仍在仓内且未通读**：
   - `packages/engine/tests/` 其余 **9 个未变测试文件**正文（`test_mainline_cleanup_regressions.py` 174、`test_mainline_draft_dispatch.py` 251、`test_mainline_example_create.py` 690、`test_mainline_example_provider.py` 135、`test_mainline_named_example_dispatch.py` 307、`test_mainline_query_changeset.py` 361、`test_mainline_query_projection.py` 442 等，合计约 2600 行）；它们**不在 base→head 变更集**内，仅被本轮新增用例**间接 import**（`test_mainline_postwrite_rows_budget.py` import `test_mainline_named_example_dispatch`；`test_mainline_postwrite_admission.py` import `test_mainline_language_input_rejection`／`test_mainline_manual_input_rejection`／`test_mainline_read_work_budget`；`test_mainline_read_work_budget.py` import `test_mainline_query_changeset`）——**被 import 的对象**（`named_owned`、`request`、`staged_bundle`、`diff_pages`）的**定义体**本人**未逐行读**；
   - `packages/engine/src/ontolearn_engine/job_store.py` 2993 行中的**非 diff 部分**（本轮只读 `740-752` 闭包）；
   - `apps/desktop/src/main/engine.ts` 1200+ 行的**非必要闭包部分**（前序轮次已读必要闭包）；
   - `docs/iterations/I01/` 下**其余文件**；`docs/reviews/I03/inputs/` 仅作同名副本哈希核对；
   - `round-04`–`round-08` 报告正文、`round-01/02/03` 旧 WIP、全部历史 raw —— **未读、未改**。
3. **运行类证据**：完整 check／native24／C1／GUI **本轮未重跑**，均为 O064 归档的**他人运行结果**（O063 **无运行**）。**`240b581c` 的真实 CI 回单不存在**，CI41 根因不可得。
4. **wheel 二进制内部成员**：**未逐字读**；哈希链闭合依据的是 PROVENANCE／repack 脚本／锁文件／NOTICE 的**文本级**强校验关系（§17.2.1）。
5. **组织与法律事实**：#57 的"是否属个人数据"、人类资深工程师签字、双方最终接收 —— **不可从代码判定**，保持未闭合。

#### 17.6.3 证据层级（本节新增部分）

| 层级 | 含义 | 本节归属 |
|---|---|---|
| **L1 本轮实测** | 本人本轮亲自读取的原件正文或亲自执行的纯计算／比对 | §17.0 A 类全部；§17.1；§17.2.1 的哈希与尺寸核；§17.2.3 的 `_lang_tag_regex`／`Literal.__new__` 实际实现；§17.2.4 的 4299/4300 覆盖缺口；§17.3.1 的两个算式互证；§17.4 各条所引行号；§17.5.3 的分布重算与合计校验；§17.6.1 的前缀 EXACT |
| **L2 他人运行 ＋ 本轮交叉核验** | 他人归档的运行结果，本轮做交叉一致性核对 | O064 的 check／native24／C1 结果；O059／O060／O062 的诊断事实；O063 的"无运行"事实（由其 `COMPLETION.json` 自证） |
| **L3 推断（明示为推断）** | 由 L1／L2 事实作出的、标明不确定性的解释 | §17.2.5 的环境耦合后果（条件式）；§17.3.1 "区间内可能包含多种成分"的成分列举（**不断言成因**） |
| **L4 不可得** | 需真实 CI／人类／组织事实 | `240b581c` 的 CI 回单；CI41 根因；4299/4300 消费侧断言是否存在于其它仓外证据；#57 的组织裁定；人类签字 |

### 17.7 本节对结论的影响（明确未变与已变）

**未变**：

1. **§1.1 的 ConditionalPass（限定技术阶段）** —— **维持**。本轮补读的 **6A＋1M 引擎测试、1796 行 e2e spec、依赖三件套与锁文件**，**未发现 push 前源码技术阻断**；本节全部内容为**覆盖闭合、口径更正与判定归口**，**不产生新的源码技术阻断**。
2. **§3 的 Top 9** —— **位置与级别全部维持**（2×P1 ＋ 7×P2）；F-R09-03 的**表述**按 §17.4 限定（错误反例与改码建议已于 §16.4-C3 撤回，**根因 HOLD 保留**）；F-R09-04 的**数值口径**按 §17.3 更正。**新增 P3 观察 OBS-R09-10 不占 Top 位**。
3. **§4 的 31 个当前位置**、**§5 的权威 78 个历史位置** —— **逐项承接维持**（missing 0／dup 0；R06 MM01–13 仍为本方额外观察）。
4. **§8 的五句结论** —— 维持；第 1、2、4、5 句不变，第 3 句"7 条 P2"维持。
5. **§10–§12** —— 维持；**§12 的全部独立 HOLD 保留**。
6. **M0 的 S1／S2／S3／C1／B1／U1 退出门槛全部保留未关闭**；整体合并可用仍为 **2/17**；**C1 不得以 O064 同源本机子集视作完成**。
7. **全部 FAIL／UNKNOWN／OPEN-HOLD、容量／损坏库物理保护／跨平台／新包／engine 未知退出／法律组织事项** —— **不变**。

**已变（仅以下三处，均以本节追加表达）**：

| 位置 | 原表述 | 更正后 |
|---|---|---|
| §16.4-C4 | "非 poll 时间约 **144.185876 s**" | **撤回**；改为 **145.101449 s**，并**限定**为"区间非 poll 经过时间"，**不称为空闲、不归因任何单一原因**（§17.3.1） |
| §16.6 | "**O063／O064 运行结果**" | 更正为"**O064 的运行结果（O063 无运行）**"（§17.3.2） |
| §6 的 #48／#57 两行 ＋ §16.3 的条件性预演 | 原判定 `不适用`；预演分布 26/56/2/73/1/2 | **有效判定**：#48 → `部分适用`；#57 → `部分适用／无法确认（组织事实）`；**有效分布 26/55/2/73/1/2/1 = 160**（§17.5） |

### 17.8 本节的边界声明

- 本节**不新增**产品功能、验证门禁、owner 指派或事件窗口；只**归口**既有事项的**当前有效表述**。
- 本节**未**修改源码、测试、配置、依赖、需求、验收、锁文件或状态文档；**未**运行 formatter／HMR／install／build；**未**执行 git 写操作、push、CI 或 merge；**未**重跑任何已通过验证。
- 本节**未**读取另一作者的本轮 R09 报告或结论。
- **本票整候选必要覆盖已完成**（§17.1）；**整候选全范围覆盖不成立**，§17.6.2 所列范围**仍未覆盖**，本报告**不报全范围通过**。

---

*（本节为第三段追加。以上 §17 的全部数值与判定均由本人本轮实测或原件直读得出；最终 bytes 与 SHA256 由本人写入仓外记录，不内嵌于本报告正文，以避免自指悖论。）*

---

## 18. 事实更正与有效替代关系 v4（2026-10-26 · 同一 R09 的第四段追加）

> **本节性质**：同一 R09 任务的第四段**纯追加**内容，处理**四组**在 §17 中新出现的事实问题。四组均为**本报告自身表述的事实/归属错误**，**不产生新的源码技术阻断**，**不新增**任何产品功能、验证门禁、owner 指派、事件窗口或风险条目。
>
> **写入方式**：本节以**纯追加**方式写入文件**末尾**（既有 §17 末行之后），**未替换、未删除、未改写**上文任何字节；**166925B 原前缀 EXACT 的实测结果见 §18.7**。
>
> **固定身份**：cwd `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes`；base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `240b581c98dbbaec0b4e3773e011c0a14879fa78` / tree `0933a33107da5a645d432538da1582c8c004080d`；模型 M3.1-Flash／思考 xhigh；始终授权。**未改源／测试／配置／依赖／预算／验收，未运行产品、未重跑验证、未执行 formatter／build／install、未执行 git 写、push、CI 或 merge，未开新任务、未重置、未购买。**

### 18.0 四组更正一览（先给结论）

| 组 | 被更正对象 | 更正性质 | 更正后是否改变 Top 9 的编号／级别／位置 |
|---|---|---|---|
| **一** | §17.4 F-R09-01 的"6A＋1M 引擎测试与 1796 行 spec 亦从未在任何真实 CI 执行过……O064 原 24 例不覆盖本轮新增用例" | **断言撤回**（抹除了已存在的运行证据） | **否** |
| **二** | §17.4 F06／F07／F09 的"本轮**未改动**该文件（base→head 无该路径变更）" | **差异区间更正**（把单提交 delta 当成受审范围） | **否** |
| **三** | §17.4 F04／F05 的"未来 CI／merge 门禁 ＝ 是（须实测……／先确认 annotation 实际落盘）" | **门禁归属更正**（观测建议被写成硬门禁） | **否** |
| **四** | §17.2.3 的"小写化发生在 `n3()` 渲染而非构造" | **来源更正**（小写化在应用层 `term()` 封装） | **否**（该条本就在 §17.2 而非 Top 9） |

### 18.1 事实更正一：F-R09-01 的"从未执行过"断言**撤回**

#### 18.1.1 被撤回的原句（逐字，保留原前缀不改）

> "**本轮新增加强证据**：本轮补读的 **6A＋1M 引擎测试（3494＋523 行）与 1796 行 e2e spec 亦从未在任何真实 CI 执行过**——O064 的 native24「原 24 例」验收**不覆盖**本轮新增用例"

**该句不实**：它把"最新三文件修复尚无 240 真实 CI"扩大成了"**累计**测试从未执行"，并据此否定 O064 既有运行证据的作用。**本人撤回。**

#### 18.1.2 原件依据（本人本轮实测，全部 L1）

**(a) 真实差异区间与 blob 同源性**（`git rev-parse` 逐文件实测）：

| 文件 | 2b6c8a26 的 blob | 240b581c 的 blob | 同源性 |
|---|---|---|---|
| `test_mainline_language_input_rejection.py` | `2fc4c2f0…51a5061e` | `2fc4c2f0…51a5061e` | **SAME** |
| `test_mainline_manual_input_rejection.py` | `24130617…43501` | `24130617…43501` | **SAME** |
| `test_mainline_postwrite_admission.py` | `1e7cc306…163379d` | `1e7cc306…163379d` | **SAME** |
| `test_mainline_postwrite_rows_budget.py` | `e74c7272…3281` | `e74c7272…3281` | **SAME** |
| `test_mainline_postwrite_text_budget.py` | `a6f0ae00…74b5` | `a6f0ae00…74b5` | **SAME** |
| `test_mainline_read_work_budget.py` | `40b44653…70bff` | `40b44653…70bff` | **SAME** |
| `test_mainline_dispatch.py` | `311e524b…1eb71` | `311e524b…1eb71` | **SAME** |
| `tests/e2e/t02-fr200-fr201.spec.ts` | `8006952f…628ca` | `3f4a61f2…53d0` | **DIFF**（被 240 单提交修改） |

即：**七个引擎测试文件在 2b→240 之间 blob 全部相同**——它们在 head `2b6c8a26` 上**已就位并随该 head 被 CI41 实际执行过**；`240b581c` 只改了 spec 与另两个测试文件。

**(b) CI41 原日志的逐文件／逐 node 执行证据**（`outputs/20261026_t02_2b6c8a26_remote_ci_059/` 的三个 raw job log）：

- **Quality（Linux）** `quality-job-raw.log`（5701 行）：L600 `collected 3769 items`；L4474 `packages/engine/tests/test_mainline_dispatch.py ........................ [ 36%]`；L4510 `packages/engine/tests/test_mainline_read_work_budget.py ............     [ 51%]`；L4572 `=== 1629 passed, 9 skipped, 2131 deselected, 1 warning in 164.56s ===`；L4583 `======== 2087 passed, 44 skipped, 1638 deselected in 202.34s ========`。
- **Windows** `windows-job-raw.log`（8481 行）：L412 `collecting ... collected 3769 items`；L5731 起为**逐 node** 记录，例如 `packages/engine/tests/test_mainline_read_work_budget.py::test_core_same_host_reads_then_last_remove_job_marker_and_after_read PASSED [ 50%]`、同文件 `::test_original_64mib_work_limit_rejects_before_validation_at_both_stages[lower] PASSED`、`::test_core_admission_still_runs_full_authentication_and_holds_corruption[context] PASSED` 等；L8155 `======== 2087 passed, 44 skipped, 1638 deselected in 474.68s ========`；L8217 `=== 1634 passed, 4 skipped, 2131 deselected, 1 warning in 480.76s ===`。
- **macOS** `macos-job-raw.log`（974 行）：L447 `packages/engine/tests/test_mainline_read_work_budget.py ............     [ 33%]`；L526 `=========== 3719 passed, 50 skipped, 1 warning in 306.50s (0:05:06) ============`；L639–644 逐条 `✓` 列出本 spec 的**六个 case 全部通过**——`class: … (9.9s)`、`objectProperty: … (10.5s)`、`dataProperty: … (10.4s)`、`individual: … (9.5s)`、`FR201 UI relations and multivalue manual records … (1.7m)`、`FR201 canonical numeric language subtags … (9.3s)`；L654 `21 passed (4.0m)`。
- **逐文件命中计数**（`grep -c`）：七个引擎测试文件在 quality 日志各 **2** 次、macos 各 **1** 次、windows **10–120** 次不等；`t02-fr200-fr201` 在三者分别为 **7／7／18** 次。
- **一致性交叉校验**：CI41 macOS 日志中的 spec 行号为 **564／685／1571**，恰为 **2b** blob（`8006952f`）的行号；而 240 blob（`3f4a61f2`）的行号为 **597／718／1619**。行号与 blob 关系**互相吻合**，可据此确认 CI41 跑的是 2b 内容、O064 native24 跑的是 240 内容。

**(c) O064（修复后内容）的运行证据**（`outputs/20261026_t02_ci41_bootstrap_repair_064/`）：

- `full-check-after-lint-fix.stdout`（240 行）：L113 `collected 3769 items`；**L139／146／148／153／155／156／161 逐一列名这七个文件**（`test_mainline_dispatch.py`、`test_mainline_language_input_rejection.py`、`test_mainline_manual_input_rejection.py`、`test_mainline_postwrite_admission.py`、`test_mainline_postwrite_rows_budget.py`、`test_mainline_postwrite_text_budget.py`、`test_mainline_read_work_budget.py`，各带独立通过点列）；L240 `=========== 3719 passed, 50 skipped, 1 warning in 175.97s (0:02:55) ============`。
- `native24/case-results.json`（24 case）：本 spec 的**六个 case 全部 PASSED，retry 0，errors 空**——`class` 5945 ms、`objectProperty` 6057 ms、`dataProperty` 6138 ms、`individual` 5915 ms、**`FR201 UI relations and multivalue manual records …` 68009 ms**、**`FR201 canonical numeric language subtags …` 6876 ms**；其 `line` 字段为 597／718／1619 ＝ **240** 内容的行号。

**(d) 源绑定（不得反向否认已有内容验证的前提）**：

- `full-check-after-lint-fix.json` 与 `source-before-validation-03.json`：`head = 2b6c8a26…`、`tree = 08ce3f6e…`（＝**2b parent HEAD ＋ exact APPLIED03 工作树**）。
- `after-commit-source-build.json`：`head = 240b581c…`、`tree = 0933a331…`（＝**提交后内容 exact**）。
- 三文件 240 blob 的 SHA256 与本报告既有记录**一致**：`native-driver.ts` `f994ce5a…d7d35`／11993 B、`t02-fr200-fr201.spec.ts` `e5bd057f…79e40`／75089 B、`native-driver.test.ts` `31a4cb64…b352`／13224 B。

#### 18.1.3 **更正后的 F-R09-01 有效表述**（替代原依据句）

> 本候选的**累计**变更（base→240）**已被真实执行过**：CI41 在 head `2b6c8a26` 上于 Linux（Quality）／Windows／macOS 三平台**逐文件、逐 node 实际执行**了这七个引擎测试文件与本 spec 的六个 case，引擎侧**全部通过**（Quality 3769 collected、Windows 2087 passed／1634 passed、macOS 3719 passed／native e2e 21 passed、spec 六 case 全 ✓）；O064 又在与**提交后内容逐字等价**的工作树（2b parent HEAD ＋ exact APPLIED03）上跑了完整 check（collected 3769、**3719 passed／50 skipped**）与 native24（本 spec 六 case **全 PASS**，含 FR201 68009 ms 与 language cohort 6876 ms）。
> **真正未结的只有一条**：**`240b581c` 这个提交本身尚无 GitHub Actions 真实 CI 运行**——尤其是 CI41 失败的两个平台（Linux x64 的 Quality native-recovery 步骤、Windows 的 FR201 case16 整例超时）上，该**三文件修复**未在真实 CI 上被验证。
> **不得反向否认已有内容验证**；CI41 的失败是 Quality 的 `app.isPackaged` 步骤与 Windows FR201 case16 的整例超时，**不是**引擎测试失败。

**级别 P1 与 merge 阻断属性维持**；事件窗口维持"下一次精确 push 票触发的真实 CI"。

### 18.2 事实更正二：F06／F07／F09 的**差异区间混写**更正

#### 18.2.1 被更正的原句（逐字，保留原前缀不改）

> F06："本轮**未改动** `scripts/run-engine-tests.py`（**base→head 无该路径变更**）"
> F07："本轮**未改动**该文件"
> F09："本轮**未改动** `.github/workflows/ci.yml`"

**后半句不准确**：把 `240b581c` 单提交的 delta 当成了**受审 base→240 整候选的范围**。**更正如下。**

#### 18.2.2 Git 原件实测（`git diff --name-status`，L1）

| 路径 | base583 → 240 | 2b6c8a26 → 240 | 该路径的 diffstat（base→240） |
|---|---|---|---|
| `scripts/run-engine-tests.py` | **A**（新增） | 无变化 | **+470** |
| `scripts/engine-test-reporting.py` | **A**（新增） | 无变化 | **+124** |
| `scripts/repack-rdflib-input-types.py` | **A**（新增） | 无变化 | +170 |
| `.github/workflows/ci.yml` | **M**（修改） | 无变化 | **+34／−11** |

#### 18.2.3 **更正后的表述**（替代原依据句）

> `scripts/run-engine-tests.py`、`scripts/engine-test-reporting.py` 与 `.github/workflows/ci.yml` **是受审 base→240 累计候选的一部分**（前两者由该候选**新增**，`ci.yml` 由该候选**修改**）；`240b581c` 单提交相对其父 `2b6c8a26` **未改**它们。此前 §17.4 写"base→head 无该路径变更"**不准确**，**撤回该后半句**。
> **原证据局限本身全部维持**：`run-engine-tests.py:379-383` 的 `git rev-parse` 在 `try` 之外、非 0 → `None` 且**不计 errors** 的 fail-open 形态仍在树；`:462` 的 `python -m pytest` 与 `sys.path[0]` 语义仍在树；`engine-test-reporting.py` 的 identity 13 项**仍无 `sys.path`**；`ci.yml` 的 `cancel-in-progress: true`、Quality 15 min／Desktop 20 min 预算、两个 `if: always()` 制品步仍在树。**据此不新改源码。**

### 18.3 事实更正三：F04／F05 的**门禁归属**更正

#### 18.3.1 被更正的两格（逐字，保留原前缀不改）

> F04 的"未来 CI／merge 门禁"格：**是**（须实测整例墙钟与 poll 分布）
> F05 的"未来 CI／merge 门禁"格：**是**（先确认 annotation 实际落盘，再评估其证据价值）

**该归属不准确**：二者被写成了**成功 CI 的硬门禁**，与"本轮不新增门禁"以及"成功 CI 不产生 failure annotation 是正常行为"这一已接受事实冲突。**更正如下。**

#### 18.3.2 **更正后的门禁归属**

- **F-R09-04** —— 未来 CI／merge 门禁：**否**。整例墙钟与 poll 分布是**原真实 CI 之后的观测建议**，用于判断 `intervals: [100]` 的实际收益与剩余耗时结构；**不构成**合并前必须实测的条件，**不要求**为此新跑或变更预算。
- **F-R09-05** —— 未来 CI／merge 门禁：**否**。**仅在确实出现失败样本时**才核该 annotation 是否落盘及其证据价值；**成功 CI 不产生 failure annotation 是正常行为**，**不要求人为制造失败**、**不为取得附件而新跑或变更预算**；**不新增**"成功 CI 必须有失败样本"之类硬门禁。
- **保持不变**：原 ROOT 的接收条件——**完整 CI、head／tree 绑定、自然结束、后继步骤实际 success**——**原样保持**，本节不触碰。
- **明确不越界**：**不把"CI41 根因 UNPROVEN"偷加为合并前必须证因**。根因 UNPROVEN 仍是 §17.4 F-R09-02 的**独立 HOLD 与表述纪律**（"不得称已修复"），**不是**新增的合并前证因门禁。

### 18.4 事实更正四：§17.2.3 小写化**来源**更正

#### 18.4.1 被更正的原句（逐字，保留原前缀不改）

> "……与 `Literal` 不转小写并不矛盾——**小写化发生在 `n3()` 渲染**而非构造。"

**来源不准确**，更正如下。

#### 18.4.2 原件实测（本人本轮直读 `packages/engine/src/ontolearn_engine/rdf_snapshot.py`）

`:30` 起 `def term(value: str) -> URIRef | Literal:`；`:54-57`：

```
    if isinstance(result, Literal):
        if result.datatype == XSD.string:
            return Literal(str(result))
        if result.language:
            return Literal(str(result), lang=result.language.lower())
```

#### 18.4.3 **更正后的表述**（替代原句）

> 小写化发生在**应用层 `rdf_snapshot.term()` 的显式封装**——`Literal(str(result), lang=result.language.lower())`（`rdf_snapshot.py:56-57`）；`n3()` 只是**序列化这个已小写的 Literal**。vendored `Literal.__new__` **不**转小写与此**不矛盾**：库层不做规范化，应用层封装显式做，两层各司其职。

#### 18.4.4 **结论维持不变**（本节只更正来源，不改判）

| 输入类别 | 实际拒绝点 | 判定面 |
|---|---|---|
| **合法语法**（`"设备"@de-CH-1901`） | 应用 `term()` 显式小写 → 与调用方原词面不等 → `storage.py:492` `term(fact["object"]).n3() != fact["object"]` **canonical 等值拒绝** | canonical 精确性 |
| **非法标签**（`"设备"@1`、`"设备"@zh1`） | `_is_valid_langtag` 不匹配 → 补丁的 `InvalidLanguageTagError` | 解析器**输入类型**拒绝 |

**不改产品、不运行探针、不把它改判为新源码缺陷**；§17.2.3 的"两类拒绝路径"结论**维持**，仅其**来源归属**被本节更正。

### 18.5 被替代原句 → 追加表述（逐条对照，供取代使用）

| 位置 | 被替代的原句（要点） | **追加的有效表述** | 依据出处 |
|---|---|---|---|
| §17.4 F-R09-01 依据格 | "6A＋1M 引擎测试与 1796 行 spec 亦从未在任何真实 CI 执行过……O064 原 24 例不覆盖本轮新增用例" | **撤回**；累计变更已在 CI41 三平台与 O064 **实际执行并通过**；未结的**只有** `240b581c` 提交本身无 GitHub Actions 真实 CI 运行 | §18.1.2（a–d）、§18.1.3 |
| §17.4 F06 依据格 | "本轮**未改动** `scripts/run-engine-tests.py`（base→head 无该路径变更）" | 该文件在 base→240 为 **A 新增（+470）**，属受审累计候选；仅 2b→240 无变化。原 fail-open 局限**维持** | §18.2.2、§18.2.3 |
| §17.4 F07 依据格 | "本轮**未改动**该文件" | `scripts/engine-test-reporting.py` 在 base→240 为 **A 新增（+124）**，属受审累计候选；仅 2b→240 无变化。identity 无 `sys.path` 局限**维持** | §18.2.2、§18.2.3 |
| §17.4 F09 依据格 | "本轮**未改动** `.github/workflows/ci.yml`" | `ci.yml` 在 base→240 为 **M 修改（+34／−11）**，属受审累计候选；仅 2b→240 无变化。取消／预算／`always()` 局限**维持** | §18.2.2、§18.2.3 |
| §17.4 F04 门禁格 | "未来 CI／merge 门禁＝**是**（须实测整例墙钟与 poll 分布）" | **否**；整例墙钟与 poll 分布为**原真实 CI 之后的观测建议**，非合并前硬门禁 | §18.3.2 |
| §17.4 F05 门禁格 | "未来 CI／merge 门禁＝**是**（先确认 annotation 实际落盘，再评估其证据价值）" | **否**；**仅在确实出现失败样本时**才核 annotation 有无及其证据价值；成功 CI 无 failure annotation 属正常行为，**不制造失败、不为取附件新跑或改预算** | §18.3.2 |
| §17.2.3 末句 | "小写化发生在 `n3()` 渲染而非构造" | 小写化发生在**应用层 `rdf_snapshot.term()`** 的 `Literal(str(result), lang=result.language.lower())`（`:56-57`）；`n3()` 只序列化已小写的 Literal | §18.4.2、§18.4.3 |

### 18.6 稳定位置**不漂移**声明（逐项明示）

- **Top 9**：F-R09-01…F-R09-09 的**编号、级别（2×P1 ＋ 7×P2）、标题与在 §3 的位置**——**全部不变**。本节只更正 **F01／F06／F07／F09 的依据句**与 **F04／F05 的门禁归属格**，**不新增、不删除、不改级、不换位**。
- **§4 的 31 个当前位置**、**§5 的权威 78 个历史位置**（missing 0／dup 0，R06 MM01–13 仍为本方额外观察）——**不变**。
- **§6 的 160 行判定与分布**——**不变**：有效分布仍为 **26／55／2／73／1／2／1 ＝ 160**（§17.5 的裁定继续有效；本节**不触碰** #48／#57）。
- **§16.3 的实测原分布 26／54／2／75／1／2 ＝ 160**——**不变**。
- **§17.3 的 145.101449 s 口径**与 **"O064 的运行结果（O063 无运行）"** 证据层级——**不变**（本节不重复核读、不无变化重述）。
- **全部原 FAIL／UNKNOWN／OPEN-HOLD** —— **保留**；**2/17 不变**；**S1／S2／S3／C1／B1／U1 退出门槛全部仍未关闭**；C1 仍**不得**以 O064 同源本机子集视作完成。
- **不新增**产品功能、验证门禁、owner、事件窗口或风险条目；**不为无关小数字／措辞另开研究**。

### 18.7 本节写入后的实测状态与仍未覆盖面

#### 18.7.1 前缀完整性

- **166925B 原前缀是否 EXACT**：**是**。本节以**纯追加**方式写入文件**末尾**，**未使用替换式编辑**，未触碰前缀任一字节；写入后本人以 `head -c 166925 | cmp` 对写入前快照（SHA256 `e0ece3722d1cd562732c4c34300b80d3416977f7c301a29b71275b45b1fa498b`）比对，结果 **EXACT**。
- **本节未改**：`apps/`、`packages/`、`tests/`、`scripts/`、`.github/`、`uv.lock`、`licenses/`、`docs/`、`AGENTS.md`、旧 `round-01/02/03` WIP —— **均零改动**（`git diff` 实测为空）。

#### 18.7.2 本轮**新增**读取的对象（L1 本人实测）

CI41 的 `quality-job-raw.log`／`macos-job-raw.log`／`windows-job-raw.log`（逐行 grep 与定点行读取）；O064 的 `full-check-after-lint-fix.stdout`（240 行，定点行读取）、`native24/case-results.json`、`after-commit-source-build.json`、`source-before-validation-03.json`、`full-check-after-lint-fix.json`；`packages/engine/src/ontolearn_engine/rdf_snapshot.py:30-57`；以及 base→240／2b→240 的 `git diff --name-status` 与 8 个文件的 blob SHA。

#### 18.7.3 仍未覆盖面（据实；**不因本节而缩小**，沿用 §17.6.2 并追加两点）

1. §17.6.2 所列全部（被 import 但定义体未逐行读的 9 个未变测试文件约 2600 行；`job_store.py` 2993 行非 diff 部分；`engine.ts` 1200+ 行非必要闭包；`docs/iterations/I01/` 其余文件；`round-04`–`round-08` 报告正文、`round-01/02/03` 旧 WIP、全部历史 raw；wheel 二进制内部成员；组织／法律事实；人类签字）。
2. **追加**：**CI41 的具体失败时序根因仍不可得**（O059／O060／O062 的诊断均在 Electron **启动阶段**止步，`reachedNativeRecoveryRequire: false`，**不是** GitHub x64 复现）；**`240b581c` 的真实 CI 回单不存在**。
3. **追加**：CI41 的**逐 case／逐 node 原始 PASS/FAIL 语义**已核，但**该次运行的完整平台矩阵结果**（尤其 Linux x64 的 native-recovery 步骤为何失败）**未闭合**。

#### 18.7.4 证据层级（本节）

| 层级 | 本节归属 |
|---|---|
| **L1 本轮实测** | §18.1.2 的 blob SHA 与 CI41 三日志定点行、O064 stdout/case-results/源绑定 JSON、`rdf_snapshot.py:30-57`、差异区间表、§18.7.1 的前缀 EXACT |
| **L2 他人运行 ＋ 本轮交叉核验** | CI41 三 job 的整体结论、O064 的完整 check 与 native24 结果 |
| **L4 不可得** | `240b581c` 的 CI 回单、CI41 根因、组织／法律裁定、人类签字 |

### 18.8 本节对结论的影响

- **结论维持**：**ConditionalPass（限定技术阶段）**；Top 9 的编号与级别（2×P1＋7×P2）**不变**；**2/17 不变**。
- **本节四组更正全部是本报告自身表述的事实／归属错误**，**不产生新的源码技术阻断**，**不解除**任何 FAIL／UNKNOWN／HOLD，**不新增**任何门禁。
- **本轮最重要的实质影响**（据实）：F-R09-01 的**未结范围被显著收窄并被准确表述**——受审累计变更**已有真实执行证据**（CI41 三平台 ＋ O064），真正待办的只是 `240b581c` 提交在真实 CI（尤其 CI41 曾失败的两个平台）上的运行回单与归因；F06／F07／F09 的**归属被如实归位**（是本候选新增／修改的代码，而非"外部遗留"）。

---

*（本节为第四段追加。以上 §18 的全部数值与判定均由本人本轮实测原件得出；最终 bytes 与 SHA256 由本人写入仓外记录，不内嵌于本报告正文，以避免自指悖论。）*
