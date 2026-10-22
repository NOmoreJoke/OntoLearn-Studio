# T09-S1 round-1 独立完整对抗审查报告（ZCode / GLM-5.3）

- 报告日期：2026-10-23（Asia/Shanghai）
- 审查者：ZCode 独立只读审查任务（本轮新建，不继承旧短任务）
- 受审候选：T09-S1「离线内容、学习检查 reducer 与独立页面」
- 审查区间：approved base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → product `76596656908ed84e577e8202a602e3256d5febcc`（tree `8b646570108026a8deabe8330c548cab0280122d`），完整 55 文件区间，不缩水、不拼接 stage 原型
- 流程证据基线：d969 `d96924e715a1b2139a75b70aea40fc30ae1129fe`；本审查工作区 HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985`（product 之后仅追加 docs/流程证据，已核实 product..HEAD 仅 docs 路径）

## 1. 来源、身份与设置读回

| 项目 | 实际值 | 依据 |
| --- | --- | --- |
| 输入正文 | 粘贴附件 51699 bytes，SHA-256 `ebdaf40e51c09a602174a9cca2060934e53d376b7a48c2555927eef2565d922f`；与树内 `docs/reviews/T09/dispatch-20261022/s1-zcode/full-dispatch.md` 逐字节一致（shasum 双向核对） | 本轮实测 |
| 模型 | 运行环境自报 GLM-5.3（`account:bigmodel-individual-coding-plan/GLM-5.3`）；创建时 owner CUI 读回 modelUI=GLM-5.3、reasoning=最高、permission=完全访问（requiredEquivalent max/yolo） | 会话环境；`dispatch-runtime/s1-zcode/metadata/task-settings-receipt.json` |
| session/task ID | **无法验证**：创建回执记录时点 `actualSessionId/actualTaskId` 均为 null（incomplete launch 阶段），会话内部不可观测自身 ID；由 owner 以实际读回为准 | 同上；不自猜 |
| 思考等级/权限模式会话内读回 | **无法验证**（会话内部无该观测面）；采信 owner 创建回执与环境声明，不据此扩大职责 | 同上 |
| workspace 绑定 | cwd = `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-s1-zcode-review-7659665`（实测 `pwd`），与 `workspace-mapping.json` 的 actualCWD/报告路径一致；本报告写入约定路径 | 实测；映射文件 |
| 后台入口/版本/integrity 回执 | **无法验证**：冻结输入仅含 `inputs/background-route-snapshot.md`（SHA `9a2d722d…` 已核），本会话经用户前台粘贴任务发起，无后台入口回执可观测 | 按规则标注 |
| 对端 MiniMax | 冻结提示 `minimax-m31flash-input.md`（SHA `f1342191…`）仅登记身份，**未读取内容**；未读任何对端报告/运行状态/任务数据库/兄弟工作区 | 本轮纪律声明 |

## 2. 树、哈希与范围覆盖（审查前后一致性）

- **Git 实况**：detached HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985`（与回执一致）；`git status` 仅 `M AGENTS.md`（SHA `de15f6ce…` 当前版，按要求保持未暂存、未写回）+ 三个 dispatch 未跟踪目录。
- **base/product/process 分列**：base `5f910b52`（存在性核验）；product `76596656` tree `8b646570`（`rev-parse ^{tree}` 实测一致）；process d969 及 HEAD `72aa83a8` 独立列出；product..HEAD 差异仅为 docs/reviews、docs/iterations、round-1 冻结输入（19+13 文件，无产品源码）。
- **input-manifest.json 全量核对**：106/106 entries 逐条以 `git show <commit>:<path>` / 实际文件字节计算 SHA-256 全部吻合（脚本 `scratch/verify_manifest.py`，输出 `raw/manifest-verification.txt`）。`productChangedPaths`(55) 与 `git diff --name-only base product` 集合完全相等且全为新增。
- **full-source-bytes.json**：869/869 tracked 文件实际字节、sha256、HEAD blob 与记录全部一致；`git ls-files` 集合与记录集合相等（quotepath 修正后零差异）。
- **固定 fixture manifest**：`tests/fixtures/product-baselines/manifest.json` SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`（实测）；17 输入文件哈希 17/17 吻合；source PRD SHA `7586b2c4…` 与 base 提交内 PRD 实测一致。
- **审查前/后一致性**：32 个产品源码/数据路径两轮实测均与 product 提交字节相同（终检 drift NONE）；审查期间未改任何产品/测试/配置/依赖/锁文件，未 stage/commit/push/切分支。
- **范围覆盖（逐项，非摘要）**：① `content/learning/` 四文件全文读取（course 9 任务、glossary 23 术语、transfer-inputs 全文、checks.json 54 检查结构化全量+重点反例逐条）；② fixtures 17 输入全文/结构化读取（E.5 两产能八轮逐字段、cases 50 计划、coverage 50 原文、G-base/G-map-empty/G-behavior/CSV/RQ 全文）；③ verify 脚本+engine learning 三文件全文；④ 三个 pytest 文件全文（42 测试逐一归类）；⑤ UI 五文件全文+两个 vitest 文件全文（16+18 用例归类）；⑥ 产品 diff 内全部 docs/证据文件读取（status/recovery/verification/jobstore/learning-ui 三内审、handoff/contract/user-acceptance、controller/coordination/ui-controller 回执、operation-policy-receipt、verification-summary/baseline-verification、npm-check-ui-final 全文、两个首失败 gzip 原件解压 SHA 复核、两张截图 SHA+亲自视觉核验）。

## 3. 本轮实际运行与证据分类（严格区分）

全部在本工作区独立 runtime（node_modules/.venv 均本任务 setup 产物，回执 `metadata/setup-receipt.json`：npm ci --ignore-scripts exit0、uv sync --frozen exit0），`TMPDIR`/`UV_CACHE_DIR` 指向本任务 scratch/uv-cache，原始输出全部落 `dispatch-runtime/s1-zcode/raw/`。

| # | 命令（cwd=本工作区根） | 退出码 | 结果 | 原件 |
| --- | --- | --- | --- | --- |
| 1 | `python3 scripts/verify-product-baselines.py` | 0 | 17 文件/50 计划完整性与来源 hash 通过，`productRuntime: not-executed` | raw/verify-product-baselines.out |
| 2 | `uv run --frozen pytest packages/engine/tests/test_learning_baselines.py test_learning_service.py test_learning_jobstore_integration.py -q` | 0 | **42 passed**（11 fixture/reset+真实RDF解析+Store 重建、24 reducer 合成 adapter、7 真实 I04 stdio 通道） | raw/learning-pytest-r1.out |
| 3 | `npx --no-install vitest run learning`（未设 T09_HEADLESS_UI） | 0 | **18 passed | 16 skipped**（纯投影 18 项真实执行；浏览器 16 项恒 skip，与 runtime 无关） | raw/learning-vitest-r1.out |
| 4 | `T09_HEADLESS_UI=1 npx --no-install vitest run learning` | **1** | `browserType.launch: Executable doesn't exist`（chromium_headless_shell-1248 缺失）——实证「显式 1 缺匹配 runtime 是失败」，不得把 skip 报通过 | raw/learning-vitest-headless-noruntime.out |
| 5 | manifest/full-source-bytes/fixture 程序化核对（见 §2） | 0 | 106/106、869/869、17/17 全通过 | raw/manifest-verification.txt、raw/full-source-bytes-verification.txt |

