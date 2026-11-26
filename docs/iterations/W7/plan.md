# Wave 7（`W7`）迭代更新计划：零代码底层本体概念沙盒与零售会员门店订单仿真体系

> **前置基准**：`feature/w6-ui-shell-harness` @ `8c16d5d7`（继承 `origin/develop` @ `bc76d036` 与 W6 双模分屏壳层、Design Harness）。
> **工作树与分支**：`.worktrees/W7-zero-code-foundations` · `feature/w7-zero-code-foundations`。
> **设计北极星**：`design/prototypes/OntoLearn-Studio-Prototype-v2.pen` 第 12 组标杆画板（`12A` `Td2Qm`、`12B` `XZzbj`、`12C` `EHJ8q`、`12D` `R7leMd`、`12E` `F72Kn`）与 `design-harness/`。
> **L1 隔离与契约红线**：严禁修改脏主目录 `OntoLearn-Studio`（`e6ed8101`）及任何既有冻结工作树；严禁修改 `docs/source-manifest.json` 锁定的 12 份归档文件（尤其是初版 `design/prototypes/OntoLearn-Studio-Prototype.pen` SHA-256 `55529367...`）；本迭代全部工程实现严格限定在 `apps/desktop/src/renderer/**`、`design/**`、`design-harness/**`、`docs/iterations/W7/**` 与 `tests/**`，**零触碰** `packages/contracts`、`packages/engine/src/**`、`apps/desktop/src/main/**`、`apps/desktop/src/preload/**` 与 `docs/prd/**`，确保 PR 审查分级保持 **`L1`**，所有零代码交互在渲染层编译为既有标准 `ChangeSet` / `OntologySession` / `Mapping` / `Quality` 契约请求。

---

## 一、已确认 `Steer` 与 `Concept` 核心设计决策（四大支柱）

### 1. 受众画像：完全零代码的业务分析师（BA）与产品经理（PM）

- **去技术语法遮挡**：默认新手视图下彻底隐藏裸 `<urn:...>` 命名空间、英文类与属性术语（`owl:Class` / `rdfs:Class` / `rdf:type`）、N3 字面量引号与数据类型后缀（`"36.00"^^xsd:decimal`），以及裸 `JSON.stringify` 键值快照。
- **业务母语第一界面**：优先以“Excel 宽表行列拆解”、“PRD 需求原句四色圈词”、“下拉自然语言造句器”和“三列表格业务可读变更预览”作为主操作界面；同时保留一键切换至 `标准 RDF/IRI 视图` 与折叠查看底层 RDF 三元组 / JSON 原文的能力，实现零代码直觉与严谨语义图谱的双向同源透明对照。

### 2. 底层本体元概念六步阶梯（`00 三元组与概念沙盒`）

将原本假设用户具备领域建模与技术背景的直接实操，前置拆分为循序渐进的 6 个零代码微关卡：

| 步骤      | 底层元概念                                                | 零代码教学载体与核心心智突破                                                                                       |
| :-------- | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `Step 01` | **万物皆三元组（S–P–O 原子事实）**                        | 将 `Excel` 单行宽表逐列拆解为独立 `[主语] — [谓语] → [宾语]` 积木，直观感受“加字段/加关系无需改整张表结构”。       |
| `Step 02` | **唯一身份 ID vs 显示名称（IRI vs Label）**               | 通过两个同名“王敏”（`#M-018` 黑金会员 vs `#M-209` 普通会员）与店长改花名（`#EMP-07` 阿杰 → Jie）建立稳定身份直觉。 |
| `Step 03` | **对象关系 vs 数值属性（圆节点 vs 方字面量）**            | 对比 `下单门店 → 静安旗舰店（可继续牵出店长的圆节点）` 与 `实付金额 → 36.00（到此为止的方盒子）`。                 |
| `Step 04` | **类（模具）vs 个体（实例）与上下位层级（`subClassOf`）** | 区分“黑金会员（概念模具）”与“王敏 `#M-018`（具体个体）”，并体会 `黑金会员 ⊂ 注册会员` 的规则自动继承。             |
| `Step 05` | **关系方向性与事件实体化（Anti-Pattern Clinic）**         | 针对 PRD 原句诊断“为什么不能只连 `王敏 —购买了→ 杨枝甘露`”，引导重构出独立事件实体 `门店订单 #SO-101`。            |
| `Step 06` | **显式断言 vs 规则推导 & 开放世界假设（SHACL 体检）**     | 区分“人工录入事实”与“规则推导标签（高流失风险待挽回会员）”，理解本体默认不把漏填当报错、需靠 SHACL 体检拦截脏行。  |

### 3. 双案例阶梯与双规模仿真数据集

