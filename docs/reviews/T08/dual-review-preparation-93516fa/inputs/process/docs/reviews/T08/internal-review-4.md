# 固定候选9641446独立复核

独立agent：`/root/t08_internal_review`；固定SHA `9641446a6c53c02d95b069a29235c92d956254eb`。

原始结论：**暂不通过**。原跨用户轮次阻断已关闭，4文件58项定向通过，历史reasoning/tool关联、usedCalls和预算保留。

新增P2：公开state仅提供最终answer，工具分支完成后answer=null；后续providerFailed(TIMED_OUT)仍answer=null，已生成草稿/已完成工具收据不可取。独立agent从固定SHA复现ontology_propose完整draft已返回，但公开状态中无草稿。三工具批次取消还可能导致executeCalls整批reject，隐藏已完成的前项。

修复：AgentSession新增宿主只读克隆currentTurnReceipts()，conversation.state始终提供localReceipts和原始inputContext，与最终answer分开；fail/cancel不擦除既有收据。新用户问题仍仅清本轮记录，历史协议与防重放/预算保留；实际UI保存草稿和项目版本仍由获批T01/页面服务负责。

新增反例：工具完成后最终模型失败、下一请求预算耗尽、完整草稿后模型失败、三工具批次前项成功/中项取消/后项未执行；快照克隆不可反写会话。开发定向61项通过。新固定候选的独立复核另存，原不通过结论保留。