**证据分类边界**：静态（哈希/全文读）与纯逻辑（18 vitest 投影）本轮真实执行；reducer 合成 adapter 24 项仅证 reducer 不证领域；I04 基础设施 7 项为真实 JobStore/stdio/test.atomic 探针、rollback-only 预览非业务确认；**16 项 headless 组件测试本轮未运行**（本任务无绑定浏览器 runtime，且禁止暗装；采信 d969 同版原件：`npm-check-ui-final.txt` SHA `210d3d9b…` 实测吻合、命令含 `T09_HEADLESS_UI=1`、664 Vitest/1094 pytest/lint/类型/构建/ruff exit0，且本轮已实证其 opt-in 语义）；两张截图 SHA 吻合且经我本人视觉核验（桌面 1440 布局完整、移动 390 单列无页面横向溢出；路径项容器内省略属截断非溢出）。**全量 `npm run check` 本轮未重跑**：worktree 与 product 字节一致、S1 定向套件已全部独立复跑通过、冻结同版原件已全文读取核 hash，符合「无变化不机械重跑」的派发要求。package/native/Electron/e2e/真人/生产：S1 范围外，未运行（派发亦禁止 Electron/产品启动/可见浏览器）。

## 4. 发现清单

**范围内阻断或降级缺陷：无。** 以下为本轮独立发现的三项 P3 观察项（不阻断 S1 有界验收，供后续迭代处置）：

