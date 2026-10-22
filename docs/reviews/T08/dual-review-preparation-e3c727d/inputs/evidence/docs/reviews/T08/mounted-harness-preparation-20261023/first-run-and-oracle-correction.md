# 首跑真实失败与oracle纠正

44f134615a8898f56b51e77eccfc4067ae2806f3的mounted-01：真实Chrome155.0.8059.85，5组通过、第6组失败，实际exit1；28源码前后相同，pageErrors/requests均空。原raw/metadata/result及浏览器profile保留，不覆盖或删除。

失败是本新增runner错误地要求取消后只有一条收据。既有7a33的tests/unit/t08-conversation.test.ts369–398原合同要求完成收据与取消失败收据都保留。3896改成完整deepEqual：query_draft原base/内容＋query1固定failure/CANCELLED，不只把数量改2。独审确认与既有契约一致，未发现产品缺陷或改变原取消语义。

3896的mounted-02六组实际exit0，但随后独审发现busy掩盖Diff的覆盖假阳性，故其成功不冒充最终完整覆盖。8d9补非busy正对照与旧上下文警告/禁用，e3补依赖/输出realpath边界；最终另跑mounted-03，所有旧字节及失败均保留。真实I04持久job/ACK、T04 QueryPage、provider/业务执行仍未接线。
