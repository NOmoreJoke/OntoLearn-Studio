# 完整首版发布证据

T11 的版本化证据工具入口是 `scripts/release/verify-release.mjs`；它只做离线一致性核对，始终输出 `releaseAuthorized:false`。发布决定仍由原总控按完整 P0、指定双模型、实际 CI、真实双平台和渠道门执行。当前进度与缺口只维护在 `docs/reviews/T11/status.md`。

## 证据清单 v1

唯一 schema 是 `scripts/release/verify.ts` 的 `manifestSchema`。不再维护另一份 JSON schema 或 builder 配置。`tests/unit/t11-release.test.ts` 的完整合成样例展示所有字段；样例身份、签名和参与者均为测试构造，不能转作实际证据。

在受控取证目录保存实际安装包、来源文件、T09 manifest 引用的原文件、签名验证输出、完整预期/实际结果和报告；清单仅含相对路径与 SHA256。大文件/录屏放受控 CI artifact 或负责人证据目录，入库仅留摘要与哈希。不得纳入私钥、密码、token、未经授权的个人或业务数据。普通用户不需要 Node/Python，核验器运行在独立工程审查机。

```text
node scripts/release/verify-release.mjs MANIFEST.json EVIDENCE_ROOT TRUSTED_FREEZE.json
```

TRUSTED_FREEZE.json 必须从总控冻结候选独立取得，不能从待检清单复制作为信任依据。字段为 candidateSha、prdSha256、baselineSha256、candidateFrozenAt、modelMode、evaluationSha256、returnedModel、serviceVersion、recoverySnapshotSha256、migrationSnapshotSha256、previousAssets、expectedResults；不填 now，CLI使用当前时间。冻结时刻、模型/评估版本、恢复/双向迁移源快照、上一版双平台版本/源码/资产哈希和每项预期结果哈希都由外部pin约束，不能自填两边相同假数据绕过重验。所有 source/candidate/reviewed/build/report SHA 必须与该候选一致，报告时间在冻结之后且不在未来；任何实现、配置、依赖、验收、基线或模型变化都按原规则重验。测试模式 `synthetic` 的 CLI 总是退出 1；`evidence` 一致时退出 0，也不授予发布权限；不一致退出 1，无法读取或格式错退出 2。工具不调用网络、不启动产品、不签名或触碰凭据。

expectedResults 键为报告 label 加冒号加 check id（如 `PRODUCT:FR-001`），值为该完整预期文件SHA256。各验收owner冻结预期后交总控，不能从待验manifest生成真实freeze；测试自动生成只供合成fixture。迁移label为 `MIGRATION_<from>_<to>`，回退label为 `ROLLBACK_<target>`；其余label见核验器中evidence调用。migrationSnapshotSha256按源target索引；previousAssets每条包含target/version/sourceSha/sha256，必须覆盖双平台。

清单强制同时具备 Win11 x64 NSIS 与 macOS15 arm64 DMG：版本、NSIS PE/DMG koly文件头、app/engine 架构、构建来源与两份锁/唯一配置、完整组件 inventory/许可证文件、有效签名时间戳；Mac 另有 Hardened Runtime、公证和 ticket。设备记录必须有实际 OS 补丁/构建号、CPU/RAM、干净镜像、隔离会话和无开发环境声明。下载文件与候选包逐字节哈希一致，下载受众可访问且安装启动已验证。URL 不存临时鉴权参数。

每份报告绑定 candidate、T09 manifest、安装产物 SHA、操作者、设备/环境、实际时间、原始记录哈希以及具名 checks。每条 check 引用完整 expected/actual JSON，按对象字段与数组内容/顺序比较，不能只记录数量。数组应由领域唯一负责人按其规范稳定排序；不能通过排序掩盖行为轨迹顺序错误。原始失败结果保留，新结果另存。57 个 P0 从固定 PRD 提取；G 的 50 条 ID 与原条款从 T09 coverage 读取并与 PRD 校核；每个G预期须与T09 cases.json中的expected完全相同，E.5 exact/replay文件指针展开为exact/replayExact完整对象；T09 清单内每个文件都校验哈希。没有实际 T09 文件时直接失败，不生成第二份基线。

回退资产同时记录双平台上一版版本/来源SHA/签名报告，检查文件格式与独立上一版记录，不接受任意文本或当前资产冒充上一版。恢复/迁移比较使用 `t11-comparison-v1` 只读导出：projectId/sourceSnapshotId/revision、完整事实/定义/来源所有权/映射状态/查询结果/历史/轮次/撤销依据和执行版本。各集合项是唯一稳定id与完整payload，源快照哈希须与总控独立冻结记录一致。它不是项目格式、Store 或可变权威；由 T01/T10 从真实只读快照导出，T11 不补造数据。先后完整值须相同，缺字段、空层、无身份行、模板和数量摘要拒绝。字段布局见 `tests/fixtures/release/comparison.json`；该文件内容仅为小型合成反例输入。

## 核验的实际边界

哈希能证明提交给工具的字节一致，不能证明报告签发者、真人资格、真实操作或签名链可信。清单中的 valid/human 等声明必须由指定负责人对照原生命令原件、预约/观察证据独立核验。组件 inventory 应来自实际包和固定依赖图，不能由同一遗漏清单自证完整。工程 check 的 expected 文件应由原验收负责人冻结，actual 来自真实驱动；把两者都写成相同虚构值无法变成产品通过。此工具是必要的一致性检查，不能作为独立上线放行器。

## 官方协议依据与唯一配置交接

2026-10-21 核对：[Electron 签名说明](https://www.electronjs.org/docs/latest/tutorial/code-signing) 区分签名、公证，并说明代码身份对 Keychain 升级识别的影响；[Apple 公证说明](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution) 与 [Microsoft SignTool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool) 用于原生验证。electron.build 旧签名页此次返回 404，改以实际锁定 `electron-builder@26.15.3` 自带类型/实现核对可用配置字段；不根据失效链接猜配置。具体共享变更见 `docs/iterations/T11/shared-file-handoff.md`。
