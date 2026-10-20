# I02 / C1 显式 CSP 与窗口生命周期 — 独立对抗性审查报告（Round 1）

- 报告路径：`docs/reviews/I02/round-1/minimax-m31flash.md`
- 任务标识：`I02-R1-MiniMax-M31Flash-20261020-0735`
- 审查模型：MiniMax M3.1-Flash（MiniMax 3.1 Flash）｜思考程度：xhigh
- 审查角色：独立对抗性审查者（只读）
- 报告日期：2026-10-20（Asia/Shanghai）

---

## 0. 最终结论

**通过（Pass）。**

冻结的 I02 / C1 全部验收项均已由本轮**独立复现**（开发态、构建态、真实 macOS arm64 打包 executable 三套环境），且我额外补测了既有矩阵未覆盖的 `base-uri` / `form-action` / `object-src` 阻断、锚点同文档导航与 hash 变化后的 health 可信文档校验、以及真实 packaged 应用中"暂不恢复 / 重新打开窗口"两个恢复分支。

发现 **5 项问题：0 项阻断，3 项中（构建可复现性、原生对话框证据边界、开发 origin 校验失败路径），2 项低（生产内联脚本隐性风险、后续迭代路由约束未记录）**。全部为非阻断，均给出可执行修复建议；其中 M-01、M-03 建议在推送前处理（不改变本次受审实现语义），M-02 建议在验收/证据表述上更正，其余两项可允许延期至 I03/M1。

**门禁意见**：具备"双指定模型对同一候选版本均明确通过"的通过条件之一（仅代表本模型方，未代表另一模型方）。是否推送/合并由总控与另一模型结论共同决定。

---

## 1. 评审任务、模型及思考设置的来源记录

| 项目 | 实际值 | 来源 |
| --- | --- | --- |
| 任务标识 | `I02-R1-MiniMax-M31Flash-20261020-0735` | 本轮派发指令正文 + `docs/reviews/I02/round-1/tasks.json`（同批次创建，非本审查者写入） |
| 应用 | MiniMax Code（本会话） | 本会话自身 |
| 模型 | M3.1-Flash（MiniMax 3.1 Flash） | 本会话运行时上下文（`agent-context` 明确标注 `MiniMax-M3.1-Flash`）；与 `tasks.json` 中 `"model": "M3.1-Flash"` 一致 |
| 思考程度 | xhigh | 本轮派发指令明确指定；与 `tasks.json` 中 `"thinking": "xhigh"` 一致 |
| 项目路径来源 | 由本开发会话通过 MiniMax 原生 Select 目录选择器重新核验完整仓库路径 | 派发指令正文 + `docs/reviews/I02/status.md` "Round 1 冻结"段 |
| 新建空白任务 UI 实际显示 | 本地 / M3.1-Flash / xhigh / `feature/I02-csp-window-lifecycle` | 派发指令正文（由派发方经 computer use 实际观察后记录） |
| 报告路径 | `docs/reviews/I02/round-1/minimax-m31flash.md` | 派发指令正文 + `goal-objective.md` 第四节第 6 条命名约定 |
| 是否读取另一模型本轮报告 | **否** | 本轮开始前 `docs/reviews/I02/round-1/` 仅存在 `tasks.json`；未打开、未推断、未引用另一模型任何结论 |
| 是否预设结论 | 否 | 全部结论由本轮实际读取代码与实际运行结果得出 |

**设置核验方式**：本报告不依赖"上次设置"或截图。我以本会话实际运行时上下文（模型标识、思考档位）为准，并用 `tasks.json`（派发方在本轮创建）交叉核对模型与思考设置、base/head、仓库路径四项一致。

---

## 2. 项目路径、分支、base SHA、head SHA

