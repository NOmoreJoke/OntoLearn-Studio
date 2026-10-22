# T06 UI 未装配独立组件 — MiniMax Code M3.1-Flash 完整独立只读对抗审查

**结论：通过「未装配独立 UI 组件完整范围」的本次本地独立审查。** 历史 3 项 P2 经本审查独立复核全部确认关闭；本次另发现 **1 项 P2（新增）**、**3 项 P3（新增）**、**1 项 P3 验证脚本稳健性观察**。P2-新不阻断本组件自身完整范围，但**必须在 T00 装配前修复或以宿主契约显式约束**，否则存在重复提交与在途结果被静默丢弃的风险。

本结论**不是**：指定外审通过、原 FR-600–604 父模块通过、真实 App/bridge/引擎/Store/推理/Agent 联验通过、原生两 OS 通过、包内验证通过、真人验收通过、CI/推送/PR/合并/发布通过。全部未验门在第 9 节逐条列出。

---

## 1. 任务来源、模型身份与权限事实（owner 外部读回 vs 模型自身可核，分开陈述）

### 1.1 来源

- 派发来源：父级总控经 `docs/reviews/T06/ui-round-1/minimax-m31flash-input.md`（21006 B，SHA-256 `1dd600c234cfc7958ccad2599701c85e71357b23dfeeb27a2bdcbad2cd07ed38`）冻结输入，加 owner「实际派发 addendum」映射实际工作区、证据路径与报告路径。
- 本审查者读取的自身派发输入：同目录 `dispatch-preflight.json`（自身派发证据映射）与 `prepared-environments.json` 中 `model: "minimax"` 记录。
- **未读取**：S1 当前外审的任何提示/报告/输出/推理；另一模型的输入/意见/报告/会话。本目录经列举确认只含 `dispatch-preflight.json`、`minimax-m31flash-dispatch-20261022.md`、`minimax-m31flash-input.md`、`prepared-environments.json`，无另一模型报告文件。

### 1.2 模型自身可核事实

| 项 | 值 |
|---|---|
| 应用 | MiniMax Code（桌面本地运行时） |
| 模型 | MiniMax-M3.1-Flash |
| Session ID | `mvs_1e7a6b7b6e624cc28afb6f4bad4470e3` |
| 最高思考等级 | 由指派指定为 xhigh；**模型自身无法读回该任务的实际思考等级读回值**，不据此声明 |
| 运行目录 | `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-da37709` |

### 1.3 owner 外部读回事实（**本审查者无法自证，如实标注**）

- `dispatch-preflight.json` 中 `actualModelTasks.minimax` 字段在派发时为 **`null`**。
- 因此：**当前任务的 taskID、创建租约、以及实际 `permissionMode=bypassPermissions`（始终授权/Full access）的读回值，均未由 owner 在本审查树内留下可核记录**。addendum 明确写明「本补充本身不证明任务设置」。
- 本审查**不**声明「已受理」「已设为始终授权」「已按 xhigh 运行」。使用者默认权限政策（AGENTS §ZCode/MiniMax Code）在本任务中被视为**已获授权但未在树内留痕**；本审查全程只读，未因此扩大写面：未修改受审源码/测试/配置/锁，未提交、未推送、未切分支、未写另一报告或原开发树。
- addendum 要求的「owner 提交前后真实核验 model taskID、实际权限/等级与创建租约」**仍需 owner 在总控侧完成**，本报告不能替代该回执。

---

## 2. 工作区、Git 身份与源码哈希核验

### 2.1 实际工作区（唯一）

```
/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-ui-minimax-review-da37709
```

| 项 | 实测值 | 与冻结输入 |
|---|---|---|
| HEAD | `3b3af941c73b7a5d416fda50ec6fb8102992551f` | 一致 |
| 分支 | **detached**（`git branch --show-current` 为空） | 一致 |
| base | `5f910b52c69d86a1076b2032e5d3c63e715947f3` | 一致 |
| 产品候选 | `da37709dcf09e04ded767ab2d08c26bbd8df24f3` | 一致 |
| 流程 HEAD | `3b3af94`（= 工作区 HEAD） | 一致 |

`git log --oneline -5`：`3b3af94` docs → `da37709` fix → `571b4d6` feat → `5f910b5` Merge PR#5。

### 2.2 完整 base→product diff

```
git diff --binary 5f910b52c69d86a1076b2032e5d3c63e715947f3 da37709dcf09e04ded767ab2d08c26bbd8df24f3
SHA-256 = 0b2ebc607543cfbc0a02a2856c1fddbf4b4a92c6204cf186f3655d0b90f8a2b4   ✅ 与冻结输入一致
```

`--name-status` 实测为 **10 个 A（全部新增）**，`2840 insertions(+)`，无共享文件改动：

```
A apps/desktop/src/renderer/src/behavior/BehaviorWorkspace.tsx   (804 行)
A apps/desktop/src/renderer/src/behavior/README.md               (43 行)
A apps/desktop/src/renderer/src/behavior/behavior.css           (301 行)
A apps/desktop/src/renderer/src/behavior/controller.ts           (253 行)
A apps/desktop/src/renderer/src/behavior/model.ts                (348 行)
A apps/desktop/src/renderer/src/behavior/presentation.ts         (42 行)
A apps/desktop/src/renderer/src/behavior/status.md               (32 行)
A apps/desktop/src/renderer/src/behavior/verification.json       (73 行)
A apps/desktop/src/renderer/src/behavior/verify-headless.mjs     (265 行)
A tests/unit/t06-behavior-ui.test.ts                             (679 行)
```

### 2.3 product→流程 HEAD 差异（逐字读完，仅 2 项流程文件）

`git diff da37709 3b3af94` = **仅** `apps/desktop/src/renderer/src/behavior/status.md`（+8 行）与 `.../verification.json`（+37/-3 行）。两者内容均为流程性证据记录（新增「da37709 完整独立复核终态」段、把 `new_candidate_review` 从 `"pending new full independent review"` 展开为对象、把 `not_verified` 中 `independent review and specified dual external review` 改为 `specified GLM-5.3/M3.1-Flash dual external review`、新增 `product_head`）。

