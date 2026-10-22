# T04-S1 独立完整审查报告：MiniMax M3.1-Flash

- 报告路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89/docs/reviews/T04/round-1/minimax-m31flash.md`（本方唯一报告）
- 审查对象：T04-S1 完整独立查询编写与批准读取客户端
- 固定 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 固定 product：`554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`
- 本方 review HEAD：`9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1`（detached，无开发分支）
- 实际 cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89`
- 结论（仅适用于本固定版本的完整 S1 范围）：**通过**

结论先行：本方已完整实读本轮全部输入（496 行，逐行读完，无截断），独立复现完整 diff 与全部 33 项来源，独立重跑允许范围内的普通验证并全部 exit 0，独立复核 R1-01/R1-02/R5-01..04/R6-01/同版本终态/同数量错义反例/总控归档 R1 共 11 项历史结论，逐项独立核对源码后确认关闭。发现 **3 项 P3 低严重度问题**（均为新发现，不在既有内审范围），均不构成 S1 阻断。**完整 T04 父功能未完成**，本报告不构成父功能验收，也不代判另一指定审者、不授权 push/PR/merge。

---

## 1. 实际任务来源、ID、时间与逐任务设置读回

### 1.1 附件完整性与实读

| 项 | 值 | 核验方式 |
| --- | --- | --- |
| 附件路径 | `/Users/kyle/.minimax/v2/assets/2026/10/22/23-49-04-187-asset_20261022-234904-187_94be45ae7e59_58bb1567-pasted-text.txt` | 用户随本轮提供 |
| 字节数 | `83104` | `wc -c`，与操作者声明一致 |
| 行数 | `496`（末尾另有空行） | `wc -l`，与操作者声明一致 |
| SHA-256 | `94be45ae7e598a57ad63a0e53521c6ca13d9c76be3028cd7941dea81e0c9921a` | `shasum -a 256`，与操作者声明逐字符一致 |
| 实读情况 | **完整读取 496 行，分 4 段（1–130、128–257、258–387、368–496）逐行读完，末尾附录 `<!-- END DIFF OPERATION NOTE ORIGINAL BYTES -->` 已读到** | 读取工具曾两次返回截断提示，本方按同一路径继续分段读取直至末尾，无跳读、无摘要替代 |

交叉一致性：本方工作树内 `test-results/t04-review-runtime/minimax/metadata/submitted-body.txt` 为 83104 字节、SHA-256 `94be45ae7e598a57ad63a0e53521c6ca13d9c76be3028cd7941dea81e0c9921a`，与附件**逐字节相同**，证明附件确为本方投递正文，未被替换或截断。

### 1.2 实际 task ID —— 无法验证（不假填）

三份互相独立的记录一致显示**不存在可用 task ID**：

| 来源 | 字段 | 值 |
| --- | --- | --- |
| `test-results/t04-review-runtime/minimax/metadata/owner-task-settings.json` | `taskId` | `null` |
| 同上 | `taskCreated` / `bodySubmitted` / `fullReadAccepted` | `false` / `false` / `false` |
| `.../metadata/submission-input.json` | `taskId` / `taskCreated` / `bodySubmitted` | `null` / `false` / `false` |
| `docs/reviews/T04/round-1/launch-20261022/mapping-minimax.json` | `actualTaskId` / `actualTaskSettingsReadback` | `null` / `null` |
| `.../launch-20261022/delivery-manifest-minimax.json` | `actualTaskId` / `actualSettingsReadback` | `null` / `null` |

**实际 task ID：无法验证。** 本方不拥有、也不允许自行推断该 ID，不自填、不伪造。本报告的"任务来源"只能如实记为：操作者通过 owner CUA 在 MiniMax Code 新建任务并投递本附件，本会话即为接收该正文并执行审查的实际任务实例；其平台侧任务标识符对本方不可读。

### 1.3 逐任务模型 / 思考 / 权限 / 路径 —— 读回来源与读回限度

唯一允许的设置收据是 `test-results/t04-review-runtime/minimax/metadata/owner-task-settings.json`（873 字节，本方最小设置收据）：

```json
{
  "observedAt": "2026-10-22T15:48:15.632480+00:00",
  "source": "owner CUA actual own new task composer and native directory picker readback",
  "phase": "draft-settings-observed-before-submit",
  "cwd": "/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-554ec89",
  "reviewHead": "9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1",
  "model": "M3.1-Flash（订阅限免）",
  "thinking": "xhigh",
  "permission": "始终授权",
  "permissionInterpretation": "bypassPermissions",
  "settingsActuallyObservedForThisDraft": true,
  "globalConfigOrOtherTaskEvidenceUsed": false
}
```

