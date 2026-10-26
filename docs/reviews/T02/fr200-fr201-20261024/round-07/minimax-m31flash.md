# T02 FR-200/FR-201 全新 R07 整候选独立工程审查（MiniMax Code / MiniMax-M3.1-Flash）

> 本报告是本轮（R07）本方唯一报告文件。R06 及更早的双方历史报告按"同等历史输入"可读；本轮另一方正文与当前结论未读取、未索取。

## 0. 结论摘要（结论先行）

**整候选（base `583c05c7` → head `b215f543`，tree `7cab46f0`）判定：附条件通过（Conditional Pass）——本地实现与本地验收通过；未发现 push 前技术阻断；合并必须等待 push 后真实 CI 全量验收。**

1. **本地实现通过**：本轮对 b215 唯一新增（`pyproject.toml` 一行 ruff format 排除 literal）做了独立源码级语义核验，命中面经独立计算精确到 7 个 tracked 文件 / 13 个磁盘文件，无跨层、无 `*`、无 `.py`、无其它 FR 越权；FR-200/201 的 canonical 策略、所有权冲突结构化 witness、preload/IPC/CSP/渲染端隔离等架构不变量逐条复查未发现违反。
2. **本地验收通过**：O047 的实际 `uv run --offline --frozen npm run check`（自然 0、TS 1892 PASS、Python 3769 收集/3719 PASS/50 skip、Ruff 全部已格式化）与原六例真实 GUI（6 PASS/0 skip/0 retry/0 flaky、自然 0）证据齐备，124 针 FINAL-MANIFEST 我逐条复算与磁盘一致。
3. **无 push 前技术阻断**：本轮编号发现 R07-01 至 R07-13 全部为低/信息/维护级；未发现数据泄露、资金损失、服务中断类缺陷（该产品为本地优先桌面应用，本轮范围内无账号/计费/多租户面）。
4. **必须等 push 后真实 CI 才可 merge**：b215 未 push、本 head 无任何 CI；远端 feature 仍为 `33059f82`、develop 仍为 `583c05c7`、PR16 open 未合并。Windows 完整 3769 全集及全部后继 typecheck/build/E2E/package/verify 与三 job 真实 success、Quality packaged recovery 步骤自身 success，仍是接收前硬门禁。
5. **不可继承项**：R06 的 ConditionalPass / verification-incomplete 不构成本版通过依据；历史具名 HOLD（D3/D4/D6/D8/D10/D11 等）与全部法律、平台、容量、退出码、Undo HOLD 原样保留。整体合并可用仍为 2/17，不得据此宣称 Goal／M0／发布完成。

---

## 1. 身份、来源与可证范围

| 项 | 值 | 来源与可证性 |
|---|---|---|
| 应用／代理 | MiniMax Code，Agent 路由 ID `mavis` | 运行时注入的 agent-context |
| 会话 ID | `mvs_8d66d37640404c25bc061bffe6311b0b` | 运行时注入 |
| 模型 | MiniMax-M3.1-Flash | 运行时注入的 Environment 声明 |
| thinking 等级 | 封存声明为 `xhigh` | **本代理侧不可自证**：运行时未向本代理暴露思考等级／权限模式字段，故按"声明值、不可自证"记录，不虚造观测 |
| 权限模式 | 封存声明为"始终授权" | 同上，不可自证；本轮实际未行使任何越权写入 |
| 官方 UI 的任务 ID／cwd／provider／model／thinking／permission | — | 由操作者从官方 UI 核；本方仅记录上述"实际可知来源" |
| cwd | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T02-s1-review-fixes` | 本方 `pwd` 实测 |
| 分支 | `feature/weekly-t02-fr200-fr201` | 本方 `git rev-parse --abbrev-ref HEAD` |
| base（显式审查基线） | `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` | 实测；`git merge-base --is-ancestor 583c05c7 b215f543` → **YES**（base 是 head 祖先）。**更正**：本工作区本地 `develop` ref 实际停在 `5f910b52c69d86a1076b2032e5d3c63e715947f3`，`merge-base(HEAD, 本地 develop) == 5f910b52`（过期本地 ref），**不等于**显式审查基线 583；两者须分开表述 |
| head | `b215f5432d0c9f74df9e9e3fbb6120bff57703a9` | 实测 `git rev-parse HEAD` |
| tree | `7cab46f041140114d5011d86077c54aeb93d537d` | 实测 `git rev-parse HEAD^{tree}` |
| 规模 | 33 提交 / 88 差异叶 / 1371 tracked 物理源 / 5 构建 | 逐项实测（`rev-list --count` / `diff --name-only | wc -l` / `ls-tree -r | wc -l`），与封存声明一致 |
| 附件封存 prompt | 28717 B，SHA256 `53d6f688f7a095308ae8dc3f0f5a916e038818ea5a5bede452e95c02ffba73c8` | 实测；读取至 EOF（236 行），原 160 项清单恰一次。清单原文段（marker `你现在是我的软件工程审查员。` 至 EOF）实测 **11255 B、文件无末尾换行、marker 在全文恰出现 1 次且起始于 byte 17462**，与原声明的 11255 B 一致 |
| 本轮事实包（收据见 §12.1） | 11096 B，SHA256 `8dfb706dcee9197ce6198166d1ad92838129a7c0935554134abafe28fb48bc73` | 实测一致；经本地绝对路径读取，非 UI 附件 |

**同行正文边界（如实声明）**：目录操作中见到 `round-01`…`round-07` 下的报告文件名、字节数与 mtime 等元信息（如 `round-06/minimax-m31flash-r2.md`；末次交付自检时 `round-07/` 下已并存 `zcode-glm53.md`）。**本方未读取任何同行模型报告正文**（round-06 的 `zcode-glm53.md` / `minimax-m31flash.md` / `minimax-m31flash-r2.md` 与 round-07 的 `zcode-glm53.md` 正文均未读）。R06 的双方结论仅通过操作者自有的 `round-06/disposition.md` 与 `version-map.json` 读到，未以同行正文为审查依据，也未反推已读正文。**元信息随时间变化不影响当时的匹配面测量**：b215 排除模式在原测量时点命中 7 份 tracked ＋ 6 份未跟踪 ＝ 13；当前磁盘命中数已因后续报告（含本文件与并存同行文件）增加，**该增量不否定当时的 13**，也不构成把后续报告纳入受审集合的理由。

---

## 2. 已读范围（完整）

### 2.1 需求与决策原件

- `docs/prd/PRD-本体学习与落地Agent工作台.md`：93584 B / SHA256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb`（实测一致）。实读正文 FR-200（307–310 行）、FR-201（312–318 行）、附录 C（959–981）、附录 D.1/D.2（983–1015）、附录 E/G 的引用约定，以及第 623、744、827、856、904–905 行等约束句。
- `docs/iterations/I01/ADR-0002-storage.md` 第 27 行 canonical 政策原文（实读全句）。
- `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`：真实归档路径存在，35812 B / SHA256 `c289a1cd1a9cf40187ef6e506e134b0edcae6dea95d9e99805d4f3045e67cf96`；`docs/reviews/I03/inputs/` 下有同名同 SHA 件；`docs/architecture/` 下无该件（仅 0001、0003）。
- 人类授权 `iteration-control/2026-10-21-weekly-release/user-grants/T02-D8-choice-A-20261025.json`：2172 B / SHA256 `72c8fca8376d421e4fe8593ffccd5f79de5e605b34763a7008685d8be746b26c`（实测一致），全文实读。

### 2.2 候选差异（88 叶全部覆盖）

- 全部 88 个差异叶经 `git diff --name-status` 列出并分类；源码／测试／配置／CI／依赖侧 57 叶（11992 插入 / 251 删除）全部实读差异或委派实读（见 §3.3）。
- 引擎侧实读差异：`project/mainline.py`（+417）、`project/project_host.py`（+169）、`storage.py`（+114）、`job_store.py`（+406）、`project/query_presentation.py`（+21）、`project/domain_changesets.py`（+36）、`rdf_snapshot.py`（+32）、`coordinator.py`（+23）、`packages/engine/pyproject.toml`。
- 契约／桌面侧实读或委派实读差异：`packages/contracts/python/contract_v2.py`、`packages/contracts/src/{index.ts,v2.ts}`、`packages/contracts/v2/{schema.json,registry.json,fixtures.json,binding-regressions.json}`、`apps/desktop/src/main/{desktop-ipc.ts,engine.ts,project-mainline-service.ts}`、`apps/desktop/src/preload/index.ts`、`apps/desktop/src/renderer/src/ontology/*`（7 叶）、`tests/e2e/t02-fr200-fr201.spec.ts`（1748 行，读其用例矩阵与参数化结构）。
- 配置侧：`pyproject.toml` 全量（base 与 head 双向）、`.prettierignore`、`.prettierrc.json`、`.gitignore`、`package.json` scripts、`.github/workflows/ci.yml`（全量）。
- 证据与历史：`round-06/{disposition.md,version-map.json,artifact-manifest.json}`、`round-05/fr200-fr201-original-clause-evidence-map.md`、`docs/reviews/T02/status.md`、`docs/m0-checklist.md`。
- 证据目录：`outputs/20261025_t02_raw_report_format_repair_047/`（O047）全量文件清单与关键 JSON；`outputs/20261025_t02_33059f82_ci_attempt2_046/`（O046）三 job 原始日志与 `pr-final.json`/`refs-final.txt`/`final-guards.json`；`outputs/20261025_t02_934bd14f_remote_ci_040/`（O040）；`outputs/20261025_t02_33059f82_remote_ci_045/`（O045）。

### 2.3 外部权威来源（只读）

- ruff `0.17.1` 官方源码：`crates/ruff_linter/src/settings/types.rs`（FilePattern／FilePatternSet）、`crates/ruff_workspace/src/configuration.rs`（FormatConfiguration::from_options）、`crates/ruff_workspace/src/resolver.rs`（match_exclusion）、`crates/ruff_linter/src/fs.rs`（normalize_path_to）、`crates/ruff/src/commands/format.rs`（Markdown 分支与排除调用点）。
- `uv.lock` 内 `ruff==0.17.1`（pin 实测）。

---

## 3. 本人实做 vs 读回验证（严格区分）

### 3.1 本方本轮亲自执行的只读计算与结论

