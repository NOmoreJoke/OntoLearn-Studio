# Wave 5 发布收敛总账（`B5/T11`）

> **唯一状态账本。** 本文件取代 `docs/reviews/T11/status.md` 作为 Wave 5 发布收敛的**唯一**状态入口；`docs/reviews/T11/**` 是 T11 本地会话的私有归档，**未随本分支引入**（归档零新增），其中任何指针都不是现行状态源。
>
> 基线工作树：`.worktrees/W5-release`，分支 `feature/w5-release`（已按 `origin/develop@a02cdac8` / `M_W4` 对齐，PR `#36` R3 闭环收口中）。
> 本总账只登记**已实测**的自动化结论与**明确未闭合**的外部 HOLD，不做发布放行判断。

---

## 0. 显著声明（先读这一节）

| 声明项                           | 值                                                      | 依据                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| :------------------------------- | :------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`newFRPasses`**                | **`0`**                                                 | 仓库转为 public 后，`B1a`（PR `#27`）→ `B1b`（PR `#29`）→ `L1`（PR `#30`，其合入后 `develop` CI 由后继 PR `#31` / `f6600d2c` Run `45127532064` 前向修复全绿）→ `CI Hardening`（PR `#31`）→ `Lq`（PR `#32`）→ `W3a`（PR `#33`）→ `W3b`（PR `#34`）→ `W4`（PR `#35`, `M_W4 = a02cdac8`）已全部通过三平台 PR CI + 合入后 `develop` CI + 0% 自审 L2 复核并合入 `origin/develop`（上游代码队列仅余本分支 Wave 5 / PR `#36`；注：`#2..#35` 为历史 PR 区间简写，含 squash 合入的 `#6` 等共 18 个正式合并点/基线节点）。**但正式发布可放行的 P0 新增通过数仍恒为 `0`**：外部非代码人类/真机/凭据 HOLD `H1..H10` 全部未闭合，`FR-803` 正式写工具仍为空，`FR-806`/`FR-900`/`FR-902`/`A-10`/`§11.3` 依赖 `H6`，`FR-901`/`FR-1000` 真机边界依赖 `H2`/`H3`。 |
| **`releaseAuthorized`**          | **`false`**                                             | `scripts/release/verify.mts` 在所有返回路径上硬编码 `releaseAuthorized: false`（`:217`/`:602`/`:610`/`:1078`）。工具是**必要的一致性检查**，不是独立上线放行器。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **`installerAcceptanceClaimed`** | **`false`**                                             | `scripts/run-w5-packaged-release-hygiene.py` 的 `summary.json` 恒定写入该字段（`:228`/`:229`）。无签名目录预验包（`package:dir`）**绝不冒充**已签名安装器，也**绝不冒充**真机验收证据。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 外部人类发布 HOLD                | **`H1..H10` 全部 `PENDING_EXTERNAL_HOLD — NOT CLOSED`** | 见 §4。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 正式发布放行                     | **未发生**                                              | `verify.mts` 恒锁死 `releaseAuthorized: false`；放行属总控 `H10` 决策。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

**一句话结论**：Wave 5 已把「发布所需的**工具与门禁**」建好并随上游合入队列（`origin/develop@a02cdac8` 及 PR `#36` 三平台自动化验证）推进闭环；**没有任何一项外部人类/真机/凭据类发布条件被闭合**。本总账**不构成**任何形式的发布许可。

---

## 1. 自动化可执行项 `A1..A8` 逐条结算

判定口径：**绿 = 真实命令 exit 0 且制品绑定精确 `base/head/tree`**，不是「看起来过了」。凡标 ✅ 者均在 `.worktrees/W5-release`（历史基准含 `37ac2174`/`9030957a`，及与 `origin/develop@a02cdac8` 对齐后的候选提交）上**实测**；凡标 ⛔ 者如实说明为何不能在本机闭合。

### A1 安装包正式目标与无签名目录预验**分离**

| 项       | 内容                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态     | ✅ 已落地并静态核对                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 实现     | `apps/desktop/electron-builder.yml`：mac `dmg`/`arm64` + `hardenedRuntime: true` + `notarize: true`；win `nsis`/`x64` + `signAndEditExecutable: true` + `signExecutable: true`；全局 `forceCodeSigning: true`；**零硬编码身份/证书/秘钥**。`apps/desktop/package.json` 的 `package:dir` 显式覆写 `-c.forceCodeSigning=false -c.mac.identity=null -c.mac.hardenedRuntime=false -c.mac.notarize=false -c.win.signExecutable=false`，即目录预验通道**永不触发 Keychain 弹窗、永不产出可验收安装器**。 |
| 范围决策 | **macOS 首发正式目标明确限定 `arm64`（`macOS 15 arm64` DMG）**：首版桌面发布目标矩阵为 `Windows 11 x64` NSIS 与 `macOS 15 Apple Silicon arm64` DMG（与 `docs/release/q5-decision-proposal-20261022.md:20`、`scripts/release/collect-macos.sh:8` 一致），暂不包含 Intel `macOS x64` / `universal` 正式安装包；后续若扩展至 `macOS x64` 或 `universal`，须经总控与设备负责人显式审批、更新 `electron-builder.yml` 与 `collect-macos.sh` 并补全对应干净真机验收。                                     |
| 命令     | `npm run package:dir`（无签名目录预验）/ `npm run package:release:mac` / `npm run package:release:win`（正式签名构建，需授权身份）；根 `package.json` 另提供 `release:verify` 与 `release:hygiene`。                                                                                                                                                                                                                                                                                               |
| 证据     | Stage 0 提交 `b84c244a`（`electron-builder.yml` +16/-3、`apps/desktop/package.json` +6/-1、根 `package.json` +4）。                                                                                                                                                                                                                                                                                                                                                                                |
| 未闭合   | 正式签名构建与安装器验收 → `H4`/`H5`（需 Apple Developer ID 与 Windows 代码签名证书）；真机安装 → `H2`/`H3`。                                                                                                                                                                                                                                                                                                                                                                                      |

### A2 零残留签名 / 6 项 `extraResources` / 零密钥扫描

| 项      | 内容                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态    | ✅ 门禁已实现并接入 `desktop` CI 打包腿；⛔ **未产出已签名正式安装包**                                                                                                                                                                                                                                                                                                                                                                                                     |
| 实现    | `scripts/run-w5-packaged-release-hygiene.py` 对已打包产品树做 fail-closed 检查：① 恰好一个产品（`*.app/Contents/Resources` / `*unpacked/resources` / `@ontolearndesktop/resources`）；② 6 项 `extraResources` 存在且**字节非空**（引擎可执行文件、contracts v2 registry/schema、FR003 设备运维示例、`licenses/` 目录、Electron `LICENSE`、Electron `LICENSES.chromium.html`）；③ 文件名级敏感残留扫描（`.pem`/`.key`/`.p12`/`.pfx`/`.sqlite`/`.sqlite3`/`.db` 及 `password | secret | certificate | api[-_]?key | identity | csc` 键名），普通运行时库（`.dat`/`.pak`/`.so`/`.dylib`）不误伤；④ 复检 Stage 0 打包不变量。 |
| 命令    | `npm run release:hygiene` → `uv run --frozen python scripts/run-w5-packaged-release-hygiene.py release build/w5-release-hygiene`                                                                                                                                                                                                                                                                                                                                           |
| CI 接线 | Stage 0 已把该脚本加入 `.github/workflows/ci.yml` 的 `macos-latest` 与 `windows-latest` 打包腿，在无签名 `package:dir` 目录包上执行并上传 `build/w5-release-hygiene-ci/` 制品。                                                                                                                                                                                                                                                                                            |
| 未闭合  | **未**在本地或 CI 产出正式签名包（受 `H4`/`H5` 外部证书与公证凭据阻塞，非 GitHub Actions 计费阻塞）；本项当前证明的是**门禁逻辑与无签名目录预验包的卫生不变量通过**，绝不冒充「已签名安装器验收通过」。                                                                                                                                                                                                                                                                    |

