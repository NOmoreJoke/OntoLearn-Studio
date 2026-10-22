# T04-S1 修复候选 5070004：MiniMax M3.1-Flash 全新完整独立审查报告（Round 3）

- 报告路径（本方唯一报告）：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-r3-5070004/docs/reviews/T04/round-3/minimax-m31flash.md`
- 审查对象：T04-S1 完整范围（离线查询编写 + 批准读取客户端 + 本轮四 P3 修复）
- 批准共享基线 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`
- 固定产品 product：`5070004ec8e3219bea33960bd88f57f1976e9cf8`
- 本方实际 review HEAD：`5070004ec8e3219bea33960bd88f57f1976e9cf8`（detached，无开发分支）
- 实际 cwd：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-r3-5070004`

## 0. 结论（先行）

**本固定版本（base `5f910b52…` → product `5070004e…`）的完整 T04-S1 范围：通过。**

依据（本方独立取得，非采信任何既有结论）：

1. 本轮完整输入 **147 行 / 29715 B / SHA-256 `1985d7c54e0d…3f1c40`** 三项与操作者声明逐字符一致，已逐行读完 1–147，无跳读、无摘要替代。
2. 本方**完整复现** base→product binary diff（`256242` B，SHA-256 `27c090fc00cd6d1a851695551c2d5e4e9714d9845b9d5f3ee91ae51f9995b030`，42 个变更路径），并按 `product-manifest.json` 逐项核对 **42/42** 产品文件的 manifest ↔ 工作树 ↔ Git blob 三方一致，**0 项不符**。
3. 四项 P3（D1/D2/D3/D4）在本方**自写独立反例**下逐项复判为**已修复且通过**；D1 另以 Python/TypeScript 双语言各 40 例独立探针复现（**0 mismatch**）。
4. 历史意见 R1-01、R1-02、R5-01、R5-02、R5-03、R5-04、R6-01 及"同版本矛盾/已观察终态重开"、"同数量错义反例"、"总控 R1 原件可恢复性"共 **10 项**，本方在固定 product 源码上逐条独立定位并确认**已关闭**。
5. T09 provenance：完整 `approved-t09-provenance-inputs.tar.gz` **19/19** 项字节与 SHA-256 全部复算一致；产品实际消费的 4 个副本与归档原件**逐字节相同**；独立重建 G-base 后复现 **A01 唯一 / 改 Closed 后空集 / 故意错误 Closed-High 得 A02（同数量、异答案）** 三组完整答案。
6. 本轮实际执行的 3 条受控验证全部 exit 0：`npm run check`（TS 18 文件/719 项、Python 1167 项、lint/format/typecheck/build/ruff 全过）、静态 SSR **14 项**、真实组件 DOM **5/5** 情景（独立 Chrome 155.0.8059.85、headless、offline、0 请求、0 pageError）。
7. 未发现 P0/P1/P2 问题；本轮新发现 **1 项 P3**（TS 内部字符串长度计量口径不一致，方向为偏严，不越权、不泄露）＋ 3 项观察级记录。
8. 旧 554 轮的任何 Pass、上一 507 轮的任何 Pass、既有 8 份内审"通过"、既有两方外审结论，**均未被本报告采用为依据**；本报告不沿用旧结论，也不缩减为 delta。

**保留的真实边界**：本结论**仅适用于上述固定同版本的完整 S1 范围**。完整 T04 父功能、真实 `query.execute`、T01 事务保存、T08 真实模型、ASK/RDF term 元数据、App/T10、两 OS/真人、全部父 P0/跨模块与发布门**均未完成、未验证**。本报告**不代判另一指定审者**，**不授权** push / PR / CI / merge / 发布。

---

## 1. 任务身份、设置与证据来源

本节**只引用操作者在本方 `test-results/t04-review-runtime/minimax/operator/` 下的原始回执**；未读取、也未以任何方式推断全局配置、原生 session 数据库、其他 task/session/peer 树或运行时全局日志。

| 项                        | 值                                                | 来源（唯一）                                                                                                                                                  |
| ------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 会话 ID                   | `mvs_4e9f4b2b7bdd47348293cdbb41f60109`            | `operator/acceptance.json`、`operator/settings.json`                                                                                                          |
| 原 turn ID                | `659fd77a-9a0b-49c5-b39f-48aeb928d9f1`            | `operator/input-read-proof.json`                                                                                                                              |
| 平台侧任务标识（task ID） | **UNKNOWN**                                       | `operator/preparation.json` 记 `taskId: null`；`operator/acceptance.json` 未提供该字段 → 按缺项如实记 UNKNOWN，不自填、不推断                                 |
| 原 turn 正式终态          | **UNKNOWN**                                       | `operator/acceptance.json`：`formalOriginalTurnTerminal: "UNKNOWN"`；`operator/input-read-proof.json`：`terminal: "UNKNOWN"` → 报告存在不等于任务已 completed |
| 实际模型                  | `M3.1-Flash（订阅限免）`                          | `operator/settings.json`：`modelUI`，来源为本方当前任务 UI 实际读回，`settingScope: "Current submitted task UI, not global default"`                          |
| 思考等级                  | `xhigh`                                           | `operator/settings.json`：`reasoningUI`                                                                                                                       |
| 权限模式                  | `始终授权`（映射 `bypassPermissions`）            | `operator/settings.json`：`permissionUI` / `permissionMapping`                                                                                                |
| 工作目录 / HEAD           | 与本方实测 `pwd`、`git rev-parse HEAD` 逐字符相同 | `operator/settings.json`、`operator/acceptance.json` vs 本方实测                                                                                              |
| 附件字节/行数/SHA         | `29715` / `147` / `1985d7c54e0d…3f1c40`           | `operator/acceptance.json` + 本方实测一致                                                                                                                     |

**收据限度（必须如实说明）**：`operator/settings.json` 的 `originalTurnId` 为 `UNKNOWN`（owner 的原生精确查询须在 GUI 释放后单独执行），原 turn ID 由**稍后**的 `operator/input-read-proof.json` 记录。`operator/preparation.json`（准备阶段）记 `actualTaskSettingsReadback: false`、`bodySubmitted: false`、`guiLeaseGranted: false`，即该文件反映的是**投递前**状态，不作为提交后运行期读回。运行期思考等级与权限模式在**本会话内无第二读回途径**，本报告只引用上述回执，不声称二次确认。

**本方未做的事（按本轮输入边界）**：未调用 `agent list`、未调用 `session get`、未列举或搜索任何应用全局配置/全局日志/账号目录/原生 session 目录与 rollout、未接触另一审者本轮任何材料、未写或覆盖任何 operator 目录既有文件、未签发 operator 收据、未读取凭据、未调用付费模型 API。

**本方首失败（保留）**：`operator/initial-input-verification-attempts.json` 记录了本方首次附件核验请求的失败——把附件文件路径当作目录 `cd`，返回 `Not a directory`（exit 1）。该失败**原样保留**，随后改为按文件路径 `wc`/`shasum` 成功。本方工程验证侧的首失败同样保留于自有收据（见第 7 节与第 12 节）。

---

## 2. 附件核验与实读

| 项       | 声明                                                                                                                           | 本方实测               | 结果 |
| -------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------- | ---- |
| 附件路径 | `/Users/kyle/.minimax/v2/assets/2026/10/23/04-13-45-488-asset_20261023-041345-488_1985d7c54e0d_e0dc3c19-full-minimax-input.md` | 同路径                 | ✅   |
| 行数     | 147                                                                                                                            | `wc -l` → `147`        | ✅   |
| 字节数   | 29715                                                                                                                          | `wc -c` → `29715`      | ✅   |
| SHA-256  | `1985d7c54e0d1f0b8804018542e7d57d070c3d4da08b3055e1940f8dc53f1c40`                                                             | `shasum -a 256` → 同值 | ✅   |

- **实读**：完整读取第 **1–98** 行与第 **99–147** 行两段，覆盖 1–147 且连续无缺口。读取工具对首段提示截断时按同一路径续读至末尾，末尾“2026-10-22 后台恢复补充”与“历史”段已读到。
- **同一原件交叉印证**：树内 `docs/reviews/T04/p3-repair/launch-r3/full-minimax-input.md` 亦为 **29715 B**，与附件同体量来源；`operator/input-read-proof.json` 记录的原生读取路径即本附件路径，其 `nativeReconstructedBytes: 29715` / `nativeReconstructedSHA256` 与本方实测一致。
- **附件内容在本轮作为被审查对象处理**：正文本身声明了工作树、diff、42 项清单、边界与政策；本报告以正文的**约束**为准，但其中所有**对产品与历史的事实性断言**均由本方独立复核，未直接采信。

---

## 3. 工作树身份、完整 diff 与 42 项产品核验

### 3.1 工作树与 HEAD

| 检查                     | 审前                                                                        | 审后     | 结果                             |
| ------------------------ | --------------------------------------------------------------------------- | -------- | -------------------------------- |
| `pwd`                    | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-r3-5070004` | 同左     | ✅                               |
| `git rev-parse HEAD`     | `5070004ec8e3219bea33960bd88f57f1976e9cf8`                                  | 同左     | ✅ 未变                          |
| 分支状态                 | detached（`git symbolic-ref HEAD` 无符号引用）                              | 同左     | ✅ 无开发分支                    |
| `git status --short`     | ` M AGENTS.md` + `?? docs/reviews/T04/p3-repair/launch-r3/`                 | 完全相同 | ✅ 未变                          |
| 保护 `AGENTS.md` SHA-256 | `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`          | 同左     | ✅ 未覆盖/未格式化/未暂存/未提交 |
| `package-lock.json`      | `a462ba7092588c325829e0b05bbcb1a0fa97e6914307b84d97103875b3c29bb5`          | 同左     | ✅                               |
| `uv.lock`                | `d5d027da6628a2f4fc2e73730ce3a5e40d85aebba95188b0d4c3801ebdde949e`          | 同左     | ✅                               |

