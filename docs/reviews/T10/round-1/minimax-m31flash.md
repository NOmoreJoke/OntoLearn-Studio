# T10-S1 独立外审报告（MiniMax M3.1-Flash / round-1）

审查模型：MiniMax M3.1-Flash（思考档位 xhigh，权限模式 bypassPermissions）。本轮为全新独立只读审查任务，未复用任何旧对话，未读取、未接收、未展示另一方本轮报告/摘要/结论/问题清单。

本报告是本模型本轮唯一产物。结论先行：**明确通过 T10-S1 有界阶段**，登记 1 项 P2（不阻断本阶段）与 6 项 P3。完整 T10 父门全部未关闭，本通过不构成产品、迁移、G.6、跨平台、包内或发布通过。

---

## 1. 实际身份与执行环境

| 项 | 实际值 | 核验方式 |
| --- | --- | --- |
| 隔离工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-c3c7e90` | 全部读写只在此树 |
| Git HEAD | detached `77f2d5048630827ba5220fe092392ded6ab1c697` | `git rev-parse HEAD` |
| 批准 base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git cat-file -t` 通过 |
| 固定证据/清单候选 A | `a1e7efef4bd47c97b630753c0e7c4dc34de1d8ae` | 存在；141 delta + 6 不变上下文 |
| 产品实现 C | `c3c7e90f721344113c4279d663127f9c8d5bda59` | 存在 |
| 工具实现 N | `66eeedd735370576b49eb39cd4b14cdef9c0d55b` | 存在 |
| 恢复点 D | `d3546af3b6fe895957f9626fd4de28bf59dc600a` | 存在 |
| AGENTS.md | `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | 实算 SHA-256 **完全匹配** addendum 声明；保持未暂存 |
| Node / npm | v24.15.0 / 11.12.1 | `node -v` / `npm -v` |
| Python | CPython 3.12.12（`.venv`，本树自建） | `uv sync --frozen` 于本树完成（`raw/uv-sync.txt`、`raw/npm-ci.txt`） |

**身份区分（按 addendum 要求）**：执行树 77 与固定候选 A 之间，141 个受审文件（源码/tests/fixtures/锁/CI）**逐 blob 无差异**；差异仅为流程材料 `docs/reviews/T10/status.md` 及 A→77 新增的两份流程回执文档（`t01-transfer-design-acceptance-r1.md`、`i06-transfer-response-acceptance-r1.md`）。因此本报告不把 a1 当作实际执行 HEAD，也不把当前工作树 status 追加当作 a1 的相同 blob。

**Git 只读**：全程仅 `status/show/diff/log/cat-file/ls-tree/merge-base/rev-parse`，无 stage/commit/stash/reset/checkout/merge/push。审查结束时 `git status --porcelain` 仅 `M AGENTS.md`（受保护）与 `?? docs/reviews/T10/round-1/`（本报告与我的派生流），受审文件零改动。

**本轮任务 ID 未向模型可见**：本会话未收到任何 ZCode/MiniMax 任务 ID、会话 ID 或终态回执字段，因此本报告不猜测任务 ID；如需关联，由原线用实际创建/终态原件关联。

---

## 2. 固定输入清单核验（147 项）

对 `external-review-input-manifest.json` 的 147 项逐项从 **Git 对象**（`git cat-file blob`）取真实字节后重算 SHA-256 与长度：

- 141 项 `candidate-delta` + 6 项 `unchanged-context`：**147/147 长度与 SHA-256 全部匹配，0 缺失、0 不匹配**。
- 首轮报出 1 项"缺失"是 `docs/prd/PRD-本体学习与落地Agent工作台.md`；复核为 `git ls-tree` 对非 ASCII 路径的引号转义所致，以 `-c core.quotepath=false` 复算后**匹配**（93584 B / `7586b2c4…60fbb`），工作树文件与 blob 逐字节相同。
- 关键实现哈希与候选文档自述交叉一致：
  - `prepared-report-file.ts` = `71e7359e…4a0219`（= 清单、= 容器 `compiled-sources.json`、= 内审读回表）
  - `report.ts` = `b5e50810…8c05`（= 容器 `compiled-sources.json`、= 内审读回表）
  - `inspection.py` = `c64ea0f0…41e6e8`；`t10-report-file.test.ts` = `7d0f4253…14e5`；`malicious-texts.json` = `b1b41d90…4e0f`；`render-probe.mjs` = `dcccc5b9…c8807`（后四项亦逐项实算匹配内审读回表）
  - `docs/iterations/T10/i06-trusted-transfer-contract-request.md` = `6e52cdf4…b7bd`（匹配 status.md 声明）
  - `evidence/isolated-native/manifest.json` = `9e515ec9…31e1`（匹配 status.md 声明）

---

## 3. 实际读过与实际运行过的内容

### 3.1 逐字读过的受审文件

- 产品源码 4 份：`packages/engine/src/ontolearn_engine/transfer/inspection.py`(219)、`.../transfer/__init__.py`、`apps/desktop/src/renderer/src/transfer/report.ts`(230)、`.../transfer/TransferPanel.tsx`(82)、`apps/desktop/src/main/project-transfer/prepared-report-file.ts`(338)
- 不变上下文 1 份：`apps/desktop/src/csp.ts`(26)
- 测试 3 份：`packages/engine/tests/test_transfer_inspection.py`(315)、`tests/unit/t10-report.test.ts`(183)、`tests/unit/t10-report-file.test.ts`(513)
- fixture 3 份：`tests/fixtures/transfer/{inspection-expected,malicious-texts,report-input}.json`
- 工具 7 份：`docs/iterations/T10/render-probe.mjs`、`docs/iterations/T10/isolated/{Dockerfile,run.sh,prepare-native.mjs,native-hook.cjs,native-driver.mjs,run-container.py}`
- 候选文档：`private-stage-candidate.md`、`verification.md`、`status.md`、`internal-review.md`、`report-file-internal-review.md`、`isolated-native-review.md`、`trusted-contract-review.md`、`docs/iterations/T10/{private-preparation,interface-needs,report-file-publication}.md`
- 证据原件：attempt-1/2/3 全部 JSON 与日志、`native-compiled-postrun-readback/`、`legacy-raw-archive/index.json` 及 40 项归档、`browser-summary.json`、`initial-browser-summary.json`、`verification-summary.json`、`check-failure-notes.json`、`report-file-failures.json`、`approved-input-reference.json`

### 3.2 实际运行的命令（全部首失败均保留）

| 命令 | 环境 | 结果 | 原始输出 |
| --- | --- | --- | --- |
| `npm run check`（lint/format/类型/构建/vitest/ruff/pytest） | 本树 node_modules + .venv | **EXIT=0**；17 文件 **691 TS passed**；**1112 Python passed** | `raw/npm-run-check.txt` |
| `npx vitest run tests/unit/t10-report.test.ts tests/unit/t10-report-file.test.ts` | 同上 | 2 文件 **61 passed**（18 + 43） | `raw/vitest-t10-targeted.txt` |
| `pytest packages/engine/tests/test_transfer_inspection.py -q` | `.venv` | **60 passed** | `raw/pytest-transfer-targeted.txt` |
| `npm run verify:sources` | 本树 | exit 0，"已核对 12 个归档源文件" | `raw/verify-sources.txt` |
| 审查方独立反例（Python，21 例） | `.venv` | 见 §5.1 | `raw/adversarial-inspection.txt` |
| 审查方 NUL 名单构造（2 例） | `.venv` | 见 §5.1 | `raw/nul-filename.txt`、`raw/nul-filename-detail.txt` |
| 审查方独立 TS 反例（8 项） | 自建 scratch vitest 配置 | 全通过 | `raw/adversarial-ts.txt` |
| 审查方产物复算（5 项） | 自建 scratch vitest 配置 | 全通过 | `raw/recompute-artifacts.txt`、`raw/diff-browser-artifact.txt` |
| 55 项 native manifest + 40 项 legacy 归档逐 hash | 脚本 | 0 缺失 0 不匹配 | `raw/manifest-native-verify.txt` |
| 容器 source-manifest 116 项 vs 当前树 | 脚本 | 0 缺失 0 不匹配 | `raw/source-manifest-verify.txt` |

审查方全部反例与复算脚本、派生输出位于自己的 scratch `out/t10-review/round-1/minimax/`，未写入任何受审源码、测试、fixture、锁、配置或旧原件。

---

## 4. 独立复现结论（与候选自述逐项比对）

| 候选自述 | 审查方实测 | 结论 |
| --- | --- | --- |
| 整仓 `npm run check` 691 TS / 1,112 Python 全通过，exit 0 | 完全一致（EXIT=0） | ✅ 复现 |
| 定向 T10：60 Python / 18 报告 TS / 43 文件服务 TS | 完全一致 | ✅ 复现 |
| 容器内 61 TS / 60 Python（容器定向，非全 check） | 61 TS / 60 Py 复现；确认 `run.sh` 只跑这三条定向命令，**未**冒充容器全 check | ✅ 口径属实 |
| 真实 native 产物 3896 B / SHA256 `ad367a31…3cdcd` / 0600 | **审查方独立复算 = 3896 B / `ad367a31…3cdcd`，且与 `attempt-3/native-report.html` 原件逐字节相同**；发布文件 inode 与暂存 inode 相同（硬链接发布，非拷贝） | ✅ 成立 |
| 浏览器产物 3900 B / `26af1230…76b6` | **审查方独立复算 = 3900 B / `26af1230…76b6`，与归档 `published-report.html` 逐字节相同** | ✅ 成立（口径修正见 F6） |
| native 源提交 `a8a497a8` | 与候选 C 的差异**仅 `docs/reviews/T10/verification-summary.json`、`docs/reviews/T10/status.md` 两份文档**；`apps/ packages/ tests/ scripts/ package.json / package-lock.json / pyproject.toml / uv.lock` **零差异** | ✅ 成立 |
| 容器源清单 116 项 | 116/116 与当前树逐 hash 相同 | ✅ 成立 |
| native 55 项 manifest、legacy 40 项归档 | 55/55、40/40 逐 hash 通过；`missingReferencedSnapshots` 2 项缺口如实登记 | ✅ 成立 |
| attempt1 未启动 | `Status: "created"`、`StartedAt/FinishedAt` 为零值、`Pid: 0`，无 native/units 原件 | ✅ 属实（按 addendum 澄清：容器已创建，启动前 CAP 名称检查拦下，从未启动，不构成一次 native 运行） |
| attempt2 真实失败 | `native.json` 停在 `stage: "T10 01a15bce save"`、`nativeDialogs: 1`；`driver.json` `result: FAIL` / `error: T10_NATIVE_DEADLINE`；容器 `ExitCode: 1` | ✅ 属实 |
| attempt3 成功 | driver/native 均 PASS，容器 `ExitCode: 0`，真实 GTK 保存（Alt+s）与取消（Escape），`pickerUnchanged: true`，`cancelFileAbsent: true` | ✅ 属实 |
| 既有 engine-connection-state TIMEOUT 保留、原因未证实 | `check-failure-notes.json` 记 690 通过/1 失败 `EngineError: TIMEOUT`、单文件 8 通过、`cause: "not established"`；审查方整仓 check 本次 691/691 全绿，**未**复现该 flake | ✅ 属实且未夸大（未宣称已定位原因，也未宣称已修复） |
| ESLint `no-control-regex` 与 fsync 注入首失败 | `report-file-failures.json` 保存原文与 SHA；当前 `prepared-report-file.ts:68` 已无控制字符正则，改逐字符判定 | ✅ 属实 |
| 内审读回哈希 | 6 项全部实算匹配 | ✅ 属实 |

---

## 5. 独立反例结果（不使用受审测试替身，直接打真实实现）

### 5.1 Python 只读信封检查器（`inspect_candidate` 真实调用）

全部反例在内存中构造 ZIP 字节，直接调用冻结源码实现。**20 例中 13 例按预期拒绝、5 例按预期接受（设计上允许），2 例被意外接受（A1/A2）**；另有 2 例 NUL 专项。

| 组 | 用例 | 实测 |
| --- | --- | --- |
| A | EOCD `entries_total` 低报（1）/ 高报（3） | **均被接受** → 见 F1 |
| A | ZIP64 计数标记 0xFFFF / 计数为 0 | ARCHIVE_LIMIT |
| B | 名单内嵌 NUL（截断后仍合法）、反斜杠分隔符、绝对路径、大写 `CON.json`、`data/../x.json`、`data/nul.bin` | 全部拒绝（UNSAFE_PATH / ARCHIVE_SHAPE） |
| B 专项 | NUL 位于"完全合法名之后"（结构正确构造） | **UNSAFE_PATH**；实测 `zipfile` 的 `filename` 被截断为 `data/definitions.json`（仍匹配 PATH），但 `orig_filename` 保留 NUL → `inspection.py:156` 的 `orig_filename == path` 检查正是拦截点，该检查有效 |
| C | 9 MiB deflate 成员 vs `MAX_MEMBER` 8 MiB | ARCHIVE_LIMIT |
| C | 第二个成员共用第一个成员的本地 header | UNLISTED_OR_MISSING_FILE |
| C | 在中央目录前拼接**未编入索引**的隐藏本地成员 | **ARCHIVE_LAYOUT**（本地 header 连续覆盖检查生效） |
| D | `kind="full"` 缺核心角色 | MISLABELED_FULL_PACKAGE |
| D | 可选角色在册但选项为 false | UNSELECTED_CONTENT |
| D | `kind="full"` + 四个核心角色 + **无**原文件/推导/历史/会话 | **接受且 `declared_kind="full"`**（满足"不误降模板"） |
| D | 四个选项为 true 但无对应成员 | 接受，`selected_options` 与 `included_options` 分离正确 |
| D | `kind="template"` 且四个核心角色齐全 | 接受（仅保留声明值）→ 见 F2 |

### 5.2 报告 HTML 与主进程文件服务

| 检查 | 实测 |
| --- | --- |
| 元素白名单（12 条攻击串填入全部动态字段） | 输出仅含 `html,head,meta,title,body,p,h1,h2,section,pre,span` 11 种元素，无 script/style/img/svg/iframe/object/link/a |
| 属性白名单 | 全文档属性仅 `charset, content, http-equiv, lang` 四个静态属性；无任何 `on*=`、`src=`、`href=`、`javascript:` 出现在标签位置 |
| CSP meta 解码后 | `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'` —— 与 `csp.ts` 生产变体一致，**无 `unsafe-inline`/`unsafe-eval`**、无任何 http(s) 源 |
| 前导 LF | `<pre><span>` 方案生效：`<pre>` 后无裸 LF，攻击串原样保留于文本节点 |
| 发布权限位 | 暂存文件 0600、暂存目录 0700、**发布文件 0600** |
| 发布方式 | 发布文件 inode == 暂存文件 inode → 确为同文件系统 hard link 原子发布（非覆盖拷贝） |
| 原子不覆盖 | 既有文件/目录/最终符号链接均返回 `REPORT_TARGET_EXISTS` 且原目标内容不变 |
| 发布后回调异常 | `link-completed`/`published` 阶段抛错仍返回 `state: published, postPublicationError: true`，不谎报失败/取消 |
| 目录 fsync 不可确认 | 返回 `published + durability: unconfirmed + postPublicationError: true`，不降级为普通失败 |
| 清理 | 只按自身 inode 身份删除，不递归；出现陌生文件时保留并返回 `pending`，禁止再次暂存；`retryCleanup` 单飞 |
| 并发 | 同一实例并发保存 → `REPORT_EXPORT_BUSY`；两个独立实例并发发布到不同目标均成功 |
| 失败后可复用 | 导出失败后同一实例可再次保存并成功发布 |
| 拒绝源可访问器 | 抛错对象的 `code` 为 getter 时不被执行（`errno()` 只读数据属性） |

