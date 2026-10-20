# I02 Round 2 独立对抗性审查报告（ZCode / GLM-5.3）

日期：2026-10-20。审查者：ZCode 桌面端独立只读审查任务（Round 2 全新任务，未复用 Round 1 对话）。

## 最终结论

**通过。** 固定范围 `1b6df7a220fc9a67d7046133a340085f03f0a96c → 76b9d18bd87b9090551eb0dc39dfd6aa061eea79`（完整 I02：2cc03da 实现、caa0847 流程证据、76b9d18 测试/CI 修订）在冻结的 I02/C1 验收内实现完整、证据真实、边界诚实。本人在本机独立复现了构建态、真实打包 executable、开发态三套 C1 矩阵（构建态共运行 4 次：1 次失败、1 次外部取消、2 次通过），`npm run check`（15 TS + 198 Python）与 `verify:sources`（13 项）全部通过。Round 1 全部历史意见经逐项独立复核：M-01/M-02 按其自述替代方案关闭，M-03/Z-P3-1/Z-P3-2 等按非阻断延期且约束已记录，无阻断遗留。

两点必须如实说明：(1) 我的第一次构建态运行出现一次**未复现失败**（进入 native 阶段、证据 JSON 无失败诊断、错误原文被下一次运行覆盖丢失），其后的完整运行 4 次全部通过（构建 2、打包 1、开发 1），无法归因，登记为观察项 R2-Z2 与诊断缺口 R2-Z1（均非阻断）；(2) 远端 CI 尚未在新候选 76b9d18 上运行过，**通过结论不构成推送或合并授权**——按 goal-objective.md 第六节原流程，推送的前置是两个指定模型对同一候选均明确通过（当前 MiniMax Round 2 尚未执行，推送门禁未齐）；推送并创建 PR 后，远端 CI 实际全部通过前不得合并 develop；CI 失败若需改动实现/测试，回到新候选双方重审循环。

## 一、评审任务、模型及思考设置的来源记录

- 任务标识：`I02-R2-ZCode-GLM53-20261020-0900`。
- 来源：I02 开发会话按 `docs/iterations/I01/inputs/goal-objective.md` 第四节流程，通过 computer use 在 ZCode 桌面端新建的独立审查任务；本报告依据该任务提示词全文执行。任务参数与 `docs/reviews/I02/round-2/tasks.json` 记录一致（base/head、报告路径、promptSha256 逐项对应）。
- 模型：GLM-5.3；思考程度：最高。以上为任务派发方在任务创建时经应用 UI 实际核验的声明（模型弹窗 selected 非Flash、思考档位最高、分支选中当前 feature），本报告不自行推断。
- 独立性：本轮未读取、未引用另一模型任何 Round 2 意见（其任务尚未创建）；Round 1 两份历史报告按复审规则读取，仅作逐项复核对象，不作为本轮通过依据。

## 二、项目路径、分支与版本

| 项 | 值（本报告实际核验） |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（`git rev-parse --show-toplevel`） |
| 分支 | `feature/I02-csp-window-lifecycle`（`git branch --show-current`，全程未切换） |
| base SHA | `1b6df7a220fc9a67d7046133a340085f03f0a96c`（develop 合并基点） |
| head SHA | `76b9d18bd87b9090551eb0dc39dfd6aa061eea79`（当前 HEAD；审查前后复验一致） |
| 提交构成 | `2cc03da` 实现 → `caa0847` 流程证据/native UI 补证（已 push，PR #3 head）→ `76b9d18` 测试与 CI 修订（未 push） |
| 工作区 | 17 项既有未提交/未跟踪条目（64 项保护对象载体 + round-2 编排文件），审查前后 `git status` 完全一致 |

## 三、需求与验收依据（已完整读取原文）

