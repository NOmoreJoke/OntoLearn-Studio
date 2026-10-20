# I02 / C1 显式 CSP 与窗口生命周期 — 独立对抗性审查报告（Round 2）

- 报告路径：`docs/reviews/I02/round-2/minimax-m31flash.md`
- 任务标识：`I02-R2-MiniMax-M31Flash-20261020-0900`
- 审查模型：MiniMax M3.1-Flash（MiniMax 3.1 Flash）｜思考程度：xhigh
- 审查角色：独立对抗性审查者（只读）
- 报告日期：2026-10-20（Asia/Shanghai）

---

## 0. 最终结论

**通过（Pass）——但仅针对本轮冻结的 I02 / C1 验收范围与候选 `76b9d18`；本报告不构成推送/合并授权，远端 CI 门禁仍未闭合。**

冻结的 I02 / C1 全部验收项在开发态、构建态、真实 macOS arm64 打包 executable 三套环境中**由本审查者独立复现**；产品源码 `apps/`、`packages/`、依赖与协议相对 Round 1 候选 `2cc03da` **逐字未变**（`git diff 2cc03da 76b9d18 -- apps packages package.json package-lock.json uv.lock` 输出为空，已实测）。

本轮共提出 **8 项问题：0 项阻断，3 项中（native 夹具取焦硬前提导致的可复现偶发失败／CI 跨平台零证据／M-03 失败方式），5 项低**。其中 R2-01/R2-02 指向**合并门禁**而非 C1 验收本身，但必须明确记录：**GitHub 90s 超时与本机旧 timeout 的根因至今未被证实，候选方案不得被表述为"已修复根因"**。

历史意见复核：M-01 **按证据标注路线关闭**（代码未修，残余 R2-05）；M-02 **证据边界部分关闭**、**静默 catch 残余未关闭**（R2-04）；M-03 **仍未关闭且本轮独立复现**（R2-03）；M-04 **仍未关闭**（延期 M1，附本轮实测佐证当前产物不触发）；M-05 **关闭**（约束已写入 design.md，残余 R2-08 为其实测化）；ZCode P3-1 仍未关闭（低，延期）；P3-2 同 M-03；**P3-3 关闭**（其前提"成为未处理拒绝"不成立）；ZCode O1 同 M-01；O2 关闭；内部 H-1/H-2/H-3 关闭。

---

## 1. 评审任务、模型及思考设置的来源记录

| 项目 | 实际值 | 来源 |
| --- | --- | --- |
| 任务标识 | `I02-R2-MiniMax-M31Flash-20261020-0900` | 本轮派发指令正文 + `docs/reviews/I02/round-2/tasks.json`（同批次创建，非本审查者写入） |
| 应用 | MiniMax Code（本会话） | 本会话自身 |
| 模型 | M3.1-Flash（MiniMax 3.1 Flash） | 本会话运行时上下文 `agent-context` 标注 `MiniMax-M3.1-Flash`；与 `round-2/tasks.json` 的 `"model": "M3.1-Flash"` 一致 |
| 思考程度 | xhigh | 本轮派发指令明确指定；与 `round-2/tasks.json` 的 `"thinking": "xhigh"` 一致；`tasks.json` 记录任务创建时原生 UI 实际显示 `xhigh` |
| 项目路径 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio` | 派发指令正文；本轮由 `git rev-parse --show-toplevel` 独立核验一致 |
| 分支 | `feature/I02-csp-window-lifecycle` | 派发指令正文；`git branch --show-current` 独立核验一致 |
| base / head | `1b6df7a220fc9a67d7046133a340085f03f0a96c` → `76b9d18bd87b9090551eb0dc39dfd6aa061eea79` | 派发指令正文；`round-2/tasks.json` 一致；`git rev-parse HEAD` 独立核验 |
| 报告路径 | `docs/reviews/I02/round-2/minimax-m31flash.md` | 派发指令正文 + `goal-objective.md` 第四节第 6 条命名约定 |
| 是否读取另一模型本轮报告 | **否** | 本轮全程未打开 `docs/reviews/I02/round-2/zcode-glm53.md`（若存在），未推断、未引用另一模型任何结论；`round-2/` 下我仅读取派发方公共证据（`tasks.json`、`review-start-integrity.json`、`preparation.md`、`candidate-validation.json`、三份 `*direct-loop.json`、CI 失败日志、docker 诊断元数据），以及 Round 1 允许读取的两份历史报告 |
| 是否预设结论 | 否 | 全部结论由本轮实际读取代码与实际运行结果得出；历史"通过"不作为本轮依据 |

**设置核验方式**：以本会话运行时上下文（模型标识、思考档位）为准，用 `round-2/tasks.json`（派发方创建）交叉核对模型、思考档位、base/head、仓库路径四项；不依赖"上次设置"或截图。

---

## 2. 项目路径、分支、base SHA、head SHA

| 项目 | 实际值 | 核验方式（本轮实际执行） |
| --- | --- | --- |
| 仓库绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio` | `git rev-parse --show-toplevel` |
| 分支 | `feature/I02-csp-window-lifecycle` | `git branch --show-current` |
| base SHA | `1b6df7a220fc9a67d7046133a340085f03f0a96c` | 派发指令；`git merge-base --is-ancestor base head` 成立 |
| head SHA | `76b9d18bd87b9090551eb0dc39dfd6aa061eea79` | `git rev-parse HEAD` |
| 提交关系 | base → head 共 3 笔：`2cc03da`（实现）、`caa0847`（流程证据）、`76b9d18`（Round 2 修订） | `git log --oneline base..head` |
| 审查范围规模 | 123 文件 / +9520 / −23（其中产品代码仅 6 个文件） | `git diff --stat base head` |
| Round 2 相对 Round 1 的实现差异 | **产品 `apps/`/`packages/`/依赖/锁文件为空**；仅 `tests/`（4 文件）、`.github/workflows/ci.yml`、`docs/` | `git diff --stat 2cc03da 76b9d18 -- apps packages package.json package-lock.json uv.lock` → 无输出 |
| 是否已推送 | **否**（PR#3 仍停在 `caa0847`，未合并） | `docs/reviews/I02/status.md`；本轮未执行任何 push/merge |
| 本轮工作区影响 | 审查前后 `git status --porcelain` 均为 17 条且完全相同；16 冻结 + 64 保护哈希 0 差异 | 见 §5.6 |

---

## 3. 需求与验收依据（实际读取清单）

本轮**实际完整读取**下列原始要求，未以开发者验收摘要替代原要求：

