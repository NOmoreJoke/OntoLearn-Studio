# M0 技术验证与交接清单

当前 PRD 为 V0.6，仍待 M0 验证；初始化仓库和开发骨架不等于完成 M0。

## 本次交付

- [x] 原样归档 PRD、可编辑 .pen 和全部现有审查文件，建立校验清单。
- [x] 桌面、受限 IPC、Python 引擎连接、运行时协议校验和错误状态。
- [x] JS/Python 锁文件、单元测试、真实桌面冒烟、CI、贡献与架构说明。
- [x] 提供当前系统未签名应用目录打包命令和 Python 运行时打包路径。

## M0 退出前待完成

- [ ] Q2：首发操作系统、架构、参考设备及签名安装验证。
- [ ] Q3：确认“学习体验优先”的单一主成功标准。
- [ ] Q5：数据量、三元组规模与容量测试口径。
- [ ] Q6：用附录 C/G 代表样例验证 RDFS + 受控规则 + 有限 SHACL，冻结支持范围及解释边界。
- [ ] Q7：确认附录 E 固定轮次模型与指标。
- [ ] 固定 G-base、G-map-empty、G-behavior、E.5 的实际数据、配置、预期输出及失败样例；目前未生成或执行这些基线。
- [ ] 项目文件格式、SQLite/图存储接口、原子提交、快照、迁移和异常恢复技术设计。
- [ ] S2 常驻协调器、ExecutionJob、取消和资源限制的运行验收与合并门禁（[I04 状态](reviews/I04/status.md)、[ADR-0003](architecture/0003-resident-coordinator-and-jobs.md)）；模型授权边界待 I06 正式集成。
- [ ] Q8/Q9：开发投入、排期和实际受测模型协议；当前不调用模型。
- [ ] 签名、公证、安装与无开发环境设备离线启动验证。

## 原型遗留事项

2026-10-19 第四轮审查报告列出的三项问题保留，未在本次改写原型：

| 项目      | 交接要求                                                     |
| --------- | ------------------------------------------------------------ |
| A-01 残余 | 对应流程页的底部主动作使用具体文案，遵循 PRD 8.3             |
| B-03      | Agent 徽章表达导师/项目模式，不保留“状态”占位                |
| B-04      | 自动保存与底部徽章给出真实状态；尚未实现保存时不得宣称已保存 |

按 FR → 附录 C、FR-602/701 → 附录 E → 附录 G 维护轻量需求追踪，不把历史审核建议自动当作新增功能。

T02 FR-200／FR-201 已完成同版静态、开发GUI、package094机械与包内验收，fresh指定双审均为本范围附条件非阻断通过；当前仅证据文档收口、待ROOT远端门禁，尚未合并且不增加整体2/17。详见[T02状态](reviews/T02/status.md)。

## 2026-10-25 T02 当前快照追加

受审候选为 `aff386f6`（29 提交／71 差异叶／1355 源）；O036 同源完整 check 自然 0、O037 同版真实六例 GUI 通过。R05 两方原判均为 ConditionalPass，ROOT 已接收推送前技术审查范围，不是无条件整候选双 Pass。PR16 已存在、head 58c9 且未合并；CI36 的 Quality／Windows 取消及 79 个 Windows 失败标记尚未关闭，aff 未 push、无新 CI；本次仅获一次本地证据归档提交，远端需另票。原 094 旧包桥接及所有原 HOLD 保留，合并可用仍 2/17。Q6 用户已采用决定单推荐规则／规范版本；其原验证义务及其他独立边界不因该决定消失。以上旧段落保留为历史快照；当前证据、原条款覆盖与逐意见处置见 [T02 状态追加](reviews/T02/status.md)。

## 2026-10-25 T02 当前快照追加：831813c6／R06

受审候选为 `831813c6`（tree `944724a8`，31提交／79叶／1363源／5构建）；O041三模块151 PASS与原UV完整check自然0，O042本head原六GUI6 PASS。O041执行时Git为934加两测试精确UTF-8修订，提交后物理源桥接，不冒Windows已绿。父934的run40171564866为macOS及Quality成功（含packaged recovery）、Windows因cp1252追踪写首败，旧CI36的79F逐例原因仍未知；新绿不得倒填旧因果。

