# T02 FR-200／FR-201 全新 R08 整候选独立工程审查

**本方**：MiniMax Code ／ M3.1-Flash ／ xhigh ／ 始终授权（完整访问）
**本方唯一报告**：`docs/reviews/T02/fr200-fr201-20261024/round-08/minimax-m31flash.md`
**审查类型**：独立对抗性工程审查，整候选（base→head）范围，非仅审新 CI 两脚本

---

## 0. 身份、范围与独立性声明

### 0.1 固定身份（本人实测，非引述）

| 项 | 声明值 | 本人实测值 | 判定 |
| --- | --- | --- | --- |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | 同 | ✅ |
| 分支 | `feature/weekly-t02-fr200-fr201` | `feature/weekly-t02-fr200-fr201` | ✅ |
| base | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 存在，tree `133357a527a3967417189195b5c24e3f8a5752e8` | ✅ |
| head | `62d4b0a2c3ad49ae37775b875a3e7e31db5fadac` | 同 | ✅ |
| tree | `7ad1d13d6a064aaa07bd046e78427e881e1732b4` | 同 | ✅ |
| 累计提交 | 36 | `git rev-list --count base..HEAD` = **36** | ✅ |
| 差异叶 | 98 | `git diff --name-status` 行数 = **98** | ✅ |
| tracked 物理源 | 1380 | `git ls-tree -r --name-only HEAD | wc -l` = **1380** | ✅ |
| 构建 | 5 | 5（`main/index.js`、`preload/index.js`、`renderer/index.html`、`renderer/assets/index-*.js`、`renderer/assets/index-*.css`），由 O056 证据三份副本独立复算 | ✅ |

`git diff --shortstat base..HEAD` = **98 files changed, 19977 insertions(+), 268 deletions(-)**。

### 0.2 谱系补充（本人新发现，非原提示内容）

base `583c05c7` = 本地 `develop`（`5f910b52`，PR#5 I04 合并）**+1 个提交**（`583c05c7 feat: integrate audited project ontology and query mainline (#6)`）。即 PR16 的目标基线比已合并的 I04 线领先一个整合提交；本候选 36 提交叠加其上。这解释了为何 base 的 FR-200 元数据／CRUD 基础（`entity_metadata.py`，五组 metadata `identifier/labels/definitions/synonyms/examples`，`KNOWN={triples,singleValuedPredicates,references,KEY}`）在 base 已存在——本候选是在其上做 FR-201 语义与控制层收口，而非从零实现 FR-200。

### 0.3 独立性

- 本票为**全新 R08**，另一应用独立新建任务。本票**未读取、未索取、未推断**对方 R08 正文或结论。
- **诚实披露**：在准备写入本文件前，本人对 `docs/reviews/T02/fr200-fr201-20261024/round-08/` 执行过一次目录列举（写入目标定位所必需），看到目录内已存在一个 55592 B 的 `zcode-glm53.md`。本票**未打开、未 grep、未读取其任何字节**，不据其文件名推断内容或结论，也不声称"从未见过任何元信息"。上述列举是本人唯一的接触点。
- R01–R07 历史为双方同等可读的历史输入，本票据实引用。
- 旧 R07／其他轮次的通过或 ConditionalPass **不继承**。本票对 base→`62d4b0a` 整体重新作判断。

### 0.4 操作者与 UI 证据边界

本票全部结论来自**代码、配置、Git 只读与纯计算**，以及**对他人已提交原始证据文件的读取**。本票**没有**操作桌面端 UI，没有逐项核验路径／provider／model／thinking／permission，**没有**产生任何 UI 侧一手证据。涉及 UI 的结论一律标注为"源码层可确认／GUI 未实测"。本票不虚造自己看见过的 UI 证据。

---

## 1. 结论先行

### 1.1 对整个 base→`62d4b0a` 候选的判断

**附条件通过（Conditional Pass）——本地实现与本地验收层面通过，无 push 前源码技术阻断；但不具备合并条件，且 R07 结论不适用于本 head。**

拆成四句：

1. **本地实现层：通过。** 我逐层读过本候选 98 个差异叶中承担产品语义的全部叶（引擎 8 个源文件、契约 7 个、桌面端 8 个、CI 控制层 4 个、测试 15 个），未发现可在本 worktree 内修复的源码技术阻断。发现的问题最高为 P2，且均为**一致性／可追溯性／流程**类，无数据损坏、无越权、无凭据泄露、无金额类风险。
2. **本地验收层：通过，但证据为他人运行，非本人重跑。** O056 的 11 项声明经独立复核，**11/11 实质数值全部确认**（含 COMPLETION.json 20220B/`bb8be59b…`、FINAL-MANIFEST.json 417088B/`914ce3f4…`、1692 针、1892 PASS、3769=3719+50、Ruff 384、mode2 原生 0/114.075s、57 文件 1638+2131、setup/call/teardown 3769/3763/3769、native24 5264605B/`32ca3e7e…` 21PASS+3skip、101 附件、23 字节 nonce 差异、三份独审哈希）。**我自己没有重跑任何测试、构建、打包或 GUI**。
3. **push 前源码技术阻断：未发现。** 本票未找到任何"必须先改源码才能 push"的缺陷。
4. **合并：当前不可合并，且不是源码问题。** 本 head `62d4b0a` **未 push**、PR16 head 仍为 `9cbdf34`、远端 develop 仍 `583c05c`、**本 head 无任何 CI 运行**。合并必须等待本 head 的真实三 job CI。

### 1.2 最关键的三条

- **A. R07 全链与本 head 脱钩。** `round-07/disposition.md:3`、`version-map.json:6`、`artifact-manifest.json:6` 三处均钉 `b215f543`／tree `7cab46f0`；`docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 末节仍是 b215／R07 快照，**全仓无 `62d4b0a` 或 `O056` 命中**。b215→HEAD 新增 3 个提交，其中 `422bdfdb`＋`62d4b0a2` 改写了 `package.json:26` 的引擎执行路径（`uv run --frozen pytest` → `uv run --frozen python scripts/run-engine-tests.py`）与 `ci.yml`，新增 **594 行**（18980B＋4067B）**从未进入任何指定双审的审查范围**。R07 两位作者的"整个 base→b215 无 push 前源码技术阻断"**不能外推**到本 head。
- **B. 本候选要解决的正是历史 CI 取消与 Windows 未结算问题，但本 head 零 CI 数据。** 9cb CI40 attempt1 的 Quality 15 分钟取消、Windows 20 分钟取消且 3477/3769 结算、292 未结算——本候选用两进程分片 + 首败诊断正面回应，但**本地 114.075s 是开发机数字，不能外推 GitHub runner**（尤其 2 核 Windows）。在没有本 head 的真实三 job 回单前，"更快"只是设计意图。
- **C. 唯一状态来源未记当前候选。** 这使 R07 的 MM R07-04 条件（状态源须追加当前候选）在 HEAD 上重新变开，也使"完成度"没有单一可信落点。

### 1.3 一句话给 ROOT

本票可以接收为**推送前技术审查阶段**的独立意见；**不能**作为合并放行；合并前必须补：①本 head 的真实三 job CI 回单（Windows 完整 3769 逐项或有据 skip、自然 0、无失败／早停／取消／timeout／NOTRUN）；②状态源追加 `62d4b0a`／O056 快照；③F04／F06／F07 三条 P2 的处置结论（可延期但须书面归口）；④对 F03 的 CI 口径裁定。

---

## 2. 完整已读范围

### 2.1 源码／配置（全部读过实体或 diff）

| 类别 | 文件 |
| --- | --- |
| CI 控制层 | `.github/workflows/ci.yml`（HEAD 全文 163 行）、`package.json`、`scripts/run-engine-tests.py`（18980B，470 行）、`scripts/engine-test-reporting.py`（4067B，124 行）、`scripts/build-engine.mjs`（全文）、`scripts/repack-rdflib-input-types.py`（存在，未逐行） |
| 引擎核心 | `packages/engine/src/ontolearn_engine/project/mainline.py`（+417）、`storage.py`（+114/−103）、`job_store.py`（+405/−1）、`project/project_host.py`（+169/−59）、`project/domain_changesets.py`（+36/−34）、`rdf_snapshot.py`（+32/−21）、`project/query_presentation.py`（+21/−19）、`coordinator.py`（+23/−22）、`project/entity_metadata.py`（base 已有，读了 KNOWN/FIELDS 与 label/comment 映射） |
| 契约 | `packages/contracts/v2/schema.json`（+525，含 `error3` 全 oneOf 分支、ownershipDetailDocument、ownershipDetailHeader 摘录）、`src/index.ts`（+160，含 `reassembleOwnershipDetail`）、`src/v2.ts`（+131，含手写 SHA-256 与 `matchesOwnershipDetail`）、`python/contract_v2.py`（+49）、`v2/registry.json`、`v2/fixtures.json`、`v2/binding-regressions.json` |
| 桌面端 | `apps/desktop/src/main/desktop-ipc.ts`、`main/engine.ts`、`main/project-mainline-service.ts`、`preload/index.ts`、`renderer/src/ontology/{OntologyMainlinePage.tsx,OntologyPage.tsx,OwnershipConflictDetailView.ts,mainline-api.ts,mainline-facts.ts,mainline-ownership.ts,mainline-session.ts}` |
| 依赖／供应链 | `pyproject.toml`、`packages/engine/pyproject.toml`、`uv.lock`、4 个 vendored wheel（zip 只读）、`packages/engine/vendor/rdflib/{PROVENANCE.json,notation3-input-types.patch,LICENSE}`、`licenses/NOTICE` |
| 测试 | `tests/e2e/t02-fr200-fr201.spec.ts`（1748 行，读了 describe/test 结构与 3 个测试块标题）、`tests/unit/t02-manual-preview-lifetime.test.ts`（读全部 6 个 it 名与关键断言）、其余 7 个新增／改动的 TS 与 Python 测试文件（读标题与断言要点） |

### 2.2 需求与决策闭包

- `docs/prd/PRD-本体学习与落地Agent工作台.md` —— **93584 B／SHA256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`，与声明逐位相符**；读了正文 FR-200（307–309 行）、FR-201（311–318 行）、FR-202/203/204（320–331 行）、FR-003（244 行）、FR-006（256 行）、FR-804（521 行）、附录 A/B 定位、**附录 C（959–982 行全文）**、**附录 D.1/D.2（983–1015 行全文）**、附录 E/F/G 定位。
- `docs/iterations/I01/ADR-0002-storage.md`（13747 B）、`docs/architecture/0001-desktop-framework.md`（3876 B）、`docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`（35812 B，读了 S1/S2/S3/C1/B1/U1 目标与**退出门槛**）。
- **AGENTS.md overlay 链接失效已核实且未据此略过归档**：`AGENTS.md:10` 指向 `docs/architecture/m0-review-and-update-plan-2026-10-19.md`（**不存在**）与 `docs/architecture/0002-storage.md`（**不存在**）；真实归档在 `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` 与 `docs/iterations/I01/ADR-0002-storage.md`，两者本票均已读。overlay 为受保护的未提交 policy overlay，**非候选缺陷**（SHA256 `de15f6ce…`／15147 B 与声明相符，物理 AGENTS.md 未被本候选新增）。
- 人类 D8 选择 A：`iteration-control/2026-10-21-weekly-release/user-grants/T02-D8-choice-A-20261025.json`（经 PROVENANCE.json 的 authorization 段交叉确认存在与哈希；未逐字读原文，**该文件内容未由本人独立打开**，故不引申其条款细节）。
- `docs/reviews/T02/fr200-fr201-20261024/round-05/fr200-fr201-original-clause-evidence-map.md`（86 行，**全文读**）、`round-07/{disposition.md,version-map.json,artifact-manifest.json,minimax-m31flash.md,zcode-glm53.md,independent-*.md}`、`docs/reviews/T02/status.md`（全文）、`docs/m0-checklist.md`（全文＋diff）。
- `outputs/20261025_t02_b215f543_fresh_r07_048/resume-20261026-03/DISPOSITION.md`（与仓内 round-07/disposition.md **字节相同**：20347 B／`da18a978…`，由子任务实测）。

### 2.3 证据

`outputs/20261026_t02_ci_parallel_evidence_repair_056/` 的 `COMPLETION.json`、`FINAL-MANIFEST.json`、`config-fixed-full-check.{stdout,json,stderr}`、`config-fixed-verify-sources.{stdout,json}`、`config-fixed-full-mode2-qualification.json`、`full-mode2-config-fixed/run-30cfd5248084418fb6a3a725cb02aae3/summary.json`、`config-probe-native-uv/effective.json`、`native24-config-fixed/{report.json,qualification.json,result.json,stderr.log,attachment-index.json,profile-bindings.json}`、`exact-build-nonce-delta.json`、`independent-ci-code-review.md`、`independent-final-validation-review.md`、`independent-successor-validation-review.md`。

### 2.4 本票**未**读／未做（边界）

- 对方 R08 正文（任何字节）。
- `round-04`～`round-06` 各轮原始报告全文（只经处置表与本票需要的片段引用）。
- `tests/e2e/t02-fr200-fr201.spec.ts` 的 1748 行断言体逐条（只读了结构、测试标题与关键锚点）。
- 全部 `outputs/` 下 O040/O045/O046/O050/O054/O055 原件（经状态表与处置表转述，未开原件）。
- 任何 README／CHANGELOG／隐私政策／法律文本。
- 任何产品运行、CI、打包、GUI、SQL、probe。

---

## 3. 本人实做纯计算 vs 读取他人真实运行（严格区分）

### 3.1 本人**实做**的纯计算（隔离临时目录／只读，方法披露）

| # | 计算 | 方法 | 结果 |
| --- | --- | --- | --- |
| C1 | **手写 SHA-256 正确性对拍** | 从 `packages/contracts/src/v2.ts` **程序化抽取** `ownershipSha256` 的 `k[64]`／`h[8]` 字面量，再按源码逐行移植为 Python，与 `hashlib.sha256` 比对 137 个长度（0–129、255/256/257/1000/4096/32768/32769，含 55/56/63/64/65 填充边界）＋`"abc"` 向量 | `k`/`h` **逐位等于标准 SHA-256**；**137/137 无差异**；abc 向量吻合 → **TS 手写 SHA-256 不是缺陷**，排除一项潜在 P1 |
| C2 | **vendored wheel 重建** | stdlib `zipfile` 解出 upstream wheel 的 `notation3.py` → `patch --dry-run` 后真实 apply `notation3-input-types.patch` → 与 fr201.1/2/3 三个 wheel 内同名成员逐字节比对 | patch **干净应用**；**upstream+patch 与 fr201.3 内 `notation3.py` 逐字节相同**；fr201.1／fr201.2 为更早增量 |
| C3 | **wheel 哈希链** | `sha256` 四个 wheel | fr201.3 = `99fab7bdd9148267…` **与 uv.lock 内 `wheels[].hash` 及 PROVENANCE `artifact.sha256` 三方一致**；upstream wheel = `30c0a3eb4b649be7…` **与 uv.lock 旧条目（PyPI rdflib-7.6.0）同哈希**，即 vendor 内 upstream 确为 PyPI 原版 |
| C4 | **契约双实现判据比对** | 逐行读 `v2.ts matchesOwnershipDetail` 与 `contract_v2.py ownership_detail_matches` | 发现**判据分叉**（见 F04） |
| C5 | **base 谱系** | `git merge-base --is-ancestor` 双向 + `rev-list --count` | develop→base 恰 1 提交（§0.2） |
| C6 | **R07 链一致性** | `diff` + `shasum` 对比仓内 round-07 六件与外部 DISPOSITION.md | **字节相同**，manifest 声明的哈希与实物全部吻合 |
| C7 | **归档路径真实存在性** | `ls`/`shasum` | 真实 M0 计划 35812 B、ADR-0002 13747 B 存在；overlay 两条链接目标不存在 |
| C8 | **脚本/文件哈希与体积** | `shasum`/`wc` | `run-engine-tests.py` `27d978ac…`／18980 B；`engine-test-reporting.py` `0210d2ee…`／4067 B |

**披露**：C1–C3 在 `/tmp` 下的隔离临时目录进行，仅用 Python stdlib（`zipfile`／`hashlib`／`re`）与 `patch`／`shasum` 等文本工具；**未导入、未执行产品代码**，未触碰 `node_modules`／`.venv`／`build`／`release`。

### 3.2 本人**读取他人真实运行结果**（未由本人重跑）

O056 的全部数字（1892 PASS、3769=3719+50、Ruff 384、mode2 114.075s、native24 21PASS+3skip、101 附件、23 字节 nonce 差异、5 build 逐字节）与三份独审的结论，**均为他人运行的原始文件**。本票做的是**对原始文件的独立重算与复哈希**（例如把 mode2 `summary.json` 的 3769 条 outcome 重新统计出 status/phase 分布、重算 101 个附件哈希、重做 build 字节 diff），**不是本人重跑测试**。两者在本报告中始终区分。

### 3.3 两名子核验代理（披露）

本票使用了两个**只读 verifier** 子任务代理，用于机械性证据核验与历史表重建：(a) O056 十一项声明的独立复算；(b) R07 的 78 个历史位置（23＋55）重建。两者均被显式禁止访问 `round-08/`，且均为 verifier 角色（不改项目文件）。其结论已由本人在关键处复核（数量、哈希、字节差异本人独立重算过一遍）。**代理结论不等同于人类资深工程师签字**（见 §12 第 148 项）。

---

## 4. Top 10 问题（按严重程度排序）

> 以下 10 项之外，§6 仍列出全部 P3 及历史 OPEN 项；Top10 不是穷举。

### F01 ｜ P1 ｜ **R07 审查链与本 head 脱钩，594 行新控制层从未进入指定双审**

- **位置**：`docs/reviews/T02/fr200-fr201-20261024/round-07/disposition.md:3`（"受审身份固定 base…→ head b215f5432d0c…／tree 7cab46f0…"）、`round-07/version-map.json:6`、`round-07/artifact-manifest.json:6`、`docs/reviews/T02/status.md` 末节、`docs/m0-checklist.md` 末节"2026-10-26 … b215f543／R07"。
- **触发**：以 R07 双作者"整个 base→b215 无 push 前源码技术阻断"的 ConditionalPass 作为 `62d4b0a` 的放行依据。
- **影响**：`62d4b0a` 相对 `b215f543` 新增 3 个提交（`9cbddf34` docs、`422bdfdb` ci、`62d4b0a2` ci）。后两个把 `package.json:26` 的 `engine:check` 由 `uv run --frozen pytest` 改为 `uv run --frozen python scripts/run-engine-tests.py`，并改写 `.github/workflows/ci.yml`（+45/−11）。**新增 18980 B＋4067 B＝23 KB／594 行的 Python 控制层**，其正确性、失败模式、退出码语义与证据自洽性**不在 R07 的任何一票审查范围内**。R07 的 78 个位置中没有任何一条覆盖这两文件。
- **证据**：`git log --oneline b215f543..62d4b0a`；`git diff` 四叶；三处指针文件均无 `62d4b0a`；`grep -rn "62d4b0a\|O056" docs/reviews/T02/status.md docs/m0-checklist.md` → **0 命中**。
- **建议**：本 R08 双审即为该覆盖的执行者（另一方结论不得被本票引用为放行依据）；合并前须由 ROOT 明确记录"CI 控制层是否纳入指定双审范围"的书面裁定。
- **阻断性**：**是（流程／审查覆盖），非源码缺陷。**

### F02 ｜ P1 ｜ **本 head 零 CI 数据；CI 时间预算未在 62d4 上验证，本地 114.075s 不能外推 runner**

- **位置**：`.github/workflows/ci.yml:17`（Quality `timeout-minutes: 15`）、`:121`（Desktop `timeout-minutes: 20`）、`package.json:26`。
- **触发**：本候选的目的正是消除 CI40 attempt1 的"Quality 15 分钟取消"与"Windows 3477/3769 结算、292 未结算"。要验证这一点，必须有本 head 的真实三 job 回单。
- **影响**：本地 mode2 原生 114.075s 是开发机（`.venv/bin/python3`）数字；GitHub Windows runner 的 CPU、文件系统与杀毒软件行为与之差异大，且 `run-engine-tests.py:22-31` 的 `HISTORICAL_SCORES` 注释已自陈"**NOT per-test durations or promised speedups**"。因此"Quality 不再超时"目前**只是设计意图**。同时本 head 未 push，**不存在任何本 head 的 CI 运行**，既不能证明会绿，也不能据此判定源码有 bug。
- **证据**：`scripts/run-engine-tests.py:19-21` 注释；O056 `config-fixed-full-mode2-qualification.json` 的 `"nativeRun":{"exit":0,"seconds":114.0749856249895,"engineShards":"2"}`；`independent-successor-validation-review.md` 明写"不替…Windows/Quality 远端 CI"。
- **建议**：合并门禁写死为"本 head 的真实三 job 回单"；不得以本地数字或另一方结论替代；Windows 必须给出完整 3769 逐项或有据 skip、自然 0。
- **阻断性**：**是（合并门禁），非源码缺陷。**

### F03 ｜ P2 ｜ **Windows 引擎步被从验收步降级为"仅诊断"并加 `--maxfail=1`，与合并门禁口径自相矛盾**

- **位置**：`.github/workflows/ci.yml:136-147`；对照 base `ci.yml` 的单行 `- run: npm run engine:check`（无 PYTEST_ADDOPTS、无分片、属三 job 的验收步）。
- **触发**：Windows job 运行。
- **影响**：三处口径冲突。①步骤自述 `name: Windows engine first-failure diagnostic (not acceptance)` 与 `run:` 前的注释 `# Diagnostic only: … not acceptance or merge approval.`，但同一 job 的绿结果又是"Windows 完整 3769 自然 0"这一合并门禁的唯一可能来源——**同一份产出不能既声明不构成验收又被引作验收回单**。②`PYTEST_ADDOPTS='-vv --maxfail=1 --tb=short --durations=20 --full-trace'` 由 `run-engine-tests.py:77` 的 `os.environ.copy()` **原样继承进两个分片子进程**，一旦出现失败即早停，剩余用例不结算——这正是历史 Windows"292 未结算"证据缺口的成因（诊断目的合理，但**该次产出不能作为"全量已跑"的证据**）。③`--durations=20 --full-trace` 的追加改变了诊断输出形态，而它被写在**同一份验收步**上。
- **证据**：`git diff base..HEAD -- .github/workflows/ci.yml`；`git show base:.github/workflows/ci.yml`（Windows 段）；`scripts/run-engine-tests.py:77`、`:100-107`。
- **建议**：把诊断与验收拆成两条明确口径——要么恢复 Windows 的无 `--maxfail` 全集步并把诊断参数移到独立的诊断 job，要么由 ROOT 书面裁定"该 job 全绿即等价于 Windows 全集验收"并删除误导性标签。**不得**让 merge 门禁引用一个自称"not acceptance"的产出而不作裁定。
- **阻断性**：**合并门禁相关（条件）**；不构成源码阻断。

