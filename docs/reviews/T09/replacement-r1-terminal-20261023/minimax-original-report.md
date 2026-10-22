# T09-S1 replacement-r1：MiniMax Code (M3.1-Flash / xhigh) 完整独立审查报告

- 报告路径：`docs/reviews/T09/replacement-r1/minimax-m31flash.md`（本轮新路径，本方唯一写面）
- 本方 owncwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-s1-minimax-review-7659665`
- 私有 raw：`docs/reviews/T09/replacement-r1-runtime/minimax/raw`
- 私有 scratch：`docs/reviews/T09/replacement-r1-runtime/minimax/scratch`
- 审查模型：MiniMax Code，模型 M3.1-Flash，思考等级 xhigh，权限 始终授权 / bypassPermissions
- 准备与执行日期：2026-10-23（Asia/Shanghai）

> 本轮是 T09-S1 replacement-r1 的**全新完整独立审查**。未沿用前组任务、前组 SID、前组设置回执或前组任何结论；13 项旧问题、3 项 P3 延期与 3 项 PARENT 全部由本方从固定源码与固定原件重新独立判定。未读取另一方本轮报告/提示/意见，未恢复旧停止回合，未创建或操作 GUI。

---

## 1. 最终结论

### **通过**

**范围限定：仅限完整 T09-S1 同版范围** —— 批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → 产品 `76596656908ed84e577e8202a602e3256d5febcc`（tree `8b646570108026a8deabe8330c548cab0280122d`），公共 review HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985`，原流程证据 `d96924e715a1b2139a75b70aea40fc30ae1129fe`。base / source / process 三角色分列核验，未以物理 HEAD 覆盖产品或原流程角色。

**通过理由（本方独立核得）：**

1. 固定输入完整性无缺口：`input-manifest.json` 全部 **106/106 条**目按声明角色（product-diff 55 / existing-process-evidence 42 / approved-prd-context 1 / frozen-round-input 8）从真实 Git 对象取出并逐条重算 SHA-256 与字节数，**全部一致**；其中 55 条（全部 product-diff）还声明了 `gitBlob`，blob 与文件内容一一吻合、0 处不符（`raw/manifest-verification.json`，含另 2 条 base/product tree 身份复算，共 108 条核验记录）。base tree `0a23f708…` 与 product tree `8b646570…` 独立复算一致。
2. 固定 fixture manifest `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` 与 **17/17** 文件摘要一致，绑定 PRD SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` 一致。
3. 本方本轮实际运行 4 条授权普通检查，**真实整数退出码全为 0**：fixture/PRD 校验器（17 文件 / 50 计划 / `productRuntime: not-executed`）、reset 导出（独立原始模型，**不含任何 oracle/expected 键**）、学习专项 pytest（**42 passed**，含 4 套真实 I04 通道与 3 个负例）、前端纯投影 vitest（**18 passed / 16 skipped**）。
4. 本方独立重建并验证了旧问题涉及的每一条断言，不采信历史"已关闭"标签：**13 项旧问题全部独立判为已关闭**，且关闭依据为本方在固定源码/固定原件上的复算，而非旧结论复制。
5. 范围内**无 P0 / P1 / P2 发现**。5 项发现全部为 P3；其中 3 项即总控授权的有条件延期项，经本方独立复核**接受延期**（不接受即不通过的理由不成立），另 2 项为本方新发现的 P3 改进项，不阻断 S1。
6. 未发现把占位界面、测试替身、spike 或合成 adapter 冒充产品能力的情形；未发现把"计划/预期"当"实际领域执行通过"的声明；未发现跨边界回传原始异常、堆栈、路径或单元格原值。

### 明确不覆盖（不因本结论而关闭）

本结论**不关闭** T09 父功能与任何产品发布门，**不构成**条件通过，**不得**据以 push / PR / merge。详见 §9 父门清单与 §8 未验边界。

---

## 2. 身份、模型、权限与来源回执

身份与设置**仅**取自本方映射指定的单份 fresh 操作员回执 `docs/reviews/T09/replacement-pair-r1-20261023/s1-minimax/operator-own-receipt.json`（该文件由操作员唯一写，本审查者只读）。未调用 `agent list` / `session get` / 任何 session/task 列举或发现，未读取用户级或全局 config、凭据、应用状态库、全局日志、安装包内部或 peer 任务/报告/意见。

| 项目 | 实际值 | 来源 | 状态 |
| --- | --- | --- | --- |
| 模型 | `M3.1-Flash（订阅限免）` | 操作员 fresh 新建任务 composer 官方 UI 读回 | 已核 |
| 思考等级 | `xhigh` | 同上 | 已核 |
| 权限模式 | `始终授权`（bypassPermissions） | 同上 | 已核 |
| 设置来源 | fresh own new-task composer；无全局配置或模型自发现 | 回执 `settingsSource` | 已核 |
| 任务目录绑定 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-s1-minimax-review-7659665`（官方目录选择器 GoTo 完整路径读回 + composer 本人文件夹标签） | 回执 `actualTaskCWDFromOfficialUI` | 已核，并与本方实际 cwd 逐字一致 |
| 操作员 shell HEAD | `72aa83a80a973a3edeb62ed95518bf1a22178985` | 回执 `operatorShellHEAD` | 已核，与本方实际 `git rev-parse HEAD` 一致 |
| 正文输入 | 75943 bytes，SHA-256 `18fbcbe32a1dd353e36c63a311db31f7257e2b0ef2ad538dc2084880ec47fe1b` | 回执 `fullInputBytes` / `fullInputSHA256` | 已核：本方应用原生全文附件与固定副本 `full-input.md` 均为 75943 bytes 且 SHA 完全相同 |
| 总控 START 收到 | `rootStartReceived: true` | 回执 | 已核 |
| 仅本方任务 | `onlyThisOwnTask: true` | 回执 | 已核 |
| **sessionId** | **UNKNOWN** | 操作员侧，尚未写入 | **无法验证（按指令不发现补齐）** |
| **originalTurn** | **UNKNOWN** | 同上 | **无法验证** |
| **acceptedAtUTC（正文受理时间）** | **UNKNOWN** | 同上 | **无法验证** |
| **officialMenuSIDReadBack** | **UNKNOWN** | 同上 | **无法验证** |
| **unsentDraftCleared（未发草稿清空）** | **UNKNOWN** | 同上 | **无法验证** |

回执自身状态字段为 `fresh draft observed before single send; SID/accepted fields pending`。因此**任务实例标识与受理时刻在本轮结束时仍未由操作员回填**。