| # | 本方实做命令／方法 | 结果 |
|---|---|---|
| E1 | 附件 `wc -c` + `shasum -a 256` | 28717 B / `53d6f688…73c8`，与封存声明逐字一致 |
| E2 | `read` 全文至 EOF（236 行），脚本提取 `>` 清单行 | 160 项，编号 1–160 与原序一致。**更正**：原写的"清单段 11257 B、声明 11255 B、差 2 B 仅为尾部换行口径"是**错的口径比较**——11257 B 是"提示末行之后到 EOF"这一**不同**片段的长度；原声明的 11255 B 对应 marker `你现在是我的软件工程审查员。` 至 EOF 的片段，实测恰为 **11255 B**，marker 恰出现 1 次、起始 byte 17462、文件无末尾换行 |
| E3 | `git rev-parse` / `rev-list --count` / `diff --name-only \| wc -l` / `ls-tree -r \| wc -l` | base/head/tree/33/88/1371 全部与声明一致。**更正**：本地 `develop` 实为 `5f910b52`（过期本地 ref），`merge-base(HEAD, 本地 develop) == 5f910b52`；显式审查基线 583 经 `--is-ancestor` 独立验证为 head 祖先。两者不可混同 |
| E4 | `git diff base head -- pyproject.toml` + 全量 `pyproject.toml` 双向对比 | **仅在既有 `[tool.ruff.format].exclude` 末尾追加 1 行 literal**；`[tool.ruff]`、`[tool.ruff.lint]`（无 exclude 键）、`lint.per-file-ignores`、`pytest.testpaths`、依赖组、命令、CI、锁文件全部未变 |
| E5 | ruff 0.17.1 官方源码链阅读（5 个 raw 文件） | `format.exclude` → `FormatConfiguration::from_options` → `FilePattern::User(pattern, GlobPath::normalize(pattern, project_root))` → `absolutize_from` → 项目根锚定的**绝对** globset；因 pattern 含 `/`，`FilePattern::add_to` 不注册 basename 回退；`ruff format` 在 0.17.1 对 `.md` 生效（`ruff_markdown::format_code_blocks`） |
| E6 | 纯 Python glob→regex 独立复算命中面 | **tracked 精确 7 份**（round-04×2、round-05×2、round-06×3）；磁盘在册 **13 份**（+round-01/02/03 未跟踪 6 份）；负例全部不匹配：`round-04/archive/*`、`disposition.md`、`-r3`、`round-100`、`round-6`、任意 `.py`、T01 冻结脚本、裸文件名 `minimax-m31flash.md` |
| E7 | `git show 831813c6` + Python AST 对拍（剥 6 个 `encoding="utf-8"` 关键字后与 base 逐树比较） | 两文件均 **AST 严格相同 = True**（剥除数 5 + 1 = 6），印证"去六 keyword 后完整 AST 严格相同" |
| E8 | 测试树 `write_text` / `ensure_ascii=False` 全量 AST 普查 | `write_text` 39 处＝**19 显式 UTF-8 + 20 默认**（与 R06 口径一致）。**更正**：20 处默认者的真实分布为 `manual_input_rejection` **13** + `read_work_budget` **5** + `postwrite_admission` **1** + `dispatch` **1** = 20（原报告写 14+5+1+1 有误）；其首参一律是使用默认 `ensure_ascii=True` 的 `json.dumps(...)`，输出为纯 ASCII。39 处中含 `ensure_ascii=False` 载荷者共 **12** 处，**全部显式 UTF-8**：其中首参恰为 `json.dumps(..., ensure_ascii=False)` 者 **10**，另 **2** 处首参是 `json.dumps(..., ensure_ascii=False) + "\n"` 的 BinOp 载荷（`test_mainline_postwrite_rows_budget.py:261`、`test_mainline_postwrite_text_budget.py:200-214`，encoding 在 214 行）——原报告"多出的 2 处是更深的嵌套/间接变量"表述不准确。测试树 `json.dumps(ensure_ascii=False)` 全树共 **23** 处（另一分母） |
| E9 | O047 build／nonce 独立复算 | build **5 项**：`before.json`(head=33059f82) → `after-fullcheck.json`(head=b215f543) **4 项 byte-exact、仅 `apps/desktop/out/main/index.js` 变**（`6470899108e1…`→`dac669aefe85…`）；main 606471 B 前后等长，**24 字符 nonce 字段内有 23 个字节不同**（差异位置集中于 `[602382,602406)`），内容 `nhapxQBkVHgUy3gyCiH7jtNx` → `oB7QhDLgV/PI8q/xX8+ucqvw`，与声明逐字一致；GUI 前后 build 5/5 全等。**边界**：这是文件身份，不是内存模块哈希、不是 serve/HMR/新包证明 |
| E10 | O046 三 job 原始日志行核对 | 三 job 一致：`All checks passed!` → `unformatted: File would be reformatted` → `1 file would be reformatted, 385 files already formatted`；随后 pytest 与全部后继步骤 SKIPPED（Windows 诊断步 2 秒内失败，macOS engine:check 1 秒内失败，Quality 在 `npm run check` 失败）。**更正/补记**：Quality job 在失败前**实际跑过** I04 矩阵 `144 passed in 21.89s`、typecheck（`tsc --noEmit`）、vitest `Test Files 39 passed (39)`、三次 `built in`；**只有完整 3769 项 pytest 套件在三 job 全部 NOTRUN**。故"完整套件未运行"**不得**被表述为"没有任何 Python／typecheck／build 运行过" |
| E11 | O047 `COMPLETION.json` 实读 | head/tree/唯一改动/TS 39 文件 1892 PASS/Python 3769 收集 3719 PASS 50 skip 1 warning/Ruff 379/GUI 6 PASS/58 附件/57 事务/43 拒绝/101 采样/33 knownPID/0-2-5 remaining [0,0,0]，及 8 条 limits 与 handoff 门禁，均与声明一致 |
| E12 | `docs/reviews/T02/status.md` 与 `docs/m0-checklist.md` 实读 | 两者当前最新追加节仍停在 `831813c6`／R06（status 记 "Ruff386"）；**未记录 b215 当前事实**（见 R07-04） |
| E13 | 远端状态读回（O046 快照，非本轮实时） | PR16 open、未合并、mergeable true；远端 feature `33059f82`、develop `583c05c7`（本轮无远端权限，未联网复核） |
| E14 | Ruff format 计数与候选集合对账（`git ls-tree` 以 `core.quotePath=false` 重算扩展名） | 831813c6：tracked 可格式化 **384**（py 109 + md 275）；b215f543/33059f82：tracked **390**（py 109 + md 281）；pyi/ipynb 均为 0。base 已有的 **4 条** `format.exclude`（T01 四个冻结生成脚本，均为 tracked `.py`）计入 tracked 数内。候选集对账：8318 = 384 tracked + 6 未跟踪 round-01/02/03 = 390 − 4 既有排除 = **386**；b215 = 390 + 6 = 396 − 4 − 13 新模式 = **379**。与 status.md 的 "Ruff386" 与 O047 的 "379" **逐一吻合** |
| E15 | `mainline-facts.ts` 事实 ID 派生实现复读 | renderer 用 `TextEncoder` + WebCrypto `crypto.subtle.digest('SHA-256', …)`（第 75–81 行）派生事实 ID，**不是手写 SHA-256**；孤立代理项拒绝在第 58–62 行。手写 SHA-256 位于另一模块 `packages/contracts/src/v2.ts`（见 R07-13） |
| E16 | `storage.py` 错误码表与 `job_store.py` 出口复读 | `storage.py:50-64` 的 category→code 映射表**确无 `ownership` 键**（未命中即默认 `INTERNAL_ERROR`）；但 `ManualOwnershipConflict`（67-94）与 `SingleDeclarationConflict` 均以 `category="ownership"` 构造。`job_store.py:617-636` 在 `except Conflict` 分支按 `error.category` 拦截：有 ownership proof 且为 typed witness → 持久化结构化 detail；无 proof → 遗留裸 detail；**两个出口最终都是 `OWNERSHIP_CONFLICT`**。故码表缺键不等于"ownership 类必然落到 INTERNAL_ERROR"，也不等于"所有裸 ownership 家族已闭合" |
| E17 | `tests/e2e/t02-fr200-fr201.spec.ts` 拒绝与保留断言复读 | 第 762–775 行以 `toHaveValue` 断言 S/P/O 在受控拒绝后**保留**（含 4301 输入，O047 实测通过）；第 767–770 行的拒绝文案为**单一固定中文提示**（INVALID_REQUEST 一种、OWNERSHIP_CONFLICT 另一种），**不是**按内部 typed category 分语言/整数/canonical 的差异化文案 |
| E18 | Undo 现状复读 | `OntologyMainlinePage.tsx:401-404` 存在"预览撤销本次修改"按钮 → `session.prepareUndo()`；`mainline-session.ts:393-400` 的 `prepareUndo` **重新读取新基准**并以 `intent: 'undo'` + 原 `operationId` 准备。**Undo UI 现已存在**（旧 ADR 的"此次不实现产品撤销 UI"是 spike 期历史表述），但仍未被本轮六例 GUI 证据覆盖 → 记 UNTESTED／HOLD，**不构成父 FR 闭合** |
| E19 | 语言标签 canonical 正反控复读 | 正控 canonical 为小写形式 `de-ch-1901`／`en-001`；`de-CH-1901` 语法合法但**非 canonical，受控拒绝**（原报告把它写成正控，属更正） |
| E20 | 本轮事实包原件收据 | `/tmp/t02-r07-minimax-facts-8dfb706dcee9.txt`：实测 **11096 B**、SHA256 `8dfb706dcee9197ce6198166d1ad92838129a7c0935554134abafe28fb48bc73`，与声明一致；已完整读取至 EOF（EOF. 结束）。传输方式为**本地绝对路径引用 + 本方实际读取**，非 UI 附件；未随包提供任何本轮同行材料 |

### 3.2 读回验证（操作者证据，本方未重跑）

以下结论来自**读回操作者既有证据原件**，不是本轮模型重跑：本轮 `npm run check` 的自然 0 与全部计数、原六例真实 GUI 的 6 PASS 与 3997237 B report、58 个 inline body 解码全等、57 事务语义与 43 拒绝语义、package094 身份与旧包内验收、O040 的 cp1252 首败栈、O045 的 GitHub 账单／spending-limit 门禁、124 针 FINAL-MANIFEST 的被钉事实。本方对这些原件做了哈希／字节／结构一致性复算（E9–E13 与 §3.3 C 项），**但没有重新执行产品、测试、构建、打包或 GUI**。

### 3.3 委派取证（三个只读子代理，已披露）

为覆盖 88 叶中的大体量差异，本方并行派出三个只读取证子代理，均被禁止运行 npm/check/vitest/pytest/ruff/build/package/GUI/sqlite、禁止改文件与 git 写操作：
- **A（引擎侧）**：`packages/engine/src/**` 与 `scripts/repack-rdflib-input-types.py` 差异取证 → 结论已由本方对 `mainline.py`／`storage.py`／`rdf_snapshot.py`／`domain_changesets.py`／`project_host.py`／`coordinator.py`／`query_presentation.py` 的一手复读覆盖。
- **B（契约＋桌面侧）**：`packages/contracts/**` 与 `apps/desktop/**` 差异取证 → 关键结论（zod `.strict()`、preload 仅新增业务命名方法、无 `invoke(method,params)` 通用通道、IPC sender/mainFrame/可信文档校验保留、`csp.ts` 未出现在 diff、renderer 无 `innerHTML`/`dangerouslySetInnerHTML` 等 XSS sink）本方已一手复核。
- **C（证据链与历史处分）**：O040/O045/O047 与 R06 原件取证 → 其给出的 status.md 路径更正、build 五项口径、R06 D1–D12 覆盖、028 笔映射口径、D8 四条禁止，本方均已一手复核。

### 3.4 本轮明确未做（执行边界）

未运行 npm / `npm run check` / vitest / pytest / ruff / tsc / vite build / package / install / `uv sync` / HMR / 任何 GUI 或产品启动 / 任何 sqlite 打开；未改 index、未 commit／push／切分支／动 remote；未读密钥、`.mimosa`、无关 profile；未读取本轮另一方报告正文；未重试被拒 probe、未打开旧失败 DB；未修改源码、测试、配置、依赖、构建产物或任何历史报告。**本轮仓库内唯一写入是本文件。**

---

## 4. 对封存声明的独立核验结论

