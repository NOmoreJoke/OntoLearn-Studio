# T04 Q3 修复交付记录（2026-11-09）

## 会话与授权

| 项               | 值                                                                                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 作者会话 SID     | `59149c4208539963ebc7435c470a050c`（同 Q3 原作者，ROOT 续接派发）                                                                                         |
| 本轮修复执行模型 | ZCode · **GLM-5.3-Flash**（官方 UI 实切，ROOT `model-readback.json` 记录 `uiObservedAfter: GLM-5.3-Flash 最高`，完全访问）                                |
| 原候选作者模型   | GLM-5.3（历史运行记录如实保留，不冒称 Flash）                                                                                                             |
| 授权凭据         | ROOT 修复票 `iteration-control/2026-10-21-weekly-release/execute-20261109/q3-author/repair-ticket.md`；用户已授权按调整计划执行 P0/P1                     |
| 独立对审终态     | MiniMax-M3.1-Flash / high · SID `mvs_609f0d5111a84a53a93f94f734abeebd` · **ConditionalPass**（条件 C-1…C-6），报告与 report.json 原件封存于 `q3-minimax/` |
| 修复证据目录     | `iteration-control/2026-10-21-weekly-release/execute-20261109/q3-author/repair01/`                                                                        |

## 候选序列（全部本地，无 push / PR / CI / merge）

| 提交                    | tree           | 内容                                                                  |
| ----------------------- | -------------- | --------------------------------------------------------------------- |
| base `02888871`         | `8807f9c9`     | develop 含 PR#22 Q1+Q2                                                |
| 原产品 `a2708ee2`       | `73fcbb7a`     | Q3 增量（= 保全 ffc6fc35 补丁逐字节）                                 |
| 原交付 `a9de75a4`       | `d09e81ce`     | 产品 + 6 验证文档（ConditionalPass 受审对象，原样保全不 reset/amend） |
| **修复候选 `cd470d39`** | **`346fab4e`** | 本轮产品+测试普通提交（3 文件 +112/−5）                               |

ROOT 已于 2026-11-09T01:26:25Z 独立实采 `root-preformal-source-seal.json`（1443 tracked 实际字节 / git blob / 磁盘可执行 mode 全部匹配，clean），该 seal 仅为正式 full check / E2E 之前实采。

## F-01…F-11 处置表

| #    | 严重度 | 处置                                                                                                                                                                                                                                                                                                                                      | 落点                                |
| ---- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| F-01 | Medium | **已修**：SVG `<title>` 改单表达式模板字符串；新增真实 TSX SSR 标题完整文本断言 + `console.error` 探针零触发断言                                                                                                                                                                                                                          | `QueryResultPanel.tsx`；图单测例 11 |
| F-02 | Medium | **已修**：`mappingState` 仅自有属性查找（`Object.hasOwn`，继承键一律 `null`）；新增契约有效 `constructor`/`__proto__` 负例（先断言 DTO 有效）与 JSON.parse 显式自有属性正例（保留字不被一刀切拒绝）                                                                                                                                       | `result-graph.ts`；图单测例 12、13  |
| F-03 | Low    | **已更正**：交付索引 Panel 行数改 `+275/−69`，注明 344 = 总变动行数（与 `git diff --numstat 02888871 a2708ee2` 一致）                                                                                                                                                                                                                     | 交付索引文件表                      |
| F-04 | Low    | **已更正**：精确 diff 口径分列 = `git diff 02888871 a2708ee2`（43747 B / 1085 行）；6 文档 = `a2708ee2→a9de75a4`（70142 B / +1342）；base→原交付全量 113889 B（14 路径 +2253/−69）。数字全部由 git 实测，未沿用报告文字                                                                                                                   | 交付索引标识表                      |
| F-05 | Low    | **已记账**：交付索引「未测项与风险」逐条列出 Mimosa `inconclusive`/`partial`、7/8 路径、`typed-results.css` 未纳入、两新文件 baseline 不可读、`model_calls=0`、`runtime_verification=not_performed`、`rules_version=unavailable`、`finding_count=0` 不等于安全通过、两次提交 `scanner_enobufs` 放行（本轮修复提交亦复现，同样不宣称安全） | 交付索引风险项 5                    |
| F-06 | Low    | **已修（票选最小方案）**：合法来源检查移到锚过滤之前，`omittedRecords` 统一为文案所称全输入非墓碑口径、同一记录最多计一次；锚外合法记录不成边亦不计数；墓碑不成边；graph limits 未动。新增计数断言（锚内不完整来源 / 锚外不完整来源 / 锚外合法不成边不计数 / 字面量 / 墓碑）                                                              | `result-graph.ts`；图单测例 14      |
| F-07 | Low    | **挂账**：不加 `useMemo`、无性能改动、无性能实测，不声称可感知或量化改善；登记为后续基准验证项                                                                                                                                                                                                                                            | 交付索引风险项 7                    |
| F-08 | Low    | **挂账**：保留现有明确截断提示与事实记录 ID 行为，登记缺就地全文入口的后续可用性项，不虚构可用的完整值跳转                                                                                                                                                                                                                                | 交付索引风险项 8                    |
| F-09 | Low    | **登记备查**：个人提交邮箱属仓库级身份卫生，非本 Q3 产品缺陷；不改 Git 历史 / 作者全局设置                                                                                                                                                                                                                                                | 本表                                |
| F-10 | 边界   | **保留**：打包态图区 / CSP 未专项验证，历史 CSP 文档仅适用旧产物；登记后续批次门禁                                                                                                                                                                                                                                                        | 本表 + 交付索引风险项 2             |
| F-11 | 边界   | **保留**：真实 mapping→facts 物理运行链仍为单测 / SSR 级证据；不得表述为映射链已验收；F-02 端到端可达性同受此边界限制                                                                                                                                                                                                                     | 本表 + 交付索引风险项 1             |