- **S1-OBS-01（P3）导出防假成功守卫缺少自动化测试**。`apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx:308-325`（`sameContext(result.context) && result.exported` 才示成功，否则「报告尚未导出，请重试。」）与 `:486-494`（缺 `exportReport` 能力时禁用并提示「报告导出暂不可用。」）实现正确（本轮代码级核对），但 18 纯+16 headless 用例均未覆盖该路径；`learning-ui-contract.md` 的「报告仅实际导出成功回执才显示成功」声明目前只有代码没有测试钉住。建议接线 T10 前补一个 headless 用例（能力缺席提示 + exported:false 拒绝成功文案）。
- **S1-OBS-02（P3）两个迁移任务的 1/2 级提示文本完全相同**。`content/learning/course.json` 中 `transfer-repair`（hints[0]/[1]）与 `transfer-classify`（hints[0]/[1]）为同两条通用文案（「先判断要校验已有记录还是计算新分类。」「使用检查报告定位对象；查看事实来源而非只看显示名称。」），而 3/4 级是任务专属。无 PRD 违反（提示为实现约定，conventions.json 已声明），但低层级提示对两题区分度为零，属内容质量改进项。修复会改 manifest 哈希 → 需新候选。
- **S1-OBS-03（P3）checks.json 内联 oracle 与 E.5.json 的一致性无自动断言**。`content/learning/checks.json` 的 G-list-01 `capacities` 与 G-list-06 `independentReplays` 是 E.5.json `expected` 的完整内联副本；本轮程序化核验**当前逐字节相等**（含两次 replay 均 == expected/3），但没有任何测试断言该相等。漂移风险被双层缓解（两文件均被 manifest SHA `aaaef2c0…` 钉住；E.5.json 自身被 `test_e5_literal_sets_from_prd_and_complete_order_history` 以 PRD 原文钉住），故仅 P3：建议在测试中加一条 `checks["G-list-01"].expected.capacities == E.5.expected` 断言以防未来同版维护失误。