- **模型**：M3.1-Flash（订阅限免）。与本会话实际运行模型标识 `MiniMax-M3.1-Flash` 一致。✅
- **思考等级**：xhigh（来源为上收据的 composer 读回；运行期无第二读回途径）。✅（来源单一）
- **权限**：`始终授权` / `bypassPermissions`。✅（来源单一）
- **工作目录**：收据所记绝对路径与本方实测 `pwd` **逐字符相同**；本方实测 `git rev-parse HEAD` = `9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1`，与收据 `reviewHead` 相同。✅
- **收据限度（必须如实说明）**：该收据 `phase` 为 `draft-settings-observed-before-submit`，`settingsActuallyObservedForThisDraft: true`，即它是**本任务合成器与原生目录选择器在提交前的实际读回**，不是"已创建任务在运行期的读回"；同时 `taskCreated/bodySubmitted/fullReadAccepted` 均为 `false`。因此：设置三要素有来源可信的读回，**但运行期思考等级/权限模式本会话内无独立读回途径**，只能引用该收据，不得声称已二次确认。
- **未读取的来源**（按本轮要求主动规避）：全局身份配置（`~/.minimax/config.yaml`、`~/.zcode/cli/config.json` 等）、其他会话日志、以及**另一指定审者本轮材料**（`docs/reviews/T04/round-1/zcode-glm53-input.md` 全程未打开，仅在目录列举中见到文件名）。
- **正文接收时间**：附件于 2026-10-22 23:49:04（+0800）投递本会话；设置收据观测时间 2026-10-22T15:48:15Z（= 23:48:15 +0800），早于正文投递约 1 分钟，与"先读回设置、后提交正文"顺序一致。

---

## 2. 身份核验：diff、33 项来源、映射 hash、冻结一致性

### 2.1 完整 product diff 独立复现

| 项 | 声明值 | 本方实测 | 结果 |
| --- | --- | --- | --- |
| `git diff --abbrev=7 5f910b5… 554ec89…` | 170428 字节 / SHA-256 `777ef6d58b8697530024ad4c47110443b613b9ba7de37d8420fae97e44b6c651` | 170428 字节 / `777ef6d58b8697530024ad4c47110443b613b9ba7de37d8420fae97e44b6c651` | ✅ 完全一致 |
| 变更路径数 | 33（全部新增 `A`） | 33（全部 `A`） | ✅ |
| base→product 关系 | — | `git merge-base --is-ancestor` 成立，product 为 base 后代 | ✅ |
| product 提交 | — | `554ec898…`（"test: reject equal-count query semantic counterexample"，2026-10-21） | ✅ |

原件：`test-results/t04-review-runtime/minimax/raw/product-diff-abbrev7.txt`（170428 字节，SHA `777ef6d58b869753…`）、`product-diff-name-status.txt`。
附录所述 `--abbrev=7` 与默认 8 位只影响 diff 内 `index` 行对象名缩写，**不影响任何 blob 字节**；本方以 blob 逐项复核证实（见 2.2），不存在源码漂移。

### 2.2 全部 33 项来源逐项核验

对 `mapping-minimax.json` 的 `all33ProductInputs` 全部 33 条，用 `git show 554ec898…:<path>` 直接取固定 product 的 Git blob，逐条比对字节数与 SHA-256：

**33/33 全部一致，0 项不符**（明细：`test-results/t04-review-runtime/minimax/raw/blob-verification.txt`）。同时取得 33 项固定 Git blob object id，可供后续按 blob 精确追溯。

### 2.3 本方工作树物理文件 vs product 原字节

`test-results/t04-review-runtime/minimax/raw/physical-vs-product.txt`：

- 32 项（源码、测试、fixture、SSR 探针、文档、证据）**物理文件与 product blob 完全相同**；
- 唯一差异：`docs/reviews/T04/status.md`（物理 8413 字节 / `59e85856…`，product 原字节 5541 字节 / `237f2343…`）。这与 `mapping-minimax.json` 的 `physicalProductManifestDifferences: ["docs/reviews/T04/status.md"]` 声明一致，且属**追加流程状态**，非源码漂移。**判定为符合预期，不构成源码变化**。

### 2.4 审查前后冻结一致性（本方未改任何受审内容）

