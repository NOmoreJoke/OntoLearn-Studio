# I05 directSteps 与 shape 组合收件

2026-10-22。总控受限接收产品 `43d56317f0bfbdfeec05efc583b306615ae54a30` / 纯过程 `a15f1478e398fb3b58fd60b1421a9cad04fdb430`。已全文读取主稿、独立增量审查，并逐核144受控及143新过程的原始字节、manifest和固定Git身份，共29292909字节；旧1095过程仅核Git对象身份保持，不重复读取旧257MB。根核验细节见 `I05-controller-shape-combination-delta-proof.json`。

相对fb99仅semantic.py的两个_shapes集合采用3bd，三个新增原件与3bd Git完全相同；其余AST及逻辑保持DAG版本。正常完整检查实际1125TS、4990Python通过、44既有跳过，12来源退出0；77DAG与26shape在同一完整检查，不重复累加。26观察含9次真实Validator调用，四项旧差异完整报告与固定golden一致。

旧失败及early启动失败保留；date-entry和illtyped-entry仍pending。上述接收仅覆盖固定组合源码和证据，不关闭正式Job/Store/selected、父功能、双指定模型、CI、OS/真人及远端合并门。原I05树冻结，T05按另行精确窗口采用。根未运行产品、测试或构建。
