# I02 Round 3 独立对抗性审查报告（ZCode / GLM-5.3）

日期：2026-10-20。审查者：ZCode 桌面端独立审查任务（Round 3 全新任务，未复用此前任何轮次对话）。

## 最终结论

**通过（Pass，仅本模型方、仅候选 `09a2e6648edfb465debe47bc9fb15e2c6f23e088` 的冻结 I02/C1 验收范围）。**

候选 `09a2e66` 相对 Round 2 双方通过的 `76b9d18` 仅有一处受审文件差异：`tests/e2e/csp-lifecycle.spec.ts` 的 `forcefullyCrashRenderer` 终止理由断言由仅接受 `killed` 改为接受 `killed || crashed`。我对该修订做了独立契约核验（锁定 Electron 44.9.0 官方 `electron.d.ts` 原文与 SHA 逐项比对）、完整代码审查、以及对新候选的三环境运行复现（构建态 2/2、真实打包 2/2〔首跑一次失焦失败后复跑通过，两次均如实记录〕、开发态 1/1），结论：该修订精确契合锁定版本的官方文档契约，未放宽其他任何断言或时限，产品源码与 `76b9d18` 逐字一致；全部 16 项冻结文件与 64 项既有保护文件在审查首尾两次核验零差异。

**通过不等于门禁闭合**：新候选尚未 push，其远端 CI 未运行（旧 head `7e26155` 的 CI 因同一过窄断言在 Linux/Windows 失败、macOS 通过——我已核对两份原始 job 日志与 Linux artifact，失败点确为唯一断言且位于 native 恢复全部既有断言之后）；另一模型本轮结论未知且按独立性约束未读取；按 goal-objective.md 第六门禁，实际全部 CI 成功前禁止合并 develop。历史遗留的非阻断项（M-03、R2-04 catch 残余、R2-05 等）均有明确延期归属，我逐项独立复核并保留其未关闭状态，不自动关闭。

本轮我复现了一次 R2-01 模式的失焦失败（见 R3-Z1），再次确认该夹具脆弱性在新候选上仍然存在，属非阻断测试夹具问题且失败有界、可区分；未发现任何新的产品代码缺陷。

## 一、评审任务、模型及思考设置的来源记录

- 任务标识：`I02-R3-ZCode-GLM53-20261020-1040`。
- 来源：派发方按 `docs/iterations/I01/inputs/goal-objective.md` 第四节流程，通过 computer use 在 ZCode 桌面端新建的独立空白审查任务；本报告依据该任务提示词全文执行。任务参数与 `docs/reviews/I02/round-3/tasks.json` 中本任务条目一致（base/head、报告路径、promptSha256 对应）。
- 模型：GLM-5.3；思考程度：最高。以上为派发方在任务创建时经应用 UI 实际核验的声明（tasks.json 记录 GLM-5.3 popup selected 非 Flash、最高 selected、feature 分支选中），本报告不自行推断。
- 独立性：本轮未读取另一模型任何 Round 3 产物（其报告文件按流程记录已存在，我未打开）、未读取 `round-3/processing.md`（审查中途接到的新执行约束明令禁止，此前亦未读过）、未读取另一模型任何 /tmp 运行记录。允许读取的 Round 1/Round 2 历史双方报告与候选前共同证据（preparation、candidate-validation、CI 原始日志/artifact、electron 契约 JSON）均已读，仅作核对对象，不作为通过依据。
- 审查中途的执行约束变化：任务开始后用户下达"无桌面打扰"新政策（工作区 AGENTS 第 4/5 节、仓库外 `../iteration-control/2026-10-19/goal-objective.md` 第九节、`guidance-transition-2026-10-20/policy.md`，三份均已实际读取）。政策下达前我已完成全部本机桌面验证（当时经用户明确授权，含日志方式修正指令）；政策下达后我未再启动任何 Electron/Playwright/dev/native/HMR 窗口操作。我已完成的 15 份原始日志/矩阵被派发方按原字节保全于 `round-3/zcode-runtime/`（`runtime-preservation-manifest.json` 记录 hash），我逐文件核验保全件与我 `/tmp` 原件 SHA-256 一致（15/15）。保全是归档行为，不是新的验证结果。

