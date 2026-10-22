# T10-S1 round-2 独立外审报告（MiniMax M3.1-Flash / xhigh）

**结论先行：本轮对 `T10-S1 私有包检查与安全报告文件服务` 有界阶段给出「明确通过」。** 登记 **0 项 P0/P1/P2 证实缺陷**；新增 **3 项 P3 观察项**（均为格式取舍量化或文档口径，不改变任何已登记验收结论）。round-1 的 10 项议题逐条复核：2 项已在本候选修复并经独立复现，6 项仍为登记在案的开放项（其中 1 项明确延期未修），2 项为跨 owner 的既有状态——**没有任何一项被本轮误标为已关闭**。

本通过**仅限**该有界阶段。完整 T10 父门（正式格式/schema、可信且排除凭据的业务投影、唯一 writer 原子导入、真实学习与重放语义、真实 App/bridge 接线、FR-1000/1001/104 全量、A-06–08、G.6、12.4/12.5、全部 57 项 P0、包内与双平台、真人验收、CI/push/PR/develop 合并/远端核验）**全部仍未关闭**，本报告不构成其中任何一项的通过。

---

## 1. 实际身份与执行环境（读回值，非计划值）

| 项 | 实际值 | 核验方式 |
| --- | --- | --- |
| 隔离工作树 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T10-minimax-review-r2-66cc152` | 全程读写只在此树 |
| Git HEAD | detached `66cc15200611d592d3da2877961f9e079eb05277` | `git rev-parse HEAD` |
| 批准 base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | `git cat-file -t` = commit |
| 上一产品点 C | `c3c7e90f721344113c4279d663127f9c8d5bda59` | 存在 |
| 工具/证据点 N | `66eeedd735370576b49eb39cd4b14cdef9c0d55b` | 存在 |
| 历史冻结候选 A | `a1e7efef4bd47c97b630753c0e7c4dc34de1d8ae` | 存在 |
| AGENTS.md（工作树） | SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` | `shasum -a 256` 实算，与 addendum 声明**完全一致**；保持未暂存，本轮未改写 |
| AGENTS.md（HEAD blob） | `1b3c02916e9bab79f463a61f2818846f01e849014b70251b37c112377443a6fb` | 受保护副本是未暂存的工作树修改，与本轮说明一致 |
| 模型 / 档位 / 权限 | `minimax/MiniMax-M3.1-Flash`、effort `xhigh`、`permissionMode: bypassPermissions` | `/Users/kyle/.minimax/config.yaml` 实读 + 本会话运行时上下文 |
| Node / npm | v24.15.0 / 11.12.1 | `node -v` / `npm -v` |
| Python | CPython 3.12.12（本树 `.venv`，由预备方 `uv sync --frozen` 建立） | `.venv/bin/python -V` |
| 本会话可见标识 | session `mvs_d314cc7a43c84a559e31d5ddf3663af7` | 运行时上下文可见 |
| 派发侧任务ID/turn | **本会话未收到** ZCode/MiniMax 任务ID、会话ID或终态回执字段 | 不猜测、不捏造；由原 owner 用实际创建/终态原件关联 |

**Git 只读**：全程仅用 `status / show / diff / log / cat-file / ls-tree / rev-parse / check-ignore / merge-base`。未执行 stage/commit/stash/reset/checkout/switch/merge/push，也未运行 `npm run format` 或 HMR 探针。

**审查结束时的写面**（`git status --porcelain`）：

```
 M AGENTS.md          ← 受保护，未暂存，本轮未改
?? docs/reviews/T10/round-2/   ← 本报告 + 本审者 raw + 预备方冻结输入副本
```

除上述目录与被 `.gitignore` 覆盖的派生目录（`out/t10-review/round-2/minimax/**`、`out/t10-render-probe/`、`.pytest_cache/`、`.ruff_cache/`、`__pycache__/`）外，本轮**未在受审树产生任何新文件**；无 `.mimosa/`；`git diff 66cc152 -- docs/reviews/T10/round-1/ docs/reviews/T10/evidence/` 为**空**（历史原件与 round-1 报告逐字节未动）；冻结输入副本 `docs/reviews/T10/round-2/minimax-input/` 时间戳均为 18:11–18:12（早于本会话 18:19），未被本轮修改。

---

## 2. 固定输入核验（225 项，逐 Git blob）

新 `input-manifest.json`（`docs/reviews/T10/round-2/minimax-input/`）声明 base `5f910b52`、candidate `66cc152`、`fileCount=225 / deltaCount=219 / unchangedContextCount=6`。

审查方自写脚本（`out/t10-review/round-2/minimax/scripts/verify-manifest.py`）对 225 项逐项 `git cat-file blob 66cc152:<path>` 取真实字节后重算长度与 SHA-256，并同时比对工作树副本：

- **225/225 长度与 SHA-256 全部匹配，0 缺失、0 不匹配**；工作树副本与 blob 逐字节相同。
- `git diff --name-only 5f910b52 66cc152` = **219** 个文件，与清单 delta 集合**完全相等**（双向无差集）；6 项 unchanged-context 为 `apps/desktop/src/csp.ts`、`docs/prd/PRD-本体学习与落地Agent工作台.md`、`package.json`、`package-lock.json`、`pyproject.toml`、`uv.lock`。
- 旧 147 清单副本 SHA-256 = `b2c17f448608370b86ac0549e4f72312e3c8542afa2835138f9fd3b1a4f80623`，与新清单 `prior147ManifestSHA256` 一致；旧清单 147/147 项对历史候选 A 复算**全部匹配**（旧原件未改、仅作历史链）。

