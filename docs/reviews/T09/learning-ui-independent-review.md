# T09 学习组件独立内审

2026-10-21，Asia/Shanghai。

## 结论与身份

**当前组件范围通过独立内审，无未关闭的阻断问题。**此结论覆盖私有学习页面、投影保护、静态课程消费和组件测试；不代表领域工具、学习记录持久化、产品路由、正式报告或真人学习验收已完成，也不替代指定双模型外审。

- 审查者：当前 T09 聊天的独立 Codex 子 agent `t09_prd_audit`，未冒充 ZCode 或 MiniMax 指定审查。
- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-learning-baselines`。
- 分支：`feature/weekly-t09-learning-baselines`。
- 批准集成 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 本次 UI 前置 T09 检查点：`6f6264bd6c090e54abf1919157e1a1127c8916ba`。
- 本次固定受审提交：`76596656908ed84e577e8202a602e3256d5febcc`。
- tree：`8b646570108026a8deabe8330c548cab0280122d`。
- 定稿时再次读取 HEAD/tree，并核对该提交至工作区的下列八个范围文件差异为空。提交后仅追加流程证据和报告。

已全文读取本树最新版 AGENTS、外部 `developer-common-instructions.md` 和 `external-review-permissions.md`。实际核对 AGENTS SHA 为 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`，common SHA 为 `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`。权限政策变化未作为产品变化重开测试。审查期间未启动 Electron、可见 GUI、外审应用、HMR、焦点或凭据操作，未外发、付费、兑换额度或修改配置；仅写本报告。

## 受审范围与方法

固定提交中的完整新增范围：

1. `apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx`
2. `apps/desktop/src/renderer/src/learning/content.ts`
3. `apps/desktop/src/renderer/src/learning/types.ts`
4. `apps/desktop/src/renderer/src/learning/presentation.ts`
5. `apps/desktop/src/renderer/src/learning/learning.css`
6. `tests/unit/learning-presentation.test.ts`
7. `tests/unit/learning-workspace.test.ts`
8. `docs/iterations/T09/learning-ui-contract.md`

同时核对既有 `content/learning/`、固定基线及 PRD FR-100～105、9.4、11.2、12.1；本次相对 `51cdc0e` 的课程和 `tests/fixtures/product-baselines/` 内容差异为空。未将旧内审或旧测试结果当作新增 UI 自动通过。

方法为完整静态阅读、旧问题逐项复核、针对具体新疑点的无窗口 Node 纯函数探针，以及读取开发线同版测试原件。未并发重复启动开发线正在运行的浏览器套件或全量检查。另使用文件图像读取查看已有 1440px 与 390px 截图，没有操作用户桌面。

## 原问题与关闭证据

| 问题 | 原触发与影响 | 固定提交处置及证据 | 结论 |
| --- | --- | --- | --- |
| UI-01，P1：更新记录降低辅助归因 | 已确认完整示范/Agent 辅助后，较高版本或同版本冲突的 props 记录可重新显示独立完成 | `presentation.ts` 的 `observeRecord` / `projectionRecord` 保留最高有效提示、辅助和版本，等版不同内容标记冲突；组件经该投影取记录。纯测试及浏览器 `newer-lower`、`same-version-conflict` 覆盖返回任务后仍拒绝 | 已关闭 |
| UI-02，P1：无保存能力先泄露提示 | 真实 context 已存在而 actions 未注入时，预览分支直接显示完整答案；切任务清除本地提示后可能计独立 | `LearningWorkspace.tsx:242` 起区分无 context 与真实尝试；真实尝试缺 `recordHint`、保存失败或回执不符时不显示提示。无 context 的迁移题所有四级提示均要求先进入真实尝试；提示、检查、导出分别按可用能力注入。浏览器覆盖保存失败、能力缺席和迁移预览四级拒绝 | 已关闭 |
| UI-03，P1：同一尝试跨输入洗白 | 四元组按 inputVersion 分桶后，v1 已用完整示范，v2 新桶仍能接受独立成功 | `LearningWorkspace.tsx:61` 的 `currentFloor` 按 project/task/attempt 汇总辅助与提示；具体结果仍按完整四元组隔离。`currentRecord` 及回执/反馈均必须达到该尝试水位。浏览器覆盖 hint4 → 同 attempt/input2 → 独立记录拒绝 | 已关闭 |
| UI-04，P1：丢弃矛盾新记录而保留旧通过 | props 的高版本记录语义矛盾，被过滤后旧 independent passed 继续计完成 | `presentation.ts:166` 起保留语义无效的新记录，`projectionRecord` 拒绝该当前投影，不回退旧通过。纯测试及 `contradictory-newer` 浏览器变体覆盖旧通过失效和后续修正 | 已关闭 |
| UI-05，P2：越界提示污染可恢复水位 | 无效 maxHintLevel=5 被写入辅助水位，合法后续 maxHintLevel=4 也无法恢复 | `presentation.ts:116` 起仅将有效范围提示、safe 非负版本及已知辅助类别加入水位；无效最新记录仍令当前投影不可用，后续合法记录可恢复。纯测试覆盖 maxHint5 → 合法完整示范 v3 恢复 | 已关闭 |

UI-03、UI-05 在修复前曾用直接调用纯函数的独立探针复现。UI-04 修前依据为静态推导；开发线补充修后负例，审查者在删除 skip 后的修复版执行纯函数探针，确认矛盾新记录使投影不可用，未独立运行其修前版本。上述探针未把未接入的 owner 或领域工具当作真实来源。最终关闭判定依据固定提交源码与同版测试，不把先前通过结果外推至修后候选。