1. `AGENTS.md`（仓库根，10 条开发规则全文）。
2. `docs/iterations/I01/inputs/goal-objective.md` 全文——重点**第四节"两个第三方模型的审查要求"**（第 57–94 行，含第 65–66 行报告路径命名、第 92 行"阻断问题未关闭或关键验收仍无法验证不得出具通过"）与**第五、六节**（修复复审循环、推送合并门禁）。
3. `docs/iterations/I01/inputs/scope.md` 全文——**I02 / C1 行完整冻结验收**（第 25 行）、非目标与未决边界（第 33–39 行）、统一门禁（第 41–50 行）。
4. `docs/architecture/m0-review-and-update-plan-2026-10-19.md`——**C1 全文（第 145–153 行）**，含"不得向开发页面注入会阻断 HMR 的生产 meta""生产脚本不允许 unsafe-inline/unsafe-eval""只检查 meta 存在或控制台没有报错不能视为通过"等原文。
5. `docs/prd/PRD-本体学习与落地Agent工作台.md` V0.6——**8.7（第 640–646 行）、10.3（第 720–726 行）、10.4（第 728–737 行）、12.5（第 840–846 行）**原文。
6. `docs/iterations/I02/design.md`、`acceptance.md`、`commands.md`、`docs/iterations/I02/evidence/*`、`docs/iterations/I02/inputs/*`（含受保护的原始 CSP 实测逐字快照与 `sources.json`）。
7. `docs/reviews/I02/round-1/minimax-m31flash.md`、`docs/reviews/I02/round-1/zcode-glm53.md`、`docs/reviews/I02/round-1/processing.md`、`docs/reviews/I02/internal-review.md`、`docs/reviews/I02/native-dialog-probe/README.md`、`docs/reviews/I02/package-manifest-semantics.json`、`docs/reviews/I02/status.md`。

**未采纳为验收依据**：`docs/iterations/I02/acceptance.md` 与 `status.md` 仅作"声明"核对；`round-2/preparation.md`、`candidate-validation.json` 仅作待核对对象，不作通过依据。

---

## 4. 已检查范围

### 4.1 产品实现（逐行读完）

| 文件 | 检查重点 |
| --- | --- |
| `apps/desktop/src/csp.ts`（新增 26 行） | 单配置来源、开发/生产变体、指令集合与顺序、origin/nonce 校验与 fail-closed、序列化结果 |
| `apps/desktop/electron.vite.config.ts`（改 25 行） | `defineConfig` 工厂 + `command` 分支、生产 meta 插件（`apply:'build'` / `order:'post'` / `injectTo:'head-prepend'`）、`html.cspNonce` 仅 serve、`server.host/port/strictPort`、main `define` 无条件注入 |
| `apps/desktop/src/main/index.ts`（改 50 行） | `app.enableSandbox()` 时机、`web-contents-created` 注册时机、`createWindow` 顺序与先建后销、`closed` 回调不误清空、health IPC 三重校验、dev header 注册条件与异常逃逸路径、`before-quit` 标志 |
| `apps/desktop/src/main/window-security.ts`（新增 24 行） | preferences 工厂字段完整性、全 contents 加固（popup/导航/子 frame/重定向/webview） |
| `apps/desktop/src/main/window-recovery.ts`（新增 54 行） | 崩溃/无响应判定、提示去重、`did-finish-load` 状态清理、恢复前置条件、异常吞并范围、退出与窗口销毁保护 |
| `apps/desktop/src/main/trusted-document.ts`（未改） | hash 容差、协议/主机/端口/路径/查询全等、URL 规范化与百分号编码边界 |
| `apps/desktop/src/main/engine.ts`（未改） | health 子进程超时/限量/清理，恢复路径是否可能重复写入或遗留子进程 |
| `apps/desktop/src/preload/index.ts`（未改） | 暴露面是否只有 `getEngineHealth` |
| `apps/desktop/src/renderer/src/App.tsx`（未改） | 锚点导航、health 手动触发、初始"尚未检查"、是否存在内联 style |

### 4.2 测试与夹具

`tests/e2e/csp-lifecycle.spec.ts`（314 行）、`tests/e2e/native-driver.ts`（113 行）、`tests/e2e/native-recovery.cjs`（112 行）、`tests/unit/{csp,window-recovery,native-driver}.test.ts`、`tests/e2e/desktop.spec.ts`、`playwright.config.ts`。

### 4.3 CI 与流程证据

`.github/workflows/ci.yml`（新增 Linux sandbox 准备步骤与 `pw:browser`/`I02_EVIDENCE`）、`docs/reviews/I02/round-2/*`（preparation、candidate-validation、ci-attempt-1-failed、linux-attempt-2、build-native-timeout-{before,with}-focus、check-final、unit-*、三份 `*direct-loop.json`、docker-diagnostic 元数据）、`docs/reviews/I02/round-1/*`、`docs/iterations/I02/preexisting-files.json`（64）、`docs/reviews/I02/round-2/frozen-files.json`（16）。

### 4.4 第三方实现事实核对（读取本机 `node_modules`）

- `node_modules/playwright-core/lib/coreBundle.js:45670`：Electron 启动**仅在 Linux** 且 `chromiumSandbox !== true` 时注入 `--no-sandbox`（决定 R2-06 的平台适用性）。
- `node_modules/vite/dist/node/chunks/node.js:31767-31770, 32151-32215`：`injectCspNonceMetaTagHook` 为 preHook、`injectNonceAttributeTagHook` 为 **postHook**，会遍历并给所有 `<script>/<style>/<link rel=stylesheet|modulepreload|preload>` 补 `nonce`（覆盖 `@vitejs/plugin-react` 的 preamble），是开发态 React Refresh 可在 `script-src 'self' 'nonce-…'` 下工作的机制依据。
- `node_modules/@vitejs/plugin-react/dist/index.js:190`、`:8-12`：preamble 以 inline `<script type="module">` 注入，故必须依赖上述 postHook 补 nonce。

---

## 5. 独立验证：命令与实际结果

以下全部由本审查者**实际执行**，工作目录均为仓库根。临时产物一律写入 `/tmp`，未写入仓库；asar 仅提取到 `/tmp`，未提取到仓库根；未运行 `I02_HMR=1` 写源探针；未修改任何实现/测试/配置/依赖/验收文件；未提交、未推送、未切换分支。

### 5.1 静态与单元门禁（不启动桌面）

| 命令 | 实际结果 |
| --- | --- |
| `npx vitest run` | **EXIT 0** — Test Files 4 passed / Tests **15 passed**（含 6 项恢复竞态、3 项 native 驱动故障/诊断模拟） |
| `npx eslint . --max-warnings 0` | **EXIT 0**，无输出 |
| `npx prettier --check .` | **EXIT 0** — "All matched files use Prettier code style!" |
| `npx tsc --noEmit -p apps/desktop/tsconfig.json` | **EXIT 0** |
| `node scripts/verify-sources.mjs` | **EXIT 0** — "已核对 13 个归档源文件。" |
| `uv run --frozen pytest -q` | **EXIT 0** — **198 passed in 5.49s** |

> 未整跑 `npm run check`：其 `npm run build` 段会写 `apps/desktop/out/`，与桌面运行验证共用该目录，故拆为"静态/单元先行 + 单独 `npm run build`"，覆盖等价。

### 5.2 构建态矩阵（`npm run build` → Playwright）

`npm run build` → **EXIT 0**（`out/main/index.js` 167.55 kB、`out/preload/index.js` 0.20 kB、`out/renderer/index.html` 0.70 kB）。

**第一次运行：FAILED**（`I02_EVIDENCE=/tmp/i02-r2-mavis-build-matrix.json npm run test:e2e` → 1 failed / 1 passed，失败于 native 段）：

```
Error: native exit 1/null: {"executable":"…/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron",
"args":["--user-data-dir=/tmp/ontolearn-i02-D1YERZ","…/apps/desktop"],"exitCode":1,…}
```

