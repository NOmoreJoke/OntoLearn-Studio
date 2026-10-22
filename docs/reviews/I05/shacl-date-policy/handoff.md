# SHACL date 设计交回

2026-10-22。本轮完成用户已采有限 UTC date 政策的设计更新，施工基线为 `7f99e9c62bed85b6fa38a8efb6be44ce3f1fba81`。本次只新增设计及本目录过程文档；旧产品、测试、设计、消费者输入/goldens 和历史证据保持原字节。

具体设计见 [shacl-date-policy-design.md](../../../iterations/I05/shacl-date-policy-design.md)，独立静态审查见 [independent-review.md](independent-review.md)，固定身份和文档验证见 [manifest.json](manifest.json)。独审提出的预算与错误次序问题已通过稳定遍历、明确计费和先付规则修订；审查报告保留原发现及复核依据。

设计复用 `validate_shacl_text` 的显式双政策入口，拟新增 `utc-date-range-v1` / `i05-shacl-text-2`；仅扩 minInclusive/maxInclusive。精确 `xsd:date`、ASCII `YYYY-MM-DDZ`、0001–9999 真实公历域，双侧检查，不转换 offset 或词法。相等 inclusive 通过，超界须来自真实 Validator 报告；当前 exclusive 仍不开放。旧 legacy / 整数入口 / 全局语义及规则政策不变。

本轮只做静态源码核对、独立设计审查、指定新增文档格式和 Git 范围检查。未导入或探测库，未跑产品测试或真实 Validator。新增 date 产品能力、实际边界与报告、预算反例、T05 消费者联验、正式执行链及原双外审/CI/平台/合并门均待另授实施和实际证据，不能从本设计推定通过。

SQLite 保留损坏输入保护并维持 HOLD；此前拒绝的 SQLite/heap 分析保持停止。Whole-worker/H 和未授 object envelope 状态不变。本交回不创建或修改 Goal，不要求用户重选 date/Q6，也不授权产品施工。