### 3.2 完整 base→product diff 独立复现

| 项                                             | 声明                                                               | 本方实测                 | 结果 |
| ---------------------------------------------- | ------------------------------------------------------------------ | ------------------------ | ---- |
| `git diff --binary 5f910b52… 5070004e…` 字节数 | `256242`                                                           | `256242`                 | ✅   |
| 上述 diff 的 SHA-256                           | `27c090fc00cd6d1a851695551c2d5e4e9714d9845b9d5f3ee91ae51f9995b030` | 同值（审前、审后各一次） | ✅   |
| 变更路径数                                     | 42                                                                 | 42                       | ✅   |

**共享路径零改动**（架构不变量）：按 `git diff --name-only base product` 过滤 `apps/desktop/src/main/`、`apps/desktop/src/preload/`、`apps/desktop/src/csp.ts`、`packages/contracts/`、`package.json`、`package-lock.json`、`uv.lock`、`pyproject.toml` → **空集**。本轮 diff 未触及共享契约、CSP、preload/main、锁文件与依赖清单。

### 3.3 全部 42 项产品文件三方一致

按 `docs/reviews/T04/p3-repair/launch-r3/product-manifest.json` 逐项，对 **manifest 声明的 bytes+sha256 ↔ 工作树物理文件 ↔ 固定 product 的 Git blob** 三方比对：

```
manifest file count: 42
all-3-way match: 42/42
MISMATCH: none
```

42 项分类（与 `process-history-neutral.md` 一致）：runtime 7 / 测试 5 / fixture 8 / probe 2 / 其他文档 20。本方**逐项阅读了全部 42 项**（见第 4 节），未只审四 P3、UI、reader 或某个 stage；`candidate-files.json` 的 22 项作为 runtime/test/fixture/probe 子集单独核对，未用于替代 42 项。

---

## 4. 已读完整范围（本方逐文件实读）

**实现（7）**

- `packages/engine/src/ontolearn_engine/query_service/__init__.py`（249 B，仅导出 4 个纯函数）
- `packages/engine/src/ontolearn_engine/query_service/drafts.py`（6315 B）
- `apps/desktop/src/renderer/src/query/draft.ts`（6047 B）
- `apps/desktop/src/renderer/src/query/results.ts`（4400 B）
- `apps/desktop/src/renderer/src/query/reader.ts`（14095 B）
- `apps/desktop/src/renderer/src/query/QueryPage.tsx`（27492 B）
- `apps/desktop/src/renderer/src/query/query.css`（2104 B）

**测试（5）**：`packages/engine/tests/test_query_service_authoring.py`、`test_query_service_approved_baseline.py`；`tests/unit/t04-query-authoring.test.ts`、`t04-query-results.test.ts`、`t04-query-reader.test.ts`（484 行，完整读完）。

**Fixture（8）**：`tests/fixtures/query/authoring-case.json`、`draft-boundaries.json`、`p3-interaction.tsx`；`tests/fixtures/query/approved-baseline/{G-base.json, conventions.json, manifest.json, provenance.json, unclosed-high.rq}`。

**探针（2）**：`docs/iterations/T04/ssr-probe.mjs`、`p3-interaction-probe.mjs`。

**文档（20）**：`docs/iterations/T04/{acceptance.md, integration-handoff.md, reader-integration.md, p3-repair-plan.md}`；`docs/reviews/T04/{status.md, internal-candidate.md, internal-review-1..7.md}`；`docs/reviews/T04/evidence/{final-verification.json, verification-summary.json}`；`docs/reviews/T04/p3-repair/{candidate-files.json, plan-review.md, implementation-review.md, verification.json, owner-verification-raw.tar.gz}`。