### A3 `verify.mts` + `verify-release.mjs` 版本化核验器

| 项         | 内容                                                                                                                                                                                                                                                                                                                                           |
| :--------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态       | ✅ 已落地，本轮单测全绿（`2 test files / 136 passed`，**0 skipped**）                                                                                                                                                                                                                                                                          |
| 实现       | `scripts/release/verify.mts` 是**唯一** schema（`manifestSchema` / `comparisonSchema`）；`scripts/release/verify-release.mjs` 是纯 JS 入口，先核参数与运行时再在错误边界内加载 `.mts`，**不依赖**根 package 的模块类型探测。工具**不调用网络、不启动产品、不签名、不触碰凭据**。                                                               |
| 关键不变量 | `APPROVED_BASELINE` 直接硬钉已提交基线 manifest SHA `0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad`、`version: prd-v0.6-learning-1`、PRD SHA `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`；根 `package.json` 已显式声明同版本 `"zod": "4.6.7"`（消除 workspace 提升幽灵依赖，零新增包）。             |
| 信任边界   | **`TRUSTED_FREEZE.json` 程序性信任边界**：`APPROVED_BASELINE` 与 `APPROVED_MODEL` 由 `verify.mts` 常量强制锁定且不可被外部覆盖；其余内容类 pin（预期哈希、恢复/迁移快照与上一版资产哈希）以独立 `TRUSTED_FREEZE.json` 为唯一输入，其来源完整性属程序性信任边界——须由总控带外冻结保管，并在每次执行 `release:verify` 前独立核对其文件 SHA-256。 |
| 诚实边界   | 哈希能证明**提交给工具的字节一致**，不能证明报告签发者、真人资格、真实操作或签名链可信。`releaseAuthorized` 恒 `false`。                                                                                                                                                                                                                       |

### A4 PRD 57 条 P0 与附录 `G` 50 条用例**对账**

| 项           | 内容                                                                                                                                                                                                                                                                                                                                                               |
| :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态         | ✅ 机械化对账已内建于核验器并被单测覆盖                                                                                                                                                                                                                                                                                                                            |
| 实现         | `scripts/release/verify.mts:653-654` 从固定 PRD 文本正则抽取 `### FR-xxx ...【P0...】`，若 `p0.length !== 57` 或存在重复即 `fail('PRD_SCOPE')`；`:684` 要求 `coverage.json` 的 `entries` 长度恰为 `50`；`:727` 要求 `cases.json` 的 `cases` 长度恰为 `50`。                                                                                                        |
| 本轮独立复核 | PRD 全文抽取 `### FR-` 标题共 **59** 条，其中 `FR-506`（高级设置）与 `FR-903`（用量与状态）标注为 **P1**，故 **P0 恰为 57 条**。`tests/fixtures/product-baselines/coverage.json` 的 `entries` 实测 **50** 条（`M` 6 + `Q` 2 + `V` 1 + `R` 6 + `O` 1 + `B` 11 + `A` 10 + `G-list` 13）。`manifest.json` 实测 **18** 个文件并含 `content/learning/extensions.json`。 |
| 未闭合       | 对账只证明**数量与来源一致**，不证明 57 条 P0 或 50 条 G 用例在产品中**实际通过**（那需要真机与真人，见 §3、§4）。                                                                                                                                                                                                                                                 |

### A5 只读双平台 collector

| 项       | 内容                                                                                                                                                                                                                    |
| :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态     | ✅ 工具已落地；⛔ **未在批准设备上实跑**（无 Windows 批准执行环境、无 macOS 15 arm64 干净真机）                                                                                                                         |
| 实现     | `scripts/release/collect-macos.sh`（`bash -n` 通过）、`scripts/release/collect-windows.ps1`、`scripts/release/pe-machine.ps1`。collector **只收只读元数据**：不启动产品、不安装、不签名、不解锁、不调用模型、不发消息。 |
| 协议     | mac：`bash scripts/release/collect-macos.sh --approved-isolated-session APP DMG NEW_DIR`；Windows：`collect-windows.ps1` 传入安装包、应用/引擎 exe 与新输出目录。开关**只防误运行，不构成授权**。                       |
| 完成标记 | `collectorStatus` 严格为 `{schemaVersion:1,status:"complete",step:"complete",exitCode:0}`，与 `collector-complete` 实际 check 绑定；缺失/pending/failed/异常结构一律拒绝。                                              |
| 未闭合   | 真实采集 → `H2`（Win11 x64 干净真机）/ `H3`（macOS 15 arm64 干净真机）。                                                                                                                                                |

### A6 T10 → `t11-comparison-v3` **只读**投影

| 项       | 内容                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态     | ✅ 已落地，本轮 `packages/engine/tests/test_w5_release_projection.py` 实测 **10 passed**                                                                                                                                                                                                                                                                                                                                |
| 实现     | `scripts/release/project-t10-comparison.py`：读取真实 `ontolearn-project-package-v1` ZIP（`manifest.json` + `data/*.json`），经 fd pre-stat 预检与流式解压上限读入并校验成员路径/大小/SHA-256/选项隔离/核心角色完整性，使用 `layer:id` 复合定义主键（对齐 `storage.py` `(project,layer,id)` 主键），输出对齐 `comparisonSchema` 的 `t11-comparison-v3` 文档。                                                           |
| 诚实约束 | **不修改** `packages/engine/src/ontolearn_engine/storage.py`，**不修改** `transfer/service.py`。v1 格式本就不携带的层（`queries`/`results`/`rounds`/`rawSources`/`undo`/`derivedResults`）投影为**严格空数组**，**绝不伪造**；`rerunOriginalMapping`/`replaySandbox` 恒 `false`（`mappingSources: missing` / `replaySemantics: missing`）。模板包或缺当前事实/所有权的包按 `restoreCurrent: false` 诚实拒绝并退出非零。 |
| 退出码   | `0` 可恢复完整投影 / `1` 诚实拒绝（投影仍写出）/ `2` 用法或非法包失败（stderr 固定单行，**不回显包字节**）。                                                                                                                                                                                                                                                                                                            |

### A7 CLI **三态退出码**

| 项       | 内容                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态     | ✅ 已落地并被单测覆盖                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 实现     | `scripts/release/verify-release.mjs`：参数数量错误 → 固定 usage + **exit 2**；非 24.3+ 的 24.x → `UNSUPPORTED_NODE_RUNTIME` + **exit 2**；模块加载/清单或 freeze 不可读/JSON 解析或 schema 错/超限 → `MANIFEST_OR_FREEZE_UNREADABLE_OR_INVALID` + **exit 2**（stdout 为空）；`synthetic` 模式**恒 exit 1**；`evidence` 一致 → **exit 0**（仍不授予发布权限）；不一致 → **exit 1**；可解析 JSON 但 manifest schema 不合法 → 按合同输出 `MANIFEST_SCHEMA` 一致性结果并 **exit 1**（不改 exit 2）。 |
| 运行环境 | 要求 Node **24.3 及以上**的 24.x；本轮实测 Node `v24.15.0`。不屏蔽 Node 诊断：操作者注入的 preload/运行时警告仍可见。                                                                                                                                                                                                                                                                                                                                                                            |