| 检查 | 审查前 | 审查后 | 结果 |
| --- | --- | --- | --- |
| `git rev-parse HEAD` | `9a4dfc8f1e9106a4c05423f80a26e9e88eb0aaa1` | 同左 | ✅ 未变 |
| `git status --porcelain` | ` M AGENTS.md` + 两个 untracked 过程目录 | 完全相同 | ✅ 未变 |
| 保护 `AGENTS.md` SHA-256 | `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 同左 | ✅ 未覆盖、未格式化、未提交 |
| `package-lock.json` SHA-256 | `a462ba7092588c325829e0b05bbcb1a0fa97e6914307b84d97103875b3c29bb5` | 同左 | ✅ 未变 |
| `uv.lock` SHA-256 | `d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e` | 同左 | ✅ 未变 |
| product blob 抽查（QueryPage.tsx） | `984eeeb985a6d47a…` | 同左 | ✅ 未变 |

本方全部写入仅限：唯一报告文件，以及 `test-results/t04-review-runtime/minimax/`（ignored 独占运行目录）下的反例、raw 与收据。**未执行任何 `git add/commit/push/reset/checkout`，未修改源码、测试、配置、锁、验收或他人报告。**

### 2.5 其他输入与来源 hash

| 输入 | 声明 SHA-256 | 本方核验 | 结果 |
| --- | --- | --- | --- |
| 完整正文原件 `full-minimax-input.md` | `3b3e5cbba17731fb8d89b1df352fdc78b03c3e1f18eab6c29f37fd577f2586bc`（78555 B） | 读入并与附件正文段一致 | ✅ |
| 本轮提示映射 `mapping-minimax.json` | `7c888742658aab32fe257c234597ee0615dcd7eff3ca804e37af167457a47bd5`（9069 B） | 已读全文 | ✅ |
| `setup-minimax.json` | `07608bc9d6c57b2d83b64df8fa5faf7fcba35ec4e739de9078c4d53931fa2d10`（2364 B） | 已读全文 | ✅ |
| `current-execution-supplement.md` | `a6cf1335042a6e25d4ab0f67b27978c346c13cd82e59f355d302e1ec80681d3e`（6215 B） | 已读全文 | ✅ |
| 旧冻结提示 `minimax-m31flash-input.md` | `9873b3f6797d72937fd2da25c204b9aaf57f8c53ccdefc0e7b75b0097dd5ca9a`（20651 B） | 未修改 | ✅ |
| 旧包 manifest `frozen-input-manifest.json` | `804ce95a0bbded75895fd18d19d7c33981e106abe961581615cc6f6179ba446c`（11937 B） | 未修改 | ✅ |
| 批准 base PRD | `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` | base 与 product 处实测同值，**product 未改 PRD** | ✅ |
| T09 固定输入 manifest | `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e` | 由 `test_query_service_approved_baseline.py` 每次重算核对 | ✅ |

### 2.6 原始证据归档独立复核（总控 R1 项）

`docs/reviews/T04/evidence/raw-logs-554ec89.tar.gz`（6081 字节，声明 SHA `c17c2595d79900c539e4a0aa61bc1ad012e058af9e666282aa9c1f6079064865`）：

- 归档 SHA-256 实测与声明一致；tar 成员名集合与 index `members` 完全一致；
- **37/37 成员逐一重算字节数与 SHA-256，全部一致**，原始总字节 61602 与 index `rawBytes` 相符。

明细：`test-results/t04-review-runtime/minimax/raw/archive-verification.txt`。**总控 R1"原件可恢复性"项由本方独立验证成立，非仅凭索引自述。**

---

## 3. 实际审查范围（已读源码清单）

本方**逐文件通读**下列 33 项 product 内容（非摘要、非 manifest 自述）：

**实现（6）**：`packages/engine/src/ontolearn_engine/query_service/__init__.py`、`.../drafts.py`；`apps/desktop/src/renderer/src/query/draft.ts`、`results.ts`、`reader.ts`、`QueryPage.tsx`、`query.css`
**测试（5）**：`packages/engine/tests/test_query_service_authoring.py`、`test_query_service_approved_baseline.py`；`tests/unit/t04-query-authoring.test.ts`、`t04-query-results.test.ts`、`t04-query-reader.test.ts`
**Fixture（6）**：`tests/fixtures/query/authoring-case.json`；`tests/fixtures/query/approved-baseline/{G-base.json,conventions.json,manifest.json,provenance.json,unclosed-high.rq}`
**探针（1）**：`docs/iterations/T04/ssr-probe.mjs`
**文档（9）**：`docs/iterations/T04/{acceptance.md,integration-handoff.md,reader-integration.md}`；`docs/reviews/T04/{internal-candidate.md,internal-review-1..7.md,status.md}`；`docs/reviews/T04/evidence/{final-verification.json,verification-summary.json}`
**流程原件（本方补充读取）**：`docs/reviews/T04/internal-review-8.md`、`docs/reviews/T04/round-1/{review-inputs.md,verification-and-history-index.md}`、`docs/reviews/T04/evidence/{reader-service-verification.json,service-candidate-554ec89.json,raw-logs-554ec89.index.json}`、`docs/iterations/T04/service-stage.md`、`docs/reviews/T04/round-1/launch-20261022/{mapping-minimax.json,delivery-manifest-minimax.json,setup-minimax.json,entrypoint-static-proof.json,root-registration.txt}`、`test-results/t04-review-runtime/minimax/metadata/{owner-task-settings.json,submission-input.json}`

**父需求依据（实读）**：批准 base PRD `docs/prd/PRD-本体学习与落地Agent工作台.md` 的 FR-006（数据层次与结果失效）、FR-400（多种查询入口）、FR-401（查询透明性与数据范围）、FR-402（本地只读与网络限制）、FR-403（结果与空结果解释）、FR-404（查询保存与复用）、附录 C（MVP 能力矩阵，含 SPARQL `SELECT`/`ASK` 仅项目内只读、`CONSTRUCT`/`DESCRIBE`/更新/远程联邦不属于 P0）、附录 G（Q-01、Q-02、O-01 原文预期）。PRD 在 base 与 product 处 SHA 相同，未被本产品改动。

**架构不变量专项核对（静态）**：
- 共享路径零改动 —— product diff 的 33 项**全部为新增**，未触及 `csp.ts`、`preload/`、`main/`、`packages/contracts/`、`package.json`、两份锁文件（`git diff --name-only` 按上述路径过滤为空）。✅
- 渲染端隔离 —— 新增 renderer 文件无 `node:`/`require`/`process.`/`fetch`/`localStorage`/`window.`/`indexedDB`；其唯一外部依赖 `packages/contracts/src` 亦无 Node 内建导入。✅
- 无第二可变源、无执行器、无 Store 写入、无通用 `invoke(method, params)` 通道；reader 只复用批准 `DesktopBridge` 的 `getResult`/`getResultPage`/`getJob`/`cancelJob`。✅
- 无新增依赖；SSR 探针仅用仓库已锁定的 `typescript` 与 `react-dom/server`。✅
- `staleReason` 只读自批准 result schema，不由 UI 自行推断；错误只出固定错误码与 `params.field`。✅

---

## 4. 本方实际运行的验证（完整 argv、cwd、起止、真实 exit、raw 与 hash）

环境隔离（每条命令均设）：`npm_config_cache=<runtime>/cache/npm`、`UV_CACHE_DIR=<runtime>/cache/uv`、`TMPDIR=<runtime>/tmp`，runtime = `test-results/t04-review-runtime/minimax`。cwd 均为本方 review 树。

| # | argv | 起止（UTC） | exit | 结果 / raw |
| --- | --- | --- | --- | --- |
| 1 | `git diff --abbrev=7 5f910b5… 554ec89…` | 15:48–15:49 | 0 | 170428 B，SHA `777ef6d5…`；raw `raw/product-diff-abbrev7.txt` |
| 2 | `git show <product>:<path>` ×33 + SHA-256 比对 | 15:49–15:50 | 0 | 33/33 一致；raw `raw/blob-verification.txt` |
| 3 | `python3` 物理文件 vs product blob 比对 | 15:50 | 0 | 32 同、1 差异（status.md，已声明）；raw `raw/physical-vs-product.txt` |
| 4 | `python3` 归档 37 成员逐一校验 | 15:55 | 0 | 37/37 一致；raw `raw/archive-verification.txt` |
| 5 | `npx vitest run tests/unit/t04-query-authoring.test.ts tests/unit/t04-query-results.test.ts tests/unit/t04-query-reader.test.ts` | 15:53:08 → 15:53:10 | **0** | **Test Files 3 passed / Tests 36 passed**；raw `raw/vitest-t04-targeted.log`（246 B） |
| 6 | `uv run --frozen pytest packages/engine/tests/test_query_service_authoring.py packages/engine/tests/test_query_service_approved_baseline.py -q` | 15:53:10 → 15:53:12 | **0** | **31 passed in 0.42s**；raw `raw/pytest-t04-targeted.log`（99 B） |
| 7 | `node docs/iterations/T04/ssr-probe.mjs` | 15:53:16 → 15:53:17 | **0** | `passed:true`，**14 项检查**全过；raw `raw/ssr-probe.log`（423 B，SHA `f730e85970c4fff87784f8d377da18f50da85de9487a4a0080fedc38a0f80874`）—— 与归档 `raw/reader-ssr-first.log` **逐字节相同**，独立复现成立 |
| 8 | `npm run check`（lint → format:check → typecheck(contracts/unit/desktop) → vitest → build → engine:check） | 15:53:17 → 15:54:34 | **0** | **TS 18 文件 / 666 项通过**；3 段 build 成功（✓ built in 49/24/85 ms）；ruff check + ruff format --check 通过；**pytest 1083 passed in 55.36s**；raw `raw/npm-run-check.log`（5317 B） |
| 9 | `uv run --frozen python <py-probe>` / `node <ts-probe>` / `node <csv-probe>`（本方反例，见 §6） | 15:56–15:59 | 0 | 见 §6 逐项 |

**本方独立复现与既有终态的吻合度**：`npm run check` 实测 TS 18/666、Python 1083，与 `reader-service-verification.json` 所记固定 554 终态**完全一致**；本方**未**采用旧的 640/642 TS 汇总或旧 SSR 8/11 作为最终数据。

**首失败与后继验证**：本轮**没有出现首失败**（全部首跑即 exit 0）。既有首失败原件（`check-first.log` 正则 lint、`check-second/third.log` 类型失败、`check-fourth.log` import 排序、`ssr-first.log` 误用未安装 esbuild、`reader-vitest-error-shape.log` 错误分类）均在本方已验证的 37 成员无损归档中，本方逐成员重算哈希确认其字节真实存在，未改写、未删除、未以失败后筛绿冒充通过。

**明确未执行（本轮不扩大）**：`npm run dev`、HMR、`npm run test:e2e`（Electron）、`npm run package:dir`、产物启动、任何新 native/caller/producer、任何真实 query.execute、真实 Store 写入、App 挂载、浏览器交互、下载、CSP/平台/真人验收。理由与授权边界见本轮执行补充；这些项目**未以静态或合成证据代替**。

---

## 5. 历史项逐项独立复核（11 项）

本方**不采信**开发者"已 closed"的表述；以下每项均在固定 product 源码上独立定位实现并核对调用路径后给出结论。

| 项 | 原问题 | 本方独立复核结论 | 依据（实际文件:行） |
| --- | --- | --- | --- |
| **R1-01** | 复用保存丢失 definitionId；新建保存不返回真实 ID | **已关闭** ✅ 私有 `savedQuerySchema` 携 `definitionId` 且 strict；载入保留身份（`QueryPage.tsx:545-551`）；保存回调必须返回真实持久 ID 并经 `definitionIdSchema` 校验（`draft.ts:142`、`QueryPage.tsx:498`）；更新时 ID 必须一致否则抛错（`QueryPage.tsx:501-502`）；迟到响应以 `request` token + `documentGeneration` 双闸拒绝（`QueryPage.tsx:496,503-507`）；同名不同定义以不同 `definitionId` 区分（`draft.ts:142-149`，`t04-query-authoring.test.ts:87-102`） |
| **R1-02** | 同项目非 query 任务被显示并可取消 | **已关闭** ✅ `queryJob` 复用批准 `validateV2('job')` 并限定同项目 + `capability === 'query.execute'`，否则返回 `undefined`（`results.ts:101-113`）；页面据其结果决定是否渲染任务区/取消入口（`QueryPage.tsx:145,148,585`）；不同 jobId 的结果持续标注"此前查询结果"（`QueryPage.tsx:613-615`）；失败说明走受限 `explainError`，不回传原始异常（`QueryPage.tsx:146,577-584`；`task-presentation.ts:11-51`） |
| **R5-01** | ACK 后重读未完成即释放 cancelBusy，重复取消 | **已关闭** ✅ `cancel()` 以 `return await this.refreshJob(jobId)` 覆盖 ACK 后重读全生命周期（`reader.ts:418`），`cancelBusy` 仅在 `finally` 且 `current()` 成立时释放（`reader.ts:422-424`）；重复 cancel 被 `cancelBusy` 与 token 双重拒绝（`reader.ts:360-361`） |
| **R5-02** | 空页丢失最后非空排序锚，10→空→5 被接纳 | **已关闭** ✅ 仅在 `page.rows.at(-1)` 存在时更新锚点，空页保留旧锚（`reader.ts:303-304`）；跨页回退被拒（`reader.ts:294-302`）；新读/新绑定/释放清理锚点（`reader.ts:209,116,434`） |
| **R5-03** | ACK 版本下限在后续刷新/通知/取消前查丢失 | **已关闭** ✅ `cancelFloor` 私有保存 ACK 版本下限（`reader.ts:79,412-415`），`minimumJobVersion()` 供刷新（`reader.ts:338`）、通知（`reader.ts:167`）、取消前查（`reader.ts:384`）共用；切 job/新绑定正确清理（`reader.ts:346,118`） |
| **R5-04** | `trim` 改写实际执行 SPARQL 原文 | **已关闭** ✅ `executedSparql` 仅用 trim 做非空判定，保留原字符串（`reader.ts:37-38,275`）；`presentationSchema` 另校验 ≤65536；页面展示实际执行文本而非编辑器文本（`QueryPage.tsx:128-131,619`） |
| **R6-01** | `INVALID_REQUEST` 用 `params={}`，降级为 internal | **已关闭** ✅ `invalid(field)` 只取批准枚举 `identity|params|cursor` 并写入 `params.field`（`reader.ts:57-63`）；元数据/分页失败分别归 `identity`/`cursor`（`reader.ts:260,266,292,302`）；原始 bridge 异常固定 `INTERNAL_ERROR`（`reader.ts:317-319,350-353,419-421`），无原异常外泄（测试断言 `PRIVATE_PATH` 不出现在快照，`t04-query-reader.test.ts:257-269`） |
| **同版本终态边界** | 同版本状态矛盾、已观察终态重开须拒绝；不得拒绝合法跳跃观测 | **已关闭** ✅ `compatibleJob()` 允许版本跳跃，但同版本异状态与终态再开均拒（`reader.ts:177-186`）；本方核对未使用"相邻状态转换"约束，排除对合法跳跃观测的误拒 |
| **同数量错义反例** | 正确 A01 与错误 A02 行数相同，必须比对完整答案 | **已关闭** ✅ `test_query_service_approved_baseline.py:86-95` 显式构造 Closed/High 有效查询得 A02，与正确 A01 行数相同但集合不同，断言 `wrong_rows != correct_rows`；本方实跑 31 项 pytest 通过。**未使用 expected 预填 Store**，每次从实际 ontology/facts 独立还原 G-base（`:28-35`） |
| **总控 R1 原件可恢复性** | 37 份 raw 仅 ignored，需无损归档 | **已关闭** ✅ 本方独立解压并逐成员重算哈希：37/37 一致、61602 字节相符（见 §2.6） |
| **T09 固定输入 provenance** | 17 项与 PRD 来源 hash | **部分可核，其余仅记录** ⚠️ manifest 与 provenance 的 17 项哈希、来源 commit `873c8c05…`、PRD SHA 记录完整且被测试每次重算；本方工作树内**仅 3 个被实际消费的副本**（G-base/conventions/unclosed-high）可逐字节复核（均与 manifest 对应条目相符）；**其余 14 项原始文件不在本工作树**（`tests/fixtures/product-baselines/` 不存在），本方无法独立重算其字节 → 仅能确认"记录完整且未被改写"，不能确认"原始 17 项本方逐字节复验"。此项**不影响 S1 判定**（未被消费），但正式 Q-01/02 联验时须在拥有原件的环境补齐 |

---

## 6. 本方发现的问题

以下 3 项均为本方**新发现**，不在既有内审 1–8 覆盖范围内。严重度按对 S1 范围与父功能的影响评定。

### F-1（P3／低）Python 与 TypeScript 草稿长度边界判定口径不一致

- **位置**：`packages/engine/src/ontolearn_engine/query_service/drafts.py:116-117`（`_text(draft["name"], 128)` 先按**未去空白**原串判长，再 `.strip()`）对照 `apps/desktop/src/renderer/src/query/draft.ts:57,59`（`scalarText.trim().min(1).max(128)` 先 trim 再判长）。
- **触发**：同一原始草稿 `name` = 128 个字符 + 1 个空格（或 1 个空格 + 128 个字符）；`sparql` = 65536 字符 + 1 个空格同理。
- **实测证据**：本方用仓库锁定 TypeScript（与 `ssr-probe.mjs` 同一编译方式）分别执行两侧实现并逐例比对，**5 例判定分歧**：
  - `name_128_plus_space`、`name_space_plus_128`、`name_127_plus_2space`、`sparql_65536_plus_space`、`sparql_65535_plus_2space`
  - 结果一致为：Python 抛 `DraftError`，TypeScript **接受**并返回去空白后的值。
  其余 18 项草稿、18 项 RDF 项、3 项可视编译用例**全部一致**（RDF 序列化与可视编译跨语言逐字节相同）。证据：`test-results/t04-review-runtime/minimax/counterexamples/{py-results.json,ts-results.json,py-ts-comparison.txt}`。
- **影响（已核实，不夸大）**：当前接线中**不会出现跨边界失败** —— UI 在 `withDraft` 中先经 `draftSchema.parse` 得到去空白后的值再交给回调（`QueryPage.tsx:103-108`），其值必然 ≤ 边界，Python 侧接受。因此**无数据完整性或安全影响**，无未受控数据可穿过边界。
  真实风险是**口径不一致本身**：Python 侧 `validate_draft`/`save_intent` 是引擎侧权威校验入口，对"去空白后仍在界内"的原始草稿比 TS 更严；若日后出现不经过 TS schema 的调用方（引擎侧直接校验、或适配器从项目记录读回草稿再校验），同一输入会得到不同结论。
- **建议**：统一为同一口径（两侧都在 trim 之后测量，或都在原始串上测量并各自显式说明），并在 `test_query_service_authoring.py` 增补与 TS 同名用例的边界断言。

### F-2（P3／低）CSV 导出对负数数值单元格追加文本前缀，改变导出取值

- **位置**：`apps/desktop/src/renderer/src/query/results.ts:89-93`（`escape()`：先 `String(value)`，随后 `/^[\s]*[=+\-@]/u` 命中即前缀 `'`）。
- **触发**：结果页含负数数值单元格（如 `-5`）。
- **实测证据**：本方反例实测导出字节为 `"-5"` 之外的 `"'-5"`（完整输出 `'"c0","c1","c2","c3"\r\n"\'-5","3.5","0","42"\r\n'`），即导出文本含真实撇号前缀，数值单元格的**类型与原值不再可严格还原**（Excel 会把前导 `'` 当作文本标记而隐藏，原始 CSV 消费者则读到 `'-5`）。其余边界实测正常：公式串 `=SUM(1)`/`+1`/`-1`/`@SUM(A1)` 与前导空白公式均被加前缀；控制字符保留在引号内；引号双写、含逗号单元格安全；`null` → 空引号；201 行被批准 `page` schema 拒绝（200 行上限由**批准契约** `packages/contracts/v2/schema.json` 的 `rows.maxItems: 200` 强制，非本线自设）。证据：`test-results/t04-review-runtime/minimax/counterexamples/{csv-export-probe.mjs,csv-probe.out}`。
- **影响**：公式注入防护本身正确且必要（对字符串单元格有效），但对**数值**单元格属误伤：数值不可能是公式，却因此丢失数值类型。这是导出保真问题，不是安全绕过（防护未被削弱）。
- **建议**：把公式前缀仅施加于字符串单元格（数值/布尔直接输出其规范文本），或在导出说明中明确数值以文本形式导出。