**未改动任何源码、测试或脚本**；源码/测试/脚本在产品与流程 HEAD 之间逐字节相同（见 2.4）。

### 2.4 7 项受审源/测试/脚本三方 SHA（本审查者实测重算）

| 文件 | 冻结基线 | 审查树 | Git 产品 `da37709` | 流程 HEAD `3b3af94` |
|---|---|---|---|---|
| BehaviorWorkspace.tsx | `0e7012e1…671b` | ✅ | ✅ | ✅ |
| controller.ts | `36d59ea1…17d3` | ✅ | ✅ | ✅ |
| model.ts | `b246491a…f90f` | ✅ | ✅ | ✅ |
| presentation.ts | `5966010c…a1d2` | ✅ | ✅ | ✅ |
| behavior.css | `869ebea1…1465` | ✅ | ✅ | ✅ |
| verify-headless.mjs | `a4573ccc…a742` | ✅ | ✅ | ✅ |
| t06-behavior-ui.test.ts | `cad7082f…0440c` | ✅ | ✅ | ✅ |

**审查结束时的最终重算与开始时完全一致**（第 8 节），受审内容未被本审查改动。

### 2.5 PRD 与 AGENTS

- PRD：`/Users/kyle/Documents/工作/知爻/本体/PRD-本体学习与落地Agent工作台.md`，SHA-256 `7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb` ✅ 与冻结输入一致。已全文读 **FR-600/601/602/603/604、附录 C（能力矩阵主定义）、附录 D.1/D.2（结果状态与失效表）、附录 E.1（事件/条件快照/写入）、E.2（固定轮次状态机）、E.5、G.0（固定基线与重置）、G-behavior、G.3（B-01…B-11）、附录 F（Agent 授权表）**。
- AGENTS：本树 `AGENTS.md` SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4` ✅ 与 addendum 一致（当前政策原字节副本）。**保持 dirty 未暂存、未还原**（Git 中 HEAD 版本为 `1b3c0291…`，差异为政策更新，非产品变更）。开始与结束 `git status` 一致：`M AGENTS.md` + 两个未跟踪目录（`docs/reviews/T06/`、`ui-review-evidence/`）。

---

## 3. 实际读取范围（全部完成，无抽样）

**受审 10 文件全文读完**：`BehaviorWorkspace.tsx`（804 行，分两次读完）、`README.md`、`behavior.css`、`controller.ts`、`model.ts`、`presentation.ts`、`status.md`、`verification.json`、`verify-headless.mjs`、`tests/unit/t06-behavior-ui.test.ts`（679 行，分两次读完）。

**历史原件 7 项全部读完**（owner 复制为本树只读副本，逐字节 SHA 复核一致）：

| 历史原件 | SHA-256 | 状态 |
|---|---|---|
| ui-integration-handoff.md | `b0403445…715d` | ✅ |
| ui-local-review-1.md（571b4d6 **不通过**原报告） | `628f2370…292` | ✅ |
| ui-local-review-2.md（da37709 通过报告） | `0ed80af7…9b3` | ✅ |
| evidence/ui-validation-da37709.json | `a7cfcdb0…820` | ✅ |
| evidence/ui-archive-index-20261021.json | `a2131587…d231` | ✅ |
| evidence/ui-archive-20261021.md | `33c33705…7232` | ✅ |
| evidence/ui-571b4d6-negative-probes.mjs | `dc8b5495…62ab` | ✅ |

**原失败产品 Git 对象已读取**：`git show 571b4d64120c8420d527f9fda2a3cb81bbd47d3f:apps/desktop/src/renderer/src/behavior/verification.json` → SHA-256 `ddd1bc99026c51d444755ad2363423f428d84a57f2a7092b4bd42e20a3d18bc9` ✅ 与 `verification.json` 中 `previous_verification.sha256` 一致；其 7 项源哈希为 571 旧值（`39d258fd…`/`016161c1…`/`d27417f9…`/`ff2ece45…`），与当前 `da37709` 不同，证实 571 与产品确为两个不同候选。

**两个归档独立复核（本审查者自写只读校验器，不执行包内任何代码）**：

| 包 | 字节数 | 包 SHA-256 | 内嵌 manifest SHA | 白名单成员 | 实测 |
|---|---|---|---|---|---|
| ui-original-artifacts-20261021.tar.gz | 2,232,198 ✅ | `a51bfec8…b433` ✅ | `42950c37…b629d` ✅ | 33 | **33/33 字节+SHA 全部一致** |
| ui-session-tool-records-20261021.tar.gz | 6,698 ✅ | `06d2e863…a5b3` ✅ | `b35e8ae0…2156` ✅ | 6 条原工具记录 + README | **7/7 一致** |

合计 **42 个归档成员**（33 + 7 + 2 个 manifest）。全部成员经校验为 **regular 文件**：无绝对路径、无 `..`、无符号链接/硬链接、无设备文件、无白名单外成员。已恢复副本与包内字节逐件一致。校验器输出：`/tmp/t06-ui-m31flash-review-da37709/archive-verification.json`（EXIT=0）。

> 六条历史工具原行（独立 34 单测 exit0、571 虚拟入口失败 exit1、571 build 数组形态失败 exit1）及其 call_id/源行号/字节偏移/终态均在包内 manifest，已核；未读取任何全会话、人类/系统消息或凭据。

---

## 4. 本次实际执行的命令与结果（含首败）

全部命令在唯一工作区 `/Users/kyle/.../T06-ui-minimax-review-da37709` 内执行，使用本树自有 `node_modules`（317 项）、本树自有 `.venv`、Node v24.15.0 / npm 11.12.1。

| # | 命令 | cwd | 退出码 | 结果 |
|---|---|---|---|---|
| 1 | `npx vitest run tests/unit/t06-behavior-ui.test.ts` | 工作区根 | **0** | **34 passed / 34**（16 文件中的 1 个），耗时 302 ms |
| 2 | `npm run check`（owner 复制的 `ui-review-evidence/` 在树内） | 工作区根 | **1** | **1055 个 eslint error，全部来自 2 个文件**，见 4.1 |
| 3 | `npm run check`（审查者自有的证据目录临时移出仓库后） | 工作区根 | **0** | lint / format:check / typecheck(contracts+unit+desktop) / **664 TS（16 文件）** / desktop build / ruff / **1052 Python** 全通过 |
| 4 | `PLAYWRIGHT_BROWSERS_PATH=<树内 out/t06-ui-review-browser> npx playwright install chromium --only-shell` | 工作区根 | **1** | `ECONNRESET`，见 4.2 |
| 5 | `node out/t06-ui-review-headless/verify.mjs`（第 1 次） | 工作区根 | **1** | **首败**：点击 `检查本地结构` 可操作性超时，见 4.3 |
| 6 | `node out/t06-ui-review-headless/verify.mjs`（第 2、3 次） | 工作区根 | **0 / 0** | 全链路通过，产物一致 |
| 7 | `npx vitest run --config out/t06-ui-review-headless/vitest.probe.config.mts` | 工作区根 | **0** | 追加只读反例 8/8 通过，产出 4 项新发现证据 |
| 8 | `node out/t06-ui-review-headless/verify.mjs`（owner 官方来源核验后的**确认复跑**，默认 1248 路线） | 工作区根 | **0** | 全链路再次通过；`evidence.json` SHA 仍为 `d7397917…` |
| 9 | `node out/t06-ui-review-headless/argv-probe.mjs`（只读，记录真实启动 argv） | 工作区根 | **0** | 可执行文件解析到**本树自有** `chromium_headless_shell-1248`；未使用 `executablePath` |

### 4.1 首败 #2 的归因（重要，避免误判为产品缺陷）

`npm run check` 在**含 owner 复制的证据目录**时退出 1，1055 个错误**全部**来自两个文件：

```
ui-review-evidence/ui-original-artifacts-20261021/independent-build/verify.mjs
ui-review-evidence/ui-original-artifacts-20261021/independent-build/output/preview.js
```

二者均为历史归档 `ui-original-artifacts-20261021.tar.gz` 的成员（tar 成员清单可核对），是**历史原件副本**，非受审产品代码。仓库 `eslint.config.mjs` 的 ignores 覆盖 `out/**`、`dist/**`、`test-results/**` 等，但**不覆盖** `ui-review-evidence/**`——这是 owner 把归档解包进仓库根造成的布局效应。

为取得真实产品面结论，审查者将**仅审查者自有的** `ui-review-evidence/` 临时移出仓库（记录 51 个文件 SHA → 移出 → 运行 → 移回 → 逐文件 SHA 比对），移回后 **51/51 文件逐字节一致**，`git status` 恢复原状（`M AGENTS.md` + 两个未跟踪目录）。复跑 `npm run check` 退出 0。**未修改仓库任何 eslint/prettier 配置，未跳过任何检查步骤。**

### 4.2 浏览器环境事实（owner 纠正后的最终状态）

> **owner 纠正（2026-10-22）**：原派发补充中「只能 1248、禁止 1208/1217/1234」的限制被明确纠正——**1248 只是 Playwright 1.64.1 的默认配套修订号，原用户并未给额外浏览器修订号硬门，不能把默认版本变成永久产品门**。原 TLS 失败记录与冻结原输入完整保留。本审查的执行**本就落在默认 1248 路线**（未用 `executablePath`、未改 Playwright 配置、未改冻结 7 源码/锁/原输入），故**该纠正不改变本报告任何结论**，仅补全环境 provenance。

**（a）官方下载失败记录（本审查者第 5 次实测，保留）**
审查者在固定目录 `out/t06-ui-review-browser` 实际执行官方安装，退出 1，`ECONNRESET`（`cdn.playwright.dev` → TLS 连接前断开）。与 owner 记录的 4 次失败（95403 exit1、14040 exit35、86209 exit1、owner 同步 exec exit35）**同一失败模式**，未降低 TLS、未改全局网络、未选旧 cache 顶替。

**（b）官方来源补全（owner 提供，本审查者独立复核）**
owner 已从 **Google 官方 GCS 同一 bucket/object** 的 JSON API 入口完整下载官方 ZIP：

- GET：`https://www.googleapis.com/storage/v1/b/chrome-for-testing-public/o/156.0.8078.4%2Fmac-arm64%2Fchrome-headless-shell-mac-arm64.zip?alt=media`（TLS 200，103,778,487 B）
- ZIP SHA-256 `94e4337b70cbc5638f0935fbc46b9f242bc7416f657e3fbe924baf348404b53d`；MD5 base64 `DlFzouaq+2z7axsdckdo9w==` **与官方 `x-goog-hash` 一致**；ZIP 16 成员 **CRC 全过**
- 官方记录：`outputs/20261022_t06_external_review/ui-browser-resolution/`（`findings.md`、`source-and-network-findings.json`、`owner-install-receipt.json`，本审查者**只读**）
- 无未知镜像、无 TLS 放宽、无全局网络更改

**（c）本审查者对「本树浏览器」的独立逐件复核**
owner 回执中我这一条为 `existedBeforeOwnerInstall: true / verified all16 existing bytes; did not overwrite`（owner 未覆盖我的副本）。本审查者**独立**把本树 `out/t06-ui-review-browser/chromium_headless_shell-1248/` 的内容与 owner 回执中**官方 ZIP 派生的 16 成员清单**逐件比对：

```
OFFICIAL-ZIP MEMBER VERIFICATION (my tree): 16/16 matched on bytes+SHA256+mode | mismatches: 0
```

含主可执行文件 `chrome-headless-shell`（176,747,664 B，mode `0755`）SHA-256 `77d8278b1ac9d0687fad4e817ea83023ede09b1deef36e1864b49ba194ac9634`——与 owner 独立计算值**逐字节一致**。树内另有 2 个官方安装器 marker（`DEPENDENCIES_VALIDATED`、`INSTALLATION_COMPLETE`），非额外载荷。实际执行 `--version` 退出 0：`Google Chrome for Testing 156.0.8078.4`。

**（d）本审查者的处置（与 owner 纠正完全一致）**
机器上存在与当前 lock **完全相同的 revision 1248**，审查者将其**复制**（非移动、非顶替旧 cache）到本树固定目录 `out/t06-ui-review-browser/`，逐文件 SHA 比对确认与来源树字节一致（BROWSER TREE BYTE-IDENTICAL）。全局旧 cache `1208/1217/1234` **未被使用**；**未**使用 `executablePath`；**未**改 Playwright 配置或冻结依赖。

**（e）仍然存在的缺口（不倒推）**
历史三次运行所用的浏览器 binary SHA 与完整 argv **仍未记录**（`knownSourceLimitations` 第 1 条）。本次记录仅覆盖本次运行，**不声称已复现历史 binary 身份**。

### 4.3 首败 #5：headless 脚本可操作性超时（非确定性）

第 1 次运行在 `verify-headless.mjs:122` 处失败：

```
locator.click: Timeout 10000ms exceeded.
- waiting for getByRole('button', { name: '检查本地结构', exact: true })
- locator resolved to <button class="behavior-secondary">检查本地结构</button>
- attempting click action
- waiting for element to be visible, enabled and stable
```

审查者随后用只读诊断探针实测该按钮：`disabled=false`、`visible=true`、**连续 6 帧包围盒完全相同（稳定）**、`pageerror` 为空，且诊断探针中该点击**成功**并产出 `本地结构检查通过；真实推理、幂等与竞争检查仍由隔离执行服务完成。`。随后对**未修改**的重定位脚本连续再跑 2 次，均退出 0。

判定：**非确定性的环境/时序抖动**（最可能与浏览器首次冷启动相关），**不是受审组件的稳定缺陷**。但由于 `verify-headless.mjs` 本身属受审 10 文件之一，此项作为 **P3 验证脚本稳健性观察**列入第 5 节。

### 4.4 headless 重定位与新产物

重定位副本：`out/t06-ui-review-headless/verify.mjs`。与产品脚本 `diff` **恰好 2 行**：

```
- const component = fileURLToPath(new URL('./BehaviorWorkspace.tsx', import.meta.url))
- const output = path.resolve('test-results/t06-behavior-ui-r2')
+ const component = fileURLToPath(new URL('file:///…/T06-ui-minimax-review-da37709/apps/…/BehaviorWorkspace.tsx'))
+ const output = '/…/T06-ui-minimax-review-da37709/out/t06-ui-review-headless/output'
```

产品脚本本体未被修改（SHA 仍为 `a4573ccc…a742`）；副本 SHA `6a3e35b72e7b6383843582d186f01694ea9dbd74d0d6cb04528b1c95454efe86`。未运行归档旧 `preview.js`/`index.html`/旧脚本，未覆盖任何历史证据。

**新产物**（本审查者独立生成，非历史复制）：

| 文件 | 本次 SHA-256 | 与历史记录比较 |
|---|---|---|
| `output/evidence.json` | `d7397917d1446c5901f10d92481666c477e7bc6ae529fa919b82241bc5ee0b56` | **与历史 r2 记录逐字节一致** ✅ |
| `output/width-1440.png` | `565483abad02192c84d230a452dbb047e8d142b697cb646a83ccf9ff0146c393` | 与历史 `2a2ea63a…` 不同（夹具含随机 requestId，截图非确定） |
| `output/width-390.png` | `fb94b095318cd4c5a10ca14b02cebe25780072ae83a937055295af318ff07000` | 同上 |
| `output/viewport-390.png` | `570922bd87141b8dbb2bff5b81bcb9ee5e110ba918256149a653f60203eecd30` | 同上 |

`evidence.json` 字节一致说明当前产品**确定性复现**了历史 r2 的 8 条检查结论；而截图不可字节复现是**因为夹具 requestId 含 `crypto.randomUUID()`**，属夹具固有性质，非产品问题。

**截图已实际查看**：`width-1440.png`（1440×2516 全页）与 `viewport-390.png`（390 宽）均由本审查者打开审阅。观察到：顶部黄条明确标注「开发验证夹具 · 非引擎结果 · 不接入产品」；「当/如果/那么」三段结构完整；条件 1 为「无额外条件（恒真）」且**不渲染对象/属性字段**；结果区呈现「运行已取消 · 本轮未提交 / 当前输入」、动作「已回滚」、通知「已丢弃」；通知内容 `<img src=x onerror=alert(1)>` 以**纯文本**呈现，页面中 `img` 元素数为 0；390 宽单列布局无横向溢出、中文可读。**局限**：全部为开发夹具视图，不是引擎结果，也不是正式 App 装配视图。

### 4.5 默认 1248 路线的确认复跑与真实启动 argv（owner 纠正后补做）

owner 指出其**尚未运行本次 UI 夹具**，且「安装/版本读回不是 Pass」。据此本审查者在 owner 完成官方来源核验后**再次实际运行**了原完整 headless 验证（脚本仅含 4.4 所述的 2 行重定位，其余正/负断言、1440/390、键盘、`pageerror`、截图与安全设置全部保留）：

- 第 4 次运行：**EXIT=0**，8 条 check 全过，`output/evidence.json` SHA-256 仍为 `d7397917d1446c5901f10d92481666c477e7bc6ae529fa919b82241bc5ee0b56`（与历史 r2 记录**再次逐字节一致**）。
- 真实启动 argv（只读探针，未使用 `executablePath`，由 Playwright 默认 registry 解析）：

```
resolved executable: /Users/kyle/.../T06-ui-minimax-review-da37709/out/t06-ui-review-browser/
                     chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell
spawnargs: [--disable-field-trial-config, --disable-background-networking, --disable-background-timer-throttling,
            --disable-backgrounding-occluded-windows, --disable-back-forward-cache, --disable-breakpad,
            --disable-client-side-phishing-detection, --disable-component-extensions-with-background-pages,
            --disable-component-update, --no-default-browser-check, --disable-default-apps, --disable-dev-shm-usage,
            --disable-edgeupdater, --disable-extensions, --disable-features=…(Playwright 默认集),
            --enable-features=CDPScreenshotNewSurface, --allow-pre-commit-input, --disable-hang-monitor,
            --disable-ipc-flooding-protection, --disable-popup-blocking, --disable-prompt-on-repost,
            --disable-renderer-backgrounding, --disable-updater-scheduler, --force-color-profile=srgb,
            --metrics-recording-only, --no-first-run, --password-store=basic, --use-mock-keychain,
            --no-service-autorun, --export-tagged-pdf, --disable-search-engine-choice-screen,
            --unsafely-disable-devtools-self-xss-warnings, --edge-skip-compat-layer-relaunch, --disable-infobars,
            --disable-search-engine-choice-screen, --disable-sync, --enable-unsafe-swiftshader, --headless,
            --hide-scrollbars, --mute-audio, --blink-settings=…, --no-sandbox,
            --user-data-dir=<系统临时目录>/playwright_chromiumdev_profile-XXXX, --remote-debugging-pipe, --no-startup-window]
```

**精确说明，避免被误读为伪造原生验收**：`--disable-hang-monitor` 与 `--use-mock-keychain` 是 **Playwright 对 headless shell 注入的默认参数**，**不是**产品级 hang monitor 关闭、也不是原生 Keychain 验收替代；本次是**未装配组件的浏览器夹具验证**，与第 9.2 节列出的 Electron/macOS/Windows 原生门**完全无关**，不得据此推断原生验收。`--user-data-dir` 落在系统临时目录，**不共享可变 cache**；无 HMR、无 Electron、无真实项目数据。

至此本审查者共完成 **4 次**当前脚本实跑：1 次首败（非确定性可操作性超时，诊断见 4.3）+ **3 次 EXIT=0**，每次 `evidence.json` SHA 均相同。

---

## 5. 发现清单（新增，按严重度）

### 【P2-新-1】宿主重建等价回调身份会丢弃在途结果并放行重复提交

- **位置**：
  - `apps/desktop/src/renderer/src/behavior/controller.ts:72-77`（`serviceChanged` 按**函数身份**比较）
  - `apps/desktop/src/renderer/src/behavior/controller.ts:95-102`（`else if (serviceChanged)` 分支：`this.invalidate()` 并 `publish({ pending: undefined, cancelling: false, notice: '能力连接已变化，请核对后重新运行。' })`）
  - `apps/desktop/src/renderer/src/behavior/BehaviorWorkspace.tsx:43-45`（`useEffect` 依赖 `[controller, context, catalog, services, initialDraft]`）
  - `apps/desktop/src/renderer/src/behavior/BehaviorWorkspace.tsx:503`（运行按钮仅受 `Boolean(state.pending)` 约束）
  - `apps/desktop/src/renderer/src/behavior/README.md`（回调契约表未要求引用稳定）
- **最小有效触发输入**：宿主每次渲染重新构造 `services` 对象（内联箭头函数），且此时有一次 `runSample` 在途：
  ```ts
  const controller = new BehaviorController(context, catalog, draft, { runSample: runA })
  controller.editEvents([event])
  const inflight = controller.run()                      // pending = run
  controller.configure(context, catalog, { runSample: runB }) // 能力等价，仅函数身份不同
  ```
- **实测影响**（PROBE-A 实测输出）：
  ```
  PROBE-A after identity churn: {"cancelling":false,"notice":"能力连接已变化，请核对后重新运行。"}
  PROBE-A runSample call count after second run: 2
  ```
  即：① 在途请求的 `pending` 被清空、首轮回包被 epoch 校验拒绝并**静默丢弃**；② “在隔离副本中测试”按钮立即恢复可用，用户可在**首个请求尚未收尾**时再次提交，**`runSample` 被调用两次**。
- **影响**：违反 FR-603「重复提交同一事件必须验证幂等结果」的可达前提（幂等由服务承担，但 UI 放行了重复提交），且与交接文档「不得盲目重发写请求」相抵触；同时在途结果被丢弃，用户看到「能力连接已变化」而非真实原因，**取证链断裂**。
- **缓解事实（须同时记录）**：组件**尚未装配**，当前无生产影响；宿主若用 `useMemo` 稳定回调即不触发。
- **修复建议（二选一，建议都做）**：
  1. **宿主契约**：在 `behavior/README.md` 回调契约表中明确写入「三个 callback 须引用稳定（`useMemo`/模块级常量）；组件以函数身份判定能力变更」；
  2. **组件侧最小修复**：能力变更时**只作废结果、不清 `pending`**（保留「有请求在途」事实），使首个请求收尾前无法再次提交；同时在 `pending` 未收尾期间显示「上一请求仍在收尾，结果已作废」而非泛化的「能力连接已变化」。

### 【P3-新-1】含保留键的混合载荷会连同普通业务字段一并被拒

- **位置**：`apps/desktop/src/renderer/src/behavior/model.ts:284`（`reservedPayloadKeys`）、`model.ts:305-320`（JSON.parse 后、`z.record` 前的自有键检查；命中即 `return`，**整条事件不进入 `parsed`**）
- **最小有效触发输入**：`payload = '{"equipment":"T1","level":"high","__proto__":"x"}'`
- **实测影响**（PROBE-B）：
  ```
  PROBE-B mixed payload issues: [{"path":"events.0","message":"事件内容包含保留键（__proto__、constructor 或 prototype），请改用普通业务字段"}]
  PROBE-B mixed payload delivered events: []
  PROBE-B ordinary-key payload delivered events: [{"id":"E-1","type":"alarm","payload":{"equipment":"T1","level":"high"},"changes":[]}]
  PROBE-B near-miss keys delivered events: [{"id":"E-1","type":"alarm","payload":{"__proto_value":"a","Constructor":"b","normal":null},"changes":[]}]
  ```
  普通字段 `equipment`、`level` **未送达**执行回调；仅当载荷完全不含保留键时普通字段才完整保留；`__proto_value`、`Constructor` 等近似名不误伤（大小写敏感精确匹配，符合预期）。
- **影响**：用户仅因一个误输入的保留键，就**整条事件不可提交**，必须手工改写 JSON 才能恢复；而提示文案「请改用普通业务字段」只说明保留键问题，**未说明同一载荷内的普通字段也被一并阻断**，指引不完整。
- **口径澄清（重要，避免误判为 P2-3 重开）**：原不通过报告 `ui-local-review-1.md` 的 P2-3 明确写「**建议：显式拒绝该类保留键并给出本地问题，或用安全自有属性表示无损保存；不得静默删除**」。当前实现取「显式拒绝 + 本地问题 + 编辑器原文保留 + 不进入 callback」，**符合原 P2-3 的首选建议**，**不构成 P2-3 未关闭**。本项是 addendum 措辞「须拒绝并保留原文及普通键」在「混合载荷」情形下的细化差异，按原权威 P2 口径列为 **P3 澄清与指引缺口**。
- **修复建议**：在保留键提示中明示「该事件整体不会执行，其中普通字段也不予提交，请删除保留键后重试」；或改为「仅剔除保留键、其余普通字段照常送达」并补混合载荷正/负例。现有单测只覆盖「纯普通字段保留」，**缺混合载荷用例**。

### 【P3-新-2】取消回包绑定不匹配时，提示语指向结果展示而非取消未确认

- **位置**：`apps/desktop/src/renderer/src/behavior/controller.ts:230-245`
- **最小有效触发输入**：`cancelSample` 返回 `state:'cancelled'` 但 `binding.requestId` 为他人请求（如 `'someone-elses-request'`）
- **实测影响**（PROBE-G）：
  ```
  PROBE-G after mismatched cancel: {"pending":{"kind":"run",…},"cancelling":false,
      "notice":"返回结果格式或项目/版本/请求不匹配，已拒绝显示。"}
  PROBE-G after original run resolves: {"result":"candidate","notice":""}
  ```
  行为本身**正确**：`pending` 保留（不谎报已取消）、`cancelling` 归位、原请求收尾后自动恢复；但用户看到的是**结果展示类**提示，而非 `controller.ts:235` 中为「取消未确认」准备的专用文案「取消尚未得到有效收尾确认，原请求继续等待。」。
- **影响**：仅提示语选择不当；**不构成假取消、不丢结果**（原请求收尾后正常落库）。因 `parsed.data.state === 'cancelled'` 已满足，`controller.ts:234` 的分支未被命中，专用文案不可达。
- **修复建议**：在 `controller.ts:238` 之前先校验 `sameContext`/`requestId` 是否与在途绑定一致，不一致时走 `controller.ts:235` 的取消未确认分支并给出专用文案。

### 【P3-新-3】结果自由文本字段不受敏感内容约束（适配器边界残余风险）

- **位置**：`apps/desktop/src/renderer/src/behavior/model.ts:105`（`freshnessDetail`）、`model.ts:115`（`reason`）、`model.ts:130`（`detail`）；`apps/desktop/src/renderer/src/behavior/presentation.ts:29`（原样渲染 `item.detail`）
- **最小有效触发输入**：服务返回 `detail: '/Users/kyle/secret/path.sqlite stack trace at Object.<anonymous>'`
- **实测影响**（PROBE-W）：组件**原样渲染**该字符串。
- **定性**：**组件自身无缺陷**——组件产生的所有错误均为固定枚举 + 固定本地文案（`controller.ts:166/219/248`），`catch` 块不携带原始异常；`grep` 确认受审目录内无 `error.message`/`stack`/`console.log`/`innerHTML`/`dangerouslySetInnerHTML`/`fetch`/`window.*`/`localStorage` 等使用。风险在于**适配器违约**：若适配器把路径/堆栈/凭据塞入 `detail`，UI 会照实显示。`README.md` 已明文禁止（「禁止将 `BehaviorError.evidence`、原始异常、路径、堆栈、密钥或业务原值塞入错误或 trace detail」）。
- **修复建议**：在 T00 装配清单中把「适配器白名单化 `detail`/`reason`/`freshnessDetail`」列为**装配前必过项**；可选地在 schema 层加「疑似路径/栈形态」的宽松拒绝（注意勿误伤合法业务文本）。

### 【P3-新-4】`verify-headless.mjs` 存在一次可操作性超时（验证脚本稳健性）

- **位置**：`apps/desktop/src/renderer/src/behavior/verify-headless.mjs:122`
- **实测**：3 次运行中 1 次在点击 `检查本地结构` 处超时（详见 4.3）；诊断证明按钮非 disabled、非不可见、包围盒 6 帧稳定；再跑 2 次均 exit 0。
- **影响**：**不影响产品能力**，影响的是**验证脚本的可靠性**：在冷启动或负载高时可能产生假失败。
- **修复建议**：对关键点击使用更稳的定位/等待（如先 `waitFor` + `scrollIntoViewIfNeeded`），或在脚本内对可操作性超时做一次有界重试。

### 补充观察（不构成缺陷，列明以免遗漏）

1. **`catalog` 未用于任何界面呈现**：`BehaviorWorkspace.tsx` 仅把 `catalog` 交给控制器做校验（`controller.ts:76/244-245`），界面未提供对象/类/属性的候选提示，用户需凭外部知识手填 ID。PRD FR-600 要求的是「卡片或**填空式**编辑」，故**不违反需求**；但 T00 接线时若要「引导模式」体验，此处是既有缺口。
2. **事件级断言变更无本地单多值校验**：动作侧有「单值覆盖/多值追加拒绝」（`model.ts:272-279`），而事件 `add/remove/set` 变更（`model.ts:322-334`）只校验形状，不校验基数与已知性。`README.md` 第 19 行已把「拒绝不可表示的……变更」明确划归 **adapter** 职责，故属**已声明的职责边界**，非缺陷；但接线时 adapter 必须补齐，否则单值属性可被事件侧覆盖。
3. **`crypto.randomUUID()` 位于 `try` 之外**（`controller.ts:148`）：若在非安全上下文抛错，`run()` 会 reject 且**不产生任何用户可见提示**（`pending` 尚未置位）。`file://`/`127.0.0.1` 均为可信来源，实际触发概率低；建议移入 `try` 或前置降级。
4. **同 ID 重投保真已验证**：事件 ID `' E-1 '` 归一为 `'E-1'` 且**跨两次运行保持稳定**，仅 `binding.requestId` 变化（PROBE-L），符合交接文档「不能用 requestId 作为事件内容版本」。

---

## 6. 历史 3 项 P2 的独立复核（逐项关闭/重开判定）

> 判定依据为**原不通过报告 `ui-local-review-1.md` 的权威条款**与当前源码/实测，不采信开发者声明，也不以 `ui-local-review-2.md` 的结论代替本次核验。

### P2-1「无法显式表达无额外条件的行为」→ **关闭（确认）**

- **要求**：显式 always；仍拒真正缺失/空条件；不把空输入静默当通过；补 author→validate→callback 回归。
- **实测**：源码 `model.ts:13` 为严格 `z.object({kind: z.literal('always')}).strict()`；`model.ts:247` 对 always 跳过对象/属性校验；`model.ts:53` `conditions` 仍 `min(1)`；`draftSchema` 拒绝 `always` 夹带额外字段。
- **新增探针（PROBE-C）**：`[{kind:'always'},{kind:'equals',object:'ghost',…}]` → `[{path:'conditions.1',message:'条件引用了未知对象'}]`。**always 不掩盖同组兄弟条件的有效性**，即「显式恒真」不等于「整组恒真」。
- **headless 实测**：条件类型切到「无额外条件（恒真）」后，`条件对象 ID`/`条件属性 ID` 元素数均为 0，宿主 `onDraftChange` 收到精确 `[{"kind":"always"}]`，执行回调收到同一内容；移除至 0 条后校验仍拒绝，重新选择 always 后通过。
- **判定**：**关闭**。

### P2-2「结果内部证据状态与运行状态不一致仍被接收展示」→ **关闭（确认）**

- **要求**：单次 sample 的状态/动作/通知矩阵；严格 schema 拒绝矛盾；候选不得带 applied/recorded；四状态完整正/负组合；刷新保留上一份有效结果。
- **实测**：`model.ts:153-189` `superRefine` 实现完整矩阵（candidate: planned/deduplicated/skipped + candidate 通知；completed: applied/deduplicated/skipped + recorded；failed/cancelled: rolled_back/skipped + discarded），另含 `committed ⟺ completed`、`failed ⟺ error≠null`、`stale` 必须有说明。
- **证据**：既有单测遍历全部 **60 种** 4×5×3 合成组合（本审查者复跑 34 项通过）；headless 实测矛盾 `candidate+applied/recorded` 被拒（提示含「已拒绝显示」）、**刷新后上一份有效结果仍在**、新请求不展示矛盾证据。
- **本审查者补充核验**：`supersRefine` 只约束**动作与通知状态**，未约束 `diff` 内容——failed/cancelled 仍可携带非空 diff。此为**设计选择**（回滚尝试的差异可视化），标签为「未提交尝试 Diff」，未冒充提交，不构成假通过。
- **判定**：**关闭**。

### P2-3「事件载荷保留键被静默丢弃，输入内容身份折叠」→ **关闭（确认），另附 P3-新-1 细化**

- **要求**：显式拒绝保留键并给出本地问题，或无损保存；不得静默删除；不得把丢值误述为原型污染利用。
- **实测**：`model.ts:305-320` 在 `JSON.parse` 之后、`z.record` 归一化之前检查**自有键**；`__proto__`（含 `\u005f` 转义形式）、`constructor`、`prototype` 三类均命中。
- **关键回归**：两份**同 ID、不同内容**的 `{"__proto__":"first"}` / `{"__proto__":"second"}` 各自被独立拒绝，**执行回调计数不增加**（headless 实测 `测试调用次数` 不变），不存在内容折叠；回调收到的 payload 与原文一致，无修改。
- **定性正确**：原 P2-3 明确「此项是静默丢值，不是原型污染利用」；当前实现与文档（`README.md` 第 19 行）均如实表述，**未夸大为原型污染**。
- **附注**：混合载荷下普通字段一并被拒（P3-新-1），按原权威 P2 口径不构成重开。
- **判定**：**关闭**。

**历史 3 项 P2 独立判定：3/3 关闭，无重开。** 原不通过结论（`ui-local-review-1.md`，571b4d6）与原件**保留未改写**。

---

## 7. 全范围其余核对（本次独立完成）

**FR-600**：名称/说明/触发事件/条件/动作/效果/启用/优先级/版本齐备；单组 AND（`model.ts:53` 单一 `conditions` 数组，无 `preconditions`——`draftSchema.strict()` 拒绝 `preconditions`，实测 `safeParse` 失败）；行为 ID 唯一 + 编辑现有 ID 例外（PROBE-M：编辑 `other` 时 `saved` 被拒；编辑 `saved` 时通过）；事件 ID 唯一（批内重复被拒，跨运行重投保留 ID，PROBE-L）。
**FR-601**：安全动作限 create/update/relate/notify 四类，界面文案明示「没有邮件、消息或外部数据库操作」。
**FR-602**：缺失条件、无效对象、未知类/属性/IRI、重复事件、单值关系追加拒绝、多值覆盖拒绝、动作顺序编辑均在本地校验（`model.ts:233-283`）；**未在 UI 重做领域引擎**，界面明确把真实推理/幂等/竞争检查划归服务（`controller.ts:132`）。
**FR-603/604**：触发/未触发原因、完整动作顺序与状态、Diff 增删、通知、request/runId/project/input/behavior/scope 与断言/推导/语义版本均可见（`presentation.ts:21-41`、`BehaviorWorkspace.tsx:740-761`）；隔离副本边界以界面与 README 双重声明。
**E.1**：事件与事实变更数组顺序保留、显式 add/remove/set 可编辑；`create` 后同实例前向引用被允许（PROBE-E），指向从未创建对象被拒；稳定排序文案与 E.1 一致。
**附录 D**：当前/过期/历史由**服务**给出，UI 不推断；`stale` 必须带说明；候选/提交/失败/取消四态互斥呈现。
**异步与生命周期**：epoch + `sameContext` + `requestId` + `runId` 四重校验拒绝迟到回包；切项目/输入版本清结果且按约定保留同项目草稿；能力连接变更与卸载后回包不覆盖；取消须真实终态，ack 不冒充取消；完成先赢与取消先赢两向竞态均有实测（既有单测 + 本次 headless「拒绝迟到完成覆盖取消」）。
**安全与能力边界**：无 `window.*`、`ipcRenderer`、Store、网络、`innerHTML`/`dangerouslySetInnerHTML`（全目录 grep 无命中）；组件所有错误为固定文案；HTML-like 通知以纯文本渲染且页面 `img` 元素数为 0；无 `window.ontolearn`、无公共能力注册、无正式数据写入。
**可访问性与布局**：`<section aria-labelledby>`、`<aside aria-label>`、`<fieldset>/<legend>` 分组、`role="status" aria-live="polite"`、`role="alert"`、`aria-label` 列表；Tab 焦点实际推进（唯一行为 ID → 行为名称）；1440/390 无横向溢出（`scrollWidth <= innerWidth` 实测）；中文文案可读、无溢出截断。
**60 的含义核对**：60 = 4（运行状态）× 5（动作状态）× 3（通知状态）的**合成 schema 组合**，**不是** 60 次真实引擎运行——本审查者未把单测计数当作引擎证据。

---

## 8. 审查期间受审面零变更核验

| 时点 | `git status` | HEAD | 7 源 SHA |
|---|---|---|---|
| 开始 | `M AGENTS.md` + `?? docs/reviews/T06/` + `?? ui-review-evidence/` | `3b3af94` | 全部匹配 |
| 结束 | `M AGENTS.md` + `?? docs/reviews/T06/` + `?? ui-review-evidence/` | `3b3af94` | 全部匹配 |

- 受审 10 文件**字节未变**（含 `verify-headless.mjs` 仍为 `a4573ccc…a742`）。
- **未**提交、未推送、未切分支、未建 PR、未合并；**未**写原开发树 `T06-behavior-ui`、未写另一模型报告、未写共享控制文件、`state.json` 或受审源码/测试/配置/锁。
- 新增产物仅限：本树 gitignore 的 `out/t06-ui-review-browser/`、`out/t06-ui-review-headless/`，以及系统临时目录 `/tmp/t06-ui-m31flash-review-da37709/`（日志、校验器、探针、归档校验报告）。`AGENTS.md` 保持 dirty 未暂存。
- 唯一报告文件：本文件 `docs/reviews/T06/ui-round-1/minimax-m31flash.md`。

---

## 9. 明确结论与未验门

### 9.1 结论（仅限本次范围）

**「未装配独立 UI 组件完整范围」：通过。**

依据：受审 10 文件与 base→product 完整 diff 已逐字读完；7 源三方 SHA 全部一致；PRD FR-600–604/C/D/E.1/E.2/E.5/G.0/G-behavior/G.3/F 已读原条款；历史原件 7 项 + 2 包 42 成员 + 571b4d6 Git 对象全部复核；本审查者**独立实际执行** 34 项专项单测（exit 0）、完整 `npm run check`（产品面 exit 0，664 TS + 1052 Python）、真实 headless 全链路（1 次首败 + **3 次 exit 0**，含 owner 官方来源核验后的确认复跑；产物 `evidence.json` 与历史记录逐字节一致）、8 项追加只读反例（8/8）；浏览器经 16/16 官方 ZIP 成员独立复核、默认 1248 路线、真实启动 argv 已记录；历史 3 项 P2 经独立核验 3/3 关闭。

**附带条件（须在 T00 装配前闭环）**：
1. **P2-新-1** 必须在装配前修复，或以 `README.md` 宿主契约明确约束回调引用稳定 + 禁止在途重复提交；二者均未闭环前，本组件不应被接入会重渲染宿主。
2. **P3-新-1 / P3-新-2** 建议在装配前一并修文案与用例（提示语 + 混合载荷正/负例）。
3. **P3-新-3** 的适配器白名单化必须列入装配前必过项。
4. 本报告**不**覆盖另一模型的结论；另一模型意见由 owner 全文读回后统一处置。**受审内容一旦变化，双方须新建同版完整审查。**

### 9.2 未验门（本报告不覆盖，逐条列出）

1. 正式 App 装配、共享导航与宿主生命周期；
2. 公共 bridge / preload / CSP 边界（本子阶段无相关改动）；
3. 真实引擎：条件冻结快照、写入意图、竞争写入、幂等、事务原子提交与回滚、取消终态持久化；
4. Store 原子提交、版本化、旧基线拒绝、持久恢复；
5. 真实推理与行为前推导（G.3 B-04 快照检错、B-05/B-09 竞争回滚、B-10/B-11 排序与去重、B-06 多行为触发实例）；
6. Agent 交互、G.3 全量基线、真实 G.3 语义执行；
7. `exists`/`type` 与已批准 S1 语义的无损映射（**私有 callback 不得当作 S1 兼容**）；
8. 正式权限/受信来源证明（隔离 scope 标签**不是**权限证明）；
9. 结果失效与 `staleReason` 的现行失效表来源（现由服务给出，UI 不推断）；
10. 原生 Electron / macOS / Windows 双平台；
11. 包内验证（`npm run package:dir` + 包内样例）、首发平台验收；
12. 真人验收；
13. 指定双模型外审的**另一模型**部分（本报告仅代表 M3.1-Flash 一次独立审查）；
14. CI、推送、PR、合并、发布；
15. 历史三次运行使用的浏览器 binary SHA 与完整 argv（**历史缺口，不倒推**）。

### 9.3 本报告自身限制

- 全部浏览器证据来自**开发夹具**，非引擎、非正式 App。
- 浏览器为 **Playwright 1.64.1 默认配套 revision 1248**，走**默认 registry 路线**（未用 `executablePath`、未改 Playwright 配置）；本审查者已**独立逐件复核**其 16 个成员与 owner 由 Google 官方 GCS 同一 object 派生的清单在 bytes+SHA-256+权限上 **16/16 一致**（见 4.2c）。owner 已纠正「1248 为永久产品门」的表述，本报告据此只把 1248 记为**当前 lock 的默认配套**，**不作为产品门**。历史三次运行的 browser binary 身份仍不可考，**不倒推**。
- `npm run check` 的产品面结论建立在**临时移出审查者自有证据目录**后复跑取得（移回后 51/51 字节一致），未修改仓库任何检查配置。
- owner 对本任务的实际 taskID / `permissionMode=bypassPermissions` / 思考等级读回**未在树内留痕**（`actualModelTasks.minimax` 为 `null`），本报告不代为声明。
- 未执行 GUI/CUA/Electron/e2e/native/HMR/Keychain、无凭据/付费/模型 API 操作；未修改任一受审文件或其他工作树。