该次证据（`/tmp/i02-r2-mavis-build-matrix.json` → `nativeRecovery`）显示：`events:["killed"]`（崩溃已触发）、`windows:2`、`prompts:1`、`health` 两次均 `ok:true`、`hangFault:"executeJavaScript-infinite-loop"`（新故障注入已生效）、`hangTrigger:{visible:true, focused:false}`、`error:"native hang input requires a focused visible window"`。→ 见 **R2-01**。

**第二次运行（同命令，间隔约 25 秒）：PASS**（`/tmp/i02-r2-mavis-build-matrix-r2.json`）：

- `2 passed (20.4s)`；`result: PASS`；stage 走完 `launch → … → native-recovery → cleanup-enter`。
- 运行时：`app.isPackaged=false`、Electron **44.9.0** / Chromium **152.0.7977.167**、`noSandboxSwitch=false`、Playwright 主进程 `hangMonitor=false`（loader 注入 `--disable-hang-monitor`）、native 子进程 `hangMonitorEnabled=true`。
- 生产 CSP meta **恰好 1 个**，内容 = `contentSecurityPolicy()` 生产变体逐字（`default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'`）；页面响应 **无 CSP header**（`responseCSP=null`），符合"生产仅 meta"。
- 阻断矩阵全部 `disposition=enforce`：`script-src-elem`×2（内联、未授权外部）、`style-src-elem`、`style-src-attr`、`connect-src`、`img-src`、`frame-src`；`inlineExecuted=false`、`remoteExecuted=false`、`fetchBlocked=true`、`styleElement=false`、`styleAttribute=false`、`cssom=true`、`window.require==='undefined'`；本地 HTTP 接收端 **零请求**（`receiverRequests: []`）。
- 导航/popup 被拒（URL 不变、窗口数仍 1）；同来源异窗口 health 返回 `{ok:false,error:'请求来源不受信任。'}`（`foreignSenderRejected=true`）。
- native：`result PASS`、`events:['killed','unresponsive']`、`windows:3`、`prompts:2`、`inspectorClosedBeforeFaults=true`、三窗手动 health 全 `ok`；`hangTrigger.focused=true`。

### 5.3 真实打包 executable 矩阵

`npm run package:dir` → **EXIT 0**（electron-builder 26.15.3，electron 44.9.0，darwin arm64，未签名本地包）。
`ONTOLEARN_PACKAGED_EXECUTABLE="…/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio" I02_EVIDENCE=/tmp/i02-r2-mavis-packaged-matrix.json npm run test:e2e` → **2 passed (22.9s)**，`result: PASS`。

- `app.isPackaged=true`、`noSandboxSwitch=false`、native `packaged=true`、`hangMonitorEnabled=true`。
- meta 1 个且策略同上；`responseCSP=null`（无响应头）。
- 7 类 violation 全 `enforce`；内联/外部脚本未执行；`fetchBlocked=true`；style 元素/属性被拦、CSSOM 生效；`require==='undefined'`；接收端 **零请求**；异窗口 sender 被拒。
- native：`events:['killed','unresponsive']`、`windows:3`、`prompts:2`、`inspectorClosedBeforeFaults=true`。

### 5.4 开发态矩阵（**未设 `I02_HMR=1`**）

`npm run dev`（后台）→ dev server 就绪（`http://127.0.0.1:5173` HTTP 200）。
`ELECTRON_RENDERER_URL=http://127.0.0.1:5173 I02_EVIDENCE=/tmp/i02-r2-mavis-dev-matrix.json npx playwright test tests/e2e/csp-lifecycle.spec.ts` → **1 passed (19.9s)**，`result: PASS`。

- **无生产 meta**（`meta=null`），符合"不得向开发页面注入会阻断 HMR 的生产 meta"。
- 实际下发 header：`default-src 'self'; script-src 'self' 'nonce-gODuFAZIXUTVpgs46QLA8kyn'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src http://127.0.0.1:5173 ws://127.0.0.1:5173; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'`。
- 阻断矩阵 `enforce`：`script-src-elem`×2、`connect-src`、`img-src`、`frame-src`；接收端零请求；style 元素/属性在开发态**允许**（HMR 需要）、CSSOM 允许；`foreignSenderRejected=true`。
- native：`events:['killed','unresponsive']`、`windows:3`、`prompts:2`、`hangTrigger.focused=true`。

### 5.5 我补充的独立探测（冻结矩阵未覆盖，脚本仅在 `/tmp`）

| 探测 | 实测结果 |
| --- | --- |
| `base-uri 'none'` 是否在 meta 交付下生效 | **生效**：注入 `<base href="https://evil.example/">` 触发 `base-uri/enforce`，`document.baseURI` 仍为本地 `file://…/app.asar/out/renderer/index.html`（base 被忽略） |
| `form-action 'none'` | **生效**：`form.submit()` 触发 `form-action/enforce`，本地接收端 **零请求** |
| `object-src 'none'` | **生效**：`<object data="http://…/object">` 触发 `object-src/enforce` |
| 渲染端暴露面 | `window.ontolearn` 仅 `getEngineHealth`（无其他自有键）；`window.ipcRenderer`、`window.require`、`window.process`、`window.electron` **均为 `undefined`** |
| 渲染端发起的 `location.reload()` | **被全局 `will-navigate` 阻止**：`location.reload()` 无异常抛出，但页面未重载（预置 `window.__marker` 存活，2s 后仍在） |
| `history.pushState` 后的可信文档校验 | `history.pushState({}, '', '/modules')` 在 file:// 文档上**静默成功**（无异常），文档 URL 变为 `file:///modules`；此后 `getEngineHealth()` 由 `{ok:true,…}` 变为 **`{ok:false,error:'请求来源不受信任。'}`** |
| 渲染端发起 `history.pushState` 是否被加固拦截 | **未被拦截**（`will-navigate`/`will-frame-navigate` 不覆盖同文档 pushState），故上条风险真实可达 |
| M-03 失败路径复现 | `ELECTRON_RENDERER_URL=http://localhost:5173 node_modules/.bin/electron apps/desktop` → stderr `UnhandledPromiseRejectionWarning: Error: INVALID_DEVELOPMENT_CSP`；进程**不退出**（12s 后由 `timeout` 结束，EXIT=124）、**不创建任何窗口**、无其他诊断 |
| 包内字节一致性（asar 提取到 `/tmp`） | `out/renderer/index.html` = `27641d72…`、`out/preload/index.js` = `c73129a6…` 与构建产物**逐字节一致**；`out/main/index.js` 与 asar 版本**仅差一个 24 字符 base64 字面量**（build `gODuFAZIXUTVpgs46QLA8kyn` vs asar `ziEtSLEe9jN4mLKpsFjDzh2A`），掩码后全文相同（两侧均 167231 字符） |
| 产物 HTML 结构 | `out/renderer/index.html` 中 CSP meta 为 `<head>` **第一项**（先于 `<meta charset>`、外链 `<script>`、外链 `<link>`）；全文**仅 1 个外链 module script + 1 个外链 CSS，无内联 script/style、无 modulepreload 内联 polyfill 块** |

### 5.6 保护与冻结边界核查（审查前后各一次）

