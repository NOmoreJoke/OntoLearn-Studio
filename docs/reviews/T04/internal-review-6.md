# T04 读取适配修复候选复核

agent `/root/t04_private_review`；固定 head `f68d3c5560516d8401ace55b7d3736242eea903a`，base 仍 `5f910b52c69d86a1076b2032e5d3c63e715947f3`。

实际终态：**暂不通过；原 3 项 P2/1 项 P3 已关闭，另有 1 项 P2 错误分类缺口。**

原项独立纯内存探针 7 项通过：ACK 后重读完整防重复、跨空页倒退拒绝/前进接受、ACK 下限覆盖刷新/通知/取消前查、实际执行原文保留、同版本矛盾拒绝、终态不重开。仍仅一页载荷及两字段锚点，无新公共 IPC/Store/执行器。

新 P2：固定 reader.ts:57 的 invalid() 使用 params={}；批准 INVALID_REQUEST 必需枚举 params.field。独立 safeError 调用确认降为 INTERNAL_ERROR/engine.internal，参数/身份/分页拒绝失去正确原因。须使用批准字段分类并断言返回错误码。审查者看见工作区补丁，但未算入固定 SHA 结论。

未写文件/运行 GUI/全套。真实 IPC/I05/Store/App/平台/父验收/指定双外审和 CI 仍待验。

## 开发线处置（待新固定候选独立确认）

invalid(field) 仅取批准 identity/params/cursor 枚举，safeError 使用完整 params.field；元数据和分页校验失败明确分到 identity/cursor，原始 bridge 异常仍固定 INTERNAL_ERROR。定向测试新增错误码及参数断言；首次断言暴露元数据抛错被外层归为 internal 的缺口，已分类修复，失败原件 reader-vitest-error-shape.log 保留。最终 24 项读取测试通过，不自行改判内审通过。