1. 仓库 `AGENTS.md` 全文（本地优先、渲染端禁 Node/文件系统/shell/通用 IPC、证据分层等）。
2. `docs/iterations/I01/inputs/goal-objective.md` 第四至六节（双模型审查、修复复审、推送合并门禁）。
3. `docs/iterations/I01/inputs/scope.md` I02/C1 行全文（单配置双变体、生产 meta 或 meta+header 固化、开发 nonce/HMR 不受生产 meta 误阻、统一窗口加固与来源/主 frame 校验、崩溃/无响应恢复、三环境正常+阻断矩阵、恢复不得重复写入、仅 health 恢复实测、任务重连留 I04）。
4. `docs/architecture/m0-review-and-update-plan-2026-10-19.md` C1 全文（含"不得向开发页面注入阻断 HMR 的生产 meta""生产脚本不允许 unsafe-inline/unsafe-eval""style 元素/属性/CSSOM 分别验证""只检查 meta 存在或控制台无报错不能视为通过"）。
5. PRD V0.6 8.7 / 10.3 / 10.4 / 12.5 原文。
6. `docs/iterations/I02/design.md`、`acceptance.md`、`commands.md`、`evidence/*`、`inputs/*`；Round 1 两报告、`round-1/processing.md`、`native-dialog-probe/`、`package-manifest-semantics.json`；Round 2 `preparation.md`、`candidate-validation.json`、三份 `*matrix*direct-loop.json`、CI 失败原始日志、焦点对照超时 JSON、docker 诊断元数据。

## 四、已检查范围与验证结果

### 4.1 代码审查范围

- **全量 diff**（123 文件，+9520/−23）：实现 `apps/desktop/src/csp.ts`、`src/main/index.ts`、`src/main/window-security.ts`、`src/main/window-recovery.ts`、`electron.vite.config.ts`、`.prettierignore`；测试 `tests/e2e/csp-lifecycle.spec.ts`、`tests/e2e/native-driver.ts`、`tests/e2e/native-recovery.cjs`、`tests/unit/{csp,window-recovery,native-driver}.test.ts`；CI `.github/workflows/ci.yml`；其余为 I02 文档/证据（按流程证据对待）。**76b9d18 相对 2cc03da 仅改测试与 CI（apps 产品源码零差异已核）**，与"产品 apps/协议/依赖与 Round 1 未改"的声明一致；`package.json`/锁文件/`pyproject.toml`/`uv.lock` 在范围内无改动。
- **迁移完整性**：对照 base 版 `main/index.ts`——base 为 per-window 局部加固 + 恒定 header 注入（生产 `connect-src 'self'`）；新实现收敛为 `securePreferences` 工厂 + 进程级 `web-contents-created` 全 contents 加固（新增 `will-frame-navigate`/`will-redirect`/`will-attach-webview` 覆盖）+ `app.enableSandbox()` + 生产仅 meta + 开发仅 header，生产 `connect-src` 收紧为 `'none'`（health 走窄 IPC，三态矩阵无回归）。
- **未改动上下文**：`trusted-document.ts`（hash 容差+全等）、`preload/index.ts`（仅 health 窄接口）、renderer HTML/App、desktop.spec.ts、playwright 配置。
- **构建产物**：`out/renderer/index.html` 中 CSP meta 为 `<head>` 首元素（先于 charset/script/link），内容与 `contentSecurityPolicy()` 生产变体逐字一致（含 HTML 实体转义）。
- **冻结核验**：round-2 `frozen-files.json` 16 项、`preexisting-files.json` 64 项 SHA-256 在审查开始与结束各核验一次，全部一致；HMR 两个源文件 `git diff` 为空；未运行 `I02_HMR=1`。

### 4.2 本人独立运行的验证

| 命令 | 结果 |
| --- | --- |
| `npm run check` | 通过：lint/format/tsc/vitest 4 文件 **15 项 TS**（含 6 项恢复竞态、3 项 native 驱动故障模拟）、electron-vite build、ruff、pytest **198 项** |
| `npm run verify:sources` | 通过：13 个归档源文件一致 |
| `I02_EVIDENCE=/tmp/i02-r2-zcode-build-matrix.json npm run test:e2e`（构建态，第 1 次） | **失败**：C1 矩阵在 native 阶段中断（详见 R2-Z2），desktop 冒烟通过 |
| 同上（构建态，第 3/4 次，matrix3/matrix4） | **2 次均通过**（20.0s / 19.4s）：7 类 violation 全 enforce、接收端零请求、style 元素/属性拦+CSSOM 允许、异窗口 IPC 拒绝、native `killed`+`unresponsive`、3 窗/2 提示/3 health 全 ok、inspectorClosed=true、无 no-sandbox、输入时可见且获焦 |
| `npm run package:dir` + `ONTOLEARN_PACKAGED_EXECUTABLE=… npm run test:e2e` | 打包 EXIT 0；e2e **2/2 通过**（22.2s）：`app.isPackaged=true`、meta 1 个且逐字一致、响应无 CSP header、阻断矩阵/恢复矩阵与构建态同构全过，native 阶段使用真实 packaged exe |
| `npm run dev` + `ELECTRON_RENDERER_URL=http://127.0.0.1:5173 npx playwright test tests/e2e/csp-lifecycle.spec.ts`（未设 I02_HMR） | **1/1 通过**（19.7s）：无生产 meta、响应 header 含 nonce 与 `ws://127.0.0.1:5173`、style 元素/属性/CSSOM 均允许（HMR 变体）、阻断矩阵 enforce、native 恢复全过 |
| 三份 direct-loop 矩阵 hash 复算 | 与 `candidate-validation.json` 记录的 SHA-256 逐一相符，内容字段与本人复现矩阵同构 |