- **Lv.1 零基础入门案例（新增推荐起点）：`知味茶饮 · 全渠道会员与门店订单履约`**
  - 统一命名空间前缀：`retail:`（映射标准 URI `urn:ontolearn:retail:`）。
  - 配套 4 张贴近 BA / PM 日常工作的仿真业务源表：
    1. `members`（小程序会员档案表）：含同名“王敏”冲突、黑金/普通等级、注册渠道、手机号缺失脏行；
    2. `stores_staff`（门店与店长台账）：含华东区域、直营/加盟门店、店长改名记录、悬空店长工号脏行；
    3. `orders`（全渠道订单流水）：含堂食/外卖渠道、实付金额负值异常、履约超时分钟数、关联商品明细；
    4. `complaints`（超时客诉与赔付单）：含客诉等级、免单券赔付状态、待回访标记。
  - **双规模仿真数据一键切换（`DualScaleDatasetSwitch`）**：
    - **微缩沙盒集（10 行精选）**：用于 `00 沙盒` 与 `01 建模` 初学阶段，图谱连线根根分明、一眼看清；
    - **真实压力集（80 行含脏数据）**：埋入同名同姓冲突、漏填所属门店、负实付金额、悬空店长工号与连续超时客诉会员，在 `02 数据映射 → 03 本体查询 → 04 质量与推导` 亲手验证“无需手写 SQL 与脚本即可批量揪出脏数据并自动推导待挽回名单”的工程杠杆。
- **Lv.2 进阶工程迁移案例（完整保留）：`智能工厂 · 设备运维与告警闭环`**
  - 完整保留既有 `offline-course-2` 与 `lx01` / `repair` / `classification` 全套课程资产、映射模板与查询用例，确保全部 37 条既有 E2E 回归测试及底层合约零破坏。

### 4. 交互架构组合（`Concept A+B + Concept C`）

- **`Concept A + B`（前置交互式概念沙盒 + 坏模型诊所）**：
  - 左侧 `核心工作台` 顶部新增前置关卡 **`00 三元组与概念沙盒`**（路由标识 `foundation`），内部提供 `[Excel 拆积木沙盒 | PRD 圈词与坏模型诊所]` 双模式，对应原型 `12B`（`XZzbj`）与 `12C`（`EHJ8q`）。
- **`Concept C`（正式工作台零代码辅助轮与可读 Diff）**：
  - **`01 本体构建`** 顶部增加分段开关 **`[零代码业务视图 (推荐) | 标准 RDF/IRI 视图]`**（对应原型 `12D` `R7leMd`）：
    - 零代码视图下将 `urn:...` 折叠为紧凑业务前缀胶囊（如 `retail:Order`），三元组录入区升级为可搜索下拉造句器 `[主体对象 ▾] — [关系/特征 ▾] → [关联对象 | 填写文字/数值]`（底层自动编码为标准 IRI 或带类型 N3 字面量）；
    - 变更预演区将原裸 `<pre>{JSON.stringify(state.prepared.rows, null, 2)}</pre>` 升级为三列 **`ReadableBusinessDiff`** 业务可读变更表（`变更动作 | 业务可读事实 | 影响说明`），并提供默认折叠的 `展开底层 RDF 三元组 / JSON 原文` 抽屉。
  - **`04 质量与推导`** 增加双规模数据集切换状态指示、零代码白话体验规则卡片与分步证据链展示（对应原型 `12E` `F72Kn`）。

---

## 二、分阶段实施清单（`W7-0` 至 `W7-4`）

### `W7-0`：原型 V2 第 12 组画板、Design Harness 沉淀与 W7 方案提交（本轮闭环）

- **交付物**：
  - `design/prototypes/OntoLearn-Studio-Prototype-v2.pen` 新增 `12A`–`12E` 五张 `1440×960` 标杆画板（`Td2Qm`、`XZzbj`、`EHJ8q`、`R7leMd`、`F72Kn`），复用 `UR7GQ`（`Component / PortalShell`）与 `aLI9i`（`Component / AppShell`）；
  - `design-harness/` 沉淀 W7 `Steer` 记忆、共享词汇表、渐进揭露交互模式与 `00 沙盒` 四态矩阵；
  - 正式仓内计划 `docs/iterations/W7/plan.md` 与外部控制副本。
- **退出验证**：`node scripts/verify-sources.mjs`（12/12 冻结文件零变更）、Prettier 格式化校验、`node scripts/check-design-harness.mjs` 通过、5 张 `.pen` 画板目视导出核查无重叠截断、`review-level` 非 `L2`。

### `W7-1`：双案例课程包与茶饮会员订单双规模仿真数据集