| # | 封存声明 | 核验结论 | 依据 |
|---|---|---|---|
| V1 | base/head/tree/33 提交/88 叶/1371 源/5 构建 | **属实**（base 指显式审查基线 583；本地 develop 实为过期 ref `5f910b52`，二者已分开表述） | E3 |
| V2 | AGENTS.md 为 15147 B / `de15f6ce…c8c4` 的受保护未提交 overlay | **属实** | 实测字节与 SHA；`git status` 显示仅 AGENTS.md 修改 + round-01/02/03 未跟踪 |
| V3 | PRD 93584 B / `7586b2c4…f60fbb` | **属实** | 实测 |
| V4 | b215 只在 `[tool.ruff.format].exclude` 追加 1 行 literal，配置 1593→1707 B，`e4b989…`→`ed02773b…` | **属实** | E4 |
| V5 | 该规则只 FORMAT，不改顶层或 lint exclude | **属实** | `[tool.ruff]` 无 exclude 键；`[tool.ruff.lint]` 无 exclude 键，仅 `per-file-ignores` 未动 |
| V6 | 当前 tracked 命中 7 份 | **属实** | E6 |
| V7 | 无任意跨层 `*`，不匹配 nested archive/disposition/独核/manifest/其它 MD/其它 FR/任意 `.py`，不授予创建额外文件权 | **属实** | E6 全部负例不匹配；ruff 侧因 pattern 含 `/` 不注册 basename 回退 |
| V8 | `831813c6` 两文件六处 `write_text` 新增 UTF-8，去六 keyword 后 AST 严格相同 | **属实** | E7（AST 对拍 True/True） |
| V9 | 测试树 39 write_text；12 ensure_ascii=False 均显式 UTF8 | **属实（口径已精确化）** | E8：39＝19 显式 + 20 默认；12 = 首参恰为 `json.dumps(..., ensure_ascii=False)` 10 处 ＋ BinOp 载荷 `json.dumps(...)+"\n"` 2 处（rows_budget.py:261、text_budget.py:214），12 处**全部显式 UTF-8**；20 处默认者全部 `ensure_ascii=True`（纯 ASCII）；全树 `json.dumps(False)` 23 处为另一分母 |
| V10 | O047 四文件字节/SHA、FINAL-MANIFEST 124 针 | **属实** | 字节与 SHA 逐个实测一致；124 条路径存在、bytes/SHA 全部一致（子代理 C 复算，本方采信并抽查） |
| V11 | O047 五 build 四项 byte-exact，main 仅 24 字符 dev nonce 差 | **属实**（读法须为"5 项中 4 项相等"；24 字符字段内 23 字节不同） | E9 |
| V12 | O046 三 job 自然 failure，Ruff lint 通过后 FORMAT 报 1 would/385 already，pytest 全 NOTRUN，后继 skipped | **属实**（须与"Quality 内 I04 矩阵 144 PASS、TS 39 文件、typecheck、build 实际跑过"并列，不得简化为"什么都没跑"） | E10 |
| V13 | O040 首败为 cp1252 UnicodeEncodeError，1FAIL/980PASS/3SKIP/258.55s | **属实** | O040 `FIRST-WINDOWS-FACTS.json` 真实栈原文；自陈 notProved 项与声明一致 |
| V14 | O045 为 GitHub 付款/spending-limit 门禁，三 job runner0/steps[]/artifact0 | **属实** | O045 `FINAL-CI-FACTS.json` 原文 |
| V15 | R05 `fr200-fr201-original-clause-evidence-map.md` 有"原 28 笔实际 Read 映射" | **部分属实（口径需更正）** | 该文为**条款级映射＋笔段定位**（class 第 3–7 笔、原02 第 3–7 笔、原05 第 8–18 笔、FR201 原 22 笔 records），非逐笔 28 行台账；**但 FR-200 四类表单 28 笔的 GUI 语义覆盖事实不变，层级／domain／range／type／五组 metadata 也不得后移到后续** |
| V16 | 远端 feature=330、develop=583、PR16 open 未合并 | **属实**（读回 O046 快照，非本轮实时） | E13 |
| V17 | "证据只提交摘要"与本轮唯一报告路径 | **遵守** | 本文件为唯一仓库写入 |
| V18 | 原声明"用户原始 11255 字节审查清单全文" | **属实**（原报告的 11257 B 比较口径错误，已更正） | E2：marker→EOF 实测 11255 B、marker 恰 1 次、起始 byte 17462、无末尾换行；其 SHA256 实测 `1ca23def39d88ceaace9ad1b8aa14ee8714229871e9d6b1d1edd0f9e847f709c` |
| V19 | Ruff format 计数 386（8318/O041）与 379（b215/O047） | **属实且现已完成对账** | E14：384 tracked + 6 未跟踪 − 4 既有 T01 排除 = 386；390 + 6 − 4 − 13 新模式 = 379。**边界**：数字吻合不证明 ruff 的发现/选择集合完全等同于扩展名计数，也不单独证明"差 7 由 7 份 tracked 报告引起"这一因果 |
| V20 | Undo 现状 | **更正**：Undo UI **已存在**（`OntologyMainlinePage.tsx:401-404` → `mainline-session.ts:393-400` 重新读基准后以 `intent:'undo'` 准备）；旧 ADR"此次不实现产品撤销 UI"是 spike 期历史表述 | E18；本轮六例 GUI 未覆盖 Undo → UNTESTED／HOLD，不构成父 FR 闭合 |
| V21 | 事实包所载 marker 段摘要值 `ca23def3…f709c` 标注为 SHA1 | **部分可复现**：长度 11255 B、偏移 17462、单次出现、无末尾换行均可复现；该 63 位十六进制值实为同一片段 **SHA256** `1ca23def…f709c` 去掉首位 `1`（本方实测 SHA1 为 `8b6861f3e51cfaed683858c9b2fe4b3e6d7516e7`）。**算法标签与首字符被截断**，故原样照抄会失真，按实测登记 | E2／E20 |

---

## 5. 本轮发现（编号／等级／位置／触发／影响／证据／建议／阻断性）

> 等级定义：**阻断**＝push 前必须修复；**条件**＝merge 前必须完成且不涉及新源码缺陷；**低**＝可延后；**信息**＝事实澄清或已核验通过。

### R07-01【信息·已核验通过】b215 的一行 ruff 排除在语义与影响面上均正确、无越权

- **位置**：`pyproject.toml:39`（`[tool.ruff.format].exclude` 第 5 项）
- **触发**：任何 `ruff format --check .`（即 `npm run engine:check` 的第二步）
- **影响**：正确修复 CI 的 format 步失败，同时不扩大排除面
- **证据**：E4–E6；ruff 0.17.1 源码链（`FormatConfiguration::from_options` → `FilePattern::User` → `GlobPath::normalize` → `absolutize_from` → 项目根锚定绝对 glob；pattern 含 `/` 故不注册 basename 回退）；命中面 tracked 7 份、磁盘 13 份，全部为 T02 本评审的 raw 报告
- **建议**：接受，无需修改
- **阻断性**：否

### R07-02【低】排除模式不覆盖未来同类 raw 命名（如 `-r3`）

- **位置**：`pyproject.toml:39`
- **触发**：将来出现 `round-NN/minimax-m31flash-r3.md` 或 `round-NN/zcode-glm53-r2.md` 且其 Python fence 需要 ruff 改写
- **影响**：CI format 步重新失败（仅当该文件含需改写的 fence）；不涉及产品正确性
- **证据**：E6 负例 `round-06/minimax-m31flash-r3.md` 不匹配
- **建议**：当前按"现状可接受"处理；若将来新增 `-rN` 命名，须以新候选同步扩展该 literal（不得为格式绿重排 raw）
- **阻断性**：否

### R07-03【低】ruff format 与 prettier 的 Markdown 策略不一致

- **位置**：`.prettierignore:10-11`（整目录排除 `docs/prd`、`docs/reviews`）vs `pyproject.toml:33-40`（仅排除 3 个 raw 文件名）
- **触发**：将来修改 `round-0N/disposition.md`、`independent-*.md`、`round-04/archive/*.md` 等其余评审 Markdown，且其内含需 ruff 改写的 Python fence
- **影响**：CI format 步失败；与"原始审查是不可变引用证据"的原则冲突面小（其余评审文档不是 raw 原稿）
- **证据**：`cat .prettierignore` 与 `pyproject.toml` 实读；O046 显示 raw 报告正是当前唯一触发点
- **建议**：由唯一维护者在后续新候选统一策略（要么 ruff 侧同样排除 `docs/reviews`，要么明确其余评审文档允许被格式化），本轮不扩大排除面
- **阻断性**：否

### R07-04【条件】唯一状态源尚未记录 b215 当前事实

- **位置**：`docs/m0-checklist.md`（末尾追加节仍为 `831813c6`）、`docs/reviews/T02/status.md`（末尾追加节仍为 `831813c6`／R06）
- **触发**：以 b215 为受审 head 合入后
- **影响**：AGENTS.md §6 规定完成度只在这两处维护；当前二者描述的是上一时点受审候选（且 status 内仍记 "Ruff386"），与 b215 事实脱节
- **证据**：E12；`git show 33059f82 --stat` 证实 `33059f82` 只做了 R06 归档与两处追加，b215 提交本身未追加
- **建议**：**merge 前**由唯一维护者仅追加 b215 当前时点（head/tree/唯一改动/O047 事实/本轮门禁），**不改写** R04/R05/R06 历史前缀与旧 manifest
- **阻断性**：否（文档动作，非源码缺陷；但属 merge 前条件）

### R07-05【低】AGENTS.md 中 M0 计划链接指向不存在的路径

- **位置**：AGENTS.md 第 10 行（受保护的未提交 overlay）→ `docs/architecture/m0-review-and-update-plan-2026-10-19.md`
- **触发**：按 AGENTS.md 指引去读 M0 计划
- **影响**：读者会漏读真实原件；真实归档在 `docs/iterations/I01/inputs/`（同件亦见于 `docs/reviews/I03/inputs/`，SHA 相同），`docs/architecture/` 下无该件
- **证据**：子代理 C 定位 + 本方复核 SHA `c289a1cd…cf96`
- **建议**：AGENTS.md 属受保护 overlay，**本轮不改**；请操作者在允许时单独更新该链接（属 AGENTS 变更，不影响候选受审内容）
- **阻断性**：否

### R07-06【信息·口径更正】"12 个 ensure_ascii=False"＝10 处直参 ＋ 2 处 BinOp 载荷

- **位置**：`packages/engine/tests/` 全树 39 处 `write_text` 中，载荷含 `ensure_ascii=False` 的 12 处
- **触发**：无（事实口径）
- **影响**：不改变结论；12 处**全部显式 UTF-8**
- **证据**：E8 —— 首参恰为 `json.dumps(..., ensure_ascii=False)` 者 **10** 处；另 **2** 处首参是 `json.dumps(..., ensure_ascii=False) + "\n"` 的 BinOp 载荷（`test_mainline_postwrite_rows_budget.py:261`、`test_mainline_postwrite_text_budget.py:200-214`，encoding 在 214 行）。原报告称"多出的 2 处是更深的嵌套／间接变量"不准确，已更正。测试树 `json.dumps(ensure_ascii=False)` 全树共 **23** 处（另一分母，勿混用）
- **建议**：固定表述为"39 处 write_text＝19 显式 UTF-8 ＋ 20 默认；载荷含 ensure_ascii=False 者 12 处（10 直参 ＋ 2 BinOp），全部显式 UTF-8"
- **阻断性**：否

### R07-07【信息·边界补强】剩余 20 处无显式 encoding 的 `write_text` 当前不产生 cp1252 编码错误

