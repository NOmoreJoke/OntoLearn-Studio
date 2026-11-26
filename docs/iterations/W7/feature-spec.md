# Wave 7（`W7`）具体功能开发方案（`feature-spec`）

> **关联迭代计划**：[docs/iterations/W7/plan.md](./plan.md)
> **目标工作树与分支**：`.worktrees/W7-zero-code-foundations` · `feature/w7-zero-code-foundations`（基于 `e1b59045`）
> **原型北极星**：`design/prototypes/OntoLearn-Studio-Prototype-v2.pen` 第 12 组（`12A` `Td2Qm`、`12B` `XZzbj`、`12C` `EHJ8q`、`12D` `R7leMd`、`12E` `F72Kn`）
> **架构等级红线**：严格保持 PR 审查分级为 **`L1`**（仅改动 `apps/desktop/src/renderer/**`、`scripts/check-design-harness.mjs`、`design-harness/**`、`docs/iterations/W7/**` 与 `tests/**`），严禁修改 `packages/contracts`、`packages/engine/src/**`、`apps/desktop/src/main/**`、`apps/desktop/src/preload/**`、`docs/prd/**` 与 `docs/source-manifest.json`。

---

## 一、全局状态与模块拓扑总览

```text
apps/desktop/src/renderer/src/
├── App.tsx                                        # 一级分屏路由 + 00 沙盒接入 + 学习路线图双案例卡
├── shell/
│   ├── shell-routing.ts                           # 扩展导航/工作台分发辅助（保持 COURSE_NAV_STEPS 01-08 契约）
│   └── SidebarNav.tsx                             # 左侧常驻 00 三元组与概念沙盒入口 (data-testid="nav-step-00")
├── learning/
│   ├── DualTrackRoadmapHeader.tsx                 # [新增] 12A 双案例阶梯卡 + 6 步底层概念微关卡入口
│   └── scenarios/
│       └── retail-membership-orders.ts            # [新增] 知味茶饮 Lv.1 词表、4 表结构、10 行微缩集 & 80 行压力集
├── foundation/                                    # [新增] 00 三元组与概念沙盒模块（12B & 12C）
│   ├── foundation-types.ts                        # 6 步微关卡状态、积木槽位与 PRD 四色词段类型
│   ├── FoundationSandboxPage.tsx                  # 顶层沙盒页（Step 01-06 + 拆积木/坏模型诊所切换）
│   ├── ExcelTripleBuilder.tsx                     # 12B Excel 原表点选 + 零代码积木造句
│   ├── PrdConceptClinic.tsx                       # 12C PRD 四色圈词 + 二元直连 vs 事件实体化对比重构
│   ├── LiveTripleMiniGraph.tsx                    # 声明式 SVG 图谱（圆节点/方字面量/虚线推导边）
│   └── foundation.css                             # 仅使用 tokens.css 语义变量（零裸 hex）
├── ontology/
│   ├── rdf-display-adapter.ts                     # [新增] 前缀折叠、零代码 N3 双向编解码、ReadableBusinessDiff 投影
│   ├── ZeroCodeTripleBuilder.tsx                  # [新增] 12D 零代码概念向导 + 下拉自然语言造句器
│   ├── ReadableBusinessDiff.tsx                   # [新增] 12D 三列表格可读 Diff + 单一 <pre> 原文抽屉
│   └── OntologyMainlinePage.tsx                   # 接入 [零代码业务导引 | 标准 RDF/IRI 视图] 与 ReadableBusinessDiff
└── quality/
    ├── RetailSimulationBanner.tsx                 # [新增] 12E 10/80 行仿真切换、4 类异常摘要与白话推导证据链
    └── QualityWorkspace.tsx                       # 接入 retail-micro-10 / retail-stress-80 样本预设
```

---

## 二、五大功能模块开发规格

### 模块 A：双案例课程与知味茶饮双规模仿真数据集（`W7-1`）

