# 独立收费规范候选入口

先读[规范及现行/提案边界](specification.md)，再读[五operation逐动作delta](operation-schedule.md)、[逐ID表](per-id.md)和[完整手算账](hand-examples.md)。可计算载体为fee-contract.json、bound-formulas.json、per-id.json；invoice_model.py只做外部纯数学，19个手列向量由test_invoice_model.py的8个methods验证。后继见[handoff](handoff.md)。

review同名前缀保固定输入manifest、16组精确原行/片段SHA、最终实际命令argv/双流/exit、作者修订和首失败转录。author-v1-input-exposure仅为root保全的not-independent历史，不能作为本新规范依据；manifest只收bytes/hash，不读内容。所有原始固定输入副本未经formatter改写。

交付边界：113项完整17L预测+1项canonical默认的条件预测、18格独立整数真值、完整114输入/外部业务expected的独立字段域均可消费；完整现行114收费invoice/真实同次发点权威仍pending。不能由本候选宣称417 oracle/产品/预算运行通过，或把任意RESOURCE_LIMIT当合法预期。
