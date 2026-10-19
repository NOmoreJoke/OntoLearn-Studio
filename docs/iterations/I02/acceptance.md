# I02 / C1 实际验收记录

本项唯一范围及全部验收继续以 I01/inputs 中 scope 与 C1 原文为准。本记录不降低验收；当前真实能力仅 health，未宣称业务状态恢复/任务引擎/生产发布。

## 已执行矩阵

| 环境        | app.isPackaged | UI/CSS/health/锚点/隔离/同来源异窗口IPC拒绝 | style元素 / 属性 / CSSOM生效 | 未授权HTTP接收端请求 | 原生事件与重建后手动health            | 结果 |
| ----------- | -------------- | ------------------------------------------- | ---------------------------- | -------------------- | ------------------------------------- | ---- |
| development | False          | PASS                                        | True / True / True           | 0                    | ['killed', 'unresponsive'] / 3 health | PASS |
| build       | False          | PASS                                        | False / False / True         | 0                    | ['killed', 'unresponsive'] / 3 health | PASS |
| packaged    | True           | PASS                                        | False / False / True         | 0                    | ['killed', 'unresponsive'] / 3 health | PASS |

三种环境均捕获 enforce script-src-elem（内联及未授权外部script）、img-src、connect-src、frame-src；脚本标记未执行、fetch拒绝、接收端零请求。生产额外捕获 style-src-elem/attr，CSSOM赋值允许。生产仅meta，实际response无CSP header；meta位于资源之前；开发无生产meta，实际header有nonce。dev CSS HMR/React Refresh均成功，文档canary与组件health state保留。导航/popup被拒，锚点正常。

原生驱动暂时以main inspector装入测试hook，在fault前关闭inspector并显式断言；renderer始终无CDP/Playwright loader，真实forcefullyCrashRenderer和无限循环+原生input触发killed/unresponsive。记录两次native提示和三窗初始“尚未检查”/手动health成功。对话框用户选择由测试stub自动选择，未合成原生事件。包内main/preload/HTML与打包前build逐字节一致见package-manifest；源码/asar未注入测试代码。

## 静态与逻辑验证

- npm run check：lint/format/typecheck/build、14项TS（其中6项恢复逻辑竞态、2项native驱动故障模拟）、198项Python。逻辑模拟与原生矩阵分开。
- npm run verify:sources：工作区原始资料哈希；候选归档的原始manifest另作独立核验，避免把64项保护差异夹带进去。
- npm run test:e2e：构建态2项、真实packaged executable 2项均成功；开发专用C1矩阵1项成功。
- npm run package:dir：真实RDFLib依赖沿用I01，未改协议/依赖；本机arm64应用目录构建成功。
- 64项保护文件SHA逐一一致；renderer临时HMR两源文件无差异；只精确暂存I02自有文件与实现。

原始命令见commands.md；原始结果见evidence各日志和JSON。内部独立只读审查及处理见../../reviews/I02/internal-review.md。

## 边界

本机macOS 27.0.1 arm64、Electron44.9.0/Chromium152.0.7977.167。未验证Windows/Linux原生生命周期、签名/安装器/干净设备/正式生产。当前未接项目编辑UI；I01持久事务保证未被改变，此项不以单独文件canary冒充完整项目恢复。未来I04按project/job/持久提交标记只读重连，并补零提交/部分轮次/提交响应丢失/完成后取消联验，不自动重放写入；本项不实现虚构任务。
