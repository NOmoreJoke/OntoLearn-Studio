# 方案审查意见处置

初版固定 `64bbfe27a2191e65e8e81ab34862b9867e46a034` 的完整独立审查不通过报告保留在 `independent-review-initial.md`；不改成通过。

| 意见 | 修订 | 状态 |
| --- | --- | --- |
| P2-1 供应证明未贯穿确认/Job提交 | 主方案§4新增S2原持久envelope/sourceBinding与版本化previewHash、planRef/原receipt绑定；明确T01 domain_changesets/job_store准确扩展、确认/接收/commit各自原事务重读复验、同revision漂移与历史/当前proof区别；§6/8/9同步 | 固定4406103独立复核关闭（仅方案层） |
| P2-2 累计预算无执行前接点 | 主方案§4首步改为预扣先于旧bind/change_preview；§7新增逐固定调用图cost profile、所有旧解析/副本/plan/blob/历史/页/失败计费与有限尝试；无法保守预扣时须先root批准meter精确扩展，不事后补计、不猴补；S2与测试矩阵同步 | 固定4406103独立复核关闭（仅方案层） |

以上均为方案修改，没有实施来源绑定或meter，也没有运行产品。T01供方合同及root精确实施/采用授权仍待，原Goal继续blocked。

完整修订方案 `4406103ac309b21ddabb5f99b3efd11265acb64f` 已由同一独立agent全文复核通过，无新阻断；原报告见 `independent-review-final.md`。主方案SHA `6b88b1f7a8e9b7b08719f6b48dda16905a3eb800a7b8baef21f4b7a26b06983c`。方案后只追加过程证据，不把内审等同采用、实施或运行授权。
