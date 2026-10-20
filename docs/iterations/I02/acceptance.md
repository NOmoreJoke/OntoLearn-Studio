# I02 / C1 实际验收记录

本项唯一范围及全部验收继续以 I01/inputs 中 scope 与 C1 原文为准。本记录不降低验收；当前真实能力仅 health，未宣称业务状态恢复/任务引擎/生产发布。

## 已执行矩阵

| 环境        | app.isPackaged | UI/CSS/health/锚点/隔离/同来源异窗口IPC拒绝 | style元素 / 属性 / CSSOM生效 | 未授权HTTP接收端请求 | 原生事件与重建后手动health            | 结果 |
| ----------- | -------------- | ------------------------------------------- | ---------------------------- | -------------------- | ------------------------------------- | ---- |
| development | False          | PASS                                        | True / True / True           | 0                    | ['killed', 'unresponsive'] / 3 health | PASS |
| build       | False          | PASS                                        | False / False / True         | 0                    | ['killed', 'unresponsive'] / 3 health | PASS |
| packaged    | True           | PASS                                        | False / False / True         | 0                    | ['killed', 'unresponsive'] / 3 health | PASS |

三种环境均捕获 enforce script-src-elem（内联及未授权外部script）、img-src、connect-src、frame-src；脚本标记未执行、fetch拒绝、接收端零请求。生产额外捕获 style-src-elem/attr，CSSOM赋值允许。生产仅meta，实际response无CSP header；meta位于资源之前；开发无生产meta，实际header有nonce。dev CSS HMR/React Refresh均成功，文档canary与组件health state保留。导航/popup被拒，锚点正常。

原生驱动暂时以main inspector装入测试hook，在fault前关闭inspector并显式断言；renderer始终无CDP/Playwright loader，真实forcefullyCrashRenderer和无限循环+原生input触发killed/unresponsive。记录两次native提示请求和三窗初始“尚未检查”/手动health成功。测试整体 stub `dialog.showMessageBox`，只证明请求、选项和选择分支，不单独证明真实 sheet；未合成故障事件。真实 packaged sheet 显示、按钮可达及显式恢复/拒绝另由 computer use 补证，见 ../../reviews/I02/native-dialog-probe/README.md Run 2。包内main/preload/HTML与**同一次打包所用 build**逐字节一致见package-manifest；随机开发nonce导致main/asar跨构建哈希不可复现，不得把equalsBuild解释成独立重建相同，补充说明见 ../../reviews/I02/package-manifest-semantics.json。源码/asar未注入测试代码。

## 静态与逻辑验证

- npm run check：lint/format/typecheck/build、初版14项TS，Round 2为15项TS（其中6项恢复逻辑竞态、3项native驱动故障/诊断模拟）、198项Python。逻辑模拟与原生矩阵分开。
- npm run verify:sources：工作区原始资料哈希；候选归档的原始manifest另作独立核验，避免把64项保护差异夹带进去。
- npm run test:e2e：构建态2项、真实packaged executable 2项均成功；开发专用C1矩阵1项成功。
- npm run package:dir：真实RDFLib依赖沿用I01，未改协议/依赖；本机arm64应用目录构建成功。
- 64项保护文件SHA逐一一致；renderer临时HMR两源文件无差异；只精确暂存I02自有文件与实现。

原始命令见commands.md；原始结果见evidence各日志和JSON。内部独立只读审查及处理见../../reviews/I02/internal-review.md。

## 边界

本机macOS 27.0.1 arm64、Electron44.9.0/Chromium152.0.7977.167。未验证Windows/Linux原生生命周期、签名/安装器/干净设备/正式生产。当前未接项目编辑UI；I01持久事务保证未被改变，此项不以单独文件canary冒充完整项目恢复。未来I04按project/job/持久提交标记只读重连，并补零提交/部分轮次/提交响应丢失/完成后取消联验，不自动重放写入；本项不实现虚构任务。

## PR CI 修订及历史证据关联

Round 1 候选 `2cc03da` 的 PR attempt1：macOS通过；Windows原生探针错误复用shell spawnfile，修订为从实际 Electron main 读取 process.execPath。产品源码、CSP与恢复行为均未改，历史三态及真实原生UI证据对应的产品源码仍逐字相同。Linux首次runner磁盘耗尽，不能记为应用通过。修订后需重新运行本机必要验证、创建新候选并双模型新任务，远端CI必须实际通过才合并。原始失败、处理和新验证另保存在 docs/reviews/I02/round-2。

Round 2 的测试夹具进一步显式启用 C1 Playwright Chromium sandbox（不带 no-sandbox），Linux CI 为锁定 Electron 的官方 chrome-sandbox 配置 root/4755，保留全部断言与原90/40/45秒时限。native 输入前有界确认窗口可见/获焦，并记录投递时状态；直接启动真实无限循环，避免依赖 renderer 定时器调度。旧定时器方案两次本机挂起超时均保留在 round-2，不将“焦点不足/定时器节流”说成已证明根因。修订后实际结果以 round-2 新矩阵/日志为准；产品 apps 源码、配置、协议与依赖相对 Round 1 不变。
