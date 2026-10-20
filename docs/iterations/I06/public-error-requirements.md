# I06 → I03 公共错误映射需求

日期：2026-10-20。请求方 I06；唯一公共契约维护者 I03，经总控协调。依据当前核心检查点 `637e0e6869091610141b0b9b9ebf01545205e648` 的 `policy.ts`、`gateway.ts`、`credentials.ts`、`transport.ts`。实际内部枚举为 **11 类**。

这是一份交接需求，不是批准的公共 schema。I03 可复用其现有受限公共错误 code 或统一命名；下表左列仅是 I06 内部身份，不要求原样加入公共枚举。messageKey 是建议，最终命名/params/展示映射以 I03 冻结契约为准；本次不修改共享 contracts、不注册 bridge、不提前接线。

| 当前内部 code            | 必须可表达的语义与实际来源                                                                          | 建议 messageKey                 | safe params 要求 |
| ------------------------ | --------------------------------------------------------------------------------------------------- | ------------------------------- | ---------------- |
| `INVALID_INPUT`          | 严格参数/端点校验失败，材料/正文或内部登记上限；不包含原始校验 issue、被拒绝输入或 URL              | `gateway.invalidInput`          | `{}`             |
| `LOCAL_ONLY`             | 项目处于完全本地，禁止新外发；不自动启用模型                                                        | `gateway.localOnly`             | `{}`             |
| `AUTHORIZATION_REQUIRED` | grant/预览缺失或撤销，项目/用途/接收配置不匹配；不泄露其他项目或授权记录的存在                      | `gateway.authorizationRequired` | `{}`             |
| `SCOPE_EXCEEDED`         | 最终材料来源超范围、handle 缺失/释放、跨项目；工具/历史/摘要/错误来源并集同样检查                   | `gateway.scopeExceeded`         | `{}`             |
| `CONFIGURATION_CHANGED`  | 配置缺失、配置版本/接收端/主体/凭据身份或隐私 epoch 改变，旧预览/授权不得复用                       | `gateway.configurationChanged`  | `{}`             |
| `CREDENTIAL_UNAVAILABLE` | 凭据缺失、身份不匹配、安全存储不可用/不安全 Linux 后端、加解密/仓库失败、密文绑定或内部格式校验失败 | `gateway.credentialUnavailable` | `{}`             |
| `AUDIT_UNAVAILABLE`      | 本地最小审计无法持久保存；发送前失败阻止发送，失败发生在派发后则不能宣称此前零外发                  | `gateway.auditUnavailable`      | `{}`             |
| `REDIRECT_REJECTED`      | 接收端返回任意 3xx，禁止自动跟随；不返回 Location 或接收方原文                                      | `gateway.redirectRejected`      | `{}`             |
| `MODEL_UNAVAILABLE`      | 网络/超时/上游非成功结果、并发上限或未知内部失败的安全兜底；不传原始 HTTP body/异常                 | `gateway.modelUnavailable`      | `{}`             |
| `RESPONSE_LIMIT`         | 接收内容超过内部响应字节上限，停止读取；不返回已收正文                                              | `gateway.responseLimit`         | `{}`             |
| `CANCELLED`              | 已取消本地等待或连接；可能因切本地、撤销或相关配置变更触发，不能解释为撤回已发送内容                | `gateway.cancelled`             | `{}`             |

## 安全参数与可恢复性