### F04 ｜ P2 ｜ **同一契约的两份"独立实现"判据分叉：TS 接受 Python 拒绝的空页／尾页**

- **位置**：`packages/contracts/src/v2.ts` 的 `matchesOwnershipDetail`（`end > count` 判据）与 `packages/contracts/python/contract_v2.py` 的 `ownership_detail_matches`（`not start < end <= count` 判据）。
- **触发**：引擎返回 0 段页（`segments: []`），或 `startOrdinal == segmentCount` 的尾页。
- **影响**：Python 侧要求 `start < end`（至少一段且 `end ≤ count`），TS 侧只要求 `end ≤ count`（**允许 `end == start`，即零段页**）。二者被设计为互相独立的跨语言双实现，前提是同规则；分叉意味着该前提不成立：桌面端的响应闸门（`matchesBusiness3Response`，v2.ts 内 `q.method === 'project.ownership.detail'` 分支）会接受引擎侧契约测试会拒绝的响应。实测可达性：渲染层 `mainline-ownership.ts:73` 另有 `page.nextOrdinal <= startOrdinal` 兜底，且 `reassembleOwnershipDetail` 会因 `ordinal !== segmentCount` 或 `JSON.parse` 失败而 `INVALID_OWNERSHIP_DETAIL`，**故当前未形成端到端可利用路径**；但"两份独立实现一致"是本契约的核心安全论据之一，不能靠下游兜底维持。
- **证据**：两处源码逐行对照；`packages/contracts/src/index.ts` 的 `reassembleOwnershipDetail` 亦调用 TS 侧判据。
- **建议**：统一判据（建议两侧都要求 `start < end`），并加一条跨语言对照测试（同一组畸形页，两侧结论必须一致）。
- **阻断性**：非阻断（P2），但应在合并前处置或明确延期归口。

### F05 ｜ P2 ｜ **唯一状态来源未记当前候选 `62d4b0a`／O056**

- **位置**：`docs/reviews/T02/status.md`（**无 `62d4b0a`／`O056` 命中**）、`docs/m0-checklist.md` 末节（最新为"2026-10-26 T02 当前快照追加：b215f543／R07"）。
- **触发**：以状态源判断"当前候选是什么、已验到什么"。
- **影响**：违反 AGENTS.md"完成度只在 `docs/m0-checklist.md` 和对应 `status.md` 中维护"与"唯一状态来源"两条；同时使 R07 的 **MM R07-04**（"状态源未记 b215 事实"→ 条件采纳，归口为"ROOT 唯一维护者后续归档票后追加"）在 HEAD 上**重新变开**。另注：O056 的 `COMPLETION.json`／`FINAL-MANIFEST.json` 均**未自钉当前 head**（外部目录，无 commit 绑定），head 绑定只能靠本仓 Git 历史与 status 叙述。
- **证据**：`grep -n "62d4b0a\|O056\|20261026" docs/reviews/T02/status.md` → 0 命中；`git diff base..HEAD -- docs/m0-checklist.md` 末节为 b215。
- **建议**：由唯一文档维护者追加 `62d4b0a`／O056 快照（受审身份、O056 指针、三份独审的**限定结论原话**、Windows/Quality 远端待办、全部 HOLD 保留）。
- **阻断性**：**合并前条件**（与 MM R07-04 同类）。

### F06 ｜ P2 ｜ **默认路径把 `uv run --frozen pytest` 换成 `python -m pytest`；"原流等价"未被证据覆盖（`sys.path` 不在 identity 的七项内）**

- **位置**：`package.json:26`；`scripts/run-engine-tests.py:462`（`os.execv(sys.executable, [sys.executable, "-m", "pytest", *sys.argv[1:]])`）；`scripts/engine-test-reporting.py:63-81`（identity 记录项）。
- **触发**：未设 `CI_ENGINE_TEST_SHARDS` 或设为 `1`（**macOS Desktop job 正是这条路**；Linux Quality 与 Windows 走 `2`）。
- **影响**：`python -m pytest` 会把 **CWD（仓库根）** 插入 `sys.path[0]`，而 `pytest` console script 插入的是 venv 的 bin 目录。O056 的七项 identity（`rootpath`／`inipath`／`configSHA256`／`testpaths`／`pythonpath`／`addopts`／`executable`）经本人复核**确实全等**，收集 3769 逐项顺序亦全等——但 **`sys.path` 不在这七项里**，因此"默认路径与原流等价"这一说法**未被证据闭合**。当前 venv 依赖（rdflib／pyparsing／pyshacl／owlrl／html5rdf／packaging／prettytable／wcwidth／pytest／ruff／pyinstaller）无同名顶层包，**实际无遮蔽**；但仓库根下 `packages/`、`scripts/`、`tests/`、`apps/`、`docs/` 五个目录都将成为可导入顶层命名空间，一旦将来引入同名依赖即产生遮蔽（`import tests`／`import scripts` 之类）。
- **证据**：`scripts/run-engine-tests.py:462`；`engine-test-reporting.py:63-81`（identity 字段列表，逐项枚举无 `sys.path`）；`uv.lock` 依赖清单；O056 `config-probe-native-uv/effective.json` 与 mode2 identity 的七项相等（子任务复算，本人复核数值）。
- **建议**：(1) 在插件 identity 中追加 `sys.path`（至少 `sys.path[0]`）与 `sys.flags`，使等价性可证；(2) 或直接 exec venv 内 `pytest` 可执行文件路径而非 `-m`，从根上消除差异。
- **阻断性**：非阻断（P2/P3 交界），属"声称等价但未证明等价"的证据缺口。

### F07 ｜ P2 ｜ **`run-engine-tests.py` 的证据自绑定在 `git rev-parse` 失败时不 fail-closed**

- **位置**：`scripts/run-engine-tests.py:379-383`。
- **触发**：容器/沙箱内无 `.git`、或 `git` 不在 PATH（CI 有 git，但 `npm run engine:check` 也被本地与第三方环境直接调用）。
- **影响**：`summary["checkout"]["head"]`／`["tree"]` 会被写成 `None`，而 `summary["passed"] = not errors and not _signal` **不会因此失败**。结果是一份"passed=true 但不含 head 绑定"的 `summary.json`——即**一份无法证明自己属于哪个候选的证据文件**。本候选的整个证据体系依赖 head 绑定（`FINAL-MANIFEST.json`／`COMPLETION.json` 同理），控制层不应产出无绑定证据。
- **证据**：`scripts/run-engine-tests.py:379-383` 与 `:443`。
- **建议**：`rev-parse` 失败时写入明确的 `checkoutError` 并**计入 errors**（或至少在 CI 环境下强制要求 head 绑定），使无绑定证据不能被当作有效证据。
- **阻断性**：非阻断（P2），建议合并前修复。

### F08 ｜ P2 ｜ **事实预览围栏会静默丢弃用户操作，无任何可操作提示**

- **位置**：`apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx` 的 `preview()` 与 `current()` 闭包（`if (!current()) return`）。
- **触发**：用户点"预览"后，`await newManualFactPlan(...)`（现为异步，因需 `crypto.subtle.digest('SHA-256')`）期间发生任一快照变化——**例如用户此时点"读取当前项目"**（该按钮在 await 期间 `busy` 仍为 false、**未被禁用**），或任一 `invalidateFactPreview()`。
- **影响**：围栏 fail-closed 是**正确方向**（防止旧 continuation 复活），但丢弃路径**完全静默**：无 `formError`、无状态变化，用户看到"点了没反应"。这与仓库既有取向（错误消息应可操作）不一致。已有单测 `tests/unit/t02-manual-preview-lifetime.test.ts` 覆盖了围栏的**顺序语义**（"prepares the latest unchanged tuple exactly once after digest completion"、"supersedes older preview even when tuple is identical"、"does not surface an obsolete hash rejection on the new draft"、"does not adopt a newer draft generation changed by a synchronous discard subscriber"），但**没有一条断言"被丢弃时用户可见的反馈"**。
- **证据**：上述源码逐行；`tests/unit/t02-manual-preview-lifetime.test.ts` 全部 6 个 `it` 标题（本人枚举）。
- **建议**：丢弃时给出明确提示（如"项目状态已变化，请重新读取后预览"）；或把"读取当前项目"在 digest 期间禁用，使两条路径互斥。
- **阻断性**：非阻断。**GUI 路径本轮未实测**，实际是否可复现属既有 HOLD；本条为源码层判断。

### F09 ｜ P3 ｜ **vendor 内三个 wheel 中两个无任何引用（死制品）**

- **位置**：`packages/engine/vendor/rdflib/`：`rdflib-7.6.0+ontolearn.fr201.1-py3-none-any.whl`（2378177 B）、`…fr201.2…`（2378736 B）、`…fr201.3…`（2379774 B，**唯一被引用**）、`upstream/rdflib-7.6.0-py3-none-any.whl`（615416 B）。
- **触发**：常规 clone／归档／供应链审计。
- **影响**：约 **4.76 MB 无引用 wheel** 增加供应链面与误用可能（例如误把 fr201.2 当消费版本）。PROVENANCE.json 已把 fr201.2 明确标为"historicalBaseline / 历史保留"，故**删除与否是所有者决定，非缺陷**；但需在发布审计中写明"仅 fr201.3 被消费"。
- **证据**：`grep -rn "fr201" packages/engine/pyproject.toml uv.lock` → 仅 fr201.3；四个 wheel 体积与哈希本人实测。
- **建议**：保留历史件时在 NOTICE／发布审计清单中显式标注消费版本与历史版本；或按 T11 所有权决策归档而非留在 vendor 目录。
- **阻断性**：非阻断。

### F10 ｜ P3 ｜ **Ruff format 排除面窄于 Prettier 忽略面；将来任一 raw 报告即可让 `npm run check` 失败**

- **位置**：`pyproject.toml:39`（`[tool.ruff.format].exclude` 仅按名枚举 `round-[0-9][0-9]/{zcode-glm53,minimax-m31flash,minimax-m31flash-r2}.md`）对比 `.prettierignore`（**整目录**忽略 `docs/reviews`）。
- **触发**：新增 raw 报告、或修改 `round-04/archive/*.md`、`round-0X/independent-*.md`、`disposition.md` 等**不在排除面**的文件，且其中含 ruff 会重排的 Python 围栏。
- **影响**：**这正是 R06 attempt2 的实际失败模式**——仓库自身记录（`docs/reviews/T02/status.md:69`）："O046 三 job Ruff lint 已通过，FORMAT 在 `round-06/minimax-m31flash-r2.md` 的 Python 围栏报 1 would／385 already，完整 3769 suite 三 job 全 NOTRUN"。即 Ruff 确实会格式化 `.md` 中的 Python 围栏，而该失败直接导致三个 job 的 Python 全套 NOTRUN。当前树通过（O056 `ruff format --check .` = `384 files already formatted`），故为**前向性维护风险**。
- **证据**：`pyproject.toml:39`；`.prettierignore`；`docs/reviews/T02/status.md:69`（R06 原始记录）。
- **建议**：把排除面扩到 `docs/reviews/**`（与 Prettier 对齐），或明确约束"raw 报告不得含可解析 Python 围栏"，并把该约束写进归档流程。
- **阻断性**：非阻断（当前树通过）。

---

## 5. 附：其余问题与观察（P3，不阻断）

| ID | 级别 | 位置 | 事实与影响 | 建议 | 阻断 |
| --- | --- | --- | --- | --- | --- |
| F11 | P3 | `apps/desktop/src/renderer/src/ontology/mainline-facts.ts`（`newManualFactPlan`）＋ `packages/engine/src/ontolearn_engine/storage.py`（`reservedIdentity` 分支） | 人工事实 ID 由随机 32 字节 hex 改为 `SHA-256(JSON.stringify([S,P,O]))` 内容派生。语义自洽：同 Triple 已可见→UI `FACT_ALREADY_EXISTS`；不可见但 ID 已占→`reservedIdentity` 所有权冲突。**副作用**：跨会话重放同一事实不再"幂等成功"，而是报所有权冲突。是否为期望产品语义属人类产品决定。 | 记为 OPEN，交产品裁定"重复提交同一事实应报已存在还是所有权冲突" | 否 |
| F12 | P3 | `scripts/run-engine-tests.py:456` | 无内部看门狗：某分片挂死会吃满整个 job 预算（15／20 分钟），最终被 job timeout cancel；`if: always()` 的上传是否真的执行**须看实际回单**。该性质在 base 的裸 pytest 下同样存在，**非本候选回归**。 | 可加可选 `--engine-test-timeout`（默认关闭）；或至少在 runbook 写明 cancel 后必须核对制品回单 | 否 |
| F13 | P3 | `scripts/run-engine-tests.py:22-31` | `HISTORICAL_SCORES` 来自"CI40 Windows first-result 到 last-result 跨度"，是调度启发式而非实测单例耗时；源码注释已自陈。分组为**整文件**粒度（57 文件 → 28／29 文件两组），文件内顺序保留，符合"保文件内顺序"要求。 | 无需改；PR 说明中保留"非提速承诺"的原话 | 否 |
| F14 | P3 | `packages/contracts/src/index.ts` `reassembleOwnershipDetail` | 硬编码 `pageSize: 64` 调用 `matchesOwnershipDetail`，与实际请求页大小解耦；因真实响应已被 `matchesBusiness3Response` 用真参数校验过，当前不构成绕过。 | 可改为传入真实页大小 | 否 |
| F15 | P3 | `packages/engine/src/ontolearn_engine/storage.py:1169-1172` | `SingleDeclarationConflict` 取"实际前两条阻断记录"用 `LIMIT 2` 且**无 ORDER BY**。历史边界已明确"SQL 无 ORDER BY 不自动证明跨运行缺陷"，本票确认该 SQL 事实仍成立，但**见证顺序**在跨运行层面未被合同化。 | 若要让见证顺序稳定，需显式 ORDER BY 合同；否则维持"未确认观察" | 否 |
| F16 | P3 | `packages/contracts/v2/schema.json`（ownershipDetailDocument 字符串 `maxLength: 16777216`） | 见证文档中 id／owner／sourceRow／subject／predicate 各自上限 16 MiB，宽松但被 16 MiB 文档总量与预算预留夹持。 | 无需改 | 否 |
| F17 | P3 | `apps/desktop/src/renderer/src/ontology/OntologyPage.tsx:438` | `pattern` 由 `[A-Za-z0-9_][A-Za-z0-9_-]*` 改为 `[A-Za-z0-9_][A-Za-z0-9_\-]*`（转义连字符）。**语义等价**，仅去歧义。 | 无 | 否 |
| F18 | P3 | `packages/engine/src/ontolearn_engine/rdf_snapshot.py:10` | `from rdflib.plugins.parsers.notation3 import BadSyntax, Notation3InputError` **只在 vendored fr201.3 成立**（上游 7.6.0 无 `Notation3InputError`，本人已实测）。打包走 `build-engine.mjs` 的 `uv run --frozen pyinstaller`（同一 venv／同一 vendored wheel），故包内一致；但**任何绕过 uv.lock 的安装路径**（例如从 PyPI 直接装 rdflib==7.6.0）会立刻 ImportError。 | 在 `packages/engine/pyproject.toml` 依赖旁加注释或 CI 断言，避免他人误改为 registry 源 | 否 |
| F19 | P3 | `docs/reviews/T02/fr200-fr201-20261024/round-07/` 三件指针 | R07 链内 ID 命名歧义：`Z P1–P8` 同时出现于 R05 与 R06 组；`R04 Z01`／`Z01`／`R04 Z` 三种写法；`disposition.md:111` 用 `R05ZP7`（无空格）。`MM R07-10` 标题写"已定位并闭合"而正文与两份独核限为"静态集合对账、原 run 差因未证"——**引用标题会误判为已闭合**。 | 本票按正文口径采信（不按标题）；建议归档时统一 ID 命名 | 否 |

---

## 6. CI 控制层专项审查（本轮改动核心）

### 6.1 两脚本的实际设计（本人逐行读）

**`scripts/engine-test-reporting.py`（124 行，插件）**：注册 `--engine-ci-report`／`--engine-ci-owner`／`--engine-ci-files` 三个私有选项；`pytest_configure` 以 `"x"` 独占模式打开 `events.jsonl` 并记 `session_start`（含 pid／ppid／owner）；`pytest_collection_modifyitems`（`trylast`）按整文件过滤 items 并 `pytest_deselected` 其余；`pytest_collection_finish` 写 `collection.json`（identity ＋ items）并在分片场景**逐条比对**全量 manifest，不符即 `pytest.UsageError`；`pytest_runtest_logstart/logreport/logfinish` 记 start／report／finish；`pytest_sessionfinish` 记 exitstatus。

**`scripts/run-engine-tests.py`（470 行，调度）**：
- `main()`：`CI_ENGINE_TEST_SHARDS` 默认 `"1"` → `os.execv` 原生 pytest；`"2"` → `parallel()`；其它值 → 打印错误并 **返回 2**（fail-closed）。
- `parallel()`：先跑一次 `--collect-only` 全量收集（独立 `os-temp`／`basetemp`／`cache`／报告目录、uuid owner、独立 PID 记录），再按**整文件**分两组（贪心 + 历史分值启发式），两个子进程并行，最后逐 node 结算。
- `account()`：对每个期望 node 要求 `starts==finishes==1`、setup/teardown 报告齐备、阶段顺序合法；状态机把 `unsettled／failed／error／teardown-skipped` 全部计入 `errors` → **父进程非 0**。集合差异、重复 node、跨 shard 重复、报告缺损、session 边界异常、输出流错误 → 全部非 0。
- `stop()`／`wait()`：POSIX 用 `start_new_session=True` + `killpg`（组级 SIGINT→SIGTERM→SIGKILL，并记录 `groupStillPresent`）；Windows 用 `CREATE_NEW_PROCESS_GROUP` + `CTRL_BREAK_EVENT` → `taskkill /T /F`，并**显式记录** `descendants: "UNKNOWN after launcher exit; no job handle"`。这与独立审查的历史 P2（"Windows venv redirector PID 不能硬等同真实 pytest PID"、"末条 packaged-native 漏 reporter"）一致：**Windows 后代状态保持 UNKNOWN，不外推 POSIX orphan 结论**。
- 退出码：`128 + signal`（被打断）／`0`（passed）／`1`（失败）。

**结论**：这两脚本的设计是**保守且 fail-closed** 的。我没有找到"失败能变绿"的路径。`account()` 的全量结算要求、`collection.json` 的逐条比对、session 边界唯一性、owner 绑定（`session_owned` 同时接受 `native==launcher 且 parent==我` 与 `parent==launcher` 两种，兼容 Windows 真实 pytest PID 不同于 redirector PID 的情形）都经得起逐行推敲。**但这些结论是静态的**——本票未运行过它们。

### 6.2 `62d4b0a` 相对 `422bdfdb` 的那一处改动（本次唯一改动）

`422bdfdb` 的资格失败真相：mode2 自有参数（`--engine-ci-report=<abs>`、`--engine-ci-files=<abs>`）在 `-p` 插件加载**之前**进入 pytest 的参数解析，**污染了 rootdir／config 推断**，漏掉 S2 pyproject 且 nodeid 前缀不同 → **资格真实失败**，不能倒填为通过。

`62d4b0a` 的处置：把自有参数全部改为 `--key=value` 形态（`--engine-ci-report=`／`--engine-ci-files=`／`--basetemp=`），`-o cache_dir=` 仍走 `-o` 选项值。**本人复核结论：该处置方向正确**——`-o` 的取值不参与位置参数推断，`--key=value` 的值也不作为位置参数。但在同一改动里，`--basetemp=<abs>` 仍是绝对路径参数，pytest 对 `--basetemp` 有专门处理（作为临时根目录使用，不参与 rootdir 推断），因此保留是合理的。O056 的七项 identity 全等 + 逐项顺序全等 + `configSHA256 = ed02773b100aed953f3240b0534883fa72d7aa50bf1f672a24c80cbcf57a8a38` 真实对应本 worktree 的 `pyproject.toml`，与该处置一致。

**但**：`--basetemp` 与 `--engine-ci-files` 的绝对路径仍进入 argv；本票**没有**运行 pytest 去验证 pytest 8/9 在不同 rootdir 推断实现下的行为——O056 的证据支持"当前本机 pytest 9.1.1 下正确"，不构成跨 pytest 版本保证。这是 F06 同源的证据边界。

### 6.3 `ci.yml` 其余改动（本人逐条核对）

- **Quality job**：`npm run check` 加 `CI_ENGINE_TEST_SHARDS: '2'`（Linux 首次走分片）；E2E 改 `--reporter=list,github,json --output=test-results/main` ＋ `PLAYWRIGHT_JSON_OUTPUT_FILE`；4 个 I04 步骤与 3 个 packaged 步骤同样加 reporter 与 JSON 输出路径；制品上传路径扩为 `build/i04-package-ci/`、`build/i04-matrix-ci/*`、`build/engine-tests/`、`test-results/`；`failure-traces-linux` 由 `if: failure()` 改为 `if: always()`。
- **Desktop job**：`npm run engine:check` 加 `if: runner.os != 'Windows'`；**新增** Windows 诊断步（见 F03）；E2E 同样加 reporter；制品上传路径扩为三项。
- **未变**：仍 3 job、`fail-fast: false`、Quality 15 分钟／Desktop 20 分钟、actions 全部 SHA 固定、Linux `npm ci` + `uv sync --frozen` + `verify:sources`、Chromium sandbox 4755 准备、I04 矩阵与 packaged recovery 步骤、`scripts/verify-i04-package.py`。
- **Mac**：**仍走 mode 1**（无 `CI_ENGINE_TEST_SHARDS`），符合"Mac 仍默认 1"。副作用是**原裸 pytest 路径如今只在 macOS job 被覆盖**，Linux 与 Windows 都走新分片路径——即"mode 1 与原流等价"的证据只来自 macOS 一处，加上本地 Mac 一次（O056 114.075s / 205.846s）。这放大了 F06 的重要性。

### 6.4 `package.json`

仅一行：`engine:check` 由 `uv run --frozen ruff check . && uv run --frozen ruff format --check . && uv run --frozen pytest` 改为 `… && uv run --frozen python scripts/run-engine-tests.py`。**`ruff check` 与 `ruff format --check` 未被绕过**（仍在同一命令内、仍在脚本之前），`check` 脚本的其余五步未动。**依赖未新增**（无 xdist、无新包），符合"无 xdist 或新依赖"。

---

## 7. 业务实现与契约层专项审查（FR-200／FR-201）

### 7.1 需求闭包

