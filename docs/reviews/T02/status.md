# T02 FR-200／FR-201 状态

当前为**本地证据文档收口、待ROOT远端门禁**，尚未推送、创建PR、运行本候选CI或合并。整体合并可用仍为2/17，本记录不宣布M0或完整产品完成。

## 固定受审实现

- 分支：`feature/weekly-t02-fr200-fr201`；base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`。
- 受审head `cb8c9b7a5d780544b2910901ec9141236905d65c`；tree `b8010eea4e04f962598a80d767b7a9ea24d2d7e7`；27累计提交、58差异叶、1344源文件。
- 范围：真实表单CRUD、事实原ID编辑、多值、词法受控拒绝、ownership可见定位及其共享依赖闭包。已验阶段与发布边界分别记录。
- 本次后继仅追加审查／处置／状态流程证据，受审实现保持不变；精确文件清单及对应关系见[证据桥接](fr200-fr201-20261024/round-04/evidence-only-bridge.md)。

## 已完成的同版证据

| 类别               | 实际结果                                                                                                     | 范围及原件                                                                                                                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 静态／完整check    | 唯一一次自然exit0；TS39文件1892通过；Python3769收集、3719通过、50跳过、1原duplicate-ZIP警告；Ruff369格式合格 | `outputs/20261025_t02_rows_text_integration_029/`；原始日志与before／after／current守护保留                                                                                                                 |
| 开发GUI            | 原完整六例6通过、0skip／retry／flaky；57成功事务、43受控拒绝                                                 | 同目录`runtime-full6-001/`；完整Diff／Read／Job／marker绑定；仅reservedIdentity有本轮GUI，不推广其他family或Undo                                                                                            |
| package094机械     | 新内部未签名mac-arm64包；1344源／5构建同版，912项App成员type／mode／link／hash固定                           | `outputs/20261025_t11_package094_actual_001/`；非签名／公证／法律或全平台通过                                                                                                                               |
| 包内原验收         | 原18收集、16通过、2原Linux条件skip、0FAIL／NOTRUN／retry                                                     | `outputs/20261025_t01_package094_runtime_inputs_001/`；不称18项均实际执行                                                                                                                                   |
| 故障与native       | 三query在途故障真实各一次；standalone native响应0／0／1、真实CmdQ后App退出0                                  | `outputs/20261025_t01_package094_fault_native_inputs_001/`；native engine退出仍UNKNOWN，读取到施加故障非原子                                                                                                |
| named              | 24／24通过，98成功seed／follow-up事务，43拒绝                                                                | `outputs/20261025_t01_package094_named_inputs_001/`；engine24个exit／close0，App退出码UNKNOWN                                                                                                               |
| controlled text002 | 两fresh profile ASCII／Unicode各通过、0retry；56309 scalars，56309／56314 UTF-8字节、各5页                   | `outputs/20261025_t01_package094_text_inputs_002/`；原text001首败／Unicode NOTRUN及cleanup TypeError保留                                                                                                    |
| fresh指定双审      | ZCode与MiniMax各新R04任务，均本范围附条件非阻断通过、真实自然终态                                            | [ZCode最终原稿](fr200-fr201-20261024/round-04/zcode-glm53.md)、[MiniMax原稿](fr200-fr201-20261024/round-04/minimax-m31flash.md)、[逐意见处置](fr200-fr201-20261024/round-04/disposition.md)；不改写模型结论 |

上述七项阶段原始ROOT接收票、报告／自然终态针、任务ID和原文清单身份见[归档索引](fr200-fr201-20261024/round-04/artifact-manifest.json)。原执行日志位于仓库外outputs；克隆本仓库不等于已取得全部raw，须按针向原保管位置取得。

## 未关闭边界与后续门禁

- 两模型附条件意见已逐项作事实处置；M-01本次落实纯文档，其余不采／部分采纳／OPEN按原分工。ROOT尚须核全部条件，再发具体远端执行授权。
- 排序稳定性无构造性反例，保未确认观察；definitions.triples wire的早期坏词法OPEN在原始triples／Agent接线前由T01处理；通用ownership定位合同、实际方法错误码覆盖与边界回归按原负责人延期。
- 当前canonical精确输入政策按基线ADR执行；没有新human政策批准。可选改变该政策不作为当前新增前置；若改变，须新候选验证与双审。
- unknown parser／N3／Store／坏快照／损坏SQLite物理保护、standalone EOF残余、容量口径／旧超限库恢复、签名／公证／法律与_distutils来源、跨OS／参考设备／低端硬件HOLD保留。FullRead逻辑相等不代表物理DB零写，PID缺席不代表全部自然退出0或全后代回收。
- 旧R03 ZPass／MMFail、0e7完整check TIMEOUT与GUI容量失败、O027三FAIL、093的13PASS／1FAIL／2skip／2NOTRUN、受控RED、text001及fixture／guard／AX等首败均保留，不覆盖或迁移旧PASS。
- 本次不复跑产品、不制造包、不修改验收；未push／PR／CI／merge，不增加2/17。远端与发布阶段分别由ROOT按既有门禁决定。


## 2026-10-25 当前快照：aff386f6／R05 推送前技术审查已接收

本节追加当前状态；以上 cb8／O029 数值与未推送陈述保留为当时快照，不作为当前远端事实。

- 固定受审候选：base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `aff386f6b43cf60a847c9c9597265b0b1b477095`，tree `2d9b113b4b6ca25049c157c2b94fc79db42ef38d`；29 累计提交、71 差异叶、1355 tracked 源、5 构建。此后本次只追加证据归档与状态，不改变受审实现。
- 同版本地证据：O035 裸调用首败两处 Python ENOENT 原样保留；O036 按授权使用原 UV 冻结环境的一次纠正，完整 check 自然 0，TS 1892 PASS、Python 3719 PASS／50 skip、Ruff 379。O029 的 Ruff 369 是另一真实历史口径，差异原因不推定。O037 在 aff 新构建真实六例 6 PASS，57 事务、43 拒绝、58 附件。原 094 包全部 912 成员不变，旧运行按 ROOT 有界桥接保留，不写成 aff 新包运行。
- 全新 R05 双指定任务均实际自然终态，原文结论均为 ConditionalPass；ROOT 已接收推送前技术审查范围，**不是无条件整候选双 Pass，也未放行合并**。[两终稿及身份索引](fr200-fr201-20261024/round-05/artifact-manifest.json)、[21 新＋14 旧意见处置](fr200-fr201-20261024/round-05/disposition.md)、[原条款与真实证据映射](fr200-fr201-20261024/round-05/fr200-fr201-original-clause-evidence-map.md)均保留精确字节。
- FR-200 类层级、domain／range、个体类型与全部元数据已在四类表单 28 笔实际 Read／CRUD 中覆盖；不采 ZCode §4.1 将其归后续的句子，不由此推全附录 C 或父 FR 整条完成。Q6 用户已采用决定单推荐规则／规范版本；既有 canonical 政策继续，未来改变才需新人类决定。
- 当前远端：PR16 已存在且 open／未合并，head 为 `58c9bbb39338b7438e1b8ccf202c0391827d6dfb`；develop 仍 `583c05c7870ba0f8f642e3eeea1d0590e5859ca2`；aff 尚未 push、无新 CI。CI36／run 40164456782 attempt1 在旧 head 58c9，实际 PR checkout 为合成 `681ffbd0bd5e417c7097e7d9bc18ceea2605ee59`：macOS success，Quality 15 分钟取消且 packaged recovery skipped，Windows 20 分钟取消前出现 79 个 F。无真实首败断言栈或最终 pytest 总表，编码根因仍未确认；aff 只增加首败诊断配置，不能称 79F 已修或完整 Windows 验收通过。
- 本票仅允许一次本地证据提交；push／新 CI／merge 尚未授权，需 ROOT 核证据桥接后另发精确票。完整平台 CI 及全部原 HOLD 保留，整体合并可用仍为 2/17，Goal 未完成。以上历史首败、原七份报告及未提交 AGENTS／旧审查 WIP 均不纳入本次提交。

## 2026-10-25 当前快照追加：831813c6／R06 技术接收与本地证据归档

本节为当前时点追加；以上 cb8／aff 数值、未推送陈述及 R04／R05 原判仍保留为当时快照，不改写历史原件。

- 固定受审候选：base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `831813c60a32155a579a69fc9e2cbc879b8139bb`，tree `944724a8d0e2d03502de3cf6551e0cde97e5e2f4`；31 累计提交、79 差异叶、1363 tracked 物理源、5 构建。本次后继只归档证据及追加状态，产品、测试、配置、依赖与验收标准不变。
- O040 父候选 `934bd14f` 一次普通推送触发 run `40171564866` attempt1；实际合成 checkout `a0d166c59e619cb3ebbd0be1d57fc3db69ea5a9d` 的 tree 与 934 相同。macOS 593s、Quality 718s 均成功，Quality 含 packaged recovery 真实 success；Windows 328s 失败。首败是 language:47 调用 manual:486 在追踪 JSON 落盘时触发 cp1252 `UnicodeEncodeError`，发生在业务拒绝／Read／身份／HOLD／合法后继断言之前；实际 1 FAIL／980 PASS／3 SKIP／258.55s、exit1、maxfail1，余2785项及 Windows 后继 typecheck／build／E2E／package／verify 未运行。
- 8318 相对 934 只在两测试文件六处 `write_text` 增加 UTF-8 encoding；去除六关键字后完整 AST 相同。O041 指定三模块一次151 PASS；原 UV 完整 check 一次自然0（TS39文件1892 PASS；Python3769收集／3719 PASS／50 skip／1原warning；Ruff386）。进程启动 Git HEAD 为934加精确两文件工作树修订，提交后全部1363物理源与执行后相同，不冒称启动时已是8318。五build四项全同，main仅一处24字符dev nonce差；不是Windows已绿。
- O042 在实际8318新构建的原六GUI一次6 PASS／0 skip／retry／flaky，108413.912ms；runner58606自然0。58附件、57事务、43拒绝及完整Diff／Read／Job／marker绑定已独核。原四类28笔实际覆盖层级、domain／range、个体type及完整metadata，不能后移原FR200范围；仍不证明全部附录C或父FR全条完成。旧094包912成员及rootmode不变，原包运行仅有界保留，不称8318新包。
- fresh R06 两新任务均实际自然终态：Z `session_3656bb05dd7ed7d1ccfe89755a461ace`（Start Plan／GLM-5.3／最高／完全访问）原判ConditionalPass；MiniMax `mvs_e7a25882036e477fa423cd4dd3a5eced`（M3.1-Flash订阅限免／xhigh／始终授权）原判verification-incomplete。两作者均明确整个base→8318无push前技术阻断，未放行合并。两方20个当轮意见位置（含MM正面D12）及35旧意见位置均已事实处分、具名事件延期；完整1–160各自保留。模型原稿、修订优先级和终态针见[本轮索引](fr200-fr201-20261024/round-06/artifact-manifest.json)、[版本图](fr200-fr201-20261024/round-06/version-map.json)、[处置](fr200-fr201-20261024/round-06/disposition.md)。MM首稿加最终r2附录组合阅读；其额外报告命名、仅见peer目录元信息未读正文的边界均披露。
- ROOT已接收本轮限定推送前技术阶段，未重判为无条件整候选双Pass。本票只允许一次本地纯证据commit；当前远端feature仍934、develop仍583，PR16 open／未合并，8318未push、无新CI。归档commit/tree待实际产生后用外部回执绑定；须ROOT验明证据桥接，再另票决定push／CI，不自动执行远端。
- 未来CI接收须同受审实现／测试／CI／依赖：3769全集每项由最终通过或原有有据条件skip覆盖、自然0、零失败／早停／取消／timeout／NOTRUN，Windows全部后继步骤及三job真实success。`--maxfail=1`只失败早停，无筛选；Z已独立接受ROOT显式口径并将P2并入P1，不因diagnostic步名自动验收或强制改配置。旧CI36的language6／manual72／read-work1共79F缺逐例栈和完整表，原因保留未知残留；新绿不得追溯证明旧79F全同因。
- 具名OPEN事件窗口：T01在原始definitions／Agent接线前处理早期wire UNKNOWN／HOLD；T01详情合同与T02消费在对应ownership家族／方法接线前处理裸detail及缺码；T01下次授权触及witness选取时核排序观察、下次两PATH-python测试或新环境适配时维护解释器；T02 vendor与T01在新增不经封装parser入口前复核standalone EOF；T01失效、T02编辑与各下游owner在父FR／消费链整体验收前核D.2具名下游；T02下次授权整数守卫维护时考虑4299／4300。归口不等于本轮新增修复授权，不泛捕ValueError／IndexError、不按文案分类、不静默规范化、不升cap。
- FR200 GUI编辑到推导／保存查询／SHACL／报告四类真实下游失效未逐类实测；公共ontology／facts规则、同事务stale／current更新与九行正负例存在，不能称完全无证据。Q6用户已采用推荐规则／规范版本；既有canonical继续，未来改政策才新人类决定，不为当前候选重问。
- 独立HOLD全部保留：签名／公证／wholeApp法律与_distutils、跨OS／参考设备／macOS15／Win11、Q5／D2容量与旧超限库恢复、损坏SQLite物理保护、unknown parser／N3／Store／坏快照、Undo GUI／未验ownership家族、native engine及named App未知退出码。FullRead逻辑相等不证物理DB零写，已知PID缺席不证所有自然0或全部后代回收。0e7／O027／093／text001／R03 ZPass与MMFail／O022被拒probe缺raw、旧取消及首败均保留。本次无产品重跑／新包／SQL／probe，合并可用仍2/17，Goal及发布未完成。

## 2026-10-26 当前快照追加：b215f543／R07 技术接收与本地证据归档

本节追加当前时点；以上 cb8／aff／8318 的数值、远端状态和作者原判均保留为当时快照，不改写历史前缀或旧 manifest。

- 固定受审候选：base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `b215f5432d0c9f74df9e9e3fbb6120bff57703a9`，tree `7cab46f041140114d5011d86077c54aeb93d537d`；33 累计提交、88 差异叶、1371 tracked 物理源、5 构建。b215 相对父 330 只追加一行 Ruff format 排除 literal，lint、受审实现、测试、依赖、CI、预算与验收标准未改。本次后继仅归档 7 叶与追加两份状态文档；实际本地归档 commit／tree 由仓外 O049 回执绑定，不冒充新的产品验收候选。
- O047 同 b215 的实际 `uv run --offline --frozen npm run check` 一次自然 0：TS 39 文件 1892 PASS，Python 3769 收集／3719 PASS／50 原有据 skip／1 原 warning，Ruff 379。原六 GUI 一次 6 PASS／0 skip／retry／flaky，runner 自然 0；57 事务、43 拒绝、58 inline body 与完整 Diff／Read／Job／marker 已独核。五 build 在 fullcheck 前后四项 byte-exact，main 仅 24 字符 nonce 字段内 23 字节不同；GUI 前后 5／5 相同。文件身份不证内存模块／serve／HMR，也不证 Windows 已绿。
- O045 的付款／spending-limit 门禁与 O046 的 330 attempt2 FORMAT 首败分别保原件。O046 三 job Ruff lint 已通过，FORMAT 在 `round-06/minimax-m31flash-r2.md` 的 Python 围栏报 1 would／385 already，完整 3769 suite 三 job 全 NOTRUN，desktop 后继 skipped；同 run Quality 此前 I04 矩阵 144 PASS／21.89s、TS 1892、typecheck／build 实际已跑，不概称所有 Python 或构建未执行。旧 CI36 的 79F 逐例原因仍未知，新绿不能追溯倒填。
- R07 两个原 SID：Z `session_1f663b7f4a09f84efc0dcd066f28ce63`（GLM-5.3／最高／Start Plan／完全访问）；MM `mvs_8d66d37640404c25bc061bffe6311b0b`（M3.1-Flash／xhigh／始终授权）。首自然稿分别 30400B／`f25d8827…c7723`、57131B／`ce4b1ae7…6b8c8`；各同 SID 一次事实修订后分别 41817B／`a94b7ef7…19b2c`、81951B／`eee3e39d…f974a`。首稿、diff、自然终态与收据仍仓外封存；仓内仅按[别名映射与外部版本针](fr200-fr201-20261024/round-07/artifact-manifest.json)复制最终原报告、独核、版本图与处置，未将所有外部版本复制入 Git。
- 两作者原判及修订均 ConditionalPass：限定本地实现／验收通过、整个 base→b215 无 push 前源码技术阻断；merge 必须等待未来真实完整 CI。ROOT 已完整核验并接收本轮技术阶段，不是无条件双 Pass、不增加 FR／Goal／M0／发布完成度。23 个当前位置（22 原编号＋MM 原未编号现 R07-13）及 20＋35 个历史位置逐项保留归口与事件窗口，见[最终处置](fr200-fr201-20261024/round-07/disposition.md)；两份最终独核、完整 160 项与 Z 历史 55 行保全。
- 本方事实包的 372／378 扩展名误计与 `SHA1ca23…` 连写歧义保原并纠正：NUL 路径真实计数为 384／390，真正清单段 11255B、SHA256 `1ca23def…f709c`。386／379 可作静态集合对账，不能称原 run 发现／ignore／选择差因全证；作者残句按处置限定，不重写原件。ROOT 为 Codex 自动总控，不冒人类逐行审读；无新增人类放行门。Undo UI 已在，Undo GUI 未验；必要 E／G 闭包披露不等全部附录通过。
- 本票仅允许一次本地证据 commit 及规定维护文档格式／`verify:sources`／默认锁定 Ruff FORMAT 检查；不执行产品、fullcheck、GUI、package、SQL 或 probe。ROOT 票时远端 develop 仍 583、feature 仍 330，PR16 open／未合并；b215 尚无新 CI。push／PR 修改／新 CI／merge 均待另票，不能由归档自动授权。
- 未来 merge 仍须同受审实现／测试／CI／依赖下完整 3769 全集逐项通过或原有有据条件 skip、自然 0、零失败／早停／取消／timeout／NOTRUN，全部后继与三 job 实际 success，Quality packaged recovery 步骤自身 success。旧 094 的全部 912 成员与 root mode 保持，原包运行仅有界桥接，不称 b215 新包或新 runtime。
- 所有原独立 OPEN／HOLD 与具体事件窗口不变：早期 definitions wire、裸 ownership／其他家族、缺码可达性、无序未确认观察、standalone EOF、PATH-python、4299／4300 应用边界维护、FR200 编辑后推导／保存查询／SHACL／报告四类具名下游 GUI；容量／旧超限库恢复／损坏 SQLite 物理保护、unknown parser／N3／Store／坏快照、Undo GUI、native engine／named App 未知退出码、跨 OS／参考设备／macOS15／Win11、wholeApp／签名公证／_distutils／法律隐私产权与供应链均保留。FullRead 逻辑相等不证物理 DB 零写，PID 缺席不证全部自然 0。整体合并可用仍 2/17，Goal／发布未完成；旧失败、AGENTS 与旧审查 WIP 均保留且不暂存。


## 2026-10-26 当前快照追加：62d4b0a2／R08 技术阶段接收与九文档归档

本节为当前时点追加，以上各轮候选、首败、原判和远端陈述均保留为历史快照；原字节前缀不改。固定受审 base `583c05c7870ba0f8f642e3eeea1d0590e5859ca2` → head `62d4b0a2c3ad49ae37775b875a3e7e31db5fadac`，tree `7ad1d13d6a064aaa07bd046e78427e881e1732b4`，36 提交／98 差异叶／1380 tracked 源／5 构建。本次只归档九条文档路径；实际本地证据 child commit/tree、检查原始结果与其余源／构建／WIP／旧094不变证明由仓外 `outputs/20261026_t02_r08_docs_archive_058/` 回执绑定，不预写尚未发生的检查或提交成功。

- O056 同版完整 check 一次自然0：TS1892、Python3769收集／3719P／50原有据skip／1原warning；正确配置 mode2 原生0／114.075s，七配置字段与原UV基线及ordered3769相同，57整文件分片1638＋2131、setup3769／call3763／teardown3769，无缺失重号未结算。native24为21P＋3原I04skip／retry0；23个Electron自然0与1个原CSP finally SIGKILL分开，engine自然退出UNKNOWN。原422b配置资格失败/撤销保留，不以自洽计数追认资格；本轮没有产品重跑、新构建或新包。
- fresh R08 原SID：Z `session_044963784e4cae32b7da2231bfc90b43`（现有BigModel个人GLM Coding Pro／GLM-5.3／最高／完全访问，优先Start Plan实际无可用套餐，原ROOT批准同订阅fallback）；MM `mvs_8cda942f8e3b4491b0c79ed3e6ebc9cf`（M3.1-Flash／xhigh／始终授权）。MM人工交还时原任务已提交并自然完成，操作者未见证初始Send、不重复发；通过官方复制全文回读核26703B原提示/SHA054625…及EOF清单精确相同，当前实际xhigh已核。两方原输入、同7917B共同事实、各版raw、UI与自然终态针见[版本图](fr200-fr201-20261024/round-08/version-map.json)和[归档索引](fr200-fr201-20261024/round-08/artifact-manifest.json)，外部日志/旧版本没有假称全部入库。
- 最终原稿Z78771B／`98d298c20c7557ba014f53a681ee7dbe2b63279ce205b5fa1060fa5f80b00ce4`、MM167434B／`8a5209cf32e6fa458b77597fc84ebf0fd766215f66a0164916bf6311c818537b`逐字归档。两作者仍ConditionalPass、未发现push前源码技术阻断；各160条、78历史独立位置和当前Z12＋MM19本人裁定/owner/窗口完整。ROOT已全文接收同版双技术审查阶段，含594行控制层及三个主进程delta必要闭包，不继承R07，不是无条件双Pass、不走D8、不增加完成度；[31＋78逐项处置](fr200-fr201-20261024/round-08/disposition.md)和两指定独核保留全部原判与未解窗口。
- F01本轮覆盖接收已完成；F05通过当前两状态文档追加及原报告/版本/针归档履行，实际提交和检查仍按O058真实回执接收。F03接受完整逐node/phase/session/身份/coverage/自然退出和原有据skip，不凭diagnostic名称、step绿或总数验收；F06/F07/F10保原具名后续维护窗口，不声称完整sys.path等价、不接受无head/tree回单、不重写raw或扩大格式排除。ROOT本票只准一次本地文档检查与普通提交，push／PR修改／新CI／merge尚未授权；票时ROOT实核remote develop583／feature9cb、PR16 open未合并，本轮不刷新或修改远端。
- 未来CI须同交付实现/测试/配置/依赖下Windows3769全集逐项PASS或原有据skip、自然0，无失败／早停／取消／timeout／NOTRUN，全部后继typecheck/build/E2E/package/verify、Quality专项与packaged recovery步骤自身success及原三job实际success，15/20分钟不变。case7若复发须定因并处置且完整CI绿；旧79F和CI40取消／292未结算真实原因未知，新绿不倒填。作者原CI后条件确认、精确merge票与remote develop实际SHA/tree/功能复核仍待；只有实际T02 merge/remote后原T04才更新基线并必要重验。
- 已验子集纠偏：O056第18例真实定义Undo／Undo-of-Undo／owned restart通过，rev1/2/3、三个唯一succeeded Job/operation、状态和重开等式成立；仅收窄该子集，其余Undo/ownership保持HOLD。FR201受控负例S/P/O字段保留有实际toHaveValue，限本屏/具名输入。迁移468＝424P＋44条件skip及显式备份门禁P只证Store合成前向/失败原子中止，不代表人工schema降级、大规模活库、无锁或损坏SQLite物理保护。dependabot配置root npm/actions weekly与workspace实际更新、SLA/EOL未核分开；构建配置预期消费fr201.3不冒当前新包实物。
- 原件残句按处置限证，不重写：MM readProject也有前置owner与返回身份守卫，epoch/current-project才是相应增量；“仅durations/fulltrace”限CLI参数，同step另加SHARDS2；Z Top10按§5/唯一Z08-ID定位。MM F04空页/base64本人撤回、F11事实ID与operation幂等分开，组织/实际数据/法律角色无法由代码认证，不新增人类签字/产品裁决前置。
- 全部原OPEN/窗口与HOLD保持：早期definitions、裸ownership、缺码可达性、无序观察、standalone EOF、PATH-python、4299/4300、D.2推导／保存查询／SHACL／报告四下游GUI；Q5/D2容量与旧超限库恢复、损坏SQLite物理保护、unknown parser/N3/Store/坏快照、其它Undo/ownership、native engine/named App和Windows后代UNKNOWN、目标macOS15/Win11/参考设备、签名公证/wholeApp法律/_distutils/隐私产权与供应链。FullRead逻辑相等不证物理DB零写，PID缺席不证全部自然0。旧094的912成员/root0755及旧有界运行保留，不称62d4新包；AGENTS overlay、旧round01/02/03 WIP和历史首败不暂存。整体合并可用仍2/17（FR401/402），Goal/M0/发布未完成。