## 二、项目路径、分支、base/head 与冻结核验

| 项 | 值（本报告实际核验） |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（`git rev-parse --show-toplevel`） |
| 分支 | `feature/I02-csp-window-lifecycle`（`git branch --show-current`，全程未切换） |
| base SHA | `1b6df7a220fc9a67d7046133a340085f03f0a96c`（固定审查基点，与历轮一致） |
| head SHA | `09a2e6648edfb465debe47bc9fb15e2c6f23e088`（当前 HEAD，审查首尾复验一致） |
| 提交构成 | base→head 共 5 笔：`2cc03da` 实现 → `caa0847` 流程证据/native UI 补证（已 push，PR#3 head）→ `7e26155` R2 门禁证据（已 push）→ `76b9d18` 测试/CI 修订 → `09a2e66` 本轮断言修订 |
| 新候选唯一受审差异 | `git show 09a2e66 -- tests/e2e/csp-lifecycle.spec.ts`：仅 292–296 行一处断言 + 一行契约注释；`docs/iterations/I02/evidence/frozen-files.json` 同步该文件新 hash；其余为 round-3 证据/流程文件。产品 `apps/`、`packages/`、依赖、锁文件、CI、验收文档相对 `76b9d18` 零改动 |
| 冻结核验 | `round-3/frozen-files.json` 16 项：HEAD 提交树与工作区均与清单一致（审查开始与结束各一次，中途并发变更后再验一次，均 0 差异）；`docs/iterations/I02/preexisting-files.json` 64 项：工作区与清单一致（0 差异）。其中 57 项本为未入库保护资料、7 项为候选前既有工作区差异，均未被 I02 触碰 |
| 工作区纪律 | 审查期间并发开发会话追加了流程文件（`status.md`/`preparation.md` 工作区修改、round-3 下 hold/policy 等新未跟踪文件、`docs/decisions/`）。我逐一确认均非冻结 16 项、非实现/测试/配置/依赖/验收；`AGENTS.md` 工作区差异为新版扩展指南，产品不变量与 HEAD 版一致且更严格。受审候选本身未受影响（见 R3-O2） |
| HMR 源文件 | `git diff -- apps/desktop/src/renderer/src/App.tsx apps/desktop/src/renderer/src/style.css` 为空；全程未运行 `I02_HMR=1` |

## 三、需求与验收依据（实际读取原文，未以开发者摘要替代）

1. 仓库 `AGENTS.md`（HEAD 提交版与工作区新版两版均读，约束一致）。
2. `docs/iterations/I01/inputs/goal-objective.md` 第四至六节完整流程（双模型审查规则、修复复审循环、推送合并门禁）。
3. `docs/iterations/I01/inputs/scope.md` I02/C1 完整冻结行（第 25 行）。
4. `docs/architecture/m0-review-and-update-plan-2026-10-19.md` C1 全文（145–153 行），含"不得向开发页面直接注入会阻断 Refresh/HMR 的生产 meta""生产脚本不允许 unsafe-inline/unsafe-eval""style 元素/属性/CSSOM 分别验证，不能把 React style 统一当成会被阻断""只检查 meta 存在或控制台没有报错不能视为通过""恢复不得丢失已提交项目状态或自动重复写任务"。
5. PRD V0.6 `docs/prd/PRD-本体学习与落地Agent工作台.md` 8.7 / 10.3 / 10.4 / 12.5 原文。
6. `docs/iterations/I02/design.md`、`acceptance.md`、`commands.md`、`evidence/*`、`inputs/*`（含受保护原始 CSP 实测快照）；`docs/reviews/I02/round-3/` 候选前共同证据（preparation、candidate-validation、两平台 CI 原始日志与 Linux artifact、electron-force-crash-contract、windows-log-byte-preservation、round-2-ci-final/snapshot）；Round 1/Round 2 双方历史报告与 round-1/round-2 processing；`native-dialog-probe/README.md`。

