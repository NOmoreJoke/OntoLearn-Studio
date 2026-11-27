# T09 学习页面私有接线约定

唯一实现目录 `apps/desktop/src/renderer/src/learning/`，入口 `LearningWorkspace`。总控已授权此目录及 `tests/unit/learning-*.test.ts`；共享 App、样式、桥、main/preload、契约、依赖锁均未改。页面为可接入组件，尚无正式产品路由。

组件只消费静态课程与受信 owner 的 `LearningWorkspaceProps`，不持有 Node/IPC/SQLite/模型能力。这里的 TypeScript view model 是私有投影，不是批准的跨进程契约；实际桥接仍由 T00/T01 运行时严格校验并维护唯一存储权威。

## 身份与辅助归因

结果由 projectId/taskId/attemptId/inputVersion 四元组隔离；generation 或 project 改变重建页面，任务/尝试/输入切换会卸载旧任务并丢弃迟到回执。辅助来源、最高提示层级则在同 project/task/attempt 内跨输入单调保留。输入变更不能使已用示范变成独立完成。

`records` 应包含当前尝试已知的辅助历史与当前结果，且每次更新提供不可变数组。T01 必须持久维护同尝试的辅助归因，并在首次挂载/重开/跨窗口恢复时提供完整水位；renderer 的临时防降级投影不代替存储保证。新的 attemptId 必须由 owner 明确创建，不能由 UI 自动洗白。

每个完整 context 的 recordVersion 为单调非负整数；一次新检查/提示必须返回严格更新版本，等版不同内容视作冲突。更高版本也不能降低同尝试 maxHintLevel 或 assistance；冲突时不计完成，提示重新检查。仅 actual passed + 非空依据可计操作完成；独立迁移还须 independent、未用提示、实际迁移任务。

## 能力和异常

`recordHint`、`checkTask`、`exportReport` 独立按实际能力注入。真实 context 的提示必须先由 owner 保存归因并返回匹配回执，之后才展示答案。保存缺席/失败/串上下文不泄露答案。无 context 可预览课程，迁移练习各级提示均须进入真实练习并记录。纯组件合成回调只是交互测试，不能充当领域工具。

检查失败、冲突、过期、待依赖不会被转为通过；错误显示固定中文消息，不展示异常或路径。反馈文本由 React 转义，不接受 HTML。报告仅实际导出成功回执才显示成功。实际三阶段证据、T08来源、T10报告和包内资源仍按 handoff 接线。

## 无桌面验证

普通 `npm run check` 总是跑纯投影测试；浏览器套件须显式 `T09_HEADLESS_UI=1` 并提供与当前 Playwright 匹配的独立浏览器运行时。测试在 about:blank 内存构建组件，无 HTTP 服务，拦截并断言无网络请求；headless 且 chromiumSandbox=true，移除默认 disable-hang-monitor 和 mock-keychain 参数，不启动 Electron。截图开关 `T09_UI_CAPTURE=1`。

T11 后续应在隔离 CI 显式提供浏览器并启用此套件；当前未抢改共享 CI，也未将默认 skip 算浏览器通过。组件截图不代表真实 Electron/包内/平台/真人验收。