## 修复内容（3 文件，+112/−5）

- `apps/desktop/src/renderer/src/query/QueryResultPanel.tsx`（+1/−3）：F-01 title 单表达式。
- `apps/desktop/src/renderer/src/query/result-graph.ts`（+6/−2，共 8 行变动）：F-02 `Object.hasOwn` 自有属性查找；F-06 来源检查前移。
- `tests/unit/t04-result-graph.test.ts`（+105）：新增 4 例（14 例总数；原 10 例零删改）。首败说明：例 14 初版夹具误把锚 D 当非锚对象，首败日志 `graph-unit-silent-false.log` 如实保全，夹具修正（D→C）随候选一并提交。

既有 E2E 零改动（票授权了增量但本批无需）；未改共享供给、依赖、锁、配置、timeout/retry/skip、控制门禁。

## 验证与证据（两段如实分列）

### 第一段：修复预检（未提交树上运行，不冒充候选运行）

树状态 = 已改未提交（HEAD 仍 `a9de75a4`）。含真实首败及修复后重跑：

| 命令                                                                                        | 退出码                          | 日志                                        |
| ------------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------- |
| `npx vitest run --silent=false tests/unit/t04-result-graph.test.ts`（首败：例 14 夹具错误） | 1                               | `graph-unit-silent-false.log`（保全不覆盖） |
| 同上（夹具修正后）                                                                          | 0，14/14，React title 错误 0 条 | `graph-unit-silent-false-run2.log`          |
| `npx vitest run --silent=false tests/unit/t04-empty-results.test.ts`                        | 0，8/8                          | `empty-unit.log`                            |
| `npm run verify:sources`                                                                    | 0                               | `verify-sources.log`                        |
| `PATH=Node24:.venv npm run check`                                                           | 0（2026/2026 + engine 3798）    | `check-full.log`                            |

### 第二段：正式同版验证（冻结候选 `cd470d39` 上运行）

签名绑定口径：**8 条命令 × 运行前/后各一份 × SHA256 字节与 index-mode 两类清单 = 32 份签名文件**，逐一比对候选基准全部相同、0 不匹配。图正式日志 Start at 为 01:26:17Z，早于 ROOT seal 01:26:25Z；图/空结果/源校验依据各自前后 SHA/index 清单绑定，不将 ROOT seal 倒写为此前置。ROOT 实际 mode 采样仅在正式 check/E2E 之前；作者 lstat 在正式 check 后、E2E 前，与候选逐一相同（1443 文件全部 `-rw-r--r--`）。JSON 两次 startTime 分别 01:34:04.396Z 与 01:34:49.772Z；console 日志未记录精确起始时刻。Node24 显式 PATH（`/Users/kyle/.nvm/versions/node/v24.15.0/bin`）+ 本树 `.venv`。