---

## 6. 产物可复现性：两个原生/浏览器产物的确切关系（口径修正，见 F6）

审查方独立复算结论：

- **native 产物** = 当前冻结 `report.ts` 渲染 `report-input.json` 且 `goals = malicious-texts.json`（保留 fixture 原标题）→ 3896 B / `ad367a31…3cdcd`，与 `attempt-3/native-report.html` 原件**逐字节相同**。
- **浏览器产物** = 同一份当前冻结 `report.ts` 渲染同一份夹具，但 `render-probe.mjs:40` 额外把 `title` 覆盖为 `attacks[0]` → 3900 B / `26af1230…76b6`，与归档 `published-report.html` / `malicious-report.html` **逐字节相同**。

即：两者**不是两个不同版本的源码、也不是两个不可比的运行**，而是**同一冻结源码、同一 12 条攻击集的两种投影输入**；4 字节差异完全来自标题文本。候选文档中的"旧 browser3900B/26af"标注与此不符（见 F6）。浏览器证据因此是**当前候选源码的证据**，而非旧版本遗留物。

---

## 7. 问题清单（逐项：优先级 / 位置 / 触发 / 影响 / 证据 / 建议 / 处置）

### F1 [P2｜不阻断本阶段] ZIP EOCD 声明条目数未与中央目录实际条目数交叉核对

