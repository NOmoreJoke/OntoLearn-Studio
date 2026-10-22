# T09 d643 F04 修复、普通验证与 F05 旁注有限收件

结论：可以有限接收本次两路径实际修复、固定普通验证记录及 F05 新旁注；在本次静态根收件范围未发现真正阻断。**新候选可准备下一轮指定模型完整独立双审，尚不授 GUI START/新模型任务或任何新运行。**本审不自行关闭 F04/F05 原 P3、旧 Z PROCESS_FAIL、旧 Pair0、13 项作者旧意见、三项有条件 P3 或三个父项。

## 固定身份与直接检查

入口 `outputs/20261023_t09_zero_record_version_fix/handoff-manifest.json`：**10830 B / SHA256 6e0b8ad9cfe5fb480663086d67b03f46f6fb12d9bbb74325aa664accdefaa0f8**。

树 `.worktrees/T09-zero-record-version-fix-20261023`，本审实际读回当前 HEAD **60b0672c91d2fa4b87f2481b40f24bbbf22b3d2d**；其 parent 是产品提交 **d643c5a41f42d4d5395ab7d6c457c6e002cf481f**，产品 parent 是本轮基准 **0cde6a11604214f4ff34d2a9fbcfb80b6f72bfd2**。Git 直接核产品提交只有两路径 M，后续过程提交只有指定目录 **29 项新增**（含 18 gzip 原流），未把过程封存称为产品变更。

| 产品路径 | B | SHA256 |
| --- | ---: | --- |
| apps/desktop/src/renderer/src/learning/LearningWorkspace.tsx | 18669 | `5bd90f57bdb25874839c7f43bd4c61e42cf46b945675129a8a59eadce149fa9a` |
| tests/unit/learning-workspace.test.ts | 27178 | `b779a723fe46545e10f7d98c39e9da8bf69238bc0d77f2416a9c3d8055ef005a` |

清单两产品及 29 过程文件逐项普通文件/bytes/SHA、当前字节与固定 60b Git 全部一致。32-source-vector 无重复；逐项核 candidate/base765 的 blob ID、bytes、SHA 和候选当前文件，准确为 **2 变 + 30 同765**，0cde 的这 32 项也与765一致。AGENTS overlay 仍 **15147 B / de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4**，不混作产品源变更。output runner 仅核2852 B/SHA身份，未执行或 import。

三份独审（5303/2798/8032 B）、phase-and-validation、validation、F05 sidecar、source-start、Chrome pre/postflight 均全文读；两路径完整 Git diff 全文读，必要现有守卫上下文定点读。18 gzip 完整解压并阅读 stdout/stderr，未以尾部或 losslessRoundTripVerified 布尔值代核。没有未补读的展示截断，也没有复读旧两模型报告或旧全量运行材料。

## F04 实现与六项组件回归

`LearningWorkspace.tsx:29–30,63–79` 新局部 `ContextFloor.hasContextRecord` 明确区分“同 attempt 只有其他 input 辅助水位”和“当前完整 context 已有版本”。当前 context 未出现时，保留0作为合法非负比较基值，同时 hasContextRecord=false；跨 input 的 maxHintLevel/assistance 仍按同 project/task/attempt 聚合最高水位。当前已有记录包括无效/冲突投影，不能借它不通过展示校验而伪装成 absence。

hint 接收在 `:263–279` 仍先查完整 context、level、合法 record、最高提示及辅助等级；仅已有当前 context 版本才适用 `<=` 拒绝。check 在 `:294–305` 同样保留 validFeedback/最高提示/独立迁移规则及已有版本严格递增。未全局把 `<=` 改 `<`；未改 presentation 的安全非负整数、conflictVersion、辅助不降级，也未改公共 view model、持久化权威或业务适配。live/context 迟到拒绝保留。

测试新增 hint/check 各三例，共六项真实 DOM 组件案例：

1. 有其他 input 已确认辅助历史，新 input 首条合法0可接受；仍不计独立迁移。
2. 当前完整 context 已有0，重放0拒绝且不展示答案/检查结果，后续1才接受。
3. 新 input 首条0试图清除先前辅助水位，hint/check 均拒绝，答案与结果不显示、独立计数为0。