**过程补充与本方输入（非受审 Git HEAD）**：`launch-r3/{full-minimax-input.md, process-history-neutral.md, post-freeze-review.md, setup-minimax.json, product-manifest.json, historical-files.json, t09-provenance-files.json, prior-554-review-history.tar.gz, approved-t09-provenance-inputs.tar.gz, current-agents.md, current-permissions.md, current-desktop-policy.md, current-section9.md, mapping-minimax.json, role-package-minimax.json, policy-sources.json}`。

**归档原件（本方独占解包读取）**：`prior-554-review-history.tar.gz` 全 **71** 项，`historical-files.json` 声明来源提交 `9da9da48b45b4f0cbbe084d95c3d23ebd85c579b`、被审产品 `554ec89844ae5e8efcc4ac0d4f7e21d955a4b6a6`。本方逐成员重算：71/71 字节与哈希一致，0 项不符，无"磁盘多出"或"清单缺项"。

---

## 5. 原需求依据（PRD）与架构不变量核对

### 5.1 实读 PRD 条款

- `docs/prd/PRD-本体学习与落地Agent工作台.md`（V0.6，93584 B，1255 行）。本方实读 **FR-006**（数据层次与结果失效）、**FR-400**（多种查询入口）、**FR-401**（查询透明性与数据范围）、**FR-402**（本地只读与网络限制）、**FR-403**（结果与空结果解释）、**FR-404**（查询保存与复用）、**附录 C**（MVP 能力矩阵主定义）、**附录 D**（数据变化与结果失效表 D.1/D.2）、**附录 G**（Q-01/Q-02/O-01 原文预期）、**第 11 节**（产品指标）、**第 12 节**（MVP 端到端验收标准 12.1/12.2/12.3）。
- PRD 在 base `5f910b52…`、product `5070004e…` 与本树物理文件三处 SHA-256 均为 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` → **本产品未改 PRD**。
- 附录 C 明确：`SPARQL SELECT/ASK`「仅项目内只读执行」，`CONSTRUCT`/`DESCRIBE`/更新/远程联邦**不属于 P0**；附录 G Q-01 要求「完整结果只有 A01；包含 A02/A03 均失败」，Q-02 要求改 Closed 后**空结果**，O-01 要求「未记录」语义。

### 5.2 架构不变量逐条核对（静态 + 运行）

| 不变量                                           | 核对结论 | 证据                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 本地优先：无自动模型/遥测/云服务、不开 HTTP 端口 | ✅       | 42 项 diff 未新增网络调用；`QueryPage`/`reader` 无 `fetch`/`http`/`WebSocket`；模型仅经父传入的 `modelDraft` 可见草稿                                                                                                                                                                     |
| 渲染端隔离：无 Node/文件系统/shell/通用 IPC      | ✅       | 新增 renderer 文件无 `node:`/`require`/`process.`/`fs`；preload/main/contracts 零改动；只复用已批准 `DesktopBridge` 的 `getResult`/`getResultPage`/`getJob`/`cancelJob` 四个命名方法，无 `invoke(method, params)` 式通道                                                                  |
| CSP 唯一配置源                                   | ✅       | `apps/desktop/src/csp.ts` 未改动（本轮 diff 无该路径）                                                                                                                                                                                                                                    |
| 确定性结果只来自真实引擎；Agent 只产草稿         | ✅       | 页面无执行器、无 Store 写入；无真实 adapter 时执行/保存按钮禁用并显示「真实查询服务尚未接入 / 项目事务服务尚未接入」                                                                                                                                                                      |
| 存储唯一源真相；正式写入只经 `Store.commit`      | ✅       | `query_service` 无 `storage.py` 引用；`save_intent` 仅返回 `{family,id,expectedProjectRevision,draftDigest,value}` 意图，文档明确「never commit」                                                                                                                                         |
| 失效规则只来自 `invalidation-v2.json`            | ✅       | 页面 `staleReason` 只读自批准 `result` schema，不自推断；`invalidation-v2.json` 未被本轮改动                                                                                                                                                                                              |
| 跨边界只传固定错误码与受限参数                   | ✅       | `reader.ts:57-63` 的 `invalid(field)` 只取 `identity`/`params`/`cursor`，均在 `packages/contracts/v2/errors.json:5-18` 的批准枚举 `["envelope","params","identity","config","cursor","dependency","kind"]` 内；原始 bridge 异常固定 `internalError`，测试以 `PRIVATE_PATH` 标记断言不外泄 |
| 数据层次分层、历史不可改写                       | ✅       | 本轮未触及历史/失败/取消语义；仅页面区分「此前查询结果」与当前任务                                                                                                                                                                                                                        |
| 未批准依赖                                       | ✅       | `@playwright/test 1.64.1`、`@vitejs/plugin-react 6.1.2`、`vite 8.3.4`、`typescript 5.9.3` 均为仓库既有锁定项；双锁文件未变                                                                                                                                                                |

---

## 6. 独立源码审查要点（逐文件，非摘要）

### 6.1 Python `query_service/drafts.py`

- `_text`（:23-31）拒绝非字符串、超界与**孤立代理项**（`0xD800–0xDFFF`），先于任何编码操作。
- `_DRAFT_EDGE_SPACE`（:34-37）为 **Python 29 个空白 + U+FEFF = 恰 30 个**码点，与 TS 侧集合逐码点相同。
- `_draft_text`（:40-48）顺序正确：**先 `_text` 标量/原串检查 → 再按 UTF-16 code units 判长 → 再按固定 30 字符去边缘 → 拒空**；内部字符不动。因 `_text` 先于 `value.encode("utf-16-le")`，孤立代理项不会触发 `UnicodeEncodeError` 而只会得到 `DraftError`。
- `serialize_term`（:60-80）：IRI 强制 `scheme:` 前缀并拒绝空白/控制字符/`<>"{}|^`\` 与孤立代理项；literal 用 `json.dumps(ensure_ascii=False)` 并把 `\x7f` 改写为 `\u007F`；language 与 datatype 互斥，language 小写输出。
- `compile_visual`（:83-128）：严格 `_object` 精确键集；字段 ≤16、条件 ≤32；`exists`/`not-exists` 走 `FILTER (NOT) EXISTS`；其他算子走三段式 `?item <p> ?conditionN .` + `FILTER (?conditionN op value)`；返回值字段用 `OPTIONAL`；末尾 `ORDER BY` 按 `?item ?field0…`。
- `validate_draft`（:131-145）：六字段精确键集；`name`/`sparql` 走 `_draft_text`；`description`/`capabilityQuestion` 仍按 4096 **码点**判定（上限未变）；`scope`/`source` 枚举。
- `save_intent`（:148-168）：`definition_id` 正则 `[A-Za-z0-9_.-]{1,128}` 拒路径穿越；`expected_revision` 用 `type(...) is not int` 拒 bool/浮点/越界；只产出意图与 `draftDigest`，不提交。

### 6.2 TS `query/draft.ts`

