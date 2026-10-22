# T09 S1 原 ZCode 完整终态收件与意见登记

原任务 `session_b0a43d8ead0ec43ae5e6eb571a653775` / 原 turn `turn_79759cfb-6abd-4aba-b35a-9003fb5bd895` 已正式 completed。模型原结论为“通过——限 T09-S1 同版有界范围”，原文完整保存在 `zcode-original-report.md`，未格式化或改写。此为原任务意见，不是总控验收，不关闭父 T09 或发布门；同轮 MiniMax 过程 Fail / aborted 保留，**没有同轮双审通过**，也不得把本 Z 结论继承给后续新 pair。

## 新意见全部登记

| 编号 | 模型级别与问题 | 模型所给位置及建议 | 当前处置 |
| --- | --- | --- | --- |
| S1-OBS-01 | P3：导出成功回执守卫缺自动化覆盖 | `LearningWorkspace.tsx:308-325,486-494`；建议能力缺席与 `exported:false` 的组件用例 | 已收件，待总控决定后继范围；未改实现/测试，未声称修复 |
| S1-OBS-02 | P3：两个迁移任务 1/2 级提示文案相同 | `content/learning/course.json` 的 transfer-repair / transfer-classify；内容调整会改 manifest | 已收件，待总控内容决定；未改内容或 manifest |
| S1-OBS-03 | P3：checks 内联 E.5 oracle 与固定 oracle 一致性无自动断言 | `content/learning/checks.json` 的 G-list-01 / G-list-06；模型称当前相等，建议一致性断言 | 已收件，待总控决定后继测试范围；未新增测试或将建议当缺陷已修 |

三项均为模型报告的观察与建议，操作者没有重新审源或独立复现实质判断，也未擅自把 P3 升降级、采纳或关闭。若后续调整产品/测试/内容/manifest，须新候选、必要验证与双方全新完整审查。

## 旧意见全部保留其原报告判定

报告逐项判“已关闭”的 13 项为：CONTENT-01、CONTENT-02、CONTENT-03、CONTENT-04、CONTENT-05、INFRA-01、UI-01、UI-02、UI-03、UI-04、UI-05、DOC-01、DOC-02。其每项依据完整保存在原报告第 5 节；这是 ZCode 独立重判，不替代总控或另一指定模型结论。

PARENT-01 / PARENT-02 / PARENT-03 均判保留、未关闭。报告列明的父缺口全部保留：T02–T07 真实领域执行器与阶段证据契约；T01 durable 学习记录/跨 attempt 辅助账本及案例生命周期；业务命名 bridge / App 正式路由；课程与 fixture 入包；T08 真实完整代做来源及指定评估集；T10 实际导出联验；双平台与至少 5 名新手 80% 原口径真人验收；CI、远端、push/PR/merge 及 57 项 P0 总门。

## 运行证据与缺证分列

固定的本人原回合公开工具返回记录了：verify 完整性检查 `exit=0` 且 `productRuntime:not-executed`；学习 pytest `exit=0`、42 passed；未设 opt-in 的 learning Vitest `exit=0`、18 passed / 16 skipped；显式 `T09_HEADLESS_UI=1` 的一次调用 `exit=1`，因匹配 Chromium runtime 缺失，18 passed / 16 skipped。最后一项是实际失败，不能计 16 项浏览器通过；模型对旧同版 headless 原件的采信原文保留，不改写为本轮浏览器实跑。

四个产品子命令的退出值来自原命令在重定向后立即捕获并打印的 `exit=` 文本；原生公开工具结果未单独暴露整数进程 exitCode / stderr 字段，不能把工具完成状态替代子命令退出值。完整调用输入和对应公开返回见 `zcode-native-public-results.json`。操作者本轮没有重跑任何产品验证，也不重复已有 32-source/current/hash/完整输入取证。

报告身份栏保留原有 UNKNOWN，以及其引用旧 incomplete 回执的原始表述；操作员后来提供的 SID/UI 设置事实见已提交 `81a670647f36a4ace7025aa13afef19ac6220718` 的 `actual-launch-receipt.json`。两者按时间和来源并列，不能回填改写模型原报告或假装该模型已读取后来回执。Z 报告与其他模型隔离，未向 Z 发送 MiniMax 意见或异常。