| 项目 | 实际值 | 核验方式（本次实际执行） |
| --- | --- | --- |
| 仓库绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio` | `pwd`；`git rev-parse --show-toplevel` 一致 |
| 分支 | `feature/I02-csp-window-lifecycle` | `git rev-parse --abbrev-ref HEAD` |
| base SHA | `1b6df7a220fc9a67d7046133a340085f03f0a96c` | `git cat-file -t` = commit；`git merge-base --is-ancestor base head` 成立 |
| head SHA | `2cc03da82ffccc8448c7b03dc6cff87595027653` | `git rev-parse HEAD` |
| 提交关系 | base → head 为**单一提交**（`git log --oneline base..head` 仅一条） | 提交 `2cc03da feat(I02): deliver explicit CSP and safe window recovery` |
| 改动规模 | 34 文件 / +2628 / −23 | `git diff --stat base head` |
| 是否已推送 | **否** | `git ls-remote --heads origin feature/I02-csp-window-lifecycle` 无输出；`git branch -r` 无该分支 |
| 受审工作区 | 无未提交实现改动 | `git status --porcelain` 与受审前一致（详见 §5.6） |

---

## 3. 需求与验收依据（实际读取清单）

本轮**实际完整读取**下列原始要求，未以开发者验收摘要替代原要求：

1. `AGENTS.md`（仓库根，9 条开发规则全文）。
2. `docs/iterations/I01/inputs/goal-objective.md` 全文（10k）——重点第三节开发流程、**第四节"两个第三方模型的审查要求"**（含第 65–66 行报告路径命名约定、第 92 行"阻断问题未关闭或关键验收无法验证不得出具通过"）。
3. `docs/iterations/I01/inputs/scope.md` 全文——**I02 / C1 行的完整冻结验收与非目标**（第 25 行）、非目标与未决边界（第 33–39 行）、统一门禁（第 41–50 行）。
4. `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md`——**C1 全文（第 145–153 行）**及其 §4 批次表（第 174 行）、§5 证据口径（第 185–199 行）、§6 采纳说明。
5. `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6——**8.6（第 629 行）、8.7（第 640 行）、10.1–10.5（第 704–748 行）、12.5（第 840 行）**，以及 FR-001~FR-1001 中与本次相关的 FR-402/FR-803/FR-901/FR-1001、附录 C/D/E/G（G.5 行列出）。
6. `docs/iterations/I02/inputs/csp-packaged-probe-2026-10-19.md`（受保护的原始 CSP 实测逐字快照全文）与 `docs/iterations/I02/inputs/sources.json`。
7. `docs/iterations/I02/design.md`、`acceptance.md`、`commands.md`、`docs/reviews/I02/internal-review.md`、`docs/reviews/I02/status.md`、`docs/iterations/I02/evidence/*` 全部。

**未采纳为验收依据**：`docs/iterations/I02/acceptance.md`（开发者验收记录）仅作为"声明"被我核对，不作为通过依据；`docs/iterations/I02/status.md` 同理。

---

## 4. 已检查范围

### 4.1 实现代码（逐行读完后 diff 对照）

| 文件 | 检查重点 |
| --- | --- |
| `apps/desktop/src/csp.ts`（新增，26 行） | 单配置来源、开发/生产变体、origin/nonce 校验、指令集合、序列化顺序 |
| `apps/desktop/electron.vite.config.ts` | `defineConfig` 工厂形式、`command` 分支、生产 meta 插件（`apply:'build'` / `order:'post'` / `injectTo:'head-prepend'`）、`html.cspNonce` 仅 serve 生效、`server.host/port/strictPort` |
| `apps/desktop/src/main/index.ts` | `app.enableSandbox()` 时机、`web-contents-created` 注册时机、`createWindow` 顺序、`reopen` 先建后销、`closed` 回调不误清空、health IPC 三重校验、dev header 注册条件、退出标志 |
| `apps/desktop/src/main/window-security.ts`（新增） | preferences 工厂字段、全局 contents 加固（popup/导航/子 frame/重定向/webview） |
| `apps/desktop/src/main/window-recovery.ts`（新增） | 崩溃/无响应判定、提示去重、`did-finish-load` 状态清理、恢复前置条件、异常吞并、退出与窗口销毁保护 |
| `apps/desktop/src/main/trusted-document.ts`（未改） | hash 容差、协议/主机/端口/路径/查询全等 |
| `apps/desktop/src/preload/index.ts`（未改） | 仅暴露 `getEngineHealth` 窄接口 |
| `apps/desktop/src/renderer/src/App.tsx`（未改） | 锚点 `<a href="#modules">`、health 手动触发、初始"尚未检查"状态 |

### 4.2 测试与证据

`tests/e2e/csp-lifecycle.spec.ts`（273 行）、`tests/e2e/native-driver.ts`、`tests/e2e/native-recovery.cjs`、`tests/unit/csp.test.ts`、`tests/unit/window-recovery.test.ts`、`tests/unit/native-driver.test.ts`、`tests/e2e/desktop.spec.ts`；`docs/iterations/I02/evidence/` 全部 JSON/TXT（build/packaged/development 三套矩阵、check、verify-sources、package-dir、package-manifest、frozen-files、protected-check）。

### 4.3 保护边界

`docs/iterations/I02/preexisting-files.json`（64 项）、`docs/iterations/I02/evidence/frozen-files.json`（15 项）逐文件 SHA-256 重算比对（见 §5.6）。

---

## 5. 独立验证：命令与实际结果

以下全部由本审查者**实际执行**（工作目录均为仓库根）。临时产物一律写入 `/tmp`，未写入仓库。

### 5.1 静态与单元门禁

| 命令 | 实际结果 |
| --- | --- |
| `npm run check` | **EXIT 0**。lint / format:check / typecheck / build 全通过；vitest **4 文件 14 项全通过**；pytest **198 项全通过**（Python 3.12.12，platform darwin） |
| `npm run verify:sources` | **EXIT 0**，输出「已核对 13 个归档源文件。」 |

### 5.2 构建态矩阵（独立重跑）

`I02_EVIDENCE=/tmp/i02-review-build-matrix.json npm run test:e2e` → **EXIT 0，2 passed**（`csp-lifecycle.spec.ts` + `desktop.spec.ts`）。

