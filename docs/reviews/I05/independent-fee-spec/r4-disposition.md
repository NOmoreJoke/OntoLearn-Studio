# R3 Fail 的 R4 候选回应（待独立delta审查）

revisionBase=6bb1c1e5a4250468f894033e42864d480ccdb815。正式R3报告12799B/SHA521dc9104bcb3571973d91427465912ac7ea715a3a61868bade1a991724f6524、新adversarial3314201B/SHA34ac5fac52c20e43aa544798874c36fa0f1307e0e87e32116eb04925f62e6142均已读。全部旧源、manifest、数学/golden、Fail及root封存保持，旧proof/隔离材料只opaque保护，不执行旧collector。

| 发现                                                 | 本候选具体回应                                                                                                                                                                                       | 完整入口证据                                                                                                                                                               |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R3-F1 P1 metadata未整次先验验证，坏ID再从receipt逸出 | E00位于bind和任何sort/allocation前，完整类型/UTF8/唯一性/外层RuleSpec元数据门；receipt和预测child只消费已验证字段。拒绝保原JSON pointer、绑定未完成，无child/dummy/17L；走真实H01/paidPrefix/cleanup | 非stringID=7、另一外层input=7、根[]、后项坏ID、duplicate、坏规则/disabled容器、坏revision、非法Unicode、byte+1完整invoice；合法空字符串与byte恰界仍可成功                  |
| R3-F2 P2 rdf:type when/head类位置Variable错误成功    | head在已有静态Catalog收费动作、when补固定类型门与完整classes扫描，均要求固定、kindIRI且已声明类TermInput；不以binding替代语言位置                                                                    | head三模式compile:head拒绝、when三模式compile:when拒绝，另未声明/literal拒绝与固定when正例；固定class+Variable subject、合法property Variable object完整成功且独立集合核对 |
| 原R2六例与source occurrence、完整预算/cleanup边界    | 不修改原输入或严格执行器；新E00前缀加在原错误发生点之前                                                                                                                                              | 原六错误类型与更早resource保持，alias一共享对象vsJSON六份整invoice相同；不重跑无改动numeric/Q6、旧小Ledger或旧collector                                                    |

新增正常费用分别来自E00完整元数据门和when类位置门（含实际R16-child重编译）：baseline+567work/+271scan/+39事件；114的E00总+53265work/+25379scan/+3928事件；when总+30699work/+30501scan/+657事件。每ID完整依据另存metadata-delta-r4.json并与R3逐域、cap、峰和首错交叉。F2修正不增加合法head原单价，新增when检查逐发生点完整计价；所有原cap保持，当前产品不因此被声明已遵守。

实际focused6方法、27完整入口程序、114生成、141两seed、独立无reference import的双tape/IFR3/fee-codec/每ID差表审计通过。四个实际exit1（locator状态、长度字面、raw IRI、R16重复compile审计）和一次查询exit2在修订记录保留；最终固定refs、manifest和current=Git=SHA由后续process receipt列真实值，不预填未来hash。

审查入口：[R4规范](../../../iterations/I05/independent-fee-spec/specification-r4.md)、[独立手算](../../../iterations/I05/independent-fee-spec/hand-examples-r4.md)、[交接](../../../iterations/I05/independent-fee-spec/handoff-r4.md)。当前source/codec、真实同issue17L/capture/issuer/usage、owner/调用许可继续分栏pending；不自认全部发现闭合。

when/head同受integration:59+64约束，是原已采用条款的完成；不作用普通输入RDF图，不改legacy。根确认解释前的R4中间成功/source与差表已另存raw，不能外推到最终完整语言门。
