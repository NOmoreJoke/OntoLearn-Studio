# 真实原生提示补证据（2026-10-20）

对应受审候选 `2cc03da82ffccc8448c7b03dc6cff87595027653`，base `1b6df7a220fc9a67d7046133a340085f03f0a96c`。本目录仅追加运行过程证据；未改实现、测试、配置、依赖或验收标准。保留 Round 1 两报告原文与原结论。

## 证据勘误（适用于既有 design/acceptance/矩阵中的 native 提示描述）

`docs/iterations/I02/design.md` “自动化仅替代原生对话框的用户选择”不准确：两处自动化整体 stub `dialog.showMessageBox`。因此既有自动化矩阵证明的是提示请求/文案/选项和选择分支、真实故障事件与重建/health，**不单独证明原生 sheet 渲染或按钮可达**。`acceptance.md` 的“两次 native 提示”应在上述边界内理解。此处纠正证据解释，没有缩小原提示与恢复验收；以下补上未替换 API 的真实运行证据。既有文档与自动化文件保留受审字节，避免把修改验收混入流程证据。

## Run 2：真实 packaged / 同一进程连续挂起与崩溃

- `launch.json` / `driver.log`：实际 app.asar executable、独立临时 profile，主进程 PID 64273，`app.isPackaged=true`。瞬时 MAIN inspector 仅注入故障/只读事件观察，随后关闭；renderer 无 CDP，hang monitor 启用。`bootstrap-payload.txt` 保留完整注入内容；只保存/比较 `showMessageBox` 原引用，**从未替换该 API**。
- 初始真实 UI 手动点击连接检查成功：`01-health.*`。
- 00:06:57Z 请求 hang，00:07:13Z 真实 `unresponsive`；`02-hang-prompt.*` 原子 AX+截图直接显示原生警告 sheet 和两个按钮。通过 CUA 点击当前 AX 的“重新打开窗口”，窗口 2 创建后窗口 1 关闭，`03-hang-reopened.*` 显示“尚未检查”；再次真实手动检查成功见 `04-hang-manual-health.*`。
- 00:08:39Z 对窗口 2 真实 `forcefullyCrashRenderer` → `killed`；`05-crash-observation.*` 显示真正崩溃 sheet。CUA 点击“重新打开窗口”，窗口 3 创建后窗口 2 关闭，`06-crash-reopened.*` 为“尚未检查”；真实手动 health 成功见 `07-crash-manual-health.*`。
- 00:08:58Z 再对窗口 3 crash；`08-decline-prompt.*` 显示真实提示，点击“暂不恢复”后 `09-declined.*` 保留空故障窗口。events 至退出始终仅 3 个窗口，无第 4 窗/自动恢复；00:09:07Z 显式 quit，before-quit → closed(3) → will-quit，driver `childExit:0`。观察结束后没有调用会自动启动 app 的 CUA 读状态。
- 事件流 `events.jsonl` 对每次故障记录 `dialogUnmodified=true`；两次恢复同一子进程内完成，期间无退出/relaunch。AX “尚未检查”以及手动按钮后“本地引擎已连接 · v0.1.0 · 协议 v1”分别保存，不能把新窗口初始状态误当自动重试。

结论：本机 macOS arm64、当前真实未签名 packaged build 下，崩溃与挂起原生提示可显示，两按钮可达；显式恢复后可继续手动 health；拒绝不会自动重建。截图、AX、事件、进程日志联合使用。

## Run 1：保留异常与工具干扰，不作完整通过依据

首次 crash 的原生 sheet 曾在 CUA inline 输出可见，随后新窗口实际加载。但保存 AX/截图与使用旧元素 ID 混在同次调用，报 stale/invalid ID，落盘图已是新窗口，不能把 `03-*` 称为 sheet 图；无法确认那次点击来源。第二次 crash 未稳定观察到 sheet，不能据此判定应用通过或缺陷。退出后再次调用 CUA getAXState 导致工具重启 app，**该重启不计恢复**。保留所有原始产物，重启的自有进程随后终止。

Run 2 使用原子 AX+截图与当前元素索引消除了该操作偏差，同进程连续恢复已成功。Run 1 未能确定原因的观察保留为限制，不改写历史失败/不确定记录。

## 边界

本次不证明签名安装器、干净设备、Windows/Linux native sheet、生产部署或未来任务重连。`catch {}` 无诊断仍为非阻断建议，未模拟原生 API 任意异常，也未因本机成功宣称所有环境可靠。无源码/测试变更，无新的功能范围。

补充包身份核验：`run-2/package-identity.json` 保存实际运行包 asar/main/preload/HTML 哈希。尝试与当前 out 逐字节比较时 main 不同，不能声称当前 out 与该包来自同一次构建；实际 diff 仅一个开发 nonce 字面量，规范化该唯一值后全文相同，preload/HTML 原始字节相同。差异原文见 package-main-diff.txt，符合 M-01 记录的跨构建随机性，没有用旧 package-manifest 的 main 哈希冒充本次运行包。
