# T08 指定审后 WIP patch 独立审查 1（2026-10-23）

结论：**本次 WIP 暂不通过**。发现一处剩余 P2：运行时变异的 AgentError.code 仍可绕过收据入口净化，进入本地主进程完整收据。provider 投影已正确回退安全码，不能把该问题描述成已证实的模型外发泄漏。其余本次身份 pin、响应思考字段、输出超额检查、重复 ID 与 BUSY 调整未发现新的阻断问题。

本结论针对下列实际 WIP 字节，不是 product93516fa、未来修改版或指定双审整体通过。原审方严重度/NotPass 保留；未改旧独立分析报告。

## 实际读取的候选身份

开发树 HEAD `7476dae2d622fc965efe4a8c4340a33ea70dd050`，基础产品 `93516fa8455cf4b195cbfb699aa7a6652d428b6f`。读取六个 owned 源文件的现有实现及 diff、四个旧测试的相关变更、新回归测试全文和设计变更；未读取或修改两棵冻结审查树。

| 当前文件                                                      | SHA-256                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------------------ |
| `apps/desktop/src/main/agent/agent-service.ts`                | `5f61f75f168d8e917937db72986d2d819ae7a278478a524c61eb94aceec368a7` |
| `apps/desktop/src/main/agent/capabilities.ts`                 | `3b05b573ff3cbddb6bcbd1b97679efe084096e9a4856e0ca8648b967ef308303` |
| `apps/desktop/src/main/agent/conversation.ts`                 | `a386a804703c210b2eb5847b66d6265f11e4e9246ec1efff7108e292dee5fd07` |
| `apps/desktop/src/main/agent/deepseek-codec.ts`               | `f89db7df0298f2fd56cb7c98adccbfc3d42709f75e96f47d0372c541cac07065` |
| `apps/desktop/src/main/agent/errors.ts`                       | `5b01268e6bada04522bf84541d7a02b6d2ff36f4f9da39aa229d5d816b4e2c0a` |
| `apps/desktop/src/renderer/src/agent/sidebar-presentation.ts` | `0169ab89a41070b8b70d35ef34fbc6b6dce9d7502e9ab86abfdf02ff67cf1e55` |
| `tests/unit/t08-agent.test.ts`                                | `6d5d5869a81e0bc71e6778c77c72e8952ae5c49f1542410e06e80fab2f179f1e` |
| `tests/unit/t08-conversation.test.ts`                         | `41faf2bf7b8982bb4c2e059c78222e372342bfef05eb20feffc6ed21c72f7649` |
| `tests/unit/t08-fixed-input.test.ts`                          | `e323563aa88532694d25fb1685071350b9441c4e27c673861b4e079273f81c95` |
| `tests/unit/t08-sidebar.test.ts`                              | `7d9e543cdddd347ad5703787983228a986025675580eb3a64c9125ae6284cc0c` |
| `tests/unit/t08-review-regressions.test.ts`                   | `db96d30fee2c5ebcb4ac8557d3e6466800625cf9729da58ce0856743f9467cb1` |
| `docs/iterations/T08/design-and-integration.md`               | `f6cbf4ccbde8737c971e1978c7256c604b57d2ffcae06aeac74727151e74b06c` |

未重跑 full suite，也不把主写者通报的 105 项结果算成本复核自行运行。

## [P2] 在收据入口再次净化运行时错误码

**位置：** `agent-service.ts:262–268`，尤其 `code: error instanceof AgentError ? error.code : 'TOOL_FAILED'`。新 `errors.ts` 构造器虽校验初始 code，但 TypeScript readonly 不会把运行时属性冻结。

**触发：** untyped adapter 构造正常 `AgentError('TOOL_FAILED')`，随后把其 code 改为合成字符串 `secret/path/private-cell`，再由 execute 抛出。也可构造具有相同 prototype 的对象，不能只依赖 instanceof 作为安全枚举证明。

本复核在内存转译当前实际模块，执行一次有限的合成端口反例，观察到：