fresh R06 Z原判ConditionalPass、MiniMax原判verification-incomplete均保留；两作者明确整个候选无push前技术阻断，20当轮位置及35旧位置已处分。ROOT已接收限定技术阶段，本票仅本地纯证据归档，仍无新push／CI／merge授权；当前远端feature934、develop583，PR16 open未合并，8318无新CI。未来须同受审全集、原有有据skip、自然0、无失败／早停／取消／timeout／NOTRUN、Windows后继及三job全success，不能只凭diagnostic绿验收。

FR200层级／domain／range／type／metadata原28笔CRUD已证，不后移范围；D.2具体下游GUI未逐类验，公共失效机制与九行正负例已有。Q6／canonical无新人类前置，全部具名OPEN窗口与法律／设备／容量／SQLite物理保护／UNKNOWN／Undo／退出码HOLD保留；原失败不覆盖、旧094不称新包。合并可用仍2/17，Goal／发布未完成。详见[T02当前追加](reviews/T02/status.md)及[R06索引](reviews/T02/fr200-fr201-20261024/round-06/artifact-manifest.json)；本节不改以上历史快照或R04／R05原件。

## 2026-10-26 T02 当前快照追加：b215f543／R07

固定受审 base583→`b215f543`（tree `7cab46f0`，33 提交／88 叶／1371 源／5 构建），相对父330仅新增一行 Ruff format 排除 literal。O047 同 head 实际完整 check 一次自然0（TS1892、Python3769收集／3719 PASS／50有据skip／1原warning、Ruff379），原六GUI一次6 PASS／0skip／retry／flaky，57事务／43拒绝／58附件已独核。五build仅main的24字符nonce字段内23字节不同，GUI前后5／5相同；不冒Windows或内存代码已验。

R07 两作者首稿和同SID一次事实修订均保留 ConditionalPass，最终原稿分别41817B／`a94b7ef7…19b2c`、81951B／`eee3e39d…f974a`；原首自然稿、diff与收据仓外封存，仓内只按[本轮别名与版本索引](reviews/T02/fr200-fr201-20261024/round-07/artifact-manifest.json)逐字节复制最终报告／独核／版本图／处置。ROOT已接收限定推送前技术阶段，23当前意见位置与20＋35历史位置均处分，不是无条件双Pass。报告残句、Ruff静态计数与SHA连写歧义按[处置](reviews/T02/fr200-fr201-20261024/round-07/disposition.md)限证；ROOT自动流程不冒人类逐行审读，Undo入口存在但GUI未验。

旧330 attempt2三job为Ruff FORMAT首败，完整3769 suite全NOTRUN；Quality此前144专项、TS／typecheck／build已跑，不能概称所有Python或构建未执行。旧79F逐例原因未知保留。b215仍无新CI；票时远端feature330、develop583，PR16 open未合并。本票只归档7叶、两维护文档只追加并作规定本地检查和一个证据commit；实际新commit／tree在仓外O049回执，不授权push／PR修改／新CI／merge。未来完整三job与全部后继、Quality packaged recovery实际成功仍是merge门禁。

FR200层级／domain／range／type／完整metadata原28笔覆盖不后移，公共失效九例不替四具名下游GUI；旧094的912成员及旧运行仅有界桥接，不称b215新包。原具名OPEN、法律隐私产权／供应链／签名公证／_distutils、跨OS与参考设备、容量和旧超限库恢复／损坏SQLite物理保护、unknown parser／N3／Store／快照、UndoGUI／其他ownership家族／未知退出码等HOLD全部保留，事件窗口不后移。整体合并可用仍2/17，Goal／M0／发布未完成，以上所有历史字节前缀保留。详见[T02当前追加](reviews/T02/status.md)。

## 2026-10-26 T02 当前快照追加：62d4b0a2／R08