- `scalarText`（:4）以 `/[\uD800-\uDFFF]/u` 拒绝孤立代理项；`u` 标志下 astral 字符为单码点，**不**被误判（这是 D1 的关键前提）。
- `draftEdgeSpace`（:56-59）与 Python 同为 **30 个**码点；`draftText`（:60-70）顺序为 **raw → 显式 `s.length`（UTF-16）→ 去边缘 → 拒空**。
- `visualSchema`（:47-53）：`fields` ≤16、`conditions` ≤32，**数组本身无 `.min(1)`**；`conditionSchema` 为 `discriminatedUnion`，严格对象。
- `compileVisual`（:98-120）与 Python 逐 token 一致（含 `ORDER BY` 空格与换行）。
- `serializeTerm`（:83-97）：`JSON.stringify` + `\u007F` 改写；language 小写；language/datatype 互斥。
- `savedQuerySchema`/`definitionIdSchema`（:158-165）：`{definitionId,draft}` 严格对象；`definitionId` 正则拒路径穿越。

### 6.3 TS `query/results.ts`

- `queryMetadata`（:29-34）复用 `validateV2('result')` 并限定 `kind==='query'` 与断言范围。
- `acceptPage`（:44-67）复用 `validateV2('page')`（批准 schema `packages/contracts/v2/schema.json:2181+` 的 `page.rows.maxItems: 200` 为**真实强制点**），并追加：完整五字段身份一致、`columns` ≤64 且每项为 string 且 ≤128、rowId 唯一、页内 `(ordinal,rowId)` 严格升序、每行 `cells.length === columns.length`。返回 `structuredClone` 副本。
- `exportPageCsv`（:80-106）：仅**字符串**（含列头）施加公式/前导控制字符 `'` 前缀；有限 number/boolean 输出 `String(value)` 规范文本；`null` → 空；非有限数值与对象/数组/`undefined` 一律 `query.invalidPage`；引号双写；CRLF 连接；仅当前页，行数 >200 拒绝。
- `queryJob`（:108-121）复用 `validateV2('job')` 并限定 `projectId` 与 `capability === 'query.execute'`，否则返回 `undefined`。

### 6.4 TS `query/reader.ts`

- 仅用 `DesktopBridge` 的 4 个命名方法（:42），无新 IPC、无 cursor 发行、无持久缓存、无隐式重试。
- `bind`/`receiveUpdate`（:96-173）以 `generation`/项目/输入快照/项目版本变化为界作全量重置，迟到 metadata/page 在 token/epoch 失配时不发布；`compatibleJob`（:177-186）允许**合法版本跳跃**，但拒绝同版本异状态与已观察终态重开。
- `cancelFloor`/`minimumJobVersion`（:79,188-190,412-415）让 ACK 版本下限跨刷新、通知、取消前查询保留。
- `fetchPage`（:244-320）：只请求引擎实际发行的 `nextCursor`；跨页倒退/自循环游标拒绝；空页保留**最后非空行** `(ordinal,rowId)` 有界锚（:303-304）；`evicted` 保留身份不请求缺失载荷。

### 6.5 TS `query/QueryPage.tsx`

- 范围与输入选择始终可见（:171-196）；执行请求携带 `current|historical` + `snapshotId`。
- 可视构建：字段计数（:232）、达 16 只禁用**未选**项（:239）、`onChange` 在**最新 state** 中防重复与超限（:243-252）；条件 32 上限（:424）。
- 生成按钮取**真实** `visualSchema.safeParse` 有效性（:63, :442-445），并给检查提示；`build()`（:113-121）编译失败时**不调用** `update()`，草稿不被覆盖。
- 非法 RDF 类型切换（:326-349）只改 `visual`，不改写 `draft.sparql`。
- 新建（:548-557）与成功 saved 载入（:559-574）清空 `visual` 的 class/fields/conditions 并推进 `documentGeneration`；model 载入（:536-547）同样清空 `visual`。
- 保存身份：`onSaveDraft` 必须返回真实 ID，经 `definitionIdSchema.parse`（:513），更新时 ID 必须一致否则抛错（:516-517），且仅在同 request token **且**同 document generation 时绑定（:519-522）。
- 结果侧：`executedSparql` 取自结果对象而非编辑器；`null` 显示「未记录」；空页按 `nextCursor` 区分「仍有后续页」与末页并列 5 条可操作检查方向；CSV 导出仅当前页并带 BOM。

---

## 7. 本轮实际执行的验证（完整 argv / cwd / UTC 起止 / 真实 exit / raw / SHA）

运行环境：cwd 均为本方 review 树；`npm_config_cache`/`UV_CACHE_DIR`/`TMPDIR` 由日志工具指向本方独占 `test-results/t04-review-runtime/minimax/`。日志工具 `docs/reviews/T04/p3-repair/launch-r3/run-review-command.py` 未被修改。

| #   | argv                                                                                                                                 | 起止（UTC）                    | exit  | 结果 / raw                                                                                                                                                                                                                                                                                                                       | 收据                                                                                                                    |
| --- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 1   | `npm run check`（lint→format:check→typecheck×3→vitest→build→engine:check）                                                           | 2026-10-22T20:15:47 → 20:17:07 | **0** | lint 0 警告；prettier 全过；三套 tsc 全过；**vitest 18 文件 / 719 项通过**；`electron-vite build` main/preload/renderer 三段成功；`ruff check`/`ruff format --check` 全过（196 文件）；**pytest 1167 passed in 56.07s**                                                                                                          | `metadata/mm-r3-full-check-01.json`，raw 5389 B，SHA `1b86a3e70f159fcd5d011d4b94e5b441aa72299af926599305b7600793b10d7f` |
| 2   | `node docs/iterations/T04/ssr-probe.mjs`                                                                                             | 2026-10-22T20:18:29 → 20:18:29 | **0** | `passed:true`，**14 项**检查：offline-disabled / scope-visible / text-escaped / historical-identity / executed-query / empty-directions / project-rejection / evicted-identity / non-query-job-rejection / query-job-accepted / previous-result-labeled / cancel-ack-separate / cancel-ack-bound-to-job / result-loading-visible | `metadata/mm-r3-ssr-01.json`，raw 423 B，SHA `f730e85970c4fff87784f8d377da18f50da85de9487a4a0080fedc38a0f80874`         |
| 3   | `node docs/iterations/T04/p3-interaction-probe.mjs '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' review-minimax-r3` | 2026-10-22T20:18:32 → 20:18:37 | **0** | Chrome **155.0.8059.85**，headless、offline、**requests 0、pageErrors 0**；**5/5** 情景通过：invalid-rdf-type-blocks-generation / sixteen-fields-and-reselection / saved-load-clears-old-builder / new-query-clears-old-builder / model-load-clears-old-builder                                                                  | `metadata/mm-r3-component-01.json`，raw 1037 B，SHA `2acd93153f7a294c623c4d5a99fbe807fa0d5efb3b17a74c7838b811e3cce705`  |

三份 raw 文件的 SHA-256 经审后独立重算，与上表收据**逐字符一致**。