- **位置**：`packages/engine/src/ontolearn_engine/transfer/inspection.py:89-99`（`_preflight`），配合 `:149-151`（`_inspect`）。
- **触发**：把 EOCD 的 `entries_total` / `entries_this_disk`（偏移 `len-12` / `len-14`）改成与中央目录实际记录数不同的值（1 或 3），归档仍被接受。`_preflight` 只校验 `count_disk == count`、`1 <= count <= MAX_ENTRIES`、`offset + size == len(raw)-22`；而 CPython `zipfile` 是按 `cd_size`（而非 `count`）解析中央目录条目，因此 `count` 与 `len(archive.infolist())` 从未被比对。
- **影响**：**当前草案内无实际危害** —— `count` 从不用于分配缓冲区或决定成员集合；每个成员仍独立通过路径/保留名/类型/长度/CRC/SHA/本地布局校验，且 `seen == listed | {"manifest.json"}` 保证中央目录里多出的成员无法逃过清单核对（见 A1/A2 实测：多报/少报都被完整校验，成员集合未扩大）。真实风险在于信封自身声明的结构计数没有被强制：生产者与消费者对条目数的分歧在本阶段不可见，若后续正式格式或导入器以该计数为准，会成为完整性缺口。
- **证据**：审查方独立反例 `raw/adversarial-inspection.txt`（A1/A2 两行 `!!-ACCEPTED`）。受审 60Py 现有用例只覆盖计数越界（`MAX_ENTRIES+1`），未覆盖计数与实际条目数不一致。
- **建议**：在 `_inspect` 中断言 `len(entries) == count`（并保留 `count_disk == count`），补两条计数不一致反例。属草案加固，**不改变本阶段任何已登记验收的结论**。
- **处置**：由原唯一 owner 在后续**新候选**中修复并重新验证；按 AGENTS「候选变更后需双方各新任务完整同版重审」，此修复生效时本轮通过不自动继承。**本项不构成本阶段不通过的理由**。

