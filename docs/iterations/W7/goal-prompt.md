# Wave 7（`W7`）`/goal` 长程自治目标提示词

> **用法**：在 Antigravity 对话框输入 `/goal` 后，将下方代码块完整粘贴并发送，即可驱动 Agent 在独立工作树内按阶段完成 `W7-1` 至 `W7-4` 全部开发、属性测试、真实 Electron E2E 与 L1 退出门禁验收。

```text
请以严谨的高可信 Agentic Engineering 模式，在独立隔离工作树中完整实现 OntoLearn Studio Wave 7（`W7-1` 至 `W7-4`：零代码底层本体概念沙盒 + 知味茶饮会员门店订单双规模仿真体系 + `01 本体构建` 零代码辅助轮与可读 Diff）。

## 一、绝对隔离红线与工作目录（违反任意一条立即停止并报错）
1. **唯一允许改动的 Repo 工作目录**：
   `/Users/kyle/Documents/工作/知爻/本体/.worktrees/W7-zero-code-foundations`（当前分支 `feature/w7-zero-code-foundations`）。
2. **绝对禁区**：
   - 严禁修改脏主目录 `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（HEAD 必须保持 `e6ed8101`）；
   - 严禁修改 `.worktrees/W6-ui-shell-harness`（必须保持 `8c16d5d7` 干净）及任何其他工作树；
   - 严禁修改 `docs/source-manifest.json` 锁定的 12 份归档文件（尤其是初版 `design/prototypes/OntoLearn-Studio-Prototype.pen`）；
   - **严格保持 PR 审查分级为 `L1`**：只允许改动 `apps/desktop/src/renderer/**`、`scripts/check-design-harness.mjs`、`design-harness/**`、`docs/iterations/W7/**` 与 `tests/**`。绝对禁止修改 `packages/contracts/**`、`packages/engine/src/**`、`apps/desktop/src/main/**`、`apps/desktop/src/preload/**` 与 `docs/prd/**`。
3. **运行环境准备**：
   - 所有命令执行前必须注入 Node 24 与项目 `.venv`：
     `export PATH="$(pwd)/.venv/bin:/Users/kyle/.nvm/versions/node/v24.15.0/bin:$PATH"`
   - 若新工作树尚未存在 `node_modules` 或 `.venv`，先在不改动任何源码的前提下在 `.worktrees/W7-zero-code-foundations` 内完成 `npm ci` 与 `.venv` 就绪准备（或复用既有 Python 环境并确保 `node -v` 为 `v24.x`、`python --version` 可运行 pytest）。

## 二、开工前必读权威设计文档
开工编写任何业务代码前，先在 `.worktrees/W7-zero-code-foundations` 完整读取以下设计北极星与护栏：
1. `docs/iterations/W7/plan.md`（Wave 7 总体架构与分阶段计划）
2. `docs/iterations/W7/feature-spec.md`（组件拓扑、数据契约、编解码协议与既有 E2E DOM 兼容红线）
3. `design-harness/README.md`、`design-harness/components/patterns.md`、`design-harness/components/screens.md`、`design-harness/foundations/colors.md`
4. `scripts/check-design-harness.mjs`

## 三、三大防踩坑 DOM 与门禁铁律（编码时时刻核对）
1. **学习路线图向后兼容**：`#learning-center` 必须保持包含 `'离线课程 · 无需模型 API'` 与 `'设备运维'`，`data-testid="learning-path-task"` 必须严格维持 `9` 个（仅归 `offlineCourse.tasks`），新增 `Lv.1 知味茶饮` 6 步入口必须使用独立的 `data-testid="w7-foundation-step-card"`。
2. **`01 本体构建` 与 `.ontology-diff` 严格契约**（参考 `tests/e2e/ui-observation.ts` 与 `t02-fr200-fr201.spec.ts`）：
   - `.ontology-page` 内禁止使用 `<input type="submit|button|reset">`，禁止在 `<section>` 上挂载 `aria-labelledby`，不得修改存量表单的 `<label>` 文本或给受测按钮/输入框覆写冲突 `role`/`aria-label`；
   - `.ontology-diff` 内以三列表格渲染 `ReadableBusinessDiff`，并将 `JSON.stringify(state.prepared.rows, null, 2)` 置于 `<details><summary>展开底层 RDF 三元组 / JSON 原文</summary><pre>...</pre></details>` 之中——**整个 `.ontology-diff` 区域内必须且只能存在这唯一 1 个 `<pre>` 标签**，且完整保留既有数量与校验段落。