**本轮无首失败**：三条命令均首跑 exit 0。既有首失败（网络安装 `ECONNRESET`、Python 回归 8 failed/104 passed、TS 回归 19 failed/46 passed、交互探针定位失败、Zod 码点长度反例 2 例、lint `no-control-regex`、docs format 失败）由 owner 原样保留在 `docs/reviews/T04/p3-repair/verification.json` 与 `owner-verification-raw.tar.gz` 中，本方已解包并逐成员核对（51 成员：25 命令 metadata + 25 raw + `run-evidence.py`），未删除、未改写、未以失败后筛绿冒充通过。

**本方未执行（不扩大）**：`npm run dev`、HMR（`I02_HMR=1`，冻结期间禁跑）、`npm run test:e2e`（Electron）、`npm run package:dir`、产物/Electron/App 启动、任何真实 `query.execute`、真实 Store 写入、真实凭据/原生提示、两 OS 与真人验收。以上均未以静态或合成证据代替。

---

## 8. 本方独立反例（自写，不筛绿）

全部写于本方独占写面 `test-results/t04-review-runtime/minimax/counterexamples/`，只调用受审公开 API，不修改任何产品/测试/fixture/依赖/配置/验收。

| 探针                      | 目的                                                                          | 结果                                                                                                                                                                                                                                                                                                   |
| ------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `zod-unit-probe.mjs`      | 实测本仓 zod（**4.6.7**）`.max()` 的计量单位                                  | `max(64)` 接受 64 个 astral 字符（64 码点 / 128 UTF-16 单位）→ **zod v4 `.max()` 按码点计量**。据此，D1 在 `draft.ts` 显式使用 `s.length` 是**必需且正确**的                                                                                                                                           |
| `d1-python-probe.py`      | D1 Python 侧独立边界                                                          | **40 例，0 mismatch**：共享 fixture 20 例 + 30 个边缘码点 × 2 字段 × 2 断言 + 20 例自拟边界（129 码点 / 128 码点 / 64 astral / 65 astral / 64 astral+1 ASCII / 30 边缘空白 / 纯空白 / 内部空白保留 / 孤立代理项高·低·内部·边缘 / sparql 65536、65537、32768 astral、32769 astral / 孤立代理项 / trim） |
| `d1-ts-probe.ts`          | D1 TypeScript 侧独立边界（Node 24 类型剥离直引产品 `draft.ts`，不经产品测试） | **40 例，0 mismatch**，与 Python 逐例一致；另独立核 **16 字段接受 / 17 拒绝、32 条件接受 / 33 拒绝、空数组允许**                                                                                                                                                                                       |
| `t09-provenance-check.py` | T09 provenance 与完整答案集独立核验                                           | **19/19** 成员字节+SHA 一致；**4/4** 产品副本与归档原件逐字节相同（含 manifest `aaaef2c0…`）；**0 mismatch**。独立重建 G-base 后：原查询与生成查询均只返回 **A01**；A01 改 Closed 后均为**空集**；故意错误 Closed/High 返回 **A02**，与正确结果**行数相同但集合不同**（同数量错义被检出）              |

> 说明：本方在编写首个 JSON 附加用例文件时误用了 JavaScript `.repeat()` 语法导致 JSON 解析失败；该失败保留在过程记录中，随后改为由 Python/TS 脚本内联构造，未修改任何产品文件。

---

## 9. 四项 P3 逐项独立判断

### D1（Z-P3-1 / M-F1）：trim 与长度口径 —— **已修复，通过**

- **要求**：只统一 `name`/`sparql`；**原串先按 UTF-16 code units 限 128/65536，再按固定 30 字符去边缘空白，拒空，内部不变**；收紧接受面，不提高上限；`description`/`question`/RDF 上限不变。
- **实现核对**：`drafts.py:40-48` 与 `draft.ts:60-70` 的**检查顺序一致**（raw → UTF-16 → trim → 拒空）；两侧边缘空白集合均为**恰 30 个码点**（`drafts.py:34-37` vs `draft.ts:56-59`，逐码点相同）；内部字符不变；孤立代理项仍在两侧被拒（`drafts.py:23-31` 的 `_text` 先于 `encode`；`draft.ts:4` 的 `u` 标志正则不误伤 astral）。
- **独立证据**：`zod-unit-probe.mjs` 证明 zod v4 `.max()` 按码点，故 `draft.ts:62` 的显式 `s.length` 是使 UTF-16 口径成立的**唯一**手段；`d1-python-probe.py` 与 `d1-ts-probe.ts` 各 40 例、**0 mismatch**，两语言接受面与规范化值逐例一致。
- **未放宽**：`description`/`capabilityQuestion` 仍 4096 码点；IRI 2048、literal 8192、label 128 未变；`visualSchema` 的 16/32 上限未变。
- **判定：关闭。**

### D2（Z-P3-2 / M-F2）：CSV 数值保真 —— **已修复，通过**

- **要求**：列头必 string；有限实际 number/boolean 保规范文本（含负数/-0）；null 空；**仅 strings（含列头）**沿用公式与前导控制字符防护；保引号双写/CRLF；非法非有限数值/对象等拒绝；核字符串负数与实际负数语义不同；不减字符串防护。
- **实现核对**：`results.ts:90-100` 的分支顺序为 `string → 前缀防护` / `null → ''` / `boolean|有限number → String(value)` / `else → throw`；列头经同一 `escape` 处理，故**列头同样受公式防护**；`results.ts:82-88` 拒绝非 string 列头、>200 行与 cells 长度不匹配。
- **独立证据**：产品单测 `t04-query-results.test.ts:125-163` 断言完整 CSV 字节——实际 `-5` → `"-5"`、字符串 `'-5'` → `"'-5"`、`-0` → `"0"`、`1e-7` → `"1e-7"`、`true/false` 保真、`null` → `""`、引号双写、CRLF、`NaN/Infinity/-Infinity/undefined/{}/[]` 全部抛错、非 string 列头抛错、201 行被拒。本方独立复核确认这些断言**覆盖 D2 的每一项要求**，且未削弱字符串注入防护。
- **判定：关闭。**

### D3（Z-P3-3）：可视字段超 16 的 UX —— **已修复，通过**

- **要求**：在**最新 state** 上防重复与超 16；达 16 时**只禁未选项**、已选可取消；显示计数；条件 32 上限保持。
- **实现核对**：`QueryPage.tsx:232` 显示「已选 n/16」；:239 的 `disabled` 条件为 `length >= 16 && !已选`，即已选项始终可点；:243-252 的 `onChange` 使用**函数式** `setVisual(current => …)`，在最新 state 上先查重复、再查 `current.fields.length >= 16`，重复勾选与第 17 项均被拒绝而取消不受影响；:424 的条件 32 上限保持；编译层 `draft.ts:50-51` 与 `drafts.py:87-93` 的 16/32 上限未变。
- **独立证据**：本方 component probe 情景 `sixteen-fields-and-reselection`（exit 0）实际执行「选满 16 → 第 17 项禁用 → 第 1 项仍可用 → 取消第 1 项 → 选第 17 项 → 生成」，并逐字断言生成的 `SELECT DISTINCT ?item ?field0…?field15` 与所选 16 个谓词**顺序完全对应**；本方 TS 探针另行独立确认 16 接受/17 拒绝、32 接受/33 拒绝。
- **判定：关闭。**