- **位置**：测试树 20 处默认 encoding 的 `write_text`，真实分布为 `test_mainline_manual_input_rejection.py` **13**、`test_mainline_read_work_budget.py` **5**、`test_mainline_postwrite_admission.py` **1**、`test_mainline_dispatch.py` **1**（原报告写 14+5+1+1 有误，已更正）
- **触发**：Windows cp1252 环境执行测试
- **影响**：这 20 处首参一律是使用默认 `ensure_ascii=True` 的 `json.dumps(...)`，输出为纯 ASCII，当前不会产生 cp1252 编码错误；**但这不构成"全部编码风险已关闭"或"全 Windows 无编码风险"的证明**（未来新增 `ensure_ascii=False` 或直接写入非 ASCII 字面量即重新引入；且本次未在 Windows 实跑）
- **证据**：E8（AST 判定首参是否含 `ensure_ascii=False`）
- **建议**：维持"窄修复"定位；不建议扩大改动面（改 20 处属无实质收益的扩散），但应把"新写 trace 一律显式 `encoding="utf-8"`"写入测试约定
- **阻断性**：否

### R07-08【信息·更正】R05 的"原 28 笔 Read 映射"是条款级映射＋笔段定位，不是逐笔清单

- **位置**：`docs/reviews/T02/fr200-fr201-20261024/round-05/fr200-fr201-original-clause-evidence-map.md`
- **触发**：引用该证据时
- **影响**：把"28 笔"说成"逐笔 28 行实际 Read 清单"会夸大证据粒度
- **证据**：该文第 10、42 行及各条款行的笔段定位引用
- **建议**：后续引用统一表述为"四类表单 28 笔实际 Read／CRUD 已覆盖（条款级映射＋笔段定位）"
- **阻断性**：否

### R07-09【信息·更正】O047 "build 四项 byte-exact" 的正确读法是"5 项中 4 项相等"

- **位置**：`outputs/20261025_t02_raw_report_format_repair_047/final-source-build.json`（5 项）与 `before.json`／`after-fullcheck.json`
- **触发**：引用构建证据时
- **影响**：把"四项"读成"只有 4 个构建产物"会与实际 5 项不符；正确表述为"5 个构建产物中 4 项前后 byte-exact，仅 `apps/desktop/out/main/index.js` 因 dev nonce 变化"，且 GUI 前后 5/5 全等。**边界**：这是**文件身份**，不是内存模块哈希、不是 serve/HMR 执行证明、不是新包证明；旧 094 包的有界旧身份不因此升级
- **证据**：E9（24 字符 nonce 字段内 23 个字节不同）
- **建议**：统一按 5 项口径表述
- **阻断性**：否

### R07-10【信息·已对账】ruff format 计数与候选集合的 4 份差已定位为 base 既有的 4 条排除

- **位置**：`ruff format --check .` 的"files already formatted"计数；`pyproject.toml` base 已有的 4 条 `[tool.ruff.format].exclude`（T01 四个冻结生成脚本，均为 tracked `.py`）
- **触发**：把 O041/O047 的 386／379 与工作区可格式化候选数逐一对账
- **影响**：不影响任何结论；原报告记为"无法确认"的 4 份差已定位并闭合
- **证据**：E14 —— 831813c6：tracked 可格式化 384（py 109 + md 275）＋ 6 未跟踪 round-01/02/03 = 390 − 4 既有排除 = **386**；b215f543：390（py 109 + md 281）＋ 6 = 396 − 4 − 13 新模式 = **379**。两次与实测计数逐一吻合。**边界**：扩展名计数与 ruff 的发现／选择集合不必然完全等价；且数字吻合本身**不**证明"差 7 完全由 7 份 tracked 报告引起"这一因果表述成立——本报告因此不在任何位置使用该因果说法（见 E14/V19 与 §8.3 MM04）。本轮亦未、亦不需要新跑 ruff
- **建议**：引用计数时使用 E14 的分解口径；不再使用"差 7 由 7 份 tracked 报告引起"的因果表述
- **阻断性**：否

### R07-11【低·观察】FR-201 实例事实编辑歧义判定被放宽，须以既有 ADR 政策为准而非新合同

- **位置**：`apps/desktop/src/renderer/src/ontology/mainline-facts.ts:20-37`（`manualFactPlan`）
- **触发**：同一槽位存在多值事实时执行"编辑"
- **影响**：判定由"同槽活跃事实数 ≠ 1 即拒"改为"存在其它同槽记录且其对象 ≠ 原值/新值且无 owner/sourceRow/managed_value 时放行"。**更正**：该函数处理的是 `domain.state.facts` 中的**实例事实**，属 **FR-201 实例事实编辑**，不是 FR-200 类/属性定义表单。语义上：同槽其它人工值可并存或被墓碑；owner/sourceRow/managed 支撑的受管记录、重复的原值/新值编辑目标、与定义重叠的值均被拒；原记录真实 ID 保留；**不接管映射所拥有的事实**——与 ADR-0002 第 27 行同向，属语义澄清而非新增能力
- **证据**：本方实读该 diff 与 ADR-0002 第 27 行原文；O047 原六例 GUI 含多值/删除影响用例
- **建议**：在合并说明中显式记这一处口径澄清，避免被读成"放宽到可接管他人事实"
- **阻断性**：否

### R07-12【低·观察】引擎运行时依赖改为 vendored 补丁 wheel，供应链 HOLD 不因此解除

- **位置**：`packages/engine/pyproject.toml`（`rdflib==7.6.0+ontolearn.fr201.3`，`[tool.uv.sources]` 指向 `vendor/rdflib/*.whl`）、`packages/engine/vendor/rdflib/{PROVENANCE.json,notation3-input-types.patch}`、4 个 wheel、`scripts/repack-rdflib-input-types.py`、`uv.lock`
- **触发**：任何引擎安装/打包
- **影响**：这是让"已知语法错误 vs 未知解析失败"可区分（`BadSyntax`/`Notation3InputError` vs 泛化 ValueError）的机制来源，直接支撑 D8 "不按异常文案分类"的实现方式；但引入了本地补丁 wheel 的供应链面（upstream 615416 B 整件、fr201.3 2379774 B 整件/STORED、透明 parser 补丁确改内容），原始供应链审计 HOLD 仍在
- **证据**：`git diff` 实读、`licenses/NOTICE` 变更、`packages/engine/vendor/rdflib/PROVENANCE.json`
- **建议**：保留既有供应链 HOLD 与体积计量分层表述（整件 / 解压量 / 压缩 payload 分开），不得称"仅压缩且内容完全相同"
- **阻断性**：否

### R07-13【低·维护项】`contracts/src/index.ts` 的 TS 数值类型范围宽于 zod schema（非绕过，非阻断）

- **位置**：`packages/contracts/src/index.ts`（`project.ownership.detail` 第二变体，允许 `startOrdinal:0` 且 `pageSize` 无上界）vs `packages/contracts/v2/schema.json`（要求 `startOrdinal ≥ 1`、`pageSize 1..64`）
- **触发**：调用方以越界组合构造分页参数
- **影响**：当前唯一调用方 `mainline-ownership.ts:19-36` 组合合规；越界会在引擎边界 `engine.ts:1241` 被拒为 invalid，**不构成实际绕过**；属既有风格一致问题，非本次回归
- **证据**：本方实读 `contracts/src/index.ts`、`schema.json`、`mainline-ownership.ts` 与 `engine.ts` 边界校验
- **归口与事件窗口**：契约 owner（I01 契约线）在下次触及该类型时统一收紧；**本轮不改代码、不改测试**，也不据此新增验收
- **阻断性**：否（维护项）

> 说明：本条原先以"另记"形式存在，现按"每条发现须可独立识别"的要求补齐编号与归口；编号顺序不代表严重程度排序。

---

## 6. Top 10（按严重程度排序）

**先说边界**：本候选范围内**未发现**数据泄露、资金损失、服务中断级缺陷。该产品为本地优先桌面应用，本轮范围内不存在账号体系、计费、多租户、对外 HTTP 服务与模型外发，故上述类别的多数条目天然不适用。以下是本轮最值得处理的 10 项，**全部非 push 前技术阻断**，其中 R07-04 是 merge 前条件。

1. **R07-04（条件）** 状态源未记录 b215 当前事实 → merge 前必须由唯一维护者追加，不得改写历史前缀。
2. **R07-11（低）** FR-201 实例事实编辑歧义判定放宽 → 合并说明中显式记口径澄清，避免被读成可接管他人事实。
3. **R07-12（低）** vendored 补丁 wheel 的供应链面 → 保留供应链 HOLD 与体积分层表述。
4. **R07-03（低）** ruff format 与 prettier 的 Markdown 策略不一致 → 后续新候选统一，避免再因评审文档触发 CI。
5. **R07-02（低）** 排除模式不覆盖未来 `-rN` 命名 → 新增同类 raw 时同步新候选扩展 literal。
6. **R07-05（低）** AGENTS.md 的 M0 计划链接失效 → 请操作者单独更新（属 overlay，不影响候选）。
7. **R07-13（低·维护）** TS 数值类型范围宽于 zod schema → 契约 owner 下次触及该类型时收紧；当前唯一调用方合规，非绕过。
8. **R07-07（信息→约定）** 20 处默认 encoding 的 `write_text` 依赖 `ensure_ascii=True` → 把"新写 trace 必显式 UTF-8"写成测试约定。
9. **R07-06（信息）** "12" 的口径（10 直参 ＋ 2 BinOp） → 统一表述，避免证据夸大。
10. **R07-08（信息）** R05"28 笔"实为条款级映射＋笔段定位 → 统一表述，避免夸大证据粒度；FR-200 四类 28 笔 GUI 语义覆盖与范围不后移。

（按要求不省略其他阻断：**R07-01 为已核验通过项；R07-09（build 口径）与 R07-10（计数对账）已闭合为事实更正项，不再占用 Top10**；以上 10 项之外**无 push 前技术阻断**，详见 §10。编号不表示严重程度排序。）

---

## 7. 原 160 项清单逐项裁定

判定口径：**适用**＝本轮范围内确需且已核；**部分**＝部分适用、部分缺证；**本轮范围外**＝属其他 FR／迭代或后续里程碑；**不适用**＝该产品形态下无此面；**无法确认**＝本轮证据不足。每项一行，依据与缺口同行给出。清单原序与文字取自封存 prompt 内嵌原文，未改写。