### A8 `release/` **三重忽略盲区**修复

| 项       | 内容                                                                                                                                                                                                                                                                                                                                                   |
| :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 状态     | ✅ 已修复并内建于标准门禁                                                                                                                                                                                                                                                                                                                              |
| 缺陷     | `.gitignore` 的 `release/`、`.prettierignore` 的 `release`、`eslint.config.mjs` 的 `'**/release/**'` 均为**非根锚定**规则，会把 `scripts/release/**` 与 `docs/release/**` 一并排除 → 「核验器与发布文档既不入 Git、也不被 Lint/Prettier 覆盖」。                                                                                                       |
| 修复     | Stage 0（`b84c244a`）：`.gitignore` → `/release/`；`.prettierignore` → `/release`；`eslint.config.mjs` → `'release/**'`。                                                                                                                                                                                                                              |
| 本轮实测 | `git check-ignore -v scripts/release/verify.mts` / `docs/release/README.md` / `scripts/release` → **均 exit 1（未被忽略）**；`npx eslint --print-config scripts/release/verify.mts` → 返回配置（未被忽略）；`npx eslint scripts/release --max-warnings 0` → exit 0；`npx prettier --check scripts/release docs/release docs/iterations/T11` → exit 0。 |
| 结论     | `scripts/release/**` 新文件**已受正常 Git 追踪与 Lint 覆盖**；T11 历史文档中的 `--ignore-path /dev/null` / `--no-ignore` 旁路写法**已失效**（保留仅为历史可追溯）。                                                                                                                                                                                    |

---

## 2. PRD 57 条 P0 `FR` 追踪矩阵

上游状态口径统一为：

- **`MERGED-UPSTREAM（已合入 origin/develop@a02cdac8；正式发布验收仍待 H1..H10）`** = 该 FR 所属 Wave 的代码与自动化测试已通过三平台 PR CI + 合入后 `develop` CI + 0% 自审 L2 复核并合入 `origin/develop@a02cdac8`（`M_W4`）；**但不构成正式发布 `newFRPasses`**（正式发布仍受 `H1..H10` 与下列结构性/外部依赖约束）。
- **`DEP-H6`** = 依赖真实 DeepSeek API 权限/余额（`H6`）。
- **`UNVERIFIABLE-Hn`** = 在本机/本仓**不可能**闭合，必须由外部人类或真机闭合。
- **`FR-803 正式写工具仍为空`** = 结构性缺口已在账本显式披露。

> `origin/develop` 已从 `cb5d9631`（G0）串行推进并合入至 **`a02cdac8`（`M_W4`，PR `#27..#35`）**；上游代码收口队列仅余本分支 **Wave 5（`feature/w5-release`，PR `#36` 候选）**。但全部 10 项外部发布 HOLD（`H1..H10`）均未闭合，故 `newFRPasses` 仍恒为 **`0`**。

### 2.1 基础生命周期 / 快照（Q3 / G0 / B1a / B1b）

| FR     | 名称                          | Wave           | 本地验证证明单元                                                                                                  | 上游状态                                                                             |
| :----- | :---------------------------- | :------------- | :---------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| FR-001 | 首次启动引导                  | B1a / L1       | `tests/e2e/b1a-project-lifecycle.spec.ts`、`tests/e2e/l1-learning-vertical.spec.ts`                               | `MERGED-UPSTREAM`（PR #27 / #30 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |
| FR-002 | 项目创建与打开                | B1a            | `tests/unit/b1a-project-management-runtime.test.ts`、`b1a-library-ipc.test.ts`、`b1a-lifecycle-admission.test.ts` | `MERGED-UPSTREAM`（PR #27 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-003 | 内置示例项目                  | T03 / W4       | `tests/unit/t01-example-host-runtime.test.ts`、`scripts/run-w4-packaged-workspaces.py`（FR003 bundle）            | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-004 | 自动保存与快照                | B1b / W3b / W4 | `tests/unit/b1b-project-restore.test.ts`、`w3b-cross-slice-before-commit-and-loopback.test.ts`                    | `MERGED-UPSTREAM`（PR #29 / #34 / #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-005 | 模式切换（完整专业模式为 P1） | W3b            | `w3b-cross-slice-before-commit-and-loopback.test.ts`（`FR-802_FR-005`）                                           | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-006 | 数据层次与结果失效            | B1b / W4       | `tests/unit/b1b-project-restore-runtime.test.ts`、`packages/engine/tests/test_w4_learning_checks.py`              | `MERGED-UPSTREAM`（PR #29 / #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |

### 2.2 学习与离线课程（L1 / Lq / W3a）

| FR     | 名称                   | Wave          | 本地验证证明单元                                                                                                                     | 上游状态                                                                             |
| :----- | :--------------------- | :------------ | :----------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| FR-100 | 学习路径               | L1            | `tests/unit/l1-learning-ledger.test.ts`、`scripts/run-l1-packaged-learning.py`                                                       | `MERGED-UPSTREAM`（PR #30 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-101 | 离线分级提示与模型增强 | L1 / W3b      | `tests/unit/l1-mentor-panel.test.ts`、`w3b-agent-and-b2.spec.ts`                                                                     | `MERGED-UPSTREAM`（PR #30 / #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |
| FR-102 | 学习检查与反馈         | L1 / Lq / W3a | `packages/engine/tests/test_w4_learning_checks.py`、`test_w3a_quality_b3.py`                                                         | `MERGED-UPSTREAM`（PR #30 / #32 / #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-103 | 术语帮助               | L1            | `tests/unit/l1-mentor-panel.test.ts`（内嵌术语别名搜索）                                                                             | `MERGED-UPSTREAM`（PR #30 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-104 | 学习成果               | L1 / W3a      | `tests/unit/l1-learning-ledger.test.ts`                                                                                              | `MERGED-UPSTREAM`（PR #30 / #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |
| FR-105 | 最小迁移学习验证       | W3a           | `packages/engine/tests/test_w3a_quality_b3.py`、`tests/e2e/w3a-quality-and-b3.spec.ts`（`transfer-repair`/`transfer-classify` 两关） | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |

### 2.3 本体建模（T02 / W3b）

| FR     | 名称                   | Wave | 本地验证证明单元                                                                                                        | 上游状态                                                                       |
| :----- | :--------------------- | :--- | :---------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| FR-200 | 业务概念管理           | T02  | `tests/unit/t02-mainline-metadata.test.ts`、`tests/e2e/t02-fr200-fr201.spec.ts`                                         | `MERGED-UPSTREAM`（PR #16 / #20 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-201 | 结构关系与实例事实创建 | T02  | `tests/unit/t02-mainline-consumer.test.ts`、`t02-ownership-detail.test.ts`                                              | `MERGED-UPSTREAM`（PR #16 / #20 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-202 | 多视图展示             | W3b  | `tests/e2e/w3b-agent-and-b2.spec.ts`（第一例）                                                                          | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |
| FR-203 | 本体导入导出           | W3b  | `w3b-cross-slice-before-commit-and-loopback.test.ts`（`FR-203-turtle-roundtrip` / `FR-203-import-full-diff-isolation`） | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |
| FR-204 | 建模草稿与修改预览     | W3b  | `tests/e2e/w3b-agent-and-b2.spec.ts`（整份 Diff 显式确认）                                                              | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）       |