- `executeCalls` 返回的 failure.code 为 `secret/path/private-cell`；
- `currentTurnReceipts()` 的克隆仍包含该自由字符串；
- `describeAgentError` 对该值返回 undefined，本地错误分类信息丢失；
- `projectToolMessage` 已正确输出 `{"kind":"failure","code":"TOOL_FAILED"}`。

**影响：** 固定安全错误码的主进程收据边界仍可被未类型化适配器异常突破，未来消费者不能依靠 ToolReceipt 的静态类型假定 code 合法。问题位于本地主收据，并非此反例已向 provider 发送异常正文。新增回归只覆盖构造时非法 code 和直接投影伪造 receipt，未覆盖“构造后变异，再由真实收据入口捕获”的路径。

**最小修复建议：** 在 executeOne catch 处对读取到的 code 再经 safeAgentErrorCode，或创建新的安全 AgentError 后仅取其固定 code；不要将捕获到的实例本身视作已净化。会话对外重抛/保存错误时也应规范化为新的安全实例，防止未来入口把已变异对象继续传播。补一项适配器抛出变异 AgentError 的反例，断言返回值、state.localReceipts、UI 分类与 provider 投影均为固定安全码，且不含合成私有串。

上述适配器是有限反例，不是获准领域服务，不构成真实工具集成。复现过程未写测试、源码或配置文件，没有读取密钥或执行真实 API。

## 其余 patch 结论

- **返回身份。** expectedProviderSignature 必填且复用严格 schema，mode/effort 与 pin 一致，Zod 解析产生独立快照；响应 model/fingerprint 在任何端口调用及答案接纳前精确检查。未发现首次响应自建 baseline、请求别名硬等同返回版本或宽松后缀匹配。新增测试覆盖缺 pin、模式/effort 不符、外部 pin 变异、返回模型/指纹漂移及必需指纹消失。此处仍不证明宿主真实评估 ready 或 I06 实际配置/端点/主体有效。
- **思考模式。** enabled 响应在无工具时同样要求 string reasoning_content；编码历史仍保留有工具与无工具两种协议规则。新增测试区分响应缺失/null、disabled 响应与无工具历史，不伪造补字段。实际 provider/effort 未验这一边界在设计中保留。
- **usage。** completion 超请求 maxTokens 在工具/答案处理前拒绝；不把 prompt/total 与已请求输出预算混比。usage 缺失仍返回 null。新测试同时检查端口零调用、大输入不误拒、失败后的旧草稿与累计请求占用保留。没有扩成费用硬限额或实际输入预算，设计对此说明准确。
- **收据保留。** 漂移和输出超额进入既有 fail 流程，只清 pending/answer，不清 session 收据；state 仍通过克隆提供 localReceipts。新回归实际构造前轮草稿，再拒绝后一轮，方向正确。错误码入口问题见上节。
- **投影。** failure 分支只增加有限安全枚举，未知值回退 TOOL_FAILED；draft 仍只发 kind。现有异常正文不回传测试已同步。外发授权仍归 I06，没有因 code 安全就假定可以发送。
- **诊断与预验。** BUSY 独立于真实调用预算；codec 历史重复 ID 改为 INVALID_PROTOCOL，未知工具仍 TOOL_NOT_ALLOWED；批内重复 ID 前移至 prepare 前且不削弱执行前全批校验。未发现调用次数或已用 ID 被回退。
- **选择顺序。** 未排序 selectedObjectIds；新对照测试确认 main 与 sidebar 对重排都判不同，避免无依据改变语义。
- **local SSR。** 新测试只证明给定 local hint handler 时 markup 可用、模型发送仍禁用，注释明确不是挂载点击或 T09 真实 handler。没有把 SSR、合成 pin、手工固定输入或行为反例宣称为真实 DOM/provider/受测模式通过。

## 尚未覆盖的门

M 原 P1、真实 DOM 挂载、离线实体、隐私权威和公共工具映射等不因本轮局部修改关闭；具体归属与争议须保留原严重度及依赖事实。当前结果需先修复上述 P2，再按新实际文件 hash 做增量复核；此报告不能用于通过尚未冻结的新候选，也不替代同版指定双审与完整原验收。

本轮只新增此报告；未改产品、测试、依赖、配置、旧分析或冻结审查树。未执行安装、GUI、真实 API 或 full check。