### F-3（P3／低）可视构建器状态不随"新建查询"与"复用已保存查询"重置，可静默覆盖已载入的 SPARQL

- **位置**：`apps/desktop/src/renderer/src/query/QueryPage.tsx:60`（`visual` 状态初始化）、`531-539`（新建查询）、`541-555`（复用已保存查询）、`430`（"生成可见 SPARQL 草稿"按钮，始终可点）。
- **触发**：先在可视构建器选择对象类与返回字段 → 点击"复用已保存查询"载入 B → 再点击"生成可见 SPARQL 草稿"；或先构建后点"新建查询"再点同一按钮。
- **证据**：源码逐处核对 —— `setVisual` 的 11 处调用**全部**位于可视构建器自身的控件回调（`QueryPage.tsx:113,217,235,255,291,318,346,363,381,401,414`），**新建查询（531-539）与复用已保存查询（541-555）两处只重置 `draft` 与 `definitionId`，从不重置 `visual`**；而 `430` 的生成按钮无任何条件禁用，编译的是**上一次遗留的** `visual` 值。因此一次点击即可把 A 查询的对象/字段生成结果写入 B 的草稿 SPARQL。
- **影响**：**仅限编辑器内容**，不产生假执行、不产生假持久化：真正执行文本仍来自适配器的 `executedSparql` 并单独展示（`QueryPage.tsx:128-131,619`），保存仍需用户显式操作且身份闸门不受影响。但对用户是**静默的内容替换**，可能让人误以为"刚载入的查询内容被改坏"。附带一处相邻小问题：RDF 类型切换把 literal 文本原样搬作 IRI（`QueryPage.tsx:324-333`），生成的 IRI 通常不合法，只以通用提示"无法生成查询"呈现。
- **未覆盖说明**：S1 无 DOM 交互测试装置（`package.json` 无 jsdom/@testing-library，vitest 仅含 `tests/unit/**/*.test.ts`，SSR 探针为静态渲染），本方无法以交互测试复现，仅以源码逐处核对为依据。
- **建议**：在"新建查询"与"复用已保存查询"两处同步重置 `visual`（或按载入草稿反解重建），并让生成按钮在 `visual` 非法时给出可定位原因；如需正式覆盖，请由 T00/App 侧在具备交互装置后补测。