| 需求 | 原文位置 | 本票核查 |
| --- | --- | --- |
| FR-200 表格/表单 CRUD（类、对象属性、数据属性、个体、类层级、基本关系、中文名、英文标识、定义、同义词、示例）＋"删除已被引用内容前展示影响范围" | PRD 307–309 行；附录 C 959–982 行 | **源码层闭合**：五组 metadata 由 `entity_metadata.py`（`FIELDS={identifier,labels,definitions,synonyms,examples}`）承载；层级/domain/range/type 由 `mainline-ontology.ts` 生成 `rdfs:subClassOf`／`rdfs:domain`／`rdfs:range`／`rdf:type`；"影响范围"由 `mainline-ontology.ts` 收集 S/P/IRI 命中并**有引用即拒绝计划**，页面先读并列出影响。**GUI 未实测**（既有 HOLD） |
| FR-201 明确区分"定义结构关系"与"创建实例事实"，界面不得用同一句自然语句模糊代替，用户必须能以实际 RDF 核对 | PRD 311–318 行 | **源码层闭合**：结构走 `entityEditPlan`、事实走 `mainline-facts.ts` 的"原 ID 编辑/删除"与"内容 ID 新增"两条计划；页面分两个区并有明示说明；提交前展示完整 Diff、需显式人类确认。**GUI 未实测** |
| 附录 C 能力边界 | PRD 959–982 行 | **范围受限闭合**：本票只覆盖附录 C 中的"结构定义与实例断言分开编辑""label/comment 保留""不支持高级构造按 FR-203 拒绝"三条相关面；**不覆盖** bnode/list、SHACL 模板、受控规则、SPARQL、解释最低要求（979 行）。附录 C 的"解释能力最低要求"（自定义规则依据链／RDFS 公理与直接输入事实／SHACL 真实验证报告）**本候选未触及** |
| 附录 D.2 失效表 | PRD 983–1015 行 | **机制层有，具名下游未逐类验**：公共失效机制与九行正负例已有；**"手工新增/修改/删除断言事实 → 相关当前推导、查询结果、SHACL 结果、行为测试、报告"这一行的四类具名下游 GUI 未逐类消费联验**（既有 OPEN，非本候选引入） |
| S1 退出门槛 #2（"多来源所有权冲突均可定位并阻止不合法提交"） | `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` | **本候选正面贡献**：`ManualOwnershipConflict`／`SingleDeclarationConflict` 携带真实 `witness`，经 `_persist_ownership_detail` 落 `job_details`＋`job_blobs`，再由 `project.ownership.detail` 分页读出，桌面端 `OwnershipConflictDetailView` 渲染"首个阻断冲突定位"。这是"可定位"的直接实现 |
| 用户 D8 choice-A：不扩功能/预算/付费 | `iteration-control/.../T02-D8-choice-A-20261025.json` | **未见越界**：本候选新增 `project.ownership.detail` 属既有 FR-200"展示影响范围"与 FR-201 冲突定位的实现手段，未新增 FR、未改容量上限、未引入付费；**未引入"泛捕 ValueError"**（`rdf_snapshot.py` 明确把 `BadSyntax/Notation3InputError` 与未知异常分流，后者仍为普通 `ValueError` 走 UNKNOWN/HOLD）、**未按异常文案分类**、**未静默规范化**（canonical 严格取 `term(value).n3()` 精确相等）、**未提高容量上限** |

### 7.2 逐条发现的实现级判断

1. **canonical 精确化是正确的**。`domain_changesets.py` 的 `preview_changeset` 对 `manual[].subject/predicate` 做 `iri()` 校验，对 manual object 与所有 `edits` 值做 `term()` 解析并要求 `parsed.n3() == value`，否则 `INVALID_REQUEST field=params`；`rdf_snapshot.py` 把"确定的语法/策略拒绝"（`TermInputError`）与"未知解析失败"（普通 `ValueError`）严格分开。`TermInputError` 是 `ValueError` 子类，故未知分支仍会被上层 `except ValueError` 捕获并保持 UNKNOWN——**没有把产品失败静默降级为成功**。**控制层 `run-engine-tests.py` 的 `except Exception as error: errors.append(...)` 也只把异常计入 errors 并返回非 0**，未借异常处理吞掉产品/测试失败。
2. **`_WriteAdmission` 是本候选最复杂的部分**（`mainline.py:49-296`）。它是"实际写入者聚合持有"：在 `JobStore._transaction` 外层包一层，把最终物化成本在 `before_commit` 一次性计费；`bind()` 拒绝在已有不确定写入者、已有 retained 持有、已有事务或已计费 reply 时绑定；`_clean_predecessor()` 要求前任**显式 close 成功**（`owner._clean_close`）且读者已关闭、无 reply、无 pending 任务，才允许后继接管——**"关掉后再开"不会把不确定的写责任当干净账本接受**。这是保守设计，方向正确。
3. **`_application` 两个出口确实不同**（`job_store.py:607-636`）：有 `ownership_proof` 且错误是 `ManualOwnershipConflict`／`SingleDeclarationConflict` → 落详情文档并 `fault("OWNERSHIP_CONFLICT", detailRef=identity)`；否则走**仅 3 个固定键**（category/resource/projectId）的旧裸 detail → 同样 `OWNERSHIP_CONFLICT`。两者最终错误码相同，但**携带的信息量不同**。历史结论"裸族定位未全闭"在 HEAD 仍成立。
4. **`storage.py` 的 `_single_predicates`／`_validate_single_slots(project, introduced_singles)` 区分了"本次计划新引入的单值声明"与"既有单值声明"**：新引入且已存在同槽两条事实 → 抛 `SingleDeclarationConflict`（带实际前两条记录）；既有声明冲突 → 抛通用 `Conflict`。这直接支撑 FR-201 的"不得把 domain/range 当必填约束"与"单值声明与既有事实冲突要能定位"。
5. **跨边界的错误面是收敛的**：`contract_v2.py` 的 `ownership_detail_matches` 与 `v2.ts` 的 `matchesOwnershipDetail` 校验页的段序、字节偏移、长度、**逐段 SHA-256**、总段数与 `nextOrdinal`／`complete` 的一致性；`reassembleOwnershipDetail` 重新拼装字节流、用 `crypto.subtle.digest('SHA-256')` 校验整档哈希、以 `TextDecoder('utf-8',{fatal:true})` 解码、`JSON.parse` 后再过 `ownershipDetailDocument` schema，并以 `capture()` 做**原型污染安全的深拷贝**（只接受 `Object.prototype`／`null`／`Array.prototype`，拒绝 symbol 键、拒绝非枚举自有属性、限制节点数 16384／深度 8／字符预算）。**未发现 `dangerouslySetInnerHTML` 或字符串注入路径**。
6. **`project.ownership.detail` 的授权链是完整的**：`EngineSupervisor` 要求 `params.projectId === record.selected?.projectId`；引擎侧 `_OwnershipProof.check()` 同时校验 owner／reply／store／connection／lease／project／generation／method，并 `owner.authorize({"projectId": project})`；`detailRef` 读取时校验 `header["origin"] == proof.origin` 与 `fingerprint == digest({origin,requestHash,documentHash})`；`mainline-service.ts` 复核 selection epoch、owner、projectId、engineSessionId 后才返回。**未发现越权读取他人项目详情的路径。**

### 7.3 FR-200／FR-201 层面的未闭口（明确不作实现缺失断言）

- **"复制"的口径**：结构定义复制已由 28 笔实际 CRUD 覆盖；**独立实例事实的"复制"没有 UI 动作证据**（R05 条款映射已明确指出，本票确认该缺口在 HEAD 仍在）。**按既有裁定，本票不擅自把该解释设为新增需求，也不断言实现缺失**——列为"口径待裁定"。
- **四类具名下游**（推导／保存查询／SHACL／报告）在 GUI 逐类消费联验未做。**通用失效机制与九行正负例已有**（`invalidation-v2.json` 为 `staleReason` 唯一来源），本票区分"通用覆盖"与"具体未验"，不把未验断成缺失，也不宣称全部下游闭合。
- **Undo**：入口与准备链在树中（`OntologyMainlinePage` 按钮 → `session.prepareUndo()` 重读基准 → `intent:'undo'`），**GUI 路径未实测**，保持 HOLD。
- **42 个 INVALID 共用单一固定中文文案**（非逐原因），保持历史事实，不改判。

---

## 8. 供应链与依赖完整性（本票实证）

| 检查项 | 本人实测 | 判定 |
| --- | --- | --- |
| `uv.lock` 指向 vendored wheel | `rdflib` = `7.6.0+ontolearn.fr201.3`，`source={path="packages/engine/vendor/rdflib/rdflib-7.6.0+ontolearn.fr201.3-py3-none-any.whl"}`，`wheels[].hash = sha256:99fab7bdd9148267…` | ✅ 与实物哈希**三方一致**（实物／uv.lock／PROVENANCE） |
| upstream 原版未被篡改 | vendor 内 `upstream/rdflib-7.6.0-py3-none-any.whl` SHA256 = `30c0a3eb4b649be7…`，与 `uv.lock` 被替换前的 PyPI 条目同哈希 | ✅ **确为 PyPI 原版** |
| 补丁可重建 | `notation3-input-types.patch` 对 upstream 的 `notation3.py` **干净应用**（`patch --dry-run` 通过），结果与 fr201.3 wheel 内该成员**逐字节相同** | ✅ **供应链可重建** |
| 补丁范围 | 仅 `notation3.py`；新增 `Notation3InputError` 家族（`RelativeIRIBaseError`／`UnicodeCodePointError`／`UnterminatedStringError`／`MissingDatatypeError`／`InvalidLanguageTagError`／`IntegerDigitLimitError`）；`BadSyntax` 计数 76（与上游相同）；**未加 catch、未加文案分类器、未写 settings/cap/policy**（与 PROVENANCE `changeScope` 自陈一致） | ✅ 与供应商记录吻合 |
| 打包一致性 | `build-engine.mjs` 走 `uv run --frozen pyinstaller`（同一 venv、同一 vendored wheel），`--collect-all rdflib` | ✅ 包内 rdflib 即 fr201.3 |
| 引擎 import 依赖 vendored 特性 | `rdf_snapshot.py:10` 导入 `Notation3InputError`，上游 7.6.0 **没有**该符号 | ⚠️ 绕过 uv.lock 的安装路径会 ImportError（见 F18） |
| 冗余件 | fr201.1／fr201.2 共 4.76 MB **无引用** | ⚠️ 见 F09 |
| `licenses/NOTICE` | 本候选 +14/−1 记录 vendored rdflib 修订 | ✅ 已在树中（归属 T11） |

**结论**：本候选对第三方库的改造**做得比多数同类改动更干净**——补丁可从上游原版逐字节重建、wheel 哈希三方钉死、上游原件本身哈希与 PyPI 一致。这是本票给出正面评价的一项，也是 §12 第 38 项（"确认每个被装上的包都存在且是你想要的那个"）在本候选上的实际达成。

---

## 9. 证据链核验（O056，本票独立复算）

11 项声明**全部确认**（子任务复算，本人在哈希与字节差异处复核）。以下 5 处为**口径／归属注记**，非数值矛盾：

1. 三份独审**都不构成完整放行**：`independent-ci-code-review.md`（10452 B／`306ceec9…`）开篇即"当前版本暂不通过"（2 条 P2：Windows redirector PID 身份、末条 packaged-native 漏 reporter），后段才允许冻结 4 叶新候选，并自陈"这里不是这些后续验证已经通过"；`independent-final-validation-review.md`（4463 B／`4d1b60c1…`）**绑定的是 `422bdfdb`／tree `835ec63e…`**、引用的是旧的 native24 报告 `5269380B/…`，且**留有一条开放 P2**（mode2 配置绑定不合格）；`independent-successor-validation-review.md`（4727 B／`8cfc9269…`，与声明逐位相符）只覆盖 62d4 的本地范围，明写"不替新指定双审、Windows/Quality 远端 CI、package/release 或父功能验收"，并明写"engine 自然退出码仍 UNKNOWN""不写全 App 自然 0"。**三者无一构成合并放行。**
2. "SIGKILL 来自 csp-lifecycle.spec.ts:313" 这一归因出现在 `COMPLETION.json:385` 与后继独审，**不在** `native24-config-fixed/qualification.json` 内（该文件只记 `{"pid":50411,"exitCode":"null","signal":"SIGKILL"}`）。**本人已独立核对代码**：`tests/e2e/csp-lifecycle.spec.ts:313` 确为 `application.process().kill('SIGKILL')`，位于第 305 行 `finally {` 块内。归因成立，但证据位置需注明。
3. "12 个归档源"**不在 `npm run check` 的 stdout 内**，而是独立命令 `config-fixed-verify-sources.stdout`（exit 0／0.164s）。
4. "其余 4 个构建相同"应读作**每份副本的其余 4 个文件**（3 副本 × 5 文件 = 15；12 个非 main 文件逐字节相同）；nonce 区域 24 字符但**实际仅 23 字节不同**（before→422b 为 21 字节）。
5. 101 附件中**唯一 SHA 为 100**（两个 CSV 附件 `actual-ui-导出当前页 CSV-2.csv`／`CSV-3.csv` 同哈希），101＝100 逐字节可解码 ＋ 1 真实引用，本票复算 101/101 与记录哈希逐位相同。

**远端事实（本票只能读到本地 Git 状态，无远端权限）**：本地 `origin/*` 跟踪引用显示 `develop` = `5f910b52`；任务提示的"远端 develop 仍 583／feature 仍 9cb／PR16 open"**来自任务陈述，本票未通过 `git fetch` 复核（禁止联网与远端操作）**，故按"任务陈述的远端事实"记录，不冒充本人实测。

---

## 10. 历史逐项本版现状

### 10.1 计数核对（本人复核）

R07 处置链：**本轮 23**（Z F1–F10＝10、MM R07-01–12＝12、MM 原未编号→R07-13＝1）＋ **历史 55**（R06 Z P1–P8＝8、R06 MM D1–D12＝12、其余 35）＝ **78**，与"23＋55"一致，无缺漏无重号。仓内 `round-07/disposition.md` 与外部 `DISPOSITION.md` **字节相同**（20347 B／`da18a978…`），`round-07/` 六件的字节与哈希与 `artifact-manifest.json` 声明**逐一吻合**。

### 10.2 本轮 23 个当前位置的 HEAD 现状

| ID | 标题 | 原处置 | **本版（62d4b0a）现状** |
| --- | --- | --- | --- |
| Z F1 | Windows 完整验收缺 | 合并门禁 | **仍开（门禁）**。本 head 无 CI；F02／F03 展开。代码侧无新增阻断 |
| Z F2 | formatter 排除面按名枚举 | 部分采纳·未来维护 | **仍开（维护）**，并升级为 F10（本票给出更完整的失效路径与 R06 成因证据） |
| Z F3 | write_text 编码规约 | 采纳·维护 | **仍开（维护）**。R06 六处显式 UTF8 仍在树中 |
| Z F4 | UTF-8 双口径 | 事实澄清 | **已闭合（口径）**。无代码义务 |
| Z F5 | 两 TS 仍 PATH python | 采纳·维护 | **仍开（维护）**：`tests/unit/t01-ontology-metadata-contract.test.ts:168`、`t01-mainline-contract.test.ts:656` 仍在树中 |
| Z F6 | 历史 OPEN 集合 | 部分采纳·保留 OPEN | **仍开（逐项见 §10.3）**，未集合化关闭 |
| Z F7 | 发布前 HOLD 群 | 采纳·HOLD | **仍开（HOLD）**。见 §11 |
| Z F8 | ownership 闭环/受控分类 | 正面核验 | **部分闭合**。`rdf_snapshot.py` 的"确定拒绝 vs 未知"分流在 HEAD 仍在；`_application` 两出口仍不同（裸族未全闭，见 §7.2-3） |
| Z F9 | 安全不变量 | 正面核验 | **已闭合（限本受审面）**。本票复核 `project.ownership.detail` 授权链完整（§7.2-6） |
| Z F10 | 六 GUI 语义断言 | 观察·非缺陷 | **仍开（观察）**。GUI 本轮未实测 |
| MM R07-01 | Ruff 一行排除正确 | 信息·已核验 | **已闭合**。排除面仍在（`pyproject.toml:39`），但覆盖面问题见 F10 |
| MM R07-02 | 不覆盖未来 `-rN` 命名 | 低·未来维护 | **仍开（维护）** |
| MM R07-03 | Ruff 与 Prettier MD 策略不一致 | 低 | **仍开**，本票给出完整失效路径（F10） |
| MM R07-04 | 状态源未记当前候选 | **条件（merge 前）** | **在 b215 已闭合，在 62d4b0a 重新变开**（F05） |
| MM R07-05 | AGENTS.md M0 链接失效 | 低·overlay 非候选缺陷 | **仍开（overlay 维护）**。本票已核实真实归档位置（§2.2），未因链接失效略过 |
| MM R07-06 | "12"＝10 直参+2 BinOp | 信息·口径更正 | **已闭合（口径）** |
| MM R07-07 | 20 处默认 encoding 现状 | 信息·边界补强 | **已闭合（口径）** |
| MM R07-08 | "28 笔"是条款级映射 | 信息·更正 | **已闭合（口径）** |
| MM R07-09 | "build4 项"实为 5 中 4 | 信息·更正 | **已闭合（口径）**，本票复核并给出精确读法（§9-4） |
| MM R07-10 | Ruff 386/379 计数对账 | 信息·已对账 | **已闭合（口径）**，但**标题写"已定位并闭合"、正文限"差因未证"**（F19） |
| MM R07-11 | FR-201 多值 edit 判定放宽 | 低·观察 | **仍开（观察）**。`mainline-facts.ts` 放宽判定仍在；本票补充其与 F11 的关系 |
| MM R07-12 | vendored 补丁 wheel 供应链面 | 低·观察 | **仍开（HOLD）**；本票**强化**其正面部分（§8：补丁可重建、哈希三方一致），死制品问题见 F09 |
| MM R07-13 | TS 数值类型宽于 zod | 低·维护 | **仍开（维护）**。`contracts/src/index.ts` 的 `OwnershipDetailArgs` 仍宽于 schema（`startOrdinal:0`／`pageSize:number` vs schema 的 const 0／1..64） |

### 10.3 历史 55 个位置的 HEAD 现状（归并，逐条可追）

**本票以代码核验为准**（子任务定位 ID 与指针，本人在关键处复核）：

| 组 | 位置 | HEAD 现状 |
| --- | --- | --- |
| R06 Z P1 | 新 head Windows 缺证／旧 79F 全因未证 | **仍开门禁**（F02）。旧 79F 逐例原因仍未知；新绿不倒填旧因 |
| R06 Z P2 | 诊断参数与完整验收口径 | **仍开**，并被 F03 具体化：诊断步与验收口径需分离或裁定 |
| R06 Z P3 | definitions 早期坏 wire | **仍开（代码事实仍在）**：`domain_changesets.py` 预览校验内 `_definition(...)` 的未分类 `ValueError` 仍无分类 |
| R06 Z P4 | ownership 通用定位 | **部分闭合**：typed witness 已落地并可读；**裸族仍未全闭**（§7.2-3） |
| R06 Z P5 | 错误码集合（UI17／契约26／交集10／额外7／缺16） | **仍开**：集合事实成立；**未证 16 码全可达**，不得一次性泛加白名单 |
| R06 Z P6 | SQL 无 ORDER BY | **仍开（未确认观察）**：代码事实仍在（F15），不升级为已证跨运行缺陷 |
| R06 Z P7 | canonical 政策 | **已闭合（沿既有决定）**：精确 `term(value).n3()` 在 HEAD 生效（§7.2-1）；**无新人类表态前置** |
| R06 Z P8 | 规模／EOF／边界／状态／PATH | **逐项仍开**，不以集合标题掩盖 |
| R06 MM D1 | 新 head 未 CI | **仍开门禁**（F02） |
| R06 MM D2 | 状态／历史 manifest | **部分闭合**：b215 追加已做；**62d4 未追加**（F05） |
| R06 MM D3 | definitions 时序 | **仍开（代码事实仍在）**，与 Z P3 同源 |
| R06 MM D4 | ownership 最终码 | **部分闭合**：两出口最终码均为 OWNERSHIP_CONFLICT 成立；**裸族定位未全闭** |
| R06 MM D5 | 无序查询 | **仍开（未确认观察）**，同 Z P6 |
| R06 MM D6 | standalone EOF 裸索引 | **仍开（代码事实仍在）**：vendored `notation3.py` 的 `n[-1]` 索引仍在 |
| R06 MM D7 | 缺 16 码 | **仍开**，同 Z P5 |
| R06 MM D8 | 两 TS PATH python | **仍开（维护）**，同 Z F5 |
| R06 MM D9 | Ruff 计数分层 | **已闭合（口径）** |
| R06 MM D10 | D/E/G 与失效联动 | **仍开**：四类具名下游 GUI 未逐类验（§7.1） |
| R06 MM D11 | 4299/4300 应用边界 | **仍开（维护）**：HEAD 仅对 4301 有断言，4299/4300 应用边界断言仍缺 |
| R06 MM D12 | 正面结论 | **保留（有界）**，不外推 |
| R04 全部 14 条 | Z01–Z07／M01–M07 | **逐条承接**：其中 **R04 Z02（43692 分页误因果）已撤回**；Z01/Z03/Z04/Z05 仍开；Z06/Z07、M01/M02/M06/M07 为口径／维持类已闭合；**M04（standalone 残余）仍开**；**M05（早期 definitions）仍开**；M03（4299/4300）仍开 |
| R05 Z P1 | O040 首败定因 | **仍开门禁**；旧 79 全因仍未追认 |
| R05 Z P2 | 934 Quality 718s 新证据 | **已闭合（事实）**；**不迁移成新 CI 绿** |
| R05 Z P3 | 早期 definitions | **仍开**，同 Z P3 |
| R05 Z P4 | 通用定位合同 | **部分闭合**，同 Z P4 |
| R05 Z P5 | 缺 16 | **仍开**，同 Z P5 |
| R05 Z P6 | canonical 语义观察 | **已闭合（口径）**，无新增当前批准 |
| R05 Z P7 | pytest 诊断选项已变／规模 | **已闭合（口径）**，但见 F03（本候选再次改动 Windows 诊断参数） |
| R05 Z P8 | 历史 aff 状态永久保留 | **已闭合（维持）** |
| R05 MM01 | 首败假设被部分超越 | **仍开门禁**：旧 79 原因仍未知 |
| R05 MM02 | 934 两 success／一 failure | **已闭合（事实）** |
| R05 MM03 | 无新包／原 094 有界桥接 | **仍开门禁**：本 head 未打包（§11） |
| R05 MM04 | 入口追加 vs Ruff 差因未知 | **已闭合（分别承接）** |
| R05 MM05 | 缺码 | **仍开**，同 Z P5 |
| R05 MM06 | 早期 definitions OPEN | **仍开**，同 Z P3 |
| R05 MM07 | Manual/SingleDeclaration 真 witness | **部分闭合**：typed witness 已实现并可读；裸族仍延期 |
| R05 MM08 | SQL 事实 | **仍开（未确认观察）**，同 Z P6 |
| R05 MM09 | wheel/payload/解压量分层 | **已闭合（维持）**；本票另给出冗余件问题（F09） |
| R05 MM10 | AGENTS overlay | **已闭合（维持）**，非候选缺陷 |
| R05 MM11 | locator 无 object | **已闭合（信息）**；本票确认 witness 的 locator 仍只含 id/owner/sourceRow/slot，不含 object |
| R05 MM12 | 两 TS PATH python | **仍开（维护）** |
| R05 MM13 | 核心规模信息 | **已闭合（信息）**，不以 LOC 推正确性 |