## 四、已检查范围

- **全量 diff**（base→head，182 文件 +17241/−23）：实现 6 文件（`csp.ts`、`main/index.ts`、`window-security.ts`、`window-recovery.ts`、`electron.vite.config.ts`、`.prettierignore`）、测试 6 文件（e2e 3 + unit 3）、CI `.github/workflows/ci.yml`，其余为文档/证据（按流程证据对待）。
- **逐行读毕**：上述全部实现与测试文件；`trusted-document.ts`、`preload/index.ts`、`renderer/`、`engine.ts` 在范围内零改动已用 diff 命令确认；对比 base 版 `main/index.ts` 确认从"恒定 header 注入 + per-window 局部加固"到"生产仅 meta + 开发仅 header + 全 contents 统一加固"的完整迁移，生产 `connect-src` 由 `'self'` 收紧为 `'none'`。
- **产物核验**：`out/renderer/index.html` 的 CSP meta 为 `<head>` 首元素（偏移 55 < script 494 < link 575），内容与 `contentSecurityPolicy()` 生产变体逐字一致（HTML 实体转义形态）；产物无内联 script/style。
- **M-01 残余实证**：`out/main/index.js` 内嵌 24 字符随机 base64 nonce 字面量（与 dev header nonce 同值），并据 dev 矩阵 responseCSP 与当前 out/main 内嵌值一致证实 dev watch 曾覆写 out/main——R2-05 描述的两条失效路径在我本轮工件中均可观察。

## 五、独立验证：命令与实际结果（本人执行；完整 stdout/stderr 均保存 /tmp 独立日志并记录原始退出码）

