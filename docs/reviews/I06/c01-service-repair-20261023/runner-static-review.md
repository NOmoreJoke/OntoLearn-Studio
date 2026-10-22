# 四路径普通命令 runner 静态审查

当前结论：有一项 P2 捕获闭包问题，应修后定点回读；未执行 runner、子进程、测试或格式化。source-freeze/runtime-plan 尚待主线生成，故本报告不签精确运行门完整可用。

受审 runner：`outputs/20261023_I06_C01_service_repair/run-command.py`，5749B，SHA-256 `80a34fb09b839e7cc74b2bd1e0bd978fd759e8d9fe4d39d3890d1dbb652e9669`。树仍 `/Users/kyle/Documents/工作/知爻/本体/.worktrees/I06-C01-service-repair-20261023`。授权沿已全文读取6465B/73b70587ff0a1301ab9ecba6ccf56ccd3fc96c4b452650175d2c6ed5b49d2612精确四路径票。本轮只读该新runner及定位行/hash，没有执行或导入它。

## P2-R01：后捕获与cleanup异常可跳过terminal receipt

位置：runner:95–110。`after = source_vector()`、source-after独占写、stdout/stderr digest 和最终receipt写均在唯一捕获try之外。具体反例：目标child已wait返回0，然后947源码中的一个读取发生OSError；第104行直接抛到顶层，已有claim/raw/started仍在，却没有包含实际child exit、`launchOrCaptureError`、source状态未知的terminal receipt。类似地，digest读取输出失败也会跳过receipt。不能把“脚本进程非0”当完整失败回执。

此外:97–103的poll/terminate/wait清理本身不是独立捕获；terminate抛异常时可连既有capture异常也无法收口。若child已在poll时结束，poll取得的真实returncode也没有回填 `exit_code`。这些是普通capture错误语义，不要求新增进程发现、全局drain或物理硬时限。

最小建议：收口为分阶段、best-effort终态记录；保留已获得的真实child退出码。after不可取得时显式 UNKNOWN、`sourceUnchanged=false`、固定非空`launchOrCaptureError`；每个cleanup动作错误只记unknown，不让它跳过后续receipt尝试；输出摘要失败同样记录读取失败，不冒称hash成功。receipt若自身持久写失败，至少输出受限fallback并让wrapper非0，明确不能保证磁盘不可写时仍有文件。不要重写旧claim/raw、不要自动重试命令、不要扩大清理到进程组/foreign PID。

## 其余已见机制与待补输入

- env完整dict替换Popen，不传继承environment；检查UV_NO_SYNC/OFFLINE=1、own HOME/.venv、ownnode/.venv先于.local/bin。仍需最终runtime-plan核全变量与禁用native/Electron/HMR门，不能只因上述几个assert就证明完整env安全。
- source_vector包含947 before路径+新增MF02 test，运行前后hash；requiresRuntimeFreeze路径比较精确sourceVector，逐件检查independentReviews bytes/SHA。仍需最终freeze确实绑定本轮四路径报告pin，及finalargv/绝对cwd/命令时限。
- 每个command独占O_EXCL claim，留在失败后；双流独占创建、stdin=DEVNULL，记录actual Popen.pid/argv/cwd/环境SHA。没有进程名发现/组信号/foreignkill。
- dependency检查前序receipt的exit0、无captureerror、sourceUnchanged；最终plan应明确 target3→check→verify 的依赖链与300000/600000/120000ms票内deadline，前序失败不能调后序。
- timeout只对保留的Popen对象terminate，10s后kill再等10s；不是全后代清理，不应称全局drain。Popen构造、源码向量读取、Git rev-parse、日志写入及同步OS调用无总硬时限；票中的operational wall不是syscall物理证明，现不另设此类前置。
- 当前没有改变产品、测试、运行票或四路径审查结论。待P2修正和finalplan/freeze后只定点静态复核，不运行探针求证，也不开发额外框架。
