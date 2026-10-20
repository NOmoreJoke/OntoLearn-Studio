# I06 主进程接线交接约束

2026-10-21。此文件供总控在 I05 接线稳定或完成后组织唯一 owner 交接；当前没有注册公共模型能力，没有要求 I05 实现 S3。下列“可消费”仅指已经实现的 main 内部接口，不表示公共契约已经批准。完整验收仍按原 S3 和总控 `I05-I06-controller-completion-evidence-map.md`。

## 现有私有模块可消费接口

| 接口                                           | 输入与结果                                                                                                     | 调用约束 / 失败行为                                                                                                                                                                                                                                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PrivateCiphertextRepository.open(location)`   | `{ userDataPath: absolutePath, excludedRoots: absolutePath[] }` → repository；路径 ≤4096 字符、排除根 1–128 个 | 只能由可信 main 提供真实 app userData、项目及可用导出根。固定 `model-gateway-private-v1/credentials`；任何祖先/后代相交均拒绝。POSIX owner/mode/目录身份与原始祖先信任检查失败时 `CREDENTIAL_UNAVAILABLE`。当前 Windows ACL 未实现，明确拒绝。                              |
| `createElectronCredentialBoundary(repository)` | 现有 `CiphertextRepository` → `EncryptedCredentialBoundary`                                                    | Electron `process.type=browser` 且 app ready 后。实际 safeStorage 每次读写再次检查后端；Linux basic_text/unknown/不可用拒绝，不回退明文。factory 不打开窗口，不创建自己的 Store。                                                                                           |
| `boundary.store(principal, secret)`            | UUID 主体、1–4096 位可打印 ASCII secret → `{ref, principal, version}`                                          | secret 只停留于 main 调用栈及平台加密 API；repo 只接收密文。生成新 ref/version，不覆写旧密文；返回不含 secret。绑定与密文内身份逐项核对。读取 secret 的 `read(ref)` 结果只允许注入 gateway，不能出 main。非法输入 `INVALID_INPUT`，平台/存储失败 `CREDENTIAL_UNAVAILABLE`。 |
| `PersistentGatewayAudit.open(location)`        | 同上 location → `AuditSink`                                                                                    | 固定私有 `audit` 目录，与项目/Job 数据没有第二权威关系。仅 metadata；严格 UUID/用途/范围/事件/原因/规范 origin/time。已发布损坏记录拒绝恢复并保留文件，错误 `AUDIT_UNAVAILABLE`。                                                                                           |
| `audit.append(record)`                         | 现有 `AuditRecord` → `Promise<void>`                                                                           | 临时文件独占创建、文件同步、同目录硬链接无覆写发布、删除自身临时名、目录同步及身份复核全部成功后才 resolve。失败不得发送；最终文件即使已存在也不删除，不把失败当成功确认。重开只读历史，绝不重发 intent。                                                                   |
| `repository.close()` / `audit.close()`         | 无参数 → `Promise<void>`                                                                                       | 拒绝新操作并等待已接纳工作，再关闭目录句柄。单实例最多 32 项 private 操作，超量立即固定错误。main 不得先关闭依赖再继续发送，也不得为失败存储创建内存成功替身。                                                                                                              |
| `new ModelGatewayCore(boundary, audit)`        | 已就绪的两个私有实例 → gateway                                                                                 | 产品默认 HTTPS；`loopback-probe-only` 仅测试可用，不由 renderer 设置。不允许 Python 或 renderer 持有 `OpenCredential`/transport。当前合成 wire payload 仍受 Q9 未决约束。                                                                                                   |

`listBindings()`、`readEntries()` 是 main 内部恢复/诊断方法，不是 renderer 的凭据或审计批量查询权限。全部私有模式使用严格 schema、有限字节和已发布记录完整性摘要。SHA-256 检测损坏，不声称防御完全控制同一 OS 账号的攻击者。私有目录 0700、文件 0600；不自动修复既有放宽权限。只有 root 拥有的系统路径别名可作为原始祖先（例如 macOS `/tmp`），最终 userData 本身不能是 symlink。

准入阈值为 credentials 4096、audit 10000；它们是单次观察的内部资源保护，跨进程不承诺原子计数。合法小幅并发越线仍可恢复；总目录枚举有界 11024 项（包含 pending），超过后失败关闭并保留证据。未发布 pending 不读作成功，也不自动清理其他进程可能仍在写的临时文件。禁止把这些数值写成 Q5 产品容量或性能指标。

## 现有授权与材料调用顺序

1. 可信 owner 验证当前项目与选择，读取有权限的真实 Store/Job 结果。需要解释已有结果时，验证项目、producer、输入/版本、真实内容 hash、当前/历史身份、完整结果及依据来源；缺损/已回收拒绝，不按当前规则重算冒充旧结果。这部分消费 I05 的已批准能力，当前不自行定义第三份协议。
2. main 调用 `registerMaterial({projectId, scopes, kind, text})` 建立不透明 handle；`kind` 为 selected/tool/history/summary/error。不得使用 renderer、Python、模型文本或导入内容自报的 scope 作为授权事实。派生材料调用 `deriveMaterial({projectId, inputs, kind, text})` 保留输入 scope 并集。每份最多 256 scope，调用至多 64 份材料，总唯一 scope 也至多 256；超限在建立审计 metadata 前 `INVALID_INPUT`，不截断来源。
3. `configure({id, endpoint, credentialRef, principal, credentialVersion, model})`，返回 `{id, version}`。配置 ID 是身份，不是显示名；当前 core 没有显示名字段。相同规范配置复用版本；endpoint/主体/凭据版本/model/新身份变化撤销对应 grant/preview 并取消关联等待，不改变领域 staleReason。
4. 项目默认 local。经明确用户选择用 `setPrivacy(projectId, minimal|project)`；`previewAuthorization({projectId, configId, purpose, scopes})` 返回真实规范 endpoint、主体、配置版本、范围、隐私档。真实 UI 展示该预览后，可信确认动作才调用 `confirmAuthorization(previewId)`。不得由后台自动确认，或将工具读取权自动视为外发同意。
5. `invoke({projectId, configId, grantId, purpose, materials})` 只用 main 已复制的字节和 handle。凭据、持久审计及 socket 发送前逐次重检。撤销用 `revokeAuthorization(grantId)`，项目关闭用 `closeProject(projectId)`，材料释放用 `releaseMaterial(id)`。窗口重连只查询既有状态，不重新 invoke/确认。网络错误不自动重放；429/503 至多一次内部重试，每次重新检查并先持久记录。

生命周期应由主进程项目服务持有，与可重建窗口分离。模型模块初始化、超时、凭据不可用或审计失败只能禁用相应模型操作；不得使本地 Store 启动/保存/历史读取依赖模型初始化成功。接线时需要真实 Store 保存/失败隔离与窗口重建证据，当前独立模块和 loopback probe 不能代替。

## 未来公共契约扩展：尚未批准

- 当前 contracts 没有 S3 公共 capability，不直接把私有 zod 类型或方法名注册成 IPC/JSON-RPC。新版本由唯一公共 owner 冻结 TS/Python schema、registry、正反例及安全错误，之后才接 main/preload/UI。
- 凭据录入需要最窄的受信调用，输入只用于 main 加密，响应不回显；不得新增通用 `request(method, params)`、任意 URL/headers/body 转发、secret 读取或批量 vault 导出。是否持久化非秘密模型配置、凭据轮换/旧记录回收策略仍需正式生命周期设计，不将当前不可变文件当可无限积累的产品方案。
- [I03 错误 disposition 读回](public-error-requirements.md) 保持：现有通用错误仅安全兜底；精确网关错误需要新契约/公共正反例和完整双审。固定 params、messageKey、retryable 来自批准表，不透传 upstream body、路径、平台异常或凭据。未来公共取消是独立结果分支；当前私有 `CANCELLED` 不能原样作为公共错误或领域 staleReason。retryable 不授权 bridge/重连自动重发，写任务先对账。
- Q9 模型协议未决；当前 `{model,parts}` / 合成字符串响应不是公开支持的 provider 协议、结构化输出或工具调用。不得借测试静默冻结 provider。

## 涉及的共享文件及交接后检查

以下仅列未来接线面，本阶段未修改；具体变更需在总控交接唯一 owner 后落地并纳入同一候选双审：

| 共享面                     | 当前文件 / 范围                                                                                | 应核对的行为                                                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| main 生命周期与受信 sender | `apps/desktop/src/main/index.ts`、`task-service.ts`、`trusted-document.ts`、window-*           | 私有实例 app ready 后初始化/退出排空；sender/mainFrame/document 门；项目切换/关闭、重连不重放；模型失败不阻断 Store。            |
| 窄 bridge / 展示           | `apps/desktop/src/preload/index.ts`、`apps/desktop/src/renderer/src/App.tsx`、env/呈现相关文件 | 明确用户同意和窄方法，禁止秘密查询；安全错误和独立取消分支贯通，不信任 UI 自报身份/范围。                                        |
| 唯一公共协议               | `packages/contracts/src/`、`packages/contracts/v2/`、`packages/contracts/python/`              | 同一版本 schema/registry/fixtures/错误映射，Python 不得新增模型凭据或外发入口。                                                  |
| 真实 Store/结果/导出       | I05/I04 所有的实际服务与持久化实现                                                             | 从真实权限与不变结果派生材料；用合成标记核验实际可用保存/导出/普通日志排除，模型失败、重连不破坏保存。不存在的导出器不伪造成功。 |
| 构建/入口/依赖/CI          | app build/package 脚本及共享 CI、锁文件                                                        | 正式打包确实包含唯一 gateway；真实候选运行链和实际平台 CI，不以纯模块测试替代。当前不要求新增依赖。                              |

隔离 Linux 实测、实际文件故障与内部独立审查的结果只按各自 source hash/环境引用。macOS/Windows 平台加密、Windows ACL、签名升级/干净设备保持待验。完整正式链和指定 GLM-5.3/最高、MiniMax M3.1-Flash/xhigh 同一冻结候选双审通过前不 push；之后仍须 PR→develop、实际 CI 和远端合并核验。
