# T11 round-1 ZCode GLM-5.3 独立只读审查报告（完整工程范围）

日期：2026-10-22（Asia/Shanghai）。审查者：ZCode（GLM-5.3 / 最高思考 / permission.mode=yolo，只读职责不因完全访问而扩大）。

## 0. 终态结论（先行）

**对完整离线发布证据核验工具工程范围（25 个 product 路径全部内容：verify.ts、verify-release.mjs、collect-macos.sh、collect-windows.ps1、t11-release.test.ts、两个 release fixture、docs/release 五件、docs/iterations/T11 三件、docs/reviews/T11 全部评审/来源/失败证据）：通过。**

通过的含义与边界：

- 通过仅指：冻结字节实现与固定验收 `docs/iterations/T11/acceptance.md`（product 版）一致；测试在本方独立环境复现（探针 65/65 零 skip、默认 62 通过 + 3 显式 skip）；既有证据披露与归档逐条核实为真；未发现新的阻断缺陷（P1–P3 为零，仅 6 项 P4 建议项）。
- 两 collector 的**目标平台运行行为**、以及一切真实发布证据（双 OS 真机安装/native/凭据/恢复/迁移、真实签名公证、模型 API、五真人、指定双审、push/PR/CI/合并/远端、最终渠道实装）为**无法验证**，按原验收完整保留，不因本通过关闭；Windows collector 仅静态审阅、Mac collector 仅 `bash -n` 语法证据，未移除任何验收项。
- `releaseAuthorized` 恒为 `false`；本报告的"通过"不构成发布授权，不关闭任何父 T11 发布门（57 P0、C–G、10–12、双 OS、模型、真人、CI、合并、远端、渠道门全部保留）。

## 1. 任务来源与设置读回

- 任务来源：用户在 ZCode 应用内提交的粘贴文本附件（322 行）+ 本方 UI 设置收据 `.t11-review-runtime/metadata/owner-task-settings.json`。按用户指示，权限以该收据为准，未读取全局配置或日志。
- 附件：`pasted-text-20261022-190833-b4662dbe.txt`，53740 bytes，SHA256 `1c044e9a98d984528b2a73a33940501bff64d074dfd9dc544e4ee7634d13c911`，实读全文（系统注入完整 322 行；`wc -l`=321 由末行无换行符解释，与收据 observedPastedLines=322 一致）。runtime 副本 `.t11-review-runtime/full-prompt.md` 哈希相同。
- 设置收据读回：role=zcode，model=**GLM-5.3**，effort=**最高**，permission=**完全访问（yolo）**，taskId=`session_31c8c641b36907791bdab363f7473a01`，submitted=true，attachmentBytes/SHA256 与实测一致。模型与本会话系统声明一致（account:bigmodel-individual-coding-plan/GLM-5.3）。思考等级与权限按收据如实登记；本会话自身无法从内部读回任务 ID，以收据为准（用户已明确该收据即证明）。
- 独立性：未读取任何 peer（MiniMax）本轮报告/状态/metadata；未扫描父 .worktrees 或总控队列；未向任何一方传递本轮意见。
- 操作边界遵守：未修改任何受审路径/测试/配置/依赖；未 stage/commit/push/PR；未切分支（checkout 保持 detached）；AGENTS.md 保持 ` M` 未暂存（工作树 SHA `de15f6ce…c8c4`，与 setup.json 期望一致；HEAD 内为 `1b3c0291…`）。仅读取冻结 Git 对象/文件/hash、解读既有日志，并在自己 runtime 写 raw/metadata/report。

## 2. 受审输入身份（全部核实）