**R07 两位作者原判均为 ConditionalPass**（`version-map.json` 记录），故**R07 未产出任何"通过"**；本票不继承任何 R07 结论，仅按代码事实重判。

---

## 11. 独立 HOLD 与未验事项（本票逐条保留，不消解）

**本票新增/确认的未闭**：

1. 本 head **无新包制造、无包内运行**；旧 094 包 912 成员基线按原样保留，本票**不冒重新整包 hash**、不称 62d4 新包。
2. **签名、公证、wholeApp 法律／`_distutils` 来源**、全平台／目标 macOS 15／Windows 11／参考设备 — 保留 HOLD。
3. **Q5／D2 容量口径、旧超限库恢复、损坏 SQLite 物理资源保护**（用户明确保留）— 保留 HOLD。
4. **unknown parser／N3／Store／坏快照** — 保留 HOLD。本票确认 `rdf_snapshot.py` 的"未知分支"（普通 `ValueError`）仍在，未被本候选消解。
5. **Undo GUI** — 源码在、GUI 未实测。
6. **未验 ownership 家族（裸族）／缺码可达性／见证顺序合同** — 保留延期。
7. **四类具名下游**（推导／保存查询／SHACL／报告）GUI 逐类 — 未验。
8. **native engine／named App 未知退出码** — 保留（O056 亦明写 `WindowsRemoteCIProven: false`、engine 自然退出码 UNKNOWN）。
9. **Windows 后代回收状态 UNKNOWN** — 脚本已显式记录 `descendants: "UNKNOWN after launcher exit; no job handle"`，**不外推 POSIX orphan 结论**。
10. **清单组织／产权／隐私／法律类**（如第 145、146、147 项）— 代码无法确认，标注为**无法确认**；**某条代码不适用不能取消组织的发布义务**。

**整体完成度**：仍为 **2/17（FR-401／FR-402）**，**不是**整个 Goal／M0／发布完成。本票不增加任何完成度。

---

## 12. 用户原始清单 1–160 逐条

> 判定口径：**适用**（本产品确有此面，本票给出结论）／**部分适用**（有对应面但不完整）／**本轮范围外**（属其他 FR／里程碑，不因本票关闭）／**不适用**（本产品形态下无此面）／**无法确认**（代码/文件无法判定，需人类或组织事实）。
> 每行一条，独立不合并。

| # | 清单项 | 判定 | 依据／缺口 |
| --- | --- | --- | --- |
| 1 | 表结构是先设计而非 AI 即兴逐表拼 | 适用 | `packages/contracts/v2/schema.json` 以 `$defs`＋`oneOf`＋`additionalProperties:false` 定义全部边界；`error3` 每个错误码独立分支。本票实测 schema 增至 11446+ 行。**未覆盖附录 C 构造全集** |
| 2 | 带加号的邮箱也能登录 | 不适用 | 本地单机桌面应用，无账号/登录体系 |
| 3 | 密码重置链接过期且一次性 | 不适用 | 同上 |
| 4 | MFA ＋ 丢失手机恢复路径 | 不适用 | 同上 |
| 5 | 会话超时＋可吊销某用户全部会话 | 部分适用 | 有引擎会话与握手（`engineSessionId`、hello bootstrap、pendingRequests Map），**不是用户账号会话**；"吊销一个用户的所有会话"不适用 |
| 6 | 企业 SSO | 不适用 | 无身份提供方集成 |
| 7 | SAML | 不适用 | 同上 |
| 8 | SCIM 离职即时撤权 | 不适用 | 同上 |
| 9 | 比"管理员/所有人"更细的角色权限 | 部分适用 | 能力注册表＋方法白名单（`mainline.py` `METHODS`、`registry.json` business3 方法表）＋单一 mainline owner 权威；**无多角色体系** |
| 10 | 改 URL 里的一个数字就读到别人的数据 | 适用 | `projectId/detailRef/startOrdinal` 全链绑定：`engine.ts` 校验 `params.projectId === selected.projectId`；引擎 `_OwnershipProof.check()` 校验 owner/reply/store/lease/project/generation/method 并 `authorize`；`detailRef` 读取校验 `origin` 与 `fingerprint`。本地单用户，无跨用户面 |
| 11 | 租户隔离 | 不适用 | 无多租户；最接近的是项目间 owner/project 绑定 |
| 12 | 管理员"登录为该用户"＋审计 | 不适用 | 无多用户；最接近是 ownership 详情的 `origin`（ownerId/hostClientId/engineSessionId） |
| 13 | 登录限流 | 不适用 | 无登录；最接近是引擎帧/页/内存预算与 4299/4300 整数输入上限 |
| 14 | 锁定策略不误锁 CFO | 不适用 | 无账号锁定；受控拒绝不锁死用户（42 INVALID_REQUEST＋1 OWNERSHIP_CONFLICT） |
| 15 | 数据库迁移可正向可回滚 | 部分适用 | 有 format3 迁移（44 条条件 skip：8 format0 creates v1／32 format2 已有 v2／4 空 format0 无 project）。**回滚路径未验** |
| 16 | 迁移不在周二下午锁主表 | 部分适用 | SQLite 单写者＋事务；**并发迁移场景未验** |
| 17 | 索引（50 行到 500 万行） | 部分适用 | 读路径有 SQLite 查询；**容量 Q5/D2 未确认**，无百万级证据。**本轮范围外** |
| 18 | 连接池 | 不适用 | 本地 SQLite 单连接 |
| 19 | 每晚备份 | 不适用 | 无服务端；本地项目包不等于备份 |
| 20 | 从备份恢复且已演练 | 部分适用 | 项目包导入/导出属 FR-203，**本轮范围外**；无备份恢复证据 |
| 21 | 时间点恢复（误删 where） | 不适用 | 无服务端；最接近是版本化提交与历史运行不可改写（FR-804／附录 D.1） |
| 22 | 软删除 | 部分适用 | `facts` 墓碑（`rdf_snapshot.py:64` "managed deletion tombstones are provenance, not facts"）＋映射源行删除不删手工事实（S1 门槛 #2）。**任意误删的产品级回收未验** |
| 23 | 服务端校验而非只在前端 | 适用 | 引擎侧 `iri()`/`term()`＋canonical 精确相等＋`INVALID_REQUEST field=params`；契约侧 zod/`.strict()`＋`contract_v2.py`。**非仅前端** |
| 24 | 时区正确存储 | 不适用 | 无提醒/日程/时间调度功能 |
| 25 | 名字里带撇号的客户 | 适用 | 事实值全参数化 SQL＋canonical JSON＋R06 六处显式 UTF8 修复；`term()` 对撇号/引号字符的 Turtle 解析走确定拒绝路径 |
| 26 | emoji／重音／RTL | 部分适用 | canonical 精确 `term(value).n3()`＋语言标签小写 canonical（en-001／de-CH-1901 正控、混合大小写受控拒绝）；**RTL 双向文本未专门验** |
| 27 | 金额用整数存储 | 不适用 | 无金额 |
| 28 | 多国货币/舍入/税 | 不适用 | 同上 |
| 29 | 数据模型扛得住第二个客户的小改动 | 部分适用 | 数据层次（本体定义/断言事实/当前推导/场景副本/历史运行）＋版本化提交＋`entity_metadata.py` 的受控 vocabulary；"第二客户"不在本地单机范围 |
| 30 | 幂等键 | 部分适用 | `operationId` 存在（draft.save）；**人工事实 ID 内容派生后，重放同一事实报所有权冲突而非幂等成功**（F11，语义待产品裁定） |
| 31 | 连点四次提交去重 | 适用 | UI 侧 `FACT_ALREADY_EXISTS`＋引擎 `reservedIdentity`；Session 的 `sequence` 围栏＋`pending` 禁用。**GUI 未实测** |
| 32 | 第 400 页的分页 | 部分适用 | cursor＋`maxCursorRecords`＋字符上限（历史"43692 分页误因果"已撤回，262144/16MiB 边界另保）；**400 页规模未验** |
| 33 | 导出 | 部分适用 | Turtle 导出属 FR-203／附录 C，**本轮范围外** |
| 34 | 导入（2009 年的 CSV） | 部分适用 | CSV/XLSX 映射属 M2，**本轮范围外**；附录 C 构造子集受控拒绝属 FR-203 |
| 35 | 保留规则与合同一致 | 不适用 | 无合同数据保留；最接近是历史运行不可改写、缓存回收不触及历史 |
| 36 | 密钥不在代码/仓库/AI 对话 | 适用 | 凭据只在主进程；Python 引擎不持密钥、不调模型；仓库禁 `.env`／`.mimosa`。本票未见密钥入库 |
| 37 | 轮换上个月 AI 粘进配置文件的密钥 | 不适用 | 无生产密钥；模型外发 S3 前未接入 |
| 38 | 确认每个被装的包存在且是想要的那个 | 适用 | **本轮实证**：uv.lock→vendored wheel 哈希三方一致；upstream 原版哈希＝PyPI 原版；补丁可重建且与 fr201.3 逐字节相同（§8）。**遗留**：fr201.1/2 无引用（F09） |
| 39 | 依赖扫描 | 部分适用 | `npm ci`＋`uv sync --frozen`＋两份锁文件＋预装 reviewer 受限依赖；**无第三方漏洞/SCA 扫描工具** |
| 40 | 所有可输入处做输入清洗 | 适用 | 引擎 `iri()`/`term()`＋canonical；UI `pattern`/`required`；渲染层无 `innerHTML` |
| 41 | SQLi/XSS/CSRF 等 OWASP | 部分适用 | SQL 全参数化；XSS 由 React 转义＋CSP（`csp.ts` 单一来源）承担；CSRF 在本地 stdio/无导航下适用性弱。**无渗透测试** |
| 42 | 文件上传扫描/限大小/不可执行 | 部分适用 | 项目包导入属 FR-203，**本轮范围外**；无通用上传 |
| 43 | CORS 不是"全放开" | 不适用 | 无 HTTP 服务、不开端口 |
| 44 | 每个响应带安全头 | 适用 | CSP 由 `csp.ts` 单一来源生成生产 meta／开发 header 两变体；生产脚本不得出现 `unsafe-inline`/`unsafe-eval`（AGENTS 不变量，本票未发现违反） |
| 45 | 静态与传输加密 | 不适用 | 本地明文 SQLite，无网络传输。**此为已知形态边界，非本候选引入** |
| 46 | 最小权限，含持生产凭据的 AI Agent | 部分适用 | mainline owner 权威＋`_WriteAdmission`＋proof 绑定＋方法白名单；**模型外发 S3 前不得接入，故"AI Agent 持生产凭据"当前不成立** |
| 47 | 日志记录谁做了什么，不记密码/令牌/卡号 | 部分适用 | 跨边界只传固定错误码＋受限参数；stderr 限量脱敏；新 witness 含 owner/sourceRow/fact id（项目内定位符，非凭据）。**"谁"仅到 engineSessionId/hostClientId** |
| 48 | 企业安全团队前的渗透测试 | 不适用 | 本地桌面应用无外部攻击面；发布门禁另计 |
| 49 | 安全问卷逐条有证据 | 部分适用 | 技术面可答（见 36–47）；**法律/隐私/产权/合规类为组织义务，代码无法确认** |
| 50 | 漏洞披露流程 | 不适用 | 非产品功能；组织义务，**无法确认** |
| 51 | 生产访问笔记本被盗的预案 | 不适用 | 同上 |
| 52 | SOC 2 | 不适用 | 同上 |
| 53 | HIPAA | 不适用 | 无患者数据；组织义务 |
| 54 | BAA（含模型提供方） | 不适用 | 同上；且模型外发未接入 |
| 55 | 审计轨迹显示"谁查看过"而非只"谁改过" | 部分适用 | ownership 详情记录预览来源（`origin` 三元组＋`sourceBaseRevision`）；**无通用记录查看审计** |
| 56 | PCI scope 与卡号不入库 | 不适用 | 无卡号 |
| 57 | GDPR 删除请求覆盖所有表/备份/日志 | 不适用 | 无个人数据处理；最接近是本体事实删除受所有权规则约束 |
| 58 | 数据驻留 | 不适用 | 本地应用 |
| 59 | 季度访问复核签字 | 不适用 | 组织义务，**无法确认** |
| 60 | dev/staging/prod 环境一致 | 部分适用 | 三档：本地 venv／CI 三平台矩阵／本地打包 App；**无独立生产环境配置**；CI 平台差异已显式化 |
| 61 | 基础设施即代码 | 部分适用 | GitHub Actions＋`uv.lock`/`package-lock.json`＋PyInstaller 构建脚本；**本地应用无基础设施** |
| 62 | 部署流水线先跑测试 | 适用 | CI 三 job：check→verify:sources→E2E→package→verify，制品 `always` 上传。**本 head 未 push，无新 CI 运行**（F02） |
| 63 | 一键回滚 | 部分适用 | Git 分支/revert ＋ PR 流程；无发布流水线 |
| 64 | 零停机部署 | 不适用 | 本地桌面更新 |
| 65 | 特性开关 | 不适用 | 无 flag 机制；能力注册表只声明"已实现并验证" |
| 66 | 自动扩缩 | 不适用 | 无服务端 |
| 67 | CDN | 不适用 | 同上 |
| 68 | DNS/SSL 续期 | 不适用 | 无网络服务 |
| 69 | 后台任务队列 | 适用 | Coordinator ExecutionJob（queued→running→succeeded/failed/cancelled，committedProgress 语义在 S2 契约）＋`job_store.py` 有界队列 |
| 70 | 重试与退避 | 部分适用 | S2 门槛要求"引擎崩溃时 pending 清理、状态恢复和退避有测试"，状态表记为已覆盖；**本票未逐条复核退避参数与用例** |
| 71 | 死信队列 | 不适用 | 无外部投递失败语义；job 的 failed/cancelled 终态不等价于 DLQ |
| 72 | cron 不因第二台服务器而跑两次 | 不适用 | 无 cron/多实例部署 |
| 73 | 缓存与数据变化时的失效 | 适用 | `invalidation-v2.json` 为 `staleReason` 唯一来源；附录 D.2 九行正负例已有；**FR200 编辑后的四类具名下游 GUI 未逐类验**（MM D10 仍开） |
| 74 | SPF/DKIM/DMARC | 不适用 | 无发信 |
| 75 | 退信与投诉处理 | 不适用 | 同上 |
| 76 | 存储生命周期规则 | 部分适用 | 各 worktree 独立依赖/构建/临时数据；**无云存储生命周期策略** |
| 77 | 成本告警 | 不适用 | 无云账单；模型外发未接入，故无模型花费 |
| 78 | 灾难恢复预案（年度演练） | 不适用 | 组织义务，**无法确认** |
| 79 | 第二可用区 | 不适用 | 本地应用 |
| 80 | 可检索的结构化日志 | 部分适用 | stdio 一行一 JSON 协议＋stderr 限量脱敏＋本轮新增 `build/engine-tests/` 报告产物；**无集中日志检索** |
| 81 | 错误归并（不刷 4000 封邮件） | 不适用 | 无 Sentry 类；最接近是固定错误码表（UI 17／契约 26／交集 10） |
| 82 | 站外可用性探测 | 不适用 | 本地应用 |
| 83 | 告警到人且不误报 | 不适用 | 组织义务，**无法确认** |
| 84 | 延迟/错误率/吞吐看板 | 部分适用 | 本轮 CI/E2E 报告有 durations/timeout 统计；**无长期指标看板** |
| 85 | 跨服务慢请求追踪 | 部分适用 | requestId/engineSessionId/projectId/jobId 贯穿＋ownership origin＋101 附件关联；**无分布式追踪** |
| 86 | 值班轮转 | 不适用 | 组织义务 |
| 87 | Runbook | 部分适用 | 仓内 ADR/状态/处置表；**无 on-call runbook** |
| 88 | 复盘能改变东西 | 部分适用 | R01–R08 处置链确有意见落到代码：canonical 精确化、写准入、UTF8 显式、CI 两脚本与首败诊断。**属工程复盘记录，非事故复盘制度** |
| 89 | 状态页 | 不适用 | 本地应用 |
| 90 | 由懂逻辑的人写的单测 | 适用 | 本票实核新增 6 个引擎测试＋8 个 TS 测试＋1748 行 e2e；**断言面向真实需求与错误边界**（如 canonical 精确拒绝、50 原条件 skip、冲突 witness）。**作者为 AI，人工签字见第 148 项** |
| 91 | 每个第三方 API 的集成测试 | 部分适用 | 真实第三方库 rdflib/pyparsing/pyshacl 由真实依赖驱动并有回归；**无外部服务集成测试** |
| 92 | 注册/结账等赚钱流程的 E2E | 不适用 | 无此流程；最接近是 FR200/201 真实表单 CRUD 6 例＋CSP＋ACK-loss（24 例 21PASS/3 原 skip） |
| 93 | 上线前负载测试 | 不适用 | 无并发用户；容量 HOLD |
| 94 | 似真非真的测试数据 | 适用 | G-base／G-map-empty／G-behavior／E.5 固定样例＋独立生成器（不冒用同 ID 扩容） |
| 95 | 回归测试（修 41 不带回 12） | 适用 | 3769 项 Python＋1892 项 Vitest＋`binding-regressions.json`＋历史绑定回归 |
| 96 | 五年前的旧笔记本 | 未验 | 参考设备 HOLD；**无法确认** |
| 97 | 无障碍合规 | 部分适用 | 新视图用 `dl/ol/h2/h3`＋`role="alert"`/`role="status"`/`aria-label`；**无 axe/屏幕阅读器实测，无正式合规结论** |
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
| 108 | 版本化 API | 适用 | v2 协议＋`protocolVersion`＋方法白名单＋`registry.json` 哈希绑定＋schema；本候选新增方法已同步 registry/schema/TS/Python 四处 |
| 109 | 客户可创建/吊销的 API Key | 部分适用 | 无用户 API Key；最接近是 owner 绑定＋mainline 权威＋模型外发未接入 |
| 110 | 保护而不误伤真实集成的 API 限流 | 适用（部分） | `limits`/`maxFrameBytes`/`maxPageBytes`＋预算 `reserve` 逐段计费；**无限流服务** |
| 111 | 第三方 API 改响应格式的预案 | 部分适用 | rdflib 为 vendored 固定版＋PROVENANCE＋可重建补丁 → 变更面受控；**通用第三方变更无预案** |
| 112 | OAuth 令牌刷新 | 不适用 | 无外部身份 |
| 113 | 客户可测试的沙箱 | 不适用 | 无外部集成方；最接近是内置离线示例＋场景副本隔离 |
| 114 | 到达模型的每个字段都防提示注入 | 不适用 | **模型外发 S3 前不得接入，无 prompt 通道** |
| 115 | 客户/患者数据不出网进 prompt | 不适用 | 同上；本地优先不外发 |
| 116 | 每客户模型花费上限 | 不适用 | 同上 |
| 117 | 模型更新变差时的 eval | 部分适用 | 本地确定性引擎＋附录 G 固定预期可作规则/模型回归基线；**无 LLM eval** |
| 118 | 模型服务宕机的降级 | 不适用 | 无模型接入 |
| 119 | 模型弃用的迁移预案 | 不适用 | 同上 |
| 120 | 调试用 prompt/output 日志 | 不适用 | 同上 |
| 121 | 不可撤销的 AI 行为须人工确认 | 适用 | 提交仅经显式人类确认按钮（源码注释："Called only by the explicit human confirmation button after displaying all rows"）；Agent 只产草稿 |
| 122 | 酒店 WiFi 下能打开的页面 | 不适用 | 本地应用，无网络依赖 |
| 123 | 每个界面的空/加载/错误态 | 适用 | `ownershipDetail` 的 `'reading'｜'unavailable'｜'ready'` 三态＋`formError`/`state.error` 的 `role="alert"`＋`stale`/`pending` 态 |
| 124 | 可操作的错误消息 | 部分适用 | OWNERSHIP_CONFLICT 有专门文案与"首个阻断冲突定位"视图；**42 个 INVALID 仍共用单一固定文案**（历史事实保留） |
| 125 | 校验失败保留已填内容 | 适用 | 渲染层"已输入内容保留"＋本地事实编辑失败不清空＋表单 state 保留 |
| 126 | 邮件在各客户端正常渲染 | 不适用 | 无发信 |
| 127 | 可关闭的通知 | 不适用 | 无推送/邮件 |
| 128 | 撤销 | 部分适用 | 入口与准备链在树中（按钮→`prepareUndo()` 重读基准→`intent:'undo'`）；**GUI 路径未实测，HOLD** |
| 129 | 键盘导航与屏幕阅读器 | 部分适用 | 语义标签与 `role` 到位；**无实测**（同 97） |
| 130 | 多语言与本地化日期/数字 | 部分适用 | 中文界面文案＋语言标签小写 canonical；**无 i18n 框架与 locale 格式化** |
| 131 | 符合预期的返回按钮 | 不适用 | 桌面单页，无路由历史 |
| 132 | 人能读的代码 | 部分适用 | 严格类型＋zod＋显式预算与门禁注释；**但存在高密度状态机**（`_WriteAdmission`、`account()`），理解成本高 |
| 133 | 每次变更都做代码评审 | 适用 | 本 R08 为新一轮；历史 R01–R07 有处置链与独核 |
| 134 | 分支策略 | 适用 | `develop` ＋ `feature/weekly-*` ＋ 独立 worktree ＋ PR16；AGENTS.md 规定"并行开发为默认执行要求" |
| 135 | 每月依赖升级 | 部分适用 | 锁文件随改动提交＋`--frozen`；**无月度升级节奏记录** |
| 136 | 框架在停止安全补丁前升级 | 部分适用 | 版本固定（Electron/React/Vite/pytest/ruff）；**无 EOL 跟踪记录** |
| 137 | 删掉 AI 前几次尝试留下的死代码 | 部分适用 | **本轮实证**：vendor 内 fr201.1/fr201.2 共 4.76 MB 无引用（F09） |
| 138 | 拆分 AI 不断追加的 2000 行文件 | 适用 | `mainline.py` 50 KB（+417 行）；本轮新增按职责拆为 `mainline-ownership.ts`／`OwnershipConflictDetailView.ts`／`engine-test-reporting.py`／`run-engine-tests.py` |
| 139 | 写下来的架构决策与理由 | 适用 | ADR-0001／ADR-0002（`docs/iterations/I01/`）＋本票七轮处置表与版本图 |
| 140 | README 让新工程师 1 小时内跑起来 | 部分适用 | AGENTS.md 有仓库地图；**README 未由本票读，不作断言** |
| 141 | 留给继承者的文档 | 部分适用 | `status.md`＋`m0-checklist.md`＋各轮处置表；**无独立交接文档**；且 F05 显示状态源会滞后于 head |
| 142 | 运维用的管理后台 | 不适用 | 本地单机无运营团队；最接近是本体管理界面本身 |
| 143 | 客服自助工具 | 不适用 | 无客户成功团队；最接近是面向用户的 ownership 冲突定位视图 |
| 144 | 客户可读的变更日志 | 部分适用 | 仓内无 CHANGELOG（本票未核）；有各轮处置记录 |
| 145 | 条款与隐私政策与代码一致 | 无法确认 | 组织/法律义务；**代码不适用不等于义务取消** |
| 146 | 账号/域名/仓库用公司名而非原型作者名 | 部分适用 | Git 远端为 `NOmoreJoke/...`（本人从 `git branch -vv` 读到）；**归属决定属人类/组织，代码无法决定** |
| 147 | bus factor 大于 1 | 无法确认 | 代码可证存在多开发者线与双审流程；**人的因素无法从代码确认** |
| 148 | 上线前由资深工程师逐行读 AI 写的每一行 | 适用 | **本票由 AI 审查者执行，不构成人类资深工程师签字**；§3.3 已披露子代理使用。人类签字仍缺（既有 HOLD） |
| 149 | 第二个客户来之前先设计数据模型 | 部分适用 | 本票实读 ADR-0002、附录 C/D.2 与 `entity_metadata.py`；**设计责任主体仍需人类后端工程师** |
| 150 | 解释 AI 的一个修复为何引出两个新问题 | 部分适用 | 本票以可复算证据给出解释（如 canonical 精确化 → 语言标签大小写敏感 → 需区分"合法非规范"与"非法"；CI 两脚本 → rootdir 推断污染 → 私有参数形态）。**解释责任的正式承担仍需人类资深工程师** |
| 151 | 部署/回滚/服务器/云账单 | 部分适用 | 本票实核 CI workflow（3 job／15-20 分钟／SHA 固定 actions）；**无服务器与云账单**（本地应用） |
| 152 | 支付停了谁接 3am 电话 | 不适用 | 无支付；组织义务 |
| 153 | 漏洞公开当周修补框架 | 部分适用 | 锁文件＋`--frozen`＋无 SCA；**无 CVE 跟踪记录** |
| 154 | 带审计员讲清患者数据如何流动 | 不适用 | 无患者数据；组织义务 |
| 155 | 测试 AI 说它测过的东西 | 适用 | **本票对 O056 的 11 项声明做了独立复算，11/11 确认，并指出 5 处口径/归属注记**（§9） |
| 156 | 在活库上跑迁移且不丢行 | 部分适用 | `Store.commit` 原子＋旧基线拒绝＋44 条迁移条件 skip；**"不丢行"在本地条件 skip 语境下未穷尽** |
| 157 | 对会破坏三个其他功能的特性说不 | 部分适用 | 既有范围纪律记录在案（ZCode §4.1 归后续被拒、D8 choice-A 不扩功能/预算/付费）；**决策主体仍需人类 tech lead** |
| 158 | 把"我机器上能跑"变成"每个客户都能跑" | 部分适用 | 本票确认 3 job 矩阵与 Windows 特定化配置；**本 head 未在 CI 上运行**（F02） |
| 159 | 在写它的 AI 搞不定时调试代码 | 适用 | 本票对 fr201.3 供应链（§8）与 CI 控制层（§6）做了独立可复算核验，并给出具体可执行结论 |
| 160 | 一年后还记得为何如此构建 | 适用（部分） | ADR＋处置表＋状态表承载；**但 F01／F05 显示"记忆载体"会与 head 脱钩**——本票因此把 F05 列为 P2 而非"已完备" |