### D4（M-F3）：新建/复用未重置 visual —— **已修复，通过**

- **要求**：新建及**成功** saved/model 载入清空 visual 的全部 class/fields/conditions；生成按钮取**真实** `visualSchema` 有效性并给检查提示；**非法 RDF 类型切换不能覆盖原草稿**，修正后才生成；不猜反解任意 SPARQL；不改变原保存身份/documentGeneration 规则；模板仍明确填自己的 builder。
- **实现核对**：
  - 新建（:548-557）：`documentGeneration.current++`、`setDefinitionId(null)`、`setVisual(emptyVisual())`（`emptyVisual` 含 `classIri:''`、`fields:[]`、`conditions:[]`，:58）、`update(initialDraft)` → **全清**。
  - 成功 saved 载入（:559-574）：仅在 `savedQuerySchema.safeParse` 成功后推进 generation、清空 visual、绑定 `definitionId`、载入草稿；解析失败只给提示、不改状态。
  - model 载入（:536-547）：解析成功后清空 visual 后以 `source:'model'` 载入可见草稿。
  - 生成按钮（:63, :442-445）用 `visualSchema.safeParse(visual).success` 的**真实**结果决定禁用并给检查提示；`build()`（:113-121）在 `compileVisual` 抛错时**不执行 `update()`**，故草稿不被覆盖。
  - 非法 RDF 类型切换（:326-349）只改 `visual`，**不触碰 `draft.sparql`**；不猜反解任意 SPARQL（无任何 SPARQL→visual 的反解析代码）。
  - 保存身份与 generation 规则未被改动（:513-522 原样保留）。
  - 模板按钮（:200-214）显式调用 `build(alarmTemplate(vocabulary), 'template')`，**走自己的 builder**，不走可视构建器。
- **独立证据**：component probe 三个载入情景（saved/new/model）+ `invalid-rdf-type-blocks-generation` 全部通过（exit 0）：切到非法 IRI 后生成按钮禁用、原 SPARQL **完整保留**、填入 `urn:High` 后按钮恢复并生成 `…<urn:High>…`。
- **判定：关闭。**

---

## 10. 历史意见逐项独立复判（本方不采信任何"已 closed"表述）

以下每项均由本方在**固定 product 5070004 的源码**上重新定位实现并核对调用路径得出，未沿用旧 554 轮的 Pass，也未沿用既有 8 份内审的"通过"。

| 项                                                      | 原问题                                               | 本方独立复判                  | 实际依据（文件:行）                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------- | ---------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **R1-01**                                               | 复用保存丢失 definitionId；新建保存不返回真实 ID     | **已关闭** ✅                 | 私有 `savedQuerySchema`/`SavedQuery` 携 `definitionId` 且 strict（`draft.ts:158-165`）；载入保留身份（`QueryPage.tsx:563-568`）；保存回调必须返回真实 ID 并经 `definitionIdSchema.parse`（`QueryPage.tsx:513`）；更新时 ID 不一致即抛错（:516-517）；迟到响应以 request token **且** document generation 双闸拒绝（:519-522）；同名不同定义以不同 `definitionId` 区分（`draft.ts:158`，`t04-query-authoring.test.ts:116-131`） |
| **R1-02**                                               | 同项目非 query 任务被显示并可取消                    | **已关闭** ✅                 | `queryJob` 复用批准 `validateV2('job')` 并限定同项目 + `capability==='query.execute'`，否则 `undefined`（`results.ts:108-121`）；页面据其结果决定是否渲染任务区与取消入口（`QueryPage.tsx:148, 580-622`）；jobId 不同者持续标注「此前查询结果」（:632-634）；失败说明走受限 `explainError`（:149, :596-603）                                                                                                                   |
| **R5-01**                                               | ACK 后重读未完成即释放 `cancelBusy`，重复取消        | **已关闭** ✅                 | `cancel()` 以 `return await this.refreshJob(jobId)` 覆盖 ACK 后重读全生命周期（`reader.ts:418`）；`cancelBusy` 仅在 `finally` 且 `current()` 成立时释放（:422-424）；重复取消被 `cancelBusy` 与 token 双重拒绝（:363-365）                                                                                                                                                                                                     |
| **R5-02**                                               | 空页丢失最后非空排序锚，10→空→5 被接纳               | **已关闭** ✅                 | 仅在 `page.rows.at(-1)` 存在时更新锚点，空页保留旧锚（`reader.ts:303-304`）；跨页回退被拒（:294-302）；新读/新绑定/释放清理锚（:209, :116, :434）                                                                                                                                                                                                                                                                              |
| **R5-03**                                               | ACK 版本下限在后续刷新/通知/取消前查中丢失           | **已关闭** ✅                 | `cancelFloor` 私有保存 ACK 下限（`reader.ts:79, 412-415`），`minimumJobVersion()`（:188-190）被刷新（:338）、通知（:167）、取消前查（:384）共用；切 job/新绑定正确清理（:346, :118）                                                                                                                                                                                                                                           |
| **R5-04**                                               | `trim` 改写实际执行 SPARQL 原文                      | **已关闭** ✅                 | `executedSparql` 仅用 `trim()` 做非空判定，保留原字符串（`reader.ts:37-38`），写入快照时原样（:275, :312）；页面展示取自结果对象而非编辑器（`QueryPage.tsx:638`）                                                                                                                                                                                                                                                              |
| **R6-01**                                               | `INVALID_REQUEST` 用 `params={}`，被降级为 internal  | **已关闭** ✅                 | `invalid(field)` 只取 `identity`/`params`/`cursor` 并写入 `params.field`（`reader.ts:57-63`）；三者**均在** `packages/contracts/v2/errors.json:5-18` 的批准枚举内；元数据失败归 `identity`（:260, :266）、分页失败归 `cursor`（:292, :302）、参数失败归 `params`（:220）；原始 bridge 异常固定 `internalError`（:317-319, :350-353, :419-421），测试以 `PRIVATE_PATH` 标记断言不外泄（`t04-query-reader.test.ts:257-269`）     |
| **同版本矛盾 / 已观察终态重开**                         | 须拒绝同版本异状态与终态重开，但不得拒绝合法跳跃观测 | **已关闭** ✅                 | `compatibleJob()` 允许版本跳跃，同版本异状态与终态再开均拒（`reader.ts:177-186`）；本方核对确认**未**使用"相邻状态转换"约束，不误拒合法跳跃观测                                                                                                                                                                                                                                                                                |
| **同数量错义反例**                                      | 正确 A01 与错误 A02 行数相同，必须比对完整答案       | **已关闭** ✅                 | 产品测试 `test_query_service_approved_baseline.py:86-95` 显式构造 Closed/High 得 A02 并断言 `wrong_rows != correct_rows`；**本方另以独立脚本从归档原件重建 G-base 复现同一断言**（A01 唯一 / Closed 空集 / 错误 A02 同数量异答案），且每次从实际 ontology/facts 还原，未用 expected 预填 Store                                                                                                                                 |
| **总控 R1 原件可恢复性**                                | 37 份 raw 仅 ignored，需无损归档                     | **已关闭** ✅                 | 本方独立解包 `raw-logs-554ec89.tar.gz` 并逐成员重算：37/37 一致、总字节 61602 相符（经 `verification-and-history-index.md` 指向的归档逐成员核对）；本轮另独立解包 `prior-554-review-history.tar.gz` 与 `owner-verification-raw.tar.gz`（51 成员）并逐成员核对字节与哈希                                                                                                                                                        |
| **T09 provenance**（旧 M 表内标为"部分可核"的第 11 行） | 17 项输入的原始字节需可独立复验                      | **本轮已补齐为可核并通过** ✅ | 本方独立解包 `approved-t09-provenance-inputs.tar.gz`，**19/19** 项（17 项输入 + PRD + manifest）字节与 SHA-256 全部一致；产品实际消费的 4 个副本与归档原件逐字节相同；并独立复现 A01/Closed/A02 三组完整答案。**旧 M 报告原文不改写**，其当时的 partial 属当时工作树只含 3/17 副本的事实                                                                                                                                       |

