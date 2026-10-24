# I02 Round 1 独立对抗性审查报告（ZCode / GLM-5.3）

日期：2026-10-20。审查者：ZCode 桌面端独立只读审查任务。

## 最终结论

**通过。** 未发现阻断问题。固定范围 `1b6df7a220fc9a67d7046133a340085f03f0a96c → 2cc03da82ffccc8448c7b03dc6cff87595027653` 的实现满足冻结的 I02/C1 全部验收项；我对构建态、真实打包 executable、开发态（不含 HMR 改源探针）三套关键矩阵做了独立复现，全部通过，且独立生成的打包态矩阵与冻结证据逐字段一致。共提出 3 项非阻断 P3 建议与 2 项观察，均允许延期，不影响通过判断。

## 一、评审任务、模型及思考设置的来源记录

- 任务标识：I02-R1-ZCode-GLM53-20261020-0735。
- 任务来源：I02 开发会话按 `docs/iterations/I01/inputs/goal-objective.md` 第四节流程，通过 computer use 在 ZCode 桌面端新建的独立审查任务；本报告依据该任务提示词执行。
- 模型：GLM-5.3；思考程度：最高。任务创建时通过 ZCode 原生 Open 目录选择器重新核验了完整仓库路径，分支下拉当前选中 `feature/I02-csp-window-lifecycle`（以上为任务方直接声明，非本报告自行推断）。
- 独立性：本轮未读取另一模型（MiniMax）的任何报告；未以开发者验收摘要或内部审查结论作为依据，仅将其作为待核对对象。

## 二、项目路径、分支与版本

| 项 | 值（本报告实际核验） |
| --- | --- |
| 项目绝对路径 | `/Users/kyle/Documents/工作/知爻/本体/OntoLearn-Studio`（`git rev-parse --show-toplevel`） |
| 分支 | `feature/I02-csp-window-lifecycle`（`git branch --show-current`） |
| base SHA | `1b6df7a220fc9a67d7046133a340085f03f0a96c`（同时为 merge-base，单提交候选） |
| head SHA | `2cc03da82ffccc8448c7b03dc6cff87595027653`（当前 HEAD） |
| 工作区 | 15 项既有未提交修改/未跟踪文件（任务所述 64 项保护对象的载体），全程未触碰；审查结束后逐一复验哈希一致。审查过程曾误在仓库根产生 2 个临时提取文件（`index.html`/`index.js`），确认为本人 asar 提取产物后已删除，`git status` 恢复至审查前状态 |

## 三、需求与验收依据（已完整读取原文，非摘要替代）

1. 仓库 `AGENTS.md`（含"渲染端不得直接使用 Node/文件系统/shell/通用 IPC""本地优先"等约束）。
2. `docs/iterations/I01/inputs/goal-objective.md` 全文，重点第四节双模型审查规则。
3. `docs/iterations/I01/inputs/scope.md` I02/C1 行：单配置双变体、生产 meta 或 meta+header 固化、开发 nonce/HMR 不受生产 meta 误阻、统一窗口加固/来源与主 frame 校验、崩溃/无响应恢复、三环境正常+阻断矩阵、恢复不得重复写入、当前仅 health 恢复实测且任务重连留待 I04。
4. `docs/iterations/I01/inputs/m0-review-and-update-plan-2026-10-19.md` C1 全文（含"不得向开发页面注入阻断 HMR 的生产 meta""生产脚本不允许 unsafe-inline/unsafe-eval""只检查 meta 存在或控制台无报错不能视为通过"等）。
5. PRD V0.6 `docs/prd/PRD-本体学习与落地Agent工作台.md` 8.7 / 10.3 / 10.4 / 12.5 实际条款。
6. I02 解释/验证记录：`docs/iterations/I02/design.md`、`acceptance.md`、`commands.md`、`evidence/*`、`inputs/*`（原始 CSP 实测逐字快照与来源哈希）。

## 四、已检查范围

