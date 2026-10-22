# T04-S1 修复候选 5070004：minimax 全新完整独立审查

这是新候选的完整审查输入。操作者尚未创建任务；当前没有 task ID、真实任务设置或终态。只有总控交接内部短创建窗口后，原 T04 owner 才通过 computer use 创建本方全新任务并投递本完整正文。旧 554 的双 Pass 不适用于此候选；不能把文件、安装或预约当作新审查通过。

## 唯一工作树、固定版本和写面

- 本方唯一绝对路径：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-5070004`，detached，无开发分支。固定产品 `5070004ec8e3219bea33960bd88f57f1976e9cf8`，批准共享基线 `5f910b52c69d86a1076b2032e5d3c63e715947f3`；审查前后实际 `pwd`、`git rev-parse HEAD`、`git status --short` 与 blob 均须核验。若 HEAD 后追加流程提交，须从过程映射核对产品42项仍逐字等固定507，不能自动认为它是新产品。
- 全部 base→product binary diff 为 256242B，SHA-256 `27c090fc00cd6d1a851695551c2d5e4e9714d9845b9d5f3ee91ae51f9995b030`；命令 `git diff --binary 5f910b52c69d86a1076b2032e5d3c63e715947f3 5070004ec8e3219bea33960bd88f57f1976e9cf8`。`docs/reviews/T04/p3-repair/launch/product-manifest.json` 列全42项产品文件；全部逐字核对，不能只审四P3或UI/reader/某个stage。`candidate-files.json` 的22项只是 runtime/test/fixture/probe 子集，不能替代完整42项。
- 本树 AGENTS 是最新操作指南、仅保护 M，SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`。不 stage、覆盖、格式化或把它当产品改动。最新政策按下文全文及本方 current-agents.md 执行；历史档案中的静默/无GUI/不可运行/原树路径仅为历史。
- 指定模型 **M3.1-Flash / xhigh / 始终授权 bypassPermissions**。实际本任务模型/思考/权限必须由操作者创建后逐任务读回，不能以默认配置、标题或目录推断。若报告时任务ID或设置收据尚未提供，明确缺项及其来源，不编造；操作者再用客观实际收据补充，不能改你的原始判断。
- 本方 node_modules/.venv/cache/tmp 独占。setup-minimax.json 和 setup-minimax-raw.tar.gz 是真实环境安装记录，**不是产品测试通过**。ZCode 首次npm ECONNRESET及一次成功重试已原样保留；MiniMax首次安装成功。不得在对方树、旧开发树或当前主 checkout 运行。
- 允许只读实现/测试/配置/依赖/锁/原需求/输入/历史。允许本方正常构建输出、独占 cache/tmp、反例脚本与 raw/receipt 写入 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-5070004/test-results/t04-review-runtime/minimax`，以及现有 probe 在本树 `test-results/t04-p3-repair/browser/` 的唯一命名产物。禁止修改产品/测试/fixtures/依赖/配置/验收、Git提交/分支/索引、另一方本轮 prompt/报告/反例/日志，禁止通过skip/filter改绿。
- 本方最终唯一模型报告：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-5070004/docs/reviews/T04/round-2/minimax-m31flash.md`。目录可创建，报告写完正常完成本真实任务；操作者随后从官方状态读回同 session+原 turn 终态与全文报告。报告存在不等于任务已 completed。不要写另一方报告、push、PR、merge、创建 Goal、发外部消息、读凭据或调用付费模型 API。

## 完整输入、历史与证据核对

