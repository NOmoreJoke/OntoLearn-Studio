# 完整首版发布证据

T11 的版本化证据工具入口是 `scripts/release/verify-release.mjs`；它只做离线一致性核对，始终输出 `releaseAuthorized:false`。发布决定仍由原总控按完整 P0、指定双模型、实际 CI、真实双平台和渠道门执行。

**状态唯一账本入口是 `docs/iterations/W5/release-convergence-ledger.md`**，不再引用 `docs/reviews/T11/status.md`。该总账同时登记自动化可执行项 `A1..A8` 的结算、PRD 57 条 P0 `FR` 与附录 `G` 50 条用例的追踪矩阵，以及外部非代码人类发布 HOLD `H1..H10`（当前全部为 `PENDING_EXTERNAL_HOLD — NOT CLOSED`）。

> 归档说明：`docs/reviews/T11/**` 是 T11 本地会话的私有归档，本次移植**不引入该目录**（归档零新增）。下文凡指向 `../reviews/T11/...` 的链接均为指向未随本分支引入的历史归档指针，**不是本分支可访问的现行状态源**；现行状态一律以 W5 收敛总账为准。

## 证据清单 v1

唯一 schema 是 `scripts/release/verify.mts` 的 `manifestSchema`。不再维护另一份 JSON schema 或 builder 配置。`tests/unit/t11-release.test.ts` 的完整合成样例展示所有字段；样例身份、签名和参与者均为测试构造，不能转作实际证据。

在受控取证目录保存实际安装包、来源文件、T09 manifest 引用的原文件、签名验证输出、完整预期/实际结果和报告；清单仅含相对路径与 SHA256。大文件/录屏放受控 CI artifact 或负责人证据目录，入库仅留摘要与哈希。不得纳入私钥、密码、token、未经授权的个人或业务数据。普通用户不需要 Node/Python，核验器运行在独立工程审查机。

```text
node scripts/release/verify-release.mjs MANIFEST.json EVIDENCE_ROOT TRUSTED_FREEZE.json
```

TRUSTED_FREEZE.json 必须从总控冻结候选独立取得，不能从待检清单复制作为信任依据。字段为 candidateSha、prdSha256、baselineSha256、candidateFrozenAt、modelEndpoint、requestedModel、modelDecisionSha256、modelMode、evaluationSha256、returnedModel、serviceVersion、recoverySnapshotSha256、recoveryComparisonCase、migrationSnapshotSha256、migrationComparisonCases、previousAssets、expectedResults；不填 now，CLI使用当前时间。冻结时刻、模型/评估版本、恢复/双向迁移源快照、上一版双平台版本/源码/资产哈希和每项预期结果哈希都由外部pin约束，不能自填两边相同假数据绕过重验。所有 source/candidate/reviewed/build/report SHA 必须与该候选一致，报告时间在冻结之后且不在未来；任何实现、配置、依赖、验收、基线或模型变化都按原规则重验。测试模式 `synthetic` 的 CLI 总是退出 1；`evidence` 一致时退出 0，也不授予发布权限；不一致退出 1，无法读取或格式错退出 2。工具不调用网络、不启动产品、不签名或触碰凭据。

CLI要求Node 24.3及以上的24.x；实际验证版本随候选记录。入口先用纯JavaScript核参数和运行时，再在错误边界内加载唯一 `verify.mts`，不依赖根package的模块类型探测。参数数量错误只输出固定usage并退出2；不支持的运行时只输出 `UNSUPPORTED_NODE_RUNTIME` 并退出2；模块加载、清单/freeze无法读取、JSON解析/freeze schema错误或超限只输出 `MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID` 并退出2，stdout为空。无注入的正常CLI调用对以上错误严格核对整段stderr（固定一行及LF），正常synthetic或一致性结果的stderr为空。可解析JSON但manifest schema不合法仍按原合同输出 `MANIFEST_SCHEMA` 的一致性结果并退出1，不改成exit2。这里不屏蔽Node诊断：操作者额外注入的preload/运行时警告仍可见，不把全局关闭warning当错误面修复。