### 附：其余观察（不构成缺陷，未计入发现）

- `query.css:76-84` 的 `.query-check input`、`.query-condition` 未置于 `.query-workspace` 作用域内，属全局选择器，理论上可影响其他视图同名字素样式；当前仓库无同名元素，风险极低，可在父接线时随样式整理一并收敛。
- `results.ts:20` 将 `staleReason.code` 标注为 `string`，而批准 schema 的取值为固定枚举，属类型放宽而非放宽校验（运行时仍由 `validateV2('result')` 强制），不影响边界。
- `33` 项清单内的 `docs/reviews/T04/evidence/final-verification.json` 记录的是 **较早候选 `c4aa5f9c…`（TS 642/Python 1082/SSR 11）**，并非固定 554；固定 554 的终态依据在流程证据 `reader-service-verification.json`（TS 666/Python 1083/SSR 14）。两份文件都按原字节保留、未被改写为 554 的结果，符合"原件保留不改写"要求；但 33 项清单内文件不覆盖最终候选数值，阅读时须以 `reader-service-verification.json` 为准（`verification-and-history-index.md:24` 已作此说明，本方复核确认属实）。

---

## 7. 未验项与不能判断之处（单列，不以静态代替）

**本 S1 之外、真实父功能缺口（本报告不能证明）**：
真实 `query.execute` 与项目内只读执行；`SERVICE`/远程 `FROM`/更新/隐式外联的真实拒绝；真实 Q-01/Q-02 业务结果与完整答案验收；真实分页/游标发行与过期；真实取消与终态收敛；历史输入选择与历史结果恢复；T01 原子保存、preview/confirm/commit、对账、恢复、撤销、过期；T08 真实模型草稿与工具闭环；ASK 与真实 RDF 类型/执行文本元数据及局部关系图；O-01"未记录"语义的**真实**执行侧证据；App 挂载与端到端交互；T10 跨设备复用；Windows 11 x64 / macOS 15 arm64；真人验收；父 FR-400–404 全部条款与附录 C/D/G、第 11–12 节；全部父 P0 与跨模块门；发布门。