- `docs/reviews/I02/round-2/frozen-files.json` **16 项** SHA-256：工作区 **0 处不一致**；对照 `76b9d18` 提交树 **0 处不一致**。
- `docs/iterations/I02/evidence/frozen-files.json`（16 项）：**0 处不一致**。
- `docs/iterations/I02/preexisting-files.json` **64 项** SHA-256：**0 处不一致**。
- `docs/reviews/I02/round-1/frozen-files.json`（15 项）对照 `2cc03da` 提交树：**0 处不一致**（对照当前工作区有 7 处差异，恰为本轮候选合法改动的 4 个测试文件 + 3 个 I02 文档，与 `git diff --name-status 2cc03da 76b9d18` 完全吻合）。
- `git diff -- apps/desktop/src/renderer/src/App.tsx apps/desktop/src/renderer/src/style.css`：**空**（HMR 写源探针已回滚；本轮亦未运行该探针）。
- 审查前后 `git status --porcelain` 均为 **17 条且完全相同**；`git branch --show-current` = `feature/I02-csp-window-lifecycle`；`git rev-parse HEAD` = `76b9d18…` 未变；`git log` 顶部仍为 `76b9d18`，我未产生任何提交。
- 临时产物：全部在 `/tmp`（`/tmp/i02-r2-mavis-*.json`、`/tmp/i02-r2-mavis-*.mjs`、`/tmp/i02-r2-mavis-asar/`、`/tmp/i02-r2-mavis-dev-server.log`）；`test-results/` 已被仓库 `.gitignore` 覆盖（`gitignore:14`），未污染受审工作区。

---

## 6. 未验证事项与证据边界（明确不外推）

1. **Windows / Linux 原生生命周期与 CI**：新候选 `76b9d18` **从未在 Linux 或 Windows 上运行**。`round-2/candidate-validation.json` 自述 `"remoteCI": "not yet tested for new candidate"`。我方只能确认 macOS arm64 结果。GitHub 90s 超时与本机旧 timeout 的根因**未被证实**，候选方案不得被表述为已证明根因（详见 R2-01/R2-02）。
2. **开发态 CSS HMR / React Refresh 写源探针**：按指令**未运行 `I02_HMR=1`**。本轮独立确认的是：开发态无生产 meta、nonce header 实际下发、`style-src 'unsafe-inline'` 与 `connect-src ws://127.0.0.1:5173` 存在、阻断矩阵成立、React 正常挂载且 health 通过；并从 Vite 源码确认 nonce 补全为 postHook（覆盖 plugin-react 的 inline preamble），机制上支持归档证据 `hmr:{css:true,reactRefresh:true,documentAndStateRetained:true}`。**该 HMR 结论仍属归档证据，非本轮本人重跑。**
3. **真实原生对话框在崩溃/挂起父窗口下的渲染**：本轮**未**复现该路径。既有 `docs/reviews/I02/native-dialog-probe/README.md` Run 2 是同一产品源码（`apps/` 逐字未变）下的真实 sheet + AX + 截图证据，本轮采信为**历史运行证据**，不当作本轮新证据；两处自动化至今仍**整体替换** `dialog.showMessageBox`（见 R2-04 与 §8 M-02）。
4. **签名 / 安装器 / 干净设备 / 正式发布 / 更新器 / 性能与容量**：未验证。本轮为未签名本地 `--dir` 包。
5. **I04 任务重连与项目业务状态恢复**：按冻结范围不在本次交付内，本轮未验证也未虚构；仅核对 `design.md` 第 27 行只定义接入边界。
6. **I01 存储事务保证**：`packages/engine` 与存储接口未被本迭代改动，本轮不声称新增任何存储保证。
7. **Round 2 新增 native 夹具的"销毁后 Promise 拒绝"分支**：`native-recovery.cjs` 显式捕获该拒绝，但**本轮三次 native 运行均未实际触发**该分支（`hangScriptDisposed` 未出现），与 `preparation.md` 的自述一致，不声称已运行。

---

## 7. 问题清单

> 严重程度：**阻断** = 冻结验收无法成立或引入安全/数据一致性缺陷；**中** = 不影响本次通过判定，但应在推送/合并前处理或更正表述；**低** = 前向风险或交接缺口，可延期。本轮 **0 阻断 / 3 中 / 5 低**。

### R2-01（中）Round 2 新 native 夹具的"取焦"硬前提导致用例可复现地偶发失败

- **文件位置**：`tests/e2e/native-recovery.cjs:46-72`（3 秒有界取焦确认 + 250ms 时二次复核 `isFocused()`）、`tests/e2e/native-driver.ts:30-35`（`child.on('close')` 拒绝路径）、`tests/e2e/csp-lifecycle.spec.ts:290-296`。
- **触发条件**：native 阶段窗口通过 3 秒取焦确认后，在投递输入前的 250ms 窗口内被其它前台活动夺走 OS 焦点（另一应用/另一测试进程/桌面 Agent 窗口回焦）。
- **影响**：
  1. **同一候选、同一命令、同一台机器，我方 2 次运行 1 次失败**（§5.2）。开发会话记录的"build 2/2、packaged 2/2、development 1/1 全部通过"**不能代表确定性**；该用例在本机存在与桌面并发活动强相关的失败率。
  2. 失败会以 `native exit 1/null` 呈现，与"真实原生崩溃"在日志上同形（`native-recovery.cjs` 的 `save(error)` → `app.exit(1)`），排障时易被误读为产品缺陷。
  3. 在 GitHub ubuntu runner（`xvfb-run`，无窗口管理器）中焦点状态比本机更不可控；该前提不满足会让 Quality job **快速变红**（好于旧方案 90s 挂起），但**是否变红取决于该前提能否被满足，而这一点在 Linux 上从未被验证**。
- **证据**：
  - 第 1 次：`/tmp/i02-r2-mavis-build-matrix.json` → `nativeRecovery.hangTrigger={visible:true,focused:false}`、`error="native hang input requires a focused visible window"`、`hangFault="executeJavaScript-infinite-loop"`、`events:["killed"]`、无 `unresponsive`；驱动报 `native exit 1/null`。
  - 第 2 次（同命令）：`2 passed`，`hangTrigger.focused=true`，`events:['killed','unresponsive']`。
  - 对照：`round-2/build-native-timeout-before-focus.json` 与 `build-native-timeout-with-focus.json` 均为 `error:"native recovery timeout"`、`events:["killed"]`、无 `unresponsive`——即旧的"渲染端定时器"故障注入在**加焦点后仍失败**，说明新方案真正起作用的是"直接无限循环"而非取焦；`preparation.md` 对此未夸大，本轮复核认可。
- **修复建议**：
  1. 把"必须 `isFocused()`"从**硬失败**降级为**软前提**：有界取焦失败时仍尝试投递输入并等待 `unresponsive`；若在上限内仍无 `unresponsive`，以**环境不具备**（如 `ENVIRONMENT_UNFOCUSED`）明确区分于"应用缺陷"，让用例给出可区分的结论而不是混淆的 `exit 1`。
  2. 更稳妥的替代：让 native 阶段不依赖桌面焦点——例如在夹具内以受控方式触发 `unresponsive`（Chromium 侧的 hang monitor 需要可见 widget + 输入 ack 超时，必要时用 `webContents.sendInputEvent` 之外的路径），或把"真实 unresponsive"降为 Windows/Linux CI 专项用例，本机用例只保留 `killed`。
  3. 失败信息中把夹具错误与产品错误加不同前缀（当前两者同为 `native exit 1`）。