---

## 13. 最终判断（明确四句）

1. **本地实现**：**通过**。未发现 push 前必须修复的源码技术阻断。最高级别问题为 P2（F03–F08），均为一致性／可追溯性／流程类。
2. **本地验收**：**通过（证据为他人运行，本票独立复算未重跑）**。O056 十一项声明 11/11 确认；本票另行独立完成四项纯计算核验（SHA-256 对拍、补丁重建、哈希链、契约双实现判据比对）。
3. **有无 push 前源码技术阻断**：**无**。但有 **2 条 P1 流程阻断**（F01 审查覆盖缺口、F02 零 CI 数据）与 **6 条 P2** 需在合并前处置或书面归口。
4. **哪些必须等 push 后真实 CI 才 merge**：**全部 Windows／Quality 完整性结论**。合并必须以**本 head `62d4b0a`** 的真实三 job 回单为准，具体：Windows 完整 3769 每项最终 PASS 或原有有据 skip、**自然 0**、无失败／早停／取消／timeout／NOTRUN；其后 typecheck／build／E2E／package／verify 及原 3 job 实际 success；Quality 专用步骤与 packaged recovery 步骤**自身 success**。**任何分片较早 0 或总数统计都不能代证完整**；**新绿不倒填旧 79F 因果**。

**不予放行的其他必要条件**：F05 状态源追加当前候选；F03 的 Windows 验收口径裁定；F04／F06／F07 的处置结论（可书面延期，但须归口到具体 owner 与事件窗口）。

**本票不构成**：人类资深工程师签字、指定外审、完整候选双 Pass、Windows CI 通过、package/release 通过、父 FR／附录 C/D/E/G 整体通过。**整体合并可用仍为 2/17（FR-401／FR-402），Goal／M0／发布均未完成。**

---

## 14. 报告边界与不作断言清单

- 本票**未运行** npm／check／vitest／pytest／ruff／build／package／install／sync／HMR／GUI／产品／SQL／probe 中任何一项；**未改** index／commit／push／branch／remote；**未读**密钥、无关 profile 或用户 `.mimosa` 数据。
- 本票**唯一**仓库写入为本文件（`docs/reviews/T02/fr200-fr201-20261024/round-08/minimax-m31flash.md`）。**未写入**对方报告，**未另起**仓内文件，**未改写** round-01/02/03 的未跟踪 WIP、旧报告或旧 094 产出。
- 本票**未读取**对方 R08 正文任何字节（见 §0.3 的诚实披露）。
- 凡标注"**无法确认**"者，均为代码与仓库文件无法判定、需人类或组织事实的事项；本票不为其编造结论。
- 凡标注"**本轮范围外**"者，均**不因本票关闭**，归属仍在其他 FR／里程碑的 owner。
- 本票在临时目录做了 8 组纯计算核验，方法与边界已在 §3.1 逐条披露；**未导入、未执行产品代码**。
- 若后续需要新增产品验证才能关闭某条判断，本票在对应条目写明**具体证据缺口**（如 F02 的三 job 回单、F08 的 GUI 实测、§12 第 73 项的四类具名下游），由原开发会话受控执行；**不因本票无法执行而假报通过**。

---

## 15. R08 事实补充 v1（2026-10-26 · 共享事实文件核验后的条目修订）

> **版本标识**：本节为 R08 报告的**追加补充 v1**，追加于 2026-10-26。
> **不覆盖、不改写、不删除**上文任何字节；上文 §0–§14 的全部结论、160 条清单与 78 个历史位置**完整保留**，凡与本节冲突处以本节为准并显式标注被修订条目。
> 本节**不静默关闭任何意见**：每处修订都给出原表述、修订后表述、证据与严重级变化。
> 本节**不构成**另一方报告的引用、复述或代证；另一方 R08 正文本票**仍未读取**（见 §0.3 与 §15.0）。

### 15.0 补充身份、来源与独立核验边界

**事实文件（两方同一份）**：

| 项 | 声明值 | 本人实测 | 判定 |
| --- | --- | --- | --- |
| 路径 | `iteration-control/2026-10-21-weekly-release/six-patches-20261023/controller-t02-62d4b0a2-r08-shared-evidence-boundaries-20261026.md` | 同 | ✅ |
| 字节 | 7917 B | **7917 B** | ✅ 精确匹配 |
| SHA256 | `e549fa97ca1f5a2af0c30bee8f7cd14ff3e143d65ccc594dcc7f79c3cea23cb9` | **同值** | ✅ 精确匹配 |

**受审身份再确认**：base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `62d4b0a2c3ad49ae37775b875a3e7e31db5fadac` / tree `7ad1d13d6a064aaa07bd046e78427e881e1732b4`。**冻结候选未修改**：本补充全程只读，仓库唯一写入为本文件本节。

**我实际重读并核验的原件**（不是依事实文件摘要转述）：

1. `apps/desktop/src/main/desktop-ipc.ts` —— **全文 215 行**（含 `register()` 包装、`trusted(event)` 前置校验、mainline 交付/ACK 与 sender/frame/session 绑定）。
2. `apps/desktop/src/main/engine.ts` —— `MainlineMethod` 联合类型（330–360 行）、`#request` 方法白名单与参数/预算/发送段（1214–1275 行）。
3. `apps/desktop/src/main/project-mainline-service.ts` —— 255–454 行（`#current`／`#client`／`#run`／`#call`／`#selection`／`#invalidateRecovery`／`source` fence 回调）与 536–596 行（`saveProjectDraft`／`getOwnershipConflictDetailPage`／`readProject` 三者守卫逐条对比）。
4. `packages/contracts/v2/schema.json` —— `params_project.ownership.detail`、`result_project.ownership.detail`、`ownershipDetailHeader` 三定义原文。
5. `packages/contracts/src/v2.ts` —— `compile()` 数组/对象/字符串分支（70–140 行）与 `validateBusiness3`（445–462 行）。
6. `packages/contracts/python/contract_v2.py` —— `ownership_detail_matches`（含数组 `minItems` 校验行 97）。
7. `packages/engine/src/ontolearn_engine/job_store.py` —— `ownership_detail_page` 的 `chosen` 装配与 `if not chosen: fault("RESOURCE_LIMIT")`（962–966 行）。
8. `tests/e2e/t02-ontology-mainline.spec.ts` —— 300–432 行 Undo/Redo/owned restart 全链。
9. `tests/e2e/t02-fr200-fr201.spec.ts` —— 725–790 行 `rejectCallerObject`、945–990 行 xsd:string 别名负例。
10. `packages/engine/tests/test_project_format3.py` —— 文件头、`frozen()`、`test_explicit_gate_backup_and_full_domain_history`、`test_migration_atomic_faults` 参数化与注入体。
11. O056 原件 —— `native24-config-fixed/report.json`（24 specs 逐条 status/retry/duration）、`attachments/078-t02-real-m-undo-restart.bin`（字节+哈希+语义解析）、`full-mode2-config-fixed/run-30cfd5248084418fb6a3a725cb02aae3/summary.json`（3769 outcomes 逐 node 统计）。
12. `.github/dependabot.yml`（279 B 全文）、`.github/` 目录清单（**无 CODEOWNERS**）、`.github/workflows/ci.yml` 全文（**无 audit/dependabot/snyk/osv 步**）。

**我未做**：未读取另一方 R08 报告任何字节；未运行 npm/check/vitest/pytest/ruff/build/package/install/sync/HMR/GUI/产品/SQL/probe；未修改实现/配置/依赖/测试/验收；未访问用户库或私有 app 存储；未改 index/commit/push/branch/remote；未重放或回填任何旧 CI 失败。

### 15.1 §5 主进程三处 delta 的独立语义结论（本补充新增）

事实文件只给定位与行数，并明确"这些数字只是定位，不是正确性证明"。以下是我逐行读完三处 delta 及其权限/选择/transport 上下文后的独立判断。

#### 15.1.1 `desktop-ipc.ts`（+3／−0）

- 新增 `handlers['project:ownership-detail']` → `projects?.getOwnershipConflictDetailPage(args) ?? Promise.resolve(permission())`，与同组 `project:read`／`project:changeset-preview` **同构**。
- 新增 `register('project:ownership-detail', handlers['project:ownership-detail'])`，走**同一个 `register()` 包装**，因此继承全部既有安全属性：`trusted(event)` **先于任何下游调用**（第 160 行）；因 channel 以 `project:` 开头且非 `project:active`，被判为 mainline（第 161–163 行）→ **强制经过 `replies.receive()` 交付/ACK 协议**、`deliveries.size >= 16` 上限、**sender + senderFrame + engineSessionId 三元绑定**（第 177–184 行）；缺 `projects` 或 `replies` 时 fail closed 为 `PERMISSION_DENIED`。
- **通道名一致性**：`DesktopIpcMap['project:ownership-detail']`（contracts `src/index.ts`）、preload 的 `receiveMainline('project:ownership-detail', args)`、本文件的 handler 与 register —— **四处字符串同源无漂移**，本票逐一核对。
- **结论**：**未新增信任面、未引入通用 `invoke(method, params)` 式通道、未绕过可信来源校验**。符合 AGENTS.md「preload 只暴露按业务命名的方法」「IPC 处理器保持 sender/mainFrame/可信文档校验」两条不变量。**无阻断**。

#### 15.1.2 `engine.ts`（+5／−1）

- `MainlineMethod` 联合类型新增 `'project.ownership.detail'`（类型面）。
- `#request` 的方法白名单新增同名项 —— **缺此项该方法会在 transport 层被 `invalid()` 直接拒绝**，故此行是必要而非冗余。
- `validateBusiness3('params_project.ownership.detail', params)` 前置于 `budget.reserve` 与 `#send`。
- 新增分支：`params.projectId !== record.selected?.projectId` → `deniedOrdinary()`。
- **我额外核到的一点（事实文件未提，也是我在 R08 读到 TS 类型时主动复核的）**：渲染层 TS 类型 `OwnershipDetailArgs` **不含** `projectId`，而 wire schema `params_project.ownership.detail` **必填** `projectId`（`additionalProperties:false`）。二者**不矛盾**：渲染层不提供、由主进程服务层注入（见 15.1.3）。schema 必填 projectId 使 `engine.ts` 的 current-project 比对**有确定取值**，不会出现 `undefined` 恒拒。
- **参数面比 `project.read` 更严**：`project.read` 无此比对，`project.ownership.detail` 显式要求且必须等于当前选中项目。
- **结论**：**未放宽任何权限面**；新增读通道在 transport 层受白名单、schema、预算与当前项目四重约束。**无阻断**。

#### 15.1.3 `project-mainline-service.ts`（+24／−0）

`getOwnershipConflictDetailPage` 的完整守卫链（读 555–579 行）：

1. `#current()` —— 要求 `source.current()` 存在、未 `closed`、且 **`current.engineSessionId === supervisor.engineSessionId`**（404–409 行）。
2. `#client()` —— 要求未 `closed` 且存在 mainline client（398–403 行）。
3. 记 `epoch = this.#selectionEpoch`。
4. **调用前**：`if (client.owner !== current.owner) throw denied()` —— owner 绑定。
5. 调用时注入 `projectId: current.project.projectId`（**不信任调用方传入的 projectId**）。
6. **返回后**复核四項：`#selectionEpoch !== epoch`、`source.current()?.owner !== current.owner`、`source.current()?.project.projectId !== current.project.projectId`、`client.engineSessionId !== current.engineSessionId` → `denied()`。

**与既有方法逐条对比（我实测）**：

| 方法 | 调用前 owner 比对 | 返回后 selection epoch 比对 | 返回后 owner/projectId/session 比对 |
| --- | --- | --- | --- |
| `readProject` | 无 | 无 | 有（3 项） |
| `saveProjectDraft` | 无 | 无 | 有（3 项） |
| **`getOwnershipConflictDetailPage`（新）** | **有** | **有** | 有（3 项） |

**新方法严格强于 `readProject`**，与 `saveProjectDraft` 同级或更强。

**`#selectionEpoch` 语义已核**：`source` 的 fence 回调（第 264–275 行，用户清空/切换项目时触发）→ `#invalidateRecovery()` → `epoch++`（314–322 行）；`#selection()` 亦先 `#invalidateRecovery()` 再取 epoch（446–454 行）。**故用户切换项目必然使 epoch 变化，在途调用被拒**——不是仅在崩溃/恢复路径才递增。

**错误面收敛已核**：`#run()`（415–427 行）把任何异常收敛为 `safeError`／`safeDisplayError` 的**固定错误码**，**不跨边界回传原始异常、堆栈、路径**；`#call()`（428–439 行）把 transport 失败包成 `EngineError` 并交由 `supervisor.projectFailure` 投影。

- **结论**：该 ownership-detail 读通道的**权限绑定、选择生命周期、会话绑定与错误收敛四项均闭合**，**未发现越权读取、跨会话读取、选择竞态泄漏或原始异常外泄**。**无阻断**。

#### 15.1.4 三处合起来的一句话结论

**新增的 `project.ownership.detail` 是一条项目内、项目内 owner 绑定、当前选择绑定、当前引擎会话绑定、只读、分页、有预算、有 schema 全约束的读通道；它没有新增任何信任面，也没有绕过既有 IPC/transport 不变量。本票未在该闭包内发现真阻断。**

### 15.2 §1–§4 逐节独立核验结论

| 事实文件主张 | 我实际核到 | 判定 |
| --- | --- | --- |
| §1 Undo 链源码在 `t02-ontology-mainline.spec.ts`，约 349–361 行两次点「预览撤销本次修改」，380–425 行重开 owned profile 并读回三个原 Job/operation | 行号与语义**逐条属实**：确为两次点击、两次独立完整 Diff（reverse `before:expected→after:null`；forward 复用 createDiff）、`confirmAndRead` 依次产出 undone/rev2、redone/rev3，随后 `electron.launch({args:[...,'--user-data-dir='+owned.userData]})`、按 `data-project-id` 显式打开同一项目、读回三个 Job/operation | **成立** |
| §1 O056 中该例 passed、4920ms、retry0 | report.json 第 **18** 条 spec（`t02-ontology-mainline.spec.ts:301`）：`status=passed`、`duration=4920`、`retry=0` | **成立（数值精确）** |
| §1 附件 078 = 25671 B / `448a3494…` | 本人实测 **25671 B**、SHA256 **`448a3494aea1e222e6b3e4cdf41ff60fdf7c3d97d3ec21d35bca3935c428f60b`** | **成立（精确匹配）** |
| §1 stage=completed；committed/undone/redone 的 projectRevision 为 1/2/3；三个 Job 均 succeeded 且 jobId、operationId 各自唯一；undone.after.domain.state==initial；redone.after.domain.state==committed；reopened.domain 与 inputSnapshotId 均等于 redone.after | 本人解析附件：`stage=completed`；**committed=1、undone=2、redone=3**（initial=0）；三个 `job.state=succeeded`；**jobId 唯一集 3、operationId 唯一集 3**；四条等式**全部为 True**；`owned.userData === owned.sessionData`（同一 owned profile） | **成立（语义逐条复核）** |
| §1 只证明这一条链，不能全称全部 Undo GUI 未验，也不能反向解除其它 Undo/ownership/故障家族 | **同意该限定**，本票据此只收窄 Undo 的**已验子集**，不关闭其它面（见 15.3） | **成立** |
| §2 `rejectCallerObject` 在 `t02-fr200-fr201.spec.ts:731`；762–775 行对 subject/predicate/object 执行 toHaveValue；953–984 行 xsd:string 别名负例同样断言输入值保留、无静默规范化 | `const rejectCallerObject = async (` 确在 **第 731 行**；区间内确有 `toHaveValue(retained.*)`（填值前）与 `toHaveValue(entered.*)`（受控拒绝后）两组断言；953–984 确为 `"typed string"^^<xsd:string>` 别名负例，含 `await expect(objectInput).toHaveValue(alias) // No silent normalization.` | **成立**（行段归属有一处轻微不精确，见 15.3 第 8 条注） |
| §2 不能从完整 Read 相等推 UI 保留，这里另有真实字段断言 | 同意：源码确有 `toHaveValue` 级字段断言，且**另有** `completeDiff` count 0、`confirmation` count 0、`after == before` 三项，**强于**事实文件的描述 | **成立且证据更强** |
| §3 `test_project_format3.py` 文件头即"Private Store-ready acceptance on synthetic databases only; no business3/Job-ready" | 文件第 1 行**逐字一致** | **成立** |
| §3 `test_migration_atomic_faults` 用真实临时 SQLite 合成夹具、source version 0/1/2、显式 `Store(target_format=3, backup_path=...)`、对具名 phase 注入 RuntimeError/KeyboardInterrupt/OSError 或子进程 `os._exit(79)` | 全部属实：参数化 `version[0,1,2] × MIGRATION_PHASES × failure[exception,cancel,disk,exit]`；`exit` 分支确用**子进程 `os._exit(79)`**（真实崩溃注入，非 mock）；`exception/cancel/disk` 分别注入 RuntimeError/KeyboardInterrupt/OSError | **成立** |
| §3 约 159–210 行有 after_commit 格式检查、此前失败的 frozen 前后相等、存在备份的 frozen 相等及 lifetime lease 可重新获取 | 逐条属实：`if phase == "after_commit": assert frozen(path)["format"] == 3`，否则 `assert frozen(path) == before`；`if backup.exists(): assert frozen(backup) == before`；末尾 `format3.acquire_lease(path)` 后 `lease.close()`（失败/退出必须释放 lifetime lease） | **成立** |
| §3 mode2 记录中 nodeid 前缀 `test_project_format3.py::test_migration_atomic_faults[` 恰 **468** 项＝**424 passed + 44 skipped** | 本人对 O056 `summary.json` 的 3769 条 outcomes 逐条统计：**468 / 424 passed / 44 skipped**，与声明**逐位一致** | **成立（精确）** |
| §3 `test_explicit_gate_backup_and_full_domain_history` 单独 passed；约 98–126 行检查 backupRequired、显式 target3 升级、备份与原 snapshot/commit 历史、default FORMAT_VERSION2 拒 future-format、显式 3 重开保留 commits | 该 nodeid 在同一记录中 **passed**（setup/call/teardown 全 passed）；源码语义逐条属实，且**比描述更多**：另含 `app_format` 证据行的 `source_format=2` 与 `backup_hash = sha256(backup.read_bytes())` 物理哈希自洽断言 | **成立** |
| §3 44 是原格式没有对应阶段的条件 skip，不能当执行通过 | 属实：源码 skip 理由为 `only format0 creates v1`／`format2 already has v2 tables`／`empty format0 has no projects`；**本票另核**：全部 50 个 skip 的分布为 `test_project_format3.py` **44** ＋ `test_windows_example_resource.py` **6**，与本票 R08 §11 的"44 migration 条件 + 6 Windows 条件"完全吻合 | **成立** |
| §3 `frozen(path)` 是 logical_hash/user_version/snapshot rows 的逻辑观察，不是完整物理字节比较 | 属实：`frozen()` 仅取 `{dump: logical_hash(con), format: PRAGMA user_version, snapshots}`；物理字节哈希只出现在 `app_format.backup_hash` 对**备份文件**的自洽断言上 | **成立** |
| §4 `.github/dependabot.yml` 已配置 npm 与 github-actions 的 weekly 更新、target develop | 属实：279 B，两个 ecosystem（npm、github-actions），`interval: weekly`，`target-branch: develop`；npm 另有 `open-pull-requests-limit: 5` | **成立** |
| §4 该配置不证明实际运行/合并处理记录、uv/vendor 自动更新、漏洞扫描开关或人类修复 SLA 已核验 | 属实：配置内**无** uv/pip ecosystem 条目；无任何实际 PR 运行/合并记录；无 SLA 字段 | **成立** |
| §4 仓内 ci.yml 没有显式 npm/uv audit 类步骤，但不能据此断言 GitHub/整个组织不存在外部扫描 | 属实：我对 ci.yml 全文 grep `audit\|dependabot\|snyk\|osv` → **0 命中**；仓库内也无 CODEOWNERS | **成立** |
| §4 无真实人类团队人数或创始人身份证据；组织/产权/实际数据类别/法律角色无法由代码认证 | 属实：`.github/` 下无 CODEOWNERS、无 CONTRIBUTING/MAINTAINERS；仓库材料中无人名 roster | **成立** |
| §4 内容ID/操作声明/冲突围栏可形成相关防护，不等于"四连击只提交一次"的实际 GUI 运行记录；本轮未提供特定四连击新实跑 | 属实：O056 的 24 specs 中**无**四连击场景；我另核 24 条 spec 标题，无一条是重复提交/连点 | **成立** |
| §4 当前源码 grep 无凭据模式不证明全部 Git 历史/所有 AI 聊天没有密钥 | 接受。本票 R08 §12 第 36 项的措辞需按此收窄（见 15.3 第 9 条） | **成立** |
| §1–§5 不改变需求、验收标准、capacity、代码、依赖或测试；不解除签名/公证/wholeApp法律/_distutils/目标平台/参考设备/损坏SQLite/其它未验 Undo/ownership/下游/未知退出码等 HOLD；仍 2/17、未合并 | 接受。本票据此**不关闭**任何 HOLD，仅收窄 Undo 的已验子集（15.3 第 1–3 条） | **成立** |