**本轮明确未执行的验证**：`npm run dev`、HMR（`I02_HMR=1` 探针，评审冻结期间禁跑）、`npm run test:e2e`、`npm run package:dir`、产物/浏览器/Electron 启动、任何新 native/caller/producer、真实凭据或原生提示。理由：本轮执行补充将其排除在普通 S1 验证运行面之外，且桌面/原生验收条件不得以隐藏窗口、禁 hang monitor 或 stub 代真实结果。

**不能判断之处**：
1. 平台侧**实际 task ID** 与**运行期**思考/权限读回不可得（§1.2、§1.3），只能引用提交前 composer 读回收据。
2. T09 17 项输入中**未被消费**的 14 项原始字节，本工作树内不存在，无法逐字节复验（§5 末行）。
3. 因 S1 无交互测试装置，F-3 的交互后果以源码核对为依据，未由运行证据复现。
4. 本方**未**复跑 `test:e2e`/`package:dir`/打包内样例，故"包内引擎验收"无本方证据。

---

## 8. 结论

**对固定版本（base `5f910b52…` → product `554ec898…`）的完整 T04-S1 范围：通过。**

依据：
1. 本轮全部输入（496 行 / 83104 B / SHA-256 `94be45ae…`）已逐行实读到底，无截断、无摘要替代，且与工作树内 `submitted-body.txt` 逐字节相同；
2. 完整 diff（170428 B / `777ef6d5…`）与全部 33 项 product blob（33/33 字节与 SHA 一致）均由本方独立复现，非采信 manifest 自述；
3. 允许范围内的普通验证全部首跑 exit 0：`npm run check` 实测 TS 18/666、Python 1083、SSR 14 项，与既有固定终态完全吻合；SSR 原始输出与归档最终日志**逐字节相同**；
4. 37 成员原始证据归档经本方逐成员重算哈希确认无损，总控 R1 独立成立；
5. R1-01、R1-02、R5-01、R5-02、R5-03、R5-04、R6-01、同版本终态边界、同数量错义反例、总控 R1 共 10 项历史结论，本方在固定 product 源码上逐条独立定位并确认关闭；T09 provenance 项为"记录完整、3/17 可逐字节复验、其余 14 项本方不可复验"，已单列且不影响 S1 判定；
6. 未发现假执行、假结果、第二可变源、共享文件越权、未批依赖或渲染端隔离违规；
7. 新发现 3 项均为 P3 低严重度（F-1 跨语言长度口径、F-2 CSV 数值取保真、F-3 可视状态未重置），影响面限定在编辑器/导出层，不阻断 S1，建议由唯一 owner 择机修复后按现行规则重验（若触及受审实现，须生成新候选并由双方重新完整审查，本结论不自动延续）。