固定受审 base583→`62d4b0a2`（tree `7ad1d13d`，36提交／98差异叶／1380源／5构建）。O056原完整check自然0（TS1892、Python3719P＋50有据skip／3769）、正确配置mode2完整逐node计账原生0／114.075s、native24为21P＋3原I04skip／retry0，均为原同版运行，本次没有重跑产品、构建或打包。422b配置资格失败/撤销、旧79F、CI40真实case7 FAIL及取消/292未结算均保原件，原因未知不由新绿倒填。

R08两指定原任务已自然完成，两作者仍ConditionalPass、无push前源码技术阻断；各160条清单与78历史独立位置、Z12＋MM19本人裁定和具名窗口完整。ROOT已全文接收同版双技术阶段，覆盖整候选、594行CI控制层及三个主进程delta必要闭包，不继承R07、不走D8、不是无条件双Pass。最终Z78771B／98d298c…、MM167434B／8a5209cf…原字节入库，旧各版/完整输入/同共同事实/UI/自然终态留外部精确针；两指定独核分别7637B和ROOT4098B，未误用额外8728B记录。见[R08处置](reviews/T02/fr200-fr201-20261024/round-08/disposition.md)与[版本索引](reviews/T02/fr200-fr201-20261024/round-08/artifact-manifest.json)。

F01覆盖接收已完成，F05随当前状态追加和精确九文档归档履行；实际本地child commit/tree、检查退出码与不变证明由仓外O058回执绑定，未预写检查通过。本票仅本地文档检查和普通提交，不授权push/PR修改/新CI/merge。未来仍须同交付Windows完整3769逐node、原有据skip、自然0、无失败/早停/取消/timeout/NOTRUN、全部后继及Quality专用/packaged recovery步骤自身success与三job全success，原15/20分钟不变；case7复发须定因并处置而非仅解释，作者CI后条件、精确merge票和remote SHA/tree/功能复核另验。实际T02 merge/remote之后原T04才更新真实基线并必要重验。

定义级GUI Undo/Undo-of-Undo/owned restart已验仅收窄该子集；特定FR201拒绝字段保留已验不外推全部表单；迁移424P与44条件skip、合成逻辑观察与损坏库物理保护分开。全部原OPEN/原归口窗口、其余Undo/ownership/四具名下游、容量/旧超限库恢复/损坏SQLite、unknown解析/Store/快照、目标设备与跨平台、未知退出、签名公证/wholeApp法律/_distutils/隐私产权与供应链HOLD保留。旧094有界桥接不冒当前新包；整体合并可用仍2/17，Goal/M0/发布未完成。当前详见[T02状态追加](reviews/T02/status.md)，以上历史字节前缀全部保留。

## 2026-10-27 T02 当前快照追加：240b581c／R09

受审实现base583→`240b581c`（tree `0933a331`，38提交／107差异叶／1387源／5构建）已完成fresh R09两方必要覆盖/本人意见处置并被ROOT正式接收为有界推送前技术阶段；原ConditionalPass保留，不是无条件双Pass、不走D8。Z61298B与MM188552B按原字节归档，每方160/31/权威78及Top10/9完整，extra13另列；报告过宽概括按ROOT精确限证，不改raw。见[R09处置](reviews/T02/fr200-fr201-20261024/round-09/disposition.md)、[版本图](reviews/T02/fr200-fr201-20261024/round-09/version-map.json)与[索引](reviews/T02/fr200-fr201-20261024/round-09/artifact-manifest.json)。

O064同源原完整check自然0（TS1905／Python3719P50原skip/3769），native24为21P3原I04skip，本spec六例PASS、57事务43拒绝；执行为2b parent HEAD＋exact APPLIED03，提交后240内容exact。O063无运行。本次仅7证据＋2状态新增段的普通docs后继，不复跑产品/构建/打包，实际commit/tree/文档检查与保护项由仓外O066回执绑定。票时PR16 open未合并、remote2b/base583；本轮不push/PR写/新CI/merge，当前没有240新CI/新包，旧094不冒新包。

CI41仍Quality/Windows失败、Mac成功；引擎3769完整结算不覆盖两E2E失败及后继skip。O059到helper12与060/062容器提前止步分开，根因未证不改已知终态。未来仍需完整同交付Windows逐node/原有据skip/自然0、无失败/早停/取消/timeout/NOTRUN、全部后继与Quality packaged recovery自身success及三job全success，原预算不变。观测/失败annotation不新增硬门禁，原根因UNPROVEN不增合并前必须证因。