**绑定边界（重要）**：本报告的实质身份链为 —— 模型/等级/权限（fresh 官方 UI 读回）+ 候选绑定（cwd 与 HEAD 双重复核）+ 正文绑定（75943 B / SHA-256 逐字节一致）+ 独立性（本方未接触任何 peer 意见），这些均已独立核验。而 sessionId / originalTurn / acceptedAtUTC / officialMenuSIDReadBack / unsentDraftCleared 属 operator-only 收件范围，本轮输入明确不转授审查模型、且明确禁止本方以发现手段补齐，故逐项记 UNKNOWN。**在总控以官方 UI 补齐上述任务实例绑定并按窄路线收件正式终态之前，本报告不得被当作"已绑定到具体任务记录"的正式终态用于同版双方通过判定。** 此为流程绑定边界，不改变 §1 对 S1 代码范围的审查结论。

本方运行环境模型与回执声明的 M3.1-Flash 一致，且本方持有的输入字节与回执声明的 `fullInputSHA256` 完全一致——正文受理链可由字节自证，不依赖任何环境自述。

---

## 3. 候选绑定与工程核对

### 3.1 Git 身份

```
pwd                       /Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-s1-minimax-review-7659665
git rev-parse --show-toplevel   同上
git rev-parse HEAD         72aa83a80a973a3edeb62ed95518bf1a22178985   ← 与映射 expectedReviewHead 一致
git rev-parse --abbrev-ref HEAD  HEAD（detached）
git rev-parse HEAD^{tree}  0216b1729f0f43af5f1202225a76f6c7fc6a4bdc（review HEAD 自身 tree，非产品 tree）
```

base `5f910b52c69d86a1076b2032e5d3c63e715947f3`（tree `0a23f708a3d59f3e2a0353d6f069169ff8e26b3f`）、产品 `76596656908ed84e577e8202a602e3256d5febcc`（tree `8b646570108026a8deabe8330c548cab0280122d`）、原流程证据 `d96924e715a1b2139a75b70aea40fc30ae1129fe` 三者在本地对象库中**均存在且分列可取**，本审查未以 review HEAD 的物理内容冒充产品或原流程角色。

### 3.2 base → product 全区间

`git diff --name-status 5f910b52 7659665` = **55 个文件，全部为新增（A）**，合计 38162 行新增，分布与 `input-manifest.json.productChangedPaths`（55 条）完全一致，无缺项、无多项。32 条产品源/数据路径与 `productSourceAndDataPaths` 一致。

### 3.3 固定 manifest 全量核验（本方脚本，非人工比对）

`raw/manifest-verification.json`：

- 106/106 条目：**SHA-256 与字节数全部匹配**，状态全部 `OK`。
- 55 条声明 `gitBlob` 者（全部 product-diff）：**blob 内容与路径内容一致，0 处不符**。
- base tree / product tree 身份：均 `OK`。
- 固定 fixture manifest 的 17 个文件摘要：**17/17 `OK`**。
- 绑定 PRD：`docs/prd/PRD-本体学习与落地Agent工作台.md` @ base 的 SHA-256 = `7586b2c4…60fbb`，与 manifest 声明一致（`OK`）。

### 3.4 保护态与漂移

- `AGENTS.md` 当前 SHA-256 = `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`（与本轮输入声明一致），保持 **未暂存 M**，本方**未修复、未 stage、未还原**。
- `git diff --cached --name-only` 为空：**本方未 stage 任何文件**。
- 审查结束后复核：`git diff --stat HEAD -- apps packages scripts tests content docs/iterations docs/reviews/T09/round-1` **为空** → **产品/测试/配置/依赖/锁零漂移**。
- 未提交、未推送、未切分支、未合并、未建 PR，未改 Goal，未写根 `state.json` / `tasks.json` 或其他总控文件。
- 本方新增目录仅 `docs/reviews/T09/replacement-r1/`（本报告）与 `docs/reviews/T09/replacement-r1-runtime/minimax/{raw,scratch}`（私有运行产物）。仓库内既有未跟踪目录 `dispatch-20261022/`、`dispatch-inputs/`、`dispatch-runtime/`、`replacement-pair-r1-20261023/` 为派发流程材料，非本方产生，本方未删除、未加 ignore 求绿。

---

## 4. 实际读取覆盖（逐项，非摘要）

### 4.1 产品源码与数据（32 条，全部实际读取）

| 范围 | 文件 | 实际读取内容与核验点 |
| --- | --- | --- |
| 引擎 learning 包 | `learning/__init__.py`（89 B）、`learning/baselines.py`（9201 B）、`learning/service.py`（9559 B） | 全文读取。`baselines.py`：manifest 完整覆盖判定、17 文件摘要、PRD 摘要、coverage↔PRD 原文子串校验、50 用例唯一性与版本字段、`equipment.csv` 固定行、`productRuntime: not-executed`；`store_seed_plan` 定义分层与 ID 规范（点号包装）；`seed_test_project` 仅经 `Store.commit` 且拒绝非 pristine 项目。`service.py`：`Context`/`Attempt`/`ToolEvidence` 校验、`_normalise` 集合/顺序语义、`check()` 的身份/依据/来源/完整对象比较、辅助升级、`record_agent_full_assistance` 失效语义、`report_record` 白名单投影 |
| 固定验证脚本 | `scripts/verify-product-baselines.py`（921 B） | 全文读取；`--reset` 输出独立原始模型，异常固定中文前缀并非零退出 |
| 内容 | `content/learning/course.json`（15178 B）、`glossary.json`（5173 B）、`checks.json`（881942 B）、`transfer-inputs.json`（9091 B） | 全文读取 + 结构化勘测。9 任务 / 6 模块 + 2 迁移 + 1 报告；每任务 goal/instructions/completionCondition/next/4 级提示/commonErrors/knowledgePoints/transfer；术语 **23 条**，三层（plain/example/technical）**全部非空**；checks **54** 项（= 50 PRD 用例 + 4 门课程级检查），与 cases/course 交叉引用**无孤儿** |
| 固定 fixture | `tests/fixtures/product-baselines/` 13 个数据文件 + `manifest.json` | `manifest.json` 全文；`G-base`（18 条事实、字符串身份 `001`、空初始工单/事件）、`G-map-empty`（0 事实 / 0 行为）、`G-behavior`（B-risk/B-a/B-b/B-multi/X/Y/B-probe，X 设 `P=true`、Y 条件要求 `P=false`）、`E.5`（2 产能 × 4 轮 = 8 轮完整 round 对象）、`cases.json`（50 用例，含 setup/steps/failurePath/externalInputRequired/版本四元组）、`coverage.json`（50 条 PRD 原文）、4 个 CSV、`unclosed-high.rq`、`conventions.json` |
| renderer | `learning/LearningWorkspace.tsx`（18386 B）、`presentation.ts`（6215 B）、`types.ts`（2407 B）、`content.ts`（398 B）、`learning.css`（10765 B） | 前四份全文逐行读取；`learning.css` 作为样式资产读取并纳入产品 diff 覆盖（未逐条审计 CSS 规则语义，仅核无外部依赖/无远程资源） |
| 前端测试 | `tests/unit/learning-presentation.test.ts`（6791 B）、`learning-workspace.test.ts`（21193 B） | 两份全文读取，逐条清点断言 |
| Python 测试 | `test_learning_baselines.py`（11784 B）、`test_learning_service.py`（9207 B）、`test_learning_jobstore_integration.py`（8383 B） | 三份全文读取，逐条清点断言与负例 |
| 文档 | `docs/iterations/T09/{handoff.md,learning-ui-contract.md,user-acceptance.md}` | 全文读取（handoff 为 d969 流程版）。真人验收为**空记录**、未造样本、未对外招募 |