### 2.4 数据源与映射（W4 / T03）

| FR     | 名称                         | Wave | 本地验证证明单元                                                                          | 上游状态                                                                 |
| :----- | :--------------------------- | :--- | :---------------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
| FR-300 | 数据源接入                   | W4   | `tests/unit/w4-cross-slice-real-runtime.test.ts`、`tests/e2e/q3-mapping-physical.spec.ts` | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-301 | 三步映射向导与实体身份       | W4   | `tests/unit/w4-cross-slice-real-runtime.test.ts`（`M-01`/`M-02` 稳定身份）                | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-302 | 映射建议                     | W4   | 同上（无模型时手动全 P0 映射路径）                                                        | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-303 | 值转换、预览与错误定位       | W4   | 同上（`M-05` 行级错误定位 + 整批原子提交）                                                | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-304 | 来源追踪、固定重跑与人工冲突 | W4   | 同上（`M-03`/`M-04`/`M-06` 撤回、冲突、旧预览拒绝）                                       | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |

### 2.5 查询（Q3 / Lq / W3b）

| FR     | 名称                 | Wave            | 本地验证证明单元                                                                                                     | 上游状态                                                                             |
| :----- | :------------------- | :-------------- | :------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------- |
| FR-400 | 多种查询入口         | W3b             | `tests/e2e/w3b-agent-and-b2.spec.ts`（模板词表 + 模型草稿投影）                                                      | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-401 | 查询透明性与数据范围 | T04(Q3) / Lq    | `tests/unit/lq-query-learning.test.ts`、`tests/e2e/lq-query-learning.spec.ts`、`tests/e2e/q3-packaged-graph.spec.ts` | 同快照图（PR #24）与学习课程（PR #32）均 `MERGED-UPSTREAM`；正式发布仍待 `H1..H10`   |
| FR-402 | 本地只读与网络限制   | Q3 / W3b        | `tests/unit/w3b-pre-encoded-body.test.ts`（loopback 与本地零外发）                                                   | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |
| FR-403 | 结果与空结果解释     | T04(Q1/Q2) / Lq | `tests/unit/t04-empty-results.test.ts`、`lq-query-learning.test.ts`                                                  | 空结果方向（PR #22）与学习课程（PR #32）均 `MERGED-UPSTREAM`；正式发布仍待 `H1..H10` |
| FR-404 | 查询保存与复用       | Lq              | `tests/unit/lq-query-learning.test.ts`                                                                               | `MERGED-UPSTREAM`（PR #32 已入 `origin/develop@a02cdac8`，待 `H1..H10`）             |

### 2.6 质量检查与推理（W3a / T05）

| FR     | 名称               | Wave | 本地验证证明单元                                                                 | 上游状态                                                                 |
| :----- | :----------------- | :--- | :------------------------------------------------------------------------------- | :----------------------------------------------------------------------- |
| FR-500 | 一键检查与验证范围 | W3a  | `tests/unit/t05-quality.test.ts`、`packages/engine/tests/test_w3a_quality_b3.py` | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-501 | 推理执行与组合语义 | W3a  | 同上（`reasoning.execute → validation.execute` 两阶段顺序）                      | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-502 | 推导依据与解释边界 | W3a  | 同上（`R-04` RDFS 依据链）                                                       | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-503 | 问题分级与定位     | W3a  | 同上（`V-01` 名称必填违规定位）                                                  | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-504 | 最小约束编辑与测试 | W3a  | 同上（5 类 SHACL 模板与受控合取规则）                                            | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-505 | 最小规则编辑与测试 | W3a  | 同上（`R-05` P0 不支持规则链提示）                                               | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |

### 2.7 行为模型（W4 / T06）

| FR     | 名称               | Wave | 本地验证证明单元                               | 上游状态                                                                 |
| :----- | :----------------- | :--- | :--------------------------------------------- | :----------------------------------------------------------------------- |
| FR-600 | 行为模型           | W4   | `packages/engine/tests/test_w4_a2_behavior.py` | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-601 | 内置安全动作       | W4   | 同上（`B-01`/`B-02`）                          | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-602 | 行为验证与冲突     | W4   | 同上（`B-04` 行为前快照、`B-05` 竞争写入）     | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-603 | 样本测试           | W4   | 同上（`B-08` 工具失败不得声称通过）            | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-604 | 行为与正式数据隔离 | W4   | 同上（沙盘/行为隔离边界）                      | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |

### 2.8 情景推演（W4 / T07）

| FR     | 名称                 | Wave | 本地验证证明单元                               | 上游状态                                                                 |
| :----- | :------------------- | :--- | :--------------------------------------------- | :----------------------------------------------------------------------- |
| FR-700 | 场景创建             | W4   | `packages/engine/tests/test_w4_a2_scenario.py` | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-701 | 固定轮次执行语义     | W4   | 同上（`G-list-01` 逐轮状态）                   | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-702 | 场景对比与指标       | W4   | 同上（`G-list-02`/`G-list-05`）                | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-703 | 运行依据与重放       | W4   | 同上（`G-list-06` 显式续跑零重放）             | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-704 | 假设提示             | W4   | 同上（假设提示与实际运行绑定）                 | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |
| FR-705 | 沙盘隔离、取消与恢复 | W4   | 同上（`G-list-07`/`G-list-08`）                | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`） |

### 2.9 Agent 侧栏与模型边界（W3b / I06 / T08）

| FR     | 名称                        | Wave      | 本地验证证明单元                                                                   | 上游状态                                                                                             |
| :----- | :-------------------------- | :-------- | :--------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| FR-800 | 上下文感知                  | W3b       | `tests/e2e/w3b-agent-and-b2.spec.ts`（第二例）                                     | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                             |
| FR-801 | 页面上下文动作              | W3b       | 同上（每页最多四个动作）                                                           | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                             |
| FR-802 | 导师与项目模式              | W3b       | `w3b-cross-slice-before-commit-and-loopback.test.ts`                               | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                             |
| FR-803 | 工具白名单                  | W3b       | 同上（Wave 4 禁用、**正式写工具仍为空**）                                          | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`）；**正式写工具仍为空（结构性缺口未闭环）** |
| FR-804 | 版本化 Diff、原子提交与撤销 | W3b / B1b | `packages/engine/tests/test_agent_before_commit.py`、`b1b-project-restore.test.ts` | `MERGED-UPSTREAM`（PR #29 / #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                       |
| FR-805 | 可信回答边界                | W3b       | `w3b-cross-slice-before-commit-and-loopback.test.ts`                               | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                             |
| FR-806 | 模型失败降级                | W3b       | 同上（本地等待/取消/重试路径）                                                     | 本地等待/取消/重试：`MERGED-UPSTREAM`（PR #34）；**真实在线延迟与真实 DeepSeek**：`DEP-H6`           |

### 2.10 模型服务、外发与密钥（W3b）