| 命令 | 结果 |
| --- | --- |
| `npm run check`（日志 `/tmp/i02-r3-zcode-glm53-check.log`） | **EXIT 0**：eslint/prettier/tsc 通过、vitest 4 文件 **15 项**、electron-vite build、ruff、pytest **198 项**（日志内 0 处 error） |
| `npm run verify:sources` | **EXIT 0**，13 个归档源文件一致 |
| `I02_EVIDENCE=/tmp/i02-r3-zcode-glm53-build-matrix.json npm run test:e2e`（构建态） | **EXIT 0，2/2 通过**（19.0s+1.1s） |
| `npm run package:dir` | **EXIT 0**（electron-builder 26.15.3，darwin arm64 未签名本地包） |
| `ONTOLEARN_PACKAGED_EXECUTABLE=<真实包内可执行> I02_EVIDENCE=…-packaged-matrix.json npm run test:e2e`（第 1 次） | **EXIT 1 失败**：native 阶段第 2 窗 `hangTrigger.focused=false`（`visible=true`），夹具有界快速失败 `native hang input requires a focused visible window`；产品侧行为正常（`events:['killed']`、1 次提示、窗口重建、2 次 health ok、CSP/隔离断言全过）。即 R2-01 失焦模式，见 R3-Z1 |
| 同上（第 2 次，矩阵 `…-packaged-matrix2.json`） | **EXIT 0，2/2 通过**：`app.isPackaged=true`、meta 1 个逐字一致、响应无 CSP header、7 类 violation 全 enforce、style 元素/属性拦 + CSSOM 允、`inline/remote=false`、`fetchBlocked=true`、`require undefined`、接收端零请求、异窗口 IPC 拒绝、native `['killed','unresponsive']`/3 窗/2 提示/3 health 全 ok、inspectorClosed=true、hangMonitor=true、noSandbox=false、输入时可见且获焦 |
| `npm run dev`（自有进程组）+ `ELECTRON_RENDERER_URL=http://127.0.0.1:5173 I02_EVIDENCE=…-dev-matrix.json npx playwright test tests/e2e/csp-lifecycle.spec.ts`（未设 I02_HMR） | **EXIT 0，1/1 通过**：开发态 0 个 CSP meta、responseCSP 含随机 nonce + `unsafe-inline` 样式 + `connect-src http://127.0.0.1:5173 ws://127.0.0.1:5173`、style 元素/属性/CSSOM 均允许（HMR 变体）、script/img/connect/frame 阻断 enforce、接收端零请求、异窗口拒绝、native 全过（killed+unresponsive/3 窗/2 提示/3 health/inspector 关闭/可见获焦）。运行后自有 dev 进程已终止、5173 已释放 |
| `ELECTRON_RENDERER_URL=http://localhost:5173 timeout 12 node_modules/.bin/electron apps/desktop` | **EXIT 124**（12 秒后仍存活被 timeout 终止）、0 窗口、stderr 仅 `UnhandledPromiseRejectionWarning: Error: INVALID_DEVELOPMENT_CSP`——M-03/R2-03 独立复现成立 |
| pushState 探针（真实 packaged，/tmp 脚本） | `pushState({}, '', '/modules')` 在 file:// 文档**静默成功**（无异常），`location.href` 变为 `file:///modules`；探针因脚本序列化缺陷未捕获推送后 health 结果（政策下达后未重试），该半段结论与 R2-08 历史实测一致，推送后 health 拒绝部分沿用历史证据（他人执行，已标注） |
| Electron 契约核验 | 本机 `node_modules/electron` package version **44.9.0**；`electron.d.ts` SHA-256 `9f96ec8a…d4c590b` 与 `electron-force-crash-contract.json` 声明**逐字符一致**；18656–18666 行官方原文："This will cause the `render-process-gone` event to be emitted with the `reason=killed || reason=crashed`" |
| CI 原始证据核验 | `round-2-linux-job.txt`：C1 仅 1 项失败，断言 295 行 `toContain('killed')` 实收 `["crashed","unresponsive"]`，失败行位于 `native.result==='PASS'`、`inspectorClosed`、`hangMonitor`、`noSandbox===false` 四断言**之后**，随后 desktop 冒烟通过；`round-2-windows-job.txt` 同一断言同一实收值。Windows 日志 gz SHA `51d167…` 与解压 SHA `1cca49…` 双双匹配 `windows-log-byte-preservation.json`。Linux artifact `i02-linux-evidence.json`：nativeRecovery PASS、`['crashed','unresponsive']`、3 窗/2 提示/3 health、inspector 关闭、hangMonitor 开、无 no-sandbox、**输入时可见且获焦**、接收端零请求、7 类 enforce。整体 run 39359486479 conclusion=**failure**（macOS success / Windows failure / Quality failure），不当作通过 |

## 六、Round 3 问题清单（本轮新登记，均非阻断）

### R3-Z1（P3）R2-01 失焦脆弱性在新候选上复现：我的真实打包首跑失败
- 位置：`tests/e2e/native-recovery.cjs:46-87`（3 秒取焦确认 + 250ms 后投递前二次复核）、`tests/e2e/native-driver.ts:33`（`native exit 1` 呈现）。
- 触发条件：取焦确认通过后、250ms 投递窗口内焦点被其他前台活动夺走。本轮本人打包首跑实际发生（`hangTrigger:{visible:true,focused:false}`）；同命令复跑即通过。前两轮各有 1 次同类失败（R2-01、R2-Z2 相关记录），同版本同环境非确定性行为成立。
- 影响：失败时产品侧行为本身正常（崩溃事件、提示请求、窗口重建、health 全部通过），但 CI 会变红且以 `native exit 1` 呈现，与产品错误同形；证据 JSON 中 `hangTrigger.focused:false` 与 `error` 字段可区分夹具前提失败。
- 证据：`/tmp/i02-r3-zcode-glm53-packaged-matrix.json`（失败）与 `…-packaged-matrix2.json`（通过），两份完整日志均已保全。
- 建议：与 R2-01 合并跟踪，待下一次测试夹具修订时处理（处理记录中的既有立场：不降低硬断言、不跳过真实 unresponsive）；修订属受审文件变更，须新候选双方重审。可延期。