expectedResults 键为报告 label 加冒号加 check id（如 `PRODUCT:FR-001`），值为该完整预期文件SHA256。各验收owner冻结预期后交总控，不能从待验manifest生成真实freeze；测试自动生成只供合成fixture。迁移label为 `MIGRATION_<from>_<to>`，回退label为 `ROLLBACK_<target>`；其余label见核验器中evidence调用。migrationSnapshotSha256按源target索引；previousAssets每条包含target/version/sourceSha/sha256，必须覆盖双平台。

清单强制同时具备 Win11 x64 NSIS 与 macOS15 arm64 DMG：版本、NSIS PE/DMG koly文件头、app/engine 架构、构建来源与两份锁/唯一配置、完整组件 inventory/许可证文件、有效签名时间戳；Mac 另有 Hardened Runtime、公证和 ticket。设备记录必须有实际 OS 补丁/构建号、CPU/RAM、干净镜像、隔离会话和无开发环境声明。下载文件与候选包逐字节哈希一致，下载受众可访问且安装启动已验证。URL 不存临时鉴权参数。

每份报告绑定 candidate、T09 manifest、安装产物 SHA、操作者、设备/环境、实际时间、原始记录哈希以及具名 checks。每条 check 引用完整 expected/actual JSON，不能只记录数量。PRODUCT的facts/assertedFacts/inferred/addedTriples/inputs仅在内容确为完整subject/predicate/object三元组时按集合排序比较，保留重复数；事件、动作、轮次及其他数组严格保序，其余报告比较不变。领域owner仍需按其规范稳定输出，不能通过排序掩盖错误。原始失败另存。57个P0由固定PRD提取，G的50条ID/原文由T09 coverage对照PRD；每个G预期须与cases.json的完整expected一致，E.5 exact/replay指针展开成实际完整对象后比较。manifest内每个文件均校验哈希；缺文件直接失败，不生成第二份产品基线。

总控已允许固定基线输入只读引用，独立工具联验通过显式 `T11_FIXED_BASELINE_PROBE=1` 启用。Wave 5 Stage 1-A 已把该联验改为**全时运行（0 skipped）**、**离线无 `.git` 可跑**：基线不再是历史提交 `873c8c0` 的运行时对象，而是仓内**已提交的 18 文件基线** `tests/fixtures/product-baselines/manifest.json`（SHA-256 `0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad`，`version: prd-v0.6-learning-1`，含 `content/learning/extensions.json`），核验器 `scripts/release/verify.mts` 已在 `APPROVED_BASELINE` 中直接硬钉该 manifest SHA 与 PRD SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`。具体固定 SHA、18 文件核验与 0 skipped 边界见 `docs/iterations/T11/acceptance.md`。它仅证明本核验器能读取批准输入和拒绝错误，不消费T09未批准服务，不证明领域实际输出或50项产品通过。

回退资产同时记录双平台上一版版本/来源SHA/签名报告，检查文件格式与独立上一版记录，不接受任意文本或当前资产冒充上一版。恢复和每个回退资产报告都必须有 `rollback-retain-new-version-copy`、`rollback-refuse-incompatible-format`，保留其余原check。恢复/迁移使用新的 `t11-comparison-v3`；旧v2不静默转换，历史规范/报告原样保留。通用恢复允许合法空定义/映射/查询层，事实及来源所有权仍须齐全；正式双向迁移固定 `g6-conflict`，六必需层非空，全部22项迁移check保留。独立freeze同时pin源字节和case，不能用通用场景替代G.6。完整规范见 [v3](../iterations/T11/selection-comparison-v3.md) 与 [迁移流程](migration-recovery.md)。不修改T01/T10权威格式或决定F01。

Q9批准元组来自2026-10-21总控决定，原件SHA与采用段落见 [来源记录](../reviews/T11/q9-decision-source-20261023.json)。`model.endpoint` 和freeze的 `modelEndpoint` 均指具体Chat Completions请求路由 `https://api.deepseek.com/chat/completions`，其Base URL是 `https://api.deepseek.com`；requestedModel固定 `deepseek-v4-pro`，两边decisionSha256固定同份批准来源。任意URL/模型即使与freeze相同仍拒绝。返回标识、服务版本、模式、评估哈希继续独立冻结。这里只固化已有选型，不接API或推断服务可用。