| FR     | 名称                       | Wave     | 本地验证证明单元                                                                               | 上游状态                                                                                                     |
| :----- | :------------------------- | :------- | :--------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| FR-900 | 模型服务配置与能力验证     | W3b      | `tests/unit/w3b-pre-encoded-body.test.ts`（`synthetic` 探测、启停、移除、审计）                | 本地与 `synthetic`：`MERGED-UPSTREAM`（PR #34）；**真实 DeepSeek**：`DEP-H6`                                 |
| FR-901 | 密钥保护                   | W3b / W4 | `w3b-cross-slice-before-commit-and-loopback.test.ts`（边界审计）、`test_w4_learning_checks.py` | 边界审计：`MERGED-UPSTREAM`（PR #34 / #35）；**三 OS 真实 safeStorage/DPAPI/Keychain**：`UNVERIFIABLE-H2/H3` |
| FR-902 | 最终外发内容检查与隐私级别 | W3b      | `tests/unit/w3b-pre-encoded-body.test.ts`（核准正文 == socket 实收字节；越界与完全本地零外发） | 本地与 loopback：`MERGED-UPSTREAM`（PR #34）；**真实外发最小 vs 项目差异**：`DEP-H6`                         |
| FR-904 | 最小外发调用记录           | W3b      | `w3b-cross-slice-before-commit-and-loopback.test.ts`（收据与审计无凭据）                       | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                                     |

### 2.11 迁移、报告与项目包（W4 / B4 / T10）

| FR      | 名称                         | Wave | 本地验证证明单元                                                                                                                                                                                      | 上游状态                                                                                                 |
| :------ | :--------------------------- | :--- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------- |
| FR-1000 | 项目包清单、版本、迁移与重放 | W4   | `tests/unit/w4-cross-slice-real-runtime.test.ts`、`tests/e2e/w4-workspaces-and-transfer.spec.ts`、`scripts/run-w4-packaged-workspaces.py`、`scripts/release/project-t10-comparison.py`（W5 只读投影） | 包引擎/构建：`MERGED-UPSTREAM`（PR #35）；W5 只读投影待 PR `#36`；**真机双向迁移**：`UNVERIFIABLE-H2/H3` |
| FR-1001 | HTML 报告导出与安全显示      | W4   | `tests/e2e/w4-workspaces-and-transfer.spec.ts`（HTML CSP、三种隔离 Agent 工具的有界收据）                                                                                                             | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`，待 `H1..H10`）                                 |

### 2.12 已合入 `origin/develop` 的 Wave 基线（代码已合入，正式发布仍恒守 `newFRPasses = 0`）

`origin/develop` 实测合并历史（`git log --oneline --merges origin/develop`；注：`#2..#35` 为历史 PR 区间简写，含 squash 合入的 `#6` 等共 18 个正式合并点/基线节点）：

| 合并点                  | PR        | Wave / 切片  | 覆盖的 P0 能力 / 收口说明                                                                                                           |
| :---------------------- | :-------- | :----------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `1b6df7a2`              | #2        | I01          | 存储 / 快照 / 结果失效基础（`FR-006`、`FR-804`、`FR-1000` 等基础层）                                                                |
| `c2f9b038`              | #3        | I02          | CSP / 窗口生命周期（启动与原生恢复基线）                                                                                            |
| `e45e6038`              | #4        | I03          | 协议 / 契约（公共格式与 registry）                                                                                                  |
| `5f910b52`              | #5        | I04          | 常驻协调器 / ExecutionJob（`FR-800` 侧基础）                                                                                        |
| `9235454a` / `fac1a2fb` | #16 / #20 | T02          | `FR-200`、`FR-201`                                                                                                                  |
| `02888871`              | #22       | T04 Q1/Q2    | 空结果五个方向（`FR-403`）                                                                                                          |
| `0e01b4d0`              | #24       | T04 Q3       | 同快照关系图（`FR-401`）                                                                                                            |
| `d5695332` / `cb5d9631` | #25 / #26 | G0           | 审查分级策略（不新增产品 FR）                                                                                                       |
| `73441130`              | #27       | B1a          | 项目生命周期 / 管理 / 首启与崩溃恢复（`FR-001`、`FR-002`）                                                                          |
| `587a931f`              | #29       | B1b          | 快照恢复与结果失效（`FR-004`、`FR-006`、`FR-804` 底层）                                                                             |
| `dd688719`              | #30       | L1           | 垂直学习底座与离线分级提示（`FR-001`、`FR-100`..`FR-104`）                                                                          |
| `f6600d2c`              | #31       | CI Hardening | macOS CI 30m/分片与 Windows CSP 恢复韧性（不新增产品 FR）                                                                           |
| `915979f2`              | #32       | Lq           | 查询学习课程与保存复用（`FR-401`、`FR-403`、`FR-404`）                                                                              |
| `bfd9926c`              | #33       | W3a          | 质量检查 / 推理 / 最小迁移（`FR-102`、`FR-104`、`FR-105`、`FR-500`..`FR-505`）                                                      |
| `aaabfc92`              | #34       | W3b          | 多视图 / Turtle / Agent 侧栏 / 模型网关与隐私（`FR-004`..`FR-904` 相关模块；`FR-803` 正式写工具仍为空）                             |
| `a02cdac8`              | #35       | W4           | 数据源映射 / 行为 / 情景推演 / 项目包与 HTML 报告（`FR-003`..`FR-1001` 相关模块；合入后 `develop` CI Run `45337490364` 三平台全绿） |

**当前仅余待合入的上游发布分支**：**Wave 5（`feature/w5-release`，PR `#36` 候选）**，即本分支所承载的 T11 发布核验器、T10 v3 只读投影、包内发布卫生门禁与收敛总账。

### 2.13 计数闭合

- P0 `FR` 总数：**57**（PRD `### FR-` 标题 59 条 − `FR-506` P1 − `FR-903` P1 = 57）。
- 本矩阵登记：**57** 条（6 + 6 + 5 + 5 + 5 + 6 + 5 + 6 + 7 + 4 + 2 = 57）。✅ 闭合。
- 代码与自动化上游状态分布：**57/57** 条 P0 `FR` 的核心产品代码与自动化测试均已跨 `#2..#35` 合入 `origin/develop@a02cdac8`（其中 W5 的 T10 v3 只读投影与发布核验收敛由 PR `#36` 补齐）；但按发布口径仍有：**3** 条额外依赖真实 DeepSeek `H6`（`FR-806`、`FR-900`、`FR-902`）、**2** 条依赖真机 OS 检查 `H2`/`H3`（`FR-901`、`FR-1000`），以及 **`FR-803` 正式写工具仍为空** 的已知结构性缺口。
- **`newFRPasses = 0`**：尽管上游代码与三平台 CI 已推进至 `a02cdac8`，但在 `H1..H10` 全部外部人类/真机/凭据条件闭合之前，正式发布放行计数恒为 `0`。

---

## 3. 附录 `G` 50 条用例追踪矩阵

`tests/fixtures/product-baselines/coverage.json` 的 50 条 `entries`（ID 与 PRD 原文一并被 `verify.mts` 校验）与 PRD §12.1 八步链路逐条对应：