**历史复判合计：10 项历史结论已关闭；第 11 项（T09 provenance）在本轮由"部分可核"升级为"19/19 可核并通过"。**

---

## 11. 对历史表述的更正（不抹平 partial）

**更正对象**：旧 M 报告 `round-1/minimax-m31flash.md` 开头第 11 行称「独立复核 R1-01/R1-02/R5-01..04/R6-01/同版本终态/同数量错义反例/总控归档 R1 **共 11 项历史结论，逐项独立核对源码后确认关闭**」。

- **该表述与其实际表不符**：同文件 §5 表格实际为 **11 行**，其中第 11 行「T09 固定输入 provenance」的结论列写明「**部分可核，其余仅记录** ⚠️ …本方无法独立重算其字节 → 仅能确认'记录完整且未被改写'」，**并非 closed**。
- **同一报告 §8 第 5 条已给出正确表述**：「共 **10** 项历史结论…确认关闭；T09 provenance 项为'记录完整、3/17 可逐字节复验、其余 14 项本方不可复验'，已单列且不影响 S1 判定」。
- **正确表述应为：10 项 closed ＋ 1 项 partial**，不得按开头一句写成"11 项全 closed"。旧 M 报告原文**保持不改写**，此处仅按其实际表与实际 §8 更正表述。
- 本轮已用完整 17 项原件归档把该 partial **由"不可核"补齐为"19/19 可核并通过"**（第 10 节末行），但这是本轮的独立结论，不回写旧报告。

---

## 12. 本轮新发现

### F-R3-01 [P3／低] TypeScript 内部字符串长度计量口径不一致（zod v4 `.max()` 按码点 vs 手工 `.length` 按 UTF-16）

- **严重度**：P3（低）。方向为**偏严**，不构成越权接受、不泄露数据、不破坏任何安全边界；仅在极端 astral 字符输入下产生**假拒绝**与错误分类失真。
- **实际位置**：
  - `apps/desktop/src/renderer/src/query/reader.ts:33` — `columns: z.array(z.string().min(1).max(128)).max(64)`
  - `apps/desktop/src/renderer/src/query/reader.ts:36-38` — `executedSparql: z.string().min(1).max(65536)`
  - `apps/desktop/src/renderer/src/query/results.ts:54` — `columns.some((s) => typeof s !== 'string' || s.length > 128)`
  - `apps/desktop/src/renderer/src/query/QueryPage.tsx:133` — `props.result.executedSparql.length > 65536`
- **具体触发**：
  1. 列名含 astral 字符，**码点数 ≤128 但 UTF-16 code units >128**（例如 70 个 emoji = 70 码点 / 140 单位）。`reader.ts:33` 的 zod `.max(128)` 按码点 → **接受**；随后 `results.ts:54` 的 `s.length > 128` 按 UTF-16 → **拒绝**，`read()` 返回 `INVALID_REQUEST{params.field:'cursor'}`，真实原因（列名超长）被归类为游标错误。
  2. `executedSparql` 同理：zod `.max(65536)` 按码点通过，`QueryPage.tsx:133` 的 `.length > 65536` 按 UTF-16 拒绝 → 整块结果被拒并显示「结果身份、范围或分页不匹配，未显示该载荷」。
- **影响**：ASCII 列名与 ASCII SPARQL 不受影响，实际业务影响面极小；无数据完整性或安全影响。
- **证据**（本方独立实测）：`test-results/t04-review-runtime/minimax/counterexamples/zod-unit-probe.mjs` 输出 `max64Accepts64Astral: true`（64 个 astral = 64 码点 / 128 UTF-16 单位，`.max(64)` 接受），证明本仓 zod **4.6.7** 的 `.max()` 按**码点**计量。owner 侧 `verification.json` 的 `firstFailureDisposition["targeted-ts-after-fix"]` 亦记有「2 astral failures showed Zod max uses code points; fixed explicit s.length check」——**同一根因**在 D1 处已被正确修复，但**未推广**到上述四处。
- **建议**：统一口径。鉴于 D1 已确立「原串按 UTF-16 code units 计量」为既定政策，建议这四处**同样显式使用 `s.length`**（`z.string().refine(s => s.length <= n)` 或在 `.max()` 后追加显式 refine），或统一改为码点并同步修正 Python 侧（Python `len()` 即码点）。二者择一即可，但**同一模块内不得混用**。
- **边界声明**：本项**不影响** D1–D4 的关闭判定，也不影响 S1 总体结论；父契约的列/术语义仍由 T00/I05 负责。

### 观察项（不计为缺陷，但必须如实记录）