| # | 判定 | 依据与缺口 |
|---|---|---|
| 1 | 部分 | 有既定 schema（SQLite format3 + `contracts/v2/schema.json` zod 严格 schema），非即兴建表；**与"第二个客户"（#29／#149）问题不同、须分开看**：本项问"是否有人设计过 schema"，#29／#149 问"面对第二个客户能否存活"；缺口：未对第二个客户做变更冲击验证 |
| 2 | 不适用 | 本地单机桌面应用，无账号体系与邮箱标识 |
| 3 | 不适用 | 无账号／无密码重置流程 |
| 4 | 不适用 | 无 MFA 面 |
| 5 | 部分 | 有引擎会话标识（engineSessionId／hostClientId）与 mainline 租约、close/hold 语义；缺口：无"用户会话超时"与"一键吊销用户全部会话"的业务面（本地单用户） |
| 6 | 不适用 | 无 SSO/对外身份提供方 |
| 7 | 不适用 | 无 SAML |
| 8 | 不适用 | 无 SCIM、无员工生命周期 |
| 9 | 部分 | 权限以固定错误码集合、方法白名单、owner/proof 绑定表达，非"角色表"；缺口：明确无角色层级模型（MVP 不需要） |
| 10 | 部分 | 横向越权面被多层约束：`selected.projectId` 必须相等、主进程注入 projectId、ownership proof 绑定 project/generation/store/lease、未知 detailRef 返 NOT_FOUND；缺口：单项目本地应用，无多用户对照场景 |
| 11 | 不适用 | 单租户本地应用，无跨客户数据面 |
| 12 | 不适用 | 无支持人员 impersonation 面 |
| 13 | 不适用 | 无登录面 |
| 14 | 不适用 | 无登录锁定面 |
| 15 | 部分 | 有 format2→format3 前滚迁移（`actual_format` 校验、`_migrate_query_payloads`、写租约）；缺口：未实现数据库级"回滚迁移"路径 |
| 16 | 部分 | 写事务有准入与租约；缺口：#16 保留——启动期单写者不证迁移不锁主表 |
| 17 | 部分 | 有 SQL 读取路径与预算守卫；缺口：无索引证据，也未做 5M 行规模验证（容量 HOLD 保留） |
| 18 | 本轮范围外 | SQLite 单连接（`store._db`）无连接池；本地单进程无流量尖峰耗尽问题 |
| 19 | 部分 | 引擎有 `backup_path` 概念；缺口：无夜间备份调度（无服务器） |
| 20 | 部分 | 有备份路径；缺口：无"从备份恢复"的已验证演练证据 |
| 21 | 不适用 | 无 PITR 设施 |
| 22 | 适用 | ADR-0002 墓碑语义：删除手工事实或为受管事实置墓碑，保留初始 ID，不物理改写历史；已实现 |
| 23 | 适用 | 引擎侧强制 canonical（`term(value).n3()` 精确相等）+ `contracts` `.strict()` + 引擎 contract validate；已实现 |
| 24 | 本轮范围外 | P0 无时间语义与提醒（行为轮次属 FR-602/附录 E 后续） |
| 25 | 部分 | 无姓名字段；字符串值经 JSON 转义与 canonical 校验，FR-200 示例含中文/英文标签；缺口：无"撇号姓氏"专门用例 |
| 26 | 部分 | 语言标签与非 ASCII 字面量有正控与受控拒绝：**正控 canonical 为小写 `de-ch-1901`／`en-001`**；`de-CH-1901` **语法合法但非 canonical，属受控拒绝**（原报告把它写成正控，已更正）；缺口：RTL 与 emoji 无用例 |
| 27 | 不适用 | 本产品无金额金额语义（金额/计费不属本产品范围） |
| 28 | 不适用 | 无币种与税 |
| 29 | 部分 | 分层数据模型（本体定义/断言事实/当前推导/场景副本/历史运行）与版本化 schema 已设计；缺口：未做第二个客户变更演练 |
| 30 | 适用 | ADR-0002：同 operation/job/计划重试返回原标记、不重复写入；已实现 |
| 31 | 部分 | 单值槽位与所有权冲突有确定性拒绝；缺口：#31 保留——受控拒绝后的 FullRead 不变与 preview 围栏不证"四连点去重" |
| 32 | 部分 | 分页有 `pageSize 1..64`、`startOrdinal 1..511`、总字节上限与游标；缺口：#32 保留——只证明实际已测页，未证第 400 页 |
| 33 | 本轮范围外 | FR-203 导入导出未实现（PRD 明确）；不得据此称导出已完成 |
| 34 | 本轮范围外 | ADR-0002 明确映射计划由未来业务层实现，"不能称为 CSV 映射能力已完成" |
| 35 | 不适用 | 无保留期合同与自动删除面 |
| 36 | 适用 | 本地优先、引擎不持密钥、不调用模型、错误只回传固定码与受限参数；仓库内未发现凭据；已实现 |
| 37 | 不适用 | 当前无长期密钥面（模型外发 S3 前不接入） |
| 38 | 适用 | vendored wheel + `PROVENANCE.json` + `uv.lock` pin + 哈希钉；已实现 |
| 39 | 部分 | Dependabot weekly npm/actions 真实存在；缺口：该 yml 无 pip/uv 条目，本轮未证漏洞扫描配置，不能据此断言平台安全告警绝对不存在 |
| 40 | 部分 | 用户可输入处在引擎侧受控校验（canonical 精确匹配、非法语言标签与超大整数有专类错误）；**边界**：已测的是手工事实输入路径，**不闭合**早期 definitions 在 preview 内 `Store.commit` 的坏 wire（OPEN，见 D3），也不代表全部产品输入面已覆盖 |
| 41 | 部分 | 用户**值**参数化绑定，与受控的**动态 SQL 标识符**（表名/列名按 PRAGMA 结果加引号构造）并存——不得简化为"全仓无任何 SQL 拼接"，也不构成 OWASP 认证；renderer 无 `innerHTML`/`dangerouslySetInnerHTML` 等 sink；缺口：无 CSRF 场景（无 cookie 会话），无系统化 OWASP 验证 |
| 42 | 不适用 | 无文件上传面（#41 类上传扫描问题不适用） |
| 43 | 不适用 | Electron 本地应用、无对外跨源服务；跨源面由 CSP 与 `csp.ts` 唯一配置源承担 |
| 44 | 适用 | `csp.ts` 为唯一配置源，生产 `script-src 'self'`，无 `unsafe-eval`，本候选未触碰 `csp.ts`；已实现 |
| 45 | 部分 | 无网络传输面（本地优先）；缺口：本地 SQLite 无静态加密、无密钥擦除策略 |
| 46 | 适用 | Agent 只产草稿并调用白名单工具、不自动确认自己的修改；凭据只在主进程且本阶段未接入模型；已实现 |
| 47 | 部分 | operation/job/marker 提供"谁在何时改了什么"的审计骨架；跨边界只传**固定错误信封**（固定码 + 不透明 ID），不记录凭据／原始异常／路径——**边界**：新增的 ownership detail 是**受限类型化定位载荷**，含槽位 S/P、owner、sourceRow 与事实 ID（`job_store.py:_persist_ownership_detail`、schema `ownershipDetailDocument`），并非"全部只有不透明 ID"；缺口：查看侧审计（who viewed）未实现 |
| 48 | 本轮范围外 | 渗透测试保留 HOLD，本轮未做 |
| 49 | 本轮范围外 | 无对外企业安全问卷交付物 |
| 50 | 不适用 | 无对外产品与安全披露面 |
| 51 | 部分 | 本地单机无生产凭据面；缺口：本地库无加密/无失窃擦除流程 |
| 52 | 不适用 | 无 SOC 2 交付物 |
| 53 | 部分 | 本候选范围内无患者数据面；**边界**：功能缺失不能认证现实世界中绝无个人/患者数据，相关法律适用性属未验证范围，保留法律/隐私 HOLD |
| 54 | 部分 | 本候选范围内无 BAA 供应商关系；**边界**：同 #53，功能缺失不等于可认证不存在法律关系或供应商合同义务 |
| 55 | 部分 | 有"谁改了什么"审计；缺口：查看审计（who viewed）未实现 |
| 56 | 不适用 | 无卡数据与 PCI 面 |
| 57 | 部分 | 本候选无个人数据主体与删除请求流程面；**边界**：功能缺失不能认证现实世界中不存在个人数据或删除请求义务，法律/隐私适用性保留 HOLD 且范围未知 |
| 58 | 不适用 | 无数据驻留合同面（本地优先、单用户） |
| 59 | 不适用 | 无季度访问复核流程（无用户角色体系） |
| 60 | 部分 | CI 单 workflow 三平台（macOS/Windows/ubuntu）共用同一检查；缺口：无独立 dev/staging/prod 环境 |
| 61 | 本轮范围外 | 无生产基础设施（本地应用）；CI 侧 action 以 SHA pin，接近可复现但非 IaC |
| 62 | 适用 | `npm run check`（lint/format:check/typecheck/vitest/build/engine:check）在 CI 内先于发布步骤；缺口：当前该 pipeline 在 b215 上尚无 CI 结果 |
| 63 | 部分 | 有 git 分支/PR 流程与提交可回退；缺口：无产品级一键回滚 |
| 64 | 不适用 | 本地桌面应用无停机窗口概念 |
| 65 | 部分 | 能力由 profile/registry（business3）与方法白名单控制；缺口：无通用特性开关 |
| 66 | 不适用 | 无弹性伸缩面 |
| 67 | 不适用 | 无 CDN 面 |
| 68 | 不适用 | 无自有域名/DNS/证书签发面 |
| 69 | 适用 | `job_store`/`coordinator`/worker 提供后台作业与持久 job；已实现 |
| 70 | 部分 | 有作业终态与恢复/对账路径（`marker(project,operation)`）；缺口：未证退避重试策略的具体形态 |
| 71 | 部分 | 失败/取消终态保留且不与成功混显；缺口：#71 保留——非完整 DLQ 重放 |
| 72 | 不适用 | 无 cron 调度面 |
| 73 | 适用 | 失效规则来自 `invalidation-v2.json`，同事务版本递增与 stale/current 更新；缺口：FR-200 GUI 编辑后的四类具名下游未逐类实测（见 §9） |
| 74 | 不适用 | 无事务性邮件 |
| 75 | 不适用 | 无邮件发送面 |
| 76 | 部分 | 本地数据目录可控；缺口：无生命周期/保留清理策略 |
| 77 | 本轮范围外 | 本产品无计费与模型消耗面（模型外发 S3 前不接入），无成本告警义务 |
| 78 | 本轮范围外 | 灾难恢复演练保留 HOLD |
| 79 | 不适用 | 无多区域合同 |
| 80 | 部分 | 证据与 job DTO 为结构化 JSON，可离线检索；缺口：无集中式可检索日志平台（#47/#80 观察） |
| 81 | 不适用 | 无外部错误聚合服务 |
| 82 | 不适用 | 无外部探活面（本地应用） |
| 83 | 不适用 | 无值班呼叫面 |
| 84 | 不适用 | 无监控面板面 |
| 85 | 部分 | 实际形态为 **Electron 应用进程 + Python 协调器/引擎的多进程本机逻辑服务**（非单进程），跨边界有 operation/job/marker 链路与 engineSessionId 绑定；缺口：无分布式 tracing |
| 86 | 本轮范围外 | 无对外值班轮转面 |
| 87 | 部分 | `AGENTS.md` + 迭代设计与验收文档构成运行手册；缺口：无"queue depth critical"式运维术语手册 |
| 88 | 适用 | R04–R06 的 disposition 逐意见事实处置与独立 HOLD 登记构成事后复盘机制；已具备 |
| 89 | 不适用 | 无对外状态页 |
| 90 | 部分 | 引擎 3769 收集/3719 PASS、TS 39 文件 1892 PASS 单测充分；缺口："作者已知逻辑"不可核，且全部通过数依赖操作者运行证据（读回），本轮未重跑 |
| 91 | 不适用 | 无第三方 API 依赖（rdflib/pyshacl 为库，非外部服务） |
| 92 | 部分 | 有真实 E2E（FR-200/201 六例 GUI 流程，自然 0、6 PASS）；缺口：非注册/结算类流程 |
| 93 | 部分 | 有读/写预算与准入守卫（validation_rows/bytes/work）；缺口：无负载压测证据（容量 HOLD 保留） |
| 94 | 适用 | 夹具为固定样例与合成数据，非生产数据；已符合 |
| 95 | 适用 | 新增 6 个引擎回归测试文件 + 多个 TS 回归测试，覆盖语言标签、超大整数、postwrite 准入、rows/text/read 预算；已实现 |
| 96 | 部分 | 历史异平台证据已存在：Ubuntu（Quality job）与 macOS（Desktop job）CI 均有实际成功记录，Windows 为另一平台证据（尚未对 b215 绿）；**缺口**："老旧电脑"问题本身仍未实测——无参考设备、低版本环境或老旧硬件的验证，且 b215 无任何跨 OS／参考硬件证据 |
| 97 | 部分 | 新增视图使用 `aria-label`、`dl/dt/dd` 结构与 `role=status` 断言；缺口：无系统化无障碍合规审计 |
| 98 | 不适用 | 无订阅计费 |
| 99 | 不适用 | 无付款失败与催缴 |
| 100 | 不适用 | 无发票 |
| 101 | 不适用 | 无销售税/VAT |
| 102 | 不适用 | 无退款 |
| 103 | 不适用 | 无用量计费 |
| 104 | 不适用 | 无年度合同条款 |
| 105 | 不适用 | 无收入报表 |
| 106 | 不适用 | 无 webhook 对外发送 |
| 107 | 不适用 | 无 webhook 重试与投递日志 |
| 108 | 适用 | `protocolVersion=3` + `contracts/v2` 版本化契约 + registry 哈希钉；已实现 |
| 109 | 不适用 | 无对外 API key |
| 110 | 部分 | 有引擎侧读/写预算与准入（准限流）；缺口：无对外 API 租户级限流 |
| 111 | 部分 | `PROVENANCE.json` ＋ `scripts/repack-rdflib-input-types.py` **已记录**技术来源、重打包方式与校验过程；缺口：**升级治理、时限与演练仍未知**（上游 7.6.0 之后的上游变更应对流程未成文），不得由"有来源记录"推出"有升级治理" |
| 112 | 不适用 | 无 OAuth 令牌 |
| 113 | 不适用 | 无对外集成沙箱 |
| 114 | 本轮范围外 | 模型外发 S3 前不接入，本轮无字段进入模型；本地优先架构下不启用模型/遥测 |
| 115 | 部分 | 当前架构下引擎不持密钥、不调用模型、无数据出网路径；**边界**：这是本候选的实现事实，不等于可认证现实部署中绝无个人/患者数据出网，法律/隐私适用性保留 HOLD |
| 116 | 不适用 | 无模型接入与计费 |
| 117 | 本轮范围外 | 无模型接入，模型评测不适用（与 PRD 的"固定模型"属 M0 路线另一议题） |
| 118 | 不适用 | 无模型提供商 |
| 119 | 不适用 | 无模型弃用迁移 |
| 120 | 不适用 | 无模型提示/输出日志（本地证据日志另计） |
| 121 | 适用 | 确定性结果只来自真实引擎；Agent 只产草稿并调用白名单工具，不自动确认自己的修改；已实现（架构不变量） |
| 122 | 本轮范围外 | 本地桌面应用无"酒店 Wi-Fi 下加载网页"面；等价面为"离线可用"，本地优先已满足 |
| 123 | 部分 | 有加载/失败降级（ownership detail 失败降级为 unavailable、空态与状态提示有断言）；缺口：全屏逐屏空态/加载态/错误态未系统清点 |
| 124 | 部分 | 固定错误码 + 中文可操作提示；**更正**：GUI 实测中 42 条 INVALID_REQUEST 共用**同一条固定中文提示**（`操作未能完成：INVALID_REQUEST。请核对当前项目或查询原操作；已输入内容保留。`），OWNERSHIP_CONFLICT 为另一条独立提示（`tests/e2e/t02-fr200-fr201.spec.ts:767-770`）；引擎内部的 typed category 分类**不证明** UI 文案按语言标签/整数/canonical 分类，也不据此提出新的文案分类要求 |
| 125 | 部分 | 受控拒绝后保持原 ID 编辑链、状态不变；**表单字段保留已被实测断言**：`spec:762-775` 以 `toHaveValue` 断言 S/P/O 在拒绝后保留（含 4301 输入），O047 实测通过；缺口：并非所有产品表单都已逐项评估（只覆盖 FR-201 相关表单） |
| 126 | 不适用 | 无邮件发送 |
| 127 | 不适用 | 无推送通知（本地应用） |
| 128 | 部分 | **更正**：Undo **UI 现已存在**——`OntologyMainlinePage.tsx:401-404` 暴露"预览撤销本次修改"按钮，`mainline-session.ts:393-400` 的 `prepareUndo` 重新读取新基准后以 `intent:'undo'` ＋原 `operationId` 准备；旧 ADR 的"此次不实现产品撤销 UI"是 spike 期历史表述，不再描述当前代码。缺口：Undo 路径未被本轮六例 GUI 证据覆盖 → **UNTESTED／HOLD**；存储层的墓碑与变更证据是撤销基础，但**不构成父 FR 闭合** |
| 129 | 部分 | 新增视图与既有界面使用 aria-label/role/status；缺口：无完整键盘导航与读屏审计证据 |
| 130 | 部分 | 多语言标签按字面量保留（附录 C）；缺口：无 locale 日期/数字格式化层与 UI 国际化 |
| 131 | 本轮范围外 | 桌面应用无浏览器后退；窗口恢复属 I02 另一迭代 |
| 132 | 部分 | 分层命名、注释与 ADR 记录设计意图；缺口：规模信息不推可读性结论，未做可读性专项 |
| 133 | 部分 | 本候选每轮经指定双模型独立审查 + CI 门禁 + disposition 逐意见处置；**边界**：历史工作流的存在**不等于 b215 已 CI 绿或已合并**（b215 未 push、PR16 open、远端 feature 仍 330） |
| 134 | 部分 | 独立 worktree + feature 分支 + PR 合回 + 不强推共享分支的**流程已建立并实际使用**；**边界**：同样不等于 b215 已 CI 绿或已合并 |
| 135 | 部分 | Dependabot weekly npm/actions 真实存在；缺口：pip/uv 侧无同机制证据 |
| 136 | 部分 | action 以 SHA pin、依赖有精确版本与双锁文件；缺口：无框架大版本升级策略成文 |
| 137 | 无法确认 | 本轮无死代码度量证据；不以"未见"充当"已清理" |
| 138 | 部分 | 引擎已按 project/ 域拆分（mainline、storage、job_store 等）；缺口：未做文件规模治理专项，且规模不推正确性 |
| 139 | 适用 | ADR-0001/0002/0003 + M0 计划真实归档 + 每轮 disposition 记录理由；已实现 |
| 140 | 部分 | `README.md` 存在且含本地运行入口；缺口：本轮未验证"新工程师 1 小时内跑起来" |
| 141 | 适用 | `docs/iterations/**`（设计/验收/证据）+ `docs/reviews/**` + `AGENTS.md` 构成交接文档；已实现 |
| 142 | 不适用 | 无对外运营团队 |
| 143 | 不适用 | 无对外客户成功面 |
| 144 | 部分 | `docs/m0-checklist.md` 与 `docs/reviews/T02/status.md` 提供状态变更记录；缺口：无面向客户的 changelog |
| 145 | 本轮范围外 | 本候选无对外服务条款/隐私政策交付物（`SECURITY.md` 存在但不覆盖本项）；**边界**：功能缺失不认证现实合同/条款义务不存在，法律适用性保留 HOLD 且范围未知 |
| 146 | 部分 | 仓库与远端组织为 `NOmoreJoke/OntoLearn-Studio`，`licenses/NOTICE` 已记录 vendor 义务；缺口：公司资产（域名/账号/仓库）完全化不属代码可认证事项，且功能面缺失不认证现实中不存在相关合同/产权安排 |
| 147 | 部分 | 多 worktree、多 agent、双模型独立审查降低**流程**单点；**边界**：多 agent 不等于人的 bus factor 已被提高，实际知识集中度与人员备份未认证 |
| 148 | 部分 | 本轮对 88 叶全部差异做一手或委派实读并逐条复核；**边界**：ROOT 为自动 Codex 对话，非人类资深审查者，双 AI 独立审查**不等于**人类逐行签字；本报告只陈述证据界限，**不新增任何人类放行前置门禁** |
| 149 | 适用 | ADR-0002 为存储与事实身份主定义；已具备 |
| 150 | 部分 | R06 独立审查与 disposition 逐意见事实处置正是该机制；缺口："本轮未新增 bug"本身**不能证明**具备解释/修复回归的能力，机制有效性只能以历史轮次的实际处置记录为证 |
| 151 | 部分 | CI 三 job、package 流程与本地验收流程齐备；缺口：无生产运维与云账单面 |
| 152 | 不适用 | 无付款中断面、无对外 on-call |
| 153 | 部分 | Dependabot + action SHA pin + 依赖双锁；缺口：无漏洞响应 SLA 成文 |
| 154 | 部分 | 本候选无患者数据流；**边界**：同 #53/#54，功能缺失不能认证现实数据流与法律关系不存在，法律/隐私 HOLD 与未验证范围保留 |
| 155 | 适用 | 本轮独立复核（AST 对拍、glob 命中面、build/nonce 复算、124 针核对、CI 日志行核对）＋O047 的三份独立审计，即"不采信自称"；已执行 |
| 156 | 部分 | 迁移与提交有事务与格式校验；缺口：live DB 无锁迁移未证（#16） |
| 157 | 适用 | D8 四条禁止与范围限制被执行（不泛捕 ValueError、不按文案分类、不静默规范化、不升 cap）；本轮亦未新增功能；已执行 |
| 158 | 部分 | CI 覆盖三平台且本地全量通过；缺口：Windows 未对 b215 绿；**边界**：本地单机单用户环境下的通过**不等于**跨 OS、参考设备或多环境可靠性证明 |
| 159 | 部分 | 历史未知原因保留（旧 79F 缺栈、standalone EOF、未知退出码等一律标 OPEN 不强解），这是诚实的证据纪律；缺口：该纪律**不等于**已具备人类资深调试能力，相关人力能力未验证 |
| 160 | 适用 | ADR + 每轮 disposition + version-map 记录"为何如此"；已具备 |