| 用例组                                                | 条数 | Wave         | 关联 PRD §12.1 步骤              | 本地验证证明单元                                                                                                                                           | 上游状态                                                                                                                         |
| :---------------------------------------------------- | :--- | :----------- | :------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `M-01`..`M-06`（映射/身份/重跑/冲突）                 | 6    | W4 (T03)     | ③ CSV 映射                       | `tests/unit/w4-cross-slice-real-runtime.test.ts`、`packages/engine/tests/test_w4_learning_checks.py`                                                       | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`；真机/真人/正式发布验收仍待 `H1..H10`）                                 |
| `Q-01`/`Q-02`（高危告警 / 空结果）                    | 2    | Lq           | ④ 查询完整/空结果                | `tests/unit/lq-query-learning.test.ts`、`tests/e2e/lq-query-learning.spec.ts`                                                                              | `MERGED-UPSTREAM`（PR #32 已入 `origin/develop@a02cdac8`；真机/真人/正式发布验收仍待 `H1..H10`）                                 |
| `V-01`（名称必填约束）                                | 1    | W3a (T05)    | ⑤ 约束失败/修复/依据             | `tests/unit/t05-quality.test.ts`、`packages/engine/tests/test_w3a_quality_b3.py`                                                                           | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`；真机/真人/正式发布验收仍待 `H1..H10`）                                 |
| `R-01`..`R-06`（推理/依据/规则链不支持）              | 6    | W3a (T05)    | ⑤ 真实推导依据                   | 同上                                                                                                                                                       | `MERGED-UPSTREAM`（PR #33 已入 `origin/develop@a02cdac8`；真机/真人/正式发布验收仍待 `H1..H10`）                                 |
| `O-01`（未记录 ≠ 已证明不存在）                       | 1    | W4 (T03)     | ③ 来源追踪                       | `packages/engine/tests/test_w4_learning_checks.py`                                                                                                         | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`；真机/真人/正式发布验收仍待 `H1..H10`）                                 |
| `B-01`..`B-11`（行为触发/竞争/顺序/幂等）             | 11   | W4 (T06)     | ⑥ 行为应触发/不触发/重复         | `packages/engine/tests/test_w4_a2_behavior.py`、`tests/e2e/w4-workspaces-and-transfer.spec.ts`                                                             | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`；真机/真人/正式发布验收仍待 `H1..H10`）                                 |
| `A-01`..`A-10`（Diff/隐私/授权/报告安全）             | 10   | W3b          | ⑦⑧ 及 §12.5                      | `tests/e2e/w3b-agent-and-b2.spec.ts`、`tests/unit/w3b-cross-slice-before-commit-and-loopback.test.ts`、`packages/engine/tests/test_agent_before_commit.py` | `MERGED-UPSTREAM`（PR #34 已入 `origin/develop@a02cdac8`）；其中 `A-10` 的**真实版本化评估集**执行 → `DEP-H6`                    |
| `G-list-01`..`G-list-13`（沙盘逐轮/恢复/迁移/模板包） | 13   | W4 (T07/T10) | ⑦ 逐轮/指标/重放、⑧ 最小迁移任务 | `packages/engine/tests/test_w4_a2_scenario.py`、`test_w4_learning_checks.py`、`scripts/run-w4-packaged-workspaces.py`                                      | `MERGED-UPSTREAM`（PR #35 已入 `origin/develop@a02cdac8`）；其中 `G-list-09`/`G-list-13` 的**真机跨设备** → `UNVERIFIABLE-H2/H3` |

**计数闭合**：6 + 2 + 1 + 6 + 1 + 11 + 10 + 13 = **50**。✅ 与 `coverage.json` 实测条数一致。

### 3.1 PRD §11.2（可用性与学习效果验收）覆盖声明

- **完全人工辅助通过仍**不**计入独立迁移成功**：PRD §11.2 要求「迁移任务测试必须覆盖『Agent 完整代做』路径……操作可以标记完成，但该次尝试不得计入独立迁移成功」。实现侧由 `packages/engine/tests/test_agent_before_commit.py` 固定「完整代做仅随关联 ChangeSet 提交落账、未指定尝试保持 `independent`」，由 `w3b-cross-slice-before-commit-and-loopback.test.ts` 固定「完全辅助通过仍不计独立迁移成功」。该条在 `w3b-closure.json` 记为 `PRD-11.2-agent-full-assistance-exclusion: locally-verified-pass-pending-upstream-ci-and-develop-merge`。
- **5 名新手 / 80% 独立完成率**：PRD §11.2 的**产品侧**口径已实现在 `docs/release/user-study.md` 与 `docs/release/user-observation-template.csv`（5 行空表、辅助级别编码 `independent/product-hints/partial-human-help/full-demo/agent-full`、`coreCompleted`/`transferCompleted`/`transferIndependent`/`agentFullCounterexample` 四字段互不推导）。**但样本本身仍是空的** —— `H1` 未闭合。
- 因此 §11.2 的**验收条件（80% 独立完成率）当前无任何真实数据支撑**，本总账**不声称**其通过。

### 3.2 PRD §11.3（Agent 专项评估）覆盖声明

- 版本化评估集的**口径与失败定位要求**已由 `scripts/release/verify.mts` 落实为**结构性强制**：`evaluationSha256`、`returnedModel`、`serviceVersion`、`modelMode`、`modelEndpoint`、`requestedModel`、`modelDecisionSha256` 均须由**外部** `TRUSTED_FREEZE.json` 独立 pin，CLI 不得从待检清单反推。
- **Agent 模型档与正式写工具仍为空**：Wave 3b 纪要明确「Wave 4 禁用、正式写工具仍为空」，`FR-803` 工具白名单因此**尚未**放行正式写工具。
- **真实模型评估尚未执行**：真实 DeepSeek 调用、`deepseek-v4-pro` 返回标识、可得服务版本与真实评估哈希，全部需 `H6`。`A-10` 的「零次伪造、失败可定位」发布门槛在**真实服务**上**未被验证**。
- 结论：§11.3 的**发布门槛当前为「未验证」**，既不算通过，也不因工具到位而被视作通过。

### 3.3 PRD §12.1 新用户学习闭环（八步）覆盖声明

| 步骤 | 内容                                                   | 对应用例                                      | 本地状态   | 未闭合                              |
| :--- | :----------------------------------------------------- | :-------------------------------------------- | :--------- | :---------------------------------- |
| ①    | 安装、启动、打开设备运维内置案例                       | `FR-003`                                      | 工具侧通过 | 真机安装 → `H2`/`H3`                |
| ②    | 新增/修改业务概念与关系，核对 RDF                      | `FR-200`/`FR-201`                             | 工具侧通过 | —                                   |
| ③    | 离线提示完成 CSV 映射，稳定身份/预期事实/重复执行      | `M-01`..`M-06`、`O-01`                        | 工具侧通过 | 真人独立完成 → `H1`                 |
| ④    | 模板/可视化查询，核对完整预期与空结果                  | `Q-01`/`Q-02`                                 | 工具侧通过 | 真人独立完成 → `H1`                 |
| ⑤    | 无模型条件新增约束与规则，核对失败/修复/依据           | `V-01`、`R-01`..`R-06`                        | 工具侧通过 | 真人独立完成 → `H1`                 |
| ⑥    | 创建并测试行为，核对触发/不触发/重复事件               | `B-01`..`B-11`                                | 工具侧通过 | 真人独立完成 → `H1`                 |
| ⑦    | 运行基准与对比场景，核对逐轮/指标/假设/重放            | `G-list-01`..`G-list-08`                      | 工具侧通过 | 真人独立完成 → `H1`                 |
| ⑧    | 完成最小迁移任务，导出含数据版本与过期状态的 HTML 报告 | `G-list-09`..`G-list-13`、`FR-105`、`FR-1001` | 工具侧通过 | 真机跨设备 → `H2`/`H3`；真人 → `H1` |