第 2 次构建态运行被外部取消（工具调用取消，"Bash was cancelled"）；其证据 `/tmp/i02-r2-zcode-build-matrix2.json` 记录 native 子进程以 SIGTERM 退出、驱动诊断完整保留。SIGTERM 与本次取消的因果链未证实，不作归因，仅登记事实。矩阵中 Playwright 实例 `nativeHangMonitorEnabled:false` 为 Playwright loader `--disable-hang-monitor` 所致（`node_modules/playwright-core/lib/server/electron/loader.js:67`），与开发者归档矩阵一致；无响应断言由独立启动的真实 executable（hangMonitor=true）承担。

### 4.3 未验证事项与证据边界

- **开发态 HMR 写源探针**（CSS HMR/React Refresh/state 保留）：按只读约束未运行 `I02_HMR=1`；采信归档 `evidence/development-matrix.json`（`hmr` 三项 true）+ dev-server 日志 + 两源文件 diff 为空。开发态其余断言本人已独立复现。
- **Windows/Linux 原生生命周期、签名/安装器/干净设备、正式发布**：未验证，design/acceptance 已如实登记为边界。Windows 失败（spawnfile 误用 cmd.exe）的修复（改读运行 main 的 `process.execPath`）在本机 build/packaged 路径验证通过，Windows 远端行为待 CI；Linux GitHub 90s 超时根因未证实，Docker 诊断为非等价环境线索（SUID helper 报错已证），不以候选方案当已证明根因——与开发者声明一致。
- **远端 CI（新候选 76b9d18）**：未运行。合并门禁要求实际通过（见结论条件）。
- **I04 任务重连、真实项目 UI**：冻结范围为后续迭代联验项，本轮核对未夹带实现、未虚构能力。
- **另一模型 Round 2**：任务未创建，本报告零接触。

## 五、Round 2 问题清单（全部非阻断）

### R2-Z1（P3）测试失败时错误原文不进入 I02_EVIDENCE，且会被下一次运行覆盖
- 位置：`tests/e2e/csp-lifecycle.spec.ts:298-313`（finally 只写字段化 evidence，不捕获测试体异常文本）；错误原文仅存于 `test-results/…/error-context.md` 与 trace。
- 触发条件：C1 矩阵任何非 native 阶段失败，或 native 阶段失败但 `runNativeRecovery` 的 rejection 未被内层 catch 记录（见 R2-Z2 的实际发生）。
- 影响：失败后若再次运行，`test-results` 被覆盖，错误原文永久丢失，无法事后归因。本轮 R2-Z2 即为此实际代价。
- 证据：`/tmp/i02-r2-zcode-build-matrix.json`（失败证据无任何错误字段）；`test-results/` 在第二次运行后仅剩空目录结构。
- 建议：测试体外层增加 `catch (error) { evidence.testError = String(error); throw error }`（或 Playwright `testInfo.attach`）。可延期至下一测试修订。

### R2-Z2（观察，非阻断）本人第一次构建态运行出现一次未复现失败
- 位置：native 阶段（`stage: native-recovery` 已记录、`nativeLaunch` 已记录、无 `nativeFailure`/`nativeRecovery` 字段），全程 11.2s。
- 影响：因 R2-Z1 诊断缺口，错误原文不可恢复；静态穷举测试代码后，无任何代码路径可在该点既跳出 try 又跳过内层 catch 且不留下字段，原因无法确定。
- 复现情况：失败之后的后续完整运行 **4 次**全部通过：构建态 2 次（run3/run4，与失败运行同版本、同环境、同命令）、真实打包 1 次、开发态 1 次（打包/开发为不同交付形态的独立复现，不计入"同环境同命令"；另有开发者三份 direct-loop 矩阵与 Round 1 历史运行）。判定为偶发未归因事件，**不作为阻断**；若任一后续环节复现出规律性失败，应重开为缺陷。
- 证据：`/tmp/i02-r2-zcode-build-matrix{,2,3}.json`、`/tmp/i02-r2-zcode-run3-full.log`、`/tmp/i02-r2-zcode-run4-full.log`（本会话保留）。
- 建议：与 R2-Z1 一并修诊断；本轮无需代码动作。