### R3-O1（观察）pushState 击穿可信文档：本轮仅复现机制前半段
- 位置：`apps/desktop/src/main/trusted-document.ts`（全等 + hash 容差）与 R2-08 相同。
- 事实：我在真实 packaged 应用实测 `pushState` 静默成功且 `href` 变为 `file:///modules`；推送后 health 变为拒绝的半段因探针脚本缺陷未捕获，且新政策禁止再开窗口，未重试。该半段沿用 Round 2 MiniMax 历史实测（他人执行）。结论不变：R2-08 仍为已实测交接的 M1 前置项，非本轮阻断。

### R3-O2（观察）审查期间工作区出现并发流程文件写入，冻结候选未受影响
- 事实：审查中途 `status.md`、`round-3/preparation.md`（均为已提交流程文档）出现工作区修改，并新增多个未跟踪流程文件（hold/policy/receipt 等）与 `docs/decisions/`。我在每次变更后重验 16 冻结 + 64 保护哈希（3 次全 0 差异），并 diff 确认改动均为流程叙述（含另一模型任务调度记录），无实现/测试/配置/依赖/验收内容。按规则"流程证据追加不使代码审查失效，但须记录对应关系"，此观察如实在案；候选 09a2e66 提交树全程未变。

本轮未发现新的产品代码缺陷。不为对抗编造问题。

## 七、新候选唯一差异的专项裁定（不接受开发者解释作为结论）

- **契约独立核验**：锁定版本 44.9.0 的官方类型文件原文写明 `forcefullyCrashRenderer` 触发的 `render-process-gone` 理由为 `killed || crashed`；文件 SHA 与候选记录一致。Linux/Windows 真实 CI 运行实收 `crashed`，macOS（本机三环境与 CI）实收 `killed`，均落在契约集合内。原断言只接受 `killed` 属于测试对契约的过度收窄，修正是必要的。
- **放宽边界精确**：新断言 `some(reason => reason === 'killed' || reason === 'crashed')` 仅接受契约两值，不接受 clean-exit/oom/任意字符串；`unresponsive` 断言、3 窗/2 提示/3 health、`unexpected automatic restart` 守卫、inspector/hangMonitor/sandbox/packaged 断言、90/40/45 秒时限全部原样保留（我逐行比对 diff 与全文）。
- **不可掩盖性分析**：崩溃提示（prompts 第 1 项）只能由 `render-process-gone`（非 clean-exit）经产品恢复逻辑真实发出；`prompts.length===2`、`windows===3`、`events` 含 `unresponsive` 共同锁死"真实崩溃 + 真实提示 + 真实重建 + 真实无响应"链条。理论上若 `forcefullyCrashRenderer` 产生契约外理由而后续 destroy 产生 `killed`，断言仍可能通过——但契约排除了该情形，且两平台真实运行证据均为契约内值；残余风险可忽略，不构成问题。
- **范围合规**：产品 apps/packages、CI、依赖、冻结验收零改动；此修订属"CI 失败需要的受审文件再改→新候选→双方新任务重审"路径的正确执行，未夹带。
- **不能替代的事项**：R1 时期 GitHub 90s 超时的旧根因仍未归因；本次修订只解释本轮两平台的断言差异，处理记录亦如实如此声明，我核对该声明与日志相符。

## 八、历史问题逐项复核（独立判断，不以处理记录或旧通过代替）