我方独立矩阵（`/tmp/i02-review-build-matrix.json`）实测：

- `app.isPackaged = false`；Electron `44.9.0` / Chromium `152.0.7977.167`。
- 生产 meta **存在且 1 个**：`default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'`。
- 页面响应 **无 `content-security-policy` header**（`responseCSP = null`）——与"生产仅 meta"交付选择一致。
- 阻断矩阵（`disposition` 全为 `enforce`）：`script-src-elem`（inline）、`script-src-elem`（未授权外部 script）、`img-src`、`connect-src`、`frame-src`、**`style-src-elem`（inline）**、**`style-src-attr`（inline）**。
- 效果判据：内联脚本标记**未执行**（`inlineExecuted=false`、`remoteExecuted=false`）、`fetchBlocked=true`、style 元素**未生效**、style 属性**未生效**、**CSSOM 属性赋值生效**（`cssom=true`）、`window.require === 'undefined'`。
- 本地 HTTP 接收端**零请求**（`receiverRequests = []`）。
- 隔离与来源：preferences `sandbox/contextIsolation=true`、`nodeIntegration=false`、`nodeIntegrationInWorker/InSubFrames=false`、`webSecurity=true`、`allowRunningInsecureContent=false`；同来源异窗口调用 health 返回 `{ok:false,error:'请求来源不受信任。'}`；后创建 contents 的 `will-navigate/will-frame-navigate/will-attach-webview` 监听数各为 1（全局加固生效）。
- 导航：`window.open` 与 `window.location.href=外部地址` 后 URL 不变、窗口数仍为 1。
- 恢复：崩溃后弹出 1 次提示并重建窗口；新窗口初始为"尚未检查"。

### 5.3 真实打包 executable 矩阵（独立重新打包 + 重跑）

| 步骤 | 实际结果 |
| --- | --- |
| `npm run package:dir` | **EXIT 0**（electron-builder 26.15.3，electron 44.9.0，darwin arm64，未签名本地包） |
| `ONTOLEARN_PACKAGED_EXECUTABLE=".../OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio" I02_EVIDENCE=/tmp/i02-review-packaged-matrix.json npm run test:e2e` | **EXIT 0，2 passed** |

我方独立打包矩阵（`/tmp/i02-review-packaged-matrix.json`）实测：`app.isPackaged = true`；meta 1 个且策略与源码生成结果逐字一致；响应无 CSP header；7 类 violation 全 `enforce`；接收端零请求；style 元素/属性被拦、CSSOM 生效；异窗口 sender 被拒；原生崩溃与无响应均触发（`events=['killed','unresponsive']`，`windows=3`），`inspectorClosedBeforeFaults=true`，三窗手动 health 全部 `ok`。

### 5.4 开发态矩阵（独立重跑，**未**使用 `I02_HMR=1`）

`npm run dev` 启动后，`ELECTRON_RENDERER_URL=http://127.0.0.1:5173 I02_EVIDENCE=/tmp/i02-review-dev-matrix.json npx playwright test tests/e2e/csp-lifecycle.spec.ts` → **1 passed**。

- **无生产 meta**（`meta = null`），符合"不得向开发页面直接注入会阻断 Refresh/HMR 的生产 meta"。
- 开发 header 实际下发：`default-src 'self'; script-src 'self' 'nonce-<随机>'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src http://127.0.0.1:5173 ws://127.0.0.1:5173; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'`。
- 阻断矩阵：内联脚本、未授权外部 script、img、connect、frame 均 `enforce`；接收端零请求；style 元素与 style 属性在开发态**允许**（Vite HMR 需要），CSSOM 允许。
- 原生崩溃/无响应与恢复同打包态（`killed`+`unresponsive`，3 窗，手动 health 成功）。
- 本轮**未运行** `I02_HMR=1`（按审查指令禁止写源探针），故 HMR 本身不在我方运行证据内（见 §6）。

### 5.5 构建产物独立核查

- 生产 HTML 实际内容（`apps/desktop/out/renderer/index.html`）：`<meta http-equiv="Content-Security-Policy" ...>` 位于 `<head>` **第一项**，`meta` 起始偏移 49 < `<script>` 494 < `<link>` 575 —— **meta 确实先于所有资源加载**。
- 产物内**无内联脚本**（仅一个外链 `<script type="module" crossorigin src="./assets/index-*.js">` 与一个外链 CSS），与生产 `script-src 'self'` 相容。
- `package-manifest.json` 声明的 `out/renderer/index.html`（`27641d72…`）与 `out/preload/index.js`（`c73129a6…`）与我方重算**逐字节一致**；`out/main/index.js` **不一致**（见 M-01）。

### 5.6 保护与冻结边界核查

