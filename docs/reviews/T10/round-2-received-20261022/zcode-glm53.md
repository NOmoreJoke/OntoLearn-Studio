# T10-S1 round-2 外审报告（ZCode / GLM-5.3 / 最高推理）

- 报告性质：round-2 全新完整独立、只读审查（本会话不复用 round-1 对话，未读取、未接收、未展示另一方本轮任何报告/摘要/结论/问题清单；本轮 round-2 目录中也不存在另一方内容）。审查对象为固定候选 `66cc15200611d592d3da2877961f9e079eb05277` 的全部 T10-S1 登记 范围（11 个产品/测试/fixture 作者路径 + 7 个工具 + S1-A/B/C、T-A/B/C 全部验收与历史证据），不是只审 EOCD 增量，也不是完整 T10 Goal 的验收。不创建 Goal、不修改受审实现/测试/依赖/配置、不做任何 Git 写操作。
- 审查执行树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-zcode-review-r2-66cc152`（detached HEAD `66cc15200611d592d3da2877961f9e079eb05277`，与本轮候选同一提交）。权限模式为已授权默认完全访问；完全访问不改变只读职责。
- 本模型会话内未见外部任务 ID 或可回读定位字段（如实声明，不作猜测）；由原 owner 以实际创建/终态原件关联。
- 唯一报告写入本文件；验证原始输出在 `docs/reviews/T10/round-2/zcode-raw/`；独立反例脚本、scratch vitest 配置与派生产物在 `out/t10-review/round-2/zcode/`（git 忽略目录）。审查结束时 `git status --porcelain` 仅 `M AGENTS.md`（受保护未暂存）与 `?? docs/reviews/T10/round-2/`（本报告与 zcode-input/zcode-raw），受审文件零改动；仓库根出现用户级 `~/.mimosa`（hook 系统自身目录）但仓库内无 `.mimosa/` 污染。

## 1. 核验的身份与固定输入

| 项 | 声明 | 核验结果 |
| --- | --- | --- |
| 批准 base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | Git 对象存在 |
| 本轮候选/产品实现 | `66cc15200611d592d3da2877961f9e079eb05277`（= 执行树 HEAD，detached） | `git rev-parse HEAD` 一致；提交对象存在 |
| 旧产品 C / 证据 A / 工具 N | `c3c7e90f…` / `a1e7efef…` / `66eeedd…` | 对象均存在；C→66cc152 产品代码增量仅 inspection.py、test_transfer_inspection.py、render-probe.mjs、private-preparation.md 四文件（见 §3），未触共享契约/Store/writer/main/index/preload/App/锁/CI |
| round-2 输入清单 | `round-2/zcode-input/input-manifest.json` 225 项（219 delta + 6 上下文） | 225/225 逐项与候选 Git blob SHA256+长度比对全部一致（raw: `zcode-raw/manifest-verification.txt`） |
| 旧 147 清单（历史链） | `manifest-original147.json` SHA `b2c17f44…0623` | 147/147 与 A 的 Git blob 全部一致；冻结副本哈希 = `prior147ManifestSHA256` = 现存 `external-review-input-manifest.json` 哈希，三方一致 |
| AGENTS 保护 | SHA `de15f6ce…c8c4`，未暂存 | 实算一致；`M AGENTS.md` 未暂存保持；本审查未改写 |
| 修后候选源哈希 | verification.json 声明 4 文件长度/SHA | 4/4 实算一致（inspection `a94e41be…`、tests `56f894a7…`、probe `c5d89b33…`、doc `9c629fae…`） |
| 环境 | Node v24.15.0 / npm 11.12.1 / uv 0.11.12 / Python 3.12.12（本树 .venv，`uv sync --frozen` 核对 14 包一致）/ macOS 27.0.1 arm64 | 全部在本树独立 env + 自有缓存（UV_CACHE_DIR/npm_config_cache/XDG_CACHE_HOME/TMPDIR 指向自己 scratch）执行 |

## 2. 实际读过与运行过的内容

**逐行通读（代码）**：`packages/engine/src/ontolearn_engine/transfer/{inspection.py(223行),__init__.py}`、`apps/desktop/src/renderer/src/transfer/{report.ts(230行),TransferPanel.tsx(82行)}`、`apps/desktop/src/main/project-transfer/prepared-report-file.ts(338行)`、`apps/desktop/src/csp.ts`；测试 `packages/engine/tests/test_transfer_inspection.py(342行)`、`tests/unit/t10-report.test.ts(183行)`、`tests/unit/t10-report-file.test.ts(513行)`；fixture 3 份（inspection-expected/malicious-texts/report-input）。

**逐行通读（7 工具）**：`docs/iterations/T10/render-probe.mjs`、`docs/iterations/T10/isolated/{Dockerfile,run.sh,run-container.py,prepare-native.mjs,native-hook.cjs,native-driver.mjs}`。

**通读（文档/证据）**：private-stage-candidate、status.md（含 2026-10-22 三段更新）、verification.md、internal-review、report-file-internal-review、isolated-native-review 概要、trusted-contract-review 概要、round-1-disposition、round-2-preparation/{internal-review,verification.json,validation/*}、dispatch-20261022/terminal-receipt、PRD FR-104/FR-1000/FR-1001 原文、12.4/12.5、A-06–08、G.6、verification-summary.json、browser-summary.json。

**实际运行（本树独立 env，全部原始输出留 zcode-raw，含首失败）**：

1. `npm run check` 全量：**exit 0，一次通过** — ESLint(--max-warnings 0)、prettier check、三段 typecheck、vitest **691/691**（17 文件）、构建、ruff+format、pytest **1118/1118**。历史 engine-connection-state TIMEOUT 本轮未复现（与"原因未证实"记录一致）。
2. 定向：`uv run --frozen pytest test_transfer_inspection.py` **66 passed**（round-1 为 60，+6 新参数化用例）；`npx vitest run t10-report + t10-report-file` **61 passed（18+43）**。
3. `node docs/iterations/T10/render-probe.mjs`（修复版，本树实跑）：exit 0，输出 3 个 HTML 到被忽略的 `out/t10-render-probe/`；`malicious-report.html` 3900B/`26af1230…76b6`、`panel.html`、`invalid-panel.html` 与冻结历史原件**逐字节相同**；旧 `evidence/runtime` 目录不存在；受审树无新增可见文件。
4. 独立 ZIP 反例 26 项（自建内存归档直打真实实现，scratch 脚本）。
5. 独立 TS 反例 5 项（scratch vitest 配置，不进入仓库测试发现流）。
6. 报告字节复算：两种输入变体在本机从冻结源码渲染。
7. 哈希核验脚本：225/147 清单、native 55、legacy 40+11、postrun 3、两实物、attempt1/2/3 状态、verification.json 4 文件。

## 3. C→66cc152 增量审查（本轮新改动）

产品代码增量仅 4 文件，全部在 T10 授权写面内：

1. **`inspection.py` EOCD 计数修复（M-F1/Z-O1）**：`_preflight` 现返回 `(offset, count)`；`_inspect` 新增形参 `declared_count` 并在读取任何成员内容之前 `_require(len(entries) == declared_count, "ARCHIVE_SHAPE")`（`inspection.py:154`）。CPython `zipfile` 按中央目录尺寸而非声明计数解析条目，因此该比较确实交叉核验了声明字段；原 `count_disk == count`、`1<=count<=MAX_ENTRIES`、`offset+size==len-22`、连续本地布局检查全部保留。调用点 `inspect_candidate` 完整传递（`inspection.py:215-218`）。无第二套解析器、无新能力开放。
2. **`test_transfer_inspection.py` 新增 6 个参数化用例**：少报（declared=1）、多报（declared=3）→ `ARCHIVE_SHAPE`；两字段不等 (1,2)/(2,1) → `ARCHIVE_SHAPE`（由既有 `count_disk==count` 前置检查拦截）；合法 STORED/DEFLATED full 四核心角色无可选内容对照组 → 接受且 `declared_kind="full"` 保持、四能力恒 false。`pack()` 新增 `compression` 参数，默认值不变（旧 60 用例语义不变）。测试与实现精确对应，无替身。
3. **`render-probe.mjs` 输出目录修复（M-F5）**：`resolve('docs/reviews/T10/evidence/runtime')` → `resolve('out/t10-render-probe')`；`out/` 在 `.gitignore` 内（`git check-ignore` 实证）。本树实跑确认不再污染证据树。
4. **`private-preparation.md`** 同步一句运行说明，与实现一致。

## 4. 独立复现与反例结果（摘要，全量原文见 zcode-raw）

### 4.1 ZIP 检查器（26 项，最终 26/26 通过）

- **EOCD 计数攻击（A1–A8）**：2 成员归档声明 total=1/3、disk=1/total=2、disk=2/total=1、count=0、count=257，及 5 成员归档声明 4/6 —— 全部以预期固定码拒绝（前五者分别为 `ARCHIVE_SHAPE`×4 + `ARCHIVE_LIMIT`×2，后二者 `ARCHIVE_SHAPE`）；5 成员如实声明 count=5 对照组接受。**round-2 修复被独立证实有效，且诚实归档不被误伤。**
- **合法对照（B）**：STORED/DEFLATED full 四核心角色无可选成员 → 接受、kind=full 保持（"完整包无可选内容不误降模板"验收独立复现）；最小 template 接受。
- **round-1 信封性质回归（C1–C13）**：尾随字节/注释、隐藏 deflate 尾随流、前置未编入索引字节、内嵌 NUL 文件名、81 字符名、大写 sha256、重复 manifest 键、NaN、full 缺 checkpoint、未选可选角色出现、中央 CRC 篡改、声明 300 项 —— 全部仍以原固定码拒绝。**修复未破坏既有防线。**
- **能力冻结（D1）**：`import_allowed/restore_current` 恒 false，reason 固定。
- 中途 3 次失败均为**我方构造错误**且被实现正确处理：保留名 `aux` 正确拒绝（UNSAFE_PATH）、77 字符名（≤80 上限）正确接受、重复角色正确拒绝（DUPLICATE_ROLE）——侧面证实保留名/长度/角色唯一检查真实生效。首失败与修正过程全部留档（counterexamples-zip*.txt 三份）。

### 4.2 报告 HTML 与文件服务（5 项 TS 独立反例，全部通过）

- 10 条**新造攻击串**（不在 12 条 fixture 内：`<img onerror>`、`</pre><script>`、`<svg onload>`、`javascript:`、srcdoc、template shadowrootmode 等）注入全部动态字段：输出元素白名单恰为 11 种（html/head/meta/title/body/p/h1/h2/section/pre/span），无任何 `on*=` 出现在标签位置，无 script/iframe/svg/style/img/a/template 标签，全部以转义文本呈现。
- CSP meta 解码后为生产策略：`connect-src 'none'`、`object-src 'none'`、`script-src 'self'`，无 `unsafe-inline`/`unsafe-eval`、无任何 http(s) 源。
- 新造 getter 探针不被执行；非对象输入固定 `REPORT_PROJECTION_INVALID`。
- 前导 LF 完整保留于 `<pre><span>` 内，`<pre>` 后无裸 LF，CRLF 原样。
- 真实 fs 发布：0600、暂存清理完成、二次保存 `REPORT_ALREADY_PUBLISHED`、第二实例覆盖既有文件 `REPORT_TARGET_EXISTS`；**O4 现行为复核**：从未进入 unconfirmed 相位的新实例调用 `reconcilePublication()` 返回字符串 `'unconfirmed'` —— 与"延期未修"声明一致（见 §6）。
- TS 反例中途 3 次失败为我方脚本/断言构造错误（vitest 不接受 /dev/null 配置、scratch 相对路径差一级、`\son[a-z]+=` 正则误伤已转义文本），修正后全过；首失败留档（counterexamples-ts*.txt 三份）。scratch 配置仅包含自己目录，未进入仓库测试发现流。

### 4.3 产物跨环境复算（决定性验证）

- native 输入（`goals=attacks`、保留 fixture 标题"设备运维学习报告"）在本机渲染 → **3896 B / `ad367a31…3cdcd`，与 attempt-3 容器实物逐字节相同**。
- probe 输入（`goals=attacks` + `title=attacks[0]`）→ **3900 B / `26af1230…76b6`，与 legacy 浏览器实物逐字节相同**。
- 两产物差异 4 B 完全由标题输入解释；二者仍是不同文件、不同实际运行（Chrome 的 DOM/哨兵/外联观测 ≠ native 的 picker/0600/容器终态），未混同。

## 5. 历史证据链核验

- native manifest **55/55**、legacy 归档 **40/40** + requiredSummaryRaw **11/11** 逐 hash 通过；postrun 读回 **3/3**（`archivedAs` 指向的 `.cjs.raw` 副本与 index 声明长度/SHA 一致，"停止容器事后读回、非运行时输出 hash"标注保留）；两项旧 snapshot missing 如实登记未伪造。
- attempt-1：`Status=created`、`StartedAt=0001-01-01`、`Pid=0` —— 容器已创建、启动前 CAP 名称检查失败、从未运行，与 addendum 澄清一致；attempt-2：driver `FAIL/T10_NATIVE_DEADLINE`、exit 1、native 停在 save 阶段、nativeDialogs=1，真实失败保留；attempt-3：容器 exit 0、driver/native 双 PASS、真实 GTK 保存(Alt+s)/取消(Escape)、nativeDialogs=2、pickerUnchanged、cancelFileAbsent、3896B/0600(ad367) 与服务回执一致。
- 容器内 61 TS/60 Py 原件复核一致（`attempt-3/units.txt`、`pytest.txt`）；口径为"容器定向三条命令"，未冒充容器全 check。
- 隔离边界如实公开：构建联网/runtime `--network none`、非 root 1110、chrome-sandbox 0:4755、额外 `SYS_ADMIN`、短时 main loopback inspector（picker 前关闭）—— 未被美化为最小权限/全程无 listener。
- verification-summary 的 `formalIntegration/approvedFormat/dualPlatform/credentialExclusionEndToEnd/dualSpecifiedReview/pushed/merged` 全为 false —— 与仓库事实一致，无夸大。

## 6. round-1 十项意见的逐项关闭核对（本轮独立验证）

| 原项 | 处置声明 | 本轮独立验证结果 |
| --- | --- | --- |
| M-F1 P2 / Z-O1 EOCD 计数 | 已修复 | **证实关闭**：代码 §3.1 + 新 6 测试 + 我方 8 项计数攻击与 2 组合法对照（§4.1） |
| M-F5 probe 输出污染 | 已修复 | **证实关闭**：本树实跑，输出落忽略目录，3 HTML 与原件逐字节一致，旧 runtime 目录不存在，树无污染 |
| M-F6 browser/native 标注 | 已澄清 | 处置文档给出精确口径（同源码不同输入、4B 标题差、两运行不相代）；我方复算独立证实该口径；旧原件未改 |
| M-F7 executed:null | 已澄清 | `browser-summary.json` 原样保留 `executed:null`（未观测哨兵），处置文档明确其度量含义，未升级为主张 |
| M-F2 / Z-O2 模板反向 | 开放项 | **仍开放且行为不变**：实测 template+四核心角色仍接受、`declared_kind` 仅保留声明值；未代格式 owner 定规则，与声明一致 |
| Z-O3 每角色单成员/预算 | 开放项 | **仍开放**：`DUPLICATE_ROLE`/8MiB/32MiB/256 项预算原样保留，"非容量承诺"注释在 |
| Z-O4 reconcile 返回值 | 延期未修 | **证实未修**（我方 TS 反例实测现行为仍返回 `'unconfirmed'`）；无生产 caller、不产生发布/越权；声明未标关闭，属实 |
| Z-O5 崩溃残留目录 | 延期未修 | **证实未修**：代码仍无启动清扫器，仅身份绑定非递归 cleanup；已公开为生命周期边界 |
| M-F3 main→renderer 依赖 | 开放项 | **仍开放**：`prepared-report-file.ts:8` 仍 import renderer 目录纯函数模块；未见运行隔离突破，维护风险定性不变 |
| M-F4 desktop 缺显式 zod | 转共享 owner | **仍开放**：`apps/desktop/package.json` 依赖表与 base `5f910b5` 完全相同（无 zod），非本线回归；未称已解除 |

无任何一项被虚报关闭；两项修复（M-F1、M-F5）均已在本轮候选中独立证实。

## 7. 本轮问题清单

**未发现新的 P0/P1/P2 级证实缺陷。** 本轮增量（EOCD 计数修复、probe 输出修复、6 项新测试、一行文档）经逐行审读与 26+5 项独立反例未发现绕过、误伤或回归。以下为**延续开放项**（均已在 round-1 处置中登记，本轮逐一独立复核其现状，无一在本阶段被虚报为已修）：

| # | 级别 | 位置 | 现状与影响 | 边界/建议 |
| --- | --- | --- | --- | --- |
| R2-1（=Z-O4） | P3 | `prepared-report-file.ts:182-187` | 非 unconfirmed 相位调用 `reconcilePublication()` 返回字符串 `'unconfirmed'`（本轮实测复现），纯 API 语义瑕疵；无生产 caller，不产生发布/越权/写入 | 正式 caller 接线前改为固定错误或显式 not-pending 状态，补 prepared/busy 无 IO 及 published 幂等测试 |
| R2-2（=M-F3） | P3 | `prepared-report-file.ts:8` | main 模块依赖 renderer 目录源码；report.ts 现为纯函数（仅依赖 zod+csp），未见运行隔离突破 | 正式接线前下沉至批准的中立纯模块位置，保持行为不变 |
| R2-3（=M-F4） | P3 | `apps/desktop/package.json` | zod 未显式声明（与 base 相同，非本线回归）；靠根提升满足；进入 main bundle 打包前须补声明 | 由共享依赖唯一 owner 在接线/包内验收前处理，T10 不抢写锁 |
| R2-4（=Z-O5） | P3 | `prepared-report-file.ts:257` | 崩溃后 `.ontolearn-report-*` 残留目录无清扫器（本轮代码复核确认未变） | 正式生命周期协议到位后补恢复/身份核验/陌生文件保留验收；当前身份绑定非递归 cleanup 不放宽 |
| R2-5（=M-F2/Z-O2） | P3 开放项 | `inspection.py:199` | template 反向约束（含全部核心角色仍可标 template，本轮实测）与最小角色集未定 | 正式 schema 定稿时由格式 owner 决定，并同步 `TransferPanel.tsx:27` 文案 |
| R2-6（=Z-O3） | P3 开放项 | `inspection.py:19-23,169-171` | 每角色单成员、8MiB/32MiB 防御预算为草案级约束（已注明非容量承诺） | 正式格式阶段按实测重估多成员/分片需求 |
| R2-7（新增观察） | P3 建议 | `packages/engine/tests/test_transfer_inspection.py:257-261` | 新增 disk/total 不等两用例实际由既有 `_preflight` 的 `count_disk==count` 检查拦截（`inspection.py:95`），并非练习新增的 `len(entries)==declared_count` 路径；新检查本身由同文件 declared=1/3 两用例充分覆盖，测试意图与拦截点存在轻微错位 | 可选：为该两用例补充注释说明拦截点，或将用例改构为绕开 preflight 的变体；不影响验收结论 |

历史遗留按原样保留：engine-connection-state TIMEOUT 原因未证实（本轮 691/1118 一次通过未复现）；attempt1/2 失败原件保留且不作为现行候选；两项旧 snapshot missing 保留。

## 8. 承诺准确性抽查（文档 vs 实现/证据）

- "定向 66 Python / 61（18+43）TS / 整仓 691 TS / 1118 Python、check 一次 exit 0" —— 本轮独立复测全部一致。
- "render-probe 输出到忽略的 `out/t10-render-probe/`、3900B/26af 字节不变、旧 evidence/runtime 不存在" —— 本树实跑逐项证实。
- round-2-preparation/verification.json 的 4 文件哈希、probe-output-verification.json 的 3 文件哈希 —— 实算一致。
- status.md 三段 2026-10-22 更新（双审启动/round-1 终态/修后候选）与 terminal-receipt.json、disposition、round-2-preparation 相互一致；"新候选仍需双方各全新完整同版 round-2 审查"如实未把 round-1 通过延伸到本候选。
- `nativePicker:true` 的 scope 限定 "private service; Linux arm64" —— 未冒充正式 App 接线或双平台。
- 引擎正式能力仍仅 health（AGENTS 状态快照口径）—— 未夸大为迁移/包内能力。

## 9. 未验证 / 本阶段不可验证的边界（不因本报告关闭）

正式包格式/schema 与完整 checkpoint 批准（owner 未定）；可信且排除 vault/凭据/发送授权的业务投影（T09/T08，A-06 端到端凭据排除仅为信封级角色拒绝 + 严格 schema，不证明业务文本无凭据）；唯一 writer 原子导入与 receipt；真实学习/重放语义与跨设备续编辑；共享代次/项目/窗口接线、真实 App 内 picker 与触发的 e2e；I06 动态私有根 guard/正式桥接；FR-1000 全量迁移验收；G.6 全部条目；12.4/12.5 双平台与包内验证（本轮未运行 package:dir/e2e，不在本阶段有界验收内）；真人验收；全部 57 P0 与父功能门；指定双审另一方（MiniMax M3.1-Flash/xhigh）本轮同版完整独立审查；push/PR/实际 CI/develop 合并/远端核验。本阶段通过不扩展为上述任何一项。本轮全部验证在 macOS arm64 本机完成（历史 native 证据仅证明原 C 范围的 Linux arm64 隔离容器运行，未被写成新候选的全新原生运行）。

## 10. 最终结论

**明确通过本阶段**（T10-S1 私有包检查与安全报告文件服务，含登记 T-A/T-B/T-C 工具与保全证据，固定于候选 `66cc152`、base `5f910b5`，完整 11+7 作者路径与全部 S1-A/B/C、T-A/B/C 有界验收）：

- 225/225 round-2 输入清单与 147/147 历史清单逐 blob 核验通过；AGENTS 保护与工作树边界全程未破坏。
- 11 项产品/测试/fixture 作者路径与 7 项工具逐行审读；round-1 两项修复（EOCD 计数、probe 输出）经代码审读、新增测试与本人 8+2 项独立攻击/对照、本树实跑逐字节比对独立证实关闭；其余 8 项开放/延期项无一被虚报，现状逐一复核属实。
- 全量 `npm run check`（691 TS / 1118 Py）与定向 66 Py + 61 TS 在隔离 env 一次通过，exit 0；无 TIMEOUT 复现。
- 独立反例合计 31 项（ZIP 26 + TS 5）全部通过；两份历史实物（3900B browser、3896B native）在本机从冻结源码逐字节独立复算成功。
- 55/40/11/3 项证据哈希链全部通过；attempt1/2/3、失败原件、missing 项、口径澄清均如实保留。

通过范围严格限于上述有界阶段；完整 T10 Goal 及第 9 节所列全部父门仍未满足、继续有效。本报告为本模型 round-2 唯一产物，仅写入本文件；未修改任何受审源码、测试、fixture、依赖声明、锁、配置、原始证据或 AGENTS，未执行任何 Git 写操作，未读取另一方本轮任何输出。