1. **数据源文件**：新建 `apps/desktop/src/renderer/src/learning/scenarios/retail-membership-orders.ts`
   - 命名空间常量：`export const RETAIL_NS = 'urn:ontolearn:retail:'`，前缀简写 `retail:`。
   - 核心导出类型：
     - `export type RetailDatasetScale = 'micro10' | 'stress80'`
     - `export type RetailSourceTableId = 'members' | 'stores_staff' | 'orders' | 'complaints'`
     - `export type RetailVocabularyItem = { iri: string; compactIri: string; zhLabel: string; kind: 'class' | 'objectProperty' | 'dataProperty' | 'individual'; domain?: string; range?: string; datatype?: 'string' | 'zhText' | 'decimal' | 'integer' | 'boolean'; plainHint: string }`
     - `export type FoundationMicroStepId = 'step-01' | 'step-02' | 'step-03' | 'step-04' | 'step-05' | 'step-06'`
     - `export type RetailTableRow = { table: RetailSourceTableId; rowId: string; cells: Record<string, string | number | null>; anomalyTag?: 'missing_store' | 'negative_amount' | 'dangling_manager' | 'churn_target' | 'homonym' | 'renamed_staff' }`
   - **10 行微缩沙盒集（`micro10`）**：确定性固定 10 条跨 4 表精选行，必须覆盖：
     - 会员表 `members`：同名“王敏”冲突对（`#M-018` 黑金会员 vs `#M-209` 普通会员）；
     - 门店店长表 `stores_staff`：静安旗舰店 `#S-01`（华东区·直营），店长 `#EMP-07`（显示名曾为“阿杰”现改“Jie”）；
     - 订单流水 `orders`：事件订单 `#SO-101`（多杯同单：`杨枝甘露 + 茉莉奶绿`，实付 `36.00`，外卖履约超时 `25` 分钟）；
     - 客诉赔付单 `complaints`：客诉单 `#CP-301`（对应 `#SO-101`，已触发超时免单券赔付，状态 `已赔付` / `待回访`）。
   - **80 行脏数据压力集（`stress80`）**：**严禁使用 `Math.random()`**，必须由确定性数组/生成器构造精确 **80 条**跨 4 表流水，且精确注入以下 4 类体检靶标：
     1. **必填缺失（3 行）**：3 笔 `orders` 行缺失 `storeId`（触发 SHACL `minCount 1` 拦截）；
     2. **数值越界（2 行）**：2 笔 `orders` 行 `paidAmount < 0`（如 `-12.00`，触发 SHACL `numericRange >= 0` 拦截）；
     3. **悬空引用（2 行）**：2 笔 `stores_staff` 行指向不存在的店长工号 `#EMP-999`；
     4. **规则推导靶标（4 名会员）**：4 名 `retail:BlackGoldMember` 在华东区门店关联超时客诉，驱动规则引擎推导为 `retail:ChurnRiskMember`（高流失风险待挽回会员）。
   - **合规文案禁区**：全文件所有数据字符串中**严禁出现 `待开发` 或 `待实现` 子串**（避免触发 `check-design-harness.mjs` 的 `no-stale-placeholders` 门禁）；客诉未闭环状态统一用 `待回访`、`处理中`、`已赔付`。

2. **双案例学习路线图（`12A`）**：
   - 新建 `apps/desktop/src/renderer/src/learning/DualTrackRoadmapHeader.tsx`，嵌入 `App.tsx` 中 `#learning-center` 顶部（`primaryView === 'learning'`）：
     - 双案例切换卡：`Lv.1 知味茶饮 · 全渠道会员与门店订单（零代码入门推荐）`（`data-testid="learning-track-retail"`）与 `Lv.2 智能工厂 · 设备运维与告警闭环（工程进阶）`（`data-testid="learning-track-equipment"`）。
     - 在 `Lv.1` 面板渲染 6 步概念微关卡卡片（使用 `data-testid="w7-foundation-step-card"`），点击任意卡片切入 `00 三元组与概念沙盒` 并选中对应 `Step 01..06`。
   - **硬性兼容不变量 #1（保护 `l1-learning-vertical.spec.ts:263-268`）**：
     - `#learning-center` 必须在 `1024×720` / `1440×900` 视口内通过 `toBeInViewport()`；
     - `#learning-center` 文本必须持续包含 `'离线课程 · 无需模型 API'` 与 `'设备运维'`；
     - `data-testid="learning-start-example"` 按钮与既有 `offlineCourse.tasks` 列表保持完整；
     - `data-testid="learning-path-task"` **必须严格保持恰好 `9` 个**（新增 `Lv.1` 微步骤卡片不得复用 `learning-path-task` 作为 `data-testid`）。

---

### 模块 B：`00 三元组与概念沙盒` 与坏模型诊所（`W7-2`）