- **处理结论**：**新发现，未关闭**。不阻断本轮 C1 冻结验收结论（产品行为未受影响）；但**阻断"CI 必绿"的推定**，合并前必须由远端 CI 实际验证。不得表述为"已修复 90s 超时根因"。

### R2-02（中）新候选在 Linux/Windows 上零运行证据，CI 修复与新夹具均未经跨平台验证

- **文件位置**：`.github/workflows/ci.yml:32-41`（新增 `Prepare Linux Chromium sandbox` 步骤）、`tests/e2e/csp-lifecycle.spec.ts:30-37`（`chromiumSandbox: true`）。
- **触发条件**：任何一次在 Linux/Windows 上执行 `npm run test:e2e`。
- **影响**：
  1. `chromiumSandbox: true` 在 Linux 上**首次真正启用 Chromium sandbox**（Playwright 仅在 Linux 且该选项非 true 时注入 `--no-sandbox`，见 `node_modules/playwright-core/lib/coreBundle.js:45670`），因此 C1 矩阵在 Linux 上进入了一个**全新且未验证**的运行条件；新 CI 步骤用 `sudo chown root:root` + `chmod 4755` 准备锁定 Electron 的 `chrome-sandbox` helper，是官方常规做法，方向正确，但**从未在目标 runner 上跑过**。
  2. Round 1 的 Linux 失败面**不限于** C1 native 段：同一次运行中 `desktop.spec.ts` 亦以 `Error: electronApplication.firstWindow: Target page, context or browser has been closed` 失败（`round-2/linux-attempt-2.txt:384-412`）。该现象的成因（worker teardown 30s 超时的连带效应 vs. xvfb 下 Electron 启动本身）**未区分**，因此不能断言"新方案只修好了 C1 段"。
  3. `round-2/docker-diagnostic/metadata.json` 自述 `notEquivalentTo: GitHub Ubuntu x64 runner`，**不构成** Linux 通过证据。
- **证据**：见上；`round-2/candidate-validation.json` 的 `"remoteCI": "not yet tested for new candidate"`。
- **修复建议**：以**新候选 push 后的远端 CI 实际全绿**作为合并前置条件（不得以本机或 Docker 结果替代）；同时在 CI 中保留 `I02_EVIDENCE` 与 `DEBUG: pw:browser` 产出，使任何再次失败可定位到 stage 级（本轮已新增 stage 标记，是有效改进）。
- **处理结论**：**新发现，未关闭**。属**合并门禁**未闭合项，不影响本轮 C1 验收结论；我**不**认定"已修复"，也不把 Docker 诊断当作 CI 通过。

### R2-03（中）M-03 未关闭：开发 origin/nonce 校验失败仍是"活着的空应用"（本轮独立复现）

- **文件位置**：`apps/desktop/src/csp.ts:14-18`（`throw new Error('INVALID_DEVELOPMENT_CSP')`）、`apps/desktop/src/main/index.ts:55-67`（该调用位于 `void app.whenReady().then(...)` 回调内，无 `catch`）。
- **触发条件**：`ELECTRON_RENDERER_URL` 不是 `http://127.0.0.1:5173`（如 `http://localhost:5173`），或 nonce 字符集非法；`new URL(origin)` 非法时抛的是 `TypeError [ERR_INVALID_URL]` 而非预期错误，同属静默失败。
- **影响**：异常逃逸出 `whenReady` 链成为 unhandled rejection；主进程**不退出**、**不创建任何窗口**、无错误框、无日志文件。开发表现为"双击后什么都没发生"，唯一线索是 stderr 的 `UnhandledPromiseRejectionWarning`。另外 `csp.ts:16` 与 `electron.vite.config.ts:34` **重复硬编码端口**，一旦调整端口，正常开发流程必然踩中该失败路径。
- **证据（本轮独立复现）**：`ELECTRON_RENDERER_URL=http://localhost:5173 timeout 12 node_modules/.bin/electron apps/desktop` → stderr `UnhandledPromiseRejectionWarning: Error: INVALID_DEVELOPMENT_CSP`；**EXIT=124**（进程 12 秒后仍存活被 timeout 终止）、**0 窗口**、无其他诊断；timeout 后无遗留进程。
- **修复建议**：把策略生成移出 `whenReady` 回调或在其内 `try/catch`，失败时 `dialog.showErrorBox` 或 `console.error` + `app.exit(1)`；期望 origin 由 Vite `server` 配置派生，消除重复硬编码。**该失败方向是 fail-closed（安全），需要修的是失败方式，不是取消校验。**
- **处理结论**：**历史问题 M-03 / ZCode P3-2 仍未关闭**（本轮独立复现，事实与 Round 1 一致）。允许延期，但须在**改动开发端口/启动配置之前**落实；本轮不认可"因三态正常通过而自动消失"。

### R2-04（中）M-02 残余未关闭：原生提示异常被静默吞掉，且与"应用崩溃"日志同形

- **文件位置**：`apps/desktop/src/main/window-recovery.ts:19-35`（`dialog.showMessageBox(window, …)` 与空 `catch {}`）；替换点 `tests/e2e/csp-lifecycle.spec.ts:241-245`、`tests/e2e/native-recovery.cjs:23-26`。
- **触发条件**：原生对话框无法创建（无显示环境、父窗口状态异常、Electron API 抛错），或恢复重建时 `createWindow()` 同步抛出。
- **影响**：
  1. **静默失败**：用户既看不到提示、也得不到重建窗口，且**无任何日志**，现象是"崩溃后窗口停住且无反应"；`catch {}` 同样吞掉 `reopen()` 的同步异常（此时旧窗口因"先建后销"顺序而保留，用户看到的是一个死窗口）。
  2. **与 R2-01 叠加**：夹具侧错误同样表现为 `native exit 1`，产品侧静默吞异常也表现为"没有提示也没有恢复"，两侧在日志上都难以区分（产品侧甚至没有日志）。
- **证据**：`window-recovery.ts:32-34` 的空 `catch`（注释仅覆盖"父窗口被关闭"一种情形）；两处测试整体替换 `dialog.showMessageBox`；仓库内不存在不替换该 API 的**自动化**用例（真实 UI 证据仅 `native-dialog-probe/README.md` Run 2 的历史人工/CUA 记录）。
- **修复建议**：`catch` 中区分"父窗口已销毁"（静默跳过合理）与"其他异常"（写一条最小诊断日志，保持不自动重启的保守行为）；对 `reopen()` 单独包一层并记录。
- **处理结论**：**M-02 的证据边界部分已关闭**（`design.md`/`acceptance.md` 措辞已改为"整体替换整个 API"，并由 Run 2 补真实原生 sheet 证据）；**静默 catch 残余仍未关闭**，允许延期但须在 M1 前登记并落实。

### R2-05（低）M-01 残余：生产 main 仍内嵌随机开发 nonce，且"包内外一致"会被后续 `npm run dev` 破坏