### R2-Z3（P3，门禁条件而非代码缺陷）远端 CI 在 76b9d18 上未运行；Linux 焦点前提在 xvfb 无窗口管理器环境未经验证
- 位置：`.github/workflows/ci.yml:32-41`；焦点依赖 `tests/e2e/native-recovery.cjs:46-71`。
- 事实：CI 修订内容本身合理——`install-electron` bin 存在（`node_modules/.bin/install-electron → ../electron/install.js`）、chown root + 4755 为锁定 Electron 官方 helper 标准准备、`chromiumSandbox:true` 显式不接收 no-sandbox、断言/时限未放宽、失败时上传 `test-results/`（含 I02_EVIDENCE）；焦点不可获得时 3 秒有界快速失败并记录 `hangTrigger` 状态，不会静默挂起。但 `xvfb-run -a`（无 WM）下 `isFocused()` 行为无本机等价证据，Windows/Linux 均待远端实测。
- 影响：不降低本轮代码审查结论。按 goal-objective.md 第六节原流程，**推送的前置是同版双模型通过等条件而非 CI**（候选的远端 CI 正是由推送/PR 产生）；推送并创建 PR 后，**远端 CI 实际全部通过前不得合并 develop**；若 CI 再失败且需改实现/测试，回到新候选双方重审。
- 建议：push 后以实际 CI 结果与 `failure-traces-linux` artifact（含 `i02-linux-evidence.json`、`DEBUG: pw:browser` 日志）核验；不预写通过。

## 六、历史问题逐项复核（Round 1 两报告 + 内部审查）

| 编号 | 摘要 | 本轮判断 | 依据 |
| --- | --- | --- | --- |
| M-01（中）随机 dev nonce 进入生产 main，跨构建不可复现 | **关闭**（按其自述方案 2：证据语义标注）；源码级确定性构建优化延期 | `package-manifest-semantics.json` 明确 `equalsBuild`=同一次构建语义、`crossBuildReproducible:false`、nonce 在 packaged 分支不使用不削弱策略；native-dialog-probe `package-identity.json`/`package-main-diff.txt` 按 same-build 语义如实登记实际运行包。冻结验收不要求可复现构建，M-01 原文允许二选一解除 |
| M-02（中）native 对话框整体 stub + 空 catch | **关闭（必须项）**：design/acceptance/commands 已更正为"整体替换 API、不单独证明 sheet"；真实 UI 由 native-dialog-probe Run 2 补证（真实 packaged 同进程、showMessageBox 从未替换、AX+截图、两按钮可达、拒绝不重建、3 窗无第 4 窗、childExit 0），且 apps 产品源码 2cc03da→76b9d18 零差异，历史 UI 证据仍对应本候选产品代码。**建议项（catch 区分异常+最小诊断）延期未修**，作为非阻断建议保留（与 R2 复核一致） | README + run-2 全套文件在库；`window-recovery.ts:32-34` 空 catch 仍在 |
| M-03（中）非法手工 dev origin/nonce → 无窗口未处理拒绝 | **未关闭，按非阻断延期**（处理记录如实声明未修） | `csp.ts:16-18` 仍同步抛出、`whenReady` 回调仍无 catch。本人独立判断：正常流程不可达（Vite `strictPort` 固定 127.0.0.1:5173、nonce 由构建注入、packaged 分支不受影响），fail-closed 方向正确；两份 R1 报告均判非阻断。延期条件（改端口前做显式诊断+非零退出+统一 origin 来源）已记录于 processing.md |
| M-04（低）未来构建内联脚本静默失效 | **延期关闭**（交接约束已记录） | processing.md 记录"生产 HTML 不得新增当前 CSP 无法授权的内联 script/style，新增构建插件/目标须重验矩阵"；当前锁定产物仅外链 script/CSS（本人核对 out/renderer/index.html） |
| M-05（低）全局导航阻断未交接 | **部分采纳关闭** | design.md 已写明文档/子 frame/重定向拒绝与 hash 保留；processing.md 补充 history API 改 pathname/query 会使可信文档失配的边界 |
| Z-P3-1 自愈后选择恢复无反馈 | **未关闭，延期 M1**（设计选择保留，竞态单测覆盖） | `window-recovery.ts:30-31` 守卫不变；6 项竞态测试本轮运行通过 |
| Z-P3-2 / 同 M-03 | **未关闭，延期**（与 M-03 同一缺陷） | 同上 |
| Z-P3-3 reopen 同步抛错成为未处理拒绝 | **原措辞不成立（已澄清）**：`reopen()` 调用点位于 `prompt()` 的 `try` 内（`window-recovery.ts:18-36`），同步 throw 进入 catch；"无日志"事实并入 M-02 建议项延期 | 本人读码独立确认 |
| Z-O1 生产 main 内嵌随机 nonce | **关闭**（同 M-01） | 同 M-01 |
| Z-O2 dev connect-src 显式 origin 无 'self' | **关闭**（无需修改） | 固定 origin 下等价；开发矩阵双方/本人均通过 |
| H-1/H-2/H-3（内部审查三项） | **关闭** | 工厂/contents 分层、6 项竞态测试、驱动三段有界+45s deadline+finally 清理均在实际代码与本人运行中复现 |