1. **侧栏与路由接入（`shell/` 与 `App.tsx`）**：
   - `SidebarNav.tsx` 新增常驻导航链接 **`00 三元组与概念沙盒`**（`data-testid="nav-step-00"`）：
     - 无论 `hasProject` 为 `true` 或 `false`，用户均可随时点击进入概念沙盒进行零代码预热；
     - 既有的 `COURSE_NAV_STEPS`（`01`–`08`、`data-testid="nav-step-01"`..`08`）及 `stepMetaForWorkspace`、`workspaceForLearningTask` 映射保持 100% 不变；
     - `SidebarNav` 在未打开项目时点击 `nav-step-00` 切入 `primaryView = 'foundation'`（或无项目沙盒态），打开项目后亦可作为工作台内同级视图切换，且需确认 `tests/unit/w4-renderer-workspaces.test.ts` 的 `tree()` 遍历绿灯。

2. **沙盒组件拆分（`apps/desktop/src/renderer/src/foundation/`）**：
   - `FoundationSandboxPage.tsx`（`data-testid="foundation-sandbox-page"`）：
     - 顶部提供 `Step 01` 至 `Step 06` 微关卡步进条、模式切换分段器 `[Excel 拆积木沙盒 | PRD 圈词与坏模型诊所]` 与当前案例规模标识；
     - 维护每个微关卡的完成状态（纯 UI 会话内练习进度）及当前构建的沙盒三元组集合。
   - `ExcelTripleBuilder.tsx`（对齐原型 `12B` `XZzbj`）：
     - 左侧展示可点选的 `知味茶饮` 源表行（点击行内主语/属性/客体单元格自动高亮并填入中间积木槽；点击同名“王敏”行时弹出对比提示卡片说明 `#M-018` 与 `#M-209` 为两个独立身份）；
     - 中间提供 `[主体对象 ▾] — [关系/特征 ▾] → [关联对象/数值]` 积木槽位、验证与“加入右侧图谱”动作，校验逻辑区分圆节点对象（IRI）与方框数值（字面量）。
   - `LiveTripleMiniGraph.tsx`（纯声明式 SVG，无命令式 DOM/定时器）：
     - 使用语义 CSS 变量绘制双色区分图谱：圆角椭圆节点代表对象个体（如 `会员 #M-018`、`门店订单 #SO-101`、`静安旗舰店 #S-01`），直角方框代表不可继续下挂的字面量数值（如 `"36.00"`、`25 分钟`），虚线高亮边表示规则推导结论（如 `高流失风险待挽回`）。
   - `PrdConceptClinic.tsx`（对齐原型 `12C` `EHJ8q`）：
     - 左侧展示带四色下划线标注的知味茶饮 PRD 原文段落（点击“实体类 / 对象关系 / 属性数值 / 规则约束”词段高亮解释其本体角色）；
     - 右侧上下对照渲染“❌ 常见坏模型：`王敏 —购买了→ 杨枝甘露`（二元边导致多杯同单、实付金额与下单时间无法挂载）”与“✅ 标准事件实体重构：`#M-018 —下单了→ #SO-101 门店订单`”，提供 `一键重构为标准订单实体模型` 交互，若当前已打开项目且会话就绪，额外提供 `将本组三元组带入 01 本体构建草稿` 按钮（直接跳转到 `ontology` 并预填/交由 `OntologySession` 走真实预览确认流程，绝不绕过 Diff 直写数据库）。
   - `foundation.css`：100% 使用 `apps/desktop/src/renderer/src/tokens.css` 语义 CSS 变量，零裸 hex。

---

### 模块 C：`01 本体构建` 零代码造句辅助轮与 `ReadableBusinessDiff`（`W7-3a`）