原始输出：`docs/reviews/T10/round-2/minimax-raw/manifest-verification.txt`。

**候选身份边界（重要）**：`git diff --name-only c3c7e90 66cc152 -- apps packages tests scripts package.json package-lock.json pyproject.toml uv.lock` 仅两条：`packages/engine/src/ontolearn_engine/transfer/inspection.py` 与 `packages/engine/tests/test_transfer_inspection.py`。即**本候选的产品代码改动只限于 Python 检查器与其测试**，其余 219 项为证据/文档/工具材料。

---

## 3. 实际读过与实际运行过的内容

### 3.1 逐字读过的受审文件（11 个作者路径 + 7 个工具 + 不变上下文）

- 产品源码：`packages/engine/src/ontolearn_engine/transfer/inspection.py`(223)、`transfer/__init__.py`(6)、`apps/desktop/src/renderer/src/transfer/report.ts`(230)、`transfer/TransferPanel.tsx`(82)、`apps/desktop/src/main/project-transfer/prepared-report-file.ts`(338)
- 不变上下文：`apps/desktop/src/csp.ts`(26)
- 测试：`packages/engine/tests/test_transfer_inspection.py`(341)、`tests/unit/t10-report.test.ts`(183)、`tests/unit/t10-report-file.test.ts`(513)
- fixture：`tests/fixtures/transfer/{inspection-expected,malicious-texts,report-input}.json`（攻击串实测 **12** 条）
- 工具 7 个：`docs/iterations/T10/render-probe.mjs`、`docs/iterations/T10/isolated/{Dockerfile,run.sh,prepare-native.mjs,native-hook.cjs,native-driver.mjs,run-container.py}`
- 候选文档：`private-stage-candidate.md`、`verification.md`、`status.md`、`internal-review.md`、`report-file-internal-review.md`、`isolated-native-review.md`、`trusted-contract-review.md`、`round-1-disposition.md`、`round-2-preparation/{verification.json,internal-review.md,validation/*}`、`docs/iterations/T10/{private-preparation,interface-needs,report-file-publication,isolated-native-validation,i06-trusted-transfer-contract-request,t01-transfer-design-acceptance-r1,i06-transfer-response-acceptance-r1}.md`
- PRD：`FR-104`(L297)、`FR-1000`(L569)、`FR-1001`(L589)、`A-06/A-07/A-08`(L1241-1243)、`G.6`(L1247)、`12.4`(L833)、`12.5`(L840)
- 历史证据原件：attempt-1/2/3 全部 JSON 与日志、`native-compiled-postrun-readback/`、`legacy-raw-archive/`（index + 40 项）、`browser-summary.json`、`initial-browser-summary.json`、`verification-summary.json`、`check-failure-notes.json`、`report-file-failures.json`、`approved-input-reference.json`、`round-1/terminal-receipt.json`

### 3.2 实际运行的命令（全部首失败保留在 raw）

| 命令 | 环境 | 结果 | 原始输出 |
| --- | --- | --- | --- |
| `npm run check`（lint/format/类型/vitest/build/ruff/pytest） | 本树 node_modules + .venv | **EXIT=0 一次通过**；vitest 17 文件 **691 passed**；pytest **1118 passed** | `minimax-raw/check-full.txt` |
| `pytest packages/engine/tests/test_transfer_inspection.py -q` | `.venv` | **66 passed** | `minimax-raw/targeted-suites.txt` |
| `npx vitest run tests/unit/t10-report.test.ts tests/unit/t10-report-file.test.ts` | 本树 | 2 文件 **61 passed**（18 + 43） | `minimax-raw/targeted-suites.txt` |
| `npm run verify:sources` | 本树 | exit 0，「已核对 12 个归档源文件」 | `minimax-raw/targeted-suites.txt` |
| `node docs/iterations/T10/render-probe.mjs`（真实工具） | 本树 | `T10_SYNTHETIC_PROBE_READY`，输出至 `out/t10-render-probe/` | `minimax-raw/render-probe.txt` |
| 审查方独立 Python 反例（55 例） | `.venv`，直调冻结源码 | 见 §5.1 | `minimax-raw/adversarial-inspection.txt` |
| 审查方诊断脚本（可达上限 / 第三方归档） | `.venv` | 见 §5.1 | `minimax-raw/diagnostics.txt` |
| 审查方独立 TS 反例（25 项，scratch 自建 vitest 配置） | 本树 | **25/25 通过** | `minimax-raw/ts-checks.txt` |
| 审查方产物复算（2 变体 + 4 原件逐字节比对） | 本树 | 见 §6 | `minimax-raw/recompute-artifacts.txt` |
| 审查方 DOM 级白名单分析（stdlib `html.parser`） | `.venv` | 6 份产物全部 PASS | `minimax-raw/dom-analysis.txt` |
| 审查方证据链逐 hash 核验（55/40/11/3 + 容器 source-manifest 116） | 本树 | 见 §7 | `minimax-raw/evidence-verification.txt` |

审查方全部脚本、派生输出与产物在自建 scratch `out/t10-review/round-2/minimax/`；**未修改任何受审源码、测试、fixture、依赖声明、锁、配置、验收、旧原件或 AGENTS**。自建 scratch vitest 配置 `include` 仅指向 `out/**/**.checks.ts`，**不会被仓库默认 `vitest run`（`include: tests/unit/**/*.test.ts`）发现**，未污染受审测试发现流。

---

## 4. 逐项审查结论

### 4.1 S1-A Python 只读 ZIP 信封检查 —— 通过（限登记范围）

逐行核对 `inspection.py` 全部 223 行并逐条反例验证：