### F2 [P3｜登记的开放项，非缺陷] `kind="template"` 未反向约束

- **位置**：`packages/engine/src/ontolearn_engine/transfer/inspection.py:196`。
- **触发**：四个核心角色（definitions/assertions/ownership/checkpoint）齐全但声明 `kind="template"`，被接受并原样返回 `declared_kind="template"`；现有约束只做单向（`full` ⇒ 核心角色齐全）。
- **影响**：不产生任何能力 —— `restore_current/rerun_mapping/replay_runs/import_allowed` 恒为 `false`，原因固定 `UNAPPROVED_FORMAT_AND_UNVERIFIED_PAYLOADS`。`docs/iterations/T10/private-preparation.md` 已明确声明"`declared_kind` 仅保留清单声明"，因此实现与自身文档一致，**不是缺陷**。
- **证据**：审查方独立反例 D2（`raw/adversarial-inspection.txt`）。
- **建议**：模板/完整包的判定方向属产品决定（AGENTS「不设 PRD 未决问题的默认答案」），**审查方不代定**；请格式 owner（T00）在正式格式批准时明确单向还是双向约束，并同步到界面文案（`TransferPanel.tsx:27` 当前表述只覆盖单向）。

### F3 [P3｜架构] 主进程模块直接依赖渲染端源码目录