全部原owner/事件窗口、容量/损坏SQLite物理保护/跨平台/目标设备/未知退出/其余Undo与ownership/具名下游/签名公证/组织法律供应链HOLD保留，整体合并可用仍2/17，Goal/M0/发布未完成。当前完成度以[T02状态](reviews/T02/status.md)为准；以上历史字节前缀全部保留。

## 2026-10-27 T02 当前快照追加：67b7bcbd／R10

受审base583→`67b7bcbd`（tree `78a6b5d5`，40提交／117差异路径／1396源／5build）完成fresh R10双方必要覆盖、本人意见处置与ROOT有界技术接收；两作者原ConditionalPass保留，不是无条件双Pass/完整CI、不走D8。Z77347B、MM165505B最终原件保前缀，双方160/31/权威78/R09新19＋OBS/extra13及Top9/10＋T11/T12逐项承接，归口和未来窗口不扩大。MM生成来源针不等于当前针；仅3/9断言推论不采，静态九rule参数化正反断言在位但四具名下游GUI仍独立未验。详见[T02当前状态](reviews/T02/status.md)、[R10处置](reviews/T02/fr200-fr201-20261024/round-10/disposition.md)及[索引](reviews/T02/fr200-fr201-20261024/round-10/artifact-manifest.json)。

O069同内容原check自然0（TS1912／Python3719P50原S/3769），native24=21P3原I04S/retry0，57事务43拒绝；实际b0 HEAD＋exact4WIP后与67 Git blob精确相同，未以提交标签变化冒重跑。当前7证据＋2状态仅docs后继，实际提交/tree、文档检查与保护守卫由仓外O071回执绑定。CI41/42失败/取消/部分回执及原根因UNPROVEN保留，引擎完整计账不冲抵E2E失败及SKIP；67未push、无新67CI/包，PR16 open未合并、remote b0/base583。此票无push/PR写/新CI/旧retry/merge，T04不推进；未来完整三job及全部后继/Quality packaged recovery、原预算和精确合并门禁保持。

所有原owner/事件窗口及容量/旧超限与损坏SQLite物理保护/跨OS与参考设备/未知退出/其他Undo与ownership/四具名下游/签名公证/组织法律供应链等HOLD未关闭；旧094仅原有界证据不称当前新包。整体仍2/17，Goal/M0/发布未完成；以上历史前缀逐字保留，当前完成度以[T02状态](reviews/T02/status.md)为准。

## 2026-10-27 R11 / d1aca 必要技术阶段已接收；受控docs归档

ROOT补充票controller-t02-r11-status-three-lf-exception-20261027.json核准status.md旧前缀仅删除三个历史多余LF，原字节范围[6255,6256)、[19564,19565)、[28186,28187)。原32029B/c7f935404ca25e227b391b169e243a12373b64cb6e000ba2e774b23651e039fe保存在O076/status.md.before；修后旧prefix32026B/a81628680410342b5ca3da8586201e38e3b0bda260ce93ea3b42144f7bdce238，其他旧字节顺序精确。M0旧prefix13998B/a812e0cf7d5cc8351becff6e9ff01e02f0779bee1f9a0af18feabcd2b7ad26aa仍逐字精确。保留首次格式化/prefix守卫失败和完整七文件check首败，只对此明确文档例外重验；verify:sources输入未变，沿用实测exit0/12源，不重复执行。

受审base583→d1aca3e34ec4d00095c10a14a413efb552d3776a/tree389848f84fe60325bcdcd1b7827a7ee6e039a0e1，累计43提交/125路径/1403源叶。cfcc R10归档之后，2d6仅修复M0接缝一个LF；d1aca仅两个原E2E观测修补，全部旧记录保持历史。ROOT在2026-10-27T02:36:55Z接收双方R11必要技术阶段和完整意见处置，push前源码技术阻断0；两作者原ConditionalPass保留，不是无条件双Pass或完整产品/CI放行。