- `frozen-files.json` 15 项 SHA-256：**0 处不一致**。
- `preexisting-files.json` 64 项 SHA-256：**0 处不一致**。
- `git diff -- apps/desktop/src/renderer/src/App.tsx apps/desktop/src/renderer/src/style.css`：**空**（HMR 探针写源已完全回滚）。
- `docs/iterations/I02/inputs/sources.json` 声明的 5 个来源文件哈希：**5/5 全部一致**；`docs/iterations/I02/inputs/csp-packaged-probe-2026-10-19.md` 与受保护原件 `docs/verification/csp-packaged-probe-2026-10-19.md` **逐字节相同**。
- 审查全程未修改任何实现、测试、依赖、配置或验收文件；`git status` 中受审前后差异仅为我方新增的本报告（外加派发方在本轮创建的 `docs/reviews/I02/branch-protection-preflight.md`、`docs/reviews/I02/round-1/tasks.json`，均非实现改动）。

### 5.7 我补充的独立探测（既有矩阵未覆盖）

在真实 packaged 应用上（`/tmp` 临时脚本，不入库）：

| 探测 | 实测结果 |
| --- | --- |
| `base-uri 'none'` 是否在 meta 交付下生效 | **生效**：注入 `<base href="https://evil.example/">` 触发 `base-uri` / `enforce` violation，`document.baseURI` 仍为本地 `file://`（base 元素被忽略） |
| `form-action 'none'` | **生效**：`form.submit()` 触发 `form-action` / `enforce`，本地接收端**零请求** |
| `object-src 'none'` | **生效**：`<object data="http://…/object">` 触发 `object-src` / `enforce` |
| 锚点同文档导航 | **可用**：`…/index.html` → `…/index.html#modules`，`scrollY=35.5`，模块标题可见；hash 变化后 `window.ontolearn.getEngineHealth()` 仍返回 `ok:true`（`isTrustedDocument` 的 hash 容差生效） |
| "暂不恢复"分支（真实 packaged） | **不重建窗口**（窗口数 1→1），原窗口仍在；用户手动 reload 后应用恢复为"尚未检查"且 bridge 存在 |
| "重新打开窗口"分支（真实 packaged） | **重建 1 个窗口**，旧窗口 `isDestroyed=true`，新窗口 URL 为本地 renderer、`status='尚未检查 · 当前仅开放连接检查能力。'`、`bridge='function'`（**无自动 health/任务重放**） |
| dev origin 校验失败路径 | **失败方式不合理**（见 M-03） |

---

## 6. 未验证事项与证据边界（明确不外推）

1. **Windows / Linux 生命周期**：未验证。`window-all-closed` 的"先建后销"规避逻辑仅在 macOS 路径被触及；非 darwin 平台的 `app.quit()` 行为无运行证据。
2. **签名 / 安装器 / 干净设备 / 正式发布**：未验证。本轮为未签名本地 `--dir` 包，不能作为安装或发布证据。
3. **开发态 CSS HMR 与 React Refresh 的实际写源探针**：按审查指令**未运行** `I02_HMR=1`。该结论仅来自开发者归档证据 `development-matrix.json`（`hmr: {css:true, reactRefresh:true, documentAndStateRetained:true}`）与 `dev-server.txt` 中的 `[vite] (client) hmr update /src/style.css`、`/src/App.tsx` 日志，我核对了该证据与源码回滚状态（`git diff` 为空），**但未由我本人重跑**。本轮独立确认的是：开发态**无生产 meta**、nonce header 正常下发、阻断矩阵成立、HMR 所需的 `style-src 'unsafe-inline'` 与 `connect-src ws://127.0.0.1:5173` 存在。
4. **真实原生对话框在"父窗口渲染进程已崩溃/已挂起"状态下的实际渲染**：未验证（两处测试均整体替换了 `dialog.showMessageBox`，见 M-02）。已验证的是"主进程发起了对话框请求、参数正确、用户选择分支行为正确"。
5. **I04 任务重连 / 项目与业务状态恢复**：按冻结范围不在本次交付内，本轮**未**验证，也**未**虚构。`design.md` 对 I04 的只读查询与对账边界描述与 PRD 10.3/12.5 不冲突。
6. **I01 存储事务保证**：本次未改动 `packages/engine` 与存储接口，本轮不声称新增任何存储保证。
7. **签名/公证、Updater、性能与容量**：M0 范围外。

---

## 7. 问题清单

> 严重程度定义：**阻断** = 冻结验收无法成立或引入安全/数据一致性缺陷；**中** = 不影响本次通过判定，但应在推送前处理或更正证据表述；**低** = 前向风险或交接缺口，可延期。

### M-01（中）生产构建不可复现：开发用随机 nonce 被写入生产主进程产物