| 项 | 值 | 核实 |
| --- | --- | --- |
| 实际 workspace | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T11-zcode-review-7d28fdb` | cwd 一致，detached |
| review HEAD | `b6e57a0534c94316dd07c3a87b4b8931d5a39501`（docs: prepare complete T11 offline-tool review inputs） | `git rev-parse HEAD` 一致 |
| product | `7d28fdb27c0aac39ed7df1f9fd5fa0f127b5d9f4`（fix: separate T11 restore and replay evidence） | 对象存在，25 路径核验 |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 对象存在，BASE..PRODUCT diff=25 路径 |
| process anchor | `9f12f17b74f1e26f310c8298232a7fe66cb026ad` | 对象存在，8 流程件在其上核验 |
| 固定 T09 输入 | `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380` | 对象存在；manifest SHA 实测 `aaaef2c0…c39e`、17 文件、PRD `7586b2c4…0fbb` 全部吻合 |
| 环境隔离 | 本树 `node_modules`（node v24.15.0/npm 11.12.1）与 `.venv`（uv 0.11.12）；安装日志 npm-ci.log/uv-sync.log 均 exit 0（setup 登记） | 未采用他树 env |
| TMPDIR/TMP/TEMP | `.t11-review-runtime/tmp` | 本轮全部测试/解包均在其下 |

- `git status`：仅 ` M AGENTS.md` 与 `?? .t11-review-runtime/`，与 source-setup.json 登记一致；822 受控文件中仅 AGENTS 为政策差异（mismatches=["AGENTS.md"]），无其他受控源码/验收漂移 → 未触发"停止并报告"条件。
- BASE..PRODUCT diff 恰为 25 个新增路径，与 `docs/reviews/T11/round-1/manifest.json` productFiles 完全一致；PRODUCT..HEAD 为 17 处流程变化（4 改 + 13 增，其中 9 份为 b6e57a05 的 round-1 准备件）。manifest 登记的 product 后 8 份流程变化在 process anchor 上逐字节核验（33/33 哈希全 OK，见 raw/001）。
- round-1 准备件（document-review.md、history-disposition.md、manifest.json、preparation-index.json、raw-logs-index.json、raw-logs.tar.gz、scope-registration.md、两份 prompt）按流程证据读取；其中 minimax prompt 仅作为流程输入确认范围等价性，未吸收任何对方意见（本轮不存在对方报告）。

## 3. 25 项 product 路径覆盖表（全部通读，非抽样）

| # | 路径 | productSHA256 核验 | 审查结论要点 |
| --- | --- | --- | --- |
| 1 | docs/iterations/T11/acceptance.md | OK e8e25919 | 验收与门禁定义清晰；探针/默认 skip、Windows 仅静态、显式 `--ignore-path /dev/null` 格式边界、后续完整关闭条件全部成文且与实现一致 |
| 2 | docs/iterations/T11/selection-comparison-v2.md | OK 03dd36b5 | v2 语义（三能力分判、选择携带、零提交重放）与 snapshotSchema superRefine 逐条对应 |
| 3 | docs/iterations/T11/shared-file-handoff.md（product 版） | OK fb5f2b9b | 共享文件交接提案边界清楚：不旁路唯一配置、不新建第二份 builder/lock/CI；当前版本（process d160bb0d）追加 T03/T01 责任路由，属流程而非验收变化 |
| 4 | docs/release/README.md | OK 0d738c72 | freeze 字段、exit 语义（evidence 一致=0，synthetic/不一致=1，读不了/格式错=2）、RDF 集合比较边界、"核验的实际边界"诚实声明均与代码一致 |
| 5 | docs/release/migration-recovery.md | OK 7177d924 | A/B 双向、t11-comparison-v2 必需层/可选层、三项能力判定条件、回退/升级边界与 MIGRATION/RECOVERY_CHECKS 一一对应 |
| 6 | docs/release/target-device-runbook.md | OK 29fda85e | 11 步真机规范；明确 collector 只收元数据不替代原生操作；不可用 CI/开发机抵扣目标机 |
| 7 | docs/release/user-observation-template.csv | OK c2229f58 | 空表结构含辅助级别/独立迁移/Agent 反例列，与 participant schema 对应；未预填 |
| 8 | docs/release/user-study.md | OK 9c77c08d | ≥5 真人/≥80%（5 人至少 4）、辅助五级编码、agentFullCounterexample/agentMarkedIndependent 语义与 verify.ts USER_* 检查一致 |
| 9 | docs/reviews/T11/approved-fixed-baseline-probe.json | OK 61423666 | 固定 873 输入许可、17 文件 SHA、65/65 零 skip、defaultMode 与 didNot 边界登记完整，与实测一致 |
| 10 | docs/reviews/T11/completion-audit.md（product 版） | OK f38a846b | 逐门未完成清单如实（当前 process 版 d8e16dbe 追加 blocked 阶段记录，未覆盖失败） |
| 11 | docs/reviews/T11/external-review-permissions-receipt.json | OK bd354b13 | 权限政策接收记录，只读边界保留 |
| 12 | docs/reviews/T11/first-failure.json | OK 2d6b63f5 | 首 38 失败摘要+摘录+诊断（同名 import），明确"完整输出在 transcript、非完整 raw log"，缺口如实 |
| 13 | docs/reviews/T11/internal-review.md | OK ab5f4815 | 内审 5 项 P1 处置与复核、41/41 与续审 45/45 记录；不替代指定双审 |
| 14 | docs/reviews/T11/operating-policy-receipt.json（product 版） | OK 9e36049f | 政策哈希匹配记录（当前 process 版 b94083ae 为追加） |
| 15 | docs/reviews/T11/selection-v2-review.md | OK dea7c2d6 | v2 内审（undo 泄漏/零提交误拒）+ 固定输入续审，核验器 SHA `8f6aac79…a6c06` 与 product 实测一致 |
| 16 | docs/reviews/T11/status.md（product 版） | OK c3a360b0 | 唯一状态来源；已实现/已验证/未完成分层清楚（当前 process 版 cc56d692 追加 blocked/责任路由） |
| 17 | docs/reviews/T11/t09-readonly-alignment.json | OK 038b9e85 | 只读对齐记录（17 文件/50 用例/3 指针），与实测一致 |
| 18 | docs/reviews/T11/verification.json | OK 0cb03592 | 65/695/1052/构建/ruff/sources/显式 lint+format/bash-n 登记；3 组失败保留；notExecuted 7 类如实；48 份日志 SHA 与归档互证 |
| 19 | scripts/release/collect-macos.sh | OK f273da7b | 见 §5 审查；只读、目标门禁、防覆盖、无敏感枚举；本轮 `bash -n` 通过 |
| 20 | scripts/release/collect-windows.ps1 | OK 9194c705 | 见 §5 审查；仅静态审阅（无批准 Windows 环境，维持验收） |
| 21 | scripts/release/verify-release.mjs | OK 184141eb | CLI：参数严格（≠5→exit2）、freeze 独立注入 now、synthetic 一致也 exit 1、错误固定文案不回显内容（测试覆盖） |
| 22 | scripts/release/verify.ts | OK 8f6aac79 | 见 §5 逐项审查；releaseAuthorized 恒 false（返回类型层面固化） |
| 23 | tests/fixtures/release/comparison.json | OK 615f14f8 | 合成 v2 快照（selection 含 agentSessions=false 等负例形状），仅供回归，明示非真实证据 |
| 24 | tests/fixtures/release/synthetic-profile.json | OK 654965c8 | 合成身份/时间窗，purpose 声明"never genuine … release evidence" |
| 25 | tests/unit/t11-release.test.ts | OK 504d23c2 | 65 用例（默认 62+3 skip）；正例/负例断言到具体错误码与语义（多重集、保序、能力分判、指针、CLI exit） |

## 4. 核验重点逐项结论（对应派发提示"核验重点"）

1. **严格 schema / 安全文件读取 / symlink 边界**：manifestSchema 及全部子 schema `.strict()`；`boundPath` 拒绝绝对路径/反斜杠/`.`/`..` 段，realpath 后以 `relative()` 判界（外部 symlink 解析后必出根 → UNSAFE_PATH），非常规/空/超限文件拒绝；大文件流式 8 GiB 上限内边读边哈希。测试实覆盖 `../outside.json`、symlink→/etc/hosts、多余键 `publish:true`、count-only payload。通过（P4-2/P4-6 建议见 §6）。
2. **候选/来源/受审/构建/报告/安装资产绑定**：source/candidate/reviewedSha 必须全等于 freeze 的 candidateSha；build.sourceSha、各 report 的 candidateSha/baselineSha256/artifactSha256 绑定（PRODUCT/MODEL/ENGINEERING/RECOVERY 的 artifactSha256 必须命中两实际资产之一；下载文件哈希必须等于候选包；回退资产禁止复用当前哈希）。负例测试覆盖（CANDIDATE_SHA、MODEL_BINDING、WIN_ARTIFACT、WIN_CHANNEL_HASH、ROLLBACK_IDENTITY_PIN 等）。通过。
3. **独立 freeze 的预期/时间/模型/旧资产 pin，防两边同填**：expectedSchema 由 CLI 从 TRUSTED_FREEZE.json 读取并强制覆盖 `now` 为当前时钟（无法用 freeze 回填时间）；冻结时刻、modelMode/returnedModel/serviceVersion/evaluationSha256、恢复/双迁移快照、previousAssets、逐 check expectedResults 全部 pin；testedAt 必须落在 [frozen, now]。工具层面成立。**边界**：freeze 文件本身的独立性（不由清单作者自填）是流程控制项，工具无法证明——README §核验的实际边界已如实声明，维持该边界。
4. **PE/DMG 结构及签名/公证/许可证/渠道拒绝边界**：DMG 检查 UDIF 'koly' 尾扇区；PE 检查 MZ→PE\0\0→machine(0x14c/0x8664)；签名 valid+timestamped+scheme+identity 非 adhoc/unsigned/none（正则）；Mac 另要求 hardenedRuntime/notarized/stapled；许可证 inventory 与 components 集合等价（排序比较）；下载 URL 必须 https、无凭据/query/hash、文件哈希=候选、installed=true、渠道报告三 check。负例全覆盖。通过（结构检查不等于签名链验证——文档已声明由负责人对照原生命令原件核验，维持）。
5. **57 P0、T09 manifest 全文件与 G 完整 expected / E.5 exact/replay 指针绑定**：PRD 正则提取 P0 必须恰 57 且唯一（本方运行通过隐含验证）；baseline source 哈希=PRD 哈希、逐文件哈希核验；coverage 50 条与 PRD G.1 表行/G.4 列表逐字符对应且 sourceSha256=PRD；cases 50 条 id 唯一、exactFile/exactPointer/replayExact* 从 baseline 文件展开（指针未解析→CASE_POINTER）；G-base/G-map-empty/G-behavior/E.5/cases 五件必须在列。负例（缺指针/漂移/错对象）覆盖。通过。
6. **RDF 完整 SPO 多重集合与其他数组保序**：`compareProductComplete` 仅对字段名 ∈ {facts,assertedFacts,inferred,addedTriples,inputs} 且**全部元素为 {subject,predicate,object} 三字符串键对象**的数组排序成多重集合比较（重复数保留）；其余数组（events/trace/rounds 等）严格保序；对象键序无关。单测覆盖重排通过、重复数不同拒绝、轮次倒序拒绝（固定 E.5 oracle）。通过。
7. **比较 v2 三能力分判与排除**：snapshotSchema superRefine——未选内容必须为空（UNSELECTED_CONTENT）；rerunOriginalMapping 严格等于 canRerun（原文件已选+存在+mappingSources=embedded）；replaySandbox 严格等于 canReplay（历史已选+存在+inputs+configuration+semantics=supported）；零提交（rounds 空）可重放不被误拒；restoreCurrent 字面 true；核心层非空 + 行唯一 id + 非空 payload 且拒绝 count-only。四种 packageProfile 正例 + 未选夹带/能力虚标/缺 ownership/v1 格式负例全覆盖。恢复前后、迁移前后全量 compareComplete。通过。
8. **至少 5 真人/80% 与迁移辅助区分**：users ≥5 唯一 id；human=true、developer=false、ontologyNovice=true、资产绑定、blockers 空；每人 agentFullCounterexample=true 且 agentMarkedIndependent=false；transferIndependent ⇒ transferCompleted 且 assistance∈{independent,product-hints}；成功=core+transfer+assistance∈{independent,product-hints}；比例 <0.8 拒绝。AI 用户/开发者/重复/旧证据/口头帮助计入/Agent 标独立负例全覆盖。与 user-study.md 口径一致（分母不删人、五级辅助、反例另开重置尝试）。通过（真人资格真实性仍属负责人独立核验边界）。
9. **CLI exit 与 synthetic 不得发布**：exit 0 仅当 consistent 且 mode='evidence'；synthetic 一致 → 1（测试实跑）；不一致 → 1；不可读/格式错/参数错 → 2；错误输出固定文案，不回显敏感内容（测试断言 stderr 不含原文）。`releaseAuthorized:false` 为返回类型字面量，代码层面不可能输出 true。通过。
10. **两 collector 的只读/目标/失败处理与已知未测项**：见 §5。通过（静态层面）；目标机运行=无法验证。

## 5. 实现文件审查细节

### 5.1 scripts/release/verify.ts（923 行）

- schema 层（L6–193）：全 `.strict()`；text≤512、sha/commit 正则、ISO datetime 带时区；artifacts/reviews/rollback/migration 恰 2、users 5–100、checks 1–512、components 1–1024；model endpoint/requestedModel 字面量 pin（DeepSeek）；download.url 用 z.url()。
- `boundPath`（L288–303）/`readBound`（L304–312）/`verifyLargeFile`（L313–331）：见 §4.1。
- `installerFormat`（L333–357）：DMG koly@size-512（size≥512 前置）；PE MZ→e_lfanew→'PE\0\0'→machine，offset≤size-6 防越界。结构判别正确。
- `canonical`/`compareComplete`（L359–371）：键排序、数组保序；同进程内比较，localeCompare 不构成跨机风险。
- `compareProductComplete`（L373–398）：见 §4.6。
- `verifyManifest`（L401–923）：identity 冻结（candidate/baseline/freeze/时间窗）；PRD 57 P0；baseline/coverage/cases 链条；`evidence()` 统一做绑定+时间窗+raw 哈希+覆盖+逐 check EXPECTATION_PIN+expected/actual 全量比较（多余 check 也必须被 pin）；artifact 矩阵/架构/版本/格式/构建输入；签名/公证/许可证/inventory；设备 24 check 与干净目标（node/python/docker 均必须未装）；渠道四重约束；DISTINCT_DEVICES；PRODUCT=57P0+50 固定用例且固定用例 expected 必须等于 T09 baseline 值（actual==expected==baseline 链）；MODEL pin+零伪造；双指定审查（GLM-5.3/highest、M3.1-Flash/xhigh、pass、unresolved=0、distinct taskId、资产绑定）；USER 规则；comparison-v2 snapshotSchema+superRefine；恢复源 pin+前后全等+回退独立 pin（禁当前资产、旧版签名/公证、四 check 报告）；双向迁移+源 pin+前后全等+22 check 报告绑定目标资产。
- 恒等返回 `releaseAuthorized:false`（L922）。

### 5.2 scripts/release/verify-release.mjs（29 行）

参数恰 3 个否则 exit 2；manifest/freeze 各限 16 MiB；`now` 强制取 CLI 当前时间（freeze 内 now 被覆盖，无法回填历史时刻做时间窗）；结果 JSON 输出；exit 语义如 §4.9；catch 固定文案 exit 2。

### 5.3 scripts/release/collect-macos.sh（31 行）

`set -euo pipefail`；必须 `--approved-isolated-session` 且恰 4 参（否则 exit 2）；目标门禁 uname -m=arm64 且 macOS 15.*（否则 exit 1）；APP/DMG 存在、输出目录必须不存在（防覆盖）；采集 sw_vers/arch/cpu+mem（避开序列号/主机名/用户名/Keychain 枚举，有注释）/DMG SHA/plist 版本/file 架构/codesign display+verify deep strict/spctl/xcrun stapler validate（只读）；关键工具 /usr/bin 绝对路径；scope.txt 明示"仅元数据，native/嵌套清单/证据审查另行为之"。任一步失败即非零退出（fail-closed）。本轮 `bash -n` 通过（raw/004）。

### 5.4 scripts/release/collect-windows.ps1（51 行，仅静态审阅）

Mandatory 开关+四参；`$ErrorActionPreference='Stop'`；OS 门禁（Caption 含 Windows 11 且 OSArchitecture=X64，throw TARGET_REQUIRED）；输出目录必须新建；输入必须为叶子文件；device.json 仅 OS/CPU 名称与位宽/总内存（无序列号/主机/用户）；Get-PeMachine 复核 MZ/PE 签名/machine；每个文件 Get-AuthenticodeSignature 必须 Valid 且带 TimeStamperCertificate（否则 SIGNATURE_INVALID）；app/engine 必须 0x8664（安装器允许 0x14c 的 32 位 NSIS stub，与 verify.ts 口径一致）；artifacts.json 记文件名/SHA/machine/状态/签名人/时间戳签名人/产品版本；scope.txt 明示 signtool /pa /all、安装、DPAPI 及全部 native 场景另行。无安装/启动/网络/写入产品行为。**静态审查通过；运行行为无法验证（无批准 Windows 环境，未降低验收）。**

### 5.5 tests/unit/t11-release.test.ts（947 行，65 用例）

fixture 于 mkdtemp 根内构造完整合成清单（文件写入+SHA 登记一体化）；fixedBaseline 分支只读 `git show 873:<path>` 并先验 manifest SHA/PRD SHA/17 文件再落临时根——不转读变化 HEAD、不加载 T09 服务/Store、不执行领域用例（与 acceptance.md L22-24 一致）。正例：完整清单、4 种 packageProfile、RDF 重排。负例 31 项 mutate + 场景例（未选夹带×6、能力虚标×2、指针×2、v1 格式、缺 ownership、渠道凭据、回退复用当前资产、FR 伪造、CLI synthetic/malformed 等），全部断言到具体错误码。CLI 测试断言 exit 1/2 与 stderr 不泄漏。质量符合"断言真实需求与错误边界"的项目约定。

## 6. 发现的问题（全部为 P4 建议项；P1–P3：无）

| # | 严重度 | 位置 | 触发 | 影响 | 证据 | 建议 |
| --- | --- | --- | --- | --- | --- | --- |
| F1 | P4 | `scripts/release/verify.ts:423` | expectedSchema 在 L415 已校验并提前返回，L422-424 再次 `safeParse` | 死代码；无功能影响 | 代码路径：L415-421 early return 保证 L423 恒真 | 未来候选删除重复校验 |
| F2 | P4 | `scripts/release/verify.ts:288-311` | boundPath statSync 与 readFileSync 之间存在 TOCTOU；符号链接/stat 后被换 | 理论上可绕过 16 MiB 上限读大文件或换指向；内容仍受 SHA256 pin 约束，离线本地工具风险极低 | 代码结构；verifyLargeFile 已用 openSync 后流式读取 | 可改为 openSync+fstat 后用同一 fd 读取 |
| F3 | P4 | `scripts/release/verify.ts:920` | `dest?.file.sha256` 可选链：若目标 artifact 缺失则该 evidence 跳过资产绑定 | 现实不可达（TARGET_MATRIX+MIGRATION_DIRECTIONS 先行 fail），仅防御性缺口 | 代码；负例未覆盖该分支 | 改为显式 fail 而非静默跳过绑定 |
| F4 | P4 | `scripts/release/collect-macos.sh:17-18,20` | sw_vers/uname/sysctl/mkdir/xcrun 未用绝对路径（其余 /usr/bin 均绝对） | PATH 投放理论上可替换采集工具；运行于负责人批准隔离会话，风险低 | 逐行比对 | 统一绝对路径（xcrun 需 PATH 的场景可显式 xcrun --find 记录） |
| F5 | P4 | `scripts/release/collect-windows.ps1:25-35` | Get-PeMachine 未先校验 e_lfanew 偏移在文件界内即 seek+read | 越界读取抛 EndOfStream → 脚本终止（fail-closed，不产生错误"通过"） | 静态阅读 | 读取前校验 offset+6≤length |
| F6 | P4 | `scripts/release/collect-macos.sh:16` / `collect-windows.ps1:19` | 输出目录先建，后续步骤失败时留下不完整目录 | 消费方若不核对退出码可能误读半成品证据 | 脚本结构 | runbook 已要求绑定 candidate/asset 后再纳入清单；可在 scope.txt 之外加显式完成标记文件 |

以上均不构成对冻结验收的阻断；按冻结规则，任何采纳须由原 owner 另做新候选并按原门禁重审，本轮不自行修复。

## 7. 本轮实际运行的检查（命令、cwd、环境、exit、日志）

cwd 均为本 worktree 根；TMPDIR/TMP/TEMP 均指向 `.t11-review-runtime/tmp`；除列明项外无其他环境覆盖（010/010b 另设 GIT_DIR 指向临时空仓库以模拟缺对象）。

| 编号 | 命令 | 结果 | raw 日志（SHA256 前 8 位） |
| --- | --- | --- | --- |
| 001 | python3 冻结哈希核验（git show PRODUCT/PROCESS×33） | 33/33 OK，0 fail | 001-frozen-hash-verify.log d57b916b |
| 002 | tar 展开归档+逐条 SHA/字节核验 | 归档 SHA `c1f34bd3…e99b5` 吻合；48/48 条目 OK；总计 73704 bytes 与登记一致；无多余文件 | 002-rawlogs-tar-verify.log b4cc9989 |
| 003 | git show 873:…manifest.json + 哈希/计数 | SHA `aaaef2c0…ac39e`、17 文件、PRD `7586b2c4…0fbb` 全吻合 | 003-t09-manifest-direct.log bc8a7cc4 |
| 004 | bash -n scripts/release/collect-macos.sh | exit 0 | 004-bash-n-mac-collector.log ece12353 |
| 005 | T11_FIXED_BASELINE_PROBE=1 npx vitest run tests/unit/t11-release.test.ts | **65 passed / 0 skipped，exit 0** | 005-probe-specialized-test.log 658e8555 |
| 006 | npx vitest run tests/unit/t11-release.test.ts（默认） | **62 passed + 3 skipped，exit 0**（默认通过≠固定输入联验） | 006-default-specialized-test.log 04879c74 |
| 007 | npx eslint --no-ignore scripts/release/verify.ts scripts/release/verify-release.mjs | exit 0，无输出 | 007-explicit-release-lint.log bb7b8cf0 |
| 008 | npx prettier --ignore-path /dev/null --check <7 类 release/iteration 文件> | exit 0，All matched | 008-explicit-release-format.log 99d71334 |
| 009 | shasum 工作树 PRD（并对比 HEAD） | 均 `7586b2c4…0fbb`，与 T09 pin 一致 | 009-prd-hash.log a6de6105 |
| 010/010b | GIT_DIR=<空仓库> T11_FIXED_BASELINE_PROBE=1 npx vitest run …（缺 873 对象反证） | **3 个探针用例失败（git show 显式报错）/62 通过，vitest exit=1** → 证明缺对象显式失败、无 live HEAD 回退 | 010 系列 32dd072e / 5ed8c13d |

另注：010 首次记录的 "EXIT=0" 为本人管道写法误差（记录的是 tail 退出码），已在 010b 用准确捕获更正为 vitest exit=1；两者测试结果一致。

**未重跑项及依据**：`npm run check` 全链与 `verify:sources` 未重跑——25 路径及 PRD 冻结字节与既有证据记录时完全一致（受控 822 文件无漂移、实现六文件 SHA 与 verification.json reviewedFilesSha256 相同），按检查边界"无变化历史不机械全部重跑"，沿用归档 `fixed-baseline-full-check.log`（SHA cce3b1f5…，在 48 条目归档内核验，内容含 lint/format:check/typecheck×3/vitest 695/构建/ruff+format/pytest 1052 全链通过）与 `sources.log`（12 归档源）。静态证据不以运行证据冒充：本节运行项即本轮新增运行证据。

## 8. 历史报告与失败处置逐项核对（history-disposition.md 12 项）

| 历史项 | 本轮复核结论 |
| --- | --- |
| P1 expected/actual 数量自证 | 已关闭：EXPECTATION_PIN 逐 check pin + PRODUCT 固定用例必须等于 baseline 值 + count-only/FR 伪造负例（L895-896、L921-928 测试）仍在 |
| P1 空/任意等值恢复快照 | 已关闭：snapshotSchema 必需层/唯一 id/非空 payload/执行版本 + RECOVERY_SOURCE_PIN；任意行、空快照负例在 |
| P1 冻结时间回填 | 已关闭：FREEZE_IDENTITY/FUTURE_FREEZE/fresh 时间窗 + CLI 强制 now；伪造 2020 冻结负例在 |
| P1 文本/当前资产冒充旧版 | 已关闭：PE/DMG 结构 + previousAssets 独立 pin + 禁当前哈希 + 旧版签名/公证；'not an installer' 与当前资产回退负例在 |
| P2 真人 core/迁移矛盾 | 已关闭：USER_ASSISTANCE/USER_COMPLETION_RATE 规则与负例（口头帮助、Agent 标独立、缺反例）在 |
| E.5 引用新增回归 | 在案：exact/replay 展开、缺指针/漂移/错对象负例；45 计数为历史，当前 65 |
| v2 P1 未选旧 undo 泄漏 | 已关闭：priorUndo 选择 + 未选必空（superRefine）+ 六类未选夹带负例 |
| v2 P2 零提交误拒 | 已关闭：canReplay 不依赖 rounds 非空（仅历史+输入+配置+语义）；zero-commit-replay 正例在 |
| 固定 873/SPO 续审 | 在案并本轮独立复现（005/010b）；"actual 仍 oracle 构造"边界如实 |
| CLI 同名首 38 失败 | 处置正确：first-failure.json 摘录 + 诊断（更名 verify-release.mjs）；**完整首跑 raw 永久缺失**，归档不补造（raw-logs-index limits 明示）——缺口保留，不视为已补 |
| 声明误删失败 | 保留：unit-third-run/check-first-run 原件在归档（13471/2260 bytes 核验） |
| Python 环境 ENOENT | 保留：check-second-run（22864 bytes）在归档；独立 uv sync --frozen 后通过，不当产品错误 |

父级缺口（完整 P0 同候选、正式接口、双 OS 真机、签名渠道、模型 API、五真人、双指定审查、CI/合并/远端、下载实装）在 completion-audit/blocked-audit/recovery.json/notExecuted 中一致登记，**本轮不关闭任何一项**。

## 9. 无法验证边界（不假设通过、不移除验收）

1. Windows collector 运行行为（无批准 Windows 执行环境；仅静态审阅）。
2. Mac collector 目标机行为（仅 bash -n；无真机 codesign/spctl/stapler 实际输出、无安装结果）。
3. 真实签名/公证/时间戳链、双 OS 安装/native/凭据/恢复/双向迁移、真实模型 API 评估、五真人研究、指定双模型审查（含 MiniMax 方）、push/PR/实际 CI/合并/远端核验、最终渠道下载实装——全部未执行，维持原门。
4. 首轮 38 失败的独立完整 raw 文件不存在（仅摘要/摘录/transcript 线索），永久缺口如实保留。
5. 工具固有边界：不能证明操作者/签名人/真人资格或原始报告真实性，不能证明 TRUSTED_FREEZE 与清单作者的独立性（流程控制），不能以 "consistent" 作为发布授权——README/acceptance 已声明，本报告维持该口径。
6. 本报告为指定双审中 ZCode 一方；对完整父级发布的 verdict 属总控后续合成，不在此越权给出。

## 10. 结论重述

- **完整工程范围（离线证据核验工具全部 25 路径）：通过。** 无 P1–P3 新发现；6 项 P4 建议供未来候选；既有披露经逐条核验为准确；本方环境独立复现探针 65/65、默认 62+3skip、缺对象显式失败、显式 lint/format、bash -n、T09/PRD/归档哈希。
- **子项"无法验证"清单见 §9**（尤其两 collector 目标机运行），这些不因工程审通过而关闭，父 T11 全部发布门保留，`releaseAuthorized:false`。
- 本轮零修改受审路径、零 stage/commit/push；raw/metadata/report 全部在自己 runtime 目录。

## 附：报告与证据位置

- 本报告：`.t11-review-runtime/report/review.md`
- raw 日志 13 份（含 setup 两份安装日志）：`.t11-review-runtime/raw/`（哈希见 §7 与 metadata/review-run-summary.json）
- 设置读回与运行登记：`.t11-review-runtime/metadata/`