- **严格性**：`draftVersion` 字面量精确匹配，不匹配一律 `FORMAT_UNSUPPORTED`，无任何隐式迁移（E8 实测）；manifest 键集严格相等；重复键 `MANIFEST_DUPLICATE_KEY`（E1）；`NaN`/`Infinity`/非对象/截断 JSON 一律 `MANIFEST_SHAPE`（E2–E6）；深嵌套 `RecursionError` 收敛为固定码；角色封闭集合，`vault/credentials/audit/authorization/unknown` 全拒 `ROLE_UNSUPPORTED`（B7）。
- **布局反隐藏**：EOCD 必须位于文件尾且 `offset+size == len-22`（无尾随字节/注释/ZIP64/多磁盘，C13–C15、A3–A4）；本地 header 从偏移 0 连续铺到中央目录（`ARCHIVE_LAYOUT`）；本地/中央 flags、compression、CRC、packed/unpacked、文件名逐项一致；`extra_len == 0`；仅允许 0x800 位（拒加密 C12、拒流式 data descriptor C13）；中央目录独占 `[offset, len-22)`。**不存在可藏字节的缝隙**：字节被完整划分为「本地头+数据」/「中央目录区」/「EOCD」三段且互相核算。
- **解压安全**：raw-deflate 带界输出并检查 `eof/unused_data/unconsumed_tail`（F1 隐藏尾随流 → `ARCHIVE_INVALID`）；STORED/DEFLATED only；逐成员 CRC+长度+SHA-256；预算 40MiB/32MiB/8MiB/64KiB/256 项且文档明确「非容量承诺」。
- **语义克制**：`import_allowed/restore_current/rerun_mapping/replay_runs` 恒 `false`，reason 固定（我的 B1/B2 反例直接断言了四个 `False`）；不凭角色/hash 推断 checkpoint 语义；**无解包、无路径、无 DB、无 import/restore/rerun/replay 入口**（全仓 grep 确认 `transfer` 包无任何其他导出）。
- **不误降模板**：四个核心角色齐全且无原文件/推导/历史/会话时，`declared_kind="full"` 原样保留、`included_options == selected_options == ()`（B1/B2/B3 实测），符合 FR-1000「未携带当前断言事实和来源所有权元数据的包只能标为模板包」的反向约束。
- **本轮新增修复（EOCD 计数）独立复核通过**，详见 §5.2。

### 4.2 S1-B 安全 HTML 报告与未接线页面 —— 通过（限登记范围）

- **FR-1001 栏目齐全**：11 个必需栏目全部出现（R2-17 独立断言）；结果显式绑定 `inputRevision/semanticsVersion/scope` 与 当前/过期/历史/失败/取消 状态。
- **FR-104 学习分类**：五级标签（`尚未验证完成`/`Agent 完整辅助完成`/`使用完整示范完成`/`使用部分提示或 Agent 辅助完成`/`独立完成`）；未完成或检查未过 → 尚未验证完成；完整辅助/完整示范不计独立；任何部分提示/辅助不计独立；点击完成 ≠ 掌握（R2-24 独立覆盖 9 种组合）；旧尝试不被新尝试覆盖（R2-25）。
- **纯文本与离线**：`escapeReportText` 只把动态串放进 HTML 文本位置；**用真实 HTML 解析器（stdlib `html.parser`）复核 6 份产物**：报告标记层仅 `html/head/meta/title/body/p/h1/h2/section/pre/span` 11 种元素、仅 `charset/content/http-equiv/lang` 4 个静态属性；**无 script/style/img/link/iframe/object/svg/a/form/base/video/audio/source/track/embed/applet**；CSP 与 `csp.ts` 生产变体逐字一致（`connect-src/object-src/base-uri/frame-src/form-action` 均 `none`，无 `unsafe-inline`/`unsafe-eval`）；`<pre>` 后**从不**紧跟裸 LF，前导 LF 保留（R2-19）。
  - 审查方第一次用正则抽取属性时得到 `onerror/onload/href/src/rel/data` 命中，**经解析器复核确认全部位于文本节点内**（即被转义后按字面显示的攻击串，如 `&lt;img src=&quot;…&quot; onerror=&quot;…&quot;&gt;`），不是标记属性；这是 A-07/A-08 要求的「按既定文本策略显示，不被当作页面标记执行」，非缺陷。**审查方如实保留这次自身误判的更正过程**（`minimax-raw/whitelist-analysis.txt` 为误判版本，`dom-analysis.txt` 为解析器定论）。
- **防御**：`checkBudget` 在 Zod 克隆前限节点/字符/数组/键数；拒绝 getter（自有/继承/数组下标）、稀疏数组、异常原型、循环引用，且实测 getter **未被执行**（R2-20，`invoked === false`）；错误统一 `REPORT_PROJECTION_INVALID`，无源值/诊断泄漏。
- **凭据形状**：`apiKey/password/token/vault/audit/agentSessions/sendAuthorization` 等一切额外键被 strict 拒绝（R2-22），不 dump 任意对象。
- **页面**：`TransferPanel` 独立未接线；4 选项默认未选、导入/导出禁用、三项能力明示「未验证」、无效投影 1 个 alert；无 Node/innerHTML/通用 IPC/外联。全仓 grep 确认**无任何生产 import**（见 §8）。
- **口径诚实**：合成夹具未被声称为可信 Store/T09/T08 联验或凭据排除；`private-preparation.md` L15 明确「不证明允许业务 payload 的自由文本没有凭据，也不证明已实现 A-06 端到端排除」。

### 4.3 S1-C 主进程不可变报告文件服务 —— 通过（限登记范围）

逐行核对 338 行并以真实文件系统 16 项独立断言（R2-01…R2-16，全部通过）复核：