**限制声明**：
- 本结论**仅适用于**上述固定同版本的完整 S1 范围，**不表示完整 T04 或产品验收通过**；父功能缺口见 §7。
- 本结论**不代判另一指定审者**（ZCode GLM-5.3 意见本方未读、未用），**不授权** push / PR attach / CI / 合并 / 远端核验 / 发布。
- 审查期间**未修改**任何源码、测试、配置、锁、验收或他人报告，未执行任何 Git 写操作；唯一写入为本报告与本方 ignored 运行目录产物。
- 实际 task ID 无可信来源，已标"无法验证"，未自填。

---

## 附：本方运行产物（ignored，均在本方独占目录）

- `test-results/t04-review-runtime/minimax/raw/`：`product-diff-abbrev7.txt`(170428 B)、`product-diff-name-status.txt`、`blob-verification.txt`、`physical-vs-product.txt`、`archive-verification.txt`、`vitest-t04-targeted.log`(246 B)、`pytest-t04-targeted.log`(99 B)、`ssr-probe.log`(423 B)、`npm-run-check.log`(5317 B)
- `test-results/t04-review-runtime/minimax/counterexamples/`：`py-authoring-probe.py`、`ts-authoring-probe.mjs`、`py-results.json`、`ts-results.json`、`py-ts-comparison.txt`、`csv-export-probe.mjs`、`csv-probe.out`
- `test-results/t04-review-runtime/minimax/metadata/owner-task-settings.json`（最小设置收据，本轮唯一设置来源）

反例仅写于本方 ignored 独占目录，未进入源目录或原测试目录，未改变任何验收真值，未构成第二执行器/Store/公共 schema。