### 15.3 受影响条目修订（逐条，含严重级变化）

> 修订只针对**本票自己已写的表述**。每条给：被修订位置 → 原表述 → 修订后表述 → 依据 → 严重级/结论是否变化。
> **原 160 条与 78 个历史位置均完整保留**，本节只标注"本版修订/收窄"，不删除原行。

| # | 被修订位置 | 原表述 | 本版修订 | 依据 | 结论变化 |
| --- | --- | --- | --- | --- | --- |
| 1 | §7.3 第 3 项（第 307 行） | "**Undo**：入口与准备链在树中…**GUI 路径未实测**，保持 HOLD。" | "**Undo（收窄）**：定义类、已执行输入/影响范围的 **GUI Undo → Undo-of-Undo(redo) → owned profile 重开并读回持久状态与三个原 Job/operation 链已在 O056 实跑通过**（passed／4920ms／retry0；rev 1→2→3；三个 Job succeeded、jobId 与 operationId 各唯一；undone.after.domain.state==initial、redone.after.domain.state==committed、reopened.domain/inputSnapshotId==redone.after）。**其余 Undo 面仍未验**：实例事实撤销、批量/多记录撤销、跨项目选择变更后撤销、跨引擎会话/崩溃后撤销、ownership 冲突面撤销、映射/派生结果撤销。**保持 HOLD（子集收窄，不全称关闭）。**" | 15.2 §1 全部实测（源码＋附件字节＋语义解析） | **原表述为全称过度声明，本票自行更正**；不改变整候选结论 |
| 2 | §11 第 5 项（第 438 行） | "**Undo GUI** — 源码在、GUI 未实测。" | "**Undo GUI** — 源码在；**已验子集**（定义类 Undo/Undo-of-Undo/owned restart）见 15.3-1；**其余 Undo 面与全部其它 HOLD 保留**。" | 同上 | 严重级由"HOLD（未验）"改为"**HOLD（子集已验，其余未验）**"，**不关闭** |
| 3 | §12 第 **128** 条（原第 583 行） | "撤销 \| 部分适用 \| … **GUI 路径未实测，HOLD**" | "撤销 \| **部分适用** \| 源码入口与准备链在树中；**已验子集**：定义类 Undo/Undo-of-Undo/owned restart 的真实 GUI 执行（O056 passed，rev 1/2/3，三 Job 唯一且 succeeded，状态等式成立）。**未验**：实例事实/批量/跨选择/跨会话/崩溃后/ownership 面撤销。**HOLD 按子集保留**" | 同上 | 判定仍为"部分适用"，**证据基础由源码层推断升为已执行 GUI 断言** |
| 4 | §12 第 **15** 条（原第 470 行） | "数据库迁移可正向可回滚 \| 部分适用 \| 有 format3 迁移（44 条条件 skip：8 format0 creates v1／32 format2 已有 v2／4 空 format0 无 project）。**回滚路径未验**" | "数据库迁移可正向可回滚 \| **部分适用（本版精确化）** \| **前向迁移：已验**（合成 format0/1/2 → 显式 `Store(target_format=3, backup_path=...)`，Store 层；含 backupRequired 闸门与 history 保留）。**失败回滚：已验为『失败原子中止』**——注入异常/取消/磁盘错误/子进程 `os._exit(79)` 后源库逻辑状态与备份均等于 before，lifetime lease 可重新获取。**降级：显式不支持**（`Store(path)` 对 future format 抛 `Unsupported future project format`）。**44 条是条件 skip、非执行证据**（跳过理由逐条在源码）；`frozen()` 是逻辑观察、非源库完整物理字节比较。**不证明**业务 Job-ready、人工 schema 降级、大规模活库、无锁或损坏 SQLite 物理资源保护" | 15.2 §3 全部实测（源码＋468 node 状态） | 判定仍"部分适用"，**证据由『回滚路径未验』精确为『失败原子中止已验／降级显式拒绝』** |
| 5 | §12 第 **135** 条（原第 590 行） | "每月依赖升级 \| 部分适用 \| 锁文件随改动提交＋`--frozen`；**无月度升级节奏记录**" | "每月依赖升级 \| 部分适用（**本版更正原措辞**） \| 锁文件随改动提交＋`--frozen`；**`.github/dependabot.yml` 已配置每周自动更新 PR**（npm、github-actions，target develop；npm 限 5 个并发 PR）。**uv/vendor 生态未覆盖**；**实际运行/合并记录与人工修复 SLA 未核验**" | 15.2 §4（dependabot.yml 全文实测） | **原措辞过强，本票自行更正**；判定不变 |
| 6 | §12 第 **136** 条（原第 591 行） | "框架在停止安全补丁前升级 \| 部分适用 \| 版本固定…；**无 EOL 跟踪记录**" | "框架在停止安全补丁前升级 \| 部分适用（本版补充） \| 版本固定（Electron/React/Vite/pytest/ruff）；**github-actions 由 dependabot 每周覆盖**；**应用框架栈未被自动更新覆盖**；无 EOL 跟踪记录 | 同上 | 判定不变，覆盖面描述补全 |
| 7 | §12 第 **39** 条（原第 494 行） | "依赖扫描 \| 部分适用 \| …**无第三方漏洞/SCA 扫描工具**" | "依赖扫描 \| 部分适用（**本版更正原措辞**） \| `npm ci`＋`uv sync --frozen`＋两份锁文件＋dependabot 每周更新 PR。**仓内 ci.yml 无显式 npm/uv audit 步**（已 grep 确认）；**pin/frozen 本身不是漏洞扫描**；**平台侧/组织级外部扫描（如 Dependabot alerts）是否存在，本票无法从仓库确认**" | 15.2 §4 | **原措辞把『仓内无』写成了『无』，属过度断言，本票自行更正**；判定不变 |
| 8 | §12 第 **125** 条（原第 580 行） | "校验失败保留已填内容 \| 适用 \| 渲染层'已输入内容保留'＋本地事实编辑失败不清空＋表单 state 保留" | "校验失败保留已填内容 \| **适用（本版补强证据基础）** \| 源码层机制如原述；**并有已执行 GUI 字段级断言**：受控拒绝后 subject/predicate/object 的 `toHaveValue(entered.*)` 与填值前 `toHaveValue(retained.*)` 均成立，且 `完整事务差异` 与 `确认提交` 按钮 count 为 0、`after == before`；xsd:string 别名负例另断言 `toHaveValue(alias)`（无静默规范化）。**范围仅限本屏/这些输入**，不推出所有表单与错误族都保留" | 15.2 §2（源码逐行） | 判定不变，**证据由源码推断升为已执行断言**；范围限制写明 |
| 9 | §12 第 **36** 条（原第 491 行） | "密钥不在代码/仓库/AI 对话 \| 适用 \| …**本票未见密钥入库**" | "密钥不在代码/仓库/AI 对话 \| **适用（证据范围收窄）** \| 凭据只在主进程；引擎不持密钥、不调模型；仓库禁 `.env`／`.mimosa`。**本票观察范围＝当前工作树源码的凭据模式检查**；**不覆盖完整 Git 历史与 AI 对话历史**，故不据此宣称二者无密钥 | 15.2 §4（事实文件第三点末句） | **原措辞的证据范围被本票显式收窄**；判定不变 |
| 10 | §12 第 **31** 条（原第 486 行） | "连点四次提交去重 \| 适用 \| UI 侧 `FACT_ALREADY_EXISTS`＋引擎 `reservedIdentity`；Session 的 `sequence` 围栏＋`pending` 禁用。**GUI 未实测**" | "连点四次提交去重 \| 适用 \| …**内容ID/操作声明/冲突围栏只构成相关防护，不等于『四连击只提交一次』的实际 GUI 运行记录**；**本轮未提供特定四连击实跑**（O056 的 24 specs 中无重复提交场景）。**该场景仍未验**" | 15.2 §4 第三点 | 判定不变，**措辞更精确**（避免把机制存在当作已验证行为） |
| 11 | §12 第 **147** 条（原第 602 行） | "bus factor \| 无法确认 \| 代码可证存在多开发者线与双审流程；**人的因素无法从代码确认**" | "bus factor \| **无法确认（本版补证）** \| …**仓内 `.github/` 无 CODEOWNERS、无维护者名册**；多个 AI 开发者线**不能**证明 bus factor 等于 1 或大于 1" | 15.2 §4（`.github/` 清单实测） | 判定不变（**无法确认**），补强依据 |
| 12 | §12 第 **90**／**92** 条（原第 545／547 行） | "…24 例 21PASS/3 原 skip" | 补充：24 例中**第 18 例**为 `five fields, complete Diff, original receipt, Undo/Redo and owned restart`（passed／4920ms／retry0），第 16 例为 `FR201 UI relations and multivalue manual records…`（passed／76897ms／retry0），3 例 skip 均为 `i04-jobs.spec.ts` 原 I04 条件 | 15.2 §1–§2（report.json 24 specs 逐条） | 判定不变，**索引可追溯性补强** |
| 13 | §5 **F04**（本票自有发现） | P2：「TS 与 Python 双实现判据分叉，TS 接受 Python 拒绝的空页/尾页」 | **P3（本票自行降级，依据见 15.5）** | 见 15.5 | **降级但未静默**，理由与证据全列 |
| 14 | §5 **F05**（状态源未记当前候选） | P2：状态源末节仍是 b215/R07，无 62d4b0a/O056 命中 | 维持 P2，并**追加一项待记工件**：本事实文件（7917 B／`e549fa97…`）位于仓外 `iteration-control/`，同样是"当前候选证据"的一部分，状态源追加 `62d4b0a` 快照时应一并指针 | 本票实测仓外事实文件字节/哈希 | 严重级不变，**归口范围扩充** |

**未受影响且维持原判的关键条目**：F01（P1 R07 链脱钩）、F02（P1 零 CI 数据）、F03（P2 Windows 诊断口径）、F06（P2 `sys.path` 未被 identity 覆盖）、F07（P2 证据 head 绑定不 fail-closed）、F08（P2 预览围栏静默丢弃）、F09/F10（P3 供应链冗余、Ruff 排除面）、以及 §6–§9 的全部专项结论与 §11 的第 1–4、6–10 项 HOLD。

### 15.4 历史意见处置影响（78 位置）

**本补充不关闭任何历史位置**，只对两个与 Undo 相关的聚合项做**子集收窄**：

| 位置 | 原状态（R07／本票 R08 §10） | 本版状态 | 依据 |
| --- | --- | --- | --- |
| Z F7（发布前 HOLD 群，逐类具名保留） | HOLD，逐类保留 | **Undo 子项由『GUI 未验』收窄为『已验子集 + 其余未验』**；**签名／公证／wholeApp 法律／`_distutils`／全平台／目标 macOS15／Windows11／参考设备／容量 Q5-D2／旧超限库恢复／损坏 SQLite 物理保护／unknown parser-N3-Store-坏快照／native engine-named App 未知退出码／Windows 后代 UNKNOWN —— 全部原样保留** | 15.2 §1 末段与 §5 末段；本票 §11 其余各项不动 |
| Z F6（历史 OPEN 集合，保留 OPEN 不集合关闭） | 部分采纳／保留 OPEN | **维持 OPEN 集合**；Undo 子项按上表收窄，**其余 definitions 早期 wire／裸 ownership／standalone EOF／缺码集合／无序未确认／4299-4300 应用边界 逐项原样未动** | 15.2 §1 末段；本票 §10.3 逐条代码核验不变 |
| Z F8（ownership 闭环/受控分类，正面核验） | 正面核验，裸族未全闭 | **维持**。本票另在 §15.1 独立确认新读通道的 owner/epoch/project/session 四项绑定闭合，**该确认不外推到裸族** | §15.1.3 |
| MM D10（D/E/G 与失效联动，四具名下游未验） | 仍开 | **维持仍开**。Undo 收窄**不构成**四类具名下游的证据 | 15.2 §1 末段 |
| Z F1／Z P1／Z P2／MM D1 等合并门禁类 | 仍开（门禁） | **维持**。本 head 仍**无 push、无 CI、无 PR 更新、无 merge**；Undo 已验**不能**替代 Windows/Quality 完整回单 | §15.7-B |
| 其余 73 个位置 | 见本票 §10.2／§10.3 | **逐条维持**，无一因本补充改变 | — |

**明确不关闭的清单**：`F6` 历史 OPEN 集合、`Z F6` 的六个子项、`R05 MM03`（本 head 未打包）、`R04 M04`（standalone 残余）、`R05 MM07`（裸族 witness）、`Z P5/D7/MM05/MM07`（缺码可达性）、`Z P6/MM D5/R04 Z01/R05 MM08`（无序未确认观察）、`MM D11/R04 M03`（4299/4300 应用边界断言缺）、`Z F5/MM D8/R05 MM12`（两 TS PATH python）、`MM R07-13`（TS 类型宽于 zod）、`MM R07-03/Z F2/MM R07-02`（Ruff 排除面）。

### 15.5 本补充中我自己发现的变更（F04 降级，不静默）

**原 R08 F04（P2）**：「同一契约的两份『独立实现』判据分叉：TS 接受 Python 拒绝的空页／尾页」，位置 `packages/contracts/src/v2.ts` 的 `matchesOwnershipDetail`（`end > count`）与 `packages/contracts/python/contract_v2.py` 的 `ownership_detail_matches`（`not start < end <= count`）。

**本补充复核后的独立结论：该分歧点在合法输入集合上不可达，F04 由 P2 降为 P3。**

**降级理由（全部为我本人实测，非引述）**：

1. **两侧都先过同一个 schema**。`result_project.ownership.detail` 定义 `segments` 为 `"minItems": 1, "maxItems": 64`。TS 侧 `matchesOwnershipDetail` 的第一行即 `validateBusiness3('result_project.ownership.detail', value)`；Python 侧 `ownership_detail_matches` 同样先 `validate("result_project.ownership.detail", value)`。
2. **两侧校验器都强制 `minItems`**。TS：`packages/contracts/src/v2.ts` 的 `compile()` 对 `type === 'array'` 执行 `.array(compile(s.items!)).min(s.minItems ?? 0).max(s.maxItems ?? 100000)`（第 111–115 行）。Python：`packages/contracts/python/contract_v2.py` 第 97 行 `s.get("minItems", 0) <= len(value) <= s.get("maxItems", math.inf)`。**故零段页在两侧都被拒绝。**
3. **引擎本身也不会产出空页**。`job_store.py:962-963`：首段即超限时 `if not chosen: fault("RESOURCE_LIMIT", resource="page")`，不会出现 `segments: []`。
4. **在 `segments.length >= 1` 的合法集合上，两侧判据等价**：`end = start + len(segments) >= start + 1`，故 Python 的 `start < end` **恒真**，与 TS 的 `end <= count` 是同一组约束。`count` 的算法（Python 整数除法 vs TS `Math.ceil`）在 `totalBytes <= 16 MiB` 内无精度差异。
5. **两侧的 SHA-256 实现已被本票 R08 §3.1 C1 证明一致**（常量逐位等于标准 SHA-256，137 个长度边界零差异）。

**降级后残留的真实差异（仅此一项，P3）**：base64 解码宽容度不同——TS `atob` 按 WHATWG 规范**忽略 ASCII 空白**，Python `base64.b64decode(..., validate=True)` **拒绝**任何非字母表字符（含空白）。方向上 TS 更宽松，且该宽容**不是内容篡改面**：被接受的段仍须通过逐段 SHA-256 与整档 SHA-256 双重比对，而 `reassembleOwnershipDetail` 用的是同一 `atob` 加 `crypto.subtle.digest('SHA-256')` 整档校验。影响：仅当引擎产出的 base64 含空白时，Python 侧契约测试会拒绝而桌面侧会接受——**属严格度一致性 nit，非安全绕过**。

**保留的建议不变**：仍建议两侧抽出同一判据定义并加一组跨语言畸形页对照测试（防止未来 schema 变更使二者再次分叉）——但**已从"合并前须处置"降为"建议"**。

**说明**：本降级**只针对我自己提出的 F04**，不涉及任何他人意见，也不涉及任何由事实文件引入的问题。事实文件未提出 F04，本降级完全来自我本轮对 schema 与校验器的独立核验。

### 15.6 仍无法确认的范围（本补充**未扩大**任何一项）

1. **本 head 的真实 CI 结果**——未 push、无 CI、无 PR 更新、无 merge 授权；**Undo 已验不能替代** Windows/Quality 完整回单。
2. **本 head 的新包制造与包内运行**——未做；旧 094 包 912 成员仅按原样保留，不冒重新整包 hash。
3. **签名、公证、wholeApp 法律、`_distutils` 来源、全平台／目标 macOS 15／Windows 11／参考设备**——HOLD 保留。
4. **Q5／D2 容量口径、旧超限库恢复、损坏 SQLite 物理资源保护**（用户明确保留）——HOLD 保留。
5. **unknown parser／N3／Store／坏快照**——HOLD 保留；本票确认 `rdf_snapshot.py` 的未知分支仍在。
6. **未验 ownership 家族（裸族）／缺码可达性／见证顺序合同**——延期保留。
7. **四类具名下游（推导／保存查询／SHACL／报告）GUI 逐类消费联验**——未验。
8. **其余 Undo 面**（实例事实、批量、跨选择、跨会话、崩溃后、ownership 面、映射/派生撤销）——未验。
9. **native engine／named App 未知退出码；Windows 后代回收 UNKNOWN**——保留。
10. **四连击重复提交的实际 GUI 行为**——本轮未提供实跑。
11. **完整 Git 历史与 AI 对话历史中是否存在密钥**——按范围不读取、不作断言。
12. **依赖更新的实际运行／合并记录、人工修复 SLA、平台侧/组织级外部漏洞扫描是否存在**——仓内无法确认。
13. **真实人类团队人数、创始人身份、组织/产权/实际数据类别与法律角色**——代码无法确认；**且不因代码不适用而取消组织的发布义务**。
14. **本补充未新增任何产品运行**；所有 O056 数字仍是**他人运行结果**，本票做的是独立复算与源码语义核验，**不是重跑**。

### 15.7 三类门禁的分离陈述

**A. push 前源码技术门禁（本票结论：无）**
经本补充对 §5 三处主进程 delta 及其权限/选择/transport 闭包的独立语义核验，以及 §1–§4 的源码与原证据核验，**本票在 base→`62d4b0a` 上仍未发现任何"必须先改源码才能 push"的技术阻断**。本补充唯一的严重级变更是 **F04 由 P2 降为 P3**（§15.5，附完整降级理由与残留差异），**不新增任何 P1/P2**。

**B. 需 push 后新 CI 才能核的剩余合并条件（与本票 R08 §13 一致，无一项被本补充解除）**
1. 本 head `62d4b0a` 的**真实三 job 回单**：Windows 完整 3769 每项最终 PASS 或原有有据 skip、**自然 0**、无失败／早停／取消／timeout／NOTRUN；其后 typecheck／build／E2E／package／verify 及原 3 job 实际 success；Quality 专用步骤与 packaged recovery 步骤**自身 success**。**分片较早 0 或总数统计不能代证完整；新绿不倒填旧 79F 因果。**
2. **F03** 的 Windows 验收口径裁定（诊断步与验收步分离，或书面裁定该 job 全绿即等价全集验收）。
3. **F05** 状态源追加 `62d4b0a`／O056 快照（并指针本事实文件）。
4. **F01** 对"CI 控制层是否纳入指定双审范围"的书面裁定（R07 结论不覆盖本 head 的 594 行新控制层）。
5. **F06／F07／F10** 的处置或书面归口（**F04 已降为建议，不再是合并前条件**）。

**C. 全部原 HOLD（逐条保留，本补充只收窄 Undo 一个子集）**
签名、公证、wholeApp 法律／`_distutils` 来源、全平台／目标 macOS 15／Windows 11／参考设备、Q5／D2 容量口径与旧超限库恢复、**损坏 SQLite 物理资源保护（用户明确保留）**、unknown parser／N3／Store／坏快照、**Undo 的其余未验面**、未验 ownership 家族与缺码可达性、四类具名下游、native engine／named App 未知退出码、Windows 后代 UNKNOWN、清单组织／产权／隐私／法律类无法确认项——**全部保留，无一被本补充消解**。CSP finally 的 SIGKILL 与 engine UNKNOWN 继续按原证据保留。

### 15.8 最终条件与结论（是否改变）

**结论不变：附条件通过（Conditional Pass）。**

- **本地实现层**：通过。本补充新增的 §15.1 三处主进程 delta 独立语义核验**未发现真阻断**，且确认新增 ownership-detail 读通道的权限、选择生命周期、会话绑定与错误收敛四项闭合。
- **本地验收层**：通过（证据为他人运行，本票独立复算未重跑）。本补充把证据边界**收窄到具体**：Undo 的已验子集、迁移的前向/失败中止/降级三段、FR-201 负例的字段级保留断言。
- **push 前源码技术阻断**：**无**。F04 降为 P3 后，本票 P2 及以上仍为 **F01(P1)、F02(P1)、F03、F05、F06、F07、F08**。
- **合并**：**当前仍不可合并**，且原因与本票 R08 完全一致——**本 head 未 push、无 CI、无 PR 更新**，B 类五项条件全部未满足。
- **完成度**：仍为 **2/17（FR-401／FR-402）**；Goal／M0／发布均未完成；本补充**不增加任何完成度**。
- **本补充不构成**：人类资深工程师签字、指定外审、完整候选双 Pass、Windows CI 通过、package／release 通过、父 FR 或附录 C／D／E／G 整体通过。

