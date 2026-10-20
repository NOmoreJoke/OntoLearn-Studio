# I02 / C1：CSP 与窗口生命周期

本项依据已冻结 C1 及 PRD V0.6 8.7、10.3、10.4、12.5。原始工程计划、范围及完整第三方审查流程保留在 `../I01/inputs/`，当前文件只解释实现，不改写验收。不开发 v2、ExecutionJob、业务模块或模型网关。

## 策略交付选择

采用**生产仅 meta，开发 header**。单一配置 `apps/desktop/src/csp.ts` 生成两个变体。生产 Vite post-transform 在 head 首部插入 meta，早于 script/link；开发插件不运行，不插入生产 meta。生产不再注册 CSP 响应头处理器，避免平台对 file header 交付的差异及多份策略叠加维护成本。本项所有生产需要的指令均可由 meta 提供，不以 meta 声称支持仅 header 指令（如 frame-ancestors）。

比较：meta+header 可以增加 header 专用指令，但当前没有嵌入业务文档需求；旧本机 header enforce 确实有效，未登记为缺失漏洞。仅 meta 则有明确可审查的 HTML 顺序和跨 file 交付方式，且无需两次叠加求交。若未来增加 header 专用约束，重新从同源生成并实测叠加，不能手写第三套策略。

生产 script 不允许 unsafe-inline/unsafe-eval；样式使用本地 CSS；连接全拒绝（health 通过窄 bridge，而非 renderer 网络）。开发只增加固定 127.0.0.1:5173 HTTP/WebSocket、随机 nonce 与 Vite 样式 HMR 所需 unsafe-inline。未知开发 origin/非法 nonce 拒绝生成，不静默扩大来源。

style 元素和 style 属性字符串在生产被拦；CSSOM 属性赋值仍允许。这是 Chromium 现行行为，不将 React style 统一描述为被阻断。原始记录见 `inputs/csp-packaged-probe-2026-10-19.md`，它是受保护的既有资料；本项新矩阵保存在本目录 evidence。

## 窗口与来源

在创建第一个窗口前注册 app `web-contents-created`，对所有后来创建的 contents 拒绝新窗口、文档/子 frame 导航、重定向和 webview。锚点同文档导航保持可用。所有应用窗口只经过统一安全 preferences 工厂，进程级 enableSandbox 覆盖未来 contents，session 拒绝权限请求/检查。主进程代码仍只加载固定本地入口；Electron 的程序化 loadURL 不触发 will-navigate，不能把它当作任意 main 代码的沙箱。

health IPC 保持同时校验当前窗口 sender、mainFrame 和完全匹配的文档身份（只容许 hash 改变）。后来创建的同一可信文档窗口也不能冒用当前窗口。renderer 无 Node/通用 IPC/文件系统入口。

## 恢复及未来重连边界

render-process-gone（非 clean-exit）和原生 unresponsive 触发主进程原生对话框。默认/取消是暂不恢复。选择恢复才重建窗口；同一窗口同时最多一个提示；窗口已关闭、应用退出中或无响应已经恢复且没有崩溃时不重建。先创建新窗再销毁旧窗，避免 Windows/Linux window-all-closed 导致意外退出；旧 closed 回调不会清空新窗引用。

恢复仅重建视图，不调用引擎、不清理持久数据、不自动重放 health 或未来写任务。新的 UI 显示“尚未检查”，用户手动 health 后重新确认引擎状态。当前未接项目编辑 UI，不能宣称已实现业务状态恢复或业务任务重连。

I04 接入 ExecutionJob 时，恢复页需通过 project/job 身份和权威持久 job/提交标记只读查询；用 engineSessionId/seq 拒绝旧通知，展示最后已提交状态。提交成功响应丢失先对账，禁止重建窗口自动创建新写任务；零提交/部分轮次/全部提交后取消须联验。本项仅定义接口接入边界，不新增虚构运行方法。

## 验证方法与边界

`tests/e2e/csp-lifecycle.spec.ts` 对实际 Electron 页面注入临时 DOM，使用脚本标记、computed style、原生 securitypolicyviolation(enforce) 和真实本地 HTTP 接收端零请求交叉证明；未启用 bypassCSP，不用 page.evaluate 本身可执行证明 CSP 失效。测试创建同来源异窗口实测 IPC 拒绝。真实 forcefullyCrashRenderer 与 renderer 无限循环分别触发崩溃/无响应；自动化整体替换 `dialog.showMessageBox`，验证提示请求、文案和选择分支；它不能单独证明原生 sheet 渲染或按钮可达，不合成故障事件。真实 packaged 原生提示另由 computer use 观察并点击，详见 `../../reviews/I02/native-dialog-probe/README.md`（Run 2，同一进程 hang/crash 后恢复、拒绝不重建）。Playwright loader 禁用 hang monitor，故无响应实测另启原始 executable；通过主进程 inspector 短暂加载 test-only 驱动，驱动在故障前关闭 inspector 并记录 inspector.url() 为空。渲染进程始终没有 CDP/inspector，实际 app 源码/包内 main 不变。打包 executable 会忽略任意 --require，已明确改用上述统一驱动，未把忽略参数的超时当作通过。三个窗口各验证初始“尚未检查”和手动 health，捕获原生 killed/unresponsive 事件及两次提示。

开发 HMR 探针需显式 I02_HMR=1，临时更改 CSS/React 文案后 finally 逐字节恢复；冻结审查期间不运行该写源探针，审查者读取归档与哈希证据即可，其他默认测试不写实现。

本机 macOS arm64 的开发目录程序与未签名包仅为本机验证；Windows/Linux 生命周期、签名、安装器、干净设备、正式发布及 I04 job 联验保留为未验证。I01 事务化存储验证不是由窗口测试重新实现；这里不声称新增存储保证。

官方 API 依据：[Electron webContents 导航/崩溃事件](https://www.electronjs.org/docs/latest/api/web-contents)、[app web-contents-created](https://www.electronjs.org/docs/latest/api/app#event-web-contents-created)、[Vite CSP nonce](https://vite.dev/guide/features.html#content-security-policy-csp)。实际行为以锁定 Electron 44.9.0 / Vite 8.3.4 的矩阵为准。
