# T03 独立内审

审查 agent：`/root/t03_service_review`。只读检查指定工作树私有服务、真实测试、renderer mapping 页面及交接；未改文件、启动 GUI 或消费未批准候选。此报告为开发聊天据该 agent 实际原文整理；不替代指定 ZCode/MiniMax 外审。

## 已发现并复核关闭

| 问题 | 实际修复与回归 |
| --- | --- |
| 合法 XLSX 稀疏尾空格及中间空行误报 ROW_WIDTH | 按标题宽度补空、保留物理行；稀疏测试通过 |
| 公式已缓存空字符串误报无缓存 | 检查选中 sheet 原始 OOXML 中 t=str 和显式空 v；不执行公式；空缓存与缺缓存分别测试 |
| 复合引用错误未定位实际空字段 | 按 reference_columns 每个字段检查，报告实际列与字段 |
| CSV 非法编码用逗号/换行简单计数，忽略引号 | 按引号、转义、CRLF 和多行记录状态定位起始源行/字段 |
| 同文件换 sheet 后迟到旧预览可接受 | 预览绑定 selectionId/sheet/encoding/local generation；改草稿、选源、取消递增代次 |

内审复核实际运行：真实候选依赖解析测试 40 passed；私有页面状态 8 passed；CSV/XLSX 探针核对精确四事实和字符串 001；React SSR 恶意样本转义检查通过。发现 UI 问题后首次回归有 3 failed/5 passed，修正比较条件后 8 passed；保留 `ui-state-after-review.txt` 与 `ui-state-final.txt`。

最终 agent 明确结论：**本轮只读内审通过，已发现的 5 项问题全部关闭；未发现新的明确阻断。** 服务、页面、测试和交接在该结论范围内。

## 未验边界

正式 T00 bridge/公共契约/App、T01 真实应用服务确认/取消/提交对账、T02 定义语义、正式依赖与包内双平台、迁移、指定双新外审、CI 及远端门禁未验。正式接线必须在请求发起时捕获代次，取消时失效，不能在响应到达时用新代次包装旧结果。候选 PyInstaller 验证不等于正式产品包。
