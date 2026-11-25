# Wave 6（`W6`）迭代更新计划：双模菜单分屏、右侧宽度释放与 Design Harness 视觉精修

> **前置基准**：`origin/develop` @ `bc76d0365a0c8dc4c381900b5bb8282f98000918`（Waves 0–5 全代码波次已合入）。
> **工作树与分支**：`.worktrees/W6-ui-shell-harness` · `feature/w6-ui-shell-harness`。
> **设计北极星**：`design/prototypes/OntoLearn-Studio-Prototype-v2.pen` 与 `design-harness/`。
> **隔离与契约红线**：严禁修改脏主目录 `OntoLearn-Studio`（`e6ed8101`）及任何既有冻结工作树；严禁修改 `docs/source-manifest.json` 锁定的初版 `design/prototypes/OntoLearn-Studio-Prototype.pen`；本迭代纯属渲染层（`apps/desktop/src/renderer/**`）与设计文档/测试升级，**不改动** `packages/contracts`、`packages/engine/src/**`、`apps/desktop/src/main/**` 与 `apps/desktop/src/preload/**`（保持 PR 审查分级为 `L1`）。

---

## 一、改版核心目标（已确认 `Steer` 决策）

1. **终结单页瀑布流，采用 Concept A + B 双模闯关菜单**：
   - 将原平铺于同一 `<main>` 下的宣传区、引擎诊断、学习中心、项目库全家桶、三栏工作台、过期“待开发”模块海报与模型设置，拆分为互相独立的一级全屏视图（`projects` / `learning` / `workspace` / `settings`）。
   - 左侧菜单按认知顺序排列 **`01 本体构建 → 02 数据映射 → 03 本体查询 → 04 质量与推导 → 05 行为定义 → 06 情景推演 → 07 迁移练习 → 08 导出与成果`**，并实时展示各关课程完成状态；从独立全屏“学习路线图”点击任一关卡可直达对应工作台并聚焦导师任务卡。
2. **合并右侧双栏，释放中间编辑器宽度**：
   - 将原并排挤占横宽的 `MentorPanel`（课程导师）与 `AgentPanel`（AI 助手）收拢到单一 `320px` 可收起辅助栏的 **`[课程导师 | AI 助手]` 双 Tab** 中，点击顶栏开关可一键收起至 `0px`，使 `1440px` 桌面视口下的中间编辑区扩展至约 `1200px`。
   - 将“检查点恢复”与“后台任务状态”收纳为顶栏按需弹出的抽屉，取代旧版页面中部大块堆叠与跨千像素 `scrollIntoView`。
3. **同步落地 `design-harness/` 与全工作台视觉精修**：
   - 基于 `design-harness/` 语义 Token、间距阶梯与 10 条硬性禁区，清零渲染层 CSS 硬编码裸 hex，新增确定性样式/护栏单测，完成全部子工作台与门户页的视觉密度、单一主动作层级与 `1440px` / `390px` 响应式抽屉适配。

---

## 二、分阶段实施清单（`W6-0` 至 `W6-4`）

### `W6-0`：原型 V2 升级与 Design Harness 冷启动（已先行闭环）

- **交付物**：
  - `design/prototypes/OntoLearn-Studio-Prototype-v2.pen`（升级 `Component / PortalShell` 与 `Component / AppShell`，保留全部 32 屏实例覆写兼容性；新增第 11 组 `11 V2*` 共 5 张标杆画板，含学习路线图、导师 Tab、AI 助手 Tab、侧栏收起宽屏查询画布及 `390px` 移动端抽屉态）。
  - `design-harness/` 四层设计底座（`foundations/`、`intelligence/`、`components/`）。
  - 本迭代计划 `docs/iterations/W6/plan.md`。
- **退出验证**：`npm run verify:sources`（12/12 冻结归档零变更）、Prettier 格式化校验、5 张 V2 原型画面目视渲染核查。

### `W6-1`：顶层分屏路由与 Concept A+B 双模菜单重构

