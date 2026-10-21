# I06：正式语义与真实导出的最小接线请求

2026-10-21。只读当前 I06 产品 `e2c269ad`、本次远端批准 develop `5f910b52`、PRD FR-806/901/902/904/1000/1001 与总控 T10 责任登记。本文是待相关 owner 冻结的接口及验收请求，不新增方法、共享写权或实现通过。e2c 原件/原生回归已收口；不为此重跑旧矩阵。

## 1. I05 实际语义结果：已有接口与真正缺口

当前 `StoredResultSource` 已使用 `EngineSupervisor.request` 的 `project.get → result.get → job.get → result.page → result.get/job.get`，全程检查同 session、项目/result/job 归属、succeeded/可用 payload、完整输入/implementation/dependency 绑定、页游标/顺序/字节界限及末次重读。current 必须实际 current；显式 historical 保留读时状态，不自动降级，也不承诺 socket 时仍是 live-current。无需为整结果读取另造公共 API。

| 对接项                           | 相关 owner 交付                                                                                                                                                             | I06 消费与可验结果                                                                                                                                          |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 实际 producer                    | I05 提供已批准合并的 query.execute/reasoning.execute/validation.execute 实际 runtime 结果；由 canonical 唯一 owner T01 同版登记，不能把当前 proposal 直接改名 runtime       | 对应 kind=query/reasoning/validation，真实 Store/job/result/page 闭环；未批准或未知 producer 仍拒绝                                                         |
| 版本身份                         | 冻结真实 executionSemanticsVersion、engineVersion、dependencyLockHash、definitionId、parametersHash、dependencyVector/definitionSetDigests；给源/实际包同输入原件及批准 SHA | 不预填未批准语义常量；同次读取/发送准备中的预期身份、implementation、页绑定或末次重读漂移拒绝；合法新结果按实际 scope 核授权，不按裸 result/job ID 决定复用 |
| 失败与历史                       | 实际空结果、失败/取消无成功结果、stale/显式历史、payload 回收、页上限/游标失效样例                                                                                          | 只传固定安全错误；禁止原异常/路径泄漏，禁止 current 静默转历史；模型失败不阻断本地任务/Store                                                                |
| 正式字段选择（若该业务对外启用） | owner 给可核验的稳定字段 key、类型/空值、列位置、实际派生依赖与 producer/definition/implementation 精确身份，按实际业务冻结有限 main policy                                 | 生产默认 fieldModels=[] 保持。不能从 renderer、结果 tag 或未经证明的 dependsOn 推断权限；未知/歧义 schema 拒绝，派生字段依赖未授权则拒绝                    |

同次读取链的 result/job 身份必须精确绑定；新的合法 result/job/catalog 不单独撤销授权。已证明字段 scope 以及项目、用途、端点/配置/凭据等其他授权绑定均保持时，可以复用旧 grant（A03 已验边界）；整结果仍按其真实材料范围核对，不把字段复用规则扩大为任意新内容复用。

实际来源：`apps/desktop/src/main/model-gateway/stored-result-source.ts`、`stored-field-projector.ts`、`model-service.ts`。整结果读取和正式字段溯源是不同验收；现有有限 A03 不扩成“全 M1 CSV 溯源”，也不把全部 M1 能力作为与它无关的 S3 核心的统一前置。

正式语义实际合入后，I06 与唯一维护者协调 contracts/engine 冲突；本线不再修改已交出的八文件。I06 专属材料/投影/网关模块可按真实接口变更适配。只有真实 delta 才新增必要反例或复测；旧 9fc 领域专项仍只绑定 9fc，未来完整组合候选另验。

## 2. T10 真实导出：需要的接口边界

总控登记 T10 独占 `apps/desktop/src/main/project-transfer/`、engine `transfer/`、renderer `transfer/` 及专属测试。当前 I06 canonical 中没有 export capability；main 初始化私有目录只排除实际 DB、wal、shm。因此当前证明限于项目数据库排除，**尚无真实导出/导入排除通过**。

I06 私有内容位于 main 取得的 userData 下 `model-gateway-private-v1/{credentials,configurations,audit}`；另有 main 内存中的 context、grant、preview、发送 ledger。凭据不可读回给 renderer/Python；metadata-only 审计也不因此成为项目导出载荷。项目的正常配置/版本与这些 profile 私有网关状态须分别建模，不禁止 T01/T10 自己合同内的合法项目配置和应用历史。

