# T06 行为 UI 子任务回执

2026-10-21，独立子任务，沿用父 T06 Goal。没有建立第二个 Goal。

- 工作树：`/Users/kyle/Documents/工作/知爻/本体/.worktrees/T06-behavior-ui`。
- 分支：`feature/T06-behavior-ui`；实际启动 HEAD/base：`5f910b52c69d86a1076b2032e5d3c63e715947f3`。
- 启动时仅受保护 AGENTS 未暂存，SHA256 `db1fb184809932a27c5bfd8c91b72837d719cdbdc07d7a83860e5cba38529786`；已全文读 AGENTS、共同指令、frontend-design、FR600–604/C/D/E.1/G.0/G.3。
- 共同指令启动 SHA256 `9717f699e14b5941e15d90269f33cbebc32ef9bec6e7439739be848753419880`；已接收第九节、无桌面全文。
- 总控授权补充后实际读回 AGENTS SHA256 `78df28251883651ea8a068a8a21daed6d6dc0f50348894d59a808b969a97a759`、共同指令 SHA256 `df09014af4d6cf757ca0977a995497f3646cd330e8921710876663a40a8cbcb4`；已读完整 external-review-permissions。该政策不改变 UI 禁止 GUI/审查应用的任务约束，不改写受审服务或重启 Goal。
- 责任仅新增 `apps/desktop/src/renderer/src/behavior/` 与 `tests/unit/t06-*.test.ts`。AGENTS 保持未暂存；没有修改共享 App、style、bridge、Store、主树、依赖锁、CI 或总控文件。

已实现可装配草稿、单组条件、四类安全动作及排序、显式事件/断言变更、缺省能力禁用、受限结果解析、完整触发原因/动作轨迹/Diff/通知及失败/取消/过期/历史展示。条件评估及排序文字遵守 E.1；没有在 UI 重做行为引擎。

实际执行：`npm ci --ignore-scripts`、`uv sync --frozen` 成功。最终 `npm run check` 完整通过：lint、格式、strict 类型、651 项 TS（本线 21 项）、桌面构建、ruff、1052 项 Python；源码为独立批准基线，没有采用 S1 引擎实现。补入单值关系追加拒绝、单值 IRI 覆盖与多值追加的明确正/负例。

Headless 已实际通过：未接入服务禁用、键盘 Tab、事件/事实变更、候选与失败/取消/历史、触发理由/完整动作文本/通知安全、刷新保留草稿及宿主回调、取消迟到完成拒绝、项目切换、1440/390 无横向溢出。已用 view_image 实际检查宽屏、手机全页与手机视口截图。所有输出均为明确标识的开发夹具，不是引擎或生产结果。

首败保留：初始 Vite 虚拟 entry 解析与缺少 Headless Shell 的工具原输出在本会话；后续嵌套 select 精确 label 定位超时有 `test-results/t06-ui-headless.log`、`t06-ui-headless-2.log` 原始日志，并实际读可访问树后修正为 role 定位。首次全 check 在开发中脚本格式未定时失败，保留 `test-results/t06-ui-check.log`。修复后的完整通过与最终通过分别保留 `t06-ui-check-2.log`、`t06-ui-check-final.log`，最终 headless 日志为 `t06-ui-headless-final.log`。均为本树忽略产物，不混入源码。精确源哈希、日志/截图哈希与验收边界见 [verification.json](./verification.json)。

下一可验交付：本地可恢复提交交父 agent 完整独立内审；抽查反馈不作为独立通过。未作指定外审、推送、PR 或合并。正式 App 接线、真实引擎/事务/Agent 联验、原生窗口和首发平台验收仍由父模块按原门禁完成。