历史通过不作本轮依据：本轮结论完全基于对 76b9d18 的上述独立检查与运行。

## 七、需求符合性抽查（冻结验收对 76b9d18 的成立性）

1. 单配置双变体：`src/csp.ts` 唯一来源，生产 meta（Vite build 插件 head-prepend）与开发 header（`onHeadersReceived`）同源；非法 nonce/origin 拒绝生成（单测覆盖，本人运行通过）。
2. 生产仅 meta 交付 + 理由与锁定版本记录（design.md）；生产响应无 CSP header、meta 先于资源（本人构建/打包两态实测）。
3. 开发不受生产 meta 误阻：开发态 0 meta + nonce header 实测；HMR 变体（style unsafe-inline + ws connect）在位。
4. 统一加固/来源/主 frame 校验：`web-contents-created` 先于任何窗口注册于模块顶层；`enableSandbox` + session 权限全拒；health 三重校验；异窗口实测拒绝；锚点导航保留。
5. 崩溃/无响应恢复：真实 `killed`/`unresponsive` 事件、先建后销、closed 回调保护、退出/销毁/自愈守卫（6 项竞态单测）；恢复零写入、新窗"尚未检查"、仅手动 health；不虚构任务重连（I04 边界仅在 design 定义）。
6. 三环境阻断矩阵：7 类 directive 全 `enforce` + 本地 HTTP 接收端零请求 + 脚本未执行 + `require undefined`；不把"控制台无错/meta 存在"当通过（矩阵以 securitypolicyviolation enforce + 行为效果 + 零请求交叉证明）。
7. CI/测试修订不降低断言：90/40/45 秒时限、全部断言、真实故障注入（真实 crash + 真实无限循环 + 真实输入）保持；无 no-sandbox/权限放宽。

## 八、结论重申

对 `1b6df7a → 76b9d18` 出具**通过**：无阻断问题；3 项 Round 2 新登记项（R2-Z1/R2-Z3 为 P3 建议，R2-Z2 为观察）均允许延期或属门禁条件；Round 1 历史意见全部有明确处理结论（关闭/延期/澄清），延期项均非阻断且约束已记录。

通过的边界与条件：(1) 按 goal-objective.md 第五、六节原流程：推送的前置是两个指定模型对同一候选（76b9d18）均明确通过——当前 MiniMax Round 2 尚未执行，推送门禁尚未满足；推送并创建 PR 后，远端 CI 实际全部通过并核验前**不得合并 develop**；CI 失败若需改动实现/测试/配置，须新候选、双模型全新任务重审，本通过不沿用。(2) Windows/Linux 原生生命周期仍属未验证边界。(3) R2-Z2 的偶发失败已如实登记，任一后续环节复现规律性失败时应重开。本报告仅代表 ZCode/GLM-5.3 本轮独立判断，不构成对另一模型结论的引用或合并授权。