- **固定 diff 全量**（34 文件，+2628/−23）：`.prettierignore`、`apps/desktop/electron.vite.config.ts`、`apps/desktop/src/csp.ts`、`src/main/index.ts`、`src/main/window-recovery.ts`、`src/main/window-security.ts`、`tests/e2e/csp-lifecycle.spec.ts`、`tests/e2e/native-driver.ts`、`tests/e2e/native-recovery.cjs`、`tests/unit/{csp,window-recovery,native-driver}.test.ts`，以及 I02 文档/证据（按流程证据对待，未当作代码差异）。
- **未改动上下文核对**：`src/main/trusted-document.ts`、`src/preload/index.ts`、`src/renderer/index.html`、`src/renderer/src/App.tsx`、`tests/e2e/desktop.spec.ts`、根/桌面 `package.json`（范围内无依赖或锁文件变更）、`.gitignore`、playwright 配置；并对比 base 版本 `main/index.ts` 确认旧行为（恒定 header 注入、per-window 局部加固）向新结构的完整迁移。
- **冻结与保护核验**：`evidence/frozen-files.json` 15 项、`preexisting-files.json` 64 项，SHA-256 全部与当前工作区一致（审查开始与结束各核验一次）。

## 五、验证命令与实际结果（本人独立运行）

| 命令 | 结果 |
| --- | --- |
| `npm run check` | 通过：eslint 0 警告、prettier、tsc、vitest 4 文件 14 项（含 6 项恢复竞态、2 项 native 驱动故障模拟）、electron-vite build、ruff + pytest 198 项 |
| `npm run verify:sources` | 通过：13 个归档源文件一致 |
| `npm run test:e2e`（构建态，未设 I02_HMR/I02_EVIDENCE） | 2/2 通过（C1 真实 CSP/恢复矩阵 19.4s + 桌面冒烟） |
| `npm run package:dir` 后 `ONTOLEARN_PACKAGED_EXECUTABLE=… npm run test:e2e`（证据写 /tmp） | 2/2 通过；矩阵关键字段与冻结 `packaged-matrix.json` 逐字段一致（详见下） |
| `ELECTRON_RENDERER_URL=http://127.0.0.1:5173 npx playwright test tests/e2e/csp-lifecycle.spec.ts`（先起 `npm run dev`，**未设 I02_HMR=1**） | 1/1 通过（开发态矩阵，HMR 改源块按约束跳过） |
| 构建产物核验 | `out/renderer/index.html` 中 CSP meta 为 `<head>` 首元素、先于脚本/样式，内容与 `contentSecurityPolicy()` 生产变体逐字符一致；asar 内 `out/{renderer/index.html,main/index.js,preload/index.js}` 与构建产物 `cmp` 逐字节一致；renderer HTML SHA-256 `27641d72…` 与冻结 `package-manifest.json` 记录完全相同 |

独立打包态矩阵要点（与冻结证据一致）：`app.isPackaged=true`；meta 策略=`default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-src 'none'; form-action 'none'`；响应无 CSP header（生产仅 meta 属实）；内联/未授权外部 script 未执行、fetch 拒绝、接收端零请求；style 元素与 style 属性被拦、CSSOM 赋值生效；`script-src-elem/img-src/connect-src/frame-src/style-src-elem/style-src-attr` 全部 enforce；同来源异窗口 health 被拒（"请求来源不受信任。"）；native 恢复 3 窗口/2 次提示/`killed`+`unresponsive`/3 次手动 health 全 ok/`inspectorClosedBeforeFaults=true`/PASS。

## 六、需求符合性核对（冻结验收逐项）