### 4.2 原验证/失败原件与历史意见（d969 角色，全部实际读取）

- `evidence/learning-ui-verification.json`（6987 B）—— 当前同版过程证据，逐字段核对。
- `evidence/npm-check-ui-final.txt`（5314 B，SHA `210d3d9b…41e5`）—— 实际读出并核对：`eslint . --max-warnings 0`、`tsc --noEmit`（两处）、`vitest run` → **17 个 Test Files / 664 Tests passed**、`ruff check` + `ruff format --check` → `All checks passed!`、`pytest` → **1094 passed in 52.32s**。
- `evidence/npm-check-{final,after-review,jobstore-final}.txt`、`learning-{pytest-final,pytest-after-review,42-pytest}.txt`、`first-learning-pytest.txt`、`first-ruff.txt`。
- **12 个 gzip 首败归档全部解压复核**（`raw/archive-expansion.json`）：每个压缩件解压后的 SHA-256 与字节数**与证据中登记的原始 raw SHA/字节逐一吻合（12/12 OK）**，并逐个核对了其失败文本：
  - `first-npm-check.txt`（66464 B）→ 末行 `27 failed, 1055 passed`，正文为 `ValueError: Fixture digest mismatch: content/learning/checks.json` —— 与"27 digest mismatch"记载一致。
  - `jobstore-first-pytest.txt`（15311 B）→ 末行 `4 failed, 3 passed in 33.46s`；失败文本为 `assert final["state"] == "succeeded"` 与 `timeout` 相关 `ValueError`。**原件确实没有直接打印 dependencyKey 错误**，与历史索引"原件并非直接打印 dependencyKey 错误"的诚实说明一致。
  - `ui-third-vitest.txt`（13634 B）→ `Tests 13 failed | 16 passed (29)`，错误为 `(0 , import_jsx_dev_runtime.jsxDEV) is not a function` —— 与"第三次 16 纯 pass / 13 组件 fail"一致。
  - `ui-first-vitest.txt` / `ui-second-vitest.txt`（入口解析 / 缺匹配浏览器）、`ui-fourth-vitest.txt`（中间 30 项）、`npm-check-ui-first.txt`（ESLint 扫到下载的浏览器 `content.js`，路径在**原开发树** `.runtime/playwright/chromium_headless_shell-1248/…`）、`npm-check-ui-type-failure.txt`（TS2353）、`npm-check-ui-intermediate-661.txt.gz`、`ui-browser-install.txt.gz`（真实 Chromium 下载记录）、`ui-eslint.txt.gz`（0 字节）、`ui-typecheck.txt.gz`。
- `evidence/{baseline-verification.json, ui-fixed-baseline-check.json, jobstore-verification.json}`、`evidence/verification-summary.json`、`independent-review.md`、`jobstore-integration-review.md`、`learning-ui-independent-review.md`、`operation-policy-receipt.md`、`recovery.json`、`status.md`、`controller-delivery.json`、`coordination-authorization.json`、`ui-controller-delivery.json`。
- **两张 UI 截图实际查看**：`evidence/ui/desktop-course.png`（1440×1050）与 `evidence/ui/mobile-behavior.png`（文件 390×1932，采样 viewport 390×844）。桌面图确认 9 任务路径、6 模块 + 2 迁移 + 报告、四级提示、术语区、"完成，不等于独立掌握"边界说明、"课程预览 · 提示可阅读，当前不会保存学习进度。"。移动图确认 390px 下内容纵向堆叠、提示 2 列栅格、术语区下移、路径为横向滚动容器而非页面横向溢出。
- `docs/reviews/T09/round-1/input-manifest.json`（106 条）、`verification-and-history-index.md`（归档历史索引）、`freeze-receipt.json`。

### 4.3 本方未读取（按指令明确排除）

- 另一方本轮冻结提示正文（`round-1/zcode-glm53-input.md`）与其 materializedPath —— 只在 manifest 中核对了其**身份登记**（bytes/SHA），**未打开正文、未跟随其路径**。
- 前组任务的报告、launch/terminal packet、旧指定模型意见与原运行元数据（`dispatch-runtime/` 下的 task-settings/setup/raw/scratch/metadata）。
- 全局/用户级 config、应用状态库、全局日志、安装包与运行时内部实现、peer 任务与意见。
- `.mimosa` 等未知元数据（未读取、未 hash、未解析、未删除）。

---

## 5. 实际运行（本方新运行，非历史复述）

### 5.1 运行收据

运行器 `scratch/run_checks.py` 以**直接子进程**执行，stdout/stderr 分别落盘，用 `subprocess.run(..., check=False).returncode` 取得**真实整数退出码**；未使用 `tail`/`grep`/`tee`/管道末命令或 `echo` 掩盖子进程失败，未把 `isError=false` 当 exit 0，未把 runner 退出与 child 退出混为一谈。完整收据：`raw/run-receipt.json`。

| id | argv | cwd | env 差异 | 开始(UTC) | **returncode** | stdout / stderr |
| --- | --- | --- | --- | --- | --- | --- |
| verify-product-baselines | `.venv/bin/python scripts/verify-product-baselines.py` | owncwd | `TMPDIR`→本方 scratch；unset `T09_HEADLESS_UI`/`PLAYWRIGHT_BROWSERS_PATH`/`ONTOLEARN_TEST_ENGINE` | 2026-10-22T21:11:49Z | **0** | 876 B / 0 B |
| verify-product-baselines-reset-G-base | `.venv/bin/python scripts/verify-product-baselines.py --reset G-base` | owncwd | 同上 | 同上 | **0** | 8227 B / 0 B |
| learning-pytest-suite | `.venv/bin/python -m pytest packages/engine/tests/test_learning_{baselines,service,jobstore_integration}.py -q` | owncwd | 同上 | 同上 | **0** | 99 B / 0 B |
| learning-vitest-unit | `npx --no-install vitest run tests/unit/learning-presentation.test.ts tests/unit/learning-workspace.test.ts` | owncwd | 同上 | 2026-10-22T21:11:52Z | **0** | 270 B / 0 B |

### 5.2 结果与判读