- **涉及文件**：
  - 新增 `apps/desktop/src/renderer/src/learning/scenarios/retail-membership-orders.ts`（含 `10 行微缩集` 与 `80 行脏数据压力集` 的 4 张表原始数据、预期业务词汇表、标准三元组对照答案与 SHACL/规则推导示例）；
  - 更新 `apps/desktop/src/renderer/src/learning/content.ts`、`apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx` 与 `learning.css`。
- **实施细节**：
  1. 在学习路线图页（`12A`）顶部新增 **双案例课程切换卡**：`Lv.1 知味茶饮 · 全渠道会员与门店订单（零代码推荐）` 与 `Lv.2 智能工厂 · 设备运维与告警闭环（进阶工程迁移）`。
  2. 为 `Lv.1` 渲染 `00 概念沙盒（Step 01–06）→ 01 本体建模 → 02 四表映射 → 03 业务查询 → 04 80 行体检与推导` 闯关路线，点击各微步骤可带参直达 `00 沙盒` 或 `01 工作台`。
  3. **向后兼容保护**：保持既有 `offlineCourse`（设备运维）数据结构与 `learning-center` 既有按钮/选择器完整可用，不破坏 `l1-learning-vertical.spec.ts` 与 `lq-query-learning.spec.ts`。
- **阶段验证**：新增数据集完整性与双规模行号/脏数据注入单元测试，`npm run typecheck && npm run build` 绿灯。

### `W7-2`：`00 三元组与概念沙盒` 与坏模型重构诊所（`12B` & `12C`）

- **涉及文件**：
  - 新增 `apps/desktop/src/renderer/src/foundation/`：`FoundationSandboxPage.tsx`、`ExcelTripleBuilder.tsx`、`PrdConceptClinic.tsx`、`LiveTripleMiniGraph.tsx`、`foundation-codec.ts`、`foundation.css`；
  - 更新 `apps/desktop/src/renderer/src/shell/shell-routing.ts`、`SidebarNav.tsx`、`App.tsx`。
- **实施细节**：
  1. 在 `SidebarNav` 的 `核心工作台` 组首位增加 **`00 三元组与概念沙盒`**（`data-testid="nav-workspace-foundation"`），在未打开项目时亦可用于无门槛概念预热（已打开项目时支持一键“将本步练习三元组写入项目草稿”）。
  2. 实现 `Step 01–06` 微关卡切换条与双标签模式 `[Excel 拆积木沙盒 | PRD 圈词与坏模型诊所]`：
     - **Excel 拆积木沙盒（`12B`）**：左侧渲染可点击单元格的茶饮表格（标亮同名“王敏”`#M-018`/`#M-209` 与改名店长），中部提供 `[主语 ▾] — [谓语 ▾] → [宾语 ▾]` 零代码积木拼装与即时微反馈，右侧实时生长双色 SVG 知识图谱（圆节点=对象个体 / 方盒子=文字数值 / 虚线框=规则推导标签）。
     - **PRD 圈词与坏模型诊所（`12C`）**：展示带四色下划线标注的业务需求片段（紫色=实体类、蓝色=对象关系、绿色=属性数值、橙色=业务事件/规则），右侧并排对比“❌ 常见坏模型（二元直连丢失时间/金额/多杯明细）”与“✅ 一键重构为标准事件实体模型（#SO-101 订单节点）”，重构完成后可通过既有 `OntologySession` 编码器直接写入当前项目或跳转 `01 本体构建`。
  3. **样式红线**：`foundation.css` 严禁出现任何裸 hex，全部引用 `tokens.css` 语义变量。
- **阶段验证**：单元测试覆盖 6 步微关卡状态推进、坏模型检测规则与图谱节点分类断言，加上 `node scripts/check-design-harness.mjs` 绿灯。

### `W7-3`：`01 本体构建` 零代码造句辅助轮、可读 Diff 与 `04 质量与推导` 仿真体验（`12D` & `12E`）

- **涉及文件**：
  - 新增 `apps/desktop/src/renderer/src/ontology/ZeroCodeTripleBuilder.tsx`、`ReadableBusinessDiff.tsx`、`rdf-display-adapter.ts`；
  - 更新 `apps/desktop/src/renderer/src/ontology/OntologyMainlinePage.tsx`、`OntologyPage.tsx`、`ontology.css`；
  - 更新 `apps/desktop/src/renderer/src/quality/QualityWorkspacePage.tsx`、`quality.css`。
