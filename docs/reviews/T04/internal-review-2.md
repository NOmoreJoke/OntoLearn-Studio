# T04 独立内审 2

agent `/root/t04_private_review`，固定 head `1cd155518da58d081b35f30d3abf505c059f7ff8`，base `5f910b52c69d86a1076b2032e5d3c63e715947f3`。只读、无窗口定向复核；未写文件或重复全套。

实际终态：**暂不通过，剩余 1 项 P2**。

- R1-01 部分关闭：已保存查询载入后 ID 保留，同名可区分；但 onSaveDraft 的 Promise<void> 不返回新定义身份。首次新建保存成功后 selected ID 仍 null，再次保存继续请求新建。建议接收 T01 真实保存返回 ID，在同项目实例/请求/选中身份仍匹配时接纳；保留期间新增编辑的未保存提示。
- R1-02 已关闭：queryJob 复用批准校验并限定同项目 query.execute；其他能力无取消入口。旧结果不同 job 标为此前，失败用受限模板。
- 其余变更未发现新阻断、越权共享修改或假执行/第二存储。真实执行/Store/平台/父验收/指定双外审仍保留。

## 开发线处置

onSaveDraft 返回真实 definitionId 字符串，经严格私有 ID schema 检查；更新已有定义时返回 ID 必须一致。只在同 request token、同 document generation 时绑定返回 ID；载入另一查询、新建和卸载都推进 generation。普通编辑不改变文档选中身份，但编辑 revision 变化使完成提示继续指出新草稿未保存。未自行分配、猜测或以同名映射 ID。

修复待新固定 SHA 独立复核，未自行改判通过。