- **涉及文件**：
  - `apps/desktop/src/renderer/src/App.tsx`
  - 新增 `apps/desktop/src/renderer/src/shell/shell-routing.ts`、`apps/desktop/src/renderer/src/shell/SidebarNav.tsx`
  - 整合 `apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx`（对齐 `learning-center` 路线图视图）
- **实施细节**：
  1. 在 `App.tsx` 引入显式一级视图状态 `primaryView: 'projects' | 'learning' | 'workspace' | 'settings'`：
     - 未打开项目时默认 `'projects'`；成功打开/创建项目或从学习路线图选择“开始案例/去实操”时切入 `'workspace'`；
     - 四大一级视图互斥渲染（Portal 视图与 Workspace 视图绝不同屏纵向堆叠）。
  2. `SidebarNav` 分为三组：
     - **门户总览**：`我的项目`（`data-testid="nav-project-library"`）、`学习路线图`（`data-testid="nav-learning-center"`）；
     - **核心工作台（01–08）**：`01 本体构建`（`ontology`）→ `02 数据映射`（`mapping`）→ `03 本体查询`（`query`）→ `04 质量与推导`（`quality`）→ `05 行为定义`（`behavior`）→ `06 情景推演`（`scenario`）→ `07 迁移练习`（聚焦 `transfer-repair` / `transfer-classify` 并切 `quality`）→ `08 导出与成果`（`transfer`），每项展示课程状态胶囊/圆点，点击仍走既有 `selectWorkspace` 准入锁与脏草稿拦截确认；
     - **系统与诊断**：`模型与隐私设置`（`data-testid="nav-model-settings"`）及底部紧凑型 `本地引擎状态` 条。
  3. 清理 `App.tsx` 底部陈旧的 `#modules`（“六个模块 · 待开发”）静态占位区，更新页脚说明文本。
- **阶段验证**：`npm run typecheck && npm run build && npx vitest run tests/unit/b1a-lifecycle-admission.test.ts tests/unit/view-navigation.test.ts`。

### `W6-2`：右侧 `[课程导师 | AI 助手]` 合并侧栏与顶栏抽屉化

- **涉及文件**：
  - 新增 `apps/desktop/src/renderer/src/shell/UnifiedAssistantRail.tsx`
  - 新增 `apps/desktop/src/renderer/src/shell/TopContextBar.tsx`
  - 新增 `apps/desktop/src/renderer/src/shell/WorkspaceDrawers.tsx`
  - 更新 `apps/desktop/src/renderer/src/App.tsx` 与 `apps/desktop/src/renderer/src/learning/MentorPanel.tsx`
- **实施细节**：
  1. `TopContextBar`（56px）：展示当前视图上下文、当前项目名与 `data-testid="selected-project-version"`、全局状态反馈条、引导/辅助模式指示、`检查点恢复` 抽屉开关、`后台任务 (N)` 抽屉开关以及 `data-testid="mentor-panel-toggle"` 右侧栏收放开关。
  2. `UnifiedAssistantRail`（320px / 收起 0px）：顶部提供 `role="tablist"` 的 `课程导师` 与 `AI 助手` 双 Tab，切换时保留两边组件未提交草稿与已展开提示；点击“继续当前任务”或从学习路线图跳转时自动打开右侧栏并切到 `课程导师` Tab；点击“查看检查点恢复”改为直接打开顶栏检查点抽屉。
  3. `WorkspaceDrawers`：按需展开 `ProjectCheckpointRestorePanel` 与后台 `durable-job` 列表，减少主工作区垂直占用。
- **阶段验证**：`npm run typecheck && npm run build && npx vitest run tests/unit/l1-mentor-panel.test.ts tests/unit/w3b-agent-panel.test.ts tests/unit/t08-sidebar.test.ts`。

### `W6-3`：Design Harness 语义 Token 落地、确定性样式门禁与全模块视觉精修