- **文件位置**：`apps/desktop/electron.vite.config.ts:7,11`（`devNonce` 无条件生成、`define` 无条件作用于 main 构建）、消费点 `apps/desktop/src/main/index.ts:61`。
- **触发条件**：任何一次 `npm run build` / `npm run package:dir`。
- **影响**：
  1. **生产产物不可复现**：`out/main/index.js` 每次构建都不同（我方实测 build 侧 `gODuFAZIXUTVpgs46QLA8kyn`、asar 侧 `ziEtSLEe9jN4mLKpsFjDzh2A`，掩码后全文相同）。生产策略本身不含 nonce（`script-src 'self'`），**不构成策略削弱**；但发行物内嵌一个永不使用的随机值，且外部无法按记录复算校验。
  2. **本轮新增的可复现偏差来源**：`npm run dev` 的 main watch 构建会**覆写** `apps/desktop/out/main/index.js`（我方打包后启动 dev server，out/main 的时间戳与内容随即变化），因此"包内外字节一致"仅在"打包后未再运行 dev"时成立。`package-manifest-semantics.json` 目前只解释了"跨构建不可复现"，**未记录"dev watch 覆写 out/"这一新的失效路径**。
- **证据**：`/tmp/i02-r2-mavis-asar/` 与 `apps/desktop/out/` 的逐文件 SHA 对比与掩码 diff（§5.5）。
- **修复建议**（二者取其一即可）：① 把 `define` 限定到 serve 模式（`command === 'serve' ? {define:{…}} : {}`），使生产 main 产物可复现；② 在 `package-manifest-semantics.json` 补记"dev watch 构建会覆写 out/，跨构建 main 哈希不可复现"，并明确该 manifest 的核对窗口。本轮评估：**允许延期**至 M1/首次签名发布前，但延期须有明确归属与时点，不得以"已解决"表述。
- **处理结论**：**M-01 按"证据标注"路线关闭**（`package-manifest-semantics.json` + `acceptance.md` 措辞已准确，本轮复核通过）；**代码未修，残余登记为 R2-05（低）**。

### R2-06（低）新增的 `no-sandbox` 断言只在 Linux 有效，验收文档未标注平台适用范围

- **文件位置**：`tests/e2e/csp-lifecycle.spec.ts:56-61, 291-293`；`tests/e2e/native-recovery.cjs:14-15`。
- **触发条件**：在 macOS / Windows 上运行 C1 矩阵。
- **影响**：Playwright 仅在 Linux 注入 `--no-sandbox`，故 `expect(noSandboxSwitch).toBe(false)` 在 macOS/Windows **恒真**，无约束力；同一次 CI 运行中 `desktop.spec.ts` 仍使用 Playwright 默认参数（Linux 下带 `--no-sandbox`），即"同一运行内两种隔离强度并存"。`preparation.md` 已如实登记"桌面既有冒烟仍保留 PW 默认参数"，但 `acceptance.md` 的矩阵表述未标注该断言的平台适用范围。
- **证据**：`node_modules/playwright-core/lib/coreBundle.js:45670`；我方 macOS 三次运行的 `noSandboxSwitch` 均为 false，而 Round 1 矩阵（未加该断言）同样为无 `--no-sandbox`。
- **修复建议**：在 `evidence.runtime` 中记录注入平台（如 `sandboxInjectionPlatform`），或在断言旁注明"仅 Linux 具备约束力"；验收表按"dev / build / packaged"与"macOS / Windows / Linux"双维度区分隔离强度。
- **处理结论**：**新发现，低**；不阻断，可随验收文档下一版更正。

### R2-07（低）渲染端发起的 `location.reload()` 被全局 `will-navigate` 阻止，应用内无自恢复路径

- **文件位置**：`apps/desktop/src/main/window-security.ts:20`（`contents.on('will-navigate', (event) => event.preventDefault())`，对所有 contents 生效）。
- **触发条件**：渲染进程自身执行 `location.reload()`（或任何渲染发起的文档级导航）。
- **影响**：reload 被静默取消——**无异常、无提示、无控制台线索**；用户在应用内没有自恢复手段（只能靠浏览器发起的 reload，如菜单/快捷键路径，`webContents.reload()` 属程序化导航，不触发该事件）。当前 M0 代码无 `location.reload()` 调用，且用户拒绝恢复后仍可由菜单重载，故不构成当前缺陷。
- **证据（本轮实测）**：`location.reload()` 无异常抛出，但预置 `window.__marker` 在 2 秒后仍存活（未重载），href 保持本地可信 URL。
- **修复建议**：在 `design.md` 明确"应用内不得使用渲染发起的文档级 reload"，或对可信文档的同源 reload 放行；`hardenWebContents` 注释补一句。
- **处理结论**：**新发现，低**；可延期至 M1 引入路由/重载需求前。

### R2-08（中/低）`history.pushState` 在 file:// 文档上静默成功并击穿可信文档校验，health 桥永久失效且报错误导

- **文件位置**：`apps/desktop/src/main/trusted-document.ts:1-12`（要求 href 全等，仅容 hash）、`apps/desktop/src/main/window-security.ts:20-21`（`will-navigate`/`will-frame-navigate` 不覆盖同文档 pushState）。
- **触发条件**：任何未来前端路由使用 `history.pushState`（React Router 等 SPA 默认做法）改变 pathname/query。
- **影响**：
  1. **静默击穿**：在真实 packaged file:// 文档上 `history.pushState({}, '', '/modules')` **不抛异常**，文档 URL 变为 `file:///modules`；随后 `getEngineHealth()` 由 `{ok:true,…}` 变为 **`{ok:false, error:'请求来源不受信任。'}`**。M0 唯一业务能力被永久打断，且错误文案把"路由写错"表述为"来源不可信"，**排障方向被误导**。
  2. **交接缺口**：M-05 的约束虽已写入 `design.md:19`（"完全匹配的文档身份（只容许 hash 改变）"）与 `round-1/processing.md`，但**没有任何实测**说明失败形态有多隐蔽、也没说明 `pushState` 在 file:// 下**不会**被加固层拦住。
- **证据（本轮实测）**：见 §5.5 表（`before.ok=true` → `after.ok=false`，`pushError=null`，`href=file:///modules`）。
- **修复建议**：
  1. 在 `design.md` 增列硬约束"渲染端路由只允许 hash 变化；任何改变 pathname/query 的 `pushState` 会使 health 桥被拒且无提示"（把 `round-1/processing.md` 的口头约束升级为设计条款）。
  2. 更稳妥：`isTrustedDocument` 对 `file:` 同源放宽为"同目录同文件、仅容 hash 与已知查询参数"，或对 `pushState` 变更做显式允许 + 记录。
  3. M1 引入任何路由库前，必须先跑一次"路由变更后 health 仍可用"的回归。
- **处理结论**：**新发现**；把 M-05 的路由约束从"文档声明"升级为"实测证据"。当前 M0 无路由代码，**不影响本轮验收**；列为 M1 前置处理项（中：因失败静默且误导；低：因当前不可达）。

### 附：未发现问题的检查项（不编造问题）

