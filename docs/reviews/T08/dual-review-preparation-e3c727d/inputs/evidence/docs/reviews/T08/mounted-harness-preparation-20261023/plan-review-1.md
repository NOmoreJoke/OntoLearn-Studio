# 挂载方案独审1：暂不通过

来源：现有独立agent /root/t08_internal_review 最终回复，owner归档；未运行或写文件。

方案暂不通过，仅需补明确一处执行边界：codec使用Node的Buffer.byteLength，不能把AgentConversation/AgentSession直接并入普通browser IIFE。建议保留Node runner，通过专用Playwright binding/安全state快照驱动真实browser ReactDOM/Sidebar，不用Buffer/hook/DOM shim，不启动Vite server。其余范围、Query供方缺口、隔离与失败保留合理。交接索引12项匹配固定证据提交。

原初版方案未单独导出原字节文件，其完整创建工具记录保留在本聊天；不虚填初版SHA。原意见保留，纠正另记复核2。