生产 `mode=evidence` 另强制批准**已提交的 18 文件基线**：`tests/fixtures/product-baselines/manifest.json`（SHA-256 `0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad`）、`version: prd-v0.6-learning-1`、PRD SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` 及该 manifest 内 18 个精确路径；每文件内容 hash 仍来自唯一 manifest，不复制第二产品基线。`synthetic` 允许工具用自标合成 baseline；它永远不授发布权限。改变 freeze 不能扩大生产批准 profile。

每设备需 `collectorStatus` 文件引用，其JSON严格为 `{schemaVersion:1,status:"complete",step:"complete",exitCode:0}`，并与 `collector-complete` 实际check绑定；缺失、pending、failed或异常结构均拒绝。collector新目录内先写pending/步骤，失败保留failed/步骤/有限退出码及首次raw/半成品，成功最后才complete；重跑用新目录。marker只表示采集流程结束。`installed-components-match-package` 的完整JSON为 `{packageSha256,inventory,app,engine,method,provenance}`，inventory/app/engine/provenance文件引用均为path/sha256，method为installed或extracted。它绑定候选包、声明的唯一包内清单、组件字节和安装/解包原件；全部预期hash独立冻结。真实同包成员关系及安装/解包来源仍须T03唯一清单与独立审者对照原件，本工具只核引用字节及声明的一致性，不能因同目录或marker通过关闭该门。

## 核验的实际边界

哈希能证明提交给工具的字节一致，不能证明报告签发者、真人资格、真实操作或签名链可信。清单中的 valid/human 等声明必须由指定负责人对照原生命令原件、预约/观察证据独立核验。组件 inventory 应来自实际包和固定依赖图，不能由同一遗漏清单自证完整。工程 check 的 expected 文件应由原验收负责人冻结，actual 来自真实驱动；把两者都写成相同虚构值无法变成产品通过。此工具是必要的一致性检查，不能作为独立上线放行器。

## 官方协议依据与唯一配置交接

2026-10-21 核对：[Electron 签名说明](https://www.electronjs.org/docs/latest/tutorial/code-signing) 区分签名、公证，并说明代码身份对 Keychain 升级识别的影响；[Apple 公证说明](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution) 与 [Microsoft SignTool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool) 用于原生验证。electron.build 旧签名页此次返回 404，改以实际锁定 `electron-builder@26.15.3` 自带类型/实现核对可用配置字段；不根据失效链接猜配置。具体共享变更见 `docs/iterations/T11/shared-file-handoff.md`。

## Wave 5 Stage 0 / Stage 1-A 已落地的发布面事实

以下均为 Wave 5 在 `feature/w5-release` 上**已提交**的实现事实，不是计划。Stage 1-A 两个提交：`b84c244a`（Stage 0 发布面与忽略规则）与 `37ac2174`（Stage 1-A T11 核验器 / T10 投影 / 包内卫生门禁）。

### `release/` 三重忽略盲区已修复并内建于标准门禁

修复前 `.gitignore` 的 `release/`、`.prettierignore` 的 `release`、`eslint.config.mjs` 的 `'**/release/**'` 均为**非根锚定**规则，会把 `scripts/release/**` 与 `docs/release/**` 一并排除，造成「核验器与发布文档既不入 Git、也不被 Lint/Prettier 覆盖」的盲区。Stage 0 已改为根锚定：

| 文件                | 修复前            | 修复后         | 效果                     |
| :------------------ | :---------------- | :------------- | :----------------------- |
| `.gitignore`        | `release/`        | `/release/`    | 仅忽略仓库根构建输出目录 |
| `.prettierignore`   | `release`         | `/release`     | 同上                     |
| `eslint.config.mjs` | `'**/release/**'` | `'release/**'` | 仅忽略根级 `release/`    |

因此 `scripts/release/**` 新文件**已受正常 Git 追踪**并被标准 `npm run lint` / `npm run format:check` 覆盖，**不再需要** `--ignore-path /dev/null`、`--no-ignore` 或 `--ignore-pattern '!scripts/release/**'` 之类旁路参数（历史文档中的该写法已失效，保留仅为历史记录）。

### 正式安装包目标与无签名目录预验严格分离

`apps/desktop/electron-builder.yml` 现声明**正式目标**：`mac` 为 `dmg` / `arm64` + `hardenedRuntime: true` + `notarize: true`；`win` 为 `nsis` / `x64` + `signAndEditExecutable: true` + `signExecutable: true`；全局 `forceCodeSigning: true`。**零硬编码证书、秘钥或签名身份**——实际身份由负责人在已授权签名环境注入。`extraResources` 固定 6 项（引擎、contracts v2、FR003 设备运维示例、`licenses/` 目录、Electron `LICENSE`、Electron `LICENSES.chromium.html`）。

`apps/desktop/package.json` 的 `package:dir` 是**无签名目录预验**通道，显式覆写 `-c.forceCodeSigning=false -c.mac.identity=null -c.mac.hardenedRuntime=false -c.mac.notarize=false -c.win.signExecutable=false`，因此目录包**绝不冒充**已签名安装器，也**绝不触发本地 Keychain 弹窗**。

正式命令与预验/核验命令严格分离：

| 命令                          | 用途                                                 | 是否授予发布权限 |
| :---------------------------- | :--------------------------------------------------- | :--------------- |
| `npm run package:dir`         | 无签名目录预验                                       | 否               |
| `npm run package:release:mac` | 正式 macOS DMG/arm64（需授权签名身份）               | 否               |
| `npm run package:release:win` | 正式 Windows NSIS/x64（需授权签名证书）              | 否               |
| `npm run release:verify`      | 运行 `scripts/release/verify-release.mjs` 一致性核验 | 否               |
| `npm run release:hygiene`     | 运行包内卫生门禁                                     | 否               |

### 只读投影脚本与包内卫生门禁

- `scripts/release/project-t10-comparison.py`：把真实 `ontolearn-project-package-v1` ZIP **只读**投影为 `t11-comparison-v3`；不修改 `storage.py` 或 `transfer/service.py`。v1 格式本就不携带的层（`queries`/`results`/`rounds`/`rawSources`/`undo`/`derivedResults`）投影为**严格空数组**，绝不伪造；`rerunOriginalMapping`/`replaySandbox` 保持 `false`。
- `scripts/run-w5-packaged-release-hygiene.py`：对**已打包**产品树做 fail-closed 卫生检查——恰好一个产品、6 项 `extraResources` 均**非空**、文件名级零密钥/SQLite 残留、复检 Stage 0 打包不变量（强制签名/公证、零硬编码身份、`package:dir` 与正式签名构建隔离）。**从不签名、启动、安装或公证任何东西**，只读字节并写出两份 JSON 制品。

两者输出**恒定声明** `releaseAuthorized: false` 与 `installerAcceptanceClaimed: false`：目录预验包永远不能替代已签名安装器的验收证据。

## 取证目录与时钟

普通文件和CLI manifest/freeze限16MiB，安装/下载/回退包及组件流式hash限8GiB；这是工具工程边界，不是Q5业务容量或性能指标。读取先打开受控fd并fstat核普通非空文件及限额，再分配/解析；同fd做完整读取、hash和PE/koly结构检查，结束检查增长、短读及文件元数据漂移，异常关闭自有fd。叶节点无跟随/非阻塞打开依赖平台提供的flag；证据根及祖先目录须可信且在读取期间不受不可信并发修改，此实现未消除全部TOCTOU。

CLI用审查机当前墙钟覆盖freeze.now，没有生产任意时间开关。操作者须核对该机日期/时区/同步来源和可知偏差，并将无法核实的偏差作为未验证限制；本工具既不认证时钟，也不伪称发生过网络校时。签名valid等声明与时间戳链仍依赖原生原件审查。PE仅检查DOS/PE标记、偏移界限及允许机器字段，DMG仅检查尾部koly；这些均不能证明NSIS/DMG实质有效或签名可信。