**§12.1 的诚实结论**：八步的**产品实现与固定结果验收**已具备本地证明；但 §12.1 原文要求的是「**在没有开发人员帮助、没有预先配置模型 API 的情况下**，新用户应能够完成以下流程」——这**必须**由真人真机闭合（`H1`/`H2`/`H3`）。因此 **§12.1 当前为「工具侧通过、验收条件未闭合」**。

### 3.4 PRD §12.2..12.5 覆盖声明

| 章节                       | 内容                                                                                                           | 本地证明                                                                                                                                                                                  | 未闭合                                                                                                         |
| :------------------------- | :------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------- |
| §12.2 Agent 闭环（7 项）   | 模型配置后可验证的 Agent 修改建议 / Diff 冲突 / 中途失败回滚 / 查询草稿 / 忠实解释 / 授权边界 / 模型不可用降级 | `w3b-agent-and-b2.spec.ts`、`w3b-cross-slice-before-commit-and-loopback.test.ts`、`test_agent_before_commit.py`                                                                           | 需**有效且通过能力验证的模型 API** → `H6`；**正式写工具仍为空**（`FR-803`）→ 该项结构性缺口已登记，非外部 HOLD |
| §12.3 数据正确性与结果失效 | 映射 / 查询 / SHACL / 推理 / 行为 / 沙盘 / 恢复 七类                                                           | `test_w4_a2_behavior.py`、`test_w4_a2_scenario.py`、`test_w4_learning_checks.py`、`test_w3a_quality_b3.py`                                                                                | 存储失败与异常退出的**真机**故障注入 → `H2`/`H3`                                                               |
| §12.4 兼容性与迁移         | Turtle 可读性 / SPARQL 复现 / 项目包跨设备导入 / 重放前提                                                      | `w3b` Turtle 往返、`project-t10-comparison.py` 只读投影                                                                                                                                   | **跨设备真机导入** → `H2`/`H3`                                                                                 |
| §12.5 安全与恢复           | 产物/报告/日志/外发记录零凭据 / 完全本地零外发 / 写入版本化与可撤销 / HTML 纯文本安全显示 / 失败不损坏项目     | `w3b-pre-encoded-body.test.ts`（核准正文 == socket 实收字节、越界与完全本地零外发、审计无凭据）、`test_w4_learning_checks.py`（FR-901）、`w4-workspaces-and-transfer.spec.ts`（HTML CSP） | 三 OS 真实 safeStorage/DPAPI/Keychain → `H2`/`H3`；真实外发差异核对 → `H6`                                     |

---

## 4. 外部非代码人类发布 HOLD（`H1..H10`）

> **全部为 `PENDING_EXTERNAL_HOLD — NOT CLOSED`。** 以下每一项都需要**仓外**的人类、硬件、凭据或渠道资源，**无法**由本仓任何自动化、任何单测、任何目录包或任何合成自检闭合。**任何**把这些项写成「已闭合」的记录都是错误的。

| ID      | 内容                                                                                                                                        | 依赖资源                                                                   | 当前状态                             | 为什么不能由本仓闭合                                                                                                                                                                                           |
| :------ | :------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **H1**  | 5 名真实新手被试与 **80% 独立完成率**（含 **Agent 全代做反例**）                                                                            | 5 名未参与开发、缺乏本体经验的真人；独立主持人；同意与录屏授权             | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 需要真实真人行为数据。`docs/release/user-observation-template.csv` 当前只有 5 行**空表**；PRD §11.2 明确「测试人员不得直接代替用户操作」，自动化**不能**合成真人记录。                                         |
| **H2**  | 纯净 **Windows 11 x64** 真机安装 / 首启 / **DPAPI** / 崩溃 / 双向迁移 **26 项设备检查（`verify.mts` `DEVICE_CHECKS`）与 22 项双向迁移检查** | 干净镜像 Win11 x64 设备 + 独立会话 + 管理员边界 + 可用时段                 | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 需要真实 Windows 真机与真实 DPAPI 后端。Server2025 CI、macOS CI、Linux 容器**不可替代**；`collect-windows.ps1` 因无批准 Windows 执行环境**只做静态审阅**，未记运行通过。                                       |
| **H3**  | **macOS 15 arm64** 真机 Gatekeeper / 公证 / **Keychain** / 原生恢复 / 双向迁移                                                              | 干净镜像 macOS 15 arm64 设备 + 批准隔离会话                                | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 需要真实 Gatekeeper、公证票据与 Keychain 升级识别路径。当前 macOS 26 CI 腿与本机开发机**不可替代**目标真机。                                                                                                   |
| **H4**  | **Apple Developer ID** 签名与公证授权（含 `hardenedRuntime` / `notarize` 实环境凭证）                                                       | Apple Developer Program 账号、有效 Developer ID 应用证书、 notarytool 凭据 | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | `electron-builder.yml` 已声明 `notarize: true` / `hardenedRuntime: true` / `forceCodeSigning: true` 且**零硬编码身份**，但 `notarize: true` 本身**不会取得认证资源**；须由负责人在批准环境注入既有身份与权限。 |
| **H5**  | **Windows 代码签名证书**与时间戳服务                                                                                                        | 有效代码签名证书 + RFC3161 时间戳服务（signtool）                          | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | `signAndEditExecutable` / `signExecutable` 已默认启用，但证书与时间戳链只能由证书持有方提供；无证书不得用 adhoc 冒充。                                                                                         |
| **H6**  | 真实 **DeepSeek API**（`https://api.deepseek.com/chat/completions` / `deepseek-v4-pro`）权限与可消费余额                                    | 可用 API Key + 账户余额 + 真实返回标识与可得服务版本                       | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 协议与合成探针**不等于**真实服务通过。`FR-806` 真实延迟、`FR-900` 真实能力验证、`FR-902` 真实外发最小差异、`A-10` 真实评估集、`§11.3` 发布门槛全部依赖此项。                                                   |
| **H7**  | 正式受控**下载渠道 URL**、受众访问权限与安装包**校验哈希**                                                                                  | 已授权发布渠道 + 受众权限 + 最终签名包                                     | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 下载副本须与签名候选包**逐字节**一致；URL 不得存临时鉴权参数。当前无正式包即无正式下载副本。                                                                                                                   |
| **H8**  | **Q5** 大规模容量通过线审定与真机/实样测量                                                                                                  | 审定的容量口径 + 真机与真实脱敏样本                                        | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 工具侧限额（16MiB / 8GiB）是**工程边界，不是 Q5 业务容量或性能指标**；容量通过线须由 owner 审定后以冻结门槛做正式验收。                                                                                        |
| **H9**  | **同候选双模型**指定终态 L2 复核（正式 `releaseAuthorized` 前由总控绑定最终签名候选）                                                       | 两个指定模型的全新实际终态复核（不得复用已 completed 会话）                | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 必须绑定**最终签名候选**才有意义；当前无正式签名候选可绑定。历史上各 Wave 的 L2 复核均针对**本地候选**，不能替代终态复核。                                                                                     |
| **H10** | 总控**发布放行决策**（`verify.mts` 恒锁死 `releaseAuthorized: false`）                                                                      | 总控决策                                                                   | `PENDING_EXTERNAL_HOLD — NOT CLOSED` | 工具**永不**自行放行；这是唯一能把 `releaseAuthorized` 从 `false` 变为放行的动作。                                                                                                                             |

**HOLD 汇总**：`holdsRemaining = ["H1","H2","H3","H4","H5","H6","H7","H8","H9","H10"]` —— **10 项全部未闭合**。