1. **单配置生成开发/生产策略**：`src/csp.ts` 唯一工厂；生产 meta（Vite `apply:'build'` 插件）与开发 header（`whenReady` 内 `onHeadersReceived`）同源生成；单元测试覆盖非法 nonce（含注入串）与非 127.0.0.1:5173 origin 拒绝。达标。
2. **生产交付选择（仅 meta）及理由**：`design.md` 记录了 Electron 44.9.0/Vite 8.3.4 锁定版本、meta+header 与仅 meta 的比较（不需要 header 专用指令、避免叠加求交与第三套手写策略、meta 顺序可审查、官方推荐 file 页面用 meta），且明示"不以 meta 声称支持 frame-ancestors 等仅 header 指令"。`inputs/csp-packaged-probe-2026-10-19.md` 提供旧基线 header 交付的本机实测作为对照输入。我独立复核：理由成立，选择被三环境矩阵实测支撑，正常/阻断矩阵真实（见上）。达标。
3. **开发 nonce/HMR 不受生产 meta 误阻**：生产插件 `apply:'build'`、开发 `cspNonce` 仅 serve；开发态实测 0 个 CSP meta、响应 header 含 nonce，React 正常挂载、health 通过；CSS HMR/React Refresh/文档与 state 保留仅在归档 `development-matrix.json`（`hmr` 字段全 true），因只读审查禁止 `I02_HMR=1` 未独立复现——见"未验证事项"。达标（边界已注明）。
4. **统一窗口安全加固、来源与主 frame 校验**：`web-contents-created`（模块顶层注册，先于任何窗口）统一拒绝新窗口/`will-navigate`/`will-frame-navigate`/`will-redirect`/`will-attach-webview`；`securePreferences` 工厂 + `app.enableSandbox()` + session 权限全拒；health 保持 sender=当前窗口 webContents、senderFrame=mainFrame、`isTrustedDocument`（仅容 hash）三重校验；e2e 实测同来源异窗口（加载同一可信文档）health 被拒、导航/popup 不变、隔离配置生效。锚点同文档导航保留。达标。
5. **渲染崩溃/无响应恢复**：`render-process-gone`（非 clean-exit）与 `unresponsive` 触发原生对话框，默认/取消为"暂不恢复"，显式选择才重建；先建后销避免 Windows/Linux `window-all-closed` 误退出；旧窗 closed 回调不清空新窗引用；同一窗口同时最多一个提示；退出/已关闭/已恢复无崩溃时不重建；`did-finish-load` 清理旧状态。6 项竞态单元测试通过；真实 `forcefullyCrashRenderer` 与无限循环+原生输入触发的 `killed`/`unresponsive` 在构建态、打包态、开发态均独立复现（native 驱动经主进程 inspector 短暂注入后关闭，renderer 无 CDP，asar/main 未改——已核对）。达标。
6. **恢复不得重复写入 / 不虚构任务**：恢复路径零写入（不调引擎、不清数据、不重放请求），新窗初始"尚未检查"、health 仅手动；native 测试断言恰 2 次提示/3 窗口、第 4 窗即报错（无自动重启循环）。I04 重连边界仅在 design 中定义接口约束，未新增运行方法。达标。
7. **回归与边界**：生产 `connect-src` 由 base 的 `'self'` 收紧为 `'none'`（health 走窄 IPC bridge，不依赖 renderer 网络，三态实测无回归）；无依赖/锁文件/协议变更；`.prettierignore` 扩展符合"归档不批量格式化"惯例。

## 七、问题清单（全部非阻断，允许延期）

### P3-1 恢复对话框挂起期间自愈后，选择"重新打开窗口"无任何反馈
- 位置：`apps/desktop/src/main/window-recovery.ts:30-31`。
- 触发条件：`unresponsive` 弹出对话框后渲染进程自行恢复响应（`responsive=true`、`gone=false`），用户仍点击"重新打开窗口"。
- 影响：`(gone || !responsive)` 守卫使 reopen 静默不执行，对话框关闭但无任何用户可见提示。这是 design.md 明示的设计选择（不重建已健康窗口），语义正确，仅是轻微 UX 缺口。
- 证据：单元测试 `tests/unit/window-recovery.test.ts:39-51`（responsive 用例断言不重启）。
- 建议：M1 接入真实 UI 时，在对话框 detail 中说明"若窗口已自行恢复则无需重建"，或对已恢复场景给出轻量提示。可延期。