| 编号 | 摘要 | 本轮判断 | 依据（本人独立核验） |
| --- | --- | --- | --- |
| M-01（中）/Z-O1 | 随机 dev nonce 进入生产 main，跨构建不可复现 | **按证据标注路线维持关闭；残余即 R2-05 未关闭（低，延期 M1/签名发布前）** | `package-manifest-semantics.json` 语义标注准确；我本轮在 `out/main/index.js` 实测内嵌随机 nonce 字面量，并观察到 dev watch 覆写 out/main（dev 矩阵 responseCSP nonce == 当前 out/main 内嵌值）。策略本身不含 nonce，不构成削弱 |
| M-02（中） | native 对话框整体 stub + 空 catch | **证据边界部分维持关闭（措辞已更正 + native-dialog-probe Run 2 真实 sheet 历史 UI 证据，同一产品源码且 09a2e66 未改产品文件）；静默 catch 残余未关闭（=R2-04，延期 M1 前）** | `window-recovery.ts:32-34` 空 catch 原样存在（本人读码）；两处测试仍整体替换 `dialog.showMessageBox`；Run 2 为历史实测，非本轮新拍，已按历史证据标注 |
| M-03（中）/Z-P3-2 | 非法 dev origin/nonce → 无窗口未处理拒绝僵尸进程 | **未关闭（本轮本人独立复现：EXIT 124、0 窗口、仅 UnhandledPromiseRejectionWarning）**，按非阻断延期，触发条件（改开发端口/启动配置之前必须修）已记录于 round-2/processing.md | 复现命令与日志见 §五；`csp.ts:16-18` 同步抛出、`whenReady` 回调无 catch 均未变 |
| M-04（低） | 生产无 nonce 源，未来内联脚本静默失效 | **未关闭，延期 M1（当前不触发）** | 我核对本轮构建 `out/renderer/index.html` 仅 1 个外链 module script + 1 个外链 CSS，无内联 script/style；交接约束在处理记录中 |
| M-05（低） | 全局导航阻断约束未记录 | **关闭（design 已记录；实测化为 R2-07/R2-08 继续跟踪）** | `design.md:17` 明确拒绝新窗口/文档/子 frame 导航/重定向/webview、锚点保留 |
| Z-P3-1（低） | 自愈后选择"重新打开窗口"无反馈 | **未关闭，延期 M1（设计选择保留）** | `window-recovery.ts:30` `(gone \|\| !responsive)` 守卫不变；6 项竞态单测本轮随 check 通过 |
| Z-P3-3（低） | reopen 同步抛错成为未处理拒绝 | **关闭（前提不成立）** | 本人读码：`reopen()` 调用点在 `prompt()` 的 try 块内（`window-recovery.ts:18-36`），同步 throw 进入 catch；"无日志"并入 M-02/R2-04 |
| Z-O2 | dev connect-src 显式 origin 无 'self' | **关闭（无需修改）** | 固定 origin 下等价；我本轮开发矩阵 header 实测且通过 |
| H-1/H-2/H-3（内部审查） | 工厂分层 / 恢复竞态 / 驱动有界失败 | **关闭** | 代码分层与 6 项竞态、3 项驱动模拟测试均在本轮 check（15 项）中实际通过 |
| R2-01（中） | native 夹具取焦硬前提致可复现偶发失败 | **未关闭，非阻断，本轮本人再次复现一次（R3-Z1）** | 相对 R2 新增事实：Linux CI 官方 runner 的 xvfb 环境**实际满足**了可见+获焦前提（artifact `hangTrigger:{visible:true,focused:true}`），说明该前提在目标 CI 可达成但非确定；修正仍留待下次夹具修订 |
| R2-02（中） | 新候选跨平台零运行证据 | **部分推进，门禁未闭合**：旧 head `7e26155` 的三平台 CI 已实际运行（macOS 全绿；Linux/Windows 唯一失败即本轮修订针对的断言，native 恢复本身通过）；**新候选 `09a2e66` 的远端 CI 仍未运行**（未 push），实际全绿前禁止合并 | 我核对两份原始 job 日志 + Linux artifact + run conclusion=failure；不以旧 run 推断新 head 必绿 |
| R2-03（中） | = M-03 本轮复现 | **未关闭**（同 M-03） | 见 M-03 行 |
| R2-04（中） | M-02 残余：空 catch 无诊断 | **未关闭，延期 M1 前** | 读码确认未改 |
| R2-05（低） | nonce 残余 + dev watch 覆写 out/ | **未关闭，延期；本轮两条路径均被我独立观察证实** | 见 M-01 行与 §四 |
| R2-06（低） | no-sandbox 断言仅 Linux 有约束力 | **未关闭（文档性），验收表未标注平台适用范围** | 断言原样存在（spec 61/293 行）；macOS/Windows 恒真属事实 |
| R2-07（低） | 渲染端 location.reload 被静默阻止 | **未关闭，延期引入路由/重载需求前** | `window-security.ts:20` 未变；约束已记录 |
| R2-08（中/低） | pushState 静默击穿可信文档校验 | **未关闭，M1 引入路由前处理；本轮复现其机制前半段（R3-O1）** | 见 §五与 R3-O1 |
| R2-Z1（P3） | 失败错误原文不进 I02_EVIDENCE 且被覆盖 | **未关闭，延期至下次测试修订** | spec 代码结构未变（finally 仅写字段化 evidence）；注：本轮我打包首跑失败时 native 阶段内层 catch 确实把 `nativeFailure`+`nativeRecovery` 写入了证据（该路径诊断有效），但非 native 阶段失败原文仍会丢失 |
| R2-Z2（观察） | R2 一次未归因失败 | **维持未归因事实，不关闭为"已修复"** | 本轮我未出现同模式失败（我的失败均有完整诊断，属 R2-01 模式）；单次成功样本不证确定性 |
| R2-Z3（P3/门禁） | 新候选 CI 未跑；Linux 焦点前提未验 | **按新事实更新：Linux 焦点前提已在官方 runner 实际达成一次；新候选 CI 仍未跑，门禁项继续挂着** | 同 R2-02 行 |