ZCode GLM-5.3/最高/完全访问与MiniMax M3.1-Flash/xhigh/始终授权均为新会话同候选审查，natural03原稿逐字归档于round-11；Z74583B/05bf18b5f33991234aa1455d5d48e7049766d70973c464f39b0cf134d88271e0，MM174277B/ab0f072e2eb3a1e3224dff91352a89ff63e24e3abd6243e3c69329cc1015d5e7。各160及原163位置、Z新增3和Top9映射、MM新增9及S01alias/所有原owner窗口逐项保留。有效160分别30/51/70/9与16/48/89/7；不计产品通过数。F01必要正文阅读流程现由ROOT接收，与R11-F01计划版本化事实分开；F05登记缺口以本次两状态追加处理，仅文档状态闭合。

实际已有O074运行仍为2d6+exact2 WIP后经blob绑定d1aca，不能改写运行HEAD。既有完整check exit0：TS1912PASS、Python3769=3719PASS+50原SKIP、Ruff393；原Mac24自然driver0=21PASS+3原I04SKIP、retry0/flaky0、57交易/43拒绝（42INVALID+1ownership）、FR最终rev22及2原ID编辑，case7原op/Job/read/marker/单提交。FR22真实7create/11assert/2edit/2remove；43metadata25add/17edit/1无action字符串alias、语义26add17edit；name new23/edit15；原稿拆分残留只以owner纠正。新计时最大2223B≤4096B，C1本机成功未触发失败catch；Windows附件和超时修复仍未证。434/487资格为既有结果，无本次重算或运行。

CI41同步helper12 TypeError旧根因未证单列；CI43 C1是ready/bootstrap后child close1/null、异步原因UNKNOWN；FR整例180002ms/第21笔后最后Diff名义余474.210ms/最终rev21，新计时仅观测。CI43 failure、Quality完整3769 NOTRUN、后步骤SKIP和所有历史失败/取消不覆盖。不设push前必须证因或预算余量阈值。未来完整CI按ROOT精确票及原15/20min/完整suite和原理据skip/自然0/全部后步骤与Quality回收门禁接收。

本次soleparent d1aca的普通docs后继仅新增round-11七文件并追加本节到两状态文件；version-map记录受审身份和后继契约，实际新head/tree/检查/独核绑定在仓外outputs/20261027_t02_r11_evidence_archive_076/COMMIT-BINDING.json及HANDOFF.json，避免文档自引用。artifact-manifest绑定O075仓外169针；GUI、日志、运行库和private原件不入Git。作者raw不格式化；仅适用五份新生成文档及两份完整组装状态Prettier、verify:sources，实际退出码见仓外回执。不重跑check/build/Ruff/产品/GUI/SQL。本票不push、PR写入、新CI/rerun/cancel、merge或T04推进。

整体已合并可用FR仍2/17（FR401/402），HOLD关闭0、D8未用、Goal/M0/release未完成。组织法律/IP/隐私/真实human bus-factor、容量与坏SQLite物理保护/旧超限库恢复、包内完整GUI/签名公证、跨OS及参考8GB设备、供应链、engine自然退出及Windows后代、sys.path等价、parser/N3Store坏snapshot、下游/ownership家族/剩余Undo/旧79F等原HOLD/UNKNOWN保持。未新增人类审批需求；后续远端动作等待ROOT精确票。

## 2026-10-27 R12 / dc6 必要技术阶段已接收；受控11路径docs归档

ROOT在2026-10-27T15:09:42.632204Z实际接收base583→dc6c112ecc944116dc421f9ef569eb50e132e217/treeba11405f4e4d9ba88136ed47ce74f2848a12b9ac（sole-parent deac095f，45累计提交/135路径/1412源）的指定双审必要技术阶段与全部意见处置。两作者原ConditionalPass限定技术及首判/更正链不改写，push前源码技术阻断0；不是无条件双Pass、完整产品/CI或发布放行。