---

## 8. 历史意见逐项现状（R06 及更早）

### 8.1 R06 ZCode P1–P8

| 项 | R06 处置 | 本轮现状（2026-10-26 独立复核） |
|---|---|---|
| P1 新 8318 Windows 缺证／旧 79F 全因未证 | 采纳；旧 79F 保留未知残留 | **维持**：b215 仍无 CI，旧 CI36 的 79F 仍无逐例首栈与最终表；新绿不得倒填旧因果 |
| P2 诊断参数与完整验收口径 | `--maxfail=1` 仅失败早停、无筛选；须全量口径 | **维持**：本方沿用同一口径，不把 diagnostic 标签当验收，不要求新增人工诊断例外 |
| P3 definitions 早期坏 wire | 采纳原 OPEN（preview 内 Store.commit 即失败，非 clean Diff 后才失败） | **维持 OPEN**：T01 原归口；本候选未触及该路径 |
| P4 ownership 通用定位 | typed witness 成立；裸旧 detail → INVALID_STATE → unavailable | **维持并已部分闭合**：本候选 `job_store._ownership_header` 显式区分"历史合法 detail"（→ INVALID_STATE）与"其它实际 detail 类型"（→ NOT_FOUND）；未接线家族仍 OPEN |
| P5 错误码集合（UI17/契约26/交集10/额外7/缺16） | 集合事实成立≠16 条当前可达 | **维持**：缺码仍为非阻断延期；本轮新增 `project.ownership.detail` 的码由 zod/schema 双向覆盖 |
| P6 SQL 无 ORDER BY | SQL 事实采纳，未升级为已证跨运行缺陷 | **维持**：本候选未触及 witness 选取顺序 |
| P7 canonical | 精确 `term(value).n3()` 政策继续；未来改政策才新人类决定 | **维持且已核**：`domain_changesets.preview_changeset` 强制 `parsed.n3() == value`，非规范别名 → INVALID_REQUEST；无静默规范化路径 |
| P8 规模/EOF/边界/状态/PATH | 按旧意见逐条区分 | **维持**：见 §8.3 |

### 8.2 R06 MiniMax D1–D12