- **fixture/PRD 校验**：输出 `version: prd-v0.6-learning-1`、`manifestSha256: aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`、`filesVerified: 17`、`casesPrepared` 恰为 50 条（M-01..06、Q-01/02、V-01、O-01、R-01..06、B-01..11、A-01..10、G-list-01..13）、`productRuntime: not-executed`。
  **额外交叉印证**：本方该次 stdout 的 SHA-256 = `e3cf790a4e1f3cdb3616a8690d106cea59998f4260733535d93c1ec3551758fb`，与归档 `evidence/baseline-verification.json` 的登记 SHA **逐字节相同**——本方独立运行**精确复现**了归档基线校验产物。
- **reset 导出**：输出顶层 17 键，**不含 `expected` 键**（递归探针确认任意层级均无 `expected`），`facts` 18 条 → 确认"reset 返回独立原始模型、不预置 oracle/推导"。
- **学习专项 pytest**：stdout 末行 `42 passed in 2.70s`，stderr 0 字节，退出码 0。本方 `--collect-only -q` 实测分解为 **fixture 完整性 11 + reducer/服务 24 + 真实 I04 通道 7 = 42**（`test_learning_jobstore_integration.py` 的 7 项 = 4 个 baseline 成功通道 + 3 个负例模式：stale-preview → `REVISION_CONFLICT`、worker-failure → `INTERNAL_ERROR`、product-mode → `UNSUPPORTED_CAPABILITY`；每个成功通道真实经 rollback 预览 / stdio coordinator / 隔离 worker / test.atomic 提交 / operation.get / result.page / SQLite 重开 / 依赖向量）。
- **前端 vitest**：stdout `Test Files 1 passed | 1 skipped (2)` / **`Tests 18 passed | 16 skipped (34)`**，退出码 0。**16 项浏览器组件测试为 skip，不是通过**；本轮**未**将 skip 报为浏览器通过，**未**重跑已知缺 1248 的 headless 失败，**未**安装任何 runtime。
- **浏览器环境事实（只读自本人 node_modules）**：`@playwright/test` 1.64.1，其 `playwright-core/browsers.json` 要求 `chromium` / `chromium-headless-shell` revision **1248**，与已知历史缺失项一致。本方**未**做浏览器缓存盘点、**未**扫描全局缓存、**未**更换 Playwright 版本、**未**以更宽 sandbox 求绿。

### 5.3 与参考命令的偏离（如实披露）

参考命令为 `uv run --frozen pytest …`。本方改用映射中已存在的 `existingVenv`（`.venv/bin/python -m pytest …`）执行，原因是避免任何 `uv sync` 触发的联网与 venv 写入副作用；本方**未**执行 `uv sync`，**未**改动 `.venv`、`uv.lock`、`pyproject.toml` 或任何依赖。该偏离不改变被测代码与断言，运行器为直接子进程等待，退出码为真实整数。

### 5.4 静态勘测脚本（本方只读探针，非产品代码）

- `scratch/verify_manifest.py` → `raw/manifest-verification.json`（106 条 + 17 fixture + 2 tree 身份）。
- `scratch/probe_fixtures.py` → `raw/probe-fixtures.json`（G-list-01 ↔ E.5 oracle 一致性、G-list-09 ↔ M-04 一致性、cases 结构、CSV、conventions、coverage）。
- `scratch/expand_archives.py` → `raw/archive-expansion.json` + 12 份解压原文（只读原件，输出到本方 raw）。

---

## 6. 发现

范围内**无 P0、无 P1、无 P2**。以下 5 项全部为 P3。

### F-01（P3）导出成功回执守卫缺少组件断言 —— 与总控延期项 S1-OBS-01 同对象，本方确认其成立

- **位置**：`apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx:308-325`（守卫）、`:485-494`（按钮与缺席提示）。
- **现状**：守卫本身**存在且正确** —— `sameContext(result.context, context) && result.exported` 同时校验上下文与成功标志；`exported:false` 或异/迟到 context 一律落入固定中文"报告尚未导出，请重试。"；`actions.exportReport` 缺席时按钮 `disabled` 并显示"报告导出暂不可用。"；`exportReport` 返回 `undefined` 会在 `try` 内抛 `TypeError` 并被 `catch` 转为固定提示，**不会假成功**。
- **缺口**：`tests/unit/learning-*.test.ts` 中**对 `exportReport` 的断言数为 0**（全文检索 `exportReport` 与"导出"均无命中）。总控点名的三类组件断言——**缺能力**、**`exported:false`**、**异迟 context**——**全部不存在**；实际上整个导出交互路径**无任何自动化覆盖**。
- **触发**：需要 T10 接入 `exportReport` 后才会可达。
- **影响**：导出"假成功"这一原始验收反例当前只有**静态**保障，无自动化回归护栏；后续接线者若改动守卫或提示文案，无测试会失败。
- **证据**：`LearningWorkspace.tsx:316`（守卫条件）、`:488`（disabled 条件）、`:494`（缺席提示）；`tests/unit/learning-workspace.test.ts` 全文无导出相关断言。
- **建议**：按总控延期条件，在 **T10 正式导出接线验收前**补齐三类组件断言（缺能力 → 按钮禁用且显示固定提示；`exported:false` → 显示"报告尚未导出，请重试。"且不显示成功；异迟/异 context 回执 → 同样不显示成功）。
- **本方处置**：**接受延期**（见 §8）。

### F-02（P3）两迁移任务的 1/2/3 级提示文本完全相同 —— 与总控延期项 S1-OBS-02 同对象，本方确认其成立

- **位置**：`content/learning/course.json:241-256`（transfer-repair）与 `:278-293`（transfer-classify）。
- **现状**：两个迁移任务的 L1/L2/L3 提示文本**逐字节相同**（"先判断要校验已有记录还是计算新分类。" / "使用检查报告定位对象；查看事实来源而非只看显示名称。" / "示范查看一个已有名称的断言来源；其余独立完成。"）。仅 L4 不同（分别指向 `equipment/102`/`供水泵` 与 `equipment/201`/`检测泵`/`T-A1`）。CONTENT-01 所修的"第 4 提示跨题泄露"**确已闭合**（两题 L4 互不含对方实体号，且对应 `transfer-inputs.json` 实际数据，核对一致）。
- **触发**：学习者在前三级得到的是跨题通用文本，两题在前三级的区分度仅靠 L1 一句"要校验已有记录还是计算新分类"的自述。
- **影响**：纯内容可读性/教学区分度问题；**不构成洗白风险**——L1/L2/L3 完全一致意味着任何一题使用过提示都会同样抬高尝试水位，UI 侧 `currentFloor` 反而**更严格**（任一题的提示水位都会作用于同 attempt 的另一题）。
- **建议**：留待后继内容候选增强时区分两题 L1–L3；**不得改动当前冻结题**（改动会触发新候选与双方全新完整审查）。
- **本方处置**：**接受延期**（见 §8）。

### F-03（P3）`checks.json` 内联 E.5 oracle 与固定 expected 缺自动一致断言 —— 与总控延期项 S1-OBS-03 同对象，本方确认其成立