- **构造期冻结**：渲染一次并冻结 payload/hash/长度（`Object.freeze`）；构造后修改源对象不影响产物。
- **选择校验**：strict schema + 绝对目录 + NUL 拒绝 + `.html` 后缀 + 非法/控制字符 + Windows 保留名 + 相对目录/额外键拒绝（R2-04、R2-05 均无任何 IO 副作用，目录保持为空）。
- **排他暂存/0600**：`mkdtemp` + `wx+` 打开 + 0600；发布文件权限实测 **0600**（R2-02）。
- **发布前身份核验**：经保留句柄有界读回**全字节+长度+路径身份**（同 inode 同长度改写、替换为 symlink、增长/截断均拒，R2-11/R2-12）。
- **原子不覆盖**：同文件系统 **hard link** 发布（R2-02 实测发布文件 inode == 暂存 inode）；EEXIST 即 `REPORT_TARGET_EXISTS`；既有文件/目录/最终符号链接均不覆盖且对方内容不变（R2-03）；picker 返回后竞争写入者胜出（R2-06）。
- **发布后语义**：link 成功后固定 published；其后回调错误（含伪造 EEXIST，R2-08）、中止、目录 fsync 失败**均不倒退为失败/取消**（R2-07：`postPublicationError: true` + `state: published`）。
- **清理**：仅删自己身份绑定的暂存文件与空目录，**非递归**；陌生文件保留并 `pending`，pending 期间拒绝新暂存（`REPORT_CLEANUP_PENDING`），`retryCleanup` 单飞（R2-09）。
- **并发**：同实例并发保存 → `REPORT_EXPORT_BUSY`，第二次 picker **未被调用**（R2-10）。
- **不执行访问器**：抛错对象的 `code` 为 getter 时不被执行（R2-14）。
- **边界如实**：无 I06 动态私有根 guard/可信投影/正式桥接；无跨进程提交日志/启动清扫器；**无生产 caller**。

### 4.4 T-A / T-B / T-C 工具与保全证据 —— 通过（限工具与证据范围）

- **T-A `render-probe.mjs`**：CLI-only，经 TypeScript transpile 动态 import，**不启动 Electron/浏览器**；输出目录已改为被忽略的 `out/t10-render-probe/`（见 §5.3）。
- **T-B 隔离原生六工具**：Dockerfile 摘要钉扎、非 root 1110、chrome-sandbox 0:4755、构建联网/runtime `--network none`；`run-container.py` 对**已 create 但未启动**的容器做硬配置断言并从其中复制 controls 逐 hash 比对当前受审文件；driver 5 秒命令超时 + 55 秒总 deadline + 只杀自己进程组；`native-hook.cjs` 硬断言 NoNewPrivs=1/Seccomp=2/CapEff=0/sandbox/contextIsolation/nodeIntegration=false/hang-monitor 开/mock-keychain 关/inspector 已关，真实 GTK `showSaveDialog` 保存(Alt+s)/取消(Escape)、picker 未被改写、nativeDialogs=2。**额外 `SYS_ADMIN` 与短时 main loopback inspector（picker 前关闭）如实公开，未美化为最小权限/全程无 listener。**
- **T-C 保全证据**：postrun 三份 cjs 明确标注「停止容器事后读回、非运行时独立输出 hash」；Git 副本权限不冒充原运行 0600；两个产物为两实物两运行，未混同；两项旧 snapshot missing 如实登记。

---

## 5. 独立反例与复算结果

### 5.1 审查方自制反例（不导入受审测试助手，全部自行构造字节）

**Python 55 例**（`minimax-raw/adversarial-inspection.txt`）：53 例与预期完全一致；2 例为**审查方自身构造/预期错误**，已用专门诊断脚本复算并更正结论，未记为产品缺陷：

- `E3-1`（256 条目用例）：构造时给全部成员同一 role 且选项关闭 → 实测 `UNSELECTED_CONTENT`。**真实结论见 §5.1.2**：受 `DUPLICATE_ROLE` 与 8 个角色限制，可达上限是 **9 条目**（manifest.json + 8 个数据成员），非声明的 256。
- `G1`（Info-ZIP `zip -D` 产物）：实测 `UNSAFE_ENTRY`。**真实结论见 §5.1.3**：该归档 EOCD 计数**正确**（count=2），拒绝原因是中央目录 24 字节 extra 字段 —— 属**已文档化**的格式取舍，不是本轮新增计数检查所致。

**5.1.1 覆盖要点**：EOCD 少报(1)/高报(3)/两字段不等/计数为 0/ZIP64 标记；计数不一致**先于**成员内容读取（见 §5.2）；`full` 在 STORED 与 DEFLATED 下均正确接受且四能力恒 false；模板反向（开放项，仍接受）；full 缺核心角色；未选可选内容；vault/credentials 角色；重复 role；路径穿越/绝对路径/反斜杠/大写扩展名/`.env`/保留名 con·lpt1/嵌套目录/81 字符名；**真实 NUL 文件名**；symlink 成员；加密位；流式 data descriptor；尾随字节；归档注释；未索引前缀字节；未索引本地成员；manifest 重复键/NaN/Infinity/数组/截断；额外凭据键；未知 draft 版本；缺 manifest 成员；清单外成员；隐藏 deflate 尾随流。