1. 完整读取本正文、本方 setup、product-manifest 全42项、固定507的 status/acceptance、p3-repair-plan、plan-review、implementation-review、verification.json、candidate-files，以及过程补充 `post-freeze-review.md`、全部当前政策。通过固定Git blob核对，区分507产品原文与后续过程补充。
2. `prior-554-review-history.tar.gz` 与 historical-files.json 从旧冻结开发提交 `9da9da48b45b4f0cbbe084d95c3d23ebd85c579b` 原字节归档71项，含完整内审1–8、先前输入/验证/归档、旧双方原报告/运行/收件和逐意见处置。只在本方 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-5070004/test-results/t04-review-runtime/minimax/history/` 解包读取；原路径是档案成员，不能据旧路径进入旧树执行。它是既有历史，不是另一方本轮新意见；新双方不得互看本轮报告。旧文档的历史“未审/未运行/无GUI/blocked”等按原时间与对应版本读，现行操作规定由本正文和最新指南取代，历史事实不改写。
3. 历史索引是导航，不能只读摘要。逐项复核 R1-01/R1-02/R5-01..04/R6-01、同版本矛盾/已观察终态重开、同数量错义与总控 raw 归档R1修复保持。旧 M 报告开头“11项历史closed”应按其实际表为10closed＋1partial，不能抹平partial。
4. 旧双审新增四P3及本轮修复必须独立核对：D1 Z-P3-1/M-F1；D2 Z-P3-2/M-F2；D3 Z-P3-3；D4 M-F3。旧 Z 关于 columns 非空下限的观察有事实误读：`reader.ts` 的 `.min(1)` 限列名字串，不限制数组，数组允许[]；本轮未改reader或决定零列/ASK接口。不得复述错误观察作为已有保证；父元数据语义仍未定。
5. 固定T09 `873c8c051b9870aa12fc7e1dbbd3e0c358e7c380`、manifest `aaaef2c023320038bc155640566bdc69e0bb862a2836d7cc6ef49f4a632ac39e`。`approved-t09-provenance-inputs.tar.gz` 与 t09-provenance-files.json 提供全部17项原件＋PRD＋manifest，逐项hash与来源可独立核对。产品实际仅消费 G-base/conventions/unclosed-high 三副本；额外14项是只读provenance，不能说已运行它们或扩大为正式规则/行为/Store验收。相同数量不代表答案相同，必须核完整A01、Closed空集、故意错误A02反例。
6. 本轮owner原运行收据和小raw无损包位于固定507的 p3-repair/verification.json 与 owner-verification-raw.tar.gz，包含首网络/真实回归/探针定位/Zod长度/lint等失败与后续修复，不删除失败。完整check实际TS18文件719/Python1167 exit0；定向65/112；SSR14；最终真实组件DOM5。大trace/screenshots保本地ignored runtime，verification列哈希和内嵌结果；若本树无大原件，明确不可逐字核该大原件，不能用hash自述冒充已读。
7. 独立内审固定507通过，22源码/fixture/probe current=Git=manifest，51归档成员/25命令raw/10browser产物及收据一致。独审另244组纯探针仅在其原会话内联命令，缺绝对起止与独立script/raw/SHA；post-freeze-review如实记录，不能升级为owner持久运行原件，不能拿它替代你的独立判断。

## 必须完整审查的 S1

- Python query_service 与TS draft：离线告警模板、对象/返回字段/条件编译、名称/说明/SPARQL/范围/关联问题/source；IRI/语言/datatype/literal序列化的安全与完整值、边界/异常/类型；严格shape及孤立代理项拒绝；不得借编写激活执行、授权、第二公共schema/writer/Store。
- D1只统一name/SPARQL：**原串先按UTF-16 code units限128/65536，再按固定30字符去边缘空白，拒空，内部不变**。这是收紧接受面，不提高上限；description/question/RDF上限未变。当前Zod max内部按码点，所以显式s.length；Python先现有标量/原串检查，再UTF16长度，固定并集=Python29空白＋U+FEFF。两语言共用fixture原始at/above、trim超限、astral、30边缘/内部/lone-surrogate，不能只检查trim后长度。
- QueryPage/CSS：模板、基础可视条件/字段、SPARQL/model草稿可见载入、显式范围/当前历史输入/结果身份，源字符串纯文本转义；null“未记录”、空页与后续页区别、可操作检查方向、最多200行、无示例结果。D3最新state防重复/超16、只禁未选/可取消、显示计数；condition32上限保持。
- D4新建及成功saved/model载入清visual全部class/fields/conditions；生成按钮取真实visualSchema有效性并给检查提示，非法RDF类型切换不能覆盖原草稿，修正后才生成。不猜反解任意SPARQL，不改变原保存身份/documentGeneration规则。模板仍明确填自己的builder。
- 保存/复用：同名不同定义、成功真实ID回填、更新ID不变、request/document generation/edit revision、新建/切项目/载入/卸载/迟到回执/保存期间新编辑。无真实adapter时保存/执行禁用，不声称持久化，不renderer发行ID或直接Store；正式CAS/preview/confirm/commit仍缺父接线。
- results/reader：直接复用批准validator/TaskView/TaskUpdate/getResult/getResultPage/getJob/cancelJob；完整project/job/result/snapshot/scope/params身份；generation/input切换拒迟到，实际已执行SPARQL原文保留，不用编辑器当前值伪造。仅消费真实发行的cursor并核绑定、页内/跨空页稳定排序及有界锚、回收载荷保留身份；不在renderer发行cursor。不扩大bridge或公开新协议。
- 任务/取消：仅同项目query.execute，single-flight覆盖ACK后实际job重读，ACK与真实终态分开，已知版本下限跨刷新/通知/取消前查询，拒同版本矛盾和已观察终态重开但允许合法跳跃观测，旧结果与当前job区分。
- 错误固定受限INVALID_REQUEST identity/params/cursor和params.field、原始bridge异常固定internal/explainError不泄漏。无假结果/执行、第二可变权威、共享抢写、未批准依赖。
- D2 CSV：列头必string；有限实际number/boolean保规范文本（含负数/-0），null空；仅strings含列头沿用公式及前导控制字符防护，保引号双写/CRLF；非法非有限数值/对象等拒绝。核字符串负数与实际负数不同语义，前导空白/控制字符/引号逗号换行及200边界，不减字符串防护。
- 全部42产品文件、全部TS/Python测试/fixture/SSR/新DOMprobe、历史处置与新原始证据。测试通过不能替代源码审查；manifest/hash自述不能代逐字核验。完整PRD FR-400–404、FR-006、C/D/G Q-01/02/O-01、第11–12和全部57父P0/跨模块保留。

## 本轮可执行验证与实际证据

不因历史“只能静态/禁止测试”阻止本轮必要验证；也不为刷数量机械重复。可以运行本方隔离的完整`npm run check`、T04定向、SSR，发现具体疑点可在本方runtime写独立反例；允许真实组件headless/offline probe，不启动端口、不连接用户profile。没有共享main/preload/CSP/打包依赖改动，本轮不要求宽泛Electron/e2e/native/HMR/凭据测试；如确有对应风险，先报告具体缺口并由总控协调。

为避免旧轮V1–V3未捕获明确exit的问题，**每个实际测试保存完整argv/cwd/UTC起止/真实exit/raw与SHA，首失败保留**。可用本方已提供日志工具，不修改它：

```sh
python3 docs/reviews/T04/p3-repair/launch/run-review-command.py full-check npm run check
python3 docs/reviews/T04/p3-repair/launch/run-review-command.py ssr node docs/iterations/T04/ssr-probe.mjs
python3 docs/reviews/T04/p3-repair/launch/run-review-command.py component node docs/iterations/T04/p3-interaction-probe.mjs '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' review-minimax
```

失败需要纠正探针/环境时保存首失败再用新label；不能修改产品断言或筛选为绿。日志工具只输出收据，仍须读取本方完整raw。独立runtime：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T04-s1-minimax-review-5070004/test-results/t04-review-runtime/minimax`；显式npm_config_cache/UV_CACHE_DIR/TMPDIR由该工具设为本方cache/tmp，不打印其他环境变量或敏感配置。