- **文件位置**：`apps/desktop/electron.vite.config.ts:7`（`const devNonce = randomBytes(18).toString('base64')`）、`apps/desktop/electron.vite.config.ts:11`（`define: { __DEV_CSP_NONCE__: JSON.stringify(devNonce) }`，作用于 **main** 构建，无 `command` 条件）；消费点 `apps/desktop/src/main/index.ts:61`。
- **触发条件**：任何一次 `npm run build` / `npm run package:dir`（含生产打包）。
- **影响**：
  1. **生产产物字节不可复现**：`out/main/index.js` 每次构建都不同（本次实测三次哈希互不相同：`9780c6b9…`（开发者打包时）→ `52eea6b3…`（我方第一次重建）→ `c46c7844…`（我方第二次重建）），而 `out/preload/index.js` 与 `out/renderer/index.html` 逐字节稳定。
  2. **生产包内嵌一个永不使用的随机值**：该 24 字符 base64 字面量（实测产物内可见 `aSCIva1ByQUwu6n34FNgDZVl`）在打包态 `devURL` 为 `undefined`，对应分支永不执行；生产 meta 策略本身不含 nonce（`script-src 'self'`），故**不构成策略削弱**，但属不必要的敏感语义数据进入发行物。
  3. **既有证据不可由第三方复算**：`docs/iterations/I02/evidence/package-manifest.json` 中 `out/main/index.js` 的 `"equalsBuild": true` 与 `asarSha256` 仅在打包当时成立；我方按记录重算时该行**不成立**。`acceptance.md` 第 15 行"包内main/preload/HTML与打包前build逐字节一致见package-manifest"因此**不能被独立复现**（preload/HTML 两项可复现，main 不可）。
- **证据**：`shasum -a 256 apps/desktop/out/main/index.js` 连续两次重建结果不同；`grep -oE '[A-Za-z0-9+/]{24}' out/main/index.js` 命中随构建变化的字面量；对照 `package-manifest.json` 声明值 `9780c6b9…` 与我方 `52eea6b3…`。
- **修复建议**：
  1. 仅在 serve 模式生成 nonce，并把 `define` 限定到 dev：`command === 'serve' ? { define: { __DEV_CSP_NONCE__: JSON.stringify(randomBytes(18).toString('base64')) } } : {}`（生产不注入该常量），使生产主进程产物可复现；
  2. 或保留现状但在 `package-manifest.json` 中显式区分"可复现项（preload/renderer）"与"含一次性随机量项（main）"，并把 `equalsBuild` 的语义改述为"同一次构建产出的包内外字节一致"，避免第三方按记录复算时误判为实现漂移；
  3. 两者取其一即可解除本项。
- **不阻断理由**：冻结验收不要求可复现构建；运行时安全策略与功能行为在三种环境均已独立复现通过。

### M-02（中）原生对话框从未被真实渲染；自动化整体替换了 `dialog.showMessageBox`，且生产代码静默吞掉所有对话框异常

- **文件位置**：`apps/desktop/src/main/window-recovery.ts:19-33`（生产代码 `dialog.showMessageBox(window, …)` 与 `catch {}`）；测试替换点 `tests/e2e/csp-lifecycle.spec.ts:227-230`、`tests/e2e/native-recovery.cjs:21-24`。
- **触发条件**：渲染进程崩溃或无响应，需要向用户提示并征求"重新打开窗口 / 暂不恢复"选择。
- **影响**：
  1. **证据边界被高估**：两处自动化都把 `dialog.showMessageBox` **整体替换**为 `async () => ({response: 0})`，因此本轮全部证据只能证明"主进程发起了对话框请求、选项文案正确、用户选择分支行为正确"，**不能**证明在"父窗口渲染进程已崩溃 / 已挂起"这一实际状态下原生对话框能够渲染。`design.md` 第 31 行"自动化仅替代原生对话框的用户选择"与代码实际（替换整个 API）表述不一致；`acceptance.md` 第 15 行"记录两次 native 提示"同属该边界内。
  2. **静默失败路径**：生产代码 `catch {}` 吞掉一切异常（含原生对话框在崩溃态下无法创建、Electron API 抛错等）。若真实对话框无法显示，用户既看不到提示、也得不到重建窗口，且**无任何日志**，现象是"崩溃后窗口停住且无反应"。
- **证据**：两处测试文件中 `dialog.showMessageBox = async (…) => ({response: 0, …})` 的整体替换；`window-recovery.ts:32-34` 的空 `catch`（注释仅覆盖"父窗口被关闭"一种情形）；仓库内不存在任何真实调用原生对话框的用例。
- **修复建议**：
  1. **更正证据表述**（必须）：在 `design.md` / `acceptance.md` 中把结论改述为"已验证对话框请求与选项内容、用户选择分支（接受/暂不恢复）的行为；**未**验证崩溃/挂起父窗口下原生对话框的实际渲染"，避免按 AGENTS.md"验收结果明确区分静态、运行、打包和生产证据"被误读为生产级证据；
  2. **区分异常类型**（建议）：在 `catch` 中区分"父窗口已销毁"（当前静默跳过是合理的）与"其他异常"（至少写一条最小诊断日志，仍保持不自动重启的保守行为）；
  3. 可选：补一条不替换 `showMessageBox` 的原生手动用例，或在验收记录中把该点显式登记为"证据边界/待补"。
- **不阻断理由**：冻结验收要求的是"定义提示、重建和任务重连策略"及"崩溃/无响应恢复"的可运行证据；策略、请求内容与两个用户选择分支均已被独立复现（我方在真实 packaged 应用上另行验证了"暂不恢复不重建"与"重新打开窗口重建且状态为尚未检查"）。

