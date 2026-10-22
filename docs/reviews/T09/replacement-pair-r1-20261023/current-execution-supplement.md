## 本轮当前执行补充（优先适用，不改变完整原scope）

这是 S1 replacement-r1 的两方全新完整任务准备。当前只有准备授权，任务数为 0、GUI RELEASED；总控另发 START 后操作员才可通过官方 UI 创建双方各一个新任务。审查模型收到正式完整首输入后只执行自身代码审查，不操作 GUI、不另建任务。另一 N0/stage 组继续排队，12699cc/245718/e651 及任何其余未批准实现不属于本 S1 输入。两候选不拼接。

### 1. 冻结身份与独立职责

- 共享批准 base `5f910b52c69d86a1076b2032e5d3c63e715947f3`；产品 `76596656908ed84e577e8202a602e3256d5febcc`，tree `8b646570108026a8deabe8330c548cab0280122d`；双方公共 review HEAD `72aa83a80a973a3edeb62ed95518bf1a22178985`；原流程证据 `d96924e715a1b2139a75b70aea40fc30ae1129fe`。base/source/process 必须分列，不以物理 HEAD 代产品/原流程角色。
- 操作政策维持 AGENTS 15147B / SHA-256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，M 覆盖保持不 stage、不还原。本准备复用已根接收的固定证明，不声称重新核过未来创建时的实际状态；创建时由操作员 fresh ownUI 核本人目录/设置/HEAD 绑定。
- 原完整 scope 为 base→product 全部 55 文件，32 产品源/数据路径、106 manifest 身份、869 tracked 字节基线及原全部文档/失败/验收。本文完整嵌入本方旧原文和完整历史索引，不得只审尾部或只审 UI/delta。原 PRD、17 输入/50 计划、全部重点反例、13 旧问题与 PARENT-01/02/03 全保留，各自从头独立重判，不复制旧结论。
- 双方各为新任务。不得恢复旧停止回合、继承任何旧指定模型结论或把旧受理/SID/设置/报告当作本轮证据；不得读前轮或本轮另一方的报告/提示/任务/状态/意见。下述三 P3 是总控授权的共同后继议题及延期条件，非另一模型的本轮意见，更不是预填结论。

### 2. 身份和设置只采操作员 fresh 本人回执

模型/思考/权限要求不变：ZCode GLM-5.3/最高(max)/完全访问(yolo)；MiniMax Code M3.1-Flash/xhigh/始终授权(bypassPermissions)。**审查模型只可读取本文明确指定的单份 fresh operator-own-receipt.json；它不存在、尚未写入SID/turn或字段缺失/矛盾时，报告写 UNKNOWN / 无法验证，不主动发现来补齐。** 操作员通过官方 UI 提供本人目录/模型/等级/权限/创建受理/菜单 SID 事实；原 turn 的后台绑定与正式终态由操作员在授权窄路线收件，模型不负责查询。环境自动自述、旧 setup 或旧 incomplete task-settings 回执不是 fresh 证明。

明确禁止为身份/设置/来源记录调用 `agent list`（包括 include_primary）、`session get`、session/task list/search/discovery、自省代理枚举；禁止读取/grep/哈希全局或用户级 config/AGENTS、凭据、应用状态库、全局日志、安装包/运行时内部实现、历史 metadata 和其他任务。报告要求身份来源也不构成例外。不读取旧 dispatch-runtime 目录的 task-settings/setup/raw/scratch/metadata；既有 setup 的来源身份已在本方映射中供给，只是历史安装回执，不能证明新任务配置。

只允许应用本条明确提供的**当前本人原生全文附件精确路径**经获准官方 Read 读取；该路径位于应用目录不等于可以遍历或发现附近资产。不得导出应用自动包装的 system/header/reminder、用户级指引或 thinking。只用本人 fresh 回执中实际已提供的字段；不回写/补造该回执，不另找 SID、provider registry、权限配置或后台入口。未知 `.mimosa` 等元数据只允许路径/lstat，不能读、hash、解析或删除。另一方冻结 prompt 在旧 manifest 中仅登记身份，不读取其正文或借 hash 核验打开它；同样不跟随其 materializedPath。

自身 cwd/Git root/ref/tree、获准固定工程源与对应 manifest 的工程核对仍按完整scope进行；它们不授予应用身份发现。固定原文中的全局路径/旧后台快照仅为历史说明，不能跟随读取。shared 源仅取本文批准 refs 与本方已批准物化副本，不采用其他线新代码或 moving HEAD。