组件probe通过page.setContent/IIFE真实QueryPage＋synthetic catalog/saved/model，无桥接/执行/持久化/模型调用，真实DOM选择/取消/载入/类型切换，独立Chrome/headless/offline/all routes abort/无HTTP端口；核5情景完整SPARQL与名称/构建清空/禁用状态。它不验证App、IPC、执行器、Store、生产CSP、下载/原生/平台或父功能。SSR14仍仅静态。

## 完整父验收与报告要求

完整T04仍待真实query.execute/项目内只读及外联拒绝、完整Q-01/02/分页/游标/时限/取消/历史、T01事务保存/恢复/撤销/过期、T08真实模型/工具闭环、ASK/RDF/实际执行元数据及适用局部图、App/T10、两OS/真人、全部父P0/跨模块/发布。S1允许独立判断，不能以“整个M0未完”拒判S1，也不能将S1通过写成父验收通过。

报告必须写清：实际任务来源/ID/真实模型思考权限与证据（未知如实）、唯一路径/branch或detached/base/product/实际HEAD、全diff及42blob与输入hash核验、已读完整范围和PRD、每条实际命令结果/未验项、历史每项及四P3逐项判断。每个新发现含严重度/实际路径行号/具体触发/影响/证据/建议。明确本固定完整S1“通过 / 不通过 / 无法验证”，并保留真实边界。不得代判另一方或授权push/PR/merge。