对派发「需求与重点反例」逐项独立核对的结论（均为**通过**，证据见 §2/§3 与下节）：G.0 全对象/关系/名称、字符串 001 身份（mapping `keyType:"string"`、CSV 原样、测试断言）、空初始工单/事件；G-behavior T1.P 类型化 `false`、X/Y 同优先级按 ID 序、B-06 X→Y 冻结快照单通知、B-10 E-M4→E-M3 实例内 1→2 + 双通知、B-11 相同值幂等去重 + 双通知；E.5 两产能×4 轮完整 facts/orders/consumption/triggered/actionTrace/scheduledFutureEvents/指标/重放契约（产能3 backlog 1/2/3/4、累计 3/6/9/12；产能4 全清 4/8/12/16），且 checks 内联副本与文件 oracle 相等（非互相复制的孤立 oracle）；M-03 撤 002 受管事实保留 002 人工备注、M-04/G-list-09 同版 `equipment-updated.csv`（G-list-09 relink 钉 SHA `f513469a…`）；规则/行为/实现/语义版本四元固定；Q-01 仅 A01、Q-02 空、V-01 仅 003 minCount、R-01 依据含 A01+R-risk、R-05 无二阶结果、B-04 空行为前推导、B-05/B-09 competing-write、B-01 幂等 repeatChanges 空、B-02 notTriggered 带原因；「计划 vs 实际执行」区分（50 cases 全部 `input-and-expectation-prepared-runtime-pending`，verify() 拒绝其他状态、返回 not-executed）；reset 每次 verify 全 manifest 且 deepcopy 独立导出（含变异不串测、路径穿越拒绝）；seed 计划不含 expected/replay/推导（测试断言 `"expected" not in payload`）；点号 ID（`G-base.ontology` 等）经真实 canonical Project DTO/依赖向量/stdio/重开七项验证；LearningService 仅收 context/check 匹配 + `provenance=="persisted-domain-tool"` + status succeeded 的 typed evidence，集合排序/序列保序、True≠1（`type() is int` 拒 bool、JSON canonical 比较）、事实集合与事件/动作/轮次顺序不混淆；提示/Agent 辅助单调不降、完整示范与 Agent 全辅助不改独立迁移、操作完成与独立迁移分离、报告白名单投影；UI 同 context 高版本降级/等版冲突/矛盾新版不回退旧 pass/非法水位 fail-closed 可恢复/同 attempt 换 input/五类迟到/提示未保存不泄露/能力缺席/注入文本纯渲染/双尺寸（代码+18 纯测本轮实跑+16 headless d969 同版原件+截图亲验）；页面无 Node/fs/shell/通用 IPC/模型/持久化（import 面与 App/main/preload 零引用实测）、固定中文错误、React 文本渲染、renderer floor 非权威（契约明示 owner 账本责任）；7 项真实 I04 为 rollback-only 预览/test.atomic 专用（product-mode 断言 UNSUPPORTED_CAPABILITY），内部确认 metadata 非人类点击；G-list-02 仍为 exactFile/exactPointer（PARENT-02 保留未虚报）；A-10 三固定反例带 scopeNote 不冒充 T08 评估集。文档面：未发现把占位/计划/合成证据说成产品能力的误导声明；user-acceptance 为空记录未造样本；DOC-01/02 口径已按 d969 修正。

## 5. 历史意见逐项处置（本轮独立重判，不复制旧结论）

| 编号 | 本轮判定 | 本轮依据 |
| --- | --- | --- |
| CONTENT-01 | **已关闭** | transfer 正文仅给目标/数据（`transfer-inputs.json` facts 无「缺哪个/答案」；102 缺名与供水泵、201 来源判定均只在各自 level-4）；`test_retracted_mapping…no_answer_in_body` 断言含跨题防泄露（供水泵/102/201 不入对方正文与提示） |
| CONTENT-02 | **已关闭** | M-04 与 G-list-09 均引用 `equipment-updated.csv`；G-list-09 relink 步骤钉 `sourceSha256 f513469a…` 与实际文件 SHA 相等（实测） |
| CONTENT-03 | **已关闭** | E.5 基线 cases 均绑 `behaviorVersion: e5-behaviors-1`，与 E.5.json 一致（程序化核对+测试断言） |
| CONTENT-04 | **已关闭** | M-03 manualFacts=002 note；预期 facts 保留该备注且 002 无其他事实（我逐条读 expected + 测试断言） |
| CONTENT-05 | **已关闭** | E.5 八轮（两产能）每轮含 actionTrace（每事件 1→2）与 scheduledFutureEvents（12/8/4/0 递减）；当前 manifest `aaaef2c0…` |
| INFRA-01 | **已关闭** | baselines.py 点号 ID；7 项真实通道断言 canonical Project、依赖向量、重开、重复 operation 幂等；首失败原件（4 failed/3 passed）解压 SHA 与记录一致 |
| UI-01 | **已关闭** | `observeRecord/projectionRecord` 单调水位+等版冲突；`newer-lower/same-version-conflict` headless 用例（d969 同版原件）+ 我对 presentation.ts 代码核对与 18 纯测实跑 |
| UI-02 | **已关闭** | 先 `recordHint` 回执校验后 `setHint`；无 context 迁移题四级全拒；缺能力/保存失败不泄露；对应 headless 用例在 d969 原件 |
| UI-03 | **已关闭** | `currentFloor` 按 project/task/attempt 聚合（跨 inputVersion）；hint4→input2 独立记录拒绝用例在 d969 原件；代码核对一致 |
| UI-04 | **已关闭** | 矛盾新版令 `conflictVersion` 置位、投影 undefined、不回退旧 pass（`contradictory-newer` 用例+代码核对） |
| UI-05 | **已关闭** | 无效水位不入 floor、fail-closed、合法高版本可恢复（纯测 `blocks invalid owner values…` 本轮实跑通过） |
| DOC-01 | **已关闭** | d969 `recovery.json`（SHA `3a05647a…`）指向 learning-ui-verification.json/765；旧 765 内 recovery 为历史层不覆盖（我按角色分别核 hash，未以物理 HEAD 覆写旧角色） |
| DOC-02 | **已关闭** | d969 明确「未设 1 恒 skip、设 1 缺 runtime 是 launch 失败、sandbox 仅配置+成功、viewport/文件尺寸分记」；本轮命令 3/4 直接实证前两条 |
| PARENT-01/02/03 | **保留（未关闭，且未虚报关闭）** | 见下节父缺口；本轮确认 S1 未宣称关闭它们 |

