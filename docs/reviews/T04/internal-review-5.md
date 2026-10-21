# T04 客户端读取适配内审

agent `/root/t04_private_review`；固定 base `5f910b52c69d86a1076b2032e5d3c63e715947f3` → head `c3f771b1dbdbee18d53f629bd8c7dd79985b8883`，完整本线范围及新增 7 文件差异。只读、无窗口独立 bridge 探针，未写文件/重复全套。

实际终态：**不通过：3 项 P2、1 项 P3。**

1. P2 reader.ts:359/364：return refreshJob 的 finally 提前释放 cancelBusy。ACK 后任务重读悬空时再取消，独立实测 cancelCalls=2、secondAccepted=true。须等待重读完成。
2. P2 reader.ts:197：从当前空页取 at(-1) 丢排序锚点，ordinal 10 → 空页 → 5 被接受。须保留最后非空行的有界锚点。
3. P2 reader.ts:270/359：ACK 版本 5，首次 getJob 版本 4 被拒后，普通 refreshJob 默认下限 0 又接受 4 并清错误。须跨刷新/通知/取消前查询保留当前 job ACK 版本下限。
4. P3 reader.ts:34：executedSparql.trim 改变实际来源原文；只校验非空，保留原字符串。

此前查询保存身份/任务能力隔离继续有效；未发现新 IPC、Store 或假执行器。真实 presentation 来源、I05 执行、Store、App、平台/父验收/指定外审与 CI 仍待批准依赖，不能由合成探针替代。

## 开发线处置（待独立复核，未自改通过）

- R5-01：`return await refreshJob`，防重复保护覆盖 ACK 后重读完整生命周期；新增延迟该阶段的重复请求反例。
- R5-02：只保存最后非空行 ordinal/rowId 两字段，空页保留，新结果/绑定/释放清理；新增倒退与前进两变体。
- R5-03：当前 job 版本下限记录在私有显示状态中，刷新、通知、取消前校验共用；新绑定/实际切 job 清理。新增失败后再次读/通知/取消均拒绝旧版本及达到下限后恢复样例。
- R5-04：仅 refine trim 非空，显示值保留原字节；新增前后空白完整保留与全空白拒绝。
- 另自行补齐同版本状态矛盾/已观察终态重开拒绝、同绑定 restored 仅更新原选中 job 的边界；不使用相邻转换约束去拒绝合法跳跃观测，不新增公共状态机。

修复版客户端定向测试共 24 项；实际终态及新候选内审另记。完整 check 按真实产品改动重新执行，不把旧 c4/c3 通过冒充新候选通过。
