# T10-S1 round-1 外审报告（ZCode / GLM-5.3 / 最高推理）

- 报告性质：一轮完整、独立、只读的代码与证据审查。审查对象为已登记有界阶段 `T10-S1 私有包检查与安全报告文件服务`（含 T-A/T-B/T-C 工具与保全证据），不是完整 T10 Goal 的验收，不创建 Goal、不修改候选、不 push/PR/CI/合并。
- 审查执行树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-zcode-review-c3c7e90`（detached HEAD `77f2d5048630827ba5220fe092392ded6ab1c697`）。本模型会话内未见外部实际任务 ID 或可回读定位（如实声明，不作猜测）；权限模式未在会话内回读，只读职责不依赖权限模式。
- 唯一报告写入本文件；验证原始输出在 `docs/reviews/T10/round-1/zcode-raw/`；独立反例/脚本/派生构建在 `out/t10-review/round-1/zcode/`（scratch）。未读取另一方（MiniMax）本轮任何输出。

## 1. 核验的身份与固定输入

| 项 | 声明 | 核验结果 |
| --- | --- | --- |
| 批准 base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | Git 对象存在（I04 合并点），与全部身份链一致 |
| 产品实现 D→C | `d3546af3…` → `c3c7e90f…` | 存在；base→C delta 共 27 文件，全部位于授权写面（transfer/、project-transfer/、renderer/transfer/、T10 tests/fixtures/docs），未触公共契约、Store、writer、main/index、preload、App、锁、CI |
| 工具/证据点 N | `66eeedd735370576b49eb39cd4b14cdef9c0d55b` | 存在；66→A→HEAD 仅文档/证据/流程追加 |
| 固定输入 A | `a1e7efef4bd47c97b630753c0e7c4dc34de1d8ae` | `external-review-input-manifest.json` 147 项（141 delta + 6 上下文）逐项与 A 的 Git blob SHA256 比对：147/147 全部一致（raw: `zcode-raw/manifest-verification.txt`） |
| 当前执行树 77 vs 产品 C | 源码/tests/fixture/锁/CI 零差异 | `git diff c3c7e90 77f2d50 -- apps packages tests scripts package.json package-lock.json uv.lock .github` 为空；77 仅追加流程材料。工作树与 A 的差异仅 `docs/reviews/T10/status.md`（后续流程更新，预期内） |
| AGENTS 保护 | SHA `de15f6ce…c8c4` | 实测一致；保持未暂存、未提交；本次审查未改写 |
| 内审冻结哈希 | inspection `c64ea0f0…`、report `b5e50810…`、prepared-report-file `71e7359e…`、t10-report-file.test `7d0f4253…`、malicious-texts `b1b41d90…`、render-probe `dcccc5b9…` | 全部与当前文件实测一致 |

## 2. 实际读过与运行过的内容

**通读**（代码逐行）：`inspection.py`、`transfer/__init__.py`、`report.ts`、`TransferPanel.tsx`、`prepared-report-file.ts`、`test_transfer_inspection.py`（60 项）、`t10-report.test.ts`（18 项）、`t10-report-file.test.ts`（43 项）、三个 fixture、`csp.ts`、`render-probe.mjs`、隔离六工具（Dockerfile/run.sh/run-container.py/native-driver.mjs/native-hook.cjs/prepare-native.mjs）。
**通读**（文档/证据）：private-stage-candidate、status、verification、internal-review、report-file-internal-review、isolated-native-review、trusted-contract-review 概要、evidence-preservation-E1、designated-review-backlog、blocked-audit、private-preparation、report-file-publication、isolated-native-validation、interface-needs、verification-summary/browser-summary/check-failure-notes、PRD FR-104/FR-1000/FR-1001、12.4/12.5、A-06–08、G.6。
**哈希核验**：147 项输入 manifest；55 项 native manifest（55/55）；legacy 归档 40 项（40/40，index 内 11 项 requiredSummaryRaw 亦一致）；postrun 读回 3 份 cjs（3/3）；两份实物（native 3896B/`ad367a…`、browser 3900B/`26af12…`）实测与各回执一致；两项旧 snapshot 缺失如实登记。
**运行**（本树独立 env，缓存指向自己 scratch）：
1. `npm run check` 全量：**exit 0，一次通过** — lint、format、双端+unit 类型、vitest **691/691**（17 文件）、构建、ruff、pytest **1112/1112**（raw: `zcode-raw/check-full.txt`）。历史 engine-connection-state TIMEOUT **本轮未复现**，与"原因未证实"的记录一致。
2. 定向：`pytest test_transfer_inspection.py` **60 passed**；`vitest t10-report + t10-report-file` **61 passed（18+43）**。与登记数字完全一致。
3. 独立反例（scratch，脚本与输出均在 raw/scratch 留档）：ZIP 检查器 21 个自制用例 + 报告字节复算（见 §4/§5）。

## 3. 逐项审查结论

### S1-A Python 只读 ZIP 信封检查 — 通过（限登记范围）

- 严格性：draft 版本字面量精确匹配（`FORMAT_UNSUPPORTED` 不做任何隐式迁移）；manifest 严格键集、重复键拒绝、NaN/Infinity 拒绝、深嵌套 RecursionError 收敛为固定码；角色封闭集合，vault/credentials/audit/authorization/unknown 全拒（测试覆盖）；每角色至多一个成员、每路径唯一。
- 布局反隐藏：EOCD 必须位于文件尾且 `offset+size==len-22`（无尾随字节/注释/ZIP64/多磁盘）；本地 header 从偏移 0 连续铺到中央目录，本地/中央 flags、compression、CRC、packed/unpacked、文件名逐项一致，extra 必须为零，仅允许 0x800 位（拒加密与流式 data descriptor）。中央目录独占 `[offset, len-22)`。**不存在可藏字节的缝隙**。
- 解压安全：raw-deflate `decompressobj` 带界输出、`eof/unused_data/unconsumed_tail` 全查（拒压缩尾随与截断输出）；STORED/DEFLATED only；逐成员 CRC+长度+SHA256 核验；预算 40MiB/32MiB/8MiB/64KiB/256 项且在文档中明确"非容量承诺"。
- 语义克制：`import_allowed/restore_current/rerun_mapping/replay_runs` 恒 false、reason 固定；不凭角色/hash 推断 checkpoint 语义；无解包、无路径、无 DB、无 import/restore/rerun/replay 入口。`full` 必含四核心角色（含断言+所有权，方向与 FR-1000 "缺当前断言/所有权只能标模板"一致）；未选可选内容出现即 `UNSELECTED_CONTENT`；"选择≠包含"分开返回；完整包缺可选数据不降模板（`test_full_without_optional…`）。
- 我的独立反例（非套件用例）：手造合法 STORED/DEFLATED 归档作为对照组通过；隐藏 deflate 尾随流、截断到声明前缀、中央区垃圾、81 字符名、大写扩展名、BOM manifest、大写 hash、记录内重复键等全部以正确固定码拒绝（raw: `counterexamples-zip*.txt`）。未发现绕过。

### S1-B 安全 HTML 报告与未接线页面 — 通过（限登记范围）

- FR-1001 栏目齐全（目标/能力问题/逐 attempt 学习/本体/数据/查询/验证/行为/场景/假设/待解决），结果显式绑定 inputRevision/semanticsVersion/scope 与 当前/过期/历史/失败/取消 状态；`current` 必须与 projectRevision 一致、inputRevision 不得超前（superRefine）；通过却无 evidenceRef 拒绝。
- 学习分类（FR-104）：五级标签，未完成或检查未过=尚未验证完成；完整辅助/完整示范不计独立；任何部分提示/辅助不计独立；点击完成≠掌握。旧尝试不被新尝试覆盖（独立渲染）。
- 编码与离线：所有动态串仅进入 HTML 文本位置并经 `escapeReportText`；CSP 复用 `csp.ts` 唯一源（生产无 unsafe-inline/eval，connect-src/object-src/base-uri/frame-src/form-action 均 none）；无脚本/样式/链接/图片/字体；12 攻击文本 + 中文引号/实体/前导 LF（`<pre><span>`）在单测与浏览器实物中一致。zod strict 拒绝 apiKey/password/token/vault/audit/agentSessions/sendAuthorization 等一切额外键。
- 防御：`checkBudget` 节点/字符/数组/键数预算，拒绝 getter（自有/继承）、稀疏数组、异常原型、循环引用，且实测未执行 getter；错误统一 `REPORT_PROJECTION_INVALID`，无源值/诊断泄漏。
- 页面：独立未接线，4 选项默认未选、导出/导入禁用、三项能力明确"未验证"、无效投影 1 alert；无 Node/innerHTML/通用 IPC。合成输入未被声称为可信 Store/T09/T08 联验或凭据排除——声明与事实相符。

### S1-C 主进程不可变报告文件服务 — 通过（限登记范围）

- 构造期渲染一次并冻结 payload/hash/长度（Object.freeze）；后续源对象变异不影响产物（测试实证）。
- 选择校验：strict schema + 绝对目录 + NUL 拒绝 + `.html` 后缀 + 非法字符/控制字符 + Windows 保留名 + 相对目录/额外键拒绝；picker 适配器保持在受信主进程侧，无 renderer/模型路径入口；未接线任何真实 IPC/Store/picker（文档如实声明）。
- 暂存与发布：目标父目录 `mkdtemp` + `wx+`/0600 独占句柄；写+fsync；发布前经保留句柄有界读回**全字节+长度+路径身份**（同 inode 同长度改写、替换为 symlink、增长/截断均拒）；同文件系统 hard link 原子发布，EEXIST 即 `REPORT_TARGET_EXISTS`，不覆盖既有文件/目录/最终符号链接，竞争写者胜出时保留对方内容。
- 发布后语义：link 成功立即固定 published；其后回调错误（含伪造 EEXIST）、中止、目录 fsync 失败均不倒退为失败/取消（postPublicationError/durability 单列）；link 回执丢失（EIO 注入）以自己临时 inode 读回裁决，读不回进入 publication-unconfirmed 并阻止再次保存，`reconcilePublication` 显式读回后才定 published/not-present，"当前未观察到"≠"从未提交"。
- 清理：仅删自己身份绑定的暂存文件与空目录，非递归、未知文件保留并 pending；单飞 retryCleanup；pending 期间拒绝新暂存（`REPORT_CLEANUP_PENDING`）；并发保存 `REPORT_EXPORT_BUSY`（同步检查，无可竞争窗口）。错误码封闭，`errno()` 用描述符读 code 不执行访问器（测试实证未触发 getter）。
- 边界如实：无 I06 动态私有根 guard/可信投影/正式桥接；不阻止同 UID 外部持续篡改；无跨进程提交日志/启动清扫器（文档明示）。

### T-A render-probe / T-B 隔离 native 工具 / T-C 保全证据 — 通过（限工具与证据范围）

- T-A：CLI-only，经 TypeScript transpile 动态 import，不启动 Electron/浏览器；我在 scratch 复刻其编译路径（输出指向自己 scratch，未覆盖旧原件），产物与归档 HTML 逐字节一致（见 §5）。
- T-B：Dockerfile 摘要钉扎、非 root 1110、chrome-sandbox 0:4755、构建联网/runtime `--network none`（已公开区分）；run-container.py 对 create 后未启动容器做硬配置断言并从其中复制 controls 逐 hash 比对当前受审文件；driver 5 秒命令超时+55 秒总 deadline+只杀自己进程组；native-hook 硬断言 NoNewPrivs=1/Seccomp=2/CapEff=0/sandbox/contextIsolation/nodeIntegration=false/hang-monitor 开/mock-keychain 关/inspector 已关，真实 GTK `showSaveDialog` 保存(Alt+s)/取消(Escape)、picker 未被改写、nativeDialogs=2。额外 `SYS_ADMIN` 与短时 main loopback inspector（picker 前关闭）如实公开，未美化为最小权限/无 listener。
- 三次 attempt 原件一致：attempt1 `Status=created/StartedAt=0`（按 addendum 澄清解读为"已创建、启动前 CAP 名称检查失败"，非一次 native 运行）；attempt2 `T10_NATIVE_DEADLINE`（Return 键无回执）；attempt3 容器 exit 0、61TS/60Py、3896B/0600/`ad367a…` 与服务回执一致。失败原件均保留、未改记通过。
- T-C：postrun 三份 cjs 明确标注"停止容器事后读回、非运行时独立输出 hash"；Git 副本权限不冒充原运行 0600；旧 browser（3900B/26af）与 native（3896B/ad367）两实物两运行，未混同；两项旧 snapshot missing 如实记录。

## 4. 独立反例与复算结果（摘要，全文见 zcode-raw）

ZIP（round1/2/3）：
- 手造含 manifest 的合法归档（STORED、DEFLATED 对照组）→ 接受；
- 声明压缩大小内藏第二 deflate 流（尾随私有数据）→ `ARCHIVE_INVALID`；
- 解压实际输出超过声明 usize 前缀 → `ARCHIVE_INVALID`；
- 中央区垃圾字节 → `UNSAFE_ENTRY`；81 字符名/大写扩展名/BOM/大写 hash/记录重复键 → 各自固定码拒绝；
- 预算：>32MiB 总量拒绝；EOCD count 谎报（见问题 O-1）接受但无隐藏字节风险。
- 首轮反例中若干用例因我构造偏差被拒（字段偏移写错、双层压缩、多余成员），行为均正确；已修正构造后复测，结论以上述为准。

报告字节复算（跨环境决定性验证）：
- 以当前冻结源码+fixture 在本机（macOS/Node 24.15.0）按 native-hook 真实输入（仅 `goals=attacks`）渲染 → **3896 字节 / `ad367a…`，与 attempt-3 容器产物逐字节一致**；
- 按 render-probe 输入（`goals=attacks`+`title=attacks[0]`）渲染 → **3900 字节 / `26af12…`，与归档 browser 实物逐字节一致**。两实物差异完全由输入差异解释，无未声明变量。

## 5. 问题清单

**未发现 P0/P1/P2 级证实缺陷。** 以下为 P3 观察项/建议（均不阻断本阶段，属未来 owner 取舍）：

| # | 级别 | 位置 | 触发与影响 | 建议 |
| --- | --- | --- | --- | --- |
| O-1 | P3 建议 | `packages/engine/src/ontolearn_engine/transfer/inspection.py:94-99`（EOCD 解析）与 `:151`（条目计数） | EOCD `count` 字段与实际中央条目数不一致时仍被接受（我实测 count 谎报通过）。因 `offset+size==len-22` 与本地布局连续性已使全部字节可核算，**无隐藏内容风险**，仅声明字段完整性未交叉核验 | 在 `_inspect` 增加 `len(entries) == preflight count` 校验，收紧信封卫生 |
| O-2 | P3 观察 | `inspection.py:176`、`:196` | `template` 允许零角色空清单（实测接受），也允许含全部核心角色。FR-1000 只约束"缺断言/所有权不得标 full"这一方向，现行实现与 PRD 方向一致；反向与最小内容属未来正式格式决定 | 正式 schema 定稿时决定 template 的最小角色集与反向误标规则 |
| O-3 | P3 观察 | `inspection.py:187`（`DUPLICATE_ROLE`） | 每角色至多一个成员、单成员 ≤8MiB、总量 ≤32MiB：属草案级规模约束（已声明非容量承诺） | 正式格式阶段重新评估多成员/分片需求 |
| O-4 | P3 观察 | `apps/desktop/src/main/project-transfer/prepared-report-file.ts:182-187` | 非处于 `unconfirmed` 相位时调用 `reconcilePublication()` 返回字符串 `'unconfirmed'`，易与真实未确认态混淆（纯 API 语义瑕疵，测试未触达） | 非 unconfirmed 相位时抛固定错误或返回显式状态 |
| O-5 | P3 观察（已知边界） | `prepared-report-file.ts:257`（暂存目录建于目标父目录） | 进程崩溃后 `.ontolearn-report-*` 目录残留，无启动清扫器；文档已如实声明，正式接线时由应用生命周期验收覆盖 | 正式集成时补崩溃残留清理与生命周期联验 |

历史遗留（已有处置、无需新动作）：engine-connection-state TIMEOUT 原因未证实、原件保留，本轮未复现（691/691 一次通过）；attempt1/2 失败原件保留且不作为现行候选；旧 snapshot 两项 missing 保留不伪造。

## 6. 承诺准确性抽查（文档 vs 实现/证据）

- "60 Py / 18 报告 TS / 43 文件服务 TS / 整仓 691 TS / 1112 Py" — 本轮独立复测全部一致。
- verification-summary 的 `formalIntegration/approvedFormat/dualPlatform/credentialExclusionEndToEnd/dualSpecifiedReview/pushed` 全为 false — 与仓库事实（未接线、未 push、无 PR/CI/合并）一致。
- 引擎能力仅 `health`（native.json capabilities）— 与 AGENTS 状态快照一致，未夸大为正式迁移/包内引擎能力。
- 两份内审（2 P2 + 3 P2）修复声明 — 冻结哈希与现行源码一致，修复点（本地布局覆盖、getter 防护、staged 字节核验、pending 语义、post-link EEXIST）均能在代码与测试中定位到对应实现与反例。
- D1/D2 流程文档中的旧路径/旧"仅报告可写"条款已按本轮 addendum 替代执行；原 packet 字节保留未改，无追溯问题。

## 7. 未验边界与未满足的父 T10 门（不因本报告关闭）

正式包格式/schema 与完整 checkpoint（owner 未批准）；可信且排除 vault/凭据/发送授权的业务投影（T09/T08）；唯一 writer 原子导入与 receipt；真实学习/重放语义与跨设备续编辑/查询/重跑冲突/撤销；共享代次/项目/窗口接线与真实 App 内 main picker + 触发的 e2e；FR-1000 全量迁移验收；A-06 端到端凭据排除（本阶段仅信封级角色拒绝+严格 schema，明确不证明业务文本无凭据）；G.6 全部条目；12.4/12.5 双平台与包内验证；真人验收；全部 57 P0 与父功能门；指定双审另一方（MiniMax M3.1-Flash/xhigh）同版完整独立审查；push/PR/实际 CI/develop 合并/远端核验。本阶段通过不扩展为上述任何一项。

## 8. 最终结论

**明确通过本阶段**（T10-S1 私有包检查与安全报告文件服务，含登记的 T-A/T-B/T-C 工具与保全证据，固定于 candidate `a1e7efef`、产品实现 `c3c7e90f`、工具 `66eeedd`、base `5f910b52`）：

- 11 项产品/测试/fixture delta 逐行审读，未发现 P0/P1/P2 缺陷；5 项 P3 观察均已列出并给建议。
- 全量 `npm run check` 与定向复测在本隔离树独立复现登记结果（691/1112/60/18/43，exit 0）。
- 两份历史实物（3900B browser、3896B native）在本机从冻结源码逐字节独立复算成功，跨环境决定性与证据链完整性得到独立确认。
- 147/55/40/11/3 项哈希核验全部通过；失败原件、missing 项、超时历史均如实保留。

通过范围严格限于上述有界阶段；完整 T10 Goal 及全部父门仍未满足、继续有效。
