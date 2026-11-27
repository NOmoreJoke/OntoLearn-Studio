# T01 业务3 canonical 校验采用与后续运行时边界

本候选只新增唯一 canonical 内的 business3 校验分支、完整跨端 fixture 与绑定助手；生产默认协议/格式2、coordinator 的3启动守卫、主进程握手均保持。运行状态以 [status](../../reviews/T01/status.md) 为准。

## 固定依据及采用范围

- T01 `format3-foundation-contract.md` SHA256 `d435f2340ddda8d77e1f74c9291a7de64dfcac2fba1ba2d3834c6e24498c9855`。
- 总控 `T00-project-format-version-proposal.md` SHA256 `c4f32d24367929d137ac49be7c3a8610135116cb70e26340a41864145a1610a4`。
- 总控 `T00-project-format-version-review.md` SHA256 `1c4a0607a690c078ed0b50e62ccb24235b26d1aa78751a787e912a559e2c9098`。

只在原 `schema.json` 的 `$defs` 添加3分支，registry/errors 增 foundationProfiles.business3；原2分支、能力、生产入口及错误码不变。目录名/容器 schemaVersion2表示原资源容器，不把它当业务版本；业务3外层和 Project.formatVersion3另以严格定义约束。没有注册 source、parser、learning 或新应用IPC方法。

## 完整帧和绑定

`fixtures.json.business3` 保存完整 request/response/notification 值；固定UUID是合成身份，hello registryHash是当前 `registry.json` 原字节 SHA256 `04642f84124bc29ba3ee4092376e6c82d98c2e87a8353616734d0f419670dbc5`，两端测试独立实算比对，不把合成 a*64 当实际构建hash。

新客户端发 bootstrap2 hello supportedVersions=[3]、null session。hello成功仍外层2，selectedVersion3，内外新session完全相等且非null；后续请求/响应/通知外层3且严格session。Project只把已存在formatVersion改为3，保留其他精确字段，拒绝额外metadata字段。请求hello保留一般版本协商数组以识别旧客户端；成功只允许实际offer3。

null-session hello错误仅三种：VERSION_INCOMPATIBLE/supportedVersions=[3]、INVALID_REQUEST/field=params、SESSION_MISMATCH/空params，均固定 messageKey/retryable=false。旧引擎完整 VERSION_INCOMPATIBLE/supportedVersions=[2]只返回 incompatible-close；不授予session、不降级。混合[2,3]诊断、额外参数、错误retryable、其他null-session业务错误拒绝。

`matchesBusiness3Response` 先验证完整3信封/语义及真实预期hash，再在私有副本投影已知版本字面值以复用原严格 project/job/operation/input/confirmation/resource/page 绑定。投影不发送帧、不改调用者对象、不丢字段。事件同样先验3再复用原subscription/sequence/state绑定；完整原绑定反例另在同一 `binding-regressions.json.business3` 测试。hello outcome 的 success只表示待请求帧成立，不证明数据库ready；假hash即 invalid-close，真实监督器仍须使整个会话失效。

当前84 schema、15 hello、43 response、11 routing与41 trusted-binding反例由TS/Python消费同一完整JSON。TS另两项构建hash/default2检查，Python合并为一项，因此首跑196/195差1来自测试包装，不是覆盖数据差异。首跑日志单独保留；最终同版验证另记。

## 实际握手启用前必须完成

1. 同一构建加载原canonical字节，并固定 registryHash与schema/helper资源hash清单；主进程可信启动预期hash、引擎hello实值必须一致，不能从对端自报值生成期望。
2. 独占writer lease下 Store3完整验证/迁移、JobStore初始化/原任务对账均成功后才允许hello成功。任何失败关闭连接/进程并释放租约，不发送成功hello，不降库格式。
3. 固定受限结构化启动失败通道和不支持格式诊断，避免解析原始stderr/异常。需先提交准确schema、允许码、接收时机和main显示边界；当前未实现，不用null-session通配错误代替。
4. coordinator真实选3、发送/接收/通知均3；main绑定真实session/hash、重复hello/假hash/旧session关闭会话和清理pending。Store3裸打开或纯JSON通过均不能绕过ready。
5. 无窗口真实子进程验证新App/新Engine成功、旧App/新Engine和新App/旧Engine安全终止、启动各阶段失败、同chunk假hash后业务、旧session/重复hello/超时退出/重启、迁移/CAS/receipt真实闭环。旧App/旧Engine保留2路径。先固定准确测试和受信启动诊断，再启用；GUI/打包/native验收依总控隔离预约。

默认2与source/learning未齐能力保持，后续真实接线是新候选，须重新执行实际变化对应验证和独立审查。指定双模型审查、PR/CI、正常合并与远端核验要求保留。