- **位置**：`apps/desktop/src/main/project-transfer/prepared-report-file.ts:8`（`import { renderPreparedReport } from '../../renderer/src/transfer/report'`）。
- **触发**：构建主进程包时把 renderer 目录的模块纳入 main 侧依赖图。
- **影响**：今天 `report.ts` 是纯函数（无 Node / React / 网络），复用安全；但方向与「渲染端隔离」约定相反，且正式接线后 main bundle 会打进 renderer 目录代码，属可维护性与边界风险，不是当前功能缺陷。
- **证据**：`prepared-report-file.ts:8`；`report.ts` 全部 import 仅 `zod` 与 `../../../csp`。
- **建议**：正式接线前把报告投影/渲染下沉到共享纯模块位置（如 `packages/contracts` 或 main 私有目录），由 main 与 renderer 共同依赖；行为不变。

### F4 [P3｜既有状态，非 T10 引入] `apps/desktop` 直接 import `zod` 但未在该包声明依赖

- **位置**：`apps/desktop/package.json:13-17` 依赖表 vs `apps/desktop/src/renderer/src/transfer/report.ts:3`、`apps/desktop/src/main/project-transfer/prepared-report-file.ts:7`。
- **触发/影响**：当前靠根 `node_modules` 提升恰好满足（`packages/contracts` 依赖 `zod@4.6.7`）。一旦 T10 模块真正进入 main bundle，`package:dir` 的依赖收集可能不带 `zod`，运行时报模块缺失。
- **证据（**关键**：非 T10 回归**）**：批准 base `5f910b5` 的 `apps/desktop/src/main/index.ts:4` 已同样 `import { z } from 'zod'`，且 base 的 `apps/desktop/package.json` 依赖表与当前完全相同（`@ontolearn/contracts` / `react` / `react-dom`）。
- **建议**：由共享依赖唯一 owner（I06）在正式接线前把 `zod` 加入 `apps/desktop` 显式依赖并同步锁文件；**T10 不抢写共享依赖清单**，本项不计入 T10 缺陷。