| 项 | R06 处置 | 本轮现状 |
|---|---|---|
| D1 新 head 未 CI | 合并条件，非新源码缺陷 | **维持**：b215 未 push、无 CI；本方独立判断——这不构成本地源码缺陷，但构成 merge 前硬门禁 |
| D2 状态/历史 manifest | 历史 manifest 永久绑定当时 head；不改写伪装当前 | **维持且现需行动**：状态源最新追加节仍停在 831813c6，b215 事实待追加（R07-04），且只能追加不得改写旧前缀 |
| D3 definitions 时序 | 早期坏 wire → UNKNOWN/HOLD 仍 OPEN | **维持 OPEN**（T01 原归口） |
| D4 ownership 最终码 | 两分支最终均 OWNERSHIP_CONFLICT；裸旧 detail 无 witness/unavailable 成立 | **维持**：本候选新增了结构化 witness 与 detail 持久化，但"所有 ownership 家族接线"未完成，缺口保留 |
| D5 无序查询 | 不宣称不稳定已实测 | **维持**：未确认观察 |
| D6 standalone EOF | 两处裸索引残余属实，仍 OPEN | **维持 OPEN**：本候选未新增不经封装的 parser 入口 |
| D7 缺 16 码 | 集合事实≠当前可达 | **维持** |
| D8 两 TS PATH python | 仍真实存在；报告更正≠源码已修 | **维持**：本轮实测两处仍在（未复核具体行，见下"无法确认"） |
| D9 Ruff 计数 | 379/380/386 为真实运行计数，不推差因 | **维持并补记**：b215 下为 379；本轮已完成计数对账（E14/R07-10）：8318 ＝ 384 tracked ＋ 6 未跟踪 − 4 既有排除 ＝ 386；b215 ＝ 390 ＋ 6 − 4 − 13 新模式 ＝ 379。**仍不推差因**：数字吻合不单独证明"差 7 由 7 份 tracked 报告引起" |
| D10 D/E/G 与失效联动 | 承认本轮映射未覆盖 D/E/G；四类具名下游未逐类验 | **维持**：本轮独立复读确认——公共失效机制与 `test_storage` 九行正负例存在；FR-200 GUI 编辑→推导/保存查询/SHACL/报告四类下游仍未逐类实测，不得称"全部下游完成"，也不称"实现缺失" |
| D11 4299/4300 | 应用层缺该边界断言属未来维护；4301 拒绝与合法后继已有实证 | **维持**：本候选未升 cap |
| D12 正面结论 | 六 keyword AST、已通过本地运行、旧包身份按原资格保留 | **维持并独立复核**：AST 对拍 True/True（E7）；本地运行与旧包身份为读回证据，未重跑 |

### 8.3 R04/R05 的 35 个历史位置（逐条现状）

| 位置 | R06 处置 | 本轮现状 |
|---|---|---|
| R04 Z01 无序查询 | 未确认观察 | 维持；未触及 |
| R04 Z02 分页信封误因果 | 撤回；整文档/16MiB 预算另保 | 维持；未触及 |
| R04 Z03 definitions 早期 wire | OPEN | 维持 OPEN |
| R04 Z04 typed witness/裸 detail | 分开处理 | 部分闭合（见 D4） |
| R04 Z05 集合差与可达性 | 分开 | 维持 |
| R04 Z06 canonical | 继续既有政策 | 维持；本轮独立核验 canonical 强制点在 `domain_changesets.py` |
| R04 Z07 规模信息 | 不新增重构 | 维持 |
| R04 M01 归档→最终状态追加 | 历史演进，不矛盾 | 维持；b215 追加待办（R07-04） |
| R04 M02 无 hash 前提 | 不采；保留 PROVENANCE/多件审计 | 维持 |
| R04 M03 4299/4300 | 未来维护 | 维持 |
| R04 M04 standalone 残余 | OPEN | 维持 OPEN |
| R04 M05 早期 definitions | OPEN | 维持 OPEN |
| R04 M06 schema 与内容身份分层 | 非当前绕过漏洞 | 维持；**更正本轮原表述**：renderer 事实 ID 用 `TextEncoder` ＋ WebCrypto `crypto.subtle.digest('SHA-256', …)`（`mainline-facts.ts:75-81`）派生，与引擎 `digest([S,P,O])` 的跨端一致依赖"拒绝孤立代理项"（同文件 58-62 行），该依赖成立；手写 SHA-256 位于另一模块 `contracts/src/v2.ts`（见 R07-13），二者不可混同 |
| R04 M07 桶导出兼容 | 不缩导出面 | 维持 |
| R05 Z P1 | O040 定因，不追认旧 79 全因 | 维持 |
| R05 Z P2 | 934 Quality 含 recovery 成功为新阶段证据 | 维持；不迁移成 b215 的 CI 绿 |
| R05 Z P3 | 早期 definitions OPEN | 维持 OPEN |
| R05 Z P4 | 通用定位合同 OPEN | 部分闭合 |
| R05 Z P5 | 缺码延期 | 维持 |
| R05 Z P6 | canonical 观察 | 维持；本轮独立核验该策略的实现点 |
| R05 Z P7 | 当时有效 pytest 选项已变 | 维持；**该条原含两部分**：①诊断参数（当时有效 pytest 选项已随时间变化）；②文件增长信息。本轮只作读回、未重跑；两部分均按原处分保留，不因本轮复核改写旧报告 |
| R05 Z P8 | 历史 aff 状态永久保留 | 维持；不覆写 |
| R05 MM01 | 首败假设被 O040 单栈部分超越 | 维持 |
| R05 MM02 | 新阶段事实，旧取消不抹除 | 维持 |
| R05 MM03 | 无新包，原 094 有界桥接 | 维持；b215 无新包制造、无包内重跑 |
| R05 MM04 | 入口追加与 Ruff 差因未知 | 部分补记（R07-10／E14：计数分解已对账为 386 与 379；**仍不推差因**，不写"差 7 由 7 份 tracked 报告引起"） |
| R05 MM05 | 缺码非阻断 | 维持 |
| R05 MM06 | 早期 definitions OPEN | 维持 OPEN |
| R05 MM07 | Manual/SingleDeclaration 真 witness 与裸族分开 | 本轮复核：`ManualOwnershipConflict`/`SingleDeclarationConflict` 均带 `witness` 且以 `category="ownership"` 构造；`storage.py:50-64` 的 category→code 映射表**确无 `ownership` 键**（未命中即默认 `INTERNAL_ERROR`），但 `job_store.py:617-636` 在 `except Conflict` 按 category 拦截——有 ownership proof 且 typed witness → 持久化结构化 detail，无 proof → 遗留裸 detail，**两出口最终都是 `OWNERSHIP_CONFLICT`**。故码表缺键不等于 ownership 类必然落 INTERNAL_ERROR；**但所有裸 ownership 家族仍未闭合，HOLD 保留** |
| R05 MM08 | SQL 事实未确认观察 | 维持 |
| R05 MM09 | wheel/体积分层 | 维持（R07-12） |
| R05 MM10 | AGENTS 为受保护 overlay | 维持；本轮只读不写（R07-05 仅建议） |
| R05 MM11 | locator 无 object 是最小定位边界 | 维持；本轮核 `witness` 只含 id/owner/sourceRow/slot，不含单元格原值 |
| R05 MM12 | 两 PATH python 仍在 | 维持 |
| R05 MM13 | 核心规模信息 | 维持 |

---

## 9. 未验事项与保留的 HOLD（本轮不得视为已闭合）

**本轮未能验证（不是失败，是未做）**：Windows 平台完整 3769 全集；Windows/macOS/Linux 三 job 真实 success；Quality packaged recovery 步骤自身 success；全部后继 typecheck/build/E2E/package/verify；b215 的任何 CI（b215 未 push）；b215 新包制造与新包内运行；旧 CI36 的 79F 逐例首因；`D8` 所指两处 PATH-python 测试的具体行号复核（子代理报告与 R06 结论一致，本方未逐行复读）；`docs/architecture/` 是否曾存在 M0 计划件（现不存在）；本轮未联网复核远端 PR16 实时状态（读回 O046 快照）；**ruff 的发现/选择集合是否与扩展名计数完全等价**（计数分解已在 E14 闭合，但 ruff 的实际选择集合未运行核验）；**Undo GUI 路径的真实运行结果**（UI 已存在但未纳入本轮六例 GUI 证据）。

**O046 的精确限定（不得被简化）**：三 job 的 **完整 3769 项 pytest 套件全部 NOTRUN**、全部后继 desktop/package 步骤 skipped；但 Quality job 在失败前**实际执行并成功**了 I04 矩阵 `144 passed in 21.89s`、typecheck（`tsc --noEmit`）、vitest `Test Files 39 passed (39)` 与三次 `built in`。因此"完整套件未运行"**不等于**"没有任何 Python／typecheck／build 运行过"。

**原样保留的 HOLD**：签名/公证/wholeApp 法律与 `_distutils`；跨 OS/参考设备/macOS15/Win11；Q5/D2 容量与旧超限库恢复；损坏 SQLite 物理资源保护（用户明确保留）；unknown parser/N3/Store/坏快照；**Undo GUI（UI 已存在、运行未验）**；未验 ownership 家族；native engine 与 named App 未知退出码；D3 早期 definitions wire；D4 裸 detail 家族；D6 standalone EOF；D8 两 PATH python；D10 四类具名下游（对比 9 条通用失效正负例）；D11 4299/4300 应用边界断言；供应链与 vendored wheel 审计；**法律/隐私/知识产权与现实适用性（功能缺失不构成"不存在"的认证）**；R06 两位作者的原始结论（ConditionalPass / verification-incomplete）作为独立历史事实保留。

**明确不成立的推论**：FullRead 逻辑相等不证物理 DB 零写；已知 PID 缺席不证全部自然退出；旧包身份不证新包；CRUD 通过不证全附录 C 或父 FR 完成；四类 CRUD 不自动证明附录 C 推理/解释/导出；局部 28 笔不证整 FR；"未验"不等于"实现缺失"；**错误码集合的 26/17/10/7/16 算术不等于全部当前可达**；**无 ORDER BY 是代码事实，不等于已证跨运行不确定性**；**O047 的 57 事务／43 拒绝／28 笔 FR-200 属有界验收，不证物理 DB 零写、全部 PID 自然 0、全附录 C 或全 FR／Goal／M0／发布完成**。

---

## 10. 最终整候选结论与条件

**结论：附条件通过（Conditional Pass）。**

- **本地实现是否通过**：**通过**。本轮对 **583c05c7 → b215f543** 全部 88 差异叶做了一手或委派实读与独立复核；未发现违反架构不变量（本地优先、渲染端隔离、CSP 单一来源、确定性/Agent 解耦、存储唯一真相、数据分层、失效规则来源、错误只传固定码）的实现；未发现 D8 四条禁止被违反（无泛捕 ValueError 的业务分类、无按异常文案分类、无静默规范化、无 cap 扩张）。
- **本地验收是否通过**：**通过（读回证据）**。O047 的完整 check 自然 0 与原六例真实 GUI 自然 0 证据齐备；本方复核了 build 5 项中 4 项 byte-exact 与 24 字符 nonce 差、CI 三 job 原始失败行、O047 四文件字节/SHA、状态文档当前时点内容。**本方未重跑任何产品/测试/构建**。
- **是否存在 push 前技术阻断**：**未发现**。本轮 13 条编号发现（R07-01…R07-13）全部为低/信息/维护级；其中唯一 merge 前必办项（R07-04）是文档追加动作，不是源码缺陷。
- **必须等 push 后真实 CI 才可 merge**：**是，且为硬门禁**。同一受审实现/测试/CI/依赖下，Windows 3769 全集每项须最终通过或原有有据条件 skip、自然 0、零失败/早停/取消/timeout/NOTRUN；全部后继 typecheck/build/E2E/package/verify 及三 job 真实 success；Quality packaged recovery 须步骤自身 success。`--maxfail=1` 仅失败早停、无筛选；未答复的旧 diagnostic fast-track 不构成批准。
- **不可提前宣称**：不得据本报告增 FR、不得称 Goal/M0/发布完成；整体合并可用仍为 **2/17**；PR16 仍 open 未合并；远端 feature 仍 `33059f82`、develop 仍 `583c05c7`。
- **若将来出现新绿**：只证明新 run，不倒填旧 79F 逐例原因；b215 当前事实由唯一维护者追加（R07-04），旧 manifest 与 R04/R05/R06 历史前缀不改写。

