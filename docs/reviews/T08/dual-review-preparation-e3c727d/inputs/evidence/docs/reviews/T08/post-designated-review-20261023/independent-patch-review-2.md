# T08 WIP 净化修复独立复核 2（2026-10-23）

结论：**本次净化增量复核通过**。独审 1 新发现的“变异 AgentError.code 进入本地完整收据”P2 在下列实际 WIP 字节中已修复；未发现该修复削弱原 patch 的新问题。独审 1 暂不通过原件保持，不回填历史结果。本结论不关闭 M 原发现，不是指定模型 Pass，也不改变整体 NotPass 或完整原验收门。

## 当前字节与增量范围

HEAD 仍为 `7476dae2d622fc965efe4a8c4340a33ea70dd050`。相对独审 1 的 12 文件 hash 清单，仅 agent-service、conversation、errors 与新回归测试四文件变化；其余八文件 hash 均与独审 1 相同。实际复核这四文件的新增净化函数、调用点与回归，以及其对既有身份/预算/收据流程的影响。

| 当前源码/新增回归测试                                                 | SHA-256                                                            |
| --------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `apps/desktop/src/main/agent/agent-service.ts`                        | `915b334c0cd0e35f683750f148d331b9e14f7d0d3344e54fd532619b789ebded` |
| `apps/desktop/src/main/agent/capabilities.ts`（未变）                 | `3b05b573ff3cbddb6bcbd1b97679efe084096e9a4856e0ca8648b967ef308303` |
| `apps/desktop/src/main/agent/conversation.ts`                         | `0304e444d925eb7d44603471fcde2d04b1900eb5a08ca6765a1ddff4be10aacd` |
| `apps/desktop/src/main/agent/deepseek-codec.ts`（未变）               | `f89db7df0298f2fd56cb7c98adccbfc3d42709f75e96f47d0372c541cac07065` |
| `apps/desktop/src/main/agent/errors.ts`                               | `9269319454eb6ed640789e24420cd5e0516057697b2b97e2e0e733ec6ec92c45` |
| `apps/desktop/src/renderer/src/agent/sidebar-presentation.ts`（未变） | `0169ab89a41070b8b70d35ef34fbc6b6dce9d7502e9ab86abfdf02ff67cf1e55` |
| `tests/unit/t08-review-regressions.test.ts`                           | `962348e162c5d3aa634f648c495c5eba377b1c404aa00de3013b4ed1d587e946` |

## 修复判定

- `errors.ts:38–48` 的 normalizeAgentError 在 try/catch 内判断实例并读取 code。外部实例的 code getter 或 proxy 原型访问抛错时回退，不读取其 message/stack，也不调用字符串转换；安全枚举之后总是生成新 AgentError，不保留外部实例。
- `agent-service.ts:262–268` 在 failure 收据入账前使用 normalizeAgentError 的固定 code，修复原本只凭 instanceof 就信任可变属性的缺口。本地完整收据和只读克隆现在也受枚举边界保护，而不只是 provider 投影。
- `conversation.ts:137–140,215–218` 两个 catch 以 INVALID_PROTOCOL 作为非 AgentError 的默认分类，并重建安全实例后保存/重抛。合法既有码仍保留；外部错误正文和变异实例不继续传播。
- `t08-review-regressions.test.ts:296–325` 新增实际适配器抛出变异 code / throwing getter 的两例，断言 executeCalls 返回值与 currentTurnReceipts 均为 TOOL_FAILED 且不含合成私有串，覆盖了独审 1 所缺入口路径。

## 实际有限验证

未重跑 full check 或整套定向测试。使用已安装 TypeScript 在内存转译当前模块，运行四个有限合成端口反例，进程退出 0：

| 外部异常变体                                  | 新实例 code/message | 完整收据、克隆、provider 投影     |
| --------------------------------------------- | ------------------- | --------------------------------- |
| 构造后将 code 改为合成私有串                  | TOOL_FAILED         | 均为 TOOL_FAILED                  |
| code getter 抛错                              | TOOL_FAILED         | 均为 TOOL_FAILED                  |
| proxy 的 getPrototypeOf 抛错                  | TOOL_FAILED         | 均为 TOOL_FAILED                  |
| 合法 TIMED_OUT，但原 message 被改为合成私有串 | TIMED_OUT           | 均为 TIMED_OUT，原 message 不保留 |

四例 normalizeAgentError 返回值均不是外部原实例，记录均不含合成私有串。原结果已保存：`../review-runtime-post-designated-20261023/independent-patch-review-2-observations.json`，3321 字节，SHA-256 `233684522dcbc6f94fcef52e1b3e5d9580fe1ffddc6c03620926a0bb250d9972`；其中保留实际加载源码 hash。该证据只证明纯模块异常净化，不是真实 provider 或领域运行。

## 对原 patch 的影响与限制

身份 pin、工具执行前 model/fingerprint 检查、enabled 响应 reasoning 规则、completion 超请求值检查、未知 usage 语义、BUSY/重复 ID 诊断和安全投影均未被改写。catch 仍调用既有 fail 流程，不新增收据清空或预算回退；已完成记录依旧由 session 保留并克隆读取。

本次只检查净化增量及相应影响，不重新裁定其余指定模型发现。主写者的 check-02 正在执行这一事实不计为本复核通过证据；完整检查结果须由其实际终态另记。未修改实现、测试、配置、依赖、旧报告或冻结审查树；只新增本报告与上述有限观测文件，未访问 GUI、凭据、真实 API 或安装依赖。
