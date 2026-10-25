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