### 3. 新写面、旧原件与隔离

本方精确 owncwd、报告、raw/scratch/cache 和单一 fresh operator 回执路径见本方 replacement-mapping.json 与本输入开头。它们覆盖嵌入旧原文的原开发树/round-1/旧 dispatch-runtime 写面；旧 round-1 报告、旧 launch/terminal packet、旧指定模型当前意见与原运行元数据均不得读取或覆盖。仅本方固定 manifest 列出的历史内审/验证原件是完整原scope的输入，按角色/ref取用，不扩大至此后新增模型材料。

保留所有旧文件和失败，不删除、不加 ignore 求绿。只可写本轮明确报告、私有 raw/scratch、必要正常构建输出；新 fresh operator 回执由操作员唯一写，模型只读。输入/源码/测试/依赖/锁/配置/验收只读；不提交、切分支、push、PR、merge或改Goal。cwd/基线不同、源漂移、映射缺失或写面冲突时报告实际问题，不自行换兄弟树、重新绑定环境、安装依赖或修产品。

### 4. 必须保留的此次流程失败和首败

先前创建组中一侧实际执行了禁止的 `agent list(include_primary=true)` 及对用户级 global config 的 `grep permissionMode`，总控判该侧过程 Fail；已由操作员官方 Stop，原 turn 正式 `aborted`。曝光范围 UNKNOWN，不宣称具体泄露或零泄露；本轮不提供/不读取这些调用的返回，不重演命令、不尝试相同发现。另一独立任务不获得该侧意见。操作者曾过宽投影应用 reminder，事实保留而多余上下文排除在正式 packet；这不授权审查模型回读包装上下文。本轮不得把前组当作已有双审通过。

同候选既有一次显式 headless 首败事实：`T09_HEADLESS_UI=1 npx --no-install vitest run learning` 子命令捕获退出文本 1，`browserType.launch: Executable doesn't exist`，所需 `chromium_headless_shell-1248` 当次缺失；输出18 passed / 16 skipped。未设 opt-in 的那次为退出文本0、18 passed /16 skipped；学习 pytest42 passed、verify 完整性 `productRuntime:not-executed`。这些是操作员供给的历史运行事实，不是本方新运行、不证明当前runtime，也不传递前模型结论。原公开工具未独立暴露整数 exitCode/stderr 字段，缺证保留；不要用其 completed/isError=false 替代子命令退出码。已根收的来源不要求再次取证；本方如需实质疑点核对，可读本方原scope内固定验证原件，不得转读前一模型目录。

原 ruff/npm digest mismatch、I04 超时、UI入口/浏览器缺失/JSX失败、lint/type和中间候选原件及顺序全按历史索引保留，不以最终成功覆盖。此次首败也保留；默认 skip 不是浏览器通过，显式失败不是16组件通过。旧同版 fullcheck/headless/截图的强度及是否足以支持本轮结论须本方独立判断，不能预设采信或给条件Pass。

### 5. 三 P3 的总控有条件延期，需本方独立重判

总控仅把以下延期认作**当前有界 S1 非阻断延期**，未改冻结产品/题目/测试，未将问题标已修或关闭；不能由总控代另一指定模型给 Pass。逐项报告“接受延期 / 不接受延期 / 证据不足”及独立理由，发现实际更高严重度或范围内必验缺失须照实判断，不因P3标签豁免。

| 编号      | 待改进对象                                                | 总控延期条件及触发门                                                                                                                         |
| --------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| S1-OBS-01 | `LearningWorkspace.tsx` 的导出成功回执守卫缺组件断言      | **T10 正式导出接线验收前**补缺能力、`exported:false`、异迟 context 三类组件断言；当前不声称已有覆盖或已修                                    |
| S1-OBS-02 | `course.json` 两迁移任务1/2级提示区分度                   | 留待**后继内容候选增强**；不得改当前冻结题，不暗示已修；内容/manifest实际改变仍新候选和双方全新完整审查                                      |
| S1-OBS-03 | checks 内联 E.5 oracle 与固定 expected 的一致性缺自动断言 | **相关内容或 oracle 下次维护前**补完整对象、顺序、双 replay 与固定 expected 的直接一致断言；不能只比较长度/计数/公式、互相复制或弱化完整比较 |

13项旧问题 CONTENT-01~05、INFRA-01、UI-01~05、DOC-01/02须逐项从固定源码/原件重新判“已关闭/未关闭/证据不足”；嵌入历史索引的“已关闭”只是当时记录，不是本轮默认结果。PARENT-01/02/03均保留，不能以这三项延期关闭。