1. **纯函数编解码与业务投影适配器（`apps/desktop/src/renderer/src/ontology/rdf-display-adapter.ts`）**：
   - `compactIri(iri: string, prefixes = DEFAULT_PREFIXES): string` 与 `expandCompactIri(value: string, prefixes = DEFAULT_PREFIXES): string`：
     - 支持 `retail:`（`urn:ontolearn:retail:`）、`learning:`（`urn:ontolearn:learning:`）、`rdf:`、`rdfs:`、`owl:`、`xsd:`；未匹配任意已知前缀时原样返回，保证**幂等与无损**。
   - `encodeZeroCodeObject(input: ZeroCodeObjectInput): string` 与 `decodeRdfObjectToZeroCode(n3Object: string): ZeroCodeObjectValue`：
     - `mode === 'entity'`：要求非空合法 IRI，输出 `<${expandedIri}>`；
     - `mode === 'zhText'`：严格转义 `\`、`"`、`\n`、`\r`、`\t` 后输出 `"${escaped}"@zh`；
     - `mode === 'string'`：严格转义后输出 `"${escaped}"`；
     - `mode === 'decimal'`：校验 `/^-?\d+(?:\.\d+)?$/`，输出 `"${normalized}"^^<http://www.w3.org/2001/XMLSchema#decimal>`；
     - `mode === 'integer'`：校验 `/^-?\d+$/`，输出 `"${normalized}"^^<http://www.w3.org/2001/XMLSchema#integer>`；
     - `mode === 'boolean'`：输出 `"true"^^<http://www.w3.org/2001/XMLSchema#boolean>` 或 `"false"^^...`；
     - `decodeRdfObjectToZeroCode`：精确逆向还原上述 6 类表示，对于任意无法归类的复杂 N3 字符串返回 `{ mode: 'raw', rawValue: n3Object }` 无损透传。
   - `summarizePreparedDiffRows(rows, ontologyView)`：将 `state.prepared.rows` 中每条 `{ resource, before, after }` 翻译为：
     - `action`: `'新增' | '修改' | '移除'`
     - `resourceLabel`: 前缀折叠后的可读主体/资源标识
     - `businessFactSummary`: 业务可读中文摘要句（如 `门店订单 #SO-101 的 实付金额 设为 36.00`）
     - `impactNote`: 影响说明（如 `新增实例断言；仅写入待确认事务，需人工确认生效`）

2. **零代码导引区与双视图融合（`OntologyMainlinePage.tsx` & `ZeroCodeTripleBuilder.tsx`）**：
   - 顶部增加分段切换器 `[零代码业务导引 (推荐) | 标准 RDF/IRI 视图]`（`data-testid="ontology-view-mode-toggle"`）。
   - `ZeroCodeTripleBuilder.tsx`：
     - 从当前项目已定义实体 + `retail-membership-orders` 业务词表自动聚合下拉候选项；
     - 用户通过 `[选择主体对象 ▾] — [选择业务关系/特征 ▾] → [关联对象 ▾ | 填写文字/数值]` 拼接自然语言事实句并实时看到中文预览句，点击 `填入并预览新增事实` 时调用 `encodeZeroCodeObject` 生成规范 RDF 参数并复用 `OntologyMainlinePage` 的 `preview('add')` 事务通道（经过 `session.prepare(plan)` 生成完整 `ChangeSet` 预览）。
   - **硬性兼容不变量 #2（保护 `t02-ontology-mainline.spec.ts`、`t02-fr200-fr201.spec.ts`、`l1-learning-vertical.spec.ts` 及 `ui-observation.ts`）**：
     1. 在 `<section className="ontology-page" aria-label="本体项目编辑">` 内，**严禁**渲染 `<input type="submit|button|reset">`、**严禁**在任何 `<section>` 上使用 `aria-labelledby`、**严禁**在受测 `<button>` / `<input>` / `<textarea>` 上增加与标签冲突的 `role` 或 `aria-label`（`ui-observation.ts` 的 `snapshotElements` 会对这些 DOM 标记 fail-closed 报错）；
     2. 原生标准表单控件（`类型`、`类声明`、`稳定 IRI`、`英文标识`、`主体个体 IRI`、`属性 IRI`、`规范 RDF 对象`、`预览定义修改`、`预览新增事实`、`读取当前项目`）**必须继续保持现有 `<label>` 文本与可读状态**；切至 `标准 RDF/IRI 视图` 时折叠零代码导引区，切至 `零代码业务导引` 时导引卡置于独立引导容器内，与下方标准表单互不遮挡、不改名既有表单；
     3. 在 `<section className="ontology-diff" aria-label="完整事务差异">` 内，渲染 **`ReadableBusinessDiff`**（三列业务对比表：`变更动作 | 业务可读事实 | 影响说明`），并将其下的原始 JSON 放入折叠抽屉 `<details className="raw-diff-drawer"><summary>展开底层 RDF 三元组 / JSON 原文</summary><pre>{JSON.stringify(state.prepared.rows, null, 2)}</pre></details>`：**`.ontology-diff` 内必须保留且仅保留这唯一的 1 个 `<pre>` 标签**，且原段落文本 `全部 {state.prepared.rows.length} 项；分段顺序、长度、SHA 与完整文档已核对。` 原样保留，确保 `t02-fr200-fr201.spec.ts` 的 `actual.pre.length === 1` 与 `JSON.parse(pre[0])` 校验零回归。

