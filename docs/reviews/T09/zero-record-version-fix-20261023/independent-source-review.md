# F04 版本 0 修复独立静态审查

结论：当前两路径 actualdelta 静态审查通过，未发现阻断问题。可以进入授权票规定的后续运行验证；本结论不代表测试运行通过、指定模型双审通过、Pair Pass 或父功能验收通过。

## 固定范围与身份

本次实际读取本树 `AGENTS.md`、授权票、相对 `0cde6a11604214f4ff34d2a9fbcfb80b6f72bfd2` 的两路径完整差异，以及必要的本树 `presentation.ts`、`types.ts`、`learning-ui-contract.md` 与 PRD FR100–105。未扩展到旧 reviewroot、native/global、`.mimosa`、其他源码或其他工作树。

- 本树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T09-zero-record-version-fix-20261023`。
- 产品来源：`76596656908ed84e577e8202a602e3256d5febcc`；本次差异基准：`0cde6a11604214f4ff34d2a9fbcfb80b6f72bfd2`；批准共享基线：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。本次只核对指定差异，未重新证明整树或历史候选。
- 实读 `AGENTS.md`：15147 B，SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。
- 实读票 `T09-F04-zero-context-version-source-and-ordinary-ticket-20261023.json`：5973 B，SHA-256 `c4247305e4462a1aa46e65f041f91b1c3a998b4c2af1d18d460f33cbca3e5505`，与通知一致。

| 本次实际文件                                                   | 字节数 | SHA-256                                                            |
| -------------------------------------------------------------- | -----: | ------------------------------------------------------------------ |
| `apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx` |  18669 | `5bd90f57bdb25874839c7f43bd4c61e42cf46b945675129a8a59eadce149fa9a` |
| `tests/unit/learning-workspace.test.ts`                        |  27162 | `b45db359bc3b5571786eb84864b9e74294f09f4277492818b440743371149074` |

## 静态核对结果

1. `LearningWorkspace.tsx:29–30,63–79` 的局部 `ContextFloor` 以 `hasContextRecord` 区分“同 attempt 仅有其他 input 的辅助水位”与“已有当前完整 context 投影”。跨 input 水位依旧聚合相同 project/task/attempt 的最高提示及辅助等级，版本只取当前 context；不存在当前记录时的数值 0 不再被误认为已有版本 0。
2. `LearningWorkspace.tsx:263–279,294–305` 的 hint/check 接收路径仅在 `hasContextRecord` 为真时施加 `recordVersion <= floor.recordVersion` 拒绝。已有同 context 的版本 0 仍拒绝重放 0，随后 1 可以通过其余校验；新 input 首条合法 0 可通过。未将全局 `<=` 改成 `<`，未改变 `presentation.ts` 中安全非负整数版本、完整 context、提示/辅助及独立迁移校验。
3. 辅助保护仍同时约束最高提示与辅助等级。新 input 的版本归零不会清除本 attempt 已确认的提示 4/full-demonstration；不满足该水位的回执不会展示答案或检查结果。既有无效/冲突投影仍保留为“当前已有记录”，本次改动没有以 absence 洗掉冲突或水位。
4. 生命周期防线未改变：project/generation 的会话 key、完整 context 的面板 key、卸载后的 `live` 拒绝与回执 context 对照仍在。既有 task/attempt/input 迟到检查负例及 project/generation 迟到负例保留（测试 `296–326,563–589`）；本次未将旧 context 的回执用于新 input。
5. 新测试 `442–562` 为 hint/check 各三种情形，共六项参数化案例：有旧 input 辅助记录时新 input 首条 0 接受；当前 context 已有 0 时重放 0 拒绝、随后 1 接受；新 input 首条 0 试图降低既有辅助水位时拒绝。它们调用真实组件入口并断言可见反馈/提示与迁移计数，`state.version=-1` 仅使 synthetic owner 的自增回执发出合法 0，没有向组件传负版本。未将 synthetic 回执当作持久化或领域工具证据。
6. 测试 `193–200` 只新增显式 `T09_CHROME_EXECUTABLE` 与实际 `browser.version()` 输出；默认路径行为、headless、sandbox 和默认参数保留方式未改变。请求全部 abort、pageerror/request 为空断言仍在（`202–224`）。该静态核对不能证明 Chrome 身份、实际版本、运行成功或环境可用，仍须由后续票内运行与回执证明。

此修复符合 FR101/102/104/105 的相关边界：答案仍在保存回执校验后展示，完成反馈仍只接受 owner 注入结果，辅助与独立迁移不混同。FR100/103 的课程与术语内容不在本次修改中；本次未重新验收完整课程或实际领域适配。

## 验证与未关闭门禁

实际完成：上述只读静态审查、文件字节/SHA-256 核对，以及仅两指定路径的 `git diff --check`（退出 0）。本次未启动浏览器、GUI、产品测试、构建或服务，未安装依赖，未进行真实领域、持久化、环境或端到端验证。六项新案例和既有迟到案例的运行结果在本报告定稿时均未由本审查者取得，不记作通过。

本次只写此授权报告，不修改产品或测试。后续仍需票内实际 Chrome 身份与运行证据、相应普通检查，以及新候选所需的正式指定双审；旧 Z 过程失败、原因 UNKNOWN、其他历史问题和父验收门不因本次静态结论关闭。