**5.1.2 有效成员上限 9，而非声明的 256**（`minimax-raw/diagnostics.txt`）：`manifest.json + definitions/assertions/ownership/checkpoint + raw-source/derived/history/agent-session` = 9 条目、四选项全开时**被接受**，角色集合与 selected/included 正确分离。因此源码中的 `MAX_ENTRIES = 256` 与 `len(files) < MAX_ENTRIES` **在任何输入下都无法触发**；实际约束是 `DUPLICATE_ROLE` + 角色封闭集合。`private-preparation.md` L11 已声明这些是「私有解析边界，未经业务容量测量」，故这是**预算口径与有效上限的量化差异**，供格式 owner 决策（见 R2-O1）。

**5.1.3 真实第三方归档的实际兼容边界**（同上）：Info-ZIP `zip -D` 产出的 2 成员归档 **EOCD 计数正确（count=2）**，但因中央目录带 24 字节 extra 字段被判 `UNSAFE_ENTRY`；带目录项的 `zip -r` 归档同样被判 `UNSAFE_ENTRY`（目录成员 → `S_IFDIR`）。`private-preparation.md` L11 已明确「ZIP64、多磁盘、注释、extra 和流式 data descriptor 当前明确拒绝」，故这是**已公开的格式取舍**，其代价是「标准 `zip` 工具产物当前一律不可导入」，供格式 owner 取舍（见 R2-O2）。

**TS 25 项**（`minimax-raw/ts-checks.txt`）：文件服务 16 项 + 报告投影 9 项，**全部通过**。

### 5.2 新修复（EOCD 计数）独立复核 —— 已闭合

- 实现形态：`_preflight` 返回 `(offset, count)`；`_inspect` 在**读取任何成员内容之前**强制 `len(entries) == declared_count`，不符固定 `ARCHIVE_SHAPE`。**只有一处断言、一个调用点**（`_preflight` 全仓仅 `inspect_candidate` 一处调用），未引入第二套 ZIP 解析器，未开放任何导入能力。
- 独立实测：少报(1)、高报(3)、两字段不等(1/2、2/1) → 全部 `ARCHIVE_SHAPE`；计数 0 与 ZIP64 标记 0xFFFF → `ARCHIVE_LIMIT`；合法 STORED 与 DEFLATED 的「四核心角色 + 无可选内容」包**仍被接受**且 `kind=full`、四能力 false、`selected==included==()`。
- **顺序证明（关键）**：构造「EOCD 计数谎报 + 成员 sha256 错误」的同一归档 → 实测 `ARCHIVE_SHAPE`（计数检查先触发）；把计数改回真值后同一归档 → `HASH_MISMATCH`。**证明计数校验确实发生在成员内容读取之前**，与处置文档的声明一致。
- 回归面：修复只加严、不放宽，未使任何此前接受的合法归档被拒（我的合法对照组、第三方工具归档计数、STORED/DEFLATED 双变体均实测）。

### 5.3 probe 输出隔离修复独立复核 —— 已闭合

- 真实运行 `node docs/iterations/T10/render-probe.mjs` → `T10_SYNTHETIC_PROBE_READY`，生成 **3 个 HTML**：1527B/`0519a2f9…`、**3900B/`26af1230…`**、2748B/`021ec9b2…`，与 `round-2-preparation/validation/probe-output-verification.json` 声明**逐字节一致**。
- 输出目录 `out/t10-render-probe/` 被 `.gitignore:9` 的 `out/` 覆盖（`git check-ignore -v` 实测确认）。
- **旧 `docs/reviews/T10/evidence/runtime/` 不存在**（`ls` 实测 No such file），旧证据目录未被污染；历史 `evidence/legacy-raw-archive/**` 全部 40 项 hash 仍与 index 一致。
- `private-preparation.md` L38 的运行说明已同步为新输出目录。

---

## 6. 产物可复现性（跨环境决定性复算）

审查方用**冻结的 `report.ts`** 自行编译并渲染两种投影输入，再与归档原件逐字节比对（`minimax-raw/recompute-artifacts.txt`）：

| 复算输入 | 复算结果 | 归档原件 | 逐字节相同 |
| --- | --- | --- | --- |
| `goals = malicious-texts`（保留 fixture 标题）→ native 输入 | **3896 B / `ad367a31…3cdcd`** | `evidence/isolated-native/attempt-3/native-report.html` | **是** |
| `goals = malicious-texts` + `title = attacks[0]` → probe 输入 | **3900 B / `26af1230…76b6`** | `evidence/legacy-raw-archive/report-file-runtime/{malicious,published}-report.html` | **是** |
| 同上 | 3900 B / `26af1230…` | 本轮真实 probe 产物 `out/t10-render-probe/malicious-report.html` | **是** |

即：**4 字节差异 100% 由标题输入解释**，两份实物是同一冻结源码的两种投影输入，而非两个源码版本或两个不可比运行；与 round-1 处置文档的澄清一致。

---

## 7. 证据链逐 hash 核验（`minimax-raw/evidence-verification.txt`）