- `app.enableSandbox()` + `securePreferences` 组合：sandbox 渲染器下 preload 仅用 `electron`（contextBridge/ipcRenderer），实测 `window.require/process/ipcRenderer/electron` 均为 `undefined`。
- `hardenWebContents` 对全部 contents 生效：`will-navigate/will-frame-navigate/will-attach-webview` 监听数 > 0，且异窗口 health 被拒。
- health IPC 三重校验（sender / senderFrame===mainFrame / 可信文档）：hash 变化仍放行；异窗口、pushState 改 pathname 后均拒绝（后者见 R2-08）。
- 恢复路径零写入：不调引擎、不重放、不清数据；重建窗初始"尚未检查"，health 仅手动。
- `pendingHealth` 并发复用无竞态覆盖（`.finally` 置空与新赋值不交错）；引擎子进程在 `finish()` 中 `kill()`，崩溃恢复不遗留子进程。
- 生产 meta 位于 `<head>` 首项、先于全部资源；当前产物无内联 script/style（M-04 当前不触发）。
- 依赖/锁文件/协议/PRD/`.pen` 在本迭代范围内无变更。

---

## 8. 历史问题逐项判断

### 8.1 Round 1（MiniMax M3.1-Flash）问题

| 编号 | Round 1 判定 | 本轮判断 | 依据 |
| --- | --- | --- | --- |
| M-01（中）随机 dev nonce 进入生产 main、构建不可复现、证据不可复算 | 未关闭（建议证据标注） | **按"证据标注"路线关闭；代码未修，残余 R2-05（低）** | `package-manifest-semantics.json` 明确 `equalsBuild` 只指"同一次 build"、`crossBuildReproducible:false`；`acceptance.md` 第 15 行同步更正；本轮实测 build↔asar 仅差一个 24 字符 base64 字面量，掩码后全文相同，**措辞准确无夸大**。残余：生产 main 仍不可复现，且新发现 dev watch 覆写 out/ 这一新的失效路径 |
| M-02（中）原生提示从未真实渲染；`catch {}` 吞异常 | 未关闭 | **证据边界部分关闭；静默 catch 残余未关闭（R2-04，中）** | `design.md:31` 与 `acceptance.md:15` 已改为"整体替换整个 API…不单独证明原生 sheet"；`native-dialog-probe/README.md` Run 2 补真实 sheet/AX/点击证据。**残余**：`window-recovery.ts:32-34` 空 catch 仍吞一切异常且无日志 |
| M-03（中）开发 origin/nonce 校验失败 → 无窗口静默僵尸进程 | 未关闭 | **仍未关闭（R2-03，中），本轮独立复现** | EXIT=124（进程存活）、0 窗口、stderr 仅 `UnhandledPromiseRejectionWarning: Error: INVALID_DEVELOPMENT_CSP`；事实与 Round 1 完全一致 |
| M-04（低）生产无 nonce 源，未来内联脚本被静默阻断 | 未关闭（延期 M1） | **仍未关闭（低），本轮实测佐证当前不触发** | 我方读取 `out/renderer/index.html`：仅 1 个外链 module script + 1 个外链 CSS，无内联 script/style、无 modulepreload 内联 polyfill 块；`csp.test.ts` 另断言生产策略不含 nonce/unsafe。延期至 M1 引入 UI 库或改 build target 前可接受，建议加一条构建后断言 |
| M-05（低）全局阻断文档级导航的约束未记入 design | 未关闭 | **关闭；残余升级为 R2-07/R2-08（实测化）** | `design.md:17` 已写"拒绝新窗口、文档/子 frame 导航、重定向和 webview。锚点同文档导航保持可用"，`design.md:19` 已写"完全匹配的文档身份（只容许 hash 改变）"。本轮补测：`location.reload()` 被阻止（R2-07）、`pushState` 静默击穿校验（R2-08） |

### 8.2 Round 1（ZCode GLM-5.3）问题与观察

| 编号 | Round 1 判定 | 本轮判断 | 依据 |
| --- | --- | --- | --- |
| P3-1（低）恢复对话框挂起期间自愈后，选"重新打开窗口"无反馈 | 未关闭，延期 M1 | **仍未关闭（低），允许延期** | `window-recovery.ts:30` 的 `(gone || !responsive)` 守卫语义正确（不重建已健康窗口），仅 UX 缺口；单测 `window-recovery.test.ts` 的 responsive 用例已覆盖。允许延期 M1 |
| P3-2（低）非法 dev CSP 配置以未处理拒绝失败，缺诊断 | 未关闭，可延期 | **仍未关闭**，与 M-03 合并为 R2-03 | 见 R2-03 证据 |
| P3-3（低）`reopen()` 内 `createWindow()` 同步失败会成为未处理拒绝 | 未关闭，可延期 | **关闭（前提不成立）** | `window-recovery.ts:19-34`：`reopen()` 在 `try` 块内被调用，其同步抛出被同一 `catch {}` 捕获，**不会**成为未处理拒绝。其"无日志"部分已并入 M-02/R2-04；"先建后销"保证旧窗在构造失败时保留 |
| 观察 1（生产 main 内嵌随机 nonce） | 观察 | **并入 M-01/R2-05** | 见上 |
| 观察 2（开发 connect-src 显式 origin 不含 `'self'`） | 不需修改 | **关闭（不需修改）** | 固定 `127.0.0.1:5173` 下与 `'self'` 等价；我方开发矩阵实测 `connect-src http://127.0.0.1:5173 ws://127.0.0.1:5173` 下 HMR 与阻断矩阵同时成立；调整 origin 需同步策略并重新验证 |

### 8.3 开发者内部独立审查建议

| 编号 | 内部建议 | 本轮判断 | 依据 |
| --- | --- | --- | --- |
| H-1 | 区分 preferences 工厂与全 contents 导航加固 | **已关闭** | `window-security.ts` 两函数分层；e2e 分别断言 `listenerCount>0` 与复制后的 preferences 字段，未越界声称 hook 能修正不安全构造器；`design.md:17` 表述一致 |
| H-2 | 补充恢复选择的延迟竞态 | **已关闭** | `tests/unit/window-recovery.test.ts` 6 组用例（responsive/close/quit/decline + hang→crash 合并 + 手动 reload）本轮随 15 项 vitest 全部通过 |
| H-3 | native 驱动 bootstrap 有界竞速与清理 | **已关闭** | `tests/e2e/native-driver.ts` 三段等待 + 45s deadline + socket close 拒绝 + `finally` 清理；`tests/unit/native-driver.test.ts` 3 项模拟测试本轮通过；三次 native 运行均正常收敛 |

---

## 9. 冻结验收逐条核对（结论：满足）

