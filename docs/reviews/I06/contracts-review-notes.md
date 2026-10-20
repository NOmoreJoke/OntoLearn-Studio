# I06 S3 公共契约子任务记录

2026-10-21；独立 worktree `I06-model-contracts` / `feature/I06-model-contracts`，base `1d9f784f5ab6dae58c1df5b811970cb50218c5e7`。仅维护授权的7个 contracts 文件、本专属记录与 `tests/unit/i06-model-contracts.test.ts`；protected AGENTS SHA `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786` 保持未提交。不采用未批准 I05 候选，不改 Python/build/依赖锁/CI/窗口安全代码，不 push。

## 可消费类型与唯一校验路径

`@ontolearn/contracts` 导出 ModelParamsMap / ModelResultMap / ModelMethod / ModelBridge；DesktopBridge 增加12个命名方法。配置、catalog、whole-result/fields 选择、预览、状态和独立 Outcome 类型均在同一入口。字段选择回传已选 fields 描述（fieldId/label/type/nullable/requires），fieldIds 与其集合严格相等；requires 只能指本目录/已选集合且无重复/环，不返回列 key、原正文或自报来源。

`@ontolearn/contracts/v2` 导出 `isModelMethod`、`validateModelParams`、`validateModelResult`（校验 data）、`validateModelReply`（完整 BridgeResult）、`validateModelValue` 及 `matchesModelResult`。后者绑定配置/规范端点、凭据并发版本、选择结果/目录/句柄、单 invocation 和 privacy 回显；它不能代替 main 的真实项目、存储及用户确认门。

`registry.mainRuntime/mainCapabilities` 独立列出12个 main-only 方法，owner=main、agentEligible/pythonEligible=false。原 productRuntime、v2Runtime、job capability、hello 枚举不变，main 方法不能通过 Python envelope。JSON Schema 只用已支持词汇，没有要求改 Python 编译器；模型跨字段语义只由 main 专门校验器执行。普通 `validateV2` 拒绝 model* schema，防止绕过专门门；引擎256KiB预算保持。

主进程专门校验允许 completed 文本最多1MiB实际 UTF-8，同时对整个 main DTO 施加2MiB有界估算/32层保护。无效 Unicode、循环、undefined、额外字段、非规范输出端点、混合项目、重复 ID、超量活跃/终态及取消分支混杂均拒绝。byteCount/rowCount 的准确值仍须由实际来源服务计算：契约只检查形状与64KiB/1024行边界，不能凭数字或 hash 证明实际字节。

configureModel 的创建 ID/version 同 null，更新同 UUID；storeModelCredential 必需实际 main 签发的 configurationVersion 作并发前置。返回新版本不得等于录入时版本；真正旧目标→新目标竞争、密文发布/配置原子安装仍由 main service 实现和联验。displayName/no-op 可同配置版本，不强制无意义轮换。

无实际项目时 contextId/projectId 必须同 null、availability=unavailable、privacy=local，选择/调用为空；应用配置列表仍可显示。非 null context 只是并发上下文令牌，实际 main caller/项目许可不可由 DTO 自证。状态上限32配置、64选择、4活跃+64终态；字段16、调用材料64。未知/跨项目授权、来源映射和最终 payload 仍由实际 owner 核验。

## 固定错误与取消

按 I03 disposition 和本轮唯一 owner 确认，10个 GATEWAY_* 包含 GATEWAY_INVALID_INPUT；精确 code/messageKey/严格空 params/retryable=false 全在原唯一 errors catalog。`modelGatewayError(code:unknown)` 显式映射10个内部码；未知输入返回固定 INTERNAL_ERROR。`modelInvalidRequestError()` 专供公共形状错误，固定 INVALID_REQUEST/protocol.invalidRequest/{field:'params'}/false。

CANCELLED 不在公共 error 中，必须先映射独立 cancelled outcome（externalEffect=unknown）；不得把该私有码直接传给错误映射当取消实现。cancel 方法回执只允许 cancelling 或已终态，不能在成功受理后仍声称 running；getOutcome 仍可返回 running。所有 retryable 均不授权 bridge/恢复重放，模型失败也不能证明此前未发送。

结果 schema 没有 secret/credentialRef/credentialVersion/ciphertext 字段，只有凭据录入 params 允许 secret；未知字段、错误参数与上游自选 messageKey 被严格拒绝。schema 不证明不透明字符串的来源，也不替代实际正文/日志/导出及可信字段发送链。

## 实际验证及内部独立审查

本线独立 `npm ci --ignore-scripts`、`uv sync --frozen`。完成 contracts/unit TypeScript 检查及指定文件 lint/格式/diff；定向运行新 main 契约 corpus、原 contract-v2 与原 binding-regressions，合计635项通过。main corpus 新增147项正反例、24项请求/结果绑定，旧 corpus 不重写为 main case；专属测试覆盖1MiB单/多字节、取消、错误与 registry/输出秘密字段排除。原 Python `test_contract_v2.py` 433项通过；另用未修改 Python checker 对51个有效 main case 做结构校验，确认相同有限 schema 词汇可读，不声称 Python 实现 main 语义。

真实 resident coordinator CLI 验证 hello 返回原14项运行能力及完整 registry hash `730613e019f49e19d834c1eced78c16b188488e8fd3ca4c1161b1734381f753f`；保持 stdin 开放，注入 getModelAccessStatus 后会话终止，无附加 stdout/stderr、未执行 main 能力。实际 exit=0 是 coordinator 的协议拒绝清理语义。首次探针误把“拒绝必须非零 exit”当断言，失败保留于工具输出；核对实际 serve 路径后改为检测保持 stdin 开放仍终止，未修改产品让其迎合错误断言。定向检查也曾发现专属测试缺少 registry 方法 type guard、lint 不允许控制字符 regex，均已修正对应源码/测试后通过。

内部独立只读 agent `contracts_review` 核验全部指定文件和24项绑定样例，发现 cancel 成功回执允许 running：已同步收窄 TS 与 schema、补负例；审查者实际读回执行确认关闭。其余未发现未关闭的可复现问题。该内审不替代指定 GLM-5.3/最高与 MiniMax M3.1-Flash/xhigh 同版全范围双审。

本子任务不运行全库/桌面/native/Keychain，不声明 main/preload/UI 已接好、真实字段外发或平台/Store/导出通过。根正常合并后需对实际完整候选运行对应检查与接线反例，旧独立/契约通过不等于 I06 完成。