### F5 [P3｜工具卫生] `render-probe.mjs` 输出落在受审证据树内的未跟踪目录

- **位置**：`docs/iterations/T10/render-probe.mjs:10`（`const output = resolve('docs/reviews/T10/evidence/runtime')`）。
- **触发**：按文档执行 `node docs/iterations/T10/render-probe.mjs` 会在 `docs/reviews/T10/evidence/runtime/` 生成 3 个 HTML。该目录既不在 `.gitignore`，也不在 147 项固定清单内（仓库当前不存在该目录）。
- **影响**：复现者会在**受审证据树**内产生未跟踪文件，与「证据目录只放已登记原件」的约定相悖，也使该步骤无法在冻结候选上无痕重跑。
- **证据**：`docs/reviews/T10/evidence/` 实际内容（无 `runtime/`）；`.gitignore` 无该路径（`out/`、`evidence/out` 已被覆盖，但 `evidence/runtime` 未覆盖）。
- **建议**：把 probe 输出重定向到 `out/` 或 `evidence/out/`（已在忽略范围），或在 `private-preparation.md` 明确标注该目录为生成物。
- **审查方处置**：因此**未在原位运行 probe**，改为在 scratch 内完成等价渲染复算（结果见 §6），未向受审树写入任何文件。

### F6 [P3｜证据标注不准] "旧 browser3900B/26af" 的"旧"字与事实不符