`state.version=-1` 仅是 synthetic owner 在下次自增时发出合法0，不是给组件传负版本。案例调用真实组件入口及可见 DOM，证明组件合成回调边界，**不是领域引擎、Store 或 durable provenance 集成证据**。

首轮 test blob 为27162 B/SHA `b45db359bc3b5571786eb84864b9e74294f09f4277492818b440743371149074`。本审将最终测试唯一新增精确 locator 反替换成上轮正则，得到该初始 bytes/SHA 完全一致，确认后继只修这一行定位，没有改产品或放宽断言。由 `/完整示范/` 改为 `name: '04 完整示范', exact:true` 排除侧栏歧义，保留 role/错误提示/版本0拒绝/版本1接受；未用 first/nth/force、skip 或取消断言求绿。

测试另外只增加显式 `T09_CHROME_EXECUTABLE` 入口及 browser.version 输出，默认路径仍由 Playwright 决定；headless=true、chromiumSandbox=true、移除默认 disable-hang-monitor/mock-keychain、请求全部 abort、pageerror/request为空断言仍保留。这不是把默认 bundled 浏览器或 OS sandbox 证明偷换掉。

## 九命令原收据与两流

9 份 receipt 均有 argv、唯一 own cwd、显式 env、当时 HEAD、UTC起止、runner/直接child PID与 returncode、两路径 before/after、分离 stdout/stderr。将每份 receipt 按原 JSON 格式重建，九个原 receipt bytes/SHA 精确匹配；18 个 gzip 的压缩 bytes/SHA、完整解压原流 bytes/SHA，与 receipt channel 元数据全部一致。本审读取保存记录而非重新运行，也没有访问独立输出 receipt 路径补证。