### M-03（中）开发 origin / nonce 校验失败时，应用退化为"无窗口的静默僵尸进程"

- **文件位置**：`apps/desktop/src/csp.ts:16-18`（`throw new Error('INVALID_DEVELOPMENT_CSP')`）；抛出点 `apps/desktop/src/main/index.ts:60-67`——该 `contentSecurityPolicy(...)` 调用位于 `app.whenReady().then(() => { … })` 回调内部，且该 promise 以 `void` 修饰（`main/index.ts:55`）。
- **触发条件**：`ELECTRON_RENDERER_URL` 不是 `http://127.0.0.1:5173`（例如 `http://localhost:5173`），或 nonce 字符集非法。仓库自身配置下不会触发（`electron.vite.config.ts:34` `host:'127.0.0.1', port:5173, strictPort:true`；electron-vite `resolveHostname('127.0.0.1')` 返回 `127.0.0.1`，已核对其实现 `node_modules/electron-vite/dist/chunks/lib-DoUt4oMD.js:18`），打包态 `app.isPackaged=true` 亦不受影响。
- **影响**：异常逃逸出 `whenReady` 链成为 **unhandled rejection**；Electron 主进程**不退出**（Node 默认 `--unhandled-rejections=warn`），应用保持运行但**一个窗口都不创建**，唯一线索是 stderr 的 `UnhandledPromiseRejectionWarning`。对开发者表现为"应用双击后什么都没发生"，且无对话框、无日志文件。
- **证据**：本轮独立复现（`ELECTRON_RENDERER_URL=http://localhost:5173` 启动 `apps/desktop`）：
  - Playwright 侧：`firstWindow()` 15s 超时，`app.windows().length = 0`；
  - 直接启动 stderr：`(node:…) UnhandledPromiseRejectionWarning: Error: INVALID_DEVELOPMENT_CSP at contentSecurityPolicy (apps/desktop/out/main/index.js:4998:98)`。
- **修复建议**：
  1. 把策略生成移出 `whenReady` 回调，或在回调内用 `try/catch` 包裹；失败时调用 `dialog.showErrorBox(...)`（或 `console.error` + `app.exit(1)`）给出明确原因后退出，避免"活着的空应用"；
  2. 让期望 origin 由 Vite `server` 配置派生，而不是在 `csp.ts:16` 与 `electron.vite.config.ts:34` **重复硬编码端口**——否则一旦调整端口，正常开发流程必然触发该失败路径（当前两处字面量耦合是本项的根因之一）；
  3. 该失败路径属"安全控制的 fail-closed 行为"，方向正确；需要修的是**失败方式**，不是取消校验。
- **不阻断理由**：仅影响开发态且需人为错误配置才触发；冻结验收的三条正常路径（开发/构建/打包）均已独立复现通过。

### M-04（低）生产构建不再为 HTML 注入 nonce，未来若产物出现内联脚本将静默失效

- **文件位置**：`apps/desktop/electron.vite.config.ts:33`（`html: command === 'serve' ? { cspNonce: devNonce } : undefined`）；`apps/desktop/src/csp.ts:5`（生产 `script-src 'self'`，**无 nonce 源**）。
- **触发条件**：未来 Vite 版本、构建目标或插件变化导致生产 HTML 出现内联脚本（典型如 legacy 目标的 modulepreload polyfill、banner 注入）。
- **影响**：生产策略既无 `unsafe-inline` 也无 nonce 源，内联脚本会被**静默阻断**（白屏或局部功能缺失），且构建与测试不一定会报警——属于前向隐性风险。
- **证据**：当前锁定版本（Vite 8.3.4、现代目标）产物确无内联脚本，我已逐字核对 `out/renderer/index.html`（仅外链 module script + 外链 CSS）；基线提交 `1b6df7a` 对 build 也设置了 `cspNonce`，本次改动**移除**了该保护。
- **修复建议**：在 `design.md` 写明"生产 HTML 不得含内联脚本"并加一条构建后断言（扫描 `out/renderer/index.html` 确认无内联 `<script>`/`<style>` 内容）；或在生产 meta 与 HTML 之间引入**同一构建期 nonce**（两者同源于 `src/csp.ts`，不构成第三套手写策略）。
- **可延期**：可延期至 M1 引入 UI 库/构建目标变化之前处理。

### M-05（低）全局阻断文档级导航的约束未记入 design，交接给 I03/M1 时易踩坑