- **OBS-1｜旧 M 报告开头"11 项历史 closed"与其实际表不符**：实际为 10 closed ＋ 1 partial（T09 provenance）。详见第 11 节。本轮已把该 partial 补齐为 19/19 可核并通过；旧报告原文不改写。
- **OBS-2｜Z 的 columns 非空下限观察为事实误读，本轮代码未引入该问题**：固定 5070004 的 `reader.ts:33` 为 `z.array(z.string().min(1).max(128)).max(64)`——`.min(1)` **只约束每个列名字符串**，数组本身允许 `[]`；`results.ts:44-67` 的 `acceptPage` 也不要求至少一列；`draft.ts:50-51` 的 `fields`/`conditions` 数组同样无 `.min(1)`。因此**不得**把"至少一列"当作已有保证；本轮**未改 reader**，也**未决定**零列/ASK 接口语义——**父元数据语义仍未定**，属父契约待定项，不是本轮缺陷。
- **OBS-3｜CSS 全局选择器**：`apps/desktop/src/renderer/src/query/query.css:76-84` 的 `.query-check input`、`.query-condition` 未限定在 `.query-workspace` 作用域内。当前仓库无同名元素，无实际冲突；属父 App 样式接线整理项，本轮未改（`query.css` 本轮无内容变更）。与旧 M 报告的同一观察判断一致。
- **OBS-4｜`staleReason.code` 静态类型较宽**：`results.ts:20` 声明为 `string`，而批准 schema 取值为固定枚举；属类型放宽，运行时仍由 `validateV2('result')` 强制，不影响边界。与旧 M 报告同一判断一致。
- **OBS-5｜owner 归档 `evidence/final-verification.json` / `verification-summary.json` 属更早候选**（`c4aa5f9c…` 与 `4c17a381…`），5070004 的终态入口是 `p3-repair/verification.json`。两份文件按其 candidate 原字节保留，未被改写为 507 的结果，符合「原件保留不改写」要求；阅读时须以 `p3-repair/verification.json` 为准。本方在 `p3-repair/verification.json` 中逐条核对了 25 条命令的 label/argv/exit/起止/raw 字节数，并解包 `owner-verification-raw.tar.gz` 的 51 成员逐一重算字节与 SHA-256，**一致**。
- **OBS-6｜独审 244 组纯探针的证据等级**：`launch-r3/post-freeze-review.md` 如实记录该 244 组来自 reviewer 原会话的**内联** `node <<'JS'` 命令，**无绝对起止时间、无独立 script/raw/SHA 文件**，仅存于其会话工具调用/输出中，故**不计为 owner 的持久运行原件**。本方不将其升级为运行证据，也未重跑以"补造"该原件；本方结论只依赖第 7、8 节自有收据与自有反例。该表述属实且恰当。

---

## 13. 未验边界与父功能缺口（本报告不证明）

完整 T04 父功能**仍待**（本 S1 或本轮均未证明，且不得以本报告替代）：

1. **真实执行与外联拒绝**：真实 `query.execute`、项目内只读执行、`SERVICE`/远程 `FROM`/更新/非 SELECT-ASK 的**真实**拒绝、隐式外联拒绝、真实时限/取消收敛/游标发行与过期/历史输入恢复。模板编译探针**不构成**外联拒绝验收。
2. **T01 事务保存**：唯一 preview/confirm/commit、原子失败与撤销、读取恢复、过期、同项目/旧基线拒绝、真实保存身份回填。`save_intent` 仅为私有意图，**不是**公共 ChangeSet。
3. **T08 / T09 / T10**：真实自然语言草稿与工具闭环、T09 完整案例、跨设备复用与项目包。
4. **结果元数据**：ASK 布尔结果约定、真实 RDF term 类型与列语义、适用局部关系图、`O-01`「未记录」的**真实执行侧**证据。
5. **父验收矩阵**：FR-400–404 全部条款、附录 C/D/G、第 11–12 节、全部 57 父 P0 与跨模块门、两 OS/真人。
6. **工程外围**：`npm run test:e2e`（Electron）、`npm run package:dir` 与包内同样例、原生/凭据、生产 CSP、App 挂载与下载。
7. **交付门**：CI、远端核验、正常合并、发布。本报告**不授权** push/PR/merge。

**本报告能证明的**：固定 `5070004e…` 上完整 S1 的**离线编写与批准读取客户端**实现正确、四项 P3 已修复、历史 10 项意见已关闭、T09 固定输入 19/19 可核且完整答案集正确、完整 check 与两项定向运行验证真实 exit 0。

---

## 14. 结论与声明

- **判定**：对固定 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → product `5070004ec8e3219bea33960bd88f57f1976e9cf8` 的**完整 T04-S1 范围：通过**。理由见第 0 节八条依据。
- **四 P3**：D1、D2、D3、D4 **全部关闭**，其中 D1 另有本方 Python/TS 双语言各 40 例独立反例佐证。
- **历史项**：10 项历史结论**已关闭**；旧 M 表内第 11 项（T09 provenance）在本轮由 partial 补齐为 **19/19 可核并通过**；旧报告开头"11 项 closed"的表述按其实际表更正为 **10 closed ＋ 1 partial**（第 11 节），旧原文不改写。
- **新发现**：1 项 P3（F-R3-01，TS 内部长度计量口径不一致，偏严、不越权）+ 6 项观察级记录，均不阻断 S1。
- **本轮验证**：3 条受控命令全部首跑 exit 0 并留下完整 argv/cwd/UTC 起止/raw/SHA 收据；4 个本方独立反例全部 0 mismatch。
- **限制声明**：
  - 本结论**仅适用于**上述固定同版本的完整 S1 范围，**不表示完整 T04 或产品验收通过**；
  - **不代判另一指定审者**，本轮未读取、未使用其任何材料；
  - **不授权** push / PR attach / CI / 合并 / 远端核验 / 发布；
  - 审查期间**未修改**任何源码、测试、fixtures、依赖、配置、锁或验收，**未执行**任何 Git 写操作；受审面在审前审后 `HEAD`、`git status --short`、保护 `AGENTS.md`、双锁文件与 base→product diff 全部**逐字节未变**；
  - 本方全部写入仅限：唯一报告文件、本方独占 ignored 运行目录 `test-results/t04-review-runtime/minimax/`（反例、raw、收据）以及 `test-results/t04-p3-repair/browser/review-minimax-r3/`（既有 probe 的唯一命名产物）；
  - **task ID 与原 turn 正式终态为 UNKNOWN**（见第 1 节），本方未自填、未编造、未以全局配置或原生 session 补查。

---

## 附：本方运行产物（均在本方独占 ignored 目录）

- `test-results/t04-review-runtime/minimax/metadata/`：`mm-r3-full-check-01.json`、`mm-r3-ssr-01.json`、`mm-r3-component-01.json`（本方工程验证收据；**不是** operator 设置/身份/输入实读证明）
- `test-results/t04-review-runtime/minimax/raw/`：对应三份 raw（5389 B / 423 B / 1037 B，SHA 与收据一致）
- `test-results/t04-review-runtime/minimax/counterexamples/`：`zod-unit-probe.mjs`、`d1-python-probe.py`、`d1-python-results.json`、`d1-ts-probe.ts`、`t09-provenance-check.py`、`t09-provenance-results.json`
- `test-results/t04-review-runtime/minimax/history/`：71 项旧 554 轮归档原件（逐成员字节+哈希已核）
- `test-results/t04-review-runtime/minimax/t09/`：19 项 T09 provenance 原件（逐成员字节+哈希已核）
- `test-results/t04-review-runtime/minimax/owner-raw/`：owner `owner-verification-raw.tar.gz` 的 51 成员展开（逐成员已核）

反例仅写于本方独占目录，未进入源码目录或原测试目录，未改变任何验收真值，未构成第二执行器/Store/公共 schema。