### P3-2 开发态 CSP 配置非法时以未处理拒绝方式失败，缺少明确诊断
- 位置：`apps/desktop/src/main/index.ts:60-67`；抛出点 `apps/desktop/src/csp.ts:16-18`。
- 触发条件：手工将 `ELECTRON_RENDERER_URL` 设为非 `http://127.0.0.1:5173` 或注入非法 nonce。正常流程不可达（Vite `strictPort` 固定 5173；`npm run dev` 自动注入匹配值），仅限人为误配置。
- 影响：`contentSecurityPolicy()` 在 `whenReady().then` 回调内同步抛出成为未处理 promise 拒绝：应用以无窗口、无 IPC handler 状态静默挂起，排障体验差。不影响生产与验收路径。
- 证据：代码路径推演（`void app.whenReady().then(…)` 无 catch）。
- 建议：用显式 try/catch 包裹并 `console.error` 具体原因后 `app.exit(1)`。可延期。

### P3-3 `reopen()` 内 `createWindow()` 同步失败会成为未处理拒绝
- 位置：`apps/desktop/src/main/window-recovery.ts:30-31` 与 `apps/desktop/src/main/index.ts:39-44`。
- 触发条件：恢复重建时 `BrowserWindow` 构造同步抛出（如极端显示环境异常）。概率极低；旧窗因异常发生在 `created.destroy()` 之前而保留，不会丢窗口，但无日志。
- 影响：未处理拒绝仅打印告警；不影响已提交数据与正常路径。
- 建议：`reopen` 调用点 catch 并记录日志。可延期。

### 观察项（不计为问题）
1. 生产 main bundle 每次构建内嵌随机 `__DEV_CSP_NONCE__`（`electron.vite.config.ts:11` 的 define 无条件应用），使 `out/main/index.js`/asar 哈希不可复现；生产路径因 `if (devURL)` 守卫永不使用该值，无安全影响。冻结 manifest 以 renderer HTML 哈希 + 逐字节 `cmp` 证明一致性是正确做法；未来可让 build 变体使用占位常量提升可复现性。
2. 开发变体 `connect-src` 显式列出 origin 而不含 `'self'`，二者在固定 127.0.0.1:5173 server 下等价，无覆盖缺口。

## 八、内部审查建议的复核（关闭判断）

本轮为 Round 1，无外部历史问题需复判。对 `docs/reviews/I02/internal-review.md` 记录的 3 项内部建议逐项核验：①preferences 工厂与全 contents 导航加固的区分——design.md 已明确分层，e2e 对后建窗口同时断言 listenerCount 与实际行为，**已关闭**；②恢复选择延迟竞态——6 项竞态测试存在且我本轮运行通过，`did-finish-load` 状态清理已实现，**已关闭**；③native 驱动有界失败——deadline/退出竞速、socket close 拒绝、finally 清理已实现，2 项模拟测试通过，**已关闭**。内部审查为流程证据，未作为本报告通过依据。

## 九、未验证事项与证据边界

- **开发态 HMR 改源探针**（CSS HMR/React Refresh/文档与 state 保留）：仅采信归档 `development-matrix.json`（任务约束禁止审查期间运行 `I02_HMR=1`）。开发态其余全部断言（无生产 meta、header nonce、页面挂载、health、阻断矩阵、导航拒绝、异窗口拒绝、native 恢复）已由我独立复现。
- **Windows/Linux 原生生命周期、签名/安装器/干净设备、正式发布**：未验证，`acceptance.md`/`design.md` 已如实登记为边界，未宣称覆盖。
- **I04 任务重连（project/job 身份、提交标记对账、零提交/部分轮次/响应丢失/完成后取消联验）**：按冻结范围为后续迭代联验项，本轮仅核对未夹带实现、未虚构业务能力。
- **I01 延期项**（内部 kind/错误/缓存语义）按任务约束未重开；本轮范围内未发现对 I01 存储语义的改动。

## 十、结论重申

通过。固定候选 `2cc03da` 在冻结需求范围内实现完整、证据真实、边界诚实；3 项 P3 建议与 2 项观察均不阻断，允许延期处理。本报告仅代表 ZCode/GLM-5.3 本轮独立判断，不构成对另一模型结论的任何引用或预设。