---

### 模块 D：`04 质量与推导` 双规模仿真与白话证据链（`W7-3b`）

1. **仿真预设扩展（`apps/desktop/src/renderer/src/quality/QualityWorkspace.tsx` & `RetailSimulationBanner.tsx`）**：
   - 在既有 `SamplePreset` 类型新增 `'retail-micro-10' | 'retail-stress-80'`（保留原有 `'rdfs-trigger' | 'rule-chain-unsupported' | 'order-independent' | 'current-draft'` 不变）。
   - `RetailSimulationBanner.tsx`：提供 `[微缩沙盒 10行 | 压力仿真 80行含脏数据]` 切换按钮及一键运行入口，调用真实 Python 引擎样本测试或项目质量校验接口，输出：
     - **4 类脏数据体检摘要卡**：缺失下单门店订单（3 笔）、负实付金额订单（2 笔）、悬空店长工号门店（2 家）、已识别高流失风险待挽回黑金会员（4 名）；
     - **白话推导证据链卡片**：将命中的规则条件（前提 1：黑金会员身份 + 前提 2：华东区订单 + 前提 3：触发超时客诉赔付 → 结论：`高流失风险待挽回会员`）以分步自然语言卡片呈现。

---

### 模块 E：确定性门禁、属性测试与真实 Electron E2E（`W7-4`）

1. **确定性门禁增强（`scripts/check-design-harness.mjs` & `tests/unit/w6-design-harness-invariants.test.ts`）**：
   - 保持并扩展全 `apps/desktop/src/renderer/src/**/*.css` 零裸 hex 检查（含新增 `foundation.css`）；
   - 扩展检查规则：`apps/desktop/src/renderer/src/foundation/` 下严禁出现 `setTimeout`/`setInterval`/`requestAnimationFrame`/`requestIdleCallback` 与 `@ts-ignore`/`@ts-nocheck`；
   - `OntologyMainlinePage.tsx` 中 `.ontology-diff` 区域不得退化回直接无包装展示裸 `<pre>`（要求必须存在 `<ReadableBusinessDiff` 调用且 `<pre>` 被 `<details>` 包裹）；
   - 必须通过正向全量扫描 + `--stdin` 负向违例拦截双重反证。
2. **单位测试与属性测试（`tests/unit/w7-zero-code-foundation.test.ts`）**：
   - 使用 `fast-check` 对 `rdf-display-adapter.ts` 执行 4 项性质验证：
     - **Round-trip（往返守恒）**：`decodeRdfObjectToZeroCode(encodeZeroCodeObject(input))` 对合法 `entity`/`zhText`/`string`/`decimal`/`integer`/`boolean` 与原值等价；
     - **转义安全**：任意包含 `"`、`\`、`\n`、`\r`、`\t` 的随机中文/英文业务文本编码后不破坏引号边界且能无损解码还原；
     - **幂等性（Idempotency）**：`compactIri(compactIri(x)) === compactIri(x)`、`expandCompactIri(expandCompactIri(x)) === expandCompactIri(x)`；
     - **异常守卫**：非法小数/整数输入明确抛错或返回校验错误，不静默拼出无效字面量。
   - 对 `retail-membership-orders.ts` 验证：`micro10` 行数为 `10`、`stress80` 行数为 `80`、4 类异常标注条数精确匹配、零 `待开发`/`待实现` 违禁占位词。
3. **真实 Electron E2E 与双视口视觉核验（`tests/e2e/w7-zero-code-foundation.spec.ts`）**：
   - 使用 Playwright + 真实 Electron 应用端到端走通：`学习路线图` 切换至 `Lv.1 知味茶饮` → 点击进入 `00 三元组与概念沙盒` 完成 Step 01 拆积木与 `#SO-101` 坏模型重构 → 新建项目进入 `01 本体构建` 使用零代码造句器新增茶饮订单三元组，核验三列表格 `ReadableBusinessDiff` 并展开底层原文完成提交 → 进入 `04 质量与推导` 运行 `80 行压力仿真` 验证推导结论与证据链；
   - 在 `1440×900` 桌面视口与 `390×844` 移动视口保存实机截图并通过视觉检查确认无重叠、无横向溢出、四态完备。