### 6. 正常验证、真实 child exit 与审批拒绝

只因具体疑点选择原批准的对应普通检查，说明理由；不因“新审惯例”机械重跑所有 unchanged check，不用本准备触发重测。原 `npm run check` 的lint/format/types/vitest/build/ruff/pytest链、学习专项与受控stdio临时SQLite/worker授权仍按旧执行补充，不等同新native/HTTP/生产/正式领域调用。运行只在本人独立既有node_modules/.venv与本轮scratch/cache，不使用用户数据/兄弟环境。

必要运行必须先记录完整argv/cwd/env差异/开始时间，stdout、stderr原始完整保存到本人raw的不同文件；用直接子进程等待获得真实整数returncode（例如 `subprocess.run(argv, cwd=owncwd, env=..., stdout=out, stderr=err, check=False).returncode`），连同退出时间、原件bytes/SHA写本方运行收据。运行器自身退出也保留，不把它与产品child混为一谈。若只获原生工具文本而无独立整数字段，明确哪些值来自子进程收据、哪些native字段不可观测。**不用 tail/grep/tee/管道末命令/echo 的成功掩盖真实child失败，不把isError=false或报告自述当exit0。** 阅读原件因UI截断可经原已获准的同一Read分段完整读取，保首失败/纠正；不伪补旧raw、删失败或只交摘录。

**任何官方工具审批/权限拒绝必须保留实际拒绝并停止该被拒路径/能力；不得包装、换 Bash/Python/cat/base64/脚本/子进程/私有RPC或另一工具读取/运行同一被拒对象来绕过。** 不把缺签/会话状态冲突当命令失败再试“同义命令”。缺关键源或验收据实不通过/无法验证并报告总控；可继续未受拒绝影响的独立范围，不自行扩大授权。

### 7. 浏览器、环境与全部未验边界

本准备沿用原两方各自已绑定环境，**没有新环境/浏览器安装或setup票，没有运行产品或浏览器探针**。已知历史1248缺失不是新的缓存盘点；不为已知失败重跑headless，不靠不同Playwright/Chromium版本、全局缓存或更宽sandbox求绿。原证据不足可据实写待验，不强制生成Pass。

若本方认为需要新增/补齐浏览器环境，先停止该安装/启动路径，只报告：本人node_modules中精确Playwright版本及其官方browsers.json所需revision、本人**明确授权私有缓存路径**的存在/lstat事实、拟最小setup argv、下载/写路径与影响、是否改锁/源码/共享缓存；等总控另给精确setup票。不得扫描全局缓存、安装包/应用内部、用户目录或用另一版本临时替换。未绑同版runtime不得把16 skip转Pass。审查模型不运行 Electron/e2e/native/HMR、可见浏览器/产品窗口、其他常驻服务、真实domain producer/API/付费/密钥或平台确认绕过。

静态、纯投影/reducer、真实I04基础设施、headless组件、领域、包/native、双平台、真人和生产分列。T02–T07真实领域执行器/阶段证据、T01 durable学习/跨attempt辅助账本及案例生命周期、业务命名bridge/App路由、课程/fixture入包、T08真实完整代做/指定评估集、T10实际导出/项目包、Windows/macOS、至少5名真实新手80%原口径、CI/远端/push/PR/merge与57项P0原门全部未闭；S1或延期不关闭父门。

### 8. 全文报告与正式终态

完整报告只写本轮新路径，至少包含原全文所有七类要素：来源/UNKNOWN，base/source/process和完整覆盖，实际命令/真实退出/完整raw及未验，所有发现精确触发与证据，13旧问题+3P3延期+3parent逐项独立处置，明确通过/不通过/无法验证及完整有界原因，报告与正式terminal绑定。关键身份/重要证据不足按原门判无法验证；范围内阻断/必验缺失不得Pass；不写条件Pass。

operator-only创建/收件工作不转授审查模型。未来START后操作员 fresh核本人cwd/HEAD/模型/权限，正式完整附件受理，官方菜单SID→本人未发草稿读回→清空，即GUI RELEASE；后台仅按本人新SID/原turn授权窄路线保完整附件/Read链/正式terminal/全文报告，不续发、peer发现或后台mutation。未知字段保UNKNOWN。新一对双方同候选实际终态、全文读回、全部意见处置与双方明确通过之前，不push/PR/合并；之后也须原CI/远端/父门。新输入准备不等于任务启动、验收通过或Goal完成。
