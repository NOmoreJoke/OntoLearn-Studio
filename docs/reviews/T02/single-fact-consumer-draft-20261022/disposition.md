# 单事实消费草案：独立审查处置

初版固定 `db77a347a826b7b50d6ef88c5e894c365d63eefe` 独立完整审查不通过，原件 `independent-review-initial.md` 保留。仅为draft方案错误，未运行产品，不是C5产品或S1双审失效。

| 项 | 初版问题与具体反例 | 实际修订／状态 |
| --- | --- | --- |
| P2-1 domain/range被误当值校验 | 输入行含range适配判据，F11要求声明range不容newO则拒绝；但PRD688/970明确RDFS推理非数据校验，C5只校词项/支持datatype/ill_typed与property/literal形态 | 删除额外range比较；输入只保domain/range声明，F11限实际词项/编码/支持域，并补“不仅因range=xsd:string而canonical integer literal不同就拒绝”的语义护栏。PRD V0.6/1255行/93584B/SHA7586b2c4784b8c691d510e2be16310ed551e110af6df96b7c6aeb86152f60fbb按批准5f固定Git核同，读取版本和688/970相关行。待固定修订独立复核；不预定SHACL校验合同 |
| 文字精度：重复页与合法重试 | F15/R5原“重复页”可能误禁受控同页重取 | 已在固定e976835a8a9c40cf86a07e6d5ad1cc6421a95b83修为组装确认材料重复拼段；合法重取按实际T01合同并同会话计费，不新定cursor协议；独审已核该两行，歧义关闭 |

其它范围沿初审完整审读；新PRD精确输入只作本次语义修订依据，不重跑34/130/825或产品。实际新供方、采用/实施、模型轮与父验收仍待；原十件/C5/Goal不变。
