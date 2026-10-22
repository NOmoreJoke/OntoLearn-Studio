# T09 F-04 修复与 F-05 历史阶段旁注

F-04 保持原 P3：修复同一 attempt 切换 input 后合法首条 `recordVersion=0` 被误拒。局部投影新增 `hasContextRecord`，区分“该完整 context 尚无记录”与“已知版本为 0”。仅前者允许首条 0；已有完整 context 的 hint/check 回执仍须严格递增，跨 input 的最高提示和辅助来源水位不降低，既有身份、冲突和迟到拒绝不变。公共 view model、presentation、owner 持久化权限均未改。

本次从 `0cde6a11604214f4ff34d2a9fbcfb80b6f72bfd2` 新建 `fix/t09-zero-record-version` 独立树。产品改动只有 `LearningWorkspace.tsx` 和既有 `learning-workspace.test.ts`；测试新增六项参数化用例，另允许显式选择现有 Chrome executable，默认 Playwright 运行时不变。实际差异先经[独立静态审查](independent-source-review.md)，再执行必要本树验证。首轮 39 通过、1 失败：新增测试宽泛 locator 同时匹配侧栏和提示按钮；修为精确可访问名后，另经[限定独立静态审查](independent-locator-correction-review.md)，受影响用例实跑通过（另 21 项筛选跳过）。首败原件保留，组件实现未因这次测试定位修正变化。最终运行记录、两路径字节及完整 32 路径向量以[验证收据](validation.json)为准。

修复源提交为 `d643c5a41f42d4d5395ab7d6c457c6e002cf481f`。原 `npm run check` 显式启用本树 headless 后 exit 0：670 项 Vitest（含 22 项组件、其中 6 项新增）及 1094 项 Python 全通过，lint/格式/类型/构建/ruff 通过，无 Vitest skip。`npm run verify:sources` exit 0，核对 12 个归档源文件。验证运行于提交前的固定两 blob，前后 SHA 与该源提交相同，不虚称在后来提交 HEAD 上执行。首个 own headless 启动实际记录 Chrome `155.0.8059.85`；后续成功套件的捕获输出没有版本行，不补造该行。固定 executable/plist 前后哈希一致；sandbox 仅有配置及运行证据，未采 OS 隔离证明。

## F-05：旧摘要的阶段与引用

[历史 verification-summary.json](../evidence/verification-summary.json) 是 `51cdc0e9d138c98cdd4ace865074a71883657a68` 引入的学习服务/固定基线阶段收据，位于后续 jobstore 修复和 UI 组件阶段之前。其 3972B、SHA-256 `0acc4fafe1e334118afdb440295ca14d755babaff0494035aeeb087a9f789fa1` 和六个 `sourceCodeSha256` 已静态核对；六项都匹配该阶段提交。35 项学习 Python、630 项 Vitest、1087 项全量 Python 是该阶段原始记录，不是 765 产品候选或本次修复的计数。

本旁注只补充旧摘要的阶段和引用，不改旧摘要、原运行证据、旧候选或作者审查。后续 UI/基础设施历史应分别查看[原状态说明](../status.md)、[冻结输入清单](../round-1/input-manifest.json)及[replacement-r1 终态意见](../replacement-r1-terminal-20261023/opinions-and-disposition.md)。本次新验证与历史阶段分列，不能覆盖真实树失败、镜像替代、缺浏览器失败或 skip。

## 保留边界

此次局部修复不倒灌为原审查通过。Z 过程 FAIL、原轮 Pair Pass=false、环境归因及 global 执行成功 UNKNOWN 保持。13 旧项的作者意见、三项有条件延期及三项父项不改变；Z E-01/E-02 和 M F-04/F-05 的原严重度不改变。F-05 的新旁注与 F-04 的实现修复不自行关闭根处置。

仍需对新完整同候选执行两指定模型全量独立审查。本次未创建新双审；未接正式领域、bridge/App、持久化或报告；未跑 Electron、native、包装、双 OS、真人、生产、远端或 CI；无 push/PR/发布或父 Goal 完成。旧根、原稿、收据和 AGENTS overlay 均保留；未访问 global 实际目标或受禁返回，也未清理 hook 或镜像。
