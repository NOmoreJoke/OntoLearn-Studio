# T05 两规则图与13C：测试及反例证据受限收件

2026-10-22。总控全文读取主文9864B、作者独审2390B及根独立审查18588B（SHA256 `70cc2b68f1c3eecd9a2dee2ba9767a043e31fddfb47be29494bfee20c5633406`），受限接收本轮测试实现与实际观察，不接收产品全绿或父M1完成。

固定树 `.worktrees/T05-profile-M1-graph-consumers`；base `5f910b52c69d86a1076b2032e5d3c63e715947f3`，adoption `8fccf64c99e42e03003f90d799a58db8ecc97df6`，测试提交 `2ce39f011282b6fdce5e6870610529cff1458fdd`，纯过程提交 `4b8bc6bedcd1d1726259b322c6f6f77b529d16ea`。143原只读输入未变，只有fixture和test两项新增；过程201项（manifest200+self）闭包实核，工作区干净。

15实际观察为9项规范相符、4项产品入口差异、2项pending。最终正常检查实际exit1：1125项前端通过；Python4899通过、4失败、44既有跳过。四红为langString、inclusive-nni、dateTime-equal、dateTime-before；已交原I05修复。date-entry与illtyped-entry尚未完成政策及规范报告验收。另三direct图未运行，不计skip/xfail或通过。

两规则图真实经过prepare、production和完整restore；成功保全when/bindings、typed values、三次head occurrence到两条RDF结果及原C/R/L，false→error保实际比较顺序、完整诊断和无成功结果。13C保真实query或SHACL入口阶段；5份真实SHACL RDF报告与API及独立golden逐字段相符。两项测试断言P2已按实际补丁和同版原件关闭。

最终ZIP1307902B、SHA256 `06eb119efb8e6ec44b903723c1a4f7d6f3fc25d657b9f14b5f0b35ec51321124`，79成员/15观察；全部8份历史ZIP成员、原始命令和首失败保留并校验。两规则实际fee事件合计978709（成功737537、失败241172），条数不冒充预算用量。

本树继续冻结。等待总控完整核验I05 shape修复后，另给精确单路径采用及新组合验证窗口；不得自行消费尚未接收的候选，或改golden取得绿。directSteps仍等原owner真实carrier。此收件不替代正式Job/Store/worker集成、父验收、指定同版双外审、CI、目标系统/真人、推送和develop合并。