3. **Design Harness 确定性门禁**：
   - `apps/desktop/src/renderer/src/**/*.css`（除 `tokens.css` 外）严禁任何裸 hex 色值；
   - 渲染层源码与仿真数据（如客诉状态）**严禁出现 `待开发` 或 `待实现` 子串**（请使用 `待回访`、`处理中`、`已赔付`）；
   - `shell/` 与新增 `foundation/` 内禁止 `setTimeout`/`setInterval`/`requestAnimationFrame`/`requestIdleCallback` 与 `@ts-ignore`/`@ts-nocheck`。

## 四、分阶段执行里程碑（按顺序推进并做阶段提交）
1. **里程碑 1（`W7-1`）**：实现 `apps/desktop/src/renderer/src/learning/scenarios/retail-membership-orders.ts`（确定性无随机的 10 行微缩集 & 80 行含 4 类指定脏数据的压力集）及 `DualTrackRoadmapHeader.tsx`，接入 `App.tsx` 学习路线图门户并配齐单测。通过近源检查后显式 `git add` 提交 `feat(w7-1): add retail dual-scale simulation datasets and roadmap track`（带 `Verified: check`）。
2. **里程碑 2（`W7-2`）**：实现 `apps/desktop/src/renderer/src/foundation/`（`FoundationSandboxPage`、`ExcelTripleBuilder`、`PrdConceptClinic`、`LiveTripleMiniGraph`、`foundation.css`），更新 `shell/SidebarNav.tsx` 常驻 `00 三元组与概念沙盒` 入口（`data-testid="nav-step-00"`）与 `App.tsx` 视图接入，支持 6 步概念闯关及事件实体化 `#SO-101` 一键重构带入草稿。过检查后提交 `feat(w7-2): add 00 foundation triple sandbox and PRD concept clinic`。
3. **里程碑 3（`W7-3`）**：实现 `rdf-display-adapter.ts`、`ZeroCodeTripleBuilder.tsx`、`ReadableBusinessDiff.tsx` 接入 `OntologyMainlinePage.tsx`（含 `[零代码业务导引 | 标准 RDF/IRI 视图]` 切换）；实现 `RetailSimulationBanner.tsx` 并扩展 `QualityWorkspace.tsx` 支持 `retail-micro-10` 与 `retail-stress-80` 仿真体检与白话证据链。过检查后提交 `feat(w7-3): add zero-code ontology builder, readable diff, and 80-row simulation`。
4. **里程碑 4（`W7-4`）**：
   - 扩展 `scripts/check-design-harness.mjs` 与 `tests/unit/w6-design-harness-invariants.test.ts`（并做 `--stdin` 违例反证）；
   - 新增 `tests/unit/w7-zero-code-foundation.test.ts`（使用 `fast-check` 验证双向编解码 Round-trip、转义安全与幂等性）；
   - 新增 `tests/e2e/w7-zero-code-foundation.spec.ts` 端到端走通茶饮入门闭环并在 `1440×900` 与 `390×844` 双视口截图；
   - 跑通全部退出门禁并提交 `test(w7-4): add property tests, harness guardrails, and W7 electron E2E`。

## 五、自愈熔断与退出验收门禁（全部实跑通过才算结束）
- **3 轮自愈熔断**：同一构建/测试失败连续自动修复最多 3 轮；第 3 轮仍失败立刻停机保存现场并汇报根因，严禁删减业务断言、加硬编码 `sleep`、加 `.skip` 或放宽门槛换绿。
- **必须全部通过的终验门禁**（最终代码修改后实跑并附实测输出摘要）：
  1. `node scripts/verify-sources.mjs`（12/12 通过）
  2. `node scripts/check-design-harness.mjs`（正/负向反证全过）
  3. `npm run check`（ESLint + Prettier + TypeScript + Vitest + Vite Build + Ruff + Pytest 全绿）
  4. `npm run test:e2e`（全部存量 E2E + 新增 `w7-zero-code-foundation.spec.ts` 全绿，零 Flaky）
  5. `1440×900` 桌面与 `390×844` 移动端真实 Electron 截图目视检查无重叠、无溢出、四态清晰
  6. `npm run package:dir && npm run release:hygiene`（PASSED）
  7. `node scripts/review-level.mjs`（确认分级保持 `L1`，未触发 `L2`）
  8. 确认脏主目录 `OntoLearn-Studio` HEAD 仍为 `e6ed8101`、`.worktrees/W6-ui-shell-harness` 仍干净在 `8c16d5d7`。
```