### 4.1 「哪些东西**不能**用来冒充 HOLD 已闭合」

以下**均不构成**任何 HOLD 的闭合证据（Reviewer B 必核陷阱）：

1. `npm run package:dir` 产出的**无签名目录预验包** —— 不是已签名安装器，不是真机验收。
2. **合成自检 / 合成 fixture / 合成探针** —— 只能证明核验器能读批准输入并拒绝错误，**不证明**领域实际输出或 50 条 G 产品用例通过。
3. `verify.mts` 返回 `consistent: true` —— 只是**必要的一致性检查**，不是上线放行。
4. `release:hygiene` 的 `summary.json` —— 恒声明 `releaseAuthorized: false` 与 `installerAcceptanceClaimed: false`。
5. 本地单测 / Linux 容器 / macOS 开发机 / CI 腿 —— **均不能替代**目标干净真机（`H2`/`H3`）。
6. 历史 Wave 的 L2 复核结论 —— 绑定的是**旧候选**，候选变化后按原规则**必须重验**。

---

## 5. 澄清与术语固定

| 项            | 固定口径                                                                                                                                                                                                                                                                                                       |
| :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PRD 迁移章节  | 是 **`FR-1000`**（项目包清单、版本、迁移与重放）与 **`FR-1001`**（HTML 报告导出与安全显示），以及安全条款 **`FR-901`**（密钥保护）。**PRD 中不存在 `FR-905` / `FR-906`**，任何引用这两个编号的记录都是错误的。                                                                                                 |
| P0 条数       | **57**（PRD `### FR-` 标题 59 条中，`FR-506` 与 `FR-903` 为 P1）。                                                                                                                                                                                                                                             |
| 附录 G 条数   | **50**（`coverage.json` 的 `entries`，与 `cases.json` 的 `cases` 各 50 条互相印证）。                                                                                                                                                                                                                          |
| 冻结基线      | 已提交的 **18 文件**基线 `tests/fixtures/product-baselines/manifest.json`，SHA-256 `0588f5804f0b13c55ccece009b444cfd3efcc572e53067703ca8d9224f4cf8ad`，`version: prd-v0.6-learning-1`，含 `content/learning/extensions.json`；PRD SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`。 |
| 状态唯一入口  | 本文件 `docs/iterations/W5/release-convergence-ledger.md`。                                                                                                                                                                                                                                                    |
| `newFRPasses` | **`0`**。                                                                                                                                                                                                                                                                                                      |

---

## 6. 证据索引

| 类型           | 路径                                                                                                                                                                                                                                                                                                                                                                                                                        |
| :------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 本仓实现       | `scripts/release/verify.mts`、`scripts/release/verify-release.mjs`、`scripts/release/project-t10-comparison.py`、`scripts/release/collect-macos.sh`、`scripts/release/collect-windows.ps1`、`scripts/release/pe-machine.ps1`、`scripts/run-w5-packaged-release-hygiene.py`                                                                                                                                                  |
| 本仓配置       | `apps/desktop/electron-builder.yml`、`apps/desktop/package.json`、根 `package.json`、`.gitignore`、`.prettierignore`、`eslint.config.mjs`、`.github/workflows/ci.yml`                                                                                                                                                                                                                                                       |
| 本仓单测       | `tests/unit/t11-release.test.ts`、`tests/unit/t11-release-io.test.ts`、`packages/engine/tests/test_w5_release_projection.py`                                                                                                                                                                                                                                                                                                |
| 本仓文档       | `docs/release/README.md`、`docs/release/migration-recovery.md`、`docs/release/q5-decision-proposal-20261022.md`、`docs/release/target-device-runbook.md`、`docs/release/user-study.md`、`docs/release/user-observation-template.csv`、`docs/iterations/T11/acceptance.md`、`docs/iterations/T11/shared-file-handoff.md`、`docs/iterations/T11/selection-comparison-v2.md`、`docs/iterations/T11/selection-comparison-v3.md` |
| Wave 闭环记录  | `iteration-control/2026-10-21-weekly-release/execute-20261115/{g0-closure,w3a-closure,w3b-closure,w4-closure}.json`、`w4-upstream-r4-adjudication.json`、`w4-develop-ci-green.json`（Run `45337490364`）                                                                                                                                                                                                                    |
| 历史阻塞与演进 | `iteration-control/2026-10-21-weekly-release/execute-20261115/PAUSED-GITHUB-BILLING-20261116.json`、`b1a-ci-failed-43808662149.json`（历史计费阻塞后已通过公开仓库解除并完成 `#27..#35` 合入）                                                                                                                                                                                                                              |
| 评审量表       | `docs/verification/FEATURE-MAP.md`（`W5: B5/T11 发布收敛与门禁` 行）、`docs/verification/VERIFY.md` §3（W5 触发行）                                                                                                                                                                                                                                                                                                         |

---

## 7. 变更与提交纪律

本分支已按 `origin/develop@a02cdac8`（`M_W4`）完成合并对齐（`e6de8c1b`），并在后续收敛中完成以下增量更新：

1. **`6ead1dfc`**：强制 `packages/engine/tests/test_w5_release_projection.py` 以 UTF-8 写入宿主机选取元数据并同步本总账与 `origin/develop@a02cdac8` 基线；
2. **`e0e98300`**：按 `weeds.md` 晋升两项出现 `>=2` 次的存量 CI 偶发——在 `packages/engine/src/ontolearn_engine/coordinator.py` 新增 `_signal_worker` 绕过 POSIX `Popen.poll()` / `waitpid(WNOHANG)` 竞态（附 `packages/engine/tests/test_learning_jobstore_integration.py` 2 项确定性回归单测），并将 `tests/e2e/t04-query-variants.spec.ts` `Q-02` 双重启 E2E 用例对齐基线 `test.setTimeout(60000)`（PR `#36` R1 Run `45360969524` 曾暴露上述两项及 Windows C1 偶发，经 `e0e98300` 修复后 R2 Run `45387347671` Attempt 1 三平台全绿）；
3. **R3 闭环加固**：响应 R1 三方 0% 自审 L2 审计意见，加固 `scripts/release/project-t10-comparison.py`（fd 预检、流式解压上限、缺失成员/非字典 JSON/非整型大小统一固定 exit 2、`layer:id` 复合定义主键）、扩充 `packages/engine/tests/test_w5_release_projection.py` 至 10 项测试、在根 `package.json`/`package-lock.json` 显式声明同版 `"zod": "4.6.7"`、加固 `tests/unit/t11-release-io.test.ts` 全 fd 关闭与 POSIX `ELOOP` 断言、扩展 `_signal_worker` 为捕获 `OSError`、并在 6 份发布文档与量表内校准 `TRUSTED_FREEZE` 程序性信任边界、macOS 首发 `arm64` 范围决策及逐工具字段声明；同时保留 Windows C1 `W-WIN-CSP-CRASH-FLAKE` 在 `weeds.md` 的存量档案，不声称已消除。

全过程严格未触碰 `docs/reviews/**`、`docs/source-manifest.json`、归档源文件、`packages/engine/src/ontolearn_engine/storage.py`、`packages/engine/src/ontolearn_engine/transfer/**`、`OntoLearn-Studio`（`e6ed8101`）及任何其他冻结 worktree。

**`Verified: check, verify:sources, cp1252-sim, e2e, packaged`**