- **涉及文件**：
  - `apps/desktop/src/renderer/src/tokens.css`、`apps/desktop/src/renderer/src/style.css`
  - `project/project.css`、`learning/learning.css`、`learning/mentor.css`、`agent/agent-sidebar.css`、`ontology/ontology.css`、`mapping/mapping.css`、`query/workspace.css`、`query/typed-results.css`、`quality/quality.css`、`behavior/behavior.css`、`scenario/scenario.css` 及对应 TSX 空白/错误态文案与主按钮层级
  - 新增 `tests/unit/w6-design-harness-invariants.test.ts`
- **实施细节**：
  1. 在 `tokens.css` 补全 `design-harness/foundations/colors.md`、`typography.md`、`icons-and-motion.md` 中定义的全部语义 CSS 变量，并清理各业务 CSS 中的硬编码裸 hex。
  2. 在 `tests/unit/w6-design-harness-invariants.test.ts` 建立确定性护栏：扫描 `apps/desktop/src/renderer/src/**/*.css`（排除 `tokens.css`）零裸 hex、扫描 `App.tsx` 零“待开发”过期占位、校验 `tokens.css` 必需变量完备，并执行正向全绿 + 负向违例样本反证（防假绿）。
  3. 对 8 大子工作台及门户视图逐一精修：统一卡片边距与表格密度、确保每屏唯一最高权重主按钮（PRD §8.3）、补齐 `390px` 移动端顶部汉堡抽屉与底部主动作可达性、确认 `@media (prefers-reduced-motion: reduce)` 生效。
- **阶段验证**：`npm run check` 全绿。

### `W6-4`：单测与 36 条真实 Electron E2E 回归适配、双视口截图验收与 L1 独立复核

- **必须对齐的既有测试选择器与行为契约**：
  1. **首屏引擎健康条与项目库顺序**（`tests/unit/b1a-lifecycle-admission.test.ts:99-116`、`tests/e2e/desktop.spec.ts:21-47`、`tests/e2e/csp-lifecycle.spec.ts:61`）：门户 `'projects'` 首屏保留紧凑型本地引擎健康条（含 `id="health-title"` 与 `检查本地引擎` 按钮，位于 `data-testid="project-library"` 之前并在 `1024×720` 首屏可见）；进入 `'workspace'` 后自动让位给工作区，并在侧栏底部提供引擎状态入口。
  2. **项目库切换与状态提示**（12+ 个 E2E 文件读取 `getByTestId('project-library').getByRole('status')`）：在 `'projects'` 视图内创建/打开项目时保持原有 `role="status"` 提示文本；已进入 `'workspace'` 后如需再次切换/管理项目，通过点击 `data-testid="nav-project-library"` 返回项目库，并按需同步更新对应 E2E 的导航前置步骤（绝不删减任何业务断言）。
  3. **学习中心与导师/助手/模型设置入口**（`tests/e2e/l1-learning-vertical.spec.ts:263-267`、`tests/e2e/w3b-agent-and-b2.spec.ts`）：点击 `data-testid="nav-learning-center"` 切入全屏 `'learning'` 视图；点击 `data-testid="nav-model-settings"` 切入全屏 `'settings'` 视图；工作台内测试交互按需切换右侧 `[课程导师 | AI 助手]` Tab。
- **完整退出门禁**：
  - `npm run verify:sources`（12/12）
  - `npm run check`（ESLint + Prettier + TypeScript + Vitest + Vite Build + Ruff + Pytest 全绿）
  - `npm run test:e2e`（全部 36 条真实 Electron E2E 零失败、零 Flaky）
  - 真实渲染截图视觉验收（`1440px` 桌面全屏/收起右侧栏 + `390px` 移动端抽屉）
  - `npm run package:dir` 与 `npm run release:hygiene`
  - 0% 自审 `L1` 独立复核通过后提 PR 合入 `origin/develop`。

---

## 三、交付边界说明

- 本 `W6` 迭代聚焦 **UI 壳层结构、菜单组织、右侧宽度释放与视觉精修**，不改变 `newFRPasses = 0` 与外部发布 HOLD `H1..H10` 状态；完成 `W6` 后将显著改善 `H1`（5 名真实新手独立可用性测试）的上手体验。