**一句话**：共享事实文件经本票**逐条独立复核后成立**（§1–§5 全部实测，仅 §2 一处行段归属有轻微不精确）；它**收窄了我自己 R08 中两条过度声明**（Undo 全称未验、依赖升级/SCA 措辞），**促成了我自己 F04 的降级**（P2→P3，附完整证据），**未新增任何阻断**，**未关闭任何 HOLD**，**未改变**本票的附条件通过结论与合并门禁。

---

## 16. R08 本方意见处置 v1（2026-10-26 · 对处置提案的逐项独立裁定）

> **版本标识**：本节为 R08 报告**追加的本人意见处置 v1**，追加于 2026-10-26。
> **§0–§15 全部原字节保持不变**（首稿 88740 B 前缀已逐字校验为 `7abc0337…`）；凡与本节冲突处，以本节为准并逐条标注被更正的原句位置。
> 本节**不新增审查任务**、不重审实现、不运行产品/测试/构建、不访问私有 app 存储或用户库、不改源以迎合提案。
> 本节**不关闭**任何原 HOLD、**不改变**原 15/20 分钟预算、**不改变** 2/17 完成度、**不授予** push/CI/merge 任何授权。
> 本节**未读取**另一方当前报告正文。

### 16.0 提案来源核验与独立判断声明

| 项 | 声明值 | 本人实测 | 判定 |
| --- | --- | --- | --- |
| 提案路径 | `outputs/20261026_t02_62d4_fresh_r08_057/minimax-opinion-disposition-proposal-03.md` | 同 | ✅ |
| 字节 | 13040 B | **13040 B** | ✅ 精确匹配 |
| SHA256 | `c640203f46715b5601326a0543b5077480c57e8c70498493a6eac36397fdbabd` | **同值** | ✅ 精确匹配 |
| 受审身份 | base `583c05c7` → head `62d4b0a2` / tree `7ad1d13d` | 与 §0.1 一致，**未变** | ✅ |

**我据以裁定的实际证据**（全部本人静态读取或纯计算，未引用提案结论）：

1. `packages/contracts/v2/schema.json` —— `changeSetSegment.dataBase64` 的 `pattern` 为 `^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$`（严格 RFC-4648 带填充，**无空白容差**）；`result_project.ownership.detail.segments` 为 `minItems:1 / maxItems:64`；`ownershipDetailManifest.totalBytes` 下限 2、`segmentCount` 下限 1。
2. `packages/contracts/src/v2.ts` —— `compile()` 字符串分支 `new RegExp(s.pattern).exec(v)?.[0] === v`（**要求匹配子串等于整串**）与数组分支 `.min(s.minItems ?? 0).max(s.maxItems ?? 100000)`；`validateBusiness3` 先行调用 `validateV2`。
3. `packages/contracts/python/contract_v2.py` —— 字符串分支 `re.fullmatch(s["pattern"], value) is not None`（第 105 行）与数组分支 `s.get("minItems", 0) <= len(value) <= s.get("maxItems", math.inf)`（第 97 行）。
4. **纯计算**：以该 pattern 对 9 个样本做 `re.fullmatch` —— 规范填充形式（`QUJD`/`QUJ=`/`QQ==`）接受；**尾随换行、前导/尾随空格、内部空格、内部制表符、CRLF 全部拒绝**。
5. `packages/engine/src/ontolearn_engine/storage.py` —— 同 operationId 同 fingerprint/job → `return previous`（672–678 行）；manual 同 ID 且 `owner` 为空且 object 相同 → **`continue`（幂等 no-op，非冲突）**，仅当 `existing["owner"]` 非空或 `existing["object"] != fact["object"]` → `ManualOwnershipConflict(reason="reservedIdentity")`（818–833 行）。
6. `packages/engine/src/ontolearn_engine/job_store.py` —— 同 operation 的 `operation_claims` 已存在 → `return self._accepted_job(...)`（1452–1457 行）。
7. `apps/desktop/src/renderer/src/ontology/mainline-facts.ts` —— 同可见 triple → `FACT_ALREADY_EXISTS`（53–73 行）。
8. `scripts/run-engine-tests.py` —— `subprocess.run(["git","rev-parse",...])` 位于 **`try:` 之前**（379–383 行对 386 行），故 git 程序缺失会抛 `FileNotFoundError` 并使进程非 0 退出；rev-parse 返回非 0 时写 `None` 且**不计入 errors**。
9. `git log -S "PYTEST_ADDOPTS" -- .github/workflows/ci.yml` → **仅 `aff386f6`** 引入该变量；base（CI40 所跑的 `9cb`）的 Windows 步为裸 `- run: npm run engine:check`，**无 PYTEST_ADDOPTS、无 maxfail**。
10. O056 原件 —— `COMPLETION.json.candidate` 实含 `head=62d4b0a2…`、`tree=7ad1d13d…`、`parent=422bdfdb…`、`ciWindowParent=9cbddf34…`、`pathsAgainstWindowParent=[ci.yml, package.json, 两个脚本]`、`branch`、`sourceCount=1380`、`at`；`FINAL-MANIFEST.json.candidateHEAD/candidateTree` 同值；`mode2 summary.checkout` = `{head:62d4b0a2…, tree:7ad1d13d…}`。
11. `package.json` —— `electron 44.9.0`／`electron-vite 6.0.0`／`vite 8.3.4` 在**根** devDependencies；`apps/desktop/package.json` —— `react 19.3.1`。`.github/dependabot.yml` 的 npm 条目为 `directory: /`（**仅根**）。
12. `docs/reviews/T02/fr200-fr201-20261024/round-07/disposition.md` 第 73–86 行 —— R04 Z01–Z07／M01–M07 的**原处置与归口·事件窗口原文**（本节 §16.4 逐条原样承接）。

### 16.1 A1–A9 逐项裁定

| A | 提案主张 | 我的独立核验 | **裁定** | 当前阻断性 | owner · 事件窗口 |
| --- | --- | --- | --- | --- | --- |
| **A1** | 诊断标签与实际完整验收须分开；完整回单成立后可有界接收完整性证据，不先改冻结标签；maxfail 致 292 未结算的归因未证 | 脚本 `account()` 为**全量逐 node 结算**：失败/早停/缺证/集合差异/重复/未结算/输出错误均使父进程非 0；`parallel()` 另核 `reportCoverage` 与 universe 相等。故"step 绿"已蕴含全集通过，标签是**描述性文字而非执行语义**。同时 §16.3-2 证实提案对 292 归因的纠偏正确 | **同意（附限定）**：标签不构成必须改源的门禁；可在本 head 真实回单成立后**有界接收**其完整性证据，条件为回单来自本 head、逐 node 全体与原有据 skip、setup/call/teardown 全集、session/身份、原生退出、后继 typecheck/build/E2E/package/verify、Quality 专用与 packaged recovery 步骤自身 success、三 job 实际 success，**且不得以 step 绿或总数替代**。**保留**：标签与门禁口径的文档不一致仍应择票写清（不要求本轮改源） | 否（合并门禁项，非源码） | ROOT 在未来真实三 job 回单后逐项核验、merge 前闭合；标签文字归后续归档/维护票 |
| **A2** | schema 前置是否排除 F04 反例；并核 §15.5 的 base64 空白残留可达性 | 已核：两侧均先过**同一** schema；`segments.minItems=1` 两侧均强制（TS `.min()`、Python 第 97 行）；`totalBytes≥2`、`segmentCount≥1` 有正下限；引擎 `job_store.py:962-963` 亦不出空页。故 `len(segments)≥1 → end>start`，两侧判据在合法输入集上**等价**。另：base64 pattern 严格无空白容差，9 样本实测全部拒绝含空白变体，**进入 atob/b64decode 前已被拒绝** | **同意**：**撤回 F04**（原 §4 的 P2 与 §15.5 的 P3 残留**一并撤回**），保留原字节并在本节更正（§16.3-8） | 否 | 原 MM 作者本票内闭合；不新增源改动/测试 |
| **A3** | 文档滞后与原证据自绑定须分开；O056 实际含 head/tree 绑定，"二者均未自钉当前 head"须纠正 | 已核：O056 `COMPLETION.json.candidate`、`FINAL-MANIFEST.json.candidateHEAD/candidateTree`、`mode2 summary.checkout` **三者均绑定** `62d4b0a2`／`7ad1d13d` | **同意**：接受事实纠偏；我 §4-F05 与本节 §16.3-1 相应更正。**F05 的实质条件（唯一状态源未追加当前候选）不变** | 否（合并前文档条件，非源码） | ROOT 唯一文档维护者；R08 收口后、merge 前，按票决定是否须先于 push |
| **A4** | F07 失败模型范围：git 程序缺失会抛 FileNotFoundError 非 0；rev-parse 非 0 才写 None 且不计 errors；O056 现有 summary.checkout 实际已绑定 | 已核（§16.0 第 8、10 项）：`subprocess.run` 在 `try:` 之前；rev-parse 非 0 → `checkout[name]=None` 且 `errors` 不增 → `passed` 可为 true。**git 缺失路径不会走到 passed=true** | **同意（范围收窄）**：F07 的真实缺口仅为"**git 存在但 rev-parse 失败仍可产出无绑定且 passed=true 的 summary**"；不得表述为"git 缺失"。**当前验收必须拒绝无 head/tree 绑定的回单**（与 §15.2 一致） | 否 | 原 T02 开发归口；ROOT 后续首个证据控制层维护票；**在接收任何无 head/tree 产出前**生效 |
| **A5** | F11／清单 30：事实 ID 与 operation 幂等须分开；"同事实跨会话重放一律所有权冲突/需新产品裁定"的全称应撤回或收窄 | 已核（§16.0 第 5–7 项）：**三路结果**——① 同 operationId + 同 fingerprint/job → `return previous`（幂等），`operation_claims` 亦幂等；② 同 triple 且该 ID 未被异值占用 → 引擎侧 **`continue` 幂等 no-op**，同屏可见时先由 `FACT_ALREADY_EXISTS` 拦下；③ **原 ID 已被先前编辑改成异值**后再新增同 Triple → `ManualOwnershipConflict(reason="reservedIdentity")` | **同意（收窄）**：我 F11 的全称**错误**，须更正（§16.3-4）。**剩余真实面仅第③种**；且该情形是安全拒绝＋可定位 witness，**不自动升级为需人类产品裁定的新需求**。仅"第③种情形 UX 应表述为已存在还是所有权冲突"可作产品层观察，保留为**原 T02 范围内**，不新增审批 | 否 | 原 MM 作者本票内闭合；如需产品层用词澄清，归原 T02 授权内，**不默认要求新人类裁定** |
| **A6** | §13 "不构成指定外审"与本任务指定模型身份相矛盾，须澄清层次 | 属实：原任务即以 **MiniMax Code／M3.1-Flash／xhigh** 指派我作独立对抗性工程审查；我 §13 与 §15.8 两处写"不构成：…指定外审…"，**自相矛盾**。本票**就是**本方指定模型对该整候选的独立指定外审意见 | **同意（我方措辞缺陷）**：更正为"本票是本方指定模型的独立工程外审意见；**不构成**的是人类资深工程师签字、双方完整接收、完整产品/合并/发布验收、Windows CI 通过等"。**该更正不改变 ConditionalPass，也不解除任何条件**（§16.3-6） | 否 | 本票内更正；人类签字属既有 HOLD，非本票新增前置 |
| **A7** | dependabot 的 npm 依赖面包含 Electron/React/Vite，故"应用框架栈未被自动更新覆盖"的全称应收窄 | **部分不成立**：dependabot 的 npm 条目为 `directory: /`，**仅覆盖根 `package.json`**。实测：`electron 44.9.0`／`electron-vite 6.0.0`／`vite 8.3.4` 在**根**（被覆盖）；`react 19.3.1` 在 **`apps/desktop/package.json`**（**根条目不覆盖**） | **限定同意**：按实际 ecosystem/目录配置写为"**根级 npm 依赖（含 electron/electron-vite/vite）被每周更新 PR 覆盖；`apps/desktop` 子目录依赖（如 react）未被覆盖**"。uv/vendor 生态未配置、EOL 跟踪、实际运行/合并记录与人工 SLA 仍未知。**配置存在 ≠ 更新已执行**，不增加实际运行 | 否 | ROOT 报告归档归口 + 原 T02 依赖维护归口；**不新增配置改动** |
| **A8** | F18／§8 打包行：build-engine.mjs 与 uv.lock 只能证明构建配置预期消费 fr201.3，不能当当前 head 新包实物或包内运行已证 | 属实：§8"打包一致性"行与 §4-F18 表中的"故包内一致"**属过度陈述**；本 head 无新包制造、无包内实测，旧 094 仅有界桥接 | **同意**：显式澄清并更正（§16.3-3）。**不因此要求本轮重打包** | 否 | 原 T11 供应链 + 原 T02 依赖归口；未来真实 CI package/verify 逐项核验 |
| **A9** | 清单 48/53/57/58 等"本地无外部攻击面/无患者或个人数据/本地所以不适用"不能由代码确认；148–150/157 可作未知审查事项，不自动新增人类签字或产品裁决前置 | 属实：我 §12 第 48／53／57／154 行把**架构推断写成事实**（"无外部攻击面""无患者数据""无个人数据处理"）；§12 第 148–150／157 行的"仍需人类"写法须精确化为"未知/原范围"，以免读作新增前置 | **同意**：更正措辞（§16.3-7）；**本地架构只能限制已读技术面，不能推导外部攻击面不存在、真实患者/个人数据不存在或独立法律义务免除**；wholeApp 法律/隐私等原 HOLD 全部保留 | 否（组织义务，非源码） | 原发布/法律归口；**不新增当前流程的人类签字或产品裁决前置** |

### 16.2 F01–F19 逐项最终处置

| ID | **本人裁定** | 依据（本人实测） | 当前阻断性 | owner · 事件窗口 |
| --- | --- | --- | --- | --- |
| **F01** | **同意** | R07 三处指针钉 `b215f543`，HEAD 多 3 提交且含 594 行新控制层（§0/§4-F01/§15.4） | 否（流程） | T02 审查作者完成本票；ROOT 在任何 push 前接收 |
| **F02** | **同意** | 本 head 未 push、无 CI；本地 114.075 s 为开发机数字，脚本自陈非提速承诺（§6.3/§9） | 否（合并门禁） | ROOT 发精确普通 push/PR16 票后、原 15/20 分钟内运行并逐 node 核验；merge 前 |
| **F03** | **同意 + 限定**（见 A1） | 脚本全量结算语义；标签为描述性文字；**并接受 292 归因纠偏** | 否（合并门禁） | 见 A1 |
| **F04** | **撤回**（见 A2） | schema 前置排除反例；base64 残留一并不可达 | 否 | 本票内闭合 |
| **F05** | **同意 + 我方事实更正**（见 A3） | O056 三处均绑定当前 head；状态源仍停在 b215/R07 | 否（合并前文档条件） | ROOT 唯一文档维护者，R08 收口后、merge 前 |
| **F06** | **同意** | `python -m pytest` 改 `sys.path[0]`，而 identity 七项无 `sys.path`（§6.2/§4-F06）；当前无遮蔽反例 | 否 | 原 T02 开发归口；ROOT 后续首个 CI 控制层维护票；**任何声称完整导入路径等价之前** |
| **F07** | **同意 + 范围收窄**（见 A4） | `subprocess.run` 在 try 之前；rev-parse 非 0 → None 且不计 errors | 否 | 原 T02 开发归口；ROOT 后续首个证据控制层维护票；**接收任何无 head/tree 产出前** |
| **F08** | **同意** | 源码确有静默丢弃路径；用户可复现性未实跑（§4-F08/§7.3） | 否 | 原 T02 前端归口；后续已获票 UX/异步预览维护窗口；**原 fence 不变量保留** |
| **F09** | **同意** | vendor 三 wheel 中仅 fr201.3 被引用，fr201.1/2 共 4.76 MB 无引用（§8） | 否 | 原 T11 供应链/发布归口；实际 merge 后后续包/发布审计窗口；**不私自删 wheel** |
| **F10** | **同意** | Ruff 排除面仅按名枚举 3 文件/轮次目录，`.prettierignore` 整目录忽略 `docs/reviews`；R06 attempt2 已实证其致失败（§4-F10） | 否 | ROOT 报告归档归口 + 原 T02 维护归口；下一次有票归档含 Python 围栏原件前核对应路径；**不改 raw、不宽泛排除绕过检查** |
| **F11** | **同意 + 收窄**（见 A5） | 三路结果已核（§16.0 第 5–7 项） | 否 | 原 MM 作者本票内闭合；**不默认要求新人类裁定** |
| **F12** | **同意** | `if: always()` 不保证 cancel 后上传；脚本无内部看门狗（§4-F12） | 否 | ROOT 未来 CI 结算逐步核产物；原 T02 控制层维护票再评估看门狗；**不延时/重试/隐藏取消** |
| **F13** | **同意** | `HISTORICAL_SCORES` 自陈非提速承诺（§4-F13） | 否 | ROOT 后续 PR16 说明/CI 结算窗口；**不量化未实测 runner 提速** |
| **F14** | **同意** | `reassembleOwnershipDetail` 硬编码 pageSize 64，但真实响应已由 `matchesBusiness3Response` 用真参数校验（§4-F14） | 否 | 原 T02 契约归口；后续首个 ownership-detail 契约维护票 |
| **F15** | **同意** | `LIMIT 2` 无 ORDER BY 的见证顺序仍未合同化（§4-F15/§5） | 否 | 原 T02 storage/契约归口；后续原见证顺序合同维护窗口；**不新增顺序需求** |
| **F16** | **同意** | 文档总量与预算夹持下无需改动（§4-F16） | 否 | 原 T02 契约归口持续保留原 capacity；**不提高上限、不解除容量 HOLD** |
| **F17** | **同意** | `pattern` 转义连字符语义等价（§4-F17） | 否 | 原 T02 前端归口；无新增动作 |
| **F18** | **同意 + 我方过度陈述更正**（见 A8） | 依赖 vendored 特性属实；"包内一致"属过度陈述（§16.3-3） | 否 | 原 T11 供应链 + 原 T02 依赖归口；下次依赖/打包维护票与发布前供应链核验 |
| **F19** | **同意** | R07 链内 ID 命名歧义、标题与正文口径冲突（§4-F19/§10.4） | 否 | ROOT 唯一归档归口；R08 最终版本图/处置归档窗口；**保留旧 raw 与旧标题，不改写旧 79F 或 Ruff 差因** |

### 16.3 我对自己原句的更正（8 条，逐条可验）

> 均为**本方首稿/§15 补充中我自己写下的错误**，更正依据全部为本人本轮实测。**原文不删改**，仅在此更正并指向被更正位置。

| # | 被更正位置 | 我原来的表述 | 更正后 | 依据 |
| --- | --- | --- | --- | --- |
| 1 | §4 **F05**「影响」末句（第 177 行） | "O056 的 `COMPLETION.json`／`FINAL-MANIFEST.json` 均**未自钉当前 head**（外部目录，无 commit 绑定），head 绑定只能靠本仓 Git 历史与 status 叙述。" | "O056 三处**均自钉当前 head**：`COMPLETION.json.candidate`（head/tree/parent/ciWindowParent/pathsAgainstWindowParent/branch/sourceCount/at）、`FINAL-MANIFEST.json.candidateHEAD/candidateTree`、`mode2 summary.checkout` 皆为 `62d4b0a2`／`7ad1d13d`。**F05 的实质条件不变**：唯一状态源仍未追加当前候选。" | §16.0 第 10 项实测 |
| 2 | §4 **F03**「影响」②（第 159 行） | "一旦出现失败即早停，剩余用例不结算——**这正是历史 Windows『292 未结算』证据缺口的成因**。" | "一旦出现失败即早停，剩余用例不结算——故**该次产出不能作为『全量已跑』的证据**。**我原归因错误**：CI40 所跑的 `9cb` 其 Windows 步为裸 `npm run engine:check`，**当时并无 PYTEST_ADDOPTS／maxfail**（该变量由 `aff386f6` 才引入），**292 未结算的真实原因仍未知**，不得归因于 maxfail。" | `git log -S "PYTEST_ADDOPTS" -- .github/workflows/ci.yml` → 仅 `aff386f6`；base ci.yml 第 129 行无该变量 |
| 3 | §8「打包一致性」行（第 320 行）与 §4 **F18** 表（第 240 行）中"故包内一致" | "✅ 包内 rdflib 即 fr201.3"；"…（同一 venv／同一 vendored wheel），故包内一致" | "**构建配置预期**消费 fr201.3（`uv.lock` 的 vendored path ＋ `build-engine.mjs` 的 `uv run --frozen pyinstaller` ＋ `--collect-all rdflib`）。**本 head 无新包制造、无包内实测**；旧 094 仅原有界桥接。**包内实物与包内运行仍待未来真实 CI 的 package/verify 逐项。**" | 本 head 无新包（§11-1）；无包内运行证据 |
| 4 | §4 **F11** 表（第 233 行） | "**副作用**：跨会话重放同一事实不再『幂等成功』，而是报所有权冲突。是否为期望产品语义属人类产品决定。" | "**三路结果**：① 同 operationId＋同 fingerprint/job → 幂等返回 previous（`storage.py:672-678`），`operation_claims` 亦幂等（`job_store.py:1452-1457`）；② 同 triple 且该 ID 未被异值占用 → **引擎侧 `continue` 幂等 no-op**（`storage.py:829-830`），同屏可见时先由 `FACT_ALREADY_EXISTS` 拦下；③ **原 ID 已被先前编辑改成异值**后再新增同 Triple → `ManualOwnershipConflict(reason='reservedIdentity')`。**我原『一律报所有权冲突并需人类产品裁定』的全称错误，撤回。**剩余真实面仅第③种，且属安全拒绝＋可定位 witness，**不自动升级为新需求**。" | §16.0 第 5–7 项实测 |
| 5 | §15.3 表第 6 行（清单 136）（第 770 行） | "**应用框架栈未被自动更新覆盖**" | "**根级 npm 依赖（含 electron 44.9.0／electron-vite 6.0.0／vite 8.3.4）被 dependabot 每周更新 PR 覆盖；`apps/desktop` 子目录依赖（如 react 19.3.1）未被 `directory: /` 条目覆盖**"；uv/vendor 生态未配置、EOL 跟踪、实际运行/合并记录与人工 SLA 仍未知 | §16.0 第 11 项实测 |
| 6 | §13 末句（第 628 行）与 §15.8（第 858 行） | "本票不构成：人类资深工程师签字、**指定外审**、完整候选双 Pass、Windows CI 通过、package/release 通过、父 FR／附录 C／D／E／G 整体通过。" | "**本票即本方指定模型（MiniMax Code／M3.1-Flash／xhigh）对 base→`62d4b0a` 整候选的独立指定外审意见，可作为本方指定模型的工程外审意见接收**；它**不构成**的是：人类资深工程师签字、双方完整接收、完整产品/合并/发布验收、Windows CI 通过、package/release 通过、父 FR／附录 C／D／E／G 整体通过。**该澄清不改变 ConditionalPass，也不解除任何条件。**" | 原任务即以本模型指派本票；§0 与 §1 的身份表述与此处原措辞相矛盾 |
| 7 | §12 第 **48**／**53**／**57**／**154** 行（第 503／508／512／609 行） | "本地桌面应用**无外部攻击面**"；"**无患者数据**"；"**无个人数据处理**" | "**本票只能确认当前已读技术面**；外部攻击面是否存在、实际处理的数据类别、组织的法律前提**无法由代码确认**。本地架构可限制已读技术面，**不能推导**外部攻击面不存在、患者/个人数据不存在或独立法律义务免除。相关组织义务与原 HOLD 保留。" | §16.1-A9 |
| 8 | §4 **F04**（P2）与 §15.5 的"base64 空白宽容度残留 P3" | "TS 接受 Python 拒绝的空页／尾页"；残留"TS `atob` 忽略 ASCII 空白、Python `validate=True` 拒绝" | "**F04 撤回**：`result_project.ownership.detail.segments.minItems=1` 经两侧校验器**均强制**（TS `compile()` 的 `.min()`；Python 第 97 行），引擎亦不出空页，故该分歧点**在合法输入集合上不可达**。**base64 空白残留一并撤回**：`changeSetSegment.dataBase64` 的严格 pattern（无空白容差）在两侧均于**进入解码器之前**拒绝含空白变体（9 样本实测全部拒绝），解码器宽容度差异**不可达**。" | §16.0 第 1–4 项实测 |