T10 需提供以下最小、main 受信的合同和实际样例；名称由其唯一 owner 冻结，I06 不私造第二套实现：

1. **范围与根路径**：导出选项、清单/格式版本及 main 解析的源项目/目标/staging/backup/import-unpack 根；renderer 自报路径或排除数组不能成为权限依据。I06 需要在实际打开/切换位置时校验这些根与私有目录不相交，或由双方冻结等价的受信白名单读取边界。现有 `PrivateLocation.excludedRoots` 集合在 open 时固定，并在后续 private I/O 重验已登记根；尚未接入的动态 export/staging/unpack 根没有因此自动登记，不能据此宣称真实 exporter 已覆盖。
2. **载荷白名单**：从正式 Store/domain/application 投影取明确数据，禁止递归复制 userData、任意工程目录、私有 vault/config journal/audit，或将它们作为附件/日志/失败 dump 打包。credentials 即使是密文也不得混入；旧 context/grant/preview/发送记录不可恢复为新授权。
3. **完整与模板语义**：FR-1000 的当前事实/来源所有权/实际清单及可移植引用、可选原始数据/历史/Agent 会话各有明确范围。排除私有凭据不能使完整包静默丢失合法业务内容；缺少外部依赖、版本或语义须说明，不能伪称可重跑/重放。
4. **重新导入**：新上下文默认 local，导入的模型文本、配置和会话只作为数据；即使同一 profile 有可用凭据，也不得用包内旧 grant 自动发送。经原合法选择/预览/确认后才可外发。
5. **错误与报告**：导出成功/失败/取消/恢复、manifest、HTML、项目库及日志不包含凭据、令牌、密文私有原件或原始异常；HTML 对模型/业务文本按实际位置编码，离线不自动加载远端资源。失败路径和临时目录也在实际扫描范围内。

若接线确需 I06 仍持有的 `main/index.ts` 或 `task-service.ts` 生命周期钩子，T10 先给精确 diff/调用时机/受信参数和失败处理；由 I06 代改或逐文件安全交接。若需 canonical/engine 变更则由 T01 统一维护。本文不授予其余共享路径、旧测试、CI 或 resources 写权。

## 3. 同候选实际验收输入

| ID          | 必需直接证据                                                                                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| X1 范围     | 真实完整包/模板包/HTML/可选会话与未选历史，清单和实际成员逐项相符；失败/取消的临时产物亦核对                                                                             |
| X2 私有排除 | 隔离合成配置/凭据/授权/audit 注入区分性标记，逐成员扫描实际导出字节、manifest、HTML、库页/日志/临时产物；同时比对私有密文原件 hash/字节，不能只搜 plaintext 后称排除成功 |
| X3 路径     | 真实 DB/用户指定项目/导出/staging/backup/unpack 的包含、祖先、符号链接和重新打开反例；私有目录与项目范围重叠时安全拒绝                                                   |
| X4 重新打开 | 实际导出→导入到独立 profile，以及同 profile 重新导入；context 新建、旧 grant 不结算、不自动发请求，用户实际确认前 receiver=0                                             |
| X5 本地保存 | 模型启动/审计/网络失败、取消及窗口恢复期间，真实当前 Store 操作/receipt/域状态与应用 CAS 保留；只读恢复不重放发送或领域写任务                                            |
| X6 包内     | 源码与实际新包同输入，固定 source/canonical/implementation/包实物/逐门原件；未知版本与缺少依赖按有限错误拒绝，不以 overlay 或替身代替                                    |

X1–X4 必须使用真实 T10 入口；尚不存在入口时保持未验，不用假 exporter 关闭门。X5 的 9fc 原平台证据保留原范围；最终受影响候选的真实保存/窗口/导出组合另验。既有专属测试若已覆盖且无 delta 不重复；新增跨模块测试路径由相应 owner 提案登记。

后续同版指定 GLM-5.3/最高、M3.1-Flash/xhigh 完整外审及真实 CI/远端合并要求保留。目前没有获准的安全审查桌面入口/时段，不启动当前 Mac GUI。S3 合成协议证据也不扩大为 FR-900 真实服务、结构化输出或工具调用已验。