| 名称/实际目的 | child PID | 真实 returncode | 原流支持的结果 |
| --- | ---: | ---: | --- |
| setup-npm：npm ci | 9761 | 0 | 440 added/443 audited，0 vulnerabilities；deprecated/新版提示 stderr 如实保留 |
| setup-uv：uv sync --frozen | 9771 | 0 | 本树 Python3.12.12 .venv/14 packages；安装输出不是产品检查结果 |
| format-owned：仅两路径 --write | 10638 | 0 | 两路径均 unchanged，首轮测试 blob仍27162 B |
| format-owned-r2：同两路径 | 20724 | 0 | 两路径 unchanged，测试 locator 后27178 B |
| learning-runtime-first | 19636 | **1** | **39 passed / 1 failed**；22组件+18纯投影，strict locator在点击处歧义，尚未到回执 guard |
| learning-locator-affected：精确 -t | 21267 | 0 | **1 passed / 21 skipped**，是筛选跳过，不能称22全过 |
| full-check：原 npm run check | 21515 | **0** | lint→format→types→Vitest→build→ruff→pytest完整链，17 Vitest文件/**670 passed，无skip**；**1094 Python passed**，stderr0 |
| verify-sources | 19635 | 0 | 原 stdout明确 **12** 个归档源文件，非旧口述10 |
| source-diff-check：只两路径 | 22958 | 0 | stdout/stderr均空 |

三次实际组件运行明确 `T09_HEADLESS_UI=1` 且绑定 `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`，有隔离 own TMPDIR/cache/venv，T09_UI_CAPTURE未启用。最终完整套件没有名称过滤；670总数与本源22组件（旧16+新6）/18学习纯案例口径一致。最终原 stdout主要给总计，没有逐条打印22名称，不能说本审看到了每条成功案例单独原行；首轮22统计及固定源/环境与最终完整670无skip共同构成限定运行收据。首失败始终保留，不因后绿重写为首轮全绿。

原 `verify:sources` 在 locator修正前执行，但两路径 before/after 已明确当时 blob；它验证的12归档源不因这次 locator 一行改变，未冒为后继源 HEAD 上新跑。source-diff-check与full-check末段时间有重叠，是记录中的真实顺序，不把后来文件排列当运行时序或隐造重跑。

## 运行时 WIP、后提交及浏览器边界

**所有9条运行 HEAD 都是0cde，产品代码当时为未提交 WIP，不能写成在后来 d643/60b HEAD运行。**每条两路径 before=after；组件始终5bd90…，首轮及前期测试b45db…，locator后筛选/完整check为最终b779a…。最终完整check前后精确字节与d643提交相同，故可以把保存的运行结果绑定到该源候选，但不扩写成运行期间全树持续不可变证明。独审当时观察HEAD=d643、当前HEAD=60b是不同时间快照，后者29项纯过程封存不倒写前者。

首轮失败 suite 的实际stdout有 `T09 headless browser version: 155.0.8059.85`；筛选成功及最终全套成功 stdout **均没有版本行**，不从首轮或plist补造后两次launch的实际打印。已有指定路径的成功运行与显式env是真实证据，但不声称这两次也独立打印了155版本。

preflight记录 executable367696 B/SHA `6e156f2271cef44afce9db36a5b920e94518857b94a4160f082696f8c3bd1c9d`，plist18856 B/SHA `0c994f7cd1de97963191ac6e54341f5d20a551a544606636b58fc1852ee2ee23`。新增 postflight 为 **21:55:40.702829Z** 的真实后来静态采样，晚于 full-check结束 **21:53:22.598595Z**，两项值与preflight一致；不伪装成原先未落盘的“后比较”时间/原值。该收件缺口已以新明示采样材料补足，不需本审重新触碰Chrome实体。它不证明连续文件监视、浏览器进程实际映像或OS隔离。

这证明限定 headless组件运行，不等于默认 Playwright bundled版本验收、真实Electron/native、正式路由、双OS或产品发布通过。不凭没有后两次版本行另发明新版本门或要求无变重跑。

## F05 历史旁注

新 phase说明及 sidecar将旧 `docs/reviews/T09/evidence/verification-summary.json` 明确绑定 **51cdc0e9d138c98cdd4ace865074a71883657a68** 的服务/固定基线阶段，旧35学习Python/630Vitest/1087总Python不再混作765或本次计数。

本审直接核旧summary当前 **3972 B / SHA256 0acc4fafe1e334118afdb440295ca14d755babaff0494035aeeb087a9f789fa1**，与51cdc、765、0cde及d643 Git对象逐字节相同；六项声明 sourceCodeSha256分别与51cdc的对应Git字节重算一致。只是静态身份与阶段绑定，不重新证明旧命令曾运行，也没原位改summary、六个历史来源或旧报告。独立validation审当时只承接此层事实的限制保留，本审此处明确多做了该小范围身份核对，不倒填其过去已独立验证。

## 下一步与未关闭门

可以接收 **F04实现修复+对应保存普通结果**，及 **F05新阶段旁注**。下一步只需准备新d643候选的指定完整双审：完整源范围、base/源/过程分域、全部原报告/首败/流程FAIL/UNKNOWN及本次修复证据、13旧作者意见/三条件P3/三父项都保留；不能只给两路径patch或六案例，不能沿用765旧作者Pass。输入/独立环境/实际设置与执行许可仍按正式准备和调度记录办理，本报告不发START或增加创建计数。

F04/F05原P3仍按root后续处置，不以本收件直接改级/关闭；旧Z PROCESS_FAIL、旧Pair0、环境归因/global成功UNKNOWN及操作方早期越界扫描范围UNKNOWN不因修复消失。OBS01–03原到期条件、PARENT01–03、FR父项、领域/bridge/App、持久化/报告/T08/T10、资源入包、native/包装/双OS/真人原口径、CI/远端/PR/merge/57P0与Goal门保持。当前新指定任务0、Pair0、push/PR0，不把普通headless当正式接线。

本审仅 stdlib/Git/hash/JSON/文本与gzip静态收件；没有产品执行/import、测试、formatter、安装、browser/GUI/CUA、DB、全局/native/私密返回读取；没有改owner源码/证据、控制state或旧原件。只新增本根.private MD和同名JSON。
