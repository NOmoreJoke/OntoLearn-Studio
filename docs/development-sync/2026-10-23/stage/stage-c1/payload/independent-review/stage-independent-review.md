# 阶段验收包独立审查

2026-10-22，北京时间。审查者：独立 agent `/root/background_entry`。只读产品与构建产物；未修改业务组件、验收外壳或原生应用；没有启动 Electron、可见浏览器或原生 GUI，没有运行任何指定模型任务。

## 当前结论

**限定 Pass：可作为本轮离线组件交互与已批准基础引擎的人工阶段验收包交付。** 首个浏览器候选发现的 P2 窄屏裁剪已修复并真实复验，三项 P2 全部关闭，未发现本次范围内仍需阻止交付的 P1/P2。最终浏览器 SHA-256 为 `adff7f408e1844392d550a7e0a3bdacb5e1c1cd167b24d3b236a517456033a81`。此结论不替代指定模型双审，不证明业务集成、原生 GUI 或发布通过。下文保留原发现与复验边界。

## 真实发现与处置

1. **P2：390px 学习工作台被裁剪。** 在真正 headless Chrome、`file://` 入口、390×1000 窗口进入离线学习：`document.scrollWidth=390`，但 `.stage-surface.scrollWidth=1424`，`.learning-grid > .learning-path/.learning-task/.learning-reference` 的 rect 均宽 1398、left 41、right 1439。主表面 `overflow:hidden` 把内容裁掉，不能用页面无横向滚动作为布局通过证据。外壳 mobile `grid-template-columns:1fr` 覆盖原组件的 `minmax(0,1fr)`。已通知作者仅修验收 CSS，保留固定源码。
2. **P2：重置提示与实际行为不符，已关闭。** 初读顶部写重置后验收勾选丢失，实际重置只清当前组件草稿。作者改为切换/重置清当前草稿，刷新/关闭清全部记录；冻结候选已实测重置草稿为空且先前“符合预期”勾选和反馈文字保留。
3. **P2：总指南笼统声称无回调按钮全禁用，已关闭。** 离线学习“检查我的操作”可点击，但正确提示“此任务的检查暂不可用，可先查看离线提示”，进度仍为 0。根 README 已精确区分主要执行/保存禁用与课程检查提示，不要求篡改固定组件。

## 已实际核验

- 34 个 snapshot 文件分别逐字比较对应 Git commit/blob，字节数与 SHA-256 均匹配；没有将活动工作树文件冒作固定版本。
- 浏览器离线进入页面，实际搜索“传感器”得到两项；可切类树/局部图，编辑/重置表单；预览禁用。
- 查询选择 Sensor/温度，完整 SPARQL 与独立预期逐字一致；执行、保存均禁用，无模拟结果。
- 行为可编辑名称、添加和移除条件/动作；隔离试跑禁用，无伪造运行结果。
- 学习可切换到任务 02/数据映射、选择 SPARQL 术语、展开技术定义。检查不可用不产生完成，进度保持 0/9。
- 真正触发并读取两个下载：验收 JSON 含先前勾选和 `独审下载验证` 文字；合成样例 JSON 标记 `synthetic=true`、六个对象。没有仅检查下载按钮存在。
- `console error` 0 条；网络记录没有外部请求，只有本地 file 入口。
- 原生 manifest 的九份交付文件哈希、429 个包内实文件/14 个符号链接及权限、固定 5f 的两份锁与工作树逐字匹配；工作树仅保护 AGENTS 未暂存变化。包内独立名称/appId 与 Info.plist 一致；ASAR 的五份编译产物与 parity 清单匹配。
- 直接全文审阅包内探针脚本及结果：真实内置引擎 hello、同 session 十次 health、18 triples 的完整固定查询结果、引擎及 storage 探针 exit0；首个 wrapper 错误 exit2 留存且说明未改产品。此次独审不重复没有新变化的原生探针。
- 未签名/未公证、未测实际 userData 运行路径、未启动 GUI、未做跨模块业务/Windows/干净设备验收等边界在指南与 verification 中准确披露。
- 启动 `.command` 静态仅根据自身目录打开本地 index；独审未执行 `open`。后台入口报告仅列已安装契约和待运行路径，没有声称双审已启动；`persistAsWorkspaceLastUsed` schema/handler 差异已披露。

## 工具边界

首次 Playwright CLI 导航被其默认 file 协议策略阻止，页面未加载；这是工具入口限制。使用 CLI 文档支持的 `PLAYWRIGHT_MCP_ALLOW_UNRESTRICTED_FILE_ACCESS=1` 在自有新 headless session 重新进入真实 file 页面，没有 HTTP 服务、CSP 绕过或产品改动。真正布局失败单独保留，不将该工具限制当产品缺陷。


## 最终修复复验与身份

P2 窄屏裁剪已关闭：只改验收外壳 CSS 的 grid 轨道为 `minmax(0,1fr)` 并给直接子项 `min-width:0`，34 个固定 snapshot 未改。新最终候选已在独立 headless Chrome 重新从 file 页面加载；390×1000 下 surface clientWidth/scrollWidth 均为 360，learning grid 及 path/task/reference 均宽 308、right 349；四提示按钮最大 right 332、术语下拉框 right 328。路径内部 ol 宽 308、scrollWidth 1398 且 overflow-x:auto，保留正常有界横滑，没有把整个页面裁掉。任务02切换、SPARQL术语选择与技术定义展开通过，console 0 error/0 warning。还查看了作者修后完整390截图，主卡、提示、术语及反馈入口均可读。

只复测实际受 CSS 改动影响的学习窄屏与新 bundle 加载。此前对同 JS/源组件的四模块真实交互、两个 JSON 下载、1440四模块、390其余三模块结果仍限定引用，没有无变化重复整套测试。

最终 `stage-delivery.json` 的七个固定交付文件字节数/SHA-256 逐项匹配；根指南修正文案也相符。独立浏览器 session 已关闭。正式机器可读身份与范围为 `stage-review-proof.json`；该 proof 不包含动态双审任务状态，以免误把协调回执当成通过。