- 本阶段不需要动态 params：每个错误只有固定语义。请采用严格空对象（或公共契约中等价的“无参数”形状），拒绝额外键。错误码和 messageKey 不能承载插值正文；不接受服务返回值指定 code/messageKey/params。
- 不回传 endpoint/Location 原文、API Key/解密信封/密文、credentialRef/principal/版本、材料正文、工具结果、数据库原值、项目绝对路径、OS 后端异常、库堆栈、zod issues 或未知字段。授权预览的目标/范围通过另一个可信业务接口显式提供，不能借错误参数扩充范围或泄露其他项目。
- I03 若已有同语义 code/messageKey，I06 在正式接线时做单一显式映射，不复制第二份公共注册表；主进程错误不为了统一而绕行 Python。错误参数即使是安全的，也仍须经过模型外发范围检查。
- 需要对齐公共 `retryable` 的精确定义。当前 I06 只返回内部 code，`MODEL_UNAVAILABLE` 不足以证明请求没有发送。**不得根据错误码自动重发**；当前映射宜保守保持不可自动重试。用户手动重试是新请求，仍须全部授权/配置/最终载荷检查；最多一次 429/503 内部重试已由网关掌握，bridge/任务恢复不能再叠加重放。
- 四段式 UI 说明由公共层根据固定 messageKey 映射现象、原因、影响、下一步；授权/范围/配置类引导重新预览确认，完全本地保持本地，凭据/审计类修复本机条件，网络类允许用户重新发起或转本地功能。失败/取消不等于确定性工具通过，也不应使本地保存依赖模型成功。

## 采用后的必要验证

I03 维护公共 code/messageKey/params 配对、未知字段和错误参数拒绝样例；I06 在依赖合并后的实际主进程 → bridge → UI 路径验证本表 11 类的完整固定映射和安全说明。测试须断言返回字段全集，不以文件中存在枚举、单元 mock 或当前私有码直接穿透作为接入完成。若最终公共契约需要细分 timeout/忙碌/上游错误，先保留本表安全兜底，再由 I06 在实际来源处产生精确类别，不能从异常文本猜分类。

## I03 实际承接读回（2026-10-20）

总控转交后，I06 已只读核对 I03 的 `docs/reviews/I03/handoffs/I06-error-disposition.md`，来源工作树为 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I03-protocol-contracts`。读回内容 SHA-256：`25910655ff5f03e20509393a45863af0093a0d7d0436cceb72ff1603deaee50a`。以下记录是接口协作证据，不表示 I03 新契约已冻结或 S3 能力已注册。

- I03 当前不新增 S3 方法/能力，不透传 I06 私有码。现有 `INVALID_REQUEST`、`PERMISSION_DENIED`、`INTERNAL_ERROR` 只能作安全兜底，不能冒充已经精确表达 11 类网关语义。特别不把配置失效映射成项目 revision/session 冲突，不把重定向拒绝映射成确定性查询外联禁止，不借用业务存储或引擎帧/分页错误。
- 原文件对 `INVALID_INPUT` 的现有兜底是 `INVALID_REQUEST / protocol.invalidRequest / {field:"params"} / retryable=false`，其中 field 只能为固定类别，不能含输入或校验 issue。其余网关新错误采用严格空 params、固定 messageKey、`retryable=false`。这一区别按实际文件保留；不将“新网关错误应为空参数”的要求误写成现有通用错误也是空参数。
- 精确网关 code/messageKey 在实际 I06 接线前由共享契约唯一维护者形成新版本、新候选，包含公共正反例并履行当时完整双审门禁。I03 表中 `GATEWAY_*` 等均是候选命名，当前不属于已批准 schema；I06 不能另建公共注册表或提前接线。
- `CANCELLED` 后续采用独立取消结果分支，不能直接塞入当前公共 error 枚举，也不作为确定性任务 failed 或领域 staleReason。只说明停止本地等待/连接，已发送内容无法撤回。
- 公共 `retryable` 只说明条件修复后用户能否显式重发，不授权自动重放。写任务先以 operation/job 对账；模型失败不证明未发送，bridge 恢复不得叠加网关已掌握的一次 429/503 重试。用户手动发送仍须重新进行完整授权、配置和最终载荷检查。
- 新版本落地后验证真实 main → 窄 bridge → UI 的全部字段、安全参数拒绝、取消分支和四段式说明；不得因模型失败阻断本地保存。这份设计承接不替代正式接线、实际 safeStorage、存储/导出和窗口重连验收，也不解除依赖/隔离环境阻塞。
