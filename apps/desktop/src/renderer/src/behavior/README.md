# T06 独立行为工作台

入口：`BehaviorWorkspace.tsx`。沿用已批准 App 的浅绿背景、白色卡片、青绿色强调与系统中文字体。组件未装配到 App；没有注册 bridge、调用 `window.ontolearn`、创建 Store 或自动启用服务。

## 本地组件契约（待 T00 接线）

`BehaviorWorkspaceProps` 的 `context` 必须来自真实项目状态，包含项目、输入版本、行为定义版本和已创建的隔离副本 ID。`catalog` 由同一快照提供已知对象、类、属性单/多值约束、项目行为 ID，以及可选的当前编辑行为 ID。不得用正式项目 ID 冒充隔离副本 ID。

`initialDraft` 仅用于第一次装载或切换项目。结果刷新、同项目输入版本更新不覆盖本地草稿；切换输入版本清空原结果并拒绝迟到回包。宿主切换所编辑的行为时，必须用 `key={projectId + ':' + selectedBehaviorId}` 创建对应编辑实例，配合 `onDraftChange` 保存该行为的本地草稿。此回调只是草稿变更通知，不表示保存、Store 提交或 Agent 批准。重进页面的草稿恢复由宿主负责。切项目/版本/卸载只隔离回包，不会自动撤销后台任务；旧任务的持久跟踪、取消或对账由宿主按真实生命周期处理，不得盲目重发写请求。

`services` 默认为空。只有真实能力被批准且完成版本/隔离校验后，宿主才可传入下述私有 callback；这些名字不是公共方法，不能直接添加到 preload 或能力注册表：

| callback        | 输入                                                                        | 输出与责任                                                              |
| --------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `runSample`     | `SampleRequest`：请求绑定、行为草稿、有序事件及显式 add/remove/set 断言变更 | 未知数据，必须满足 `resultSchema`；真正执行冻结条件、竞争检查与隔离收尾 |
| `refreshResult` | 原请求绑定、原 runId                                                        | 只读同一运行，不重发事件，不覆盖草稿                                    |
| `cancelSample`  | 原请求绑定                                                                  | 必须返回真实已取消终态；接受取消请求不等于收尾完成                      |

输入/输出的精确私有类型见 `model.ts`。条件只提供一组 AND，支持显式 `always`（无额外条件）、属性值等于、已有属性、类型判断；类型判断必须映射到真实行为前推导。安全动作限创建个体、更新单值属性、添加关系、内部通知。多值关系和单值覆盖分别标明。空条件数组或缺失条件字段仍拒绝，不把未作选择解释为通过。事件内容是有限大小 JSON 键值对象，解析前显式拒绝自有键 `__proto__`、`constructor`、`prototype`（含 JSON 转义形式），避免 schema 静默删值；普通字段完整保留。断言变更另以有序结构编辑。adapter 必须逐项转换为批准引擎契约，拒绝不可表示的条件、值、动作或变更；当前未声称与未批准服务类型兼容。

结果必须包含原项目/版本/隔离副本/requestId、runId、断言/推导/执行语义版本、逐个触发或未触发理由、全部动作的真实顺序和状态、Diff、通知以及当前/过期/历史标记。`committed=false` 的成功计划只能是候选；`completed + committed=true` 指隔离副本提交。正式数据不属于此组件的执行目标。错误只接受固定枚举并用本地说明展示；禁止将 `BehaviorError.evidence`、原始异常、路径、堆栈、密钥或业务原值塞入错误或 trace detail。未知字段（含 evidence）使结果校验失败。

本组件的结果是单次 sample、单个隔离轮次，不能混入此前轮次已提交证据。严格结果组合如下；任何不相容组合拒绝显示，刷新失败时保留上一份有效结果：

| 单轮状态  | committed | 允许的动作状态                 | 允许的通知状态 |
| --------- | --------- | ------------------------------ | -------------- |
| candidate | false     | planned、deduplicated、skipped | candidate      |
| completed | true      | applied、deduplicated、skipped | recorded       |
| failed    | false     | rolled_back、skipped           | discarded      |
| cancelled | false     | rolled_back、skipped           | discarded      |

`failed` 必须有固定错误码，其余状态不能附失败错误；过期结果必须有真实过期说明。未触发可返回空轨迹/空通知，不推断存在缺失记录。候选的 deduplicated 仅表示计划中的同值去重，不代表提交；失败或取消的尝试统一标明回滚/未执行与通知丢弃。

T00 接线需要：共享 App 导航/宿主装配；批准的项目与隔离生命周期；真实能力与安全边界适配；同快照 catalog；真实 input/behavior/assertion/inference/semantics 版本；事件幂等、跨实例竞争、事务回滚和取消终态的来源；结果过期原因须来自现行失效表，不由 UI 推断。刷新必须保留 runId 和原请求绑定，历史只读；切换行为/项目由宿主保留对应草稿。T06-S1、Store、推理、Agent 和 UI 的联合验证由父任务安排。

## 验证入口

- `npx vitest run tests/unit/t06-behavior-ui.test.ts`：纯状态机和完整证据文本断言。
- `npm run check`：本工作树完整规则检查。
- `PLAYWRIGHT_BROWSERS_PATH="$PWD/test-results/t06-browser-cache" npx playwright install chromium --only-shell`：只安装本树 headless shell。
- `PLAYWRIGHT_BROWSERS_PATH="$PWD/test-results/t06-browser-cache" node apps/desktop/src/renderer/src/behavior/verify-headless.mjs`：构建隔离夹具，在临时 loopback 服务上用真正 headless shell 验证交互及 1440/390 布局，始终关闭浏览器与服务器。没有 Vite HMR 或 Electron。夹具始终标为非引擎结果，验证组件状态，不能证明算法、真实事务或正式接线。

证据与已知限制见 [status.md](./status.md)。生成截图、构建文件、浏览器缓存及原始日志放本树忽略的 `test-results/`，不随源代码提交。
