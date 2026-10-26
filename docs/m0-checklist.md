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
