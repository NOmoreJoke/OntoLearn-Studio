# T01 → T02 最小供方交付计划

[完整计划](plan.md.raw)按现有真实依赖分段：纯字段校验、可信 owner 费用基础、完整同连接源、内部严格 canonical、M 最小持久写门与 S2 四事务 proof、T02 实际 Preview/原 Job 机制链，最后是命名产品接线。每段列明精确候选新旧路径、输入、计费/错误/闭包及健康临时库验收；当前只交设计，不发行实现、公共 API 或运行票。

计划复用真实五字段唯一 home、L1 缺失处理和精确 identifier 唯一政策；缺业务 identifier 不派生。首次源读取前须已有可信发行的同一 CostSession，失败累计；四次重取/重演位于原事务中，receipt/undo 沿原唯一 writer。旧 423、ReadLimits 或同形 JSON 不能替代新供方或物理授权。完整 M 编辑器、Turtle、T08/T10 或 M0 总完成均不是立即技术准备的统一前置。

[初稿](initial-plan.md.raw)与[首次独审不通过](independent-review-initial.md.raw)均保留。具体 P2 是内部机制所需 strict canonical 原先只列在后期产品窗；修订已把 K 明确提前为 M1/S2 的共同冻结前置，保留正式 engine/main/I06 启用后置。[最终独审](independent-review-final.md.raw)确认该 P2 关闭、设计层可接收，不代表实际实现或指定外审通过。

完整计划及两独审是其原始 /tmp 生成版本的精确字节副本，文内“只写 /tmp”记录当时生成范围；本次归档只新增当前文档 prefix，没有写入其拟议源码或改变冻结候选。实际输入身份见 [input-identities.json](input-identities.json)。本批不附旧 81538 B 主方案的重复副本，不重建其源码闭包。

C1 A/B 修复仍在自己的新工作树执行；本设计没有抢用共享 writer。后续实现由总控指定累计 base、逐路径采用和短窗口，再产生同版真实供方与必要验证。