### 16.4 原交付输出缺项：R04 十四条补齐为独立行（完整 78 位置）

**原 §10.3 曾把 R04 全部 14 条合为 1 行**（叙述了多个 ID，但不等于每个位置独立成行）。按原提示的 **23＋55＝78**，现将 R04 Z01–Z07 与 M01–M07 **各补一行**，**原归口与事件窗口逐条沿 R07 `disposition.md` 第 73–86 行原样承接**，不静默取消任何维护窗口。

| 位置 | 标题 | 原处置 · 归口 · 事件窗口（原样承接） | 本版（62d4b0a）状态与依据 |
| --- | --- | --- | --- |
| **R04 Z01** | 无序查询观察未确认 | 无序查询观察未确认；T01下次触及witness选取，同D5 | **仍开（未确认观察）**。SQL 事实仍在（`storage.py` 的 `GROUP BY subject … LIMIT 1` 与 `LIMIT 2` 均无 ORDER BY）；**不升级为已证跨运行缺陷**。归口与窗口同原 |
| **R04 Z02** | 43692 分页信封误因果 | 43692分页信封的误因果撤回；262144整文档/16MiB预算另保原边界，已有round05独立行，不复活已撤回缺陷；T01详情预算下次授权维护 | **撤回维持（不复活）**。262144 整文档／16 MiB 预算边界仍在（`maxFrameBytes` 与段长/文档上限）。归口与窗口同原 |
| **R04 Z03** | definitions 早期 wire | definitions早期wire OPEN，T01原始triples／Agent接线前；同D3 | **仍开（OPEN）**。代码事实仍在：预览校验内 `_definition` 的未分类 `ValueError` 未被分类。归口与窗口同原 |
| **R04 Z04** | typed witness／裸旧 detail 分开 | typed witness/裸旧detail分开，T01/T02对应家族接线前；同D4 | **部分闭合**：typed witness 已落地并可读（本票 §15.1、§15.2-1）；**裸族仍未全闭**。归口与窗口同原 |
| **R04 Z05** | 集合差与可达性分开 | 集合差与可达性分开，T01/T02对应方法接线前；同D7 | **仍开**。缺码可达性未证；不一次性泛加白名单。归口与窗口同原 |
| **R04 Z06** | 既有 canonical 政策 | 既有canonical继续；未来真改政策才新人类决定 | **已闭合（沿既有决定）**：精确 `term(value).n3()` 在 HEAD 生效，**无新人类表态前置**。归口与窗口同原（未来真改政策才新决定） |
| **R04 Z07** | 规模信息 | 2993/1887/1748规模信息，不新增重构 | **已闭合（信息）**；不以 LOC 推正确性。归口与窗口同原 |
| **R04 M01** | 归档演进 | 从原归档待ROOT到最终状态追加完成是历史演进，不互相矛盾；新8318当前节另追加 | **已闭合（历史演进）**。**当前 head `62d4b0a` 的状态源追加另见 F05**，不并入本条、不视为已完成 |
| **R04 M02** | 不采无 hash 前提；保留审计件 | 不采无hash前提；uv/PROVENANCE哈希保留，不删.1/.2/upstream审计件 | **已闭合（维持）**。本票 §8 另实证哈希三方一致与补丁可重建；fr201.1/2 **保留不删**（见 F09）。归口与窗口同原 |
| **R04 M03** | 4299/4300 未来维护 | 4299/4300未来维护，4301已证保留；同D11 | **仍开（未来维护）**：HEAD 仅对 4301 有断言，4299/4300 应用边界断言仍缺。归口与窗口同原 |
| **R04 M04** | standalone 残余 | standalone残余OPEN，未证当前UI可达；同D6 | **仍开（OPEN）**。vendored `notation3.py` 的 `n[-1]` 索引仍在；**未证当前 UI 可达**。归口与窗口同原 |
| **R04 M05** | 早期 definitions 不受后置 catch 覆盖 | 早期definitions不受后置catch覆盖，T01原始wire接线前；同D3 | **仍开（OPEN）**。代码事实仍在。归口与窗口同原 |
| **R04 M06** | schema 形状与内容身份分层 | schema形状与Store内容身份分层，真实双端ID校验/原IDedit已有证据，非当前绕过漏洞 | **已闭合（维持分层，非绕过漏洞）**。本票 §15.1 另核 ownership-detail 的双端校验链；**不外推为全产品安全认证**。归口与窗口同原 |
| **R04 M07** | 桶导出兼容 | 桶导出兼容信息，未证冲突，不直接缩导出面；契约owner下次API整理时评估 | **仍开（维护窗口保留）**：未证冲突，**不直接缩导出面**。**关闭"当前已证冲突"的推断不取消本维护窗口**——契约 owner 下次 API 整理时评估。归口与窗口同原 |

**78 位置完整性确认**：R07 本轮 **23**（Z F1–F10＝10、MM R07-01–12＝12、原未编号→R07-13＝1）＋ R06 Z **8** ＋ R06 MM **12** ＋ R04 **14**（本次补齐独立行）＋ R05 **21** ＝ **78**，与原提示 "23＋55＝78" 一致，**无一位置被取消、合并或静默关闭**；各组归口与事件窗口均沿 R07 `disposition.md` 原样承接。

### 16.5 受影响 160 清单条目的澄清（**只追加，不覆盖原 160 行**）

| 清单 # | 原行保留 | 本节澄清 |
| --- | --- | --- |
| 15 | 保留 | 见 §16.3-4 相关：**前向迁移已验／失败回滚＝失败原子中止已验／降级显式拒绝**（原行"回滚路径未验"已由 §15.3-4 精确化，本节不再重复） |
| 30 | 保留 | **不与 F11 混同**：operation 幂等由 `storage.py:672-678` 与 `job_store.py:1452-1457` 承担（**已验**）；事实 ID 内容派生后的三路结果见 §16.3-4 |
| 31 | 保留 | 维持"该场景仍未验"；机制存在 ≠ 已验证行为；**本轮无四连击实跑** |
| 36 | 保留 | 证据范围收窄见 §16.3-7（仅当前工作树源码检查，不覆盖完整 Git 历史与 AI 对话历史） |
| 39 | 保留 | 措辞收窄见 §15.3-7 与 §16.1-A7（仓内 ci.yml 无 audit 步；**平台侧/组织级外部扫描无法确认**；pin/frozen ≠ 扫描） |
| 48／53／57／154 | 保留 | 更正见 §16.3-7：**本票只能确认已读技术面**；实际数据类别与组织法律前提无法由代码确认；组织义务与原 HOLD 保留 |
| 128 | 保留 | 维持 §15.3-3 的收窄（Undo 已验子集 + 其余未验，HOLD 按子集保留） |
| 135 | 保留 | 维持 §15.3-5 的更正（dependabot weekly 已配置；uv/vendor 未覆盖；执行记录与 SLA 未核） |
| 136 | 保留 | 更正见 §16.3-5（根级 npm 覆盖 electron/electron-vite/vite；`apps/desktop` 的 react 未被覆盖） |
| 145／146／147 | 保留 | 维持"无法确认"；§16.1-A9 补强依据：仓内无 CODEOWNERS、无维护者名册；**不新增人类签字或产品裁决前置** |
| 148／149／150／157 | 保留 | 精确化为"**未知／原范围**"：本票为 AI 审查者执行，**不构成人类资深签字**；这些角色项属用户清单的未知事项，**不自动新增当前流程前置**（§16.1-A6／A9） |

### 16.6 三类门禁的分离陈述（全部维持不变）

**A. push 前源码技术门禁：无。**
经本轮对 §5 三处主进程 delta 的独立语义核验（§15.1）与对处置提案 A1–A9 的逐项复核，**base→`62d4b0a` 上仍无必须先改源码才能 push 的技术阻断**。本轮唯一的严重级变化是 **F04 撤回**（原 P2 → §15.5 的 P3 残留 → **全部撤回**）与 **F11 收窄**，**未新增任何 P1/P2**。本方 P1 及以上仍为 **F01（审查覆盖/流程）** 与 **F02（零 CI 数据）**。

**B. 需 push 后新 CI 才能核的剩余合并条件（五项，无一解除、无一新增）**
1. 本 head `62d4b0a` 的**真实三 job 回单**：Windows 完整 3769 逐项最终 PASS 或原有有据 skip、**自然 0**、无失败／早停／取消／timeout／NOTRUN；其后 typecheck／build／E2E／package／verify 及原 3 job 实际 success；Quality 专用步骤与 packaged recovery 步骤**自身 success**。**分片较早 0 或总数统计不能代证完整；新绿不倒填旧 79F 或 292 的原因。**
2. **F03** 的诊断标签与验收口径裁定（A1 限定条件已给出；**不要求本轮改源**）。
3. **F05** 唯一状态源追加 `62d4b0a`／O056 快照（含本仓外事实文件与处置提案的指针）。
4. **F01** 对"CI 控制层是否纳入指定双审范围"的书面裁定。
5. **F06／F07／F10** 的处置或书面归口（**F04 已撤回，不再是条件；F11 已收窄**）。

**C. 全部原 HOLD（逐条保留，本轮无一项被消解）**
签名、公证、wholeApp 法律／`_distutils` 来源、全平台／目标 macOS 15／Windows 11／参考设备、Q5／D2 容量口径与旧超限库恢复、**损坏 SQLite 物理资源保护（用户明确保留）**、unknown parser／N3／Store／坏快照、**Undo 的其余未验面**、未验 ownership 家族（裸族）与缺码可达性、四类具名下游（推导／保存查询／SHACL／报告）GUI 逐类联验、native engine／named App 未知退出码、Windows 后代回收 UNKNOWN、清单组织／产权／隐私／法律类无法确认项、R04 各条仍开的维护窗口 —— **全部保留**。CSP finally 的 SIGKILL 与 engine UNKNOWN 继续按原证据保留。

### 16.7 最终条件与结论（是否改变）

**结论不变：附条件通过（Conditional Pass）。**

- **本地实现层**：通过。本轮新增核验（§16.1 A1–A9）未发现真阻断；§5 三处主进程 delta 的权限／选择／transport 闭包确认闭合。
- **本地验收层**：通过（**证据为他人运行，本票独立复算未重跑**）。本轮把证据边界进一步收窄到具体：Undo 已验子集、迁移三段、FR-201 负例字段级断言、O056 的 head/tree 自绑定。
- **push 前源码技术阻断**：**无**。F04 撤回、F11 收窄；本方 P1/P2 集合不变（F01、F02、F03、F05、F06、F07、F08）。
- **合并**：**当前仍不可合并**——本 head 未 push、无 CI、无 PR 更新；B 类五项条件全部未满足。
- **完成度**：仍为 **2/17（FR-401／FR-402）**；Goal／M0／发布均未完成；本轮**不增加任何完成度**。
- **本票身份（依 A6 更正）**：本票是**本方指定模型（MiniMax Code／M3.1-Flash／xhigh）对 base→`62d4b0a` 整候选的独立指定外审意见**；**不构成**人类资深工程师签字、双方完整接收、完整产品/合并/发布验收、Windows CI 通过、package/release 通过、父 FR 或附录 C／D／E／G 整体通过。
- **本轮明确不做**：不重审实现、不运行产品/测试/构建、不访问私有 app 存储或用户库、不改源以迎合提案、不新增人类签字或产品裁决前置、不新增 push/CI/merge 授权。若某条判断确需新增产品验证，本票已在 §16.1 各行**具体列出证据缺口**并交 ROOT／原开发会话按既有职责受控执行，**本票不自行执行**。

**一句话**：处置提案经本人逐条独立核验后**整体成立**（A1–A9、F01–F19 中 **17 条同意**、**2 条限定**〔A1 的标签裁定、A7 的 npm 覆盖目录〕、**2 条我方自行更正**〔F04 撤回、F11 收窄〕、**另 4 条我方原句更正**）；它促成了**我自己的 F04 撤回**与**F11 收窄**，并使我的原句更正为 8 条；**未新增任何阻断、未关闭任何 HOLD、未改变**附条件通过结论与合并门禁。

---

## 17. R08 短勘误 v1（2026-10-26 · 两处直接源码/历史定位错误 + 一处未核实推断）

> **版本标识**：追加的短勘误节。**§0–§16 的 159046 B 原字节全部保持**（本节写入前已逐字校验为 `f55811b8cc7a71ca9239d36df36c061276fcd4ef76269e55071e63b0b08d1cb6`）。
> **不重开实现审查**、不重复全部处置、不改实现/配置/依赖/测试/验收、不运行产品/测试/构建、不访问私有 app 存储或用户库。
> 本轮**未读取**另一方当前正文/意见/结论。
> 原 160 条清单、78 个历史位置、R04 十四条独立行、原 Top10 与处置表**均不删改**；本节只作勘误与更正指引。

### 17.1 勘误一（历史定位）：base 583 ≠ CI40 实际 head 9cb

**被更正位置**：§16.0 第 9 项（第 891 行）、§16.3 表第 2 行（第 941 行）；连带更正 §4 F03「影响」②（第 159 行）的**撤回依据**。

**直接依据（本人本轮实读）**：
- `git show 9cbddf34e94fac1a66448afe5f8d51aa01d07887:.github/workflows/ci.yml` 第 129–139 行：Windows 步**已**是 `# Diagnostic only: first-failure evidence; not acceptance or merge approval.` / `name: Windows engine first-failure diagnostic (not acceptance)`，`env: PYTEST_ADDOPTS: '-vv --maxfail=1 --tb=short'`。
- `git show 583c05c7870ba0f8f642e3eeea1d0590e5859ca2:.github/workflows/ci.yml` 第 129 行才是裸步 `- run: npm run engine:check`。
- `git merge-base --is-ancestor aff386f6 9cbddf34` → **真**（`aff386f6` 是 `9cb` 的祖先）。

**我错在哪**：§16.0 第 9 项与 §16.3-2 把 **base 583 的裸步**误当成 **CI40 所跑的 9cb 的步**。**这是勘误的勘误——我上一轮"纠偏"所依据的事实本身是错的。**

**更正后的准确表述（三点分开，不得再混）**：
1. **CI40（run 40252093380，实际 head `9cb`）的 Windows 作业确实带 `--maxfail=1`**（9cb 的 `PYTEST_ADDOPTS: '-vv --maxfail=1 --tb=short'`）；裸步只存在于 base `583c05c7`。
2. **但 maxfail 的存在本身不构成 292 未结算的因果证明**；CI40 的实际记录是 **20 分钟取消／KeyboardInterrupt**，**292 未结算的真实原因仍未知**，**不回填旧原因**。
3. 因此：**§4 F03「影响」②中"这正是历史 Windows『292 未结算』证据缺口的成因"这一因果归因仍予撤回**——撤回**结论不变**，撤回**依据**更正为"因果未证"而非"当时无 maxfail"；其中性可用结论"**该次产出不能作为『全量已跑』的证据**"保留。

**附带成立**：本候选相对 `9cb` 的 Windows 诊断步实际增量只有 `--durations=20 --full-trace`（9cb 为 `-vv --maxfail=1 --tb=short`），故 §4 F03「影响」③关于"新增 durations/full-trace 仅改变诊断输出形态"的描述**仍然成立**。

### 17.2 勘误二（源码描述）：三方法共用同一 current-projectId 分支

**被更正位置**：§15.1.2（第 698 行）。

**直接依据**：`apps/desktop/src/main/engine.ts` 第 1241–1247 行实读——

```text
if (
  (method === 'project.read' ||
    method === 'project.draft.save' ||
    method === 'project.ownership.detail') &&
  params.projectId !== record.selected?.projectId
)
  throw deniedOrdinary()
```

且 schema 实测：`params_project.read`、`params_project.draft.save`、`params_project.ownership.detail` **三者 `required` 均含 `projectId`**，`additionalProperties:false`。

**我错在哪**：§15.1.2 写"参数面比 `project.read` 更严：`project.read` 无此比对"——**该比对是三方法共用的单一分支**，且 `project.read` 的 params 同样必填 `projectId`。故 ownership.detail 在这一项上**并不强于** read。

**更正后的准确表述**：
- **transport 层**：`project.read`／`project.draft.save`／`project.ownership.detail` **共用同一 current-projectId 比较**（三者 params 均必填 projectId，比较值确定）。ownership.detail 的额外约束只在其**自身 schema 的字段集与页参数**（`detailRef`／`documentHash`／`startOrdinal`／`pageSize`），**不在该 projectId 比对上**。
- **服务层（§15.1.3 内容不变、仍然成立）**：ownership.detail 另有 **调用前 `client.owner !== current.owner`** 与 **返回后 `#selectionEpoch` 比对**两道守卫；**这两道才是相对 `readProject` 的实际增量**（`readProject` 无 owner 比对、无 epoch 比对）。
- **结论不变**：该读通道确受白名单、schema、预算、当前项目、owner、选择 epoch、会话绑定与错误收敛多重约束，**未发现越权**；§15.1.4 的一句话结论**不受影响**。

### 17.3 勘误三（未核实推断）：dependabot npm 对 workspace 的覆盖不可由 `directory` 字面断定

**被更正位置**：§16.1-A7（第 906 行）、§16.3 表第 5 行（第 944 行）；连带更正 §15.3 表第 6 行（第 770 行）中的"应用框架栈未被自动更新覆盖"。

**直接依据（仓库侧事实）**：
- 根 `package.json` 声明 `"workspaces": ["apps/desktop", "packages/contracts"]`。
- 根 `package-lock.json`（224331 B）的 `packages` 键**含 `apps/desktop` 条目**，其 `dependencies` 为 `["@ontolearn/contracts","react","react-dom"]` —— **子工作区的依赖出现在根锁文件中**，根级 npm 依赖图**可见**这些包。
- `.github/dependabot.yml`：npm ecosystem、`directory: /`、`interval: weekly`、`target-branch: develop`、`open-pull-requests-limit: 5`；另含 github-actions ecosystem。

**我错在哪**：我仅凭 `directory: /` 的**字面**就断言"`apps/desktop` 子目录依赖（如 react）未被覆盖"——这**未核** Dependabot 对 npm workspace／根锁文件的实际解析与更新范围规则，属**仅字面推断写成已证不覆盖**；且方向性也站不住，因为 `react` 就在根锁文件里。

**更正后的准确表述**：
- **配置事实**：仓内配置了 **root npm 每周更新 PR**（另含 github-actions 每周），target develop。
- **仓库事实**：根锁文件覆盖 `apps/desktop` 的 `react`／`react-dom`，这些依赖**出现在根级依赖图中**。
- **未核**：Dependabot 对该 workspace 的**实际更新范围、PR 生成与合并记录、以及人工修复 SLA 未核验**；uv/vendor 生态未在 dependabot 中配置；EOL 跟踪无记录。
- **因此**：原"应用框架栈未被自动更新覆盖"（§15.3-6）与我的收窄版"`apps/desktop`（react）未被覆盖"（§16.3-5）**两处均不予采信**；正确写法为"**配置 root npm weekly；对子 workspace 的具体覆盖与实际执行未核验**"。
- **不扩大**：未联网、未运行 Dependabot 填此缺口；本条**不新增验证要求、不新增门禁**。

### 17.4 对原最终结论与三类门禁的影响

| 项 | 影响 |
| --- | --- |
| **最终结论** | **不变**：附条件通过（Conditional Pass） |
| **A. push 前源码技术门禁** | **不变（无）**。三条勘误均属**我方的历史定位与描述错误**，**不指向任何源码缺陷**；无新增 P1/P2 |
| **B. 需 push 后新 CI 才核的剩余合并条件（五项）** | **不变**，无一项被解除或新增：①本 head 真实三 job 回单（Windows 完整 3769 逐项或有据 skip、自然 0、无失败／早停／取消／timeout／NOTRUN，后继 typecheck/build/E2E/package/verify 与 Quality packaged recovery 步骤自身 success，**不得以 step 绿或总数替代，不倒填旧 79F/292 原因**）②F03 诊断标签与验收口径裁定 ③F05 唯一状态源追加 ④F01 双审范围书面裁定 ⑤F06/F07/F10 处置归口 |
| **C. 全部原 HOLD** | **不变**，无一项被本勘误消解 |
| **完成度与授权** | **2/17 不变；无 push／CI／merge 票不变；原 15/20 分钟预算不变** |
| **受影响的是表述而非结论** | F03 的因果归因**仍撤回**（依据更正为"因果未证"）；F03 其余各点、§15.1.3 服务层守卫、§15.1.4 结论**不受影响**；清单 136／135 的措辞按 §17.3 更正；§16.1-A7 的"限定同意"改为"**以 §17.3 的三段式表述为准**" |

### 17.5 本节维持不变的事项

§0–§16（159046 B）原字节全部保持；原 **160 条清单**、**78 个历史位置**、**R04 十四条独立行**、原 Top10 与处置表**均不删改**；本节只作勘误与更正指引，**不静默关闭任何意见**。