若模型/认证/额度/路径/源漂移阻断，保存官方错误/实际句柄/现有原件和恢复条件，不换指定模型、不创建重复任务或伪造成功。实现/测试/配置/依赖/验收/base变化须新候选、必要验证、双方全新完整审查；纯追加过程证据保持对应，不重跑无变产品。任务完成后操作者从官方状态核同sid＋原turn真实terminal、全文报告、设置/输入真实来源，不能用文件存在或当前turnfallback替代。

## 现行效率与额度规则全文

九、效率优先、额度恢复与持续执行（2026-10-20 用户更新）

本节与最新 AGENTS/scope 一起适用于总控、现有功能 Goal、后续开发会话及模块子任务；与旧提示词统一串行、额度不足一律停止后项的文字冲突时，以本节为准。用户表示 ZCode、Codex、MiniMax Code 均仍有额外重置次数；这属于用户提供的权益信息，实际余额、可用次数和恢复结果须在执行时核实，不假定无限额度。

1. **开发效率优先。** 不以节省 token 为目标压缩需求、实现、异常处理、必要上下文或验证；以正确交付和缩短关键路径为目标。充分利用实际可用的 agent 并发槽、独立 worktree 与 feature 分支，尽早开展不依赖尚未就绪接口的设计、真实探针和独立模块。不是为提高 token 消耗而重复探索、无变化重测、无效轮询或新增无关范围；普通任务不强设三轮。
2. **保留指定模型与门禁。** ZCode 的 GLM-5.3/最高思考、MiniMax Code 的 M3.1-Flash/xhigh 继续适用；Codex 保持任务既有设置，按复杂度和已授权工具能力分配 agent，不因节省额度擅自降级或更换模型。独立审查、冻结候选、原验收、双模型通过、CI 与远端核验要求均不变。
3. **额度受限先恢复。** 出现实际额度告警或明确 rate/usage-limit 错误时，先区分额度耗尽、短时限速、服务故障、账单异常和认证错误，保存 base/head、任务标识、报告与已运行证据。由总控指定每个平台/账号唯一额度负责人，查询当前额度、可用重置权益及恢复条件；不要让多个并行任务同时消费同一权益或重复充值。
4. **已有权益优先自动使用。** 用户已授权在平台及工具允许的范围内，额度受限时使用该账号已有的额外重置次数、已购余额或已配置的官方恢复能力，尽快继续原任务。仅调用实际可用、经核验的官方入口；无需逐次确认且无额外新增支付时可自动执行。若工具或平台要求该次确认，按该要求办理；如需UI由唯一资源owner依2026-10-22当前政策直接computer use，不等待额外用户桌面时段。不得绕过确认或支付验证。
5. **Codex 的具体限制。** 优先使用 `get_usage_limits` 查询；当前 `consume_usage_reset` 工具仅在五小时或周额度剩余不高于 10% 时尝试兑换已有重置，并硬性要求每次使用都取得用户对该次操作的明确确认。本节的未来批量授权不能替代该次确认。确认后每个逻辑尝试使用唯一 `idempotencyKey`，不确定结果重试必须复用原 key；`reset`/`alreadyRedeemed` 均表示该尝试已完成，不能再次消费；`noCredit`/`nothingToReset` 不得记为成功。使用后查询实际额度，区分兑换完成与额度刷新失败，不直接重复兑换。
6. **ZCode / MiniMax Code 的机制核实。** 两者的额外重置次数由用户说明，目前未在本任务中核验可调用的恢复接口或实际余额。遇限时由对应开发线核实官方状态与入口，满足第 4 条才自动使用；没有支持的方式时如实记录缺少条件。不得猜测私有接口、索取或打印凭据、自动点击未知付款按钮，亦不得声称已配置三平台无人值守充值。
7. **重置与新增付费充值分开。** 优先消费已有权益。本次用户未给出新增付款的单次金额、累计上限或套餐选项；“不考虑 token”不是无限额新增付款授权。确需新增支出时，先查明实际可选方案与费用，在交易前明确并确认单次金额及累计上限；已有明确金额授权可按其范围执行，平台/支付工具要求逐次确认时仍遵守。不得通过擅自切换付费 API、订阅升级或其他账号绕过额度门禁。
8. **恢复后续跑、受限时不停无关工作。** 以平台实际确认及额度读回验证恢复结果，再续接原任务与同一候选，不无故新建 Goal、丢弃报告或重跑不变的验证。等待确认、自然恢复或隔离环境时，继续其他已授权且不受限的开发线；保存准确恢复条件，不无限重试。持续到目标达成，但遵守实际工具/系统预算；不能用本节绕过硬限制、伪造自动续跑或将未完成标记完成。
9. **记录和透传。** 记录平台/账号的不敏感标识、实际额度来源、受限类型、已有权益、该次授权、幂等尝试标识、操作结果和复查结果；不记录凭据或付款敏感信息。总控统一更新状态，新任务提示词必须附本节与当前桌面政策；进行中任务在安全边界读取并执行，不改写已归档的冻结输入，不仅因调度/额度政策变化重开产品审查。文档更新不等于运行中 Goal 自动生效，必须向总控及各开发线实际传达并记录接收状态。

