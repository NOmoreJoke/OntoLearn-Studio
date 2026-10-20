# I06 公共错误需求处置

2026-10-20，经总控01a154de-843b-7a00-8a80-51ba1c0aebce转交。源：I06 `docs/iterations/I06/public-error-requirements.md`，其内部检查点637e0e6869091610141b0b9b9ebf01545205e648；本线已实际读取源文件。此记录为接口协作证据，不声明下列新命名已经进入I03 schema或批准S3公开调用。

I03 当前没有S3公开方法或网关能力注册项；I06仍是主进程内部模块。当前安全兜底与最终可操作语义分开：通用错误不能冒充已精确区分11类。正式接线前，由I03契约维护者在新候选中补充下面预留的网关公共错误/取消结果schema及公共样例，并按当时完整门禁审查；I06不得直接透传私有码或另建公共注册表。该未来网关接线不阻断当前S2/U1设计冻结。

| I06内部身份 | 当前I03可用边界 / 正式接线前的明确承接 |
| --- | --- |
| INVALID_INPUT | 可复用 INVALID_REQUEST / protocol.invalidRequest / params={field:"params"} / retryable=false；field是固定类别，不含zod issue或原输入。若UI需独立网关提示，下版再定义 GATEWAY_INVALID_INPUT 严格{} |
| LOCAL_ONLY | 通用 PERMISSION_DENIED {}只能作安全兜底；正式语义预留 GATEWAY_LOCAL_ONLY，严格{}、retryable=false，解释完全本地禁止新请求 |
| AUTHORIZATION_REQUIRED | 通用 PERMISSION_DENIED {}不泄露授权存在；正式预留 GATEWAY_AUTHORIZATION_REQUIRED，严格{}、false，引导重新预览确认 |
| SCOPE_EXCEEDED | 通用 PERMISSION_DENIED {}不泄露他项目；正式预留 GATEWAY_SCOPE_EXCEEDED，严格{}、false，重新选择合法材料与预览 |
| CONFIGURATION_CHANGED | 不套用项目REVISION_CONFLICT或引擎SESSION_MISMATCH；正式预留 GATEWAY_CONFIGURATION_CHANGED，严格{}、false，拒旧配置/隐私epoch授权 |
| CREDENTIAL_UNAVAILABLE | 不借用引擎/业务存储错误暗示同一存储层；正式预留 GATEWAY_CREDENTIAL_UNAVAILABLE，严格{}、false，修复本机安全存储；不打印后端错误 |
| AUDIT_UNAVAILABLE | 正式预留 GATEWAY_AUDIT_UNAVAILABLE，严格{}、false；UI明确失败可能发生在发送前或派发后，不宣称零外发 |
| REDIRECT_REJECTED | 不是本地语义NETWORK_FORBIDDEN；正式预留 GATEWAY_REDIRECT_REJECTED，严格{}、false；禁止跟随3xx，不带Location |
| MODEL_UNAVAILABLE | 当前未知主进程异常只能用 INTERNAL_ERROR {}、false；正式预留 GATEWAY_MODEL_UNAVAILABLE，严格{}、false，不推断未发送、不自动重试 |
| RESPONSE_LIMIT | 不冒充引擎frame/page上限；正式预留 GATEWAY_RESPONSE_LIMIT，严格{}、false，停止读取且不返回部分正文 |
| CANCELLED | 按取消结果而非确定性任务failed/领域staleReason表达；后续GatewayCallOutcome独立cancelled分支，安全说明仅停止本地等待/连接，已发送内容无法撤回。内部CANCELLED不可直接塞进当前error枚举 |

预留项的最终code/messageKey仍需与公共契约版本一起冻结；不承诺这里的候选名称直接采用。新错误严格空params、固定messageKey、retryable=false；不带endpoint/Location/凭据主体或版本/密文/材料/路径/异常正文。预览目标和范围另走可信窄接口，错误不扩授权。

公共 retryable 只说明在条件修复后用户是否可显式重新发起；它不授权自动重放，尤其不能证明请求未发送。现有 STORAGE_BUSY/ENGINE_EXITED/TIMEOUT 的true也不允许重放写入，必须先operation/job对账。I06的最多一次429/503内部重试仅由网关掌握，每次重新授权/配置/最终载荷检查；bridge恢复不得叠加重试。所有本表网关错误保守false；用户手动重新发送仍是重新检查的新请求。

后续必要验证：公共schema/错误配对/未知字段/安全参数/取消分支共用正反例；I06真实主进程→窄bridge→UI完整11类字段全集和四段式说明，检查无原值外泄、无自动重放、不因模型失败阻断本地保存。只读模块测试或枚举文件存在都不是接线完成。