| 冻结验收（`scope.md` I02 行 / C1 原文） | 本轮判定 | 依据 |
| --- | --- | --- |
| 单配置生成开发/生产策略 | **满足** | `src/csp.ts` 唯一工厂，同时供构建期 meta（`electron.vite.config.ts`）与开发 header（`main/index.ts`）使用；`csp.test.ts` 覆盖非法 nonce 与非 127.0.0.1:5173 origin 拒绝 |
| 评估后固化生产 meta 或 meta+header，记录锁定版本、交付差异与理由 | **满足** | 选定"生产仅 meta、开发 header"；`design.md:7-9` 给出理由、差异与"若并存须同源生成"约束，并明示不以 meta 声称支持 frame-ancestors 等 header 专用指令 |
| 开发 nonce/HMR 不受生产 meta 误阻 | **满足** | 开发态实测 `meta=null`、nonce header 实际下发、`style-src 'unsafe-inline'` 与 `connect-src ws://…` 存在、React 挂载与 health 通过；nonce 补全机制经 Vite 源码核对为 postHook。HMR 写源探针按指令未运行（见 §6.2） |
| 统一窗口安全加固、来源与主 frame 校验 | **满足** | `app.enableSandbox()` + `securePreferences` 工厂 + 全局 `hardenWebContents` + session 权限全拒；health 保持 sender/mainFrame/可信文档三重校验；实测同来源异窗口被拒、渲染端无 Node/IPR 暴露 |
| 渲染崩溃/无响应恢复 | **满足** | 三环境 native 段均 `events:['killed','unresponsive']`、3 窗/2 提示/三窗手动 health 全 ok；`inspectorClosedBeforeFaults=true`；真实原生 sheet 另有 Run 2 历史证据 |
| 三环境正常 UI/CSS/health/导航/隔离 | **满足** | 我方独立复现构建态 2/2、打包态 2/2、开发态 1/1；锚点导航、导航/popup 拒绝、异窗口拒绝均实测 |
| 三环境内联脚本/资源/连接/frame 阻断矩阵 | **满足** | 三环境均 `enforce` + 接收端零请求 + 可见效果（未执行/未生效）；另补测 `base-uri`/`form-action`/`object-src` 均 `enforce` |
| 恢复不得重复写入 | **满足** | 恢复路径零写入（不调引擎、不清数据、不重放）；重建窗初始"尚未检查"，health 仅手动 |
| 当前仅 health 的恢复实测 | **满足** | 三窗手动 health 均 `ok`，`capabilities:["health"]` |
| 任务重连在 I04 实现后联验，不虚构尚不存在的任务 | **满足** | `design.md:27` 仅定义接入边界（project/job 身份、权威持久 job/提交标记只读查询、旧通知拒绝、零提交/部分轮次/提交响应丢失/完成后取消四类联验），未新增虚构运行方法 |

---

## 10. 结论与门禁意见

1. **最终结论：通过（Pass）** —— 针对 base `1b6df7a220fc9a67d7046133a340085f03f0a96c` → head `76b9d18bd87b9090551eb0dc39dfd6aa061eea79` 的**完整 I02 范围**（含 Round 1 候选 `2cc03da` 的全部产品实现与 Round 2 修订）。
2. **问题处理结论**：本轮 8 项（0 阻断 / 3 中 / 5 低）均已给出处理结论。**R2-01、R2-02 属合并门禁未闭合项**，须以新候选 push 后的**远端 CI 实际全绿**为准，不得以本机 macOS 或 Docker 诊断替代，也不得表述为"已修复 90s 超时根因"。**R2-03（M-03）、R2-04（M-02 残余）允许延期**，但须在"改动开发端口/启动配置之前"与"M1 之前"分别落实，且必须保留为未关闭事实。**R2-05/R2-06/R2-07/R2-08 允许延期**，其中 R2-08 建议在 M1 引入任何前端路由前先行处理。
3. **本模型方的通过意见仅覆盖本轮 base→head 候选 `76b9d18`**，不代表另一模型方结论，也不构成推送/合并授权。合并门禁（双方同版本明确通过 + 阻断全关闭 + 远端 CI 实际全绿 + 远端 develop 核验）**当前未满足**：PR#3 仍停在 `caa0847` 且 CI 未全通过，新候选尚未 push。
4. **证据边界**：本轮通过建立在 **macOS 27.0.1 arm64** 的开发态/构建态/真实未签名 packaged executable 三环境实测 + 静态/单元/pytest 门禁之上；**Windows/Linux 原生生命周期、签名/安装器/干净设备/正式发布、I04 任务重连**均未验证。
5. **审查过程合规**：本轮**未**修改任何实现、测试、配置、依赖或验收文件；**未**提交、未推送、未切换分支；未运行 `I02_HMR=1` 写源探针；未向仓库根提取 asar（仅提取至 `/tmp`）；临时产物全部在 `/tmp`；16 项冻结与 64 项保护哈希在审查前后**均 0 差异**；`git status` 与审查前完全一致。**未写入任何全局或跨会话记忆。**

---

### 附录 A：本轮实际执行的命令清单

```sh
# 版本与状态
pwd; git rev-parse --show-toplevel; git branch --show-current; git rev-parse HEAD
git log --oneline 1b6df7a…..76b9d18…; git diff --stat 1b6df7a… 76b9d18…
git diff --stat 2cc03da… 76b9d18… -- apps packages package.json package-lock.json uv.lock   # 空

# 静态与单元（不启动桌面）
npx vitest run
npx eslint . --max-warnings 0
npx prettier --check .
npx tsc --noEmit -p apps/desktop/tsconfig.json
node scripts/verify-sources.mjs
uv run --frozen pytest -q

# 构建与三环境运行验证
npm run build
I02_EVIDENCE=/tmp/i02-r2-mavis-build-matrix.json    npm run test:e2e      # 失败（native 焦点）
I02_EVIDENCE=/tmp/i02-r2-mavis-build-matrix-r2.json npm run test:e2e      # 2 passed
npm run package:dir
ONTOLEARN_PACKAGED_EXECUTABLE="$PWD/release/mac-arm64/OntoLearn Studio.app/Contents/MacOS/OntoLearn Studio" \
  I02_EVIDENCE=/tmp/i02-r2-mavis-packaged-matrix.json npm run test:e2e    # 2 passed
npm run dev &                                            # 127.0.0.1:5173
ELECTRON_RENDERER_URL=http://127.0.0.1:5173 \
  I02_EVIDENCE=/tmp/i02-r2-mavis-dev-matrix.json \
  npx playwright test tests/e2e/csp-lifecycle.spec.ts                        # 1 passed
pkill -f "electron-vite dev"; lsof -ti:5173 | xargs kill -9

# 独立补充探测（脚本仅在 /tmp）
npx asar extract "release/mac-arm64/OntoLearn Studio.app/Contents/Resources/app.asar" /tmp/i02-r2-mavis-asar
shasum -a 256 apps/desktop/out/{main/index.js,preload/index.js,renderer/index.html} /tmp/i02-r2-mavis-asar/out/…
node /tmp/i02-r2-mavis-extra-probe.mjs      # base-uri/form-action/object-src + 暴露面
node /tmp/i02-r2-mavis-nav-probe2.mjs       # location.reload() 阻止 + pushState 击穿 health
ELECTRON_RENDERER_URL=http://localhost:5173 timeout 12 node_modules/.bin/electron apps/desktop   # M-03 复现

# 冻结与保护核验
python3  # 16 冻结 / 64 保护 SHA-256 逐项重算；对照提交树
git status --porcelain    # 审查前后均 17 条且相同
```

### 附录 B：环境

macOS 27.0.1 arm64（darwin arm64）｜Node v24.15.0｜npm 11.12.1｜uv 0.11.12｜Python 3.12.12｜pytest 9.1.1｜Electron 44.9.0 / Chromium 152.0.7977.167｜Vite 8.3.4｜electron-vite 6.0.0｜electron-builder 26.15.3｜Playwright 1.64.1｜vitest 5.0.5｜TypeScript 5.9.3。