- **文件位置**：`apps/desktop/src/main/window-security.ts:20-21`（`will-navigate` / `will-frame-navigate` 一律 `preventDefault()`），对**所有** contents 生效。
- **触发条件**：M1/I03 的应用内路由若使用文档级跳转（非 hash、非 `history.pushState`）。
- **影响**：导航被静默阻止且无用户提示。当前 M0 唯一导航为 `<a href="#modules">` 锚点，**可用**（我方实测 hash 变化、滚动生效、且 hash 变化后 health 可信文档校验仍通过），故不构成当前缺陷；但该约束未写入 `design.md`，后续迭代容易误用整页跳转。
- **证据**：我方真实 packaged 实测 `…/index.html` → `…/index.html#modules`、`scrollY=35.5`、模块标题可见、`getEngineHealth()` 仍 `ok:true`；同时 `will-navigate` 对外部地址生效（`window.location.href` 后 URL 不变）。
- **修复建议**：在 `design.md` 增加一行约束"应用内路由必须使用 hash / history API；文档级跳转一律被 `will-navigate` 拒绝"，并在 I03/M1 的交接项中带上；`hardenWebContents` 注释亦可补一句。
- **可延期**：可延期至 I03 协议/路由设计时处理。

---

## 8. 历史问题逐项判断

### 8.1 开发者内部独立审查（`docs/reviews/I02/internal-review.md`）的 3 项建议

> 说明：该记录来自 I02 开发会话内的独立 agent 审查，**不是**本轮指定双审之一。以下是我基于实际代码与运行的独立判断。

| 编号 | 内部审查建议 | 本轮判断 | 依据 |
| --- | --- | --- | --- |
| H-1 | 区分 preferences 工厂与全 contents 导航加固；新窗口测试复制 preferences，不能声称事件 hook 会修正任意不安全构造器 | **已关闭** | `window-security.ts` 明确分为 `securePreferences()`（字段工厂）与 `hardenWebContents()`（行为加固），`design.md` 第 17 行亦分别表述；`csp-lifecycle.spec.ts:210-221` 断言的是"后创建 contents 的监听数 > 0"与"复制 preferences 后的字段值"，未越界声称 hook 能修正不安全构造器 |
| H-2 | 补充恢复选择的延迟竞态（responsive/close/quit/decline、hang→crash 合并、manual reload） | **已关闭** | `tests/unit/window-recovery.test.ts` 4 组用例覆盖上述竞态；我方在**真实 packaged 应用**上另行验证"暂不恢复不重建 + 手动 reload 可恢复"与"接受重建 + 旧窗销毁 + 新窗'尚未检查'"，行为与单测一致 |
| H-3 | native 驱动 bootstrap 在退出/无响应时可能不结束 → 需有界竞速、socket close 拒绝、finally 清理 | **已关闭** | `tests/e2e/native-driver.ts` 实现三段等待 + 45s deadline 竞速 + socket close 拒绝 + `finally` 清理；`tests/unit/native-driver.test.ts` 覆盖"永不回复时有界退出+kill+close"与"启动失败立即拒绝"；本轮三套矩阵中 native 段均为 `result: PASS`、`inspectorClosedBeforeFaults: true` |

**另核对开发者内部记录中"两项非阻断建议"的一句话修正**（status.md 所述"措辞"建议）：`design.md` 第 31 行"自动化仅替代原生对话框的用户选择"与代码实际不符（替换的是整个 API）——此点即本报告 **M-02**，**未完全关闭**，需按 M-02 建议更正表述。

### 8.2 本轮问题在后续复审时的跟踪状态

| 编号 | 当前状态 | 是否阻断 | 复审时需要看到的关闭证据 |
| --- | --- | --- | --- |
| M-01 | **未关闭** | 否 | 生产 `out/main/index.js` 两次独立构建哈希一致；或 `package-manifest.json` 就"含一次性随机量项"给出明确标注与不可复现说明 |
| M-02 | **未关闭** | 否 | `design.md`/`acceptance.md` 对"原生对话框未实际渲染"作出明确证据边界说明；`window-recovery.ts` 的 `catch` 区分异常类型并留最小诊断 |
| M-03 | **未关闭** | 否 | 校验失败时给出明确错误并退出（或显示错误框），不再出现"活着的空应用"；期望 origin 不再与端口字面量重复耦合 |
| M-04 | **未关闭** | 否 | 允许延期至 M1：design 记录"生产无内联脚本"约定，或构建后断言落地 |
| M-05 | **未关闭** | 否 | 允许延期至 I03：design 记录路由约束 |

> 上述五项均**不影响**本轮"通过"判定；若在下一候选提交中修改实现/测试/配置/依赖/验收文件，按 `goal-objective.md` 第五节第 5 条，须对新候选版本重新双审，旧版结论不得沿用。

### 8.3 对冻结要求与门禁的逐条核对（结论：通过）

