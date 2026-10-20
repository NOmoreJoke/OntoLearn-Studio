# I06 主进程接线交接约束

2026-10-21；对齐开发实现 `9fcba6634d5c16983c36ef671d4ec8e79694b6d6`，批准依赖 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`。本文件取代此前“公共方法尚未注册”的提案口径；当前 12 个专名方法已经在本开发分支 main/preload/UI 接线，精确参数见 [命名接口](narrow-interface-draft.md)。完成度与验收待办只由 [status](../../reviews/I06/status.md) 维护，不采用 I05 未批准 C1/C2。

## 运行 owner 与责任

总控已将约定的精确 14 文件交接 I06 唯一维护，见 [接收回执](shared-owner-acceptance-20261021.md)：contracts 的 index.ts/v2.ts/schema/registry/errors/fixtures/binding-regressions，main index/task-service/engine，preload index，renderer env/App/style。该权限不扩展到 Python Store/job/worker/protocol、入口 build、依赖锁/CI、CSP/窗口安全/恢复文件；新增必要变更须先协调精确路径责任。独立文档、契约、平台和只读审查各有独立 worktree，不能争写 root。

main 的 `ModelGatewayService` 为 app 唯一配置、授权与调用 owner。app profile 单实例锁阻止第二主进程继续持有旧授权。TaskService 仅把实际主项目变更通知 `selectProject`；renderer 不传项目身份。每个 context 默认 local，持有 GatewayApplication、选择/目录/预览/grant 与最多 4 活动+64 终态 ledger；切项目关闭旧 application，使旧 context/句柄失效。窗口重建保留 owner，UI 读取状态/outcome cache，不自动确认/重发。main 重启不恢复执行、grant 或旧 response，持久审计仅恢复 metadata。

所有 12 个 IPC handler 先验证可信 sender/mainFrame/document，再按固定专名验证 params；mainCapabilities 不进入 Python 方法表。`handle` 复制输入，并对输出执行 validateModelResult/matchesModelResult。配置保存及来源读取后复核同一 context，旧 UI 的结构合法请求仍会被权限拒绝。字段描述、requires 闭包、whole/fields 的实际 rowCount/byteCount 和 cancellation 独立状态均贯通，UI 只按文本展示输出。

## app 初始化、私有存储与退出

| 模块                                           | 实际约束                                                                                                                                                                             |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `PrivateCiphertextRepository.open(location)`   | main 提供 app userData 与实际 Store db/wal/shm 排除根；固定私有目录，POSIX owner/mode/原始祖先/目录身份复核。Windows ACL 尚未实现时明确拒绝。任何相交根拒绝。                        |
| `ConfigurationRepository`                      | 仅非秘密配置与凭据 binding，严格有界；串行 owner、持久 CAS/发布。持久结果不确定则 fail closed，不能继续用旧内存配置/grant。                                                          |
| `createElectronCredentialBoundary(repository)` | app ready 后实际 Electron browser safeStorage；Linux basic_text/unknown/不可用拒绝，无明文回退。secret 仅传平台加密 API 和唯一网关，不出 main。                                      |
| `boundary.store(principal,secret)`             | secret 为 1–4096 可打印 ASCII；主体/ref/version 由 main 生成，密文严格绑定，生成新 immutable 记录，不覆写旧密文。公开 store 另核对 expected configurationVersion，并返回新配置版本。 |
| `PersistentGatewayAudit`                       | 只保存受限 metadata；独占 temp、fsync、同目录无覆写发布、目录同步/身份复核后才准发送。损坏记录拒绝恢复并保留，失败不能补造成功。恢复不重放 intent。                                  |
| `ModelGatewayCore`                             | 产品 HTTPS，仅 main 私有测试 policy 可用 loopback；凭据、持久 audit 和 socket 发送前重检；拒绝 redirect，429/503 最多一次内部重试。响应 1MiB、fatal UTF-8 解码。                     |

私有目录 0700/文件 0600，最多 32 项 private 操作；credentials admission 4096、audit 10000、总枚举 11024（含 pending）。内部资源界限不是 Q5 容量承诺；并发越线不宣称跨进程原子计数。pending 不当成功、不删除其他进程可能仍写的原件。SHA 只检测损坏，不防御完全控制同一 OS 账号者。旧密文不自动回收，产品回收策略仍需后续设计。secret 录入控件提交后清除，但 JS 字符串不承诺物理内存清零。

模型初始化独立于 Store/窗口启动，失败只让模型 unavailable；不能创建内存“成功”仓库替代磁盘错误。退出先取消模型等待并排空私有操作，再停止 tasks/engine，整体等待上限 5 秒；同步 OS 凭据提示无法靠 JS timer 撤销，不能将退出上限表述为平台提示已可取消。当前 Mac 不启动 GUI/Keychain，实际原生行为在隔离环境或授权窗口验证。

## 真实配置与调用顺序

1. `configureModel` 新建为 configurationId/configurationVersion 双 null，更新为双 UUID，后者必须匹配 owner 版本。endpoint 规范化后变化产生新版本并清凭据，key 不沿用到新目标；model 变化更新版本但可保留同 endpoint binding；displayName-only 保留身份/version。凭据轮换必须带预期配置版本，生成新配置版本并撤销对应预览/grant。
2. `selectModelResults` 真实完整读取批准 I04 来源；批次成功替换，失败保留旧选择。`getModelFieldCatalog/selectModelFields` 只接受 main 有限模型产生的 catalog/field ID，包含类型、nullable 和 requires 闭包。普通生产模型列表为空，未知 shape 拒绝；有限 launch fixture 是 main 绝对 path+env+unpackaged/test-runtime 条件，不由 renderer 开启。
3. 用户明确设置 minimal/project，main `previewModelExplanation` 重读来源并返回精确 endpoint/配置版本/主体/范围/状态；确认动作才签发 grant。reusable 由 main scope/版本/privacy/purpose 计算，UI 不自报。字段 grant 与 whole-result 分开，允许同源且已选字段不变的新真实 worker 结果复用授权，不把未选列带入。
4. `startModelExplanation` 立即登记 invocationId/running，异步失败由 `getModelExplanationOutcome` 独立 failed 分支返回。cancel 只对单 invocation，cancelling 不等于远端未收；cancelled.externalEffect=unknown。释放选择/中间派生祖先定向取消所有依赖后代；窗口重连、retryable 或 audit 恢复都不重新 invoke。
5. 实际 EngineError 使用批准 catalog/受限参数；10 个固定 GATEWAY_* 错误 params={}、retryable=false；格式错误固定 INVALID_REQUEST 的 field=params。内部 CANCELLED 只投影独立 cancelled，不透传 raw error/body/path/key。endpoint 已变且未新录入凭据时 start 先拒绝 CREDENTIAL_UNAVAILABLE；新凭据录入后旧 grant 仍已撤销，不能借重新 running 绕过异步授权检查。

## 来源、字段与证据边界

`StoredResultSource` 固定实际 EngineSupervisor/项目，读取 project/result/job/全页 rows 并重读身份；无第二 SQLite writer，不重算 evicted 历史。metadata/hash 不是外发权限。明确历史版本是 PRD D/F 已允许语义；current 不静默降为 historical，UI 展示实际 version、read-time-state、选择模式。读回到 socket 的跨 Store 变化窗口必须披露；检测到变化时保守拒绝，发送边界仍重检配置/凭据/grant/材料。原 S3 不要求所有写者/socket 原子 live-current lease；更强持续 current 承诺才另审。

有限字段来源模型绑定完整 main policy digest、producer/definition/精确 implementation、项目/输入/参数/依赖和实际有序字段值。目录绑定具体 result/job/完整副本以重读，scope 身份另允许同源不变字段复用。tool/history/summary/error 仅用允许投影重建；无法证明的任意 text 拒绝。外发不含原 row UUID/ordinal、未选列与相关派生值、完整输入/参数 hash。原 UUID/ordinal 泄露反例及祖先释放反例已在字段阶段修复，按原 hash 保全，不以新漂移源码代替旧证据。

当前策略是固定 main 合成 policy + 批准 test.read echo worker。static dependsOn 不是 worker 计算出的生产溯源；未批准 I05 的 `i05-finite-3` 不作为最终常量。真正 I05 特定业务模型仅在其新语义实际批准合并后绑定、刷新冲突并重验。A-03 有限证明不要求全 M1 CSV、恰好两个 API 或 I05 编号前置。

旧私有字段实际请求完整字节已有执行断言，独立 probe 未保存成功 HTTP 原 body，不能声称独立重扫归档正文。新正式平台证据须在忽略目录保存仅合成 receiver 完整 body 和 hash，排除 headers/凭据/业务数据；产品日志/导出仍不记录 payload。当前批准基线无导出入口，不能用不存在的导出器或 mock 计通过。Q9 真实 provider 未决不阻止既定合成 S3 验证，也不使 `{model,parts}` 自动成为公开 provider 协议。

本次文档对齐仅执行四个同版 validator、ID 保全和格式检查；已有 998 TS/1052 Python/check/source12 是根线固定实现验证回执，本子任务不重复或扩写为平台通过。新 main/preload/UI/safeStorage/Linux 实际运行及其他平台、完整指定 GLM-5.3/最高 + M3.1-Flash/xhigh 同版全范围双方审查、PR/实际 CI/远端合并均以 status 追踪；旧私有 Linux 结果不继承为当前全候选通过。
