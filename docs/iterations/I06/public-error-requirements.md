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