**父功能缺口（独立列示，S1 Pass 不关闭任何一项）**：真实 T02–T07 领域执行器与阶段证据契约（检查仍返回 pending-dependency）；T01 durable 学习记录/跨 attempt 辅助账本与产品案例生命周期（renderer floor 明示非权威）；T00/T01 业务命名 bridge 与 App 正式路由（实测零接线）；课程资源与 fixture 入包（repo-root 读取 ≠ 包内资源）；T08 真实完整代做来源与指定评估集；T10 实际报告/项目包导出联验；Windows/macOS 双平台与至少 5 名真实新手 80% 原口径真人验收；CI/远端核验/push/PR/merge 与 57 项 P0 总门。以上在 status/handoff/验收方案中均如实申报为未完成，无夸大。

## 6. 最终结论

**通过**——限「T09-S1 同版有界范围」：base `5f910b52` → product `76596656`（tree `8b646570`）区间内，固定 17 输入/50 计划内容与 PRD V0.6 FR-003/100–105、9.4、11.2、12.1 及附录 C/D/E/G 的固定语义逐项吻合；verify/reset 隔离、reducer 归因不可洗白、I04 真实基础设施边界、独立学习页面的投影防护与组件证据均经本轮静态+定向运行独立复核成立；d969 同版 fullcheck/headless/截图原件完整且与受审字节一致。范围内未发现阻断/必验缺失：三项 P3 观察项（§4）不构成门禁条件，headless 组件验收以 d969 同版原件+本轮 opt-in 语义实证采信。关键身份中 session/task ID 等不可观测项已按规则标「无法验证」，但不属「重要证据不足」——候选与证据链完整性由可核验哈希闭环支撑。本通过**不**延伸至父 T09 模块、正式接线、打包、双平台、真人验收或任何发布门（§5 父缺口全保留）。

## 7. 终态声明

- 本报告为该任务实际终态产物，已写入约定路径 `docs/reviews/T09/round-1/zcode-glm53.md`；报告 SHA-256 由 owner 实际读取时核验（本会话不自引用哈希）。
- 审查期间：未修改任何产品/测试/配置/依赖/锁/固定输入；未提交、推送、切分支、合并或建 PR；未运行 Electron/e2e/native/HMR/产品启动/可见浏览器/凭据操作；未读对端提示内容、对端报告、任务数据库、全局配置或兄弟工作区；未新增付费/额度消费/平台确认绕过；仅写本报告与本任务 raw/scratch/metadata。
- 终检（报告落盘前）：HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985` 未变；git status 与启动时同构（AGENTS.md M 未暂存 + 3 个 dispatch 目录）；32 产品路径与 product 提交字节零漂移。raw 原件 4 份 + 核对输出 3 份保留于 `dispatch-runtime/s1-zcode/raw/`，scratch 含核对脚本与临时目录，均如实保留。
- 后续 push/PR/CI/merge 由开发线按总控 lease 决定；同版双方（本报告与 MiniMax M3.1-Flash）均明确通过、全部意见有处置之前，不得进入合并门。