- **实施细节**：
  1. 在 `01 本体构建` 顶部放置分段切换 **`[零代码业务视图 (推荐) | 标准 RDF/IRI 视图]`**：
     - **前缀胶囊折叠**：`urn:ontolearn:retail:Order` 在零代码视图显示为 `零售订单 (retail:Order)` 胶囊；
     - **零代码下拉造句器**：提供 `[选择主体对象 ▾] — [选择业务关系/特征 ▾] → [关联对象 ▾ | 填写文字/数值]` 与即时自然语言预览句（如“黑金会员王敏 #M-018 的 下单门店 指向 静安旗舰店 #S-01”）；通过纯函数 `rdf-display-adapter.ts` 无损编译为标准 IRI 或带类型 N3 字面量并回填至底层三元组状态；
     - **`ReadableBusinessDiff` 变更表**：将原裸 `JSON.stringify(state.prepared.rows, null, 2)` 替换为三列可读对比表（`变更动作 | 业务可读事实 | 影响说明`），下方保留可折叠的 `<details>` 抽屉用于核查原始 RDF 三元组 / JSON 行快照。
  2. **既有 E2E 选择器零破坏保护**：在标准 RDF/IRI 视图与兼容模式中完整保留既有输入框标签（`主体个体 IRI`、`属性 IRI`、`规范 RDF 对象`、`rdfs:Class`/`owl:Class`）及所有既定 `data-testid` / `role="status"` 契约，并在默认配置下确保所有存量 E2E 用例无需降级断言即可通过。
  3. **`04 质量与推导` 双规模仿真增强（`12E`）**：增加 `[微缩沙盒 10行 | 压力仿真 80行含脏数据]` 数据源快捷切换条与一键加载按钮，并在体检结果与推导事实旁呈现白话中文解释与证据链（如“实付金额小于 0”、“悬空店长引用”、“连续超时客诉 → 自动归入高流失风险待挽回会员”）。
- **阶段验证**：`rdf-display-adapter.ts` 编译/反解析往返与 `ReadableBusinessDiff` 渲染单测通过，`npm run check` 全绿。

### `W7-4`：确定性门禁扩展、属性测试、真实 Electron E2E 与双视口视觉验收

- **涉及文件**：
  - 更新 `scripts/check-design-harness.mjs` 与 `tests/unit/w6-design-harness-invariants.test.ts`；
  - 新增 `tests/unit/w7-zero-code-adapter.test.ts`（含 `fast-check` 属性测试）；
  - 新增 `tests/e2e/w7-zero-code-foundation.spec.ts`。
- **实施细节**：
  1. **属性测试（Property-based Testing）**：使用 `fast-check` 验证 `rdf-display-adapter.ts` 的双向编码往返守恒（Round-trip）、特殊引号/换行转义安全性以及无效数值拦截不变量。
  2. **确定性门禁扩展**：将 `foundation.css` 与新增组件纳入 `check-design-harness.mjs` 扫描范围（零裸 hex、禁止主工作台默吐未包装的裸 `JSON.stringify` `<pre>`），并完成正向全绿 + 负向违例样本反证。
  3. **真实 Electron E2E 与双视口渲染核验**：编写 `w7-zero-code-foundation.spec.ts` 端到端走通 `学习路线图 Lv.1 选茶饮案例 → 00 概念沙盒 Step 01–06 + 坏模型重构 → 01 零代码造句器与可读 Diff 提交 → 04 80 行脏数据体检与推导证据链`，同时在 `1440×900` 与 `390×844` 双视口抓取截图完成真实目视复核。
- **完整退出门禁**：
  - `npm run verify:sources`（12/12）
  - `node scripts/check-design-harness.mjs`
  - `npm run check`（ESLint + Prettier + TypeScript + Vitest + Vite Build + Ruff + Pytest 全绿）
  - `npm run test:e2e`（既有 37 条 + 新增 W7 E2E 全绿、零 Flaky）
  - `npm run package:dir && npm run release:hygiene`
  - `npm run review:level`（确认保持 `L1`）并经过 0% 自审独立复核后提 PR。

---

## 三、既有测试与契约非回归护栏

1. **零代码视图与存量 E2E 的兼容性策略**：
   - `OfflineCourse`（智能工厂设备运维）保留为独立可切换/兼容默认课程包，确保 `l1-learning-vertical.spec.ts`、`lq-query-learning.spec.ts` 等依赖设备运维任务 ID（`lx01` / `repair` / `classification`）的存量测试零改动或按显式路径平滑通过。
   - `OntologyMainlinePage` / `OntologyPage` 在提供 `零代码业务视图` 的同时，保留一键切回 `标准 RDF/IRI 视图` 的分段开关，所有既有 `IRI` / `rdfs:Class` / `owl:Class` 控件标识与 `data-testid` 原样维持。
2. **渲染层隔离与 L1 边界**：
   - 本迭代全部变更均不触及 Python 引擎校验逻辑、IPC 白名单、CSP 策略或 `@ontolearn/contracts` DTO Schema，确保安全边界与已过回归基线稳固无损。