- **位置**：`docs/reviews/T10/status.md`（"旧browser3900B/26af与新native3896B/ad367是不同实物"）、`docs/reviews/T10/designated-review-backlog-20261022.md`（"真实Chrome检查旧3900B/26af实物"）。
- **事实**：审查方独立复算证明 3900 B / `26af1230…76b6` 由**当前冻结源码**（`report.ts` @ `c3c7e90`，SHA `b5e50810…`）渲染得出，与 native 产物仅差标题输入（见 §6）。它不是旧版本遗留物。
- **影响**：方向是"低估"而非"高估"—— 该标注会让读者把一份**当前有效**的浏览器证据当成陈旧件折扣掉；但同一句话也可能被反向读成"浏览器证据更新、比 native 新"，造成两个证据的先后关系被误读。
- **建议**：改为"浏览器产物与 native 产物为同一冻结源码的两种投影输入（render-probe 覆盖标题为 attacks[0]），字节差异 4 B 全部来自标题文本"，并去掉"旧"字。

### F7 [P3｜措辞] 浏览器摘要中 `"executed": null` 的度量含义需写明

- **位置**：`docs/reviews/T10/evidence/browser-summary.json`、`docs/reviews/T10/evidence/legacy-raw-archive/browser-report-file-summary.json`。
- **事实**：该字段取自 `page.evaluate(() => globalThis.__t10xss ?? null)`，语义是"**未观测到**哨兵被触发"，不是"证明无任何脚本上下文"。同一摘要里的 `dangerousNodes: 0` 与 `externalRequests: []` 才是支撑"不执行、不外联"的正面证据。
- **影响**：单看 `executed: null` 容易被读成比实际更强的主张。
- **佐证**：审查方独立核验（§5.2）确认渲染产物只有 11 种元素、4 个静态属性、无 script/style/iframe/img/link/object/svg/a —— 该前提成立，所以"脚本未执行"的结论本身是稳固的，只是字段命名需要更精确。
- **建议**：把字段改名为可度量的名字（如 `observedSentinel: null`、`scriptContexts: 0`），或在摘要旁补一行度量定义。

---

## 8. 历史处置与既有内部审查核对

- `internal-review.md` 2 项 P2（中央目录外隐藏成员/前后缀；数组 spread 执行 getter 并原样抛敏感异常）在当前冻结源码中**均已实际闭合**：本地 header 从偏移 0 连续覆盖到中央目录（`inspection.py:102-126`）与数据描述符预算（`report.ts:113-145`）在代码中可见，且被审查方独立反例复现（隐藏成员 → ARCHIVE_LAYOUT；访问器不被执行 → 我的 TS 反例与受审用例一致）。
- `report-file-internal-review.md` 3 项 P2（暂存原地改写、清理状态误报、post-link 回调 EEXIST 误判）同样在当前源码中闭合，且**由审查方独立复现**（0600 + inode 相同 + 发布后回调仍 `published` + 清理 `pending` 保留陌生文件）。
- 两份内审均声明"读回时 HEAD 为未提交中间稿"（`a1c76d8a…`），与 backlog 中"提交前中间稿不承诺可重建"的说明一致，本报告不把中间稿当作受审输入。
- `docs/reviews/T10/blocked-audit.md` 记录的 Goal blocked 状态与本阶段候选状态不冲突（候选与原件不变，未 push/PR/CI/合并）。
- **未发现**候选文档与实现之间的实质矛盾；未发现把占位界面、测试替身或 spike 表述为已实现产品能力。

---

## 9. 未验证 / 本阶段不可验证的边界（明确不覆盖）

