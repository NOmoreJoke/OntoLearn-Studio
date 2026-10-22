# 2026-10-22 用户决定：SQLite保护与SHACL date

本文件记录本轮用户对两项待决问题的实际回复。只更新设计和调度，不追认实现、运行或发布通过。

## SQLite：保留损坏输入保护，维持HOLD

用户原答复：“保留损坏输入保护，维持 HOLD”。原问题对应T01-controller-physical-resource-contract-options-review.md。

继续保留损坏/畸形数据库的物理资源保护要求；不采用A的受控、物理良构输入域缩减，也未选择或授权B/C施工。T01已有WIP、固定cap、真实owner生命周期及whole-worker对象上界要求不变。原Store/profile启用、迁移/重开和新child准入继续HOLD。此决定关闭输入域选择问题，不关闭技术缺口；原T01 blocked状态可继续保持，不创建替代Goal。

此前平台拒绝的SQLite/heap资源接口分析保持停止，不能以本次答复重试、改入口或改述后续做。其他独立工作继续。

## SHACL date：采用推荐的有限UTC扩展

用户原答复：“按你的推荐设置来，将选择结论更新在设计方案中”。所答问题明确列出有限UTC扩展与严格core方案；本次采用推荐的有限UTC扩展，不采用相等date也违规的严格core分支。已采用Q6规则与规范pin保持不变，本决定只补SHACL消费者政策。

- 仅接受精确xsd:date的合法`YYYY-MM-DDZ`，年份0001–9999；按公历校验真实月日与闰年。
- 不推测时区、不转换其他offset为Z；无时区、`+00:00`、其他offset、超年域、非法词法或不兼容混合类型明确拒绝，不静默fallback、改写词法或输出。
- 在inclusive范围约束中，相等日期通过；越界产生真实普通范围违规。已有exclusive约束仍按严格边界，相等不满足，不将“相等通过”误用于exclusive。
- 应作为显式、独立版本的范围政策接入现有SHACL组件入口，调用者需明确选择；旧strict/legacy入口和全局语义版本不因文档决定改变。不把规则comparator直接移作query/SHACL语义，也不全局monkeypatch库。
- 新设计须列明适用约束、target/value与bound检查阶段、固定错误、完整报告与原词法保留、政策身份和预算/失败边界；原非法整数显式入口及其已收件证据保留。

原I05负责把这一决定落实到本功能的设计附录，列最小writer及必要正反验收后交回；T05收到政策后不自行消费未固定供方或改旧golden/历史pending。新的真实报告、consumer联验及原指定双外审、CI、平台、正式执行链和合并门禁继续按实际证据关闭。
