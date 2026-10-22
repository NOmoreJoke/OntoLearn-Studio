# T11 round-1 独立审查报告（MiniMax M3.1-Flash）

> 本报告为 T11 离线发布证据核验工具**工程范围**的独立只读审查终态。报告由指定模型 M3.1-Flash / xhigh 在独立 review worktree 中实际执行产生，结论为**真实终态**，未预设通过，未修改任何受审实现/测试/配置/依赖，未 stage/commit/push/PR，未启动产品，未关闭任何父 T11 发布门。

---

## 0. 终态结论

| 维度 | 结论 |
| --- | --- |
| **完整工程范围（4 脚本 + 专属测试 + 2 fixture + docs/release 5 文件 + docs/iterations/T11 3 文件 + 全部评审/来源/失败证据 + 8 份流程变化）** | **不通过** |
| 父 T11 发布门（57 P0 同候选、真实双平台安装/签名/公证/渠道、真实模型 API、五真人、指定双审、push/PR/CI/合并/远端、最终下载实装） | **无法验证 / 未关闭**，本轮不关闭任何一项 |
| 核验器自身发布授权 | 始终 `releaseAuthorized:false`（已实测验证），与 `docs/release/README.md:3` 一致 |

**不通过的唯一硬因**：受审实现与其自身验收文档在比较投影 v2 的核心口径上直接冲突——文档两处明确声明"仅固定 G.6 冲突场景的必需层不可为空""v2 取代 v1 过度强制所有层非空"，而实现对**每一个**快照无条件强制这 6 个必需层非空，并有专门反例测试把该行为固化为 v2 预期（详见 F-A，高严重度）。另有 3 项中严重度缺口（F-B 端点硬编码无依据、F-C 基线 17 文件集未在核验器内约束、F-L 失败原件表述超出归档实际内容）。

**未发现**任何"可导致虚假发布授权"的问题：核验器无任何路径可输出 `releaseAuthorized:true`；预期侧全部由独立 freeze 外部 pin；伪造/漂移/自证类反例均被拒绝。

---

## 1. 任务来源、模型与权限读回