1. **无正式格式批准**：`t10-envelope-draft-1` 未批准；`import/restore/rerun/replay` 从未开放，恒为 `false`；hash 只证明字节完整性，**不**证明语义、所有权或 checkpoint 可恢复。
2. **无可信业务投影**：报告 DTO 不是可信学习记录来源；真实逐 attempt 证据须由 T09/T08/T01 投影；合成夹具不得冒称真实学习验收。
3. **未接线**：私有报告文件服务与 `TransferPanel` 均**无任何生产 import**（全仓仅其自身定义处出现）；无 preload/bridge、无 App 入口、无真实 native picker、无 I06 动态私有根 guard 或可信投影。**不得把本阶段 Pass 读成正式 App 接线通过。**
4. **无 A-06 端到端凭据排除证明**：检查器只证明未知/私有角色不作为已知成员通过，**不**证明允许角色的自由文本不含凭据，也不证明已实现端到端排除；不得读取真实密钥来扫描。
5. **无打包 / 包内 / 双平台证据**：本阶段未产出 `package:dir`、包内引擎/迁移、双 OS、真人验收证据；本轮**未**执行 `npm run package:dir` 与 e2e（不在本阶段有界验收内，且审查方不得占用受审实现做打包改动）。
6. **原生证据的适用面**：仅 Linux arm64 隔离容器内的**私有服务**保存/取消；容器额外 `SYS_ADMIN`（非最小权限）、**构建期联网 / 运行期 `--network none`**、启动阶段曾存在**短时 main loopback inspector**（由 hook 在 picker 前 `inspector.close()` 关闭，原件记 `mainInspectorClosed: true`），这些边界必须按实际表述，不得美化为"最小权限 / 全程无 listener"。该证据**不**代表通用 e2e、正式 App/bridge 可信投影、G.6、跨平台或包内完成。
7. **既有 TIMEOUT 原因未证实**：engine-connection-state 的 `EngineError: TIMEOUT` 本次未复现，原因仍未确立，保留原样。
8. **浏览器"不执行"是观测结论**：基于 `dangerousNodes: 0` + 哨兵未触发 + 外部请求为空 + 审查方独立元素/属性白名单核验，非形式化证明。
9. **双审与远端门**：本报告只是本轮一方结论；另一方本轮结论、实际 CI、push/PR、正常 develop 合并与远端核验均不在本报告内，也未由本轮触发。

---

## 10. 明确结论

**本阶段结论：T10-S1「私有包检查与安全报告文件服务」有界阶段 —— 明确通过。**

依据：本阶段登记的全部有界验收项均被独立复现满足（141 delta 清单 147/147 逐 hash 一致；整仓 `npm run check` 691 TS / 1,112 Python exit 0；定向 60 Py / 18 TS / 43 TS 全通过；容器 61 TS / 60 Py 口径属实；native 3896 B / `ad367a31…3cdcd` 与浏览器 3900 B / `26af1230…76b6` 两个产物均可由当前冻结源码逐字节复现；55 项 native 与 40 项 legacy 原件逐 hash 通过；失败原件 attempt1/attempt2 与既有 TIMEOUT 均真实保留）。审查方自建 30 项独立反例未发现任何成员逃逸、HTML 注入、外联、覆盖发布、越权清理或失败谎报。

登记问题：1 项 P2（F1，草案加固，不阻断本阶段，须由原唯一 owner 在后续新候选中修复并触发双方新同版复审）与 6 项 P3（F2–F7）。所有 P3 均为登记的开放项、既有状态或标注/措辞修正，**不改变本阶段任何验收结论**。

审查方自建并实际执行的反例合计 **30 项**（Python 20 项 + NUL 专项 2 项 + TypeScript 8 项），另有 5 项产物复算断言，全部通过或按 §7 如实记录；未发现任何成员逃逸、HTML 注入、外联、覆盖发布、越权清理或失败谎报。

**该通过的边界**：仅覆盖 T10-S1 有界阶段。**完整 T10 父门全部未关闭** —— 正式格式/schema 与完整 checkpoint、可信且排除 vault/凭据/发送授权的业务投影、唯一 writer 的原子导入、真实学习与重放语义、公共同代次/项目/窗口/bridge 接线、FR-1000/1001/104、A-06–08、G.6、12.4/12.5、全部父功能与跨模块门、包内与双平台验收、全部 57 项 P0、CI / push / PR / 正常合并 / 远端核验，均**未**因本报告通过。**不得**把本阶段通过扩写为产品、迁移、G.6、跨平台、包内、真实凭据排除或发布通过。

本报告为本模型 round-1 唯一产物，仅写入 `docs/reviews/T10/round-1/minimax-m31flash.md`；未修改任何受审源码、测试、fixture、依赖声明、锁、配置、验收、旧原件或 AGENTS，未执行任何 Git 写操作。
