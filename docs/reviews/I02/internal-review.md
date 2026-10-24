# I02 内部独立只读审查记录

独立审查 agent：/root/i02_internal_review。记录者：I02 开发会话，根据其两次实际返回消息整理；不是指定 ZCode/MiniMax 的报告，不替代第三方门禁。

检查范围：仓库 AGENTS、冻结 I02/C1、PRD 对应安全与恢复条款，CSP 配置/Vite 注入/main 窗口/来源检查/security/recovery、相关测试与 design。只读，不修改文件，不操作 Git/桌面，不运行会改 out/release 的命令。

首次结论：当前唯一应用窗口/health 范围无阻断性安全或恢复缺陷。两项非阻断建议均采纳：

1. 区分 preferences 工厂与全 contents 导航加固；新窗口测试复制 preferences，不能声称事件 hook 会修正任意不安全构造器。design 明确分开工厂、app sandbox、session 权限与 contents 行为限制。
2. 补充恢复选择的延迟竞态。新增 6 项逻辑测试覆盖 responsive/close/quit/decline、hang→crash 合并、manual reload；同时 did-finish-load 清除旧 gone/responsive 状态，避免旧提示重建已健康窗口。

增量复核：两项可关闭，无新阻断；未新增引擎调用或任务重放。新增测试是 EventEmitter/dialog stub 的逻辑验证，与原生 executable 的真实崩溃/挂起矩阵分别记录。

证据边界：只读独立代码审查；测试实际执行结果由开发会话的 evidence/check.txt 和各运行矩阵提供。指定第三方双审尚须另行新任务同版完成。

## Native 驱动增量复核

真实 packaged executable 忽略任意 --require；现统一采用短暂 main inspector 注入、故障前 inspector.close，渲染进程不附加 CDP。独立 agent 核对真实性后发现 bootstrap socket 等待在退出/无响应时可能不结束。该项采纳修复：三段等待与 child 结束/45 秒 reject deadline 竞速、socket close 拒绝、finally 清理。新增两项模拟测试验证永不回复时有界退出+kill+close和启动失败立即拒绝；e2e 显式断言 inspector 已关闭、模式一致与 killed/unresponsive。

独立增量复核结论：该问题可关闭，无新阻断；仅只读，不运行桌面/写文件。该审查仍不替代实际矩阵和两指定模型。