| 项 | 实测 |
| --- | --- |
| `evidence/isolated-native/manifest.json` | **55/55** 逐 hash 一致，0 缺失 0 不匹配 |
| `evidence/legacy-raw-archive/index.json` → files | **40/40** 逐 hash + 长度一致 |
| index 内 `requiredSummaryRaw` | **11/11** 一致 |
| `native-compiled-postrun-readback/` 三份 cjs | **3/3** SHA-256 与长度与 index 一致 |
| attempt-1 | `Status=created`、`StartedAt/FinishedAt` 为零值、`Pid=0` → **从未启动**（与 addendum 澄清一致，不是一次 native 运行） |
| attempt-2 | driver `FAIL` / `T10_NATIVE_DEADLINE`；native `stage="T10 01a15bce save"`、`nativeDialogs=1`；容器 `ExitCode=1` → **真实失败原件保留，未改记通过** |
| attempt-3 | driver/native 均 `PASS`；容器 `exited / ExitCode=0`；`nativeDialogs=2`、`pickerUnchanged=true`、`cancelFileAbsent=true`、`mainInspectorClosed=true`；保存回执 `published` 3896B/`ad367a31…`/`mode=384`(=0600)；`NoNewPrivs=1`、`Seccomp=2`、`CapEff=0000000000000000` |
| attempt-3 容器配置 | `user=1110:1110`、`networkMode=none`、`privileged=false`、`capAdd=['CAP_SYS_ADMIN']`、`portBindings={}`、`mounts=0` → **额外 SYS_ADMIN 与无端口如实可见，未美化为最小权限** |
| 两条旧 snapshot | `missingReferencedSnapshots` 2 项如实登记，未伪造补回 |
| `check-failure-notes.json` | 首次 690 通过 / 1 失败 `EngineError: TIMEOUT`，单文件 8 通过，`cause: "not established"` → **本轮整仓 check 1118/1118 一次全绿，未复现该 flake，原因仍未证实**（未称已定位或已修） |
| `verification-summary.json` | `approvedFormat/ci(null)/pr(null)/pushed/merged/formalIntegration/credentialExclusionEndToEnd/crossDeviceAcceptance/desktopE2E/dualPlatform/dualSpecifiedReview` 全为 false/null → **与仓库事实一致，未夸大** |

**容器 source-manifest 116 项**：**114/116 与当前树一致，2 项不一致**——恰为本候选改动的 `inspection.py` 与其测试。这从数据上证明**原生与浏览器证据覆盖的是产品点 C，不是本候选 66cc152**。处置文档已如实声明「旧原件证明原C范围，未被写成新候选的全新原生运行」；本报告据此明确边界，见 §8 R2-O4。

---

## 8. 问题清单

### 8.1 证实缺陷

**未发现任何 P0 / P1 / P2 级证实缺陷。**

### 8.2 本轮新增 P3 观察项（3 项，均不改变任何已登记验收结论）

**R2-O1 [P3｜格式开放项，非缺陷] 声明的成员预算 256 在任何输入下都无法触发，有效上限是 9**

- **位置**：`packages/engine/src/ontolearn_engine/transfer/inspection.py:23`（`MAX_ENTRIES = 256`）、`:153`（`1 <= len(entries) <= MAX_ENTRIES`）、`:183`（`len(files) < MAX_ENTRIES`）、`:190`（`DUPLICATE_ROLE`）；文档 `docs/iterations/T10/private-preparation.md:11`。
- **触发**：任意包最多只能有 8 个数据成员（四个核心 + 四个可选角色，`DUPLICATE_ROLE` 拒绝同角色第二个成员），加 `manifest.json` 共 **9** 条目。实测 9 条目（四选项全开）**被接受**；256/257 条目的构造分别被 `UNSELECTED_CONTENT` / `ARCHIVE_LIMIT` 提前拦下，从未走到 `MAX_ENTRIES` 分支。
- **影响**：**不产生任何能力或安全缺口**。`MAX_ENTRIES`、`len(files) < MAX_ENTRIES` 与文档「256 个成员」的表述都是**不会触发的死约束**，实际约束来自角色封闭集合。风险是口径：格式 owner 若按「256 成员」理解可承载规模，会高估当前格式的真实容量；后续放开分片/多成员时，`MAX_ENTRIES` 会突然开始生效而未被当前测试覆盖。
- **证据**：`minimax-raw/diagnostics.txt`（H1：9 条目被接受并正确分离 selected/included）；`minimax-raw/adversarial-inspection.txt`（E3-1/E3-2）。
- **建议**：由格式 owner 在正式格式定稿时明确「每角色单成员」是否为终局约束；若是，把 `MAX_ENTRIES` 与文档表述对齐到实际可达上限；如否，保留 `MAX_ENTRIES` 并补一条真正到达 256 条目的用例。**审查方不代定产品规则。**

**R2-O2 [P3｜已文档化的格式取舍，仅量化互操作性代价] 标准 `zip` 工具产物当前一律不可导入**

- **位置**：`inspection.py:121`（`extra_len == 0`）、`:168`（`not item.extra and not item.comment`）、`:165`（`stat.S_IFMT(mode) in {0, S_IFREG}`）；文档 `private-preparation.md:11`。
- **触发**：Info-ZIP `zip -D` 产出的 2 成员归档（**EOCD 计数正确 = 2**，与本轮新增检查无关）因中央目录带 24 字节 extra 字段被拒 `UNSAFE_ENTRY`；`zip -r` 归档因含目录成员同样被拒。
- **影响**：这是**文档已明确声明**的拒绝项（"ZIP64、多磁盘、注释、extra 和流式 data descriptor 当前明确拒绝，后续正式格式由 owner 取舍"），因此**不是缺陷**。本项只补上一个此前未量化的代价：**当前草案格式与主流第三方压缩工具的产物不兼容**；若将来由外部系统产出候选包，此限制会成为直接的接入阻碍。
- **证据**：`minimax-raw/adversarial-inspection.txt`（G1/G2/G3）、`minimax-raw/diagnostics.txt`（I 节）。
- **建议**：格式 owner 在正式格式阶段明确「是否要求零 extra 字段」；若要求保留，请把该限制写进格式说明与导入方提示，而不是仅留在实现里。

**R2-O3 [P3｜文档口径] `status.md` 存在已过时的「当前/最新」数字与 AGENTS SHA**

