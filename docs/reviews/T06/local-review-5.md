# T06 固定输入适配候选完整本地独立审查

审查者 `/root/behavior_independent_review`。结论：**不通过本轮新增适配边界与诊断完整性审查**。2 项 P2 可复现；固定九例和既有算法回归均通过。

候选 `567ab48f2b1cd9a89e2763846c1a0f258ff60a84`，分支 feature/weekly-t06-behavior，base 5f910b52c69d86a1076b2032e5d3c63e715947f3。开始时全文公共指令SHA9717f699…9880匹配，指南SHA仍db1fb184…9786；后续权限政策追加另行接收，不改写这份历史输入。

1. **P2：展开后的身份未经 IRI 验证，能投影非法 RDF。** baseline_adapter.py 原146/493–518行，_entity 模板跳过IRI，展开通知ID仅_text，subject未复验。用单测model把behavior id改bad id，notify ID N:{eventId}:{behaviorId}，adapt→prepare→plan→project成功却输出subject urn:test:baseline:N:E1:bad id的两条事实；create模板subject同类。不是九例已经失配，属于严格边界负例。建议投影前校验全部展开subject/predicate、通知ID/事件/生成类型IRI并加负例。
2. **P2：create.initial 动态解析漏 initial_index。** planner.py 原597行list comprehension内_resolve，initial[1].value={event_field:missing}时报missing_event_field，证据只有intent_validation/event/behavior/action_index，没有initial_index。无部分候选或输入修改；需逐字段_explain(initial_index)并精确错误断言。

其余全范围核对：历史常量创建、Diff/冲突证据、事件源位置未回归；冻结/四层排序/跨实例任意单值竞争/同值保留/隔离/消费正确。create.initial按一个源动作，所有单值初始化参与竞争，501通过/1001拒绝。Boolean与类型/引用负例、manifest所有hash/root边界/同字节解析正常。无导入未批准Python；安全异常文本和私有evidence边界清楚；失败未返回candidate/consumption，discarded未记正式执行。

独立实际：116行为pytest通过，9个Python ruff/check格式通过，固定manifest九例probe完整facts/orders/notifications/actions/consumption通过，临时原件 /tmp/T06-567ab48-independent-review-probe.json。人工gold/not-executed/formal_acceptance=false仍保留。

未验证真实推理/RDF通用适配、Store事务/回滚/取消、资源、Agent/UI、完整B、指定双审、打包/CI/合并/生产；全仓新检查由开发线另提供。未写源码/其他树、未推送/GUI/付费。结束HEAD未变，另有开发线生成的未跟踪流程证据t09-probe-567ab48.json。

开发处置：全部RDF投影subject/predicate和展开通知/事件/类型IRI复验；initial逐字段解析附索引；新增四个非法展开subject、一项关联事件、一项动态初始字段失败完整证据负例。修后122项行为测试通过，原不通过结论保留，等待新候选完整复核。
