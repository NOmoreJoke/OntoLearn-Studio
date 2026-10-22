# T09-S1 d643 新完整指定双审：当前唯一执行约定

2026-10-23，Asia/Shanghai。本约定是完整审查准备材料，不是 START、模型任务、环境安装或运行许可。当前新任务数为 0；只有总控另行发出明确准备操作票、完成各自环境核对及 GUI START 后，操作者才可用官方应用 UI 为双方各创建一个全新独立任务并提交各自完整首输入。不得恢复任何旧 SID/turn，不自行发模型消息或占用 GUI。N0/stage 仍另队列。

## 1. 固定身份、范围及规则优先级

批准集成 base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。本轮产品源：`d643c5a41f42d4d5395ab7d6c457c6e002cf481f`，tree `fbbe968e500d98eed8277588a0a535036260f12d`。两方独立 ownroot 的物理 review HEAD 均为 `60b0672c91d2fa4b87f2481b40f24bbbf22b3d2d`（detached），其在 d643 上只新增 29 项过程证据。旧产品 765、旧原验证 d969、0cde 终态包、新 d643 源、新 60b 验证封存和本次纯准备分域记录，不用物理 HEAD 代替产品角色，也不把过程提交当新产品改动。

本方 ownCWD、单份输入、完整新报告、raw/scratch、环境 namespace、唯一 fresh operator 回执精确路径由本完整输入开头及本方 `review-mapping.json` 指定。只在本方根操作。不要跟随历史材料内旧绝对路径、peer materializedPath、应用目录或旧 runtime 到其他树；相同相对路径的历史报告/证据只读本方 HEAD 内已有副本。原先各来源的提交身份照旧保留，不伪装成在本方运行。