ZCode GLM-5.3/最高/完全访问，SID session_a3121c2e640b72b7a56782376270e618，最终93526B/7c4a3e32a6a87f4f877c25c03648c724133f0477fd8c375204c5c16429827a7e；MiniMax M3.1-Flash/xhigh/始终授权，SID mvs_9fdac9995ac940e0aa1105d923ebbaa4，最终310134B/a982d752cf6166f19f7b0813455280d51bbc926fa5080639dbdecd777324f013。同SID必要补读与纠错、误停/续审、原160完整输入和官方自然终态均在O081；Mini额度满后无新请求/积分/购买/reset。两原稿逐字节归档，不格式化。有效160分别30/55/69/6与21正面+17普通/53部分/65NA/4未知（归一38/53/65/4），均不是产品通过数。

stable163+Z新增3+Mini新增9=175位置及17本轮观察逐项有当前处置、理由、原owner/事件窗口和限证；Top9/S01仅alias不增位。Mini汇总算术、F-R09-03撤回/CIUNKNOWN双半面与F-R09-08→F05等由owner窄erratum处理，原稿不改；LEDGER-01只同步四条Z最终理由，独立反演精确复原旧账，其余不变。F01仅本轮必要阅读/技术收件动作闭合，F05/MM12-N1登记缺口由本次两状态追加落实，仅文档状态闭合；R11-F01仍是M0计划版本化事实，不混coverage。详见[处置](reviews/T02/fr200-fr201-20261024/round-12/disposition.md)、[完整owner索引](reviews/T02/fr200-fr201-20261024/round-12/owner-effective-index.json)、[窄勘误](reviews/T02/fr200-fr201-20261024/round-12/owner-errata.json)、[版本图](reviews/T02/fr200-fr201-20261024/round-12/version-map.json)及[247针清单](reviews/T02/fr200-fr201-20261024/round-12/artifact-manifest.json)。

已接收O081原完整check自然0：TS1924/41files、Python3798=3748PASS+50原条件SKIP/1原duplicateZIPwarning、Ruff397；原native24一次自然双0=21PASS+3原I04SKIP/retry0/flaky0，57事务/43拒绝（42INVALID+1ownership）、FR201finalrev22及两原ID编辑、case7原op单commit/0execute/0replay/1Job/完整Read与marker，146业务资格全true。实际运行仍deac checkout+精确四WIP，后四Gitblob映射dc6；不冒未来docs commit重跑。AGENTS政策overlay唯一Git/current例外，其他1411blob相等。C1成功19371ms无failureObservation，新增observer真实平台失败仍未证；FR20156.482s仅本机观察，不量化提速或证明Windows修复。O079首败/底因UNKNOWN完整保留。

旧CI41 helper12与CI43异步新形态、CI44失败/取消/NOTRUN分列。CI44 Quality engine3769=3716P53原S已完整，后verify15min取消不倒称engine未运行。dc6无新CI，本票不push/改PR/触发重跑取消CI/merge。未来须当前完整发现集合（当前3798含新增29）、原有据skip/自然0/无失败早停取消timeoutNOTRUN、全部后继/三job自身success与Quality packaged recovery自身success，原15/20min及40/45/90、5/60/180预算/断言不变。Windows诊断是条件step，maxfail只在失败时早停；单步绿不等产品/merge，不加旧根因先证、余量阈值或故意失败门。

本票直接后继sole-parent dc6，只新增round-12九文件并追加两状态，共11路径。实际新head/tree、逐字节raw/语义等价/旧前缀/原1410源/5build/7保护项及O081247针、7新生成+2完整状态文档检查/verify:sources/独立文档差异审查在仓外outputs/20261027_t02_r12_docs_archive_082回执绑定，避免自引用。仅本地普通docs提交；后继远端动作仍须ROOT精确票。

整体合并可用FR仍2/17（FR401/402），HOLD关闭0、D8未用、Goal/M0/release未完成、T04不推进。法律/IP/隐私/真实human能力与bus-factor、供应链/签名公证/包内GUI、容量/旧超限/坏SQLite物理保护、unknown parser/N3Store、engine退出与Windows后代、sys.path等价、跨OS/参考8GB设备、其余Undo/ownership及四具名下游全部HOLD/UNKNOWN原窗口保留。全部旧状态前缀逐字保留。