- **位置**：`content/learning/checks.json` 的 `G-list-01`（内联 `capacities.3/4` + `independentReplays`）、`G-list-06`（`independentReplays` 2 次 + `resumeFromRound2`）；对照 `tests/fixtures/product-baselines/E.5.json` 的 `expected["3"] / ["4"]`；另 `G-list-02.expected = {exactFile:"E.5.json", exactPointer:"/expected/3", crossPhaseConflict:false}`。
- **本方独立实测（当前状态一致）**：`checks["G-list-01"]["expected"]["capacities"]["3"]` 与 `E.5.json#/expected/3` **完全相等**；`capacities["4"]` 与 `E.5.json#/expected/4` **完全相等**；`G-list-06.expected.independentReplays` 长度 2 且**两次互等**；每轮对象含 `actionTrace`（8 条）与 `scheduledFutureEvents`（12 条）等 16 个字段，与 E.5 源同构。
- **缺口**：`packages/engine/tests/` 中**无任何断言**把 `checks.json` 的内联 oracle 与 `E.5.json` 的 expected 绑定（全文检索 `G-list-01` 仅出现在 `test_learning_service.py:212` 的合成 adapter 载荷改写处，`checks.json` 仅被作为合成 adapter 的 expected 来源读取）。因此"当前一致"是**本方一次性探针的实测结果**，不是受保护的回归不变量。
- **触发**：`checks.json` 或 `E.5.json` 任一被维护修改且 manifest 摘要同步刷新时，两者可能静默分叉，且不会有任何测试失败。
- **影响**：数据当前无分叉（已实测），风险为**回归护栏缺失**而非现值错误；暴露面被固定 manifest 摘要限定（任一文件改动都会先使 `verify()` 失败），故非静默失效。
- **建议**：按总控延期条件，在相关内容或 oracle 下次维护前补**完整对象、顺序、双 replay 与固定 expected 的直接一致断言**（不得只比长度/计数/公式、不得互相复制、不得弱化完整比较）。
- **本方处置**：**接受延期**（见 §8）。

### F-04（P3，本方新发现）renderer 的 `recordVersion` 哨兵值 0 与严格 `>` 版本守卫冲突

- **位置**：`LearningWorkspace.tsx:61-76`（`currentFloor`）、`:266-270`（`showHint` 回执守卫）、`:292-299`（`checkTask` 回执守卫）；对照 `docs/iterations/T09/learning-ui-contract.md:13`（owner 契约："每个完整 context 的 recordVersion 为**单调非负整数**；一次新检查/提示必须返回严格更新版本"）。
- **触发**：同一 attempt 已在**另一 inputVersion** 下存在记录（`currentFloor` 的 `related` 非空 → floor 存在），而 owner 对当前 inputVersion 的**首条**回执使用 `recordVersion = 0`。此时 `currentFloor` 对当前精确 context 取 `acknowledged[contextKey(context)]?.floor.recordVersion ?? 0` = **0**（"该 context 尚无记录"的哨兵），而守卫条件是 `receipt.record.recordVersion <= floor.recordVersion` → `0 <= 0` 成立 → 回执被拒。
- **影响**：该 attempt 在新输入下的**首次提示与首次检查**会被拒（固定中文"提示使用记录与当前任务不一致，请重试。"／"检查结果与当前输入或提示记录不一致，请重新检查。"），在该 attempt 内形成死路，直至 owner 的版本计数器前进到 ≥1。属**功能性拒绝**，非安全洗白（拒绝方向是保守的）。可达性取决于未实现的 T01 版本编号起点：若 owner 从 1 起编，则不触发。
- **证据**：`currentFloor` 用 `?? 0` 兼作"无记录"哨兵，而契约明确允许 0 为合法版本号；`projectionRecord`（`presentation.ts:159-164`）用 `>=` 比较同一 floor，行为不一致；现有测试全部从版本 1 起（`learning-workspace.test.ts:76` `state.version++` 先自增），**无覆盖首条版本 0**。
- **建议**：在 T01 接线前把"无记录"哨兵与合法 `recordVersion = 0` 分离（例如 floor 用 `undefined`/独立标志表示"该 context 无记录"，或把守卫改为"首条记录允许任意非负版本、其后要求严格递增"），并补一条首条 `recordVersion = 0` 的组件断言。
- **本方处置**：不阻断 S1（触发面窄、依赖未实现 owner 编号、拒绝方向保守、无洗白风险）；建议在 T01 正式接线验收前一并处理。

### F-05（P3，本方新发现）`evidence/verification-summary.json` 缺阶段/提交标记，其源码摘要块对应的是修前版本

- **位置**：`docs/reviews/T09/evidence/verification-summary.json:5-12`（`sourceCodeSha256` 块）、`:22-32`（命令与计数）。
- **现状**：该文件**不含 commit / 阶段字段**，其 `sourceCodeSha256` 中 `packages/engine/src/ontolearn_engine/learning/baselines.py` = `a2435502cf7aee0190f468c865aeefb60b63efa069f92b24ba4b92fd4a0552a0`。本方实测：该摘要**正是 `51cdc0e`（INFRA-01 点号包装 ID 修复之前）版本**的 baselines.py；当前产品 `7659665` 的 baselines.py 为 `a2b8921903f460fa1128c45e8c92f2b14e2a493d9d1e99901bf6d9b707e04d94`。同块其余 5 个文件摘要与服务层摘要**与当前产品一致**。
- **影响**：读者若把该文件的 `sourceCodeSha256` 当作当前产品摘要，会对 `baselines.py` 得到错误结论。缓解因素：该文件内的计数（35 学习 / 630 Vitest / 1087 Python）与当前候选（42 / 664 / 1094）明显不同，归档历史索引亦已把它正确限定在"51cdc0e 早期内容/Store"阶段；因此**不构成对当前候选的错误通过声明**，但缺少显式阶段标记使其具备误读风险。属文档准确性问题，不是产品缺陷。
- **建议**：在 `verification-summary.json` 增补 `implementationCommit` / 阶段标识（或把该摘要明确标注为 51cdc0e 阶段），避免后续读者据其源码摘要块误判当前候选。
- **本方处置**：不阻断 S1；建议在下次流程证据维护时修正。

---

## 7. 13 项旧问题独立重判

判定依据一律为**本方在固定源码/固定原件上的复算**，不采信历史索引的"已关闭"标签。