## 现行桌面操作政策全文

# 当前桌面操作政策：撤回静默限制

总控已正式read_thread核验人类最新原文：“直接使用computer use调用桌面端的工具就行，删除我之前要求的静默桌面操作”。来源chat `01a1628e-1220-7fb1-9135-97cbea4a3ed5`，turn `01a162ce-e65a-7753-84ab-47db9975c1d3`，human message `01a162cf-5a30-7e13-95ee-24d468007ce5`。这条在“现在可以登录”答复之后，当前执行以其为准。

## 立即生效

- 撤回此前静默、不占当前桌面、禁止聚焦/点击、须先预约用户时段的偏好。已授权任务可直接computer use操作桌面端审查工具及按既有验收运行本机浏览器/Electron/native；不为常规桌面操作重复询问，不把CLI认证、后台、headless或隔离桌面作为前置。
- 同一桌面应用、原生故障测试与其他互斥资源由总控内部调度。本轮最先创建ZCode/MiniMax任务的负责人是原T06聊天 `01a15bba-0c8a-7dc2-b612-5b5c4ec4a4b9`；直接创建ZCode GLM-5.3/max/yolo完整新审，保留现有MiniMax真实session/turn/stream，不重复任务、不互泄本轮意见。其自有OAuth等待已实际收尾，不再给本人CLI登录前置。T06创建已完成并释放前台；后台任务保持，不独占整个应用推理时长。当前短时创建/核验lease以execution-state.json为准，
- 尚在排队的T02/T03/T04/T07/T09/T10/T11不自行抢同一桌面；总控按实际资源交接。内部协调不是向用户重新申请桌面时段。完整必要验证可以按任务授权执行，不以“静默不了”一律停工；原native/窗口验收条件保留，不用隐藏/stub/禁hang monitor代真实结果。
- 操作政策撤回不扩大具体阶段写面/运行权：纯文档、源码静态准备、未签native caller、尚未获运行票的构建/探针，以及已被自动审批拒绝的工作仍按各自原界限；不得把桌面可用当ABI/loader/drain、SQLite损坏HOLD/whole-H/owner或其他产品验收通过。
- 指定模型/思考/逐任务权限、同版双审、必要验证、完整终态/全文报告/全部意见、CI/两OS/真人/develop远端及全部57P0保持。无新增付费、密钥读取/搬运、重置逐次确认绕过或宽泛结束用户进程授权。

## 规则传播与历史

阶段主聊天唯一修改主repo AGENTS及注册worktree政策副本；总控唯一修改common、active scope/goal-objective、permissions、state/队列。当前主AGENTS15147B/SHA `de15f6ce13795bb26fbf9807130f475fcac1e16be142bee62d70058056a5c8c4`，传播收据 `outputs/20261022_desktop_policy_update/propagation.json`；异版仅按原操作政策段更新，其余不覆盖。

历史冻结prompt、原始审查输入、历史报告与旧原件不改。新任务附当前政策，已有任务由原owner在安全边界透传；单纯guidance变化不是产品/测试/依赖/验收或base变化，不重建Goal、不因本政策重审现有MiniMax。旧“无GUI许可”“待桌面时段”“必须先CLI登录”只能按历史时点解读，不能继续成为当前阻断理由。实际派发/任务ID/设置与终态另记，不把policy落地当任务已完成。