## 九、冻结验收逐条核对（对 `09a2e66`）

1. **单配置生成开发/生产策略**：`src/csp.ts` 唯一工厂；生产 meta（Vite build 插件 `head-prepend`）与开发 header（`onHeadersReceived`）同源生成；非法 nonce（含注入串）与非固定 origin 拒绝（单测覆盖并通过）。达标。
2. **生产仅 meta 交付 + 锁定版本与理由**：design.md 记录 Electron 44.9.0/Vite 8.3.4、比较与理由，明示不以 meta 声称支持 frame-ancestors 等 header 专用指令；我实测生产响应无 CSP header、meta 为 head 首元素先于资源。达标。
3. **开发 nonce/HMR 与生产 meta 隔离**：生产插件 `apply:'build'`、`cspNonce` 仅 serve；开发态实测 0 meta + nonce header；归档 HMR 写源证据（`hmr:{css,reactRefresh,documentAndStateRetained:true}`）按约束未重跑（本轮禁止 `I02_HMR=1`），开发态其余断言全部本人复现。达标（HMR 部分为归档证据，边界如实）。
4. **脚本禁 unsafe-inline/eval + 样式三分验证**：生产变体无 unsafe/nonce（单测断言 + 产物实测）；style 元素/属性被拦、CSSOM 赋值允许在我构建态与打包态矩阵实测。达标。
5. **实际 enforce + 接收端零请求**：三环境 7 类 directive 全 `enforce`（原生 securitypolicyviolation 事件）+ 本地 HTTP 接收端零请求 + `inlineExecuted/remoteExecuted=false`；未以"meta 存在/控制台无错"代替。达标。
6. **正常 UI/CSS/导航/health**：三环境页面矩阵（标题/布局 computed style/模块锚点导航/手动 health `本地引擎已连接`）全部通过；导航/popup 拒绝、窗口数保持 1。达标。
7. **全 contents 加固 + sender/mainFrame/文档来源校验**：`web-contents-created` 模块顶层注册先于任何窗口；`enableSandbox`+session 权限全拒；health 三重校验保持；异窗口（复制 preferences + 同可信文档）实测拒绝；后建 contents 监听数 >0 且 preferences 隔离字段生效。达标。
8. **真实崩溃/无响应 + 显式恢复**：真实 `forcefullyCrashRenderer`（killed/crashed）与无限循环 + 真实输入（可见获焦时）触发原生 `unresponsive`；默认/取消不重建、显式选择才重建；先建后销、旧 closed 回调保护、退出/销毁/自愈守卫（6 项竞态单测）；真实 native sheet 由 Run 2 历史证据覆盖（非本轮新拍）。达标。
9. **新窗"尚未检查" + 零重放/零写入**：重建窗初始状态实测"尚未检查"，health 仅手动；恢复路径不调引擎、不清数据、不重放；native 断言锁死 3 窗/2 提示/第 4 窗即报错。达标。
10. **I04 任务重连仅核对接入边界**：design.md 第 27 行只定义 project/job 身份、持久提交标记只读查询、旧通知拒绝与四类联验边界，未新增任何虚构运行方法；本轮范围内无任务系统改动。达标。

