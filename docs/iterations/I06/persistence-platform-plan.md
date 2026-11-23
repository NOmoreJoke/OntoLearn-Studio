# I06 私有持久化与平台阶段（2026-10-21）

实际接续：原会话 01a15746-c2e2-7ee0-836b-c8c92346ddd4、feature/I06-model-gateway。正常 merge 已批准 develop `5f910b52c69d86a1076b2032e5d3c63e715947f3`，产生 `0c569851baa067a08ad8cf8d6d94437ef9620d69`。既有源码/测试与 protected AGENTS 哈希保全见 premerge 证据。原 Goal 工具仍返回 blocked，本阶段实际授权与依赖已变化；不重建 Goal、不假称存在 resume API、不将原状态当新阻断。

## 明确文件责任和并行

- 本会话只写 `apps/desktop/src/main/model-gateway/` 的私有目录/密文仓库/metadata 审计与原网关、专属 I06 单元/故障探针及 I06 文档；不编辑公共 contracts/registry/error/Store/job/main/preload/bridge/UI/protocol/entry/build/依赖锁/共享 CI。
- 独立子任务 platform：自己的 worktree/feature 分支，写 `model-gateway/electron-safe-storage.ts`、`tests/i06-platform/`、专属 `i06-platform-*` 测试与 `docs/iterations/I06/platform/` / `docs/reviews/I06/platform/`；准备自己的 Linux Docker/Xvfb/Openbox/secret-service，实际运行锁定 Electron 44.9.0。无主机 Electron/Keychain/GUI/CUA 操作。不共享其他线的可变依赖、容器、输出或运行数据。最终由本线正常接入子任务提交；不 push。
- 内部独立审查只读，不争写实现；不替代指定 GLM-5.3/最高与 M3.1-Flash/xhigh 双审。审查应用预约现归 I05，本线不占用。

## 内部接口和实现方向

- 保留现有 `CiphertextRepository` 与 `EncryptedCredentialBoundary`：实际仓库只接收密文 Buffer 和不透明 binding，不接收 secret；密文内部绑定 ref/principal/version，读取逐项匹配。
- 仓库 `PrivateCiphertextRepository.open({ userDataPath, excludedRoots })`：仅可信主进程传入 app 私有 userData 与真实项目/导出根；固定私有子目录，拒绝与这些根相交、符号链接/错误 owner/不安全权限。凭据 ref 为 UUID、固定文件后缀，不接受任意路径。临时文件独占创建、写入与 fsync、同目录原子发布、目录 fsync；既有 ref 不覆写。恢复只接受完整且严格校验的已发布记录，未发布临时记录不视为成功。
- 审计 `PersistentGatewayAudit.open({ userDataPath, excludedRoots })` 实现现有 AuditSink；每项最小记录独立不可变文件原子发布，避免共享可变 journal head/跨进程部分追加。字段严格白名单及有限范围，附记录身份/完整性摘要；读取/恢复拒绝损坏已发布记录，不删除历史，不从 intent 自动重发。append 在实际持久边界成功后才 resolve，失败网关 fail closed。
- 平台 factory `createElectronCredentialBoundary(repository: CiphertextRepository)` 只能在 Electron 主进程 app ready 后使用实际 safeStorage，返回既有边界。真实 API/后端事实由独立 Linux 容器验证，basic_text/unknown/unavailable 拒绝，不以 Node 模式或 mock 充当平台证据。实际新私有仓库与 factory 的组合探针在两模块整合后补齐。
- 数据模式/常量均是私有持久化，不形成第三份公共协议。I03 既有 disposition 和 I05 唯一公共契约维护权保持；精确接线前仍须统一新契约与正反例、当时指定双审。

## 可信边界与必要交接

主进程需提供可信 userData、项目根及导出目的地边界；这些参数不直接来自 renderer/Python/模型。0700/0600 及符号链接防护针对其他系统用户/意外重定向，不能声称抵御可完全控制同一 OS 账号或内核的攻击者。真实项目/导出能力未接线时，仅能证明此私有存储的数据边界及故障行为，不能据此声称产品导出已排除或 Store 保存联验通过。

之后唯一接线 owner 需负责：主进程私有实例的构造/关闭、凭据录入窄方法不回显、配置身份与授权生命周期、持久审计注入、可信材料/工具读取来源、公共错误/独立取消结果，以及真实 Store 保存/窗口重连/导出失败隔离。模型配置只撤销外发授权，不产生领域 staleReason；Q9/真实模型协议保持未决。

## 验证范围

实际文件权限、原子发布与提交前中后故障/进程退出、重复 ref/损坏/未来格式/越界及链接反例、重开恢复；持久 metadata 与原网关本地假接收端组合验证零正文/凭据日志泄漏与审计失败拒发。新基线执行相应 check/verify:sources；独立平台探针证据记录 Electron/Node/OS/后端和源 hash，不启动本机窗口。Linux 证据不外推 macOS/Windows/签名升级或干净设备。