- **位置**：`docs/reviews/T10/status.md:16`（「最新稳定整仓 check 为 691 项 TS / 1,112 项 Python」）、`:26`（「AGENTS 当前受保护 SHA `78df2825…`」）。
- **触发**：本候选的整仓结果为 **691 TS / 1,118 Python**（本轮实测），且当前工作树 AGENTS 实算 SHA 为 `de15f6ce…`。status.md 作为按时间追加的流水记录，第 75 行的最新段落已给出 691/1118，但**未重述 AGENTS SHA**；第 16/26 行的「当前/最新」措辞仍指向 C 期的 1,112 与旧 SHA。
- **影响**：AGENTS 规定完成度只在 `docs/m0-checklist.md` 与对应 `status.md` 维护，读者可能把 1,112 与旧 SHA 当作现状。同一目录下 `verification.md`、`private-stage-candidate.md`、`evidence/verification-summary.json` 也仍为 C 期的 60/18/43 与 691/1112（本轮新数字在 `round-2-preparation/verification.json`），**交叉引用不明显**。
- **证据**：本轮 `minimax-raw/check-full.txt`（1118 passed）、`shasum -a 256 AGENTS.md`（de15f6ce…）、`status.md:16/26/75`。
- **建议**：在 status.md 最新段落补一行「当前整仓 691/1118、当前 AGENTS SHA de15f6ce…」；并在 `verification.md` / `verification-summary.json` 顶部标注其为 C 期冻结证据并指向 round-2 数值。**属文档口径问题，不涉及实现。**

### 8.3 明确的证据边界（不是缺陷，但必须随本通过一起传递）

**R2-O4 新修复没有新的原生/浏览器证据**

- 本候选唯一的产品代码改动是 `inspection.py` 的 EOCD 计数断言与对应测试。**原生容器镜像构建自产品点 C**（容器 source-manifest 116 项中恰有 2 项与当前树不同，即这两个文件），浏览器产物亦复算自同一冻结 `report.ts` 的 C 版输入。
- 因此**本轮新增的计数校验没有任何新的原生或浏览器运行证据**；它由本轮 55 例 Python 反例 + 66 例定向 pytest + 整仓 1118 例覆盖。
- 处置文档已如实声明「旧原件证明原C范围，未被写成新候选的全新原生运行」。**本报告据此不把旧原生原件当作本候选的原生证据**，并建议原 owner 在最终接线阶段补一次覆盖本候选的原生/包内运行（原候选本就把该门列为父门）。
- 该项**不构成本阶段不通过的理由**：本阶段从未把原生运行登记为对新候选的验收项。

### 8.4 round-1 全部 10 项议题的逐条状态（**没有任何一项被误标为已关闭**）

| 原项 | 原级别 | 本轮实测状态 | 本轮判定 |
| --- | --- | --- | --- |
| M-F1 / Z-O1 EOCD 计数 | P2 / P3 | 已修复：`_preflight` 返回 count，`_inspect` 在读成员前强制相等，不符 `ARCHIVE_SHAPE`；少报/高报/两字段不等/合法 STORED+DEFLATED 正例 6 项测试在册；本轮独立复现通过 | **已闭合** |
| M-F2 / Z-O2 模板反向/最小角色 | P3 | 四核心角色齐全仍声明 `template` → 仍被接受（B4 实测），四能力恒 false | **仍开放**（正式格式 owner 决定，本阶段不改语义） |
| Z-O3 每角色单成员/预算规模 | P3 | 仍开放；本轮补充量化：有效上限 9 条目，`MAX_ENTRIES=256` 不可触发 | **仍开放 + 新增量化**（R2-O1） |
| Z-O4 非待确认阶段 `reconcilePublication` 返回 `unconfirmed` | P3 | **仍未修**：R2-15 实测 fresh 实例与 published 实例分别返回 `'unconfirmed'` / `'published'`，非 unconfirmed 相位仍返回 `'unconfirmed'` | **仍开放（明确延期，未称已修）** |
| Z-O5 崩溃残留暂存目录 | P3 | 无跨进程权威日志/生产位置 lease，无启动清扫器；身份绑定非递归 cleanup 未放宽 | **仍开放（已公开生命周期边界）** |
| M-F3 main 依赖 renderer 纯报告模块 | P3 | 仍在：`prepared-report-file.ts:8` → `'../../renderer/src/transfer/report'`；`report.ts` 仅 import `zod` + `csp`，为纯函数，未见运行隔离突破 | **仍开放（正式接线前协调）** |
| M-F4 desktop 缺显式 zod 依赖 | P3 | 仍在：`apps/desktop/package.json` 依赖仅 `@ontolearn/contracts/react/react-dom`；`git diff base..66cc152 -- apps/desktop/package.json` **为空** → 非 T10 引入 | **仍开放（共享依赖 owner，非本线回归）** |
| M-F5 probe 输出污染证据目录 | P3 | 已修复：输出改至被忽略的 `out/t10-render-probe/`，真实运行产出 3 HTML 且 hash 与声明逐字节一致，旧 `evidence/runtime` 不存在，旧原件未改 | **已闭合** |
| M-F6 browser/native 标注 | P3 | 处置文档已精确澄清；本轮独立复算再次确认 4B 差异 100% 来自标题输入，旧冻结字节保留未改 | **已闭合（标注口径）** |
| M-F7 `executed:null` 度量含义 | P3 | 处置文档已定义「仅表示未观测到哨兵」；摘要原件按要求不改写 | **已闭合（口径）** |

---

## 9. 未验证 / 本阶段不可验证的边界（明确不覆盖）