| 项 | 实际值 | 读回来源 |
| --- | --- | --- |
| 任务来源 | 用户直接提交本条附件提示（`/root` 派发的 round-1 待调度提示 + 精确派发补充 + 当前桌面政策原文） | 附件本体 |
| 附件字节/行数 | 53774 bytes / 322 行（`wc -l` 计 321 个换行 + 无尾换行末行） | 实测 |
| 附件 SHA256 | `35a8ee75e450d16b199dd25d052c43f57613b5b473b99c291844131779f40978` — **与用户给定值一致** | `shasum -a 256` |
| 前缀完整性 | 附件前 29857 字节与仓内 `docs/reviews/T11/round-1/minimax-m31flash-prompt.md` **逐字节相同**（其 sha256 `36a3c694…dde4c0`），提示自称"前缀是原 round-1 完整原字节"**成立** | 实测比对 |
| 模型 | `minimax/MiniMax-M3.1-Flash`，variant `thinking`，`thinking.effort = xhigh` | `mavis session get --session me`（本会话）＋ `owner-task-settings.json` |
| 权限模式 | 始终授权 / `bypassPermissions`（未读取全局配置或日志） | `.t11-review-runtime/metadata/owner-task-settings.json`（UI 设置收据，sha256 `64c7f506…dc843`） |
| 会话/任务 ID | `mvs_52775b8f354f485a919e2c0e8ebe6bd2`（sessionId 与收据 taskId 一致） | 同上 |
| turn / stream ID | 本运行时 `session get` 不暴露 turn/stream 标识，**未获得即不记录**，不编造 | — |
| 工作区 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-minimax-review-7d28fdb`（与提示指定唯一工作区一致） | 实测 `pwd` ＋ session 元数据 |

模型/思考等级与指定值一致；权限以本方 UI 收据为准，未依赖用户级配置推断。

---

## 2. 冻结输入、路径与漂移核验

| 项 | 值 | 核验结果 |
| --- | --- | --- |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 对象存在；`git diff --check BASE PRODUCT` 无空白错误 |
| product | `7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4` | 对象存在 |
| process anchor | `9f12f17b74f1e26f310c8298232a7fe66cb026ad` | 对象存在 |
| review HEAD | `b6e57a0534c94316dd07c3a87b4b8931d5a39501` | 本工作树 detached HEAD，一致；**未切分支** |
| 分支/工作树 | 原开发树 `/…/.worktrees/T11-release`、`feature/weekly-t11-release` 为**历史来源说明**，非本轮 workspace；未复制或采用其实现 | — |
| checkout 状态 | 仅 ` M AGENTS.md` ＋ 未跟踪 `.t11-review-runtime/` | 与提示一致 |

### 2.1 25 条 product 路径逐条 git blob 核验（全部通过）

以 `git show PRODUCT:path` 取冻结内容并逐条计算 SHA256，与 `docs/reviews/T11/round-1/manifest.json` 的 `productSHA256`/`productBytes` 比对，**25/25 全部相等**；同时比对工作树实体字节，21 条相等，4 条（`shared-file-handoff.md`、`completion-audit.md`、`operating-policy-receipt.json`、`status.md`）与 manifest 的 `currentSHA256` 相等（= 流程锚点字节，符合 manifest 的 `currentEqualsProduct:false` 登记）。原始记录：`.t11-review-runtime/raw/hash-verify-25product.log`。

### 2.2 8 份流程变化（process-only）按锚点字节核验（全部通过）

`PRODUCT→ANCHOR` 恰为 8 项：4 改（shared-file-handoff.md、completion-audit.md、operating-policy-receipt.json、status.md）＋ 4 增（blocked-audit.json、format-public-ownership-receipt.json、format-python-ownership-receipt.json、recovery.json）；逐条按锚点 `git show` 计算的字节数与 SHA256 与 manifest `processOnlyChanges` **8/8 相等**。原始记录：`hash-verify-8process.log`。`ANCHOR→HEAD` 的 9 个新增文件为 round-1 准备件（manifest、两个提示、raw-logs 索引与归档、preparation-index、scope-registration、history-disposition、document-review），属流程证据，**不替换 product 的验收范围**，本轮未将其当作产品基线或发布 manifest。

### 2.3 受控 822 文件漂移门禁（通过）

以 `metadata/source-setup.json` 的 822 条记录，逐条比对 `git rev-parse HEAD:path` ↔ 记录 `gitBlob`、git blob 实体 SHA256 ↔ 记录 `sha256`、工作树实体 SHA256 ↔ 记录 `actualSHA256`：**822/822 全部匹配，0 处 blob 偏差，0 处实体偏差**。唯一声明差异为 `AGENTS.md`（product/HEAD blob `1b3c0291…`，当前实体 `de15f6ce…`，等于 `expectedAGENTSSHA256`，属已传播的操作政策差异，保持未暂存）。→ **受审源码/验收/依赖/基线无漂移，无需请求总控重新冻结。**

---

## 3. 全部 25 条 product 路径覆盖表（逐条已读）

| # | 路径 | 字节 | SHA256（前16） | 审读深度 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 1 | `docs/iterations/T11/acceptance.md` | 3294 | `e8e259199bb194a1` | 全文 | 验收命令与边界表述准确；见 F-E |
| 2 | `docs/iterations/T11/selection-comparison-v2.md` | 2625 | `03dd36b5cc3493cf` | 全文 | 口径声明与实现冲突，见 F-A |
| 3 | `docs/iterations/T11/shared-file-handoff.md` | 7876 | `fb5f2b9bb21930d0` | 全文（含锚点版 9781） | 流程/所有权提案，无产品验收；无缺陷 |
| 4 | `docs/release/README.md` | 6878 | `0d738c720e31efa6` | 全文 | 与实现冲突（F-A）、口径差异（F-D/F-F） |
| 5 | `docs/release/migration-recovery.md` | 5108 | `7177d924771fab5b` | 全文 | 模板包无表达（F-A）；回退子项缺 id（F-F） |
| 6 | `docs/release/target-device-runbook.md` | 4648 | `29fda85e9e91d736` | 全文 | 待执行规范；工具不强制部分步骤（F-G） |
| 7 | `docs/release/user-observation-template.csv` | 647 | `c2229f58febf8c76` | 全文 | 28 列、5 空行；工具不解析（F-G） |
| 8 | `docs/release/user-study.md` | 4075 | `9c77c08dc8c770fd` | 全文 | 80% 口径差异（F-D） |
| 9 | `docs/reviews/T11/approved-fixed-baseline-probe.json` | 3833 | `614236667b67a576` | 全文 | 65/65 零 skip 与 3 skip 边界**实测吻合** |
| 10 | `docs/reviews/T11/completion-audit.md` | 7534 | `f38a846b3e498c64` | 全文（锚点版 8059） | 父门禁判定与实际一致；版本双值见 F-K |
| 11 | `docs/reviews/T11/external-review-permissions-receipt.json` | 1722 | `bd354b1349ddbbed` | 全文 | 与当前权限政策一致；无缺陷 |
| 12 | `docs/reviews/T11/first-failure.json` | 603 | `2d6b63f58d2cbdb9` | 全文 | 如实声明"非完整 raw"，与 F-L 相关 |
| 13 | `docs/reviews/T11/internal-review.md` | 2781 | `ab5f4815eaf6f7e3` | 全文 | 历史内审项与处置对应，无新增缺陷 |
| 14 | `docs/reviews/T11/operating-policy-receipt.json` | 2582 | `9e36049f2ea4bd9a` | 全文（锚点版 4177） | 状态双值见 F-K |
| 15 | `docs/reviews/T11/selection-v2-review.md` | 2402 | `dea7c2d6064a21ff` | 全文 | 内审"通过"仅覆盖既有内部审查，未冒充本轮 |
| 16 | `docs/reviews/T11/status.md` | 6579 | `c3a360b0b182d160` | 全文（锚点版 9083） | 失败原件表述见 F-L；状态双值见 F-K |
| 17 | `docs/reviews/T11/t09-readonly-alignment.json` | 617 | `038b9e851ff65294` | 全文 | 17 文件/50 条目/3 指针，manifest SHA 与批准值一致 |
| 18 | `docs/reviews/T11/verification.json` | 8857 | `0cb03592bcde2f0f` | 全文 | 65/695/1052 口径与本轮实测一致；48 日志 SHA 与归档一致 |
| 19 | `scripts/release/collect-macos.sh` | 1793 | `f273da7b4eaf8eb2` | 全文 30 行 | 只读合规；失败处理见 F-H |
| 20 | `scripts/release/collect-windows.ps1` | 2927 | `9194c70522154249` | 全文 50 行 | 只读合规；绑定与目标见 F-H |
| 21 | `scripts/release/verify-release.mjs` | 1133 | `184141eb11691727` | 全文 29 行 | CLI 语义与 README:15 完全一致 |
| 22 | `scripts/release/verify.ts` | 31794 | `8f6aac79f43167cd` | 全文 923 行 | 主实现；问题见 F-A/F-B/F-C |
| 23 | `tests/fixtures/release/comparison.json` | 2543 | `615f14f86c6c3b1a` | 全文 | t11-comparison-v2 样例；schema 覆盖 6 必需层 |
| 24 | `tests/fixtures/release/synthetic-profile.json` | 348 | `654965c87ff3f26e` | 全文 | 合成身份声明清晰，无误导 |
| 25 | `tests/unit/t11-release.test.ts` | 33509 | `504d23c278fb9f1c` | 全文 947 行 | 断言粒度合格；含 F-A 反向固化 |

**未抽样**：25 条全部以 `git show PRODUCT:path` 读取冻结内容并核 hash 后逐条审读，含两个 collector 与全部 JSON 证据；未只审 `verify.ts`。

---

## 4. 核验重点逐条比对结果

| 核验重点 | 工具行为（位置） | 本轮判定 |
| --- | --- | --- |
| 严格 schema | `manifestSchema`/`expectedSchema` 均 `.strict()`，边界数据全部 zod 解析 | **符合** |
| 安全文件读取 / symlink 边界 | `boundPath`（verify.ts:288-303）拒绝对路径、`\`、`..`/`.` 段；`realpathSync` 解析后 `relative` 必须落在根内；空文件/超限拒绝；`readBound` 校验 SHA256 | **符合**；`tests/unit/t11-release.test.ts:869-879` 已覆盖 `../` 穿越与外部 symlink，实测拒绝 |
| 候选/来源/受审/构建/报告/安装资产绑定 | `CANDIDATE_SHA`/`BASELINE_IDENTITY`/`FREEZE_IDENTITY`/`${label}_BINDING`/`${label}_BUILD_SHA`/`${label}_ASSET`/`ROLLBACK_IDENTITY_PIN` | **符合** |
| 独立 freeze 的预期/时间/模型/旧资产 pin，防两边同填自证 | `expectedResults` 由外部 `TRUSTED_FREEZE.json` 提供（verify-release.mjs:18-21，注释明示"never derives them from the manifest"）；冻结时间、模型档位/返回模型/服务版本、恢复与迁移源快照、上一版双资产均外部 pin | **符合**，设计正确；产品报告 expected 与基线 `cases.json` 完整 expected 双向比对（`PRODUCT_EXPECTATION_BASELINE`） |
| PE / DMG 结构 | `installerFormat`（verify.ts:333-357）：PE 校验 MZ + e_lfanew + `PE\0\0` + machine∈{0x14c,0x8664}；DMG 校验尾部 512 偏移 `koly` | **符合（结构级）**；不做 NSIS/DMG 实质格式与密码学校验，属能力边界（F-I） |
| 签名/公证/许可证/最终渠道拒绝边界 | 缺签名/adhoc 身份/缺时间戳 → `${label}_SIGNATURE`；Mac 缺 HardenedRuntime/公证/staple → `MAC_NOTARIZATION`；组件清单与 inventory 全等比对 → `${label}_LICENSE_COVERAGE`；渠道 URL 禁凭据/查询串/片段、下载件字节哈希须与候选包一致 → `${label}_CHANNEL_*` | **符合**，反例齐全 |
| 57 P0 | PRD 标题正则抽取须恰为 57 且唯一（verify.ts:462-463）；本轮独立解析 PRD 得 **57 唯一**，与工具口径一致 | **符合** |
| T09 manifest 全文件 | 核验器校验 baseline 内每个文件的字节哈希，并点名 5 个必需文件 + coverage.json；**不校验文件总数/版本/必需路径** | **部分符合**（F-C） |
| G 完整 expected / E.5 exact / replay 指针绑定 | `cases.json` 须 50 条；`exactFile`+`exactPointer`、`replayExactFile`+`replayExactPointer` 展开为实际完整对象再比较；缺指针/引用文件漂移/同数量错对象均拒绝 | **符合**；本轮独立解析 PRD 得 37 表项 + 13 列表项 = 50，与工具派生口径一致 |
| RDF 完整 SPO 多重集合、其他数组保序 | `compareProductComplete`（verify.ts:373-398）仅对 `facts/assertedFacts/inferred/addedTriples/inputs` 且元素为完整 SPO 时排序，保留重复数；其余数组严格保序 | **符合**；单测 461-475 直接断言重复数与保序 |
| 比较 v2：当前恢复/映射重跑/沙盘重放分开 | `capabilities.restoreCurrent` 恒 true；`rerunOriginalMapping` 与 `replaySandbox` 按 `selection`+`dependencies` 齐全性独立判定（verify.ts:835-850） | **符合** |
| 未选原文/历史/会话/旧 undo 排除 | `superRefine`（verify.ts:826-834）对 5 类未选内容强制为空 | **符合** |
| 零提交可重放条件 | `canReplay` 依赖 `historicalRuns` 选中且 history 非空 + inputs/configuration/semantics 齐全；**不以已有输出轮次（rounds）为前提** | **符合**（rounds 未作为前提，与 `migration-recovery.md:11`、内审 P2 处置一致） |
| 至少 5 真人 / 80% 与迁移辅助区分 | `users` ≥5 ≤100；`human && !developer && ontologyNovice`；辅助级别枚举独立编码；口头帮助/完整示范/Agent 代做不计入；`agentMarkedIndependent` 必须 false；`agentFullCounterexample` 必须有 | **符合（偏严）**，80% 分子口径差异见 F-D |
| CLI exit 与 synthetic 模式不得发布 | verify-release.mjs:24 → 仅 `consistent && mode==='evidence'` 退出 0；synthetic 退 1；不可读/格式错退 2；输出恒 `releaseAuthorized:false` | **符合**，且 `tests/unit/t11-release.test.ts:931-946` 实测 synthetic→1、非法→2 且不回显敏感内容 |
| 两 collector 的只读/目标/失败处理 | Mac：仅在 macOS 15 arm64、输出目录必须新建、只采集元数据与只读校验（codesign/spctl/stapler validate），不签名/不公证/不安装/不启动；Win：必须 `-ApprovedIsolatedSession` + Windows 11 + X64，真实 `Get-AuthenticodeSignature` 校验 Status=Valid 且有时间戳证书，非安装器必须 x64；两者均不安装/不启动 | **只读与目标校验符合**；失败处理与绑定见 F-H |
| 工具不得把"consistent"写成发布授权 | `Verification.releaseAuthorized` 类型恒为 `false`（verify.ts:168-173、922）；README:3、:15、:29 一致声明 | **符合** |

---

## 5. 本轮实际执行的检查（原始结果保全）

环境：自带 `node_modules` 与 `.venv`（未复用 peer/原开发树可变环境）；`TMPDIR/TMP/TEMP` 统一指向 `.t11-review-runtime/tmp`；未运行产品。

| # | 命令 | 退出码 | 实际结果 | 原始日志（sha256 前16） |
| --- | --- | --- | --- | --- |
| C7 | `T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-release.test.ts` | **0** | **Tests 65 passed (65)，零 skip** | `t11-specialized-probe.log` `56519284cd880ce3` |
| C8 | `npx vitest run tests/unit/t11-release.test.ts`（默认） | 0 | **62 passed \| 3 skipped (65)** —— 3 项固定输入探针默认 skip，与"默认通过不证明固定输入联验"口径一致 | `t11-default-mode.log` `7a71d780dc43059e` |
| C9 | `T11_FIXED_BASELINE_PROBE=1 npm run check` | **1** | lint **通过**；format:check **失败，仅 1 个文件**：`.t11-review-runtime/metadata/setup.json`（**本轮自建 runtime 元数据**，非产品代码、不在 25 条冻结路径内）；`&&` 链在此中断 | `full-check-with-probe.log` `ddd7af3be678ef09` |
| C10 | `T11_FIXED_BASELINE_PROBE=1 npm run typecheck && npm test && npm run build && npm run engine:check` | **0** | typecheck 通过；**vitest 16 文件 / 695 测试全过**；electron-vite 构建通过；`uv run --frozen ruff check` + `ruff format --check` 全过；**pytest 1052 passed** | `full-check-rest.log` `3572d0392990c86f` |
| C11 | `npx eslint --no-ignore scripts/release/verify.ts scripts/release/verify-release.mjs` | 0 | 无问题 | `release-explicit-checks.log` `6c5c0d15efb77a12` |
| C12 | `npx prettier --ignore-path /dev/null --check <release 全集>` | 0 | 全部符合 Prettier 风格 | 同上 |
| C13 | `bash -n scripts/release/collect-macos.sh` | 0 | 语法通过（**未执行 collector**） | 同上 |
| C14 | `npm run verify:sources` | 0 | 已核对 12 个归档源文件 | 同上 |
| C15 | `git diff --check BASE PRODUCT` | 0 | 无空白错误 | — |
| C5 | raw-logs 归档逐文件比对 | 0 | 归档 sha256 `c1f34bd3…`/7208 bytes 与索引一致；**48 条目全部匹配**（无缺、无哈希/字节偏差） | `raw-logs-archive-verify.log` `bde0821b32f7bfcf` |

**关于 C9 的处置声明**：format:check 唯一命中的文件是本轮 setup 阶段生成的 runtime 元数据 `setup.json`（owner 收据）。按提示要求，我**未删除该文件、未新增 ignore 规则、未 exclude 后宣称原完整检查通过**；owner 收据字节保持不变。为取得同等覆盖，剩余链路步骤（typecheck/test/build/engine:check）按仓库原定义逐条实际执行并全绿（C10）。结论应表述为：**产品树本身无格式问题；`npm run check` 在本工作树的 exit 1 由本轮自建元数据引起，非受审候选缺陷。**

---

## 6. 未运行 / 无法验证边界（逐项如实保留）

| 项 | 状态 | 阻断影响 |
| --- | --- | --- |
| Windows collector 运行 | **未运行**（无批准 Windows 执行环境；仅静态审阅） | 无法验证 PowerShell 脚本在真实 Win11 x64 上的行为、Authenticode 状态读取、PE 解析与失败路径 |
| Mac collector 运行 | **未运行**（仅既有 `bash -n` 语法证据） | 无法验证 codesign/spctl/stapler 真实输出与 fail-fast 行为 |
| 目标设备安装/native/凭据/恢复/迁移 | **未运行** | DEVICE_CHECKS 24 项无任何真实设备证据 |
| 真实签名/公证/ticket/最终渠道与下载实装 | **未执行**（不签名、不公证提交） | 签名链真实性不可证；渠道 hash 一致性仅有合成样例 |
| 真实模型 API 评估 | **未调用**（不发未经授权 API） | 模型档位/零伪造仅结构校验 |
| 五真人 80% 用户研究 | **未执行** | 真人资格、记录真实度不可证 |
| 指定双模型审查（GLM-5.3/最高、M3.1-Flash/xhigh） | **本轮尚未完成**（本报告是 M3.1-Flash 一方终态） | 双方同候选双审门未关闭 |
| push/PR/实际 CI/正常合并/远端核验/最终下载实装 | **未执行**（未提交、未推送） | 发布链路门未关闭 |
| e2e / install-electron / package:dir | **未授权未执行** | 本轮为工具范围审查，非打包验收 |
| 首跑 38 失败完整 raw | **永久缺失**（归档内无任何含 "38 failed" 的日志） | 历史失败只能凭 `first-failure.json` 摘要/摘录＋原会话 transcript 复述，不可从归档完整重建 |

**工具能力边界（不可由工具证明，须外部独立核验）**：报告签发者身份、签名人/证书链真实性、真人资格与真实操作、原始报告真实性、组件清单是否由实际包与固定依赖图得出。`docs/release/README.md:29` 已作此声明，核验器实现与之一致。

---

## 7. 发现清单（严重度 / 文件行 / 触发 / 影响 / 证据 / 建议）

### F-A【高】比较投影 v2 必需层口径：文档声明与实现直接冲突

- **位置**：`scripts/release/verify.ts:777`（`const coreRows = rows.min(1)`）与 `:809-814`（`facts/definitions/ownership/mappingState/queries/results` 全部 `coreRows`）；`tests/unit/t11-release.test.ts:558-566`（"still rejects a missing mandatory source/ownership layer in a current-only package"）。
- **冲突文档**：`docs/release/README.md:25` 明确写"**仅固定 G.6 冲突场景的**事实/定义/来源/映射/查询核对必需层不可为空"，并称"**v2 取代本工具先前过度强制所有层非空的 v1**"；`docs/reviews/T11/round-1/history-disposition.md:8` 同样记为"v2 只对固定丰富冲突 fixture 要求当前必需层"；`docs/iterations/T11/selection-comparison-v2.md` 亦以此为 v2 变更主张。
- **触发**：对任一快照（`recovery.backup`/`recovery.restored` 与两方向 `migration.before/after`）提交 facts/ownership 等 6 层中任一层为空的合法 v2 投影。
- **影响**：①核验器会判 `MIGRATION_AFTER_SCHEMA`/`RECOVERY_*_SCHEMA` 并拒绝一份**符合文档口径**的当前态恢复投影 → 工具比已接受验收更严，可能产生虚假失败；②README:25 与 history-disposition:8 关于"v2 已解除过度强制"的陈述**在受审实现中不成立**，读者会据此误判工具行为；③专门反例把 v1 行为固化为 v2 预期，测试无法暴露该冲突；④`migration-recovery.md:15` 要求的"只含定义/缺事实或来源的包**标模板**"这一合法观察态在快照 schema 中**无 template 标记字段**，只能被当作 schema 非法而拒绝。
- **证据**：本轮已实测 C7/C8 全绿，但同时实测到"current-only 包清空 ownership 必被拒"由 `tests/unit/t11-release.test.ts:558-566` 断言；`docs/release/README.md:25` 与 `history-disposition.md:8` 原文如上；`compareComplete`/`snapshotSchema` 强制 `min(1)` 见 verify.ts:777、809-814。
- **建议（由唯一 owner 在新候选中处理，本轮不自行修复）**：三选一并同步文档与测试——①按 v2 声明把 6 层非空约束收敛为"仅 G.6 固定冲突 fixture 适用"，其余场景按各层实际选择范围校验，并补 template 标记表达；②保留实现但改写 README:25 与 history-disposition:8 的口径陈述，明确 v2 仅放宽 7 个可选层；③按场景参数化判定并保留 G.6 专项正反例。任一方案都须重跑专项探针与全仓 check，并按原门禁重新独立审查。

### F-B【中】核验器把厂商端点与模型名硬编码为字面量，且无 PRD/文档依据

- **位置**：`scripts/release/verify.ts:114-115`：`endpoint: z.literal('https://api.deepseek.com/chat/completions')`、`requestedModel: z.literal('deepseek-v4-pro')`。
- **触发**：真实发布清单使用其他已批准端点或模型（例如按 AGENTS「模型外发」要求走主进程唯一网关）。
- **影响**：`MANIFEST_SCHEMA` 直接失败（fail-closed，安全方向正确），但会把一个**产品口径问题**伪装成清单格式错误，且使工具无法承载已批准的其他模型档位；冻结侧 `returnedModel`/`serviceVersion` 可变而 `endpoint`/`requestedModel` 不可变，口径不对称。
- **证据**：全仓检索 `deepseek` 仅命中 `verify.ts:114-115` 与 `tests/unit/t11-release.test.ts:338-339`；**PRD 全目录零命中**；`docs/release/README.md:15` 与 `docs/release/target-device-runbook.md` 只要求"记录端点/版本化评估"，未出现该端点与模型名；`AGENTS.md` 规定模型外发须经主进程唯一网关（S3 前不得接入），与该字面量口径未见对齐说明。
- **建议**：确认该端点/模型的授权来源（PRD 条款、总控批准口径或 T08/I06 网关约定），并把它改为"由 freeze/expected 外部 pin 的字段 + 允许值白名单"，或至少在文档中写明依据与适用边界；若口径本身有误，应改为可配置并重新审查。

### F-C【中】T09 基线的 17 文件全集未在核验器内约束，完全依赖外部 freeze pin

- **位置**：`scripts/release/verify.ts:464-473`（baseline 仅校验 `version` 为自由文本 + `source` + `files` 映射）、`:476-520`（coverage 50 条须与 PRD G 段逐条对齐）、`:577-586`（仅点名 `G-base.json`/`G-map-empty.json`/`G-behavior.json`/`E.5.json`/`cases.json` 五个必需文件）；`tests/unit/t11-release.test.ts:149` 才有 `expect(Object.keys(fixed.files)).toHaveLength(17)`——**该断言只在探针测试内，不在核验器内**。
- **触发**：freeze 中的 `baselineSha256` 被填为一份缩水基线（例如只含 6 个文件、缺 `content/learning/*.json`、缺 `alarms.csv`/`conventions.json`/`equipment*.csv`/`unclosed-high.rq`）。
- **影响**：核验器仍可能判定一致——即"approved-fixed-baseline-probe.json:16-34"列出的 17 文件全集与 `t09-readonly-alignment.json:8` 的 `filesVerified:17` **未被工具自身保证**；`docs/release/README.md:23` 表述为"17 文件核验"会让人误以为已内建该约束。
- **证据**：`approved-fixed-baseline-probe.json:16-34` 登记 17 个固定 SHA；本轮实测该 17 文件集合在探针路径上逐文件 hash 校验通过（探针内 `tests/unit/t11-release.test.ts:143-156`），但该逻辑不在 `verify.ts`。
- **建议**：在核验器内增加"基线文件数与必需路径集合"校验（并核对 `version` 为批准值），使其不再仅依赖外部 pin；或改写 README:23 表述，明确"17 文件全集由总控 freeze 的 baselineSha256 间接保证，工具不独立校验"。

### F-L【中】状态文档"失败原件保留"表述超出归档实际内容

- **位置**：`docs/reviews/T11/status.md:18`："失败原件与重跑日志保留本树 ignored 的 `*.log`……未把失败覆盖为通过。"
- **冲突/事实**：归档 48 份日志中**不存在**任何含 "38 failed" 的原始输出（实测全量 grep 无命中）；`unit-second-run.log` 记录的是**修复后**的 "38 passed"；`unit-third-run.log` 是 40 failed 的另一次失败；`check-first-run.log`/`check-second-run.log` 分别为 TS 声明缺失失败与 `.venv/bin/python ENOENT`（8 failed）。即**首跑 38 失败只有摘录与原会话 transcript**。
- **佐证披露是充分的**：`docs/reviews/T11/first-failure.json:12` 明确写"First-run excerpts and summary; full output retained in tool transcript, not represented here as full raw log"；`round-1/history-disposition.md:16` 写"无独立完整首跑 raw file，只有摘录/原会话 transcript，明确无法从归档完整重建首跑"；`round-1/raw-logs-index.json:254` 同样列为 limits。
- **影响**：status.md 作为"唯一状态来源"（AGENTS §6）会给出比归档更强的保证印象；不构成伪造（归档与三处披露均一致），属表述与证据不同步。
- **建议**：将 status.md:18 改为"首跑 38 失败仅有摘录与原会话 transcript，无独立完整 raw；其后各次失败（unit-third-run、check-first-run、check-second-run）原件已在归档内"。

### F-D【低】80% 分子口径：工具比用户研究文档更严，且不单列迁移成功率

- **位置**：`scripts/release/verify.ts:751-765`（`successes` 需 `coreCompleted && transferCompleted && assistance∈{independent,product-hints}`）vs `docs/release/user-study.md:19`（"依靠产品引导完成核心案例人数/总人数≥80%；5 人至少 4 人……**迁移成功另外统计**"）。
- **影响**：完成核心案例但迁移任务未完成者，在文档口径下计入分子、在工具口径下计入分母；工具未提供独立的迁移成功率指标，与"迁移成功另外统计"不符。方向为偏严（fail-closed），且内审处置 `round-1/history-disposition.md:11` 明确选择了"80% 计入者必须迁移完成"，说明这是 owner 的显式决定——但被接受的 `user-study.md:19` 文本未同步。
- **建议**：由 owner 统一口径（推荐在 user-study.md:19 写明分子含迁移完成，并补"工具不单列迁移成功率"）；或在工具中拆出两个指标。属文档/实现口径同步，不改变任何结论。

### F-E【低】固定输入联验的边界表述准确，但"实际启用探针"的口径应限定为命令级

- **位置**：`docs/iterations/T11/acceptance.md:22`（"本机最终检查实际启用探针"）与 `docs/reviews/T11/status.md:16`。
- **事实**：本轮实测 C7（显式探针 65/65 零 skip）与 C8（默认 62 passed / 3 skipped）与两处表述一致；固定对象 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` 在本树**可取**，17 文件逐文件 hash 在探针内校验通过，固定 manifest SHA `aaaef2c0…ac39e` 与 PRD SHA `7586b2c4…f60fbb` 与批准值一致。
- **影响**：仅为表述精度问题——"最终检查"应指具体命令而非工作树默认状态；无实质缺陷。
- **建议**：在 acceptance.md:22 注明"须以 `T11_FIXED_BASELINE_PROBE=1` 前缀显式执行，默认状态为 3 项 skip"（该句已部分存在，建议补"工作树默认状态"三字以免歧义）。

### F-F【低】回退与恢复的部分文档子项没有对应的强制 check id

- **位置**：`docs/release/migration-recovery.md:17` 要求"回退先停止写入并保留新版本数据副本"、"旧版不能读取新格式时应拒绝直接打开，只能恢复兼容备份"；`scripts/release/verify.ts:252-258` 的 `RECOVERY_CHECKS`（6 项）与 `:895-905` 的 `ROLLBACK_*` 检查 id 集合（`previous-source-version`/`previous-signature`/`rollback-format-compatible`/`rollback-install`）**均无对应条目**。
- **影响**：上述两条只能靠 expected/actual 载荷内容间接体现，工具不强制其存在；实为能力边界而非安全漏洞（工具本就不证明语义）。
- **建议**：如需强制，追加明确 check id（如 `rollback-refuse-new-format`、`rollback-retain-new-version-copy`）并补反例；否则在 migration-recovery.md:17 注明该两项由人工原件核验。

### F-G【低】真人研究的部分文档要求在 participant schema 中无字段承载

- **位置**：`docs/release/user-study.md:7`（观察/录屏须事先取得同意）、`:14`（须实际修复约束并区分断言/推导才计独立）、`:19`（记录完整示范完成数但不得混入独立指标）、`:21`（记录文件需保存每段/每次尝试细节，不能仅填总布尔）vs `scripts/release/verify.ts:75-98` 的 participant schema（无 consent、无逐段记录、无完整示范计数字段，仅一个 `record` 引用）。
- **影响**：工具只校验记录文件的路径与哈希，不解析内容，因此上述要求**无法由工具核验**；这与 `docs/release/README.md:29` 的能力边界一致，属已知边界而非新缺陷，但应显式登记，避免被当作工具已覆盖。
- **建议**：在 user-study.md:21 或 README:29 增列"同意、逐段记录、完整示范计数由观察记录原件与主持人核验，工具不解析"。

### F-H【低】两个 collector 的失败处理与绑定存在缺口（Windows collector 仅静态审阅）

- **位置**：`scripts/release/collect-macos.sh:3`（`set -euo pipefail`）、`:16`（`mkdir "$output_dir"`）、`:25-29`（codesign/spctl/stapler 均为外部命令，输出重定向到文件）；`scripts/release/collect-windows.ps1:15`（输出目录必须不存在）、`:37-47`（对 Installer/AppExe/EngineExe 独立取签名与 PE 信息）。
- **触发/影响**：①Mac：任一 `codesign --verify`/`spctl --assess`/`stapler validate` 返回非零即中止脚本（fail-fast 合理），但**已创建的输出目录会残留半份证据且不再可写入**（第 15 行要求目录必须不存在），无 trap 清理，重跑需另选目录；②Win：脚本**不校验 AppExe/EngineExe 来自所给 Installer**，三条输入彼此独立接受，安装包与被检可执行文件之间的来源绑定仅依赖上游报告；③Win 的 `Get-PeMachine` 未对 e_lfanew 做边界检查，异常 PE 会以流异常方式抛出（非受控错误码）。
- **证据**：均为静态审阅结论；Mac 仅 `bash -n` 语法证据，Windows 无批准执行环境，**两项均无运行证据**（本轮不获授权运行）。
- **建议**：Mac 增加失败路径的 trap 清理或明确"部分目录需人工清理"；Win 增加"AppExe/EngineExe 路径位于 Installer 解包根内"的显式断言与 e_lfanew 边界检查；修复后按原门禁在批准环境复验。

### F-I【低】安装包格式与签名真伪属结构/声明级校验

- **位置**：`scripts/release/verify.ts:333-357`（PE/koly 结构）、`:637-645`（签名/公证字段与 identity 关键字）、`:646-653`（签名报告一致性）。
- **事实**：工具不解析 Authenticode/Developer ID 签名、不验证证书链，签名"有效"取自 manifest 声明并与签名报告的 expected/actual 一致性绑定；PE/koly 校验为结构级，不判定是否真为 NSIS 安装器或可挂载 DMG。
- **影响**：不能因本工具 `consistent:true` 就推断签名链可信或资产可安装——与 `docs/release/README.md:29` 的声明一致，属能力边界。
- **建议**：在 README 的"核验的实际边界"节显式列出"不解析签名、不判定安装器实质格式"两条，避免下游误用。

### F-J【低】新鲜度判定依赖本地墙钟

- **位置**：`scripts/release/verify-release.mjs:20`（`now: new Date().toISOString()` 覆盖 freeze 中的 `now`）、`scripts/release/verify.ts:457-460`（`fresh()` 以 `frozen ≤ testedAt ≤ now` 判定）。
- **影响**：机器时钟偏移会误判过期/新鲜；不构成 pin 绕过（预期/候选/资产 pin 不受影响），属操作风险。
- **建议**：在 freeze 中额外记录受信时间源或允许 `now` 由受信参数传入并在报告中标注。

### F-K【低】流程文档存在并存的版本双值（多数已由文档自身标注为历史阶段）

- **位置**：`docs/reviews/T11/completion-audit.md:5`（"当前实现基线 ffa0972／核验器 8370444e"）vs `status.md:30`/`completion-audit.md:32`/`blocked-audit.json:53`/`recovery.json:7,20`（`7d28fdb`／`8f6aac79`）；`operating-policy-receipt.json:27-28`（`currentImplementationAndTestCommit`=`50a3212`、`verifierSha256`=`8370444e`）以"current"字样并存；`operating-policy-receipt.json:21`（goal active）vs `:67`（goalStatus blocked）vs `status.md:3`/`recovery.json:31`/`blocked-audit.json:4`（blocked）vs `completion-audit.md:30`（"Goal 保持 active"）；`blocked-audit.json:31-32` 与 `format-python-ownership-receipt.json:12-13` 对同一 `execution-state.json` 记录了不同 SHA（`0b41a993…` / `cf21df89…`）而 updatedAt 相同。
- **缓解情况**：`status.md:40`（"前文 active 均为历史阶段记录"）、`completion-audit.md:34`（"上文 active/进展分类属于历史轮次"）、`completion-audit.md:32`（"上表记录 50a3212 阶段，不当作当前候选未变的证明"）已显式消解时间顺序歧义。
- **影响**：不影响受审工程；仅降低状态文档的即时可读性，增加误读风险（尤其"current"字样出现在非当前段落）。
- **建议**：给每条状态回执加"生效时间/取代关系"字段，或把"当前"改为绝对时间戳表述。

---

## 8. 历史每项处置的关闭/重开依据

依据 `docs/reviews/T11/round-1/history-disposition.md`、`internal-review.md`、`selection-v2-review.md`、`first-failure.json`、`verification.json` 与本轮实测逐项复核：

| 历史项 | 原处置 | 本轮复核依据 | 本轮判定 |
| --- | --- | --- | --- |
| P1 expected/actual 数量自证 | 绑定 T09 完整 expected/E.5 + 独立 freeze 每项预期 hash | 核验器 `expectedResults` 外部 pin + `PRODUCT_EXPECTATION_BASELINE` 与基线完整 expected 比对；反例实测拒绝 | **保持关闭** |
| P1 空/任意等值恢复快照 | 身份/唯一 id/完整 payload + 外部 snapshot pin | `snapshotSchema` + `RECOVERY_SOURCE_PIN`；`recovery.json:27` 的旧"当前"提交号属流程记录瑕疵（F-K） | **保持关闭**（实现侧有效） |
| P1 冻结时间可回填 | 独立 freeze 固定时间 | `FREEZE_IDENTITY`/`FUTURE_FREEZE`/`${label}_STALE` 实测拒绝 | **保持关闭** |
| P1 文本/当前安装器冒充旧版 | PE/DMG 结构 + 独立旧资产 pin | `ROLLBACK_BINARY_FORMAT`/`ROLLBACK_IDENTITY_PIN` 实测拒绝 | **保持关闭** |
| P2 真人 core 与迁移完成矛盾 | 80% 计入者须迁移完成，区分口头/示范/Agent 代做 | 实现已按此强制；但与 `user-study.md:19` 文字口径未同步 | **保持关闭**（文档同步项转入 F-D） |
| E.5 引用新增回归 | exact/replay 真实展开 + 3 类拒绝 | 本轮 C7 实测通过，含缺指针/文件漂移/同数量错对象反例 | **保持关闭** |
| v2 P1 未选旧 undo 泄漏 | priorUndo 选择记录，未选必须空 | `superRefine` UNSELECTED_CONTENT + 泄漏反例 | **保持关闭** |
| v2 P2 零提交运行可重放误拒 | 不要求已有 rounds 非空 | 实现 `canReplay` 不以 rounds 为前提；`zero-commit-replay` 样例实测 consistent | **保持关闭** |
| 固定 873/SPO 新增续审 | 17 文件 hash、重复事实数保留、仅完整 SPO 无序 | 本轮 C7 实测 65/65 零 skip；17 文件逐文件 hash 通过；PRD 独立解析 57 P0/50 条目一致 | **保持关闭**（但工具未内建 17 文件约束 → F-C） |
| CLI 同名首跑 38 失败 | 更名 `verify-release.mjs`；**无独立完整首跑 raw** | 归档 48/48 完整核对，实测无含 "38 failed" 的日志 | **保持关闭且缺口确认**；表述不一致转入 F-L |
| 声明误删失败 | unit-third-run/check-first-run 保留 | 归档内确有 40 failed 与 TS 声明缺失原件 | **保持关闭** |
| Python 环境 ENOENT | check-second-run 保留，独立 uv sync --frozen 后重跑 | 归档内确有 ENOENT 原件；本轮 C10 用自有 `.venv` 实跑 1052 passed | **保持关闭** |
| v2 必需层口径（**本轮新发现**） | 文档称 v2 已解除"所有层非空"的过度强制 | 实现对 6 必需层**全局**强制 min(1) 并有专门反例 | **重新打开 → F-A（高）** |
| 端点/模型口径（**本轮新发现**） | — | `verify.ts:114-115` 字面量无 PRD/文档依据 | **新开 → F-B（中）** |

---

## 9. 父 T11 发布门状态（本轮不关闭任何一项）

依 `docs/reviews/T11/completion-audit.md:22-26`、`blocked-audit.json`、`recovery.json` 与本轮独立观察，下列**全部仍未完成**：完整 57 P0 与 C–G/10–12 同候选真实联验；正式 T01/T10 只读接口与整产品集成；Win11 x64 / macOS 15 arm64 真实安装、native、凭据、恢复、双向迁移；真实模型 API 版本化评估与零伪造；至少 5 真人 80% 及迁移辅助反例；批准 Q5 口径与测量；同候选 GLM-5.3/最高 + M3.1-Flash/xhigh 双审与意见处理（**本报告仅 M3.1-Flash 一方终态**）；门禁 push/PR 实际 CI、正常合并、远端核验；最终渠道与下载实装。核验器在任何输入下均返回 `releaseAuthorized:false`（已实测）。

---

## 10. 交付物与保全位置

- 本报告：`.t11-review-runtime/report/review.md`
- 实际任务/会话/设置读回：`.t11-review-runtime/metadata/review-session.json`
- 实际命令、环境范围、退出码与日志哈希：`.t11-review-runtime/metadata/commands-run.json`
- 原始日志（10 份，sha256 见 `commands-run.json`）：`.t11-review-runtime/raw/`
  - `t11-specialized-probe.log`（65/65 零 skip）、`t11-default-mode.log`（3 skip）、`full-check-with-probe.log`（npm run check exit 1）、`full-check-rest.log`（695 TS / 1052 Py / build / ruff 全过）、`release-explicit-checks.log`（显式 release lint/format、sources、bash -n）、`hash-verify-25product.log`、`hash-verify-8process.log`、`source-setup-drift-verify.log`、`raw-logs-archive-verify.log`
- 本轮 git 状态：` M AGENTS.md`（政策差异，保持未暂存）＋ 未跟踪 `.t11-review-runtime/`；**未 stage/commit/push/PR/切分支，未修改任何受审文件**。

---

## 11. 给总控的处置建议（非发布授权）

1. **F-A 必须在下一候选解决**：实现与 README:25 / history-disposition:8 的 v2 口径直接冲突，且专门反例把该冲突固化；建议由原唯一 owner 出新候选（文档或实现二选一，同步测试），并按原门禁重新走独立审查。
2. **F-B/F-C 建议同批处理**：端点/模型字面量须补授权来源或改为外部 pin；17 文件全集建议进入核验器或改写 README:23 表述。
3. **F-L 属表述更正**，不需要新证据即可修正 status.md:18。
4. 其余 F-D/E/F/F-G/H/I/J/K 为口径与边界登记类，建议在下一份状态回执中统一同步。
5. 本报告为 M3.1-Flash 一方终态，**不替代 GLM-5.3/最高一方**，**不关闭任何父 T11 门**；后续 push/发布按原门禁由总控调度。

---

## 12. 附录：本报告落盘后的工作树最终状态（自述完整性）

本报告与本轮元数据写入后，对工作树再次执行了与仓库同款的格式与 lint 门，结果如下（原始输出：`.t11-review-runtime/raw/prettier-final-state.log`、`eslint-final-state.log`）：

| 检查 | 退出码 | 结果 |
| --- | --- | --- |
| `npx prettier --check .` | **1** | 命中 **2 个文件，全部位于本轮自建 runtime 目录**：`.t11-review-runtime/metadata/setup.json`（owner 设置收据，字节未改）与 `.t11-review-runtime/report/review.md`（本报告自身）。**受审 25 条产品路径与全部仓库产品文件无一命中** |
| `npx eslint . --max-warnings 0` | **0** | 全仓无问题 |
| `git status --short` | — | 仅 ` M AGENTS.md`（政策差异，保持未暂存）＋ 未跟踪 `.t11-review-runtime/`；**无任何受审文件被修改，无 stage/commit/push** |

按本轮规则，上述两个文件**未被删除、未被 ignore、未被 exclude**，其存在与命中事实原样保留并在此登记；C9 的 `npm run check` exit 1 因此仍如实归因于**本轮自建 runtime 元数据与本报告自身**，不构成受审候选缺陷，也不得据此宣称"原完整检查通过"。

