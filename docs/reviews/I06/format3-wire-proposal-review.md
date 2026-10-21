# 格式 3 小合同：独立静态审查

2026-10-21，独立 agent `/root/i06_design_review` 读取批准 `5f910b52`、总控最小合同及两份提案，完成只读审查；未改实现、运行产品校验器、产品测试或平台。

初稿 `6780202` 提出两项消歧，修订 `cf059e4` 已实际复核关闭：

- 全表 `normalPendingAcceptance` 改为 `preHashPendingMatch`，只含完整 shape/pair/pending/phase；N05 明确假 hash 最终 reject、连接 terminal、pending 不 resolve，不因预匹配成功得到 ready。
- checkpoint 排除范围限定 I06 私有网关配置/凭据/授权/发送 ledger，明确 T01 的 metadata/drafts/learningCurrent/assistanceAudit 覆盖仍保留。

独立复核还全文核对已生效 Python 四文件交接原文 SHA `18485767098d448a4fcce2fc7e59b5a325433826894b98111cab96926fdc2097`，与修订后的权属/隔离描述一致。根合入后按审查者已认可的精确措辞，将“八文件 ack 已登记”改成“I06 八文件释放回执已单独提交”，避免将本线提交误作总控生效登记；其余内容未变。

最终提案：

| 文件                                                      | SHA-256                                                            |
| --------------------------------------------------------- | ------------------------------------------------------------------ |
| `docs/iterations/I06/format3-wire-contract-proposal.md`   | `3b64483010f3bb17b41e2a6b9ec3c558d52e42ae051dd21f01bad869fc577ebb` |
| `docs/iterations/I06/format3-wire-fixtures-proposal.json` | `9d9936eca623cbfd654de813846b542578cd7eb1056d454273b0cdda81a12fb8` |

静态实际核对：严格 JSON 无重复键/案例 ID；28 对 wire、4 通知、6 启动分类和4兜底，实际 ready/dispatch/claim/confirmation 标记均为 false；启动码/localError/bridgeFailure 配对，相关 wire/error 编码在现有字节界限内。外2选3/双 session、三个新 null 错误、旧[2]仅终止、业务3精确绑定、同步 hash/帧限制后才 ready、registry 原始字节 hash 算法与批准源码边界一致。结构化初始化类别/prehello/current generation/首错优先及未知退出/信号安全兜底均有限，不解析 stderr，不提前声明新 runtime 能力。

无剩余文档审查意见。这不是 canonical 批准或运行通过；固定 a64 hash 仍是 schema-fixture-only，真实协议3资源、同源异常/退出表、两端实际校验、真实 Store/Job-ready、混版本/源码和包内联验必须由接收 owner 冻结并实施。八文件的总控登记与 T01 逐项接收另行完成。