## 十、未验证事项与证据边界

- **新候选 `09a2e66` 的远端 CI**：未运行（未 push）。门禁未闭合，本通过不含 CI 结论。
- **另一模型 Round 3**：未读取其任何产物；双模型同版通过条件是否满足由派发方分别核验。
- **Windows/Linux 原生生命周期（新候选本身）**：无本机条件；旧 head CI 证据显示 native 恢复通过、仅断言差异（已核对原始日志），但旧 head 结果不等于新 head 已验证。
- **HMR 写源探针**：全程禁止，采信归档证据 + 两源文件 diff 为空。
- **真实 native sheet**：历史 Run 2 证据（同一产品源码），非本轮新拍。
- **pushState 后 health 拒绝**：本轮仅复现机制前半段，后半段为 Round 2 历史实测（他人执行）。
- **签名/安装器/干净设备/正式发布、I04 任务重连、真实项目 UI**：未验证，文档已如实登记。
- **政策切换后的补充桌面验证**：按 2026-10-20 无桌面打扰政策不再新增；如需对新候选重验真实可见/获焦/无响应，须隔离环境，且不得以 headless/隐藏窗口/禁 hang monitor/stub 提示冒充。

## 十一、结论重申与门禁状态

对 `1b6df7a220fc9a67d7046133a340085f03f0a96c → 09a2e6648edfb465debe47bc9fb15e2c6f23e088` 完整 I02 范围出具**通过**：无阻断问题；本轮新登记 R3-Z1（P3）与 R3-O1/R3-O2（观察）均非阻断；全部历史意见逐项有明确关闭/未关闭结论（§八），未关闭项均为已记录延期条件的非阻断项。

通过附带的门禁事实（缺一不可合并 develop）：
1. 另一指定模型对同版 `09a2e66` 明确通过（本轮未知、未读）。
2. push 产生新 head 的远端 CI，三平台实际全部成功（旧 run 39359486479 为 failure，不当作通过；若 CI 再需改受审文件，回新候选双方重审）。
3. 合并前核验远端 develop 实际包含本功能。

运行资源释放记录：本人自有 dev 服务器已停止、5173 无监听、无遗留测试进程；政策下达后未再启动任何窗口操作。本报告是本轮我唯一写入的文件；未修改实现/测试/配置/依赖/验收，未提交/push/切分支，未写入任何全局或跨会话记忆。
