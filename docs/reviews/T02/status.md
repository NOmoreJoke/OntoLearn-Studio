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