1. **无正式格式批准**：`t10-envelope-draft-1` 未批准；`import/restore/rerun/replay` 从未开放（恒 false）；hash 只证明字节完整性，不证明语义、所有权或 checkpoint 可恢复。
2. **无可信业务投影**：报告 DTO 不是可信学习记录来源；真实逐 attempt 证据须由 T09/T08/T01 投影；合成夹具不得冒称真实学习验收或凭据排除（A-06 端到端未实现）。
3. **未接线**：私有报告文件服务与 `TransferPanel` **无任何生产 import**（本轮全仓 grep 实测为空）；无 preload/bridge、无 App 入口、无真实 native picker、无 I06 动态私有根 guard 或可信投影。**不得把本阶段通过读成正式 App 接线通过。**
4. **无打包 / 包内 / 双平台证据**：本阶段未产出 `package:dir`、包内引擎/迁移、双 OS、真人验收证据；本轮**未**执行 `npm run package:dir` 与 e2e（本阶段有界验收之外，且审查不得占用受审实现做打包改动）。
5. **原生证据的适用面**：仅 Linux arm64 隔离容器内的**私有服务**保存/取消；容器额外 `SYS_ADMIN`（非最小权限）、构建期联网 / 运行期 `--network none`、启动阶段短时 main loopback inspector（picker 前关闭）；**不得美化为最小权限 / 全程无 listener**。该证据**不**代表通用 e2e、正式 App/bridge 可信投影、G.6、跨平台或包内完成。
6. **本候选无新原生证据**：见 R2-O4。
7. **既有 TIMEOUT 原因未证实**：本轮整仓 1118/1118 一次全绿，未复现该 flake，原因仍未确立，原样保留。
8. **浏览器「不执行」是观测结论**：`dangerousNodes: 0` + 哨兵未触发 + 外部请求为空 + 本轮解析器级标记白名单复核；非形式化证明。
9. **双审与远端门**：本报告只是本轮一方结论；**另一方（ZCode GLM-5.3）本轮结论、实际 CI、push/PR、正常 develop 合并与远端核验均不在本报告内，也未由本轮触发**。
10. **本轮未做的事**：未创建 Goal、未派发其他模型任务、未读取/接收/展示另一方本轮报告或其结论、未执行任何 Git 写操作、未修改受审实现/测试/依赖/配置/验收/旧原件/AGENTS。

---

## 10. 最终结论

**本阶段结论：T10-S1「私有包检查与安全报告文件服务」有界阶段 —— 明确通过。**

依据（本轮全部独立复现，非引用旧报告数字）：

- 固定输入 **225/225** 项逐 Git blob 核验通过；`base..candidate` 的 219 文件 delta 与清单完全相等；旧 147 清单 147/147 对 A 复算通过且字节未改。
- 整仓 `npm run check` 在本隔离树**一次 exit 0**（691 TS / 1,118 Python，lint/格式/类型/构建全通过）；定向 **66 Python / 61 TS（18+43）**；`verify:sources` 通过。
- 本轮新增的 EOCD 计数修复**已独立复现并证明其检查顺序**（计数谎报 + 坏 hash 同归档 → `ARCHIVE_SHAPE`；计数改真 → `HASH_MISMATCH`）；probe 输出隔离修复**已用真实工具跑通并与声明 hash 逐字节一致**，旧证据目录未污染。
- 审查方自建 **55 例 Python 反例 + 25 项 TS 断言**（合计 80 项）全部通过或按 §5 如实记录，未发现任何成员逃逸、HTML 注入、外联、覆盖发布、越权清理或失败谎报；用真实 HTML 解析器完成标记级白名单复核，报告仅 11 种元素与 4 个静态属性，CSP 与 `csp.ts` 生产变体逐字一致。
- 两份历史实物（native 3896B/`ad367a31…`、browser 3900B/`26af1230…`）均由本轮从冻结源码**逐字节独立复算**成功，4B 差异完全由标题输入解释。
- 证据链 55/55、40/40、11/11、3/3 逐 hash 通过；attempt1 未启动、attempt2 真实失败、attempt3 真实成功**原件均保留未改写**；既有 TIMEOUT 原因仍未证实且未声称已修。

登记问题：**0 项 P0/P1/P2**；**3 项新增 P3**（R2-O1 预算有效上限量化、R2-O2 第三方归档兼容代价、R2-O3 status.md 过时口径）+ **1 项证据边界**（R2-O4 新修复无新原生证据）。round-1 的 10 项议题中 2 项已闭合、6 项仍开放（**含明确延期的 Z-O4，未称已修**）、2 项为跨 owner 既有状态，**无一被本轮误标为已关闭**。

**该通过的边界**：仅覆盖 T10-S1 有界阶段。**完整 T10 父门全部未关闭** —— 正式格式/schema 与完整 checkpoint、可信且排除 vault/凭据/发送授权的业务投影、唯一 writer 的原子导入与 receipt、真实学习与重放语义、公共同代次/项目/窗口/bridge 接线、FR-1000/1001/104 全量、A-06–08、G.6、12.4/12.5、全部父功能与跨模块门、57 项 P0、包内与双平台验收、真人验收、CI / push / PR / 正常 develop 合并 / 远端核验，**均未因本报告通过**。**不得**把本阶段通过扩写为产品、迁移、G.6、跨平台、包内、真实凭据排除或发布通过。

本报告为本模型 round-2 唯一产物，仅写入 `docs/reviews/T10/round-2/minimax-m31flash.md`；未修改任何受审源码、测试、fixture、依赖声明、锁、配置、验收、旧原件或 AGENTS，未执行任何 Git 写操作。本轮可见会话标识为 `mvs_d314cc7a43c84a559e31d5ddf3663af7`；派发侧任务ID/turn 未向本模型可见，如实留白，由原 owner 以实际创建/终态原件关联。