## 指定应用权限政策全文

# ZCode / MiniMax Code 默认执行权限

2026-10-21 用户明确指令：“更新调用zcode和minimax code的权限，默认为完全访问和始终授权”。适用于本项目现有和后续对这两个应用的调用；应用权限模式不改变具体任务的职责与验收。

## 默认与实际持久化

| 应用         | 默认模式               | 本机实际配置                                                             | 本次结果                                 |
| ------------ | ---------------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| ZCode        | 完全访问               | `/Users/kyle/.zcode/cli/config.json` → `permission.mode = "yolo"`        | 原子写入并读回；其他配置与原权限子项保留 |
| MiniMax Code | 始终授权 / Full access | `/Users/kyle/.minimax/config.yaml` → `permissionMode: bypassPermissions` | 原配置已经满足，核对后保留               |

ZCode 的默认配置路径、合法模式及 yolo 跳过权限提示的语义，来自已安装应用 `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs` 的实际配置加载器、schema 和权限判定实现。修改前备份为 `/Users/kyle/.zcode/cli/config.json.before-permission-20261021-084806.bak`，仅在需要恢复时本机读取，不复制进仓库或输出其他配置内容。

MiniMax 的配置和界面映射由已安装 `@mavis/local-runtime` 实际代码独立核验：`bypassPermissions` 对应中文“始终授权”和英文“Full access”。`config.chatPermissions` 不是已证实的全局默认入口，未手造或修改。运行时官方配置更新入口会清缓存并广播变更；本轮没有启动/连接运行时、修改其桌面 store 或重启应用。

## 调用时的执行要求

1. 新任务默认使用上述模式；创建/进入实际任务时读回其显示或实际配置，不只依赖用户级文件。项目覆盖值、显式请求参数和既有会话状态可能优先于用户默认。
2. 当前计算、冻结候选和审查任务不重启、不丢弃；在安全边界确认权限，必要时通过应用支持的会话设置切换。不能仅凭配置文件改动声称所有在途会话已经即时切换。
3. 用户已授权上述默认应用权限，常规调用不因旧提示词中的默认模式重复询问。应用硬限制、系统权限和平台工具自己的确认机制仍以实际支持为准。
4. 对抗审查仍只读实现；只允许约定验证和独立报告写入，禁止修改受审实现或自行提交/推送。完全访问是执行能力，不把审查任务改为开发任务。
5. 指定模型、思考等级、同版双审、意见处理、CI与远端核验保持。2026-10-22静默桌面偏好已撤回，可由原功能owner直接computer use，互斥桌面资源由总控内部协调；不必再申请用户时段。
6. 新任务提示词和共同开发指南附上本要求；历史冻结输入保留原样，文档权限规则更新本身不触发无变化的实现重审。

## 证据与接收

- ZCode 写前 SHA-256：`c7f88256c49fbae707d57bfcd294dfa4becee03169ded1f14f9ab7b8aa47bb5f`。
- ZCode 写后 SHA-256：`67f26b9702a009fa8353b77f9f9b6d44658bd9fc41f55b31e924d872cb2124`。
- 已逐项比较非权限配置及权限中其他字段，结构相同；未修改任务数据库、应用安装包、模型或思考设置。
- MiniMax 的本轮独立只读核验确认默认已符合；没有把静态文件核验当作每个运行会话的权限回执。
- 由现有执行总控维护调用指南与派发状态，在安全边界透传进行中开发线；实际发送/回执另行记录，不假定写文件即自动生效。

## 2026-10-22 后台恢复补充

当前人类已撤回静默桌面偏好，原功能owner可直接computer use；已启动的官方CLI/app-server任务继续。原指定模型、思考等级、逐任务权限读回、同版独立审查和全文终态门不变。T06两项真实任务已启动，桌面创建动作已结束；其他线由总控内部安排资源，不自行抢建任务。

历史：昨日短时答复曾被误记未答、随后又被误作本轮新答复，原件及16:01停止记录保留。当前人类已经撤回整个静默桌面偏好，原T06直接CUA创建ZCode审查，不再以旧时段/CLI认证阻塞；现有MiniMax任务保持。详见desktop-operation-policy-20261022.md。