---

## 11. 本报告的证据界限与自限

- 本报告所有"本地实现通过"结论建立在**静态差异阅读 + 读回操作者证据 + 独立纯计算**之上；不含本轮任何产品运行结果。
- 160 项清单的判定是**适用性与证据充分性判定**，不是 160 项功能验收，也不构成新增需求；其中"不适用/不适用性"一律按产品形态给出理由，且**不把"功能缺失"当作可认证的"不存在"**；未用合规式 N/A 取消任何法律/平台/容量/隐私 HOLD。
- 本轮编号发现为 R07-01 至 R07-13：R07-01 为已核验通过项；R07-06/07/08/09/10 为事实口径更正与对账（R07-10 已由"无法确认"闭合为可对账）；R07-02/03/05/11/12/13 为低/维护/观察项。**未凑数、未新增无用功能建议、未因编号推导任何放行结论**。
- 本方未读取本轮另一方报告正文；目录操作中见到文件名/字节/mtime 等元信息已如实声明，未据此反推已读正文。本轮事实包亦**未随附任何同行材料**，本方也未索取。
- 本轮仓库内唯一写入为本文件 `docs/reviews/T02/fr200-fr201-20261024/round-07/minimax-m31flash.md`；未新增其他报告文件，未覆盖操作者历史副本，未修改源码/测试/配置/依赖/构建/旧报告，未触碰 git index 与远端。

---

## 12. 事实包收据与本次唯一修订记录

### 12.1 收据（实际接收，非 UI 附件）

- 传输方式：**本地绝对路径引用** `/tmp/t02-r07-minimax-facts-8dfb706dcee9.txt` ＋ **本方实际读取**（`read` 完整读取至 EOF，末行以 `EOF.` 结束）。
- 实测原件：**11096 B**，SHA256 `8dfb706dcee9197ce6198166d1ad92838129a7c0935554134abafe28fb48bc73` —— 与随附声明**逐字一致**。
- 首份自然报告原件：**57131 B**，SHA256 `ce4b1ae7121d97a003de22e656730ef7f685b32df148707bc3245a974ce6b8c8`（该副本独立保留，未被覆盖）。
- 适用身份：原会话 `mvs_8d66d37640404c25bc061bffe6311b0b`，MiniMax-M3.1-Flash / xhigh。本轮**未新建任务、未新建模型、未新建报告文件**。

### 12.2 本次唯一修订的内容（一次、原地、同一文件）

在**原报告同一文件**内完成一次事实修订，**结论、附条件通过判定、无 push 前技术阻断判定、merge 条件与全部 HOLD 均未改动**。逐项处置：

| 事实包条目 | 处置 | 落点 |
|---|---|---|
| A01 merge-base／base 区分 | **已采纳并实测**：本地 develop 实为 `5f910b52`（过期 ref），`merge-base(HEAD, 本地 develop) == 5f910b52`；显式基线 583 经 `--is-ancestor` 独立验证为 head 祖先。原报告"merge-base == base"表述**错误，已更正** | §1 base 行、E3、V1 |
| A01 "b215→head" 笔误 | **已更正**为 `583c05c7 → b215f543` | §10 |
| A01 marker 段口径 | **已更正**：原 11257 B 比较口径错误；实测 marker→EOF 恰 11255 B、单次出现、起始 byte 17462、无末尾换行 | §1、§3.1 E2、V18、V21 |
| A01 marker 段摘要 | **限定采信**：长度/偏移/单次出现可复现；所载 63 位十六进制值实为同段 **SHA256** 去掉首位 `1`（算法标签与首字符有误），本方实测 SHA1 为 `8b6861f3…e7` | V21、E2 |
| A02 write_text 计数 | **已采纳并实测**：20 处默认者的真实分布 13+5+1+1；12 ＝ 10 直参 ＋ 2 BinOp（rows_budget.py:261、text_budget.py:214），全部显式 UTF-8；23 处为另一分母 | R07-06、R07-07、E8、V9 |
| A02 边界 | **已采纳**：不构成"全 Windows 无编码风险"证明 | R07-07 |
| A03 计数因果 | **已采纳**：删除"差 7 恰由 7 份 tracked 报告引起"的因果表述；保留 386／379 与分解 | R07-10、D9、MM04、E14、V19 |
| A03 对账 | **本方独立闭合**（超出事实包）：4 份差定位为 base 既有 4 条 `format.exclude`；384+6−4=386、390+6−4−13=379 逐一吻合；仍保留"ruff 发现/选择集合未运行核验"的边界 | E14、R07-10、V19 |
| A03 现盘 15 份 | **已限定**：现盘含后续报告，不否定当时的 13 份；不据此改写历史测量 | R07-01/E6 边界 |
| A04 renderer digest | **已采纳并实测**：WebCrypto `crypto.subtle.digest`（75-81 行），非手写 SHA-256；孤立代理项拒绝在 58-62 行 | R07-11、M06、E15 |
| A04 错误码表 | **已采纳并实测**：`storage.py:50-64` 无 `ownership` 键，但两个 ownership 子类以 `category="ownership"` 构造，`job_store.py:617-636` 按 category 拦截、两出口均 OWNERSHIP_CONFLICT；不推 INTERNAL_ERROR，也不闭合全部裸家族 | R07-11、M07、E16 |
| A04 R07-11 归属 | **已更正**为 FR-201 实例事实编辑（非 FR-200 定义表单） | R07-11 |
| A05 CI 精确化 | **已采纳并实测**：Quality 在失败前实际跑过 I04 矩阵 144 PASS/21.89s、typecheck、vitest 39 文件、三次 build；仅完整 3769 套件三 job 全 NOTRUN | E10、V12、§9 |
| A05 build 边界 | **已采纳**：文件身份 ≠ 内存哈希 ≠ serve/HMR ≠ 新包 | R07-09 |
| A06 #26 | **已更正**：正控为 `de-ch-1901`/`en-001`，`de-CH-1901` 语法合法但非 canonical、受控拒绝 | 清单 #26、E19 |
| A06 #85 | **已更正**：Electron 应用 + Python 协调器/引擎为多进程本机逻辑服务 | 清单 #85 |
| A06 #96 | **已更正**：Ubuntu/macOS CI 历史证据存在，Windows 非唯一异平台证据；"老旧电脑"仍未实测 | 清单 #96 |
| A06 #124 | **已更正并实测**：42 条 INVALID_REQUEST 共用同一固定中文提示，OWNERSHIP 为另一条；内部 typed category 不证明 UI 文案分类，也不新增文案分类要求 | 清单 #124、E17 |
| A06 #125 | **已更正并实测**：`spec:762-775` 以 `toHaveValue` 断言 S/P/O 保留（含 4301，O047 通过）；未覆盖的是其它产品表单 | 清单 #125、E17 |
| A06 #128 | **已更正并实测**：Undo UI **已存在**（按钮 + `prepareUndo` 重读基准）；旧 ADR 表述为 spike 期历史；Undo GUI 记 UNTESTED／HOLD，不构成父 FR 闭合 | 清单 #128、V20、E18 |
| A07 各项 | **全部采纳并按产品事实改写**：#1 与 #29/#149 分开；#40 不闭合早期 definitions wire；#41 值参数化与受控动态标识符并存；#47 固定信封与受限类型化定位载荷分层；#53/54/57/115/145/146/154 一律保留法律/隐私/知识产权 HOLD 与未验证范围；#111 来源记录 ≠ 升级治理；#133/134 历史流程 ≠ b215 已绿/已合并；#147 多 agent ≠ 人的 bus factor；#148 ROOT 为自动 Codex 对话而非人类资深审查者，且不新增人类放行门禁；#150 "无新 bug" ≠ 具备解释/修复能力；#158 本地单机 ≠ 跨 OS/参考设备/多环境可靠性；#159 保留未知是诚实纪律但不证明人力调试能力 | 清单对应行 |
| A08 编号可识别性 | **已采纳**：R07-01…R07-13 各自独立可识别并附归口/事件窗口；原"另记"条目升为 **R07-13**（TS 数值类型范围宽于 zod schema，维护项、当前唯一调用方合规、边界校验拒越界、不改代码/测试） | §5、§6 |
| A08 R07-12 计量 | **已保留**：upstream 整件 615416 B／142 成员 DEFLATED，fr201.3 整件 2379774 B／142 成员 STORED；供应链/法务/来源 HOLD 与旧 wheel 保留 | R07-12 |
| A09 历史可追溯 | **已采纳**：20 个 R06 位置与 35 个 R04/R05 位置逐条保留状态/证据/归口；R05 ZP7 的**诊断参数与文件增长两部分均保留**；A03 应用到 MM04、A04 应用到 M06/MM07，且不改写受保护旧报告 | §8.1、§8.2、§8.3 |
| A09 D 系列与 HOLD | **已保留**：D3 OPEN；D4 裸家族 OPEN；D6 OPEN（未证经封装 UI 可达）；D8 两 PATH python 不变；D10 四类具名下游未验 vs 9 条通用失效正负例；D11 应用边界维护；26/17/10/7/16 算术 ≠ 全部可达；无 ORDER BY 是代码事实 | §8.2、§9 |
| A09 O047 语义 | **已保留**：57 事务／43 拒绝／28 笔 FR-200 属有界验收；不证物理 DB 零写、全部 PID 自然 0、全附录 C、全 FR／Goal／M0／发布完成 | §9 |
| A09 D8 选择 A | **已保留**：当前仅解除 T02 本功能 R4+；旧 `45f64` 候选**永不**成为原样批准的候选 | §8.2、§10 |
| A10 收据与终态 | **已执行**：本节记录实际读取与实测值；修订后的文件实际字节/SHA 见 §12.3 | §12 |

### 12.3 本次修订后的文件状态

- 文件：`docs/reviews/T02/fr200-fr201-20261024/round-07/minimax-m31flash.md`（**原路径、原文件、原会话**，未另建报告、未覆盖首版副本）
- 修订性质：**一次**原地事实修订；结论段（§0、§10）与全部 HOLD 未变
- 终态：**末次实质修订完成版（全部实质修订已落地、含本节但不含本行回填）实测 81721 B / SHA256 `e489122d900486a51fe1f7cc3d2591772072569b28b598a9897f1df522b2835b`，608 行**；结构自检：160 项清单行 **1–160 连续、无缺号无重复**，编号发现 **R07-01…R07-13 共 13 条**齐备。首版 57131 B / `ce4b1ae7…6b8c8` 的独立副本未被覆盖。本行回填会使最终文件字节数大于上述值（回填行为本身新增字节），故以"回填前"口径登记，避免自指循环。**末次自检时的现盘排除命中数为 15**（原测量 13 ＋ 本文件 ＋ 并存的 round-07 同行文件），该增量只反映后续文件出现，**不否定原测量面的 7 tracked / 13 物理命中**
- 未执行：未运行产品/测试/ruff/构建/安装/SQL/probe；未改源码/配置/测试/CI/AGENTS/历史报告；未 push、未切分支、未触碰 index；未读取本轮同行报告正文