当前 AGENTS overlay 必须为 15147B / SHA256 `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，保持未暂存、不改、不 stage、不还原。它是操作规则，不是产品源改动。原共同指令、旧本人 round-1 完整输入、旧历史索引、旧终态登记与根收件在文后逐字存为**历史证据区**；其中旧路径、HEAD、task、Goal、租约、setup、后台入口、权限发现方法及执行建议均不是当前授权。历史“已关闭”“Pass”只是原作者/当时记录，不是本轮结论。冲突以本当前约定、最新 AGENTS 和正式本人 operator 回执中的具体授权为准；本约定不扩大系统/工具规则。

原用户授权目标、完整共同指令和全部原验收不因准备而删减。原定首版 2026-10-25 是历史目标，不是新承诺；57 项 P0、PRD C–G、第 10–12 节、P1/P2 原延期及所有父门照保。不得创建、恢复、完成或更换 Goal；不维护总控 state/tasks，不将本 S1 通过写成首版上线。

## 2. 完整源审查，不是两文件 patch 审查

先核本方 cwd/Git root、detached HEAD、批准 base、产品 ref/tree、当前 AGENTS 和本方输入/映射。`source-and-evidence-manifest.json` 是本轮身份清单；其中 32 个完整源/数据文件取 d643，逐项与本方工作字节绑定，30 项同旧 765、仅 2 新 blob 是事实描述，**不得把审查范围缩成这 2 项**。`tracked-review-head.json` 登记整个 60b tracked blob 集合；其是身份索引，不等于逐文件已阅读。

完整审查 base→产品的全部 S1 实现、数据、验收及流程声明：

1. `content/learning/{course,checks,glossary,transfer-inputs}.json` 全文：六模块顺序、九任务目标/操作/完成条件/下一步、四级离线提示/示范、常见错误、23 术语三层解释、迁移输入、辅助与独立迁移口径。无模型 API 仍可读。
2. `tests/fixtures/product-baselines/` 完整 G-base/G-map-empty/G-behavior/E.5、CSV、查询、约定、coverage/cases/manifest。manifest 固定 SHA `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`，17 输入/50 计划；计划与 expected 不是实际领域通过。
3. `scripts/verify-product-baselines.py`、`packages/engine/src/ontolearn_engine/learning/{__init__,baselines,service}.py` 全部：完整性、reset 深拷贝、白名单 seed、类型/集合/顺序比较、受信 evidence reducer、最高提示与完整代做归因。仅测试新项目可经批准 Store.commit，不能覆盖用户数据或预填 oracle/推导。
4. 三项 `packages/engine/tests/test_learning_{baselines,service,jobstore_integration}.py` 全文，区分真实 RDF/Store/I04 基础设施与 SyntheticTools；不把复制 expected 当领域工具。
5. `apps/desktop/src/renderer/src/learning/{LearningWorkspace.tsx,content.ts,types.ts,presentation.ts,learning.css}` 和两项 `tests/unit/learning-*.test.ts` 全文，含现有 18 纯投影及 22 组件案例；完整身份、能力、回执、迟到、冲突、辅助单调、恶意文本及响应式边界。
6. `docs/iterations/T09/{handoff,learning-ui-contract,user-acceptance}.md`、T10 supplier facts 的 F16 UNKNOWN 声明，以及清单列出的全部原验证、失败、独审、旧指定作者报告、正式终态和本次 d643/60b 收据。审查声明是否准确，不能以“只是文档”忽略错误通过。

只读本方批准 base 的 shared Store/JobStore/coordinator/worker/protocol/contracts/resources 及必要架构上下文；不取其他线 moving HEAD，不引入 T01 新 ledger/CAS、未批 I05/I06、T09 stage 12699cc/245718/e651 或其他候选代码/环境/结果。shared owner 的当前规则仍不授本审查者写权限。

固定 PRD V0.6 必须完整阅读相关 FR-003、100–105、9.4、11.2、12.1、附录 C/D/E/G，并对原 57P0 和父门保持原口径。大 JSON/长文件可用同一获准 Read 分段完整读取或作完整数据结构核对；报告准确写实际覆盖，不能将少数键抽样、摘要或哈希当全部语义阅读。不得因输出截断丢弃余下内容。

## 3. 原完整重点反例及新增 F04/F05

- G.0 对象/关系/名称和字符串 `001` 身份；空初始工单/事件；G-behavior false、条件冻结、B-10 E-M4→E-M3/实例内 1→2、B-11 两通知；E.5 两产能八轮完整 facts/orders/consumption/actionTrace/scheduledFutureEvents/指标/双 replay。完整对象/顺序/类型不能被计数、公式或互相复制 oracle 替代。
- M-03 撤回 002 的受管事实后仍保留 002 人工备注；M-04/G-list-09 同版 CSV；规则/行为/实现版本一致；Q-01 仅 A01、Q-02 空；约束失败/修复与推理依据完整。reset 验完整 manifest 并返回独立模型，E.5 源 oracle 不能写入正式 seed。
- 内部 Store 接受不证明 canonical Project/dependencyKey 合法；点号 ID、真实 stdio、worker、收据页及重开七项 I04 测试的覆盖与限制分别核。test.atomic 与内部 confirmation metadata 不是实际业务确认或人类点击。
- LearningService 只接受匹配 project/task/attempt/input/check ID、真实成功/非空依据及受信 provenance 的 owner evidence。JSON `true` 与 `1` 不同，事实集合排序不能抹去事件/动作/轮次顺序；辅助不因再检查洗白，操作完成与独立迁移分开。
- UI 核同 context 高版本降辅助、等版冲突、矛盾新版回退旧 pass、非法水位与合法恢复、同 attempt 跨 input、project/generation/task/attempt/input 迟到、缺保存能力/保存失败先揭示、HTML/URL 文本、导出假成功。renderer 私有投影无 Node/文件系统/shell/通用 IPC/模型/持久化权威，首次挂载/重开仍靠 owner 提供完整账本。
- F04 保持原 P3，根仅有限接收实现修复与保存验证：局部 `hasContextRecord` 区分 absence 和已知 0；新 input 首合法 0 可接受，但已有完整 context 回执必须严格更大，跨 input 辅助不降。新六案例分别测 hint/check 首 0、同 context 0 拒绝后 1、首 0 洗辅助拒绝。请独立从完整当前源判断是否关闭、未关闭或证据不足，不能因根收件或 fail-closed 自动延期/降级；也不能只测六例就放弃其余源。
- F05 保持原 P3：只新加 phase sidecar 定位历史 `verification-summary.json` 到 51cdc 阶段及原 35/630/1087；旧原件不改。请判断旁注与来源/阶段是否充分，不把旧计数当 765 或本次结果，不要求篡改历史来求闭合。
- G-list-02 exactFile/exactPointer 不是完整 round DTO 比较器，课内 scenario 用 G-list-01/06；A-10 三反例不替代 T08 指定完整集。T10 supplier F16 UNKNOWN 不默认新业务答案。

## 4. 所有旧意见、延期及父项逐项重判

历史索引的 13 项全部保留：CONTENT-01~05、INFRA-01、UI-01~05、DOC-01/02。文后原索引给出触发和当时处置；本方必须从固定源/原件逐项判“已关闭 / 未关闭 / 证据不足”并给本轮依据，不照抄“已关闭”。旧 UI-01~04 的原 P1、UI-05 原 P2 等历史严重度照存，当前发现如需重新判级说明证据，不改旧原文。

三项 P3 是总控的有条件非阻断延期提案，仍未修、未关闭；双方独立判断“接受延期 / 不接受延期 / 证据不足”。原到期条件不变：

| 项                 | 内容与必须保留的条件                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| S1-OBS-01 / M F-01 | T10 正式导出接线验收前补缺能力、exported:false、异迟 context 三类组件断言；当前不声称已有覆盖                          |
| S1-OBS-02 / M F-02 | 两迁移任务 L1/L2/L3 相同的作者观察保留；后继内容候选增强，不动当前冻结题。内容/manifest 变更仍新候选和双方全新完整审查 |
| S1-OBS-03 / M F-03 | 相关内容/oracle 下次维护前补完整对象、顺序、双 replay 与固定 expected 的直接一致断言；不以计数/公式/弱互抄替代         |

Z E-01/E-02 原 P3、M F-04/F-05 原 P3 全保留。本次修复/旁注不自动关闭根处置；请逐项独立判断，既不能因历史 P3 标签豁免实际阻断，也不能因根收件自动降级。M F-01~03 与三既有延期为同对象，不重复计新增。

PARENT-01/02/03 均保留未闭：多阶段 Q01/修复前后不能重贴终态标签；G-list-02/指定完整评估集缺口；跨窗口/重开/跨 attempt 辅助归因仍须受信 durable 账本。renderer floor 和 reducer 不替代权威历史。

所有父门保留：T02–T07 真实领域执行器与阶段证据、T01 durable 学习/跨 attempt 账本及案例生命周期、业务命名 bridge/App 正式路由、课程/fixture 资源入包、T08 真实完整代做来源/指定集、T10 实际报告/项目包导出、双 OS/native/包装、至少五名真实新手 80% 原口径、CI/远端/push/PR/merge/57P0 与 Goal。S1 Pass 或三延期均不关闭父门。

## 5. 旧流程失败、首败与 UNKNOWN 不被新修复覆盖

旧一组 M 因 agent list/include_primary 和用户级 global config 查询被总控判过程 FAIL，原 turn 被官方 Stop 后正式 aborted；该组没有 Pair Pass。不能恢复其 SID、读取其被禁返回、复演发现或把旧设置搬作本方身份。

replacement-r1 两作者原 turn 均 completed，各写 bounded S1 Pass，但 Z 因明确拒绝后换 Write/Bash/同目标 argv 后继和越写面 global Read/Edit 输入被总控判 **PROCESS FAIL，原 Pair Pass=false**。其真实树 verify=1、pytest 38 failed/4 passed 与 scratch HEAD 镜像 verify=0/42 passed、名称过滤 18 passed/16 skipped 的替代关系保留；不得以作者“误报/非绕过/唯一 hook 污染”自述豁免。环境/hook 因果 UNKNOWN。

global 部分只保已知 call ID/名称/路径 metadata，实际 Read/Edit 执行或写入成功 UNKNOWN。禁止为证 UNKNOWN 打开结果正文、实际 global 目标或查成功状态。操作员早期拒绝扫描未先 whitelist 而遍历 result.value，可能处理越界字符串；未导出正文不等于从未处理/零曝光，范围 UNKNOWN。精确扫描时间 UNKNOWN，21:22:13.412416Z—21:24:47.983209Z 仅已有快照夹定窗口；后来纠正请求截断 21:20:12.768Z 不是扫描时刻。该责任与作者过程 FAIL 分列，不能重取 global 或整请求来证明边界。

原 ruff 格式失败、fixture/manifest 初期 27 digest mismatch、I04 4fail/3pass 超时、UI 入口/匹配浏览器缺失/JSX 开发生产混用、浏览器脚本 lint、Vite 类型与中间候选等全照原索引及原件保留。旧显式 headless 缺 `chromium_headless_shell-1248` 为 launch 失败，18pass/16skip 不是组件通过；未启用开关恒 skip 与 runtime 存在无关。

本次 d643 own 验证首轮是 39pass/1fail（22组件+18纯），新增 same-context0 hint 的宽 locator 同时匹配侧栏和提示按钮，尚未到产品回执 guard。唯一修正精确按钮名后，经非作者限定静态审查，筛选用例 1pass/21skip；随后原完整 check：17文件/670 Vitest 全过无 skip（22组件含6新，18学习纯）、1094 Python 及 lint/格式/类型/构建/ruff 通过，verify:sources 核12归档源 exit0。九命令 receipt、18 原两流 gzip 和三独审完整保留。

九命令运行时 HEAD 是 0cde+未提交固定 WIP，两源 before/after hash 与后来 d643 一致；不得写成运行在 d643/60b HEAD 或全树持续不可变。首轮实际 browser.version 行为155.0.8059.85，后两次成功输出没有该行，不补造。固定 executable/plist preflight 与明确后来 postflight（21:55:40.702829Z，晚于 fullcheck21:53:22.598595Z）一致；不是连续文件监控、实际浏览器进程映像或 OS sandbox 证明。初次未独立落盘后采样缺口已由新明示采样收据补足，不能冒充原先时刻。

旧 51cdc 35/630/1087、873 42学习/630/1094、765 664（18纯+16组件）/1094、旧 1440/390 图片及所有 d969 证据按阶段引用；390×844 viewport 与390×1932文件分列。当前保存普通结果不等于本方新运行、默认 bundled 浏览器验收、正式领域、native、真人或生产。

## 6. 身份只读本人 fresh 回执；禁止发现/越界与绕拒

本方指定模型/思考/权限只取本方单份 `operator-own-receipt.json` 的 fresh 官方 UI 读回。模板不是回执；字段缺失、SID/turn/设置未知就写 UNKNOWN/无法验证，不自己补齐。只允许读取操作者明确给出的本方原生完整附件精确路径；不得导出其 system/header/reminder/thinking 或其他包装上下文。

禁止 agent/session/task list/search/discovery、自省代理枚举、全局或用户级 config/AGENTS/记忆/凭据/日志/DB、应用安装包/内部 RPC/registry/认证信息、其他 task/peer 的任何发现读取。报告要求身份来源不构成例外。工程 cwd/ref/tree/批准源核对仍允许，不能扩为应用身份调查。

本方 HEAD 中清单点名的**旧完成原稿副本与历史证据**是本轮共同只读输入；这是对旧“不得读前轮另一方报告”的明确更新，不授权读旧实际 root、旧后台 metadata 或当前新一轮另一方输入/报告/状态/意见。新本轮双方完全独立，不互传意见。旧 prompt 的 peer 路径仅历史记录，不跟随读取。

未知 `.mimosa`、hook、会话 metadata 只可在具体问题必要时记路径/lstat，不能读、hash、解析、修改或删除；禁止镜像替代真实树验证、清理未登记文件或加 ignore 求绿。

**任何官方审批/权限/guard 明确拒绝即保留实际 input、拒绝和错误，停止同一被拒对象/目的并报总控。不得换工具、同义 argv/名称筛选、Python/Bash/Write 包装、脚本/子进程、另一 tree/镜像、私有 API/DB或改规则来绕过。** 不把拒绝归因“误报”后继续，不把 source hash 查询当访问被禁结果的理由。独立未受阻范围可继续；重要证据缺失如实不通过/无法验证，不能强求 Pass。

## 7. 环境与普通检查：现在仅提案，不执行

两 ownroot 从同60b新建，各自 node_modules/.venv/cache/TMPDIR/output，不借兄弟树、全局缓存或用户 profile。准备时实际尚无 node_modules/.venv；不能把目录创建或旧安装记录当新环境就绪。本人 `ordinary-setup-proposal.json` 给精确 argv/env/写路径/覆盖及停止条件，须总控另票后由操作者准备并 fresh 绑定，审查模型不得自行安装、改锁或换版本。

新普通浏览器路径明确使用当前测试已支持的 `T09_HEADLESS_UI=1` 和 `T09_CHROME_EXECUTABLE=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`。现有155事实与 executable/plist 身份只是本次已保存验证，未来精确 preflight 另据实际票核；不扫描缓存、不下载 Chromium、不从缺1248反复失败、不默认 skip 22组件、不改测试关闭 sandbox 或 hang monitor。headless=true、chromiumSandbox=true、去掉默认 disable-hang-monitor/mock-keychain、独立临时 profile、setContent/route.abort/pageerror/request 断言保持；不连用户标签、profile、服务或端口。

先完整读保存原件、核受测源；仅有具体实质疑点才在正式已绑定本方环境执行必要原普通检查，不因新审惯例重跑全 check。纯源/记录足以判断时如实说未新跑。若选跑含组件套件，必须显式 UI1/固定 Chrome，不能把 skip 当通过；失败即保首失败，不任意换环境求绿。正常允许范围仅提案所列 verify/reset、学习三项 pytest（受控临时 SQLite/stdio/worker）、学习纯/真实 headless、原 npm run check/verify:sources/源码 diff；不是任意 shell 或正式 domain、模型/API、产品服务许可。

必要运行保存真实完整 argv/cwd、相关显式 env 与继承环境未导出边界、UTC 起止、runner/实际 child PID、独立 stdout/stderr 原件和 bytes/SHA、真实整数 child returncode、本方 fixed source 前后向量。直接等待子进程，不用管道尾部/echo/isError=false/completed 代退出码；runner退出与child分列。工具只给文本时照实声明来源，不补旧缺字段。输出截断可同一获准 Read 分段读完，不换工具绕拒。

只写本轮本人报告、获准 raw/scratch、正常 node_modules/.venv/构建输出及操作者明确环境 namespace；实现/测试/内容/依赖/锁/配置/验收/输入/旧报告只读。fresh operator 回执由操作者唯一写，模型不可补值。源码漂移/环境不符/写面缺失即报告，不修产品、不切分支/提交/push/PR/merge，不私改 Goal。

禁止 Electron/e2e/native/HMR、可见产品/浏览器窗口、GUI/CUA/focus、其他常驻服务、真实 domain producer、provider API/新增付费/订阅/密钥/平台确认绕过。额度真实故障由唯一账号负责人协调；旧额度权益不等于无限支付或允许模型自行重置。本文件保留历史第九节全文，但本轮不授任何恢复、支付、GUI或 API 动作。

## 8. 全文报告与正式终态

本方中文完整报告至少七类信息齐全：来源/实际设置和 UNKNOWN；base/source/process/ownroot/输入映射及完整阅读覆盖；真实命令/原件/退出与各类未验；每项发现稳定ID、P0–P3、精确文件行/输入触发/影响/证据/建议；13旧项+3条件P3+Z E01/E02+M F04/F05+3parent逐项独立判断；明确“通过 / 不通过 / 无法验证”的有界原因；由操作者按本方原SID/原turn绑定正式terminal与全文报告hash。

不得条件 Pass、以截止日给 Pass、将缺身份/重要证据当通过；范围内阻断或必验缺失须不通过，关键证据不足须无法验证，领域/native/真人等未验分列。只有本轮同候选两新任务真实终态、全文读回、全部意见有处置及双方明确通过以后，总控才按原门决定后续 push/PR/CI/正常 merge/远端/父验收；本审查者不执行。准备完成、设置显示、草稿、storage ready、普通670/1094绿或根有限收件均不等于新任务、指定 Pass、Pair Pass 或父 Goal 完成。

操作者流程另列：未来 START 时 fresh owncwd/HEAD/模型/最高思考/权限核对、正式完整首输入受理、官方菜单SID→本人未发草稿读回→清空后 GUI RELEASE。后台只能在另行明确的本人原 SID/turn 窄路线读取全文附件/获准Read链/正式终态/报告，不续发、不发现peer、不mutate后台。未知保持UNKNOWN，任何拒绝停止同目的。当前没有该START或后台票。

以下历史证据区保原字节，**只用于追踪，不作为本轮执行命令或权限来源**。