| 编号 | 历史问题 | 本方独立核验依据 | 本方结论 |
| --- | --- | --- | --- |
| CONTENT-01 | 迁移题正文泄露答案、第 4 提示跨题泄露 | `course.json` 全文：两题 `instructions` 均无答案实体；L4 互不含对方实体号（repair-L4 无 "201"、classify-L4 无 "102"）；`transfer-inputs.json` 中 `equipment/102` 缺 name、参考清单 102=供水泵；`equipment/201` name=检测泵、告警 `T-A1` High/Open —— L4 与实际数据**一致对应**；`test_learning_baselines.py:272-278` 的防泄露断言存在 | **已关闭** |
| CONTENT-02 | G-list-09 的 CSV 与 M-04 非同版源 | `cases.json` 中 M-04 与 G-list-09 的 `relink`/`map` 步骤**同指** `equipment-updated.csv` 且**同记** `sourceSha256: f513469a…ce171`；本方实测该文件摘要与 manifest 登记一致，内容 `001,源端新名称 / 002,泵站B`；`checks.json` 的 `G-list-09.exactBaseCaseExpected` 与 `M-04.expected` **逐字段完全相等**（本方探针实测 `true`） | **已关闭** |
| CONTENT-03 | E.5 行为版本不匹配 | `cases.json` 全部 E.5 起点用例 `behaviorVersion = e5-behaviors-1`，与 `E.5.json.behaviorVersion` 一致；`test_learning_baselines.py:269-271` 对**全部** E.5 用例做断言 | **已关闭** |
| CONTENT-04 | M-03 人工备注放在 001，无法检出误删 002 | `cases.json` M-03：`manual-add` 的事实为 `equipment/002 / note / "手工备注"`；第三步改用只含 001 的内联 CSV（撤回 002 受管事实）；`checks.json` M-03.expected.facts = {001 type, 001 name 泵站A, **002 note 手工备注**}，ownership 仅 2 条（001 受管事实）—— **被撤回的 002 的人工备注被保留、受管事实被撤回**；`test_learning_baselines.py:259-268` 有精确断言 | **已关闭** |
| CONTENT-05 | E.5 轨迹/未来排程证据不完整 | 本方实测：E.5 `expected["3"]`/`["4"]` 每轮均含 `actionTrace`（8 条）与 `scheduledFutureEvents`（12 条），且 `checks.json` G-list-01 的内联 oracle 与之**逐对象相等**；`test_learning_baselines.py:163-186` 对**两产能全部 4 轮**断言 actionTrace 形状、scheduledFutureEvents 余量、orders ID 序列、consumedEvents 序列；G-list-06 两次独立 replay **互等** | **已关闭** |
| INFRA-01 | 冒号包装 ID 违反 dependencyKey、提交后 project.get 超时 | `baselines.py:144/166/173/191` 使用 `baseline + ".ontology"`、`<baseline>.initial`、`E.5-capacity-N` **点号**形式；`test_learning_jobstore_integration.py` 断言 `dependencyVector` 键为 `layer + ":" + id` 且 `reopened.project_get` 通过 `CONTRACT.validate("result_project.get")`；本方本轮 **42 项 pytest 实际通过**（含 7 项真实通道：预览零正式写入、stdio worker、提交收据、result.page、重开读回、依赖向量）；负例三模式按预期拒绝 | **已关闭** |
| UI-01 | 高版本降级辅助、同版本冲突可洗成独立 | `presentation.ts:112-152` `observeRecord`：同版本异内容 → `conflictVersion`；`projectionRecord:157` 遇冲突即 `undefined`；`floor` 的 `maxHintLevel`/`assistance` 单调不降；`test_learning-presentation.test.ts:140-166` 覆盖 newer-lower / same-version-conflict / 更早版本；浏览器变体 `newer-lower`、`same-version-conflict` 存在 | **已关闭** |
| UI-02 | 真 context 缺保存能力仍先显示提示 | `LearningWorkspace.tsx:245-256`：无 context → 预览/迁移题拒绝；**有 context 但缺 `recordHint` → 固定提示且 `return`，不揭示答案**；`:261-273` 回执不符亦拒绝；`:276-278` 保存失败 → 固定中文且不显示提示内容（组件测试断言不泄露 `synthetic-sensitive-message`）；迁移题四级在预览下一律拒绝 | **已关闭** |
| UI-03 | 同 attempt 换 input 洗白 | `LearningWorkspace.tsx:61-76` `currentFloor` 按 project/task/**attempt** 聚合（**忽略 inputVersion**）取最高提示与辅助；`currentRecord:77-88` 与回执守卫均要求达到该水位；浏览器用例"retains assistance when inputs change inside the same transfer attempt"存在 | **已关闭** |
| UI-04 | 丢弃矛盾新版后旧独立通过仍计当前 | `presentation.ts:127-139` 保留**版本更高**的记录为 `latest`（不因语义矛盾而丢弃），`conflictVersion` 使 `projectionRecord` 返回 `undefined` → 不回退旧 pass；`test_learning-presentation.test.ts:167-183` 与浏览器 `contradictory-newer` 变体覆盖 | **已关闭** |
| UI-05 | maxHint 5 污染水位、后续合法 4 永久不可用 | `presentation.ts:116-124` `nextFloor` 对非法 `maxHintLevel` 归 0（不写入越界值），非法 assistance 归最低档；`projectionRecord` 因 `validRecord` 失败而不可用（fail-closed）；随后合法新版本可恢复 —— `test_learning-presentation.test.ts:184-199` 明确断言"无效不污染可恢复水位" | **已关闭** |
| DOC-01 | 旧 873 recovery 仍指初始 51 摘要 | 本方实测当前 `recovery.json`：`implementationCommit = 76596656908ed84e577e8202a602e3256d5febcc`、`implementationTree = 8b646570…`、`manifestSha256 = aaaef2c0…`、`verification = evidence/learning-ui-verification.json`、`independentReview = learning-ui-independent-review.md`，并以 `previousImplementationCommit` 保留 873 历史；`operation-policy-receipt.md` 记录 6f6264b 的定位修复 | **已关闭** |
| DOC-02 | opt-in/runtime skip 措辞、截图尺寸、sandbox 范围表述 | `learning-ui-verification.json` 明写"未设 `T09_HEADLESS_UI=1` 恒 skip，与 runtime 有无无关；设 1 缺匹配 runtime 是启动失败"，并把 desktop（viewport 1440×1050 = imageSize）与 mobile（viewport 390×844 / imageSize 390×1932）**分记**；`browser.assuranceBoundary` 明写"仅证 chromiumSandbox:true 配置与成功，未采当次 argv/OS sandbox 状态与二进制 hash，不当作原生平台隔离证明"；`status.md:63`、`handoff.md:53`、`learning-ui-contract.md:23-25` 口径一致。**本方本轮实测印证**：未设开关时 16 项浏览器用例确为 **skip（16 skipped）而非 pass** | **已关闭** |

**13/13 独立判定为已关闭。** 关闭依据全部为本方可复算的源码/原件证据。

---

## 8. 三项 P3 总控有条件延期：独立重判

总控仅将下列三项认作**当前有界 S1 非阻断延期**，未改冻结候选、未将问题标已修或关闭，也不代表另一模型本轮意见。本方逐项独立判定：

| 编号 | 待改进对象 | 本方独立核验 | 本方处置 | 理由 |
| --- | --- | --- | --- | --- |
| S1-OBS-01 | 导出成功回执守卫缺组件断言 | **成立**：`tests/unit/learning-*.test.ts` 中 `exportReport` 断言数为 **0**，缺能力/`exported:false`/异迟 context 三类断言全无（见 F-01） | **接受延期** | 守卫本身经本方逐行静态核对**正确**（上下文 + 成功标志双校验、失败路径固定中文、无假成功）；S1 **无 T10 导出接线**，`actions.exportReport` 在 S1 不可达，缺能力态实际恒为"按钮禁用 + 报告导出暂不可用"；该缺口不构成安全或数据正确性风险。延期条件（T10 正式导出接线验收前补三类断言）与风险暴露时点对齐，条件恰当 |
| S1-OBS-02 | 两迁移任务 1/2 级提示区分度 | **成立**：两题 L1/L2/L3 **逐字节相同**，仅 L4 不同（见 F-02） | **接受延期** | 内容可读性/教学区分度问题，非洗白风险（两题共用 L1–L3 反而使同 attempt 水位更严）；改动当前冻结题会触发新候选与双方全新完整审查，代价与收益不相称 |
| S1-OBS-03 | `checks.json` 内联 E.5 oracle 与固定 expected 缺自动断言 | **成立**：无任何自动化断言绑定二者（见 F-03）；但本方实测**当前两者逐对象相等**（容量 3/4 各 4 轮完整相等，`independentReplays` 两次互等） | **接受延期** | 现状**无数据分叉**，缺的是回归护栏而非正确性；暴露面受固定 manifest 摘要硬约束（任一文件改动必先使 `verify()` 失败）；延期条件（相关内容或 oracle 下次维护前补完整对象/顺序/双 replay 直接一致断言）与风险触发时点对齐 |

**三项均接受延期**，不构成 S1 阻断。若后续发现这三项在 S1 范围内实际可达并产生错误结果，本方会改判——但本方在本轮未发现任何此类可达性。

---

## 9. PARENT 保留项与父门

### 9.1 三项 PARENT（**保留，未关闭**）

| 编号 | 内容 | 本方独立核验 |
| --- | --- | --- |
| PARENT-01 | 多阶段历史 Q-01 与修复前后不可重贴终态标签 | **保留**。`cases.json` 中 Q-01 与 Q-02 的 `steps` 相同但 **setup 不同**（Q-02 额外 `replace alarm/A01 status "Closed"`），`checks.json` Q-01 rows=[A01]、Q-02 rows=[] —— 输入区分真实存在；但**逐阶段版本/快照/结果绑定的公共契约与真实适配尚未实现**（`handoff.md:37` 明确列为待 T00/T01 批准），本轮无任何产品机制阻止历史阶段结果被重贴当前 |
| PARENT-02 | G-list-02 不是完整 round DTO 比较器；A-10 仅三个固定反例 | **保留**。本方实测 `checks.json` 的 `G-list-02.expected` = `{exactFile:"E.5.json", exactPointer:"/expected/3", crossPhaseConflict:false}` —— **确为文件/指针定位，不是完整 DTO 比较器**；`cases.json` 中 G-list-02 步骤为 `run-scenario capacity 3`，课程 scenario 任务实际使用 G-list-01/06（已展开的完整 round 对象）。A-10 的 `externalInputRequired` 明确写"T08 批准的完整指定版本 Agent 评估集及真实模型服务；固定三个负例仅作子集" —— 声明诚实，缺口真实 |
| PARENT-03 | 跨窗口/重开/跨 attempt 辅助不可洗需真实账本 | **保留**。renderer 的 `acknowledged`/`currentFloor` 是**一次性内存投影**（组件注释自述 "Monotonic, disposable view floor. The owning store still decides durable provenance."），无本地持久化（已静态核实 renderer learning 目录**无** localStorage/sessionStorage/fs/ipc）；T01/T08 受信持久来源未接，**renderer floor 不是权威账本** |

### 9.2 本轮仍未闭的父功能与发布门（逐项，均不因本结论关闭）

- T02–T07 真实领域执行器与阶段证据（解析/查询/验证/推理/行为/轮次适配）；G.5/G.6 跨模块适配。
- T00 批准命名的业务 bridge、App 路由与 IPC 契约；S1 页面**无正式产品入口**（`learning-ui-contract.md:3`："尚无正式产品路由"）。
- T01 durable 学习记录与跨 attempt 辅助账本、产品案例生命周期与创建/确认路径。
- 课程与 fixture **入包**（`scripts/build-engine.mjs` 等实际资源入口尚未绑定 content/learning 与 fixture；仓库根读取不等于包内资源）。
- T08 真实完整代做来源与完整指定评估集；T10 实际 HTML/项目包导出与项目包校验。
- 至少 5 名真实新手、80% 原口径的真人验收（`user-acceptance.md` 为**空记录**，未造样本、未对外招募）。
- Windows / macOS 双平台与实际 Electron 原生验收；本轮**未**运行 Electron/e2e/native/HMR/可见浏览器/产品窗口。
- CI、远端核验、push/PR/merge 与发布；57 项原 P0 门。
- 本轮 replacement-r1 前一组创建过程失败（一方实际执行了被禁的 `agent list(include_primary=true)` 与对用户级 global config 的 `grep permissionMode`，该侧 turn 正式 `aborted`，曝光范围 UNKNOWN）—— **本轮不得把前组当作已有双审通过**。

---

## 10. 证据强度分列

| 类别 | 本轮状态 | 依据 |
| --- | --- | --- |
| 静态（逐文件阅读） | **已覆盖**：32 产品源/数据路径 + 55 文件全 diff + d969 全部流程原件 | §4 |
| 固定输入完整性（SHA/字节/原文覆盖） | **已覆盖，本方独立复算**：106/106 manifest 条目、17/17 fixture、PRD SHA、50 条 coverage 原文（`verify()` 运行期校验通过）、base/product tree | `raw/manifest-verification.json`、verify 运行 |
| 纯逻辑（reducer / 投影） | **已覆盖，本方实际运行**：18 项 vitest 纯投影 + 42 项 pytest（含 reducer 全部负例） | `raw/learning-vitest-unit.stdout.txt`、`raw/learning-pytest-suite.stdout.txt` |
| I04 真实基础设施 | **已覆盖，本方实际运行**：7 项真实通道（rollback 预览 / stdio coordinator / 隔离 worker / test.atomic 提交 / 收据 / result.page / SQLite 重开 / 依赖向量）+ 3 项负例 | 同上，42 项内 |
| headless 组件 | **本轮未独立重跑**（环境未绑定 chromium 1248，按指令不重跑已知失败、不安装 runtime）；本方实际跑的是同目录的**纯投影文件**（`learning-presentation.test.ts`，18 passed），而 `learning-workspace.test.ts` 的 16 项浏览器用例在本轮确为 **skip（16 skipped）而非 pass**；该子项的通过结论**依赖 d969 固定同候选证据**，其覆盖的 7 个源码 SHA 与 manifest SHA 已由本方逐条核对与受审字节一致，且 `ui-browser-install`（真实 Chromium 下载记录）、`ui-third-vitest`（68.42s 真实浏览器执行时长）、`npm-check-ui-first`（ESLint 扫到下载的浏览器 `content.js`）等归档旁证互相印证该套件**确实执行过**而非跳过 | §5.4、`raw/archive-expansion.json` |
| 领域（真实产品领域执行） | **未执行**（T02–T07 未就绪；合成 adapter 只测 reducer，模块自述已声明） | `test_learning_service.py:1` |
| package / native / 双平台 | **未执行**（无依赖/锁/打包改动，S1 不触发 package 触发） | §9.2 |
| 真人 | **未执行**（空记录） | `user-acceptance.md` |
| 生产 | **未执行**（未推送、未建 PR、未合并、未上线） | §9.2 |

---

## 11. 本方新增产物与未验边界

### 11.1 新增产物（仅本方写面）

- 报告：`docs/reviews/T09/replacement-r1/minimax-m31flash.md`（本文件）。
- raw（27 文件）：`docs/reviews/T09/replacement-r1-runtime/minimax/raw/`
  - `manifest-verification.json`（54771 B，SHA `0dc746749a6c39bd879bcefa066b73c5280864101796d27da057aba8d82790a2`）
  - `probe-fixtures.json`（11856 B，SHA `07b8c0d5f6ace854c09aef81424db13b522276d8c2d42ecc3a37d32440858098`）
  - `archive-expansion.json`（9699 B，SHA `d5c9490f50c0b1f1ae65212a4b04f4630d2d0ab6125d894aab8237d39757ea22`）+ 12 份解压首败原文
  - `run-receipt.json`（6065 B，SHA `9e15046fdbe959300aa28b7e1a923d460c365bfb6232659db067c3d409ef86d4`）+ 8 份 stdout/stderr 原件
  - `verify-product-baselines.stdout.txt`（SHA `e3cf790a…58fb`，与归档 `baseline-verification.json` 逐字节相同）
- scratch（4 个本方探针脚本 + 运行器 + pytest/node 临时目录，均在本方 scratch 内）。

**未删除任何旧文件或失败原件，未新增 ignore，未修改产品/测试/配置/依赖/锁，未提交、未推送、未切分支、未合并。**

### 11.2 未验 / 不采信边界

- 未运行 Electron / e2e / native / HMR / 可见浏览器 / 产品窗口 / 真实领域 producer / 任何外部 API、付费、密钥读取；未创建或操作 GUI；未与另一方通信或互传意见。
- 未重跑已知缺 1248 的 headless 浏览器失败；未做浏览器缓存盘点；未安装 runtime。
- 未复现 d969 的完整 `npm run check`（664/1094 全量）——该全量结论由本方**读取原件并逐项核对**（`npm-check-ui-final.txt` 的 lint/typecheck/vitest 664/ruff/pytest 1094 各段实际读出），本方只重跑了与本轮具体疑点对应的最小充分集合（verify / reset / 学习 pytest / 学习 vitest），未做无变化重测。
- 合成 adapter（`SyntheticTools`）复制 `expected` 只证明 reducer 行为，**不证明任何领域执行**；本报告未将其计入领域通过。
- `test.atomic` 内部 `prepare_plan` 的确认元数据**不是人类点击确认**；`product-mode` 下该能力按预期被 `UNSUPPORTED_CAPABILITY` 拒绝。
- sandbox 证据仅支持 `chromiumSandbox:true` 配置与成功，**未**采当次 argv/OS sandbox 状态与浏览器二进制 hash，不外推原生平台隔离。

---

## 12. 终态与自述

- 本方任务已运行至终态：完整读取本轮首输入（75943 B / SHA-256 `18fbcbe32a1dd353e36c63a311db31f7257e2b0ef2ad538dc2084880ec47fe1b`，与应用附件逐字节一致）→ 完成 base→product 全区间与 d969 全流程原件的独立审查 → 完成 4 项授权运行的真实退出码取证 → 完成 13 旧问题 / 3 P3 延期 / 3 PARENT 的独立重判 → 完整报告落盘于本方约定路径。
- 报告路径：`docs/reviews/T09/replacement-r1/minimax-m31flash.md`。报告文件自身的 SHA-256 与字节数由总控/owner 在收件路线实际读取绑定（**本方不自行签发终态哈希回执**）。
- 源码零漂移已复核（§3.4）：HEAD 仍为 `72aa83a80a973a3edeb62ed95518bf1a22178985`，产品/测试/配置/依赖/锁无差异，`AGENTS.md` 保持未暂存 M 且未被本方 stage 或还原。
- 本报告**不**授权 push / PR / merge / CI / 发布；同版双方明确通过、全部意见有处置、实际待推内容一致之后，仍由开发线按总控 lease 决定，且原 CI、远端核验与 57 项 P0 父门全部保留。

---

### 附：本轮原始运行与探针文件清单（SHA-256）

| 文件 | 字节 | SHA-256 |
| --- | --- | --- |
| `raw/manifest-verification.json` | 54771 | `0dc746749a6c39bd879bcefa066b73c5280864101796d27da057aba8d82790a2` |
| `raw/probe-fixtures.json` | 11856 | `07b8c0d5f6ace854c09aef81424db13b522276d8c2d42ecc3a37d32440858098` |
| `raw/archive-expansion.json` | 9699 | `d5c9490f50c0b1f1ae65212a4b04f4630d2d0ab6125d894aab8237d39757ea22` |
| `raw/run-receipt.json` | 6065 | `9e15046fdbe959300aa28b7e1a923d460c365bfb6232659db067c3d409ef86d4` |
| `raw/verify-product-baselines.stdout.txt` | 876 | `e3cf790a4e1f3cdb3616a8690d106cea59998f4260733535d93c1ec3551758fb` |
| `raw/verify-product-baselines-reset-G-base.stdout.txt` | 8227 | `dbae89cc1ba9df375a65eb4cb92ce314e181d5dfe65e7755ccb1796a88813a69` |
| `raw/learning-pytest-suite.stdout.txt` | 99 | `ab91cd9f96ad7a6e39c85485bd8976742833d132c24453cb05a69345d1cd7c28` |
| `raw/learning-vitest-unit.stdout.txt` | 270 | `2b1c34cf069aa442224b734c0ac65284a5345aae633c63d4565201d9ce9a1f07` |
| `raw/archive-jobstore-first-pytest.txt` | 15311 | `0ca0a58e9530c0b2ac1f7015007517ff020921286077cc07ce4954a0f7da3358` |
| 其余 11 份解压首败原文 | — | 见 `raw/archive-expansion.json` 逐条登记，均与证据登记的原始 raw SHA/字节吻合 |