| 冻结验收（`scope.md` I02 行 / C1 原文） | 本轮判定 | 依据 |
| --- | --- | --- |
| 单配置生成开发/生产策略 | **满足** | `src/csp.ts` 单一来源，同时供 `electron.vite.config.ts`（构建期 meta）与 `main/index.ts`（开发 header）使用 |
| 评估后固化生产 meta 或 meta+header，记录锁定版本、交付差异与理由 | **满足** | 选定"生产仅 meta、开发 header"；`design.md` 第 7–9 行给出理由、差异与后续"若选并存须同源生成"的约束 |
| 开发 nonce/HMR 不受生产 meta 误阻 | **满足（部分依赖归档证据）** | 我方实测开发态 `meta=null` + nonce header 正常；HMR 写源探针按指令未运行，仅有归档证据（见 §6.3） |
| 统一窗口安全加固 | **满足** | `securePreferences` 工厂 + 全局 `hardenWebContents` + `app.enableSandbox()` + session 权限全拒；实测后创建 contents 监听数与 preferences 均符合 |
| 来源与主 frame 校验 | **满足** | `event.sender` + `event.senderFrame` + `isTrustedDocument` 三重；实测同来源异窗口被拒；hash 变化仍放行 |
| 渲染崩溃/无响应恢复 | **满足** | 原生 `killed` + `unresponsive` 均触发，3 窗重建，手动 health 成功；不自动重放 |
| 开发/构建/真实打包三环境正常 UI/CSS/health/导航/隔离 | **满足** | 三环境独立复现（§5.2–5.4），锚点导航与异窗口拒绝均实测 |
| 三环境内联脚本/资源/连接/frame 阻断矩阵 | **满足** | 三环境均 `enforce` + 接收端零请求；我方另补 `base-uri`/`form-action`/`object-src` 同样 `enforce` |
| 恢复不得重复写入 | **满足** | 恢复路径不调用引擎、不重放请求；重建窗口初始为"尚未检查"（实测） |
| 当前仅 health 的恢复实测 | **满足** | 三窗手动 health 均 `ok`，`capabilities:["health"]` |
| 任务重连在 I04 实现后联验，不虚构尚不存在的任务 | **满足** | `design.md` 第 27 行只定义接入边界（project/job 身份、权威持久 job/提交标记只读查询、旧通知拒绝、零提交/部分轮次/提交响应丢失/完成后取消四类联验），未新增虚构运行方法 |

**无阻断问题遗留；关键验收项均可验证并已验证 → 出具"通过"。**

---

## 9. 结论与门禁意见

1. **最终结论：通过（Pass）。**
2. **问题处理结论**：M-01、M-02、M-03 为非阻断但**建议在推送前处理**（M-01、M-03 涉及构建可复现性与失败路径，M-02 涉及证据表述准确性，均不改变本次受审实现的功能与安全语义，处理后按 `goal-objective.md` 第五节第 5 条走新候选与重新双审）；M-04、M-05 允许**明确延期**至 M1 / I03，但需在 `design.md` 留一行约束记录。
3. **本模型方的通过意见仅覆盖本轮 base→head 候选 `2cc03da`**；不代表另一模型方结论，也不构成推送/合并授权。是否推送与合并由总控按 `goal-objective.md` 第六节门禁（双模型同版本明确通过、阻断问题全关闭、待推送实现与受审实现一致）独立判定。
4. **本轮未修改任何实现、测试、依赖、配置或验收文件**；未提交、未推送、未切换分支；64 项受保护文件与 15 项冻结文件在审查前后哈希均 100% 一致。

---

### 附录 A：本轮实际执行的命令清单

```sh
# 状态与版本核验
pwd; git rev-parse --abbrev-ref HEAD; git rev-parse HEAD
git cat-file -t 1b6df7a…; git cat-file -t 2cc03da…
git merge-base --is-ancestor 1b6df7a… 2cc03da…
git diff --stat 1b6df7a… 2cc03da…; git log --oneline 1b6df7a…..2cc03da…
git ls-remote --heads origin feature/I02-csp-window-lifecycle

# 门禁
npm run check
npm run verify:sources
npm run test:e2e                                  # 构建态
npm run package:dir
ONTOLEARN_PACKAGED_EXECUTABLE="$PWD/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio" npm run test:e2e   # 真实打包
npm run dev + ELECTRON_RENDERER_URL=http://127.0.0.1:5173 npx playwright test tests/e2e/csp-lifecycle.spec.ts   # 开发态（未设 I02_HMR=1）

# 产物与哈希
shasum -a 256 apps/desktop/out/{main/index.js,preload/index.js,renderer/index.html}
# 15 项冻结 + 64 项保护 SHA-256 逐项重算比对（/tmp 内 python 脚本）

# 独立补充探测（/tmp 临时脚本，不入库）
node /tmp/i02-adversarial-probe.mjs   # base-uri / form-action / object-src
node /tmp/i02-probe2.mjs              # 锚点导航 + hash 后 health
node /tmp/i02-probe4.mjs              # 暂不恢复 / 重新打开窗口 两分支
node /tmp/i02-probe5.mjs              # dev origin 校验失败路径
ELECTRON_RENDERER_URL=http://localhost:5173 node_modules/.bin/electron apps/desktop   # 失败路径 stderr
```

### 附录 B：环境

macOS 27.0.1 arm64（darwin arm64）｜Node v24.15.0｜npm 11.12.1｜uv 0.11.12｜Python 3.12.12｜Electron 44.9.0 / Chromium 152.0.7977.167｜Vite 8.3.4｜electron-vite 6.0.0｜electron-builder 26.15.3｜Playwright 1.64.1。