## 需求、安全与可集成性核对

- FR-100/101：页面消费固定顺序课程，展示目标、操作、完成条件、下一步、常见错误及四级提示；不依赖模型。真实尝试先保存提示再显示，课程预览不伪造学习进度。
- FR-102：检查按钮只调用 owner 注入的私有 `checkTask`；缺能力、异常、上下文或归因不一致均不形成通过。显示完成项、修复项、建议和依据；组件没有领域执行器，也不把固定 expected 自行包装成真实结果。
- FR-103：术语提供通俗解释、项目例子及可展开技术定义，包含开放世界、定义域和值域与 SHACL 区别。静态消费未改写既有教学语义。
- FR-104/105：操作完成与独立迁移分别投影；提示、完整示范及 Agent 辅助不被降级或因同尝试数据修改清除。新 attempt 的创建、跨窗口/重开后的归因恢复由 owner 持久账本负责，私有约定已明确。
- project/generation 变化重建 Session；task/attempt/input 变化使用完整 context key 卸载旧 Panel。异步回执检查 live 状态、完整 context、版本和归因；浏览器覆盖 project+generation、task、attempt、input 的迟到检查。未发现当前范围新的晚返回混用路径。
- 所有课程、提示、反馈和依据均经 React 文本渲染，无 `dangerouslySetInnerHTML`、Node、文件系统、shell、通用 IPC、模型请求或本地持久化。错误仅显示固定中文消息。恶意反馈文本测试断言没有标签执行和网络请求。
- 私有类型没有被冒充为批准跨进程契约。首次挂载及恢复必须由 owner 提供完整辅助历史；正式桥仍须由 T00/T01 做严格运行时校验与唯一存储接线。组件临时归因保护不能代替该责任。
- 静态核对原生 button/select/details、label、aria-current、aria-pressed、aria-live 和 focus-visible；查看截图及 390px 溢出断言未发现明显布局阻断。未将这些检查扩大为完整屏幕阅读器、键盘流程或 WCAG 认证。

## 验证与失败原件

最终开发线全量检查终态为退出码 0，原件：[npm-check-ui-final.txt](evidence/npm-check-ui-final.txt)。报告定稿时全文读取并核对终态内容：

- lint、Prettier、TypeScript、三段构建与 ruff 检查通过。
- 17 个 Vitest 文件、664 项测试通过。冻结候选的 T09 测试包括 18 项纯投影测试与显式启用的 16 项 Chromium headless 组件测试。
- Python 1094 项通过，包含既有 T09 内容、纯服务及 7 项真实 JobStore/stdio 基础设施通道测试。
- 开发线提供了最终进程 `93897` 退出码 0 的终态回执；审查者未重复跑该套件。

固定输入摘要、受审源文件哈希、完整显式运行命令、最终日志哈希、截图及历史原件/压缩件哈希见 [learning-ui-verification.json](evidence/learning-ui-verification.json)。最终命令显式启用 `T09_HEADLESS_UI=1`，故本轮组件测试真实执行，未将普通默认 skip 算为通过。

浏览器 harness 为 Vite 内存 bundle + about:blank，不启动 HTTP 服务；使用当前 Vite 8 支持的 `oxc.jsx` automatic/production 转换，与 React runtime 一致。Chromium headless 开启 sandbox，并移除默认禁用 hang monitor 和 mock keychain 参数。回调和 owner 数据均明确标为 unit-only synthetic；页面拦截并断言无网络请求。

失败原件以 gzip 无损归档保留，原始与压缩件 SHA/字节数在上述 summary 中；可解压读回。不以修后成功改写历史：

- [ui-first-vitest.txt.gz](evidence/ui-first-vitest.txt.gz)：虚拟入口解析失败，纯测试通过而浏览器未执行。
- [ui-second-vitest.txt.gz](evidence/ui-second-vitest.txt.gz)：浏览器运行时缺失，15 项纯测试通过、7 项组件未执行。
- [ui-third-vitest.txt.gz](evidence/ui-third-vitest.txt.gz)：JSX development 产物与 production React runtime 混搭，16 项纯测试通过、13 项组件失败；统一 jsxDEV 错误随后修复。
- [ui-fourth-vitest.txt.gz](evidence/ui-fourth-vitest.txt.gz)：中间候选 30 项通过，不能替代后续改动的最终验证。
- [npm-check-ui-first.txt.gz](evidence/npm-check-ui-first.txt.gz)：隔离浏览器自带 JavaScript 被 ESLint 扫描。运行时后来移入本树既有 node_modules 默认忽略范围，没有放宽共享 lint 规则。
- [npm-check-ui-type-failure.txt.gz](evidence/npm-check-ui-type-failure.txt.gz)：旧 esbuild JSX 选项不符合当前 Vite 8 类型，改用实际支持的 OxcOptions 后关闭。
- [npm-check-ui-intermediate-661.txt.gz](evidence/npm-check-ui-intermediate-661.txt.gz)：中间候选完整检查通过；新增矛盾记录和恢复保护后另以最终日志验收。

## 剩余门禁

本次未把主 App 接入、实际学习 Store/领域适配、T08 辅助来源、T10 HTML/项目包导出、阶段版本证据契约、打包资源、真实 Electron 或平台原生验收标为完成。组件测试的 synthetic callbacks 不证明这些能力，也不能替代至少五名非开发新手的真人学习与迁移验收。

指定 ZCode GLM-5.3/最高及 MiniMax M3.1-Flash/xhigh 的同版独立双审仍 pending；推送、PR、实际 CI、合并与远端核验按总控门禁继续。完整 T09 父任务状态以其 `status.md` 为准。