| 命令                                                                                                  | 退出码 | 结果                                                                                                                                        | 日志 / 退出码文件                                       |
| ----------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `npx vitest run --silent=false tests/unit/t04-result-graph.test.ts`                                   | 0      | **14/14**；React `<title>` 错误计数 **0**（修复前 53）                                                                                      | `graph-unit-final.log` / `.exit`                        |
| `npx vitest run --silent=false tests/unit/t04-empty-results.test.ts`                                  | 0      | **8/8**（Q1+Q2 无回滚）                                                                                                                     | `empty-unit-final.log` / `.exit`                        |
| `npm run verify:sources`                                                                              | 0      | 12 个归档源核对通过                                                                                                                         | `verify-sources-final.log` / `.exit`                    |
| `PATH=… npm run check`                                                                                | 0      | lint/format/typecheck 0 警告；**2026/2026** 单测；build 通过；engine **3798 passed / 50 skipped / 1 warning**（既有 warning，与原候选一致） | `check-final.log` / `.exit`                             |
| `npm run test:e2e -- tests/e2e/t04-query-variants.spec.ts --output=<repair01>/e2e-artifacts/variants` | 0      | **6/6**（原 5 例 + 图场景全部保留；1 worker / 0 retry / 30s 未改）                                                                          | `e2e-variants-final.log` / `.exit`                      |
| `npm run test:e2e -- tests/e2e/t04-query-workspace.spec.ts --output=…/workspace`                      | 0      | **1/1**（保存→重开全链）                                                                                                                    | `e2e-workspace-final.log` / `.exit`                     |
| `npx playwright test …variants… --reporter=json`（补充 JSON 报告）                                    | 0      | stats `expected:6, unexpected:0, flaky:0`                                                                                                   | `e2e-variants-report.json` / `e2e-variants-json.exit`   |
| `npx playwright test …workspace… --reporter=json`（补充 JSON 报告）                                   | 0      | stats `expected:1, unexpected:0, flaky:0`                                                                                                   | `e2e-workspace-report.json` / `e2e-workspace-json.exit` |

附件保全：共 4 次 E2E 运行：console（npm script）两次、JSON 报告（npx playwright）两次；四个输出目录共 4 个 `.last-run.json`，workspace 两次各 2 截图，共 4 文件、两对字节相同；JSON 两次共有 31 个内嵌附件（variants 28 + workspace 3，全部带内嵌 body）。全过无失败 → 按 `trace: retain-on-failure` 无 trace。实际产物照实盘点，不虚构。构建产物 pin：`build-out-pin.txt`（`apps/desktop/out` 5 文件 SHA256，清单哈希 `192a08e1…`）。环境指纹：`environment.txt`（Darwin 27.0.0 arm64 / Apple M5 Pro / Node v24.15.0 / npm 11.12.1 / Python 3.12.12 / candidate `cd470d39` / tree `346fab4e` / porcelain 0）。

## 边界（继续有效，不得升级表述）

1. 本批只覆盖 Q3 修复；不构成 FR-403 整体结算、发布通过、Windows/Linux 通过、打包态通过。
2. 真实映射链证据层级不变（单测 / SSR 级）。
3. 全部运行证据 darwin arm64 单机。
4. Mimosa：截至 `6f7e651e` 已实际观察到 **三次**修复相关提交（`cd470d39`、`bd05bd72`、`6f7e651ef0`）均 `scanner_enobufs` 兼容放行；后续提交的实际回执以当时 hook 输出为准并记录于 repair01——不据此宣称安全；独立安全复核由 ROOT 安排的 MiniMax 复核承担（对新候选 `cd470d39`）。
5. 推送 / draft PR / 完整 CI / merge 仍待 ROOT 另票；本地分支未 push。

## 待 ROOT

- 对新候选 `cd470d39` 独立复核（可交 MiniMax）；
- 确认接收后另行授权远端动作；
- `repair01/delivery.json` 与 `README.md` 为机读 / 人读交付入口。
